---
title: "IAM 사용자·역할·액세스 키"
parent: "아티팩트 · AWS"
nav_order: 390
---

# IAM 사용자·역할·액세스 키 (IAM)

AWS 계정 안에 어떤 사용자와 역할이 있고, 어떤 자격 증명이 언제 마지막으로 쓰였으며, 누가 어느 역할을 넘겨받아 무엇을 했는지를 IAM 자격 증명 보고서·마지막 접근 정보·CloudTrail 기록으로 이어 붙이는 쪽입니다.

## 무엇을 기록하나 · 왜 생기나

AWS 의 호출은 모두 자격 증명 하나에 묶여 있습니다. 자격 증명은 IAM 사용자 (IAM user)·루트 사용자 (root user) 가 쓰는 장기 자격 증명과, 역할 (role) 을 넘겨받거나 STS 를 불러 받는 임시 자격 증명으로 나뉩니다. 액세스 키 (access key) 는 IAM 사용자나 루트 사용자의 장기 자격 증명이고, 액세스 키 ID 와 비밀 액세스 키 두 부분으로 되어 있습니다[5]. 비밀 액세스 키는 만들 때만 받아 볼 수 있고, 사용자 한 명에게 액세스 키를 두 개까지 만들 수 있습니다[5].

조사에 쓰는 기록은 세 갈래입니다. 자격 증명 보고서 (credential report) 는 계정의 모든 사용자와 그 비밀번호·액세스 키·MFA 상태를 CSV 한 장에 담습니다[1]. 마지막 접근 정보 (last accessed information) 는 사용자·역할·그룹·정책별로 어느 서비스와 어느 관리 작업에 마지막으로 접근을 시도했는지 보여 줍니다[3]. CloudTrail 은 IAM 과 STS 에 들어온 인증된 요청을 모두 기록하고, 다른 서비스 호출에도 요청한 자격 증명을 `userIdentity` 에 남깁니다[4]. 앞의 둘은 "지금 어떤 상태인가" 를 보여 주는 요약이고, 무엇을 언제 어디서 했는지는 CloudTrail 에서 읽습니다. 사용자·역할·임시 자격 증명의 일반 개념은 [클라우드 계정과 역할](../../01-foundations/identity/users-roles.md) 과 [토큰과 세션](../../01-foundations/identity/tokens-sessions.md) 에서 다룹니다.

## 위치와 버전별 차이

| 기록 | 얻는 곳 | 보관·갱신 | 알려 주는 것 |
|---|---|---|---|
| 자격 증명 보고서 | IAM 콘솔 → Credential report → Download Report, 또는 `aws iam generate-credential-report` 로 만들고 `aws iam get-credential-report` 로 받음[1] | 4시간에 한 번 만들 수 있고, 4시간 안에 다시 요청하면 이전 보고서를 줌. 계정에 보고서 하나만 두고 새로 만들면 덮어씀[1] | 사용자별 비밀번호·액세스 키 2개·MFA·X.509 인증서 상태와 마지막 사용 |
| 마지막 접근 정보 | IAM 콘솔, 또는 API `GenerateServiceLastAccessedDetails`·`GetServiceLastAccessedDetails`[3] | 콘솔 반영은 4시간 안. 서비스 정보는 최소 400일 추적[3] | 서비스·관리 작업별 마지막 접근 시도 시각 |
| CloudTrail 의 IAM·STS·로그인 이벤트 | 이벤트 기록·트레일·Lake ([CloudTrail](cloudtrail/index.md)) | CloudTrail 저장소마다 다름 ([트레일과 이벤트 기록](cloudtrail/trails.md)) | 누가 어떤 자격 증명으로 무엇을 언제 어디서 호출했나 |

자격 증명 보고서를 받으려면 `iam:GenerateCredentialReport` 와 `iam:GetCredentialReport` 권한이 필요합니다[1]. 마지막 접근 정보는 만든 주체만 내용을 볼 수 있고, 역할이나 STS 페더레이션 사용자의 임시 자격 증명으로 만들었다면 같은 세션 안에서 받아야 합니다[3].

기록이 시작된 날짜가 항목마다 달라서, 오래된 계정을 볼 때는 아래 표와 맞춰 봐야 합니다(2026년 9월 문서 기준).

