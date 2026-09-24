# 왓츠앱 데스크톱 (WhatsApp Desktop)

> 위치: 아티팩트 사전 > 메신저

## 한 줄 요약

Windows 용 왓츠앱은 스토어 패키지 앱이고, 대화 DB 를 패키지의 `LocalState` 폴더에 둡니다. 이 DB 는 암호화된 SQLite 입니다. 키는 장치 고유 ID 에 따라 정해집니다. 공개 자료는 대상 PC 가 켜져 있어야 이 ID 를 얻을 수 있다고 설명합니다. DB 에서 지운 값은 0 으로 덮입니다. 그래서 WAL 파일을 꼭 함께 모읍니다.

이 페이지의 저장 구조 설명은 공개 저장소 ZAPiXDESK 의 README 를 따릅니다. 관찰 PC 에 왓츠앱이 없어서 직접 확인한 내용은 없습니다. 그래서 이 페이지에는 "관찰" 항목이 없습니다.

## 무엇을 기록하나 · 왜 생기나

앱은 대화를 PC 에서 다시 보여 주려고 로컬 DB 에 기록을 적습니다. README 가 설명하는 DB 는 아래와 같습니다. (ZAPiXDESK README)

- **대화 DB**: 암호화된 SQLite 입니다. 파일 이름은 README 요약에 없습니다.
- **session.db**: 세션 정보를 담습니다.
- **nativeSettings.db**: README 는 "나머지 키들" 을 담는 DB 라고 적었습니다.
- **WAL 파일**: 각 DB 옆에 쓰기 앞 로그 (Write-Ahead Log, WAL) 파일이 있습니다.

메시지와 연락처가 어느 DB 의 어느 표에 있는지는 확인하지 못했습니다. 받은 파일과 미디어를 두는 폴더도 확인하지 못했습니다.

왓츠앱 데스크톱은 구조가 바뀌어 왔습니다. CCL 글은 Local Storage·IndexedDB 를 LevelDB 로 저장하는 앱 목록에 왓츠앱 데스크톱을 넣었습니다. (CCL 글) 이 목록은 글을 쓴 시점 기준입니다. 지금 README 가 설명하는 판은 스토어 패키지 구조입니다. LevelDB 를 쓰던 판의 폴더 경로는 확인하지 못했습니다. LevelDB 형식은 [LevelDB 저장소](/01-foundations/database-log-formats/leveldb.md) 에서 다룹니다.

## 위치와 버전별 차이

### 두 가지 구조

README 는 Meta 가 2025-12-09 부터 Windows 판을 UWP 구조에서 WebView2 구조로 바꿨다고 적었습니다. (ZAPiXDESK README)

| 구조 | README 가 적은 시기 | 확인하지 못한 점 |
|---|---|---|
| UWP 구조 | 2025-12-09 이전 | 업데이트가 사용자마다 같은 날 적용됐는지 확인하지 못했습니다 |
| WebView2 구조 | 2025-12-09 이후 | 두 구조의 폴더 구성 차이를 확인하지 못했습니다 |

README 에는 두 구조의 패키지 이름을 따로 적은 곳이 없습니다. 그래서 패키지 이름만 보고 구조를 가리지 않습니다. 폴더 안 파일 구성과 설치된 버전을 함께 보고 가립니다.

### 설치 폴더

README 가 든 설치 경로 예는 아래와 같습니다. (ZAPiXDESK README)

```
C:\Program Files\WindowsApps\5319275A.WhatsAppDesktop_2.2587.9.0_x64__cv1g1gvanyjgm\WhatsApp.Root.exe
```

- README 가 든 실행 파일 이름은 `WhatsApp.Root.exe` 입니다.
- 폴더 이름에 앱 버전(이 예에서는 2.2587.9.0)과 아키텍처가 들어 있습니다.
- 증거 PC 에 설치된 버전은 [스토어 앱 설치 목록](/02-artifacts/system-account/appx-staterepository.md) 에서 확인합니다.

### 데이터 폴더

README 는 주 데이터 폴더를 패키지의 `LocalState` 폴더라고 적었습니다. (ZAPiXDESK README)

