---
title: "시각 조작 흔적"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 1440
---

# 시각 조작 흔적 (Time Manipulation)

기기의 실제 시각 시계(wall clock)가 언제, 어느 경로(통신망·NTP·GNSS·사용자 입력 등)로 바뀌었는지를 시각 맞춤 서비스와 알람 관리자, 앱 사용 기록이 남긴 흔적과 기록 사이의 모순으로 확인하는 작업입니다.

## 언제 쓰나

타임라인에서 시각이 거꾸로 가거나 크게 비는 구간이 보일 때, 사용자가 시계를 바꿔 기록 시각을 흐렸다는 의심이 있을 때, 또는 보고서에 쓸 시각이 기기의 실제 시각 시계 기준이라 그 시계를 믿을 수 있는지 밝혀야 할 때 씁니다. 이 페이지는 시계가 바뀐 뒤 시스템에 남는 흔적과 그 해석만 다룹니다. 값을 UTC 로 옮기는 방법은 [시각 정규화](time-normalization.md), 바뀐 구간을 표시해 가며 기록을 엮는 방법은 [여러 기록 엮기](correlation.md) 에 있습니다. 이 페이지의 동작 설명은 현행 AOSP(frameworks/base 의 main 가지) 기준입니다.

## 시각이 바뀌는 경로

자동 시각 맞춤을 맡는 `time_detector` 서비스는 여러 출처에서 시각 제안 (suggestion) 을 받아 시계를 맞추고, 출처는 아래 다섯 가지로 나뉩니다 [5].

| 출처 상수 | 뜻 |
|---|---|
| `ORIGIN_TELEPHONY` | 통신망이 보내 주는 시각 (NITZ) |
| `ORIGIN_NETWORK` | NTP 서버에 물어 얻은 시각 |
| `ORIGIN_GNSS` | 위성 위치 신호(GNSS)에서 얻은 시각 |
| `ORIGIN_MANUAL` | 사용자가 손으로 넣은 시각 |
| `ORIGIN_EXTERNAL` | 외부 출처 |

기본 출처는 네트워크(NTP)와 통신망(NITZ)이고, GNSS 와 외부 출처는 Android 12 이상에서 고를 수 있지만 기본으로는 쓰지 않습니다. 출처끼리의 우선순위는 `config_autoTimeSourcesPriority` 설정으로 정하고, 현재 AOSP 기본값은 네트워크를 통신망보다 먼저 쓰며, Android 11 이하에서는 통신망이 먼저였습니다. 제조사는 `core/res/res/values/config.xml` 에서 이 순서를 바꿀 수 있습니다 [2].

NTP 쪽은 `network_time_update_service` 가 SNTP(UDP)로 서버에 시각을 묻고 그 결과를 `time_detector` 에 제안합니다 [3]. 현재 AOSP 기본값은 아래와 같고, Android 13 이하는 서버를 하나만 쓰고 설정 키도 다릅니다 [3].

| 설정 | 기본값 | 뜻 |
|---|---|---|
| `config_ntpServers` | `ntp://time.android.com` | 물어볼 서버 |
| `config_ntpPollingInterval` | 64800000 ms (18시간) | 평소 묻는 간격 |
| `config_ntpPollingIntervalShorter` | 60000 ms (1분) | 실패한 뒤 다시 묻는 간격 |
| `config_ntpRetry` | 3 | 재시도 횟수 |
| `config_ntpTimeout` | 5000 ms | 응답 기다리는 시간 |

