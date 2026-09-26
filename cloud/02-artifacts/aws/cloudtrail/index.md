---
title: "CloudTrail"
parent: "아티팩트 · AWS"
nav_order: 350
has_children: true
has_toc: false
---

# CloudTrail (CloudTrail)

CloudTrail 은 AWS 계정에서 누가 어떤 API 를 언제 어디서 불렀고 결과가 어땠는지를 이벤트 하나당 JSON 레코드 하나로 남기는 기록입니다[1][4].

## 왜 중요한가

AWS 관리 콘솔·AWS CLI·AWS SDK·API 로 한 작업이 모두 이벤트로 남아서, 계정 안에서 무슨 일이 있었는지는 CloudTrail 레코드에서 찾습니다[2]. 레코드에는 호출한 자격 증명(`userIdentity`), 호출한 서비스와 작업 이름(`eventSource`·`eventName`), 요청이 끝난 시각(`eventTime`, UTC), 호출한 주소와 리전(`sourceIPAddress`·`awsRegion`), 결과(`errorCode`·`responseElements`)가 들어 있습니다[4]. 필드 하나하나를 읽는 법은 [레코드 구조](./record-structure.md)에서 다룹니다.

CloudTrail 은 AWS 계정에서 기본으로 켜져 있어서 따로 설정하지 않은 계정에도 기록이 있습니다[2]. 다만 기본으로 볼 수 있는 이벤트 기록 (Event history) 은 리전마다 최근 90일의 관리 이벤트만 보여 줍니다[1][2]. 90일보다 오래된 기록이나 S3 객체를 읽고 쓴 것 같은 데이터 이벤트는 사고가 나기 전에 트레일 (Trail) 이나 CloudTrail Lake 이벤트 데이터 저장소 (Event data store) 를 만들어 둔 계정에만 남습니다[1][3]. 그래서 조사를 시작하면 기록을 읽기 전에 그 계정에 트레일이 있었는지, 무엇을 기록하도록 설정했는지부터 확인합니다.

CloudTrail 이 기록하는 이벤트는 관리 이벤트 (Management events)·데이터 이벤트 (Data events)·네트워크 활동 이벤트 (Network activity events)·Insights 이벤트 (Insights events) 네 가지이고, 모두 같은 CloudTrail JSON 형식을 씁니다[3]. 트레일과 이벤트 데이터 저장소는 기본으로 관리 이벤트만 기록하고, 데이터 이벤트와 Insights 이벤트는 따로 켜야 기록합니다[3]. 따라서 "기록이 없다" 는 사실은 그 종류의 이벤트를 켜 두었을 때만 "그 행위가 없었다" 는 뜻이 됩니다. 종류별 범위와 설정 확인 방법은 [관리 이벤트와 데이터 이벤트](./event-types.md)에서 다룹니다.

## 한눈에 보기

CloudTrail 기록은 네 곳에 있을 수 있고, 곳마다 보관 기간과 담기는 이벤트가 다릅니다. 보관 기간과 요금은 2026년 9월 문서 기준입니다.

| 저장 위치 | 보관 기간 | 담기는 이벤트 | 비용 |
|---|---|---|---|
| 이벤트 기록 (Event history) | 리전마다 최근 90일[2] | 관리 이벤트만[2] | 보는 데 CloudTrail 요금 없음[2] |
| 트레일 → S3 버킷 | 버킷에 두는 동안 계속, S3 수명 주기 규칙으로 보관·삭제[1] | 설정한 관리·데이터·네트워크 활동·Insights 이벤트[3] | 관리 이벤트 첫 사본은 CloudTrail 요금 없음, S3 저장 요금은 있음[6] |
| 트레일 → CloudWatch Logs | 로그 그룹의 보관 설정대로, 기본은 기한 없이 보관[8] | 트레일과 같되, 256KB 를 넘는 이벤트는 보내지 않음[7] | — |
| Lake 이벤트 데이터 저장소 | 1년 연장형: 기본 366일·최대 3,653일, 7년형: 2,557일[9][10] | 고급 이벤트 선택기 (Advanced event selectors) 로 고른 이벤트[9] | 수집·저장·쿼리 요금[10] |

