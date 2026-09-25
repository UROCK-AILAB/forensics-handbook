---
title: "USB 장치 식별자"
parent: "USB 저장장치 흔적"
grand_parent: "아티팩트 · 외부 장치"
nav_order: 1490
---

# USB 장치 식별자 (Enum\USB VID·PID)

## 한 줄 요약

SYSTEM 하이브의 `Enum\USB` 키에는 이 PC 에 연결된 USB 장치가 스스로 밝힌 제조사 번호, 제품 번호, 일련번호가 장치마다 키 하나로 남습니다.

## 무엇을 기록하나 · 왜 생기나

USB 장치를 꽂으면 PC 는 먼저 장치에서 장치 설명자 (Device Descriptor) 를 받습니다. 장치 설명자에는 제조사 번호 (Vendor ID, VID), 제품 번호 (Product ID, PID), 장치 개정 번호 (bcdDevice) 가 들어 있고, 일련번호 문자열이 있는지는 `iSerialNumber` 칸이 알려 줍니다. Windows 의 USB 허브 드라이버는 VID·PID·개정 번호로 장치 ID (Device ID) 를 만들고, 플러그 앤 플레이 관리자 (PnP Manager) 는 장치 ID 에 인스턴스 ID (Instance ID) 를 이어 붙여 장치 인스턴스 ID (Device Instance ID) 를 만듭니다. 장치 인스턴스 ID 는 재부팅해도 바뀌지 않으며, Windows 는 이 값을 경로로 삼아 `Enum` 아래에 장치 키를 만듭니다.

VID 는 USB 표준 단체 (USB-IF) 가 제조사에 나눠 주고, PID 는 제조사가 제품마다 정합니다.

`Enum\USB` 는 USB 버스에 붙은 장치를 종류와 상관없이 기록하므로 저장장치 말고도 키보드·마우스, 스마트폰, 웹캠, 허브가 여기에 남습니다. USB 저장장치 하나는 두 곳에 나뉘어 남습니다. `Enum\USB` 키는 USB 장치 자체를 나타내고 [USBSTOR](usbstor.md) 키는 그 장치 안의 디스크를 나타내며, `Enum\USB` 쪽은 VID·PID 숫자로, USBSTOR 쪽은 제조사·제품 이름 문자열로 장치를 가리킵니다.

## 위치와 버전별 차이

```text
SYSTEM\ControlSet00X\Enum\USB\VID_vvvv&PID_pppp\<인스턴스 ID>
SYSTEM\ControlSet00X\Enum\USB\VID_vvvv&PID_pppp&MI_zz\<인스턴스 ID>    (복합 장치의 인터페이스)
```

- 하이브 파일 위치는 [하이브 파일 종류와 위치](../../../01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md) 에 있습니다.
- 실행 중인 시스템에서는 `HKLM\SYSTEM\CurrentControlSet\Enum\USB` 로 보입니다.
- 이미지에서 꺼낸 하이브에는 `CurrentControlSet` 이 없습니다. `Select` 키에서 쓰던 컨트롤셋 번호를 먼저 확인합니다. → [컨트롤셋 고르기](../../../01-foundations/database-log-formats/registry-hive/controlset-select.md)
- `vvvv`·`pppp` 는 16진수 네 자리입니다.
- `MI_zz` 의 `zz` 는 인터페이스 번호입니다.
- 키 이름을 비교할 때는 대소문자를 가리지 않습니다.

Microsoft 는 `Enum` 트리를 운영체제 전용으로 두고 구조가 바뀔 수 있다고 밝히므로 값 이름과 하위 키는 검체의 Windows 버전에서 직접 확인합니다.

| 항목 | Windows 버전 | 비고 |
|---|---|---|
| `VID_vvvv&PID_pppp\<인스턴스 ID>` 키 구조 | XP ~ 11 | 이름 규칙이 같습니다 |
| 장치가 보내는 컨테이너 ID 설명자 (Microsoft OS ContainerID descriptor) | 7 이후 | 공식 문서 기준 |
| `Properties` 아래 마지막 연결·해제 시각 | 8 이후 | → [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md) |
| UASP 저장장치 (서비스 `UASPStor`) | 8 이후 | 디스크가 USBSTOR 가 아닌 곳에 남습니다 → [USBSTOR 에 안 남는 장치](uasp-scsi-sd.md) |

