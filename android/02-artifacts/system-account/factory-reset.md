---
title: "초기화 흔적"
parent: "아티팩트 · 시스템·계정"
nav_order: 400
---

# 초기화 흔적 (Factory Reset)

> 공장 초기화 (Factory Reset) 를 하면 사용자 데이터 영역이 지워지지만, 초기화 뒤 첫 부팅이 끝날 때 bootstat 이 `/data/misc/bootstat/factory_reset` 파일의 수정 시각에 그 시각을 적어 두고, 설정 값·계정 기록·공장 초기화 보호 (FRP) 영역에도 "여기서부터 다시 시작했다" 는 흔적이 남습니다.

## 무엇을 기록하나 · 왜 생기나

초기화는 `/data` 를 지우는 일이라 초기화 전 기록은 대부분 함께 사라집니다. 그래서 이 페이지에서는 지워진 내용을 되살리는 방법 대신, 초기화 뒤 처음부터 다시 쌓이기 시작한 기록에서 초기화 시점과 방식을 거꾸로 읽어 내는 방법을 다룹니다. 초기화를 요청하는 과정과 복구 모드로 넘어가는 흐름은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에서 다룹니다.

가장 직접적인 흔적은 부팅 기록 도구 bootstat 이 남깁니다. bootstat 은 부팅이 끝날 때마다 한 번 돌고, `factory_reset` 파일이 없으면 그 파일을 새로 만들어 그때 시각을 적습니다. 초기화 뒤에는 이 기록이 없다는 점을 초기화 시점의 신호로 쓰고, 이 값은 초기화 한 번에 한 번만 적습니다(현행 AOSP 기준). [1]

그 밖에도 설정 데이터베이스가 다시 만들어지면서 그때의 빌드 ID 를 적고, 앱마다 보이는 Android ID 는 초기화하면 바뀔 수 있습니다. [5] 반대로 설정 화면을 거치지 않은 초기화에서는 persistent 파티션의 FRP 데이터가 지워지지 않고 남습니다. [6]

## 위치와 버전별 차이

| 흔적 | 위치 | 근거 |
|---|---|---|
| bootstat 기록 | `/data/misc/bootstat/` 아래 파일 하나당 기록 하나 | 현행 AOSP 기준 [1][2][3] |
| 복구 모드 기록 | `/data/misc/recovery/last_log`, `/data/misc/recovery/last_kmsg` | 현행 AOSP 기준 [4] |
| FRP 데이터 | persistent 파티션(위치는 시스템 속성 `ro.frp.pst`), `/data/system/frp_secret` | 현행 AOSP 기준 [6] |
| 설정 값 | settings global·secure 의 키 | 현행 AOSP 기준 [5] |
| dumpsys 출력 | `dumpsys user`, `dumpsys account`, `dumpsys batterystats`, `dumpsys package` | |

bootstat 폴더는 권한이 0700 이고 소유자가 system 이라서 [3], adb 일반 셸로는 읽을 수 없고 루트 권한이나 전체 파일 시스템 추출이 있어야 할 것으로 보입니다. 추출 방식은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다. `/data/misc/bootstat`, `/data/misc/recovery`, `/data/system/frp_secret` 이 실제 기기에 그대로 있는지는 직접 확인해야 합니다.

버전과 제조사에 따라 달라지는 부분은 아래와 같습니다. 대부분의 항목은 특정 버전 태그가 아닌 현행 AOSP 소스 기준이라서 도입 버전을 단정할 수 없습니다.

