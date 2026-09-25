---
title: "ChatGPT Android 앱"
parent: "ChatGPT"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 110
---

# Android 앱 (Android)

Android 용 ChatGPT 앱(패키지 `com.openai.chatgpt`)은 대화 목록과 메시지를 앱 데이터 폴더의 SQLite 데이터베이스에 평문으로 두고, 계정·요금제·맞춤 지시·채팅 기록 설정은 `files/datastore/` 아래 설정 파일에, 분석 도구 식별자는 `shared_prefs/` 의 XML 에 둡니다 [2][3][4].

이 쪽의 경로와 칸은 앱 1.2024.177 까지 다루는 ALEAPP 분석기 기준이고, 지금 판은 형식이 다를 수 있습니다[3][4].

## 무엇을 기록하나 · 왜 생기나

앱은 계정의 대화를 기기 데이터베이스에 사본으로 둡니다. 그래서 기기에는 대화 제목·만든 시각·고친 시각과 메시지 본문이 남고, 로그인한 계정의 이메일·이름·요금제, 사용자가 적은 맞춤 지시(custom instructions), "채팅 기록 끄기" 설정도 함께 남습니다 [3][4].

Tyagi·Gong·Karabiyik(2025)은 ChatGPT 가 Android 와 iOS 모두에서 대화를 브라우저 데이터와 함께 평문으로 저장한다고 초록에 적었습니다 [2]. 두 ALEAPP 분석기도 복호화 단계 없이 데이터베이스를 바로 엽니다 [3][4].

LangurTrace 논문은 Dragonas·Lambrinoudakis·Nakoutis(2024)[1]를 ChatGPT 모바일 앱을 처음 포렌식으로 분석한 연구로 소개하고, 이 연구가 Android·iOS·클라우드 저장소에서 흔적을 찾았다고 요약했습니다 [7]. Ex Machina 논문은 같은 연구가 캐시된 프롬프트, 접근 토큰, 네트워크 흔적처럼 증거로 쓸 수 있는 흔적을 찾았다고 요약했습니다 [6]. ALEAPP `chatgpt.py` 의 작성자도 Dragonas 입니다 [3].

## 위치와 버전별 차이

앱 폴더는 `/data/data/com.openai.chatgpt/` 입니다. 폴더 구조의 일반 원리는 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html)에서, 이 폴더가 기기 암호화의 보호를 받는 방식은 [저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html)에서 다룹니다.

| 앱 폴더 안 경로 | 형식 | 담긴 것 | 근거 |
|---|---|---|---|
| `databases/*_conversations.db` 와 `-wal`·`-shm` | SQLite | 대화 목록, 메시지 | [3][4] |
| `files/datastore/*_user.preferences_pb` | protobuf 안의 JSON | 사용자 ID·이메일·이름·계정 생성 시각 | [3] |
| `files/datastore/*_accountstatus.preferences_pb` | protobuf 안의 JSON | 계정 ID, 요금제, 결제 경로, 비활성 여부 | [3] |
| `files/datastore/*_accountuser_state.preferences_pb` | protobuf 안의 JSON | 이 기기에 로그인한 계정 목록과 지금 쓰는 계정 | [3] |
| `files/datastore/*_custom_instructions.preferences_pb` | protobuf 안의 JSON | 맞춤 지시 본문과 켜짐 여부 | [3] |
| `files/datastore/*_user_settings.preferences_pb` | protobuf 안의 JSON | 채팅 기록 끄기 설정 등 | [3] |
| `shared_prefs/analytics-android-oai.xml` | SharedPreferences XML | 분석 도구(Segment) 식별자, 이메일, 앱 버전 | [3] |
| `cache/files/` | 이미지 등 | 앱이 캐시한 이미지 | [3] |

ALEAPP 은 대화 DB 파일 이름에서 `_conversations.db` 앞부분을 떼어 "Account" 칸으로 보여 줍니다 [3]. 같은 꼬리의 파일이 여러 개 있으면 앞부분별로 따로 읽고, `_accountuser_state` 의 계정 목록과 검체에서 맞춰 봅니다.

