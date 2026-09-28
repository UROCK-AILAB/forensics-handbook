---
title: "카메라·마이크 사용 기록"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 1120
---

# 카메라·마이크 사용 기록 (CapabilityAccessManager)

Windows 는 앱이 카메라·마이크를 쓴 때를 레지스트리의 ConsentStore 키에 남깁니다. 앱마다 마지막으로 쓰기 시작한 시각 (LastUsedTimeStart) 과 멈춘 시각 (LastUsedTimeStop) 이 FILETIME 으로 남습니다. `C:\ProgramData\Microsoft\Windows\CapabilityAccessManager` 에는 사용 기록 표가 든 SQLite DB 도 있습니다.

## 무엇을 기록하나 · 왜 생기나

Windows 설정의 개인 정보 화면에서 앱의 카메라·마이크 사용을 허용하거나 막습니다. 카메라에 표시등이 있으면 카메라가 켜질 때 불이 들어오고, 표시등이 없으면 Windows 가 카메라가 켜지고 꺼질 때 알림을 띄웁니다. 앱이 마이크를 쓰면 작업 표시줄 알림 영역에 마이크 아이콘이 뜹니다. 스토어 앱은 앱마다 켜고 끌 수 있지만 데스크톱 앱은 하나씩 끌 수 없고 스위치 하나로 한꺼번에 관리합니다. 카메라·마이크를 쓴 데스크톱 앱은 설정 화면 목록에 나오며, 앱을 누르면 카메라나 마이크에 접근한 파일의 세부 정보를 볼 수 있습니다[1].

레지스트리에는 권한마다 키가 있고, 그 아래에 앱마다 하위 키가 생깁니다. 앱 하위 키에는 그 앱이 장치를 쓰기 시작한 시각과 멈춘 시각이 남습니다. 카메라는 `webcam` 키, 마이크는 `microphone` 키입니다.

ConsentStore 에는 카메라·마이크 말고도 권한 키가 여럿 있습니다. Windows 11 25H2(빌드 26200)에는 다음 35개가 있습니다.

```
appDiagnostics, appointments, bluetooth, bluetoothSync, broadFileSystemAccess,
cellularData, chat, contacts, documentsLibrary, email, gazeInput,
graphicsCaptureProgrammatic, graphicsCaptureWithoutBorder, humanInterfaceDevice,
humanPresence, location, microphone, musicLibrary, passkeys, passkeysEnumeration,
phoneCall, phoneCallHistory, picturesLibrary, radios, sensors.custom,
serialCommunication, systemAIModels, usb, userAccountInformation, userDataTasks,
userNotificationListener, videosLibrary, webcam, wifiData, wiFiDirect
```

이 페이지는 `webcam` 과 `microphone` 을 다룹니다.

## 위치와 버전별 차이

### 레지스트리

| 하이브 | 키 |
|---|---|
| NTUSER.DAT (사용자마다) | `Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\<권한 이름>` |
| SOFTWARE | `Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\<권한 이름>` |

하이브 파일의 위치는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

### 데이터베이스

`C:\ProgramData\Microsoft\Windows\CapabilityAccessManager\` 폴더에는 다음 파일이 있습니다. 형식은 모두 SQLite 입니다.

| 파일 | 함께 있던 파일 |
|---|---|
| `CapabilityAccessManager.db` | `-wal`, `-shm` |
| `CapabilityConsentStorage.db` | `-wal`, `-shm` |
| `CapabilityAccessManager (1).db` (예전 파일로 보임) | `-wal`, `-shm` |

SQLite 형식은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

### 버전에 따라 달라지는 점

| 항목 | 내용 | 근거 |
|---|---|---|
| 데스크톱 앱 스위치 이름 | Windows 11 은 "Let desktop apps access your camera", Windows 10 은 "Allow desktop apps to access your camera" | [1] |
| SOFTWARE 쪽 앱별 기록 | RECmd 배치 파일이 SOFTWARE 하이브의 `microphone`·`webcam` 아래에서 시각 값을 읽습니다 | [2] |
| 앱별 기록이 있는 하이브 | SOFTWARE 쪽 `webcam`·`microphone` 키에는 `Value`·`LastSetTime` 만 있고 앱 하위 키가 없습니다. 앱별 사용 시각은 NTUSER.DAT 쪽에 있습니다 | Windows 11 25H2 (빌드 26200) |

앱별 기록은 SOFTWARE 와 NTUSER.DAT 두 하이브를 모두 봅니다.

## 구조

### 앱 하위 키

| 앱 종류 | 하위 키 위치 | 하위 키 이름 예 |
|---|---|---|
| 스토어 (패키지) 앱 | `<권한 이름>\<패키지 패밀리 이름>` | `Microsoft.WindowsCamera_8wekyb3d8bbwe` |
| 일반 데스크톱 앱 | `<권한 이름>\NonPackaged\<실행 파일 전체 경로>` | `C:#Program Files#<회사>#<앱>#<앱>.exe` |

