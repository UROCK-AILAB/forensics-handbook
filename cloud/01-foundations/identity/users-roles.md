---
title: "클라우드 계정과 역할"
parent: "기반 · 계정과 인증"
nav_order: 30
---

# 클라우드 계정과 역할 (Users·Roles·Service Accounts)

클라우드 로그에서 "누가" 에 해당하는 신원은 사람 계정뿐 아니라 서비스 계정·서비스 주체·관리 ID·역할 세션까지 여러 종류이고 종류마다 식별자와 기록 필드가 다르므로, 표시 이름이 아니라 바뀌지 않는 ID 로 행위자를 묶어 읽어야 합니다.

## 이 형식을 쓰는 아티팩트

이 쪽은 파일 형식이 아니라 로그 레코드가 행위자를 적는 방식을 다룹니다. 계정을 만들고 지우는 일, 역할을 주고 빼는 일은 각 서비스의 관리 감사 기록에 남고, 그 계정이 한 행동은 서비스 로그의 행위자 필드에 남습니다. 두 기록을 잇는 열쇠가 아래 표의 "바뀌지 않는 ID" 입니다.

| 서비스 | 신원 종류 | 바뀌지 않는 ID | 계정·역할 변경이 남는 곳 |
|---|---|---|---|
| Microsoft 365·Entra ID | 사용자, 애플리케이션·서비스 주체·관리 ID | 객체 ID (`oid`, Graph 의 `id`) | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md)의 감사 로그, [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md) |
| Azure | Entra 신원 + Azure RBAC 역할 할당 | `PrincipalId` | [활동 로그](../../02-artifacts/azure/activity-log.md) |
| AWS | 루트, IAM 사용자, 역할과 역할 세션, Identity Center 사용자 | 고유 ID (`AIDA`·`AROA` 등으로 시작) | [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md), [IAM](../../02-artifacts/aws/iam.md) |
| Google Cloud | 사용자, 서비스 계정(사용자 관리·기본·서비스 에이전트) | `principalSubject`, 서비스 계정 메일 | [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md), [IAM 키](../../02-artifacts/gcp/iam-keys.md) |
| Google Workspace | 사용자, 관리자 역할, OAuth 앱 | `actor.profileId` | [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md) |
| Okta·Slack·GitHub | 사용자, 관리 역할, API 토큰 | 서비스마다 다름 | [Okta](../../02-artifacts/saas/okta.md), [Slack](../../02-artifacts/saas/slack.md), [GitHub](../../02-artifacts/saas/github.md) |

신원이 어느 테넌트·계정·프로젝트에 속하는지는 [테넌트·구독·계정·프로젝트](../model/tenancy.md)에서 다룹니다. 앱 등록과 동의로 생기는 앱 신원은 [OAuth 앱과 동의](oauth-consent.md)에서, 신원이 받은 토큰과 세션은 [토큰과 세션](tokens-sessions.md)에서 다룹니다.

## 구조

### Microsoft Entra ID (Microsoft 365·Azure 공통 디렉터리)

Entra 의 신원은 사용자와 워크로드 신원 (workload identity) 으로 나뉩니다. 워크로드 신원은 애플리케이션·서비스 주체·관리 ID 셋입니다[1]. 애플리케이션 객체는 모든 테넌트에서 쓰는 전역 틀이고, 서비스 주체 (service principal) 는 그 앱이 특정 테넌트에 만든 사본으로 그 테넌트에서 앱이 실제로 할 수 있는 일과 접근할 자원을 정합니다[1]. 관리 ID (managed identity) 는 개발자가 자격 증명을 관리하지 않아도 되는 특별한 서비스 주체입니다[1]. 그래서 로그의 행위자가 사람이 아니라 앱일 수 있고, 앱이 권한을 받는 과정은 [OAuth 앱과 동의](oauth-consent.md)에서 따로 읽습니다.

사용자와 서비스 주체를 가리키는 값은 객체 ID 입니다. 액세스 토큰의 `oid` 클레임은 요청자의 바뀌지 않는 ID 이고, 같은 테넌트 안에서는 앱이 달라도 값이 같으며 Graph 가 돌려주는 사용자의 `id` 와 같습니다[2]. 같은 사람이라도 테넌트마다 객체 ID 가 다릅니다[2]. `sub` 는 앱마다 값이 달라지는 쌍 식별자 (pairwise identifier) 이고, `preferred_username`·`name` 은 바뀔 수 있는 표시용 값입니다[2].

