---
title: "Key Vault 기록"
parent: "아티팩트 · Azure"
nav_order: 500
---

# Key Vault 기록 (Key Vault Logs)

Azure Key Vault 에서 비밀·키·인증서를 읽고 쓰고 지운 요청은 리소스 로그의 `AuditEvent` 범주에 남고, 볼트를 만들거나 지우거나 액세스 정책을 바꾼 관리 작업은 활동 로그에도 남습니다. `AuditEvent` 는 진단 설정을 만들어 둔 기간에만 쌓이고, 비밀 값 자체는 기록하지 않습니다[1][3][8].

## 무엇을 기록하나 · 왜 생기나

Key Vault 는 비밀 (secret), 키 (key), 인증서 (certificate) 를 보관하는 서비스입니다. 여기에 들어온 REST API 요청은 누가·언제·어느 IP 에서·어느 객체에·무슨 작업을 했는지와 HTTP 결과까지 `AuditEvent` 레코드 한 줄로 남습니다[1]. 인증 요청, 볼트 자체에 대한 작업(만들기·지우기·액세스 정책 설정·태그 같은 속성 변경), 키와 비밀에 대한 작업(만들기·지우기·서명 등)이 모두 대상입니다[4].

같은 볼트의 작업이 두 기록으로 나뉩니다. Azure Resource Manager 를 거친 관리 작업, 곧 제어 평면 (control plane) 작업은 [활동 로그](./activity-log.md)에 남고, 비밀 값을 가져오는 것 같은 데이터 평면 (data plane) 작업은 활동 로그가 아니라 리소스 로그에 남습니다[8]. 관리·데이터 평면의 일반 원리는 [로그의 종류](../../01-foundations/logging/log-types.md)에 있습니다.

| 조사 질문 | 기록 | 작업 이름 예 |
|---|---|---|
| 누가 비밀 값을 읽었나 | `AuditEvent` | `SecretGet` |
| 비밀·키 목록을 훑었나 | `AuditEvent` | `SecretList`, `SecretListVersions`, `KeyList` |
| 비밀을 만들거나 바꿨나 | `AuditEvent` | `SecretSet`, `SecretUpdate` |
| 키로 복호화·서명을 했나 | `AuditEvent` | `KeyDecrypt`, `KeyUnwrap`, `KeySign` |
| 비밀·키의 백업 파일을 만들었나 | `AuditEvent` | `SecretBackup`, `KeyBackup`, `CertificateBackup` |
| 지우고 영구 삭제했나 | `AuditEvent` | `SecretDelete` → `SecretPurge`, `KeyDelete` → `KeyPurge` |
| 볼트를 만들거나 설정·정책을 바꿨나, 지웠나 | 활동 로그·`AuditEvent` | `Microsoft.KeyVault/vaults/write`·`/delete`·`/accessPolicies/write`, `VaultPut`·`VaultPatch`·`VaultDelete` |
| 지운 볼트를 영구 삭제했나 | 활동 로그 | `Microsoft.KeyVault/locations/deletedVaults/purge/action` |

활동 로그 쪽 작업 이름은 권한 문서의 제어 평면 작업(Action) 목록이고, 2026년 9월 문서 기준입니다[7]. `AuditEvent` 쪽 작업 이름은 아래 구조 절에 모았습니다.

## 위치와 버전별 차이

### 로그 범주와 표

Key Vault 의 리소스 로그 범주는 두 가지입니다(2026년 9월 문서 기준)[2].

| 리소스 종류 | 범주 | Log Analytics 표 |
|---|---|---|
| 볼트 (`Microsoft.KeyVault/vaults`) | `AuditEvent` | `AzureDiagnostics` 또는 `AZKVAuditLogs` |
| 볼트 | `AzurePolicyEvaluationDetails` | `AZKVPolicyEvaluationDetailsLogs` 또는 `AzureDiagnostics` |
| 관리형 HSM (`microsoft.keyvault/managedhsms`) | `AuditEvent` | `AzureDiagnostics` 또는 `AZKVAuditLogs` |

