---
title: "파일 구조"
parent: "앱 사용 기록"
grand_parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 460
---

# 파일 구조 (usagestats)

앱 사용 기록(usagestats)이 디스크에 어떤 폴더와 파일로 남는지, 파일 안의 칸과 시각을 어떻게 읽는지 정리합니다. 소스로 확인한 값은 현행 AOSP 기준(frameworks/base 의 main 가지)이고, 어느 Android 출시 버전에서 바뀌었는지는 대부분 확인하지 못했습니다. 실제 폰에서 본 모양에는 확인 범위를 붙였습니다.

## 한 줄 요약

usagestats 는 사용자별 CE 영역의 `usagestats` 폴더에 일·주·월·연 구간 파일로 쌓이고, 현행 형식(버전 5)은 패키지 이름을 번호로 바꿔 저장하는 프로토콜 버퍼라서 `mappings` 파일과 함께 확보해야 이름을 되살릴 수 있습니다.

## 위치와 버전별 차이

### 경로

현행 AOSP 의 UsageStatsService 는 `Environment.getDataSystemCeDirectory(userId)` 아래 `usagestats` 폴더에 기록하고, 실제 경로로 쓰면 `/data/system_ce/<사용자ID>/usagestats/` 입니다 [3]. CE 영역은 사용자가 잠금을 풀어야 열리는 저장 영역이라서, 암호화 구조는 [저장 공간 암호화](../../../01-foundations/storage/encryption/index.md) 페이지를 함께 봅니다. 예전에는 `/data/system/usagestats/` 아래 사용자별 하위 폴더(`/data/system/usagestats/<사용자ID>/`)를 썼고, ALEAPP 도 `*/system_ce/*/usagestats*` 와 `*/system/usagestats/*` 두 패턴을 모두 찾습니다 [2][3].

서비스는 새 위치에 `migrated` 파일이 없으면 예전 사용자 폴더를 통째로 복사하고, `migrated` 파일에 백업 버전 값(BACKUP_VERSION)을 적은 뒤 예전 폴더를 지웁니다(deleteLegacyUserDir) [3]. 어느 Android 버전부터 system_ce 로 옮겼는지는 소스 주석으로 확인하지 못했습니다.

첫 잠금 해제 전에 생긴 이벤트는 서비스가 메모리에 모아 둡니다. 잠금 해제 전에 사용자가 멈추면(종료 등) 모아 둔 이벤트를 `/data/system_de/<사용자ID>/usagestats/` 폴더에 `pendingevents_<유닉스 밀리초>` 파일로 쓰고, 잠금 해제 때 이 파일을 읽어 합친 다음 이 system_de 쪽 `usagestats` 폴더를 통째로 지웁니다 [3]. 그래서 잠금 해제가 한 번이라도 끝난 기기에서는 이 파일이 남아 있지 않은 것이 보통입니다.

모든 사용자에 걸친 부품 사용 기록 파일 `globalcomponentusage` 는 사용자별 폴더가 아니라 `/data/system/usagestats/` 에 따로 둡니다. 이 파일을 처음 추가할 때 `/data/system_de/usagestats/` 에 잘못 두었던 적이 있어서, 서비스는 새 위치에 없으면 그 옛 위치에서 읽고 옛 폴더는 지우지 않습니다(소스 주석) [3]. 그러니 `/data/system/usagestats/` 폴더가 있다고 해서 사용자별 기록을 옮기기 전의 기기라고 볼 수는 없습니다.

### 폴더 안 구성

현행 AOSP 의 UsageStatsDatabase 가 만드는 파일과 폴더는 다음과 같습니다 [1][3].

| 이름 | 담긴 것 |
|---|---|
| `version` | 스키마 버전과 빌드 지문(build fingerprint) |
| `daily/` `weekly/` `monthly/` `yearly/` | 구간별 통계 파일 |
| `mappings` | 버전 5부터 생깁니다. 토큰 번호와 패키지·클래스 이름 같은 문자열의 대응표입니다 |
| `backups/<토큰>/` | 버전을 올릴 때 기존 파일을 옮겨 두는 곳이고, 토큰은 그때의 밀리초 값입니다 |
| `breadcrumb` | 업그레이드 진행 상태(토큰과 이전 버전)를 적고, 업그레이드가 끝나면 지웁니다 |
| `migrated` | 예전 경로에서 옮겨 왔다는 표시입니다 |

