---
title: "클라우드 로그의 시각"
parent: "기반 · 로그 체계"
nav_order: 110
---

# 클라우드 로그의 시각 (Timestamps·Time Zones)

클라우드 로그의 시각은 거의 다 UTC 이지만, 한 레코드 안에도 "일이 일어난 시각" 과 "서비스가 받은 시각" 이 따로 있고 표기(ISO 8601·유닉스 초·밀리초·strftime)와 화면 시간대가 서비스마다 달라서, 어느 필드를 무슨 뜻으로 읽는지부터 정해야 타임라인이 어긋나지 않습니다.

## 이 형식을 쓰는 아티팩트

이 페이지는 파일 형식이 아니라 여러 로그가 시각을 적는 방식을 다룹니다. [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md), [CloudWatch Logs](../../02-artifacts/aws/cloudwatch-logs.md), [S3 서버 접근 로그](../../02-artifacts/aws/s3-access-logs.md), [AWS VPC 흐름 로그](../../02-artifacts/aws/vpc-flow-logs.md), [Azure 활동 로그](../../02-artifacts/azure/activity-log.md)와 [리소스 로그](../../02-artifacts/azure/resource-logs.md), [Azure 흐름 로그](../../02-artifacts/azure/flow-logs.md), [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [통합 감사 로그 (Unified Audit Log, UAL)](../../02-artifacts/m365/unified-audit-log/index.md), [Google Cloud 감사 로그](../../02-artifacts/gcp/cloud-audit-logs.md)와 [VPC 흐름 로그](../../02-artifacts/gcp/vpc-flow-logs.md), [Google Workspace 관리 감사](../../02-artifacts/google-workspace/admin-audit.md)·[로그인 감사](../../02-artifacts/google-workspace/login-audit.md), [Okta](../../02-artifacts/saas/okta.md), [Slack](../../02-artifacts/saas/slack.md), [GitHub](../../02-artifacts/saas/github.md), [Dropbox·Box](../../02-artifacts/saas/dropbox-box.md)가 여기에 해당합니다.

레코드를 감싼 겉모양과 고유 ID·중복·순서는 [JSON 로그 읽기](json-logs.md)에서, 기록이 얼마나 오래 남는지는 [보관 기간과 라이선스](retention-licensing.md)에서 다룹니다.

## 구조

### 시각 필드 — 발생·수신·게시

한 레코드에 시각 필드가 둘 이상 있으면 대개 하나는 일이 일어난 시각(발생)이고, 다른 하나는 로그 서비스가 받은 시각(수신)이나 조회할 수 있게 된 시각(게시)입니다. 타임라인의 기준은 발생 시각으로 잡고, 수신·게시 시각은 지연을 재거나 수집 범위를 정할 때 씁니다.

| 서비스 | 필드 | 뜻 | 표기 | 근거 |
|---|---|---|---|---|
| CloudTrail | `eventTime` | 요청이 끝난 시각입니다. API 엔드포인트를 제공하는 AWS 호스트의 시계를 따르고, AWS 서비스는 대체로 NTP 로 시계를 맞춥니다. | ISO 8601, UTC | [1] |
| CloudTrail | `userIdentity.sessionContext.attributes.creationDate` | 임시 자격 증명을 발급한 시각입니다. | 설명은 ISO 8601 기본 표기(basic notation)이고, 문서 예시에는 `20131102T010628Z` 와 `2021-02-21T23:46:28Z` 두 모양이 다 있습니다. | [2] |
| CloudWatch Logs | 이벤트 `timestamp` | 이벤트가 일어난 시각입니다. | 1970-01-01 00:00:00 UTC 부터 센 밀리초 | [6] |
| AWS VPC 흐름 로그 | `start`, `end` | 집계 구간(aggregation interval) 안에서 흐름의 첫 패킷과 마지막 패킷을 받은 시각입니다. 실제 패킷 송수신과 최대 60초 차이가 날 수 있습니다. | 유닉스 초 | [7] |
| S3 서버 접근 로그 | Time | 요청을 받은 시각입니다. | `[%d/%b/%Y:%H:%M:%S %z]`, UTC | [8] |
| Azure 활동 로그 | `eventTimestamp` | 요청을 처리한 Azure 서비스가 이벤트를 만든 시각입니다. | ISO 8601, `Z` | [11] |
| Azure 활동 로그 | `submissionTimestamp` | 이벤트를 조회할 수 있게 된 시각입니다. | ISO 8601, `Z` | [11] |
| Azure Monitor Logs | `TimeGenerated` | 원천에서 레코드를 만든 시각입니다. 원천이 값을 주지 않으면 수신 시각이 들어갑니다. | — | [13] |
| Azure Monitor Logs | `_TimeReceived`, `ingestion_time()` | 수집 엔드포인트가 받은 시각, 작업 영역 (workspace) 에 저장되어 조회할 수 있게 된 시각입니다. | — | [13] |
| Azure 흐름 로그 | `time` | 로그를 기록한 시각입니다. | ISO 8601, UTC | [15][16] |
| Azure 흐름 로그 | `flowTuples` 첫 값 | 흐름이 일어난 시각입니다. | 유닉스 epoch (아래 "함정" 참고) | [15][16] |
| Entra 로그인 | `createdDateTime` (Graph), `CreatedDateTime` (Log Analytics `SigninLogs`) | 로그인을 시작한 시각입니다. | 늘 UTC, 예 `2014-01-01T00:00:00Z` | [17][18] |
| Entra 감사 | `activityDateTime` | 활동을 한 시각입니다. | 늘 UTC | [19] |
| M365 UAL | `CreationTime` (`AuditData` 안) | 감사 레코드를 만든 시각입니다. | UTC, 문서 예시는 `2015-06-29T20:03:19` 처럼 `Z` 가 없음 | [23][24] |
| Management Activity API | `contentCreated` | 콘텐츠 묶음을 받아 갈 수 있게 된 시각입니다. | UTC | [24] |
| Google Cloud | `timestamp` | 항목이 설명하는 일이 일어난 시각입니다. 항목의 나이와 보관 기간을 이 값으로 셉니다. | RFC 3339 | [27] |
| Google Cloud | `receiveTimestamp` | Cloud Logging 이 항목을 받은 시각입니다. | RFC 3339 | [27] |
| Google Cloud VPC 흐름 로그 | `start_time`, `end_time` | 집계 구간 안에서 처음·마지막으로 관측한 패킷의 시각입니다. | RFC 3339 문자열 | [31] |
| Google Workspace | `id.time` | 활동이 일어난 시각입니다. | 아래 "함정" 참고 | [32][33] |
| Okta | `published` | 이벤트를 게시한 시각입니다. | `date-time`, 예 `2020-11-16T18:15:12.862Z` | [36][45] |
| Slack 감사 로그 | `date_create` | 이벤트 시각입니다. | 문서 예시가 10자리 정수(유닉스 초 모양) | [38] |
| Slack 접근 로그 | `date_first`, `date_last` | 같은 사용자·IP·사용자 에이전트 조합의 첫 접속과 마지막 접속입니다. | 유닉스 시각, 예시 10자리 | [37] |
| GitHub 감사 로그 | `created_at` | 이벤트 시각입니다. | UTC epoch 밀리초 | [39][40] |
| Dropbox 팀 이벤트 | `timestamp` | 동작을 한 시각입니다. | `%Y-%m-%dT%H:%M:%SZ` | [41] |

### 값 모양 — 네 가지 표기

같은 시각이라도 서비스마다 아래 네 모양 가운데 하나로 적힙니다. 아래 값은 모두 같은 순간(2025-09-26 01:30:45 UTC)을 적은 만든 예시입니다.

| 표기 | 만든 예시 | 쓰는 곳 |
|---|---|---|
| ISO 8601 / RFC 3339 | `2025-09-26T01:30:45Z`, `2025-09-26T01:30:45.123Z` | CloudTrail, Azure, Entra, UAL, Google Cloud, Okta, Dropbox |
| 유닉스 초 (10자리) | `1758850245` | AWS VPC 흐름 로그, Slack, Azure NSG 흐름 로그 예시 |
| 유닉스 밀리초 (13자리) | `1758850245123` | CloudWatch Logs, GitHub, Azure VNet 흐름 로그 예시 |
| strftime + 오프셋 | `[26/Sep/2025:01:30:45 +0000]` | S3 서버 접근 로그 |

소수 자릿수도 서비스마다 다릅니다. Azure 활동 로그 문서 예시에는 `2018-01-29T20:42:31.3810679Z` 처럼 7자리와 `2018-09-04T15:33:43.65Z` 처럼 2자리가 함께 나옵니다[11]. Google Cloud 는 나노초 정밀도로 저장하고, 출력할 때는 늘 `Z` 로 맞춘 뒤 소수 0·3·6·9자리 가운데 하나로 적습니다[27]. 입력으로는 `+05:30` 같은 다른 오프셋도 받습니다[27].

### 화면·질의의 시간대

로그 파일 안의 값은 UTC 여도, 관리 화면과 검색 조건은 보는 사람의 시간대를 따르는 경우가 있습니다.

| 화면·질의 | 시간대 | 근거 |
|---|---|---|
| Entra 관리 센터 로그인 로그 화면 | 로그를 보는 관리자의 시간대입니다. 로그인한 사용자의 시간대가 아닙니다. | [20] |
| Entra 로그에서 내려받은 CSV·JSON | UTC | [21] |
| Purview 감사 검색 화면 | 날짜·시간 범위와 결과의 "Date (UTC)" 모두 UTC | [25] |
| `Search-UnifiedAuditLog` 의 `-StartDate`·`-EndDate` | 시간대 없이 준 값은 UTC 로 해석합니다. | [26] |
| Google Workspace 사용자 로그 이벤트 화면 | "Date" 열은 브라우저 기본 시간대로 보입니다. | [35] |
| Google Workspace 보안 조사 도구 | 최고 관리자가 조사 시간대를 바꿀 수 있고, 바꾼 시간대가 검색 조건과 결과에 함께 적용됩니다. | [35] |
| Google Workspace Reports API `startTime`·`endTime` | RFC 3339, 예 `2010-10-28T10:26:35.000Z` | [32] |
| Google Cloud 로그 탐색기 | 표시 형식에서 "Date, time, and timezone" 을 고를 수 있고 기본은 "Date and time" 입니다. | [30] |

### 지연 시간

일이 일어난 뒤 로그에서 보이기까지 걸리는 시간입니다. 2026년 9월 문서 기준이고, 어느 서비스도 이 시간을 보장하지 않습니다.

| 서비스 | 지연 | 근거 |
|---|---|---|
| CloudTrail → S3 | 로그 파일을 약 5분마다 게시하고, 평균 약 5분 안에 배달합니다. | [4] |
| AWS VPC 흐름 로그 | 집계 구간이 끝난 뒤 CloudWatch Logs 는 약 5분, S3 는 약 10분 걸리고 더 늦을 수 있습니다. | [7] |
| S3 서버 접근 로그 | 대부분 몇 시간 안에 배달하지만 최선 노력(best effort)이라 훨씬 늦거나 빠지거나 두 번 들어올 수 있습니다. | [9] |
| Azure 활동 로그 | 3~20분 | [12][13] |
| Azure 리소스 로그 | 보통 3~10분 | [13] |
| M365 UAL (Exchange·SharePoint·OneDrive·Teams) | 보통 60~90분, 그 밖의 서비스는 더 걸릴 수 있습니다. | [25] |
| Management Activity API | 구독을 만든 뒤 첫 콘텐츠까지 최대 12시간 | [24] |
| Google Workspace | 관리·Drive·Gmail·로그인 이벤트 등은 몇 분, Calendar·Groups 는 수십 분(몇 시간까지), OAuth 는 몇 시간까지, Token 은 두어 시간, 사용자 계정 이벤트는 수십 분, Takeout 완료 이벤트는 데이터 크기에 따라 며칠까지 | [34] |

CloudTrail 배달 주기는 문서끼리 적은 값이 다릅니다. CloudTrail 사용 설명서는 "약 5분마다"[4], S3 로깅 방식 비교 문서는 "데이터 이벤트 5분마다, 관리 이벤트 15분마다"[10] 로 적었습니다. 수집 범위를 정할 때는 긴 쪽을 기준으로 여유를 둡니다.

Purview 감사 검색 작업이 끝나기까지 걸리는 시간은 지연과 다른 문제입니다. 사용자가 많은 테넌트에서 범위를 넓게 잡은 검색 작업은 최대 48시간 걸릴 수 있습니다[25].

### 파일·블롭 이름 속 시각

파일 이름이나 경로에 들어간 시각은 대개 배달·수신 시각이라서, 그 안 레코드의 발생 시각과 같지 않습니다.

| 서비스 | 이름 속 시각 | 레코드 시각과의 관계 | 근거 |
|---|---|---|---|
| CloudTrail | `AccountID_CloudTrail_RegionName_YYYYMMDDTHHmmZ_UniqueString.FileNameFormat` 의 `YYYYMMDDTHHmmZ` | 파일을 배달한 시각(UTC)입니다. 그 시각 이전 아무 때의 레코드가 들어 있을 수 있습니다. | [3] |
| Azure 리소스 로그 → 저장소 | 경로의 `y=`·`m=`·`d=`·`h=` 와 `PT1H.json` | 로그를 받은 시각 기준의 한 시간 블롭입니다. 블롭 URL 의 시간 밖 이벤트가 들어갈 수 있고, Application Insights 처럼 늦은 원격 측정을 올리는 원천이면 48시간 전 데이터까지 들어갈 수 있습니다. 정시 직후에는 이전 시간 블롭과 새 블롭에 동시에 쓰일 수 있습니다. | [14] |
| Google Cloud → Cloud Storage | `08:00:00_08:59:59_S0.json`, `08:00:00_08:59:59_A0:1616681700.json` | 파일 안 시각은 UTC 입니다. `timestamp` 와 `receiveTimestamp` 가 같은 60분 창이면 주 조각(`_Sn.json`)에, 다른 창이면 덧붙임 조각(`_An:유닉스시각.json`)에 들어가고, 덧붙임 조각의 유닉스 시각은 파일을 Cloud Storage 로 보낸 시각입니다. | [29] |

## 읽는 법

1. 레코드마다 시각 필드가 몇 개인지 보고, 위 표로 발생·수신·게시 가운데 무엇인지 정합니다. 타임라인의 기준 열은 발생 시각으로 하고, 수신·게시 시각은 따로 남깁니다.
2. 값 모양을 봅니다. 숫자만 있으면 자릿수로 구분하는데, 10자리면 유닉스 초, 13자리면 유닉스 밀리초일 가능성이 큽니다. 문자열이면 끝의 `Z` 나 `+00:00` 같은 오프셋을 확인합니다.
3. 모두 UTC 의 ISO 8601 로 바꿔 한 열에 모읍니다. 만든 예시로 보면 `1758850245`(초), `1758850245123`(밀리초), `[26/Sep/2025:01:30:45 +0000]` 은 모두 `2025-09-26T01:30:45Z` 가 되고, 한국 시각(UTC+9)으로는 `2025-09-26T10:30:45+09:00` 입니다. 바꿀 때는 원래 값을 지우지 않고 옆 열에 둡니다.

   ```bash
   date -u -d @1758850245 +%Y-%m-%dT%H:%M:%SZ          # 초
   date -u -d @1758850245.123 +%Y-%m-%dT%H:%M:%S.%3NZ   # 밀리초는 1000 으로 나눠 넣는다
   ```

4. 화면 캡처나 관리 콘솔에서 옮겨 적은 시각이 섞여 있으면, 캡처한 사람의 시간대를 확인해 UTC 로 되돌립니다. Entra 화면은 보는 사람의 시간대이고 내려받은 파일은 UTC 입니다[20][21].
5. 조회 범위를 잡을 때는 지연 시간만큼 끝을 늘립니다. `Search-UnifiedAuditLog` 에는 UTC 값(예 `"2018-05-06 14:30:00z"`)을 넣거나, `(Get-Date "5/6/2018 9:30 AM").ToUniversalTime()` 처럼 현지 시각을 UTC 로 바꿔 넣으면 됩니다[26]. 시각 없이 날짜만 주면 그날 자정(0시)이 쓰이고, 시작과 끝 날짜가 같으면 시각을 넣어야 결과가 나옵니다[26].
6. 순서는 파일 순서가 아니라 발생 시각 필드로 다시 정렬합니다. 서비스별 순서 보장과 중복 처리는 [JSON 로그 읽기](json-logs.md)의 "고유 ID·중복·순서" 에 있습니다.

여러 서비스의 시각을 한 타임라인으로 합치는 절차는 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)을 봅니다. 온프레미스 로그와 섞을 때의 공통 원리는 [Windows 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html)과 [Linux 타임라인 만들기](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/timeline.html)에 있습니다.

