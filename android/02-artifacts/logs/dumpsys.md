---
title: "dumpsys 출력"
parent: "아티팩트 · 로그"
nav_order: 1230
---

# dumpsys 출력 (dumpsys)

dumpsys 출력 (dumpsys) 은 기기에서 돌고 있는 시스템 서비스가 자기 상태를 텍스트로 내놓은 것이고, 앱 사용 이벤트·알림·계정 변경 이력·사용자 로그인 시각처럼 파일을 직접 꺼내기 어려운 기록을 adb 셸에서 읽어 오는 통로가 됩니다 [1].

## 무엇을 기록하나 · 왜 생기나

dumpsys 는 원래 개발자가 시스템 서비스의 상태를 확인하려고 쓰는 도구입니다 [1]. 서비스마다 출력 형식이 제각각이고, 서비스도 입력(input), 그래픽(gfxinfo), 네트워크 통계(netstats), 배터리(batterystats), 프로세스 통계(procstats), 메모리(meminfo) 로 다양합니다 [1].

포렌식에서는 시스템 영역 파일을 루팅 없이 꺼내기 어려운 기기에서 서비스가 내놓는 기록을 텍스트로 받을 수 있다는 점이 쓸모 있습니다. 아래 절의 서비스들은 adb 일반 셸 권한으로 읽을 수 있습니다. 서비스별 해석은 각 아티팩트 페이지에서 다룹니다.

## 위치와 버전별 차이

dumpsys 는 파일이 아니라 명령의 출력이라, 부르는 순간에만 생깁니다. 문법은 아래와 같습니다 [1].

```
adb shell dumpsys [-t timeout] [--help | -l | --skip services | service [arguments] | -c | -h]
```

| 옵션 | 뜻 |
|---|---|
| `-t` | 시간 제한(초). 기본값 10초 |
| `-l` | 쓸 수 있는 시스템 서비스 전체 목록 |
| `--skip` | 출력에서 뺄 서비스 |
| `-c` | 일부 서비스에서 기계가 읽기 좋은 형식으로 출력 |
| `-h` | 일부 서비스의 도움말 |

서비스 이름 뒤에 서비스별 인자를 붙일 수 있습니다. batterystats 의 경우 `--checkin` 은 CSV 형식, `--charged` 는 마지막 충전 이후의 데이터를 내놓고, `--unplugged` 는 Android 5.1.1 에서 폐기됐습니다 [1]. 서비스 인자 가운데는 기록을 지우는 것도 있으니, 증거 수집 중에는 뜻을 확인한 인자만 씁니다. batterystats 의 예는 [배터리 사용 기록 (batterystats)](../app-usage/batterystats.md) 의 함정 절에 있습니다.

버그 리포트 본문에도 dumpsys 출력이 들어 있습니다 [2]. 버그 리포트로 한꺼번에 받는 방법은 [버그 리포트 (bugreport)](bugreport.md) 에서 다룹니다.

부르는 쪽 권한에 따라 출력이 달라지는지는 공식 문서에 나오지 않습니다 [1]. 버전·제조사마다 서비스 목록과 출력 필드가 다를 수 있으니, 기기마다 `-l` 목록부터 받아 둡니다.

## 구조

아래 서비스의 출력은 adb 일반 셸로 받을 수 있습니다. 줄 수와 눈에 띄는 모양은 다음과 같습니다.

| 서비스 | 줄 수 | 눈에 띄는 모양 | 해석 페이지 |
|---|---|---|---|
| `usagestats` | 7546 | `Last ## hour events` 아래 `time= type= package= class= flags=` 줄 | [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) |
| `package` | 192000 | `Database versions:`, `Known Packages:` | [설치된 앱 (packages.xml)](../app-usage/packages/index.md) |
| `batterystats` | 98027 | `Battery History [Format: #] (...)` 머리와 `+`/`-` 표시 줄 | [배터리 사용 기록 (batterystats)](../app-usage/batterystats.md) |
| `notification` | 4750 | `Notification List:` 아래 `NotificationRecord(...)` | [알림 기록 (Notification History)](../app-usage/notification-history.md) |
| `wifi` | 10850 | `Verbose logging is off`, `WifiDeviceStateChangeManager - Log Begin ----` 구간 | [와이파이 설정과 접속 기록 (WifiConfigStore)](../network/wifi.md) |
| `bluetooth_manager` | 16690 | `Bluetooth Status`, `Enable log:` 줄 | [블루투스 장치 (Bluetooth)](../network/bluetooth.md) |
| `account` | 415 | `Accounts: ##`, `Accounts History` 표 | [계정 (Accounts)](../system-account/accounts/index.md) |
| `user` | 789 | `Current user:`, `UserInfo{...}` 와 로그인·잠금 해제 시각 필드 | [사용자와 프로필 (Multi-user·users)](../system-account/users-profiles.md) |

