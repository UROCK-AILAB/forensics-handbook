---
title: "토큰과 세션"
parent: "기반 · 계정과 인증"
nav_order: 50
---

# 토큰과 세션 (Tokens·Sessions)

클라우드 서비스에서는 로그인을 한 번 하고 나면 그 뒤의 접근이 토큰과 세션 쿠키로 이어집니다. 그래서 "그 세션에서 무엇을 했나" 를 말하려면 로그인 기록 하나와 그 뒤의 활동 기록 여럿을 토큰·세션 식별자로 이어 붙여야 합니다.

## 이 형식을 쓰는 아티팩트

이 쪽은 파일 형식이 아니라 로그인 뒤의 접근을 이어 주는 증표를 다룹니다. 액세스 토큰 (access token) 은 API 를 부를 때 내는 짧은 수명의 증표이고, 새로 고침 토큰 (refresh token) 은 사용자가 다시 인증하지 않아도 새 액세스 토큰을 받게 해 주는 긴 수명의 증표입니다. 브라우저에서는 세션 쿠키 (session cookie) 가 같은 일을 합니다. AWS 처럼 토큰 대신 임시 자격 증명 (temporary security credentials) 을 내주는 서비스도 있습니다. 증표를 새로 받거나 쓸 때 서비스가 남기는 식별자가 로그를 잇는 고리가 됩니다.

| 서비스 | 세션을 잇는 증표 | 레코드 속 세션·토큰 식별자 | 대표 기록 |
|---|---|---|---|
| Microsoft Entra ID·Microsoft 365 | 액세스 토큰, 새로 고침 토큰, 주 새로 고침 토큰 (PRT), 브라우저 세션 쿠키 | 로그인 로그 `sessionId`·`uniqueTokenIdentifier`, 통합 감사 로그 `AppAccessContext.AADSessionId`·`UniqueTokenId`, Graph 활동 로그 `SessionId`·`SignInActivityId` | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md) |
| Azure | Entra 액세스 토큰 | 활동 로그 `claims` 안의 `uti`·`iat` | [활동 로그](../../02-artifacts/azure/activity-log.md) |
| AWS | STS 임시 자격 증명(액세스 키 ID 가 `ASIA` 로 시작) | `userIdentity.accessKeyId`, `sessionContext.attributes.creationDate`, `sessionContext.signInSessionArn` | [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md) |
| Google Cloud | 서비스 계정의 짧은 수명 OAuth 2.0 액세스 토큰 | `GenerateAccessToken` 기록, `serviceAccountDelegationInfo[]` | [IAM과 서비스 계정 키](../../02-artifacts/gcp/iam-keys.md) |
| Google Workspace | 로그인 세션 쿠키, 앱에 준 OAuth 토큰 | 로그인 로그 `login_type`, 토큰 로그 `activity` 이벤트 | [로그인 기록](../../02-artifacts/google-workspace/login-audit.md), [OAuth 토큰 기록](../../02-artifacts/google-workspace/token-audit.md) |
| Okta | Okta 세션 | `authenticationContext.externalSessionId`·`rootSessionId`, `transaction.id` | [Okta 시스템 로그](../../02-artifacts/saas/okta.md) |
| Slack | 로그인 세션 | 접근 기록의 사용자·IP·사용자 에이전트 조합 | [Slack 감사 로그](../../02-artifacts/saas/slack.md) |

토큰을 받는 주체(사람·서비스 주체·역할)의 식별자는 [클라우드 계정과 역할](users-roles.md)에서, 앱에 준 권한과 동의 기록은 [OAuth 앱과 동의](oauth-consent.md)에서 다룹니다.

## 구조

### Microsoft Entra ID 의 토큰 종류와 수명

2026년 9월 문서 기준 기본 수명은 아래와 같습니다. 액세스 토큰 수명은 구성 가능 토큰 수명 (Configurable token lifetime, CTL) 정책으로 바꿀 수 있고[1], 브라우저 세션 길이는 조건부 접근 로그인 빈도 (sign-in frequency) 설정에 따라 달라집니다[5].

| 증표 | 기본 수명 | 갱신·무효화 |
|---|---|---|
| 액세스 토큰 | 발급 때 60~90분 사이에서 무작위(평균 75분). 조건부 접근을 쓰지 않는 테넌트의 Teams·Microsoft 365 같은 클라이언트는 2시간. 연속 접근 평가 (Continuous Access Evaluation, CAE) 를 켠 조직의 긴 수명 토큰은 20~28시간[1] | 만료되면 클라이언트가 새로 고침 토큰으로 조용히 새로 받음[1] |
| 새로 고침 토큰 | 단일 페이지 앱 (SPA) 24시간, 이메일 일회용 암호 흐름 24시간, 그 밖 90일[2] | 쓸 때마다 새 토큰으로 바뀌지만 옛 토큰은 취소되지 않음[2] |
| 주 새로 고침 토큰 (Primary Refresh Token, PRT) | 발급 뒤 90일, 기기를 쓰는 동안 계속 갱신[3] | Windows 는 CloudAP 플러그인이 4시간마다 갱신, macOS·Linux 도 4시간, iOS 는 충전 중에 2일에 한 번 이하로 추가 갱신[3] |
| 브라우저 세션 | 사용자 로그인 빈도 기본값은 90일 굴러가는 창 (rolling window)[5] | 지속 브라우저 세션이면 브라우저를 닫았다 열어도 로그인이 유지됨[5] |

새로 고침 토큰은 사용자와 클라이언트에 묶이고, 암호화돼 있어 Microsoft ID 플랫폼만 읽을 수 있습니다[2]. 클라이언트는 액세스 토큰을 내용을 모르는 문자열로 다뤄야 하고, Microsoft API 가 받는 토큰은 풀어 볼 수 있는 JWT 가 아닐 수도 있습니다[1]. 그래서 토큰 원문보다는 로그에 남은 토큰 식별자로 조사하게 됩니다.

