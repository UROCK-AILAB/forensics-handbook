# 카카오톡 PC (KakaoTalk PC)

## 한 줄 요약

카카오톡 PC 는 Windows 사용자마다 `C:\Users\<사용자>\AppData\Local\Kakao\KakaoTalk\` 폴더에 데이터를 남깁니다(논문).
그 아래 `users\` 에는 카카오톡 계정별 폴더가 있고, 이 폴더에 대화·연락처·계정 정보·받은 사진이 모입니다.
대화 기록 파일의 확장자는 `.edb` 이지만 형식은 SQLite 입니다.
대화 DB 는 카카오톡 버전과 상태에 따라 평문일 때도 있고 암호문일 때도 있습니다.

## 왜 중요한가

- 대화 DB 에는 대화방마다 메시지와 보낸 사람 ID, 시각이 남습니다. 누구와 무엇을 주고받았는지 볼 때 이 파일이 중심입니다.
- 레지스트리와 계정 폴더의 파일에는 이 기기에서 쓴 계정의 흔적이 남습니다. 이 흔적으로 어느 계정을 언제쯤 썼는지 가늠합니다.
- 받은 사진과 섬네일은 `.cng` 파일로 따로 남습니다. 대화 DB 와 별개로 이미지를 주고받은 흔적을 볼 수 있습니다.
- 카카오톡 버전에 따라 대화 DB 암호화 방식이 바뀝니다. 그래서 버전과 파일 상태를 먼저 확인해야 읽는 방법을 고를 수 있습니다.
- 카카오톡의 `.edb` 는 Windows 검색 색인 같은 ESE 파일과 확장자만 같습니다. ESE 도구로 열면 실패하므로 SQLite 로 엽니다.

증명하지 못하는 것도 있습니다.

- 대화 DB 가 평문으로 남아 있어도 "카카오톡은 원래 평문으로 저장한다" 고 단정하지 않습니다. 그 PC 가 특정 시점에 방식을 바꾸던 중이었을 수 있습니다.
- 레지스트리 키 이름과 파일 시각은 마지막으로 고친 때일 수 있습니다. 이 값을 첫 로그인 순간이라고 단정하지 않습니다.
- 백업 파일과 `-wal` 파일은 특정 시점까지만 담습니다. 여기서 나온 메시지를 대화 전체라고 말하지 않습니다.

## 한눈에 보기

> 그림 자리: `KakaoTalk\users\<계정 폴더>\` 아래의 DB(`chatLogs_*`·`chatListInfo`·`TalkUserDB`·`ActionLogDB`)와 짝 파일(`-wal`·`-shm`), 상태 파일(`profile.dat`·`appstate.dat`·`login_list.dat`·`last_pc_login.dat`), `chat_data\` 백업 폴더, 레지스트리 `DeviceInfo\<DATE>` 키를 나무 모양으로 보여 주는 그림

### 위치

| 항목 | 위치 | 근거 |
|---|---|---|
| 데이터 기본 폴더 | `C:\Users\<사용자>\AppData\Local\Kakao\KakaoTalk\` | 논문 |
| 계정별 폴더 | `...\KakaoTalk\users\<계정 폴더>\` | 논문 |
| 계정 폴더 이름 | 40자 16진수 문자열이었습니다 | 관찰 |
| 기기 정보 | `HKEY_CURRENT_USER\SOFTWARE\Kakao\KakaoTalk\DeviceInfo\<DATE>` | 논문, 관찰 |
| 프로그램 설치 폴더 | 이번 자료로 확정하지 못했습니다 | — |

"관찰" 로 적은 칸의 확인 범위는 카카오톡 PC 26.6.0.5208, Windows 11 한 대입니다.
다른 PC 와 다른 버전에서는 다를 수 있습니다.

### 버전에 따라 달라지는 점

Windows 버전에 따른 차이는 이번 자료로 확인하지 못했습니다.
차이를 가르는 기준은 카카오톡 버전입니다.

| 카카오톡 버전 | 대화 DB 상태 | 근거 |
|---|---|---|
| 25.7.2 미만 | 카카오톡 자체 모듈 EvaSQLite 로 암호화합니다 | 논문 |
| 25.7.2 이상 | SQLCipher 4 로 암호화합니다 | 논문 |
| 26.6.0.5208 | 활성 `chatLogs_*.edb` 여러 개가 평문 SQLite 였습니다. 연락처 DB 등 일부는 암호문이었습니다 | 관찰 (Windows 11 한 대) |

표의 버전 경계와 실제 파일 상태는 다를 수 있습니다.
그래서 버전만 믿지 않고 파일 머리를 직접 봅니다.
평문과 암호문을 가르는 법은 [대화 DB 암호화와 버전별 차이](/02-artifacts/messengers/kakaotalk-pc/chat-db-encryption.md) 에서 다룹니다.

### 알려 주는 것

| 알 수 있는 것 | 어디에 남나 (계정 폴더 기준) | 형식 | 자세히 |
|---|---|---|---|
| 대화방별 메시지·보낸 사람 ID·시각 | `chatLogs_<대화방 식별자>.edb` | SQLite (평문 또는 암호문) | [대화 DB 암호화와 버전별 차이](/02-artifacts/messengers/kakaotalk-pc/chat-db-encryption.md) |
| 대화방 목록 | `chatListInfo.edb` | SQLite | [설치 위치와 파일 구성](/02-artifacts/messengers/kakaotalk-pc/install-paths-files.md) |
| 연락처 (친구) | `TalkUserDB.edb` | SQLite | [설치 위치와 파일 구성](/02-artifacts/messengers/kakaotalk-pc/install-paths-files.md) |
| 행동 로그와 계정 userId | `ActionLogDB.edb` | SQLite | [계정·로그인 흔적](/02-artifacts/messengers/kakaotalk-pc/account-login.md) |
| 주고받은 사진과 섬네일 | `.cng` 파일 | 암호화한 이미지 파일 | [받은 파일·사진 폴더](/02-artifacts/messengers/kakaotalk-pc/received-files.md) |
| 로그인했던 이메일 | `login_list.dat`, `last_pc_login.dat` | 상태 파일 (관찰) | [계정·로그인 흔적](/02-artifacts/messengers/kakaotalk-pc/account-login.md) |
| 기기 정보와 계정 설정 시기 단서 | 레지스트리 `DeviceInfo\<DATE>` | 레지스트리 키 | [계정·로그인 흔적](/02-artifacts/messengers/kakaotalk-pc/account-login.md) |
| 대화방별 예전 대화 | `chat_data\chatLogs_<대화방 식별자>.edb_<YYYYMMDD>_<HHMMSS>.backup` | 평문 SQLite (관찰) | [대화 DB가 안 열릴 때 남는 단서](/02-artifacts/messengers/kakaotalk-pc/when-db-wont-open.md) |
| 본 DB 에 아직 합치지 않은 최근 변경 | `*.edb-wal`, `*.edb-shm` | SQLite 쓰기 전 로그 (WAL) | [대화 DB가 안 열릴 때 남는 단서](/02-artifacts/messengers/kakaotalk-pc/when-db-wont-open.md) |

## 읽는 순서

1. [설치 위치와 파일 구성 (Install Paths·Files)](/02-artifacts/messengers/kakaotalk-pc/install-paths-files.md) — 데이터 폴더와 계정 폴더의 위치, 그 안의 DB 와 상태 파일을 정리합니다. 확장자 `.edb` 를 ESE 와 헷갈리지 않는 법도 다룹니다.
2. [대화 DB 암호화와 버전별 차이 (Chat DB Encryption)](/02-artifacts/messengers/kakaotalk-pc/chat-db-encryption.md) — 버전별 암호화 방식과 평문·암호문을 가르는 법을 다룹니다. 전원을 끈 디스크만으로 대화 DB 가 읽히는지도 봅니다.
3. [받은 파일·사진 폴더 (Received Files)](/02-artifacts/messengers/kakaotalk-pc/received-files.md) — 받은 파일과 `.cng` 이미지·섬네일이 어디에 어떻게 남는지 봅니다. 파일 시각과 메시지 시각을 맞춰 보는 법도 다룹니다.
4. [계정·로그인 흔적 (Account·Login)](/02-artifacts/messengers/kakaotalk-pc/account-login.md) — 레지스트리 기기 정보, 로그인 파일, userId 로 이 기기에서 쓴 계정을 찾습니다. 시각이 말해 주는 범위도 다룹니다.
5. [대화 DB가 안 열릴 때 남는 단서 (메모리·캐시·이미지)](/02-artifacts/messengers/kakaotalk-pc/when-db-wont-open.md) — 암호화한 대화 DB 를 못 열 때 볼 평문 백업, `.cng`, `ActionLogDB.edb`, `-wal` 파일, 메모리 이미지를 다룹니다. 각 단서가 담는 범위도 밝힙니다.

## 함께 볼 페이지

- [SQLite 데이터베이스 (SQLite)](/01-foundations/database-log-formats/sqlite/index.md) — 카카오톡 `.edb` 의 실제 저장 형식입니다.
- [ESE 데이터베이스 (Extensible Storage Engine)](/01-foundations/database-log-formats/extensible-storage-engine/index.md) — 확장자 `.edb` 가 같은 다른 형식입니다. 둘을 가를 때 봅니다.
- [레지스트리 하이브 구조 (Registry Hive)](/01-foundations/database-log-formats/registry-hive/index.md) — `DeviceInfo\<DATE>` 키를 읽을 때 필요한 구조입니다.
- [암호화 증거 다루기 (Encrypted Evidence)](/03-techniques/analysis/encrypted-evidence/index.md) — 암호문으로 남은 증거를 다루는 일반 절차입니다.
- [메모리 분석 (Memory Forensics)](/03-techniques/analysis/memory-forensics/index.md) — 메모리 이미지에 남을 수 있는 단서를 다룹니다.
- [누구와 연락을 주고받았나 (Communication Reconstruction)](/04-scenarios/activity/communication-reconstruction.md) — 여러 메신저와 메일 기록을 묶어 연락 관계를 되짚는 순서입니다.
- [그 시각에 PC 를 쓴 사람이 누구인가 (User Attribution)](/04-scenarios/activity/user-attribution.md) — 계정 흔적을 실제 사용자와 이어 볼 때 봅니다.

## 참고 문헌

- 논문: 카카오톡 PC 포렌식 연구 논문(EvaSQLite·SQLCipher, 버전 경계, 파일·레지스트리 경로), KoreaScience — https://www.koreascience.kr/article/JAKO202530836043843.page
- SQLite WAL 문서: SQLite, "Write-Ahead Log" 파일 형식(-wal·-shm 의 뜻과 이름 규칙), SQLite.org — https://www.sqlite.org/walformat.html
