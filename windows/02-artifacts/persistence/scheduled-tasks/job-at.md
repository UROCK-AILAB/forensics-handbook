# 옛 작업 파일 (.job·at)

> 상위 허브: [예약 작업 (Scheduled Tasks)](/02-artifacts/persistence/scheduled-tasks/index.md)

## 한 줄 요약

XML 작업 정의가 나오기 전에는 예약 작업을 `.job` 이라는 바이너리 파일로 저장했습니다. `.job` 파일에는 실행할 프로그램, 인자, 작성자, 트리거, 마지막 실행 시각, 상태가 들어 있습니다. `at` 은 정해진 시각에 명령을 실행하도록 예약하는 옛 명령입니다. Windows XP 까지의 시스템을 보거나, 옛 방식으로 만든 작업의 흔적을 볼 때 이 페이지를 씁니다.

## 무엇을 기록하나 · 왜 생기나

`.job` 파일 하나에 작업 하나가 들어 있습니다. 파일은 두 부분으로 나뉩니다.

- 고정 길이 부분(68바이트): 버전, 작업 식별자, 재시도·유휴 설정, 최대 실행 시간, 종료 코드, 상태, 마지막 실행 시각
- 가변 길이 부분: 응용 프로그램 이름, 인자, 작업 폴더, 작성자, 설명, 트리거 같은 문자열과 목록

문자열은 BOM 없는 UTF-16 LE 로 적습니다. 인코딩은 [문자 인코딩 (UTF-16LE·UTF-8·CP949)](/01-foundations/value-decoding/utf-16le-utf-8-cp949.md)에서 다룹니다.

Vista·2008 부터 쓰는 XML 작업 정의는 [작업 정의 파일 (System32\Tasks XML)](/02-artifacts/persistence/scheduled-tasks/system32-tasks-xml.md)에서 다룹니다.

## 위치와 버전별 차이

### XP 의 레지스트리

XP 에서는 `HKLM\Software\Microsoft\SchedulingAgent` 키를 씁니다. 이 키에는 다음 값이 있습니다.

- DataVersion, LastTaskRun, LogPath, MaxLogSizeKB, MinutesBeforeIdle, OldName, PriorDataVersion, TasksFolder

winreg-kb 문서에는 이 값들의 뜻이 비어 있습니다. 다만 TasksFolder 와 LogPath 는 이름으로 보아 작업 폴더와 로그 파일의 위치를 찾는 첫 단서입니다. `.job` 파일의 기본 위치와 XP 작업 로그 파일은 이번 조사에서 확인하지 못했습니다. XP 검체에서는 TasksFolder 값을 먼저 읽고, 그 폴더를 봅니다.

Vista 이후의 `Schedule` 키는 [작업 캐시 레지스트리 (TaskCache Tree·Tasks)](/02-artifacts/persistence/scheduled-tasks/taskcache-tree-tasks.md)에서 다룹니다.

### 제품 버전 값

`.job` 파일의 첫 2바이트는 제품 버전입니다. 형식 명세(libyal dtformats)의 표에는 다음 값이 있습니다.

| 제품 버전 | Windows |
|---|---|
| 0x0400 | NT 4.0 |
| 0x0500 | 2000 |
| 0x0501 | XP |
| 0x0600 | Vista |
| 0x0601 | 7 |
| 0x0602 | 8 |
| 0x0603 | 8.1 |
| 0x0a00 | 10 |

표에는 Windows 10 값까지 있습니다. 하지만 Vista 이후 시스템에서 `at` 이나 `schtasks /v1` 으로 만든 작업이 `.job` 을 함께 남기는지는 이번 조사에서 확인하지 못했습니다.

한 PC 의 `C:\Windows\Tasks` 폴더에는 `SA.DAT` 파일 하나만 있었습니다. 크기는 6바이트(`06 00 00 00 02 03`)였습니다. 이 파일의 뜻은 확인하지 못했습니다. (확인 범위: Win11 25H2 한 대)

