---
title: "외부 장치 연결 이벤트"
parent: "아티팩트 · 이벤트 로그"
nav_order: 2700
---

# 외부 장치 연결 이벤트 (Partition/Diagnostic·Kernel-PnP·DriverFrameworks)

저장장치를 꽂고 뺄 때 이벤트 로그 여러 곳에 기록이 남습니다. Partition/Diagnostic 로그의 1006 은 꽂을 때와 뺄 때마다 한 건씩 쌓입니다. Kernel-PnP/Configuration 로그의 400·410 은 장치를 처음 구성할 때 남습니다. Kernel-PnP/Device Management 로그의 1010 은 장치가 버스에서 사라졌을 때 남습니다. 메시지 문구는 "예고 없이 빠짐 (surprise removed)" 입니다. DriverFrameworks-UserMode/Operational 로그는 꺼져 있을 수 있습니다. 기록 계정은 모두 SYSTEM 이어서, 누가 꽂았는지는 이 로그로 알 수 없습니다. 시각은 UTC 입니다.

## 무엇을 기록하나 · 왜 생기나

### 세 공급자

| 공급자 | 로그 (채널) | 주로 보는 이벤트 | 남는 때 |
|---|---|---|---|
| Microsoft-Windows-Partition | Microsoft-Windows-Partition/Diagnostic | 1006 | 디스크를 꽂을 때와 뺄 때 |
| Microsoft-Windows-Kernel-PnP | Kernel-PnP/Configuration | 400·410 | 장치를 처음 구성하고 시작할 때 |
| Microsoft-Windows-Kernel-PnP | Kernel-PnP/Device Management | 1010 | 장치가 버스에서 사라졌을 때 (문구는 "surprise removed") |
| Microsoft-Windows-DriverFrameworks-UserMode | DriverFrameworks-UserMode/Operational, System | 2003~2010·2100~2106, 10000·10100 | 사용자 모드 드라이버 프레임워크 (UMDF) 드라이버를 올리거나 설치할 때 |

### Partition/Diagnostic 1006

공급자 GUID 는 `412bdff2-a8c4-470d-8f33-63fe0d8c20e2` 입니다. 공급자 메타데이터에 적힌 1006 의 설명은 "For internal use only." 한 줄이라서, 필드의 뜻은 필드 이름을 보고 다른 기록과 맞춰 확인합니다. 1006 은 USB·VHD 디스크를 꽂거나 뺀 기록입니다[1].

같은 공급자에는 1001 "Operation started.", 1002 "Operation completed.", 1007 "Disk %1 has %2 hidden partitions." 도 있습니다. 1008·1009 는 파티션 오류이고, 5000~5006 은 작업 항목 이름입니다. 실제 로그에는 1006 만 남아 있기도 합니다(Windows 11 25H2 PC 한 대에서 247건).

### Kernel-PnP

공급자 GUID 는 `9c205a39-1250-487d-abd7-e831c6290539` 입니다. 이 공급자는 System, Kernel-PnP/Configuration, Device Management 채널에 쓰고, Boot Diagnostic, Device Enumeration Diagnostic, Configuration Diagnostic, Driver Diagnostic, Driver Watchdog 채널에도 씁니다. Configuration 로그에는 장치를 구성하고(400) 시작하고(410) 지운(420) 기록이 남고, Device Management 로그에는 장치가 버스에서 사라진 기록(1010·1011)이 남습니다.

### DriverFrameworks-UserMode

공급자 GUID 는 `2e35aaeb-857f-4beb-a418-2e6c0e54d988` 입니다. 이 공급자는 DriverFrameworks-UserMode/Operational, Kernel-Power/Diagnostic, System 채널에 씁니다. Operational 로그는 UMDF 호스트가 장치의 드라이버를 올리는 과정과 PnP·전원 요청을 적고, System 채널의 10000·10100 은 UMDF 드라이버 패키지 설치를 적습니다. Operational 로그가 꺼져 있어도 처음 꽂을 때 System 채널에 10000·10100 이 남습니다.

## 위치와 버전별 차이

### 로그 설정

Windows 11 25H2 PC 한 대의 설정입니다.

