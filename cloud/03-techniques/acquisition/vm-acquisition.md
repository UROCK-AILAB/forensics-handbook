---
title: "클라우드 가상 머신 수집"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 670
---

# 클라우드 가상 머신 수집 (VM·Disk Acquisition)

클라우드 가상 머신의 디스크는 서버를 뜯지 않고 제어 평면에서 스냅숏으로 떠서 조사 계정으로 옮기며, 그 전에 멈추면 사라지는 메모리와 임시 저장소를 게스트 안에서 먼저 확보합니다.

## 언제 쓰나

AWS EC2, Azure VM, Google Compute Engine 인스턴스 안에서 무슨 일이 있었는지 파일 시스템 수준으로 봐야 할 때 씁니다. 제어 평면 로그는 누가 인스턴스를 만들고 바꿨는지까지만 보여 주고, 인스턴스 안에서 실행한 명령·내려받은 파일·남긴 백도어는 디스크에 있습니다. 게스트 OS 안의 분석 방법은 Linux 판의 [클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html)·[디스크 이미징](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/disk-imaging.html)·[메모리 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/memory-acquisition.html)에서 다루고, 이 페이지는 클라우드 제어 평면에서 디스크 사본을 뜨고 꺼내는 순서와 그 과정이 남기는 흔적을 다룹니다.

디스크 사본을 뜨기 전에 제어 평면 로그부터 보존합니다. 순서와 방법은 [로그부터 지키기](log-preservation.md)에, 조사 전체의 틀은 [조사 절차](investigation-process.md)에 있습니다. 고객이 디스크 사본을 직접 뜰 수 있는 범위는 [책임 공유와 조사 범위](../../01-foundations/model/shared-responsibility.md)에서 정해집니다.

## 세 서비스 한눈에 보기

| 항목 | AWS EBS | Azure 관리 디스크 | Google Cloud Persistent Disk·Hyperdisk |
|---|---|---|---|
| 사본 단위 | 증분 스냅숏. 직전 스냅숏 뒤로 바뀐 블록만 저장[1] | 관리 디스크의 전체 읽기 전용 사본. 포털에서는 Full·Incremental 선택[9][10] | 스냅숏 유형 `STANDARD`(기본)·`ARCHIVE`, 기본으로 전역 리소스[14] |
| 실행 중 뜨기 | 가능. 요청 시점에 볼륨에 쓰인 데이터만 들어가고 캐시는 빠짐. 루트 볼륨이면 인스턴스 중지 권장[2] | 가능하지만 전원을 껐다 켜거나 충돌한 순간과 같은 상태. 데이터 디스크가 있으면 VM 중지 권장[10] | 실행 중인 인스턴스에 붙은 디스크도 가능[14] |
| 밖으로 꺼내기 | 다른 계정에 공유, EBS direct API 로 블록 읽기[3][4] | SAS URL 로 VHD 내려받기[10] | 이미지로 만든 뒤 Cloud Storage 로 내보내기(`disk.raw` 를 tar·gzip)[15] |
| 제어 평면 기록 | CloudTrail `ModifySnapshotAttribute`, `SharedSnapshotCopyInitiated`·`SharedSnapshotVolumeCreated`, `StartSnapshot`·`CompleteSnapshot`(EBS direct API)[3][5][8] | 활동 로그 `Microsoft.Compute/snapshots/write`, `disks/beginGetAccess/action`·`snapshots/beginGetAccess/action`, `endGetAccess/action`[12] | 관리 활동 로그 `v1.compute.disks.createSnapshot`, `v1.compute.snapshots.insert`, `v1.compute.images.insert`[16] |
| 멈추면 사라지는 저장소 | 인스턴스 스토어(중지·최대 절전·종료 때 지워짐)[6] | 임시 OS 디스크(스냅숏 지원 안 함)[11] | 실제 인스턴스 구성에서 확인 |

표의 값은 2026년 9월 문서 기준입니다.

## 절차