| 항목 | 추적 시작 | 비고 |
|---|---|---|
| 자격 증명 보고서 `password_last_used` | 2014년 10월 20일[1] | 2018년 5월 3일 22:50 PDT ~ 5월 23일 14:08 PDT 사이 사용은 서비스 문제로 빠져 있음[1] |
| 자격 증명 보고서 `access_key_N_last_used_*` | 2015년 4월 22일[1] | 빠진 기간 없음[1] |
| 마지막 접근 정보 — S3 관리 작업 | 2020년 4월 12일[3] | |
| 마지막 접근 정보 — EC2·IAM·Lambda 관리 작업 | 2021년 4월 7일[3] | |
| 마지막 접근 정보 — 나머지 서비스 관리 작업 | 2023년 5월 23일[3] | 리전의 추적 시작이 더 늦으면 그 날부터[3] |

## 구조

### 고유 ID 접두사와 ARN

IAM 은 사용자·그룹·역할·정책 같은 자원을 만들 때 고유 ID 를 붙이고, 앞 네 글자로 자원 종류를 나타냅니다[2]. 같은 이름으로 사용자를 지웠다가 다시 만들어도 고유 ID 는 달라지므로, 이름이 같은 두 사용자를 가를 때 이 값을 씁니다[2]. 고유 ID 는 IAM 콘솔에 나오지 않고 `get-user`·`get-role`·`get-caller-identity` 같은 명령으로 얻습니다[2]. 접두사는 만든 시기에 따라 다를 수 있습니다[2].

| 접두사 | 자원 | 접두사 | 자원 |
|---|---|---|---|
| AIDA | IAM 사용자 | AKIA | 액세스 키 |
| AROA | 역할 | ASIA | 임시(STS) 액세스 키 |
| AGPA | 사용자 그룹 | AIPA | EC2 인스턴스 프로파일 |
| ANPA | 관리형 정책 | ANVA | 관리형 정책의 버전 |
| APKA | 공개 키 | ASCA | 인증서 |
| ABIA | STS 서비스 베어러 토큰 | ACCA | 컨텍스트별 자격 증명 |

ASIA 로 시작하는 키 ID 는 비밀 액세스 키·세션 토큰과 함께일 때만 유일합니다[2]. ARN 은 `arn:partition:service:region:account:resource` 형식이고, IAM 자원은 region 칸이 비어 있으며, 중국(베이징) 리전의 partition 은 `aws-cn` 입니다[2].

### 자격 증명 보고서의 열

보고서는 CSV 이고 열 순서는 아래와 같습니다[1]. 시각 값은 ISO 8601 형식입니다[1].

| 열 | 뜻 |
|---|---|
| `user`, `arn` | 사용자 이름과 ARN |
| `user_creation_time` | 사용자를 만든 시각 |
| `password_enabled` | 비밀번호가 있으면 `TRUE` |
| `password_last_used` | 비밀번호로 AWS 웹 사이트(콘솔·토론 포럼·Marketplace)에 마지막으로 로그인한 시각. 5분 안에 여러 번 쓰면 첫 번째만 남음. 쓴 적이 없거나 추적을 시작한 2014년 10월 20일 뒤로 쓴 적이 없으면 `no_information`, 비밀번호가 없으면 `N/A` |
| `password_last_changed` | 비밀번호를 마지막으로 정한 시각 |
| `password_next_rotation` | 비밀번호 정책상 다음 교체 시각. 루트는 항상 `not_supported` |
| `mfa_active` | MFA 장치를 켰으면 `TRUE` |
| `access_key_1_active` | 첫 번째 키가 Active 이면 `TRUE` |
| `access_key_1_last_rotated` | 첫 번째 키를 만들거나 마지막으로 바꾼 시각 |
| `access_key_1_last_used_date` | 첫 번째 키로 마지막으로 API 요청에 서명한 시각. 15분 안에 여러 번 쓰면 첫 번째만 남음 |
| `access_key_1_last_used_region` | 그때의 리전. S3 처럼 리전과 무관한 서비스면 `N/A` |
| `access_key_1_last_used_service` | 그때의 서비스 네임스페이스(예: `s3`, `ec2`) |
| `access_key_2_*` | 두 번째 키의 같은 다섯 열 |
| `cert_1_active`, `cert_1_last_rotated`, `cert_2_active`, `cert_2_last_rotated` | X.509 서명 인증서 상태 |
| `additional_credentials_info` | 키나 인증서가 두 개를 넘을 때 그 개수와 목록을 볼 작업 |

