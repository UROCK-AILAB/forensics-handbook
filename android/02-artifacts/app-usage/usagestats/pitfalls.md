---
title: "해석 함정"
parent: "앱 사용 기록"
grand_parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 480
---

# 해석 함정 (Pitfalls)

앱 사용 기록(usagestats)을 보고서에 옮길 때 자주 어긋나는 곳을 모았습니다. 소스로 확인한 동작은 현행 AOSP 기준(frameworks/base 의 main 가지)이고, 실제 폰에서 본 내용에는 확인 범위를 붙였습니다. 파일과 칸의 생김새는 [파일 구조](structure.md), 이벤트 번호의 뜻은 [이벤트 종류](event-types.md) 페이지에 있습니다.

## 한 줄 요약

usagestats 이벤트는 사용자의 조작과 시스템의 동작이 섞인 기기 시계 기준 기록이고 며칠만 남으며, 구간·조회 방법·저장 시점에 따라 빠지거나 겹치기 때문에 이벤트 이름과 시각의 기준을 확인한 만큼만 말합니다.

## 증거로서 의미

| 기록 | 말할 수 있는 것 | 말할 수 없는 것 |
|---|---|---|
| ACTIVITY_RESUMED·PAUSED·STOPPED | 그 시각(기기 시계 기준)에 그 패키지의 액티비티가 앞으로 나오고, 뒤로 가고, 화면에서 사라졌다는 시스템 기록 | 누가 조작했는지, 앱 안에서 무엇을 했는지 |
| SCREEN_INTERACTIVE·NON_INTERACTIVE | 화면이 완전히 켜진 시각과, 꺼지거나 ambient 상태가 된 시각 | 화면을 사람이 보고 있었는지 |
| KEYGUARD_SHOWN·HIDDEN | 잠금 화면이 나타나고 숨은 시각 | 잠금 해제가 있었다는 단정 |
| FOREGROUND_SERVICE_START·STOP, STANDBY_BUCKET_CHANGED | 앱의 서비스가 돌았거나 시스템이 앱의 대기 등급을 바꿨다는 기록 | 사용자가 그 앱을 화면에서 썼다는 것 |
| 기록이 없음 | — | 그 시간에 앱을 쓰지 않았다는 것 |

마지막 줄은 아래 "빠지거나 겹치는 기록" 절의 이유들 때문입니다. 누가 기기를 썼는지를 따지는 방법은 [그 시각에 폰을 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 시나리오를 봅니다.

## 시각 해석

파일 안의 시각 칸은 구간 시작(파일 이름)으로부터의 밀리초 차이라서, 파일 이름을 더하지 않고 그대로 유닉스 밀리초로 읽으면 1970년 근처 시각이 나옵니다 [4]. 차이값은 구간 시작보다 최대 1시간 앞선 음수일 수도 있고 [4], 도구마다 음수를 다루는 방식이 다를 수 있어서 음수가 나온 이벤트는 두 도구 이상으로 맞춰 봅니다. ALEAPP 의 음수 처리와 계산 예시는 [파일 구조](structure.md) 페이지에 있습니다.

파일 이름과 이벤트 시각은 모두 기기의 벽시계(System.currentTimeMillis)를 따르고 [1], 사용자가 기기 시각을 바꾸면 기록에도 그대로 반영됩니다. 서비스는 실제 시각과 기대한 시각이 2초(TIME_CHANGE_THRESHOLD_MILLIS)보다 벌어지면 시각이 바뀐 것으로 보고 `Time changed in by ... seconds` 로그를 남긴 다음 기준 시각을 다시 잡습니다 [2]. 이때 이미 저장된 파일과 이벤트를 어떻게 다루는지는 확인하지 못했습니다. 실제 폰의 `dumpsys usagestats` 출력에서는 "UsageStats RollOver history" 절에 `Time changed. actualSystemTime:... expectedSystemTime:...` 줄이 5건 있었고, 시각 변경의 흔적을 이 절에서 찾을 수 있습니다 (확인 범위: Android 16, One UI 8.5). 시각 조작을 의심하는 사건이라면 [시간대와 시각 설정](../../system-account/time-zone.md)과 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) 페이지를 함께 봅니다.

