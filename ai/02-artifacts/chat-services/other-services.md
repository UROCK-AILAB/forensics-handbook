---
title: "그 밖의 서비스"
parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 380
---

# 그 밖의 서비스 (DeepSeek·Grok 등)

DeepSeek·Grok 처럼 따로 페이지를 두지 않은 대화형 AI 서비스의 수집·보관 규칙과 Android 앱의 저장 구조를 같은 기준으로 모았습니다.

Replika·Character.AI 같은 AI 컴패니언 앱은 [AI 컴패니언 앱](companion-apps.md)에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

조사에서는 대화 원본이 서버에 있는지 기기에 있는지부터 가립니다. 이 기준은 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다. 두 서비스는 기기에 남기는 것이 크게 다릅니다. DeepSeek Android 앱은 대화 목록과 메시지 본문을 SQLite 에 저장하고[3][4], Grok Android 앱에는 계정 정보와 영상 캐시가 남습니다[6].

### DeepSeek

DeepSeek 의 개인정보 처리방침은 앱과 웹에 모두 적용되고, 쿠키 같은 일부 항목만 웹에 해당합니다[1]. DeepSeek 이 수집하는 사용자 입력은 텍스트, 음성, 프롬프트, 올린 파일, 사진, 피드백, 채팅 기록이고, 사용자가 올린 음성·사진에서 음성 인식 정보, 얼굴 인식 정보 같은 고유한 생체 정보는 뽑아내지 않습니다[1]. 함께 수집하는 기기 정보는 기기 모델, 운영체제, IP 주소, 기기 식별자, 시스템 언어이고, 네트워크 정보는 이동 통신사, MCC, MNC, 접속 방식, IP 주소입니다[1]. 서버 자료를 받으면 대화 내용뿐만 아니라 어느 기기·어느 IP 에서 접속했는지도 맞춰 볼 수 있습니다.

DeepSeek 서버는 중화인민공화국에 있습니다[1]. 서버 쪽 자료를 요청할 때 어느 나라 절차를 거쳐야 하는지가 여기서 갈리고, 절차는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)에서 다룹니다.

Android 앱(패키지 `com.deepseek.chat`)은 사용자별 데이터베이스에 대화 목록을 두고, 대화 하나마다 메시지 표를 따로 만듭니다[4][7]. 계정 정보는 다른 데이터베이스에 있고, 여기에 인증 토큰·이메일·전화번호가 함께 들어 있습니다[5]. 기기를 확보하면 서버 자료 없이도 대화 본문을 볼 수 있다는 뜻입니다.

### Grok (xAI)

Grok 은 2023-11 에 X(옛 Twitter) 안의 기능으로 일부 사용자에게 먼저 공개됐습니다[2]. grok.com 웹과 iOS 앱은 2024-12 에 베타로 나와 2025-01-09 에 전 세계에 공개됐고, Android 앱은 2025-02-04 에 일부 지역부터 나왔습니다[2]. 3D 애니메이션 캐릭터와 대화하는 동반자 기능(2025-07), 이미지 생성 Aurora(2024-12-09), 영상 생성 Grok Imagine(2025-07-28) 같은 기능이 있어서[2], 흔적은 대화 글뿐만 아니라 생성한 이미지·영상으로도 이어집니다. 생성물 흔적의 일반 원리는 [Midjourney와 이미지 생성 서비스](../generative-media/image-generation.md)에서 다룹니다.

Android 앱(패키지 `ai.x.grok`)에서 읽을 수 있는 흔적은 두 가지입니다[6]. 하나는 앱에 들어간 고객 지원 SDK(Intercom)가 설정 XML 에 남긴 계정 속성이고, 다른 하나는 Grok Imagine 영상을 재생하면서 쌓인 영상 캐시입니다. Android 기기에서 대화 본문이 어디에 남는지는 공개된 분석 자료가 없어 검체로 확인해야 하고, ALEAPP 에도 Grok 대화 분석기는 없습니다.

같은 Grok 을 X 앱 안에서도, grok.com 에서도, 전용 앱에서도 쓸 수 있어서 한 사용자의 흔적이 세 곳에 흩어질 수 있습니다. X 계정으로 쓴 Grok 대화가 X 데이터 내보내기(아카이브)에 들어가는지는 공개 자료가 없어서, 받은 아카이브의 파일 목록으로 직접 확인합니다.

