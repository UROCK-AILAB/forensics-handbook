---
title: "시각 값"
parent: "기반 · 값 읽는 법"
nav_order: 240
---

# 시각 값 (Unix 밀리초·Chrome 시각·기타)

## 한 줄 요약

Android 기기의 시각 값은 1970년 기준 Unix 시각, 1601년 기준 Chrome 시각, 16진수로 적은 정수, dumpsys 가 사람이 읽도록 바꾼 문자열처럼 여러 모양으로 남습니다. 값마다 기준점(epoch)과 단위, 시간대를 먼저 가려내야 제대로 읽을 수 있습니다.

## 이 형식을 쓰는 아티팩트

| 값의 모양 | 보이는 곳 | 자세히 |
|---|---|---|
| Unix 시각(초·밀리초·마이크로초 정수) | 앱 SQLite 데이터베이스 | [SQLite 데이터베이스](../data-formats/sqlite/index.md), [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md) |
| Chrome 시각(1601년 기준 마이크로초) | Chromium 계열 브라우저 | [크롬](../../02-artifacts/browsers/chrome/index.md) |
| 16진수 긴 정수 | 사용자별 `package-restrictions.xml` 의 첫 설치 시각 | [설치된 앱](../../02-artifacts/app-usage/packages/index.md) |
| 사람이 읽는 날짜 문자열 | dumpsys usagestats·notification·account | [dumpsys 출력](../../02-artifacts/logs/dumpsys.md) |
| 연도 없는 "월-일 시:분:초.밀리초" | dumpsys batterystats·wifi·bluetooth_manager, logcat | [배터리 사용 기록](../../02-artifacts/app-usage/batterystats.md), [logcat](../../02-artifacts/logs/logcat.md) |
| 이름으로만 시각을 알 수 있는 설정 값 | settings global·secure·system | [설정 값](../../02-artifacts/system-account/settings.md) |

앱 SQLite 데이터베이스가 열마다 어떤 단위를 쓰는지는 앱과 버전마다 달라서 이 페이지에서 일반 규칙으로 정하지 않습니다. 삼성 기본 앱도 각 앱 페이지에서 열마다 따로 확인합니다.

## 구조

### Unix 시각과 Chrome 시각

Unix 시각은 1970-01-01 00:00:00 UTC 부터 흐른 시간을 세고, 초·밀리초·마이크로초 가운데 무엇으로 세는지는 기록하는 쪽이 정합니다. Chromium 의 `base::Time` 은 UTC 를 기준으로 1601-01-01 00:00:00 UTC(Windows epoch)부터 흐른 마이크로초로 시각을 나타냅니다. Chromium 소스에는 두 기준점 사이의 차이를 마이크로초로 적은 상수 `kMicrosecondsFromWindowsToUnixEpoch = 11644473600000000` 이 있고, 저장용으로 값을 바꿀 때는 `FromDeltaSinceWindowsEpoch()` 와 `ToDeltaSinceWindowsEpoch()` 를 씁니다[2]. 이 상수에서 바로 다음 식이 나옵니다.

```
Unix 초 = (Chrome 값 − 11644473600000000) ÷ 1,000,000
```

크롬 데이터베이스의 어느 열이 이 형식인지는 [크롬](../../02-artifacts/browsers/chrome/index.md) 페이지에서 다룹니다.

값만 보고 단위를 짐작할 때는 자릿수가 가장 빠른 단서입니다. 아래 표는 2001년 9월부터 2286년 11월 사이의 시각을 기준으로 셈한 결과이고, 명세에서 나오는 산술입니다. 이 기간을 벗어나면 Unix 시각의 자릿수가 하나 줄거나 늘어납니다.

| 형식 | 기준점 | 단위 | 자릿수 | 2025-01-01 00:00:00 UTC 값 |
|---|---|---|---|---|
| Unix 초 | 1970-01-01 UTC | 초 | 10 | 1735689600 |
| Unix 밀리초 | 1970-01-01 UTC | 밀리초 | 13 | 1735689600000 |
| Unix 마이크로초 | 1970-01-01 UTC | 마이크로초 | 16 | 1735689600000000 |
| Chrome 시각 | 1601-01-01 UTC | 마이크로초 | 17 | 13380163200000000 |

