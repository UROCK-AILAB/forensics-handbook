---
title: "시각 바꾸기"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 1680
---

# 시각 바꾸기 (Time Change)

기기 시각이 바뀐 적이 있는지, 바뀌었다면 기록의 시각을 어떻게 읽어야 하는지를 정리합니다. 기기 시각을 손으로 바꾸면 그 뒤에 생긴 기록은 모두 틀린 시각을 달게 되고, 시스템이 이미 저장된 기록의 이름까지 옮기는 경우가 있어서 타임라인 전체를 다시 따져 봐야 합니다. 소스 동작은 현행 AOSP(frameworks/base 의 main 가지) 기준입니다.

## 조사 질문

"수집한 기록의 시각을 기기 시계 그대로 믿어도 되는가, 사건 무렵 기기 시각을 자동이 아닌 손으로 맞춰 두었거나 크게 옮긴 흔적이 있는가" 를 묻습니다. 시각 조작 자체를 밝히는 일뿐만 아니라, 다른 모든 시나리오의 시각을 보고서에 옮기기 전에 거치는 점검까지 다룹니다.

## 먼저 확인할 것

- **자동 시각 설정**: 시각은 자동으로 맞추거나 사용자가 직접 정할 수 있고 [3], `settings global` 에는 `auto_time`, `auto_time_zone`, `auto_time_zone_explicit` 키가 있습니다. 이 값은 수집 시점의 상태일 뿐 사건 당시 상태가 아니라는 점도 함께 적습니다.
- **시간대**: 시간대 설정은 [시간대와 시각 설정](../../../02-artifacts/system-account/time-zone.md) 에서 봅니다. `settings global` 키 목록에 `time_zone` 키가 없을 수 있고, 삼성 기기의 `settings system` 에는 삼성이 추가한 것으로 보이는 `TIME_DIFFERENCE`, `homecity_timezone` 키가 있을 수 있습니다. 두 키의 뜻은 공개된 설명이 없습니다.
- **수집 시각**: 수집할 때 기기 시각과 믿을 만한 기준 시각을 함께 적어 두면, 수집 시점의 차이를 기준으로 삼을 수 있습니다. 수집 절차는 [조사 절차](../../../03-techniques/acquisition/investigation-process.md) 에 있습니다.

## 시각을 정하는 방식

자동 시각의 출처는 네 가지이고, Android 버전에 따라 쓸 수 있는 출처와 설정 이름이 다릅니다 [3].

| 항목 | Android 버전 | 내용 |
|---|---|---|
| 네트워크(NTP), 통신사(NITZ) 출처 | — | 자동 시각 출처 |
| GNSS 출처, 외부(External) 출처 | 12 이상 | 외부 출처는 제조사가 붙이는 출처 |
| 설정 이름 "Use network-provided time" | 11 이하 | 끄면 사용자가 직접 시각을 정함 |
| 설정 이름 "Set time automatically" | 12 이상 | 끄면 사용자가 직접 시각을 정함 |
| time_detector 서비스 | 10 이상 | 자동 시각 감지를 맡음 |
| 자동 시간대 감지(통신사 NITZ) | — | 셀룰러 기기, 11 이하에서는 이 방식만 씀 |
| 자동 시간대 감지(위치) | 12 이상 | 위치 서비스가 켜져 있어야 함 |

time_detector 서비스의 상태는 제안을 받은 "certain" 과 제안이 없거나 오래된 "uncertain" 두 가지이고, time_zone_detector 서비스도 같은 두 상태를 씁니다 [3]. `adb shell cmd time_detector dump` 는 출처 우선순위, 자동 감지가 켜져 있는지, 시각 변경 기록(time change logs), 출처별 제안 이력을 보여 줍니다 [3]. 일반 권한으로 실행되는지는 실제 기기에서 확인합니다.

## usagestats 가 시각 변경을 다루는 방식

앱 사용 기록(usagestats) 서비스는 시각 변경을 스스로 알아채고 저장 파일의 이름까지 옮겨서, 시각 조작을 볼 때 따로 알아 둘 만합니다.

