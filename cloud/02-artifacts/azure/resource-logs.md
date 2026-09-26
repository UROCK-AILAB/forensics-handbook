---
title: "리소스 로그와 진단 설정"
parent: "아티팩트 · Azure"
nav_order: 470
---

# 리소스 로그와 진단 설정 (Resource Logs·Diagnostic Settings)

Azure 리소스 안에서 일어난 작업을 리소스 종류마다 다른 내용으로 적는 로그이고, 리소스마다 진단 설정을 만들어 둔 기간에만 Log Analytics·Storage·Event Hubs 로 모입니다.

## 무엇을 기록하나 · 왜 생기나

리소스 로그 (resource log) 는 Azure 리소스 안에서 한 작업과 그 작업의 상태를 적습니다[1]. 구독 수준에서 리소스를 만들고 바꾸고 지운 기록은 [활동 로그](activity-log.md) 에 남고, 리소스 로그는 그 리소스 안쪽의 작업을 다룹니다. 예를 들어 Key Vault 의 비밀 읽기, Storage 의 블롭 읽기, NSG 규칙이 연결에 적용된 횟수가 리소스 로그에 들어갑니다. 관리 평면과 데이터 평면의 구분은 [로그의 종류](../../01-foundations/logging/log-types.md) 에서 다룹니다.

리소스 로그는 기본으로 모이지 않습니다[1][2]. 플랫폼 메트릭과 활동 로그는 설정 없이 자동으로 모이고 진단 설정은 이것을 다른 곳으로 보낼 때만 필요하지만, 리소스 로그는 리소스마다 진단 설정 (diagnostic setting) 을 만들어야 비로소 기록이 쌓입니다[2]. 그래서 조사에서는 로그를 읽기 전에 "그 시점에 그 리소스에 어떤 진단 설정이 있었나" 를 먼저 확인합니다.

이 로그의 예전 이름은 진단 로그 (diagnostic logs) 이고, 2019년 10월에 리소스 로그로 이름이 바뀌었습니다[3]. 오래된 문서나 도구에 나오는 "diagnostic logs" 는 같은 것을 가리킵니다.

리소스 로그는 손실이 전혀 없다고 보장하지 않습니다. 하루에 페타바이트 단위를 옮기는 저장 후 전달 (store and forward) 구조라서 재시도는 하지만 트랜잭션 보장이 없고, 일시적인 서비스 문제로 적은 양이 빠질 수 있습니다[1].

## 위치와 버전별 차이

### 진단 설정이 정하는 것

진단 설정 하나는 "이 리소스에서 어떤 로그 범주를 모아 어디로 보낼지" 를 정합니다[2]. 설정 하나에 목적지 종류마다 하나씩만 고를 수 있고, 리소스 하나에 설정을 5개까지 만들 수 있습니다[2]. 같은 종류 목적지 두 곳(예: Log Analytics 작업 영역 두 개)으로 보내려면 설정을 둘 만듭니다[2].

| 목적지 | 쓰임 | 조건 |
|---|---|---|
| Log Analytics 작업 영역 | 로그 쿼리·경고. 표는 첫 데이터가 올 때 자동으로 생김[2] | 작업 영역만 미리 있으면 됨[2] |
| Storage 계정 | 감사·보관. 기간 제한 없이 둘 수 있고 불변 (immutable) 정책으로 수정을 막을 수 있음[2] | 지역 리소스면 같은 지역. Premium Storage 계정과 Azure DNS 영역 끝점 계정은 목적지로 쓸 수 없음. 가상 네트워크 방화벽이 켜져 있으면 "신뢰할 수 있는 Microsoft 서비스" 허용 필요[2] |
| Event Hubs | 외부 SIEM 등으로 스트리밍[2] | 지역 리소스면 같은 지역. 압축된 (compacted) 이벤트 허브는 쓸 수 없음[2] |
| 파트너 솔루션 | Azure 와 통합된 외부 감시 제품[2] | 제품마다 다름[2] |

목적지는 설정한 사람이 두 구독 모두에 권한이 있으면 다른 구독에 둘 수 있고, 다른 Microsoft Entra 테넌트에 두려면 Azure Lighthouse 를 씁니다[2]. 그래서 로그가 조사 대상 구독 밖, 심지어 다른 테넌트의 작업 영역에 쌓여 있을 수 있습니다. 구독과 테넌트의 관계는 [테넌트·구독·계정·프로젝트](../../01-foundations/model/tenancy.md) 에서 다룹니다.