줄 수는 한 기기의 한 시점 값이라 다른 기기와 비교하는 기준으로 쓰지 않습니다.

### 이벤트 줄 (usagestats)

`dumpsys usagestats` 는 `Last ## hour events (timeRange="...")` 머리 아래에 이벤트를 한 줄씩 적습니다.

```
  Last ## hour events (timeRange="..." )
    time="..." type=ACTIVITY_RESUMED package=<패키지> class=<패키지> flags=<값>
    time="..." type=SCREEN_INTERACTIVE package=<값> flags=<값>
```

나올 수 있는 type 에는 `ACTIVITY_RESUMED`, `ACTIVITY_PAUSED`, `ACTIVITY_STOPPED`, `FOREGROUND_SERVICE_START`, `FOREGROUND_SERVICE_STOP`, `SCREEN_INTERACTIVE`, `SCREEN_NON_INTERACTIVE`, `KEYGUARD_SHOWN`, `KEYGUARD_HIDDEN`, `NOTIFICATION_INTERRUPTION`, `NOTIFICATION_SEEN`, `SHORTCUT_INVOCATION`, `USER_INTERACTION`, `STANDBY_BUCKET_CHANGED` 가 있습니다. 앞의 세 가지 ACTIVITY 줄에는 `instanceId`, `taskRootPackage`, `taskRootClass` 필드가 더 붙고, `NOTIFICATION_INTERRUPTION` 에는 `channelId`, `SHORTCUT_INVOCATION` 에는 `shortcutId`, `STANDBY_BUCKET_CHANGED` 에는 `standbyBucket`, `reason` 필드가 붙습니다.

### 변경 이력 표 (account)

`dumpsys account` 는 계정 목록 아래에 변경 이력을 쉼표로 나눈 표로 적습니다.

```
  Accounts: ##
    Account {name=..., type=...}
  AccountId, Action_Type, timestamp, UID, TableName, Key
  Accounts History
  ##,action_account_add,...,#####,accounts,##
```

Action_Type 에는 `action_account_add`, `action_account_remove`, `action_called_account_remove` 등이 있습니다.

### 사용자 상태 (user)

`dumpsys user` 는 사용자마다 `UserInfo{...} serialNo= isPrimary=` 줄과 `Type`, `Flags`, `State`, `Created`, `Last logged in`, `Last logged in fingerprint`, `Start time`, `Unlock time`, `Last entered foreground` 필드를 적습니다. 주 사용자의 `State` 는 `RUNNING_UNLOCKED` 처럼 나오고, `Created:` 필드는 `<unknown>` 으로 나올 수 있습니다.

### 그 밖의 서비스

`dumpsys package` 에는 `Database versions:` 아래 `sdkVersion=`, `databaseVersion=`, `buildFingerprint=` 필드와, 시스템·설치 관리자·검증기·브라우저 같은 역할별 기본 패키지를 적은 `Known Packages:` 목록이 있습니다. `dumpsys notification` 의 `NotificationRecord(...)` 아래에는 `uid`, `userId`, `opPkg`, `icon`, `flags`, `originalFlags`, `pri`, `key`, `seen`, `groupKey` 필드가 이어집니다.

## 증거로서 의미

**증명하는 것**

dumpsys 출력은 그 명령을 부른 시각에 그 서비스가 내놓은 상태입니다. `usagestats` 의 이벤트 줄은 그 시각에 그 패키지의 화면·서비스·화면 켜짐 이벤트가 있었다는 서비스 기록이고, `account` 의 이력 표는 계정 추가·삭제 동작이 그 시각에 그 UID 로 있었다는 기록이며, `user` 의 `Last logged in`·`Unlock time` 필드는 이름대로 읽으면 그 사용자가 마지막으로 로그인하고 잠금을 푼 시각입니다(추론).

**증명하지 못하는 것**

dumpsys 는 서비스의 현재 상태를 뽑기 때문에 부르는 시점에 따라 내용이 달라집니다(추론). 이틀 뒤에 다시 부르면 그 사이 지워지거나 밀려난 기록은 나오지 않으니, 출력 한 번은 그 시점의 사진일 뿐입니다. 출력에 없는 기록이 원래 없었다는 뜻도 아닌데, 서비스가 보여 주는 기간이 `Last ## hour events` 처럼 정해져 있을 수 있고, 부르는 쪽 권한에 따라 출력이 달라지는지도 공식 문서에 나오지 않습니다. 보고서에는 "이 시각에 받은 dumpsys usagestats 출력에 이런 이벤트 줄이 있다" 처럼 받은 시각과 서비스 이름을 함께 씁니다.