### 그 밖(Le Chat, Kimi, Qwen 등)

이런 서비스를 만나면 아래 표와 같은 칸(제공 형태, 서버 위치, 보관 기간, 내보내기, 기기 저장 위치)을 사건 당시의 처리방침과 검체로 하나씩 채웁니다. 근거가 없는 칸은 비워 두고, 보고서에도 비어 있다고 적습니다.

## 위치와 버전별 차이

| 항목 | DeepSeek | Grok |
|---|---|---|
| 제공 형태 | 앱과 웹(처리방침 적용 범위)[1] | X 안의 기능, grok.com 웹, iOS 앱, Android 앱[2] |
| 서버 위치 | 중화인민공화국[1] | 사건 당시 xAI 처리방침으로 확인 |
| 대화·계정 보관 | 계정 탈퇴 때까지 또는 이용 목적을 이룰 때까지[1] | 사건 당시 xAI 처리방침으로 확인 |
| 데이터 내보내기 | 현재 웹 버전에서만 가능[1] | 사건 당시 xAI 처리방침으로 확인 |
| 계정 삭제 뒤 | 계정과 관련 콘텐츠·개인정보를 되살릴 수 없음[1] | 사건 당시 xAI 처리방침으로 확인 |
| Android 패키지 | `com.deepseek.chat`[3] | `ai.x.grok`[6] |
| Android 대화 본문 | SQLite 에 있음[4] | 공개 분석 자료 없음, 검체로 확인 |
| iOS·웹·PC 저장 위치 | 공개 분석 자료 없음, 검체로 확인 | 공개 분석 자료 없음, 검체로 확인 |

DeepSeek 은 웹사이트 방문 기록을 통신 관련 법에 따라 3개월, 거래 기록을 소비자 보호 법에 따라 5년 보관합니다[1]. 근거 법이 어느 나라 법인지는 사건 당시의 원문판에서 확인합니다. 같은 주소라도 접속 지역에 따라 다른 언어판이 열릴 수 있어서, 사건에 쓸 때는 원문판을 따로 확보해 인용 문장과 대조합니다.

Android 쪽 파일은 모두 앱 데이터 폴더(`/data/data/패키지 이름/`) 아래에 있습니다. 폴더 구조와 수집 방법은 [Android 앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/app-data-layout.html)를 따릅니다.

| 서비스 | 경로(앱 데이터 폴더 기준) | 담긴 것 | 근거 |
|---|---|---|---|
| DeepSeek | `databases/deepseek_chat_사용자UUID.db` | 대화 목록(`chat_session_list`), 대화별 메시지 표 | [3][4][7] |
| DeepSeek | `databases/deepseek_chat.db` | 계정 정보(`app_user_info`) | [5][7] |
| DeepSeek | `files/mmkv/mmkv.default`, `files/mmkv/사용자UUID` | MMKV 키-값 저장소. `mmkv.default` 에 `key_user_info`(이메일·토큰이 든 프로필 JSON)가 있음 | [7] |
| Grok | `shared_prefs/INTERCOM_SDK_USER_PREFS.xml`, `shared_prefs/INTERCOM_DEDUPER_PREFS.xml` | Intercom SDK 가 저장한 계정 속성 | [6] |
| Grok | `databases/exoplayer_internal.db` | 영상 캐시 색인과 캐시 파일별 메타데이터 | [6] |
| Grok | `cache/*/video-cache/*/*.exo` | 영상 캐시 조각 파일 | [6] |

분석기마다 시험한 판이 다릅니다. ALEAPP 의 Grok 분석기는 Grok 1.0.71(2025-11-11)로 시험한 것이고, 영상 분석기의 마지막 수정은 2026-08-01 입니다[6]. DeepSeek 분석기 세 개(2026-05-24 작성)에는 시험한 앱 판이 적혀 있지 않습니다[3][4][5]. 두 앱 모두 지금 판과 구조가 다를 수 있어서, 검체에서 표 이름과 칸을 먼저 확인한 뒤 분석기 결과를 씁니다.

## 구조

### DeepSeek — 대화 목록