로그 범주는 리소스 종류마다 다르고, 범주를 하나씩 고르거나 범주 그룹 (category group) 을 고릅니다[2]. 범주 그룹은 두 가지입니다. `allLogs` 는 그 리소스의 모든 범주이고, `audit` 는 데이터나 서비스 설정에 대한 고객의 상호작용을 적는 로그 묶음입니다[2]. 범주 그룹을 고르면 개별 범주를 따로 고를 수 없고, Microsoft 가 그룹 구성을 바꾸면 수집 범위도 저절로 바뀝니다[2]. Azure SQL Database 에서는 진단 설정의 `audit` 를 켜도 데이터베이스 감사가 켜지지 않고, 감사는 SQL 의 감사 화면에서 따로 켭니다[2].

### Log Analytics 의 두 수집 모드

Log Analytics 로 보낸 리소스 로그가 어느 표에 들어가는지는 리소스 종류와 수집 모드에 따라 정해집니다[1].

| 모드 | 들어가는 표 | 특징 |
|---|---|---|
| Azure 진단 (Azure diagnostics) | 모든 리소스가 `AzureDiagnostics` 한 표에 씀[1] | 예전 방식. 여러 리소스의 스키마를 합친 표라 열이 많음[1][6] |
| 리소스별 (resource-specific) | 범주마다 전용 표[1] | 앞으로 모든 서비스가 이 방식으로 옮김[1] |

대부분의 리소스는 모드를 고를 수 없고, 일부 리소스만 진단 설정에서 모드를 고릅니다[1]. 기존 설정을 리소스별 모드로 바꾸면 이미 모인 데이터는 보관 기간이 끝날 때까지 `AzureDiagnostics` 에 남고 새 데이터만 전용 표로 갑니다[1]. 모드를 바꾼 시점을 사이에 둔 기간은 두 표를 `union` 으로 함께 조회합니다[1].

### 보관 기간 (2026년 9월 문서 기준)

리소스 로그는 목적지마다 보관 방식이 다릅니다. Storage 목적지는 진단 설정에서 보관 기간을 정할 수 없고, 로그 컨테이너에 수명 주기 관리 (lifecycle management) 정책을 걸어 관리합니다[8]. Event Hubs 로 보낸 로그는 받아 간 외부 시스템의 보관 설정을 따로 확인합니다. Log Analytics 작업 영역의 값은 아래와 같습니다[4].

| 항목 | 값 |
|---|---|
| 작업 영역 기본 보관 | 30일. 30일로 둔 작업 영역은 31일 동안 남을 수 있음[4] |
| `AzureActivity`·`Usage`·Application Insights 표 | 최소 90일 무료[4] |
| Analytics 표의 분석 보관 | 4일~730일(2년)[4] |
| 장기 보관을 포함한 총 보관 | 최대 12년(4,383일). 포털·API 로만 12년, CLI·PowerShell 은 7년까지[4] |
| Basic·Auxiliary 표 | 총 보관 기본 30일[4] |
| 보관 기간을 줄이면 | 30일 기다린 뒤 지움(되돌릴 여유)[4] |
| 보관 기간을 늘리면 | 아직 지워지지 않은 기존 데이터에도 적용[4] |
| 사용자 정의 표(`_CL`, Analytics·Basic) 삭제 | 데이터는 지워지지 않고 이름이 15일 동안 예약됨[4] |
| 검색 결과 표(`_SRCH`) 삭제 | 표와 데이터가 바로 영구 삭제[4] |

보관 기간과 라이선스를 서비스끼리 견주는 표는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 에 있습니다.

## 구조

### 공통 최상위 스키마

모든 리소스 로그는 같은 최상위 스키마를 쓰고, 서비스마다 고유한 값은 `properties` 안에 넣습니다[3]. 리소스 종류(`resourceId` 안에 있음)와 범주를 합치면 스키마가 하나로 정해집니다[3]. 아래 이름은 Storage·Event Hubs 로 보낸 로그의 이름이고, Log Analytics 에서는 열 이름이 다를 수 있습니다[3].