| 로그 | 파일 | 켜짐 | 최대 크기 | 방식 | 남아 있던 기간 |
|---|---|---|---|---|---|
| Partition/Diagnostic | `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-Partition%4Diagnostic.evtx` | 켜짐 | 16MB | 순환 | OS 설치(2026-06-26 무렵) 뒤 전부, 247건 |
| Kernel-PnP/Configuration | 실제 데이터로 확인 | 켜짐 | 약 1MB | 순환 | OS 설치 뒤 전부, 1,367건 |
| Kernel-PnP/Device Management | 실제 데이터로 확인 | 켜짐 | 5MB | 순환 | 2026-08-18 부터 약 5주, 10,816건 |
| DriverFrameworks-UserMode/Operational | `Microsoft-Windows-DriverFrameworks-UserMode%4Operational.evtx` | 꺼짐 | 1MB | 순환 | 기록 없음 |

- 순환 (Circular) 방식 로그는 가득 차면 오래된 이벤트부터 덮어씁니다.
- Device Management 로그는 크기가 가장 컸지만 남은 기간이 가장 짧았습니다. 이유는 "함정과 한계" 에서 다룹니다.
- Windows 7 에서는 DriverFrameworks-UserMode/Operational 로그가 기본으로 켜져 있었다는 설명이 있습니다. 분석 대상마다 켜져 있는지부터 봅니다.
- 로그 설정 읽는 법은 [감사 정책과 로그 설정](audit-policy-log-settings.md)에서 다룹니다.

### 1006 의 이벤트 버전

| 이벤트 버전 | 출처 | Vbr 필드 |
|---|---|---|
| 4 | EvtxECmd 맵의 첫 번째 예시 (2020년) | 있음 |
| 0 | EvtxECmd 맵의 두 번째 예시 (2022년). EventData 에 "Version" 필드가 따로 있고 값이 3 입니다 | 있음 |
| 7 | Win11 25H2 레코드 | 없음 |

- 맵 예시에는 Vbr0Bytes·Vbr0·Vbr1Bytes·Vbr1·Vbr2Bytes·Vbr2·Vbr3Size·Vbr3 필드가 있었습니다.
- Win11 25H2 의 버전 7 에는 이름에 Vbr 이 든 필드가 없습니다. 어느 빌드에서 빠졌는지는 실제 데이터의 이벤트 버전으로 확인합니다.
- 두 번째 예시는 System 부분의 Version 이 0 인데 EventData 에 Version 필드가 따로 있습니다. 버전을 적는 방식이 바뀐 적이 있는 것으로 보입니다.
- 이 로그에서 볼륨 시리얼 번호 (VSN) 를 꺼내는 방법을 다룬 글이 있습니다[1]. 실제 데이터의 1006 에 Vbr 필드가 있는지부터 봅니다.
- 맵 첫 번째 예시의 공급자 GUID 는 끝자리가 `63fabc8c20e2` 로, 위 GUID(`63fe0d8c20e2`)와 다릅니다. 두 번째 예시는 위 GUID 와 같습니다. 예시를 가리면서 바뀐 것으로 보입니다. GUID 로 거를 때는 공급자 이름도 함께 봅니다.

## 구조

### 1006 에서 보는 필드

| 필드 | 내용 |
|---|---|
| BusType | 버스 종류입니다. 7 은 USB, 15 는 VHD 같은 파일 기반 가상 디스크, 17 은 NVMe 입니다 |
| Capacity | 디스크 용량입니다. 꽂을 때 0 보다 크고 뺄 때 0 입니다 |
| PartitionCount | 파티션 개수입니다. 뺄 때 0 입니다 |
| SerialNumber | SCSI 시리얼 번호 (SCSI SerialNumber) 입니다[1]. USBSTOR 키의 시리얼 번호와 늘 같지는 않습니다 |
| RegistryId | 이 값을 SYSTEM 하이브에서 찾으면 맞는 USBSTOR 키와 시리얼 번호가 나옵니다[1]. USB 장치의 1006 에는 채워져 있습니다 |
| ParentId | 외장 SSD 의 1006 에서는 `USB\VID_…&PID_…\…` 모양의 USB 장치 인스턴스 ID 입니다 |
| UserRemovalPolicy | 꽂을 때 true, 뺄 때 false 입니다 |
| MbrBytes | 꽂을 때 512, 뺄 때 0 입니다 |

