---
title: "기록은 어디에 남나"
parent: "기반 · 클라우드 조사의 구조"
nav_order: 20
---

# 기록은 어디에 남나 (Where Records Live)

클라우드의 기록은 관리 작업, 데이터 읽기·쓰기, 로그인, 서비스 안 데이터의 네 종류로 나뉘어 서로 다른 곳에 남고, 종류마다 기본으로 남는지·얼마나 오래 남는지가 다릅니다.

## 이 형식을 쓰는 아티팩트

이 페이지는 파일 형식이 아니라 "어떤 일이 어느 로그에 남는가" 를 다룹니다. 클라우드 서비스는 기록을 하나의 로그에 모으지 않습니다. 가상 머신을 만든 일과 그 가상 머신 안 데이터를 읽은 일은 다른 로그에 남고, 로그인은 또 다른 로그에 남습니다. 조사 질문을 받으면 먼저 그 일이 네 종류 가운데 어디에 속하는지 정하고, 그 종류의 로그가 켜져 있었는지와 아직 보관 기간 안인지를 확인해야 합니다.

| 종류 | 기록하는 일 | 대표 기록 |
|---|---|---|
| 제어 평면 (control plane) | 리소스를 만들고 바꾸고 지우는 관리 작업, 권한·설정 변경 | [Azure 활동 로그](../../02-artifacts/azure/activity-log.md), [CloudTrail 관리 이벤트](../../02-artifacts/aws/cloudtrail/index.md), [Cloud Audit Logs 의 Admin Activity](../../02-artifacts/gcp/cloud-audit-logs.md), [Workspace 관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md) |
| 데이터 평면 (data plane) | 리소스 안의 데이터를 읽고 쓰는 일 | [Azure 리소스 로그](../../02-artifacts/azure/resource-logs.md), CloudTrail 데이터 이벤트, Cloud Audit Logs 의 Data Access |
| 신원 (identity) | 로그인, 디렉터리 변경 | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [Workspace 로그인 기록](../../02-artifacts/google-workspace/login-audit.md) |
| 앱 안 데이터 | 서비스가 저장한 문서·레코드 자체의 변경 이력 | [Vault와 Takeout](../../02-artifacts/google-workspace/vault-takeout.md), [Purview eDiscovery와 보존](../../02-artifacts/m365/purview-ediscovery.md) |

Microsoft 365 의 [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md)는 Exchange·SharePoint·OneDrive·Entra 같은 여러 서비스의 사용자·관리자 활동을 한곳에 모으고, 레코드의 `Workload` 필드에 활동이 일어난 서비스를 적습니다[14][23]. 그래서 한 로그 안에 여러 종류가 섞여 있습니다. 로그 종류마다 필드가 어떻게 생겼는지는 [로그의 종류](../logging/log-types.md)에서 다룹니다.

## 구조

### 제어 평면

Azure 에서 제어 평면 요청은 모두 Azure Resource Manager(ARM) 주소로 갑니다. 전역 클라우드의 주소는 `https://management.azure.com` 이고, ARM 이 역할 기반 접근 제어·정책·잠금을 적용한 뒤 요청을 리소스 공급자에 넘깁니다[1]. 이 요청을 기록하는 곳이 활동 로그 (Activity Log) 입니다. 활동 로그는 설정하지 않아도 수집되고, 고객이 항목을 바꾸거나 지울 수 없습니다[2]. 주로 만들기·바꾸기·지우기와 action 작업이 남고, 읽기 작업은 보통 남지 않습니다[2]. 리소스를 누가 만들었는지는 활동 로그에만 남습니다[2].

AWS CloudTrail 은 트레일이나 이벤트 데이터 저장소를 만들지 않아도 최근 90일의 관리 이벤트를 이벤트 기록 (Event history) 에 보여 주고, 이 기록은 바꿀 수 없습니다[7]. 이벤트 기록은 이벤트가 일어난 리전에 남습니다[7].

