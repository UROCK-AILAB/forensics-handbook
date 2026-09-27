---
title: "GuardDuty"
parent: "아티팩트 · AWS"
nav_order: 420
---

# GuardDuty

AWS 가 계정의 로그를 따로 받아 분석하고 수상한 활동을 "결과 (finding)" 로 남기는 위협 탐지 서비스이고, 결과 하나는 어느 자원·자격 증명에 어떤 유형의 활동이 언제부터 언제까지 몇 번 있었는지를 알려 줍니다.

## 무엇을 기록하나 · 왜 생기나

GuardDuty 를 켜면 기반 데이터 원천 (foundational data sources) 세 가지를 따로 설정하지 않아도 곧바로 분석합니다. CloudTrail 관리 이벤트, EC2 인스턴스의 VPC 흐름 로그, Route53 Resolver DNS 질의 로그가 그 셋입니다[1][2]. GuardDuty 는 각 원천을 계정의 설정과 무관한 "독립된 복제 스트림" 으로 받아 필요한 필드만 뽑아 분석하고, 원래 로그는 버립니다[2]. 그래서 GuardDuty 를 켜도 계정의 CloudTrail·흐름 로그 설정은 바뀌지 않고, GuardDuty 가 본 로그를 계정에 넘겨주지도 않습니다[2].

GuardDuty 가 남기는 것은 로그가 아니라 판단입니다. 위협 정보 목록(악성 IP·도메인·파일 해시)과 기계 학습 모델로 수상하다고 본 활동마다 결과를 만들고[1], 같은 문제가 되풀이되면 새 결과 대신 기존 결과를 갱신합니다[7]. 결과 이름은 아래 형식을 따릅니다[3].

```text
ThreatPurpose:ResourceTypeAffected/ThreatFamilyName.DetectionMechanism!Artifact
```

`Recon:EC2/PortProbeUnprotectedPort` 는 EC2 인스턴스의 열린 포트를 누군가 스캔하고 있다는 뜻이고, `CryptoCurrency:EC2/BitcoinTool.B!DNS` 는 EC2 인스턴스가 알려진 비트코인 관련 도메인과 통신한다는 뜻이고, 끝의 `!DNS` 가 악성 활동에 쓰인 도구의 자원을 가리키는 산출물 (artifact) 자리입니다[3]. 이 자리는 결과 유형에 따라 없을 수도 있습니다[3]. 탐지 방식 자리에 `.Custom` 이 붙으면 계정이 등록한 위협 목록으로, `.Reputation` 이 붙으면 도메인 평판 모델로 찾은 것입니다[3]. 맨 앞의 위협 목적 (threat purpose) 에는 `Backdoor`, `Behavior`, `CredentialAccess`, `Cryptocurrency`, `DefenseEvasion`, `Discovery`, `Execution`, `Exfiltration`, `Impact`, `InitialAccess`, `Pentest`, `Persistence`, `Policy`, `PrivilegeEscalation`, `Recon`, `Stealth`, `Trojan`, `UnauthorizedAccess` 가 오고, 이 가운데 여럿은 MITRE ATT&CK 전술과 짝이 맞습니다[3].

## 위치와 버전별 차이

### 무엇을 켰느냐에 따른 차이 (2026년 9월 문서 기준)

GuardDuty 는 리전 단위 서비스라서 리전마다 켭니다[2]. 한 리전에서 처음 켜면 30일 무료 체험이 붙고, 이때 Runtime Monitoring 을 뺀 보호 계획 (protection plan) 이 모두 자동으로 켜집니다[1][2]. 이미 GuardDuty 를 쓰던 계정에는 나중에 나온 보호 계획이 자동으로 켜지지 않습니다[1]. 여러 단계 공격을 묶어 보는 Extended Threat Detection 은 GuardDuty 를 켜면 추가 비용 없이 켜집니다[1].

