---
title: "권한 변화 따라가기"
parent: "기법 · 분석"
nav_order: 700
---

# 권한 변화 따라가기 (Permission Changes)

지금 누가 어떤 권한을 가졌는지 적은 목록(현재 상태)과 감사 로그에 남은 권한 변경 기록(변경 이벤트)을 맞대어, 각 권한이 언제 누구의 손으로 생겼고 그 뒤에 무엇에 쓰였는지를 한 줄로 잇는 방법입니다.

## 언제 쓰나

계정을 빼앗긴 뒤 관리자 역할이 붙었는지, 앱이나 서비스 계정에 넓은 권한이 새로 생겼는지, 사서함·파일·드라이브를 외부 사람이 볼 수 있게 바뀌었는지를 가려낼 때 씁니다. 권한 변경은 비밀번호를 바꿔도 남아 있는 경우가 많아서, 침해 범위를 정하고 무엇을 되돌려야 하는지 목록을 만들 때 이 분석이 기준이 됩니다. 역할·서비스 주체·서비스 계정이 무엇인지는 [클라우드 계정과 역할](../../01-foundations/identity/users-roles.md)에, 앱 동의는 [OAuth 앱과 동의](../../01-foundations/identity/oauth-consent.md)에 있습니다.

이 분석은 두 가지 자료를 함께 씁니다. 감사 로그는 누가 언제 무엇을 바꿨는지를 남기지만 보관 기간 안의 일만 보여 줍니다. 현재 상태 목록은 조사하는 날의 권한만 보여 주고 언제 생겼는지는 알려 주지 않습니다. 둘을 맞대면 "지금 있는 권한 중 기록으로 출처를 댈 수 있는 것" 과 "보관 기간 밖에서 생겨 출처를 댈 수 없는 것" 이 갈립니다. 서비스별 보관 기간은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)를 봅니다.

## 절차

1. **현재 권한 목록부터 받습니다.** 역할 구성원, 앱 권한 부여, 사서함 권한, 공유 설정을 조사 시점 기준으로 내려받아 기준선으로 삼습니다. Microsoft 365 에서 쓰는 공개 도구는 아래 도구 절에 있습니다. 목록은 로그보다 먼저 받아 두어야 조사 중에 누가 권한을 되돌려도 그 전 상태가 남습니다.
2. **감사 로그를 권한 변경 작업 이름으로 거릅니다.** 서비스별 작업 이름과 필드는 아래 표에 있습니다. 결과마다 행위자(바꾼 쪽)와 대상(권한을 받은 쪽), 권한의 범위를 나눠 적습니다.
3. **성공한 변경만 따로 추립니다.** Azure 활동 로그는 한 작업에 레코드가 여러 개 생기고, `status` 에 `Started`·`Succeeded`·`Failed` 같은 값이 들어갑니다[5]. 한 작업의 레코드는 `operationId` 가 같고, 같은 큰 동작에 속한 레코드는 `correlationId` 가 같습니다[5]. Entra 감사 로그는 `result` 에 `success`·`failure`·`timeout` 같은 값이 들어갑니다[2]. CloudTrail 은 요청이 오류를 돌려주면 `errorCode` 가 붙습니다[12].
4. **대상 목록을 1단계의 현재 목록과 맞댑니다.** 기록은 있는데 목록에 없으면 나중에 되돌린 권한이고, 목록에는 있는데 기록이 없으면 보관 기간 밖에서 생긴 권한일 가능성이 있습니다.
5. **행위자가 그 직전에 어떻게 로그인했는지 봅니다.** 행위자 계정의 로그인 기록을 [이상한 로그인 가려내기](suspicious-sign-ins.md)의 방법으로 확인합니다.
6. **권한이 생긴 뒤 그 권한으로 한 일을 붙입니다.** 권한을 받은 계정·앱의 활동과 데이터 접근 기록을 [클라우드 타임라인](timeline.md)에 올립니다.
7. **되돌린 흔적도 찾습니다.** 역할 제거, 권한 회수, 삭제 작업을 같은 방식으로 거르면 권한을 잠깐 올렸다가 내린 흔적이 드러납니다. Sigma 의 `azure_ad_account_created_deleted` 규칙은 Entra 감사 로그에서 `Add user` 와 `Delete user` 를 함께 봅니다[24].

