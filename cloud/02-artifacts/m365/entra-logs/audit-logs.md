---
title: "감사 로그"
parent: "Entra ID 로그"
grand_parent: "아티팩트 · Microsoft 365"
nav_order: 190
---

# 감사 로그 (Audit Logs)

Entra ID 감사 로그는 테넌트 안에서 사용자·그룹·앱·역할·정책을 누가 언제 어떻게 바꿨는지 남기는 디렉터리 변경 기록이고, 바뀌기 전 값과 바뀐 뒤 값까지 담습니다[1].

## 무엇을 기록하나 · 왜 생기나

Entra ID 는 사용자·그룹·응용 프로그램·라이선스의 변경을 감사 로그에 기록하고, 사용자 지정 보안 특성 (custom security attributes) 과 에이전트 (agent) 에 대한 변경도 같은 로그에 남깁니다[1]. 관리자가 관리 센터에서 바꾼 것뿐만 아니라 앱이 API 로 바꾼 것, 사용자가 스스로 인증 수단을 등록한 것까지 들어옵니다[2][3]. 항목은 시스템이 만들고, 바꾸거나 지울 수 없습니다[1].

침해 조사에서 감사 로그가 답하는 질문은 "로그인한 뒤 계정·권한 구조를 어떻게 바꿨나" 입니다. 공격자가 오래 머물려고 남기는 흔적, 즉 새 앱 등록과 앱 비밀 추가, 앱 동의, 역할 부여, 인증 수단 등록, 도메인 페더레이션 변경, 조건부 접근 정책 수정이 모두 감사 로그의 활동 이름으로 남습니다[2]. 로그인 자체는 이 로그가 아니라 [로그인 로그](sign-in-logs.md) 에 남습니다.

Microsoft 365 구독이 있으면 Exchange Online 이 디렉터리를 맞추려고 Entra ID 에 쓰는 만들기·고치기·지우기 작업도 감사 로그에 들어옵니다. 이런 항목은 작업자가 "Microsoft Substrate Management" 로 표시되고, 정보용 기록입니다[1].

## 위치와 보관

관리 센터에서는 **Entra ID > Monitoring & health > Audit logs** 에서 봅니다[2]. 화면 기본 탭은 **Directory** 이고, 사용자 지정 보안 특성 변경은 **Custom Security** 탭에 따로 나오며 이 탭은 Attribute Log Administrator 나 Attribute Log Reader 역할이 있어야 보입니다[1].

같은 기록을 받는 경로와 보관 기간은 [Entra ID 로그](index.md) 에 표로 정리했습니다. 이 페이지에 필요한 것만 추리면 아래와 같습니다(2026년 1월 문서 기준).

| 항목 | 값 |
|---|---|
| Entra ID 안 보관 기간 | Free 7일, P1·P2 30일[4] |
| 관리 센터 내려받기 | CSV·JSON, 파일 하나에 250,000건까지, 시각은 UTC[5] |
| Graph API | `auditLogs/directoryAudits`(자원 이름 `directoryAudit`)[3][11][12] |
| Log Analytics 표 | `AuditLogs`[6][7] |
| 통합 감사 로그 사본 | 레코드 유형 `AzureActiveDirectory`[10], E5 계열은 Purview Audit (Premium) 보존 정책으로 더 길게 둘 수 있음[4] |

보관 기간은 출처끼리 적은 값이 다릅니다. 조건부 접근 문서는 감사 로그 데이터를 기본 30일 보관한다고 적었지만[6], 보관 기간 문서의 표는 Free 7일, P1·P2 30일로 나눕니다[4]. 테넌트의 라이선스를 먼저 확인하고 짧은 쪽을 기준으로 수집을 서두릅니다.

## 구조

Graph `directoryAudit` 자원 하나가 감사 항목 하나입니다[3].

