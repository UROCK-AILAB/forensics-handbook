---
title: "왓츠앱"
parent: "아티팩트 · 메신저"
nav_order: 960
---

# 왓츠앱 (WhatsApp)

왓츠앱은 메시지·대화방·통화 기록을 `msgstore.db` 에, 연락처를 `wa.db` 에 나눠 두는 SQLite 메신저이고, 앱 버전에 따라 메시지 표가 예전 구조 `messages` 와 새 구조 `message` 로 갈립니다.

## 무엇을 기록하나 · 왜 생기나

왓츠앱은 주고받은 메시지, 대화방, 통화, 위치 공유, 그룹 정보를 앱 내부 저장소의 DB 에 한 행씩 쌓습니다[1].

## 위치와 버전별 차이

패키지 이름은 `com.whatsapp` 입니다. 공개 도구 ALEAPP 의 `WhatsApp.py` 가 찾는 파일은 다음과 같습니다[1].

```
*/com.whatsapp/databases/msgstore.db*
*/com.whatsapp/databases/wa.db*
*/com.whatsapp/shared_prefs/com.whatsapp_preferences_light.xml
*/com.whatsapp/shared_prefs/startup_prefs.xml
*/com.whatsapp/files/Avatars/*
*/com.whatsapp/files/Media/*
*/WhatsApp/Media/*
```

DB 파일 이름 뒤의 `*` 는 `-wal`·`-shm` 같은 딸린 파일까지 함께 잡으려는 것으로 보입니다. DB 를 확보할 때는 딸린 파일을 같이 가져와야 최근 변경분을 잃지 않고, 그 이유는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다. `shared_prefs` 아래 두 XML 은 앱 설정 파일이고, 읽는 법은 [설정 XML과 SharedPreferences](../../01-foundations/data-formats/shared-preferences.md)를 봅니다.

마지막 줄 `*/WhatsApp/Media/*` 는 앞쪽 경로를 가리지 않고 찾는 패턴이라서, 받은 사진·파일이 [공용 저장 공간](../../01-foundations/storage/shared-storage.md) 어디에 있든 잡습니다. Android 11 이후 이 폴더가 `/sdcard/Android/media/com.whatsapp/WhatsApp/` 로 옮겨졌다는 이야기가 있지만 공식 자료는 없으므로, 검체에서 두 위치를 모두 찾아봅니다.

| 항목 | 알려진 것 | 검체에서 확인할 것 |
|---|---|---|
| 메시지 표 | 예전 구조 `messages`, 새 구조 `message` 두 가지가 있고 ALEAPP 는 둘 다 읽습니다 | 어느 앱 버전에서 바뀌었는지 |
| 미디어 폴더 | ALEAPP 는 `*/WhatsApp/Media/*` 로 찾습니다 | Android 11 이후 폴더 이동 |
| 백업 | | 외부 저장소에 남는 암호화 백업의 위치와 형식 |
| One UI | | 삼성 기기에서의 차이 |

## 구조

### wa.db — 연락처

| 표 | 칸 |
|---|---|
| `wa_contacts` | `jid`, `given_name`, `family_name`, `display_name`, `number`, `wa_name` |
| `wa_group_admin_settings` | `jid`, `creator_jid` |

`wa_contacts.jid` 는 `msgstore.db` 의 `jid.raw_string` 과 같은 값이라서, `wa.db` 를 `msgstore.db` 에 붙여 열면 두 표를 이어 붙일 수 있습니다[1]. `wa_group_admin_settings` 도 `wa.db` 쪽 표이고, 그룹 JID 로 이 표에서 찾은 `creator_jid` 는 그룹을 만든 사람을 가리키는 것으로 보입니다[1].

### msgstore.db — 메시지, 대화방, 통화

예전 구조와 새 구조의 메시지 표는 칸이 다릅니다.

| 구조 | 표 | 칸 |
|---|---|---|
| 예전 | `messages` | `timestamp`, `received_timestamp`, `key_remote_jid`, `key_from_me`, `data`, `remote_resource`, `media_url` |
| 새 | `message` | `timestamp`, `received_timestamp`, `from_me`, `text_data`, `chat_row_id`, `recipient_count`, `sender_jid_row_id` |

