# 작업 정의 파일 (System32\Tasks XML)

> 상위 허브: [예약 작업 (Scheduled Tasks)](index.md)

## 한 줄 요약

예약 작업을 등록하면 `C:\Windows\System32\Tasks` 아래에 작업 이름과 같은 파일이 하나 생깁니다. 이 파일에는 확장자가 없습니다. 파일 안에는 작업 정의가 XML 로 들어 있습니다. 무엇을, 언제, 어느 계정으로 실행할지가 여기에 적힙니다.

## 무엇을 기록하나 · 왜 생기나

작업 스케줄러 (Task Scheduler) 는 작업 하나를 등록할 때 흔적을 세 곳에 남깁니다. 레지스트리에 키가 두 개 생깁니다. 이 폴더에는 XML 파일이 하나 생깁니다. 레지스트리 쪽은 [작업 캐시 레지스트리 (TaskCache Tree·Tasks)](taskcache-tree-tasks.md)에서 다룹니다.

XML 파일에는 작업 정의 전체가 들어 있습니다.

- 실행할 프로그램과 인자
- 실행할 때(트리거)
- 실행할 계정과 권한 수준
- 작성자, 등록 일시, 설명 같은 관리 정보
- 숨김, 실행 시간 제한 같은 설정

XML 작업 정의는 Windows Vista · Server 2008 부터 쓰입니다. 그 전의 작업 파일은 [옛 작업 파일 (.job·at)](job-at.md)에서 다룹니다.

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 폴더 | `C:\Windows\System32\Tasks` |
| 파일 이름 | 작업 이름과 같습니다. 확장자가 없습니다 |
| 하위 폴더 | 작업 경로(예: `\Microsoft\Windows\...`)와 같은 모양입니다 |
| 최소 버전 | Windows Vista · Server 2008 |

레지스트리 `TaskCache\Tasks\{GUID}` 키에는 Path 값이 있습니다. 이 값 앞에 `C:\Windows\System32\Tasks` 를 붙이면 XML 파일의 경로가 됩니다. 한 PC 에서는 작업 269개가 모두 이렇게 맞았습니다. (확인 범위: Win11 25H2 한 대)

뿌리 요소 `<Task>` 에는 version 속성이 붙습니다. 한 PC 에서 이 값은 다음과 같이 나뉘었습니다. (확인 범위: Win11 25H2 한 대)

| version 속성 | 파일 수 |
|---|---|
| 1.2 | 25 |
| 1.3 | 5 |
| 1.4 | 25 |
| 1.6 | 35 |
| 속성 없음 | 179 |

속성이 없는 파일은 주로 Windows 기본 작업이었습니다. 레지스트리 Schema 값과 이 속성이 어떻게 짝을 이루는지는 [작업 캐시 레지스트리](taskcache-tree-tasks.md)에서 다룹니다.

## 구조

### 파일 첫 부분

한 PC 의 XML 271개는 모두 첫 2바이트가 `FF FE` 였습니다. 이 두 바이트는 UTF-16 LE 의 바이트 순서 표시 (BOM) 입니다. XML 선언은 `<?xml version="1.0" encoding="UTF-16"?>` 였습니다. (확인 범위: Win11 25H2 한 대) 인코딩은 [문자 인코딩 (UTF-16LE·UTF-8·CP949)](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)에서 다룹니다.

뿌리 요소는 다음 꼴입니다.

```xml
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
```

### 주요 요소

`<Task>` 바로 아래에는 요소 다섯 개가 옵니다.

| 요소 | 들어 있는 것 | 먼저 볼 자식 요소 |
|---|---|---|
| RegistrationInfo | 작성자·등록 일시 같은 관리 정보 | Author, Date |
| Triggers | 실행할 때 | LogonTrigger, CalendarTrigger |
| Principals | 실행할 계정과 권한 | UserId, LogonType, RunLevel |
| Settings | 동작 설정 | Enabled, Hidden, ExecutionTimeLimit |
| Actions | 실행할 동작 | Exec\Command, Exec\Arguments |