- 표의 "꽂을 때·뺄 때" 값은 Windows 11 25H2 기준입니다.
- BusType 값 표는 [USB 로 무엇을 가져갔나](../../04-scenarios/exfiltration/data-exfiltration/usb.md)에서 다룹니다.
- 디스크 구조 필드는 [파티션 구조](../../01-foundations/disk-volume/mbr-gpt.md)를 알고 읽습니다.

### 시리얼 번호 맞추기

두 장치의 1006 SerialNumber 를 장치 인스턴스 ID 와 맞춰 보면 다음과 같습니다.

| 장치 | 장치 인스턴스 ID | 1006 SerialNumber |
|---|---|---|
| USB 메모리 | `USBSTOR\…\<시리얼>` | 20자. USBSTOR 인스턴스 ID 안에 그대로 들어 있었습니다 |
| 외장 SSD (UASP 연결) | `SCSI\DISK&VEN_…&PROD_…\…` | 15자. 장치 인스턴스 ID 와 달랐습니다 |

외장 SSD 는 USBSTOR 아래에 없었는데도 1006 에는 BusType 7(USB)로 남았습니다. 곧 USBSTOR 에 남지 않는 UASP 장치도 1006 에는 USB 연결로 잡힙니다.

- UASP 장치의 레지스트리 흔적은 [USBSTOR 에 안 남는 장치](../external-devices/usb-storage-artifacts/uasp-scsi-sd.md)에서 다룹니다.

### 꽂을 때와 뺄 때가 번갈아 남는다

BusType 이 7 인 1006 은 두 모양이 번갈아 나왔습니다.

| 모양 | Capacity | PartitionCount | UserRemovalPolicy | MbrBytes | 맞는 시각 |
|---|---|---|---|---|---|
| 꽂을 때 | 0 보다 큼 | 실제 데이터로 확인 | true | 512 | 장치 속성의 마지막 연결 시각 |
| 뺄 때 | 0 | 0 | false | 0 | 장치 속성의 마지막 해제 시각 |

한 가지 예외가 있었습니다. 리눅스 USB 가젯은 꽂을 때도 Capacity 가 0 이고 PartitionCount 가 1 이었습니다. 매체가 없는 장치처럼 보였습니다.

> 그림 자리: 한 장치의 1006 을 시간 축에 늘어놓고, Capacity 가 있는 레코드(꽂음)와 Capacity 0·PartitionCount 0 레코드(뺌)가 번갈아 나오는 모습. 마지막 한 쌍 위에 장치 속성의 마지막 연결·해제 시각을 겹쳐 표시

### Kernel-PnP 이벤트 틀

메시지 틀과 필드 이름은 공급자 템플릿의 값입니다.

| 로그 | ID | 메시지 틀 | 필드 |
|---|---|---|---|
| Configuration | 400 | "Device %1 was configured." | DeviceInstanceId, DriverName, ClassGuid, DriverDate, DriverVersion, DriverProvider, DriverInbox, DriverSection, DriverRank, MatchingDeviceId, OutrankedDrivers, DeviceUpdated, Status, ParentDeviceInstanceId. 버전 1 에 DriverPackageId 가 더해집니다 |
| Configuration | 410 | "Device %1 was started." | DeviceInstanceId, DriverName, ClassGuid, ServiceName, LowerFilters, UpperFilters, Problem, Status |
| Configuration | 420 | "Device %1 was deleted." | DeviceInstanceId, ClassGuid, Problem, Status |
| Configuration | 430 | "Device %1 requires further installation." | DeviceInstanceId |
| Configuration | 440 | "Device settings for %1 were migrated from previous OS installation." | DeviceInstanceId, LastDeviceInstanceId, ClassGuid, LocationPath, MigrationRank, Present, Status |
| Configuration | 441·442 | 441 은 설정 옮기기 실패, 442 는 부분·모호 일치여서 옮기지 않음 | 440 과 같습니다 |
| Device Management | 1010 | "Device %1 has been surprise removed as it is reported as missing on the bus." | DeviceInstanceId, DeviceCount |
| Device Management | 1011 | "Device %1 has been surprise removed as it was reported to be failing." | DeviceInstanceId, DeviceCount |

- Windows 11 25H2 PC 한 대의 Configuration 로그에는 400(502건), 410(442건), 440(193건), 430(86건), 420(72건), 442(58건), 411(9건), 403(4건), 412(1건)가 있었습니다.
- Device Management 로그는 10,816건 가운데 10,814건이 1010 이었습니다.

