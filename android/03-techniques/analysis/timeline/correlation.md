---
title: "여러 기록 엮기"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 1430
---

# 여러 기록 엮기 (Correlation)

UTC 로 옮긴 여러 기록을 한 시간 축에 올리되, 부팅 경계와 실제 시각 시계(wall clock)가 뛴 구간을 구분해 순서를 믿을 수 있는 범위를 정하고, 같은 사건이 여러 곳에 남긴 흔적끼리 맞춰 보는 작업입니다.

## 언제 쓰나

앱 사용 기록·logcat·dumpsys 출력처럼 서로 다른 곳에서 나온 기록으로 한 사건의 앞뒤를 밝혀야 할 때 씁니다. 값 하나하나를 UTC 로 옮기는 일은 [시각 정규화](time-normalization.md) 에서 먼저 끝내고, 이 페이지는 옮긴 기록끼리 맞물리는 방법을 다룹니다. 시계가 바뀐 흔적 자체를 찾는 방법은 [시각 조작 흔적](time-manipulation.md) 에 있습니다.

## 두 시계로 순서 세우기

실제 시각 기록끼리는 유닉스 에포크로 맞춘 뒤 시간순으로 합칠 수 있지만, 실제 시각 시계는 앞뒤로 뛸 수 있어서 그 사이에 시계가 바뀌었으면 순서가 틀어집니다 [1]. `elapsedRealtime` 은 깊은 절전 시간까지 세면서 단조 증가하기 때문에 한 부팅 안에서는 순서를 믿을 수 있는 기준이지만, 부팅할 때마다 0부터 다시 셉니다 [1]. 그래서 부팅 기준 값을 쓰려면 부팅 경계부터 찾아야 하고, 부팅 기준 값을 날짜로 옮기려면 같은 순간의 실제 시각 값이 함께 적힌 기록이 있어야 합니다.

두 시계를 잇는 다리가 되는 기록은 아래와 같습니다.

| 기록 | 함께 적히는 값 | 근거 |
|---|---|---|
| `dumpsys usagestats` 의 "UsageStats RollOver history" 절, `rolloverStats` 줄 | `realTime:`, `systemTime:` | |
| 같은 절의 "Time changed." 줄 | `actualSystemTime`, `expectedSystemTime`, `actualRealtime` | 뜻은 [시각 조작 흔적](time-manipulation.md) 참고 |
| 알람 관리자 서비스의 마지막 시각 변경 기록 | 변경 때의 실제 시각과 그때의 부팅 기준 시각 | 현행 AOSP 기준. [시각 조작 흔적](time-manipulation.md) 참고 |
| logcat 을 두 형식으로 뽑은 결과 | `-v monotonic`(마지막 부팅 이후 CPU 초)와 `-v epoch`(1970-01-01 부터 초) | [2] |

`rolloverStats` 줄은 아래 모양입니다(값 자리는 가림). `realTime:` 과 `systemTime:` 이 어떤 단위와 형식으로 찍히는지, 이 절이 AOSP 에도 있는지 삼성이 더한 것인지는 실제 기기로 확인해야 합니다.

```
<<한글>>:##:##.###User[#] rolloverStats by event Type:#/ init elapsed time:<<한글>>/ timeStamp:<<한글>>/ ExpiryDate:<<한글>>/ realTime:<<한글>>/ systemTime:<<한글>>
```

logcat 은 같은 줄을 `-v monotonic` 과 `-v epoch` 로 한 번씩 뽑으면 두 기준을 맞댈 수 있습니다 [2]. 다만 logcat 은 순환 버퍼라서 [2] 두 번 뽑는 사이에 앞쪽 줄이 밀려날 수 있습니다. 두 결과는 PID·TID·태그·내용이 같은 줄끼리 짝을 짓습니다.

> 그림 자리: 부팅 기준 축(부팅마다 0에서 시작)과 실제 시각 축을 위아래로 두고, rolloverStats 줄 하나가 두 축의 한 점씩을 잇는 모습

## 절차

1. **정규화를 먼저 끝냅니다.** 기록마다 시계 종류, 원래 표기, 옮긴 UTC 시각이 한 줄에 있어야 엮을 수 있습니다. 방법은 [시각 정규화](time-normalization.md) 에 있습니다.
2. **부팅 경계를 찾습니다.** 부팅 기준 값은 부팅마다 0부터 다시 세서 [1], 경계를 모르면 서로 다른 부팅의 값을 한 줄에 섞게 됩니다. `dumpsys bluetooth_manager` 의 `Enable log:` 아래에는 아래 같은 줄이 있습니다. 부팅 무렵 시스템이 블루투스를 켠 기록으로 보이고, 이 시각이 부팅 시각과 얼마나 가까운지는 실제 기기로 확인합니다. `settings global` 에는 `boot_count` 키도 있는데, 이 값으로 부팅 시점을 알 수 있는지는 시험 기기를 재부팅해 값이 바뀌는지로 확인합니다.

   ```
   ##-## ##:##:##.### 	Package [android] requested to [Enable]. 	Reason is SYSTEM_BOOT
   ```