메시지 표는 앱 판에 따라 두 가지입니다. 예전 판은 `DBMessage` 표의 `messageNode` 칸에 메시지 JSON 을 통째로 두었고, 나중 판은 `DBMessageChunk` 표에 메시지 JSON 을 여러 조각으로 나눠 둡니다 [3][4]. ALEAPP `chatgpt.py` 는 `DBMessage.messageNode` 칸이 없으면 예전 형식 읽기를 건너뛰고 `chatgpt2.py` 가 새 형식을 읽습니다. 시험 이미지(Android 15, 버전 코드 2525902)에서는 예전 형식이 0행, 새 형식이 12행이었습니다 [3][4].

## 구조

형식별 읽는 법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html)와 [설정 XML과 SharedPreferences](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/shared-preferences.html)에서 다루고, 여기서는 ChatGPT 앱에 해당하는 표·칸·키만 적습니다.

### 대화 목록: `DBConversation`

칸은 `id` 와 `conversation` 이고, `conversation` 칸에 대화 하나의 JSON 이 들어 있습니다 [3].

| JSON 키 | 뜻 |
|---|---|
| `$.id` | 대화 ID(ALEAPP 칸 이름 Conversation ID, 행의 `id` 칸은 ID) |
| `$.remote_id` | 원격 ID(ALEAPP 칸 이름 Remote ID) |
| `$.title`, `$.has_title` | 대화 제목, 제목이 붙었는지 여부 |
| `$.creation_date`, `$.modification_date` | 대화를 만든 시각, 고친 시각(ISO 8601) |
| `$.moderation_results` | 검토(moderation) 결과 |
| `$.gizmo_id` | ALEAPP 칸 이름 Gizmo ID |

### 메시지(예전 형식): `DBMessage`

칸은 `id`, `conversationId`, `messageNode` 이고, `conversationId` 가 `DBConversation.id` 와 이어집니다 [3].

| `messageNode` 안 JSON 키 | 뜻 |
|---|---|
| `$.content.role`, `$.content.role_name` | 누가 쓴 메시지인지 |
| `$.content.content.content` | 본문 |
| `$.content.date` | 메시지 시각(ISO 8601) |
| `$.content.attachments` | 첨부 |
| `$.content.model` | 답한 모델 |
| `$.content.is_complete`, `is_blocked`, `is_flagged`, `is_interrupted` | ALEAPP 칸 이름 Complete, Blocked, Flagged, Interrupted(참이면 Yes) |
| `$.content.is_user_system_message`, `is_voice_message` | ALEAPP 칸 이름 User System Message, Voice Message(참이면 Yes) |

### 메시지(새 형식): `DBMessageChunk`

칸은 `messageId`, `chunkIndex`, `chunk`(BLOB) 입니다 [4]. 같은 `messageId` 의 `chunk` 를 `chunkIndex` 순서로 이어 붙여 UTF-8 로 읽으면 JSON 하나가 됩니다.

| 이어 붙인 JSON 키 | 뜻 |
|---|---|
| `content.conversation_id` | 이 메시지가 속한 대화(`DBConversation.id` 와 맞춤) |
| `content.created_date`, `content.modification_date` | 만든 시각, 고친 시각 |
| `content.content` | 본문. 사전(dict)이면 그 안의 `content` 가 본문이고 `references` 가 참조 목록이며, 일부 도구·음성 메시지는 그냥 문자열입니다 |

보조 자료인 LEAF 문서는 조각 JSON 에 `role`(User 또는 Assistant), `model`, `is_visually_hidden_in_conversation` 가 있다고 적었고, LEAF 파서는 이 값이 참인 조각을 건너뜁니다 [8]. ALEAPP `chatgpt2.py` 는 이 세 키를 읽지 않아서 [4], 도구 결과에는 역할과 숨김 여부가 나오지 않습니다. 이 키가 JSON 의 어느 층에 있는지는 검체에서 확인합니다.