### 처음 꽂았을 때 남는 순서

리눅스 USB 가젯을 처음 꽂았을 때(2026-09-15T05:51:35Z) Configuration 로그에 남은 순서입니다. 모두 1초 안에 남았습니다.

1. `USB\VID_…&PID_…\…` — 400·410
2. 인터페이스 `…&MI_00` ~ `…&MI_07` — 400·430
3. `USBSTOR\Disk&Ven_Linux&Prod_File-Stor_Gadget&Rev_0504\…` — 400·410
4. `STORAGE\Volume\…` — 400·410
5. `SWD\WPDBUSENUM\…` — 430

같은 1~2초 안에 System 로그에도 아래 이벤트가 남았습니다.

- Service Control Manager 7045
- DriverFrameworks-UserMode 10000·10002·10100
- UserPnp 20003
- WPDClassInstaller 24576·24577·24579

연결·해제 때 남는 Kernel-PnP 레코드와 1006 의 기록 계정 (System 의 Security UserID) 은 `S-1-5-18`(SYSTEM) 입니다.

### DriverFrameworks-UserMode 이벤트 틀

메시지 틀과 필드 이름은 공급자 템플릿의 값입니다.

| 채널 | ID | 메시지 틀 (줄임) | 필드 |
|---|---|---|---|
| Operational | 2003 | "The UMDF Host Process (%1) has been asked to load drivers for device %2." | LifetimeId, InstanceId |
| Operational | 2004 | "The UMDF Host is loading driver %4 at level %3 for device %2." | LifetimeId, InstanceId, Level, Service, ClsId |
| Operational | 2005 | "… has loaded module %3 while loading drivers for device %2." | LifetimeId, InstanceId, ModulePath, CompanyName, FileDescription, FileVersion |
| Operational | 2010 | "… has successfully loaded drivers for device %2." | LifetimeId, InstanceId, FinalStatus |
| Operational | 2100 | "Received a Pnp or Power operation (%3, %4) for device %2." | LifetimeId, InstanceId, MajorCode, MinorCode, Argument1~4, Status |
| Operational | 2101·2102·2105·2106 | PnP·전원 요청을 마쳤거나(2101), 아래 드라이버로 넘겼거나(2102·2105), 아래 드라이버가 마친(2106) 기록 | 2100 과 같습니다 |
| System | 10000 | "A driver package which uses user-mode driver framework version %2 is being installed on device %1." | DeviceId, FrameworkVersion |
| System | 10001·10002 | UMDF 서비스 설치·업그레이드 | |
| System | 10100 | "The driver package installation has succeeded." | FinalStatus |
| System | 10110·10111 | 사용자 모드 드라이버 충돌 | |

- Operational 채널 템플릿은 버전 1 입니다.
- 장치를 뽑은 요청을 2100·2102 의 MinorCode 값으로 가를 수 있다는 설명이 있습니다. 값마다의 뜻은 실제 데이터로 확인합니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 기록된 시각에 이 버스 종류·시리얼 번호의 디스크가 나타났거나 사라졌습니다 (1006) | 누가 꽂았는지. 기록 계정은 SYSTEM 입니다 |
| 한 장치를 여러 번 꽂고 뺀 이력. 1006 은 꽂고 뺄 때마다 쌓입니다 | 장치 안의 파일을 열거나 복사했다는 것 |
| 이 장치를 이 PC 에서 처음 구성하고 시작한 시각 (400·410) | 400·410 이 없으니 그 시각에 연결이 없었다는 것. 다시 꽂을 때는 남지 않습니다 |
| 장치가 버스에서 사라진 시각 (1010) | Capacity 0 인 1006 이 모두 뺀 기록이라는 것 |
| USBSTOR 에 없는 UASP 장치도 USB 로 연결됐다는 것 (1006 의 BusType 7) | "안전하게 제거" 로 뺐는지. 그때 1010 이 남는지는 알려져 있지 않습니다 |

### 보고서 문장

