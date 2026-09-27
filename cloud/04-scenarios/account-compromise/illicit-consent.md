---
title: "악성 OAuth 앱에 동의했나"
parent: "시나리오 · 계정 침해"
nav_order: 740
---

# 악성 OAuth 앱에 동의했나 (Illicit Consent)

사용자나 관리자가 외부 앱에 메일·파일·디렉터리 권한을 넘겨주는 동의를 했는지, 그 앱이 받은 권한으로 무엇을 했는지를 묻는 조사를 다룹니다. Microsoft 365 에서는 Entra 감사 로그와 통합 감사 로그로 동의 활동을 찾고, 현재 권한 목록과 앱 정보를 받은 뒤 Graph 활동 로그와 메일함·파일 활동 기록으로 앱이 부른 요청을 봅니다. Google Workspace 는 토큰 로그와 관리 콘솔 감사 로그에서, Okta 는 System Log 에서 동의와 철회 기록을 찾습니다.

## 조사 질문

사용자나 관리자가 외부 앱에 메일·파일·디렉터리 권한을 넘겨주는 동의를 했는지, 했다면 언제 누가 어떤 권한을 줬는지, 그 앱이 그 권한으로 실제 무엇을 읽거나 바꿨는지를 묻습니다. 이 시나리오에서는 공격자가 사용자 비밀번호를 몰라도 되고, 앱은 동의로 받은 토큰으로 사용자를 대신해 API 를 부릅니다[2]. 그래서 로그인 기록보다 **동의 기록**과 **앱이 부른 API 기록**이 조사의 중심이 됩니다.

OAuth 동의 (OAuth consent), 위임 권한 (delegated permission), 응용 프로그램 권한 (application permission) 같은 기본 개념은 [OAuth 앱과 동의](../../01-foundations/identity/oauth-consent.md)에서 다룹니다.

## 먼저 확인할 것

**어느 서비스인지와 라이선스.** 동의 기록이 남는 곳과 보관 기간이 서비스·요금제마다 다릅니다. 아래 표는 이 시나리오에 쓰는 기록만 모은 것이고, 전체 표는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에 있습니다.

| 서비스 | 동의 기록 | 보관 | 앱이 한 일의 기록 |
|---|---|---|---|
| Microsoft Entra ID | 감사 로그 (audit log) | Free 7일, P1·P2 30일[4] (2026년 1월 문서 기준) | Microsoft Graph 활동 로그 — P1·P2 에서만, 진단 설정으로 내보내야 남음[4][7] |
| Microsoft 365 통합 감사 로그 | RecordType `AzureActiveDirectory` 레코드 | Audit (Standard) 180일(2023-10-17 이후 생성분, 그 전 생성분 90일), Audit (Premium) 기본 정책은 E5 등 사용자의 Entra·Exchange·SharePoint·OneDrive 기록 1년[5] (2026년 6월 문서 기준) | 메일함·파일 활동 레코드의 `AppAccessContext`[8] |
| Google Workspace | 토큰 로그 (`applicationName=token`) | OAuth 토큰 로그 6개월[25] | 같은 토큰 로그의 `activity` 이벤트 — Enterprise Plus·Education Plus·Enterprise Standard·Education Standard·Cloud Identity Premium 에서만[24] |
| Okta | System Log | 90일 넘은 기록은 조회되지 않음[31] | 앱이 부른 리소스 쪽 로그 |

Entra ID 를 Free 에서 P1 으로 올려도 이미 지난 기록은 돌아오지 않고, 올린 시점에 남아 있던 최대 7일치만 보입니다[4]. Free 테넌트에서 동의가 일주일보다 오래전이면 Entra 감사 로그보다 통합 감사 로그에서 찾을 가능성이 높습니다.

**사건 전에 감사가 켜져 있었는지.** 앱이 메일함에서 무엇을 했는지 보려면 공격 전에 메일함 감사와 관리자·사용자 활동 감사가 켜져 있어야 합니다[3][2]. Graph 활동 로그는 진단 설정에서 로그 범주를 켠 뒤부터 모읍니다[4].

