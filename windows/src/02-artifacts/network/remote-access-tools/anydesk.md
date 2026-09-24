# 애니데스크 (AnyDesk)

> 상위 허브: [원격 제어 프로그램 (Remote Access Tools)](index.md)

## 한 줄 요약

애니데스크 (AnyDesk) 는 원격 지원 프로그램입니다. 받는 쪽 PC 의 `connection_trace.txt` 에는 들어온 접속이 한 줄씩 남고, 줄마다 날짜·시각, 승인 방식, AnyDesk ID 가 적힙니다. trace 로그(`ad.trace`, `ad_svc.trace`)에는 상대 ID 와 외부 IP 주소가 남습니다.

## 무엇을 기록하나 · 왜 생기나

AnyDesk 의 흔적은 세 갈래입니다.

- 접속 목록 (`connection_trace.txt`): 들어온 접속만 적습니다. 받는 쪽에만 생깁니다.
- trace 로그: 사용자 화면 쪽 로그(`ad.trace`)와 서비스 로그(`ad_svc.trace`)가 따로 있습니다. 접속과 IP 는 두 로그에 같은 내용으로 남습니다.
- 설정 파일 (`*.conf`): 설정 값, 무인 접속 비밀번호의 해시, 인증서가 들어 있습니다.

설치할 때는 서비스, 프린터 드라이버, 시작 프로그램 바로가기가 함께 생깁니다. 채팅을 쓰면 채팅 파일도 남습니다. 받는 쪽과 거는 쪽이 무엇인지는 [허브](index.md)에서 정리합니다.

## 위치와 버전별 차이

아래 경로는 Synacktiv 가 AnyDesk 7.0.14.0 으로 시험한 결과에 LOLRMM 목록을 더한 것입니다.

### 파일

| 흔적 | 경로 | 메모 |
|---|---|---|
| 설치 폴더 | `C:\Program Files (x86)\AnyDesk` | 설치할 때 바꿀 수 있습니다 |
| 접속 목록 | `%PROGRAMDATA%\AnyDesk\connection_trace.txt` | 받는 쪽만. LOLRMM 은 `%APPDATA%\AnyDesk\connection_trace.txt` 도 적습니다 |
| 서비스 로그 | `%PROGRAMDATA%\AnyDesk\ad_svc.trace` | |
| 사용자 화면 쪽 로그 | `%APPDATA%\AnyDesk\ad.trace` | |
| 설정 파일 | `%APPDATA%\AnyDesk\user.conf`, `system.conf`, `service.conf` / `%PROGRAMDATA%\AnyDesk\service.conf`, `system.conf` | |
| 채팅 | `%APPDATA%\AnyDesk\chat\*.txt` | 채팅을 쓴 경우 |
| 프린터 드라이버 설치 파일 | `%APPDATA%\AnyDesk\printer_driver` | |
| 시작 프로그램 바로가기 | `%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\StartUp\AnyDesk.lnk` | |
| 뜻을 확인하지 못한 경로 | `C:\Users\*\Videos\AnyDesk\*.anydesk`, `C:\Windows\SysWOW64\config\systemprofile\AppData\Roaming\AnyDesk\*` | LOLRMM 이 흔적 목록에 올렸습니다. 무엇을 담는지는 이번 자료로 확인하지 못했습니다 |

### 레지스트리

- `HKLM\SOFTWARE\Clients\Media\AnyDesk`
- `HKLM\SYSTEM\CurrentControlSet\Services\AnyDesk`
- `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\AnyDesk`
- `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Print\Printers\AnyDesk Printer\*`

### 설치할 때 남는 기록

| 기록 | 내용 |
|---|---|
| System 7045 | ServiceName "AnyDesk Service", ImagePath `"C:\Program Files (x86)\AnyDesk\AnyDesk.exe" --service`, 자동 시작 |
| Security 4697 | 같은 서비스 설치. 감사 정책이 켜져 있을 때만 남습니다 |
| Microsoft-Windows-Shell-Core/Operational 28115 | 앱 목록(App Resolver Cache)에 AnyDesk 바로가기가 추가된 기록. 설치 날짜와 설치한 사용자의 SID 를 알 수 있습니다. 예: `"AppID":"prokzult ad","Flags":49,"Name":"AnyDesk"` |
| `C:\Windows\inf\setupapi.dev.log` | 기본 AnyDesk 프린터 드라이버 설치 기록 |
| 프로세스 명령줄 | 조용한 설치는 `--install`, `--start-with-win`, `--silent` 인자를 함께 씁니다. 명령줄로 비밀번호를 넣으면 `echo <비밀번호> \| anydesk.exe --set-password` 꼴이 됩니다 |

