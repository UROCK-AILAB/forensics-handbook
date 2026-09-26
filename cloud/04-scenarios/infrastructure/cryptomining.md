---
title: "채굴용 자원을 만들었나"
parent: "시나리오 · 인프라 침해"
nav_order: 790
---

# 채굴용 자원을 만들었나 (Cryptomining)

## 조사 질문

클라우드 계정에서 주인이 모르는 컴퓨팅 자원(가상 머신·컨테이너·함수)이 생겼을 때 세 가지를 차례로 묻습니다. 누가 어떤 자격 증명으로 언제 어느 리전·구독·프로젝트에 그 자원을 만들었는지, 그 자원이 채굴과 관련된 통신이나 프로세스를 보였는지, 자원 안에서 무엇을 실행했는지입니다. 앞의 두 질문은 공급자의 관리 로그와 위협 탐지 결과로 답하고, 마지막 질문은 디스크·메모리를 수집해야 답할 수 있습니다.

이 쪽은 컴퓨팅 자원을 만드는 AWS·Azure·Google Cloud 를 다룹니다. 자원을 만든 자격 증명이 어디서 새었는지는 [액세스 키가 새어 나갔나](leaked-keys.md)에서, 그 자격 증명이 권한을 넓혔는지는 [권한을 올렸나](privilege-escalation.md)에서 이어 봅니다.

## 먼저 확인할 것

**어느 리전까지 기록되는가.** AWS 에서 EC2 API 호출은 모두 CloudTrail 관리 이벤트로 남습니다[1]. 콘솔로 만든 트레일은 모두 다중 리전이지만, CLI 로 만든 단일 리전 트레일은 그 리전의 이벤트만 담습니다[1]. 트레일 없이 볼 수 있는 이벤트 기록 (Event history) 은 리전 하나의 최근 90일 관리 이벤트만 보여 주고, 한 번에 리전 하나만 검색합니다[3]. 평소 쓰지 않는 리전에 자원을 만들었을 가능성이 있으므로 트레일 설정부터 확인하고, 이벤트 기록으로 볼 때는 리전을 하나씩 바꿔 가며 봅니다.

**얼마나 남아 있는가.** Azure 활동 로그 (Activity Log) 는 90일 동안 보관한 뒤 지우고, 자원을 만든 사람이 누구인지는 활동 로그에만 남습니다[8]. 90일보다 오래된 생성 기록이 필요하면 진단 설정으로 Log Analytics 작업 영역 등에 내보내 두었는지 확인하고, 내보냈다면 `AzureActivity` 표에서 찾습니다[8]. 보관 기간 전반은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에 정리했습니다.

**탐지 서비스가 켜져 있었는가.** 채굴을 직접 가리키는 기록은 대부분 공급자의 위협 탐지 서비스가 만드는 결과(finding)·경고(alert)이고, 서비스가 꺼져 있었으면 생기지 않습니다. 서비스별 조건은 아래와 같습니다(2026년 9월 문서 기준).

| 공급자 | 서비스 | 채굴 결과가 생기는 조건 |
|---|---|---|
| AWS | GuardDuty | 기본 데이터 원천(VPC 흐름 로그·DNS 로그)으로 EC2 결과가 생기고[6], 프로세스 실행을 보는 결과는 Runtime Monitoring 과 에이전트가 필요함[7] |
| Azure | Defender for Cloud(서버용) | Linux 머신의 호스트 데이터 분석과 ARM 작업 분석으로 경고가 생김[11] |
| Google Cloud | Security Command Center | Premium 또는 Enterprise 등급에서 Event Threat Detection·VM Threat Detection 을 켜야 하고, 채굴 프로그램이 알려진 나쁜 도메인을 부르는 것을 잡으려면 Cloud DNS 로깅도 켜야 함[12]. Enterprise 등급은 2027년 5월 21일에 끝나고 Premium 으로 옮겨 감[12] |

