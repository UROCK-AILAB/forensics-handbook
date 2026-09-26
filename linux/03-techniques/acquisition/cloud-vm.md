---
title: "클라우드 가상 머신 수집"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 940
---

# 클라우드 가상 머신 수집 (Cloud VM)

클라우드 가상 머신은 디스크를 떼어 낼 수 없어서, 메모리와 휘발성 흔적은 게스트 안에서 뜨고 디스크는 제공자 API 로 스냅숏 (snapshot) 을 떠서 받습니다.

## 언제 쓰나

AWS EC2, Google Compute Engine, Azure 가상 머신처럼 조사 대상 Linux 가 클라우드에서 돌 때 씁니다. 수집은 게스트 안과 게스트 밖 두 갈래로 나뉩니다. 게스트 안에서는 [라이브 응답 수집](live-response.md)과 [메모리 수집](memory-acquisition.md)을 그대로 하되 결과를 클라우드 저장소로 곧바로 보내고, cloud-init 과 제공자 에이전트가 남긴 흔적을 함께 뜹니다. 게스트 밖에서는 제공자 API 로 디스크 스냅숏과 콘솔 출력을 받습니다.

게스트 안 도구로 뜬 메모리는 도는 시스템을 읽으므로 원자적 (atomic) 사본이 아닙니다. QEMU/KVM 에서 가상 머신을 멈추고 `dump_guest_memory` 로 뜬 메모리를 기준값으로 삼은 시험에서, 게스트 안 수집 도구로 뜬 메모리는 이 기준과 바이트가 달랐습니다[17]. 자체 하이퍼바이저에서 도는 가상 머신은 [KVM·libvirt](../../02-artifacts/containers/kvm-libvirt.md)에서 다룹니다.

## 절차