## 포렌식에서 중요한 점

**증명하는 것.** 로그 시각은 서비스가 그 요청을 처리한 시각이고, CloudTrail `eventTime` 처럼 API 엔드포인트를 제공하는 서비스 쪽 호스트의 시계를 따릅니다[1]. 그래서 "이 시각에 이 서비스가 이 요청을 받아 처리했다" 는 것을 사용자 기기의 시계와 상관없이 보여 줍니다. 보고서에는 "2025-09-26 01:30:45 UTC 에 이 계정으로 로그인한 기록이 있다" 처럼 시간대를 붙여 기록으로 확인되는 만큼만 적습니다.

**증명하지 못하는 것.** 로그 시각은 사용자 기기의 시계나 사용자가 있던 곳의 시간대를 알려 주지 않습니다. Entra 화면에 보이는 시각이 로그인한 사람의 현지 시각인 것도 아닙니다[20]. 위치는 [IP·사용자 에이전트·위치 정보](ip-ua-geo.md)에서 따로 판단합니다.

**발생과 수신의 차이는 조작의 증거가 아닙니다.** 발생 시각과 수신 시각이 벌어지는 것은 배달 지연과 늦은 원천 때문에 흔히 생깁니다. CloudTrail 은 배달이 늦은 레코드에 `addendum` 을 붙이고[1], Google Cloud 는 늦게 받은 항목을 덧붙임 조각에 넣습니다[29]. `addendum` 필드를 읽는 법은 [JSON 로그 읽기](json-logs.md)에 있습니다.