ALEAPP 는 절대 유닉스 밀리초로 바꾼 뒤 UTC 로 보여 주지만 [6], `dumpsys usagestats` 는 시각을 한글이 섞인 날짜 문자열로 찍었습니다 (확인 범위: Android 16, One UI 8.5). dumpsys 가 어느 시간대 기준으로 찍는지는 확인하지 못했으니, 두 출력을 나란히 놓을 때는 시간대를 먼저 맞춥니다. 밀리초 값을 바꾸는 법은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

## 이벤트 뜻을 넘겨짚는 함정

통계를 넘길(rollover) 때 앞에 있던 앱은 END_OF_DAY(3)와 CONTINUE_PREVIOUS_DAY(4)로, 돌던 서비스는 ROLLOVER_FOREGROUND_SERVICE(22)와 CONTINUING_FOREGROUND_SERVICE(21)로 기록되는데, 사용자가 그 시각에 앱을 열거나 닫은 것이 아닙니다 [1]. 구간 경계에 몰린 이벤트는 이 네 종류인지 먼저 봅니다.

1번과 2번은 새 이름(ACTIVITY_RESUMED·ACTIVITY_PAUSED)과 옛 이름(MOVE_TO_FOREGROUND·MOVE_TO_BACKGROUND)이 같은 번호라서 [1], 도구나 버전에 따라 이름이 달라도 같은 이벤트입니다. ACTIVITY_PAUSED 는 액티비티가 뒤로 간 것이고 화면에서 사라진 것은 ACTIVITY_STOPPED(23)라서 [1], 사용을 마친 시각을 PAUSED 하나로만 잡지 말고 같은 액티비티의 STOPPED 와 함께 봅니다.

SCREEN_NON_INTERACTIVE 에는 화면이 꺼진 경우뿐 아니라 ambient 상태(항상 켜진 화면 등)도 들어갑니다 [1]. KEYGUARD_HIDDEN 은 소스 설명이 "보통(typically)" 잠금 해제 때 생긴다고 적었을 뿐이라서 [1], 잠금 해제와 같다고 단정하지 않습니다.

FOREGROUND_SERVICE_START·STOP 은 앱의 서비스가 돈 기록이지 사용자가 화면에서 앱을 쓴 기록이 아닙니다 [1]. 실제 폰의 최근 이벤트 목록에서도 이 두 종류가 수백 건씩 나왔습니다 (확인 범위: Android 16, One UI 8.5). STANDBY_BUCKET_CHANGED 도 시스템이 앱의 대기 등급을 바꾼 기록이고, 이유 값에는 PREDICTED, TIMEOUT, FORCED_BY_SYSTEM 같은 시스템 쪽 이유가 있습니다 [5].

## 빠지거나 겹치는 기록

이벤트는 시스템이 며칠만 보관하고("Events are only kept by the system for a few days.") [5], 구간 파일도 구간마다 정해진 기간이 지나면 지웁니다(기준은 [파일 구조](structure.md) 페이지) [3]. 개별 이벤트가 담긴 구간 파일이 지워지면 그 이벤트도 함께 사라집니다. 주·월·연 파일에도 개별 이벤트가 담기는지는 확인하지 못했으니, 오래된 기간에 누적 통계만 남는다고 보고서에 단정하지 않습니다.

같은 사용 기록이 daily·weekly·monthly·yearly 여러 구간에 겹쳐 나오고 [6], 구간을 가리지 않고 더하면 사용 시간을 여러 번 세게 됩니다. 사용 시간을 합칠 때는 한 구간만 고릅니다.

서비스는 정해진 주기마다 파일에 쓰고 정상 종료(DEVICE_SHUTDOWN)나 사용자 중지(USER_STOPPED) 때도 쓰지만 [2], 기기가 갑자기 꺼질 때는 쓸 기회가 없습니다. 그래서 배터리가 빠지는 식으로 기기가 갑자기 꺼지면 마지막 저장 뒤의 이벤트가 파일에 없을 수 있습니다. 첫 잠금 해제 전에 생긴 이벤트는 메모리나 `/data/system_de/<사용자ID>/usagestats/` 의 `pendingevents_` 파일에만 있을 수 있고, 잠금 해제 때 합친 뒤 이 폴더를 지웁니다 [2]. Android 11(R)부터는 사용자가 잠금 해제되지 않은 상태에서 API 로 조회하면 결과가 null 입니다 [5].