## 구조

### 키 이름 (장치 ID)

키 이름의 VID·PID 는 장치 설명자의 `idVendor`·`idProduct` 에서 옵니다. Microsoft 문서는 USB 장치 ID 를 `USB\VID_v(4)&PID_d(4)&REV_r(4)` 형식으로 설명하지만, 같은 문서 모음의 예시에서 장치 인스턴스 ID 는 `USB\VID_045E&PID_0840\0C33CG9212501N0` 처럼 개정 번호 (REV) 없이 쓰입니다. `Enum\USB` 아래 키 이름도 REV 가 빠진 `VID_vvvv&PID_pppp` 형태이며, 개정 번호는 인스턴스 키의 `HardwareID` 값에서 확인합니다.

### 인스턴스 ID — 일련번호인지 먼저 가린다

인스턴스 ID 는 버스 드라이버가 알려 줍니다. Microsoft 는 버스가 지원하면 인스턴스 ID 에 일련번호가 들어가고 아니면 위치 정보가 들어간다고 설명하며, USB 에서는 두 가지 모양으로 나타납니다.

| 모양 | 예 (Microsoft 문서의 예시) | 뜻 |
|---|---|---|
| 장치 일련번호 | `0C33CG9212501N0` | 장치가 보낸 일련번호 문자열입니다. 같은 장치는 어느 포트에 꽂아도 같은 키에 모입니다. |
| 시스템이 만든 값 | `5&109d12e&0&1` | 장치가 일련번호를 주지 않았거나 Windows 가 일련번호를 쓰지 않았습니다. 부모 장치와 연결 위치에 따라 정해집니다. |

두 번째 글자가 `&` 이면 시스템이 만든 값으로 보는데, 이 판별법은 포렌식 자료에서 널리 쓰입니다.

`SYSTEM\CurrentControlSet\Control\usbflags\vvvvpppprrrr` 키에는 장치별 USB 설정이 들어가고, `rrrr` 는 개정 번호입니다. 이 키의 `IgnoreHWSerNum` 값이 `0x01` 이면 USB 드라이버가 장치 일련번호를 무시하고 장치 인스턴스는 꽂은 포트에 묶입니다. 그래서 "이 장치에는 일련번호가 없다" 고 쓰기 전에 이 값을 확인합니다.

### 인스턴스 키 안의 값

(Windows 10·11 기준. 장치와 버전에 따라 없는 값도 있습니다.)

| 값 | 형식 | 읽는 법 |
|---|---|---|
| `HardwareID` | REG_MULTI_SZ | `USB\VID_vvvv&PID_pppp&REV_rrrr` 와 `USB\VID_vvvv&PID_pppp` 가 들어 있습니다. 개정 번호는 여기서 봅니다. |
| `CompatibleIDs` | REG_MULTI_SZ | 클래스 코드가 들어 있습니다. 장치 종류를 가리는 데 씁니다. |
| `Service` | REG_SZ | 이 장치에 붙은 드라이버 서비스입니다. 예: `USBSTOR`, `UASPStor`, `usbccgp`, `HidUsb` |
| `DeviceDesc`·`Mfg` | REG_SZ | 드라이버 설치 파일 (INF) 이 정한 이름과 제조사입니다. `@usb.inf,...;표시 문자열` 처럼 INF 참조 뒤에 표시 문자열이 붙기도 합니다. |
| `ClassGUID`·`Class` | REG_SZ | 장치 설치 클래스입니다. → [GUID 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) |
| `Driver` | REG_SZ | `{클래스 GUID}\nnnn` 형태로 드라이버 설정 키를 가리킵니다. |
| `ContainerID` | REG_SZ | 한 물리 장치에서 나온 여러 장치 노드를 묶는 GUID 입니다. |
| `LocationInformation` | REG_SZ | 장치가 잡힌 포트와 허브입니다. 예: `Port_#0002.Hub_#0001` |
| 하위 키 `Properties` | — | 장치 속성이 들어 있습니다. 설치·연결·해제 시각도 여기 있습니다. |
| 하위 키 `Device Parameters` | — | 드라이버별 설정이 들어갑니다. |

