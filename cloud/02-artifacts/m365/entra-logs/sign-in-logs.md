---
title: "로그인 로그"
parent: "Entra ID 로그"
grand_parent: "아티팩트 · Microsoft 365"
nav_order: 180
---

# 로그인 로그 (Sign-in Logs)

Microsoft Entra ID 가 인증 요청을 처리할 때마다 남기는 기록으로, 어느 계정이 언제 어느 IP 에서 어느 앱·리소스에 로그인을 시도했고 결과가 어땠는지를 알려 줍니다.

## 무엇을 기록하나 · 왜 생기나

로그인 로그는 네 종류로 나뉩니다[1]. 사람이 화면에서 직접 인증하면 대화형 사용자 로그인 (interactive user sign-in) 이 남고, 클라이언트 앱이나 운영체제 구성 요소가 사용자를 대신해 토큰을 받으면 비대화형 사용자 로그인 (non-interactive user sign-in) 이 남습니다[2]. 앱 자체의 자격 증명으로 인증하면 서비스 주체 로그인 (service principal sign-in), Azure 자원이 관리 ID 로 인증하면 관리 ID 로그인 (managed identity sign-in) 이 남습니다[1]. 옛 로그인 로그 화면은 대화형 사용자 로그인만 보여 주므로, 화면 하나만 보고 "기록이 없다" 고 판단하면 안 됩니다[1].

비대화형 로그인에는 리프레시 토큰으로 액세스 토큰을 받는 요청, 인가 코드를 토큰으로 바꾸는 요청, Entra 조인 PC 에서 인증 입력 없이 이뤄지는 SSO, 모바일에서 FOCI (Family of Client IDs) 로 두 번째 Office 앱에 로그인하는 경우가 들어갑니다[2]. 2025년 4월 11일부터는 FIDO2 키로 리프레시 토큰을 새로 받는 로그인도 비대화형 로그에 기록합니다[2].

로그인 로그 항목은 시스템이 만들고, 바꾸거나 지울 수 없습니다[1][2]. 로그인 뒤에 무엇을 했는지는 이 로그에 없고, 디렉터리 변경은 [감사 로그](audit-logs.md), 위험 판정은 [위험 탐지](identity-protection.md) 쪽에 남습니다.

## 위치와 버전별 차이

같은 기록을 어느 경로로 받느냐에 따라 필드 이름과 보관 기간이 달라집니다.

| 받는 경로 | 이름·위치 | 조건 |
|---|---|---|
| Entra 관리 센터 화면·다운로드 | 모니터링 및 상태 > 로그인 로그, CSV·JSON 내려받기 | 최소 역할 Reports Reader[5] |
| Microsoft Graph v1.0 | `signIn` 리소스 (`auditLogs/signIns`) | Entra ID P1 또는 P2[6] |
| Microsoft Graph beta | `signIn` 리소스, `signInEventTypes` 로 네 종류 구분 | Premium 라이선스[5][7] |
| Log Analytics (진단 설정) | `SigninLogs`, `AADNonInteractiveUserSignInLogs`, `AADServicePrincipalSignInLogs`, `AADManagedIdentitySignInLogs`, `ADFSSignInLogs` 테이블 | 진단 설정을 켠 뒤부터 쌓임[8][9] |

Entra 안의 보관 기간은 라이선스에 따라 다릅니다(2026년 1월 문서 기준)[4].

| 보고서 | Entra ID Free | P1 | P2 |
|---|---|---|---|
| 로그인 (Sign-ins) | 7일 | 30일 | 30일 |
| 위험 로그인 (Risky sign-ins) | 7일 | 30일 | 90일 |

Free 에서 P1·P2 로 올려도 이미 지난 기록은 돌아오지 않고, 올리는 시점에 남아 있던 최대 7일분만 볼 수 있습니다[4]. 더 오래 두려면 Azure Monitor 로 Azure 저장소 계정에 보내 보관합니다[4]. Entra 로그인 로그는 Microsoft 365 [통합 감사 로그](../unified-audit-log/index.md)와 저장소·보관이 따로이고, Entra 라이선스를 바꿔도 통합 감사 로그 보관에는 영향이 없습니다[4]. 보관 기간 전반은 [보관 기간과 라이선스](../../../01-foundations/logging/retention-licensing.md)에서 다룹니다.

