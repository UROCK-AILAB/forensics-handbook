---
title: "어떤 앱을 언제 썼나"
parent: "시나리오 · 행위 재구성"
nav_order: 1570
---

# 어떤 앱을 언제 썼나 (App Usage)

Android 폰에서 어떤 앱이 언제 화면 앞에 나와 있었는지, 설치만 된 앱인지 실제로 쓴 앱인지를 묻는 조사를 다룹니다. 설치된 앱 목록으로 그 시각에 앱이 기기에 있었는지 먼저 확인하고, 앱 사용 기록(usagestats)의 이벤트와 누적 통계로 앱 화면이 앞에 있던 구간과 사용자가 조작한 시각을 뽑습니다. 그다음 디지털 웰빙과 삼성 Rubin, 최근 앱 목록, 알림 기록으로 같은 시각을 교차 확인합니다.

## 조사 질문

"사건 시각에 이 메신저 화면이 떠 있었나", "지도 앱을 마지막으로 연 때가 언제인가", "이 앱은 설치만 돼 있었나, 실제로 썼나" 같은 질문에 답하는 흐름입니다. 폰 전체를 놓고 화면이 켜져 있고 잠금이 풀려 있던 시간대를 찾는 일은 [폰 사용 시간 재구성](usage-time.md) 에서 다루고, 이 페이지는 그 시간대 안에서 앱 하나하나가 언제 앞에 나와 있었는지를 좁히는 데 집중합니다.

기록은 "이 앱의 화면이 이 시각에 앞으로 나왔다", "사용자가 이 앱과 상호작용했다" 까지 알려 주지만, 화면 안에서 무엇을 했는지와 누가 조작했는지는 알려 주지 않습니다. 앱 안에서 한 일은 각 앱의 데이터로, 사람은 [그 시각에 폰을 쓴 사람이 누구인가](user-attribution.md) 로 이어 갑니다.

## 먼저 확인할 것

- **OS 버전과 제조사** — 앱 사용 기록(usagestats)은 AOSP 에 있는 기록이라 대부분의 기기에 있지만, 사용 시간을 보여 주는 앱은 제조사마다 다릅니다. 삼성 기기에서는 삼성 디지털 웰빙과 삼성 맞춤 서비스 Rubin 이 같은 사건을 다르게 남길 수 있어서 [4], 분석 대상 기기가 어느 쪽인지부터 적어 둡니다.
- **시간대** — usagestats 의 이벤트 시각은 기기 시스템 시계를 따르는 유닉스 밀리초입니다. 시간대와 시각 변경을 먼저 보는 이유와 방법은 [폰 사용 시간 재구성](usage-time.md) 의 "먼저 확인할 것" 에 정리해 두었습니다.
- **사용자와 프로필** — usagestats 파일은 사용자별 경로(`*/system_ce/*/usagestats*`)에 쌓입니다 [3]. 보안 폴더나 작업 프로필의 앱은 다른 사용자 ID 아래에 기록이 남으니 [사용자와 프로필](../../02-artifacts/system-account/users-profiles.md) 을 먼저 봅니다.
- **수집 범위** — 조사 대상 앱이 설치 목록에 있는지, 사용 기록을 담은 파일까지 확보했는지, 아니면 `dumpsys` 출력만 있는지를 먼저 나눠 둡니다. `dumpsys usagestats` 는 "Last ## hour events" 머리줄 아래 최근 몇 시간치 이벤트만 보여 주므로, 며칠 전 사용을 물으려면 usagestats 파일이 있어야 합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 설치된 앱 (`packages.xml`, `dumpsys package`) | 앱이 기기에 있었는지, 언제 설치·갱신됐는지 | [설치된 앱](../../02-artifacts/app-usage/packages/index.md) |
| 2 | usagestats 앱 이벤트 | 앱 화면이 앞으로 나오고 뒤로 간 시각, 상호작용한 시각 | [앱 사용 기록](../../02-artifacts/app-usage/usagestats/index.md) |
| 3 | usagestats 앱별 누적 통계 | 앱마다 쓴 시간·보인 시간의 합계와 마지막 사용 시각 | [앱 사용 기록](../../02-artifacts/app-usage/usagestats/index.md) |
| 4 | 디지털 웰빙 (Google·삼성) | 제조사 쪽에 따로 남은 사용 이벤트 | [디지털 웰빙](../../02-artifacts/app-usage/digital-wellbeing.md) |
| 5 | 최근 앱 화면 (`recent_tasks`) | 최근 앱 목록에 남은 앱과 그 태스크가 마지막으로 앞에 있던 시각 | [최근 앱 화면](../../02-artifacts/app-usage/recents-snapshots.md) |
| 6 | 알림 기록, 배터리 사용 기록 | 앱이 알림을 올린 시각, 앱이 돌며 남긴 상태 변화 | [알림 기록](../../02-artifacts/app-usage/notification-history.md), [배터리 사용 기록](../../02-artifacts/app-usage/batterystats.md) |