1. **인스턴스와 디스크를 기록합니다.** 인스턴스 ID, 리전·영역, 붙은 디스크(볼륨) 목록, 디스크마다 루트인지 데이터 디스크인지를 적습니다. 이 값은 뒤에서 스냅숏의 원본 디스크 ID 와 맞춰 보는 데 씁니다.
2. **콘솔 출력을 먼저 받습니다.** 게스트에 들어가지 않고도 부팅 메시지를 볼 수 있습니다. EC2 의 `GetConsoleOutput` 은 Linux 인스턴스에서 물리 모니터에 보였을 콘솔 출력을 base64 로 돌려주고, 결과의 `Timestamp` 는 출력이 마지막으로 바뀐 시각입니다[1]. `GetConsoleScreenshot` 은 실행 중인 인스턴스의 화면을 JPG(base64)로 돌려줍니다[1]. Compute Engine 의 `instances.getSerialPortOutput` 은 직렬 포트 출력의 마지막 1MB 를 돌려주고, 버퍼(1MB)를 넘으면 오래된 출력을 새 출력이 덮어씁니다[2]. 덮어쓰기 전에 받아야 하므로 순서상 앞에 둡니다.
3. **게스트 안에서 메모리를 뜹니다.** 도구와 커널 제약은 [메모리 수집](memory-acquisition.md)에서 다룹니다. 클라우드에서는 결과를 게스트 디스크에 쓰지 않고 저장소로 보내는 방법을 씁니다. AVML 은 Azure Blob SAS URL(`--sas-url`), AWS S3·Google Cloud Storage 사전 서명 URL(`--url`, HTTP PUT)로 올리고, `--delete` 를 붙이면 올리기에 성공한 뒤 로컬 파일을 지웁니다[5]. `avml stream blob` 은 로컬 파일을 만들지 않고 바로 올립니다[5]. Azure 에서는 customScript VM 확장으로 `avml acquire --compress --sas-url … --delete` 를 원격 실행하는 방법도 있습니다[5].
4. **게스트 안 휘발성 흔적과 클라우드 흔적을 뜹니다.** 방법은 [라이브 응답 수집](live-response.md)과 같습니다. UAC 는 결과물과 로그 파일을 SFTP(`--sftp`), S3 호환 저장소(`--s3-provider amazon|google|ibm`, `--s3-bucket` 등), AWS S3 사전 서명 URL(`--aws-s3-presigned-url`, 로그 파일은 `--aws-s3-presigned-url-log-file`), Azure Storage SAS URL(`--azure-storage-sas-url`)로 보냅니다[6]. `--delete-local-on-successful-transfer` 를 붙이면 전송이 끝난 뒤 로컬 결과물과 로그를 지웁니다[6]. 이때 아래 "게스트 안에서 뜰 클라우드 흔적" 표의 경로를 빠뜨리지 않습니다. 특히 `/run/cloud-init/` 은 tmpfs 인 `/run` 아래라 부팅 때 비워지므로[16] 인스턴스를 멈추기 전에 떠야 합니다.
5. **디스크 스냅숏을 뜹니다.** 제공자별 방법과 일관성 차이는 아래 표에 있습니다. 가능하면 인스턴스를 멈추고 뜨고, 멈출 수 없으면 여러 디스크를 한 시점으로 묶어 뜹니다.
6. **스냅숏을 분석할 수 있는 모양으로 받습니다.** 스냅숏에서 새 디스크를 만들어 분석용 인스턴스에 읽기 전용으로 붙이거나, 이미지 파일로 내려받습니다. Azure 는 실행 중인 VM 에 붙은 디스크에서는 VHD 를 내려받을 수 없어서 스냅숏에서 받습니다[4]. 읽기 전용 SAS URL 은 `az disk grant-access --access-level Read --duration-in-seconds …` 로 만들고, 포털의 기본 만료 시간은 3,600초입니다[4]. 받은 뒤에는 `az disk revoke-access` 로 접근을 거둡니다[4]. 받은 이미지의 해시와 검증은 [디스크 이미징](disk-imaging.md)과 같게 합니다.
7. **수집 기록을 남깁니다.** 스냅숏 ID, 원본 디스크 ID, 스냅숏 시작·완료 시각, 인스턴스를 멈췄는지, 쓴 명령과 옵션을 적습니다. 기록 양식은 [조사 절차](investigation-process.md)를 따릅니다.

### 제공자별 디스크 스냅숏

| 제공자 | 방법 | 일관성과 제약 | 기록할 값 |
|---|---|---|---|
| AWS EC2 | `CreateSnapshot`(볼륨 하나), `CreateSnapshots`(인스턴스에 붙은 볼륨 전체)[1] | 사용 중인 볼륨도 뜰 수 있지만 명령 시점에 볼륨에 쓰인 데이터만 담고, 앱이나 OS 가 캐시에 둔 데이터는 빠질 수 있습니다. 쓰기를 멈출 수 없으면 언마운트하고 뜨고, 루트 볼륨은 인스턴스를 멈추고 뜨기를 권합니다[1]. `CreateSnapshots` 는 인스턴스 전체에 걸쳐 크래시 일관 (crash-consistent) 스냅숏을 만들고, 루트 볼륨(`ExcludeBootVolume`)이나 특정 데이터 볼륨(`ExcludeDataVolumeIds`)을 뺄 수 있습니다[1]. 스냅숏은 원본 볼륨과 같은 리전에 만들고, 원본이 Local Zone·Outpost 에 있으면 같은 Local Zone·Outpost 나 그 상위 리전에 만듭니다[1]. | `SnapshotId`, `VolumeId`, `StartTime`, `CompletionTime`, `Encrypted`, `KmsKeyId`[1] |
| Google Compute Engine | `disks.createSnapshot`(일반 생성은 `snapshots.insert` 를 권함)[2] | `guestFlush` 를 켜면 OS 에 알려 앱 일관 스냅숏을 시도합니다[2]. | `sourceDisk`, `sourceDiskId`, `creationTimestamp`, `status`, `diskSizeGb`[2] |
| Azure | 관리 디스크 스냅숏(Full 또는 Incremental)[4] | 관리 디스크 스냅숏은 디스크 하나의 전체 읽기 전용 사본이고, OS 디스크와 데이터 디스크를 따로 뜨며, 원본 디스크와 따로 존재합니다[3]. 실행 중인 VM 의 스냅숏은 전원을 껐다 켰거나 비정상 종료(crash)된 상태와 같고, 데이터 디스크가 하나라도 있으면 VM 을 멈추고 떠야 합니다[4]. | 스냅숏 이름, 원본 디스크, 스냅숏 유형[4] |

