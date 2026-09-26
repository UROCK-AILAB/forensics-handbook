---
title: "OAuth 앱과 동의"
parent: "기반 · 계정과 인증"
nav_order: 40
---

# OAuth 앱과 동의 (OAuth Apps·Consent)

OAuth 동의 (consent) 는 사용자나 관리자가 앱에 "나(또는 조직) 대신 데이터에 접근해도 된다" 고 허락하는 일이고, 비밀번호를 바꾸거나 다단계 인증을 켜도 그 허락은 사라지지 않으므로 조사에서는 동의를 준 기록과 지금 남아 있는 부여 목록을 함께 봅니다.

## 이 형식을 쓰는 아티팩트

이 페이지는 파일 형식이 아니라 앱이 사람 대신, 또는 스스로 데이터에 접근할 권리를 얻는 구조를 다룹니다. 동의 한 건은 두 곳에 흔적을 남깁니다. 하나는 동의가 일어난 순간을 적은 감사 로그이고, 다른 하나는 디렉터리에 지금 남아 있는 부여 객체입니다. 감사 로그는 보관 기간이 지나면 사라지고 부여 객체는 취소하면 사라지므로, 둘 중 하나만 보면 과거에 줬다가 거둔 권한이나 보관 기간 전에 준 권한을 놓칩니다.

| 서비스 | 동의·부여를 남기는 기록 | 지금 부여 상태를 보는 곳 | 자세히 |
|---|---|---|---|
| Microsoft 365·Entra ID | Entra 감사 로그 `ApplicationManagement` 범주, 통합 감사 로그 `AzureActiveDirectory` 레코드 | 서비스 주체의 위임 권한 부여(oauth2PermissionGrants)와 앱 역할 할당(appRoleAssignments) | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md) |
| Google Workspace | 토큰 감사(`token`), 관리 감사의 앱 접근·API 클라이언트 접근 이벤트 | Directory API `tokens` 자원, 관리 콘솔 API 제어 화면 | [OAuth 토큰 기록](../../02-artifacts/google-workspace/token-audit.md), [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md) |
| Okta | 시스템 로그 `app.oauth2.as.consent.*` 이벤트 | Okta 관리 화면 | [Okta 시스템 로그](../../02-artifacts/saas/okta.md) |
| Slack | 감사 로그 `app_*` 동작 | 워크스페이스 앱 관리 화면 | [Slack 감사 로그](../../02-artifacts/saas/slack.md) |
| GitHub | 감사 로그 `oauth_application`·`oauth_app_access_*` 이벤트 | 조직·엔터프라이즈 설정 | [GitHub 감사 로그](../../02-artifacts/saas/github.md) |

AWS 와 Google Cloud 에서 다른 주체에 권한을 넘기는 기록은 역할 넘겨받기·서비스 계정 가장으로 남고, 이 페이지가 아니라 [토큰과 세션](tokens-sessions.md)·[페더레이션과 SSO](federation-sso.md)에서 다룹니다. 앱과 서비스 주체가 신원으로서 어떤 식별자를 쓰는지는 [클라우드 계정과 역할](users-roles.md)에 있습니다.

## 구조

### 위임 권한과 애플리케이션 권한

Microsoft ID 플랫폼의 권한은 두 종류입니다. 위임 권한 (delegated permission) 은 로그인한 사용자가 있는 앱이 그 사용자를 대신해 쓰는 권한이고, 사용자나 관리자가 동의할 수 있습니다[4]. 애플리케이션 권한 (application permission, 앱 역할) 은 백그라운드 서비스처럼 로그인한 사용자 없이 도는 앱이 쓰는 권한이고, 관리자만 동의할 수 있습니다[4]. 동의 화면에서 애플리케이션 권한의 설명은 대개 "without a signed-in user" 로, 위임 권한의 설명은 "on behalf of the signed-in user" 로 끝납니다[3].

위임 권한 부여에는 동의 종류 (consent type) 가 붙습니다. `Principal` 은 사용자 한 명이 자기 데이터에 대해 준 동의이고, `AllPrincipals` 는 관리자가 테넌트 전체를 대신해 준 동의입니다[4][2]. 사용자가 앱에 처음 로그인할 때 그 권한에 대한 이전 동의 기록이 없으면 동의 화면이 뜨고, 동의하면 기록이 남아 같은 앱에 다시 로그인할 때는 대개 묻지 않습니다[1].

