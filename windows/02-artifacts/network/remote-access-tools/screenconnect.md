---
title: "스크린커넥트"
parent: "원격 제어 프로그램"
grand_parent: "아티팩트 · 네트워크"
nav_order: 2400
---

# 스크린커넥트 (ScreenConnect)

> 상위 허브: [원격 제어 프로그램 (Remote Access Tools)](index.md)

## 한 줄 요약

스크린커넥트 (ScreenConnect) 는 ConnectWise 의 원격 지원 제품입니다. 조종당하는 PC 에 클라이언트 서비스가 설치되고, 서비스 명령줄에 중계 서버 주소와 세션 종류가 붙습니다. Application 이벤트 로그에는 세션 시작·끝, 파일 전송, 명령 실행이 남습니다.

## 무엇을 기록하나 · 왜 생기나

ScreenConnect 는 ScreenConnect 가 돌아가는 관리 서버와 조종당하는 PC 에 설치되는 클라이언트, 두 부분으로 나뉩니다.

LOLRMM 목록에는 "ScreenConnect" 와 "ConnectWise Control" 이 두 항목으로 따로 올라 있으므로 흔적을 찾을 때는 두 이름을 모두 씁니다.

클라이언트는 설치할 때 서비스를 등록하고, 원격에서 명령을 실행하면 스크립트를 디스크에 쓴 뒤 그 스크립트에 맞는 해석기로 실행합니다. 그래서 명령 하나가 세 곳에 흔적을 남깁니다.

- Application 이벤트 로그: 명령을 실행했다는 기록과 명령 길이
- 임시 폴더: 스크립트 파일
- 프로세스 생성 기록: 스크립트를 실행한 cmd.exe

The DFIR Report 가 공개한 사건에서는 이 방식으로 systeminfo, ipconfig, net 명령이 실행됐습니다. 분석가는 4688 과 Sysmon 1 로 이 명령들을 추적했습니다.

## 위치와 버전별 차이

### 클라이언트 (조종당하는 PC)

