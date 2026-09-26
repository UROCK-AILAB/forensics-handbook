---
title: "권한을 올렸나"
parent: "시나리오 · 인프라 침해"
nav_order: 780
---

# 권한을 올렸나 (Privilege Escalation)

공격자나 내부자가 원래 없던 권한을 자기 자신이나 다른 주체에게 붙였는지를 AWS·Azure·Microsoft Entra ID·Google Cloud·Google Workspace·Okta 의 감사 기록으로 가려내는 순서를 다룹니다.

## 조사 질문

- 누가 어느 주체(사용자·그룹·역할·서비스 주체·서비스 계정)에게 어떤 역할이나 정책을 붙였나?
- 붙인 시각은 언제이고, 요청은 성공했나?
- 권한이 미친 범위는 어디까지인가(계정 하나, 구독 하나, 리소스 그룹, 테넌트 전체, 조직 전체)?
- 붙은 권한으로 그 뒤에 무엇을 불렀나?
- 붙였던 권한을 나중에 떼어 내 흔적을 줄이려 했나?

권한이 바뀐 기록은 대부분 관리 작업용 감사 로그에 남습니다. 권한 변화 기록을 한 줄씩 읽는 방법은 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md) 에 있고, 이 쪽은 "무엇을 어떤 순서로 보는가" 를 다룹니다.

## 먼저 확인할 것

**권한이 어느 층에서 바뀌었을지 정합니다.** 같은 "관리자" 라도 층마다 기록되는 곳이 다릅니다. Azure 구독·관리 그룹의 역할(Azure RBAC)은 Azure 활동 로그 (Activity Log) 에, Entra ID 의 디렉터리 역할은 Entra 감사 로그에 남습니다[12][18]. Google Cloud 프로젝트·폴더·조직의 역할은 Cloud Audit Logs 의 관리 활동 로그에, Google Workspace 관리 콘솔 역할은 관리 콘솔 감사 로그에 남습니다[26][33]. 계정·역할의 기본 개념은 [클라우드 계정과 역할](../../01-foundations/identity/users-roles.md) 에 있습니다.

**기록이 남는 기간을 확인합니다.** 권한을 붙인 때가 보관 기간 밖이면 "언제" 를 잃습니다. 아래 표는 2026년 9월 문서 기준이며, 서비스별 전체 표는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 에 있습니다.

| 서비스 | 권한 변경을 담는 기록 | 기본 보관 | 늘리는 방법 |
|---|---|---|---|
| AWS | CloudTrail 관리 이벤트 | 이벤트 기록 (Event history) 90일[5] | 트레일·이벤트 데이터 저장소 |
| Azure | 활동 로그(구독별, 디렉터리 수준) | 90일[13] | 진단 설정으로 다른 곳에 보냄[13] |
| Microsoft Entra ID | 감사 로그 | Free 7일, P1·P2 30일[19] | Azure Monitor 로 내보냄. 라이선스를 올려도 지난 기록은 되살아나지 않음[19] |
| Google Cloud | 관리 활동 감사 로그 | 로그 버킷 설정을 따름([Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md)) | 버킷 보관 설정, 싱크 |
| Google Workspace | 관리 콘솔 감사 로그 | 6개월[35] | BigQuery 내보내기 등 |
| Okta | 시스템 로그 | 90일이 넘은 기록은 API 가 돌려주지 않음[38] | 외부 저장소로 스트리밍 |

