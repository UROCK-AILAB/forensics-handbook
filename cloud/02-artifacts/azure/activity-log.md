---
title: "활동 로그"
parent: "아티팩트 · Azure"
nav_order: 460
---

# 활동 로그 (Activity Log)

활동 로그는 Azure 구독의 리소스를 만들고 고치고 지운 관리 작업을 누가, 언제, 어떤 결과로 했는지 남기는 기록이고, 설정하지 않아도 90일 동안 남습니다[1].

## 무엇을 기록하나 · 왜 생기나

Azure Resource Manager(ARM)를 거치는 관리 작업, 곧 제어 평면 (control plane) 작업이 활동 로그에 남습니다. 가상 머신을 만들거나, Key Vault 액세스 정책을 바꾸거나, 배포가 실패한 일이 그 예입니다[1]. 기록은 대개 만들기·수정·삭제와 동작(action) 작업에서 생기고, 읽기 작업은 대개 남지 않습니다[1]. 리소스 안에서 일어난 데이터 평면 (data plane) 작업, 예를 들어 Key Vault 비밀 값을 가져오거나 데이터베이스에 요청한 일은 활동 로그가 아니라 리소스 로그에 남습니다[1]. 관리·데이터 평면의 구분은 [로그의 종류](../../01-foundations/logging/log-types.md)에, 리소스 로그는 [리소스 로그와 진단 설정](./resource-logs.md)에 있습니다.

활동 로그는 기본으로 모이고 따로 켤 필요가 없습니다. 시스템이 만든 항목이라 사용자가 바꾸거나 지울 수 없습니다[1]. 누가 리소스를 만들었는지는 활동 로그에만 남습니다[1]. 그래서 "이 가상 머신은 누가 만들었나", "이 역할 할당은 누가 추가했나" 같은 질문은 활동 로그에서 시작합니다.

이벤트마다 범주 (category) 가 하나 붙습니다[2].

| 범주 | 담는 것 |
|---|---|
| Administrative | ARM 으로 한 모든 만들기·수정·삭제·동작. 구독의 Azure RBAC 변경도 여기 들어감 |
| Service Health | 구독의 리소스에 영향을 준 Azure 서비스 장애·점검 |
| Resource Health | 리소스 상태 변화(Available·Unavailable·Degraded·Unknown), 플랫폼이 시작했는지 사용자가 시작했는지 |
| Alert | Azure 경고가 울린 기록 |
| Autoscale | 자동 크기 조정 엔진의 동작 |
| Recommendation | Azure Advisor 권장 사항 |
| Security | Microsoft Defender for Cloud 경고 |
| Policy | Azure Policy 가 Audit·Deny 같은 효과를 적용한 기록 |

조사에서 주로 보는 것은 Administrative 입니다. 작업 종류가 Write·Delete·Action 이면 작업이 시작된 기록과 성공 또는 실패한 기록이 둘 다 남습니다[2]. Policy 범주에서 Audit 는 수준(level)이 `Warning`, Deny 는 `Error` 이고, Deny 된 평가의 상태는 `Failed` 입니다[2].

## 위치와 범위별 차이

### 세 가지 범위

활동 로그는 구독 수준이 기본입니다. 이와 별도로 테넌트 수준과 관리 그룹 수준 기록이 있습니다[1]. 구독·관리 그룹·테넌트의 관계는 [테넌트·구독·계정·프로젝트](../../01-foundations/model/tenancy.md)에서 다룹니다.

| 범위 | 담는 것 | 조회 방법 |
|---|---|---|
| 구독 | 리소스 공급자가 직접 만든 이벤트까지 담음. 기본 범위 | 포털 구독 > Activity log, `az monitor activity-log list`, `Get-AzActivityLog`, REST |
| 테넌트 | 관리 그룹이나 구독을 만든 일처럼 수는 적지만 중요한 이벤트. ARM 이벤트만 | 포털 Monitor > Activity log 에서 **Directory Activity** 선택, REST(`az rest`·`Invoke-AzRestMethod`) |
| 관리 그룹 | 정책 할당, 관리 그룹 멤버십 변경. ARM 이벤트만 | 포털 관리 그룹 > Activity log, REST(api-version `2017-03-01-preview` 필수) |

