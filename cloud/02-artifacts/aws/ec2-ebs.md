---
title: "EC2 인스턴스와 스냅숏"
parent: "아티팩트 · AWS"
nav_order: 440
---

# EC2 인스턴스와 스냅숏 (EC2·EBS Snapshots)

EC2 가상 머신을 누가 만들고 멈추고 바꿨는지는 CloudTrail 로, 디스크 안에 무엇이 있었는지는 EBS 스냅숏으로, 부팅할 때 무엇을 실행했는지는 사용자 데이터와 인스턴스 안의 실행 로그로 이어 붙이는 페이지입니다.

## 무엇을 기록하나 · 왜 생기나

EC2 인스턴스 조사는 두 층으로 나뉩니다. 바깥층은 AWS 가 남기는 제어 기록입니다. EC2 API 호출은 전부 CloudTrail 관리 이벤트 (management event) 로 남고, `RunInstances`·`DescribeInstances`·`StopInstances` 같은 호출이 여기에 들어갑니다[5]. 안쪽 층은 인스턴스의 운영체제가 디스크에 남기는 기록이고, 책임 공유 모델에서 이 부분은 고객이 지키고 수집합니다([책임 공유와 조사 범위](../../01-foundations/model/shared-responsibility.md)).

두 층 사이에 EC2 만의 기록이 몇 가지 있습니다.

- **EBS 스냅숏 (EBS snapshot)** 은 볼륨을 특정 시점에 복사한 것입니다. 앞 스냅숏 뒤로 바뀐 블록만 저장하는 증분 백업이고, 스냅숏에서 만든 새 볼륨은 스냅숏을 찍은 순간의 볼륨과 똑같이 시작합니다[1]. AWS 는 EBS 볼륨을 자동으로 백업하지 않으므로, 고객이 직접 찍거나 Amazon Data Lifecycle Manager·AWS Backup 으로 만들어 둔 스냅숏이 없으면 과거 디스크 상태도 없습니다[1].
- **사용자 데이터 (user data)** 는 인스턴스를 띄울 때 넘기는 스크립트나 cloud-init 지시문입니다. 인스턴스 속성으로 저장되고, Linux 에서는 cloud-init 이, Windows 에서는 실행 에이전트(EC2Launch v2, EC2Launch, EC2Config)가 처리합니다[7]. 공격자가 부팅 때 명령을 심는 자리여서 변경 흔적을 봅니다.
- **콘솔 출력과 화면 캡처**는 인스턴스에 접속하지 못해도 AWS 쪽에서 받아 볼 수 있는 출력입니다[6].
- **인스턴스 메타데이터 서비스 (Instance Metadata Service, IMDS)** 는 인스턴스 안에서 자기 정보와 역할 자격 증명을 받는 곳입니다. 여기서 받은 자격 증명으로 부른 API 는 CloudTrail 에 표시가 남습니다[9].

## 위치와 버전별 차이

