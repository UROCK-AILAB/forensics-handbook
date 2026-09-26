---
title: "Lambda·컨테이너 서비스 기록"
parent: "아티팩트 · AWS"
nav_order: 450
---

# Lambda·컨테이너 서비스 기록 (Lambda·ECS·EKS)

Lambda 함수와 ECS 태스크, EKS 클러스터를 누가 만들고 바꿨는지는 CloudTrail 에 남고, 함수와 컨테이너가 실행 중에 출력한 내용과 Kubernetes 요청 기록은 설정을 켜 둔 경우에만 CloudWatch Logs 에 남습니다.

## 무엇을 기록하나 · 왜 생기나

서버리스 함수와 컨테이너는 실행이 끝나면 실행 환경이 사라지므로, 조사할 때 남은 기록은 대부분 계정 쪽 로그입니다. 기록은 두 층으로 나뉩니다.

첫째 층은 제어 평면 (control plane) 기록입니다. 함수를 만들고 코드를 바꾸고 권한을 붙이는 Lambda API 호출, 서비스·태스크·클러스터를 다루는 ECS API 호출, 클러스터를 만들고 지우는 EKS API 호출은 모두 CloudTrail 관리 이벤트로 남습니다[3][5][7]. 관리 이벤트는 기본으로 기록되고, 트레일이 없어도 이벤트 기록 (Event history) 에서 최근 90일을 볼 수 있습니다[3][5]. CloudTrail 레코드를 읽는 법은 [레코드 구조](cloudtrail/record-structure.md) 에서, 관리 이벤트와 데이터 이벤트의 차이는 [관리 이벤트와 데이터 이벤트](cloudtrail/event-types.md) 에서 다룹니다.

둘째 층은 실행 기록입니다. Lambda 는 실행 역할에 로그 권한이 있으면 모든 호출의 로그를 CloudWatch Logs 로 보냅니다[1]. ECS 컨테이너는 `awslogs` 로그 드라이버를 설정하면 표준 출력과 표준 오류를 CloudWatch Logs 로 보냅니다[4]. EKS 는 제어 평면 로그 다섯 종류를 켠 것만 CloudWatch Logs 로 보내고, 기본으로는 하나도 보내지 않습니다[6]. 이 층은 누군가 켜 두지 않았다면 처음부터 없습니다.

GuardDuty 를 쓰는 계정이면 여기에 탐지 결과가 더해집니다. Lambda Protection 은 VPC 네트워킹을 쓰지 않는 함수까지 모든 Lambda 함수의 흐름 로그를 분석하고[10], EKS Protection 은 계정에 감사 로그를 켜지 않았어도 GuardDuty 자체 스트림으로 EKS 감사 로그를 분석합니다[11]. 보호 계획의 종류와 결과 읽는 법은 [GuardDuty](guardduty.md) 에서 다룹니다.

## 위치와 버전별 차이

### 서비스별 기록과 기본값 (2026년 9월 문서 기준)

