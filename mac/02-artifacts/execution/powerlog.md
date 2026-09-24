---
title: "전원 로그"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 760
---

# 전원 로그 (PowerLog)

전원 로그 (PowerLog)는 `CurrentPowerlog.PLSQL` 데이터베이스에 기기의 전원·앱 활동을 모아 두는 기록이고, macOS 에서는 `PLAPPLICATIONAGENT_EVENTNONE_APPINFO` 표에 앱의 이름·실행 파일·번들 ID·버전·아키텍처가 시각과 함께 남아서, 이 맥에 어떤 앱이 어떤 버전으로 있었는지를 시간 순서로 볼 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

전원 로그 데이터베이스의 이름은 `CurrentPowerlog.PLSQL` 이고, 공개 분석 도구 APOLLO 의 macOS 전용 모듈 `powerlog_app_info_macos` 가 이 데이터베이스에서 "App Info" 활동을 뽑습니다 [1]. 모듈이 읽는 표 `PLAPPLICATIONAGENT_EVENTNONE_APPINFO` 에는 앱의 이름, 실행 파일, 표시 이름, 번들 ID, 버전 문자열 여러 개, 패키지·앱 종류, 빌드한 기기의 OS 빌드, 아키텍처가 들어 있습니다 [1].

APOLLO 에는 이름이 `powerlog_` 로 시작하는 모듈이 많고, 이름만 보면 앱 사용, 앞에 있던 앱, 앱 생애 주기, 앱 삭제, 프로세스 ID, 사용자 유휴 상태, 덮개 상태, 전원 상태, 화면, 네트워크 사용량, 시간대 같은 기록을 다룹니다 [2].

| APOLLO 모듈(이름만 확인) [2] |
|---|
| `powerlog_app_usage`, `powerlog_app_frontmost`, `powerlog_app_lifecycle`, `powerlog_app_deletion` |
| `powerlog_process_id`, `powerlog_process_monitor_dynamic`, `powerlog_coalition_interval`, `powerlog_kernel_task_monitor` |
| `powerlog_user_idle`, `powerlog_clamshell_state`, `powerlog_power_state`, `powerlog_powernap`, `powerlog_scheduled_wake_events` |
| `powerlog_display`, `powerlog_window_server_timeline` |
| `powerlog_network_usage`, `powerlog_process_data_usage`, `powerlog_wifi_properties`, `powerlog_timezone` |

이 가운데 이름에 `macos` 가 붙은 모듈은 `powerlog_app_info_macos` 하나뿐이고, 나머지 모듈이 macOS 를 지원하는지와 어떤 표를 읽는지는 확인하지 못했습니다. 검체에서 이 모듈들을 돌려 결과가 나오더라도, 표 이름과 칸을 `.schema` 로 직접 확인한 뒤에 씁니다.

## 위치와 버전별 차이

APOLLO 모듈이 파일 이름 `CurrentPowerlog.PLSQL` 만 적고 macOS 의 전체 경로는 적지 않아서 [1], 이 페이지에도 경로를 쓰지 않았습니다. 검체에서는 파일 이름으로 볼륨 전체를 찾고, 이름이 비슷한 압축 보관본이 함께 있는지도 봅니다. 보관본이 있는지와 그 형식은 확인하지 못했습니다.

| macOS 버전 | `powerlog_app_info_macos` 모듈 [1] |
|---|---|
| 10.15 Catalina | 모듈 버전 목록에 있음 |
| 10.16 (= 11 Big Sur) | 모듈 버전 목록에 있음 |
| 12 Monterey 이후 | 목록에 없음. 같은 표가 있는지 확인하지 못함 |

## 구조

데이터베이스 형식은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다. 모듈이 읽는 표와 칸은 아래와 같습니다 [1].