구간 파일의 이름은 그 구간이 시작한 시각(beginTime)을 유닉스 밀리초 숫자 그대로 적은 값입니다. 체크인한 파일에는 접미사(CHECKED_IN_SUFFIX)가 붙지만 그 문자열 값은 확인하지 못했습니다. 파일은 AtomicFile 방식으로 쓰기 때문에 쓰는 도중에는 `.bak` 파일이 함께 생깁니다 [1].

### 형식 버전

| DB 버전 | 형식 | 읽고 쓰는 코드 |
|---|---|---|
| 1~3 | XML | UsageStatsXml |
| 4 | 프로토콜 버퍼 | UsageStatsProto |
| 5 | 프로토콜 버퍼 V2(패키지 이름 등을 토큰으로 바꿔 저장) | UsageStatsProtoV2 |

현행 AOSP 의 기본 버전(DEFAULT_CURRENT_VERSION)은 5이고 백업 버전(BACKUP_VERSION)은 4입니다 [1]. 버전을 올릴 때는 이전 형식으로 읽은 다음, 버전 5 이상으로 올리는 경우 토큰으로 바꿔 새 형식으로 다시 씁니다 [1]. 버전 5가 어느 Android 출시 버전부터 쓰였는지는 확인하지 못했습니다.

ALEAPP 는 프로토콜 버퍼 파일을 문자열을 파일 안에 넣는 "Version 1" 과 바깥의 mappings 파일이 필요한 "Version 2" 로 나눠 부릅니다 [2]. AOSP 의 DB 버전 번호(4·5)와 이름이 다르니 보고서에서 섞어 쓰지 않습니다.

### 보관 기간과 파일 수 한도

현행 AOSP 는 구간마다 파일 수 한도(MAX_FILES_PER_INTERVAL_TYPE)와 정리(prune) 기준을 따로 둡니다 [1].

| 구간 | 최대 파일 수 | 이보다 오래된 파일을 지움 |
|---|---|---|
| daily | 100 | 10일 |
| weekly | 50 | 4주 |
| monthly | 12 | 6개월 |
| yearly | 10 | 2년 |

공유 선택창 선택 기록(chooser counts)은 기본 14일(SELECTION_LOG_RETENTION_LEN) 보관합니다 [1].

### 디스크에 쓰는 시점

서비스는 평소 20분(FLUSH_INTERVAL)마다 메모리의 통계를 파일로 쓰고, 기기 종료(DEVICE_SHUTDOWN)와 사용자 중지(USER_STOPPED) 때도 씁니다 [3]. 그래서 마지막 저장 뒤 최대 약 20분 사이의 이벤트는 파일에 아직 없고 메모리에만 있을 수 있습니다. 개발용 설정(COMPRESS_TIME)을 켜면 이 주기가 10초로 줄어듭니다 [3].

## 구조 — 프로토콜 버퍼 V2

버전 5 파일은 `usagestatsservice_v2.proto` 에 정의된 메시지로 되어 있습니다 [4]. 필드 번호와 varint 를 바이트에서 읽는 법은 [프로토콜 버퍼](../../../01-foundations/data-formats/protobuf.md) 페이지에 있습니다.

**IntervalStatsObfuscatedProto** — 구간 파일 한 개입니다.

| 번호 | 칸 | 뜻 |
|---|---|---|
| 1 | end_time_ms | 구간 끝 시각 |
| 2 | major_version | 주 버전 |
| 3 | minor_version | 부 버전 |
| 10 | interactive | 화면 상호작용 상태의 횟수와 지속 시간 |
| 11 | non_interactive | 화면 비상호작용 상태의 횟수와 지속 시간 |
| 12 | keyguard_shown | 잠금 화면 표시의 횟수와 지속 시간 |
| 13 | keyguard_hidden | 잠금 화면 숨김의 횟수와 지속 시간 |
| 20 | packages | 패키지별 기록 |
| 21 | configurations | 기기 설정 기록 |
| 22 | event_log | 개별 이벤트 |
| 23 | pending_events | 보류된 이벤트 |
| 24 | package_usage | 패키지 사용 기록 |

**UsageStatsObfuscatedProto** — 패키지 하나의 누적 통계입니다.