| 서비스 | 기록 | 기본 | 남는 곳 | 전달 지연 |
|---|---|---|---|---|
| Lambda | 관리 작업(`CreateFunction20150331` 등) | 켜짐[3] | CloudTrail | [트레일과 이벤트 기록](cloudtrail/trails.md) 참고 |
| Lambda | 함수 실행(`Invoke`) | 꺼짐, 데이터 이벤트·추가 요금[3] | CloudTrail(데이터 이벤트를 켠 트레일·이벤트 데이터 저장소) | 같은 쪽 참고 |
| Lambda | 이벤트 소스 매핑이 Disabled 로 바뀜(`LambdaESMDisabled`) | 켜짐(기본 기록되는 데이터 이벤트)[3] | CloudTrail | 같은 쪽 참고 |
| Lambda | 호출 로그(`START`·`END`·`REPORT` 줄과 코드 출력) | 실행 역할에 `logs:CreateLogGroup`·`logs:CreateLogStream`·`logs:PutLogEvents` 가 있으면 보냄[1] | CloudWatch Logs `/aws/lambda/함수이름`(다른 그룹으로 바꿀 수 있음)[1] | 호출 뒤 5~10분[1] |
| ECS | 제어 평면 작업(`CreateService`·`RunTask`·`DeleteCluster` 등) | 켜짐[5] | CloudTrail | [트레일과 이벤트 기록](cloudtrail/trails.md) 참고 |
| ECS | 컨테이너 인스턴스 작업(`ecs:Poll`·`ecs:StartTelemetrySession`·`ecs:PutSystemLogEvents`) | 꺼짐, 데이터 이벤트·추가 요금[5] | CloudTrail(`AWS::ECS::ContainerInstance`) | 같은 쪽 참고 |
| ECS | 컨테이너 표준 출력·표준 오류 | 태스크 정의에 `awslogs` 드라이버를 설정해야 보냄[4] | CloudWatch Logs(태스크 정의의 `logConfiguration` 이 정한 그룹) | 검체에서 확인 |
| ECS | 태스크 네트워크 흐름 | 흐름 로그 v7 의 `ecs-*` 필드를 넣어야 남음[14] | VPC 흐름 로그 | [VPC 흐름 로그](vpc-flow-logs.md) 참고 |
| EKS | EKS API 호출(`CreateCluster`·`DeleteCluster` 등) | 켜짐[7] | CloudTrail(`eks.amazonaws.com`)[19] | [트레일과 이벤트 기록](cloudtrail/trails.md) 참고 |
| EKS | 제어 평면 로그(api·audit·authenticator·controllerManager·scheduler) | 모두 꺼짐, 종류마다 켬[6] | CloudWatch Logs `/aws/eks/클러스터이름/cluster`[6] | 몇 분 안, 최선 노력[6] |

ECS 컨테이너 로그를 보내는 조건은 실행 방식에 따라 다릅니다. Fargate 에서는 태스크 정의에 `logConfiguration` 파라미터를 넣어 `awslogs` 드라이버를 켜야 합니다[4]. EC2 에서는 컨테이너 인스턴스의 컨테이너 에이전트가 1.9.0 이상이어야 하고, 사용자 지정 AMI 라면 에이전트를 띄울 때 `ECS_AVAILABLE_LOGGING_DRIVERS=["json-file","awslogs"]` 환경 변수로 `awslogs` 를 쓸 수 있게 해 두어야 하며, 인스턴스 역할에 `logs:CreateLogStream`·`logs:PutLogEvents` 권한이 있어야 합니다[4]. ECS 컨테이너 인스턴스 작업의 데이터 이벤트 가운데 `ecs:Poll`·`ecs:StartTelemetrySession` 은 EC2 와 ECS Managed Instances 에서, `ecs:PutSystemLogEvents` 는 ECS Managed Instances 에서만 남습니다[5].

EKS 제어 평면 로그를 켰는지는 콘솔의 클러스터 화면 Observability 탭 Control plane logging 절에서 봅니다[6]. 설정을 바꾼 작업은 `aws eks describe-update` 결과에 `"type": "LoggingUpdate"` 와 켠 종류 목록으로 남으므로[6], 로그가 언제부터 쌓였는지 가늠할 때 씁니다. 로그 그룹의 보관 기간과 삭제 규칙은 [CloudWatch Logs](cloudwatch-logs.md) 에서 다룹니다.

## 구조

### Lambda 호출 로그

Lambda 는 실행 환경 (execution environment) 마다 로그 스트림을 하나씩 만들고, 스트림 이름은 `YYYY/MM/DD[Function version][Execution environment GUID]` 모양입니다[2]. 함수가 동시에 여러 개 실행되면 실행 환경마다 스트림이 따로 생기고, 실행 환경 하나는 살아 있는 동안 같은 스트림에 씁니다[2]. 코드가 아무것도 출력하지 않아도 호출마다 `START`·`END`·`REPORT` 세 줄이 남고, `START` 와 `END` 사이의 줄은 모두 같은 호출에 속합니다[2].

아래는 스트림 하나에서 받은 줄 모양을 흉내 낸 만든 예시입니다. 요청 ID 와 수치는 지어낸 값이고, `REPORT` 줄의 항목은 탭으로 갈라져 있습니다[2].