Google Cloud 의 Admin Activity 감사 로그는 리소스 구성이나 메타데이터를 바꾸는 호출을 기록하고, 항상 쓰이며 끌 수도 제외할 수도 없습니다[9]. Cloud Logging API 를 꺼도 생성됩니다[9]. Google 시스템이 스스로 바꾼 구성(자동 확장으로 인스턴스가 늘고 줄어든 일 같은 것)은 System Event 감사 로그에 남고, 이것도 끌 수 없습니다[9]. 보안 정책 때문에 접근이 거부된 일은 Policy Denied 감사 로그에 남는데, 기본으로 생성되고 끌 수는 없지만 제외 필터로 저장을 막을 수 있습니다[9]. Cloud Audit Logs 가 쓴 항목은 바꿀 수 없습니다[9].

### 데이터 평면

Azure 의 데이터 평면 요청은 리소스마다 다른 주소로 갑니다. 저장소 계정이라면 `https://myaccount.blob.core.windows.net` 같은 주소입니다[1]. 관리·통제 기능이 데이터 평면에는 적용되지 않을 수 있어서, 데이터베이스 삭제를 막는 잠금을 걸어도 쿼리로 데이터를 지우는 일은 막지 못합니다[1]. Key Vault 에서 비밀을 읽거나 데이터베이스에 요청한 일은 리소스 로그 (resource logs) 에 남는데, 리소스 로그는 기본으로 수집되지 않고 리소스마다 진단 설정 (diagnostic setting) 을 만들어야 모입니다[2][4].

AWS 트레일과 이벤트 데이터 저장소는 기본으로 관리 이벤트만 기록하고 데이터 이벤트는 기록하지 않습니다[8]. S3 객체 읽기 같은 데이터 이벤트는 따로 켜야 남습니다. 자세한 선택 방법은 [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md)에서 다룹니다.

Google Cloud 의 Data Access 감사 로그는 BigQuery 를 빼고 기본으로 꺼져 있어서 켜야 기록됩니다[9]. 켜면 데이터에 접근한 쪽이 아니라 데이터가 있는 프로젝트에 쓰입니다[9]. `allUsers` 나 `allAuthenticatedUsers` 에 공개한 리소스에 접근한 일은 감사 로그를 만들지 않습니다[9].

### 신원

Entra ID 의 로그인 로그와 감사 로그는 Microsoft 365 통합 감사 로그와 따로 저장되고, 통합 감사 로그의 보관은 Purview Audit 가 정합니다[12]. 통합 감사 로그에도 Entra ID 이벤트(`Workload` 가 `AzureActiveDirectory` 인 레코드, 로그인은 `AzureActiveDirectoryStsLogon` 형식)가 들어오지만, 이 레코드의 보관 기간은 Entra 로그와 따로 정해집니다[12][14][23].

Entra ID 가 로그를 모으기 시작하는 시점도 라이선스마다 다릅니다. P1·P2 는 구독에 가입할 때부터 모으고, Free 는 Entra ID 를 처음 열거나 보고 API 를 처음 쓸 때부터 모읍니다[12]. Microsoft Graph 활동 로그는 진단 설정에서 해당 범주를 켠 때부터 모입니다[12].

Google Workspace 의 로그인·관리 이벤트는 관리 콘솔의 감사 및 조사 페이지나 Admin SDK 보고서 API 로 가져옵니다[16][17]. 관리자는 로그 이벤트 데이터를 지우거나 보관 기간을 바꿀 수 없습니다[16].

### 앱 안 데이터

서비스가 저장한 데이터 자체에도 변경 흔적이 남습니다. SaaS 데이터베이스의 레코드에 남은 `LastModifiedBy`·`LastModifiedDate` 값과 변경 내용을 알려진 정상 사본과 비교하면, 이벤트 로그와 따로 변경을 추적할 수 있습니다[20]. SaaS 이벤트 로그의 예로는 `EVENT_TYPE`, `TIMESTAMP`, `REQUEST_ID`, `ORGANIZATION_ID`, `USER_ID` 로 시작하고 `CLIENT_IP` 를 담는 CSV 가 있습니다[20].

