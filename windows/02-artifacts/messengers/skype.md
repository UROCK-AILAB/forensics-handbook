---
title: "스카이프"
parent: "아티팩트 · 메신저"
nav_order: 2050
---

# 스카이프 (Skype)

> 위치: 아티팩트 사전 > 메신저

## 한 줄 요약

Skype 서비스는 2025-05-05 에 끝났습니다. 클라우드에서 데이터를 내보내는 기한도 2026-06-15 로 지났습니다. 그래서 지금 조사할 수 있는 것은 옛 PC 와 디스크 이미지에 남은 로컬 파일입니다. 옛 Skype 의 `main.db` 는 SQLite 파일이고, 계정·대화·통화·SMS·파일 전송 기록이 표로 남습니다. 공개 파서 plaso 는 이 파일의 시각을 모두 1970-01-01 UTC 부터 센 초로 풉니다.

관찰 PC 에는 Skype 폴더가 없었습니다. 이 페이지에는 "관찰" 항목이 없습니다.

## 무엇을 기록하나 · 왜 생기나

### 서비스 종료

Microsoft 지원 문서는 아래처럼 적었습니다. (Microsoft Support)

2025-05-05 부로 Skype 는 종료되었습니다. Skype 계정으로 무료 Teams 에 로그인하면 대화와 연락처가 자동으로 옮겨지고, 새 계정은 필요 없으며 동기화는 1분이 안 걸린다고 적었습니다.

아래 대화는 옮겨지지 않습니다.
  - Skype 와 Teams 업무 계정 사이의 대화
  - Skype 와 Skype for Business 사이의 기록
  - 자기 자신과의 대화
  - 비공개 (private) 대화
내보내기 포털은 `secure.skype.com/en/data-export` 이고 "Available Exports" 에서 받으며, 큰 파일은 최대 30일 걸릴 수 있습니다. 내보내기 기한은 2026-06-15 이고, 2026-04-01 이후에 내보낸 데이터는 불완전할 수 있습니다.

2024-12 ~ 2025-02 에 활동했고 2025-12-01 전에 무료 Teams 를 쓴 사용자는 접근이 유지되지만, 나머지 사용자의 데이터는 2026-06-15 뒤 모두 지워집니다.

같은 문서에 "Your Skype data will be available until January 2026" 이라는 문장도 있는데 위 날짜와 맞지 않습니다. 이 페이지는 2026-06-15 를 최종 기한으로 봅니다.

해석: 이 글을 쓴 2026년 9월 기준으로 클라우드 내보내기 기한은 지났습니다. 조사 대상은 세 곳입니다.

1. 옛 PC·디스크 이미지에 남은 Skype 로컬 파일
2. 사용자가 기한 전에 내려받아 둔 내보내기 파일. 파일 형식은 확인하지 못했습니다.
3. 무료 Teams 로 옮겨진 대화. [마이크로소프트 팀즈](teams.md) 에서 다룹니다.

### main.db

옛 Skype 는 대화와 통화 기록을 `main.db` 라는 SQLite 파일에 적었습니다. 공개 타임라인 도구 plaso 에 이 파일을 읽는 파서가 있습니다. (plaso skype.py) 아래 표 이름과 칸 이름은 이 파서의 쿼리에서 가져왔습니다.

## 위치와 버전별 차이

Skype 는 세대마다 저장 방식이 달랐습니다. 이 페이지에서 확인한 범위는 아래와 같습니다.

| 세대 | 저장 방식 | 확인한 것 | 확인하지 못한 것 |
|---|---|---|---|
| `main.db` 를 쓰는 판 | SQLite | 표와 칸 이름 (plaso) | 폴더 경로, `main.db` 를 쓴 마지막 버전 |
| 크롬 계열 구조의 판 | Local Storage·IndexedDB 를 LevelDB 로 저장 | CCL 글이 Skype 를 LevelDB 사용 앱으로 들었습니다 | 폴더 경로, 대화가 남는 곳 |
| 스토어 판 | — | — | 패키지 폴더 이름, 안의 DB 이름 |

경로를 확인하지 못했으므로, 이미지에서는 이름으로 찾습니다. `main.db` 라는 이름의 파일을 모두 찾고, 그 가운데 아래 "구조" 의 표 일곱 개가 모두 있는 파일을 Skype DB 로 봅니다.

