---
title: "USB 로 무엇을 가져갔나"
parent: "자료를 밖으로 빼돌렸나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 3590
---

# USB 로 무엇을 가져갔나 (USB)

> 상위 허브: [자료를 밖으로 빼돌렸나 (Data Exfiltration)](index.md)

USB 메모리나 외장 디스크가 언제 어느 드라이브 문자로 붙었는지는 [USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md) 허브에서 다룹니다. 이 페이지는 그 연결 기록에 이벤트 로그와 파일을 연 흔적을 이어 붙이는 순서를 다룹니다.

아래 이벤트 로그 설정과 칸 구성은 Windows 11 Home 25H2(빌드 26200.9457) 기준이며, 다른 빌드에서는 다를 수 있습니다.

## 조사 질문

- 어떤 USB 저장장치가 이 PC 에 붙었습니까? 언제 붙었고 언제 빠졌습니까?
- 장치가 붙어 있는 동안 누가 장치 안의 어떤 파일과 폴더를 열었습니까?
- 이 기록으로 "파일을 가져갔다" 고 어디까지 말할 수 있습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | 장치 속성에 남는 시각의 종류가 버전마다 다릅니다. 버전별 표는 [USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md) 에 있습니다. |
| 시간대 | 기록마다 시각 기준이 다릅니다. `setupapi.dev.log` 는 현지 시각이고, 장치 속성·키 시각·바로가기 파일 시각은 UTC 입니다. [시간대 설정](../../../02-artifacts/system-account/time-zone.md) 을 먼저 읽어 둡니다. |
| 사용자 | 장치 기록이 모인 SYSTEM 하이브에는 사용자 정보가 없습니다. 사용자는 NTUSER.DAT 와 사용자별 바로가기 파일·점프리스트·셸백으로 좁힙니다. |
| 수집 범위 | SYSTEM·SOFTWARE·사용자 하이브, `setupapi.dev.log`, 이벤트 로그, 사용자 프로필 폴더를 함께 확보합니다. 장치 실물이 있으면 장치도 이미지로 확보합니다. |

이벤트 로그는 먼저 확보합니다. 아래에서 보듯 크기가 작고 순환하는 로그가 있어 시간이 지나면 오래된 기록이 사라집니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | USBSTOR·Enum\USB·장치 속성·MountedDevices·MountPoints2·setupapi.dev.log·WPD·EMDMgmt | 어떤 장치가 언제 어느 드라이브 문자로 붙었나, 볼륨 시리얼 번호 | [USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md) |
| 2 | Partition/Diagnostic 1006, Kernel-PnP/Configuration 400·410 | 처음과 마지막 사이의 연결, 버스 종류, 모델·시리얼 번호 | [외부 장치 연결 이벤트](../../../02-artifacts/event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) |
| 3 | 바로가기 파일 | 장치 안에서 연 파일, 드라이브 종류, 드라이브 시리얼 번호, 대상 파일의 시각 | [바로가기 파일](../../../02-artifacts/file-folder-usage/lnk.md) |
| 4 | 점프리스트 | 앱별로 최근에 연 파일 | [점프리스트](../../../02-artifacts/file-folder-usage/jump-lists.md) |
| 5 | 셸백 | 장치 안에서 탐색기로 연 폴더 | [셸백](../../../02-artifacts/file-folder-usage/shellbags/index.md) |
| 6 | 파일 접근 감사 | 감사를 켜 둔 PC 에서만, 원본 파일에 접근한 기록 | [파일 접근 감사](../../../02-artifacts/event-logs/4656-4663-4660.md) |

## 이벤트 로그로 연결 사이를 채우기

장치 속성에는 대부분 처음 시각과 마지막 시각만 남습니다. 그 사이의 연결은 이벤트 로그에서 찾습니다. 로그 파일을 읽는 법은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에서 다룹니다.

### Partition/Diagnostic 1006

로그 파일은 `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-Partition%4Diagnostic.evtx` 이고, 이 빌드에서는 켜져 있습니다. 최대 크기는 16MB 이고 순환 (Circular) 방식이어서, 가득 차면 오래된 이벤트부터 덮어씁니다. 이 로그의 이벤트는 모두 ID 1006, 이벤트 버전 7 입니다.

공급자 설명문이 "For internal use only." 라서 칸의 뜻은 이름으로 읽고 다른 기록과 맞춰 확인합니다. 버전 7 의 1006 에는 칸이 85개 있고, 조사에 쓰는 칸은 아래와 같습니다.

