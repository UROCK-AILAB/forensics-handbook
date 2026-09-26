---
title: "Storage 계정 기록"
parent: "아티팩트 · Azure"
nav_order: 490
---

# Storage 계정 기록 (Storage Logs)

Azure Storage 계정에서 블롭을 읽고 쓰고 지운 요청은 데이터 평면 기록인 Storage 리소스 로그(`StorageBlobLogs`)나 클래식 Storage Analytics 로그(`$logs`)에 남고, 계정 키를 받아 가거나 설정을 바꾼 작업은 활동 로그에 남습니다. 두 데이터 평면 기록은 모두 따로 켜야 쌓이고 최선 노력 (best-effort) 방식이라 빠지는 요청이 있습니다[1][5][9].

## 무엇을 기록하나 · 왜 생기나

Storage 계정에 대한 작업은 두 종류로 나뉩니다[3]. 계정을 만들거나 계정 속성을 바꾸는 Azure Resource Manager 요청은 제어 평면 (control plane) 작업이고 [활동 로그](./activity-log.md)에 남습니다. 블롭을 올리거나 내려받는 것처럼 Storage 서비스 끝점으로 들어온 요청은 데이터 평면 (data plane) 작업이고 Storage 리소스 로그에 남습니다[3]. 관리·데이터 평면의 일반 원리는 [로그의 종류](../../01-foundations/logging/log-types.md)에 있습니다.

| 조사 질문 | 기록 | 예 |
|---|---|---|
| 계정 키·SAS 를 누가 받아 갔나 | 활동 로그 | `Microsoft.Storage/storageAccounts/listkeys/action`, `listAccountSas/action`, `listServiceSas/action` |
| 키를 새로 만들었나 | 활동 로그 | `Microsoft.Storage/storageAccounts/regeneratekey/action` |
| 계정을 만들거나 속성·태그·도메인을 바꿨나, 지웠나 | 활동 로그 | `Microsoft.Storage/storageAccounts/write`, `/delete` |
| 불변 정책·법적 보존을 바꿨나 | 활동 로그 | `.../blobServices/containers/immutabilityPolicies/write`·`delete`·`lock/action`·`extend/action`, `.../containers/setLegalHold/action` |
| 진단 설정을 바꿨나 | 활동 로그 | `Microsoft.Storage/storageAccounts/blobServices/providers/Microsoft.Insights/diagnosticSettings/write` |
| 어떤 블롭을 읽고 쓰고 지웠나 | 리소스 로그·`$logs` | `GetBlob`, `PutBlob`, `DeleteBlob` |

작업 이름은 2026년 9월 문서 기준입니다[7]. `listkeys/action` 은 계정 액세스 키를 돌려주는 작업이고, `listAccountSas/action` 과 `listServiceSas/action` 은 계정 SAS·서비스 SAS 토큰을 돌려주는 작업입니다[7]. Sigma 의 드문 작업 규칙은 `Microsoft.Storage/storageAccounts/listKeys/action` 을 탐지 대상에 넣었습니다[11]. 권한 문서는 `listkeys`, Sigma 규칙은 `listKeys` 로 대소문자가 달라서 검색은 대소문자를 구분하지 않게 합니다.

데이터 평면 요청은 요청이 들어온 서비스 끝점에만 기록이 생깁니다[1]. 블롭 끝점에만 요청이 있었다면 블롭 기록만 생기고 큐·테이블 기록은 없습니다[1][5]. Azure 포털에서 계정을 열어 보기만 해도 포털이 부른 작업이 기록되므로, 아무도 데이터를 쓰지 않은 계정에도 기록이 있을 수 있습니다[1].

### 기록되는 요청과 기록되지 않는 요청

| 요청 | 기록 여부 |
|---|---|
| 인증된 요청: 성공, 실패(시간 초과·제한·네트워크·권한 오류 등) | 기록 |
| SAS·OAuth 로 인증한 요청(성공·실패 모두) | 기록 |
| 분석 데이터(`$logs` 컨테이너, `$metric` 표)에 대한 요청 | 기록 |
| 익명 요청: 성공, 서버 오류, 클라이언트·서버 시간 초과, 304(Not Modified) 로 실패한 GET | 기록 |
| 그 밖의 실패한 익명 요청 | 기록 안 함 |
| SAS 서명이 맞지 않는 등 검증에 실패한 SAS 요청 | 익명으로 보고 기록 안 함 |
| 서비스가 스스로 한 요청(로그 만들기·지우기) | 기록 안 함 |
| `insights-logs-` 컨테이너 안의 활동 | Azure Monitor 가 걸러 냄 |

