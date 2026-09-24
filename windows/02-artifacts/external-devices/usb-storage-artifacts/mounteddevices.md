# 드라이브 문자 매핑 (MountedDevices)

## 한 줄 요약

SYSTEM 하이브의 `MountedDevices` 키는 마운트 관리자 (Mount Manager) 가 볼륨 이름과 드라이브 문자를 적어 두는 곳입니다. USB 저장장치를 볼륨 GUID 와 드라이브 문자에 잇는 중간 고리입니다.

## 무엇을 기록하나 · 왜 생기나

마운트 관리자는 볼륨마다 이름을 붙이고 관리합니다.

- **고유 볼륨 이름 (unique volume name)**: `\??\Volume{GUID}` 꼴입니다. 볼륨을 시스템에서 떼어 낸 뒤에도 이 이름은 바뀌지 않습니다.
- **드라이브 문자 (drive letter)**: `\DosDevices\E:` 꼴입니다. 재부팅해도 남습니다. 다만 볼륨이 붙고 떨어지면 다른 볼륨에 다시 줄 수 있습니다.
- **폴더 마운트 지점 (mount point)**: `\DosDevices\C:\mymount` 처럼 폴더에 볼륨을 붙인 경우입니다.

이 이름들은 커널의 심볼릭 링크입니다. 심볼릭 링크는 재부팅하면 사라집니다. 그래서 마운트 관리자는 링크의 *이름*을 레지스트리에 적어 둡니다. Microsoft 는 이것을 영구 이름 데이터베이스 (persistent name database) 라고 부릅니다.

값 하나가 이름 하나입니다. 값 이름이 영구 이름이고, 값 데이터가 그 볼륨의 고유 ID (unique ID) 입니다. 같은 볼륨을 가리키는 이름들은 고유 ID 가 모두 같습니다. 이 점 덕분에 드라이브 문자와 볼륨 GUID 를 서로 이을 수 있습니다.

볼륨이 오프라인이 되면 마운트 관리자는 심볼릭 링크만 지웁니다. 데이터베이스에 적힌 이름은 지우지 않습니다. 그래서 USB 를 뽑은 뒤에도 이 키에 흔적이 남습니다.

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 하이브 파일 | SYSTEM ([하이브 파일 종류와 위치](../../../01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md)) |
| 키 경로 | `SYSTEM\MountedDevices` (라이브에서는 `HKLM\SYSTEM\MountedDevices`) |
| 값 형식 | 모두 REG_BINARY |
| 확인된 버전 | Windows 2000 부터 Windows 11 까지 같은 위치 |

이 키는 하이브 바로 아래에 있습니다. `ControlSet00X` 아래가 아니므로 [컨트롤셋 고르기](../../../01-foundations/database-log-formats/registry-hive/controlset-select.md)가 필요 없습니다.

이동식 USB 저장장치가 남기는 값 데이터는 자료마다 모양이 다릅니다.

| 시기 | 값 데이터 모양 | USB 장치로 잇는 방법 |
|---|---|---|
| Windows XP 자료 | `\??\STORAGE#RemovableMedia#7&2c9a320d&0&RM#{53f5630d-…}` | 가운데 `7&2c9a320d&0` 이 ParentIdPrefix 입니다. USBSTOR 쪽 ParentIdPrefix 값과 맞춥니다. |
| 그 뒤 자료 | `_??_USBSTOR#Disk&Ven_Generic&Prod_Flash_Disk&Rev_8.07#01234567&0#{GUID}` | 문자열 안에 USBSTOR 장치 이름과 인스턴스 ID 가 그대로 있습니다. |

위 두 줄은 참고 문헌에 실린 예시입니다. 두 번째 줄의 끝 GUID 는 원문에서 가린 값입니다. 어느 버전에서 모양이 바뀌었는지는 이 글에서 확인한 자료로 못 박지 않습니다. 검체에서 실제 모양을 보고 판단합니다.

USBSTOR 쪽 이름과 ParentIdPrefix 는 [USB 저장장치 목록 (USBSTOR)](usbstor.md)에서 다룹니다.

## 구조

### 값 이름