| 기록 | 얻는 곳 | 기본 상태(2026년 9월 문서 기준) | 알려 주는 것 |
|---|---|---|---|
| EC2 API 호출 | CloudTrail, `eventSource` 가 `ec2.amazonaws.com`[5] | 관리 이벤트라 기본으로 기록. 이벤트 기록은 리전별 최근 90일[5] | 인스턴스·볼륨·스냅숏·보안 그룹을 누가 언제 바꿨나 |
| EBS direct API 제어 호출 | CloudTrail, `eventSource` 가 `ebs.amazonaws.com`, `StartSnapshot`·`CompleteSnapshot`[4] | 관리 이벤트라 기본으로 기록[4] | 볼륨 없이 스냅숏을 직접 만든 일 |
| EBS direct API 블록 읽기·쓰기 | CloudTrail 데이터 이벤트 `ListSnapshotBlocks`·`ListChangedBlocks`·`GetSnapshotBlock`·`PutSnapshotBlock`[4] | 기본 꺼짐, 켜면 추가 요금. 이벤트 기록에는 남지 않음[4] | 스냅숏 블록을 누가 읽고 썼나 |
| 공유한 스냅숏의 사용 | 소유자 계정 CloudTrail `SharedSnapshotCopyInitiated`·`SharedSnapshotVolumeCreated`[2] | 공유한 스냅숏에 작업이 있으면 남음[2] | 공유받은 쪽이 복사하거나 볼륨을 만들었나 |
| EC2 Instance Connect | CloudTrail, `eventSource` 가 `ec2-instance-connect.amazonaws.com`, `SendSSHPublicKey`[5] | 이벤트 기록에서 볼 수 있는 관리 이벤트[5] | SSH 접속에 쓴 인스턴스 ID·OS 사용자 이름·공개 키 |
| 콘솔 출력 | 콘솔 Actions → Monitor and troubleshoot → Get system log, 또는 `aws ec2 get-console-output`[6] | 인스턴스 소유자만 받을 수 있음[6] | Linux 는 모니터에 보일 콘솔 출력, Windows 는 최근 시스템 이벤트 로그 오류 3개 |
| 화면 캡처 | `aws ec2 get-console-screenshot`, 출력은 base64[6] | JPG, 100kb 이하. `*.metal`·Graviton·NVIDIA GRID 드라이버 인스턴스 등은 안 됨[6] | 접속되지 않는 인스턴스의 화면 |
| 사용자 데이터 | `aws ec2 describe-instance-attribute --attribute userData`, 인스턴스 안의 메타데이터[7] | 인스턴스 속성. AMI 를 만들어도 따라가지 않음[7] | 부팅 때 실행하도록 넣은 내용 |
| 사용자 데이터 실행 흔적(Linux) | `/var/log/cloud-init-output.log`, 스크립트 사본 `/var/lib/cloud/instances/instance-id/`[7] | 스크립트는 실행 뒤에도 지우지 않음[7] | 실행한 스크립트와 그 출력 |
| 사용자 데이터 실행 흔적(Windows) | EC2Launch v2 `C:\ProgramData\Amazon\EC2Launch\log\agent.log`, EC2Launch `C:\ProgramData\Amazon\EC2-Windows\Launch\Log\UserdataExecution.log`, EC2Config `C:\Program Files\Amazon\Ec2ConfigService\Logs\Ec2Config.log`[7] | 에이전트에 따라 다른 파일 | 실행 시작·끝, 매 부팅 실행 여부, 스크립트 출력 |
| GuardDuty 가 보관한 스냅숏 | GuardDuty 계정 | Malware Protection for EC2 의 스냅숏 보관 옵션을 켰고 악성코드를 찾아 결과가 생겼을 때만 보관[11] | 탐지 당시 디스크 |

콘솔 출력은 Nitro 기반 인스턴스라면 인스턴스가 실행 중인 동안 최신 직렬 콘솔 출력을 받을 수 있습니다[6]. 화면 캡처는 Asia Pacific (Thailand)·Mexico (Central)·GovCloud 리전에서 쓸 수 없습니다[6].

## 구조

### 스냅숏의 저장과 공유

스냅숏은 고객이 직접 열 수 없는 S3 버킷에 저장되고, S3 콘솔이나 S3 API 로는 보이지 않습니다[1]. 그래서 스냅숏 내용을 읽은 흔적은 [S3 접근 기록](s3-access-logs.md) 이 아니라 EBS direct API 데이터 이벤트나 스냅숏으로 볼륨을 만든 기록에서 찾습니다. 스냅숏 데이터는 리전 안의 모든 가용 영역에 복제됩니다[1].

스냅숏은 모든 AWS 계정에 공개하거나 특정 계정에만 공유할 수 있습니다[2]. 공유 권한은 스냅숏의 `createVolumePermission` 속성이고, 공개는 그룹을 `all` 로, 특정 계정은 12자리 계정 ID 를 넣어 정합니다[2]. 공유에는 조건이 붙습니다[2].

