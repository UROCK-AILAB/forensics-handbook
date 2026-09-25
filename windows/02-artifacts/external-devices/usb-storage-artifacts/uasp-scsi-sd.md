---
title: "USBSTOR 에 안 남는 장치"
parent: "USB 저장장치 흔적"
grand_parent: "아티팩트 · 외부 장치"
nav_order: 1550
---

# USBSTOR 에 안 남는 장치 (UASP·SCSI·SD 카드)

## 한 줄 요약

USBSTOR 키에는 Usbstor.sys 드라이버가 맡은 저장장치만 남습니다. UASP 로 붙은 USB 저장장치와 eSATA·썬더볼트 외장 디스크는 `Enum\SCSI` 에 남고, 내장 SD 슬롯에 꽂은 메모리 카드는 `Enum\SD` 에 남습니다. 그래서 USBSTOR 가 비어 있어도 외부 저장장치를 안 썼다고 단정할 수 없습니다.

## 왜 USBSTOR 에 안 남나

SYSTEM 하이브 `ControlSet00X\Enum` 바로 아래 키 이름은 장치를 찾아낸 열거자 (Enumerator) 입니다. `USB`·`USBSTOR`·`SCSI`·`SD`·`STORAGE` 가 모두 열거자 이름입니다. 어느 컨트롤셋을 볼지는 [컨트롤셋 고르기](../../../01-foundations/database-log-formats/registry-hive/controlset-select.md) 에서 다룹니다.

`USBSTOR` 에는 USB 저장 포트 드라이버인 Usbstor.sys 가 만든 장치가 모입니다. Microsoft 문서에 따르면 Usbstor.sys 는 USB 저장장치 하나를 논리 장치 최대 16개로 나눌 수 있습니다. 문서의 카드 리더 예에서는 슬롯마다 물리 장치 객체 (PDO) 를 하나씩 만듭니다. 이 장치 객체가 `USBSTOR\Disk&Ven_…` 항목이 됩니다. 다른 드라이버가 맡은 저장장치는 이 자리에 나타나지 않습니다.

USBSTOR 를 거치지 않는 경우는 세 가지입니다.

**1. UASP 장치.** USB 연결 SCSI 프로토콜 (USB Attached SCSI Protocol, UASP) 을 쓰는 장치는 Uaspstor.sys 가 맡습니다. Microsoft 는 이 드라이버를 벌크 스트림 (Bulk Stream) 을 지원하는 SuperSpeed USB 장치용 클래스 드라이버로 설명합니다. 대상은 USB 대용량 저장 클래스 (08h) 가운데 하위 클래스 06h·프로토콜 62h 인 장치입니다. 이 장치의 설치 클래스는 USB 가 아니라 SCSIAdapter 입니다. 그래서 그 아래 디스크는 내장 디스크처럼 `Enum\SCSI` 에 남습니다. UASP 를 지원하는 외장 SSD 와 디스크 케이스가 여기에 해당합니다.

**2. USB 가 아닌 버스로 붙은 디스크.** eSATA 외장 디스크는 내장 SATA 디스크와 같은 드라이버를 씁니다. 썬더볼트 외장 NVMe 디스크는 PCIe 장치로 붙으므로 내장 NVMe 디스크와 같은 드라이버를 씁니다. 두 경우 모두 내장 디스크가 남는 열거자에 남습니다. Windows 8 이후 기본 AHCI·NVMe 드라이버에서는 `Enum\SCSI` 입니다. 드라이버에 따라 `Enum\IDE` 같은 다른 열거자에 남을 수 있으므로 검체의 내장 디스크 위치부터 봅니다.

**3. 내장 SD 슬롯.** PCI 버스에 붙은 SD 호스트 컨트롤러 (SD Host Controller) 는 SD 버스 드라이버 sdbus.sys 가 맡습니다. 여기에 메모리 카드를 꽂으면 카드 항목이 `Enum\SD` 에 생깁니다. USB 로 붙은 카드 리더는 다릅니다. 이 리더는 Usbstor.sys 가 맡으므로 USBSTOR 에 남습니다. 노트북 내장 리더라도 안에서 USB 로 붙어 있으면 USBSTOR 에 남습니다.