```text
START RequestId: 3f1c2a9e-7b4d-4e2a-9c61-0d5e8a7b1f20 Version: $LATEST
2026-09-01T03:10:12.481Z	3f1c2a9e-7b4d-4e2a-9c61-0d5e8a7b1f20	INFO	EVENT {"key": "value"}
END RequestId: 3f1c2a9e-7b4d-4e2a-9c61-0d5e8a7b1f20
REPORT RequestId: 3f1c2a9e-7b4d-4e2a-9c61-0d5e8a7b1f20	Duration: 31.52 ms	Billed Duration: 32 ms	Memory Size: 128 MB	Max Memory Used: 74 MB	Init Duration: 180.44 ms
```

| 항목 | 뜻 |
|---|---|
| `RequestId` | 요청마다 새로 만드는 ID. Lambda 가 요청을 재시도하면 ID 가 바뀌지 않고 재시도마다 같은 ID 가 다시 나옴[2] |
| `Version` | 실행한 함수 버전(문서 예시에서는 `$LATEST`)[2] |
| `Duration` | 핸들러 함수를 실행한 시간, INIT 코드는 뺌[2] |
| `Billed Duration` | 요금 계산용으로 올림한 시간[2] |
| `Memory Size` / `Max Memory Used` | 함수에 준 메모리 / 호출 중 가장 많이 쓴 메모리[2] |
| `Init Duration` | 핸들러 밖의 INIT 코드를 실행한 시간[2] |

`Init Duration` 은 새 실행 환경을 만든 호출(콜드 스타트, cold start)의 `REPORT` 줄에 붙고, 콜드 스타트 비율을 세는 Logs Insights 질의도 `REPORT` 줄에 이 문자열이 있는지로 셉니다[2]. 둘째 줄처럼 함수 코드가 남긴 줄의 모양은 런타임과 코드에 따라 달라지므로 검체에서 확인합니다. Logs Insights 로 Lambda 로그를 읽으면 `@timestamp`, `@logStream`, `@message`, `@requestId`, `@duration`, `@billedDuration`, `@type`, `@maxMemoryUsed`, `@memorySize` 필드가 늘 붙고, X-Ray 를 켠 함수면 `@xrayTraceId`·`@xraySegmentId` 가 더 붙습니다[2].

### CloudTrail 의 Lambda 이벤트 이름

Lambda 관리 이벤트는 `eventName` 에 날짜와 판이 붙는 경우가 많고, 이름이 달라도 같은 공개 API 작업을 가리킵니다[3].

| API 작업 | CloudTrail `eventName` | 기록에서 빠지는 파라미터 |
|---|---|---|
| `CreateFunction` | `CreateFunction20150331` | `Environment`, `ZipFile`[3] |
| `UpdateFunctionCode` | `UpdateFunctionCode20150331v2` | `ZipFile`[3] |
| `UpdateFunctionConfiguration` | `UpdateFunctionConfiguration20150331v2` | `Environment`[3] |
| `PublishLayerVersion` | `PublishLayerVersion20181031` | `ZipFile`[3] |
| `AddPermission` / `RemovePermission` | `AddPermission20150331v2` / `RemovePermission20150331v2` | —[3] |
| `CreateEventSourceMapping` / `UpdateEventSourceMapping` | `CreateEventSourceMapping20150331` / `UpdateEventSourceMapping20150331` | —[3] |
| `DeleteFunction` | `DeleteFunction20150331` | —[3] |
| `CreateFunctionUrlConfig`, `GetFunctionUrlConfig`, `ListFunctions` 등 | API 이름 그대로 | —[3] |

`LambdaESMDisabled` 데이터 이벤트는 Amazon SQS·DynamoDB·Kinesis 이벤트 소스 매핑이 오류로 Disabled 상태가 될 때 남고, `serviceEventDetails` 에 `RESOURCE_NOT_FOUND`, `FUNCTION_NOT_FOUND`, `REGION_NAME_NOT_VALID`, `AUTHORIZATION_ERROR`, `FUNCTION_IN_FAILED_STATE` 가운데 하나가 들어갑니다[3]. 사람이 `UpdateEventSourceMapping` 으로 상태를 바꾼 경우는 관리 이벤트로 따로 남으므로[3], 두 기록으로 매핑이 스스로 꺼졌는지 누가 껐는지를 가릅니다.