PRT 는 Windows 10 이상에서 Entra 가입·하이브리드 가입 기기에 조직 계정으로 로그인할 때 받습니다[3]. TPM 이 있으면 토큰 요청과 PRT 갱신 요청은 TPM 이 지키는 세션 키로 서명되고, 이 세션 키로 서명하지 않은 요청은 Entra 가 무효로 처리합니다[3]. 조건부 접근 정책은 PRT 를 발급할 때도, 갱신할 때도 평가하지 않습니다[3]. PRT 는 사용자나 기기를 삭제·비활성화하면 무효가 되고, 비밀번호로 받은 PRT 는 비밀번호를 바꾸면 무효가 됩니다[3]. 다만 삭제·비활성화된 사용자라도 전에 로그인했던 기기에서는 CloudAP 가 상태를 알아챌 때까지 캐시 로그인이 됩니다[3]. 토큰에 다단계 인증 결과가 실려 가는 방식은 [다단계 인증과 조건부 접근](mfa-conditional-access.md)에서 다룹니다.

새로 고침 토큰이 취소되는 범위는 무엇이 일어났는지에 따라 다릅니다[2].

| 일어난 일 | 비밀번호 기반 쿠키 | 비밀번호 기반 토큰 | 비밀번호 아닌 쿠키 | 비밀번호 아닌 토큰 | 기밀 클라이언트 토큰 |
|---|---|---|---|---|---|
| 비밀번호 만료 | 유지 | 유지 | 유지 | 유지 | 유지 |
| 사용자가 비밀번호 변경, 셀프 서비스 재설정 (SSPR), 관리자가 Azure 포털에서 재설정 | 취소 | 취소 | 유지 | 유지 | 유지 |
| 관리자가 Entra 관리 센터나 Microsoft 365 관리 센터에서 재설정 | 취소 | 취소 | 유지 | 취소 | 취소 |
| 사용자가 자기 새로 고침 토큰 취소, 관리자가 사용자의 새로 고침 토큰 전부 취소 | 취소 | 취소 | 취소 | 취소 | 취소 |
| 단일 로그아웃 (single sign-out) | 취소 | 유지 | 취소 | 유지 | 유지 |

B2B 사용자의 새로 고침 토큰은 리소스 테넌트에서 취소되지 않고 홈 테넌트에서 취소해야 합니다[2]. 테넌트 경계는 [테넌트·구독·계정·프로젝트](../model/tenancy.md)에서 다룹니다.

CAE 를 지원하는 서비스(Exchange Online·SharePoint Online·Teams)는 아래 중요 이벤트를 거의 실시간으로 반영합니다[4]. 사용자 계정 삭제·비활성화, 비밀번호 변경·재설정, 사용자에게 다단계 인증을 켬, 관리자가 사용자의 새로 고침 토큰을 전부 취소, ID Protection 이 높은 사용자 위험을 탐지한 경우입니다[4]. CAE 세션의 토큰 수명은 최대 28시간이고, CAE 를 지원하지 않는 클라이언트의 액세스 토큰 기본 수명은 CTL 로 바꾸지 않았다면 1시간입니다[4]. 액세스 토큰 기본 수명은 출처마다 달라서, 토큰 문서(2025-05-14)는 60~90분 무작위로, CAE 문서(2026-04-08 갱신)는 1시간으로 적습니다[1][4]. 위치 정책에 적힌 IP 범위의 합이 5,000 을 넘으면 Entra 는 1시간짜리 CAE 토큰을 냅니다[4].

액세스 토큰 클레임 가운데 조사에 쓰는 것은 아래와 같습니다[6].

| 클레임 | 뜻 |
|---|---|
| `iat` | 이 토큰의 인증이 일어난 시각(Unix 시각) |
| `nbf`·`exp` | 처리해도 되는 시작 시각·만료 시각(Unix 시각). 리소스는 인증 변경이나 토큰 취소 때문에 `exp` 전에도 토큰을 거부할 수 있음 |
| `amr` | 인증 방법 배열 |
| `sid` | 새 세션이 생길 때 만들어지는 세션 식별자(GUID) |
| `uti` | 토큰 식별자. JWT 명세의 `jti` 와 같고, 토큰마다 하나이며 대소문자를 가림 |
| `xms_cc` | 값이 `cp1` 이면 클레임 챌린지를 처리할 수 있는 클라이언트 |

### Microsoft 로그인 로그의 토큰·세션 필드

로그인 로그의 `signInEventTypes` 값은 `interactiveUser`, `nonInteractiveUser`, `servicePrincipal`, `managedIdentity` 가운데 하나입니다[9]. 비대화형 로그인 (non-interactive sign-in) 은 클라이언트 앱이나 OS 구성 요소가 사용자 대신 인증 요소 없이 한 로그인입니다[7]. 새로 고침 토큰으로 액세스 토큰을 받거나, 인가 코드를 토큰으로 바꾸거나, Entra 가입 PC 에서 SSO 로 앱에 들어가거나, 모바일 기기에서 FOCI (Family of Client IDs) 로 두 번째 Office 앱에 로그인한 일이 여기에 남습니다[7]. 2025년 4월 11일부터는 FIDO2 키로 새로 고침 토큰을 받는 새 로그인도 모두 비대화형 로그에 남습니다[7].

