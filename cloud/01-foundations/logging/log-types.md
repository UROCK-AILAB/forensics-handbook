---
title: "로그의 종류"
parent: "기반 · 로그 체계"
nav_order: 80
---

# 로그의 종류 (관리·데이터·로그인·흐름)

클라우드 로그는 설정을 바꾼 관리 작업, 자원 안 데이터를 읽고 쓴 작업, 로그인, 네트워크 연결의 네 갈래로 나뉘고, 갈래마다 로그 이름과 필드, 기본으로 켜지는지가 다릅니다.

## 이 형식을 쓰는 아티팩트

이 쪽은 파일 형식이 아니라 "레코드 한 줄이 어느 갈래에 속하고, 그 갈래에서 무엇을 말할 수 있는가" 를 다룹니다. 갈래를 어디에 저장하는지와 보관 기간은 [기록은 어디에 남나](../model/where-records-live.md)에서, 요금제별 보관 기간은 [보관 기간과 라이선스](retention-licensing.md)에서 다룹니다.

| 갈래 | 기록하는 일 | Microsoft 365·Entra | AWS | Azure | Google Cloud | Google Workspace·SaaS |
|---|---|---|---|---|---|---|
| 관리 (제어 평면, control plane) | 자원을 만들고 바꾸고 지우는 일, 권한·설정 변경 | [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md)의 관리 작업, [Entra 감사 로그](../../02-artifacts/m365/entra-logs/index.md) | [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md) 관리 이벤트 | [활동 로그](../../02-artifacts/azure/activity-log.md) | [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md) Admin Activity·System Event | [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md) |
| 데이터 (데이터 평면, data plane) | 자원 안의 데이터를 읽고 쓰는 일 | 통합 감사 로그의 파일·메일 작업 | CloudTrail 데이터 이벤트·네트워크 활동 이벤트, [S3 서버 접근 로그](../../02-artifacts/aws/s3-access-logs.md) | [리소스 로그](../../02-artifacts/azure/resource-logs.md) | Cloud Audit Logs Data Access | Drive·Gmail 로그 이벤트 |
| 로그인 (신원, identity) | 인증 시도와 결과 | Entra 로그인 로그 | CloudTrail `ConsoleLogin` | Entra 로그인 로그 | — | [로그인 기록](../../02-artifacts/google-workspace/login-audit.md), [Okta 시스템 로그](../../02-artifacts/saas/okta.md), [Slack 액세스 로그](../../02-artifacts/saas/slack.md) |
| 흐름 (네트워크, flow) | 주소·포트·프로토콜 단위의 연결 요약 | — | [VPC 흐름 로그](../../02-artifacts/aws/vpc-flow-logs.md) | [NSG·VNet 흐름 로그](../../02-artifacts/azure/flow-logs.md) | [VPC 흐름 로그](../../02-artifacts/gcp/vpc-flow-logs.md) | — |

Microsoft 365 통합 감사 로그는 관리 작업과 데이터 작업이 한 로그에 섞여 있어서, 갈래를 레코드마다 `Operation` 과 `Workload` 로 가립니다[13]. Entra ID 의 로그인·감사 로그는 통합 감사 로그와 따로 보관됩니다[20].

## 구조

### 관리

AWS 는 계정 안 자원에 대한 관리 작업을 관리 이벤트 (management events) 로 기록하고, 이것을 제어 평면 작업이라고도 부릅니다[1]. `AttachRolePolicy`·`CreateSubnet`·`CreateTrail` 같은 API 호출이 여기에 들고, 콘솔 로그인(`ConsoleLogin`)처럼 API 가 아닌 이벤트도 관리 이벤트로 남습니다[1]. 레코드의 `eventCategory` 값은 `Management` 입니다[2]. 트레일에서는 관리 이벤트를 읽기(Read)와 쓰기(Write)로 나눠 고르거나 KMS·RDS Data API 이벤트를 뺄 수 있으며, 기본 설정은 KMS·RDS Data API 이벤트를 모두 포함합니다[4]. KMS 의 `Encrypt`·`Decrypt`·`GenerateDataKey` 는 KMS 이벤트의 99% 넘게 차지하며 읽기 이벤트로 기록됩니다[4].

