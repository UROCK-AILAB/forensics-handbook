---
title: "탐지 규칙으로 로그 검색하기"
parent: "기법 · 분석"
nav_order: 710
---

# 탐지 규칙으로 로그 검색하기 (Sigma·KQL)

수집한 클라우드 로그에 공개 탐지 규칙을 돌려 먼저 읽을 레코드를 추리고, 걸린 레코드는 원본 로그로 돌아가 다시 해석하는 방법입니다.

## 언제 쓰나

감사 로그가 수십만 줄이라 처음부터 읽기 어렵거나, 사건 범위를 몰라 알려진 흔적(로깅 중지, 새 액세스 키, 메일 전달 규칙, 역할 할당 등)이 있는지부터 한 번에 확인하고 싶을 때 씁니다. 규칙 검색은 타임라인을 대신하지 않고, [클라우드 타임라인](timeline.md)에 넣을 시작점을 찾는 단계입니다.

이 페이지에서 다루는 도구는 두 가지입니다. 시그마 규칙 (Sigma rule) 은 로그 원천과 검색 조건을 YAML 로 적는 벤더 중립 형식이고, 변환기 (backend) 가 이를 각 플랫폼의 조회 언어로 바꿉니다[1][5]. KQL (Kusto Query Language) 은 Log Analytics·Microsoft Sentinel·Defender XDR 고급 헌팅 (advanced hunting) 에서 쓰는 조회 언어이고, 읽기 전용 요청이며 표 형태의 입력을 파이프(`|`)로 다음 연산자에 넘깁니다[9][10].

서비스가 스스로 내린 판정(Defender 경고, GuardDuty 결과, Entra ID 위험 탐지)은 규칙 검색과 성격이 다르므로 [Defender 경고와 기록](../../02-artifacts/m365/defender-xdr.md)과 [GuardDuty](../../02-artifacts/aws/guardduty.md)에서 따로 다룹니다.

## Sigma 규칙의 짜임

규칙에서 반드시 있어야 하는 부분은 `title`·`logsource`·`detection` 셋이고, `detection` 안에는 `condition` 이 꼭 있어야 합니다[1]. `logsource` 는 `category`·`product`·`service` 세 값으로 로그 원천을 가리키고, 변환기 설정이 이 값을 실제 인덱스나 테이블로 연결합니다[1]. `logsource` 안의 `definition` 은 변환기가 읽지 않는 설명 필드라서, 그 규칙이 동작하려면 어떤 로그 설정이 켜져 있어야 하는지를 사람에게 알려 줍니다[1].

아래는 SigmaHQ 저장소의 AWS 규칙 `aws_update_login_profile.yml` 에서 `logsource` 부터 끝까지 옮긴 것입니다[7].

```yaml
logsource:
    product: aws
    service: cloudtrail
detection:
    selection:
        eventSource: 'iam.amazonaws.com'
        eventName: 'UpdateLoginProfile'
    filter_main_user_identity:
        userIdentity.arn|fieldref: requestParameters.userName
    condition: selection and not 1 of filter_main_*
falsepositives:
    - Legitimate user account administration
level: high
```

`selection` 은 CloudTrail 레코드의 `eventSource` 와 `eventName` 이 모두 맞는 레코드를 고르고, `filter_main_user_identity` 는 두 필드 값을 비교하는 `fieldref` 수식어로 호출한 주체의 `userIdentity.arn` 과 대상 `requestParameters.userName` 이 같은 레코드를 골라냅니다[3][7]. `condition` 은 앞의 것에서 뒤의 것을 뺍니다. 같은 모양으로 `1 of selection*`, `all of ...`, and·or·not, 괄호를 조합할 수 있고, 이름이 `_` 로 시작하는 검색 식별자는 `them` 에 들어가지 않습니다[1].

값 비교에는 기본 규칙이 몇 가지 있습니다. 문자열은 대소문자를 구분하지 않고 `*`·`?` 와일드카드를 쓸 수 있지만, 정규식은 기본으로 대소문자를 구분합니다[1]. 대소문자를 구분하려면 `cased` 수식어를 붙입니다[3]. 그 밖에 `contains`·`startswith`·`endswith`·`exists`·`neq`·`cidr`·`re`·크기 비교(`lt`·`gt` 등)와 날짜에서 분·시·일·주·월·연을 뽑는 시간 수식어가 있습니다[3].

