---
title: "관리 이벤트와 데이터 이벤트"
parent: "CloudTrail"
grand_parent: "아티팩트 · AWS"
nav_order: 370
---

# 관리 이벤트와 데이터 이벤트 (Management·Data Events)

CloudTrail 이벤트는 관리·데이터·네트워크 활동·Insights 네 종류로 나뉘고, 트레일에 어느 종류를 켰는지에 따라 같은 계정에서도 남는 기록의 범위가 크게 달라집니다[1].

## 무엇을 기록하나

관리 이벤트 (Management events) 는 계정 안의 리소스를 만들고 설정하는 작업, 곧 제어 평면 (control plane) 작업을 기록합니다. IAM `AttachRolePolicy`, EC2 `CreateDefaultVpc`·`CreateSubnet`, CloudTrail `CreateTrail` 같은 호출이 여기에 들어가고, API 호출이 아닌 콘솔 로그인(`ConsoleLogin`)도 관리 이벤트로 남습니다[1][2]. API 호출이 아닌 이벤트는 `eventType` 으로 구별하며, AWS 서비스가 스스로 만든 이벤트는 `AwsServiceEvent`, 콘솔 로그인은 `AwsConsoleSignIn` 입니다[6].

데이터 이벤트 (Data events) 는 리소스 안의 데이터를 다루는 작업, 곧 데이터 평면 (data plane) 작업을 기록합니다. S3 객체의 `GetObject`·`PutObject`·`DeleteObject`, Lambda 함수 실행(`Invoke`), SNS 주제의 `Publish`·`PublishBatch`, CloudTrail Lake 채널의 `PutAuditEvents` 가 예이고, 대개 건수가 많습니다[3].

네트워크 활동 이벤트 (Network activity events) 는 VPC 끝점 (VPC endpoint) 소유자가 사설 VPC 에서 그 끝점을 거쳐 AWS 서비스로 간 API 호출을 기록합니다[4]. S3·KMS·EC2·DynamoDB·Secrets Manager·Bedrock 처럼 문서에 적힌 서비스만 지원하고, 레코드의 `eventType` 은 `AwsVpceEvents`, `eventCategory` 는 `NetworkActivity` 입니다[4][5].

Insights 이벤트 (Insights events) 는 쓰기 관리 API 의 호출량이나 관리 API 의 오류율이 평소와 크게 달라졌을 때만 생깁니다[1]. 비정상 활동이 시작될 때 한 건, 끝날 때 한 건이 남고, 두 레코드는 `eventID` 가 서로 다르지만 `sharedEventID` 는 같습니다[9].

네 종류는 모두 같은 CloudTrail JSON 형식을 씁니다[1]. 필드 하나하나를 읽는 법은 [레코드 구조](./record-structure.md)에서, 레코드가 어디에 얼마나 남는지는 [트레일과 이벤트 기록](./trails.md)에서 다룹니다.

## 종류별 기본값과 요금

2026년 9월 문서 기준입니다.

| 종류 | `eventCategory` | 트레일·이벤트 데이터 저장소 기본값 | 이벤트 기록(90일) | 요금 |
|---|---|---|---|---|
| 관리 | `Management` | 기록함 | 보임 | 첫 사본은 무료(S3 저장 요금은 따로), 사본을 더 만들면 요금[3][12] |
| 데이터 | `Data` | 기록하지 않음 | 안 보임 | 추가 요금[3] |
| 네트워크 활동 | `NetworkActivity` | 기록하지 않음 | 안 보임 | 추가 요금[4] |
| Insights | `Insight` | 기록하지 않음 | 안 보임 | 추가 요금, 트레일과 이벤트 데이터 저장소 양쪽에 켜면 따로 청구[1] |