아래 시각과 시리얼 번호는 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "Partition/Diagnostic 로그에는 <시각> UTC 에 BusType 7, SerialNumber ○○ 인 디스크의 1006 이 있습니다. <시각> UTC 에는 같은 SerialNumber 에 Capacity 0, PartitionCount 0 인 1006 이 있습니다. 두 시각은 이 장치의 장치 속성에 적힌 마지막 연결·해제 시각과 1초 안팎으로 맞습니다."
- 쓰면 안 되는 문장: "사용자 ○○ 이 USB 메모리를 꽂아 파일을 옮겼다."

두 번째 문장은 사람과 행위를 단정합니다. 이 로그에는 장치와 시각만 있습니다.

## 시각 해석

- 이 페이지의 이벤트 시각은 모두 `<TimeCreated SystemTime>` 에 들어 있습니다. 끝에 Z 가 붙은 UTC 값입니다.
- 현지 시각으로 바꿀 때는 조사 대상 PC 의 [시간대 설정](../system-account/time-zone.md)을 씁니다.

### 장치 속성 시각과 맞춰 보기

장치 속성의 마지막 연결·해제 시각(DEVPKEY_Device_LastArrivalDate·LastRemovalDate, 레지스트리 속성 0066·0067)과 1006 시각을 맞춰 보면 다음과 같습니다(Windows 11 25H2).

| 장치 | 동작 | 장치 속성 시각 | 1006 시각 | 1006 모양 |
|---|---|---|---|---|
| 외장 SSD | 꽂음 | 2026-08-31T02:40:29.732Z | 02:40:29.824Z | Capacity 있음 |
| 외장 SSD | 뺌 | 2026-09-01T22:11:53.232Z | 22:11:52.218Z | Capacity 0 |
| 리눅스 USB 가젯 | 꽂음 | 2026-09-15T05:51:35.932Z | 05:51:35.947Z | Capacity 0, PartitionCount 1 |
| 리눅스 USB 가젯 | 뺌 | 2026-09-15T05:51:55.578Z | 05:51:55.575Z | Capacity 0 |

네 쌍 모두 1초 안팎으로 맞습니다. Capacity 0·PartitionCount 0 인 1006 은 장치를 뺀 시각과 맞습니다(Windows 11 25H2 기준).

장치 속성은 마지막 한 번만 남기는데 1006 은 꽂고 뺄 때마다 쌓입니다. 외장 SSD 한 대에 1006 이 189건 쌓인 예처럼, 여러 번 꽂은 이력은 1006 이 더 자세합니다.

- 장치 속성 읽는 법은 [연결·해제 시각](../external-devices/usb-storage-artifacts/deviceclasses-device-properties-0064-0066-0067.md)에서 다룹니다.

### Kernel-PnP 시각이 뜻하는 것

- 이미 설치된 외장 SSD 를 다시 꽂았을 때(2026-08-31T02:39~02:41Z) Configuration 로그에는 400·410 이 하나도 없었습니다. 같은 시간대의 1006 은 남았습니다.
- 곧 400·410 의 시각은 "처음 구성한 시각" 입니다. 다시 꽂은 시각은 1006 에서 찾습니다.
- 리눅스 USB 가젯을 뺄 때(05:51:55Z)는 Configuration 로그에 기록이 없었습니다. Device Management 로그에 1010 이 `USB\VID_…&PID_…\…` 과 `STORAGE\Volume\…` 으로 남았습니다.
- 외장 SSD 를 뺄 때(2026-09-01T22:11:52Z)도 1010 이 그 SSD 의 USB 장치와 `STORAGE\Volume\…` 으로 남았습니다. 시각은 뺄 때의 1006 과 같았습니다.

## 함정과 한계

