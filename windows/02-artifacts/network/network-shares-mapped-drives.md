---
title: "공유 폴더·네트워크 드라이브"
parent: "아티팩트 · 네트워크"
nav_order: 2440
---

# 공유 폴더·네트워크 드라이브 (Network Shares·Mapped Drives)

> 이 페이지의 값은 Windows 11 Home 25H2(빌드 26200.9457) 기준입니다. 다른 버전에서는 값이 다를 수 있습니다.

공유 흔적은 방향에 따라 남는 곳이 다릅니다. 이 PC 가 폴더를 공유했다면 SYSTEM 하이브의 `LanmanServer\Shares` 에 남습니다. 이 PC 가 다른 컴퓨터의 공유에 연결했다면 사용자 하이브와 SMB 클라이언트 이벤트 로그에 남습니다. 공유에 누가 들어왔는지는 서버 쪽 Security 로그에 남지만, 감사 정책을 켜 두어야 기록됩니다.

## 무엇을 기록하나 · 왜 생기나

윈도 파일 공유는 SMB (Server Message Block) 로 주고받습니다. 폴더를 내주는 쪽이 서버이고, 그 폴더에 연결하는 쪽이 클라이언트입니다. PC 한 대가 두 역할을 다 할 수 있습니다. 그래서 기록도 두 가지로 나눠 봅니다.

| 쪽 | 기록 | 생기는 때 | 알려 주는 것 |
|---|---|---|---|
| 서버 | SYSTEM `LanmanServer\Shares` | 공유를 만들 때 | 공유 이름, 공유한 폴더, 설명 |
| 서버 | Security 로그 5140·5142~5145 | 감사를 켜 둔 PC 에서 공유에 접근하거나 공유를 바꿀 때 | 접근한 계정과 원본 주소, 공유 추가·수정·삭제 |
| 클라이언트 | NTUSER.DAT `Map Network Drive MRU` | 이름으로 보면 탐색기 "네트워크 드라이브 연결" 대화상자를 쓸 때 | 입력한 공유 경로와 순서 |
| 클라이언트 | NTUSER.DAT `MountPoints2` | 사용자 세션에 볼륨이나 원격 드라이브가 나타날 때 | `#` 으로 시작하는 원격 드라이브 하위 키 |
| 클라이언트 | `Microsoft-Windows-SmbClient/Connectivity` | 공유에 연결할 때 | 공유 경로, 서버 주소와 포트, 서명·암호화 사용 여부 |
| 클라이언트 | `Microsoft-Windows-SmbClient/Security` | 인증이나 공유 연결에 실패할 때 | 사용자 이름, 서버 이름, 경로 |

이 기록으로 아래 질문에 답합니다.

- 이 PC 가 어떤 폴더를 공유했나
- 이 PC 에서 어느 서버의 어느 공유에 연결했나
- 연결이나 인증에 실패한 시도가 있었나
- 이 PC 의 공유에 누가 어디서 들어왔나(감사를 켜 두었을 때)

## 위치와 버전별 차이