이벤트 기록 (Event history) 화면은 관리 이벤트만 보여 주고 데이터·Insights·네트워크 활동 이벤트는 보여 주지 않습니다[7]. 데이터 이벤트 가운데 Lambda 의 `LambdaESMDisabled` 는 예외로 기본 기록됩니다[12]. `eventCategory` 필드 설명에는 `Management`·`Data`·`NetworkActivity` 세 값만 나오지만, 로그 예시의 Insights 레코드에는 `"eventType": "AwsCloudTrailInsight"` 와 `"eventCategory": "Insight"` 가 붙어 있습니다[5][9].

## 기록 범위를 정하는 설정

트레일은 기본 이벤트 선택기 (basic event selectors) 나 고급 이벤트 선택기 (advanced event selectors) 가운데 하나로 무엇을 기록할지 정하고, 고급 선택기를 적용하면 기존 기본 선택기를 덮어씁니다[2]. 기본 선택기로 데이터 이벤트를 받을 수 있는 리소스 형식은 `AWS::S3::Object`·`AWS::Lambda::Function`·`AWS::DynamoDB::Table` 셋뿐이고, `AWS::S3::AccessPoint`·`AWS::SNS::Topic`·`AWS::ECS::ContainerInstance` 같은 나머지 형식은 고급 선택기로만 켤 수 있습니다[3]. 이벤트 데이터 저장소는 데이터 이벤트를 고급 선택기로만 받습니다[3].

고급 선택기는 `eventCategory`, `eventSource`, `eventName`, `eventType`, `readOnly`, `resources.type`, `resources.ARN`, `userIdentity.arn`, `sessionCredentialFromConsole` 필드에 조건을 겁니다[2][3]. 네트워크 활동 이벤트에는 `vpcEndpointId` 와 `errorCode` 가 더 있고, `errorCode` 에 쓸 수 있는 값은 `VpceAccessDenied` 하나입니다[4]. 조건에 `*` 같은 와일드카드는 쓸 수 없고 `StartsWith`·`EndsWith`·`NotStartsWith`·`NotEndsWith` 로 앞뒤를 맞춥니다[2]. 조건에는 특정 IAM 주체(`userIdentity.arn`), 콘솔 세션에서 나온 호출(`sessionCredentialFromConsole`), AWS 서비스 이벤트(`eventType` 이 `AwsServiceEvent`)를 빼는 것도 들어갈 수 있습니다[2]. 그래서 트레일에 없는 기록이 설정 때문에 빠졌을 가능성을 늘 먼저 따집니다.

**읽기와 쓰기.** 관리 이벤트와 데이터 이벤트 모두 읽기(Read)만, 쓰기(Write)만, 둘 다 가운데 하나를 고를 수 있습니다[2][3]. 읽기는 `DescribeSecurityGroups`·`DescribeSubnets` 처럼 리소스를 바꾸지 않는 작업이고, 쓰기는 `RunInstances`·`TerminateInstances` 처럼 바꾸거나 바꿀 수 있는 작업입니다[2]. 레코드에서는 `readOnly` 가 `true` 이면 읽기, `false` 이면 쓰기입니다[5].

**KMS·RDS Data API 제외.** 관리 이벤트에서 KMS 와 RDS Data API 이벤트를 뺄 수 있습니다. 기본 선택기에서는 `ExcludeManagementEventSources` 에 `kms.amazonaws.com`·`rdsdata.amazonaws.com` 을 넣고, 고급 선택기에서는 `eventSource` 에 `NotEquals` 조건을 겁니다[2]. KMS 의 `Encrypt`·`Decrypt`·`GenerateDataKey` 는 흔히 KMS 이벤트의 99% 넘게 차지하고 읽기 이벤트로 기록되며, `Disable`·`Delete`·`ScheduleKey` 같은 작업은 쓰기 이벤트로 기록됩니다[2]. 이 제외 설정은 트레일과 이벤트 데이터 저장소에만 걸리고 이벤트 기록에는 걸리지 않습니다[2].

