---
title: "텔레그램"
parent: "아티팩트 · 메신저"
nav_order: 950
---

# 텔레그램 (Telegram)

텔레그램 앱은 대화 목록·메시지·연락처·비밀 대화 정보를 앱 내부 저장소의 SQLite 파일 `cache4.db` 에 모아 두고, 메시지 본문은 텍스트 열이 아니라 앱 자체 형식으로 직렬화한 BLOB 안에 넣습니다.

## 무엇을 기록하나 · 왜 생기나

텔레그램 앱은 대화 목록과 메시지를 기기의 `cache4.db` 에 저장합니다. 파일 이름과 위치, 표 구조는 텔레그램 Android 앱 공개 소스의 `MessagesStorage.java` 에 정의돼 있습니다[1]. 앱이 자주 바뀌므로 실제 기기의 앱 버전에서 표 구조를 먼저 확인하고 읽습니다.

`cache4.db` 에는 메시지, 대화 목록, 사용자, 그룹·채널, 비밀 대화, 미디어 색인, 연락처, 보낸 파일, 내려받기 대기 목록이 표로 나뉘어 들어 있습니다[1]. 그래서 본문을 풀지 않아도 누구와 어떤 대화방에서 언제 메시지가 오갔는지, 비밀 대화를 연 적이 있는지 같은 윤곽을 잡을 수 있습니다.

## 위치와 버전별 차이

앱의 자바 패키지 경로는 `org.telegram.messenger` 입니다[1]. Play 스토어의 패키지 이름도 같다고 알려져 있으니, 분석할 기기에서는 [설치된 앱](../app-usage/packages/index.md) 기록으로 실제 패키지 이름을 먼저 확인합니다.

`cache4.db` 는 앱의 files 폴더(`ApplicationLoader.getFilesDirFixed()`) 아래에 만들어집니다[1]. 계정 번호가 0 인 첫 계정은 files 바로 아래를 쓰고, 번호가 0 이 아닌 계정은 "account" 뒤에 번호를 붙인 하위 폴더(`account1/`, `account2/` …)를 씁니다. 그래서 경로는 다음 형식이 됩니다. 앞부분(`/data/data/…/files`)은 기기에서 실제 경로를 확인합니다.

```
/data/data/org.telegram.messenger/files/cache4.db            (첫 계정, 번호 0)
/data/data/org.telegram.messenger/files/account<N>/cache4.db (두 번째 계정부터, N 은 1 이상)
```

계정이 여럿인 기기에서는 files 아래를 모두 살펴 `cache4.db` 가 몇 개인지부터 셉니다. 앱 내부 저장소의 일반 구조는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md)에서 다룹니다.

| 항목 | 알려진 것 | 실제 기기에서 확인할 것 |
|---|---|---|
| DB 버전 | 상수 `LAST_DB_VERSION` 이 178 이고, 버전이 오를 때 표 구조가 바뀝니다 | 실제 앱 버전과 DB 버전의 대응 |
| 여러 계정 | 첫 계정은 files 바로 아래, 나머지는 `account<N>/` 하위 폴더 | 기기에서의 전체 경로 |
| 받은 파일 | | 외부 저장소에 저장되는 폴더 |
| Android 버전·One UI | | 버전·제조사별 차이(공개 자료 없음) |

## 구조

`cache4.db` 의 주요 표는 다음과 같습니다. 열 이름은 소스의 `CREATE TABLE` 문에 있는 그대로이고[1], 뜻은 열 이름으로 짐작한 것이라 값으로 맞춰 봐야 합니다.

| 표 | 열 | 뜻(짐작) |
|---|---|---|
| `messages_v2` | `mid`, `uid`, `read_state`, `send_state`, `date`, `data`(BLOB), `out`, `ttl`, `media`, `replydata`(BLOB), `imp`, `mention`, `forwards`, `replies_data`(BLOB), `thread_reply_id`, `is_channel`, `reply_to_message_id`, `custom_params`(BLOB), `group_id`, `reply_to_story_id` | 메시지 한 건이 한 행입니다. 기본 키는 (`mid`, `uid`)이고, `uid` 는 대화 상대나 대화방 ID, `out` 은 보낸 메시지 여부, `read_state` 는 읽음 상태로 보입니다 |
| `dialogs` | `did`(기본 키), `date`, `unread_count`, `last_mid`, `inbox_max`, `outbox_max`, `last_mid_i`, `unread_count_i`, `pts`, `date_i`, `pinned`, `flags`, `folder_id`, `data`(BLOB), `unread_reactions`, `last_mid_group`, `ttl_period`, `unread_poll_votes` | 대화 목록 |
| `users` | `uid`, `name`, `status`, `data`(BLOB) | 사용자 |
| `chats` | `uid`, `name`, `data`(BLOB) | 그룹·채널 |
| `enc_chats` | `uid`, `user`, `name`, `data`, `g`, `authkey`, `ttl`, `layer`, `seq_in`, `seq_out`, `use_count`, `exchange_id`, `key_date`, `fprint`, `fauthkey`, `khash`, `in_seq_no`, `admin_id`, `mtproto_seq` | 비밀 대화 |
| `media_v4` | `mid`, `uid`, `date`, `type`, `data`(BLOB) | 미디어 색인. 기본 키는 (`mid`, `uid`, `type`) |
| `contacts` | `uid`, `mutual` | 텔레그램 연락처 |
| `user_contacts_v7` | `key`, `uid`, `fname`, `sname`, `imported` | 기기 주소록에서 가져온 연락처 |
| `sent_files_v2` | `uid`, `type`, `data`, `parent` | 보낸 파일 |
| `download_queue` | `uid`, `type`, `date`, `data`, `parent` | 내려받기 대기 목록 |

