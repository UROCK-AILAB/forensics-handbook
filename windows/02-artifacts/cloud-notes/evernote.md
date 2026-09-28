---
title: "에버노트"
parent: "아티팩트 · 클라우드·노트"
nav_order: 2280
---

# 에버노트 (Evernote)

에버노트 데스크톱 앱은 계정의 노트를 로컬 DB 에 담아 둡니다. v10 이전 앱은 계정마다 SQLite 파일 `<계정 이름>.exb` 를 쓰고, v10 이후 앱은 `AppData\Roaming\Evernote` 폴더를 씁니다. 옛 DB 에는 노트 제목, 작성자, 노트북, 시각, 위치 정보가 들어 있습니다.

> 경로는 2021년 11월 기준입니다[2]. v10 이후 폴더의 내부 구조는 실제 데이터로 확인합니다.

## 무엇을 기록하나 · 왜 생기나

에버노트는 노트를 서버에 두고 여러 기기에서 동기화하는 노트 서비스이고, 데스크톱 앱은 계정의 노트를 로컬 DB 에 담아 두고 씁니다. 옛 노트 DB 에는 작성자, 제목, 만든·고친 시각, 위치, 노트북, 위치 정보(위도·경도·고도)가 들어 있습니다. 이 DB 에서 뽑을 수 있는 열은 40개가 넘고, 만든·고친·지운·공유한 시각, 공유 정보, 암호화 표시, 동기화 상태도 들어 있습니다. 같은 폴더의 다른 파일에는 계정 정보와 노트 미리보기 조각이 있고, 앱 로그에는 인증 정보, 계정 ID, 앱 시작·종료 시각이 남습니다[2].

## 위치와 버전별 차이

### v10 이전 앱

