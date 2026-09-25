---
title: "이벤트 로그 버퍼"
parent: "아티팩트 · 로그"
nav_order: 1210
---

# 이벤트 로그 버퍼 (events)

## 한 줄 요약

이벤트 로그 버퍼 (events) 는 시스템이 정해 둔 태그 번호와 칸 형식에 맞춰 프로세스 시작·종료, 화면(Activity) 전환, 잠금 화면 표시 같은 시스템 이벤트를 바이너리로 적는 logcat 버퍼이고, logcat 이 태그 사전으로 해석해서 사람이 읽는 줄로 보여 줍니다 [1][3].

## 무엇을 기록하나 · 왜 생기나

events 버퍼는 logcat 문서에서 "해석된 바이너리 시스템 이벤트 버퍼" 로 소개하는 버퍼이고 [1], 코드는 `android.util.EventLog` 로 이 버퍼에 이벤트를 남깁니다 [2]. 이벤트 로그는 바이너리 형식이라 일반 logcat 보다 덜 시끄럽고 [3], 태그마다 칸 이름과 자료형이 정해져 있어서 앱마다 제각각인 main 버퍼 로그보다 읽는 방법이 일정합니다.

시스템 서버의 ActivityManager 와 WindowManager 가 프로세스와 화면의 상태가 바뀔 때마다 태그를 남기기 때문에, 짧은 시간대 안에서 어떤 앱 프로세스가 언제 뜨고 죽었는지, 어떤 화면이 언제 앞으로 나오고 멈췄는지를 순서대로 따라갈 수 있습니다. 버퍼 자체의 성격(메모리 순환 버퍼, 접근 제한, 출력 형식)은 [logcat (logcat)](logcat.md) 에서 다룹니다.

## 위치와 버전별 차이

events 버퍼는 다른 logcat 버퍼처럼 `logd` 의 메모리 버퍼에 있고, `adb logcat -b events` 로 읽습니다 [1]. 태그 번호를 이름과 칸으로 바꾸는 태그 사전 파일은 기기의 `/system/etc` 아래에 설치되고, logcat 이 해석할 때 이 사전을 씁니다 [5]. 사전 파일의 정확한 이름은 확인하지 못했습니다.

관찰 기기에서는 adb 일반 셸 권한으로 events 버퍼의 줄을 읽을 수 있었지만, 같은 기기의 버퍼 크기 목록에는 events 가 나오지 않았습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 목록에 빠진 이유는 확인하지 못했습니다.

태그 이름은 Android 버전에 따라 다릅니다. source.android.com 의 버그 리포트 문서에는 `am_focused_activity` 가 나오지만 [3], 현재 AOSP main 의 ActivityManager 태그 파일에는 이 태그가 없고 [4], 화면 전환 태그는 WindowManager 태그 파일에 `wm_` 으로 시작하는 이름으로 있습니다 [6]. 태그가 옮겨 간 Android 버전은 확인하지 못했으니, 검체를 읽을 때는 그 기기의 태그 사전과 실제 출력으로 이름을 확인합니다.

| 출처 | 기준 | 담긴 태그 |
|---|---|---|
| ActivityManager 태그 파일 | AOSP main | `am_` 으로 시작하는 프로세스·메모리 이벤트 [4] |
| WindowManager 태그 파일 | AOSP main | `wm_` 으로 시작하는 화면·작업(Task) 이벤트 [6] |
| logcat 공통 태그 파일 | AOSP main | 부팅 단계, 스레드 락 경합 표본, 와이파이 상태 같은 공통 이벤트 [5] |
| 버그 리포트 문서 | 문서 작성 시점 | `am_focused_activity` 같은 예전 이름이 보임 [3] |

아래 표의 번호와 칸은 모두 AOSP main 기준이고, 특정 Android 버전이나 삼성 기기에서 같은지는 확인하지 못했습니다.

## 구조

### 줄 모양

이벤트 로그 한 줄은 "timestamp PID TID log-level tag tag-values" 순서입니다 [3]. 관찰 기기의 출력은 아래 모양이었고, 확인한 수준은 I 였으며 연도는 없었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5).

```
--------- beginning of events
##-## ##:##:##.### <PID> <TID> I <태그>: <내용>
```

