---
title: "연결·해제 시각"
parent: "USB 저장장치 흔적"
grand_parent: "아티팩트 · 외부 장치"
nav_order: 1500
---

# 연결·해제 시각 (DeviceClasses·Device Properties 0064·0066·0067)

## 한 줄 요약

Windows 8 부터는 USB 저장장치를 마지막으로 꽂은 시각과 마지막으로 뺀 시각이 장치 속성 값으로 남습니다. 자리는 SYSTEM 하이브 `Enum\USBSTOR` 장치 키 아래 `Properties\{83da6326-97a6-4088-9453-a1923f573b29}` 의 `0066`·`0067` 이고, 같은 자리의 `0064`·`0065` 에는 설치 시각이 남습니다. Windows 7 까지는 연결 시각 값이 따로 없었기 때문에 `Control\DeviceClasses` 아래 키의 마지막 기록 시각으로 연결 시각을 짐작했습니다.

## 무엇을 기록하나 · 왜 생기나

플러그 앤 플레이 관리자 (Plug and Play Manager) 는 장치 인스턴스마다 장치 속성 (Device Property) 을 저장합니다. 속성은 GUID 와 번호 한 쌍으로 구분하는데, 시각 속성 네 개는 GUID `{83da6326-97a6-4088-9453-a1923f573b29}` 를 함께 쓰고 번호는 10진 100~103 입니다. 레지스트리에는 이 번호를 16진 네 자리 키 이름으로 적기 때문에 100 은 `0064` 가 됩니다.

| 키 이름 | 번호 | 속성 이름 (Windows SDK `devpkey.h`) | 뜻 | 버전 |
|---|---|---|---|---|
| `0064` | 100 | `DEVPKEY_Device_InstallDate` | 이 장치 인스턴스를 **마지막으로** 설치한 때. 드라이버를 업데이트할 때마다 바뀝니다 | 7 이상 |
| `0065` | 101 | `DEVPKEY_Device_FirstInstallDate` | 이 장치 인스턴스를 **처음** 설치한 때. 드라이버를 업데이트해도 바뀌지 않습니다 | 7 이상 |
| `0066` | 102 | `DEVPKEY_Device_LastArrivalDate` | 장치가 마지막으로 연결(도착)된 때 | 8 이상 |
| `0067` | 103 | `DEVPKEY_Device_LastRemovalDate` | 장치가 마지막으로 제거된 때 | 8 이상 |

USB 저장장치는 처음 꽂을 때 설치 과정을 거치므로 `0065` 는 보통 처음 연결한 때와 가깝고, `0066`·`0067` 은 연결하고 뺄 때마다 다시 쓰입니다.

`Control\DeviceClasses` 는 장치 인터페이스 클래스 (Device Interface Class) 를 모아 둔 키입니다. 저장장치가 연결되면 디스크 인터페이스와 볼륨 인터페이스가 등록되고, 등록된 인터페이스마다 하위 키가 하나씩 생깁니다. 이 하위 키에는 시각 값이 없어서 쓸 수 있는 시각은 키의 마지막 기록 시각뿐입니다.

## 위치와 버전별 차이

모든 경로는 SYSTEM 하이브 안에 있고, 오프라인 하이브에는 `CurrentControlSet` 이 없습니다. 어느 `ControlSet00X` 를 볼지는 [컨트롤셋 고르기](../../../01-foundations/database-log-formats/registry-hive/controlset-select.md)를 봅니다.

| 무엇 | 경로 |
|---|---|
| 장치 속성 시각 | `ControlSet00X\Enum\USBSTOR\Disk&Ven_<제조사>&Prod_<제품>&Rev_<판>\<인스턴스 ID>\Properties\{83da6326-97a6-4088-9453-a1923f573b29}\0064`~`0067` |
| 디스크 인터페이스 | `ControlSet00X\Control\DeviceClasses\{53f56307-b6bf-11d0-94f2-00a0c91efb8b}\##?#USBSTOR#Disk&Ven_...&Prod_...&Rev_...#<인스턴스 ID>#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}` |
| 볼륨 인터페이스 | `ControlSet00X\Control\DeviceClasses\{53f5630d-b6bf-11d0-94f2-00a0c91efb8b}\##?#STORAGE#RemovableMedia#<...>&RM#{53f5630d-b6bf-11d0-94f2-00a0c91efb8b}` 꼴 |