아래는 역할을 넘겨받은 세션이 함수를 지운 기록을 흉내 낸 만든 예시입니다. 계정·주소·이름·ID 는 모두 지어낸 값이고, 필드 모양은 AWS 문서 예시와 같습니다[3][5].

```json
{
  "eventVersion": "1.09",
  "userIdentity": {
    "type": "AssumedRole",
    "arn": "arn:aws:sts::123456789012:assumed-role/DeployRole/ops-session",
    "accountId": "123456789012",
    "accessKeyId": "ASIAIOSFODNN7EXAMPLE",
    "sessionContext": {
      "sessionIssuer": {
        "type": "Role",
        "arn": "arn:aws:iam::123456789012:role/DeployRole",
        "accountId": "123456789012",
        "userName": "DeployRole"
      }
    }
  },
  "eventTime": "2026-09-01T03:22:40Z",
  "eventSource": "lambda.amazonaws.com",
  "eventName": "DeleteFunction20150331",
  "awsRegion": "us-east-1",
  "sourceIPAddress": "203.0.113.25",
  "userAgent": "aws-cli/2.17.0",
  "requestParameters": { "functionName": "invoice-export" },
  "responseElements": null,
  "requestID": "0b7d4c1e-EXAMPLE",
  "eventID": "5a9e2f3c-EXAMPLE",
  "eventType": "AwsApiCall",
  "recipientAccountId": "123456789012"
}
```

### 함수와 컨테이너가 부른 기록

Lambda 함수나 ECS 태스크가 자기 역할의 자격 증명으로 다른 AWS 서비스를 부르면, 그 서비스의 CloudTrail 레코드 `userIdentity.inScopeOf` 에 요청이 어느 자원에서 나왔는지가 들어갈 수 있습니다[9].

| 속성 | 뜻 |
|---|---|
| `sourceArn` | 서비스 간 요청을 일으킨 자원의 ARN[9] |
| `sourceAccount` | `sourceArn` 을 가진 계정 ID, `sourceArn` 과 함께 나옴[9] |
| `issuerType` | `credentialsIssuedTo` 의 자원 형식, 예 `AWS::Lambda::Function`[9] |
| `credentialsIssuedTo` | 자격 증명을 발급한 실행 환경과 관련된 자원[9] |

`userAgent` 가 `lambda.amazonaws.com` 이면 Lambda 가 한 요청입니다[8]. 역할과 임시 자격 증명을 읽는 법은 [IAM 사용자·역할·액세스 키](iam.md) 와 [토큰과 세션](../../01-foundations/identity/tokens-sessions.md) 에서 다룹니다.

### EKS 제어 평면 로그

| 종류(설정 이름) | 기록하는 것 | 로그 스트림 이름 |
|---|---|---|
| API 서버 (`api`) | Kubernetes API 를 내놓는 API 서버의 로그. 클러스터를 띄울 때나 직후에 켜면 API 서버를 시작한 플래그도 남음[6] | `kube-apiserver-` 뒤에 16진수 문자열[6] |
| 감사 (`audit`) | 클러스터에 영향을 준 사용자·관리자·시스템 구성 요소의 기록(Kubernetes 감사 로그)[6] | `kube-apiserver-audit-` 뒤에 16진수 문자열[6] |
| 인증기 (`authenticator`) | EKS 에만 있는 로그. IAM 자격 증명으로 Kubernetes RBAC 인증을 하는 구성 요소의 기록[6] | `authenticator-` 뒤에 16진수 문자열[6] |
| 컨트롤러 관리자 (`controllerManager`) | Kubernetes 에 딸린 핵심 제어 루프를 관리하는 구성 요소[6] | `kube-controller-manager-` 뒤에 16진수 문자열[6] |
| 스케줄러 (`scheduler`) | 파드를 언제 어디서 돌릴지 정하는 구성 요소[6] | `kube-scheduler-` 뒤에 16진수 문자열[6] |

켠 로그는 상세 수준 (verbosity) 2 로 보냅니다[6]. CloudTrail 이 받는 것은 Amazon EKS API 호출이고[7], 클러스터 안에서 Kubernetes API 로 한 요청은 감사 로그에서, IAM 자격 증명으로 한 인증은 인증기 로그에서 찾습니다[6].