> 그림 자리: 게스트 안 휘발성 수집 → 스냅숏 → 조사 계정으로 옮기기 → 해시·보관 → 분석용 인스턴스에 붙이기, 각 단계가 남기는 제어 평면 기록을 옆에 표시

1. **조사에 쓸 계정과 기록 양식을 정합니다.** 스냅숏을 뜨고 공유하고 SAS 를 발급하는 일은 모두 제어 평면 로그에 조사자의 작업으로 남습니다[3][5][11][12][16]. 나중에 공격자의 작업과 가를 수 있게 조사용 계정·역할, 작업 시각(UTC), 원본 인스턴스와 볼륨 ID 를 기록합니다. 조사자 활동을 기록하는 방법은 [조사 절차](investigation-process.md)에 있습니다.

2. **인스턴스의 저장소 구성부터 확인합니다.** 붙어 있는 볼륨·디스크 목록, 인스턴스 스토어나 임시 OS 디스크를 쓰는지, 최대 절전이 켜져 있는지, 게스트 OS 안에서 BitLocker·dm-crypt 같은 OS 수준 암호화를 쓰는지 봅니다. AWS 인스턴스 스토어는 스냅숏 대상이 아니고, EBS 기반 AMI 를 만들어도 인스턴스 스토어 데이터는 들어가지 않습니다[6]. Azure 임시 OS 디스크 (ephemeral OS disk) 는 로컬 VM 호스트에만 저장되고 스냅숏을 지원하지 않습니다[11]. 이런 저장소가 있으면 3단계에서 게스트 안에서 떠야 합니다.

3. **멈추면 사라지는 것을 게스트 안에서 먼저 확보합니다.** 디스크 스냅숏에는 요청 시점에 볼륨에 쓰인 데이터만 들어가고, 애플리케이션이나 운영체제가 캐시한 데이터는 빠집니다[2]. 메모리·실행 중 프로세스·네트워크 연결은 Linux 판의 [라이브 응답 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/live-response.html)·[메모리 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/memory-acquisition.html)(Windows 게스트는 Windows 판의 [라이브 응답](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/process-acquisition/live-response/index.html))으로 뜨고, 인스턴스 스토어 내용도 이때 EBS 볼륨이나 저장소로 복사합니다. AWS 인스턴스 스토어는 재부팅에는 남지만 중지·최대 절전·종료하면 모든 블록이 암호학적으로 지워지고, 인스턴스 유형을 바꾸거나 OS 안에서 종료(shutdown)해도 데이터가 남지 않습니다[6]. 격리한다고 인스턴스를 먼저 멈추면 이 단계의 자료가 없어집니다.

   게스트에 로그인할 수 없으면 제어 평면에서 보조 자료를 받아 둡니다. EC2 콘솔 출력은 Linux 에서는 시작·중지·재부팅·종료 같은 상태 전환 직후의 버퍼된 출력이고, Windows 에서는 최근 시스템 이벤트 로그 오류 세 건입니다[7]. EC2 스크린숏은 100KB 이하 JPG 이고 CLI 는 base64 로 돌려주며, 베어메탈·Graviton 인스턴스와 일부 리전에서는 쓸 수 없습니다[7]. Google Cloud 의 `v1.compute.instances.getSerialPortOutput`·`getScreenshot` 은 데이터 접근 로그(`DATA_READ`)로 남습니다[16].

   ```bash
   aws ec2 get-console-output --instance-id i-0123456789abcdef0
   aws ec2 get-console-screenshot --instance-id i-0123456789abcdef0
   ```

   인스턴스 ID 는 만든 예시입니다.

