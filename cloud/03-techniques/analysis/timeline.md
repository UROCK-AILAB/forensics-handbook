---
title: "클라우드 타임라인"
parent: "기법 · 분석"
nav_order: 680
---

# 클라우드 타임라인 (Timeline)

여러 클라우드 서비스의 로그를 사건 시각 하나로 맞춰 시간순으로 합치고, 세션 ID·토큰 ID 같은 열쇠로 같은 행위의 기록끼리 묶어 읽는 방법입니다.

## 언제 쓰나

클라우드 사고는 로그 하나로 끝나는 일이 드뭅니다. 계정 탈취를 예로 들면 로그인은 Entra ID 로그에, 받은편지함 규칙 생성은 통합 감사 로그에, 가상 머신 조작은 Azure 활동 로그나 CloudTrail 에 남습니다. 이렇게 흩어진 기록을 한 표에 모아야 "로그인 → 권한 변경 → 데이터 접근" 순서가 보이고, 어느 단계부터 기록이 비는지도 드러납니다.

로그마다 사건 시각을 담는 필드 이름과 형식이 다르고, 수집 도구가 돌려주는 순서가 사건 순서와 다르고, 관리 화면이 시각을 현지 시간대로 바꿔 보여 주는 경우가 있습니다. 그래서 파일을 이어 붙이기만 해서는 타임라인이 되지 않고, 아래 절차처럼 열을 고르고 형식을 맞추고 다시 정렬하는 과정을 거쳐야 합니다. 시각 필드의 일반 원리는 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에서 다루고, 이 페이지는 여러 로그를 엮는 방법만 다룹니다. 디스크·메모리 아티팩트로 타임라인을 만드는 공통 원리는 [Windows 판 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html)과 [Linux 판 타임라인 만들기](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/timeline.html)를 보면 됩니다.

## 절차

### 1. 조사 범위와 수집 끝 시점을 정한다

먼저 어떤 서비스의 어떤 로그를 넣을지와 시간 범위를 정합니다. 서비스와 라이선스에 따라 남아 있는 기간이 다르므로 범위의 앞쪽 끝은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에서 확인합니다.

범위의 뒤쪽 끝은 로그가 늦게 들어오는 시간을 생각해서 정합니다. 사건 직후에 수집하면 아직 들어오지 않은 기록이 빠지고, 그 빈자리를 "그 뒤로 아무 일도 없었다" 로 읽게 됩니다. 아래 값은 표에 적은 문서 날짜 기준입니다.

| 로그 | 기록이 조회되기까지 걸리는 시간 | 근거 |
|---|---|---|
| Microsoft 365 감사 로그 검색 | Exchange·SharePoint·OneDrive·Teams 는 보통 사건 후 60~90분이고, 다른 서비스는 더 걸릴 수 있습니다. Microsoft 는 특정 시간을 약속하지 않습니다(2026-06-19 문서). | [10] |
| Office 365 Management Activity API | 구독을 만든 뒤 첫 콘텐츠 블롭이 나오기까지 최대 12시간 걸립니다(2024-12-03 문서). | [9] |
| Azure 활동 로그 → Azure Monitor | 3~20분입니다(2026-07-31 문서). | [14] |
| Azure 리소스 로그 → Azure Monitor | 보통 3~10분입니다. | [14] |
| Entra 로그인 → Log Analytics | `TimeGenerated` 와 `CreatedDateTime` 의 차이가 처리·전송에 걸린 시간입니다. | [1] |
| AWS CloudTrail | 로그 파일을 약 5분마다 게시하고, API 호출 뒤 평균 약 5분 안에 전달합니다. 보장하는 값은 아닙니다. | [17] |
| Google Workspace | 관리(Admin)·Drive·Gmail·SAML·로그인 이벤트는 몇 분, 사용자 계정 이벤트는 수십 분, Calendar·Groups 는 수십 분에서 두어 시간, OAuth 는 최대 몇 시간, Token 은 두어 시간, Takeout 종료 이벤트는 데이터 크기에 따라 며칠까지 걸립니다. 드물게 이보다 늦거나 아예 보고되지 않을 수 있습니다(2026-09-25 문서). | [24] |
| Okta System Log | since·until 을 모두 준 요청이라도 그 기간의 이벤트가 모두 들어 있지 않을 수 있습니다. 드물지만 늦게 들어오는 이벤트가 있습니다. | [30] |