**사건 당시 동의 설정.** Entra ID 의 사용자 동의 설정에서 기본으로 고를 수 있는 것은 "사용자 동의 끄기", "확인된 게시자 (verified publisher) 와 자기 조직 앱에 한해 저영향으로 분류한 권한만 허용", "관리자 동의가 필요 없는 권한이면 모든 앱에 동의 허용" 세 가지이고, 사용자 지정 앱 동의 정책을 만들어 쓸 수도 있습니다[10]. Entra 감사 로그의 Core Directory 서비스에는 AuthorizationPolicy 범주의 `Update authorization policy` 활동이 있으므로[1], 사건 전후에 이 활동이 있었는지, 그 변경 내용에 동의 설정이 들어 있는지를 실제 로그로 확인합니다. 설정이 느슨했으면 일반 사용자 혼자 동의할 수 있었고, 조였으면 관리자 계정이 동의했을 가능성을 먼저 봅니다. 관리자 동의는 Application Administrator, Cloud Application Administrator 역할도 할 수 있습니다[2].

**시각의 기준.** Purview 감사 검색 화면의 날짜 범위와 결과의 "Date (UTC)" 는 UTC 로 나옵니다[6]. Google 관리 콘솔의 OAuth 로그 이벤트 화면은 브라우저의 기본 시간대로 날짜를 보여 주므로[24], 같은 기록도 API 로 받은 값과 화면 값이 다르게 보일 수 있습니다. 자세한 내용은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 있습니다.

**기록이 들어오는 데 걸리는 시간.** 동의 기록이 감사 검색 결과에 나오기까지 30분에서 24시간이 걸릴 수 있습니다[2][3]. 감사 검색 문서는 핵심 서비스 기록이 보통 60~90분 뒤에 나오고 다른 서비스는 더 늦을 수 있으며 보장 시간은 없다고 설명합니다[6]. 두 문서의 값이 다르므로, 사건 직후 검색에서 결과가 없어도 하루는 지나서 다시 검색합니다. Google Workspace 의 OAuth 로그는 최대 몇 시간, 토큰 로그는 두어 시간 늦을 수 있습니다[25].

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | Entra 감사 로그 (Core Directory, 범주 ApplicationManagement) | 동의·권한 부여·서비스 주체 생성·자격 증명 추가의 시각과 행위자 | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md) |
| 2 | 통합 감사 로그 (RecordType `AzureActiveDirectory`) | 같은 동의 활동을 Entra 보관 기간보다 오래 | [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md) |
| 3 | 현재 권한 목록 (oauth2PermissionGrant·appRoleAssignment) | 지금 남아 있는 권한, 동의 범위, 앱 게시자·리디렉션 주소 | [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md) |
| 4 | Microsoft Graph 활동 로그 | 앱이 부른 Graph 요청, 쓴 권한, 요청 IP | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md) |
| 5 | 통합 감사 로그의 메일함·파일 활동 | 어느 앱이 메일·파일에 접근했는지(`AppAccessContext`) | [Exchange Online](../../02-artifacts/m365/exchange-online/index.md) |
| 6 | Google Workspace 토큰 로그 | 동의(`authorize`), API 호출(`activity`), 거부·철회 | [OAuth 토큰 기록](../../02-artifacts/google-workspace/token-audit.md) |
| 7 | Google Workspace 관리 콘솔 감사 로그 | 도메인 전체 위임, 앱 신뢰·차단 목록 변경 | [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md) |
| 8 | Okta System Log | 사용자·관리자 동의, OAuth 클라이언트 생성, 클라이언트 비밀 추가 | [Okta 시스템 로그](../../02-artifacts/saas/okta.md) |

## 분석 흐름

### Microsoft 365·Entra ID