**대응자가 한 변경을 먼저 받아 둡니다.** 권한을 회수하거나 격리 정책을 붙인 대응 작업도 같은 작업 이름으로 남습니다. 대응 시각과 대응에 쓴 계정을 먼저 받아 두어야 공격자의 변경과 섞이지 않습니다. 로그를 먼저 확보하는 방법은 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 공급자·탐지 규칙의 표시: GuardDuty `PrivilegeEscalation:IAMUser/AnomalousBehavior`, Entra PIM 경고, Sigma 규칙 결과 | 권한 상승과 관련된 API 호출이 이상하다고 표시된 시각과 주체 | [GuardDuty](../../02-artifacts/aws/guardduty.md), [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md) |
| 2 | AWS CloudTrail 의 `iam.amazonaws.com` 이벤트 | 정책 부착·인라인 정책·정책 버전·신뢰 정책 변경 | [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md), [IAM](../../02-artifacts/aws/iam.md) |
| 3 | Azure 활동 로그의 `Microsoft.Authorization/*` 작업, 디렉터리 수준 활동 로그의 `elevateAccess` | 구독·관리 그룹 역할 할당, 루트 범위 권한 올리기 | [활동 로그](../../02-artifacts/azure/activity-log.md) |
| 4 | Entra 감사 로그 RoleManagement 범주, PIM 활동 | 디렉터리 역할 부여·적격 역할 활성화 | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md) |
| 5 | Google Cloud 관리 활동 로그의 `SetIamPolicy`, `UpdateRole` | 프로젝트·서비스 계정 정책에 붙은 역할과 구성원 | [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md), [IAM과 서비스 계정 키](../../02-artifacts/gcp/iam-keys.md) |
| 6 | Google Workspace 관리 콘솔 감사 로그 | 관리자 역할 할당, 역할에 권한 추가 | [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md) |
| 7 | Okta 시스템 로그, GitHub 감사 로그 | SaaS 관리자 역할 부여, 실행 경로 추가 | [Okta 시스템 로그](../../02-artifacts/saas/okta.md), [GitHub 감사 로그](../../02-artifacts/saas/github.md) |
| 8 | 권한을 받은 뒤의 호출 | 붙은 권한을 실제로 썼는지 | [클라우드 타임라인](../../03-techniques/analysis/timeline.md) |

## 분석 흐름

1. **공급자의 표시와 탐지 규칙 결과를 모읍니다.** AWS GuardDuty 의 `PrivilegeEscalation:IAMUser/AnomalousBehavior` 는 높은 권한을 얻는 데 흔히 쓰는 API 가 이상한 방식으로 불렸다는 결과이고, 기본 심각도는 Medium, 데이터 원천은 CloudTrail 관리 이벤트입니다[1]. 이 결과는 API 하나일 수도 있고, 한 사용자 ID 가 가까운 시간에 부른 여러 API 일 수도 있습니다[1]. 이 부류에는 IAM 정책·역할·사용자를 바꾸는 `AssociateIamInstanceProfile`, `AddUserToGroup`, `PutUserPolicy` 같은 API 가 들어가고, 요청의 어느 요소(요청한 사용자, 요청 위치, API)가 이상한지는 결과 상세에 있습니다[1]. 결과가 없다고 끝내지 않고, 아래 단계의 작업 이름으로 로그를 직접 찾습니다.

2. **AWS 에서는 CloudTrail 의 IAM 이벤트를 훑습니다.** `eventSource` 가 `iam.amazonaws.com` 인 레코드에서 `eventName` 이 권한을 바꾸는 작업인 것을 고릅니다. AWS 가 유출된 키를 격리하려고 만든 관리형 정책 `AWSCompromisedKeyQuarantineV3` 이 거부하는 목록에는 `AddUserToGroup`, `AttachGroupPolicy`, `AttachRolePolicy`, `AttachUserPolicy`, `CreateAccessKey`, `CreateInstanceProfile`, `CreateLoginProfile`, `CreatePolicyVersion`, `CreateRole`, `CreateUser`, `PassRole`, `PutGroupPolicy`, `PutRolePolicy`, `PutUserPermissionsBoundary`, `PutUserPolicy`, `SetDefaultPolicyVersion`, `UpdateAssumeRolePolicy`, `UpdateLoginProfile`, `UpdateAccessKey` 가 들어 있어서, 권한 상승에 쓰일 수 있는 IAM 작업을 고를 때 출발점으로 쓸 수 있습니다[2]. 각 작업의 `requestParameters` 에 들어가는 값(정책 문서, 대상 사용자·역할 이름)은 검체의 레코드를 열어 확인합니다. 다른 사용자의 콘솔 비밀번호를 바꾼 기록은 `UpdateLoginProfile` 가운데 `userIdentity.arn` 과 `requestParameters.userName` 이 다른 레코드로 찾을 수 있고, Sigma `aws_update_login_profile` 이 이 조건을 씁니다[6]. IAM 밖에서 권한을 넘겨받는 길도 봅니다. Sigma 규칙은 Glue 개발 엔드포인트 작업(`glue.amazonaws.com` 의 `CreateDevEndpoint`·`DeleteDevEndpoint`·`UpdateDevEndpoint`)과 Lambda 레이어 부착(`lambda.amazonaws.com` 에서 `UpdateFunctionConfiguration` 으로 시작하고 `requestParameters.layers` 가 있는 레코드)을 권한 상승으로 분류합니다[7][8]. EC2 사용자 데이터 변경(`ec2.amazonaws.com` 의 `ModifyInstanceAttribute`, `requestParameters.attribute` 가 `userData`)은 Sigma 가 실행 (execution) 으로 분류하지만, 인스턴스가 부팅할 때 root 나 SYSTEM 권한으로 실행되는 스크립트를 바꾸는 작업이라 함께 봅니다[9]. 사용자 데이터 변경은 [채굴용 자원을 만들었나](cryptomining.md) 에서도 다룹니다.