`deepseek_chat_사용자UUID.db` 의 `chat_session_list` 표에 대화 하나가 한 행으로 들어가고, 칸은 아래와 같습니다[3][7]. ALEAPP 은 이 가운데 `id`, `title`, `updated_at` 세 칸만 읽습니다[3].

| 칸 | 형식 | 뜻 | 근거 |
|---|---|---|---|
| `id` | TEXT | 대화 ID. 메시지 표 이름 끝에 붙는 값 | [3][7] |
| `title` | TEXT | 대화 제목 | [3] |
| `updated_at` | REAL | 마지막으로 갱신된 시각(Unix 초, 소수) | [3][7] |
| `inserted_at` | REAL | 대화를 만든 시각(Unix 초, 소수) | [7] |
| `titleType` | TEXT | 제목 종류. 시험 대화 두 개에서는 `SYSTEM` | [7] |
| `pinned` | INTEGER | 고정 여부 | [7] |
| `current_message_id`, `cache_version`, `schema_version` | INTEGER | 앱 내부 관리 값 | [7] |

### DeepSeek — 대화별 메시지 표

대화마다 `chat_session_messages_대화UUID` 라는 이름의 표가 따로 생깁니다[4][7]. 그래서 표를 모두 뽑으려면 `sqlite_master` 에서 `chat_session_messages_%` 로 찾아야 하고, ALEAPP 도 이렇게 찾습니다[4].

| 칸 | 형식 | 뜻 | 근거 |
|---|---|---|---|
| `role` | TEXT | 말한 쪽(`USER`·`ASSISTANT`) | [4][7] |
| `inserted_at` | REAL | 메시지가 들어간 시각(Unix 초, 소수) | [4][7] |
| `fragments` | TEXT | 본문 조각을 담은 JSON 배열 | [4][7] |
| `message_id`, `parent_id` | INTEGER | 메시지 ID 와 부모 메시지 ID | [7] |
| `thinking_enabled` | INTEGER | 추론 모드를 켰는지(0/1) | [7] |
| `status` | TEXT | 응답 상태(예: `FINISHED`) | [7] |
| `feedback_type`, `accumulated_token_usage` | TEXT, INTEGER | 피드백 종류와 누적 토큰 수 | [7] |

`fragments` 배열의 각 항목에는 `type` 과 `content` 가 있고, 사용자 입력은 `type` 이 `REQUEST`, 응답은 `RESPONSE` 입니다[4][7]. ALEAPP 은 이 두 종류의 `content` 만 이어 붙여 보여 주므로[4], 다른 `type` 의 항목이 있으면 분석기 결과에서 빠집니다. 원본 JSON 은 한 번 직접 봅니다. 아래는 이 구조를 따라 만든 예시입니다.

```json
// 만든 예시: 사용자 메시지 행의 fragments
[{"type": "REQUEST", "id": 1, "content": "회의록을 세 줄로 줄여 줘"}]
// 만든 예시: 응답 행의 fragments
[{"type": "RESPONSE", "id": 1, "content": "1. ... 2. ... 3. ...", "references": [], "stage_id": 1}]
```

### DeepSeek — 계정 정보

`deepseek_chat.db` 의 `app_user_info` 표에는 `id`, `token`, `email`, `mobile_number` 칸이 있습니다[5]. 연동된 외부 로그인(OAuth) 프로필을 담은 JSON 칸 `id_profiles` 와 `chat_status`, `status`, `need_birthday` 칸도 있습니다[7]. `token` 은 인증 토큰이라 보고서에서는 가리고, 다루는 원칙은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)을 따릅니다. `mmkv.default` 의 `key_user_info` 에도 토큰이 있으니 같은 원칙을 적용합니다[7].

### Grok — 계정 속성

두 Intercom 설정 XML 에 든 키는 아래와 같습니다[6]. 설정 XML 자체의 형식은 [설정 XML과 SharedPreferences](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/data-formats/shared-preferences.html)에 있습니다.

| 키 | 담긴 것 |
|---|---|
| `CachedAttributes` | JSON. `name`, `email`, 그리고 `custom_attributes` 안의 `name`·`email`·`xUsername`(X 계정 이름) |
| `intercomsdk-session-INTERCOM_SDK_USER_ID` | Intercom 쪽 사용자 ID |
| `intercomsdk-session-INTERCOM_SDK_EMAIL_ID` | Intercom 쪽 이메일 ID |