`DeviceDesc`·`Mfg` 는 장치가 스스로 보낸 제품 이름과 다를 수 있습니다. 공용 드라이버를 쓰는 장치에는 `USB Composite Device`, `(Standard USB Host Controller)` 같은 일반 문자열만 남으므로 (Microsoft 문서의 예시) 상표 이름을 찾으려면 USBSTOR 쪽 문자열과 함께 봅니다.

`CompatibleIDs` 는 `USB\Class_cc&SubClass_ss&Prot_pp` 형태이고, Windows 10 이후에는 `USB\DevClass_...`, `USB\COMPAT_VID_...` 형태도 함께 보입니다 (Microsoft 문서의 예시). 자주 보는 클래스 코드는 아래와 같으며, 코드 뜻은 USB-IF 의 클래스 코드표를 따릅니다.

| 코드 | 뜻 |
|---|---|
| `Class_08&SubClass_06&Prot_50` | 대용량 저장장치, 벌크 전용 전송 (Bulk-Only Transport). 보통 서비스가 `USBSTOR` 입니다. |
| `Class_08&SubClass_06&Prot_62` | 대용량 저장장치, UAS 전송. 보통 서비스가 `UASPStor` 입니다. |
| `Class_03` | 입력 장치 (HID). 키보드·마우스 |
| `Class_06` | 정지 영상 장치 (Still Imaging). 카메라, 일부 스마트폰 |
| `Class_09` | 허브 |
| `Class_0E` | 영상 장치 (Video). 웹캠 |
| `Class_FF` | 제조사 전용 |

### 복합 장치 (Composite Device)

인터페이스가 여러 개인 장치를 복합 장치라고 합니다. Windows 는 복합 장치에 USB 공용 부모 드라이버 (USB generic parent driver) 를 붙이고, 이 드라이버는 인터페이스마다 `VID_vvvv&PID_pppp&MI_zz` 키를 따로 만듭니다. 부모 키의 `Service` 는 보통 `usbccgp` 이며, 스마트폰, 웹캠, 무선 키보드·마우스 수신기가 흔히 복합 장치로 잡힙니다.
인터페이스 키의 인스턴스 ID 는 시스템이 만든 값인 경우가 많습니다. 관찰로 알게 된 것이고, 모든 장치에서 그런지는 확인하지 않았습니다.
그래서 인터페이스 키와 부모 키는 일련번호가 아니라 `ContainerID` 로 잇습니다.

## 증거로서 의미

**증명하는 것**

- 이 VID·PID 로 자신을 밝힌 USB 장치를 이 Windows 가 장치로 등록한 적이 있습니다.
- 인스턴스 ID 가 일련번호이면, 그 문자열로 USBSTOR·설치 로그·다른 PC 의 기록에서 같은 장치를 찾을 수 있습니다.
- `CompatibleIDs`·`Service` 로 저장장치인지, 입력 장치인지, 복합 장치인지 가릴 수 있습니다.
- 스마트폰·카메라처럼 USBSTOR 에 남지 않는 장치의 연결 흔적이 여기에 남습니다.

**증명하지 못하는 것**

- 누가 연결했는지 알려 주지 않습니다. SYSTEM 하이브는 PC 전체의 기록입니다. 사용자는 [사용자별 장치 연결 (MountPoints2)](mountpoints2.md) 로 좁힙니다.
- 언제 연결했는지는 키 이름과 값만으로 알 수 없습니다.
- 파일을 옮겼는지 알려 주지 않습니다.
- 겉에 찍힌 상표를 증명하지 않습니다. VID·PID·일련번호는 장치 펌웨어가 스스로 보고한 값입니다. 펌웨어를 고친 장치는 다른 번호를 댈 수 있습니다.
- 키가 없다고 연결한 적이 없다는 뜻은 아닙니다. 흔적 정리, 재설치, 초기화 뒤에는 키가 없을 수 있습니다.

보고서에는 기록이 말하는 만큼만 씁니다.
예: "SYSTEM 하이브 `ControlSet001\Enum\USB\VID_1234&PID_5678` 아래에 인스턴스 ID 가 `ABC0123456789` 인 장치 키가 있다. 이 키의 `Service` 값은 `USBSTOR` 이다." (값은 설명용으로 만든 예시입니다.)

## 시각 해석