Entra 에는 역할 체계가 둘 있습니다. Entra 역할은 사용자·그룹·도메인 같은 디렉터리 자원의 권한이고, Azure RBAC 역할은 구독 안 리소스의 권한입니다(자세한 경계는 [테넌트 쪽](../model/tenancy.md)). 두 체계의 변경은 서로 다른 로그에 남습니다.

| 하는 일 | Entra 감사 로그 (범주 · 작업) | 통합 감사 로그 작업 |
|---|---|---|
| 사용자 만들기·지우기 | UserManagement · `Add user`, `Delete user`, `Hard Delete user`, `Restore user` | `Add user.`, `Delete user.` |
| 사용자 속성·상태 바꾸기 | UserManagement · `Update user`, `Disable account`, `Enable account` | `Update user.` |
| 비밀번호 | UserManagement · `Change user password`, `Reset password`, `Set force change user password` | `Change user password.`, `Reset user password.`, `Set force change user password.` |
| 디렉터리 역할 주기·빼기 | RoleManagement · `Add member to role`, `Add eligible member to role`, `Add scoped member to role`, `Remove member from role` | `Add member to role.`, `Remove member from role.` |
| 역할 정의 | RoleManagement · `Add role definition`, `Update role definition`, `Delete role definition` | — |
| PIM 활성화·할당 | RoleManagement · `Add member to role requested (PIM activation)`, `Add member to role completed (PIM activation)`, `Add eligible member to role in PIM completed (permanent)`, `Remove member from role (PIM activation expired)`, `Update role setting in PIM` | — |

Entra 감사 로그의 작업 이름은 [4], 통합 감사 로그의 작업 이름은 [5]에 있습니다. 권한 있는 역할 관리 (Privileged Identity Management, PIM) 기록은 비슷한 작업이 많아서 이름 끝의 renew·timebound·permanent 를 구분해 읽어야 합니다[4]. 통합 감사 로그에서 Entra 관리 작업은 `RecordType` 8 (`AzureActiveDirectory`) 이고, 15 (`AzureActiveDirectoryStsLogon`) 는 로그인, 9 (`AzureActiveDirectoryAccountLogon`) 는 폐기된 로그인 형식입니다[6]. 이 레코드에는 행위자 `Actor`, 대상 `Target`, 행위자 조직 GUID `ActorContextId`, 대상 조직 GUID `TargetContextId`, `ActorIpAddress`, 다른 사람이 대신 작업한(act-on-behalf-of) 경우의 고객 지원 티켓 ID `SupportTicketId` 가 있습니다[6]. `Actor`·`Target` 은 형식과 값의 쌍 목록이고 형식은 `Claim`·`Name`·`Other`·`PUID`·`SPN`·`UPN` 중 하나입니다[6].

### Azure RBAC

구독 안의 역할 할당·역할 정의 변경은 활동 로그에 `Microsoft.Authorization/roleAssignments/write`, `Microsoft.Authorization/roleAssignments/delete`, `Microsoft.Authorization/roleDefinitions/write` 작업으로 남습니다[7]. 역할 할당 레코드의 `requestbody` 에는 역할을 받은 주체의 `PrincipalId`, 그 종류 `PrincipalType`(예: `User`), `RoleDefinitionId`, `Scope` 가 들어갑니다[7]. 활동 로그로 지난 90일의 RBAC 변경을 볼 수 있습니다(2022년 8월 갱신 문서 기준)[7]. 보관 기간은 [보관 기간과 라이선스](../logging/retention-licensing.md)에서 다룹니다.

Entra 전역 관리자가 권한 올리기 (elevate access) 를 하면 루트 범위(`/`)에 User Access Administrator 역할이 붙습니다[8]. 이 일은 Entra 감사 로그와 Azure 활동 로그 둘 다에 남습니다[8].