3. **뼈대 기록을 고릅니다.** 연도가 있고 실제 시각 기준이 분명한 기록을 뼈대로 삼고 나머지를 붙입니다. 앱 사용 기록의 원본 이벤트 시각은 유닉스 밀리초라서 뼈대로 쓰기 좋고, 자세한 내용은 [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) 페이지에 있습니다.
4. **연도가 빠진 줄을 채웁니다.** logcat 기본 형식, `dumpsys batterystats` 의 기록 줄, `dumpsys wifi` 의 `rec[#]` 줄, `dumpsys bluetooth_manager` 의 `Enable log:` 줄은 모두 `MM-DD HH:MM:SS.mmm` 모양이라 연도가 없습니다. 수집한 시각이나 같은 사건이 연도와 함께 남은 다른 기록으로 연도를 채우고, 수집이 1월 초라면 12월 날짜 줄은 전년도일 수 있다는 점을 따져 봅니다. 채운 연도는 원래 값과 구별되게 "추정" 으로 표시합니다.
5. **같은 사건을 여러 기록에서 맞춰 봅니다.** 아래 "같은 사건이 남는 곳" 표의 짝을 찾아 두 기록의 시각 차이를 적어 두면, 한쪽 기록만 있는 구간에서 시각을 얼마나 믿을 수 있는지 추정할 수 있습니다.
6. **기록마다 보관 범위를 표시합니다.** logcat 은 main·system·crash·radio·events 버퍼를 돌려 쓰는 순환 버퍼이고 [2], 앱 사용 기록의 이벤트는 며칠만 남습니다([앱 사용 기록](../../../02-artifacts/app-usage/usagestats/index.md) 참고). 어떤 기록이 비어 있는 구간이 보관 범위 밖이라면 "그때 아무 일도 없었다" 는 뜻이 아닙니다.
7. **시계가 바뀐 구간을 따로 표시합니다.** 변경 시점을 찾는 방법은 [시각 조작 흔적](time-manipulation.md) 에 있고, 그 앞뒤 구간의 실제 시각 기록은 따로 묶어 순서를 다시 확인합니다.

## 같은 사건이 남는 곳

필드 이름으로 짝을 지은 표입니다. 짝끼리 시각이 실제로 얼마나 맞는지는 실제 기기로 확인하고, 필드마다 무엇을 사건으로 치는지도 조금씩 다를 수 있어서 같은 밀리초를 기대하지 않습니다.

| 사건 | 앱 사용 기록 (`dumpsys usagestats`) | 다른 기록 |
|---|---|---|
| 화면 켜짐·꺼짐 | `SCREEN_INTERACTIVE`, `SCREEN_NON_INTERACTIVE` | `dumpsys batterystats` 의 `+screen`·`-screen`, `screenwake=`, `display_state_changed=`, `dumpsys wifi` 의 `CMD_SCREEN_STATE_CHANGED` |
| 잠금 화면 | `KEYGUARD_SHOWN`, `KEYGUARD_HIDDEN` | 같은 시각의 다른 기록을 실제 기기에서 찾아 확인 |
| 알림 | `NOTIFICATION_INTERRUPTION`, `NOTIFICATION_SEEN` | `dumpsys notification` 의 `mCreationTimeMs`, `mUpdateTimeMs` 등 |

알림 쪽은 `dumpsys notification` 의 시각 필드에 `+####` 오프셋이 함께 찍혀서 시간대가 분명하고, 앱 사용 기록 쪽은 원본이 유닉스 밀리초라서 두 기록을 맞추면 서로의 시간대 해석을 검산할 수 있습니다. 각 기록의 뜻은 [배터리 사용 기록 (batterystats)](../../../02-artifacts/app-usage/batterystats.md), [알림 기록 (Notification History)](../../../02-artifacts/app-usage/notification-history.md), [와이파이 설정과 접속 기록 (WifiConfigStore)](../../../02-artifacts/network/wifi.md) 페이지에 있습니다.

## 도구

공개 도구 ALEAPP 는 기록마다 시각을 UTC 로 맞춘 뒤 지정한 시간대로 보여 주고, 그 변환 함수는 [시각 정규화](time-normalization.md) 페이지에 정리했습니다.

도구와 상관없이 엮은 결과는 한 표에 모읍니다. 열은 UTC 시각, 원래 표기, 기록 출처, 시계 종류(실제 시각·부팅 기준), 부팅 구간 번호, 연도를 채웠는지 여부, 시계 변경 구간 여부 정도면 나중에 순서를 다시 검토할 때 따라갈 수 있습니다.

## 함정과 한계

시계가 바뀐 구간에서는 UTC 로 옮긴 값의 순서가 실제 일어난 순서와 다를 수 있고 [1], 이 경우 순서를 뒷받침하는 근거는 같은 부팅 안의 부팅 기준 값뿐입니다. 부팅 기준 값이 없는 기록은 그 구간에서 순서를 확정하지 못합니다.

연도를 채운 줄은 추정이 섞인 값이라서, 연도가 바뀌는 무렵의 기록이나 수집보다 오래된 기록에서는 틀릴 수 있습니다. 기록끼리 실제로 몇 초씩 어긋나는지와 삼성 One UI 가 기록 형식을 AOSP 와 다르게 바꿨는지는 기기마다 다를 수 있어 실제 기기로 확인합니다.

## 결과를 어떻게 해석하나

엮은 타임라인이 보여 주는 순서는 근거에 따라 무게가 다릅니다. 같은 부팅 안에서 시계 변경이 없는 구간의 순서는 믿을 만하지만, 서로 다른 기록 사이의 앞뒤는 짝 사건으로 확인한 시각 차이보다 가까우면 단정하지 않습니다. 보고서에는 순서를 뒷받침한 기록과 그 한계를 함께 적습니다.

> (앱) 의 `ACTIVITY_RESUMED` 기록은 (시각) UTC 이고, `dumpsys batterystats` 의 `-screen` 기록은 (시각) UTC 입니다. 두 기록은 같은 부팅 구간에 있고 그 사이 시계 변경 흔적은 없었습니다. batterystats 기록의 연도는 수집 시각으로 채운 추정값입니다.

보고서 전체의 틀은 [포렌식 보고서](../../reporting/forensic-report.md) 페이지에 있습니다.

## 참고 문헌

1. SystemClock.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/os/SystemClock.java
2. Logcat command-line tool — Android Developers, https://developer.android.com/tools/logcat