### 16진수로 적은 첫 설치 시각

Android 패키지 관리자는 첫 설치 시각을 `first-install-time` 속성(`ATTR_FIRST_INSTALL_TIME`)에 두고, 사용자별 `package-restrictions.xml` 을 읽을 때 이 속성을 `getAttributeLongHex` 로 읽습니다[1]. 그래서 이 파일의 첫 설치 시각은 10진수가 아니라 16진수 긴 정수로 적혀 있고, 사용자마다 값이 따로 있습니다. 앱이 보는 `PackageInfo.firstInstallTime` 은 `System.currentTimeMillis()` 와 같은 단위, 곧 Unix 밀리초입니다[3]. 파일에 적힌 값도 같은 값이라 밀리초일 가능성이 높습니다. 현재 AOSP 는 이 파일들을 `TypedXmlSerializer`·`TypedXmlPullParser` 로 읽고 쓰기 때문에 일반 텍스트 XML 이 아닌 [안드로이드 바이너리 XML](../data-formats/abx.md)일 수 있습니다[1]. 파일 위치와 나머지 필드는 [설치된 앱](../../02-artifacts/app-usage/packages/index.md)에서 다룹니다.

### dumpsys 와 logcat 이 보여 주는 문자열

dumpsys 와 logcat 은 저장된 숫자를 그대로 내보이지 않고 사람이 읽는 문자열로 바꿔 찍는 경우가 많고, 서비스마다 모양이 다릅니다. 서비스별 출력 모양은 아래와 같습니다.

| 출력 | 필드 이름·줄 | 값의 모양 |
|---|---|---|
| dumpsys usagestats 이벤트 | `time="…" type=… package=…` | 숫자가 아닌 날짜 문자열이고 한글이 섞여 있음 |
| dumpsys usagestats 일별 통계 | `totalTimeUsed`, `lastTimeUsed`, `totalTimeVisible`, `lastTimeVisible`, `lastTimeComponentUsed`, `totalTimeFS` | 따옴표로 감싼 문자열 |
| dumpsys usagestats 끝부분 | `mDumpInitLastTimeSaved`, `mDumpInitEndTime` | 따옴표로 감싼 문자열 |
| dumpsys notification | `mRankingTimeMs`, `mCreationTimeMs`, `mVisibleSinceMs`, `mUpdateTimeMs` | `값(날짜 ##:##:##.###+####)` — 괄호 안에 지역 시각과 시간대 오프셋 |
| dumpsys notification | `when=값/값`, stats 줄의 `posttimeToFirstClickMs`, `posttimeToDismissMs`, `airtimeMs`, `currentAirtimeStartElapsedMs` | 이름이 Ms 로 끝나는 필드, 일부는 `-#` 처럼 음수 |
| dumpsys account "Accounts History" | `AccountId, Action_Type, timestamp, UID, TableName, Key` | `timestamp` 는 `날짜:##:##` 모양 문자열 |
| dumpsys user | `Created`, `Last logged in`, `Start time`, `Unlock time`, `Last entered foreground` | 주 사용자의 `Created` 는 `<unknown>` |
| dumpsys batterystats 기록, dumpsys wifi `rec[#]: time=`, dumpsys bluetooth_manager "Enable log", logcat | 줄 맨 앞 | `##-## ##:##:##.###` — 연도와 시간대 표시가 없음 |
| dumpsys batterystats 기록 첫 줄 | `RESET:TIME:` | 기록의 기준 시각 |

설정 값 가운데 이름으로 시각임을 드러내는 키도 있습니다. 값의 단위는 키마다 실제 기기에서 확인합니다.

| 설정 공간 | 키 |
|---|---|
| global | `auto_time`, `auto_time_zone`, `auto_time_zone_explicit`, `boot_count`, `network_watchlist_last_report_time`, `dbsc_consent_*_agree_date`, `sleep_charging_finish_time` |
| secure | `biometrics_strong_enroll_timestamp`, `ppp_enroll_timestamp`, `zen_duration_end_time` |
| system | `TIME_DIFFERENCE`, `sat_big_data_weekly_update_last_update_time_in_milli_seconds`, `llm_model_loaded_timestamp`, `llm_running_timestamp` |

