---
title: "AI 컴패니언 앱"
parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 390
---

# AI 컴패니언 앱 (Replika·Character.AI 등)

사용자가 고른 캐릭터와 친구·연인처럼 대화하는 AI 컴패니언 앱은 앱마다 대화를 두는 곳이 달라서, 기기에 평문 SQLite 로 남는 앱과 인증 토큰만 남는 앱을 먼저 가르고 읽어야 합니다.

저장 구조는 루팅한 Android 12(API 31) 에뮬레이터에서 여섯 앱을 시험한 논문[1] 기준이고, 그 뒤 판에서는 경로와 표가 바뀌었을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

AI 컴패니언 앱 (AI companion app) 은 사용자가 캐릭터(봇)를 정해 두고 오래 대화하는 앱입니다. 사용자가 감정이나 사생활을 털어놓는 일이 많아서, 논문은 이 앱이 사건에서 털어놓은 상대나 기록 보관소 구실을 할 수 있다고 봅니다[1]. 논문이 시험한 앱과 Google Play 다운로드 수는 아래와 같습니다[1].

| 앱 | 다운로드 수 | 봇 방식 | 사람끼리 메시지 기능 |
|---|---|---|---|
| Replika | 10M+ | 봇 하나 | 없음 |
| Kindroid | 500K+ | 정해 둔 캐릭터 중에서 고름 | 없음 |
| Character.AI | 5M+ | 사용자가 만든 봇 여럿 | 없음 |
| Linky.AI | 10M+ | 봇 여럿 | 있음 |
| Persona.AI | 500K+ | 봇 여럿 | 있음 |
| Fantasy.AI | 500K+ | 봇 여럿 | 있음 |

대화를 두는 곳은 세 갈래입니다. Replika·Linky.AI·Persona.AI·Fantasy.AI 는 대화를 기기 안 데이터베이스에 평문으로 두고, Kindroid 는 대화 본문을 서버(Firebase)에 두면서 일부 데이터를 암호화해 기기에 둡니다. Character.AI 는 기기에 대화를 두지 않고 인증 토큰과 기기 정보만 남깁니다[1]. 서버와 기기 중 어디를 먼저 볼지 가르는 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

Replika 는 대화와 함께 앱이 사용자에 대해 알아낸 사실을 `memory_fact_v3` 표에 따로 모으고, 대화 가운데 일부에는 봇의 "속마음" 글도 함께 남깁니다[1]. Persona.AI 와 Fantasy.AI 는 이름만 다를 뿐 같은 백엔드를 씁니다. 논문은 두 앱이 AI 처리용 역할 ID, 음성용 Agora SDK ID, 광고용 Unity3D 앱 키, 데이터베이스 스키마까지 같다고 보고했습니다[1]. 그래서 한 앱을 읽는 방법을 다른 앱에 그대로 쓸 수 있습니다.

## 위치와 버전별 차이

앱 폴더 이름은 논문 표와 도구 코드가 서로 다릅니다. 논문 부록 Table 4 는 `ai.character.rk/`, `com.linkyai/`, `com.persona.ai/`, `com.fantasy.ai/` 로 적었고[1], 도구 코드는 아래 표의 패키지 이름으로 폴더를 찾습니다[2]. 도구 코드는 이 이름으로 추출본 안의 앱 폴더를 찾으므로 폴더를 찾을 때는 코드 쪽 이름을 먼저 대 보고, 두 쪽 모두 맞지 않으면 아래 파일 이름으로 검체 전체를 찾습니다.

| 앱 | 도구 코드의 패키지 이름[2] | 논문 표의 폴더[1] | 대화 본문 |
|---|---|---|---|
| Replika | `ai.replika.app` | (적지 않음) | 기기 |
| Kindroid | `com.kindroid.app` | (적지 않음) | 서버(Firebase) |
| Character.AI | `ai.character.app` | `ai.character.rk/` | 서버 |
| Linky.AI | `com.aigc.ushow.ichat` | `com.linkyai/` | 기기 |
| Persona.AI | `com.aipersona.camera` | `com.persona.ai/` | 기기 |
| Fantasy.AI | `online.fantasyai.android` | `com.fantasy.ai/` | 기기 |