Azure 는 가상 머신 만들기, Key Vault 접근 정책 바꾸기 같은 제어 평면 작업을 활동 로그 (activity log) 에 남깁니다[8]. 활동 로그의 범주는 Administrative, Service Health, Resource Health, Alert, Autoscale, Recommendation, Security, Policy 여덟 가지입니다[9]. 이 가운데 Administrative 가 Resource Manager 를 거친 만들기·바꾸기·지우기·action 작업과 역할 기반 접근 제어 변경을 담습니다[9]. 구독 단위 활동 로그와 따로 관리 그룹·구독 생성 같은 일을 담는 테넌트 단위 활동 로그가 있는데, 테넌트 단위 활동 로그는 다른 REST API 끝점으로 읽습니다[8].

Google Cloud 는 자원 구성·메타데이터를 바꾸는 호출을 Admin Activity 감사 로그에, Google 시스템이 스스로 구성을 바꾼 일을 System Event 감사 로그에 남기고, 둘 다 끌 수 없습니다[11]. 로그 이름은 각각 `cloudaudit.googleapis.com%2Factivity`, `cloudaudit.googleapis.com%2Fsystem_event` 로 끝납니다[12].

Microsoft 365 통합 감사 로그에서 Exchange 관리 작업은 `Operation` 에 실행한 cmdlet 이름이, `ObjectId` 에 cmdlet 이 바꾼 개체 이름이 남습니다[13]. Google Workspace 는 관리 콘솔 작업을 Admin 로그 이벤트로 남기고, Reports API 에서는 `applicationName` 이 `admin` 입니다[16][30].

### 데이터

AWS 데이터 이벤트 (data events) 는 자원 위·안에서 한 작업이고, S3 객체의 `GetObject`·`DeleteObject`·`PutObject`, Lambda 함수 호출(`Invoke`)이 예입니다[1]. 양이 많은 작업이고, 트레일을 만들어도 기본으로 기록하지 않으며, 켜면 요금이 붙습니다[1][5]. `eventCategory` 값은 `Data` 입니다[2]. VPC 엔드포인트를 거친 API 호출은 네트워크 활동 이벤트 (network activity events) 로 따로 남고, `eventCategory` 가 `NetworkActivity`, `eventType` 이 `AwsVpceEvents` 입니다[2][6]. 이것도 기본으로 꺼져 있고 요금이 붙습니다[1]. S3 서버 접근 로그 (server access logs) 는 CloudTrail 과 따로 남는 로그입니다[7].

Azure 리소스 로그 (resource logs) 는 Key Vault 비밀 읽기나 데이터베이스 요청처럼 자원 안에서 한 데이터 평면 작업을 담습니다[8]. 리소스 로그는 기본으로 모이지 않고, 자원마다 진단 설정 (diagnostic setting) 을 만들어야 모입니다[10].

Google Cloud 의 Data Access 감사 로그는 자원 구성·메타데이터를 읽는 호출과, 사용자 데이터를 만들고 바꾸고 읽는 호출을 담고, BigQuery 를 빼면 기본으로 꺼져 있습니다[11]. 로그 이름은 `%2Fdata_access` 로 끝납니다[12]. 보안 정책 때문에 접근을 막은 일은 Policy Denied 감사 로그(`%2Fpolicy`)에 남고, 이 로그는 기본으로 생성됩니다[11][12].

Microsoft 365 에서 SharePoint·OneDrive 파일 작업은 통합 감사 로그의 `ObjectId` 에 파일·폴더 전체 경로를 남깁니다[13]. 메일 열람은 Exchange 사서함 감사의 `MailItemsAccessed` 로 남고, Office 365·Microsoft 365 E3·E5 사용자에게 기본으로 켜집니다[14]. Google Workspace 에서는 Drive 로그 이벤트와 Gmail 로그 이벤트가 이 갈래에 듭니다[16].

### 로그인