AWS 에서 암호화한 볼륨의 스냅숏은 자동으로 암호화되고, 그 스냅숏으로 만든 볼륨도 암호화됩니다[1]. 분석 계정이 그 키를 쓸 권한이 있는지 수집 전에 확인합니다.

### 게스트 안에서 뜰 클라우드 흔적

| 경로 | 남는 것 | 참고 |
|---|---|---|
| `/run/cloud-init/cloud-init-generator.log` | 부팅 초기에 cloud-init 이 돌지 않은 이유[9] | tmpfs, 부팅 때 비워짐[16] |
| `/run/cloud-init/ds-identify.log` | 부팅 초기에 어느 플랫폼으로 판단했는지, 돌지 않은 이유[9] | tmpfs, 부팅 때 비워짐[16] |
| `/var/log/cloud-init.log` | cloud-init 주 로그[9] | 여러 부팅 기록이 이어 쓰임[9] |
| `/var/log/cloud-init-output.log` | 단계별 출력과 사용자 스크립트 출력[9] | 여러 부팅 기록이 이어 쓰임[9] |
| `/var/lib/cloud/instance/user-data.txt` | 파일 이름으로 보아 user-data 를 담은 파일일 가능성이 있음 | `cloud-init collect-logs` 수집 대상[10] |
| `/var/lib/cloud/seed/` | 데이터 소스를 초기화할 때 쓰는 인스턴스 메타데이터[10] | `cloud-init clean --seed` 가 지움[10] |
| `/var/lib/waagent` | Azure 데이터 소스가 메타데이터 파일을 읽고 받은 데이터를 쓰는 곳(기본값)[14] | Azure |
| `/var/log/waagent.log`, `/var/log/azure` | Azure Linux VM 에이전트 로그[8] | Azure |
| `/var/lib/waagent/run-command/download` | Run Command 로 실행한 스크립트와 그 stdout·stderr[8] | Azure |
| `/etc/amazon/ssm` | AWS Systems Manager 에이전트(SSM Agent) 설정[7] | AWS |
| `/var/log/amazon/ssm/*.log` | SSM Agent 로그[7] | AWS |

제공자 에이전트 경로는 에이전트가 깔려 있을 때만 있습니다. `cloud-init collect-logs` 를 쓰면 `/var/log/cloud-init.log`, `/var/log/cloud-init-output.log`, `/run/cloud-init`, `/var/lib/cloud/instance/user-data.txt`, cloud-init 패키지 판, `dmesg` 와 `journalctl` 출력을 tar 하나로 묶습니다[10]. 저널을 따로 뜨는 방법은 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md)에서 다룹니다.

인스턴스 정보는 `cloud-init query --all` 을 root 로 실행하면 instance-data 라는 JSON 으로 볼 수 있습니다[11]. `v1.cloud_name`(예: `aws`, `azure`), `v1.instance_id`, `v1.distro` 같은 표준 키가 있고, 비밀번호처럼 민감한 값은 root 만 읽을 수 있게 따로 두어 일반 사용자에게는 가린 값을 보여 줍니다[11]. 인스턴스에 넘긴 user-data 와 vendor-data 는 root 로 `cloud-init query` 의 `userdata`·`vendordata` 키를 읽으면 디코딩한 값으로 나옵니다[10][11]. instance-data 파일이 디스크 어디에 있는지는 검체에서 `/run/cloud-init/` 아래를 보고 확인합니다.