### Microsoft Entra ID

Entra 감사 로그에서 권한과 관련된 활동은 몇 개 범주 (Category) 에 모입니다(2025년 3월 문서 기준)[1].

| 범주 | 활동 이름 |
|---|---|
| RoleManagement | `Add member to role`, `Add eligible member to role`, `Add scoped member to role`, `Add member to role scoped over Restricted Management Administrative Unit`, `Remove member from role` |
| ApplicationManagement | `Add app role assignment to service principal`, `Add delegated permission grant`, `Add owner to application`, `Add service principal credentials`, `Update application - Certificates and secrets management`, `Consent to application` |
| GroupManagement | `Add member to group`, `Add member to role in PIM completed (timebound)`, `Add eligible member to role in PIM completed (permanent)` 등 |
| DirectoryManagement | `Set federation settings on domain` |
| Policy | `Update Conditional Access policy` |
| AuthorizationPolicy | `Update authorization policy` |

권한 있는 ID 관리 (Privileged Identity Management, PIM) 활동은 서비스 `Privileged Identity Management` 아래에 있고, 같은 이름의 활동이 RoleManagement·GroupManagement·ResourceManagement 범주에 나뉘어 있습니다[1].

레코드(Graph 의 directoryAudit)에는 `activityDateTime`, `activityDisplayName`, `category`, `correlationId`, `initiatedBy`(사용자 또는 앱), `loggedByService`, `operationType`, `result`, `targetResources` 가 있습니다[2]. 바뀐 속성은 `targetResources` 안의 `modifiedProperties` 에 들어가고, Sigma 규칙은 `TargetResources.ModifiedProperties.DisplayName` 으로 바뀐 속성 이름을, `TargetResources.ModifiedProperties.NewValue` 로 새 값을 찾습니다[24]. 역할은 이름 대신 GUID 로 찾기도 하는데, Sigma 의 전역·기기 관리자 역할 추가 규칙은 `Category: RoleManagement` 이면서 `OperationName` 에 `Add` 와 `member to role` 이 든 레코드 중 `TargetResources` 에 `62e90394-69f5-4237-9190-012177145e10` 이나 `7698a772-787b-4ac8-901f-60d6b08affd2` 가 든 것을 찾습니다[24]. 앱 동의의 해석(관리자 동의 여부, `AllPrincipals`)은 [OAuth 앱과 동의](../../01-foundations/identity/oauth-consent.md)와 [악성 OAuth 앱에 동의했나](../../04-scenarios/account-compromise/illicit-consent.md)에 있습니다. 로그를 받는 방법은 [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md)를 봅니다.

### Azure 역할 기반 액세스 제어

Azure 역할 기반 액세스 제어 (Azure RBAC) 의 역할 할당·역할 정의 변경은 활동 로그 (Activity Log) 에 남고, `authorization.action` 값은 `Microsoft.Authorization/roleAssignments/write`·`/roleAssignments/delete`·`/roleDefinitions/write`·`/roleDefinitions/delete` 입니다[3]. 범위는 `authorization.scope`, 행위자는 `caller`, 시각은 `eventTimestamp`, 결과는 `status.value` 에서 읽습니다[3]. 서비스 주체가 할당을 만들면 `caller` 에 이메일 대신 서비스 주체의 객체 ID 가 들어갑니다[3]. 새로 만든 할당의 내용은 `properties.requestbody` 에 `PrincipalId`·`PrincipalType`·`RoleDefinitionId`·`Scope` 로 들어 있고, `RoleDefinitionId` 는 역할 정의 GUID 가 붙은 경로라서 역할 이름은 따로 풀어야 합니다[3]. 아래는 문서의 레코드 모양을 따라 만든 예시입니다.

