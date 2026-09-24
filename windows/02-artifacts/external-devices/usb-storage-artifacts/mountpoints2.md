# 사용자별 장치 연결 (MountPoints2)

## 한 줄 요약

MountPoints2 는 사용자 하이브(NTUSER.DAT)에 있는 키입니다. 그 사용자가 로그온해 있을 때 나타난 볼륨·네트워크 공유가 하위 키로 남습니다. SYSTEM 하이브에는 사용자 정보가 없으므로, USB 볼륨이 어느 사용자 세션에 나타났는지는 이 키로 좁힙니다.

## 무엇을 기록하나 · 왜 생기나

- 볼륨이 붙으면 마운트 관리자 (Mount Manager) 가 볼륨 GUID 를 붙이고 SYSTEM 하이브의 `MountedDevices` 에 적습니다([드라이브 문자 매핑 (MountedDevices)](/02-artifacts/external-devices/usb-storage-artifacts/mounteddevices.md)).
- 같은 볼륨 GUID 가 사용자 하이브의 MountPoints2 아래에 `{GUID}` 이름의 하위 키로도 생깁니다.
- 이 하위 키는 사용자마다 따로 생깁니다. 그래서 장치와 사용자를 잇는 몇 안 되는 레지스트리 기록입니다.
- 볼륨만 남는 것이 아닙니다. 연결한 네트워크 공유도 `##서버#공유` 꼴의 하위 키로 남습니다.

Harlan Carvey 가 정리한 순서는 다음과 같습니다(2013).

1. USBSTOR 에서 장치를 찾습니다.
2. `MountedDevices` 에서 그 장치를 가리키는 `\??\Volume{GUID}` 값을 찾아 볼륨 GUID 를 얻습니다.
3. 사용자마다 NTUSER.DAT 의 MountPoints2 에서 같은 GUID 를 찾습니다.

> 그림 자리: USBSTOR 인스턴스 ID → MountedDevices `\??\Volume{GUID}` → 사용자 A·B 의 NTUSER.DAT MountPoints2 `{GUID}` 하위 키. 사용자 A 에게만 키가 있는 경우와 둘 다 있는 경우를 나란히 보여 줍니다.

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 하이브 파일 | 사용자 프로필의 `NTUSER.DAT` ([하이브 파일 종류와 위치](/01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md)) |
| 키 경로 | `Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2` |
| 라이브 경로 | `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2` |
| 사용자 확인 | 하이브가 어느 SID 의 것인지는 [사용자 프로필 목록 (ProfileList)](/02-artifacts/system-account/profilelist.md)으로 확인합니다 |

| 버전 | 키 이름 | 근거 |
|---|---|---|
| Windows 2000 | `MountPoints` (끝에 2 가 없음) | libyal winreg-kb |
| XP·2003·Vista·2008·7·8·8.1·10 | `MountPoints2` | libyal winreg-kb 가 확인한 버전 목록 |
| Vista 이후로 추정 | `MountPoints2\CPC`, `CPC\Volume` 이 생김 | winreg-kb 도 물음표를 달아 둔 추정입니다 |
| 7 이후로 추정 | `CPC\LocalMOF` 가 생김 | winreg-kb 의 추정입니다 |
| 11 | `MountPoints2` 와 `CPC\Volume` 이 있음 | 관찰 (확인 범위: Win11 25H2 한 대) |

## 구조

키 하나에 여러 종류의 하위 키가 섞여 있습니다. 하위 키 이름으로 종류를 가립니다.

| 하위 키 이름 모양 | 뜻 | 예 |
|---|---|---|
| `{GUID}` | 볼륨 GUID. `MountedDevices` 의 `\??\Volume{GUID}` 와 짝입니다 | `{01234567-89ab-cdef-0123-456789abcdef}` (winreg-kb 예시) |
| `##…#…` | 네트워크 공유. UNC 경로의 `\` 가 `#` 로 바뀐 꼴입니다 | `##1.2.3.4#username` (winreg-kb 예시) |
| 영문 한 글자 | 드라이브 문자 | `C` (winreg-kb 예시) |
| `CPC` | 아래에 `Volume`·`LocalMOF` 하위 키가 있습니다 | 뜻은 공개 문서로 확인하지 못했습니다 |

`{GUID}` 하위 키 안에는 다음 하위 키와 값이 있을 수 있습니다(winreg-kb).