버전 5 파일은 `mappings` 파일이 있어야 패키지·클래스 이름을 되살릴 수 있고, 구간 파일만 뽑으면 이름 대신 번호만 남습니다 [3][6]. 형식 버전을 올릴 때 이전 파일이 `backups/` 아래에 남을 수 있어 업그레이드 이전 기간 기록의 출처가 될 수 있지만 [3], 업그레이드 뒤에도 계속 남는지는 확인하지 못했습니다. 예전 경로(`/data/system/usagestats/<사용자ID>/`)의 기록은 새 경로로 옮긴 뒤 지우니 [2], 두 경로에 같은 기록이 함께 있다고 기대하지 않습니다. `/data/system/usagestats/` 폴더 자체는 공용 파일(`globalcomponentusage`)을 두는 곳으로 계속 쓰입니다 [2].

제3자 앱이나 API 로 받은 결과는 호출한 앱에 따라 SHORTCUT_INVOCATION·LOCUS_ID_SET 이벤트가 빠지거나 알림 채널 ID·인스턴트 앱 이름이 가려질 수 있습니다 [1][2]. 가림 옵션은 [이벤트 종류](event-types.md) 페이지에 정리했습니다. `dumpsys usagestats` 는 서비스의 메모리 상태를 보여 주고 이벤트 목록도 "Last ## hour events" 처럼 최근 몇 시간만 담아서, 파일에 저장된 내용과 범위가 다릅니다 (확인 범위: Android 16, One UI 8.5).

## 제조사 차이

| 항목 | 현행 AOSP | Android 16, One UI 8.5 관찰 |
|---|---|---|
| 보관 한도와 저장 주기 | [파일 구조](structure.md) 페이지의 값 | 삼성이 바꿨는지 확인하지 못함 |
| dumpsys 의 "UsageStats RollOver history" 절 | 소스에서 확인하지 못함 | 있음 |
| dumpsys 의 mDumpInitLastTimeSaved·mDumpInitEndTime 줄 | 소스에서 확인하지 못함 | 있음 |

AOSP 소스에서 찾지 못한 절이 dumpsys 에 보인다는 점에서 제조사가 덧붙인 부분이 있을 수 있고, 다른 제조사 기기라면 출력 모양부터 다시 확인합니다.

## 보고서 문장 예

기록이 말하는 만큼만 씁니다. "피의자가 이 시각에 앱을 열었다" 는 기록보다 많이 말하는 문장입니다. 아래처럼 씁니다.

> usagestats 일간 파일에 기기 시계 기준 (시각) UTC 에 (패키지) 의 ACTIVITY_RESUMED 이벤트가 있고, 같은 액티비티의 ACTIVITY_STOPPED 이벤트가 (시각) UTC 에 있습니다. 이 두 기록 사이에 그 앱의 액티비티가 화면에 나와 있었다고 볼 수 있지만, 누가 조작했는지는 이 기록만으로 알 수 없습니다.

## 교차 검증

- 알림 이벤트는 [알림 기록 (Notification History)](../notification-history.md) 과 맞춰 봅니다.
- 화면 상태와 포그라운드 서비스는 [배터리 사용 기록 (batterystats)](../batterystats.md) 과 맞춰 봅니다.
- 마지막으로 연 앱 화면은 [최근 앱 화면 (Recents·Snapshots)](../recents-snapshots.md) 과 맞춰 봅니다.
- 사용 시간 수치는 [디지털 웰빙 (Digital Wellbeing)](../digital-wellbeing.md) 과 나란히 보되, 두 수치가 어떻게 다른지는 출처로 확인하지 못했습니다. 관찰한 폰의 `dumpsys package` 에서는 "Wellbeing:" 역할 항목 값이 none 이었습니다 (확인 범위: Android 16, One UI 8.5).
- 여러 아티팩트를 한 시간 축에 놓는 방법은 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md), 사용 행위를 재구성하는 흐름은 [어떤 앱을 언제 썼나](../../../04-scenarios/activity/app-usage.md) 와 [폰 사용 시간 재구성](../../../04-scenarios/activity/usage-time.md) 시나리오에 있습니다.

## 참고 문헌

1. UsageEvents.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/app/usage/UsageEvents.java
2. UsageStatsService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsService.java
3. UsageStatsDatabase.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsDatabase.java
4. UsageStatsProtoV2.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsProtoV2.java
5. UsageStatsManager.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/app/usage/UsageStatsManager.java
6. ALEAPP usagestats.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/usagestats.py