```json
{
  "authorization": {
    "action": "Microsoft.Authorization/roleAssignments/write",
    "scope": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-example/providers/Microsoft.Authorization/roleAssignments/11111111-1111-1111-1111-111111111111"
  },
  "caller": "admin@contoso.com",
  "eventTimestamp": "2026-03-01T22:07:42.456241+00:00",
  "properties": {
    "requestbody": "{\"Properties\":{\"PrincipalId\":\"22222222-2222-2222-2222-222222222222\",\"PrincipalType\":\"User\",\"RoleDefinitionId\":\"/providers/Microsoft.Authorization/roleDefinitions/33333333-3333-3333-3333-333333333333\",\"Scope\":\"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-example\"}}"
  }
}
```

Log Analytics 로 보낸 활동 로그에서는 `AzureActivity | where Authorization contains "Microsoft.Authorization/roleAssignments/write" and ActivityStatus == "Succeeded"` 로 성공한 할당을 거릅니다[3]. 구조는 [활동 로그](../../02-artifacts/azure/activity-log.md)를 봅니다.

전역 관리자의 액세스 권한 상승 (elevate access) 은 루트 범위(`/`)에 사용자 액세스 관리자 (User Access Administrator) 역할을 스스로 할당하는 동작입니다[4]. 이 기록은 Entra 감사 로그와 Azure 활동 로그 양쪽에 남습니다(2025년 3월 문서 기준)[4]. Entra 감사 로그에서는 서비스 필터 `Azure RBAC (Elevated Access)` 에 `User has elevated their access to User Access Administrator for their Azure Resources` 로 보이고, 이 기록은 미리 보기 기능입니다[4]. 활동 로그에서는 구독이 아닌 **디렉터리 활동 (Directory Activity)** 에 작업 이름 `Assigns the caller to User Access Administrator role`, `authorization.action` 값 `Microsoft.Authorization/elevateAccess/action`, 범위 `/providers/Microsoft.Authorization`, 범주 `Administrative` 로 남습니다[4]. 이 테넌트 수준 기록은 `https://management.azure.com/providers/Microsoft.Insights/eventtypes/management/values` 로 조회하고, 전역 관리자가 아닌 계정이 이 기록을 읽게 하려면 `/providers/Microsoft.Insights` 범위에 Reader 역할을 줍니다[4].

### Exchange Online·SharePoint·OneDrive

사서함 권한 부여는 통합 감사 로그의 `ExchangeAdmin` 레코드 유형에 `Add-MailboxPermission`·`Add-RecipientPermission`·`Add-ADPermission` 작업으로 남습니다[7]. Hawk 는 이 셋을 모은 뒤 `AccessRights` 가 `FullAccess`·`SendAs` 이거나 작업이 `Add-ADPermission`·`Add-RecipientPermission` 인 것을 조사 대상으로 뽑고, `NT AUTHORITY\SYSTEM (Microsoft.Exchange.ServiceHost)` 가 DiscoverySearchMailbox 에 `Discovery Management` 로 준 권한은 정상 시스템 작업으로 뺍니다[7]. Exchange 관리 역할 변경은 같은 레코드 유형의 `New-`·`Remove-ManagementRole`, `New-`·`Remove-`·`Set-ManagementRoleAssignment`, `New-`·`Remove-`·`Set-ManagementScope`, `New-`·`Remove-`·`Set-ManagementRoleEntry`, `New-`·`Remove-`·`Set-RoleGroup`, `Add-`·`Remove-RoleGroupMember` 로 찾습니다[8].

