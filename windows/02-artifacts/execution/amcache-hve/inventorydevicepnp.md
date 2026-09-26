---
title: "장치 항목"
parent: "AmCache"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 910
---

# 장치 항목 (InventoryDevicePnp)

## 한 줄 요약

Amcache.hve 의 `Root\InventoryDevicePnp` 키에는 플러그 앤 플레이 (Plug and Play, PnP) 장치가 하나씩 하위 키로 남습니다. USB 저장장치의 VID·PID·일련번호·볼륨 이름을 SYSTEM 하이브와 다른 파일에서 한 번 더 확인할 때 씁니다. 연결 시각은 이 키만으로 알 수 없습니다.

## 무엇을 기록하나 · 왜 생기나

Windows 는 업그레이드한 뒤에도 장치와 드라이버가 호환되는지 판단하려고 PnP 장치와 드라이버 정보를 모읍니다. 같은 정보는 진단 데이터 이벤트 `Microsoft.Windows.Inventory.Core.InventoryDevicePnpAdd` 로도 나갑니다. Amcache.hve 하위 키의 값 이름은 이 이벤트의 필드 이름과 같습니다.

Windows 10 1607 기본 라이브러리에서는 예약 작업 Microsoft Compatibility Appraiser 가 돌 때만 장치 정보가 갱신됩니다(ANSSI). 그래서 장치를 꽂은 순간에 바로 기록된다고 볼 수 없습니다.

USB 장치만 들어가는 것도 아닙니다. 프로세서·디스플레이·블루투스·오디오·프린터·볼륨·디스크 같은 클래스가 두루 들어 있습니다(Zimmerman).

## 위치와 버전별 차이

| 항목 | 경로 |
|---|---|
| 파일 | `%WinDir%\AppCompat\Programs\Amcache.hve` (같은 폴더의 `.LOG1`·`.LOG2` 도 함께 수집) |
| 장치 항목 | `Root\InventoryDevicePnp\<장치 인스턴스 ID 를 바꾼 이름>` |
| 짝이 되는 키 | `Root\InventoryDeviceContainer\<컨테이너 ID>` |

형식은 Windows 버전이 아니라 호환성 라이브러리의 판을 따릅니다(ANSSI). 판별 키 구성은 [구조와 버전별 차이](structure-versions.md)에서 다룹니다. 이 키에 관련된 것만 추립니다.

| 라이브러리 판 (처음 실린 Windows) | InventoryDevicePnp | 근거 |
|---|---|---|
| 6.2·6.3 (Windows 8·8.1) | 키가 없습니다. 8.1 판은 연결된 장치 목록을 `FullCompatReport.xml` 에 적었습니다. | ANSSI |
| 10.0.14913 (Windows 10 1607) | `InventoryDevicePnp`·`InventoryDeviceContainer` 가 처음 보입니다. | ANSSI |
| 10.0.16299 (Windows 10 1709) | 공개 연구가 USB 흔적으로 이 키를 다루기 시작한 판입니다. | Zimmerman·df-stream (2017) |
| Windows 11 | 공개된 명세나 연구가 없습니다. 실제 데이터에서 키가 있는지부터 봅니다. | — |

라이브러리를 업데이트한 Windows 7·8.1 에도 같은 형식이 생길 수 있습니다(ANSSI).

## 구조

### 하위 키 이름

