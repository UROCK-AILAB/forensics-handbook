---
title: "윈도 업데이트 기록"
parent: "아티팩트 · 시스템·계정"
nav_order: 680
---

# 윈도 업데이트 기록 (Windows Update·CBS Log)

> 이 페이지의 실제 위치·개수·예시 값은 Windows 11 25H2(빌드 26200.9457), 한국 표준시(UTC+9) 기준입니다. 다른 버전에서는 실제 기기에서 확인합니다.

## 한 줄 요약

윈도 업데이트 기록은 한 파일이 아니라 여러 곳에 나뉘어 남습니다. 설치된 업데이트 목록과 설치 시각은 SOFTWARE 하이브의 Component Based Servicing 키에 남고, 설치 과정은 이벤트 로그·CBS.log·ETL 로그·ReportingEvents.log 에 남습니다. 기록마다 시각 기준(UTC·현지 시각)이 달라서 섞어 쓰면 시간대만큼 어긋납니다.

## 무엇을 기록하나 · 왜 생기나

업데이트는 여러 구성 요소가 나눠 처리하고, 구성 요소마다 로그를 따로 씁니다.

| 구성 요소·기록 | 하는 일 | 남기는 기록 |
|---|---|---|
| Windows Update 클라이언트 | 업데이트를 찾고 내려받습니다 | ETL 진단 로그. Windows 8.1 부터 ETW (Event Tracing for Windows) 로 만듭니다 |
| 업데이트 오케스트레이터 (Update Orchestrator) 서비스 | 내려받기·설치 순서를 맡습니다. Windows 10 부터 있습니다 | USO 로그(.etl) |
| 서비싱 스택 (servicing stack) | 업데이트를 실제로 설치합니다 | CBS.log |
| 설치가 끝난 패키지 | — | Component Based Servicing 레지스트리 키, `servicing\Packages` 의 .mum 파일 |
| Windows Update 이벤트 | 설치 시작·성공·실패 | System 로그, Setup 로그, WindowsUpdateClient/Operational 로그 |

이 기록으로 아래 질문에 답합니다.

- 어느 시점에 어떤 누적 업데이트까지 설치돼 있었나
- 어떤 업데이트를 언제 설치했고, 성공했나 실패했나
- 어떤 프로그램이 Windows Update 를 불렀나
- OS 를 언제 새로 설치했나 (다른 기록과 함께)

## 위치와 버전별 차이

로그 파일은 아래와 같습니다[1].

| 파일 | 위치 | 버전 | 담긴 것 |
|---|---|---|---|
| windowsupdate.log | `C:\Windows\Logs\WindowsUpdate` | Windows 8.1 부터 ETW(.etl)로 만듭니다 | Windows Update 클라이언트의 진단 기록 |
| UpdateSessionOrchestration.etl | `C:\ProgramData\USOShared\Logs` | Windows 10 부터 | 오케스트레이터 서비스의 이벤트 |
| NotificationUxBroker.etl | `C:\ProgramData\USOShared\Logs` | Windows 10 부터 | 알림 표시 기록 |
| CBS.log | `%systemroot%\Logs\CBS` | — | 서비싱 스택이 업데이트를 설치한 과정 |

Windows Update 는 이제 WindowsUpdate.log 를 직접 만들지 않고 바로 읽을 수 없는 .etl 파일을 만들기 때문에, 읽을 수 있는 WindowsUpdate.log 는 PowerShell `Get-WindowsUpdateLog` 로 .etl 을 풀어서 만듭니다[2]. Windows 8.1 이전의 텍스트 로그 위치와 CBS.log 가 처음 생긴 Windows 버전은 실제 기기에서 확인해야 합니다.

Windows 11 25H2 의 실제 위치는 아래와 같습니다.