`-v descriptive` 수식어를 붙이면 events 항목에 설명을 붙여 보여 줍니다 [1].

### 태그 정의 형식

태그 사전의 한 줄은 아래 형식이고, 태그 번호는 0 부터 2^31 까지의 십진수입니다 [4][5].

```
태그번호 태그이름 (칸이름|자료형|단위),(칸이름|자료형|단위),...
```

자료형과 단위는 숫자나 문자 코드로 적습니다 [5].

| 자료형 코드 | 뜻 |
|---|---|
| 1 | int |
| 2 | long |
| 3 | string |
| 4 | list |
| 5 | float |

| 단위 코드 | 뜻 |
|---|---|
| 1 | 객체 수 |
| 2 | 바이트 |
| 3 | 밀리초 |
| 4 | 할당 수 |
| 5 | Id |
| 6 | 퍼센트 |
| s | 초(단조 시간) |

### 프로세스·메모리 태그 (ActivityManager)

| 번호 | 태그 | 칸 |
|---|---|---|
| 30014 | `am_proc_start` | User, PID, UID, Process Name, Type, Component |
| 30010 | `am_proc_bound` | User, PID, Process Name |
| 30011 | `am_proc_died` | User, PID, Process Name, OomAdj, ProcState |
| 30023 | `am_kill` | User, PID, Process Name, OomAdj, Reason, Rss(바이트) |
| 30008 | `am_anr` | User, pid, Package Name, Flags, reason |
| 30039 | `am_crash` | User, PID, Process Name, Flags, Exception, Message, File, Line, Recoverable |
| 30040 | `am_wtf` | User, PID, Process Name, Flags, Tag, Message |
| 30017 | `am_low_memory` | Num Processes |
| 30052 | `am_uid_running` | UID |
| 30053 | `am_uid_stopped` | UID |
| 30051 | `am_user_state_changed` | id, state |
| 30047 | `am_pss` | Pid, UID, Process Name, Pss, Uss, SwapPss, Rss, StatType, ProcState, TimeToCollect |
| 30050 | `am_mem_factor` | Current, Previous |
| 30100 | `am_foreground_service_start` | User, Component Name 로 시작하고 fgsType 으로 끝남. 가운데 칸은 확인하지 못함 |

출처는 AOSP main 의 ActivityManager 태그 파일입니다 [4].

### 화면·작업 태그 (WindowManager)

| 번호 | 태그 | 칸 |
|---|---|---|
| 30005 | `wm_create_activity` | User, Token, Task ID, Component Name, Action, MIME Type, URI, Flags |
| 30006 | `wm_restart_activity` | User, Token, Task ID, Component Name |
| 30007 | `wm_resume_activity` | User, Token, Task ID, Component Name |
| 30009 | `wm_activity_launch_time` | User, Token, Component Name, time(long, 밀리초) |
| 30013 | `wm_pause_activity` | User, Token, Component Name, User Leaving, Reason |
| 30048 | `wm_stop_activity` | User, Token, Component Name |
| 30001 | `wm_finish_activity` | User, Token, Task ID, Component Name, Reason |
| 30018 | `wm_destroy_activity` | User, Token, Task ID, Component Name, Reason |
| 30043 | `wm_set_resumed_activity` | User, Component Name, Reason |
| 30044 | `wm_focused_root_task` | User, Display Id, Focused Root Task Id, Last Focused Root Task Id, Reason |
| 31001 | `wm_task_created` | TaskId |
| 31003 | `wm_task_removed` | TaskId, Root Task ID, Display Id, Reason |
| 30067 | `wm_set_keyguard_shown` | Display Id, keyguardShowing, aodShowing, keyguardGoingAway, occluded, Reason |

출처는 AOSP main 의 WindowManager 태그 파일입니다 [6].

### 공통 태그 (logcat 태그 파일)

| 번호 | 태그 |
|---|---|
| 3000 | `boot_progress_start` |
| 3020 | `boot_progress_preload_start` |
| 3030 | `boot_progress_preload_end` |
| 20003 | `dvm_lock_sample` |
| 20004 | `art_hidden_api_access` |
| 50021 | `wifi_state_changed` |
| 52000 | `db_sample` |
| 60000 | `viewroot_draw` |
| 80100번대 | `bionic_event_` 로 시작하는 태그들 |
| 1937006964 | `stats_log` |

