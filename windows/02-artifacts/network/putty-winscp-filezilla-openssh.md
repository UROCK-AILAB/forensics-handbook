---
title: "SSH·FTP 도구 흔적"
parent: "아티팩트 · 네트워크"
nav_order: 2430
---

# SSH·FTP 도구 흔적 (PuTTY·WinSCP·FileZilla·OpenSSH)

> 이 페이지에서 "" 는 Windows 11 Home 25H2(빌드 26200.9457) PC 한 대에서 직접 본 사실을 뜻합니다. 조사 PC 에는 PuTTY·WinSCP·FileZilla 가 설치돼 있지 않았습니다. 그래서 PuTTY·WinSCP 내용은 공식 문서와 공개 도구 소스로만 확인했습니다.

## 한 줄 요약

PuTTY 와 WinSCP 는 접속한 서버의 흔적을 사용자 레지스트리(NTUSER.DAT)에 남깁니다. 윈도 내장 OpenSSH 클라이언트는 사용자 홈의 `.ssh` 폴더에 접속 설정과 서버 호스트 키를 평문으로 남깁니다. OpenSSH 서버를 켠 PC 에는 `%programdata%\ssh` 아래 설정·키 파일과 OpenSSH 이벤트 채널이 흔적으로 남습니다. FileZilla 는 이번에 공식 문서를 열지 못해 구체적인 위치를 싣지 않습니다.

## 무엇을 기록하나 · 왜 생기나

SSH 클라이언트는 처음 접속한 서버의 호스트 키 (host key) 를 저장해 두고, 다음 접속 때 같은 서버인지 확인합니다. 그래서 호스트 키 목록은 곧 접속을 시작한 서버 목록이 됩니다. 도구마다 저장 세션, 최근 경로, 설정 파일도 남깁니다.