| 필드 | 필수 | 뜻 |
|---|---|---|
| `time` | 필수 | 이벤트 시각, UTC[3] |
| `resourceId` | 필수 | 이벤트를 낸 리소스. 테넌트 서비스는 `/tenants/테넌트ID/providers/공급자이름` 꼴[3] |
| `tenantId` | 테넌트 로그에서 필수 | 테넌트 수준 로그에만 나옴[3] |
| `operationName` | 필수 | 작업 이름. 대개 `Microsoft.공급자/리소스형식/하위형식/Write·Read·Delete·Action` 꼴이고, 예로 `Microsoft.Storage/storageAccounts/blobServices/blobs/Read`[3] |
| `operationVersion` | 선택 | API 로 한 작업이면 그 API 버전[3] |
| `category` 또는 `type` | 필수 | 로그 범주. 리소스에서 켜고 끄는 단위. 흔한 값 `Audit`·`Operational`·`Execution`·`Request`[3] |
| `resultType` | 선택 | `Started`·`In Progress`·`Succeeded`·`Failed`·`Active`·`Resolved` 등[3] |
| `resultSignature` | 선택 | 하위 상태. REST 호출이면 HTTP 상태 코드[3] |
| `resultDescription` | 선택 | 작업 설명 문구[3] |
| `durationMs` | 선택 | 걸린 시간(밀리초)[3] |
| `callerIpAddress` | 선택 | 공인 IP 에서 온 API 호출이면 호출한 쪽 IP[3] |
| `correlationId` | 선택 | 관련 이벤트를 묶는 GUID. 같은 작업의 `Started`·`Succeeded` 가 같은 값을 씀[3] |
| `identity` | 선택 | 작업한 사용자·앱을 적은 JSON. 대개 권한 정보와 Entra 토큰의 클레임이 들어감[3] |
| `level` | 선택 | `Informational`·`Warning`·`Error`·`Critical`[3] |
| `location` | 선택 | 이벤트를 낸 리소스의 지역[3] |
| `properties` | 선택 | 범주마다 다른 확장 속성[3] |

"선택" 필드는 리소스마다 비어 있을 수 있습니다. `identity` 와 `callerIpAddress` 가 모든 범주에 있다고 보지 않고, 범주별 스키마 문서에서 확인합니다. JSON 로그를 읽는 일반 방법은 [JSON 로그 읽기](../../01-foundations/logging/json-logs.md) 에서 다룹니다.

### Storage 목적지의 블롭 경로

Storage 계정으로 보내면 켜 둔 범주에서 이벤트가 처음 생길 때 컨테이너가 만들어지고, 블롭 이름은 아래 규칙을 따릅니다[1].

```
insights-logs-{log category name}/resourceId=/SUBSCRIPTIONS/{subscription ID}/RESOURCEGROUPS/{resource group name}/PROVIDERS/{resource provider name}/{resource type}/{resource name}/y={four-digit numeric year}/m={two-digit numeric month}/d={two-digit numeric day}/h={two-digit 24-hour clock hour}/m=00/PT1H.json
```

컨테이너 이름은 `insights-logs-` 뒤에 범주 이름을 붙인 것이라, 컨테이너 목록만 봐도 어떤 범주가 한 번이라도 기록됐는지 알 수 있습니다. 예를 들어 Key Vault 의 `AuditEvent` 범주는 `insights-logs-auditevent`, NSG 흐름 로그는 `insights-logs-networksecuritygroupflowevent` 컨테이너에 쌓입니다[10]. 블롭은 한 시간마다 하나라서 경로 끝의 `m=00` 은 늘 `00` 입니다[1]. 블롭 안에는 이벤트가 한 줄에 JSON 객체 하나씩 들어갑니다[1].

### Event Hubs 목적지

Event Hubs 로 보낸 로그는 한 번에 받는 묶음마다 `records` 배열 안에 레코드가 들어 있는 JSON 입니다[1]. 레코드 하나의 필드는 위 공통 스키마와 같습니다[1].

### Log Analytics 의 `AzureDiagnostics` 표