관리 센터에서 내려받을 때는 파일 하나에 로그인 기록 100,000건까지 들어가고, 이보다 크면 다운로드가 시간 초과로 끊길 수 있습니다[5]. 조사 기간이 길면 기간을 나눠 받거나 Graph 로 받습니다. 공개 수집 도구도 Graph beta 의 `auditLogs/signIns` 를 쓰고, Microsoft-Extractor-Suite 는 `signInEventTypes/any(t: t eq 'nonInteractiveUser')` 같은 필터로 종류를 골라 받습니다[13][14]. 수집 절차는 [Microsoft 365 수집 도구](../../../03-techniques/acquisition/m365-collection.md)를 봅니다.

## 구조

Graph `signIn` 레코드의 주요 필드는 아래와 같습니다[6][7].

| 필드 | 뜻 |
|---|---|
| `id` | 로그인 활동 하나의 고유 ID |
| `createdDateTime` | 로그인이 시작된 시각(UTC), 예 `2014-01-01T00:00:00Z` |
| `userPrincipalName`, `userId`, `userDisplayName` | 로그인한 사용자. UPN 은 늘 소문자로 저장 |
| `appId`, `appDisplayName` | 로그인에 쓴 앱 |
| `resourceDisplayName`, `resourceId` | 로그인 대상 리소스 |
| `ipAddress` | 로그인에 쓴 클라이언트 IP |
| `location` | 도시·주·국가 코드(`city`, `state`, `countryOrRegion`) |
| `deviceDetail` | 장치 ID·운영체제·브라우저 |
| `clientAppUsed` | 클라이언트 종류. 최신 인증은 Browser 등, 레거시 인증은 Exchange ActiveSync·IMAP·MAPI·SMTP·POP 등 |
| `isInteractive` | 대화형 여부 |
| `status` | 오류 코드와 실패 설명 |
| `conditionalAccessStatus` | 조건부 접근 결과 `success`, `failure`, `notApplied` |
| `appliedConditionalAccessPolicies` | 이 로그인에 걸린 조건부 접근 정책 목록 |
| `correlationId` | 클라이언트가 보낸 요청 ID |
| `riskLevelDuringSignIn`, `riskLevelAggregated`, `riskDetail` | 위험 수준. P2 가 아니면 `hidden` |
| `riskEventTypes_v2`, `riskState` | 이 로그인에 연결된 위험 유형과 상태 |

beta 에만 있는 필드 가운데 조사에 자주 쓰는 것은 다음과 같습니다[7]. `authenticationProtocol` 은 `oAuth2`, `ropc`, `deviceCode`, `saml20`, `wsFederation` 같은 인증 프로토콜이고, `incomingTokenType` 은 인증에 내민 토큰 종류(`primaryRefreshToken`, `refreshToken`, `saml20` 등)입니다. `originalTransferMethod` 는 `deviceCodeFlow`·`authenticationTransfer` 로 세션이 시작됐는지를, `signInEventTypes` 는 `interactiveUser`·`nonInteractiveUser`·`servicePrincipal`·`managedIdentity` 중 어느 종류인지를 나타냅니다. `uniqueTokenIdentifier` 는 발급한 토큰을 리소스에서 쓸 때 따라가는 base64 식별자이고, `sessionId`·`userAgent`·`crossTenantAccessType`·`homeTenantId`·`resourceTenantId` 도 beta 에 있습니다. `incomingTokenType` 목록에 없는 토큰으로 인증했을 수도 있어서, 값이 `none` 이라고 토큰을 쓰지 않았다고 볼 수는 없습니다[7].

Log Analytics 로 보낸 기록은 열 이름이 대문자로 시작합니다(`CreatedDateTime`, `IPAddress`, `ResultType`, `ResultDescription`, `UniqueTokenIdentifier`, `SessionId`, `LocationDetails`, `TimeGenerated` 등)[8]. `ResultType` 은 5~6자리 오류 코드이고 `0` 이면 성공입니다[8]. 탐지 규칙은 `ClientApp`, `properties.message` 처럼 Graph·Log Analytics 열 이름과 다른 키를 쓰기도 하므로[12], 받은 데이터에서 실제 키 이름을 먼저 확인하고 검색합니다. JSON 로그를 읽는 요령은 [JSON 로그 읽기](../../../01-foundations/logging/json-logs.md)에 있습니다.