| 필드 | 뜻 |
|---|---|
| `id` | 항목 고유 ID(GUID) |
| `activityDateTime` | 활동을 한 시각. 항상 UTC 이고 `2014-01-01T00:00:00Z` 형식 |
| `activityDisplayName` | 활동 이름(예: `Add member to group`) |
| `category` | 대상 자원의 범주(예: `UserManagement`, `GroupManagement`, `ApplicationManagement`, `RoleManagement`) |
| `loggedByService` | 기록한 서비스(예: `Core Directory`, `Self-service Password Management`, `Invited Users`, `Privileged Identity Management`) |
| `operationType` | `Add`, `Assign`, `Update`, `Unassign`, `Delete` 등 |
| `result` · `resultReason` | `success`, `failure`, `timeout`, 실패·시간 초과면 그 이유 |
| `initiatedBy` | 작업을 한 주체. 사용자면 `user`(`id`, `displayName`, `userPrincipalName`), 앱이면 `app`(`appId`, `displayName`) |
| `targetResources` | 바뀐 대상. 유형은 `User`, `Device`, `Directory`, `App`, `Role`, `Group`, `Policy`, `Other` |
| `correlationId` | 여러 서비스에 걸친 활동을 묶는 ID |
| `additionalDetails` | 키·값 목록으로 된 추가 정보 |

화면에서 항목을 고르면 Correlation ID, 작업자와 대상, 그리고 해당하는 경우 바뀐 속성의 옛 값과 새 값이 나옵니다[1]. 바뀐 속성은 `targetResources` 안의 `modifiedProperties` 에 들어 있고, 옛 값과 새 값은 JSON 입니다[6]. 속성 이름은 `displayName`, 값은 `oldValue`·`newValue` 에 들어가며, 값은 `"[\"Guest\"]"` 처럼 JSON 배열을 한 번 더 문자열로 감싼 형식입니다[8]. 조건부 접근 정책을 고친 항목이라면 정책 전체 JSON 이 옛 값과 새 값으로 통째로 들어가서, 두 값을 비교해야 무엇이 바뀌었는지 보입니다[6].

감사 로그 상세의 IP 주소는 OAuth 클라이언트의 IP, 곧 서비스 끝점 (endpoint) 에 TCP 로 붙은 상대 주소입니다[1].

### 조사에서 자주 보는 활동 이름

활동 이름은 서비스와 범주별로 수백 개가 있고 수시로 바뀝니다[2]. 아래는 2025년 3월 문서 기준으로 침해 조사에서 자주 찾는 것만 추렸습니다[2].

| 범주 | 활동 이름 | 찾는 이유 |
|---|---|---|
| ApplicationManagement | `Add application`, `Add service principal` | 새 앱 등록 |
| ApplicationManagement | `Add service principal credentials`, `Update application - Certificates and secrets management` | 앱 비밀·인증서 추가 |
| ApplicationManagement | `Consent to application`, `Add delegated permission grant`, `Add app role assignment to service principal` | 앱에 대한 동의와 권한 부여 |
| ApplicationManagement | `Add owner to application` | 앱 소유자 추가 |
| RoleManagement | `Add member to role`, `Add eligible member to role` | 관리 역할 부여 |
| UserManagement | `Add user`, `Delete user`, `Restore user`, `Change user password` | 계정 만들기·지우기·되살리기, 비밀번호 변경 |
| UserManagement | `Disable Strong Authentication`, `User registered security info`, `Admin registered security info` | 다단계 인증 끄기, 인증 수단 등록 |
| UserManagement | `Update StsRefreshTokenValidFrom Timestamp` | 사용자의 `StsRefreshTokenValidFrom` 시각 변경 |
| DirectoryManagement | `Set domain authentication`, `Set federation settings on domain` | 도메인 인증 방식·페더레이션 변경 |
| Policy | `Add Conditional Access policy`, `Update Conditional Access policy`, `Delete Conditional Access policy` | 조건부 접근 정책 변경 |
| KeyManagement | `Read BitLocker key` | BitLocker 복구 키 조회 |

권한 관리 (PIM) 는 같은 역할 부여라도 `Add eligible member to role in PIM requested (timebound)` 처럼 요청·완료·취소와 기간 유형을 붙인 이름을 따로 씁니다[2]. 앱 동의와 권한 부여가 무엇을 뜻하는지는 [OAuth 앱과 동의](../../../01-foundations/identity/oauth-consent.md) 에, 역할 구조는 [클라우드 계정과 역할](../../../01-foundations/identity/users-roles.md) 에 있습니다.