4. **디스크 스냅숏을 뜹니다.** Azure 에서 실행 중에 뜬 스냅숏은 VM 전원을 껐다 켜거나 VM 이 충돌한 순간과 같은 상태라서, 충돌에 대비하지 않은 애플리케이션이면 문제가 생길 수 있습니다[10]. 스냅숏에는 요청 시점의 데이터가 들어가므로 디스크를 하나씩 따로 뜨면 디스크마다 시점이 다르고[2], AWS 에서는 인스턴스에 붙은 볼륨 전체나 일부를 한 번에 뜨는 다중 볼륨 스냅숏 (multi-volume snapshot) 을 쓸 수 있습니다[2]. 3단계를 마쳤다면 인스턴스를 멈춘 뒤 뜨는 편이 일관된 사본을 얻습니다. AWS 는 루트 볼륨이면 인스턴스 중지를[2], Azure 는 데이터 디스크가 하나라도 있으면 VM 중지를 권합니다[10]. Google Cloud 에서 애플리케이션을 멈추고 떴다면 스냅숏이 `UPLOADING` 상태가 된 뒤에 다시 돌립니다[14].

   ```bash
   # Azure: OS 디스크 스냅숏
   osDiskId=$(az vm show -g rg-example -n web01      --query "storageProfile.osDisk.managedDisk.id" -o tsv)
   az snapshot create -g rg-example --source "$osDiskId" --name evidence-os-snap
   # Google Cloud: 영역 디스크 스냅숏
   gcloud compute snapshots create SNAPSHOT_NAME \
     --source-disk-zone=SOURCE_ZONE \
     --source-disk=SOURCE_DISK_NAME \
     --snapshot-type=STANDARD
   ```

   리소스 그룹·VM·스냅숏 이름은 만든 예시이고, Google Cloud 명령의 대문자 부분은 실제 값으로 바꿉니다[14]. Azure PowerShell 에서는 `New-AzSnapshotConfig -CreateOption copy` 로 설정을 만들고 `New-AzSnapshot` 으로 뜹니다[9].

   EBS 스냅숏은 만들자마자 생기지만, 데이터가 모두 옮겨질 때까지 `pending` 상태로 몇 시간 걸릴 수 있습니다[2]. 스냅숏에 들어가는 것은 요청 시점의 데이터이므로[2], 기록에는 요청 시각과 완료 시각을 따로 적고 "요청 시점의 볼륨" 으로 씁니다.

5. **조사 계정으로 옮기거나 파일로 꺼냅니다.** 서비스마다 방법과 제약이 다릅니다.

   | 서비스 | 방법 | 제약 |
   |---|---|---|
   | AWS | 스냅숏의 `createVolumePermission` 속성에 조사 계정 ID 를 넣어 공유하고, 조사 계정에서 복사하거나 볼륨을 만듦[3] | 스냅숏은 만든 리전에 묶여 다른 리전은 복사한 뒤 공유. 기본 AWS 관리형 키로 암호화한 스냅숏은 공유할 수 없고 고객 관리형 키로 암호화한 것만 되며, 그 KMS 키도 함께 공유해야 함[3] |
   | AWS | EBS direct API 로 볼륨을 만들지 않고 블록을 읽음(`ListSnapshotBlocks`·`GetSnapshotBlock`, 두 스냅숏 차이는 `ListChangedBlocks`)[4][5] | 블록 읽기는 CloudTrail 데이터 이벤트라 기본으로 기록되지 않음[5] |
   | Azure | 디스크나 스냅숏에 읽기 전용 SAS URL 을 발급해 VHD 를 내려받고, 다 받으면 회수[10] | 실행 중인 VM 에 붙은 디스크는 받을 수 없어 VM 을 Stopped (deallocated) 로 만들거나 스냅숏에서 받음. 포털의 SAS 기본 만료는 3,600초, 2025년 2월 15일부터 최대 60일(5,184,000초)[10] |
   | Google Cloud | 스냅숏에서 이미지를 만든 뒤 `gcloud compute images export` 로 Cloud Storage 에 내보냄[15] | 기본 형식은 `disk.raw` 를 tar 로 묶어 gzip 한 파일이고, `--export-format` 으로 `vmdk`·`vhdx`·`vpc`·`vdi`·`qcow2` 를 고름. Cloud Build 세션은 최대 24시간[15] |

   AWS 공유와 Azure SAS 발급은 아래처럼 합니다. 스냅숏 ID·계정 ID·이름은 만든 예시입니다.

   ```bash
   aws ec2 modify-snapshot-attribute \
     --snapshot-id snap-0123456789abcdef0 \
     --attribute createVolumePermission \
     --operation-type add \
     --user-ids 123456789012

   az disk grant-access --duration-in-seconds 3600 --access-level Read \
     --name evidence-os-disk --resource-group rg-example --query accessSas --output tsv
   az disk revoke-access --name evidence-os-disk --resource-group rg-example

   gcloud compute images export \
     --destination-uri gs://evidence-bucket-example/web01-os.tar.gz \
     --image web01-os-image
   ```

   PowerShell 에서는 `Grant-AzDiskAccess ... -Access 'Read'` 로 발급하고 `Revoke-AzDiskAccess` 로 회수합니다[10]. Microsoft Entra ID 로 디스크 내려받기를 보호하는 환경이면 내려받는 사람에게 RBAC 권한이 있어야 하고, `az storage blob download` 에 `--auth-mode login` 을 붙입니다[10].