| 기록 | 찾는 값 |
|---|---|
| Entra 감사 로그 (서비스 Azure RBAC (Elevated Access), 2026년 9월 문서 기준 미리 보기) | 범주 `AzureRBACRoleManagementElevateAccess`, 작업 `User has elevated their access to User Access Administrator for their Azure Resources`, 해제는 `The role assignment of User Access Administrator has been removed from the user`[4][8] |
| Azure 활동 로그 (Directory Activity) | 작업 표시 이름 `Assigns the caller to User Access Administrator role`, `authorization.action` = `Microsoft.Authorization/elevateAccess/action`, `scope` = `/providers/Microsoft.Authorization`, 권한을 올린 사용자는 `caller`[8] |

활동 로그 쪽은 구독 활동이 아니라 Directory Activity 로 바꿔서 봐야 나타납니다[8].

### AWS

CloudTrail 레코드의 `userIdentity.type` 이 행위자 종류를 알려 줍니다[9].

| `type` | 뜻 | `userName` |
|---|---|---|
| `Root` | 계정 루트 사용자 | 계정 별칭이 있으면 별칭, 없으면 필드가 없음("Root" 라는 값은 들어가지 않음) |
| `IAMUser` | IAM 사용자의 장기 자격 증명 | IAM 사용자 이름 |
| `AssumedRole` | `AssumeRole` 로 받은 역할의 임시 자격 증명 | 없음. 역할 이름은 `sessionContext.sessionIssuer.userName` |
| `Role` | 역할 | 사용자 정의 |
| `FederatedUser` | `GetFederationToken` 으로 받은 임시 자격 증명 | 없음 |
| `AWSAccount` | 다른 AWS 계정이 내 역할을 넘겨받음 | 없음 |
| `AWSService` | AWS 서비스가 내 역할을 넘겨받음 | 없음 |
| `IdentityCenterUser` | IAM Identity Center 사용자 | 없음. `onBehalfOf` 의 `userId`·`identityStoreArn` 으로 찾음 |
| `SAMLUser`·`WebIdentityUser` | STS 의 SAML·웹 ID 페더레이션 호출 | — |
| `Directory`·`Unknown` | 디렉터리 서비스, 알 수 없는 신원 | 있을 수 있음 |

표의 내용은 [9]에 있습니다. 페더레이션으로 들어온 신원은 [페더레이션과 SSO](federation-sso.md)에서 다룹니다.

IAM 자원에는 이름과 별도로 고유 ID 가 붙고, 접두사로 종류를 알 수 있습니다. `AIDA` 는 IAM 사용자, `AROA` 는 역할, `AGPA` 는 그룹, `AIPA` 는 EC2 인스턴스 프로파일, `AKIA` 는 액세스 키, `ASIA` 는 STS 임시 액세스 키입니다[10]. 접두사는 만든 시기에 따라 다를 수 있고, `ASIA` 키 ID 는 비밀 키·세션 토큰과 함께여야 유일합니다[10]. `AKIA` 로 시작하는 키는 IAM 사용자나 루트의 장기 자격 증명이고 `ASIA` 로 시작하는 키는 STS 로 만든 임시 자격 증명입니다[11]. `GetAccessKeyInfo` 로 키가 속한 계정 ID 를 알 수 있지만 키가 활성·비활성·삭제 중 어느 상태인지는 알 수 없고, `ASIA` 키를 누가 요청했는지는 CloudTrail 의 STS 이벤트에서 찾습니다[11]. `GetAccessKeyLastUsed` 는 키를 마지막으로 쓴 시각·서비스·리전과 키 주인의 사용자 이름을 돌려줍니다[12]. 자격 증명 보고서와 마지막 접근 정보는 [IAM 사용자·역할·액세스 키](../../02-artifacts/aws/iam.md)에서 다룹니다.

IAM Identity Center 기록은 이벤트 원천으로 나뉩니다. 권한 세트·앱·할당은 `sso.amazonaws.com`, 사용자·그룹·MFA 장치는 `sso-directory.amazonaws.com`·`identitystore.amazonaws.com`, CLI·IDE 로그인은 `sso-oauth.amazonaws.com`, SCIM 프로비저닝은 `identitystore-scim.amazonaws.com` 입니다[13].

### Google Cloud

서비스 계정은 세 종류입니다. 사용자 관리 서비스 계정은 고객이 직접 만들고, 기본 서비스 계정은 일부 서비스를 켤 때 자동으로 생기지만 관리 책임은 고객에게 있으며, 서비스 에이전트는 Google Cloud 가 만들고 관리하면서 서비스가 고객 자원에 접근할 때 씁니다[14]. IAM 정책에서 서비스 계정은 `serviceAccount:my-service-account@my-project.iam.gserviceaccount.com` 모양으로 적습니다[14].