**원천 시계가 크게 틀린 기록은 아예 없을 수 있습니다.** 서비스가 너무 오래되었거나 미래인 시각을 받지 않거나 바꿔 넣기 때문입니다.

| 서비스 | 받지 않거나 바꾸는 조건 | 근거 |
|---|---|---|
| CloudWatch Logs `PutLogEvents` | 14일보다 오래되었거나 로그 그룹 보관 기간보다 앞선 이벤트, 2시간 넘게 미래인 이벤트는 거부합니다. | [6] |
| Google Cloud Logging | 보관 기간보다 오래되었거나 24시간 넘게 미래인 항목은 버립니다. | [28] |
| Azure Monitor Logs | `TimeGenerated` 가 받은 시각보다 2일 넘게 과거이거나 1일 넘게 미래면 받은 시각으로 바꿔 넣습니다. 원천이 값을 주지 않으면 `_TimeReceived` 와 같게 넣습니다. | [13] |

Azure Monitor 에서 `TimeGenerated` 와 `_TimeReceived` 가 똑같은 레코드는 원천이 시각을 주지 않았거나 원천 시각이 허용 범위를 벗어났을 가능성이 있습니다[13]. 이런 레코드의 `TimeGenerated` 는 발생 시각이 아니라 수신 시각으로 읽습니다.

