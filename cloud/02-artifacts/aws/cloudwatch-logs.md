---
title: "CloudWatch Logs"
parent: "아티팩트 · AWS"
nav_order: 430
---

# CloudWatch Logs (CloudWatch Logs)

애플리케이션·인스턴스·AWS 서비스가 보낸 로그 줄을 로그 그룹과 로그 스트림에 나눠 담는 AWS 의 로그 저장소이고, 한 줄마다 보낸 쪽이 적은 발생 시각과 CloudWatch Logs 가 받은 시각이 함께 남습니다.

## 무엇을 기록하나 · 왜 생기나

CloudWatch Logs 는 스스로 사건을 만들어 내는 로그가 아니라, 다른 곳에서 보낸 로그를 받아 보관하는 곳입니다. 로그 이벤트 (log event) 하나는 감시 대상 애플리케이션이나 자원이 남긴 활동 기록이고, 사건이 일어난 시각과 가공하지 않은 메시지 두 가지로 이뤄지며 메시지는 UTF-8 이어야 합니다[1]. 같은 원천에서 온 이벤트가 이어진 것이 로그 스트림 (log stream) 이고, 예를 들어 호스트 한 대의 Apache 접근 로그가 스트림 하나가 됩니다[1]. 로그 그룹 (log group) 은 보관·감시·접근 제어 설정을 함께 쓰는 스트림의 묶음이고, 스트림은 반드시 그룹 하나에 속하며 그룹 하나에 들어갈 스트림 수에는 제한이 없습니다[1][2].

로그가 들어오는 길은 여러 AWS 서비스가 자동으로 보내는 경우와, CloudWatch 에이전트·AWS CLI 의 `put-log-events`·`PutLogEvents` API 로 직접 보내는 경우로 나뉩니다[2]. 그래서 조사에서 만나는 로그 그룹은 대개 CloudTrail 사본, VPC 흐름 로그, Lambda 함수 로그, 컨테이너 출력, EC2 인스턴스에서 에이전트가 올린 운영체제·애플리케이션 로그 가운데 하나입니다. 어느 서비스가 어떤 로그를 어디에 남기는지는 [기록은 어디에 남나](../../01-foundations/model/where-records-live.md) 에서, 로그 종류 전반은 [로그의 종류](../../01-foundations/logging/log-types.md) 에서 다룹니다.

누가 로그를 보내도록 설정하지 않았다면 그 로그 그룹은 없습니다. CloudTrail 을 CloudWatch Logs 로도 보내게 하거나, Lambda 실행 역할에 로그 권한을 주거나, 인스턴스에 에이전트를 설치해야 비로소 그룹이 생기고 기록이 쌓입니다[2][8][11].

## 위치와 버전별 차이

### 서비스별 로그 그룹과 스트림

로그 그룹 이름은 계정 안에서 리전마다 하나뿐이고, 1~512자의 영문자·숫자·`_`·`-`·`/`·`.`·`#` 로 이뤄집니다[3][9]. 로그 그룹은 리전에 속하므로 계정의 로그를 모을 때는 리전마다 그룹 목록을 따로 받습니다. 여러 계정·리전의 로그 그룹을 중앙 계정으로 자동 복제하는 기능이 있으므로[2], 조직 단위 조사라면 중앙 계정에 사본이 있는지도 봅니다.

| 원천 | 로그 그룹 | 로그 스트림 | 전달 지연 |
|---|---|---|---|
| CloudTrail 트레일 | 새로 만들면 CloudTrail 이 정한 이름이나 직접 넣은 이름(예 `CloudTrail/logs`), 기존 그룹도 고를 수 있음. 트레일과 같은 계정·같은 리전에 있어야 함[8][9] | `account_ID_CloudTrail_trail_region`, 양이 많으면 끝에 `_number`[9] | 평균 약 5분, 보장 없음[8] |
| VPC 흐름 로그 | 흐름 로그를 만들 때 지정[10] | 네트워크 인터페이스마다 하나[10] | [VPC 흐름 로그](vpc-flow-logs.md) 참고 |
| Lambda | 기본 `/aws/lambda/함수이름`, 다른 그룹으로 바꿀 수 있음[11] | 실행 환경마다 하나, `YYYY/MM/DD[Function version][Execution environment GUID]`[12] | 호출 뒤 5~10분[11] |
| ECS (`awslogs` 드라이버) | [Lambda·컨테이너 서비스 기록](lambda-containers.md) 참고 | 같은 페이지 참고 | 실제 데이터에서 확인 |
| EKS 제어 평면 | `/aws/eks/클러스터이름/cluster`[13] | `kube-apiserver-…`, `kube-apiserver-audit-…`, `authenticator-…`, `kube-controller-manager-…`, `kube-scheduler-…`[13] | 몇 분 안, 최선 노력[13] |
| S3 서버 접근 로그 | 전달 대상으로 고른 그룹, 구조화 형식[14] | 실제 데이터에서 확인 | 몇 시간 안[14] |
| EC2 인스턴스 (CloudWatch 에이전트) | 에이전트를 설치하는 과정에서 만들어짐[2] | 원천마다 하나(예 호스트별 Apache 접근 로그)[1] | 실제 데이터에서 확인 |