감사 로그의 `protoPayload.authenticationInfo` 에 행위자가 적힙니다[15].

| 필드 | 뜻 |
|---|---|
| `principalEmail` | 요청한 사용자나 서비스 계정의 메일. 개인정보 보호 때문에 가려질 때가 있음 |
| `principalSubject` | 요청자 신원의 문자열 표현. 1자·3자 신원 모두 채워짐 |
| `serviceAccountKeyName` | 서비스 계정 키로 인증했을 때 그 키의 이름. `//iam.googleapis.com/projects/{PROJECT_ID}/serviceAccounts/{ACCOUNT}/keys/{key}` 모양 |
| `serviceAccountDelegationInfo[]` | 서비스 계정을 대신 쓴 실제 주체들의 위임 이력. 원래 위임 순서대로 정렬됨 |

서비스 계정 만들기·지우기 같은 관리 작업의 `methodName` 은 `google.iam.admin.v1.CreateServiceAccount`, `google.iam.admin.v1.DeleteServiceAccount`, `google.iam.admin.v1.DisableServiceAccount`, `google.iam.admin.v1.UndeleteServiceAccount` 모양입니다[16]. 키 필드와 키 목록을 뽑는 방법은 [IAM과 서비스 계정 키](../../02-artifacts/gcp/iam-keys.md)에서 다룹니다.

### Google Workspace

사용자와 관리자 역할의 변경은 관리 감사 로그에 이벤트 이름으로 남습니다.

| 하는 일 | 이벤트 이름 |
|---|---|
| 사용자 만들기·지우기·되살리기·이름 바꾸기 | `CREATE_USER`, `DELETE_USER`, `UNDELETE_USER`, `RENAME_USER` |
| 정지·해제·보관 | `SUSPEND_USER`, `UNSUSPEND_USER`, `ARCHIVE_USER` |
| 관리자 권한 | `GRANT_ADMIN_PRIVILEGE`, `REVOKE_ADMIN_PRIVILEGE`, `GRANT_DELEGATED_ADMIN_PRIVILEGES` |
| 비밀번호·복구 정보 | `CHANGE_PASSWORD`, `CHANGE_PASSWORD_ON_NEXT_LOGIN`, `VIEW_TEMP_PASSWORD`, `ADD_RECOVERY_EMAIL`, `CHANGE_RECOVERY_EMAIL` |
| 조직 단위 이동·사용자 목록 내려받기 | `MOVE_USER_TO_ORG_UNIT`, `DOWNLOAD_USERLIST_CSV` |
| 위임 관리자 역할 | `CREATE_ROLE`, `DELETE_ROLE`, `RENAME_ROLE`, `UPDATE_ROLE`, `ASSIGN_ROLE`, `UNASSIGN_ROLE`, `ADD_PRIVILEGE`, `REMOVE_PRIVILEGE` |

사용자 설정 이벤트는 [17], 위임 관리자 이벤트는 [18]에 있습니다. `GRANT_ADMIN_PRIVILEGE` 의 설명문은 "Admin privileges granted to {USER_EMAIL}" 입니다[17].

활동 레코드의 행위자는 `actor` 에 적힙니다. `actor.profileId` 는 Workspace 사용자의 고유 프로필 ID 인데, Workspace 사용자가 아니면 없거나 자리 표시 값 `105250506097979753968` 이 들어갑니다[19]. `actor.key` 는 `actor.callerType` 이 `KEY` 일 때만 있고 OAuth 2LO 요청의 `consumer_key` 이거나 로봇 계정 식별자입니다[19]. 앱이 한 일이면 `actor.applicationInfo` 에 `oauthClientId`, `applicationName`, 사용자를 가장했는지 알려 주는 `impersonation` 이 들어갑니다[19].

### 업무용 SaaS