6. **해시를 떠서 따로 보관합니다.** 받은 파일의 해시를 계산하고, 해시는 증거 사본과 다른 곳에 둡니다. Azure 참조 구조는 이 순서를 자동화한 예입니다. 별도 SOC 구독의 Automation 하이브리드 Runbook Worker 가 `Copy-VmDigitalEvidence` Runbook 으로 OS·데이터 디스크 스냅숏을 떠서 법적 보존 (legal hold) 정책이 걸린 불변 Blob 과 임시 파일 공유로 옮기고, 파일 공유의 사본으로 해시를 계산해 SOC Key Vault 에 저장한 뒤 불변 Blob 사본만 남기고 지웁니다[11]. 해시 알고리즘은 MD5·SHA256·SKEIN·KECCAK(SHA3) 가운데 고릅니다[11]. Automation 계정의 관리 ID (managed identity) 에는 SOC 쪽 Storage Account Contributor·Key Vault Secrets Officer 와 대상 VM 리소스 그룹의 Contributor 역할이 필요하고, 조사자에게는 만료가 짧은 읽기 전용 SAS(예: 8시간)를 주고 Storage 방화벽에 조사자 IP 를 허용합니다[11]. 이 구조는 증거와 인프라를 조사 대상과 같은 리전에 둡니다[11]. 이 구조를 법적 용도로 쓰기 전에는 법무 부서와 적용 가능성을 검토합니다[11]. 보고서의 무결성 문장은 [클라우드 포렌식 보고서](../reporting/forensic-report.md)를 따릅니다.

7. **분석용 인스턴스에 붙여 봅니다.** 사본은 원본 VM 을 켜지 않고 분석 전용 컴퓨터에 붙일 수 있습니다[11]. AWS 에서는 공유받은 스냅숏으로 조사 계정에 볼륨을 만들어 분석 인스턴스에 붙이고, Azure 는 받은 VHD 나 스냅숏으로 만든 디스크를, Google Cloud 는 내려받은 `disk.raw` 를 씁니다. 붙인 뒤에는 읽기 전용으로 올리고 파일 시스템을 분석합니다. 그 과정은 Linux 판 [디스크 이미징](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/disk-imaging.html)을 따릅니다.