다중 리전 트레일은 켜진 모든 리전의 이벤트를 로그 그룹 하나로 보내고, 그 그룹은 트레일을 만든 리전에 있습니다[8]. CloudTrail 이 로그를 넣을 때 쓰는 기본 IAM 역할 이름은 `CloudTrail_CloudWatchLogs_Role` 입니다[8]. 트레일 설정과 사본의 범위는 [트레일과 로그 파일](cloudtrail/trails.md) 에서 다룹니다.

### 보관 기간과 로그 클래스 (2026년 9월 문서 기준)

| 항목 | 내용 |
|---|---|
| 기본 보관 | 무기한(콘솔 표시는 Never Expire)[2] |
| 고를 수 있는 보관 일수 | 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653[3] |
| 무기한으로 되돌리기 | `DeleteRetentionPolicy`[3] |
| 만료 뒤 실제 삭제 | 보통 72시간 안, 드물게 더 늦음[2][3] |
| 로그 클래스 | Standard(모든 기능), Infrequent Access(값이 싸고 기능 일부만)[1] |
| 삭제 보호 | 켜면 로그 그룹과 스트림을 지우는 작업을 모두 막음, 기본은 꺼짐[1] |

보관 설정은 로그 그룹마다 따로 정하고 그 그룹의 모든 스트림에 똑같이 적용됩니다[1]. 서비스·요금제별 보관 기간 비교는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 에서 다룹니다.

## 구조

조건에 맞는 이벤트를 API 로 받을 때 나오는 객체(`FilteredLogEvent`)에는 필드가 다섯 개 있습니다[5]. `get-log-events` 로 받으면 그 가운데 `timestamp`·`message`·`ingestionTime` 세 필드가 나옵니다[12].

| 필드 | 뜻 |
|---|---|
| `eventId` | 이벤트 ID[5] |
| `logStreamName` | 이벤트가 속한 로그 스트림 이름, 1~512자이고 `:` 과 `*` 는 쓰지 않음[5] |
| `timestamp` | 사건이 일어난 시각, 1970-01-01 00:00:00 UTC 부터 흐른 밀리초[5] |
| `ingestionTime` | CloudWatch Logs 가 이벤트를 받은 시각, 1970-01-01 00:00:00 UTC 부터 흐른 밀리초[5] |
| `message` | 이벤트에 담긴 데이터(원천이 보낸 메시지 그대로)[1][5] |

`timestamp` 는 보내는 쪽이 요청에 직접 넣는 값이고, `PutLogEvents` 요청에는 이벤트마다 `message` 와 `timestamp` 만 들어갑니다[4]. 한 요청은 최대 10,000건, 최대 1,048,576바이트(UTF-8 메시지 길이 합에 이벤트마다 26바이트를 더한 값)이고, 이벤트 하나는 1MB 를 넘지 못합니다[4]. 요청 안의 이벤트는 `timestamp` 순서여야 하고, 한 요청의 시간 폭은 24시간을 넘지 못합니다[4]. 2시간 넘게 미래인 이벤트와, 14일보다 오래됐거나 로그 그룹 보관 기간보다 앞선 이벤트는 거부되고 나머지만 들어갑니다[4].

`message` 의 모양은 원천마다 다릅니다. CloudTrail 사본이면 CloudTrail JSON 레코드 하나이고([레코드 구조](cloudtrail/record-structure.md)), VPC 흐름 로그면 공백으로 가른 레코드 한 줄이며([VPC 흐름 로그](vpc-flow-logs.md)), Lambda 면 `START`·`END`·`REPORT` 줄과 함수 코드가 출력한 줄입니다[12]. EKS 로그를 구독 필터 (subscription filter) 로 다른 서비스에 넘기면 Base64 로 인코딩하고 gzip 으로 압축한 모양이 됩니다[13].