| 조건 | 내용 |
|---|---|
| 리전 | 스냅숏은 만든 리전에 묶임. 다른 리전에 주려면 복사한 뒤 사본을 공유 |
| 기본 AWS 관리 키로 암호화 | 공유할 수 없음 |
| 고객 관리 키로 암호화 | 특정 계정에만 공유할 수 있고, 그 KMS 키도 함께 공유해야 함 |
| 공개 공유 | 암호화하지 않은 스냅숏만 가능. 리전에 공개 차단 (Block public access) 을 켰으면 막힘 |

### EBS direct API 레코드

EBS direct API 는 볼륨을 만들지 않고도 스냅숏 블록을 읽고, 두 스냅숏 사이에 바뀐 블록을 찾고, 스냅숏에 블록을 써 넣습니다[3]. 블록을 읽는 레코드는 `eventCategory` 가 `Data`, `managementEvent` 가 `false` 이고, 대상 스냅숏은 `resources` 에 `AWS::EC2::Snapshot` 형식으로 남습니다[4]. `ListChangedBlocks` 는 `requestParameters` 에 `firstSnapshotId`·`secondSnapshotId` 를 담습니다[4]. 문서 예시의 `StartSnapshot` 응답에는 `blockSize` 가 `524288` 로 들어 있습니다[4]. 아래는 만든 예시입니다.

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
  "eventTime": "2026-09-02T14:05:31Z",
  "eventSource": "ebs.amazonaws.com",
  "eventName": "GetSnapshotBlock",
  "awsRegion": "us-east-1",
  "sourceIPAddress": "198.51.100.23",
  "userAgent": "aws-cli/2.x",
  "requestParameters": {
    "snapshotId": "snap-0123456789abcdef0",
    "blockIndex": 42,
    "blockToken": "(생략)"
  },
  "responseElements": null,
  "readOnly": true,
  "resources": [
    {
      "accountId": "123456789012",
      "type": "AWS::EC2::Snapshot",
      "ARN": "arn:aws:ec2:us-east-1::snapshot/snap-0123456789abcdef0"
    }
  ],
  "eventType": "AwsApiCall",
  "managementEvent": false,
  "eventCategory": "Data",
  "recipientAccountId": "123456789012"
}
```

`GetSnapshotBlock` 한 건은 블록 하나를 읽은 기록이라, 한 사람이 스냅숏을 통째로 읽었다면 같은 `snapshotId` 로 `blockIndex` 만 다른 레코드가 많이 쌓입니다. 관리 이벤트와 데이터 이벤트를 켜는 방법은 [관리 이벤트와 데이터 이벤트](cloudtrail/event-types.md) 에서 다룹니다.

### 사용자 데이터

사용자 데이터는 API 로 넘길 때 base64 로 인코딩하고, 인코딩 전 원문은 16KB 까지입니다[7]. AWS 는 내용을 해석하지 않고 받은 그대로 돌려줍니다[7]. 인스턴스 메타데이터나 콘솔로 보면 자동으로 디코딩해 보여 주지만, `describe-instance-attribute` 는 base64 그대로 돌려줍니다[7].

기본으로 사용자 데이터 스크립트와 cloud-init 지시문은 인스턴스를 처음 띄울 때 한 번만 실행됩니다[7]. 사용자 데이터를 바꾸려면 인스턴스를 먼저 멈춰야 하고, 바꾼 뒤 시작하면 새 내용이 인스턴스에 보이지만 설정을 따로 하지 않았으면 스크립트는 실행되지 않습니다[7]. Windows 에서는 사용자 데이터에 `<persist>true</persist>` 를 넣으면 재부팅·시작 때마다 실행합니다[7]. 이 설정은 실행 로그에 남습니다[7].

| 에이전트 | 로그에 남는 줄[7] |
|---|---|
| EC2Launch v2 | `Info: Initialize user-data state`(실행 시작), `Info: Frequency is: always`(매 부팅), `Info: Frequency is: once`(한 번), `Stage: postReadyUserData execution completed`(실행 끝) |
| EC2Launch | `Userdata execution begins`, `<persist> tag was provided: true`, `Running userdata on every boot`, 스크립트 출력 |
| EC2Config | `Ec2HandleUserData: Message: Start running user scripts`, `Ec2HandleUserData: Message: Re-enabled userdata execution`, 스크립트 출력 |

Linux 에서는 처리한 스크립트를 `/var/lib/cloud/instances/instance-id/` 로 복사해 실행하고 지우지 않습니다[7]. 이 폴더를 지우지 않고 AMI 를 만들면 그 AMI 로 띄운 모든 인스턴스에 스크립트가 남습니다[7]. 그래서 이 폴더에 스크립트가 있다고 이 인스턴스에서 넣었다고 단정할 수는 없고, 인스턴스 ID 가 들어간 폴더 이름과 AMI 출처를 함께 봅니다.

### 인스턴스 메타데이터 서비스

IMDS 는 요청 하나에 응답 하나를 주는 IMDSv1 과, PUT 요청으로 세션 토큰을 받아 헤더에 넣어 쓰는 IMDSv2 가 있습니다[8]. 기본으로는 두 방식을 모두 받고, 인스턴스마다 IMDSv2 만 받도록 바꿀 수 있습니다[8]. IMDSv2 세션 토큰의 유효 시간은 1초부터 6시간까지입니다[8]. IMDS 에서 받은 역할 자격 증명으로 AWS API 를 부르면 CloudTrail `userIdentity.sessionContext.ec2RoleDelivery` 에 IMDSv1 이면 `1.0`, IMDSv2 이면 `2.0` 이 남습니다([레코드 구조](cloudtrail/record-structure.md))[9]. 인스턴스가 169.254.169.254 로 메타데이터를 받은 트래픽은 [VPC 흐름 로그](vpc-flow-logs.md) 에 남지 않습니다[10].

## 증거로서 의미

**증명하는 것**

- CloudTrail 의 EC2 관리 이벤트는 어떤 자격 증명이 언제 어느 IP 에서 인스턴스를 만들고 멈추고 끝냈는지, 보안 그룹과 스냅숏 권한을 바꿨는지를 보여 줍니다[5].
- 스냅숏은 찍은 순간의 볼륨 블록 내용입니다[1]. 볼륨을 만들어 붙이면 파일 시스템 분석을 할 수 있고, 그 방법은 Linux 판 [클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html) 과 [디스크 이미징](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/disk-imaging.html) 을 따릅니다.
- `ModifySnapshotAttribute` 는 스냅숏 공유 권한을 바꾼 기록이고[2][13], 소유자 계정의 `SharedSnapshotCopyInitiated`·`SharedSnapshotVolumeCreated` 는 공유받은 쪽이 그 스냅숏을 복사하거나 볼륨으로 만들었다는 기록입니다[2].
- `ModifyInstanceAttribute` 에서 `requestParameters.attribute` 가 `userData` 이면 사용자 데이터를 바꾼 기록입니다[15].
- `ec2RoleDelivery` 가 있는 호출은 IMDS 에서 나온 역할 자격 증명으로 부른 것입니다[9].

**증명하지 못하는 것**

- 스냅숏에는 메모리가 없습니다. 실행 중인 프로세스·네트워크 연결은 [메모리 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/memory-acquisition.html) 으로 따로 확보해야 합니다.
- 스냅숏 두 개 사이에 무슨 일이 몇 번 있었는지는 알 수 없습니다. `ListChangedBlocks` 는 두 스냅숏 사이에 바뀐 블록을 알려 줄 뿐이라[3], 블록이 언제 어떤 순서로 바뀌었는지는 나오지 않습니다.
- 공유받은 계정이 EBS direct API 로 블록을 읽었다면, 그 데이터 이벤트는 소유자 계정으로 가지 않습니다[4]. 소유자 계정만 보고 "공유한 스냅숏을 읽은 기록이 없다" 고 쓸 수는 없습니다.
- 사용자 데이터를 바꾼 기록은 그 스크립트가 실행됐다는 뜻이 아닙니다. 기본 설정에서는 바꾼 뒤 시작해도 실행되지 않으므로[7], 실행 여부는 인스턴스 안의 cloud-init·EC2Launch 로그로 확인합니다.
- `ec2RoleDelivery` 는 자격 증명을 어디서 받았는지만 알려 줍니다. 그 자격 증명이 인스턴스 밖으로 빠져나가 다른 곳에서 쓰였는지는 `sourceIPAddress` 와 GuardDuty 결과로 따로 봅니다.

보고서에는 "2026년 9월 2일 14:05 UTC 에 액세스 키 AKIAIOSFODNN7EXAMPLE 로 198.51.100.23 에서 스냅숏 snap-0123456789abcdef0 의 블록을 읽은 데이터 이벤트가 있다" 처럼 기록으로 확인되는 만큼만 씁니다(만든 예시).

## 시각 해석

| 값 | 무엇의 시각인가 | 형식·시간대 |
|---|---|---|
| CloudTrail `eventTime` | API 요청 | UTC, `2026-09-02T14:05:31Z` 모양. [레코드 구조](cloudtrail/record-structure.md) 참고 |
| `StartSnapshot` 응답의 `startTime` | 스냅숏 시작 | `Jul 3, 2020 11:27:26 PM` 모양의 문자열이고 시간대 표시가 없음[4]. 타임라인에는 같은 레코드의 `eventTime` 을 씀 |
| 스냅숏 내용 | 찍은 순간의 볼륨[1] | 안의 파일 시각은 운영체제 기준. 해석은 Linux 판 [타임라인 만들기](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/timeline.html) |
| 콘솔 출력 | 시작·정지·재부팅·종료 같은 상태 전환 직후 버퍼[6] | 계속 갱신되지 않음[6]. 받은 시각과 내용의 시각이 다를 수 있음 |
| 화면 캡처 | 요청한 순간 | 실행 중에도, 인스턴스가 오류로 멈춘 뒤에도 받을 수 있음[6] |
| 사용자 데이터 | 시각 값 없음 | 바꾼 때는 `ModifyInstanceAttribute` 의 `eventTime` 으로만 알 수 있음 |
| cloud-init·EC2Launch 로그 | 인스턴스 안에서 실행한 때 | 인스턴스의 시간대 설정을 따르므로 실제 데이터에서 확인 |

CloudTrail 이 트레일 저장소에 파일을 넣기까지 걸리는 시간과 이벤트 기록의 보관 범위는 [트레일과 이벤트 기록](cloudtrail/trails.md) 에서 다룹니다. 클라우드 로그 시각 전반은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 을 봅니다.

## 함정과 한계

- **스냅숏을 지워도 데이터가 남을 수 있습니다.** 증분이라서 스냅숏 하나를 지우면 그 스냅숏만 쓰던 데이터만 지워지고, 다른 스냅숏이 참조하는 데이터는 남습니다[1]. 반대로 지금 남은 스냅숏 목록만 보고 과거 어느 시점의 디스크를 모두 되살릴 수 있다고 볼 수는 없습니다.
- **인스턴스를 멈추면 인스턴스 스토어 볼륨의 데이터가 사라집니다**[7]. 사용자 데이터를 바꾸려면 인스턴스를 멈춰야 하고[7], 공격자가 멈췄든 조사자가 수집하려고 멈췄든 인스턴스 스토어 내용은 잃습니다. 멈추기 전에 [클라우드 가상 머신 수집](../../03-techniques/acquisition/vm-acquisition.md) 순서를 확인합니다.
- **사용자 데이터 변경은 앞뒤 호출과 함께 봅니다.** 멈춘 인스턴스에서만 바꿀 수 있으므로[7], 같은 인스턴스에 `StopInstances`, `ModifyInstanceAttribute`(`userData`), `StartInstances` 가 차례로 남아 있을 가능성이 있습니다. `StopInstances`·`StartInstances` 레코드의 모양은 [레코드 구조](cloudtrail/record-structure.md) 를 봅니다.
- **사용자 데이터 스크립트 사본은 AMI 로 퍼질 수 있습니다.** 사용자 데이터는 AMI 에 들어가지 않지만[7], `/var/lib/cloud/instances/` 아래 스크립트 사본은 디스크에 남아 AMI 로 퍼집니다[7].
- **콘솔 출력은 계속 갱신되는 로그가 아닙니다**[6]. 오래 켜 둔 인스턴스의 콘솔 출력에는 최근 일이 없을 수 있습니다.
- **EBS direct API 데이터 이벤트는 기본으로 꺼져 있습니다**[4]. 켜지 않은 기간에는 스냅숏 블록을 누가 읽었는지 계정 안 어디에도 남지 않습니다.
- **스냅숏 공유는 KMS 키 공유와 짝입니다.** 고객 관리 키로 암호화한 스냅숏을 공유하면 키도 함께 공유해야 하므로[2], 키 정책 변경도 같은 시간대에서 찾아봅니다.

## 직접 분석해 보기

**사용자 데이터를 바이트로 한 번 풀기.** `describe-instance-attribute` 는 base64 를 그대로 주므로 직접 디코딩합니다[7]. 아래 값은 만든 예시이고, 명세(base64)로 만든 헥스입니다.

```text
$ aws ec2 describe-instance-attribute --instance-id i-0123456789abcdef0 --attribute userData
{
    "UserData": {
        "Value": "IyEvYmluL2Jhc2gKdXNlcmFkZCAtbSBzdmMtYmFja3VwCg=="
    },
    "InstanceId": "i-0123456789abcdef0"
}

