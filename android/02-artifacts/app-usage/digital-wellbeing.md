---
title: "디지털 웰빙"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 490
---

# 디지털 웰빙 (Digital Wellbeing)

디지털 웰빙 (Digital Wellbeing) 앱은 앱이 화면에 올라오고 내려간 시각, 알림이 울린 시각, 잠금이 풀린 시각 같은 사용 이벤트를 자기 SQLite DB 에 적어 두고, 이 DB 를 읽으면 시스템의 앱 사용 기록(usagestats)과 같은 체계의 이벤트를 앱 데이터 쪽에서 한 번 더 볼 수 있습니다 [1].

## 무엇을 기록하나 · 왜 생기나

디지털 웰빙은 앱별 사용 시간을 보여 주는 Google 앱입니다. 이 앱의 DB 에는 이벤트마다 시각, 패키지, 이벤트 종류가 한 줄씩 들어 있고, 액티비티 이름까지 적는 별도 표도 있습니다 [1].

이 DB 의 숫자가 뜻하는 이벤트 이름 [1] 은 `dumpsys usagestats` 에 찍히는 `type=` 이름과 같은 체계이고, `dumpsys usagestats` 에도 ACTIVITY_RESUMED·ACTIVITY_PAUSED·ACTIVITY_STOPPED, NOTIFICATION_INTERRUPTION, KEYGUARD_HIDDEN, FOREGROUND_SERVICE_START·FOREGROUND_SERVICE_STOP 이 나옵니다. 다만 디지털 웰빙이 usagestats 에서 이벤트를 받아 옮겨 적는다는 공식 설명은 없습니다. 두 기록이 같은 출처에서 나왔는지는 기기마다 두 쪽 시각을 맞춰 보고 판단해야 합니다.

## 위치와 버전별 차이

Google 디지털 웰빙 앱의 DB 는 앱 데이터 영역의 아래 경로 패턴에 있습니다 [1].

```
*/com.google.android.apps.wellbeing/databases/app_usage*
```

앱 데이터 영역의 짜임새는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 페이지에서 다룹니다. 앱 데이터 영역이라 루팅되지 않은 기기에서는 adb 일반 권한으로 이 DB 를 읽을 수 없습니다.

| 기기 | 기록하는 쪽 | 내용 |
|---|---|---|
| Google 디지털 웰빙 앱이 깔린 기기 | `com.google.android.apps.wellbeing` | DB 경로 패턴과 표 구조 [1] |
| 삼성 One UI | 실제 기기에서 확인 | 아래 설명 참고 |

삼성 기기에서는 `dumpsys package` 출력의 "Known Packages" 에서 `Wellbeing:` 항목 값이 `none` 으로 나올 수 있습니다. 시스템이 디지털 웰빙 역할로 지정한 패키지가 없다는 뜻입니다. settings system 키 가운데 `add_info_com_samsung_android_forest#screenTime` 이라는 키도 있는데, 이 키의 뜻은 정해져 있지 않으므로 보고서에는 값만 옮기고 뜻을 단정하지 않습니다. 삼성 기기에서는 화면 사용 시간 기능이 어떤 앱의 어떤 DB 에 기록하는지 실제 기기에서 확인해야 하고, Google 경로가 없다고 해서 사용 이벤트 기록이 없다고 결론 내리면 안 됩니다. 설정 키를 읽는 법은 [설정 값](../system-account/settings.md) 페이지에 있습니다.

DB 를 몇 날치 남기는지, 어느 Android 버전부터 이 앱이 있었는지는 실제 기기에서 확인해야 합니다.

## 구조

`app_usage` DB 에서 이벤트를 담은 표는 네 개입니다 [1]. SQLite 파일 형식 자체는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에서 다룹니다.

| 표 | 열 | 담긴 것 |
|---|---|---|
| `events` | `timestamp`, `package_id`, `type` | 앱 단위 이벤트 한 건 |
| `packages` | `_id`, `package_name` | 패키지 번호와 이름 |
| `component_events` | `_id`, `timestamp`, `component_id`, `type` | 구성 요소(액티비티) 단위 이벤트 한 건 |
| `components` | `_id`, `package_id`, `component_name` | 구성 요소 번호와 이름, 소속 패키지 |

`events.package_id` 를 `packages._id` 와 이어야 패키지 이름이 나오고, `component_events.component_id` 는 `components._id` 로, 다시 `components.package_id` 는 `packages._id` 로 이어집니다 [1].

`type` 열의 숫자는 아래 뜻입니다 [1]. 각 이벤트가 무슨 순간에 생기는지는 [앱 사용 기록 (usagestats)](usagestats/index.md) 페이지에서 설명합니다.

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

화면이 앞에 올라왔다는 기록만으로 사람이 그 화면을 보거나 조작했다고 말할 수 없고, 누가 폰을 들고 있었는지도 알려 주지 않습니다. 알림 이벤트에는 알림 내용이 없어서 무슨 메시지가 왔는지는 [알림 기록 (Notification History)](notification-history.md) 같은 다른 기록에서 찾아야 합니다. 앱 안에서 무엇을 했는지(메시지를 보냈는지, 파일을 열었는지)는 이 DB 에 나와 있지 않습니다.