**시각 기준.** CloudTrail `eventTime` 은 요청이 끝난 시각이고 UTC 입니다[2]. Azure 활동 로그 `eventTimestamp` 는 요청을 처리한 Azure 서비스가 이벤트를 만든 시각이고 `Z` 가 붙은 UTC 로 적힙니다[9]. Google Cloud 감사 로그의 `timestamp` 도 `Z` 가 붙은 UTC 입니다[14]. 여러 공급자의 기록을 한 줄로 세우는 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)과 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)을 따릅니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | CloudTrail 관리 이벤트(`RunInstances`, `ImportKeyPair`, `ModifyInstanceAttribute`, `EnableRegion`) | 누가 어떤 키로 언제 어느 리전에 인스턴스를 만들고, 키 쌍을 넣고, 시작 스크립트를 바꾸고, 리전을 켰는지 | [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md) |
| 1 | Azure 활동 로그(`Microsoft.Compute/virtualMachines/write` 등) | 누가 언제 어느 구독에 VM·확장 집합을 만들거나 확장을 설치했는지 | [활동 로그](../../02-artifacts/azure/activity-log.md) |
| 1 | Google Cloud 관리 활동 감사 로그(`v1.compute.instances.insert`) | 누가 언제 어느 프로젝트에 VM 을 만들고 어떤 서비스 계정을 붙였는지 | [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md) |
| 2 | GuardDuty 결과 | 인스턴스가 암호화폐 관련 IP·도메인과 통신했거나 채굴 관련 바이너리를 실행했다는 공급자의 판단 | [GuardDuty](../../02-artifacts/aws/guardduty.md) |
| 2 | Defender for Cloud 경고 | 채굴 관련 프로세스·컨테이너 이미지, 수상한 GPU 확장 설치 | [Azure 가상 머신](../../02-artifacts/azure/azure-vm.md) |
| 2 | Security Command Center 결과 | 채굴 전조(stage-0)와 채굴 실행 중(stage-1) 판단 | [액세스 키가 새어 나갔나](leaked-keys.md) |
| 3 | VPC·NSG 흐름 로그 | 인스턴스가 바깥 어디로 얼마나 연결했는지 | [AWS](../../02-artifacts/aws/vpc-flow-logs.md) · [Azure](../../02-artifacts/azure/flow-logs.md) · [Google Cloud](../../02-artifacts/gcp/vpc-flow-logs.md) |
| 4 | 사용자 데이터와 인스턴스 안의 실행 로그 | 부팅할 때 무엇을 실행하도록 넣었고 실제로 실행했는지 | [EC2 인스턴스와 스냅숏](../../02-artifacts/aws/ec2-ebs.md) |
| 5 | 디스크 스냅숏·메모리 | 자원 안에서 실행한 프로그램과 설정 | [클라우드 가상 머신 수집](../../03-techniques/acquisition/vm-acquisition.md) |

## 분석 흐름

1. **로그부터 지킵니다.** 활동 로그는 90일이 지나면 사라지고[8], 채굴 자원을 지우면 디스크 증거도 함께 사라집니다. 관리 로그를 내보내고 의심 자원의 스냅숏을 먼저 뜹니다. 절차는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md), [클라우드 가상 머신 수집](../../03-techniques/acquisition/vm-acquisition.md), [Linux 판 클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html)을 따릅니다.

2. **자원 생성 기록을 모든 리전에서 찾습니다.** AWS 에서는 `eventSource` 가 `ec2.amazonaws.com` 이고 `eventName` 이 `RunInstances` 인 레코드를 찾고, `userIdentity` 로 호출한 주체와 액세스 키를, `awsRegion` 으로 리전을, `sourceIPAddress` 로 호출한 곳을 봅니다[2]. 아래는 만든 예시입니다.

   ```json
   {
     "eventTime": "2026-09-20T03:12:45Z",
     "eventSource": "ec2.amazonaws.com",
     "eventName": "RunInstances",
     "awsRegion": "ap-southeast-2",
     "sourceIPAddress": "203.0.113.25",
     "userIdentity": {
       "type": "IAMUser",
       "accountId": "123456789012",
       "accessKeyId": "AKIAIOSFODNN7EXAMPLE"
     }
   }
   ```

   Azure 에서는 활동 로그의 `operationName` 이 `Microsoft.Compute/virtualMachines/write`(VM 생성·변경) 또는 `Microsoft.Compute/virtualMachineScaleSets/write` 인 이벤트를 찾고[10], `caller` 로 작업한 사용자의 메일 주소·UPN 또는 서비스 주체의 SPN 을, `resourceId` 로 만든 자원을 봅니다[9]. Sigma 규칙 `azure_creating_number_of_resources_detection` 은 `Microsoft.Compute/virtualMachines/write` 와 `Microsoft.Resources/deployments/write` 를 키워드로 찾습니다[19]. Google Cloud 에서는 관리 활동 로그의 `methodName` 이 `v1.compute.instances.insert` 인 항목에서 `protoPayload.authenticationInfo.principalEmail` 로 만든 사람을, `protoPayload.request.serviceAccounts[0].email` 로 VM 에 붙인 서비스 계정을 봅니다[13]. plaso 의 GCP 로그 파서는 이 기록에서 원본 이미지(`sourceImage`)와 서비스 계정 이메일, 부여한 OAuth 범위(scopes)를 따로 뽑아 줍니다[15].