데스크톱 앱의 하위 키 이름은 실행 파일의 전체 경로이고, 경로의 `\` 는 `#` 으로 바뀌어 있습니다.

### 앱 하위 키의 값

| 값 | 형식 | 뜻 | 근거 |
|---|---|---|---|
| `LastUsedTimeStart` | REG_QWORD, FILETIME | 그 앱이 장치를 쓰기 시작한 시각 | [2] |
| `LastUsedTimeStop` | REG_QWORD, FILETIME | 그 앱이 장치 쓰기를 멈춘 시각 | [2] |
| `LastUserAnnotatedLabel` | REG_DWORD (예: 2) | 뜻을 단정하지 않고 값만 옮깁니다 | |
| `PersistedInDatabase` | REG_DWORD (예: 1) | 이름으로 짐작하면 DB 에 옮겨 적었다는 표시로 보입니다 | |

- 스토어 앱 하위 키에는 `Value` (REG_SZ) 와 `LastSetTime` (REG_QWORD) 도 있습니다. `Value` 에는 `Allow` 나 `Prompt` 가 들어갑니다.
- 한 번도 장치를 쓰지 않은 앱의 하위 키에는 `LastUsedTime` 값이 없습니다.

### 권한 키와 NonPackaged 키의 값

권한 키 자체와 `NonPackaged` 키에는 `Value` (REG_SZ, 예: `Allow`) 와 `LastSetTime` (REG_QWORD) 이 있습니다.

- `Value` 는 설정 화면의 켬·끔으로 보입니다.
- `LastSetTime` 은 그 설정을 바꾼 시각으로 보입니다.
- 알려진 `Value` 는 `Allow` 와 `Prompt` 입니다. `Deny` 가 오는지는 실제 데이터로 확인해야 합니다.

### 데이터베이스 표

아래 표 구조는 옛 파일 `CapabilityAccessManager (1).db` (2025년 4월 날짜) 의 것입니다. 지금 쓰는 DB 도 구조가 같은지는 실제 DB 의 표 목록으로 확인합니다.

| 표 | 열 |
|---|---|
| `NonPackagedUsageHistory` | ID, LastUsedTimeStart, LastUsedTimeStop, AccessBlocked, Capability, FileID, ProgramID, BinaryFullPath, UserSid, AppName, ServiceName, AccessGUID, Label |
| `PackagedUsageHistory` | ID, LastUsedTimeStart, LastUsedTimeStop, AccessBlocked, Capability, PackageFamilyName, UserSid, AccessGUID, Label, AppName |
| `NonPackagedIdentityRelationship` | ID, BinaryFullPath, FileID, ProgramID, LastObservedTime |
| `NonPackagedGlobalPromptHistory` | ID, ShownTime, Capability, FileID, ProgramID, UserSid |
| 문자열 사전 표 (열은 ID, StringValue) | Capabilities, PackageFamilyNames, BinaryFullPaths, Users, FileIDs, ProgramIDs, AccessGUIDs, AppNames, ServiceNames |

- 사용 기록 표의 Capability, BinaryFullPath, UserSid, FileID 같은 열에는 숫자 ID 가 들어 있고, 실제 문자열은 같은 이름의 사전 표에서 찾습니다. 예를 들어 Capability 열의 숫자는 `Capabilities` 표의 ID 입니다.
- 사전 표 값의 예를 들면, `Capabilities` 에는 `location`, `BinaryFullPaths` 에는 `C:\Windows\System32\dllhost.exe`, `Users` 에는 `S-1-5-21-…-500` 모양의 SID 가 들어갑니다.
- `FileIDs` 와 `ProgramIDs` 의 값은 `0000` 뒤에 16진수 40자가 붙은 44자 문자열입니다. [AmCache](amcache-hve/index.md) 의 FileId·ProgramId 와 모양이 같습니다. 파일의 SHA-1 인지는 `BinaryFullPath` 의 파일에서 SHA-1 을 직접 구해 맞춰 봅니다.
- 시각 열에는 FILETIME 정수가 들어 있습니다.