## 증거로서 의미

**증명하는 것.** CloudTrail 관리 이벤트는 어느 주체가 언제 어느 주소에서 함수·태스크 정의·서비스·클러스터를 만들고 바꾸고 지웠는지를 보여 줍니다[3][5][7]. `RegisterTaskDefinition`·`RunTask` 기록의 `requestParameters.containerDefinitions` 에는 컨테이너에 준 명령(`command`)까지 남을 수 있어서, 탐지 규칙도 이 필드를 검사합니다[18]. Lambda 호출 로그는 어느 실행 환경에서 어느 버전이 언제 몇 번 실행됐는지를, `REPORT` 줄과 `RequestId` 로 호출 단위까지 보여 줍니다[2]. EKS 감사 로그를 켜 두었다면 클러스터에 영향을 준 사용자와 구성 요소를 요청 단위로 볼 수 있습니다[6].

**증명하지 못하는 것.** `Invoke` 데이터 이벤트를 켜지 않았다면 CloudTrail 에는 함수를 누가 실행했는지가 없고, 호출 로그에는 실행됐다는 사실만 있고 호출한 주체는 없습니다[2][3]. `CreateFunction`·`UpdateFunctionCode`·`PublishLayerVersion` 기록에는 코드 묶음(`ZipFile`)이 빠지고 `CreateFunction`·`UpdateFunctionConfiguration` 기록에는 환경 변수(`Environment`)가 빠지므로[3], CloudTrail 만으로 어떤 코드를 올렸는지는 알 수 없습니다. 컨테이너 로그에 무엇이 남는지는 대부분 `ENTRYPOINT` 명령에 달려 있고 `awslogs` 드라이버는 기본으로 표준 출력·표준 오류를 넘기므로[4], 컨테이너 안에서 파일을 읽거나 프로세스를 띄운 일은 코드가 출력하지 않는 한 남지 않습니다. 그런 동작은 GuardDuty Runtime Monitoring 에이전트가 있을 때 파일 접근·프로세스 실행·명령줄·네트워크 연결로 보이고, EKS on Fargate 는 이 기능을 지원하지 않습니다[12]. EKS 제어 평면 로그를 켜기 전 기간의 Kubernetes 요청은 계정에 없습니다[6].

보고서에는 "2026-09-01 03:22:40 UTC 에 역할 `DeployRole` 의 세션이 203.0.113.25 에서 함수 `invoice-export` 를 지우는 요청을 했고 오류 없이 기록됐다" 처럼 기록이 말하는 만큼만 씁니다(만든 예시). "함수로 자료를 빼냈다" 같은 문장은 호출 로그나 데이터 이벤트, 흐름 로그로 뒷받침될 때만 씁니다. 문장 쓰는 법은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에서 다룹니다.

## 시각 해석

CloudTrail 의 `eventTime` 은 요청이 끝난 시각이고 UTC 입니다[8]. CloudWatch Logs 이벤트의 `timestamp`·`ingestionTime` 은 1970-01-01 UTC 부터 흐른 밀리초이고, 두 값을 읽는 법은 [CloudWatch Logs](cloudwatch-logs.md) 에서 다룹니다.

Lambda 호출 로그는 함수 코드가 남긴 줄까지 모든 메시지에 시각이 붙습니다[2]. `START` 줄의 시각이 호출이 시작된 때이고, `Duration` 은 INIT 을 뺀 핸들러 실행 시간이라[2] `START` 줄과 `END` 줄의 시각 차이와 같은 값으로 읽지 않습니다. 로그는 호출 뒤 5~10분 지나서야 보일 수 있으므로[1], 사건 직후에 받은 로그에 마지막 호출이 빠져 있을 수 있습니다. 스트림은 실행 환경이 생길 때 만들어지고 실행 환경은 살아 있는 동안 같은 스트림에 쓰므로[2], 날짜가 바뀐 뒤의 호출이 앞날 이름의 스트림에 있을 수 있습니다. 날짜로 스트림을 고를 때는 앞날 스트림도 함께 받습니다.

EKS 제어 평면 로그는 몇 분 안에 전달되지만 최선 노력이라 보장이 없습니다[6]. 여러 로그의 시각을 한 줄로 맞추는 법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 과 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 함정과 한계