## 구조

### 고정 길이 부분 (68바이트)

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 2 | 제품 버전 |
| 2 | 2 | 형식 버전 |
| 4 | 16 | 작업 식별자 (UUID, 리틀 엔디언) |
| 20 | 2 | 응용 프로그램 이름 오프셋 |
| 22 | 2 | 트리거 오프셋 |
| 24 | 2 | 오류 재시도 횟수 |
| 26 | 2 | 재시도 간격 (분) |
| 28 | 2 | 유휴 기한 (분) |
| 30 | 2 | 유휴 대기 (분) |
| 32 | 4 | 우선순위 |
| 36 | 4 | 최대 실행 시간 (밀리초) |
| 40 | 4 | 종료 코드 |
| 44 | 4 | 상태 |
| 48 | 4 | 플래그 |
| 52 | 16 | 마지막 실행 시각 (SYSTEMTIME) |

마지막 실행 시각은 SYSTEMTIME 구조입니다. 연·월·요일·일·시·분·초·밀리초가 2바이트씩 차례로 들어 있습니다.

### 가변 길이 부분

고정 길이 부분 뒤에 다음 항목이 이 순서로 옵니다.

1. 실행 중인 인스턴스 수 (2바이트)
2. 응용 프로그램 이름
3. 인자
4. 작업 폴더
5. 작성자
6. 설명 (Comment)
7. 사용자 데이터
8. 예약 데이터
9. 트리거 (없을 수 있음)
10. 작업 서명 (없을 수 있음)

응용 프로그램 이름과 인자는 작업이 실행할 대상입니다. 작성자와 설명도 문자열로 남습니다.

### 트리거

트리거 하나는 48바이트입니다. 첫 칸은 트리거 크기이고, 값은 항상 48 입니다. 오프셋은 트리거 시작점 기준입니다.

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 2 | 트리거 크기 (48) |
| 2 | 2 | 예약 |
| 4 · 6 · 8 | 2씩 | 시작 날짜 (연·월·일) |
| 10 · 12 · 14 | 2씩 | 끝 날짜 (연·월·일) |
| 16 · 18 | 2씩 | 시작 시각 (시·분) |
| 20 | 4 | 지속 시간 (분) |
| 24 | 4 | 간격 (분) |
| 28 | 4 | 트리거 플래그 |
| 32 | 4 | 트리거 종류 |
| 36 | 6 | 종류별 값 |
| 42 ~ 47 | 6 | 채움·예약 |

42 이후 칸의 세부 경계는 libyal dtformats 원문 표로 확인합니다.

### 상태 값

| 값 | 뜻 |
|---|---|
| 0x00041300 | SCHED_S_TASK_READY. 다음 예약 시각에 실행할 준비가 된 상태 |
| 0x00041301 | SCHED_S_TASK_RUNNING. 실행 중 |
| 0x00041305 | SCHED_S_TASK_NOT_SCHEDULED. 예약대로 실행하는 데 필요한 속성 가운데 설정되지 않은 것이 있음 |

libyal dtformats 표에는 이 세 값이 있습니다. 상수 이름과 뜻은 Microsoft 의 작업 스케줄러 오류·성공 상수 문서(WinError.h)를 따랐습니다. 같은 문서에는 0x00041302(사용 안 함), 0x00041303(아직 실행한 적 없음), 0x00041307(유효한 트리거 없음) 같은 값도 있습니다.

Vista 이후 작업 스케줄러에서도 같은 꼴의 값이 보입니다. 한 PC 에서 한 번도 실행하지 않은 작업을 `Get-ScheduledTaskInfo` 로 조회했습니다. LastRunTime 은 1999-11-29 15:00:00Z, LastTaskResult 는 0x00041303 이었습니다. (확인 범위: Win11 25H2 한 대) 0x00041303 은 Microsoft 문서에서 SCHED_S_TASK_HAS_NOT_RUN(아직 실행한 적 없음)입니다. 도구가 1999-11-29 를 보여 주면 실제 실행 시각으로 읽지 않습니다.

