---
title: "가상 머신·클라우드 디스크 확보"
parent: "증거 획득"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 3090
---

# 가상 머신·클라우드 디스크 확보 (VM·Cloud Disk)

> 상위 허브: [증거 획득 (Evidence Acquisition)](index.md)

## 한 줄 요약

가상 머신의 디스크는 호스트 안의 파일이나 클라우드의 디스크 스냅숏 (Snapshot) 으로 확보합니다.
차등 디스크는 부모와 달라진 부분만 담으므로 부모 파일까지 모두 모아야 전체 디스크를 읽을 수 있고, 클라우드 스냅숏은 요청한 시점에 디스크에 쓰인 데이터만 담습니다.

## 언제 쓰나

Hyper-V 나 VMware 같은 가상화 환경이나 Azure, AWS 같은 클라우드의 가상 머신을 조사할 때 씁니다.
실물 디스크를 뜨는 방법은 [디스크 이미징](disk-imaging.md) 에 있습니다.
가상 디스크 형식의 구조 전체는 [증거 이미지·가상 디스크 형식](../../../01-foundations/disk-volume/e01-raw-aff4-vhdx-vmdk.md) 에서 다룹니다. 이 페이지는 확보할 때 필요한 부분만 봅니다.

## 절차

1. **메모리를 먼저 뜰지 정합니다.** RFC 3227 과 SP 800-86 의 휘발성 순서에서 메모리는 디스크보다 앞서므로, 가상 머신을 멈추거나 끄기 전에 정합니다. 방법은 [메모리 분석](../../analysis/memory-forensics/index.md) 과 [라이브 응답](../live-response/index.md) 에 있습니다.
2. **가상 디스크 구성을 파악합니다.** 고정·동적·차등 가운데 무엇인지, 부모 파일과 익스텐트 파일이 몇 개인지 확인합니다.
3. **디스크를 확보합니다.** 온프레미스는 가상 디스크 파일과 부모·익스텐트 파일을 모두 복사합니다. 클라우드는 디스크 스냅숏을 뜹니다.
4. **해시를 계산해 따로 보관합니다.** 복사한 파일마다 계산합니다. 절차와 알고리즘은 [해시로 무결성 검증](hash-verification.md) 에 있습니다.
5. **사본으로 분석합니다.** 원본 가상 머신을 켜거나 접속하지 않고, 디스크 사본을 분석용 컴퓨터에 붙여 읽습니다.
6. **누가 언제 무엇을 했는지 기록합니다.** 기록 항목은 [증거 보관 연속성](chain-of-custody.md) 에 있습니다.

## 가상 디스크 파일 확보

### VHDX (Hyper-V)

VHDX 파일은 맨 앞 식별자로 알아봅니다.

```
VHDX 파일, 오프셋 0x00 (명세로 만든 예시)
00000000  76 68 64 78 66 69 6C 65  .. .. .. .. .. .. .. ..   vhdxfile........
```

오프셋 0 에 파일 형식 식별자 `vhdxfile` 이 있고, 오프셋 8 부터 512바이트에 만든 프로그램 이름이 UTF-16 LE 로 들어갑니다.
식별자 영역은 64 KiB 입니다.
이미지 헤더(4 KiB)와 영역 표(64 KiB)에는 CRC-32C 체크섬이 있어서, 복사한 파일의 머리 부분이 손상됐는지 이 값으로 확인할 수 있습니다.

VHDX 디스크 종류는 고정 (Fixed), 동적 (Dynamic), 차등 (Differential) 세 가지입니다.
차등 디스크는 부모-자식 관계로 이어집니다.

차등 이미지는 메타데이터 항목 "Parent locator" 로 부모를 가리키며, 부모 위치 형식 GUID 는 `b04aefb7-d19e-4a81-b789-25b8e9445913` 입니다.
부모 위치 항목의 키는 아래 표와 같고, 이 값으로 부모 파일을 찾아 함께 복사합니다.

| 키 | 뜻 |
|---|---|
| relative_path | 상대 경로 |
| absolute_win32_path | Win32 절대 경로 |
| volume_path | 볼륨 경로 |
| parent_linkage | 부모 연결 값 (GUID 문자열) |
| parent_linkage2 | 부모 연결 값 (두 번째 키) |