메시지 본문은 `messages_v2.data` BLOB 안에 텔레그램 자체 직렬화 형식으로 들어 있어서, SQL 만으로는 본문을 바로 읽기 어렵고 이 형식을 해석하는 도구가 따로 필요합니다. `users.name`, `chats.name` 처럼 이름이 텍스트 열로 따로 있는 표는 SQL 로 바로 읽을 수 있어서, `messages_v2.uid` 를 이 표들과 이어 붙이면 대화 상대 이름을 붙인 메시지 목록을 만들 수 있습니다. 그룹·채널 대화의 ID 는 음수이고 앱은 `chats` 를 찾을 때 부호를 뒤집어 쓰므로[1], `chats` 와 이을 때는 `-uid` 로 맞춥니다.

앱은 DB 를 연 뒤 `PRAGMA journal_mode = WAL` 을 실행하고 `cache4.db-wal`, `cache4.db-shm` 파일도 함께 다루므로[1], 확보할 때는 두 딸린 파일을 같이 가져와야 최근 변경분을 잃지 않습니다. 파일 전체가 암호화돼 있는지는 아래 "직접 분석해 보기" 의 머리글 확인으로 기기마다 판단합니다. SQLite 파일 구조와 딸린 `-wal`·`-shm` 파일은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `messages_v2` 에 행이 있으면 그 `uid` 대화에 해당하는 메시지가 기기의 캐시에 저장돼 있었다는 뜻입니다. `dialogs` 는 기기에 남은 대화방 목록과 마지막 메시지 시각을, `user_contacts_v7` 은 기기 주소록에서 텔레그램으로 가져온 연락처를 보여 줍니다. `enc_chats` 에 행이 있으면 그 상대와 비밀 대화를 연 흔적이 기기에 남아 있다는 뜻이고, 본문이 없어도 비밀 대화가 있었다는 사실 자체는 이 표로 볼 수 있습니다.

**증명하지 못하는 것.** `cache4.db` 가 계정의 대화 전체를 담는지, 기기에 받아 둔 부분만 담는지는 공개 자료가 없으므로, 행이 없다고 그 대화가 없었다고 말할 수 없습니다. `out`, `read_state` 같은 열의 값 뜻은 열 이름으로 짐작한 것이므로, 보고서에 "보냈다", "읽었다" 를 쓰기 전에 알려진 대화 몇 건으로 값의 뜻을 먼저 맞춰 봅니다. `users.name` 에 들어가는 이름이 어디서 오는지도 알려져 있지 않으니, 이 이름을 실제 인물과 곧바로 같다고 보지 않습니다.

## 시각 해석

`messages_v2`, `dialogs`, `media_v4` 의 `date` 열은 INTEGER 이고 유닉스 초(밀리초 아님)입니다. 앱은 메시지를 저장할 때 텔레그램 메시지 객체의 `date` 값을 `bindInteger` 로 그대로 넣고[1], 이 값은 32비트 정수로 적은 초 단위 시각입니다. 실제 데이터에서는 자릿수(10자리면 초, 13자리면 밀리초)로 한 번 더 확인합니다. 유닉스 시각은 1970-01-01 00:00:00 UTC 부터 센 값이라, 현지 시각으로 바꿀 때는 기기의 [시간대와 시각 설정](../system-account/time-zone.md)을 함께 봅니다. 단위 판별과 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

`date` 가 메시지를 보낸 시각인지, 서버가 받은 시각인지, 기기가 받은 시각인지는 알려진 대화로 맞춰 봐야 합니다. `dialogs.date` 가 무엇을 가리키는 시각인지도 알려져 있지 않으니, 이 열 하나로 "대화를 시작한 시각" 을 쓰지 않습니다.

## 함정과 한계