| 탐지 원천 | 켜는 방식 | 원천 기록이 계정에 따로 있나 |
|---|---|---|
| CloudTrail 관리 이벤트 | 기본(GuardDuty 를 켜면 바로)[2] | 트레일·이벤트 기록은 CloudTrail 설정을 따름[2] |
| VPC 흐름 로그(EC2) | 기본[2] | 계정이 흐름 로그를 만들어 둔 경우만[2] |
| Route53 Resolver DNS 질의 로그 | 기본. AWS 기본 리졸버를 쓸 때만 분석, OpenDNS·GoogleDNS·자체 리졸버면 분석하지 못함[2] | Route 53 Resolver 질의 로깅을 따로 켠 경우만[2] |
| S3 Protection | 보호 계획. CloudTrail 의 S3 데이터 이벤트를 분석[1] | 트레일에 S3 데이터 이벤트를 켠 경우만 |
| EKS Protection | 보호 계획. EKS 감사 로그를 자체 스트림으로 분석[11] | EKS 제어 평면 로깅을 켠 경우만[11] |
| Runtime Monitoring | 보호 계획(자동으로 켜지지 않음[1]). EKS·ECS on Fargate·EC2 에 보안 에이전트를 두고 파일 접근·프로세스 실행·명령줄·네트워크 연결을 봄. EKS on Fargate 는 지원하지 않음[12] | 없음 |
| Malware Protection for EC2 | 보호 계획. 인스턴스에 붙은 EBS 볼륨을 스캔. Fargate 워크로드는 지원하지 않음[10] | 악성코드가 나왔을 때 스냅숏을 보관하도록 설정한 경우만[10] |
| Lambda Protection | 보호 계획. VPC 네트워킹을 쓰지 않는 함수까지 모든 Lambda 함수의 흐름 로그를 분석[2] | 없음 |
| RDS Protection, Malware Protection for S3·AWS Backup, AI Protection | 보호 계획[1] | 원천마다 다름 |

기반 원천을 분석한다고 해서 원천 로그가 남는 것이 아니므로, GuardDuty 결과는 있는데 그 결과를 뒷받침할 흐름 로그·DNS 로그는 계정에 없을 수 있습니다[2]. 로그 종류와 보관 기간 전반은 [로그의 종류](../../01-foundations/logging/log-types.md) 와 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 에서 다룹니다.

### 결과는 어디에 있나

GuardDuty 는 결과를 90일 동안 보관합니다[8]. 그보다 오래 두려면 내보내기를 미리 설정해 두어야 하고, 내보낼 곳은 아래와 같습니다.

| 어디서 | 무엇이 | 언제 |
|---|---|---|
| GuardDuty 콘솔·API·CLI | 보관 중인 결과 전부(보관 처리한 결과 포함)[6][9] | 90일까지[8] |
| Amazon EventBridge | 새 활성 결과와 기존 결과의 갱신[8] | 새 결과는 만들어진 뒤 약 5분 안, 갱신은 설정한 주기[8] |
| S3 버킷(선택) | 활성 결과. 보관 처리한 결과는 기본으로 내보내지 않음[8] | 갱신은 15분·1시간·6시간 가운데 고른 주기(기본 6시간)[8] |
| AWS Security Hub CSPM, Amazon Detective | 연동한 경우 결과 사본[1][8] | 연동 설정을 따름 |

S3 내보내기는 리전마다 따로 설정하고, GuardDuty 가 KMS 키로 암호화해서 씁니다[8]. 버킷과 KMS 키는 같은 리전에 있어야 합니다[8]. 위임 관리자 계정에서 설정하면 같은 리전의 멤버 계정 결과도 같은 곳으로 나갑니다[8]. GuardDuty 는 폴더를 만들어 주지 않으므로 아래 경로를 미리 만들어 두어야 하고, 객체의 전체 경로는 둘째 줄 모양으로 이름 끝이 `.jsonl.gz` 입니다[8].

```text
/AWSLogs/123456789012/GuardDuty/Region
amzn-s3-demo-bucket/prefix-name/UUID.jsonl.gz
```

