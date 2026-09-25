---
title: "빅스비"
parent: "아티팩트 · 삼성 기기 전용"
nav_order: 1150
---

# 빅스비 (Bixby)

## 한 줄 요약

빅스비는 삼성 기기의 음성 비서이고, 기기 안에 어떤 파일을 남기는지는 공개 포렌식 자료로 확인되지 않았지만, 설정 값의 키 이름과 삼성의 개인정보 처리방침으로 어떤 자료가 기기와 삼성 계정 쪽에 쌓일 수 있는지를 가늠할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

빅스비는 음성이나 터치로 받은 명령을 처리하려고 명령 내용과 기기 정보를 모읍니다. 삼성의 빅스비 개인정보 처리방침(Bixby Privacy Notice, 글로벌 영어판, 2026-01-01 시행)은 모으는 자료를 아래처럼 적었습니다.

| 갈래 | 처리방침에 적힌 항목 |
|---|---|
| 명령 | 음성 명령(질문·요청·지시), 터치 입력과 그 밖의 입력, 음성 호출(wake-up) 데이터와 녹음 |
| 기기 정보 | 하드웨어 모델, IMEI 같은 고유 식별자, MAC 주소, IP 주소, OS 버전 |
| 기기 안 자료 | 앱 사용 목록, 제3자 앱 정보, 연락처, 음악, 일정, 북마크, 메모, 통화 기록 |
| 위치 | 위치 기능을 켰을 때 GPS·Wi-Fi·기지국 정보 |

처리방침에 따르면 이 자료는 삼성 계정에 연결되고, 같은 계정으로 로그인한 모든 기기에 적용됩니다. 다만 처리방침은 어떤 자료가 기기에 남고 어떤 자료가 서버로 가는지를 나눠 적지 않았습니다. 그래서 처리방침은 "이런 자료가 어딘가에 있을 수 있다" 를 알려 줄 뿐, 기기 안 흔적의 위치를 알려 주지는 않습니다.

보관 기간은 자료마다 다르게 적혀 있습니다.

| 자료 | 보관 기간 |
|---|---|
| 읽어 주기(read-aloud) 내용 | 최대 30일 |
| 문제 해결용 녹음 | 계정 식별자와 연결해 1개월 보관한 뒤, 식별자를 떼어 모두 합쳐 1년까지 |
| 목소리 특징 정보(voiceprint) | 삼성 계정이 아닌 임의 식별자에 연결해 1년 |

처리방침은 사용자가 고를 수 있는 설정 메뉴로 "Bixby settings → Privacy settings → Allow audio recording review" 와 "Bixby settings → Voice wake-up → Recognize voice" 를 듭니다. 한국어 화면에서 이 메뉴가 어떤 이름으로 나오는지는 확인하지 못했습니다.

## 위치와 버전별 차이

빅스비 앱의 패키지 이름과 기기 안 데이터베이스·파일 경로는 공개 포렌식 자료에서 찾지 못했습니다. 삼성 전용 흔적을 모은 Mattia Epifani 의 글(2025-11)에도 빅스비 항목은 없습니다.

실제 폰에서 adb 일반 권한으로 설정 값의 키 이름을 읽었을 때 빅스비와 음성 비서에 관련된 이름으로 보이는 키는 아래와 같았습니다(확인 범위: Android 16, One UI 8.5). 값은 가려져 있고, 키의 뜻은 하나도 확인하지 못했습니다.

```
settings global : bixby_pregranted_permissions
settings system : bixby_setting_show_app_icon_enabled
                  add_info_com_samsung_android_app_routines#dashboard
                  key_now_bar_com_samsung_android_app_routines
settings secure : game_bixby_block
                  assistant, voice_interaction_service, voice_recognition_service
                  assist_long_press_home_enabled, assist_touch_gesture_enabled
```

system 쪽 두 키에는 "모드 및 루틴" 앱의 패키지 이름으로 보이는 `com_samsung_android_app_routines` 가 들어 있습니다. 예전 빅스비 루틴이 이 앱으로 옮겨 갔는지는 확인하지 못해서, 두 키를 빅스비 흔적으로 적지 않습니다. secure 쪽 `assistant`, `voice_interaction_service` 같은 키는 이름에 빅스비가 없어서, 값을 읽어야 어느 음성 비서를 가리키는지 알 수 있고 그 해석도 확인하지 못했습니다. 설정 값을 읽는 법과 저장 위치는 [설정 값](../system-account/settings.md) 에서 다룹니다.

One UI 판에 따라 빅스비가 어떻게 달라졌는지는 공식 자료로 확인하지 못했습니다.

## 구조

기기 안 파일을 확인하지 못해서 이 절에서 설명할 구조는 없습니다. 지금 볼 수 있는 흔적은 위 설정 키이고, 저장 형식은 [설정 값](../system-account/settings.md) 과 [안드로이드 바이너리 XML](../../01-foundations/data-formats/abx.md) 을 봅니다.

## 증거로서 의미

### 증명하는 것

설정 키 목록에 `bixby_` 로 시작하는 키가 있으면, 그 기기의 설정 저장소에 빅스비 관련 항목이 만들어져 있다는 것까지 말할 수 있습니다. 전체 추출로 값을 읽을 수 있다면 `voice_interaction_service` 같은 키가 기본 음성 비서를 가리킬 가능성이 있지만, 이 뜻은 확인하지 못했으므로 값을 적을 때 "이 키에 이 값이 있다" 까지만 씁니다.

처리방침은 증거가 아니라 수사 방향을 잡는 자료입니다. 음성 명령과 녹음, 목소리 특징 정보가 삼성 계정 쪽에 정해진 기간 동안 남을 수 있다고 적혀 있어서, 명령 내용이 필요하면 기기보다 계정 쪽 자료를 적법한 절차로 요청하는 길을 먼저 검토합니다([클라우드 데이터](../../03-techniques/acquisition/cloud-data.md)).

