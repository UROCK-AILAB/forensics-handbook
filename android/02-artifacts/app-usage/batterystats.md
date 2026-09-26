---
title: "배터리 사용 기록"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 500
---

# 배터리 사용 기록 (batterystats)

배터리 사용 기록 (batterystats) 은 마지막 충전(또는 초기화) 이후 화면·GPS·카메라·작업(job)·깨우기 잠금(wake lock) 같은 구성 요소가 언제 켜지고 꺼졌는지를 시간 순서로 적는 시스템 기록이고, 앱이 어느 시간대에 무엇을 켜 두었는지 짐작하는 근거가 됩니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

시스템은 배터리 소모를 따지려고 마지막 충전(또는 초기화) 이후의 데이터를 모으고, 여기에는 앱별(UID별) 통계와 시간에 따른 전원 관련 이벤트가 함께 들어갑니다 [1]. 이 기록은 구성 요소가 "켜져 있었는지" 를 보여 줄 뿐이고, 그 구성 요소가 전력을 얼마나 썼는지를 보여 주지는 않습니다 [1].

포렌식에서 쓸모 있는 부분은 시간에 따른 이벤트 목록(Battery History)입니다. 화면이 켜진 시각, 카메라·오디오·GPS 가 켜진 구간, 앱의 작업이 돈 시각이 한 줄씩 쌓여서, 다른 기록이 비어 있는 시간대에 기기가 무엇을 하고 있었는지 채워 줄 수 있습니다.

## 위치와 버전별 차이

기록은 메모리의 버퍼에 쌓이다가 파일로 백업되고, 파일은 아래 디렉터리에 `.bh` 확장자로 남습니다 [2].

```
/data/system/battery-history/
```

버퍼가 차면 새 파일을 열고, 파일 수가 최대치를 넘거나 저장 공간이 100MB 아래로 떨어지면 번호가 작은(오래된) 파일부터 지웁니다 [2]. 최대 파일 수와 버퍼 크기는 `BatteryStatsImpl.Constants` 의 `MAX_HISTORY_FILES`, `MAX_HISTORY_BUFFER` 로 정하고, 구체 값은 판마다 다를 수 있어 소스나 실제 기기에서 확인합니다 [2]. settings global 에는 `battery_stats_constants` 라는 키가 있을 수 있는데, 이 키가 위 값을 바꾸는지 밝힌 공개 자료는 없습니다.

`/data/system/` 은 시스템 영역이라 루팅되지 않은 기기에서 파일을 직접 복사하기 어렵습니다. 대신 아래 방법으로 텍스트를 받을 수 있습니다 [1].

| 방법 | 명령 | 비고 |
|---|---|---|
| dumpsys | `adb shell dumpsys batterystats` | 현재 모은 데이터를 텍스트로 출력 |
| 버그 리포트 (Android 7.0 이상) | `adb bugreport <경로>/bugreport.zip` | 압축 파일로 받음 |
| 버그 리포트 (Android 6.0 이하) | `adb bugreport` | 텍스트 파일(`bugreport.txt`)로 받음 |

`dumpsys batterystats` 는 adb 일반 셸 권한으로 읽을 수 있습니다. 버그 리포트의 짜임새는 [버그 리포트 (bugreport)](../logs/bugreport.md), dumpsys 일반은 [dumpsys 출력 (dumpsys)](../logs/dumpsys.md) 페이지에서 다룹니다.

제조사 차이는 아래처럼 정리할 수 있습니다.

| 기기 | 내용 |
|---|---|
| AOSP | 디렉터리·확장자·파일 교체 규칙(소스 기준) [2] |
| 삼성 One UI | 기록 줄에 `ap_temp=`, `pa_temp=`, `skin_temp=`, `txshare_event=`, `current_event=`, `misc_event=` 항목이 더 보임 |

## 구조

`.bh` 파일의 바이너리 형식은 공개 문서에 설명이 없어서, 여기서는 `dumpsys batterystats` 텍스트 출력의 모양을 정리합니다.

출력은 아래 모양의 머리줄로 시작합니다.

```
Battery History [Format: #] (##% used, ####KB used of ####KB, #### strings using ###KB):
```

머리줄 괄호 안은 기록 버퍼를 얼마나 썼는지 보여 줍니다. 그 아래 기록 줄은 아래 모양이고, 맨 앞 `##-## ##:##:##.###` 은 연도 없이 월-일과 시각을 적은 필드입니다.

