---
title: "이벤트 종류"
parent: "앱 사용 기록"
grand_parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 470
---

# 이벤트 종류 (Event Types)

앱 사용 기록(usagestats)의 개별 이벤트가 어떤 번호와 이름으로 남는지, 이벤트마다 어떤 필드가 붙는지 정리합니다. 번호와 이름은 현행 AOSP 기준(frameworks/base 의 main 가지)이고, 번호마다 처음 들어간 API 수준이 다를 수 있습니다.

## 한 줄 요약

이벤트 한 건에는 0~31번 가운데 하나의 종류(type)가 붙고, 앱 화면 전환·화면 켜짐과 꺼짐·잠금 화면·알림·포그라운드 서비스·대기 버킷 변경처럼 사용자의 조작과 시스템의 동작이 한 목록에 섞여 있어서 번호의 뜻부터 확인하고 읽어야 합니다.

## 이벤트 번호표

UsageEvents.Event 에 정의된 번호입니다 [1]. "공개" 는 일반 SDK 에 드러난 것이고, "@hide" 와 "@SystemApi" 는 시스템 전용입니다.

| 번호 | 이름 | 공개 여부 | 뜻 |
|---|---|---|---|
| 0 | NONE | 공개 | 이벤트 종류 없음 |
| 1 | ACTIVITY_RESUMED (옛 이름 MOVE_TO_FOREGROUND) | 공개 | 액티비티가 앞으로 나옴, onResume() 에 해당 |
| 2 | ACTIVITY_PAUSED (옛 이름 MOVE_TO_BACKGROUND) | 공개 | 액티비티가 뒤로 감, onPause() 에 해당 |
| 3 | END_OF_DAY | @hide | 통계를 넘기는(rollover) 순간 앞에 있던 부품, ACTIVITY_PAUSED 처럼 다룸 |
| 4 | CONTINUE_PREVIOUS_DAY | @hide | 전날부터 앞에 있던 부품, ACTIVITY_RESUMED 처럼 다룸 |
| 5 | CONFIGURATION_CHANGE | 공개 | 기기 설정(configuration) 변경 |
| 6 | SYSTEM_INTERACTION | @SystemApi @hide | 시스템이 패키지와 상호작용 |
| 7 | USER_INTERACTION | 공개 | 사용자가 패키지와 어떤 식으로든 상호작용 |
| 8 | SHORTCUT_INVOCATION | 공개 | 사용자가 바로가기(ShortcutInfo)에 해당하는 동작을 실행 |
| 9 | CHOOSER_ACTION | @hide | 공유 선택창(ChooserActivity)에서 사용자가 패키지를 고름 |
| 10 | NOTIFICATION_SEEN | @SystemApi @hide | 사용자가 알림을 봄 |
| 11 | STANDBY_BUCKET_CHANGED | 공개 | 앱 대기 버킷(App Standby Bucket) 변경 |
| 12 | NOTIFICATION_INTERRUPTION | @SystemApi @hide | 앱이 방해하는(interruptive) 알림을 올림 |
| 13 | SLICE_PINNED_PRIV | @SystemApi @hide | 기본 런처나 어시스턴트가 Slice 를 고정 |
| 14 | SLICE_PINNED | @SystemApi @hide | 앱이 Slice 를 고정 |
| 15 | SCREEN_INTERACTIVE | 공개 | 화면이 상호작용 상태(완전히 켜짐)가 됨 |
| 16 | SCREEN_NON_INTERACTIVE | 공개 | 화면이 비상호작용 상태(꺼짐 또는 ambient)가 됨 |
| 17 | KEYGUARD_SHOWN | 공개 | 잠금 화면(keyguard) 표시 |
| 18 | KEYGUARD_HIDDEN | 공개 | 잠금 화면 숨김, 보통 잠금 해제 때 |
| 19 | FOREGROUND_SERVICE_START | 공개 | 포그라운드 서비스 시작 |
| 20 | FOREGROUND_SERVICE_STOP | 공개 | 포그라운드 서비스 종료 |
| 21 | CONTINUING_FOREGROUND_SERVICE | @hide | 구간이 시작할 때 이미 돌던 서비스, FOREGROUND_SERVICE_START 처럼 다룸 |
| 22 | ROLLOVER_FOREGROUND_SERVICE | @hide | 통계를 넘길 때 돌던 서비스 |
| 23 | ACTIVITY_STOPPED | 공개 | 액티비티가 화면에서 안 보이게 됨, onStop() 에 해당 |
| 24 | ACTIVITY_DESTROYED | @hide | 액티비티 파괴, onDestroy() 에 해당 |
| 25 | FLUSH_TO_DISK | @hide | 사용 기록 데이터베이스를 파일로 저장 |
| 26 | DEVICE_SHUTDOWN | 공개 | Android 런타임 종료 과정 |
| 27 | DEVICE_STARTUP | 공개 | 종료나 재시작 뒤 Android 런타임 시작 |
| 28 | USER_UNLOCKED | @hide | 사용자가 처음 잠금 해제됨(CE 저장소를 열 수 있게 됨) |
| 29 | USER_STOPPED | @hide | 전원 끔이나 사용자 전환으로 사용자가 멈춤 |
| 30 | LOCUS_ID_SET | @hide | 액티비티에 새 locusId 가 설정됨 |
| 31 | APP_COMPONENT_USED | @hide | 패키지의 부품(방송 수신기·서비스·제공자)이 쓰임 |

