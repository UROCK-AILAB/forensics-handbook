---
title: "S3 접근 기록"
parent: "아티팩트 · AWS"
nav_order: 400
---

# S3 접근 기록 (S3 Server Access Logs)

S3 서버 접근 로그 (server access logs) 는 버킷에 들어온 요청을 한 줄에 하나씩 적은 텍스트 기록이고, CloudTrail 에 남지 않는 인증 실패 요청과 수명 주기 작업까지 담지만 버킷마다 따로 켜야 하고 전달은 최선 노력 (best-effort) 입니다[2][3][4].

## 무엇을 기록하나 · 왜 생기나

S3 는 버킷에 들어온 요청의 기록을 모아 두었다가 주기적으로 정해 둔 곳에 전달합니다[2]. 레코드 하나가 요청 하나이고, 누가(Requester) 어디서(Remote IP) 어떤 작업(Operation)으로 어느 객체(Key)를 요청했으며 응답 코드와 보낸 바이트가 얼마였는지 적힙니다[1].

S3 는 서버 접근 로그를 기본으로 모으지 않습니다[4]. 원본 버킷 (source bucket) 에 로깅을 켜고 로그를 받을 대상 버킷 (destination bucket, target bucket) 을 지정해야 S3 가 접근 로그를 전달합니다[4]. 그래서 로깅을 켜기 전의 요청은 서버 접근 로그에 없습니다. 로그 객체는 S3 로그 전달 계정이 쓰고 소유하며, 대상 버킷의 버킷 정책으로 로깅 서비스 주체 `logging.s3.amazonaws.com` 에 쓰기 권한을 줍니다[4].

AWS 는 버킷·객체 작업 기록에 CloudTrail 을 권하지만, 두 기록이 담는 범위가 달라서 조사에서는 둘을 함께 봅니다[3]. S3 요청이 CloudTrail 에서 관리 이벤트와 데이터 이벤트로 어떻게 나뉘는지는 [관리 이벤트와 데이터 이벤트](./cloudtrail/event-types.md)에 있습니다.

| 기록되는 것 | CloudTrail | 서버 접근 로그 |
|---|---|---|
| 객체 작업·버킷 작업(S3 API) | 예 | 예 |
| 일괄 삭제(batch delete)에 든 키 | 예 | 예 |
| 수명 주기 전환·만료·복원 | 아니오 | 예 |
| 인증 실패(잘못된 자격 증명) | 아니오 | 예 |
| Object Size·Total Time·Turn-Around Time·Referer 필드 | 예 | 예 |
| Object Lock 매개변수·S3 Select 속성 필드 | 예 | 아니오 |
| 접두사로 일부 객체만 켜기 | 예 | 아니오 |
| 로그 파일 무결성 검증(서명·해시) | 예 | 아니오 |

2026년 9월 문서 기준이고, 표의 "인증 실패" 는 제시한 자격 증명이 올바르지 않은 요청을 말합니다[3]. CloudTrail 은 이런 요청과 301 리다이렉트로 실패한 요청을 남기지 않지만, 권한이 없어 거부된 요청(`AccessDenied`)과 익명 요청은 남깁니다[3].

## 위치와 버전별 차이

### 전달 대상

서버 접근 로그는 두 곳으로 보낼 수 있고, 둘을 함께 써도 됩니다[2]. 2026년 9월 문서 기준입니다.

| 항목 | S3 범용 버킷 | CloudWatch Logs |
|---|---|---|
| 형식 | 공백으로 나눈 텍스트 | 구조화된 JSON(로그 그룹), S3 로 다시 보내면 JSON·Parquet |
| 받는 곳 | 원본 버킷과 같은 리전·같은 계정의 버킷만 | 로그 그룹, S3, Data Firehose(교차 계정·교차 리전 가능) |
| 암호화 | SSE-S3 만 | AWS KMS 가능 |
| 설정 | `PutBucketLogging` API 또는 콘솔 | CloudWatch Logs API 또는 S3 콘솔 |
| 조회 | Amazon Athena | CloudWatch Logs Insights, S3 Tables 사본은 Athena·Spark |
| 요금 | 전달 무료, 저장 요금만 | CloudWatch vended logs 수집 요금 |
| 전달 지연 | 몇 시간 안 | 몇 시간 안 |