아래는 EC2 인스턴스의 에이전트가 올린 로그 스트림을 `get-log-events` 로 받은 모양을 흉내 낸 만든 예시입니다. 스트림 이름·주소·시각은 모두 지어낸 값입니다.

```json
{
  "events": [
    {
      "timestamp": 1788232212345,
      "message": "Sep  1 03:10:12 ip-198-51-100-10 sshd[2211]: Accepted publickey for ec2-user from 203.0.113.25 port 51544 ssh2",
      "ingestionTime": 1788232214901
    },
    {
      "timestamp": 1788213600000,
      "message": "Aug 31 22:00:00 ip-198-51-100-10 sshd[1980]: Accepted password for admin from 192.0.2.77 port 40211 ssh2",
      "ingestionTime": 1788232262118
    }
  ]
}
```

첫 이벤트는 발생 시각(2026-09-01 03:10:12.345 UTC)과 받은 시각(03:10:14.901 UTC)의 차이가 약 2.6초입니다. 두 번째 이벤트는 발생 시각이 전날 22:00:00 UTC 인데 받은 시각은 03:11:02 UTC 라서 약 5시간 늦게 들어왔고, 에이전트가 밀린 파일을 늦게 올렸거나 누가 과거 시각을 적어 넣었을 가능성이 있습니다. 이런 모양은 `timestamp`·`message`·`ingestionTime` 세 필드가 나오는 AWS 예시 출력과 같습니다[12].

## 증거로서 의미

**증명하는 것.** 어떤 원천이 이 메시지를 이 로그 그룹의 이 스트림에 보냈고, CloudWatch Logs 가 그것을 `ingestionTime` 에 받았다는 사실입니다[5]. CloudTrail 사본·흐름 로그·Lambda 로그처럼 AWS 서비스가 직접 넣는 그룹이면 메시지 내용은 그 서비스의 기록으로 읽고, 해석은 원래 기록의 페이지에서 합니다. 보관 설정이 무기한인 그룹이면 원천 시스템에서 이미 지워진 로그도 남아 있을 수 있습니다[2].

**증명하지 못하는 것.** 에이전트나 애플리케이션이 보낸 메시지는 보낸 쪽이 만든 문자열이고, `timestamp` 도 보낸 쪽이 정한 값이라 내용과 발생 시각이 맞는지는 CloudWatch Logs 가 보증하지 않습니다[4]. 쓰기 권한(`logs:PutLogEvents`)이 있는 주체는 14일 안의 과거 시각으로 이벤트를 넣을 수 있으므로[4], 순서가 어긋나 보이는 줄은 `ingestionTime` 으로 확인합니다. 보관 기간이 지나 지워진 이벤트, 14일보다 오래된 시각이라 거부된 이벤트, CloudTrail 사본에서 빠진 256KB 넘는 이벤트는 그룹에 없습니다[3][4][8]. 로그 그룹이 없다고 해서 그 기간에 활동이 없었다는 뜻도 아니고, 보내도록 설정하지 않았을 수 있습니다.

보고서에는 "로그 그룹 A 의 스트림 B 에 2026-09-01 03:10:14 UTC 에 받은 이벤트가 있고, 그 메시지에는 03:10:12 에 203.0.113.25 에서 `ec2-user` 로 공개 키 로그인을 허용했다고 적혀 있다" 처럼 기록으로 확인되는 만큼만 씁니다(만든 예시). 문장 쓰는 법은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에서 다룹니다.

## 시각 해석

`timestamp` 와 `ingestionTime` 은 모두 1970-01-01 00:00:00 UTC 부터 흐른 밀리초라서 시간대가 없는 UTC 값입니다[5]. `timestamp` 는 보내는 쪽 시계, `ingestionTime` 은 CloudWatch Logs 쪽 시계로 찍히므로, 두 값의 차이로 전달 지연과 원천 시계의 어긋남을 추정합니다[4][5]. 원천 메시지 안에 따로 적힌 시각(syslog 의 현지 시각 등)은 세 번째 시각이고, 원천 시스템의 시간대 설정을 따르므로 따로 확인합니다.