### 계정·설정 파일: `files/datastore/*.preferences_pb`

이 파일들은 protobuf 로 감싼 JSON 입니다. ALEAPP 은 protobuf 를 풀어 필드 1 → 2 → 5 에 든 바이트를 JSON 으로 읽습니다 [3].

| 파일 꼬리 | JSON 키 |
|---|---|
| `_user` | `id`, `email`, `name`, `created`(Unix 초), `picture` |
| `_accountstatus` | `accounts` 아래 계정마다 `account_id`, `account_user_id`, `plan_type`, `structure`, `is_deactivated`, `subscription.plan`, `subscription.purchase_origin`, `subscription.will_renew` |
| `_accountuser_state` | `active_account_id`, `available_account_users[]` 의 `account`(위와 같은 키, `subscription.expiration_date` 포함)와 `user`(`id`, `email`, `name`, `created`, `picture`) |
| `_custom_instructions` | `enabled`, `about_user_message`, `about_model_message` |
| `_user_settings` | `history_disabled`, `seen_custom_instructions_introduction`, `has_seen_voice_intro`, `has_seen_voice_selection` |

`about_user_message` 와 `about_model_message` 는 사용자가 직접 쓴 글이라서 대화 본문처럼 다룹니다. `history_disabled` 는 ALEAPP 이 "Chat History Disabled" 로 보여 주는 값으로, 사용자가 채팅 기록 끄기를 켰는지 알려 줍니다 [3].

### 분석 도구 식별자: `shared_prefs/analytics-android-oai.xml`

`<string>` 항목 가운데 `segment.userId`, `segment.anonymousId`, `segment.device.id`, `segment.app.version`, `segment.traits` 를 씁니다 [3]. `segment.traits` 는 JSON 이고 안에 `email`, `workspace_id`, `account_has_plus`, `plan_type`, `has_active_subscription` 가 있습니다. 이 파일에는 XML 에 쓸 수 없는 제어 문자가 섞여 있을 때가 있어서, ALEAPP 은 첫 읽기가 실패하면 제어 문자를 지우고 다시 읽습니다 [3].

Google Play 데이터 안전 항목에는 "기기 또는 그 밖의 ID 를 제3자와 공유" 가 신고돼 있고 [9], 기기 안에서는 이 파일의 `segment.device.id`·`segment.anonymousId` 같은 식별자 값을 볼 수 있습니다 [3]. 두 값이 신고된 공유 대상과 같은 것인지는 공개된 분석 자료가 없어 검체로 확인해야 합니다.

### 데이터 안전 항목

Google Play 데이터 안전 페이지는 앱 개발사가 신고한 내용이고, 2026-09-25 에 본 내용은 다음과 같습니다 [9].

| 구분 | 신고된 항목 |
|---|---|
| 수집 — 앱 정보·성능 | 오류 기록, 진단, 그 밖의 성능 데이터 |
| 수집 — 메시지 | 앱 안 메시지(선택 항목) |
| 수집 — 개인 정보 | 이름, 이메일 주소, 주소, 전화번호 |
| 수집 — 앱 활동 | 앱 안 상호작용, 사용자가 만든 콘텐츠 |
| 수집 — 위치 | 대략적인 위치 |
| 제3자와 공유 | 기기 또는 그 밖의 ID(광고·마케팅, 사기 방지·보안·규정 준수 목적) |
| 보안 | 전송 구간 보안 연결, 사용자가 데이터 삭제를 요청할 수 있음 |

여기서 "수집" 은 앱이 데이터를 서버로 보낸다는 신고이고, 기기에 무엇이 남는지는 위 구조 절로 판단합니다. 개발사가 이 항목을 고쳐 쓸 수 있어서, 보고서에 인용할 때는 본 날짜를 함께 적습니다.

## 증거로서 의미

