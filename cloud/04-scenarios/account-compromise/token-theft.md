---
title: "토큰을 훔쳐 로그인했나"
parent: "시나리오 · 계정 침해"
nav_order: 750
---

# 토큰을 훔쳐 로그인했나 (Token Theft)

비밀번호와 MFA 를 거치지 않고, 이미 발급된 새로 고침 토큰 (refresh token)·세션 쿠키·주 새로 고침 토큰 (Primary Refresh Token, PRT) 이 원래 장치 밖에서 쓰였는지를 로그로 가려내는 순서를 다룹니다. 중심은 Microsoft Entra ID 이고, Google Workspace·Okta·AWS 에서 같은 질문을 볼 곳을 함께 적습니다.

## 조사 질문

- 한 로그인 세션이나 토큰이 사용자의 평소 장치·IP 가 아닌 곳에서도 쓰였나?
- 그렇다면 처음 다른 곳에서 쓰인 시각과 마지막으로 쓰인 시각은 언제인가?
- 그 세션·토큰으로 메일·파일·Graph API 에서 무엇에 접근했나?
- 그 세션으로 MFA 수단이나 장치를 새로 등록해 발판을 남겼나?
- 토큰을 폐기한 뒤에도 활동이 이어졌다면, 남은 토큰 수명 안의 일인가?

토큰이 어떻게 새어 나갔는지(피싱 역방향 프록시, 장치의 악성 코드, 장치 분실)는 클라우드 로그만으로 답하지 못하는 경우가 많습니다. 클라우드 로그로 알 수 있는 건 "같은 세션·토큰이 어디서 언제 쓰였나" 까지이고, 새어 나간 경로는 장치 쪽 증거와 함께 봐야 합니다[6].

## 먼저 확인할 것

**어떤 로그인 기록을 받았는지부터 봅니다.** 토큰 재사용은 사용자가 화면에서 로그인하지 않는 비대화형 로그인 (non-interactive sign-in) 으로 남을 가능성이 높습니다. 비대화형 로그인은 클라이언트가 새로 고침 토큰이나 인증 코드로 사용자 대신 토큰을 받는 경우이고, Entra 조인 PC 의 SSO 도 여기에 들어갑니다[2]. 그런데 Graph beta 의 로그인 API 는 필터를 주지 않으면 대화형 로그인만 돌려주고, 비대화형은 `signInEventTypes/any(t: t eq 'nonInteractiveUser')` 로 따로 받아야 합니다[1]. Graph v1.0 의 signIn 리소스에는 `sessionId`·`uniqueTokenIdentifier`·`incomingTokenType`·`userAgent` 가 아예 없습니다[3]. 그래서 이미 받아 둔 자료가 어느 API 로, 어떤 필터로 받은 것인지 먼저 확인합니다. 공개 도구도 호출 방식이 서로 다릅니다.

| 도구 | 로그인 기록을 받는 방식 | 이 시나리오에서 볼 점 |
|---|---|---|
| Microsoft-Extractor-Suite `Get-GraphEntraSignInLogs` | beta API 에 `signInEventTypes` 필터를 붙이고, `-EventTypes` 기본값 `All` 이면 대화형·비대화형을 한 필터로 함께 받고, 사용자를 지정하지 않았을 때는 서비스 주체·관리 ID 도 따로 받음[29] | 비대화형이 함께 들어옴 |
| Hawk `Get-HawkUserEntraIDSignInLog` | v1.0 cmdlet `Get-MgAuditLogSignIn` 을 사용자·기간 필터로 부름[30] | `sessionId`·`uniqueTokenIdentifier`·`incomingTokenType` 이 없음[3] |
| DFIR-O365RC | beta cmdlet `Get-MgBetaAuditLogSignIn -All` 을 기간 필터로 부르고, `tenantSize` 가 `normal` 이 아니면 성공(`status/errorCode eq 0`)과 정해진 앱 ID 로 더 거름[31] | `signInEventTypes` 필터가 없어, 문서대로라면 대화형만 돌아옴[1] |
| Log Analytics 로 보낸 기록 | 대화형은 `SigninLogs`, 비대화형은 `AADNonInteractiveUserSignInLogs` 표에 따로 쌓임[7][34] | 두 표를 함께 조회해야 함 |

