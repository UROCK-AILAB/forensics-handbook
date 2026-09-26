---
title: "인스타그램"
parent: "아티팩트 · 메신저"
nav_order: 890
---

# 인스타그램 (Instagram)

인스타그램 다이렉트 메시지(DM)는 `DirectSQLiteDatabase` 폴더의 SQLite DB 에 남고, 대화방은 `THREADS` 표에, 메시지는 `MESSAGES` 표에 들어 있지만 본문·보낸 사람·시각은 `ARCHIVE` 열에 NSKeyedArchiver 로 묶여 있어 풀어야 읽힙니다.

## 무엇을 기록하나 · 왜 생기나

앱이 DM 대화방과 메시지를 기기 안에 저장해 두는 곳이 `DirectSQLiteDatabase` 폴더의 DB 입니다[1][2]. 이 DB 에는 글 메시지, 미디어 메시지(미디어 URL 포함), 음성·영상 통화 기록이 남고, 메시지에 단 반응과 공유한 미디어 정보도 함께 들어 있습니다[1][2]. 공개 도구는 DB 에 지금 남아 있는 메시지만 읽어서[1], 지운 메시지는 도구 결과에 나오지 않습니다.

## 위치와 버전별 차이

DB 가 어느 컨테이너에 있는지는 자료마다 다릅니다. iLEAPP 는 앱 데이터 컨테이너에서 찾고[1], 다른 분석 글은 앱 그룹 컨테이너에 있다고 적습니다[2].

```
# iLEAPP 가 찾는 위치(파일 시스템 추출 기준)
*/mobile/Containers/Data/Application/*/Library/Application Support/DirectSQLiteDatabase/*.db*

# 다른 분석 글이 적은 위치
/private/var/mobile/Containers/Shared/AppGroup/<App_GUID>/Library/Application Support/DirectSQLiteDatabase/****.db
```

두 컨테이너를 모두 찾아보고, 폴더 안의 `.db` 파일과 함께 `-wal`·`-shm` 파일도 가져옵니다. 컨테이너 종류와 앱 그룹은 [번들 ID와 앱 그룹 (Bundle ID·App Group)](../../01-foundations/value-decoding/bundle-id-app-group.md)에서 다룹니다. iOS 버전과 앱 버전에 따라 위치나 표가 어떻게 달라지는지는 공개 자료가 없습니다. 앱 업데이트마다 바뀔 수 있어서 위 경로는 "도구가 찾는 위치" 로 보고 실제 기기에서 직접 확인합니다.

## 구조

### 표와 열

주요 표와 열은 아래와 같습니다[1].

| 표 | 열 | 읽는 법 |
|---|---|---|
| `THREADS` | `THREAD_ID` | 대화방 ID 입니다 |
| `THREADS` | `VIEWER_ID` | 값을 설명한 공개 자료가 없습니다 |
| `THREADS` | `METADATA` | 대화방 정보가 NSKeyedArchiver 로 들어 있고 참여자 목록을 여기서 찾습니다 |
| `MESSAGES` | `MESSAGE_ID` | 메시지 ID 입니다 |
| `MESSAGES` | `THREAD_ID` | `THREADS.THREAD_ID` 와 이어 어느 대화방의 메시지인지 찾습니다 |
| `MESSAGES` | `ARCHIVE` | 메시지 내용이 NSKeyedArchiver 로 들어 있습니다 |

### `ARCHIVE` 안의 키

`ARCHIVE` 를 풀면 객체 그래프가 나오고, 아래 키를 따라가면 값을 꺼낼 수 있습니다[1].

| 키 | 담긴 것 |
|---|---|
| `IGDirectPublishedMessageMetadata*metadata` | 보낸 사람과 시각을 묶은 객체입니다 |
| `NSString*senderPk` | 보낸 사람 ID 입니다 |
| `NSDate*serverTimestamp` | 서버 시각입니다 |
| `IGDirectPublishedMessageContent*content` | 본문과 미디어를 묶은 객체입니다 |
| `NSString*string` | 글 본문입니다 |
| `IGDirectThreadActivityAnnouncement*threadActivity` | 음성·영상 통화 알림입니다 |
| `NSArray<IGDirectMessageReaction *>*reactions` | 메시지에 단 반응이고, 안에 `emojiUnicode`·`userId`·`serverTimestamp` 가 있습니다 |
| `IGDirectPublishedMessageMedia*media` | 공유한 사진 정보이고, 안에 이미지 URL 과 `expiration_date` 가 있습니다 |