스마트폰처럼 MTP 로 붙는 장치는 저장장치로 붙지 않습니다. 이 경우는 [휴대용 장치·볼륨 이름 기록 (WPD·EMDMgmt)](wpd-emdmgmt.md) 과 [스마트폰으로 옮겼나 (MTP·Phone Link)](../../../04-scenarios/exfiltration/data-exfiltration/mtp-phone-link.md) 에서 다룹니다.

## 위치와 버전별 차이

### 연결 방식별 기록 위치

| 연결 방식 | 맡는 드라이버 | 남는 곳 (SYSTEM `ControlSet00X\Enum\…`) | USBSTOR |
|---|---|---|---|
| UASP 를 쓰지 않는 USB 저장장치 | Usbstor.sys | `USB\VID_…&PID_…`, `USBSTOR\Disk&Ven_…` | 남음 |
| UASP 외장 SSD·디스크 케이스 | Uaspstor.sys | `USB\VID_…&PID_…` (Service 값 `UASPStor`), `SCSI\Disk&Ven_…&Prod_…` | 안 남음 |
| USB 카드 리더 | Usbstor.sys | `USBSTOR\…` (슬롯마다 하나) | 남음 (리더 정보만) |
| PCI 에 붙은 내장 SD 슬롯 | sdbus.sys 와 SD 저장 드라이버 | `SD\VID_…&OID_…&PID_…&REV_…` | 안 남음 |
| eSATA·썬더볼트 외장 디스크 | 내장 디스크와 같은 드라이버 | 내장 디스크와 같은 열거자 (예: `SCSI\Disk&Ven_…&Prod_…`) | 안 남음 |

### Windows 버전에 따른 차이

| 항목 | Windows 7 | Windows 8·8.1 | Windows 10·11 |
|---|---|---|---|
| UASP 기본 드라이버 (Uaspstor.sys) | 없음 | 있음 | 있음 |
| 컨테이너 ID (Container ID) | 있음 | 있음 | 있음 |
| 장치 속성 0064·0065 | 있음 | 있음 | 있음 |
| 장치 속성 0066·0067 | 없음 | 있음 | 있음 |

Windows 7 에는 UASP 기본 드라이버가 없어서 같은 장치도 Windows 7 PC 에서는 Usbstor.sys 로 붙어 USBSTOR 에 남을 수 있습니다. Windows 8 이후라도 USB 2.0 포트에 꽂으면 장치가 SuperSpeed 로 붙지 않으므로 이때도 Usbstor.sys 로 붙을 수 있습니다. 컨테이너 ID 는 Windows 7 부터 모든 장치 노드에 붙는 속성입니다. 장치 속성 0064~0067 의 버전별 차이는 [연결·해제 시각 (DeviceClasses·Device Properties 0064·0066·0067)](deviceclasses-device-properties-0064-0066-0067.md) 에서 다룹니다.

## 구조 — UASP 장치의 두 항목 잇기

UASP 장치 하나는 `Enum\USB` 와 `Enum\SCSI` 에 항목을 하나씩 남깁니다. `Enum\USB` 항목은 USB 장치 자체이고 `Enum\SCSI` 항목은 그 안의 디스크이므로, 두 항목을 이어야 VID·PID·시리얼 번호와 디스크 모델명·시각을 한 장치로 묶을 수 있습니다.

아래에서 "(관찰)" 을 붙인 내용은 문서에 없고 Windows 11 빌드 26200 레지스트리에서 본 것입니다.

> 그림 자리: `Enum\USB\VID_…&PID_…\MSFT30<시리얼>` (Service=UASPStor, ParentIdPrefix=P, ContainerID=C) → `Enum\SCSI\Disk&Ven_…&Prod_…\P&000000` (ContainerID=C, Partmgr DiskId=D) → `Enum\STORAGE\Volume\{D}#…`·WPD 키 `SWD#WPDBUSENUM#{D}#…` 로 이어지는 그림

### Enum\USB 인스턴스 키

| 값 | UASP 장치 | Usbstor.sys 장치 |
|---|---|---|
| Service | `UASPStor` | `USBSTOR` |
| ClassGUID | `{4d36e97b-e325-11ce-bfc1-08002be10318}` (SCSIAdapter) | `{36fc9e60-c465-11cf-8056-444553540000}` (USB) |
| 인스턴스 ID | `MSFT30` 뒤에 시리얼 번호 (관찰) | 시리얼 번호 |
| ParentIdPrefix | 있음 (관찰) | 장치에 따라 다름 |