조사에 쓸 때 눈여겨볼 선택 항목은 셋입니다.

| 항목 | 값 | 해석 |
|---|---|---|
| `status` | stable / test / experimental / deprecated / unsupported | test 는 환경에 따라 조금 손봐야 할 수 있는 규칙, experimental 은 오탐이나 잡음이 있을 수 있는 규칙입니다[1]. |
| `level` | informational / low / medium / high / critical | informational 은 이벤트에 꼬리표를 다는 보강용이라 경보를 내지 않습니다. low 는 정기 검토, medium 은 그보다 자주 손으로 검토, high 는 서둘러 검토, critical 은 바로 검토할 대상입니다[1]. |
| `falsepositives` | 자유 문장 | 규칙이 정상 활동에도 걸리는 경우를 적어 둡니다. 적중을 해석할 때 가장 먼저 읽습니다[1]. |

`falsepositives` 에 적힌 정상 원인은 이런 것들입니다. AWS SSO 포털로 로그인해도 `GetSigninToken` 이벤트가 생겨 콘솔 `GetSigninToken` 규칙에 걸리고, Terraform 같은 자동화도 `AssumeRole` 규칙에 걸립니다[7]. 관리자가 Okta 관리 콘솔을 처음 쓰기 시작하면 Okta 의 판단 기준이 이를 이상 행동으로 잘못 보아 새 행동 규칙에 걸릴 수 있습니다[8].

## 서비스별 로그 원천과 규칙 묶음

Sigma 명세의 분류표(taxonomy)가 정한 클라우드 로그 원천과, SigmaHQ 저장소에서 그 원천을 쓰는 규칙 폴더는 아래와 같습니다[2][7][8]. 규칙 수와 `status` 집계는 2026년 9월 저장소 사본 기준입니다.

| 서비스 | `logsource` | 규칙 폴더 | 규칙이 보는 필드 예 | 규칙 수(status) |
|---|---|---|---|---|
| AWS | `product: aws`, `service: cloudtrail` | `rules/cloud/aws/cloudtrail/` | `eventSource`, `eventName`, `userIdentity.arn` | 57 (test 40, experimental 15, stable 2) |
| Azure·Entra ID | `product: azure`, `service:` `activitylogs`·`auditlogs`·`riskdetection`·`pim`·`signinlogs` | `rules/cloud/azure/` 아래 다섯 폴더 | `ResultType`, `riskEventType` | 123 (전부 test) |
| Google Cloud·Google Workspace | `product: gcp`, `service:` `gcp.audit`·`google_workspace.admin` (규칙에는 `google_workspace.login` 도 씀) | `rules/cloud/gcp/audit/`, `rules/cloud/gcp/gworkspace/` | `gcp.audit.method_name`, `eventName`, `protoPayload.metadata.event.eventName` | 26 (test 23, experimental 3) |
| Microsoft 365 | `product: m365`, `service:` `audit`·`exchange`·`threat_detection`·`threat_management` | `rules/cloud/m365/` | `eventSource`, `eventName`, `status` | 19 (test 17, experimental 2) |
| Okta·GitHub·Bitbucket | `okta`/`okta`, `github`/`audit`, `bitbucket`/`audit` | `rules/identity/okta/`, `rules/application/github/audit/`, `rules/application/bitbucket/audit/` | `eventType`, `action`, `auditType.action` | 50 (test 48, experimental 2) |

규칙은 두 부류로 나뉩니다. 한 부류는 원시 활동을 찾는 규칙으로, CloudTrail 의 `eventName`, Google Cloud 의 메서드 이름, Okta 의 `eventType`, GitHub 의 `action` 같은 작업 이름에 조건을 겁니다[7][8]. 다른 부류는 벤더가 이미 내린 판정을 다시 거르는 규칙으로, Entra ID `riskdetection` 규칙은 `riskEventType` 값 하나마다 규칙 하나를 두고, M365 `threat_management` 규칙은 경고 이름 문자열(예: `Activity performed by terminated user`)에, Okta 규칙은 `security.threat.detected` 이벤트에 기댑니다[7][8]. 뒤쪽 부류는 벤더 탐지가 켜져 있고 라이선스가 있어야 입력 자체가 생기는데, Entra ID 위험 탐지는 대부분 Microsoft Entra ID P2 가 있어야 세부 내용이 나오고 없는 테넌트에는 `Additional risk detected` 로만 남습니다[20].

