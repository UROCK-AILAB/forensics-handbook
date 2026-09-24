# 블루투스 장치 (BTHPORT)

## 한 줄 요약

SYSTEM 하이브의 `Services\BTHPORT\Parameters\Devices` 키에는 블루투스 장치가 주소마다 하위 키 하나로 남습니다. 하위 키에는 장치 이름, VID·PID, `LastSeen`·`LastConnected` 시각 같은 값이 있습니다. 관찰한 PC 한 대에서는 두 시각 값이 UTC 가 아니라 현지 시각이었습니다. 시각은 페어링 이벤트와 장치 속성 시각에 맞춰 본 뒤에 씁니다.

> 이 페이지에서 "관찰 PC" 는 Windows 11 Home 25H2(빌드 26200.9457), 시간대 Korea Standard Time(UTC+9) PC 한 대를 말합니다. 관찰 PC 에서 본 내용은 모두 "확인 범위: Win11 25H2 한 대" 입니다. 관찰 PC 의 장치 주소는 적지 않고 장치 A·B·C 로 부릅니다.

## 무엇을 기록하나 · 왜 생기나

블루투스 장치 하나는 `Devices` 아래 하위 키 하나이고, 하위 키 이름은 상대 장치의 블루투스 주소입니다. 16진수 12자리를 소문자로, 구분 기호 없이 적습니다(관찰 PC). 같은 주소가 System 로그에서는 콜론을 넣은 모양으로 나오는데, 예를 들어 키 이름이 `a1b2c3d4e5f6` 이면 로그에는 `a1:b2:c3:d4:e5:f6` 으로 적힙니다(관찰 PC, 주소는 만든 예시).

관찰 PC 에는 저전력 블루투스 (Bluetooth Low Energy, BLE) 장치 2개(A·B)와 일반 블루투스(BR/EDR) 장치 1개(C)가 있었습니다. 장치 A·B 는 이 키의 항목, `Enum\BTHLE` 키, System 로그의 페어링 성공 이벤트가 짝을 이뤄 나왔습니다. 그래서 페어링할 때 항목이 생긴다고 봅니다. 장치 C 는 이 키에만 있었고 Enum 쪽 키도, 페어링 이벤트도 없었는데, 그 시점의 System 로그가 남아 있었는지는 확인하지 않았습니다. 장치를 검색하기만 해도 항목이 생기는지는 확인하지 못했습니다.

## 위치와 버전별 차이

하이브 파일 위치와 `ControlSet00X` 를 고르는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)를 봅니다.

| 기록 | 하이브와 경로 | 주로 보는 것 |
|---|---|---|
| 장치 목록 | SYSTEM `ControlSet00X\Services\BTHPORT\Parameters\Devices\<주소>` | 하위 키 이름, 이름·시각·VID·PID 값 |
| 같은 키 (라이브) | `HKLM\SYSTEM\CurrentControlSet\Services\BTHPORT\Parameters\Devices` | 위와 같음 |
| BLE 장치 노드 | SYSTEM `ControlSet00X\Enum\BTHLE\Dev_<주소>` | 장치 인스턴스, 장치 속성 |
| BLE 서비스 노드 | SYSTEM `ControlSet00X\Enum\BTHLEDevice\{서비스 UUID}_Dev_VID&…_PID&…_REV&…_<주소>` | VID·PID·리비전 |
| 지속성 확인용 값 | SYSTEM `…\BTHPORT\Parameters\Radio Support` 의 `SupportDLL` | 불러오는 DLL |

- 공개 플러그인 RegRipper `bthport` 는 `Select` 키의 `Current` 값으로 현재 컨트롤셋 번호를 찾은 뒤 `Devices` 키를 읽습니다.
- 같은 플러그인은 `Radio Support` 키의 `SupportDLL` 값도 읽는데, 레지스트리 지속성 (persistence) 을 확인하려고 2017-01-29 판에서 넣은 항목입니다. 관찰 PC 에는 이 키가 없었습니다.
- 관찰 PC 의 `Parameters` 아래에는 `Devices` 말고도 하위 키가 12개 더 있었습니다. `ExceptionDB`, `HciBypassServices`, `Keys`, `LocalServices`, `PerDevices`, `PnpId`, `Restrictions`, `ServiceGroups`, `Services`, `SupportedServices`, `UnsupportedServices`, `Wdf` 입니다.
- `Keys` 키는 관리자 권한 PowerShell 로도 열리지 않았습니다. 오류는 "Requested registry access is not allowed" 였습니다(관찰 PC).
- `Keys` 에 페어링 키인 링크 키 (link key) 가 있다는 설명이 널리 알려져 있습니다. 이 글에서는 확인하지 못했습니다.
- 관찰 PC 에는 `Enum\BTHENUM` 키가 없었습니다. `Enum\BTH` 아래에는 `MS_BTHBRB`, `MS_BTHLE`, `MS_BTHPAN`, `MS_RFCOMM` 이 있었습니다.

