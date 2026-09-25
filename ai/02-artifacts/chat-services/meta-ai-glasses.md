---
title: "Meta AI 앱과 AI 안경"
parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 400
---

# Meta AI 앱과 AI 안경 (Meta AI·Ray-Ban Meta)

Ray-Ban Meta 안경으로 찍은 사진·동영상과 Meta AI 에 한 음성 질문은 안경뿐만 아니라 짝지은 휴대폰의 Meta AI 앱(Android 패키지 `com.facebook.stella`)과 Meta 계정의 클라우드에도 나뉘어 남습니다 [1].

논문은 Android 14 기기, Ray-Ban Meta 1세대 안경, Meta AI 앱 258.0.0.15.167 로 실험했고, iOS 앱과 이후 세대 안경·펌웨어에서는 결과가 다를 수 있습니다 [1].

## 무엇을 기록하나 · 왜 생기나

논문은 증거가 세 층에 나뉘어 있다고 봅니다 [1]. 안경은 촬영과 음성 입력을 맡고 찍은 미디어를 안에 든 플래시 메모리에 잠시 둡니다. 휴대폰 앱은 안경의 미디어를 가져오고 AI 대화와 기기 연결 기록을 남깁니다. 클라우드는 AI 처리를 맡고 대화 기록·처리한 미디어·계정 정보를 보관합니다. 안경 자체를 여는 일은 칩을 떼어 내는 수준의 분해가 필요해서 논문은 다루지 않았고, 휴대폰 앱과 클라우드 내보내기만 분석했습니다 [1].

그래서 이 기기로 한 행동은 대부분 앱 폴더에서 읽습니다. 앱은 누가 로그인했는지(계정), 어느 안경과 짝지었는지(일련번호·MAC 주소), 언제 무엇을 찍었는지(촬영 시각·미디어 종류·동영상 위치), AI 에게 무엇을 물었는지(대화 기록)를 따로따로 저장합니다 [1]. 클라우드 내보내기에는 기기에서 가려진 사용자 질문이 평문으로 남습니다 [1].

음성으로 AI 를 부르는 기능의 일반 원리는 [음성 대화 기능](../generative-media/voice-mode.md)에, 서버와 기기 중 어디에 원본이 있는지 가리는 법은 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

## 위치와 버전별 차이

### 수집 방식에 따른 차이

루팅하지 않은 채 `adb backup` 으로 받으면 머리말만 든 47바이트 파일이 나옵니다 [1]. 논문 팀이 JADX 로 APK 를 풀어 보니 `AndroidManifest.xml` 에 `android:allowBackup="false"` 가 있었고, 이 설정이 백업 방식의 추출을 막습니다 [1]. 루트 권한으로 `adb pull /data/data/com.facebook.stella` 를 하면 SQLite 데이터베이스·설정 파일·캐시 미디어·AI 대화 기록이 나왔습니다 [1]. 논문 표 3 에서 권한 없는 수집은 계정·기기 식별자, 설정, 미디어, AI 대화, 시스템 기록 가운데 거의 모든 항목을 얻지 못했습니다 [1]. 권한 없는 수집 경로에서는 미디어를 SD 카드 저장 공간에서 따로 꺼냈습니다 [1].

앱 폴더 구조의 일반 원리는 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html)에서, 이 폴더가 기기 암호화의 보호를 받는 방식은 [저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html)에서 다룹니다.

### 앱 폴더 안의 파일 (Android)

아래 경로는 `/data/data/com.facebook.stella/` 기준입니다. 논문 표 4 와 4.3절을 옮겼고, 분석 도구가 읽는 칸은 다음 절에서 따로 적습니다.