3. **AWS 의 역할 넘겨받기를 이어 붙입니다.** 역할을 넘겨받은 자격 증명으로 부른 호출은 `userIdentity.type` 이 `AssumedRole` 이고 `userIdentity.sessionContext.sessionIssuer.type` 이 `Role` 인 레코드로 찾고, Sigma `aws_sts_assumerole_misuse` 가 이 조건을 씁니다[10]. 역할을 넘겨받은 자격 증명으로 다시 다른 역할을 넘겨받는 역할 체이닝 (role chaining) 에서는 처음 정한 `sourceIdentity` 가 다음 요청까지 이어지고, 다른 값으로 바꾸려 하면 요청이 거부됩니다[4]. 다른 계정의 역할을 넘겨받으면 호출한 계정과 역할이 있는 계정 양쪽에 레코드가 생기고, 두 레코드의 `sharedEventID` 가 같습니다[4]. `iam:PassRole` 은 IAM 의 마지막 접근 정보 (last accessed information) 에 나오지 않으므로, 이 정보만 보고 "역할을 넘긴 적이 없다" 고 판단하지 않습니다[3]. 임시 자격 증명을 따라가는 방법은 [액세스 키가 새어 나갔나](leaked-keys.md) 와 [토큰과 세션](../../01-foundations/identity/tokens-sessions.md) 에 있습니다.

4. **Azure 에서는 역할 할당 작업을 찾습니다.** 구독 안에서 역할 할당이나 역할 정의를 바꾸면 활동 로그에 남고, 90일치를 볼 수 있습니다[12]. 작업 이름은 역할 할당 생성 `Microsoft.Authorization/roleAssignments/write`, 삭제 `Microsoft.Authorization/roleAssignments/delete`, 사용자 지정 역할 정의 생성·변경 `Microsoft.Authorization/roleDefinitions/write`, 삭제 `Microsoft.Authorization/roleDefinitions/delete` 이고, 이벤트 범주는 Administrative 입니다[12]. 레코드에서 `authorization:scope`(범위), `caller`(요청자), `eventTimestamp`, `status:value`(Started·Succeeded·Failed)를 읽습니다[12]. 서비스 주체가 역할을 할당했으면 `caller` 에 메일 주소 대신 개체 ID 가 찍힙니다[12]. 누구에게 어떤 역할을 줬는지는 `properties.requestbody` 의 `PrincipalId`, `PrincipalType`, `RoleDefinitionId`, `Scope` 에 있는데, `RoleDefinitionId` 는 `/providers/Microsoft.Authorization/roleDefinitions/` 뒤에 GUID 가 붙은 값이라 역할 이름은 역할 정의 목록과 대조해 풀어야 합니다[12][11]. PowerShell 로는 `Get-AzLog` 결과를 `Authorization.Action` 이 `Microsoft.Authorization/roleAssignments/*` 인 것으로 거르면 됩니다[12]. Sigma `azure_granting_permission_detection` 은 활동 로그에서 `Microsoft.Authorization/roleAssignments/write` 를 키워드로 찾습니다[15].

    ```powershell
    Get-AzLog -StartTime (Get-Date).AddDays(-7) | Where-Object {$_.Authorization.Action -like 'Microsoft.Authorization/roleAssignments/*'}
    ```