- 인스턴스 키의 마지막 기록 시각 (Last Write Time) 은 UTC 기준 FILETIME 입니다. → [키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md), [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)
- 이 시각은 그 키의 값이나 하위 키 목록이 바뀔 때 바뀌므로 첫 연결 시각이나 마지막 연결 시각으로 바로 쓰지 않습니다.
- 옛 자료에는 USB 장치 키의 마지막 기록 시각을 마지막 연결 시각으로 설명한 것도 있습니다. 다른 기록과 맞춰 보기 전에는 따르지 않습니다.
- 설치·연결·해제 시각은 인스턴스 키 아래 `Properties` 하위 키에 따로 남습니다. 읽는 법은 [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md) 에서 다룹니다.
- 저장장치라면 `Enum\USB` 쪽 시각과 USBSTOR 쪽 시각을 나란히 놓고 비교합니다.

## 함정과 한계

1. **시스템이 만든 인스턴스 ID 를 일련번호로 적지 않습니다.** 두 번째 글자가 `&` 인 값은 장치의 일련번호가 아닙니다.
2. **키 개수는 장치 개수와 다릅니다.** 일련번호가 없는 장치는 꽂은 포트마다 키가 따로 생길 수 있습니다. 반대로 일련번호 없는 같은 모델 두 개를 같은 포트에 번갈아 꽂으면 키 하나로 보일 수 있습니다.
3. **일련번호가 같다고 반드시 같은 장치는 아닙니다.** 값싼 장치 가운데에는 여러 개가 같은 일련번호를 보고하는 제품이 있습니다.
4. **USB 일련번호와 볼륨 일련번호 (Volume Serial Number) 는 다른 값입니다.** 볼륨 일련번호는 포맷할 때 파일시스템이 정합니다. 볼륨 일련번호는 [WPD·EMDMgmt](wpd-emdmgmt.md) 와 [LNK](../../file-folder-usage/lnk.md) 에서 봅니다.
5. **VID 로 상표를 바로 단정하지 않습니다.** 저장장치는 컨트롤러 칩 제조사의 VID 를 그대로 쓰는 경우가 있습니다. 공개 VID·PID 목록 (예: Linux USB ID 목록 `usb.ids`) 은 여러 사람이 모아 만든 목록이며 공식 등록부가 아닙니다.
6. **외부 장치만 있는 것이 아닙니다.** 루트 허브 (`ROOT_HUB20`, `ROOT_HUB30`) 와 노트북 내장 웹캠·블루투스 어댑터 같은 내부 장치도 `Enum\USB` 에 있습니다. Microsoft 문서에 따르면 PC 안에 붙은 것으로 판단한 장치는 PC 본체의 컨테이너 ID 를 물려받습니다. 여러 장치가 같은 `ContainerID` 를 나눠 쓰면 내장 장치인지 확인합니다.
7. **`ContainerID` 로 다른 PC 의 기록을 잇지 않습니다.** Microsoft 문서는 USB 장치의 컨테이너 ID 가 일련번호의 해시이거나 무작위 값이라고 설명합니다. 무작위 값이면 PC 마다 달라집니다. 같은 PC 안에서 노드를 묶는 데만 씁니다.
8. **지운 흔적이 다른 곳에 남습니다.** 흔적 정리 도구는 `Enum\USB`·USBSTOR 키를 지울 수 있습니다. 지운 키는 하이브 안 빈 공간, 트랜잭션 로그, 섀도 복사본에 남아 있을 수 있습니다. → [지워진 키·값 복구](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md), [트랜잭션 로그](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md), [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md), [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md)

## 직접 분석해 보기

### 헥스로 한 번

**1) 장치 설명자에서 키 이름으로**

아래 18바이트는 명세의 구조로 만든 예시이고 실제 검체에서 나온 값이 아닙니다. 장치 설명자는 디스크에 저장되지 않으며, 레지스트리 값이 어디서 왔는지 보여 주려고 넣었습니다.

```text
12 01 00 02 00 00 00 40 34 12 78 56 00 01 01 02 03 01
```