보고서에는 비밀번호·사용자별 처음 두 개의 액세스 키·MFA 장치·X.509 서명 인증서만 들어갑니다[1]. CodeCommit 비밀번호, Amazon Bedrock 장기 API 키, CloudWatch Logs 장기 API 키 같은 서비스별 자격 증명과 세 번째 이후 키는 빠지므로 `ListServiceSpecificCredentials`·`ListAccessKeys` 로 따로 확인합니다[1].

### CloudTrail 의 `userIdentity`

CloudTrail 레코드 전체 구조와 `userIdentity` 의 모든 필드는 [레코드 구조](cloudtrail/record-structure.md) 에서 다룹니다. 이 쪽에서는 IAM 조사에 바로 쓰는 값만 추립니다.

| `userIdentity.type` | 뜻 | 사람을 가리키는 값이 있는 곳 |
|---|---|---|
| `Root` | 계정 루트 자격 증명[7] | 계정 별칭을 정했으면 `userName` 이 별칭, 아니면 `userName` 없음[7] |
| `IAMUser` | IAM 사용자 자격 증명[7] | `userName`, `principalId`(AIDA…), `accessKeyId`(AKIA…) |
| `AssumedRole` | AssumeRole 로 받은 임시 자격 증명[7] | `userName` 없음. 역할 이름은 `sessionContext.sessionIssuer.userName`, 세션 이름은 `arn` 끝과 `principalId` 의 콜론 뒤[7] |
| `FederatedUser` | GetFederationToken 으로 받은 임시 자격 증명[7] | `sessionContext.sessionIssuer` 가 루트인지 IAM 사용자인지 알려 줌[7] |
| `AWSAccount`, `AWSService` | 다른 계정 또는 AWS 서비스가 이 계정의 역할을 넘겨받음[7] | 역할 소유 계정 쪽 레코드에는 호출 계정 번호와 (사용자면) `principalId`, 서비스면 서비스 주체만 남음[4] |

`sessionContext.attributes.mfaAuthenticated` 는 루트나 IAM 사용자가 MFA 로 인증했을 때 `true` 입니다[7]. IAM 사용자가 MFA 로 로그인한 뒤 역할을 넘겨받으면 그 역할로 한 작업에도 `mfaAuthenticated: true` 가 남습니다[4]. `sessionContext.sourceIdentity` 는 역할을 넘겨받은 원래 사용자를 가리키고, 역할을 이어서 넘겨받아도 유지됩니다[7][4]. EC2 인스턴스 메타데이터 서비스에서 받은 자격 증명이면 `sessionContext.ec2RoleDelivery` 가 `1.0`(IMDSv1) 또는 `2.0` 입니다[7].

### AssumeRole 레코드

임시 자격 증명을 만드는 STS API 는 읽기 전용 여부와 상관없이 `responseElements` 를 남깁니다. `AssumeRole`·`AssumeRoleWithSAML`·`AssumeRoleWithWebIdentity` 는 `readOnly` 가 `true` 인데도 비밀 액세스 키만 빼고 응답 전체를 기록합니다[4]. 그래서 응답 안의 새 임시 키 ID(ASIA…)로 그 뒤 호출을 이어 붙일 수 있습니다. 아래는 만든 예시입니다.

```json
{
  "eventVersion": "1.08",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "AIDACKCEVSQ6C2EXAMPLE",
    "arn": "arn:aws:iam::123456789012:user/dev-kim",
    "accountId": "123456789012",
    "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
    "userName": "dev-kim"
  },
  "eventTime": "2026-09-01T02:10:05Z",
  "eventSource": "sts.amazonaws.com",
  "eventName": "AssumeRole",
  "awsRegion": "us-east-1",
  "sourceIPAddress": "203.0.113.10",
  "userAgent": "aws-cli/2.x",
  "requestParameters": {
    "roleArn": "arn:aws:iam::123456789012:role/ops-admin",
    "roleSessionName": "dev-kim-ops",
    "sourceIdentity": "dev-kim"
  },
  "responseElements": {
    "credentials": {
      "accessKeyId": "ASIAIOSFODNN7EXAMPLE",
      "expiration": "Sep 1, 2026, 3:10:05 AM",
      "sessionToken": "(생략)"
    },
    "assumedRoleUser": {
      "assumedRoleId": "AROADBQP57FF2AEXAMPLE:dev-kim-ops",
      "arn": "arn:aws:sts::123456789012:assumed-role/ops-admin/dev-kim-ops"
    },
    "sourceIdentity": "dev-kim"
  },
  "readOnly": true,
  "eventType": "AwsApiCall",
  "recipientAccountId": "123456789012"
}
```