스토어 패키지 앱의 폴더 규칙을 따르면 전체 경로는 아래처럼 짐작합니다.

```
%LOCALAPPDATA%\Packages\5319275A.WhatsAppDesktop_cv1g1gvanyjgm\LocalState
```

- 이 경로는 README 의 설치 폴더 이름에서 버전과 아키텍처를 빼서 만든 것입니다.
- 직접 확인한 경로가 아닙니다.
- 실제 증거에서는 사용자마다 `%LOCALAPPDATA%\Packages` 아래에서 `WhatsApp` 이 들어간 폴더를 모두 찾습니다.
- 패키지 폴더 구조는 [UWP 앱 데이터 구조](/01-foundations/app-mail-data/packages-settings-dat.md) 에서 다룹니다.

## 구조

### LocalState 의 파일

| 파일 | 형식 | 내용 | 근거 |
|---|---|---|---|
| `session.db` | 암호화된 SQLite | 세션 정보 | README |
| `nativeSettings.db` | 암호화된 SQLite | 나머지 키들 | README |
| 그 밖의 DB | 암호화된 SQLite | 이름은 README 요약에 없음 | README |
| 각 DB 의 WAL 파일 | SQLite WAL | 아직 DB 본체에 합쳐지지 않은 변경 | README |

SQLite 파일과 WAL 파일의 구조는 [SQLite 데이터베이스](/01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

### 암호화

이 절은 무엇이 암호화됐고 키가 무엇에 묶였는지만 적습니다. 푸는 절차는 적지 않습니다.

- 대화 DB 는 암호화된 SQLite 입니다. (ZAPiXDESK README)
- 고정 키들은 DPAPI-NG 로 보호합니다. (ZAPiXDESK README) DPAPI 는 [DPAPI 구조](/01-foundations/protection/data-protection-api/index.md) 에서 다룹니다.
- 키는 오프라인 장치 고유 ID (OfflineDeviceUniqueID, ODUID) 에 따라 정해집니다. (ZAPiXDESK README)
- ODUID 는 TPM·레지스트리 등에서 나옵니다. (ZAPiXDESK README)
- README 는 대상 PC 가 켜져 있어야 이 장치 고유 ID 를 얻을 수 있고, 이 ID 없이는 풀 수 없다고 적었습니다.
- README 는 이 ID 와 `LocalState` 폴더를 함께 모으면 다른 PC 에서 풀 수 있다고 적었습니다.
- 암호 알고리즘 이름은 README 에 없습니다.
- 사용자의 Windows 암호가 필요한지도 README 에 없습니다.

해석: 꺼진 PC 의 디스크 이미지만으로는 풀기 어려울 수 있습니다. 켜진 PC 를 현장에서 만났을 때가 중요한 기회입니다. 켜진 PC 를 다루는 순서는 [라이브 응답](/03-techniques/process-acquisition/live-response/index.md) 에서, 암호화된 증거를 다루는 방법은 [암호화 증거 다루기](/03-techniques/analysis/encrypted-evidence/index.md) 에서 다룹니다.

### 지운 값과 WAL

- DB 에는 secure-delete 설정(PRAGMA)이 켜져 있습니다. (ZAPiXDESK README)
- 그래서 지운 값은 DB 본체에서 0 으로 덮입니다.
- README 는 필요한 값을 WAL 파일에서 되찾는다고 적었습니다.

해석: WAL 파일을 빼고 DB 본체만 모으면 지운 값과 최근 변경을 잃을 수 있습니다. `-wal` 로 끝나는 파일을 반드시 함께 모읍니다.

## 증거로서 의미

### 증명하는 것

- **앱이 이 계정에 있었다는 것.** 사용자 프로필의 `Packages` 아래에 왓츠앱 데이터 폴더가 있으면, 그 계정에 앱이 등록된 적이 있다는 단서입니다.
- **설치된 버전.** 설치 폴더 이름에 앱 버전이 들어 있습니다.
- **DB 를 푼 뒤의 기록.** 풀면 대화 DB 에 적힌 기록을 볼 수 있습니다. 어느 표에 무엇이 있는지는 확인하지 못했으므로, 표마다 뜻을 먼저 확인합니다.
- **지우기 전 값의 단서.** DB 본체에서 0 으로 덮인 값이 WAL 파일에 남아 있을 수 있습니다.

### 증명하지 못하는 것

- **DB 를 풀지 못하면 대화 내용.** 파일이 있다는 사실만 말할 수 있습니다.
- **어느 기기에서 보냈는지.** 이 페이지는 보낸 기기를 가리는 칸을 확인하지 못했습니다. PC 의 DB 에 있다고 PC 에서 보냈다고 단정하지 않습니다.
- **누가 입력했는지.** 계정까지만 알려 줍니다. 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](/04-scenarios/activity/user-attribution.md) 에서 다룹니다.
- **왓츠앱을 쓰지 않았다는 것.** 왓츠앱에는 웹 판도 있습니다. README 가 인용한 논문 제목이 웹 판과 UWP 판을 함께 다룹니다. 데스크톱 폴더가 없으면 [크롬 계열 브라우저](/02-artifacts/browsers/chrome-edge-whale/index.md) 의 방문 기록도 봅니다.