| 종류 | 이름 |
|---|---|
| 하위 키 | `_Autorun`, `_Autorun\Action`, `_Autorun\DefaultIcon`, `_Autorun\DefaultLabel` |
| 하위 키 | `Shell`, `Shell\Autoplay`, `Shell\Autoplay\DropTarget`, `Shell\AutoRun`, `Shell\AutoRun\Command` |
| 값 | `BaseClass` (REG_SZ) |

Win11 25H2 한 대에서 본 모습은 이렇습니다(관찰).

- `{GUID}` 하위 키 가운데 여럿은 값도 하위 키도 없는 빈 키였습니다.
- 나머지에는 `shell\Autoplay` (값 `MUIVerb`) 와 `shell\Autoplay\DropTarget` (값 `CLSID`) 가 있었습니다.
- `CPC\Volume` 아래에는 `{GUID}` 하위 키가 있었고, 값 이름은 `Data`·`Generation` 이었습니다. 이 값의 뜻은 문서로 확인하지 못했으므로 해석하지 않습니다.
- 드라이브 문자 하위 키는 없었습니다.

### 볼륨 GUID 안에 든 정보

볼륨 GUID 가 UUID 버전 1 (시각 기반) 형식이면 안에 시각과 노드 (node) 값이 들어 있습니다. 버전은 세 번째 칸의 첫 글자로 봅니다. `xxxxxxxx-xxxx-1xxx-…` 처럼 `1` 이면 버전 1 입니다.

| 칸 | 버전 1 에서의 뜻 |
|---|---|
| 1·2·3번째 칸 (버전 글자 제외) | 1582-10-15 00:00 UTC 부터 100나노초 단위로 센 60비트 시각 |
| 마지막 칸 (12자리) | 노드 값. 보통 네트워크 카드의 MAC 주소입니다 |

Carvey 는 MountPoints2 와 `MountedDevices` 의 볼륨 GUID 일부가 버전 1 형식이라고 보고했습니다(2012). 노드 값에서 그 PC 의 MAC 주소가 나왔습니다. 모든 GUID 가 버전 1 은 아닙니다. Win11 25H2 한 대에서는 세 번째 칸이 `0…` 이나 `4…` 로 시작하는 GUID 가 대부분이었습니다(관찰). 이런 GUID 에는 시각도 MAC 주소도 없습니다.

GUID 문자열과 바이트 순서는 [윈도 식별자 형식](/01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md)에서 다룹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 GUID 의 볼륨이, 이 사용자가 로그온해 있던 동안 이 PC 에 나타난 적이 있습니다 | 이 사용자가 장치를 직접 꽂았는지 |
| 이 사용자 하이브에 `##서버#공유` 키가 있으면, 이 사용자 세션에서 그 공유를 연결한 적이 있습니다 | 볼륨 안의 파일을 열었거나 복사했는지 |
| `MountedDevices` 와 짝이 맞으면, 그 볼륨이 어느 USB 장치의 것인지 이을 수 있습니다 | 몇 번 연결했는지 |
| | 처음 연결한 때 |
| | 키가 없으면 그 사용자 세션에 나타난 적이 없다는 것 (지웠을 수 있습니다) |

Jacky Fox 의 연구를 Carvey 가 소개한 내용에 따르면, 볼륨이 붙으면 그 GUID 는 로그온해 있는 **모든** 사용자의 MountPoints2 에 들어갑니다(2013). 콘솔 앞의 사용자에게만 들어가지 않습니다. 빠른 사용자 전환 (Fast User Switching) 으로 여러 사용자가 로그온해 있었다면 여러 하이브에 같은 GUID 가 남을 수 있습니다.

보고서에는 기록이 말하는 만큼만 씁니다.

- 쓸 수 있는 문장: "사용자 A 의 NTUSER.DAT MountPoints2 에 볼륨 GUID `{…}` 하위 키가 있습니다. 이 GUID 는 SYSTEM 하이브 MountedDevices 에서 인스턴스 ID `…` 인 USB 저장장치의 볼륨과 짝을 이룹니다. 이 하위 키의 마지막 기록 시각은 … UTC 입니다."
- 쓰면 안 되는 문장: "사용자 A 가 … UTC 에 USB 를 꽂았습니다."

## 시각 해석

값에는 시각이 없습니다. 시각은 키마다 하나씩 있는 마지막 기록 시각 (Last Write Time) 뿐입니다. 이 시각은 UTC FILETIME 입니다. 무엇이 이 시각을 바꾸는지는 [키 마지막 기록 시각](/01-foundations/database-log-formats/registry-hive/last-write-time.md)에서 다룹니다.