| 표 | 칸 |
|---|---|
| `PLAPPLICATIONAGENT_EVENTNONE_APPINFO` | `TIMESTAMP`, `NAME`, `EXECUTABLE`, `CFDISPLAYNAME`, `LSDISPLAYNAME`, `BUNDLEID`, `NUMERICVERSION`, `SHORTVERSIONSTRING`, `VERSION`, `PACKAGETYPE`, `APPLICATIONTYPE`, `BUILDMACHINEOSBUILD`, `ARCHITECTURE`, `ID` |
| `PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET` | `TIMESTAMP`, `SYSTEM`(시각 보정 값), `ID` |

모듈 쿼리는 두 표를 조건 없는 `LEFT JOIN` 으로 잇고 앱 정보 행마다 `GROUP BY` 로 보정 표의 `ID` 가 가장 큰 행을 골라서, 결과적으로 가장 최근 `SYSTEM` 값 하나를 앱 정보 표의 모든 행에 더합니다 [1]. 결과에는 보정 행의 `TIMESTAMP` 도 `OFFSET_TIMESTAMP` 로 함께 나옵니다 [1]. 번들 ID 를 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 행 하나는 이 시각에 전원 로그가 이 번들 ID·실행 파일·버전·아키텍처의 앱 정보를 기록했다는 뜻입니다 [1]. 같은 번들 ID 의 행을 시간 순서로 늘어놓으면 버전 문자열이 바뀐 때를 볼 수 있고, 지금은 지운 앱의 이름과 번들 ID 가 남아 있을 수도 있습니다(필자 해석, 행이 지워지는 조건은 확인하지 못함).

**증명하지 못하는 것.** 이 표의 행이 앱을 실행할 때 생기는지, 설치하거나 갱신할 때 생기는지는 확인하지 못했습니다. 그래서 행 하나를 "앱을 실행했다" 로 옮기지 않고, 실행 여부는 [통합 로그의 프로세스 실행 기록 (Process Events)](unified-log-process.md)이나 [KnowledgeC (knowledgeC.db)](knowledgec/index.md)로 확인합니다. 어느 사용자가 쓴 앱인지도 이 표에는 없습니다.

보고서에는 "전원 로그의 앱 정보 표에 이 시각(보정 전 UTC, 보정 후 UTC)에 이 번들 ID 와 이 버전이 기록되어 있다" 처럼 쓰고, 보정 값을 어떻게 골랐는지 함께 적습니다.

## 시각 해석

`TIMESTAMP` 는 유닉스 시각(1970-01-01 기준 초)으로 읽히고, 모듈은 `DATETIME(TIMESTAMP, 'UNIXEPOCH')` 로 바꿉니다 [1]. `localtime` 옵션이 없어서 결과는 UTC 이고, 현지 시각은 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)을 보고 바꿉니다. 유닉스 시각을 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에서 다룹니다.

모듈은 여기에 보정 표 `PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET` 의 `SYSTEM` 값을 더해 `ADJUSTED_TIMESTAMP` 를 만들고, 이때 보정 표에서 `ID` 가 가장 큰 행, 곧 가장 최근 보정 값을 씁니다 [1]. 보정 값이 여러 개일 때 각 행이 기록된 때에 맞는 값을 고르지 않아서, 오래된 행에는 맞지 않는 보정 값이 더해질 수 있습니다(모듈 쿼리 구조에서 읽은 해석). `SYSTEM` 보정 값이 왜 생기는지도 확인하지 못했습니다. 그래서 타임라인에는 보정 전 시각과 보정 후 시각을 둘 다 적고, 보정 표의 행을 모두 뽑아 값이 하나인지 여러 개인지 먼저 봅니다.

## 함정과 한계

- **확인한 표가 하나.** 이 페이지에서 구조를 확인한 표는 앱 정보 표와 보정 표 둘이고 [1], 다른 모듈의 표는 이름만 봤습니다 [2].
- **보정 값 고르기.** 도구가 보여 주는 "보정된 시각" 이 가장 최근 보정 값 하나로 계산한 결과인지 확인합니다 [1]. 보정 값이 여러 개면 보정된 시각을 그대로 믿지 않습니다.
- **버전 범위.** 모듈이 확인한 macOS 버전은 10.15 와 10.16(11) 입니다 [1]. 이후 버전은 검체의 `.schema` 로 표가 있는지부터 봅니다.
- **행이 생기는 때.** 행이 생기는 조건을 확인하지 못해서, 행이 없는 날에 맥을 쓰지 않았다고 결론 내리지 않습니다.
- **지운 행.** 지운 행을 찾는 방법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

