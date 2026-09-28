---
title: "계정과 친구 목록"
parent: "카카오톡"
grand_parent: "아티팩트 · 메신저"
nav_order: 940
---

# 계정과 친구 목록 (Account·Friends)

친구 목록은 로그인한 뒤 생기는 `KakaoTalk2.db` 의 `friends` 표에 들어 있고, 이름·전화번호·프로필 같은 열은 암호화돼 있으며, 이 열을 풀 때 쓰는 기기 주인의 사용자 ID 는 `open_profile` 표에 있습니다.

## 무엇을 기록하나 · 왜 생기나

카카오톡에 로그인하면 `databases` 폴더에 `KakaoTalk2.db` 가 생기고, 친구 정보와 차단한 친구, 채널 기록이 이 DB 에 쌓입니다. 파일 위치와 로그인 뒤에 생기는 다른 파일은 [저장 위치와 파일](paths-files.md)에서 다룹니다.

표 구조는 공개 포렌식 도구 CARPE[2][3], 암호화 열 목록은 공개 스크립트 kakaodecrypt[1] 기준입니다. 두 도구가 어느 앱 버전에 맞춰 만들어졌는지와 Android 버전·삼성 One UI 에 따른 차이는 실제 기기에서 확인해야 합니다.

## 구조

### KakaoTalk2.db 의 표

`KakaoTalk2.db` 의 주요 표는 다음과 같습니다[2][3].

| 표 | 한 행의 열 수(CARPE 기준) | 비고 |
|---|---|---|
| `friends` | 37 | 암호화 열을 푼 뒤 `friends_dec` 로 읽음 |
| `block_friends` | 4 | |
| `channel_history` | 8 | |
| `open_profile` | — | 기기 주인의 사용자 ID 가 든 표 |

`open_profile` 표는 `friends` 와 같은 DB 파일에서 읽히므로 `KakaoTalk2.db` 에 있는 것으로 보입니다[1].

같은 방식으로 암호화된 표로 `friends_board_contents`(`image_url`, `thumbnail_url`, `url`, `v` 열), `item`(`v` 열), `item_resource`(`v` 열)도 있습니다[1]. 이 표들이 어느 DB 파일에 있는지는 실제 기기에서 확인합니다.

### friends 의 열

`friends` 의 37개 열을 순서대로 적으면 다음과 같습니다[3].

```
_id, contact_id, id, type, uuid, phone_number, raw_phone_number, name,
phonetic_name, profile_image_url, full_profile_image_url,
original_profile_image_url, status_message, chat_id, brand_new, blocked,
favorite, position, v, board_v, ext, nick_name, user_type, story_user_id,
account_id, linked_services, hidden, purged, member_type, involved_chat_ids,
contact_name, enc, created_at, new_badge_updated_at, new_badge_seen_at,
status_action_token, status_action_v
```

이 가운데 암호화되는 열은 다음과 같습니다[1].

```
uuid, phone_number, raw_phone_number, name,
profile_image_url, full_profile_image_url, original_profile_image_url,
status_message, v, board_v, ext, nick_name, contact_name
```

`friends` 에는 행마다 `enc` 열이 있어서, 이 값으로 그 행에 쓰인 암호화 방식을 구분합니다[1]. 대화 표 `chat_logs` 가 `v` 열의 JSON 에서 enc 값을 찾는 것과 다른 점이고, 암호화 방식 전반은 [대화 DB 구조와 암호화](chat-db.md)에서 설명합니다.

### 기기 주인의 사용자 ID

친구 쪽 표를 풀 때는 `open_profile` 표의 `user_id` 를 기기 주인의 사용자 ID 로 씁니다[1]. 이 값이 없으면 kakaodecrypt 에 사용자 ID 를 직접 넣어야 하고, kakaodecrypt 저장소에는 `guess_user_id.py` 라는 보조 스크립트도 있습니다.

이름으로 짐작하면 계정·프로필과 관련 있는 파일은 로그인한 뒤 새로 생기는 `shared_prefs/KakaoTalk.profile.preferences.xml`, `shared_prefs/KakaoTalk.multiprofile.preferences.xml`, `databases/multi_profile_database.db` 와, 설치 직후부터 있다가 로그인할 때 바뀌는 `files/datastore/LocalUser_DataStore.pref.preferences_pb` 입니다[4]. 이 파일들의 내용은 실제 기기로 확인해야 합니다.