조사에서 자주 보는 오류 코드는 아래와 같습니다[10]. 문서 번호는 `AADSTS` 를 앞에 붙인 형태이고, 로그의 `ResultType`·`errorCode` 에는 숫자만 남습니다.

| 코드 | 이름 | 뜻 |
|---|---|---|
| 50126 | InvalidUserNameOrPassword | 사용자 이름이나 비밀번호가 틀림 |
| 50053 | IdsLocked 등 | 틀린 시도가 많아 잠겼거나, 악성 활동이 있던 IP 에서 와서 막힘(두 원인) |
| 50057 | UserDisabled | 비활성화된 계정 |
| 50055 | InvalidPasswordExpiredPassword | 비밀번호 만료 |
| 50076 | UserStrongAuthClientAuthNRequired | 다단계 인증이 필요함 |
| 50074 | UserStrongAuthClientAuthNRequiredInterrupt | 다단계 인증을 통과하지 못함 |
| 53003 | BlockedByConditionalAccess | 조건부 접근 정책이 토큰 발급을 막음 |
| 50140 | KmsiInterrupt | "로그인 상태 유지" 질문으로 끊긴 정상 흐름 |

`ResultType` 이 500121 이고 `ResultDescription` 에 "Authentication failed during strong authentication request" 가 들어 있는 기록도 다단계 인증이 중단된 기록으로 보고 함께 찾습니다[12].

## 증거로서 의미

**증명하는 것**: 특정 시각(UTC)에 특정 계정으로 특정 앱·리소스에 인증을 시도한 기록이 있고, 그 결과(성공·오류 코드), 요청 IP, 클라이언트 종류, 인증 프로토콜, 적용된 조건부 접근 정책이 무엇이었는지를 보여 줍니다[6][7]. 레거시 프로토콜(IMAP·POP·SMTP 등)이나 장치 코드 흐름으로 로그인했다는 사실도 `clientAppUsed`·`authenticationProtocol`·`originalTransferMethod` 로 드러납니다[6][7].

**증명하지 못하는 것**: 로그인 뒤에 메일을 읽거나 파일을 받았는지는 알 수 없으니, 그건 [통합 감사 로그](../unified-audit-log/index.md)나 Graph 활동 로그에서 확인합니다[9]. 성공한 로그인이 계정 주인 본인이었는지도 알 수 없습니다. 위치는 IP 로 추정한 값이라 VPN·모바일 통신사 주소 풀 때문에 실제 위치와 크게 다를 수 있습니다[3]. 보고서에는 "이 시간대에 이 IP 에서 이 계정으로 로그인에 성공한 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`createdDateTime` 은 로그인이 시작된 시각이고 UTC 입니다[6]. 관리 센터 화면은 시각을 **화면을 보는 관리자의 시간대**로 바꿔 보여 주고, 로그인한 사용자의 시간대와는 관계가 없습니다[3]. 내려받은 파일의 시각은 UTC 입니다[5]. 화면 캡처와 내려받은 파일을 섞어 쓰면 시간대가 어긋나므로 한쪽으로 맞춥니다.

Log Analytics 에서는 `CreatedDateTime` 이 Entra 가 인증을 처리한 시각이고 `TimeGenerated` 는 기록이 작업 영역에 들어와 저장된 시각이라, 타임라인에는 `CreatedDateTime` 을 씁니다[3]. 비대화형 로그인은 묶여서 보이므로 묶음을 펼쳐 각 시각을 봐야 합니다(아래 함정 참고). 클라우드 로그 시각 전반은 [클라우드 로그의 시각](../../../01-foundations/logging/timestamps.md)을 봅니다.

## 함정과 한계

