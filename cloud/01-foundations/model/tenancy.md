---
title: "테넌트·구독·계정·프로젝트"
parent: "기반 · 클라우드 조사의 구조"
nav_order: 10
---

# 테넌트·구독·계정·프로젝트 (Tenant·Subscription·Account·Project)

클라우드 서비스는 리소스와 사용자를 테넌트·구독·계정·프로젝트 같은 경계로 나눠 관리하고 로그 레코드마다 그 경계의 식별자를 적으므로, 조사는 "이 기록이 어느 경계에서 나왔고 행위자는 어느 경계에 속하는가" 를 읽는 데서 시작합니다.

## 이 형식을 쓰는 아티팩트

이 페이지는 파일 형식이 아니라 조사 대상의 경계를 다룹니다. 경계는 기록이 어느 로그에 남는지, 누가 그 로그를 받을 수 있는지, 레코드의 어느 필드에 경계 식별자가 적히는지를 함께 정합니다. 그래서 사건 하나를 조사할 때도 관련된 테넌트나 계정이 둘 이상이면 로그를 경계마다 따로 받아야 하고, 받은 로그를 합칠 때는 경계 식별자로 다시 나눠 읽어야 합니다.

| 서비스 | 경계의 계층 | 레코드 속 경계 식별자 | 대표 기록 |
|---|---|---|---|
| Microsoft 365 | 테넌트 | `OrganizationId` | [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md) |
| Entra ID | 테넌트 | `HomeTenantId`·`ResourceTenantId` | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md) |
| Azure | 테넌트 → 관리 그룹 → 구독 → 리소스 그룹 → 리소스 | `subscriptionId`, `resourceId`, `claims` 안의 테넌트 ID, 테넌트 수준 리소스 로그의 `tenantId` | [활동 로그](../../02-artifacts/azure/activity-log.md), [리소스 로그](../../02-artifacts/azure/resource-logs.md) |
| AWS | 조직 → 조직 단위 → 계정 | `userIdentity.accountId`, `recipientAccountId`, `sharedEventID` | [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md) |
| Google Cloud | 조직 → 폴더 → 프로젝트 → 리소스 | `logName` 의 앞부분(`projects/`·`folders/`·`organizations/`·`billingAccounts/`) | [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md) |
| Google Workspace | 고객 ID 로 가리키는 계정 | `id.customerId`, `ownerDomain` | [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md) |
| Slack Enterprise | 엔터프라이즈 조직 → 워크스페이스 | `context.location.type`·`context.location.id` | [Slack 감사 로그](../../02-artifacts/saas/slack.md) |
| GitHub Enterprise Cloud | 엔터프라이즈 계정 → 조직 | 필드는 해당 페이지에서 다룸 | [GitHub 감사 로그](../../02-artifacts/saas/github.md) |

사용자·역할·서비스 계정처럼 경계 안에서 행동하는 주체는 [클라우드 계정과 역할](../identity/users-roles.md)에서, 경계마다 어떤 로그가 기본으로 남는지는 [기록은 어디에 남나](where-records-live.md)에서 다룹니다.

## 구조

### Microsoft 365 와 Entra ID

Microsoft 365·Azure·Dynamics CRM Online 을 구독하면 모두 Entra 테넌트를 쓰게 되고, 새 디렉터리에는 `contoso.onmicrosoft.com` 같은 초기 도메인이 붙습니다[1]. 통합 감사 로그의 공통 스키마에서 `OrganizationId` 는 조직의 Office 365 테넌트 GUID 이고, 어느 Microsoft 365 서비스에서 생긴 레코드든 같은 조직이면 값이 같습니다[2]. 여러 테넌트의 로그를 한곳에 모았다면 이 값으로 테넌트를 가를 수 있습니다.