- DB 버전이 오르면 표 구조가 바뀌므로, 앱 버전에 따라 표 이름과 열이 다를 수 있습니다. 표 목록부터 뽑아 보고 이 페이지의 이름과 대조합니다.
- ALEAPP 모듈 목록에는 텔레그램 이름의 모듈이 따로 보이지 않습니다[2]. 도구가 결과를 내지 않았다고 텔레그램 흔적이 없다고 보지 않습니다.
- 메시지를 지우면 행이 사라지지만, SQLite 는 지운 행을 곧바로 덮어쓰지 않을 때가 있습니다. 남는 방식과 복구는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.
- `cache4.db` 는 앱 내부 저장소에 있고, 이 영역을 읽는 권한은 [앱 샌드박스와 권한](../../01-foundations/security-model/sandbox-permissions.md)에서 다룹니다. 어떤 방법으로 파일을 얻었는지 기록해 두고, 확보 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

먼저 `cache4.db` 가 평문 SQLite 인지 확인합니다. SQLite 파일의 맨 앞 16바이트는 `SQLite format 3` 과 0x00 이고, 이렇게 보이면 일반 SQLite 도구로 열 수 있습니다. 다음은 명세로 만든 예시입니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

`date` 열 값이 레코드 안에 어떻게 들어가는지도 한 번 따라가 봅니다. SQLite 레코드는 정수를 빅엔디언으로 저장하고, 유닉스 초 1758800000 은 4바이트 정수라서 다음처럼 보입니다. 이 값도 명세로 만든 예시이고 실제 데이터에서 나온 값이 아닙니다.

```
68 D5 28 80   → 0x68D52880 = 1758800000 → 2025-09-25 11:33:20 UTC
```

### 공개 도구로 한 번

`sqlite3` 명령행 도구나 DB Browser for SQLite 로 사본을 엽니다. 표 목록을 먼저 보고, 메시지 표에 대화방 이름을 붙여 시간 순으로 뽑습니다. 1:1 대화의 `uid` 는 `users.uid` 와 같고, 그룹·채널 대화의 `uid` 는 음수라서 `chats.uid` 와는 부호를 뒤집어 잇습니다. 비밀 대화의 ID 는 또 다른 방식으로 만들어지므로 이 쿼리로는 이름이 붙지 않을 수 있습니다.

```sql
.tables
SELECT m.mid, m.uid, u.name AS user_name, c.name AS chat_name,
       datetime(m.date, 'unixepoch') AS date_utc, m.out, m.read_state
FROM messages_v2 m
LEFT JOIN users u ON u.uid = m.uid
LEFT JOIN chats c ON c.uid = -m.uid
ORDER BY m.date;
```

본문(`data` BLOB)은 이 쿼리로 읽히지 않습니다. 텔레그램 형식을 해석하는 도구를 쓴다면 그 도구가 어느 앱 버전까지 맞는지 [도구 검증](../../03-techniques/reporting/tool-validation.md)의 방법대로 확인한 뒤 결과를 씁니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [설치된 앱](../app-usage/packages/index.md) | 실제 패키지 이름, 설치·업데이트 시각 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 메시지 시각 무렵 텔레그램 화면이 앞에 있었는지 |
| [알림 기록](../app-usage/notification-history.md) | 받은 메시지 알림의 제목과 시각 |
| [연락처](../communications/contacts.md) | `user_contacts_v7` 에 들어온 주소록 연락처의 원본 |
| [데이터 사용량](../network/netstats.md) | 그 시간대에 앱이 주고받은 데이터 양 |

여러 메신저를 한 시간선에 모으는 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md)에서 다룹니다.

## 실습

공개 시험 자료(NIST CFReDS 등) 가운데 텔레그램이 설치된 Android 이미지를 골라 다음 질문을 풀어 봅니다.

1. files 폴더 아래에 `cache4.db` 가 몇 개 있고, 각각 어느 계정의 것인지 어떻게 구분하나요?
2. `cache4.db` 의 표 목록을 뽑아 이 페이지의 표 이름과 다른 것이 있나요? 있다면 그 이미지의 앱 버전은 무엇인가요?
3. `enc_chats` 에 행이 있나요? 있다면 `user` 열의 값이 `users` 의 어느 사용자와 이어지나요?
4. `messages_v2.date` 의 자릿수로 단위를 판단하고, 가장 이른 메시지와 가장 늦은 메시지의 UTC 시각을 구해 보세요.

## 참고 문헌

1. DrKLO/Telegram — MessagesStorage.java. https://raw.githubusercontent.com/DrKLO/Telegram/master/TMessagesProj/src/main/java/org/telegram/messenger/MessagesStorage.java
2. ALEAPP — scripts/artifacts 폴더 목록(GitHub API). https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