**S3 데이터 이벤트의 범위.** S3 데이터 이벤트는 버킷과 접두사 단위로 켭니다[3]. 버킷 `amzn-s3-demo-bucket3` 의 접두사 `my-images` 에 쓰기만 켰다면 기록 여부는 다음과 같습니다[3].

| 호출 | 대상 객체 | 기록 여부 | 까닭 |
|---|---|---|---|
| `DeleteObject` | `my-images/example.jpg` | 기록함 | 버킷·접두사·쓰기 조건에 모두 맞음 |
| `DeleteObject` | `my-videos/example.avi` | 기록 안 함 | 접두사가 다름 |
| `GetObject` | `my-images/example.jpg` | 기록 안 함 | 읽기 이벤트인데 쓰기만 켰음 |

### 설정 확인하기

지금 트레일에 걸린 선택기는 `aws cloudtrail get-event-selectors --trail-name TrailName` 으로, 이벤트 데이터 저장소의 선택기는 `aws cloudtrail get-event-data-store --event-data-store` 에 저장소 ARN 을 주어 봅니다[2][3]. 아무것도 바꾸지 않은 트레일은 관리 이벤트만 기록하도록 다음과 같이 나옵니다(계정 ID 는 만든 예시이고, 구조는 문서의 기본값 예시와 같습니다)[2].

```json
{
 "TrailARN": "arn:aws:cloudtrail:us-east-1:123456789012:trail/TrailName",
 "AdvancedEventSelectors": [
  {
   "Name": "Management events selector",
   "FieldSelectors": [
    { "Field": "eventCategory", "Equals": [ "Management" ] }
   ]
  }
 ]
}
```

기본 선택기를 쓰는 트레일이면 `EventSelectors` 아래에 `ReadWriteType`, `IncludeManagementEvents`, `DataResources`, `ExcludeManagementEventSources` 가 나옵니다[2].

이 명령은 지금 설정만 보여 주고 사건 당시 설정은 보여 주지 않습니다. 선택기는 `PutEventSelectors`, Insights 설정은 `PutInsightSelectors` API 로 바꾸고[1][3], CloudTrail 자신의 설정 호출도 관리 이벤트로 남습니다(`CreateTrail` 이 관리 이벤트의 예입니다)[1]. 관리 이벤트에서 `eventSource` 가 `cloudtrail.amazonaws.com` 이고 `eventName` 이 `PutEventSelectors`·`PutInsightSelectors` 인 레코드를 찾아 `requestParameters` 를 읽으면 언제부터 어떤 범위가 기록됐는지 시간 순으로 세울 수 있습니다. 트레일을 멈추거나 지우거나 고친 `StopLogging`·`DeleteTrail`·`UpdateTrail` 도 같은 방법으로 찾습니다[15].

## 서비스별 경계

같은 서비스라도 어떤 작업은 관리 이벤트, 어떤 작업은 데이터 이벤트로 남습니다.

| 서비스 | 관리 이벤트 예 | 데이터 이벤트 예 | 더 볼 곳 |
|---|---|---|---|
| S3 | `CreateBucket`, `DeleteBucket`, `PutBucketPolicy`, `PutBucketLifecycle`, `ListBuckets`[10] | `GetObject`, `PutObject`, `DeleteObject`, `DeleteObjects`, `HeadObject`, `ListObjects`, `RestoreObject`(`AWS::S3::Object`)[10] | [S3 접근 기록](../s3-access-logs.md) |
| Lambda | `CreateFunction20150331`, `UpdateFunctionCode20150331v2` 처럼 이름에 날짜·판이 붙음[12] | `Invoke`(`AWS::Lambda::Function`)[12] | [Lambda·컨테이너 서비스 기록](../lambda-containers.md) |
| EBS direct API | `StartSnapshot`, `CompleteSnapshot`[13] | `ListSnapshotBlocks`, `ListChangedBlocks`, `GetSnapshotBlock`, `PutSnapshotBlock`[13] | [EC2 인스턴스와 스냅숏](../ec2-ebs.md) |
| ECS | `CreateService`, `RunTask`, `DeleteCluster`[14] | `ecs:Poll`, `ecs:StartTelemetrySession`, `ecs:PutSystemLogEvents`(`AWS::ECS::ContainerInstance`)[14] | [Lambda·컨테이너 서비스 기록](../lambda-containers.md) |
| DynamoDB | — | `PutItem`, `DeleteItem`, `UpdateItem`(`AWS::DynamoDB::Table`)[3] | 스트림이 있는 테이블이면 `resources` 에 `AWS::DynamoDB::Stream` 과 `AWS::DynamoDB::Table` 이 함께 들어감[3] |