예전 구조는 상대 식별자(`key_remote_jid`)와 본문(`data`)이 메시지 행에 바로 있습니다. 새 구조는 본문이 `text_data` 에 있지만 상대는 번호로만 가리켜서, `message.chat_row_id` → `chat.jid_row_id` → `jid.raw_string` 순서로 이어 붙여야 상대 번호가 나옵니다[1].

새 구조에서 메시지에 딸린 표와 통화·그룹 표는 다음과 같습니다.

| 표 | 칸 | 담는 것 |
|---|---|---|
| `message_media` | `message_row_id`, `file_path`, `file_size` | 첨부 파일 경로와 크기 |
| `message_location` | `message_row_id`, `latitude`, `longitude`, `live_location_share_duration`, `live_location_final_latitude`, `live_location_final_longitude`, `live_location_final_timestamp` | 위치 메시지와 실시간 위치 공유 |
| `chat` 또는 `chat_view` | `_id`, `subject`, `jid_row_id`, `created_timestamp` | 대화방. `subject` 는 그룹 이름으로 보입니다 |
| `jid` | `_id`, `raw_string` | 상대·그룹 식별자 |
| `call_log` | `timestamp`, `duration`, `from_me`, `video_call`, `jid_row_id`, `group_jid_row_id` | 통화 기록 |
| `group_participants` | `gjid`, `jid` | 그룹 참여자. 예전 구조에서는 이 표로 그룹의 참여자 목록을 만듭니다 |

## 증거로서 의미

**증명하는 것.** `message` 에 행이 있으면 그 대화방에 그 시각으로 적힌 메시지 기록이 기기의 DB 에 있었다는 뜻입니다. `from_me`(예전 구조는 `key_from_me`)는 이 기기 쪽에서 보낸 기록인지 받은 기록인지를 가르며, 0 은 받은 것, 1 은 보낸 것입니다[1]. `call_log` 는 왓츠앱으로 걸고 받은 통화의 시각·길이·영상 여부(`video_call` 이 1 이면 영상)를 보여 주고, 기기 기본 통화 기록과는 따로 대조합니다. `message_location` 은 위치를 보낸 기록과 실시간 위치 공유의 마지막 좌표·시각을 보여 줍니다.

**증명하지 못하는 것.** `from_me` 가 이 기기 쪽이라는 뜻이어도 그 순간 폰을 누가 쥐고 있었는지는 말해 주지 않고, 이 판단은 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)의 방법으로 따로 합니다. `message_media.file_path` 는 첨부가 저장된 경로를 가리킬 뿐이라서, 그 경로에 지금 파일이 있는지는 공용 저장 공간을 직접 확인해야 합니다. 위치 좌표는 앱이 보낸 좌표이고, 그 사람이 그 자리에 있었다는 사실과는 구분해서 씁니다.

보고서에는 "A 에게 사진을 보냈다" 가 아니라 "이 시각에 이 대화방으로 `from_me` 값이 1 인 미디어 메시지 기록이 있고, 첨부 경로는 이렇다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

시각 칸은 유닉스 밀리초이고, `datetime(칸/1000,'unixepoch')` 로 바꿉니다[1]. 이 변환 결과는 UTC 이며, 현지 시각이 필요하면 [시간대와 시각 설정](../system-account/time-zone.md)을 함께 봅니다. 메시지 표에는 `timestamp` 와 `received_timestamp` 두 시각이 있고, 이름으로 보면 앞의 것이 메시지 시각, 뒤의 것이 기기가 받은 시각입니다. 두 칸이 정확히 언제 쓰이는지는 공개 자료가 없으니, 알려진 대화 몇 건으로 차이를 먼저 확인합니다.

`chat.created_timestamp` 는 대화방 시각, `message_location.live_location_final_timestamp` 는 실시간 위치 공유의 마지막 시각, `call_log.timestamp` 는 통화 시각이고 `call_log.duration` 은 길이입니다. `duration` 은 초 단위라서 `timestamp/1000 + duration` 이 통화가 끝난 시각입니다[1]. 단위 판별과 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

## 함정과 한계