**기록이 남는 기간을 확인합니다.** 토큰 탈취는 알아챈 날보다 먼저 시작된 경우가 많으므로, 보관 기간이 짧은 기록부터 확보합니다([로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)). 아래 표는 2026년 9월 문서 기준이고, 서비스별 전체 표는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 에 있습니다.

| 기록 | 조건 | 보관 |
|---|---|---|
| Entra 로그인 로그·감사 로그 | Free / P1·P2 | 7일 / 30일. Free 에서 P1 으로 올려도 이미 지난 기록은 돌아오지 않음[4] |
| Entra 위험한 로그인 (Risky sign-ins) | Free / P1 / P2 | 7일 / 30일 / 90일[4] |
| Microsoft Graph 활동 로그 | P1·P2 에서 진단 설정으로 저장소·분석 도구에 보낸 경우만 | 보낸 곳의 설정을 따름. 켜기 전의 요청은 없음[4][7] |
| Google Workspace 로그 이벤트 | 대부분의 로그와 API 로 받는 감사 데이터 | 6개월[22] |
| Okta 시스템 로그 | 모든 조직 | 90일이 넘은 기록은 API 가 돌려주지 않음[24] |

**라이선스에 따라 보이는 탐지가 다릅니다.** ID 보호 (ID Protection) 의 토큰 관련 탐지는 대부분 프리미엄 탐지이고, Free·P1 테넌트에서는 세부 없이 `generic`("Additional risk detected") 으로만 보입니다[5]. 위험 탐지 이름과 라이선스는 아래 분석 흐름 3단계의 표에 있습니다.

**대응 조치의 시각을 받아 둡니다.** 세션 폐기, 비밀번호 재설정, 장치 격리 같은 조치도 같은 로그에 남습니다. 대응자가 언제 무엇을 했는지 먼저 받아 두어야 뒤의 활동이 공격자의 것인지, 남은 토큰의 것인지 가를 수 있습니다. 로그인 로그의 `createdDateTime` 은 항상 UTC 이고 `2014-01-01T00:00:00Z` 모양입니다[1]. 서비스마다 기록이 늦게 들어오는 정도는 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | ID 보호 위험 탐지(`anomalousToken`, `attackerinTheMiddle`, `attemptedPrtAccess` 등), Defender 경고 | 서비스가 토큰 재생이나 프록시 피싱을 의심한 시각과 사용자 | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [Defender 경고와 기록](../../02-artifacts/m365/defender-xdr.md) |
| 2 | Entra 로그인 로그(대화형·비대화형) | 세션 ID·토큰 식별자·들어온 토큰 유형·IP·사용자 에이전트·장치 | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [이상한 로그인 가려내기](../../03-techniques/analysis/suspicious-sign-ins.md) |
| 3 | Graph 활동 로그 | 토큰으로 부른 Graph API 요청과 요청 IP | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md) |
| 4 | 통합 감사 로그 (UAL) 의 `AppAccessContext`, `MailItemsAccessed` 의 `SessionId` | 메일·파일 활동을 로그인 세션과 잇는 값 | [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md), [Exchange Online](../../02-artifacts/m365/exchange-online/index.md) |
| 5 | Entra 감사 로그의 보안 정보·장치 등록 | 세션을 쥔 쪽이 MFA 수단이나 장치를 더했는지 | [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md) |
| 6 | 폐기 기록(`Update StsRefreshTokenValidFrom Timestamp`) | 폐기 시각. 그 뒤 활동을 해석하는 기준 | [토큰과 세션](../../01-foundations/identity/tokens-sessions.md) |
| 7 | Google Workspace 로그인·관리 로그, Okta 시스템 로그, AWS GuardDuty·CloudTrail | 다른 서비스의 세션 쿠키 이상·세션 로밍·임시 자격 증명 외부 사용 | [로그인 기록](../../02-artifacts/google-workspace/login-audit.md), [Okta 시스템 로그](../../02-artifacts/saas/okta.md), [GuardDuty](../../02-artifacts/aws/guardduty.md) |

## 분석 흐름