| 도구 | 주로 남는 곳 | 알려 주는 것 |
|---|---|---|
| PuTTY | `HKCU\Software\SimonTatham\PuTTY` | 저장한 세션, 서버 호스트 키 |
| WinSCP | `HKCU\SOFTWARE\Martin Prikryl\WinSCP 2` 또는 `WinSCP.ini` | 서버 호스트 키, 원격·로컬 경로 기록, 저장한 세션 |
| OpenSSH 클라이언트 | `%userprofile%\.ssh\` | 접속 대상 이름·계정·경유 서버, 서버 호스트 키, 개인 키 |
| OpenSSH 서버 | `%programdata%\ssh\`, OpenSSH 이벤트 채널 | 서버 설정, 허용한 공개 키, 서버 로그 |
| FileZilla | 이번에 확인하지 못했습니다 | — |

이 기록으로 아래 질문에 답합니다.

- 이 사용자 계정이 SSH·SFTP 로 어느 서버에 접속을 시도했나
- 어떤 계정으로, 어느 서버를 거쳐 접속하도록 설정했나
- 원격·로컬의 어느 폴더를 오갔나
- 이 PC 가 SSH 서버로 쓰였나, 누구의 공개 키로 들어올 수 있게 해 두었나

## 위치와 버전별 차이

### PuTTY

설정은 대부분 `HKEY_CURRENT_USER\Software\SimonTatham\PuTTY` 에 저장되고, 저장한 세션은 그 아래 `Sessions`, SSH 호스트 키는 `SshHostKeys` 에 있습니다. [1] 난수 시드 파일 `PUTTY.RND` 는 기본으로 Application Data 폴더에 있으며 위치는 `...\PuTTY\RandSeedFile` 값으로 바꿀 수 있습니다. [1] Windows 7 이후에는 최근 실행한 세션이 점프 목록에 남습니다. [1]

PuTTY 는 비밀번호를 저장하지 않는데, FAQ 는 보안 때문에 일부러 그렇게 만들었다고 설명합니다. [1] `Sessions` 아래 값 이름과 `SshHostKeys` 값 이름의 형식은 이번 자료로 확인하지 못했습니다.

### WinSCP

레지스트리에 저장하면 `HKEY_CURRENT_USER\SOFTWARE\Martin Prikryl\WinSCP 2` 에 들어갑니다. [2] 문서에는 `HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Martin Prikryl\WinSCP 2` 도 나오는데, 문서는 이 키를 설치 프로그램이 만든다고 적습니다. 설정을 찾을 때 WinSCP 는 HKCU 다음에 HKLM 까지 두 곳을 모두 봅니다. [2]

INI 파일에 저장할 수도 있으며 파일 이름은 실행 파일과 같은 이름(`WinSCP.ini`)이어야 합니다. [2] WinSCP 는 INI 파일을 먼저 실행 파일 폴더에서 찾고 다음으로 `C:\Users\<사용자>\AppData\Roaming\WinSCP.ini` 에서 찾습니다. [2] 새 INI 파일은 실행 파일 폴더에 쓰려고 하고, 쓸 수 없으면 사용자 프로필의 응용 프로그램 데이터 폴더에 씁니다. [2]

공개 도구 RegRipper 의 winscp 플러그인은 `WinSCP 2` 밑의 다음 키를 읽습니다. [5]

| 키 | 담긴 것 (키 이름과 플러그인 동작으로 읽은 뜻) |
|---|---|
| `Configuration\CDCache` | 캐시 값. 내용은 확인하지 않았습니다 |
| `Configuration\History\RemoteTarget` | 원격 경로 기록 |
| `Configuration\History\LocalTarget` | 로컬 경로 기록 |
| `Configuration\Interface\Commander\LocalPanel` 의 `LastPath` | 로컬 창에서 마지막으로 연 경로 |
| `Configuration\Interface\Commander\RemotePanel` 의 `LastPath` | 원격 창에서 마지막으로 연 경로 |
| `SshHostKeys` | 서버 호스트 키 |

`Sessions\<세션 이름>` 아래 값 이름은 이번 자료로 확인하지 못했습니다.

### FileZilla

FileZilla 공식 설정 파일 문서(wiki.filezilla-project.org/Config_Files)는 이번에 열리지 않았습니다. 그래서 설정 파일의 위치·형식과 비밀번호 저장 방식을 이 페이지에 싣지 않습니다. 검체에서는 이 공식 문서로 위치를 확인한 뒤 수집합니다. 실행 흔적은 아래 "교차 검증" 의 아티팩트로 확인합니다.

### OpenSSH (윈도 내장)

- OpenSSH 는 Windows Server 2019 와 Windows 10(빌드 1809)부터 윈도에 들어갔습니다. [4]
- 기본 설치 폴더는 `%systemdrive%\Windows\System32\openssh` 입니다. [4]
- 조사 PC 의 이 폴더에는 ssh.exe, scp.exe, sftp.exe, ssh-add.exe, ssh-agent.exe, ssh-keygen.exe, ssh-keyscan.exe 등이 있었습니다. 버전은 OpenSSH_9.5p2 for Windows 였습니다.
- 클라이언트와 서버는 따로 설치하는 선택적 기능입니다. 조사 PC 에는 OpenSSH.Client 만 있고 OpenSSH.Server 는 없었습니다.

클라이언트 쪽 파일은 아래와 같습니다.

| 파일 | 위치 | 메모 |
|---|---|---|
| 클라이언트 설정 | `ssh.exe -F` 로 준 파일 → `%userprofile%\.ssh\config` → `%programdata%\ssh\ssh_config` | 이 순서로 읽습니다 [4] |
| 호스트 키 목록 | `%userprofile%\.ssh\known_hosts` | 조사 PC 에는 `known_hosts.old` 도 있었습니다 |
| 개인 키 | `%userprofile%\.ssh\` | 조사 PC 에는 `.pem` 개인 키 파일이 설정 파일과 함께 있었습니다 |

서버 쪽 파일과 설정은 아래와 같습니다. 모두 [4] 의 내용입니다.

| 항목 | 위치·값 | 메모 |
|---|---|---|
| 서버 설정 | `%programdata%\ssh\sshd_config` | 파일이 없으면 서비스가 시작할 때 기본값으로 만듭니다. `-f` 로 다른 파일을 줄 수 있습니다 |
| 서버 호스트 키 | `%programdata%\ssh\ssh_host_rsa_key`, `ssh_host_dsa_key`, `ssh_host_ecdsa_key`, `ssh_host_ed25519_key` | 없으면 서비스가 시작할 때 만듭니다 |
| 허용한 공개 키 (일반 사용자) | 사용자 홈의 `.ssh/authorized_keys` (예: `C:\Users\username`) | `AuthorizedKeysFile` 기본값입니다 |
| 허용한 공개 키 (관리자 그룹 사용자) | `%programdata%/ssh/administrators_authorized_keys` | 이 파일에는 NT Authority\SYSTEM 과 BUILTIN\Administrators 권한만 있어야 합니다 |
| 기본 셸 | `HKEY_LOCAL_MACHINE\SOFTWARE\OpenSSH` 의 문자열 값 `DefaultShell` | 처음 기본값은 cmd.exe 입니다 |
| 파일 로그 | `%programdata%\ssh\logs` | `sshd_config` 의 `SyslogFacility` 가 `LOCAL0` 일 때만 씁니다. 기본값(`AUTH`)을 비롯한 다른 값이면 ETW 로 보냅니다 |

문서의 AuthenticationMethods 항목은 윈도 OpenSSH 서버의 인증 방식이 password 와 publickey 뿐이라고 적습니다. 같은 문서의 GSSAPIAuthentication 항목에는 Windows Server 2022, Windows 11, Windows 10(2021년 5월 업데이트)부터 GSSAPI(Kerberos) 인증을 켤 수 있다고 적혀 있습니다(기본값 no). `sshd_config` 에서 이 값도 함께 봅니다. `PermitRootLogin` 은 윈도에 해당하지 않습니다. [4]

## 구조

### OpenSSH 클라이언트 설정 (.ssh\config)

조사 PC 의 `config` 에는 `Host`, `HostName`, `User`, `Port`, `IdentityFile`, `ProxyJump` 키워드가 쓰였습니다. 접속 대상 이름, 계정, 경유 서버가 평문으로 남습니다.

아래는 문법을 보여 주려고 만든 예시입니다. 주소는 문서용 예약 주소입니다.

```
Host jump
    HostName 203.0.113.10
    User admin