`time_detector` 는 제안을 그대로 받아들이지 않습니다. 자동·수동 제안 모두 하한값 (lower bound) 보다 이른 시각이면 거부하고(`validateSuggestionAgainstLowerBound`), 24시간(`MAX_SUGGESTION_TIME_AGE_MILLIS`)보다 오래된 제안은 버립니다 [5]. 하한은 Android 12 부터 빌드 시각으로 정하고, 32비트 프로세스를 지원하는 기기에서 2038년 문제를 막는 상한은 Android 14 부터 더해졌습니다 [2]. 자동 시각 맞춤이 켜져 있을 때 사용자 입력(`ORIGIN_MANUAL`) 제안이 거부되는지는 공개 자료로 정해지지 않았고, 자동 맞춤 설정을 언제 껐는지 남는 기록도 알려진 것이 없습니다. 그래서 "손으로 바꾼 시점에는 자동 맞춤이 꺼져 있었다" 는 추론은 보고서에 쓰지 않습니다.

### Android 버전별 차이

| 항목 | 버전 | 출처 |
|---|---|---|
| `time_detector` 서비스(자동 시각 맞춤) | Android 10 이상 | [2] |
| `time_zone_detector` 서비스(자동 시간대 맞춤) | Android 11 이상 | [2] |
| 자동 시각 스위치 이름: Android 11 이하 "Use network-provided time", Android 12 이상 "Set time automatically" | Android 12 에서 바뀜 | [2] |
| 사용자별 "Use location to set time zone" 스위치 | Android 12 이상 | [2] |
| 출처 우선순위 기본값이 통신망 우선에서 네트워크 우선으로 바뀜 | Android 12 이상 | [2] |
| GNSS·외부 출처 선택, 빌드 시각 하한 검사 | Android 12 이상 | [2] |
| 2038년 문제를 막는 상한 검사 | Android 14 이상 | [2] |
| 여러 NTP 서버 지원 | Android 14 이상 | [3] |

Android 10 미만의 동작과, 삼성 One UI 가 이 서비스들을 바꾸거나 시각 변경을 따로 기록하는지는 실제 기기로 확인합니다.

## 바뀐 시각이 남기는 흔적

### 알람 관리자 서비스

실제 시각 시계를 설정하는 일은 `AlarmManagerService.setTimeImpl()` 이 맡고, 시간대가 바뀌면 `setTimeZoneImpl()` 이 `Intent.ACTION_TIMEZONE_CHANGED` 를 `EXTRA_TIMEZONE` 과 함께 방송합니다 [4]. 시계가 바뀌었다는 방송은 `Intent.ACTION_TIME_CHANGED` 이고, `setTimeImpl()` 안에서 보내지는 않습니다. 시각이 바뀌면 알람 관리자는 실제 시각 기준 알람의 울릴 시각을 다시 계산하고(`reevaluateRtcAlarms`), 아래 세 값을 적어 둡니다 [4].

| 필드 | 담는 것 |
|---|---|
| `mLastTimeChangeClockTime` | 마지막으로 시각이 바뀐 때의 실제 시각 |
| `mLastTimeChangeRealtime` | 그때의 부팅 기준 시각(elapsed realtime) |
| `mNumTimeChanged` | 시각이 바뀐 횟수 |

앞의 두 값은 한 순간을 두 시계로 함께 적은 것이라서 시계가 바뀐 시점을 부팅 기준 축에 고정하는 데 쓸 수 있습니다. 필드 이름으로 보면 마지막 변경 한 번과 횟수만 담고, 변경마다 이력을 쌓지는 않습니다. 이 값들이 `dumpsys alarm` 에 찍히는 이름은 판마다 다를 수 있어 실제 기기로 확인합니다.

### 시각 맞춤 서비스 덤프

`adb shell cmd time_detector dump` 를 실행하면 자동 맞춤이 켜져 있는지, 시각 하한·상한, 출처 우선순위, 시각 변경 로그, 출처별 최근 제안 이력이 나옵니다 [2]. 시각 변경 로그가 몇 건까지 남고 재부팅 뒤에도 남는지는 실제 기기로 확인합니다. 이력은 "Telephony suggestion history", "Network suggestion history", "Gnss suggestion history", "External suggestion history" 로 나뉘고, 출처마다 최근 10개(`KEEP_SUGGESTION_HISTORY_SIZE = 10`)만 남깁니다 [5]. 오래된 제안은 새 제안에 밀려나서, 시각이 바뀐 시점이 오래 전이면 이 이력으로 경로를 판별하기 어렵습니다.