VHDX 의 가상 디스크 식별자는 차등 이미지와 부모 사이에서 바뀌지 않으며, 이 점이 VHD(버전 1)와 다릅니다.
VHDX 에는 메타데이터 저널 역할을 하는 로그 영역이 있습니다. 로그 항목 구조는 공개 명세에 아직 정리돼 있지 않으므로, 도구가 로그를 어떻게 처리하는지 확인하고 기록합니다.

### VMDK (VMware)

VMDK 디스크는 설명 파일 (Descriptor) 과 익스텐트 (Extent) 파일로 이뤄집니다.
설명 파일은 대소문자를 구분하지 않는 텍스트이며, 헤더, 익스텐트 설명, 변경 추적 파일, 디스크 데이터베이스(DDB) 항목이 들어갑니다.

| 헤더 필드 | 뜻 |
|---|---|
| version | 1, 2, 3 가운데 하나 |
| CID | 임의 32비트 값. 디스크를 연 뒤 내용이 처음 바뀔 때 새로 정합니다 |
| parentCID | 부모와 짝을 맞추는 값. `ffffffff` 이면 부모가 없습니다 |
| createType | 디스크 종류 |
| parentFileNameHint | 부모 파일 이름. 차등 이미지에만 있습니다 |
| encoding | 문자 인코딩. 기본값은 UTF-8 입니다 |

createType 값은 아래와 같습니다.

- 2GbMaxExtentFlat, 2GbMaxExtentSparse
- monolithicFlat, monolithicSparse
- vmfs, vmfsSparse, vmfsEagerZeroedThick, vmfsPreallocated, vmfsThin
- streamOptimized
- fullDevice, partitionedDevice, vmfsRaw, vmfsRDM, vmfsRDMP

익스텐트 설명 한 줄은 접근 방식, 섹터 수, 익스텐트 종류, 파일 이름으로 이뤄집니다.

접근 방식은 RW, RDONLY, NOACCESS 가운데 하나이고, 익스텐트 종류는 FLAT, SPARSE, ZERO, VMFS, VMFSSPARSE, VMFSRDM, VMFSRAW 가운데 하나입니다.
익스텐트 설명에 적힌 파일을 모두 복사해야 디스크 하나가 온전해집니다.

익스텐트 파일은 앞머리로 알아봅니다.

| 파일 | 오프셋 0 시그니처 | 헤더 크기 | 그레인 표 항목 수 |
|---|---|---|---|
| 희소 익스텐트 | `KDMV` (4바이트) | 512바이트 | 512 (고정) |
| ESX 희소 익스텐트 | `COWD` | 2,048바이트 | 4,096 |
| vmfs 평면 익스텐트 | 시그니처 대신 이름이 `-flat.vmdk` 로 끝납니다 | | |

```
희소 익스텐트 파일, 오프셋 0x00 (명세로 만든 예시)
00000000  4B 44 4D 56 .. .. .. ..  .. .. .. .. .. .. .. ..   KDMV............
```

그레인 (Grain) 크기는 2의 거듭제곱이고 8섹터보다 커야 합니다.
streamOptimized 는 deflate 로 압축한 희소 익스텐트 하나에 마커를 넣은 형식입니다. 마커에는 그레인, 그레인 표, 그레인 디렉터리, 꼬리, 스트림 끝이 있습니다.

### 델타 사슬을 끝까지 모읍니다

델타(차등) 이미지는 부모와 달라진 부분만 담고, CID 와 parentCID 로 부모와 짝을 맞춥니다.
델타 이미지는 다른 델타 이미지에 이어질 수 있어서 parentCID 가 `ffffffff` 인 설명 파일이 나올 때까지 부모를 따라가며 모두 모읍니다.

아래는 짝을 맞추는 모습을 보인 **명세로 만든 예시**입니다. 값은 지어낸 것입니다.

| 설명 파일 | CID | parentCID |
|---|---|---|
| 기반 디스크 | `1a2b3c4d` | `ffffffff` |
| 첫째 델타 | `5e6f7a8b` | `1a2b3c4d` |
| 둘째 델타 | `9c0d1e2f` | `5e6f7a8b` |

자식의 parentCID 가 부모의 CID 와 같아야 짝이 맞으며, 짝이 맞지 않으면 부모 파일이 바뀌었거나 다른 사슬의 파일일 수 있습니다.

## 클라우드 디스크 스냅숏

### Azure 예시 아키텍처

Microsoft 의 Azure 아키텍처 센터에는 디지털 증거의 보관 연속성을 다룬 예시 아키텍처가 있습니다.
법적 요청에 대응해 획득·보존·접근 전 단계에서 보관 연속성을 보이는 인프라와 절차를 담은 예시입니다.
작성자들의 지식에 바탕을 둔 예시이므로, 법적 용도로 쓰기 전에 법무 부서와 적용할 수 있는지 확인합니다.