1. **사용자별로 로그인 기록을 한 줄에 모읍니다.** 대화형과 비대화형을 합쳐 시간순으로 놓고, 장치·위치·IP·앱 조합이 처음과 마지막으로 나타난 시각을 뽑습니다. 토큰 탈취 대응 플레이북의 쿼리는 `SigninLogs` 를 `UserId` 로 거른 뒤 `DeviceDetail.deviceId`·`DeviceDetail.displayName`·`LocationDetails.city`·`LocationDetails.countryOrRegion`·`IPAddress`·`ResultDescription`·`AppDisplayName` 별로 `TimeGenerated` 의 최솟값과 최댓값을 구합니다[6]. 같은 쿼리를 `AADNonInteractiveUserSignInLogs` 에도 돌립니다. 장치 ID 가 비어 있고 처음 보는 IP·자율 시스템 번호 (ASN) 에서 성공한 줄이 후보입니다. IP·사용자 에이전트를 읽는 법은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md) 에 있습니다.

2. **세션과 토큰 식별자로 잇습니다.** `sessionId` 는 로그인 때 만들어진 세션의 식별자이고, `uniqueTokenIdentifier` 는 Entra ID 가 발급한 토큰이 리소스에서 쓰일 때 추적하는 base64 식별자입니다[1]. 같은 `sessionId` 아래에서 IP·ASN·사용자 에이전트·장치가 바뀌는 지점이 있으면, 한 세션이 두 곳에서 쓰였다는 기록입니다. `incomingTokenType` 은 로그인 때 제시된 토큰 유형(`primaryRefreshToken`, `refreshToken`, `saml20` 등)입니다[1]. `authenticationDetails` 의 인증 방법 값에는 `Satisfied by token`·`Previously satisfied` 가 있고[11], 이 세부 정보로 사용자에게 비밀번호나 SMS OTP 를 다시 묻지 않고 토큰 안의 클레임으로 인증 요구를 채운 경우를 볼 수 있습니다[35]. 아래는 필드 모양만 보여 주는 만든 예시 두 건(필드 일부만 남김)입니다.

   ```json
   [
     {
       "createdDateTime": "2026-09-02T01:10:04Z",
       "userPrincipalName": "user@contoso.com",
       "appDisplayName": "Office 365 Exchange Online",
       "isInteractive": false,
       "signInEventTypes": ["nonInteractiveUser"],
       "incomingTokenType": "refreshToken",
       "sessionId": "00000000-0000-0000-0000-000000000001",
       "ipAddress": "198.51.100.20",
       "autonomousSystemNumber": 64500,
       "userAgent": "example-client/1.0",
       "status": { "errorCode": 0 }
     },
     {
       "createdDateTime": "2026-09-02T03:47:31Z",
       "userPrincipalName": "user@contoso.com",
       "appDisplayName": "Office 365 Exchange Online",
       "isInteractive": false,
       "signInEventTypes": ["nonInteractiveUser"],
       "incomingTokenType": "refreshToken",
       "sessionId": "00000000-0000-0000-0000-000000000001",
       "ipAddress": "203.0.113.77",
       "autonomousSystemNumber": 64511,
       "userAgent": "another-client/2.3",
       "status": { "errorCode": 0 }
     }
   ]
   ```

   `incomingTokenType` 의 `refreshToken`, `authenticationProtocol` 의 `refreshTokenGrant`·`prtGrant` 같은 값은 요청에 `Prefer: include-unknown-enum-members` 헤더를 넣어야 돌려받습니다[1]. Log Analytics 의 `AuthenticationProtocol` 열은 `none`, `oAuth2`, `ropc`, `wsFederation`, `saml20`, `deviceCode` 밖의 프로토콜을 `none` 으로 적습니다[10]. 토큰 보호 (Token Protection) 는 장치에 묶인 로그인 세션 토큰(PRT 등)만 받아 주는 조건부 접근 세션 제어이고, Windows·iOS/iPadOS·macOS 의 네이티브 앱에서 정식으로 제공됩니다[18]. 이 기능을 쓰는 테넌트에서는 `tokenProtectionStatusDetails` 로 로그인 토큰이 장치에 묶였는지를 봅니다[1][10]. 토큰 원본을 확보했다면 액세스 토큰 안의 `sid` 는 세션 GUID, `uti` 는 대소문자를 구분하는 토큰 식별자, `ipaddr` 는 사용자가 인증한 IP 입니다[19].

