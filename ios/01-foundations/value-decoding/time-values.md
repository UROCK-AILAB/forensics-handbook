---
title: "시각 값"
parent: "기반 · 값 읽는 법"
nav_order: 180
---

# 시각 값 (Mac 절대 시각·Unix·기타)

iOS 의 시각 값은 대부분 2001-01-01 UTC 부터 센 초이지만, 같은 백업 안에 Unix 초·나노초·plist 날짜 형이 함께 섞여 있어서 값마다 기준점과 단위를 먼저 가린 뒤에 바꿔야 합니다.

## 이 형식을 쓰는 아티팩트

Apple 의 Core Foundation 은 2001-01-01 00:00:00 GMT 를 참조 시각으로 삼고, 이 시각부터 센 초를 배정밀도 실수(double)로 담는 값을 CFAbsoluteTime 이라고 부릅니다 [1]. 이 핸드북에서는 이 값을 Mac 절대 시각 (Mac Absolute Time) 이라고 부르고, 공개 도구 iLEAPP 는 같은 값을 Cocoa 시각 또는 Core Data 시각이라는 이름으로 다룹니다 [3].

관찰한 로컬 백업에서 시각이 들어갈 이름을 단 칸과 키는 아래와 같습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 이름과 형만 확인했고 값은 읽지 않아서, 칸마다 단위와 기준점은 따로 확인해야 합니다.

| 위치 | 표 또는 키 | 시각 칸·키 |
|---|---|---|
| sms.db | `message` | `date`, `date_read`, `date_delivered`, `date_played` |
| sms.db | `chat_message_join` / `chat_recoverable_message_join` / `attachment` | `message_date` / `delete_date` / `created_date`, `start_date` |
| TCC.db | `access` / `expired` | `last_modified`, `last_reminded` / `last_modified`, `expired_at` |
| `MobileDeviceDomain` :: `ProvisioningProfiles/mis.db` | `profiles` / `online_auth` | `install_time`, `expires` / `last_success_monotonic_time` |
| 블루투스 DB (`com.apple.MobileBluetooth.ledevices.paired.db`·`other.db`) | `PairedDevices`·`OtherDevices` | `LastSeenTime`, `LastConnectionTime` |
| Shortcuts.sqlite | `ZSHORTCUT` | `ZCREATIONDATE`, `ZMODIFICATIONDATE`, `ZLASTRUNEVENTDATE` |
| DataUsage.sqlite | `ZPROCESS` | `ZFIRSTTIMESTAMP`, `ZTIMESTAMP` |

`Z` 로 시작하는 표는 Core Data 가 만든 표이고, iLEAPP 는 이런 표의 날짜 칸을 Mac 절대 시각으로 전제하고 바꿉니다 [3]. 다만 관찰한 백업의 개별 칸 값으로 이 전제를 확인하지는 않았습니다.

plist 쪽에서는 plist 자체의 날짜 형(datetime)으로 적힌 키가 458줄 있었고, 이름에 Date·Time 이 들어가는데 실수(float)로 적힌 키가 111줄, 정수(int)로 적힌 키가 135줄 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 날짜 형의 예는 `WebsiteNameProviderLastUpdateTime`, com.apple.MobileBackup.plist 의 `AccountEnabledDate` 이고, 실수의 예는 `AMSMetricsIdentifierDateLastSynced`, `AppUsageSyncTime`, `HDCloudSyncFullSyncStartTime` 이며, 정수의 예는 RootDomain 의 com.apple.backupd.plist 에 있는 `CKStartupTime` 입니다. 저장 형식은 [속성 목록 파일](../data-formats/plist.md) 과 [SQLite 데이터베이스](../data-formats/sqlite/index.md) 에서 다룹니다.

## 구조

### 기준점과 단위

| 이름 | 기준점 | 단위 | 근거 |
|---|---|---|---|
| Mac 절대 시각 (CFAbsoluteTime) | 2001-01-01 00:00:00 GMT | 초, double. 음수는 기준점 이전 | [1] |
| Mac 절대 시각의 나노초 값 | 2001-01-01 | 나노초. 10^9 로 나눠야 초가 됨 | [2] |
| Unix 시각 | 1970-01-01 UTC | 초·밀리초·마이크로초·나노초 | [3] |
| plist 날짜 형 (datetime) | plist 형식이 정함 | iLEAPP 는 마이크로초를 떼고 UTC 로 봄 | [3] |
| 문자열 시각 | 없음 | `'%b %d %Y %H:%M:%S'` 같은 글자 형식 | [3] |