- **날짜가 붙은 이벤트 이름.** `eventName = 'UpdateFunctionConfiguration'` 처럼 정확히 맞추면 `UpdateFunctionConfiguration20150331v2` 가 걸리지 않습니다[3]. Sigma 규칙은 `startswith` 로, Invictus-AWS 의 Athena 질의는 `LIKE 'UpdateFunctionConfiguration%'` 로 찾습니다[17][20]. `GetFunction` 은 문서 예시에서 날짜 없이 남은 레코드와 `GetFunction20150331v2`·`GetFunction20150331` 로 남는다는 설명이 함께 나오므로[3], 여러 모양을 모두 찾습니다.
- **호출 기록은 따로 켜야 함.** `Invoke` 는 데이터 이벤트라 데이터 이벤트를 켠 트레일·이벤트 데이터 저장소에만 있고, 이벤트 기록 화면에는 나오지 않습니다[3]. 선택기 설정은 [관리 이벤트와 데이터 이벤트](cloudtrail/event-types.md) 에서 다룹니다.
- **로그 권한을 뺀 실행 역할.** Lambda 호출 로그는 실행 역할의 로그 권한에 기대므로[1], 역할에서 `logs:PutLogEvents` 를 빼거나 로그 그룹을 바꾸면 그 뒤 호출 로그가 사라지거나 다른 그룹으로 갑니다. 역할 정책 변경과 함수 설정 변경을 CloudTrail 에서 먼저 확인합니다.
- **ECS 로그 그룹은 태스크 정의가 정함.** 로그 설정은 태스크 정의의 `logConfiguration` 에 들어가므로[4], 서비스 이름만 보고 로그 그룹을 짐작하지 않습니다. 조사 기간에 쓰인 태스크 정의를 `RegisterTaskDefinition`·`RunTask` 기록에서 찾아 로그 그룹을 확인합니다.
- **ECS 흐름 로그 필드의 빈칸.** 흐름 로그 구독 소유자의 것이 아닌 태스크(예: 공유한 서브넷에 다른 계정이 띄운 태스크)는 `ecs-*` 필드를 계산하지 않고, ECS 가 아닌 인터페이스의 값은 `-` 입니다[15]. `awsvpc` 네트워크 모드로 띄운 태스크만 지원합니다[15].
- **EKS 파드 주소.** 파드 IP 는 파드가 도는 노드 인터페이스 IP 와 다를 수 있으므로 흐름 로그에서는 `srcaddr`·`dstaddr` 과 `pkt-srcaddr`·`pkt-dstaddr` 를 함께 봅니다[14]. 필드 설명은 [VPC 흐름 로그](vpc-flow-logs.md) 에 있습니다.
- **GuardDuty 가 본 감사 로그와 계정의 감사 로그는 다름.** EKS Protection 은 자체 스트림으로 감사 로그를 보므로, 결과가 있어도 계정에는 제어 평면 로깅을 켜지 않았다면 감사 로그가 없습니다[11]. `CredentialAccess:Kubernetes/SuccessfulAnonymousAccess` 같은 결과[13]를 받았다면 계정의 `kube-apiserver-audit-` 스트림이 있는지 먼저 확인합니다.
- **켜기 전 API 서버 로그.** API 서버 로그를 켜기 전에 서버에서 회전된 로그 파일은 CloudWatch Logs 로 내보낼 수 없고, 스트림은 커지면 이름이 바뀌어 같은 종류가 여럿 생깁니다[6].
- **로그 끄기와 지우기.** 제어 평면 로그 설정은 `aws eks update-cluster-config` 같은 EKS API 호출로 바꾸고[6] EKS API 호출은 CloudTrail 에 남으므로[7], 검체의 `eks.amazonaws.com` 이벤트에서 그 작업 이름을 확인해 끈 시각과 주체를 찾습니다. 로그 그룹 삭제와 보관 기간 변경은 [CloudWatch Logs](cloudwatch-logs.md) 와 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md) 에서 다룹니다.

## 직접 분석해 보기