사용자의 인증 홈 디렉터리는 하나뿐이지만, 같은 사용자가 여러 디렉터리에 게스트로 들어갈 수 있습니다[3]. 다른 조직 사용자를 B2B 협업으로 초대하면 리소스 쪽 디렉터리에 사용자 개체가 새로 생기고, 외부 게스트라면 `UserType` 이 `Guest` 입니다[4]. 이 개체의 UPN 은 게스트 메일 주소 뒤에 `#EXT#` 와 초대한 테넌트의 `tenantname.onmicrosoft.com` 을 붙인 모양이라, john@contoso.com 을 fabrikam 디렉터리에 초대하면 `john_contoso.com#EXT#@fabrikam.onmicrosoft.com` 이 됩니다[4]. 다른 Entra 조직의 자격 증명으로 로그인하는 게스트는 `Identities` 값이 `ExternalAzureAD` 입니다[4]. `UserType` 은 호스트 조직과의 관계만 나타내고 로그인 방식이나 디렉터리 역할과는 관계가 없으며, 관리자가 `Member` 와 `Guest` 사이에서 바꿀 수도 있습니다[4].

### Azure

Azure 의 관리 범위는 관리 그룹·구독·리소스 그룹·리소스의 네 단계이고, 아래 단계는 위 단계의 설정을 물려받습니다[5]. 구독은 Azure 리소스와 Azure 역할 할당을 관리하는 범위이고, 테넌트는 로그인에 쓰는 신원이 있는 디렉터리입니다[3]. 구독 하나는 디렉터리 하나만 신뢰하지만, 테넌트 하나는 여러 구독의 신뢰를 받을 수 있습니다[3]. Azure 역할은 구독 안 리소스에 대한 접근을, Entra 역할은 사용자·그룹·도메인 같은 디렉터리 리소스에 대한 접근을 정합니다[3].

한 관리 그룹 안의 구독은 모두 같은 Entra 테넌트를 신뢰해야 합니다[6]. 디렉터리 하나에 관리 그룹을 10,000개까지 둘 수 있고, 관리 그룹 트리는 루트 단계와 구독 단계를 빼고 6단계까지 깊어질 수 있으며, 관리 그룹과 구독의 부모는 하나뿐입니다[6]. 디렉터리마다 맨 위에 루트 관리 그룹이 하나 있는데, 표시 이름 기본값은 "Tenant root group" 이고 ID 는 Entra 테넌트 ID 와 같습니다[6]. 새 구독은 만들 때 기본으로 루트 관리 그룹 아래에 들어갑니다[6].

리소스 그룹은 리소스의 메타데이터를 저장하고, 리소스 그룹의 위치가 그 메타데이터가 저장되는 위치입니다[5]. 리소스 그룹을 지우면 그 안의 리소스도 모두 지워집니다[5].

아래 표는 Azure 로그 레코드에서 각 범위가 보이는 곳입니다. 식별자 값은 Microsoft 문서의 예시 모양을 따른 만든 예시입니다.

| 범위 | 식별자 모양(만든 예시) | 레코드에서 보이는 곳 |
|---|---|---|
| 테넌트 | `aaaabbbb-0000-cccc-1111-dddd2222eeee` | 활동 로그 `claims` 의 `http://schemas.microsoft.com/identity/claims/tenantid` 와 `iss`(`https://sts.windows.net/` 뒤에 테넌트 ID)[7], 테넌트 수준 리소스 로그의 `tenantId`[8] |
| 루트 관리 그룹 | 테넌트 ID 와 같은 값 | 관리 그룹 수준 활동 로그[9] |
| 구독 | `aaaa0a0a-bb1b-cc2c-dd3d-eeeeee4e4e4e` | 활동 로그 `subscriptionId`, `resourceId` 의 `/subscriptions/` 뒤[7] |
| 리소스 그룹 | `myResourceGroup` | `resourceId` 의 `/resourcegroups/` 뒤[7] |
| 리소스 | 공급자·형식·이름 | `resourceId` 의 `/providers/` 뒤[7] |

리소스 로그 공통 스키마의 `tenantId` 는 테넌트 수준 로그에만 쓰이고 리소스 수준 로그에는 나오지 않습니다[8]. 테넌트 서비스가 만든 리소스 로그의 `resourceId` 는 `/tenants/tenant-id/providers/provider-name` 모양입니다[8]. 저장소 계정이나 Event Hubs 로 내보낸 활동 로그는 리소스 로그 스키마를 따르고, `subscriptionId`·`resourceType`·`resourceGroupName` 은 `resourceId` 에서 알아낸 값입니다[7].

### AWS

