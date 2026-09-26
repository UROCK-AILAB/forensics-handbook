---
title: "USB 저장장치 목록"
parent: "USB 저장장치 흔적"
grand_parent: "아티팩트 · 외부 장치"
nav_order: 1480
---

# USB 저장장치 목록 (USBSTOR)

> 상위 허브: [USB 저장장치 흔적 (USB Storage Artifacts)](index.md)

SYSTEM 하이브의 `Enum\USBSTOR` 키에는 USB 대용량 저장장치 드라이버로 붙은 저장장치가 하나씩 남습니다. 키 이름에서 장치 종류·제조사·제품·리비전 문자열과 인스턴스 ID (Instance ID) 를 읽습니다. 이 키의 값만으로는 언제, 누가 꽂았는지 알 수 없습니다.

## 무엇을 기록하나 · 왜 생기나

USB 장치가 대용량 저장장치 부류이면 Windows 는 USB 저장 포트 드라이버 `Usbstor.sys` 를 올립니다. Windows 2000 부터 들어 있는 드라이버입니다. `Usbstor.sys` 는 장치 안의 논리 장치 (Logical Unit) 마다 물리 장치 객체 (PDO) 를 하나씩 만들며, 논리 장치는 16개까지입니다. 슬롯이 두 개인 카드 리더라면 PDO 가 슬롯마다 하나씩 생깁니다.

이 PDO 의 식별 문자열은 장치가 SCSI 조회 명령 (INQUIRY) 에 답한 데이터로 만듭니다. 플러그 앤 플레이 관리자 (PnP Manager) 는 장치마다 `Enum` 아래에 키를 만들고 이 정보를 적습니다. 장치를 뺀 뒤에도 키는 남지만, Windows 8.1 이후는 오래 안 보인 장치의 키를 스스로 지웁니다(아래 "함정과 한계").

`Enum` 트리는 운영체제 부품만 쓰는 곳이고 트리의 배치도 바뀔 수 있습니다. 그래서 키 이름과 값의 해석은 드라이버 문서와 실제 기록에 기댑니다. USB 3 의 UASP 로 붙는 장치는 이 키에 남지 않습니다. → [USBSTOR 에 안 남는 장치](uasp-scsi-sd.md)

## 위치와 버전별 차이

| 항목 | 경로 |
|---|---|
| 하이브 파일 | `%SystemRoot%\System32\config\SYSTEM` (같은 폴더의 `SYSTEM.LOG1`·`SYSTEM.LOG2` 도 함께 수집) |
| 키 | `ControlSet00X\Enum\USBSTOR\<장치 항목>\<인스턴스>` |
| 실행 중인 시스템 | `HKLM\SYSTEM\CurrentControlSet\Enum\USBSTOR` |

이미지에서 꺼낸 하이브에는 `CurrentControlSet` 이 없습니다. 어느 컨트롤셋을 볼지는 [컨트롤셋 고르기](../../../01-foundations/database-log-formats/registry-hive/controlset-select.md)에서 다룹니다. 하이브 파일은 [하이브 파일 종류와 위치](../../../01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md)를 봅니다.

| Windows | USBSTOR 와 관련해 달라지는 점 | 근거 |
|---|---|---|
| 2000 이후 | `Usbstor.sys` 가 USB 대용량 저장장치를 기본으로 지원합니다. | Microsoft Learn |
| 7 | 인스턴스 키의 `Properties` 에 설치 시각(0064)과 처음 설치 시각(0065)이 있습니다. | Khatri (2013) |
| 8 | 마지막 연결(0066)·마지막 해제(0067) 시각이 더해졌습니다. | Khatri (2013) |
| 8.1·10 | 예약 작업 "Plug and Play Cleanup" 이 30일 넘게 안 보인 장치의 키를 지웁니다. | Cowen (2017) |
| 11 | 같은 정리를 저장소 센스 (Storage Sense) 가 `cleanmgr.exe /autocleanstoragesense` 로 돌립니다. 로그에는 기본 기준이 30일로 적힙니다. 앞의 예약 작업은 없습니다. |  |

## 구조

### 두 단계 키

`USBSTOR` 아래에는 장치 항목 키 (Device Class ID) 가 있습니다. 그 아래에 인스턴스 키가 있습니다.