| 필드 | 뜻 | 조사에서 쓰는 곳 |
|---|---|---|
| `sessionId` | 로그인 때 만들어진 세션의 식별자[9] | 같은 세션의 로그인 기록 묶기, 통합 감사 로그 `AADSessionId`·Graph 활동 로그 `SessionId` 와 맞추기 |
| `uniqueTokenIdentifier` | 발급된 토큰을 리소스 쪽에서 추적하는 base64 식별자[9] | Graph 활동 로그 `SignInActivityId` 와 맞추기[10] |
| `correlationId` | 로그인을 시작할 때 클라이언트가 보내는 식별자[9]. 클라이언트가 넘긴 값이라 Entra 가 정확성을 보장하지 않음[8] | 한 로그인 흐름의 여러 요청 묶기 |
| 요청 ID (Request ID) | 발급된 토큰에 대응하는 식별자. 특정 토큰의 로그인을 찾으려면 토큰에서 요청 ID 를 먼저 꺼내야 함[8] | 가진 토큰에서 로그인 찾기 |
| `originalRequestId` | 인증 흐름 첫 요청의 ID[9] | 흐름의 시작점 찾기 |
| `originalTransferMethod` | 세션을 시작한 전달 방법. `none`, `deviceCodeFlow`, `authenticationTransfer`[9] | 기기 코드 흐름·인증 전달로 시작된 세션 가리기 |
| `incomingTokenType` | 로그인 때 제시된 토큰 종류. `none`, `primaryRefreshToken`, `saml11`, `saml20`, `remoteDesktopToken`, `refreshToken`[9] | PRT·새로 고침 토큰으로 이어진 로그인 가리기 |
| `clientCredentialType` | 클라이언트나 서비스 주체가 낸 자격 증명 종류. `clientSecret`, `clientAssertion`, `federatedIdentityCredential`, `managedIdentity`, `certificate` 등[9] | 서비스 주체 로그인의 인증 수단 보기 |
| `tokenProtectionStatusDetails` | 토큰이 기기에 묶였는지. 예전 필드 `signInTokenProtectionStatus`·`appTokenProtectionStatus` 는 폐기됨[9] | 기기에 묶인 토큰인지 보기 |

이 필드들은 Graph beta 의 `signIn` 리소스에 정의돼 있고[9] v1.0 의 `signIn` 리소스에는 `sessionId`·`uniqueTokenIdentifier`·`incomingTokenType` 이 없으므로[45], 수집한 자료가 어느 API 판으로 받은 것인지 먼저 확인합니다. 로그인 로그는 시스템이 만들고 바꾸거나 지울 수 없습니다[7]. 로그인 로그 필드 전체는 [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md)에서 다룹니다.

로그인 뒤의 활동 기록에는 아래 필드가 토큰·세션을 가리킵니다.

| 기록 | 필드 | 뜻 |
|---|---|---|
| 통합 감사 로그 공통 스키마 `AppAccessContext` | `AADSessionId` | 앱이 사용자 대신 한 Entra 로그인의 SessionId[11] |
| | `UniqueTokenId` | Entra 토큰이 있는 요청에만 채워지는 토큰 식별자, 대소문자를 가림[11] |
| | `IssuedAtTime` | 그 Entra 토큰의 인증이 일어난 시각[11] |
| | `ClientAppId`·`ClientAppName`·`CorrelationId` | 사용자 대신 접근한 앱, 서비스 사이 상관 식별자[11] |
| Microsoft Graph 활동 로그 | `SessionId`·`SignInActivityId`·`UniqueTokenId`·`TokenIssuedAt` | 인증 세션 식별자, 로그인 활동 식별자, API 호출에 쓴 토큰 식별자, 토큰 발급 시각[10] |
| Azure 활동 로그 `claims` | `uti`·`iat`·`nbf`·`exp`·`ipaddr`·`appid`·`http://schemas.microsoft.com/claims/authnmethodsreferences` | 호출에 쓴 토큰의 클레임[12] |

`AppAccessContext` 의 필드는 모두 필수가 아니라서 빠진 레코드가 있습니다[11].

### AWS 임시 자격 증명과 세션

AWS 의 임시 자격 증명은 정한 기간 동안 유효하고, 기간은 900초(15분)부터 129,600초(36시간)까지이며 기본은 43,200초(12시간)입니다[19]. `AssumeRole` 의 `DurationSeconds` 는 900~43,200초이고 기본은 3,600초이며, 역할 체이닝 (role chaining) 으로 받은 세션은 최대 1시간입니다[20]. 임시 자격 증명의 액세스 키 ID 는 `ASIA` 로 시작하고, 이 값은 비밀 액세스 키·세션 토큰과 함께 있을 때만 고유합니다[24].

CloudTrail 레코드에서 세션은 `userIdentity.sessionContext` 로 읽습니다[22].

| 필드 | 뜻 |
|---|---|
| `sessionContext.attributes.creationDate` | 임시 자격 증명이 발급된 시각[22] |
| `sessionContext.attributes.mfaAuthenticated` | 자격 증명을 쓴 루트 사용자나 IAM 사용자가 MFA 기기로도 인증했으면 `true`[22] |
| `sessionContext.sessionIssuer` | 임시 자격 증명을 받은 원래 주체(역할 등)[22] |
| `sessionContext.signInSessionArn` | 요청의 바탕이 된 로그인 세션의 ARN. `arn:aws:signin:region:account-id:session/uuid` 모양이고 주체 ARN 보다 세션을 더 좁게 가리킴[22] |
| `sessionContext.sourceIdentity` | 역할을 넘겨받아 행동한 원래 사용자. 역할 체이닝 동안 유지됨[22][20] |
| `sessionCredentialFromConsole` | 콘솔 세션의 자격 증명으로 부른 호출이면 `"true"`[25] |

STS 의 `AssumeRole`·`AssumeRoleWithSAML`·`AssumeRoleWithWebIdentity` 는 읽기 전용 이벤트로 기록되지만 CloudTrail 은 이 셋의 `responseElements` 를 `secretAccessKey` 만 빼고 모두 남깁니다[23]. `GetFederationToken`·`GetSessionToken`·`AssumeRoot` 도 응답 요소를 남깁니다[23]. 그래서 발급 레코드의 `responseElements.credentials.accessKeyId` 로 이후 호출의 `userIdentity.accessKeyId` 를 찾아 이어 붙일 수 있습니다. 응답에는 `sessionToken` 값도 남으므로 CloudTrail 사본은 자격 증명이 든 자료로 다룹니다[23].