테넌트·관리 그룹 수준 기록에는 ARM 밖에서 리소스 공급자가 직접 만든 이벤트가 들어가지 않습니다[1]. 테넌트 수준과 관리 그룹 수준에는 CLI·PowerShell 전용 명령이 없어서 REST 를 직접 부릅니다[1].

REST 로 받을 때 주소는 다음과 같습니다[1].

```text
구독:      GET https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Insights/eventtypes/management/values?api-version=2015-04-01&$filter=eventTimestamp ge '{startTime}' and eventTimestamp le '{endTime}'
테넌트:    GET https://management.azure.com/providers/Microsoft.Insights/eventtypes/management/values?api-version=2015-04-01&$filter=...
관리 그룹: GET https://management.azure.com/providers/Microsoft.Management/managementGroups/{managementGroupId}/providers/Microsoft.Insights/eventtypes/management/values?api-version=2017-03-01-preview&$filter=...
```

`$filter` 에는 `eventTimestamp` 시작값이 반드시 들어가야 하고, 시작과 끝이 모두 90일 안에 있어야 합니다. 필터에는 시각 범위에 더해 `resourceGroupName`, `resourceUri`, `resourceProvider`, `correlationId` 조건을 붙일 수 있습니다. 요청 제한 시간은 `Prefer` 헤더로 정할 수 있고 최대 75초(`Prefer: wait=75`)입니다[1].

### 보관 기간과 내보내기 (2026년 9월 문서 기준)

| 보관 위치 | 보관 기간 | 비용 | 켜는 방법 |
|---|---|---|---|
| 활동 로그 자체 | 90일 뒤 삭제 | 없음 | 기본 |
| Log Analytics 작업 영역(`AzureActivity` 표) | 최소 90일 무료, 늘리면 최대 12년(4,383일). CLI·PowerShell 로는 7년까지 | 수집 요금 없음, 90일을 넘긴 기간만 보관 요금 | 진단 설정 |
| Storage 계정 | 90일보다 오래 둘 수 있음 | — | 진단 설정 |
| Event Hubs | 외부 SIEM 으로 넘기는 통로 | — | 진단 설정 |

근거: 보관·비용[1][3], 12년·7년 한도[3]. Storage 목적지의 보관 관리는 [리소스 로그와 진단 설정](./resource-logs.md)에서 다룹니다.

90일을 넘는 기록은 진단 설정 (diagnostic setting) 으로 미리 내보내 둔 곳에만 있습니다[1]. 그래서 사고를 알게 되면 먼저 구독과 관리 그룹에 활동 로그용 진단 설정이 있는지, 목적지가 어디인지 확인합니다. 포털에서는 Monitor > Activity log > **Export Activity Logs** 에서 볼 수 있습니다[1]. 옛 내보내기 방식은 로그 프로필 (log profile) 이고 지금은 꺼 두어야 하는 방식이라[1], 오래된 구독에서는 로그 프로필로 쌓인 옛 사본이 따로 있을 가능성이 있습니다. 보존 절차는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)에 있습니다.

Storage 로 내보내면 컨테이너 `insights-activity-logs` 아래에 한 시간에 하나씩 블롭이 생깁니다[1].

```text
insights-activity-logs/resourceId=/SUBSCRIPTIONS/{subscription ID}/y={yyyy}/m={MM}/d={dd}/h={HH}/m=00/PT1H.json
```

경로의 `m=00` 은 블롭이 시간 단위라 늘 `00` 입니다[1]. Storage 에 쓰는 형식은 2018년 11월 1일에 JSON Lines 로 바뀌었고[2], 그 뒤로는 한 줄에 이벤트 하나가 JSON 객체로 들어갑니다[1]. Event Hubs 로 보내면 `records` 배열로 감싼 JSON 으로 나옵니다[1].

## 구조

활동 로그는 가져온 경로에 따라 필드 이름이 셋으로 갈립니다. REST·포털·CLI·PowerShell 로 받은 것, Storage·Event Hubs 로 내보낸 것, Log Analytics 의 `AzureActivity` 표가 각각 다릅니다[2][4]. 포털에서 이벤트를 **JSON** 으로 보면 REST 와 같은 모양입니다[2].

### REST 형식

다음은 사용자가 구독에 역할 할당을 추가한 Administrative 이벤트를 가정해 만든 예시입니다. 필드 구성은 문서의 Administrative 예시를 따랐고[2], 구독 ID·GUID·메일 주소·IP 는 모두 지어낸 값입니다.