`{53f56307-...}` 는 디스크 인터페이스 클래스 (`GUID_DEVINTERFACE_DISK`) 이고, `{53f5630d-...}` 는 볼륨 인터페이스 클래스 (`GUID_DEVINTERFACE_VOLUME`) 입니다. 디스크 쪽 하위 키 이름에는 USBSTOR 장치 이름과 인스턴스 ID 가 그대로 들어가고, 볼륨 쪽 하위 키 이름에는 부모 ID 접두사 (ParentIdPrefix) 가 들어갈 수 있습니다. 이 값으로 드라이브 문자 기록과 잇는 방법은 [드라이브 문자 매핑](mounteddevices.md)에서 다루고, 장치 이름과 인스턴스 ID 읽는 법은 [USB 저장장치 목록](usbstor.md)을 봅니다.

같은 속성 GUID 는 `Enum` 아래 다른 장치 인스턴스 키에도 있습니다. 예를 들어 같은 USB 저장장치의 `Enum\USB\VID_xxxx&PID_xxxx\<일련번호>` 키에도 `Properties` 가 있습니다([USB 장치 식별자](enum-usb-vid-pid.md)).

| 항목 | XP·Vista | 7 | 8 이후 (8.1·10·11) |
|---|---|---|---|
| `0064`·`0065` | 지원 버전 밖 (7 이상에서 지원) | 있음. `0064\00000000` 키의 `Data` 값 | 있음. `0064` 키의 기본값 `(Default)` |
| `0066`·`0067` | 없음 | 없음 | 있음. 기본값 `(Default)` |
| `DeviceClasses` 인터페이스 키 | 있음 | 있음 | 있음 |
| 마지막 연결 시각을 구하는 주된 방법 | 여러 키의 마지막 기록 시각 | 여러 키의 마지막 기록 시각 | `0066` 값 |

## 구조

`Properties` 키 아래는 다음처럼 생겼습니다(Windows 8 이후).

```
Enum\USBSTOR\Disk&Ven_<제조사>&Prod_<제품>&Rev_<판>\<인스턴스 ID>
└─ Properties
   ├─ {83da6326-97a6-4088-9453-a1923f573b29}
   │  ├─ 0064   (Default) = FILETIME 8바이트
   │  ├─ 0065   (Default) = FILETIME 8바이트
   │  ├─ 0066   (Default) = FILETIME 8바이트
   │  └─ 0067   (Default) = FILETIME 8바이트   ← 없을 수 있음
   └─ {다른 속성 GUID} ...
```

- 값 데이터는 8바이트 FILETIME 입니다. 리틀 엔디언으로 읽습니다.
- Windows 7 에서는 한 단계가 더 있습니다. `0064\00000000` 키 아래 `Data` 값에 FILETIME 이 들어 있습니다.
- `Properties` 아래에는 다른 GUID 의 속성도 있습니다. 모두 시각은 아닙니다.
- 값 형식 칸에는 `REG_*` 목록에 없는 수가 들어 있을 수 있습니다. 하이브 형식 명세는 미리 정하지 않은 형식 값도 허용합니다. 그래서 보기 도구에 따라 이 값이 알 수 없는 형식이나 이진 값으로 보입니다.

키와 값이 하이브 안에서 어떻게 저장되는지는 [하이브 내부 구조](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)에서 다룹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 제조사·제품·인스턴스 ID 의 저장장치가 이 PC 에 연결된 적이 있습니다 | 연결된 횟수와 그때그때의 시각. 마지막 한 번만 남습니다 |
| `0066`: 시스템이 이 장치의 도착을 마지막으로 처리한 때 | `0066` 이 사람이 손으로 꽂은 때인지. 장치를 꽂은 채 다시 시작해도 바뀝니다 |
| `0067`: 시스템이 켜진 상태에서 이 장치가 마지막으로 빠진 때 | `0067` 이 없을 때 장치를 언제 뺐는지 |
| `0065`: 이 장치 인스턴스를 처음 설치한 때 | 누가 꽂았는지. 어느 사용자로 쓰였는지 |
| | 어떤 파일을 읽거나 복사했는지 |

