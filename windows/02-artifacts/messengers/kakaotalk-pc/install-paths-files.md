---
title: "설치 위치와 파일 구성"
parent: "카카오톡 PC"
grand_parent: "아티팩트 · 메신저"
nav_order: 1990
---

# 설치 위치와 파일 구성 (Install Paths·Files)

> 위치: [카카오톡 PC (KakaoTalk PC)](index.md) > 설치 위치와 파일 구성

## 한 줄 요약

카카오톡 PC 는 Windows 사용자마다 `AppData\Local\Kakao\KakaoTalk\` 폴더에 데이터를 남기고, 그 아래 `users\` 에는 카카오톡 계정별 폴더가 있습니다.
계정 폴더에는 대화·대화방 목록·연락처·행동 로그 DB 와 계정 상태 파일이 있습니다.
DB 확장자는 `.edb` 이지만 형식은 SQLite 입니다.

## 무엇을 기록하나 · 왜 생기나

카카오톡 PC 는 대화, 연락처, 계정 정보, 받은 파일을 사용자별 데이터 폴더에 저장합니다(논문).
대화와 연락처는 SQLite 계열 DB 에 들어가고, 계정과 앱 상태는 몇 개의 `.dat` 파일에 들어갑니다.
이 페이지는 어느 파일이 어디 있는지만 정리하고, 파일마다 내용을 읽는 법은 표의 링크에서 다룹니다.

## 위치와 버전별 차이

### 데이터 폴더

| 경로 | 뜻 | 근거 |
|---|---|---|
| `C:\Users\<사용자>\AppData\Local\Kakao\KakaoTalk\` | Windows 사용자별 데이터 기본 폴더 | 논문 |
| `C:\Users\<사용자>\AppData\Local\Kakao\KakaoTalk\users\<계정 폴더>\` | 카카오톡 계정별 폴더 | 논문 |

- `<사용자>` 는 Windows 사용자 프로필 폴더 이름입니다. 이 폴더가 어느 Windows 계정의 것인지는 [사용자 프로필 목록](../../system-account/profilelist.md) 에서 확인합니다.
- `<계정 폴더>` 이름은 40자리 16진수 문자열이었습니다(카카오톡 PC 26.6.0.5208 기준).
- 이 이름이 무엇을 가리키는지는 [계정·로그인 흔적](account-login.md) 에서 다룹니다.

### 프로그램 설치 폴더

실행 파일이 깔리는 폴더는 이번에 연 자료로 확정하지 못해서 이 페이지에는 경로를 적지 않습니다.
설치 흔적은 [설치 프로그램](../../system-account/uninstall.md) 에서 찾아봅니다.

### 버전별 차이

논문은 25.7.2 이상으로 업데이트하면 계정 폴더 이름이 `<계정 폴더>_backup_<백업 시각>` 으로 바뀐다고 적습니다.
이 백업 시각은 UTC+0 기준입니다(논문).
그래서 `users\` 아래에 이 이름의 폴더가 있으면 업데이트 전 데이터가 남은 것일 수 있습니다.
그 밖에 데이터 폴더 위치가 카카오톡 버전이나 Windows 버전에 따라 바뀌는지는 확인하지 못했습니다.
이 페이지의 관찰은 Windows 11 한 대에서만 했습니다.
카카오톡 버전에 따라 달라진다고 확인한 것은 대화 DB 의 암호화 방식입니다.
경계가 되는 버전은 [대화 DB 암호화와 버전별 차이](chat-db-encryption.md) 에 정리했습니다.

## 구조

### 계정 폴더 안의 파일

```
KakaoTalk\users\<계정 폴더>\
├─ chatLogs_<대화방 식별자>.edb        (대화방마다 하나)
├─ chatListInfo.edb
├─ TalkUserDB.edb
├─ ActionLogDB.edb
├─ <DB 이름>.edb-wal, <DB 이름>.edb-shm   (DB 마다 한 쌍)
├─ profile.dat
├─ appstate.dat
├─ last_pc_login.dat
├─ login_list.dat
└─ chat_data\
   └─ chatLogs_<대화방 식별자>.edb_<YYYYMMDD>_<HHMMSS>.backup