CloudTrail 의 `eventName` 은 API 작업 이름과 다를 수 있습니다. S3 의 `PutBucketLifecycleConfiguration` 은 `PutBucketLifecycle` 로, `DeletePublicAccessBlock`(계정 수준)은 `DeleteAccountPublicAccessBlock` 으로 남고[10], Lambda 의 `GetFunction` 은 `GetFunction20150331v2` 로 남습니다[12]. 검색할 때는 API 이름이 아니라 기록된 이벤트 이름으로 찾습니다.

## 증거로서 의미

**증명하는 것.** 관리 이벤트는 기본으로 켜져 있고 이벤트 기록에 90일 동안 남아서, 트레일이 없는 계정에서도 최근 90일 동안 누가 어느 리소스의 설정을 바꿨는지 보여 줍니다[2][7]. 데이터 이벤트가 켜져 있었다면 어느 자격 증명이 어느 객체를 읽고 쓰고 지웠는지까지 보여 줍니다[3]. S3 버킷 소유자의 트레일에는 다른 계정이 그 버킷 객체를 부른 호출도 남아서, 호출한 쪽 계정의 로그 없이도 교차 계정 접근을 볼 수 있습니다[3]. 선택기 변경 기록은 어느 기간에 어떤 종류가 기록됐는지를 보여 줍니다.

**증명하지 못하는 것.** 관리 이벤트만 있으면 버킷 설정 변경은 보이지만 객체를 읽었는지는 보이지 않습니다[10]. 데이터 이벤트가 꺼져 있었거나 호출이 버킷·접두사·읽기/쓰기 조건 밖이었다면 "기록 없음" 은 "행위 없음" 이 아닙니다[3]. 다른 계정이 소유한 객체를 내 트레일에 지정해도 내 계정이 부른 호출만 남습니다[3]. 공유받은 스냅숏에 EBS direct API 를 쓰면 데이터 이벤트가 스냅숏 소유 계정으로 가지 않습니다[13]. 잘못된 자격 증명으로 인증에 실패한 S3 요청과 301 리다이렉트는 CloudTrail 에 남지 않고, 권한 부족(`AccessDenied`)과 익명 요청은 남습니다[11]. VPC 끝점 정책이 거부한 S3 요청은 요청자와 버킷 소유자에게 CloudTrail 로그로 가지 않고[11], 끝점 소유자가 네트워크 활동 이벤트를 켜 두었다면 `VpceAccessDenied` 로 남습니다[4]. Insights 이벤트는 비정상의 시작과 끝만 알려 줄 뿐 개별 호출을 담지 않습니다[9].

보고서에는 "이 기간 이 트레일은 이 버킷의 쓰기 데이터 이벤트만 기록하도록 설정돼 있었고, 그 범위 안에 이 역할 세션의 `DeleteObject` 레코드가 있다" 처럼 기록 범위와 기록 내용을 함께 씁니다.

## 시각 해석

모든 종류의 `eventTime` 은 요청이 끝난 시각이고 UTC 입니다[5]. 형식과 시계의 출처는 [레코드 구조](./record-structure.md)에서 다룹니다.