조사에 쓰는 범주는 `AuditEvent` 이고, 로그 레코드의 `category` 값도 늘 `AuditEvent` 입니다[1]. 볼트의 기록이 `AzureDiagnostics` 에 들어가는지 `AZKVAuditLogs` 에 들어가는지는 진단 설정의 수집 모드가 정합니다[9]. 두 모드의 차이와 모드를 바꾼 기간을 함께 조회하는 방법은 [리소스 로그와 진단 설정](./resource-logs.md)에 있습니다.

### 진단 설정과 목적지

`AuditEvent` 는 볼트에 진단 설정을 만들어 목적지로 보내기 전까지 모이지도 저장되지도 않습니다[3]. 진단 설정은 포털, CLI, PowerShell, Azure Policy 로 만들 수 있고[3], 목적지는 Log Analytics 작업 영역, Storage 계정, Event Hubs, 일부 Microsoft 모니터링 파트너 가운데서 고릅니다[3].

Storage 계정을 목적지로 고르면 그 계정에 `insights-logs-auditevent` 컨테이너가 저절로 생기고, 여러 볼트가 한 계정을 같이 쓸 수 있습니다[1]. 컨테이너 안의 블롭 경로 규칙(`resourceId=/.../y=/m=/d=/h=/m=00/PT1H.json`), 목적지별 조건, Log Analytics 보관 기간은 [리소스 로그와 진단 설정](./resource-logs.md)에서 다룹니다. Storage 로 보낸 기록은 로그를 모은 계정에서 관리하며, 누가 그 기록을 읽을 수 있는지와 언제 지울지는 그 계정의 접근 제어와 삭제 관리에 달려 있습니다[1].

### 설정 확인하기

진단 설정이 언제 생기고 바뀌었는지는 활동 로그에서 `Microsoft.KeyVault/vaults/providers/Microsoft.Insights/diagnosticSettings/Write` 작업으로 봅니다[7]. 볼트의 삭제 보호 설정은 `AZKVAuditLogs` 의 `EnableSoftDelete`, `EnablePurgeProtection`, `SoftDeleteRetentionInDays` 열과 권한 모델을 알려 주는 `EnableRbacAuthorization` 열로 확인할 수 있습니다[4].

### 삭제와 영구 삭제 (2026년 9월 문서 기준)

지운 객체를 되살릴 수 있는지는 볼트의 일시 삭제 (soft-delete) 와 영구 삭제 방지 (purge protection) 설정에 달려 있습니다[6].

| 항목 | 내용 |
|---|---|
| 일시 삭제 기본값 | 새 볼트는 켜짐. 한 번 켜면 끌 수 없음[6] |
| 보관 기간 | 7~90일, 기본 90일. 볼트를 만들 때만 정하고 바꿀 수 없음[6] |
| 영구 삭제 | 지운 뒤(삭제 상태) 다시 purge 해야 사라짐. purge 권한 필요(예 "Key Vault Purge Operator" 역할)[6] |
| 영구 삭제 방지 | 기본 꺼짐. 켜면 보관 기간이 끝나기 전에는 purge 할 수 없음[6] |
| 일시 삭제가 꺼진 볼트 | 키를 지우면 바로 영구 삭제됨[6] |
| 삭제 상태의 객체 | 목록 보기·복구·영구 삭제만 할 수 있고 값을 읽을 수 없음[6] |
| 볼트를 일시 삭제하면 | 연결된 Azure RBAC 역할 할당과 Event Grid 구독이 지워지고, 볼트를 복구해도 돌아오지 않음[6] |

삭제 상태의 객체는 Azure CLI 의 `az keyvault key list-deleted` 나 Azure PowerShell 의 `Get-AzKeyVault -InRemovedState` 로 봅니다[6]. 삭제 상태의 볼트 이름은 보관 기간 동안 다시 쓸 수 없습니다[6].

## 구조

### 레코드 필드