Azure 는 UDF 형식 CD 로 `ovf-env.xml` 을 붙여 초기 데이터를 넘기고, 이 파일에는 `HostName` 과 base64 로 인코딩한 user-data(`UserData` 또는 `CustomData` 요소)가 들어 있습니다[14].

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| 제공자 API·CLI(EC2 `CreateSnapshot`·`CreateSnapshots`·`GetConsoleOutput`, Compute Engine `disks.createSnapshot`·`instances.getSerialPortOutput`, `az disk grant-access`) | 디스크 스냅숏, 콘솔 출력, 이미지 내려받기[1][2][4] |
| AVML | 게스트 메모리를 떠서 Azure Blob·S3·Cloud Storage 로 올림[5] |
| UAC | 라이브 응답 결과를 SFTP·S3·Azure Storage 로 보냄, SSM·Azure 에이전트 흔적 수집[6][7][8] |
| cloud-init CLI | `collect-logs`(로그 묶기), `query`(instance-data 보기), `analyze`(로그에서 부팅 기록 뽑기)[10][11][12] |

## 함정과 한계

- **여러 디스크를 따로 뜨면 시점이 섞입니다.** 디스크마다 스냅숏 시각이 달라 파일 시스템 사이의 순서가 어긋납니다. EC2 는 `CreateSnapshots` 로 묶어 뜨고, Azure 는 데이터 디스크가 있으면 VM 을 멈추고 뜹니다[1][4].
- **실행 중에 뜬 스냅숏은 전원을 껐다 켰거나 비정상 종료된 상태와 같습니다[4].** 앱이나 OS 가 캐시에만 두었던 데이터는 빠지고[1], 그때 돌던 앱이 비정상 종료에 약하면 문제가 생길 수 있습니다[4]. 이 사본을 읽기 전용으로 마운트하는 방법은 [디스크 이미징](disk-imaging.md)에서 다룹니다.
- **스냅숏에는 메모리가 없습니다.** 프로세스, 네트워크 연결, 복호화된 키는 3단계에서 뜬 것만 남습니다.
- **`/run` 은 부팅 때 비워집니다.** `/run` 은 tmpfs 라서 `/run/cloud-init/` 의 로그는 다음 부팅에서 남지 않습니다[16].
- **Compute Engine 직렬 포트 출력은 1MB 까지만 남고 오래된 것부터 덮어씁니다[2].** 오래 돈 인스턴스에서는 부팅 메시지가 이미 없을 수 있습니다.
- **Compute Engine 의 `storageBytes` 는 스냅숏끼리 저장소를 나눠 쓰는 크기라서 다른 스냅숏을 만들거나 지우면 값이 바뀝니다[2].** 이 값으로 스냅숏 내용이 같은지 다른지 판단하지 않습니다.
- **cloud-init 이 흔적을 지울 수 있습니다.** `cloud-init clean` 은 `/var/lib/cloud` 산출물을 지우고, `--logs` 는 `/var/log/` 의 cloud-init 로그를, `--seed` 는 `/var/lib/cloud/seed/` 를 지웁니다[10]. `--machine-id` 는 systemd 환경에서 `/etc/machine-id` 를 `uninitialized` 로 바꿉니다[10]. 골든 이미지를 복제할 때 쓰는 정상 절차이기도 해서, 이 흔적만으로 은폐라고 보지 않습니다.
- **수집 명령이 URL 을 흔적으로 남깁니다.** AVML·UAC 는 SAS URL 이나 사전 서명 URL 을 명령줄 인자로 받습니다[5][6]. 이 URL 이 수집 대상 인스턴스의 [셸 명령 기록](../../02-artifacts/execution/shell-history/index.md)에 남을 수 있으므로, 만료 시간을 짧게 잡고 조사 기록에 "수집 작업이 남긴 명령" 으로 구분해 둡니다.
- **`--delete` 와 `--delete-local-on-successful-transfer` 는 게스트 디스크에 쓰고 지우는 일입니다[5][6].** 로컬 파일을 만들지 않으려면 `avml stream blob` 처럼 바로 보내는 방법을 씁니다[5].