ALEAPP 은 `custom_attributes` 안에 `name`·`email` 이 있으면 바깥 값 대신 그 값을 보여 줍니다[6]. 두 값이 다를 수 있어서 보고서에는 원본 JSON 도 함께 적습니다.

### Grok — 영상 캐시

영상 캐시는 AndroidX Media3 의 SimpleCache 형식입니다[6][8]. `exoplayer_internal.db` 에서 이름이 `ExoPlayerCacheIndex` 로 시작하는 표에는 `id` 와 `key`(원래 URL)가 있고, `ExoPlayerCacheFileMetadata` 로 시작하는 표에는 캐시 파일 이름(`name`), 길이(`length`), `last_touch_timestamp`(ms)가 있습니다[6]. 표 이름 뒤에 다른 글자가 붙을 수 있어서 ALEAPP 도 앞부분으로 찾습니다[6].

캐시 파일 이름은 `색인ID.위치.시각.v3.exo` 꼴입니다[8]. 첫 값은 `ExoPlayerCacheIndex` 의 `id` 와 이어지고, 두 번째 값은 원래 파일 안에서 이 조각이 시작하는 위치이며, 세 번째 값은 Unix ms 시각입니다[8]. ALEAPP 은 첫 값으로 원래 URL 을 찾아, URL 이 `https://assets.grok.com/users/` 로 시작하면 사용자가 만든 영상(User Generated)으로, 아니면 공개 영상(Public)으로 나눕니다[6].

## 증거로서 의미

**증명하는 것.** DeepSeek 메시지 표의 행은 그 기기의 앱에 그 시각의 입력과 응답이 저장됐다는 기록이고, `app_user_info` 의 이메일·전화번호는 그 앱에 로그인한 계정을 가리킵니다. Grok 의 `CachedAttributes` 는 앱에 로그인한 계정의 이름·이메일·X 계정 이름을 보여 줍니다. Grok 영상 캐시의 원래 URL 이 `assets.grok.com/users/` 로 시작하면 사용자 생성 영상을 이 기기에서 불러온 기록입니다[6]. 서버 쪽 자료에는 처리방침이 적은 대로 채팅 기록과 함께 기기 정보·IP 주소가 있을 수 있어서[1], 확보하면 기기 기록과 맞춰 볼 수 있습니다.

**증명하지 못하는 것.** 앱에 남은 계정은 그 계정으로 로그인했다는 뜻일 뿐이고, 누가 기기를 들고 입력했는지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 좁힙니다. Grok 캐시 영상은 기기가 그 영상을 받아 재생에 썼다는 기록이라서, 영상을 끝까지 봤다거나 그 기기에서 만들었다는 것까지는 보이지 못합니다. 기기에 대화가 남아 있지 않다고 대화가 없었다고 할 수 없고, DeepSeek 계정을 지운 뒤라면 처리방침대로 되살릴 수 없어서[1] 서버 쪽 원본이 없다는 사실이 삭제 시점을 알려 주지도 않습니다.

## 시각 해석

DeepSeek 의 `updated_at`·`inserted_at` 은 Unix 초를 소수로 담은 REAL 값이고, ALEAPP 은 이를 UTC 로 바꿔 보여 줍니다[3][4]. 같은 대화 안의 메시지 순서는 `inserted_at` 으로 정할 수 있고, ALEAPP 도 이 값으로 정렬합니다[4]. 대화 목록의 `updated_at` 은 그 대화의 마지막 메시지 시각과 견주어, 메시지 없이 목록만 바뀐 때가 있는지 봅니다.

Grok 영상 캐시에는 시각이 두 개 있고 뜻이 다릅니다. 파일 이름의 시각은 Media3 가 캐시 파일을 쓰기 시작할 때의 기기 시계 값입니다[8]. `last_touch_timestamp` 는 캐시를 읽을 때마다 갱신되는 값이라 사용자가 본 시각이 아니고, 앱이 LRU 가 아닌 캐시 정리 방식을 쓰면 아예 갱신되지 않습니다[6][8]. Media3 는 파일 색인 DB 가 있으면 이 값을 DB 에만 쓰고 파일 이름은 바꾸지 않으며, 색인 DB 가 없을 때만 파일 이름을 새 시각으로 바꿉니다[8]. 두 값 모두 Unix ms 이고, ALEAPP 은 UTC 로 보여 줍니다[6].