`MSFT30` 여섯 글자는 장치 시리얼 번호가 아니므로 다른 기록과 맞출 때는 이 접두어를 떼고 비교합니다. 이 접두어가 붙는 조건을 밝힌 Microsoft 문서는 찾지 못했습니다. 그래서 UASP 여부는 접두어가 아니라 Service 값과 ClassGUID 값으로 가립니다. 시리얼 번호와 VID·PID 를 읽는 법은 [USB 장치 식별자 (Enum\USB VID·PID)](enum-usb-vid-pid.md) 에서 다룹니다.

### Enum\SCSI 인스턴스 키

- 키 경로는 `Enum\SCSI\Disk&Ven_<제조사>&Prod_<제품>\<인스턴스 ID>` 꼴입니다 (관찰).
- 인스턴스 ID 는 `Enum\USB` 쪽 ParentIdPrefix 값 뒤에 `&` 와 16진수 6자리가 붙은 꼴입니다 (관찰).
- 두 키의 ContainerID 값은 같았습니다 (관찰). Microsoft 문서에 따르면 한 물리 장치에 속한 장치 노드는 모두 같은 컨테이너 ID 를 씁니다.
- 사람이 읽는 장치 이름은 FriendlyName 값에 있습니다.
- `Properties\{83da6326-97a6-4088-9453-a1923f573b29}\0064`~`0067` 에 설치·연결·해제 시각이 있습니다 (관찰).
- `Device Parameters\Partmgr` 키의 DiskId 값에 디스크를 가리키는 GUID 가 있습니다 (관찰).

### DiskId 로 볼륨 기록까지 잇기

UASP 디스크의 볼륨 기록은 키 이름에 시리얼 번호 대신 DiskId 를 씁니다 (관찰).

| 하이브 | 위치 | 키 이름 꼴 (관찰) |
|---|---|---|
| SYSTEM | `ControlSet00X\Enum\STORAGE\Volume` | `{DiskId}#<16진수 16자리>` |
| SYSTEM | `ControlSet00X\Enum\SWD\WPDBUSENUM` | `{DiskId}#<16진수 16자리>` |
| SOFTWARE | `Microsoft\Windows Portable Devices\Devices` | `SWD#WPDBUSENUM#{DiskId}#<16진수 16자리>` |
| SYSTEM | `ControlSet00X\Control\DeviceClasses\{53f56307-b6bf-11d0-94f2-00a0c91efb8b}` | `##?#SCSI#Disk&Ven_…&Prod_…#<인스턴스 ID>#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}` |

Usbstor.sys 장치라면 이 자리에 USBSTOR 장치 경로와 시리얼 번호가 들어갑니다. 그래서 시리얼 번호로만 찾으면 UASP 볼륨 기록을 놓칩니다.

같은 PC 의 MountedDevices 값 데이터에는 `SCSI#Disk…` 장치 경로 문자열이 없었습니다 (관찰). 값 데이터를 푸는 법은 [드라이브 문자 매핑 (MountedDevices)](mounteddevices.md) 에서 다룹니다.

### Enum\SD 인스턴스 키

Microsoft 문서가 정한 SD 메모리 카드의 장치 ID 는 `SD\VID_v(2)&OID_o(4)&PID_p(0~5)&REV_n.m` 꼴입니다. 레지스트리에서는 `Enum\SD\VID_…&OID_…&PID_…&REV_…\<인스턴스 ID>` 가 됩니다.

| 칸 | 뜻 |
|---|---|
| VID | SD 카드 협회 (SD Card Association, SDA) 가 정한 제조사 번호. 16진수 2자리 |
| OID | SDA 가 정한 OEM·카드 내용 번호. 16진수 4자리 |
| PID | 제조사가 넣은 제품 이름. ASCII 0~5자 |
| REV | 제조사가 넣은 리비전. 예: `6.2` |

하드웨어 ID 는 두 개인데, 하나는 장치 ID 와 같고 다른 하나는 장치 ID 에서 리비전을 뺀 값입니다. 호환 ID 는 언제나 `SD\CLASS_STORAGE` 입니다.

이 식별자는 카드 모델을 가리키며, 문서의 장치 ID 에는 카드 한 장을 가리키는 시리얼 번호가 없습니다. 인스턴스 ID 에 무엇이 들어가는지는 문서에 없으므로 인스턴스 ID 를 카드 시리얼 번호로 단정하지 않습니다.

