---
title: "기타 원격 제어 도구"
parent: "원격 제어 프로그램"
grand_parent: "아티팩트 · 네트워크"
nav_order: 2410
---

# 기타 원격 제어 도구 (RustDesk·Splashtop·Chrome Remote Desktop)

> 상위 허브: [원격 제어 프로그램 (Remote Access Tools)](index.md)

## 한 줄 요약

이 페이지는 원격 제어 도구 세 가지의 흔적을 정리합니다. RustDesk 는 사용자 폴더와 서비스 폴더의 로그 파일을 봅니다. Splashtop 은 전용 이벤트 로그 두 개와 텍스트 로그 두 개를 봅니다. Chrome Remote Desktop 은 "chromoting" 이름으로 남는 이벤트 ID 1~6 을 봅니다.

## 무엇을 기록하나 · 왜 생기나

| 도구 | 성격 | 먼저 볼 흔적 |
|---|---|---|
| RustDesk | 공개 소스 원격 제어 도구. 중계 서버를 직접 둘 수 있습니다 | `%AppData%\RustDesk\log\` 와 서비스 폴더 아래 로그 |
| Splashtop | 원격 지원 프로그램 | 전용 이벤트 로그 두 개, `SPLog.txt`, `FTCLog.txt`, 레지스트리 ClientInfo |
| Chrome Remote Desktop | Google 의 원격 접속 서비스. 상시 접속과 일회성 지원 두 방식이 있습니다 | 서비스 이름 chromoting, 이벤트 ID 1~6 |

서비스 설치 이벤트와 여러 도구에 공통으로 남는 실행 흔적은 [허브](index.md)에서 정리합니다.

## RustDesk

### 위치

| 흔적 | 경로 | 메모 |
|---|---|---|
| 설치 폴더 | `C:\Program Files\RustDesk` | 설치 경로 예 |
| 사용자 설치 | `C:\Users\*\AppData\Local\rustdesk\rustdesk.exe` | |
| 서비스 쪽 폴더 | `C:\Windows\ServiceProfiles\LocalService\AppData\Roaming\RustDesk\*` | |
| 로그 (휴대용, 설치형의 거는 쪽) | `%AppData%\RustDesk\log\RustDesk_rCURRENT.log` | RustDesk FAQ |
| 로그 (설치형의 받는 쪽) | `C:\Windows\ServiceProfiles\LocalService\AppData\Roaming\RustDesk\log\server\` 또는 `C:\Windows\SysWOW64\config\systemprofile\AppData\Roaming\RustDesk\log\server` | RustDesk FAQ |
| 자체 서버 로그 (Linux) | `/var/log/rustdesk-server/` 의 `hbbr.log`, `hbbs.log` | 중계 서버를 직접 둔 경우 |

포트는 자료마다 조금 다르게 적혀 있습니다.

- LOLRMM 은 443, 21115, 21116 을 적습니다.
- RustDesk FAQ 는 ID(랑데부) 서버에 TCP 21116(UDP 21116 도 씀), 중계 서버에 TCP 21117, 웹 콘솔에 21114 를 적습니다.

LOLRMM 의 도메인 칸에는 "user_managed" 가 적혀 있는데, 쓰는 사람이 중계 서버를 정할 수 있어서 접속 도메인 목록으로 거르기 어렵습니다.

### 증거로서 의미

**증명하는 것**

- 로그 파일이 있으면 RustDesk 가 이 PC 에서 돌았습니다.
- 로그가 `log\server\` 아래에 있으면 설치형의 받는 쪽으로 동작한 흔적입니다. `%AppData%\RustDesk\log\` 아래에 있으면 휴대용 실행이나 설치형의 거는 쪽 흔적입니다.

**증명하지 못하는 것**

- 로그 안에 상대 ID·IP 가 어떤 모양으로 남는지는 이번 자료로 확인하지 못했습니다. 로그를 열어 직접 확인하고, 확인한 버전을 보고서에 적습니다.
- 설정 파일의 위치와 이름도 이번 자료로 확인하지 못했습니다.
- 중계 서버를 직접 둔 경우, 서버 로그는 그 서버에 있습니다. 조사하는 PC 만으로는 서버 쪽 기록을 볼 수 없습니다.

## Splashtop

### 위치

아래 경로는 Synacktiv 가 Splashtop 3.52.1.42 로 시험한 결과에 LOLRMM 목록을 더한 것입니다. 이 시험에서 Splashtop 은 Atera 에 딸려 설치됐습니다.

| 흔적 | 경로 | 메모 |
|---|---|---|
| 설치 폴더 | `C:\Program Files (x86)\Splashtop` | |
| 실행 파일 | `...\Splashtop Remote\Server\SRService.exe`(원격 서비스), `SRAgent.exe`(에이전트), `SRUtility.exe`, `SRFeature.exe`, `...\Splashtop Software Updater\SSUAgent.exe` | |
| 주 로그 | `C:\Program Files (x86)\Splashtop\Splashtop Remote\Server\log\SPLog.txt` | 접속한 호스트 이름, 표시 이름, 상대 공인 IP, 파일 전송, 채팅 |
| 파일 전송 로그 | `%PROGRAMDATA%\Splashtop\Temp\log\FTCLog.txt` | |
| 디버그·내부 로그 | 주 로그와 같은 폴더의 `agent_log.txt`, `svcinfo.txt` | Synacktiv 는 포렌식 가치가 낮다고 적었습니다 |
| 저장한 채팅 | `Splashtop_Chat_[YYYYMMDD]_[HHMM].txt` | 사용자가 채팅을 저장한 경우. 저장 위치는 이번 자료로 확인하지 못했습니다 |
| 암호화된 파일 | `...\Server\db\SRAgent.sqlite3`, `%PROGRAMDATA%\Splashtop\Splashtop Remote Server\Credential\<무작위 이름>` | 암호화돼 있어 바로 읽지 못합니다 |
| 전용 이벤트 로그 | `C:\Windows\System32\winevt\Logs\Splashtop-Splashtop Streamer-Remote Session%4Operational.evtx`, `Splashtop-Splashtop Streamer-Status%4Operational.evtx` | |

| 레지스트리 | 내용 |
|---|---|
| `HKLM\SYSTEM\ControlSet001\Services\SplashtopRemoteService` | 서비스 키 |
| `HKLM\SYSTEM\CurrentControlSet\Control\SafeBoot\Network\SplashtopRemoteService` | 안전 모드(네트워크)에서도 서비스가 뜨게 하는 키 |
| `HKLM\SOFTWARE\WOW6432Node\Splashtop Inc.\Splashtop Remote Server\ClientInfo` | 마지막으로 접속한 상대. DeviceName(상대 호스트 이름), Client_DisplayName(표시 이름), UDID, AppVersion |
| `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Print\Printers\Splashtop PDF Remote Printer` | 원격 인쇄용 프린터 |

7045 에는 "Splashtop® Remote Service"(SRService.exe)와 "Splashtop Software Updater Service"(SSUService.exe) 두 서비스가 남습니다. LOLRMM 은 "SplashtopRemoteService" 라는 이름도 적습니다.

### 전용 이벤트 로그

| 로그 | 남는 것 | 예시 (Synacktiv) |
|---|---|---|
| Splashtop-Splashtop Streamer-Remote Session/Operational | 원격 세션 생성, 파일 전송, 상대 호스트 이름, 파일 이름 | `A file was transferred during the Splashtop remote session (1018449597). App version: 3.5.2.1 File name: mechant.7z From: mechant_host (N/A) To: LABWINDOWS (C:\Users\lab\Desktop)` |
| Splashtop-Splashtop Streamer-Status/Operational | 서비스 상태 | `Splashtop streamer went online. App version: 3.5.2.1 Server Info: st-v3-univ-srs-win-3521-g3.api.splashtop.com RMM ID: hZCDFPhK75mJ` |

두 로그의 이벤트 ID 번호는 이번 자료로 확인하지 못했습니다. 메시지 문구로 찾습니다.

### 텍스트 로그

**FTCLog.txt** 는 파일 전송 로그입니다. 칸은 날짜·시각, 파일 경로, 크기(KB), 전송 종류, 상태, 사용자 이름, (IP) 순서입니다.

```
2022-09-01 11:42:14 C:\Users\lab\Desktop\mechant.7z 0.0 KB Upload Completed john doe (123.231.123.231)
```

**SPLog.txt** 는 주 로그입니다. 줄 앞에 연도 없는 날짜와 시각이 옵니다.

```
<1>Sep  1 11:40:53 [SM_04020]:[Auth-L] ok, client (mechant_host) can connect to AV server
<1>Sep  1 11:40:58 [AP_07144]:[Banner] Got client 1 public IP 123.231.123.231
<1>Sep  1 11:42:12 [SM_04020]:[FTC] UploadRequest, fileID[289614100], filePath[C:\Users\lab\Desktop\mechant.7z]
```

`[Auth-L]` 줄에는 접속한 상대 호스트 이름이, `[Banner]` 줄에는 상대 공인 IP 가, `[FTC]` 줄에는 파일 전송 요청과 파일 경로가 나옵니다. 위 예시는 모두 Synacktiv 공개 예시입니다.

### 증거로서 의미

**증명하는 것**

- Remote Session 로그와 `FTCLog.txt` 는 파일 이름, 방향(Upload 등), 상대 호스트 이름을 보여 줍니다.
- `SPLog.txt` 의 `[Banner]` 줄은 상대 공인 IP 를 보여 줍니다.
- ClientInfo 키는 마지막으로 접속한 상대의 호스트 이름과 표시 이름을 보여 줍니다.
- SafeBoot\Network 키가 있으면 안전 모드(네트워크)에서도 원격 서비스가 뜨도록 설정돼 있었습니다.

**증명하지 못하는 것**

- ClientInfo 는 마지막 상대만 보여 줍니다. 그 전 접속은 로그에서 찾습니다.
- `SRAgent.sqlite3` 와 Credential 폴더의 파일은 암호화돼 있어 내용을 바로 읽지 못합니다.
- 상대 호스트 이름과 IP 는 사람을 가리키지 않습니다.

## Chrome Remote Desktop

### 위치와 서비스

| 흔적 | 내용 |
|---|---|
| 호스트 실행 파일 | `C:\Program Files (x86)\Google\Chrome Remote Desktop\<버전>\remoting_host.exe` |
| 서비스 이름 | "chromoting" 이 들어갑니다 |
| 이벤트 로그 이름 | 호스트는 시스템 이벤트 로그에 "chromoting" 이라는 이름으로 기록합니다(Chromium 소스의 kApplicationName) |
| 접속 도메인·포트 | `remotedesktop.google.com`, `*.remotedesktop.google.com`, `remotedesktop-pa.googleapis.com`, `chromoting-host.talkgadget.google.com` 등. 포트 443, 3478 |

Windows 에서는 호스트가 여러 프로세스로 돌아서, 호스트가 IPC 로 넘기면 다른 프로세스가 이벤트를 기록합니다. 그래서 실제 원본 이름과 로그 이름(Application 인지)은 이번 자료로 확인하지 못했습니다. 로그 전체에서 원본 이름에 "chromoting" 이 든 이벤트를 찾습니다.

호스트 설정 파일의 위치는 이번 자료로 확인하지 못했습니다.

### 이벤트 ID

아래 표는 Chromium 소스의 메시지 파일 정의와 영어 문구입니다.

| ID | 이름 | 수준 | 문구 |
|---|---|---|---|
| 1 | MSG_HOST_CLIENT_CONNECTED | 정보 | `Client connected: <상대 사용자>.` |
| 2 | MSG_HOST_CLIENT_DISCONNECTED | 정보 | `Client disconnected: <상대 사용자>.` |
| 3 | MSG_HOST_CLIENT_ACCESS_DENIED | 오류 | `Access denied for client: <상대 사용자>.` |
| 4 | MSG_HOST_CLIENT_ROUTING_CHANGED | 정보 | `Channel IP for client: <상대 식별자> ip='<상대 IP:포트>' host_ip='<호스트 IP:포트>' channel='<채널 종류>' connection='<연결 종류>'.` |
| 5 | MSG_HOST_STARTED | 정보 | `Host started for user: <호스트 계정>.` |
| 6 | MSG_HOST_LOG_EVENT | 정보 | 원래 로그 문구를 그대로 적습니다 |

- 소스의 예시 값에서 상대 사용자는 `client@email.com` 꼴입니다. 이벤트 4 의 예시는 `client@email.com/TalkGadgetABCDABCD`, `127.0.0.1:1000`, `mux`, `direct` 입니다.
- 이벤트 4 는 채널이 새로 열릴 때마다 남습니다. 연결 하나 위에 채널 여러 개가 겹칠 수 있습니다.
- 메시지 파일은 언어별로 만들어집니다. 그래서 문구는 OS 언어에 따라 다를 수 있습니다.
- 문구 목록에는 IDS_HOST_STOPPED("Host stopped.")도 있습니다. 그러나 메시지 파일에는 이 ID 가 없습니다. 호스트가 멈춘 이벤트를 이 ID 목록에서 찾지 않습니다.
- 이 정의는 Chromium 소스의 현재 판(HEAD) 기준입니다. 옛 버전의 호스트와 다를 수 있습니다.

### 증거로서 의미

**증명하는 것**

- 이벤트 1·2 는 상대 사용자의 접속과 끊김 시각을 보여 줍니다.
- 이벤트 3 은 접속이 거부된 시도를 보여 줍니다.
- 이벤트 4 는 상대 IP·포트, 호스트 IP·포트, 연결 종류를 보여 줍니다.
- 이벤트 5 는 어느 호스트 계정으로 호스트가 시작됐는지 보여 줍니다.

**증명하지 못하는 것**

- 상대 사용자 칸에는 계정 식별자가 남습니다(소스 예시는 이메일 주소 꼴). 그 계정을 쓴 사람은 이 칸으로 특정하지 못합니다.
- 이벤트 4 는 채널마다 남습니다. 이벤트 4 의 개수는 접속 횟수가 아닙니다.
- 세션 중에 한 일은 이 이벤트들에 없습니다.

## 시각 해석

- Splashtop 전용 이벤트 로그와 Chrome Remote Desktop 이벤트의 시각은 이벤트 레코드 시각입니다. 레코드 시각을 읽는 법은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.
- `SPLog.txt` 의 시각에는 연도가 없습니다(예: `Sep  1 11:40:53`). 연도는 파일 시각이나 같은 때의 다른 기록에서 채웁니다.
- `SPLog.txt`, `FTCLog.txt`, RustDesk 로그의 시각이 UTC 인지는 이번 자료로 확인하지 못했습니다. 같은 파일 전송을 Remote Session 로그와 `FTCLog.txt` 에서 찾아 두 시각의 차이를 잽니다. PC 의 시간대 설정은 [시간대 설정](../../system-account/time-zone.md)에서 봅니다.
- Splashtop 공개 예시의 시각은 `[FTC] UploadRequest` 줄이 11:42:12, `FTCLog.txt` 줄이 11:42:14 입니다. 두 파일이 같은 시간대로 적힌 것으로 보입니다. 이 판단은 예시 두 줄을 비교해 추론한 것입니다.

## 함정과 한계

- **RustDesk 는 도메인으로 거르기 어렵습니다.** 중계 서버를 직접 둘 수 있습니다.
- **Splashtop 은 다른 제품에 딸려 설치될 수 있습니다.** Synacktiv 시험에서는 Atera 에 딸려 설치됐습니다. 사용자가 Splashtop 을 따로 설치하지 않았어도 흔적이 있을 수 있습니다.
- **Splashtop 이벤트 ID 를 모릅니다.** 로그 이름과 메시지 문구로 찾습니다.
- **SPLog.txt 에 연도가 없습니다.** 해를 넘긴 로그는 순서가 헷갈립니다.
- **Chrome Remote Desktop 이벤트의 원본 이름과 로그 이름이 확인되지 않았습니다.** 특정 로그 하나만 보지 말고 로그 전체에서 "chromoting" 을 찾습니다.
- **Chrome Remote Desktop 문구는 OS 언어에 따라 다를 수 있습니다.** 문구보다 이벤트 ID 와 원본 이름을 함께 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

이 페이지의 흔적은 이벤트 로그, 레지스트리, 텍스트 로그입니다. 도구마다의 이진 구조는 이번 자료로 확인한 것이 없어 헥스 예시를 싣지 않습니다. 이벤트 레코드를 헥스로 따라가는 법은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.

### 공개 도구로 한 번

Splashtop 전용 이벤트 로그는 파일을 바로 엽니다.

```powershell
$logs = 'E:\case\winevt\Logs'   # 수집한 폴더로 바꿉니다
Get-WinEvent -Path "$logs\Splashtop-Splashtop Streamer-Remote Session%4Operational.evtx" |
  Select-Object @{ n = 'UTC'; e = { $_.TimeCreated.ToUniversalTime() } }, Id, Message