```json
{
  "authorization": {
    "action": "Microsoft.Authorization/roleAssignments/write",
    "scope": "/subscriptions/ffff9f9f-aa0a-bb1b-cc2c-dddddd3d3d3d/providers/Microsoft.Authorization/roleAssignments/abab1212-cdcd-3434-efef-565656787878"
  },
  "caller": "alice@contoso.com",
  "channels": "Operation",
  "claims": {
    "aud": "https://management.core.windows.net/",
    "iss": "https://sts.windows.net/eeee5e5e-ff6f-aa7a-bb8b-cccccc9c9c9c/",
    "iat": "1788220200", "nbf": "1788220200", "exp": "1788224100",
    "http://schemas.microsoft.com/claims/authnmethodsreferences": "pwd,mfa",
    "appid": "12121212-3434-5656-7878-909090909090",
    "ipaddr": "203.0.113.25",
    "http://schemas.microsoft.com/identity/claims/objectidentifier": "0a0a0a0a-1b1b-2c2c-3d3d-4e4e4e4e4e4e",
    "http://schemas.microsoft.com/identity/claims/tenantid": "eeee5e5e-ff6f-aa7a-bb8b-cccccc9c9c9c",
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn": "alice@contoso.com"
  },
  "correlationId": "c0c0c0c0-d1d1-e2e2-f3f3-a4a4a4a4a4a4",
  "eventDataId": "b1b1b1b1-c2c2-d3d3-e4e4-f5f5f5f5f5f5",
  "eventName": { "value": "EndRequest", "localizedValue": "End request" },
  "category": { "value": "Administrative", "localizedValue": "Administrative" },
  "eventTimestamp": "2026-09-01T02:31:07.1234567Z",
  "httpRequest": { "clientRequestId": "d6d6d6d6-e7e7-f8f8-a9a9-b0b0b0b0b0b0", "clientIpAddress": "203.0.113.25", "method": "PUT" },
  "level": "Informational",
  "operationId": "a9a9a9a9-b8b8-c7c7-d6d6-e5e5e5e5e5e5",
  "operationName": { "value": "Microsoft.Authorization/roleAssignments/write", "localizedValue": "Microsoft.Authorization/roleAssignments/write" },
  "resourceId": "/subscriptions/ffff9f9f-aa0a-bb1b-cc2c-dddddd3d3d3d/providers/Microsoft.Authorization/roleAssignments/abab1212-cdcd-3434-efef-565656787878",
  "status": { "value": "Succeeded", "localizedValue": "Succeeded" },
  "subStatus": { "value": "Created", "localizedValue": "Created (HTTP Status Code: 201)" },
  "submissionTimestamp": "2026-09-01T02:31:26.7654321Z",
  "subscriptionId": "ffff9f9f-aa0a-bb1b-cc2c-dddddd3d3d3d"
}
```

대부분의 필드는 `value` 와 `localizedValue` 쌍이라 기계 비교에는 `value` 를 씁니다[2]. 주요 필드의 뜻은 다음과 같습니다[2].

| 필드 | 담는 것 | 읽을 때 주의 |
|---|---|---|
| `caller` | 작업한 주체의 메일 주소, UPN 클레임, SPN 클레임 가운데 있는 것 | 사람 이름이 아닐 수 있음. 아래 "함정" 참고 |
| `claims` | ARM 인증에 쓴 JWT 토큰의 클레임 | `objectidentifier`·`appid`·`upn`·`authnmethodsreferences`(예: `pwd`, `rsa,mfa`)·`ipaddr`·`tenantid` 등 |
| `authorization` | RBAC 판단 정보. 대개 `action`·`role`·`scope` | 내보낸 형식의 예시에는 `evidence` 에 역할 이름·할당 범위·할당 ID·역할 정의 ID·주체 ID·주체 종류가 들어 있음 |
| `httpRequest` | `clientRequestId`·`clientIpAddress`·`method` | 포털에서 이벤트를 볼 때는 빠짐(요청 원문에 민감한 정보가 있을 수 있어서) |
| `correlationId` | 한 덩어리 작업에 속한 이벤트들이 공유하는 GUID | 같은 상위 작업의 이벤트를 묶는 열쇠 |
| `operationId` | 한 작업의 이벤트들이 공유하는 GUID | 시작·끝 이벤트를 짝짓는 열쇠 |
| `eventDataId` | 이벤트 하나의 고유 ID | `id` 안에도 들어 있음 |
| `eventName` | `BeginRequest`·`EndRequest` 등 | 시작과 끝 구분 |
| `operationName` | ARM 작업 이름. `Microsoft.공급자/형식/.../write` 형식 | 탐지 규칙이 거는 필드 |
| `status`·`subStatus` | `Started`·`Succeeded`·`Failed` 등, 그리고 대개 HTTP 상태(`Created`, `Conflict` 등) | 성공 여부는 둘을 함께 봄 |
| `level` | `Critical`·`Error`·`Warning`·`Information`/`Informational` | 수준은 리소스 공급자 개발자가 정함 |
| `eventTimestamp`·`submissionTimestamp` | 이벤트 생성 시각과 조회 가능해진 시각 | 아래 "시각 해석" 참고 |