| 서비스 | 계정·권한 변경 기록 |
|---|---|
| Okta | `user.lifecycle.create`, `user.lifecycle.deactivate`, `user.account.privilege.grant`(관리 권한 변경), `user.account.privilege.revoke`(관리 권한 전부 회수), `group.user_membership.add`, `system.api_token.create`(범위 없는 API 토큰 생성), `system.api_token.revoke`[20]. 관리 역할 할당은 `group.privilege.grant`, `iam.resourceset.bindings.add` 로도 찾습니다[25] |
| Slack | `user_created`, `user_deactivated`, `user_email_updated`, `role_change_to_admin`, `role_change_to_owner`[22]. 감사 로그 API 는 Enterprise 요금제에서만 씁니다[23] |
| GitHub | 토큰으로 한 이벤트에 토큰의 SHA-256 해시 `hashed_token`, 인증 방식 `programmatic_access_type`, 토큰 범위 `token_scopes` 가 붙습니다[24] |

Okta 에서 특정 API 토큰으로 한 일은 `transaction.detail.requestApiTokenId` 로 모읍니다[21].

## 읽는 법

레코드 하나에서 행위자를 읽을 때는 종류 → 바뀌지 않는 ID → 표시 이름 순서로 봅니다. 종류가 사람이 아니면(역할 세션, 서비스 계정, 앱) 그 뒤에 있는 사람을 찾는 단계를 한 번 더 거칩니다.

아래는 AWS 문서의 필드 구조로 만든 예시입니다. 값은 모두 지어낸 것입니다.

```json
"userIdentity": {
  "type": "AssumedRole",
  "principalId": "AROAEXAMPLEROLEID1234:ops-session",
  "arn": "arn:aws:sts::123456789012:assumed-role/OpsAdmin/ops-session",
  "accountId": "123456789012",
  "accessKeyId": "ASIAIOSFODNN7EXAMPLE",
  "sessionContext": {
    "sessionIssuer": {
      "type": "Role",
      "principalId": "AROAEXAMPLEROLEID1234",
      "arn": "arn:aws:iam::123456789012:role/OpsAdmin",
      "accountId": "123456789012",
      "userName": "OpsAdmin"
    }
  }
}
```

이 레코드는 역할 `OpsAdmin` 의 임시 자격 증명으로 한 호출입니다. 역할의 고유 ID 는 `sessionIssuer.principalId` 의 `AROA...` 이고, 최상위 `principalId` 는 그 뒤에 세션 이름을 붙인 값입니다[9]. `AssumedRole` 레코드에는 `userName` 이 없으므로 역할 이름은 `sessionIssuer.userName` 에서 읽습니다[9]. 누가 이 역할을 넘겨받았는지는 같은 `ASIA` 키를 내준 STS `AssumeRole` 이벤트를 찾아야 알 수 있습니다[11]. 역할 세션을 사람과 잇는 필드와 방법은 [토큰과 세션](tokens-sessions.md)에서 다룹니다.

Google Cloud 레코드는 `serviceAccountKeyName` 이 있으면 키로 인증한 것이고, `serviceAccountDelegationInfo` 가 있으면 다른 주체가 서비스 계정을 대신 쓴 것입니다[15]. Workspace 레코드는 `actor.callerType` 과 `actor.applicationInfo` 를 먼저 보고 사람이 한 일인지 앱이 한 일인지 나눕니다[19]. Entra 사용자의 마지막 로그인 시각을 볼 때는 `signInActivity` 의 세 값을 구분합니다[3].

| 값 | 뜻 |
|---|---|
| `lastSignInDateTime` | 마지막 대화형 로그인 시도. 성공과 실패를 모두 포함 |
| `lastNonInteractiveSignInDateTime` | 마지막 비대화형 로그인 시도. 성공과 실패를 모두 포함. 2020년 5월 기록부터 유지 |
| `lastSuccessfulSignInDateTime` | 대화형·비대화형을 가리지 않고 마지막 성공 로그인. 2023년 12월 1일부터 제공되고 이전 값은 채우지 않음 |

각 값에는 해당 로그인 레코드를 가리키는 요청 ID(`lastSignInRequestId` 등)가 붙어서 로그인 로그의 원래 레코드로 찾아갈 수 있습니다[3].

## 포렌식에서 중요한 점

**증명하는 것.** 바뀌지 않는 ID 로 특정한 신원이 언제 만들어지고 지워졌는지, 어떤 역할을 누구에게서 받았는지를 작업 이름·시각·행위자로 보여 줍니다[4][7][17]. AWS 역할 세션이 어느 역할에서 나왔는지는 `sessionIssuer` 가, Google Cloud 요청이 서비스 계정 키로 인증됐다는 사실은 `serviceAccountKeyName` 이 보여 줍니다[9][15].