| 묶음 | 칸 이름 |
|---|---|
| 장치를 가리키는 칸 | DiskNumber, Capacity, BusType, Manufacturer, Model, Revision, SerialNumber, Location, ParentId, DiskId, AdapterId, RegistryId, PoolId, StorageId, AdapterSerialNumber, UserRemovalPolicy |
| 디스크 구조 칸 | PartitionStyle, PartitionCount, PartitionTableBytes, PartitionTable, MbrBytes, Mbr, Ebr0~Ebr3 |

디스크 구조 칸은 [파티션 구조](../../../01-foundations/disk-volume/mbr-gpt.md) 를 알고 읽습니다.

**BusType 으로 USB 연결 고르기.** BusType 칸의 값은 STORAGE_BUS_TYPE 열거값입니다[1]. 조사에 자주 쓰는 값은 아래와 같습니다.

| 값 | 이름 | 뜻 |
|---|---|---|
| 0 | Unknown | 알 수 없음 |
| 7 | Usb | USB |
| 11 | Sata | SATA |
| 12 | Sd | SD |
| 13 | Mmc | MMC |
| 14 | Virtual | 가상 |
| 15 | FileBackedVirtual | 파일 기반 가상 디스크 (VHD 등) |
| 17 | Nvme | NVMe |

표의 이름은 앞의 `BusType` 을 뺀 것이고, 실제 열거 이름은 `BusTypeMaxReserved` 처럼 앞에 `BusType` 이 붙습니다[1]. 표의 값은 C 열거 선언 순서로 센 것이며, 선언에 숫자가 직접 적힌 값은 0x00 과 BusTypeMaxReserved(0x7F) 둘뿐입니다[1].

1006 에는 USB(7) 말고도 NVMe(17), 파일 기반 가상 디스크(15) 같은 BusType 이 함께 남습니다. 그래서 USB 연결은 BusType 이 7 인 이벤트부터 보고, 그다음 SerialNumber·Model 칸으로 장치마다 묶습니다. UASP 장치처럼 USBSTOR 에 남지 않는 저장장치도 있는데, 이런 장치는 [USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md) 허브의 읽는 순서를 따라 따로 확인합니다.

**볼륨 시리얼 번호는 기대하지 않습니다.** 버전 7 에는 이름에 Vbr 이 든 칸이 없습니다. 이 빌드의 공급자 메타데이터에는 1006 이 버전 7 하나뿐이어서, 1006 으로 볼륨 시리얼 번호를 얻지 못합니다. 다른 빌드의 검체는 이벤트 버전부터 확인합니다.

**PartitionCount 0 인 이벤트.** BusType 이 7 인 1006 가운데 PartitionCount 가 0 인 이벤트도 적지 않게 남습니다. 이 이벤트가 연결 때 남는지 해제 때 남는지는 공개된 설명이 없습니다. 이 값 하나로 연결과 해제를 가르지 않고 아래 Kernel-PnP 이벤트와 장치 속성 시각에 맞춰 봅니다.

### Kernel-PnP/Configuration 400·410

`Microsoft-Windows-Kernel-PnP/Configuration` 로그는 이 빌드에서 켜져 있고, 최대 크기는 1MB 이며 순환 방식입니다. 크기가 작아서 가장 오래된 이벤트가 약 3개월 전 것일 수 있고, 오래된 연결은 새 이벤트에 밀려 사라집니다.

| ID | 메시지 틀 | 주로 보는 칸 |
|---|---|---|
| 400 | "Device %1 was configured." | DeviceInstanceId, DriverName, ClassGuid, DriverDate, DriverVersion, DriverProvider, DriverInbox, DriverSection, DriverRank, MatchingDeviceId, OutrankedDrivers, DeviceUpdated, Status, ParentDeviceInstanceId |
| 410 | "Device %1 was started." | DeviceInstanceId, DriverName, ClassGuid, ServiceName, LowerFilters, UpperFilters, Problem, Status |
| 420 | "Device %1 was deleted." | |
| 430 | "Device %1 requires further installation." | |

(메시지 틀과 칸 이름은 공급자 템플릿에 정의된 것입니다.)

410 의 DeviceInstanceId 에 `USBSTOR\Disk&Ven_…&Prod_…&Rev_…\<시리얼>` 모양의 값이 남습니다. 이 값은 USBSTOR 키 경로와 같은 모양이라서 끝의 시리얼 부분으로 USBSTOR 인스턴스와 바로 잇습니다. 같은 연결 때 `STORAGE\Volume\…` 장치의 400·410 도 남습니다.

### DriverFrameworks-UserMode/Operational

이 로그는 꺼져 있을 수 있으므로 검체에서 켜져 있는지부터 봅니다. 2003 의 메시지 틀은 "The UMDF Host Process (%1) has been asked to load drivers for device %2." 이고 칸은 LifetimeId 와 InstanceId 입니다. 로그가 켜져 있다면 InstanceId 칸에서 장치를 찾습니다. 2100·2102 는 PnP·전원 작업을 적는 이벤트이며 칸은 LifetimeId, InstanceId, MajorCode, MinorCode, Argument1~4, Status 입니다.