SAS 검증에 실패한 요청은 호출한 쪽을 믿을 만하게 가려낼 수 없어서 익명 요청으로 다룹니다[5].

## 위치와 버전별 차이

### 두 방식

데이터 평면 기록을 모으는 방식은 두 가지입니다. Microsoft 는 Azure Monitor 의 리소스 로그 방식을 권합니다[5].

| 항목 | 리소스 로그 (Azure Monitor) | 클래식 Storage Analytics 로그 |
|---|---|---|
| 켜는 곳 | 진단 설정 (diagnostic settings) | 서비스 속성(Set Blob Service Properties 등) |
| 기본값 | 꺼짐(진단 설정을 만들어야 모임) | 꺼짐 |
| 범주·종류 | `StorageRead`, `StorageWrite`, `StorageDelete` | 블롭 메타데이터 `LogType` 이 read·write·delete 조합 |
| 형식 | JSON(Storage·Event Hubs), Log Analytics 표 | 세미콜론으로 나눈 텍스트 |
| 저장 위치 | Log Analytics 작업 영역, 다른 Storage 계정, Event Hubs | 같은 계정의 `$logs` 컨테이너 |
| 서비스 | Blob·Files·Queue·Table 각각 | Blob·Queue·Table |
| 반영 지연 | 보통 3~10분 | 최대 1시간 |

2026년 9월 문서 기준입니다[1][2][5][6][9][10]. Log Analytics 표 이름은 서비스마다 `StorageBlobLogs`, `StorageFileLogs`, `StorageQueueLogs`, `StorageTableLogs` 입니다[8]. 클래식 로깅은 Premium 성능의 범용 v2 계정에서는 쓸 수 없고 Premium BlockBlobStorage 계정에서는 쓸 수 있습니다[5].

### 리소스 로그의 위치

진단 설정에서 Storage 계정을 목적지로 고르면 범주 이름을 딴 컨테이너에 한 시간 단위 블롭이 쌓입니다. 블롭 읽기 기록의 경로 모양은 다음과 같습니다[3][9]. 구독 ID·리소스 그룹·계정 이름은 만든 예시입니다.

```text
insights-logs-storageread/resourceId=/subscriptions/1a2b3c4d-0000-4e5f-8a9b-0c1d2e3f4a5b/resourceGroups/rg-example/providers/Microsoft.Storage/storageAccounts/examplestore01/blobServices/default/y=2026/m=03/d=14/h=02/m=00/PT1H.json
```

쓰기·삭제 범주는 `insights-logs-storagewrite`, `insights-logs-storagedelete` 컨테이너에 같은 규칙으로 쌓입니다. 경로 규칙과 "받은 시각" 기준으로 블롭이 나뉘는 점, 진단 설정의 목적지 조건과 Log Analytics 보관 기간은 [리소스 로그와 진단 설정](./resource-logs.md)에 있습니다.

Storage 계정에만 붙는 조건이 둘 있습니다[1]. 감시하는 계정 자신으로는 로그를 보낼 수 없어서 기록은 반드시 다른 계정이나 작업 영역에 있습니다. 진단 설정에서 보관 기간을 정할 수 없어서, Storage 로 보낸 기록은 그 계정의 수명 주기 관리 (lifecycle management) 정책이 지우고, Log Analytics 로 보낸 기록은 작업 영역의 보관 설정을 따릅니다[1].

### 클래식 로그의 위치

클래식 로그는 계정 블롭 네임스페이스의 `$logs` 컨테이너에 블록 블롭으로 쌓입니다[5]. 이 컨테이너는 List Containers 같은 목록 작업에 나오지 않아서 이름을 직접 적어 열어야 합니다[5]. 로깅을 켠 뒤에는 컨테이너를 지울 수 없지만 안의 블롭은 지울 수 있습니다[5].

```text
{service-name}/YYYY/MM/DD/hhmm/{counter}.log
예: blob/2026/03/14/0200/000000.log
```

