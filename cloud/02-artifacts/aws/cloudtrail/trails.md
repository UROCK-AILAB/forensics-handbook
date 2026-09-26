---
title: "트레일과 이벤트 기록"
parent: "CloudTrail"
grand_parent: "아티팩트 · AWS"
nav_order: 380
---

# 트레일과 이벤트 기록 (Trails·Event History·Lake)

CloudTrail 기록은 이벤트 기록·트레일·Lake 이벤트 데이터 저장소 가운데 어디에 있느냐에 따라 보관 기간과 담기는 이벤트가 다르고, 트레일로 S3 에 쌓인 로그 파일은 다이제스트 파일로 전달 뒤에 바뀌거나 지워졌는지 확인할 수 있습니다[1][4][12].

## 무엇을 기록하나 · 왜 생기나

CloudTrail 은 계정에 기본으로 켜져 있어서 따로 설정하지 않아도 이벤트 기록 (Event history) 을 볼 수 있습니다[1]. 이벤트 기록은 리전마다 최근 90일의 관리 이벤트를 보여 주고, 내용을 고칠 수 없으며, 보는 데 CloudTrail 요금이 들지 않습니다[1]. 90일을 넘는 기록이 필요하면 트레일 (Trail) 을 만들어 S3 버킷에 로그 파일로 쌓거나, CloudTrail Lake 의 이벤트 데이터 저장소 (Event data store) 를 만들어야 합니다[1][4]. 이벤트 기록은 계정에 있는 트레일·이벤트 데이터 저장소와 따로 움직이므로 트레일을 바꾸거나 멈춰도 이벤트 기록은 그대로 남습니다[1][4].

조사에서는 세 곳을 모두 확인합니다. 이벤트 기록은 설정과 상관없이 90일 안의 관리 이벤트를 보여 주고, 그보다 오래된 기록과 데이터 이벤트는 사고 전에 만들어 둔 트레일이나 Lake 이벤트 데이터 저장소에만 있습니다. 트레일이 있었다면 그 이벤트를 나중에 이벤트 데이터 저장소로 복사해 올 수 있습니다[13]. 어떤 이벤트가 어느 곳에 기본으로 기록되는지는 [관리 이벤트와 데이터 이벤트](./event-types.md)에서, 레코드 한 건의 필드는 [레코드 구조](./record-structure.md)에서 다룹니다.

## 위치와 버전별 차이

보관 기간과 요금은 2026년 9월 문서 기준입니다.

| 저장 위치 | 보관 | 담기는 이벤트 | 꺼내는 방법 |
|---|---|---|---|
| 이벤트 기록 | 리전마다 최근 90일[1] | 관리 이벤트만, 데이터·Insights·네트워크 활동 이벤트는 없음[1] | 콘솔 Event history, `aws cloudtrail lookup-events`, `LookupEvents` API[1] |
| 트레일 → S3 | 버킷에 두는 동안 계속, S3 수명 주기 규칙으로 보관·삭제[4] | 트레일에 설정한 이벤트 | S3 에서 `.json.gz` 파일을 받음[5] |
| 트레일 → CloudWatch Logs | 로그 그룹의 보관 설정대로 | 트레일과 같되 256KB 를 넘는 이벤트는 빠짐[10] | CloudWatch Logs 조회 |
| Lake 이벤트 데이터 저장소 | 1년 연장형: 기본 366일·최대 3,653일, 7년형: 2,557일[13][15] | 고급 이벤트 선택기로 고른 이벤트[13] | SQL 쿼리(Trino `SELECT`)[13] |

### 이벤트 기록

이벤트 기록은 한 번에 한 계정·한 리전만 검색하고, 속성 필터 하나와 시간 범위만 걸 수 있으며, 조직 전체를 모아 보는 기능이 없습니다[1]. 콘솔에서 내려받으면 파일 하나에 최대 200,000건이 들어가고, 넘으면 파일을 더 받습니다[1]. KMS 나 RDS Data API 이벤트를 트레일에서 뺐더라도 그 설정은 이벤트 기록에 적용되지 않습니다[1]. AWS 서비스가 새 이벤트를 추가하면 그 이벤트의 90일치 기록이 다 차기까지 90일이 걸립니다[1].