3. **서비스의 탐지를 대조합니다.** 위험 탐지는 서비스의 판단이므로 2단계의 기록으로 확인한 뒤에 씁니다. 2026년 4월 문서 기준으로 토큰과 관련된 탐지는 다음과 같습니다.

   | 탐지 이름 | `riskEventType` | 계산 | 라이선스 | 뜻 |
   |---|---|---|---|---|
   | Anomalous token | `anomalousToken` | 실시간 또는 오프라인 | P2 | 수명이 이상하거나 낯선 위치에서 재생된 세션 토큰·새로 고침 토큰. 낮음·중간 위험에서는 오탐 가능성이 여전히 높음[5] |
   | Attacker in the Middle | `attackerinTheMiddle` | 오프라인 | Microsoft 365 E5 with Enterprise Mobility + Security E5 | 인증 세션이 악성 역방향 프록시와 연결됨. Defender for Cloud Apps 로 포착하고 사용자를 고위험으로 올림[5] |
   | Possible attempt to access PRT | `attemptedPrtAccess` | 오프라인 | P2 와 Defender for Cloud Apps 단독 라이선스, 또는 Microsoft 365 E5 with EMS E5 | Defender for Endpoint 가 PRT 접근 시도를 탐지. MDE 를 배포한 조직에서만 나옴[5] |
   | Token issuer anomaly | `tokenIssuerAnomaly` | 오프라인 | P2 | SAML 토큰 발급자가 침해됐을 가능성[5] |

   탐지 계산 방식은 문서마다 달라서, 토큰 탈취 플레이북은 Anomalous token 을 오프라인 탐지로[6], 위험 탐지 문서는 실시간 또는 오프라인으로 적었습니다[5]. Sigma 규칙은 로그 원본 `azure`/`riskdetection` 에서 `riskEventType` 값으로 `anomalousToken`, `attemptedPrtAccess` 를 찾습니다[27][28]. 이상 토큰 탐지처럼 로그인 로그에 짝 기록이 없는 경고도 있으므로 `OfficeActivity`·`AuditLogs`·`CloudAppEvents` 를 함께 봅니다[6]. 탐지 규칙을 쓰는 법은 [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md) 에 있습니다.

4. **세션으로 한 일을 찾습니다.** Graph 활동 로그에는 요청마다 `SessionId`·`SignInActivityId`·`TokenIssuedAt`·`UniqueTokenId`·`IPAddress`·`RequestUri` 가 남고, `IPAddress` 는 요청을 보낸 클라이언트의 IP 입니다[7]. 로그인 로그와는 `MicrosoftGraphActivityLogs` 의 `SignInActivityId` 와 로그인 표의 `UniqueTokenIdentifier` 를 맞춰 잇고, Microsoft 앱의 활동은 짝이 되는 로그인 기록이 없을 수 있습니다[7]. UAL 레코드의 `AppAccessContext` 에는 앱이 사용자 대신 한 Entra 로그인의 `AADSessionId`, 토큰이 있을 때 채워지는 `UniqueTokenId`(대소문자 구분), 토큰 인증 시각 `IssuedAtTime` 이 들어가지만, 모든 레코드에 채워지는 필드는 아닙니다[8]. 메일함의 `MailItemsAccessed` 레코드에는 `SessionId`·`ClientIPAddress`·`ClientInfoString` 이 있고, `SessionId` 는 같은 계정에서 공격자의 행동과 평소 행동을 가르는 데 씁니다[9]. 메일을 읽은 기록을 해석하는 법은 [메일 계정을 빼앗겨 송금 사기를 당했나](bec.md) 에 있습니다.

5. **발판을 남겼는지 봅니다.** 세션을 쥔 쪽이 남기는 발판으로는 새로 등록한 장치, 새로 더한 MFA·비밀번호 없는 자격 증명, 받은 편지함 규칙과 전달, 권한 계정 변경이 있습니다[6]. Entra 감사 로그의 UserManagement 범주에서 `User registered security info`, `User changed default security info`, `User deleted security info`, `Admin registered security info`, `Admin updated security info`, `Admin deleted security info`, `User reviewed security info` 가 보안 정보 변경이고[6][16], Device 범주의 `Register device`, `Add device`, `Add registered owner to device` 가 장치 등록입니다[16]. Sigma `azure_change_to_authentication_method` 는 `LoggedByService` 가 `Authentication Methods`, `Category` 가 `UserManagement`, `OperationName` 이 `User registered security info` 인 레코드를 찾습니다[26]. 이 기록의 시각이 2단계에서 찾은 낯선 세션 안에 들어가는지 봅니다. 받은 편지함 규칙은 [BEC 쪽](bec.md), 앱 동의는 [악성 OAuth 앱에 동의했나](illicit-consent.md) 로 넘어갑니다.