AWS 조직 (organization) 은 관리 계정 (management account) 하나와 0개 이상의 멤버 계정·조직 단위 (OU)·정책으로 이루어지고 루트는 하나입니다[10]. 조직 단위는 루트와 맨 아래 조직 단위에 만든 계정을 빼고 5단계까지 깊어질 수 있습니다[10]. AWS 계정은 AWS 리소스를 담는 그릇이고, 그 안에서 행동하는 IAM 사용자·역할과는 다른 개념입니다[10]. 멤버 계정은 한 번에 한 조직에만 속하고, 어느 계정이 관리 계정인지는 바꿀 수 없습니다[10]. 서비스 제어 정책 (SCP) 을 루트에 붙여도 관리 계정에는 적용되지 않습니다[10].

AWS 리소스 이름 (ARN) 은 `arn:partition:service:region:account:resource` 모양이고, `account` 부분에 하이픈 없는 계정 ID 가 들어갑니다[11]. partition 은 표준 리전이 `aws`, 중국(베이징) 리전이 `aws-cn` 이며, partition 이 다른 계정 사이에는 접근을 위임할 수 없습니다[11]. 다른 계정의 사용자가 역할을 쓰게 하려면 역할 신뢰 정책의 `Principal` 에 그 계정을 적고, 사용자가 역할을 쓰는 동안에는 원래 사용자 권한이 멈춥니다[12].

### Google Cloud

Google Cloud 의 리소스 계층은 맨 위 조직 (organization) 아래에 선택 사항인 폴더 (folder), 그 아래 프로젝트 (project), 프로젝트 안의 서비스 리소스로 이루어지고, 맨 위를 뺀 모든 리소스의 부모는 정확히 하나입니다[13]. 조직 리소스에는 조직 ID, Workspace 나 Cloud Identity 기본 도메인에서 온 표시 이름, 만든 시각과 바꾼 시각, 소유자가 있습니다[13]. 소유자는 Directory API 의 Google Workspace 고객 ID 이고, 조직을 만들 때 정하며 바꿀 수 없습니다[13]. 아래는 문서의 조직 리소스 예시에서 두 식별자만 추린 것입니다.

```json
{
  "name": "organizations/34739118321",
  "owner": { "directoryCustomerId": "C012ba234" }
}
```

Workspace 나 Cloud Identity 계정 하나는 조직 리소스 하나와만 연결되고, 그 계정의 사용자가 프로젝트를 만들면 조직 리소스가 자동으로 생깁니다[13]. 조직이 생긴 뒤 그 도메인의 관리 대상 사용자는 조직에 속하지 않은 프로젝트를 만들 수 없습니다[13]. 무료 체험·무료 등급 사용자가 만든 프로젝트만 조직 없이 계층 맨 위에 올 수 있습니다[13].

프로젝트의 식별자는 둘입니다. 프로젝트 ID (`projectId`) 는 만들 때 사람이 정하고, 프로젝트 번호 (`projectNumber`) 는 자동으로 붙는 읽기 전용 값입니다[13]. 표시 이름은 바꿀 수 있고 프로젝트 ID 와 다릅니다[13]. 프로젝트의 수명 상태는 `ACTIVE` 나 `DELETE_REQUESTED` 같은 값이고, 새 프로젝트는 만든 사람에게 owner 역할을 주는 IAM 정책으로 시작합니다[13].

### Google Workspace

Google Workspace 나 Cloud Identity 에 가입하면 계정에 고유한 고객 ID 가 붙습니다[14]. 관리 콘솔의 메뉴 > Account > Account settings > Profile 에서 Customer ID 로 확인하고, 도메인 설정 관리자 권한이 필요합니다[14]. 이 고객 ID 가 Google Cloud 조직 리소스의 소유자 값(`directoryCustomerId`)이므로[13], Workspace 로그와 Google Cloud 로그가 같은 조직의 것인지 이 값으로 맞춰 볼 수 있습니다.

### 업무용 SaaS

Slack 감사 로그는 개별 워크스페이스가 아니라 Enterprise 조직 전체에서 동작하므로, 감사 로그 API 를 부르는 토큰은 앱을 조직에 설치해서 받아야 하고 범위는 `auditlogs:read` 입니다[15]. 이벤트의 `context` 는 행위가 일어난 곳이고 항상 워크스페이스나 Enterprise 가운데 하나입니다[15]. ID 는 첫 글자로 종류가 갈려서 E 는 Enterprise, T 는 워크스페이스, W 는 사용자, C 는 채널, F 는 파일, A 는 앱입니다[15].