SharePoint·OneDrive 의 공유는 권한을 주는 것과 같은 효과를 냅니다. 대상이 디렉터리에 있는 사용자면 SharePoint 그룹에 넣으면서 `AddedToGroup` 과 `SharingSet` 을 남깁니다[6]. 디렉터리에 없는 외부인이면 `AnonymousLinkCreated`, `SecureLinkCreated`, `AddedToSecureLink`, 사이트를 공유할 때만 `SharingInvitationCreated` 가 남고, 받는 사람은 `TargetUserOrGroupName` 필드에 들어갑니다[6]. 외부인이 초대를 받아들이면 `SharingInvitationAccepted`, 익명 링크로 열면 `AnonymousLinkUsed`, 특정 사용자 링크로 열면 `FileAccessed` 가 남습니다[6]. 공유 분석의 흐름은 [외부 공유 링크로 새어 나갔나](../../04-scenarios/data-leak/external-sharing.md)에 있고, 레코드 구조는 [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md)와 [SharePoint·OneDrive](../../02-artifacts/m365/sharepoint-onedrive.md)를 봅니다.

### AWS IAM

IAM 과 STS 의 모든 동작은 CloudTrail 에 기록되고[14], `eventName` 은 호출한 API 이름입니다[12]. 2021년 11월 22일부터 트레일은 IAM·STS 같은 전역 서비스 이벤트를 us-east-1 리전에 기록하므로, 단일 리전 트레일이 다른 리전에 있으면 이 이벤트가 빠집니다[13]. AWS 가 유출된 IAM 사용자 자격 증명에 붙이는 관리형 정책 `AWSCompromisedKeyQuarantineV3` 이 막는 동작 목록에는 권한을 바꾸는 IAM 동작이 많이 들어 있고, `iam:AddUserToGroup`, `iam:AttachRolePolicy`, `iam:AttachUserPolicy`, `iam:CreateAccessKey`, `iam:CreateLoginProfile`, `iam:CreatePolicyVersion`, `iam:CreateRole`, `iam:PutRolePolicy`, `iam:PutUserPolicy`, `iam:UpdateAssumeRolePolicy`, `s3:PutBucketPolicy` 등이 들어 있습니다[16]. CloudTrail 에서는 접두어 없이 `AddUserToGroup` 처럼 `eventName` 으로 보이고, 그룹 이름과 사용자 이름은 `requestParameters` 의 `groupName`·`userName` 에 들어갑니다[15].

행위자와 대상이 다른 계정인지가 판단의 실마리가 됩니다. Sigma 의 `aws_iam_backdoor_users_keys` 규칙은 `CreateAccessKey` 에서 `userIdentity.arn` 에 `responseElements.accessKey.userName` 이 들어 있지 않은 경우, 곧 남의 액세스 키를 만든 경우를 찾고, `aws_update_login_profile` 규칙은 `UpdateLoginProfile` 에서 `userIdentity.arn` 이 `requestParameters.userName` 과 다른 경우를 찾습니다[24]. 레코드 필드는 [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md)에, IAM 개체와 키는 [IAM 사용자·역할·액세스 키](../../02-artifacts/aws/iam.md)에 있습니다.

### Google Cloud IAM

IAM 정책 변경은 관리 활동 감사 로그(`logName` 이 `.../logs/cloudaudit.googleapis.com%2Factivity` 로 끝남)에 `protoPayload.methodName` 이 `SetIamPolicy` 인 레코드로 남고, IAM 서비스 자체의 서비스 계정 정책은 `google.iam.admin.v1.SetIAMPolicy` 로 남습니다[17][18]. 바꾼 사람은 `protoPayload.authenticationInfo.principalEmail` 입니다[18].

