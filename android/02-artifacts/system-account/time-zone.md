---
title: "시간대와 시각 설정"
parent: "아티팩트 · 시스템·계정"
nav_order: 380
---

# 시간대와 시각 설정 (Time Zone)

기기 시계를 무엇으로 맞췄는지, 시간대가 무엇이었는지를 알려 주는 설정과 그 설정으로 다른 기록의 시각을 어떻게 읽는지를 정리합니다.

## 한 줄 요약

자동 시각·자동 시간대를 켰는지는 Settings.Global 의 `auto_time`·`auto_time_zone` 에, 현재 시간대 ID 는 시스템 속성 `persist.sys.timezone` 에 들어가고 [1][4], 이 값들로 기기 시계를 얼마나 믿을지와 현지 시각으로 적힌 기록을 UTC 로 바꿀 기준을 정합니다.

## 무엇을 기록하나 · 왜 생기나

Android 는 시각과 시간대를 따로 맞춥니다. 자동 시각 설정은 time_detector 서비스(Android 10 부터)가, 자동 시간대 설정은 time_zone_detector 서비스(Android 11 부터)가 맡습니다 [1].

시각을 받아 오는 출처는 네트워크(NTP), 통신망(NITZ), GNSS, 외부(제조사가 연동한 출처)가 있고, GNSS 와 외부 출처는 Android 12 부터 쓸 수 있습니다 [1]. 시간대는 통신망 정보로 정하는 방식에 더해 Android 12 부터 위치로 정하는 방식을 고를 수 있습니다 [1].

조사에서 이 설정이 중요한 까닭은 기록마다 시각을 적는 방식이 달라서입니다. 유닉스 밀리초처럼 UTC 로 적힌 기록은 시간대와 상관없지만, 현지 시각 문자열로 적힌 기록은 어느 시간대였는지 알아야 UTC 로 바꿀 수 있습니다. 또 자동 시각이 꺼져 있었다면 시계를 손으로 맞췄을 수 있어서 기기 시각 전체를 얼마나 믿을지 따로 따져야 합니다.

## 위치와 버전별 차이

| 버전 | 바뀐 점 [1] |
|---|---|
| Android 10 | time_detector 서비스 도입 |
| Android 11 | time_zone_detector 서비스 도입. 이 버전까지 시각 출처는 통신망이 네트워크보다 우선으로 고정 |
| Android 12 | 기본 우선순위가 네트워크 먼저로 바뀜. GNSS·외부 시각 출처 추가. 위치로 시간대 정하기(선택 기능)와 사용자별 설정 `location_time_zone_detection_enabled` 추가. 빌드 시각보다 이른 자동 시각 제안을 버림 |
| Android 13 | 위치 감지가 불확실하면 잠깐 통신망 값을 쓰는 대체 모드 추가 |
| Android 14 | 32비트 프로세스를 지원하는 기기에서 Y2038 문제를 일으킬 수 있는 시각 제안을 막는 상한 추가. 위치 감지만 지원하는 기기는 `location_time_zone_detection_enabled` 값을 무시 |

자동 시각 키 `auto_time` 과 자동 시간대 키 `auto_time_zone` 은 Settings.Global 에 있습니다 [4]. AOSP 기본값은 자동 시간대 켜짐이고, 다른 기기의 백업을 복원하면 `auto_time_zone` 값도 기본으로 복원됩니다 [1]. 그래서 이 값이 사용자가 직접 고른 값이 아닐 수 있습니다.

삼성 기기에는 global 표에 `auto_time`, `auto_time_zone`, `auto_time_zone_explicit`, `clockwork_auto_time`, `clockwork_auto_time_zone` 키가 있습니다. system 표에는 `homecity_timezone`, `dualclock_menu_settings`, `TIME_DIFFERENCE`, `next_alarm_formatted` 키가 있는데, 이름으로 보아 삼성 듀얼 시계 기능과 관련된 듯하지만 뜻을 설명한 공개 자료는 없습니다. `time_12_24` 와 `location_time_zone_detection_enabled` 는 목록에 없을 수 있습니다. `auto_time_zone_explicit` 과 `clockwork_` 로 시작하는 키도 뜻을 설명한 공개 자료가 없습니다. settings 파일의 위치와 구조는 [설정 값 (Settings Global·Secure·System)](settings.md) 페이지에 있습니다.