원천마다 `timestamp` 가 가리키는 시점이 다릅니다. VPC 흐름 로그에서는 레코드의 `start` 와 같고 `ingestionTime` 은 레코드의 `end` 보다 늦습니다[10]. CloudTrail 사본을 콘솔에서 보면 Time (UTC) 열은 이벤트가 로그 그룹에 들어온 시각이고, CloudTrail 이 기록한 실제 시각은 메시지 안의 `eventTime` 입니다[8]. Lambda 로그는 함수 코드가 남긴 줄까지 모든 메시지에 시각이 붙고, `START` 줄과 `END` 줄 사이의 줄이 한 호출에 속합니다[12].

시각을 기준으로 거르는 기능도 두 시각 가운데 어느 쪽을 쓰는지 다릅니다. S3 내보내기 작업의 시작·끝 범위는 받은 시각 기준이라 늦게 들어온 이벤트는 발생 시각과 다른 범위에 들어갈 수 있습니다[6]. Logs Insights 는 로그 그룹을 만든 시각보다 앞선 `timestamp` 의 이벤트에 접근하지 못하고, 2018년 11월 5일 이후에 들어온 로그만 검색합니다[7]. 여러 로그의 시각을 한 줄로 맞추는 법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 과 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 함정과 한계

- **보관 설정 바꾸기.** 보관 일수를 줄이면 그보다 오래된 이벤트는 삭제 대상이 되고 보통 72시간 안에 지워집니다[2][3]. 삭제 대상으로 표시된 이벤트는 실제로 지워지기 전이라도 API 로 받는 `storedBytes` 에 들어가지 않으므로[2][3], 저장 용량 값만 보고 남은 양을 판단하지 않습니다. 수집을 마치기 전에는 보관 설정을 건드리지 않고, 먼저 사본을 받아 둡니다. 절차는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 에서 다룹니다.
- **지우기와 설정 변경의 흔적.** 보관 설정 변경(`PutRetentionPolicy`·`DeleteRetentionPolicy`), 그룹·스트림 삭제(`DeleteLogGroup`·`DeleteLogStream`), S3 내보내기(`CreateExportTask`), 이벤트 조회(`GetLogEvents`·`FilterLogEvents`)는 CloudTrail 이 이벤트로 기록하는 CloudWatch Logs 작업이고, 이 레코드의 `eventSource` 는 `logs.amazonaws.com` 입니다[17]. 이벤트를 넣는 `PutLogEvents` 는 CloudTrail 이 기록하는 작업 목록에 없습니다[17]. 삭제 보호는 기본으로 꺼져 있어서[1], 켜 두지 않은 그룹은 권한이 있는 주체가 바로 지울 수 있습니다. 흐름은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md) 에서 다룹니다.
- **CloudTrail 사본의 빈틈.** CloudWatch Logs 는 이벤트 하나를 256KB 까지만 받으므로 CloudTrail 은 이보다 큰 이벤트를 보내지 않습니다[8]. 트레일이 데이터 이벤트만 기록하도록 설정됐다면 사본에도 데이터 이벤트만 들어갑니다[8]. 원본은 S3 의 트레일 로그 파일에서 확인합니다.
- **전달처를 바꾸는 동안.** S3 서버 접근 로그의 전달 대상 로그 그룹을 바꾸면 한동안 일부 로그가 이전 그룹으로 계속 들어갈 수 있습니다[14]. 설정 변경 시각 앞뒤 구간은 두 그룹을 모두 봅니다.
- **스트림 이름이 바뀜.** EKS 스트림은 데이터가 커지면 이름이 바뀌어 같은 종류의 스트림이 여럿 생기고, 제어 평면 로그를 켜기 전에 서버에서 회전된 API 서버 로그는 내보낼 수 없습니다[13]. CloudTrail 스트림도 양이 많으면 끝에 번호가 붙은 스트림이 여럿 생깁니다[9]. 스트림 하나만 받고 끝내지 않습니다.
- **순서 번호가 없음.** `PutLogEvents` 의 시퀀스 토큰은 이제 무시되고, 같은 스트림에 여러 요청을 동시에 넣을 수 있습니다[4]. 토큰으로 이벤트의 들어온 순서나 누락을 따질 수 없습니다.
- **내보낸 파일의 순서.** S3 로 내보낸 파일 안의 데이터 조각은 시각 순서로 정렬된다는 보장이 없고, 데이터가 내보낼 수 있게 되기까지 최대 12시간이 걸리며, 내보내기 작업은 24시간이 지나면 시간 초과로 끝납니다[6]. 시간 초과가 나면 범위를 줄여 다시 만듭니다[6].
- **CloudWatch Logs 장기 API 키.** 이 키는 IAM 자격 증명 보고서에 나오지 않으므로 `ListServiceSpecificCredentials` 로 따로 확인합니다[15]. 키 전반은 [IAM 사용자·역할·액세스 키](iam.md) 에서 다룹니다.
- **도구가 모으는 범위.** Invictus-AWS 의 CloudWatch 수집 단계는 대시보드·지표·경보 설정을 모으고 로그 이벤트 자체는 받지 않습니다[16]. 로그 그룹의 이벤트는 따로 받아야 합니다.