## 외부 인증 방법 추가와 변경

외부 인증 방법 (external authentication method, EAM) 은 다단계 인증의 두 번째 단계를 Microsoft 가 아닌 외부 공급자에게 맡기는 기능이고, 지금 Microsoft 문서는 외부 MFA (external MFA) 라고 부릅니다[14]. 사용자가 이 방법을 고르면 Entra ID 가 브라우저를 공급자에게 보내고, 공급자가 서명해 돌려준 토큰이 검증을 통과하면 다단계 인증을 채운 것으로 처리합니다[15]. 그래서 공격자가 만든 공급자가 등록되면 그 공급자가 돌려준 토큰으로도 다단계 인증을 통과합니다[15][18]. 2026년 9월에 공개된 한 시험 테넌트에서는 이렇게 등록한 공급자가 다단계 인증 단계에서 비밀번호 입력 화면을 띄워 비밀번호를 받아 갔고, 비밀번호를 재설정한 뒤에도 다음 로그인에서 새 비밀번호를 다시 받아 갔습니다[18]. 아래에서 "시험에서는" 이라고 적은 값은 모두 이 시험 환경의 값입니다.

**설정이 놓이는 곳과 필요한 역할.** 공급자 정보는 테넌트의 인증 방법 정책 (Authentication methods policy) 에 `externalAuthenticationMethodConfiguration` 유형의 항목으로 들어갑니다[15]. 항목에는 사용자에게 보이는 이름 `displayName`, 공급자 연동 앱의 `appId`, 공급자 OIDC 설정 `openIdConnectSetting`(`clientId`, `discoveryUrl`), 켜짐 여부 `state`(`enabled`·`disabled`), 이 방법을 쓸 그룹 `includeTargets` 와 뺄 그룹 `excludeTargets` 가 있고, `displayName` 은 만든 뒤에 바꿀 수 없습니다[14][16][17]. 관리 센터에서 외부 인증 방법을 추가하려면 최소 Authentication Policy Administrator 역할이 필요하고, 공급자 앱에 관리자 동의 (admin consent) 를 주려면 최소 Privileged Role Administrator 역할이 필요합니다[14]. 동의 없이 저장한 방법은 켤 수 없고, Graph 로 정책을 바꾸려면 `Policy.ReadWrite.AuthenticationMethod` 권한이 있어야 합니다[14]. 변경한 계정이 Authentication Policy Administrator 나 Global Administrator 역할을 언제 받았는지 위 표의 역할 부여 활동으로 함께 확인합니다[14][18].

**감사 로그에 남는 활동.** 외부 인증 방법은 인증 방법 정책 안의 항목이라[15], 감사 로그에서는 인증 방법 정책 변경 활동인 `Authentication Methods Policy Update` 부터 찾고, 정책을 초기화했다면 `Authentication Methods Policy Reset` 도 봅니다. 두 활동 모두 범주는 `ApplicationManagement` 입니다[2]. 무엇을 바꿨는지는 그 항목의 `modifiedProperties` 에서 옛 값과 새 값을 비교해 확인합니다. 시험에서는 공급자 하나를 등록하자 외부 방법 추가, 사용자 개체 갱신, 방법 등록 확인의 세 기록이 차례로 남았고, 시험 사용자의 `SearchableDeviceKey` 속성에 FIDO 키가 하나 붙었습니다[18]. 세 기록의 실제 활동 이름은 받은 데이터에서 `Authentication Methods Policy Update` 앞뒤 몇 분의 항목을 펼쳐 확인합니다. 사용자별 등록은 관리자가 대신 할 수도 있고 사용자가 보안 정보 (Security info) 화면이나 등록 마법사에서 할 수도 있으므로[14], `Admin registered security info` 와 `User registered security info` 를 함께 찾습니다[2]. 외부 인증 방법을 쓸 수 있는 사용자는 인증 방법 등록 보고서에 나오지 않아서[14], 등록 보고서만 보고 판단하면 빠집니다.