| 기록 | 위치 | 메모 |
|---|---|---|
| 공유 목록 | SYSTEM `<ControlSet>\Services\LanmanServer\Shares` | `Select\Current` 가 가리키는 ControlSet 에서 읽습니다[2] |
| 공유 권한 | `...\LanmanServer\Shares\Security` | 공유 이름과 같은 이름의 값으로 남습니다 |
| 서버 설정 | `...\LanmanServer\Parameters` 의 `AutoShareServer`·`AutoShareWks`·`NullSessionShares` | RegRipper shares 플러그인이 함께 읽는 값입니다[2] |
| 드라이브 연결 입력 기록 | NTUSER.DAT `Software\Microsoft\Windows\CurrentVersion\Explorer\Map Network Drive MRU` | 수집 대상 키입니다[1]. RegRipper mndmru 플러그인으로 읽습니다[2] |
| 사용자별 볼륨·원격 드라이브 | NTUSER.DAT `Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2` | RegRipper mp2 플러그인으로 읽습니다[2] |
| 연결 복원 설정 | `HKCU\Software\Microsoft\Windows NT\CurrentVersion\Network\Persistent Connections` | `SaveConnections=yes` 값이 있습니다 |
| 클라이언트 이벤트 | `Microsoft-Windows-SmbClient/Connectivity`, `Microsoft-Windows-SmbClient/Security`, `Microsoft-Windows-SMBClient/Operational` | 기본으로 켜져 있고 최대 크기는 각 8MB(8388608바이트)입니다 |
| 서버 이벤트 | Security 로그 5140·5142~5145 | 감사 정책을 켜야 남습니다 |
| 서버 쪽 채널 | `Microsoft-Windows-SMBServer/Operational`·`/Connectivity`·`/Security`·`/Audit` | 최대 8MB 입니다. 내용은 이 페이지에서 다루지 않습니다 |

- 윈도 버전에 따라 키 이름이 `lanmanserver` 와 `LanmanServer` 로 대소문자가 다릅니다[2]. 직접 만든 스크립트로 키를 찾을 때는 대소문자를 가리지 않고 비교합니다.
- 오프라인 SYSTEM 하이브에는 `CurrentControlSet` 이 없습니다. `Select` 키가 가리키는 `ControlSet00n` 을 읽습니다. 하이브 구조는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.
- 이벤트 채널과 ID 는 Windows 11 25H2 기준입니다. 다른 윈도 버전의 채널 구성은 실제 데이터로 확인합니다.

## 구조

### 공유 목록 (LanmanServer\Shares)

값 하나가 공유 하나이고, 값 이름이 공유 이름입니다. 값 형식은 REG_MULTI_SZ 로, 값 안에 "이름=값" 문자열이 여러 개 들어 있습니다.

아래는 공유 `ZZTestShare` 를 만들었을 때 값 안에 들어가는 줄입니다. 폴더 경로와 설명은 자리 표시입니다.

```
CATimeout=0
CSCFlags=0
MaxUses=4294967295
Path=<공유한 폴더>
Permissions=0
Remark=<설명>
ShareName=ZZTestShare
Type=0
```

| 줄 | 읽는 법 |
|---|---|
| `Path` | 공유한 로컬 폴더 경로입니다 |
| `ShareName` | 공유 이름입니다. 값 이름과 같습니다 |
| `Remark` | 공유에 붙인 설명입니다 |
| `MaxUses` | 예시 값은 4294967295(0xFFFFFFFF)입니다 |
| `CATimeout`·`CSCFlags`·`Permissions`·`Type` | 예시 값은 모두 0 입니다 |

- 공유별 권한은 `Shares\Security` 아래에 공유 이름과 같은 이름의 값으로 따로 남습니다.
- 기본 관리 공유(C$·ADMIN$·IPC$)는 `Shares` 키에 값으로 없습니다. 따로 만든 공유가 없으면 `Shares` 키는 비어 있습니다.

### 드라이브 연결 입력 기록 (Map Network Drive MRU)

이 키에는 `MRUList` 값과 한 글자 이름의 값들이 있습니다. 한 글자 이름의 값에 경로가 들어가고, `MRUList` 는 그 값들의 순서를 적습니다. RegRipper mndmru 플러그인은 `MRUList` 를 먼저 보여 주고, 나머지 값을 이름순으로 보여 줍니다[2].

탐색기의 "네트워크 드라이브 연결" 대화상자를 쓴 적이 없는 PC 에는 이 키가 없을 수 있습니다.

### MountPoints2 의 원격 드라이브

MountPoints2 의 전체 구조와 시각 해석은 [USB 저장장치 흔적](../external-devices/usb-storage-artifacts/index.md) 허브의 MountPoints2 페이지에서 다룹니다. 여기서는 공유와 관련된 점만 적습니다.