| 경로 | 형식 | 담긴 것 | 근거 |
|---|---|---|---|
| `databases/StellaDatabase` → `user_profile` | SQLite | 사용자 ID, 사용자 이름, 계정 ID, 프로필 사진 | [1] |
| `databases/StellaDatabase` → `device_assets` | SQLite | 기기 UUID, 블루투스 MAC, 짝짓기(pairing) 이력 | [1] |
| `databases/StellaDatabase` → `capture` | SQLite | 촬영 시각, 기기 일련번호, 짝짓기 ID, 미디어 종류 | [1] |
| `databases/StellaDatabase` → `media_item` | SQLite | 휴대폰으로 가져온 시각, 처리 상태, 미디어 종류 | [1] |
| `databases/StellaDatabase` → `media_item_location` | SQLite | 동영상의 GPS 위도·경도 | [1] |
| `databases/StellaDatabase` → `multimodal_metadata` | SQLite | AI 시각 질의 이미지를 촬영 세션·기기 일련번호와 연결 | [1] |
| `databases/StellaDatabase` → `update_log` | SQLite | 펌웨어 무선 업데이트(OTA) 이력 | [1] |
| `databases/StellaDatabase` → `contacts_row_contact` | SQLite | 동기화한 Messenger·Instagram 연락처 | [1] |
| `databases/interaction_log.db` → `entries` | SQLite | AI 대화 상태, 응답 글, 세션 UUID | [1] |
| `cache/graphql_response_cache/.../P3%3a*` | 캐시 | 사용자 질문 평문, AI 응답 | [1] |
| `files/assistantLogs/*.json` | JSON | 음성 명령 메타데이터, 상호작용 ID, 기기 상태 | [1] |
| `files/media/[ID]/*.jpg`, `*.mp4` | 미디어 | 사진(원본·처리본·미리보기), 동영상(원본·표시용) | [1] |
| `files/media/[ID]/*.bin` | 바이너리 | 가속도계·자이로 값(IMU), 동영상 시각 메타데이터 | [1] |
| `files/media/.../SupernovaDeviceMediaSource_*` | 바이너리 | 카메라·IMU·오디오·LED·터치·조도 센서 보정 값 | [1] |
| `app_light_prefs/.../device_system_info_*` | 바이너리 protobuf | 일련번호, MAC 주소, 테 종류·색, 렌즈 종류, 소프트웨어 빌드 | [1] |
| `app_light_prefs/.../wearable_device_settings_*` | 바이너리 protobuf | LED 밝기, 동영상 흔들림 보정, 알림 설정 | [1] |
| `app_light_prefs/.../app_privacy_consent_settings` | 바이너리 protobuf | 개인 정보 동의 시각, 데이터 공유 설정 | [1] |
| `app_light_prefs/.../partner_app_settings` | 바이너리 protobuf | Spotify·Amazon Music 패키지 이름과 설정 | [1] |
| `app_analytics/fflogger/FFLogger.sql` → `event` | SQLite | 어시스턴트 분석 기록, 성능 수치, 파일 전송 | [1] |
| `app_errorreporting/.../systems_health_report.txt` | 텍스트 | 시스템 상태, 기기 이벤트, 연결 시각 | [1] |
| `files/stella/general_files/aum_account_*` | 데이터베이스 | Messenger·Instagram 계정 데이터베이스 | [1] |
| `files/media/aimodels/*.pte`, `*.ptl` | PyTorch 모델 | 얼굴 검출·분류·가림 판단 모델 다섯 개 | [1] |
| `files/mobileconfig/.../*.mctable` | 설정 | LLM 시스템 프롬프트, AI 설정 값, UUID | [1] |

### 클라우드 내보내기

Meta 계정 센터(Accounts Center)의 데이터 내보내기는 분류별 HTML 파일로 옵니다 [1]. 논문 표 5 가 꼽은 파일은 `meta_ai_profile/your_ai_conversations.html`(사용자 질문·AI 응답·대화 날짜), 프로필 HTML(계정 생성일·마지막 갱신 시각), `meta_ai_app/meta_ai_media.html`(미디어와 기기 일련번호·날짜의 연결), `posts/media/your_posts/`(AI 대화에 입력한 이미지), `meta_ai_app/connected_devices.html`("Hey Meta" 설정·기기 설정), `meta_ai_app/app_settings.html`(마지막 앱·기기 설정)입니다 [1]. 파일마다 칸과 시각 표기는 [계정 데이터 내보내기 형식](../../01-foundations/storage-model/data-export-formats.md)의 Meta AI 절에서, 내보내기를 받아 보존하는 절차는 [계정 데이터 내보내기로 수집](../../03-techniques/acquisition/export-collection.md)에서 다룹니다. 계정 주인의 협조 없이 서버 쪽 기록이 필요하면 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 받습니다.