## 결과를 어떻게 해석하나

**증명하는 것.** 스냅숏은 명령을 낸 시점(또는 멈춘 시점)에 디스크에 쓰여 있던 상태를 보여 줍니다[1]. `/var/lib/waagent/run-command/download` 의 스크립트와 그 stdout·stderr 는 Azure Run Command 로 게스트에서 실행한 기록입니다[8]. SSM Agent 로그는 AWS Systems Manager 에이전트가 남긴 기록이라[7], 관리 기능으로 들어온 작업의 흔적이 있는지 이 로그에서 확인합니다. cloud-init 로그는 부팅 단계별 출력과 사용자 스크립트 출력을 담으므로[9], 인스턴스를 띄울 때 무엇이 실행됐는지 보여 줍니다.

**증명하지 못하는 것.** 스냅숏에는 캐시에만 있던 데이터와 메모리 내용이 없습니다[1]. Run Command 나 SSM 흔적은 명령이 게스트에 들어왔다는 것까지만 보여 주고, 어느 계정이 보냈는지는 게스트 밖에 있는 제공자의 감사 기록을 따로 봐야 합니다. Compute Engine 의 `sourceDiskId` 는 스냅숏을 지금 있는 디스크에서 떴는지, 예전에 같은 이름으로 있던 디스크에서 떴는지 가르는 데 쓸 수 있습니다[2]. 디스크 이름만으로 원본을 특정하지 않습니다.

**시각.** 스냅숏 시각은 제공자가 매긴 값입니다. EC2 는 `StartTime`(시작)과 `CompletionTime`(완료)을 따로 기록하고, 담긴 데이터는 시작 명령을 낸 시점 기준입니다[1]. Compute Engine 의 `creationTimestamp` 는 RFC3339 텍스트 형식이고[2], 시간대는 값에 붙은 오프셋으로 확인합니다. `cloud-init analyze dump` 는 cloud-init 로그를 읽어 이벤트 목록을 JSON 으로 내고, `timestamp` 는 `1567057578.037` 처럼 소수점이 붙은 숫자로 나옵니다[12]. 이 값은 Unix 시각(초)일 가능성이 있으므로 같은 이벤트의 `/var/log/cloud-init.log` 줄 시각과 맞춰 보고 씁니다. `analyze show` 는 여러 부팅 기록을 오래된 것부터 차례로 보여 주므로[12], 이어 쓰인 `/var/log/cloud-init.log` 를 부팅 단위로 나눌 때 씁니다. 여러 출처의 시각은 [타임라인 만들기](../analysis/timeline.md)에서 한 줄로 맞춥니다.

**메타데이터 서비스 주소.** EC2 데이터 소스는 보통 `169.254.169.254` 의 HTTP 서버에서 user-data 와 메타데이터를 받고, 기본 주소 목록에는 `http://[fd00:ec2::254]` 도 있습니다[13]. Azure 의 인스턴스 메타데이터 서비스(IMDS)도 `169.254.169.254` 에 있고[14], Compute Engine 은 `http://meta-data.google.internal/computeMetadata/v1/` 입니다[15]. 셸 기록이나 네트워크 기록에서 이 주소가 보이면 인스턴스 메타데이터를 읽은 것일 가능성이 있습니다. cloud-init 도 정상적으로 이 주소에 접근하므로, 어느 프로세스·사용자가 접근했는지를 함께 봅니다.

보고서에는 "2026-03-02 01:10:00 UTC 에 시작한 스냅숏 snap-0example 은 볼륨 vol-0example 의 그 시점 상태이고, 인스턴스는 멈추지 않은 상태에서 떴다" 처럼 수집 조건까지 적습니다(만든 예시).