**증명하는 것.** `*_conversations.db` 에 대화 행이 있으면 그 계정으로 그 제목의 대화가 있었고, 그 사본이 이 기기에 내려와 있었다고 쓸 수 있습니다. 메시지 행이 있으면 대화 안의 글을 읽을 수 있고(예전 형식은 `role` 칸으로 쓴 쪽을 나눕니다), `created_date`·`modification_date` 로 메시지가 언제 만들어졌는지 알 수 있습니다. `_user`·`_accountuser_state` 파일은 이 기기에 로그인한 계정의 이메일·이름·요금제를 알려 주고, `_custom_instructions` 는 사용자가 모델에 준 지시를 알려 줍니다.

**증명하지 못하는 것.** 대화 행이 있다는 사실만으로 그 대화를 이 기기에서 입력했다고 쓸 수는 없습니다. 같은 계정을 웹이나 다른 기기에서도 썼다면 그쪽에서 한 대화가 이 DB 에 들어오는지 검체로 가려야 합니다. 또 기기에 대화가 없다고 대화를 하지 않았다고 볼 수 없는데, 채팅 기록을 껐거나(`history_disabled`), 앱에서 지웠거나, 앱을 다시 깔았을 수 있습니다. 기기를 쓴 사람이 누구인지는 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)에서처럼 다른 기록과 맞춥니다.

보고서에는 "이 기기의 ChatGPT 앱 데이터베이스에 이 계정의 대화 N 건과 메시지 M 건이 있고, 가장 이른 메시지 생성 시각은 이렇다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

| 값 | 형식 | 근거 |
|---|---|---|
| `DBConversation` 의 `creation_date`, `modification_date` | ISO 8601 문자열. ALEAPP 은 끝의 `Z` 를 UTC 로 읽습니다 | [3] |
| `DBMessage` 의 `$.content.date` | ISO 8601 문자열 | [3] |
| `DBMessageChunk` JSON 의 `created_date`, `modification_date` | `%Y-%m-%dT%H:%M:%S.%fZ` 또는 소수점 없는 `%Y-%m-%dT%H:%M:%SZ`, UTC | [4] |
| `_user`·`_accountuser_state` 의 `created` | Unix 초, UTC | [3] |

대화의 `modification_date` 가 무엇이 바뀔 때 갱신되는지는 공개된 자료가 없어서, 대화를 연 시각으로 읽지 않고 메시지 하나하나의 `created_date` 를 함께 봅니다. `created` 는 ALEAPP 이 "Account Creation Time" 으로 보여 주는 값이라서 [3], 이 기기에 로그인한 시각으로 옮기지 않습니다.