| 항목 | 차이 |
|---|---|
| bootstat 의 초기화 기록 | 현행 AOSP 에 있습니다. 도입 버전과 삼성 기기에도 그대로 남는지는 실제 기기에서 확인합니다. |
| `/data/misc/recovery` 로 옮기는 동작 | `/cache` 파티션이 없는 기기에서만 옮깁니다. `/cache` 가 있으면 `--force-persist` 옵션이 있을 때만 옮깁니다. [4] |
| FRP secret 확인 강제 | 기능 플래그로 켜고, 소스에 "Upgrading from Android 14 or lower" 처리가 있어 Android 15 부터의 동작으로 보입니다. [6] |
| 앱마다 다른 Android ID | Android 8.0(API 26)부터입니다. [5] |
| `setup_wizard_has_run` (system) | AOSP 에 있는 키지만 기기에 따라 settings system 키 목록에 없을 수 있습니다. |
| 삼성·구글이 더한 설정 키 | `setup_skipped`, `setup_type`, `smartswitch_*`, `quick_start_*`, `rampart_is_reset_by_at_command` 같은 키가 삼성 기기에 있습니다. 뜻이 정해져 있지 않아 값만 옮깁니다. |

## 구조

### bootstat 폴더

bootstat 은 기록마다 파일을 하나씩 만들고 파일 이름을 기록 이름으로 씁니다. 파일 내용은 비어 있고, 값은 **파일의 수정 시각 (mtime)** 에 넣습니다. 권한 0600 으로 빈 파일을 만든 뒤 `utime()` 으로 수정 시각을 값으로 바꾸고, 읽을 때도 `stat()` 의 `st_mtime` 을 값으로 씁니다. 값은 int32 로 다룹니다. [2]

폴더는 부팅 초기 post-fs-data 단계에서 만들고, bootstat 은 부팅이 끝났을 때(`sys.boot_completed=1`) 아래 명령으로 한 번 돕니다. 완전히 다시 부팅할 때마다 한 번만 돌도록 `sys.bootstat.first_boot_completed` 속성으로 막습니다. [3]

```
mkdir /data/misc/bootstat 0700 system log
/system/bin/bootstat --record_boot_complete --record_boot_reason --record_time_since_factory_reset -l
```

초기화와 관련된 파일과 각 파일의 수정 시각이 뜻하는 값은 아래와 같습니다(현행 AOSP 기준). [1][3]

| 파일 | 수정 시각에 담긴 값 | 단위 |
|---|---|---|
| `factory_reset` | 파일이 없을 때만 만들고, 그때 bootstat 이 돈 시각을 적습니다. 곧 초기화 뒤 첫 부팅이 끝난 시각입니다. | 유닉스 초 (UTC) |
| `factory_reset_current_time` | bootstat 이 돌 때마다 현재 시각으로 덮어씁니다. | 유닉스 초 (UTC) |
| `factory_reset_record_value` | `factory_reset` 이 이미 있을 때 그 값을 다시 적습니다. | 유닉스 초 (UTC) |
| `time_since_factory_reset` | 현재 시각에서 `factory_reset` 값을 뺀 값이고, 첫 부팅 때는 적지 않습니다. | 경과 초 |
| `factory_reset_current_time_failure` | 현재 시각이 음수일 때 그 절댓값을 적고 멈춥니다. | 초 |
| `build_date` | 빌드 날짜(`ro.build.date.utc`)입니다. | 유닉스 초 |
| `factory_reset_boot_complete`, `factory_reset_boot_complete_no_encryption` | 부팅을 시작해서 끝날 때까지 걸린 시간입니다. | 경과 초 |
| `last_boot_time_utc` | 부팅이 끝날 때마다 현재 시각을 적습니다. | 유닉스 초 (UTC) |
| `time_since_last_boot` | 직전 `last_boot_time_utc` 와의 차이입니다. | 경과 초 |

bootstat 은 `build_date` 로 첫 부팅을 가려냅니다. 이 파일이 없으면 지금을 초기화 뒤 첫 부팅으로 보고, 부팅 완료 기록 이름 앞에 `factory_reset_` 을 붙이고 부팅 사유 기록에 `reboot,factory_reset` 을 더합니다. 파일은 있는데 빌드 날짜가 다르면 `ota_` 를 붙이고 `reboot,ota` 를 더합니다. 부팅 사유 표에서 `reboot,factory_reset` 의 값은 64 입니다. `_no_encryption` 이 붙은 이름은 전체 디스크 암호화 시절의 이름이 남은 것이라 지금은 늘 같이 적습니다. [1] 빌드 날짜를 읽는 법은 [기기 정보와 빌드](device-build.md) 에 있습니다.