문서 예시에서 `id` 는 `.../events/{eventDataId}/ticks/{ticks}` 형식이고, 끝의 ticks 는 `eventTimestamp` 와 같은 순간을 .NET 틱(100나노초 단위)으로 적은 값입니다[2]. 이 스키마는 강제되지 않아서 서비스나 국가 클라우드에 따라 필드가 더 붙을 수 있습니다[2]. 범주마다 쓰는 필드도 다르고, 예를 들어 Alert 이벤트의 `caller` 는 늘 `Microsoft.Insights/alertRules` 입니다[2].

### Storage·Event Hubs 로 내보낸 형식

진단 설정으로 내보내면 이벤트가 리소스 로그 공통 스키마로 바뀝니다[2].

| 내보낸 필드 | REST 필드 | 비고 |
|---|---|---|
| `time` | `eventTimestamp` | |
| `resourceId` | `resourceId` | 구독 ID·리소스 형식·리소스 그룹은 여기서 읽어 냄 |
| `operationName` | `operationName.value` | |
| `category` | 작업 이름의 일부 | 아래 "함정" 참고 |
| `resultType` | `status.value` | |
| `resultSignature` | `subStatus.value` | 예시 값 `Succeeded.Created` |
| `resultDescription` | `description` | |
| `callerIpAddress` | `httpRequest.clientIpAddress` | |
| `correlationId` | `correlationId` | |
| `identity` | `claims` 와 `authorization` | `identity.claims`, `identity.authorization.evidence` |
| `location` | 없음 | 이벤트를 처리한 곳. 리소스 위치가 아님 |
| `properties.eventCategory` | `category` | 없으면 Administrative |
| `properties.eventName`·`properties.operationId` | `eventName`·`operationId` | |

이 형식에는 `caller` 필드가 따로 없어서, 주체는 `identity.claims` 의 클레임으로 찾습니다[2].

### Log Analytics 의 `AzureActivity` 표

Log Analytics 로 보내면 `AzureActivity` 표에 들어가고 열 이름이 다시 바뀝니다[4]. `OperationNameValue`(예: `Microsoft.Storage/storageAccounts/listAccountSas/action`), `ActivityStatusValue`, `ActivitySubstatusValue`, `CategoryValue`, `Caller`, `CallerIpAddress`, `Claims_d`, `Authorization_d`, `Properties_d`, `HTTPRequest`, `CorrelationId`, `OperationId`, `EventDataId`, `Level`, `ResourceGroup`, `ResourceProviderValue`, `SubscriptionId`, `_ResourceId`, `Hierarchy`(관리 그룹 계층), `TimeGenerated`, `EventSubmissionTimestamp` 가 조사에 쓰는 열입니다[4]. `TenantId` 열은 Entra 테넌트가 아니라 Log Analytics 작업 영역 ID 입니다[4]. `Claims`·`Authorization`·`Properties` 는 문자열 열이고 `_d` 가 붙은 열이 동적(dynamic) 형식이라 필드를 꺼낼 때는 `_d` 열을 씁니다[4].

## 증거로서 의미