콘솔 로그인은 `eventSource` 가 `signin.amazonaws.com`, `eventName` 이 `ConsoleLogin`, `eventType` 이 `AwsConsoleSignIn` 인 레코드로 남고, `additionalEventData.MFAUsed` 에 MFA 사용 여부가 적힙니다[25]. 페더레이션 콘솔 로그인 토큰 요청은 같은 `eventSource` 의 `GetSigninToken` 으로 남고[25], AWS SSO 포털로 로그인할 때도 생깁니다[26]. 액세스 키 자체의 수명과 마지막 사용 정보는 [AWS IAM](../../02-artifacts/aws/iam.md)에서 다룹니다.

### Google Cloud

서비스 계정의 짧은 수명 자격 증명은 OAuth 2.0 액세스 토큰이고 기본 1시간 뒤 만료됩니다[27]. 이런 토큰은 몇 시간 이하로 짧고 자동으로 갱신되지 않습니다[28]. 다른 주체가 서비스 계정을 가장 (impersonation) 해 토큰을 받으려면 `iam.serviceAccounts.getAccessToken` 권한(역할 `roles/iam.serviceAccountTokenCreator`)이 있어야 합니다[28]. 토큰 발급은 `serviceName` 이 `iamcredentials.googleapis.com`, `methodName` 이 `GenerateAccessToken` 인 감사 로그로 남고, 이 레코드의 `logName` 은 데이터 접근 로그(`cloudaudit.googleapis.com%2Fdata_access`)입니다[29]. 가장해서 부른 호출 레코드의 `authenticationInfo.serviceAccountDelegationInfo[]` 에는 서비스 계정에 위임한 실제 주체의 이력이 원래 순서대로 들어갑니다[30]. App Engine·GKE 같은 일부 서비스는 짧은 수명 자격 증명을 만든 신원을 남기지 않습니다[27]. 키 인증 흔적과 데이터 접근 로그 설정은 [IAM과 서비스 계정 키](../../02-artifacts/gcp/iam-keys.md)에서 다룹니다.

### Google Workspace

로그인 로그의 `login_type` 값 `exchange` 는 기존 자격 증명을 다른 형식으로 바꾼 로그인(예: OAuth 토큰을 SID 로)이고, 이미 로그인한 세션 둘이 합쳐졌을 가능성을 뜻합니다[31]. `reauth` 는 이미 인증된 사용자가 다시 인가해야 하는 경우입니다[31]. 로그인 로그에는 `logout` 이벤트와, 의심스러운 세션 쿠키 때문에 로그아웃시킨 `user_signed_out_due_to_suspicious_session_cookie` 이벤트도 있습니다[31]. 관리자 조치는 관리 콘솔 감사 로그에 `RESET_SIGNIN_COOKIES`("Cookies reset for {USER_EMAIL} and forced re-login"), `UNBLOCK_USER_SESSION`, `REVOKE_3LO_TOKEN`, `REVOKE_3LO_DEVICE_TOKENS` 로 남고[32], 세션 길이 설정 변경은 `SESSION_CONTROL_SETTINGS_CHANGE`·`CHANGE_SESSION_LENGTH` 로 남습니다[33].

로그인 활동 보고서는 명시적인 비밀번호 로그인과 SAML SSO 로그인만 기록합니다[34]. 앱이 OAuth 토큰으로 API 를 부른 일은 토큰 로그의 `activity` 이벤트로 봅니다[35]. 레코드 상세는 [로그인 기록](../../02-artifacts/google-workspace/login-audit.md)과 [OAuth 토큰 기록](../../02-artifacts/google-workspace/token-audit.md)에서 다룹니다.

### Okta·Slack

Okta 시스템 로그에서 `authenticationContext.externalSessionId` 는 같은 사용자 세션의 이벤트를, `transaction.id` 는 한 요청으로 함께 생긴 이벤트를 묶습니다[37]. Okta 시스템 행위자가 사용자 대신 한 일은 `externalSessionId` 가 다를 수 있어서, 같은 루트 세션을 공유하는 이벤트는 `authenticationContext.rootSessionId` 로 모읍니다[37]. 로그인에 실패한 이벤트는 세션이 생기지 않아 `externalSessionId` 가 null 일 수 있습니다[37]. 세션 이벤트 이름은 `user.session.start`, `user.session.end`, `user.session.clear`, `security.session.detect_client_roaming`(세션 로밍 탐지), `user.session.impersonation.grant`·`user.session.impersonation.initiate` 이고, 일회용 새로 고침 토큰을 다시 쓰려 한 시도는 `app.oauth2.as.token.detect_reuse` 로 남습니다[38].

Slack 의 `team.accessLogs` 는 사용자·IP·사용자 에이전트 조합마다 `date_first`·`date_last`·`count`·`ip`·`user_agent`·`isp`·`country`·`region` 을 묶어 돌려주고, 유료 요금제에서만 쓸 수 있습니다[39]. `isp`·`country`·`region` 은 IP 로 짐작한 값입니다[39]. 감사 로그에는 `user_login`, `user_login_failed`, `user_logout`, `user_session_invalidated`, `user_session_reset_by_admin`, `bulk_session_reset_by_admin` 이 있습니다[40].

## 읽는 법