Entra ID 로그인 로그는 대화형 사용자, 비대화형 사용자, 서비스 주체, 관리 ID 의 네 종류로 나뉩니다[18]. Microsoft Graph beta 의 로그인 레코드에서는 `signInEventTypes` 값 `interactiveUser`·`nonInteractiveUser`·`servicePrincipal`·`managedIdentity` 로 종류를 가립니다[19]. 옛 로그인 로그 화면은 대화형 사용자 로그인만 보여 줍니다[18]. 통합 감사 로그에도 Entra 레코드가 들어오지만[13] 보관은 Entra 로그와 따로 정해집니다[20].

AWS 콘솔 로그인은 `eventType` 이 `AwsConsoleSignIn`[2], 이벤트 이름이 `ConsoleLogin`[1] 인 CloudTrail 레코드로 남습니다. 앞에서 본 것처럼 이 레코드는 관리 이벤트로 분류되므로, AWS 에서는 로그인과 관리 작업을 같은 로그에서 봅니다[1].

Google Workspace 의 User 로그 이벤트(예전 이름 Login audit log)는 Reports API 의 `applicationName` 이 `login` 이고, `login_success`·`login_failure`·`login_challenge`·`suspicious_login` 같은 이벤트와 `login_type`·`is_suspicious` 같은 파라미터를 담습니다[16][17]. Okta 는 시스템 로그 (System Log) 의 `eventType` 으로 로그인을 가르고, 로그인해 세션을 받은 일은 `user.session.start` 입니다[21]. Slack 의 액세스 로그 (`team.accessLogs`) 는 로그인 하나가 한 줄이 아니라 사용자·IP·사용자 에이전트 조합 하나가 한 줄이고, 그 조합의 첫 접속(`date_first`)과 마지막 접속(`date_last`)을 유닉스 초로 적습니다[22]. 이 조합에는 실제 로그인뿐 아니라 접속할 때 따라오는 API 호출도 들어갑니다[22].

### 흐름

흐름 로그는 패킷 내용 없이 연결을 주소·포트·프로토콜 단위로 묶어 요약합니다. 세 클라우드 모두 따로 켜야 남습니다[23][25][27].

| 항목 | AWS VPC 흐름 로그 | Azure VNet 흐름 로그 | Google Cloud VPC 흐름 로그 |
|---|---|---|---|
| 레코드 모양 | 공백으로 구분한 한 줄 문자열[23] | JSON, `flowTuples` 는 쉼표로 구분한 문자열[25] | Cloud Logging 항목, `connection` 필드에 5-튜플[28] |
| 묶는 구간 | 최대 10분(기본) 또는 1분, Nitro 인스턴스는 늘 1분 이하[23] | 진행 중인 흐름은 5분마다 통계(`C` 상태)[25] | 5초(기본)·30초·1분·5분·10분·15분[27] |
| 모든 흐름이 남나 | 남지만 `log-status` 가 `SKIPDATA` 인 구간은 일부 빠짐[23] | 흐름 상태 `B`·`C`·`E`·`D` 로 시작·진행·끝·거부를 구분[25] | 패킷을 표본 추출함. 2차 표본 비율 기본값은 Compute Engine API 로 만든 설정 50%, Network Management API 로 만든 설정 100%[27] |
| 형식 변경 | 만든 뒤 바꿀 수 없음[24] | — | — |

AWS 기본 형식은 버전 2 필드를 `version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status` 순서로 적습니다[23]. `start`·`end` 는 구간 안 첫 패킷과 마지막 패킷을 받은 유닉스 초이고, `action` 은 `ACCEPT` 또는 `REJECT` 입니다[23]. 아래는 이 순서대로 만든 예시입니다.

```text
2 123456789012 eni-0a1b2c3d4e5f67890 203.0.113.25 192.0.2.10 49152 443 6 12 1840 1790000000 1790000060 ACCEPT OK
```

Azure NSG 흐름 로그는 2027년 9월 30일에 퇴역하고 지금은 새로 만들 수 없습니다[26]. 퇴역한 뒤 Azure 는 NSG 흐름 로그 리소스를 지우지만, 저장소에 이미 쌓인 레코드는 지우지 않고 설정한 보관 정책을 따릅니다[26]. 2026년 9월 문서 기준입니다.