```

Chrome Remote Desktop 이벤트는 로그 이름을 확정하지 못했으므로, 수집한 evtx 파일 전체에서 원본 이름으로 찾습니다.

```powershell
Get-ChildItem 'E:\case\winevt\Logs\*.evtx' | ForEach-Object {
  Get-WinEvent -Path $_.FullName -ErrorAction SilentlyContinue |
    Where-Object { $_.ProviderName -like '*chromoting*' }
} | Select-Object @{ n = 'UTC'; e = { $_.TimeCreated.ToUniversalTime() } }, LogName, ProviderName, Id, Message
```

`TimeCreated` 는 분석 PC 의 시간대로 바뀌어 나오므로 UTC 로 바꿔 출력합니다. 텍스트 로그는 `Select-String` 으로 `[Banner]`, `[FTC]`, `Upload`, `Download` 같은 문자열을 찾습니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 서비스 설치 (7045·4697) | 세 도구의 서비스 설치 시각. Sigma 규칙이 SplashtopRemoteService, SSUService, chromoting 이름을 찾습니다 | [서비스 설치](../../event-logs/7045-4697.md), [이벤트 로그 규칙 검색](../../../03-techniques/analysis/sigma-rules.md) |
| 서비스·드라이버 | Splashtop 서비스 키와 SafeBoot 키 | [서비스·드라이버](../../persistence/services-drivers.md) |
| 실행 흔적 | 프리페치, BAM, AmCache 등에 남은 실행 시각 | [프리페치](../../execution/prefetch/index.md), [AmCache](../../execution/amcache-hve/index.md), [BAM·DAM](../../execution/background-activity-moderator.md) |
| 마스터 파일 테이블 | 전송된 파일이 받는 쪽 폴더에 생긴 시각 | [마스터 파일 테이블](../../filesystem/mft.md) |
| DNS·프록시 기록 | Splashtop 은 `*.splashtop.com`(`api.splashtop.com`, `relay.splashtop.com` 포함). Chrome Remote Desktop 도메인은 위 표 | — |

## 실습

공개 검체(NIST CFReDS 등) 가운데 이 도구들의 흔적이 있는 이미지를 골라 아래 질문을 풀어 봅니다.

1. RustDesk 로그가 `%AppData%\RustDesk\log\` 와 `log\server\` 가운데 어디에 있습니까? 이 PC 는 받는 쪽입니까, 거는 쪽입니까?
2. Splashtop Remote Session 로그에서 파일 전송 이벤트를 찾습니다. 같은 전송이 `FTCLog.txt` 에도 있습니까? 두 시각은 몇 초 차이 납니까?
3. `SPLog.txt` 의 `[Banner]` 줄에서 상대 공인 IP 를 찾습니다. 연도는 어떻게 정했습니까?
4. ClientInfo 키의 DeviceName 은 로그에 나온 상대 호스트 이름과 같습니까?
5. 원본 이름에 "chromoting" 이 든 이벤트가 어느 로그에 있습니까? 이벤트 1 과 2 로 세션 길이를 구합니다.

## 참고 문헌

1. Synacktiv, "Legitimate RATs: a comprehensive forensic analysis of the usual suspects" (Théo Letailleur, 2022-10-20). https://www.synacktiv.com/publications/legitimate-rats-a-comprehensive-forensic-analysis-of-the-usual-suspects.html
2. LOLRMM API, rmm_tools.json (RustDesk, Splashtop, Chrome Remote Desktop 항목). https://lolrmm.io/api/rmm_tools.json
3. RustDesk GitHub 위키, FAQ. https://github.com/rustdesk/rustdesk/wiki/FAQ
4. SigmaHQ 규칙 저장소 (커밋 16eb587, 2026-09-22). rules/windows/builtin/system/service_control_manager/win_system_service_install_remote_access_software.yml, rules/windows/builtin/security/win_security_service_install_remote_access_software.yml. https://github.com/SigmaHQ/sigma
5. Chromium 소스, remoting/host/win/host_messages.mc.jinja2 (HEAD). https://chromium.googlesource.com/chromium/src/+/HEAD/remoting/host/win/host_messages.mc.jinja2
6. Chromium 소스, remoting/resources/remoting_strings.grd (HEAD). https://chromium.googlesource.com/chromium/src/+/HEAD/remoting/resources/remoting_strings.grd
7. Chromium 소스, remoting/host/remoting_me2me_host.cc (HEAD). https://chromium.googlesource.com/chromium/src/+/HEAD/remoting/host/remoting_me2me_host.cc