### 2. 원본 레코드를 그대로 받는다

타임라인은 수집한 원본 JSON 을 그대로 두고 그 사본으로 만듭니다. 수집 도구가 레코드를 요약하거나 열을 줄이면 나중에 열쇠 필드(세션 ID·토큰 ID)를 되살릴 수 없습니다. 수집 방법은 [Microsoft 365 수집 도구](../acquisition/m365-collection.md)와 [AWS·Azure·GCP 수집](../acquisition/iaas-collection.md)에서 다루고, 타임라인과 관련해서 챙길 점만 적으면 다음과 같습니다.

Entra 로그인은 종류별로 따로 받아야 합니다. Microsoft Graph beta `/auditLogs/signIns` 는 필터를 주지 않으면 대화형 로그인만 돌려주고, 사용자 로그인과 서비스 주체 로그인을 한 필터로 함께 받는 방법은 지원하지 않습니다[3]. 비대화형 로그인을 빼면 토큰을 재사용한 기록이 통째로 빠집니다.

`Search-UnifiedAuditLog` 는 기본으로 100건만 돌려줍니다. `-SessionCommand ReturnLargeSet` 은 최대 5만 건을 **정렬하지 않고** 돌려주고, `ReturnNextPreviewPage` 는 날짜순으로 정렬하지만 최대 5,000건입니다. 한 SessionId 에서 두 값을 섞으면 결과가 1만 건으로 제한됩니다[11]. 미리 보기 기능인 `-HighCompleteness` 스위치를 주지 않으면 빨리 끝나는 대신 결과가 빠질 수 있습니다[11].

Office 365 Management Activity API 는 한 번에 24시간 이내 구간만 조회할 수 있고, 시작 시각은 7일 전보다 앞설 수 없습니다[9].

### 3. 로그마다 사건 시각 열을 고른다

한 레코드에 시각이 두 개 이상 있는 로그가 많습니다. 하나는 사건이 일어난 시각이고, 다른 하나는 로그 시스템이 받거나 적재한 시각입니다. 타임라인의 정렬 열은 사건 시각이고, 적재 시각은 지연을 재는 데만 씁니다.

| 서비스·로그 | 사건 시각 필드 | 형식 | 받은·적재 시각 필드 (정렬에 쓰지 않음) | 근거 |
|---|---|---|---|---|
| Entra 로그인 (Graph) | `createdDateTime` | UTC, 예 `2014-01-01T00:00:00Z` | — | [3] |
| Entra 로그인 (Log Analytics `SigninLogs`) | `CreatedDateTime` | UTC | `TimeGenerated` (Log Analytics 에 적재·저장된 시각) | [1][4] |
| Entra 감사 로그 (Graph `directoryAudit`) | `activityDateTime` | UTC | — | [6] |
| Entra ID Protection 위험 탐지 (`riskDetection`) | `activityDateTime` (위험한 활동이 일어난 시각) | UTC ISO 8601 | `detectedDateTime` (위험을 탐지한 시각) | [7] |
| Microsoft 365 통합 감사 로그 | `CreationTime` (감사 레코드를 만든 시각) | UTC | — | [8] |
| Azure 활동 로그 (원본 JSON) | `eventTimestamp` (요청을 처리한 Azure 서비스가 이벤트를 만든 시각) | 예 `2018-01-29T20:42:31.3810679Z` | `submissionTimestamp` (조회할 수 있게 된 시각) | [12] |
| Azure 활동 로그 (Log Analytics `AzureActivity`) | `TimeGenerated` | — | `EventSubmissionTimestamp` | [13] |
| AWS CloudTrail | `eventTime` (요청이 끝난 시각) | UTC | — | [16] |
| Google Cloud (LogEntry) | `timestamp` (사건이 일어난 시각) | RFC 3339, 출력은 항상 Z 로 맞추고 소수 0·3·6·9자리 | `receiveTimestamp` (Logging 이 받은 시각) | [22] |
| Google Workspace Reports API | `id.time` | 출처 차이 있음(아래 4단계) | — | [25][26] |
| Okta System Log | `published` | 예 `2024-08-13T15:58:20.353Z` | 내부 persistence time (로그에 커밋된 시각, 레코드에는 없음) | [30][44] |
| Slack Audit Logs API | `date_create` | Unix 초 | — | [32] |
| Slack Access Logs | `date_first`, `date_last` | Unix 초 | — | [33] |
| GitHub 감사 로그 | `created_at` | Unix 밀리초, UTC | — | [34][35] |