트레일은 로그 파일을 gzip 으로 압축한 JSON 파일로 S3 버킷에 쌓고, 파일은 한 시간에 여러 번, 대략 5분마다 나옵니다[1][5]. API 호출 뒤 전달까지 평균 5분쯤 걸리지만 이 시간은 보장되지 않습니다[1]. 버킷에 쓸 수 없게 설정이 틀어지면 CloudTrail 은 30일 동안 다시 전달을 시도합니다[1]. 로그 파일 무결성 검증 (Log file integrity validation) 을 켜 두면 한 시간마다 그 시간에 전달한 로그 파일의 SHA-256 해시를 담고 SHA-256 with RSA 로 서명한 다이제스트 파일 (Digest file) 이 따로 생겨서, 전달한 뒤 로그 파일이 바뀌거나 지워졌는지 확인할 수 있습니다[11].

CloudTrail Lake 는 2026년 5월 31일부터 새 고객을 받지 않고, 이미 쓰던 고객은 그대로 씁니다[9]. 이벤트 기록은 계정에 있는 트레일·이벤트 데이터 저장소와 이어져 있지 않아서 트레일을 멈추거나 지워도 영향을 받지 않습니다[1][2]. `CreateTrail` 같은 로깅 설정 작업은 관리 이벤트라서[3], 트레일을 멈춘 `StopLogging` 호출도 90일 안이면 이벤트 기록에서 찾을 수 있습니다. 저장 위치별 경로·파일 이름·무결성 검증은 [트레일과 이벤트 기록](./trails.md)에서 다룹니다.

## 읽는 순서

1. [레코드 구조 (Event Record)](./record-structure.md) — 레코드 한 건의 필드, `userIdentity` 로 호출 주체를 구분하는 법, 시각 필드를 읽는 법을 다룹니다.
2. [관리 이벤트와 데이터 이벤트 (Management·Data Events)](./event-types.md) — 이벤트 종류마다 무엇이 기록되고 무엇이 기본으로 빠지는지, 당시 설정을 어떻게 확인하는지를 다룹니다.
3. [트레일과 이벤트 기록 (Trails·Event History·Lake)](./trails.md) — 기록이 저장되는 곳과 보관 기간, S3 경로와 파일 이름, 다이제스트 파일로 무결성을 확인하는 법을 다룹니다.

## 함께 볼 페이지

- [IAM 사용자·역할·액세스 키](../iam.md) — `userIdentity` 에 나오는 사용자·역할·액세스 키 ID 를 IAM 쪽 기록과 맞춰 봅니다.
- [S3 접근 기록](../s3-access-logs.md) — 데이터 이벤트를 켜지 않은 버킷의 객체 접근은 S3 서버 접근 로그에서 찾습니다.
- [CloudWatch Logs](../cloudwatch-logs.md) — 트레일이 CloudWatch Logs 로 보낸 사본의 보관과 조회를 다룹니다.
- [GuardDuty](../guardduty.md) — CloudTrail 을 분석해 만든 탐지 결과를 원래 레코드와 맞춰 봅니다.
- [로그의 종류](../../../01-foundations/logging/log-types.md) · [보관 기간과 라이선스](../../../01-foundations/logging/retention-licensing.md) — 클라우드 로그 전반의 구분과 보관 원리입니다.
- [AWS·Azure·GCP 수집](../../../03-techniques/acquisition/iaas-collection.md) — CloudTrail 로그를 모으는 절차입니다.
- [클라우드 타임라인](../../../03-techniques/analysis/timeline.md) — UTC 인 `eventTime` 을 다른 기록과 한 줄로 맞추는 법입니다.
- [linux] [클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html) — EC2 인스턴스 안쪽의 기록은 가상 머신 수집으로 따로 확보합니다.

## 참고 문헌

1. AWS, "How CloudTrail works", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/how-cloudtrail-works.html
2. AWS, "Working with CloudTrail event history", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
3. AWS, "CloudTrail concepts", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html
4. AWS, "CloudTrail record contents for management, data, and network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
5. AWS, "Getting and viewing your CloudTrail log files", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/get-and-view-cloudtrail-log-files.html
6. AWS, "Working with CloudTrail trails", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-trails.html
7. AWS, "Sending events to CloudWatch Logs", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/send-cloudtrail-events-to-cloudwatch-logs.html
8. AWS, "Working with log groups and log streams", Amazon CloudWatch Logs User Guide. https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html
9. AWS, "Working with AWS CloudTrail Lake", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake.html
10. AWS, "Managing CloudTrail Lake costs", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake-manage-costs.html
11. AWS, "Validating CloudTrail log file integrity", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html