문서 편집 이력이 서버에 남는 방식은 서비스마다 다릅니다. 2016년 Google Docs 에서는 편집 이력이 changelog 로 서버에 남았고, 이전 판으로 되돌리면 옛 기록을 지우지 않고 그 판의 스냅숏을 담은 "revert" 항목을 덧붙였습니다[21]. 이런 동작은 서비스가 바뀌면 달라질 수 있으므로, 사건 당시의 동작은 조사 대상 계정의 판 기록을 직접 열어 확인합니다.

### 기본으로 남는 것과 켜야 남는 것

| 서비스 | 기본으로 남는 것 | 켜야 남는 것 | 켜져 있는지 확인하는 곳 |
|---|---|---|---|
| Microsoft 365 | 통합 감사 로그(기본값이 켜짐) | — | Exchange Online PowerShell 의 `Get-AdminAuditLogConfig` 결과에서 `UnifiedAuditLogIngestionEnabled`[15] |
| Entra ID | 로그인·감사 로그 | Microsoft Graph 활동 로그(P1·P2 에서 진단 설정) | Entra 진단 설정[12] |
| Azure | 활동 로그 | 리소스 로그, 90일을 넘는 활동 로그 보관 | 리소스·구독의 진단 설정[2][5] |
| AWS | 이벤트 기록의 관리 이벤트(90일) | 트레일·이벤트 데이터 저장소, 데이터 이벤트 | `aws cloudtrail get-event-selectors --trail-name TrailName`[10] |
| Google Cloud | Admin Activity, System Event, Policy Denied | Data Access(BigQuery 제외) | 프로젝트·폴더·조직의 Data Access 감사 로그 설정[9] |
| Google Workspace | 관리·로그인·Drive·OAuth 토큰 등 로그 이벤트 | — | 관리 콘솔 보고서[16] |
| Slack | Enterprise 요금제의 감사 로그 API | — | Enterprise 조직에 설치한 앱(`auditlogs:read`)[18] |

`UnifiedAuditLogIngestionEnabled` 는 기본값이 `$true` 이고, `$false` 이면 사용자·관리자 활동이 통합 감사 로그에 기록되지 않고 검색도 되지 않습니다[15]. 이 값은 Exchange Online PowerShell 에서 확인해야 하며, Security & Compliance PowerShell 에서는 늘 `False` 로 나옵니다[15]. Slack 감사 로그 API 는 Slack 감사 이벤트 전부가 아니라 일부만 제공합니다[18].

### 기본 저장 위치와 보관 기간

아래 표는 2026년 9월 문서 기준입니다. 라이선스별 세부 조건과 연장 방법은 [보관 기간과 라이선스](../logging/retention-licensing.md)에서 다룹니다.

| 서비스 | 기록 | 기본 저장 위치 | 기본 보관 기간 |
|---|---|---|---|
| Microsoft 365 | 통합 감사 로그 | Purview Audit | Audit(Standard) 180일(2023년 10월 17일 전에 생긴 레코드는 90일). Audit(Premium) 기본 정책은 E5 사용자의 `Workload` 가 AzureActiveDirectory·Exchange·OneDrive·SharePoint 인 레코드를 1년, 나머지는 180일. 서비스 주체·시스템·앱이 만든 레코드는 1년 고정[13][14] |
| Entra ID | 로그인·감사 로그 | Entra | Free 7일, P1·P2 30일[12] |
| Entra ID | 위험 로그인 | Entra | Free 7일, P1 30일, P2 90일[12] |
| Azure | 활동 로그 | 플랫폼 | 90일, 그 기간 요금 없음[2] |
| Azure | 리소스 로그 | 없음(진단 설정 목적지) | 목적지에 따라 다름[4][5] |
| Azure | Log Analytics 표 | 작업 영역 | 기본 30일(90일 기본인 표 있음), 분석 보관 최대 2년, 전체 보관 최대 12년[6] |
| AWS | CloudTrail 관리 이벤트 | 이벤트 기록(리전별) | 90일[7] |
| AWS | CloudTrail 데이터 이벤트 | 없음(트레일·이벤트 데이터 저장소) | 목적지에 따라 다름[8] |
| Google Cloud | Admin Activity·System Event·Access Transparency | 리소스의 `_Required` 버킷 | 400일, 바꿀 수 없음[11][28] |
| Google Cloud | Data Access·Policy Denied | 리소스의 `_Default` 버킷 | 30일, 프로젝트 버킷은 1~3650일로 조정, 폴더·조직 버킷은 조정 불가[9][11] |
| Google Workspace | 관리·로그인·Drive·Gmail·OAuth 토큰 로그 이벤트 | Workspace | 6개월(API 조회는 최대 180일), 메일 로그 검색 30일, Vault 로그 이벤트 무기한[16][17] |
| GitHub Enterprise Cloud | 엔터프라이즈 감사 로그 | GitHub | 180일, Git 이벤트 7일[19] |

