---
title: "이상한 로그인 가려내기"
parent: "기법 · 분석"
nav_order: 690
---

# 이상한 로그인 가려내기 (Suspicious Sign-ins)

로그인 기록을 계정·IP·인증 방식·결과로 묶어 평소와 다른 로그인을 골라내고, 그 로그인 뒤에 계정 설정이 바뀌었는지까지 이어서 보는 방법입니다.

## 언제 쓰나

계정 침해가 의심될 때 가장 먼저 씁니다. 메일 규칙이 몰래 생겼거나 송금 요청 메일이 나갔을 때, 외부에서 특정 IP 를 알려 왔을 때, 서비스가 위험 경고를 띄웠을 때가 여기에 해당합니다. 사건별 흐름은 [메일 계정을 빼앗겨 송금 사기를 당했나](../../04-scenarios/account-compromise/bec.md), [토큰을 훔쳐 로그인했나](../../04-scenarios/account-compromise/token-theft.md), [MFA 피로 공격을 당했나](../../04-scenarios/account-compromise/mfa-fatigue.md), [액세스 키가 새어 나갔나](../../04-scenarios/infrastructure/leaked-keys.md) 시나리오에 있고, 이 쪽은 그 시나리오들이 함께 쓰는 로그인 판별 방법만 다룹니다.

서비스마다 로그인 기록이 있는 곳과 결과를 가르는 필드가 다릅니다. 아래 표는 이 쪽에서 쓰는 필드만 모은 것이고, 각 로그의 전체 구조는 표 첫 열의 아티팩트 쪽에 있습니다.

| 서비스 | 로그인 기록 | 성공·실패 | 다단계 인증(MFA) 흔적 | 서비스가 붙인 판정 |
|---|---|---|---|---|
| Microsoft Entra ID (Microsoft 365·Azure) — [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md) | 로그인 로그. Graph `signIn`, Log Analytics `SigninLogs`·`AADNonInteractiveUserSignInLogs`[3][5][31] | `status.errorCode`·`ResultType` 가 0 이면 성공, 그 밖은 5~6자리 오류 코드[3][5] | `authenticationRequirement`[4], `conditionalAccessStatus`[3] | `riskEventTypes_v2`, `riskLevelDuringSignIn`[3] |
| Microsoft 365 통합 감사 로그 — [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md) | RecordType `AzureActiveDirectoryStsLogon`, 작업 `UserLoggedIn`·`UserLoginFailed`[9][10] | `ErrorCode`(0 = 성공), `LogonError`(실패 이유 문장)[9] | — | Microsoft Cloud App Security 경고 이름(예: `Impossible travel activity`)[28] |
| AWS — [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md) | `eventSource` `signin.amazonaws.com`, `eventName` `ConsoleLogin`, `eventType` `AwsConsoleSignIn`[11] | `responseElements.ConsoleLogin` 이 `Success`·`Failure`, 실패는 `errorMessage` `Failed authentication`[11] | `additionalEventData.MFAUsed`, IAM 사용자는 별도 `CheckMfa` 이벤트[11] | — |
| Google Workspace — [로그인 기록](../../02-artifacts/google-workspace/login-audit.md) | Reports API `login` 애플리케이션[14] | `login_success`·`login_failure`[14] | `login_challenge_method`, `2sv_enroll`·`2sv_disable`[14] | `is_suspicious`, `suspicious_login` 계열 이벤트[14] |
| Okta — [Okta 시스템 로그](../../02-artifacts/saas/okta.md) | System Log `user.session.start`("User login to Okta")[17] | `outcome.result`[18] | `user.authentication.auth_via_mfa`[17] | `security.threat.detected`(ThreatInsight)[17] |
| Slack — [Slack 감사 로그](../../02-artifacts/saas/slack.md) | Audit Logs API `user_login`·`user_login_failed`[21] | 동작 이름 자체 | — | `anomaly`[21] |