Google Cloud 흐름 레코드의 기본 필드는 패킷 헤더에서 바로 가져오고, 메타데이터 필드는 근삿값이라 빠지거나 틀릴 수 있습니다[28]. `reporter` 필드는 흐름을 보고한 쪽을 알려 주고, VM·서버리스 끝점에서는 보내는 쪽 `SRC` 또는 받는 쪽 `DEST`, Cloud Interconnect·Cloud VPN 같은 게이트웨이에서는 `SRC_GATEWAY` 또는 `DEST_GATEWAY` 입니다[28].

## 읽는 법

레코드 한 줄을 받으면 먼저 갈래를 정합니다. 서비스마다 갈래를 알려 주는 필드가 있습니다.

| 서비스 | 갈래를 가리는 필드 | 값 |
|---|---|---|
| AWS CloudTrail | `eventCategory` | `Management`·`Data`·`NetworkActivity`[2] |
| AWS CloudTrail | `eventType` | 콘솔 로그인 `AwsConsoleSignIn`, 네트워크 활동 `AwsVpceEvents`[2] |
| Azure 활동 로그 | `category` | `Administrative`·`Policy`·`Security` 등 여덟 범주[9] |
| Google Cloud | `logName` 끝부분 | `activity`·`system_event`·`data_access`·`policy`[12] |
| Entra ID 로그인 | `signInEventTypes`(Graph beta) | `interactiveUser`·`nonInteractiveUser`·`servicePrincipal`·`managedIdentity`[19] |
| Google Workspace | Reports API `applicationName` | `admin`·`login`·`drive`·`token` 등[30] |

아래는 CloudTrail 레코드에서 갈래를 가리는 필드만 추려 만든 예시입니다. `eventCategory` 가 `Data` 라서, 이 레코드는 데이터 이벤트를 켠 트레일이나 이벤트 데이터 저장소에서만 나옵니다.

```json
{
  "eventSource": "s3.amazonaws.com",
  "eventName": "GetObject",
  "eventCategory": "Data",
  "recipientAccountId": "123456789012"
}
```

갈래를 정한 다음에는 그 갈래가 조사 기간에 켜져 있었는지를 확인합니다. 서비스별로 기본으로 켜지는 로그와 설정을 확인하는 곳은 [기록은 어디에 남나](../model/where-records-live.md)의 "기본으로 남는 것과 켜야 남는 것" 표에 있습니다. 레코드 안 필드를 푸는 방법은 [JSON 로그 읽기](json-logs.md)에서, 시각 필드는 [클라우드 로그의 시각](timestamps.md)에서, IP·사용자 에이전트는 [IP·사용자 에이전트·위치 정보](ip-ua-geo.md)에서 다룹니다.

## 포렌식에서 중요한 점

**증명하는 것.** 관리 로그는 누가 언제 어떤 설정을 바꿨는지 보여 줍니다. 로그인 로그는 어느 계정으로 인증을 시도했고 결과가 어땠는지 보여 줍니다. 흐름 로그는 어느 주소·포트 사이에 연결이 있었고 바이트가 얼마나 오갔는지 보여 줍니다[23].

**증명하지 못하는 것.** 관리 로그만으로는 데이터를 읽었는지 말할 수 없습니다. AWS 데이터 이벤트, Azure 리소스 로그, Google Cloud Data Access 감사 로그는 모두 기본으로 꺼져 있습니다[1][10][11]. 데이터 로그가 꺼져 있던 기간에 읽은 기록이 없다는 사실은 "읽지 않았다" 의 증거가 되지 못하므로, 그 기간의 로깅 설정부터 확인합니다. 로깅 설정이 바뀐 흔적은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)에서 다룹니다.

로그인 로그는 인증을 보여 줄 뿐, 그 세션으로 무엇을 했는지는 관리·데이터 로그와 이어 봐야 압니다. 세션과 토큰이 로그에 어떻게 이어지는지는 [토큰과 세션](../identity/tokens-sessions.md)에서 다룹니다.