앱 데이터 폴더(`/data/data/` 아래 패키지 폴더) 기준으로 볼 파일은 아래와 같습니다. 폴더 구조의 일반 설명은 [Android 앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html)에 있습니다.

| 앱 | 파일 | 담긴 것 | 출처 |
|---|---|---|---|
| Replika | `databases/REPLIKA_DB` | 대화, 사용자·봇 프로필, 사용자 사실(`memory_fact_v3`) | [1][2] |
| Kindroid | `files/PersistedInstallation.*.json` | Firebase 설치 토큰, 갱신 토큰, 설치 ID | [2] |
| Kindroid | `shared_prefs/com.kindroid.app_preferences.xml` | RevenueCat 항목에 든 사용자 ID | [2] |
| Kindroid | `app_webview/Default/Local Storage/leveldb/` | 캐릭터 ID(`ai_id`) | [2] |
| Kindroid | `app_webview/Default/IndexedDB/https_kindroid.ai_0.indexeddb.leveldb/` | Firebase 사용자 토큰 | [2] |
| Kindroid | `app_webview/IndexedDB` 의 `*.db` | 암호화된 봇 설정·배경 이야기, 사용자별 AI 기억, 말투 지시 | [1] |
| Character.AI | `databases/RKStorage` | 인증 토큰(`catalystLocalStorage` 표의 `AUTH_TOKEN` 키) | [1][2] |
| Character.AI | `shared_prefs/CodePush.xml`, `shared_prefs/appsflyer-data.xml`, `shared_prefs/FirebaseHeartBeat*.xml` | 앱 버전(`appVersion`), 버전 코드(`versionCode`), 기기 정보 | [2] |
| Linky.AI | `app_flutter/messages_user_<botID>.hive` | 봇이 한쪽으로 보낸 메시지 | [1] |
| Linky.AI | `app_flutter/OpenIM_v2_conv<convID>.*` | 주고받은 봇 대화 | [1][2] |
| Linky.AI | `databases/com.im_10.8.7.db` | 사람끼리 메시지 | [1] |
| Persona.AI·Fantasy.AI | `databases/ai_personal_db`, `ai_personal_db-wal` | 봇 대화 | [1][2] |
| Persona.AI·Fantasy.AI | `databases/com.im_10.8.7.db` | 사람끼리 메시지 | [1] |

출처끼리 다른 곳이 두 군데 더 있습니다. Kindroid 의 `PersistedInstallation` 파일을 논문 표는 `app_webview/Local Storage` 에 있다고 적었고[1], 도구 코드는 `files/` 폴더에서 `PersistedInstallation.` 뒤에 긴 이름이 붙은 JSON 을 코드에 적어 둔 파일 이름 그대로 읽습니다[2]. Linky.AI 대화 파일은 논문 본문이 `OpenIM_v2_conv<convIDNumber>.cd` 로 적으면서 같은 폴더의 파일이 `.hive` 와 `.db` 형식이라고 했고, 논문 표는 `.hive, .db` 로 적었습니다[1]. 도구 코드는 `app_flutter/` 에서 `OpenIM` 으로 시작하고 `.db` 로 끝나는 파일을 읽습니다[2]. 두 경우 모두 검체에서 파일 이름으로 찾아 실제 위치를 적습니다.

Kindroid 는 앱 화면을 웹뷰로 띄우는 구조라서 `app_webview/` 아래가 크롬 계열 프로필과 같은 모양입니다. 이 구조는 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)와 [LevelDB와 IndexedDB (Android)](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/leveldb-indexeddb.html)를 따라 읽습니다.

논문은 앱 버전을 적지 않았습니다. Character.AI 는 `shared_prefs/CodePush.xml` 의 `appVersion` 값으로 검체의 앱 버전을 알 수 있고, 도구 코드는 이 값을 못 읽으면 1.11.3 을 기본값으로 씁니다[2]. 다른 앱도 분석 결과에 검체의 앱 버전을 함께 적습니다.