RegRipper mp2 플러그인은 하위 키 이름의 첫 글자로 종류를 나눕니다[2].

| 첫 글자 | mp2 의 분류 |
|---|---|
| `{` | 볼륨 |
| 영문 대문자 | 드라이브 문자 |
| `#` | 원격 드라이브 (Remote Drives) |

관리자 권한 PowerShell 에서 `net use` 로 드라이브를 연결했다가 끊기만 하고 탐색기로 열지 않으면, `#` 으로 시작하는 하위 키가 생기지 않을 수 있습니다. 원격 드라이브 하위 키 이름이 어떤 모양인지는 MountPoints2 페이지를 봅니다.

### SMB 클라이언트 이벤트

Connectivity 채널의 이벤트입니다.

| ID | 뜻 |
|---|---|
| 30830 | 연결 선택 |
| 30833 | 공유에 처음 연결했습니다 ("The initial connection to the share was established.") |
| 30803 | 연결 실패 |
| 30804 | 연결 끊김 |
| 30805 | 세션을 잃음 |
| 30806 | 세션을 다시 맺음 |
| 30807 | 공유 연결을 잃음 |
| 30808 | 공유 연결을 다시 맺음 |
| 30822 | 멀티채널 연결 실패 |

30833 메시지에는 Share name, Server address, Session ID, Tree ID, Transport type, Signing used, Encryption used, Compression requested, NTLM blocked 필드가 있습니다.

`net use` 로 `\\127.0.0.1\C$` 를 연결하면 아래처럼 남습니다.

- 30830 뒤에 30833 이 두 건 남고, 하나는 IPC$, 하나는 대상 공유 C$ 에 대한 기록입니다.
- 이벤트 데이터의 `ServerName` 필드에는 `\127.0.0.1\C$` 처럼 앞 역슬래시가 하나인 공유 경로가 들어 있고, `Address` 필드에는 소켓 주소가 16진 원시값으로 들어 있습니다. 푸는 법은 아래 "헥스로 한 번" 에서 따라갑니다.
- 이벤트 레코드의 UserId 는 비어 있어서 누가 연결했는지는 남지 않습니다.
- 드라이브를 끊은 뒤에도 30833 기록은 로그에 그대로 남습니다.

Security 채널에는 실패 기록이 남습니다.

| ID | 뜻 | 필드 |
|---|---|---|
| 31001 | 인증 실패 | User name, Logon ID, Server name |
| 31010 | 공유 연결 실패 ("The SMB client failed to connect to the share.") | Path |
| 31017 | 안전하지 않은 게스트 로그온을 거부함 | |

### 서버 쪽 Security 이벤트

| ID | 뜻 |
|---|---|
| 5140 | 네트워크 공유 개체에 접근함 |
| 5142 | 공유 추가 |
| 5143 | 공유 수정 |
| 5144 | 공유 삭제 |
| 5145 | 클라이언트에 원하는 권한을 줄 수 있는지 검사함. 공유 안의 파일 경로가 함께 남습니다 |



필드와 해석은 [공유 폴더 접근](../event-logs/5140-5145.md)에서 다룹니다. 감사를 켜는 설정은 [감사 정책과 로그 설정](../event-logs/audit-policy-log-settings.md)에서 다룹니다.

- "파일 공유" 와 "세부 파일 공유" 감사가 모두 "No Auditing" 이면 공유에 연결해도 5140·5145 가 한 건도 남지 않습니다.

## 증거로서 의미

**증명하는 것**

- `Shares` 의 값 하나는 수집 시점에 그 이름의 공유가 있었다는 기록입니다. `Path` 로 어느 폴더를 공유했는지 압니다.
- 30833 은 그 시각에 이 PC 가 그 공유에 연결했다는 기록입니다. 서버 주소와 포트가 함께 남습니다.
- 드라이브를 끊어도 30833 은 남습니다. 지금 연결된 드라이브가 없어도 과거 연결을 찾을 수 있습니다.
- 31001·31010 은 인증이나 공유 연결에 실패한 시도를 보여 줍니다.
- `Map Network Drive MRU` 의 값은 그 사용자 하이브에 그 경로가 입력 기록으로 남았다는 뜻입니다.
- 감사를 켠 서버의 5140·5145 는 어느 계정이 어느 주소에서 공유에 접근했는지 보여 줍니다.