```
Enum\USBSTOR
 └─ Disk&Ven_SanDisk&Prod_U3_Cruzer_Micro&Rev_3.27      ← 장치 항목 키 (종류·제조사·제품·리비전)
     └─ 0000161511737EFB&0                               ← 인스턴스 키
         ├─ (값) FriendlyName, ContainerID, HardwareID …
         ├─ Device Parameters
         └─ Properties
```

같은 모델의 장치를 여러 개 꽂으면 장치 항목 키 하나 아래에 인스턴스 키가 여러 개 생깁니다.

> 그림 자리: `Enum\USBSTOR` 의 장치 항목 키·인스턴스 키와, 같은 `ContainerID` 로 이어지는 `Enum\USB` 키·AmCache 장치 항목·MountedDevices 값을 선으로 잇는 그림

### 장치 항목 키 이름

키 이름은 `<종류>&Ven_<제조사>&Prod_<제품>&Rev_<리비전>` 형식입니다. 네 필드는 장치가 SCSI 조회 명령에 답한 문자열입니다. 종류 필드에 들어가는 말은 아래와 같습니다.

| SCSI 장치 유형 코드 | 종류 필드 | 일반 이름 (Generic Type) |
|---|---|---|
| 0 (직접 접근 장치) | `Disk` 또는 `SFloppy` | `GenDisk` 또는 `GenSFloppy` |
| 1 (순차 접근 장치) | `Sequential` | `GenSequential` |
| 4 (한 번 쓰기 장치) | `Worm` | `GenWorm` |
| 5 (읽기 전용 직접 접근 장치) | `CdRom` | `GenCdRom` |
| 7 (광학 장치) | `Optical` | `GenOptical` |
| 8 (매체 교환 장치) | `Changer` | `GenChanger` |
| 그 밖의 값 | `Other` | `UsbstorOther` |

하드웨어 ID 는 필드 사이에 구분자 없이 고정 길이로 붙여 씁니다. 제조사는 8자, 제품은 16자, 리비전은 4자입니다. 공백 같은 특수 문자는 밑줄로 바꿉니다. 제품 문자열이 `U3 Cruzer Micro` 라고 가정하고 위 예를 이 규칙으로 쓰면 `USBSTOR\DiskSanDisk_U3_Cruzer_Micro_3.27` 입니다.

키 이름은 이 형식과 다릅니다. 키 이름에는 `&Ven_`·`&Prod_`·`&Rev_` 구분자가 있고 필드 끝을 채운 밑줄은 없습니다. 같은 인스턴스 키의 `HardwareID` 값 첫 줄은 위의 고정 길이 형식입니다.

이 문자열은 장치가 스스로 알린 값입니다. 상표 이름과 다를 수 있습니다. 제조사 필드에 `USB` 라고 적고 상표와 모델은 제품 필드에 적는 USB 메모리도 있습니다. 실제 제조사는 [USB 장치 식별자 (Enum\USB VID·PID)](enum-usb-vid-pid.md)의 VID 로 다시 확인합니다.

### 인스턴스 키 이름

인스턴스 ID 는 버스 드라이버가 알려 주는 문자열이고, 버스가 지원하면 일련번호를 담고 아니면 위치 정보를 담습니다. 장치 능력의 UniqueID 가 참이면 버스가 준 문자열을 그대로 쓰고, 거짓이면 PnP 관리자가 문자열을 고쳐서 이 PC 안에서만 겹치지 않게 만듭니다. 인스턴스 ID 는 재시작해도 바뀌지 않습니다.

분석에서 널리 쓰는 규칙이 하나 있습니다. 인스턴스 키 이름의 둘째 글자가 `&` 이면 시스템이 만든 이름입니다. Forensics Wiki 는 이때 장치에 일련번호가 없었다고 설명합니다.

Windows 11 빌드 26200 에서 두 장치는 이렇게 남았습니다.

| 장치 | `Capabilities` 값 | `Enum\USB` 쪽 인스턴스 키 | USBSTOR 인스턴스 키 |
|---|---|---|---|
| 일반 USB 메모리 | 0x10 | 일련번호 120자 | 그 일련번호의 앞 63자. 끝에 `&0` 이 없었습니다. |
| 리눅스 기반 기기의 복합 장치 (Composite Device) | 0 | 일련번호 15자 | `<저장 인터페이스 키의 ParentIdPrefix>&<그 일련번호>&0`. 둘째 글자가 `&` 였습니다. |