Azure 테넌트로 들어오는 로그인은 모두 Entra 로그인 로그에 남으므로, Azure 포털이나 Azure 자원에 쓰는 계정도 같은 표의 첫 줄로 봅니다[1]. Google Workspace 로그인 기록을 Google Cloud 로 공유했다면 Cloud Logging 에서 `protoPayload.serviceName` 이 `login.googleapis.com` 인 항목으로 찾습니다[29]. 공유 설정과 공유되는 로그 종류는 에디션마다 다르고, 공유한 데이터는 관리 콘솔이 아니라 Google Cloud 쪽 보관 정책을 따릅니다(2026년 9월 문서 기준)[16].

## 절차

### 1. 로그인 기록을 빠짐없이 받는다

사용자가 직접 암호나 인증 요소를 입력한 대화형 로그인만 받으면 토큰으로 이어진 접속이 빠집니다. Entra 는 리프레시 토큰으로 액세스 토큰을 받는 경우, 인가 코드로 토큰을 받는 경우, 같은 앱 계열(FOCI, Family of Client IDs)로 두 번째 Office 앱에 로그인하는 경우를 비대화형 로그인(non-interactive sign-in)으로 따로 남깁니다[2]. Graph 의 `signInEventTypes` 값은 `interactiveUser`, `nonInteractiveUser`, `servicePrincipal`, `managedIdentity` 네 가지입니다[4]. 필터를 따로 주지 않으면 Graph 는 대화형 로그인만 돌려주므로[4], 종류마다 필터를 주어 받습니다. 서비스 주체와 관리 ID 의 로그인까지 받아야 앱 자격 증명이 쓰인 흔적도 보입니다.

Microsoft-Extractor-Suite 의 `Get-GraphEntraSignInLogs` 는 `-EventTypes` 기본값이 `All` 이고 종류마다 `signInEventTypes/any(...)` 필터로 나눠 받습니다[23]. Untitled Goose Tool 은 `adfs`·`rt`·`sp`·`msi` 네 갈래로 나눠 `signin_` 으로 시작하는 폴더에 저장합니다[24]. Graph 로 로그인 로그를 받으려면 Entra ID P1 또는 P2 라이선스가 필요합니다[3]. 수집 경로와 한도는 [Microsoft 365 수집 도구](../acquisition/m365-collection.md), 보관 기간은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에 있습니다. Okta System Log 는 90일 넘은 데이터를 돌려주지 않고[18][19], Slack 감사 로그는 2018년 3월 이전 데이터가 없습니다(2026년 9월 문서 기준)[21].

### 2. 계정마다 평소 모습을 잡는다

계정마다 평소에 쓰는 IP 대역·ASN·국가·사용자 에이전트·기기·앱을 먼저 정리합니다. Entra ID Protection 도 같은 방식으로 과거 로그인을 학습하는데, 익숙하지 않은 로그인 속성(`unfamiliarFeatures`)은 IP·ASN·위치·기기·브라우저·테넌트 IP 서브넷을 비교하고 새 사용자의 학습 기간이 최소 5일이며, 비정상 이동(`unlikelyTravel`)은 14일 또는 로그인 10회 가운데 먼저 닿는 쪽까지 학습합니다[7]. 수집한 기간이 이보다 짧으면 사람이 비교해도 기준선이 약합니다. IP 를 위치로 바꾼 값을 어디까지 믿을지는 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md)에서 다룹니다.

### 3. 실패를 이유별로 나눈다

실패 건수만 세지 않고 오류 코드로 나눠야 암호 추측, 차단, 정상 흐름이 갈립니다. Entra 에서 자주 보는 코드는 아래와 같습니다(2025년 2월 문서 기준)[6].

