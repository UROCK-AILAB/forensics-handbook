---
title: "AWS VPC 흐름 로그"
parent: "아티팩트 · AWS"
nav_order: 410
---

# VPC 흐름 로그 (VPC Flow Logs)

AWS VPC 안의 네트워크 인터페이스로 오간 IP 트래픽을 집계 간격마다 한 줄씩 요약한 기록이고, 어느 주소가 어느 포트로 언제 몇 바이트를 주고받았으며 허용됐는지 거부됐는지를 알려 줍니다.

## 무엇을 기록하나 · 왜 생기나

흐름 로그 (flow log) 는 VPC·서브넷·네트워크 인터페이스 가운데 하나에 만들고, VPC 나 서브넷에 만들면 그 안의 인터페이스를 모두 지켜봅니다[2]. 만들 때 받을 트래픽 종류(허용된 것, 거부된 것, 전부)와 보낼 곳을 고르고, 보낼 곳은 CloudWatch Logs·S3·Data Firehose 가운데서 고릅니다[1][2]. 로드 밸런서·RDS·ElastiCache·Redshift·WorkSpaces·NAT 게이트웨이·전송 게이트웨이 (transit gateway) 처럼 다른 서비스가 만든 인터페이스에도 만들 수 있습니다[2].

레코드 한 줄은 한 인터페이스에서 한 집계 간격 (aggregation interval) 동안 생긴 흐름 하나를 나타내고, 흐름은 5-튜플(출발지·목적지 주소, 출발지·목적지 포트, 프로토콜)로 가릅니다[3]. 패킷 내용은 담지 않고 개수·바이트 수·시각·허용 여부 같은 요약만 담습니다[3]. 흐름 로그는 트래픽 경로 밖에서 모으므로 켜거나 꺼도 네트워크 속도에 영향이 없습니다[1].

흐름 로그는 자원마다 만들어야 기록이 생기고, 만든 뒤에도 모으기 시작하기까지 몇 분이 걸립니다[2]. 그래서 사고 전에 흐름 로그를 만들어 두지 않았다면 그 구간의 기록은 없습니다. GuardDuty 는 계정의 흐름 로그 설정과 상관없이 EC2 인스턴스의 흐름 로그를 따로 복제한 스트림으로 받아 분석하지만, 그 데이터를 계정에서 볼 수 있게 해 주지 않습니다[8]. 그래서 GuardDuty 결과가 있다고 흐름 로그 원본이 있는 것은 아닙니다. 로그 종류 전반은 [로그의 종류](../../01-foundations/logging/log-types.md) 에서 다룹니다.

## 위치와 버전별 차이

### 보낸 곳에 따른 차이

| 보낸 곳 | 저장 단위 | 전달 지연 | 시각 표시 |
|---|---|---|---|
| CloudWatch Logs | 로그 그룹 안에 인터페이스마다 로그 스트림 하나[7] | 보통 약 5분, 최선 노력[3] | 이벤트 `timestamp` 는 레코드의 `start`, `ingestionTime` 은 받은 시각으로 `end` 보다 늦음[7] |
| S3 | 5분마다 게시하는 gzip 파일, 텍스트(기본) 또는 Parquet[6] | 보통 약 10분, 최선 노력[3] | 파일 이름의 UTC 시각, 객체의 Last modified 는 올린 시각[6] |
| Data Firehose | 지정한 전달 스트림[1] | 전달 스트림 쪽 설정을 확인 | 전달 스트림 쪽 설정을 확인 |

CloudWatch Logs 에서 같은 인터페이스가 같은 로그 그룹의 흐름 로그 여러 개에 들어 있으면 스트림은 하나로 합쳐지고, 하나는 허용·하나는 거부만 받도록 했다면 합쳐진 스트림에는 전부가 담깁니다[7]. 흐름 로그를 만든 뒤 서브넷에 새 인스턴스가 뜨면 그 인터페이스에 트래픽이 생기는 순간 새 스트림이나 새 파일이 생깁니다[2]. 로그 그룹의 보관 기간은 [CloudWatch Logs](cloudwatch-logs.md) 에서 다룹니다.

S3 에 쌓이는 경로는 아래와 같고, 시간 단위 분할을 켜면 끝에 `hour/`(Hive 호환 접두사와 함께 켜면 `hour=hour/`)가 더 붙습니다[6].