**원본 JSON 직접 읽기.** S3 에 쌓인 트레일 로그 파일은 `{"Records": [...]}` 모양의 JSON 이라[3], gzip 을 풀어 `jq` 로 세 서비스의 이벤트만 골라 시각순으로 늘어놓습니다. 파일 경로는 만든 예시입니다.

```bash
zcat trail-logs/*.json.gz | jq -r '.Records[]
  | select(.eventSource == "lambda.amazonaws.com" or .eventSource == "ecs.amazonaws.com" or .eventSource == "eks.amazonaws.com")
  | [.eventTime, .eventSource, .eventName, (.userIdentity.arn // "-"), (.sourceIPAddress // "-"), (.errorCode // "")] | @tsv' | sort
```

이름에 날짜가 붙은 Lambda 작업은 앞부분으로 거릅니다.

```bash
zcat trail-logs/*.json.gz | jq -c '.Records[]
  | select(.eventSource == "lambda.amazonaws.com")
  | select(.eventName | test("^(UpdateFunctionCode|UpdateFunctionConfiguration|AddPermission|CreateFunctionUrlConfig|DeleteFunction)"))'
```

Lambda 로그 스트림을 `get-log-events` 로 받아 두었다면, `REPORT` 줄만 골라 호출마다 한 줄씩 만들면 호출 횟수와 콜드 스타트 여부가 드러납니다. 받는 법은 [CloudWatch Logs](cloudwatch-logs.md) 에 있습니다.

```bash
jq -r '.events[] | select(.message | startswith("REPORT")) | [(.timestamp/1000|floor|todate), .message] | @tsv' stream.json
```

**공개 도구로 읽기.** SigmaHQ 규칙 네 개가 이 쪽의 흔적을 CloudTrail 필드로 찾습니다. `aws_lambda_function_url` 은 `CreateFunctionUrlConfig` 를[16], `aws_new_lambda_layer_attached` 는 `UpdateFunctionConfiguration` 으로 시작하는 이벤트 가운데 `requestParameters.layers` 가 있는 것을[17], `aws_ecs_task_definition_cred_endpoint_query` 는 `DescribeTaskDefinition`·`RegisterTaskDefinition`·`RunTask` 의 `requestParameters.containerDefinitions.command` 에 `$AWS_CONTAINER_CREDENTIALS_RELATIVE_URI` 가 든 것을[18], `aws_eks_cluster_created_or_deleted` 는 `eks.amazonaws.com` 의 `CreateCluster`·`DeleteCluster` 를 찾습니다[19]. Invictus-AWS 는 같은 흔적을 Athena 질의로 찾지만 조건이 조금 다릅니다[20]. 레이어 질의는 `requestParameters.layers` 를 보지 않아 설정 변경 전부가 걸리고, ECS 질의는 이벤트 이름을 가리지 않고 `requestparameters` 문자열에 `containerDefinitions` 와 그 변수가 있는지만 봅니다[20]. 규칙을 로그에 돌리는 법은 [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md) 에서, 계정 전체의 로그를 모으는 순서는 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md) 에서 다룹니다.

## 교차 검증

- [CloudTrail](cloudtrail/index.md) — 함수·태스크 정의·클러스터를 바꾼 시각과 주체를 먼저 정하고, 실행 기록을 그 앞뒤로 맞춰 봅니다.
- [CloudWatch Logs](cloudwatch-logs.md) — 호출 로그·컨테이너 로그·EKS 제어 평면 로그가 든 그룹의 보관 설정과 받은 시각을 확인합니다.
- [IAM 사용자·역할·액세스 키](iam.md) — 실행 역할·태스크 역할의 권한과, `inScopeOf` 로 드러난 함수가 그 역할로 부른 다른 서비스 호출을 확인합니다.
- [VPC 흐름 로그](vpc-flow-logs.md) — ECS 태스크(`ecs-task-arn` 등)와 EKS 파드(`pkt-srcaddr`)의 바깥 연결을 봅니다[14].
- [GuardDuty](guardduty.md) — Lambda Protection·EKS Protection·Runtime Monitoring 결과를 위 기록과 맞춰 봅니다[10][11][12].
- [EC2 인스턴스와 스냅숏](ec2-ebs.md) — EC2 방식 ECS 와 EKS 노드는 인스턴스라서, 호스트 쪽 흔적은 디스크와 메모리에서 찾습니다. 수집 절차는 [클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html) 에서 다룹니다.