GitHub Enterprise Cloud 의 엔터프라이즈 감사 로그는 엔터프라이즈 계정이 소유한 모든 조직의 행동을 모아 보여 줍니다[16].

### 경계 위에서 한꺼번에 모으는 기록

여러 계정·구독·프로젝트를 한 번에 기록하는 설정이 있으면 조사 범위를 한꺼번에 덮을 수 있지만, 설정마다 빠지는 곳이 있습니다.

AWS 조직 트레일 (organization trail) 은 관리 계정이나 위임 관리자가 만들고, 관리 계정과 모든 멤버 계정의 이벤트를 기록합니다[17]. 멤버 계정 사용자는 조직 트레일을 볼 수는 있지만 지우거나, 기록을 켜고 끄거나, 기록할 이벤트 종류를 바꿀 수 없습니다[17]. 기본으로는 관리 계정만 트레일의 S3 버킷과 로그에 접근할 수 있습니다[17]. 로그 파일은 아래 경로처럼 조직 ID 폴더 아래 계정 ID 폴더에 나뉘어 쌓입니다[18].

```text
amzn-s3-demo-bucket/prefix_name/AWSLogs/O-ID/Account ID/CloudTrail/Region/YYYY/MM/DD/file_name.json.gz
```

계정이 조직을 떠나면 그 계정에서 조직 트레일이 사라지고 그 뒤 이벤트는 기록되지 않지만, 떠나기 전에 만든 로그 파일은 버킷의 그 계정 폴더에 남습니다[17]. 콘솔로 만든 조직 트레일은 다중 리전이고, 홈 리전이 사용자가 직접 켜야 하는 opt-in 리전이면 그 리전을 켠 멤버 계정만 활동을 보냅니다[17]. 모든 partition 을 기록하려면 partition 마다 조직 트레일을 따로 만들어야 합니다[17].

Azure 는 관리 그룹에 진단 설정을 만들면 그 관리 그룹과 아래 모든 관리 그룹의 활동 로그 이벤트를 내보냅니다[9]. 테넌트 수준과 관리 그룹 수준의 활동 로그는 Azure Resource Manager 이벤트만 담고, ARM 을 거치지 않고 리소스 공급자가 직접 만든 이벤트는 구독 수준에만 있습니다[9]. 테넌트 수준 활동 로그는 보통 항목이 적지만 관리 그룹이나 구독을 만든 일 같은 이벤트가 남을 수 있습니다[9]. 관리 그룹과 구독 진단 설정이 겹칠 때 생기는 중복은 [기록은 어디에 남나](where-records-live.md)에서 다룹니다.

Google Cloud 는 조직이나 폴더에 집계 싱크 (aggregated sink) 를 만들어 그 아래 리소스의 로그 항목까지 한 목적지로 보냅니다[19]. 가로채는 (intercepting) 집계 싱크에 걸린 항목은 아래 리소스의 싱크로 가지 않지만, 항목이 생긴 리소스의 `_Required` 싱크로는 항상 갑니다[19].

## 읽는 법

레코드 한 줄에는 "어느 경계의 로그로 모였는가" 를 나타내는 값과 "행위자가 어느 경계에 속하는가" 를 나타내는 값이 따로 있습니다. 두 값이 다르면 경계를 넘은 접근이므로, 두 값을 나란히 놓고 읽습니다.

1. **레코드가 모인 경계를 읽습니다.** 통합 감사 로그는 `OrganizationId`[2], Azure 활동 로그는 `subscriptionId` 와 `resourceId`[7], CloudTrail 은 `recipientAccountId`[20], Google Workspace 보고서 API 는 `id.customerId`[21], Slack 은 `context.location`[15] 을 봅니다. Google Cloud 감사 로그는 `logName` 의 앞부분이 `projects/PROJECT_ID`, `folders/FOLDER_ID`, `billingAccounts/BILLING_ACCOUNT_ID`, `organizations/ORGANIZATION_ID` 가운데 무엇인지로 로그를 가진 경계를 알 수 있습니다[22]. 뒷부분(`activity`·`data_access` 같은 종류)은 [기록은 어디에 남나](where-records-live.md)에서 다룹니다.
2. **행위자가 속한 경계를 읽습니다.** Entra 로그인 로그는 홈 테넌트 (home tenant), CloudTrail 은 `userIdentity.accountId`, Google Workspace 는 `actor.email` 의 도메인을 봅니다.
3. **두 값을 비교합니다.** 아래에서 서비스별로 비교하는 방법을 봅니다.