Sigma 규칙 "Suspicious Application Installed" 는 28115 에서 AppID `prokzult ad` 를 찾습니다. 명령줄 두 꼴도 각각 Sigma 규칙이 있습니다. 서비스 설치 이벤트 자체는 [서비스 설치](../../event-logs/7045-4697.md)에서 다룹니다.

## 구조

### 접속 목록 (connection_trace.txt)

줄 모양은 `Incoming <날짜, 시각> <승인 방식> <숫자> <숫자>` 입니다. 아래는 공개 자료의 예시입니다.

```
Incoming 2022-08-23, 10:23 Passwd 547911884 547911884
Incoming 2022-09-28, 12:39 User 442226597 442226597
```

날짜는 년-월-일 순서이고 시각은 분까지만 있습니다(예시 기준). 승인 방식 `Passwd` 는 비밀번호를 넣고 들어온 접속이고, `User` 는 이 PC 의 사용자가 수락한 접속입니다.

끝의 두 숫자를 Synacktiv 는 상대 ID 와 로컬 ID 로 적었습니다. 그런데 공개 예시에서는 두 값이 같아서 두 숫자의 뜻을 확정하지 못했습니다. trace 로그의 Client-ID 줄과 맞춰 보고 판단합니다.

### trace 로그 (ad.trace, ad_svc.trace)

아래는 LOLRMM 이 공개한 줄 예시입니다.

```
info 2022-09-28 12:39:26.845       lsvc   9952   9944   21                anynet.any_socket - …
```

앞에서부터 수준(info), 날짜와 시각(밀리초까지), 구성 요소(lsvc), 숫자 칸(프로세스·스레드 번호 등)이 옵니다. 그 뒤에 모듈 이름과 내용이 옵니다. 칸마다 정확한 이름과 뜻은 공식 자료로 확인하지 못했습니다.

접속을 찾을 때는 아래 문자열을 검색합니다. 예시 값은 공개 자료의 것입니다.

| 문자열 (예시) | 알려 주는 것 |
|---|---|
| `anynet.any_socket - Client-ID: 442226597 (FPR: 8e28a2a25b30).` | 상대 AnyDesk ID 와 지문(FPR) |
| `anynet.any_socket - Logged in from 12.xx.xx.21:59562 on relay 80e496c0.` | 상대의 외부 IP 와 포트 |
| `anynet.relay_conn - External address: 34.xx.xx.123:46798` | 이 PC 의 외부 IP 와 포트 |
| `New user data. Client-ID: 294433414` | 이 PC 의 AnyDesk ID |
| `Preparation of 1 files completed (io_ok)` | 파일 전송. 파일 이름은 적히지 않습니다 |

공개 예시에서는 접속 목록의 `2022-09-28, 12:39 User 442226597` 줄과 trace 로그의 `Client-ID: 442226597` 줄에 같은 ID 가 나옵니다. 두 파일을 ID 와 시각으로 이어 볼 수 있다는 뜻입니다. 이 판단은 공개 예시 두 개를 비교한 것입니다.

### 설정 파일

`system.conf` 와 `user.conf` 에는 설정 변수와 함께 인증서와 개인 키(PEM)가 들어 있습니다. 무인 접속 비밀번호를 정하면 솔트 (salt) 를 섞은 해시가 `ad.anynet.pwd_hash=…` 줄로 저장됩니다. 거는 쪽 설정에는 원격 파일 창의 시작 경로가 남습니다. 예: `ad.session.remote_browser_start_path=294422414:C*\\Users\\john.doe\\Documents`

### 채팅 파일

`%APPDATA%\AnyDesk\chat\*.txt` 에 사용자 이름과 메시지가 남습니다. 예: `john.doe: bonjour`

## 증거로서 의미

**증명하는 것**

- 접속 목록 한 줄은 그 시각에 이 PC 로 들어온 접속 기록입니다. 승인 방식이 같은 줄에 남습니다.
- `User` 줄은 누군가 이 PC 에서 접속을 수락했다는 기록입니다.
- trace 로그의 `Logged in from` 줄은 상대가 인터넷에 나온 IP 와 포트를 보여 줍니다.
- `ad.anynet.pwd_hash` 줄이 있으면 무인 접속 비밀번호를 정한 적이 있습니다.
- 28115 는 AnyDesk 를 설치한 날짜와 설치한 사용자의 SID 를 보여 줍니다.
- 채팅 파일은 보낸 사람 이름과 메시지를 보여 줍니다.