`LookupEvents` API 로 찾을 수 있는 속성은 AWS access key, Event ID, Event name, Event source, Read only, Resource name, Resource type, User name 이고, `LookupAttributes` 에는 한 번에 하나만 넣습니다[2]. 한 번에 최대 50건을 돌려주고 나머지는 `NextToken` 으로 이어 받으며, 계정·리전마다 초당 2회를 넘으면 스로틀링 오류가 납니다[2]. 응답의 `Events` 는 최근 이벤트가 먼저 오고, 항목마다 `EventTime`(숫자)·`EventName`·`Username`·`Resources` 같은 요약 칸과 함께 원래 레코드 JSON 을 문자열로 담은 `CloudTrailEvent` 가 들어 있습니다[2][16].

### 트레일

콘솔로 만든 트레일은 모두 다중 리전 트레일이라서 켜져 있는 모든 리전의 이벤트를 기록합니다[3]. 단일 리전 트레일은 AWS CLI 나 API 로만 만들 수 있고, 그 방법으로 트레일을 만들 때는 단일 리전이 기본값입니다[3]. AWS Organizations 의 관리 계정이나 위임된 관리자 계정은 조직의 모든 계정 이벤트를 모으는 조직 트레일을 만들 수 있고, 멤버 계정은 그 트레일을 볼 수만 있으며 기본으로 버킷의 로그 파일에 접근하지 못합니다[3]. 따라서 멤버 계정을 조사할 때는 조직 관리 계정 쪽 버킷도 확인합니다.

콘솔로 만든 트레일은 로그 파일과 다이제스트 파일을 기본으로 KMS 키로 암호화하고, 이것을 끄면 S3 서버 측 암호화 (SSE) 를 씁니다[4]. 버킷에 쓸 수 없게 설정이 틀어지면 CloudTrail 은 30일 동안 다시 전달을 시도합니다[4][5].

로그 파일은 S3 에 다음 경로로 쌓입니다[5].

```text
버킷/접두사/AWSLogs/계정ID/CloudTrail/리전/YYYY/MM/DD/파일이름.json.gz
버킷/접두사/AWSLogs/조직ID/계정ID/CloudTrail/리전/YYYY/MM/DD/파일이름.json.gz   (조직 트레일)
```

`CloudTrail` 자리에는 이벤트 종류에 따라 다른 문자열이 옵니다. 관리·데이터 이벤트는 `CloudTrail`, Insights 이벤트는 `CloudTrail-Insight`, 네트워크 활동 이벤트는 `CloudTrail-NetworkActivity`, 데이터 이벤트 집계는 `CloudTrail-Aggregated` 입니다[5]. 접두사는 트레일을 만들 때 고른 경우에만 있습니다[5].

파일 이름은 `AccountID_CloudTrail_RegionName_YYYYMMDDTHHmmZ_UniqueString.json.gz` 꼴입니다[6]. 시각 부분은 파일을 전달한 시각을 UTC 로 분까지 적은 것이고, 16자 `UniqueString` 은 덮어쓰기를 막으려는 값이라 뜻이 없습니다[6]. 예를 들면 `123456789012_CloudTrail_ap-northeast-2_20260901T0215Z_EXAMPLE0123456AB.json.gz` 이고, 만든 예시입니다.

트레일이 CloudWatch Logs 로도 보내면 로그 스트림 이름은 `account_ID_CloudTrail_trail_region` 꼴이고, 양이 많아 스트림이 여럿이면 끝에 `_number` 가 붙습니다[9]. 다중 리전 트레일은 모든 리전의 이벤트를 로그 그룹 하나로 보냅니다[4]. CloudWatch Logs 쪽 보관과 조회는 [CloudWatch Logs](../cloudwatch-logs.md)에서 다룹니다.