Android 계정 관리자(`dumpsys account`)에 카카오 계정이 어떤 계정 종류로 나오는지는 실제 기기에서 확인합니다. 계정 관리자 기록을 읽는 법은 [계정 (Accounts)](../../system-account/accounts/index.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `friends` 에 행이 있으면 그 상대가 이 계정의 친구 목록에 올라 있었다는 기록이 됩니다. `chat_id`, `involved_chat_ids` 열은 이름으로 짐작하면 대화방과 이어 주는 값으로 보이고, `chat_logs` 의 `user_id` 를 `friends` 와 맞춰 보면 대화 상대의 이름을 붙일 수 있습니다.

**증명하지 못하는 것.** 친구 목록에 있다는 사실만으로 그 상대와 대화했다고 말할 수는 없습니다. `blocked`, `favorite`, `hidden`, `purged` 같은 열은 이름으로 보면 차단·즐겨찾기·숨김·삭제 상태를 뜻하는 것 같지만, 값의 뜻은 정해져 있지 않으므로 보고서에 "차단했다" 처럼 단정하지 않습니다. `name` 과 `contact_name` 이 어떻게 다른지는 기기의 연락처와 앱 화면에 보이는 이름을 맞춰 보고 확인합니다.

## 시각 해석

`friends` 에는 `created_at`, `new_badge_updated_at`, `new_badge_seen_at` 시각 열이 있습니다. 세 열의 단위와 시간대, 값이 바뀌는 때는 값만 보고 단정하지 않습니다. 단위를 추정하는 방법은 [시각 값](../../../01-foundations/value-decoding/time-values.md)을 보고, 시험 기기에서 친구를 추가한 시각과 비교해 확인한 뒤에 씁니다.

## 함정과 한계

암호화 열을 푸는 도구는 사용자 ID 가 맞아야 제대로 된 값을 돌려줍니다. `open_profile` 에서 값을 찾지 못해 사용자 ID 를 직접 넣었다면, 그 값을 어디서 얻었는지 보고서에 함께 적습니다.

CARPE 도 kakaodecrypt 와 같은 방식으로 `friends_dec` 표를 만들어 읽으므로 원본이 아닌 사본에서 작업합니다. 열 목록은 CARPE 스키마 한 가지를 기준으로 한 것이라, 실제 파일의 열 수가 다르면 그대로 기록해 둡니다.

## 직접 분석해 보기

사본을 SQLite 뷰어로 열어 `friends`, `block_friends`, `channel_history`, `open_profile` 표가 있는지 보고, `friends` 의 열 수가 37개인지 확인합니다. `phone_number`, `name` 열에 읽을 수 있는 값 대신 Base64 문자열이 들어 있으면 암호화된 상태이고, `enc` 열에 어떤 값들이 나오는지 세어 둡니다. 암호화된 열은 kakaodecrypt 나 CARPE 로 풀 수 있고, 풀린 전화번호는 기기 연락처와 맞춰 봅니다.

## 교차 검증

- [연락처 (contacts2.db)](../../communications/contacts.md) — 풀린 전화번호가 기기 연락처에 있는지, 이름이 어떻게 저장돼 있는지 맞춰 봅니다.
- [계정 (Accounts)](../../system-account/accounts/index.md) — 기기에 등록된 계정과 계정이 더해지거나 지워진 기록을 봅니다.
- [대화 DB 구조와 암호화 (KakaoTalk.db)](chat-db.md) — `chat_logs` 의 `user_id` 로 대화 상대를 친구 목록과 이어 봅니다.
- [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md) — 로그인한 계정이 곧 기기를 쓴 사람이라고 볼 수 있는지 따지는 조사 흐름입니다.

## 실습

카카오톡이 설치된 공개 이미지나 직접 만든 시험 기기 이미지로 다음 질문을 풀어 봅니다.

1. `KakaoTalk2.db` 에 어떤 표가 있고, `friends` 의 열 수는 몇 개입니까?
2. `open_profile` 표가 있습니까? 있다면 `user_id` 열에 값이 들어 있습니까?
3. 시험 기기에서 친구를 한 명 차단한 뒤 `friends` 와 `block_friends` 에서 무엇이 바뀝니까?

## 참고 문헌

1. jiru/kakaodecrypt — kakaodecrypt.py. https://github.com/jiru/kakaodecrypt/blob/HEAD/kakaodecrypt.py
2. dfrc-korea/carpe — modules/kakaotalk_mobile_decrypt_connector.py. https://github.com/dfrc-korea/carpe/blob/HEAD/modules/kakaotalk_mobile_decrypt_connector.py
3. dfrc-korea/carpe — modules/schema/kakaotalk_mobile/lv1_app_kakaotalk_mobile_friends.yaml. https://github.com/dfrc-korea/carpe/blob/HEAD/modules/schema/kakaotalk_mobile/lv1_app_kakaotalk_mobile_friends.yaml
4. stulle123/kakaotalk_analysis — recon/file_diff_before_and_after_login.txt. https://github.com/stulle123/kakaotalk_analysis/blob/HEAD/recon/file_diff_before_and_after_login.txt
5. stulle123/kakaotalk_analysis — doc/RECON.md. https://github.com/stulle123/kakaotalk_analysis/blob/HEAD/doc/RECON.md