Slack Access Logs 는 한 줄이 사건 하나가 아니라 사용자·IP 주소·사용자 에이전트 조합 하나이고, `date_first` 와 `date_last` 는 그 조합이 처음과 마지막으로 보인 시각입니다[33]. 타임라인에는 두 시각을 따로 두 줄로 넣고, 그 사이의 접근은 `count` 만큼 있었다고만 적습니다.

같은 `TimeGenerated` 라는 이름이 표마다 뜻이 다릅니다. `SigninLogs` 의 `TimeGenerated` 는 적재 시각이고[1], `AzureActivity` 의 `TimeGenerated` 는 Azure 서비스가 이벤트를 만든 시각입니다[13]. 열 이름만 보고 고르지 말고 표마다 설명을 확인합니다. 비대화형 로그인 표 `AADNonInteractiveUserSignInLogs` 의 참조 문서는 `TimeGenerated` 를 "The date and time of the event in UTC" 라고 설명해서, 적재 시각이라는 Entra 문서의 설명과 다릅니다[1][5]. 이 표도 사건 시각은 `CreatedDateTime` 으로 잡습니다.

### 4. 시각 형식을 UTC ISO 8601 하나로 맞춘다

로그마다 시각 형식이 ISO 8601 확장형, ISO 8601 기본형, Unix 초, Unix 밀리초, 마이크로초 정수로 섞여 있습니다. 한 열로 합치기 전에 모두 `YYYY-MM-DDThh:mm:ss.sssZ` 형식의 UTC 로 바꿉니다. 아래는 같은 순간을 서로 다른 형식으로 적은 만든 예시입니다.

| 원래 값 (만든 예시) | 어느 필드의 형식인가 | 맞춘 값 |
|---|---|---|
| `2026-09-01T02:10:33Z` | CloudTrail `eventTime` | 2026-09-01T02:10:33.000Z |
| `20260901T021033Z` | CloudTrail `sessionContext.attributes.creationDate` (기본형) | 2026-09-01T02:10:33.000Z |
| `1788228633` | Slack `date_create` (Unix 초) | 2026-09-01T02:10:33.000Z |
| `1788228633000` | GitHub `created_at` (Unix 밀리초) | 2026-09-01T02:10:33.000Z |
| `1788228633000000` | Google Workspace `login_timestamp` (마이크로초) | 2026-09-01T02:10:33.000Z |

자릿수로 단위를 가려낼 수 있습니다. 2026년 무렵의 Unix 시각은 초 단위면 10자리, 밀리초면 13자리, 마이크로초면 16자리입니다.

형식이 문서끼리 다르게 적힌 필드가 둘 있습니다. CloudTrail 의 `creationDate` 는 userIdentity 문서가 "ISO 8601 basic notation" 이라고 설명하고 `20131102T010628Z` 를 예로 들지만, 같은 문서의 다른 예시와 콘솔 로그인 이벤트 문서의 예시는 `2023-07-15T03:51:12Z` 같은 확장형입니다[20][21]. Google Workspace 의 `id.time` 은 Reports API 참조 문서(activities.list)가 "UNIX epoch time in seconds" 라고 적고, 같은 API 의 관리 활동 안내서 예시 응답은 `"2011-06-17T15:39:18.460Z"` 문자열입니다[25][26]. 두 필드 모두 변환기가 두 형식을 다 읽도록 만들고, 실제 형식은 실제 로그로 확인합니다.

한 레코드에 같은 순간이 두 형식으로 들어 있는 SaaS 로그도 있습니다. `EVENT_TYPE`·`TIMESTAMP`·`REQUEST_ID` 열로 시작하는 SaaS 이벤트 로그 파일 한 줄에는 구분자 없는 숫자형 `TIMESTAMP`(`YYYYMMDDhhmmss.sss` 형식)와 Z 로 끝나는 ISO 8601 `TIMESTAMP_DERIVED` 가 함께 있습니다[43]. 이런 경우에는 시간대가 명시된 쪽을 씁니다.