**보관 기간은 발생 시각으로 셉니다.** Google Cloud 는 `timestamp` 로 항목의 나이와 보관 기간을 계산하고[27], CloudTrail Lake 도 `eventTime` 이 보관 기간 안인지로 남길지를 정합니다[5]. 늦게 들어온 레코드는 받은 뒤 얼마 안 되어 보관 기간을 넘길 수 있습니다.

## 함정

- **Entra 화면과 파일의 시간대가 다릅니다.** 화면은 보는 사람의 시간대, 내려받은 CSV·JSON 은 UTC 입니다[20][21]. 화면 캡처와 파일을 한 표에 섞으면 시간대 차이만큼 어긋납니다.
- **UAL 조회에 현지 날짜를 그대로 넣으면 범위가 밀립니다.** `Search-UnifiedAuditLog` 는 시간대 없는 값을 UTC 로 해석하므로[26], 한국 시각(UTC+9)으로 생각한 날짜를 그대로 넣으면 9시간 어긋난 범위를 조회합니다.
- **Management Activity API 의 `startTime`·`endTime` 은 발생 시각 범위가 아닙니다.** 이 두 값은 `contentCreated`, 곧 콘텐츠를 받아 갈 수 있게 된 시각을 기준으로 거르고, 시작은 포함·끝은 제외입니다[24]. 두 값은 24시간 넘게 벌어지면 안 되고 시작은 7일 이내여야 합니다[24].
- **초와 밀리초가 섞입니다.** Slack·AWS VPC 흐름 로그는 초, CloudWatch Logs·GitHub 는 밀리초입니다[6][7][37][39]. Azure 흐름 로그는 NSG·VNet 문서 모두 "UNIX epoch" 라고만 적었지만, 예시 값은 NSG 가 `1487282421` 처럼 10자리(초), VNet 이 `1663146003599` 처럼 13자리(밀리초)입니다[15][16]. 실제 값의 자릿수를 보고 판단합니다.
- **Google Workspace `id.time` 은 문서끼리 표기가 다릅니다.** Reports API 참조 문서는 "UNIX epoch 초" 라고 설명하는데[32], 같은 API 가이드의 예시 응답은 `"2011-06-17T15:39:18.460Z"` 같은 RFC 3339 문자열입니다[33]. 실제 값의 모양을 보고 읽습니다.
- **UAL `CreationTime` 에는 시간대 표시가 없을 수 있습니다.** 스키마는 UTC 라고 정의하지만 문서 예시 값은 `2015-06-29T20:03:19` 처럼 끝에 `Z` 가 없습니다[23][24]. 이런 값을 도구가 현지 시각으로 읽지 않도록 UTC 로 지정해 바꿉니다.
- **S3 서버 접근 로그 시각은 ISO 8601 파서가 그대로 읽지 못합니다.** `[06/Feb/2019:00:00:38 +0000]` 처럼 대괄호와 strftime 형식이라[8] 형식 문자열을 지정해 바꿉니다.
- **Entra 비대화형 로그인은 묶여서 같은 시각처럼 보일 수 있습니다.** 화면은 시각만 다르고 나머지가 같은 로그인을 한 줄로 묶어 "# sign-ins" 열에 개수를 적고, 펼치면 각각의 시각이 보입니다[22].
- **VPC 흐름 로그의 `start`·`end` 는 패킷 시각과 최대 60초 차이가 납니다.** 집계 구간 안에서 받은 시각이라[7], 초 단위로 다른 로그와 맞출 때 이 폭을 둡니다.
- **파일 이름 시각으로 범위를 자르면 레코드가 빠집니다.** CloudTrail 파일 이름, Azure `PT1H.json` 경로, Google Cloud 조각 이름은 배달·수신 기준이라[3][14][29], 조사 구간보다 뒤 시각의 파일까지 함께 받습니다.
- **CloudTrail `creationDate` 는 두 모양으로 나옵니다.** 기본 표기 `20131102T010628Z` 와 확장 표기 `2021-02-21T23:46:28Z` 가 문서 예시에 함께 있어[2] 두 모양을 모두 읽도록 파서를 씁니다.