무엇이 바뀌었는지는 서비스마다 다르게 남습니다. `serviceData` 필드를 쓰는 서비스(예: App Engine)는 `protoPayload.serviceData.policyDelta.bindingDeltas` 에 `action: "ADD"`, `role`, `member` 로 차이를 적습니다[17]. 반면 서비스 계정에 역할을 주는 `google.iam.admin.v1.SetIAMPolicy` 레코드에는 `response` 에 `google.iam.v1.Policy` 형식의 `bindings`(역할과 구성원 목록)만 있고 차이 표시는 없습니다[18]. 이때 추가된 구성원은 같은 자원의 앞선 `SetIamPolicy` 레코드나 조사 시점의 정책과 비교해 구합니다. 서비스 계정을 가장할 수 있게 하는 `roles/iam.serviceAccountUser` 와 단기 자격 증명을 만들 수 있게 하는 `roles/iam.serviceAccountTokenCreator` 를 주는 동작도 같은 모양의 레코드를 남깁니다[18]. 레코드 구조는 [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md), 서비스 계정 키는 [IAM과 서비스 계정 키](../../02-artifacts/gcp/iam-keys.md)를 봅니다.

### Google Workspace

관리자 역할 변경은 관리 콘솔 감사 로그(Reports API 의 `admin` 애플리케이션)에 남습니다(2026년 9월 문서 기준)[19][20].

| 이벤트 이름 | 뜻 |
|---|---|
| `ASSIGN_ROLE` / `UNASSIGN_ROLE` | 사용자에게 역할을 할당·해제. 매개변수 `ROLE_NAME`, `USER_EMAIL`, `ORG_UNIT_NAME` |
| `ADD_PRIVILEGE` | 역할에 권한을 추가 |
| `GRANT_ADMIN_PRIVILEGE` / `REVOKE_ADMIN_PRIVILEGE` | 사용자에게 관리자 권한을 부여·회수 |
| `GRANT_DELEGATED_ADMIN_PRIVILEGES` | 위임 관리자 권한 부여 |

Drive 공유 권한 변경은 Drive 로그에 남습니다[21]. 사용자별 권한이 바뀌면 `change_user_access` 가 남고, 매개변수 `target_user` 에 권한이 바뀐 사용자·그룹의 이메일이나 도메인 이름이, `old_value`·`new_value` 에 바뀌기 전후 권한이, `old_visibility`·`visibility` 에 공개 범위(예: `people_with_link`)가 들어갑니다[21]. 링크 공유 범위는 `change_document_visibility`·`change_document_access_scope`, 편집자 설정은 `change_acl_editors`, 소유자는 `change_owner`, 공유 드라이브 구성원은 `shared_drive_membership_change` 로 찾고, 폴더 계층 조정 (hierarchy reconciliation) 때문에 바뀐 경우는 `_hierarchy_reconciled` 가 붙은 이벤트로 따로 남습니다[21]. 자세한 매개변수는 [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md)와 [Drive 기록](../../02-artifacts/google-workspace/drive-audit.md)에 있습니다.

### 업무용 SaaS

| 서비스 | 권한 변경 이벤트 | 주의 |
|---|---|---|
| Okta | `user.account.privilege.grant`, `group.privilege.grant`, `iam.resourceset.bindings.add`, 반대는 `user.account.privilege.revoke`·`group.privilege.revoke` | `user.account.privilege.grant` 에는 변경 뒤 사용자가 가진 **현재** 권한 전체(직접 할당과 그룹을 통한 것)가 들어 있습니다[22] |
| Slack | `role_change_to_admin`, `role_change_to_owner`, `role_change_to_user`, `role_change_to_guest`, `role_assigned`, `role_removed`, `permissions_assigned`, `permissions_removed`, `owner_transferred` | 감사 로그 API 로 받습니다[23] |
| GitHub | `org.add_member`, `org.invite_member` 등 `action` 필드 | 이 규칙에 쓰는 로그는 감사 로그 스트리밍을 켜야 받습니다[25] |
| Bitbucket | `auditType.category: 'Permissions'` 와 `auditType.action` 의 `Global permission granted`·`Global permission removed` 등 | "Advance" 로그 수준이 필요합니다[25] |

각 로그의 구조는 [Okta 시스템 로그](../../02-artifacts/saas/okta.md), [Slack 감사 로그](../../02-artifacts/saas/slack.md), [GitHub 감사 로그](../../02-artifacts/saas/github.md)를 봅니다.