| 코드 | 뜻 | 읽는 법 |
|---|---|---|
| 50126 | 사용자 이름 또는 암호가 틀림 | 사용자 실수로도 어느 정도는 생깁니다. 한 IP 에서 여러 계정으로 나오면 4단계로 넘어갑니다 |
| 50053 | 잘못된 ID·암호를 되풀이해 잠김, 또는 악성 활동이 있던 IP 에서 온 로그인이라 차단 | 두 원인 중 어느 쪽인지는 로그인 로그의 실패 이유(Failure reason)로 가립니다 |
| 50074 | 강한 인증이 필요했는데 MFA 챌린지를 통과하지 못함 | 같은 시각 전후 기록에서 1차 인증 결과를 함께 봅니다 |
| 50076 | 관리자 설정(조건부 접근, 사용자별 MFA, 위치 변경)으로 MFA 가 필요함 | 곧이어 같은 세션의 성공이 있는지 봅니다 |
| 50140 | "로그인 상태 유지" 질문으로 끊김 | 정상 로그인 흐름의 일부입니다 |
| 53003 | 조건부 접근 정책이 막음 | 어느 정책이 막았는지는 적용된 정책 목록에서 봅니다 |
| 70016 | 장치 코드 흐름(device code flow)에서 승인을 기다리는 중 | 장치 코드 흐름이 쓰였다는 표시입니다 |

통합 감사 로그의 `ErrorCode` 에도 같은 코드가 들어갑니다[9]. AWS 는 `errorMessage` 가 `Failed authentication` 인 `ConsoleLogin`[11], Okta 는 `outcome.result` 가 `FAILURE` 인 `user.session.start` 로 찾습니다[18]. Google Workspace 의 `login_failure` 에 있던 `login_failure_type` 은 더 이상 쓰지 않는 값(Deprecated)이라 비어 있어도 이상하지 않습니다[14].

### 4. 한 IP 가 건드린 계정을 모은다

암호 뿌리기(password spray)처럼 한 곳에서 여러 계정을 시도한 흔적은 계정이 아니라 IP 로 묶어야 보입니다. 의심 IP 하나가 나오면 그 IP 로 시도한 계정 수와 성공한 계정 수를 따로 세고, 같은 IP·사용자 에이전트로 인증한 다른 계정도 찾습니다[8]. 아래는 Log Analytics 에서 쓰는 만든 예시 쿼리이고, IP 는 문서용 대역입니다.

```kusto
SigninLogs
| where TimeGenerated between (datetime(2026-09-01) .. datetime(2026-09-08))
| where IPAddress == "203.0.113.45"
| summarize attempts = count(),
            successes = countif(ResultType == "0"),
            users_tried = dcount(UserPrincipalName),
            users_ok = dcountif(UserPrincipalName, ResultType == "0")
  by IPAddress
```

`ResultType` 은 문자열 열이라 따옴표로 비교합니다[5]. 비대화형 로그인은 `AADNonInteractiveUserSignInLogs` 에 따로 있으므로 같은 쿼리를 한 번 더 돌립니다[31]. 이 표의 `ResultType` 설명은 "Success 또는 Failure" 로 `SigninLogs` 의 설명(0 이면 성공)과 다르므로[5][31], 검체에서 실제 값을 먼저 확인합니다. 반대로 계정 하나를 두고 IP·ASN·국가·기기 조합이 바뀐 시점을 찾으면 접속 환경이 바뀐 때가 드러납니다.

### 5. 성공한 로그인이 어떻게 통과했는지 본다

실패 뒤에 성공이 이어지면, 그 성공이 어떤 방식으로 인증을 통과했는지 봅니다. 로그인 한 건은 누가(사용자), 어떻게(인증 요구·클라이언트 앱·자격 증명 유형), 무엇에(자원) 세 갈래로 나눠 읽으면 볼 범위가 좁아집니다[1]. Entra 로그인 레코드에서 볼 필드는 아래와 같습니다.