5. **Azure 의 루트 범위 권한 올리기를 따로 찾습니다.** Entra ID 전역 관리자 (Global Administrator) 가 "Azure 리소스에 대한 액세스 관리 (Access management for Azure resources)" 토글을 켜면 루트 범위(`/`)에 User Access Administrator 역할이 붙고, 테넌트의 모든 구독·관리 그룹에서 역할을 할당할 수 있게 됩니다[11]. 이 설정은 켠 사용자 한 명에게만 적용됩니다[11]. 이 작업은 두 곳에 남습니다. Entra 감사 로그에서는 서비스 필터 "Azure RBAC (Elevated Access)" 로 거르고, 활동 이름은 올릴 때 `User has elevated their access to User Access Administrator for their Azure Resources`, 뗄 때 `The role assignment of User Access Administrator has been removed from the user` 이며, 감사 범주는 `AzureRBACRoleManagementElevateAccess` 입니다[11][18]. Entra 감사 로그 쪽 기록은 미리 보기 기능입니다[11]. Azure 활동 로그에서는 구독이 아닌 디렉터리 활동 (Directory Activity) 에 작업 `Assigns the caller to User Access Administrator role` 로 남고, 원본 JSON 에는 `authorization.action` 이 `Microsoft.Authorization/elevateAccess/action`, `authorization.scope` 가 `/providers/Microsoft.Authorization`, `subscriptionId` 가 빈 문자열로 찍힙니다[11]. 디렉터리 수준 활동 로그는 구독 경로가 없는 `https://management.azure.com/providers/Microsoft.Insights/eventtypes/management/values` 주소로 받고[11], Microsoft-Extractor-Suite 의 `Get-AzureDirectoryActivityLogs` 가 이 주소를, `Get-AzureActivityLogs` 가 구독별 주소를 부릅니다[23][24]. DFIR-O365RC 의 `Get-AzRMActivityLogs` 로도 구독의 활동 로그를 받을 수 있고, 도움말 예시는 최근 90일치를 받습니다[25]. Sigma `azure_subscription_permissions_elevation_via_activitylogs` 는 `operationName` 값 `MICROSOFT.AUTHORIZATION/ELEVATEACCESS/ACTION` 을 고릅니다[16]. 지금 권한이 올라가 있는 사용자는 Entra ID 속성 화면의 "Manage elevated access users" 나 `az role assignment list --role "User Access Administrator" --scope "/"` 로 확인합니다[11].

6. **Entra ID 디렉터리 역할을 봅니다.** 감사 로그의 RoleManagement 범주에 `Add member to role`, `Add eligible member to role`, `Add scoped member to role`, `Add member to role scoped over Restricted Management Administrative Unit`, `Remove member from role` 같은 활동이 남습니다[18]. Privileged Identity Management(PIM) 를 쓰면 `Add member to role in PIM requested (timebound)`, `Add member to role in PIM completed (timebound)`, `Add eligible member to role in PIM completed (permanent)` 처럼 이름이 비슷한 활동이 많이 생기므로 renew·timebound·permanent 를 구분해 읽고, 24시간에도 기록이 많이 쌓이니 필터로 좁힙니다[18]. Sigma `azure_pim_role_assigned_outside_of_pim` 은 PIM 경고 `riskEventType` 값 `rolesAssignedOutsidePrivilegedIdentityManagementAlertConfiguration`, 즉 PIM 밖에서 권한 역할을 할당한 경고를 고릅니다[22]. 서비스 주체에 역할을 붙인 기록은 `targetResources.type` 이 `Service Principal` 인 역할 추가 활동으로 찾을 수 있습니다[21]. 앱에 API 권한을 주거나 동의한 기록(`Add app role assignment to service principal`, `Add delegated permission grant`, `Consent to application`)은 [악성 OAuth 앱에 동의했나](../account-compromise/illicit-consent.md) 에서 다룹니다[18].

