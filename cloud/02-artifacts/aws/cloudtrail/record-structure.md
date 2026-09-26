---
title: "레코드 구조 (Event Record)"
parent: "CloudTrail"
grand_parent: "아티팩트 · AWS"
nav_order: 360
---

# 레코드 구조 (Event Record)

CloudTrail 이벤트 레코드 하나에는 누가(`userIdentity`), 무엇을(`eventSource`·`eventName`), 언제(`eventTime`), 어디서(`sourceIPAddress`·`awsRegion`), 어떤 결과로(`errorCode`·`responseElements`) 호출했는지가 JSON 필드로 들어 있습니다[1].

## 무엇을 기록하나

CloudTrail 은 API 호출과 콘솔 로그인 같은 활동을 이벤트 하나당 JSON 레코드 하나로 남깁니다. 관리 이벤트·데이터 이벤트·네트워크 활동 이벤트는 모두 같은 레코드 구조를 쓰고, 종류에 따라 일부 필드가 있거나 없습니다[1]. 이벤트 종류와 기록 범위는 [관리 이벤트와 데이터 이벤트](./event-types.md)에서, 레코드가 어디에 얼마나 남는지는 [트레일과 이벤트 기록](./trails.md)에서 다룹니다. 이 쪽은 레코드 안의 필드를 읽는 법만 다룹니다.

## 파일과 레코드의 모양

트레일이 S3 에 전달하는 로그 파일은 gzip 으로 압축한 JSON 파일이고, 파일 하나에 레코드가 하나 이상 들어 있습니다[3]. 최상위 키는 `Records` 하나이고 그 값이 레코드 배열입니다[3]. 파일 안의 레코드는 API 호출 순서대로 쌓이지 않아서 순서에 의미가 없습니다[4]. 분석할 때는 `eventTime` 으로 다시 정렬합니다.

다음은 역할을 넘겨받은 임시 자격 증명으로 EC2 인스턴스를 멈춘 호출을 가정해 만든 예시이고, 필드 이름과 구조는 `StopInstances` 레코드와 같습니다[3]. 계정 ID·키 ID·IP·GUID 는 모두 지어낸 값입니다.

```json
{"Records": [{
  "eventVersion": "1.11",
  "userIdentity": {
    "type": "AssumedRole",
    "principalId": "AROAEXAMPLEROLEID0001:ops-session",
    "arn": "arn:aws:sts::123456789012:assumed-role/OpsRole/ops-session",
    "accountId": "123456789012",
    "accessKeyId": "ASIAIOSFODNN7EXAMPLE",
    "sessionContext": {
      "sessionIssuer": {
        "type": "Role",
        "principalId": "AROAEXAMPLEROLEID0001",
        "arn": "arn:aws:iam::123456789012:role/OpsRole",
        "accountId": "123456789012",
        "userName": "OpsRole"
      },
      "attributes": {
        "creationDate": "2026-09-01T02:10:44Z",
        "mfaAuthenticated": "false"
      }
    }
  },
  "eventTime": "2026-09-01T02:14:05Z",
  "eventSource": "ec2.amazonaws.com",
  "eventName": "StopInstances",
  "awsRegion": "ap-northeast-2",
  "sourceIPAddress": "203.0.113.25",
  "userAgent": "aws-cli/2.13.5 Python/3.11.4",
  "requestParameters": {"instancesSet": {"items": [{"instanceId": "i-EXAMPLE0123456789"}]}, "force": false},
  "responseElements": {"instancesSet": {"items": [{"instanceId": "i-EXAMPLE0123456789",
    "currentState": {"code": 64, "name": "stopping"}, "previousState": {"code": 16, "name": "running"}}]}},
  "requestID": "11111111-2222-3333-4444-EXAMPLE00001",
  "eventID": "aaaaaaaa-bbbb-cccc-dddd-EXAMPLE00002",
  "readOnly": false,
  "eventType": "AwsApiCall",
  "managementEvent": true,
  "recipientAccountId": "123456789012",
  "eventCategory": "Management",
  "tlsDetails": {"tlsVersion": "TLSv1.2", "cipherSuite": "ECDHE-RSA-AES128-GCM-SHA256",
    "clientProvidedHostHeader": "ec2.ap-northeast-2.amazonaws.com"}
}]}
```

호출이 실패하면 같은 레코드에 `errorCode` 와 `errorMessage` 가 붙습니다[1]. 없는 트레일을 고치려 한 `UpdateTrail` 호출이면 `"errorCode": "TrailNotFoundException"` 과 `"errorMessage": "Unknown trail: ..."` 이 남고 `responseElements` 는 `null` 입니다[3].