1. **로그인 레코드에서 세션과 토큰 식별자를 적어 둡니다.** Entra 는 대화형·비대화형 로그인 로그의 `sessionId`·`uniqueTokenIdentifier`·`incomingTokenType` 을, AWS 는 `AssumeRole`·`GetSessionToken` 레코드의 `responseElements.credentials.accessKeyId` 를, Okta 는 `externalSessionId` 를 봅니다.
2. **활동 기록에서 같은 값을 찾습니다.** Entra 세션은 통합 감사 로그 `AppAccessContext.AADSessionId`, Graph 활동 로그 `SessionId` 로 찾습니다[11][10]. Graph 활동 로그의 `SignInActivityId` 는 로그인 로그의 `UniqueTokenIdentifier` 와 맞춥니다[10]. AWS 는 이후 레코드의 `userIdentity.accessKeyId` 와 `sessionContext.attributes.creationDate` 가 발급 레코드와 같은지 봅니다.
3. **세션 안에서 IP·사용자 에이전트·기기가 바뀌는지 봅니다.** 한 세션 식별자 아래에서 IP 나 사용자 에이전트가 갑자기 바뀌면 다른 곳에서 세션을 이어 썼을 가능성이 있습니다. IP 해석은 [IP·사용자 에이전트·위치](../logging/ip-ua-geo.md)에서 다룹니다.
4. **세션이 끝난 기록을 찾습니다.** 무효화 작업, 로그아웃, 만료·취소 오류 코드를 찾아 세션의 끝을 정합니다(아래 "세션 무효화 기록").

Log Analytics 로 모았다면 Graph 활동 로그와 로그인 로그를 아래처럼 잇습니다[10].

```kusto
MicrosoftGraphActivityLogs
| where TimeGenerated > ago(7d)
| join kind=leftouter (union SigninLogs, AADNonInteractiveUserSignInLogs, AADServicePrincipalSignInLogs, AADManagedIdentitySignInLogs, ADFSSignInLogs
 | where TimeGenerated > ago(7d))
 on $left.SignInActivityId == $right.UniqueTokenIdentifier
```

Microsoft 앱의 활동 로그는 모두 짝이 되는 로그인 로그 항목이 있지는 않습니다[10].

AWS 에서 발급과 사용을 잇는 모양은 아래와 같습니다. 필드 이름과 배치는 문서 예시를 따른 만든 예시이고 값은 모두 지어낸 것입니다.

```json
{
  "eventTime": "2026-03-02T01:15:07Z",
  "eventSource": "sts.amazonaws.com",
  "eventName": "AssumeRole",
  "sourceIPAddress": "203.0.113.10",
  "requestParameters": {
    "roleArn": "arn:aws:iam::123456789012:role/ExampleRole",
    "roleSessionName": "example-session"
  },
  "responseElements": {
    "credentials": {
      "accessKeyId": "ASIAIOSFODNN7EXAMPLE",
      "expiration": "Mar 2, 2026, 2:15:07 AM"
    }
  }
}
```

```json
{
  "eventTime": "2026-03-02T01:40:52Z",
  "eventSource": "s3.amazonaws.com",
  "eventName": "ListBuckets",
  "sourceIPAddress": "198.51.100.25",
  "userIdentity": {
    "type": "AssumedRole",
    "accessKeyId": "ASIAIOSFODNN7EXAMPLE",
    "sessionContext": {
      "sessionIssuer": { "type": "Role", "userName": "ExampleRole" },
      "attributes": { "creationDate": "2026-03-02T01:15:07Z", "mfaAuthenticated": "false" }
    }
  }
}
```

두 번째 레코드의 `accessKeyId` 와 `creationDate` 가 첫 번째 레코드의 발급 값과 맞으므로 같은 임시 자격 증명으로 부른 호출로 읽습니다. 발급 요청 IP(203.0.113.10)와 사용 IP(198.51.100.25)가 다르면, 자격 증명을 받은 곳과 쓴 곳이 다르다는 사실까지만 보고서에 씁니다.

### 세션 무효화 기록

| 서비스 | 무효화 흔적 |
|---|---|
| Entra ID | Graph `revokeSignInSessions` 는 사용자에게 발급된 새로 고침 토큰과 브라우저 세션 쿠키를 무효로 만들고 사용자 속성 `signInSessionsValidFromDateTime` 을 호출한 시각으로 바꿉니다[13]. 감사 로그에는 `UserManagement` 범주의 "Update StsRefreshTokenValidFrom Timestamp" 작업이 있습니다[14]. 무효화 뒤 옛 토큰을 쓰면 오류 코드 AADSTS50173(취소되어 만료된 권한 부여, TokensValidFrom 날짜 안내)이 남을 수 있습니다[15]. |
| AWS | 콘솔에서 역할의 "Revoke active sessions" 를 누르면 역할에 인라인 정책 `AWSRevokeOlderSessions` 가 붙습니다[21]. 이 정책은 `aws:TokenIssueTime` 이 지정 시각보다 이른 임시 자격 증명의 요청을 모두 거부하고, 콘솔 버튼은 누른 시각에서 약 30초 뒤까지를 기준으로 삼습니다[21]. 정책을 붙이려면 `PutRolePolicy` 권한이 필요하므로, CloudTrail 에서는 이 정책 이름으로 찾습니다[21]. |
| Google Workspace | `RESET_SIGNIN_COOKIES`, `REVOKE_3LO_TOKEN`, `REVOKE_3LO_DEVICE_TOKENS`[32] |
| Okta | `user.session.clear`, `user.session.end`[38] |
| Slack | `user_session_invalidated`, `user_session_reset_by_admin`, `bulk_session_reset_by_admin`[40] |

Entra 의 다른 세션 관련 오류 코드는 AADSTS50132(SsoArtifactInvalidOrExpired)·50133(SsoArtifactRevoked, 둘 다 비밀번호 만료나 최근 변경으로 세션 무효), AADSTS70043(조건부 접근 로그인 빈도 검사로 새로 고침 토큰 만료·무효), AADSTS700082(오래 쓰지 않아 새로 고침 토큰 만료)입니다[15]. 700082 는 정상적인 토큰 수명 주기에서도 생깁니다[15].