```text
bucket-and-optional-prefix/AWSLogs/account_id/vpcflowlogs/region/year/month/day/
bucket-and-optional-prefix/AWSLogs/aws-account-id=account_id/aws-service=vpcflowlogs/aws-region=region/year=year/month=month/day=day/
```

두 번째 줄은 Hive 호환 접두사를 켰을 때의 모양입니다[6]. 파일 이름은 `aws_account_id_vpcflowlogs_region_flow_log_id_YYYYMMDDTHHmmZ_hash.log.gz` 형식이고, 예를 들어 `123456789012_vpcflowlogs_us-east-1_fl-1234abcd_20180620T1620Z_fe123456.log.gz` 에는 `end` 가 16:20:00 부터 16:24:59(UTC) 사이인 레코드가 들어 있습니다[6]. 한 5분 구간이 파일 여러 개로 나뉠 수 있습니다[6].

### 요금과 설정 제약 (2026년 9월 문서 기준)

흐름 로그를 게시하면 CloudWatch 의 서비스 제공 로그 (vended logs) 수집·보관 요금이 붙습니다[1]. 흐름 로그를 보낼 곳과 권한을 묶은 설정을 구독 (subscription) 이라고 부르고[1], 자원 하나에 계정당 구독을 250개까지 만들 수 있습니다[5]. 흐름 로그는 만든 뒤 설정과 레코드 형식을 바꿀 수 없어서, 바꾸려면 지우고 새로 만듭니다[5]. 내 계정에 있지 않은 피어링 VPC 에는 흐름 로그를 만들 수 없습니다[5].

### 필드 버전

기본 형식은 버전 2 필드를 아래 순서로 담고, 바꿀 수 없습니다[3].

```text
version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status
```

사용자 지정 형식 (custom format) 은 필드와 순서를 직접 고르고, `version` 값은 고른 필드 가운데 가장 높은 버전이 됩니다[3]. 필드마다 들어온 버전은 아래와 같습니다[3]. 버전 6 은 전송 게이트웨이 흐름 로그에서 들어온 버전이라 아래 표에 없습니다[1].

| 버전 | 필드 |
|---|---|
| 2 | `version`, `account-id`, `interface-id`, `srcaddr`, `dstaddr`, `srcport`, `dstport`, `protocol`, `packets`, `bytes`, `start`, `end`, `action`, `log-status` |
| 3 | `vpc-id`, `subnet-id`, `instance-id`, `tcp-flags`, `type`, `pkt-srcaddr`, `pkt-dstaddr` |
| 4 | `region`, `az-id`, `sublocation-type`, `sublocation-id` |
| 5 | `pkt-src-aws-service`, `pkt-dst-aws-service`, `flow-direction`, `traffic-path` |
| 7 | `ecs-cluster-arn`, `ecs-cluster-name`, `ecs-container-instance-arn`, `ecs-container-instance-id`, `ecs-container-id`, `ecs-second-container-id`, `ecs-service-name`, `ecs-task-definition-arn`, `ecs-task-arn`, `ecs-task-id` |
| 8 | `reject-reason` |
| 9 | `resource-id` |
| 10 | `encryption-status` |
| 11 | `instance-tag`, `instance-tag-2`, `interface-tag`, `interface-tag-2`, `asg-tag`, `asg-tag-2`, `interface-type`, `next-hop-interface-id`, `next-hop-subnet-id`, `next-hop-az-id`, `next-hop-vpc-id`, `next-hop-interface-type` |

## 구조

레코드는 공백으로 가른 문자열 한 줄입니다[3]. 해당하지 않거나 계산하지 못한 필드는 `-` 로 나오고, 패킷 헤더에서 오지 않은 메타데이터 필드는 어림값이라 빠지거나 틀릴 수 있습니다[3]. S3 텍스트 형식이면 모든 필드가 문자열이고, Parquet 이면 필드마다 형식이 정해져 있습니다[3].

