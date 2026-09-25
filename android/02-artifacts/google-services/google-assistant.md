---
title: "구글 어시스턴트 기록"
parent: "아티팩트 · 구글 입력·음성 비서"
nav_order: 1190
---

# 구글 어시스턴트 기록 (Google Assistant)

## 한 줄 요약

구글 어시스턴트(Google Assistant)와 구글 검색 위젯에 넣은 질의는 구글 앱 데이터 폴더의 `app_session` 아래 `.binarypb` 파일에 프로토콜 버퍼로 남고, 여기서 질의 글과 소리 데이터를 꺼낼 수 있지만 공개 도구가 보여 주는 시각은 파일 수정 시각뿐입니다. 계정 쪽에는 웹 및 앱 활동 기록이 따로 쌓입니다.

## 무엇을 기록하나 · 왜 생기나

기기 안의 어시스턴트 흔적은 구글 앱(패키지 `com.google.android.googlequicksearchbox`)의 데이터 폴더에 남습니다. 공개 도구 ALEAPP 는 이 흔적을 "Google Quick Search Queries" 모듈로 읽고, 모듈 설명은 "Search query sessions from the Google Search widget / Assistant (Google Now)" 입니다. 모듈 이름대로 구글 검색 위젯과 어시스턴트의 질의 세션이 같은 파일 묶음에 섞여 있고, 한 파일 안에는 세션 종류와 질의 글, 그리고 MP3 소리 데이터가 들어 있을 수 있습니다.

기기 밖에도 기록이 남습니다. 구글 계정의 웹 및 앱 활동(Web & App Activity)을 켜 두면 구글 어시스턴트 같은 일부 구글 서비스의 활동이 계정에 저장되고, 이 설정이 켜져 있을 때 "음성 및 오디오 활동 포함(Include voice and audio activity)" 을 따로 고를 수 있습니다. 저장된 활동은 My Activity(myactivity.google.com)에서 보고 지울 수 있고, 기기가 오프라인일 때도 활동이 저장될 수 있다고 안내합니다. 오프라인일 때 기기 안 어디에 임시로 두는지는 확인하지 못했습니다.

어시스턴트 전용 앱이 따로 있는지, 제미나이(Gemini)가 어시스턴트를 대신하는 기기에서 흔적 위치가 어떻게 바뀌는지는 출처로 확인하지 못했습니다. 삼성 기기의 음성 비서인 빅스비 쪽 흔적은 [빅스비](../samsung/bixby.md) 에서 다룹니다.

## 위치와 버전별 차이

```
/data/data/com.google.android.googlequicksearchbox/app_session/*.binarypb
```

ALEAPP 는 `app_session` 바로 아래의 `.binarypb` 파일만 읽고, 경로에 `/mirror/` 가 들어간 파일과 폴더는 건너뜁니다. 앱 데이터 폴더의 짜임은 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 에 있습니다.

이 모듈은 @abrignoni 가 만들었고 만든 날과 고친 날이 모두 2020-03-22 로 적혀 있지만, ALEAPP 의 시험 자료는 Android 13·14 기기입니다.

| 시험 자료 | Android | 구글 앱 버전 코드 | 결과 행 |
|---|---|---|---|
| sharon_a14 | 14 | 301381725 | 1 |
| russell_pixel6a_a13 (Pixel 6a) | 13 | 301246250 | 2 |
| 삼성 One UI 기기 | — | — | 시험 자료 없음 |

삼성 기기에서 같은 경로와 구조가 쓰이는지는 확인하지 못했습니다. 이 파일이 언제 만들어지고 얼마 동안 남는지도 출처에 없습니다.

기기 쪽 설정에는 음성 비서와 관련된 키 이름이 보입니다. 아래는 실제 기기에서 adb 일반 권한으로 읽은 키 이름이고, 값은 가려져 있어서 이 기기의 기본 비서가 어떤 앱인지는 알 수 없습니다(확인 범위: Android 16, One UI 8.5).

```
settings secure : assistant, voice_interaction_service, voice_recognition_service,
                  assist_long_press_home_enabled, assist_touch_gesture_enabled
settings global : hotword_detection_enabled,
                  max_sound_trigger_detection_service_ops_per_day,
                  sound_trigger_detection_service_op_timeout,
                  bixby_pregranted_permissions
settings system : key_now_bar_com_google_android_googlequicksearchbox,
                  key_now_bar_com_google_android_googlequicksearchbox_finance,
                  bixby_setting_show_app_icon_enabled
```