### iOS 와 다른 세대

논문은 Android 앱만 분석했고 iOS 앱은 다음 연구로 남겼습니다 [1]. iOS 앱은 공개된 분석 자료가 없어 검체로 확인해야 합니다. 웹의 Meta AI 는 브라우저 흔적으로 남으므로 도메인 목록은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)을 봅니다.

## 구조

### StellaDatabase

`StellaDatabase` 는 SQLite 파일이고, 논문은 이 파일을 앱에서 증거가 가장 많은 데이터베이스로 꼽았습니다 [1]. 형식 자체는 [Android SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html) 페이지를 따릅니다. ALEAPP 플러그인이 조회하는 칸은 아래와 같습니다 [2].

| 표 | 플러그인이 읽는 칸 | 쓰임 |
|---|---|---|
| `user_profile` | `user_id`, `user_name`, `profile_picture_uri`, `fetch_timestamp_ms`, `eligible_for_c50` | 사용자 ID·표시 이름·프로필 사진 주소·프로필을 받아 온 시각·Meta AI 사용 자격 |
| `capture` | `capture_id`, `pairing_id`, `device_serial`, `capture_timestamp_ms`, `type` | 촬영 기록. 안경 일련번호와 짝짓기 ID 가 함께 적힘 |
| `media_item` | `media_item_id`, `capture_id`, `import_completed_timestamp_ms` | 휴대폰으로 가져오기를 마친 시각 |
| `media_item_display` | `media_item_id`, `is_current_version`, `display_full_media_file_id` | 지금 보여 주는 판의 파일 번호 |
| `media_file` | `media_file_id`, `uri` | 파일 경로 |
| `media_item_location` | `media_item_id`, `latitude`, `longitude` | 위치 |
| `multimodal_metadata` | `media_item_id` | AI 시각 질의에 쓴 미디어 |

표끼리는 `capture.capture_id` → `media_item.capture_id` → `media_item.media_item_id` → `media_item_display` → `media_file` 순서로 이어집니다 [2]. 위치와 AI 시각 질의도 `media_item_id` 로 붙습니다 [2].

### 계정과 기기 식별자

논문은 식별자 세 가지로 사람과 기기를 잇습니다 [1]. 계정 ID(`account_id`)는 Meta 계정을 가리키고 Facebook·Instagram 같은 연결 서비스와 맞춰 볼 수 있습니다. 사용자 ID(`user_id`)는 앱 안의 데이터베이스와 파일 경로에서 같은 사람의 기록을 묶는 값입니다. 기기 일련번호(`device_serial`)는 안경 왼쪽 다리 안쪽에 새겨져 있고, 논문 실험에서 앱에서 뽑은 값과 실물의 각인이 같았습니다 [1]. 짝짓기 ID(`pairing_id`)는 짝지을 때 쓴 MAC 주소이고 짝짓기를 풀거나 초기화하면 바뀔 수 있습니다 [1].

논문 표 4 는 `user_profile` 에 계정 ID 가 있다고 적었지만 [1], 2026-04-12 판 플러그인은 `user_profile` 에서 `user_id` 와 `user_name` 만 읽고 계정 ID 는 `app_light_prefs/com.facebook.stella/` 의 `meta_fx_cache` 에서 읽습니다 [2]. 이 파일을 JSON 으로 열어 `accounts` 배열의 `platform`, `username`(없으면 `email`), `account_id` 를 꺼내고, JSON 으로 열리지 않으면 `account_id`·`account_type`·`username`·`email` 을 문자열 검색으로 찾습니다 [2]. 검체에서는 두 곳을 모두 열어 봅니다.

