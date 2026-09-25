---
title: "디지털 웰빙"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 490
---

# 디지털 웰빙 (Digital Wellbeing)

## 한 줄 요약

디지털 웰빙 (Digital Wellbeing) 앱은 앱이 화면에 올라오고 내려간 시각, 알림이 울린 시각, 잠금이 풀린 시각 같은 사용 이벤트를 자기 SQLite DB 에 적어 두고, 이 DB 를 읽으면 시스템의 앱 사용 기록(usagestats)과 같은 체계의 이벤트를 앱 데이터 쪽에서 한 번 더 볼 수 있습니다 [1].

## 무엇을 기록하나 · 왜 생기나

디지털 웰빙은 앱별 사용 시간을 보여 주는 Google 앱입니다. ALEAPP 가 읽는 이 앱의 DB 에는 이벤트마다 시각, 패키지, 이벤트 종류가 한 줄씩 들어 있고, 액티비티 이름까지 적는 별도 표도 있습니다 [1].

ALEAPP 가 이 DB 의 숫자에 붙이는 이벤트 이름 [1] 은 `dumpsys usagestats` 에 찍히는 `type=` 이름과 같은 체계이고, 관찰 기기의 `dumpsys usagestats` 에도 ACTIVITY_RESUMED·ACTIVITY_PAUSED·ACTIVITY_STOPPED, NOTIFICATION_INTERRUPTION, KEYGUARD_HIDDEN, FOREGROUND_SERVICE_START·FOREGROUND_SERVICE_STOP 이 보였습니다 (확인 범위: Android 16, One UI 8.5). 다만 디지털 웰빙이 usagestats 에서 이벤트를 받아 옮겨 적는다는 구조 설명은 공식 문서로 확인하지 못했습니다. 두 기록이 같은 출처에서 나왔는지는 검체마다 두 쪽 시각을 맞춰 보고 판단해야 합니다.

## 위치와 버전별 차이

Google 디지털 웰빙 앱의 DB 는 앱 데이터 영역에 있고, ALEAPP 는 아래 경로 패턴으로 찾습니다 [1].

```
*/com.google.android.apps.wellbeing/databases/app_usage*
```

앱 데이터 영역의 짜임새는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 페이지에서 다룹니다. 루팅되지 않은 기기에서 adb 일반 권한으로 이 DB 를 읽을 수 없다는 점은 앱 데이터 영역의 일반 원칙이고, 이 DB 에 대해 따로 확인하지는 않았습니다.

| 기기 | 기록하는 쪽 | 확인한 것 |
|---|---|---|
| Google 디지털 웰빙 앱이 깔린 기기 | `com.google.android.apps.wellbeing` | DB 경로 패턴과 표 구조(ALEAPP 기준) [1] |
| 삼성 One UI | 확인하지 못함 | 아래 관찰 내용만 있음 |

관찰 기기의 `dumpsys package` 출력에서 "Known Packages" 의 `Wellbeing:` 항목 값은 `none` 이었습니다. 시스템이 디지털 웰빙 역할로 지정한 패키지가 이 기기에는 없다는 뜻입니다 (확인 범위: Android 16, One UI 8.5). 같은 기기의 settings system 키 가운데 `add_info_com_samsung_android_forest#screenTime` 이라는 이름이 있었지만, 키 이름만 확인했고 값과 뜻은 모릅니다 (확인 범위: Android 16, One UI 8.5). 삼성 기기에서 화면 사용 시간 기능이 어떤 앱의 어떤 DB 에 기록하는지는 확인하지 못했으니, 삼성 검체에서는 Google 경로가 없다고 해서 사용 이벤트 기록이 없다고 결론 내리면 안 됩니다. 설정 키를 읽는 법은 [설정 값](../system-account/settings.md) 페이지에 있습니다.

DB 를 몇 날치 남기는지, 어느 Android 버전부터 이 앱이 있었는지는 확인하지 못했습니다.

## 구조

`app_usage` DB 에서 ALEAPP 가 읽는 표는 네 개입니다 [1]. SQLite 파일 형식 자체는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에서 다룹니다.

| 표 | 칸 | 담긴 것 |
|---|---|---|
| `events` | `timestamp`, `package_id`, `type` | 앱 단위 이벤트 한 건 |
| `packages` | `_id`, `package_name` | 패키지 번호와 이름 |
| `component_events` | `_id`, `timestamp`, `component_id`, `type` | 구성 요소(액티비티) 단위 이벤트 한 건 |
| `components` | `_id`, `package_id`, `component_name` | 구성 요소 번호와 이름, 소속 패키지 |

`events.package_id` 를 `packages._id` 와 이어야 패키지 이름이 나오고, `component_events.component_id` 는 `components._id` 로, 다시 `components.package_id` 는 `packages._id` 로 이어집니다 [1].

`type` 칸의 숫자를 ALEAPP 는 아래처럼 풉니다 [1]. 각 이벤트가 무슨 순간에 생기는지는 [앱 사용 기록 (usagestats)](usagestats/index.md) 페이지에서 설명합니다.

| type | 이름 |
|---|---|
| 1 | ACTIVITY_RESUMED |
| 2 | ACTIVITY_PAUSED |
| 12 | NOTIFICATION_INTERRUPTION |
| 18 | KEYGUARD_HIDDEN |
| 19 | FOREGROUND_SERVICE_START |
| 20 | FOREGROUND_SERVICE_STOP |
| 23 | ACTIVITY_STOPPED |
| 26 | DEVICE_SHUTDOWN |
| 27 | DEVICE_STARTUP |

ALEAPP 가 풀어 주는 숫자는 이 아홉 개이고, 표에 없는 숫자가 나오면 usagestats 번호 체계와 맞춰 보되 같은 뜻이라고 확인하기 전에는 보고서에 이름을 붙이지 않습니다.

## 증거로서 의미

**증명하는 것**

이 DB 에 ACTIVITY_RESUMED 줄이 있으면 그 시각에 해당 패키지의 화면이 앞으로 올라왔다고 기록돼 있다는 뜻이고, 이어지는 ACTIVITY_PAUSED·ACTIVITY_STOPPED 줄과 짝을 지으면 앱이 앞에 있던 시간대를 가늠할 수 있습니다. KEYGUARD_HIDDEN 은 잠금 화면이 걷힌 시각이고, DEVICE_STARTUP·DEVICE_SHUTDOWN 은 기기가 켜지고 꺼진 시각을 알려 줍니다. NOTIFICATION_INTERRUPTION 은 그 패키지의 알림이 사용자에게 울렸다는 기록입니다.

**증명하지 못하는 것**

화면이 앞에 올라왔다는 기록만으로 사람이 그 화면을 보거나 조작했다고 말할 수 없고, 누가 폰을 들고 있었는지도 알려 주지 않습니다. 알림 이벤트에는 알림 내용이 없어서 무슨 메시지가 왔는지는 [알림 기록 (Notification History)](notification-history.md) 같은 다른 기록에서 찾아야 합니다. 앱 안에서 무엇을 했는지(메시지를 보냈는지, 파일을 열었는지)는 이 DB 가 말하지 않습니다.

## 시각 해석

`timestamp` 는 유닉스 에포크 밀리초이고, ALEAPP 는 1000 으로 나눠 UTC 시각으로 바꿉니다 [1]. 현지 시각으로 옮길 때는 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 에서 기기 시간대를 먼저 확인합니다. 값을 읽는 일반 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

기기 시계를 사람이 바꾸면 그 뒤 이벤트의 벽시계 시각도 따라 바뀔 수 있습니다. 관찰 기기의 `dumpsys usagestats` 에는 `Time changed. actualSystemTime:... expectedSystemTime:...` 모양의 줄이 있어서 시스템 쪽에서는 시계 변경을 따로 적습니다 (확인 범위: Android 16, One UI 8.5). 디지털 웰빙 DB 가 시계 변경을 어떻게 처리하는지는 확인하지 못했으니, 시각 순서가 뒤집힌 구간이 보이면 usagestats 쪽 기록과 맞춰 봅니다.

## 함정과 한계

