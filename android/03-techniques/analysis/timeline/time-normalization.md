---
title: "시각 정규화"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 1420
---

# 시각 정규화 (Time Normalization)

## 한 줄 요약

기록마다 다른 시계·단위·기준점·시간대로 적힌 시각을 한 기준(보통 UTC)으로 옮기고, 옮기기 전의 값과 표기를 옆에 그대로 남겨 두는 작업입니다.

## 언제 쓰나

여러 기록을 한 시간 축에 올리기 전에 먼저 합니다. Android 기록에는 유닉스 밀리초 정수, 연도가 빠진 "월-일 시:분:초" 문자열, 시간대 오프셋이 붙은 문자열, 한글이 섞인 현지 형식 문자열이 함께 나오고, 부팅한 뒤 흐른 시간을 세는 값도 있습니다. 이 차이를 맞추지 않고 정렬하면 순서와 간격이 틀어집니다.

이 페이지는 값 하나하나를 같은 기준으로 옮기는 데까지만 다룹니다. 옮긴 기록을 서로 맞물리는 방법은 [여러 기록 엮기](correlation.md), 벽시계가 바뀐 흔적을 찾는 방법은 [시각 조작 흔적](time-manipulation.md) 에 있고, 밀리초·Chrome 시각 같은 개별 값의 변환 공식은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다. 소스로 확인한 동작은 현행 AOSP 기준(frameworks/base 의 main 가지)이고, 실제 폰에서 본 내용에는 확인 범위를 붙였습니다.

## Android 의 시계 종류

Android 에는 성격이 다른 시계가 여럿 있고, 기록이 어느 시계로 적혔는지에 따라 정규화 방법이 달라집니다 [1].

| 시계 | 기준과 단위 | 성질 |
|---|---|---|
| `System.currentTimeMillis()` — 벽시계 (wall clock) | 유닉스 에포크(1970-01-01 UTC)부터 밀리초 | 사용자나 통신망이 바꿀 수 있어서 앞뒤로 갑자기 뛸 수 있음 |
| `SystemClock.uptimeMillis()` | 부팅부터 밀리초 | 깊은 절전 (deep sleep) 중에는 멈추고, 단조 증가 (monotonic) |
| `SystemClock.elapsedRealtime()` · `elapsedRealtimeNanos()` | 부팅부터 밀리초 · 나노초 | 깊은 절전 시간까지 세고, 단조 증가 |
| `SystemClock.currentNetworkTimeClock()` | 네트워크 시간으로 맞춘 시계 | 사용자가 바꿀 수 없지만 네트워크 지연·서버 차이·기기 쪽 흔들림 때문에 값의 순서가 뒤바뀔 수 있고, 쓸 수 없으면 `DateTimeException` |
| `SystemClock.currentGnssTimeClock()` | 위치 제공자(GNSS)로 맞춘 시계 | 부팅 뒤 위치를 한 번도 잡지 못했으면 `DateTimeException` |

마지막 두 메서드가 어느 API 수준부터 들어갔는지는 확인하지 못했습니다. 벽시계 기록은 사용자가 바꾼 시각을 그대로 따르고, 부팅 기준 기록은 부팅할 때마다 0부터 다시 셉니다 [1]. 그래서 정규화는 기록마다 어느 시계를 썼는지 가리는 데서 시작합니다. 예를 들어 앱 사용 기록의 이벤트 시각은 벽시계와 같은 유닉스 밀리초이고, 자세한 내용은 [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) 페이지에 있습니다.

## 절차

1. **수집할 때 기준 정보를 적어 둡니다.** 수집한 시각(UTC)과 기기의 시간대, 자동 시각·자동 시간대 설정 값을 함께 기록합니다. 관찰한 폰에서는 `settings global` 에 `auto_time`, `auto_time_zone`, `auto_time_zone_explicit`, `boot_count` 키가 있었고, `settings system` 에 `TIME_DIFFERENCE`, `homecity_timezone` 키가 있었습니다 (확인 범위: Android 16, One UI 8.5). 이 페이지의 출처로는 각 키의 뜻을 확인하지 못했고, 설정 값을 읽는 법은 [설정 값](../../../02-artifacts/system-account/settings.md), 시간대 설정의 의미는 [시간대와 시각 설정](../../../02-artifacts/system-account/time-zone.md) 페이지를 봅니다.
2. **기록마다 시계와 단위를 가립니다.** 칸 이름이나 명세로 벽시계인지 부팅 기준인지, 초·밀리초·마이크로초·나노초 중 무엇인지 확인합니다. 부팅 기준 값은 그 자체로는 날짜로 바꿀 수 없고, 같은 부팅 안에서 벽시계와 짝을 이룬 기록이 있어야 옮길 수 있습니다. 그 짝을 찾는 방법은 [여러 기록 엮기](correlation.md) 에 있습니다.
3. **기준점 (epoch) 을 맞춥니다.** 유닉스 에포크(1970년) 말고도 기준점이 다른 시각 값이 있습니다. 978307200 초는 1970-01-01 부터 2001-01-01 까지의 초이고, 11644473600 초는 1601년 기준 WebKit 시각을 유닉스 시각으로 옮길 때 쓰는 상수라서 두 값을 혼동하면 결과가 수백 년 어긋납니다. 기준점별 공식은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.
4. **시간대를 가립니다.** 문자열에 `+0900` 같은 오프셋이 붙어 있으면 그 오프셋으로 옮기고, 오프셋이 없으면 어느 시간대 기준인지 따로 확인합니다. 사용자가 시각을 손으로 넣을 때는 현지 시각으로 넣고, 시스템은 그때의 시간대로 유닉스 에포크 시각을 계산합니다 [2].
5. **연도가 빠진 표기에 표시를 해 둡니다.** 연도를 채우는 방법은 다른 기록과 맞춰 봐야 해서 [여러 기록 엮기](correlation.md) 단계에서 다룹니다.
6. **UTC 로 옮기고 원래 값을 옆 칸에 남깁니다.** 원래 값, 원래 표기, 시계 종류, 옮긴 방법을 한 줄에 함께 적어 두면 나중에 다른 시간대로 다시 보이거나 변환을 검토할 때 되짚을 수 있습니다. 공개 도구 ALEAPP 도 결과를 UTC 로 맞춘 뒤 필요하면 지정한 시간대로 바꿔 보여 줍니다 [4].