장치 하나가 하위 키 하나입니다. 하위 키 이름은 SYSTEM 하이브 `Enum` 의 장치 인스턴스 ID (Device Instance ID) 와 같은 모양입니다. 다만 모두 소문자이고 `\` 자리에 `/` 가 들어갑니다(df-stream).

USB 저장장치 하나를 꽂으면 하위 키가 네 개 생깁니다(df-stream).

```
usb/vid_{VID}&pid_{PID}/{일련번호 또는 UID}                         ← USB 장치
usbstor/disk&ven_{제조사}&prod_{모델}&rev_{리비전}/{일련번호 또는 UID}  ← 디스크 드라이브
swd/wpdbusenum/_??_usbstor#disk&ven_…&prod_…&rev_…#{일련번호 또는 UID}#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}  ← 휴대용 장치(WPD)
storage/volume/_??_usbstor#disk&ven_…&prod_…&rev_…#{일련번호 또는 UID}#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}  ← 볼륨
```

- 끝의 GUID 는 디스크 장치 인터페이스 GUID 입니다.
- 네 하위 키에는 같은 `ContainerId` 값이 들어 있습니다. 이 값으로 네 키를 한 장치로 묶습니다.
- 일련번호 자리에 Windows 가 만든 ID 가 들어가는 경우는 [USB 저장장치 목록 (USBSTOR)](../../external-devices/usb-storage-artifacts/usbstor.md)에서 다룹니다.

> 그림 자리: USB 저장장치 하나가 만든 하위 키 네 개가 `ContainerId` 로 `InventoryDeviceContainer` 하위 키 하나와 SYSTEM 하이브 `Enum\USBSTOR` 항목에 이어지는 모습

### 주요 값

뜻은 Microsoft 진단 데이터 문서(1809 판)의 필드 설명을 옮긴 것입니다.

| 값 | 뜻 | 분석에 쓰는 곳 |
|---|---|---|
| `ParentId` | 부모 장치의 인스턴스 ID | `usbstor/` 하위 키에서는 여기서 VID·PID·일련번호를 읽습니다(df-stream). |
| `ContainerId` | 한 물리 장치에 속한 기능 장치들을 묶는 GUID | 같은 장치의 하위 키들, `InventoryDeviceContainer`, SYSTEM 하이브 `Enum\USBSTOR` 를 잇습니다. |
| `Class`·`ClassGuid` | 장치 설치 클래스와 그 GUID | `usb`·`diskdrive`·`volume` 처럼 장치 종류를 가릅니다. |
| `Enumerator` | 장치를 찾아낸 버스 | |
| `Description`·`BusReportedDescription` | 장치 설명, 버스가 알려 준 장치 설명 | WPD 하위 키의 `Description` 에 볼륨 이름이 들어간 사례가 있습니다(df-stream). |
| `Manufacturer`·`Model` | 제조사, 모델 | |
| `HWID`·`COMPID`·`MatchingID` | 하드웨어 ID 목록, 호환 ID 목록, 설치에 실제로 쓴 ID | |
| `DriverName`·`Service` | 드라이버 이미지 파일 이름, 서비스 이름 | [드라이버 항목](inventorydriverbinary.md)과 잇습니다. |
| `Inf`·`DriverPackageStrongName` | INF 이름(`oemXX.inf` 로 바뀔 수 있음), 드라이버 패키지 이름 | `DriverPackageStrongName` 은 `InventoryDriverPackage`·`InventoryDriverBinary` 에도 있어 셋을 잇습니다(Zimmerman). |
| `DriverVerDate`·`DriverVerVersion` | 드라이버 날짜와 버전 | 장치를 꽂은 때와 관계없습니다. |
| `InstallState`·`ProblemCode`·`DeviceState` | 설치 상태, 오류 코드, 상태 비트 | 아래 "증명하지 못하는 것" 참고 |
| `InstallDate`·`FirstInstallDate` | 가장 최근에 설치한 날짜, 처음 설치한 때 | 아래 "시각 해석" 참고 |

### 짝이 되는 InventoryDeviceContainer

하위 키 이름이 컨테이너 ID 이고, `InventoryDevicePnp` 의 `ContainerId` 값이 이 이름을 가리킵니다(Zimmerman). 이 키에는 `FriendlyName`·`Manufacturer`·`ModelName`·`ModelNumber`·`Categories`·`IsConnected`·`IsPaired` 같은 값이 있어서, 사람이 읽기 좋은 장치 이름은 이쪽에서 찾습니다.

## 증거로서 의미

### 증명하는 것

- 인벤토리 작업이 돌 때 이 장치 인스턴스가 PnP 에 등록돼 있었습니다.
- 그러므로 그 전에 이 장치가 이 PC 에 한 번 이상 설치됐습니다.
- 장치를 가리키는 식별 정보가 남습니다. VID·PID, 제조사·모델 문자열, 일련번호(또는 Windows 가 만든 ID), 컨테이너 ID 입니다.
- 어떤 드라이버와 INF 로 설치됐는지 알 수 있습니다.
- 볼륨 이름이 WPD 하위 키에만 남은 사례가 있습니다. 다른 곳에서 볼륨 이름을 못 찾으면 여기서 찾아봅니다(df-stream).
- SYSTEM 하이브와 다른 파일입니다. 그래서 SYSTEM 하이브의 USB 흔적만 지운 경우에도 식별 정보가 남아 있을 수 있습니다.

### 증명하지 못하는 것

- 연결한 시각, 해제한 시각, 연결한 횟수를 알 수 없습니다.
- 누가 꽂았는지 알 수 없습니다. Amcache.hve 는 사용자별 파일이 아닙니다.
- 장치에서 파일을 복사하거나 열었는지 알 수 없습니다.
- 조사 시점에 장치가 꽂혀 있었는지 알 수 없습니다. `DeviceState` 의 "있음"(0x20) 비트는 지금은 늘 켜져 있고, "연결됨"(0x01) 비트는 컨테이너에만 씁니다(Microsoft 문서 22H2 판).
- 키가 없다고 해서 연결된 적이 없다는 뜻은 아닙니다. 가장 최근에 꽂은 장치 항목이 재시작 뒤 지워진 사례가 있습니다(df-stream). 인벤토리 작업이 아직 돌지 않았을 수도 있습니다.
- Amcache 에서는 항목이 "있다" 는 사실만 결론의 근거로 삼습니다(ANSSI).

### 보고서 문장 예

- 쓰지 않을 문장: "사용자는 이 USB 를 ○월 ○일에 연결했다."
- 쓸 문장: "Amcache.hve `InventoryDevicePnp` 에 VID ○○○○·PID ○○○○·일련번호 ○○○ 인 USB 저장장치 항목이 있다. 이 항목은 하이브가 갱신되기 전 어느 때에 이 장치가 이 PC 에 설치된 적이 있음을 보여 준다. 연결 시각은 이 항목만으로 정할 수 없다."

## 시각 해석

| 시각 | 무엇이 바뀔 때 바뀌나 | 기준 |
|---|---|---|
| 하위 키 마지막 기록 시각 | 인벤토리 작업이 항목을 다시 쓸 때 바뀝니다. 첫 연결 때도 바뀌지만, 연결·해제와 관계없는 때에도 바뀝니다(df-stream). 한 장치의 하위 키 네 개는 시각이 같습니다. | UTC, FILETIME ([키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md)) |
| `FirstInstallDate` 값 | 이 장치를 처음 설치한 때입니다(Microsoft 필드 설명). | 저장 형식은 아래 참고 |
| `InstallDate` 값 | 이 장치를 가장 최근에 설치한 날짜입니다(Microsoft 필드 설명). | 저장 형식은 아래 참고 |
| `DriverVerDate` 값 | 드라이버 패키지의 날짜입니다. 장치 사용과 관계없습니다. | 날짜만 |

- SYSTEM 하이브의 장치 속성에도 같은 이름의 값이 있습니다. `DEVPKEY_Device_InstallDate` 는 속성 번호 0064, `DEVPKEY_Device_FirstInstallDate` 는 0065 입니다.
- `FirstInstallDate` 속성은 드라이버를 업데이트해도 바뀌지 않습니다. `InstallDate` 속성은 드라이버를 업데이트할 때마다 바뀔 수 있습니다.
- Amcache 의 두 값이 이 속성을 그대로 옮긴 것인지, 저장 형식과 시간대가 무엇인지 밝힌 공개 명세는 없습니다.
- 그래서 두 값은 원시 바이트를 먼저 보고, SYSTEM 하이브의 속성 값과 맞춰 본 뒤에 씁니다. 속성 위치는 [연결·해제 시각](../../external-devices/usb-storage-artifacts/deviceclasses-device-properties-0064-0066-0067.md)에서 다룹니다.

## 함정과 한계

1. **키 시각을 연결 시각으로 쓰는 실수.** 공개 파서가 내는 "시각" 열이 하위 키 마지막 기록 시각인 경우가 있습니다. 한 공개 파서(AmcacheParser)는 소스에서 이 열에 하위 키 마지막 기록 시각을 넣습니다. 여러 장치가 같은 시각이면 인벤토리 작업이 한꺼번에 다시 쓴 흔적으로 봅니다.
2. **항목이 빨리 빠집니다.** USB 장치 항목이 금방 목록에서 빠지기도 합니다(df-stream). [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 속 옛 Amcache.hve, [지워진 키](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md), [트랜잭션 로그](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md)를 함께 봅니다.
3. **도구마다 내는 값이 다릅니다.** 앞의 공개 파서는 소스상 `InstallDate`·`FirstInstallDate`·`LocationPaths`·필터 값을 결과에 넣지 않습니다(2026-09 소스 기준). 이 값이 필요하면 원시 키를 봅니다.
4. **키 이름은 소문자입니다.** 일련번호나 모델명으로 찾을 때 대소문자를 가리지 않고 찾습니다.
5. **USB 가 아닌 항목이 대부분입니다.** `usb/`·`usbstor/`·`swd/wpdbusenum/`·`storage/volume/` 으로 시작하는 하위 키를 먼저 거릅니다.
6. **Microsoft 문서 판마다 설명이 다릅니다.** Windows 10 22H2·21H2 판 문서의 `InventoryDevicePnpAdd` 필드 설명은 표에서 한 칸씩 밀려 있습니다(2026년 9월 기준). 예를 들어 `ContainerId` 옆에 호환 ID 설명이 붙어 있습니다. 값의 뜻은 1809 판과 맞대어 봅니다.
7. **Amcache 공통 함정**은 [AmCache 해석 함정](sha1.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

1. Amcache.hve 와 `.LOG1`·`.LOG2` 를 사본으로 확보합니다. 로그 반영은 [트랜잭션 로그](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md)에서 다룹니다.
2. 조사할 장치의 일련번호를 정합니다. SYSTEM 하이브 `Enum\USBSTOR` 에서 가져옵니다.
3. 하이브에서 일련번호를 소문자 ASCII 로 찾습니다. 키 이름이 걸리면 그 셀이 하위 키의 nk 셀입니다.
4. 같은 일련번호를 UTF-16LE 로도 찾습니다. 대문자와 소문자를 모두 찾습니다. 값 데이터(`ParentId`·`HWID` 등)가 걸립니다.
5. nk 셀에서 값 목록을 따라가 vk 셀을 읽습니다. vk 셀 안에는 값 이름이 있고, 데이터는 따로 떨어진 셀에 있습니다. 셀 구조는 [하이브 내부 구조 (regf·hbin·Cell)](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)를 봅니다.
6. nk 셀에서 마지막 기록 시각(FILETIME)을 읽고 UTC 로 풉니다.

아래는 문자 인코딩 규칙으로 만든 예시입니다. 실제 데이터에서 나온 값이 아닙니다. 일련번호가 `AB12CD34` 라고 가정합니다.

```
찾는 것                    바이트                                              글자
키 이름 (ASCII, 소문자)     61 62 31 32 63 64 33 34                             "ab12cd34"
값 데이터 (UTF-16LE, 대문자) 41 00 42 00 31 00 32 00 43 00 44 00 33 00 34 00     "AB12CD34"
값 이름 (ASCII)             50 61 72 65 6E 74 49 64                             "ParentId"
```

### 공개 도구로 한 번

- 레지스트리 뷰어로 하이브를 열고 `Root\InventoryDevicePnp` 를 펼칩니다. 뷰어는 로그를 반영해 여는지 확인합니다.
- Amcache 전용 공개 파서(예: AmcacheParser)는 이 키를 따로 표로 냅니다. 표에서 USB 관련 하위 키를 거르고 `ContainerId` 로 묶습니다.
- 파서 결과에 빠진 값은 뷰어로 원시 키에서 확인합니다.
- 두 결과가 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 절차를 따릅니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 값 | 링크 |
|---|---|---|
| USBSTOR | 일련번호, 제조사·모델, `ContainerID` | [USB 저장장치 목록 (USBSTOR)](../../external-devices/usb-storage-artifacts/usbstor.md) |
| Enum\USB | VID·PID, `ParentId` | [USB 장치 식별자 (Enum\USB VID·PID)](../../external-devices/usb-storage-artifacts/enum-usb-vid-pid.md) |
| 장치 속성 0064·0065·0066·0067 | `InstallDate`·`FirstInstallDate`, 마지막 연결·해제 시각 | [연결·해제 시각](../../external-devices/usb-storage-artifacts/deviceclasses-device-properties-0064-0066-0067.md) |
| WPD·EMDMgmt | WPD 하위 키 `Description` 의 볼륨 이름 | [휴대용 장치·볼륨 이름 기록 (WPD·EMDMgmt)](../../external-devices/usb-storage-artifacts/wpd-emdmgmt.md) |
| MountedDevices | 드라이브 문자 | [드라이브 문자 매핑 (MountedDevices)](../../external-devices/usb-storage-artifacts/mounteddevices.md) |
| setupapi.dev.log | 장치를 처음 설치한 시각 | [장치 설치 로그 (setupapi.dev.log)](../../external-devices/usb-storage-artifacts/setupapi-dev-log.md) |
| 외부 장치 연결 이벤트 | 연결 시각 | [외부 장치 연결 이벤트](../../event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) |
| InventoryDriverBinary | `DriverPackageStrongName`·`Service` | [드라이버 항목](inventorydriverbinary.md) |
| 블루투스 장치 | 블루투스 클래스 항목 | [블루투스 장치 (BTHPORT)](../../external-devices/bthport.md) |

USB 흔적 전체 흐름은 [USB 저장장치 흔적](../../external-devices/usb-storage-artifacts/index.md)과 [USB 로 무엇을 가져갔나](../../../04-scenarios/exfiltration/data-exfiltration/usb.md)에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 자료 가운데 Windows 10 1709 이후 이미지를 골라 풀어 봅니다.

1. `InventoryDevicePnp` 에서 `usbstor/` 로 시작하는 하위 키를 모두 찾습니다. 같은 `ContainerId` 를 가진 하위 키를 묶으면 장치가 몇 개인가요?
2. 각 장치의 일련번호를 SYSTEM 하이브 `Enum\USBSTOR` 와 맞춰 봅니다. 한쪽에만 있는 장치가 있나요? 있다면 왜 그럴까요?
3. WPD 하위 키의 `Description` 과 SOFTWARE 하이브의 휴대용 장치 기록에 있는 볼륨 이름을 비교합니다.
4. 여러 장치 하위 키의 마지막 기록 시각을 나란히 놓습니다. 같은 시각이 몰려 있다면 무엇을 뜻하나요?
5. `FirstInstallDate` 원시 값을 SYSTEM 하이브 속성 0065 값과 비교합니다. 형식과 시간대가 같은가요?

## 참고 문헌

- Microsoft Learn, "Windows 10, version 1809 basic diagnostic events and fields" 의 `InventoryDevicePnpAdd` 절 — https://learn.microsoft.com/en-us/windows/privacy/basic-level-windows-diagnostic-events-and-fields-1809 · 같은 절의 22H2·21H2 판(`DeviceState` 비트 설명, 필드 설명이 밀린 판) — https://learn.microsoft.com/en-us/windows/privacy/required-windows-diagnostic-data-events-and-fields-2004
- Microsoft Learn, "DEVPKEY_Device_FirstInstallDate" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/devpkey-device-firstinstalldate
- Blanche Lagny (ANSSI), "Analysis of the AmCache" v2, 2019 — https://cyber.gouv.fr/documents/632/anssi-coriin_2019-analysis_amcache-v2.pdf
- Eric Zimmerman, "(Am)cache still rules everything around me (part 2 of 1)", binary foray, 2017 — https://binaryforay.blogspot.com/2017/10/amcache-still-rules-everything-around.html
- Digital Forensics Stream, "Amcache and USB Device Tracking", 2017 — https://df-stream.com/2017/10/amcache-and-usb-device-tracking/
- AmcacheParser 소스 `Amcache/AmcacheNew.cs` (2026-09 열람) — https://github.com/EricZimmerman/AmcacheParser/blob/master/Amcache/AmcacheNew.cs