6. **폐기 시각을 기준선으로 긋습니다.** 폐기 시각은 Entra 감사 로그에서 찾습니다. 감사 활동 목록에는 Core Directory 서비스, UserManagement 범주에 `Update StsRefreshTokenValidFrom Timestamp` 가 있으므로, 대응자가 세션을 폐기한 시각 전후로 이 활동이 남았는지 검체에서 확인합니다[16]. Graph 의 `revokeSignInSessions` 는 사용자의 새로 고침 토큰과 브라우저 세션 쿠키를 무효로 하면서 `signInSessionsValidFromDateTime` 을 현재 시각으로 바꾸고, 폐기까지 몇 분 늦을 수 있으며 외부 사용자에게는 적용되지 않습니다[15]. 이미 발급된 액세스 토큰은 폐기 뒤에도 수명 동안 남을 수 있으므로, 폐기 뒤의 활동을 해석할 때는 아래 수명을 함께 봅니다.

   | 토큰 | 수명 | 폐기와 보호 |
   |---|---|---|
   | 액세스 토큰 | 60~90분 사이 무작위(평균 75분). 조건부 접근을 쓰지 않는 테넌트의 Teams·Microsoft 365 같은 클라이언트는 2시간. 연속 액세스 평가 (Continuous Access Evaluation, CAE) 세션은 20~28시간[12] | CAE 를 지원하는 서비스(Exchange Online·SharePoint Online·Teams 등)는 사용자 삭제·비활성, 비밀번호 변경·재설정, MFA 사용 설정, 관리자의 전체 새로 고침 토큰 폐기, 고위험 사용자 탐지를 거의 실시간으로 반영하고, 전파에 최대 15분이 걸릴 수 있음[14] |
   | 새로 고침 토큰 | 단일 페이지 앱·이메일 일회용 암호 흐름 24시간, 나머지 90일. 쓸 때마다 새것으로 바뀌고 옛것을 서버가 폐기하지 않음[13] | 사용자의 비밀번호 변경은 비밀번호 기반 쿠키·토큰만 폐기하고, 관리자의 전체 새로 고침 토큰 폐기는 모두 폐기함. B2B 사용자는 홈 테넌트에서 폐기해야 함[13] |
   | PRT | 90일. 장치를 쓰는 동안 4시간마다 갱신(Windows 는 CloudAP 플러그인, macOS 는 플랫폼 SSO)[17] | 정상 작동하는 TPM 이 있는 장치에서는 장치 키와 세션 키를 TPM 이 보호함[17] |

   CAE 세션의 액세스 토큰은 최대 28시간까지 쓰일 수 있습니다[12][14]. 폐기 뒤 몇 분에서 수십 분 안에 같은 세션으로 성공한 활동이 있으면 남은 토큰일 가능성이 있고, 폐기 시각보다 늦게 발급된(`TokenIssuedAt`·`IssuedAtTime` 이 폐기 뒤인) 토큰으로 한 활동은 새로 인증했을 가능성이 높으므로 다시 1단계로 돌아갑니다.