`Capabilities` 값은 장치 능력 플래그 (`CM_DEVCAP_*`) 이고 `cfgmgr32.h` 에서 0x10 은 UniqueID 입니다. 두 장치 모두 레지스트리 값과 PnP API 가 돌려준 값이 같았습니다.

둘째 장치는 일련번호가 있었는데도 UniqueID 가 꺼져 있었고, 이름은 둘째 글자가 `&` 인 모양이었습니다. 앞의 인스턴스 ID 설명과 맞습니다. 그러므로 `&` 형 이름은 "일련번호가 없다" 보다 "이 PC 의 PnP 관리자가 만든 이름" 으로 읽습니다. 이름 안에 일련번호가 섞여 있을 수 있고, 이런 이름은 다른 PC 에서 같은 장치를 꽂았을 때 같게 나온다는 보장이 없습니다.

첫째 장치처럼 긴 일련번호는 잘릴 수 있으므로 `Enum\USB` 쪽과 맞출 때는 앞부분이 같은지, `ContainerID` 가 같은지를 봅니다.

끝의 `&0` 은 논리 장치 번호로 보는 해석이 널리 쓰이지만 공식 문서에는 설명이 없습니다. 위 표처럼 `&0` 이 붙지 않은 이름도 있습니다.

일련번호는 장치가 Windows 에 알려 준 값입니다. 장치 겉에 인쇄된 번호와 다를 수 있습니다. 보고서와 압수 요청서에는 "Windows 에 보고된 일련번호" 라고 적습니다.

### 주요 값

인스턴스 키에는 값 12개가 있습니다. 아래 표에 없는 값은 `Driver`·`ConfigFlags`·`Address` 입니다. `ContainerID` 밖의 값은 `SetupDiGetDeviceRegistryProperty` 의 같은 이름 속성과 뜻이 같습니다.

| 값 | 뜻 | 분석에 쓰는 곳 |
|---|---|---|
| `FriendlyName` | 장치 표시 이름 | 제조사·제품 문자열 뒤에 ` USB Device` 가 붙은 형식입니다. |
| `HardwareID`·`CompatibleIDs` | 하드웨어 ID 목록, 호환 ID 목록 (REG_MULTI_SZ) | 호환 ID 는 `USBSTOR\Disk`·`USBSTOR\RAW`·`GenDisk` 입니다. |
| `ContainerID` | 한 물리 장치에서 나온 장치 노드를 묶는 GUID | `Enum\USB`·AmCache·휴대용 장치 기록과 같은 PC 안에서 잇습니다. |
| `ClassGUID` | 장치 설치 클래스 GUID | 디스크는 `{4d36e967-e325-11ce-bfc1-08002be10318}` 입니다. |
| `Service` | 장치에 붙은 서비스 이름 | 디스크는 `disk` 입니다. |
| `Mfg`·`DeviceDesc` | 제조사, 장치 설명 | INF 의 일반 문자열("Standard disk drives", "Disk drive")입니다. 실제 제조사가 아닙니다. |
| `Capabilities` | 장치 능력 플래그 | 0x10(UniqueID)이 켜져 있으면 버스가 준 인스턴스 ID 를 그대로 씁니다. |

Forensics Wiki 는 인스턴스 키의 `ParentIdPrefix` 값으로 MountedDevices 와 잇는 방법을 설명하지만, Windows 11 의 USBSTOR 인스턴스 키에는 이 값이 없고 복합 장치의 저장 인터페이스 키(`Enum\USB\...&MI_xx`)에 있습니다. 잇는 방법은 [드라이브 문자 매핑 (MountedDevices)](mounteddevices.md)에서 다룹니다.

### 하위 키