1. **동의 활동을 찾습니다.** Entra 감사 로그의 Core Directory 서비스, 범주 ApplicationManagement 에서 아래 활동을 모읍니다[1].

   | 활동 이름 | 뜻 |
   |---|---|
   | `Consent to application` | 사용자나 관리자가 앱에 동의함 |
   | `Add delegated permission grant` | 위임 권한 부여 |
   | `Add app role assignment to service principal` | 응용 프로그램 권한(앱 역할) 부여 |
   | `Add service principal` | 테넌트에 앱의 서비스 주체가 생김 |
   | `Add service principal credentials`, `Update application - Certificates and secrets management` | 앱에 비밀·인증서가 추가됨 |
   | `Add owner to application`, `Add owner to service principal` | 앱 소유자 추가 |
   | `Remove delegated permission grant`, `Remove app role assignment from service principal` | 권한 회수 |
   | `Restore consent`, `Set verified publisher`, `Update service principal` | 동의 복원, 게시자 확인 설정, 서비스 주체 변경 |

   같은 Core Directory 서비스의 GroupManagement 범주에 있는 `Grant contextual consent to application` 도 함께 봅니다[1]. Sigma 규칙은 위임 권한 부여와 앱 역할 부여를 `properties.message` 필드로, 서비스 주체 생성을 `operationName` 필드로 찾습니다[18][19][21].

2. **통합 감사 로그에서 같은 활동을 찾습니다.** 통합 감사 로그에서는 작업 이름 끝에 마침표가 붙고, 위임 권한 부여는 이름도 다릅니다. Hawk 는 `Search-UnifiedAuditLog -RecordType 'AzureActiveDirectory' -Operations 'Add OAuth2PermissionGrant.','Consent to application.'` 로 검색하고, 결과에서 Id, Operation, ResultStatus, Workload, ClientIP, UserID 와 ExtendedProperties 안의 actorUPN, targetName, env_time, correlationId 를 뽑습니다[12]. Entra 감사 로그의 이름(`Add delegated permission grant`)만 넣고 통합 감사 로그를 검색하면 Hawk 가 찾는 `Add OAuth2PermissionGrant.` 레코드를 놓칩니다.

3. **관리자 동의인지 구분합니다.** 동의 레코드의 세부 정보에서 `IsAdminConsent` 가 True 이면 전역 관리자 (Global Administrator) 권한이 있는 누군가가 데이터에 넓은 접근을 허용했을 가능성이 있습니다[3]. Sigma 규칙은 같은 값을 `ConsentContext.IsAdminConsent` 필드로 찾고, `'false'` 이면 일반 사용자 동의로 봅니다[16]. Microsoft 의 앱 동의 대응 문서 한 곳에는 이 이름이 "IsAdminContent" 로 적혀 있는데[2], 다른 문서와 Sigma 규칙은 `IsAdminConsent` 를 씁니다[3][16].

4. **막힌 동의도 봅니다.** 위험 기반 단계 상향 동의 (risk-based step-up consent) 가 위험한 요청을 막으면 사용자는 AADSTS90094(AdminConsentRequired) 메시지를 받고[2][11], 감사 로그에는 Category "ApplicationManagement", Activity Type "Consent to application", Status Reason "Risky application detected" 레코드가 남습니다[2]. Sigma 규칙은 이 경우를 `failure_status_reason: 'Microsoft.online.Security.userConsentBlockedForRiskyAppsExceptions'` 로 찾습니다[17]. 막힌 기록이 있으면 같은 앱이 다른 사용자나 관리자에게서 동의를 받았는지 이어서 찾습니다.

5. **지금 남은 권한을 받습니다.** 위임 권한은 oauth2PermissionGrant 개체이고 `ConsentType` 이 `AllPrincipals` 면 관리자가 조직 전체에, `Principal` 이면 사용자 한 명이 자기 데이터에 대해 동의한 것입니다[2]. 응용 프로그램 권한은 appRoleAssignment 개체이고 관리자만 동의할 수 있습니다[2]. 받는 방법은 도구마다 다릅니다.

   - Microsoft-Extractor-Suite 의 `Get-OAuthPermissions` 는 `Get-MgOauth2PermissionGrant` 와 `Get-MgServicePrincipalAppRoleAssignment` 결과를 한 표로 합치고 ConsentType, Permission, AppDisplayName, PublisherName, ReplyUrls, AppOwnerOrganizationId, VerifiedPublisherId 같은 열을 씁니다[14]. `AppOwnerOrganizationId` 가 `f8cdef31-a31e-4b4a-93e4-5f571e91255a` 또는 `72f988bf-86f1-41af-91ab-2d7cd011db47` 이면 "Microsoft Application" 으로 분류합니다[14].
   - Hawk 의 `Get-HawkTenantConsentGrant` 는 ConsentType 이 `AllPrincipals` 이거나 권한 이름에 "all" 이 들어가면 "Broad-Scope Grant", `AppRoleAssignment.ReadWrite.All`·`RoleManagement.ReadWrite.Directory` 는 "Extremely Dangerous", `Mail.ReadWrite`·`Mail.Send`·`Files.*` 등은 "High Risk" 로 표시하고, 전체는 Consent_Grants, 표시된 것은 _Investigate_Consent_Grants 파일로 씁니다[13].
   - DFIR-O365RC 의 `Get-AADApps` 는 삭제된 응용 프로그램과 서비스 주체까지 JSON 으로 받고, 삭제되지 않은 서비스 주체에만 oauth2PermissionGrant·appRoleAssignment 를 붙입니다[15]. 삭제된 개체에는 `deleted` 값이 true 로 붙습니다[15].