Audit(Premium) 기본 정책은 Office 365·Microsoft 365 E5 라이선스나 Microsoft Purview Suite, E5 eDiscovery and Audit 추가 라이선스가 있는 사용자의 활동에만 적용되고, E5 가 아닌 사용자와 게스트 사용자의 레코드는 180일 보관됩니다[14]. 10년 보관은 사용자별 추가 라이선스와 정책이 있어야 하고, 정책을 만들기 전에 생긴 레코드에는 적용되지 않습니다[13].

## 읽는 법

기록 한 줄을 받으면 그것이 어느 종류에서 어느 경로로 들어왔는지부터 읽습니다. 서비스마다 레코드 안에 출처를 알려 주는 값이 있습니다.

1. **어느 로그인지 확인합니다.** Google Cloud 감사 로그는 `logName` 이 `projects/PROJECT_ID/logs/cloudaudit.googleapis.com%2Factivity` 처럼 끝나고, 끝부분이 `activity`·`data_access`·`system_event`·`policy` 가운데 무엇인지로 종류가 나뉩니다[9]. 앞부분이 `projects/`·`folders/`·`organizations/`·`billingAccounts/` 가운데 무엇인지는 [테넌트·구독·계정·프로젝트](tenancy.md)에서 다룹니다. 통합 감사 로그는 `Workload` 로 서비스를 구분합니다[23].
2. **사건 시각과 들어온 시각을 나눠 읽습니다.** Azure 활동 로그의 `eventTimestamp` 는 요청을 처리한 서비스가 이벤트를 만든 시각이고, `submissionTimestamp` 는 조회할 수 있게 된 시각입니다[3]. 활동 로그 항목은 보통 이벤트 뒤 3~20분 안에 조회할 수 있게 됩니다[2]. 통합 감사 로그의 `CreationTime` 은 UTC 입니다[23].
3. **어디서 받은 사본인지 확인합니다.** 저장소 계정으로 내보낸 활동 로그는 아래 경로의 한 시간 단위 파일에 쌓입니다[2].

   ```text
   insights-activity-logs/resourceId=/SUBSCRIPTIONS/{subscription ID}/y={four-digit numeric year}/m={two-digit numeric month}/d={two-digit numeric day}/h={two-digit 24-hour clock hour}/m=00/PT1H.json
   ```

   이 파일에는 그 시간 동안 받은 이벤트가 받은 순서대로 덧붙고, 이벤트가 생긴 시각과는 상관이 없습니다[2]. 그래서 파일 경로의 시각은 사건 시각이 아니라 받은 시각으로 읽어야 합니다.

   아래는 활동 로그 스키마 예시[3]를 바탕으로 필드 몇 개만 추려 만든 예시입니다. 두 시각 사이의 약 19초가 조회할 수 있게 되기까지 걸린 시간입니다.

   ```json
   {
     "operationName": { "value": "Microsoft.Network/networkSecurityGroups/write" },
     "resourceId": "/subscriptions/aaaa0a0a-bb1b-cc2c-dd3d-eeeeee4e4e4e/resourcegroups/myResourceGroup/providers/Microsoft.Network/networkSecurityGroups/myNSG",
     "eventTimestamp": "2026-09-01T02:10:31.3810679Z",
     "submissionTimestamp": "2026-09-01T02:10:50.0724829Z"
   }
   ```