Storage 로 보낸 `AuditEvent` 레코드와 Log Analytics 의 두 표는 필드 이름이 다릅니다[1][2][4][5].

| Storage 필드 | `AZKVAuditLogs` 열 | `AzureDiagnostics` 열 | 뜻 |
|---|---|---|---|
| `time` | `TimeGenerated` | `TimeGenerated` | 작업이 일어난 UTC 시각(`AzureDiagnostics` 표 설명은 레코드를 만든 시각) |
| `resourceId` | `_ResourceId` | `_ResourceId` | 볼트의 리소스 ID(Key Vault 로그는 늘 볼트 ID) |
| `operationName` | `OperationName` | `OperationName` | `SecretGet` 같은 작업 이름 |
| `operationVersion` | `OperationVersion` | `OperationVersion` | 클라이언트가 요청한 REST API 버전 |
| `resultType` | `ResultType` | 검체에서 확인 | REST API 요청의 결과 |
| `resultSignature` | `ResultSignature` | `ResultSignature` | HTTP 상태(예 `OK`, `Forbidden`) |
| `durationMs` | `DurationMs` | `DurationMs` | 서버가 요청을 처리한 밀리초. 네트워크 지연은 빠짐 |
| `callerIpAddress` | `CallerIpAddress` | `CallerIPAddress` | 요청한 클라이언트 IP |
| `correlationId` | `CorrelationId` | 검체에서 확인 | 클라이언트가 넘길 수 있는 선택 GUID |
| `identity` | `Identity` | `identity_claim_*` 열(예 `identity_claim_appid_g`) | 요청에 쓴 토큰의 신원 |
| `properties.clientInfo` | `ClientInfo` | `clientInfo_s` | User-Agent |
| `properties.requestUri` | `RequestUri` | `requestUri_s` | 요청 URI |
| `properties.id` | `Id` | `id_s` | 요청 결과로 돌려준 키·비밀·볼트의 URI |
| `properties.httpStatusCode` | `HttpStatusCode` | `httpStatusCode_d` | HTTP 상태 코드(예 200) |

`identity` 에는 토큰의 클레임이 들어가며, 보통 사용자, 서비스 주체 (service principal), 또는 Azure PowerShell 에서 온 요청처럼 사용자와 앱 ID 를 합친 모양입니다[1]. `properties.id` 는 `KeyCreate`·`VaultGet` 처럼 요청이 객체를 돌려줄 때 들어갑니다[1].

`AZKVAuditLogs` 에는 권한 판단을 보여 주는 열이 더 있습니다[4].

| 열 | 뜻 |
|---|---|
| `IsRbacAuthorized` | 접근 검사에서 RBAC 로 허용됐는지 |
| `AppliedAssignmentId` | 접근을 허용하거나 거부한 역할 할당 ID |
| `IsAccessPolicyMatch` | 테넌트가 볼트 테넌트와 같고 액세스 정책이 그 주체에게 권한을 명시했는지 |
| `IsAddressAuthorized`·`AddressAuthorizationType` | 허가된 곳에서 온 요청인지, 주소 종류(공인 IP·서브넷·프라이빗 연결) |
| `SubnetId` | 알려진 서브넷에서 온 요청이면 그 서브넷 ID |
| `TrustedService` | 신뢰할 수 있는 서비스로 접근했는지. 비어 있으면 아님 |
| `Tlsversion` | 요청에 쓴 네트워크 암호 프로토콜 |
| `SecretProperties`·`KeyProperties`·`CertificateProperties` | 객체 속성(종류·특성, 키 크기·곡선 등) |
| `VaultProperties`·`NetworkAcls`·`Nsp` | 볼트의 액세스 정책·IP 규칙·네트워크 설정 |

### 작업 이름

`operationName` 은 "대상+동사" 모양입니다[1]. 볼트 작업은 `Vault` 로, 키는 `Key` 로, 비밀은 `Secret` 으로, 인증서는 `Certificate` 로 시작합니다[1].