## 구조

### Replika — `REPLIKA_DB`

평문 SQLite 입니다[1]. 도구 코드가 읽는 표와 칸은 아래와 같습니다[2].

| 표 | 칸 |
|---|---|
| `user_profile` | `id`, `first_name`, `last_name`, `email`, `birthday_date`, `user_gender_pronounce` |
| `bot_profile` | `id`, `name`, `gender`, `score`, `day_counter` |
| `chat_message` | `id`, `text`, `nature`, `timestamp`, `timestamp_ms`, `type`, `is_local`, `reactions`, `action`, `avatar_emotion`, `voice_url`, `duration_in_second` |

`chat_message.nature` 가 `Customer` 이면 사용자가 보낸 메시지이고 `Robot` 이면 봇의 답입니다[2]. `bot_profile.score` 와 `day_counter` 를 도구는 관계 점수와 함께한 날수로 보여 줍니다[2]. `memory_fact_v3` 표는 논문이 이름만 밝혔고[1] 칸 구성은 공개되지 않았습니다. 봇의 "속마음" 이 어느 칸에 들어가는지도 공개되지 않아서 검체에서 표를 열어 확인합니다.

### Kindroid — 토큰과 암호화된 데이터

`PersistedInstallation.*.json` 에는 `AuthToken`, `RefreshToken`, `Fid` 칸이 있고, 도구 코드의 주석은 이 토큰이 사용자 로그인 토큰이 아닌 Firebase 설치 토큰이라고 적었습니다[2]. 논문은 봇 설정·배경 이야기, 사용자별 AI 기억, 말투 지시를 담은 데이터베이스 파일이 AES-256-CBC 로 암호화돼 있고, 암호문이 `Salted__` 로 시작하며, 사용자 ID 에서 MD5 로 키를 만든다고 보고했습니다[1]. 도구 코드(`kindroid_chat_puller.js`)는 `!enc:` 로 시작하는 값을 암호문으로 보고, 그 뒤를 base64 로 푼 머리가 `Salted__` 인지 확인합니다[2]. 논문은 이 구조를 키 관리가 약한 부분 암호화로 평가했습니다[1].

### Character.AI — `RKStorage`

`RKStorage` 는 SQLite 이고, 도구 코드는 `catalystLocalStorage` 표에서 `key` 가 `AUTH_TOKEN` 인 행의 `value` 를 인증 토큰으로 읽습니다[2]. 대화는 기기에 없습니다[1]. 논문이 가로챈 서버 응답 JSON 에는 도시, 우편번호, 시간대, 좌표 같은 위치 칸이 들어 있었습니다[1]. 이 값은 기기 파일이 아니라 앱과 서버 사이의 통신 내용에서 나왔습니다[1].

### Linky.AI — OpenIM 데이터베이스

봇 대화는 봇마다 파일이 따로 있습니다[1]. 도구 코드는 `OpenIM*.db` 파일마다 아래 두 표를 읽고 결과를 `send_time` 순으로 합칩니다[2].

| 표 | 칸 |
|---|---|
| `local_conversations` | `conversation_id`, `conversation_type`, `user_id`, `group_id`, `show_name`, `face_url`, `unread_count`, `latest_msg`, `latest_msg_send_time` |
| `local_chat_logs` | `client_msg_id`, `server_msg_id`, `send_id`, `recv_id`, `sender_nick_name`, `sender_face_url`, `session_type`, `msg_from`, `content_type`, `content`, `is_read`, `status`, `send_time`, `create_time` |

도구 코드가 `content_type` 을 읽는 방식은 101 글, 102 이미지, 103 음성, 104 동영상, 105 파일, 106 멘션, 110 사용자 정의(JSON 안의 `text`)입니다[2]. 논문은 도구가 `.hive` 파일에서도 봇 대화를 뽑는다고 적었지만[1], 공개된 도구 코드는 `.hive` 파일을 읽지 않습니다[2]. 공개된 구조 분석 자료도 없어 검체로 확인해야 합니다.