1. **Capacity 0 인 1006 을 곧바로 "뺌" 으로 읽습니다.** 리눅스 USB 가젯은 꽂을 때도 Capacity 0 이었습니다. PartitionCount 와 앞뒤 레코드, 장치 속성 시각을 함께 봅니다.
2. **1006 의 SerialNumber 를 USBSTOR 시리얼 번호와 그대로 맞춥니다.** 이 값은 SCSI 시리얼 번호여서 다를 수 있습니다[1]. UASP 외장 SSD 에서는 실제로 달랐습니다. 맞지 않으면 RegistryId 로 SYSTEM 하이브의 장치를 찾습니다.
3. **USBSTOR 에 없으니 USB 저장장치가 아니었다고 봅니다.** UASP 외장 SSD 는 `SCSI\…` 인스턴스였지만 1006 에는 BusType 7 로 남았습니다.
4. **400·410 으로 연결 횟수를 셉니다.** 400·410 은 처음 구성할 때 남습니다. 다시 꽂은 기록은 1006 에 있습니다.
5. **Device Management 로그가 오래 남는다고 봅니다.** 블루투스 HID 장치(`HID\{00001812-…}` 같은 장치)가 1010 을 계속 남기면 5MB 로그에 약 5주치만 남기도 합니다. USB 를 뺀 1010 은 빨리 밀려납니다.
6. **Configuration 로그가 오래 남는다고 봅니다.** 최대 크기가 약 1MB 입니다. OS 를 설치한 지 석 달쯤 된 PC 에서는 설치 뒤 기록이 다 남아 있었지만, 오래 쓴 PC 에서는 밀려났을 수 있습니다.
7. **DriverFrameworks-UserMode/Operational 에 기록이 없으니 연결도 없었다고 봅니다.** 이 로그는 꺼져 있을 수 있습니다. 꺼져 있어도 System 채널에 10000·10100 이 남습니다.
8. **BusType 15·17 을 USB 로 봅니다.** 15 는 VHD 같은 파일 기반 가상 디스크이고, 17 은 NVMe 입니다.
9. **1010 을 "안전하게 제거하지 않은 증거" 로 단정합니다.** 메시지 문구("surprise removed")는 예고 없이 뽑은 경우를 가리킵니다. 그러나 안전하게 제거했을 때 1010 이 남는지는 알려져 있지 않으므로 실습 3번으로 확인합니다.
10. **기록 계정을 사용자로 읽습니다.** 1006 과 Kernel-PnP 레코드의 기록 계정은 SYSTEM 입니다. 사람은 로그온 기록과 장치 안 파일을 연 흔적으로 따로 찾습니다.

### 지우기와 조작

- **로그를 지웁니다.** 지운 기록은 [이벤트 로그 삭제](1102-104.md)에서 찾습니다.
- **로그를 끄거나 크기를 줄입니다.** 로그 설정이 분석 대상에서 어떤 상태였는지는 [감사 정책과 로그 설정](audit-policy-log-settings.md)에서 봅니다.
- 조작이 없어도 순환 로그는 스스로 밀려납니다. 기록이 없는 기간은 "연결 없음" 이 아니라 "기록 없음" 으로 적습니다.

## 직접 분석해 보기

### 헥스로 한 번

로그 파일 안의 문자열은 UTF-16LE 로 들어 있습니다. 그래서 장치 인스턴스 ID 조각을 UTF-16LE 바이트로 바꿔 파일 전체를 찾을 수 있습니다. 도구가 레코드로 읽어 주지 않는 자리에 남은 조각도 이렇게 찾습니다.

아래는 문자열을 형식대로 옮긴 예시입니다. 실제 데이터에서 뽑은 바이트가 아닙니다.

```
"USBSTOR"  →  55 00 53 00 42 00 53 00 54 00 4F 00 52 00
```

1. Kernel-PnP/Configuration 로그 파일의 사본을 헥스 편집기로 엽니다.
2. 위 바이트 열을 찾습니다.
3. 찾은 자리의 앞뒤를 읽어 `USBSTOR\Disk&Ven_…&Prod_…&Rev_…\<시리얼>` 전체를 확인합니다.
4. 같은 시리얼 번호를 UTF-16LE 로 바꿔 Partition/Diagnostic 로그 사본에서도 찾습니다.
5. 도구 결과에 없는 자리에서 나왔다면, [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 설명하는 구조로 그 자리가 레코드인지 확인합니다.

인코딩 자체는 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)에서 다룹니다.

### 공개 도구로 한 번

Windows 에 들어 있는 PowerShell 로 1006 사본에서 USB 연결만 뽑아 늘어놓을 수 있습니다.

```powershell
Get-WinEvent -Path '.\Microsoft-Windows-Partition%4Diagnostic.evtx' -FilterXPath "*[System[(EventID=1006)]]" -Oldest |
  ForEach-Object {
    $d = @{}
    ([xml]$_.ToXml()).Event.EventData.Data | ForEach-Object { $d[$_.Name] = $_.'#text' }
    if ($d['BusType'] -eq '7') {
      [pscustomobject]@{
        TimeUtc        = $_.TimeCreated.ToUniversalTime()
        Capacity       = $d['Capacity']
        PartitionCount = $d['PartitionCount']
        SerialNumber   = $d['SerialNumber']
        RegistryId     = $d['RegistryId']
        ParentId       = $d['ParentId']
      }
    }
  } | Format-Table
```