| 필드 | 값 | 가려낼 점 |
|---|---|---|
| `authenticationRequirement` | `singleFactorAuthentication`·`multiFactorAuthentication` | 단일 요소로 성공한 로그인. 1차 인증이 실패하면 조건부 접근을 거치지 않아 늘 `singleFactorAuthentication` 입니다[1] |
| `conditionalAccessStatus` | `success`·`failure`·`notApplied`[3] | 적용된 정책이 없던 로그인 |
| `clientAppUsed` | `Browser`, 최신 인증 클라이언트, 또는 Exchange ActiveSync·IMAP·MAPI·SMTP·POP 같은 레거시 인증[3][5] | 평소 쓰지 않던 레거시 프로토콜 |
| `authenticationProtocol` | `oAuth2`, `ropc`, `deviceCode`, `saml20` 등(beta)[4] | 암호를 앱에 직접 넘기는 ROPC, 장치 코드 흐름 |
| `originalTransferMethod` | `none`·`deviceCodeFlow`·`authenticationTransfer`(beta)[4] | 세션을 처음 연 방식 |
| `incomingTokenType` | `primaryRefreshToken`, `refreshToken`, `saml20` 등(beta)[4] | 토큰을 내밀어 인증한 로그인 |
| `tokenIssuerType` | `AzureAD`, `ADFederationServices` 등(beta)[4] | 페더레이션 IdP 를 거친 로그인([페더레이션과 SSO](../../01-foundations/identity/federation-sso.md)) |
| `crossTenantAccessType`, `homeTenantId`, `resourceTenantId` | `none`, `b2bCollaboration`, `serviceProvider` 등(beta)[4] | 다른 테넌트 계정의 접근 |
| `clientCredentialType` | `clientSecret`, `certificate`, `federatedIdentityCredential` 등(beta)[4] | 서비스 주체가 평소와 다른 자격 증명 유형을 씀 |
| `deviceDetail` | `deviceId`, OS, 브라우저[3]. 포털의 기기 정보 탭에는 준수·관리·하이브리드 조인 여부도 나옵니다[1] | 평소 쓰지 않던 기기·OS·브라우저 |

다른 서비스에서는 이렇게 봅니다. AWS `ConsoleLogin` 은 `additionalEventData.MFAUsed` 가 `Yes`·`No` 이고 루트 계정이면 `userIdentity.type` 이 `Root` 입니다[11]. Google Workspace `login_success` 에는 `login_type`(`google_password`, `saml`, `reauth`, `exchange`, `unknown`)과 `login_challenge_method` 가 있고, 한 로그인 세션에서 만난 챌린지는 이벤트 하나로 묶여 `login_challenge_method` 에 차례대로 들어갑니다[14]. Okta 의 `policy.evaluate_sign_on` 은 결과가 `ALLOW`·`CHALLENGE`·`DENY` 가운데 하나이고[17], `user.authentication.auth_via_mfa` 는 Classic 에서는 2차 요소 검증에만, Identity Engine 에서는 1차·2차 요소 모두에 남습니다[17]. MFA 와 조건부 접근의 원리는 [다단계 인증과 조건부 접근](../../01-foundations/identity/mfa-conditional-access.md), 토큰 재사용은 [토큰과 세션](../../01-foundations/identity/tokens-sessions.md)에서 다룹니다.

### 6. 서비스가 붙인 판정과 맞춰 본다

서비스가 스스로 위험하다고 표시한 기록을 5단계에서 고른 로그인과 맞춰 봅니다. 판정은 라이선스에 따라 보이는 범위가 달라서, 빈 칸이 "위험 없음" 인지 "볼 권한 없음" 인지를 먼저 가립니다.

| Entra ID 라이선스 | 받는 로그인 위험 탐지(`riskEventType`) | 로그인 로그의 위험 필드 |
|---|---|---|
| Free·P1 | `anonymizedIPAddress`, `investigationsThreatIntelligence`, `adminConfirmedUserCompromised`, 그리고 P2 탐지가 걸렸지만 내용을 숨긴 `generic`[7] | `riskLevelDuringSignIn`·`riskLevelAggregated`·`riskDetail` 이 `hidden`[3] |
| P2 | 위 탐지에 더해 `unlikelyTravel`, `mcasImpossibleTravel`, `unfamiliarFeatures`, `anomalousToken`, `tokenIssuerAnomaly`, `passwordSpray`, `authenticatorPhishing`, `newCountry`, `maliciousIPAddress`, `suspiciousBrowser`, `nationStateIP` 등[7] | 값이 채워짐[3] |

표는 2026년 4월 문서 기준입니다. 위 탐지 가운데 `unlikelyTravel`·`mcasImpossibleTravel`·`newCountry` 처럼 오프라인으로 계산하는 것은 로그인보다 늦게 나오고, `unfamiliarFeatures` 처럼 실시간으로 계산하는 것은 로그인 때 붙습니다[7]. 비대화형 로그인에 붙은 익숙하지 않은 로그인 속성 탐지는 토큰 재사용 가능성이 있어 먼저 봅니다[7][8].