### 동의를 누가 줄 수 있나

사용자 동의 허용 범위는 관리자가 고르고, 기본 제공 선택지는 세 가지입니다[1][5].

| 설정 | 사용자가 할 수 있는 일 | 기본 제공 정책 ID |
|---|---|---|
| 사용자 동의 끄기 | 새 앱·새 권한에 동의할 수 없고, 이미 동의한 앱에는 계속 로그인 | 해당 없음 |
| 확인된 게시자와 자기 테넌트 앱만, 고른 권한만 | 확인된 게시자 (verified publisher) 앱과 자기 테넌트에 등록된 앱에, 영향이 낮다고 분류한 권한만 동의 | `microsoft-user-default-low` |
| 모든 앱 허용 | 관리자 동의가 필요 없는 모든 권한에, 모든 앱에 대해 동의 | `microsoft-user-default-legacy` |

2026년 9월 문서 기준으로 기본값은 "관리자 동의가 필요 없는 권한에는 모든 사용자가 동의할 수 있다" 입니다[4][5]. 테넌트의 현재 설정은 `GET https://graph.microsoft.com/v1.0/policies/authorizationPolicy/authorizationPolicy` 의 `permissionGrantPolicyIdsAssignedToDefaultUserRole` 값(`managePermissionGrantsForSelf.{consent-policy-id}` 모양)과 `GET https://graph.microsoft.com/v1.0/policies/permissionGrantPolicies` 로 확인합니다[5]. 이 설정을 바꾸면 Entra 감사 로그에 `Update authorization policy`, 권한 부여 정책을 바꾸면 `Add permission grant policy`·`Update permission grant policy`·`Delete permission grant policy` 가 남습니다[8].

테넌트 전체 관리자 동의를 줄 수 있는 역할은 출처마다 다르게 적혀 있습니다. 관리자 동의 문서는 모든 권한을 줄 수 있는 Privileged Role Administrator 와, Microsoft Graph 앱 역할을 뺀 권한을 줄 수 있는 Cloud Application Administrator·AI Administrator·Application Administrator, 그리고 동의 권한이 든 사용자 지정 역할을 듭니다[2]. 동의 사고 대응 플레이북은 Application Administrator 와 Cloud Application Administrator 두 가지만 듭니다[4]. 역할 이름으로 "동의를 줄 수 있었던 사람" 을 가릴 때는 앞의 넓은 목록을 기준으로 삼는 편이 빠뜨림이 적습니다. 관리자 동의 워크플로 (admin consent workflow) 를 켜 두면 사용자는 "Approval required" 화면에서 사유를 적어 승인을 요청하고, 같은 요청을 여러 번 보내도 첫 요청만 관리자에게 갑니다[1].

### 앱 객체에서 조사에 쓰는 속성

앱 등록의 매니페스트 (manifest) 에는 조사에 쓰는 속성이 몇 개 있습니다[10].

| 속성 | 뜻 |
|---|---|
| `appId` | Microsoft Entra ID 가 앱에 매긴 고유 식별자 |
| `signInAudience` | `AzureADMyOrg`(단일 테넌트), `AzureADMultipleOrgs`(다중 테넌트), `AzureADandPersonalMicrosoftAccount`, `PersonalMicrosoftAccount` |
| `requiredResourceAccess` | 앱이 요청하는 권한 목록 |
| `keyCredentials` | 인증서 자격 증명. `keyId`·`type`(예 `AsymmetricX509Cert`)·`startDateTime`·`endDateTime` |
| `passwordCredentials` | 클라이언트 비밀. `displayName`·`hint`·`keyId`·`startDateTime`·`endDateTime` |
| `replyUrlsWithType` | 인증 뒤 돌려보낼 주소 |
| `publisherDomain` | 게시자로 확인된 도메인(읽기 전용) |

동의 결과는 액세스 토큰에도 실립니다. 사용자 토큰의 `scp` 는 동의받은 범위를 공백으로 구분한 목록이고, 클라이언트 자격 증명 흐름으로 받은 앱 토큰은 `roles` 에 권한이 들어갑니다[11]. 토큰을 쓴 클라이언트는 v1.0 토큰의 `appid`, v2.0 토큰의 `azp` 에 적히고, 클라이언트가 인증한 방식은 `azpacr`(v1.0 은 `appidacr`)가 0 이면 공개 클라이언트, 1 이면 클라이언트 비밀, 2 이면 인증서입니다[11]. 토큰 수명과 로그인 로그에서 토큰을 잇는 법은 [토큰과 세션](tokens-sessions.md)에서 다룹니다.