- 이미지 전체에서 이름으로 찾는 방법은 [마스터 파일 테이블](../filesystem/mft.md) 에서 다룹니다.
- 크롬 계열 구조는 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 와 [LevelDB 저장소](../../01-foundations/database-log-formats/leveldb.md) 에서 다룹니다.
- 설치했던 버전은 [설치 프로그램](../system-account/uninstall.md) 과 [스토어 앱 설치 목록](../system-account/appx-staterepository.md) 에서 확인합니다.

## 구조

plaso 파서는 아래 일곱 표가 있어야 이 파일을 Skype DB 로 읽습니다. (plaso skype.py)

`Accounts`, `Calls`, `CallMembers`, `Chats`, `Messages`, `SMSes`, `Transfers`

표마다 파서가 읽는 칸은 아래와 같습니다. (plaso skype.py) 계정 시각 칸과 통화 시각 칸의 뜻은 plaso 에서 확인했습니다. 나머지 칸의 뜻은 칸 이름으로 짐작한 것이므로, 검체에서 값을 보고 확인합니다.

### 계정 (Accounts)

| 칸 | 뜻 |
|---|---|
| `id`, `fullname`, `given_displayname`, `emails`, `country` | 계정 식별 정보 |
| `profile_timestamp` | 프로필을 바꾼 시각 |
| `authreq_timestamp` | 인증 요청을 받은 시각 |
| `sent_authrequest_time` | 인증 요청을 보낸 시각 |
| `mood_timestamp` | 기분 메시지를 바꾼 시각 |
| `lastonline_timestamp` | 마지막으로 온라인이었던 시각 |
| `lastused_timestamp` | 마지막으로 쓴 시각 |

### 대화 (Chats + Messages)

`Chats` 와 `Messages` 는 `chatname` 칸으로 이어서 읽습니다. 쿼리가 꺼내는 칸은 아래와 같습니다. `id`·`participants`·`friendlyname`·`dialog_partner` 는 `Chats` 의 칸이고, 나머지는 `Messages` 의 칸입니다.

| 칸 | 뜻 |
|---|---|
| `id` | 대화방 번호 |
| `participants` | 대화 참여자 |
| `friendlyname` | 대화방 이름 |
| `author`, `from_dispname` | 보낸 사람의 계정과 표시 이름 |
| `dialog_partner` | 1:1 대화 상대 |
| `body_xml` | 메시지 본문 |
| `timestamp` | 메시지 시각 |

본문 칸 이름은 `body_xml` 입니다. 본문이 어떤 형식으로 적히는지는 확인하지 못했습니다.

### 통화 (Calls + CallMembers)

`Calls` 에서 `id`·`is_incoming`·`begin_timestamp` 를, `CallMembers` 에서 나머지 칸을 읽습니다. (plaso skype.py)

| 칸 | 표 | 뜻 |
|---|---|---|
| `id` | Calls | 통화 번호 |
| `is_incoming` | Calls | 받은 통화인지 건 통화인지 |
| `begin_timestamp` | Calls | 통화를 시도한 시각 |
| `guid`, `call_db_id` | CallMembers | 통화 식별 정보. `call_db_id` 로 `Calls` 와 잇습니다 |
| `start_timestamp` | CallMembers | 통화가 연결(수락)된 시각 |
| `call_duration` | CallMembers | 통화 길이 |
| `videostatus` | CallMembers | 영상 통화 상태 |

### SMS (SMSes)

| 칸 | 뜻 |
|---|---|
| `id` | 번호 |
| `target_numbers` | 받는 전화번호 |
| `timestamp` | 시각 |
| `body` | 본문 |

### 파일 전송 (Transfers)

| 칸 | 뜻 |
|---|---|
| `partner_handle`, `partner_dispname` | 상대 계정과 표시 이름 |
| `offer_send_list` | 보내기 대상 목록으로 보입니다 |
| `starttime`, `accepttime`, `finishtime` | 칸 이름으로 보아 전송을 시작한·수락한·끝낸 시각입니다 |
| `filepath`, `filename`, `filesize` | 파일 경로·이름·크기 |
| `status` | 전송 상태. 값의 뜻은 확인하지 못했습니다 |
| `id`, `parent_id`, `pk_id` | 식별 정보 |