`hh` 는 24시간제 UTC 시작 시각, `mm` 은 늘 `00`, counter 는 그 시간 안에서 000000 부터 매기는 여섯 자리 번호입니다[5]. 블롭마다 메타데이터 `LogType`(예 `read,write`), `StartTime`·`EndTime`(`YYYY-MM-DDThh:mm:ssZ`, 안에 든 레코드의 가장 이른·늦은 시각), `LogVersion` 이 붙습니다[5]. 로그가 늦게 쓰이는 일이 있어서 블롭 이름보다 메타데이터가 내용을 더 정확히 알려 줍니다[5].

### 설정 확인하기

진단 설정이 언제 생기고 바뀌었는지는 활동 로그의 `diagnosticSettings/write` 작업으로 봅니다[7]. 계정 단위 설정은 `Microsoft.Storage/storageAccounts/providers/Microsoft.Insights/diagnosticSettings/write`, 블롭 서비스 설정은 `Microsoft.Storage/storageAccounts/blobServices/providers/Microsoft.Insights/diagnosticSettings/write` 입니다[7]. 클래식 로그는 `$logs` 의 블롭 목록과 메타데이터로 쌓인 구간을 확인합니다. PowerShell 로는 블롭 이름으로 시간을 고르고 메타데이터로 쓰기 기록이 든 블롭만 추립니다[5].

```powershell
Get-AzStorageBlob -Container '$logs' |
Where-Object { $_.Name -match 'blob/2026/03/14/02' -and $_.ICloudBlob.Metadata.LogType -match 'write' } |
ForEach-Object { "{0} {1} {2} {3}" -f $_.Name, $_.ICloudBlob.Metadata.StartTime, $_.ICloudBlob.Metadata.EndTime, $_.ICloudBlob.Metadata.LogType }
```

## 구조

### 리소스 로그 레코드

Storage·Event Hubs 로 보낸 레코드와 Log Analytics 표는 필드 이름이 다릅니다[2]. 아래는 OAuth 로 인증한 사용자가 블롭 하나를 내려받은 요청을 필드 설명에 맞춰 만든 예시입니다. 실제 파일에서는 레코드 하나가 한 줄입니다.

```json
{
  "time": "2026-03-14T02:17:45.1234567Z",
  "resourceId": "/subscriptions/1a2b3c4d-0000-4e5f-8a9b-0c1d2e3f4a5b/resourceGroups/rg-example/providers/Microsoft.Storage/storageAccounts/examplestore01/blobServices/default",
  "category": "StorageRead",
  "operationName": "GetBlob",
  "operationVersion": "2023-11-03",
  "schemaVersion": "1.0",
  "statusCode": 200,
  "statusText": "Success",
  "durationMs": 41,
  "callerIpAddress": "203.0.113.25:50412",
  "correlationId": "5c6d7e8f-0000-4111-8222-933344445555",
  "location": "koreacentral",
  "protocol": "HTTPS",
  "uri": "https://examplestore01.blob.core.windows.net/reports/q1.xlsx",
  "identity": {
    "type": "OAuth",
    "authorization": [
      { "action": "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/read",
        "result": "Granted", "type": "RBAC",
        "principals": [ { "id": "11112222-aaaa-3333-bbbb-4444cccc5555", "type": "User" } ] }
    ],
    "requester": {
      "appId": "99998888-7777-6666-5555-444433332222",
      "audience": "https://storage.azure.com/",
      "objectId": "11112222-aaaa-3333-bbbb-4444cccc5555",
      "tenantId": "aaaabbbb-1111-cccc-2222-dddd3333eeee",
      "upn": "someone@contoso.com"
    }
  },
  "properties": {
    "accountName": "examplestore01",
    "userAgentHeader": "azsdk-python-storage-blob/12.19.0",
    "serviceType": "blob",
    "operationCount": 0,
    "responseBodySize": 18432,
    "serverLatencyMs": 12,
    "objectKey": "/examplestore01/reports/q1.xlsx"
  }
}
```

조사에 자주 쓰는 필드는 다음과 같습니다[2][4].