## 시각 해석

`timestamp` 는 유닉스 에포크 밀리초라서 1000 으로 나누면 UTC 시각이 됩니다 [1]. 현지 시각으로 옮길 때는 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 에서 기기 시간대를 먼저 확인합니다. 값을 읽는 일반 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

기기 시계를 사람이 바꾸면 그 뒤 이벤트의 시스템 시계 시각도 따라 바뀔 수 있습니다. `dumpsys usagestats` 에는 `Time changed. actualSystemTime:... expectedSystemTime:...` 모양의 줄이 있어서 시스템 쪽에서는 시계 변경을 따로 적습니다. 디지털 웰빙 DB 에서 시각 순서가 뒤집힌 구간이 보이면 usagestats 쪽 기록과 맞춰 봅니다.

## 삼성 디지털 웰빙의 시간대 변경 기록

삼성 기기의 디지털 웰빙 앱(`com.samsung.android.forest`)은 공용 DB `dwbCommon.db` 의 `Logging` 표에 기기 시간대가 바뀐 때를 이전 시간대·새 시간대와 함께 한 줄씩 적습니다 [2][3]. 위에서 다룬 Google 앱의 `app_usage` DB 와는 다른 앱의 다른 DB 입니다. 시스템 속성과 설정 값에는 현재 시간대만 남아서 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md), 과거에 기기가 어느 시간대에 있었는지 찾을 때 이 표를 봅니다.

### 위치와 구조

DB 는 아래 경로에 있고, ALEAPP 는 `*/com.samsung.android.forest/databases/dwbCommon.db*` 패턴으로 이 파일을 찾습니다 [2][3]. ALEAPP 는 2026.3.0 판부터 이 기록을 읽고 [2], ALEAPP 시험 데이터 가운데 Android 10 갤럭시 S10 이미지와 Android 14 이미지에서 각각 한 줄씩 나옵니다 [3].

```
/data/data/com.samsung.android.forest/databases/dwbCommon.db
```

| 열 | 담긴 것 |
|---|---|
| `timeStamp` | 이 줄의 시각. 단위는 아래 시각 해석 참고 |
| `key` | 기록 종류. 시간대 변경 줄에는 `UsageDataManager::timeZoneChanged()` 가 들어 있습니다 |
| `Value` | 이전 시간대와 새 시간대 |

ALEAPP 는 `key` 에 `UsageDataManager::timeZoneChanged()` 가 들어 있는 줄만 `LIKE` 로 골라 읽습니다 [3]. `Value` 는 `, ` 로 나뉜 두 부분이고, 앞부분은 `prevTimezone( ` 으로, 뒷부분은 `newTimezone( ` 으로 시작합니다. ALEAPP 는 이 앞에 붙은 글자와 각 부분의 마지막 한 글자를 떼어 내고 남은 값을 이전 시간대(Previous Timezone)와 새 시간대(New Timezone)로 보여 줍니다 [3]. 시간대가 `Asia/Seoul` 같은 시간대 ID 로 적히는지, UTC 와의 차이로 적히는지는 실제 `Value` 를 열어 확인하고, 파서가 떼어 낸 결과가 원래 값과 맞는지도 함께 봅니다. `Logging` 표에는 다른 `key` 의 줄도 들어 있어서 `SELECT DISTINCT key FROM Logging` 으로 어떤 기록이 함께 있는지 먼저 봅니다.

### 시각 해석

`timeStamp` 는 유닉스 에포크 기준 값이고, ALEAPP 는 단위를 정해 두지 않고 값의 크기로 판단해 UTC 로 바꿉니다 [3][4]. 값이 10^10 이상이면 밀리초, 10^13 이상이면 마이크로초, 10^16 이상이면 나노초로 읽으므로 [4], 직접 읽을 때도 자릿수부터 확인합니다. 2001-09-09 부터 2286년 사이의 날짜를 밀리초로 적으면 13자리입니다.

변경 줄을 시각순으로 늘어놓으면 기기 시간대가 어느 구간에 어떤 값이었는지 나옵니다. 현지 시각 문자열로 적힌 다른 기록(logcat 등)은 확보 시점의 시간대가 아니라 그 기록의 시각이 속한 구간의 시간대로 UTC 로 바꿉니다. 첫 변경 줄보다 이른 구간은 그 줄의 이전 시간대로 볼 수 있지만, 이 표에 남은 가장 오래된 줄 앞에 다른 변경이 있었는지는 이 표만으로 알 수 없습니다.

시간대 변경은 시계(유닉스 시각) 자체를 바꾸는 일과 다른 사건입니다. 위의 usagestats `Time changed` 줄이나 [시각 바꾸기 (Time Change)](../../04-scenarios/activity/anti-forensics/time-change.md) 에서 다루는 시계 변경 흔적과 섞어 읽지 않습니다.