8. **제어 평면 로그로 수집 과정을 다시 따라가 봅니다.** 조사자의 작업이 기록한 대로 남았는지, 조사 기간 안에 다른 주체가 같은 스냅숏을 만들거나 공유하거나 내려받지 않았는지 봅니다.

   | 서비스 | 볼 기록 | 뜻 |
   |---|---|---|
   | AWS | CloudTrail `eventSource` `ec2.amazonaws.com`, `eventName` `ModifySnapshotAttribute`[8] | 스냅숏 공유 권한을 바꿈 |
   | AWS | 소유 계정 CloudTrail `SharedSnapshotCopyInitiated`·`SharedSnapshotVolumeCreated`[3] | 공유받은 쪽이 복사하거나 볼륨을 만듦 |
   | AWS | `eventSource` `ebs.amazonaws.com`, `StartSnapshot`·`CompleteSnapshot`(관리 이벤트), `ListSnapshotBlocks`·`ListChangedBlocks`·`GetSnapshotBlock`·`PutSnapshotBlock`(데이터 이벤트)[5] | EBS direct API 로 스냅숏을 만들거나 블록을 읽고 씀 |
   | Azure | `Microsoft.Compute/snapshots/write`·`/delete`, `Microsoft.Compute/disks/beginGetAccess/action`·`endGetAccess/action`, `Microsoft.Compute/snapshots/beginGetAccess/action`·`endGetAccess/action`[12] | 스냅숏 만들기·삭제, 디스크·스냅숏 SAS 발급·회수 |
   | Google Cloud | `v1.compute.disks.createSnapshot`·`v1.compute.regionDisks.createSnapshot`·`v1.compute.snapshots.insert`·`v1.compute.instantSnapshots.insert`·`v1.compute.machineImages.insert`·`v1.compute.images.insert`(관리 활동, `ADMIN_WRITE`), `v1.compute.snapshots.setIamPolicy`(`ADMIN_WRITE`)[16] | 스냅숏·이미지 만들기, 스냅숏 IAM 정책 변경 |

   Azure 활동 로그의 `operationName` 이 위 권한 이름과 같은 모양으로 남는지(대소문자 포함)는 실제 로그로 확인합니다. 레코드 구조와 예시는 [EC2 인스턴스와 스냅숏](../../02-artifacts/aws/ec2-ebs.md), [Azure 가상 머신](../../02-artifacts/azure/azure-vm.md), [활동 로그](../../02-artifacts/azure/activity-log.md), [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md)에 있습니다.

## 도구

디스크 사본은 각 서비스의 기본 CLI 로 뜹니다. AWS 는 AWS CLI(`aws ec2 modify-snapshot-attribute`, `get-console-output`, `get-console-screenshot`)[3][7]와 EBS direct API[4], Azure 는 Azure CLI(`az snapshot create`, `az disk grant-access`, `az disk revoke-access`, `az storage blob download`)와 Az PowerShell(`New-AzSnapshotConfig`, `New-AzSnapshot`, `Grant-AzDiskAccess`, `Revoke-AzDiskAccess`, `Get-AzStorageBlobContent`)[9][10], Google Cloud 는 gcloud(`gcloud compute snapshots create`, `gcloud compute images export`)[14][15]를 씁니다. Azure 에서 수집을 자동화하고 증거 관리 연속성 (chain of custody) 을 남기려면 `Copy-VmDigitalEvidence` Runbook 을 쓰는 참조 구조가 있습니다[11].

게스트 안에서 명령을 돌리는 Azure Run Command 는 수집 도구로 쓰기에 제약이 큽니다. 출력은 마지막 4,096바이트만 돌려주고, 한 번에 스크립트 하나만 돌며, 최대 90분까지 돌고 도중에 취소할 수 없고, 결과를 돌려받으려면 VM 에서 밖으로 나가는 연결이 필요합니다[13]. Linux 에서는 기본으로 권한이 상승된 사용자로 실행되고 `/var/log/azure/run-command/handler.log` 에 기록이 남습니다[13]. 이 기록과 활동 로그의 `Microsoft.Compute/virtualMachines/runCommand/action`[12]은 조사자의 흔적이므로 수집 기록에 적습니다. Run Command 의 두 방식 차이는 [Azure 가상 머신](../../02-artifacts/azure/azure-vm.md)에 있습니다.

## 함정과 한계

