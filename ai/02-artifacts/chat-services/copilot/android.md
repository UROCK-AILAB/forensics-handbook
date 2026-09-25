---
title: "Microsoft Copilot Android 앱"
parent: "Microsoft Copilot"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 250
---

# Android 앱 (Android)

Android 용 Microsoft Copilot 앱(패키지 `com.microsoft.copilot`)은 앱 데이터 폴더에 로그인 계정 정보, 동의·설정 값, 원격 측정 (telemetry) 이벤트 대기열을 남기고, 대화 본문이 기기에 남는지는 연구 시점과 앱 판에 따라 결과가 갈립니다 [1][4][6].

> 확인 날짜: 2026-09-25. 패키지 이름은 공개 저장소 두 곳에서 옮겼습니다 [2][3]. 파일 경로와 키 이름은 LEAF 저장소의 문서 [4][5]와 이 저장소에 올라온 수집 파일 [6]에서 옮겼습니다. 수집 파일은 Android 16 에 설치한 앱 30.0.440127001 에서 나왔고 기록 시각은 2026-01~02 입니다. LEAF 문서의 관찰은 Android 15, 2026-04-20 입니다. 지금 배포되는 판은 파일 구성이 다를 수 있어서 경로와 키 이름은 검체에서 한 번 더 확인합니다.

## 무엇을 기록하나 · 왜 생기나

Microsoft 개인정보 처리방침은 소비자용 Copilot 을 웹과 Windows·Mac·iOS·Android 앱으로 제공한다고 적습니다 [8]. 대화 원본은 계정에 쌓이고, 계정 쪽 기록은 [계정 데이터 내보내기](export.md)로 받습니다.

기기에 대화가 남는지는 두 출처가 다르게 말합니다. Tyagi·Gong·Karabiyik(2025)은 Copilot 이 Android 와 iOS 모두에서 대화를 브라우저 데이터와 함께 평문으로 저장한다고 초록에 적었고, Android 에서는 사용자 프롬프트, 브라우저 데이터, 위치 데이터를 되살렸다고 적었습니다 [1]. 초록에는 시험한 앱 판이 나오지 않습니다. 반면 LEAF 문서(2026-04-20, Android 15)는 앱 폴더에 원격 측정 대기열만 있고 대화는 기기에 저장하지 않는다고 적었습니다 [4]. 같은 저장소의 README 는 Copilot 의 형식을 "SQLite 안의 암호화된 JSON" 이라고 적어서 자기 문서끼리도 어긋납니다 [5].

LEAF 저장소에 올라온 수집 파일(2026-02, 앱 30.0.440127001)에도 대화 본문을 담은 파일 이름은 보이지 않습니다 [6]. 대신 새 대화를 연 횟수, 대화 차례 수 같은 계수 값과 로그인 계정 정보가 설정 파일에 남습니다. 그래서 검체마다 앱 판을 먼저 적고, 그 판에서 대화 본문이 어디에 있는지 직접 열어 봅니다.

## 위치와 버전별 차이

앱 폴더는 `/data/data/com.microsoft.copilot/`(같은 곳을 `/data/user/0/com.microsoft.copilot/` 로도 가리킴)입니다 [6]. 폴더 짜임의 일반 원리는 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html)에서, 이 폴더를 수집할 수 있는 범위는 [저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html)에서 다룹니다.

패키지 이름과 실행 화면의 접두어가 다릅니다. 패키지는 `com.microsoft.copilot` 이고 [2][3], 앱을 여는 액티비티는 `com.microsoft.copilotn.MainActivity` 입니다 [3]. 원격 측정 기록의 앱 이름도 `CopilotN-prod-android` 로 남습니다 [6]. 설치 앱 목록에서는 패키지 이름으로, 로그와 원격 측정에서는 `copilotn` 이 붙은 이름으로 찾습니다.

아래 표는 수집 파일(Android 16, 앱 30.0.440127001)에 있던 파일입니다 [6]. LEAF 문서(Android 15, 2026-04-20)는 이 가운데 원격 측정 DB 만 적었습니다 [4].