`AzureDiagnostics` 에는 로그를 낸 리소스의 `resourceId`, 로그 범주, 로그가 만들어진 시각과 리소스별 속성이 들어갑니다[1]. 이 표에는 작업 영역마다 적어도 같은 열 200개가 있고, 새 필드가 오면 열을 늘리다가 500개에 이르면 그 뒤의 새 필드는 `AdditionalFields` 라는 동적 열 안의 속성으로 넣습니다[6]. 열 이름 끝에는 `NewInfo1_s`, `Perf1Sec_i` 처럼 접미사가 붙습니다[6]. 같은 필드가 어떤 작업 영역에서는 열로, 다른 작업 영역에서는 `AdditionalFields` 안의 속성으로 있을 수 있어서, 쿼리를 다른 작업 영역에 그대로 옮겨 쓰면 결과가 빠질 수 있습니다.

## 증거로서 의미

**증명하는 것.** 진단 설정이 켜져 있던 기간에, 그 리소스에서 켜 둔 범주의 작업이 기록된 만큼입니다. `operationName`·`resultType`·`resultSignature` 로 어떤 작업을 했고 성공했는지, `identity` 와 `callerIpAddress` 가 있는 범주에서는 어느 주체가 어느 IP 에서 요청했는지를 알 수 있습니다[3]. `correlationId` 로 같은 작업의 시작·완료 이벤트를 묶을 수 있습니다[3].

**증명하지 못하는 것.** 진단 설정이 없던 기간과 켜지 않은 범주에는 기록 자체가 없습니다[1][2]. 로그가 없다는 사실은 그 작업이 없었다는 뜻이 아니고, 먼저 설정이 있었는지를 따져야 합니다. 설정이 있었더라도 손실이 없다는 보장이 없어서 한두 건이 빠진 것만으로 결론을 내리지 않습니다[1]. `identity` 가 비어 있는 범주에서는 누가 했는지를 이 로그만으로 말할 수 없고, [활동 로그](activity-log.md) 나 [Entra ID 로그](../m365/entra-logs/index.md) 와 맞춰 봐야 합니다.

보고서에는 "Key Vault A 의 `AuditEvent` 로그에 2026-09-01 03:10:14 UTC, 203.0.113.25 에서 비밀을 읽은 요청이 성공으로 기록되어 있다" 처럼 기록이 말하는 만큼만 씁니다(만든 예시). 로그가 없는 구간은 "이 기간에는 이 리소스에 진단 설정이 없어 리소스 로그가 남지 않았다" 처럼 공백의 이유와 함께 씁니다. 문장 쓰는 법은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에서 다룹니다.

## 시각 해석

공통 스키마의 `time` 은 이벤트 시각이고 UTC 입니다[3]. Log Analytics 에서는 한 레코드에 시각이 셋 붙습니다[5].

| 시각 | 뜻 | 주의 |
|---|---|---|
| `TimeGenerated` | 원천에서 레코드를 만든 시각[5] | 받은 시각보다 2일 넘게 이르거나 1일 넘게 미래면 받은 시각으로 바뀜. 원천이 값을 안 주면 `_TimeReceived` 와 같음[5] |
| `_TimeReceived` | 수집 끝점이 받은 시각[5] | 큰 데이터 거르기에는 쓰지 않음[5] |
| `ingestion_time()` | 작업 영역에 저장되어 조회할 수 있게 된 시각[5] | 작업 영역에 들어온 기간으로 거를 때 씀. `TimeGenerated` 조건을 더 넓게 함께 줌[5] |

리소스 로그는 보통 발생 뒤 3~10분 안에 조회할 수 있고, Azure SQL Database 와 Azure Virtual Network 는 5분마다 로그를 보냅니다[5]. 활동 로그는 3~20분, 플랫폼 메트릭은 1분 안에 메트릭 저장소에 들어오고 내보내기에 3분이 더 걸립니다[5]. 사고 직후에 조회한 결과가 비어 있다면 이 지연 시간이 지난 뒤 다시 조회합니다. 진단 설정을 새로 만든 경우에는 데이터가 흐르기 시작할 때까지 최대 90분이 걸릴 수 있고, 24시간이 지나도 아무것도 없으면 로그가 생기지 않았거나 전달 경로에 문제가 있을 수 있습니다[2].

