---
title: "폰 사용 시간 재구성"
parent: "시나리오 · 행위 재구성"
nav_order: 1610
---

# 폰 사용 시간 재구성 (Usage Time)

## 조사 질문

"그날 밤 11시부터 새벽 1시 사이에 이 폰을 쓰고 있었나", "운전하던 그 몇 분 동안 화면이 켜져 있었고 잠금이 풀려 있었나" 같은 질문에 답하는 흐름입니다. 앱 하나를 언제 썼는지는 [어떤 앱을 언제 썼나](app-usage.md) 에서 다루고, 이 페이지는 폰 전체를 놓고 화면이 켜져 있고 잠금이 풀려 사람이 조작할 수 있던 시간대를 찾는 데 집중합니다.

기록은 화면이 켜졌는지, 잠금 화면이 걷혔는지, 어떤 앱 화면이 앞에 있었는지까지 알려 주지만, 그 시간에 누가 화면을 보고 있었는지는 알려 주지 않습니다. 사람을 가리는 문제는 [그 시각에 폰을 쓴 사람이 누구인가](user-attribution.md) 에서 이어 갑니다.

## 먼저 확인할 것

- **OS 버전과 제조사** — 이 페이지의 파일 위치와 보관 기간은 현행 AOSP 기준이라서, 검체의 Android 버전과 One UI 같은 제조사 버전을 먼저 적어 둡니다.
- **시간대와 시각 변경** — 앱 사용 기록(usagestats)의 이벤트 시각은 `System.currentTimeMillis()` 와 같은 기준의 유닉스 밀리초라서 기기 벽시계를 그대로 따릅니다 [1]. 현지 시각으로 바꾸려면 기기 시간대가 필요하고, 사용자가 시각을 바꾸면 그 값이 그대로 기록에 들어갑니다. 시간대는 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md), 값 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 봅니다.
- **사용자와 프로필** — usagestats 파일은 `*/system_ce/*/usagestats*` 처럼 사용자별 경로에 쌓이고, 공개 도구 ALEAPP 도 출력을 사용자 칸으로 나눕니다 [3]. 기기에 보안 폴더나 작업 프로필이 있으면 어느 사용자 ID 의 기록을 보는지부터 정합니다([사용자와 프로필](../../02-artifacts/system-account/users-profiles.md)).
- **수집 범위** — `dumpsys usagestats` 는 메모리에 있는 상태를, 저장된 파일은 디스크에 기록된 상태를 보여 주어 둘의 범위가 다릅니다. `dumpsys usagestats` 이벤트 목록은 "Last ## hour events" 머리줄 아래 최근 몇 시간치만 나옵니다. 며칠 전 시간대를 물으면 `/data/system_ce/` 아래 파일이 있어야 하므로 확보 방식을 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 먼저 정합니다. `dumpsys batterystats` 를 받을 때는 `--reset` 같은 옵션을 붙이지 않고 그대로 받습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | usagestats 화면·잠금 이벤트 (`SCREEN_INTERACTIVE`·`SCREEN_NON_INTERACTIVE`·`KEYGUARD_SHOWN`·`KEYGUARD_HIDDEN`) | 화면이 켜져 조작할 수 있던 구간, 잠금 화면이 걷혀 있던 구간 | [앱 사용 기록](../../02-artifacts/app-usage/usagestats/index.md) |
| 2 | usagestats 앱 이벤트 (`ACTIVITY_RESUMED`·`ACTIVITY_PAUSED`·`ACTIVITY_STOPPED`·`USER_INTERACTION`·`NOTIFICATION_SEEN`) | 구간 안에서 앞에 있던 앱 화면, 앱과 상호작용하거나 알림을 본 흔적 | [앱 사용 기록](../../02-artifacts/app-usage/usagestats/index.md) |
| 3 | usagestats 앱별 누적 통계 | 앱마다 쓴 시간·보인 시간의 합계와 마지막 사용 시각 | [앱 사용 기록](../../02-artifacts/app-usage/usagestats/index.md) |
| 4 | 디지털 웰빙 `app_usage` DB | usagestats 와 같은 번호 체계로 남은 이벤트 사본 | [디지털 웰빙](../../02-artifacts/app-usage/digital-wellbeing.md) |
| 5 | `dumpsys batterystats` 의 Battery History | 화면 켜짐·꺼짐, 화면 깨움, 밝기 같은 상태 변화 줄 | [배터리 사용 기록](../../02-artifacts/app-usage/batterystats.md) |