보고서에는 "피의자가 왓츠앱으로 대화했다" 가 아니라 이렇게 씁니다. "A 계정의 `%LOCALAPPDATA%\Packages` 아래에 왓츠앱 데스크톱 패키지 폴더가 있고, 그 `LocalState` 에 암호화된 SQLite DB 와 WAL 파일이 있다. 이 DB 는 수집 시점에 풀지 못했다."

## 시각 해석

| 시각 | 알려 주는 것 | 주의 |
|---|---|---|
| DB 안의 시각 칸 | 확인하지 못했습니다 | DB 를 푼 뒤 칸마다 형식을 확인합니다. 형식은 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다 |
| DB·WAL 파일의 파일 시스템 시각 | 앱이 파일을 마지막으로 고친 때의 단서 | 앱이 실행 중이면 사용자 동작 없이도 바뀔 수 있습니다. [마스터 파일 테이블](/02-artifacts/filesystem/mft.md) 에서 봅니다 |
| 설치 폴더와 데이터 폴더의 시각 | 설치·업데이트 때의 단서 | 설치 기록은 [스토어 앱 설치 목록](/02-artifacts/system-account/appx-staterepository.md) 과 맞춰 봅니다 |

파일 시스템 시각은 UTC 로 적힙니다. 보고서에 현지 시각으로 옮길 때는 [시간대 설정](/02-artifacts/system-account/time-zone.md) 을 확인합니다.

## 함정과 한계