7. **Google Cloud 에서는 `SetIamPolicy` 를 찾습니다.** 역할 부여는 허용 정책 (allow policy) 을 바꾸는 `SetIamPolicy` 로 관리 활동 로그에 남습니다. 프로젝트 정책이면 `protoPayload.serviceName` 이 `cloudresourcemanager.googleapis.com`, `resource.type` 이 `project` 이고, `protoPayload.authenticationInfo.principalEmail` 이 역할을 준 주체, `response.bindings[]` 가 바뀐 뒤의 정책입니다[27]. 일부 서비스는 `serviceData.policyDelta.bindingDeltas[]` 에 `action`(예: `ADD`), `role`, `member` 로 바뀐 부분만 따로 적고[28], plaso 의 GCP 로그 파서는 이 값을 "`ACTION member with role ROLE`" 모양의 문자열로 뽑습니다[31]. 서비스 계정에 서비스 계정 사용자 (`roles/iam.serviceAccountUser`) 역할을 주면 그 주체가 서비스 계정을 가장 (impersonate) 할 수 있고, 이 부여는 `resource.type` 이 `service_account` 인 `google.iam.admin.v1.SetIAMPolicy` 로 남습니다[27]. 단기 자격 증명을 만들 수 있는 서비스 계정 토큰 생성자 (`roles/iam.serviceAccountTokenCreator`) 역할도 비슷한 기록을 남깁니다[27]. 로그 탐색기에서는 다음처럼 찾습니다[26].

    ```text
    resource.type = "project" AND
    log_id("cloudaudit.googleapis.com/activity") AND
    protoPayload.methodName:"SetIamPolicy"
    ```

    사용자 지정 역할을 바꾼 기록은 `resource.type = "iam_role"` 과 `protoPayload.methodName:"UpdateRole"` 로, 서비스 계정 생성·삭제는 `CreateServiceAccount`·`DeleteServiceAccount` 로 찾습니다[26]. Sigma `gcp_service_account_modified` 는 `gcp.audit.method_name` 이 `.serviceAccounts.patch`·`.serviceAccounts.create`·`.serviceAccounts.update`·`.serviceAccounts.enable`·`.serviceAccounts.undelete` 로 끝나는 기록을 고릅니다[32]. 프로젝트의 `getIamPolicy` 결과에는 상위 조직·폴더에서 물려받은 정책이 나오지 않으므로, 폴더·조직 수준의 `SetIamPolicy` 도 그 수준의 로그에서 따로 봅니다[30]. 서비스 계정 가장으로 받은 토큰의 흔적은 [액세스 키가 새어 나갔나](leaked-keys.md) 에 있습니다.

8. **Google Workspace 관리 콘솔 역할을 봅니다.** 관리 콘솔 감사 로그에서 `type=DELEGATED_ADMIN_SETTINGS` 인 이벤트가 관리자 역할 설정 기록입니다[33]. `ASSIGN_ROLE` 은 콘솔에 `Role {ROLE_NAME} assigned to user {USER_EMAIL}` 로, `CREATE_ROLE` 은 `New role {ROLE_NAME} created` 로, `ADD_PRIVILEGE` 는 `New privilege {PRIVILEGE_NAME} created under role {ROLE_NAME}` 로 표시되고, 회수 쪽은 `UNASSIGN_ROLE`, `REMOVE_PRIVILEGE` 입니다[33]. 사용자에게 관리자 권한을 준 기록은 `type=USER_SETTINGS` 인 사용자 설정 이벤트 `GRANT_ADMIN_PRIVILEGE`(`Admin privileges granted to {USER_EMAIL}`)로 남습니다[34]. Reports API 로는 `GET https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/admin?eventName=ASSIGN_ROLE` 처럼 이벤트 이름으로 거릅니다[33]. 관리 로그는 몇 분 안에 조회할 수 있게 됩니다[35]. Sigma `gcp_gworkspace_user_granted_admin_privileges` 는 `GRANT_DELEGATED_ADMIN_PRIVILEGES` 와 `GRANT_ADMIN_PRIVILEGE` 를 고릅니다[36].