레지스트리에는 앱마다 마지막 한 쌍만 남습니다. DB 는 사용할 때마다 행을 쌓을 수 있는 표 모양입니다. 여러 번 쓴 기록이 실제로 여러 행으로 남는지는 실제 DB 에서 확인합니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 사용자 하이브에서 이 앱이 카메라나 마이크를 마지막으로 쓰기 시작한 시각과 멈춘 시각 | 무엇을 찍거나 녹음했는지. 녹화·녹음 파일이 남았는지 |
| 어느 실행 파일 경로가 장치를 썼는지 (NonPackaged 하위 키 이름) | 마지막 한 번 전의 사용 이력 |
| 어느 사용자 프로필에서 쓴 기록인지 (NTUSER.DAT) | 그 계정 앞에 실제로 누가 앉아 있었는지 |
| | 기록이 없을 때 장치를 쓰지 않았다는 것 |

- 이 기록은 앱이 장치를 열고 닫은 시각이며, 녹화·녹음한 내용이 있다는 뜻은 아닙니다.
- NonPackaged 하위 키 이름으로 원격 도구나 화상 회의 프로그램 같은 실행 파일이 카메라·마이크를 썼는지 알 수 있습니다.
- 데스크톱 앱이 설정 목록에 늘 나오지는 않습니다[1]. 설정을 꺼도 카메라·마이크에 접근할 수 있는 경우도 있어서 기록이 없다고 장치를 쓰지 않았다고 단정하지 않습니다.

### 보고서 문장

아래 경로와 시각은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 A 의 NTUSER.DAT 에서 `ConsentStore\webcam\NonPackaged\C:#Tools#meet.exe` 키를 보면 LastUsedTimeStart 가 2025-05-12 09:00:00 UTC, LastUsedTimeStop 이 2025-05-12 09:45:10 UTC 입니다. 이 실행 파일이 카메라를 마지막으로 쓴 구간이 이 시간대라는 기록입니다."
- 쓰면 안 되는 문장: "사용자 A 가 2025-05-12 18:00 부터 45분 동안 화상 회의를 녹화했습니다."

## 시각 해석

| 시각 | 어디에 남나 | 무엇을 가리키나 | 형식 |
|---|---|---|---|
| `LastUsedTimeStart` | 앱 하위 키 | 앱이 장치를 쓰기 시작한 때 | FILETIME, UTC |
| `LastUsedTimeStop` | 앱 하위 키 | 앱이 장치 쓰기를 멈춘 때 | FILETIME, UTC |
| `LastSetTime` | 권한 키, NonPackaged 키, 스토어 앱 하위 키 | 설정을 바꾼 때로 보입니다 | REG_QWORD |
| DB 의 시각 열 | `LastUsedTimeStart`, `LastUsedTimeStop`, `LastObservedTime`, `ShownTime` | 열 이름이 가리키는 때로 보입니다 | FILETIME 정수 |

- 시작·끝 값은 FILETIME 이므로 UTC 로 읽습니다. UTC 로 풀면 시작과 끝의 간격이 몇 초에서 몇 시간으로 나옵니다. 예를 들어 01:16:34 UTC 에 시작해 02:29:28 UTC 에 끝난 항목이 있습니다.
- 옛 DB 파일의 값 133897659145807372 는 2025-04-22 03:25:14 UTC 입니다.
- 레지스트리에는 앱마다 시작·끝 한 쌍만 있습니다. 새로 쓰면 이 한 쌍을 덮어쓰는 것으로 보입니다.
- 장치를 쓰는 동안 `LastUsedTimeStop` 이 0 인지는 실제 데이터로 확인해야 합니다.
- 옛 DB 파일의 `NonPackagedUsageHistory` 에서 `AccessBlocked=1` 인 행은 `LastUsedTimeStart` 가 0 이고 `LastUsedTimeStop` 에만 시각이 있습니다. 막힌 접근은 시작 시각 없이 남는 것으로 보입니다. 이런 행이 4개뿐인 예라 일반화하기 어렵습니다.
- FILETIME 계산은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서, 현지 시각 변환은 [시간대 설정](../system-account/time-zone.md) 에서 다룹니다.

## 함정과 한계