| 대상 | 작업 이름 |
|---|---|
| 인증 | `Authentication`(Microsoft Entra 끝점으로 인증) |
| 볼트 | `VaultGet`, `VaultPut`(만들기·수정), `VaultPatch`, `VaultDelete`, `VaultRecover`, `VaultAccessPolicyChangedEventGridNotification` |
| 비밀 | `SecretSet`, `SecretGet`, `SecretUpdate`, `SecretDelete`, `SecretList`, `SecretListVersions`, `SecretPurge`, `SecretBackup`, `SecretRestore`, `SecretRecover`, `SecretGetDeleted`, `SecretListDeleted` |
| 키 | `KeyCreate`, `KeyGet`, `KeyImport`, `KeyDelete`, `KeySign`, `KeyVerify`, `KeyWrap`, `KeyUnwrap`, `KeyEncrypt`, `KeyDecrypt`, `KeyUpdate`, `KeyList`, `KeyListVersions`, `KeyPurge`, `KeyBackup`, `KeyRestore`, `KeyRecover`, `KeyGetDeleted`, `KeyListDeleted`, `KeyRotate`, `KeyRotateIfDue`, `KeyRotationPolicyGet`, `KeyRotationPolicySet` |
| 인증서 | `CertificateGet`, `CertificateCreate`, `CertificateImport`, `CertificateUpdate`, `CertificateList`, `CertificateDelete`, `CertificatePurge`, `CertificateBackup`, `CertificateRestore`, `CertificateRecover`, `CertificatePolicySet`, `CertificateIssuerSet`, `CertificateContactsSet` 등 |
| 알림 | `SecretNearExpiryEventGridNotification`, `KeyExpiredEventGridNotification`, `CertificateNearExpiryEventGridNotification` 같은 `...EventGridNotification` |

`...EventGridNotification` 작업은 Event Grid 구독이 없어도 기록됩니다[1]. `KeyRotateIfDue` 는 회전 정책에 따라 예약된 자동 키 회전입니다[1]. 볼트 작업은 `VaultGet`·`VaultCreate` 처럼 적는다는 설명도 있지만, 작업 이름 표에는 만들기와 수정이 `VaultPut` 하나로 적혀 있습니다[1]. 검체에서 실제 값을 `summarize count() by OperationName` 으로 먼저 봅니다.

## 증거로서 의미

**증명하는 것.** 레코드 한 줄은 어느 UTC 시각에, 어느 토큰 신원(개체 ID·UPN·앱 ID)이, 어느 IP 와 User-Agent 로, 어느 볼트의 어느 객체에, 어떤 작업을 요청했고 HTTP 결과가 무엇이었는지를 보여 줍니다[1]. 권한이 없어 거부된 요청도 남으므로 `ResultSignature` 가 `Forbidden` 인 레코드는 실패한 시도의 흔적입니다[3]. `IsRbacAuthorized`·`AppliedAssignmentId`·`IsAccessPolicyMatch` 로 어떤 역할 할당이나 액세스 정책이 그 접근을 허용했는지까지 좁힐 수 있습니다[4]. `SecretBackup` 은 비밀의 백업 파일을 만드는 요청이고, 이 파일은 같은 구독의 Key Vault 에 복원할 수 있습니다[7]. 비밀·키를 옮기려 한 정황을 볼 때 `SecretGet` 과 함께 찾습니다.

**증명하지 못하는 것.** 비밀 값과 키 재료는 기록에 없어서, 레코드는 "값을 가져가는 요청이 성공했다" 까지만 말합니다. 가져간 비밀로 무엇을 했는지는 그 비밀을 쓰는 서비스의 기록(Storage 연결 문자열이면 [Storage 계정 기록](./storage-logs.md), 앱 비밀이면 [Microsoft Entra 로그](../m365/entra-logs/index.md))에서 따로 찾아야 합니다. 진단 설정이 없던 기간에는 기록이 아예 없습니다[3]. 레코드는 토큰의 주체를 가리킬 뿐 키보드 앞의 사람을 가리키지 않습니다. 보고서에는 "이 시각에 이 IP 에서 이 서비스 주체로 이 비밀의 값을 가져오는 요청이 성공한 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다. 문장 쓰는 법은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)에 있습니다.