이 쪽은 S3 버킷으로 받은 텍스트 형식을 다룹니다. CloudWatch Logs 로 받은 JSON 형식의 필드 이름은 검체의 로그 그룹에서 레코드를 하나 열어 확인하고, 로그 그룹 자체는 [CloudWatch Logs](./cloudwatch-logs.md)에서 다룹니다.

대상 버킷에는 조건이 붙습니다. S3 Object Lock 을 켠 버킷이나 기본 보존 기간을 설정한 버킷은 대상이 될 수 없고, 요청자 지불 (Requester Pays) 을 켠 버킷도 안 됩니다[4]. 대상 버킷이 SSE-KMS 기본 암호화를 쓰면 접근할 수 없는 키로 암호화된 로그 객체가 전달될 수 있습니다[4]. 원본 버킷 자신을 대상으로 삼을 수는 있지만 로그가 끝없이 늘어나는 고리가 생깁니다[4].

### 로그 객체 이름

대상 버킷의 로그 객체 키는 설정에 따라 두 모양 가운데 하나입니다[4].

```text
날짜로 나누지 않음:
[DestinationPrefix][YYYY]-[MM]-[DD]-[hh]-[mm]-[ss]-[UniqueString]

날짜로 나눔:
[DestinationPrefix][SourceAccountId]/[SourceRegion]/[SourceBucket]/[YYYY]/[MM]/[DD]/[YYYY]-[MM]-[DD]-[hh]-[mm]-[ss]-[UniqueString]
```

날짜로 나누는 형식은 날짜 기준을 S3 이벤트 시각(event time)과 로그 파일 전달 시각(log file delivery time) 가운데 하나로 고릅니다[4]. 접두사 끝에 `/` 를 붙이지 않으면 `logs2013-11-01-21-32-16-E568B2907131C0C0` 처럼 접두사와 날짜가 붙어 버립니다[4]. 여러 버킷의 로그를 한 대상 버킷에 모았다면, 날짜로 나누지 않는 형식에서는 객체 이름에 원본 버킷이 드러나지 않으므로 레코드 안의 Bucket 필드로 가려냅니다.

### 설정 확인하기

지금 버킷에 걸린 설정은 `GetBucketLogging` API 로 보고, 응답에 `LoggingEnabled` 가 없으면 S3 버킷으로 보내는 로깅이 꺼진 상태입니다[4][8]. 로깅 설정은 다음과 같은 `BucketLoggingStatus` 모양이고, 대상 버킷과 접두사, 키 형식이 들어갑니다(`PutBucketLogging` 요청 예시이고, 버킷 이름은 AWS 문서 예시 이름입니다)[4].

```xml
<BucketLoggingStatus xmlns="http://doc.s3.amazonaws.com/2006-03-01">
 <LoggingEnabled>
  <TargetBucket>amzn-s3-demo-destination-bucket</TargetBucket>
  <TargetPrefix>logs/</TargetPrefix>
  <TargetObjectKeyFormat>
   <PartitionedPrefix>
    <PartitionDateSource>EventTime</PartitionDateSource>
   </PartitionedPrefix>
  </TargetObjectKeyFormat>
 </LoggingEnabled>
</BucketLoggingStatus>
```

`GetBucketLogging` 은 지금 설정만 보여 줍니다. 사건 당시에 로깅이 켜져 있었는지는 CloudTrail 관리 이벤트에서 `eventSource` 가 `s3.amazonaws.com` 이고 `eventName` 이 `PutBucketLogging` 인 레코드를 찾아 봅니다[5][7]. 공개 도구 Invictus-AWS 는 계정의 버킷마다 `get_bucket_logging` 을 불러 `LoggingEnabled` 가 있는 버킷의 `TargetBucket` 과 `TargetPrefix` 를 모읍니다[8]. 여러 클라우드의 로그를 모으는 순서는 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md)에 있습니다.