**증명하지 못하는 것**

- 거는 쪽 PC 에는 접속 목록이 생기지 않습니다. 이 파일이 없다고 AnyDesk 를 쓰지 않았다고 단정하지 않습니다.
- `User` 줄에는 수락한 사람이 누구인지 없습니다.
- 파일 전송 줄에는 파일 이름이 없습니다. 어떤 파일을 옮겼는지는 파일 시스템 흔적으로 따로 확인합니다.
- ID·지문·IP 는 사람을 가리키지 않습니다. 공유기나 VPN 뒤의 IP 는 PC 한 대를 가리키지 않을 수 있습니다.
- 비밀번호 해시는 솔트를 섞은 값입니다. 비밀번호 자체를 보여 주지 않습니다.
- 4697 은 감사 정책이 켜져 있을 때만 남습니다. 4697 이 없다고 설치가 없었다고 단정하지 않습니다.

보고서에는 기록이 말하는 만큼만 씁니다. 예를 들면 "`connection_trace.txt` 에 2022-09-28 12:39(시간대 미확인), 승인 방식 User, ID 442226597 인 들어온 접속 기록이 있다. 이 기록만으로는 수락한 사람과 세션 중에 한 일을 알 수 없다." 처럼 씁니다. 예의 값은 공개 예시입니다.

## 시각 해석

- 접속 목록의 시각은 분까지만 있습니다. 다른 기록과 맞출 때는 1분 폭으로 봅니다.
- 접속 목록과 trace 로그의 시각이 UTC 인지는 공개 자료로 확인하지 못했습니다.
- 28115 와 7045 의 기록 시각은 이벤트 레코드 시각입니다. 레코드 시각을 읽는 법은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.
- 설치 직후에 trace 로그 줄이 있으면, 그 시각을 7045 기록 시각과 견주어 trace 로그의 시간대를 가늠합니다. PC 의 시간대 설정은 [시간대 설정](../../system-account/time-zone.md)에서 봅니다.

## 함정과 한계

- **설치 폴더를 바꿀 수 있습니다.** 서비스 ImagePath 로 실제 위치를 확인합니다.
- **접속 목록이 두 곳에 있을 수 있습니다.** `%PROGRAMDATA%\AnyDesk\` 와 `%APPDATA%\AnyDesk\` 를 모두 수집합니다.
- **끝의 두 숫자의 뜻이 확정되지 않았습니다.** 상대 ID 로 단정하기 전에 trace 로그와 맞춰 봅니다.
- **trace 로그 두 개는 접속·IP 내용이 같습니다.** 한쪽이 지워졌으면 다른 쪽을 봅니다.
- **시각이 분 단위입니다.** 짧은 접속 여러 개가 같은 분에 몰리면 순서를 가리기 어렵습니다.

## 직접 분석해 보기

### 헥스로 한 번

이 페이지의 파일은 모두 텍스트입니다. 헥스로 풀어야 할 이진 구조가 없어 헥스 예시를 싣지 않습니다. 파일 인코딩은 자료에 적혀 있지 않습니다. 파일 앞 몇 바이트를 헥스로 보고 BOM 이 있는지 확인한 뒤 읽습니다. 인코딩을 가리는 법은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)에서 다룹니다.

### 공개 도구로 한 번

trace 로그에서 접속 줄만 뽑을 때는 PowerShell 로 충분합니다.

```powershell
$root = 'E:\mount'   # 마운트한 경로로 바꿉니다
Get-ChildItem "$root\ProgramData\AnyDesk\*.trace", "$root\Users\*\AppData\Roaming\AnyDesk\*.trace" |
  Select-String -Pattern 'Client-ID:', 'Logged in from', 'External address', 'files completed'
```

접속 목록은 아래 Python 코드로 칸을 나눕니다.

```python
import re

path = r"E:\mount\ProgramData\AnyDesk\connection_trace.txt"   # 마운트한 경로로 바꿉니다
pat = re.compile(r"^Incoming (\d{4}-\d{2}-\d{2}), (\d{2}:\d{2})\s+(\S+)\s+(\d+)\s+(\d+)")