## 시각 해석

`time`·`TimeGenerated` 는 작업이 일어난 UTC 시각입니다[1][4]. `durationMs` 는 서버가 요청을 처리한 시간만 담고 네트워크 지연은 빠지므로 클라이언트 쪽에서 잰 시간과 맞지 않을 수 있습니다[1].

기록은 작업 뒤 최대 10분 안에 볼 수 있고 대개는 더 빠릅니다[1]. Storage 로 보낸 `PT1H.json` 은 로그를 받은 시각으로 나뉘어서 블롭 경로의 시간 밖 레코드가 들어 있을 수 있고, 한 시간 경계 근처에서는 앞뒤 블롭을 같이 엽니다[9]. Log Analytics 의 수집 지연을 재는 방법은 [리소스 로그와 진단 설정](./resource-logs.md)에, 여러 기록의 시각을 맞추는 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 있습니다.

## 함정과 한계

- **활동 로그만 봐서는 비밀 접근이 보이지 않습니다.** 비밀 값을 가져오는 것 같은 데이터 평면 작업은 리소스 로그에만 남습니다[8]. 활동 로그만 모아 둔 조직이라면 `SecretGet` 기록은 처음부터 없습니다.
- **Sigma 규칙과 문서의 분류가 다릅니다.** Sigma 의 Key Vault 키·비밀 규칙은 로그 출처를 활동 로그로 두고 `MICROSOFT.KEYVAULT/VAULTS/SECRETS/DELETE`, `.../SECRETS/PURGE/ACTION`, `.../SECRETS/BACKUP/ACTION`, `.../SECRETS/SETSECRET/ACTION`, `.../KEYS/DELETE`, `.../KEYS/CREATE/ACTION`, `.../KEYS/PURGE/ACTION` 같은 이름을 찾습니다[10][11]. 권한 문서는 이 이름들을 데이터 평면 작업(DataAction)으로 분류하고[7], 데이터 평면 작업은 활동 로그에 남지 않습니다[8]. 그래서 이 작업들은 `AuditEvent` 의 `SecretDelete`, `SecretPurge`, `SecretBackup`, `SecretSet`, `KeyDelete`, `KeyCreate`, `KeyPurge` 로 찾습니다. 키 규칙에 있는 `MICROSOFT.KEYVAULT/VAULTS/KEYS/CREATE`(`/ACTION` 없음)는 권한 문서 목록에 없고, 제어 평면 쪽 키 만들기는 `Microsoft.KeyVault/vaults/keys/write` 입니다[7][10]. 비밀 규칙의 `SECRETS/WRITE` 와 볼트 규칙의 네 이름(`VAULTS/WRITE`·`/DELETE`·`/DEPLOY/ACTION`·`/ACCESSPOLICIES/WRITE`)은 제어 평면 작업이라 활동 로그에서 찾습니다[7][11][12]. Sigma 규칙을 쓰는 방법은 [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md)에 있습니다.
- **`Authentication` 401 은 따로 봅니다.** 실패한 요청을 셀 때는 `OperationName == "Authentication"` 이면서 `httpStatusCode_d == 401` 인 레코드를 빼고 셉니다[3]. 이 레코드만 세어 무차별 대입이라고 판단하지 않고, 같은 신원·IP 의 다른 작업 결과와 함께 봅니다.
- **표가 둘로 나뉠 수 있습니다.** 수집 모드를 바꾼 볼트는 앞 기간이 `AzureDiagnostics`, 뒤 기간이 `AZKVAuditLogs` 에 있고, 앞 기간 기록은 작업 영역 보관 기간이 끝날 때까지 `AzureDiagnostics` 에 남습니다[9]. `AzureDiagnostics` 에서는 `ResourceProvider == "MICROSOFT.KEYVAULT"` 로 걸러야 다른 서비스 기록과 섞이지 않습니다[3]. 이 표는 열이 500개에 이르면 새 열의 값을 `AdditionalFields` 열에 몰아 넣으므로, 필요한 열이 없으면 그 열을 봅니다[5].
- **레코드 모양이 문서마다 다릅니다.** Key Vault 로깅 문서의 예시는 `{"records": [...]}` 로 감싼 JSON 이고 `durationMs` 가 문자열 `"78"` 입니다[1]. 리소스 로그 문서의 `PT1H.json` 예시는 `records` 로 감싸지 않은 이벤트 한 줄이고[9], `AZKVAuditLogs` 의 `DurationMs` 는 정수입니다[4]. 내려받은 블롭은 첫 몇 줄을 열어 모양을 확인한 뒤 읽는 방법을 정합니다.
- **액세스 정책 변경은 두 곳에 남습니다.** 활동 로그의 `Microsoft.KeyVault/vaults/accessPolicies/write` 와 `AuditEvent` 의 `VaultAccessPolicyChangedEventGridNotification` 을 함께 봅니다[1][7]. RBAC 모델을 쓰는 볼트라면 역할 할당 변경을 봐야 하며, 방법은 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md)에 있습니다.
- **볼트를 지웠다 복구하면 역할 할당이 사라집니다.** 일시 삭제한 볼트를 복구해도 역할 할당과 Event Grid 구독은 돌아오지 않습니다[6]. 복구 전후의 권한 구성이 달라 보이면 이 동작 때문일 수 있습니다.
- **조사자의 조회도 기록됩니다.** 조사자가 볼트에 보낸 요청도 다른 요청과 똑같이 `AuditEvent` 에 남습니다[4]. 조사자의 계정·IP·시각을 적어 두고 결과에서 뺍니다.