## 구조

로그 파일은 줄바꿈으로 나눈 레코드의 연속이고, 레코드 하나는 요청 하나이며 필드는 공백으로 나눕니다[1]. 값을 모르거나 해당하지 않는 필드에는 `-` 가 들어갑니다[1]. Time 은 대괄호로 감싸고, Request-URI·Referer·User-Agent 는 큰따옴표로 감쌉니다[1].

아래는 필드 순서대로 풀어 본 만든 예시 레코드입니다. 역할 세션이 객체를 내려받은 요청이고, 계정 ID·정규 사용자 ID·요청 ID·호스트 ID·IP 는 모두 지어낸 값입니다.

```text
0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef amzn-s3-demo-bucket [14/Mar/2026:02:15:07 +0000] 203.0.113.10 arn:aws:sts::123456789012:assumed-role/ExampleRole/example-session 5F1A2B3C4D5E6F70 REST.GET.OBJECT reports/q1.xlsx "GET /amzn-s3-demo-bucket/reports/q1.xlsx HTTP/1.1" 200 - 48213 48213 95 12 "-" "curl/8.5.0" - EXAMPLEhostIdEXAMPLEhostIdEXAMPLE= SigV4 ECDHE-RSA-AES128-GCM-SHA256 AuthHeader s3.us-east-1.amazonaws.com TLSv1.2 - - -
```

| 순서 | 필드 | 만든 예시 값 | 뜻 |
|---|---|---|---|
| 1 | Bucket Owner | `0123…cdef` | 원본 버킷 소유자의 정규 사용자 ID (canonical user ID), AWS 계정 ID 의 다른 모양[1] |
| 2 | Bucket | `amzn-s3-demo-bucket` | 요청을 처리한 버킷 이름[1] |
| 3 | Time | `[14/Mar/2026:02:15:07 +0000]` | 요청을 받은 시각, UTC, `[%d/%b/%Y:%H:%M:%S %z]`[1] |
| 4 | Remote IP | `203.0.113.10` | 겉으로 보이는 요청자 IP[1] |
| 5 | Requester | `arn:aws:sts::…:assumed-role/…` | 요청자의 정규 사용자 ID, IAM 사용자면 사용자 이름과 계정, 역할을 넘겨받았으면 역할 세션 ARN, 인증 안 된 요청이면 `-`[1] |
| 6 | Request ID | `5F1A2B3C4D5E6F70` | S3 가 요청마다 만든 식별자[1] |
| 7 | Operation | `REST.GET.OBJECT` | 작업 이름(아래 설명)[1] |
| 8 | Key | `reports/q1.xlsx` | 객체 이름[1] |
| 9 | Request-URI | `"GET /… HTTP/1.1"` | HTTP 요청 줄[1] |
| 10 | HTTP status | `200` | 응답 코드[1] |
| 11 | Error Code | `-` | S3 오류 코드, 오류가 없으면 `-`[1] |
| 12 | Bytes Sent | `48213` | 보낸 응답 바이트(HTTP 부담 제외), 0 이면 `-`[1] |
| 13 | Object Size | `48213` | 대상 객체의 전체 크기[1] |
| 14 | Total Time | `95` | 요청을 받은 때부터 응답 마지막 바이트를 보낼 때까지(밀리초)[1] |
| 15 | Turn-Around Time | `12` | 요청 마지막 바이트를 받은 때부터 응답 첫 바이트를 보낼 때까지(밀리초)[1] |
| 16 | Referer | `"-"` | HTTP Referer 헤더[1] |
| 17 | User-Agent | `"curl/8.5.0"` | HTTP User-Agent 헤더[1] |
| 18 | Version Id | `-` | 요청의 버전 ID, `versionId` 를 받지 않는 작업이면 `-`[1] |
| 19 | Host Id | `EXAMPLE…=` | `x-amz-id-2`, 곧 S3 확장 요청 ID[1] |
| 20 | Signature Version | `SigV4` | `SigV2`·`SigV4`, 인증 안 된 요청이면 `-`[1] |
| 21 | Cipher Suite | `ECDHE-RSA-AES128-GCM-SHA256` | HTTPS 에서 협상한 TLS 암호 모음, HTTP 면 `-`[1] |
| 22 | Authentication Type | `AuthHeader` | `AuthHeader`(인증 헤더), `QueryString`(미리 서명된 URL), `-`(인증 안 됨)[1] |
| 23 | Host Header | `s3.us-east-1.amazonaws.com` | 접속한 S3 끝점[1] |
| 24 | TLS version | `TLSv1.2` | `TLSv1.1`·`TLSv1.2`·`TLSv1.3`, TLS 를 안 쓰면 `-`[1] |
| 25 | Access Point ARN | `-` | 요청이 거친 액세스 포인트 ARN[1] |
| 26 | aclRequired | `-` | 권한 판단에 ACL 이 필요했으면 `Yes`[1] |
| 27 | Source region | `-` | 요청이 나온 AWS 리전, AWS 밖 IP·PrivateLink·Direct Connect·BYOIP 나 수명 주기처럼 정책이 일으킨 작업이면 `-`[1] |