## 도구

현재 권한 목록은 Microsoft 365 에서 공개 도구로 받을 수 있습니다. Hawk 의 `Get-HawkTenantConsentGrant` 는 Graph 로 지금 남아 있는 앱 권한 부여를 모아, `ConsentType` 이 `AllPrincipals` 이거나 권한 이름에 `all` 이 든 것을 "Broad-Scope Grant", `AppRoleAssignment.ReadWrite.All`·`RoleManagement.ReadWrite.Directory` 를 "Extremely Dangerous", `Mail.ReadWrite`·`Mail.Send`·`Files.`·`Sites.` 등을 "High Risk" 로 분류합니다[9]. `Get-HawkTenantEntraIDAdmin` 은 `Get-MgDirectoryRole`·`Get-MgDirectoryRoleMember` 로 디렉터리 역할 구성원을 모읍니다[9]. Microsoft-Extractor-Suite 의 `Get-AllRoleActivity` 는 역할 구성원과 함께 각 사용자의 마지막 대화형·비대화형 로그인 시각(`SignInActivity.LastSignInDateTime`, `LastNonInteractiveSignInDateTime`)을 내보내고, `Get-PIMAssignments` 는 PIM 의 활성 할당과 자격 할당을 Graph beta 의 `roleManagement/directory/roleAssignmentSchedules`·`roleEligibilitySchedules` 로 받습니다[10]. DFIR-O365RC 의 `Get-AADApps` 는 서비스 주체·앱과 그 위임 권한 부여(`oauth2PermissionGrants`), 앱 역할 할당(`appRoleAssignments`)을 내려받습니다[11].

변경 이벤트 쪽에서는 Hawk 의 `Get-HawkTenantAdminMailboxPermissionChange` 와 `Get-HawkTenantRbacChange` 가 앞의 Exchange 작업 이름으로 통합 감사 로그를 검색합니다[7][8]. 여러 서비스의 권한 변경을 한꺼번에 살펴보려면 SigmaHQ 의 클라우드 규칙(`azure_granting_permission_detection`, `azure_subscription_permissions_elevation_via_activitylogs`, `azure_ad_user_added_to_admin_role`, `aws_iam_backdoor_users_keys` 등)을 씁니다[24]. 규칙을 조회문으로 바꾸는 방법은 [탐지 규칙으로 로그 검색하기](detection-rules.md)에 있습니다. 로그를 받는 절차는 [Microsoft 365 수집 도구](../acquisition/m365-collection.md)와 [AWS·Azure·GCP 수집](../acquisition/iaas-collection.md)을 봅니다.

## 함정과 한계