Host db
    HostName 192.0.2.20
    User deploy
    Port 2222
    IdentityFile ~/.ssh/db.pem
    ProxyJump jump
```

이 예시라면 `ssh db` 한 번으로 `jump` 서버를 거쳐 `192.0.2.20` 의 2222번 포트에 `deploy` 계정으로 접속합니다.

### 호스트 키 목록 (known_hosts)

조사 PC 의 `known_hosts` 한 줄은 "호스트 키종류 공개키" 세 칸이었습니다. 호스트 칸은 해시가 아니라 평문 IP 였습니다. 아래는 칸 모양만 보여 주려고 만든 예시입니다.

```
192.0.2.20 ssh-ed25519 AAAA…(공개 키, 생략)
```

호스트 칸이 해시로 저장되는 설정이 있다는 설명이 있지만 이번에 확인하지 못했습니다. `known_hosts.old` 가 언제 생기는지도 확인하지 못했습니다.

### OpenSSH 이벤트 채널

채널은 `OpenSSH/Admin`, `OpenSSH/Operational`, `OpenSSH/Debug` 입니다. 파일은 `%SystemRoot%\System32\Winevt\Logs\OpenSSH%4Operational.evtx` 처럼 이름이 붙습니다.

| ID | 수준 | 채널 |
|---|---|---|
| 1 | Critical | Admin |
| 2 | Error | Admin |
| 3 | Warning | Operational |
| 4 | Information | Operational |
| 6 | Debug | Debug |



메시지 형식은 모두 `%1: %2` 입니다. `%1` 은 프로그램 이름, `%2` 는 로그 한 줄입니다. 서버가 남기는 로그 줄의 실제 문장은 이번에 확인하지 못했습니다.

### WinSCP 경로 기록의 인코딩

RegRipper winscp 플러그인은 `RemoteTarget`·`LocalTarget` 값을 URL 디코딩해서 보여 줍니다. 그러니 이 값들은 `%XX` 꼴로 URL 인코딩돼 있습니다. [5] 풀어 읽는 법은 아래 "헥스로 한 번" 에서 따라갑니다.

## 증거로서 의미

**증명하는 것**

- PuTTY·WinSCP 의 `SshHostKeys` 나 `known_hosts` 에 서버가 있으면, 그 사용자 계정의 클라이언트가 그 서버와 SSH 접속을 시작한 적이 있습니다.
- `.ssh\config` 는 접속 대상 이름, 계정, 포트, 개인 키 파일, 경유 서버를 설정한 기록입니다.
- WinSCP 의 `RemoteTarget`·`LocalTarget`·`LastPath` 는 원격·로컬에서 다룬 경로를 보여 줍니다.
- PowerShell 명령 기록의 `ssh`·`scp` 줄은 접속 대상과 옵션을 명령줄 그대로 보여 줍니다. 조사 PC 에서는 이런 줄이 91개 있었습니다.
- `administrators_authorized_keys` 나 사용자 `authorized_keys` 의 공개 키는 그 키로 이 PC 에 로그인할 수 있게 해 두었다는 기록입니다.
- `DefaultShell` 값은 SSH 로 들어온 사람이 받는 셸을 보여 줍니다.

**증명하지 못하는 것**

- 호스트 키는 인증 전에 주고받습니다. 호스트 키가 저장돼 있다고 로그인에 성공했다는 뜻은 아닙니다.
- 이 흔적들에는 주고받은 파일 이름이나 내용이 없습니다.
- PuTTY 는 비밀번호를 저장하지 않습니다. 비밀번호가 없다고 이상한 것이 아닙니다.
- WinSCP 는 비밀번호를 기본으로 저장하지 않습니다. 사용자가 세션 저장 대화상자에서 따로 요청해야 저장합니다. [3]
- 조사 PC 에서는 ssh 클라이언트를 썼는데도 `OpenSSH/Operational`·`OpenSSH/Admin` 에 기록이 0건이었습니다. `known_hosts` 는 바뀌었고 프리페치도 있었습니다. 클라이언트 사용은 이 채널에 남지 않았습니다.

보고서에는 기록이 말하는 만큼만 씁니다. 예를 들면 "사용자 A 의 `known_hosts` 에 192.0.2.20 의 호스트 키가 있다. 이 사용자 계정의 SSH 클라이언트가 이 서버와 접속을 시작한 적이 있다. 이 기록만으로는 로그인 성공 여부와 접속 시각을 알 수 없다." 처럼 씁니다. 예의 값은 만든 예시입니다.

## 시각 해석

- 레지스트리 값에는 시각이 없습니다. 시각은 키의 LastWrite 하나뿐입니다. RegRipper putty 플러그인은 `SshHostKeys` 키의 LastWrite 를 함께 보여 줍니다. [5] 이 시각은 그 키 안의 무언가가 마지막으로 바뀐 때입니다. 서버마다의 접속 시각이 아닙니다. LastWrite 를 읽는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.
- `config`·`known_hosts`·개인 키 파일은 파일 시스템 시각으로 봅니다. [마스터 파일 테이블](../filesystem/mft.md)에서 읽습니다.
- 서버 호스트 키와 `sshd_config` 는 없으면 서비스가 시작할 때 만듭니다. [4] 그러니 이 파일들을 만든 시각은 sshd 서비스를 처음 시작한 때를 가늠하는 단서가 됩니다. 이 판단은 문서 내용에서 나온 추론입니다.
- 이벤트 시각은 레코드 시각입니다. 읽는 법은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.

## 함정과 한계

- **휴대용 WinSCP 는 레지스트리에 흔적이 없을 수 있습니다.** WinSCP 는 INI 파일을 실행 파일 폴더에서 먼저 찾고, 새로 쓸 때도 실행 파일 폴더를 먼저 씁니다. [2] 그래서 USB 에서 실행하면 흔적이 USB 의 `WinSCP.ini` 에만 남을 수 있습니다. 이 판단은 문서 내용에서 나온 추론입니다. USB 흔적은 [USB 저장장치 흔적](../external-devices/usb-storage-artifacts/index.md)에서 다룹니다.
- **`putty -cleanup` 은 흔적을 지웁니다.** 현재 사용자의 레지스트리 항목, 난수 시드 파일, 점프 목록 정보를 지웁니다. FAQ 는 공용 PC 에서 쓰라고 안내합니다. [1] PuTTY 실행 흔적은 있는데 레지스트리 키가 없으면 이 명령을 의심합니다.
- **WinSCP 에 저장한 비밀번호는 쉽게 풀릴 수 있습니다.** 마스터 비밀번호로 보호하지 않은 저장 비밀번호는 "쉽게 복구할 수 있는 방식" 으로 저장됩니다. 문서는 자동으로 쓸 수 있으면서 안전하게 암호화하는 방법은 없다고 적습니다. [3] 비밀번호를 풀어 쓸 때는 조사 권한 범위를 먼저 확인합니다.
- **관리자 그룹 사용자의 공개 키는 사용자 홈에 없습니다.** 관리자 그룹 사용자는 `administrators_authorized_keys` 를 씁니다. [4] 사용자 홈의 `.ssh` 만 보면 이 키를 놓칩니다.
- **`sshd_config` 가 있다고 누가 설정을 고쳤다는 뜻은 아닙니다.** 파일이 없으면 서비스가 기본값으로 만듭니다. [4] 기본값과 다른 줄이 있는지 따로 봅니다.
- **서버 로그는 기본값에서 파일이 아니라 ETW 로 갑니다.** `%programdata%\ssh\logs` 가 비어 있다고 서버를 쓰지 않았다고 단정하지 않습니다. [4]
- **OpenSSH 클라이언트 사용은 이벤트 채널에 남지 않았습니다.** 클라이언트 흔적은 `.ssh` 폴더, 프리페치, PowerShell 명령 기록으로 찾습니다.
- **ssh-agent 가 등록한 키를 어디에 두는지는 확인하지 못했습니다.** 조사 PC 에서 ssh-agent 서비스는 중지·사용 안 함 상태였습니다.
- **FileZilla 는 이 페이지에서 다루지 못했습니다.** 공식 문서로 위치를 확인한 뒤 분석합니다.

## 직접 분석해 보기

### 헥스로 한 번

이 페이지의 흔적은 레지스트리 문자열 값과 텍스트 파일입니다. 레지스트리 값의 저장 구조는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다. 여기서는 WinSCP 경로 기록의 `%XX` 를 손으로 풀어 봅니다.

URL 인코딩에서 `%XX` 의 `XX` 는 바이트 값을 16진수 두 자리로 적은 것입니다. 아래는 규칙을 보여 주려고 만든 예시입니다.

| 인코딩된 값 | `%XX` | 바이트 | 문자 | 풀어 쓴 값 |
|---|---|---|---|---|
| `/var/www/my%20site` | `%20` | `0x20` | 공백 | `/var/www/my site` |
| `C%3A%5CUsers` | `%3A`, `%5C` | `0x3A`, `0x5C` | `:`, `\` | `C:\Users` |

영문이 아닌 문자가 어느 문자 인코딩으로 들어가는지는 확인하지 못했습니다. 한글 경로를 풀 때는 UTF-8 과 CP949 로 모두 풀어 보고 맞는 쪽을 고릅니다. 두 인코딩은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)에서 다룹니다.

### 공개 도구로 한 번

RegRipper 로 사용자 하이브의 PuTTY·WinSCP 흔적을 뽑습니다.

```
rip.exe -r E:\case\NTUSER.DAT -p putty
rip.exe -r E:\case\NTUSER.DAT -p winscp
```

- putty 플러그인은 `SshHostKeys` 값을 "이름 -> 데이터" 로 모두 보여 주고, 키의 LastWrite 를 함께 보여 줍니다. [5]
- winscp 플러그인은 위 표의 키를 읽고 경로 기록을 URL 디코딩해 보여 줍니다. [5]
- 저장 세션(`Sessions`)은 레지스트리 뷰어로 따로 열어 값을 확인합니다.

OpenSSH 클라이언트 흔적은 PowerShell 로 모읍니다.

```powershell
$root = 'E:\mount'   # 마운트한 경로로 바꿉니다
# 사용자마다 .ssh 설정의 대상 이름·계정·경유 서버
Get-ChildItem "$root\Users\*\.ssh\config" -ErrorAction SilentlyContinue |
  Select-String -Pattern '^\s*(Host|HostName|User|Port|IdentityFile|ProxyJump)\s'