| Storage·Event Hubs 필드 | Log Analytics 열 | 뜻 |
|---|---|---|
| `time` | `TimeGenerated` | 스토리지가 요청을 받은 UTC 시각 |
| `category` | `Category` | `StorageRead`·`StorageWrite`·`StorageDelete` |
| `operationName` | `OperationName` | REST 작업 이름(예 `GetBlob`, `PutBlob`) |
| `statusCode`·`statusText` | `StatusCode`·`StatusText` | HTTP 상태와 상태 메시지(예 `Success`, `SASSuccess`). 2017-04-17 이후 버전은 `ClientOtherError` 대신 오류 코드를 적음 |
| `callerIpAddress` | `CallerIpAddress` | 요청한 IP 와 포트 |
| `correlationId` | `CorrelationId` | 요청마다 Storage 가 만드는 GUID, 중복 제거에 씀 |
| `uri` | `Uri` | 요청한 URI |
| `properties.objectKey` | `ObjectKey` | 접근한 객체 경로 |
| `identity.type` | `AuthenticationType` | `OAuth`, `Kerberos`, `SAS Key`, `Account Key`, `Anonymous` |
| `identity.tokenHash` | `AuthenticationHash` | 인증에 쓴 키·토큰의 SHA-256 해시 |
| `identity.authorization` | `AuthorizationDetails` | 권한 이름(`action`), 결과(`Granted`·`Denied`), 역할 할당 ID, RBAC·ABAC 구분 |
| `identity.requester.objectId` | `RequesterObjectId` | OAuth 요청자의 개체 ID(Kerberos 면 그 사용자의 개체 ID) |
| `identity.requester.upn` | `RequesterUpn` | 요청자 UPN |
| `identity.requester.appId` | `RequesterAppId` | OAuth 애플리케이션 ID |
| `identity.delegatedResource` | 실제 데이터로 확인 | 소유자를 대신해 접근한 Azure 리소스(예 가상 머신)의 ID |
| `properties.userAgentHeader` | `UserAgentHeader` | User-Agent 값 |
| `properties.requestBodySize`·`responseBodySize` | `RequestBodySize`·`ResponseBodySize` | 스토리지가 읽은·쓴 본문 바이트. 실패한 요청은 비어 있을 수 있음 |
| `properties.downloadRange` | 실제 데이터로 확인 | 블롭 일부만 받은 경우의 바이트 범위(예 `bytes=0-1023`) |
| `properties.lastModifiedTime` | `LastModifiedTime` | 돌려준 객체의 마지막 수정 시각 |

`identity.tokenHash` 의 모양은 인증 방식마다 다릅니다[2]. 계정 키면 `key1(키의 SHA-256)` 이나 `key2(...)` 처럼 어느 키였는지가 드러나고, SAS 면 `key1(...),SasSignature(SAS 토큰의 SHA-256)` 처럼 서명에 쓴 키와 SAS 서명 해시가 함께 적히며, OAuth 면 토큰의 SHA-256 하나만 적힙니다. 그 밖의 방식에는 이 필드가 없습니다[2]. `StorageBlobLogs` 에는 이 밖에도 `SourceUri`, `DestinationUri`, `CopyDestinationArmId`(복사 대상), `RequestRegion`, `SasExpiryStatus`(SAS 정책 위반), `TlsVersion`, `TrafficClassification` 열이 있습니다[4].

### 클래식 로그 줄

클래식 로그는 한 줄이 레코드 하나이고 필드는 세미콜론으로 나뉩니다[6]. 첫 필드가 로그 형식 버전이고, 1.0 은 필드 30개, 2.0 은 OAuth 정보 필드 8개를 뒤에 붙인 38개입니다[6]. Blob·Queue 는 1.0·2.0 을 모두 쓰고 Table 은 1.0 만 씁니다[6].

```text
1.0 (30칸)
<version-number>;<request-start-time>;<operation-type>;<request-status>;<http-status-code>;<end-to-end-latency-in-ms>;<server-latency-in-ms>;<authentication-type>;<requester-account-name>;<owner-account-name>;<service-type>;<request-url>;<requested-object-key>;<request-id-header>;<operation-count>;<requester-ip-address>;<request-version-header>;<request-header-size>;<request-packet-size>;<response-header-size>;<response-packet-size>;<request-content-length>;<request-md5>;<server-md5>;<etag-identifier>;<last-modified-time>;<conditions-used>;<user-agent-header>;<referrer-header>;<client-request-id>

2.0 에서 뒤에 붙는 8칸
<user-object-id>;<tenant-id>;<application-id>;<audience>;<issuer>;<user-principal-name>;<reserved-field>;<authorization-detail>
```