### 복구 모드 기록 폴더

recovery-persist 는 시스템으로 다시 부팅해 `/data` 가 올라온 뒤, 복구 모드가 pmsg 에 남긴 마지막 기록을 `/data/misc/recovery/` 로 옮깁니다. `/cache` 가 없는 기기에서 pmsg 에 담긴 `recovery/` 기록을 `/data/misc/` 아래 같은 이름으로 쓰고, 새 내용이 기존 파일과 다르면 `last_log`·`last_kmsg` 를 한 칸씩 돌린 뒤 `console-ramoops` 내용을 `last_kmsg` 로 복사합니다. [4]

| 상수 | 경로 |
|---|---|
| `LAST_LOG_FILE` | `/data/misc/recovery/last_log` |
| `LAST_KMSG_FILE` | `/data/misc/recovery/last_kmsg` |
| `LAST_PMSG_FILE` | `/sys/fs/pstore/pmsg-ramoops-0` |
| `LAST_CONSOLE_FILE` | `/sys/fs/pstore/console-ramoops-0` (없으면 `/sys/fs/pstore/console-ramoops`) |

초기화도 복구 모드에서 돌기 때문에 그 기록이 pmsg 를 거쳐 초기화 뒤 새 `/data/misc/recovery/` 에 남을 수 있습니다. 실제 기기의 `last_log` 에 초기화 요청 줄이 남는지, 삼성 기기가 pstore 를 쓰는지는 실제 기기에서 확인합니다.

### FRP 데이터

PersistentDataBlockService 는 persistent 파티션을 읽고 씁니다. 이 데이터는 설정 화면을 거치지 않은 초기화에서는 살아남고, 설정 화면에서 초기화하면 지워집니다. [6] 파티션 자체는 [파티션과 저장 영역](../../01-foundations/storage/partitions/index.md) 에서 다룹니다.

| 순서(앞에서부터) | 내용 | 크기 |
|---|---|---|
| 1 | 파티션 다이제스트 | 32바이트 |
| 2 | `PARTITION_TYPE_MARKER` | 4바이트 |
| 3 | FRP 데이터 길이 | 4바이트 |
| 4 | FRP 데이터 | 최대 100KB |
| 5 | 빈 공간 | 나머지 |
| 6 | FRP secret magic + FRP secret | 8바이트 + 32바이트 |
| 7 | 테스트 모드 데이터 블록 | 10000바이트 |
| 8 | FRP credential handle 블록 | 1000바이트 |
| 9 | OEM Unlock 비트 | 1바이트 |

`/data/system/frp_secret`(임시 파일 `frp_secret_tmp`)에는 FRP secret 사본이 있습니다. 믿을 수 없는 초기화로 `/data` 가 지워지면 이 파일도 사라져 자동 해제를 막습니다. 부팅 때 `frp_secret`, `frp_secret_tmp`, 기본값(0 32바이트) 순서로 확인하고, 셋 다 맞지 않으면 FRP 가 켜진 채로 남습니다. FRP 상태는 예전 앱과 맞추려고 Settings.Global 의 `secure_frp_mode` 에도 1 또는 0 으로 적습니다. [6] FRP 를 해제하는 방법은 이 핸드북에서 다루지 않습니다.

### 설정 키

초기화 뒤 설정 데이터베이스를 새로 만들면서 생기거나 처음부터 다시 쌓이는 키입니다. 키를 읽는 방법과 저장 형식은 [설정 값](settings.md) 에 있습니다.