사용자와 드라이브 문자는 이 값으로 알 수 없습니다. 사용자는 [사용자별 장치 연결](mountpoints2.md)에서 찾습니다.

보고서에는 기록이 말하는 만큼만 씁니다.

- 쓸 수 있는 문장: "일련번호 ○○ 인 저장장치의 마지막 연결 기록 시각은 2025-05-12 01:23:45 UTC 이고, 마지막 제거 기록 시각은 같은 날 02:10:07 UTC 입니다."
- 쓰면 안 되는 문장: "피의자가 2025-05-12 10:23 에 USB 를 꽂아 46분 동안 자료를 복사했습니다."

## 시각 해석

- 네 값 모두 FILETIME 입니다. 장치 속성의 시각은 UTC 로 두도록 권장돼 있습니다(`DEVPROP_TYPE_FILETIME`). RegRipper 같은 공개 파서도 UTC 로 풀어 보여 줍니다. 계산은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다.
- 시각은 그때의 시스템 시계에서 옵니다. 시계를 바꿔 두었다면 이 값도 틀린 시계를 따릅니다([시스템 시각을 바꿨나](../../../04-scenarios/activity/anti-forensics/system-time-change.md)).

Yogesh Khatri 의 Windows 8 시험(2013)에서 `0066`·`0067` 은 다음처럼 바뀌었습니다.

| 동작 | `0066` (마지막 연결) | `0067` (마지막 제거) |
|---|---|---|
| 장치를 꽂음 | 지금 시각으로 씁니다 | 있던 값을 지웁니다 |
| 켜진 상태에서 장치를 뺌 | 그대로 | 지금 시각으로 씁니다 |
| 장치를 꽂은 채 끔 | 그대로 | 그대로 (새로 쓰지 않습니다) |
| 장치를 꽂은 채 다시 시작 | 지금 시각으로 씁니다 | 있던 값을 지웁니다 |

(Windows 8 기준. Windows 10·11 에서는 다를 수 있습니다.)

> 그림 자리: 시간 축 위에 "꽂음 → 뺌 → 꽂음 → 꽂은 채 재시작 → 꽂은 채 종료" 를 차례로 놓고, 각 시점마다 `0066`·`0067` 값이 어떻게 바뀌는지 보여 줍니다.

이 규칙대로라면 다음처럼 읽습니다.

1. **`0067` 이 있으면** `0066` 보다 뒤여야 합니다. 두 값의 차이는 마지막 연결이 이어진 길이입니다.
2. **`0067` 이 없으면** 마지막 연결 뒤에 켜진 상태에서 뺀 기록이 없다는 뜻입니다. 수집 때 꽂혀 있었거나, 꽂은 채로 꺼졌을 수 있습니다. 마지막 종료 시각과 비교합니다([시스템 기본 정보](../../system-account/os-version-computer-name-install-date-shutdown-t.md)).
3. **`0066` 이 부팅 시각과 거의 같으면** 사람이 꽂은 때가 아닐 수 있습니다. 장치를 꽂은 채로 켜거나 다시 시작한 경우입니다. 부팅 기록과 비교합니다([켜짐·꺼짐](../../event-logs/power-on-off-events.md)).

`DeviceClasses` 키의 마지막 기록 시각은 뜻이 더 느슨합니다. XP 시절 자료에는 이 시각을 "마지막 연결 시각(마지막 부팅 동안의 첫 연결)" 으로 보는 해석이 있습니다. 키의 마지막 기록 시각은 그 키에 무언가 바뀐 때일 뿐입니다([키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md)). 새 버전에서는 `0066` 을 먼저 보고, `DeviceClasses` 시각은 보조 단서로만 씁니다.

## 함정과 한계