| 시각 | 흔히 읽는 뜻 | 조심할 점 |
|---|---|---|
| `{GUID}` 하위 키의 마지막 기록 시각 | 그 볼륨이 이 사용자 세션에 마지막으로 나타난 무렵 | Carvey 는 이것을 "일반적으로 받아들여지는 해석"이라고 썼습니다(2013). 형식 명세로 정해진 뜻이 아닙니다 |
| `MountPoints2` 키의 마지막 기록 시각 | 하위 키가 마지막으로 생기거나 지워진 무렵 | 어느 하위 키 때문인지는 알려 주지 않습니다 |
| `Shell`·`_Autorun` 같은 더 아래 하위 키의 시각 | 그 하위 키가 바뀐 때 | 아래 키의 변경은 `{GUID}` 키의 시각을 바꾸지 않습니다 |
| 버전 1 GUID 안의 시각 | GUID 를 만든 무렵 | 사용자별 값이 아닙니다. Carvey 의 시험에서는 장치를 연결한 부팅 세션의 부팅 시각을 가리켰습니다(2012). 확인된 규칙이 아니라 시험 결과입니다 |

- `{GUID}` 하위 키 시각은 [장치 속성의 마지막 연결 시각 (0066)](/02-artifacts/external-devices/usb-storage-artifacts/deviceclasses-device-properties-0064-0066-0067.md)과 맞춰 봅니다. 두 시각이 가까우면 마지막 연결 때 이 사용자가 로그온해 있었다고 볼 근거가 됩니다.
- 하위 키 시각이 0066 보다 한참 앞서면, 그 뒤의 연결 때는 이 사용자 키가 다시 쓰이지 않았을 수 있습니다. 이 사용자가 그때 로그온해 있지 않았을 가능성을 따져 봅니다.
- 현지 시각으로 바꿀 때는 그 PC 의 [시간대 설정](/02-artifacts/system-account/time-zone.md)을 씁니다.

## 함정과 한계

1. **여러 사용자에게 같은 GUID 가 남을 수 있습니다.** 로그온해 있던 사용자 모두에게 남는다는 연구가 있습니다. 한 하이브에서 GUID 를 찾았다고 그 사용자가 꽂았다고 단정하지 않습니다. 그 시각의 [로그온 세션](/02-artifacts/event-logs/logon-events/logon-id-4624-4634-4647.md)을 함께 봅니다.
2. **GUID 는 장치가 아니라 볼륨 단위입니다.** 파티션이 여럿인 장치는 GUID 도 여럿입니다. Microsoft 문서에 따르면 볼륨을 포맷할 때도 볼륨 GUID 를 붙입니다. 같은 USB 라도 포맷한 뒤에는 다른 GUID 로 남을 수 있습니다.
3. **볼륨 GUID 는 이 PC 가 붙인 이름입니다.** 장치 자체에 적힌 번호가 아닙니다. 다른 PC 의 GUID 와 맞춰 보는 용도로 쓰지 않습니다.
4. **USB 만 남지 않습니다.** 내장 디스크와 광학 드라이브의 GUID 도 남습니다(Carvey 2012). `MountedDevices` 와 짝을 맞춰 USB 장치인지 먼저 가립니다.
5. **짝이 없는 GUID 가 흔합니다.** Win11 25H2 한 대에서는 MountPoints2 의 볼륨 GUID 11개 가운데 1개만 지금의 `MountedDevices` 에 있었습니다(관찰, 원인은 확인하지 않음). 짝이 없으면 [섀도 복사본](/03-techniques/analysis/volume-shadow-copy-analysis.md) 안의 옛 SYSTEM 하이브에서 찾습니다.
6. **도구가 보여 주는 MAC 주소를 그대로 믿지 않습니다.** RegRipper 의 mp2 플러그인(2020-05-26 판)은 `{` 로 시작하는 모든 하위 키에서 마지막 칸을 떼어 MAC 목록에 넣습니다. 버전 1 인지는 확인하지 않습니다. 버전 4 GUID 의 마지막 칸은 MAC 주소가 아닙니다.
7. **버전 1 GUID 의 MAC 주소가 이 PC 의 실제 네트워크 카드라는 보장도 없습니다.** Carvey 의 시험에서 가상 머신 프로그램의 가상 어댑터 MAC 이 나왔고, 어느 MAC 과도 맞지 않는 노드 값도 있었습니다(2012).
8. **키가 없다고 연결이 없었던 것은 아닙니다.** 이 키는 사용자 권한으로 지울 수 있습니다. 하위 키를 지우면 `MountPoints2` 키의 마지막 기록 시각이 바뀝니다. 지운 키는 [지워진 키·값 복구](/01-foundations/database-log-formats/registry-hive/deleted-keys-values.md), [트랜잭션 로그](/01-foundations/database-log-formats/registry-hive/log1-log2.md), 섀도 복사본에서 다시 찾아봅니다.
9. **`Shell\AutoRun\Command` 에 명령이 적혀 있으면 따로 봅니다.** 이름대로 명령을 담는 자리입니다. 무엇을 실행하도록 걸려 있는지 확인하고 [악성코드 지속성(자동실행) 찾기](/04-scenarios/incident/persistence.md)와 함께 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 형식 명세를 보고 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다. `{GUID}` 하위 키 하나의 키 노드(`nk`) 셀입니다. 칸의 위치는 [하이브 내부 구조](/01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)를 따릅니다.