`authentication-type` 은 `authenticated`, `anonymous`, `sas` 가운데 하나이고, OAuth 토큰으로 인증한 2.0 레코드에는 `bearer` 가 들어갑니다[5][6]. `requester-account-name` 은 인증된 요청이면 계정 이름이 들어가고 익명·SAS 요청이면 비어 있습니다[6]. 따옴표·세미콜론·줄바꿈이 들어갈 수 있는 필드는 HTML 인코딩한 뒤 따옴표로 감싸므로, 요청 URL 의 `&` 는 `&amp;` 로 적힙니다[5][6]. `request-status` 에는 `Success`, `AnonymousSuccess`, `SASSuccess`, `OAuthSuccess` 같은 값이 옵니다[5][6].

블롭 복사 요청 하나는 `CopyBlob`, `CopyBlobSource`, `CopyBlobDestination` 세 줄로 남고, 세 줄의 `request-id-header` 는 같으며 `operation-count` 만 0·1·2 로 올라갑니다[6]. 리소스 로그의 `operationCount` 도 같은 뜻입니다[2]. Storage 리소스 공급자가 부른 요청도 기록되며 요청 URL 에 `sk=system-1` 이 붙어 있어 가려낼 수 있습니다[5].

## 증거로서 의미

**증명하는 것.** 레코드 한 줄은 어느 시각에 어느 IP(포트 포함)에서 어떤 인증 방식으로 어느 객체에 어떤 작업을 요청했고 결과가 무엇이었는지를 보여 줍니다[2][3]. OAuth 요청이면 `RequesterObjectId` 가 요청한 보안 주체를 가장 믿을 만하게 가리키고, 그 값을 Microsoft Entra ID 에서 찾아 이름을 확인합니다[3]. 응답 본문 크기(`ResponseBodySize`)를 더하면 내려간 바이트 양을 셀 수 있고, `downloadRange` 가 있으면 일부만 받은 요청입니다[2][3]. `AuthorizationDetails` 의 `result` 가 `Denied` 인 레코드는 권한이 없어 거부된 시도입니다[2].

**증명하지 못하는 것.** 공유 키 (Shared Key) 와 SAS 로 인증한 요청은 개인 신원을 알려 주지 않습니다[3]. 이때는 `CallerIpAddress` 와 `UserAgentHeader` 로 출처를 좁히고, SAS 는 서명 해시를 배포 기록과 맞춰 봐야 합니다[3]. 실패한 익명 요청과 검증에 실패한 SAS 요청은 기록되지 않으므로 "무단 접근 시도 기록이 없다" 가 "시도가 없었다" 를 뜻하지 않습니다[1][5]. 최선 노력 방식이라 요청 하나하나가 모두 남는다는 보장도 없습니다[1][5]. 진단 설정이나 클래식 로깅을 켜지 않은 기간에는 데이터 평면 기록이 아예 없습니다.

활동 로그의 `listkeys/action`·`listAccountSas/action` 은 "키나 SAS 를 받아 갔다" 는 제어 평면 사실만 보여 줍니다[7]. 받아 간 키로 무엇을 했는지는 데이터 평면 기록에서 같은 키(`key1`·`key2`)의 해시가 찍힌 요청을 찾아야 보입니다[2]. 보고서에는 "이 시각에 이 IP 에서 계정 키로 이 블롭을 내려받는 요청이 성공한 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

리소스 로그의 `time`·`TimeGenerated` 와 클래식 로그의 `request-start-time` 은 모두 스토리지가 요청을 받은 UTC 시각입니다[2][4][6]. 요청을 받은 시각이라 긴 다운로드는 끝난 시각이 더 늦고, 끝까지 걸린 시간은 `durationMs`(요청을 읽고 응답을 보내는 시간까지 포함), 서버 처리 시간은 `serverLatencyMs` 로 봅니다[2].