## 최상위 필드

`eventVersion` 은 레코드 형식의 판이고 2026년 9월 문서 기준 최신 값은 `1.11` 입니다[1]. 기존 구조와 호환되지 않게 바뀌면 주 번호가, 필드가 늘면 부 번호가 오르고, 부 번호에는 앞자리 0 이 붙지 않아서 숫자로 비교하면 됩니다[1]. 아래 표의 "도입" 칸은 그 필드가 처음 나온 `eventVersion` 입니다. 이보다 오래된 레코드에는 그 필드가 없습니다.

| 필드 | 도입 | 담는 것 | 읽을 때 주의 |
|---|---|---|---|
| `eventTime` | 1.0 | 요청이 끝난 시각(UTC) | 아래 "시각 해석" 참고[1] |
| `userIdentity` | 1.0 | 요청한 주체와 쓴 자격 증명 | 아래 절 참고[1][2] |
| `eventSource` | 1.0 | 요청을 받은 서비스 | 보통 `서비스.amazonaws.com` 꼴이지만 CloudWatch 는 `monitoring.amazonaws.com` 처럼 예외가 있음[1] |
| `eventName` | 1.0 | 호출한 API 작업 이름 | [1] |
| `awsRegion` | 1.0 | 요청을 받은 리전 | [1] |
| `sourceIPAddress` | 1.0 | 요청이 온 IP 주소 | 콘솔에서 한 작업은 콘솔 웹 서버가 아니라 그 밑의 고객 리소스 주소, AWS 서비스가 부른 것은 DNS 이름만, AWS 가 시작한 이벤트는 보통 `AWS Internal/#`[1] |
| `userAgent` | 1.0 | 요청한 도구 | 최대 1KB, 넘으면 잘림. AWS 서비스가 부르면 호출한 서비스의 이벤트 소스(예: `ec2.amazonaws.com`)나 `AWS Internal/#`[1] |
| `errorCode`·`errorMessage` | 1.0 | 오류 코드와 설명 | 오류일 때만 있음. 각각 최대 1KB. 서비스에 따라 오류가 `responseElements` 안에 들어가기도 함[1] |
| `requestParameters` | 1.0 | 요청에 실린 매개변수 | 100KB 를 넘으면 내용이 통째로 빠짐[1] |
| `responseElements` | 1.0 | 생성·수정·삭제 작업의 응답 | 읽기 작업이거나 응답이 없으면 `null`. 100KB 를 넘으면 빠짐[1] |
| `additionalEventData` | 1.0 | 요청·응답 밖의 추가 정보 | 최대 28KB, 내용은 이벤트마다 다름. 콘솔 로그인의 `MFAUsed` 가 여기 있음[1] |
| `requestID` | 1.01 | 서비스가 만든 요청 ID | [1] |
| `eventID` | 1.01 | CloudTrail 이 이벤트마다 만든 GUID | 이벤트 하나를 가리키는 값이라 검색용 데이터베이스의 기본 키로 쓸 수 있음[1] |
| `readOnly` | 1.01 | 읽기 전용 작업인지 | `true`/`false`[1] |
| `resources` | 1.01 | 대상 리소스 목록 | ARN·소유 계정 ID·`AWS::서비스::형식` 꼴의 형식 이름[1] |
| `apiVersion` | 1.01 | `AwsApiCall` 의 API 판 | [1] |
| `eventType` | 1.02 | 레코드를 만든 이벤트 유형 | `AwsApiCall`, `AwsServiceEvent`, `AwsConsoleAction`, `AwsConsoleSignIn`, `AwsVpceEvents`[1] |
| `recipientAccountId` | 1.02 | 이 이벤트를 받은 계정 | 교차 계정 접근이면 `userIdentity.accountId` 와 다를 수 있음[1] |
| `sharedEventID` | 1.03 | 여러 계정에 간 같은 작업의 공통 GUID | 아래 "교차 계정" 참고[1] |
| `vpcEndpointId` | 1.04 | 요청이 지난 VPC 끝점 | [1] |
| `serviceEventDetails` | 1.05 | 서비스 이벤트의 계기와 결과 | 최대 100KB[1] |
| `managementEvent` | 1.06 | 관리 이벤트인지 | 불리언[1] |
| `eventCategory` | 1.07 | `Management`, `Data`, `NetworkActivity` | [1] |
| `addendum` | 1.08 | 늦게 온 이벤트나 나중에 고친 내용의 사유 | 아래 "함정" 참고[1] |
| `sessionCredentialFromConsole` | 1.08 | 콘솔 세션에서 나온 호출인지 | 값이 `true` 일 때만 나타남[1] |
| `tlsDetails` | 1.08 | TLS 판·암호 스위트·클라이언트가 보낸 호스트 이름·키 교환 방식 | AWS 서비스가 대신 부른 호출에는 없음[1] |
| `edgeDeviceDetails` | 1.08 | 요청 대상 엣지 장치 | S3 Outposts 이벤트에 있음[1] |
| `vpcEndpointAccountId` | 1.09 | VPC 끝점 소유 계정 | [1] |
| `eventContext` | 1.11 | 리소스 태그·IAM 전역 조건 키 | 태그·조건 키를 넣도록 설정한 Lake 이벤트 데이터 저장소에만 있고, 이벤트 기록·EventBridge·`lookup-events`·트레일에는 없음[1] |