## 읽는 법

1. 값의 모양을 봅니다. 10진수 정수라면 자릿수로 단위 후보를 고르고, 16진수라면 먼저 10진수로 바꿉니다.
2. 기준점을 정합니다. 17자리 마이크로초라면 Chrome 시각일 가능성이 높고, 13자리라면 Unix 밀리초 후보입니다. 같은 열의 다른 행이나 같은 앱의 다른 열과 비교해서 한 가지로 좁힙니다.
3. UTC 로 바꿉니다. Unix 시각과 Chrome 시각은 둘 다 UTC 기준이라, 바꾼 결과에 기기 시간대를 더해야 현지 시각이 됩니다. 기기 시간대는 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md)에서 확인합니다.
4. 문자열이라면 시간대 표시가 있는지 봅니다. dumpsys notification 처럼 `+####` 오프셋이 붙어 있으면 그 오프셋을 빼서 UTC 로 맞추고, 오프셋이 없으면 기기 시간대를 따로 확인하기 전에는 UTC 로 가정하지 않습니다.
5. 연도가 없는 줄은 연도를 채워 넣어야 합니다. batterystats 는 기록 첫 줄의 `RESET:TIME:` 을 먼저 보고, 수집한 시각과 함께 놓고 연도를 정합니다. 연말과 연초에 걸친 기록이라면 월이 거꾸로 넘어가는 지점에서 연도가 바뀝니다.

### 헥스로 한 번 따라가기

아래 바이트는 실제 데이터가 아니라 명세로 만든 예시이고, 2025-01-01 00:00:00 UTC 를 두 형식으로 적은 값입니다. SQLite 레코드 안의 정수는 빅엔디언으로 저장돼서 헥스 편집기에서는 이 순서로 보입니다. 다만 SQLite 는 값에 맞는 가장 짧은 너비를 골라 저장하기 때문에, 아래 Unix 밀리초 값은 앞의 `00 00` 없이 6바이트(`01 94 1F 29 7C 00`)로 나올 수 있습니다. 저장 너비가 몇 바이트로 정해지는지는 [SQLite 데이터베이스](../data-formats/sqlite/index.md)에서 다룹니다.

```
Chrome 시각 13380163200000000
  8바이트 빅엔디언   00 2F 89 30 02 92 A0 00
  (13380163200000000 − 11644473600000000) ÷ 1000000 = 1735689600 → 2025-01-01 00:00:00 UTC

Unix 밀리초 1735689600000
  8바이트 빅엔디언   00 00 01 94 1F 29 7C 00
  1735689600000 ÷ 1000 = 1735689600 → 2025-01-01 00:00:00 UTC

16진수 문자열로 적는다면
  1735689600000 = 0x1941F297C00
```

마지막 줄은 16진수 긴 정수를 읽는 연습용입니다. `first-install-time` 값을 바꿀 때는 13자리 밀리초로 가정하고 셈한 뒤, 결과가 다른 설치 기록과 맞는지로 단위를 확인합니다.

### SQL 과 Python 으로 바꾸기

```sql
-- Unix 밀리초 칸
SELECT datetime(ts_col / 1000, 'unixepoch') FROM t;
-- Chrome 시각 칸
SELECT datetime(ts_col / 1000000 - 11644473600, 'unixepoch') FROM t;
```

```python
from datetime import datetime, timezone
ms = 1735689600000
print(datetime.fromtimestamp(ms / 1000, timezone.utc))
chrome = 13380163200000000
print(datetime.fromtimestamp((chrome - 11644473600000000) / 1_000_000, timezone.utc))
```

`ts_col` 과 `t` 는 자리를 채운 이름이라 실제 열 이름과 표 이름으로 바꿔 씁니다. SQLite 의 `datetime()` 은 결과를 UTC 로 돌려줍니다.

## 포렌식에서 중요한 점