클래식 로그 파일 이름의 시간은 작업이 끝난 시각을 따릅니다[5]. 한 시간 경계 근처에서 받은 요청은 다음 시간 파일에 들어 있을 수 있으므로 앞뒤 파일을 같이 엽니다. 리소스 로그를 Storage 로 보낸 `PT1H.json` 은 받은 시각 기준으로 나뉘어서 URL 의 시간 밖 레코드가 들어 있을 수 있습니다[9].

기록이 조회 가능해지기까지는 시간이 걸립니다. 리소스 로그는 보통 3~10분, 클래식 로그는 최대 1시간 늦게 나타납니다[5][10]. Log Analytics 에서는 `ingestion_time()` 에서 `TimeGenerated` 를 빼 지연을 잴 수 있습니다[10]. `lastModifiedTime` 은 `Tuesday, 09-Aug-11 21:13:26 GMT` 같은 GMT 문자열이라 ISO 8601 로 바꿔 맞춥니다[2][6]. 여러 로그의 시각을 맞추는 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 있습니다.

## 함정과 한계

- **로그 컨테이너 활동은 보이지 않습니다.** Azure Monitor 는 `insights-logs-` 컨테이너 안의 활동을 걸러 냅니다[1]. 기록을 모아 둔 계정에서 누가 로그 블롭을 읽거나 지웠는지는 이 기록으로 알 수 없어서, 그 계정의 수명 주기 정책 변경과 활동 로그를 따로 봅니다. 기록 보존 방법은 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)에 있습니다.
- **`$logs` 의 내용은 지울 수 있습니다.** 컨테이너는 남아도 안의 블롭은 지울 수 있고, 같은 시간대에 중복 레코드가 생길 수 있습니다[5]. 중복은 `request-id-header` 와 `operation-count` 가 같은지로 가려냅니다.
- **인증 방식 값의 철자가 문서마다 다릅니다.** 필드 설명은 `SAS Key`·`Account Key` 로 적고, 모니터링 문서의 KQL 예는 `AuthenticationType == "SAS"` 로 적었습니다[2][3]. 실제 데이터에서 `summarize count() by AuthenticationType` 로 실제 값을 먼저 봅니다. 같은 문서 본문의 `RequestObjectId` 는 `RequesterObjectId` 열을 가리킵니다[3][4].
- **UPN 이 없을 수 있습니다.** Microsoft Entra 사용자는 UPN 이 보이지만 사용자 할당 관리 ID 나 테넌트 간 인증이면 보이지 않습니다[3].
- **SAS 토큰 원문은 없습니다.** 로그에는 서명의 SHA-256 해시만 있어서, 토큰 자체를 로그에서 되살릴 수 없습니다[3].
- **포털 조회도 기록을 만듭니다.** 조사자가 포털에서 계정을 열면 그 작업이 섞이고, `$logs` 를 읽는 요청도 분석 데이터 요청으로 기록됩니다[1]. 조사자의 IP·시각·계정을 적어 두고 결과에서 뺍니다.
- **도구가 데이터 평면 기록을 대신 모아 주지 않습니다.** Untitled Goose Tool 은 Storage 계정 목록(`azure_storage_accounts.json`)과 파일 공유 목록을 받지만, 블롭 로그를 받는 기능(`auxillary_storage_log_pull`)은 Key Vault·NSG 흐름·Bastion 컨테이너만 받습니다[12]. `insights-logs-storageread` 같은 컨테이너는 따로 내려받습니다.

## 직접 분석해 보기

### 원본 한 줄 읽기

클래식 2.0 로그 한 줄을 명세대로 만든 예시로 나눠 봅니다[6]. 값은 모두 만든 예시입니다.

```text
2.0;2026-03-14T02:18:03.5550123Z;GetBlob;OAuthSuccess;200;41;12;bearer;examplestore01;examplestore01;blob;"https://examplestore01.blob.core.windows.net/reports/q1.xlsx";"/examplestore01/reports/q1.xlsx";0b1c2d3e-0000-4a5b-8c9d-0e1f2a3b4c5d;0;198.51.100.23:50433;2023-11-03;512;0;330;18432;0;;;"0x8DC0000000000AA";Friday, 13-Mar-26 09:12:40 GMT;;"azsdk-python-storage-blob/12.19.0";;"7d8e9f0a-0000-4b1c-9d2e-3f4a5b6c7d8e";11112222-aaaa-3333-bbbb-4444cccc5555;aaaabbbb-1111-cccc-2222-dddd3333eeee;99998888-7777-6666-5555-444433332222;https://storage.azure.com;https://sts.windows.net/aaaabbbb-1111-cccc-2222-dddd3333eeee/;someone@contoso.com;;
```