secure 쪽 키는 이름으로 보아 기본 비서와 음성 서비스를 가리키는 것으로 보이지만, 값의 형식과 어느 Android 버전부터 있는 키인지는 공식 문서를 열지 못해 확인하지 못했습니다. global·system 쪽 키의 뜻도 확인하지 못했습니다. 설정 값 전체는 [설정 값](../system-account/settings.md) 에서 다룹니다.

## 구조

파일은 프로토콜 버퍼(binarypb)이고, 인코딩 규칙은 [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 에 있습니다. ALEAPP 는 아래 필드만 읽습니다.

| 필드 번호 | 담긴 것 | ALEAPP 처리 |
|---|---|---|
| `3` | 세션 종류 | UTF-8 로 풀어 뜻풀이 없이 그대로 보여 줌 |
| `132269847` | 질의 글 | 바이너리에서 문자열 `com.google.android.apps.gsa.shared.search.Query` 를 찾아 그 뒤를 UTF-8 또는 UTF-16 으로 풂 |
| `132269388` | MP3 소리 데이터 | "Response" 칸의 미디어로 붙이고, 원본 파일 이름에서 확장자만 `.mp3` 로 바꿔 저장 |

세션 종류 필드에 어떤 값이 나오는지, 그 값으로 검색과 어시스턴트를 가를 수 있는지는 확인하지 못했습니다. ALEAPP 결과는 File Timestamp, Type, Queries, Response, Source File 칸으로 나옵니다.

## 증거로서 의미

### 증명하는 것

한 파일에서 질의 글이 나오면, 이 기기의 구글 앱에 그 질의가 담긴 세션 기록이 남아 있다는 뜻입니다. 소리 데이터가 나오면 그 세션에 MP3 소리가 함께 저장되어 있었다는 기록입니다. 계정 쪽 My Activity 기록은 웹 및 앱 활동이 켜져 있던 동안 그 계정으로 어시스턴트 활동이 저장됐다는 기록입니다.

### 증명하지 못하는 것

질의를 말로 했는지 글로 쳤는지, 어시스턴트였는지 검색 위젯이었는지는 세션 종류 값의 뜻을 확인하지 못해 이 파일만으로 가를 수 없습니다. MP3 소리가 사용자의 목소리인지 어시스턴트의 응답 음성인지도 출처에 적혀 있지 않고, ALEAPP 칸 이름이 Response 라는 점만 알 수 있습니다. 그래서 소리를 직접 들어 보기 전에는 "사용자가 말했다" 고 쓰지 않습니다. ALEAPP 가 보여 주는 시각은 질의한 시각이 아니라 파일 수정 시각이고, 누가 폰을 들고 질의했는지도 알 수 없습니다([그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)).

보고서에는 "이 시각에 이렇게 물었다" 가 아니라 "구글 앱 `app_session` 의 이 파일에 이 질의 글이 있고, 파일 수정 시각은 이렇다" 처럼 씁니다.

## 시각 해석

ALEAPP 의 File Timestamp 는 파일 안에 든 값이 아니라 파일의 수정 시각(`os.path.getmtime`)을 UTC 로 바꾼 값입니다. 그래서 수정 시각을 보존하지 않는 방법으로 파일을 꺼냈다면 이 시각은 추출한 때를 가리킬 수 있어 믿기 어렵습니다. 수집한 방법과 원본 파일 시스템의 시각을 함께 기록해 두고([모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md)), 파일 시스템의 시각 값 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 봅니다.

수정 시각은 파일을 마지막으로 쓴 때를 가리킬 뿐이라서, 한 파일 안에 질의가 여럿 있을 때 각 질의의 시각을 따로 알려 주지 않습니다. 파일 안에 시각 필드가 있는지는 ALEAPP 가 다루지 않아 확인하지 못했습니다.

## 함정과 한계

ALEAPP 는 `/mirror/` 경로를 건너뛰어서, 그 아래에 무엇이 있는지는 결과에 나오지 않습니다. 분석할 때는 `app_session` 아래 폴더를 직접 훑어 ALEAPP 가 읽지 않은 파일이 있는지 따로 봅니다.

ALEAPP 는 질의 글을 바이너리 안에서 클래스 이름 문자열로 찾아 그 뒤를 푸는 방식이라서, 구글 앱이 바뀌어 이 문자열이 없어지면 질의가 빈칸으로 나올 수 있습니다. ALEAPP 가 UTF-8 또는 UTF-16 으로 풀기 때문에, 직접 볼 때도 두 방식으로 모두 읽어 봅니다. 모듈을 2020-03-22 뒤로 고친 기록이 없고 삼성 기기 시험 자료도 없어서, 새 기기에서는 결과가 비어도 흔적이 없다고 단정하지 않습니다.

계정 쪽 기록은 사용자가 My Activity 에서 지울 수 있습니다. 자동 삭제 기간과 새 계정의 기본 설정, "음성 및 오디오 활동 포함" 의 기본값은 확인하지 못했습니다. 계정 쪽 자료를 어떻게 얻는지는 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 를 봅니다. 기기 쪽 파일을 지웠을 때 무엇이 남는지도 출처에 없어서, 지운 파일은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 방법으로 따로 찾아봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 문자 인코딩 규칙으로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다. 헥스 편집기에서 먼저 ASCII 문자열 `com.google.android.apps.gsa.shared.search.Query` 를 찾습니다. 앞부분 `com.google` 은 바이트로 아래와 같습니다.

```
63 6F 6D 2E 67 6F 6F 67 6C 65      "com.google"
```

이 문자열을 찾으면 그 뒤에서 질의 글을 찾습니다. 예를 들어 질의가 "날씨" 이고 UTF-8 로 적혔다면 아래 바이트가 보입니다.

```
EB 82 A0 EC 94 A8                  UTF-8 "날씨"
```

클래스 이름과 질의 글 사이에 어떤 바이트가 끼는지는 출처에 적혀 있지 않아서, UTF-8 로 읽히지 않으면 UTF-16 으로도 읽어 봅니다. 필드 '3' 과 필드 '132269388' 을 태그로 따라가는 방법은 [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 에 있습니다.

### 공개 도구로 한 번

1. 구글 앱 데이터 폴더의 `app_session` 폴더를 하위 폴더까지 통째로 복사하고, 원본 파일의 수정 시각을 함께 기록합니다.
2. ALEAPP 로 처리해 Google Quick Search Queries 결과의 Type, Queries, Response, Source File 칸을 봅니다.
3. Response 칸에 MP3 가 붙은 행은 소리를 직접 들어 사용자 목소리인지 응답 음성인지 확인하고, 확인한 내용만 보고서에 씁니다.
4. `/mirror/` 아래 파일은 ALEAPP 가 건너뛰니 헥스 편집기나 프로토콜 버퍼 풀이 도구로 따로 열어 봅니다.
5. File Timestamp 를 1단계에서 기록한 원본 수정 시각과 맞춰 봅니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [설정 값](../system-account/settings.md) | 기본 비서와 음성 서비스로 어떤 앱이 설정돼 있었는지 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 파일 수정 시각 무렵 구글 앱이 앞에 떠 있었는지 |
| [크롬](../browsers/chrome/index.md) | 같은 질의로 이어진 웹 검색·방문 기록 |
| [빅스비](../samsung/bixby.md) | 삼성 기기에서 다른 음성 비서를 쓴 흔적 |
| [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) | 계정의 My Activity 에 남은 어시스턴트 활동 |

여러 기록을 한 줄로 맞춰 보는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 과 [웹 사용 행위 재구성](../../04-scenarios/activity/web-activity.md) 을 봅니다.

## 실습

공개 검체 가운데 구글 앱이 깔린 Android 이미지를 골라 아래 질문을 풀어 봅니다.

1. `app_session` 아래 `.binarypb` 파일은 몇 개이고, `/mirror/` 아래에는 몇 개가 있습니까?
2. 각 파일에서 `com.google.android.apps.gsa.shared.search.Query` 문자열을 찾아 질의 글을 직접 풀고, ALEAPP 의 Queries 칸과 같은지 확인합니다.
3. 필드 '3' 의 세션 종류 값에는 어떤 것들이 나오고, 파일마다 어떻게 다릅니까?
4. MP3 가 나온 파일은 몇 개이고, 들어 보면 누구의 목소리입니까?
5. 파일 수정 시각을 앱 사용 기록의 구글 앱 사용 시각과 나란히 놓으면 서로 맞습니까?

## 참고 문헌

1. ALEAPP, scripts/artifacts/googleQuickSearchbox.py (GitHub main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/googleQuickSearchbox.py
2. Google Search Help, "Find & control your Web & App Activity" — https://support.google.com/websearch/answer/54068