기기에 따라 볼 곳이 달라지는 부분은 아래처럼 정리합니다.

| 기록 | Google·AOSP 기기 | 삼성 One UI | 비고 |
|---|---|---|---|
| usagestats | 현행 위치 `*/system_ce/*/usagestats*`, 옛 위치 `*/system/usagestats/*` [3] | 같은 AOSP 기록이 있고, `dumpsys usagestats` 로 이벤트 줄을 볼 수 있습니다 | 보관 기간은 daily 10일, weekly 4주, monthly 6개월, yearly 2년입니다 [2] |
| 디지털 웰빙 | Google 디지털 웰빙 `app_usage` DB | 삼성 디지털 웰빙 `dwbCommon.db` 의 `usageEvents` 표 [4] | 삼성 기기 settings system 에 `add_info_com_samsung_android_forest#screenTime` 키가 있을 수 있습니다 |
| 삼성 Rubin | 해당 없음 | Rubin 이 켜져 있으면 잠금 해제 이벤트가 `inferenceengine_logging.db` 의 `screen_state_log` 표에만 남은 사례가 있습니다 [4] | Galaxy S22(Android 15, One UI 7) 사례이고, 다른 판은 실제 기기에서 확인합니다 |
| 최근 앱 | `recent_tasks` 태스크 XML [5] | 최근 앱 화면은 삼성 런처(`com.sec.android.app.launcher`)가 맡습니다 | 삼성 런처가 `recent_tasks` 와 별도로 남기는 기록은 실제 기기로 확인해야 합니다 |

## 분석 흐름

1. **앱이 그 시각에 기기에 있었는지부터 봅니다.** [설치된 앱](../../02-artifacts/app-usage/packages/index.md) 에서 조사 대상 앱의 패키지 이름을 확인하고, `packages.xml` 의 `ut`(마지막 갱신 시각, `dumpsys package` 의 `lastUpdateTime=`)와 설치 시각 필드를 읽습니다 [6]. 지금 설치된 앱의 설치 시각은 그 설치본으로 앱을 쓸 수 있었던 때의 하한이고, 사용 기록이 그보다 앞서 있다면 지웠다가 다시 깔았을 가능성을 봅니다([증거를 없애려 했나](anti-forensics/index.md)). 앱 이름과 패키지 이름을 잇는 방법은 [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md) 에 있습니다.

2. **앱 화면 구간을 뽑습니다.** usagestats 이벤트 중 `ACTIVITY_RESUMED`(1)는 앱 화면이 앞으로 나온 때, `ACTIVITY_PAUSED`(2)는 뒤로 간 때, `ACTIVITY_STOPPED`(23)는 화면에서 보이지 않게 된 때입니다 [1]. 조사 대상 패키지의 `ACTIVITY_RESUMED` 에서 다음 `ACTIVITY_PAUSED` 까지를 한 구간으로 잡습니다. `dumpsys usagestats` 의 이벤트 줄은 `time="..." type=ACTIVITY_RESUMED package=... class=... instanceId=... taskRootPackage=... taskRootClass=... flags=...` 모양이고, 세 이벤트는 서로 비슷한 건수로 묶여 나옵니다. 필드 이름으로 짐작하면 `class` 는 앱 안의 화면을, `taskRootPackage` 는 그 화면이 속한 작업 흐름의 첫 앱을 가리키는 것으로 보입니다.

3. **구간 안에 사람이 조작한 점을 찍습니다.** `USER_INTERACTION`(7)은 사용자가 그 앱과 어떤 식으로든 상호작용한 때이고, `NOTIFICATION_SEEN`(10)은 사용자가 알림을 본 때입니다 [1]. 화면이 떠 있던 것과 사용자가 만진 것은 다른 사실이라서 두 층을 따로 적습니다. 이 밖에도 `SHORTCUT_INVOCATION`(`shortcutId=` 필드), `STANDBY_BUCKET_CHANGED`(`standbyBucket=`·`reason=` 필드), `NOTIFICATION_INTERRUPTION`(`channelId=` 필드) 같은 이벤트 종류가 나옵니다. 이 세 가지는 이름만 보고 뜻을 짐작하지 말고, 보고서에 원래 이름 그대로 옮깁니다.

4. **사용이 아닌 이벤트를 걸러 냅니다.** `FOREGROUND_SERVICE_START`(19)·`FOREGROUND_SERVICE_STOP`(20)은 포그라운드 서비스의 시작과 끝이고, `END_OF_DAY`(3)·`CONTINUE_PREVIOUS_DAY`(4)는 통계가 다음 구간으로 넘어갈 때 생기는 넘김 이벤트라서 사용자가 앱을 연 기록이 아닙니다 [1]. 사용 시간을 셀 때는 이 네 이벤트를 먼저 빼고 화면 이벤트만 남깁니다.

5. **누적 통계로 마지막 사용 시각을 확인합니다.** `dumpsys usagestats` 의 "In-memory daily stats" 절에서 앱 줄에는 `totalTimeUsed`, `lastTimeUsed`, `totalTimeVisible`, `lastTimeVisible`, `lastTimeComponentUsed` 같은 필드가 있습니다. 이벤트 파일이 보관 기간을 넘겨 지워진 날에는 이런 누적 값만 남을 수 있고, 개별 이벤트가 weekly 이상의 파일에도 담기는지는 실제 기기에서 확인합니다. 저장된 파일에서 시각을 셈하는 방법과 구간 폴더가 겹치는 문제는 [앱 사용 기록](../../02-artifacts/app-usage/usagestats/index.md) 에 있습니다 [2][3].

6. **삼성 기기라면 디지털 웰빙과 Rubin 을 함께 봅니다.** 삼성 디지털 웰빙의 `dwbCommon.db` 안 `usageEvents` 표에서 `eventType` 18 은 잠금 해제, 17 은 잠금, 27 은 기기 시작이고 [4], 이 번호는 usagestats 의 `KEYGUARD_HIDDEN`(18)·`KEYGUARD_SHOWN`(17)·`DEVICE_STARTUP`(27)과 같습니다 [1]. 해석에 영향을 주는 점이 세 가지 더 있습니다 [4]. Rubin 이 켜져 있으면 잠금 해제 이벤트가 `dwbCommon.db` 에 남지 않고 Rubin 의 `inferenceengine_logging.db` 안 `screen_state_log` 표(`screen_state`, `user_present`, `use_keyguard`, `time`, `time_string` 열)에만 남았고, 기록이 DB 에 곧바로 쓰이지 않고 1시간에서 12시간 넘게 늦게 쓰였으며, `BOOT_COMPLETED` 항목의 시각은 실제 부팅 시각이 아니라 재부팅 뒤 처음 잠금을 푼 시각이었습니다. 늦게 쓰는 동안 기록이 어디에 머무는지는 공개 자료가 없습니다 [4].

7. **최근 앱 목록과 알림으로 교차 확인합니다.** `recent_tasks` 의 태스크 XML 에는 `first_active_time`, `last_active_time`, `last_time_moved`, `calling_package`, `real_activity` 같은 속성이 있습니다 [5]. usagestats 의 마지막 `ACTIVITY_RESUMED` 와 이 태스크의 마지막 활성 시각이 가까운지 맞춰 보고, 알림을 올린 시각은 [알림 기록](../../02-artifacts/app-usage/notification-history.md) 에서 더합니다. 여러 기록을 한 축에 놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

> 그림 자리: 한 앱에 대해 "설치 시각" 을 왼쪽 끝에 두고, 그 뒤로 RESUMED~PAUSED 막대와 USER_INTERACTION 점, 포그라운드 서비스 구간(흐린 색)을 한 줄에 겹쳐 그린 그림

