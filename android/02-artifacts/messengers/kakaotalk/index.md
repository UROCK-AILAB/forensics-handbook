---
title: "카카오톡"
parent: "아티팩트 · 메신저"
nav_order: 900
has_children: true
has_toc: false
---

# 카카오톡 (KakaoTalk)

카카오톡은 대화와 친구 목록을 앱 내부 저장소의 SQLite 데이터베이스 두 개에 남기고, 그 안에서 본문·첨부 정보·친구 이름 같은 일부 열만 따로 암호화해 둡니다.

## 왜 중요한가

대화 기록, 대화방, 친구 목록이 앱 폴더 안의 DB 에 모여 있어서 누구와 언제 연락했는지 재구성할 때 중심이 되는 자료입니다. 다만 DB 파일은 보통 SQLite 로 열리지만 메시지 본문 같은 열에는 암호문이 들어 있어 그대로는 읽을 수 없고, 이 열을 풀어 주는 공개 도구도 앱이 새 암호화 방식을 쓰면 통하지 않을 수 있습니다. 그래서 파일을 찾는 단계부터 해석하는 단계까지 앱 버전과 도구의 한계를 함께 적어 두어야 합니다.

Android 앱 패키지 이름은 `com.kakao.talk` 입니다. 앱 폴더가 어디에 있고 어떤 권한으로 읽을 수 있는지는 [앱 데이터 폴더 구조](../../../01-foundations/storage/app-data-layout.md)와 [앱 샌드박스와 권한](../../../01-foundations/security-model/sandbox-permissions.md)에서 다룹니다.

폴더 목록은 카카오톡 10.1.7, Android 11 에뮬레이터 기준이라[6] 요즘 버전과는 다를 수 있습니다. Android 버전이나 제조사(삼성 One UI)에 따른 차이는 실제 기기에서 확인해야 합니다.

## 한눈에 보기

| 위치 | Android 버전 | 알려 주는 것 |
|---|---|---|
| `/data/user/0/com.kakao.talk/databases/KakaoTalk.db` | 카카오톡 10.1.7, Android 11 에뮬레이터 기준. 다른 버전은 실제 기기에서 확인 | 대화 기록(`chat_logs`)과 대화방(`chat_rooms`) |
| `/data/user/0/com.kakao.talk/databases/KakaoTalk2.db` | 위와 같음 | 친구 목록(`friends`), 차단한 친구, 채널 기록 |
| `/data/user/0/com.kakao.talk/shared_prefs/`, `files/datastore/` | 위와 같음 | 로그인한 뒤 생기거나 바뀌는 계정·프로필 설정 파일 |
| `/storage/emulated/0/Android/data/com.kakao.talk/cache` | 위와 같음 | 외부 캐시. 받은 파일 원본이 남는지는 공개 자료 없음 |

`/data/user/0/com.kakao.talk/` 는 `/data/data/com.kakao.talk/` 와 같은 폴더입니다.

공개 도구로는 개인이 만든 Python 스크립트 kakaodecrypt 와 포렌식 도구 CARPE(GitHub 조직 dfrc-korea)의 카카오톡 모바일 모듈이 두 DB 를 다룹니다[3][4]. ALEAPP 의 artifacts 폴더에는 카카오톡 모듈이 없습니다[1].

## 읽는 순서

1. [저장 위치와 파일 (Paths·Files)](paths-files.md) — 앱 폴더 아래 DB·설정 파일·캐시가 어디에 있고, 로그인 전과 뒤에 무엇이 새로 생기는지 정리합니다.
2. [대화 DB 구조와 암호화 (KakaoTalk.db)](chat-db.md) — `chat_logs`·`chat_rooms` 표의 열과 암호화된 열, 시각 열을 읽을 때 주의할 점을 다룹니다.
3. [받은 파일 (Received Files)](received-files.md) — 첨부 정보가 들어가는 열과, 받은 파일 원본의 위치처럼 공개 자료가 없는 부분을 나눠 적습니다.
4. [계정과 친구 목록 (Account·Friends)](account-friends.md) — `KakaoTalk2.db` 의 친구 표와, 암호화된 열을 풀 때 필요한 기기 주인의 사용자 ID 를 어디서 찾는지 설명합니다.

## 함께 볼 페이지

- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) — 두 DB 가 WAL 방식으로 쓰여서 최근 기록이 `-wal` 파일에 남을 수 있고, 이 구조를 여기서 설명합니다.
- [설정 XML과 SharedPreferences (XML·SharedPreferences)](../../../01-foundations/data-formats/shared-preferences.md) — `shared_prefs` 폴더의 설정 파일 형식입니다.
- [연락처 (contacts2.db)](../../communications/contacts.md) — 카카오톡 친구의 전화번호를 기기 연락처와 맞춰 볼 때 봅니다.
- [알림 기록 (Notification History)](../../app-usage/notification-history.md) — 앱 DB 밖에 남는 메시지 알림 흔적을 볼 때 씁니다.
- [누구와 연락을 주고받았나 (Communication)](../../../04-scenarios/activity/communication.md) — 카카오톡을 포함해 연락 상대를 재구성하는 조사 흐름입니다.
- [지운 대화와 사진 찾기 (Deleted Content)](../../../04-scenarios/activity/deleted-content.md) — 지운 대화를 찾을 때 DB 와 `-wal` 파일을 어떻게 보는지 다룹니다.

## 참고 문헌

1. ALEAPP — scripts/artifacts 폴더 목록. https://github.com/abrignoni/ALEAPP/tree/main/scripts/artifacts
2. jiru/kakaodecrypt — README.md. https://github.com/jiru/kakaodecrypt
3. jiru/kakaodecrypt — kakaodecrypt.py. https://github.com/jiru/kakaodecrypt/blob/HEAD/kakaodecrypt.py
4. dfrc-korea/carpe — modules/kakaotalk_mobile_decrypt_connector.py. https://github.com/dfrc-korea/carpe/blob/HEAD/modules/kakaotalk_mobile_decrypt_connector.py
5. stulle123/kakaotalk_analysis — recon/file_diff_before_and_after_login.txt. https://github.com/stulle123/kakaotalk_analysis/blob/HEAD/recon/file_diff_before_and_after_login.txt
6. stulle123/kakaotalk_analysis — doc/RECON.md. https://github.com/stulle123/kakaotalk_analysis/blob/HEAD/doc/RECON.md