| 키 | 구역 | 뜻(AOSP 문서) [5] | 삼성 기기 |
|---|---|---|---|
| `database_creation_buildid` | global | 설정 데이터베이스를 처음 만들었을 때(없어서 다시 만든 때 포함)의 빌드 ID | 있음 |
| `boot_count` | global | API 24 로 돌기 시작한 뒤의 부팅 횟수 | 있음 |
| `device_provisioned` | global | 기기 설정을 마쳤는지(0/1) | 있음 |
| `secure_frp_mode` | global | FRP 제한 모드인지(0/1) | 있음 |
| `user_setup_complete` | secure | 현재 사용자가 설정 마법사를 마쳤는지(0/1) | 있음 |
| `user_setup_personalization_state` | secure | 설정 마법사 개인화 단계 상태(완료는 10) | 있음 |
| `last_setup_shown` | secure | 설정 마법사가 마지막으로 보인 버전 | 있음 |
| `android_id` | secure | 앱 서명 키·사용자·기기 조합마다 다른 64비트 값이고, 초기화하거나 APK 서명 키가 바뀌면 달라질 수 있음 | 있음 |

`boot_count` 설명에는 "초기화 이후" 라는 말이 없어서, 초기화 때 0 부터 다시 세는지는 실제 기기에서 확인합니다. Android ID 의 성질은 [기기 식별자](../../01-foundations/value-decoding/device-identifiers.md) 에서 다룹니다.

삼성 기기에는 이름으로 보면 초기 설정과 관련된 키가 더 있습니다. global 에 `setup_skipped`, `setup_type`, `euicc_factory_reset_timeout_millis`, `lock_reset_profile`, `smartswitch_transfer_completed`, `smartswitch_transfer_start_in_oobe`, `quick_start_flow_type`, `quick_start_source_manufacturer`, `previous_version_pda` 가 있고, secure 에 `IS_SMARTSWITCH_DATA_PRESENT`, `IS_SMARTSWITCH_RESTORE_IN_PROGRESS`, `rampart_is_reset_by_at_command` 가 있습니다. 이름만 보면 초기 설정 중 다른 기기에서 옮기기나 AT 명령으로 한 초기화를 가리키는 것처럼 읽히지만, 이름만으로 뜻을 단정하지 않습니다.

### adb 로 보이는 필드

루트 없이 adb 일반 셸로도 아래 필드를 볼 수 있습니다. `<값>`·`#` 자리에 실제 값이 들어갑니다.

```
dumpsys user
  UserInfo{#:xxx:#c##} serialNo=# isPrimary=true
    Created: <unknown>
    Last logged in: <값>
    Start time: <값>
    Unlock time: <값>

dumpsys account
  AccountId, Action_Type, timestamp, UID, TableName, Key
  Accounts History
  ##,action_account_add,<시각>,#####,accounts,##

dumpsys batterystats
  Battery History [Format: #] ...
    ##-## ##:##:##.### RESET:TIME: <시각>

dumpsys package
  Database versions:
    Internal:
      sdkVersion=## sdkVersionFull=####### databaseVersion=#
      buildFingerprint=<값> fingerprint=<값>
  Known Packages:
    Setup Wizard:
      com.google.android.setupwizard
```

주 사용자의 `Created:` 필드가 `<unknown>` 으로 나올 수 있습니다. 배터리 기록의 `RESET:TIME` 은 배터리 통계를 비운 시각으로 보이지만, 초기화와 같은 뜻인지는 다른 기록과 맞춰 봐야 합니다. 각 출력은 [사용자와 프로필](users-profiles.md), [계정](accounts/index.md), [배터리 사용 기록](../app-usage/batterystats.md), [dumpsys 출력](../logs/dumpsys.md) 에서 자세히 다룹니다.

## 증거로서 의미

**증명하는 것.** `factory_reset` 파일이 있으면 그 수정 시각은 가장 최근 초기화 뒤 bootstat 이 첫 부팅을 마친 시각을 기기 시계 기준으로 알려 줍니다. [1] `database_creation_buildid` 는 지금의 설정 데이터베이스를 어떤 빌드에서 만들었는지 알려 주고, 이 값이 현재 빌드와 다르면 데이터베이스를 만든 뒤 OTA 가 있었다는 단서가 될 수 있습니다. FRP 가 켜진 흔적은 설정 화면을 거치지 않은 초기화였을 가능성을 가리킵니다. 이 상태가 로그로 남는지는 실제 기기에서 확인합니다.