다른 계정의 역할을 넘겨받으면 같은 요청이 호출 계정과 역할 계정 양쪽에 남습니다. 호출 계정 쪽은 `userIdentity.type` 이 `IAMUser`, 역할 계정 쪽은 `AWSAccount` 이고, 두 레코드의 `sharedEventID` 가 같습니다[4]. 넘겨받은 역할로 이어서 호출하면 그 레코드에는 역할 정보만 남고 사용자는 남지 않습니다[4]. 역할 세션 시간은 `DurationSeconds` 로 정하고, 900초부터 역할에 설정한 최대 세션 시간(1~12시간)까지 쓸 수 있으며 기본값은 3600초입니다[6]. 역할을 이어서 넘겨받는 역할 체이닝 (role chaining) 세션은 최대 1시간입니다[6].

### 콘솔 로그인 레코드

콘솔 로그인은 `eventSource` 가 `signin.amazonaws.com`, `eventName` 이 `ConsoleLogin` 이고, 성패는 `responseElements.ConsoleLogin` 의 `Success`·`Failure` 로 남습니다[8]. `additionalEventData` 에는 `LoginTo`, `MobileVersion`, `MFAUsed`(`Yes`·`No`), MFA 를 썼을 때 `MFAIdentifier` 가 들어갑니다[8]. 로그인 중 MFA 확인은 `CheckMfa` 이벤트로 따로 남고 `additionalEventData.MfaType` 에 `Virtual MFA`, `Multiple MFA Devices` 같은 값이 들어갑니다[8]. 페더레이션 사용자는 `mfaAuthenticated` 가 `false`, `MFAUsed` 가 `No` 이고, 이 값이 `true`·`Yes` 가 되는 것은 IAM 사용자나 루트가 MFA 를 썼을 때뿐입니다[8].

로그인 실패 레코드는 원인에 따라 모양이 다릅니다. 비밀번호가 틀리면 `errorMessage` 가 `Failed authentication` 이고 `userName` 이 남습니다[8]. 없는 사용자 이름을 넣으면 입력한 이름 대신 `HIDDEN_DUE_TO_SECURITY_REASONS` 가 남고 `errorMessage` 는 `No username found in supplied account` 입니다[4]. IAM 사용자 로그인 실패 레코드에는 `userIdentity.arn` 이 없는 예시[8][4]와 있는 예시[4]가 모두 있으므로, 성패는 `arn` 유무가 아니라 `responseElements.ConsoleLogin` 으로 가립니다.

## 증거로서 의미

**증명하는 것**

- 자격 증명 보고서는 보고서를 만든 시점에 사용자가 있었고, 키가 Active 였으며, 마지막으로 쓰인 날짜·리전·서비스가 무엇이었는지를 보여 줍니다[1].
- 마지막 접근 정보는 그 주체가 그 서비스나 관리 작업에 접근을 시도한 적이 있다는 것을 보여 줍니다[3].
- CloudTrail 의 `userIdentity` 는 어떤 자격 증명(키 ID·역할 세션)으로 호출했는지를 보여 주고, AssumeRole 레코드는 어느 사용자가 어느 역할을 어느 세션 이름으로 넘겨받았는지를 보여 줍니다[4].

**증명하지 못하는 것**

- 자격 증명 보고서는 키로 무엇을 했는지, 어느 IP 에서 썼는지, 몇 번 썼는지 알려 주지 않으니, 그건 CloudTrail 에서 확인합니다.
- 마지막 접근 정보는 성공 여부를 알려 주지 않습니다. 거부된 시도도 포함하므로, 이 정보에 뜻밖의 항목이 있다고 계정이 침해됐다고 볼 수는 없고 호출의 성공·거부는 CloudTrail 로 확인합니다[3].
- 키 ID 나 역할 세션은 사람과 같지 않습니다. 키를 여러 사람이 나눠 쓰거나 역할을 여러 사람이 넘겨받을 수 있어서, `sourceIdentity` 나 세션 이름을 사람과 묶는 규칙이 있을 때만 사람을 좁힐 수 있습니다[4].
- `mfaAuthenticated: false` 는 MFA 없이 인증했다는 뜻일 수도 있고, 페더레이션 사용자처럼 이 값을 `true` 로 쓰지 않는 경로라는 뜻일 수도 있습니다[8].