다른 서비스의 판정은 이렇게 찾습니다. Google Workspace 는 `login_success` 의 `is_suspicious`(예: 낯선 IP 에서 로그인)와 `suspicious_login`·`suspicious_login_less_secure_app`·`suspicious_programmatic_login`·`gov_attack_warning`·`account_disabled_hijacked` 이벤트를 남깁니다[14]. Okta 는 ThreatInsight 가 악성으로 본 IP 의 요청을 `security.threat.detected` 로 남기고, 이때 `outcome.result` 의 `ALLOW`·`DENY`·`RATE_LIMIT` 은 ThreatInsight 를 기록만 하는 모드로 두었는지 막는 모드로 두었는지에 따라 갈립니다[17]. Slack 은 비정상 행동을 `anomaly` 로, 그에 따른 세션 초기화를 `user_sessions_reset_by_anomaly_event_response` 로 남깁니다[21].

### 7. 로그인 뒤에 바뀐 것을 잇는다

의심 로그인 하나를 찾으면 그 뒤에 같은 계정으로 무엇이 바뀌었는지 봅니다. Entra 에서는 감사 로그의 MFA 방법 추가, 기기 등록, 자격 증명 변경과 메일함의 받은편지함 규칙·전달 규칙을 확인합니다[8]. Google Workspace 로그인 기록에도 `2sv_disable`, `password_edit`, `recovery_email_edit`, `recovery_phone_edit`, `email_forwarding_out_of_domain` 같은 계정 변경 이벤트가 함께 있습니다[14]. 설정 변경을 읽는 방법은 [권한 변화 따라가기](permission-changes.md), 로그인과 변경을 한 줄로 세우는 방법은 [클라우드 타임라인](timeline.md)에 있습니다.

## 도구

| 도구 | 이 쪽에서 쓰는 기능 |
|---|---|
| Microsoft-Extractor-Suite | `Get-GraphEntraSignInLogs -EventTypes` 로 대화형·비대화형·서비스 주체·관리 ID 로그인을 종류별로 받습니다[23] |
| Untitled Goose Tool | 로그인 로그를 `adfs`·`rt`·`sp`·`msi` 로 나눠 받습니다[24] |
| Hawk | `Search-HawkTenantActivityByIP` 가 `Search-UnifiedAuditLog -IPAddresses` 로 한 IP 의 통합 감사 로그 기록을 모아 `Success_Events`, `Unique_Users_Attempted`, `Unique_Users_Success` 파일로 나눠 냅니다[22] |
| SigmaHQ 규칙 | AWS 콘솔 로그인 실패(`eventName: ConsoleLogin` + `errorMessage: Failed authentication`)[26], MFA 없는 콘솔 로그인 성공(`additionalEventData.MFAUsed: 'NO'` + `responseElements.ConsoleLogin: 'Success'`)[25], Google Workspace 의심 로그인[29] 등. 규칙을 로그에 돌리는 법은 [탐지 규칙으로 로그 훑기](detection-rules.md)에 있습니다 |
| Okta System Log 필터 | `eventType eq "user.session.start" and outcome.result eq "FAILURE"`[18] |

Hawk 는 `ResultStatus` 가 `success` 인 레코드를 성공으로 셉니다[22]. 통합 감사 로그의 Entra STS 로그인 레코드에서 `ResultStatus` 가 `Succeeded` 인 것은 HTTP 작업이 성공했다는 뜻일 뿐 로그인 성공이 아니라서, 로그인 성공 여부는 `LogonError`·`ErrorCode` 로 다시 확인합니다[9].

## 함정과 한계

