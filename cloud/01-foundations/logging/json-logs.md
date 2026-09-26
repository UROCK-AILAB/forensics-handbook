---
title: "JSON 로그 읽기"
parent: "기반 · 로그 체계"
nav_order: 100
---

# JSON 로그 읽기 (JSON Log Records)

클라우드 로그는 대부분 JSON 레코드로 오지만, 레코드를 감싼 겉모양과 필드 이름, 고유 ID, 중복·순서 규칙이 서비스마다 달라서 레코드 한 줄을 읽기 전에 그 규칙부터 알아야 합니다.

## 이 형식을 쓰는 아티팩트

이 쪽은 파일 형식 하나가 아니라 여러 서비스가 JSON 으로 내보내는 로그 레코드를 읽는 방법을 다룹니다. [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md), [통합 감사 로그 (Unified Audit Log, UAL)](../../02-artifacts/m365/unified-audit-log/index.md), [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [Azure 활동 로그](../../02-artifacts/azure/activity-log.md)와 [리소스 로그](../../02-artifacts/azure/resource-logs.md), [Google Cloud 감사 로그](../../02-artifacts/gcp/cloud-audit-logs.md), [Google Workspace 로그인 기록](../../02-artifacts/google-workspace/login-audit.md), [Okta](../../02-artifacts/saas/okta.md), [Slack](../../02-artifacts/saas/slack.md), [Dropbox·Box](../../02-artifacts/saas/dropbox-box.md)가 모두 여기에 해당합니다. 어떤 로그가 어떤 일을 기록하는지는 [로그의 종류](log-types.md), 얼마나 오래 남는지는 [보관 기간과 라이선스](retention-licensing.md)에서 다룹니다. 시각 필드와 IP·사용자 에이전트 필드는 각각 [클라우드 로그의 시각](timestamps.md)과 [IP·사용자 에이전트·위치 정보](ip-ua-geo.md)에서 따로 다룹니다.

## 구조

### 겉모양 — 레코드를 감싼 봉투

같은 서비스라도 어디서 받느냐에 따라 레코드를 감싼 모양이 다릅니다. 파일을 열기 전에 아래 표에서 겉모양을 확인하고, 레코드 배열을 먼저 꺼낸 다음 한 레코드씩 읽습니다.

| 서비스·받는 경로 | 겉모양 | 근거 |
|---|---|---|
| CloudTrail 트레일 → S3 | gzip 으로 압축한 JSON 파일 하나에 `{"Records": [ … ]}` 배열이 들어 있습니다. 파일 이름은 `AccountID_CloudTrail_RegionName_YYYYMMDDTHHmmZ_UniqueString.json.gz` 이고, 경로는 `AWSLogs/계정ID/CloudTrail/리전/YYYY/MM/DD/` 입니다. Insights 는 `CloudTrail-Insight`, 네트워크 활동 이벤트는 `CloudTrail-NetworkActivity`, 데이터 이벤트 집계는 `CloudTrail-Aggregated` 폴더에 들어가고, 조직 트레일은 `AWSLogs/O-ID/계정ID/CloudTrail/…` 처럼 계정 ID 앞에 조직 폴더(`O-ID`)가 하나 더 붙습니다. | [2][3] |
| Azure 활동 로그 → 저장소 계정 | `insights-activity-logs/resourceId=/SUBSCRIPTIONS/구독ID/y=YYYY/m=MM/d=DD/h=HH/m=00/PT1H.json` 이름의 한 시간 단위 블롭입니다. 2018년 11월 1일부터 JSON Lines(한 줄에 레코드 하나) 형식입니다. | [4][5] |
| Azure 리소스 로그 → 저장소 계정 | `insights-logs-범주이름/resourceId=/SUBSCRIPTIONS/…/y=…/m=…/d=…/h=…/m=00/PT1H.json` 이름의 한 시간 단위 블롭입니다. | [6] |
| Azure 활동·리소스 로그 → 이벤트 허브 | `{"records": [ … ]}` 배열입니다. | [4][6] |
| Google Cloud Logging → Cloud Storage | 한 시간 단위 파일 `08:00:00_08:59:59_S0.json` 처럼 조각(shard) 번호가 붙고, 늦게 들어온 항목은 `_An:유닉스시각.json` 으로 끝나는 덧붙임 조각에 들어갑니다. | [7] |
| M365 UAL — `Search-UnifiedAuditLog`, Purview 포털 CSV | 열이 `CreationDate`, `UserIds`, `Operations`, `AuditData` 네 개이고, `AuditData` 열에 JSON 객체가 문자열로 들어 있습니다. | [9][22] |
| M365 UAL — Microsoft Graph `auditLogQuery` | 레코드의 `auditData` 가 문자열이 아니라 객체(`microsoft.graph.security.auditData`)로 옵니다. | [12][23] |
| Google Workspace Reports API | `items[]` 의 각 항목에 `id`(`time`, `uniqueQualifier`, `applicationName`, `customerId`), `actor`, `ipAddress`, `networkInfo`, `events[]` 가 있고, `events[]` 안에 `type`, `name`, `parameters[]` 가 있습니다. | [13] |
| Okta System Log | LogEvent 객체 하나가 레코드 하나입니다. 주요 필드는 `actor`, `client`, `authenticationContext`, `displayMessage`, `eventType`, `outcome`, `published`, `request`, `securityContext`, `severity`, `target[]`, `transaction`, `uuid`, `version` 입니다. | [16] |
| Slack Audit Logs API | 항목마다 `date_create`, `action`, `actor`, `entity`, `context` 가 있고, `context` 안에 `location`, `ua`, `ip_address`, `session_id` 가 있습니다. | [17] |
| Dropbox 팀 이벤트 | `TeamEvent` 객체에 `timestamp`, `event_category`, `actor`, `origin` 등이 있습니다. | [19] |

> 그림 자리: CloudTrail 파일(`Records` 배열), Azure PT1H.json(한 줄에 레코드 하나), UAL CSV(`AuditData` 열 안의 JSON 문자열)의 겉모양을 나란히 놓은 그림

### 한 레코드 안의 모양

CloudTrail 레코드는 필드 하나하나가 이름 그대로 최상위에 있습니다. 아래는 CloudTrail 레코드 명세의 필드로 만든 예시입니다[1].

```json
{
  "eventVersion": "1.11",
  "eventTime": "2026-09-01T02:10:33Z",
  "eventSource": "iam.amazonaws.com",
  "eventName": "CreateAccessKey",
  "eventID": "11111111-2222-3333-4444-555555555555",
  "userIdentity": { "type": "IAMUser", "accountId": "123456789012", "accessKeyId": "AKIAIOSFODNN7EXAMPLE" },
  "sourceIPAddress": "203.0.113.10",
  "readOnly": false,
  "eventCategory": "Management",
  "recipientAccountId": "123456789012"
}
```

UAL 은 JSON 이 두 겹입니다. CSV 한 줄의 `AuditData` 칸에 JSON 이 문자열로 들어 있어서, 칸을 한 번 더 JSON 으로 풀어야 필드가 보입니다. 아래는 만든 예시입니다.

```text
CreationDate,UserIds,Operations,AuditData
2026-09-01T02:15:00.0000000Z,user1@contoso.com,MailItemsAccessed,"{""Id"":""aaaa1111-bb22-cc33-dd44-eeeeee555555"",""CreationTime"":""2026-09-01T02:15:00"",""Operation"":""MailItemsAccessed"",""Workload"":""Exchange"",""UserId"":""user1@contoso.com"",""ClientIP"":""198.51.100.24""}"
```

UAL 의 공통 스키마(Common schema)에서 반드시 들어가는 필드는 `Id`, `RecordType`, `CreationTime`, `Operation`, `OrganizationId`, `UserType`, `UserKey`, `Workload`, `UserId`, `ClientIP` 이고, `ResultStatus`·`ObjectId`·`Scope`·`AppAccessContext` 는 없을 수도 있습니다[10]. 나머지 필드는 워크로드마다 따로 정한 스키마에 있습니다[10].

Google Cloud 의 LogEntry 는 `logName`, `resource`, `timestamp`, `receiveTimestamp`, `severity`, `insertId` 를 공통으로 두고, 내용은 `protoPayload`·`textPayload`·`jsonPayload` 가운데 많아야 하나에 들어갑니다[8]. 감사 로그 항목은 `protoPayload` 에 AuditLog 객체가 들어 있어서 다른 로그와 구분되고[26], 이 형식의 이름은 `type.googleapis.com/google.cloud.audit.AuditLog` 입니다[8]. `logName` 안의 로그 ID 는 URL 인코딩되어 있어서 `/` 가 `%2F` 로 적힙니다(예: `cloudaudit.googleapis.com%2Factivity`)[8][26].

Google Workspace 의 `events[].parameters[]` 는 이름과 값의 쌍으로 된 목록이고, 값의 형식에 따라 `value`, `multiValue`, `intValue`, `multiIntValue`, `boolValue`, `multiMessageValue` 같은 다른 키에 값이 들어갑니다[13]. 그래서 `{"name":"login_type","value":"google_password"}` 와 `{"name":"is_suspicious","boolValue":false}` 가 같은 목록에 섞여 있습니다[14]. 필드 경로로 곧바로 값을 꺼낼 수 없고, `name` 으로 항목을 찾은 뒤 형식에 맞는 키를 읽어야 합니다.

### 고유 ID·중복·순서

레코드마다 고유 ID 가 있지만 이름이 다르고, 중복과 순서에 대한 보장도 서비스마다 다릅니다. 여러 파일을 합칠 때는 아래 ID 로 중복을 걸러 냅니다.

| 서비스 | 고유 ID | 중복·순서 | 근거 |
|---|---|---|---|
| CloudTrail | `eventID`(GUID) | 드물게 로그 파일에 중복 이벤트가 들어 있을 수 있고, 중복 이벤트는 대부분 `eventID` 가 같습니다. 특정 시각에 배달된 파일에 그 이전 아무 시각의 레코드가 들어 있을 수 있습니다. | [1][2][3] |
| CloudTrail 교차 계정 | `sharedEventID` | 한 동작이 두 계정에 따로 배달되면 `sharedEventID` 는 같고 `eventID`·`recipientAccountId` 는 다릅니다. 호출한 계정과 자원 소유 계정이 같으면 이 필드가 없습니다. | [1] |
| M365 UAL | `Id` | `Search-UnifiedAuditLog` 결과에 같은 레코드가 여러 번 나올 수 있어 Untitled Goose Tool 은 `AuditData` 의 `Id` 로 중복을 셉니다. Management Activity API 의 콘텐츠 묶음 안 이벤트는 발생 순서대로 온다는 보장이 없고, 먼저 만든 묶음보다 이른 이벤트가 나중 묶음에 들어갈 수 있으며, 알림도 재시도 때문에 같은 콘텐츠에 여러 번 올 수 있습니다. | [11][24] |
| Azure 활동 로그 | `eventDataId` | 한 작업에 속한 이벤트들은 `operationId` 를 공유하고, 같은 상위 동작에 속한 이벤트들은 `correlationId` 를 공유합니다. | [5] |
| Entra 로그인 | — | 포털에서 한 줄로 보이는 MFA 로그인이 Azure Monitor 로 보낸 로그에서는 `correlationId` 가 같은 여러 줄로 나옵니다. | [21] |
| Entra 비대화형 로그인 | — | 포털은 애플리케이션·사용자·IP 주소·상태·자원 ID 가 같은 로그인을 한 줄로 묶어 "# sign-ins" 열에 개수를 적고, 펼치면 각 시각이 보입니다. | [20] |
| Google Cloud | `insertId` | 같은 프로젝트에서 `timestamp` 와 `insertId` 가 같은 항목은 한 질의 결과 안에서만 중복이 제거되고, 내보낸 로그에서는 중복 제거가 보장되지 않습니다. 같은 `logName`·`timestamp` 인 항목은 `insertId` 순으로 정렬합니다. 질의가 같거나 겹치는 싱크가 여럿이면 같은 항목이 Cloud Storage 에 여러 번 쓰일 수 있습니다. | [7][8] |
| Google Workspace | `id.uniqueQualifier` | 같은 시각에 여러 이벤트가 있을 때 서로 가르는 값입니다. | [13] |
| Okta | `uuid` | 폴링 요청(polling request)은 이벤트가 로그에 저장된 순서로 돌려주므로 `published` 순서와 어긋날 수 있고, `since`·`until` 을 모두 준 요청은 `published` 순서를 보장합니다. `since`·`until` 로 직접 페이지를 넘기면 이벤트가 빠지거나 겹칠 수 있어 응답의 `next` 링크를 따라갑니다. | [15] |
| Box | 이벤트 ID | `admin_logs` 는 시간순이고 중복이 없지만, `admin_logs_streaming` 은 순서가 뒤섞이고 중복이 생길 수 있어 이벤트 ID 로 가려냅니다. | [18] |
| Dropbox | — | 팀 이벤트 목록은 `timestamp` 순서로 정렬된다는 보장이 없습니다. | [19] |

## 읽는 법

1. 받은 파일의 겉모양을 위 표로 확인합니다. CloudTrail 은 gzip 을 풀고 `Records` 배열을, 이벤트 허브로 받은 Azure 로그는 `records` 배열을 꺼냅니다. Azure 저장소 블롭 `PT1H.json` 은 한 줄씩 읽습니다.
2. 이중 인코딩을 풉니다. UAL CSV 의 `AuditData` 는 문자열이라 한 번 더 JSON 으로 바꿔야 합니다. Excel 에서는 Power Query 편집기에서 `AuditData` 열을 JSON 으로 변환한 뒤 펼칩니다[9].
3. 고유 ID 로 중복을 걸러 내고, 순서는 파일 순서가 아니라 시각 필드로 다시 정렬합니다. 어떤 시각 필드로 정렬할지는 [클라우드 로그의 시각](timestamps.md)을 봅니다.
4. 한 동작이 여러 레코드로 나뉘었는지 확인합니다. Azure 는 `operationId`·`correlationId`, Entra MFA 는 `correlationId`, CloudTrail 교차 계정 호출은 `sharedEventID` 로 묶습니다.
5. 레코드 원문을 그대로 남깁니다. 보고서에는 레코드의 `eventID`·`Id`·`insertId`·`uuid` 같은 고유 ID 를 함께 적어 원본에서 다시 찾을 수 있게 합니다.

범용 도구로는 `jq` 와 PowerShell 의 `ConvertFrom-Json` 으로 충분합니다. 아래 명령은 CloudTrail 파일에서 레코드를 한 줄씩 꺼내 필요한 필드만 보는 예입니다.

```sh
zcat 123456789012_CloudTrail_us-east-1_20260901T0215Z_EXAMPLEa1b2c3d4e.json.gz \
  | jq -c '.Records[] | {eventTime, eventName, eventID, sourceIPAddress}'
```

UAL CSV 는 PowerShell 에서 `AuditData` 열을 풀어 읽습니다.

```powershell
Import-Csv .\ual.csv | ForEach-Object { $_.AuditData | ConvertFrom-Json } |
  Select-Object Id, CreationTime, Operation, UserId, ClientIP
```

## 포렌식에서 중요한 점

**증명하는 것.** JSON 레코드 한 줄은 "그 서비스가 그 요청을 이렇게 기록했다" 까지 증명합니다. 고유 ID 와 시각, 행위자 필드가 있으면 이 레코드를 다른 수집본에서도 같은 레코드로 짚어 낼 수 있습니다.

**증명하지 못하는 것.** 필드가 비었거나 잘렸다고 해서 요청 내용이 없었다는 뜻은 아닙니다. CloudTrail 은 `requestParameters`·`responseElements`·`serviceEventDetails` 가 100 KB, `additionalEventData` 가 28 KB 를 넘으면 내용을 빼고, `userAgent`·`errorCode`·`errorMessage`·`requestID` 는 1 KB 를 넘으면 자릅니다[1]. 최대 이벤트 크기를 1 MB 로 설정한 이벤트 데이터 저장소는 이벤트 전체가 1 MB 를 넘고 필드 한도도 넘을 때만 빼거나 자릅니다[1]. 읽기 전용 API 는 `responseElements` 가 원래 null 입니다[1]. 레코드 순서도 증거가 되지 못합니다. 파일 안 순서나 API 가 돌려준 순서는 발생 순서가 아닐 수 있습니다[3][11][15][19].

**늦게 온 레코드와 고친 레코드.** CloudTrail 레코드에 `addendum` 이 붙어 있으면 배달이 늦었거나 나중에 내용을 보탠 레코드입니다[1]. `reason` 이 `DELIVERY_DELAY` 면 배달 지연, `UPDATED_DATA` 면 빠졌거나 틀린 필드를 고친 것, `SERVICE_OUTAGE` 면 서비스 장애로 기록하지 못했던 것이고, `UPDATED_DATA` 일 때는 `updatedFields`, `originalRequestID`, `originalEventID` 로 원래 레코드와 잇습니다[1]. Google Cloud 의 덧붙임 조각(`_An:유닉스시각.json`)과 Azure `PT1H.json` 블롭도 늦게 들어온 레코드를 담습니다[6][7]. 한 시간 파일만 보고 그 시간대 기록을 다 봤다고 판단하지 않습니다.

**수집본마다 모양이 다릅니다.** 같은 UAL 이라도 도구마다 펼치는 방식이 다릅니다. 겉 필드를 남기는 도구, `AuditData` 만 남기는 도구, 객체를 문자열로 다시 바꾸는 도구가 있습니다(아래 도구 절). 수집한 도구와 옵션을 기록해 두어야 나중에 다른 수집본과 대조할 수 있고, 보존 절차는 [로그 보존](../../03-techniques/acquisition/log-preservation.md)에서 다룹니다. 레코드가 지워지거나 로깅 설정이 바뀐 흔적은 [로그 조작](../../04-scenarios/infrastructure/log-tampering.md)에서 다룹니다.

## 함정

- UAL 겉 필드와 `AuditData` 안 필드는 이름이 다릅니다. 겉은 `CreationDate`·`UserIds`·`Operations` 이고, 안은 `CreationTime`·`UserId`·`Operation` 입니다[9][10]. Graph 로 받은 UAL 은 필드 이름이 `createdDateTime`, `clientIp`, `operation`, `userPrincipalName` 같은 camelCase 입니다[12][23].
- UAL 의 `ResultStatus` 는 워크로드마다 뜻이 다릅니다. Entra STS 로그온 이벤트에서 `Succeeded` 는 HTTP 요청이 성공했다는 뜻일 뿐이고, 로그온의 성패는 `LogonError` 로 봅니다[10]. Exchange 관리 활동은 `True`·`False` 로 적습니다[10].
- UAL 의 Entra 관련 이벤트는 관리자가 한 작업도 `UserType` 이 `0`(일반 사용자)으로 남습니다. 누가 했는지는 `UserId` 로 봅니다[10].
- Azure 활동 로그는 저장소·이벤트 허브로 받은 것과 REST API 로 받은 것의 필드 이름이 다릅니다. `time` 은 `eventTimestamp`, `operationName` 은 `operationName.value`, `resultType` 은 `status.value`, `callerIpAddress` 는 `httpRequest.clientIpAddress` 에 해당하고, `durationMs` 는 REST API 쪽에 대응하는 필드가 없습니다[5]. 저장소 형식의 `location` 은 자원의 위치가 아니라 이벤트를 처리한 위치입니다[5].
- Log Analytics 의 `AzureActivity` 테이블에서는 같은 값이 대소문자만 다르게 들어 있을 수 있어서, 비교할 때 `=~` 연산자나 `tolower()` 를 씁니다[4].
- Okta 의 `target` 배열은 같은 `eventType` 이라도 `User`·`AppInstance` 같은 대상 종류가 늘 같은 자리에 있지 않습니다. `target[0]` 처럼 위치로 읽지 말고 `type` 으로 찾습니다[16].
- Google Workspace 의 `actor.profileId` 는 Workspace 사용자가 아니면 없거나 자리 표시 ID `105250506097979753968` 일 수 있습니다[13]. 이 값이 여러 레코드에 같다고 같은 사람이라고 판단하지 않습니다.
- CloudTrail 의 `eventContext` 는 이벤트 데이터 저장소에만 있고, 이벤트 기록·트레일 파일에는 없습니다[1]. `eventVersion` 은 2026년 9월 문서 기준 1.11 이고, 필드를 없애거나 표현을 바꾸는 호환되지 않는 변경이 있으면 앞자리가 올라갑니다[1]. 오래된 파일과 새 파일을 한 스크립트로 읽을 때 이 값을 먼저 봅니다.

## 도구

- **jq·PowerShell `ConvertFrom-Json`**: 어떤 서비스의 JSON 이든 겉 배열을 꺼내고 필드를 고르는 데 씁니다.
- **Microsoft-Extractor-Suite `Get-UAL`**: UAL 을 CSV·JSON·JSONL·SOF-ELK 형식으로 내보내고(`-Output`), 여러 파일을 하나로 합칠 수 있습니다(`-MergeOutput`)[22]. `-AuditDataOnly` 를 주면 `CreationDate`·`UserIds`·`Operations` 같은 겉 필드를 버리고 풀어 낸 `AuditData` 만 남깁니다[22].
- **Microsoft-Extractor-Suite `Get-UALGraph`**: Graph 로 UAL 을 받고, CSV 로 쓸 때 객체인 `auditData` 를 `ConvertTo-Json -Depth 100` 으로 다시 문자열로 바꿔 한 칸에 넣습니다[23].
- **Untitled Goose Tool**: 검색 세션마다 `AuditData` 를 풀어 한 줄에 레코드 하나인 `ual_시작_끝.json` 파일로 저장합니다[24].
- **Hawk**: 로그인 기록의 `AuditData` 를 `ConvertFrom-Json` 으로 풀고, 풀리지 않은 레코드는 따로 모읍니다[25].

여러 서비스의 레코드를 한 시간 축에 모으는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)에서, Microsoft 365 로그를 받는 절차는 [Microsoft 365 수집](../../03-techniques/acquisition/m365-collection.md)에서 다룹니다.