두 기준점 사이는 978307200초이고, Unix 초는 Mac 절대 초에 978307200 을 더해 얻습니다 [2][3]. iLEAPP 의 Cocoa 변환 함수와 "webkit 시각" 변환 함수가 모두 이 값을 더하는 방식으로 계산합니다 [3].

### 자릿수로 가리는 단위

iLEAPP 의 Unix 시각 함수는 값의 절댓값으로 단위를 가리고, 10^16 이상이면 나노초, 10^13 이상이면 마이크로초, 10^10 이상이면 밀리초, 그보다 작으면 초로 봅니다 [3]. 이 판별은 Unix 시각 함수에 들어 있고, Cocoa 시각 함수도 나노초를 스스로 가리는지는 확인하지 못했습니다.

sms.db 에서는 iOS 11 부터 같은 시각 칸 안에 9자리 값(Mac 절대 초)과 18자리 값(Mac 절대 나노초)이 섞여 들어가고, 보낸 메시지에서는 0 이 보이기도 했다는 보고가 있습니다 [2]. 관찰한 iOS 27.0 백업에서 이 칸들의 자릿수는 값을 읽지 않아 확인하지 않았습니다.

| iOS 버전 | sms.db 시각 칸의 값 | 근거 |
|---|---|---|
| iOS 11 이전 | 9자리 Mac 절대 초([2] 가 전통적인 형식이라고 부르는 값) | [2] |
| iOS 11 부터 | 9자리 초와 18자리 나노초가 같은 칸 안에 섞임 | [2] |

메시지 DB 의 칸별 해석은 [메시지](../../02-artifacts/communications/messages/index.md) 에서 다룹니다.

## 읽는 법

값 하나를 시각으로 바꿀 때는 아래 순서를 따릅니다.

1. **형을 봅니다.** plist 의 날짜 형이면 plist 가 날짜로 적은 값이라 그대로 읽고, 실수나 정수면 숫자만 있으니 2번으로 갑니다.
2. **자릿수로 단위를 가립니다.** 18자리 안팎이면 나노초, 9~10자리면 초일 가능성이 큽니다.
3. **기준점을 정합니다.** 자릿수만으로는 2001 기준인지 1970 기준인지 가릴 수 없어서, 같은 표의 다른 칸이나 같은 사건을 적은 다른 기록과 맞춰 봅니다.
4. **UTC 로 바꿉니다.** Mac 절대 초라면 978307200 을 더해 Unix 초로 만든 뒤 UTC 로 바꿉니다.
5. **시간대는 따로 입힙니다.** iLEAPP 도 먼저 UTC 로 바꾼 뒤에 원하는 시간대를 따로 적용합니다 [3].

아래는 명세로 만든 계산 예시이고, 특정 검체에서 나온 값이 아닙니다.

```
Mac 절대 초  700000000
+ 978307200  = Unix 초 1678307200  → 2023-03-08 20:26:40 UTC

Mac 절대 나노초 700000000000000000
÷ 10^9       = 700000000 (Mac 절대 초) → 위와 같은 시각
```

SQLite 에서는 `datetime` 함수로 같은 계산을 합니다. 아래 식은 초와 나노초가 섞인 칸을 자릿수로 나눠 UTC 로 바꾸는 예입니다.

```sql
SELECT date,
       CASE WHEN length(date) = 18
            THEN datetime(date / 1000000000 + 978307200, 'unixepoch')
            ELSE datetime(date + 978307200, 'unixepoch')
       END AS date_utc
FROM message;
```

[2] 에 실린 식은 끝에 `'localtime'` 을 붙여서 분석하는 컴퓨터의 시간대로 바꿉니다. 결과를 여러 기록과 엮을 때는 UTC 로 두고 시간대를 따로 적는 편이 헷갈림이 적습니다.

### 백업 자체의 시각