$ echo 'IyEvYmluL2Jhc2gKdXNlcmFkZCAtbSBzdmMtYmFja3VwCg==' | base64 --decode | xxd
00000000: 2321 2f62 696e 2f62 6173 680a 7573 6572  #!/bin/bash.user
00000010: 6164 6420 2d6d 2073 7663 2d62 6163 6b75  add -m svc-backu
00000020: 700a                                     p.
```

첫 두 바이트 `23 21`(`#!`)이 셸 스크립트의 시작이고, Linux 사용자 데이터 셸 스크립트는 이 두 글자와 해석기 경로로 시작해야 합니다[7]. `Content-Type: multipart/mixed` 머리글이 보이면 cloud-init 지시문(`text/cloud-config`)과 셸 스크립트(`text/x-shellscript`)를 섞은 MIME 여러 부분 형식이고, Windows 는 스크립트를 `<powershell>`·`<script>` 태그로 감쌉니다[7]. 풀어 낸 내용을 인스턴스 안의 `/var/lib/cloud/instances/instance-id/` 사본이나 EC2Launch 로그와 맞춰 봅니다.

**CloudTrail 에서 EC2·스냅숏 흔적 모으기.** 트레일이 S3 에 쌓은 gzip JSON 에서 EC2·EBS·Instance Connect 이벤트를 골라 시각 순서로 펼칩니다.