| 필드 | 뜻 |
|---|---|
| `account-id` | 트래픽을 기록한 인터페이스 소유 계정. AWS 서비스가 만든 인터페이스(VPC 끝점, Network Load Balancer 등)는 `unknown` 일 수 있음[3] |
| `interface-id` | 트래픽을 기록한 네트워크 인터페이스 ID. 리전 NAT 게이트웨이 흐름은 `-`[3] |
| `srcaddr`, `dstaddr` | 들어오는 트래픽은 출발지 주소와 인터페이스 주소, 나가는 트래픽은 인터페이스 주소와 목적지 주소. 인터페이스 쪽 IPv4 는 늘 사설 주소[3] |
| `protocol` | IANA 프로토콜 번호(6 은 TCP, 1 은 ICMP)[3][4] |
| `packets`, `bytes` | 그 흐름에서 오간 패킷 수와 바이트 수[3] |
| `start`, `end` | 집계 간격 안에서 첫 패킷과 마지막 패킷을 받은 시각, Unix 초[3] |
| `action` | `ACCEPT` 또는 `REJECT`. 보안 그룹·네트워크 ACL 이 막은 경우 말고도 연결이 닫힌 뒤 도착한 패킷도 `REJECT`[3] |
| `log-status` | `OK`, `NODATA`(그 간격에 트래픽 없음), `SKIPDATA`(내부 용량·오류로 레코드를 건너뜀)[3] |
| `pkt-srcaddr`, `pkt-dstaddr` | 패킷에 적힌 원래 주소. NAT 게이트웨이·EKS 파드처럼 중간 계층을 거친 트래픽에서 `srcaddr`·`dstaddr` 와 달라짐[3] |
| `tcp-flags` | FIN 1, SYN 2, RST 4, SYN-ACK 18. ACK·PSH 만 있으면 0, 한 간격 안의 플래그는 OR 로 합쳐짐(3 은 SYN+FIN, 19 는 SYN-ACK+FIN)[3] |
| `flow-direction` | 기록한 인터페이스 기준 `ingress` 또는 `egress`[3] |
| `traffic-path` | 나가는 트래픽의 경로 코드. 1 같은 VPC 안 자원, 2 인터넷 게이트웨이나 게이트웨이 VPC 끝점, 3 가상 사설 게이트웨이, 4 리전 안 VPC 피어링, 5 리전 간 VPC 피어링, 6 Local Zone·Wavelength Zone, 7 게이트웨이 VPC 끝점, 8 인터넷 게이트웨이. 들어오는 트래픽에는 쓰지 않음[3][4] |
| `pkt-src-aws-service`, `pkt-dst-aws-service` | 주소가 AWS 서비스 대역이면 `S3`·`EC2`·`ROUTE53`·`AMAZON` 같은 서비스 이름[3] |
| `reject-reason` | 거부 사유 `BPA`(VPC 공개 접근 차단) 또는 `EC`(암호화 통제), 나머지는 `-`[3] |

아래는 기본 형식으로 만든 예시 레코드입니다. 계정·인터페이스 ID·주소·시각은 모두 지어낸 값이고 주소는 문서용 IP 대역입니다(실제 레코드에서 인스턴스 쪽 주소는 VPC 의 사설 IPv4 주소입니다).

```text
2 123456789012 eni-0a1b2c3d4e5f60718 203.0.113.25 198.51.100.10 51544 22 6 18 3120 1788232200 1788232260 ACCEPT OK
2 123456789012 eni-0a1b2c3d4e5f60718 198.51.100.10 203.0.113.25 22 51544 6 15 4096 1788232200 1788232260 ACCEPT OK
2 123456789012 eni-0a1b2c3d4e5f60718 192.0.2.77 198.51.100.10 40211 3389 6 1 60 1788232200 1788232260 REJECT OK
2 123456789012 eni-0a1b2c3d4e5f60718 - - - - - - - 1788232440 1788232500 - NODATA
```

첫 두 줄은 한 SSH 연결의 두 방향이 따로 적힌 것이고, 세 번째 줄은 RDP 포트로 온 패킷이 거부된 것이며, 네 번째 줄은 그 간격에 트래픽이 없었다는 뜻입니다. 이런 모양은 AWS 예시 레코드와 같습니다[4].

## 증거로서 의미