**증명하는 것.** 이 시각에 이 주체(`caller`, 클레임의 `objectidentifier`·`appid`)가 이 리소스(`resourceId`)에 이 ARM 작업(`operationName`)을 요청했고 결과가 어땠는지(`status`·`subStatus`)를 보여 줍니다[2]. `authorization.evidence` 가 있으면 어떤 역할 할당 덕분에 허용됐는지도 보입니다[2]. 클레임의 `authnmethodsreferences` 에 든 `pwd`, `rsa,mfa` 같은 값은 인증 방법을 추정하는 단서입니다[2]. 리소스를 누가 만들었는지는 활동 로그에만 남으므로, 생성자를 밝히는 근거는 이 기록입니다[1].

**증명하지 못하는 것.** 데이터 평면 작업은 남지 않습니다. 블롭을 내려받았는지, 비밀 값을 읽었는지는 활동 로그로 알 수 없습니다[1]. 읽기 작업도 대개 없습니다[1]. 예를 들어 `listKeys/action` 이 남아 있으면 키 목록을 요청했다는 것까지이고, 그 키로 무엇을 했는지는 Storage·Key Vault 기록을 따로 봐야 합니다([Storage 계정 기록](./storage-logs.md), [Key Vault 기록](./key-vault.md)). 90일을 넘은 기록은 내보내 두지 않았으면 없습니다[1]. `level` 은 공급자 개발자가 정한 값이라 사건의 심각도를 판단하는 근거로 삼기 어렵습니다[2]. 레코드는 계정이나 서비스 주체를 가리킬 뿐 키보드 앞의 사람을 가리키지 않습니다. 보고서에는 "이 시각에 이 계정으로 구독에 역할 할당을 만든 요청이 성공한 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다. 문장 쓰는 법은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)에 있습니다.

## 시각 해석

`eventTimestamp` 는 요청을 처리한 Azure 서비스가 이벤트를 만든 시각이고, `submissionTimestamp` 는 그 이벤트를 조회할 수 있게 된 시각입니다[2]. 문서 예시의 두 시각은 모두 끝에 `Z` 가 붙은 UTC ISO 8601 이고, Administrative 예시에서는 두 값이 `20:42:31.3810679Z` 와 `20:42:50.0724829Z` 로 19초 벌어져 있습니다[2]. 타임라인에는 `eventTimestamp` 를 씁니다. 소수 자릿수는 예시마다 7자리·6자리·3자리·2자리로 달라서[1][2] 문자열이 아니라 시각으로 파싱해 정렬합니다.

활동 로그 항목은 보통 이벤트가 일어난 뒤 3~20분 안에 분석과 경고에 쓸 수 있게 됩니다[1][5]. 방금 한 작업이 바로 보이지 않는 것은 이 지연 때문일 수 있습니다.

Administrative 작업 하나에는 시작 이벤트와 끝 이벤트가 따로 있어서 시각이 둘 이상입니다[2]. `operationId`·`correlationId` 로 묶고 `eventName`(`BeginRequest`/`EndRequest`)과 `status` 로 구분합니다.

Storage 로 내보낸 `PT1H.json` 은 그 시간에 **받은** 이벤트를 담고, 이벤트가 만들어진 시각과는 상관없이 덧붙습니다[1]. 경로의 `h=` 값과 레코드 안의 `time` 이 어긋날 수 있으니, 범위를 잡아 블롭을 모을 때는 앞뒤 시간 블롭까지 함께 받습니다.

`AzureActivity` 표의 `TimeGenerated` 는 이벤트를 만든 시각이고 `EventSubmissionTimestamp` 는 조회할 수 있게 된 시각입니다[4]. Log Analytics 는 `TimeGenerated` 가 받은 시각보다 2일 넘게 이르거나 하루 넘게 미래이면 그 값을 받은 시각으로 바꿔 씁니다[5]. 여러 로그의 시각을 맞추는 원칙은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 있습니다.

## 함정과 한계