### 어느 리전에 남나

CloudFront·IAM·STS 같은 글로벌 서비스의 이벤트는 2021년 11월 22일부터 `us-east-1` 에 기록됩니다[7]. 그래서 `us-east-1` 밖에 만든 단일 리전 트레일은 이 이벤트를 받지 못하고, 단일 리전 트레일은 `IncludeGlobalServiceEvents` 가 참이어도 `us-east-1` 에 있을 때만 글로벌 서비스 이벤트를 받습니다[7]. 일부 글로벌 서비스 이벤트는 `us-east-2` 나 `us-west-2` 에 기록됩니다[7]. STS 리전 엔드포인트로 호출하면 그 리전의 트레일만 그 STS 이벤트를 받습니다[7].

콘솔 로그인 (`ConsoleLogin`) 이 기록되는 리전은 로그인 방식에 따라 다릅니다[8]. 루트 사용자는 `us-east-1`·`us-east-2`·`us-west-2` 가운데 하나에 남습니다. IAM 사용자가 글로벌 엔드포인트로 로그인하면 브라우저에 계정 별칭 쿠키가 있을 때 `us-east-2`·`eu-north-1`·`ap-southeast-2` 가운데 하나에, 없을 때 `us-east-1` 에 남습니다. 리전 엔드포인트로 로그인하면 그 리전에 남습니다[8]. 이벤트 기록은 리전마다 따로 검색하므로 로그인을 찾을 때는 이 리전들을 모두 봅니다.

### Lake

Lake 는 JSON 이벤트를 Apache ORC 형식으로 바꿔 저장하고, 이벤트 데이터 저장소는 내용을 고칠 수 없는 이벤트 모음입니다[13]. 보관 여부는 `eventTime` 으로 판단해서 보관 기간보다 `eventTime` 이 오래된 이벤트를 지웁니다[14]. 이벤트 데이터 저장소는 기본으로 삭제 보호 (Termination protection) 가 켜져 있습니다[14]. 트레일의 이벤트를 이벤트 데이터 저장소로 복사해 그 시점의 스냅숏을 만들 수 있고, 쿼리 결과는 7일 동안 볼 수 있으며, Athena 로 쿼리하도록 연동할 수도 있습니다[13]. Lake 는 2026년 5월 31일부터 새 고객을 받지 않고 기존 고객은 그대로 씁니다[13].

## 구조 — 다이제스트 파일

로그 파일 무결성 검증 (Log file integrity validation) 을 켜면 CloudTrail 은 한 시간마다 그 시간에 전달한 로그 파일 목록과 파일별 해시를 담은 다이제스트 파일 (Digest file) 을 같은 버킷의 별도 폴더에 전달합니다[11]. 해시는 SHA-256, 서명은 SHA-256 with RSA 이고, 서명 키 쌍은 리전마다 다릅니다[11].

```text
버킷/접두사/AWSLogs/계정ID/CloudTrail-Digest/리전/YYYY/MM/DD/계정ID_CloudTrail-Digest_리전_트레일이름_리전_끝시각.json.gz
```

객체 키에 나오는 앞의 두 리전(폴더 이름과 파일 이름의 첫 리전)은 다이제스트를 전달한 리전이고, 트레일 이름 뒤의 리전은 트레일을 만든 홈 리전입니다[12]. 다중 리전 트레일은 두 값이 다를 수 있습니다[12]. 조직 트레일은 `AWSLogs/` 뒤에 조직 ID 가 들어가고, 처리 지연 때문에 빠졌던 로그 파일을 나중에 담는 백필 (Backfill) 다이제스트는 이름 끝에 `_backfill` 이 붙습니다[12].

다음은 다이제스트 파일의 모양을 명세대로 만든 예시이고, 계정·버킷·해시 값은 지어낸 값입니다.