Microsoft 의 SD 드라이버 스택 문서는 카드 위에 sffdisk.sys 와 sffp_sd.sys 가 올라간다고 설명하고, Windows 10 에는 SD 저장 포트 드라이버 sdstor.sys 도 있습니다. 실제로 붙은 드라이버는 Service 값으로 확인합니다. 카드 아래 디스크 항목이 어느 열거자에 생기는지는 이 글에서 확인하지 못했습니다. 같은 ContainerID 를 쓰는 항목을 찾아 잇습니다.

### USB 카드 리더

Microsoft 문서의 예에서 CF 슬롯과 스마트미디어 슬롯이 있는 리더는 장치 객체를 두 개 만듭니다. 슬롯마다 USBSTOR 항목이 생긴다는 뜻이라서 카드를 꽂은 적이 없는 슬롯도 USBSTOR 항목으로 남을 수 있습니다. 이 항목의 제조사·제품·시리얼 번호는 리더가 알려 준 값이며 카드를 바꿔 꽂아도 그대로입니다. 어떤 카드를 꽂았는지는 볼륨 기록 (볼륨 시리얼 번호·볼륨 이름) 으로 봅니다.

## 증거로서 의미

**증명하는 것**

- `Enum\USB` 항목의 Service 값이 `UASPStor` 이면, 그 VID·PID·시리얼 번호를 쓰는 장치가 이 PC 에 UASP 로 붙은 적이 있습니다.
- 그 항목과 이어진 `Enum\SCSI` 항목은 디스크 모델명과 설치·연결·해제 시각을 알려 줍니다.
- `Enum\SD` 항목은 그 제조사 번호·제품 이름을 쓰는 SD 메모리 카드가 내장 SD 슬롯에 들어간 적이 있음을 알려 줍니다.


**증명하지 못하는 것**

- 누가 연결했는지는 알 수 없습니다. SYSTEM 하이브에는 사용자 정보가 없습니다. 사용자는 [사용자별 장치 연결 (MountPoints2)](mountpoints2.md) 로 좁힙니다.
- 파일을 옮겼는지는 알 수 없습니다.
- `Enum\SD` 항목만으로는 카드 한 장을 특정할 수 없습니다. 같은 모델 카드는 같은 장치 ID 를 씁니다.
- USB 카드 리더의 USBSTOR 항목만으로는 카드를 꽂았는지 알 수 없습니다.
- `Enum\SCSI` 항목 하나만으로는 외장 디스크인지 내장 디스크인지 알 수 없습니다.

## 시각 해석

- `Enum\SCSI` 인스턴스 키 아래 0064~0067 은 USBSTOR 쪽과 같은 장치 속성입니다. 값은 FILETIME 이고 UTC 입니다. 각 값의 뜻은 [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md) 에서 다룹니다.
- UASP 장치는 `Enum\USB` 인스턴스 키에도 0064~0067 이 따로 있습니다 (관찰). 두 쪽 시각을 나란히 놓고 봅니다.
- 도구마다 0064·0065 에 붙이는 이름이 다릅니다. RegRipper 4.0 의 scsi.pl 은 0064 를 "First Install", 0065 를 "First Inserted" 로 적습니다. 이름표가 아니라 값 번호로 읽습니다.
- 키 마지막 기록 시각은 연결이 아닌 다른 일로도 바뀝니다. 자세한 규칙은 [키 마지막 기록 시각 (Last Write Time)](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md) 에서 다룹니다.
- FILETIME 을 읽는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

## 함정과 한계