| 파일 | 위치 | 내용 |
|---|---|---|
| `*.exb` | `C:\Users\<USER>\AppData\Local\Evernote\Evernote\Databases\` | 노트 DB (SQLite). 파일 이름은 계정 이름입니다 |
| `.accounts` | 같은 `Databases` 폴더 | 계정의 사용자 이름과 이메일. KAPE 대상 파일의 파일 이름 조건은 `.accounts` 입니다[1] |
| `*.exb.snippets` | 같은 `Databases` 폴더 | 노트 스니펫(미리보기 조각) |
| `AppLog_YYYY-MM-DD.txt` | `…\Evernote\Logs\` | 앱 로그. 앞부분 경로는 실제 기기에서 확인합니다 |

- `.exb` 경로를 `AppData\Local\Evernote` 부분 없이 `C:\Users\<USER>\Evernote\Databases\` 로 적은 곳도 있습니다[2]. 경로 일부가 빠진 표기일 수 있습니다. 실제 기기에서는 사용자 프로필 아래에서 `Databases` 폴더와 `*.exb` 를 이름으로 찾습니다.
- 로그 파일은 에버노트를 실행한 날마다 한 번 만들어집니다.

### Microsoft Store 판

패키지 이름은 `Evernote.Evernote_q4d96b2w5wcc2` 입니다. 아래 경로는 `C:\Users\<USER>\AppData\Local\Packages\Evernote.Evernote_q4d96b2w5wcc2\` 아래입니다.

| 파일 | 위치 |
|---|---|
| 노트 DB | `LocalState\Databases\<계정 이름>.exb` |
| 로컬 저장소 DB | `LocalCache\Roaming\Evernote\Local Storage\databases\<파일 이름>.db` |
| 로그 | `LocalCache\Roaming\Evernote\logs\YYYYMMDD.txt` |

패키지 폴더의 공통 구조는 [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) 에 있습니다.

### v10 이후 앱

데이터 폴더는 `C:\Users\<USER>\AppData\Roaming\Evernote` 입니다. 이 폴더 안에서 노트가 들어 있는 파일·표를 찾으려면 폴더를 하위 폴더째 모은 뒤 파일마다 머리를 보고 형식을 구분합니다.

위 경로는 2021년 11월 기준입니다[2]. 그 뒤 버전에서는 경로가 달라졌을 수 있습니다.

## 구조

### 옛 노트 DB (.exb)

- `.exb` 는 SQLite 파일입니다. SQLite 파일 구조는 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에 있습니다.
- 한 분석 구현은 아래 이름을 읽습니다. 실제 데이터에서 먼저 찾아볼 후보입니다.

| 후보 표 | 후보 열 |
|---|---|
| `note_attr` (노트) | `uid`, `title`, `size`, `author`, `date_created`, `date_updated`, `date_deleted`, `notebook` |
| `resource_attr` (첨부) | — |

- 실제 데이터에서는 `.tables` 와 `.schema` 로 표·열 이름을 먼저 확인합니다. 후보와 다르면 실제 데이터의 이름을 씁니다.

### DB 에 든 정보

| 묶음 | 정보 |
|---|---|
| 노트 기본 | 제목, 작성자, 노트북 |
| 시각 | 만든 시각, 고친 시각, 지운 시각, 공유한 시각 |
| 위치 | 위치, 위도, 경도, 고도 |
| 공유·동기화 | 공유 정보, 동기화 상태 |
| 보호 | 암호화 표시 |

## 증거로서 의미

### 증명하는 것

- `.exb` 와 `.accounts` 가 있으면 그 프로필에서 옛 앱이 그 계정으로 노트를 받은 적이 있습니다.
- `.accounts` 로 계정의 사용자 이름과 이메일을 알 수 있습니다.
- 노트 DB 로 노트 제목, 작성자, 노트북, 만든·고친 시각을 알 수 있습니다.
- 노트에 위치 정보가 있으면 그 노트에 기록된 위도·경도·고도를 알 수 있습니다.
- 로그로 앱 시작·종료 시각과 계정 ID 를 알 수 있습니다.
- 후보 열 `date_deleted` 가 실제 DB 에 있으면, 열 이름으로 보면 지운(휴지통) 노트도 DB 에 남아 있을 수 있습니다.

### 증명하지 못하는 것

- 노트가 DB 에 있다고 이 PC 에서 쓴 노트라는 뜻은 아닙니다. 다른 기기에서 쓴 노트가 동기화로 내려왔을 수 있습니다.
- 작성자 열은 노트에 기록된 값입니다. 그 노트를 실제로 쓴 사람은 따로 밝힙니다([그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)).
- 위치 정보는 노트에 기록된 좌표입니다. 이 PC 가 그 자리에 있었다는 뜻은 아닙니다.
- 옛 DB 의 정보가 v10 이후 앱에도 같은 모양으로 남는지는 실제 데이터로 확인해야 합니다.
- 로그 파일이 없는 날은 앱을 실행하지 않았을 수 있습니다. 로그를 지웠을 수도 있으므로 단정하지 않습니다.

보고서에는 "사용자가 X 노트를 썼다" 대신 이렇게 씁니다. "`<계정 이름>.exb` 에 제목이 X 인 노트 행이 있고, 만든 시각 열 값을 아래 변환식으로 바꾸면 Y 이다. 변환식은 분석 대상의 다른 시각과 맞춰 확인했다."

## 시각 해석

한 분석 구현은 날짜 열을 "0001-01-01 을 1일째로 센 일수(소수)" 로 보고 아래 식으로 바꿉니다.

```sql
datetime((값 * 86400) - 62135683200, 'unixepoch')
```

- 식의 상수 62135683200 은 0001-01-01 과 1970-01-01 사이 초 수(62135596800)보다 하루(86400초) 큽니다. 그래서 값 1.0 이 0001-01-01 00:00 이 됩니다.
- 아래는 이 식으로 만든 계산 예시입니다. 실제 데이터 값이 아닙니다.

| 값 | 변환 결과 |
|---|---|
| 738886.0 | 2024-01-01 00:00:00 |
| 738886.5 | 2024-01-01 12:00:00 |

- 소수 부분이 하루 안의 시각입니다. 0.5 는 12시간입니다.
- 결과가 UTC 인지 현지 시각인지는 로그의 앱 시작 시각이나 파일의 NTFS 시각과 맞춰 정합니다.
- 다른 시각 형식과의 관계는 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.

## 함정과 한계

- **판마다 위치가 다릅니다.** 옛 앱, 스토어 판, v10 이후 앱의 폴더를 모두 봅니다.
- **자료마다 경로 표기가 다릅니다.** 경로 한 가지로만 찾지 말고 `*.exb` 파일 이름으로 찾습니다.
- **표·열 이름은 후보입니다.** 한 구현이 읽는 이름을 그대로 보고서에 쓰지 않습니다.
- **시각 변환식은 검증하고 씁니다.** 조사 중 직접 만든 노트나 로그의 시각처럼 답을 아는 값으로 맞춰 봅니다.
- **v10 이후 구조는 실제 데이터로 확인합니다.** 그 폴더에서 노트가 든 파일은 파일마다 형식을 보고 찾습니다.
- **경로는 2021년 11월 기준입니다.** 그 뒤 판에서는 달라졌을 수 있습니다.
- **지운 노트가 DB 파일 안에 조각으로 남을 수 있습니다.** SQLite 의 빈 페이지와 빈 블록에서 찾는 법은 [파일 안에 남은 지운 레코드](../../01-foundations/database-log-formats/sqlite/freelist-freeblock.md) 에 있습니다.
- **곁 파일을 함께 모읍니다.** `.exb` 와 이름이 같은 `-wal`·`-journal` 파일이 있으면 같이 둡니다([WAL과 롤백 저널](../../01-foundations/database-log-formats/sqlite/wal-journal-shm.md)).

## 직접 분석해 보기

### 헥스로 한 번

1. `Databases` 폴더를 사본으로 뜹니다. 분석은 사본에서만 합니다.
2. `.exb` 를 헥스 편집기로 열어 맨 앞이 SQLite 머리 문자열인지 봅니다.
3. 조사 대상 노트 제목 하나를 검색합니다. 찾은 자리가 사용 중인 페이지인지, 빈 페이지인지 봅니다. 빈 페이지이면 지운 레코드의 조각일 수 있습니다.
4. 날짜 열 값이 8바이트 실수로 저장돼 있으면, 그 값을 위 식으로 바꿉니다. SQLite 레코드 안의 값 종류(정수·실수·텍스트)를 읽는 법은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에 있습니다.

### 공개 도구로 한 번

- KAPE 대상 `Evernote` 로 옛 앱의 `Databases` 폴더를 모읍니다. 스토어 판과 v10 이후 폴더는 수집 범위에 들어 있는지 따로 확인합니다.
- SQLite 명령줄 도구(sqlite3) 같은 공개 도구로 `.exb` 를 엽니다. `.tables` 로 표 목록을 봅니다.
- 후보 표 `note_attr` 가 있으면 아래처럼 뽑아 봅니다. 열 이름은 `.schema note_attr` 로 먼저 확인합니다.

```sql
SELECT uid, title, author, notebook,
       datetime(date_created * 86400 - 62135683200, 'unixepoch') AS created,
       datetime(date_updated * 86400 - 62135683200, 'unixepoch') AS updated,
       datetime(date_deleted * 86400 - 62135683200, 'unixepoch') AS deleted