**증명하지 못하는 것.** 공유된 서비스 계정·키·역할을 실제로 어느 사람이 썼는지는 이 기록만으로 알 수 없습니다. Google Cloud 에서 서비스 계정 키나 연결된 서비스 계정으로 인증하면 감사 로그에는 서비스 계정 신원만 남고, VM 에서 코드를 실행한 사람이나 키를 쓴 사람은 남지 않습니다[16]. 서비스 계정 가장 (impersonation) 으로 접근하면 대부분의 감사 로그에 가장한 주체와 서비스 계정이 함께 남습니다[16]. 역할을 받은 기록과 그 권한을 실제로 쓴 기록도 다르므로, 권한을 썼는지는 해당 서비스의 로그에서 따로 확인합니다. 권한 변화를 시간순으로 따라가는 방법은 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md)에서 다룹니다.

**시각.** Entra 로그인 로그 시각과 `signInActivity` 값은 UTC 입니다[3][26]. Entra 관리 센터 화면은 로그를 보는 관리자의 시간대로 바꿔 보여 줍니다[27]. CloudTrail `eventTime` 은 `2023-07-19T21:44:40Z` 처럼 UTC 로 적힙니다[28]. Workspace 로그는 늦게 들어올 수 있는데, 관리자 로그는 몇 분, 사용자 로그의 로그인 이벤트는 몇 분, 사용자 계정 이벤트는 수십 분이 걸립니다(2026년 9월 문서 기준)[29]. Workspace 관리 콘솔 사용자 목록의 마지막 로그인은 "2 minutes ago" 같은 대략 값이고 반영에 몇 시간에서 3일이 걸립니다[30]. 시각 필드 해석은 [클라우드 로그의 시각](../logging/timestamps.md)에서 다룹니다.

**지우기.** 지운 계정도 관리 감사 기록에는 남습니다. Entra 에서는 `Delete user` 뒤에 `Hard Delete user` 가 따로 있어서 두 작업을 구분해 읽습니다[4]. DFIR-O365RC 는 현재 사용자와 함께 삭제된 사용자 목록도 받습니다[33].

## 함정

- 이름으로 신원을 묶지 않습니다. AWS 에서 사용자 John 을 지우고 같은 이름으로 다시 만들면 고유 ID 가 다르고[10], Entra 는 같은 사람이라도 테넌트마다 객체 ID 가 다르며[2], Workspace 조사 도구는 사용자 이름을 바꾸면 옛 이름으로 검색되지 않습니다[31].
- `lastSignInDateTime` 은 실패한 시도도 포함하므로 계정을 실제로 쓴 마지막 시각이 아닙니다[3]. Microsoft-Extractor-Suite 의 `Get-UsersInfo.ps1`·`Get-Roles.ps1` 은 `LastSignInDateTime`·`LastNonInteractiveSignInDateTime` 만 뽑고 `lastSuccessfulSignInDateTime` 은 뽑지 않아서[32], 이 결과로 "쓰지 않는 계정" 을 가르면 실패 시도가 섞입니다.
- 통합 감사 로그의 작업 이름은 끝에 마침표가 붙습니다(`Add member to role.`)[5]. Entra 감사 로그의 이름(`Add member to role`)으로 만든 검색 조건을 그대로 옮기면 걸리지 않습니다[4].
- 탐지 규칙마다 같은 기록의 필드 이름과 값 표기가 다릅니다. Sigma 의 Entra 규칙은 `properties.message`·`OperationName`·`Category` 같은 필드를 섞어 쓰고, PIM 할당을 `Add eligible member (permanent)` 로 찾는 반면 Entra 문서의 작업 이름은 `Add eligible member to role in PIM completed (permanent)` 입니다[25][4]. Google Cloud 서비스 계정 규칙은 `gcp.audit.method_name` 이 `.serviceAccounts.create` 로 끝나는지 보는 반면 IAM 감사 문서의 메서드 이름은 `google.iam.admin.v1.CreateServiceAccount` 모양입니다[25][16]. 규칙을 옮길 때는 수집한 형식에 맞춰 필드와 값을 바꿉니다. 방법은 [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md)에서 다룹니다.
- AWS Identity Center 문서의 표는 로그인 이벤트 원천을 `signin.amazon.com` 으로 적지만[13], 콘솔 로그인 이벤트 예시의 `eventSource` 값은 `signin.amazonaws.com` 입니다[28]. 검체의 실제 값을 먼저 확인하고 검색합니다.
- Okta 로그인 실패 레코드의 `actor.alternateId` 에 비밀번호가 들어 있을 수 있습니다. 사용자가 아이디 칸에 비밀번호를 친 경우이고, Sigma 규칙은 `legacyEventType` 이 `core.user_auth.login_failed` 인 레코드에서 이런 값을 찾습니다[25]. 보고서에 옮기거나 공유하기 전에 가립니다.
- 관리 ID·서비스 주체의 로그인은 사용자 로그인과 다른 로그 범주에 있습니다. [토큰과 세션](tokens-sessions.md)에서 다룹니다.