1. **`0064` 를 "처음 설치" 로 잘못 읽기 쉽습니다.** `devpkey.h` 에서 `0064` 는 마지막 설치 시각이고, `0065` 가 처음 설치 시각입니다. 그런데 요약 자료와 도구 가운데 `0064` 를 "첫 설치" 로 적는 것이 있습니다. 예를 들어 RegRipper 의 `usbstor` 플러그인(2020-05-15 판)은 `0064` 를 "First InstallDate", `0065` 를 "InstallDate" 로 표시합니다. 두 값은 보통 같아서 차이가 잘 드러나지 않습니다. 드라이버를 다시 설치하거나 업데이트하면 `0064` 만 바뀝니다. 처음 연결 시각은 `0065` 로 적습니다.
2. **마지막 한 번만 남습니다.** 그 전 연결은 이 값으로 알 수 없습니다. 연결마다 남는 기록은 [외부 장치 연결 이벤트](../../event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md)에서 찾습니다. 옛 값은 섀도 복사본 안의 하이브에 남아 있을 수 있습니다([섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)).
3. **Windows 7 이하에는 `0066`·`0067` 이 없습니다.** 값이 없다고 도구 오류나 삭제로 보면 안 됩니다. 먼저 OS 버전을 확인합니다.
4. **USBSTOR 에 안 남는 장치가 있습니다.** UASP 로 연결된 장치나 일부 SD 카드는 USBSTOR 가 아닌 다른 자리에 남습니다([USBSTOR 에 안 남는 장치](uasp-scsi-sd.md)). 스마트폰 같은 휴대용 장치는 [휴대용 장치·볼륨 이름 기록](wpd-emdmgmt.md)을 봅니다.
5. **일련번호가 없는 장치는 구별이 어렵습니다.** 이때 인스턴스 ID 는 Windows 가 만든 값입니다. 같은 모델의 다른 장치와 구별하기 어렵습니다([USB 저장장치 목록](usbstor.md)).
6. **가장 새 값이 트랜잭션 로그에만 있을 수 있습니다.** Windows 8.1 부터는 하이브 파일 쓰기가 늦어질 수 있습니다. 수집 직전의 연결·제거는 로그를 반영해야 보입니다([트랜잭션 로그와 반영 안 된 변경](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md)).
7. **흔적을 지우는 도구가 있습니다.** USB 기록을 지우는 공개 도구는 `Enum\USBSTOR` 나 `DeviceClasses` 의 해당 키를 지울 수 있습니다. 지운 키의 셀이 하이브 안에 남아 있을 수 있습니다([지워진 키·값 복구](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md)). 값만 바꾸면 그 키(`0066` 등)의 마지막 기록 시각이 바꾼 때로 바뀝니다. 키 시각까지 따로 조작하지 않았을 때 이야기입니다. 값 안의 시각과 키 시각이 크게 다르면 의심합니다. 지우기 흔적 전반은 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 형식 명세로 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

1. `Select` 키로 현재 컨트롤셋을 고릅니다.
2. `Enum\USBSTOR` 아래에서 장치 키와 인스턴스 ID 키를 찾습니다.
3. `Properties\{83da6326-97a6-4088-9453-a1923f573b29}\0066` 키의 기본값(이름 없는 값)을 찾습니다. 값 셀이 가리키는 데이터 8바이트를 읽습니다.

```
0066 기본값 데이터:  80 A6 F9 80 DC C2 DB 01
0067 기본값 데이터:  80 29 2D FB E2 C2 DB 01
```

4. `0066` 을 리틀 엔디언으로 읽으면 0x01DBC2DC80F9A680 입니다.
5. 10진으로는 133,914,866,250,000,000 입니다. 1601-01-01 00:00:00 UTC 부터 100나노초 단위로 센 값입니다.
6. 초로 바꾸면 13,391,486,625초입니다. 날짜로는 2025-05-12 01:23:45 UTC 입니다. 한국 시각(UTC+9)으로는 같은 날 10:23:45 입니다.
7. `0067` 은 0x01DBC2E2FB2D2980 입니다. 날짜로는 2025-05-12 02:10:07 UTC 입니다.
8. 두 값의 차이는 2,782초, 곧 46분 22초입니다. `0067` 이 `0066` 보다 뒤이므로 위 시각 해석 규칙과 맞습니다.

Windows 7 하이브라면 3단계에서 `0064\00000000` 키의 `Data` 값을 읽습니다. `0066`·`0067` 키는 없습니다.