### Microsoft 기록의 작업 이름

Entra 감사 로그의 `ApplicationManagement` 범주에 동의·앱 관련 작업이 모입니다[8].

| 무엇이 일어났나 | 작업 이름 |
|---|---|
| 동의 | `Consent to application` |
| 위임 권한 부여·취소 | `Add delegated permission grant`, `Remove delegated permission grant` |
| 애플리케이션 권한 부여·취소 | `Add app role assignment to service principal`, `Remove app role assignment from service principal` |
| 앱·서비스 주체 생성 | `Add application`, `Add service principal` |
| 자격 증명 추가·삭제 | `Update application - Certificates and secrets management`, `Add service principal credentials`, `Remove service principal credentials` |
| 소유자 추가 | `Add owner to application`, `Add owner to service principal` |
| 동의 복원, 게시자 확인 | `Restore consent`, `Set verified publisher`, `Unset verified publisher` |

그룹 범위 동의는 `GroupManagement` 범주의 `Grant contextual consent to application` 으로 남습니다[8]. 통합 감사 로그의 앱 관리 작업은 이름 끝에 마침표가 붙습니다. 예를 들어 `Add service principal credentials.`, `Add service principal.`, `Add delegation entry.` 처럼 적히고[9], Hawk 는 `-RecordType 'AzureActiveDirectory' -Operations 'Add OAuth2PermissionGrant.','Consent to application.'` 조건으로 동의 기록을 찾습니다[27].

### Google Workspace

토큰 감사(`applicationName=token`)에는 다섯 가지 이벤트가 있습니다[14]. `authorize` 는 사용자가 앱에 자기 데이터 접근을 허락한 기록이고 설명 문구는 `{actor} authorized access to {app_name} for {scope} scopes` 입니다. `revoke` 는 허락을 거둔 기록, `deny` 는 거부된 요청(`rejection_type` 에 사유), `request` 는 접근 요청(`requester_email`·`app_request_info`), `activity` 는 앱이 사용자 대신 API 를 부른 기록(`{app_name} called {method_name} on behalf of {actor}`)입니다[14]. 매개변수에는 `app_name`·`client_id`·`client_type`(`WEB`·`NATIVE_DESKTOP`·`NATIVE_ANDROID` 등)·`scope`·`api_name`·`method_name`·`num_response_bytes`·`product_bucket`(`GMAIL`·`DRIVE`·`GSUITE_ADMIN` 등)이 있습니다[14].

사용자별로 지금 유효한 토큰은 Directory API 의 `tokens` 자원(`kind` 값 `admin#directory#token`)이 돌려주고, `clientId`·`scopes`·`displayText`·`userKey` 와 함께 Google 에 등록되지 않은 익명 클라이언트 ID 면 참인 `anonymous`, 설치형 앱이면 참인 `nativeApp` 이 들어 있습니다[15].

관리자가 앱 접근을 다룬 기록은 관리 감사에 남습니다. 앱을 신뢰·제한·차단 목록에 넣고 빼면 `ADD_TO_TRUSTED_OAUTH2_APPS`·`ADD_TO_LIMITED_OAUTH2_APPS`·`ADD_TO_BLOCKED_OAUTH2_APPS`·`REMOVE_FROM_TRUSTED_OAUTH2_APPS`·`REMOVE_FROM_BLOCKED_OAUTH2_APPS` 가, 자기 도메인 소유 앱을 한꺼번에 신뢰하거나 거두면 `TRUST_DOMAIN_OWNED_OAUTH2_APPS`·`UNTRUST_DOMAIN_OWNED_OAUTH2_APPS` 가, 서비스 단위로 막거나 풀면 `ALLOW_SERVICE_FOR_OAUTH2_ACCESS`·`DISALLOW_SERVICE_FOR_OAUTH2_ACCESS`·`BLOCK_ALL_THIRD_PARTY_API_ACCESS`·`UNBLOCK_ALL_THIRD_PARTY_API_ACCESS` 가 남습니다[17]. API 클라이언트에 조직 데이터 접근 범위를 허용하면 `AUTHORIZE_API_CLIENT_ACCESS`(매개변수 `API_CLIENT_NAME`·`API_SCOPES`), 거두면 `REMOVE_API_CLIENT_ACCESS` 가 남습니다[18]. 관리자가 사용자의 3자 OAuth 토큰을 앱 단위로 취소하면 `REVOKE_3LO_TOKEN`, 기기 단위로 취소하면 `REVOKE_3LO_DEVICE_TOKENS` 가 남습니다[19].