## 기록별 시각 표기

### logcat

logcat 의 기본 출력 형식은 threadtime 이고, 날짜·호출 시각·우선순위·태그·PID·TID 를 한 줄에 찍습니다 [3]. 관찰한 폰에서 기본 형식 줄은 main·system·events·crash·radio 버퍼 모두 아래 모양이었고 연도와 시간대가 없었습니다 (확인 범위: Android 16, One UI 8.5).

```
##-## ##:##:##.### <PID> <TID> I <태그>: <내용>
```

기본 형식으로 뽑은 logcat 은 뽑은 시점의 연도와 기기 시간대를 따로 적어 두어야 정규화할 수 있습니다. 뽑을 때 `-v` 뒤에 아래 형식 수식어를 붙이면 필요한 정보를 줄마다 찍을 수 있습니다(예: `adb logcat -v epoch`) [3]. logcat 기록 자체의 해석은 [logcat](../../../02-artifacts/logs/logcat.md) 페이지에 있습니다.

| 수식어 | 찍는 것 |
|---|---|
| `epoch` | 1970-01-01 부터 흐른 초 |
| `monotonic` | 마지막 부팅 이후 CPU 초 |
| `usec` | 마이크로초 정밀도 |
| `UTC` | UTC 로 표시 |
| `year` | 연도 추가 |
| `zone` | 현지 시간대 추가 |

### dumpsys 출력

관찰한 폰의 dumpsys 출력은 서비스마다 시각을 다르게 찍었습니다 (확인 범위: Android 16, One UI 8.5). 값이 가려진 출력으로 본 것이라 모양만 적습니다.

| 명령 | 시각이 찍히는 곳 | 표기 모양 |
|---|---|---|
| `dumpsys usagestats` | 이벤트 줄의 `time="..."` | 한글이 섞인 사람이 읽는 문자열(원본 파일은 유닉스 밀리초) |
| `dumpsys notification` | `mRankingTimeMs`, `mCreationTimeMs`, `mVisibleSinceMs`, `mUpdateTimeMs`, 그리고 notification 안의 `when=` | 앞의 네 칸은 숫자값 뒤 괄호에 날짜·시:분:초.밀리초와 `+####` 오프셋 |
| `dumpsys batterystats` | Battery History 기록 줄 | `MM-DD HH:MM:SS.mmm`(연도 없음), 맨 앞에 `RESET:TIME:` 줄 |
| `dumpsys wifi` | 상태 기계 기록 `rec[#]` 의 `time=` | `MM-DD HH:MM:SS.mmm`(연도 없음) |
| `dumpsys bluetooth_manager` | `Enable log:` 아래 줄 | `MM-DD HH:MM:SS.mmm`(연도 없음) |
| `dumpsys account` | "Accounts History" 표의 `timestamp` 칸 | 날짜·시각 문자열 |
| `dumpsys user` | 사용자마다 `Created`, `Last logged in`, `Start time`, `Unlock time`, `Last entered foreground` | 주 사용자의 `Created` 는 `<unknown>` 으로 나옴 |

오프셋이 함께 찍히는 곳은 notification 의 네 칸뿐이었고, 나머지 문자열이 어느 시간대 기준인지와 각 칸이 벽시계인지 부팅 기준인지는 이 관찰만으로 알 수 없습니다. 이런 칸은 결과표에 "시간대 미확인" 으로 표시해 두고, 같은 사건이 벽시계로 남은 다른 기록과 맞춰 본 다음에 씁니다. dumpsys 출력 전반은 [dumpsys 출력](../../../02-artifacts/logs/dumpsys.md) 페이지에 있습니다.

## 도구