파일 이름의 UUID 는 무작위로 만든 값이라 탐지기 ID 나 결과 ID 와 관계가 없습니다[8]. 실제 버킷의 경로는 설정한 접두사에 따라 달라지므로 받아 오기 전에 버킷 목록을 먼저 봅니다.

## 구조

### 개요 필드

결과마다 들어 있는 정보는 결과 유형에 따라 다르고, 개요 (overview) 에는 결과를 알아보는 기본 값이 아래처럼 들어 있습니다[6]. 이름은 콘솔에 보이는 이름이고, JSON 에서 같은 값이 어떤 키 이름으로 나오는지는 받은 결과나 샘플 결과에서 확인합니다.

| 필드 | 뜻 |
|---|---|
| Account ID | 활동이 일어난 계정[6] |
| Region | 결과를 만든 리전[6] |
| Finding ID | 이 결과 유형과 매개변수 묶음의 고유 ID. 같은 모양의 새 활동은 이 ID 로 합쳐짐[6] |
| Finding type | 위 형식의 결과 유형 이름[6] |
| Resource ID | 활동의 대상이 된 AWS 자원 ID[6] |
| Severity | Critical 9.0–10.0, High 7.0–8.9, Medium 4.0–6.9, Low 1.0–3.9[5][6] |
| Count | 이 결과 ID 로 합친 활동 횟수[6] |
| Created at | 결과를 처음 만든 시각[6] |
| Updated at | 같은 모양의 새 활동으로 마지막으로 갱신한 시각[6] |
| Scan ID | Malware Protection for EC2 스캔 식별자[6] |

심각도는 같은 유형이라도 상황에 따라 달라질 수 있습니다[5]. 결과 유형 목록에서 `Low*` 처럼 별표가 붙은 유형이 그런 경우입니다[4].

### 자원과 행위

자원 역할 (resource role) 이 `TARGET` 이면 계정의 자원이 공격을 받은 쪽이고 결과에 Actor 절이 붙습니다[6]. `ACTOR` 이면 계정의 자원이 바깥으로 수상한 활동을 한 쪽이고 Target 절이 붙습니다[6]. Runtime Monitoring 결과와 Malware Protection for S3 결과에는 자원 역할이 채워지지 않습니다[6]. 자원 종류는 `Instance`, `AccessKey`, `S3Bucket`, `S3Object`, `KubernetesCluster`, `ECSCluster`, `Container`, `RDSDBInstance`, `RDSLimitlessDB`, `Lambda` 가운데 하나 이상이고[6], `AccessKey` 에는 액세스 키 ID·주체 ID·사용자 이름과 CloudTrail `userIdentity` 와 같은 사용자 유형이 들어갑니다[6].

행위 (action) 종류는 다섯 가지입니다[6].

| 행위 종류 | 뜻 | 더 붙는 정보 |
|---|---|---|
| `NETWORK_CONNECTION` | 인스턴스와 원격 호스트 사이에 트래픽이 오감 | 연결 방향 `INBOUND`·`OUTBOUND`·`UNKNOWN`, 프로토콜, Local IP, Blocked[6] |
| `PORT_PROBE` | 원격 호스트가 인스턴스의 열린 포트 여럿을 스캔함 | Local IP, Blocked[6] |
| `DNS_REQUEST` | 인스턴스가 도메인 이름을 질의함 | 프로토콜, Blocked[6] |
| `AWS_API_CALL` | AWS API 를 호출함(CloudTrail 의 API 아닌 이벤트 포함) | API 이름, 사용자 에이전트, 실패했으면 오류 코드, 서비스 이름[6] |
| `RDS_LOGIN_ATTEMPT` | 원격 IP 에서 데이터베이스 로그인을 시도함 | 원격 IP[6] |

Local IP 는 중간 계층을 거치기 전의 원래 출발지 주소라서, EKS 파드 주소와 파드가 도는 인스턴스 주소를 가를 때 씁니다[6]. Actor·Target 절에는 원격 IP 와 포트, 위치, ISP 조직, 도메인, 원격 호출자가 이 GuardDuty 환경과 관련된 계정인지를 뜻하는 Affiliated, 원격 계정 ID 가 들어갈 수 있습니다[6]. 위치와 네트워크는 MaxMind GeoIP 데이터베이스로 정하고, 나라 수준의 정확도는 높지만 나라와 IP 주소 종류에 따라 정확도가 달라집니다[6]. 위치 정보를 읽는 법은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md) 에서 다룹니다.