| 번호 | 칸 | 번호 | 칸 |
|---|---|---|---|
| 1 | package_token | 7 | chooser_actions |
| 3 | last_time_active_ms | 8 | last_time_service_used_ms |
| 4 | total_time_active_ms | 9 | total_time_service_used_ms |
| 5 | last_event | 10 | last_time_visible_ms |
| 6 | app_launch_count | 11 | total_time_visible_ms |
|  |  | 12 | last_time_component_used_ms |

**EventObfuscatedProto** — 이벤트 한 건입니다. 어느 이벤트가 어느 칸을 채우는지는 [이벤트 종류](event-types.md) 페이지에 정리했습니다.

| 번호 | 칸 | 번호 | 칸 |
|---|---|---|---|
| 1 | package_token | 8 | standby_bucket |
| 2 | class_token | 9 | notification_channel_id_token |
| 3 | time_ms | 10 | instance_id |
| 4 | flags | 11 | task_root_package_token |
| 5 | type | 12 | task_root_class_token |
| 6 | config | 13 | locus_id_token |
| 7 | shortcut_id_token | 14 | interaction_extras |

**ObfuscatedPackagesProto** — `mappings` 파일의 형식입니다. 항목(PackagesMap)마다 package_token 과 문자열 배열(strings)이 들어 있고, 토큰 번호로 이 배열에서 문자열을 찾습니다 [4]. 그래서 `mappings` 파일이 없으면 V2 파일의 패키지 이름을 되살릴 수 없습니다 [1][2].

## 시각 해석

파일 안의 시각 칸(time_ms, last_time_active_ms, last_time_visible_ms, end_time_ms 등)은 절대 시각이 아니고, 구간 시작 시각(beginTime, 곧 파일 이름)으로부터의 밀리초 차이입니다. 읽을 때는 아래처럼 파일 이름 값에 더합니다 [5].

```java
event.mTimeStamp = beginTime + proto.readLong(EventObfuscatedProto.TIME_MS);
```

쓸 때는 구간 시작 이후의 시각만 쓰는 것이 원칙이지만, 소스 주석에 따르면 넘김(rollover) 처리 때문에 시작 1시간 전까지는 허용합니다("a grace period of one hour before the begin time is allowed because of rollover logic"). 그래서 차이값이 음수일 수 있습니다 [5]. ALEAPP 는 음수가 아닌 값은 파일 이름에 더하고 음수 값은 절댓값을 그대로 시각으로 쓴다고 설명하며, 결과는 UTC 로 보여 줍니다 [2]. AOSP 는 쓸 때 시각에서 구간 시작을 뺀 값을 적고(차이가 0이면 1을 적습니다), 읽을 때는 부호와 상관없이 구간 시작에 더합니다 [5]. 곧 AOSP 기준으로 음수는 구간 시작보다 앞선 시각이라서, 음수를 절댓값으로 읽는 ALEAPP 와 결과가 다를 수 있고 음수가 나온 이벤트는 두 방법으로 모두 계산해 봅니다.

아래는 명세로 만든 계산 예시이고 검체에서 나온 값이 아닙니다.

| 단계 | 값 |
|---|---|
| 파일 이름(beginTime) | `1735689600000` → 2025-01-01 00:00:00 UTC |
| 이벤트의 time_ms | `5400000` (1시간 30분) |
| 더한 값 | `1735695000000` → 2025-01-01 01:30:00 UTC |

이 시각이 어떤 시계를 따르고 시각 변경에 어떻게 흔들리는지는 [해석 함정](pitfalls.md) 페이지에서 다룹니다.

## 라이브 기기에서 보이는 모양 (dumpsys usagestats)

adb 일반 셸 권한(UID 2000)으로 `dumpsys usagestats` 를 실행하면 파일이 아니라 서비스가 메모리에 든 최근 이벤트와 일간 통계를 글자로 보여 주고, 출력은 약 7,546줄이었습니다 (확인 범위: Android 16, One UI 8.5). 값을 가린 출력의 모양은 다음과 같습니다.

```text
user=#
  Last ## hour events (timeRange="…" )
    time="…" type=<이벤트 이름> package=… class=… flags=…
  mDumpInitLastTimeSaved="…" mDumpInitEndTime="…"
   UsageStats RollOver history :
      …User[#] Rollover scheduled @ …
      …User[#] rolloverStats by event Type:#/ init elapsed time:…/ timeStamp:…/ ExpiryDate:…/ realTime:…/ systemTime:…
      …User[#] Time changed. actualSystemTime:… expectedSystemTime:… actualRealtime:…
  In-memory daily stats
  timeRange="…"
    packages
      package=… totalTimeUsed="…" lastTimeUsed="…" totalTimeVisible="…" lastTimeVisible="…" lastTimeComponentUsed="…" totalTimeFS="…
    ChooserCounts
    configurations
    event aggregations
```