**앱 등록과 서비스 주체.** 공급자는 Entra ID 앱 하나로 연동합니다. 이 앱은 Microsoft Graph 의 위임 권한 `openid`·`profile` 을 요청하고, 공급자의 `authorization_endpoint` 를 회신 URL 로 둡니다[15]. 테넌트에서는 이 앱에 관리자 동의를 해야 서비스 주체가 생기고 연동이 동작합니다[15]. 정책 항목의 `appId` 를 기준으로 `Add application`, `Add service principal`, `Consent to application`, `Add delegated permission grant` 기록을 찾아 같은 앱인지 맞춰 보고[2][16], 회신 URL 과 `discoveryUrl` 의 도메인이 테넌트가 계약한 공급자의 것인지 확인합니다. 시험에서 공격용 앱은 `openid`·`profile` 을 요청하고 리디렉션 URI 로 `login.microsoftonline.com/common/federation/externalauthprovider` 를 적었습니다[18]. 이 주소는 공급자가 응답을 돌려보내는 Microsoft 쪽 주소입니다[15]. 같은 시험에서 서비스 주체 생성 기록에는 앱 ID, 로그인 대상 (sign-in audience), 공격자 서버(시험에서는 ngrok 도메인)를 가리키는 회신 URL, 토큰 서명용 키가 담겼습니다[18]. 연구진의 배포 도구는 `Add application`, `Add service principal`, `Add delegated permission grant` 를 몇 초 사이에 연달아 남겼고, 이 Graph 호출의 사용자 에이전트는 모두 `python-requests/2.33.1` 이었습니다[18].

**로그인 로그의 단서.** Entra ID 는 공급자 토큰의 `acr`·`amr` 조합으로 두 번째 단계가 다단계 인증 조건을 채우는지 판단하고, 토큰의 `iss` 는 공급자 discovery 문서의 발급자 (issuer) 값과 글자까지 같아야 합니다[15]. 받아들이는 값은 `acr` 이 `possessionorinherence` 등 일곱 가지, `amr` 이 하드웨어 보안 키 소유 증명을 뜻하는 `hwk` 등 열세 가지입니다[15]. 시험에서는 공급자를 거친 로그인마다 공급자의 발급자 URL 이 남았고, 토큰에는 `acr` 값 `possessionorinherence` 와 `amr` 값 `["hwk"]` 가 들어 있었습니다[18]. 정상 공급자도 같은 값을 돌려줄 수 있으므로 값 하나로 판단하지 않고, 발급자 URL 이 테넌트가 승인한 공급자의 것인지부터 확인합니다. 낯선 발급자를 거쳐 로그인한 사용자를 모두 골라내면 피해 범위가 됩니다. 공급자가 켜져 있으면 재설정한 새 비밀번호도 다음 로그인에서 다시 넘어가므로 비밀번호를 재설정하기 전에 정책에서 그 공급자를 끄고 대상 그룹을 빼야 합니다[18].

**증명하는 것과 증명하지 못하는 것.** 인증 방법 정책 변경 기록으로는 누가 언제 정책을 바꿨는지 확인되지만, 그 공급자가 정상 업체인지, 공급자 화면에서 사용자가 무엇을 입력했는지는 알 수 없습니다. 감사 로그 보관 기간이 지나도 설정은 남아 있으므로, Graph 의 `externalAuthenticationMethodConfiguration` 객체로 현재 값을 읽어 감사 기록과 맞춰 봅니다[16].

## 증거로서 의미

**증명하는 것.** 어느 주체(`initiatedBy`)가 어느 대상(`targetResources`)에 어떤 활동(`activityDisplayName`)을 했고, 그 시각(UTC)과 결과(`result`)가 무엇이었는지, 그리고 바뀐 속성의 옛 값과 새 값입니다. 보고서에는 "2026-03-02 01:14 UTC 에 계정 A 가 앱 B 에 비밀을 추가한 기록이 있다"(만든 예시) 처럼 기록으로 확인되는 만큼 씁니다.