- 검체의 메시지 표가 `messages` 인지 `message` 인지 먼저 확인합니다. 두 구조의 칸 이름이 달라서, 한쪽 구조에 맞춘 쿼리를 다른 쪽에 그대로 쓰면 빈 결과가 나옵니다.
- 새 구조에서는 상대 번호가 메시지 행에 없어서, 이어 붙이는 단계를 빠뜨리면 대화 상대를 잘못 짝지을 수 있습니다.
- ALEAPP 에는 로그 파일을 보는 모듈 `WhatsAppLogFiles.py` 가 따로 있습니다[2].
- 외부 저장소의 암호화 백업은 위치와 형식을 다룬 공개 자료가 없고, 이 핸드북은 백업을 푸는 절차를 다루지 않습니다.
- 지운 메시지가 DB 안에 남는지, 남는다면 어디에 남는지는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)와 [지운 대화와 사진 찾기](../../04-scenarios/activity/deleted-content.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

밀리초 시각이 레코드 안에서 어떻게 보이는지 따라가 봅니다. SQLite 레코드는 정수를 빅엔디언으로 저장하고, 1758800000000 같은 13자리 밀리초는 6바이트 정수(레코드 머리의 자료형 번호 5)로 들어갑니다. 다음은 명세로 만든 예시이고 검체에서 나온 값이 아닙니다.

```
01 99 80 A6 34 00   → 0x019980A63400 = 1758800000000 ms
                    → 1758800000 s → 2025-09-25 11:33:20 UTC
```

헥스 편집기에서 `timestamp` 값을 찾을 때는 이렇게 6바이트로 줄어들 수 있다는 점을 기억하고, 앞에 0x00 이 두 개 붙은 8바이트를 찾지 않습니다.

### 공개 도구로 한 번

ALEAPP 는 `WhatsApp.py` 로 연락처, 메시지, 통화, 위치, 그룹을 뽑습니다. 결과를 그대로 믿기 전에 `sqlite3` 로 사본을 열어 한 번 직접 확인합니다. 새 구조라면 다음처럼 대화 상대를 이어 붙여 시간 순으로 봅니다.

```sql
SELECT datetime(m.timestamp/1000, 'unixepoch')          AS sent_utc,
       datetime(m.received_timestamp/1000, 'unixepoch') AS received_utc,
       j.raw_string AS chat_jid, c.subject, m.from_me, m.text_data,
       mm.file_path, mm.file_size
FROM message m
LEFT JOIN chat c           ON c._id = m.chat_row_id
LEFT JOIN jid j            ON j._id = c.jid_row_id
LEFT JOIN message_media mm ON mm.message_row_id = m._id
ORDER BY m.timestamp;
```

`message_media.message_row_id` 와 `message_location.message_row_id` 는 `message._id` 에 이어집니다[1]. 검체 앱 버전에서 칸 이름이 같은지는 `PRAGMA table_info(message);` 로 먼저 확인합니다. 도구 결과와 직접 뽑은 결과의 건수가 다르면 [도구 검증](../../03-techniques/reporting/tool-validation.md)의 방법대로 원인을 찾습니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [연락처](../communications/contacts.md) | `wa_contacts` 의 번호가 기기 주소록의 누구와 맞는지 |
| [통화 기록](../communications/call-log.md) | 기본 통화와 왓츠앱 통화를 한 시간선에 놓기 |
| [미디어 저장소](../media/mediastore/index.md) | `file_path` 의 파일이 미디어 색인에 언제 들어왔는지 |
| [알림 기록](../app-usage/notification-history.md) | 받은 메시지 알림의 제목과 시각 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 보낸 메시지 시각에 앱 화면이 앞에 있었는지 |
| [구글 위치 기록과 타임라인](../location/google-timeline.md) | 위치 메시지 좌표와 기기 위치 기록 비교 |

여러 메신저를 한 시간선에 모으는 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md)에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등) 가운데 왓츠앱이 설치된 Android 이미지를 골라 다음 질문을 풀어 봅니다.

1. `msgstore.db` 의 메시지 표는 예전 구조와 새 구조 중 어느 쪽인가요? 둘 다 있다면 각 표의 건수는 얼마인가요?
2. `-wal` 파일이 함께 확보됐나요? 딸린 파일을 넣고 연 결과와 빼고 연 결과의 메시지 건수를 비교해 보세요.
3. `call_log` 의 통화 가운데 기기 기본 통화 기록에 없는 것은 몇 건인가요?
4. `message_media.file_path` 에 적힌 파일 가운데 공용 저장 공간에 실제로 남아 있는 것은 몇 개인가요?

## 참고 문헌

1. ALEAPP — WhatsApp.py. https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/WhatsApp.py
2. ALEAPP — scripts/artifacts 폴더 목록(GitHub API). https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