### 공개 도구로 한 번

RegRipper 의 `usbstor`·`devclass` 플러그인, Registry Explorer, python-registry, yarp 같은 공개 도구로 같은 값을 읽을 수 있습니다. 도구를 쓸 때는 다음을 확인합니다.

- 도구가 `0064`·`0065` 에 붙인 이름표가 `devpkey.h` 와 같은지 확인합니다(함정 1).
- 시각을 UTC 로 보여 주는지, 분석 PC 의 현지 시각으로 바꿔 보여 주는지 확인합니다.
- 트랜잭션 로그를 반영하고 읽었는지 확인합니다.
- 장치 하나를 골라 헥스로 읽은 값과 맞춰 봅니다([도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)).

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| USBSTOR 장치 키 | 제조사·제품·인스턴스 ID. 이 페이지 시각이 어느 장치 것인지 | [USB 저장장치 목록](usbstor.md) |
| Enum\USB | VID·PID·일련번호. 같은 장치의 부모 인스턴스 속성 | [USB 장치 식별자](enum-usb-vid-pid.md) |
| setupapi.dev.log | 처음 설치 기록(현지 시각). `0065` 와 비교합니다 | [장치 설치 로그](setupapi-dev-log.md) |
| 외부 장치 연결 이벤트 | 연결마다 남는 이벤트. 마지막 한 번 말고 그 전 연결 | [외부 장치 연결 이벤트](../../event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) |
| MountedDevices | 드라이브 문자와 볼륨 | [드라이브 문자 매핑](mounteddevices.md) |
| MountPoints2 | 어느 사용자 로그온 중에 볼륨이 보였는지 | [사용자별 장치 연결](mountpoints2.md) |
| AmCache 장치 항목 | 장치 설치 정보의 다른 사본 | [장치 항목](../../execution/amcache-hve/inventorydevicepnp.md) |
| 켜짐·꺼짐 이벤트 | `0066` 이 부팅 때 쓰였는지, `0067` 이 왜 없는지 | [켜짐·꺼짐](../../event-logs/power-on-off-events.md) |

전체 조사 흐름은 [USB 로 무엇을 가져갔나](../../../04-scenarios/exfiltration/data-exfiltration/usb.md)를 봅니다.

## 실습

NIST CFReDS 의 공개 검체(예: Data Leakage Case)에서 SYSTEM 하이브를 꺼내 풀어 봅니다.

1. OS 버전을 먼저 확인합니다. `0066`·`0067` 키가 있습니까? 없다면 왜 없는지 설명합니다.
2. USBSTOR 장치마다 `0064` 와 `0065` 를 비교합니다. 다른 장치가 있다면 무엇이 원인일 수 있습니까?
3. `DeviceClasses` 의 디스크 키와 볼륨 키 마지막 기록 시각을 장치별로 적습니다. setupapi.dev.log 의 설치 시각과 어떤 순서입니까?
4. `0067` 이 없는 장치가 있다면, 마지막 종료 시각과 `0066` 을 나란히 놓고 설명합니다.
5. 도구 두 개로 같은 장치를 읽고, `0064` 에 붙인 이름표가 같은지 비교합니다.

## 참고 문헌

- Microsoft Learn, "DEVPKEY_Device_InstallDate" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/devpkey-device-installdate
- Microsoft Learn, "DEVPKEY_Device_FirstInstallDate" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/devpkey-device-firstinstalldate
- Yogesh Khatri, "Windows 8 New Registry Artifacts Part 1 - New Device Timestamps", Swift Forensics (2013) — https://www.swiftforensics.com/2013/11/windows-8-new-registry-artifacts-part-1.html
- Yogesh Khatri, "Device LastRemovalDate & LastArrivalDate Behavior in Windows 8", Swift Forensics (2013) — https://www.swiftforensics.com/2013/12/device-lastremovaldate-lastarrivaldate.html
- Forensics Wiki, "USB History Viewing" — https://forensics.wiki/usb_history_viewing/
- Harlan Carvey, RegRipper 3.0 `usbstor.pl` 플러그인 — https://github.com/keydet89/RegRipper3.0/blob/master/plugins/usbstor.pl