**증명하는 것.** 이 인터페이스에서 이 시간 창 안에 이 5-튜플로 패킷 몇 개와 바이트 몇이 오갔고, 그 트래픽이 허용됐는지 거부됐는지를 보여 줍니다[3]. `tcp-flags` 가 있으면 SYN(2)을 보낸 쪽과 SYN-ACK(18)를 보낸 쪽을 갈라 누가 연결을 먼저 열었는지 볼 수 있습니다[4]. `flow-direction`·`traffic-path` 가 있으면 나간 트래픽이 인터넷 게이트웨이·피어링·VPN 가운데 어느 길로 나갔는지 알 수 있습니다[3]. 나간 쪽 바이트가 큰 흐름은 자료가 밖으로 나갔을 가능성을 가리키는 단서가 됩니다.

**증명하지 못하는 것.** 페이로드가 없으므로 무엇을 보냈는지는 알 수 없습니다[3]. 어느 프로세스·사용자·IAM 주체가 만든 트래픽인지도 담지 않으므로, 사람과 이어 붙이려면 CloudTrail 이나 인스턴스 안의 기록이 필요합니다. Amazon DNS 서버로 간 질의, 169.254.169.254 의 인스턴스 메타데이터 접근, 169.254.169.123 의 Time Sync, DHCP, ARP, 기본 VPC 라우터 예약 주소로 간 트래픽, Windows 라이선스 활성화 트래픽, 끝점 인터페이스와 Network Load Balancer 인터페이스 사이 트래픽은 기록하지 않습니다[5]. 트래픽 미러링의 원본 쪽 트래픽과 만들고 몇 분 만에 지운 리전 NAT 게이트웨이의 트래픽도 빠집니다[5]. 그래서 흐름 로그에 없다고 해서 그 통신이 없었다고 쓰면 안 됩니다. `SKIPDATA` 한 줄은 기록하지 못한 흐름 여러 개를 대신할 수 있어서[4], 그 간격에 흐름이 몇 개 빠졌는지는 이 줄로 알 수 없습니다.

보고서에는 "2026-09-01 03:10 UTC 전후 1분 창에 203.0.113.25 에서 인스턴스의 22번 포트로 TCP 패킷 18개(3,120바이트)가 들어왔고 허용된 기록이 있다" 처럼 레코드가 말하는 만큼만 씁니다(만든 예시). 문장 쓰는 법은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에서 다룹니다.

## 시각 해석

`start`·`end` 는 Unix 초라서 시간대가 없는 UTC 기준 값입니다[3]. `start` 는 집계 간격 안에서 첫 패킷을 받은 시각이고, 인터페이스에서 실제로 패킷을 받거나 보낸 시각과 최대 60초까지 차이 날 수 있습니다[3]. `end` 는 마지막 패킷 시각이고 실제보다 최대 60초 늦을 수 있습니다[3]. 그래서 흐름 로그의 시각은 초 단위 사건 시각이 아니라 "이 창 안 어딘가" 로 읽습니다.

집계 간격은 기본으로 최대 10분이고, 만들 때 최대 1분으로 줄일 수 있습니다[3]. Nitro 기반 인스턴스에 붙은 인터페이스는 설정과 상관없이 늘 1분 이하입니다[3][5]. 오래 이어진 연결은 간격마다 한 줄씩 여러 줄로 나뉘므로, 연결 하나의 전체 바이트는 같은 5-튜플의 줄을 더해서 구합니다[4].

기록이 도착하는 시각은 따로 있습니다. CloudWatch Logs 의 `ingestionTime` 은 `end` 보다 늦고[7], S3 객체의 Last modified 는 파일 이름의 시각보다 올리는 데 걸린 만큼 늦습니다[6]. 흐름 로그를 새로 만들면 모으기 시작하기까지 몇 분이 걸리고 실시간 스트림이 아닙니다[2]. 여러 로그의 시각을 한 줄로 맞추는 법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 과 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 함정과 한계