`definition` 에는 이런 전제 조건이 적혀 있습니다. GitHub 규칙은 감사 로그 스트리밍이 켜져 있어야 입력이 생기고, Bitbucket 규칙은 규칙마다 감사 로그 수준이 "Basic" 이나 "Advance" 여야 하며, M365 규칙 하나는 'eDiscovery search or exported' 경고가 켜져 있어야 합니다[7][8].

## 절차

1. **로그 원천부터 맞춘다.** 돌릴 규칙의 `logsource` 와 `definition` 을 읽고, 실제 데이터에 그 원천이 있는지와 요구하는 설정이 켜져 있었는지를 확인합니다. 원천이 없으면 그 규칙은 돌려도 알 수 있는 것이 없습니다. 보관 기간과 기본으로 꺼진 로그는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에서 확인합니다.
2. **필드 이름을 수집 형식에 맞춘다.** 같은 로그라도 수집 경로에 따라 필드 이름이 다릅니다(아래 "함정과 한계" 참고). Graph API JSON, Log Analytics 테이블, Cloud Logging 형식, Reports API, 도구가 만든 CSV 가운데 무엇으로 받았는지 보고 규칙의 필드 이름을 바꿉니다[6][7]. JSON 레코드의 중첩 필드를 점으로 이어 부르는 방식은 [JSON 로그 읽기](../../01-foundations/logging/json-logs.md)를 봅니다.
3. **규칙을 조회 언어로 바꿔 돌린다.** sigma-cli 로 변환하고, 클라우드 규칙은 테이블을 직접 지정합니다(아래 "도구" 참고)[5][6].
4. **적중을 걸러 읽는다.** 걸린 레코드마다 규칙의 `falsepositives` 와 `status` 를 함께 보고, 원본 레코드를 열어 주체·대상·IP·사용자 에이전트를 다시 읽습니다[1][7]. 로그인 기록은 [이상한 로그인 가려내기](suspicious-sign-ins.md), 역할·정책 변경은 [권한 변화 따라가기](permission-changes.md)의 방법으로 이어서 봅니다.
5. **여러 적중을 묶는다.** 상관 규칙 (correlation rule) 으로 같은 사용자나 같은 출발지의 적중을 시간 창 안에서 묶습니다. 형식은 `event_count`·`value_count`·`temporal`·`temporal_ordered` 에 수치 필드를 모으는 `value_sum`·`value_avg`·`value_percentile` 까지 있고, `group-by` 와 `timespan`(예: `90m`)으로 묶음과 창을 정합니다[4]. 명세의 `value_count` 예는 출발지와 목적지 호스트마다 하루 안에 서로 다른 사용자 계정 100개 이상으로 로그인에 실패한 경우를 찾습니다[4].
6. **적중이 없을 때는 원천을 먼저 적는다.** 그 기간의 로그가 보관돼 있었는지, 라이선스와 설정 때문에 처음부터 생기지 않았는지를 먼저 기록하고, 그다음에 "규칙 조건에 맞는 레코드가 없었다" 고 씁니다.

## 도구

### sigma-cli 와 Kusto 변환기

sigma-cli 는 변환기와 처리 파이프라인 (processing pipeline) 을 골라 규칙 파일이나 폴더를 쿼리로 바꿉니다. 변환기는 플러그인으로 설치하고, 쓸 수 있는 변환기·파이프라인은 `sigma list` 로, 출력 형식은 `-f`, 출력 파일은 `-o` 나 `--output-dir` 로 정합니다[5].

```text
sigma plugin install <backend>
sigma convert -t <backend> -p <pipeline> [-p <pipeline> ...] <directory or file>
sigma convert -t kusto -p microsoft_xdr path/to/your/rule.yml
```

KQL 로 바꾸는 변환기는 pySigma Kusto 변환기이고, 예전 이름은 pySigma Microsoft 365 Defender Backend 입니다[6]. 파이프라인은 셋이고 성숙도가 다릅니다.