- **경로마다 다른 필드 이름.** 같은 이벤트가 REST 에서는 `eventTimestamp`·`operationName.value`, Storage 에서는 `time`·`operationName`·`resultType`, Log Analytics 에서는 `TimeGenerated`·`OperationNameValue`·`ActivityStatusValue` 입니다[2][4]. 도구 출력마다 필드 대응표를 먼저 맞춥니다.
- **대소문자.** `AzureActivity` 의 문자열 값은 같은 값이라도 대소문자가 다를 수 있어서 `=~` 나 `tolower()` 로 비교합니다[1]. Sigma 규칙도 `MICROSOFT.KEYVAULT/VAULTS/WRITE` 처럼 대문자로 적은 것이 있어서[6] 대소문자를 무시하고 비교합니다.
- **`caller` 의 모양.** REST 스키마는 `caller` 를 메일 주소·UPN·SPN 가운데 있는 것이라고 하고[2], `AzureActivity` 표 설명은 "호출자의 GUID" 라고 합니다[4]. 실제 데이터의 값이 어떤 모양인지 보고 판단하고, 주체를 확정할 때는 클레임의 `objectidentifier` 를 씁니다.
- **내보낸 형식의 설명과 예시가 다름.** 대응표 설명으로는 `category` 가 늘 "Administrative", `durationMs` 가 늘 0 이지만, 같은 문서의 예시에는 `"category": "Write"`, `"durationMs": 2826` 이 들어 있습니다[2]. 실제 데이터에서 값을 확인하고, `category` 대신 `properties.eventCategory` 로 범주를 구분합니다.
- **수준 값.** REST 스키마의 수준은 `Critical`·`Error`·`Warning`·`Information`/`Informational` 이고[2], `AzureActivity` 표 설명에는 `Verbose` 도 있습니다[4]. `Information` 과 `Informational` 을 같은 값으로 묶습니다.
- **중복 이벤트.** 관리 그룹과 그 아래 구독에 모두 진단 설정이 있으면 같은 이벤트가 두 번 들어옵니다[1]. Log Analytics 에서는 모든 필드의 해시로 걷어 냅니다[1].

  ```kusto
  AzureActivity
  | extend Hash = hash(dynamic_to_json(pack_all()))
  | summarize arg_max(TimeGenerated, *) by Hash
  ```

- **PowerShell 출력 직렬화.** `Get-AzActivityLog` 결과는 `ConvertTo-Json` 으로 제대로 직렬화되지 않는 문제가 있어서, DFIR-O365RC 는 Newtonsoft.Json 으로 직접 직렬화합니다[7]. 직접 스크립트를 짤 때는 REST 로 받는 편이 원형을 지키기 쉽습니다.
- **지우기와 숨기기.** 활동 로그 자체는 사용자가 지울 수 없습니다[1]. 대신 내보내기를 끊는 일은 가능하고, 그 행위도 ARM 작업이라 활동 로그에 남을 수 있습니다. 작업 이름은 `Microsoft.Insights/DiagnosticSettings/Delete`·`/Write`, `Microsoft.Insights/LogProfiles/Delete`·`/Write` 입니다[8]. 90일 안이면 활동 로그에서 이 작업을 먼저 찾습니다.

## 직접 분석해 보기

**`id` 의 ticks 로 시각을 한 번 확인하기.** 문서 예시의 `id` 끝 ticks `636528553513810679` 는 0001-01-01 부터 센 100나노초 단위 값입니다. 여기서 1970-01-01 의 ticks `621355968000000000` 을 빼면 `15172585513810679` 이고, 10,000,000 으로 나누면 유닉스 시각 `1517258551.3810679` 초가 됩니다. 이 값은 UTC `2018-01-29T20:42:31.3810679Z` 로, 같은 이벤트의 `eventTimestamp` 와 같습니다[2]. `eventTimestamp` 가 빠지거나 가공된 사본에서 `id` 만 남아 있을 때 이렇게 시각을 거꾸로 계산할 수 있습니다.

```sh
python3 -c "import datetime;t=636528553513810679-621355968000000000;print(datetime.datetime(1970,1,1)+datetime.timedelta(microseconds=t//10))"
```

**REST 로 받은 파일 읽기.** Microsoft-Extractor-Suite 의 `Get-ActivityLogs` 는 구독마다 REST 응답의 `value` 를 `nextLink` 를 따라 모두 모아 JSON 배열 하나로 저장합니다[9]. jq 로 이벤트를 한 줄씩 펼치고 시각 순으로 정렬합니다. 파일 이름은 만든 예시입니다.

```sh
jq -c '.[] | {t: .eventTimestamp, ev: .eventName.value, op: .operationName.value,
    st: .status.value, sub: .subStatus.value, caller,
    oid: .claims["http://schemas.microsoft.com/identity/claims/objectidentifier"],
    ip: .httpRequest.clientIpAddress, res: .resourceId, corr: .correlationId}' \
  20260901023000-ffff9f9f-aa0a-bb1b-cc2c-dddddd3d3d3d-ActivityLog.json | sort
```