## 직접 분석해 보기

### 값 하나를 손으로 바꿔 보기

명세로 만든 예시로, 앱 정보 표의 `TIMESTAMP` 가 1700000000 이고 보정 표에서 `ID` 가 가장 큰 행의 `SYSTEM` 이 3600 이라고 합니다. 보정 전 시각은 1700000000 → 2023-11-14 22:13:20 UTC 이고, 보정 후 시각은 1700000000 + 3600 = 1700003600 → 2023-11-14 23:13:20 UTC 입니다. 두 값 가운데 어느 쪽이 맞는지는 같은 시각의 다른 기록과 맞춰 정합니다. 칸의 저장 형(정수·실수)은 확인하지 못해서, 헥스로 볼 때는 SQLite 레코드 헤더의 형 코드를 먼저 봅니다.

### SQL로 한 번

사본을 `sqlite3` 같은 공개 도구로 엽니다. 먼저 보정 표 전체를 보고, 그다음 모듈과 같은 방법으로 앱 정보를 뽑습니다.

```sql
.schema PLAPPLICATIONAGENT_EVENTNONE_APPINFO

SELECT * FROM PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET ORDER BY ID;

SELECT DATETIME(A.TIMESTAMP, 'UNIXEPOCH') AS ts_utc,
       DATETIME(A.TIMESTAMP + T.SYSTEM, 'UNIXEPOCH') AS adjusted_utc,
       A.BUNDLEID, A.NAME, A.EXECUTABLE,
       A.SHORTVERSIONSTRING, A.VERSION, A.ARCHITECTURE
FROM PLAPPLICATIONAGENT_EVENTNONE_APPINFO A
LEFT JOIN (SELECT SYSTEM FROM PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET
           ORDER BY ID DESC LIMIT 1) T ON 1
ORDER BY A.TIMESTAMP;
```

`LEFT JOIN` 으로 이어서 보정 표가 비어 있어도 앱 정보 행이 빠지지 않고, 이때 `adjusted_utc` 는 빈 값으로 나옵니다. APOLLO 의 `powerlog_app_info_macos` 모듈을 돌린 결과와 위 SQL 결과를 맞춰 보면 도구를 검증할 수 있습니다. 검증 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) | 같은 번들 ID 의 앱이 설치된 기록과 버전 |
| [KnowledgeC (knowledgeC.db)](knowledgec/index.md) | 같은 앱이 실제로 쓰인 구간 |
| [화면 사용 시간 (Screen Time)](screen-time.md) | 같은 번들 ID 의 시간대별 사용 시간 |
| [전원·잠자기 기록 (pmset)](../logs/power-events.md) | 맥이 켜져 있던 구간 |
| [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](../../04-scenarios/activity/usage-time.md) | 전원 기록을 묶어 사용 시간을 다시 짜는 순서 |

## 실습

공개 검체(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 볼륨 전체에서 `CurrentPowerlog.PLSQL` 을 찾아 경로를 적고, 이름이 비슷한 파일이 더 있는지 확인해 보세요.
2. `.tables` 결과에서 이름이 `PLAPPLICATIONAGENT` 로 시작하는 표를 모두 적어 보세요.
3. 보정 표의 행 수를 세고, `SYSTEM` 값이 한 가지인지 확인해 보세요.
4. 버전 문자열이 두 가지 이상인 번들 ID 를 찾아, 버전이 바뀐 시각을 설치 기록과 맞춰 보세요.

## 참고 문헌

1. APOLLO 모듈 powerlog_app_info_macos.txt (Sarah Edwards) — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/powerlog_app_info_macos.txt
2. APOLLO 저장소 modules 폴더 목록 (GitHub API) — https://api.github.com/repos/mac4n6/APOLLO/contents/modules