- **사용자 지정 형식.** 필드 순서가 흐름 로그마다 다를 수 있으므로 기본 형식이라고 가정하고 열을 자르면 안 됩니다[3]. 먼저 흐름 로그 설정을 받아 형식을 확인합니다. Invictus-AWS 는 EC2 API `describe_flow_logs` 로 흐름 로그 목록을 받고 `LogDestinationType` 과 `LogDestination` 으로 S3 버킷을 찾습니다[10].
- **주소 두 벌.** 영역 NAT 게이트웨이 (zonal NAT gateway)·전송 게이트웨이 인터페이스를 거치는 줄에서는 `srcaddr`·`dstaddr` 에 중간 인터페이스 주소가 나오고 원래 주소는 `pkt-srcaddr`·`pkt-dstaddr` 에 있습니다[4]. 리전 NAT 게이트웨이 (regional NAT gateway) 흐름은 `interface-id` 가 `-` 이고 `resource-id` 에 NAT 게이트웨이 ID 가 나오며, `dstaddr` 에도 최종 목적지 주소가 나옵니다[3][4]. 보조 사설 IPv4 로 온 트래픽도 `dstaddr` 에는 기본 사설 IPv4 가 나오고[5], 중간 계층이 클라이언트 IP 보존을 켜면 `pkt-*addr` 에 보존된 클라이언트 IP 가 나올 수 있습니다[5].
- **보안 그룹과 네트워크 ACL.** 보안 그룹은 상태를 기억해 허용한 트래픽의 응답도 허용하고, 네트워크 ACL 은 상태를 기억하지 않아 응답도 규칙을 따릅니다[4]. ping 이 들어와 허용되고 응답을 ACL 이 막으면 `ACCEPT` 한 줄과 `REJECT` 한 줄이 남습니다[4]. `REJECT` 만 보고 "들어오지 못했다" 고 단정하지 않고 방향을 함께 봅니다.
- **VPC 공개 접근 차단 (VPC BPA).** 이 흐름 로그에는 건너뛴 레코드가 없고, `bytes` 필드를 넣어도 바이트 수가 없습니다[5].
- **ECS·태그 필드.** 서브넷을 다른 계정과 공유하면 그 계정이 띄운 ECS 태스크나 태그의 필드는 계산하지 않고, 태그 필드는 구독을 만든 뒤 첫 한 시간 동안 빠지거나 틀릴 수 있습니다[5].
- **지우기.** 흐름 로그를 지우면 새 레코드가 더 생기지 않지만 이미 보낸 데이터는 보낸 곳에 남습니다[2]. 지운 작업은 CloudTrail 에 `eventName` 이 `DeleteFlowLogs` 인 레코드로 남고, 성공한 삭제만 고르려면 `errorCode` 가 없거나 `Success` 인 레코드를 찾습니다[9]. 설정을 바꿀 수 없어서 형식을 바꾸려는 관리 작업도 지웠다가 새로 만드는 모양이 되므로[5], 지운 뒤 같은 자원에 새 흐름 로그가 생겼는지 함께 봅니다. 지운 뒤 보낸 곳의 로그 그룹·버킷 데이터까지 지웠는지는 그쪽 기록에서 확인합니다. 흐름은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md) 에서 다룹니다.

## 직접 분석해 보기

**원본 텍스트 직접 읽기.** S3 에서 받은 파일은 gzip 으로 묶인 텍스트이므로 풀어서 앞 몇 줄을 봅니다. 첫 줄이 필드 이름 머리줄인지, 필드 수가 몇 개인지부터 확인하고 설정의 형식과 맞춰 봅니다.

```bash
zcat 123456789012_vpcflowlogs_us-east-1_fl-*.log.gz | head -5
zcat *.log.gz | awk '{print NF}' | sort | uniq -c
```

기본 형식이라면 11번째·12번째 필드가 `start`·`end` 입니다. 아래는 거부된 흐름만 골라 시각을 UTC 로 풀어 보는 예입니다.

```bash
zcat *.log.gz | awk '$13=="REJECT"' | while read v acct eni src dst sp dp proto pk by st en act ls; do
  echo "$(date -u -d @$st +%FT%TZ) $(date -u -d @$en +%FT%TZ) $eni $src:$sp -> $dst:$dp p=$proto $pk pkts $by bytes $act"
done
```

바깥 주소별로 나간 바이트를 더하면 많이 보낸 상대가 드러납니다. 인스턴스 주소가 198.51.100.10 인 만든 예시라면 아래처럼 씁니다.

```bash
zcat *.log.gz | awk '$4=="198.51.100.10" && $13=="ACCEPT" {b[$5]+=$10} END {for (d in b) print b[d], d}' | sort -rn | head
```

CloudWatch Logs 로 보낸 흐름 로그는 로그 그룹에서 스트림(인터페이스)별로 받아 같은 방식으로 읽고, 받는 방법은 [CloudWatch Logs](cloudwatch-logs.md) 와 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md) 에서 다룹니다.