```
  ##-## ##:##:##.### RESET:TIME: ...
  ##-## ##:##:##.### ### status=... health=... plug=... temp=### volt=#### current=####
  ##-## ##:##:##.### ### +running wake_reason=...
  ##-## ##:##:##.### ### +sensor +screen brightness=... +state=...
  ##-## ##:##:##.### ### +camera +cellular_high_tx_power +state=...
  ##-## ##:##:##.### ### -job=...
```

한 줄에는 그 순간 바뀐 항목만 적고, `+` 는 켜짐, `-` 는 꺼짐을 뜻합니다. 자주 나오는 항목을 뜻에 따라 묶으면 다음과 같습니다.

| 묶음 | 항목 |
|---|---|
| 배터리 상태 | `status=`, `health=`, `plug=`, `temp=`, `volt=`, `current=` |
| CPU 깨어남 | `+running`/`-running`, `wake_reason=`, `+wake_lock=`/`-wake_lock=` |
| 화면 | `+screen`/`-screen`, `brightness=`, `screenwake=`, `display_state_changed=` |
| 앱 작업 | `+job=`/`-job=` |
| 뜻이 공개되지 않은 항목 | `-fg=`, `+state=`/`-state=`, `+tmpwhitelist=`/`-tmpwhitelist=` |
| 장치 | `+gps`/`-gps`, `gps_signal_quality=`, `+camera`/`-camera`, `+audio`/`-audio`, `+sensor`/`-sensor` |
| 통신 | `+wifi_scan`/`-wifi_scan`, `conn=`, `cellular_high_tx_power` |
| 삼성 기기 추가 항목 | `ap_temp=`, `pa_temp=`, `skin_temp=`, `txshare_event=`, `current_event=`, `misc_event=` |

`job=`, `wake_lock=`, `fg=`, `state=` 같은 항목 뒤에 UID 나 패키지 이름이 어떤 형식으로 붙는지는 실제 출력에서 확인합니다. UID 를 패키지 이름으로 옮기는 법은 [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md) 페이지에 있습니다.

## 증거로서 의미

**증명하는 것**

`+camera` 부터 `-camera` 까지의 구간은 그 시간대에 카메라가 켜져 있었다는 기록이고, `+audio`·`+gps`·`+screen` 도 같은 방식으로 읽습니다. `+job=` 이나 `+wake_lock=` 뒤에 앱이 적혀 있으면 그 앱의 작업이나 깨우기 잠금이 그 시각에 시작됐다는 기록입니다. 화면이 꺼진 시간대에 특정 앱의 작업·GPS·카메라가 켜진 기록이 있다면, [몰래 설치된 감시 앱 (Stalkerware)](../../04-scenarios/incident/stalkerware.md) 이나 [악성 앱 흔적 분석](../../03-techniques/analysis/malicious-app-triage/index.md) 에서 확인할 단서가 됩니다.

**증명하지 못하는 것**

구성 요소가 켜졌다는 기록은 사람이 그 기능을 썼다는 뜻이 아닙니다. 카메라가 켜진 구간이 있어도 사진이 저장됐는지는 알 수 없고, 사진은 [미디어 저장소 (MediaStore)](../media/mediastore/index.md) 같은 곳에서 따로 찾아야 합니다. 이 기록은 구성 요소가 켜져 있었는지를 보여 줄 뿐 얼마나 소모했는지는 보여 주지 않으니 [1], 한 줄의 켜짐 기록을 "배터리를 많이 썼다" 로 옮겨 적지 않습니다. 보고서에는 "이 시간대에 이 앱 이름으로 작업이 시작·종료된 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

텍스트 출력의 기록 줄은 연도 없이 월-일과 시각만 찍혀 있습니다. 이 시각이 기기 현지 시각인지 UTC 인지는 같은 시각대의 다른 기록(예: usagestats 의 화면 켜짐 이벤트)과 맞춰 보고 정합니다. 연도는 수집 날짜와 `RESET:TIME:` 줄의 값으로 판단합니다.