## at 명령

Microsoft 문서는 `at` 을 다음과 같이 설명합니다.

- 정해진 날짜와 시각에 명령이나 프로그램을 실행하도록 예약합니다.
- Schedule 서비스가 돌고 있을 때만 쓸 수 있습니다.
- 인자 없이 실행하면 예약 목록을 보여 줍니다.
- 로컬 Administrators 그룹 구성원이어야 씁니다.
- 예약한 명령은 백그라운드로 돌고, 현재 폴더는 systemroot 입니다.

형식은 다음과 같습니다.

```
at [\\computername] <time> [/interactive] [/every:date[,...] | /next:date[,...]] <command>
```

`\\computername` 을 쓰면 원격 컴퓨터에 작업을 예약합니다. 예약을 지울 때는 `/delete [/yes]` 를 씁니다.

**실행 시간 제한.** 예약한 명령은 기본으로 72시간이 지나면 멈춥니다. `HKLM\SYSTEM\CurrentControlSet\Services\Schedule` 에 REG_DWORD 값 `atTaskMaxHours` 를 넣으면 이 제한을 바꿉니다. 0 은 제한 없음, 1~99 는 시간 수입니다. 오프라인 SYSTEM 하이브에서는 CurrentControlSet 대신 실제로 쓰인 ControlSet 번호 키를 봅니다. 방법은 [레지스트리 하이브 구조](/01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

**저장 위치.** 문서에는 "Scheduled commands are stored in the registry." 라는 문장만 있습니다. 어느 키인지는 적혀 있지 않습니다. 이 문서의 날짜는 2017년입니다.

**예약 작업 폴더에서 보이는 이름.** `at` 으로 만든 작업은 예약 작업 폴더에 `at3478` 같은 이름으로 보입니다. 그 폴더에서 작업을 고치면 일반 예약 작업으로 바뀝니다. 그러면 `at` 목록에서 사라지고, `at` 용 계정 설정도 적용되지 않습니다.

**최근 Windows.** 문서에는 폐지(deprecated) 안내가 없습니다. 그러나 한 PC 에서 `at.exe` 를 인자 없이 실행하자 다음 메시지가 나왔고, 종료 코드는 1 이었습니다. (확인 범위: Win11 25H2 한 대)

```
The AT command has been deprecated. Please use schtasks.exe instead.
The binding handle is invalid.
```

`at` 이 어느 Windows 버전부터 폐지되었는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것**

- `.job` 파일이 있으면 그 작업을 정의한 적이 있습니다. 응용 프로그램 이름과 인자는 실행하도록 설정된 대상입니다.
- 마지막 실행 시각 칸에 값이 있으면, 작업 스케줄러가 그 작업을 실행한 시각을 적어 둔 것입니다. 시간대는 아래 "시각 해석" 을 봅니다.
- 상태 값과 종료 코드는 마지막으로 기록된 작업 상태를 보여 줍니다.
- `at` 명령에 `\\computername` 을 쓰면 원격 컴퓨터에 작업을 넣을 수 있습니다. 그래서 서버에서 `at` 작업이 보이면 다른 컴퓨터에서 넣었을 가능성도 따져 봅니다.

**증명하지 못하는 것**

- 작성자 칸은 문자열입니다. 실제로 누가 작업을 만들었는지 확정하지 못합니다.
- 마지막 실행 시각은 한 번뿐입니다. 그 전에 몇 번 실행했는지는 이 칸으로 알 수 없습니다.
- `at3478` 같은 이름만으로 `at` 으로 만들었다고 단정하지 못합니다. 이름은 사람이 붙일 수도 있습니다.
- 예약 작업 폴더에서 고친 `at` 작업은 일반 작업으로 바뀝니다. 그래서 지금 일반 작업이라고 처음부터 그랬다고 보지 않습니다.

## 시각 해석

- 마지막 실행 시각은 FILETIME 이 아니라 SYSTEMTIME 입니다. 연·월·일·시·분·초 칸을 바로 읽습니다. 시각 형식은 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다.
- 이 값이 현지 시각인지 UTC 인지는 확정되지 않았습니다. 형식 명세에도 "TODO: confirm this is local time" 이라고 남아 있습니다. 보고서에 쓰기 전에 같은 시각 무렵의 다른 기록과 맞춰 봅니다. 시간대는 [시간대 설정](/02-artifacts/system-account/time-zone.md)에서 확인합니다.
- `.job` 파일 자체의 만든·고친 시각은 파일 시스템에 남습니다. 파일 시각을 읽는 법은 [마스터 파일 테이블 ($MFT)](/02-artifacts/filesystem/mft.md)에서 다룹니다.

## 함정과 한계

- **`.job` 파일의 기본 위치를 가정하지 않습니다.** 이번 조사에서 확인하지 못했습니다. XP 는 SchedulingAgent 키의 TasksFolder 값부터 봅니다.
- **Vista 이후에도 `.job` 이 남는지 모릅니다.** 제품 버전 표에 Windows 10 값이 있다는 것만으로 판단하지 않습니다. 검체에서 직접 확인합니다.
- **문자열에 BOM 이 없습니다.** UTF-16 LE 로 키워드를 검색해야 응용 프로그램 이름이 걸립니다.
- **트리거 오프셋은 트리거 시작점 기준입니다.** 파일 처음부터 세면 날짜와 시각을 잘못 읽습니다. 트리거 위치는 고정 길이 부분의 트리거 오프셋(22)에서 읽습니다.
- **`at` 작업의 레지스트리 위치는 문서에 없습니다.** 문서 문장 하나로 특정 키를 단정하지 않습니다.
- **최근 Windows 에서 `at` 은 돌지 않을 수 있습니다.** Win11 25H2 한 대에서는 폐지 메시지와 함께 실패했습니다. 최근 시스템에서 `at` 흔적이 나오면 실제로 작업이 만들어졌는지 다른 기록으로 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 고정 길이 부분(68바이트) 예시입니다. 실제 검체에서 뽑은 값이 아닙니다. 형식 버전, 두 오프셋, 우선순위, 플래그는 0 으로 채웠습니다. 가변 길이 부분을 싣지 않았으므로 두 오프셋은 해석하지 않습니다.

```
00000000  01 05 00 00 44 33 22 11 66 55 88 77 99 aa bb cc  |....D3".fU.w....|
00000010  dd ee ff 00 00 00 00 00 00 00 00 00 3c 00 0a 00  |............<...|
00000020  00 00 00 00 00 14 73 0f 00 00 00 00 00 13 04 00  |......s.........|
00000030  00 00 00 00 d8 07 03 00 05 00 0e 00 09 00 1e 00  |................|
00000040  0f 00 00 00                                      |....|
```

1. 0x00 의 `01 05` 는 리틀 엔디언으로 0x0501 입니다. 제품 버전 XP 입니다.
2. 0x04~0x13 의 16바이트는 작업 식별자입니다. 리틀 엔디언 UUID 로 읽으면 `{11223344-5566-7788-99AA-BBCCDDEEFF00}` 입니다.
3. 0x1C 의 `3c 00` 은 유휴 기한 60분, 0x1E 의 `0a 00` 은 유휴 대기 10분입니다.
4. 0x24 의 `00 14 73 0f` 는 0x0F731400, 곧 259,200,000 밀리초입니다. 72시간입니다.
5. 0x28 의 종료 코드는 0 입니다.
6. 0x2C 의 `00 13 04 00` 은 0x00041300 입니다. 상태는 준비입니다.
7. 0x34 부터 16바이트가 마지막 실행 시각입니다. `d8 07` 은 2008년, `03 00` 은 3월, `05 00` 은 요일 칸, `0e 00` 은 14일입니다. 이어서 `09 00`·`1e 00`·`0f 00`·`00 00` 은 9시 30분 15초 0밀리초입니다. 시간대는 확정되지 않았습니다.

### 공개 도구로 한 번

libyal dtformats 의 "Job file format" 문서가 칸마다 뜻을 적어 두었습니다. 헥스 편집기로 파일을 열고 이 문서의 표와 맞춰 읽습니다. 고정 길이 부분은 Python 표준 라이브러리로도 풀 수 있습니다.

```python
import struct, uuid

def job_fixed(b):                          # b: .job 파일 앞 68바이트
    product, fmt = struct.unpack_from("<HH", b, 0)
    f = struct.unpack_from("<6H5I", b, 20) # 오프셋 20~51
    st = struct.unpack_from("<8H", b, 52)  # 연·월·요일·일·시·분·초·밀리초
    return {
        "product_version": hex(product),
        "job_id": str(uuid.UUID(bytes_le=bytes(b[4:20]))),
        "retry_count": f[2], "retry_interval_min": f[3],
        "idle_deadline_min": f[4], "idle_wait_min": f[5],
        "max_run_ms": f[7], "exit_code": hex(f[8]), "status": hex(f[9]),
        "last_run": "%04d-%02d-%02d %02d:%02d:%02d.%03d"
                    % (st[0], st[1], st[3], st[4], st[5], st[6], st[7]),
    }
```

위 헥스 예시를 넣으면 `status` 는 `0x41300`, `last_run` 은 `2008-03-14 09:30:15.000` 이 나옵니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 작업 정의 XML · 작업 캐시 | Vista 이후의 같은 작업 정보 | [작업 정의 파일](/02-artifacts/persistence/scheduled-tasks/system32-tasks-xml.md), [작업 캐시 레지스트리](/02-artifacts/persistence/scheduled-tasks/taskcache-tree-tasks.md) |
| 프리페치 | `at.exe` 와 작업이 실행한 프로그램의 실행 흔적 | [프리페치](/02-artifacts/execution/prefetch/index.md) |
| 이벤트 로그 | XP 는 EVT 형식, Vista 이후는 EVTX 형식 | [이벤트 로그 형식](/01-foundations/database-log-formats/evtx-evt-etl/index.md) |
| 마스터 파일 테이블 | `.job` 파일이 생기고 바뀐 시각 | [$MFT](/02-artifacts/filesystem/mft.md) |
| 측면 이동 | 원격 컴퓨터에 `at` 으로 작업을 넣은 경우 | [계정 탈취와 측면 이동](/04-scenarios/incident/credential-theft-lateral-movement/index.md) |

## 실습

공개 검체(NIST CFReDS 등) 가운데 Windows XP 이미지로 아래 질문을 풀어 봅니다.

1. SOFTWARE 하이브의 SchedulingAgent 키에서 TasksFolder 와 LogPath 값은 무엇입니까?
2. TasksFolder 가 가리키는 폴더에 `.job` 파일이 있습니까? 제품 버전 값은 무엇입니까?
3. 각 `.job` 의 응용 프로그램 이름과 인자는 무엇입니까?
4. 마지막 실행 시각과 상태 값은 무엇입니까? 그 시각 무렵 같은 프로그램의 실행 흔적이 다른 곳에 있습니까?
5. `at` 으로 만든 것으로 보이는 이름의 작업이 있습니까?

## 참고 문헌

1. libyal winreg-kb, "Task scheduler". https://github.com/libyal/winreg-kb/blob/main/docs/sources/system-keys/Task-scheduler.md
2. libyal dtformats, "Job file format". https://github.com/libyal/dtformats/blob/main/documentation/Job%20file%20format.asciidoc
3. Microsoft Learn, "at" (Windows Commands). https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/at
4. Microsoft Learn, "Task Scheduler error and success constants (WinError.h)". https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-error-and-success-constants