## 함께 볼 페이지

- [조사 절차](investigation-process.md)
- [라이브 응답 수집](live-response.md)
- [디스크 이미징](disk-imaging.md)
- [메모리 수집](memory-acquisition.md)
- [컨테이너 수집](container-acquisition.md)
- [KVM·libvirt](../../02-artifacts/containers/kvm-libvirt.md)

## 참고 문헌

1. boto/botocore, `botocore/data/ec2/2016-11-15/service-2.json`(CreateSnapshot, CreateSnapshots, GetConsoleOutput, GetConsoleScreenshot, Snapshot). https://github.com/boto/botocore/blob/develop/botocore/data/ec2/2016-11-15/service-2.json
2. googleapis/google-api-go-client, `compute/v1/compute-api.json`(disks.createSnapshot, instances.getSerialPortOutput, Snapshot, SerialPortOutput). https://github.com/googleapis/google-api-go-client/blob/main/compute/v1/compute-api.json
3. MicrosoftDocs/azure-compute-docs, `articles/virtual-machines/snapshot-copy-managed-disk.md`. https://github.com/MicrosoftDocs/azure-compute-docs/blob/main/articles/virtual-machines/snapshot-copy-managed-disk.md
4. MicrosoftDocs/azure-compute-docs, `articles/virtual-machines/linux/download-vhd.md`. https://github.com/MicrosoftDocs/azure-compute-docs/blob/main/articles/virtual-machines/linux/download-vhd.md
5. microsoft/avml, `README.md`, `src/bin/avml/acquire.rs`. https://github.com/microsoft/avml/blob/main/README.md , https://github.com/microsoft/avml/blob/main/src/bin/avml/acquire.rs
6. tclahr/uac, `lib/usage.sh`. https://github.com/tclahr/uac/blob/main/lib/usage.sh
7. tclahr/uac, `artifacts/files/system/aws_ssm_agent.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/files/system/aws_ssm_agent.yaml
8. tclahr/uac, `artifacts/files/system/azure_vm_agent.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/files/system/azure_vm_agent.yaml
9. canonical/cloud-init, `doc/rtd/reference/user_files.rst`. https://github.com/canonical/cloud-init/blob/main/doc/rtd/reference/user_files.rst
10. canonical/cloud-init, `doc/rtd/reference/cli.rst`. https://github.com/canonical/cloud-init/blob/main/doc/rtd/reference/cli.rst
11. canonical/cloud-init, `doc/rtd/explanation/instancedata.rst`. https://github.com/canonical/cloud-init/blob/main/doc/rtd/explanation/instancedata.rst
12. canonical/cloud-init, `doc/rtd/explanation/analyze.rst`. https://github.com/canonical/cloud-init/blob/main/doc/rtd/explanation/analyze.rst
13. canonical/cloud-init, `doc/rtd/reference/datasources/ec2.rst`. https://github.com/canonical/cloud-init/blob/main/doc/rtd/reference/datasources/ec2.rst
14. canonical/cloud-init, `doc/rtd/reference/datasources/azure.rst`. https://github.com/canonical/cloud-init/blob/main/doc/rtd/reference/datasources/azure.rst
15. canonical/cloud-init, `doc/rtd/reference/datasources/gce.rst`. https://github.com/canonical/cloud-init/blob/main/doc/rtd/reference/datasources/gce.rst
16. UAPI Group, "Linux File System Hierarchy"(`/run/`). https://github.com/uapi-group/specifications/blob/main/specs/linux_file_system_hierarchy.md
17. Oliveri, A., Cavenati, M., De Rosa, S., Lakshmi Narasimhan, S., Balzarotti, D. "LEMON: A universal eBPF-based volatile memory acquisition tool for modern android devices and hardened linux systems". Forensic Science International: Digital Investigation 56 (2026) 302045. https://doi.org/10.1016/j.fsidi.2026.302045