보낸 사람 이름은 `ARCHIVE` 에 없어서, `THREADS.METADATA` 를 풀어 `NSArray<IGUser *>*users` 와 `IGUser*inviter` 에 든 사용자 정보를 `senderPk` 와 맞춰 찾습니다[1]. NSKeyedArchiver 를 푸는 원리는 [속성 목록 파일 (plist·NSKeyedArchiver)](../../01-foundations/data-formats/plist.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** `MESSAGES` 행은 이 기기의 인스타그램 DB 에 어느 대화방에서 어떤 사용자 ID 가 보낸 것으로 기록된 메시지가 이 서버 시각과 함께 남아 있다는 사실을 보여 줍니다. `threadActivity` 가 있는 행은 그 대화방에 통화 알림이 기록되어 있다는 뜻이고, `reactions` 로 누가 어떤 메시지에 반응했는지도 볼 수 있습니다[1].

**증명하지 못하는 것.** DB 에 남은 메시지만 보이기 때문에 행이 없다고 대화가 없었다고 볼 수 없고, 서버나 상대 기기에는 이 기기에 없는 메시지가 있을 수 있습니다. 미디어 메시지에 URL 이 남아 있어도[2] 그 파일을 기기에서 열어 봤는지는 이 DB 만으로 알 수 없습니다. `senderPk` 는 계정 ID 라서, 그 계정을 그 시각에 실제로 누가 쓰고 있었는지는 [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](../../04-scenarios/activity/user-attribution.md)처럼 다른 흔적으로 따로 밝혀야 합니다.

## 시각 해석

`serverTimestamp` 는 plist 의 날짜 값이고, UTC 로 바꿔 읽습니다[1]. 이 값이 서버에서 붙은 시각인지 기기 시계로 붙은 시각인지는 공개 자료가 없어서, 기기 시계가 틀려 있던 사건이라면 다른 흔적과 맞춰 봅니다. `ARCHIVE` 안에서 날짜가 어떤 기준의 숫자로 저장되는지도 공개 자료가 없습니다. 그래서 도구가 보여 준 시각을 쓰기 전에 원래 값을 한 번 꺼내 보고, [시각 값 (Mac 절대 시각·Unix·기타)](../../01-foundations/value-decoding/time-values.md)의 방법으로 기준을 맞춰 봅니다. 현지 시각은 UTC 로 바꾼 뒤에 시간대를 따로 적용합니다.

## 함정과 한계

DB 위치를 한 곳만 보면 놓칠 수 있습니다. 자료마다 앱 데이터 컨테이너와 앱 그룹 컨테이너로 다르게 적혀 있고[1][2], iLEAPP 는 `*.db*` 로 이름과 상관없이 찾아서[1] 폴더 안에 DB 가 여러 개면 모두 봐야 합니다. iLEAPP 의 경로는 파일 시스템 추출 기준이고, 로컬 백업에 이 파일이 들어가는지는 공개 자료가 없습니다. 백업만 확보했다면 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../01-foundations/backups/local-backup/index.md)의 `Manifest.db` 에서 먼저 파일이 있는지 확인합니다.

키 이름에 클래스 이름이 붙어 있어서(`IGDirect…`) 앱이 내부 클래스를 바꾸면 도구가 값을 못 찾고 빈 값으로 보고할 수 있습니다. 빈 본문을 "내용 없는 메시지" 로 읽기 전에 `ARCHIVE` 를 직접 풀어 확인합니다. 지운 메시지를 SQLite 빈 공간이나 WAL 에서 찾는 일반적인 방법은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)와 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

`ARCHIVE` 열의 앞 바이트를 보면 plist 가 어떤 형식으로 들어 있는지 알 수 있습니다. 이진 plist 라면 `bplist00` 으로 시작하고, XML plist 라면 `<?xml` 로 시작합니다. 아래는 명세로 만든 예시이고 실제 기기에서 나온 값이 아닙니다.

```
62 70 6C 69 73 74 30 30  ...   bplist00...
```

이진 plist 라면 열 값을 파일로 꺼내 plist 도구로 열고, `$objects` 배열에서 `senderPk`·`serverTimestamp`·`string` 이 가리키는 항목을 따라가 봅니다.

### 질의로 한 번

```sql
SELECT m.MESSAGE_ID, m.THREAD_ID, t.VIEWER_ID,
       length(m.ARCHIVE) AS archive_len,
       hex(substr(m.ARCHIVE, 1, 8)) AS head8
FROM MESSAGES m
LEFT JOIN THREADS t ON t.THREAD_ID = m.THREAD_ID
LIMIT 20;
```

`head8` 이 모두 같은 형식인지 보고, `ARCHIVE` 가 빈 행이 있는지 셉니다.

### 공개 도구로 한 번

iLEAPP 의 인스타그램 분석기는 이 DB 에서 메시지 보고서와 통화 보고서를 만듭니다[1]. 위 질의로 센 행 수와 보고서의 행 수를 맞춰 보고, 보고서에서 본문이 빈 행을 골라 `ARCHIVE` 를 직접 풀어 봅니다. 도구마다 결과가 다를 때 확인하는 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)에 있습니다.

## 교차 검증

DM 이 온 시각에 인스타그램 알림이 떴는지는 [알림 기록 (Notifications)](../app-usage/notifications.md)에서, 그 시각에 앱을 쓰고 있었는지는 [KnowledgeC (knowledgeC.db)](../app-usage/knowledgec/index.md)와 [바이옴 (Biome)](../app-usage/biome/index.md)에서 봅니다. 미디어를 주고받은 시간대에 앱이 데이터를 얼마나 썼는지는 [앱별 데이터 사용량 (DataUsage.sqlite)](../network/data-usage.md)과 맞춰 봅니다. 다른 연락 수단과 시간순으로 합치는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)과 [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md)에 있습니다.

## 실습

공개된 iOS 시험 이미지 가운데 인스타그램이 설치된 것으로 아래를 풀어 봅니다.

1. 앱 데이터 컨테이너와 앱 그룹 컨테이너 가운데 어디에 `DirectSQLiteDatabase` 폴더가 있는지 찾아봅니다.
2. 대화방 하나를 골라 `THREADS.METADATA` 의 사용자 목록과 그 방 `MESSAGES` 의 `senderPk` 를 맞춰 참여자별 메시지 수를 세어 봅니다.
3. `serverTimestamp` 의 원래 값을 꺼내 도구가 보여 준 UTC 시각과 같은지 확인해 봅니다.

## 참고 문헌

1. abrignoni/iLEAPP, `scripts/artifacts/instagramThreads.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/instagramThreads.py
2. Forensafe, "iOS Instagram" — https://www.forensafe.com/blogs/iOSInstagram.html