`.bh` 파일 이름의 숫자는 MonotonicClock 기준 밀리초이고 유닉스 기준 실제 시각(wall clock)이 아닙니다 [2]. 파일 이름을 날짜로 바꾸면 엉뚱한 날짜가 나오니, 파일 이름 숫자는 파일끼리 순서를 정하는 데만 씁니다. 시각 값 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지에서 다룹니다.

## 함정과 한계

첫째, 완전히 충전되면 모은 데이터가 지워집니다 [1]. 수집 시점 직전에 기기를 끝까지 충전했다면 그 전 기록은 dumpsys 에 나오지 않을 수 있으니, 압수 뒤 충전 여부를 수집 기록에 적어 둡니다.

둘째, `adb shell dumpsys batterystats --reset` 은 모은 데이터를 지우는 명령입니다 [1]. 측정 전 초기화에 쓰는 명령이지만, 증거 수집 중에는 절대 실행하지 않습니다. 반대로 분석 대상 기기의 기록이 이상하게 짧다면 누군가 이 명령을 썼을 가능성도 따져 봅니다.

셋째, 기록 버퍼와 파일 수에 한도가 있어서 오래된 기록은 밀려납니다 [2]. 머리줄의 사용률로 버퍼가 얼마나 찼는지 가늠할 수 있습니다.

넷째, Battery History 시각화 도구(Battery Historian)는 더 이상 활발히 관리되지 않습니다 [1]. 새 버전 출력이나 삼성 추가 항목을 제대로 읽는지 확인하지 않고 도구 그림만으로 결론 내리지 않습니다.

## 직접 분석해 보기

### 텍스트로 한 번

`.bh` 파일 형식은 공개 문서에 설명이 없어서 헥스 따라가기 대신 텍스트 출력을 직접 읽습니다.

1. `adb shell dumpsys batterystats > batterystats.txt` 로 출력을 파일에 담습니다. `--reset` 은 붙이지 않습니다.
2. 머리줄 `Battery History [...]` 로 버퍼 사용률을 확인하고 `RESET:TIME:` 줄을 찾아 기록 시작 시각을 적어 둡니다.
3. 조사할 시간대의 줄만 잘라 `+camera`, `+audio`, `+gps`, `+screen` 의 켜짐·꺼짐 짝을 맞춥니다.
4. 같은 구간의 `+job=`, `+wake_lock=`, `+state=` 줄에서 어떤 앱이 나오는지 봅니다.

### 공개 도구로 한 번

버그 리포트 압축 파일을 Battery Historian 에 올리면 구성 요소별 켜짐 구간을 막대로 보여 줍니다 [1]. 도구가 보여 주는 구간 몇 개를 텍스트 출력의 `+`/`-` 줄과 맞춰 보고 나서 결과를 씁니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [앱 사용 기록 (usagestats)](usagestats/index.md) | `+screen` 시각과 SCREEN_INTERACTIVE, 앱 전경 전환 시각 |
| [데이터 사용량 (netstats)](../network/netstats.md) | 앱의 작업 구간에 그 앱의 송수신이 있는지 |
| [카메라 사진과 메타데이터 (DCIM·EXIF)](../media/dcim-exif.md) | `+camera` 구간에 찍힌 사진이 있는지 |
| [위치 캐시 (Cached Locations)](../location/cached-locations.md) | `+gps` 구간에 위치 기록이 있는지 |
| [logcat (logcat)](../logs/logcat.md) | 같은 시각의 앱 로그 |

시간대를 하나로 맞춰 늘어놓는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

공개 안드로이드 시험 데이터(NIST CFReDS 등)에 버그 리포트나 `dumpsys batterystats` 출력이 들어 있으면 아래 질문을 풀어 봅니다.

1. `RESET:TIME:` 줄의 시각은 언제이고, 기록은 며칠 동안 이어집니까?
2. 화면이 꺼져 있던 구간에 `+gps` 나 `+camera` 가 켜진 적이 있습니까? 있다면 같은 구간의 `+job=` 줄에 어떤 앱이 있습니까?
3. 머리줄의 사용률로 보아 기록 버퍼가 가득 차서 오래된 기록이 밀려났을 가능성이 있습니까?

## 참고 문헌

1. Android Developers — Profile battery usage with Batterystats and Battery Historian — https://developer.android.com/topic/performance/power/setup-battery-historian
2. AOSP frameworks/base — BatteryStatsHistory.java — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/com/android/internal/os/BatteryStatsHistory.java
