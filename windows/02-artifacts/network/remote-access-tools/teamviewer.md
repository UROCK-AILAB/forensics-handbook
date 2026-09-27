---
title: "팀뷰어"
parent: "원격 제어 프로그램"
grand_parent: "아티팩트 · 네트워크"
nav_order: 2380
---

# 팀뷰어 (TeamViewer)

팀뷰어 (TeamViewer) 는 원격 지원 프로그램입니다. 설치 폴더의 동작 로그와 받은 접속 목록에 누가 언제 들어왔는지가 남습니다. 받는 쪽 PC 의 `Connections_incoming.txt` 에는 줄마다 상대 TeamViewer ID, 시작·끝 시각, 로컬 사용자가 적힙니다.

## 무엇을 기록하나 · 왜 생기나

TeamViewer 를 설치하면 서비스가 하나 등록됩니다. 원격 세션이 시작되면 서비스 프로세스(TeamViewer_Service.exe)가 `--IPCport 5939 --Module 1` 인자로 TeamViewer_Desktop.exe 를 띄웁니다. 이 모양은 받는 쪽에서 세션이 시작된 신호입니다[3].

접속 기록은 두 파일에 따로 남습니다.

- 동작 로그 (`TeamViewer15_Logfile.log`): 들어오고 나간 접속, 시각, 상대 호스트 이름, TeamViewer ID 가 남습니다. 받는 쪽과 거는 쪽 모두에 생깁니다.
- 받은 접속 목록 (`Connections_incoming.txt`): 들어온 접속을 한 줄씩 적습니다. 받는 쪽에만 생깁니다.

이 밖에 설치 기록, 채팅 캐시, 원격 인쇄 DB, 레지스트리 값이 남습니다. 받는 쪽과 거는 쪽이 무엇인지, 설치하지 않고 실행하면 무엇이 달라지는지는 [허브](index.md)에서 정리합니다.

## 위치와 버전별 차이

아래 경로는 TeamViewer 15.32.3.0 기준입니다[1]. 로그 파일 이름의 숫자 15 는 주 버전과 같아서 주 버전이 다르면 이 숫자도 다르다고 보고, `TeamViewer*_Logfile.log` 형식으로 넓게 찾습니다.

### 파일

| 흔적 | 경로 | 메모 |
|---|---|---|
| 설치 폴더 | `C:\Program Files\TeamViewer` | 실행 파일: TeamViewer.exe, TeamViewer_Desktop.exe, TeamViewer_Service.exe, tv_w32.exe, tv_x64.exe |
| 동작 로그 | `C:\Program Files\TeamViewer\TeamViewer15_Logfile.log` | 받는 쪽·거는 쪽 모두 |
| 동작 로그 (휴대용 실행·설치 중) | `%APPDATA%\TeamViewer\TeamViewer15_Logfile.log` | 설치하지 않고 실행할 때와 설치하는 동안 여기에 씁니다 |
| 받은 접속 목록 | `C:\Program Files\TeamViewer\Connections_incoming.txt` | 받는 쪽만 |
| 설치 기록 | `%LOCALAPPDATA%\Temp\TeamViewer\TV15Install.log` | 설치한 사용자의 SID, 시각, 버전, OS 버전 |
| 네트워크 포트 로그 | `C:\Program Files\TeamViewer\TVNetwork.log` | 세션 중 쓴 포트. 포렌식 가치가 낮습니다[1] |
| 채팅 캐시 | `%LOCALAPPDATA%\TeamViewer\Database\tvchatfilecache.db` | SQLite 3 |
| 원격 인쇄 작업 | `%LOCALAPPDATA%\TeamViewer\RemotePrinting\tvprint.db` | SQLite 3. 받는 쪽 |
| 시작 메뉴 바로가기 | `%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\TeamViewer.lnk` | |
| 용도가 공개되지 않은 경로 | `C:\Users\*\AppData\Roaming\TeamViewer\MRU\RemoteSupport\*tvc` | 흔적 목록에 올라 있습니다[2]. 담긴 내용은 실제 데이터로 확인 |

받은 접속 목록은 수집할 때 `C:\Program Files*\TeamViewer\connections*.txt` 형식으로 넓게 찾습니다[2]. 설치 기록에는 설치한 사용자의 SID 가 `User-SID:      S-1-5-21-…-1001` 모양으로 적힙니다. SID 를 사용자 이름에 맞추는 법은 [사용자 프로필 목록](../../system-account/profilelist.md)에서 다룹니다. SQLite 파일을 읽는 법은 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md)에서 다룹니다.