기록을 해석할 때 기준으로 삼을 백업 시각도 있습니다. 관찰한 백업에는 Manifest.plist 에 `Date` 키가, Info.plist 에 `Last Backup Date` 키가 있었고, com.apple.MobileBackup.plist 에는 `RestoreInfo` 아래 `RestoreDate` 키와 `BackupStateInfo`·`RestoreStateInfo` 아래 `date` 키가 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 백업 파일의 짜임은 [로컬 백업](../backups/local-backup/index.md) 에서, 복원 흔적으로 읽는 법은 [초기화와 복원 흔적](../../02-artifacts/system-account/erase-restore.md) 에서 다룹니다.

## 포렌식에서 중요한 점

기준점을 잘못 고르면 시각이 31년 가까이 어긋나고, 앞 예시의 Mac 절대 초 700000000 을 Unix 초로 읽으면 1992-03-07 20:26:40 UTC 가 나옵니다. 스마트폰 기록이 1990년대 날짜로 보이면 기준점을 먼저 의심합니다.

Mac 절대 초는 2004-03-03 무렵부터 9자리이고 2032-09-09 01:46:40 UTC 에 10자리가 되며, Unix 초는 지금 10자리입니다. 두 값의 자릿수가 비슷해서 크기로 단위를 가리는 방식은 초와 나노초를 나눌 수 있어도 2001 기준과 1970 기준은 나누지 못합니다.

값이 UTC 인지 현지 시각인지도 함께 적습니다. Mac 절대 시각과 Unix 시각은 시간대가 없는 값이고, iLEAPP 는 plist 날짜 형도 시간대 정보 없이 UTC 로 봅니다 [3]. 기기의 시간대 설정은 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md) 에서, 여러 기록을 한 줄로 엮는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 함정

- **"WebKit 시각" 이라는 이름을 믿지 않습니다.** iLEAPP 의 webkit 변환 함수는 2001 기준으로 계산하는데 [3], 다른 도구나 다른 OS 에서는 같은 이름이 1601 기준 값을 가리키기도 합니다. iOS 의 어느 DB 가 1601 기준 값을 쓰는지는 확인하지 못했으니, 이름 대신 값과 기준점을 확인합니다.
- **숫자 plist 키는 키마다 따로 확인합니다.** 실수·정수로 적힌 키는 기준점이 형에 드러나지 않고, 정수 키 가운데에는 `CAMUserPreferenceTimerDuration`, `Database.BusyTimeout` 처럼 시각이 아니라 길이나 횟수인 값도 섞여 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0).
- **이름에 monotonic 이 붙은 칸을 벽시계 시각으로 단정하지 않습니다.** mis.db 의 `last_success_monotonic_time`, `last_migration_monotonic_time` 은 이름으로 보아 벽시계 시각이 아닐 수 있지만, 뜻은 확인하지 못했습니다.
- **같은 칸 안에서도 단위가 바뀔 수 있습니다.** sms.db 처럼 초와 나노초가 섞이는 칸이 있어서 [2], 칸 전체에 한 가지 변환식을 일괄로 쓰지 않습니다.

## 도구

iLEAPP 의 `scripts/ilapfuncs.py` 에는 Cocoa 시각(`convert_cocoa_core_data_ts_to_utc`), Unix 시각(`convert_unix_ts_in_seconds`), plist 날짜(`convert_plist_date_to_utc`), 로그 문자열(`convert_log_ts_to_utc`) 변환 함수가 따로 있어 [3], 기준점과 단위를 어떻게 가리는지 코드로 확인할 수 있습니다. DB 칸은 SQLite 의 `datetime(..., 'unixepoch')` 로 직접 바꿔 보고, 도구 결과와 한 번씩 맞춰 봅니다.

## 참고 문헌

1. Apple Developer — Date Representations (Dates and Times Programming Guide for Core Foundation) — https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFDatesAndTimes/Concepts/DataReps.html
2. Smarter Forensics — Time is NOT on our side when it comes to messages in iOS 11 (2017-09) — https://smarterforensics.com/2017/09/time-is-not-on-our-side-when-it-comes-to-messages-in-ios-11/
3. iLEAPP (Alexis Brignoni) — scripts/ilapfuncs.py (main 브랜치) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/ilapfuncs.py