1. **SOFTWARE 하이브만 봅니다.** Windows 11 25H2 에서는 앱별 사용 시각이 NTUSER.DAT 에만 있을 수 있습니다. SOFTWARE 만 읽는 도구로는 결과가 비어 나올 수 있습니다. 사용자 프로필마다 NTUSER.DAT 를 따로 봅니다.
2. **기록이 없으면 쓰지 않았다고 봅니다.** 데스크톱 앱이 설정 목록에 늘 나오지는 않습니다. 설정을 꺼도 접근할 수 있는 경우가 있습니다.
3. **마지막 한 쌍을 전체 이력으로 읽습니다.** 레지스트리에는 앱마다 마지막 시작·끝만 있습니다. 이전 사용은 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 옛 하이브를 찾아 봅니다.
4. **하위 키 이름을 그대로 경로로 적습니다.** 하위 키 이름의 `#` 은 `\` 로 바꿔 읽습니다.
5. **라이브 PC 에서 DB 를 보통 방식으로 복사합니다.** 관리자 권한으로도 DB 폴더의 목록 보기가 거부될 수 있습니다. 백업 권한 복사 (`robocopy /B`) 로는 잠기지 않은 옛 파일만 복사되고, 지금 쓰는 DB 는 사용 중이라 복사되지 않습니다. 라이브 수집에는 볼륨 섀도 복사본이나 원시 디스크 읽기가 필요합니다. 방법은 [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) 과 [증거 획득](../../03-techniques/process-acquisition/evidence-acquisition/index.md) 에서 다룹니다.
6. **옛 DB 와 지금 DB 를 섞습니다.** 같은 폴더에 `CapabilityAccessManager (1).db` 같은 옛 파일이 있을 수 있습니다. 파일마다 따로 읽고, 결과에 어느 파일에서 나온 값인지 적습니다.
7. **DB 표 구조를 고정된 것으로 봅니다.** 위 표 구조는 옛 파일의 것입니다. 지금 DB 는 표 목록부터 다시 확인합니다.

### 지우기와 조작

- **키나 값을 지웁니다.** 지운 키와 값은 하이브 안 빈 공간이나 트랜잭션 로그에 남을 수 있습니다. 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.
- **DB 행을 지웁니다.** SQLite 에서 지운 행을 찾는 방법은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다. DB 를 복사할 때는 `-wal`, `-shm` 파일을 함께 가져옵니다.
- **레지스트리와 DB 가 맞지 않습니다.** 같은 앱의 레지스트리 값과 DB 행을 서로 맞춰 봅니다. 한쪽에만 기록이 있으면 한쪽을 지웠을 수도 있고, 두 곳에 남는 조건이 달라서일 수도 있습니다. 어느 쪽인지 단정하지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 FILETIME 명세를 보고 만든 예시입니다. 실제 데이터에서 뽑은 값이 아닙니다.

`LastUsedTimeStart` 값 (REG_QWORD, 8바이트) 입니다.

```
오프셋  00 01 02 03 04 05 06 07
0x00    00 28 BF 3D 1C C3 DB 01
```

1. 8바이트를 리틀 엔디언으로 읽습니다. `0x01DBC31C3DBF2800` 입니다.
2. 10진수로 바꾸면 133915140000000000 입니다.
3. FILETIME 으로 풀면 2025-05-12 09:00:00 UTC 입니다.

`LastUsedTimeStop` 값입니다.

```
오프셋  00 01 02 03 04 05 06 07
0x00    00 57 08 8D 22 C3 DB 01
```

4. 같은 방법으로 읽으면 `0x01DBC3228D085700`, 곧 133915167100000000 입니다.
5. FILETIME 으로 풀면 2025-05-12 09:45:10 UTC 입니다.
6. 두 값의 차이는 45분 10초입니다. 이 앱이 장치를 마지막으로 연 구간의 길이입니다.
7. 하위 키 이름이 `C:#Tools#meet.exe` 라면 실행 파일 경로는 `C:\Tools\meet.exe` 입니다.

### 공개 도구로 한 번

**레지스트리**: Eric Zimmerman 의 RECmd 에는 Kroll_Batch.reb 배치 파일이 있습니다. 이 배치는 SOFTWARE 하이브의 `ConsentStore\microphone` 과 `ConsentStore\webcam\*\*` 아래 `LastUsedTimeStart`·`LastUsedTimeStop` 을 하위 키까지 따라가며 읽습니다. 배치 항목의 하이브 종류는 SOFTWARE 하나뿐입니다. 값은 FILETIME 으로 풀고, 분류는 Devices 입니다.

- 앱별 기록이 NTUSER.DAT 에만 있으면 이 항목으로는 결과가 나오지 않습니다.
- NTUSER.DAT 의 같은 경로는 레지스트리 보기 도구로 따로 읽거나, 배치 항목을 고쳐 읽습니다.