흐름 로그에는 패킷 내용이 없어서 무엇을 보냈는지는 알 수 없습니다. Google Cloud 는 표본 추출이라 모든 흐름이 남지 않습니다[27]. AWS 에서 보조 사설 IPv4 주소로 온 트래픽도 `dstaddr` 에는 네트워크 인터페이스의 주 사설 IPv4 주소가 적히므로, 원래 목적지 주소는 `pkt-dstaddr` 필드를 넣어 만든 흐름 로그에서만 보입니다[24].

## 함정

- "CloudTrail 은 기본으로 켜져 있다" 는 말은 최근 90일 관리 이벤트를 리전별로 보여 주는 이벤트 기록 (Event history) 을 가리킵니다. 이벤트 기록 화면에는 데이터 이벤트, Insights 이벤트, 네트워크 활동 이벤트가 나오지 않습니다[3].
- 이벤트 기록은 트레일 설정을 따르지 않습니다. 트레일에서 KMS 이벤트를 빼도 이벤트 기록에서는 빠지지 않으므로, 트레일 사본에 없는 KMS 이벤트가 이벤트 기록에는 있을 수 있습니다[4].
- Azure 활동 로그의 Administrative 범주는 Write·Delete·Action 작업 하나를 시작 레코드와 성공·실패 레코드로 따로 남깁니다[9]. 레코드 수를 작업 수로 세지 않습니다. 한 동작이 여러 레코드가 되는 경우는 [JSON 로그 읽기](json-logs.md)에서 다룹니다.
- Microsoft 365 는 감사 로깅이 기본으로 켜지지만, Business Basic·Business Standard·Business Premium 같은 중소기업용 라이선스와, 엔터프라이즈 라이선스 무료 체험을 쓰는 관리되지 않는 테넌트 (unmanaged tenant) 는 기본으로 꺼져 있어서 관리자가 켜야 합니다[15]. 2026년 9월 문서 기준입니다.
- Entra 로그인 로그를 옛 화면에서만 보면 비대화형·서비스 주체·관리 ID 로그인이 빠집니다[18]. 클라이언트 앱이 새로 고침 토큰으로 액세스 토큰을 받은 일은 비대화형 로그인에 남으므로[33], 로그인 기록을 받을 때는 네 종류를 모두 받습니다.
- AWS VPC 흐름 로그는 만든 뒤 필드를 바꿀 수 없습니다[24]. 조사에 필요한 필드가 없는 흐름 로그라면 그 필드는 과거 기간에 대해 얻을 수 없습니다.
- AWS 흐름 로그의 `start`·`end` 는 실제 패킷 시각보다 최대 60초 앞서거나 늦을 수 있습니다[23]. 다른 로그와 초 단위로 맞추지 않습니다.
- Azure NSG 흐름 로그에서 VNet 흐름 로그로 옮긴 테넌트는 기간에 따라 흐름 로그 종류와 레코드 모양이 다를 수 있습니다[26].

## 도구

Microsoft 365·Entra·Azure 로그는 Microsoft-Extractor-Suite 가 갈래별 명령으로 받습니다. 통합 감사 로그는 `Get-UAL`·`Get-UALGraph`, Entra 로그인·감사 로그는 `Get-GraphEntraSignInLogs`·`Get-GraphEntraAuditLogs`, 구독 활동 로그는 `Get-ActivityLogs`, 테넌트 단위 활동 로그는 `Get-DirectoryActivityLogs` 입니다[31]. DFIR-O365RC 는 `Get-O365Full`·`Get-O365Light`(통합 감사 로그), `Get-AADLogs`(Entra), `Get-AzRMActivityLogs`(활동 로그)로 나눠 받습니다[32]. 도구 비교는 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md)에서 다룹니다.

Google Workspace 는 ALFA 가 Reports API 의 `applicationName` 마다 JSON 파일을 하나씩 만듭니다[30]. Gmail 로그 이벤트는 시작·끝 시각을 넣어야 하고, 그 차이가 30일 이하여야 받을 수 있습니다[30]. AWS·Azure·Google Cloud 로그 수집은 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md)에서 다룹니다.