Storage 목적지의 블롭 경로에 있는 날짜·시각은 로그를 받은 시각 기준입니다[1]. 그래서 한 블롭에 경로의 시간대 밖에서 생긴 로그가 들어 있을 수 있고, Application Insights 처럼 늦은 데이터를 올릴 수 있는 원천이면 48시간 전 데이터까지 들어갑니다[1]. 새 시간이 시작된 직후에는 이전 시간 블롭에 아직 쓰는 중일 수도 있습니다[1]. 사건 시각에 해당하는 블롭만 받지 말고, 앞뒤 몇 시간의 블롭까지 받아 줄마다 `time` 으로 다시 거릅니다. 여러 로그의 시각을 맞추는 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 에서 다룹니다.

## 함정과 한계

- **진단 설정을 지우거나 바꾸기.** 진단 설정을 지우거나 목적지를 바꾸면 그 순간부터 기록에 공백이 생깁니다. 설정을 바꾸는 권한의 작업 이름은 `Microsoft.Insights/DiagnosticSettings/Write`·`/Delete` 이고[7], 이 변경은 대상 리소스 경로 뒤에 붙은 꼴로 [활동 로그](activity-log.md) 의 `operationName` 에 나타날 수 있습니다. 예를 들어 Sigma 규칙은 NSG 의 진단 설정 쓰기를 `MICROSOFT.NETWORK/NETWORKSECURITYGROUPS/PROVIDERS/MICROSOFT.INSIGHTS/DIAGNOSTICSETTINGS/WRITE` 로 찾습니다[9]. 활동 로그에서 `diagnosticSettings` 가 들어간 작업 이름을 대소문자 구분 없이 먼저 검색합니다. 흐름은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md) 에서 다룹니다.
- **보관 기간 줄이기.** Log Analytics 의 보관 기간을 줄여도 30일 동안은 지우지 않으므로[4], 그 안이면 되돌려 데이터를 살릴 수 있습니다. 수집을 마치기 전에는 보관 설정을 건드리지 않습니다. 절차는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 에서 다룹니다.
- **남은 설정이 새 리소스에 붙음.** 리소스를 지우거나 이름을 바꾸거나 다른 리소스 그룹·구독으로 옮길 때 진단 설정을 지우지 않으면, 같은 이름으로 다시 만든 리소스에 옛 설정이 적용되어 수집이 다시 시작될 수 있습니다[2]. 같은 `resourceId` 의 로그라도 리소스를 다시 만든 시각 앞뒤로 다른 리소스일 수 있으므로 활동 로그의 생성·삭제 기록과 맞춰 봅니다.
- **자기 자신을 목적지로.** 포털에서는 Storage 계정이나 Event Hubs 네임스페이스가 자기 자신을 목적지로 고를 수 없지만, PowerShell·CLI·REST API·Resource Manager 템플릿으로는 만들 수 있습니다[2]. Blob Storage 문서는 같은 계정으로 보낼 수 없다고만 적어서[8] 두 문서가 다르므로, 검체의 진단 설정에서 목적지를 직접 확인합니다.
- **리소스 ID 의 비 ASCII 문자.** 리소스 ID 에 비 ASCII 문자가 있으면 진단 설정을 지원하지 않아 설정이 사라집니다[2]. 이런 리소스는 설정을 만든 기록이 있어도 로그가 없을 수 있습니다.
- **필드 이름이 목적지마다 다름.** Storage·Event Hubs 의 필드 이름과 Log Analytics 의 열 이름이 다를 수 있고[3], `AzureDiagnostics` 는 열 접미사와 `AdditionalFields` 때문에 작업 영역마다 쿼리가 달라집니다[6]. 목적지가 둘 이상이면 한쪽 사본만 보고 판단하지 않습니다.
- **모드 전환 뒤 두 표.** 리소스별 모드로 바꾼 뒤에는 옛 데이터와 새 데이터가 두 표에 나뉘어 있습니다[1].
- **블롭 수정 시각으로 거르기.** Goose 의 Storage 로그 수집 함수는 블롭의 `last_modified` 가 기간 안인 블롭만 받습니다[10]. 블롭은 받은 시각 기준으로 한 시간 동안 이어 쓰이므로[1], 기간 경계의 블롭이 빠지지 않게 기간을 넉넉히 줍니다.

## 직접 분석해 보기