| 값 이름 모양 | 뜻 |
|---|---|
| `\DosDevices\E:` | 드라이브 문자 |
| `\DosDevices\C:\mymount` | 폴더에 붙인 마운트 지점. 드물게 보입니다. |
| `\??\Volume{GUID}` | 고유 볼륨 이름 |
| `#{GUID}` | 용도가 문서로 밝혀지지 않았습니다. 해석하지 않습니다. |

### 값 데이터

값 데이터는 세 가지 모양 가운데 하나입니다. 저장 형식은 libyal winreg-kb 를 따릅니다.

| 모양 | 크기 | 오프셋 · 크기 · 뜻 |
|---|---|---|
| MBR 파티션 | 12바이트 | 0 · 4 · MBR 디스크 서명<br>4 · 8 · 파티션 시작 위치(바이트 단위) |
| GPT 파티션 | 24바이트 | 0 · 8 · 아스키 `DMIO:ID:`<br>8 · 16 · GPT 파티션 GUID (리틀 엔디언) |
| 장치 문자열 | 가변 | 0 · … · UTF-16LE 장치 경로. 끝에 널 문자가 없습니다. |

- 디스크 서명과 파티션 GUID 의 뜻은 [파티션 구조 (MBR·GPT)](../../../01-foundations/disk-volume/mbr-gpt.md)에서 다룹니다.
- GUID 의 바이트 순서는 [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md)에서 다룹니다.
- 장치 문자열은 `#{GUID}` 로 끝납니다. 이 GUID 는 장치 인터페이스 종류를 나타냅니다. 디스크 인터페이스 (GUID_DEVINTERFACE_DISK) 라면 `{53f56307-b6bf-11d0-94f2-00a0c91efb8b}` 입니다.

MBR·GPT 모양에는 제조사·제품·일련번호가 없습니다. 이 모양만 보고는 USB 장치인지 알 수 없습니다. 고정 디스크로 인식되는 외장 디스크는 이 모양으로 남을 수 있습니다. 이때는 디스크 서명이나 파티션 GUID 를 다른 기록과 맞춰 봅니다.

> 그림 자리: USBSTOR 인스턴스 ID → MountedDevices 장치 문자열 → 데이터가 같은 `\??\Volume{GUID}` 와 `\DosDevices\E:` → NTUSER.DAT MountPoints2 의 `{GUID}` 로 이어지는 사슬

## 증거로서 의미

### 증명하는 것

- 이 시스템의 마운트 관리자가 그 장치 문자열(또는 디스크 서명·파티션 GUID)이 적힌 볼륨을 본 적이 있습니다.
- 그 볼륨에 붙은 볼륨 GUID 를 알 수 있습니다.
- 하이브를 저장한 시점에 어떤 볼륨이 그 드라이브 문자를 마지막으로 받았는지 알 수 있습니다.

### 증명하지 못하는 것

- **언제** 연결했는지는 알 수 없습니다. 값에는 시각이 없습니다.
- **누가** 연결했는지는 알 수 없습니다. SYSTEM 하이브에는 사용자 정보가 없습니다.
- 파일을 열거나 복사했는지는 알 수 없습니다.
- 몇 번 연결했는지는 알 수 없습니다.
- 예전에 같은 드라이브 문자를 받았던 다른 장치는 알 수 없습니다. 덮어쓰기 때문입니다.

보고서에는 기록이 말하는 만큼만 씁니다.

> 예: "SYSTEM 하이브의 MountedDevices 에서 `\DosDevices\E:` 의 데이터가 인스턴스 ID `…` 인 USB 저장장치의 장치 경로와 같습니다. 하이브를 저장한 시점 기준으로 이 장치의 볼륨이 E: 를 마지막으로 받은 기록이 있습니다."

## 시각 해석

레지스트리 값에는 시각이 따로 없습니다. 시각은 키 단위로만 남습니다 ([키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md)).

- `MountedDevices` 키의 마지막 기록 시각은 UTC FILETIME 입니다.
- 이 시각은 키 안의 값 가운데 어느 하나가 바뀐 때를 가리킵니다.
- 어느 값이 바뀌었는지는 알려 주지 않습니다.
- 따라서 이 시각을 특정 USB 의 연결 시각으로 쓰면 안 됩니다.

연결·해제 시각은 [연결·해제 시각 (DeviceClasses·Device Properties)](deviceclasses-device-properties-0064-0066-0067.md)에서 구합니다.