7. **다른 서비스에서 같은 질문을 합니다.**

   | 서비스 | 볼 기록 | 뜻 |
   |---|---|---|
   | Google Workspace | 로그인 로그 `user_signed_out_due_to_suspicious_session_cookie`(매개변수 `affected_email_address`) | 의심스러운 세션 쿠키를 감지해 사용자를 로그아웃시킴[20] |
   | Google Workspace | 로그인 로그의 `login_type` 값 `exchange` | 기존 자격 증명을 다른 유형으로 바꿈(예: OAuth 토큰을 SID 로). 이미 로그인한 세션과 합쳐졌다는 표시일 수 있음[20] |
   | Google Workspace | 관리 로그 `RESET_SIGNIN_COOKIES`(매개변수 `USER_EMAIL`) | 관리자가 사용자의 로그인 쿠키를 재설정하고 다시 로그인하게 함. 폐기 시각의 기준[21] |
   | Okta | `security.session.detect_client_roaming` | 세션 로밍 감지[23] |
   | Okta | `user.session.context.change` | 세션이 쓰이는 맥락이 만들어질 때와 크게 달라짐. 보안 문제를 가리키는 경우가 많음[23] |
   | Okta | `app.oauth2.token.detect_reuse`, `app.oauth2.as.token.detect_reuse` | 일회용 새로 고침 토큰을 다시 쓰려는 시도[23] |
   | AWS | GuardDuty `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS` / `.InsideAWS` | EC2 인스턴스 시작 역할로 그 인스턴스 전용으로 만든 자격 증명이 AWS 밖 IP / 다른 AWS 계정에서 쓰임. 기본 심각도 High 이고, `.InsideAWS` 는 호출한 계정이 내 AWS 환경과 연결된 계정이면 Medium[25] |
   | AWS | CloudTrail `signin.amazonaws.com` 의 `GetSigninToken` | CLI 에서 쓰던 자격 증명으로 콘솔 세션을 여는 데 쓰일 수 있는 호출. AWS SSO 포털로 로그인할 때도 남으므로 Sigma 규칙은 사용자 에이전트에 `Jersey/${project.version}` 이 들어간 요청을 뺌[26] |

   Okta 시스템 로그에서는 `authenticationContext.externalSessionId` 가 같은 사용자 세션의 이벤트를, `authenticationContext.rootSessionId` 가 공통 루트 세션을 묶고, 로그인 실패 이벤트에는 세션이 없어 `externalSessionId` 가 null 입니다[24]. Okta 에서 익명 프록시를 거친 세션 시작은 Sigma 규칙이 `eventType` `user.session.start` 와 `securityContext.isProxy` `true` 로 찾습니다[32]. AWS 임시 자격 증명을 따라가는 법은 [액세스 키가 새어 나갔나](../infrastructure/leaked-keys.md) 에 있습니다.

8. **장치 쪽 증거와 합칩니다.** 클라우드 로그로 "어디서 쓰였나" 를 좁혔으면, 원래 장치에서 토큰이 새어 나갈 만한 흔적(Defender for Endpoint 경고, 의심스러운 확장 기능·프로세스)을 찾습니다[6]. 브라우저 자격 증명 이식을 시험한 연구에서는 Windows 브라우저 28종 가운데 데이터를 저장하지 않는 3종(Tor 등)을 뺀 모든 브라우저에서 자동 로그인 자격 증명을 다른 장치로 옮길 수 있었고, 자주 쓰는 웹 서비스 20종에 로그인해 데이터를 모을 수 있었습니다[33]. 같은 연구에서 대부분의 브라우저는 자격 증명을 DPAPI 로 암호화해 저장해서, 암호화할 때 쓴 Windows 계정 정보 없이 파일만 옮겨서는 복호화할 수 없었습니다[33]. 옮긴 세션은 원래 장치처럼 동작했지만, 세션을 갱신하거나 끝낼 때 장치 정보가 맞지 않으면 끊길 수 있었고 만료 뒤에는 쓸 수 없었습니다[33]. 이 연구는 서버 쪽 로그를 다루지 않았고, 옮긴 쿠키가 쓰이면 같은 세션이 다른 IP·사용자 에이전트로 이어지는 모습이 서버 로그에 남을 가능성이 있습니다. 여러 로그를 한 줄로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에 있습니다.

## 흔한 오판