**증명하지 못하는 것.** 변경의 의도, 그리고 그 계정을 실제로 누가 쓰고 있었는지는 알려 주지 않습니다. `initiatedBy` 가 앱이면 사람이 아니라 앱 자격 증명으로 한 작업이라서, 그 앱의 비밀이 언제 누구에게 추가됐는지를 거꾸로 따라가야 합니다. 바뀐 설정이 그 뒤 실제로 쓰였는지(예: 추가된 앱 비밀로 로그인했는지)는 로그인 로그의 서비스 주체 로그인에서 따로 확인합니다.

## 시각 해석

`activityDateTime` 은 활동을 한 시각이고 항상 UTC 입니다[3]. 관리 센터에서 내려받은 파일도 UTC 입니다[5]. 화면 표시 시간대와 Log Analytics 의 `TimeGenerated` 처럼 경로마다 달라지는 시각 문제는 [Entra ID 로그](index.md) 와 [로그인 로그](sign-in-logs.md) 에 정리했습니다.

진단 설정으로 보낸 기록은 약 5분 단위로 묶여 나가므로[13], 목적지에서는 활동 시각과 도착 시각 사이에 몇 분의 차이가 있을 수 있습니다. 순서를 맞출 때는 도착 시각이 아니라 `activityDateTime` 을 기준으로 합니다.

## 함정과 한계

- **필드 이름이 수집 경로마다 다릅니다.** Graph 는 `activityDisplayName` 처럼 소문자로 시작하고[3], Log Analytics 의 `AuditLogs` 표는 `OperationName`, `TargetResources` 처럼 대문자로 시작합니다[6][7]. 공개 탐지 규칙도 같은 활동을 규칙마다 `OperationName`, `operationName`, `properties.message` 처럼 다른 키로 찾으므로[8], 받은 데이터의 실제 키 이름을 먼저 확인합니다.
- **활동 이름 표기가 출처마다 다를 수 있습니다.** 활동 목록 문서는 `Add eligible member to role` 로 적었지만[2], 공개 탐지 규칙은 `Add eligible member (permanent)`, `Add eligible member (eligible)` 로 찾습니다[8]. 목록 문서는 실제 서비스와 어긋날 수 있다고 스스로 밝히므로[2], 받은 데이터에서 실제 이름을 뽑아 본 뒤 검색합니다.
- **통합 감사 로그 사본은 이름 끝에 마침표가 붙습니다.** 통합 감사 로그의 `AzureActiveDirectory` 레코드는 `Consent to application.`, `Add OAuth2PermissionGrant.`, `Disable Strong Authentication.` 처럼 끝에 마침표가 붙은 작업 이름으로 검색합니다[9][10]. Entra ID 쪽 이름 그대로 검색하면 빠집니다.
- **옛 값·새 값은 문자열 안의 JSON 입니다.** 한 번 더 풀어야 값을 비교할 수 있고, 조건부 접근 정책처럼 큰 객체는 두 JSON 을 통째로 비교해야 합니다[6].
- **다단계 인증 끄기가 한 이름으로만 남지 않습니다.** `Disable Strong Authentication` 활동 말고도, `Update user` 활동의 바뀐 속성 `StrongAuthenticationRequirement` 새 값에 `State":0` 이 들어간 형태로 찾는 규칙이 있습니다[8]. 활동 이름 하나로만 찾지 말고 바뀐 속성까지 봅니다.
- **정보용 항목이 많습니다.** "Microsoft Substrate Management" 가 작업자인 항목은 Exchange Online 의 동기화 기록이라[1], 사람의 작업으로 읽지 않습니다.
- **보관 기간이 짧습니다.** Free 는 7일입니다[4]. 사고를 알게 되면 [로그부터 지키기](../../../03-techniques/acquisition/log-preservation.md) 에 따라 먼저 내보냅니다.

## 직접 분석해 보기

### 레코드 한 건 읽기

아래는 Graph `directoryAudit` 필드로 만든 예시입니다. 관리자 계정이 게스트 사용자를 멤버로 바꾼 항목이고, 바뀐 속성의 모양은 공개 탐지 규칙이 찾는 문자열과 같습니다[3][8].