### Persona.AI·Fantasy.AI — `ai_personal_db`

평문 SQLite 입니다[1]. 도구 코드가 읽는 표와 칸은 아래와 같습니다[2].

| 표 | 칸 |
|---|---|
| `chats` | `both_id`, `nick_name`, `ai_role_id`, `head_img`, `gender`, `level`, `percentage` |
| `chat_messages` | `both_id`, `message_id`, `message_type`, `sender_id`, `sender_name`, `receiver_id`, `receiver_name`, `message_content`, `create_time`, `message_state` |

`chat_messages.both_id` 로 `chats` 의 캐릭터와 잇습니다. `message_content` 는 JSON 이고 `text`, `avatar`, `audio_url`, `img_url`, `video_url`, `can_voice`, `origin_text` 칸이 있습니다. 도구는 JSON 으로 풀리지 않으면 값 전체를 글로 봅니다[2].

사람끼리 메시지를 담는 `com.im_10.8.7.db` 는 Linky.AI·Persona.AI·Fantasy.AI 모두에 있고 논문은 여기서도 메시지를 뽑았다고 적었지만[1], 공개된 도구 코드는 이 파일을 읽지 않습니다[2]. 표 구성은 검체에서 확인합니다.

## 증거로서 의미

**증명하는 것.** `REPLIKA_DB`·`ai_personal_db`·OpenIM 데이터베이스의 행은 그 기기의 앱에 그 내용의 메시지가 저장됐다는 기록이고, 보낸 쪽 칸(`nature`, `sender_name`, `send_id`)으로 사용자 입력과 봇 답을 나눌 수 있습니다. Replika `user_profile` 의 이름·이메일·생일은 그 앱 계정에 입력된 프로필입니다. Character.AI 처럼 대화가 서버에만 있는 앱은 `RKStorage` 의 토큰이 그 기기에서 계정에 로그인한 상태였다는 흔적이 됩니다. 앱은 여러 광고·분석 업체에 사용 정보를 보냅니다. 논문은 Replika 가 Facebook·AppsFlyer·Adjust·Amplitude 로, Kindroid 가 웹 추적기로 TikTok Analytics·Facebook 등에, Linky.AI 가 `admob.xml` 을 거쳐 GPS 를 Google AdMob 으로, Persona.AI·Fantasy.AI 가 AppLovin 과 ThinkingData/Unity China 두 경로로 데이터를 보낸다고 보고했고, AppLovin 쪽은 사용자당 최대 41개 행동 지표를 기록했습니다[1]. 그래서 기기에서 지운 활동이 이런 업체 쪽에 남아 있을 수 있습니다.

**증명하지 못하는 것.** 앱에 남은 계정은 그 계정으로 로그인했다는 뜻일 뿐이고, 누가 기기를 들고 입력했는지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 좁힙니다. Replika `memory_fact_v3` 의 "사용자 사실" 은 앱이 대화에서 뽑아 정리한 내용이라서, 사용자가 그 문장을 그대로 말했다는 근거가 되지 못합니다. 원래 메시지를 찾아 함께 인용합니다. 봇의 답도 사용자의 생각이 아닙니다. 논문의 사례 실험에서 봇들은 처음에는 범행을 말렸지만, 사용자가 "성공했다" 고 하자 사용자가 무사해서 다행이라는 반응부터 노골적인 지지까지 반응이 갈렸습니다[1]. Character.AI 처럼 기기에 대화가 없는 앱에서 대화가 안 보인다고 대화가 없었다고 할 수 없습니다.

## 시각 해석