3. **EC2 말고도 요금을 일으키는 생성 작업을 함께 봅니다.** AWS 가 키가 노출된 IAM 사용자에게 붙이는 관리형 정책 `AWSCompromisedKeyQuarantineV3` 는 "무단 요금으로 이어지는 사기 관련 활동" 을 막으려고 `ec2:RunInstances`, `ec2:RequestSpotInstances`, `ec2:StartInstances`, `lambda:CreateFunction`, `ecs:CreateCluster`, `ecs:CreateService`, `ecs:RegisterTaskDefinition`, `sagemaker:CreateProcessingJob`, `glue:CreateJob`, `codebuild:CreateProject`, `lightsail:Create*`, `organizations:CreateAccount` 같은 작업을 거부합니다[5]. 이 목록은 스폿 인스턴스·컨테이너·함수·빌드 작업처럼 인스턴스가 아닌 자원도 요금을 일으키는 생성 작업으로 볼 수 있다는 근거이고, 이 작업이 있었다고 해서 채굴에 썼다는 뜻은 아닙니다. 쿠버네티스 작업(Job)·크론잡(CronJob)을 만든 기록은 Google Cloud 감사 로그의 `io.k8s.api.batch.v*.Job`·`io.k8s.api.batch.v*.CronJob` 메서드[22], Azure 활동 로그에서 `MICROSOFT.CONTAINERSERVICE/MANAGEDCLUSTERS/BATCH` 등으로 시작해 `/CRONJOBS/WRITE`·`/JOBS/WRITE` 로 끝나는 작업 이름으로 찾습니다[21]. 컨테이너·함수 기록의 모양은 [Lambda·컨테이너 서비스 기록](../../02-artifacts/aws/lambda-containers.md)에 있습니다.

4. **자원을 만들기 전후의 준비 작업을 봅니다.** AWS 에서 새 리전을 켜면 `account.amazonaws.com` 의 `EnableRegion` 이 남습니다[16]. 켜 둔 리전이 보안 감시 범위 밖일 수 있어서, 생성 직전에 이 기록이 있으면 감시가 덜한 리전을 골랐을 가능성이 있습니다. SSH 키 쌍을 들여온 기록은 `ImportKeyPair`[18], 시작 스크립트를 바꾼 기록은 `ModifyInstanceAttribute` 에서 `requestParameters.attribute` 가 `userData` 인 레코드입니다[17]. Azure 에서는 VM 확장 설치가 `Microsoft.Compute/virtualMachines/extensions/write`, 실행 명령이 `Microsoft.Compute/virtualMachines/runCommand/action` 으로 남습니다[10].