4. **가장 오래된 레코드를 봅니다.** 받은 로그에서 가장 오래된 레코드의 시각을 적어 두면, 그 앞 기간이 "활동이 없던 기간" 인지 "보관 기간이 지나 사라진 기간" 인지를 가를 수 있습니다. 보관 기간 표의 값과 실제로 받은 가장 오래된 시각이 다르면 실제 값을 보고서에 씁니다.

시각 필드 전반과 지연 시간은 [클라우드 로그의 시각](../logging/timestamps.md)에서 다룹니다.

## 포렌식에서 중요한 점

**증명하는 것.** 활동 로그와 Admin Activity 감사 로그는 리소스를 만들고 바꾸고 지운 관리 작업이 있었음을 보여 줍니다[2][9]. 이 두 로그는 고객이 끄거나 항목을 고칠 수 없어서[2][9], 공격자가 관리자 권한을 얻었더라도 관리 작업 흔적은 보관 기간 동안 남습니다.

**증명하지 못하는 것.** 제어 평면 로그만으로는 데이터를 읽었는지 말할 수 없습니다. 활동 로그는 읽기 작업을 보통 남기지 않고[2], Azure 리소스 로그와 Google Cloud Data Access 로그는 기본으로 꺼져 있으며[4][9], AWS 데이터 이벤트도 기본으로 기록되지 않습니다[8]. 데이터 평면 로그가 꺼져 있던 기간에 대해서는 "읽은 기록이 없다" 가 아니라 "읽기를 기록하는 설정이 꺼져 있었다" 고 써야 합니다. Google Cloud 에서 `allUsers` 로 공개한 리소스는 접근해도 감사 로그가 생기지 않으므로[9], 로그가 없다는 사실이 접근이 없었다는 뜻이 되지 않습니다.

**지나간 기록은 돌아오지 않습니다.** Entra ID 를 Free 에서 P1·P2 로 올려도 이미 7일이 지난 데이터는 복구되지 않고[12], Purview 10년 보관 정책도 만들기 전의 레코드에는 적용되지 않습니다[13]. 사고를 알게 되면 먼저 보관 기간이 짧은 로그부터 내보냅니다. 순서와 방법은 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)에서 다룹니다.

**로그는 끌 수도 있습니다.** 통합 감사 로그는 `UnifiedAuditLogIngestionEnabled` 를 `$false` 로 바꾸면 기록이 멈춥니다[15]. CloudTrail 트레일을 멈추거나 바꾸거나 지운 일은 `eventSource` 가 `cloudtrail.amazonaws.com` 이고 `eventName` 이 `StopLogging`·`UpdateTrail`·`DeleteTrail` 인 CloudTrail 이벤트로 남습니다[26]. 흔적을 찾는 순서는 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)에서 다룹니다.

## 함정