도구 코드는 Replika `chat_message` 를 `timestamp_ms` 순으로 정렬하고, Persona.AI·Fantasy.AI 의 `create_time` 과 Linky.AI 의 `send_time` 을 Unix 밀리초로 읽습니다[2]. Linky.AI 의 `create_time` 은 도구가 숫자로만 읽고 날짜로 바꾸지 않습니다[2]. Unix 시각은 UTC 기준이라, 값을 바꿨는데 1970년 무렵 날짜가 나오면 초 단위일 수 있으니 다시 봅니다. Replika 의 `timestamp` 칸은 도구가 그대로 날짜로 넘길 뿐 형식이 공개되지 않아서, 같은 행의 `timestamp_ms` 와 맞춰 형식과 시간대를 확인합니다.

공개 도구는 결과를 `toLocaleString()` 으로 찍어서, 사람이 읽는 로그의 시각이 분석 PC 의 현지 시각으로 나옵니다[2]. 보고서에는 원래 값과 UTC 로 바꾼 값을 함께 적습니다. Linky.AI 의 `local_conversations.latest_msg_send_time` 은 그 대화의 마지막 메시지 시각이라서 `local_chat_logs` 의 마지막 `send_time` 과 맞춰 보면 지워진 메시지가 있는지 가늠할 수 있습니다. Character.AI 서버 응답에 든 시간대 칸은 사용자가 있던 지역을 짐작하는 근거가 됩니다[1]. 여러 출처의 시각을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

**지운 기록이 남는 곳이 앱마다 다릅니다.** 논문이 삭제 기능을 시험한 결과는 아래와 같습니다[1]. 앱마다 지울 수 있는 단위도 달라서, 메시지 하나를 지울 수 있는 앱은 Character.AI 뿐이고, Linky.AI·Persona.AI·Fantasy.AI 는 대화 전체만 비울 수 있으며, Replika·Kindroid 는 계정을 지워야 했습니다.

| 앱 | 지운 뒤 |
|---|---|
| Replika | 계정을 지우면 주 데이터베이스가 기기에서 지워졌지만, Firebase Crashlytics 로그의 `userlog` 하위 폴더에서 대화 전체가 복구됐습니다. |
| Kindroid | 계정을 지운 뒤에는 기기에 토큰과 ID 가 남아 있어도 서버 쪽 대화를 얻지 못했습니다. |
| Character.AI | 지운 메시지는 서버 응답에서 빠졌고, 계정을 지우면 기기의 토큰과 로그인 정보가 지워졌습니다. 서버 백업에서도 지워졌는지는 알 수 없습니다. |
| Linky.AI | 대화를 비우면 새 대화 ID 만 만들고 원래 기록은 데이터베이스에 그대로 뒀습니다. 앱 안에 계정 삭제 기능이 없습니다. |
| Persona.AI·Fantasy.AI | 지운 대화가 주 데이터베이스에서는 빠졌지만 `ai_personal_db-wal` 에 남았고, 앱 데이터를 모두 지운 뒤에도 남았습니다. |

그래서 `-wal`·`-shm` 파일을 주 데이터베이스와 함께 한 번에 복사하고, 앱 폴더 전체에서 `userlog` 라는 이름의 폴더를 찾습니다. WAL 에서 지운 행을 되살리는 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)와 [SQLite 데이터베이스 (Android)](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html)에 있고, 서비스별 보관·삭제 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

**보낸 쪽을 가르는 도구 규칙은 어림입니다.** Linky.AI 도구는 보낸 이 이름에 `assistant`·`official`·`bot` 이 있거나 `send_id` 가 15자보다 길면 봇으로 보고, 나머지는 사용자로 봅니다[2]. Persona.AI·Fantasy.AI 도구는 `sender_name` 이 비어 있지 않고 `v` 가 아니면 봇으로 봅니다[2]. 둘 다 코드 주석에 적힌 관찰에서 나온 규칙이라서, 결과를 쓰기 전에 `send_id`·`recv_id`·`sender_id` 와 대화 상대 ID 를 원본에서 맞춰 봅니다.