전달 지연은 출처마다 적힌 값이 다릅니다. CloudTrail 문서는 API 호출 뒤 평균 약 5분 안에 로그를 전달하며 이 시간은 보장되지 않는다고 적고[8], S3 로그 비교표는 데이터 이벤트는 5분마다, 관리 이벤트는 15분마다 전달된다고 적습니다[11]. Insights 이벤트는 보통 비정상 활동이 있고 30분 안에 버킷에 도착하고, 처음 켠 뒤에는 첫 이벤트가 나오기까지 최대 36시간이 걸릴 수 있습니다[8]. Insights 의 끝 레코드에는 `insightDetails.state` 가 `End` 이고 `insightContext.statistics` 에 `insightDuration` 이 붙습니다[9].

선택기를 바꾼 `PutEventSelectors` 레코드의 `eventTime` 은 기록 범위가 바뀐 시점입니다. 이 시각을 타임라인에 함께 올려 두면 어느 구간에서 "기록 없음" 을 근거로 쓸 수 있는지 가려집니다. 여러 로그를 한 줄로 세우는 방법은 [클라우드 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

- **KMS 제외.** 트레일에서 KMS 이벤트를 빼면 건수가 많은 `Decrypt` 뿐 아니라 `ScheduleKey` 같은 쓰기 이벤트도 함께 빠집니다[2]. 쓰기만 남기려면 쓰기 관리 이벤트를 고르고 KMS 제외를 끄는 설정이어야 합니다[2].
- **로그 버킷의 재귀 기록.** 로그를 받는 버킷에 데이터 이벤트를 켜면 CloudTrail 이 로그 파일을 넣을 때마다 `PutObject` 가 다시 데이터 이벤트가 되고, 그 이벤트는 다음 로그 파일에 들어갑니다[3]. 로그 버킷에 `PutObject` 가 대량으로 보이면 CloudTrail 자신의 전달일 가능성이 있습니다. 트레일에 `RecursiveLogging` 을 `false` 로 두면 이런 이벤트를 억제합니다[3].
- **`DeleteObjects` 의 펼침.** S3 `DeleteObjects` 데이터 이벤트를 기록하면 `DeleteObjects` 레코드와 함께 지운 객체마다 `DeleteObject` 레코드가 남고, 이 추가 레코드를 빼도록 설정할 수 있습니다[10]. 지운 객체 수를 셀 때 두 가지를 겹쳐 세지 않도록 하고, 제외 설정이 걸려 있으면 개별 객체 이름이 남지 않았을 수 있습니다.
- **집계 이벤트.** 데이터 이벤트를 모은 집계 이벤트가 있고, 예시 이름은 `API_ACTIVITY`·`RESOURCE_ACCESS` 입니다[3]. 트레일 버킷에서는 `CloudTrail-Aggregated` 폴더에 따로 쌓입니다[8]. 개별 호출을 찾을 때는 `CloudTrail` 폴더의 원래 데이터 이벤트를 봅니다.
- **탐지 규칙과 이벤트 종류.** Sigma 규칙 `aws_s3_data_management_tampering` 이 찾는 이름 가운데 `RestoreObject` 는 S3 데이터 이벤트라서[10][16], 데이터 이벤트를 켠 트레일에서만 걸립니다. 같은 규칙은 수명 주기 설정을 `PutLifecycleConfiguration` 으로 찾지만, 이 호출은 CloudTrail 에 `PutBucketLifecycle` 로 기록됩니다[10][16]. 규칙을 돌리기 전에 검체에 실제로 남은 `eventName` 을 확인합니다. 규칙으로 로그를 훑는 방법은 [탐지 규칙으로 로그 훑기](../../../03-techniques/analysis/detection-rules.md)에 있습니다.

## 직접 분석해 보기

트레일 버킷에서 받은 로그 파일로 종류별 건수를 셉니다. 관리·데이터 이벤트는 `CloudTrail` 폴더에, Insights 는 `CloudTrail-Insight`, 네트워크 활동은 `CloudTrail-NetworkActivity` 폴더에 따로 있으므로 폴더를 모두 받아야 합니다[8].

```sh
gzip -dc *.json.gz \
  | jq -r '.Records[] | [.eventCategory, .eventType, (.readOnly|tostring)] | @tsv' \
  | sort | uniq -c | sort -rn
```

`Data` 줄이 하나도 없으면 그 기간 트레일이 데이터 이벤트를 기록하지 않았을 가능성이 큽니다. 이어서 기록 범위를 바꾼 호출을 뽑습니다.

```sh
gzip -dc *.json.gz \
  | jq -c '.Records[]
      | select(.eventSource == "cloudtrail.amazonaws.com")
      | select(.eventName | IN("PutEventSelectors","PutInsightSelectors","StopLogging","UpdateTrail","DeleteTrail"))
      | {eventTime, eventName, arn: .userIdentity.arn, ip: .sourceIPAddress, req: .requestParameters}' \
  | sort
```

트레일 버킷이 없으면 이벤트 기록에서 같은 이벤트 이름을 찾습니다. 이벤트 기록은 관리 이벤트만 담으므로 설정 변경 호출은 90일 안이면 찾을 수 있습니다[7]. 조회 방법은 [트레일과 이벤트 기록](./trails.md)에 있습니다.

## 교차 검증

- 데이터 이벤트가 꺼져 있던 S3 버킷은 [S3 접근 기록](../s3-access-logs.md)이 켜져 있었는지 봅니다. 인증 실패 요청처럼 CloudTrail 에 남지 않는 요청도 서버 접근 로그에는 남습니다[11].
- 네트워크 활동 이벤트의 `vpcEndpointId` 는 [VPC 흐름 로그](../vpc-flow-logs.md)의 같은 시간대 흐름과 맞춰 봅니다.
- 로그 종류를 서비스 사이에서 비교한 내용은 [로그의 종류](../../../01-foundations/logging/log-types.md)에, 보관 기간과 요금제 차이는 [보관 기간과 라이선스](../../../01-foundations/logging/retention-licensing.md)에 있습니다.

## 참고 문헌

1. AWS, "CloudTrail concepts", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html
2. AWS, "Logging management events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-management-events-with-cloudtrail.html
3. AWS, "Logging data events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html
4. AWS, "Logging network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-network-events-with-cloudtrail.html
5. AWS, "CloudTrail record contents for management, data, and network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
6. AWS, "Non-API events captured by CloudTrail", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-non-api-events.html
7. AWS, "Working with CloudTrail event history", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
8. AWS, "Getting and viewing your CloudTrail log files", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/get-and-view-cloudtrail-log-files.html
9. AWS, "CloudTrail log file examples", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-examples.html
10. AWS, "Amazon S3 CloudTrail events", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/cloudtrail-logging-s3-info.html
11. AWS, "Logging options for Amazon S3", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/logging-with-S3.html
12. AWS, "Logging AWS Lambda API calls using AWS CloudTrail", AWS Lambda Developer Guide. https://docs.aws.amazon.com/lambda/latest/dg/logging-using-cloudtrail.html
13. AWS, "Log EBS direct APIs calls using AWS CloudTrail", Amazon EBS User Guide. https://docs.aws.amazon.com/ebs/latest/userguide/logging-ebs-apis-using-cloudtrail.html
14. AWS, "Log Amazon ECS API calls using AWS CloudTrail", Amazon ECS Developer Guide. https://docs.aws.amazon.com/AmazonECS/latest/developerguide/logging-using-cloudtrail.html
15. SigmaHQ, aws_cloudtrail_disable_logging.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_disable_logging.yml
16. SigmaHQ, aws_s3_data_management_tampering.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_s3_data_management_tampering.yml