**데이터베이스**: sqlite3 명령줄 도구나 다른 SQLite 보기 도구로 엽니다. 사전 표를 이어 붙여야 사람이 읽을 수 있습니다. 아래는 옛 파일의 표 구조로 만든 예시 쿼리입니다.

```sql
SELECT h.ID,
       c.StringValue AS capability,
       p.StringValue AS binary_path,
       u.StringValue AS user_sid,
       h.LastUsedTimeStart,
       h.LastUsedTimeStop,
       h.AccessBlocked
FROM NonPackagedUsageHistory h
LEFT JOIN Capabilities    c ON c.ID = h.Capability
LEFT JOIN BinaryFullPaths p ON p.ID = h.BinaryFullPath
LEFT JOIN Users           u ON u.ID = h.UserSid;
```

- 쿼리를 돌리기 전에 표 목록과 열 이름이 위와 같은지 확인합니다.
- 시각 열은 FILETIME 정수이므로 따로 풉니다.
- 도구가 보여 준 시각이 UTC 인지, 분석 PC 의 현지 시각인지 확인합니다.
- 값 한두 개는 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [AmCache](amcache-hve/index.md) | DB 의 FileID·ProgramID 와 같은 모양의 값으로 같은 실행 파일을 찾습니다 |
| [BAM·DAM](background-activity-moderator.md) | 같은 실행 파일이 같은 시간대에 실행된 흔적 |
| [프리페치](prefetch/index.md) | 같은 실행 파일의 실행 시각과 횟수 |
| [SRUM](system-resource-usage-monitor/index.md) | 같은 시간대에 그 앱이 자원을 쓴 기록 |
| [스토어 앱 설치 목록](../system-account/appx-staterepository.md) | 패키지 패밀리 이름이 어떤 앱인지 |
| [사용자 프로필 목록](../system-account/profilelist.md) | DB 의 `Users` 표 SID 가 어느 계정인지 |
| [원격 제어 프로그램](../network/remote-access-tools/index.md) | NonPackaged 경로가 원격 도구일 때 그 도구의 접속 기록 |
| [줌](../messengers/zoom.md) · [마이크로소프트 팀즈](../messengers/teams.md) | 화상 회의 프로그램이 따로 남긴 회의 기록 |
| [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 옛 하이브에 남은 이전 시작·끝 시각 |

여러 기록을 합쳐 읽는 순서는 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 와 [원격 제어 프로그램으로 누가 조작했나](../../04-scenarios/incident/remote-access-tool-abuse.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 자료 가운데 Windows 10 이후의 이미지를 골라 다음을 풀어 봅니다.

1. 사용자 NTUSER.DAT 와 SOFTWARE 하이브의 `ConsentStore\webcam`, `ConsentStore\microphone` 아래에 앱 하위 키가 있습니까? 어느 하이브에 시각 값이 있습니까?
2. NonPackaged 아래 실행 파일 경로를 모두 적어 봅니다. 원격 도구나 화상 회의 프로그램이 있습니까?
3. 앱마다 `LastUsedTimeStart` 와 `LastUsedTimeStop` 을 직접 풀어 UTC 로 적어 봅니다. 사용 구간이 가장 긴 앱은 무엇입니까?
4. `CapabilityAccessManager` 폴더에 DB 가 있습니까? 표 목록이 이 페이지의 표와 같습니까?
5. DB 에서 같은 앱의 행을 찾아 레지스트리 시각과 비교해 봅니다. 행이 여러 개입니까?
6. 사용 구간 안에 같은 실행 파일의 프리페치나 BAM 기록이 있습니까?

실험용 가상 머신이 있으면 카메라 앱과 데스크톱 앱으로 장치를 한 번씩 써 봅니다. 앞뒤로 NTUSER.DAT, SOFTWARE, DB 를 떠서 어느 값과 행이 바뀌는지 비교합니다. 쓰는 동안 `LastUsedTimeStop` 이 어떻게 보이는지도 확인합니다. 결과에는 실험한 Windows 버전을 함께 적습니다.

## 참고 문헌

- Microsoft Support, "Windows camera, microphone, and privacy" — https://support.microsoft.com/en-us/windows/windows-camera-microphone-and-privacy-a83257bc-e990-d54a-d212-b5e41beba857
- Eric Zimmerman RECmd, "Kroll_Batch.reb" — https://raw.githubusercontent.com/EricZimmerman/RECmd/master/BatchExamples/Kroll_Batch.reb