## 실습

AWS 문서의 예시 레코드와 예시 출력을 교재로 씁니다[2][3][5].

1. Lambda CloudTrail 문서의 예시 파일[3]에는 레코드가 두 개 있습니다. 실패한 요청은 어느 쪽이고, 무엇으로 알 수 있나요? 두 번째 레코드의 `eventName` 을 `DeleteFunction` 으로 정확히 맞춰 찾으면 어떻게 되나요?
2. ECS CloudTrail 문서의 `CreateCluster` 예시[5]에서 요청한 주체의 유형과, 세션을 발급한 역할, 요청이 콘솔에서 왔는지를 각각 어느 필드로 판단하나요?
3. Lambda 로그 문서의 `get-log-events` 예시 출력[2]에서 한 호출에 속하는 줄은 몇 개이고, 그 가운데 함수 코드가 남긴 줄은 어느 것인가요? `REPORT` 줄에 `Init Duration` 이 없으면 무엇을 알 수 있나요?
4. 어떤 EKS 클러스터에서 감사 로그를 2026-09-01 10:00 UTC 에 켰고 GuardDuty 결과는 같은 날 08:30 UTC 의 익명 접근을 가리킨다고 해 봅니다(만든 상황). 계정의 CloudWatch Logs 에서 08:30 의 요청 기록을 찾을 수 있나요? 보고서에는 어떻게 쓰나요?

## 참고 문헌

1. AWS, "Sending Lambda function logs to CloudWatch Logs", AWS Lambda Developer Guide. https://docs.aws.amazon.com/lambda/latest/dg/monitoring-cloudwatchlogs.html
2. AWS, "Viewing CloudWatch logs for Lambda functions", AWS Lambda Developer Guide. https://docs.aws.amazon.com/lambda/latest/dg/monitoring-cloudwatchlogs-view.html
3. AWS, "Logging AWS Lambda API calls using AWS CloudTrail", AWS Lambda Developer Guide. https://docs.aws.amazon.com/lambda/latest/dg/logging-using-cloudtrail.html
4. AWS, "Send Amazon ECS logs to CloudWatch", Amazon ECS Developer Guide. https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_awslogs.html
5. AWS, "Log Amazon ECS API calls using AWS CloudTrail", Amazon ECS Developer Guide. https://docs.aws.amazon.com/AmazonECS/latest/developerguide/logging-using-cloudtrail.html
6. AWS, "Send control plane logs to CloudWatch Logs", Amazon EKS User Guide. https://docs.aws.amazon.com/eks/latest/userguide/control-plane-logs.html
7. AWS, "Log API calls as AWS CloudTrail events", Amazon EKS User Guide. https://docs.aws.amazon.com/eks/latest/userguide/logging-using-cloudtrail.html
8. AWS, "CloudTrail record contents for management, data, and network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
9. AWS, "CloudTrail userIdentity element", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
10. AWS, "GuardDuty foundational data sources", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_data-sources.html
11. AWS, "GuardDuty EKS Protection", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/kubernetes-protection.html
12. AWS, "GuardDuty Runtime Monitoring", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/runtime-monitoring.html
13. AWS, "GuardDuty finding types", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-active.html
14. AWS, "Flow log records", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html
15. AWS, "Flow log limitations", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-limitations.html
16. SigmaHQ, "New AWS Lambda Function URL Configuration Created" (aws_lambda_function_url.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_lambda_function_url.yml
17. SigmaHQ, "AWS New Lambda Layer Attached" (aws_new_lambda_layer_attached.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_new_lambda_layer_attached.yml
18. SigmaHQ, "AWS ECS Task Definition That Queries The Credential Endpoint" (aws_ecs_task_definition_cred_endpoint_query.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_ecs_task_definition_cred_endpoint_query.yml
19. SigmaHQ, "AWS EKS Cluster Created or Deleted" (aws_eks_cluster_created_or_deleted.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_eks_cluster_created_or_deleted.yml
20. Invictus Incident Response, Invictus-AWS, source/files/queries.yaml. https://github.com/invictus-ir/Invictus-AWS