**남은 토큰은 가려야 합니다.** `RKStorage` 의 `AUTH_TOKEN`, Kindroid 의 `PersistedInstallation` 토큰과 IndexedDB 의 사용자 토큰은 보고서와 결과 파일에서 가립니다. 논문은 연구진이 만든 시험 계정의 토큰으로 서버에서 대화를 받아 왔지만[1], 실제 사건에서 남은 토큰으로 서버 자료를 가져오는 일은 법적 권한이 있어야 하는 별도의 문제입니다. 서버 쪽 대화는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 받고, 토큰이 남는 곳의 일반 설명은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다.

**실험 조건이 좁습니다.** 논문은 루팅한 에뮬레이터 한 가지 환경에서 `adb root` 뒤 `/data/data` 를 tar 로 묶어 뽑았습니다[1]. 루팅하지 않은 실제 기기에서는 이 폴더를 그대로 얻지 못할 수 있으니, 수집 범위는 [저장 공간 암호화 (Android)](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html)와 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)를 보고 정합니다. 논문도 iOS·데스크톱 판이나 다른 컴패니언 앱, 새로 나온 컴패니언 앱에서는 결과가 다를 수 있다고 적었습니다[1].

## 직접 분석해 보기

**헥스로 한 번.** 폴더 이름이 달라도 파일 머리와 이름 바이트로 찾을 수 있습니다. 아래 값은 SQLite 명세와 문자 인코딩으로 만든 예시이고, 검체에서 뜬 바이트가 아닙니다.

```
만든 예시(명세와 인코딩으로 만든 바이트)
SQLite 파일 머리 "SQLite format 3\0"  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00
WAL 파일 머리                          37 7F 06 82  또는  37 7F 06 83
"REPLIKA_DB"      UTF-8                52 45 50 4C 49 4B 41 5F 44 42
"ai_personal_db"  UTF-8                61 69 5F 70 65 72 73 6F 6E 61 6C 5F 64 62
Kindroid 암호문 표시 "!enc:"            21 65 6E 63 3A
"Salted__"                             53 61 6C 74 65 64 5F 5F   (base64 로는 U2FsdGVkX1 로 시작)
```

SQLite 레코드 안의 8바이트 정수는 빅 엔디언입니다. `timestamp_ms` 나 `create_time` 이 아래처럼 보이면 Unix 밀리초로 읽습니다.

```
만든 예시(SQLite 8바이트 정수, 빅 엔디언)
00 00 01 9B 76 DA D7 DA   ->  1767225612250  ->  2026-01-01 00:00:12.250 UTC
```

**공개 도구로 한 번.** 논문이 공개한 data_pulling_tool[2]은 Node.js 스크립트이고, 기기 데이터베이스를 읽는 스크립트는 `sqlite3` 명령을 불러 씁니다. 데이터베이스 파일 경로를 인자로 주면 그 파일을 바로 읽어 JSON 과 읽기용 로그를 만들고, Linky.AI 스크립트는 한 번에 `OpenIM` 파일 하나를 읽습니다. 압축 파일을 넣는 방식도 코드에 있지만, 이때 스크립트는 먼저 스크립트 폴더나 지금 폴더의 `all_apps_database/` 아래 패키지 폴더에서 데이터베이스를 찾고 없으면 멈추므로 파일 경로를 직접 주면 됩니다[2]. 남은 토큰으로 서버 요청 헤더를 만들거나 서버에 접속하는 스크립트(`character_ai_header_extractor.js`, `characterai_chat_puller.js`, `kindroid_header_extractor.js`, `kindroid_chat_puller.js`)는 쓰지 않습니다. 경로는 만든 예시입니다.

```sh
# 만든 예시 경로
APPS=/cases/case-0007/android-data/data/data
cd /cases/case-0007/out
node replika_chat_puller.js "$APPS/ai.replika.app/databases/REPLIKA_DB"
node persona_fantasy_chat_puller.js persona "$APPS/com.aipersona.camera/databases/ai_personal_db"
for f in "$APPS"/com.aigc.ushow.ichat/app_flutter/OpenIM*.db; do node linky_chat_puller.js "$f"; done
```