with open(path, encoding="utf-8", errors="replace") as f:
    for line in f:
        m = pat.match(line.strip())
        if m:
            print(*m.groups())   # 날짜, 시각, 승인 방식, 숫자1, 숫자2
```

28115 는 PowerShell 로 거릅니다. 수집한 evtx 파일을 열 때는 `Path` 에 그 파일 경로를 넣습니다.

```powershell
Get-WinEvent -FilterHashtable @{ Path = 'E:\case\Shell-Core-Operational.evtx'; Id = 28115 } |
  Where-Object { $_.Message -like '*AnyDesk*' } |
  Select-Object @{ n = 'UTC'; e = { $_.TimeCreated.ToUniversalTime() } }, UserId, Message
```

`TimeCreated` 는 분석 PC 의 시간대로 바뀌어 나옵니다. 그래서 위 코드는 UTC 로 바꿔 출력합니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 서비스 설치 (7045·4697) | "AnyDesk Service" 설치 시각과 ImagePath | [서비스 설치](../../event-logs/7045-4697.md) |
| 프로세스 생성 · Sysmon 1 | 조용한 설치 인자, `--set-password` 명령줄 | [프로세스 생성](../../event-logs/4688.md), [Sysmon 로그](../../event-logs/sysmon/index.md) |
| Sysmon 3 (네트워크 연결) | 들어온 연결은 AnyDesk.exe 의 `Initiated=false` 로 보입니다(Sigma 규칙) | [Sysmon 로그](../../event-logs/sysmon/index.md) |
| 프리페치 | `ANYDESK.EXE-[A-F0-9]{8}.pf`. 실행 시각과 횟수 | [프리페치](../../execution/prefetch/index.md) |
| 그 밖의 실행 흔적 | BAM·UserAssist·심캐시·AmCache·점프 목록 | [허브](index.md) |
| 로그온 자동실행 | `StartUp\AnyDesk.lnk` | [로그온 자동실행](../../persistence/run-runonce-startup-folder.md) |
| 설치 프로그램 | `Uninstall\AnyDesk` 키 | [설치 프로그램](../../system-account/uninstall.md) |
| 사용자 프로필 목록 | 28115 의 SID 를 사용자 이름에 맞춤 | [사용자 프로필 목록](../../system-account/profilelist.md) |
| DNS·프록시 기록 | 설치 때 `boot.net.anydesk.com:443`, 쓰는 중에는 `relay-[a-f0-9]{8}.net.anydesk.com:443`. User-Agent `AnyDesk/*` | — |
| 메모리 | 이름 있는 파이프 `adprinterpipe` | [메모리 분석](../../../03-techniques/analysis/memory-forensics/index.md) |

## 실습

공개 검체(NIST CFReDS 등) 가운데 AnyDesk 흔적이 있는 이미지를 골라 아래 질문을 풀어 봅니다.

1. `connection_trace.txt` 는 `%PROGRAMDATA%` 와 `%APPDATA%` 가운데 어디에 있습니까? 줄은 몇 개입니까?
2. 승인 방식이 `Passwd` 인 줄과 `User` 인 줄은 각각 몇 개입니까?
3. 각 줄의 ID 가 trace 로그의 `Client-ID:` 줄에도 나옵니까? 그 부근의 `Logged in from` 줄에 적힌 IP 는 무엇입니까?
4. 설정 파일에 `ad.anynet.pwd_hash` 줄이 있습니까?
5. 28115 에서 AnyDesk 가 추가된 날짜와 SID 를 찾습니다. 7045 의 설치 시각과 맞습니까?

## 참고 문헌

1. Synacktiv, "Legitimate RATs: a comprehensive forensic analysis of the usual suspects" (Théo Letailleur, 2022-10-20). https://www.synacktiv.com/publications/legitimate-rats-a-comprehensive-forensic-analysis-of-the-usual-suspects.html
2. LOLRMM API, rmm_tools.json (AnyDesk 항목). https://lolrmm.io/api/rmm_tools.json
3. SigmaHQ 규칙 저장소 (커밋 16eb587, 2026-09-22). rules/windows/builtin/shell_core/win_shell_core_susp_packages_installed.yml, rules/windows/network_connection/net_connection_win_remote_access_tools_anydesk_incoming_connection.yml, rules/windows/process_creation/proc_creation_win_remote_access_tools_anydesk_silent_install.yml, rules/windows/process_creation/proc_creation_win_remote_access_tools_anydesk_piped_password_via_cli.yml. https://github.com/SigmaHQ/sigma