```json
{
  "awsAccountId": "123456789012",
  "digestStartTime": "2026-09-01T02:01:31Z",
  "digestEndTime": "2026-09-01T03:01:31Z",
  "digestS3Bucket": "amzn-s3-demo-bucket",
  "digestS3Object": "AWSLogs/123456789012/CloudTrail-Digest/ap-northeast-2/2026/09/01/123456789012_CloudTrail-Digest_ap-northeast-2_example-trail_ap-northeast-2_20260901T030131Z.json.gz",
  "digestPublicKeyFingerprint": "0123456789abcdef0123456789abcdef",
  "digestSignatureAlgorithm": "SHA256withRSA",
  "newestEventTime": "2026-09-01T02:14:05Z",
  "oldestEventTime": "2026-09-01T02:09:40Z",
  "previousDigestS3Bucket": "amzn-s3-demo-bucket",
  "previousDigestS3Object": "AWSLogs/123456789012/CloudTrail-Digest/ap-northeast-2/2026/09/01/123456789012_CloudTrail-Digest_ap-northeast-2_example-trail_ap-northeast-2_20260901T020131Z.json.gz",
  "previousDigestHashValue": "(이전 다이제스트의 SHA-256, 16진수)",
  "previousDigestHashAlgorithm": "SHA-256",
  "previousDigestSignature": "(이전 다이제스트의 서명, 16진수)",
  "logFiles": [
    {
      "s3Bucket": "amzn-s3-demo-bucket",
      "s3Object": "AWSLogs/123456789012/CloudTrail/ap-northeast-2/2026/09/01/123456789012_CloudTrail_ap-northeast-2_20260901T0215Z_EXAMPLE0123456AB.json.gz",
      "hashValue": "(압축을 푼 로그 파일의 SHA-256, 16진수)",
      "hashAlgorithm": "SHA-256",
      "newestEventTime": "2026-09-01T02:14:05Z",
      "oldestEventTime": "2026-09-01T02:09:40Z"
    }
  ]
}
```

| 필드 | 뜻 |
|---|---|
| `digestStartTime`·`digestEndTime` | 이 다이제스트가 다루는 구간(UTC). 이벤트 시각이 아니라 로그 파일을 전달한 시각 기준[12] |
| `newestEventTime`·`oldestEventTime` | 목록의 로그 파일 안 이벤트 가운데 가장 늦은·이른 시각(UTC)[12] |
| `logFiles[].hashValue` | 압축을 푼 로그 파일 내용의 16진수 해시[12] |
| `previousDigest*` | 바로 앞 다이제스트의 위치·해시·서명. 해시는 압축을 푼 앞 다이제스트 내용으로 계산[12] |
| `digestPublicKeyFingerprint` | 이 다이제스트를 서명한 키의 공개키 지문. `ListPublicKeys` API 나 AWS CLI `list-public-keys` 로 받은 공개키 가운데 지문이 같은 것으로 검증[12] |

현재 다이제스트의 서명은 파일 안이 아니라 S3 객체 메타데이터 `x-amz-meta-signature` 에 있고, 알고리즘은 `x-amz-meta-signature-algorithm` 에 있습니다[12]. 백필 다이제스트에는 생성 시각을 적은 `x-amz-meta-backfill-generation-timestamp` 가 더 붙습니다[12].

다이제스트마다 앞 다이제스트를 가리키므로 다이제스트끼리 사슬이 되고, 이 사슬로 다이제스트 파일이 지워졌는지도 알아낼 수 있습니다[12]. 검증을 처음 켜거나, 껐다 다시 켜거나, 로깅을 멈췄다 다시 시작하면 `previousDigest*` 다섯 필드가 `null` 인 시작 다이제스트가 생깁니다[12]. 그 시간에 활동이 없어도 `logFiles` 가 빈 배열이고 `newestEventTime`·`oldestEventTime` 이 `null` 인 다이제스트가 전달됩니다[12]. 로깅을 멈추거나 트레일을 지우면 `StopLogging` 이벤트까지를 담은 마지막 다이제스트가 전달됩니다[12].