- **"비대화형 로그인의 IP 가 평소 IP 이니 토큰은 제자리에서 쓰였다."** 기밀 클라이언트 (confidential client) 가 한 비대화형 로그인의 IP 는 새로 고침 요청이 실제로 온 IP 가 아니라 처음 토큰을 발급받을 때의 IP 입니다[2]. 요청 쪽 IP 는 Graph 활동 로그의 `IPAddress`, UAL·메일함 기록의 클라이언트 IP 로 한 번 더 봅니다. signIn beta 의 `ipAddressFromResourceProvider` 에 리소스가 받은 IP 가 남을 때도 있지만, 이 값은 비어 있는 경우가 많습니다[1].
- **"비대화형 로그인이 한 시각에 몰려 있다."** 앱·사용자·IP·상태·리소스 ID 가 같은 비대화형 로그인은 포털에서 한 줄로 묶이고, 묶인 줄은 같은 시각처럼 보일 수 있습니다[2]. 줄을 펼치거나 API·Log Analytics 로 받아 개별 시각을 봅니다.
- **"`incomingTokenType` 이 `none` 이니 토큰은 쓰이지 않았다."** Entra ID 는 이 목록에 없는 토큰 유형으로도 인증할 수 있으므로, 값이 목록에 없다고 토큰이 없었다고 볼 수 없습니다[1].
- **"`Previously satisfied` 가 찍혔으니 토큰 재사용이다."** 이 값은 인증 요구를 토큰 안의 클레임으로 채워 사용자에게 다시 묻지 않았다는 뜻이라 정상 SSO 에서도 나올 수 있습니다[11][35]. 로그가 처음 기록될 때는 Authentication details 탭에 "satisfied by claim in the token" 이 잘못 표시될 수도 있습니다[35]. 재사용의 근거는 같은 세션의 IP·장치가 바뀐 기록입니다.
- **"비밀번호를 바꿨으니 그 뒤 활동은 공격자가 아니다."** 사용자가 비밀번호를 바꾸거나 SSPR 을 해도 비밀번호가 아닌 방법으로 받은 쿠키·토큰과 기밀 클라이언트 토큰은 살아 있습니다[13]. 반대로 폐기 뒤의 활동을 곧바로 "공격 계속" 으로 쓰기 전에 남은 액세스 토큰 수명과 CAE 적용 여부를 봅니다[12][14].
- **"위험 탐지가 없으니 토큰 탈취는 없었다."** Free·P1 테넌트는 탐지 세부가 `generic` 으로만 보이고[5], `attemptedPrtAccess` 는 MDE 를 배포한 조직에서만 나옵니다[5]. Graph 활동 로그도 켜 두기 전의 요청은 없습니다[4].
- **"로그인 기록이 한 곳에서만 나오니 세션도 하나다."** Graph 활동 로그는 멀티테넌트 앱이 다른 테넌트에서 한 활동을 보여 주지 않고[7], 로그인 로그에 짝이 없는 이상 토큰 경고도 있습니다[6].

## 보고서 문장 예

- "Entra 비대화형 로그인 로그에 세션 ID 00000000-0000-0000-0000-000000000001 로 기록된 로그인이 2026년 9월 2일 01:10:04(UTC)에는 IP 198.51.100.20 에서, 같은 날 03:47:31(UTC)에는 IP 203.0.113.77 에서 성공한 기록이 있다. 두 줄의 사용자 에이전트와 ASN 이 다르다." (만든 예시)
- "03:47(UTC) 이후 Graph 활동 로그에 같은 세션 ID 로 IP 203.0.113.77 에서 보낸 메일 폴더 조회 요청이 있다." (만든 예시)
- "ID 보호 위험 탐지 `anomalousToken` 이 이 사용자에 대해 기록되어 있다. 이 탐지는 서비스가 토큰의 이상한 수명이나 낯선 위치를 판단한 결과이며, 토큰이 새어 나간 경로는 알려 주지 않는다."
- 쓰지 않을 문장: "공격자가 사용자의 쿠키를 훔쳐 메일을 읽었다." 로그는 한 세션이 두 곳에서 쓰였고 그 세션으로 요청이 있었다는 것까지 보여 주고, 누가 어떤 방법으로 토큰을 얻었는지는 장치 쪽 증거 없이 말하지 못합니다. 문장을 쓰는 법은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 같은 갈래: [메일 계정을 빼앗겨 송금 사기를 당했나](bec.md), [악성 OAuth 앱에 동의했나](illicit-consent.md), [MFA 피로 공격을 당했나](mfa-fatigue.md)
- 개념: [토큰과 세션](../../01-foundations/identity/tokens-sessions.md), [다단계 인증과 조건부 접근](../../01-foundations/identity/mfa-conditional-access.md)
- 기록: [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md), [OAuth 토큰 기록](../../02-artifacts/google-workspace/token-audit.md), [Okta 시스템 로그](../../02-artifacts/saas/okta.md)
- 수집: [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md)
- 다른 판: [[windows] 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html)

## 참고 문헌