| Windows | 확인한 내용 | 근거 |
|---|---|---|
| XP SP3 · Vista · 7 · 8 · 8.1 | RegRipper `bthport` 의 대상 OS 표시에 들어 있습니다. 판마다 값 구성이 어떻게 다른지는 확인하지 못했습니다. | RegRipper |
| 10 | 같은 플러그인이 2018-07-05 판에서 Windows 10 지원을 더했습니다. | RegRipper |
| 11 25H2 | 이 페이지의 값 목록과 시각 관찰은 이 판 PC 한 대에서 나왔습니다. | 관찰 PC |

## 구조

### 장치 키의 값

관찰 PC 의 세 장치에서 본 값입니다. 값마다 뜻을 정한 공개 명세는 이 글에서 확인하지 못했습니다.

| 값 | 있던 장치 | 관찰 PC 에서 본 종류·내용 |
|---|---|---|
| `LastSeen`, `LastConnected` | A·B·C | REG_QWORD 8바이트, FILETIME 모양. 기준 시각은 "시각 해석" 절을 봅니다. |
| `FriendlyName` | A·B·C | 세 장치 모두 `00` 한 바이트(빈 값) |
| `FingerprintString`, `FingerprintVersion`, `FingerprintTimestamp` | A·B·C | 뜻을 확인하지 못했습니다. |
| `LmpVersion`, `LmpSubversion`, `ManufacturerId`, `DibServiceVersion` | A·B·C | 뜻을 확인하지 못했습니다. |
| `Name`, `LEName` | A·B | REG_BINARY. ASCII 글자 뒤에 `00` 이 붙습니다. |
| `VID`, `PID`, `VIDType`, `Version` | A·B | 아래 "VID·PID 맞춰 보기" |
| `LEAppearance`, `LEAddressType`, `LeContainerId`(16바이트), `LeContainerIDSource`, `LocalEvaldIoCapLE` | A·B | 뜻을 확인하지 못했습니다. |
| `LMPFeatures`, `HostSupportedFeaturesMap`, `LocalEvaldIoCap` | C | 장치 C 에는 `Name` 이 없었습니다. |
| `COD` | B·C | C 는 2752780(0x2A010C), B 는 0 이었습니다. 비트 해석은 확인하지 못했습니다. |

RegRipper 는 `Name` 을 장치 이름으로 출력합니다. 한글처럼 ASCII 가 아닌 이름이 어떤 인코딩으로 들어가는지, 사용자가 붙인 이름이 `FriendlyName` 에 들어가는지는 확인하지 못했습니다.

각 장치 키 아래에는 `ServicesFor<16진수 12자리>` 하위 키가 하나씩 있었고, 이 이름 뒤 12자리는 세 장치 모두 같았습니다. PC 쪽 어댑터 주소로 보이지만 확인하지 못했습니다.

### VID·PID 맞춰 보기

`VID`·`PID` 는 10진 DWORD 로 저장되고(관찰 PC), 16진으로 바꾸면 `Enum\BTHLEDevice` 하위 키 이름 속 VID·PID 와 맞습니다. 관찰 PC 의 장치 A 는 `VID` 13652(0x3554), `PID` 62771(0xF533) 이었고 키 이름에는 `VID&023554_PID&f533_REV&0001` 로 들어 있었습니다. 키 이름 속 PID 의 16진 글자는 소문자였습니다.

`VID&` 뒤 `02` 는 `VIDType` 값 2 와 같지만, `VIDType` 2 가 어떤 번호 체계를 뜻하는지는 확인하지 못했습니다. `REV&` 뒤 네 자리는 `Version` 값이어서, `Version` 1 은 `REV&0001`, 768(0x300) 은 `REV&0300` 이었습니다.