가장 큰 번호를 뜻하는 MAX_EVENT_TYPE 도 31입니다. 1번과 2번은 새 이름(ACTIVITY_RESUMED·ACTIVITY_PAUSED)과 폐기된 옛 이름(MOVE_TO_FOREGROUND·MOVE_TO_BACKGROUND)이 같은 번호를 쓰니, 도구가 어느 이름으로 보여 주든 같은 이벤트로 읽습니다 [1]. ALEAPP 는 0~31번의 이름표 32개를 쓰고 표에 없는 번호는 숫자 그대로 보여 줍니다 [5].

## 이벤트마다 붙는 필드

모든 이벤트에는 패키지(package_token), 클래스(class_token), 시각(time_ms), flags, 종류(type)가 들어가고, 일부 이벤트에만 쓰는 필드가 더 있습니다 [2]. 각 필드의 번호는 [파일 구조](structure.md) 페이지의 EventObfuscatedProto 표에 있습니다.

| 이벤트 | 더 붙는 필드 |
|---|---|
| CONFIGURATION_CHANGE | config |
| SHORTCUT_INVOCATION | shortcut_id_token |
| STANDBY_BUCKET_CHANGED | standby_bucket |
| NOTIFICATION_INTERRUPTION | notification_channel_id_token |
| 액티비티 이벤트 | instance_id, task_root_package_token, task_root_class_token |
| LOCUS_ID_SET | locus_id_token |
| USER_INTERACTION | interaction_extras |

interaction_extras 필드는 USER_INTERACTION 이벤트에 붙고 분류(category)와 동작(action)을 토큰으로 담으며, ALEAPP 는 이를 'Interaction Category', 'Interaction Action' 열로 보여 줍니다 [2][5][6]. flags 에는 인스턴트 앱 표시(`FLAG_IS_PACKAGE_INSTANT_APP = 1 << 0`, @hide)가 들어갑니다 [1].

## 대기 버킷 값

STANDBY_BUCKET_CHANGED 의 standby_bucket 필드에는 버킷과 바뀐 이유가 함께 들어 있고, 상위 16비트가 버킷, 하위 16비트가 이유(reason)입니다 [5]. 값의 뜻은 UsageStatsManager 에 정의되어 있습니다 [3].

| 버킷 | 값 | 비고 |
|---|---|---|
| STANDBY_BUCKET_EXEMPTED | 5 | @SystemApi @hide |
| STANDBY_BUCKET_ACTIVE | 10 | |
| STANDBY_BUCKET_WORKING_SET | 20 | |
| STANDBY_BUCKET_FREQUENT | 30 | |
| STANDBY_BUCKET_RARE | 40 | |
| STANDBY_BUCKET_RESTRICTED | 45 | |
| STANDBY_BUCKET_NEVER | 50 | @SystemApi @hide |

이유 값은 주 이유(REASON_MAIN_MASK = 0xFF00)와 하위 이유(REASON_SUB_MASK = 0x00FF)로 나뉩니다. 주 이유는 DEFAULT = 0x0100, TIMEOUT = 0x0200, USAGE = 0x0300, FORCED_BY_USER = 0x0400, PREDICTED = 0x0500, FORCED_BY_SYSTEM = 0x0600 입니다 [3].

## 읽는 쪽에 따라 가려지는 정보

UsageEvents 에는 조회하는 앱에게 일부 정보를 가리는 옵션이 있습니다 [1].