**Entra ID.** 로그인 로그의 홈 테넌트는 사용자 신원을 가진 테넌트이고, 리소스 테넌트 (resource tenant) 는 로그인 대상 리소스를 가진 테넌트입니다[23]. 테넌트 밖 사용자가 리소스에 어떻게 접근하는지 보려면 홈 테넌트와 리소스 테넌트가 다른 항목을 고르면 됩니다[23]. 필드 이름은 Microsoft Graph 베타 signIn 리소스에서 `homeTenantId`·`homeTenantName`·`resourceTenantId`·`crossTenantAccessType` 이고[24], Log Analytics 의 `SigninLogs` 표에서는 `HomeTenantId`·`HomeTenantName`·`ResourceTenantId`·`CrossTenantAccessType` 입니다[25]. `crossTenantAccessType` 의 값 목록에는 `none`·`b2bCollaboration`·`b2bDirectConnect` 등이 있고, 경계를 넘지 않은 로그인이면 `none` 입니다[24]. 아래는 필드 이름만 문서에서 가져와 만든 예시입니다.

```json
{
  "userDisplayName": "John",
  "homeTenantId": "bbbbcccc-1111-dddd-2222-eeee3333ffff",
  "resourceTenantId": "aaaabbbb-0000-cccc-1111-dddd2222eeee",
  "crossTenantAccessType": "b2bCollaboration",
  "ipAddress": "203.0.113.24"
}
```

이 예시는 다른 테넌트에 신원을 둔 사용자가 B2B 협업으로 `aaaabbbb-…` 테넌트의 리소스에 로그인한 기록으로 읽습니다. 교차 테넌트 로그인에서는 개인정보 약속 때문에 홈 테넌트 이름을 채우지 않습니다[23]. `homeTenantId` 는 관리 ID 와 서비스 주체 로그인에는 해당하지 않습니다[24][25]. 교차 테넌트 접근 유형의 다른 값(`microsoftSupport`·`serviceProvider`)은 [책임 공유와 조사 범위](shared-responsibility.md)에서 다룹니다.

**AWS.** `userIdentity.accountId` 는 요청에 권한을 준 주체를 가진 계정이고, 임시 보안 자격 증명으로 한 요청이면 그 자격 증명을 얻는 데 쓴 IAM 사용자나 역할을 가진 계정입니다[26]. `recipientAccountId` 는 이벤트를 받은 계정이고, 다른 계정의 리소스에 접근하면 `accountId` 와 달라질 수 있습니다[20]. 계정 222222222222 의 사용자가 계정 111111111111 의 KMS 키로 `Encrypt` 를 부르면 CloudTrail 은 두 계정에 이벤트를 하나씩 보내고, 두 이벤트는 `sharedEventID` 가 같지만 `eventID` 와 `recipientAccountId` 가 다릅니다[20]. 아래는 필드 이름과 상황을 문서에서 가져와 만든 예시입니다.

```json
[
  {
    "eventSource": "kms.amazonaws.com",
    "eventName": "Encrypt",
    "userIdentity": { "accountId": "222222222222" },
    "recipientAccountId": "222222222222",
    "eventID": "11111111-aaaa-4bbb-8ccc-000000000001",
    "sharedEventID": "22222222-dddd-4eee-8fff-000000000002"
  },
  {
    "eventSource": "kms.amazonaws.com",
    "eventName": "Encrypt",
    "userIdentity": { "accountId": "222222222222" },
    "recipientAccountId": "111111111111",
    "eventID": "33333333-aaaa-4bbb-8ccc-000000000003",
    "sharedEventID": "22222222-dddd-4eee-8fff-000000000002"
  }
]
```

두 번째 레코드는 키를 가진 계정 111111111111 이 받은 사본이고, `userIdentity.accountId` 와 `recipientAccountId` 가 다르므로 다른 계정이 이 계정의 키를 쓴 기록으로 읽습니다. 호출한 계정과 리소스를 가진 계정이 같으면 이벤트는 하나만 가고 `sharedEventID` 는 없습니다[20]. 두 계정의 트레일을 따로 받았다면 `sharedEventID` 로 짝을 맞춥니다.