## 증거로서 의미

**증명하는 것.** 다이제스트로 검증한 로그 파일은 CloudTrail 이 전달한 뒤 바뀌지 않았다는 것을 보여 주고, 사슬이 이어진 구간에서는 어느 시간에 로그 파일이 한 건도 전달되지 않았다는 것까지 주장할 수 있습니다[11][12]. 이벤트 기록에서 `StopLogging`·`UpdateTrail`·`DeleteTrail` 을 찾으면 누가 언제 트레일을 멈추거나 바꾸거나 지웠는지 알 수 있고, 이벤트 기록은 트레일과 따로 움직여서 트레일을 멈춘 뒤에도 90일 안의 관리 이벤트가 남습니다[1][17].

**증명하지 못하는 것.** 트레일이 없던 계정에는 90일이 지난 관리 이벤트와 모든 데이터 이벤트가 어디에도 없으므로, 이 경우 "기록 없음" 은 "행위 없음" 이 아닙니다[1]. 다이제스트는 검증을 켜기 전 기간이나 검증·로깅이 꺼져 있던 동안에는 만들어지지 않아서 그 구간의 파일은 무결성을 보여 줄 수 없습니다[12]. 다이제스트는 CloudTrail 이 전달한 파일이 그대로인지를 보여 줄 뿐, 트레일 설정에서 빠진 이벤트가 있었는지는 알려 주지 않습니다. 보고서에는 "이 구간의 로그 파일은 다이제스트와 해시가 일치한다" 처럼 검증한 범위만 씁니다.

## 시각 해석

로그 파일 이름의 시각은 전달 시각(UTC, 분 단위)이고, 그 시각에 전달한 파일에는 그 전 어느 때의 레코드든 들어갈 수 있습니다[6]. CloudTrail 은 로그 파일을 한 시간에 여러 번, 대략 5분마다 내보내고 API 호출 뒤 전달까지 평균 5분쯤 걸리지만 이 시간은 보장하지 않습니다[4][5]. S3 문서의 로깅 비교표에는 데이터 이벤트는 5분마다, 관리 이벤트는 15분마다 전달된다고 적혀 있어 CloudTrail 문서와 값이 다릅니다[18]. 따라서 폴더 날짜나 파일 이름 시각으로 이벤트 시각을 짐작하지 말고, 자정 앞뒤 사건은 다음 날 폴더까지 함께 받습니다. 이벤트가 실제로 일어난 시각은 레코드의 `eventTime` 으로 읽고, 읽는 법은 [레코드 구조](./record-structure.md)에 있습니다.

다이제스트의 `digestStartTime`·`digestEndTime` 은 로그 파일 전달 시각 기준이고, 다이제스트가 늦게 전달되면 `oldestEventTime` 이 `digestStartTime` 보다 이릅니다[12]. `LookupEvents` 응답의 `EventTime` 은 숫자로 오므로 원래 레코드인 `CloudTrailEvent` 안의 `eventTime` 과 맞춰 봅니다[2].

## 함정과 한계