### 증명하지 못하는 것

설정 키가 있다고 해서 사용자가 빅스비를 켰거나 썼다는 뜻은 아닙니다. 기본 앱이 설정 항목을 미리 만들어 두는지 확인하지 못했기 때문입니다. 처리방침에 적힌 수집 항목도 한 사용자에게 그 자료가 실제로 있다는 증거가 아니고, 보관 기간이 지났으면 계정 쪽에도 남아 있지 않을 수 있습니다. 어떤 명령을 언제 말했는지는 지금 알려진 기기 안 흔적으로는 알 수 없습니다.

보고서에는 "빅스비로 이런 명령을 했다" 가 아니라 "이 기기의 설정 저장소에 이 빅스비 관련 키가 있고, 값은 이렇다" 처럼 씁니다.

## 시각 해석

확인한 설정 키 목록에는 시각 값이 없습니다. 빅스비 앱을 언제 썼는지는 [앱 사용 기록](../app-usage/usagestats/index.md) 에서 그 앱의 실행 흔적으로 찾아야 하는데, 패키지 이름을 공개 자료로 확인하지 못했으므로 설치된 앱 목록에서 먼저 짚어 둡니다. 처리방침의 보관 기간이 어느 시점부터 세는지는 처리방침에 적혀 있지 않습니다.

## 함정과 한계

`assistant`, `voice_interaction_service`, `voice_recognition_service` 는 이름에 빅스비가 없어서, 값을 읽어 어느 앱을 가리키는지 확인하기 전에는 빅스비 흔적으로 적지 않습니다. 구글 쪽 기록은 [구글 어시스턴트 기록](../google-services/google-assistant.md) 에서 다룹니다.

`routines` 가 들어간 키를 빅스비 루틴으로 읽는 것도 확인되지 않은 추측입니다. 처리방침은 판이 바뀌고 이번에 연 것은 글로벌 영어판 하나라서, 국내판 내용과 사건 당시 시행된 판은 따로 확인합니다. 빅스비의 기기 안 흔적을 다룬 공개 연구가 없어서, 도구가 결과를 내지 않는다고 흔적이 없다고 말할 수도 없습니다.

## 직접 분석해 보기

### 헥스로 한 번

헥스로 따라갈 파일을 공개 자료로 확인하지 못했습니다. 전체 추출본이 있다면 설치된 앱 목록에서 빅스비 관련 패키지를 찾고, 그 앱 데이터 폴더의 파일마다 첫 바이트를 보고 SQLite 인지, XML 인지, 프로토콜 버퍼인지부터 가립니다. 형식별로 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), [설정 XML과 SharedPreferences](../../01-foundations/data-formats/shared-preferences.md), [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 에 있습니다.

### 공개 도구로 한 번

1. adb 로 설정 키 목록을 읽습니다. `adb shell settings list global`, `adb shell settings list system`, `adb shell settings list secure` 를 차례로 실행하고 결과를 파일로 저장합니다.
2. 결과에서 `bixby`, `assist`, `voice_` 가 들어간 줄을 골라 위 목록과 비교합니다.
3. [설치된 앱](../app-usage/packages/index.md) 목록에서 빅스비 관련 패키지와 설치·갱신 시각을 확인합니다.
4. 그 패키지 이름으로 [앱 사용 기록](../app-usage/usagestats/index.md) 을 검색해 실행 흔적을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [설정 값](../system-account/settings.md) | 빅스비 관련 키의 값 |
| [설치된 앱](../app-usage/packages/index.md) | 빅스비 관련 패키지와 설치·갱신 시각 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 빅스비 앱이 앞에 뜬 시각 |
| [계정](../system-account/accounts/index.md) | 기기에 로그인한 삼성 계정. 처리방침상 빅스비 자료가 이 계정에 연결됨 |
| [구글 어시스턴트 기록](../google-services/google-assistant.md) | 같은 기기에서 다른 음성 비서를 쓴 흔적 |

Epifani 의 삼성 전용 흔적 목록에는 `com.samsung.android.privacydashboard` 의 `permission_db` 안 `permissionAccessInformations` 가 있고, 약 7일 치를 보관합니다. 빅스비가 마이크를 쓴 기록이 여기에 남는지는 확인하지 못했지만, 음성 명령 시각을 좁힐 후보로 확인해 볼 만합니다.

## 실습

공개 검체 가운데 삼성 기기 이미지를 골라 아래 질문을 풀어 봅니다.

1. 설정 값에서 `bixby` 가 들어간 키는 몇 개이고, 위 목록에 없는 키가 있습니까?
2. `voice_interaction_service` 의 값은 무엇이고, 그 값에 나오는 패키지가 설치된 앱 목록에 있습니까?
3. 설치된 앱 목록에서 빅스비 관련 패키지를 찾을 수 있습니까? 그 앱 데이터 폴더에는 어떤 형식의 파일이 있습니까?
4. `permission_db` 가 있다면, 마이크 권한을 쓴 앱 목록에 빅스비 관련 패키지가 나옵니까?

## 참고 문헌

1. Samsung, "Bixby Privacy Notice" (시행 2026-01-01) — https://d264isyiyrfhr3.cloudfront.net/storage/tos/glb/2.1.2/1765236349000/eng/glb_eng_pp.html
2. Mattia Epifani, "Beyond the Known: A Call to Forensic Research on Samsung Android Artifacts" (2025-11-07) — https://blog.digital-forensics.it/2025/11/beyond-known-call-to-forensic-research.html