**Google Workspace.** 보고서 API 활동 레코드에서 `id.customerId` 는 Google Workspace 계정의 고유 식별자이고, `ownerDomain` 은 이벤트가 영향을 준 도메인(관리 콘솔의 도메인이나 Drive 문서 소유자의 도메인)입니다[21]. `actor.email` 은 행위자의 기본 메일 주소인데, 메일 주소가 없는 행위자면 빠질 수 있습니다[21]. `actor.profileId` 는 행위자가 Workspace 사용자가 아니면 없을 수 있고, 자리 표시 값 `105250506097979753968` 이 들어갈 수도 있습니다[21]. `actor.email` 의 도메인과 `ownerDomain` 이 다르면 다른 조직 사용자가 이 조직의 자료에 손댄 기록일 가능성이 있으므로 이벤트 이름과 함께 확인합니다. `id.time` 의 형식은 [클라우드 로그의 시각](../logging/timestamps.md)에서 다룹니다.

## 포렌식에서 중요한 점

### 증명하는 것

`OrganizationId`·`subscriptionId`·`recipientAccountId`·`id.customerId`·`logName` 앞부분은 레코드가 어느 경계의 로그로 모였는지를 보여 줍니다[2][7][20][21][22]. 행위자 쪽 값(`homeTenantId`, `userIdentity.accountId`)과 다르면 경계를 넘은 접근이 있었다는 근거가 됩니다[23][20]. AWS 조직 트레일 버킷에 어떤 계정의 폴더가 있으면, 그 계정이 조직에 있던 기간의 이벤트가 그 폴더에 기록된 것입니다[17].

### 증명하지 못하는 것

경계 식별자로는 로그가 모인 곳만 알 수 있고, 행위자가 누구인지는 알 수 없습니다. 같은 테넌트의 로그라도 게스트나 다른 테넌트의 지원 담당자가 한 일이 섞여 있을 수 있으므로 행위자 쪽 값을 따로 읽어야 합니다. 조직 트레일에 어떤 계정 폴더가 없거나 비어 있다는 사실만으로는 그 계정에 활동이 없었다고 할 수 없습니다. 계정이 조직을 떠난 뒤의 활동은 조직 트레일에 기록되지 않고[17], opt-in 홈 리전 트레일은 그 리전을 켜지 않은 멤버 계정의 활동을 받지 않기 때문입니다[17].

### 시각

경계의 소속은 시간에 따라 바뀌므로, 조사 기간의 소속을 현재 상태로 짐작하지 않습니다. AWS 계정은 조직을 떠나고 들어올 수 있고[17], Azure 구독은 다른 디렉터리로 옮길 수 있으며 그러면 Azure RBAC 로 역할을 받은 사용자와 클래식 구독 관리자가 접근을 잃습니다[3]. Google Cloud 프로젝트에는 `ACTIVE`·`DELETE_REQUESTED` 같은 수명 상태가 있어서[13], 조사 시점의 상태가 사건 당시와 다를 수 있습니다. 소속이 바뀐 시각은 관리 작업 기록에서 찾습니다. Azure 에서는 구독과 관리 그룹을 만든 일 같은 이벤트가 테넌트 수준 활동 로그에 남을 수 있습니다[9]. 레코드 시각 필드의 해석은 [클라우드 로그의 시각](../logging/timestamps.md)에서 다룹니다.

## 함정