같은 폴더의 기기 정보는 두 파일에 있습니다 [2]. `connectivity_metadata.xml` 은 XML 이고 `DEVICE-METADATA-ID`(MAC)와 `serialNumber` 를 담습니다. `device_system_info_` 뒤에 MAC 이 붙은 파일은 XML 이 아닌 바이너리이고, 플러그인은 `device_serial`, `device_uuid`, `btc_address`, `device_identifier`, `device_frame_type_short_name`, `device_frame_color_name`, `device_lens_color_name`, `mcu_build`, `soc_build`, `device_type`, `device_hardware_type` 같은 키 이름을 문자열로 찾은 뒤 다음 키 이름 앞까지를 값으로 자릅니다 [2]. 논문은 이 파일을 protobuf 라고 적었고 [1], 플러그인 설명서도 이 방식이 형식을 추정해 읽는 방식이라고 밝혔습니다 [3].

### AI 대화 기록

`interaction_log.db` 의 `entries` 표에는 대화 상태·AI 응답 글·세션 UUID 가 있지만, 사용자 음성 질문은 `<redacted>` 로 바뀌어 AI 응답만 읽을 수 있습니다 [1]. 사용자 질문의 평문은 `cache/graphql_response_cache/` 아래 `P3%3a` 로 시작하는 캐시 파일과 클라우드의 `your_ai_conversations.html` 에 남습니다 [1]. `files/assistantLogs/` 의 JSON 에는 음성 명령의 메타데이터와 상호작용 ID 가 있습니다 [1]. 논문은 이 세 곳의 칸 이름을 싣지 않았고 2026-04-12 판 플러그인의 경로 목록에도 들어 있지 않아서 [2], 칸 이름은 검체에서 직접 열어 확인합니다.

## 증거로서 의미

**증명하는 것.** `capture` 행은 특정 일련번호의 안경이 그 시각에 사진이나 동영상을 찍었다는 기록입니다 [1]. 같은 행의 짝짓기 ID 는 그때 어느 연결로 짝지어져 있었는지 보여 주고, `media_item` 의 가져온 시각은 미디어가 휴대폰으로 옮겨진 때를 보여 줍니다 [1][2]. `multimodal_metadata` 는 AI 에게 보여 준 이미지가 어느 촬영에서 왔는지 이어 주고 [1], `media_item_location` 은 동영상을 찍은 위치를 줍니다 [1]. 논문의 사례 연구에서는 일련번호로 동영상 다섯 개를 한 계정·한 안경에 묶었고, 짝짓기 ID 두 개가 섞여 있는 것을 보고 그날 초기화와 다시 짝짓기가 있었다고 판단했습니다 [1].

**증명하지 못하는 것.** 안경에는 사용자를 확인하는 강한 인증이 없어서, 기록은 "그 계정에 짝지은 그 안경이 찍었다" 까지만 말합니다 [1]. 누가 안경을 쓰고 있었는지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 다른 증거와 맞춥니다. 논문 실험에서 사진에는 위치가 남지 않았으므로 [1], 사진에 위치 기록이 없다고 해서 "그곳에 없었다" 로 읽지 않습니다. `aimodels/` 의 모델 파일은 초기화와 로그아웃 뒤에도 남았으므로 [1], 모델 파일이 있다는 사실은 AI 기능을 썼다는 근거가 되지 않습니다. 기기의 대화 기록에서 사용자 질문이 가려져 있으므로 [1], 질문 내용은 캐시나 클라우드 내보내기에서 따로 찾아야 합니다.

## 시각 해석

플러그인은 `capture_timestamp_ms`, `import_completed_timestamp_ms`, `fetch_timestamp_ms` 를 1970-01-01 UTC 기준 밀리초로 보고 1000 으로 나눈 뒤 SQLite 의 `datetime(..., "unixepoch")` 로 UTC 문자열을 만듭니다 [2]. 값이 정수로 저장돼 있으면 SQLite 의 `/1000` 은 정수 나눗셈이 되므로, 보고서 시각에는 밀리초가 빠집니다. 논문 사례 연구에서 현지 시각(CDT) 오후 5:30~5:45 의 대화를 찍은 동영상이 UTC 22:31:18~22:43:27 로 나왔으므로 [1], 앱 데이터베이스의 시각은 UTC 로 읽고 보고서에는 현지 시각을 함께 적습니다.