- **스냅숏에는 메모리가 없습니다.** 요청 시점에 쓰인 데이터만 들어가고 캐시는 빠집니다[2]. 메모리는 3단계에서 게스트 안에서 뜹니다.
- **멈추면 사라지는 저장소가 있습니다.** AWS 인스턴스 스토어는 중지·최대 절전·종료에서 지워지고[6], Azure 임시 OS 디스크는 스냅숏이 되지 않습니다[11]. 격리하려고 인스턴스를 먼저 멈추면 되돌릴 수 없습니다.
- **최대 절전을 켠 EC2 인스턴스는 조심합니다.** AWS 는 최대 절전 상태이거나 최대 절전이 켜진 인스턴스에 붙은 볼륨의 스냅숏을 권하지 않습니다[2].
- **실행 중 스냅숏은 충돌 직후 상태입니다**[10]. 디스크를 하나씩 따로 뜨면 디스크마다 요청 시각이 달라 시점이 어긋납니다[2].
- **스냅숏 공유는 유출 탐지 규칙에 걸리는 작업입니다.** `ModifySnapshotAttribute` 는 다른 계정이 스냅숏을 쓸 수 있게 권한을 바꾸는 작업이라 유출(T1537) 탐지 규칙의 대상입니다[8]. 조사용 공유가 보안 경보를 일으킬 수 있으므로 보안 운영 쪽에 미리 알리고 조사 계정 ID 와 시각을 기록합니다.
- **기본 AWS 관리형 키로 암호화한 스냅숏은 공유되지 않습니다**[3]. 암호화한 볼륨의 스냅숏은 원본 볼륨과 같은 KMS 키로 암호화되므로[2], 조사 계정으로 옮기기 전에 어떤 키로 암호화됐는지 확인합니다.
- **공유한 스냅숏을 받은 쪽이 블록을 읽어도 소유 계정에는 데이터 이벤트가 가지 않습니다**[5]. 소유 계정 로그만 보고 "읽힌 적 없다" 고 쓸 수 없습니다.
- **Azure SAS URL 은 만료되거나 회수될 때까지 디스크를 읽을 수 있는 링크입니다.** 만료 시각과 회수 시각을 기록합니다. SAS 가 유효한 동안 VM 을 켜려고 하면 "There is an active shared access signature outstanding for disk" 오류가 나서 VM 이 시작되지 않습니다[10].
- **Google Cloud 이미지 내보내기는 대상 프로젝트에 자원을 만듭니다.** `${PROJECT}-daisy-bkt-${REGION}` 버킷과 임시 디스크·VM 이 생기고, 세션이 끊기거나 작업이 실패하면 이 자원이 남을 수 있고, 그때는 직접 지웁니다[15]. 이 자원은 조사자의 활동으로 기록합니다. Google 제공 라이선스를 쓰는 Windows Server 이미지는 Google Cloud 밖에서 쓸 목적으로 내보낼 수 없습니다[15].
- **Google Cloud 스냅숏이 실패하면 원본 디스크를 지울 수 없습니다.** 깨끗한 스냅숏을 뜰 때까지 원본 디스크 삭제를 막는 안전장치입니다[14]. 정리 작업이 막히면 실패한 스냅숏이 있는지 봅니다.
- **OS 수준 암호화 디스크는 사본만으로는 읽지 못할 수 있습니다.** Azure 참조 구조는 플랫폼 관리 키를 쓰는 호스트 암호화를 전제로 하고, BitLocker·dm-crypt 같은 OS 수준 암호화는 환경마다 구현이 달라 다루지 않습니다[11]. 복구 키를 어디서 받을지 수집 전에 확인합니다.

## 결과를 어떻게 해석하나

**증명하는 것.** 스냅숏은 요청 시점의 블록 장치 내용입니다[1][2]. 받은 직후 해시를 떠서 별도 저장소에 두고 사본을 불변 저장소에 보관했다면, 획득 뒤로 사본이 바뀌지 않았다는 근거가 됩니다[11]. 누가 언제 스냅숏을 뜨고 공유하고 SAS 를 발급했는지는 제어 평면 로그가 보여 줍니다[5][11][12][16].

**증명하지 못하는 것.** 메모리와 캐시 상태[2], 인스턴스 스토어 내용[6], 스냅숏 뒤에 일어난 변화, OS 수준 암호화 디스크의 평문(키가 없으면)은 스냅숏에 없습니다. AWS 스냅숏 두 개를 비교하면 바뀐 블록은 알 수 있지만[4], 그 사이에 블록이 언제 어떤 순서로 바뀌었는지는 알 수 없습니다. Azure SAS 발급 기록은 내려받을 수 있는 링크를 받았다는 기록이지 실제로 내려받았다는 기록은 아닙니다.