구성은 이렇습니다.

SOC 팀만 접근하는 별도 SOC 구독을 두고, 이 구독의 스토리지 계정이 불변 (Immutable) Blob 저장소에 디스크 스냅숏 사본을 둡니다.
전용 Key Vault 는 스냅숏 해시 값을 비밀 (Secret) 로 저장합니다.

`Copy-VmDigitalEvidence` 런북은 아래 순서로 움직입니다.

1. Automation 계정의 시스템 할당 관리 ID 로 로그인합니다.
2. 가상 머신의 OS 디스크와 데이터 디스크 스냅숏을 만듭니다.
3. 스냅숏을 불변 Blob 저장소와 임시 파일 공유로 보냅니다.
4. 파일 공유의 사본으로 해시를 계산합니다.
5. 해시를 SOC Key Vault 에 저장합니다.
6. 불변 저장소의 사본만 남기고 나머지 사본을 모두 지웁니다.

이 솔루션이 지원하는 해시 알고리즘은 MD5, SHA256, SKEIN, KECCAK(SHA3) 입니다.
증거는 사람 손을 거치지 않고 Automation 으로 최종 보관 위치까지 옮깁니다.

증거 컨테이너에는 법적 보존 (Legal Hold) 정책을 겁니다.
불변 Blob 저장소는 WORM(한 번 쓰고 여러 번 읽기) 상태가 되어 정한 기간 동안 지우거나 고칠 수 없습니다. 법적 보존을 걸면 쓰는 즉시 증거가 고정됩니다.
법적 보존이 걸린 스냅숏은 지울 수 없어서 저장 비용이 쌓입니다.

조사자에게는 이렇게 접근을 줍니다.

조사자는 SAS URI 로 증거에 접근하는데, 이 예시에서는 SOC 관리자 두 명 가운데 한 명이 8시간 뒤 만료되는 읽기 전용 SAS URI 를 만듭니다.
조사자의 IP 는 스토리지 방화벽 허용 목록에 명시적으로 넣습니다.
조사자는 얻은 디스크 사본을 원본 가상 머신을 켜거나 접속하지 않고 분석용 컴퓨터에 붙일 수 있습니다.
접근 통제와 감사 로그로 보관 연속성을 보이는 부분은 [증거 보관 연속성](chain-of-custody.md) 에서 다룹니다.

이 예시가 다루지 않는 것도 있습니다.

임시 (Ephemeral) OS 디스크는 가상 머신 호스트에만 저장되고 디스크 스냅숏을 지원하지 않으므로, 증거를 모아야 할 수 있는 가상 머신에는 쓰지 않습니다.
이 아키텍처는 플랫폼 관리 키를 쓰는 호스트 암호화 (Encryption at Host) 를 전제로 합니다.

- BitLocker 나 dm-crypt 같은 운영체제 수준 암호화는 다루지 않습니다. 이런 디스크는 [암호화 증거 다루기](../../analysis/encrypted-evidence/index.md) 를 함께 봅니다.
- 규정에 따라 증거와 인프라를 같은 Azure 지역에 두어야 할 수 있습니다.
- 런북 단계에는 메모리 수집이 없습니다.

### AWS EBS 스냅숏

EBS 스냅숏의 성질은 아래와 같습니다.

스냅숏 생성은 비동기라서 스냅숏은 바로 만들어지지만, 모든 데이터가 Amazon S3 로 옮겨질 때까지 pending 상태입니다.
pending 상태에서 볼륨을 계속 써도 스냅숏에는 영향이 없습니다.
스냅숏에는 요청한 시점에 볼륨에 쓰인 데이터만 들어가고, 애플리케이션이나 운영체제가 캐시한 데이터는 들어가지 않습니다.
일관된 스냅숏을 얻으려면 쓰기를 멈추고, 멈출 수 없으면 인스턴스 안에서 볼륨을 마운트 해제합니다.

- 루트 장치 볼륨은 인스턴스를 멈춘 뒤 스냅숏을 뜹니다.
- 인스턴스에 붙은 볼륨 전부나 일부를 한 번에 뜨는 다중 볼륨 스냅숏이 있습니다.
- 스냅숏은 원본 볼륨과 암호화 상태가 같습니다. 암호화된 볼륨의 스냅숏은 같은 KMS 키로 암호화됩니다.
- 한 리전에 있는 볼륨의 스냅숏은 같은 리전에 만들어야 합니다.
- 최대 절전 (Hibernation) 중이거나 최대 절전을 켠 인스턴스의 볼륨은 스냅숏을 뜨지 않습니다.