시간대 ID 는 `persist.sys.timezone` 속성에, 그 값을 얼마나 믿을지는 `persist.sys.timezone_confidence` 속성에 적습니다 [5]. 부팅 때 `persist.sys.timezone` 이 비었거나 올바르지 않으면 시스템이 `GMT` 를 낮은 신뢰도로 넣어서 [5], 확보한 값이 `GMT` 라면 사용자가 고른 시간대가 아닐 수 있습니다. 이 속성이 이미지 안 어느 파일에 저장되는지와 시간대 데이터(tzdata)를 어떻게 업데이트하는지는 검체에서 확인합니다.

## 구조

### 기록별 시각 방식

시간대를 알아야 하는 기록과 그렇지 않은 기록을 먼저 나눕니다.

| 기록 | 시각 방식 | 출처·범위 |
|---|---|---|
| 사용자 xml·dumpsys user 의 생성·로그인 시각 | System.currentTimeMillis() 기반 유닉스 밀리초 | [2] |
| `Build.TIME` | 유닉스 밀리초(`ro.build.date.utc` 는 유닉스 초) | [3] |
| logcat 한 줄 | `MM-DD hh:mm:ss.mmm` 로 시작하고 연도·시간대가 없음 | |

logcat 시각은 기기 시간대의 현지 시각으로 보이고, 연도가 없어서 해를 넘기는 로그는 다른 기록으로 해를 정해야 합니다. 기록별 자세한 시각 해석은 각 아티팩트 페이지와 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

### 시계가 바뀐 흔적

`dumpsys usagestats` 출력의 "UsageStats RollOver history" 아래에는 다음 모양의 줄이 나올 수 있습니다. `<값>`·`#` 자리에 실제 값이 들어갑니다.

```
<날짜>:##:##.###User[#] Time changed. actualSystemTime:<값> expectedSystemTime:<값> actualRealtime:<값>
```

칸 이름으로 보면 앱 사용 기록 서비스가 기대한 시스템 시각과 실제 시스템 시각이 어긋난 때를 적은 줄이라 시계 변경을 가려내는 단서가 될 수 있지만, 어떤 조건에서 이 줄을 쓰는지 밝힌 공개 자료는 없습니다. 앱 사용 기록 자체는 [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) 페이지에서 다룹니다.

## 증거로서 의미

| 기록 | 증명하는 것 | 증명하지 못하는 것 |
|---|---|---|
| `auto_time`·`auto_time_zone` 값 | 확보 시점에 자동 시각·자동 시간대 설정이 그 상태였다는 것 | 사건 당시에도 같은 상태였는지 |
| `persist.sys.timezone` | 확보 시점의 시간대 ID | 사건 당시 기기가 있던 시간대, 여행 중 바뀐 이력 |
| 자동 시각이 켜져 있음 | 시계를 외부 출처로 맞추도록 설정되어 있었다는 것 | 모든 기록의 시각이 정확하다는 것(출처를 받지 못한 기간이 있을 수 있음) |
| usagestats 의 "Time changed" 줄 | 그 서비스가 시각 어긋남을 적었다는 것 | 사용자가 직접 시계를 바꿨다는 것 |

보고서에는 "확보 시점에 자동 시간대 설정이 켜져 있었고 시간대 ID 는 X 였다. 현지 시각으로 적힌 기록은 이 시간대를 기준으로 UTC 로 바꿨다" 처럼 변환 기준을 함께 적습니다.

## 시각 해석

Android 12 부터 time_detector 서비스는 빌드 시각보다 이른 자동 시각 제안을 버리고, Android 14 부터는 32비트 프로세스를 지원하는 기기에서 Y2038 문제를 일으킬 수 있는 제안도 막습니다 [1]. 그래서 이 버전들에서는 빌드 시각(`ro.build.date.utc`)이 자동으로 맞춘 시계의 하한이 되고, 이보다 이른 시각이 찍힌 기록을 만나면 그 값이 어디서 왔는지 따로 확인합니다. 빌드 시각을 읽는 법은 [기기 정보와 빌드 (build.prop·Build)](device-build.md) 페이지에 있습니다.