보고서에는 "2026년 9월 1일 02:10 UTC 에 액세스 키 AKIAIOSFODNN7EXAMPLE 로 역할 ops-admin 을 세션 이름 dev-kim-ops 로 넘겨받은 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다(만든 예시).

## 시각 해석

| 값 | 바뀌는 때 | 형식·시간대 |
|---|---|---|
| CloudTrail `eventTime` | 요청이 끝난 때 | UTC, `2026-09-01T02:10:05Z` 모양. 자세한 내용은 [레코드 구조](cloudtrail/record-structure.md) |
| `sessionContext.attributes.creationDate` | 임시 자격 증명을 발급한 때[7] | 필드 설명은 ISO 8601 기본 표기(`20131102T010628Z` 모양)[7]인데, IAM 문서의 로그 예시는 `2019-10-02T21:50:54Z` 모양[4]. 두 표기를 모두 읽도록 파싱함 |
| `responseElements.credentials.expiration` | 임시 자격 증명이 끝나는 때 | `Jul 18, 2023, 4:07:39 PM` 같은 문자열이고 시간대 표시가 없음[4]. 타임라인에 그대로 넣지 않음 |
| 보고서 `password_last_used` | 5분 안의 첫 로그인[1] | ISO 8601[1]. 시간대 표시는 받은 CSV 에서 확인 |
| 보고서 `access_key_N_last_used_date` | 15분 안의 첫 서명[1] | ISO 8601[1] |
| 보고서 `access_key_N_last_rotated` | 키를 만들거나 바꾼 때[1] | ISO 8601[1] |
| 마지막 접근 정보 | 접근 시도 때 | 콘솔 반영은 4시간 안[3] |

`last_used_date` 는 15분 안의 첫 사용만 남기므로 마지막 호출 시각이 아니라 "마지막 사용이 시작된 15분 구간의 첫 시각" 에 가깝습니다[1]. 공격자가 키를 한 번 쓴 뒤 15분 안에 계속 쓰면 그 뒤 호출은 이 열에 드러나지 않습니다. 클라우드 로그 시각 전반은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 에서 다룹니다.

## 함정과 한계

- 자격 증명 보고서는 계정에 하나만 남고 새로 만들면 덮어씁니다[1]. 키를 끄거나 지우면 보고서 값도 바뀌므로, 조치하기 전에 보고서를 받아 보존합니다.
- 임시 키(ASIA…)는 세션마다 달라서 같은 사람도 세션마다 다른 키 ID 로 남습니다. AssumeRole 레코드의 `responseElements.credentials.accessKeyId` 로 그 뒤 호출을 이어 붙입니다[4].
- 교차 계정 역할 전환과 AssumeRoot 로 시작한 특권 세션에서 거부된 STS 요청은 대상 계정에 기록되지 않습니다[4]. 역할 계정만 보면 실패한 시도가 보이지 않으므로 호출 계정 쪽 기록도 받습니다.
- `AssumeRoleWithSAML`·`AssumeRoleWithWebIdentity` 는 인증 전 요청도 기록하지만, 너무 형식이 어긋난 요청은 빠질 수 있습니다[4].
- 마지막 접근 정보는 `iam:PassRole` 을 추적하지 않고, 데이터 이벤트에는 작업 정보가 없으며, 인증되지 않은 시도도 뺍니다[3].
- `accessKeyId` 는 보안상 없거나 빈 문자열일 수 있습니다[7]. 콘솔 로그인 레코드는 `accessKeyId` 가 아예 없거나 빈 문자열인 경우가 많습니다[8].
- 콘솔 로그인 이벤트의 리전은 로그인 경로에 따라 달라서, 한 리전만 보면 로그인 기록이 빠집니다[8].

| 로그인 주체·경로 | `ConsoleLogin` 이 남는 리전[8] |
|---|---|
| 루트 사용자 | us-east-1, us-east-2, us-west-2 가운데 하나 |
| IAM 사용자, 전역 엔드포인트, 브라우저에 계정 별칭 쿠키 있음 | us-east-2, eu-north-1, ap-southeast-2 가운데 하나 |
| IAM 사용자, 전역 엔드포인트, 계정 별칭 쿠키 없음 | us-east-1 |
| IAM 사용자, 리전 엔드포인트 | 그 엔드포인트의 리전 |