### RegistrationInfo

Microsoft 스키마 문서는 자식 요소를 다음과 같이 적습니다. 모든 파일에 이 요소가 다 들어 있지는 않습니다.

| 자식 요소 | 형 | 뜻 |
|---|---|---|
| Author | string | 작성자 |
| Date | dateTime | 작업이 등록된 날짜와 시각 |
| Description | | 설명 |
| Documentation | | 문서 |
| SecurityDescriptor | string | 작업의 보안 설명자 |
| Source | | 작업 출처(구성 요소·서비스·앱·사용자) |
| URI | anyURI | URI |
| Version | | 버전 |

Windows 기본 작업 가운데에는 SecurityDescriptor 에 SDDL 문자열을 넣은 것이 있습니다. Source 에 `$(@%SystemRoot%\system32\...dll,-102)` 같은 리소스 참조를 넣은 것도 있습니다. (확인 범위: Win11 25H2 한 대)

### Principals 와 Actions

`<Principals>` 아래 `<Principal id="Author">` 에는 실행 계정이 적힙니다.

- UserId: 실행할 계정
- RunLevel: 권한 수준. LeastPrivilege 또는 HighestAvailable
- LogonType: 로그온 방식. InteractiveToken, Password 등

`<Actions Context="Author">` 아래 `<Exec>` 에는 실행할 프로그램이 적힙니다.

- Command: 실행할 프로그램 경로
- Arguments: 인자

Principal 의 id 값과 Actions 의 Context 값에는 같은 이름(Author)이 들어 있었습니다. (확인 범위: Win11 25H2 한 대)

### Triggers 와 Settings

트리거 요소의 예는 다음과 같습니다. (확인 범위: Win11 25H2 한 대)

- LogonTrigger: 사용자가 로그온할 때 실행합니다.
- CalendarTrigger: 날짜와 시각으로 실행합니다. 안에 StartBoundary(시작 시각), Repetition\Interval(반복 간격), ScheduleByDay\DaysInterval(며칠마다)이 들어갑니다.

간격과 기간은 ISO 8601 기간 표기로 적습니다. `PT1H` 는 1시간, `PT72H` 는 72시간, `P3D` 는 3일입니다.

Settings 에는 Enabled, Hidden, ExecutionTimeLimit, MultipleInstancesPolicy, StartWhenAvailable, Priority 같은 요소가 들어갑니다. Hidden 의 기본값은 false 입니다. true 이면 작업 스케줄러 화면에 기본으로 보이지 않습니다. 관리자는 숨긴 작업을 모두 보이게 하는 스위치로 이 작업을 다시 볼 수 있습니다. 이 설정은 레지스트리 SD 값을 지워 숨기는 기법과 다릅니다. 차이는 [숨긴 예약 작업 찾기 (SD 값 삭제)](sd.md)에서 다룹니다.

### 예시

아래는 구조를 보여 주려고 스키마 요소로 만든 예시입니다. 실제 검체에서 나온 파일이 아닙니다.

```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2024-03-05T19:20:30.1234567</Date>
    <Author>EXAMPLE\user1</Author>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <Repetition>
        <Interval>PT1H</Interval>
      </Repetition>
      <StartBoundary>2024-03-05T19:30:00</StartBoundary>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>EXAMPLE\user1</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <Hidden>false</Hidden>
    <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>C:\Users\Public\example.exe</Command>
      <Arguments>/silent</Arguments>
    </Exec>
  </Actions>
</Task>
```

이 예시는 `C:\Users\Public\example.exe /silent` 를 2024-03-05 19:30 부터 하루 간격으로 시작해 1시간마다 되풀이해 실행하라는 뜻입니다. 실행 계정은 `EXAMPLE\user1` 이고, 권한은 낮은 쪽(LeastPrivilege)입니다.