- **비대화형 묶음**: 앱·사용자·IP 주소·상태·Resource ID 가 같고 시각만 다른 비대화형 로그인은 한 행으로 묶이고, "# sign-ins" 열에 개수가 나옵니다[2]. 묶인 로그인은 시각이 같아 보일 수 있고, 묶는 단위는 1·6·24시간 중에서 고릅니다[2]. 행을 펼치면 각 로그인의 시각이 보입니다.
- **비대화형 IP**: 기밀 클라이언트 (confidential client) 의 비대화형 로그인은 실제 리프레시 요청을 보낸 IP 가 아니라 처음 토큰을 발급받을 때의 IP 를 보여 줍니다[2].
- **Correlation ID**: 클라이언트가 넘긴 값으로 만들어서 Entra 가 정확성을 보장하지 않습니다[3]. 특정 토큰과 연결할 때는 Request ID·Unique token identifier 를 씁니다[3].
- **다단계 인증 기록**: 관리 센터에서는 한 줄로 보이지만 Azure Monitor 로 보낸 기록에서는 같은 correlation ID 로 여러 줄이 됩니다[3]. 1차 인증에서 실패하면 조건부 접근 평가 전이라 `authenticationRequirement` 가 `singleFactorAuthentication` 으로 남습니다[3].
- **조건부 접근 상태**: `success` 는 정책이 평가됐다는 뜻이고, Windows Hello for Business 로그인은 조건부 접근 대상이 아니라서 "Not Applied" 로 나옵니다[3].
- **Authentication details 탭**: 기록이 처음 쌓일 때는 "satisfied by claim in the token" 이 잘못 표시될 수 있습니다[3]. 시간이 지난 뒤 다시 확인합니다.
- **위험 필드**: P2 가 아니면 위험 수준 필드가 `hidden` 으로 나오고, 이 값은 위험이 없다는 뜻이 아닙니다[6].
- **통합 감사 로그의 로그인**: 통합 감사 로그에 남는 Entra STS 로그온 레코드의 `ResultStatus` 가 `Succeeded` 이면 HTTP 요청이 성공했다는 뜻일 뿐이고 로그인 성공을 뜻하지 않습니다[11]. 통합 감사 로그에서는 STS 로그온 레코드의 `LogonError` 속성으로 로그인 성공 여부를 판단하고[11], 로그인 로그에서는 `status`·`ResultType` 을 봅니다.
- **보관 기간**: Free 테넌트는 7일이 지나면 기록이 사라지므로, 사고를 알면 먼저 내려받거나 진단 설정을 켭니다[4]. 절차는 [로그부터 지키기](../../../03-techniques/acquisition/log-preservation.md)에 있습니다.

## 직접 분석해 보기

**JSON 레코드 한 건 읽기.** 아래는 필드 일부만 담은 만든 예시입니다.

```json
{
  "id": "00000000-0000-0000-0000-000000000001",
  "createdDateTime": "2026-09-01T02:14:07Z",
  "userPrincipalName": "user1@contoso.com",
  "appDisplayName": "Office 365 Exchange Online",
  "ipAddress": "203.0.113.25",
  "clientAppUsed": "IMAP",
  "isInteractive": true,
  "conditionalAccessStatus": "notApplied",
  "status": { "errorCode": 0 },
  "location": { "city": "Example City", "countryOrRegion": "XX" }
}
```

이 레코드는 2026년 9월 1일 02:14:07 UTC 에 `user1@contoso.com` 계정이 IMAP 으로 로그인에 성공했고(`errorCode` 0), 조건부 접근 정책이 적용되지 않았다는 기록입니다. IMAP 은 레거시 인증이라[6] 다단계 인증 없이 통과했을 가능성이 있으므로, 같은 IP 의 다른 로그인과 그 뒤 메일함 활동을 이어서 봅니다.

**공개 도구로 받기.** Microsoft-Extractor-Suite 의 `Get-AzureEntraGraphLogs.ps1` 은 Graph beta `auditLogs/signIns` 를 `signInEventTypes` 필터로 종류별로 받고[13], Untitled Goose Tool 도 같은 엔드포인트에서 받습니다[14]. 받은 JSON 은 `createdDateTime` 으로 정렬해 `ipAddress`·`userAgent`·`authenticationProtocol` 을 기준으로 묶어 봅니다. Log Analytics 에 쌓여 있다면 `SigninLogs` 와 `AADNonInteractiveUserSignInLogs` 를 함께 조회해야 대화형·비대화형을 모두 봅니다[9]. 탐지 규칙으로 로그를 검사하는 방법은 [탐지 규칙으로 로그 검색하기](../../../03-techniques/analysis/detection-rules.md)를 봅니다.

## 교차 검증