| 파이프라인 | 대상 | 상태 |
|---|---|---|
| Microsoft XDR (`microsoft_xdr`) | Defender XDR 고급 헌팅 | Production-ready |
| Sentinel ASIM | Microsoft Sentinel 의 ASIM 정규화 테이블 | Beta, 필드 매핑이 적음 |
| Azure Monitor | Log Analytics 테이블 | Alpha, 필드 매핑은 `SecurityEvent`·`SigninLogs` 두 테이블만 |

변환기는 쿼리할 테이블을 ① 코드에서 넘긴 `query_table` ② 사용자 YAML 파이프라인의 `query_table` ③ 매핑표에 있는 `logsource.category` ④ `detection` 안의 `EventID`·`EventCode` 순서로 정하고, 넷 다 없으면 오류를 냅니다[6]. 매핑표에 흔히 있는 category 는 `process_creation`·`file_*`·`registry_*` 같은 엔드포인트 쪽입니다[6]. 클라우드 규칙은 대부분 category 없이 `product`·`service` 만 적혀 있으므로, 사용자 파이프라인에서 `query_table` 을 지정해야 변환됩니다. 기본 파이프라인의 우선순위가 10이라서 사용자 파이프라인은 우선순위를 9 이하로 둡니다[6]. 규칙의 필드가 그 테이블 정의에 없으면 `Invalid SigmaDetectionItem field name encountered` 오류가 나고, 사용자 파이프라인에 `field_name_mapping` 변환을 넣어 고칩니다[6].

### KQL 로 직접 쓰기

Microsoft 쪽 로그를 Log Analytics 나 Sentinel 에 모아 두었다면 `SigninLogs`·`AADNonInteractiveUserSignInLogs`·`AuditLogs`·`AzureActivity` 테이블에 KQL 을 바로 씁니다. `SigninLogs` 의 `ResultType` 은 로그인 결과 코드이고 `0` 이 성공입니다[21]. 아래 쿼리는 최근 60일 동안 성공한 역할 할당 쓰기를 대상 리소스 제공자별로 세고 호출한 계정을 모읍니다[13].

```kusto
AzureActivity
| where TimeGenerated > ago(60d) and Authorization contains "Microsoft.Authorization/roleAssignments/write" and ActivityStatus == "Succeeded"
| parse ResourceId with * "/providers/" TargetResourceAuthProvider "/" *
| summarize count(), makeset(Caller) by TargetResourceAuthProvider
```

로그가 늦게 들어오는지는 `ingestion_time()` 과 `TimeGenerated` 의 차이로 잽니다. 아래 두 줄은 `Heartbeat` 테이블로 지연을 재는 쿼리의 일부이고, 다른 테이블에도 같은 식을 붙일 수 있습니다[14]. 탐지 창을 로그 끝부분까지 넓힐 때 이 값을 참고합니다.

```kusto
| extend E2EIngestionLatency = ingestion_time() - TimeGenerated
| extend AgentLatency = _TimeReceived - TimeGenerated
```

Defender XDR 고급 헌팅에는 클라우드 조사에 쓸 테이블이 따로 있습니다(2026년 7월 27일 문서 기준)[11].

| 테이블 | 담는 것 |
|---|---|
| `EntraIdSignInEvents` (`AADSignInEventsBeta`) | Entra ID 대화형·비대화형 로그인 |
| `EntraIdSpnSignInEvents` (`AADSpnSignInEventsBeta`) | 서비스 주체·관리 ID 로그인 |
| `CloudAppEvents` | Office 365 와 다른 클라우드 앱의 계정·개체 이벤트 |
| `CloudAuditEvents` | Defender for Cloud 가 보호하는 클라우드 플랫폼의 감사 이벤트 |
| `GraphAPIAuditEvents` | 테넌트 리소스에 대한 Microsoft Graph API 요청 |
| `IdentityLogonEvents` | Active Directory 와 Microsoft 온라인 서비스 인증 |
| `OAuthAppInfo` (미리 보기) | Entra ID 에 등록된 Microsoft 365 연결 OAuth 앱 |