### Okta·Slack

Okta 는 사용자가 앱에 동의하면 `app.oauth2.as.consent.grant`, 동의를 거두면 `app.oauth2.as.consent.revoke` 와 그 하위 이벤트, 토큰 취소 요청은 `app.oauth2.as.token.revoke` 를 남깁니다[23]. Slack 은 앱 설치 `app_installed`(꺼 둔 사용자 지정 통합을 다시 켤 때도), 관리자 승인 앱 기능이 켜진 곳에서 승인됐지만 아직 설치 전인 `app_approved`, OAuth 범위가 늘어난 `app_scopes_expanded`, 제거 `app_uninstalled`, 설치 금지 `app_restricted`, 대개 앱 소유자·설치자가 조직에서 빠졌을 때 토큰을 취소하지 않고 남긴 `app_token_preserved` 를 기록합니다[24].

## 읽는 법

Entra 감사 로그에서 동의 한 건을 읽을 때는 작업 이름, 동의한 계정, 대상 앱, 그리고 사용자 동의인지 관리자 동의인지를 차례로 봅니다. `Consent to application` 레코드의 `ConsentContext.IsAdminConsent` 가 `false` 면 사용자 동의이고[7][25], `True` 면 전역 관리자급 권한을 가진 사람이 넓은 접근을 줬을 수 있으니 권한 범위를 먼저 확인합니다[6]. 위임 권한 부여는 `Add delegated permission grant` 의 `DelegatedPermissionGrant.Scope`(준 권한)와 `DelegatedPermissionGrant.ConsentType`(`AllPrincipals` 이면 모든 사용자 대신)으로, 애플리케이션 권한 부여는 `Add app role assignment to service principal` 의 대상 API(예 Microsoft Graph)와 `AppRole.Value` 로 읽습니다[7].

기존 앱에 자격 증명을 더한 일은 `Update application - Certificates and secrets management` 와 `Update Service principal/Update Application` 으로 찾고, 앱과 서비스 주체 변경이 감사 로그에 두 줄로 남는다는 점을 감안해 셉니다[7][25]. 리디렉션 주소를 바꾼 일은 `Update Application` 작업에서 `AppAddress` 속성 변경으로 보입니다[7].

위험 기반 상향 동의 (risk-based step-up consent) 가 켜져 있으면 위험한 앱에 대한 사용자 동의가 막히고 관리자 동의로 넘어갑니다. 이때 사용자 화면에는 `AADSTS90094` 오류가 뜨고, 감사 로그에는 범주 `ApplicationManagement`, 작업 `Consent to application` 레코드가 상태 사유 "Risky application detected" 로 남습니다[4]. 탐지 규칙은 같은 차단을 실패 사유 `Microsoft.online.Security.userConsentBlockedForRiskyAppsExceptions` 로 찾습니다[25]. 두 표기가 다르므로 검색할 때 둘 다 넣습니다.

동의로 얻은 권한을 실제로 썼는지는 동의 기록이 아니라 사용 기록으로 판단합니다. Microsoft Graph 활동 로그는 요청마다 `AppId`·`Scopes`·`Roles`·`ClientAuthMethod` 를 남기지만, Entra ID P1·P2 라이선스가 있어야 하고 Azure Monitor 진단 설정으로 보낼 곳을 정해 두지 않으면 보관되지 않습니다[12][13]. Google Workspace 는 토큰 감사의 `activity` 이벤트와, 다른 애플리케이션 감사 레코드의 `actor.applicationInfo.oauthClientId`·`applicationName`·`impersonation`(사용자를 가장했는지)으로 앱이 한 일을 봅니다[14][22].

다음은 문서의 설명 문구 틀로 만든 예시입니다(사용자·앱 이름은 지어낸 값).

```text
user@example.com authorized access to Example Mail Helper for https://mail.google.com/ scopes
Example Mail Helper called messages.list on behalf of user@example.com
```