- **리전.** 이벤트 기록은 리전마다 따로라서 한 리전만 보면 다른 리전의 활동과 `us-east-1` 에 남는 글로벌 서비스·로그인 이벤트를 놓칩니다[1][7][8]. 반대로 이벤트 기록은 글로벌 서비스 이벤트를 실제로 일어난 리전에 보여 주므로 트레일 쪽 리전과 다를 수 있습니다[7].
- **이벤트 기록만 모은 자료.** Invictus-AWS 는 CloudTrail 을 모을 때 트레일 버킷이 아니라 `lookup_events` 로 이벤트 기록을 페이지마다 받아 `eventID` 이름의 JSON 파일로 저장하고, 트레일 버킷을 쓰는 코드는 주석으로 막혀 있습니다[16]. 이런 도구로 모은 자료는 90일 안의 관리 이벤트뿐이므로 데이터 이벤트가 없다고 결론 내리기 전에 트레일 버킷을 따로 확인합니다.
- **CloudWatch Logs 사본.** 256KB 를 넘는 이벤트는 CloudWatch Logs 와 EventBridge 로 보내지 않으므로 CloudWatch Logs 만 보면 큰 이벤트가 빠집니다[10]. 원본은 S3 의 로그 파일에서 확인합니다.
- **저장 위치별 필드 차이.** `eventContext` 는 리소스 태그·IAM 글로벌 조건 키를 담도록 설정한 Lake 이벤트 데이터 저장소에만 있고, 이벤트 기록·`lookup-events`·EventBridge·트레일 사본에는 없습니다[19]. 같은 이벤트의 사본끼리 필드가 다르면 먼저 이 차이인지 봅니다.
- **옮긴 로그의 검증.** AWS CLI 는 CloudTrail 이 전달한 자리에 있는 파일만 검증하고, 다른 곳으로 옮긴 로그는 따로 만든 도구로 검증합니다[11]. 버킷 정책이 틀어졌거나 서비스 장애가 있으면 다이제스트가 빠지거나 순서가 뒤바뀌어 사슬이 잠깐 끊긴 것처럼 보일 수 있으므로, 트레일 상태의 `LatestDigestDeliveryError` 를 함께 봅니다[12].
- **다이제스트도 같은 버킷에 있음.** 다이제스트는 로그 파일과 같은 버킷의 별도 폴더에 쌓이고, 다이제스트를 지키는 데 S3 MFA Delete 를 쓸 수 있습니다[11]. 사슬이 끊긴 자리는 다음 다이제스트의 `previousDigestS3Object` 가 가리키는 파일이 없는 것으로 드러나므로 빠진 구간을 기록해 둡니다[12].

## 직접 분석해 보기

**이벤트 기록 응답 펼치기.** `aws cloudtrail lookup-events` 나 `LookupEvents` API 의 응답을 파일로 저장했다면, `CloudTrailEvent` 문자열을 다시 JSON 으로 풀어 레코드를 한 줄씩 봅니다[2]. 파일 이름은 만든 예시입니다.

```sh
jq -c '.Events[].CloudTrailEvent | fromjson
       | {eventTime, eventID, eventSource, eventName, arn: .userIdentity.arn, ip: .sourceIPAddress}' \
  lookup-ap-northeast-2.json | sort
```

**다이제스트와 로그 파일 해시 맞추기.** 다이제스트에 적힌 해시는 압축을 푼 내용으로 계산한 것이므로 로그 파일도 풀어서 해시를 냅니다[12]. 파일 이름은 만든 예시입니다.

```sh
# 다이제스트가 목록에 올린 로그 파일과 해시
gzip -dc 123456789012_CloudTrail-Digest_ap-northeast-2_example-trail_ap-northeast-2_20260901T030131Z.json.gz \
  | jq -r '.logFiles[] | "\(.hashValue)  \(.s3Object)"'

# 받은 로그 파일의 해시(압축을 푼 내용)
gzip -dc 123456789012_CloudTrail_ap-northeast-2_20260901T0215Z_EXAMPLE0123456AB.json.gz | sha256sum

# 사슬: 앞 다이제스트를 풀어 낸 해시가 다음 다이제스트의 previousDigestHashValue 와 같아야 함
gzip -dc 123456789012_CloudTrail-Digest_ap-northeast-2_example-trail_ap-northeast-2_20260901T020131Z.json.gz | sha256sum
```