- **전원을 먼저 끕니다.** README 설명대로라면 장치 고유 ID 는 켜진 PC 에서 얻습니다. 전원을 끄면 그 기회를 잃을 수 있습니다(해석).
- **WAL 을 빠뜨립니다.** secure-delete 때문에 DB 본체에는 지운 값이 남지 않습니다. WAL 이 없으면 되찾을 곳이 줄어듭니다.
- **원본 DB 를 SQLite 도구로 엽니다.** 늘 사본에서 작업합니다. WAL 을 다루는 주의점은 [SQLite 데이터베이스](/01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.
- **패키지 이름으로 구조를 단정합니다.** README 는 두 구조의 패키지 이름을 나눠 적지 않았습니다. 폴더 안 파일과 버전으로 가립니다.
- **2025-12-09 를 증거 PC 가 바뀐 날로 씁니다.** README 는 이날 구조가 바뀌었다고 적었지만, 증거 PC 에 업데이트가 언제 적용됐는지는 설치 기록으로 따로 확인합니다.
- **예전 자료의 경로를 요즘 판에 씁니다.** LevelDB 를 쓰던 시절의 설명은 요즘 스토어 판에 맞지 않을 수 있습니다.
- **도구가 푼 결과만 믿습니다.** 도구가 어떤 키를 썼는지, WAL 을 넣었는지 기록합니다. 방법은 [도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 명세로 만든 예시입니다. 실제 왓츠앱 파일에서 나온 값이 아닙니다.

암호화하지 않은 SQLite 파일은 첫 16바이트가 `SQLite format 3` 과 0 바이트 하나입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00   53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
```

1. `LocalState` 의 `.db` 파일마다 첫 16바이트를 봅니다.
2. 이 문자열이 아니면 SQLite 도구로 바로 열리지 않습니다. README 가 말한 암호화된 DB 로 봅니다.
3. 이 문자열이어도 표가 읽히는지 사본에서 따로 확인합니다.
4. `.db` 마다 짝이 되는 `-wal` 파일이 있는지, 크기가 얼마인지 적어 둡니다.
5. 파일 이름·크기·파일 시스템 시각을 표로 남깁니다. 풀지 못하더라도 이 표가 "무엇이 있었나" 의 근거가 됩니다.

### 공개 도구로 한 번

공개 도구의 예로 ZAPiXDESK 가 있습니다. 켜진 PC 에서 쓰는 라이브 포렌식 도구입니다. 이 페이지의 저장 구조 설명은 그 README 에서 가져왔습니다. 도구 자체의 동작은 이 페이지에서 시험하지 않았습니다.

어느 도구를 쓰든 도구가 읽은 DB 목록과 폴더의 `.db`·`-wal` 목록을 맞춰 봅니다. 빠진 파일이 있으면 이유를 적습니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 점 |
|---|---|
| [스토어 앱 설치 목록](/02-artifacts/system-account/appx-staterepository.md) | 설치 시각과 버전을 봅니다 |
| [UWP 앱 데이터 구조](/01-foundations/app-mail-data/packages-settings-dat.md) | 패키지 폴더의 다른 하위 폴더를 읽는 법을 봅니다 |
| [SRUM](/02-artifacts/execution/system-resource-usage-monitor/index.md) | 앱이 네트워크를 쓴 시간대를 봅니다 |
| [윈도 알림 기록](/02-artifacts/execution/wpndatabase-db.md) | 앱 알림이 남았는지 봅니다 |
| [크롬 계열 브라우저](/02-artifacts/browsers/chrome-edge-whale/index.md) | 웹 판을 쓴 흔적을 봅니다 |
| [메모리 분석](/03-techniques/analysis/memory-forensics/index.md) | 켜진 PC 에서 메모리를 떴다면 화면에 띄운 내용이 남았는지 봅니다 |

조사 전체 흐름은 [누구와 연락을 주고받았나](/04-scenarios/activity/communication-reconstruction.md) 에서 다룹니다. 다른 메신저는 [카카오톡 PC](/02-artifacts/messengers/kakaotalk-pc/index.md), [텔레그램](/02-artifacts/messengers/telegram.md), [마이크로소프트 팀즈](/02-artifacts/messengers/teams.md) 페이지에서 다룹니다.

## 실습

왓츠앱 데스크톱이 들어간 공개 검체는 확인하지 못했습니다. Windows 11 가상 머신에 앱을 설치해 직접 시험합니다. 시험 전에 앱 버전을 적어 둡니다.

1. 로그인 전과 뒤에 `%LOCALAPPDATA%\Packages` 아래 왓츠앱 폴더의 파일 목록이 어떻게 달라집니까?
2. `LocalState` 에 어떤 `.db` 파일이 생깁니까? 각 파일의 첫 16바이트는 무엇입니까?
3. 메시지를 몇 개 주고받은 뒤 `-wal` 파일의 크기가 바뀝니까?
4. 메시지 하나를 지운 뒤 DB 본체와 WAL 파일의 크기·수정 시각은 어떻게 바뀝니까?
5. 앱을 제거한 뒤 패키지 데이터 폴더가 남습니까?

## 참고 문헌

- kraftdenker, ZAPiXDESK — README — https://github.com/kraftdenker/ZAPiXDESK
- CCL Solutions Group, "Hang on! That's not SQLite! Chrome, Electron and LevelDB" — https://www.cclsolutionsgroup.com/post/hang-on-thats-not-sqlite-chrome-electron-and-leveldb