- **Azure 액세스 권한 상승은 구독 활동 로그에 없습니다.** 활동 로그의 RBAC 기록은 구독 단위이고 90일치를 봅니다[3]. 액세스 권한 상승은 디렉터리 활동에 따로 남으므로 구독 활동 로그만 받으면 빠집니다[4].
- **역할이 GUID 로 적힙니다.** Azure 의 `RoleDefinitionId` 는 GUID 가 붙은 경로이고 Sigma 의 Entra 역할 규칙도 GUID 로 찾으므로, 역할 이름으로 풀어야 합니다[3][24]. 문자열 검색으로 "Administrator" 만 찾으면 GUID 로만 적힌 레코드를 놓칩니다.
- **"현재 상태" 를 담는 이벤트가 있습니다.** Okta 의 `user.account.privilege.grant` 는 새로 더해진 권한이 아니라 변경 뒤 전체 권한을 담습니다[22]. Google Cloud 의 `response.bindings` 도 정책 전체라서 추가된 구성원을 뜻하지 않습니다[18]. 이런 이벤트는 앞선 상태와 비교해야 차이가 나옵니다. 거꾸로 Okta 의 `user.account.privilege.revoke` 는 사용자의 관리자 권한이 모두 사라졌다는 뜻입니다[22].
- **응답이 비어 있어도 실패가 아닙니다.** CloudTrail 의 `responseElements` 는 읽기 전용 API 이거나 응답이 없는 동작이면 null 이고, `AddUserToGroup` 예시도 null 입니다[12][15]. 성공 여부는 `errorCode` 가 있는지로 봅니다[12]. `requestParameters`·`responseElements` 는 100KB 를 넘으면 내용이 빠지고, 최대 이벤트 크기를 1MB 로 둔 이벤트 데이터 저장소는 이벤트 전체가 1MB 를 넘을 때만 빠집니다[12].
- **한 동작이 여러 레코드를 만듭니다.** Azure 활동 로그는 상태별 레코드가 따로 생기고[5], Drive 는 여러 사람에게 한 번에 공유하면 받는 사람마다 `primary_event=true` 인 접근 변경 이벤트가 하나씩 생기며 부수 이벤트(`primary_event=false`)도 섞입니다[21]. 건수를 셀 때 이 점을 빼지 않으면 부풀려집니다.
- **표시 이메일로 적힙니다.** Drive 의 `target_user` 는 사용자에게 이메일이 여럿이면 실제로 공유에 쓴 주소 대신 표시 이메일로 남습니다[21].
- **정상 시스템 작업이 섞입니다.** Exchange 에서는 시스템 계정이 Discovery 사서함에 권한을 주는 작업이 정상적으로 일어납니다[7].
- **현재 상태 도구는 시각을 주지 않습니다.** Hawk 의 동의 목록 같은 스냅숏은 언제 동의했는지 알려 주지 않으므로, 시각은 감사 로그에서 따로 찾아야 합니다[9].
- **같은 사건이 수집 형식마다 이름이 다릅니다.** Azure 액세스 권한 상승은 활동 로그 문서에서 `Assigns the caller to User Access Administrator role` 이지만[4], Sigma 의 감사 로그 규칙은 `OperationName: 'Assigns the caller to user access admin'` 을 찾습니다[24]. Google Cloud 의 `protoPayload.methodName` 은 Sigma 규칙에서 `gcp.audit.method_name` 으로 적힙니다[24]. 규칙을 쓸 때는 받은 로그의 실제 값을 먼저 확인합니다.

## 결과를 어떻게 해석하나

**증명하는 것**은 그 시각에 그 행위자 신원(사용자 또는 서비스 주체)으로 그 권한 변경 요청이 기록됐고, 상태가 성공이었다는 것입니다[2][3]. 대상과 범위가 레코드에 적혀 있으면 어느 계정이 어느 범위에서 어떤 역할을 받았는지도 말할 수 있습니다.

**증명하지 못하는 것**은 셋입니다. 권한을 받은 쪽이 그 권한을 실제로 썼는지는 별도의 활동·데이터 접근 기록이 있어야 합니다. 행위자 계정을 쓴 사람이 계정 주인인지는 로그인 기록과 다른 정황으로 따로 판단합니다. 보관 기간 밖에서 생긴 권한은 출처를 기록으로 댈 수 없습니다.

시각은 Entra 의 `activityDateTime` 이 UTC 이고[2], CloudTrail 의 `eventTime` 은 요청이 끝난 시각을 UTC 로 적습니다[12]. Azure 활동 로그의 `eventTimestamp` 는 `Z` 나 `+00:00` 오프셋이 붙은 UTC 로 적힙니다[3]. 로그가 늦게 들어오는 정도와 화면 표시 시간대는 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)을 봅니다.

보고서에는 기록으로 확인되는 만큼만 씁니다. 예를 들면 "2026-03-01 22:07:42(UTC)에 admin@contoso.com 계정으로 사용자 22222222-… 에게 rg-example 리소스 그룹 범위의 역할 할당을 만든 요청이 성공 상태로 기록되어 있다(만든 예시)" 처럼 쓰고, "공격자가 권한을 올렸다" 는 로그인 분석과 이후 활동이 함께 뒷받침할 때만 씁니다. 권한 상승 사건 전체의 흐름은 [권한을 올렸나](../../04-scenarios/infrastructure/privilege-escalation.md), 권한 변경 뒤 로그를 끈 흔적은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)를 봅니다.