```
셀 시작 기준
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00      88 FF FF FF 6E 6B 20 00 00 2D 0B CF 96 CB DA 01   ....nk ..-......
 …
40      .. .. .. .. .. .. .. .. .. .. .. .. 26 00 00 00   ............&...
50      7B 39 61 36 61 35 35 30 30 2D 33 37 33 63 2D 31   {9a6a5500-373c-1
60      31 65 66 2D 39 61 32 62 2D 30 61 31 62 32 63 33   1ef-9a2b-0a1b2c3
70      64 34 65 35 66 7D                                 d4e5f}
```

1. `88 FF FF FF` 는 셀 크기 칸입니다. 부호 있는 정수로 -120 입니다. 음수이므로 사용 중인 셀입니다.
2. `6E 6B` 는 `nk` 서명입니다. `20 00` 은 키 이름이 ASCII 로 저장됐다는 플래그 0x0020 입니다.
3. `00 2D 0B CF 96 CB DA 01` 이 마지막 기록 시각입니다. 리틀 엔디언으로 0x01DACB96CF0B2D00 이고, 10진으로 133,642,987,540,000,000 입니다.
4. 이 값을 날짜로 바꾸면 2024-07-01 09:12:34 UTC 입니다. 한국 시각으로는 같은 날 18:12:34 입니다. 계산법은 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다.
5. 셀 오프셋 0x4C 의 `26 00` 은 키 이름 길이 38바이트입니다.
6. 0x50 부터 38바이트가 키 이름 `{9a6a5500-373c-11ef-9a2b-0a1b2c3d4e5f}` 입니다.

이제 GUID 를 풉니다.

1. 세 번째 칸 `11ef` 의 첫 글자가 `1` 이므로 버전 1 입니다.
2. 시각은 세 번째 칸에서 버전 글자를 뺀 `1ef`, 두 번째 칸 `373c`, 첫 번째 칸 `9a6a5500` 을 이어 붙인 0x1EF373C9A6A5500 입니다.
3. 1582-10-15 00:00 UTC 부터 100나노초 단위로 세면 2024-06-30 23:58:10 UTC 입니다.
4. 마지막 칸 `0a1b2c3d4e5f` 가 노드 값입니다. MAC 주소 꼴로 쓰면 `0A:1B:2C:3D:4E:5F` 입니다.

같은 풀이를 파이썬 표준 라이브러리로 확인할 수 있습니다.

```python
import uuid, datetime

u = uuid.UUID('9a6a5500-373c-11ef-9a2b-0a1b2c3d4e5f')
if u.version == 1:  # 버전 1 이 아니면 시각·MAC 이 없다
    t = datetime.datetime(1582, 10, 15, tzinfo=datetime.timezone.utc) \
        + datetime.timedelta(microseconds=u.time // 10)
    print(t, f'{u.node:012X}')   # 2024-06-30 23:58:10+00:00 0A1B2C3D4E5F
```

### 공개 도구로 한 번

- 사용자 프로필마다 `NTUSER.DAT` 를 꺼냅니다. 같은 폴더의 `.LOG1`·`.LOG2` 도 함께 꺼냅니다.
- 레지스트리 뷰어로 MountPoints2 를 엽니다. Registry Explorer·RECmd, RegRipper 의 mp2 플러그인, yarp·python-registry 같은 라이브러리가 예입니다.
- mp2 플러그인은 하위 키를 네트워크 공유(`#`)·볼륨(`{`)·드라이브 문자로 나누고 시각 순으로 보여 줍니다. MAC 목록은 위 함정 6번을 생각하고 읽습니다.
- 도구가 보여 준 GUID 와 시각 한두 개를 헥스 풀이와 맞춰 봅니다([도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md)).