## 함정과 한계

1. **드라이브 문자는 덮어씁니다.** 값 이름 `\DosDevices\E:` 에는 데이터가 하나만 들어갑니다. 나중에 다른 볼륨이 E: 를 받으면 데이터가 바뀝니다. 그래서 드라이브 문자로는 마지막 장치만 보입니다.
2. **볼륨 GUID 값은 남습니다.** `\??\Volume{GUID}` 값은 장치를 뽑아도 남습니다. 드라이브 문자가 없는 볼륨 GUID 값이 여럿 있는 것은 정상입니다.
3. **접두어로 검색하지 않습니다.** 참고 문헌 예시에서 USB 장치 문자열은 `\??\` 가 아니라 `_??_` 로 시작합니다. `USBSTOR` 나 인스턴스 ID 로 검색해야 놓치지 않습니다.
4. **헥스로만 보여 주는 도구가 있습니다.** 장치 문자열은 UTF-16LE 로 풀어야 읽힙니다 ([문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)).
5. **인스턴스 ID 가 일련번호가 아닐 수 있습니다.** 장치에 일련번호가 없으면 윈도가 만든 값이 들어갑니다. 구별하는 법은 [USB 저장장치 목록 (USBSTOR)](usbstor.md)에서 다룹니다.
6. **네트워크 드라이브는 여기에 없습니다.** 공유 폴더에 붙인 드라이브 문자는 사용자 하이브에 남습니다 ([공유 폴더·네트워크 드라이브](../../network/network-shares-mapped-drives.md)).
7. **정리 명령으로 지울 수 있습니다.** `mountvol /r` 은 지금 시스템에 없는 볼륨의 마운트 지점 폴더와 레지스트리 설정을 지웁니다. 레지스트리 편집기로 값을 지울 수도 있습니다. 두 경우 모두 키의 마지막 기록 시각이 바뀝니다. 지운 값은 다음 자리에서 찾아봅니다.
   - [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 안의 옛 SYSTEM 하이브
   - [트랜잭션 로그 (.LOG1·.LOG2)](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md)
   - 하이브 안에 남은 [지워진 키·값](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md)

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 명세로 만든 예시입니다. 실제 검체에서 나온 값이 아닙니다.

**MBR 모양 (12바이트)**

```
4D 3C 2B 1A  00 00 10 00 00 00 00 00
```

- 앞 4바이트를 리틀 엔디언 32비트로 읽습니다. 디스크 서명은 `1A2B3C4D` 입니다.
- 뒤 8바이트를 리틀 엔디언 64비트로 읽습니다. 파티션 시작 위치는 `0x100000` = 1,048,576 바이트입니다.
- 섹터가 512바이트이면 2,048번 섹터에서 시작하는 파티션입니다.

**GPT 모양 (24바이트)**

```
44 4D 49 4F 3A 49 44 3A  67 45 23 01 AB 89 EF CD 01 23 45 67 89 AB CD EF
```

- 앞 8바이트는 아스키 `DMIO:ID:` 입니다.
- 뒤 16바이트는 GUID `{01234567-89AB-CDEF-0123-456789ABCDEF}` 입니다. 앞 세 칸만 바이트 순서가 뒤집힙니다.

**장치 문자열 모양 (앞부분만)**

```
5F 00 3F 00 3F 00 5F 00 55 00 53 00 42 00 53 00 54 00 4F 00 52 00 23 00
_     ?     ?     _     U     S     B     S     T     O     R     #
```

데이터가 똑같은 값 이름을 모두 찾습니다. 그 가운데 `\??\Volume{…}` 이 볼륨 GUID 이고, `\DosDevices\X:` 가 드라이브 문자입니다.

세 모양을 가르는 순서는 짧은 코드로 옮길 수 있습니다.

```python
import struct, uuid

def decode(data: bytes) -> str:
    if len(data) == 12:
        sig, off = struct.unpack('<IQ', data)
        return f'MBR 디스크 서명 {sig:08X}, 파티션 시작 {off} 바이트'
    if len(data) == 24 and data[:8] == b'DMIO:ID:':
        return 'GPT 파티션 GUID {' + str(uuid.UUID(bytes_le=data[8:])) + '}'
    return data.decode('utf-16-le', errors='replace')