출처는 AOSP main 의 logcat 공통 태그 파일입니다 [5]. 화면 켜짐·배터리·알림처럼 흔히 기대하는 태그(`screen_toggled`, `power_screen_state`, `battery_level`, `notification_` 이나 `sysui_` 로 시작하는 태그)는 여기서 본 태그 파일들에 없었습니다 [5]. 다른 태그 파일에 있을 수 있지만 번호와 칸은 확인하지 못했으니, 다른 자료에서 본 번호를 그대로 옮겨 쓰지 않습니다.

## 증거로서 의미

**증명하는 것**

`am_proc_start` 는 그 시각에 그 UID 로 그 이름의 프로세스가 시작됐고 어떤 구성 요소(Component) 때문에 시작됐는지를 적은 기록이고, `am_proc_died`·`am_kill` 은 프로세스가 끝난 시각과 이유를 적은 기록입니다. `wm_create_activity`·`wm_resume_activity`·`wm_pause_activity`·`wm_stop_activity` 를 순서대로 이으면 어떤 화면이 언제 앞으로 나오고 언제 뒤로 물러났는지를 짧은 시간대 안에서 재구성할 수 있고, `wm_create_activity` 의 Action·URI 칸은 그 화면을 연 요청의 종류를 보여 줍니다. `wm_set_keyguard_shown` 은 잠금 화면이 표시되거나 사라지는 상태 변화가 그 시각에 있었다는 기록입니다.

**증명하지 못하는 것**