변환하면서 원래 값은 지우지 않고 옆 열에 남깁니다. 보고서에서 "원본 레코드의 이 값" 을 가리킬 수 있어야 하기 때문입니다.

### 5. 사건 시각으로 다시 정렬한다

수집 결과 파일의 순서는 사건 순서가 아닙니다. 모든 레코드를 한 표에 넣은 뒤 4단계에서 맞춘 시각으로 다시 정렬합니다.

| 로그 | 받은 순서와 사건 순서가 어긋나는 이유 | 근거 |
|---|---|---|
| CloudTrail 로그 파일 | 공개 API 호출을 순서대로 쌓은 기록이 아니라서 이벤트가 특정 순서로 나오지 않습니다. | [18] |
| Management Activity API | 여러 서버와 데이터센터에서 모아 블롭을 만들기 때문에 블롭 안 이벤트는 일어난 순서가 아니고, 뒤 블롭에 더 이른 사건이 들어 있을 수 있습니다. | [9] |
| `Search-UnifiedAuditLog -SessionCommand ReturnLargeSet` | 정렬하지 않은 결과를 돌려줍니다. | [11] |
| Okta 폴링 요청 (until 없음, sortOrder ASCENDING) | 내부 persistence time 순서라서 `published` 기준으로 보면 순서가 뒤섞일 수 있습니다. since·until 을 모두 준 한정 요청(bounded request)은 `published` 순서를 보장합니다. | [30] |

시각이 같은 레코드가 여럿이면 두 번째 정렬 열을 정합니다. Google Cloud 는 쿼리에서 `logName`·`timestamp` 가 같은 항목의 순서를 `insertId` 로 정합니다[22]. Google Workspace 는 시각이 같은 이벤트를 `id.uniqueQualifier` 로 구분합니다[25]. 다른 로그는 시각이 같으면 원래 파일 순서를 유지하는 안정 정렬(stable sort)을 쓰고, 순서를 단정하지 않습니다.

중복도 이 단계에서 걸러 냅니다. Google Cloud 의 `insertId` 중복 제거는 한 쿼리 결과 안에서만 되고 내보내기(export)에서는 보장하지 않으므로[22], 내보낸 파일을 합칠 때는 `insertId` 가 같은 줄을 직접 확인합니다.

### 6. 열쇠 필드로 같은 행위의 기록을 묶는다

시각만으로 정렬하면 서로 다른 사용자의 기록이 뒤섞입니다. 아래 필드가 같은 줄은 같은 세션·토큰·상위 작업에 속한 기록이므로, 타임라인에 열을 따로 두고 묶어 읽습니다.

| 잇는 것 | 이쪽 필드 | 저쪽 필드 | 근거 |
|---|---|---|---|
| Entra 로그인 ↔ Microsoft 365 활동 (세션) | 로그인 `sessionId` (Graph beta) / `SessionId` (`SigninLogs`) | 통합 감사 로그 `AppAccessContext.AADSessionId` | [3][4][8] |
| Entra 로그인 ↔ Microsoft 365 활동 (토큰) | 로그인 `uniqueTokenIdentifier` / `UniqueTokenIdentifier` | 통합 감사 로그 `AppAccessContext.UniqueTokenId` (대소문자 구분) | [3][4][8] |
| Entra 로그인 여러 줄 | `correlationId` — 같은 로그인 세션의 로그인을 묶습니다. 클라이언트가 보낸 값이라 Entra ID 가 정확성을 보장하지 않습니다. | — | [1] |
| Entra 로그인 인증 과정 | `originalRequestId` — 인증 과정 첫 요청의 ID 입니다. | — | [3] |
| Microsoft 365 서비스 사이 | `AppAccessContext.CorrelationId` — 한 사용자의 행위를 여러 Microsoft 365 서비스에 걸쳐 잇습니다. | — | [8] |
| Entra 감사 로그 서비스 사이 | `correlationId` | — | [6] |
| Azure 활동 로그 | `correlationId` 가 같으면 같은 상위 작업(uber action)입니다. | — | [12][13] |
| CloudTrail 계정 사이 | `sharedEventID` — 한 AWS 동작이 여러 계정에 따로 기록될 때 같은 값이고, 레코드마다 `eventID`·`recipientAccountId` 는 다릅니다. 호출한 계정과 자원 소유 계정이 같으면 이 필드가 없습니다. | — | [16] |
| Okta 세션 | `authenticationContext.externalSessionId` 는 같은 사용자 세션의 이벤트를 묶고, `authenticationContext.rootSessionId` 는 같은 루트 세션에서 나온 여러 세션을 묶습니다. | — | [30] |