- `conditionalAccessStatus` 가 `success` 여도 막는 정책이 적용됐다는 뜻은 아닙니다. 정책이 평가만 되고 적용되지 않았어도 `success` 로 나옵니다[1].
- `authenticationRequirement` 는 앞선 MFA 클레임으로 요구가 이미 채워진 경우처럼 실제로 도달한 인증을 반영하지 못하는 예외가 있습니다[1]. "MFA 없이 로그인했다" 고 쓰기 전에 같은 세션의 앞선 로그인을 봅니다.
- Windows Hello for Business 로그인은 조건부 접근이 클라우드 자원 로그인만 보호하기 때문에 `Not Applied` 로 나옵니다[1]. 기기 등록처럼 조건부 접근 평가에서 빠져야 하는 초기 설정(bootstrap) 로그인도 `Not Applied` 일 수 있습니다[1].
- 지속적 액세스 평가(CAE, Continuous Access Evaluation)는 한 인증의 여러 요청 가운데 하나에만 true 로 나오고, 대화형·비대화형 어느 쪽에도 나올 수 있습니다[1].
- 관리 센터의 비대화형 로그인 로그는 앱·사용자·IP·상태·자원 ID 가 같고 시각만 다르면 한 줄로 묶고, 묶인 수는 로그인 수 열에 나옵니다[2]. 기밀 클라이언트(confidential client)의 비대화형 로그인 IP 는 리프레시 토큰을 요청한 실제 출발지가 아니라 처음 토큰을 받을 때의 IP 입니다[2].
- 게스트 사용자는 사용자 객체에 `AdeleVance_fabrikam.com#EXT#@contoso.com` 처럼 저장되지만 로그인 로그에는 `adelevance@fabrikam.com` 처럼 원래 형식의 소문자로 남습니다[3]. 사용자 목록과 이어 붙일 때 문자열이 맞지 않습니다. 교차 테넌트 로그인에서는 홈 테넌트 이름을 채우지 않습니다[1].
- `incomingTokenType` 목록에 없는 토큰으로도 인증했을 수 있어서, 값이 `none` 이라고 토큰이 없었다고 볼 수 없습니다[4].
- 위험 탐지 이름이 출처마다 다릅니다. Entra 문서의 불가능 이동은 `mcasImpossibleTravel` 인데[7], SigmaHQ 규칙은 `impossibleTravel` 로 찾습니다[27]. 규칙을 그대로 쓰기 전에 검체의 실제 값을 확인합니다. 통합 감사 로그 쪽 Sigma 규칙은 원시 로그인이 아니라 `eventSource: SecurityComplianceCenter` 의 경고 이름을 찾으므로, 서비스가 이미 판정한 결과를 다시 거르는 셈입니다[28].
- AWS `MFAUsed` 는 IAM 사용자나 루트 사용자가 MFA 를 쓴 경우에만 참이 되고, 페더레이션 사용자의 요청은 `No` 로 남습니다[11]. IdP 쪽에서 MFA 를 했는지는 IdP 로그로 확인합니다. 값은 `Yes`·`No` 인데 Sigma 규칙은 `'NO'` 로 적습니다[11][25]. Sigma 는 대소문자를 가리지 않지만[30], jq·grep 으로 직접 찾을 때는 대소문자를 맞춥니다.
- AWS 콘솔 로그인이 기록되는 리전은 사용자 유형과 엔드포인트에 따라 다릅니다. 루트는 `us-east-1`·`us-east-2`·`us-west-2` 가운데 하나이고, IAM 사용자가 전역 엔드포인트로 로그인하면 브라우저에 계정 별칭 쿠키가 있을 때 `us-east-2`·`eu-north-1`·`ap-southeast-2` 가운데 하나, 없을 때 `us-east-1` 입니다[11]. 한 리전만 조회하면 로그인이 빠집니다.
- CloudTrail 은 교차 계정 역할 전환과 `AssumeRoot` 로 여는 권한 세션에서 거부된 STS 요청을 대상 계정에 남기지 않고, 유효성이 모자란 일부 비인증 STS 요청도 남기지 않습니다[12].
- Google Workspace `login_type` 이 `exchange` 이면 기존 자격 증명을 다른 유형으로 바꾼 것이고, 이미 로그인한 세션과 합쳐졌을 수 있습니다[14].
- Okta Classic 과 Identity Engine 은 같은 행위를 다른 이벤트로 남깁니다. Okta Verify 푸시 거절은 Classic V1 API 에서 `user.mfa.okta_verify.deny_push` 이고, Identity Engine 에서는 `user.authentication.auth_via_mfa` 에 이유 `INVALID_CREDENTIALS` 입니다[17]. `user.authentication.sso` 는 앱 SSO 가 실패해도 생기므로 이 이벤트만으로 성공을 말할 수 없습니다[17].
- Slack `team.accessLogs` 는 사용자·IP·사용자 에이전트 조합마다 `date_first`·`date_last`·`count` 로 묶은 요약이고, 실제 로그인 말고도 접속할 때 흔히 부르는 API 호출이 섞여 있습니다[20]. 로그인 한 번 한 번은 Audit Logs API 의 `user_login` 으로 봅니다[20].