SQLite 파일을 읽는 법과 지운 레코드가 남는 곳은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

- **계정.** `Accounts` 는 이 PC 에서 쓴 Skype 계정의 이름·메일·국가를 알려 줍니다.
- **대화 상대와 메시지.** `Messages` 는 누가 어느 대화방에 언제 무엇을 적었는지 기록합니다.
- **통화.** `Calls` 와 `CallMembers` 는 통화 방향, 시도·연결 시각, 길이를 알려 줍니다.
- **SMS.** `SMSes` 는 Skype 로 보낸 SMS 의 받는 번호와 본문을 알려 줍니다.
- **파일 전송.** `Transfers` 는 상대, 파일 이름, 경로, 크기, 전송 시각을 알려 줍니다.
- **계정 활동 시각.** 인증 요청을 받고 보낸 때, 프로필 변경, 기분 메시지 변경, 마지막 온라인, 마지막 사용 시각이 남습니다.

### 증명하지 못하는 것

- **전송이 끝났는지.** `status` 값의 뜻을 확인하지 못했습니다. `finishtime` 이 채워져 있는지와 대상 경로에 파일이 있는지를 함께 봅니다.
- **메시지를 읽었는지.** 읽음 여부를 가리는 칸은 이 페이지에서 확인하지 못했습니다.
- **누가 자판 앞에 있었는지.** 계정까지만 알려 줍니다. 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.
- **Skype 를 쓰지 않았다는 것.** `main.db` 가 없어도 크롬 계열 구조의 판이나 스토어 판을 썼을 수 있습니다.
- **계정의 전체 대화.** 이 PC 의 `main.db` 가 계정의 모든 대화를 담았다고 볼 수 없습니다. Teams 로 옮겨진 대화와 비교해 빠진 부분을 적습니다.

보고서에는 "피의자가 파일을 넘겼다" 가 아니라 이렇게 씁니다. "`main.db` 의 `Transfers` 표에 상대 계정 X 와 파일 이름 Y 가 있는 행이 있다. 이 행의 `starttime` 은 2020-09-13 21:26:40(KST) 이다." 값은 설명을 위한 예입니다.

## 시각 해석

plaso 는 이 파일의 시각 칸을 모두 POSIX 초, 곧 1970-01-01 00:00:00 UTC 부터 센 초로 풉니다. (plaso skype.py) 값은 UTC 기준이라서 현지 시각으로 옮길 때는 [시간대 설정](../system-account/time-zone.md) 을 확인합니다.

- 형식은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

| 칸 | 알려 주는 때 |
|---|---|
| `Messages.timestamp` | 메시지 시각 |
| `Calls.begin_timestamp` | 통화를 시도한 시각 (plaso) |
| `CallMembers.start_timestamp` | 통화가 연결된 시각 (plaso). 여기에 `call_duration` 을 더하면 끝난 때를 짐작할 수 있습니다 |
| `Transfers.starttime`, `accepttime`, `finishtime` | 파일 전송 단계별 시각 |
| `Accounts` 의 `*_timestamp`·`sent_authrequest_time` | 계정 활동 시각 |
| `main.db` 파일의 파일 시스템 시각 | 앱이 파일을 마지막으로 고친 때의 단서 |

## 함정과 한계

- **클라우드에서 받으려 합니다.** 내보내기 기한이 지났습니다. 사용자 PC 에 받아 둔 내보내기 파일이 있는지 찾습니다.
- **Teams 로 모두 옮겨졌다고 봅니다.** 비공개 대화, 자기 자신과의 대화, 업무 계정·Skype for Business 와의 대화는 옮겨지지 않습니다. 이런 대화는 옛 `main.db` 에만 남았을 수 있습니다.
- **지원 문서의 날짜를 하나만 옮깁니다.** 같은 문서에 2026년 1월과 2026-06-15 가 함께 나옵니다. 보고서에 인용할 때는 문서 표현을 그대로 옮기고 어긋남을 밝힙니다.
- **경로 하나만 봅니다.** 판마다 저장 방식과 위치가 다릅니다. 이름과 표 구성으로 넓게 찾습니다.
- **원본 DB 를 엽니다.** 늘 사본에서 작업합니다.
- **`status` 를 짐작해 풉니다.** 값의 뜻을 확인하지 못했습니다. 다른 흔적과 맞춰 본 뒤에만 뜻을 적습니다.
- **시각을 현지 시각으로 읽습니다.** 값은 UTC 기준 초입니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 명세와 POSIX 시각 정의로 만든 예시입니다. 실제 검체에서 나온 값이 아닙니다.