## 참고 문헌

1. AWS, "CloudTrail record contents for management, data, and network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
2. AWS, "CloudTrail log file examples", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-examples.html
3. AWS, "Getting and viewing your CloudTrail log files", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/get-and-view-cloudtrail-log-files.html
4. Microsoft, "Activity Log in Azure Monitor" (ms.date 2026-05-04). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
5. Microsoft, "Azure Activity Log event schema" (ms.date 2026-03-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
6. Microsoft, "Resource logs in Azure Monitor" (ms.date 2025-07-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs.md
7. Google Cloud, "View logs routed to Cloud Storage" (2026-09-25 갱신). https://cloud.google.com/logging/docs/export/storage
8. Google Cloud, "LogEntry", Cloud Logging API 참조 (2026-09-04 갱신). https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry
9. Microsoft, "Export, configure, and view audit log records", Microsoft Learn (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-export-records
10. Microsoft, "Office 365 Management Activity API schema", Microsoft Learn (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
11. Microsoft, "Office 365 Management Activity API reference", Microsoft Learn (2024-12-03 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference
12. Microsoft, "auditLogRecord resource type", Microsoft Graph 참조 (2026-08-14 갱신). https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogrecord
13. Google, "Method: activities.list", Admin SDK Reports API 참조 (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
14. Google, "Login Audit Activity Events", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/login
15. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
16. Okta, Management API OpenAPI 명세 2025.08.0 판 (LogEvent 스키마). https://github.com/okta/okta-management-openapi-spec/blob/master/dist/2025.08.0/management-minimal.yaml
17. Slack, "Monitoring your workspace with audit logs". https://api.slack.com/admins/audit-logs
18. Box, "Enterprise events", Box Developer 문서. https://developer.box.com/guides/events/enterprise-events/for-enterprise/
19. Dropbox, dropbox-api-spec `team_log.stone`. https://github.com/dropbox/dropbox-api-spec/blob/master/team_log.stone
20. Microsoft, "Non-interactive sign-in logs" (ms.date 2026-02-09). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-noninteractive-sign-ins.md
21. Microsoft, "Learn about the sign-in log activity details" (ms.date 2026-03-04). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
22. Invictus IR, Microsoft-Extractor-Suite `Get-UAL.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-UAL.ps1
23. Invictus IR, Microsoft-Extractor-Suite `Get-UALGraph.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-UALGraph.ps1
24. CISA, Untitled Goose Tool `m365_datadumper.py`. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/m365_datadumper.py
25. T0pCyber, Hawk `Get-HawkUserUALSignInLog.ps1`. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/User/Get-HawkUserUALSignInLog.ps1
26. Google Cloud, "Understanding audit logs" (2026-09-25 갱신). https://cloud.google.com/logging/docs/audit/understanding-audit-logs