5. **공급자의 채굴 판단을 모읍니다.** 아래 이름으로 결과·경고를 찾고, 대상 자원이 2단계에서 찾은 자원과 같은지 맞춰 봅니다.

   | 공급자 | 결과·경고 이름 | 뜻 | 기본 심각도 | 근거 데이터 |
   |---|---|---|---|---|
   | AWS | `CryptoCurrency:EC2/BitcoinTool.B` | EC2 가 암호화폐 관련 IP 에 질의함 | High | VPC 흐름 로그[6] |
   | AWS | `CryptoCurrency:EC2/BitcoinTool.B!DNS` | EC2 가 암호화폐 관련 도메인에 질의함 | High | DNS 로그[6] |
   | AWS | `Impact:EC2/BitcoinDomainRequest.Reputation` | EC2 가 평판이 낮은 암호화폐 관련 도메인에 질의함 | High | DNS 로그[6] |
   | AWS | `Impact:Runtime/CryptoMinerExecuted` | EC2 인스턴스나 컨테이너의 프로세스가 채굴 관련 바이너리를 실행함. 프로세스와 부모 프로세스 계보가 결과에 담김 | High | Runtime Monitoring 에이전트[7] |
   | AWS | `CryptoCurrency:Runtime/BitcoinTool.B`, `CryptoCurrency:Runtime/BitcoinTool.B!DNS`, `Impact:Runtime/BitcoinDomainRequest.Reputation` | 위 EC2 결과와 같은 통신을 에이전트가 봄 | High | Runtime Monitoring 에이전트[7] |
   | Azure | Container with a miner image detected (`VM_MinerInContainerImage`) | 채굴 관련 이미지로 Docker 컨테이너를 실행함 | High | 머신 로그[11] |
   | Azure | Digital currency mining related behavior detected | 채굴에 흔히 쓰는 프로세스·명령을 실행함 | High | 호스트 데이터[11] |
   | Azure | Process associated with digital currency mining detected | 채굴에 흔히 쓰는 프로세스를 실행함. "[seen multiple times]" 가 붙은 경고는 그날 100번 넘게 보인 경우 | Medium | 호스트 데이터[11] |
   | Azure | Suspicious installation of GPU extension in your virtual machine (Preview) (`VM_GPUDriverExtensionUnusualExecution`) | ARM 작업에서 수상한 GPU 드라이버 확장 설치를 봄 | Low | ARM 작업[11] |
   | Google Cloud | `Execution: Cryptomining YARA Rule`, `Execution: Cryptomining Hash Match`, `Execution: Combined Detection` | VM 메모리에서 채굴 프로그램의 패턴(작업 증명 상수 등)이나 해시, 또는 둘 다를 찾음 | — | VM Threat Detection[12] |
   | Google Cloud | `Malware: Bad IP`, `Malware: Bad Domain` | 채굴 프로그램이 쓰는 IP·도메인에 연결하거나 해석함 | — | Event Threat Detection[12] |

   Google Cloud 는 채굴 전조(stage-0)도 따로 나누는데, 서비스 계정 키가 GitHub 에 새었다는 `Account_Has_Leaked_Credentials`, Tor 네트워크 IP 에서 서비스를 바꿨다는 `Evasion: Access from Anonymizing Proxy`, 쓰지 않던 서비스 계정이 움직였다는 `Initial Access: Dormant Service Account Action` 이 여기에 듭니다[12]. 이 결과가 VM 생성보다 앞서 있으면 [액세스 키가 새어 나갔나](leaked-keys.md)의 흐름으로 자격 증명의 출처를 거슬러 올라갑니다.

6. **통신을 흐름 로그로 확인합니다.** 탐지 결과가 가리킨 시간대에 인스턴스가 바깥으로 연결한 주소·바이트 수를 흐름 로그로 확인합니다. GuardDuty 는 인스턴스가 기본 설정인 AWS DNS 리졸버를 쓸 때만 DNS 로그를 분석하고, 다른 공용 리졸버나 자체 리졸버를 쓰면 이 원천을 쓰지 못합니다[24]. 인스턴스가 드문 공용 DNS 리졸버와 통신하면 GuardDuty 는 `DefenseEvasion:EC2/UnusualDNSResolver`(Medium, VPC 흐름 로그)를 남기므로[6], DNS 기반 결과가 없는 이유를 이 결과로 설명할 수 있는지 봅니다.

7. **자원 안을 봅니다.** 부팅 때 실행하도록 넣은 내용은 `aws ec2 describe-instance-attribute --attribute userData` 로 받고, 돌려받은 값은 base64 라서 디코딩한 뒤 읽습니다[4]. Linux 인스턴스에서 실제로 실행한 흔적은 `/var/log/cloud-init-output.log` 와 `/var/lib/cloud/instances/instance-id/` 아래 스크립트 사본에 남습니다[4]. 해석은 [EC2 인스턴스와 스냅숏](../../02-artifacts/aws/ec2-ebs.md)에 있고, 디스크·메모리 분석은 [Linux 판 메모리 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/memory-acquisition.html)과 [Linux 판 타임라인 만들기](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/timeline.html)를 따릅니다.