## 장치 안의 파일을 열었나

연결 기록만으로는 무엇을 했는지 알 수 없습니다. 장치 안의 파일을 연 흔적은 바로가기 파일·점프리스트·셸백에서 찾습니다. 바로가기 파일의 전체 구조는 [바로가기 형식](../../../01-foundations/shell-document-formats/shell-link-lnk.md) 에서 다룹니다. 여기서는 USB 조사에 쓰는 칸만 봅니다.

**볼륨 정보 (Volume Information).** 대상 파일이 있던 볼륨을 적는 부분입니다[2].

| 볼륨 정보 안 오프셋 | 뜻 |
|---|---|
| 0 | 볼륨 정보 크기 |
| 4 | 드라이브 종류 |
| 8 | 드라이브 시리얼 번호 |
| 12 | 볼륨 레이블 위치 |
| 16 | 유니코드 볼륨 레이블 위치 (볼륨 정보 헤더가 16바이트보다 클 때만) |

| 드라이브 종류 값 | 이름 |
|---|---|
| 0 | DRIVE_UNKNOWN |
| 1 | DRIVE_NO_ROOT_DIR |
| 2 | DRIVE_REMOVABLE |
| 3 | DRIVE_FIXED |
| 4 | DRIVE_REMOTE |
| 5 | DRIVE_CDROM |
| 6 | DRIVE_RAMDISK |

드라이브 종류 값 하나로 USB 장치인지 정하지 않고, 드라이브 시리얼 번호를 장치 기록과 맞춰 봅니다. 드라이브 시리얼 번호를 EMDMgmt 의 볼륨 시리얼 번호와 맞추는 방법은 [USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md) 의 "이어 붙이는 열쇠" 표에 있습니다.

**대상 파일의 시각.** 바로가기 파일 헤더는 76바이트입니다[2]. 헤더의 오프셋 28·36·44 에는 대상 파일의 만든 시각·마지막 접근 시각·마지막 수정 시각이 있습니다[2]. 값은 FILETIME 형식의 UTC 이고, 없으면 0 입니다[2].

이 세 시각은 바로가기 파일 자신의 시각이 아니라 장치 안에 있던 대상 파일의 시각입니다. PC 안에 같은 이름의 파일이 있으면 시각을 맞춰 보고, 같은 파일인지 판단하는 재료 가운데 하나로 씁니다.

**분산 링크 추적 (Distributed Link Tracker) 블록.** 서명 0xa0000003, 크기 96바이트인 추가 데이터 블록입니다[2].

| 블록 안 오프셋 | 뜻 |
|---|---|
| 16 | 머신 식별자 문자열 |
| 32 | droid 볼륨 식별자 |
| 48 | droid 파일 식별자 |
| 64 | birth droid 볼륨 식별자 |
| 80 | birth droid 파일 식별자 |

droid 값은 NTFS $OBJECT_ID 의 GUID 입니다[2]. FAT·exFAT 에는 $OBJECT_ID 가 없는데, 장치가 이 파일 시스템일 때 이 블록이 어떻게 남는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 이 블록이 비어 있어도 이상하게 보지 않습니다.

## 분석 흐름

1. 시간대 설정을 읽어 UTC 와 현지 시각의 차이를 정합니다.
2. [USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md) 의 읽는 순서대로 장치 목록표를 만듭니다. 칸은 시리얼 번호, 제조사·제품, 처음 설치·마지막 연결·마지막 해제 시각, 드라이브 문자, 볼륨 시리얼 번호입니다.
3. Partition/Diagnostic 1006 가운데 BusType 이 7 인 이벤트를 뽑아 SerialNumber 로 장치마다 묶습니다.
4. Kernel-PnP/Configuration 410 의 DeviceInstanceId 에서 시리얼을 꺼내 같은 장치의 시각을 더합니다.
5. 2~4 의 시각을 합쳐 장치마다 연결 구간표를 만듭니다. 로그가 밀려나 기록이 없는 기간은 빈칸으로 두고 그렇게 적습니다.
6. 바로가기 파일·점프리스트에서 드라이브 시리얼 번호가 그 장치의 볼륨 시리얼 번호와 같은 항목을 찾습니다. 셸백에서는 그 드라이브 문자로 시작하는 경로를 찾습니다. 찾은 시각이 연결 구간 안에 드는지 확인합니다.
7. 대상 파일의 이름과 시각을 PC 안의 파일과 맞춥니다. 장치 이미지가 있으면 장치 안 파일과 PC 안 파일의 해시를 비교합니다([해시셋 대조와 유사 해시](../../../03-techniques/analysis/hash-set-fuzzy-hash.md)).
8. 파일 접근 감사가 켜져 있었다면 연결 구간 안의 4663 이벤트로 원본 파일에 접근한 계정을 봅니다.
9. 연결 전에 자료를 한 폴더에 모으거나 압축한 흔적이 있는지 [퇴사 전 자료를 모으고 압축했나](staging.md) 를 따라 확인합니다.
10. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리합니다.