## 교차 검증

| 아티팩트 | 잇는 값 | 더해 주는 것 |
|---|---|---|
| [드라이브 문자 매핑 (MountedDevices)](/02-artifacts/external-devices/usb-storage-artifacts/mounteddevices.md) | 볼륨 GUID | 그 볼륨이 어느 장치의 것인지, 드라이브 문자 |
| [USB 저장장치 목록 (USBSTOR)](/02-artifacts/external-devices/usb-storage-artifacts/usbstor.md) | 인스턴스 ID | 제조사·제품·시리얼 번호 |
| [연결·해제 시각](/02-artifacts/external-devices/usb-storage-artifacts/deviceclasses-device-properties-0064-0066-0067.md) | 장치 인스턴스 | 처음·마지막 연결 시각 |
| [로그온 세션 잇기](/02-artifacts/event-logs/logon-events/logon-id-4624-4634-4647.md) | 시각 | 그 시각에 누가 로그온해 있었는지 |
| [셸백 — 외부 장치 탐색 흔적](/02-artifacts/file-folder-usage/shellbags/removable-network-zip.md) | 드라이브 문자·경로 | 이 사용자가 볼륨 안의 폴더를 열었는지 |
| [바로가기 파일 (LNK)](/02-artifacts/file-folder-usage/lnk.md)·[점프리스트](/02-artifacts/file-folder-usage/jump-lists.md) | 드라이브 문자·볼륨 시리얼 번호 | 이 사용자가 볼륨 안의 파일을 열었는지 |
| [공유 폴더·네트워크 드라이브](/02-artifacts/network/network-shares-mapped-drives.md) | `##서버#공유` | 연결한 네트워크 드라이브와 드라이브 문자 |

MountPoints2 는 "이 사용자 세션에 볼륨이 나타났다" 까지만 말합니다. 사용자가 그 볼륨을 실제로 썼는지는 셸백·LNK·점프리스트로 따로 확인합니다. 전체 흐름은 [USB 로 무엇을 가져갔나](/04-scenarios/exfiltration/data-exfiltration/usb.md)와 [그 시각에 PC 를 쓴 사람이 누구인가](/04-scenarios/activity/user-attribution.md)에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 USB 사용이 들어 있고 사용자 프로필이 둘 이상인 윈도 이미지를 골라 풀어 봅니다.

1. 사용자마다 MountPoints2 하위 키를 볼륨·네트워크 공유·드라이브 문자·기타로 나눠 봅니다. 사용자별로 몇 개씩입니까?
2. USBSTOR 에 나온 USB 장치의 볼륨 GUID 를 `MountedDevices` 에서 구합니다. 그 GUID 가 어느 사용자의 MountPoints2 에 있습니까?
3. 같은 GUID 가 두 사용자에게 모두 있다면, 두 하위 키의 마지막 기록 시각을 비교합니다. 그 시각에 두 사용자가 모두 로그온해 있었습니까?
4. 그 하위 키의 시각과 장치 속성 0066(마지막 연결 시각)은 얼마나 차이가 납니까?
5. 볼륨 GUID 가운데 버전 1 인 것을 골라 시각과 노드 값을 풀어 봅니다. 노드 값이 이 PC 의 네트워크 카드 MAC 주소와 맞습니까?

## 참고 문헌

- libyal winreg-kb, "Mount points" — https://github.com/libyal/winreg-kb/blob/main/docs/sources/explorer-keys/Mount-points.md
- Microsoft Learn, "Supporting Mount Manager Requests in a Storage Class Driver" — https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/supporting-mount-manager-requests-in-a-storage-class-driver
- Microsoft Learn, "Naming a Volume" — https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-volume
- Harlan Carvey, Windows Incident Response, "HowTo: Correlate an Attached Device to a User" (2013-07) — https://windowsir.blogspot.com/2013/07/howto-correlate-attached-device-to-user.html
- Harlan Carvey, Windows Incident Response, "There Are Four Lights: USB-Accessible Storage" (2013-01, Jacky Fox 의 연구 소개) — https://windowsir.blogspot.com/2013/01/there-are-four-lights-usb-accessible.html
- Harlan Carvey, Windows Incident Response, "New Tools, Registry Findings" (2012-04, 버전 1 GUID 의 시각·MAC) — https://windowsir.blogspot.com/2012/04/new-tools-registry-findings.html