### 장치 속성

라이브 PC 에서는 장치 노드의 속성을 PnP API(cfgmgr32 `CM_Get_DevNode_PropertyW`)로 읽을 수 있습니다. 관찰 PC 에서 읽은 속성은 아래와 같습니다.

| 속성 | 속성 키 | 내용 |
|---|---|---|
| `DEVPKEY_Bluetooth_LastConnectedTime` | `{2BD67D8B-8BEB-48D5-87E0-6CDA3428040A}` 11 | FILETIME (속성 종류 0x10) |
| `DEVPKEY_Bluetooth_DeviceAddress` | 확인하지 못함 | 문자열. 주소 12자리 |
| `DEVPKEY_Bluetooth_DeviceFlags` | 확인하지 못함 | UInt32 |
| `DEVPKEY_Device_InstallDate` | `{83DA6326-97A6-4088-9453-A1923F573B29}` 100 | FILETIME |
| `DEVPKEY_Device_FirstInstallDate` | 같은 GUID, 번호는 확인하지 못함 | 시각 |
| `DEVPKEY_Device_LastArrivalDate` | `{83DA6326-97A6-4088-9453-A1923F573B29}` 102 | FILETIME |

`Enum\BTHLE\Dev_<주소>\<인스턴스>\Properties` 키는 관리자 권한으로도 열리지 않았습니다(관찰 PC). USB 장치는 이런 속성이 `Properties\{GUID}\<번호 16진 4자리>` 에 남으며, 규칙은 [USB 저장장치 흔적](usb-storage-artifacts/index.md)에서 다룹니다. 같은 규칙이라면 블루투스 장치의 `LastConnectedTime` 은 `000B`, `InstallDate` 는 `0064`, `LastArrivalDate` 는 `0066` 에 있지만, 블루투스 장치에서 이 위치를 직접 확인하지는 못했습니다.

## 증거로서 의미

### 증명하는 것

- 이 키의 항목, `Enum\BTHLE` 키, 페어링 성공 이벤트가 함께 있으면 이 PC 가 그 주소의 장치와 페어링한 적이 있습니다(관찰 PC 의 장치 A·B).
- 페어링 시각은 System 로그 BTHUSB 이벤트 8 의 기록 시각과 `DEVPKEY_Device_InstallDate` 로 정합니다. 관찰 PC 에서는 두 장치 모두 두 값이 0.1초 안쪽으로 맞았습니다.
- `Name`·`LEName` 과 VID·PID 로 어떤 장치인지 좁혀 볼 수 있습니다.

### 증명하지 못하는 것

- 블루투스로 파일을 보냈는지, 얼마나 보냈는지 알 수 없습니다. 파일 전송을 직접 적는 기록은 이 글에서 확인하지 못했습니다.
- 마지막 연결 시각을 `LastConnected` 로 정할 수 없습니다. 관찰 PC 에서 페어링 때 값이 그대로 남은 사례가 있습니다("시각 해석" 절).
- 이 키에 항목이 있다는 것만으로 페어링했다고 단정할 수 없습니다. 장치 C 처럼 다른 흔적이 없는 항목이 있습니다.
- 누가 페어링했는지 알 수 없습니다. SYSTEM 하이브는 사용자별 파일이 아닙니다.

### 보고서 문장 예

- 쓰지 않을 문장: "사용자는 2026-09-11 08:19 에 블루투스로 파일을 보냈다."
- 쓸 문장: "SYSTEM 하이브 BTHPORT 에 주소 ○○ 인 장치 항목이 있다. System 로그에 같은 주소의 페어링 성공 이벤트(BTHUSB 8)가 ○○(UTC) 에 있다. 이 기록은 이 PC 가 해당 장치와 페어링한 적이 있음을 보여 준다. 파일 전송 여부와 마지막 연결 시각은 이 기록만으로 정할 수 없다."

## 시각 해석