FROM note_attr;
```

- 결과 시각 하나를 위 헥스 절차로 직접 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 설치 프로그램 | 데스크톱 앱이 설치된 적이 있는지 봅니다 | [설치 프로그램](../system-account/uninstall.md) |
| 스토어 앱 설치 목록 | 스토어 판이 설치된 적이 있는지 봅니다 | [스토어 앱 설치 목록](../system-account/appx-staterepository.md) |
| 프리페치 | 에버노트 실행 시각을 로그의 시작 시각과 맞춰 봅니다 | [프리페치](../execution/prefetch/index.md) |
| 시간대 설정 | 로그 파일 이름의 날짜와 DB 시각의 시간대를 정합니다 | [시간대 설정](../system-account/time-zone.md) |
| 섀도 복사본 활용 | 예전 시점의 `.exb` 와 비교해 지운 노트를 찾습니다 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 누구와 연락을 주고받았나 | 공유 정보를 다른 연락 흔적과 묶어 봅니다 | [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) |

## 실습

에버노트가 깔린 공개 시험 데이터(NIST CFReDS 등)를 구해 아래 질문을 풀어 봅니다.

1. 옛 앱, 스토어 판, v10 이후 앱 가운데 어느 판의 폴더가 있습니까?
2. `Databases` 폴더의 `.exb` 파일 이름은 무엇입니까? `.accounts` 의 사용자 이름과 같습니까?
3. `.exb` 의 표 목록을 뽑습니다. `note_attr` 와 `resource_attr` 가 있습니까? 없으면 노트가 들어 있는 표는 무엇입니까?
4. 노트 하나의 만든 시각 값을 위 식으로 바꿉니다. 그 날짜에 로그 파일이 있습니까?
5. 지운 시각 열에 값이 있는 노트는 몇 개입니까?
6. 위치 정보가 있는 노트가 있습니까? 그 노트의 작성자 열은 무엇입니까?

## 참고 문헌

1. Eric Zimmerman 외, KapeFiles GitHub 저장소 (커밋 ed0f9c7), `Targets/Apps/Evernote.tkape` — https://github.com/EricZimmerman/KapeFiles
2. Forensafe, "Investigating Evernote" 블로그 (2021-11-22) — https://www.forensafe.com/blogs/evernote.html