## 흔한 오판

1. **연결 기록을 복사 증거로 씁니다.** 연결 기록은 장치가 붙었다는 것만 보여 줍니다. 까닭은 [USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md) 의 "증명하지 못하는 것" 에 있습니다.
2. **원본 파일의 마지막 접근 시각 하나로 복사를 단정합니다.** 윈도에는 "파일을 USB 로 복사했다" 는 전용 기록이 없습니다. 파일에 접근한 기록은 파일 접근 감사를 켜 두었을 때만 4663 으로 남습니다.
3. **BusType 15·17 을 USB 로 봅니다.** 15 는 VHD 같은 파일 기반 가상 디스크이고, 17 은 NVMe 입니다[1]. VHD 를 연결한 기록을 USB 장치로 보고하지 않습니다.
4. **로그에 없으면 연결도 없었다고 봅니다.** Kernel-PnP/Configuration 은 1MB 순환 로그입니다. DriverFrameworks-UserMode 로그는 꺼져 있을 수 있습니다. 이벤트가 없다는 것은 그 기간 기록이 남지 않았다는 뜻일 수 있습니다.
5. **PartitionCount 0 을 해제 기록으로 단정합니다.** 뜻이 공개되지 않은 값입니다. 다른 시각과 맞춰서만 씁니다.
6. **시간대 Bias 를 부호 없이 읽습니다.** Bias 는 REG_DWORD 로 저장되지만 부호 있는 32비트로 읽어야 합니다. UTC+9 는 -540 입니다. 부호 없이 읽으면 4294966756 이 나옵니다.
7. **드라이브 문자 하나로 장치를 잇습니다.** 드라이브 문자는 다른 장치에 다시 쓰입니다. 볼륨 시리얼 번호와 시각을 함께 맞춥니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 USB 메모리로 설계 자료를 가져갔습니다."
- 쓸 문장: "SYSTEM 하이브에 시리얼 번호 ○○ 인 USB 저장장치 기록이 있습니다. Kernel-PnP/Configuration 로그에는 같은 시리얼 번호가 든 410 이벤트가 ○○(UTC) 에 있습니다. 사용자 ○○ 의 바로가기 파일 ○개는 드라이브 시리얼 번호가 이 장치 볼륨의 시리얼 번호와 같습니다. 이 기록은 해당 파일들이 이 장치에 있었고 사용자 ○○ 의 세션에서 열렸음을 보여 줍니다. 파일을 이 PC 에서 장치로 복사했는지는 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md) — 연결 기록의 위치·구조·시각 기준입니다.
- [외부 장치 연결 이벤트](../../../02-artifacts/event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) — Partition/Diagnostic·Kernel-PnP·DriverFrameworks 로그의 구조입니다.
- [바로가기 파일](../../../02-artifacts/file-folder-usage/lnk.md) · [바로가기 형식](../../../01-foundations/shell-document-formats/shell-link-lnk.md) — 볼륨 정보와 추적 블록을 읽는 법입니다.
- [점프리스트](../../../02-artifacts/file-folder-usage/jump-lists.md) · [셸백](../../../02-artifacts/file-folder-usage/shellbags/index.md) — 장치 안 파일과 폴더를 연 흔적입니다.
- [파일 접근 감사](../../../02-artifacts/event-logs/4656-4663-4660.md) · [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) — 4663 이 남는 조건입니다.
- [스마트폰으로 옮겼나 (MTP·Phone Link)](mtp-phone-link.md) — USBSTOR 에 남지 않는 휴대폰 연결입니다.
- [퇴사 전 자료를 모으고 압축했나 (Staging)](staging.md) — 장치로 옮기기 전 단계입니다.
- [이 파일을 누가 언제 열었나](../../activity/file-access.md) — 파일 하나를 중심으로 연 기록을 모읍니다.

## 참고 문헌

1. Microsoft Learn, "STORAGE_BUS_TYPE enumeration (winioctl.h)" — https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ne-winioctl-storage_bus_type
2. libyal liblnk, "Windows Shortcut File (LNK) format" — https://raw.githubusercontent.com/libyal/liblnk/main/documentation/Windows%20Shortcut%20File%20(LNK)%20format.asciidoc