## 도구

- **Microsoft-Extractor-Suite `Get-UAL`**: 조사 기간을 분 단위 창으로 나눠 UAL 을 받고, 창 하나의 결과가 API 상한 5000건에 닿으면 창을 절반으로 줄여 다시 받습니다[42]. 조사 기간의 끝 시각은 `ToUniversalTime()` 으로 UTC 로 바꾸고, 수집 로그에는 창 경계를 UTC 로 적습니다[42]. 가장 작은 창(0.1분)에서도 5000건에 닿으면 "SOME EVENTS IN THIS RANGE ARE NOT CAPTURED" 오류를 남기고 넘어가므로[42], 수집 로그에서 이 줄을 찾아 빠진 구간을 기록합니다.
- **Untitled Goose Tool**: UAL 결과의 `AuditData` 안 `CreationTime` 을 읽어 받은 구간의 처음과 끝을 계산합니다[43].
- **ALFA**: 사용자가 준 날짜·시각에 시간대가 없으면 UTC 로 보고 RFC 3339 문자열로 바꿉니다[44].
- **KQL**: Azure Monitor Logs 에서 `ingestion_time() - TimeGenerated`, `_TimeReceived - TimeGenerated` 로 레코드마다 지연을 잴 수 있습니다[13].
- **`date`·스프레드시트·파이썬 `datetime`**: 유닉스 초·밀리초를 UTC 로 바꿀 때 씁니다. 결과는 원래 값과 나란히 둡니다.