첫째, 이 페이지의 표 구조와 숫자 뜻은 ALEAPP 파서가 기대하는 모양이고, 앱 판마다 표가 바뀌었는지는 확인하지 못했습니다. 파서가 빈 결과를 내면 표 이름부터 직접 열어 봅니다.

둘째, 삼성 기기처럼 Google 디지털 웰빙이 없는 기기가 있습니다. 관찰 기기에서는 디지털 웰빙 역할 패키지가 `none` 이었습니다 (확인 범위: Android 16, One UI 8.5).

셋째, 보존 기간을 모르니 가장 오래된 줄의 날짜를 "사용 시작일" 로 읽으면 안 됩니다. 가장 오래된 줄은 "이 DB 에 남은 기록의 시작" 일 뿐입니다.

넷째, 사용자가 디지털 웰빙 앱 데이터를 지우거나 앱을 끄면 이 DB 가 비거나 없어질 수 있습니다. 이 경우에도 usagestats 같은 시스템 쪽 기록이 남아 있을 수 있어서, 두 쪽 기록량이 크게 다르면 그 차이 자체를 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md) 관점에서 살펴봅니다.

## 직접 분석해 보기

### SQL 로 한 번

DB 사본을 SQLite 도구로 열고 표 두 개를 이어서 읽습니다. 아래 질의는 위 구조 표로 만든 예시입니다.

```sql
SELECT e.timestamp,
       datetime(e.timestamp / 1000, 'unixepoch') AS utc_time,
       p.package_name,
       e.type
FROM events e
JOIN packages p ON e.package_id = p._id
ORDER BY e.timestamp;
```

구성 요소 단위로 보려면 `component_events` 를 `components` 와 잇고, 다시 `packages` 와 이어 패키지 이름을 붙입니다. 원본 DB 가 아니라 사본을 열고, 같은 폴더에 `-wal`·`-journal` 파일이 있으면 함께 복사합니다. 그 이유는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에서 설명합니다.

### 공개 도구로 한 번

ALEAPP 의 wellbeing 모듈이 위 경로를 찾아 이벤트 표를 만들어 줍니다 [1]. 도구 결과의 시각과 패키지 이름을 위 SQL 결과의 몇 줄과 맞춰 보면 도구가 숫자를 제대로 풀었는지 확인할 수 있습니다. 도구 결과를 검증하는 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 페이지에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [앱 사용 기록 (usagestats)](usagestats/index.md) | 같은 이름의 이벤트가 같은 시각에 있는지 |
| [알림 기록 (Notification History)](notification-history.md) | NOTIFICATION_INTERRUPTION 시각에 실제 알림 내용이 있는지 |
| [배터리 사용 기록 (batterystats)](batterystats.md) | `+screen` 화면 켜짐 구간과 이벤트 시각이 겹치는지 |
| [최근 앱 화면 (Recents·Snapshots)](recents-snapshots.md) | 마지막으로 앞에 올라온 앱과 최근 태스크 시각이 맞는지 |

여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md), 조사 흐름은 [어떤 앱을 언제 썼나 (App Usage)](../../04-scenarios/activity/app-usage.md) 와 [폰 사용 시간 재구성 (Usage Time)](../../04-scenarios/activity/usage-time.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 검체에 `com.google.android.apps.wellbeing` 폴더가 있으면 아래 질문을 풀어 봅니다.

1. `events` 표에서 가장 이른 시각과 가장 늦은 시각은 언제이고, 그 사이 며칠치가 남아 있습니까?
2. DEVICE_STARTUP 과 DEVICE_SHUTDOWN 줄로 기기가 켜져 있던 구간을 나누면 몇 구간이 나옵니까?
3. 한 앱을 골라 ACTIVITY_RESUMED 와 다음 ACTIVITY_PAUSED 를 짝지으면 그 앱이 앞에 있던 시간은 모두 얼마입니까?
4. 같은 검체에 usagestats 파일이 있으면, 같은 앱의 ACTIVITY_RESUMED 시각이 두 기록에서 일치합니까?

## 참고 문헌

1. ALEAPP — scripts/artifacts/wellbeing.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/wellbeing.py