- `MFAUsed` 값은 문서 예시에서 `Yes`·`No` 인데, SigmaHQ 규칙 aws_cloudtrail_console_login_success_without_mfa 는 `'NO'` 로 찾습니다[8][9]. 검색할 때는 대소문자를 가리지 않게 합니다.

## 직접 분석해 보기

**원본 JSON 을 한 번 직접 읽기.** 트레일이 S3 에 쌓은 CloudTrail 파일은 gzip JSON 이고 `Records` 배열에 레코드가 여러 개 들어 있습니다([레코드 구조](cloudtrail/record-structure.md)). 아래처럼 IAM·STS·로그인 이벤트만 골라 시각 순서로 펼쳐 봅니다.

```bash
zcat *.json.gz | jq -c '.Records[]
  | select(.eventSource=="iam.amazonaws.com" or .eventSource=="sts.amazonaws.com" or .eventSource=="signin.amazonaws.com")
  | [.eventTime, .eventName, .userIdentity.type, .userIdentity.arn, .userIdentity.accessKeyId, .sourceIPAddress, .errorCode]' \
  | sort
```

특정 임시 키가 어디서 나왔는지 거꾸로 찾으려면 AssumeRole 응답의 키 ID 로 거릅니다.

```bash
zcat *.json.gz | jq -c '.Records[]
  | select(.eventName=="AssumeRole" and .responseElements.credentials.accessKeyId=="ASIAIOSFODNN7EXAMPLE")
  | [.eventTime, .userIdentity.arn, .requestParameters.roleArn, .requestParameters.roleSessionName, .sourceIPAddress]'
```

**자격 증명 보고서 읽기.** 콘솔에서 받은 CSV 는 열 순서가 정해져 있으므로 필요한 열만 잘라 봅니다. 아래는 사용자·비밀번호 마지막 사용·MFA·첫 번째 키 상태와 마지막 사용 열(1, 5, 8, 9, 11, 12, 13번째)을 고르는 예입니다. 첫 줄의 열 이름이 위 표와 같은지 먼저 확인하고, 시각 값의 시간대 표시도 이 출력에서 확인합니다.

```bash
cut -d, -f1,5,8,9,11,12,13 credential_report.csv
```

MFA 가 꺼진 사용자, 비밀번호가 없는데 키만 쓰이는 사용자, 사고 시각 근처에 `last_used_date` 가 찍힌 키를 먼저 뽑아 CloudTrail 에서 그 키 ID 로 다시 찾습니다.

**탐지 규칙으로 훑기.** SigmaHQ 의 AWS CloudTrail 규칙에는 IAM 흔적을 찾는 조건이 필드 이름 그대로 들어 있습니다. 규칙을 쓰는 방법은 [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md) 에서 다룹니다.

| 규칙 | 조건 | 찾는 흔적 |
|---|---|---|
| aws_iam_backdoor_users_keys[10] | `iam.amazonaws.com` 의 `CreateAccessKey` 에서 `userIdentity.arn` 이 `responseElements.accessKey.userName` 을 포함하지 않음 | 다른 사용자의 액세스 키를 만듦 |
| aws_update_login_profile[11] | `UpdateLoginProfile` 에서 `userIdentity.arn` 이 `requestParameters.userName` 과 다름 | 다른 사용자의 콘솔 비밀번호를 바꿈 |
| aws_sts_getsessiontoken_misuse[12] | `sts.amazonaws.com` 의 `GetSessionToken` 이고 `userIdentity.type` 이 `IAMUser` | IAM 사용자 키로 임시 자격 증명을 받음 |
| aws_sts_assumerole_misuse[13] | `userIdentity.type` 이 `AssumedRole` 이고 `userIdentity.sessionContext.sessionIssuer.type` 이 `Role` | 역할 세션으로 한 호출. 관리자·자동화 도구의 정상 호출도 걸리므로 사용자·User-Agent 로 걸러 봄[13] |
| aws_root_account_usage[14] | `userIdentity.type` 이 `Root` 이고 `eventType` 이 `AwsServiceEvent` 가 아님 | 루트 자격 증명 사용 |
| aws_cloudtrail_console_login_failed_authentication[15] | `ConsoleLogin` 이고 `errorMessage` 가 `Failed authentication` | 콘솔 로그인 실패 |