```

| 파일 | 담는 것 | 근거 | 자세히 |
|---|---|---|---|
| `chatLogs_<대화방 식별자>.edb` | 대화방 하나의 대화 기록 | 논문, 관찰 | [대화 DB 암호화와 버전별 차이](chat-db-encryption.md) |
| `chatListInfo.edb` | 대화방 목록과 방 정보 | 논문 | — |
| `TalkUserDB.edb` | 연락처(친구) 정보 | 논문, 관찰 | — |
| `ActionLogDB.edb` | 사용자 행동 로그와 userId | 논문 | [계정·로그인 흔적](account-login.md) |
| `*.edb-wal`, `*.edb-shm` | 위 DB 의 쓰기 전 로그와 그 색인 | SQLite WAL 문서, 관찰 | [대화 DB가 안 열릴 때 남는 단서](when-db-wont-open.md) |
| `profile.dat` | 키로 감싼 계정 키 재료 | 관찰 | [계정·로그인 흔적](account-login.md) |
| `appstate.dat` | 앱 상태 | 관찰 | [계정·로그인 흔적](account-login.md) |
| `last_pc_login.dat`, `login_list.dat` | 로그인 흔적 | 관찰 | [계정·로그인 흔적](account-login.md) |
| `chat_data\` 의 `.backup` | 대화방별 백업 | 관찰 | [대화 DB가 안 열릴 때 남는 단서](when-db-wont-open.md) |

근거 칸의 "관찰" 은 카카오톡 PC 26.6.0.5208 이 깔린 Windows 11 한 대에서 본 것입니다.
다른 PC·버전에서 같다고 보장하지 못합니다.

- `chat_data\` 의 백업 파일은 있을 수도 있고 없을 수도 있습니다.
- 받은 사진과 섬네일은 계정 폴더 아래에 암호화된 `.cng` 파일로 남습니다. 자세한 내용은 [받은 파일·사진 폴더](received-files.md) 에서 다룹니다.

### 확장자 `.edb` 를 헷갈리지 않기

Windows 검색 색인 `Windows.edb` 와 브라우저 캐시 `WebCacheV01.dat` 는 Microsoft ESE 형식입니다. ESE 는 [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다.
카카오톡의 `.edb` 는 ESE 와 확장자만 같습니다.
실제 형식은 SQLite 이거나 암호화한 SQLite 입니다(논문).
둘을 가리는 법은 [대화 DB 암호화와 버전별 차이](chat-db-encryption.md) 에 있습니다.

### 쓰기 전 로그 보조 파일

SQLite 는 쓰기 전 로그 (Write-Ahead Log, WAL) 방식에서 주 파일 옆에 `-wal`·`-shm` 파일을 둡니다.
두 파일의 이름은 주 파일 이름 뒤에 `-wal`·`-shm` 을 붙인 것입니다(SQLite WAL 문서).
예를 들어 `TalkUserDB.edb` 의 짝은 `TalkUserDB.edb-wal` 과 `TalkUserDB.edb-shm` 입니다.
카카오톡 PC 26.6.0.5208 에서는 DB 마다 두 파일이 함께 있었습니다.
두 파일을 함께 봐야 하는 이유는 [대화 DB가 안 열릴 때 남는 단서](when-db-wont-open.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것**

- 그 Windows 사용자 프로필에 카카오톡 PC 데이터 폴더가 있다는 사실
- 어떤 계정 폴더·DB·상태 파일이 남아 있는지

**증명하지 못하는 것**

- 폴더가 있어도 대화를 읽을 수 있다는 보장은 없습니다. DB 가 암호문일 수 있습니다.
- 폴더와 파일 목록만으로는 언제, 얼마나 오래 썼는지 알 수 없습니다.
- 파일이 없다고 처음부터 없었다고 말할 수 없습니다. 지웠는지는 [지운 파일의 흔적 찾기](../../../04-scenarios/activity/deleted-file-traces.md) 방법으로 따로 확인합니다.

## 시각 해석

폴더·파일의 파일 시스템 시각과 레지스트리 `DeviceInfo\<DATE>` 하위 키 이름으로 계정을 설정하거나 로그인한 시기를 가늠합니다.
어느 시각이 무엇을 뜻하는지는 [계정·로그인 흔적](account-login.md) 에서 다룹니다.

## 함정과 한계

- `.edb` 를 ESE 로 알고 ESE 도구로 열면 실패합니다. SQLite 로 엽니다.
- 주 DB 만 수집하면 `-wal` 에만 있는 최근 기록을 놓칩니다. 계정 폴더를 통째로 수집합니다.
- `chat_data\` 같은 하위 폴더도 함께 수집합니다.
- 파일 구성은 한 대·한 버전에서 본 것입니다. 다른 버전에서 이름과 구성이 같다고 보장하지 못합니다.

## 직접 분석해 보기

### 헥스로 한 번

`.edb` 파일마다 첫 16바이트를 봅니다.
평문 SQLite 인지 암호문인지 여기서 갈립니다.
명세로 만든 헥스 예시와 한꺼번에 가리는 스크립트는 [대화 DB 암호화와 버전별 차이](chat-db-encryption.md) 에 있습니다.

### 공개 도구로 한 번

1. 증거 이미지에서 `KakaoTalk\` 폴더를 통째로 내보냅니다. `-wal`·`-shm` 과 하위 폴더까지 함께 내보냅니다.
2. 계정 폴더마다 위 표의 파일이 있는지 적습니다.
3. 파일마다 크기와 파일 시스템 시각을 함께 적습니다. 시각의 뜻은 [마스터 파일 테이블](../../filesystem/mft.md) 에서 다룹니다.
4. 평문 SQLite 로 확인한 파일만 사본으로 엽니다. `sqlite3` 명령행 셸 같은 공개 도구를 씁니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [사용자 프로필 목록](../../system-account/profilelist.md) | `C:\Users\<사용자>` 가 어느 Windows 계정의 폴더인지 |
| [설치 프로그램](../../system-account/uninstall.md) | 카카오톡 PC 설치 흔적 |
| [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md) | 카카오톡 PC 를 실행한 흔적과 시각 |
| [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) | `.edb` 안의 SQLite 구조 |

## 실습

카카오톡 PC 가 든 공개 검체는 이번에 확인하지 못했습니다.
시험용 PC 에 카카오톡 PC 를 깔고 아래 질문을 풀어 봅니다.

1. `users\` 아래 계정 폴더 이름은 몇 자리입니까? 다른 계정으로 로그인하면 폴더가 하나 더 생깁니까?
2. `.edb` 파일마다 `-wal`·`-shm` 이 있습니까? 카카오톡을 끄면 두 파일 크기가 어떻게 바뀝니까?
3. 메시지를 몇 개 주고받은 뒤 어느 파일의 수정 시각이 바뀝니까?
4. `chat_data\` 에 `.backup` 파일이 생깁니까? 파일 이름의 날짜·시각은 무엇과 맞습니까?

## 참고 문헌

- 논문: 카카오톡 PC 포렌식 연구 논문(EvaSQLite·SQLCipher, 파일·레지스트리 경로), KoreaScience — https://www.koreascience.kr/article/JAKO202530836043843.page
- SQLite WAL 문서: SQLite, "Write-Ahead Log" 파일 형식(-wal·-shm 의 뜻과 이름 규칙), SQLite.org — https://www.sqlite.org/walformat.html