1. 후보 `main.db` 의 첫 16바이트가 SQLite 머리인지 봅니다.

   ```
   오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
   0x00   53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
   ```

2. 사본을 SQLite 도구로 열어 표 일곱 개가 모두 있는지 봅니다.
3. 시각 칸 값 하나를 손으로 풉니다. 예를 들어 값이 `1600000000` 이면 16진수로 `5F 5E 10 00` 입니다.
4. 이 값은 1970-01-01 00:00:00 UTC 에서 1,600,000,000초 뒤입니다. 곧 2020-09-13 12:26:40 UTC 입니다.
5. 시간대가 KST(UTC+9)이면 2020-09-13 21:26:40 입니다.
6. 도구가 보여 준 시각과 손으로 푼 시각이 같은지 확인합니다.

### 공개 도구로 한 번

공개 도구의 예로 plaso 가 있습니다. plaso 의 Skype 파서는 위 일곱 표를 읽어 타임라인 사건으로 바꿉니다. (plaso skype.py)

파서가 읽는 칸은 위 표에 적은 칸뿐이고, 다른 칸은 SQLite 도구로 따로 봅니다. 도구가 낸 메시지 수와 `Messages` 표의 행 수를 맞춰 보고, 차이가 나면 SQL 로 직접 셉니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 점 |
|---|---|
| [마이크로소프트 팀즈](teams.md) | 무료 Teams 로 옮겨진 대화가 있는지 봅니다 |
| [설치 프로그램](../system-account/uninstall.md) | Skype 를 설치·제거한 기록을 봅니다 |
| [프리페치](../execution/prefetch/index.md) | Skype 실행 시각을 봅니다 |
| [다운로드 출처 표시](../filesystem/zone-identifier.md) | `Transfers.filepath` 의 파일에 출처 표시가 붙었는지 봅니다 |
| [바로가기 파일](../file-folder-usage/lnk.md) | 전송한 파일을 연 흔적이 있는지 봅니다 |
| [볼륨 섀도 복사본 구조](../../01-foundations/disk-volume/volume-shadow-copy.md) | 예전 시점의 `main.db` 가 남았는지 봅니다 |

조사 전체 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 와 [이 파일은 어디서 왔나](../../04-scenarios/activity/file-origin.md) 에서 다룹니다.

## 실습

서비스가 끝나서 새로 검체를 만들 수 없고, Skype 가 들어간 공개 검체도 이 페이지에서 확인하지 못했습니다. 예전에 만든 검체나 가상 머신 스냅숏이 있으면 아래 질문으로 풀어 봅니다.

1. 이미지에서 `main.db` 라는 이름의 파일은 몇 개입니까? 그 가운데 표 일곱 개가 모두 있는 파일은 몇 개입니까?
2. `Accounts` 의 `lastused_timestamp` 를 손으로 풀면 언제입니까? 도구의 결과와 같습니까?
3. `Transfers` 에서 `finishtime` 이 비어 있는 행이 있습니까? 그 행의 `status` 값은 무엇입니까?
4. `Transfers.filepath` 의 파일이 디스크에 아직 있습니까? 그 파일의 파일 시스템 시각은 `finishtime` 과 얼마나 차이 납니까?
5. 같은 사용자의 Teams 폴더에 옮겨진 대화가 있습니까? `main.db` 에만 있는 대화는 무엇입니까?

## 참고 문헌

- Microsoft Support, "Skype is retiring in May 2025: What you need to know" — https://support.microsoft.com/en-us/skype/skype-is-retiring-in-may-2025-what-you-need-to-know-2a7d2501-427f-485e-8be0-2068a9f90472
- log2timeline, plaso — `plaso/parsers/sqlite_plugins/skype.py` — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/sqlite_plugins/skype.py
- CCL Solutions Group, "Hang on! That's not SQLite! Chrome, Electron and LevelDB" — https://www.cclsolutionsgroup.com/post/hang-on-thats-not-sqlite-chrome-electron-and-leveldb