- AWS 의 IAM·STS·CloudFront 같은 전역 서비스 이벤트는 2021년 11월 22일부터 트레일에 us-east-1 로 기록되지만, 콘솔 이벤트 기록과 `aws cloudtrail lookup-events` 는 실제로 일어난 리전에 보여 줍니다[8]. 일부 전역 서비스 이벤트는 us-east-2 나 us-west-2 로 기록됩니다[8]. 리전 하나만 보고 "이벤트가 없다" 고 쓰지 않습니다.
- Azure 관리 그룹과 그 아래 구독에 모두 진단 설정이 있으면 같은 이벤트가 두 번 들어옵니다[2]. 건수를 세기 전에 모든 필드의 해시로 중복을 지웁니다. 중복을 지우는 KQL 예는 `AzureActivity | extend Hash = hash(dynamic_to_json(pack_all())) | summarize arg_max(TimeGenerated, *) by Hash` 입니다[2].
- Azure 에서 리소스를 지우거나 이름·리소스 그룹·구독을 바꿀 때 진단 설정을 지우지 않으면, 같은 이름으로 다시 만든 리소스에 옛 진단 설정이 적용될 수 있습니다[5].
- Google Cloud 에서 Admin Activity·System Event 로그를 다른 프로젝트로 보내면 목적지 프로젝트의 `_Required`·`_Default` 싱크를 거치지 않으므로, 목적지에 싱크를 따로 만들어야 저장됩니다[9]. 폴더·조직 수준 로그를 30일 넘게 두려면 프로젝트 버킷으로 보내야 합니다[11].
- Google Cloud Logging API 는 1일 넘게 미래인 시각의 항목을 거부하고, 버킷 보관 기간보다 오래된 시각의 항목은 API 가 받더라도 버킷에 저장하지 않습니다[11].
- Google Workspace 로그 이벤트는 대부분 몇 분 안에 들어오지만, Calendar·Groups 는 수십 분에서 몇 시간, OAuth 는 몇 시간까지 늦을 수 있고, 드물게 보고되지 않는 이벤트도 있습니다[16]. 사고 직후 조회에서 보이지 않던 이벤트가 나중에 나타날 수 있으므로 같은 기간을 다시 받습니다.
- Microsoft 365 수집 도구의 설명에 적힌 보관 기간은 공식 문서와 다를 수 있습니다. DFIR-O365RC README 는 Exchange Online PowerShell 로 받는 통합 감사 로그를 90일, Purview 로 받는 것을 180일로 적고[24], Purview 문서는 Audit(Standard) 기본 보관을 180일로 적습니다[13]. 끝점마다 조회할 수 있는 범위가 다를 수 있으므로 실제로 받은 레코드의 가장 오래된 시각을 확인합니다.
- GitHub 엔터프라이즈 감사 로그 화면은 기본으로 최근 3개월만 보여 주고, 그보다 오래된 이벤트는 `created` 로 기간을 지정해야 보입니다[19].

## 도구

Microsoft 365 와 Azure 는 Microsoft-Extractor-Suite 의 `Get-UAL`(통합 감사 로그), `Get-GraphEntraSignInLogs`·`Get-GraphEntraAuditLogs`(Entra), `Get-ActivityLogs`(구독 활동 로그), `Get-DirectoryActivityLogs`(테넌트 수준 활동 로그)로 종류별로 받을 수 있습니다[22]. `Get-UAL` 은 한 번 조회에 5,000건 상한이 있어 시간 구간을 줄여 가며 다시 받고, 가장 짧은 구간에서도 상한을 넘으면 일부가 빠진 채 다음 구간으로 넘어가고, 그 구간을 로그에 오류로 남깁니다[22]. DFIR-O365RC 는 통합 감사 로그를 기본으로 Exchange Online PowerShell 로, Entra 로그를 Microsoft Graph PowerShell 로, Azure 활동 로그를 Az.Monitor 로 받습니다[24]. 수집 도구 비교는 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md)에서 다룹니다.

Google Workspace 는 ALFA 의 `alfa acquire` 가 로그 종류마다 JSON 파일을 하나씩 만들고, `--start-time`·`--end-time` 에 RFC3339 시각을 받습니다[25]. AWS 는 Invictus-AWS 가 리전 단위로 로그를 모아 리전 폴더에 저장합니다[27]. AWS·Azure·Google Cloud 수집 절차는 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md)에서 다룹니다.

로그 위치와 필드 이름을 맞출 때는 SigmaHQ 클라우드 규칙의 `logsource` 가 참고가 됩니다. 규칙은 `aws/cloudtrail`, `azure/activitylogs`, `azure/signinlogs`, `azure/auditlogs`, `gcp/gcp.audit`, `gcp/google_workspace.admin`, `m365/audit` 같은 짝으로 로그 위치를 나누고, CloudTrail 은 `eventSource`·`eventName`, Google Cloud 는 `data.protoPayload.serviceName` 같은 필드로 조건을 겁니다[26]. 규칙 활용은 [탐지 규칙으로 로그 검색하기](../../03-techniques/analysis/detection-rules.md)에서 다룹니다.