| 위치 | 있던 것 |
|---|---|
| `C:\Windows\Logs\WindowsUpdate\` | `WindowsUpdate.YYYYMMDD.HHMMSS.mmm.N.etl` 77개. 7일치(가장 오래된 것 2026-09-16) |
| `C:\ProgramData\USOShared\Logs\System\` | `UpdateSessionOrchestration.*.etl` 29개, `MoUxCoreWorker.*.etl` 30개 |
| `C:\ProgramData\USOShared\Logs\User\` | `UpdateUx.*.etl` |
| `C:\Windows\Logs\CBS\` | CBS.log(12.5MB), `CbsPersist_YYYYMMDDhhmmss.cab` 2개, 압축하지 않은 `CbsPersist_YYYYMMDDhhmmss.log` 1개(142MB), FilterList.log, container.etl |
| `C:\Windows\SoftwareDistribution\` | DataStore\, Download\, PostRebootEventCache.V2\, SLS\ 폴더와 ReportingEvents.log |
| `C:\Windows\SoftwareDistribution\DataStore\` | DataStore.edb(33.8MB), DataStore.jfm, Logs\ |
| `C:\Windows\servicing\Packages\` | .mum 파일 6,680개 |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\Packages` | 패키지 키 6,680개 |
| 이벤트 로그 | System, Setup, `Microsoft-Windows-WindowsUpdateClient/Operational` |