**증명하지 못하는 것**

- 30833 에는 연결한 사용자가 없습니다. 이 기록만으로는 누가 연결했는지 알 수 없습니다.
- 공유가 있다고 누가 그 공유에 들어왔다는 뜻은 아닙니다.
- 공유에 연결했다고 파일을 열거나 복사했다는 뜻은 아닙니다. 파일 단위 기록은 서버 쪽 5145 나 클라이언트 쪽 바로가기 파일·점프리스트에서 따로 찾습니다.
- 사용자 레지스트리에 흔적이 없다고 연결이 없었던 것은 아닙니다(아래 함정 참고).
- `Shares` 에 값이 없다고 공유를 연 적이 없는 것은 아닙니다. 지운 공유의 값은 바로 사라집니다.

보고서에는 기록으로 확인되는 만큼만 씁니다. 예를 들면 "`Microsoft-Windows-SmbClient/Connectivity` 로그에 공유 `\127.0.0.1\C$`(서버 주소 127.0.0.1, 포트 445)에 연결한 기록(30833)이 있다. 이 이벤트에는 사용자 정보가 없어 연결한 계정은 이 기록만으로 알 수 없다." 처럼 씁니다.

## 시각 해석

- 레지스트리 값에는 시각이 없습니다. 시각은 키마다 하나 있는 마지막 기록 시각 (Last Write Time) 뿐입니다. 이 시각은 UTC 입니다.
- `Map Network Drive MRU` 는 값이 여러 개여도 시각이 하나라서, 어느 값 때문에 바뀌었는지 알려 주지 않습니다.
- `Shares` 키의 마지막 기록 시각도 마찬가지입니다. 이 시각을 특정 공유를 만든 때라고 단정하지 않습니다. 공유를 만든 때는 감사를 켠 PC 의 5142 로 확인합니다.
- mp2 플러그인은 MountPoints2 하위 키마다 마지막 기록 시각을 붙여 시간순으로 보여 줍니다[2].
- 이벤트 시각은 레코드 시각입니다. 레코드 시각을 읽는 법은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.
- Connectivity 로그 1,968건이 OS 를 설치한 2026-06-26 부터 2026-09-23 까지 약 3개월치를 담은 예가 있습니다. 보존 기간은 연결이 얼마나 잦은지에 따라 달라집니다.
- 현지 시각으로 바꿀 때는 그 PC 의 [시간대 설정](../system-account/time-zone.md)을 씁니다.

## 함정과 한계