기록마다 확인된 범위가 달라 아래처럼 나눠 적습니다.

| 기록 | 확인된 범위 | 위치·비고 |
|---|---|---|
| usagestats 파일 | ALEAPP 시험 자료가 Android 10~16 [3] | 옛 위치 `*/system/usagestats/*`, 현행 위치 `*/system_ce/*/usagestats*` [3]. 두 위치가 갈린 버전은 공개 자료가 없습니다 |
| usagestats 보관 기간 | 현행 AOSP 기준 [4] | daily 10일, weekly 4주, monthly 6개월, yearly 2년보다 오래된 파일을 지우고, 구간별 파일 수 한도는 100·50·12·10개입니다 |
| Google 디지털 웰빙 | ALEAPP 시험 자료가 Android 13~16 [2] | `*/com.google.android.apps.wellbeing/databases/app_usage*`. 보관 기간은 공개 자료가 없습니다 |
| 삼성 기기 | | `dumpsys package` 의 Known Packages 에서 "Wellbeing:" 값이 none 일 수 있습니다. 삼성 쪽 사용 시간 앱의 DB 경로와 구조는 공개 자료가 없어 검체에서 확인합니다 |

## 분석 흐름

1. **시각의 기준을 먼저 정합니다.** 기기 시간대를 적고, 기기 시각이 옮겨진 흔적이 있는지 봅니다. 기기에 따라 `dumpsys usagestats` 에 "UsageStats RollOver history :" 절이 있고, 그 안에 `Time changed. actualSystemTime:... expectedSystemTime:... actualRealtime:...` 모양의 줄이 남습니다. 현행 AOSP 의 UsageStatsService 에는 `actualSystemTime`·`expectedSystemTime` 이라는 변수로 시각 변경을 보정하는 코드가 있지만 이 절을 찍는 문자열은 없어서 [5], 제조사가 더한 출력일 가능성이 있습니다. 시각 변경을 따지는 방법은 [증거를 없애려 했나](anti-forensics/index.md) 묶음에 있습니다.

2. **화면이 켜진 구간을 찾습니다.** `SCREEN_INTERACTIVE`(15)는 화면이 켜져 사용자와 상호작용할 수 있게 된 때이고, `SCREEN_NON_INTERACTIVE`(16)는 화면이 완전히 꺼지거나 앰비언트 디스플레이(ambient display)처럼 상호작용 없이만 켜진 상태가 된 때입니다 [1]. 둘을 짝지으면 "화면을 조작할 수 있던 구간" 이 나옵니다. `dumpsys usagestats` 에서 이 줄은 `time="..." type=SCREEN_INTERACTIVE package=... flags=...` 모양이고, 두 이벤트는 보통 거의 짝을 이룹니다. 짝이 맞지 않는 끝 한 건은 기록 범위의 처음이나 끝에 걸린 구간일 수 있습니다.

3. **잠금이 풀린 구간을 겹칩니다.** `KEYGUARD_HIDDEN`(18)은 잠금 화면이 숨겨진 때이고, 보통 사용자가 폰의 잠금을 풀 때 생깁니다. `KEYGUARD_SHOWN`(17)은 잠금 화면이 표시된 때입니다 [1]. `KEYGUARD_HIDDEN` 에서 다음 `KEYGUARD_SHOWN` 까지를 잠금이 풀린 구간으로 잡고 2단계의 화면 구간 위에 겹칩니다.

4. **앱 화면 구간을 채웁니다.** `ACTIVITY_RESUMED`(1)는 앱 화면이 앞으로 나온 때, `ACTIVITY_PAUSED`(2)는 뒤로 간 때, `ACTIVITY_STOPPED`(23)는 화면에서 보이지 않게 된 때입니다 [1]. `dumpsys usagestats` 에서 이 줄에는 `package`, `class`, `instanceId`, `taskRootPackage`, `taskRootClass`, `flags` 칸이 있고, 세 이벤트는 비슷한 건수로 묶여 나옵니다. `USER_INTERACTION`(7)은 사용자가 그 앱과 어떤 식으로든 상호작용한 때, `NOTIFICATION_SEEN`(10)은 사용자가 알림을 본 때라서 구간 안에 사람이 조작한 점을 더 찍을 수 있습니다 [1]. 반면 `END_OF_DAY`(3)와 `CONTINUE_PREVIOUS_DAY`(4)는 통계가 넘어갈 때 생기는 넘김 이벤트이고, `FOREGROUND_SERVICE_START`(19)·`FOREGROUND_SERVICE_STOP`(20)은 포그라운드 서비스의 시작과 끝이라서 둘 다 사용자가 화면을 본 기록으로 세지 않습니다 [1].