NTP 서비스의 상태는 `adb shell cmd network_time_update_service dump` 로 볼 수 있습니다. 서비스 명령의 인자와 출력 형식은 Android 판마다 바뀔 수 있고, 시각 변경 이력에 대한 공식 설명은 없습니다 [3]. 두 명령을 루팅하지 않은 기기에서 일반 adb 셸 권한으로 실행할 수 있는지는 기기마다 확인합니다.

### 앱 사용 기록의 "Time changed." 줄

앱 사용 기록 서비스는 실제 시각과 기대한 시각이 일정 기준 이상 어긋나면 시각이 바뀐 것으로 보고 로그를 남기고, 그 기준은 [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) 페이지에 있습니다. Android 16(One UI 8.5) 기기의 `dumpsys usagestats` 에는 "UsageStats RollOver history" 절에 아래 모양의 줄이 남습니다.

```
<<한글>>:##:##.###User[#] Time changed. actualSystemTime:<<한글>> expectedSystemTime:<<한글>> actualRealtime:<<한글>>
```

`actualSystemTime` 과 `expectedSystemTime` 의 차이로 시계가 얼마나 뛰었는지, `actualRealtime` 으로 그 순간이 부팅 기준 축의 어디인지 추정할 수 있습니다. 다만 이 줄에는 출처 필드가 없어서, 사용자가 바꾼 것인지 자동 맞춤이 고친 것인지는 이 줄만으로 구분할 수 없고, 줄의 건수가 곧 사용자의 조작 횟수라는 뜻도 아닙니다. 이 절이 AOSP 에도 있는지 삼성이 더한 것인지는 공개 자료로 판별할 수 없습니다.

### 그 밖의 기록

`dumpsys batterystats` 기록 맨 앞에는 `RESET:TIME:` 줄이 있습니다. 배터리 기록이 시각 변경을 따로 표시하는지는 실제 기기로 확인합니다. `settings global` 의 `auto_time`, `auto_time_zone` 키는 수집 시점의 자동 맞춤 설정을 알려 주지만, 이 값이 언제 바뀌었는지 남는 기록은 알려진 것이 없습니다. 설정 키를 읽는 법은 [설정 값](../../../02-artifacts/system-account/settings.md), 시간대 설정의 의미는 [시간대와 시각 설정](../../../02-artifacts/system-account/time-zone.md) 페이지에 있습니다.

### 기록 사이의 모순

부팅 기준 시각은 앞으로만 가기 때문에, 같은 부팅 안에서 부팅 기준 값은 커지는데 실제 시각 값이 작아지는 두 기록이 있으면 그 사이에 시계가 바뀐 것입니다 [1]. 이 판단은 SystemClock 설명에서 끌어낸 해석입니다. 두 시계를 함께 적은 기록은 [여러 기록 엮기](correlation.md) 에 정리했습니다.

> 그림 자리: 가로축은 부팅 기준 시각, 세로축은 실제 시각으로 두고, 기울기 1 로 오르던 선이 한 지점에서 아래로 뚝 떨어진 뒤 다시 오르는 모습(그 지점이 "Time changed." 줄과 맞물림)

## 절차