## 직접 분석해 보기

### 원본 한 줄 읽기

아래는 서비스 주체가 비밀 값을 가져온 요청을 필드 설명에 맞춰 만든 예시입니다[1]. 구독 ID·볼트 이름·신원·IP·User-Agent·API 버전·URI 경로는 모두 만든 값이고, 실제 파일에서는 한 줄입니다.

```json
{
  "time": "2026-03-14T02:17:45.1234567Z",
  "resourceId": "/SUBSCRIPTIONS/1A2B3C4D-0000-4E5F-8A9B-0C1D2E3F4A5B/RESOURCEGROUPS/RG-EXAMPLE/PROVIDERS/MICROSOFT.KEYVAULT/VAULTS/KV-EXAMPLE01",
  "operationName": "SecretGet",
  "operationVersion": "7.4",
  "category": "AuditEvent",
  "resultType": "Success",
  "resultSignature": "OK",
  "resultDescription": "",
  "durationMs": "12",
  "callerIpAddress": "203.0.113.25",
  "correlationId": "",
  "identity": {"claim": {"http://schemas.microsoft.com/identity/claims/objectidentifier": "11112222-aaaa-3333-bbbb-4444cccc5555", "appid": "99998888-7777-6666-5555-444433332222"}},
  "properties": {"clientInfo": "azsdk-python-keyvault-secrets/4.8.0", "requestUri": "https://kv-example01.vault.azure.net/secrets/db-password/?api-version=7.4", "id": "https://kv-example01.vault.azure.net/secrets/db-password/0a1b2c3d4e5f", "httpStatusCode": 200}
}
```

| 필드 | 값 | 읽는 법 |
|---|---|---|
| `time` | `2026-03-14T02:17:45.1234567Z` | 작업이 일어난 UTC 시각 |
| `resourceId` | `.../VAULTS/KV-EXAMPLE01` | 대상 볼트. 대문자로 적혀 있을 수 있음 |
| `operationName` | `SecretGet` | 비밀 값을 가져오는 요청 |
| `resultSignature`·`httpStatusCode` | `OK`·`200` | 성공 |
| `callerIpAddress` | `203.0.113.25` | 요청한 IP |
| `identity.claim` | 개체 ID·`appid` | UPN 없이 앱 ID 만 있어 서비스 주체의 토큰일 가능성이 있음 |
| `properties.clientInfo` | SDK 이름·버전 | 사람이 포털에서 연 것인지, 코드가 부른 것인지 가르는 단서 |
| `properties.id` | 비밀 URI | 어느 비밀(과 버전)을 돌려줬는지 |