1. **IPC$ 연결도 함께 남습니다.** `net use` 한 번에 IPC$ 와 C$ 의 30833 이 각각 남습니다. IPC$ 기록을 사용자가 연 공유로 세지 않습니다.
2. **공유 경로의 앞 역슬래시가 하나입니다.** 30833 의 `ServerName` 에는 `\127.0.0.1\C$` 처럼 적힙니다. `\\서버\공유` 형식 문자열로 검색하면 놓칩니다.
3. **주소 필드는 16진 원시값입니다.** 포트 두 바이트는 앞 바이트가 큰 자리입니다. 리틀 엔디언으로 읽으면 포트가 틀립니다.
4. **사용자 레지스트리에 흔적이 남지 않을 수 있습니다.** 관리자 권한 PowerShell 에서 `net use W:`·`Z:` 로 `\\localhost\C$` 를 `/persistent:yes` 로 연결하거나 `New-SmbMapping -Persistent $true` 로 연결하면, 연결 직후 `HKCU\Network` 아래에 하위 키가 생기지 않고 HKCU 어디에도 연결 경로 문자열이 없습니다.
5. **`HKCU\Network` 에만 기대지 않습니다.** 영구 연결 드라이브가 `HKCU\Network\<드라이브 문자>` 에 남는다는 설명이 흔하지만, 위 조건에서는 남지 않습니다. 이 키가 없다고 드라이브 연결이 없었다고 보지 않습니다.
6. **관리 공유는 `Shares` 에 없습니다.** C$·ADMIN$·IPC$ 는 값으로 적혀 있지 않습니다. `Shares` 가 비어 있다고 이 PC 에 공유가 하나도 없다고 단정하지 않습니다.
7. **지운 공유는 레지스트리에서 바로 사라집니다.** `Remove-SmbShare` 로 지우면 `Shares` 값과 `Shares\Security` 값이 둘 다 바로 없어집니다. 예전 공유는 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md)으로 옛 SYSTEM 하이브를 열어 찾습니다. 하이브 안의 지운 값을 되살리는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.
8. **서버 쪽 접근 기록은 없을 수 있습니다.** 파일 공유 감사가 꺼져 있으면 5140·5145 가 남지 않습니다. 5140 이 없다고 공유 접근이 없었다고 보지 않습니다. 먼저 감사 설정을 확인합니다.
9. **Map Network Drive MRU 는 한 가지 연결 방법의 기록입니다.** `net use` 나 PowerShell 로 연결하면 이 키는 남지 않는 것으로 보입니다. 그래서 이 키를 기대하지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

30833 의 `Address` 필드를 풉니다. 아래 앞 8바이트는 `\\127.0.0.1\C$` 에 연결했을 때 남는 값입니다.

```
02 00 01 BD 7F 00 00 01 …
```

| 바이트 | 읽는 법 | 값 |
|---|---|---|
| `02 00` | 주소 종류 | IPv4 |
| `01 BD` | 포트. 앞 바이트가 큰 자리입니다 | 0x01BD = 445 |
| `7F 00 00 01` | IPv4 주소. 한 바이트씩 10진으로 읽습니다 | 127.0.0.1 |
| 그 뒤 | 공개 자료 없음 | |

같은 풀이를 파이썬으로 확인합니다.

```python
raw = bytes.fromhex("020001BD7F000001")        # Address 칸의 앞 8바이트
family = raw[0:2]                               # 02 00 = IPv4 (조사 PC 시험)
port = int.from_bytes(raw[2:4], "big")          # 445
ip = ".".join(str(b) for b in raw[4:8])         # 127.0.0.1
print(family.hex(" "), port, ip)
```

레지스트리 값을 헥스로 읽는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

### 공개 도구로 한 번

레지스트리는 RegRipper 플러그인 세 개로 봅니다. 하이브 경로는 수집한 파일로 바꿉니다.

```
rip.exe -r E:\case\SYSTEM -p shares
rip.exe -r E:\case\NTUSER.DAT -p mndmru
rip.exe -r E:\case\NTUSER.DAT -p mp2
```

- shares 는 `Shares` 값과 `Parameters` 의 `AutoShareServer`·`AutoShareWks`·`NullSessionShares` 를 보여 줍니다.
- mndmru 는 `MRUList` 와 경로 값을 보여 줍니다.
- mp2 는 볼륨·드라이브 문자·원격 드라이브를 나눠 시간순으로 보여 줍니다. 함께 나오는 MAC 주소 목록을 읽을 때의 함정은 MountPoints2 페이지에서 다룹니다.

30833 은 PowerShell 로 뽑습니다. `Path` 에는 수집한 Connectivity 로그 파일 경로를 넣습니다.