**진단 설정 목록부터.** 구독의 리소스마다 진단 설정을 받아 어떤 범주가 어느 목적지로 갔는지 표로 만듭니다. Azure CLI 의 `az monitor diagnostic-settings` 명령 묶음이나 PowerShell 의 진단 설정 cmdlet 으로 받고[2], 결과 JSON 을 리소스 ID 와 함께 저장합니다. Untitled Goose Tool 의 `_dump_diagnostic_settings` 는 구독의 모든 리소스를 돌며 진단 설정을 받아 리소스 ID 를 붙여 `구독ID/azure_configs/diagnostic_settings.json` 에 한 줄씩 씁니다[10]. 이 목록이 지금 설정만 보여 준다는 점을 기억하고, 과거 설정은 활동 로그의 `diagnosticSettings` 변경 기록으로 되짚습니다.

**PT1H.json 직접 읽기.** 아래는 NSG 규칙 카운터 범주의 블롭 한 개를 흉내 낸 두 줄입니다. 문서 예시의 필드 가운데 일부만 남겼고 값은 모두 만든 예시입니다.

```json
{"time": "2026-09-01T03:00:37.2040000Z","systemId": "1a2b3c4d-0000-4000-8000-000000000001","category": "NetworkSecurityGroupRuleCounter","resourceId": "/SUBSCRIPTIONS/0A1B2C3D-0000-4000-8000-00000000000A/RESOURCEGROUPS/EXAMPLE-RG/PROVIDERS/MICROSOFT.NETWORK/NETWORKSECURITYGROUPS/EXAMPLE-NSG","operationName": "NetworkSecurityGroupCounters","properties": {"subnetPrefix": "10.3.0.0/24","ruleName": "/subscriptions/0a1b2c3d-0000-4000-8000-00000000000a/resourceGroups/example-rg/providers/Microsoft.Network/networkSecurityGroups/example-nsg/securityRules/default-allow-rdp","direction": "In","type": "allow","matchedConnections": 1988}}
{"time": "2026-09-01T02:58:12.0000000Z","systemId": "1a2b3c4d-0000-4000-8000-000000000001","category": "NetworkSecurityGroupRuleCounter","resourceId": "/SUBSCRIPTIONS/0A1B2C3D-0000-4000-8000-00000000000A/RESOURCEGROUPS/EXAMPLE-RG/PROVIDERS/MICROSOFT.NETWORK/NETWORKSECURITYGROUPS/EXAMPLE-NSG","operationName": "NetworkSecurityGroupCounters","properties": {"subnetPrefix": "10.3.0.0/24","ruleName": "/subscriptions/0a1b2c3d-0000-4000-8000-00000000000a/resourceGroups/example-rg/providers/Microsoft.Network/networkSecurityGroups/example-nsg/securityRules/default-allow-rdp","direction": "In","type": "allow","matchedConnections": 12}}
```

이 블롭의 경로가 `.../y=2026/m=09/d=01/h=03/m=00/PT1H.json` 이라면 두 번째 줄은 경로의 시간(03시)보다 앞선 02:58 에 생긴 이벤트입니다. 받은 시각 기준으로 블롭에 들어가기 때문에 이런 줄이 생깁니다[1]. 여러 블롭을 받아 합친 뒤 `time` 으로 정렬합니다.

```bash
find insights-logs-networksecuritygrouprulecounter -name PT1H.json -exec cat {} + \
  | jq -c 'select(.time >= "2026-09-01T02:00:00" and .time < "2026-09-01T04:00:00")' \
  | jq -s -r 'sort_by(.time)[] | [.time, .operationName, .properties.ruleName, .properties.matchedConnections] | @tsv'
```

`operationName` 이 `Microsoft.` 로 시작하는 꼴이 아닌 것도 볼 수 있는데, 공통 스키마의 작업 이름 규칙은 "대개" 그렇다는 것이지 강제가 아닙니다[3].

**Log Analytics 에서 읽기.** 작업 영역으로 보낸 경우 문서의 지연 측정 쿼리를 그대로 돌려 공급자마다 늦게 들어오는 정도를 봅니다[5].

```
AzureDiagnostics
| where TimeGenerated > ago(8h)
| extend E2EIngestionLatency = ingestion_time() - TimeGenerated
| extend AgentLatency = _TimeReceived - TimeGenerated
| summarize percentiles(E2EIngestionLatency,50,95), percentiles(AgentLatency,50,95) by ResourceProvider
```