- AWS 콘솔의 이벤트 기록 (Event history) 은 로그인한 계정의 이벤트만 보여 줍니다[17]. 관리 계정으로 로그인하면 관리 계정의 최근 90일 관리 이벤트만 보이고 멤버 계정 이벤트는 보이지 않습니다[17]. 관리 계정 화면에 멤버 계정 활동이 없다고 "활동 없음" 으로 쓰지 않습니다.
- Azure 구독을 다른 디렉터리로 옮기면 이전 디렉터리에서 받은 역할 할당으로는 더 이상 접근할 수 없습니다[3]. 현재 역할 할당 목록만 보고 과거에 누가 접근할 수 있었는지 판단하지 말고, 활동 로그의 역할 할당 기록으로 확인합니다. 권한 변화를 따라가는 방법은 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md)에서 다룹니다.
- 루트 관리 그룹에는 기본으로 접근할 수 있는 사람이 없고, Entra 전역 관리자 (Global Administrator) 만 스스로 권한을 올려 접근할 수 있습니다[6]. 권한을 올려 루트 관리 그룹에 접근하면 다른 사용자에게 어떤 Azure 역할이든 줄 수 있고[6], 모든 구독과 관리 그룹은 루트 관리 그룹 아래에 모입니다[6]. 그래서 Entra 쪽 역할이 Azure 구독 전체의 권한으로 이어질 수 있습니다. Sigma 규칙은 이 권한 올리기를 활동 로그의 `operationName` 이 `MICROSOFT.AUTHORIZATION/ELEVATEACCESS/ACTION` 인 레코드로 찾습니다[27]. 구독 수준 활동 로그만 보지 말고 테넌트 수준 활동 로그도 함께 받습니다.
- Azure 활동 로그의 `resourceId` 는 이벤트에 따라 `/subscriptions/…/resourcegroups/`, `/subscriptions/…/resourceGroups/`, `/SUBSCRIPTIONS/…/RESOURCEGROUPS/` 처럼 대소문자가 다르게 나옵니다[7]. 구독 ID 나 리소스 그룹 이름으로 레코드를 모을 때는 대소문자를 구분하지 않고 비교합니다.
- 정부용·국가별 클라우드는 관리 주소가 다릅니다. ARM 주소는 전역 Azure 가 `https://management.azure.com`, Azure Government 가 `https://management.usgovcloudapi.net/`, 21Vianet 이 운영하는 Azure 가 `https://management.chinacloudapi.cn` 입니다[28]. 수집 도구가 전역 주소만 부르면 이런 테넌트의 로그는 받지 못합니다. AWS 도 partition 이 다르면 조직 트레일을 partition 마다 따로 둡니다[17].
- Google Cloud 프로젝트 ID, 프로젝트 번호, 표시 이름은 서로 다른 값입니다[13]. 로그와 설정 자료에서 어느 값이 쓰였는지 확인하고 맞춥니다.
- Entra B2B 게스트가 이 테넌트의 리소스에 로그인한 기록은 리소스 테넌트의 로그인 로그에서 홈 테넌트가 리소스 테넌트와 다른 항목으로 찾습니다[23]. 이런 항목에는 홈 테넌트 이름이 비어 있으므로 홈 테넌트 ID 로 소속을 판별합니다[23].

## 도구

수집 도구는 대부분 "로그인한 계정이 볼 수 있는 경계" 를 기본 범위로 삼으므로, 도구를 돌리기 전에 조사 대상 경계와 수집 계정의 권한을 맞춰 봐야 합니다.

- Microsoft-Extractor-Suite 의 `Get-ActivityLogs` 는 `https://management.azure.com/subscriptions` 로 구독 목록을 받은 뒤 구독마다 활동 로그를 받습니다[29]. 기본 범위는 로그인한 계정에 연결된 모든 구독이고 기본 기간은 오늘부터 89일 전까지입니다[29]. `Get-DirectoryActivityLogs` 는 테넌트 수준 활동 로그를 받고 기본 기간은 90일입니다[29].
- Untitled Goose Tool 은 설정 파일에 테넌트 ID(`tenant`)와 구독 ID(`subscriptionid`)를 적고, 구독 ID 기본값 `All` 은 모든 구독을 뜻합니다[30]. 정부용 테넌트는 `gcc`·`gcc_high` 설정으로 구분합니다[30].
- DFIR-O365RC 는 테넌트에 앱을 등록해 로그를 받고, Azure 구독의 로그까지 받으려면 앱을 만들거나 고칠 때 `-subscriptions` 스위치를 붙여야 합니다[31].
- Invictus-AWS 는 리전 단위로 실행해 결과를 리전 폴더에 저장하고, S3·CloudTrail 로그는 `regionless` 인자로 정한 첫 리전에서만 받습니다[32].

도구별 수집 절차는 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md)와 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md)에서 다룹니다. 수집할 경계를 정하는 순서는 [조사 절차](../../03-techniques/acquisition/investigation-process.md)에서 다룹니다.