## 시각 해석

시각 형식은 서비스마다 다릅니다. `usagestats` 의 `time=` 값과 `account` 이력의 시각은 한글이 섞인 사람이 읽는 형식으로 나올 수 있고, `batterystats` 기록 줄은 연도 없이 월-일과 시각만 찍힙니다. 사람이 읽는 형식은 기기 언어 설정을 따를 수 있으니(추론), 파싱하기 전에 몇 줄을 눈으로 보고 형식과 시간대를 정합니다. 시간대 판단은 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md), 시각 값 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

## 함정과 한계

첫째, 출력마다 받은 시각을 따로 적어 둡니다. 서비스를 하나씩 부르면 서비스 사이에 시간이 흘러, 같은 시점의 상태라고 가정할 수 없습니다.

둘째, `-t` 의 기본 시간 제한은 10초입니다 [1]. `package` 나 `batterystats` 처럼 수만~수십만 줄이 나오는 서비스는 출력이 끝까지 왔는지 마지막 줄을 확인합니다.

셋째, 일부 서비스 출력에는 그 서비스가 자세한 로그를 켰는지 알려 주는 줄이 있습니다. `dumpsys wifi` 에는 `Verbose logging is off` 와 `mVerboseLoggingLevel` 줄이, `dumpsys bluetooth_manager` 에는 `Enable log:` 줄이 있습니다. 이 설정이 평소와 다르다면 누가 언제 바꿨는지 다른 기록과 맞춰 봅니다.

넷째, 출력에는 계정 이름, 알림 내용, 패키지 목록 같은 개인 정보가 많이 들어 있습니다. 조사 범위를 벗어난 부분은 보고서에 옮기지 않습니다.

## 직접 분석해 보기

### 텍스트로 한 번

dumpsys 는 텍스트 출력이라 헥스로 따라갈 바이너리가 없습니다. 출력 파일을 그대로 읽습니다.

1. `adb shell dumpsys -l` 로 서비스 목록을 받아 둡니다.
2. 필요한 서비스마다 `adb shell dumpsys 서비스이름` 출력을 파일로 받고, 받은 시각을 파일 이름이나 수집 기록에 적습니다.
3. `usagestats` 출력에서 `Last ## hour events` 머리의 `timeRange` 로 덮는 기간을 확인하고, 조사할 패키지의 ACTIVITY 줄만 골라 시각 순서로 늘어놓습니다.
4. `account` 출력의 `Accounts History` 표에서 추가·삭제 줄의 UID 를 모아 [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md) 로 어느 앱이 동작을 불렀는지 확인합니다.

### 공개 도구로 한 번

`-c` 를 지원하는 서비스는 기계가 읽기 좋은 형식으로 받고 [1], batterystats 는 `--checkin` 으로 CSV 를 받아 [1] 표 계산 도구로 엽니다. 사람이 읽는 출력과 기계용 출력의 같은 항목을 몇 개 맞춰 보고 나서 기계용 출력을 씁니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | dumpsys 이벤트 줄과 저장 파일의 이벤트 |
| [이벤트 로그 버퍼 (events)](events-buffer.md) | ACTIVITY_RESUMED 와 `wm_resume_activity` 시각 |
| [계정 (Accounts)](../system-account/accounts/index.md) | 이력 표의 추가·삭제와 계정 데이터베이스 |
| [사용자와 프로필 (Multi-user·users)](../system-account/users-profiles.md) | 로그인·잠금 해제 시각과 사용자 파일 |
| [버그 리포트 (bugreport)](bugreport.md) | 버그 리포트 본문의 같은 서비스 출력 |

여러 서비스의 시각을 한 줄로 합치는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

공개 안드로이드 시험 이미지(NIST CFReDS 등)에 버그 리포트나 dumpsys 출력이 들어 있으면 아래 질문을 풀어 봅니다.

1. `usagestats` 출력의 `timeRange` 는 어느 기간을 덮고, 그 안에서 SCREEN_INTERACTIVE 와 SCREEN_NON_INTERACTIVE 는 몇 번씩 나옵니까?
2. `account` 의 `Accounts History` 에서 계정 삭제 줄은 언제이고, 어떤 UID 가 불렀습니까?
3. `user` 출력의 `Last logged in` 과 `Unlock time` 은 usagestats 의 KEYGUARD_HIDDEN 시각과 맞습니까?

## 참고 문헌

1. Android Developers — dumpsys — https://developer.android.com/tools/dumpsys
2. Android Developers — Capture and read bug reports — https://developer.android.com/studio/debug/bug-report