함께 볼 페이지: [책임 공유와 조사 범위](shared-responsibility.md), [테넌트·구독·계정·프로젝트](tenancy.md), [로그의 종류](../logging/log-types.md), [보관 기간과 라이선스](../logging/retention-licensing.md), [클라우드 로그의 시각](../logging/timestamps.md), [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md).

## 참고 문헌

1. Microsoft, "Azure control plane and data plane", Microsoft Learn (2026-02-27 갱신). https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/control-plane-and-data-plane
2. Microsoft, "Activity log in Azure Monitor" (ms.date 2026-05-04). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
3. Microsoft, "Azure activity log event schema" (ms.date 2026-03-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
4. Microsoft, "Azure resource logs" (ms.date 2025-07-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs.md
5. Microsoft, "Diagnostic settings in Azure Monitor" (ms.date 2026-03-31). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/data-collection/diagnostic-settings.md
6. Microsoft, "Manage data retention in a Log Analytics workspace" (ms.date 2026-09-02). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/data-retention-configure.md
7. AWS, "Working with CloudTrail event history", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
8. AWS, "CloudTrail concepts", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html
9. Google Cloud, "Cloud Audit Logs overview" (2026-09-25 갱신). https://cloud.google.com/logging/docs/audit
10. AWS, "Logging data events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html
11. Google Cloud, "Cloud Logging quotas and limits" (2026-09-25 갱신). https://cloud.google.com/logging/quotas
12. Microsoft, "Microsoft Entra data retention" (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
13. Microsoft, "Learn about auditing solutions in Microsoft Purview" (2026-05-18 갱신). https://learn.microsoft.com/en-us/purview/audit-solutions-overview
14. Microsoft, "Manage audit log retention policies" (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
15. Microsoft, "Get-AdminAuditLogConfig", "Set-AdminAuditLogConfig", Exchange PowerShell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Get-AdminAuditLogConfig.md , https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Set-AdminAuditLogConfig.md
16. Google, "Data retention and lag times", Google Workspace Admin Help (2026-09-25 갱신). https://support.google.com/a/answer/7061566
17. Google, "REST Resource: activities", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/reference/activities
18. Slack, "Monitoring your workspace with audit logs". https://api.slack.com/admins/audit-logs
19. GitHub, audit log 재사용 문구(retention-periods, git-events-retention-period, only-three-months-displayed), github/docs 저장소. https://github.com/github/docs/blob/main/data/reusables/audit_log/retention-periods.md
20. Eoghan Casey, "SaaS Forensics & Response: Forensic Preservation, Recovery, and Analysis of SaaS Data", DFRWS USA 2023 발표(Baltimore, 2023-07-11). https://dfrws.org/presentation/saas-forensics-and-response/
21. Vassil Roussev, "Forensic analysis of cloud-native artifacts", DFRWS EU 2016 발표. https://dfrws.org/presentation/forensic-analysis-of-cloud-native-artifacts/
22. Invictus Incident Response, Microsoft-Extractor-Suite. https://github.com/invictus-ir/Microsoft-Extractor-Suite
23. Microsoft, "Office 365 Management Activity API schema" (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
24. ANSSI, DFIR-O365RC. https://github.com/ANSSI-FR/DFIR-O365RC
25. Invictus Incident Response, ALFA(Automated Audit Log Forensic Analysis for Google Workspace). https://github.com/invictus-ir/ALFA
26. SigmaHQ, Sigma 클라우드 규칙(rules/cloud), 예: aws_cloudtrail_disable_logging.yml. https://github.com/SigmaHQ/sigma/tree/master/rules/cloud
27. Invictus Incident Response, Invictus-AWS. https://github.com/invictus-ir/Invictus-AWS
28. Google Cloud, "Routing and storage overview" (2026-09-25 갱신). https://cloud.google.com/logging/docs/routing/overview