네트워크 활동 이벤트에서 VPC 끝점 정책 때문에 거부되면 `errorCode` 는 `VpceAccessDenied` 이고 `errorMessage` 는 늘 `The request was denied due to a VPC endpoint policy` 입니다[1].

## userIdentity

`userIdentity.type` 은 요청한 주체의 종류입니다. 값은 `Root`, `IAMUser`, `AssumedRole`, `Role`, `FederatedUser`, `Directory`, `AWSAccount`, `AWSService`, `IdentityCenterUser`, `Unknown` 이고, SAML·웹 ID 페더레이션으로 부른 STS API 에는 `SAMLUser`·`WebIdentityUser` 가 나옵니다[2]. `AWSAccount` 와 `AWSService` 는 내 계정의 역할을 다른 계정이나 AWS 서비스가 넘겨받았을 때 역할을 가진 쪽 로그에 나옵니다[2].

`userName` 이 있는지는 `type` 에 따라 다릅니다. `Root` 는 계정 별칭을 정했으면 별칭이 들어가고 없으면 필드 자체가 없으며, 값에 `Root` 라는 글자는 들어가지 않습니다[2]. `AssumedRole` 에는 `userName` 이 없고 역할 이름은 `sessionContext.sessionIssuer.userName` 에 있습니다[2]. 콘솔 로그인이 잘못된 사용자 이름 때문에 실패하면 입력값 대신 `HIDDEN_DUE_TO_SECURITY_REASONS` 가 남습니다[2].

임시 자격 증명으로 한 요청이면 `principalId` 에 세션 이름이 붙어 `AROA...:세션이름` 꼴이 되고, `arn` 은 `arn:aws:sts::계정:assumed-role/역할/세션이름` 꼴이 됩니다[2]. `accessKeyId` 는 요청에 서명한 키 ID 이고 임시 자격 증명이면 임시 키 ID 인데, 보안상 이유로 빠지거나 빈 문자열일 수 있습니다[2]. 키 ID 접두사와 키 수명은 [IAM 사용자·역할·액세스 키](../iam.md)에서 다룹니다.

`sessionContext` 에는 세션을 발급한 주체(`sessionIssuer`: `type`·`principalId`·`arn`·`accountId`·`userName`), 웹 ID 공급자 정보(`webIdFederationData`), 세션 속성(`attributes`: `creationDate`·`mfaAuthenticated`), 원래 사용자를 가리키는 `sourceIdentity`, 로그인 세션 ARN(`signInSessionArn`, `arn:aws:signin:리전:계정:session/UUID` 꼴), 관리 계정이나 위임된 관리자가 STS 로 연 루트 임시 세션 표시(`assumedRoot`), EC2 인스턴스 메타데이터 서비스가 준 자격 증명의 판(`ec2RoleDelivery`: IMDSv1 이면 `1.0`, IMDSv2 이면 `2.0`)이 들어갈 수 있습니다[2]. 이 밖에 AWS 서비스가 대신 요청했으면 `invokedBy`, 제품 공급자가 위임받은 권한으로 요청했으면 `invokedByDelegate.accountId`, IAM Identity Center 사용자를 대신한 요청이면 `onBehalfOf`(`userId`·`identityStoreArn`)가 붙습니다[2].

### 교차 계정 이벤트