통합 감사 로그 레코드의 `AppAccessContext.IssuedAtTime` 은 그 요청에 쓴 Entra 토큰의 인증이 일어난 시각입니다[8]. 이 값을 Entra 로그인 기록의 시각과 나란히 놓으면 활동에 쓴 토큰이 어느 로그인에서 나왔는지 좁힐 수 있습니다. 세션과 토큰의 관계는 [토큰과 세션](../../01-foundations/identity/tokens-sessions.md), IP 주소로 묶는 방법은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md)를 봅니다.

> 그림 자리: Entra 로그인 한 줄(`SessionId`, `UniqueTokenIdentifier`)에서 통합 감사 로그 두 줄(`AADSessionId`, `UniqueTokenId`)로 화살표가 이어지는 그림

### 7. 화면에서 옮긴 시각은 표시 시간대를 확인한다

원본 JSON 이 아니라 관리 화면에서 본 시각을 타임라인에 넣을 때는 그 화면이 어느 시간대로 보여 주는지 먼저 확인합니다.

| 화면 | 표시 시간대 | 근거 |
|---|---|---|
| Entra 관리 센터 로그인 로그 | 로그인한 사용자가 아니라 **관리 센터를 보고 있는 사람**의 시간대 | [1] |
| Purview 감사 검색 | 날짜·시간 범위와 결과의 Date 열 모두 UTC | [10] |
| `Search-UnifiedAuditLog` | 저장은 UTC 이고, 시간대 없이 준 StartDate·EndDate 는 UTC 로 해석합니다. 현지 시각은 `(Get-Date "5/6/2018 9:30 AM").ToUniversalTime()` 처럼 바꿔 넣습니다. | [11] |
| Defender XDR 고급 헌팅 | 데이터와 쿼리는 UTC 이고, 결과는 사용자가 설정한 시간대로 바꿔 보여 줍니다. | [36] |
| Google Workspace 관리 콘솔 조사 화면(관리 로그 이벤트 등) | 브라우저 기본 시간대로 표시하고, 조사 화면에서 시간대를 바꾸면 검색 조건과 결과 모두에 적용됩니다. | [28] |
| Google Workspace 이메일 로그 검색 결과 | 검색한 관리 콘솔 기기의 시간대 | [29] |
| Google Cloud Logs Explorer | 표시 형식 설정에서 "Date, time, and timezone", "Date and time (default)", "Time only" 가운데 고릅니다. | [23] |
| Okta 관리 콘솔 System Log | 드롭다운에서 고른 시간대 | [31] |
| Azure `Get-AzLog` 출력 | `EventTimestamp : 3/1/2021 10:07:42 PM` 처럼 PowerShell 의 날짜 형식으로 찍힙니다. | [15] |

## 도구

| 도구 | 타임라인과 관련된 동작 | 근거 |
|---|---|---|
| Microsoft-Extractor-Suite `Get-GraphEntraSignInLogs` | Graph beta `/auditLogs/signIns` 를 `createdDateTime` 범위로 부르고, `-EventTypes` 로 interactiveUser·nonInteractiveUser·servicePrincipal·managedIdentity 를 나눠 받습니다(기본 All). 출력은 JSON 이나 SOF-ELK 형식이고 기본 경로는 `Output\EntraID\{date_SignInLogs}\{timestamp}-{eventType}-SignInLogs.json` 입니다. | [37] |
| Microsoft-Extractor-Suite `Get-GraphEntraAuditLogs` | Graph v1.0 `/auditLogs/directoryAudits` 를 `activityDateTime` 범위로 부릅니다. | [37] |
| Untitled Goose Tool | Entra 로그인·감사 로그를 하루 단위로 나눠 받고 `createdDateTime`·`activityDateTime` 으로 정렬해 달라고 요청합니다. 날짜를 주지 않으면 29일 전부터 받습니다. | [38] |
| DFIR-O365RC | 결과를 JSON 으로 남깁니다. 수단별 조회 기간을 통합 감사 로그 Exchange Online PowerShell 90일, Purview 180일, Management API 7일, Entra 로그 Graph 30일로 정리해 둡니다. | [39] |
| Hawk `Get-HawkUserUALSignInLog` | 통합 감사 로그에서 RecordType `AzureActiveDirectoryAccountLogon`, `AzureActiveDirectory`, `AzureActiveDirectoryStsLogon` 를 모아 `Converted_Authentication_Logs.csv` 로 만듭니다. Entra 로그인 로그를 따로 받기 어려울 때 로그인 줄을 채우는 데 씁니다. | [42] |
| ALFA (Google Workspace) | `alfa acquire` 의 `--start-time`·`--end-time` 은 RFC 3339 이고, 시간대 없는 값은 UTC 로 보고 정규화합니다. `alfa analyze` 는 이벤트를 MITRE ATT&CK 클라우드 기법에 대응시킨 뒤 시간순으로 살펴 공격 흐름의 부분열(subchain)을 점수로 매기고, `id.uniqueQualifier` 를 레코드 색인으로 씁니다. | [40][41] |