`CloudAppEvents` 에는 규칙 대신 "그 사용자에게 드문가" 를 보는 열이 있습니다. `LastSeenForUser` 는 속성마다 마지막으로 본 뒤 지난 일수를 담는데 `0` 은 오늘, 음수는 처음 보는 값, 양수는 경과 일수입니다[12]. `UncommonForUser` 는 사용자에게 드문 속성 이름 목록이고, 보강 대상이 아닌 이벤트는 빈 문자열(`""`), 보강했지만 이상이 없는 이벤트는 `[]` 입니다[12]. 그래서 빈 문자열을 "이상 없음" 으로 읽으면 안 됩니다.

### 다른 플랫폼의 조회 언어

Sigma 규칙을 옮기거나 같은 조건을 손으로 쓸 때, 플랫폼마다 대소문자와 검색 범위가 다릅니다.

| 플랫폼 | 조회 수단 | 대소문자 | 범위·보관 (문서 기준) |
|---|---|---|---|
| Log Analytics·Sentinel·Defender XDR | KQL | 테이블·열 이름·연산자·함수 모두 구분함[9] | 고급 헌팅은 Defender XDR 원시 데이터 30일, Sentinel 작업 영역을 연결하면 그 테이블의 분석 계층 보관 기간만큼(2026년 8월 7일 문서)[10] |
| Google Cloud | Logging query language | 구분하지 않음. 정규식과 `AND`·`OR` 같은 논리 연산자는 예외이고 논리 연산자는 대문자로 씀[15] | 시각은 RFC 3339(`"2024-08-02T15:01:23.045Z"`) 나 ISO 8601 날짜, 나노초 단위(2026년 9월 25일 문서)[15] |
| AWS CloudTrail 이벤트 기록 | 콘솔·API 검색 | — | 최근 90일 관리 이벤트, 한 계정·한 리전, 속성 필터 하나와 시간 범위만[17] |
| AWS CloudTrail Lake | SQL | — | 여러 리전·계정, `JOIN` 지원, 보관 최대 3,653일(1년 연장형 요금) 또는 2,557일(7년 요금)[16] |
| Okta System Log API | SCIM 필터·`q` 키워드 | — | `filter=eventType eq "user.session.start" and outcome.result eq "FAILURE"` 식으로 쓰고, SCIM 필터에 `published` 는 쓸 수 없음[18]. 콘솔 필터의 contains 는 `debugContext.debugData.url` 에 안 됨[19] |

CloudTrail 이벤트 기록은 조건을 하나만 걸 수 있으므로 여러 조건을 묶는 Sigma 규칙은 CloudTrail Lake 나 따로 받아 둔 로그 파일에서 돌립니다[16][17]. 로그를 받아 두는 방법은 [AWS·Azure·GCP 수집](../acquisition/iaas-collection.md)과 [Microsoft 365 수집 도구](../acquisition/m365-collection.md)에 있습니다.

### 규칙 대신 이벤트 사슬을 보는 도구

ALFA 는 Google Workspace 감사 로그의 이벤트를 하나씩 MITRE ATT&CK 클라우드 기법에 대응시킨 뒤, 대응된 이벤트를 시간 순서로 읽어 공격 단계가 이어지는 사슬(kill chain)을 찾습니다[24]. 사슬 판정 기준은 `config/config.yml` 에 고정해 둔 상수로, 사슬 길이 최소값 `min_chain_length` 가 7, 사슬 점수 최소값 `min_chain_statistic` 이 0.6 이고, 조사하는 Workspace 에 맞게 검토해 고칩니다[24]. ALFA 는 기본으로 양성(benign) 활동을 걸러 불러오므로 전체를 보려면 `filter=False` 로 불러옵니다[24].

## 함정과 한계

**대소문자 기준이 반대입니다.** Sigma 값 비교는 기본으로 대소문자를 구분하지 않고 KQL 은 모든 것을 구분합니다[1][9]. 변환된 쿼리가 대소문자를 구분하지 않는 연산자로 옮겨졌는지 한 번 확인합니다.