## 증거로서 의미

**증명하는 것**

- 파일이 있으면 그 경로와 이름으로 작업 정의가 디스크에 있었습니다.
- Command 와 Arguments 는 작업이 실행하도록 설정된 프로그램과 인자를 보여 줍니다.
- Principals 는 실행하도록 설정된 계정과 권한 수준을 보여 줍니다.
- LogonType 이 Password 이면 실행 계정의 비밀번호가 자격 증명 관리자 (Credential Manager) 에 저장됩니다. Microsoft 문서는 관리자 권한으로 이 비밀번호를 꺼낼 수 있다고 적었습니다.
- 작업 경로가 루트(`\이름` 꼴)이면 눈여겨봅니다. Microsoft 는 사람이 손으로 만들었거나 악성코드가 만든 작업이 루트에 있는 경우가 많다고 적었습니다.

**증명하지 못하는 것**

- 작업이 실제로 실행됐는지는 XML 에 없습니다. 마지막 실행 시각은 레지스트리 DynamicInfo 값에서 봅니다. [작업 캐시 레지스트리](taskcache-tree-tasks.md)를 봅니다.
- 파일이 있다고 해서 등록된 작업이라는 뜻은 아닙니다. 한 PC 에서는 XML 파일 두 개(`\Microsoft\Windows\PI\SecureBootEncodeUEFI`, `\Microsoft\Windows\Security\Pwdless\IntelligentPwdlessTask`)가 TaskCache 에 항목이 없었습니다. 두 작업은 Get-ScheduledTask 결과에도 나오지 않았습니다. (확인 범위: Win11 25H2 한 대)
- 누가 만들었는지 확정하지 못합니다. Author 는 문자열 칸입니다. Date 는 작업을 만든 쪽이 적어 넣은 값일 수 있습니다(아래 "시각 해석").
- Hidden 이 false 여도 숨긴 작업일 수 있습니다. 레지스트리 SD 값을 지워 숨기는 방법이 따로 있습니다.

보고서에는 기록이 말하는 만큼만 씁니다. 예를 들면 "`\ExampleUpdater` 작업 정의 파일에 `C:\Users\Public\example.exe` 를 1시간마다 실행하도록 적혀 있다. 이 파일만으로는 실제로 실행되었는지 알 수 없다." 처럼 씁니다.

## 시각 해석

**RegistrationInfo\Date**

- 스키마 문서는 Date 를 "작업이 등록된 날짜와 시각" 이라고 적습니다.
- Microsoft 의 4698 문서 예시에서 Task Content 의 Date 는 `2015-09-22T19:03:06.9258653` 입니다. 시간대 표시가 없습니다.
- 같은 이벤트의 기록 시각(TimeCreated)은 `2015-09-23T02:03:06.944522200Z` 입니다. 두 값은 7시간 차이입니다.
- 그래서 예시의 Date 는 작업을 만든 컴퓨터의 현지 시각으로 보입니다. 이 판단은 문서 예시의 두 값을 비교해 추론한 것입니다.
- Date 가 없는 파일이 많습니다. 한 PC 의 XML 271개 가운데 Date 가 있는 파일은 30개였습니다. 그중 28개는 시간대 표시가 없었고, 2개는 있었습니다. (확인 범위: Win11 25H2 한 대)
- Date 는 실제 등록 시각과 다를 수 있습니다. 한 PC 에서 어느 제조사 작업의 Date 는 2013-08-09 였습니다. 같은 작업의 레지스트리 등록 시각(DynamicInfo)은 2026-08-30 이었습니다. 작업을 만든 쪽이 XML 에 적어 넣은 값이 그대로 남은 것으로 보입니다. (확인 범위: Win11 25H2 한 대)

**파일 자체의 시각**