```bash
zcat *.json.gz | jq -c '.Records[]
  | select(.eventSource=="ec2.amazonaws.com" or .eventSource=="ebs.amazonaws.com" or .eventSource=="ec2-instance-connect.amazonaws.com")
  | select((.eventName|test("Snapshot|InstanceAttribute|ExportTask|KeyPair|SecurityGroup|Instances|SSHPublicKey")))
  | [.eventTime, .eventSource, .eventName, .userIdentity.arn, .userIdentity.sessionContext.ec2RoleDelivery, .sourceIPAddress, .errorCode]' \
  | sort
```

스냅숏을 만들고 복사하고 지운 호출도 EC2 API 관리 이벤트라서[5] `eventName` 에 `Snapshot` 이 들어간 줄로 함께 모입니다. 실제 로그에서 작업 이름과 `requestParameters` 안에 `createVolumePermission` 이 어떤 모양으로 들어 있는지 확인한 뒤 걸러 냅니다.

**탐지 규칙으로 검색하기.** SigmaHQ 의 AWS CloudTrail 규칙에 EC2·EBS 흔적 조건이 필드 이름 그대로 들어 있습니다. Invictus-AWS 의 queries.yaml 에는 이 가운데 스냅숏 권한·VM 내보내기·사용자 데이터·기본 암호화 규칙이 Athena SQL 로 들어 있고, 사용자 데이터 규칙은 `requestParameters LIKE '%userData%'` 로 찾습니다[20]. 규칙을 쓰는 방법은 [탐지 규칙으로 로그 검색하기](../../03-techniques/analysis/detection-rules.md) 에서 다룹니다.