서비스는 `checkAndGetTimeLocked()` 에서 기대 시각을 "(지금 elapsedRealtime − 기준 elapsedRealtime) + 기준 시스템 시계(wall clock) 시각" 으로 셈하고, 실제 시스템 시계와 기대 시각의 차이가 2초(`TIME_CHANGE_THRESHOLD_MILLIS = 2 * 1000`)를 넘으면 시각이 바뀐 것으로 봅니다 [1][4]. 이 보정을 켤지는 시스템 속성 `persist.debug.time_correction` 으로 정하고 기본값은 true 입니다 [4]. 시각이 바뀌었다고 보면 `Time changed in by ... seconds` 로그를 남기고 `onTimeChanged()` 로 넘어가서, 캐시해 둔 이른 이벤트를 비우고, 현재 통계를 저장하고, 데이터베이스에 차이값을 넘긴 뒤 새 시각으로 현재 통계를 다시 엽니다 [1].

데이터베이스 쪽 `UsageStatsDatabase.onTimeChanged(차이)` 는 모든 통계 파일의 이름, 곧 구간 시작 유닉스 밀리초에 차이를 더해 이름을 바꾸고, 새 값이 0보다 작으면 그 파일을 지웁니다 [2]. 체크인 접미사(`CHECKED_IN_SUFFIX`)는 그대로 두고, 지운 파일 수와 옮긴 파일 수를 로그에 남깁니다(` files deleted: `, ` files moved: `) [2]. 시각을 바꾸면 이미 저장된 usagestats 파일의 이름도 같이 옮겨지니, 파일 이름만 보고 "그 시각에 기록됐다" 고 단정하지 않습니다(해석). 파일 이름과 시각 필드의 관계는 [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) 에 있습니다.

UsageStatsService.java 에는 `Intent.ACTION_TIME_CHANGED` 방송을 직접 받는 코드가 없습니다 [4].

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 자동 시각·시간대 설정 키 | 수집 시점의 자동 설정 상태 | [설정 값](../../../02-artifacts/system-account/settings.md) |
| 2 | `dumpsys usagestats` 의 "UsageStats RollOver history" 절 | 시각 변경으로 본 기록 | [앱 사용 기록](../../../02-artifacts/app-usage/usagestats/index.md) |
| 3 | logcat | usagestats 의 시각 변경 로그 줄(버퍼에 남았을 때) | [logcat](../../../02-artifacts/logs/logcat.md) |
| 4 | batterystats 의 Battery History | 기기 시계 기준 기록 줄 | [배터리 사용 기록](../../../02-artifacts/app-usage/batterystats.md) |
| 5 | 와이파이·블루투스 기록 | 같은 모양의 기기 시계 기준 기록 | [와이파이](../../../02-artifacts/network/wifi.md), [블루투스](../../../02-artifacts/network/bluetooth.md) |
| 6 | 기기 밖 시각이 붙은 기록 | 서버·통신사·상대방 기기 시각과 비교 | [클라우드 데이터](../../../03-techniques/acquisition/cloud-data.md) |

### adb 일반 권한으로 보이는 줄

기기에 따라 `dumpsys usagestats` 에 "UsageStats RollOver history :" 절이 있고, 그 안에 아래 모양의 줄이 있습니다.

```
User[#] Time changed. actualSystemTime:... expectedSystemTime:... actualRealtime:...          (5건)
User[#] rolloverStats by event Type:#/ init elapsed time:/ timeStamp:/ ExpiryDate:/ realTime:/ systemTime:
```

`Time changed. actualSystemTime` 줄의 모양은 AOSP 소스의 로그 문자열 `Time changed in by ... seconds` 와 다르고, 소스 로그 문자열에는 actualSystemTime 같은 필드 이름이 없습니다 [1]. 다만 `actualSystemTime`, `expectedSystemTime`, `actualRealtime` 은 AOSP `checkAndGetTimeLocked()` 안의 변수 이름과 같아서 [1], 같은 판정 결과를 제조사가 따로 적은 기록일 가능성이 있습니다. 이 줄은 실제 시스템 시계(actualSystemTime)와 서비스가 기대한 시각(expectedSystemTime)을 나란히 적는 모양이라서, 값이 보이는 기기라면 두 값의 차이로 시각이 얼마나 옮겨졌는지를 추정할 수 있습니다(해석). 이 절이 몇 건까지, 언제까지 남는지는 실제 기기로 확인해야 합니다.

logcat 한 줄은 `월-일 시:분:초.밀리초 PID TID 등급 태그: 내용` 모양이고, 버퍼는 main, system, events, crash, radio 등이 있습니다. `dumpsys batterystats` 의 기록 줄, `dumpsys wifi` 의 `rec[#]: time=...` 줄, `dumpsys bluetooth_manager` 의 기록 줄도 같은 "월-일 시:분:초.밀리초" 모양입니다. 연도가 없어서 해를 넘는 판단은 다른 기록과 맞춰야 합니다(해석). batterystats 에는 "Battery History" 첫 줄 가까이에 `RESET:TIME:` 줄이 있습니다. 시각이 바뀔 때 따로 줄이 생기는지는 실제 기기에서 확인합니다.