### 레지스트리

| 키·값 | 남는 쪽 |
|---|---|
| `HKLM\SOFTWARE\TeamViewer` | 설치한 PC |
| `HKU\<SID>\SOFTWARE\TeamViewer` | 설치한 PC |
| `HKLM\SYSTEM\CurrentControlSet\Services\TeamViewer` | 설치한 PC |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\TeamViewer` | 설치한 PC |
| `HKU\<SID>\SOFTWARE\TeamViewer` 아래 MainWindowHandle, DesktopWallpaperSingleImage, MultiMedia\AudioUserSelectedCapturingEndpoint | 받는 쪽. 세션 중에 생깁니다 |
| `HKLM\SOFTWARE\TeamViewer\ConnectionHistory` | 거는 쪽. 16바이트 이진값입니다 |
| `HKU\<SID>\SOFTWARE\TeamViewer` 아래 ClientWindow_Mode, ClientWindowPositions | 거는 쪽 |

하이브 파일과 키 구조는 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

## 구조

### 동작 로그 (TeamViewer15_Logfile.log)

아래는 Synacktiv 가 공개한 줄 예시입니다.

```
2022/08/22 16:50:52.967  3476  1492 S0  CommandHandlerRouting[19]::CreatePassiveSession()
```

줄 맨 앞에는 날짜와 시각이 밀리초까지 오고 날짜는 년/월/일 순서이며, 줄 끝에는 `CommandHandlerRouting[19]::CreatePassiveSession()` 같은 함수 이름이 옵니다. 그 사이의 숫자 두 필드와 `S0` 필드의 뜻은 공개 자료에 없습니다.

접속을 찾을 때는 아래 문자열을 검색합니다.

| 문자열 | 뜻 |
|---|---|
| `CreatePassiveSession` | 접속 시도 (받는 쪽) |
| `CPersistentParticipantManager::AddParticipant` | 접속 성공 |
| `SessionStateParticipants::AddParticipant` | 세션 생성 |
| `SessionTerminate` | 접속 끝 (받는 쪽) |
| `TerminateSession` | 접속 끝 (거는 쪽) |

로그에 적히는 참가자 종류(type) 값 가운데 3 은 화면을 내주는 쪽, 곧 받는 쪽입니다. 6 은 거는 쪽 참가자입니다.

### 받은 접속 목록 (Connections_incoming.txt)

아래는 Synacktiv 가 공개한 줄 예시입니다.

```
1025538549      mechant_host  22-08-2022 14:50:52     22-08-2022 14:51:09     lab     RemoteControl   {5a0ba592-76be-48de-8015-2365251d6520}
```

| 순서 | 필드 | 예시 값 |
|---|---|---|
| 1 | 상대 TeamViewer ID | 1025538549 |
| 2 | 상대 호스트 이름 | mechant_host |
| 3 | 시작 시각 | 22-08-2022 14:50:52 |
| 4 | 끝 시각 | 22-08-2022 14:51:09 |
| 5 | 로컬 사용자 | lab |
| 6 | 접속 종류 | RemoteControl |
| 7 | 세션 GUID | {5a0ba592-76be-48de-8015-2365251d6520} |

날짜는 일-월-년 순서입니다. 필드 사이 구분 문자가 탭인지 공백인지는 실제 데이터로 확인합니다.

## 증거로서 의미

**증명하는 것**

- `Connections_incoming.txt` 한 줄은 그 TeamViewer ID 에서 이 PC 로 들어온 접속 기록입니다. 시작·끝 시각, 이 PC 의 로컬 사용자, 접속 종류가 같은 줄에 남습니다.
- 동작 로그의 `CreatePassiveSession` 줄은 받는 쪽에서 접속 시도가 있었다는 기록입니다. 뒤이어 `AddParticipant` 줄이 있으면 접속이 성공했다는 기록입니다.
- 거는 쪽 PC 에 `TerminateSession` 줄이나 ConnectionHistory 값이 있으면, 그 PC 에서 다른 PC 로 접속을 건 흔적입니다.
- 받는 쪽 사용자 하이브에 MainWindowHandle 같은 세션 값이 있으면, 그 사용자 아래에서 원격 세션이 열린 적이 있다고 볼 근거가 됩니다.
- `tvprint.db` 는 원격 세션에서 인쇄한 작업을 보여 줍니다.

**증명하지 못하는 것**

- TeamViewer ID 와 상대 호스트 이름은 사람을 가리키지 않습니다. 조작한 사람을 특정하려면 다른 근거가 필요합니다.
- 받은 접속 목록에는 세션 중에 한 일이 없습니다. 필드 일곱 개 가운데 행동을 적는 필드가 없습니다.
- 거는 쪽의 나간 접속 목록 파일은 공개 자료에 없습니다. 거는 쪽에서는 동작 로그와 레지스트리를 봅니다.
- ConnectionHistory 16바이트의 구조는 공개 자료에 없습니다. 이 값만으로 상대 ID 나 시각을 읽어 내지 않습니다.
- 파일이 없다고 접속이 없었다고 단정하지 않습니다. 휴대용으로 실행했으면 로그가 `%APPDATA%` 아래에 있고, 로그를 지웠을 수도 있습니다.

보고서에는 기록으로 확인되는 만큼만 씁니다. 예를 들면 "`Connections_incoming.txt` 에 TeamViewer ID 1025538549(호스트 이름 mechant_host)에서 로컬 사용자 lab 으로 들어온 RemoteControl 접속이 시작·끝 시각과 함께 적혀 있다. 이 기록만으로는 세션 중에 한 일과 조작한 사람을 알 수 없다." 처럼 씁니다. 예의 값은 참고 문헌 [1] 의 예시입니다.

## 시각 해석

- 동작 로그 시각이 UTC 인지 현지 시각인지는 공개 자료에 없습니다.
- Synacktiv 시험의 두 예시는 같은 접속으로 보입니다[1]. 동작 로그 줄은 16:50:52 이고, 받은 접속 목록 줄의 시작 시각은 14:50:52 입니다. 두 값은 정확히 2시간 차이 납니다.
- 시험 환경이 프랑스 여름 시간(UTC+2)이었다면, 받은 접속 목록은 UTC 이고 동작 로그는 현지 시각일 수 있습니다. 공식 문서에는 이 내용이 없습니다.
- 사건에서는 같은 접속을 두 파일에서 찾아 차이를 직접 잽니다. 그 차이를 PC 의 시간대 설정과 맞춰 봅니다. 시간대 설정은 [시간대 설정](../../system-account/time-zone.md)에서 봅니다.
- 받은 접속 목록의 날짜는 일-월-년 순서입니다. 일이 12 이하이면 월과 헷갈리기 쉽습니다.
- 설치 기록(`TV15Install.log`)에도 시각이 적힙니다. 이 시각의 시간대도 실제 데이터로 확인합니다.

## 함정과 한계

- **두 로그의 시간대가 다를 수 있습니다.** 한 파일의 시각을 다른 파일에 그대로 이어 붙이지 않습니다.
- **파일 이름의 숫자가 버전마다 다릅니다.** `TeamViewer15_Logfile.log` 이름 그대로만 찾으면 다른 주 버전의 로그를 놓칩니다.
- **로그 위치가 두 곳입니다.** 설치 폴더와 `%APPDATA%\TeamViewer\` 를 모두 수집합니다.
- **로그를 지웠을 수 있습니다.** Sigma 규칙 "TeamViewer Log File Deleted" 는 이름에 `\TeamViewer_` 가 들어간 .log 파일을 지우는 동작을 증거 인멸 시도로 봅니다[3]. 지운 파일의 흔적은 [지운 파일의 흔적 찾기](../../../04-scenarios/activity/deleted-file-traces.md)에서 다룹니다.
- **TVNetwork.log 에 기대지 않습니다.** 세션 중 쓴 포트만 남습니다.

## 직접 분석해 보기

### 헥스로 한 번

이 페이지의 로그와 목록은 텍스트 파일입니다. 이진 구조가 있는 값은 ConnectionHistory(16바이트) 하나입니다. 이 값의 구조는 공개 자료에 없어 헥스 예시를 싣지 않습니다.

텍스트 파일은 파일 앞 몇 바이트를 헥스로 보고 BOM 이 있는지 확인한 뒤 읽습니다. 인코딩을 판별하는 법은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)에서 다룹니다.

### 공개 도구로 한 번

동작 로그에서 접속 줄만 뽑을 때는 PowerShell 로 충분합니다.

```powershell
$log = 'E:\mount\Program Files\TeamViewer\TeamViewer15_Logfile.log'   # 마운트한 경로로 바꿉니다
Select-String -Path $log -Pattern 'CreatePassiveSession','AddParticipant','SessionTerminate','TerminateSession'
```

받은 접속 목록은 아래 Python 코드로 표처럼 풉니다. 사용자 이름에 공백이 있어도 되도록 앞 여섯 필드와 뒤 두 필드를 먼저 떼어 냅니다. 파일이 UTF-8 이 아니면 `encoding` 을 바꿉니다.

```python
from datetime import datetime