**증명하지 못하는 것.** 초기화를 누가 했는지, 왜 했는지는 이 흔적들로 알 수 없습니다. 초기화하면 `/data` 가 지워져 `factory_reset` 파일도 함께 사라지므로, 지금 있는 파일은 가장 최근 초기화 한 번만 알려 주고 몇 번 초기화했는지는 알려 주지 않습니다. 초기화 전에 무엇이 있었는지도 이 흔적으로는 알 수 없습니다. 보고서에는 "이 기기는 이 시각에 초기화했다" 가 아니라 "기기 시계 기준으로 이 시각에 초기화 뒤 첫 부팅을 마친 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

같은 bootstat 폴더 안에서도 파일마다 수정 시각의 기준이 다릅니다. 모두 날짜처럼 보이는 수정 시각 필드에 들어 있어서, 기준을 구분하지 않고 한 줄로 늘어놓으면 엉뚱한 날짜가 섞입니다.

| 기준 | 해당 파일 | 날짜로 그대로 읽었을 때 |
|---|---|---|
| 유닉스 초 (UTC) | `factory_reset`, `factory_reset_current_time`, `factory_reset_record_value`, `last_boot_time_utc` | 그대로 날짜입니다. |
| 빌드 날짜 | `build_date` | 초기화 시각이 아니라 소프트웨어를 빌드한 날짜입니다. |
| 경과 초 | `factory_reset_boot_complete*`, `time_since_factory_reset`, `time_since_last_boot` | 1970년 무렵 날짜로 보입니다. |

`factory_reset` 의 값은 초기화를 누른 순간이 아니라 초기화 뒤 첫 부팅이 끝난 시각이라서, 실제 초기화 실행은 그보다 조금 앞일 것으로 보입니다. [1][3] 첫 부팅 때 기기 시계가 아직 맞춰지지 않았다면 값이 틀릴 수 있습니다. 유닉스 초를 날짜로 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에, 기기 시간대는 [시간대와 시각 설정](time-zone.md) 에 있습니다.

## 함정과 한계

값이 파일 내용이 아니라 수정 시각에 있어서, 수정 시각을 보존하지 않는 방식으로 파일을 옮기면 값이 사라질 수 있습니다. 추출 도구마다 수정 시각을 보존하는지가 달라서, 추출 전에 도구가 파일 시각을 지키는지 따로 확인해야 합니다. 도구 검증은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

파일이 비어 있다고 해서 쓸모없는 파일로 넘기기 쉽습니다. 크기 0 인 파일이 한 폴더에 여러 개 있을 뿐이라, 파일 목록에서 수정 시각 열을 같이 보지 않으면 놓칩니다.

이 페이지의 bootstat·recovery·FRP 내용은 현행 AOSP 소스 기준이라, 삼성 기기에서 같은 파일이 같은 이름으로 남는지는 실제 기기에서 확인합니다. 초기화 전 기록이 필요하면 기기 밖, 곧 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 나 [구글 백업](../mail-cloud/google-backup.md) 쪽을 봐야 합니다.

## 직접 분석해 보기

### 헥스로 한 번

`factory_reset` 파일을 헥스 편집기로 열면 0바이트라서 볼 내용이 없고, 값은 파일 시스템이 적어 둔 수정 시각에 있습니다. 파일 시스템 수준에서 시각을 찾아가는 법은 [파일 시스템](../../01-foundations/storage/filesystems/index.md) 에서 다룹니다. 아래는 명세로 만든 예시이고 특정 기기에서 나온 값이 아닙니다.

```
수정 시각(int32)  = 1767225600
16진수           = 0x6955B900
UTC 날짜         = 2026-01-01 00:00:00
```