# known_hosts 의 첫 칸(호스트)
Get-ChildItem "$root\Users\*\.ssh\known_hosts*" -ErrorAction SilentlyContinue |
  ForEach-Object { $f = $_.FullName; Get-Content $f | ForEach-Object { "{0}`t{1}" -f $f, ($_ -split '\s+')[0] } }
```

PowerShell 명령 기록 파일에서는 `^(ssh|scp|sftp)\s` 로 줄을 거릅니다. 파일 위치는 [PowerShell 명령 기록](../execution/consolehost-history-txt.md)에서 다룹니다.

서버 이벤트는 수집한 evtx 파일로 봅니다.

```powershell
Get-WinEvent -Path 'E:\case\OpenSSH%4Operational.evtx' |
  Select-Object @{ n = 'UTC'; e = { $_.TimeCreated.ToUniversalTime() } }, Id, LevelDisplayName, Message
```

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 프리페치 | 조사 PC 에는 `SSH.EXE-17F86097.pf` 가 있었습니다. PuTTY·WinSCP·FileZilla 실행 파일도 같은 방식으로 찾습니다 | [프리페치](../execution/prefetch/index.md) |
| PowerShell 명령 기록 | `ssh`·`scp` 명령줄의 접속 대상과 옵션 | [PowerShell 명령 기록](../execution/consolehost-history-txt.md) |
| 점프리스트 | Windows 7 이후 PuTTY 의 최근 세션 [1] | [점프리스트](../file-folder-usage/jump-lists.md) |
| AmCache · 심캐시 | 설치하지 않고 실행한 도구의 경로 | [AmCache](../execution/amcache-hve/index.md), [심캐시](../execution/shimcache-appcompatcache.md) |
| 설치 프로그램 | 설치한 도구 목록 | [설치 프로그램](../system-account/uninstall.md) |
| 서비스·드라이버 | sshd·ssh-agent 서비스의 시작 유형 | [서비스·드라이버](../persistence/services-drivers.md) |
| USB 저장장치 흔적 | 휴대용 WinSCP 를 실행한 장치 | [USB 저장장치 흔적](../external-devices/usb-storage-artifacts/index.md) |
| 자료 유출 시나리오 | SFTP·SCP 로 파일을 내보냈는지 따지는 순서 | [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md) |

## 실습

공개 검체(NIST CFReDS 등) 가운데 SSH·SFTP 도구를 쓴 이미지를 골라 아래 질문을 풀어 봅니다.

1. 사용자마다 NTUSER.DAT 에 `SimonTatham\PuTTY` 와 `Martin Prikryl\WinSCP 2` 키가 있습니까?
2. PuTTY `SshHostKeys` 에 몇 개의 서버가 있습니까? 키의 LastWrite 는 언제입니까?
3. WinSCP `RemoteTarget`·`LocalTarget` 을 풀면 어떤 경로가 나옵니까?
4. 사용자 홈의 `.ssh\config` 에 `ProxyJump` 가 있습니까? 경유 서버는 어디입니까?
5. `known_hosts` 의 호스트와 PuTTY·WinSCP 의 호스트 키 목록에 겹치는 서버가 있습니까?
6. `%programdata%\ssh` 가 있습니까? `administrators_authorized_keys` 에 공개 키가 몇 개 있습니까?
7. 프리페치에 PuTTY·WinSCP·SSH 실행 흔적이 있는데 레지스트리 키가 없는 사용자가 있습니까?

## 참고 문헌

1. PuTTY User Manual, Appendix A: PuTTY FAQ (A.2.2, A.8.2 등). https://the.earth.li/~sgtatham/putty/latest/htmldoc/AppendixA.html
2. WinSCP documentation — Configuration (configuration storage). https://winscp.net/eng/docs/config
3. WinSCP documentation — Security of stored credentials. https://winscp.net/eng/docs/security_credentials
4. OpenSSH Server Configuration for Windows — Microsoft Learn (2025-08-05). https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh-server-configuration
5. keydet89/RegRipper3.0, plugins/putty.pl, plugins/winscp.pl (master, 커밋 ec96dd4a). https://codeload.github.com/keydet89/RegRipper3.0/tar.gz/refs/heads/master