**Storage 로 내보낸 블롭 읽기.** `PT1H.json` 은 한 줄에 이벤트 하나이므로 `jq -c '{time, operationName, resultType, resultSignature, callerIpAddress, correlationId, upn: .identity.claims["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn"]}' PT1H.json` 처럼 바로 읽습니다[1][2].

**Log Analytics 에서 생성자 찾기.** 리소스를 만든 주체를 찾을 때는 쓰기 작업의 성공 기록을 봅니다[1][4].

```kusto
AzureActivity
| where OperationNameValue =~ "Microsoft.Compute/virtualMachines/write"
| where ActivityStatusValue =~ "Succeeded"
| project TimeGenerated, Caller, CallerIpAddress, _ResourceId, CorrelationId
| order by TimeGenerated asc
```

**공개 도구.** 수집 도구가 어떤 경로로 받느냐에 따라 출력 형식이 달라집니다.

| 도구 | 받는 방법 | 출력 |
|---|---|---|
| Microsoft-Extractor-Suite `Get-ActivityLogs` | 구독 REST(api-version `2015-04-01`), 구독을 지정하지 않으면 모든 구독, 기본 기간은 89일 전부터 지금까지 | `{yyyyMMddHHmmss}-{구독 ID}-ActivityLog.json`, JSON 배열[9] |
| Microsoft-Extractor-Suite `Get-DirectoryActivityLogs` | 테넌트 수준 REST | 기본 `DirectoryActivityLogs.csv`, JSON·JSONL 선택[10] |
| DFIR-O365RC `Get-AzRMActivityLogs` | 인증서 기반 앱으로 `Get-AzActivityLog -DetailedOutput` 을 한 시간 단위로 호출, 실패하면 다시 시도 | `azure_rm_activity/YYYY-MM-DD/AzRM_{테넌트}_{구독 ID}_YYYY-MM-DD_HH-00-00.json`[7][11] |
| Untitled Goose Tool | 설정의 `[azure]` 절 `activity_log`(기본 `False`)를 켜면 구독마다 하루 단위로 조회 | `{구독 ID}/Activity Log/azure_activity_log_YYYY-MM-DD.json`, 한 줄에 이벤트 하나[12][13] |

DFIR-O365RC 로 받으려면 대상 구독에 `Microsoft.Insights/eventtypes/*` 를 읽을 수 있는 Reader 권한이 필요합니다[11]. 도구 선택과 수집 순서는 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md)에 있습니다.

**탐지 규칙으로 검색하기.** SigmaHQ 의 Azure 활동 로그 규칙은 `operationName` 이나 키워드로 다음 작업을 찾습니다. 작업 이름의 대소문자는 규칙 원문 그대로입니다.

| 찾는 것 | 작업 이름 |
|---|---|
| 역할 할당 추가 | `Microsoft.Authorization/roleAssignments/write`[14] |
| 사용자가 모든 구독을 관리하도록 권한이 올라감 | `MICROSOFT.AUTHORIZATION/ELEVATEACCESS/ACTION`[15] |
| 흔하지 않은 작업 | `Microsoft.Storage/storageAccounts/listKeys/action` 등 `listKeys/action` 다섯 가지, `Microsoft.Compute/snapshots/write`, `Microsoft.Network/networkSecurityGroups/write`[16] |
| Cloud Shell 생성 | `MICROSOFT.PORTAL/CONSOLES/WRITE`[17] |
| Key Vault 수정·삭제 | `MICROSOFT.KEYVAULT/VAULTS/WRITE`, `/DELETE`, `/DEPLOY/ACTION`, `/ACCESSPOLICIES/WRITE`[6] |

규칙이 걸린다고 공격이 있었다는 뜻은 아니고, 관리자의 정상 작업도 같은 이름으로 남습니다[14][16]. 규칙 활용법은 [탐지 규칙으로 로그 검색하기](../../03-techniques/analysis/detection-rules.md)에, 역할 할당을 시간 순으로 따라가는 방법은 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md)에 있습니다.

## 교차 검증