포렌식 순서와 부딪치는 점이 하나 있습니다.

AWS 문서는 루트 볼륨을 뜨기 전에 인스턴스를 멈추라고 권하지만, 인스턴스를 멈추면 메모리 내용이 사라진다는 경고는 없습니다.
RFC 3227 과 SP 800-86 의 휘발성 순서는 메모리를 디스크보다 먼저 두므로 인스턴스를 멈추기 전에 메모리를 먼저 확보할지 정합니다.

## 함정과 한계

- **차등·델타 파일만 복사합니다.** 부모와 달라진 부분만 담은 파일이라 부모 없이는 전체 디스크를 읽을 수 없습니다.
- **익스텐트 파일 일부만 복사합니다.** 설명 파일에 적힌 익스텐트 파일을 모두 모읍니다.
- **스냅숏에 캐시 데이터까지 있다고 여깁니다.** EBS 스냅숏에는 애플리케이션과 운영체제가 캐시한 데이터가 들어가지 않습니다.
- **메모리를 판단하지 않고 인스턴스를 멈춥니다.** 메모리 내용이 사라집니다.
- **임시 OS 디스크를 쓰는 가상 머신에서 스냅숏을 기대합니다.** 임시 OS 디스크는 디스크 스냅숏을 지원하지 않습니다.
- **스냅숏이면 암호가 풀려 있다고 여깁니다.** 운영체제 수준 암호화를 쓴 디스크는 스냅숏 안에서도 암호화된 상태입니다.
- **법적 보존 비용을 잊습니다.** 법적 보존이 걸린 스냅숏은 지울 수 없어 비용이 계속 쌓입니다.
- **예시 아키텍처를 그대로 법적 절차로 씁니다.** 예시 아키텍처는 법적 절차가 아니므로 법무 부서와 먼저 확인합니다.

## 결과를 어떻게 해석하나

- **알 수 있는 것**: 클라우드 스냅숏은 스냅숏을 요청한 시점에 볼륨에 쓰인 데이터를 담습니다.
- **알 수 있는 것**: 차등 사슬을 조립한 결과는 조립에 쓴 마지막 자식 파일까지 반영한 디스크 내용입니다.
- **알 수 없는 것**: 메모리와 캐시에만 있던 데이터.
- **알 수 없는 것**: 모으지 못한 부모·익스텐트 파일에 있던 내용.

보고서에는 무엇을 어떤 방식으로 확보했는지 씁니다.

> `<날짜 시각, 시간대>` 에 가상 머신 `<이름>` 의 OS 디스크와 데이터 디스크 스냅숏을 만들었다. 스냅숏 사본의 해시(`<알고리즘>`)를 계산해 `<보관 위치>` 에 따로 저장했다. 스냅숏 전에 메모리는 `<확보함 / 확보하지 않음>`.

## 참고 문헌

- libyal/libvhdi, *Virtual Hard Disk version 2 (VHDX) image format* — https://raw.githubusercontent.com/libyal/libvhdi/main/documentation/Virtual%20Hard%20Disk%20version%202%20(VHDX)%20image%20format.asciidoc
- libyal/libvmdk, *VMWare Virtual Disk Format (VMDK)* — https://raw.githubusercontent.com/libyal/libvmdk/main/documentation/VMWare%20Virtual%20Disk%20Format%20(VMDK).asciidoc
- Microsoft Learn, *Computer Forensics Chain of Custody in Azure* (Azure Architecture Center) — https://learn.microsoft.com/en-us/azure/architecture/example-scenario/forensics/
- AWS Documentation, *Create Amazon EBS snapshots* (Amazon EBS User Guide) — https://docs.aws.amazon.com/ebs/latest/userguide/ebs-creating-snapshot.html
- D. Brezinski, T. Killalea, *RFC 3227: Guidelines for Evidence Collection and Archiving* (BCP 55, 2002-02) — https://www.rfc-editor.org/rfc/rfc3227
- Karen Kent, Suzanne Chevalier, Tim Grance, Hung Dang, *NIST SP 800-86: Guide to Integrating Forensic Techniques into Incident Response* (2006-08) — https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf
