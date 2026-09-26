---
title: "엣지 패널"
parent: "아티팩트 · 삼성 기기 전용"
nav_order: 1160
---

# 엣지 패널 (Edge Panel)

엣지 패널은 화면 가장자리의 손잡이를 끌어 여는 삼성 전용 바로가기 패널이고, 기기 안 파일을 다룬 공개 포렌식 자료는 아직 없어서 알려진 흔적은 설정 값의 키 이름과 앱 사용 기록 정도입니다.

## 무엇을 기록하나 · 왜 생기나

엣지 패널에는 자주 쓰는 앱이나 연락처 같은 바로가기를 모아 두고, 사용자는 어느 화면에서든 가장자리를 끌어 패널을 엽니다. 어떤 패널을 켜 두었는지, 손잡이를 어디에 두었는지 같은 설정은 기기 설정 저장소에 남고, 패널에서 띄운 앱은 그 앱의 실행 흔적으로 남을 수 있습니다.

다만 엣지 패널 앱의 패키지 이름은 공식 자료에 나와 있지 않아 실제 기기의 설치된 앱 목록에서 확인합니다. 엣지 패널 앱의 데이터베이스와 파일 경로, 표 이름을 다룬 공개 포렌식 자료도 없고, 삼성 전용 흔적을 모은 목록에도 엣지 패널 항목은 없습니다[1].

## 위치와 버전별 차이

One UI 8.5 기기의 설정 값에서 이름에 `edge` 나 `cocktail` 이 들어간 키는 아래와 같습니다. adb 일반 권한으로도 키 이름은 읽힙니다. 키의 뜻은 공개 자료에 없어 시험 기기로 확인합니다.

| 영역 | 키 이름 |
|---|---|
| system | `cocktail_bar_enabled_cocktails`, `edge_handler_position_percent`, `edge_show_screen`, `active_edge_area` |
| secure | `edge_enable`, `edge_handle_size_percent`, `edge_handle_transparency`, `edge_lighting_recommend_app_list`, `game_edgescreen_touch_lock` |
| global | `edge_panel_height`, `edge_panel_width`, `edge_lighting_aod_brightness`, `edgelighting_custom_color`, `edgelighting_recently_used_color` |

`cocktail_bar_enabled_cocktails` 는 이름으로 보면 켜 둔 패널 목록일 가능성이 있습니다. `edge_handle_*`, `edge_handler_position_percent` 는 이름으로 짐작하면 손잡이의 크기·투명도·위치 설정이고, `edge_panel_height`, `edge_panel_width` 는 패널 크기로 보입니다.

system 영역에는 이 밖에 `edge_lighting` 으로 시작하는 키가 10개 있습니다.

```
edge_lighting, edge_lighting_basic_color_index, edge_lighting_color_type,
edge_lighting_custom_text_color, edge_lighting_duration,
edge_lighting_show_condition, edge_lighting_style_type_str,
edge_lighting_thickness, edge_lighting_transparency, edge_lighting_version
```

이 키들은 알림이 올 때 화면 가장자리를 빛나게 하는 "엣지 조명" 설정으로 보이고, 엣지 패널과는 다른 기능입니다. 두 기능이 키 이름으로 정확히 갈린다는 공개 자료가 없으므로, 보고서에서 `edge_` 로 시작하는 키를 모두 엣지 패널로 묶지 않습니다.

One UI 판에 따라 키 이름이나 저장 방식이 다를 수 있어 실제 기기에서 확인합니다. 설정 값을 읽는 법과 저장 위치는 [설정 값](../system-account/settings.md) 에서 다룹니다.

## 구조

엣지 패널 앱 파일의 구조를 다룬 공개 자료는 없습니다. 설정 값의 저장 형식은 [설정 값](../system-account/settings.md) 과 [안드로이드 바이너리 XML](../../01-foundations/data-formats/abx.md) 을 봅니다.

앱 사용 기록에는 엣지 패널과 관련 있을 수 있는 이벤트 종류가 보입니다. `dumpsys usagestats` 출력에는 `ACTIVITY_RESUMED`, `ACTIVITY_PAUSED`, `ACTIVITY_STOPPED` 와 함께 `shortcutId` 필드가 붙은 `SHORTCUT_INVOCATION` 이벤트가 있습니다. 엣지 패널에서 앱이나 바로가기를 띄운 일이 이 이벤트로 따로 구분되는지는 시험 기기로 확인합니다. 이벤트 종류의 뜻은 [앱 사용 기록](../app-usage/usagestats/index.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

전체 추출로 설정 값을 읽을 수 있다면 `cocktail_bar_enabled_cocktails` 같은 키의 값으로 기기의 엣지 패널 설정 상태를 적을 수 있습니다. 다만 키의 뜻이 공개 자료로 밝혀지지 않았으므로 "이 키에 이 값이 있다" 까지만 쓰고, "이 패널을 켜 두었다" 로 옮기려면 같은 One UI 판의 시험 기기로 먼저 확인합니다.

### 증명하지 못하는 것

설정 값은 수집한 때의 상태라서, 언제 그 설정을 바꿨는지와 패널을 몇 번 열었는지는 알 수 없습니다. 앱 사용 기록에 남은 실행 흔적으로도 그 앱이 엣지 패널에서 열렸는지, 홈 화면이나 알림에서 열렸는지는 구분할 수 없습니다. 엣지 패널에 바로가기로 둔 연락처가 곧 자주 연락한 사람이라는 식의 해석도 근거가 없습니다.

보고서에는 "엣지 패널로 이 앱을 열었다" 가 아니라 "수집 시점에 이 설정 키의 값은 이렇고, 이 시각에 이 앱의 실행 기록이 있다" 처럼 씁니다.

## 시각 해석

위 설정 키에는 시각 값이 없어서, 설정이 언제 바뀌었는지는 알 수 없습니다. 시각이 필요하면 앱 사용 기록의 이벤트 시각을 쓰고, 그 시각이 어느 시간대로 찍혔는지는 [시간대와 시각 설정](../system-account/time-zone.md) 으로 확인합니다.

## 함정과 한계

`edge_` 로 시작하는 키에는 엣지 패널과 엣지 조명이 섞여 있어서, 이름만 보고 한 기능으로 묶으면 잘못 해석하기 쉽습니다. 패키지 이름이 공식 자료에 나와 있지 않으므로, 검색 결과에 떠도는 패키지 이름을 그대로 보고서에 옮기지 않고 실제 기기의 설치된 앱 목록에서 직접 확인합니다.

엣지 패널을 다룬 공개 연구가 없어서, 분석 도구가 엣지 패널 결과를 내지 않는다고 흔적이 없다고 말할 수 없습니다. 위 키 목록은 One UI 8.5 기기 기준이라서 다른 판과 기종에서는 키가 다를 수 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

헥스로 따라갈 엣지 패널 파일은 공개 자료에 없습니다. 전체 추출본이 있다면 설치된 앱 목록에서 엣지 패널 앱을 찾고, 그 앱 데이터 폴더의 파일마다 첫 바이트를 보고 형식부터 구분합니다. 형식별로 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), [설정 XML과 SharedPreferences](../../01-foundations/data-formats/shared-preferences.md), [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 에 있습니다.

### 공개 도구로 한 번

키의 뜻을 확인하려면 시험 기기로 설정을 바꾸기 전과 뒤를 비교합니다.

1. 시험 기기에서 `adb shell settings list system`, `adb shell settings list secure`, `adb shell settings list global` 결과를 파일로 저장합니다.
2. 엣지 패널에서 패널 하나를 켜거나 끄고, 손잡이 위치를 옮깁니다.
3. 1번을 다시 실행해 두 결과를 비교하고, 값이 바뀐 키를 기록합니다.
4. 패널에서 앱 하나를 띄운 뒤 `adb shell dumpsys usagestats` 를 저장해, 그 시각 앞뒤에 어떤 이벤트 종류가 찍혔는지 봅니다.

이렇게 확인한 결과는 시험한 기종과 One UI 판을 붙여 기록합니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [설정 값](../system-account/settings.md) | 엣지 패널 관련 키의 값 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 패널에서 띄웠을 법한 앱의 실행 시각과 `SHORTCUT_INVOCATION` 이벤트 |
| [설치된 앱](../app-usage/packages/index.md) | 엣지 패널 앱의 패키지 이름과 판 |
| [최근 앱 화면](../app-usage/recents-snapshots.md) | 같은 시각에 앞에 떠 있던 앱 |

앱을 언제 썼는지 묻는 조사 흐름은 [어떤 앱을 언제 썼나](../../04-scenarios/activity/app-usage.md) 를 봅니다.

## 실습

공개된 시험 이미지 가운데 삼성 기기 이미지를 골라 아래 질문을 풀어 봅니다. 공개 이미지만으로 뜻을 확정하기 어려우면 시험 기기 비교와 함께 풉니다.

1. 설정 값에서 `cocktail` 이나 `edge` 가 들어간 키는 몇 개이고, 위 표에 없는 키가 있습니까?
2. `cocktail_bar_enabled_cocktails` 의 값은 어떤 모양입니까? 그 안에 패키지 이름이나 번호가 보입니까?
3. 엣지 조명으로 보이는 `edge_lighting*` 키와 나머지 키를 나눠 적어 봅니다.
4. 설치된 앱 목록에서 엣지 패널 앱으로 보이는 패키지를 찾고, 앱 데이터 폴더에 어떤 파일이 있는지 적습니다.

## 참고 문헌

1. Mattia Epifani, "Beyond the Known: A Call to Forensic Research on Samsung Android Artifacts" (2025-11-07) — https://blog.digital-forensics.it/2025/11/beyond-known-call-to-forensic-research.html