**필드 이름이 수집 형식마다 다릅니다.** 같은 저장소 안에서도 Entra ID 로그인 규칙은 Log Analytics 의 `ResultType` 과 다른 형식의 `Status`·`properties.message`·`ActivityDetails` 를 섞어 씁니다[7][21]. Google Cloud 규칙은 `gcp.audit.method_name` 을 쓰지만 LogEntry 원본 필드는 `protoPayload.methodName` 입니다[7][22]. Google Workspace 관리 규칙은 `eventService`·`eventName`·`setting_name` 을 쓰지만 Reports API 응답은 `events[].name`·`events[].parameters[].name`·`events[].parameters[].value` 구조이고, 로그인 규칙은 Cloud Logging 으로 공유된 형식의 `protoPayload.metadata.event.eventName` 을 씁니다[7][23]. 필드를 바꾸지 않고 돌리면 오류 없이 0건이 나올 수 있습니다.

**시간 수식어는 시간대를 바꾸지 않습니다.** 시간 수식어는 시간대·형식 변환을 하지 않으므로 "업무 시간 밖" 같은 조건은 로그에 적힌 시각 그대로 계산됩니다[3]. 로그 시각이 UTC 인지 먼저 확인합니다([클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)).

**상관 규칙은 변환 대상에 따라 조용히 달라집니다.** 대상 시스템이 사건 순서를 알아보지 못하거나 시간 창을 정각 단위 같은 고정 경계로만 처리하면 변환기는 경고만 내고 쿼리를 만듭니다[4]. 고정 경계로 바뀌면 `timespan: 1h` 규칙은 두 시간대에 걸친 사건을 놓치고(거짓 음성), 순서를 못 보면 순서가 다른 사건까지 잡습니다(거짓 양성)[4].

**경고 이름에 기대는 규칙은 이름이 바뀌면 안 걸립니다.** M365 `threat_management` 규칙은 경고 이름 문자열을 그대로 비교하므로, 서비스가 경고 이름을 바꾸면 조용히 0건이 됩니다[7].

**대부분 stable 이 아닙니다.** 위 표처럼 클라우드 규칙 275개 가운데 stable 은 2개이고 나머지는 test 나 experimental 입니다[1][7][8].

**출처끼리 이름이 다른 곳이 있습니다.** Entra ID 문서는 불가능 이동 위험 탐지의 `riskEventType` 을 `mcasImpossibleTravel` 로 적었지만, SigmaHQ 규칙은 `impossibleTravel` 을 찾습니다[7][20]. Sigma 분류표에는 `google_workspace.login` 이 없지만 저장소의 Google Workspace 로그인 규칙은 이 `service` 를 씁니다[2][7]. 규칙 값을 실제 로그의 값과 한 번 대조한 뒤 돌립니다.

**규칙은 알려진 것만 찾습니다.** DFRWS USA 2023 발표에서 Casey 는 SaaS 데이터 분석의 과제로 처음 보는 활동을 찾는 이상 탐지, 데이터 품질·라벨과 복합 사건 문제가 있는 분류, 규칙을 만들고 유지하는 부담과 복합 규칙의 어려움을 들었습니다[25]. 규칙에서 0건이 나와도 타임라인과 계정별 검토는 따로 해야 합니다.

**고급 헌팅은 30일까지입니다.** Sentinel 을 연결하지 않았다면 고급 헌팅으로는 Defender XDR 원시 데이터를 최근 30일만 볼 수 있습니다[10]. 오래된 사건은 [로그부터 지키기](../acquisition/log-preservation.md)에서 받아 둔 사본에 규칙을 돌립니다.

## 결과를 어떻게 해석하나

**증명하는 것:** 그 기간, 그 원천의 로그에 규칙 조건에 맞는 레코드가 있었다는 사실입니다. 걸린 레코드의 주체·작업·대상·시각은 원본 레코드에서 다시 읽어 적습니다.

**증명하지 못하는 것:** 적중이 곧 침해라는 뜻은 아닙니다. 규칙마다 `falsepositives` 에 정상 원인이 적혀 있고, SSO 로그인이나 자동화 도구처럼 흔한 업무가 같은 흔적을 남깁니다[7][8]. 적중이 없다고 사건이 없었다는 뜻도 아닙니다. 필드 이름 불일치, 대소문자, 로그 원천 부재, 벤더 탐지 라이선스 부재 가운데 하나만 있어도 0건이 나옵니다[6][9][20].