| 하위 키 | 내용 |
|---|---|
| `Device Parameters` | 아래에 `MediaChangeNotification` 과 `Partmgr` 가 있습니다. `Partmgr` 에는 `DiskId`(GUID 문자열)·`Attributes`·`PartitionTableCache` 같은 값이 있습니다. 이 값들의 뜻은 공개된 명세가 없습니다. |
| `Properties` | 장치 속성입니다. `{83da6326-97a6-4088-9453-a1923f573b29}` 아래 `0064`~`0067` 에 설치·연결·해제 시각이 있습니다. `devpkey.h` 에서 `{540b947e-8b40-45bc-a8a2-6a0b894cbda2}` 의 4번 속성은 버스가 알린 장치 설명(`DEVPKEY_Device_BusReportedDeviceDesc`)입니다. 한 공개 플러그인은 `...\0004` 에서 장치 이름을 읽습니다. |

시각 속성 읽는 법은 [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md)에서 다룹니다.

실행 중인 시스템에서는 관리자 권한으로도 `Properties` 키를 열면 접근이 거부됩니다. 하위 키 이름은 보입니다. 하이브 사본을 떠서 읽으면 키 권한과 관계없이 읽힙니다.

## 증거로서 의미

### 증명하는 것

- 이 장치 항목 문자열과 인스턴스 ID 로 등록된 저장장치가 이 PC 에 USB 대용량 저장장치로 설치된 적이 있습니다.
- 장치를 특정할 단서가 남습니다. 종류·제조사·제품·리비전 문자열과 Windows 에 보고된 일련번호입니다.
- 인스턴스 이름이 일련번호 형식이면 다른 PC 의 기록이나 압수한 장치와 맞춰 볼 수 있습니다.
- `ContainerID` 로 같은 PC 안의 다른 장치 기록과 이을 수 있습니다.

### 증명하지 못하는 것

- 누가 꽂았는지 알 수 없습니다. SYSTEM 하이브는 사용자별 파일이 아닙니다. 사용자는 [사용자별 장치 연결 (MountPoints2)](mountpoints2.md)로 좁힙니다.
- 주요 값에는 시각이 없습니다. 시각은 `Properties` 와 다른 흔적에서 얻습니다.
- 몇 번 꽂았는지 알 수 없습니다.
- 장치에 파일을 복사했는지, 장치의 파일을 열었는지 알 수 없습니다.
- 어느 드라이브 문자로 붙었는지 알 수 없습니다.
- `&` 형 이름은 같은 모델의 다른 장치와 구별하기 어렵습니다. 다른 PC 의 기록과 같은 장치라는 근거로도 쓰기 어렵습니다.
- 키가 없다고 연결한 적이 없다는 뜻은 아닙니다. Windows 가 스스로 지웠거나, UASP 로 붙었거나, 누군가 지웠을 수 있습니다.

### 보고서 문장 예

- 쓰지 않을 문장: "피의자가 이 USB 메모리로 파일을 가져갔다."
- 쓸 문장: "SYSTEM 하이브 `ControlSet001\Enum\USBSTOR` 에 `Disk&Ven_○○&Prod_○○&Rev_○○` 장치 항목이 있고, 그 아래 인스턴스 ID 가 `○○○&0` 인 키가 있다. 이 기록은 Windows 에 일련번호 `○○○` 로 보고된 USB 저장장치가 이 PC 에 설치된 적이 있음을 보여 준다. 연결 시각과 사용자는 이 키만으로 정할 수 없다."

## 시각 해석

USBSTOR 의 주요 값에는 시각이 없습니다. 시각은 두 곳에서 얻습니다.

| 시각 | 무엇이 바뀔 때 바뀌나 | 기준 |
|---|---|---|
| `Properties` 의 `0064`~`0067` 값 | 설치·처음 설치·마지막 연결·마지막 해제 때 | FILETIME, UTC. 자세한 내용은 [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md) |
| 인스턴스 키의 마지막 기록 시각 | 이 키의 값이 바뀌거나 하위 키가 생기고 지워질 때 | UTC |
| 장치 항목 키의 마지막 기록 시각 | 아래에 인스턴스 키가 새로 생기거나 지워질 때. 같은 모델의 다른 장치를 처음 꽂은 때가 한 예입니다. | UTC |
| `USBSTOR` 키의 마지막 기록 시각 | 아래에 장치 항목 키가 새로 생기거나 지워질 때 | UTC |

키 시각이 무엇에 따라 바뀌는지는 [키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md)에서 다룹니다.