한 번의 촬영에는 시각이 두 개 있습니다. `capture` 의 촬영 시각은 안경에서 찍은 때이고, `media_item` 의 가져온 시각은 휴대폰으로 옮긴 때라서 둘 사이에 간격이 생길 수 있습니다 [1][2]. 클라우드 내보내기에서 플러그인은 대화 날짜를 `Conversation with Meta AI_` 뒤의 `두 자리-두 자리-네 자리` 날짜로, 미디어 시각을 `Jan 05, 2026 3:04 pm`(만든 예시) 같은 영문 문자열로 읽고, 둘 다 시간대 표시가 없어서 [2], 기기 쪽 UTC 기록 몇 개와 맞춰 본 뒤 기준을 정합니다. 여러 기록을 한 줄로 세우는 법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)과 [Android 타임라인 작성](https://urock-ailab.github.io/forensics-handbook-android/03-techniques/analysis/timeline/index.html)에 있습니다.

## 함정과 한계

### 지우기와 초기화

논문은 사용자가 할 수 있는 지우기 동작 아홉 가지를 하고 앱 폴더에 무엇이 남는지 봤습니다 [1]. 아래는 논문 표 6 을 옮긴 것입니다. ✓ 는 남음(또는 다시 생김), ✗ 는 지워짐(또는 없음), △ 는 일부만 남거나 바뀜, ⟳ 는 새 값으로 바뀜입니다.

| 아티팩트 | AF1 캐시 지우기 | AF2 짝짓기 해제 후 다시 짝짓기 | AF3 미디어 삭제 | AF4 음성 활동 삭제 | AF5 대화 삭제 | AF6 안경 초기화 후 다시 짝짓기 | AF7 로그아웃 | AF8 앱 삭제 | AF9 다시 설치 후 다시 짝짓기 |
|---|---|---|---|---|---|---|---|---|---|
| 사용자 ID | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ |
| 기기 일련번호 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| 기기 UUID | ✓ | ✓ | ✓ | ✓ | ✓ | ⟳ | ✓ | ✗ | ✓ |
| 짝짓기 ID(MAC) | ✓ | ⟳ | ✓ | ✓ | ✓ | ⟳ | ⟳ | ✗ | ⟳ |
| 사진·동영상 | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| AI 질의 이미지 | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| 동영상 위치 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| 대화 기록(`interaction_log.db`) | ✓ | △ | ✓ | ✓ | ✓ | △ | ✓ | ✗ | ✗ |
| GraphQL 캐시 | △ | ✓ | △ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| 어시스턴트 로그 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | △ | ✗ | ✗ |

안경을 초기화하면 짝짓기 ID 는 바뀌지만, 초기화 전에 찍은 미디어의 데이터베이스 기록에는 옛 짝짓기 ID 가 그대로 남았습니다 [1]. 일련번호는 앱을 지우는 경우(AF8)를 빼면 모든 동작 뒤에 그대로였습니다 [1]. `device_system_info_` 파일도 초기화와 다시 짝짓기 뒤에 지금 MAC 과 예전 MAC 의 기록을 함께 담고 있었습니다 [1]. 표 6 에서 짝짓기 ID 는 짝짓기 해제(AF2), 안경 초기화(AF6), 로그아웃(AF7), 다시 설치(AF9) 뒤에 바뀌었습니다 [1]. 그래서 짝짓기 ID 가 여러 개 보이면 이 가운데 하나가 있었다는 흔적으로 먼저 해석하고, 짝짓기 ID 가 바뀐 시점을 타임라인에 올립니다.

클라우드 쪽은 동작마다 다르게 움직였습니다 [1]. 앱에서 미디어를 지우자 뒤에 받은 내보내기의 `meta_ai_media.html` 과 `posts/media/your_posts/` 에서도 AI 처리한 미디어가 사라졌고, "Delete Voice Activity" 를 쓰자 클라우드의 대화 기록이 빠졌습니다 [1]. 그런데 AI 로 만든 알림은 대화 기록을 지우고 안경을 초기화한 뒤에도 `reminders.html` 에 남아 있어서, 앱에서 따로 지워야 사라졌습니다 [1]. 클라우드 기록은 기기를 초기화해도 남았습니다 [1]. 기기와 클라우드의 차이 자체가 선택적으로 지운 흔적이 될 수 있다고 논문은 봅니다 [1].

### 도구의 한계

플러그인 설명서는 연구 기간에 본 파일 구조로 만들고 시험했다고 적었으므로 [3], 앱 판이 258.0.0.15.167 과 다르면 결과가 비거나 어긋날 수 있습니다. 2026-04-12 판 플러그인[2]을 쓸 때는 아래를 알고 결과를 읽습니다.

- 파일 이름에 `StellaDatabase` 가 든 파일이 여러 개여도 첫 번째 하나만 엽니다.
- "Media Timeline" 보고서는 `media_file.uri` 가 없는 행을 빼므로, 파일이 지워진 촬영 기록은 이 보고서에 나오지 않습니다. 지운 미디어를 찾을 때는 `capture` 표를 직접 봅니다.
- 같은 보고서는 `user_profile` 을 모든 행에 붙이므로(`CROSS JOIN`), 프로필 행이 둘 이상이면 촬영 한 번이 여러 줄로 나옵니다.
- 같은 보고서는 `multimodal_metadata` 를 이어 붙이지만 그 표의 칸은 내보내지 않으므로, 어느 미디어를 AI 시각 질의에 썼는지는 표를 직접 봅니다.
- "Paired Devices (from DB)" 보고서는 `pairing_id` 가 비었거나 NULL 인 행을 빼고, 짝짓기 ID 와 일련번호 쌍마다 첫 촬영과 마지막 촬영 시각만 보여 줍니다.
- 경로 목록에 `*/facebook_view/media/*` 가 있지만 이 파일을 처리하는 코드는 없습니다.
- "Connected Devices (Cloud)" 보고서는 `connected_devices.html` 파일 하나에서 첫 번째 일련번호와 갱신 시각만 뽑습니다.
- `interaction_log.db`, GraphQL 캐시, `assistantLogs/` 는 경로 목록에 없어서 직접 봐야 합니다. 논문은 플러그인이 JSON 로그에서 AI 대화를 뽑고 캐시에서 미디어를 되살린다고 적었지만 [1], 2026-04-12 판 코드에는 그 처리가 없습니다 [2].

플러그인 설명서는 클라우드 HTML 을 읽는 부분이 Meta 내보내기 형식에 기대므로 형식이 바뀌면 고쳐야 할 수 있다고 적었습니다 [3]. 클라우드 HTML 파서는 `_a6_q`, `_2piu _a6_r` 같은 클래스 이름으로 칸을 찾으므로 [2], 결과가 비어 있으면 HTML 을 직접 열어 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

`capture_timestamp_ms` 는 SQLite 정수로 저장됩니다. SQLite 는 정수를 담을 수 있는 가장 짧은 길이로 저장하고, 지금 시각의 밀리초 값은 4바이트를 넘고 6바이트 안에 들어가서 형식 번호 `0x05`(6바이트 정수)로 저장됩니다. 아래 값은 SQLite 명세로 만든 예시이고 실제 검체 값이 아닙니다.

```text
레코드 머리의 형식 번호: 05                 -> 6바이트 부호 있는 정수(빅 엔디언)
레코드 본문의 값:        01 9B 77 83 31 03   -> 0x019B77833103
10진수:                  1767236645123       -> 밀리초
1000 으로 나눈 값:       1767236645.123      -> 2026-01-01 03:04:05.123 UTC
```

`capture` 의 `device_serial` 값이 `device_system_info_` 파일과 `connectivity_metadata.xml`, 클라우드의 `meta_ai_media.html` 에도 같은 문자열로 나오는지 문자열 검색으로 확인하면 층과 층을 잇는 값이 맞는지 볼 수 있습니다 [1][2].

### 공개 도구로 한 번

1. 루트 권한으로 받은 앱 폴더를 해시로 고정한 뒤 복사본으로 작업합니다. 논문도 수집한 파일마다 SHA-256 을 남겼습니다 [1].
2. ALEAPP 의 `scripts/artifacts/` 에 `meta_ai.py` 를 넣고, 앱 폴더와 클라우드 내보내기를 입력으로 돌립니다 [3].
3. "User Profile", "Paired Devices (from DB)", "Media Timeline", "Paired Devices (Detailed)", "Linked Accounts", "AI Conversations (Cloud)", "Connected Devices (Cloud)", "Cloud Media Library" 보고서가 나옵니다 [2].
4. 도구의 한계에 적은 부분(`capture` 전체, `interaction_log.db`, 캐시, `assistantLogs/`)은 SQLite 도구와 문자열 검색으로 따로 엽니다.

## 교차 검증

| 맞춰 볼 것 | 이어 주는 값 | 알 수 있는 것 |
|---|---|---|
| `capture` ↔ 클라우드 `meta_ai_media.html` | 기기 일련번호, 날짜 | 기기에서 지운 미디어가 클라우드에 있었는지 [1] |
| `interaction_log.db` ↔ GraphQL 캐시 ↔ `your_ai_conversations.html` | 대화 시각, 응답 글 | 기기에서 가려진 사용자 질문의 평문 [1] |
| `capture` ↔ `device_system_info_` 파일 | 짝짓기 ID(MAC) | 예전에 짝지었던 연결과 초기화 시점 [1] |
| `media_item_location` ↔ 휴대폰의 다른 위치 기록 | 시각 | 동영상 위치가 휴대폰 위치와 맞는지 |
| `update_log` ↔ `systems_health_report.txt` | 시각(칸 이름은 검체에서 확인) | 펌웨어 업데이트와 연결 이벤트 |

계정 ID 와 일련번호로 사람과 기기를 잇는 순서는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)에, 캐시에서 대화를 되살리는 일반 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)에 있습니다. 앱 설정 XML 을 읽는 법은 [설정 XML과 SharedPreferences](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/shared-preferences.html)를 봅니다.