| 앱 폴더 안 경로 | 형식 | 담긴 것 |
|---|---|---|
| `cache/be6e4c19699f4fdf9f8c0ec9f9b398ef.db` 와 `-wal`·`-shm`·`.ses` | SQLite | 원격 측정 이벤트 대기열(`StorageRecord` 표) |
| `files/datastore/user_info.preferences_pb` | DataStore protobuf, 값은 JSON 문자열 | 로그인 계정 정보와 인증 토큰 |
| `files/datastore/user_data.preferences_pb` | DataStore protobuf | 사용자 식별자, 지역, 나이대, 요금제, 동의 여부 |
| `files/datastore/user_settings.preferences_pb` | DataStore protobuf | 학습·개인화 동의 설정, 알림 설정, 기능별 남은 사용 횟수 |
| `files/datastore/chat_datastore.preferences_pb` | DataStore protobuf | 새 대화 수 계수, 안내문 확인 여부 |
| `files/datastore/turn_pref.preferences_pb` | DataStore protobuf | `turn_count` |
| `files/datastore/CookiePersistence.preferences_pb` | DataStore protobuf | 앱이 보관한 쿠키 |
| `shared_prefs/com.auth0.authentication.storage.xml`, `TOKEN_SHARE_PREF_UNIQUE_ID.xml`, `TokenShare_Configuration_Status.xml` | SharedPreferences XML | 이름으로 보아 로그인·토큰 공유 관련 |
| `shared_prefs/app_exit_info.xml` | SharedPreferences XML | `last_tracked_timestamp` |
| `databases/com.microsoft.appcenter.persistence`, `databases/com.google.android.datatransport.events` | SQLite | 분석·오류 보고 도구의 저장소 |
| `cache/sentry/` 아래 해시 이름 폴더 | JSON | 오류 보고 도구의 세션과 흔적 기록 |
| `cache/coil3_disk_cache/`, `cache/com.microsoft.identity.http-cache/`, `cache/cronet/` | 캐시 | 이미지·로그인·네트워크 캐시 |
| `files/downloads/` | mp3·mp4 | `call_started.mp3`, `voice_bg_20250920_dark.mp4` 같은 앱 화면용 자원 |

`files/downloads/` 의 파일은 이름이 앱 화면 자원 이름이라서 사용자가 만든 파일과 구분합니다.

## 구조

**원격 측정 DB.** `StorageRecord` 표의 칸은 `id`, `tenantToken`, `latency`, `persistence`, `timestamp`, `retryCount`, `reservedUntil`, `blob` 이고, 설정을 담는 `StorageSetting`(`name`, `value`) 표가 따로 있습니다 [6]. DB 파일 이름은 `tenantToken` 값의 앞부분과 같습니다. `blob` 은 이진 형식이지만 안의 문자열이 그대로 읽히고, 이벤트 이름(`eventName`), 앱 이름과 판, OS 판, 네트워크 종류, 시간대 오프셋, 요금제(`accountTier`), 로그인 방식(`accountType`), 위치 권한 상태(`userCoarseLocationPermissionStatus`, `userFineLocationPermissionStatus`), 학습·개인화 동의 값이 들어 있습니다 [6]. LEAF 문서도 이 표를 Microsoft 원격 측정 이벤트 대기열로 보았습니다 [4].

**계정 정보.** `user_info.preferences_pb` 에는 `active_account` 와 `re_auth_data` 키가 있고, 값은 JSON 문자열입니다. JSON 안에는 `type`(로그인 방식), `userId`, `email`, `firstName`, `userAgeGroup` 과 함께 `token`, `accessToken`, `expiry`, `expiryEpoch` 가 들어 있습니다 [6]. 토큰과 쿠키가 있는 곳과 보고서에서 가리는 기준은 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)을 따릅니다.

**사용자·설정 값.** `user_data.preferences_pb` 에는 `picasso_id`, `anid`, `region`, `age_group`, `account_tier`, `is_pro`, `is_new_user`, `user_consent_model_training`, `user_consent_personalization`, `latest_trace_id` 가 있습니다 [6]. `picasso_id` 값은 원격 측정 `blob` 의 `UserInfo.Id` 값과 같아서, 두 파일을 같은 사용자로 묶는 고리가 됩니다. `user_settings.preferences_pb` 에는 `opt_out_of_model_training`, `opt_out_personalization`, `opt_in_of_voice_training`, `first_app_start`, `local_name`, `notif_daily_enabled`, `history_migration_in_progress`, `remaining_research_calls` 같은 키가 있습니다 [6].

**대화 계수.** `chat_datastore.preferences_pb` 의 키는 `create_new_chat_count_20250818`, `last_reset_time_20250818`, `has_viewed_disclaimer` 이고, `turn_pref.preferences_pb` 에는 `turn_count` 가 있습니다 [6]. 키 이름 끝의 8자리 숫자는 공개된 설명이 없어서, 무엇을 뜻하는지 검체로 확인해야 합니다.

**쿠키.** `CookiePersistence.preferences_pb` 의 키는 "주소|쿠키 이름" 꼴이고(예: `https://copilot.microsoft.com/` 과 `__cf_bm` 을 `|` 로 이은 것), 값은 Java 직렬화 바이트를 헥스 문자열로 적은 것이라 `aced0005` 로 시작합니다 [6].