확보 시점의 시간대로 과거 기록 전체를 바꾸면 안 됩니다. 기기가 다른 시간대에 있었던 기간의 현지 시각 기록은 그때의 시간대로 바꿔야 하는데, settings 파일에는 시간대 변경 이력이 없고 현재 값만 남습니다. 그 기간의 시간대는 위치 기록이나 시간대 차이가 함께 적히는 기록에서 찾습니다.

## 함정과 한계

자동 시각이 켜져 있어도 비행기 모드처럼 출처를 받을 수 없던 기간에는 시계가 틀어졌을 수 있고, 자동 시각이 꺼져 있었다고 해서 시계를 실제로 바꿨다는 뜻도 아닙니다. 시계 조작 여부는 이 설정 하나로 판단하지 않고 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md) 페이지처럼 여러 기록의 순서를 맞춰 보고 정합니다.

삼성 듀얼 시계의 `homecity_timezone` 같은 값은 기기 시간대와 다를 수 있고 뜻도 알려져 있지 않아서, 기기 시간대의 근거로 쓰지 않습니다. 한 번도 값을 쓰지 않은 키가 목록에서 빠지는지는 알려져 있지 않아서, `location_time_zone_detection_enabled` 가 없다는 사실로 위치 기반 시간대를 쓰지 않았다고 말하지 않습니다.

time_detector 와 time_zone_detector 의 dump 출력을 adb 일반 권한으로 볼 수 있는지, 실제 기기의 출력이 문서 예시와 같은지는 검체 기기에서 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

이 설정만 담은 고유 파일이 없고 값이 settings 파일 안에 들어가서, 헥스로 읽는 법은 [설정 값 (Settings Global·Secure·System)](settings.md) 페이지의 방법을 그대로 씁니다. 파일을 열어 `name="auto_time"`, `name="auto_time_zone"` 항목을 찾아 값을 옮깁니다.

### 공개 도구로 한 번

라이브 기기에서는 settings 목록에서 시각 관련 키를 추립니다. adb 일반 권한으로 settings 목록을 읽을 수 있습니다.

```sh
adb shell settings list global | grep -E 'auto_time|clockwork_auto_time'
adb shell settings list system | grep -E 'homecity_timezone|dualclock|TIME_DIFFERENCE'
```

자동 시각·시간대 서비스의 상태는 다음 명령으로 봅니다 [1]. time_detector 출력에는 출처별 제안 기록과 현재 하한값이, time_zone_detector 출력에는 현재 시간대 ID 와 자동·위치 감지 설정이 나옵니다 [1].

```sh
adb shell cmd time_detector dump
adb shell cmd time_zone_detector dump
```

`dumpsys usagestats` 출력에서는 `Time changed.` 줄을 찾아 둡니다.

## 교차 검증

현지 시각으로 적힌 기록을 UTC 로 바꿀 때는 그 기간 기기가 어디 있었는지를 [그 시각에 어디 있었나 (Location)](../../04-scenarios/activity/location.md) 시나리오의 기록과 맞춰 시간대를 정합니다. 연도 없이 적히는 로그 시각은 [logcat (logcat)](../logs/logcat.md) 페이지와 함께 봅니다.

## 실습

공개 안드로이드 검체(NIST CFReDS 에 올라온 모바일 이미지 등)를 구해 다음을 풀어 봅니다.

1. settings 파일에서 `auto_time`·`auto_time_zone` 값을 찾아 적습니다.
2. 검체의 Android 버전을 확인하고, 위 버전 표에서 이 검체에 해당하는 동작을 고릅니다.
3. 현지 시각 문자열로 적힌 기록과 유닉스 밀리초로 적힌 기록에서 같은 사건을 하나 찾아 두 시각의 차이로 시간대를 계산해 봅니다.
4. 빌드 시각보다 이른 시각이 찍힌 기록이 있는지 찾아봅니다.

## 참고 문헌

1. Time overview — Android Open Source Project, https://source.android.com/docs/core/connect/time
2. UserManagerService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/UserManagerService.java
3. Build.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/os/Build.java
4. Settings.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/provider/Settings.java
5. SystemTimeZone.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/SystemTimeZone.java