| 시각 | 위치 | 관찰 PC 에서 본 기준 | 무엇이 바뀔 때 바뀌나 |
|---|---|---|---|
| `LastSeen`, `LastConnected` | BTHPORT 장치 키 | 현지 시각(KST) | 규칙을 확인하지 못했습니다. `LastConnected` 가 페어링 뒤 연결에도 그대로인 사례가 있습니다. |
| `DEVPKEY_Bluetooth_LastConnectedTime` | 장치 속성 | 현지 시각(KST) | 조회 1분여 전의 연결이 적혀 있었습니다. |
| `DEVPKEY_Device_InstallDate` | 장치 속성 | UTC | 페어링 이벤트와 같은 순간이었습니다. |
| `DEVPKEY_Device_LastArrivalDate` | 장치 속성 | UTC | 마지막 부팅 18초 뒤 값이었습니다. |
| BTHUSB 이벤트 8 기록 시각 | System 로그 | UTC | 페어링 성공 |
| `FingerprintTimestamp` | BTHPORT 장치 키 | 확인하지 못함 | 확인하지 못함 |
| 장치 키 마지막 기록 시각 | BTHPORT 장치 키 | UTC | 연결 시각으로 쓸 수 있는지 확인하지 못했습니다. |

### 현지 시각이라고 본 근거 (관찰 PC, 장치 A)

1. System 로그 BTHUSB 이벤트 8 의 기록 시각은 2026-09-10 23:19:56.06 (UTC) 이었습니다. 메시지는 "The remote adapter (…) successfully paired with the local adapter." 입니다.
2. 같은 장치의 `DEVPKEY_Device_InstallDate` 원시값도 2026-09-10 23:19:56.06 이었습니다. 이벤트 8 과 같은 순간입니다.
3. 이 순간을 한국 시간(UTC+9)으로 바꾸면 2026-09-11 08:19:56 입니다.
4. BTHPORT `LastConnected` 원시값을 UTC 로 읽으면 2026-09-11 08:19:54.90 이고, `LastSeen` 은 08:19:55.06 입니다.
5. 두 값은 페어링 순간과 9시간 차이가 나는데, 9시간을 빼면 2초 안쪽으로 붙습니다.
6. 그래서 원시값 08:19:54 는 UTC 가 아니라 한국 시간 08:19:54 로 읽어야 앞뒤가 맞습니다.

`DEVPKEY_Bluetooth_LastConnectedTime` 도 현지 시각이었습니다. UTC 11:43:04 에 조회했을 때 원시값은 20:41:45 였는데, UTC 로 읽으면 9시간 가까이 뒤의 미래이고 한국 시간으로 읽으면 조회 1분여 전입니다. 같은 장치의 `DEVPKEY_Device_LastArrivalDate` 는 UTC 여서 원시값 2026-09-20 21:44:33 이 마지막 부팅 21:44:15(UTC) 뒤였습니다. 한 장치 노드 안에서도 PnP 공통 시각은 UTC 였고 블루투스 전용 시각은 현지 시각이었습니다.

장치 A 는 조회 1분여 전에 연결한 기록(`DEVPKEY_Bluetooth_LastConnectedTime`)이 있었는데도 BTHPORT `LastConnected` 는 페어링 때 값 그대로였습니다. 장치 B 는 `LastSeen`, `LastConnected`, `DEVPKEY_Bluetooth_LastConnectedTime` 원시값이 모두 134322957501039515 로 같았고, UTC 로 읽으면 2026-08-27 09:15:50 입니다. 장치 B 의 페어링 이벤트 8 은 2026-06-26 03:11:25.19(UTC), `InstallDate` 는 03:11:25.21 이었습니다. BTHPORT 값이 언제 바뀌는지(연결이 끊길 때, 종료할 때 등)는 확인하지 못했습니다.

### 읽는 법

1. FILETIME 모양이라고 UTC 로 단정하지 않습니다. 값을 읽는 법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다.
2. 같은 주소의 페어링 이벤트 8 과 `InstallDate` 를 찾아 원시값과의 차이를 잽니다.
3. 차이가 시간대 오프셋과 같으면 현지 시각으로 적힌 값으로 봅니다.
4. 현지 시각이면 그 PC 의 시간대 설정(`TimeZoneInformation`)으로 UTC 로 바꿉니다. `Bias` 는 부호 있는 값으로 읽습니다. 자세한 내용은 [시간대 설정](../system-account/time-zone.md)에서 다룹니다.
5. 다른 Windows 판과 다른 PC 에서도 현지 시각인지는 확인하지 못했습니다. 검체마다 2~3번을 다시 합니다.

## 함정과 한계