도구가 만든 CSV 는 열을 줄이거나 시각을 현지 형식으로 바꿔 쓸 수 있으므로, 도구 출력만으로 타임라인을 만들지 말고 원본 JSON 과 열 하나씩 대조합니다. 레코드 겉모양과 JSON 을 펼치는 방법은 [JSON 로그 읽기](../../01-foundations/logging/json-logs.md)를 봅니다.

## 함정과 한계

아래 항목은 서로 독립된 함정입니다.

- **적재 시각 덮어쓰기**: Azure Monitor Logs 는 `TimeGenerated` 가 받은 시각보다 이틀 넘게 이르거나 하루 넘게 늦으면 받은 시각으로 바꾸고, 데이터 원천이 값을 주지 않으면 `_TimeReceived` 와 같게 채웁니다[14]. 오래된 로그를 나중에 다시 적재하면 사건 시각이 바뀐 것처럼 보일 수 있습니다.
- **묶인 비대화형 로그인**: Entra 비대화형 로그인은 시각만 빼고 내용이 같은 로그인을 한 줄로 묶고(`# sign-ins` 열이 1보다 큼), 묶인 로그인이 같은 시각처럼 보일 수 있습니다. 줄을 펼치면 각 시각이 나옵니다. 포털의 Time aggregate 필터는 1시간·6시간·24시간입니다[2].
- **비대화형 로그인의 IP**: 기밀 클라이언트(confidential client)의 비대화형 로그인 IP 는 리프레시 토큰 요청이 실제로 나온 곳이 아니라 처음 토큰을 발급받을 때의 IP 입니다[2].
- **2025년 4월 11일 앞뒤**: 이날부터 FIDO2 키로 리프레시 토큰을 받는 새 로그인은 비대화형 로그인 로그에 기록됩니다[2]. 이 날짜를 걸친 조사에서는 같은 종류의 로그인이 서로 다른 표에 있을 수 있습니다.
- **처음에 덜 채워진 인증 세부 정보**: Entra 로그인 로그의 Authentication Details 탭은 집계가 끝나기 전에 불완전하거나 틀린 값을 보일 수 있습니다[1]. 사건 직후 받은 값은 나중에 다시 받아 대조합니다.
- **활동 시각과 탐지 시각**: Entra ID Protection 위험 탐지의 `activityDateTime` 과 `detectedDateTime` 은 다릅니다[7]. 타임라인에는 활동 시각을 넣고, 탐지 시각은 "이때 탐지됨" 으로 따로 적습니다.
- **CloudTrail 이벤트 기록의 범위**: 이벤트 기록(event history)은 최근 90일의 관리 이벤트만 담고 데이터 이벤트·Insights·네트워크 활동 이벤트는 없습니다. AWS 가 새로 추가한 이벤트는 추가하고 90일이 지나야 온전한 90일 기록이 됩니다[19].
- **CloudTrail 리전**: 2021년 11월 22일부터 IAM·STS·CloudFront 이벤트는 트레일에서 us-east-1 에 기록되므로, 다른 리전의 단일 리전 트레일만 보면 빠집니다. 콘솔 이벤트 기록과 `lookup-events` 는 이 이벤트를 발생한 리전으로 보여 줍니다[18]. `ConsoleLogin` 이벤트의 리전도 사용자 유형과 로그인 엔드포인트에 따라 us-east-1·us-east-2·us-west-2·eu-north-1·ap-southeast-2 등으로 갈립니다[20].
- **잘린 요청 내용**: CloudTrail `requestParameters` 는 100KB 를 넘으면 내용이 빠집니다[16]. 레코드는 있어도 무엇을 요청했는지는 비어 있을 수 있습니다.
- **단위가 다른 두 시각**: Google Workspace 로그인 경고 이벤트의 `login_timestamp` 는 로그인 시각을 마이크로초 정수로 담고[27], 이벤트의 `id.time` 은 경고 이벤트 자체의 시각입니다. 두 값을 한 열에 넣으면 단위와 뜻이 모두 어긋납니다.
- **서비스 시계**: CloudTrail `eventTime` 은 API 엔드포인트를 제공한 AWS 호스트의 시계에서 오고, AWS 서비스는 대체로 NTP 로 시계를 맞춥니다[16]. 서로 다른 회사의 서비스 사이에서 몇 초 안쪽 차이로 선후를 가르는 것은 근거가 약합니다.