2009년 글(Cowen)은 장치 항목 키의 마지막 기록 시각을 마지막 연결 시각으로 설명했습니다. 한 번만 꽂은 장치에서는 인스턴스 키 시각이 속성의 설치 시각·마지막 연결 시각과 같고, PC 를 다시 켜도 키 시각은 바뀌지 않습니다. 여러 번 꽂은 장치에서 키 시각이 무엇을 따라가는지 설명한 공개 문서는 없습니다. 그래서 연결 시각은 속성 값, [외부 장치 연결 이벤트](../../event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md), [장치 설치 로그](setupapi-dev-log.md)로 정합니다. 키 시각은 이 값들과 맞는지 보는 데만 씁니다.
- Windows 8.1 이후는 바뀐 내용을 트랜잭션 로그에 먼저 씁니다. 하이브 파일만 보면 최근 연결이 빠질 수 있습니다. → [.LOG1·.LOG2](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md)

## 함정과 한계

1. **Windows 가 스스로 지웁니다.** Windows 8.1·10 에서는 30일 넘게 안 보인 장치의 키가 지워집니다. 지운 기록은 `setupapi.dev.log` 에 남습니다. Windows 11 에서는 한 번의 정리로 장치 16개가 지워진 예가 있습니다. 로그에서 이 정리는 `[Device and Driver Disk Cleanup Handler - {GUID}]` 구역으로 시작하고, 그 안에 장치마다 "`Device <장치 인스턴스 ID> was removed.`" 줄이 있습니다. 키가 없을 때는 사용자가 지운 것인지 Windows 가 지운 것인지부터 확인합니다.
2. **UASP 장치는 USBSTOR 에 없습니다.** → [USBSTOR 에 안 남는 장치](uasp-scsi-sd.md)
3. **이름이 `Enum\USB` 쪽 일련번호와 똑같지 않을 수 있습니다.** 일련번호가 잘리거나 앞에 다른 문자열이 붙습니다(위 "인스턴스 키 이름").
4. **제조사 필드와 `Mfg` 값으로 제조사를 정하지 않습니다.** 제조사 필드는 장치가 알린 문자열입니다. `Mfg` 는 드라이버 INF 의 일반 문자열입니다.
5. **도구마다 시각 열이 다릅니다.** 한 공개 플러그인(RegistryPlugin.USBSTOR)은 "시각" 열에 장치 항목 키의 마지막 기록 시각을 넣습니다. 같은 플러그인은 `DiskId` 를 장치 항목 키 아래 첫 번째 인스턴스에서만 읽습니다. 그래서 한 장치 항목 아래 인스턴스가 여럿이면 `DiskId` 가 모두 같게 나옵니다. 속성 `0064`·`0065` 이름을 바꿔 적는 도구도 있습니다. 이 내용은 [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md)에서 다룹니다.
6. **컨트롤셋이 여럿이면 모두 봅니다.** 한쪽에만 남은 장치가 있을 수 있습니다.
7. **누가 지운 경우에도 흔적이 남습니다.** 하이브 안의 [지워진 셀](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md), 트랜잭션 로그, [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 속 옛 SYSTEM 하이브, `setupapi.dev.log`, [AmCache 장치 항목](../../execution/amcache-hve/inventorydevicepnp.md)을 봅니다. Cowen 은 `SYSTEM\Setup\Upgrade\PnP\CurrentControlSet\Control\DeviceMigration\Devices\USBSTOR` 에도 장치가 남는다고 보고했지만, Windows 11 에서는 `DeviceMigration\Devices` 키는 있어도 그 아래에 `USBSTOR` 가 없을 수 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

1. SYSTEM 하이브와 `.LOG1`·`.LOG2` 를 사본으로 확보합니다.
2. 하이브에서 ASCII 문자열 `Disk&Ven_`(`44 69 73 6B 26 56 65 6E 5F`)를 찾습니다. 장치 항목 키의 키 노드(`nk`) 셀이 걸립니다. 같은 문자열은 `DeviceClasses` 하위 키 이름에도 들어 있으니 셀의 서명을 확인합니다.
3. 셀 맨 앞 4바이트 크기 필드의 부호를 봅니다. 음수는 쓰는 셀, 양수는 빈 셀입니다. 빈 셀에서 걸린 키는 지워진 키일 수 있습니다.
4. 장치 항목 키의 하위 키 목록을 따라가 인스턴스 키의 `nk` 셀을 읽습니다. 셀 구조는 [하이브 내부 구조 (regf·hbin·Cell)](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)를 봅니다.

아래는 libregf 형식 명세로 만든 예시입니다. 실제 데이터에서 나온 값이 아닙니다. 인스턴스 키 이름은 `AB12CD34&0` 이라고 가정했습니다. 목록 위치를 가리키는 오프셋들도 지어낸 값입니다.

```
00000000  a0 ff ff ff 6e 6b 20 00 80 e6 1b c4 9b 6e da 01  |....nk ......n..|
00000010  00 00 00 00 20 20 1b 00 02 00 00 00 00 00 00 00  |....  ..........|
00000020  80 2f 1b 00 ff ff ff ff 0c 00 00 00 10 2e 1b 00  |./..............|
00000030  78 1c 00 00 ff ff ff ff 22 00 00 00 00 00 00 00  |x.......".......|
00000040  1c 00 00 00 9c 00 00 00 00 00 00 00 0a 00 00 00  |................|
00000050  41 42 31 32 43 44 33 34 26 30 00 00 00 00 00 00  |AB12CD34&0......|
```

오프셋은 셀 시작에서 센 값입니다.

1. 0x00 의 `a0 ff ff ff` 는 -96 입니다. 쓰는 중인 96바이트 셀입니다.
2. 0x04 의 `6e 6b` 는 서명 `nk` 입니다.
3. 0x06 의 `20 00` 은 플래그 0x0020 입니다. 키 이름이 ASCII 로 적혀 있다는 뜻입니다.
4. 0x08 의 8바이트를 리틀 엔디언으로 읽으면 `0x01DA6E9BC41BE680` 입니다. FILETIME 으로 풀면 2024-03-05 01:23:45 UTC 입니다. 이 키의 마지막 기록 시각입니다. → [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)
5. 0x18 의 `02 00 00 00` 은 하위 키 2개입니다(`Device Parameters`·`Properties`).
6. 0x28 의 `0c 00 00 00` 은 값 12개입니다.
7. 0x4C 의 `0a 00` 은 키 이름 길이 10바이트입니다.
8. 0x50 부터 10바이트가 키 이름 `AB12CD34&0` 입니다. 둘째 글자가 `B` 이므로 시스템이 만든 `&` 형 이름이 아닙니다.

값 데이터는 따로 떨어진 셀에 있습니다. `FriendlyName` 같은 REG_SZ 값은 UTF-16LE 로 적힙니다. 그래서 제품 이름으로 찾을 때는 ASCII 와 UTF-16LE 를 모두 찾습니다.

### 공개 도구로 한 번

- 레지스트리 뷰어(예: Registry Explorer)로 하이브 사본을 열고 `ControlSet00X\Enum\USBSTOR` 를 펼칩니다. 뷰어가 트랜잭션 로그를 반영해 여는지 확인합니다.
- RegRipper 의 `usbstor` 플러그인은 장치 항목·인스턴스마다 이름, `FriendlyName`, `ParentIdPrefix`, 하위 키 시각, 속성 시각을 한 번에 냅니다.
- 도구가 낸 "시각" 이 어느 키, 어느 값의 시각인지 소스나 설명서로 확인합니다.
- 도구 결과와 원시 키가 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 절차를 따릅니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 값 | 링크 |
|---|---|---|
| Enum\USB | VID·PID, USB 쪽 일련번호, `ContainerID` | [USB 장치 식별자 (Enum\USB VID·PID)](enum-usb-vid-pid.md) |
| 장치 속성·DeviceClasses | 설치·연결·해제 시각 | [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md) |
| MountedDevices | 인스턴스 ID 가 든 값, 드라이브 문자·볼륨 GUID | [드라이브 문자 매핑 (MountedDevices)](mounteddevices.md) |
| MountPoints2 | 볼륨 GUID, 사용자 | [사용자별 장치 연결 (MountPoints2)](mountpoints2.md) |
| setupapi.dev.log | 처음 설치 기록, Windows 가 지운 기록 | [장치 설치 로그 (setupapi.dev.log)](setupapi-dev-log.md) |
| WPD·EMDMgmt | 볼륨 이름, 볼륨 시리얼 번호 | [휴대용 장치·볼륨 이름 기록 (WPD·EMDMgmt)](wpd-emdmgmt.md) |
| AmCache | `usbstor/` 로 시작하는 장치 항목 | [장치 항목 (InventoryDevicePnp)](../../execution/amcache-hve/inventorydevicepnp.md) |
| 이벤트 로그 | 연결 시각 | [외부 장치 연결 이벤트](../../event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) |
| 셸백·바로가기 | 장치 안의 폴더·파일을 연 흔적 | [외부 장치 탐색 흔적](../../file-folder-usage/shellbags/removable-network-zip.md), [바로가기 파일 (LNK)](../../file-folder-usage/lnk.md) |

전체 조사 순서는 [USB 로 무엇을 가져갔나](../../../04-scenarios/exfiltration/data-exfiltration/usb.md)에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 실습 이미지 가운데 USB 저장장치를 쓴 시나리오 이미지를 골라 풀어 봅니다.

1. `Select` 키로 쓰던 컨트롤셋을 정하고 `Enum\USBSTOR` 의 장치 항목 키와 인스턴스 키를 모두 적습니다. 장치는 몇 개입니까?
2. 인스턴스 키 이름의 둘째 글자가 `&` 인 장치가 있습니까? 그 장치의 `Capabilities` 값은 얼마입니까?
3. 각 인스턴스를 `Enum\USB` 의 인스턴스와 맞춥니다. 일련번호 전체가 같은지, 앞부분만 같은지, `ContainerID` 로만 이어지는지 나눠 적습니다.
4. 장치 항목 키·인스턴스 키의 마지막 기록 시각을 속성 `0065`·`0066` 과 나란히 놓습니다. 어느 시각과 가깝습니까?
5. `setupapi.dev.log` 의 "was removed." 줄과, 하이브에서 헥스로 찾은 빈 셀의 `Disk&Ven_` 이름을 모읍니다. USBSTOR 에 없는 장치가 여기에만 나옵니까?

## 참고 문헌

- Microsoft Learn, "Identifiers Generated by USBSTOR.SYS" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/identifiers-generated-by-usbstor-sys · "Identifiers for SCSI Devices" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/identifiers-for-scsi-devices · "Device Object Example for a USB Mass Storage Device" — https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/device-object-example-for-a-usb-mass-storage-device
- Microsoft Learn, "Instance ID" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/instance-ids · "HKLM\SYSTEM\CurrentControlSet\Enum Registry Tree" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/hklm-system-currentcontrolset-enum-registry-tree · "SetupDiGetDeviceRegistryPropertyW" — https://learn.microsoft.com/en-us/windows/win32/api/setupapi/nf-setupapi-setupdigetdeviceregistrypropertyw
- Forensics Wiki, "USB History Viewing" — https://forensics.wiki/usb_history_viewing/
- David Cowen, "Windows, Now with built in Anti Forensics!", Hacking Exposed Computer Forensics Blog, 2017 — https://www.hecfblog.com/2017/04/windows-now-built-in-anti-forensics.html · "What did they take when they left? Part 4 (External Devices)", 2009 — https://www.hecfblog.com/2009/08/what-did-they-take-when-they-left-part.html
- Yogesh Khatri, "Windows 8 New Registry Artifacts Part 1", Swift Forensics, 2013 — https://www.swiftforensics.com/2013/11/windows-8-new-registry-artifacts-part-1.html
- libyal, "Windows NT Registry File (REGF) format" (libregf 문서) — https://github.com/libyal/libregf/blob/main/documentation/Windows%20NT%20Registry%20File%20(REGF)%20format.asciidoc · 공개 도구 소스: RegRipper 3.0 `usbstor.pl` — https://github.com/keydet89/RegRipper3.0/blob/master/plugins/usbstor.pl , RegistryPlugin.USBSTOR `USBSTOR.cs` — https://github.com/EricZimmerman/RegistryPlugins/blob/master/RegistryPlugin.USBSTOR/USBSTOR.cs , mingw-w64 `devpkey.h`·`cfgmgr32.h` (2026-09 열람)