맨 앞의 "Last ## hour events" 절에 이벤트가 한 줄에 하나씩 나오고, time 값은 밀리초 숫자가 아니라 한글이 섞인 날짜 문자열이었습니다. "In-memory daily stats" 절에는 timeRange 가 4개 있었고 각각 packages, ChooserCounts, configurations, event aggregations 하위 절이 붙어 있었습니다 (확인 범위: Android 16, One UI 8.5). 이벤트 줄에 나온 이벤트 이름과 칸은 [이벤트 종류](event-types.md) 페이지에, dumpsys 전반은 [dumpsys 출력](../../logs/dumpsys.md) 페이지에 있습니다.

현행 AOSP 의 dumpsys usagestats 는 `--checkin`, `-c`, `flush`, `apptimelimit`, `file`, `database-info`, `appstandby`, `stats-directory`, `mappings`, `broadcast-response-stats`, `app-component-usage` 인자를 받습니다 [3]. 이 인자들을 adb 일반 권한으로 실행한 결과는 관찰하지 못했습니다.

## 직접 분석해 보기

### 파일로 따라가기

1. `usagestats` 폴더를 통째로 확보합니다. 구간 파일만 뽑고 `mappings` 와 `version` 을 빠뜨리면 이름과 형식 판단이 어려워집니다. 루팅되지 않은 기기에서 adb 일반 권한으로 이 폴더를 읽을 수 있는지는 확인하지 못했고, 확보 방법은 [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지를 봅니다.
2. `version` 파일로 스키마 버전을 확인합니다. 1~3이면 XML, 4 이상이면 프로토콜 버퍼입니다.
3. 구간 파일을 헥스 편집기로 열어 [프로토콜 버퍼](../../../01-foundations/data-formats/protobuf.md) 페이지의 방법으로 필드 번호를 찾고, 위 표와 맞춰 봅니다. `.proto` 없이 필드 번호만 풀어 주는 범용 프로토콜 버퍼 해독기를 써도 됩니다.
4. 토큰 번호는 `mappings` 파일에서 문자열로 바꾸고, 시각 칸은 파일 이름에 더해 절대 시각으로 바꿉니다.

### 공개 도구로 따라가기

ALEAPP 의 usagestats 모듈은 XML 과 프로토콜 버퍼(Version 1·2) 파일을 모두 읽습니다. 먼저 XML 로 읽어 보고 실패(ParseError)하면 프로토콜 버퍼로 읽으며, 경로에 daily·weekly·monthly·yearly 중 어느 것이 들어 있는지로 구간을 정합니다 [2]. 결과는 표 하나로 나오고 'User (UID)', 'Timestamp / Last Time Active', 'Usage Type', 'Package', 'Event Type', 'Class', 'App Launch Count', 'Total Time Visible (ms)', 'Standby Bucket (high 16 bits)', 'Notification Channel', 'Interval' 같은 칸이 붙습니다 [2]. 같은 기록이 여러 구간에서 겹쳐 나올 수 있어서 합산할 때 주의합니다.

## 실습

usagestats 폴더가 들어 있는 공개 검체나 직접 만든 시험 기기의 추출본으로 풀어 봅니다.

1. `version` 파일에 적힌 버전은 몇이고, `mappings` 파일이 있습니까?
2. `daily/` 폴더에서 가장 오래된 파일 이름을 UTC 날짜로 바꾸면 언제이고, 추출 시각과의 차이가 정리 기준(10일)과 맞습니까?
3. 이벤트 하나의 time_ms 를 파일 이름에 직접 더해 UTC 로 바꾼 값이 ALEAPP 결과의 시각과 같습니까?
4. `backups/` 폴더가 있다면 폴더 이름의 토큰은 언제를 가리킵니까?

## 참고 문헌

1. UsageStatsDatabase.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsDatabase.java
2. ALEAPP usagestats.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/usagestats.py
3. UsageStatsService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsService.java
4. usagestatsservice_v2.proto — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/proto/android/server/usagestatsservice_v2.proto
5. UsageStatsProtoV2.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsProtoV2.java