프로세스가 시작됐다는 기록은 사람이 앱을 열었다는 뜻이 아닙니다. 서비스처럼 화면 없이 뒤에서 뜬 프로세스도 같은 태그를 남길 수 있으니(추론), Type·Component 칸과 같은 시각의 `wm_` 화면 태그를 함께 봅니다. 화면이 앞으로 나온 기록이 있어도 그 화면을 누가 보고 있었는지는 알 수 없고, `wm_set_keyguard_shown` 도 잠금이 풀린 상태 변화를 보여 줄 뿐 누가 풀었는지는 보여 주지 않습니다. 사용자를 가리는 문제는 [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다. 보고서에는 "이 시각에 이 구성 요소의 화면이 앞으로 나온 기록이 있다" 처럼 씁니다.

## 시각 해석

events 줄의 시각 칸은 다른 logcat 버퍼와 같은 방식으로 찍히고, 관찰 기기에서는 연도 없이 월-일 시:분:초.밀리초였습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 시간대를 확인하는 방법과 수식어는 [logcat (logcat)](logcat.md) 의 시각 해석 절을 따릅니다.

칸 값 안의 시간은 태그 사전의 단위 코드로 읽습니다. `wm_activity_launch_time` 의 time 칸은 밀리초 단위의 걸린 시간이고 [6], 시각이 아닙니다. 단위 코드 `s` 는 단조 시간 기준 초라서 [5] 벽시계 시각으로 바꾸지 않습니다.

## 함정과 한계

첫째, 순환 버퍼라 오래된 항목이 밀려납니다 [1]. events 버퍼가 main 버퍼보다 덜 시끄럽다고 해서 [3] 더 오래 남는다는 보장은 확인하지 못했습니다.

둘째, 태그 이름과 칸은 버전마다 다릅니다. 예전 문서나 도구가 `am_focused_activity` 같은 이름을 찾는다면 최신 기기에서는 결과가 비어 나올 수 있으니 [3][4], 빈 결과를 "화면 전환이 없었다" 로 읽지 않습니다.

셋째, 짧은 간격으로 `am_proc_start` 와 `am_proc_died` 가 되풀이되면 메모리가 모자라 프로세스가 반복해서 종료되는 상태(thrashing)이고, `am_low_memory` 가 되풀이되면 시스템이 캐시 프로세스를 정리하고 있다는 신호입니다 [3]. 이런 구간의 프로세스 시작·종료를 사용자가 앱을 여닫은 것으로 해석하지 않습니다.

넷째, ANR 은 events 의 `am_anr` 이나 logcat 의 "ANR in" 문구로 찾습니다 [3]. ANR 당시 스레드 상태는 events 에 없고, [버그 리포트 (bugreport)](bugreport.md) 와 [앱 오류·종료 기록 (DropBox·tombstones·ANR)](../app-usage/crash-records.md) 에서 찾습니다.

## 직접 분석해 보기

### 텍스트로 한 번

바이너리 항목의 바이트 배치는 확인하지 못해서 헥스 따라가기 대신 해석된 텍스트를 읽습니다.

1. `adb logcat -b events` 출력을 파일로 받고, 같은 방식으로 `-v descriptive` 를 붙인 출력도 받습니다.
2. `am_proc_start` 줄을 모아 프로세스 이름과 PID 의 짝을 만듭니다.
3. 조사할 앱의 구성 요소 이름으로 `wm_create_activity`, `wm_resume_activity`, `wm_pause_activity`, `wm_stop_activity` 줄을 골라 시각 순서로 늘어놓습니다.
4. 같은 구간의 `wm_set_keyguard_shown` 줄로 잠금 화면 상태가 바뀐 시각을 끼워 넣습니다.
5. 칸 값이 태그 사전의 칸 수와 맞지 않으면 그 기기의 태그 사전이 다르다고 보고 AOSP main 표를 그대로 적용하지 않습니다.

### 공개 도구로 한 번

logcat 의 `-v descriptive` 가 태그 사전을 써서 칸에 설명을 붙여 주는 공개 도구 역할을 합니다 [1]. 텍스트로 직접 짝지은 칸 값과 descriptive 출력이 같은지 몇 줄 맞춰 보고 나서 결과를 씁니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [logcat (logcat)](logcat.md) | 같은 PID 가 main·system 버퍼에 남긴 메시지 |
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | `wm_resume_activity` 와 ACTIVITY_RESUMED 시각 |
| [최근 앱 화면 (Recents·Snapshots)](../app-usage/recents-snapshots.md) | `wm_task_created`·`wm_task_removed` 의 작업이 최근 앱 목록에 있는지 |
| [잠금 화면 설정 (Lock Settings)](../system-account/lock-settings.md) | 잠금 방식과 `wm_set_keyguard_shown` 의 상태 변화 |
| [앱 오류·종료 기록 (DropBox·tombstones·ANR)](../app-usage/crash-records.md) | `am_crash`·`am_anr` 과 같은 시각의 충돌·ANR 기록 |

앱 사용 시간대를 재구성하는 흐름은 [어떤 앱을 언제 썼나 (App Usage)](../../04-scenarios/activity/app-usage.md) 에서 다룹니다.

## 실습

공개 안드로이드 검체(NIST CFReDS 등)에 버그 리포트나 events 버퍼 출력이 들어 있으면 아래 질문을 풀어 봅니다.

1. 가장 이른 events 줄의 시각은 언제이고, 그때부터 수집 시각까지 `wm_resume_activity` 로 앞에 나온 화면은 몇 개입니까?
2. `am_proc_start` 가운데 같은 시각에 `wm_` 화면 태그가 없는 프로세스는 무엇이고, Type 칸은 무엇입니까?
3. `am_low_memory` 가 되풀이되는 구간이 있다면, 그 구간의 프로세스 시작·종료를 어떻게 해석해야 합니까?

## 참고 문헌

1. Android Developers — Logcat command-line tool — https://developer.android.com/tools/logcat
2. Android Open Source Project — Understanding logging — https://source.android.com/docs/core/tests/debug/understanding-logging
3. Android Open Source Project — Read bug reports — https://source.android.com/docs/core/tests/debug/read-bug-reports
4. AOSP frameworks/base — ActivityManager EventLogTags.logtags (main) — https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/services/core/java/com/android/server/am/EventLogTags.logtags
5. AOSP system/logging — logcat event.logtags (main) — https://android.googlesource.com/platform/system/logging/+/refs/heads/main/logcat/event.logtags
6. AOSP frameworks/base — WindowManager EventLogTags.logtags (main) — https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/services/core/java/com/android/server/wm/EventLogTags.logtags