## 포렌식에서 중요한 점

### 증명하는 것

식별자가 채워져 있으면 어떤 호출이 어느 세션(`sessionId`·`AADSessionId`·`externalSessionId`)과 어느 토큰(`uniqueTokenIdentifier`·`UniqueTokenId`·`uti`·`ASIA` 액세스 키 ID)에서 나왔는지 말할 수 있습니다[9][11][6][23][24][37]. 무효화 작업 레코드는 누가 언제 세션을 끊었는지 보여 줍니다[13][14][21]. AWS STS 발급 레코드는 어느 주체가 언제 어떤 역할 세션을 받았는지 보여 줍니다[23].

### 증명하지 못하는 것

대화형 로그인 기록이 없다고 접근이 없었다고 할 수 없습니다. 새로 고침 토큰과 쿠키로 이어진 접근은 사용자가 인증 요소를 내지 않고 일어나며 비대화형 로그에 남거나[7], Google Workspace 처럼 로그인 로그에 아예 남지 않습니다[34]. 기밀 클라이언트 (confidential client) 의 비대화형 로그인 IP 는 실제 새로 고침 요청을 보낸 곳이 아니라 처음 토큰을 받은 곳의 IP 입니다[7]. 무효화 작업이 있어도 이미 발급된 액세스 토큰은 CAE 를 지원하지 않는 클라이언트·리소스에서 만료될 때까지 쓰일 수 있고, 그 길이는 위의 수명 값을 따릅니다[1][4]. AWS 임시 자격 증명은 만료될 때까지 유효하고, 쓰지 못하게 하려면 권한을 바꾸거나 역할 세션을 취소해야 합니다[19][21]. 세션 식별자가 같다는 사실은 같은 증표를 썼다는 뜻이지, 같은 사람이 썼다는 뜻은 아닙니다.

Windows 환경에서 브라우저 28종으로 한 시험에서는 데이터를 저장하지 않는 3종(Tor 등)을 뺀 모든 브라우저의 자동 로그인 자격 증명을 다른 기기로 옮길 수 있었고, 자주 쓰는 웹 서비스 20종에 옮긴 자격 증명으로 로그인해 자료를 볼 수 있었습니다[41]. 옮긴 세션은 원래 기기에서처럼 동작했고 세션이 만료된 뒤에는 쓸 수 없었습니다[41]. 세션을 갱신하거나 끝낼 때 기기 정보가 맞지 않으면 세션이 끊길 수 있습니다[41]. 세션이 기기에 묶이지 않으면 새 로그인 없이 다른 곳에서 세션이 이어질 수 있으므로, 이때는 로그인 로그보다 활동 기록 속 IP·사용자 에이전트의 변화가 단서가 됩니다. 이상 토큰 탐지 가운데는 SigninLogs 에 짝이 되는 항목이 없는 것도 있어서, OfficeActivity·AuditLogs 도 함께 봅니다[17].

### 시각

| 값 | 무엇이 바뀔 때 바뀌나 | 표기 |
|---|---|---|
| Entra `CreatedDateTime` | Entra ID 가 인증을 처리한 시각[8] | [클라우드 로그의 시각](../logging/timestamps.md) 참고 |
| Entra `TimeGenerated`(Log Analytics) | 로그인 레코드가 Log Analytics 에 들어간 시각. `CreatedDateTime` 과 다름[8] | [클라우드 로그의 시각](../logging/timestamps.md) 참고 |
| 토큰 클레임 `iat`·`nbf`·`exp`, 활동 로그 `claims` | 토큰의 인증·유효 시작·만료 시각[6] | Unix 시각(초)[6][12] |
| 통합 감사 로그 `IssuedAtTime`, Graph 활동 로그 `TokenIssuedAt` | 토큰의 인증·발급 시각[11][10] | `IssuedAtTime` 은 Edm.Date[11], `TokenIssuedAt` 은 datetime[10] |
| AWS `sessionContext.attributes.creationDate` | 임시 자격 증명 발급 시각. 같은 세션의 레코드에서는 값이 같음[22] | ISO 8601. 문서 설명은 basic 표기(`20131102T010628Z`)[22], 로그 예시는 확장 표기(`2023-07-15T03:51:12Z`)[25] |
| AWS STS 응답 `expiration` | 자격 증명 만료 시각 | `"Aug 28, 2023, 7:00:58 PM"` 처럼 ISO 8601 이 아닌 문자열[23] |
| Slack `date_first`·`date_last` | 조합의 첫 접근·마지막 접근 | Unix 시각(초)[39] |
| Okta `published` | 이벤트가 일어난 시각. 폴링 결과는 내부 저장 시각 순이라 `published` 순서와 다를 수 있음[37] | [클라우드 로그의 시각](../logging/timestamps.md) 참고 |

비대화형 로그인은 앱·사용자·IP·상태·리소스 ID 가 같으면 한 줄로 묶이고, 묶인 줄은 같은 시각처럼 보일 수 있어서 펼쳐야 각 로그인의 시각이 보입니다[7]. 묶는 창은 1시간·6시간·24시간 가운데 고릅니다[7]. Graph 활동 로그는 대부분 지역에서 30분 안에 전달되지만 2시간까지 걸리기도 하고[10], Google Workspace 토큰 로그는 두어 시간 늦게 들어옵니다[36]. 서비스별 시각 표기와 시간대는 [클라우드 로그의 시각](../logging/timestamps.md)에서 다룹니다.

## 함정