1. **수집할 때 기기 시계와 기준 시계의 차이를 적어 둡니다.** 수집 시각과 시간대를 적는 방법은 [시각 정규화](time-normalization.md) 에 있습니다.
2. **덤프를 일찍 뽑습니다.** `cmd time_detector dump` 의 이력은 출처마다 10개뿐이라 [5] 시간이 지나면 밀려나고, 재부팅 뒤에 남는다는 보장도 없습니다. `cmd time_detector dump`, `cmd network_time_update_service dump`, `dumpsys alarm`, `dumpsys usagestats` 를 함께 뽑고, 권한 때문에 실행되지 않은 명령은 그 결과를 그대로 기록합니다.
3. **설정 상태를 기록합니다.** `auto_time`, `auto_time_zone` 값으로 수집 시점에 자동 맞춤이 켜져 있었는지 적습니다.
4. **변경 시점을 부팅 기준 축에 고정합니다.** "Time changed." 줄의 `actualRealtime` 과 알람 관리자의 마지막 변경 기록처럼 두 시계를 함께 적은 값을 찾습니다.
5. **타임라인에서 모순을 찾습니다.** 같은 부팅 안에서 부팅 기준 값은 커지는데 실제 시각 값이 작아지는 곳, 혹은 실제 시각이 크게 건너뛴 곳을 표시합니다.
6. **경로를 확인합니다.** 변경 시점 무렵 출처별 제안 이력에 맞는 제안이 있는지 봅니다. 이력은 통신망·네트워크·GNSS·외부 네 가지로 나뉘고 최근 10개뿐이라서, 이력에서 찾지 못했다고 곧 수동 변경이라고 단정하지 않습니다.

## 함정과 한계

시간대가 바뀐 경우와 시계가 바뀐 경우는 다른 방송(`ACTION_TIMEZONE_CHANGED`, `ACTION_TIME_CHANGED`)으로 알려집니다. 유닉스 밀리초는 UTC 기준이라서 시간대만 바뀌면 값은 뛰지 않고 현지 형식 문자열의 표기만 달라지므로, 현지 형식 문자열만 보고 시계 조작으로 판단하지 않습니다.

자동 맞춤이 시계를 고친 경우에도 그 차이가 앱 사용 기록의 기준을 넘으면 "Time changed." 줄이 남을 수 있습니다. 시각 변경 흔적이 있다는 것과 사용자가 시계를 조작했다는 것은 다른 말이라서, 출처를 구분하지 못하면 "시각 변경이 있었다" 까지만 씁니다.

알람 관리자의 값과 `time_detector` 이력이 dumpsys·cmd 출력에 어떤 모양으로 나오는지, 일반 adb 권한으로 볼 수 있는지, 삼성 기기에서 추가 기록이 있는지는 판마다 다를 수 있습니다. 실제 기기에서 볼 때는 출력 모양을 먼저 확인하고 이 페이지의 필드 이름과 대조합니다.

## 결과를 어떻게 해석하나

흔적은 "시계가 바뀌었다", "얼마나 바뀌었다", "어느 경로로 바뀌었다" 의 세 층으로 나눠 적습니다. 앞의 두 층은 두 시계를 함께 적은 기록으로 확인할 수 있지만, 경로는 제안 이력이나 설정 기록으로 따로 뒷받침해야 합니다. 보고서에는 기록으로 확인되는 만큼만 씁니다.

> `dumpsys usagestats` 의 "UsageStats RollOver history" 절에 "Time changed." 기록이 (건수) 있고, 그중 (부팅 기준 시각) 무렵의 기록은 시계가 기대값보다 (차이) 만큼 어긋났음을 보여 줍니다. 수집한 자료로는 이 변경이 사용자 입력인지 자동 맞춤인지 구분하지 못했습니다.

시각 조작을 포함한 증거 인멸 의심 전반은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md), 보고서의 틀은 [포렌식 보고서](../../reporting/forensic-report.md) 페이지에 있습니다.

## 참고 문헌

1. SystemClock.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/os/SystemClock.java
2. Time detection overview — Android Open Source Project, https://source.android.com/docs/core/connect/time
3. Network time detection — Android Open Source Project, https://source.android.com/docs/core/connect/time/network-time-detection
4. AlarmManagerService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/apex/jobscheduler/service/java/com/android/server/alarm/AlarmManagerService.java
5. TimeDetectorStrategyImpl.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/timedetector/TimeDetectorStrategyImpl.java