## 실습

루팅한 시험용 Android 기기와 새 Meta 계정으로 논문의 순서[1]를 따라 풀어 봅니다.

1. 앱을 설치하기 전·후와 안경을 짝지은 뒤에 앱 폴더를 받아 비교하고, `StellaDatabase` 에 새로 생긴 표를 적습니다.
2. 사진 한 장과 동영상 한 편을 찍은 뒤 `capture` 행의 촬영 시각과 `media_item` 의 가져온 시각이 얼마나 차이 나는지, 동영상에만 `media_item_location` 행이 생기는지 봅니다.
3. 음성으로 질문 하나를 한 뒤 `interaction_log.db` 에 질문이 `<redacted>` 로 남는지, 같은 질문이 GraphQL 캐시와 클라우드 내보내기에 평문으로 있는지 찾습니다.
4. 안경을 초기화하고 다시 짝지은 뒤 새로 찍은 미디어와 예전 미디어의 `pairing_id` 가 다른지 확인합니다.
5. 앱에서 미디어 하나를 지우고 클라우드 내보내기를 다시 받아 `meta_ai_media.html` 에서 사라졌는지 비교합니다.

## 참고 문헌

1. Shishir Panta, Ruba Alsmadi, Ibrahim Baggili, "Seeing the Evidence: A Forensic Framework for Analyzing Ray-Ban Meta AI Smart Glasses", Louisiana State University BiT Lab 논문 전문(본문 1~8절, 표 1~7). 코드 공개 주소는 논문의 Code Availability 절에 있습니다
2. BiTLab-BaggiliTruthLab/Meta-AI-Parser, `meta_ai.py`(버전 1.0.0, 작성 Shishir Panta, 2026-04-12) — https://github.com/BiTLab-BaggiliTruthLab/Meta-AI-Parser/blob/main/meta_ai.py
3. BiTLab-BaggiliTruthLab/Meta-AI-Parser, `README.md` — https://github.com/BiTLab-BaggiliTruthLab/Meta-AI-Parser