SigmaHQ 규칙은 로그 소스를 product·service 짝으로 나누고, 클라우드 쪽은 `aws/cloudtrail`, `azure/activitylogs`·`auditlogs`·`signinlogs`·`riskdetection`·`pim`, `gcp/gcp.audit`·`google_workspace.admin`, `m365/audit`·`exchange`·`threat_detection`·`threat_management`, `github/audit`, `okta/okta` 입니다[29]. 어느 규칙이 어느 갈래의 로그를 요구하는지 볼 때 참고가 됩니다. 규칙 활용은 [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md)에서 다룹니다.

함께 볼 페이지: [기록은 어디에 남나](../model/where-records-live.md), [보관 기간과 라이선스](retention-licensing.md), [JSON 로그 읽기](json-logs.md), [클라우드 로그의 시각](timestamps.md), [IP·사용자 에이전트·위치 정보](ip-ua-geo.md), [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md), [활동 로그](../../02-artifacts/azure/activity-log.md), [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md).

## 참고 문헌

1. AWS, "CloudTrail concepts", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html
2. AWS, "CloudTrail record contents for management, data, and network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
3. AWS, "Working with CloudTrail event history", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
4. AWS, "Logging management events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-management-events-with-cloudtrail.html
5. AWS, "Logging data events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html
6. AWS, "Logging network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-network-events-with-cloudtrail.html
7. AWS, "Logging options for Amazon S3", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/logging-with-S3.html
8. Microsoft, "Activity log in Azure Monitor" (ms.date 2026-05-04). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
9. Microsoft, "Azure activity log event schema" (ms.date 2026-03-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
10. Microsoft, "Azure resource logs" (ms.date 2025-07-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs.md
11. Google Cloud, "Cloud Audit Logs overview" (2026-09-25 갱신). https://cloud.google.com/logging/docs/audit
12. Google Cloud, "Understanding audit logs" (2026-09-25 갱신). https://cloud.google.com/logging/docs/audit/understanding-audit-logs
13. Microsoft, "Office 365 Management Activity API schema" (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
14. Microsoft, "Use MailItemsAccessed to investigate compromised accounts" (2026-06-24 갱신). https://learn.microsoft.com/en-us/purview/audit-log-investigate-accounts
15. Microsoft, "Turn auditing on or off" (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-enable-disable
16. Google, "Data retention and lag times", Google Workspace Admin Help (2026-09-25 갱신). https://support.google.com/a/answer/7061566
17. Google, "Login Audit Activity Events", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/login
18. Microsoft, "Sign-in logs in Microsoft Entra ID" (ms.date 2025-11-07). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-ins.md
19. Microsoft, "signIn resource type" (Microsoft Graph beta, 2025-11-28 갱신). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
20. Microsoft, "Microsoft Entra data retention" (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
21. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
22. Slack, "team.accessLogs method". https://api.slack.com/methods/team.accessLogs
23. AWS, "Flow log records", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html
24. AWS, "Flow log limitations", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-limitations.html
25. Microsoft, "Virtual network flow logs" (ms.date 2026-02-10). https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/network-watcher/vnet-flow-logs-overview.md
26. Microsoft, "Flow logging for network security groups" (2026-02-10 갱신). https://learn.microsoft.com/en-us/azure/network-watcher/nsg-flow-logs-overview
27. Google Cloud, "VPC Flow Logs" (2026-09-18 갱신). https://cloud.google.com/vpc/docs/flow-logs
28. Google Cloud, "About VPC Flow Logs records" (2026-09-18 갱신). https://cloud.google.com/vpc/docs/about-flow-logs-records
29. SigmaHQ, "Sigma appendix: taxonomy", sigma-specification. https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-appendix-taxonomy.md
30. Invictus Incident Response, ALFA(README.md, 설정 파일 alfa/config/config.yml). https://github.com/invictus-ir/ALFA , https://github.com/invictus-ir/ALFA/blob/main/alfa/config/config.yml
31. Invictus Incident Response, Microsoft-Extractor-Suite. https://github.com/invictus-ir/Microsoft-Extractor-Suite
32. ANSSI, DFIR-O365RC. https://github.com/ANSSI-FR/DFIR-O365RC
33. Microsoft, "Non-interactive sign-in logs" (ms.date 2026-02-09). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-noninteractive-sign-ins.md