1. **FILETIME 모양이라 UTC 로 읽는 실수.** 관찰 PC 에서는 현지 시각이었습니다. 도구도 틀리게 보여 줄 수 있습니다. PowerShell `Get-PnpDeviceProperty` 는 `DEVPKEY_Bluetooth_LastConnectedTime` 을 UTC 로 보고 9시간을 더했습니다. 그 결과 조회 시점보다 미래인 2026-09-24 05:41:45 를 보여 줬습니다.
2. **`LastConnected` 를 마지막 연결 시각으로 읽는 실수.** 장치 A 는 뒤에 다시 연결했는데도 페어링 때 값이 그대로였습니다.
3. **항목만 보고 페어링을 단정하는 실수.** 장치 C 는 Enum 키와 페어링 이벤트가 없었습니다. 다른 흔적과 짝이 맞는지 먼저 봅니다.
4. **값 종류.** RegRipper 요약본에는 `Name` 이 문자열로 적혀 있었습니다. 관찰 PC 에서 실제 종류는 REG_BINARY 였습니다. 도구 출력에 이름이 없거나 깨지면 바이트를 직접 봅니다.
5. **주소 표기.** 레지스트리는 구분 기호 없는 소문자이고, 이벤트 로그는 콜론을 넣습니다. 검색할 때 두 모양을 모두 씁니다.
6. **라이브 수집 권한.** `Parameters\Keys` 와 `Enum\BTHLE\…\Properties` 는 관리자 권한으로도 열리지 않았습니다. 하이브 사본을 떠서 읽는 방법을 씁니다. 이때 이 키들이 모두 읽히는지는 이 글에서 확인하지 못했습니다.
7. **Enum 흔적이 없는 장치.** 관찰 PC 에는 `Enum\BTHENUM` 이 없었고, 장치 C 는 Enum 쪽 키가 없었습니다. Enum 에 없다고 BTHPORT 항목을 버리지 않습니다.
8. **이벤트 로그의 잡음.** 관찰 PC 의 System 로그에는 BTHUSB 이벤트 12(142건)와 18(53건)이 많았습니다. 12 는 "The local adapter returned an improper ACL data packet which was discarded." 입니다. 18 은 링크 키를 PC 어댑터에 저장할 수 없다는 메시지입니다. 페어링 성공은 8(2건)입니다.
9. **꺼져 있거나 비어 있는 채널.** 관찰 PC 에서 `Microsoft-Windows-Bluetooth-BthLEPrepairing/Operational` 과 `Bluetooth-MTPEnum/Operational` 은 켜져 있었지만 0건이었습니다. `Bluetooth-Policy/Operational` 과 `Bluetooth-Bthmini/Operational` 은 꺼져 있었습니다.
10. **로그 보존.** 오래된 페어링 이벤트는 System 로그에서 밀려났을 수 있습니다. 이벤트가 없으면 로그가 그 시점까지 남아 있는지 먼저 확인합니다.
11. **지속성 확인.** `Radio Support` 의 `SupportDLL` 값이 있으면 그 DLL 이 무엇인지 봅니다. 자동실행 전반은 [악성코드 지속성(자동실행) 찾기](../../04-scenarios/incident/persistence.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

1. SYSTEM 하이브와 `.LOG1`·`.LOG2` 를 사본으로 확보합니다.
2. `Select` 키의 `Current` 값으로 컨트롤셋 번호를 정합니다.
3. `ControlSet00X\Services\BTHPORT\Parameters\Devices` 아래 하위 키 이름(주소)을 모두 적습니다.
4. 장치마다 `LastSeen`·`LastConnected` 데이터 8바이트를 리틀 엔디언 정수로 읽어 FILETIME 으로 바꿉니다.
5. `Name`·`LEName` 데이터는 ASCII 로 읽습니다.
6. `VID`·`PID` 를 16진으로 바꿔 `Enum\BTHLEDevice` 하위 키 이름과 맞춥니다.
7. System 로그에서 콜론을 넣은 주소로 BTHUSB 이벤트 8 을 찾습니다.

아래는 관찰 PC 에서 본 값 종류와 이름 규칙대로 만든 예시입니다. 검체에서 나온 값이 아닙니다.

```
장치 키 이름            a1b2c3d4e5f6
이벤트 로그 속 모양      a1:b2:c3:d4:e5:f6

값          데이터 바이트                  읽은 값
Name        42 54 2D 4D 4F 55 53 45 00     "BT-MOUSE" + 끝 00
LastSeen    00 5C 13 85 01 86 DC 01        0x01DC860185135C00 = 134129430000000000
VID         34 12 00 00                    4660 = 0x1234
PID         CD AB 00 00                    43981 = 0xABCD
```

- FILETIME 134129430000000000 을 UTC 로 읽으면 2026-01-15 09:30:00 입니다.
- 이 값이 관찰 PC 처럼 현지 시각(UTC+9)으로 적힌 것이라면 실제 UTC 는 2026-01-15 00:30:00 입니다.
- `VIDType` 이 2, `Version` 이 1 이라면 BLE 서비스 노드 키 이름은 `…_Dev_VID&021234_PID&abcd_REV&0001_a1b2c3d4e5f6` 모양이 됩니다.

### 공개 도구로 한 번

- RegRipper `bthport` 플러그인은 `Devices` 아래 장치마다 `Name` 을 출력합니다. `LastSeen`·`LastConnected` 는 8바이트를 FILETIME 으로 바꿔 출력합니다.
- 플러그인은 8바이트를 DWORD 두 개로 읽습니다. 바이트 배열로 읽은 값과 결과가 같습니다.
- 플러그인은 2020-05-17 판에서 날짜 출력 형식을 바꿨습니다. 판에 따라 출력 모양이 다를 수 있습니다.
- 도구가 시각을 어떤 기준으로 표시하든 원시값의 기준은 "읽는 법" 절대로 따로 정합니다.
- 라이브 PC 에서는 PowerShell `Get-PnpDeviceProperty` 로 장치 속성을 볼 수 있습니다. 함정 1번처럼 표시된 시각을 그대로 옮기지 않습니다.
- 이벤트 로그 뷰어에서 System 로그를 공급자 BTHUSB, 이벤트 ID 8 로 거릅니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 | 링크 |
|---|---|---|
| System 로그 BTHUSB 이벤트 8 | 페어링 시각(UTC), 콜론을 넣은 주소 | [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md) |
| `Enum\BTHLE`·`Enum\BTHLEDevice` | 주소, VID·PID·리비전 | [USB 저장장치 흔적](usb-storage-artifacts/index.md) (Enum 키와 장치 속성 읽는 법) |
| 장치 속성 `InstallDate`·`LastArrivalDate` | 페어링 시각, 마지막 도착 시각 | [USB 저장장치 흔적](usb-storage-artifacts/index.md) |
| 시간대 설정 | 현지 시각을 UTC 로 바꿀 `Bias` | [시간대 설정](../system-account/time-zone.md) |
| 켜짐·꺼짐 기록 | `LastArrivalDate` 와 부팅 시각 | [켜짐·꺼짐](../event-logs/power-on-off-events.md) |
| 다른 외부 장치 연결 | 같은 시간대의 다른 장치 연결 | [외부 장치 연결 이벤트](../event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) |

- 여러 시각을 한 줄로 늘어놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md)을 봅니다. 시간대가 다른 시각을 섞을 때 특히 조심합니다.
- 블루투스나 휴대폰으로 자료를 옮겼는지 묻는 흐름은 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md)에서 다룹니다.

## 실습

블루투스 장치 기록이 있는 공개 검체를 고르거나, 시험 PC 에 장치를 한 번 페어링한 뒤 풀어 봅니다. 검체 설명에서 OS 판과 시간대를 먼저 확인합니다.

1. `Devices` 아래 주소를 모두 적습니다. 각 주소가 `Enum\BTHLE` 에도 있습니까?
2. 주소마다 System 로그의 BTHUSB 이벤트 8 을 찾습니다. 이벤트가 없는 장치는 어떻게 해석하겠습니까?
3. `LastConnected` 원시값을 UTC 로 읽은 값과 이벤트 8 시각의 차이를 잽니다. 차이가 시간대 오프셋과 같습니까?
4. 장치를 한 번 더 연결합니다. `LastSeen`, `LastConnected`, `DEVPKEY_Bluetooth_LastConnectedTime` 가운데 어느 값이 바뀝니까?
5. `VID`·`PID` 를 16진으로 바꿔 `Enum\BTHLEDevice` 키 이름과 맞춥니다. 맞지 않는 장치가 있습니까?

## 참고 문헌

1. Harlan Carvey, RegRipper 3.0 플러그인 소스 `bthport.pl` (요약본으로 열람). https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/bthport.pl