함께 볼 페이지: [클라우드 타임라인](../../03-techniques/analysis/timeline.md), [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md), [JSON 로그 읽기](json-logs.md), [보관 기간과 라이선스](retention-licensing.md), [IP·사용자 에이전트·위치 정보](ip-ua-geo.md), [Windows 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html), [Linux 타임라인 만들기](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/timeline.html).

## 참고 문헌

1. AWS, "CloudTrail record contents for management, data, and network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
2. AWS, "CloudTrail userIdentity element", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
3. AWS, "CloudTrail log file examples", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-examples.html
4. AWS, "How CloudTrail works", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/how-cloudtrail-works.html
5. AWS, "CloudTrail Lake concepts and terminology", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake-concepts.html
6. AWS, "PutLogEvents", Amazon CloudWatch Logs API Reference. https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutLogEvents.html
7. AWS, "Flow log records", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html
8. AWS, "Amazon S3 server access log format", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/LogFormat.html
9. AWS, "Logging requests with server access logging", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html
10. AWS, "Logging options for Amazon S3", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/logging-with-S3.html
11. Microsoft, "Azure activity log event schema" (ms.date 2026-03-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
12. Microsoft, "Activity log in Azure Monitor" (ms.date 2026-05-04). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
13. Microsoft, "Log data ingestion time in Azure Monitor" (2026-07-31 갱신). https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-ingestion-time
14. Microsoft, "Azure resource logs" (ms.date 2025-07-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs.md
15. Microsoft, "NSG Flow Logs Overview" (ms.date 2025-12-18). https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/network-watcher/nsg-flow-logs-overview.md
16. Microsoft, "Virtual Network Flow Logs" (ms.date 2026-02-10). https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/network-watcher/vnet-flow-logs-overview.md
17. Microsoft, "signIn resource type", Microsoft Graph v1.0 (2025-11-28 갱신). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-1.0
18. Microsoft, "SigninLogs", Azure Monitor Logs table reference (2026-08-27 갱신). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
19. Microsoft, "directoryAudit resource type", Microsoft Graph (2024-05-24 갱신). https://learn.microsoft.com/en-us/graph/api/resources/directoryaudit
20. Microsoft, "Learn about the sign-in log activity details" (ms.date 2026-03-04). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
21. Microsoft, "How to download logs in Microsoft Entra ID" (ms.date 2024-11-08). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/howto-download-logs.md
22. Microsoft, "Non-interactive sign-in logs" (ms.date 2026-02-09). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-noninteractive-sign-ins.md
23. Microsoft, "Office 365 Management Activity API schema" (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
24. Microsoft, "Office 365 Management Activity API reference" (2024-12-03 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference
25. Microsoft, "Search the audit log" (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-search
26. Microsoft, "Search-UnifiedAuditLog", Exchange PowerShell 도움말 원본. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Search-UnifiedAuditLog.md
27. Google Cloud, "LogEntry", Cloud Logging API (2026-09-04 갱신). https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry
28. Google Cloud, "Routing and storage overview", Cloud Logging (2026-09-25 갱신). https://cloud.google.com/logging/docs/routing/overview
29. Google Cloud, "View logs routed to Cloud Storage", Cloud Logging (2026-09-25 갱신). https://cloud.google.com/logging/docs/export/storage
30. Google Cloud, "Logs Explorer interface", Cloud Logging (2026-09-25 갱신). https://cloud.google.com/logging/docs/view/logs-explorer-interface
31. Google Cloud, "About VPC Flow Logs records" (2026-09-18 갱신). https://cloud.google.com/vpc/docs/about-flow-logs-records
32. Google, "Method: activities.list", Admin SDK Reports API (2026-09-09 갱신). https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
33. Google, "Admin Activity Report", Admin SDK Reports API Guides (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/guides/manage-audit-admin
34. Google, "Data retention and lag times", Google Workspace Admin Help (2026-09-25 갱신). https://support.google.com/a/answer/7061566
35. Google, "User log events", Google Workspace Admin Help (2026-09-18 갱신). https://support.google.com/a/answer/4580120
36. Okta, Management API OpenAPI 명세 2025.08.0 (`LogEvent` 스키마). https://github.com/okta/okta-management-openapi-spec/blob/master/dist/2025.08.0/management-minimal.yaml
37. Slack, "team.accessLogs method". https://api.slack.com/methods/team.accessLogs
38. Slack, "Audit Logs API". https://api.slack.com/admins/audit-logs
39. GitHub, "Using the audit log API for your enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/using-the-audit-log-api-for-your-enterprise
40. GitHub, "Exporting audit log activity for your enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/exporting-audit-log-activity-for-your-enterprise
41. Dropbox, dropbox-api-spec (`common.stone` 의 `DropboxTimestamp`, `team_log.stone` 의 `TeamEvent`). https://github.com/dropbox/dropbox-api-spec
42. Invictus Incident Response, Microsoft-Extractor-Suite (`Scripts/Get-UAL.ps1`). https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-UAL.ps1
43. CISA, Untitled Goose Tool (`goosey/m365_datadumper.py`). https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/m365_datadumper.py
44. Invictus Incident Response, ALFA (`alfa/utils/dates.py`). https://github.com/invictus-ir/ALFA/blob/main/alfa/utils/dates.py
45. Okta, okta-developer-docs, "Event object" (Event Hook 구현 가이드의 LogEvent 예시). https://github.com/okta/okta-developer-docs/blob/master/packages/@okta/vuepress-site/docs/guides/event-hook-implementation/main/nodejs/event-object.md