## 결과를 어떻게 해석하나

### 증명하는 것

- 그 시각에 그 계정 이름으로 그 IP·사용자 에이전트에서 인증을 시도했고, 결과가 성공 또는 실패였다는 것[3][11][14].
- 실패라면 서비스가 정한 실패 이유(오류 코드·실패 사유 문장)[6][9].
- 성공이라면 서비스가 기록한 인증 방식(단일·다단계, 프로토콜, 토큰 유형)과 그 시점에 서비스가 붙인 위험 판정[3][4][7].

### 증명하지 못하는 것

- 그 사람이 직접 로그인했다는 것. 훔친 토큰을 다시 쓴 로그인도, 기존 세션과 합쳐진 로그인(`login_type` `exchange`)도 같은 계정 이름으로 남습니다[14].
- IP 가 가리키는 물리적 위치. 위치 값은 IP 로 짐작한 것입니다([IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md)).
- 위험 탐지가 없으니 안전했다는 것. Free·P1 테넌트에서는 위험 필드가 `hidden`, 탐지 이름이 `generic` 으로 가려지고[3][7], 오프라인 탐지는 늦게 붙습니다[7].
- 로그인 기록이 없으니 접속이 없었다는 것. 보관 기간이 지났거나, 받지 않은 로그인 종류(비대화형·서비스 주체)에 있거나, "함정과 한계" 에 적은 대로 처음부터 남지 않는 요청일 수 있습니다[2][12].

### 시각

Entra 로그인 레코드의 `createdDateTime`(`SigninLogs` 의 `CreatedDateTime`)은 로그인이 시작된 UTC 시각입니다[3][5]. Log Analytics 의 `TimeGenerated` 는 레코드가 작업 영역에 들어온 시각이라 `CreatedDateTime` 보다 늦습니다[1]. CloudTrail `eventTime` 은 요청이 끝난 UTC 시각입니다[13]. Google Workspace `suspicious_login` 에는 이벤트 시각과 별도로 로그인 시각 `login_timestamp`(마이크로초)가 있어, 둘을 섞지 않습니다[14]. Slack `date_first`·`date_last` 는 Unix 시각입니다[20]. Google Workspace 로그인 이벤트는 몇 분, 사용자 계정 이벤트는 수십 분 늦게 조회됩니다(2026년 9월 문서 기준)[15]. Entra 로그인 로그 항목은 시스템이 만들고 바꾸거나 지울 수 없습니다[2]. 서비스별 시각 필드와 지연 시간은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 모아 두었습니다.

### 보고서 문장

기록이 말하는 만큼만 씁니다. "공격자가 로그인했다" 가 아니라 "2026-09-03 02:14(UTC)에 `user@contoso.com` 계정으로 IP 203.0.113.45 에서 단일 요소 인증으로 로그인에 성공한 기록이 있다. 같은 IP 에서 앞선 40분 동안 다른 계정 12개로 50126 오류가 났다." 처럼 씁니다(값은 모두 만든 예시). 보고서 전체 틀은 [클라우드 포렌식 보고서](../reporting/forensic-report.md)에 있습니다.

## 참고 문헌