### 덧붙는 절

모든 결과에는 추가 정보 (additional information) 절이 있고, 위협 목록 이름, 샘플 결과인지를 뜻하는 Sample, 보관 처리했는지를 뜻하는 Archived, 전에 보지 못한 사용자·위치·시각·버킷·ASN 조직 같은 Unusual 값이 들어갑니다[6]. 위협 정보로 찾은 결과에는 위협 이름과 파일 SHA256 이 담긴 Evidence 절이 붙습니다[6].

이름이 `AnomalousBehavior` 로 끝나는 결과는 이상 탐지 기계 학습 모델이 만든 것입니다[6]. 이 결과의 Anomalous APIs 목록은 첫 줄이 결과를 일으킨 주 API 이고, 나머지는 같은 사용자 신원이 그 근처에 부른 다른 이상한 API 입니다[6]. 사용자 신원 유형은 `Root`, `IAMUser`, `AssumedRole`, `FederatedUser`, `AWSAccount`, `AWSService` 가운데 하나로 CloudTrail 과 같습니다[6]. 신원 유형 읽는 법은 [레코드 구조](cloudtrail/record-structure.md) 에서 다룹니다.

Malware Protection for EC2 결과에는 위협 이름, 파일의 SHA-256, EBS 볼륨 안 파일 경로와 파일 이름, 볼륨 ARN, 스냅숏 ARN, 스캔 시작·끝 시각, 스캔을 일으킨 결과 ID(Trigger finding ID)가 들어 있습니다[6]. 스캔 엔진 출처는 `Bitdefender` 또는 `Amazon` 입니다[6].

아래는 결과 하나의 개요를 콘솔 필드 이름으로 옮겨 본 만든 예시입니다. 모든 값은 지어낸 것이고, 계정 ID·IP 는 문서용 값입니다.

```text
Finding type  UnauthorizedAccess:EC2/SSHBruteForce
Severity      Low
Region        ap-northeast-2
Account ID    123456789012
Resource ID   i-0a1b2c3d4e5f60718
Resource role TARGET
Action type   NETWORK_CONNECTION (INBOUND, TCP, 22)
Actor IP      203.0.113.25
Count         412
Created at    2026-09-01T02:14:05Z
Updated at    2026-09-01T03:52:40Z
```

### 자주 보는 결과 유형

| 결과 유형 | 자원 | 원천 | 기본 심각도 |
|---|---|---|---|
| `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS` | IAM | CloudTrail 관리 이벤트 또는 S3 데이터 이벤트 | High[4] |
| `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.InsideAWS` | IAM | CloudTrail 관리 이벤트 | High*[4] |
| `Policy:IAMUser/RootCredentialUsage` | IAM | CloudTrail 관리 이벤트 또는 S3 데이터 이벤트 | Low[4] |
| `Stealth:IAMUser/CloudTrailLoggingDisabled` | IAM | CloudTrail 관리 이벤트 | Low[4] |
| `UnauthorizedAccess:EC2/SSHBruteForce` | EC2 | VPC 흐름 로그 | Low*[4] |
| `CryptoCurrency:EC2/BitcoinTool.B!DNS` | EC2 | DNS 로그 | High[4] |
| `Exfiltration:S3/AnomalousBehavior` | S3 | CloudTrail S3 데이터 이벤트 | High[4] |
| `CredentialAccess:Kubernetes/SuccessfulAnonymousAccess` | Kubernetes | EKS 감사 로그 | High[4] |
| `DefenseEvasion:Runtime/ProcessInjection.Ptrace` | 인스턴스·EKS·ECS·컨테이너 | Runtime Monitoring | Medium[4] |
| `AttackSequence:S3/CompromisedData` | 공격 흐름에 얽힌 자원 | CloudTrail 관리 이벤트와 S3 데이터 이벤트 | Critical[4] |