ALEAPP 는 공통 함수 파일(`ilapfuncs.py`)에 시각 변환 함수를 모아 두었고 [4], 함수 이름으로 어떤 입력을 받는지 알 수 있습니다.

| 함수 | 하는 일 |
|---|---|
| `convert_unix_ts_in_seconds(ts)` | 자릿수로 단위를 짐작해 나노초(÷1,000,000,000)·마이크로초(÷1,000,000)·밀리초(÷1,000)를 초로 바꿈. 10자리를 넘으면 초보다 작은 단위로 봄 |
| `convert_unix_ts_to_utc`, `convert_ts_int_to_utc` | 유닉스 시각을 UTC 시각으로 바꿈. 앞의 함수는 먼저 위 함수로 단위를 초로 맞추고, 뒤의 함수는 입력을 초로 보고 그대로 바꿈 |
| `convert_human_ts_to_utc`, `convert_ts_human_to_utc` | `'%Y-%m-%d %H:%M:%S'` 문자열을 시간대 변환 없이 UTC 로 간주하고, 소수점 아래 초는 버림 |
| `convert_local_to_utc` | `"%Y-%m-%d %H:%M:%S%z"` 처럼 오프셋이 붙은 문자열을 UTC 로 바꿈 |
| `convert_utc_human_to_timezone` | UTC 시각을 지정한 시간대로 바꿔 보여 줌 |

오프셋이 없는 문자열과 있는 문자열을 다른 함수로 처리한다는 점이 정규화 4단계와 같은 생각입니다. 다만 오프셋이 없는 문자열을 받는 두 함수는 그 문자열을 UTC 로 간주할 뿐이라서, 현지 시각으로 적힌 문자열을 넣으면 시간대 차이만큼 어긋난 값이 나옵니다. 같은 파일의 `timestampsconv` 함수는 인자 이름이 `webkittime` 이지만 실제로는 입력에 978307200 을 더해 유닉스 시각으로 바꾸므로, 2001-01-01 기준 초를 옮기는 함수이고 1601년 기준 WebKit 시각에는 맞지 않습니다. 도구 함수의 이름만 보고 기준점을 짐작하지 말고 값을 아는 기록 하나로 결과를 맞춰 봅니다. 도구 결과를 검증하는 방법은 [도구 검증](../../reporting/tool-validation.md) 페이지에 있습니다.

## 함정과 한계

자릿수로 단위를 짐작하는 방식은 편하지만, 값이 아주 작거나 0 이 채워진 칸이면 틀릴 수 있어서 칸의 정의를 먼저 확인하는 편이 안전합니다. 네트워크 시간으로 맞춘 시계는 사용자가 바꿀 수 없어도 값의 순서가 뒤바뀔 수 있어서 [1], 이 시계로 적힌 기록을 밀리초 단위로 줄 세우면 앞뒤가 뒤집힐 수 있습니다.

dumpsys 는 시각을 사람이 읽는 문자열로 바꿔 찍고, 관찰한 폰에서는 한글이 섞인 형식이었습니다 (확인 범위: Android 16, One UI 8.5). 기기 언어 설정에 따라 표기가 달라질 수 있는지는 확인하지 못했지만, 문자열을 파싱하는 스크립트는 관찰한 형식에 맞춰 짜고 한 줄씩 원래 문자열과 대조합니다.

Android 10 미만의 시각 처리 차이와, 삼성 One UI 가 AOSP 시각 서비스를 어떻게 바꾸는지는 확인하지 못했습니다. 관찰한 폰의 `TIME_DIFFERENCE`, `homecity_timezone` 같은 키도 뜻을 확인하기 전에는 정규화 근거로 쓰지 않습니다.

## 결과를 어떻게 해석하나

정규화한 UTC 시각은 "기기 벽시계가 그때 가리킨 시각을 UTC 로 옮긴 값" 이고, 실제 세계의 시각과 같다는 보장은 없습니다. 벽시계가 중간에 바뀌었다면 정규화만으로는 그 어긋남이 고쳐지지 않고, 바뀐 흔적은 [시각 조작 흔적](time-manipulation.md) 에서 따로 확인합니다. 보고서에는 옮긴 시각과 함께 원래 표기와 옮긴 근거를 적습니다.

> `dumpsys notification` 의 `mCreationTimeMs` 칸에 (원래 표기) 가 찍혀 있고, 괄호 안 오프셋 +0900 을 빼서 (시각) UTC 로 옮겼습니다. 이 값은 기기 벽시계 기준이며, 수집 시점에 기기 시계와 기준 시계의 차이는 (차이) 였습니다.

보고서 전체의 틀은 [포렌식 보고서](../../reporting/forensic-report.md) 페이지에 있습니다.

## 참고 문헌

1. SystemClock.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/os/SystemClock.java
2. Time detection overview — Android Open Source Project, https://source.android.com/docs/core/connect/time
3. Logcat command-line tool — Android Developers, https://developer.android.com/tools/logcat
4. ALEAPP ilapfuncs.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/ilapfuncs.py