결과 파일은 모두 지금 폴더에 생기고, Replika 스크립트는 지금 폴더의 `ai_chat_recovery_consolidated.json` 에 결과를 덧붙여 쓰니 빈 폴더에서 돌립니다[2]. 도구 결과는 sqlite3 로 원본과 한 번 맞춰 봅니다.

```sh
# 만든 예시 경로
DB=/cases/case-0007/android-data/data/data/com.aipersona.camera/databases/ai_personal_db
sqlite3 "$DB" "SELECT c.nick_name, m.sender_name, datetime(m.create_time/1000,'unixepoch'),
                      json_extract(m.message_content,'$.text')
               FROM chat_messages m LEFT JOIN chats c ON c.both_id = m.both_id
               ORDER BY m.create_time;"

DB=/cases/case-0007/android-data/data/data/ai.replika.app/databases/REPLIKA_DB
sqlite3 "$DB" "SELECT nature, datetime(timestamp_ms/1000,'unixepoch'), timestamp, text
               FROM chat_message ORDER BY timestamp_ms;"
sqlite3 "$DB" ".schema memory_fact_v3"
```

SQLite 가 여는 순간 WAL 내용을 주 파일에 합칠 수 있으니 이 비교는 사본에서 합니다. `-wal` 파일을 같은 폴더에 두고 한 번, 빼고 한 번 열어 행 수가 다르면 WAL 에만 있는 기록이 있다는 뜻입니다. 논문은 추출본을 Autopsy 로도 살폈습니다[1].

## 교차 검증

`*.character.ai` 같은 서비스 도메인은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)에서 시각을 맞춰 봅니다. 앱 설정 XML 은 [설정 XML과 SharedPreferences (Android)](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/shared-preferences.html)의 방식으로 읽습니다. 계정과 사람을 잇는 일은 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)를 따르고, Replika `user_profile`·Kindroid 사용자 ID·Character.AI 토큰의 계정을 기기의 다른 계정 흔적과 맞춰 봅니다. 서버와 광고·분석 업체 쪽 자료는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 확보합니다. DeepSeek·Grok 같은 일반 대화형 서비스는 [그 밖의 서비스](other-services.md)에서 다룹니다.

## 실습

AI 컴패니언 앱 흔적이 든 공개 검체가 없어서, 시험용 Android 기기(또는 에뮬레이터)와 시험 계정으로 풀어 봅니다.

1. Persona.AI 나 Fantasy.AI 에서 대화를 만들고 지운 뒤, `ai_personal_db` 와 `ai_personal_db-wal` 에서 지운 메시지가 어디에 남는지 확인합니다. 앱 데이터를 모두 지운 뒤에도 다시 확인합니다.
2. Linky.AI 에서 대화를 비우기 전과 뒤의 `local_conversations` 를 비교해 새 `conversation_id` 가 생기는지, 원래 `local_chat_logs` 행이 남는지 봅니다.
3. Replika 에서 자기소개를 몇 가지 한 뒤 `memory_fact_v3` 에 어떤 문장이 생기는지 보고, 원래 메시지와 어떻게 다른지 적어 봅니다.
4. 세 앱의 도구 결과를 UTC 로 바꾼 sqlite3 결과와 비교해, 분석 PC 의 시간대에 따라 시각이 얼마나 어긋나는지 확인합니다.

## 참고 문헌

1. Kendall J. Comeaux, Trevor T. Spinosa, Ali Ghosn, Ibrahim Baggili, "Ex Machina: A forensic evaluation of AI companion applications and their evidentiary value", Forensic Science International: Digital Investigation, 56 (2026), 302050 (DFRWS EU 2026). https://doi.org/10.1016/j.fsidi.2026.302050
2. data_pulling_tool(Ex Machina 논문의 공개 도구, 2025-10-10 생성) — https://github.com/Anonymousforensics123456789179/data_pulling_tool , `replika_chat_puller.js`, `persona_fantasy_chat_puller.js`, `linky_chat_puller.js`, `character_ai_header_extractor.js`, `characterai_chat_puller.js`, `kindroid_header_extractor.js`, `kindroid_chat_puller.js`