시각을 사람이 바꿨는지는 시각 값 하나만으로는 알 수 없고, 시스템이 시각 변경을 따로 적어 둔 곳을 찾아야 합니다. One UI 기기의 dumpsys usagestats 에는 "UsageStats RollOver history" 절이 있고, 그 안에 `Time changed. actualSystemTime:… expectedSystemTime:… actualRealtime:…` 줄과 `rolloverStats by event Type … realTime:… systemTime:…` 줄이 있습니다. 이름으로 보면 시스템 시각이 예상과 달라진 순간을 적는 줄이라 시각 조작을 의심할 때 먼저 봅니다. 다만 이 절이 AOSP 공통인지 삼성이 덧붙인 것인지, `realTime` 과 `systemTime` 의 정확한 정의가 무엇인지는 실제 기기에서 확인해야 합니다. 시각 조작을 다루는 흐름은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md)에 있습니다.

자동 시각과 자동 시간대가 켜져 있었는지는 settings global 의 `auto_time`, `auto_time_zone`, `auto_time_zone_explicit` 키로 확인합니다. 값의 뜻은 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md)에서 다룹니다. settings system 의 `TIME_DIFFERENCE` 키도 이름만 보면 시각과 관련 있어 보이지만, 뜻과 단위는 실제 값으로 확인해야 합니다.

dumpsys 와 logcat 출력은 수집하는 순간의 메모리 상태와 버퍼 내용이라, 오래된 기록은 이미 밀려나 있을 수 있습니다. 연도 없는 줄을 여러 번 수집해서 이어 붙일 때는 앞 수집과 뒤 수집이 겹치는 줄을 기준으로 맞추고, 연도를 추정했다면 추정한 사실을 보고서에 적습니다.

## 함정

단위를 잘못 고르면 결과가 크게 틀어집니다. Unix 밀리초를 초로 읽으면 수만 년 뒤의 날짜가 나오고, Chrome 시각을 1970년 기준 마이크로초로 읽으면 약 369년 뒤로 밀린 날짜가 나옵니다. 날짜가 그럴듯해 보여도 같은 열의 다른 값과 함께 바꿔 보고, 다른 기록과 앞뒤가 맞는지 확인합니다.

이름이 `Ms` 나 `time` 으로 끝난다고 모두 한 시점을 뜻하지는 않습니다. dumpsys notification 의 `airtimeMs` 같은 필드는 이름만 보면 길이를 잴 가능성이 있고, `posttimeToFirstClickMs=-#` 처럼 음수가 찍히는 필드도 있습니다. 이런 필드를 시각으로 바꾸기 전에 원 코드나 문서로 뜻을 확인합니다.

문자열로 바뀐 시각은 기기가 지역 설정에 맞춰 서식을 고른 결과라서 한글이 섞이고, 날짜 순서도 지역 설정에 따라 바뀔 수 있습니다. usagestats 시각 문자열에도 한글이 섞여 나오고, 정확한 서식은 실제 기기에서 확인합니다. 도구가 이런 문자열을 자동으로 읽을 때는 월과 일을 바꿔 읽지 않았는지 한두 줄을 손으로 대조합니다.

설정 키의 이름에 `milli_seconds` 가 들어 있어도 그 이름만으로 단위를 확정하지 않습니다. 이름과 저장 값이 어긋나는 경우가 없는지 실제 값의 자릿수로 한 번 더 봅니다.

## 도구

- sqlite3 명령줄: `datetime()`·`strftime()` 으로 열 전체를 한 번에 바꿉니다.
- Python `datetime`: 단위와 기준점을 직접 적어 바꾸는 방식이라 계산 과정을 보고서에 그대로 남길 수 있습니다.
- CyberChef 같은 공개 변환 도구: 값 한두 개를 빠르게 확인할 때 씁니다. 도구마다 기본 단위가 달라서 초인지 밀리초인지 설정을 먼저 봅니다.

바꾼 결과는 도구 하나에 맡기지 않고, 위 헥스 예시처럼 손으로 한 번 계산한 값과 맞춰 봅니다. 도구를 검증하는 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md)에 있고, 여러 기록의 시각을 한 줄로 모으는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md)에 있습니다.

## 참고 문헌

1. AOSP platform/frameworks/base — services/core/java/com/android/server/pm/Settings.java — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/Settings.java
2. Chromium — base/time/time.h — https://raw.githubusercontent.com/chromium/chromium/main/base/time/time.h
3. AOSP platform/frameworks/base — core/java/android/content/pm/PackageInfo.java (firstInstallTime·lastUpdateTime 주석) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/content/pm/PackageInfo.java