서버 쪽 시각은 받은 파일 안의 시간대 표기를 직접 봅니다. 여러 출처의 시각을 시간순으로 합치는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

DeepSeek 데이터베이스는 WAL 모드라서, `-wal`·`-shm` 파일을 함께 수집하지 않으면 `sqlite_master` 에 표 이름은 보여도 대화 목록과 메시지 표가 비어 보일 수 있습니다[7]. 파일 세 개를 한 번에 복사하고, 읽는 방법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/data-formats/sqlite/index.html)를 따릅니다. ALEAPP 의 경로 패턴(`deepseek_chat_*.db*`)은 WAL 파일까지 함께 잡습니다[3][4].

메시지 표가 대화마다 따로 있어서, 표 하나만 열어 보고 대화가 이것뿐이라고 판단하면 안 됩니다. `chat_session_list` 의 ID 와 남은 메시지 표 이름을 맞춰 보고, 짝이 안 맞는 대화는 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)의 방법으로 WAL 과 여유 공간을 확인합니다.

ALEAPP Grok 영상 결과의 "Not Present" 는 `ExoPlayerCacheFileMetadata` 에 행은 있는데 캐시 폴더에 그 파일이 없다는 뜻입니다[6]. 앱이 캐시를 정리했을 수도, 누가 지웠을 수도 있어서 이것만으로 삭제 행위를 말할 수는 없지만, 파일 이름과 원래 URL 은 캐시에 있던 영상의 흔적으로 남습니다.

2025-08 에 일부 Grok 대화가 Google 검색에 색인돼 공개됐다는 보도가 있었습니다[2]. 검색에 드러난 대화는 서버에 있는 사본이라서, 기기에서 그 주소를 찾았다고 대화 본문이 기기에 있다고 볼 수는 없습니다.

비공개 대화 같은 기능 이름만 보고 "기록이 없다" 고 단정하지 말고, 사건 당시의 처리방침과 기기 저장소를 함께 확인합니다. 보관·삭제의 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다. DeepSeek 내보내기는 웹에서만 되니[1], 앱만 쓰던 사용자라도 웹에 로그인해서 받아야 합니다. 받는 동작 자체가 계정에 새 흔적을 남길 수 있어서 [계정 데이터 내보내기로 수집](../../03-techniques/acquisition/export-collection.md)의 절차대로 기록을 남기며 받습니다.

## 직접 분석해 보기

**헥스로 한 번.** SQLite 레코드 안의 REAL 값은 8바이트 빅 엔디언 IEEE 754 배정밀도입니다. DeepSeek `inserted_at` 을 헥스로 보면 아래처럼 읽습니다. 값은 명세대로 만든 예시이고, 검체에서 뜬 바이트가 아닙니다.

```
만든 예시(SQLite REAL, 빅 엔디언 배정밀도)
41 DA 55 6E 43 10 00 00   ->  1767225612.25  ->  2026-01-01 00:00:12.25 UTC
```

캐시나 할당되지 않은 영역에서 서비스 흔적을 찾을 때는 도메인 바이트로 찾습니다. 아래도 문자 인코딩 명세대로 만든 예시입니다.

```
만든 예시(인코딩 명세로 만든 바이트)
"deepseek.com"     UTF-8     64 65 65 70 73 65 65 6B 2E 63 6F 6D
"deepseek.com"     UTF-16LE  64 00 65 00 65 00 70 00 73 00 65 00 65 00 6B 00 2E 00 63 00 6F 00 6D 00
"assets.grok.com"  UTF-8     61 73 73 65 74 73 2E 67 72 6F 6B 2E 63 6F 6D
"grok.com"         UTF-16LE  67 00 72 00 6F 00 6B 00 2E 00 63 00 6F 00 6D 00
```

**공개 도구로 한 번.** 수집한 Android 파일 시스템 사본을 ALEAPP 에 넣으면 DeepSeek 세 항목(Chat Info, Chat Messages, User Info)과 Grok 두 항목(Videos, User Account)이 나옵니다[3][4][5][6]. 분석기 결과는 sqlite3 로 원본과 한 번 맞춰 봅니다. 경로와 파일 이름은 만든 예시입니다.