## 증거로서 의미

**증명하는 것.** 앱 폴더가 있으면 그 기기에 Copilot 앱이 설치되어 있었다고 쓸 수 있습니다. `user_info` 의 계정 정보는 수집 시점에 이 기기에서 로그인해 있던 계정과 로그인 방식을 알려 주고, `user_data`·`user_settings` 는 요금제와 학습·개인화 동의 설정을 알려 줍니다. 원격 측정 대기열의 행은 적힌 시각에 앱이 이벤트를 기록했다는 사실과 그때의 위치 권한 상태, 네트워크 종류를 알려 줍니다. 대화 계수 값은 새 대화를 연 횟수와 대화 차례 수를 알려 줍니다.

**증명하지 못하는 것.** 위 파일들만으로는 무엇을 물었고 무엇을 답받았는지 알 수 없습니다. 대화 본문은 [계정 데이터 내보내기](export.md)나 법적 절차([서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md))로 확보합니다. 위치 권한이 허용되어 있었다는 기록은 위치를 보냈다는 증거가 아닙니다. 로그인 계정과 실제로 대화한 사람이 같은지도 따로 가립니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)).

보고서에는 "이 기기의 Copilot 앱 폴더에 이 계정의 로그인 정보가 있고, 이 시각에 앱이 이벤트를 기록했다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

| 위치 | 칸·키 | 형식 |
|---|---|---|
| `StorageRecord` 표 | `timestamp` | 1970-01-01 UTC 기준 밀리초 정수(13자리) [6] |
| 원격 측정 `blob` | 시간대 오프셋 문자열 | 기기의 현지 시간대(`+09:00` 꼴, 만든 예시) [6] |
| `cache/sentry/` 아래 `session.json` | `started`, `timestamp` | ISO 8601 UTC 문자열(끝에 `Z`) [6] |
| `shared_prefs/app_exit_info.xml` | `last_tracked_timestamp` | 13자리 정수(밀리초) [6] |
| `user_info` 의 JSON | `expiry`, `expiryEpoch` | 토큰 만료 시각 |

`StorageRecord.timestamp` 가 이벤트가 생긴 시각인지 대기열에 넣은 시각인지는 칸 이름만으로 알 수 없습니다. 같은 행의 `blob` 에 든 이벤트 이름과 세션 식별자를 Sentry `session.json` 의 시각, 파일 시스템 시각과 맞춰 봅니다. `blob` 에 시간대 오프셋이 있으니 현지 시각으로 바꿀 때는 그 값을 씁니다.

## 함정과 한계