- 새로 고침 토큰은 쓸 때마다 새것으로 바뀌지만 옛 토큰은 취소되지 않습니다[2]. 빼돌린 옛 토큰도 수명 동안 쓸 수 있으므로, 새 토큰이 발급된 시각을 옛 토큰이 끝난 시각으로 보지 않습니다.
- 비밀번호를 어디서 재설정했는지에 따라 취소 범위가 다릅니다. Azure 포털 재설정과 사용자의 비밀번호 변경은 비밀번호 아닌 방식으로 받은 토큰과 기밀 클라이언트 토큰을 남깁니다[2]. 보고서에 "비밀번호를 바꿔 세션을 끊었다" 고 쓰기 전에 재설정 경로와 토큰 전체 취소 기록을 확인합니다.
- B2B 게스트의 토큰과 세션은 리소스 테넌트에서 끊기지 않고 홈 테넌트에서 끊어야 합니다[2][13].
- PRT 는 발급·갱신 때 조건부 접근을 평가하지 않습니다[3]. 정책을 바꾼 뒤에도 PRT 갱신 기록은 계속 남을 수 있습니다.
- `revokeSignInSessions` 는 호출 뒤 몇 분 늦게 반영될 수 있습니다[13]. `signInSessionsValidFromDateTime` 속성과 감사 작업 "Update StsRefreshTokenValidFrom Timestamp" 가 같은 값을 가리키는지는 검체에서 시각을 대조해 확인합니다.
- `incomingTokenType` 이 목록의 값이 아니라고 토큰을 쓰지 않았다고 추론하지 않습니다. 목록에 없는 토큰 형식을 썼을 수도 있습니다[9].
- CAE 적용 여부는 한 인증의 여러 요청 가운데 하나에만 `true` 로 표시되고, 대화형·비대화형 어느 쪽에나 나올 수 있습니다[8].
- 통합 감사 로그의 SharePoint 기본 스키마에도 `UniqueTokenIdentifier` 라는 필드가 있지만 설명은 "리소스의 고유 식별자" 입니다[11]. 공통 스키마 `AppAccessContext.UniqueTokenId` 와 이름이 비슷하므로 섞지 않습니다.
- Azure 활동 로그 `claims.uti` 와 로그인 로그 `UniqueTokenIdentifier` 는 둘 다 토큰 식별자를 가리키지만[6][12], 두 값을 이어 붙이기 전에 검체에서 값이 실제로 같은지 확인합니다.
- `ASIA` 액세스 키 ID 는 비밀 키·세션 토큰과 함께일 때만 고유합니다[24]. 긴 기간을 다룰 때는 `accessKeyId` 하나만 보지 말고 `creationDate`·`sessionIssuer` 도 함께 맞춥니다.
- AWS `ConsoleLogin` 은 사용자 종류와 로그인 끝점에 따라 기록되는 리전이 다릅니다. 루트 사용자는 us-east-1·us-east-2·us-west-2 가운데 하나, 전역 끝점을 쓴 IAM 사용자는 계정 별칭 쿠키가 있으면 us-east-2·eu-north-1·ap-southeast-2 가운데 하나, 없으면 us-east-1 입니다[25]. 여러 리전의 기록을 함께 모읍니다.
- Entra ID Protection 의 이상 토큰 (`anomalousToken`) 탐지는 세션 토큰과 새로 고침 토큰을 대상으로 하고, 낮음·중간 위험에서는 오탐 가능성이 여전히 높습니다[16]. PRT 접근 시도 (`attemptedPrtAccess`) 같은 프리미엄 탐지는 P2 라이선스가 없으면 "Additional risk detected" 로만 보입니다[16].
- 로그인 로그 보관 기간은 2026년 9월 문서 기준 Entra ID Free 7일, P1·P2 30일입니다[18]. 전체 표는 [보관 기간과 라이선스](../logging/retention-licensing.md)에서 다룹니다.

## 도구

비대화형 로그인을 받는지는 도구마다 다르므로 수집 결과에 어떤 로그인 종류가 들어 있는지 먼저 확인합니다. Graph beta `signIns` 는 필터 없이 부르면 대화형 로그인만 돌려줍니다[9].

- Microsoft-Extractor-Suite 의 `Get-GraphEntraSignInLogs` 는 `-EventTypes` 로 `signInEventTypes` 를 골라 받고, 기본값 `All` 이면 대화형과 비대화형을 함께, 서비스 주체와 관리 ID 는 따로 받습니다[42].
- Untitled Goose Tool 은 `/beta/auditLogs/signIns` 를 `adfs`·`rt`·`sp`·`msi` 로 나눠 날짜별 파일(`rt_signin_log_날짜.json` 모양)로 받고, 기본 기간은 최근 29일입니다[43].
- Hawk 의 `Get-HawkUserEntraIDSignInLog` 는 Microsoft Graph PowerShell 의 `Get-MgAuditLogSignIn` 을 쓰고, `Get-HawkUserUALSignInLog` 는 통합 감사 로그에서 RecordType `AzureActiveDirectoryAccountLogon`·`AzureActiveDirectory`·`AzureActiveDirectoryStsLogon` 을 받습니다[44]. v1.0 판으로 받은 자료에는 `sessionId`·`uniqueTokenIdentifier`·`incomingTokenType` 같은 beta 필드가 없습니다[45].
- Okta 는 시스템 로그 API 에서 `authenticationContext.externalSessionId`·`transaction.id` 로 거르고[37], Slack 은 `team.accessLogs` 로 접근 조합을 받습니다[39].

수집 절차는 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md)와 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md)에서, 로그인 기록을 가려내는 방법은 [이상한 로그인 가려내기](../../03-techniques/analysis/suspicious-sign-ins.md)에서, 토큰을 빼돌렸는지 조사하는 순서는 [토큰을 훔쳐 로그인했나](../../04-scenarios/account-compromise/token-theft.md)에서 다룹니다.

함께 볼 페이지: [클라우드 계정과 역할](users-roles.md), [OAuth 앱과 동의](oauth-consent.md), [다단계 인증과 조건부 접근](mfa-conditional-access.md), [페더레이션과 SSO](federation-sso.md), [클라우드 로그의 시각](../logging/timestamps.md).

## 참고 문헌