한 작업이 두 계정에 걸치면 두 계정이 따로 레코드를 받습니다. 두 레코드는 `sharedEventID` 가 같고 `eventID` 와 `recipientAccountId` 는 서로 다릅니다[1]. 호출한 계정과 리소스 소유 계정이 같으면 레코드가 하나뿐이라 `sharedEventID` 가 없습니다[1]. 다른 계정이 내 역할을 넘겨받은 `AssumeRole` 레코드를 역할 쪽 계정에서 보면 `userIdentity.type` 이 `AWSAccount` 이고 `principalId`·`accountId` 가 남습니다[2].

## 증거로서 의미

**증명하는 것.** 이 자격 증명(키 ID 나 역할 세션)으로 이 API 를 이 시각에 호출했다는 것, 요청이 이 IP 주소와 이 User-Agent 로 왔다는 것, 호출이 성공했는지 어떤 오류로 실패했는지를 보여 줍니다[1][2]. 쓰기 작업이면 `requestParameters` 와 `responseElements` 로 무엇을 바꾸려 했고 결과가 어땠는지도 보입니다[1].

**증명하지 못하는 것.** 레코드는 자격 증명을 가리킬 뿐 사람을 가리키지 않습니다. 같은 키나 역할을 여러 사람이 쓸 수 있고, `sourceIdentity`·세션 이름·`signInSessionArn` 이 있으면 범위를 좁힐 수 있습니다[2]. `sourceIPAddress` 는 콘솔 작업이나 서비스 호출에서 사용자 단말 주소가 아닐 수 있습니다[1]. 읽기 작업은 `responseElements` 가 `null` 이라 무엇을 돌려받았는지 남지 않고, 100KB 를 넘는 매개변수와 응답은 내용이 빠집니다[1]. 보고서에는 "이 시각에 이 역할 세션으로 `StopInstances` 를 호출한 기록이 있다" 처럼 레코드가 말하는 만큼만 씁니다.

## 시각 해석

`eventTime` 은 요청이 끝난 시각이고 UTC 로 `YYYY-MM-DDTHH:MM:SSZ` 꼴로 적힙니다[1][3]. 이 값은 API 엔드포인트를 돌리는 AWS 호스트의 시계에서 오고, AWS 서비스는 대개 NTP 로 시계를 맞춥니다[1]. 레코드가 파일로 전달되는 시각은 이와 따로 움직이고, 전달 지연은 [트레일과 이벤트 기록](./trails.md)에서 다룹니다.

`sessionContext.attributes.creationDate` 는 임시 자격 증명을 발급한 시각입니다. 필드 설명은 ISO 8601 기본 표기(`20131102T010628Z`)라고 하지만 로그 예시에는 확장 표기(`2023-07-19T21:11:57Z`)도 나오므로 두 꼴을 모두 읽도록 파서를 짭니다[2][3]. 같은 세션의 레코드를 `creationDate` 로 묶으면 세션이 언제 열렸는지 알 수 있습니다.

`responseElements` 안의 시각은 서비스 응답을 그대로 옮긴 것이라 형식이 다릅니다. `CreateUser` 응답의 `createDate` 는 `Jul 19, 2023 9:25:09 PM`, `AssumeRole` 응답의 `credentials.expiration` 은 `Jan 22, 2021 12:46:28 AM` 처럼 시간대 표시가 없는 문자열입니다[2][3]. 이 값은 타임라인에 바로 넣지 말고 `eventTime` 과 견줘 어느 시간대인지 확인한 뒤 씁니다. 시간대를 다루는 공통 원칙은 [클라우드 로그의 시각](../../../01-foundations/logging/timestamps.md)에 있습니다.

## 함정과 한계