```sh
# 만든 예시 경로
python aleapp.py -t fs -i /cases/case-0005/android-fs -o /cases/case-0005/aleapp-out

DB=/cases/case-0005/android-fs/data/data/com.deepseek.chat/databases/deepseek_chat_0000-example.db
sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'chat_session_messages_%';"
sqlite3 "$DB" "SELECT m.role, datetime(m.inserted_at,'unixepoch'),
                      json_extract(j.value,'$.type'), json_extract(j.value,'$.content')
               FROM \"chat_session_messages_0000-example\" m, json_each(m.fragments) j
               ORDER BY m.inserted_at;"
```

`json_each` 로 풀면 `REQUEST`·`RESPONSE` 말고 다른 `type` 이 있는지도 함께 보입니다.

## 교차 검증

기기 흔적은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)과 시각을 맞춰 보고, 회사 기기라면 [보안 제품이 남기는 AI 사용 기록](../network-enterprise/dlp-casb.md)과 [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md)로 이어 갑니다. 웹으로 썼다면 [크롬 (Android)](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/browsers/chrome/index.html)이나 [크롬 계열 브라우저 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html)의 방문 기록과 맞춰 봅니다. Grok 생성 영상이 쟁점이면 [딥페이크·합성 이미지를 만들었나](../../04-scenarios/misuse/deepfake.md)를, 파일을 올렸는지가 쟁점이면 [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md)를 봅니다. 수집 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)에 있습니다.

## 실습

이 서비스들의 흔적이 든 공개 검체는 알려진 것이 없어서, 시험용 Android 기기와 시험 계정으로 풀어 봅니다.

1. DeepSeek 앱에서 대화 두 개를 만들고 하나를 지운 뒤, `chat_session_list` 의 행과 `chat_session_messages_` 표 목록이 어떻게 바뀌는지 적어 봅니다. WAL 파일을 빼고 연 결과와도 비교합니다.
2. 메시지 표의 `inserted_at` 과 대화 목록의 `updated_at` 을 UTC 로 바꾸고, 대화 제목을 바꾸거나 고정했을 때 `updated_at` 만 바뀌는지 확인합니다.
3. Grok 에서 영상을 하나 만들고 두 번 재생한 뒤, 캐시 파일 이름의 시각과 `last_touch_timestamp` 가 각각 어떻게 바뀌는지 비교합니다.
4. DeepSeek 웹에서 시험 계정의 데이터 내보내기를 받아, 기기 데이터베이스의 대화와 내보내기 파일의 대화가 같은지 맞춰 봅니다.

## 참고 문헌

1. DeepSeek 개인정보 처리방침(Privacy Policy), 최종 수정 2026-05-06 — https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html
2. Grok (chatbot) — 위키백과(영문, 2차 자료) — https://en.wikipedia.org/wiki/Grok_(chatbot)
3. ALEAPP, Deepseek Chat Info 분석기(RicardoBentoSantos, 2026-05-24) — https://github.com/abrignoni/ALEAPP , `scripts/artifacts/Deepseek_ChatInfo.py`
4. ALEAPP, Deepseek Chat Messages 분석기(RicardoBentoSantos, 2026-05-24) — https://github.com/abrignoni/ALEAPP , `scripts/artifacts/Deepseek_ChatMessages.py`
5. ALEAPP, Deepseek User Info 분석기(RicardoBentoSantos, 2026-05-24) — https://github.com/abrignoni/ALEAPP , `scripts/artifacts/Deepseek_UserInfo.py`
6. ALEAPP, Grok 분석기(Damien Attoe, Grok 1.0.71 시험, 2025-11-14 작성·2026-08-01 갱신) — https://github.com/abrignoni/ALEAPP , `scripts/artifacts/Grok.py`
7. LEAF Digital Forensics, 분석기 스키마 메모(Android 15, 2026-04-20 추출, 보조 근거) — https://github.com/MarcosAOSperoni/LEAF-Digital-Forensics , `docs/parser-schemas.md`
8. AndroidX Media3, SimpleCache·SimpleCacheSpan(release 브랜치) — https://github.com/androidx/media , `libraries/datasource/src/main/java/androidx/media3/datasource/cache/SimpleCache.java`, `libraries/datasource/src/main/java/androidx/media3/datasource/cache/SimpleCacheSpan.java`