| 필드 | 값 | 읽는 법 |
|---|---|---|
| 1 | `2.0` | 형식 버전. 뒤에 OAuth 필드 8개가 더 있음 |
| 2 | `2026-03-14T02:18:03.5550123Z` | 요청을 받은 UTC 시각 |
| 3·4·5 | `GetBlob`·`OAuthSuccess`·`200` | 블롭 내려받기, OAuth 인증 성공, HTTP 200 |
| 8 | `bearer` | OAuth 토큰으로 인증 |
| 12·13 | URL·`/examplestore01/reports/q1.xlsx` | 요청한 객체 |
| 14·15 | `0b1c...`·`0` | 요청 ID, 요청 안의 작업 번호 |
| 16 | `198.51.100.23:50433` | 요청한 IP 와 포트 |
| 21 | `18432` | 스토리지가 보낸 응답 바이트 |
| 26 | `Friday, 13-Mar-26 09:12:40 GMT` | 돌려준 블롭의 마지막 수정 시각 |
| 28 | `"azsdk-python-storage-blob/12.19.0"` | User-Agent |
| 31·36 | 개체 ID·`someone@contoso.com` | 요청자 개체 ID 와 UPN |

필드를 셀 때는 따옴표 안의 세미콜론에서 나누지 않고, 줄마다 첫 필드의 버전부터 보고 필드 수를 정합니다[6].

### SAS 서명 해시 맞춰 보기

SAS 로 인증한 요청의 `AuthenticationHash` 에는 서명의 SHA-256 이 들어 있습니다[3]. 조직이 배포한 SAS 가 여럿이면 각 SAS 의 `sig` 값을 URL 디코딩하고 SHA-256 을 구해 로그 값과 맞춥니다[3]. URL 디코딩은 PowerShell 의 `[uri]::UnescapeDataString` 으로 합니다[3].

```powershell
[uri]::UnescapeDataString("<SAS signature here>")
```

SAS 에는 신원 정보가 없어서, 어느 해시를 누구에게 줬는지 적어 둔 대응표가 있어야 사람이나 조직까지 이을 수 있습니다[3].

### 공개 도구와 질의

Log Analytics 로 모았다면 KQL 로 누가·언제·무엇을·어떻게를 뽑습니다[3].

```kusto
StorageBlobLogs
| where TimeGenerated between (datetime(2026-03-14T00:00:00Z) .. datetime(2026-03-15T00:00:00Z))
| project TimeGenerated, AuthenticationType, RequesterObjectId, CallerIpAddress, UserAgentHeader, OperationName, Uri, StatusText, ResponseBodySize
```

컨테이너별로 읽은 횟수와 바이트는 `Uri` 경로의 첫 부분을 잘라 셉니다[3].

```kusto
StorageBlobLogs
| where OperationName == "GetBlob"
| extend ContainerName = split(parse_url(Uri).Path, "/")[1]
| summarize ReadSize = sum(ResponseBodySize), ReadCount = count() by tostring(ContainerName)
```

삭제를 찾을 때는 `OperationName` 이 `DeleteBlob`·`DeleteContainer` 인 레코드를 거르고, 쓰기는 `PutBlob`, `PutBlock`, `PutBlockList`, `AppendBlock`, `SnapshotBlob`, `CopyBlob`, `SetBlobTier` 를 함께 봅니다[3]. Storage 계정으로만 보낸 기록은 Azure Synapse 의 서버리스 SQL 풀로 `PT1H.json` 을 직접 조회할 수 있고, 내려받은 파일은 한 줄씩 JSON 으로 읽으면 됩니다[3]. JSON 로그 다루는 법은 [JSON 로그 읽기](../../01-foundations/logging/json-logs.md)에 있습니다.