보고서에는 "규칙 ○○(SigmaHQ, status test)의 조건에 맞는 CloudTrail 레코드가 2026-03-02T01:14:09Z 에 1건 있었고, 호출 주체는 IAM 사용자 alice 였다" 처럼 규칙 이름·상태·원천·레코드 내용을 적습니다(시각과 이름은 만든 예시). 적중이 없었다면 돌린 규칙 묶음, 대상 기간, 원천의 보관 상태를 함께 적습니다. 문장을 쓰는 방식은 [클라우드 포렌식 보고서](../reporting/forensic-report.md)를 봅니다. 로깅을 끈 흔적을 규칙으로 찾은 경우의 흐름은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)에서 이어집니다.

## 참고 문헌

1. SigmaHQ, Sigma Rules Specification, Version 2.1.0 (2025-08-02). https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-rules-specification.md
2. SigmaHQ, Sigma Taxonomy Appendix, Version 2.1.0. https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-appendix-taxonomy.md
3. SigmaHQ, Sigma Modifiers Appendix, Version 2.1.0. https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-appendix-modifiers.md
4. SigmaHQ, Sigma Correlation Rules Specification, Version 2.1.0. https://github.com/SigmaHQ/sigma-specification/blob/main/specification/sigma-correlation-rules-specification.md
5. SigmaHQ, sigma-cli README. https://github.com/SigmaHQ/sigma-cli/blob/main/README.md
6. AttackIQ, pySigma-backend-kusto README. https://github.com/AttackIQ/pySigma-backend-kusto/blob/main/README.md
7. SigmaHQ, sigma 저장소 클라우드 규칙(`rules/cloud/aws/`, `rules/cloud/azure/`, `rules/cloud/gcp/`, `rules/cloud/m365/`). https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/
8. SigmaHQ, sigma 저장소 Okta·GitHub·Bitbucket 규칙. https://github.com/SigmaHQ/sigma/blob/master/rules/identity/okta/ , https://github.com/SigmaHQ/sigma/blob/master/rules/application/github/audit/ , https://github.com/SigmaHQ/sigma/blob/master/rules/application/bitbucket/audit/
9. Microsoft Learn, Kusto Query Language overview (2026-07-23). https://learn.microsoft.com/en-us/kusto/query/?view=microsoft-fabric
10. Microsoft Learn, Overview - Advanced hunting (2026-08-07). https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-overview
11. Microsoft Learn, Advanced hunting schema tables (2026-07-27). https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-schema-tables
12. Microsoft Learn, CloudAppEvents table in the advanced hunting schema (2025-05-15). https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-cloudappevents-table
13. Microsoft Learn, View activity logs for Azure RBAC changes (2022-08-21). https://learn.microsoft.com/en-us/azure/role-based-access-control/change-history-report
14. Microsoft Learn, Log data ingestion time in Azure Monitor (2026-07-31). https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-ingestion-time
15. Google Cloud, Logging query language (2026-09-25). https://cloud.google.com/logging/docs/view/logging-query-language
16. AWS, Working with AWS CloudTrail Lake (2026년 9월 사본). https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake.html
17. AWS, Working with CloudTrail event history (2026년 9월 사본). https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
18. Okta Developer, System Log query. https://developer.okta.com/docs/reference/system-log-query/
19. Okta Help Center, System Log filters. https://help.okta.com/en-us/content/topics/reports/syslog-filters.htm
20. Microsoft Learn, What are risk detections? (2026-04-22). https://learn.microsoft.com/en-us/entra/id-protection/concept-identity-protection-risks
21. Microsoft Learn, SigninLogs table reference (2026-08-27). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
22. Google Cloud, Understanding audit logs (2026-09-25). https://cloud.google.com/logging/docs/audit/understanding-audit-logs
23. Google for Developers, Reports API: activities.list (2026-09-09). https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
24. Invictus Incident Response, ALFA (Automated Audit Log Forensic Analysis for Google Workspace) README 와 `alfa/config/config.yml`. https://github.com/invictus-ir/ALFA/blob/main/README.md , https://github.com/invictus-ir/ALFA/blob/main/alfa/config/config.yml
25. Eoghan Casey, "SaaS Forensics & Response — Forensic Preservation, Recovery, and Analysis of SaaS Data", DFRWS USA 2023 발표. https://dfrws.org/presentation/saas-forensics-and-response/