Operation 은 `SOAP.operation`, `REST.HTTP_method.resource_type`, `WEBSITE.HTTP_method.resource_type`, `BATCH.DELETE.OBJECT` 가운데 하나의 모양이고, 수명 주기와 로깅은 `S3.action.resource_type`, 체크섬 계산 작업은 `S3.COMPUTE.OBJECT.CHECKSUM` 으로 적힙니다[1]. 체크섬 계산 작업의 레코드에서는 Request ID 자리에 작업(job) ID 가 들어갑니다[1].

복사는 GET 과 PUT 이 함께 일어나는 작업이라 레코드가 두 줄 남습니다[1]. GET 쪽 레코드는 Operation 이 `REST.COPY.OBJECT_GET` 이고, Bucket·Bucket Owner·Key 가 복사해 온 원본 객체를 가리키며, Version Id 는 복사 원본으로 지정한 버전입니다[1]. 버킷 사이로 객체를 옮긴 흔적을 찾을 때 두 줄을 짝지어 읽습니다.

요청 URL 에 `x-` 로 시작하는 쿼리 문자열을 붙이면 S3 는 요청을 처리할 때 무시하지만 Request-URI 필드에는 그대로 남깁니다(REST 요청만)[1]. 레코드 형식은 줄 끝에 새 필드가 붙으며 늘어날 수 있어서, 파서는 뒤에 붙은 모르는 필드를 버리고 앞의 필드만 읽어야 합니다[1].

## 증거로서 의미

**증명하는 것.** 레코드 하나는 이 시각에 이 IP 에서 이 요청자가 이 서명 방식으로 이 객체에 이 작업을 요청했고, S3 가 이 응답 코드와 이 만큼의 바이트로 답했다는 사실을 보여 줍니다[1]. `REST.GET.OBJECT` 에 응답 코드 `200` 이고 Bytes Sent 가 Object Size 와 같다면 객체 전체를 응답으로 보낸 기록입니다. Authentication Type 이 `QueryString` 이면 미리 서명된 URL 로 들어온 요청이고, `-` 이면서 Requester 가 `-` 이면 인증 없이 들어온 요청입니다[1]. CloudTrail 에 남지 않는 인증 실패 요청이 여기에는 남아서, 잘못된 키로 여러 번 시도한 흔적을 볼 수 있습니다[3].