```

### 공개 도구로 한 번

- 압수 이미지에서 SYSTEM 하이브를 꺼낸 뒤 레지스트리 뷰어로 엽니다. Registry Explorer, RegRipper 의 마운트 장치 플러그인 같은 도구가 예입니다.
- 도구가 보여 주는 볼륨 GUID·드라이브 문자·장치 문자열을 위 헥스 풀이와 맞춰 봅니다.
- 라이브 시스템에서는 `mountvol` 로 지금 붙은 볼륨과 마운트 지점을 볼 수 있습니다. 이 명령의 결과는 지금 상태이고, 하이브의 옛 기록과 다를 수 있습니다.

## 교차 검증

| 아티팩트 | 이 페이지와 잇는 값 | 더해 주는 것 |
|---|---|---|
| [USB 저장장치 목록 (USBSTOR)](usbstor.md) | 장치 이름·인스턴스 ID | 제조사·제품·일련번호 |
| [사용자별 장치 연결 (MountPoints2)](mountpoints2.md) | 볼륨 GUID | 어느 사용자 프로필에서 그 볼륨이 보였는지 |
| [연결·해제 시각 (DeviceClasses·Device Properties)](deviceclasses-device-properties-0064-0066-0067.md) | 장치 인스턴스 | 처음·마지막 연결 시각, 해제 시각 |
| [휴대용 장치·볼륨 이름 기록 (WPD·EMDMgmt)](wpd-emdmgmt.md) | 장치 인스턴스 | 볼륨 이름, 볼륨 일련번호 |
| [바로가기 파일 (LNK)](../../file-folder-usage/lnk.md)·[점프리스트](../../file-folder-usage/jump-lists.md) | 드라이브 문자 경로 | 그 드라이브에서 연 파일 |
| [셸백 — 외부 장치 탐색 흔적](../../file-folder-usage/shellbags/removable-network-zip.md) | 드라이브 문자 | 사용자가 연 폴더 |
| [외부 장치 연결 이벤트](../../event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) | 장치 인스턴스·디스크 정보 | 연결 시각과 디스크 정보 |

드라이브 문자는 덮어쓰기 때문에 한 장치에 한 번만 이어 보면 틀리기 쉽습니다. LNK·셸백의 드라이브 문자 경로를 쓸 때는 그 시각에 E: 를 받은 장치가 누구인지 연결 시각으로 따로 확인합니다. 전체 흐름은 [USB 로 무엇을 가져갔나](../../../04-scenarios/exfiltration/data-exfiltration/usb.md)에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 USB 사용이 들어 있는 윈도 이미지를 골라 풀어 봅니다.

1. `MountedDevices` 의 값 데이터를 세 모양(MBR·GPT·장치 문자열)으로 나눠 봅니다. 모양별로 몇 개입니까?
2. USBSTOR 에 나온 장치마다 그 인스턴스 ID 를 담은 값을 찾습니다. 각각의 볼륨 GUID 는 무엇입니까?
3. 그 볼륨 GUID 값과 데이터가 같은 `\DosDevices\X:` 가 있습니까? 없다면 왜 없는지 설명해 봅니다.
4. 볼륨 GUID 를 사용자별 NTUSER.DAT 의 MountPoints2 에서 찾습니다. 어느 사용자에게 나옵니까?
5. 섀도 복사본이 있다면 옛 SYSTEM 하이브의 `\DosDevices\E:` 와 지금 값을 비교합니다. 달라졌습니까?

## 참고 문헌

- Microsoft Learn, "Supporting Mount Manager Requests in a Storage Class Driver" — https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/supporting-mount-manager-requests-in-a-storage-class-driver
- Microsoft Learn, "mountvol" — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mountvol
- Microsoft Learn, "GUID_DEVINTERFACE_DISK" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/guid-devinterface-disk
- libyal winreg-kb, "Mounted devices" — https://winreg-kb.readthedocs.io/en/latest/sources/system-keys/Mounted-devices.html
- Harlan Carvey, Windows Incident Response, "HowTo: Correlate an Attached Device to a User" (2013-07) — https://windowsir.blogspot.com/2013/07/howto-correlate-attached-device-to-user.html
- Forensics Wiki, "USB History Viewing" — https://forensics.wiki/usb_history_viewing/