## 참고 문헌

1. Microsoft, "Microsoft Entra audit log categories and activities", entra-docs (ms.date 2025-03-25). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
2. Microsoft, "directoryAudit resource type", Microsoft Graph (2024-05-24 갱신). https://learn.microsoft.com/en-us/graph/api/resources/directoryaudit
3. Microsoft, "View activity logs for Azure RBAC changes" (2022-08-21 갱신). https://learn.microsoft.com/en-us/azure/role-based-access-control/change-history-report
4. Microsoft, "Elevate access to manage all Azure subscriptions and management groups" (2025-03-10 갱신). https://learn.microsoft.com/en-us/azure/role-based-access-control/elevate-access-global-admin
5. Microsoft, "Azure Activity Log event schema", azure-monitor-docs (ms.date 2026-03-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
6. Microsoft, "Use sharing auditing in the audit log", Microsoft Purview (2026-06-24 갱신). https://learn.microsoft.com/en-us/purview/audit-log-sharing
7. T0pCyber, Hawk(Get-HawkTenantAdminMailboxPermissionChange.ps1). https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Get-HawkTenantAdminMailboxPermissionChange.ps1
8. T0pCyber, Hawk(Get-HawkTenantRbacChange.ps1). https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Get-HawkTenantRbacChange.ps1
9. T0pCyber, Hawk(Get-HawkTenantConsentGrant.ps1, Get-HawkTenantEntraIDAdmin.ps1). https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Get-HawkTenantConsentGrant.ps1
10. Invictus Incident Response, Microsoft-Extractor-Suite(Scripts/Get-Roles.ps1). https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-Roles.ps1
11. ANSSI, DFIR-O365RC(README.md). https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/README.md
12. AWS, "CloudTrail record contents for management, data, and network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
13. AWS, "CloudTrail concepts", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html
14. AWS, "Logging IAM and AWS STS API calls with AWS CloudTrail", IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/cloudtrail-integration.html
15. AWS, "CloudTrail log file examples", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-examples.html
16. AWS, "AWSCompromisedKeyQuarantineV3", AWS Managed Policy Reference. https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSCompromisedKeyQuarantineV3.html
17. Google Cloud, "Understanding audit logs", Cloud Logging (2026-09-25 갱신). https://cloud.google.com/logging/docs/audit/understanding-audit-logs
18. Google Cloud, "Example logs for service accounts", IAM (2026-09-24 갱신). https://cloud.google.com/iam/docs/audit-logging/examples-service-accounts
19. Google, "Admin Audit Activity Events - Delegated Admin Settings", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-delegated-admin-settings
20. Google, "Admin Audit Activity Events - User Settings", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-user-settings
21. Google, "Drive Audit Activity Events", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/drive
22. Okta, "Event types" 목록(okta-event-types.csv). https://developer.okta.com/docs/okta-event-types.csv
23. Slack, "Audit Logs API: actions". https://api.slack.com/admins/audit-logs-call
24. SigmaHQ, 클라우드 규칙(azure/audit_logs, azure/activity_logs/azure_granting_permission_detection.yml·azure_subscription_permissions_elevation_via_activitylogs.yml, aws/cloudtrail/aws_iam_backdoor_users_keys.yml·aws_update_login_profile.yml, gcp/audit/gcp_service_account_modified.yml). https://github.com/SigmaHQ/sigma/tree/master/rules/cloud
25. SigmaHQ, GitHub·Bitbucket 감사 로그 규칙(github_new_org_member.yml, bitbucket_audit_global_permissions_change_detected.yml). https://github.com/SigmaHQ/sigma/tree/master/rules/application