6. **권한이 위험한지 봅니다.** 동의 피싱에 자주 쓰인 위임 권한은 `Mail.*`(`Mail.ReadBasic*` 제외), `Contacts.*`, `MailboxSettings.*`, `People.*`, `Files.*`, `Notes.*`, `Directory.AccessAsUser.All`, `User_Impersonation` 입니다[2]. Microsoft 사고 대응 팀은 동의 피싱의 99% 에서 공격자가 이 가운데 처음 여섯 가지를 조합해 썼다고 밝혔습니다[2]. 영향이 가장 큰 쪽은 위 권한의 응용 프로그램 권한판, `Application.ReadWrite.All`, `Directory.ReadWrite.All`, `RoleManagement.ReadWrite.Directory`, `User.ManageCreds.All` 같은 권한, 쓰기 권한이 있는 그 밖의 응용 프로그램 권한이고, 위험이 가장 낮은 쪽은 `User.Read`, `User.ReadBasic.All`, `openid`, `email`, `profile` 입니다[2]. `offline_access` 는 저위험 권한과만 짝을 이룰 때 저위험으로 봅니다[2].

7. **앱의 정체를 봅니다.** 리디렉션 주소 (ReplyURL) 의 도메인이 새로 등록됐거나 임시 도메인인지, 앱을 등록한 테넌트가 새로 만들어졌거나 침해된 곳인지, 게시자가 확인됐는지를 봅니다[2]. 이름은 흔한 제품처럼 지을 수 있으므로 이름보다 `AppOwnerOrganizationId`·`VerifiedPublisherId` 를 봅니다[2][14].

8. **앱이 한 일을 찾습니다.** Graph 활동 로그는 테넌트가 받은 Microsoft Graph HTTP 요청마다 한 줄이고, `AppId`·`ServicePrincipalId`·`Scopes`·`Roles`·`RequestMethod`·`RequestUri`·`ResponseStatusCode`·`IPAddress`·`ClientAuthMethod` 가 있습니다[7]. `ClientAuthMethod` 는 공개 클라이언트면 0, 클라이언트 비밀이면 1, 인증서면 2 입니다[7]. 동의에서 확인한 앱 ID 로 이 로그를 거르면 앱이 어느 리소스를 언제 불렀는지 나옵니다. 로그인 기록과는 아래처럼 `SignInActivityId` 와 `UniqueTokenIdentifier` 로 잇고, Microsoft 앱의 요청은 짝이 되는 로그인 기록이 없을 수 있습니다[7].

   ```kusto
   MicrosoftGraphActivityLogs
   | where TimeGenerated > ago(7d)
   | join kind=leftouter (union SigninLogs, AADNonInteractiveUserSignInLogs, AADServicePrincipalSignInLogs, AADManagedIdentitySignInLogs, ADFSSignInLogs
    | where TimeGenerated > ago(7d))
    on $left.SignInActivityId == $right.UniqueTokenIdentifier
   ```

   통합 감사 로그에서는 레코드의 `AppAccessContext` 에 `ClientAppId`·`ClientAppName`(사용자를 대신해 접근한 앱), `AADSessionId`, `UniqueTokenId`, `IssuedAtTime`(토큰 인증 시각)이 들어갈 수 있습니다[8]. 이 필드는 모든 레코드에 채워지지는 않습니다[8]. Defender for Cloud Apps 경고 `Suspicious OAuth app file download activities` 도 함께 봅니다[22].