Windows 11 25H2 에서는 USO 로그가 `Logs\` 바로 아래가 아니라 `System\`, `User\` 하위 폴더에 있고, NotificationUxBroker.etl 이 없을 수 있습니다. 두 가지 모두 위의 로그 파일 표[1]와 다르므로 `USOShared\Logs` 아래를 통째로 수집합니다.

## 구조

### WindowsUpdate.log 한 줄

`Get-WindowsUpdateLog` 로 푼 WindowsUpdate.log 의 한 줄은 네 부분으로 나뉩니다.

| 부분 | 내용 |
|---|---|
| 시각 | 그 줄을 기록한 시각 |
| 프로세스 ID·스레드 ID | 앞 4자리(16진)가 프로세스 ID, 다음 4자리(16진)가 스레드 ID 입니다. 값은 무작위라서 로그마다, 서비스 세션마다 달라집니다 |
| 구성 요소 이름 | AGENT, AU, AUCLNT, COMAPI, DRIVER, DTASTOR, HANDLER, PT, REPORT, SERVICE, SETUP, ProtocolTalker, DownloadManager, EEHandler, DataStore, IdleTimer 등 |
| 업데이트 식별자 | 아래 표의 ID 들 |

- 줄은 대개 시간 순서입니다. 다만 예외가 있습니다.

업데이트를 가리키는 번호는 네 가지입니다.

| 식별자 | 누가 매기나 | 특징 |
|---|---|---|
| 업데이트 ID (update ID) | 게시할 때 붙습니다 | GUID 입니다 |
| 개정 번호 (revision number) | 업데이트를 고쳐 다시 게시할 때마다 올라갑니다 | 업데이트 ID 와 함께 `{GUID}.revision` 처럼 씁니다. 다른 업데이트에서도 같은 번호를 쓰므로 번호만으로는 업데이트를 구분하지 못합니다 |
| 개정 ID (revision ID) | 업데이트를 처음 게시하거나 고칠 때 원본(Windows Update, WSUS)마다 따로 매기는 일련번호입니다 | 원본이 다르면 같은 번호가 다른 업데이트일 수 있습니다 |
| 로컬 ID (local ID) | 그 PC 의 Windows Update 클라이언트가 매깁니다 | PC 마다 다릅니다. `%WINDIR%\SoftwareDistribution\Datastore\Datastore.edb` 에서 확인합니다 |

### CBS.log

한 줄은 날짜 시각, 수준, 구성 요소, 내용 순서입니다.

```
YYYY-MM-DD hh:mm:ss, Info                  CBS    <내용>
```

- 줄의 시각은 시간대 표시가 없는 현지 시각입니다. 마지막 줄의 시각은 파일 수정 시각(+0900)과 같습니다.
- TrustedInstaller 가 시작할 때마다 `TI: --- Initializing Trusted Installer ---` 줄이 찍히고, 바로 이어서 `TI: Last boot time: <시각>` 줄이 찍힙니다. 두 줄을 세션 경계로 씁니다.
- `Loaded Servicing Stack v<버전> with Core: C:\WINDOWS\winsxs\...` 줄에 서비싱 스택 버전이 나옵니다.
- 패키지는 `Package_for_KB5054156~31bf3856ad364e35~amd64~~26100.6717.1.4` 같은 이름으로 나옵니다.
- 이 이름은 `~` 로 나뉘며, 순서는 이름, 공개 키 토큰, 아키텍처, 언어, 버전입니다.

로그가 넘겨지면 옛 로그는 `CbsPersist_` 파일로 바뀝니다. 파일 이름의 시각은 UTC 이고 새 CBS.log 가 시작한 시각이며, 파일 수정 시각은 그 로그의 마지막 기록 시각에 가깝습니다.

- 예를 들어 `CbsPersist_20260920234451.log` 의 이름 시각(23:44:51 UTC)은 새 CBS.log 첫 줄 시각(현지 2026-09-21 08:44:51)과 정확히 9시간 차이 납니다. .cab 파일도 같은 관계입니다.
- 옛 로그가 늘 .cab 으로 눌려 있지는 않습니다. 압축하지 않은 .log 로 남기도 합니다.
- CBS.log 를 넘기는 크기와 옛 로그를 남기는 개수는 실제 기기에서 확인해야 합니다.

### ReportingEvents.log

`C:\Windows\SoftwareDistribution\ReportingEvents.log` 는 UTF-16LE 텍스트입니다. 파일 앞에 BOM `FF FE` 가 있고, 필드는 탭으로 나눕니다.

필드 순서는 아래와 같습니다. 공식 필드 이름은 공개돼 있지 않아, 표의 필드 이름은 내용을 보고 붙인 것입니다.

| 순서 | 내용 | 예 |
|---|---|---|
| 1 | 이벤트 GUID | — |
| 2 | 시각 | `2026-08-30 00:31:01:965+0900` (시간대 오프셋 포함) |
| 3 | 숫자 | — |
| 4 | 이벤트 코드와 이름 | `147 [AGENT_DETECTION_FINISHED]` |
| 5 | 숫자 | — |
| 6 | 업데이트 서비스 GUID | — |
| 7·8 | 0, 0 | — |
| 9 | 호출한 프로세스 | `<<PROCESS>>: xxx.exe`, `MoUpdateOrchestrator` |
| 10 | 결과 | Success |
| 11 | 범주 | Software Synchronization |
| 12 | 설명 문장 | — |

- 호출한 프로세스 필드에는 제3자 업데이트 도구의 실행 파일 이름도 찍힙니다. 어떤 프로그램이 Windows Update 를 불렀는지 이 필드에서 보입니다.
- 1,264줄, 약 3주 반치(가장 오래된 줄 2026-08-30)만 남은 경우가 있습니다. 앞부분이 잘려 나가는 것으로 보이며, 잘리는 기준을 설명한 공개 문서는 없습니다.
- 이 파일이 모든 Windows 버전에 있는지는 실제 기기에서 확인합니다.

### DataStore.edb

- `SoftwareDistribution\DataStore\DataStore.edb` 는 ESE DB 입니다. 옆의 `Logs\` 폴더에 edb.chk, edb.log, `edb0029C.log` 같은 세대 로그, edbres00001.jrs, edbres00002.jrs, edbtmp.log 가 있습니다.
- 로그 이름은 옛 형식(.log·.chk)입니다. Windows 10 이후 Windows Search 는 로그를 .jtx, 체크포인트를 .jcp 로 쓰는 등 DB 마다 이름 규칙이 다르므로 복구할 때 확인합니다.
- ESE 의 구조와 복구는 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다.

### Component Based Servicing 레지스트리

`HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\Packages\<패키지 이름>` 에 서비싱 패키지마다 키가 하나 있습니다. 키 개수는 `C:\Windows\servicing\Packages\*.mum` 파일 개수와 같습니다(예: 둘 다 6,680개).

| 값 | 내용 |
|---|---|
| `InstallClient` | 설치를 맡은 주체. 예: UpdateAgentLCU, DISM Package Manager Provider |
| `InstallName` | .mum 파일 이름 |
| `InstallLocation` | 원본 .cab 경로. 예: `\\?\C:\WINDOWS\SoftwareDistribution\Download\<해시>\Windows11.0-KB5095189-x64.cab` |
| `CurrentState` | 상태 숫자 |
| `InstallTimeHigh`, `InstallTimeLow` | 합치면 64비트 FILETIME(UTC) |
| `InstallUser` | S-1-5-18 |
| `SelfUpdate`, `Visibility` | 공개 자료 없음 |

패키지 이름으로 업데이트 종류를 나눕니다.

- 월간 누적 업데이트는 `Package_for_KB…` 가 아니라 `Package_for_RollupFix~31bf3856ad364e35~amd64~~26100.<UBR>.x.y` 로 남습니다.
- 현재 RollupFix 항목의 버전(예: 26100.9457)은 `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion` 의 `UBR`(예: 9457)과 같습니다.
- `Package_for_KB…` 이름의 키는 몇 개뿐입니다(예: 6,680개 가운데 2개).
- `Package_for_ServicingStack_…`, `Package_for_DotNetRollup_…` 키도 있습니다.

`CurrentState` 값은 세 가지가 나옵니다. 숫자마다의 공식 뜻을 설명한 공개 문서는 없습니다.

| 값 | 개수 | 비고 |
|---|---|---|
| 112 (0x70) | 2,290 | 현재 누적 업데이트 |
| 80 (0x50) | 1,280 | 그 전 누적 업데이트들 |
| 64 (0x40) | 3,110 | — |

하이브의 구조는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

### 이벤트 로그

아래 이벤트 ID 와 필드는 공식 문서에 설명이 없으므로 실제 이벤트로 확인합니다.

**System 로그, 공급자 `Microsoft-Windows-WindowsUpdateClient`**

| ID | 메시지 | 알려 주는 것 |
|---|---|---|
| 19 | Installation Successful: Windows successfully installed the following update: <제목> | 설치 성공 |
| 20 | Installation Failure: Windows failed to install the following update with error 0x…: <제목> | 설치 실패와 오류 코드 |
| 43 | Installation Started: Windows has started installing the following update: <제목> | 설치 시작 |
| 44 | Windows Update started downloading an update. | 내려받기 시작 |

- 이벤트 19 의 EventData 필드는 `updateTitle`, `updateGuid`, `updateRevisionNumber`, `serviceGuid` 입니다.
- `updateGuid`·`updateRevisionNumber` 는 위의 업데이트 ID·개정 번호와 같은 뜻으로 보입니다.
- 업데이트 제목은 설치 언어로 적힙니다. 한국어 PC 에서는 한국어 제목입니다.

**`Microsoft-Windows-WindowsUpdateClient/Operational` 로그**

| ID | 메시지 |
|---|---|
| 25 | Windows Update failed to check for updates with error 0x… |
| 26 | Windows Update successfully found N updates. |
| 41 | An update was downloaded. |

**Setup 로그, 공급자 `Microsoft-Windows-Servicing`**

| ID | 메시지·뜻 |
|---|---|
| 1 | Initiating changes for package KBxxxxxxx. Current state is <상태>. Target state is <상태>. Client id: <클라이언트>. |
| 2 | Package KBxxxxxxx was successfully changed to the <상태> state. |
| 4 | A reboot is necessary before package <이름> can be changed to the Installed state. |
| 7·8 | 선택 기능 (selectable update) 켜기·끄기 시작. Client id 가 들어갑니다(예: DISM Package Manager Provider) |
| 9·10 | 선택 기능 켜기·끄기 성공 |
| 13 | 선택 기능을 켜기 전에 재부팅 필요 |

- 상태 이름으로 Superseded, Absent, Installed 가 나옵니다.
- OS 를 새로 설치한 지 석 달쯤 된 PC 에서는 세 로그 모두 OS 설치 날부터 남아 있을 수 있습니다. 오래 쓴 PC 에서 얼마나 남는지는 실제 기기에서 확인합니다.

이벤트 로그와 ETL 파일의 구조는 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

- Component Based Servicing 키가 있으면 수집 시점에 그 서비싱 패키지가 이 PC 에 등록돼 있었습니다.
- `InstallTimeHigh`·`InstallTimeLow` 는 그 패키지를 설치한 시각으로 읽습니다. OS 설치 때 들어간 패키지의 이 값은 OS 설치 시각과 몇 분 차이 납니다(예: 3분).
- RollupFix 항목의 버전이 `UBR` 과 같으면 그 항목이 현재 누적 업데이트 수준입니다.
- `InstallClient` 와 Setup 로그의 Client id 는 설치를 맡은 주체를 알려 줍니다. 이 값으로 Windows Update 에이전트(UpdateAgentLCU)와 DISM(DISM Package Manager Provider)을 나눌 수 있습니다.
- 이벤트 19·20·43 은 어떤 제목의 업데이트를 언제 설치 시작·성공·실패했는지 알려 줍니다.
- ReportingEvents.log 의 호출한 프로세스 필드로 어떤 프로그램이 Windows Update 를 불렀는지 알 수 있습니다.

### 증명하지 못하는 것

- 사람이 직접 설치를 눌렀는지는 알 수 없습니다. `InstallUser` 는 S-1-5-18(SYSTEM)로 남습니다.
- `CurrentState` 숫자의 공식 뜻을 설명한 공개 문서는 없습니다. "112 는 설치 완료" 처럼 단정하지 않습니다.
- `Get-HotFix` 의 날짜만으로는 설치 시각을 말할 수 없습니다. `InstalledOn` 은 날짜만 있고 시각은 00:00:00 입니다.
- 설치 성공 이벤트가 있어도 재부팅까지 끝났는지는 따로 봅니다. Setup 로그 이벤트 4 는 재부팅 전에는 Installed 상태로 바꿀 수 없다고 적습니다.
- 로그에 없다고 업데이트가 없었던 것은 아닙니다. ETL·ReportingEvents.log·CBS.log 는 앞부분이 밀려납니다.
- 그 시각에 누가 PC 앞에 있었는지는 알 수 없습니다.

보고서에는 "SOFTWARE 하이브의 Component Based Servicing\Packages 에 `Package_for_RollupFix~…~26100.<UBR>…` 항목이 있고, InstallTimeHigh·Low 를 합친 값은 <UTC 시각> 이다. System 로그의 이벤트 19 에 같은 업데이트 제목의 설치 성공 기록이 <UTC 시각> 으로 남아 있다" 처럼 씁니다.

## 시각 해석

기록마다 시각 기준이 다릅니다. 여러 기록을 한 줄로 세우기 전에 이 표부터 봅니다.

| 기록 | 시각 기준 |
|---|---|
| CBS.log 안의 줄 시각 | 현지 시각, 시간대 표시 없음 |
| `CbsPersist_` 파일 이름 | UTC |
| `WindowsUpdate.*.etl` 파일 이름 | 현지 시각 |
| ReportingEvents.log | 현지 시각 + 오프셋(`+0900`) |
| 이벤트 로그 TimeCreated | UTC(`Z`) |
| Component Based Servicing 키의 `InstallTimeHigh`·`InstallTimeLow` | FILETIME, UTC |
| `Get-HotFix` 의 `InstalledOn` | 날짜만 |

- CBS.log 안은 현지 시각이고 `CbsPersist_` 파일 이름은 UTC 이므로, 한국 표준시 PC 에서 둘을 섞어 쓰면 9시간 어긋납니다.
- ETL 파일 이름의 시각은 현지 시각입니다. 예를 들어 이름이 16:58:24 인 파일의 수정 시각은 현지 17:08 입니다.
- `InstallTimeHigh`·`InstallTimeLow` 는 64비트 값의 위 32비트와 아래 32비트이며, 합쳐서 FILETIME 으로 읽습니다.
- 예를 들어 OS 설치 시각(`InstallDate`)이 2026-06-26 18:07:41 UTC 인 PC 에서, OS 설치 때 들어간 패키지의 설치 시각은 18:10:32 UTC 입니다. OS 설치 시각은 [시스템 기본 정보](os-version-computer-name-install-date-shutdown-t.md) 에서 다룹니다.
- 설치 시각이 0(1601-01-01)인 RollupFix 항목도 있습니다. 이 값은 설치 시각으로 쓰지 않습니다.
- 현지 시각 기록을 UTC 로 바꿀 때는 분석 대상 PC 의 시간대 설정을 먼저 확인합니다. [시간대 설정](time-zone.md) 에서 다룹니다.
- FILETIME 변환은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

## 함정과 한계

1. **시각 기준이 섞여 있습니다.** 위 표대로 기록마다 기준을 적고 나서 시간순으로 합칩니다.
2. **.etl 은 바로 읽을 수 없습니다.** `Get-WindowsUpdateLog` 로 풉니다. 이때 로그를 만든 Windows 세대와 푸는 PC 의 세대가 맞아야 합니다.
   - Windows 10 1709(빌드 16299) 이전 로그는 Microsoft 심볼 서버에 접속해야 풀립니다. 1709 이전 Windows 10 에서 풀어야 합니다.
   - 1709 부터의 로그는 심볼 서버가 필요 없습니다. Windows 10 1709 이상에서 풀어야 합니다.
3. **푼 결과는 그때의 사본입니다.** `Get-WindowsUpdateLog` 로 만든 WindowsUpdate.log 는 새 내용을 따라가지 않습니다. 다시 실행해야 새 내용이 들어갑니다.
4. **조사 대상 PC 에서 돌리면 파일이 생깁니다.** 기본 출력은 현재 사용자 바탕 화면의 WindowsUpdate.log 입니다. 중간 파일은 `$env:TEMP\WindowsUpdateLog` 에 만듭니다.
5. **`-ForceFlush` 는 서비스를 멈춥니다.** 추적 내용을 .etl 로 강제로 내보내면서 업데이트 오케스트레이터와 Windows Update 서비스를 멈춥니다. 관리자 권한이 필요합니다. 라이브 시스템에서는 쓰기 전에 기록을 남깁니다. [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) 에서 다룹니다.
6. **문서와 실제 위치가 다를 수 있습니다.** Windows 11 25H2 에서 USO 로그는 하위 폴더에 있고 NotificationUxBroker.etl 은 없을 수 있습니다.
7. **로그가 짧게 남습니다.** ETL 은 7일치, ReportingEvents.log 는 약 3주 반치만 남은 경우가 있습니다.
8. **옛 CBS 로그는 .cab 과 .log 둘 다 있을 수 있습니다.** `Logs\CBS\` 폴더를 통째로 수집합니다.
9. **KB 번호로만 찾으면 월간 누적 업데이트를 놓칩니다.** 누적 업데이트는 `Package_for_RollupFix` 로 남고, `Package_for_KB…` 키는 몇 개뿐입니다.
10. **설치 시각이 0 인 항목이 있습니다.** 1601-01-01 로 보이면 값이 비어 있는 것으로 봅니다.
11. **`CurrentState` 숫자의 공식 뜻은 공개돼 있지 않습니다.** 값과 개수만 적습니다.
12. **이벤트 제목은 설치 언어로 적힙니다.** 영어 제목으로 검색하면 한국어 PC 의 기록을 놓칩니다. `updateGuid` 로 찾습니다.
13. **스토어 앱 업데이트 실패도 이벤트 20 에 섞여 남습니다.** 제목이 스토어 상품 ID 로 시작하면 OS 업데이트가 아닙니다. [스토어 앱 설치 목록](appx-staterepository.md) 에서 다룹니다.
14. **개정 ID 는 원본마다 따로 매깁니다.** WSUS 를 쓰는 PC 와 Windows Update 를 쓰는 PC 에서 같은 번호가 다른 업데이트일 수 있습니다.
15. **DataStore.edb 는 ESE DB 입니다.** 같은 ESE 형식이라 비정상 종료·끊긴 로그 사슬·손상 문제가 생길 수 있습니다. 자세한 내용은 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 값은 명세로 만든 예시입니다. 실제 기기에서 꺼낸 값이 아닙니다.

**InstallTimeHigh·Low 합치기.** 레지스트리 뷰어에 두 값이 아래처럼 보인다고 해 봅니다.

```
InstallTimeHigh = 0x01DA3C45   (10진수 31,079,493)
InstallTimeLow  = 0x7689C000   (10진수 1,988,739,072)
```

1. High 를 위 32비트, Low 를 아래 32비트로 붙입니다. `0x01DA3C457689C000` 입니다.
2. 10진수로 바꾸면 133,485,408,000,000,000 입니다.
3. 10,000,000 으로 나누면 13,348,540,800 입니다. 1601-01-01 부터 센 초입니다.
4. 11,644,473,600 을 빼면 1,704,067,200 입니다. 1970-01-01 부터 센 초입니다.
5. 날짜로 바꾸면 2024-01-01 00:00:00 UTC 입니다.

**CbsPersist 이름을 현지 시각으로 바꾸기.** 파일 이름이 `CbsPersist_20240101000000.log` 라고 해 봅니다.

1. 이름의 시각은 UTC 2024-01-01 00:00:00 입니다.
2. UTC+9 PC 에서는 현지 2024-01-01 09:00:00 입니다.
3. 그 뒤에 시작한 새 CBS.log 첫 줄은 이 현지 시각 근처로 찍힙니다.

**ReportingEvents.log 바이트.** 파일 맨 앞 2바이트는 BOM 입니다. 그 뒤 글자는 한 글자에 2바이트씩 이어집니다. 예를 들어 시각 필드의 `2024` 와 필드를 나누는 탭은 아래처럼 보입니다.

```
FF FE                       BOM (UTF-16LE, 파일 맨 앞)
32 00 30 00 32 00 34 00     2 0 2 4
09 00                       탭
```

인코딩은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.

### 공개 도구로 한 번

1. 아래를 사본으로 뜹니다.
   - `C:\Windows\Logs\WindowsUpdate\` 의 .etl 전부
   - `C:\ProgramData\USOShared\Logs\` 아래 전부
   - `C:\Windows\Logs\CBS\` 전부
   - `C:\Windows\SoftwareDistribution\ReportingEvents.log`
   - `C:\Windows\SoftwareDistribution\DataStore\` 폴더 전체(`Logs\` 포함)
   - SOFTWARE 하이브와 하이브 로그
   - System, Setup, `Microsoft-Windows-WindowsUpdateClient/Operational` 이벤트 로그
2. 분석 PC 에서 복사해 온 .etl 을 풉니다. `-ETLPath` 에는 폴더, .etl 파일 한 개, 쉼표로 나눈 여러 파일을 줄 수 있습니다. 로그를 만든 Windows 세대와 맞는 분석 PC 에서 실행합니다.

```powershell
Get-WindowsUpdateLog -ETLPath D:\case\WindowsUpdate -LogPath D:\case\out\WindowsUpdate.log
```

3. USO·UX 로그까지 풀려면 `-IncludeAllLogs` 를 붙입니다. 이때는 바탕 화면 폴더에 WindowsUpdate.log, USO.log, UX.log 를 씁니다.
4. 이벤트 뷰어나 공개 EVTX 파서로 System 로그를 엽니다. `Microsoft-Windows-WindowsUpdateClient` 의 19·20·43·44 를 거릅니다. Setup 로그에서는 `Microsoft-Windows-Servicing` 의 1·2·4 를 거릅니다.
5. 레지스트리 뷰어로 SOFTWARE 하이브의 `Microsoft\Windows\CurrentVersion\Component Based Servicing\Packages` 를 엽니다. `Package_for_RollupFix` 키를 찾아 `InstallTimeHigh`·`InstallTimeLow` 를 위 헥스 풀이대로 합쳐 봅니다.
6. 텍스트 편집기로 CBS.log 를 열고 `Initializing Trusted Installer` 줄을 찾습니다. 세션마다 무엇을 설치했는지 봅니다.
7. ReportingEvents.log 는 UTF-16LE, 탭 구분으로 스프레드시트에 불러옵니다. 호출한 프로세스 열을 기준으로 정렬합니다.
8. 한 업데이트를 골라 레지스트리 설치 시각, 이벤트 19 시각, CBS.log 줄 시각을 UTC 로 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 시스템 기본 정보 | OS 설치 시각과 `UBR` 을 업데이트 기록과 맞춰 봅니다 | [시스템 기본 정보](os-version-computer-name-install-date-shutdown-t.md) |
| 시간대 설정 | 현지 시각 기록을 UTC 로 바꿀 때 씁니다 | [시간대 설정](time-zone.md) |
| 스토어 앱 설치 목록 | 이벤트 20 의 스토어 앱 업데이트 실패를 AppX 기록과 맞춰 봅니다 | [스토어 앱 설치 목록](appx-staterepository.md) |
| 설치 프로그램 | 같은 시기에 설치한 일반 프로그램을 봅니다 | [설치 프로그램](uninstall.md) |
| 켜짐·꺼짐 | CBS.log 의 `Last boot time` 과 재부팅 기록을 맞춰 봅니다 | [켜짐·꺼짐](../event-logs/power-on-off-events.md) |
| 초기 침입 조사 | 침입 시점에 어떤 누적 업데이트까지 설치돼 있었는지 봅니다 | [악성코드는 어디서 들어왔나](../../04-scenarios/incident/initial-access.md) |
| 초기화·재설치 흔적 | OS 설치 때 들어간 패키지 시각과 OS 설치 시각을 함께 봅니다 | [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) |

여러 기록의 시각을 시간순으로 합치는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

## 실습

Windows 공개 시험 이미지(NIST CFReDS 등)에서 SOFTWARE 하이브, `Logs\CBS\`, `SoftwareDistribution\`, System·Setup 이벤트 로그를 꺼내 아래 질문을 풀어 봅니다.

1. 이미지의 `UBR` 은 얼마입니까? 같은 버전의 `Package_for_RollupFix` 키가 있습니까?
2. 그 RollupFix 키의 `InstallTimeHigh`·`InstallTimeLow` 를 직접 합쳐 UTC 로 바꿔 봅니다. 도구가 보여 주는 값과 같습니까?
3. System 로그 이벤트 19 가운데 같은 업데이트의 설치 성공 기록은 언제입니까? 레지스트리 시각과 얼마나 차이 납니까?
4. `CbsPersist_` 파일 이름의 시각과, 그 뒤 새 CBS.log 첫 줄의 시각은 몇 시간 차이 납니까? 이미지의 시간대와 맞습니까?
5. ReportingEvents.log 의 호출한 프로세스 필드에 Windows 기본 구성 요소가 아닌 실행 파일이 있습니까?
6. `Get-WindowsUpdateLog` 로 이미지에서 꺼낸 .etl 을 풀어 봅니다. 그 Windows 세대에 맞는 분석 PC 를 썼습니까?
7. 이벤트 20 가운데 제목이 스토어 상품 ID 로 시작하는 기록이 있습니까?

## 참고 문헌

1. Microsoft Learn, *Windows Update log files* (로그 파일 위치와 버전, WindowsUpdate.log 한 줄의 구성, 구성 요소 이름, 업데이트 ID·개정 번호·개정 ID·로컬 ID). https://learn.microsoft.com/en-us/windows/deployment/update/windows-update-logs
2. Microsoft Learn, *Get-WindowsUpdateLog (WindowsUpdate)* (.etl 을 WindowsUpdate.log 로 푸는 방법, 1709 전후 조건, `-ETLPath`·`-LogPath`·`-IncludeAllLogs`·`-ForceFlush`, 중간 파일 위치). https://learn.microsoft.com/en-us/powershell/module/windowsupdate/get-windowsupdatelog