9. **SaaS 관리자 권한을 봅니다.** Okta 시스템 로그에서 사용자의 관리자 권한 변경은 `user.account.privilege.grant`, 그룹은 `group.privilege.grant`, OAuth 2.0 클라이언트 앱은 `app.oauth2.client.privilege.grant` 이고, 관리자 역할 할당 생성은 `iam.resourceset.bindings.add`, 사용자 지정 관리자 역할 생성은 `iam.role.create`, 그 역할에 권한 추가는 `iam.role.permissions.add` 입니다[37]. Sigma 규칙은 이 가운데 `user.account.privilege.grant`·`group.privilege.grant` 와 `iam.resourceset.bindings.add` 를 고릅니다[39][40]. GitHub 에서 자체 호스팅 러너 (self-hosted runner) 를 등록하거나 러너 그룹을 바꾼 기록(`repo.register_self_hosted_runner`, `org.runner_group_updated` 등)은 역할을 올린 것은 아니지만 조직의 작업이 실행될 곳을 더한 것이라 함께 봅니다[42]. GitHub 감사 로그는 최근 180일을, Git 이벤트는 7일을 보여 줍니다[41].

10. **권한을 받은 뒤의 호출을 이어 붙입니다.** 권한 변경 기록은 권한이 붙었다는 것까지만 보여 줍니다. 권한을 받은 주체가 그 뒤에 무엇을 불렀는지는 같은 주체 ID(`userIdentity.arn`, `caller`, `principalEmail`, `actor`)로 이후 기록을 다시 검색해 확인하고, [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에 한 줄로 합칩니다. 가상 머신에서 명령을 실행하는 권한(`Microsoft.Compute/virtualMachines/runCommand/action` 등)을 쓴 흔적은 [Azure 가상 머신](../../02-artifacts/azure/azure-vm.md) 에 있고, 가상 머신 안의 흔적은 [[linux] 클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html) 을 따릅니다. 로그 설정을 끈 흔적은 [로그를 끄거나 지웠나](log-tampering.md) 로 이어집니다.

### 이 기록으로 말할 수 있는 것

권한 변경 기록은 이 주체(`caller`, `principalEmail`, `actor`)가 이 시각에 이 대상에게 이 역할이나 정책을 붙였고, 요청이 성공했는지(Azure `status`, AWS `errorCode` 유무, Google Cloud `status`)와 범위(`authorization:scope`, `resourceName`)가 어디였는지를 보여 줍니다. 붙은 권한을 실제로 썼는지, 요청한 것이 사람인지 자동화 도구인지, 보관 기간이 지나 사라진 기간에 무엇이 있었는지는 보여 주지 않습니다. Azure 는 역할 이름 대신 역할 정의 GUID 를 남기므로 역할 이름은 따로 풀어야 합니다[12].

### 시각 읽기

Azure 활동 로그의 `eventTimestamp` 는 요청을 처리한 서비스가 이벤트를 만든 시각이고, `submissionTimestamp` 는 그 이벤트를 조회할 수 있게 된 시각입니다[14]. 두 값은 UTC 로 찍힙니다(예: `2021-03-01T22:07:41.126243Z`, `2021-08-27T15:42:00.1527942Z`)[12][11]. 같은 상위 작업에 속한 이벤트는 `correlationId` 가 같습니다[14]. 다른 서비스의 시각 형식과 지연은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 에 있습니다.

## 흔한 오판

- **"Azure 역할 할당이 두 번 있었다."** 역할 할당 하나가 1초 차이로 레코드 두 건을 남길 수 있고, 한 건에는 `requestbody` 가, 다른 한 건에는 `statusCode` Created 가 들어 있습니다[12]. `status` 가 Started·Succeeded 로 나뉘기도 하므로 건수를 세지 말고 `correlationId` 로 묶어 한 작업으로 셉니다[12][14].
- **"구독별 활동 로그를 다 받았는데 권한 올리기 기록이 없다."** 루트 범위 권한 올리기는 `subscriptionId` 가 빈 디렉터리 수준 활동 로그에 남으므로, 구독별로만 받으면 빠집니다[11][24].
- **"Entra 에 `Add member to role` 이 잔뜩 있으니 관리자가 계속 늘었다."** PIM 에서 적격 역할을 켤 때마다 이 활동이 생깁니다[20]. PIM 활동의 요청·완료·갱신 기록과 함께 읽어 새 부여인지 활성화인지 가립니다[18].
- **"`SetIamPolicy` 로 찾았는데 서비스 계정 정책 변경이 안 나온다."** 서비스 계정 쪽은 `google.iam.admin.v1.SetIAMPolicy` 처럼 대소문자가 다르게 찍힙니다[27]. 로깅 쿼리 언어는 정규식과 논리 연산자 말고는 대소문자를 가리지 않으므로 `protoPayload.methodName:"SetIamPolicy"` 부분 일치로 찾되[29], 내보낸 JSON 을 다른 도구로 검색할 때는 대소문자를 무시하는 조건을 씁니다.
- **"교차 계정 역할 요청이 대상 계정 로그에 없으니 시도도 없었다."** CloudTrail 은 교차 계정 역할 넘겨받기에서 거부된 STS 요청을 대상 계정에 기록하지 않습니다[4]. 호출한 쪽 계정의 로그도 함께 받습니다.
- **"Sigma 규칙 표기와 문서 표기가 다르니 다른 이벤트다."** Sigma 의 감사 로그 규칙은 권한 올리기를 `Assigns the caller to user access admin` 로 적고[17], 문서는 활동 로그 작업을 `Assigns the caller to User Access Administrator role` 로 적습니다[11]. 규칙을 그대로 돌리기 전에 검체의 실제 값과 맞춰 봅니다([탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md)).

## 보고서 문장 예

- "2026년 9월 3일 02:14:07(UTC)에 `admin@contoso.com` 계정이 구독 범위에서 `Microsoft.Authorization/roleAssignments/write` 를 요청했고, 같은 `correlationId` 의 Succeeded 레코드가 있다. `requestbody` 의 `RoleDefinitionId` 는 Owner 역할의 정의 ID 와 같다." (만든 예시)
- "같은 날 02:20(UTC)에 디렉터리 수준 활동 로그에 `Microsoft.Authorization/elevateAccess/action` 레코드가 있고, `caller` 는 위와 같은 계정이다." (만든 예시)
- "AWS 계정 123456789012 에서 IAM 사용자 `dev-user` 가 `AttachUserPolicy` 를 호출한 기록이 CloudTrail 에 있고, 대상은 같은 사용자이며 `errorCode` 가 없다." (만든 예시)
- 쓰지 않을 문장: "공격자가 관리자 권한을 얻어 모든 자원을 장악했다." 로그는 역할이 붙었다는 것까지 보여 주고, 그 권한으로 한 일은 이후 호출 기록으로 따로 보여야 합니다.

## 함께 볼 페이지

- 같은 갈래: [액세스 키가 새어 나갔나](leaked-keys.md), [채굴용 자원을 만들었나](cryptomining.md), [로그를 끄거나 지웠나](log-tampering.md)
- 계정 쪽 권한: [악성 OAuth 앱에 동의했나](../account-compromise/illicit-consent.md), [토큰을 훔쳐 로그인했나](../account-compromise/token-theft.md)
- 기법: [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md), [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md), [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md)
- 다른 판: [[linux] 인증 로그](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/logins/auth-log.html), [[linux] 타임라인 만들기](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/timeline.html)

## 참고 문헌

1. AWS, "GuardDuty IAM finding types", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-iam.html
2. AWS, "AWSCompromisedKeyQuarantineV3", AWS Managed Policy Reference. https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSCompromisedKeyQuarantineV3.html
3. AWS, "Refine permissions in AWS using last accessed information", IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_last-accessed.html
4. AWS, "Logging IAM and AWS STS API calls with AWS CloudTrail", IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/cloudtrail-integration.html
5. AWS, "Working with CloudTrail event history", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
6. SigmaHQ, aws_update_login_profile.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_update_login_profile.yml
7. SigmaHQ, aws_passed_role_to_glue_development_endpoint.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_passed_role_to_glue_development_endpoint.yml
8. SigmaHQ, aws_new_lambda_layer_attached.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_new_lambda_layer_attached.yml
9. SigmaHQ, aws_ec2_startup_script_change.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_ec2_startup_script_change.yml
10. SigmaHQ, aws_sts_assumerole_misuse.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_sts_assumerole_misuse.yml
11. Microsoft, "Elevate access to manage all Azure subscriptions and management groups". https://learn.microsoft.com/en-us/azure/role-based-access-control/elevate-access-global-admin
12. Microsoft, "View activity logs for Azure RBAC changes". https://learn.microsoft.com/en-us/azure/role-based-access-control/change-history-report
13. Microsoft, "Azure Monitor activity log" (activity-log.md, ms.date 05/04/2026). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
14. Microsoft, "Azure Monitor activity log event schema" (activity-log-schema.md, ms.date 03/17/2026). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
15. SigmaHQ, azure_granting_permission_detection.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_granting_permission_detection.yml
16. SigmaHQ, azure_subscription_permissions_elevation_via_activitylogs.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_subscription_permissions_elevation_via_activitylogs.yml
17. SigmaHQ, azure_subscription_permissions_elevation_via_auditlogs.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/audit_logs/azure_subscription_permissions_elevation_via_auditlogs.yml
18. Microsoft, "Microsoft Entra audit log activity reference" (reference-audit-activities.md, ms.date 03/25/2025). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
19. Microsoft, "Microsoft Entra data retention" (reference-reports-data-retention.md, ms.date 01/06/2026). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
20. SigmaHQ, azure_ad_user_added_to_admin_role.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/audit_logs/azure_ad_user_added_to_admin_role.yml
21. SigmaHQ, azure_app_role_added.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/audit_logs/azure_app_role_added.yml
22. SigmaHQ, azure_pim_role_assigned_outside_of_pim.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/privileged_identity_management/azure_pim_role_assigned_outside_of_pim.yml
23. Invictus Incident Response, Microsoft-Extractor-Suite, Scripts/Get-AzureDirectoryActivityLogs.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureDirectoryActivityLogs.ps1
24. Invictus Incident Response, Microsoft-Extractor-Suite, Scripts/Get-AzureActivityLogs.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureActivityLogs.ps1
25. ANSSI, DFIR-O365RC, Get-AzRMActivityLogs.ps1. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/Get-AzRMActivityLogs.ps1
26. Google Cloud, "IAM audit logging" (Last updated 2026-09-24). https://cloud.google.com/iam/docs/audit-logging
27. Google Cloud, "Examples of audit logs for service accounts" (Last updated 2026-09-24). https://cloud.google.com/iam/docs/audit-logging/examples-service-accounts
28. Google Cloud, "Understanding audit logs" (Last updated 2026-09-25). https://cloud.google.com/logging/docs/audit/understanding-audit-logs
29. Google Cloud, "Logging query language" (Last updated 2026-09-25). https://cloud.google.com/logging/docs/view/logging-query-language
30. Google Cloud, "Enable Data Access audit logs" (Last updated 2026-09-25). https://cloud.google.com/logging/docs/audit/configure-data-access
31. log2timeline, plaso, parsers/jsonl_plugins/gcp_log.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/jsonl_plugins/gcp_log.py
32. SigmaHQ, gcp_service_account_modified.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/audit/gcp_service_account_modified.yml
33. Google, "Admin Audit Activity Events - Delegated Admin Settings", Reports API (Last updated 2026-09-03). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-delegated-admin-settings
34. Google, "Admin Audit Activity Events - User Settings", Reports API (Last updated 2026-09-03). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-user-settings
35. Google, "Data retention and lag times", Google Workspace Admin Help (Last updated 2026-09-25). https://support.google.com/a/answer/7061566
36. SigmaHQ, gcp_gworkspace_user_granted_admin_privileges.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/gworkspace/admin/gcp_gworkspace_user_granted_admin_privileges.yml
37. Okta, "Event types" (okta-event-types.csv). https://developer.okta.com/docs/okta-event-types.csv
38. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
39. SigmaHQ, okta_admin_role_assigned_to_user_or_group.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/identity/okta/okta_admin_role_assigned_to_user_or_group.yml
40. SigmaHQ, okta_admin_role_assignment_created.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/identity/okta/okta_admin_role_assignment_created.yml
41. GitHub, "Audit log for an enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/about-the-audit-log-for-your-enterprise
42. SigmaHQ, github_self_hosted_runner_changes_detected.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/application/github/audit/github_self_hosted_runner_changes_detected.yml