- **USBSTOR 만 보는 도구.** USBSTOR 만 읽는 도구나 점검표는 UASP 장치를 통째로 빠뜨립니다. RegRipper 4.0 저장소의 scsi.pl 은 2022년 8월에 만든 플러그인입니다(소스 머리말 기준). 그보다 오래된 도구 판에는 `Enum\SCSI` 를 읽는 기능이 없을 수 있습니다.
- **`Enum\SCSI` 에 섞인 항목.** 내장 SATA·NVMe 디스크와 광학 드라이브도 `Enum\SCSI` 에 있습니다. 가상 디스크 (`Disk&Ven_Msft&Prod_Virtual_Disk`, `Disk&Ven_VMware_…`) 도 있습니다. 관찰한 PC 에서 내장 NVMe 디스크의 ContainerID 는 `{00000000-0000-0000-ffff-ffffffffffff}` 였습니다. 외장 UASP 디스크에는 자기 ContainerID 가 따로 있었습니다. 이 차이로 먼저 거릅니다.
- **가상 디스크 항목.** `Msft Virtual Disk` 항목은 VHD·VHDX 를 붙인 흔적일 수 있습니다. 버리지 말고 따로 봅니다. 형식은 [증거 이미지·가상 디스크 형식](../../../01-foundations/disk-volume/e01-raw-aff4-vhdx-vmdk.md) 에서 다룹니다.
- **MSFT30 접두어.** 이 접두어를 떼지 않으면 다른 기록의 시리얼 번호와 어긋납니다. 공개 스크립트 parseUSBs 는 Partition/Diagnostic 1006 이벤트와 Storsvc/Diagnostic 1001 이벤트의 ParentId·SerialNumber 필드에서도 이 접두어를 뗍니다. UASP 장치가 이 로그에도 남을 수 있다는 뜻입니다.
- **한 장치, 두 기록.** 같은 장치를 USB 2.0 포트나 Windows 7 PC 에 꽂으면 USBSTOR 에 남을 수 있습니다. 한 PC 에서 두 방식으로 모두 붙었다면 `Enum\USB` 에 `MSFT30` 이 붙은 인스턴스와 안 붙은 인스턴스가 따로 생길 수 있습니다. 접두어를 떼고 시리얼 번호를 비교합니다.
- **제조사 드라이버.** 제조사 전용 드라이버를 깐 카드 리더나 디스크 케이스는 다른 열거자나 서비스 이름을 쓸 수 있습니다. Service 값과 ContainerID 로 따라갑니다.
- **정리 도구.** USBSTOR 만 지우는 정리 방식은 `Enum\USB`·`Enum\SCSI`·`Enum\STORAGE\Volume`·WPD 기록을 남길 수 있습니다. 지운 키는 [지워진 키·값 복구](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md)·[트랜잭션 로그](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md)·[섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 다시 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

1. SYSTEM 하이브에서 1바이트 문자 `MSFT30` 을 찾습니다. 키 이름은 대개 1바이트 문자로 저장됩니다. 저장 방식은 [하이브 내부 구조 (regf·hbin·Cell)](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md) 에서 다룹니다.
2. 찾은 키의 값 데이터에서 UTF-16LE `UASPStor` 를 확인합니다. REG_SZ 값은 UTF-16LE 로 저장됩니다. 인코딩은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.
3. 같은 키의 ParentIdPrefix 값을 읽습니다. 그 문자열로 시작하는 키 이름을 `Enum\SCSI` 아래에서 찾습니다.
4. 내장 SD 슬롯 흔적은 UTF-16LE `SD\CLASS` 로 찾습니다. CompatibleIDs 값에 `SD\CLASS_STORAGE` 가 들어가기 때문입니다.
5. 할당되지 않은 셀에서 찾은 결과는 지워진 키일 수 있습니다. 이런 결과는 따로 표시해 둡니다.

```text
아래는 문자 인코딩 규칙으로 만든 검색 패턴 예시입니다. 특정 검체에서 나온 값이 아닙니다.

"MSFT30"    1바이트 문자 (키 이름)
4D 53 46 54 33 30

"UASPStor"  UTF-16LE (REG_SZ 값 데이터, 끝의 00 00 은 문자열 끝 표시)
55 00 41 00 53 00 50 00 53 00 74 00 6F 00 72 00 00 00

"SD\CLASS"  UTF-16LE (CompatibleIDs 값 데이터의 앞부분)
53 00 44 00 5C 00 43 00 4C 00 41 00 53 00 53 00
```

### 공개 도구로 한 번

- **RegRipper 4.0 scsi.pl.** `Enum\SCSI` 아래 모든 항목의 DeviceDesc·Mfg·Service·FriendlyName 값과 0064~0067 을 적습니다. 내장 디스크와 외장 디스크를 가르지 않습니다. `Enum\USB` 항목과 잇지도 않습니다.
- **parseUSBs (Kathryn Hedley).** `Enum\USB` 에서 `MSFT30` 으로 시작하는 인스턴스를 찾습니다. ParentIdPrefix 로 `Enum\SCSI` 항목과 잇습니다. DiskId 로 WPD 키와 잇습니다. `MSFT30` 으로 시작하지 않는 UASP 인스턴스는 이 경로로 잇지 않습니다. `Enum\SD` 와 ContainerID 는 읽지 않습니다.
- 두 도구의 결과를 레지스트리 원본과 한 번씩 대조합니다. 대조하는 법은 [도구 결과 교차 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 잇는 열쇠 | 페이지 |
|---|---|---|
| Enum\USB 인스턴스 | ParentIdPrefix·ContainerID | [USB 장치 식별자](enum-usb-vid-pid.md) |
| 장치 속성 시각·DeviceClasses | 같은 인스턴스 키, 키 이름 속 `SCSI#Disk…` 경로 | [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md) |
| MountedDevices | 볼륨 GUID·값 데이터 | [드라이브 문자 매핑](mounteddevices.md) |
| MountPoints2 | 볼륨 GUID | [사용자별 장치 연결](mountpoints2.md) |
| WPD·EMDMgmt | DiskId·볼륨 시리얼 번호 | [휴대용 장치·볼륨 이름 기록](wpd-emdmgmt.md) |
| setupapi.dev.log | `MSFT30` 이 붙은 USB 장치 경로·`uaspstor.inf` (관찰) | [장치 설치 로그](setupapi-dev-log.md) |
| Partition/Diagnostic 이벤트 | `MSFT30` 을 뗀 시리얼 번호·모델명 | [외부 장치 연결 이벤트](../../event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) |
| 바로가기 파일·점프리스트 | 볼륨 시리얼 번호 | [바로가기 파일 (LNK)](../../file-folder-usage/lnk.md) · [점프리스트](../../file-folder-usage/jump-lists.md) |
| AmCache 장치 항목 | 장치 목록 | [장치 항목 (InventoryDevicePnp)](../../execution/amcache-hve/inventorydevicepnp.md) |

전체 조사 순서는 [USB 로 무엇을 가져갔나 (USB)](../../../04-scenarios/exfiltration/data-exfiltration/usb.md) 에서 다룹니다.

## 실습

1. NIST CFReDS 에서 Windows 7 이후 시스템 이미지를 하나 골라 SYSTEM 하이브를 꺼냅니다. `Enum\SCSI` 에 어떤 항목이 있습니까? 각 항목이 내장인지 외장인지 무엇으로 가렸습니까?
2. 같은 검체에서 USBSTOR 항목 수와 `Enum\USB` 의 저장장치 항목 수가 맞습니까? 맞지 않으면 남는 `Enum\USB` 항목의 Service 값은 무엇입니까?
3. 시험용 실제 PC (Windows 10·11) 에 UASP 디스크 케이스를 USB 3 포트에 꽂습니다. 그다음 USB 2.0 포트에도 꽂습니다. 두 번 연결한 뒤 USBSTOR·`Enum\USB`·`Enum\SCSI` 에 각각 무엇이 생겼습니까? 가상 머신에서는 결과가 달라질 수 있으므로 실제 PC 에서 합니다.
4. 3번에서 찾은 UASP 디스크의 DiskId 로 `Enum\STORAGE\Volume` 과 WPD 키를 찾습니다. 드라이브 문자와 볼륨 이름까지 이어집니까?
5. 내장 SD 슬롯이 있는 노트북에 같은 모델 카드 두 장과 다른 모델 카드 한 장을 차례로 꽂습니다. `Enum\SD` 항목은 어떻게 달라집니까? 인스턴스 ID 로 같은 모델 카드 두 장을 구별할 수 있습니까?

## 참고 문헌

- Microsoft Learn, "USB Device Class Drivers Included in Windows" — https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/supported-usb-classes
- Microsoft Learn, "Device Object Example for a USB Mass Storage Device" — https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/device-object-example-for-a-usb-mass-storage-device
- Microsoft Learn, "Overview of Container IDs" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/overview-of-container-ids
- Microsoft Learn, "Identifiers for Secure Digital (SD) Devices" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/identifiers-for-secure-digital--sd--devices
- Microsoft Learn, "SD Card Driver Stack" — https://learn.microsoft.com/en-us/windows-hardware/drivers/sd/sd-card-driver-stack
- Kathryn Hedley, parseUSBs (GitHub) — https://github.com/khyrenz/parseusbs
- Harlan Carvey, RegRipper 4.0 플러그인 소스 `scsi.pl` (2026-09 열람) — https://raw.githubusercontent.com/keydet89/RegRipper4.0/main/plugins/scsi.pl