- 한 PC 에서 Windows 기본 작업 XML 의 파일 생성 시각은 2026-06-26 18:07:30 (UTC) 에 모여 있었습니다. 같은 PC 의 OS 설치 시각(InstallDate)은 2026-06-26 18:07:41 (UTC) 이었습니다. (확인 범위: Win11 25H2 한 대)
- 기능 업데이트나 재설치 때 파일을 새로 만들면, 파일 생성 시각은 작업을 처음 만든 때를 뜻하지 않습니다. OS 설치 시각은 [시스템 기본 정보](../../system-account/os-version-computer-name-install-date-shutdown-t.md)에서 봅니다.
- 여러 작업에서 XML 파일의 마지막 기록 시각(UTC)이 DynamicInfo 오프셋 4 의 시각과 초 단위까지 같았습니다. 수정한 작업은 파일 생성 시각과는 다르고 마지막 기록 시각과는 같았습니다. 모든 작업이 이렇지는 않았습니다. (확인 범위: Win11 25H2 한 대)

파일 시각을 읽는 법은 [마스터 파일 테이블 ($MFT)](../../filesystem/mft.md)에서 다룹니다.

## 함정과 한계

- **확장자가 없습니다.** 확장자로 거르는 검색이나 수집 규칙은 이 파일을 놓칠 수 있습니다.
- **UTF-16 LE 입니다.** 명령 경로를 ASCII·UTF-8 로만 검색하면 걸리지 않습니다. 키워드 검색은 두 인코딩으로 모두 합니다.
- **파일과 등록 상태가 어긋날 수 있습니다.** 등록되지 않은 XML 이 있을 수 있습니다. 반대로 레지스트리 항목만 남은 작업도 있습니다. 둘을 맞추는 법은 [작업 캐시 레지스트리](taskcache-tree-tasks.md)의 Hash 절을 봅니다.
- **Date 를 그대로 믿지 않습니다.** 없거나, 현지 시각이거나, 만든 쪽이 적은 값일 수 있습니다.
- **파일 시각은 업데이트로 바뀔 수 있습니다.** 기본 작업의 파일 시각은 OS 설치 시각에 모이기 쉽습니다.
- **Hidden 과 SD 삭제는 다릅니다.** 화면에 안 보이는 작업을 찾을 때 두 가지를 모두 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시입니다. 실제 검체에서 뽑은 바이트가 아닙니다. 앞에서 본 XML 선언의 첫 48바이트입니다.

```
00000000  ff fe 3c 00 3f 00 78 00 6d 00 6c 00 20 00 76 00  |..<.?.x.m.l. .v.|
00000010  65 00 72 00 73 00 69 00 6f 00 6e 00 3d 00 22 00  |e.r.s.i.o.n.=.".|
00000020  31 00 2e 00 30 00 22 00 20 00 65 00 6e 00 63 00  |1...0.". .e.n.c.|
```

1. 0x00 의 `ff fe` 는 UTF-16 LE 의 BOM 입니다.
2. 0x02 부터는 글자마다 2바이트입니다. `3c 00` 은 `<`, `3f 00` 은 `?` 입니다.
3. 오른쪽 글자 칸에 `.` 이 한 칸씩 끼어 보이면 UTF-16 LE 문서일 가능성이 큽니다.
4. BOM 은 레지스트리 Hash 를 계산할 때 빼는 부분입니다. 자세한 내용은 [작업 캐시 레지스트리](taskcache-tree-tasks.md)를 봅니다.

### 공개 도구로 한 번

XML 파일은 텍스트 편집기나 XML 뷰어로 열 수 있습니다. 편집기가 인코딩을 UTF-16 으로 읽는지 확인합니다.

폴더를 통째로 훑을 때는 Python 표준 라이브러리로 충분합니다. 아래 코드는 마운트한 이미지의 `Tasks` 폴더 아래 파일마다 주요 요소를 뽑습니다. 파서가 BOM 과 `encoding="UTF-16"` 선언을 보고 인코딩을 알아서 고릅니다.