- **출처끼리 어긋남.** Tyagi 외(2025)는 평문 대화를 되살렸고 [1], LEAF 문서(2026-04)는 대화가 없다고 했으며 [4], LEAF README 는 암호화된 JSON 이라고 적었습니다 [5]. 앱 판과 연구 시점이 다르므로 어느 한쪽을 정답으로 삼지 않고, 검체의 앱 판과 함께 결과를 적습니다.
- **대기열은 쌓이는 기록이 아님.** `StorageRecord` 는 보낼 이벤트를 모아 두는 표라서, 수집 파일에는 행이 1개뿐이었습니다 [6]. 행이 적다고 앱을 적게 썼다고 보지 않습니다.
- **WAL 파일.** 원격 측정 DB 는 `-wal` 이 붙은 WAL 모드라서 `-wal`·`-shm` 을 함께 수집합니다. 읽는 법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html)를 따릅니다.
- **인증 정보.** `user_info`, `CookiePersistence`, `com.auth0.authentication.storage.xml` 에는 토큰과 쿠키가 있을 수 있어서 보고서와 사본 공유 때 가립니다.
- **공개 분석기 없음.** 2026-09-25 기준 ALEAPP 저장소에는 Copilot 전용 분석기가 없습니다 [7]. 파일은 SQLite 도구와 protobuf 해석 도구로 직접 읽습니다.
- **이름이 같은 다른 제품.** [Microsoft 365 Copilot](../../office-integrations/m365-copilot.md)이나 Edge 안의 Copilot([브라우저에 들어간 AI](../../office-integrations/browser-builtin-ai.md))과 구분합니다. 같은 계정을 브라우저에서 썼다면 [웹 브라우저](web.md) 쪽 흔적과 [크롬](https://urock-ailab.github.io/forensics-handbook-android/02-artifacts/browsers/chrome/index.html) 방문 기록도 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** 원격 측정 DB 를 헥스 편집기로 열면 첫 16바이트가 `53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00`("SQLite format 3" 과 NUL)이라서 암호화되지 않은 SQLite 파일임을 알 수 있습니다. `StorageRecord.blob` 을 헥스로 보면 이진 필드 사이에 `eventName`, `AppInfo_Name` 같은 이름과 그 값이 ASCII 로 섞여 나옵니다. `CookiePersistence.preferences_pb` 도 헥스로 열면 쿠키 키 뒤에 `aced0005` 로 시작하는 헥스 문자열이 이어집니다.

**공개 도구로 한 번.** 사본 폴더에서 `sqlite3` 로 표를 읽습니다.

```sh
sqlite3 -readonly be6e4c19699f4fdf9f8c0ec9f9b398ef.db \
  "SELECT id, datetime(timestamp/1000,'unixepoch') AS utc, retryCount, length(blob) FROM StorageRecord;"
```

`.preferences_pb` 파일은 protobuf 라서 `protoc --decode_raw < user_data.preferences_pb` 로 키와 값을 펼쳐 볼 수 있습니다. 설정 XML 은 [설정 XML과 SharedPreferences](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/shared-preferences.html)를 따라 읽습니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 |
|---|---|
| [계정 데이터 내보내기](export.md) | 서버에 남은 프롬프트·응답 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 앱이 서비스와 통신한 시간대. 앱의 User-Agent 에는 `CopilotSapphire/` 뒤에 판 번호가 붙습니다 [2] |
| [크롬](https://urock-ailab.github.io/forensics-handbook-android/02-artifacts/browsers/chrome/index.html) | 같은 계정으로 웹에서 쓴 흔적 |
| [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-android/03-techniques/analysis/timeline/index.html) | 원격 측정·Sentry 시각을 다른 활동과 한 시간 축에 놓기 |
| [대화 내용 되살리기](../../../03-techniques/analysis/content-recovery.md) | 캐시·알림 등 앱 폴더 밖에서 대화 조각 찾기 |

## 실습

시험용 Android 기기와 시험용 Microsoft 계정으로 직접 만든 검체에서 다음을 풀어 봅니다.

1. 설치 앱 목록에서 `com.microsoft.copilot` 의 앱 판은 무엇인가?
2. 대화를 몇 번 한 뒤 `chat_datastore` 의 계수 값과 `turn_pref` 의 `turn_count` 는 어떻게 바뀌는가?
3. 그 판에서 대화 본문이 앱 폴더의 어느 파일에 남는가, 아니면 계정 내보내기에서만 나오는가? 결과를 Tyagi 외(2025)와 LEAF(2026-04)의 결과와 나란히 적어 본다.
4. `StorageRecord` 의 `timestamp` 를 UTC 로 바꾸고, `blob` 의 시간대 오프셋으로 현지 시각을 구하면 실습한 시각과 맞는가?

## 참고 문헌

1. Sonali Tyagi, Yufeng Gong, Umit Karabiyik, "Forensic analysis and privacy implications of LLM mobile apps: A case study of ChatGPT, Copilot, and Gemini", Forensic Science International: Digital Investigation, 54 (2025), 301974. https://doi.org/10.1016/j.fsidi.2025.301974 (초록)
2. plausible/analytics, `priv/ua_inspector/client.mobile_apps.yml`(Microsoft Copilot 항목) — https://github.com/plausible/analytics/blob/master/priv/ua_inspector/client.mobile_apps.yml
3. WSTxda/SwitchAI, `app/src/main/java/com/wstxda/switchai/assistant/CopilotAssistant.kt` — https://github.com/WSTxda/SwitchAI/blob/main/app/src/main/java/com/wstxda/switchai/assistant/CopilotAssistant.kt
4. LEAF-Digital-Forensics, `docs/parser-schemas.md`(Copilot 절, 2026-04-20 관찰) — https://github.com/MarcosAOSperoni/LEAF-Digital-Forensics/blob/main/docs/parser-schemas.md
5. LEAF-Digital-Forensics, `leaf/README.md`(보조 자료) — https://github.com/MarcosAOSperoni/LEAF-Digital-Forensics/blob/main/leaf/README.md
6. LEAF-Digital-Forensics, `manual-forensics/cases/02.6.26/copilot_extracted/`(수집 파일) — https://github.com/MarcosAOSperoni/LEAF-Digital-Forensics/tree/main/manual-forensics/cases/02.6.26/copilot_extracted
7. ALEAPP, `scripts/artifacts/` — https://github.com/abrignoni/ALEAPP/tree/main/scripts/artifacts
8. Microsoft Privacy Statement (Microsoft Copilot 절), 2026-09 갱신 — https://www.microsoft.com/en-us/privacy/privacystatement