첫 줄은 동의가 있었다는 것만 알려 주고, 둘째 줄이 있어야 앱이 그 범위로 API 를 불렀다고 말할 수 있습니다.

## 포렌식에서 중요한 점

### 증명하는 것

감사 기록은 어느 계정이 언제 어떤 앱(`appId`·`client_id`)에 어떤 범위를 허락했는지, 그리고 그 허락이 사용자 한 명 몫(`Principal`)인지 테넌트 전체 몫(`AllPrincipals`)인지를 보여 줍니다. Graph 활동 로그, Workspace 토큰 감사 `activity` 처럼 앱이 그 권한으로 부른 기록이 함께 있으면 실제로 사용했다는 것까지 말할 수 있습니다.

### 증명하지 못하는 것

동의 기록만으로 데이터를 가져갔다고 볼 수는 없습니다. 현재 부여 목록은 지금 상태라서 과거에 줬다가 거둔 권한은 감사 로그로만 보이고, 감사 기능이 꺼져 있던 기간이나 보관 기간 밖의 일은 확인할 수 없습니다[6][4]. 메일함 감사와 관리자·사용자 활동 감사가 공격 전에 켜져 있어야 앱이 접근한 범위를 따질 수 있습니다[6]. Graph 활동 로그는 자기 테넌트에 들어온 요청만 모으므로, 다중 테넌트 앱이 다른 테넌트에서 한 일은 볼 수 없습니다[12].

### 시각

Entra 감사 로그의 시각과 보관 기간은 [클라우드 로그의 시각](../logging/timestamps.md)과 [보관 기간과 라이선스](../logging/retention-licensing.md)에 정리되어 있고, 2026년 9월 문서 기준 감사 로그 보관은 Entra ID Free 7일, P1·P2 30일입니다[13]. 통합 감사 로그 검색에는 일이 일어난 뒤 30분에서 24시간이 지나야 레코드가 보입니다[6]. Azure 포털 화면은 관리자 동의를 지난 90일 치만 보여 주므로, 그보다 오래된 동의는 PowerShell 이나 Graph 로 부여 목록을 뽑아 확인합니다[4].

앱 자격 증명의 `startDateTime`·`endDateTime` 은 `2022-10-19T17:59:59.6521653Z` 처럼 UTC ISO 8601 로 적히고[10], 자격 증명을 추가한 시각은 감사 로그의 자격 증명 추가 작업 시각으로 확인합니다[7].

Google Workspace 토큰 로그는 두어 시간, OAuth 로그는 몇 시간까지 늦게 들어오고 보관은 6개월입니다[20]. 보고서 API 의 토큰 보고서가 돌려주는 기간은 최대 180일입니다[21]. 관리 콘솔의 "Accessed apps" 목록은 토큰을 주거나 거둔 뒤 48시간이 지나야 바뀌고, 새로 승인한 앱의 상세는 24~48시간 뒤에 보입니다[16].

## 함정