IAM 쪽 결과가 가리키는 자격 증명은 [IAM 사용자·역할·액세스 키](iam.md) 에서, S3 쪽 결과는 [S3 접근 기록](s3-access-logs.md) 에서 원래 요청과 맞춰 봅니다.

## 증거로서 의미

**증명하는 것.** GuardDuty 가 이 리전에서 이 자원이나 자격 증명에 대해 이 유형의 활동을 탐지했고, 그 활동이 `Created at` 부터 `Updated at` 사이에 `Count` 번 합쳐졌다는 점을 보여 줍니다[6][7]. `AccessKey` 자원과 `AWS_API_CALL` 행위가 있으면 어느 액세스 키가 어느 API 를 어떤 사용자 에이전트로 불렀는지까지 알 수 있고[6], Malware Protection 결과는 볼륨 안 어느 경로에 어떤 SHA-256 의 파일이 있었는지를 알려 줍니다[6].

**증명하지 못하는 것.** 결과는 판단이지 원본 기록이 아닙니다. GuardDuty 는 분석한 원천 로그를 계정에 주지 않으므로[2], 활동 하나하나는 [CloudTrail](cloudtrail/index.md)·[VPC 흐름 로그](vpc-flow-logs.md)·DNS 로그에서 다시 찾아야 하고, 그 로그를 계정이 따로 남기지 않았다면 결과만 남습니다. 결과가 합쳐질 때 원격 IP 같은 세부 값은 가장 최근 것으로 덮어쓰므로, 결과에 보이는 IP 가 첫 시도의 IP 라고 볼 수 없습니다[7]. GuardDuty 를 켜기 전, 켜지 않은 리전, 켜지 않은 보호 계획, 90일이 지난 결과(내보내기를 설정하지 않았다면)는 알 수 없습니다[2][8]. 결과가 없다는 것도 활동이 없었다는 뜻이 아니고, GuardDuty 의 탐지 조건에 걸린 활동이 없었다는 뜻일 뿐입니다. `Pentest` 유형은 알려진 침투 시험 도구가 만드는 활동과 비슷하다는 뜻이고, GuardDuty 는 그 활동의 진짜 목적을 구분하지 못합니다[3].

보고서에는 "2026-09-01 02:14~03:52 UTC 사이 GuardDuty 가 인스턴스 i-0a1b2c3d4e5f60718 에 대한 SSH 무차별 대입 결과를 412회 합쳐 기록했고, 마지막으로 기록된 원격 주소는 203.0.113.25 이다" 처럼 결과로 확인되는 만큼만 씁니다(만든 예시). 로그인이 성공했는지는 인스턴스 안의 [인증 로그](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/logins/auth-log.html) 로 따로 확인합니다. 문장 쓰는 법은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에서 다룹니다.

## 시각 해석

`Created at` 은 결과를 처음 만든 시각이고 `Updated at` 은 같은 모양의 새 활동으로 마지막에 갱신한 시각입니다[6]. 두 값이 다르면 활동이 여러 번 있었고 이어지고 있다는 뜻입니다[6]. 둘 다 GuardDuty 가 결과를 만들고 고친 시각이지 원래 API 호출이나 패킷의 시각이 아니므로, 초 단위 사건 시각은 원천 로그에서 가져옵니다.

콘솔은 결과 시각을 보는 사람의 현지 시간대로 보여 주고, JSON 내보내기와 CLI 출력은 UTC 로 줍니다[6]. 콘솔 화면을 캡처해 증거로 쓸 때는 화면의 시간대를 함께 적습니다. Runtime Monitoring 의 프로세스 시작 시각 같은 값은 `2023-03-22T19:37:20.168Z` 모양의 UTC 문자열이고, ECS 태스크의 생성·시작 시각은 Unix 시각입니다[6]. 인스턴스의 Launch Time, EKS 클러스터의 Created At 은 결과 시각과 다른 자원 자체의 시각입니다[6].