Untitled Goose Tool 의 `dump_log_analytic_workspaces` 는 작업 영역 목록을 받은 뒤 `search "*"` 로 표마다 요약하고, 표마다 `표이름.json` 파일로 내려받습니다[10]. 기본 시작 시점은 지금에서 364×12일(4,368일) 전이라[10], 총 보관 최대치 4,383일[4]보다 15일 짧습니다. 계정 전체의 로그를 모으는 순서는 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md) 에서 다룹니다.

## 교차 검증

- [활동 로그](activity-log.md) — 진단 설정을 만들고 지운 기록, 리소스를 다시 만든 기록으로 로그 공백과 `resourceId` 의 주인을 확인합니다.
- [Storage 계정 기록](storage-logs.md) — Storage 의 리소스 로그 필드와 예전 방식인 Storage Analytics 로그를 다룹니다.
- [Key Vault 기록](key-vault.md) — `AuditEvent` 범주의 필드와 작업 이름을 다룹니다.
- [네트워크 흐름 로그](flow-logs.md) — 흐름 로그도 같은 `insights-logs-` 컨테이너 규칙으로 Storage 에 쌓입니다.
- [Entra ID 로그](../m365/entra-logs/index.md) — `identity` 에 적힌 주체와 IP 를 로그인 기록과 맞춰 봅니다.
- [CloudWatch Logs](../aws/cloudwatch-logs.md) — AWS 에서 서비스 로그를 모으는 비슷한 구조입니다.
- [클라우드 타임라인](../../03-techniques/analysis/timeline.md) — 리소스 로그의 `time` 을 다른 로그와 시간순으로 합칩니다.

## 실습

Microsoft 문서의 예시와 위의 만든 예시로 풀어 봅니다.

1. 문서의 NSG 블롭 이름 예시[1]에서 구독 ID, 리소스 그룹, 리소스 이름, 범주, 블롭의 날짜·시간을 나눠 적어 봅니다.
2. 위 만든 예시 두 줄이 같은 `h=03` 블롭에 들어 있는 이유를 설명하고, 02시대 사건을 조사할 때 어느 블롭까지 받아야 하는지 적어 봅니다[1].
3. 리소스별 모드로 바꾼 날이 조사 기간 한가운데 있다면 어떤 표 두 개를 어떻게 합쳐 조회할지 쿼리 모양을 적어 봅니다[1].
4. 누가 Log Analytics 작업 영역의 보관 기간을 90일에서 30일로 줄였다면, 언제까지 되돌려야 데이터를 살릴 수 있는지 적어 봅니다[4].
5. 실제 구독에서는 모든 리소스의 진단 설정을 받아 리소스·범주·목적지·수집 모드를 표로 만들고, 활동 로그의 `diagnosticSettings` 변경 기록과 맞춰 사고 기간에 기록이 있어야 할 리소스와 없을 리소스를 나눠 봅니다.

## 참고 문헌

1. Microsoft, "Resource logs in Azure Monitor", Azure Monitor documentation. https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs.md
2. Microsoft, "Diagnostic settings in Azure Monitor", Azure Monitor documentation. https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/data-collection/diagnostic-settings.md
3. Microsoft, "Common and service-specific schemas for Azure resource logs", Azure Monitor documentation. https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs-schema.md
4. Microsoft, "Manage data retention in a Log Analytics workspace", Azure Monitor documentation. https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/data-retention-configure.md
5. Microsoft, "Log data ingestion time in Azure Monitor", Azure Monitor documentation. https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-ingestion-time
6. Microsoft, "AzureDiagnostics", Azure Monitor Logs table reference. https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/azurediagnostics
7. Microsoft, "Azure permissions for Monitor", Azure RBAC documentation. https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/monitor
8. Microsoft, "Monitor Azure Blob Storage", Azure Storage documentation. https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/storage/blobs/monitor-blob-storage.md
9. SigmaHQ, "Azure Network Security Configuration Modified or Deleted" (azure_network_security_modified_or_deleted.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_network_security_modified_or_deleted.yml
10. CISA, Untitled Goose Tool (goosey/azure_dumper.py). https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/azure_dumper.py