## 도구

| 도구 | 하는 일 |
|---|---|
| Microsoft-Extractor-Suite | `Get-UsersInfo.ps1` 은 사용자의 `UserPrincipalName`, `Id`, `UserType`, `AccountEnabled`, `CreatedDateTime`, `LastPasswordChangeDateTime`, `OnPremisesSyncEnabled`, `ExternalUserState`, `Identities`, `SignInActivity` 등을 뽑습니다. `Get-Roles.ps1` 의 `Get-PIMAssignments` 는 Graph beta `roleManagement/directory/roleAssignmentSchedules`·`roleEligibilitySchedules` 로 활성·자격 할당을 받습니다[32] |
| DFIR-O365RC | `Get-AADUsers.ps1` 이 현재 사용자(`Get-MgUser`)와 삭제된 사용자(`Get-MgDirectoryDeletedItemAsUser`)를 함께 받습니다[33] |
| Hawk | `Get-HawkTenantEntraIDAdmin` 이 디렉터리 역할과 구성원(`Get-MgDirectoryRole`, `Get-MgDirectoryRoleMember`)을 받습니다[34] |
| Untitled Goose Tool | `identityProtection/riskyUsers` 와 위험 사용자 이력을 받습니다[35] |

AWS 와 Google Cloud 의 계정·키 목록을 받는 명령은 [IAM 사용자·역할·액세스 키](../../02-artifacts/aws/iam.md)과 [IAM과 서비스 계정 키](../../02-artifacts/gcp/iam-keys.md)에서 다룹니다. 수집 도구 전반은 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md)와 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md)에서 다룹니다.

함께 볼 페이지: [OAuth 앱과 동의](oauth-consent.md), [토큰과 세션](tokens-sessions.md), [다단계 인증과 조건부 접근](mfa-conditional-access.md), [페더레이션과 SSO](federation-sso.md), [테넌트·구독·계정·프로젝트](../model/tenancy.md), [권한을 올렸나](../../04-scenarios/infrastructure/privilege-escalation.md), [액세스 키가 새어 나갔나](../../04-scenarios/infrastructure/leaked-keys.md).

## 참고 문헌