## 결과를 어떻게 해석하나

**증명하는 것**: 타임라인의 각 줄은 그 서비스가 자기 시계로 그 시각(UTC)에 그 작업을 기록했다는 사실입니다. 6단계의 열쇠 필드가 같은 줄끼리는 같은 세션·같은 토큰·같은 상위 작업에 속한 기록입니다[1][8][16].

**증명하지 못하는 것**: 서로 다른 서비스의 기록 사이에서 몇 초 안쪽의 정확한 선후는 가를 수 없습니다. 수집 도구가 돌려준 순서가 사건 순서라는 것도 아닙니다. 1단계 표의 지연 시간 안쪽 구간에서 기록이 없다는 것은 사건이 없었다는 뜻이 아닙니다. 비대화형 로그인의 IP 가 실제 요청의 출발지라는 것도 증명하지 못합니다[2].

보고서에는 기록으로 확인되는 만큼만 씁니다. 예를 들면 "2026-09-01 02:10:33 (UTC) 에 user@contoso.com 계정으로 203.0.113.10 에서 로그인한 기록이 있고, 같은 세션 ID 로 02:14:05 (UTC) 에 받은편지함 규칙을 만든 기록이 있다" 처럼 씁니다(계정·IP·시각은 만든 예시). "공격자가 규칙을 만들었다" 는 사람을 특정하는 문장이라 이 기록만으로는 쓸 수 없습니다.

보고서에는 어느 열을 사건 시각으로 썼는지, 적재 시각은 어떻게 다뤘는지, 모든 시각을 UTC 로 맞췄는지, 화면에서 옮긴 값은 어느 시간대였는지를 함께 적습니다. 보고서 틀은 [클라우드 포렌식 보고서](../reporting/forensic-report.md)를 봅니다.

## 함께 볼 페이지