5. **파일로 며칠 전까지 넓힙니다.** 저장된 usagestats 는 daily·weekly·monthly·yearly 구간 폴더로 나뉘고, 파일 이름은 그 구간의 시작 시각을 유닉스 밀리초로 적은 숫자입니다 [4]. 파일 안의 시각이 0 이상이면 파일 이름의 숫자에 더하고, 음수이면 그 크기를 그대로 절대 시각으로 씁니다. ALEAPP 는 결과를 UTC 로 보여 줍니다 [3]. 같은 기록이 여러 구간 폴더에 겹쳐 나올 수 있어 구간을 모두 더하면 시간이 부풀고 [3], 현행 AOSP 기준으로 daily 파일은 10일이 지나면 지워집니다 [4]. 현행 AOSP 는 개별 이벤트를 daily 통계에만 넣으니 [6], 10일보다 오래된 날에는 누적 통계만 남고 이벤트가 없어도 "그날은 쓰지 않았다" 로 읽지 않습니다.

6. **누적 통계로 합계를 맞춰 봅니다.** `dumpsys usagestats` 의 "In-memory daily stats" 절에서 앱 줄에는 `totalTimeUsed`, `lastTimeUsed`, `totalTimeVisible`, `lastTimeVisible`, `lastTimeComponentUsed`, `totalTimeFS` 칸이 있습니다. 파일에서는 ALEAPP 로 'Total Time Visible (ms)', 'Last Time Visible', 'App Launch Count' 같은 칸을 뽑을 수 있습니다 [3]. 2~4단계에서 찾은 구간의 길이를 더한 값이 이 합계와 크게 어긋나면 빠진 이벤트나 겹친 구간이 있는지 다시 봅니다. `totalTimeFS` 는 포그라운드 서비스가 쓰인 시간의 합계라서 [6] 사람이 화면을 본 시간과 섞지 않습니다.

7. **다른 기록으로 교차 확인합니다.** Google 디지털 웰빙이 있는 기기라면 `app_usage` DB 의 `events` 표(`timestamp`, `package_id`, `type`)와 `packages` 표를 이어 봅니다. `type` 번호는 usagestats 와 같은 체계이고 `timestamp` 는 유닉스 밀리초입니다 [2]. 배터리 기록의 Battery History 줄은 `##-## ##:##:##.### ### (상태 변화)` 모양이고 `+screen`·`-screen`, `screenwake=`, `display_state_changed=`, `brightness=` 같은 표시가 붙습니다. 이 줄에는 연도가 없고 줄 앞 시각의 시계 기준은 공개 자료가 없으니, 같은 시각을 가리키는 usagestats 이벤트와 나란히 놓아 어긋남을 재는 데 씁니다.

8. **구간표로 정리합니다.** 시작·끝 시각(UTC 와 현지 시각), 근거 이벤트, 겹친 층(화면·잠금·앱)을 한 줄에 적고, 어느 층이 비어 있는지도 함께 남깁니다. 여러 기록을 한 시간 축에 놓는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

> 그림 자리: 가로 시간 축 위에 "화면 켜짐", "잠금 풀림", "앱 화면" 세 줄을 겹쳐 그리고, 세 줄이 모두 겹치는 부분만 "사용 구간" 으로 칠한 그림

## 흔한 오판

**`SCREEN_NON_INTERACTIVE` 를 "화면 꺼짐" 으로만 읽는 오판**이 흔합니다. 이 이벤트는 앰비언트 디스플레이처럼 화면이 켜져 있어도 상호작용할 수 없는 상태까지 포함합니다 [1].

**`KEYGUARD_HIDDEN` 을 "사람이 비밀번호를 입력했다" 로 읽는 것**도 지나칩니다. 이 이벤트는 "보통" 잠금을 풀 때 생길 뿐이고, 잠금 방식이 아예 없는 기기나 얼굴·신뢰 장치로 풀린 경우를 이 이벤트가 구분해 주지 않습니다 [1].