9. **자격 증명 추가를 봅니다.** 동의 뒤에 `Update application - Certificates and secrets management` 나 `Add service principal credentials` 가 있으면 앱에 새 자격 증명이 붙은 것이고[1], 정해진 절차 밖에서 붙인 자격 증명이면 공격자가 그 자격 증명으로 앱을 쓰고 있을 가능성이 있습니다[20]. 이어지는 권한 변화는 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md)의 방법으로 추적합니다.

### Google Workspace

1. 토큰 로그에서 `authorize` 이벤트를 찾습니다. 관리 콘솔 메시지 형식은 `{actor} authorized access to {app_name} for {scope} scopes` 이고 매개변수는 `app_name`, `client_id`, `client_type`, `scope`, `scope_data` 입니다[23]. 거부는 `deny`(`rejection_type` 값 `CAA_FOR_OIDC_BLOCK`, `EDU_UNDERAGE_BLOCK`, `EXPLICIT_ADMIN_BLOCK`, `SCOPE_BLOCK`), 요청은 `request`, 철회는 `revoke` 입니다[23].
2. 같은 `client_id` 의 `activity` 이벤트로 앱이 사용자를 대신해 부른 API 를 봅니다. 메시지 형식은 `{app_name} called {method_name} on behalf of {actor}` 이고 `api_name`, `method_name`, `num_response_bytes` 가 있습니다[23]. 이 이벤트는 위 표의 에디션에서만 남습니다[24]. 토큰 만료처럼 사용자 동작으로 생기지 않은 이벤트에는 IP 가 없을 수 있습니다[24].
3. 관리 콘솔 감사 로그에서 `AUTHORIZE_API_CLIENT_ACCESS`(도메인 전체 위임 부여, 매개변수 `API_CLIENT_NAME`·`API_SCOPES`·`DOMAIN_NAME`)와 `REMOVE_API_CLIENT_ACCESS` 를 찾습니다[26][28]. 앱 신뢰·차단 목록 변경은 `ADD_TO_TRUSTED_OAUTH2_APPS`, `ADD_TO_TRUSTED_BY_OAUTH_SCOPE_OAUTH2_APPS`, `REMOVE_FROM_BLOCKED_OAUTH2_APPS`, `TRUST_DOMAIN_OWNED_OAUTH2_APPS` 같은 이벤트로 남습니다[27]. ALFA 는 `authorize`·`ADD_TO_TRUSTED_OAUTH2_APPS`·`REMOVE_FROM_BLOCKED_OAUTH2_APPS`·`TRUST_DOMAIN_OWNED_OAUTH2_APPS` 를 방어 회피의 대체 인증 수단 사용(application access token)으로 분류하고, `authorize` 는 응용 프로그램 액세스 토큰 탈취 (steal application access token) 에도 넣습니다[29].

### Okta

사용자 동의는 `app.oauth2.as.consent.grant`(사용자 지정 인가 서버)와 `app.oauth2.consent.grant`(조직 인가 서버), 관리자 동의는 `app.oauth2.admin.consent.grant` 로 남습니다[30]. 관리자 동의 철회는 `app.oauth2.admin.consent.revoke`, 사용자 동의 철회는 `app.oauth2.as.consent.revoke` 로 시작하는 이벤트입니다[30]. OAuth 클라이언트 생성은 `app.oauth2.client.lifecycle.create`, 클라이언트 비밀이나 JWK 의 추가·활성화는 `app.oauth2.credentials.lifecycle.create`·`app.oauth2.credentials.lifecycle.activate` 입니다[30].

모든 서비스에서 찾은 동의·API 호출·권한 회수를 한 줄로 늘어놓는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 증명하는 것과 증명하지 못하는 것

`Consent to application` 레코드는 그 시각에 그 사용자나 관리자의 맥락으로 동의가 이뤄졌다는 것을 보여 줍니다. 사용자가 동의 화면에서 무엇을 보고 눌렀는지, 앱을 실제로 누가 운영하는지는 보여 주지 않습니다.