내보낸 기록이 쌓이는 시각은 따로 있습니다. 새 활성 결과는 만들어진 뒤 약 5분 안에 EventBridge 로 나가지만, 기존 결과의 갱신은 설정한 주기(기본 6시간)마다 EventBridge 와 S3 로 한꺼번에 나갑니다[8]. 6시간 주기라면 12:00 에 내보낸 뒤 갱신된 결과는 18:00 에야 나가므로[8], S3 의 기록만 보면 갱신이 늦게 일어난 것처럼 보일 수 있습니다. 여러 기록의 시각을 맞추는 법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 과 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 함정과 한계

- **리전 값.** IAM·STS·S3·CloudFront·Route 53 같은 글로벌 서비스 이벤트는 GuardDuty 를 켠 리전마다 복제해 처리하므로, 결과의 Region 이 탐지를 만든 리전과 다를 수 있고 `us-east-1` 로 보이기도 합니다[2]. 결과를 모을 때는 켜 둔 모든 리전을 살펴봅니다.
- **합쳐진 결과.** 같은 문제는 결과 ID 하나로 합쳐지고 세부 값은 최신 것으로 바뀝니다[7]. 대상 자원이 새로 바뀌면 새 결과를 만들고[7], 공격 흐름 (attack sequence) 결과는 같은 흐름에서 비슷한 신호를 볼 때만 합쳐집니다[7]. 결과 개수를 사건 개수로 세지 않습니다.
- **샘플 결과.** 콘솔·API·CLI 로 만든 샘플 결과는 지어낸 값을 담고 제목에 `[SAMPLE]` 이 붙습니다[9]. 추가 정보의 Sample 값도 함께 보고 실제 결과와 가릅니다[6].
- **보관 처리와 억제.** 보관 처리한 결과와 억제 규칙에 걸린 새 결과는 기본으로 S3 로 내보내지 않습니다[8]. 콘솔의 활성 목록이나 S3 내보내기에만 기대면 이런 결과를 놓치므로, API 로 받을 때 보관 처리한 결과까지 받고 Archived 값을 봅니다[6].
- **인스턴스 정보 빠짐.** 인스턴스가 이미 멈췄거나 다른 리전의 인스턴스에서 API 를 불렀으면 인스턴스 세부 정보가 비어 있을 수 있습니다[6].
- **보지 못하는 트래픽.** 흐름 로그를 원천으로 쓰는 EC2 결과는 IPv6 트래픽을 다루지 않습니다[4]. 인스턴스가 AWS 기본 리졸버가 아닌 DNS 리졸버를 쓰면 DNS 원천을 분석하지 못하고, AWS Outposts 의 인스턴스는 DNS 로그를 보지 못합니다[2].
- **악성코드 스캔 주기.** GuardDuty 가 스스로 여는 스캔은 24시간에 한 번만 자동으로 시작되고, 사람이 여는 스캔은 앞 스캔 시작 뒤 1시간이 지나야 다시 돌릴 수 있습니다[10]. 태그로 스캔에서 뺀 인스턴스는 자동 스캔하지 않습니다[10]. Malware Protection for S3 는 압축 파일 안의 위협을 첫 번째 것만 알리고, 해시를 계산하지 못하면 빈 문자열의 SHA-256(`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)을 넣습니다[6]. 이 해시 값으로 파일을 찾으면 안 됩니다.
- **끄기와 방해.** 탐지기를 지우거나 끄는 작업은 CloudTrail 에 `eventSource` 가 `guardduty.amazonaws.com` 이고 `eventName` 이 `DeleteDetector` 이거나, `UpdateDetector` 에 `requestParameters.enable` 이 `false` 인 레코드로 남습니다[13]. 탐지기를 지우면 모니터링이 멈추고 기존 결과도 사라집니다[13]. 신뢰 IP 목록을 추가하는 `CreateIPSet` 은 특정 주소의 경고를 끄는 데 쓰일 수 있고[14], GuardDuty 결과를 모아 보는 Security Hub 에서는 `BatchUpdateFindings`, `DeleteInsight`, `UpdateFindings`, `UpdateInsight` 로 결과 상태를 바꿀 수 있습니다[15]. 결과가 사라진 구간이 있으면 이 레코드부터 찾고, 흐름은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md) 에서 다룹니다.

## 직접 분석해 보기

**내보낸 원본 파일 읽기.** S3 로 내보낸 객체는 이름 끝이 `.jsonl.gz` 라서[8] gzip 으로 묶은 JSON Lines 일 가능성이 있으므로, 받은 파일을 풀어 한 줄이 결과 하나인지부터 확인합니다. 버킷의 경로를 먼저 살펴보고, 받은 파일의 첫 줄에서 최상위 키 이름을 확인한 뒤 필요한 값을 뽑습니다. 키 이름은 파일에서 나온 그대로 씁니다.

```bash
aws s3 ls s3://amzn-s3-demo-bucket/AWSLogs/123456789012/GuardDuty/ --recursive
zcat *.jsonl.gz | head -1 | jq 'keys'
zcat *.jsonl.gz | head -1 | jq '.'
```

객체는 GuardDuty 가 KMS 키로 암호화해 두었으므로[8], 받을 때 권한 오류가 나면 그 키의 정책을 확인합니다. 같은 결과 ID 가 여러 파일에 되풀이해 나오면 갱신 주기마다 내보낸 것이므로[8], 결과 ID 별로 가장 늦게 갱신된 줄을 남기고 앞의 줄은 갱신 이력으로 봅니다.

**API 로 받기.** Invictus-AWS 는 `list_detectors` 로 탐지기 ID 를 받고, 탐지기마다 `list_findings` 로 결과 ID 를 모은 뒤 `get_findings` 로 결과 전체를 JSON 파일에 담습니다[16]. 같은 흐름을 리전마다 돌리면 됩니다.

```python
import boto3, json
for region in ["us-east-1", "ap-northeast-2"]:          # 켜 둔 리전 전부
    gd = boto3.client("guardduty", region_name=region)
    for det in gd.list_detectors()["DetectorIds"]:
        ids = gd.list_findings(DetectorId=det)["FindingIds"]
        if ids:
            res = gd.get_findings(DetectorId=det, FindingIds=ids)
            res.pop("ResponseMetadata", None)
            json.dump(res, open(f"gd_{region}_{det}.json", "w"), default=str)
```

결과가 많으면 목록이 여러 페이지로 나뉘므로 다음 페이지 토큰으로 끝까지 받습니다(Invictus-AWS 는 이 부분을 페이지 넘김 함수로 처리합니다[16]). 90일 보관 때문에 사고를 알게 된 즉시 받아 두고, 수집 순서는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 와 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md) 에서 다룹니다.

## 교차 검증

- [CloudTrail](cloudtrail/index.md) — `AWS_API_CALL` 결과의 API 이름·액세스 키·시간대로 원래 레코드를 찾고, GuardDuty 를 끄거나 방해한 `guardduty.amazonaws.com` 레코드를 봅니다. S3 쪽 결과는 [관리 이벤트와 데이터 이벤트](cloudtrail/event-types.md) 의 S3 데이터 이벤트가 켜져 있어야 원본이 있습니다.
- [VPC 흐름 로그](vpc-flow-logs.md) — `NETWORK_CONNECTION`·`PORT_PROBE` 결과의 원격 IP·포트로 흐름을 찾아, 합쳐지며 덮어쓴 앞선 원격 주소를 되살립니다[7].
- [IAM 사용자·역할·액세스 키](iam.md) — IAM 결과가 가리키는 사용자·역할과 키가 언제 만들어지고 누가 썼는지 봅니다.
- [EC2 인스턴스와 스냅숏](ec2-ebs.md) — Malware Protection 이 보관한 스냅숏이나 새 스냅숏으로 볼륨을 확보하고, 결과의 파일 경로와 SHA-256 을 디스크에서 확인합니다. 인스턴스 안 수집은 [클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html) 에서 다룹니다.
- [Lambda·컨테이너 서비스 기록](lambda-containers.md), [CloudWatch Logs](cloudwatch-logs.md) — EKS·Runtime Monitoring 결과의 파드·컨테이너를 제어 평면 로그와 컨테이너 로그로 맞춰 봅니다. GuardDuty 가 EKS 감사 로그를 봤더라도 제어 평면 로깅을 켜지 않았다면 계정에는 감사 로그가 없습니다[11].
- [Defender 경고와 기록](../m365/defender-xdr.md) — Microsoft 365 쪽에서 같은 역할을 하는 탐지 결과입니다.
- [액세스 키가 새어 나갔나](../../04-scenarios/infrastructure/leaked-keys.md), [채굴용 자원을 만들었나](../../04-scenarios/infrastructure/cryptomining.md), [클라우드 저장소에서 자료를 빼 갔나](../../04-scenarios/data-leak/storage-exfiltration.md) — 이 페이지의 결과를 조사 흐름으로 묶습니다.

## 실습

GuardDuty 결과는 공개된 실제 결과가 드물어서, 조사용이 아닌 시험 계정에서 샘플 결과를 만들어 풀어 봅니다[9].

1. 시험 계정의 한 리전에서 샘플 결과를 만들고, 제목의 `[SAMPLE]` 과 추가 정보의 Sample 값이 JSON 에서 어느 키로 나오는지 적어 봅니다.
2. 같은 결과를 콘솔과 CLI 로 각각 보고, `Created at`·`Updated at` 이 어떻게 다르게 보이는지 시간대로 설명해 봅니다.
3. `UnauthorizedAccess:EC2/SSHBruteForce` 샘플에서 `Count` 와 Actor IP 를 보고, 이 결과만으로 첫 공격 주소를 쓸 수 있는지 판단한 뒤 대신 볼 기록을 적어 봅니다.
4. `Policy:IAMUser/RootCredentialUsage` 샘플의 API 이름과 사용자 에이전트를 CloudTrail 레코드에서 어느 필드와 맞춰 볼지 적어 봅니다.
5. 실제 계정이라면 모든 리전의 탐지기 상태, 켜진 보호 계획, S3 내보내기 설정과 갱신 주기를 표로 만들고, 사고 시각에 결과가 있을 수 있는 리전과 없을 리전을 나눠 봅니다.
6. CloudTrail 에서 `DeleteDetector`, `UpdateDetector`, `CreateIPSet` 을 찾아, 결과가 비는 구간과 겹치는지 확인해 봅니다.

## 참고 문헌

1. AWS, "What is Amazon GuardDuty?", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html
2. AWS, "GuardDuty foundational data sources", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_data-sources.html
3. AWS, "GuardDuty finding format", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-format.html
4. AWS, "GuardDuty finding types", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-active.html
5. AWS, "Severity levels of GuardDuty findings", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings-severity.html
6. AWS, "Finding details", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings-summary.html
7. AWS, "GuardDuty finding aggregation", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/finding-aggregation.html
8. AWS, "Exporting generated GuardDuty findings to Amazon S3 buckets", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_exportfindings.html
9. AWS, "Understanding and generating Amazon GuardDuty findings", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_findings.html
10. AWS, "GuardDuty Malware Protection for EC2", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/malware-protection.html
11. AWS, "GuardDuty EKS Protection", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/kubernetes-protection.html
12. AWS, "GuardDuty Runtime Monitoring", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/runtime-monitoring.html
13. SigmaHQ, aws_cloudtrail_guardduty_detector_deleted_or_updated.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_guardduty_detector_deleted_or_updated.yml
14. SigmaHQ, aws_guardduty_disruption.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_guardduty_disruption.yml
15. SigmaHQ, aws_securityhub_finding_evasion.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_securityhub_finding_evasion.yml
16. Invictus Incident Response, Invictus-AWS (source/main/logs.py). https://github.com/invictus-ir/Invictus-AWS