함께 볼 페이지: [책임 공유와 조사 범위](shared-responsibility.md), [기록은 어디에 남나](where-records-live.md), [클라우드 계정과 역할](../identity/users-roles.md), [페더레이션과 SSO](../identity/federation-sso.md), [보관 기간과 라이선스](../logging/retention-licensing.md).

## 참고 문헌

1. Microsoft, "What is Microsoft Entra?", Microsoft Learn (2026-06-18 갱신). https://learn.microsoft.com/en-us/entra/fundamentals/whatis
2. Microsoft, "Office 365 Management Activity API schema", Microsoft Learn (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
3. Microsoft, "Associate or add an Azure subscription to your Microsoft Entra tenant", Microsoft Learn (2026-06-19 갱신). https://learn.microsoft.com/en-us/entra/fundamentals/how-subscriptions-associated-directory
4. Microsoft, "Understand and manage the properties of B2B guest users", Microsoft Learn (2026-03-20 갱신). https://learn.microsoft.com/en-us/entra/external-id/user-properties
5. Microsoft, "What is Azure Resource Manager?", Microsoft Learn (2026-08-04 갱신). https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview
6. Microsoft, "What are Azure management groups?", Microsoft Learn (2025-07-21 갱신). https://learn.microsoft.com/en-us/azure/governance/management-groups/overview
7. Microsoft, "Azure Activity Log event schema" (ms.date 2026-03-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
8. Microsoft, "Azure resource logs supported services and schemas" (ms.date 2025-05-21). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs-schema.md
9. Microsoft, "Activity log in Azure Monitor" (ms.date 2026-05-04). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
10. AWS, "Terminology and concepts for AWS Organizations", AWS Organizations User Guide. https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html
11. AWS, "IAM identifiers", AWS IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html
12. AWS, "Access for an IAM user in another AWS account that you own", AWS IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios_aws-accounts.html
13. Google Cloud, "About resource hierarchy", Resource Manager (2026-09-18 갱신). https://cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy
14. Google, "Find your customer ID", Google Workspace Admin Help (2026-09-18 갱신). https://support.google.com/a/answer/10070793
15. Slack, "Monitoring your workspace with audit logs". https://api.slack.com/admins/audit-logs
16. GitHub, "Accessing the audit log for your enterprise", github/docs 저장소. https://github.com/github/docs/blob/main/content/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/accessing-the-audit-log-for-your-enterprise.md
17. AWS, "Creating a trail for an organization", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/creating-trail-organization.html
18. AWS, "Getting and viewing your CloudTrail log files", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/get-and-view-cloudtrail-log-files.html
19. Google Cloud, "Routing and storage overview" (2026-09-25 갱신). https://cloud.google.com/logging/docs/routing/overview
20. AWS, "CloudTrail record contents for management, data, and network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
21. Google, "Method: activities.list", Admin SDK Reports API (2026-09-09 갱신). https://developers.google.com/workspace/admin/reports/v1/reference/activities/list
22. Google Cloud, "Cloud Audit Logs overview" (2026-09-25 갱신). https://cloud.google.com/logging/docs/audit
23. Microsoft, "Learn about the sign-in log activity details" (ms.date 2026-03-04). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
24. Microsoft, "signIn resource type", Microsoft Graph beta, Microsoft Learn (2025-11-28 갱신). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
25. Microsoft, "SigninLogs", Azure Monitor Logs 표 참조, Microsoft Learn (2026-08-27 갱신). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
26. AWS, "CloudTrail userIdentity element", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
27. SigmaHQ, "Azure Subscription Permission Elevation Via ActivityLogs" 규칙. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_subscription_permissions_elevation_via_activitylogs.yml
28. Microsoft, "Azure control plane and data plane", Microsoft Learn (2026-02-27 갱신). https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/control-plane-and-data-plane
29. Invictus Incident Response, Microsoft-Extractor-Suite(Get-AzureActivityLogs.ps1, Get-AzureDirectoryActivityLogs.ps1). https://github.com/invictus-ir/Microsoft-Extractor-Suite
30. CISA, Untitled Goose Tool(goosey/conf.py). https://github.com/cisagov/untitledgoosetool
31. ANSSI, DFIR-O365RC(README). https://github.com/ANSSI-FR/DFIR-O365RC
32. Invictus Incident Response, Invictus-AWS(logs.py). https://github.com/invictus-ir/Invictus-AWS