| 오프셋 | 크기 | 필드 | 예시 값 | 레지스트리에 남는 곳 |
|---|---|---|---|---|
| 0x00 | 1 | bLength | 0x12 (18) | — |
| 0x01 | 1 | bDescriptorType | 0x01 (장치 설명자) | — |
| 0x02 | 2 | bcdUSB | 0x0200 (USB 2.0) | — |
| 0x04 | 1 | bDeviceClass | 0x00 (인터페이스에서 정함) | `CompatibleIDs` |
| 0x05 | 1 | bDeviceSubClass | 0x00 | `CompatibleIDs` |
| 0x06 | 1 | bDeviceProtocol | 0x00 | `CompatibleIDs` |
| 0x07 | 1 | bMaxPacketSize0 | 0x40 (64) | — |
| 0x08 | 2 | idVendor | 0x1234 | 키 이름 `VID_1234` |
| 0x0A | 2 | idProduct | 0x5678 | 키 이름 `PID_5678` |
| 0x0C | 2 | bcdDevice | 0x0100 | `HardwareID` 의 `REV_0100` |
| 0x0E | 1 | iManufacturer | 0x01 | — |
| 0x0F | 1 | iProduct | 0x02 | — |
| 0x10 | 1 | iSerialNumber | 0x03 | 일련번호 문자열이 있다는 뜻입니다. 인스턴스 ID 가 됩니다. |
| 0x11 | 1 | bNumConfigurations | 0x01 | — |

2바이트 칸은 리틀 엔디언이라서 `34 12` 는 0x1234 로 읽습니다. `iSerialNumber` 가 0 이면 일련번호 문자열이 없고, 이때 Windows 는 인스턴스 ID 를 스스로 만듭니다.

**2) `HardwareID` 값**

`HardwareID` 는 문자열 여러 개를 담는 REG_MULTI_SZ (값 종류 7) 입니다. 문자열은 UTF-16LE 로 저장되고 → [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md), 문자열마다 끝에 `00 00` 이 붙으며 목록 끝에는 `00 00` 이 한 번 더 붙습니다.
값 셀 (vk) 에서 데이터 위치를 찾는 법은 [하이브 내부 구조](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md) 에 있습니다.

아래는 위 예시 장치를 가정해 명세대로 만든 108바이트입니다.

```text
00000000  55 00 53 00 42 00 5C 00 56 00 49 00 44 00 5F 00  U.S.B.\.V.I.D._.
00000010  31 00 32 00 33 00 34 00 26 00 50 00 49 00 44 00  1.2.3.4.&.P.I.D.
00000020  5F 00 35 00 36 00 37 00 38 00 26 00 52 00 45 00  _.5.6.7.8.&.R.E.
00000030  56 00 5F 00 30 00 31 00 30 00 30 00 00 00 55 00  V._.0.1.0.0...U.
00000040  53 00 42 00 5C 00 56 00 49 00 44 00 5F 00 31 00  S.B.\.V.I.D._.1.
00000050  32 00 33 00 34 00 26 00 50 00 49 00 44 00 5F 00  2.3.4.&.P.I.D._.
00000060  35 00 36 00 37 00 38 00 00 00 00 00              5.6.7.8.....
```

| 범위 | 내용 |
|---|---|
| 0x00 ~ 0x3D | `USB\VID_1234&PID_5678&REV_0100` 과 끝 표시 `00 00` |
| 0x3E ~ 0x69 | `USB\VID_1234&PID_5678` 과 끝 표시 `00 00` |
| 0x6A ~ 0x6B | 목록 끝 표시 `00 00` |

### 읽는 순서

1. `Select` 키에서 컨트롤셋을 고릅니다.
2. `Enum\USB` 아래 VID·PID 키를 모두 적습니다. 루트 허브는 따로 표시합니다.
3. 인스턴스 ID 마다 일련번호인지, 시스템이 만든 값인지 적습니다.
4. `Service`·`CompatibleIDs` 로 장치 종류를 적습니다.
5. `ContainerID` 가 같은 키끼리 묶어 물리 장치 단위로 정리합니다.
6. 저장장치는 USBSTOR 인스턴스 ID 와 일련번호를 맞춥니다. USBSTOR 인스턴스 ID 는 일련번호 뒤에 `&0` 같은 꼬리가 붙은 꼴이 많습니다. 긴 일련번호가 잘리거나 `&0` 이 없는 이름도 있으니 `ContainerID` 도 함께 맞춥니다. → [USBSTOR](usbstor.md)
7. `Control\usbflags` 에서 `IgnoreHWSerNum` 설정을 확인합니다.

### 공개 도구로 한 번