**넘김 이벤트를 앱을 열고 닫은 시각으로 세는 경우**가 있습니다. `END_OF_DAY` 와 `CONTINUE_PREVIOUS_DAY` 는 통계를 나누면서 생긴 경계라서 그 시각에 사용자가 한 일이 아닙니다 [1].

**1970년 근처 시각이 나오면** 파일 안의 상대 시각을 파일 이름의 구간 시작 시각에 더하지 않은 것이고, 음수 값을 다루는 방식은 도구마다 다를 수 있습니다 [3].

**기록이 없는 시간을 "쓰지 않은 시간" 으로 단정하는 것**도 조심합니다. `dumpsys` 는 최근 몇 시간치만 보여 주고, 파일은 보관 기간이 지나면 지워집니다 [4]. `dumpsys` 요약 출력에 `DEVICE_STARTUP`·`DEVICE_SHUTDOWN`·`USER_UNLOCKED` 가 보이지 않더라도 생략된 줄에 있을 수 있으므로, "그 기간에 재부팅이 없었다" 는 근거로 쓰지 않습니다.

**`dumpsys` 의 시각 문자열을 그대로 옮기는 경우**에도 주의합니다. `time` 값은 숫자가 아니라 기기 언어(한국어면 한글)가 섞인 날짜 문자열로 찍힐 수 있고, 어느 시간대로 표시한 값인지 출력에 드러나지 않습니다. 보고서의 시각은 파일의 유닉스 밀리초에서 다시 셈해 적습니다.

## 보고서 문장 예

기록이 말하는 만큼만 적고, 층마다 근거 이벤트를 밝힙니다.

| 쓰지 않을 문장 | 쓸 문장 |
|---|---|
| 피의자는 ○○시부터 ○○시까지 휴대폰을 사용했다. | 기기의 앱 사용 기록(usagestats)에 따르면, 기기 시각 기준 ○○일 ○○:○○(UTC ○○:○○)부터 ○○:○○까지 화면이 상호작용 가능한 상태였고(`SCREEN_INTERACTIVE`~`SCREEN_NON_INTERACTIVE`), 그 사이 ○○:○○에 잠금 화면이 숨겨진 기록(`KEYGUARD_HIDDEN`)이 있습니다. |
| 피의자가 운전 중 메신저를 썼다. | 같은 구간 안에 ○○ 앱 화면이 앞으로 나온 기록(`ACTIVITY_RESUMED`)과 뒤로 간 기록(`ACTIVITY_PAUSED`)이 있습니다. 이 기록은 그 시간에 앱 화면이 앞에 있었다는 사실을 보여 주며, 누가 화면을 보거나 조작했는지는 담지 않습니다. |
| 그날 밤에는 폰을 쓰지 않았다. | ○○일 ○○:○○~○○:○○에 해당하는 화면·잠금 이벤트는 확보한 기록에서 찾지 못했습니다. 확보한 기록의 범위는 ○○부터 ○○까지이고, 이 기록은 보관 기간이 지나면 지워집니다. |

보고서 전체의 틀은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 아티팩트 본문: [앱 사용 기록 (usagestats)](../../02-artifacts/app-usage/usagestats/index.md), [디지털 웰빙](../../02-artifacts/app-usage/digital-wellbeing.md), [배터리 사용 기록](../../02-artifacts/app-usage/batterystats.md), [dumpsys 출력](../../02-artifacts/logs/dumpsys.md)
- 시각 해석: [시각 값](../../01-foundations/value-decoding/time-values.md), [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md)
- 이어지는 시나리오: [어떤 앱을 언제 썼나](app-usage.md), [그 시각에 폰을 쓴 사람이 누구인가](user-attribution.md), [증거를 없애려 했나](anti-forensics/index.md)
- 기법: [타임라인 작성](../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. UsageEvents.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/app/usage/UsageEvents.java
2. ALEAPP wellbeing.py — abrignoni/ALEAPP (main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/wellbeing.py
3. ALEAPP usagestats.py — abrignoni/ALEAPP (main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/usagestats.py
4. UsageStatsDatabase.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsDatabase.java
5. UsageStatsService.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsService.java
6. UserUsageStatsService.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UserUsageStatsService.java