- **비밀번호 재설정으로 끝나지 않습니다.** 동의받은 앱은 조직 밖에 있으므로 비밀번호를 바꾸거나 다단계 인증을 요구해도 그 앱의 접근은 막히지 않습니다[6]. 계정 복구 시각 뒤에도 앱의 사용 기록이 이어질 수 있습니다.
- **앱이 사라진 것과 접근이 끝난 것은 다릅니다.** 앱을 지우면 다른 사용자가 다시 동의해 돌아올 수 있어 대응 지침은 비활성화를 권하고, 비활성화된 앱은 새 토큰을 받지 못합니다[4]. 동의 취소는 감사 로그에 `Remove delegated permission grant`·`Remove app role assignment from service principal` 로 남습니다[6][8].
- **이름은 흉내 낼 수 있습니다.** 유명 제품 이름을 쓰는 앱이 있으므로[4] 표시 이름 대신 `appId`, 앱 소유 조직(`AppOwnerOrganizationId`)[26], 확인된 게시자 여부[4]로 구분합니다.
- **Entra 와 통합 감사 로그의 작업 이름이 다릅니다.** 통합 감사 로그 쪽에는 끝에 마침표가 붙어 `Consent to application.` 처럼 적힙니다[8][27]. 문자열이 정확히 같아야 걸리는 검색은 둘을 따로 씁니다.
- **문서 속 오타.** Microsoft 의 동의 조사 문서 두 곳에 `AllPrinciples` 로 적힌 문장이 있지만 실제 값은 `AllPrincipals` 입니다[6][4].
- **위험 권한 목록은 기준마다 다릅니다.** Microsoft 플레이북은 Mail.*(Mail.ReadBasic* 제외)·Contacts.*·MailboxSettings.*·People.*·Files.*·Notes.*·Directory.AccessAsUser.All·User_Impersonation 을 먼저 보라고 하고, Microsoft 사고 대응팀이 관찰한 동의 피싱의 99% 는 앞의 여섯 가지 조합을 썼습니다[4]. Hawk 는 AppRoleAssignment.ReadWrite.All·RoleManagement.ReadWrite.Directory 를 가장 위험한 권한으로, Mail.ReadWrite·Mail.Send·Files.*·Sites.*·User.* 등을 높은 위험으로, `AllPrincipals` 이거나 권한 이름에 "all" 이 든 부여를 넓은 범위로 분류합니다[27]. 도구가 붙인 위험 등급은 도구의 기준이라는 점을 보고서에 밝힙니다.
- **Workspace 설정 변경이 토큰 취소를 부릅니다.** 서비스 접근을 Restricted 로 바꾸면 신뢰하지 않은 기존 앱이 멈추고 토큰이 취소됩니다[16]. 한꺼번에 몰린 `revoke` 가 사용자의 행동이 아닐 수 있으니 같은 시각대의 관리 감사 기록을 봅니다.
- **수집 도구도 OAuth 범위 안에서만 읽습니다.** 공개 API 로 클라우드 데이터를 모으는 도구는 OAuth 2.0 으로 인증하고 서비스 회사가 정한 범위까지만 접근합니다[30]. 도구 결과에 없는 항목은 범위 밖이었을 수 있습니다.

## 도구

현재 부여 목록은 Microsoft 365 수집 도구로 뽑습니다. 도구마다 받는 범위가 조금씩 다르고, 수집 절차는 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md)에서 다룹니다.

| 도구 | 받는 것 | 참고 |
|---|---|---|
| Microsoft-Extractor-Suite `Get-OAuthPermissionsGraph` | `Get-MgOauth2PermissionGrant -All` 로 위임 권한, `Get-MgServicePrincipalAppRoleAssignment` 로 애플리케이션 권한을 받아 `PermissionType`·`AppId`·`Permission`·`ConsentType`·`PrincipalDisplayName`·`PublisherName`·`VerifiedPublisherId`·`CreatedDateTime` 등의 열로 씁니다. 앱 소유 조직 ID 가 `f8cdef31-a31e-4b4a-93e4-5f571e91255a` 나 `72f988bf-86f1-41af-91ab-2d7cd011db47` 이면 Microsoft 앱으로 표시합니다 | [26] |
| Hawk | `Get-HawkTenantConsentGrant` 가 현재 부여를 Consent_Grants.csv 로, `Get-HawkTenantEntraIDAppAuditLog` 가 통합 감사 로그의 동의 기록을 Entra_ID_Application_Audit.csv 로, `Get-HawkTenantAppAndSPNCredentialDetail` 이 앱·서비스 주체 자격 증명을 씁니다 | [27] |
| DFIR-O365RC `Get-AADApps` | 앱·서비스 주체와 함께 지운 앱·서비스 주체도 받고, 서비스 주체마다 oauth2PermissionGrants·appRoleAssignments 를 붙입니다 | [28] |
| Untitled Goose Tool | 서비스 주체별 appRoleAssignments·appRoleAssignedTo·owners·oauth2PermissionGrants·delegatedPermissionClassifications 등을 받습니다 | [29] |

Google Workspace 는 보고서 API 의 `token` 애플리케이션과 Directory API `tokens.list` 로 기록과 현재 상태를 받습니다[14][15]. 동의 기록을 찾는 탐지 규칙은 [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md)에서, 악성 앱 동의를 조사하는 순서는 [악성 OAuth 앱에 동의했나](../../04-scenarios/account-compromise/illicit-consent.md)에서 다룹니다.

## 참고 문헌