앱 폴더 안 파일의 파일 시스템 시각은 동기화나 캐시 갱신 때도 바뀌어서 대화한 시각으로 바로 옮기지 않습니다. 앱 설치·업데이트 시각과 기기의 다른 기록을 한 줄로 세우는 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-android/03-techniques/analysis/timeline/index.html)과 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **WAL 을 함께 수집합니다.** 최근 대화는 `-wal` 파일에만 있을 수 있어서, `*_conversations.db` 하나만 떼어 오면 행이 빠집니다. ALEAPP 도 `*_conversations.db*` 패턴으로 WAL 을 함께 가져옵니다 [3].
- **메시지 형식을 먼저 가립니다.** `DBMessage` 에서 0행이 나와도 `DBMessageChunk` 에 메시지가 있을 수 있습니다. 두 표를 모두 봅니다.
- **시험 범위가 좁습니다.** 공개 분석기가 시험한 판은 1.2024.177 까지와 버전 코드 2525902 하나입니다 [3][4]. 다른 판에서 표·키 이름이 바뀌면 도구가 조용히 0행을 낼 수 있어서, 도구 결과가 비면 DB 를 직접 열어 표 목록부터 봅니다.
- **캐시 이미지는 대화와 이어져 있지 않습니다.** ALEAPP 은 `cache/files/` 안에서 이미지로 열리는 파일을 모을 뿐이라서 [3], 이미지 하나가 어느 대화에서 왔는지는 파일 이름이나 메시지 JSON 의 첨부 값과 따로 맞춰 봅니다.
- **지운 대화.** GMDSOFT 는 자사 도구(MD-NEXT·MD-RED)로 Android ChatGPT 앱에서 지운 대화방을 복구하고 로그인하지 않은 세션의 흔적도 다룬다고 밝혔지만, 어느 파일의 어느 칸인지는 공개하지 않았습니다 [5]. 지운 행은 SQLite 의 빈 페이지나 WAL 에 남을 수 있으니 [내용 복구](../../../03-techniques/analysis/content-recovery.md)의 방법으로 찾습니다.
- **토큰.** 앱 데이터에서 접근 토큰이 나오면 [API 키와 토큰](../../../01-foundations/storage-model/api-keys-tokens.md)에 따라 보고서에서 가립니다. 서버에 있는 대화는 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)이나 [계정 데이터 내보내기](export.md)로 확보합니다.
- **수집 범위.** 앱 데이터 폴더는 기기를 수집한 방법에 따라 얻을 수도 있고 못 얻을 수도 있습니다. 폴더가 비어 보이면 앱 동작 때문인지 수집 범위 때문인지부터 가립니다. 수집 범위를 정하는 방법은 [기기에서 AI 흔적 모으기](../../../03-techniques/acquisition/endpoint-triage.md)에 있습니다.
- **비슷한 앱.** 브라우저로 쓴 ChatGPT 는 앱이 아니라 [웹 브라우저](web.md) 흔적으로 남습니다. 이름이 비슷한 비공식 앱도 있을 수 있어서, 패키지 이름이 `com.openai.chatgpt` 와 정확히 같은지 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

`*_conversations.db` 의 처음 16바이트는 SQLite 머리 글자 `SQLite format 3` 과 NUL 이어야 하고, 이 글자가 보이면 암호화되지 않은 SQLite 입니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

`DBMessageChunk.chunk` 한 칸을 헥스로 보면 UTF-8 JSON 의 일부가 그대로 읽힙니다. 아래는 만든 예시이고, 키 순서와 조각 경계는 검체마다 다릅니다.

```
00000000  7B 22 63 6F 6E 74 65 6E 74 22 3A 7B 22 63 6F 6E  {"content":{"con
00000010  76 65 72 73 61 74 69 6F 6E 5F 69 64 22 3A 22 30  versation_id":"0
00000020  30 30 30 61 61 61 61 2D 31 31 31 31 2D 32 32 32  000aaaa-1111-222
```

조각이 JSON 중간에서 끊기는 것이 정상이라서, 한 조각만 보고 JSON 이 깨졌다고 판단하지 않습니다.

### SQL 로 한 번

사본 DB 를 SQLite 3.44 이상에서 열면 조각을 순서대로 이어 붙여 메시지 JSON 을 얻을 수 있습니다.

```sql
SELECT messageId,
       group_concat(CAST(chunk AS TEXT), '' ORDER BY chunkIndex) AS message_json
FROM DBMessageChunk
GROUP BY messageId;
```

대화 목록은 다음처럼 뽑습니다.

```sql
SELECT id,
       json_extract(conversation, '$.title')             AS title,
       json_extract(conversation, '$.creation_date')     AS created,
       json_extract(conversation, '$.modification_date') AS modified,
       json_extract(conversation, '$.gizmo_id')          AS gizmo
FROM DBConversation;
```

`message_json` 에서 `$.content.conversation_id` 를 뽑아 `DBConversation.id` 와 맞추면 메시지가 어느 대화에 속하는지 알 수 있습니다.

### 공개 도구로 한 번

ALEAPP 에 앱 데이터 폴더가 든 추출본을 넣으면 "ChatGPT" 분류 아래에 대화 목록(Conversations Metadata), 예전 형식 메시지(Messages (Legacy)), 새 형식 메시지(Conversations), 사용자·계정 상태·맞춤 지시·사용자 설정·분석 식별자·캐시 이미지가 따로 나옵니다 [3][4]. 도구가 보여 주는 값은 위 SQL 결과와 맞춰 봅니다.