## 교차 검증

- [CloudTrail](cloudtrail/index.md) — 보고서의 `last_used_date` 근처 시각에 같은 키 ID 로 남은 호출과 `sourceIPAddress`·`userAgent` 를 확인합니다. 읽기·쓰기 이벤트 구분은 [관리 이벤트와 데이터 이벤트](cloudtrail/event-types.md) 에서 다룹니다.
- [GuardDuty](guardduty.md) — IAM 사용자·루트 자격 증명 사용이나 인스턴스 자격 증명 유출을 다룬 결과가 있는지 봅니다.
- [EC2 인스턴스와 스냅숏](ec2-ebs.md) — `ec2RoleDelivery` 가 있는 역할 세션이면 어느 인스턴스의 역할이었는지 확인합니다.
- [페더레이션과 SSO](../../01-foundations/identity/federation-sso.md), [다단계 인증과 조건부 접근](../../01-foundations/identity/mfa-conditional-access.md) — SAML·OIDC 로 들어온 역할 세션과 MFA 값을 해석할 때 봅니다.
- [IAM과 서비스 계정 키](../gcp/iam-keys.md) — Google Cloud 의 같은 역할을 하는 기록입니다.
- [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md), [액세스 키가 새어 나갔나](../../04-scenarios/infrastructure/leaked-keys.md), [권한을 올렸나](../../04-scenarios/infrastructure/privilege-escalation.md) — 이 쪽의 기록을 조사 흐름으로 묶습니다.
- 수집 순서는 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md) 과 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 를 따릅니다.

## 실습

위의 만든 예시 AssumeRole 레코드와 자격 증명 보고서의 열 설명으로 풀어 봅니다.

1. 예시 AssumeRole 레코드에서 역할을 넘겨받은 사용자, 역할, 세션 이름, 새 임시 키 ID 를 각각 어느 필드에서 읽는지 적어 봅니다.
2. 같은 세션으로 한 뒤 호출은 `userIdentity.type`·`arn`·`principalId` 가 어떤 값일지 적어 봅니다.
3. 보고서에서 `password_enabled` 가 `FALSE` 인데 `access_key_1_last_used_service` 가 `s3` 이고 `access_key_1_last_used_region` 이 `N/A` 인 사용자가 있다면, 리전이 `N/A` 인 까닭과 이 키가 무엇을 했는지 확인하려면 어디를 봐야 하는지 적어 봅니다.
4. 예시 `expiration` 값을 UTC 타임라인에 넣으려면 무엇을 확인해야 하는지 적어 봅니다.
5. 실제 검체에서는 자기 계정의 자격 증명 보고서를 받아 MFA 가 꺼진 사용자와 90일 넘게 쓰이지 않은 키를 골라 보고, 2018년 5월 공백 구간이 결과에 영향을 주는지 확인합니다.

## 참고 문헌

1. AWS, "Generate credential reports for your AWS account", IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_getting-report.html
2. AWS, "IAM identifiers", IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html
3. AWS, "Refine permissions in AWS using last accessed information", IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_last-accessed.html
4. AWS, "Logging IAM and AWS STS API calls with AWS CloudTrail", IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/cloudtrail-integration.html
5. AWS, "Manage access keys for IAM users", IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
6. AWS, "AssumeRole", AWS Security Token Service API Reference. https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html
7. AWS, "CloudTrail userIdentity element", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
8. AWS, "AWS Management Console sign-in events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-aws-console-sign-in-events.html
9. SigmaHQ, aws_cloudtrail_console_login_success_without_mfa.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_console_login_success_without_mfa.yml
10. SigmaHQ, aws_iam_backdoor_users_keys.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_iam_backdoor_users_keys.yml
11. SigmaHQ, aws_update_login_profile.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_update_login_profile.yml
12. SigmaHQ, aws_sts_getsessiontoken_misuse.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_sts_getsessiontoken_misuse.yml
13. SigmaHQ, aws_sts_assumerole_misuse.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_sts_assumerole_misuse.yml
14. SigmaHQ, aws_root_account_usage.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_root_account_usage.yml
15. SigmaHQ, aws_cloudtrail_console_login_failed_authentication.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_console_login_failed_authentication.yml