1. Microsoft, "Access tokens in the Microsoft identity platform" (ms.date 2025-05-14). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity-platform/access-tokens.md
2. Microsoft, "Refresh tokens in the Microsoft identity platform" (ms.date 2025-11-05). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity-platform/refresh-tokens.md
3. Microsoft, "Understanding Primary Refresh Token (PRT) in Microsoft Entra ID" (ms.date 2025-06-27). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/devices/concept-primary-refresh-token.md
4. Microsoft, "Continuous access evaluation", Microsoft Learn (2026-04-08 갱신). https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-continuous-access-evaluation
5. Microsoft, "Conditional Access adaptive session lifetime", Microsoft Learn (2026-04-08 갱신). https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-session-lifetime
6. Microsoft, "Access token claims reference", Microsoft Learn (2026-06-25 갱신). https://learn.microsoft.com/en-us/entra/identity-platform/access-token-claims-reference
7. Microsoft, "Non-interactive sign-in logs" (ms.date 2026-02-09). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-noninteractive-sign-ins.md
8. Microsoft, "Learn about the sign-in log activity details" (ms.date 2026-03-04). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
9. Microsoft, "signIn resource type", Microsoft Graph beta, Microsoft Learn (2025-11-28 갱신). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
10. Microsoft, "Access Microsoft Graph activity logs", Microsoft Learn (2026-07-04 갱신). https://learn.microsoft.com/en-us/graph/microsoft-graph-activity-logs-overview
11. Microsoft, "Office 365 Management Activity API schema", Microsoft Learn (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
12. Microsoft, "Azure Activity Log event schema" (ms.date 2026-03-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
13. Microsoft, "user: revokeSignInSessions", Microsoft Graph v1.0, Microsoft Learn (2025-07-23 갱신). https://learn.microsoft.com/en-us/graph/api/user-revokesigninsessions?view=graph-rest-1.0
14. Microsoft, "Microsoft Entra audit log activity reference" (ms.date 2025-03-25). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
15. Microsoft, "Microsoft Entra authentication and authorization error codes", Microsoft Learn (2025-02-03 갱신). https://learn.microsoft.com/en-us/entra/identity-platform/reference-error-codes
16. Microsoft, "What are risk detections?", Microsoft Entra ID Protection, Microsoft Learn (2026-04-22 갱신). https://learn.microsoft.com/en-us/entra/id-protection/concept-identity-protection-risks
17. Microsoft, "Token theft playbook", Microsoft Learn (2024-03-07 갱신). https://learn.microsoft.com/en-us/security/operations/token-theft-playbook
18. Microsoft, "Microsoft Entra data retention" (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
19. AWS, "Disabling permissions for temporary security credentials", AWS IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_control-access_disable-perms.html
20. AWS, "AssumeRole", AWS Security Token Service API Reference. https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html
21. AWS, "Revoke IAM role temporary security credentials", AWS IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_revoke-sessions.html
22. AWS, "CloudTrail userIdentity element", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
23. AWS, "Logging IAM and AWS STS API calls with AWS CloudTrail", AWS IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/cloudtrail-integration.html
24. AWS, "IAM identifiers", AWS IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html
25. AWS, "AWS Management Console sign-in events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-aws-console-sign-in-events.html
26. SigmaHQ, "AWS Console GetSigninToken Potential Abuse" 규칙. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_console_getsignintoken.yml
27. Google Cloud, "Service account credentials", IAM (2026-09-24 갱신). https://cloud.google.com/iam/docs/service-account-creds
28. Google Cloud, "Service account impersonation", IAM (2026-09-24 갱신). https://cloud.google.com/iam/docs/service-account-impersonation
29. Google Cloud, "Examples of audit logs for service accounts", IAM (2026-09-24 갱신). https://cloud.google.com/iam/docs/audit-logging/examples-service-accounts
30. Google Cloud, "AuditLog", Cloud Logging 참조 (2025-07-21 갱신). https://cloud.google.com/logging/docs/reference/audit/auditlog/rest/Shared.Types/AuditLog
31. Google, "Login Audit Activity Events", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/login
32. Google, "Admin Audit Activity Events - User Settings", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-user-settings
33. Google, "Admin Audit Activity Events - Security Settings", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-security-settings
34. Google, "Login Audit Activity Report", Admin SDK Reports API 안내 (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/guides/manage-audit-login
35. Google, "Token Audit Activity Events", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/token
36. Google, "Data retention and lag times", Google Workspace Admin Help (2026-09-25 갱신). https://support.google.com/a/answer/7061566
37. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
38. Okta, "Event types"(okta-event-types.csv). https://developer.okta.com/docs/okta-event-types.csv
39. Slack, "team.accessLogs". https://api.slack.com/methods/team.accessLogs
40. Slack, "Audit Logs API actions". https://api.slack.com/admins/audit-logs-call
41. Uk Hur, Soojin Kang, Giyoon Kim, Jongsung Kim, "A study on cloud data access through browser credential migration in Windows environment", Forensic Science International: Digital Investigation 45 (2023) 301568 (DFRWS 2023 USA). https://doi.org/10.1016/j.fsidi.2023.301568
42. Invictus Incident Response, Microsoft-Extractor-Suite(Get-AzureEntraGraphLogs.ps1). https://github.com/invictus-ir/Microsoft-Extractor-Suite
43. CISA, Untitled Goose Tool(goosey/entra_id_datadumper.py). https://github.com/cisagov/untitledgoosetool/blob/main/goosey/entra_id_datadumper.py
44. T0pCyber, Hawk(Get-HawkUserEntraIDSignInLog.ps1, Get-HawkUserUALSignInLog.ps1). https://github.com/T0pCyber/hawk
45. Microsoft, "signIn resource type", Microsoft Graph v1.0, Microsoft Learn (2025-11-28 갱신). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-1.0