| 규칙 | 조건(`eventSource`·`eventName`) | 찾는 흔적 |
|---|---|---|
| aws_snapshot_backup_exfiltration[13] | `ec2.amazonaws.com`·`ModifySnapshotAttribute` | 다른 계정이 쓸 수 있게 스냅숏 권한을 바꿈 |
| aws_ec2_vm_export_failure[14] | `ec2.amazonaws.com`·`CreateInstanceExportTask` 이고 `errorMessage`·`errorCode` 가 없고 `responseElements` 에 `Failure` 가 없음 | 인스턴스를 밖으로 내보내는 작업 |
| aws_ec2_startup_script_change[15] | `ec2.amazonaws.com`·`ModifyInstanceAttribute` 이고 `requestParameters.attribute` 가 `userData` | 사용자 데이터 변경 |
| aws_ec2_disable_encryption[16] | `ec2.amazonaws.com`·`DisableEbsEncryptionByDefault` | 새 볼륨 기본 암호화 끄기 |
| aws_ec2_import_key_pair_activity[17] | `ec2.amazonaws.com`·`ImportKeyPair` | 외부에서 만든 SSH 키 쌍 등록 |
| aws_cloudtrail_security_group_change_ingress_egress[19] | `ec2.amazonaws.com`·`AuthorizeSecurityGroupIngress`·`AuthorizeSecurityGroupEgress`·`RevokeSecurityGroupIngress`·`RevokeSecurityGroupEgress` | 보안 그룹 규칙 변경 |
| aws_cloudtrail_ssm_malicious_usage[18] | `ssm.amazonaws.com`·`SendCommand` 이고 `errorCode` 가 `Success` 이거나 없음 | Systems Manager 로 인스턴스에 명령을 보냄 |