**증명하지 못하는 것.** 기록은 모든 요청을 빠짐없이 담는다고 보장하지 않으므로 "로그에 없다" 를 "요청이 없었다" 로 쓸 수 없습니다[2]. Requester 는 정규 사용자 ID·IAM 사용자·역할 세션 ARN 이라서 그 뒤의 사람이 누구인지는 CloudTrail 의 역할 넘겨받기 기록이나 [IAM 사용자·역할·액세스 키](./iam.md) 쪽 기록으로 이어 가야 합니다[1]. Remote IP 는 중간 프록시나 방화벽에 가려진 값일 수 있습니다[1]. 버킷을 알 수 없는 잘못된 요청은 어느 로그에도 남지 않고[1], 2019년 3월 20일 뒤에 문을 연 리전에서는 잘못된 리전으로 간 요청의 리다이렉트 오류가 남지 않습니다[2]. VPC 끝점 정책이 거부한 요청과 VPC 정책을 따지기 전에 실패한 요청도 요청자와 버킷 소유자에게 전달되지 않습니다[3]. 보낸 바이트는 S3 가 응답으로 내보낸 양이지, 받는 쪽 단말에 파일이 온전히 저장됐다는 뜻은 아닙니다.

보고서에는 "이 시간대 이 역할 세션으로 이 객체에 GET 요청이 있었고 S3 가 객체 크기만큼 응답했다는 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

Time 필드는 S3 가 요청을 받은 시각이고 UTC 입니다[1]. 형식은 `[06/Feb/2019:00:00:38 +0000]` 처럼 일/영어 약어 월/연:시:분:초 뒤에 `%z` 오프셋이 붙습니다[1]. 같은 요청의 CloudTrail `eventTime` 은 요청이 끝난 시각이라서[6], 두 기록을 맞출 때는 Total Time 만큼 차이가 날 수 있다고 보고 맞춥니다. 클라우드 로그의 시각을 한 기준으로 맞추는 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 있습니다.

로그 객체 이름의 날짜·시각을 요청 시각으로 읽지 않습니다. 날짜로 나누는 형식은 폴더 날짜의 기준을 S3 이벤트 시각과 로그 파일 전달 시각 가운데 하나로 고르고[4], 한 요청의 레코드가 한참 늦게 전달될 수도 있습니다[2]. 그래서 특정 날짜의 요청을 찾을 때는 앞뒤 날짜의 로그 객체까지 받아 Time 필드로 거릅니다.

전달은 대개 몇 시간 안에 이뤄지지만, 한 요청의 레코드가 한참 늦게 오거나 끝내 오지 않거나 두 번 올 수도 있습니다[2]. 로깅 설정의 변화도 곧바로 반영되지 않습니다. 로깅을 켠 뒤 한 시간 동안은 요청이 기록되기도 하고 안 되기도 하며, 대상 버킷을 A 에서 B 로 바꾸면 한 시간 동안은 일부 로그가 A 로 계속 갑니다[2]. `PutBucketLogging` 레코드의 시각 앞뒤 한 시간은 기록의 빈틈이나 옛 대상 버킷에 흩어진 로그를 염두에 두고 읽습니다.

## 함정과 한계