현재 권한 목록은 수집 시점에 남아 있는 권한만 보여 줍니다. 이미 회수했거나 앱을 지운 경우에는 목록에 없으므로 감사 로그의 `Remove delegated permission grant` 같은 활동으로 채우고, 지운 앱이 있었는지는 삭제된 개체까지 받는 `Get-AADApps` 결과로 봅니다[1][15].

권한을 받았다는 사실과 데이터를 읽었다는 사실은 다릅니다. 데이터 접근은 Graph 활동 로그나 통합 감사 로그의 활동 레코드로 따로 보여야 하고, Graph 활동 로그를 사건 전에 켜지 않았으면 앱의 Graph 호출 기록은 없습니다[7][4].

## 흔한 오판

**위임 권한 목록의 날짜를 동의 시각으로 읽기.** `Get-OAuthPermissions` 결과에서 위임 권한 줄의 `CreatedDateTime` 은 앱 서비스 주체의 생성 시각입니다[14]. 응용 프로그램 권한 줄에만 할당 생성 시각인 `CreationTimestamp` 가 있습니다[14]. 위임 권한의 동의 시각은 감사 로그에서 찾습니다.

**Azure 포털 화면만 보고 관리자 동의가 없다고 판단하기.** Azure 포털은 최근 90일 관리자 동의만 보여 줍니다[2].

**비밀번호를 바꿨으니 앱 접근도 끊겼다고 보기.** 기밀 클라이언트 (confidential client) 에게 발급한 새로 고침 토큰은 사용자의 비밀번호 변경, 셀프 서비스 재설정, Azure 포털에서 관리자 재설정을 해도 유효하고, Entra·Microsoft 365 관리 센터에서 관리자가 재설정하거나 새로 고침 토큰을 모두 폐기하면 끊깁니다[9]. 비밀번호 재설정이나 MFA 요구는 이 공격에 효과가 없습니다[3]. 재설정 뒤에도 앱 호출이 이어지면 이 차이로 설명될 가능성이 있습니다. 토큰 수명과 폐기는 [토큰과 세션](../../01-foundations/identity/tokens-sessions.md)에 있습니다.

**앱 이름으로 Microsoft 앱이라고 믿기.** 공격자는 같은 생태계에서 널리 쓰는 제품의 이름을 붙일 수 있습니다[2]. `AppOwnerOrganizationId` 로 판단합니다[14].

**앱이 목록에 없으니 동의도 없었다고 보기.** 앱을 지우면 목록에서 사라지고, 다른 사용자가 다시 동의하면 돌아올 수 있습니다[2]. 그래서 Microsoft 는 대응할 때 삭제보다 비활성화를 권합니다[2]. 목록에 없으면 감사 로그와 삭제된 개체를 봅니다.

**동의가 없어 보이는데 권한이 있는 경우.** 동의가 Entra 감사 로그 보관 기간(Free 7일)보다 오래되면 Entra 쪽에는 기록이 없습니다[4]. 통합 감사 로그에서 찾습니다[5].

## 보고서 문장 예

만든 예시입니다. 사용자·앱 이름·IP 는 지어낸 값입니다.

> 2026-03-02 01:14:07 UTC 에 통합 감사 로그에 사용자 kim@contoso.com 의 `Consent to application.` 레코드가 있고, 대상 앱은 "Doc Viewer"(AppId 00000000-0000-0000-0000-000000000abc) 이며 `IsAdminConsent` 는 False 입니다. 수집 시점(2026-03-05)의 권한 목록에는 이 앱에 대해 kim@contoso.com 한 명에 대한 `Mail.Read`·`offline_access` 위임 권한이 남아 있습니다. 같은 AppId 로 Microsoft Graph 활동 로그를 거르면 2026-03-02 01:20 부터 03-04 22:41 UTC 까지 203.0.113.25 에서 `/me/messages` 요청 기록이 있습니다. 앱 운영자의 신원은 이 기록으로 알 수 없습니다.

쓸 때는 "메일을 훔쳤다" 가 아니라 "이 앱으로 이 기간에 이 리소스를 요청한 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다. 보고서 틀은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)에 있습니다.

## 함께 볼 페이지