```bash
jq -c 'select(.operationName=="GetBlob") | [.time, .callerIpAddress, .identity.type, .identity.requester.objectId, .uri, .properties.responseBodySize]' PT1H.json
```

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [활동 로그](./activity-log.md) | `listkeys/action`·`listAccountSas/action` 시각과 호출자 뒤에 같은 키 해시·SAS 해시가 데이터 평면에 나타나는지, 진단 설정·수명 주기 정책·불변 정책 변경 시각 |
| [리소스 로그와 진단 설정](./resource-logs.md) | 조사 기간에 진단 설정이 있었는지, 기록 계정의 보관 규칙 |
| [Microsoft Entra 로그](../m365/entra-logs/index.md) | `RequesterObjectId`·`RequesterAppId` 의 로그인 기록과 IP |
| [네트워크 흐름 로그](./flow-logs.md) | 가상 머신에서 Storage 끝점으로 나간 흐름과 바이트 |
| [Azure 가상 머신](./azure-vm.md) | `delegatedResource` 가 가리키는 VM 과 그 안의 작업 기록 |
| [Key Vault 기록](./key-vault.md) | 계정 키나 연결 문자열을 비밀로 둔 경우 그 비밀을 읽은 시각 |
| [S3 접근 기록](../aws/s3-access-logs.md) | AWS 쪽 대응 기록. 필드 대응을 비교할 때 |

IP·User-Agent 로 출처를 좁히는 방법은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md), 여러 기록을 시간순으로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 실습

Microsoft 문서 "Storage Analytics log format" 과 "Azure Storage analytics logging" 에 실린 예시 줄로 풀어 봅니다[5][6].

1. 1.0 형식의 익명 `GetBlob` 예시에서 `authentication-type` 과 `requester-account-name` 필드를 찾고, 두 필드가 그렇게 적힌 이유를 설명해 봅니다.
2. `CopyBlob` 예시 세 줄에서 요청 ID 와 `operation-count` 를 비교하고, 원본 블롭과 대상 블롭이 각각 어느 줄에 있는지 적어 봅니다.
3. 2.0 형식의 `ListBlobs`·`PutBlock` 예시에서 OAuth 필드 8개를 나눠 요청자 개체 ID·테넌트 ID·애플리케이션 ID 를 찾고, UPN 필드가 비어 있는지 확인해 봅니다.
4. 블롭 예시 줄의 요청 URL 에 있는 `&amp;` 를 되돌려 읽고, 그 요청이 SAS 로 인증된 요청인지 URL 의 매개변수로 판단해 봅니다.
5. 실제 사건에서는 조사 기간을 시간 단위로 나눠 `insights-logs-storageread` 의 `PT1H.json` 이나 `$logs` 블롭이 빠진 시간이 있는지 표로 만들고, 같은 시간대의 활동 로그에서 진단 설정 변경이 있었는지 확인해 봅니다.

## 참고 문헌

1. Microsoft, "Monitor Azure Blob Storage", azure-docs. https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/storage/blobs/monitor-blob-storage.md
2. Microsoft, "Azure Blob Storage monitoring data reference", Microsoft Learn. https://learn.microsoft.com/en-us/azure/storage/blobs/monitor-blob-storage-reference
3. Microsoft, "Best practices for monitoring Azure Blob Storage", azure-docs. https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/storage/blobs/blob-storage-monitoring-scenarios.md
4. Microsoft, "StorageBlobLogs", Azure Monitor Logs table reference. https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/storagebloblogs
5. Microsoft, "Azure Storage analytics logging", Microsoft Learn. https://learn.microsoft.com/en-us/azure/storage/common/storage-analytics-logging
6. Microsoft, "Storage Analytics log format", Azure Storage REST API. https://learn.microsoft.com/en-us/rest/api/storageservices/storage-analytics-log-format
7. Microsoft, "Azure permissions for Storage", Azure RBAC. https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/storage
8. Microsoft, "Azure permissions for Monitor", Azure RBAC. https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/monitor
9. Microsoft, "Azure resource logs", azure-monitor-docs. https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs.md
10. Microsoft, "Log data ingestion time in Azure Monitor", Microsoft Learn. https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-ingestion-time
11. SigmaHQ, azure_rare_operations.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_rare_operations.yml
12. CISA, Untitled Goose Tool, goosey/azure_dumper.py. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/azure_dumper.py