### 증거로서 의미

**증명하는 것**

그 시각에 디지털 웰빙 앱이 기기 시간대가 이전 값에서 새 값으로 바뀌었다고 적었다는 사실입니다. 새 시간대가 다른 나라나 지역의 시간대라면 그 무렵 기기가 다른 시간대로 옮겨 갔을 수 있다는 보조 단서가 되고, 위치 기록이 없을 때 출입국·이동 시점을 좁히는 데 씁니다. 이동 여부의 결론은 [그 시각에 어디 있었나 (Location)](../../04-scenarios/activity/location.md) 의 위치 기록과 함께 냅니다.

**증명하지 못하는 것**

사용자가 설정에서 시간대를 직접 바꿨는지, 자동 시간대 기능이 통신망이나 위치로 바꿨는지는 이 줄에 나와 있지 않습니다. 확보 시점의 `auto_time_zone` 값은 그때의 설정일 뿐이라 변경 당시 상태를 알려 주지 않습니다. 그래서 이 줄 하나로 기기가 실제로 그 지역에 있었다고 말할 수 없고, 사람이 일부러 시간대를 바꿨다고 말할 수도 없습니다. 같은 시간대를 쓰는 여러 나라 가운데 어디였는지도 나오지 않고, 변경 줄의 시각을 국경을 넘거나 비행기에서 내린 순간과 같다고 볼 근거도 없습니다. 변경 줄이 없다고 해서 이동이 없었다고 말할 수도 없습니다. 이 표를 며칠치 남기는지는 실제 기기에서 확인해야 하고, 앱 데이터를 지우면 함께 사라질 수 있습니다.

보고서에는 "`dwbCommon.db` 의 `Logging` 표에 2026-08-10 01:23:45 UTC 에 기기 시간대가 A 에서 B 로 바뀌었다는 기록이 있다(만든 예시)" 처럼 기록으로 확인되는 만큼만 씁니다.

### 직접 분석해 보기

DB 사본을 열고 `PRAGMA table_info(Logging)` 으로 열 이름을 먼저 확인합니다. 아래 질의는 `timeStamp` 가 13자리 밀리초일 때의 예시입니다.

```sql
SELECT timeStamp,
       datetime(timeStamp / 1000, 'unixepoch') AS utc_time,
       key,
       Value
FROM Logging
WHERE key LIKE '%UsageDataManager::timeZoneChanged()%'
ORDER BY timeStamp;
```

ALEAPP 의 `samsung_wellbeing_timezone` 모듈은 같은 줄을 읽어 Timestamp·Previous Timezone·New Timezone 세 열로 보여 줍니다 [3]. 도구 결과를 위 SQL 결과의 `Value` 원문과 맞춰 보면 파서가 시간대 값을 제대로 떼어 냈는지 확인할 수 있습니다.

## 함정과 한계

첫째, 이 페이지의 표 구조와 숫자 뜻은 ALEAPP 파서가 기대하는 모양이고, 앱 판에 따라 표가 바뀌었을 수 있습니다. 파서가 빈 결과를 내면 표 이름부터 직접 열어 봅니다.

둘째, 삼성 기기처럼 Google 디지털 웰빙이 없는 기기가 있습니다. 이런 기기에서는 디지털 웰빙 역할 패키지가 `none` 으로 나옵니다.

셋째, 가장 오래된 줄의 날짜를 "사용 시작일" 로 읽으면 안 됩니다. 가장 오래된 줄은 "이 DB 에 남은 기록의 시작" 일 뿐입니다.

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

NIST CFReDS 같은 공개 안드로이드 시험 데이터에 `com.google.android.apps.wellbeing` 폴더가 있으면 아래 질문을 풀어 봅니다.

1. `events` 표에서 가장 이른 시각과 가장 늦은 시각은 언제이고, 그 사이 며칠치가 남아 있습니까?
2. DEVICE_STARTUP 과 DEVICE_SHUTDOWN 줄로 기기가 켜져 있던 구간을 나누면 몇 구간이 나옵니까?
3. 한 앱을 골라 ACTIVITY_RESUMED 와 다음 ACTIVITY_PAUSED 를 짝지으면 그 앱이 앞에 있던 시간은 모두 얼마입니까?
4. 같은 데이터에 usagestats 파일이 있으면, 같은 앱의 ACTIVITY_RESUMED 시각이 두 기록에서 일치합니까?

## 참고 문헌

1. ALEAPP — scripts/artifacts/wellbeing.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/wellbeing.py
2. Kevin Pagano, "Tracking Timezone Changes in Digital Wellbeing" — https://www.stark4n6.com/2026/08/tracking-timezone-changes-in-digital.html
3. ALEAPP — scripts/artifacts/swellbeing.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/swellbeing.py
4. ALEAPP — scripts/ilapfuncs.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/ilapfuncs.py