## 흔한 오판

**앱이 설치돼 있으니 썼다고 보는 오판**이 가장 흔합니다. 설치 기록은 앱이 기기에 있었다는 사실만 보여 주고, 사용은 usagestats 같은 사용 기록으로 따로 확인해야 합니다.

**포그라운드 서비스 구간을 화면 사용 시간으로 더하는 경우**가 있습니다. `FOREGROUND_SERVICE_START`·`STOP` 은 화면을 본 기록이 아닙니다 [1].

**`ACTIVITY_RESUMED` 를 "사용자가 앱을 열었다" 로 읽는 것**도 지나칩니다. 이벤트 줄에는 화면을 띄운 주체를 적는 필드가 없으므로, 앞뒤 이벤트와 `USER_INTERACTION` 을 함께 봅니다.

**한 기록에 없다고 사건이 없었다고 보는 것**도 조심합니다. 삼성 기기에서는 같은 잠금 해제가 디지털 웰빙에는 없고 Rubin 에만 남은 사례가 있고 [4], usagestats 파일은 보관 기간이 지나면 지워집니다 [2].

**삼성 디지털 웰빙의 시각을 사건 직후에 쓰인 값으로 믿는 것**도 위험합니다. 기록이 몇 시간 늦게 쓰인 사례가 있어서 [4], 기기를 확보한 시점이 사건 직후라면 마지막 몇 시간치가 아직 DB 에 없을 수 있습니다.

## 보고서 문장 예

| 쓰지 않을 문장 | 쓸 문장 |
|---|---|
| 피의자는 ○○시에 메신저를 사용했다. | 앱 사용 기록(usagestats)에 ○○일 ○○:○○(UTC ○○:○○) ○○ 앱 화면이 앞으로 나온 기록(`ACTIVITY_RESUMED`)과 ○○:○○ 뒤로 간 기록(`ACTIVITY_PAUSED`)이 있고, 그 사이 ○○:○○ 에 사용자가 이 앱과 상호작용한 기록(`USER_INTERACTION`)이 있습니다. |
| 피의자는 하루 3시간 동안 게임을 했다. | 앱 사용 기록의 ○○일 daily 통계에서 ○○ 앱의 화면에 보인 시간 합계(`totalTimeVisible`)는 ○○ 밀리초입니다. 이 값은 화면에 보인 시간이며, 사용자가 계속 조작했다는 뜻은 아닙니다. |
| 그 앱은 한 번도 쓰지 않았다. | 확보한 앱 사용 기록의 범위(○○~○○) 안에서 ○○ 앱의 화면 이벤트는 찾지 못했습니다. 이 기록은 보관 기간이 지나면 지워집니다. |

보고서 전체의 틀은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 아티팩트 본문: [설치된 앱](../../02-artifacts/app-usage/packages/index.md), [앱 사용 기록 (usagestats)](../../02-artifacts/app-usage/usagestats/index.md), [디지털 웰빙](../../02-artifacts/app-usage/digital-wellbeing.md), [최근 앱 화면](../../02-artifacts/app-usage/recents-snapshots.md), [알림 기록](../../02-artifacts/app-usage/notification-history.md), [배터리 사용 기록](../../02-artifacts/app-usage/batterystats.md), [dumpsys 출력](../../02-artifacts/logs/dumpsys.md)
- 이어지는 시나리오: [폰 사용 시간 재구성](usage-time.md), [그 시각에 폰을 쓴 사람이 누구인가](user-attribution.md), [증거를 없애려 했나](anti-forensics/index.md)
- 기법: [타임라인 작성](../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. UsageEvents.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/app/usage/UsageEvents.java
2. UsageStatsDatabase.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsDatabase.java
3. ALEAPP usagestats.py — abrignoni/ALEAPP (main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/usagestats.py
4. Josh Hickman, "(Not) Strange Bedfellows – Samsung's Rubin & Digital Wellbeing", The Binary Hick, 2025-08-06 — https://thebinaryhick.blog/2025/08/06/not-strange-bedfellows-samsungs-rubin-digital-wellbeing/
5. ALEAPP recentactivity.py — abrignoni/ALEAPP (main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/recentactivity.py
6. Settings.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/Settings.java