1. Microsoft, "signIn resource type" (Microsoft Graph beta). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
2. Microsoft, "Non-interactive user sign-ins" (concept-noninteractive-sign-ins.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-noninteractive-sign-ins.md
3. Microsoft, "signIn resource type" (Microsoft Graph v1.0). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-1.0
4. Microsoft, "Microsoft Entra data retention" (reference-reports-data-retention.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
5. Microsoft, "What are risk detections?" (Microsoft Entra ID Protection). https://learn.microsoft.com/en-us/entra/id-protection/concept-identity-protection-risks
6. Microsoft, "Token theft playbook". https://learn.microsoft.com/en-us/security/operations/token-theft-playbook
7. Microsoft, "Microsoft Graph activity logs overview". https://learn.microsoft.com/en-us/graph/microsoft-graph-activity-logs-overview
8. Microsoft, "Office 365 Management Activity API schema". https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
9. Microsoft, "Use MailItemsAccessed to investigate compromised accounts". https://learn.microsoft.com/en-us/purview/audit-log-investigate-accounts
10. Microsoft, "SigninLogs" (Azure Monitor Logs table reference). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
11. Microsoft, "authenticationDetail resource type" (Microsoft Graph beta). https://learn.microsoft.com/en-us/graph/api/resources/authenticationdetail?view=graph-rest-beta
12. Microsoft, "Access tokens in the Microsoft identity platform" (access-tokens.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity-platform/access-tokens.md
13. Microsoft, "Refresh tokens in the Microsoft identity platform" (refresh-tokens.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity-platform/refresh-tokens.md
14. Microsoft, "Continuous access evaluation". https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation
15. Microsoft, "user: revokeSignInSessions" (Microsoft Graph v1.0). https://learn.microsoft.com/en-us/graph/api/user-revokesigninsessions?view=graph-rest-1.0
16. Microsoft, "Microsoft Entra audit log activity reference" (reference-audit-activities.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
17. Microsoft, "What is a Primary Refresh Token?" (concept-primary-refresh-token.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/devices/concept-primary-refresh-token.md
18. Microsoft, "Conditional Access: Token Protection" (concept-token-protection.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/conditional-access/concept-token-protection.md
19. Microsoft, "Access token claims reference". https://learn.microsoft.com/en-us/entra/identity-platform/access-token-claims-reference
20. Google, "Login activity events" (Admin SDK Reports API). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/login
21. Google, "Admin user settings activity events" (Admin SDK Reports API). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-user-settings
22. Google, "Data retention and lag times" (Google Workspace Admin Help). https://support.google.com/a/answer/7061566?hl=en
23. Okta, "Event types" (okta-event-types.csv). https://developer.okta.com/docs/okta-event-types.csv
24. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
25. AWS, "GuardDuty IAM finding types", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-iam.html
26. SigmaHQ, azure_change_to_authentication_method.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/audit_logs/azure_change_to_authentication_method.yml ; aws_console_getsignintoken.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_console_getsignintoken.yml
27. SigmaHQ, azure_identity_protection_anomalous_token.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/identity_protection/azure_identity_protection_anomalous_token.yml
28. SigmaHQ, azure_identity_protection_prt_access.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/identity_protection/azure_identity_protection_prt_access.yml
29. Invictus Incident Response, Microsoft-Extractor-Suite, Scripts/Get-AzureEntraGraphLogs.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureEntraGraphLogs.ps1
30. T0pCyber, Hawk, Hawk/functions/User/Get-HawkUserEntraIDSignInLog.ps1. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/User/Get-HawkUserEntraIDSignInLog.ps1
31. ANSSI-FR, DFIR-O365RC, DFIR-O365RC/DFIR-O365RC.psm1. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/DFIR-O365RC.psm1
32. SigmaHQ, okta_user_session_start_via_anonymised_proxy.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/identity/okta/okta_user_session_start_via_anonymised_proxy.yml
33. Uk Hur, Soojin Kang, Giyoon Kim, Jongsung Kim, "A study on cloud data access through browser credential migration in Windows environment", Forensic Science International: Digital Investigation 45 (2023) 301568. DOI 10.1016/j.fsidi.2023.301568
34. Microsoft, "AADNonInteractiveUserSignInLogs" (Azure Monitor Logs table reference). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadnoninteractiveusersigninlogs
35. Microsoft, "Learn about the sign-in log activity details" (concept-sign-in-log-activity-details.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