`identity.claim` 에 `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn` 클레임이 있으면 사용자 토큰이고, 개체 ID 와 앱 ID 를 [Microsoft Entra 로그](../m365/entra-logs/index.md)의 로그인 기록과 맞춰 이름과 로그인 위치를 확인합니다[1]. JSON 로그 다루는 법은 [JSON 로그 읽기](../../01-foundations/logging/json-logs.md)에 있습니다. 한 줄에 하나씩 적힌 블롭이라면 다음처럼 뽑습니다.

```bash
jq -c 'select(.operationName=="SecretGet") | [.time, .callerIpAddress, .identity.claim.appid, .properties.id, .resultSignature]' PT1H.json
```

### 공개 도구와 질의

Untitled Goose Tool 은 설정 파일의 `key_vault_log=True` 로 Key Vault 기록을 받습니다[13][14]. 구독의 모든 Storage 계정을 돌며 `insights-logs-auditevent` 컨테이너의 블롭 가운데 마지막 수정 시각이 기간 안에 드는 것을 받아 `{구독 ID}/key_vault_logs/log_{블롭 이름}` 에 저장하고, 기간을 정하지 않으면 최근 2년을 받습니다[13]. 이미 받은 블롭은 계정마다 `.{계정 이름}_savestate` 파일에 적어 두고 건너뜁니다[13]. 이 기능은 Storage 로 보낸 기록만 받으므로, Log Analytics 로 보낸 볼트는 작업 영역을 조회하거나 내보냅니다. 수집 순서 전반은 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md)에 있습니다.

Log Analytics 로 모았다면 KQL 로 거릅니다. 아래 첫째 질의는 호출 IP 별 요청 수를, 둘째 질의는 실패한 요청을 상태별로 셉니다[3].

```kusto
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.KEYVAULT"
| summarize count() by CallerIPAddress
```

```kusto
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.KEYVAULT"
| where httpStatusCode_d >= 300 and not(OperationName == "Authentication" and httpStatusCode_d == 401)
| summarize count() by requestUri_s, ResultSignature, _ResourceId
```

리소스별 모드라면 `AZKVAuditLogs` 에서 비밀 값 읽기와 삭제 흐름을 한 번에 봅니다[4].

```kusto
AZKVAuditLogs
| where TimeGenerated between (datetime(2026-03-14T00:00:00Z) .. datetime(2026-03-15T00:00:00Z))
| where OperationName in ("SecretGet", "SecretBackup", "SecretDelete", "SecretPurge", "KeyBackup", "KeyDelete", "KeyPurge")
| project TimeGenerated, OperationName, CallerIpAddress, Identity, ClientInfo, Id, ResultSignature, IsRbacAuthorized, AppliedAssignmentId
| sort by TimeGenerated asc
```

`SecretDelete` 뒤에 같은 비밀의 `SecretPurge` 가 성공으로 이어지면 되살릴 수 없게 지운 흐름입니다[6]. 영구 삭제 방지가 켜진 볼트에서는 보관 기간 안에 purge 할 수 없으므로[6], 그런 볼트에서 `SecretPurge` 가 보이면 결과 필드를 확인합니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [활동 로그](./activity-log.md) | 볼트 만들기·삭제·액세스 정책·진단 설정 변경 시각과 호출자, 지운 볼트의 영구 삭제 |
| [리소스 로그와 진단 설정](./resource-logs.md) | 조사 기간에 볼트의 진단 설정이 있었는지, 기록이 어느 목적지·표에 있는지 |
| [Microsoft Entra 로그](../m365/entra-logs/index.md) | `identity` 의 개체 ID·앱 ID 로 로그인 기록과 IP, 서비스 주체 자격 증명 변경 |
| [Storage 계정 기록](./storage-logs.md) | 비밀로 둔 계정 키·연결 문자열을 읽은 뒤 그 키로 들어온 요청 |
| [Azure 가상 머신](./azure-vm.md) | 관리 ID 를 쓰는 VM 에서 비밀을 읽은 경우 그 VM 안의 작업 |
| [CloudTrail](../aws/cloudtrail/index.md) | AWS 쪽 비밀·키 사용 기록과 견줄 때 |