1. Microsoft, Learn about the sign-in log activity details, entra-docs (ms.date 2026-03-04). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
2. Microsoft, Non-interactive sign-in logs, entra-docs (ms.date 2026-02-09). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-noninteractive-sign-ins.md
3. Microsoft, signIn resource type, Microsoft Graph v1.0 (2025-11-28 갱신). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-1.0
4. Microsoft, signIn resource type, Microsoft Graph beta (2025-11-28 갱신). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
5. Microsoft, SigninLogs table, Azure Monitor 참조 (2026-08-27 갱신). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
6. Microsoft, Microsoft Entra authentication and authorization error codes (2025-02-03 갱신). https://learn.microsoft.com/en-us/entra/identity-platform/reference-error-codes
7. Microsoft, What are risk detections?, Microsoft Entra ID Protection (2026-04-22 갱신). https://learn.microsoft.com/en-us/entra/id-protection/concept-identity-protection-risks
8. Microsoft, Token theft playbook (2024-03-07 갱신). https://learn.microsoft.com/en-us/security/operations/token-theft-playbook
9. Microsoft, Office 365 Management Activity API schema (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
10. Microsoft, Audit log activities, Microsoft Purview (2026-09-08 갱신). https://learn.microsoft.com/en-us/purview/audit-log-activities
11. AWS, AWS Management Console sign-in events, CloudTrail 사용자 안내서 (2026년 9월 사본). https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-aws-console-sign-in-events.html
12. AWS, Logging IAM and AWS STS API calls with AWS CloudTrail, IAM 사용자 안내서 (2026년 9월 사본). https://docs.aws.amazon.com/IAM/latest/UserGuide/cloudtrail-integration.html
13. AWS, CloudTrail record contents for management, data, and network activity events (2026년 9월 사본). https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
14. Google, Login Audit Activity Events, Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/login
15. Google, Data retention and lag times, Google Workspace 관리자 도움말 (2026-09-25 갱신). https://support.google.com/a/answer/7061566?hl=en
16. Google, Share data with Google Cloud services, Google Workspace 관리자 도움말 (2026-09-18 갱신). https://support.google.com/a/answer/9320190?hl=en
17. Okta, Event types (okta-event-types.csv, 2026년 9월 사본). https://developer.okta.com/docs/okta-event-types.csv
18. Okta, System Log query, 개발자 문서 (2026년 9월 사본). https://developer.okta.com/docs/reference/system-log-query/
19. Okta, System Log filters and search, 도움말 (2026년 9월 사본). https://help.okta.com/en-us/content/topics/reports/syslog-filters.htm
20. Slack, team.accessLogs method (2026년 9월 사본). https://api.slack.com/methods/team.accessLogs
21. Slack, Using the Audit Logs API (2026년 9월 사본). https://api.slack.com/admins/audit-logs-call
22. T0pCyber, Hawk, `Hawk/functions/Tenant/Search-HawkTenantActivityByIP.ps1`. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Search-HawkTenantActivityByIP.ps1
23. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-AzureEntraGraphLogs.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureEntraGraphLogs.ps1
24. CISA, Untitled Goose Tool, `goosey/entra_id_datadumper.py`. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/entra_id_datadumper.py
25. SigmaHQ, `rules/cloud/aws/cloudtrail/aws_cloudtrail_console_login_success_without_mfa.yml`. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_console_login_success_without_mfa.yml
26. SigmaHQ, `rules/cloud/aws/cloudtrail/aws_cloudtrail_console_login_failed_authentication.yml`. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_console_login_failed_authentication.yml
27. SigmaHQ, `rules/cloud/azure/identity_protection/azure_identity_protection_impossible_travel.yml`. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/identity_protection/azure_identity_protection_impossible_travel.yml
28. SigmaHQ, `rules/cloud/m365/threat_management/microsoft365_impossible_travel_activity.yml`. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/threat_management/microsoft365_impossible_travel_activity.yml
29. SigmaHQ, `rules/cloud/gcp/gworkspace/login/gcp_gworkspace_suspicious_login.yml`. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/gworkspace/login/gcp_gworkspace_suspicious_login.yml
30. SigmaHQ, Sigma Rules Specification v2.1.0 (2025-08-02). https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-rules-specification.md
31. Microsoft, AADNonInteractiveUserSignInLogs table, Azure Monitor 참조 (2026-08-27 갱신). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadnoninteractiveusersigninlogs
