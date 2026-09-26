---
title: "삼성 메시지 앱"
parent: "문자"
grand_parent: "아티팩트 · 통화·문자·연락처"
nav_order: 590
---

# 삼성 메시지 앱 (Samsung Messages)

삼성 메시지 앱의 DB 경로나 표 이름을 보여 주는 공개 자료가 없어서, 이 페이지는 앱 자체 DB 의 구조 대신 삼성 기기에서 어디부터 볼지를 다룹니다.

## 한 줄 요약

삼성 메시지 앱 자체의 DB 경로·표·열은 공개 자료가 없습니다. 공개 파서 ALEAPP 는 삼성 기기의 문자를 시스템 문자 DB(mmssms.db)로 읽고, 삼성 표본 이미지에는 Google 메시지 앱 DB(bugle_db)도 함께 있었습니다 [1][2].

## 알려진 것과 공개 자료가 없는 것

| 항목 | 내용 |
|---|---|
| 패키지 이름 | com.samsung.android.messaging 으로 알려져 있으나 공식 문서나 소스로 밝힌 자료는 없음. 실제 기기의 패키지 목록에서 확인 |
| 앱 자체 DB 의 경로·표·열 | 공개 자료 없음. ALEAPP 저장소 코드 검색에서 "com.samsung.android.messaging" 이 0건이고 [3], 모듈 목록에도 삼성 메시지 전용 모듈이 없음 [4] |
| ALEAPP 가 읽는 곳 | 삼성 기기의 문자도 mmssms.db 모듈(smsmms.py)로 읽고, 삼성 기기의 mmssms.db 에서는 spam_sms 표를 더 읽음 [1] |
| 기본 문자 앱 | 삼성 메시지인지 Google 메시지인지는 실제 기기에서 확인 |
| 삼성 클라우드·스마트 스위치 백업 안의 메시지 형식 | 공개 자료 없음 |
| One UI 버전별 차이 | 공개 자료 없음 |

spam_sms 표는 [문자 DB 구조 (mmssms.db)](mmssms-db.md) 페이지의 버전별 차이 표에 정리했습니다.

## 삼성 기기에서 문자를 찾는 순서

ALEAPP 가 결과를 공개한 삼성 표본 이미지에는 mmssms.db 의 문자와 Google 메시지 bugle_db 가 함께 들어 있었습니다 [1][2].

| 표본 | Android | mmssms.db | bugle_db |
|---|---|---|---|
| samsunga53_a14 | 14 | SMS 41행, MMS 4행 | 45행 |
| samsungs20_a13 | 13 | SMS 35행, MMS 6행 | 40행 |
| galaxys10_a10 | 10 | SMS 32행 | 공개 결과 없음 |

삼성 기기라고 해서 Google 메시지 DB 를 건너뛰지 않습니다. 먼저 시스템 문자 DB 인 mmssms.db 를 [문자 DB 구조 (mmssms.db)](mmssms-db.md) 페이지대로 읽고, bugle_db 가 있으면 [RCS 메시지 (RCS)](rcs.md) 페이지대로 읽어 두 결과를 맞춰 봅니다. 삼성 메시지 앱 자체의 데이터 폴더가 이미지에 있다면 [앱 데이터 분석 (App Data Analysis)](../../../03-techniques/analysis/app-data-analysis/index.md) 의 방법으로 DB 와 설정 파일을 하나씩 열어 보되, 표와 열의 뜻을 추측으로 적지 않습니다. 삼성 기기의 IMS 서비스 로그는 RCS 페이지에서 다룹니다.

## 기기 설정 키

설정 값에는 이름에 메시지가 들어간 아래 키가 있을 수 있습니다. 키의 뜻을 밝힌 공개 자료는 없습니다.

| 설정 구역 | 키 |
|---|---|
| settings secure | `is_support_samsung_message_key`, `rampart_enabled_message_guard` |
| settings system | `show_message_logs`, `videocallmessage_settings` |

이름만 보고 앱이나 기능이 켜져 있었다고 쓰지 않습니다. 설정 값을 뽑고 읽는 법은 [설정 값 (Settings Global·Secure·System)](../../system-account/settings.md) 페이지에 있습니다.

## 함정과 한계

공개 파서에 삼성 메시지 전용 모듈이 없어서, 도구가 삼성 기기에서 보여 주는 문자는 mmssms.db 와 bugle_db 에서 온 결과입니다 [1][2][4]. 삼성 메시지 앱이 자체 DB 에만 두는 내용이 있다면 도구 결과에서 빠질 수 있으니, 도구 결과가 비어 있다고 문자가 없었다고 쓰지 않습니다. 기본 문자 앱이 무엇인지 기록하는 위치도 공개 자료가 없어서, 어느 앱으로 문자를 주고받았는지는 mmssms.db 의 creator 열이나 앱 사용 기록처럼 다른 흔적으로 따로 확인합니다.

## 교차 검증

앱을 언제 썼는지는 [앱 사용 기록 (usagestats)](../../app-usage/usagestats/index.md), 기기에 설치된 메시지 앱은 [설치된 앱 (packages.xml)](../../app-usage/packages/index.md) 에서 확인합니다. 클라우드 쪽 사본은 [삼성 클라우드와 원드라이브 (Samsung Cloud·OneDrive)](../../mail-cloud/samsung-cloud-onedrive.md) 페이지를 봅니다.

## 참고 문헌

1. ALEAPP smsmms.py — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/smsmms.py
2. ALEAPP googleMessages.py — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/googleMessages.py
3. GitHub 코드 검색 "com.samsung.android.messaging" repo:abrignoni/ALEAPP (결과 0건), https://api.github.com/search/code?q=%22com.samsung.android.messaging%22+repo:abrignoni/ALEAPP
4. ALEAPP scripts/artifacts 폴더 목록 — abrignoni/ALEAPP (GitHub API), https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