## 직접 분석해 보기

**원본 JSON 직접 읽기.** 먼저 리전마다 로그 그룹 목록을 받아 어떤 그룹이 있고 보관 설정이 어떤지 기록해 둡니다. 그다음 조사할 그룹의 스트림에서 이벤트를 받아 JSON 그대로 보관합니다. 아래 그룹·스트림 이름은 만든 예시입니다.

```bash
aws logs describe-log-groups --region us-east-1 > log-groups-us-east-1.json
aws logs get-log-events --region us-east-1 \
  --log-group-name /aws/lambda/my-function \
  --log-stream-name '2026/09/01/[$LATEST]0123456789abcdef0123456789abcdef' > stream.json
```

받은 파일에서 두 시각을 UTC 로 풀고 차이를 초로 붙이면 늦게 들어온 줄과 과거 시각을 단 줄이 드러납니다.

```bash
jq -r '.events[] | [(.timestamp/1000|floor|todate), (.ingestionTime/1000|floor|todate), ((.ingestionTime-.timestamp)/1000|tostring), .message] | @tsv' stream.json
jq -r '.events[] | select(.ingestionTime - .timestamp > 600000) | .message' stream.json
```

두 번째 명령은 받은 시각이 발생 시각보다 10분 넘게 늦은 이벤트만 고릅니다. 위 만든 예시에 돌리면 22:00:00 로그인 줄만 나옵니다.

**S3 로 내보낸 파일 읽기.** 내보낸 파일은 gzip 으로 묶여 있고 안의 순서가 보장되지 않으므로, 풀어서 줄 머리의 숫자를 기준으로 정렬합니다[6].

```bash
find . -exec zcat {} + | sed -r 's/^[0-9]+/\x0&/' | sort -z
```

**공개 도구와 AWS 기능으로 읽기.** Logs Insights 는 Logs Insights QL, OpenSearch PPL, OpenSearch SQL 세 가지 질의 언어를 지원하고, CloudTrail·VPC·Lambda·Route 53 로그와 JSON 으로 된 로그의 필드를 자동으로 찾습니다[7]. 질의는 60분이 지나면 끝나고 결과는 7일 동안 볼 수 있으며, 요금은 읽은 압축 전 데이터 양으로 매깁니다[7]. 결과를 증거로 쓰려면 질의문과 결과를 함께 저장하고, 원본 이벤트도 따로 받아 둡니다. 계정 전체의 로그를 모으는 순서는 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md) 에서 다룹니다.

## 교차 검증

- [CloudTrail](cloudtrail/index.md) — CloudWatch Logs 의 CloudTrail 사본과 S3 의 원본 로그 파일을 맞춰 빠진 이벤트가 있는지 보고, 로그 그룹의 보관 설정을 바꾸거나 그룹을 지운 호출을 찾습니다.
- [VPC 흐름 로그](vpc-flow-logs.md) — 흐름 로그를 CloudWatch Logs 로 보냈다면 인터페이스별 스트림을 받아 흐름 로그 페이지의 해석대로 읽습니다.
- [Lambda·컨테이너 서비스 기록](lambda-containers.md) — 함수 호출 로그와 컨테이너 출력, EKS 감사 로그를 CloudTrail 의 함수·태스크·클러스터 변경 기록과 맞춰 봅니다.
- [S3 접근 기록](s3-access-logs.md) — 서버 접근 로그를 CloudWatch Logs 로 받았다면 필드 해석은 그 페이지를 따릅니다.
- [IAM 사용자·역할·액세스 키](iam.md) — 로그를 넣은 역할(`CloudTrail_CloudWatchLogs_Role`, Lambda 실행 역할)과 `logs:PutLogEvents` 권한을 가진 주체를 확인합니다.
- [GuardDuty](guardduty.md) — GuardDuty 결과의 시각 앞뒤로 같은 인스턴스·함수의 로그 그룹을 찾아봅니다.
- 인스턴스 안의 원본 파일 — 에이전트가 올린 운영체제 로그는 인스턴스 디스크에도 원본이 남아 있을 수 있으므로 [클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html) 으로 확보해 [인증 로그](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/logins/auth-log.html) 와 줄 단위로 맞춰 봅니다.
- [리소스 로그와 진단 설정](../azure/resource-logs.md) — Azure 에서 서비스 로그를 모으는 비슷한 구조입니다.