| 흔적 | 경로·이름 | 메모 |
|---|---|---|
| 설치 폴더 | `C:\Program Files (x86)\ScreenConnect Client (<16진 문자열>)\` | 괄호 안은 설치 지문(thumbprint)입니다. 예: `ScreenConnect Client (0e2f8d025e383f56)` |
| 서비스 실행 파일 | `...\ScreenConnect.ClientService.exe` | |
| 다른 실행 파일 | ScreenConnect.WindowsClient.exe, ConnectWiseControl.Client.exe 등 | |
| 클라이언트 설정 | `C:\ProgramData\ScreenConnect Client*\user.config` | |
| 명령 실행 스크립트 | `C:\Windows\Temp\ScreenConnect\<버전>\<UUID>run.cmd` 또는 `run.ps1` | 예: `C:\Windows\Temp\ScreenConnect\22.8.9717.8313\` |
| 원격 실행용으로 보낸 파일 | `C:\Users\<사용자>\Documents\ConnectWiseControl\Temp\` | 실행 전에 여기에 떨어집니다. ScreenConnect.WindowsClient.exe 가 만듭니다 |

### 서버

| 흔적 | 경로 | 메모 |
|---|---|---|
| 세션 DB | `C:\Program Files*\ScreenConnect\App_Data\Session.db` | 형식(SQLite 인지)과 표 이름은 이번 자료로 확인하지 못했습니다 |
| 사용자 설정 | `C:\Program Files*\ScreenConnect\App_Data\User.xml` | |

### 버전에 따라 달라지는 점

- 임시 폴더 경로에 버전 번호가 들어갑니다. 자료의 예는 `22.8.9717.8313`(The DFIR Report)과 `23.6.8.8644`(Sigma 규칙 예시)입니다.
- Application 로그의 이벤트 ID 가 자료마다 다릅니다. 아래 "Application 이벤트 로그" 절을 봅니다.

## 구조

### 서비스 명령줄

클라이언트를 설치하면 System 로그에 7045 가 남습니다. 시작 유형은 자동이고, 서비스 종류는 자기 프로세스 서비스(SERVICE_WIN32_OWN_PROCESS)입니다. 서비스 명령줄 끝에는 아래처럼 접속 정보가 붙습니다(The DFIR Report 예시).

```
?e=Access&y=Guest&h=instance-…-relay.screenconnect.com&p=443&s=<GUID>&k=<인코딩된 키>&…
```

| 인자 | 뜻 |
|---|---|
| e | 세션 종류 (Support, Meeting, Access) |
| y | 프로세스 종류 (Guest, Host) |
| h | 중계 서버 주소 |
| p | 중계 포트 |
| s | 클라이언트 고유 ID |
| k | 신원 확인에 쓰는 인코딩된 암호화 키 |

Sigma 규칙은 명령줄에 `e=Access&`, `y=Guest&`, `&p=`, `&c=`, `&k=` 가 모두 들어 있으면 ScreenConnect 설치 실행으로 봅니다. `c` 의 뜻은 이번 자료에 없습니다.

The DFIR Report 사건에서는 Sysmon 자료가 망가져 있었습니다. 분석가는 SYSTEM 하이브와 SYSTEM.LOG1 을 Registry Explorer 로 열어 서비스 명령줄 전체를 되살렸습니다. 하이브와 트랜잭션 로그 구조는 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

### Application 이벤트 로그

원본(공급자) 이름은 자료마다 다르게 적혀 있습니다.

- Hunt & Hackett(2021-06)은 `ScreenConnect Client (<16진 문자열>)` 로 적었습니다.
- Sigma 규칙은 Provider_Name 을 `ScreenConnect` 로 적었습니다.

| 동작 | 메시지 문구 | Hunt & Hackett 의 이벤트 ID | Sigma 규칙의 이벤트 ID |
|---|---|---|---|
| 세션 시작 | `Cloud Account Administrator Connected` | 0 | — |
| 세션 끝 | `Cloud Account Administrator Disconnected` | 0 | — |
| 파일 전송 | `Transferred files with action 'Transfer': <파일 이름들>` | 0 | 201 |
| 명령 실행 | `Executed command of length: <길이>` | 0 | 200 |

- 두 자료의 이벤트 ID 가 다릅니다. 버전에 따라 바뀐 것으로 보이지만 어느 버전부터인지는 확인하지 못했습니다. 그래서 이벤트 ID 보다 메시지 문구로 찾습니다.
- 명령 실행 이벤트에는 명령 내용이 없고 길이만 남습니다.
- "Cloud Account Administrator" 는 클라우드판의 기본 관리자 이름으로 보이지만, 자체 서버에서 이 자리에 다른 사용자 이름이 들어가는지는 확인하지 못했습니다.

### 명령 실행 스크립트

명령 실행 기능을 쓰면 부모 프로세스 ScreenConnect.ClientService.exe 아래에서 cmd.exe 가 뜹니다. 아래는 Sigma 규칙에 실린 명령줄 예시입니다.

```
"cmd.exe" /c "C:\Windows\TEMP\ScreenConnect\23.6.8.8644\3c41d689-…run.cmd"
```

스크립트 파일 이름은 UUID 뒤에 `run.cmd` 또는 `run.ps1` 이 붙은 꼴입니다.

## 증거로서 의미

**증명하는 것**

- 7045 와 서비스 명령줄은 이 PC 가 어느 중계 서버(h)와 포트(p)로 접속하도록 설치됐는지 보여 줍니다. 세션 종류(e)와 클라이언트 고유 ID(s)도 같이 남습니다.
- Connected·Disconnected 이벤트는 세션이 열리고 닫힌 시각을 보여 줍니다.
- 파일 전송 이벤트는 옮긴 파일의 이름을 보여 줍니다.
- 명령 실행 이벤트는 명령을 실행한 시각과 명령 길이를 보여 줍니다.
- 임시 폴더에 스크립트 파일이 남아 있으면 실행한 명령 내용을 볼 수 있습니다.

**증명하지 못하는 것**

- 명령 실행 이벤트만으로는 무슨 명령인지 모릅니다. 스크립트 파일, 4688, Sysmon 1 로 내용을 채웁니다.
- 스크립트 파일이 실행 뒤에도 남는지는 이번 자료로 확인하지 못했습니다. 파일이 없으면 [마스터 파일 테이블](../../filesystem/mft.md)과 [USN 변경 저널](../../filesystem/usnjrnl.md)에서 이름과 시각을 찾습니다.
- 이벤트에 적힌 이름(Cloud Account Administrator 등)은 ScreenConnect 계정 이름입니다. 조작한 사람을 가리키지 않습니다.
- 서버 쪽 Session.db 의 구조는 확인하지 못했습니다. 서버에서 세션 목록을 읽는 법은 이 페이지에서 다루지 않습니다.

보고서에는 기록이 말하는 만큼만 씁니다. 예를 들면 "Application 로그에 원본 `ScreenConnect Client (…)` 의 `Executed command of length` 이벤트가 이 시각에 있다. 이 이벤트에는 명령 내용이 없다. 같은 시각의 4688 에는 ScreenConnect.ClientService.exe 가 띄운 cmd.exe 가 `C:\Windows\Temp\ScreenConnect\` 아래 run.cmd 를 실행한 기록이 있다." 처럼 씁니다.

## 시각 해석

- Application 이벤트와 7045 의 시각은 이벤트 레코드 시각입니다. 레코드 시각을 읽는 법은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.
- 명령 실행 이벤트, 스크립트 파일의 생성 시각, cmd.exe 의 프로세스 생성 시각을 한 줄로 늘어놓고, 세 시각이 가까우면 같은 명령의 흔적으로 묶을 근거로 삼습니다.
- 세션 시작(Connected)과 끝(Disconnected) 사이에 있는 파일 전송·명령 실행 이벤트만 그 세션에 묶습니다.

## 함정과 한계

- **이벤트 ID 가 버전마다 다릅니다.** ID 0 과 200·201 을 모두 찾거나, 메시지 문구로 찾습니다.
- **원본 이름에 설치마다 다른 16진 문자열이 붙습니다.** 원본 이름을 통째로 맞추지 말고 `ScreenConnect` 로 시작하는지로 거릅니다.
- **제품 이름이 둘입니다.** 실행 파일과 폴더 이름에 ConnectWiseControl 이 들어간 것도 찾습니다.
- **Sysmon 자료가 망가졌을 수 있습니다.** 서비스 명령줄은 SYSTEM 하이브와 트랜잭션 로그에서 되살릴 수 있습니다.
- **분석 PC 에서 메시지가 비어 보일 수 있습니다.** 이벤트 뷰어가 문구를 만들지 못하면 이벤트 XML 의 데이터 부분에서 문구를 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

이 페이지의 흔적은 이벤트 로그, 레지스트리, 텍스트 스크립트입니다. ScreenConnect 만의 이진 구조는 이번 자료로 확인한 것이 없어 헥스 예시를 싣지 않습니다. 이벤트 레코드를 헥스로 따라가는 법은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.

### 공개 도구로 한 번

수집한 Application.evtx 에서 ScreenConnect 이벤트를 뽑습니다. 원본 이름이 설치마다 달라서 접두어로 거릅니다.

```powershell
Get-WinEvent -Path 'E:\case\Application.evtx' |                 # 수집한 파일 경로로 바꿉니다
  Where-Object { $_.ProviderName -like 'ScreenConnect*' } |
  Select-Object @{ n = 'UTC'; e = { $_.TimeCreated.ToUniversalTime() } }, Id, ProviderName, Message