## 증명하는 것 / 증명하지 못하는 것

관리 로그의 생성 기록(`RunInstances`, `Microsoft.Compute/virtualMachines/write`, `v1.compute.instances.insert`)은 이 주체가 이 시각에 이 리전·구독·프로젝트에 이 자원을 만들도록 요청했다는 것을 증명합니다. 탐지 결과·경고는 공급자가 그 자원에서 채굴과 관련된 통신·프로세스·메모리 패턴을 보았다는 판단을 증명합니다.

채굴 프로그램이 얼마 동안 돌았고 얼마를 벌었는지는 이 기록들에 없습니다. 탐지 결과가 없다고 채굴이 없었다고 할 수도 없는데, 서비스가 꺼져 있었거나, 억제 규칙에 걸렸거나, DNS 기록 원천이 없었을 수 있기 때문입니다. 자원 안에서 어떤 명령을 실행했는지는 디스크와 메모리를 수집해야 알 수 있습니다.

## 흔한 오판

- **채굴 결과를 곧 침해로 보는 것.** GuardDuty 는 인스턴스를 채굴이나 블록체인 작업에 쓰는 경우 결과 유형과 인스턴스 ID 두 조건으로 억제 규칙을 만들라고 안내합니다[6]. 정상 채굴 자원도 있으므로 계정 주인에게 자원의 용도를 확인합니다.
- **결과 목록이 비어 있어서 채굴이 없었다고 보는 것.** 위 억제 규칙에 걸린 결과는 보관 처리되어 기본 화면과 S3 내보내기에서 빠질 수 있습니다([GuardDuty](../../02-artifacts/aws/guardduty.md) 참고). Azure 에서 경고 억제 규칙을 새로 만든 기록은 `MICROSOFT.SECURITY/ALERTSSUPPRESSIONRULES/WRITE` 로 남으므로[20], 조사 기간에 이 작업이 있었는지 봅니다. 탐지를 끈 흔적 전반은 [로그를 끄거나 지웠나](log-tampering.md)에서 다룹니다.
- **한 리전만 보고 끝내는 것.** 단일 리전 트레일과 이벤트 기록은 다른 리전의 생성 기록을 보여 주지 않습니다[1][3].
- **Google Cloud 에서 VM 을 만든 키를 로그로 특정하려는 것.** 서비스 계정 키로 받은 토큰으로 호출하면 감사 로그에 `serviceAccountKeyName` 이 남지만, Compute Engine 은 이 키 이름을 기록하지 않습니다[13]. 어느 키였는지는 [IAM과 서비스 계정 키](../../02-artifacts/gcp/iam-keys.md)의 키 목록과 다른 서비스의 로그로 좁힙니다.
- **시작 스크립트 변경을 실행으로 보는 것.** `ModifyInstanceAttribute` 는 바꿨다는 기록이고, 기본 설정에서 사용자 데이터는 처음 부팅할 때만 실행됩니다[4]. 실행 여부는 인스턴스 안의 로그로 확인합니다.
- **사용자 데이터를 문자열로 검색하는 것.** 사용자 데이터는 base64 로 인코딩된 값이라[4] 원문 문자열 검색에 걸리지 않습니다. 같은 이름의 탐지도 도구마다 조건이 달라서, Sigma 규칙은 `requestParameters.attribute` 가 `userData` 와 정확히 같을 때[17], Invictus-AWS 질의는 `requestParameters` 어딘가에 `userData` 가 들어 있을 때 잡습니다[23].

## 보고서 문장 예

아래 값은 모두 만든 예시입니다.