- **로그인 기록.** 클레임의 `objectidentifier`·`appid` 와 시각으로 Entra ID 로그인 로그의 해당 로그인을 찾으면, 그 토큰을 어디서 어떤 인증으로 받았는지 이어 볼 수 있습니다. [Entra ID 로그](../m365/entra-logs/index.md)를 봅니다.
- **데이터 평면 기록.** 활동 로그의 `listKeys/action`, 디스크·스냅숏 작업 뒤에 실제 데이터 접근이 있었는지는 [Storage 계정 기록](./storage-logs.md), [Key Vault 기록](./key-vault.md), [Azure 가상 머신](./azure-vm.md)에서 확인합니다.
- **네트워크 설정 변경.** NSG 규칙이 바뀐 시각 전후의 실제 트래픽은 [네트워크 흐름 로그](./flow-logs.md)에 남습니다.
- **다른 클라우드와 비교하기.** AWS 의 대응 기록은 [CloudTrail](../aws/cloudtrail/index.md)입니다. 여러 로그를 시간순으로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)과 [Windows 판의 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html)을 봅니다.
- IP 주소 해석은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md), JSON 을 읽는 일반 원칙은 [JSON 로그 읽기](../../01-foundations/logging/json-logs.md)에 있습니다.

## 실습

시험용 구독을 하나 만들어 아래 작업을 한 뒤 활동 로그를 받아 풀어 봅니다.

1. 리소스 그룹에 스토리지 계정을 만들고 지웁니다. 만들기 작업에서 `BeginRequest` 와 `EndRequest` 이벤트는 몇 개 남고, 어느 필드로 짝을 지을 수 있나요?
2. 포털 화면에서 본 이벤트와 REST 로 받은 같은 이벤트를 비교해 봅니다. 포털에서 빠진 필드는 무엇인가요?
3. 스토리지 계정의 액세스 키를 포털에서 한 번 봅니다. 활동 로그에 어떤 `operationName` 이 남고, 키를 써서 블롭을 읽은 일은 어디에 남나요?
4. 활동 로그용 진단 설정을 Storage 로 만든 뒤 한 시간 넘게 기다립니다. `PT1H.json` 경로의 `h=` 값과 안에 든 `time` 값이 어긋나는 레코드가 있나요?
5. `id` 끝의 ticks 를 시각으로 바꿔 `eventTimestamp` 와 같은지 확인합니다.

## 참고 문헌

1. Microsoft, "Activity log in Azure Monitor", azure-monitor-docs (ms.date 2026-05-04). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
2. Microsoft, "Azure Activity Log event schema", azure-monitor-docs (ms.date 2026-03-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
3. Microsoft, "Manage data retention in a Log Analytics workspace", azure-monitor-docs (ms.date 2026-09-02). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/data-retention-configure.md
4. Microsoft, "AzureActivity" (Azure Monitor Logs table reference, 2026-07-27). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/azureactivity
5. Microsoft, "Log data ingestion time in Azure Monitor" (2026-07-31). https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-ingestion-time
6. SigmaHQ, azure_keyvault_modified_or_deleted.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_keyvault_modified_or_deleted.yml
7. ANSSI-FR, DFIR-O365RC.psm1 (Get-AzureRMActivityLog). https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/DFIR-O365RC.psm1
8. Microsoft, "Azure permissions for Monitor" (2026-07-01). https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/monitor
9. Invictus IR, Microsoft-Extractor-Suite, Get-AzureActivityLogs.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureActivityLogs.ps1
10. Invictus IR, Microsoft-Extractor-Suite, Get-AzureDirectoryActivityLogs.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureDirectoryActivityLogs.ps1
11. ANSSI-FR, DFIR-O365RC, Get-AzRMActivityLogs.ps1 및 README.md. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/Get-AzRMActivityLogs.ps1 , https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/README.md
12. CISA, Untitled Goose Tool, azure_dumper.py. https://github.com/cisagov/untitledgoosetool/blob/main/goosey/azure_dumper.py
13. CISA, Untitled Goose Tool, README.md. https://github.com/cisagov/untitledgoosetool/blob/main/README.md
14. SigmaHQ, azure_granting_permission_detection.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_granting_permission_detection.yml
15. SigmaHQ, azure_subscription_permissions_elevation_via_activitylogs.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_subscription_permissions_elevation_via_activitylogs.yml
16. SigmaHQ, azure_rare_operations.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_rare_operations.yml
17. SigmaHQ, azure_new_cloudshell_created.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_new_cloudshell_created.yml