### 공개 도구로 한 번

추출한 폴더에서 `stat` 으로 파일마다 수정 시각을 유닉스 초로 뽑고, `date` 로 UTC 날짜로 바꿉니다.

```
stat -c '%n %s %Y' /추출본/data/misc/bootstat/*
date -u -d @1767225600
```

루트 없이 기기에 연결했을 때는 bootstat 폴더를 읽을 수 없으므로, 설정 키와 dumpsys 필드를 먼저 모읍니다.

```
adb shell settings list global
adb shell settings list secure
adb shell dumpsys user
adb shell dumpsys account
```

bootstat 폴더는 위처럼 `stat` 으로 직접 읽습니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 계정 추가 기록 | `Accounts History` 에서 가장 오래된 `action_account_add` 시각이 초기 설정 시점의 단서가 될 수 있습니다. | [계정](accounts/index.md) |
| 설정 값 | `database_creation_buildid`, `user_setup_complete`, `secure_frp_mode` | [설정 값](settings.md) |
| 빌드 정보 | 현재 빌드 ID·빌드 날짜와 `database_creation_buildid`·`build_date` 비교 | [기기 정보와 빌드](device-build.md) |
| 사용자 정보 | 사용자 생성·첫 로그인 필드 | [사용자와 프로필](users-profiles.md) |
| 배터리 기록 | `RESET:TIME` 줄 | [배터리 사용 기록](../app-usage/batterystats.md) |
| 삼성 복구 기록 | `/efs/recovery/history` 에 초기화 뒤에도 남는 앞선 초기화 요청 기록 | [삼성 전원·재부팅·초기화 로그](../samsung/power-reset-logs.md) |

초기화 시점을 좁힐 때는 `factory_reset` 의 수정 시각을 먼저 보고, 설정 데이터베이스 생성 빌드·계정 추가 시각·사용자 설정 완료 값을 그다음에 보며, 마지막으로 여러 기록 가운데 가장 오래된 시각을 모아 맞춰 봅니다. 여러 기록을 한 줄로 엮는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

## 실습

Android 전체 파일 시스템 추출본이 들어 있는 공개 시험 자료(NIST CFReDS 등)를 골라 아래 질문을 풀어 봅니다.

1. `/data/misc/bootstat/` 에 어떤 파일이 있고, 각 파일의 수정 시각을 유닉스 초와 UTC 날짜로 적으면 무엇인가?
2. `factory_reset`, `build_date`, `factory_reset_boot_complete` 의 수정 시각 가운데 날짜로 읽으면 안 되는 것은 무엇이고, 왜 그런가?
3. `factory_reset` 시각과 계정 기록에서 가장 오래된 계정 추가 시각은 얼마나 떨어져 있는가?
4. `database_creation_buildid` 와 현재 빌드 ID 가 같은가? 다르다면 그 사이에 무슨 일이 있었다고 볼 수 있는가?
5. 이미지에 `/data/misc/recovery/last_log` 가 있다면 그 안에 초기화와 관련된 줄이 있는가?

## 참고 문헌

1. bootstat.cpp — AOSP system/core (main). https://raw.githubusercontent.com/aosp-mirror/platform_system_core/main/bootstat/bootstat.cpp
2. boot_event_record_store.cpp — AOSP system/core (main). https://raw.githubusercontent.com/aosp-mirror/platform_system_core/main/bootstat/boot_event_record_store.cpp
3. bootstat.rc — AOSP system/core (main). https://raw.githubusercontent.com/aosp-mirror/platform_system_core/main/bootstat/bootstat.rc
4. recovery-persist.cpp — AOSP bootable/recovery (main). https://android.googlesource.com/platform/bootable/recovery/+/refs/heads/main/recovery-persist.cpp
5. Settings.java — AOSP frameworks/base (main). https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/provider/Settings.java
6. PersistentDataBlockService.java — AOSP frameworks/base (main). https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pdb/PersistentDataBlockService.java