## 분석 흐름

1. 수집 시점의 기기 시각과 기준 시각의 차이, 자동 시각·시간대 설정 키 값을 적습니다.
2. `dumpsys usagestats` 의 "UsageStats RollOver history" 절에서 `Time changed.` 줄을 모두 옮겨 적고, 두 시각의 차이를 셈합니다.
3. logcat 에 usagestats 의 시각 변경 로그가 남았는지 찾습니다. 로그가 없다고 해서 변경이 없었다고 보지 않습니다.
4. usagestats 구간 파일의 이름 순서와 파일 안 이벤트 시각의 흐름을 봅니다. 파일 이름이 한꺼번에 옮겨졌을 수 있다는 점을 전제로 두고, 순서가 뒤집히거나 겹치는 곳을 표시합니다(해석).
5. 기기 시계로 찍힌 기록(사진 EXIF, 메시지, 와이파이 접속)과 기기 밖 시각(서버 수신 시각, 통신사 기록, 상대방 기기)을 한 표에 놓아 벌어진 구간을 찾습니다. 여러 출처의 시각을 한 기준으로 맞추는 법은 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 에 있습니다.
6. 벌어진 구간이 있으면 그 구간의 기록에 "기기 시계 기준, 조정 전" 을 붙여 보고서에 옮깁니다.

## 흔한 오판

**시각 변경 기록을 사용자가 손으로 바꾼 흔적으로 읽는 경우.** 자동 시각도 NTP·NITZ·GNSS 제안을 받아 시각을 옮기고 [3], usagestats 는 2초를 조금만 넘게 벌어져도 시각이 바뀐 것으로 봅니다 [4]. `Time changed.` 줄이 있다는 것만으로 사람이 바꿨다고 적지 않고, 차이의 크기와 자동 설정 상태를 함께 봅니다.

**수집 시점의 설정을 사건 당시 설정으로 보는 경우.** `auto_time` 같은 키 값은 수집할 때의 상태이고, 사건 무렵에도 같았다는 근거가 되지 못합니다.

**usagestats 파일 이름을 기록 시각으로 보는 경우.** 시각이 바뀌면 파일 이름에 차이를 더해 옮기고, 0보다 작아진 파일은 지웁니다 [2]. 파일이 없다는 것도 기록이 없었다는 뜻이 아닐 수 있습니다.

**연도 없는 로그 시각에 수집 연도를 붙이는 경우.** logcat·batterystats·wifi 기록 줄에는 연도가 없어서, 해가 바뀐 무렵의 기록이나 시각을 크게 옮긴 기록은 다른 기록으로 연도를 맞춥니다.

## 보고서 문장 예

> 수집 당시 기기 시계는 기준 시각보다 (차이) 앞서 있었습니다. `dumpsys usagestats` 의 "UsageStats RollOver history" 절에는 시각 변경 기록이 (개수) 건 있고, 그중 한 건은 실제 시각과 기대 시각의 차이가 (차이) 입니다. 이 기록은 그 무렵 기기 시각이 옮겨졌다는 것을 보여 주지만, 사용자가 직접 바꿨는지 자동 시각 조정이었는지는 이 기록만으로 가릴 수 없습니다. 따라서 이 기기에서 나온 (시각) 부터 (시각) 까지의 기록 시각은 기기 시계 기준 값으로만 적었습니다.

## 함께 볼 페이지

- 이 묶음 전체의 길잡이는 [증거를 없애려 했나](index.md) 입니다. 초기화 사유 시각과 휴지통 파일 이름의 만료 시각도 기기 시스템 시계로 만든 값이라서, [초기화](factory-reset.md) 와 [메시지·사진 지우기](content-deletion.md) 를 볼 때 이 페이지의 점검을 먼저 거칩니다.
- 시각 값의 형식은 [시각 값](../../../01-foundations/value-decoding/time-values.md), 폰 사용 시간을 재구성하는 흐름은 [폰 사용 시간 재구성](../usage-time.md) 에 있습니다.

## 참고 문헌

1. UserUsageStatsService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UserUsageStatsService.java
2. UsageStatsDatabase.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsDatabase.java
3. Time and time zone detection — Android Open Source Project, https://source.android.com/docs/core/connect/time
4. UsageStatsService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsService.java
