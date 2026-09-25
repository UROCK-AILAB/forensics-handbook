---
title: "문자"
parent: "아티팩트 · 통화·문자·연락처"
nav_order: 560
has_children: true
has_toc: false
---

# 문자 (SMS·MMS·RCS)

## 한 줄 요약

Android 의 SMS·MMS 는 시스템 제공자 패키지 com.android.providers.telephony 가 mmssms.db 한 파일에 담고, Google 메시지 앱은 자기 DB(bugle_db)를 따로 두며, RCS 대화가 어느 쪽에 들어가는지는 이번 조사에서 확인하지 못했습니다 [1][2][4].

## 왜 중요한가

문자는 누구와 언제 연락했는지를 보여 주는 기본 기록이고, 스미싱처럼 문자로 시작하는 사고에서는 첫 흔적이 되기도 합니다. mmssms.db 한 파일에 SMS(sms 표)와 MMS(pdu·part·addr 표)가 함께 들어 있고 두 종류가 threads 표의 대화 번호(thread_id)를 같이 쓰기 때문에 [1][2], 이 DB 하나로 대화 흐름을 상당 부분 되살릴 수 있습니다. 다만 MMS 첨부 파일은 DB 밖의 app_parts 폴더에 따로 있고 part 표의 _data 칸이 그 경로를 가리키니 [2][3], DB 와 폴더를 함께 확보해야 합니다.

시스템 문자 DB 만 보고 끝내면 빠지는 기록이 있습니다. Google 메시지 앱은 bugle_db 를 따로 두고 ALEAPP 도 이 DB 를 별도 모듈로 읽으며, ALEAPP 공개 표본에서는 Pixel 뿐 아니라 삼성 기기 이미지(samsunga53_a14, samsungs20_a13)에도 bugle_db 가 있었습니다 [4]. 반대로 삼성 메시지 앱 자체 DB 의 경로와 표 이름은 공개 자료로 확인하지 못했습니다 [6]. 기본 문자 앱이 무엇인지 기록하는 위치도 확인하지 못했고, 관찰한 폰의 settings secure 키 464개 가운데 `sms_default_application` 키는 없었습니다.

## 한눈에 보기

| 위치 | Android 버전 | 알려 주는 것 |
|---|---|---|
| `/data/user_de/0/com.android.providers.telephony/databases/mmssms.db` | 현행 AOSP 기준, 스키마 버전 69(main 가지) | SMS·MMS 본문, 상대 주소, 받음·보냄 구분, 시각, 대화 묶음 [1][2] |
| `/data/user_de/0/com.android.providers.telephony/app_parts` | 현행 AOSP 기준, FBE 를 쓰지 않던 기기를 Android 7(N) 로 올리면 `/data/data` 아래에서 이곳으로 옮김 | MMS 첨부 파일 본체 [2] |
| `*/com.google.android.apps.messaging/databases/bugle_db` | 오래된 DB 에는 일부 칸이 없음 | Google 메시지 앱의 대화·참여자·메시지 조각 [4] |
| com.sec.imsservice 앱 데이터 폴더의 `files/*.log` | 삼성 기기 | IMS 등록·데이터망·SIM 상태, 메시지 내용은 없음 [5] |

mmssms.db 의 전체 경로는 첨부 폴더 경로와 ALEAPP 경로 패턴으로 미루어 본 것이고, 자세한 근거는 아래 "문자 DB 구조" 페이지에 있습니다.

## 읽는 순서

1. [문자 DB 구조 (mmssms.db)](mmssms-db.md) — sms·pdu·part·addr·threads 표의 칸과 값, 밀리초와 초가 섞인 시각 단위, 첨부 파일 대응, 지울 때 도는 트리거를 다룹니다.
2. [RCS 메시지 (RCS)](rcs.md) — Google 메시지 bugle_db 에서 공개 파서가 읽는 표와 방향 판정, 삼성 IMS 서비스 로그, RCS 에 대해 확인하지 못한 점을 다룹니다.
3. [삼성 메시지 앱 (Samsung Messages)](samsung-messages.md) — 삼성 기기에서 확인한 것과 확인하지 못한 것, 문자를 찾는 순서, 관찰한 설정 키를 정리합니다.

## 함께 볼 페이지

- [통화 기록 (calllog.db)](../call-log.md), [연락처 (contacts2.db)](../contacts.md) — 같은 상대와의 통화와 연락처 이름
- [알림 기록 (Notification History)](../../app-usage/notification-history.md), [앱 사용 기록 (usagestats)](../../app-usage/usagestats/index.md) — 문자가 들어온 시각과 문자 앱을 연 시각
- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md), [시각 값](../../../01-foundations/value-decoding/time-values.md) — DB 를 직접 읽을 때 필요한 기초
- [카카오톡 (KakaoTalk)](../../messengers/kakaotalk/index.md), [텔레그램 (Telegram)](../../messengers/telegram.md) — 문자 밖에서 오간 대화
- [누구와 연락을 주고받았나 (Communication)](../../../04-scenarios/activity/communication.md), [스미싱 흔적 (Smishing)](../../../04-scenarios/incident/smishing.md), [지운 대화와 사진 찾기 (Deleted Content)](../../../04-scenarios/activity/deleted-content.md) — 이 기록을 쓰는 조사 시나리오

## 참고 문헌

1. Telephony.java — AOSP frameworks/base (main), https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/provider/Telephony.java
2. MmsSmsDatabaseHelper.java — AOSP packages/providers/TelephonyProvider (main), https://android.googlesource.com/platform/packages/providers/TelephonyProvider/+/refs/heads/main/src/com/android/providers/telephony/MmsSmsDatabaseHelper.java
3. ALEAPP smsmms.py — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/smsmms.py
4. ALEAPP googleMessages.py — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/googleMessages.py
5. ALEAPP samsungImsService.py — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/samsungImsService.py
6. GitHub 코드 검색 "com.samsung.android.messaging" repo:abrignoni/ALEAPP (결과 0건), https://api.github.com/search/code?q=%22com.samsung.android.messaging%22+repo:abrignoni/ALEAPP