## 실습

AWS 문서의 예시와 위의 만든 예시로 풀어 봅니다.

1. 위 만든 예시 두 이벤트의 `timestamp`·`ingestionTime` 을 UTC 로 풀고, 두 번째 이벤트가 늦게 들어온 이유로 생각할 수 있는 것을 두 가지 적어 봅니다.
2. Lambda 문서의 `get-log-events` 예시 출력[12]에서 `START` 줄의 발생 시각과 받은 시각 차이를 밀리초로 계산해 봅니다.
3. 보관 기간이 30일인 로그 그룹에서 누가 보관 일수를 1일로 바꿨다면, 72시간 안에 어떤 이벤트가 사라질 수 있는지, 그리고 `storedBytes` 가 어떻게 보일지 설명해 봅니다[2][3].
4. 다중 리전 트레일의 CloudTrail 사본에서 `ap-northeast-2` 리전의 이벤트를 찾으려면 어느 리전의 로그 그룹을 봐야 하는지, 스트림 이름이 어떤 모양일지 적어 봅니다[8][9].
5. 실제 계정에서는 리전마다 로그 그룹 목록을 받아 그룹 이름·원천·보관 일수·삭제 보호 여부를 표로 만들고, 사고 시각에 기록이 남아 있을 그룹과 이미 지워졌을 그룹을 나눠 봅니다.

## 참고 문헌

1. AWS, "Amazon CloudWatch Logs concepts", Amazon CloudWatch Logs User Guide. https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CloudWatchLogsConcepts.html
2. AWS, "Working with log groups and log streams", Amazon CloudWatch Logs User Guide. https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html
3. AWS, "PutRetentionPolicy", Amazon CloudWatch Logs API Reference. https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutRetentionPolicy.html
4. AWS, "PutLogEvents", Amazon CloudWatch Logs API Reference. https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutLogEvents.html
5. AWS, "FilteredLogEvent", Amazon CloudWatch Logs API Reference. https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_FilteredLogEvent.html
6. AWS, "Exporting log data to Amazon S3", Amazon CloudWatch Logs User Guide. https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/S3Export.html
7. AWS, "Analyzing log data with CloudWatch Logs Insights", Amazon CloudWatch Logs User Guide. https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html
8. AWS, "Sending events to CloudWatch Logs", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/send-cloudtrail-events-to-cloudwatch-logs.html
9. AWS, "CloudWatch log group and log stream naming for CloudTrail", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudwatch-log-group-log-stream-naming-for-cloudtrail.html
10. AWS, "Publish flow logs to CloudWatch Logs", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-cwl.html
11. AWS, "Sending Lambda function logs to CloudWatch Logs", AWS Lambda Developer Guide. https://docs.aws.amazon.com/lambda/latest/dg/monitoring-cloudwatchlogs.html
12. AWS, "Viewing CloudWatch logs for Lambda functions", AWS Lambda Developer Guide. https://docs.aws.amazon.com/lambda/latest/dg/monitoring-cloudwatchlogs-view.html
13. AWS, "Send control plane logs to CloudWatch Logs", Amazon EKS User Guide. https://docs.aws.amazon.com/eks/latest/userguide/control-plane-logs.html
14. AWS, "Logging requests with server access logging", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html
15. AWS, "Generate credential reports for your AWS account", AWS IAM User Guide. https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_getting-report.html
16. Invictus Incident Response, Invictus-AWS (source/main/logs.py). https://github.com/invictus-ir/Invictus-AWS
17. AWS, "Logging CloudWatch Logs API and console operations in AWS CloudTrail", Amazon CloudWatch Logs User Guide. https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/logging_cw_api_calls_cwl.html