- 하이브 뷰어 (예: Registry Explorer) 로 SYSTEM 하이브를 열고 `Enum\USB` 를 펼칩니다.
- 열기 전에 트랜잭션 로그 (.LOG1·.LOG2) 를 반영할지 정합니다. 반영하는지에 따라 보이는 키가 다를 수 있습니다.
- 스크립트형 도구 (예: RegRipper) 로 같은 하이브에서 장치 목록을 따로 뽑습니다.
- 두 결과의 VID·PID·인스턴스 ID 개수를 맞춰 봅니다. → [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [USB 저장장치 목록 (USBSTOR)](usbstor.md) | 일련번호, 제조사·제품 문자열 |
| [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md) | 설치·마지막 연결·해제 시각 |
| [장치 설치 로그 (setupapi.dev.log)](setupapi-dev-log.md) | 같은 장치 인스턴스 ID 가 처음 설치된 시각 |
| [드라이브 문자 매핑 (MountedDevices)](mounteddevices.md) | 저장장치에 붙은 드라이브 문자 |
| [사용자별 장치 연결 (MountPoints2)](mountpoints2.md) | 어느 사용자 계정에 남았는지 |
| [휴대용 장치·볼륨 이름 기록 (WPD·EMDMgmt)](wpd-emdmgmt.md) | 스마트폰 이름, 볼륨 이름, 볼륨 일련번호 |
| [USBSTOR 에 안 남는 장치 (UASP·SCSI·SD 카드)](uasp-scsi-sd.md) | `Service` 가 `UASPStor` 인 장치의 디스크 기록 |
| [장치 항목 (InventoryDevicePnp)](../../execution/amcache-hve/inventorydevicepnp.md) | 레지스트리와 따로 남은 장치 기록 |
| [외부 장치 연결 이벤트](../../event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) | 연결 이벤트의 시각 |
| [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 예전 SYSTEM 하이브에만 있는 장치 |

USB 흔적 전체의 읽는 순서는 [USB 저장장치 흔적](index.md) 에 있습니다.
조사 흐름은 [USB 로 무엇을 가져갔나](../../../04-scenarios/exfiltration/data-exfiltration/usb.md) 와 [스마트폰으로 옮겼나](../../../04-scenarios/exfiltration/data-exfiltration/mtp-phone-link.md) 에서 이어집니다.

## 실습

USB 사용이 들어 있는 공개 검체 (예: NIST CFReDS 의 Data Leakage Case) 에서 SYSTEM 하이브를 꺼내 아래 질문을 풀어 봅니다.

1. `Enum\USB` 아래 VID·PID 키는 몇 개입니까? 루트 허브와 내장 장치를 빼면 몇 개가 남습니까?
2. 인스턴스 ID 의 두 번째 글자가 `&` 인 장치는 무엇입니까? 그 장치가 일련번호를 보내지 않은 것인지, `IgnoreHWSerNum` 때문인지 가려 보십시오.
3. 같은 VID·PID 아래 인스턴스 키가 여러 개인 장치가 있습니까? 장치가 여러 개인지, 포트가 달랐는지 무엇으로 가릴 수 있습니까?
4. `Service` 가 `USBSTOR` 인 장치의 일련번호를 USBSTOR 인스턴스 ID 와 맞춰 보십시오. 맞지 않는 장치가 있다면 이유는 무엇입니까?
5. `ContainerID` 로 묶으면 물리 장치는 몇 개입니까?
6. 섀도 복사본이 있다면 예전 SYSTEM 하이브와 비교해 사라진 장치 키가 있습니까?

## 참고 문헌

- Microsoft Learn, "Standard USB Identifiers" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/standard-usb-identifiers
- Microsoft Learn, "Instance ID" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/instance-ids
- Microsoft Learn, "USB Device Registry Entries" (usbflags, IgnoreHWSerNum) — https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/usb-device-specific-registry-settings
- Microsoft Learn, "_USB_DEVICE_DESCRIPTOR (usbspec.h)" — https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/usbspec/ns-usbspec-_usb_device_descriptor
- Microsoft Learn, "How USB Devices are Assigned Container IDs" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/how-usb-devices-are-assigned-container-ids
- ForensicsWiki, "USB History Viewing" — https://forensics.wiki/usb_history_viewing/