```

System.evtx 에서는 서비스 설치 명령줄을 봅니다.

```powershell
Get-WinEvent -FilterHashtable @{ Path = 'E:\case\System.evtx'; Id = 7045 } |
  Where-Object { $_.Message -like '*ScreenConnect*' } |
  Select-Object @{ n = 'UTC'; e = { $_.TimeCreated.ToUniversalTime() } }, Message
```

`TimeCreated` 는 분석 PC 의 시간대로 바뀌어 나오므로 UTC 로 바꿔 출력합니다. 레지스트리 쪽은 Registry Explorer 같은 공개 레지스트리 뷰어로 SYSTEM 하이브의 서비스 키를 엽니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 서비스 설치 (7045·4697) | 클라이언트 서비스 설치 시각과 명령줄 | [서비스 설치](../../event-logs/7045-4697.md), [서비스·드라이버](../../persistence/services-drivers.md) |
| 프로세스 생성 (4688) · Sysmon 1 | ScreenConnect.ClientService.exe 가 띄운 cmd.exe 와 스크립트 경로 | [프로세스 생성](../../event-logs/4688.md), [Sysmon 로그](../../event-logs/sysmon/index.md) |
| Sysmon 파일 생성 | ScreenConnect.WindowsClient.exe 가 `Documents\ConnectWiseControl\Temp\` 에 만든 파일 | [Sysmon 로그](../../event-logs/sysmon/index.md) |
| PowerShell 실행 기록 | `run.ps1` 로 실행한 PowerShell 명령 | [PowerShell 실행 기록](../../event-logs/powershell-event-logs-4103-4104.md) |
| 마스터 파일 테이블 · USN 변경 저널 | 지워진 스크립트 파일의 이름과 시각 | [마스터 파일 테이블](../../filesystem/mft.md), [USN 변경 저널](../../filesystem/usnjrnl.md) |
| 서버의 프로세스 생성 | 서버 프로세스 ScreenConnect.Service.exe 가 cmd.exe·csc.exe 를 띄우면 웹셸 실행으로 의심합니다(Sigma 규칙, 2024-02-26 작성) | [이벤트 로그 규칙 검색](../../../03-techniques/analysis/sigma-rules.md) |
| DNS·프록시 기록 | `control.connectwise.com`, `*.connectwise.com`, `*.screenconnect.com`, `live.screenconnect.com`. The DFIR Report 사건의 중계 서버는 `instance-…-relay.screenconnect.com:443` 꼴이었습니다 | — |

## 실습

공개 검체(NIST CFReDS 등) 가운데 ScreenConnect 흔적이 있는 이미지를 골라 아래 질문을 풀어 봅니다.

1. `C:\Program Files (x86)\` 아래에 `ScreenConnect Client (…)` 폴더가 있습니까? 괄호 안 문자열은 무엇입니까?
2. 7045 의 서비스 명령줄에서 `h`, `p`, `e` 값은 무엇입니까?
3. Application 로그에서 원본이 `ScreenConnect` 로 시작하는 이벤트를 모두 뽑습니다. 이벤트 ID 는 0 입니까, 200·201 입니까?
4. `Executed command of length` 이벤트마다, 가까운 시각의 4688 에 cmd.exe 가 있습니까? `C:\Windows\Temp\ScreenConnect\` 아래 스크립트 파일이 남아 있습니까?
5. 파일 전송 이벤트에 적힌 파일 이름이 디스크에 남아 있습니까?

## 참고 문헌

1. The DFIR Report, "From ScreenConnect to Hive Ransomware in 61 hours" (2023-09-25). https://thedfirreport.com/2023/09/25/from-screenconnect-to-hive-ransomware-in-61-hours/
2. Hunt & Hackett, "REvil: the usage of legitimate remote admin tooling" (Krijn de Mik, 2021-06-10). https://www.huntandhackett.com/blog/revil-the-usage-of-legitimate-remote-admin-tooling
3. LOLRMM API, rmm_tools.json (ScreenConnect, ConnectWise Control 항목). https://lolrmm.io/api/rmm_tools.json
4. SigmaHQ 규칙 저장소 (커밋 16eb587, 2026-09-22). rules/windows/builtin/application/screenconnect/win_app_remote_access_tools_screenconnect_command_exec.yml, …_file_transfer.yml, rules/windows/file/file_event/file_event_win_remote_access_tools_screenconnect_remote_file.yml, rules/windows/process_creation/proc_creation_win_remote_access_tools_screenconnect_remote_execution.yml, …_screenconnect_installation_cli_param.yml, …_screenconnect_webshell.yml. https://github.com/SigmaHQ/sigma