```json
{
  "id": "0f1e2d3c-4b5a-4968-8776-a5b4c3d2e1f0",
  "category": "UserManagement",
  "correlationId": "11111111-2222-3333-4444-555555555555",
  "result": "success",
  "resultReason": "",
  "activityDisplayName": "Update user",
  "activityDateTime": "2026-03-02T01:14:07Z",
  "loggedByService": "Core Directory",
  "operationType": "Update",
  "initiatedBy": {
    "user": {
      "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
      "displayName": "Alex Kim",
      "userPrincipalName": "alex@contoso.com"
    }
  },
  "targetResources": [
    {
      "type": "User",
      "displayName": "Sam Lee",
      "modifiedProperties": [
        {
          "displayName": "UserType",
          "oldValue": "[\"Guest\"]",
          "newValue": "[\"Member\"]"
        }
      ]
    }
  ],
  "additionalDetails": []
}
```

읽는 순서는 이렇습니다. `activityDisplayName` 과 `category` 로 어떤 종류의 변경인지 보고, `initiatedBy` 로 사람(`user`)인지 앱(`app`)인지 확인합니다. `targetResources` 로 대상을 확인한 뒤 `modifiedProperties` 의 `oldValue`·`newValue` 를 풀어 무엇이 바뀌었는지 봅니다. 이 예시라면 외부 게스트였던 계정이 테넌트 멤버가 됐다는 뜻입니다. 마지막으로 `correlationId` 가 같은 항목을 모아 한 작업이 여러 줄로 나뉘어 남았는지 확인합니다.

### 공개 도구로 받기

- **Microsoft-Extractor-Suite** 는 `v1.0/auditLogs/directoryAudits` 를 `activityDateTime` 범위로 거르고, 사용자를 지정하면 `initiatedBy/user/userPrincipalName` 으로, `-All` 을 주면 그 사용자가 대상인 항목까지 받습니다[11].
- **Untitled Goose Tool** 은 `beta/auditLogs/directoryAudits` 에서 받습니다[12].
- **Hawk** 의 `Get-HawkTenantEntraIDAuditLog` 는 최근 30일의 감사 로그를 Graph 로 받아 `EntraIDAuditLogs.csv`·`EntraIDAuditLogs.json` 으로 저장하고, `Get-HawkTenantEntraIDAppAuditLog` 는 통합 감사 로그에서 앱 동의 관련 사건만 따로 찾습니다[10].

도구 설치와 인증 설정은 [Microsoft 365 수집 도구](../../../03-techniques/acquisition/m365-collection.md) 에서 다룹니다.

### Log Analytics 로 좁히기

진단 설정으로 `AuditLogs` 표를 쌓고 있다면 아래처럼 활동별 개수부터 봅니다[7].

```kusto
AuditLogs
| where TimeGenerated >= ago(7d)
| summarize auditCount = count() by OperationName
```

조건부 접근 정책 변경만 보려면 `OperationName == "Update Conditional Access policy"` 로 거르고 `TargetResources` 안의 `modifiedProperties` 를 펼칩니다[6].

## 교차 검증

| 함께 볼 기록 | 맞춰 보는 것 |
|---|---|
| [로그인 로그](sign-in-logs.md) | 변경 직전 `initiatedBy` 계정의 로그인 IP·기기·결과, 새로 비밀을 받은 앱(서비스 주체)의 로그인 |
| [위험 탐지](identity-protection.md) | 변경한 계정이 같은 시기에 위험 사용자로 표시됐는지 |
| [통합 감사 로그](../unified-audit-log/index.md) | `AzureActiveDirectory` 레코드로 남은 같은 변경, 그리고 Entra ID 보관 기간이 지난 뒤의 사본 |
| [Azure 활동 로그](../../azure/activity-log.md) | 같은 계정이 Azure 구독 자원을 바꾼 기록 |

변경들을 시간 순으로 엮는 방법은 [권한 변화 따라가기](../../../03-techniques/analysis/permission-changes.md) 와 [클라우드 타임라인](../../../03-techniques/analysis/timeline.md) 에 있습니다.

## 실습