1. Microsoft, "What are workload identities?", Microsoft Learn (2026-05-08 갱신). https://learn.microsoft.com/en-us/entra/workload-id/workload-identities-overview
2. Microsoft, "Access token claims reference", Microsoft Learn (2026-06-25 갱신). https://learn.microsoft.com/en-us/entra/identity-platform/access-token-claims-reference
3. Microsoft, "signInActivity resource type", Microsoft Graph, Microsoft Learn (2025-07-05 갱신). https://learn.microsoft.com/en-us/graph/api/resources/signinactivity
4. Microsoft, "Microsoft Entra audit log categories and activities" (ms.date 2025-03-25). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
5. Microsoft, "Audit log activities", Microsoft Purview, Microsoft Learn (2026-09-08 갱신). https://learn.microsoft.com/en-us/purview/audit-log-activities
6. Microsoft, "Office 365 Management Activity API schema", Microsoft Learn (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
7. Microsoft, "View activity logs for Azure RBAC changes", Microsoft Learn (2022-08-21 갱신). https://learn.microsoft.com/en-us/azure/role-based-access-control/change-history-report
8. Microsoft, "Elevate access to manage all Azure subscriptions and management groups", Microsoft Learn (2025-03-10 갱신). https://learn.microsoft.com/en-us/azure/role-based-access-control/elevate-access-global-admin
9. AWS, "CloudTrail userIdentity element", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
10. AWS, "IAM identifiers", AWS IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html
11. AWS, "GetAccessKeyInfo", AWS STS API Reference. https://docs.aws.amazon.com/STS/latest/APIReference/API_GetAccessKeyInfo.html
12. AWS, "GetAccessKeyLastUsed", AWS IAM API Reference. https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetAccessKeyLastUsed.html
13. AWS, "Logging IAM Identity Center API calls with AWS CloudTrail", IAM Identity Center User Guide. https://docs.aws.amazon.com/singlesignon/latest/userguide/logging-using-cloudtrail.html
14. Google Cloud, "Service accounts overview", IAM (2026-09-24 갱신). https://cloud.google.com/iam/docs/service-account-overview
15. Google Cloud, "AuditLog", Cloud Logging 참조 (2025-07-21 갱신). https://cloud.google.com/logging/docs/reference/audit/auditlog/rest/Shared.Types/AuditLog
16. Google Cloud, "Service account impersonation", IAM (2026-09-24 갱신). https://cloud.google.com/iam/docs/service-account-impersonation ; Google Cloud, "IAM audit logging" (2026-09-24 갱신). https://cloud.google.com/iam/docs/audit-logging
17. Google, "Admin Audit Activity Events - User Settings", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-user-settings
18. Google, "Admin Audit Activity Events - Delegated Admin Settings", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-delegated-admin-settings
19. Google, "Method: activities.list", Admin SDK Reports API (2026-09-09 갱신). https://developers.google.com/workspace/admin/reports/v1/reference/activities/list
20. Okta, "Event types" (okta-event-types.csv). https://developer.okta.com/docs/okta-event-types.csv
21. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
22. Slack, "Using the Audit Logs API" (actions 목록). https://api.slack.com/admins/audit-logs-call
23. Slack, "Monitoring your workspace with audit logs". https://api.slack.com/admins/audit-logs
24. GitHub, "Identifying audit log events performed by an access token", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/identifying-audit-log-events-performed-by-an-access-token
25. SigmaHQ, Sigma 규칙. rules/cloud/azure/audit_logs/azure_priviledged_role_assignment_add.yml, rules/cloud/azure/audit_logs/azure_subscription_permissions_elevation_via_auditlogs.yml, rules/cloud/gcp/audit/gcp_service_account_modified.yml, rules/identity/okta/okta_admin_role_assigned_to_user_or_group.yml, rules/identity/okta/okta_admin_role_assignment_created.yml, rules/identity/okta/okta_password_in_alternateid_field.yml. https://github.com/SigmaHQ/sigma
26. Microsoft, "signIn resource type", Microsoft Graph beta, Microsoft Learn (2025-11-28 갱신). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
27. Microsoft, "Learn about the sign-in log activity details" (ms.date 2026-03-04). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
28. AWS, "AWS Management Console sign-in events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-aws-console-sign-in-events.html
29. Google, "Data retention and lag times", Google Workspace Admin Help (2026-09-25 갱신). https://support.google.com/a/answer/7061566
30. Google, "View your users' last sign-in", Google Workspace 관리자 도움말 (2026-09-18 갱신). https://knowledge.workspace.google.com/admin/reports/view-your-users-last-sign-in
31. Google, "OAuth log events", Google Workspace Admin Help (2026-09-18 갱신). https://support.google.com/a/answer/6124308?hl=en
32. Invictus Incident Response, Microsoft-Extractor-Suite (Scripts/Get-UsersInfo.ps1, Scripts/Get-Roles.ps1). https://github.com/invictus-ir/Microsoft-Extractor-Suite
33. ANSSI, DFIR-O365RC (Get-AADUsers.ps1). https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/Get-AADUsers.ps1
34. T0pCyber, Hawk (Hawk/functions/Tenant/Get-HawkTenantEntraIDAdmin.ps1). https://github.com/T0pCyber/hawk
35. CISA, Untitled Goose Tool (goosey/entra_id_datadumper.py). https://github.com/cisagov/untitledgoosetool/blob/main/goosey/entra_id_datadumper.py