- **공백으로만 나누면 필드가 밀린다.** Time 에는 공백이 들어 있고, Request-URI·Referer·User-Agent 는 따옴표 안에 공백이 들어갑니다[1]. 더구나 이 세 필드에는 사용자가 넣은 따옴표가 이스케이프되지 않은 채 남을 수 있어서, 따옴표를 기준으로 나눠도 드물게 필드가 밀립니다[1]. HTTP status 자리에 세 자리 숫자가 아닌 값이 오면 그 줄은 손으로 다시 봅니다.
- **User-Agent 와 Referer 는 요청자가 정한 값이다.** 헤더 값을 그대로 적은 것이라 도구 이름을 가장했을 가능성이 있습니다[1]. 판단 방법은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md)에 있습니다.
- **`x-` 쿼리 문자열.** Request-URI 안의 `x-` 로 시작하는 매개변수는 요청자가 임의로 붙일 수 있는 값이고 S3 동작에는 영향이 없습니다[1]. 이 값만으로 사용자를 판단하지 않습니다.
- **대소문자.** TLS version 필드 설명은 `TLSv1.2` 로 적지만 같은 문서의 예시 로그에는 `TLSV1.2` 가 나옵니다[1]. 검색할 때는 대소문자를 가리지 않게 합니다.
- **로그 보호 장치가 없다.** 서버 접근 로그에는 CloudTrail 같은 무결성 검증이 없고, Object Lock 을 켠 버킷은 대상 버킷이 될 수 없습니다[3][4]. 로그 객체에는 버킷 소유자에게 모든 권한이 주어지고, 로그 파일은 언제든 지울 수 있습니다[4]. AWS 는 대상 버킷에 서버 접근 로깅을 켜지 말라고 권하므로[4], 로그 파일을 지운 흔적은 대상 버킷에 CloudTrail 데이터 이벤트를 켜 둔 경우에만 남았을 가능성이 있습니다[5].
- **로깅을 끄거나 돌린 흔적.** 로깅 설정 변경은 CloudTrail 관리 이벤트 `PutBucketLogging` 으로 남고, Sigma 규칙 `aws_s3_data_management_tampering` 이 이 이름을 찾습니다[5][7]. 수명 주기 만료로 사라진 객체는 서버 접근 로그에는 남지만 CloudTrail 에는 남지 않습니다[3]. 로그를 끄거나 지운 사건을 따라가는 순서는 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)에 있습니다.
- **요금 보고서와 건수가 다를 수 있다.** 최선 노력 전달 때문에 사용량 보고서에는 있는데 서버 접근 로그에는 없는 요청이 있을 수 있습니다[2].

## 직접 분석해 보기

**원문 한 줄 따라가기.** AWS 문서의 예시 로그 다섯 줄 가운데 마지막 줄은 `REST.PUT.OBJECT s3-dg.pdf "PUT /amzn-s3-demo-bucket1/s3-dg.pdf HTTP/1.1" 200 - - 4406583 41754 28` 로 이어집니다[1]. 앞에서부터 Operation, Key, Request-URI, HTTP status 가 오고, Error Code 는 `-`, Bytes Sent 는 보낸 응답 바이트가 0 이라 `-`, Object Size 는 4406583 바이트, Total Time 은 41754 밀리초, Turn-Around Time 은 28 밀리초입니다[1]. Total Time 은 요청을 받은 때부터, Turn-Around Time 은 요청의 마지막 바이트를 받은 때부터 재므로[1], 큰 객체를 올리는 요청에서 요청 본문을 받는 시간은 Turn-Around Time 에 들어가지 않습니다.

**스크립트로 읽기.** 대상 버킷에서 로그 객체를 받은 뒤, 대괄호와 따옴표 묶음을 한 필드로 보고 나머지는 공백으로 나누면 됩니다. 27번째 뒤의 필드는 버립니다.

```python
import re, sys

TOK = re.compile(r'\[[^\]]*\]|"[^"]*"|\S+')
NAMES = ["bucket_owner", "bucket", "time", "remote_ip", "requester", "request_id",
         "operation", "key", "request_uri", "http_status", "error_code", "bytes_sent",
         "object_size", "total_time", "turn_around_time", "referer", "user_agent",
         "version_id", "host_id", "signature_version", "cipher_suite", "auth_type",
         "host_header", "tls_version", "access_point_arn", "acl_required", "source_region"]

for line in sys.stdin:
    rec = dict(zip(NAMES, TOK.findall(line)))  # 줄 끝에 새로 붙은 필드는 버린다
    if not rec.get("http_status", "").isdigit():
        print("CHECK", line.rstrip(), file=sys.stderr)  # 따옴표 때문에 밀린 줄
        continue
    print(rec["time"], rec["remote_ip"], rec["requester"], rec["operation"],
          rec["key"], rec["http_status"], rec["bytes_sent"], rec["auth_type"], sep="\t")
```