```python
import os
import xml.etree.ElementTree as ET

NS = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
FIELDS = ["t:RegistrationInfo/t:Date", "t:RegistrationInfo/t:Author",
          "t:Principals/t:Principal/t:UserId", "t:Principals/t:Principal/t:LogonType",
          "t:Settings/t:Hidden", "t:Actions/t:Exec/t:Command", "t:Actions/t:Exec/t:Arguments"]

top = r"E:\mount\Windows\System32\Tasks"   # 마운트한 경로로 바꿉니다
for dirpath, _, names in os.walk(top):
    for name in names:
        path = os.path.join(dirpath, name)
        root = ET.parse(path).getroot()
        print("\\" + os.path.relpath(path, top))          # 작업 경로
        for f in FIELDS:
            e = root.find(f, NS)
            print("   ", f.split("/")[-1][2:], "=", e.text if e is not None else "(없음)")
```

살아 있는 시스템에서는 PowerShell 의 `Get-ScheduledTask` 로 등록된 작업 목록을 볼 수 있습니다. 이 목록과 폴더의 파일 목록을 맞춰 보면 등록되지 않은 XML 이 드러납니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 작업 캐시 레지스트리 | 등록 여부, XML 해시, 마지막 실행 시각 | [작업 캐시 레지스트리](taskcache-tree-tasks.md) |
| 예약 작업 이벤트 | 4698 의 Task Content 필드에 새 작업의 XML 전체가 남습니다. 로그를 켜 두었다면 XML 파일을 지운 뒤에도 내용이 남습니다 | [예약 작업 이벤트](../../event-logs/taskscheduler-4698.md) |
| 자격 증명 관리자 | LogonType 이 Password 인 작업의 저장 비밀번호 | [자격 증명 관리자와 볼트](../../credentials/credential-manager-windows-vault.md) |
| 마스터 파일 테이블 · USN 변경 저널 | XML 파일이 생기고 바뀌고 지워진 흔적 | [$MFT](../../filesystem/mft.md), [$UsnJrnl](../../filesystem/usnjrnl.md) |
| 프리페치 · 프로세스 생성 | Command 의 프로그램이 실제로 실행됐는지 | [프리페치](../../execution/prefetch/index.md), [프로세스 생성 (4688)](../../event-logs/4688.md) |
| 섀도 복사본 | 지금은 없거나 바뀐 옛 XML | [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

## 실습

공개 검체(NIST CFReDS 등)에서 `C:\Windows\System32\Tasks` 폴더와 SOFTWARE 하이브를 꺼내 아래 질문을 풀어 봅니다.

1. 작업 경로가 루트(`\이름` 꼴)인 작업을 모두 찾습니다. 각 작업의 Command 는 무엇입니까?
2. Command 가 `Users` 폴더나 임시 폴더를 가리키는 작업이 있습니까?
3. RegistrationInfo\Date 가 있는 작업은 몇 개입니까? 시간대 표시가 붙은 값이 있습니까?
4. LogonType 이 Password 인 작업이 있습니까? 있다면 실행 계정은 무엇입니까?
5. 레지스트리 TaskCache 에 항목이 없는 XML 파일이 있습니까?

## 참고 문헌

1. Microsoft Security Blog, "Tarrask malware uses scheduled tasks for defense evasion" (2022-04-12). https://www.microsoft.com/en-us/security/blog/2022/04/12/tarrask-malware-uses-scheduled-tasks-for-defense-evasion/
2. Microsoft Learn, "4698(S) A scheduled task was created." https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4698
3. Microsoft Learn, "RegistrationInfo (taskType) Element". https://learn.microsoft.com/en-us/windows/win32/taskschd/taskschedulerschema-registrationinfo-tasktype-element
4. Microsoft Learn, "Hidden (settingsType) Element". https://learn.microsoft.com/en-us/windows/win32/taskschd/taskschedulerschema-hidden-settingstype-element