## 교차 검증

- [CloudTrail](cloudtrail/index.md) — EC2 관리 이벤트와 EBS direct API 데이터 이벤트가 이 페이지에서 다루는 기록의 뼈대입니다.
- [IAM 사용자·역할·액세스 키](iam.md) — `ec2RoleDelivery` 가 있는 세션이면 그 역할이 어느 인스턴스 프로파일에 붙어 있는지 확인해 인스턴스를 좁힙니다.
- [VPC 흐름 로그](vpc-flow-logs.md) — `instance-id`·인터페이스로 인스턴스의 바깥 통신을 봅니다. 메타데이터 접근은 남지 않습니다[10].
- [GuardDuty](guardduty.md) — `UnauthorizedAccess:EC2/SSHBruteForce`, `CryptoCurrency:EC2/BitcoinTool.B!DNS`, `UnauthorizedAccess:EC2/MetadataDNSRebind` 같은 EC2 결과와[12], 인스턴스용 자격 증명이 외부 IP 에서 쓰였다는 `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS` 를 찾습니다[21]. 악성코드 탐지로 보관한 스냅숏이 있는지도 봅니다[11].
- [CloudWatch Logs](cloudwatch-logs.md) — 인스턴스 안의 로그를 CloudWatch 로 보내고 있었다면 인스턴스를 지운 뒤에도 로그가 남아 있을 수 있습니다.
- Linux 판 [인증 로그](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/logins/auth-log.html)·[SSH](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/logins/ssh/index.html) — `SendSSHPublicKey` 의 `osUser` 와 시각을 인스턴스 안의 SSH 로그인과 맞춰 봅니다.
- [Azure 가상 머신](../azure/azure-vm.md) — Azure 에서 같은 역할을 하는 기록입니다.
- [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md), [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md), [채굴용 자원을 만들었나](../../04-scenarios/infrastructure/cryptomining.md), [액세스 키가 새어 나갔나](../../04-scenarios/infrastructure/leaked-keys.md) — 이 페이지의 기록을 조사 흐름으로 묶습니다.

