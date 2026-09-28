---
title: "테일스케일"
parent: "아티팩트 · 네트워크"
nav_order: 2425
---

# 테일스케일 (Tailscale)

테일스케일 (Tailscale) 은 여러 기기를 하나의 사설망처럼 묶어 주는 VPN 프로그램입니다. Windows 에서는 `%ProgramData%\Tailscale\server-state.conf` 에 로그인한 계정, 그 계정을 쓰는 로컬 사용자 SID, 무인 모드 설정이 남고, 서비스 로그에는 테일넷 주소(100.x.x.x)와 기기 사이 파일 전송이 남습니다. 전송이 끝나지 않은 파일은 `%ProgramData%\Tailscale\files` 아래에 `.partial` 파일로 남을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

테일스케일 계정으로 로그인하면 그 계정에 속한 기기들이 테일넷 (tailnet) 이라는 사설망을 이루고, 기기마다 100.x.x.x 대역의 테일넷 주소를 받습니다. 테일넷 안의 기기끼리는 테일드롭 (Taildrop) 으로 파일을 주고받을 수 있습니다[1]. USB 나 클라우드 업로드를 거치지 않는 파일 이동 경로라서 자료 유출을 조사할 때 따로 확인합니다.

Windows 클라이언트는 계정·설정을 상태 파일에, 연결과 파일 전송을 서비스 로그에 남깁니다. 한 PC 에서 여러 계정으로 로그인해 계정을 바꿔 쓸 수 있고, 계정마다 상태 파일에 프로필이 하나씩 생깁니다[2]. 무인 모드 (Run Unattended) 를 켜면 로그인한 사용자가 없어도 테일스케일이 계속 동작하고, 이 설정도 상태 파일에 남습니다[4].

| 기록 | 생기는 때 | 알려 주는 것 |
|---|---|---|
| `server-state.conf` | 로그인·계정 전환·설정 변경 때 | 계정 이메일과 표시 이름, 테일넷 이름, 로컬 사용자 SID, 무인 모드 여부 |
| 서비스 로그 (`Logs\tailscale-service*.txt`) | 서비스가 도는 동안 계속 | 테일넷 주소 사이의 연결, 파일 받기·보내기, 클라이언트 버전 |
| 테일드롭 임시 폴더 (`files\...`) | 파일을 받을 때 | 받는 중이거나 끝나지 않은 파일 |
| `Avatars` 폴더 | 계정 프로필 사진을 받아 올 때 | 계정 프로필 사진 |
| 설치 로그 | 설치할 때 | 설치 과정 |

## 위치와 버전별 차이

아래 위치는 Windows 11 25H2 에 테일스케일 1.96.3 을 설치했을 때 기준입니다[1].