## 교차 검증

기기의 대화 사본은 [계정 데이터 내보내기](export.md)로 받은 `conversations.json` 의 같은 대화와 제목·시각을 맞춥니다. `remote_id` 가 내보내기의 대화 ID 와 같은지도 검체로 맞춰 봅니다. 접속 시간대는 [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)으로 보고, 같은 사람이 브라우저로도 썼다면 [크롬 (Chrome for Android)](https://urock-ailab.github.io/forensics-handbook-android/02-artifacts/browsers/chrome/index.html) 기록도 함께 봅니다. 같은 계정을 쓴 iPhone 이 있으면 [iOS 앱](ios.md)의 대화 사본과도 맞춥니다.

## 실습

시험용 기기나 에뮬레이터에 앱을 깔고 시험용 계정으로 가짜 대화를 만든 뒤 앱 데이터 폴더를 수집해 다음을 풀어 봅니다.

1. `databases/` 에 생긴 `*_conversations.db` 의 표 목록을 보고, 메시지가 `DBMessage` 와 `DBMessageChunk` 가운데 어디에 있는지 적습니다.
2. 대화 하나의 `creation_date` 와 첫 메시지의 `created_date` 를 비교하고, 둘 다 UTC 인지 확인합니다.
3. `files/datastore/` 의 `_user_settings` 파일에서 `history_disabled` 값을 읽은 뒤, 앱에서 채팅 기록을 끄고 다시 수집해 값이 어떻게 바뀌는지 봅니다.
4. 앱에서 대화 하나를 지운 뒤 다시 수집해, 본 DB 와 `-wal` 에 그 대화의 제목이 남는지 문자열로 찾아봅니다.
5. 로그아웃한 채로 앱을 쓴 뒤 `databases/` 와 `files/datastore/` 에 어떤 파일이 생기는지 적습니다.

## 참고 문헌

1. Evangelos Dragonas, Costas Lambrinoudakis, Panagiotis Nakoutis, "Forensic analysis of OpenAI's ChatGPT mobile application", Forensic Science International: Digital Investigation, 50 (2024), 301801. https://doi.org/10.1016/j.fsidi.2024.301801
2. Sonali Tyagi, Yufeng Gong, Umit Karabiyik, "Forensic analysis and privacy implications of LLM mobile apps: A case study of ChatGPT, Copilot, and Gemini", Forensic Science International: Digital Investigation, 54 (2025), 301974. https://doi.org/10.1016/j.fsidi.2025.301974 (초록)
3. ALEAPP, `scripts/artifacts/chatgpt.py`(작성 Evangelos Dragonas, 2026-08-01 갱신) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/chatgpt.py
4. ALEAPP, `scripts/artifacts/chatgpt2.py`(작성 Alexis Brignoni, 2026-07-10 갱신) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/chatgpt2.py
5. GMDSOFT Tech Letter Vol.21, "ChatGPT Q&A: 10 Key Questions", Forensic Focus, 2026-05-20 — https://www.forensicfocus.com/news/gmdsoft-tech-letter-vol21-chatgpt-qa-10-key-questions/
6. Kendall J. Comeaux, Trevor T. Spinosa, Ali Ghosn, Ibrahim Baggili, "Ex Machina: A forensic evaluation of AI companion applications and their evidentiary value", Forensic Science International: Digital Investigation, 56 (2026), 302050. https://doi.org/10.1016/j.fsidi.2026.302050 (2절 관련 연구)
7. Sungjo Jeong, Sangjin Lee, Jungheum Park, "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987. https://doi.org/10.1016/j.fsidi.2025.301987 (2.1절)
8. LEAF-Digital-Forensics, `leaf/README.md`(보조 자료) — https://github.com/MarcosAOSperoni/LEAF-Digital-Forensics
9. Google Play, ChatGPT 데이터 안전 — https://play.google.com/store/apps/datasafety?id=com.openai.chatgpt