## 실습

위의 만든 예시와 자기 계정의 시험 환경으로 풀어 봅니다.

1. 예시 `GetSnapshotBlock` 레코드가 관리 이벤트가 아니라 데이터 이벤트라는 것을 어느 두 필드로 알 수 있는지 적어 봅니다.
2. 스냅숏을 다른 계정에 공유했는데 소유자 계정에 `SharedSnapshotVolumeCreated` 만 있고 `GetSnapshotBlock` 은 없다면, 공유받은 쪽이 블록을 직접 읽지 않았다고 쓸 수 있는지 판단하고 이유를 적어 봅니다.
3. 예시 사용자 데이터를 디코딩한 결과에서 어떤 계정이 만들어질지 읽고, 그 명령이 실제로 실행됐는지 확인하려면 인스턴스 안의 어느 파일을 봐야 하는지 적어 봅니다.
4. 시험 계정에서 인스턴스를 멈추고 사용자 데이터를 바꾼 뒤 다시 시작해, CloudTrail 에 남은 이벤트 이름과 순서, `requestParameters.attribute` 값을 확인합니다. 새 스크립트가 실행됐는지 `/var/log/cloud-init-output.log` 로 확인합니다.
5. 시험 인스턴스에서 IMDSv1 만 허용한 때와 IMDSv2 만 허용한 때 각각 역할 자격 증명으로 API 를 한 번 불러, `ec2RoleDelivery` 값을 비교합니다.

## 참고 문헌

1. AWS, "Amazon EBS snapshots", Amazon EBS User Guide. https://docs.aws.amazon.com/ebs/latest/userguide/ebs-snapshots.html
2. AWS, "Share an Amazon EBS snapshot with other AWS accounts", Amazon EBS User Guide. https://docs.aws.amazon.com/ebs/latest/userguide/ebs-modifying-snapshot-permissions.html
3. AWS, "Use EBS direct APIs to access the contents of an EBS snapshot", Amazon EBS User Guide. https://docs.aws.amazon.com/ebs/latest/userguide/ebs-accessing-snapshot.html
4. AWS, "Log EBS direct APIs calls using AWS CloudTrail", Amazon EBS User Guide. https://docs.aws.amazon.com/ebs/latest/userguide/logging-ebs-apis-using-cloudtrail.html
5. AWS, "Log Amazon EC2 API calls using AWS CloudTrail", Amazon EC2 User Guide. https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitor-with-cloudtrail.html
6. AWS, "Troubleshoot an unreachable Amazon EC2 instance", Amazon EC2 User Guide. https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-console.html
7. AWS, "Run commands when you launch an EC2 instance with user data input", Amazon EC2 User Guide. https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html
8. AWS, "Use the Instance Metadata Service to access instance metadata", Amazon EC2 User Guide. https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
9. AWS, "CloudTrail userIdentity element", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-user-identity.html
10. AWS, "Flow log limitations", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-limitations.html
11. AWS, "GuardDuty Malware Protection for EC2", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/malware-protection.html
12. AWS, "GuardDuty finding types", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-active.html
13. SigmaHQ, aws_snapshot_backup_exfiltration.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_snapshot_backup_exfiltration.yml
14. SigmaHQ, aws_ec2_vm_export_failure.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_ec2_vm_export_failure.yml
15. SigmaHQ, aws_ec2_startup_script_change.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_ec2_startup_script_change.yml
16. SigmaHQ, aws_ec2_disable_encryption.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_ec2_disable_encryption.yml
17. SigmaHQ, aws_ec2_import_key_pair_activity.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_ec2_import_key_pair_activity.yml
18. SigmaHQ, aws_cloudtrail_ssm_malicious_usage.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_ssm_malicious_usage.yml
19. SigmaHQ, aws_cloudtrail_security_group_change_ingress_egress.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_security_group_change_ingress_egress.yml
20. invictus-ir, Invictus-AWS, source/files/queries.yaml. https://github.com/invictus-ir/Invictus-AWS
21. AWS, "GuardDuty IAM finding types", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-iam.html