```powershell
Get-WinEvent -FilterHashtable @{ Path = 'E:\case\<수집한 Connectivity 로그>.evtx'; Id = 30833 } |
  ForEach-Object {
    $d = @{}
    ([xml]$_.ToXml()).Event.EventData.Data | ForEach-Object { $d[$_.Name] = $_.'#text' }
    [pscustomobject]@{ UTC = $_.TimeCreated.ToUniversalTime(); Share = $d.ServerName; Address = $d.Address }
  } | Sort-Object UTC
```

`TimeCreated` 는 분석 PC 의 시간대로 보여서 위 코드는 UTC 로 바꿔 출력합니다. `Address` 가 16진 문자열로 나오면 위 파이썬 풀이로 주소와 포트를 읽습니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 공유 폴더 접근 (5140·5145) | 서버 쪽에서 어느 계정이 어느 주소에서 들어와 어느 파일을 요청했는지 | [공유 폴더 접근](../event-logs/5140-5145.md) |
| 감사 정책과 로그 설정 | 5140·5145 가 남을 수 있는 설정이었는지 | [감사 정책과 로그 설정](../event-logs/audit-policy-log-settings.md) |
| MountPoints2 | 사용자 세션에 나타난 원격 드라이브 | [USB 저장장치 흔적](../external-devices/usb-storage-artifacts/index.md) |
| 셸백 | 탐색기로 연 네트워크 폴더 | [셸백](../file-folder-usage/shellbags/index.md) |
| 바로가기 파일·점프리스트 | 공유 안에서 연 파일 | [바로가기 파일](../file-folder-usage/lnk.md), [점프리스트](../file-folder-usage/jump-lists.md) |
| 프리페치 | `net use` 를 실행한 뒤 `NET.EXE`·`NET1.EXE` 항목이 생기거나 갱신됩니다 | [프리페치](../execution/prefetch/index.md) |
| PowerShell 명령 기록 | `net use`·`New-SmbMapping`·`New-SmbShare` 같은 명령이 남았는지 | [PowerShell 명령 기록](../execution/consolehost-history-txt.md) |
| 로그온·로그오프 | 30833 시각에 로그온해 있던 사용자 | [로그온·로그오프](../event-logs/logon-events/index.md) |
| 시간대 설정 | 현지 시각 기록과 맞출 때 | [시간대 설정](../system-account/time-zone.md) |

공유를 거쳐 자료를 옮겼는지는 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md)에서 다룹니다. 다른 PC 의 관리 공유로 옮겨 다닌 흔적은 [계정 탈취와 측면 이동](../../04-scenarios/incident/credential-theft-lateral-movement/index.md)에서 다룹니다.

## 실습

공개 시험 이미지(NIST CFReDS 등) 가운데 파일 공유나 네트워크 드라이브를 쓴 윈도 이미지를 골라 아래 질문을 풀어 봅니다.

1. SYSTEM 하이브의 `LanmanServer\Shares` 에 값이 있습니까? 공유 이름과 `Path` 는 무엇입니까?
2. 사용자마다 `Map Network Drive MRU` 가 있습니까? `MRUList` 순서대로 경로를 적어 봅니다.
3. MountPoints2 에 `#` 으로 시작하는 하위 키가 있습니까? 마지막 기록 시각은 언제입니까?
4. Connectivity 로그의 30833 에서 IPC$ 를 뺀 공유 경로는 몇 개입니까? 각 `Address` 를 풀면 서버 주소와 포트는 무엇입니까?
5. Security 채널에 31001·31010 이 있습니까? 실패한 사용자 이름과 경로는 무엇입니까?
6. 30833 시각에 로그온해 있던 사용자는 누구입니까? 그 사용자의 셸백·점프리스트에 같은 공유 경로가 있습니까?

## 참고 문헌

1. ForensicArtifacts/artifacts, artifacts/data/windows.yaml (main, 커밋 b4108448). https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/windows.yaml
2. keydet89/RegRipper3.0, plugins/shares.pl·mndmru.pl·mp2.pl (master, 커밋 ec96dd4a). https://codeload.github.com/keydet89/RegRipper3.0/tar.gz/refs/heads/master