1. Microsoft, "User and admin consent in Microsoft Entra ID" (ms.date 2025-03-18). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/enterprise-apps/user-admin-consent-overview.md
2. Microsoft, "Grant tenant-wide admin consent to an application" (ms.date 2025-03-25). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/enterprise-apps/grant-admin-consent.md
3. Microsoft, "Manage consent to applications and evaluate consent requests" (ms.date 2025-07-20). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/enterprise-apps/manage-consent-requests.md
4. Microsoft, "App consent grant investigation", Microsoft Learn (2025-03-12 갱신). https://learn.microsoft.com/en-us/security/operations/incident-response-playbook-app-consent
5. Microsoft, "Configure how users consent to applications", Microsoft Learn (2025-06-24 갱신). https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/configure-user-consent
6. Microsoft, "Detect and remediate illicit consent grants", Microsoft Learn (2026-07-03 갱신). https://learn.microsoft.com/en-us/defender-office-365/detect-and-remediate-illicit-consent-grants
7. Microsoft, "Microsoft Entra security operations guide for applications", Microsoft Learn (2023-10-23 갱신). https://learn.microsoft.com/en-us/entra/architecture/security-operations-applications
8. Microsoft, "Microsoft Entra audit log activity reference" (ms.date 2025-03-25). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
9. Microsoft, "Audit log activities", Microsoft Purview, Microsoft Learn (2026-09-08 갱신). https://learn.microsoft.com/en-us/purview/audit-log-activities
10. Microsoft, "Microsoft Entra app manifest" (ms.date 2025-04-15). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity-platform/reference-app-manifest.md
11. Microsoft, "Access token claims reference", Microsoft Learn (2026-06-25 갱신). https://learn.microsoft.com/en-us/entra/identity-platform/access-token-claims-reference
12. Microsoft, "Access Microsoft Graph activity logs", Microsoft Learn (2026-07-04 갱신). https://learn.microsoft.com/en-us/graph/microsoft-graph-activity-logs-overview
13. Microsoft, "Microsoft Entra data retention" (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
14. Google, "OAuth Token Audit Activity Events", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/token
15. Google, "REST Resource: tokens", Admin SDK Directory API (2025-03-25 갱신). https://developers.google.com/workspace/admin/directory/reference/rest/v1/tokens
16. Google, "Control which third-party & internal apps access Google Workspace data" (2026-09-18 갱신). https://knowledge.workspace.google.com/admin/apps/control-which-third-party-and-internal-apps-access-google-workspace-data
17. Google, "Admin Security Settings Activity Events", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-security-settings
18. Google, "Admin Domain Settings Activity Events", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-domain-settings
19. Google, "Admin User Settings Activity Events", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-user-settings
20. Google, "Data retention and lag times", Google Workspace Admin Help (2026-09-25 갱신). https://support.google.com/a/answer/7061566
21. Google, "OAuth Token audit activity reports", Admin SDK Reports API 안내 (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/guides/manage-audit-tokens
22. Google, "Method: activities.list", Admin SDK Reports API (2026-09-09 갱신). https://developers.google.com/workspace/admin/reports/v1/reference/activities/list
23. Okta, "Event types" 목록(okta-event-types.csv). https://developer.okta.com/docs/okta-event-types.csv
24. Slack, "Audit Logs API: actions". https://api.slack.com/admins/audit-logs-call
25. SigmaHQ, Azure 감사 로그 규칙(azure_app_end_user_consent.yml, azure_app_end_user_consent_blocked.yml, azure_app_credential_added.yml). https://github.com/SigmaHQ/sigma/tree/master/rules/cloud/azure/audit_logs
26. Invictus Incident Response, Microsoft-Extractor-Suite(Scripts/Get-OAuthPermissions.ps1). https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-OAuthPermissions.ps1
27. T0pCyber, Hawk(Get-HawkTenantConsentGrant.ps1, Get-HawkTenantEntraIDAppAuditLog.ps1, Get-HawkTenantAppAndSPNCredentialDetail.ps1). https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Get-HawkTenantConsentGrant.ps1
28. ANSSI, DFIR-O365RC(Get-AADApps.ps1). https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/Get-AADApps.ps1
29. CISA, Untitled Goose Tool(goosey/entra_id_datadumper.py). https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/entra_id_datadumper.py
30. Jihyeok Yang, Jieon Kim, Jewan Bang, Sangjin Lee, Jungheum Park, "CATCH: Cloud Data Acquisition through Comprehensive and Hybrid Approaches", Forensic Science International: Digital Investigation 43 (2022) 301442. https://doi.org/10.1016/j.fsidi.2022.301442