- **Graph 활동 로그 (Microsoft Graph activity logs)**: 로그인 뒤에 어떤 Graph API 를 불렀는지 보여 주고, `SignInActivityId` 를 로그인 로그의 `UniqueTokenIdentifier` 와 맞춰 잇습니다[9]. P1·P2 가 필요하고 진단 설정 목적지에만 저장되며, 대개 30분 안에(드물게 2시간까지) 도착합니다[9].
- **[감사 로그](audit-logs.md)**: 로그인 직후 인증 수단 등록·앱 동의·역할 부여 같은 변경이 이어졌는지 봅니다.
- **[위험 탐지](identity-protection.md)**: 같은 로그인에 붙은 위험 판정과 탐지 시각을 봅니다.
- **[통합 감사 로그](../unified-audit-log/index.md)와 [Exchange Online](../exchange-online/index.md)**: 같은 IP·같은 시간대에 메일함·파일 작업이 있었는지 봅니다.

IP·사용자 에이전트·위치 해석은 [IP·사용자 에이전트·위치 정보](../../../01-foundations/logging/ip-ua-geo.md), 토큰과 세션 개념은 [토큰과 세션](../../../01-foundations/identity/tokens-sessions.md), 조건부 접근은 [다단계 인증과 조건부 접근](../../../01-foundations/identity/mfa-conditional-access.md)에 있습니다. 이상한 로그인을 가려내는 절차는 [이상한 로그인 가려내기](../../../03-techniques/analysis/suspicious-sign-ins.md), 사례별 흐름은 [토큰을 훔쳐 로그인했나](../../../04-scenarios/account-compromise/token-theft.md)와 [MFA 피로 공격을 당했나](../../../04-scenarios/account-compromise/mfa-fatigue.md)를 봅니다.

## 실습

시험용 테넌트에서 로그인 로그를 JSON 으로 내려받아 아래 질문을 풀어 봅니다.

1. 같은 계정의 대화형 로그인과 비대화형 로그인 수를 `signInEventTypes` 또는 `isInteractive` 로 나눠 세어 보고, 비대화형 행을 펼쳤을 때 "# sign-ins" 값과 실제 행 수가 맞는지 확인합니다.
2. 관리 센터 화면에 보이는 시각과 내려받은 파일의 `createdDateTime` 이 몇 시간 차이 나는지, 그 차이가 관리자 계정의 시간대와 같은지 확인합니다.
3. 비밀번호를 일부러 틀리게 넣은 뒤 `status` 의 오류 코드가 50126 으로 남는지, 다단계 인증 요청을 거절하면 어떤 코드가 남는지 봅니다.
4. Log Analytics 를 켰다면 같은 로그인의 `TimeGenerated` 와 `CreatedDateTime` 차이를 재 봅니다.

## 참고 문헌

1. Microsoft, "What are Microsoft Entra sign-in logs?", entra-docs (ms.date 2025-11-07). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-ins.md
2. Microsoft, "Non-interactive user sign-ins", entra-docs (ms.date 2026-02-09). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-noninteractive-sign-ins.md
3. Microsoft, "Sign-in log activity details", entra-docs (ms.date 2026-03-04). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
4. Microsoft, "Microsoft Entra data retention", entra-docs (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
5. Microsoft, "How to download logs in Microsoft Entra ID", entra-docs (ms.date 2024-11-08). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/howto-download-logs.md
6. Microsoft, "signIn resource type" (v1.0), Microsoft Learn (2025-11-28 갱신). https://learn.microsoft.com/en-us/graph/api/resources/signin
7. Microsoft, "signIn resource type" (beta), Microsoft Learn (2025-11-28 갱신). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
8. Microsoft, "SigninLogs" table reference, Azure Monitor (2026-08-27 갱신). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
9. Microsoft, "Microsoft Graph activity logs", Microsoft Learn (2026-07-04 갱신). https://learn.microsoft.com/en-us/graph/microsoft-graph-activity-logs-overview
10. Microsoft, "Microsoft Entra authentication and authorization error codes", Microsoft Learn (2025-02-03 갱신). https://learn.microsoft.com/en-us/entra/identity-platform/reference-error-codes
11. Microsoft, "Office 365 Management Activity API schema", Microsoft Learn (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
12. SigmaHQ, sigma — rules/cloud/azure/signin_logs (azure_legacy_authentication_protocols, azure_app_device_code_authentication, azure_mfa_interrupted). https://github.com/SigmaHQ/sigma
13. Invictus IR, Microsoft-Extractor-Suite — Scripts/Get-AzureEntraGraphLogs.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite
14. CISA, Untitled Goose Tool — goosey/entra_id_datadumper.py. https://github.com/cisagov/untitledgoosetool