path = r"E:\mount\Program Files\TeamViewer\Connections_incoming.txt"  # 마운트한 경로로 바꿉니다
fmt = "%d-%m-%Y %H:%M:%S"                                             # 일-월-년

with open(path, encoding="utf-8", errors="replace") as f:
    for line in f:
        t = line.split()
        if len(t) < 9:
            continue
        try:
            start = datetime.strptime(t[2] + " " + t[3], fmt)
            end = datetime.strptime(t[4] + " " + t[5], fmt)
        except ValueError:
            continue
        user = " ".join(t[6:-2])
        print(t[0], t[1], start, end, end - start, user, t[-2], t[-1])
```

출력의 시각은 파일에 적힌 값 그대로입니다. 시간대를 정한 뒤에 보고서에 옮깁니다.

레지스트리 값은 공개 레지스트리 뷰어로 SOFTWARE 하이브와 사용자 NTUSER.DAT 를 열어 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 서비스 설치 (System 7045) | ServiceName "TeamViewer", ImagePath `C:\Program Files\TeamViewer\TeamViewer_Service.exe`, 자동 시작. 설치 시각 | [서비스 설치](../../event-logs/7045-4697.md) |
| 프로세스 생성 · Sysmon | TeamViewer_Service.exe 가 TeamViewer_Desktop.exe 를 `--IPCport 5939 --Module 1` 로 띄운 시각. 받는 쪽 세션이 시작된 때 | [프로세스 생성](../../event-logs/4688.md), [Sysmon 로그](../../event-logs/sysmon/index.md) |
| 프리페치 | `TEAMVIEWER.EXE-[A-F0-9]{8}.pf`. 실행 시각과 횟수 | [프리페치](../../execution/prefetch/index.md) |
| 설치 프로그램 | `Uninstall\TeamViewer` 키 | [설치 프로그램](../../system-account/uninstall.md) |
| DNS·프록시 기록 | 접속 도메인 `router15.teamviewer.com:443`, `client.teamviewer.com:443`, `taf.teamviewer.com:443` | — |
| 메모리 | 뮤텍스 TeamViewer_LogMutex, TeamViewerHooks_DynamicMemMutex | [메모리 분석](../../../03-techniques/analysis/memory-forensics/index.md) |
| 이벤트 로그 규칙 | 세션 시작, 로그 삭제를 잡는 Sigma 규칙 | [이벤트 로그 규칙 검색](../../../03-techniques/analysis/sigma-rules.md) |

## 실습

공개 데이터셋(NIST CFReDS 등) 가운데 TeamViewer 흔적이 있는 이미지를 골라 아래 질문을 풀어 봅니다.

1. `Connections_incoming.txt` 가 있습니까? 줄마다 상대 ID, 시작·끝 시각, 로컬 사용자를 표로 정리합니다.
2. 같은 접속을 동작 로그의 `CreatePassiveSession` 줄에서 찾습니다. 두 시각은 몇 시간 차이 납니까? 그 차이는 PC 의 시간대 설정과 맞습니까?
3. System 로그의 7045 에서 TeamViewer 서비스가 설치된 시각을 찾습니다. `TV15Install.log` 의 SID 는 어느 사용자입니까?
4. 이 PC 는 받는 쪽입니까, 거는 쪽입니까? ConnectionHistory 값과 `TerminateSession` 줄로 판단합니다.
5. `%APPDATA%\TeamViewer\` 아래에 동작 로그가 있습니까? 설치 과정에서 생긴 로그인지 휴대용 실행의 로그인지 어떻게 가려냅니까?

## 참고 문헌

1. Synacktiv, "Legitimate RATs: a comprehensive forensic analysis of the usual suspects" (Théo Letailleur, 2022-10-20). https://www.synacktiv.com/publications/legitimate-rats-a-comprehensive-forensic-analysis-of-the-usual-suspects.html
2. LOLRMM API, rmm_tools.json (TeamViewer 항목). https://lolrmm.io/api/rmm_tools.json
3. SigmaHQ 규칙 저장소 (커밋 16eb587, 2026-09-22). rules/windows/process_creation/proc_creation_win_remote_access_tools_teamviewer_incoming_connection.yml, rules/windows/file/file_delete/file_delete_win_delete_teamviewer_logs.yml. https://github.com/SigmaHQ/sigma