- **중복 레코드.** 드물게 로그 파일에 같은 이벤트가 두 번 들어가고, 대개 `eventID` 가 같습니다[5]. 건수를 셀 때는 `eventID` 로 중복을 걷어 냅니다.
- **순서.** 파일 안의 레코드 순서에는 뜻이 없습니다[4]. 파일 이름의 시각은 전달 시각이고 그 파일에는 그 전 어느 때의 레코드든 들어갈 수 있어서[3] `eventTime` 으로 정렬합니다.
- **성공 판정.** 성공한 호출에는 `errorCode` 가 아예 없습니다[1]. Sigma 의 S3 버킷 삭제 탐지 규칙은 성공한 호출을 `errorCode: 'Success'` 와 `errorCode: null` 두 조건으로 함께 잡습니다[6]. 직접 걸러 낼 때도 "필드가 없음" 을 성공으로 보도록 조건을 짭니다.
- **나중에 붙는 내용.** 전달이 늦었거나 빠진 값을 나중에 채우면 `addendum` 이 붙습니다. `reason` 은 `DELIVERY_DELAY`, `UPDATED_DATA`, `SERVICE_OUTAGE` 가운데 하나이고, `UPDATED_DATA` 일 때는 `updatedFields`·`originalRequestID`·`originalEventID` 로 원래 레코드를 가리킵니다[1].
- **잘린 필드.** Lake 이벤트 데이터 저장소는 최대 이벤트 크기를 256KB 에서 1MB 로 늘릴 수 있고, 1MB 를 넘으면 `annotation` → `requestID` → `additionalEventData` → `serviceEventDetails` → `userAgent` → `errorCode` → `eventContext` → `responseElements` → `requestParameters` → `errorMessage` 순서로 자릅니다[1]. 트레일 사본과 Lake 사본의 같은 이벤트가 길이가 다르면 이 차이일 가능성이 있습니다.
- **가려진 값.** 민감한 응답 값은 `<sensitiveDataRemoved>` 로 바뀌어 남습니다(예: `CreateKeyPair` 의 `keyMaterial`)[3]. `accessKeyId` 가 빈 문자열인 레코드도 있습니다[2].

## 직접 분석해 보기

**원본 파일 한 개.** S3 에서 받은 `.json.gz` 파일을 풀면 `{"Records": [` 로 시작하는 JSON 이 나옵니다[3]. jq 로 레코드를 한 줄에 하나씩 펼치고 필요한 필드만 뽑습니다.

```sh
gzip -dc 123456789012_CloudTrail_ap-northeast-2_20260901T0215Z_EXAMPLE0123456AB.json.gz \
  | jq -c '.Records[] | {eventTime, eventID, eventSource, eventName,
      type: .userIdentity.type, arn: .userIdentity.arn,
      key: .userIdentity.accessKeyId, ip: .sourceIPAddress, errorCode}' \
  | sort
```

`sort` 는 줄 맨 앞의 `eventTime` 으로 정렬하려고 붙였습니다. 여러 파일을 합칠 때는 `eventID` 로 중복을 먼저 걷어 냅니다. 파일 이름은 만든 예시입니다.

**많은 파일.** 버킷에 쌓인 로그 전체를 볼 때는 Athena 로 S3 의 로그 파일을 옮기지 않고 SQL 로 조회할 수 있습니다. 테이블은 CloudTrail 콘솔에서 만들거나 Athena 콘솔에서 수동 파티션·파티션 프로젝션으로 만들고, 조직 트레일용 방법도 따로 있습니다[7]. 수집 절차는 [AWS·Azure·GCP 수집](../../../03-techniques/acquisition/iaas-collection.md)에, 탐지 규칙으로 훑는 방법은 [탐지 규칙으로 로그 훑기](../../../03-techniques/analysis/detection-rules.md)에 있습니다.

## 교차 검증

- 같은 `sharedEventID` 를 가진 다른 계정의 레코드로 교차 계정 작업의 양쪽을 맞춥니다[1].
- `AssumeRole` 응답의 `responseElements.credentials.accessKeyId` 로 그 뒤 임시 키 호출을 이어 붙입니다[2]. 방법은 [IAM 사용자·역할·액세스 키](../iam.md)에 있습니다.
- `sourceIPAddress`·`userAgent` 해석은 [IP·사용자 에이전트·위치 정보](../../../01-foundations/logging/ip-ua-geo.md)를, 여러 로그를 시간순으로 합치는 방법은 [클라우드 타임라인](../../../03-techniques/analysis/timeline.md)을 봅니다.
- JSON 로그를 읽는 일반 원칙은 [JSON 로그 읽기](../../../01-foundations/logging/json-logs.md)에 있습니다.

## 참고 문헌

1. AWS, "CloudTrail record contents for management, data, and network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
2. AWS, "CloudTrail userIdentity element", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
3. AWS, "CloudTrail log file examples", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-examples.html
4. AWS, "CloudTrail concepts", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-concepts.html
5. AWS, "Getting and viewing your CloudTrail log files", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/get-and-view-cloudtrail-log-files.html
6. SigmaHQ, aws_cloudtrail_bucket_deleted.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_bucket_deleted.yml
7. AWS, "Query AWS CloudTrail logs", Amazon Athena User Guide. https://docs.aws.amazon.com/athena/latest/ug/cloudtrail-logs.html