해시가 맞아도 다이제스트 자체가 진짜인지는 서명을 검증해야 알 수 있습니다. 서명 검증은 AWS CLI 로 하고, 다른 곳으로 옮긴 파일이면 따로 만든 도구로 `x-amz-meta-signature` 값과 같은 리전의 공개키를 써서 검증합니다[11][12]. 버킷에 쌓인 로그 전체를 SQL 로 조회하는 방법과 jq 로 로그 파일 하나를 읽는 방법은 [레코드 구조](./record-structure.md)에 있습니다.

## 교차 검증

- 트레일이 당시 무엇을 기록하도록 설정되어 있었는지는 [관리 이벤트와 데이터 이벤트](./event-types.md)의 방법으로 확인합니다.
- 데이터 이벤트를 켜지 않은 버킷의 객체 접근은 [S3 접근 기록](../s3-access-logs.md)에서 찾습니다.
- 이벤트 기록에서 찾은 `StopLogging`·`DeleteTrail` 호출 주체는 [IAM 사용자·역할·액세스 키](../iam.md)에서 키·역할의 주인을 맞춰 봅니다.
- 보관 기간이 로그마다 다른 이유와 수집 순서는 [보관 기간과 라이선스](../../../01-foundations/logging/retention-licensing.md)와 [AWS·Azure·GCP 수집](../../../03-techniques/acquisition/iaas-collection.md)을 봅니다.
- 전달 시각과 `eventTime` 을 다른 로그와 한 줄로 세우는 방법은 [클라우드 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

## 실습

시험용 AWS 계정에서 다음 질문을 풀어 봅니다.

1. 콘솔로 트레일을 하나 만들고 검증을 켠 뒤, 첫 다이제스트의 `previousDigest*` 필드 값은 무엇인가?
2. 트레일 로깅을 멈췄다 다시 켜면 이벤트 기록에 어떤 `eventName` 이 남고, 다이제스트 사슬은 어떻게 되는가?
3. 활동이 없던 시간의 다이제스트에서 `logFiles` 와 `newestEventTime` 은 어떻게 적히는가?
4. IAM 사용자로 콘솔에 로그인한 뒤 `ConsoleLogin` 이벤트는 어느 리전의 이벤트 기록에서 보이는가?
5. 로그 파일 이름의 시각과 그 안 레코드의 `eventTime` 은 얼마나 차이 나는가?

## 참고 문헌

1. AWS, "Working with CloudTrail event history", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
2. AWS, "LookupEvents", AWS CloudTrail API Reference. https://docs.aws.amazon.com/awscloudtrail/latest/APIReference/API_LookupEvents.html
3. AWS, "Working with CloudTrail trails", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-trails.html
4. AWS, "How CloudTrail works", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/how-cloudtrail-works.html
5. AWS, "Getting and viewing your CloudTrail log files", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/get-and-view-cloudtrail-log-files.html
6. AWS, "CloudTrail log file examples", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-examples.html
7. AWS, "CloudTrail concepts", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html
8. AWS, "AWS Management Console sign-in events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-aws-console-sign-in-events.html
9. AWS, "CloudWatch log group and log stream naming for CloudTrail", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudwatch-log-group-log-stream-naming-for-cloudtrail.html
10. AWS, "Sending events to CloudWatch Logs", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/send-cloudtrail-events-to-cloudwatch-logs.html
11. AWS, "Validating CloudTrail log file integrity", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html
12. AWS, "CloudTrail digest file structure", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-digest-file-structure.html
13. AWS, "Working with AWS CloudTrail Lake", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake.html
14. AWS, "CloudTrail Lake concepts and terminology", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake-concepts.html
15. AWS, "Managing CloudTrail Lake costs", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake-manage-costs.html
16. invictus-ir, Invictus-AWS, source/main/logs.py. https://github.com/invictus-ir/Invictus-AWS/blob/main/source/main/logs.py
17. SigmaHQ, aws_cloudtrail_disable_logging.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_disable_logging.yml
18. AWS, "Logging options for Amazon S3", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/logging-with-S3.html
19. AWS, "CloudTrail record contents for management, data, and network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