시험용 테넌트를 하나 만들어 아래 작업을 직접 해 보고, 감사 로그에 어떻게 남는지 확인합니다.

1. 앱을 하나 등록하고 클라이언트 비밀을 추가합니다. `Add application`, `Add service principal`, 비밀 추가 활동이 몇 줄로 남고, 그 줄들의 `correlationId` 가 같은지 확인합니다.
2. 사용자 한 명에게 인증 수단을 등록하고 다른 사용자는 스스로 등록하게 합니다. `Admin registered security info` 와 `User registered security info` 가 `initiatedBy` 에서 어떻게 달라지는지 봅니다.
3. 조건부 접근 정책 하나의 조건을 바꿉니다. 옛 값과 새 값 JSON 을 비교해 바뀐 부분만 골라냅니다.
4. 같은 기간을 관리 센터 내려받기(JSON), Graph, 통합 감사 로그로 각각 받아 필드 이름과 활동 이름 표기가 어떻게 다른지 표로 만듭니다.

## 참고 문헌

1. Microsoft, "What are Microsoft Entra audit logs?" (ms.date 2026-06-05). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-audit-logs.md
2. Microsoft, "Microsoft Entra audit log categories and activities" (ms.date 2025-03-25). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
3. Microsoft, "directoryAudit resource type" (갱신 2024-05-24). https://learn.microsoft.com/en-us/graph/api/resources/directoryaudit
4. Microsoft, "Microsoft Entra data retention" (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
5. Microsoft, "How to download logs in Microsoft Entra ID" (ms.date 2024-11-08). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/howto-download-logs.md
6. Microsoft, "Use audit logs to troubleshoot Conditional Access policy changes" (갱신 2026-03-25). https://learn.microsoft.com/en-us/entra/identity/conditional-access/troubleshoot-policy-changes-audit-log
7. Microsoft, "Analyze Microsoft Entra activity logs with Log Analytics" (ms.date 2026-02-27). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/howto-analyze-activity-logs-log-analytics.md
8. SigmaHQ, Sigma 규칙 `rules/cloud/azure/audit_logs/`(`azure_app_credential_added.yml`, `azure_change_to_authentication_method.yml`, `azure_priviledged_role_assignment_add.yml`, `azure_guest_to_member.yml`, `azure_user_account_mfa_disable.yml` 등). https://github.com/SigmaHQ/sigma/tree/master/rules/cloud/azure/audit_logs
9. SigmaHQ, Sigma 규칙 `rules/cloud/m365/audit/microsoft365_disabling_mfa.yml`. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/audit/microsoft365_disabling_mfa.yml
10. T0pCyber, Hawk, `Hawk/functions/Tenant/Get-HawkTenantEntraIDAuditLog.ps1`, `Get-HawkTenantEntraIDAppAuditLog.ps1`. https://github.com/T0pCyber/hawk
11. invictus-ir, Microsoft-Extractor-Suite, `Scripts/Get-AzureEntraGraphLogs.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureEntraGraphLogs.ps1
12. CISA, Untitled Goose Tool, `goosey/entra_id_datadumper.py`. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/entra_id_datadumper.py
13. Microsoft, "Microsoft Entra activity log integration options and considerations" (ms.date 2025-05-27). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-log-monitoring-integration-options-considerations.md
14. Microsoft, "How to manage external MFA in Microsoft Entra ID" (ms.date 2026-02-24). https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-authentication-external-method-manage
15. Microsoft, "Microsoft Entra External MFA Method Provider Reference" (ms.date 2026-02-23). https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-external-method-provider
16. Microsoft, "externalAuthenticationMethodConfiguration resource type", Microsoft Graph v1.0 (ms.date 2026-01-19). https://learn.microsoft.com/en-us/graph/api/resources/externalauthenticationmethodconfiguration
17. Microsoft, "openIdConnectSetting resource type", Microsoft Graph v1.0 (ms.date 2026-01-19). https://learn.microsoft.com/en-us/graph/api/resources/openidconnectsetting
18. Elad Ghvarh, "TrustSink", Varonis Threat Labs (2026-09-16). https://www.varonis.com/blog/trustsink