- 결과를 SerialNumber 로 묶으면 장치마다 꽂고 뺀 이력이 나옵니다.
- 같은 방법으로 Kernel-PnP 로그에서 400·410·1010 을 뽑아 DeviceInstanceId 를 봅니다.
- EvtxECmd 맵 저장소에는 Partition/Diagnostic 1006, Kernel-PnP/Configuration 400·410·430, DriverFrameworks-UserMode/Operational 2100, System 의 DriverFrameworks-UserMode 10000 맵이 있습니다. 도구가 뽑은 필드는 XML 원문 한두 건과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 무엇을 맞춰 보나 | 링크 |
|---|---|---|
| USBSTOR·장치 속성 | 시리얼 번호, 처음·마지막 연결 시각, UASP 장치 | [USB 저장장치 흔적](../external-devices/usb-storage-artifacts/index.md) |
| 서비스 설치 이벤트 | 처음 꽂을 때 함께 남은 7045 | [서비스 설치](7045-4697.md) |
| 파티션 구조 | MbrBytes 가 가리키는 디스크 첫머리 | [파티션 구조](../../01-foundations/disk-volume/mbr-gpt.md) |
| 가상 디스크 | BusType 15 기록의 대상 파일 | [증거 이미지·가상 디스크 형식](../../01-foundations/disk-volume/e01-raw-aff4-vhdx-vmdk.md) |
| 블루투스 장치 | Device Management 로그를 채운 블루투스 장치 | [블루투스 장치](../external-devices/bthport.md) |
| 바로가기 파일 | 장치 안의 파일을 열었는지 | [바로가기 파일](../file-folder-usage/lnk.md) |
| 로그온 기록 | 그 시각에 로그온해 있던 사용자 | [로그온·로그오프](logon-events/index.md) |

합쳐 읽는 순서는 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md)와 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)에서 다룹니다.

## 실습

직접 만든 Windows 10·11 가상 머신에 USB 저장장치를 연결해 봅니다. 각 단계의 시각을 UTC 로 적어 둡니다.

1. 처음 보는 USB 메모리를 꽂습니다. Configuration 로그의 400·410 과 1006 이 몇 초 안에 남는지 보십시오.
2. 같은 장치를 뽑고 다시 꽂습니다. 400·410 이 다시 남는지, 1006 만 남는지 보십시오.
3. 한 번은 "안전하게 제거" 로 빼고, 한 번은 그냥 뽑습니다. Device Management 1010 이 두 경우 모두 남는지 비교하십시오. 함정 9번의 답이 여기서 나옵니다.
4. 뺄 때의 1006 에서 Capacity 와 PartitionCount 를 확인하십시오. 장치 속성의 마지막 해제 시각과 몇 초 차이인지 재어 보십시오.
5. VHD 파일을 연결해 봅니다. 1006 의 BusType 이 무엇으로 남는지 보십시오.
6. 1006 의 이벤트 버전과 Vbr 필드가 있는지 확인하십시오. 다른 빌드의 가상 머신과 비교하면 버전 표를 채울 수 있습니다.

NIST CFReDS 같은 공개 시험 데이터에서 이벤트 로그를 꺼냈다면, 먼저 Partition/Diagnostic 로그가 있는지와 1006 의 이벤트 버전을 보십시오. 그다음 USBSTOR 의 시리얼 번호가 1006 SerialNumber 에 그대로 들어 있는지 확인하십시오.

## 참고 문헌

- Eric Zimmerman evtx (EvtxECmd) 맵, "Microsoft-Windows-Partition-Diagnostic_Microsoft-Windows-Partition_1006.map" (작성 Mark Hallman 외) — https://raw.githubusercontent.com/EricZimmerman/evtx/master/evtx/Maps/Microsoft-Windows-Partition-Diagnostic_Microsoft-Windows-Partition_1006.map
- GitHub API, EricZimmerman/evtx 저장소 evtx/Maps 폴더 파일 목록 (맵 파일 이름만 확인) — https://api.github.com/repos/EricZimmerman/evtx/contents/evtx/Maps