`cat 로그객체들 | python3 s3log.py | sort` 로 돌리면 시각·IP·요청자·작업·객체·응답 코드·보낸 바이트·인증 방식이 탭으로 나뉘어 나옵니다. 여기서 한 요청자가 짧은 시간에 많은 `REST.GET.OBJECT` 를 부른 구간, `QueryString` 으로 들어온 요청, `403` 이 몰린 IP 를 차례로 거릅니다. 로그가 많으면 Amazon Athena 로 대상 버킷의 로그를 직접 조회할 수 있습니다[2].

**공개 도구.** Invictus-AWS 는 계정의 버킷을 돌며 서버 접근 로깅이 켜진 버킷과 로그가 가는 대상 버킷·접두사를 목록으로 만듭니다[8]. 사건 초기에 어느 버킷의 기록이 있을 수 있는지 가늠하는 데 씁니다.

## 교차 검증

- 같은 객체 요청을 CloudTrail 데이터 이벤트에서 찾습니다. S3 데이터 이벤트가 켜져 있었다면 `eventName` 이 `GetObject`·`PutObject`·`DeleteObject` 인 레코드의 `userIdentity` 로 요청자를 더 자세히 볼 수 있습니다[5]. 필드 읽는 법은 [레코드 구조](./cloudtrail/record-structure.md), 기록 범위는 [관리 이벤트와 데이터 이벤트](./cloudtrail/event-types.md)에 있습니다.
- Remote IP 가 VPC 안의 주소이거나 끝점을 거친 요청이면 [VPC 흐름 로그](./vpc-flow-logs.md)에서 같은 시간대의 흐름을 봅니다.
- 역할 세션 ARN 이 요청자로 나오면 그 역할을 누가 넘겨받았는지 [IAM 사용자·역할·액세스 키](./iam.md)와 CloudTrail 에서 찾습니다.
- S3 관련 탐지 결과는 [GuardDuty](./guardduty.md)에서 함께 봅니다.
- 저장소에서 자료를 빼 간 사건 전체의 흐름은 [클라우드 저장소에서 자료를 빼 갔나](../../04-scenarios/data-leak/storage-exfiltration.md)에, 여러 로그를 한 줄로 세우는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 실습

AWS 문서 "Amazon S3 server access log format" 에 실린 예시 로그 다섯 줄로 풀어 봅니다[1].

1. 다섯 요청 가운데 실패한 요청은 어느 것이고, 응답 코드와 오류 코드는 무엇입니까?
2. 객체를 올린 요청을 찾아 객체 이름과 크기를 적고, Bytes Sent 가 `-` 인 까닭을 설명해 봅니다.
3. 액세스 포인트를 거친 요청은 몇 건이고, 그 요청의 Source region 과 Host Header 의 리전이 서로 다른 점을 어떻게 해석할지 적어 봅니다.
4. 다섯 요청의 User-Agent 가 모두 `S3Console/0.4` 입니다. 이 값만으로 콘솔에서 사람이 한 작업이라고 쓸 수 있는지 따져 봅니다.
5. 실제 검체에서는 조사 대상 버킷마다 `GetBucketLogging` 결과와 CloudTrail 의 `PutBucketLogging` 기록을 나란히 놓고, 조사 기간 가운데 서버 접근 로그가 있어야 할 구간과 없어도 되는 구간을 나눠 봅니다.

## 참고 문헌

1. AWS, "Amazon S3 server access log format", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/LogFormat.html
2. AWS, "Logging requests with server access logging", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html
3. AWS, "Logging options for Amazon S3", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/logging-with-S3.html
4. AWS, "Enabling Amazon S3 server access logging", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/enable-server-access-logging.html
5. AWS, "Amazon S3 CloudTrail events", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/cloudtrail-logging-s3-info.html
6. AWS, "CloudTrail record contents for management, data, and network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
7. SigmaHQ, aws_s3_data_management_tampering.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_s3_data_management_tampering.yml
8. invictus-ir, Invictus-AWS, source/main/logs.py. https://github.com/invictus-ir/Invictus-AWS