- "2026-09-20 03:12:45(UTC)에 액세스 키 AKIAIOSFODNN7EXAMPLE 를 쓴 IAM 사용자가 IP 203.0.113.25 에서 ap-southeast-2 리전에 `RunInstances` 를 호출한 기록이 CloudTrail 에 있습니다. 이 계정에서 같은 리전에 그 전 90일 동안 다른 생성 기록은 없습니다."
- "GuardDuty 는 위 인스턴스에 대해 2026-09-20 03:40(UTC)부터 `CryptoCurrency:EC2/BitcoinTool.B!DNS` 결과를 남겼습니다. 이는 인스턴스가 암호화폐 관련 도메인에 질의했다는 GuardDuty 의 판단이며, 채굴 프로그램의 실행 시간이나 수익은 이 기록으로 알 수 없습니다."
- "Google Cloud 관리 활동 로그에 admin@contoso.com 이 서비스 계정 my-service-account@my-project.iam.gserviceaccount.com 을 붙여 VM 을 만든(`v1.compute.instances.insert`) 기록이 있습니다."

## 함께 볼 페이지

- [액세스 키가 새어 나갔나](leaked-keys.md) — 자원을 만든 키가 어디서 새었는지
- [권한을 올렸나](privilege-escalation.md) — 자원을 만들 권한을 스스로 넓혔는지
- [로그를 끄거나 지웠나](log-tampering.md) — 트레일·탐지 서비스를 끄거나 결과를 억제한 흔적
- [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md) — 관리 로그와 탐지 결과를 받는 방법
- [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md) — 위 Sigma 규칙을 로그에 돌리는 방법
- [IAM 사용자·역할·액세스 키](../../02-artifacts/aws/iam.md) — 호출한 주체와 키의 주인 찾기

## 참고 문헌

1. AWS, "Log Amazon EC2 API calls using AWS CloudTrail", Amazon EC2 User Guide. https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitor-with-cloudtrail.html
2. AWS, "CloudTrail record contents for management, data, and network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
3. AWS, "Working with CloudTrail event history", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
4. AWS, "Run commands when you launch an EC2 instance with user data input", Amazon EC2 User Guide. https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html
5. AWS, "AWSCompromisedKeyQuarantineV3", AWS Managed Policy Reference. https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSCompromisedKeyQuarantineV3.html
6. AWS, "GuardDuty EC2 finding types", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-ec2.html
7. AWS, "GuardDuty Runtime Monitoring finding types", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/findings-runtime-monitoring.html
8. Microsoft, "Activity Log in Azure Monitor" (ms.date 2026-05-04). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
9. Microsoft, "Azure Activity Log event schema" (ms.date 2026-03-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
10. Microsoft, "Azure permissions for Compute", Microsoft Learn. https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/compute
11. Microsoft, "Alerts for Linux machines", Microsoft Defender for Cloud. https://learn.microsoft.com/en-us/azure/defender-for-cloud/alerts-linux-machines
12. Google Cloud, "Cryptomining detection best practices" (2026-09-18 갱신), Security Command Center. https://cloud.google.com/security-command-center/docs/cryptomining-detection-best-practices
13. Google Cloud, "Example logs for service accounts", IAM. https://cloud.google.com/iam/docs/audit-logging/examples-service-accounts
14. Google Cloud, "Understanding audit logs", Cloud Logging. https://cloud.google.com/logging/docs/audit/understanding-audit-logs
15. log2timeline, plaso gcp_log.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/jsonl_plugins/gcp_log.py
16. SigmaHQ, aws_cloudtrail_region_enabled.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_region_enabled.yml
17. SigmaHQ, aws_ec2_startup_script_change.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_ec2_startup_script_change.yml
18. SigmaHQ, aws_ec2_import_key_pair_activity.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_ec2_import_key_pair_activity.yml
19. SigmaHQ, azure_creating_number_of_resources_detection.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_creating_number_of_resources_detection.yml
20. SigmaHQ, azure_suppression_rule_created.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_suppression_rule_created.yml
21. SigmaHQ, azure_kubernetes_cronjob.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_kubernetes_cronjob.yml
22. SigmaHQ, gcp_kubernetes_cronjob.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/audit/gcp_kubernetes_cronjob.yml
23. Invictus Incident Response, Invictus-AWS (source/files/queries.yaml). https://github.com/invictus-ir/Invictus-AWS
24. AWS, "GuardDuty foundational data sources", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_data-sources.html