- [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md), [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md), [Azure 활동 로그](../../02-artifacts/azure/activity-log.md), [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md), [Google Workspace 로그인 기록](../../02-artifacts/google-workspace/login-audit.md), [Okta 시스템 로그](../../02-artifacts/saas/okta.md), [Slack 감사 로그](../../02-artifacts/saas/slack.md), [GitHub 감사 로그](../../02-artifacts/saas/github.md)
- [이상한 로그인 가려내기](suspicious-sign-ins.md), [권한 변화 따라가기](permission-changes.md)
- 다른 판: [macOS 판 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/analysis/timeline/index.html), [AI 판 AI 사용 타임라인](https://urock-ailab.github.io/forensics-handbook/ai/03-techniques/analysis/timeline.html)

## 참고 문헌

1. Microsoft, "Sign-in log activity details" (ms.date 2026-03-04). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
2. Microsoft, "Non-interactive sign-ins" (ms.date 2026-02-09). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-noninteractive-sign-ins.md
3. Microsoft Graph, "signIn resource type (beta)" (2025-11-28). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
4. Azure Monitor, "SigninLogs table reference" (2026-08-27). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
5. Azure Monitor, "AADNonInteractiveUserSignInLogs table reference" (2026-08-27). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadnoninteractiveusersigninlogs
6. Microsoft Graph, "directoryAudit resource type" (2024-05-24). https://learn.microsoft.com/en-us/graph/api/resources/directoryaudit
7. Microsoft Graph, "riskDetection resource type" (2025-11-28). https://learn.microsoft.com/en-us/graph/api/resources/riskdetection
8. Microsoft, "Office 365 Management Activity API schema" (2026-08-26). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
9. Microsoft, "Office 365 Management Activity API reference" (2024-12-03). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference
10. Microsoft Purview, "Search the audit log" (2026-06-19). https://learn.microsoft.com/en-us/purview/audit-search
11. Microsoft, "Search-UnifiedAuditLog". https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Search-UnifiedAuditLog.md
12. Microsoft, "Azure Monitor activity log schema" (ms.date 2026-03-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
13. Azure Monitor, "AzureActivity table reference" (2026-07-27). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/azureactivity
14. Azure Monitor, "Log data ingestion time in Azure Monitor" (2026-07-31). https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-ingestion-time
15. Microsoft, "View activity logs for Azure RBAC changes" (2022-08-21). https://learn.microsoft.com/en-us/azure/role-based-access-control/change-history-report
16. AWS, "CloudTrail record contents". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
17. AWS, "How CloudTrail works". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/how-cloudtrail-works.html
18. AWS, "CloudTrail concepts". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html
19. AWS, "Working with CloudTrail event history". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
20. AWS, "AWS Management Console sign-in events". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-aws-console-sign-in-events.html
21. AWS, "CloudTrail userIdentity element". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
22. Google Cloud, "LogEntry" (2026-09-04). https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry
23. Google Cloud, "Logs Explorer interface" (2026-09-25). https://cloud.google.com/logging/docs/view/logs-explorer-interface
24. Google Workspace 관리자 도움말, "Data retention and lag times" (2026-09-25). https://support.google.com/a/answer/7061566?hl=en
25. Google Workspace Admin SDK, "Method: activities.list" (2026-09-09). https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
26. Google Workspace Admin SDK, "Admin Console Audit Activity Reports" (2026-09-03). https://developers.google.com/workspace/admin/reports/v1/guides/manage-audit-admin
27. Google Workspace Admin SDK, "Login Audit Activity Events" (2026-09-03). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/login
28. Google Workspace 관리자 도움말, "Admin log events" (2026-09-18). https://support.google.com/a/answer/4579579?hl=en
29. Google Workspace, "Understand email log search results" (2026-09-18). https://knowledge.workspace.google.com/admin/gmail/advanced/understand-email-log-search-results
30. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
31. Okta, "System Log filters and search". https://help.okta.com/en-us/content/topics/reports/syslog-filters.htm
32. Slack, "Audit Logs API". https://api.slack.com/admins/audit-logs , https://api.slack.com/admins/audit-logs-call
33. Slack, "team.accessLogs". https://api.slack.com/methods/team.accessLogs
34. GitHub Docs, "Reviewing the audit log for your organization". https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization
35. GitHub Docs, "Using the audit log API for your enterprise". https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/using-the-audit-log-api-for-your-enterprise
36. Microsoft Defender XDR, "Overview - Advanced hunting" (2026-08-07). https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-overview
37. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-AzureEntraGraphLogs.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureEntraGraphLogs.ps1
38. CISA, Untitled Goose Tool, `goosey/entra_id_datadumper.py`. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/entra_id_datadumper.py
39. ANSSI, DFIR-O365RC, `README.md`. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/README.md
40. Invictus IR, ALFA, `README.md`. https://github.com/invictus-ir/ALFA/blob/main/README.md
41. Invictus IR, ALFA, `alfa/utils/dates.py`, `alfa/config/config.yml`, `alfa/main/activity.py`. https://github.com/invictus-ir/ALFA/blob/main/alfa/utils/dates.py
42. T0pCyber, Hawk, `Hawk/functions/User/Get-HawkUserUALSignInLog.ps1`. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/User/Get-HawkUserUALSignInLog.ps1
43. Eoghan Casey, "SaaS Forensics & Response — Forensic Preservation, Recovery, and Analysis of SaaS Data", DFRWS USA 2023 발표(Baltimore, 2023-07-11). https://dfrws.org/presentation/saas-forensics-and-response/
44. Okta, Management API OpenAPI 명세 2025.08.0 (`ListLogs` 응답 예시). https://github.com/okta/okta-management-openapi-spec/blob/master/dist/2025.08.0/management-minimal.yaml