| 기록 | 위치 | 메모 |
|---|---|---|
| 상태 파일 | `%ProgramData%\Tailscale\server-state.conf` | JSON 이고, 값은 Base64 로 인코딩돼 있습니다[2] |
| 서비스 로그 | `%ProgramData%\Tailscale\Logs\tailscale-service*.txt` | Velociraptor 수집 규칙이 이 이름으로 로그를 찾습니다[5] |
| 테일드롭 임시 폴더 | `%ProgramData%\Tailscale\files\` 아래 계정별 폴더 | 받은 파일은 여기에 먼저 저장된 뒤 `%USERPROFILE%\Downloads` 로 옮겨집니다. 끊긴 전송을 이어 받으려고 이렇게 합니다[1] |
| 받은 파일 | `%USERPROFILE%\Downloads` | |
| 프로필 사진 | `%LOCALAPPDATA%\Tailscale\Avatars` | |
| 설치 로그 | `%LOCALAPPDATA%\Temp\Tailscale*.log` | |

한 PC 에서 로그인한 계정이 둘이어도 `Avatars` 폴더에 파일이 하나만 생길 수 있습니다. Google 계정과 Microsoft 계정으로 로그인하면 상태 파일에서 `ProfilePicURL` 필드는 Google 계정 프로필에만 있습니다[2].

Linux 클라이언트는 비슷한 기록을 `/var/lib/tailscale` 에 남기고, `profile-data/*/netmap-cache` 폴더에 테일넷의 사용자, 기기, 기기 소유자, 라우팅 규칙을 담은 캐시 파일을 둡니다[7]. 이 캐시는 프로필 폴더 아래 `netmap-cache` 에 쓰이고, 자기 기기 정보나 네트워크 지도 전체를 쓸 때 서비스 로그에 `updating netmap in disk cache` 나 `writing netmap to disk cache` 가 남습니다[9]. Windows 에서는 `%ProgramData%\Tailscale` 아래에 `profile-data` 폴더와 `netmap-cache` 폴더가 있는지, 서비스 로그에 두 문구가 있는지 확인합니다. 캐시 파일 이름은 ASCII 문자열을 16진수로 적은 것이라 `706565722d...` 는 `peer-...`, `646e73` 은 `dns` 로 읽습니다[7].

## 구조

### 상태 파일 (server-state.conf)

파일은 JSON 객체 하나이고, 키마다 값이 Base64 문자열입니다. 값을 풀면 아래와 같습니다[2][3][4]. 계정 이름, SID, ID 는 만든 예시입니다.

```
{
  "_current/S-1-5-21-1111111111-2222222222-3333333333-1001": "profile-a1b2",
  "_machinekey": "privkey:…",
  "_profiles": "{ \"a1b2\": { \"ID\": \"a1b2\", \"Name\": \"user@example.com\", … } }",
  "profile-a1b2": "{ \"ControlURL\": \"https://controlplane.tailscale.com\", \"WantRunning\": true, … }",
  "server-mode-start-key": null
}
```

| 키 | 알려 주는 것 |
|---|---|
| `_current/` 뒤에 SID | 그 로컬 사용자가 지금 쓰는 테일스케일 프로필입니다. 로컬 사용자마다 한 줄씩 생깁니다[3] |
| `_machinekey` | 기기 키입니다. `privkey:` 로 시작하는 개인 키라 보고서에 옮기지 않습니다 |
| `_profiles` | 로그인한 적 있는 계정 목록입니다. 프로필마다 `ID`, `Name`(계정), `NetworkProfile.MagicDNSName`(테일넷 이름, `tail….ts.net`), `UserProfile.LoginName`·`DisplayName`, `NodeID`, `LocalUserID`, `ControlURL` 이 있습니다 |
| `profile-` 뒤에 ID | 그 계정의 설정입니다. `WantRunning`, `LoggedOut`, `ExitNodeID`·`ExitNodeIP`, `RunSSH`, `AdvertiseRoutes`, 무인 모드일 때 `ForceDaemon` 이 들어 있습니다 |
| `server-mode-start-key` | 무인 모드가 꺼져 있으면 `null` 이고, 켜면 무인 모드로 쓰는 프로필의 키(예: `profile-0533`)가 Base64 로 들어갑니다[4] |

`LocalUserID` 값과 `_current/` 키 이름 뒤의 문자열은 그 계정으로 테일스케일을 쓴 Windows 로컬 사용자의 SID 입니다. 그래서 어느 로컬 사용자가 어느 테일스케일 계정을 썼는지 이 파일만으로 이어 볼 수 있습니다[3]. `DisplayName` 에는 Google·Microsoft 계정을 만들 때 적은 이름이 그대로 들어갑니다[2].

무인 모드를 켜면 두 곳이 바뀝니다. `server-mode-start-key` 가 `null` 에서 프로필 키로 바뀌고, 그 프로필의 설정에 `"ForceDaemon": true` 가 생깁니다[4]. `ForceDaemon` 은 로그인한 사용자가 없거나 GUI 가 꺼져도 테일스케일이 계속 동작하게 하는 설정이고, 1.96.3 에서는 Windows 에만 적용됩니다[8]. 1.96.3 의 상태 키에는 테일드롭으로 파일을 한 번이라도 받았는지(일부만 받은 경우 포함) 표시하는 `_taildrop-received` 도 있습니다[8]. 실제 파일에 이 키가 있는지 확인합니다.

### 서비스 로그

로그 줄은 `시각: 내용` 형식입니다. 아래는 파일을 받은 PC 의 줄이고, 주소 일부는 원문에서 `x` 로 가린 값입니다[1].

```
2026-04-21T11:10:28.000-04:00: [v1] Accept: TCP{100.105.x.x:56010 > 100.113.x.x:36843} 52 tcp ok
2026-04-21T11:10:28.033-04:00: peerapi: got put of <=1MB in 0s from 100.105.x.x/0x7ff60151dc40
```

| 문자열 | 남는 곳 | 알려 주는 것 |
|---|---|---|
| `peerapi: got put of … in … from 주소/…` | 받는 PC | 파일 하나를 다 받은 시각, 대략의 크기, 걸린 시간, 보낸 기기의 테일넷 주소[1] |
| `localapi: [PUT] /localapi/v0/file-put/` | 보내는 PC | 파일 보내기를 요청한 시각. 받는 기기 주소는 이 줄에 없습니다[1] |
| `[v1] Accept: TCP{주소:포트 > 주소:포트} …` | 양쪽 | 테일넷 주소 사이의 TCP 연결 |
| `v1.96.3-t3ffddb134-g460d8764a` | 양쪽 | 그 줄을 남긴 클라이언트 버전 |

크기는 정확한 바이트 수가 아닙니다. 1.96.3 코드는 1KB 이하면 `<=1KB`, 1MB 이하면 `<=1MB`, 그보다 크면 MB 단위로 내림한 값을 `~141MB` 처럼 적습니다[10]. 주소 뒤 `/` 다음 자리에는 상대 기기 이름이 아니라 `0x7ff60151dc40` 같은 16진수 값이 찍힙니다[1]. 1.96.3 코드가 이 자리에 기기 이름을 돌려주는 메서드(`ComputedName`)를 호출하지 않고 그대로 넘겨서, 이름 대신 메모리 주소가 찍힙니다[10]. 이 값으로 보낸 기기를 특정하지 않습니다.

받다가 취소한 전송의 예시 로그에는 `got put of` 줄이 없고, 같은 주소·포트의 `Accept: TCP{…} 1280 tcp non-syn` 줄이 10초 간격으로 보입니다[1]. `got put of` 줄은 받기가 오류 없이 끝났을 때만 남습니다[10].

### 테일드롭 임시 파일

받는 중인 파일은 원래 이름 뒤에 보낸 기기의 고정 ID(StableID)와 `.partial` 이 붙어 `report.pdf.n12345CNTRL.partial`(만든 예시) 형식이 됩니다[10]. Windows 가 지우지 못한 파일 옆에는 같은 이름에 `.deleted` 를 붙인 표시 파일이 생기는데, 이 파일은 Windows 에서만 만듭니다[10].

1.96.3 코드는 받다가 끊긴 `.partial` 파일을 1시간 뒤에 지웁니다[6][10]. 서비스가 시작할 때는 상태 파일의 `_taildrop-received` 에 값이 있을 때만 폴더를 살펴, 진행 중인 전송이 없는 `.partial` 파일을 삭제 대기열에 넣고 `.deleted` 표시 파일은 원래 파일과 함께 바로 지웁니다[10]. 그래서 PC 를 끄기 직전에 끊긴 전송의 `.partial` 파일은 디스크 이미지에 남아 있을 수 있습니다.

## 증거로서 의미

**증명하는 것**

- `_profiles` 의 프로필 하나는 이 PC 에서 그 테일스케일 계정으로 로그인한 적이 있다는 기록입니다. 계정 이메일, 표시 이름, 테일넷 이름이 함께 남습니다.
- `LocalUserID` 와 `_current/` 의 SID 는 그 계정을 쓴 Windows 로컬 사용자를 가리킵니다.
- `server-mode-start-key` 에 값이 있고 그 프로필에 `"ForceDaemon": true` 가 있으면, 수집 시점에 그 계정으로 무인 모드가 켜져 있었습니다.
- `got put of` 줄은 그 시각에 이 PC 가 그 테일넷 주소의 기기에게서 파일 하나를 다 받았다는 기록입니다.
- `file-put` 줄은 그 시각에 이 PC 에서 파일 보내기를 요청했다는 기록입니다.
- `files` 아래의 `.partial` 파일은 테일드롭으로 받다가 끝나지 않은 파일의 내용입니다.

**증명하지 못하는 것**

- 로그의 파일 전송 줄에는 파일 이름이 없습니다. 받은 파일은 `Downloads` 폴더의 파일 시스템 흔적과 시각으로 맞춰 봅니다.
- 크기는 범위나 MB 단위 근삿값입니다.
- `file-put` 줄 앞뒤의 `Accept: TCP` 줄에 받는 기기의 주소가 보일 수 있지만, 그 줄이 전송과 관계없는 기기 사이 통신일 수도 있습니다[1]. 받는 기기를 이 줄만으로 단정하지 않습니다.
- 테일넷 주소는 테일넷 안에서만 뜻이 있는 주소입니다. 그 주소를 쓴 기기와 소유자는 상대 기기나 테일스케일 관리 콘솔 자료로 확인합니다.
- 프로필이 있다고 지금도 로그인해 있다는 뜻은 아닙니다. 그 프로필의 `LoggedOut`·`WantRunning` 값과 서비스 로그를 함께 봅니다.
- 상태 파일은 계정 설정만 담고 있어 언제 로그인했는지는 알려 주지 않습니다.

보고서에는 기록으로 확인되는 만큼만 씁니다. 예를 들면 "서비스 로그에 2026-04-21 11:10:28(UTC-4) 테일넷 주소 100.105.x.x 인 기기에서 1MB 이하 파일 하나를 받은 기록(`peerapi: got put of <=1MB`)이 있다. 로그에는 파일 이름이 없다." 처럼 씁니다. 예의 시각과 주소는 공개 예시 값입니다.

## 시각 해석

- 서비스 로그의 시각은 밀리초까지 있는 ISO 8601 형식이고, 끝에 UTC 와의 차이가 붙습니다(예: `2026-04-21T11:10:28.033-04:00`)[1]. 이 차이를 빼면 UTC 가 됩니다.
- `got put of` 줄은 전송이 끝난 시각에 남습니다. 같은 줄의 걸린 시간(`in 2.2s`)을 빼면 전송을 시작한 시각을 추정할 수 있습니다.
- 상태 파일에는 시각 필드가 없습니다. 파일이 마지막으로 바뀐 때는 [마스터 파일 테이블](../filesystem/mft.md)의 시각으로 봅니다.
- `.partial` 파일과 `Downloads` 로 옮겨진 파일의 만든 시각·수정 시각도 파일 시스템에서 읽습니다.

## 함정과 한계

- **값이 Base64 입니다.** `server-state.conf` 에서 계정 이메일을 문자열로 검색하면 나오지 않습니다. 먼저 값을 풀고 검색합니다.
- **프로필 사진 파일 수와 계정 수가 다를 수 있습니다.** `Avatars` 폴더만 보고 계정 수를 세지 않습니다. 계정 목록은 `_profiles` 에서 봅니다.
- **임시 파일은 오래 남지 않습니다.** 서비스가 돌고 있으면 끝나지 않은 `.partial` 파일은 1시간 뒤 지워집니다. 실행 중인 PC 를 수집한다면 이 폴더를 먼저 복사합니다.
- **개인 키가 들어 있습니다.** `_machinekey`, `PrivateNodeKey`, `NetworkLockKey` 값은 보고서나 공유 자료에 옮기지 않습니다.
## 직접 분석해 보기

### 헥스로 한 번

상태 파일과 로그는 텍스트입니다. 헥스로 볼 곳은 `Avatars` 폴더의 파일인데, HTTP/2 응답으로 보이는 데이터 안에 프로필 사진이 들어 있어 헥스 편집기로 잘라 낼 수 있습니다[1]. 파일에서 JPEG 시그니처 `FF D8 FF` 나 PNG 시그니처 `89 50 4E 47 0D 0A 1A 0A` 를 찾아 그 위치부터 이미지 끝까지 잘라 냅니다.

상태 파일의 Base64 값은 아래처럼 풉니다. 무인 모드를 켠 뒤의 `server-mode-start-key` 값입니다[4].

| 단계 | 값 |
|---|---|
| 파일에 적힌 값 | `cHJvZmlsZS0wNTMz` |
| Base64 를 푼 바이트 | `70 72 6F 66 69 6C 65 2D 30 35 33 33` |
| ASCII 로 읽음 | `profile-0533` |

SID 를 읽는 법은 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md)에서, 텍스트 인코딩을 판별하는 법은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)에서 다룹니다.

### 공개 도구로 한 번

Velociraptor 의 `Windows.Applications.Tailscale` 수집 규칙은 `server-state.conf` 의 값을 Base64 로 풀어 보여 주고, `Logs\tailscale-service*.txt` 를 줄 단위로 읽고, `files\*\*.partial` 파일을 수집합니다[5]. 수집한 파일을 직접 볼 때는 아래 Python 코드로 상태 파일을 풉니다.

```python
import base64, json

path = r"E:\mount\ProgramData\Tailscale\server-state.conf"   # 마운트한 경로로 바꿉니다

with open(path, encoding="utf-8-sig") as f:
    raw = json.load(f)

state = {k: base64.b64decode(v).decode("utf-8", "replace") if isinstance(v, str) else v
         for k, v in raw.items()}

for k, v in state.items():
    if k.startswith("_current/"):
        print("로컬 사용자 SID", k.split("/", 1)[1], "→ 지금 프로필", v)
print("무인 모드 프로필(server-mode-start-key):", state.get("server-mode-start-key"))

profiles = json.loads(state.get("_profiles") or "{}")
for p in (profiles.values() if isinstance(profiles, dict) else profiles):
    print("\n프로필", p.get("ID"), "| 계정", p.get("Name"),
          "| 표시 이름", p.get("UserProfile", {}).get("DisplayName"),
          "| 로컬 사용자", p.get("LocalUserID"),
          "| 테일넷", p.get("NetworkProfile", {}).get("MagicDNSName"),
          "| NodeID", p.get("NodeID"))

for k, v in state.items():
    if k.startswith("profile-"):
        prefs = json.loads(v)
        print(k, {f: prefs.get(f) for f in ("ForceDaemon", "WantRunning", "LoggedOut", "ExitNodeIP", "RunSSH")})
```

개인 키 값은 출력하지 않도록 필드를 골라 뽑습니다. 서비스 로그의 파일 전송 줄은 PowerShell 로 찾습니다.

```powershell
$root = 'E:\mount'   # 마운트한 경로로 바꿉니다
Get-ChildItem "$root\ProgramData\Tailscale\Logs\tailscale-service*.txt" |
  Select-String -Pattern 'peerapi: got put of', 'localapi: \[PUT\] /localapi/v0/file-put/', 'netmap to disk cache', 'netmap in disk cache'
```

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 받은 파일의 파일 시스템 시각 | `Downloads` 에 생긴 파일과 `got put of` 시각이 맞는지 | [마스터 파일 테이블](../filesystem/mft.md) |
| 사용자 프로필 목록 | `LocalUserID` 의 SID 를 사용자 이름에 맞춤 | [사용자 프로필 목록](../system-account/profilelist.md) |
| 서비스 설치 (7045·4697) | 테일스케일 서비스를 설치한 시각 | [서비스 설치](../event-logs/7045-4697.md) |
| 설치 프로그램 | 설치 여부와 버전 | [설치 프로그램](../system-account/uninstall.md) |
| 프리페치 | 테일스케일 실행 파일의 실행 시각과 횟수 | [프리페치](../execution/prefetch/index.md) |
| SRUM 네트워크 사용량 | 프로그램별 송수신 바이트로 전송량 규모를 봄 | [네트워크 사용량](../execution/system-resource-usage-monitor/network-data-usage.md) |
| 섀도 복사본 | 예전 `server-state.conf` 와 지워진 `.partial` 파일 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 윈도 내장 VPN | 내장 VPN 연결 기록과 구분 | [VPN 연결 기록](vpn-connections.md) |
| 시간대 설정 | 로그 시각의 UTC 차이와 PC 시간대가 맞는지 | [시간대 설정](../system-account/time-zone.md) |

자료 유출 조사 전체 흐름은 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md)에서 다룹니다.

## 실습

공개 데이터셋(NIST CFReDS 등) 가운데 테일스케일을 설치한 Windows 이미지를 골라 아래 질문을 풀어 봅니다. 없으면 가상 머신 두 대에 테일스케일을 설치해 파일을 주고받은 뒤 이미지를 떠서 풉니다.

1. `server-state.conf` 의 `_profiles` 에 계정이 몇 개 있습니까? 각 계정의 `Name`, `DisplayName`, `MagicDNSName` 은 무엇입니까?
2. `_current/` 줄의 SID 는 어느 로컬 사용자입니까? `LocalUserID` 와 같습니까?
3. `server-mode-start-key` 는 `null` 입니까? 값이 있다면 그 프로필에 `"ForceDaemon": true` 가 있습니까?
4. 서비스 로그에 `got put of` 줄이 몇 개 있습니까? 각 줄의 시각을 UTC 로 바꾸면 `Downloads` 폴더의 어느 파일과 시각이 맞습니까?
5. `file-put` 줄이 있습니까? 그 앞뒤 `Accept: TCP` 줄에 어떤 테일넷 주소가 보입니까?
6. `%ProgramData%\Tailscale\files` 아래에 `.partial` 이나 `.deleted` 파일이 있습니까?

## 참고 문헌

1. ogmini, "Examining Tailscale Artifacts" (2026-04-21). https://ogmini.github.io/2026/04/21/Examining-Tailscale-Artifacts.html
2. ogmini, "Examining Tailscale Artifacts - Part 2" (2026-04-22). https://ogmini.github.io/2026/04/22/Examining-Tailscale-Artifacts-Part-2.html
3. ogmini, "Examining Tailscale Artifacts - Part 3" (2026-04-23). https://ogmini.github.io/2026/04/23/Examining-Tailscale-Artifacts-Part-3.html
4. ogmini, "Examining Tailscale Artifacts - Part 4" (2026-04-24). https://ogmini.github.io/2026/04/24/Examining-Tailscale-Artifacts-Part-4.html
5. Velocidex/velociraptor-docs, content/exchange/artifacts/Windows.Applications.Tailscale.yaml (커밋 428b2fb). https://github.com/Velocidex/velociraptor-docs/blob/master/content/exchange/artifacts/Windows.Applications.Tailscale.yaml
6. ogmini, "Examining Tailscale Artifacts - Part 6" (2026-06-23). https://ogmini.github.io/2026/06/23/Examining-Tailscale-Artifacts-Part-6.html
7. ogmini, "Examining Tailscale Artifacts - Part 7" (2026-07-13). https://ogmini.github.io/2026/07/13/Examining-Tailscale-Artifacts-Part-7.html
8. tailscale/tailscale v1.96.3, ipn/store.go, ipn/prefs.go. https://github.com/tailscale/tailscale/blob/v1.96.3/ipn/store.go , https://github.com/tailscale/tailscale/blob/v1.96.3/ipn/prefs.go
9. tailscale/tailscale (커밋 ca79c1e), ipn/ipnlocal/diskcache.go. https://github.com/tailscale/tailscale/blob/ca79c1e09b4ba34a0b8f071835e1383ba397bdf0/ipn/ipnlocal/diskcache.go
10. tailscale/tailscale v1.96.3, feature/taildrop/peerapi.go, feature/taildrop/taildrop.go, feature/taildrop/delete.go. https://github.com/tailscale/tailscale/tree/v1.96.3/feature/taildrop