- [OAuth 앱과 동의](../../01-foundations/identity/oauth-consent.md)
- [토큰과 세션](../../01-foundations/identity/tokens-sessions.md)
- [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md)
- [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md)
- [OAuth 토큰 기록](../../02-artifacts/google-workspace/token-audit.md)
- [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)
- [탐지 규칙으로 로그 검색하기](../../03-techniques/analysis/detection-rules.md)
- [메일 계정을 빼앗겨 송금 사기를 당했나](bec.md)
- [토큰을 훔쳐 로그인했나](token-theft.md)

## 참고 문헌

1. Microsoft, "Microsoft Entra audit log activity reference", entra-docs (ms.date 2025-03-25). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
2. Microsoft, "App consent grant investigation" (2025-03-12). https://learn.microsoft.com/en-us/security/operations/incident-response-playbook-app-consent
3. Microsoft, "Detect and remediate illicit consent grants in Microsoft 365" (2026-07-03). https://learn.microsoft.com/en-us/defender-office-365/detect-and-remediate-illicit-consent-grants
4. Microsoft, "Microsoft Entra data retention", entra-docs (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
5. Microsoft, "Manage audit log retention policies" (2026-06-19). https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
6. Microsoft, "Search the audit log" (2026-06-19). https://learn.microsoft.com/en-us/purview/audit-search
7. Microsoft, "Access Microsoft Graph activity logs" (2026-07-04). https://learn.microsoft.com/en-us/graph/microsoft-graph-activity-logs-overview
8. Microsoft, "Office 365 Management Activity API schema" (2026-08-26). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
9. Microsoft, "Refresh tokens in the Microsoft identity platform", entra-docs (ms.date 2025-11-05). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity-platform/refresh-tokens.md
10. Microsoft, "Overview of user and admin consent", entra-docs (ms.date 2025-03-18). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/enterprise-apps/user-admin-consent-overview.md
11. Microsoft, "Microsoft Entra authentication and authorization error codes" (2025-02-03). https://learn.microsoft.com/en-us/entra/identity-platform/reference-error-codes
12. Hawk, Get-HawkTenantEntraIDAppAuditLog.ps1. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Get-HawkTenantEntraIDAppAuditLog.ps1
13. Hawk, Get-HawkTenantConsentGrant.ps1. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Get-HawkTenantConsentGrant.ps1
14. Microsoft-Extractor-Suite, Get-OAuthPermissions.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-OAuthPermissions.ps1
15. DFIR-O365RC, Get-AADApps.ps1. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/Get-AADApps.ps1
16. SigmaHQ, azure_app_end_user_consent.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/audit_logs/azure_app_end_user_consent.yml
17. SigmaHQ, azure_app_end_user_consent_blocked.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/audit_logs/azure_app_end_user_consent_blocked.yml
18. SigmaHQ, azure_app_delegated_permissions_all_users.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/audit_logs/azure_app_delegated_permissions_all_users.yml
19. SigmaHQ, azure_app_privileged_permissions.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/audit_logs/azure_app_privileged_permissions.yml
20. SigmaHQ, azure_app_credential_added.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/audit_logs/azure_app_credential_added.yml
21. SigmaHQ, azure_service_principal_created.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/audit_logs/azure_service_principal_created.yml
22. SigmaHQ, microsoft365_susp_oauth_app_file_download_activities.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/threat_management/microsoft365_susp_oauth_app_file_download_activities.yml
23. Google, "OAuth Token Audit Activity Events" (2026-09-03 UTC). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/token
24. Google, "OAuth log events", Google Workspace Admin Help. https://support.google.com/a/answer/6124308?hl=en
25. Google, "Data retention and lag times", Google Workspace Admin Help. https://support.google.com/a/answer/7061566?hl=en
26. Google, "Admin Audit Activity Events - Domain Settings" (2026-09-03 UTC). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-domain-settings
27. Google, "Admin Audit Activity Events - Security Settings" (2026-09-03 UTC). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-security-settings
28. SigmaHQ, gcp_gworkspace_granted_domain_api_access.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/gworkspace/admin/gcp_gworkspace_granted_domain_api_access.yml
29. ALFA, alfa/utils/mappings.yml. https://github.com/invictus-ir/ALFA
30. Okta, okta-event-types.csv. https://developer.okta.com/docs/okta-event-types.csv
31. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