IP·User-Agent 로 출처를 좁히는 방법은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md), 여러 기록을 시간순으로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md), 기록이 지워지기 전에 지키는 방법은 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)에 있습니다.

## 실습

Microsoft 문서 "Azure Key Vault logging" 에 실린 예시 레코드와 "Monitor Azure Key Vault" 의 질의로 풀어 봅니다[1][3].

1. 예시 레코드의 `identity.claim` 에서 개체 ID·UPN·앱 ID 를 찾고, 이 요청이 사용자 토큰인지 서비스 주체 토큰인지 설명해 봅니다.
2. 예시 레코드의 `properties.clientInfo` 와 `requestUri` 를 보고, 이 요청이 데이터 평면 끝점과 관리 끝점 가운데 어디로 들어왔는지 판단해 봅니다.
3. 실패 집계 질의가 `Authentication` 401 을 빼는 까닭을 설명하고, 빼지 않으면 결과가 어떻게 달라질지 적어 봅니다.
4. 작업 이름 표에서 비밀 값이나 백업 파일을 요청한 쪽에 돌려주는 작업을 골라 목록을 만들어 봅니다.
5. 실제 검체에서는 조사 기간을 시간 단위로 나눠 `insights-logs-auditevent` 의 `PT1H.json` 이나 `AZKVAuditLogs` 행이 빠진 시간이 있는지 표로 만들고, 같은 시간대 활동 로그에 진단 설정 변경이 있었는지 확인해 봅니다.

## 참고 문헌

1. Microsoft, "Azure Key Vault logging", Microsoft Learn. https://learn.microsoft.com/en-us/azure/key-vault/general/logging
2. Microsoft, "Azure Key Vault monitoring data reference", Microsoft Learn. https://learn.microsoft.com/en-us/azure/key-vault/general/monitor-key-vault-reference
3. Microsoft, "Monitor Azure Key Vault", Microsoft Learn. https://learn.microsoft.com/en-us/azure/key-vault/general/monitor-key-vault
4. Microsoft, "AZKVAuditLogs", Azure Monitor Logs table reference. https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/azkvauditlogs
5. Microsoft, "AzureDiagnostics", Azure Monitor Logs table reference. https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/azurediagnostics
6. Microsoft, "Azure Key Vault: soft-delete overview", Microsoft Learn. https://learn.microsoft.com/en-us/azure/key-vault/general/soft-delete-overview
7. Microsoft, "Azure permissions for Security", Azure RBAC. https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/security
8. Microsoft, "Azure Monitor activity log", azure-monitor-docs. https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
9. Microsoft, "Azure resource logs", azure-monitor-docs. https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs.md
10. SigmaHQ, azure_keyvault_key_modified_or_deleted.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_keyvault_key_modified_or_deleted.yml
11. SigmaHQ, azure_keyvault_secrets_modified_or_deleted.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_keyvault_secrets_modified_or_deleted.yml
12. SigmaHQ, azure_keyvault_modified_or_deleted.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_keyvault_modified_or_deleted.yml
13. CISA, Untitled Goose Tool, goosey/azure_dumper.py. https://github.com/cisagov/untitledgoosetool/blob/main/goosey/azure_dumper.py
14. CISA, Untitled Goose Tool, README.md. https://github.com/cisagov/untitledgoosetool/blob/main/README.md