**공개 도구로 읽기.** Invictus-AWS 는 계정의 흐름 로그 설정을 훑어 S3 로 보내는 흐름 로그의 버킷 이름을 모읍니다[10]. 그 버킷에서 위 경로 규칙으로 날짜 범위의 파일을 받고, 위의 명령으로 거릅니다.

## 교차 검증

- [CloudTrail](cloudtrail/index.md) — 흐름 로그를 지운 기록(`DeleteFlowLogs`)과, 같은 시간대에 인스턴스·보안 그룹을 바꾼 API 호출을 찾습니다. VPC 끝점을 거친 API 호출은 [관리 이벤트와 데이터 이벤트](cloudtrail/event-types.md) 의 네트워크 활동 이벤트와 맞춰 봅니다.
- [GuardDuty](guardduty.md) — GuardDuty 는 흐름 로그를 자체 복제본으로 분석하므로, 계정에 흐름 로그가 없어도 네트워크 관련 결과가 있을 수 있습니다[8].
- [S3 접근 기록](s3-access-logs.md) — `pkt-dst-aws-service` 가 `S3` 인 큰 흐름이 있으면 같은 시간대의 S3 요청 기록에서 어느 객체였는지 찾습니다.
- [EC2 인스턴스와 스냅숏](ec2-ebs.md) — `instance-id`·인터페이스 ID 로 인스턴스를 찾고, 인스턴스 안의 기록은 [클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html) 으로 확보해 [인증 로그](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/logins/auth-log.html) 의 SSH 로그인과 맞춰 봅니다.
- [네트워크 흐름 로그](../azure/flow-logs.md), [VPC 흐름 로그 (Google Cloud)](../gcp/vpc-flow-logs.md) — 다른 클라우드의 같은 역할을 하는 기록입니다.
- [클라우드 저장소에서 자료를 빼 갔나](../../04-scenarios/data-leak/storage-exfiltration.md), [채굴용 자원을 만들었나](../../04-scenarios/infrastructure/cryptomining.md) — 이 쪽의 기록을 조사 흐름으로 묶습니다.

## 실습

AWS 문서의 예시 레코드[4]와 위의 만든 예시로 풀어 봅니다.

1. 위 만든 예시 첫 줄의 `start`·`end` 를 UTC 로 풀고, 실제 첫 패킷 시각이 들어갈 수 있는 범위를 적어 봅니다.
2. 문서의 ping 예시에서 `ACCEPT` 줄과 `REJECT` 줄이 각각 어느 방향이고, 왜 응답만 거부됐는지 보안 그룹·네트워크 ACL 로 설명해 봅니다[4].
3. 문서의 TCP 플래그 예시에서 연결을 먼저 연 쪽이 어느 주소인지, `tcp-flags` 값 3 과 19 가 무엇을 뜻하는지 적어 봅니다[4].
4. 문서의 NAT 게이트웨이 예시에서 `dstaddr` 와 `pkt-dstaddr` 가 다른 줄을 골라, 보고서에 인터넷 쪽 상대 주소로 어느 값을 써야 하는지 적어 봅니다[4].
5. 인스턴스가 메타데이터 서비스에서 자격 증명을 받아 갔는지 흐름 로그로 확인할 수 있는지 판단하고, 대신 볼 기록을 적어 봅니다.
6. 실제 계정에서는 흐름 로그 설정을 받아 어느 자원에 어떤 형식·어느 보낸 곳으로 켜져 있는지 표로 만들고, 사고 시각에 기록이 있을 자원과 없을 자원을 나눠 봅니다.

## 참고 문헌

1. AWS, "Logging IP traffic using VPC Flow Logs", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html
2. AWS, "Flow logs basics", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-basics.html
3. AWS, "Flow log records", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html
4. AWS, "Flow log record examples", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-records-examples.html
5. AWS, "Flow log limitations", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-limitations.html
6. AWS, "Flow log files", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-s3-path.html
7. AWS, "Publish flow logs to CloudWatch Logs", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-cwl.html
8. AWS, "GuardDuty foundational data sources", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_data-sources.html
9. SigmaHQ, aws_cloudtrail_vpc_flow_logs_deleted.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_vpc_flow_logs_deleted.yml
10. Invictus Incident Response, Invictus-AWS, source/main/logs.py. https://github.com/invictus-ir/Invictus-AWS/blob/main/source/main/logs.py