| 옵션 | 값 | 가리는 것 |
|---|---|---|
| SHOW_ALL_EVENT_DATA | 0 | 가리지 않음 |
| OBFUSCATE_INSTANT_APPS | 0x1 | 인스턴트 앱의 패키지·클래스 이름 |
| HIDE_SHORTCUT_EVENTS | 0x2 | SHORTCUT_INVOCATION 이벤트 전부 |
| OBFUSCATE_NOTIFICATION_EVENTS | 0x4 | 알림 채널 ID |
| HIDE_LOCUS_EVENTS | 0x8 | LOCUS_ID_SET 이벤트 전부 |

서비스는 호출한 앱에 따라 어느 옵션을 쓸지 정하고, 인스턴트 앱 가림은 기록할 때가 아니라 조회하는 시점의 상태를 기준으로 합니다 [4]. 그래서 사용 시간 앱 같은 제3자 앱으로 뽑은 결과에서는 일부 이벤트나 필드가 빠질 수 있고, 파일이나 dumpsys 출력과 다를 수 있습니다.

## dumpsys 에 찍히는 이벤트

`dumpsys usagestats` 의 최근 이벤트 목록에는 ACTIVITY_RESUMED, ACTIVITY_PAUSED, ACTIVITY_STOPPED, FOREGROUND_SERVICE_START, FOREGROUND_SERVICE_STOP, SCREEN_INTERACTIVE, SCREEN_NON_INTERACTIVE, KEYGUARD_SHOWN, KEYGUARD_HIDDEN, USER_INTERACTION, SHORTCUT_INVOCATION, NOTIFICATION_SEEN, NOTIFICATION_INTERRUPTION, STANDBY_BUCKET_CHANGED 같은 이벤트 이름이 찍힙니다. NOTIFICATION_SEEN 과 NOTIFICATION_INTERRUPTION 은 SDK 에서는 시스템 전용이지만 dumpsys 에서는 이름 그대로 나옵니다.

이벤트 종류에 따라 줄에 찍히는 필드는 다음과 같습니다.

| 이벤트 | dumpsys 줄의 필드 |
|---|---|
| ACTIVITY_RESUMED·PAUSED·STOPPED | package, class, instanceId, taskRootPackage, taskRootClass, flags |
| FOREGROUND_SERVICE_START·STOP | package, class, flags |
| STANDBY_BUCKET_CHANGED | package, standbyBucket(두 자리 숫자), reason, flags |
| NOTIFICATION_INTERRUPTION | package, channelId, flags |
| NOTIFICATION_SEEN | package, flags |
| SHORTCUT_INVOCATION | package, shortcutId, flags |
| SCREEN_INTERACTIVE·NON_INTERACTIVE, KEYGUARD_SHOWN·HIDDEN | package, flags |

dumpsys 에서는 대기 버킷과 이유가 standbyBucket 과 reason 으로 나뉘어 찍힙니다. 화면과 잠금 화면 이벤트에도 package 필드에 값이 들어갑니다. NOTIFICATION_INTERRUPTION 의 channelId 에는 CHANNEL_ID_SMS_MMS, REMINDER_CHANNEL_ID_NOTIFICATION, CHR, BATTERY, SECURITY 같은 값이, SHORTCUT_INVOCATION 의 shortcutId 에는 AUTO_UPDATE 나 한글 문자열 같은 값이 들어갑니다.

액티비티 이벤트는 RESUMED, PAUSED, STOPPED 세 줄이 묶여 나오는 경우가 많아서, 세 이벤트의 개수가 거의 같습니다. 이 세 이벤트를 사용 시작과 끝으로 어떻게 읽을지, 시스템이 만든 이벤트를 사용자 조작과 어떻게 가를지는 [해석 함정](pitfalls.md) 페이지에서 다룹니다.

## 함께 볼 페이지

- 알림 이벤트는 [알림 기록 (Notification History)](../notification-history.md) 과 함께 봅니다.
- 포그라운드 서비스와 화면 상태는 [배터리 사용 기록 (batterystats)](../batterystats.md) 과 함께 봅니다.
- 패키지 이름을 읽는 법은 [패키지 이름과 UID](../../../01-foundations/value-decoding/package-uid.md) 페이지에 있습니다.

## 참고 문헌

1. UsageEvents.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/app/usage/UsageEvents.java
2. usagestatsservice_v2.proto — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/proto/android/server/usagestatsservice_v2.proto
3. UsageStatsManager.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/app/usage/UsageStatsManager.java
4. UsageStatsService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsService.java
5. ALEAPP usagestats.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/usagestats.py
6. UsageStatsProtoV2.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsProtoV2.java