**시각.** 스냅숏의 기준 시각은 완료 시각이 아니라 요청 시각입니다[2]. CloudTrail 의 `eventTime` 은 `2020-07-03T23:27:26Z` 처럼 UTC 로 적히고, `StartSnapshot` 응답의 `startTime` 은 `Jul 3, 2020 11:27:26 PM` 처럼 시간대 표시가 없는 문자열입니다[5]. 타임라인에는 같은 레코드의 `eventTime` 을 씁니다. 서비스별 시각 표기는 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 있습니다. 스냅숏 안 파일의 시각은 게스트 운영체제의 기준을 따르므로, 두 시각을 합치는 방법은 [클라우드 타임라인](../analysis/timeline.md)과 Linux 판 [타임라인 만들기](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/timeline.html)를 봅니다.

보고서에는 "2026년 9월 2일 14:05 UTC 에 조사용 역할로 인스턴스 i-0123456789abcdef0 의 볼륨 스냅숏 snap-0123456789abcdef0 을 요청했고, 조사 계정 123456789012 로 공유해 만든 볼륨의 SHA256 해시는 보관 목록과 같다" 처럼 한 일과 기록을 그대로 씁니다(만든 예시).

## 참고 문헌

1. AWS, "Amazon EBS snapshots", Amazon EBS User Guide. https://docs.aws.amazon.com/ebs/latest/userguide/ebs-snapshots.html
2. AWS, "Create Amazon EBS snapshots", Amazon EBS User Guide. https://docs.aws.amazon.com/ebs/latest/userguide/ebs-creating-snapshot.html
3. AWS, "Share an Amazon EBS snapshot with other AWS accounts", Amazon EBS User Guide. https://docs.aws.amazon.com/ebs/latest/userguide/ebs-modifying-snapshot-permissions.html
4. AWS, "Use EBS direct APIs to access the contents of an EBS snapshot", Amazon EBS User Guide. https://docs.aws.amazon.com/ebs/latest/userguide/ebs-accessing-snapshot.html
5. AWS, "Log EBS direct APIs calls using AWS CloudTrail", Amazon EBS User Guide. https://docs.aws.amazon.com/ebs/latest/userguide/logging-ebs-apis-using-cloudtrail.html
6. AWS, "Data persistence for Amazon EC2 instance store volumes", Amazon EC2 User Guide. https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-store-lifetime.html
7. AWS, "Troubleshoot an unreachable Amazon EC2 instance", Amazon EC2 User Guide. https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-console.html
8. SigmaHQ, "AWS Snapshot Backup Exfiltration" (aws_snapshot_backup_exfiltration.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_snapshot_backup_exfiltration.yml
9. Microsoft, "Create a snapshot of an Azure managed disk", Microsoft Learn (2026-09-19). https://learn.microsoft.com/en-us/azure/virtual-machines/snapshot-copy-managed-disk
10. Microsoft, "Download a Windows VHD from Azure", Microsoft Learn (2026-09-03). https://learn.microsoft.com/en-us/azure/virtual-machines/windows/download-vhd
11. Microsoft, "Computer forensics chain of custody in Azure", Azure Architecture Center. https://learn.microsoft.com/en-us/azure/architecture/example-scenario/forensics/
12. Microsoft, "Azure permissions for Compute", Microsoft Learn (2026-07-01). https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/compute
13. Microsoft, "Run scripts in your Linux VM by using action Run Commands", Microsoft Learn (2025-08-27). https://learn.microsoft.com/en-us/azure/virtual-machines/linux/run-command
14. Google Cloud, "Create archive and standard disk snapshots", Compute Engine documentation (2026-09-24). https://cloud.google.com/compute/docs/disks/create-snapshots
15. Google Cloud, "Export a custom image to Cloud Storage", Compute Engine documentation (2026-09-24). https://cloud.google.com/compute/docs/images/export-image
16. Google Cloud, "Compute Engine audit logging", Compute Engine documentation (2026-09-24). https://cloud.google.com/compute/docs/logging/audit-logging
