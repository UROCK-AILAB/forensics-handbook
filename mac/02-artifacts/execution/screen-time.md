---
title: "화면 사용 시간"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 730
---

# 화면 사용 시간 (Screen Time)

화면 사용 시간 (Screen Time) 기록은 `RMAdminStore-Local.sqlite`·`RMAdminStore-Cloud.sqlite` 데이터베이스에 앱별 사용 시간을 한 시간 단위로 모아 두고, 어느 기기·어느 Apple 계정의 기록인지도 함께 남겨서 "이 시간대에 이 앱을 몇 초 썼다" 를 계정·기기와 묶어 읽을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

화면 사용 시간은 앱별 사용 시간을 모으는 기능이고, 모은 기록은 macOS 와 iOS 모두 위 두 SQLite 데이터베이스에 들어갑니다 [1]. 공개 분석 도구 APOLLO 의 `screentime_timed_items` 모듈은 이 데이터베이스에서 번들 ID, 도메인, 앱 사용 시간(초), 앱 분류, 시간 구간의 시작 시각, 앱을 쓰지 않고 기기를 집어 든 횟수를 뽑고, 기록이 속한 기기 이름과 사용자 이름·Apple ID 까지 함께 붙여 보여 줍니다 [1]. 모듈 설명이 "Screen Time - App (By Hour)" 이라서, 사용 기록을 한 시간 단위 구간으로 나눠 보는 구조로 읽습니다 [1].

APOLLO 에는 같은 데이터베이스를 읽는 모듈이 `screentime_by_category`, `screentime_by_hour`, `screentime_counted_items`, `screentime_timed_items` 네 개 있습니다 [2]. 이 페이지는 내용을 직접 확인한 `screentime_timed_items` 의 쿼리를 기준으로 쓰고, 나머지 세 모듈이 무엇을 뽑는지는 확인하지 못했습니다.

## 위치와 버전별 차이

데이터베이스 파일 이름은 `RMAdminStore-Local.sqlite` 와 `RMAdminStore-Cloud.sqlite` 이고, APOLLO 모듈은 이 파일을 macOS 와 iOS 에서 같은 쿼리로 읽습니다 [1]. 모듈이 파일 이름만 적고 macOS 의 전체 경로는 적지 않아서, 이 페이지에도 경로를 쓰지 않았습니다. 검체에서는 파일 이름으로 전체 볼륨을 찾고, 찾은 경로를 보고서에 그대로 적습니다. Local 과 Cloud 두 파일이 각각 무엇을 담는지(이 기기의 기록인지, iCloud 로 받은 다른 기기의 기록인지)도 확인하지 못해서, 두 파일을 모두 수집하고 따로 읽습니다.

| APOLLO 쿼리가 적은 버전 | 쿼리에서 달라지는 점 [1] |
|---|---|
| iOS 12 | `ZCOREDEVICE.ZPLATFORM`, `ZCOREUSER.ZALTDSID` 칸을 읽지 않음 |
| iOS 13, iOS 14 | 두 칸을 함께 읽음 |
| macOS 10.15 Catalina | 두 칸을 함께 읽음 |
| macOS 10.16 (= 11 Big Sur) | 두 칸을 함께 읽음 |
| macOS 12 Monterey 이후 | 모듈 버전 목록에 없음. 같은 표 구조인지 확인하지 못함 |

macOS 12 이후 검체에서는 아래 표 이름과 칸이 그대로 있는지 `.schema` 로 먼저 확인하고, 없는 칸은 추정해서 채우지 않습니다.

## 구조

데이터베이스 형식 자체는 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다루고, 여기서는 APOLLO 쿼리가 쓰는 표와 칸만 정리합니다 [1].

| 표 | 칸 | 뜻 |
|---|---|---|
| `ZUSAGETIMEDITEM` | `ZBUNDLEIDENTIFIER` | 번들 ID |
| `ZUSAGETIMEDITEM` | `ZDOMAIN` | 도메인(무엇이 들어가는지는 확인하지 못함) |
| `ZUSAGETIMEDITEM` | `ZTOTALTIMEINSECONDS` | 앱 사용 시간(초) |
| `ZUSAGETIMEDITEM` | `ZCATEGORY` | `ZUSAGECATEGORY` 와 잇는 키 |
| `ZUSAGECATEGORY` | `ZIDENTIFIER` | 분류 코드 |
| `ZUSAGECATEGORY` | `ZBLOCK` | `ZUSAGEBLOCK` 과 잇는 키 |
| `ZUSAGEBLOCK` | `ZSTARTDATE` | 시간 구간의 시작 |
| `ZUSAGEBLOCK` | `ZNUMBEROFPICKUPSWITHOUTAPPLICATIONUSAGE` | 앱을 쓰지 않고 집어 든 횟수 |
| `ZUSAGEBLOCK` | `ZUSAGE` | `ZUSAGE` 와 잇는 키 |
| `ZUSAGE` | `ZUSER`, `ZDEVICE` | `ZCOREUSER`·`ZCOREDEVICE` 와 잇는 키 |
| `ZCOREDEVICE` | `ZNAME`, `ZIDENTIFIER`, `ZLOCALUSERDEVICESTATE`, `ZPLATFORM` | 기기 이름·기기 ID·로컬 사용자 기기 상태·플랫폼 |
| `ZCOREUSER` | `ZGIVENNAME`, `ZFAMILYNAME`, `ZFAMILYMEMBERTYPE`, `ZAPPLEID`, `ZDSID`, `ZALTDSID` | 이름·성·가족 구성원 종류·Apple ID·DSID·ALT DSID |

표는 사용 시간 항목에서 시작해 분류, 시간 구간, 사용 묶음을 거쳐 사용자와 기기로 이어집니다 [1].

```
ZUSAGETIMEDITEM.ZCATEGORY = ZUSAGECATEGORY.Z_PK
ZUSAGECATEGORY.ZBLOCK     = ZUSAGEBLOCK.Z_PK
ZUSAGEBLOCK.ZUSAGE        = ZUSAGE.Z_PK
ZUSAGE.ZUSER              = ZCOREUSER.Z_PK
ZUSAGE.ZDEVICE            = ZCOREDEVICE.Z_PK
```

분류 코드 `ZUSAGECATEGORY.ZIDENTIFIER` 에는 APOLLO 가 아래처럼 이름을 붙입니다 [1].

| 코드 | APOLLO 가 붙인 이름 |
|---|---|
| `DH0011` / `DH0012` / `DH0013` | Unspecified1 / 2 / 3 |
| `DH1001` | Games |
| `DH1002` | Social Networking |
| `DH1003` | Entertainment |
| `DH1004` | Creativity |
| `DH1005` | Productivity |
| `DH1006` | Education |
| `DH1007` | Reading & Reference |
| `DH1008` | Health & Fitness |
| `DH1009` | Other |

플랫폼 칸 `ZCOREDEVICE.ZPLATFORM` 은 0 이 Unknown, 1 이 macOS, 2 가 iOS, 4 가 Apple Watch 입니다 [1]. 이 칸이 있다는 점에서 한 데이터베이스에 같은 Apple 계정의 다른 기기 기록이 섞일 수 있다고 짐작할 수 있지만, 실제로 섞이는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것.** 행 하나는 이 시간 구간에 이 번들 ID 의 사용 시간이 이만큼(초) 쌓였다는 기록이고, 그 기록이 어느 기기 이름·플랫폼, 어느 사용자 이름·Apple ID 에 묶여 있는지도 함께 보여 줍니다 [1]. 앱을 쓰지 않고 기기를 집어 든 횟수도 시간 구간마다 남아 있습니다 [1].

**증명하지 못하는 것.** 사용 시간은 한 시간 구간 안에서 합친 값이라서, 앱을 정확히 몇 시 몇 분에 열고 닫았는지는 이 기록만으로 알 수 없습니다. 한 행이 정확히 1시간 구간인지도 확인하지 못했습니다. 앱을 쓴 사람이 계정 주인이라는 뜻도 아니라서, 사람을 특정하려면 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../04-scenarios/activity/user-attribution.md)의 방법으로 다른 기록과 맞춰 봅니다. 기기 칸이 이 맥이 아닌 기기를 가리키는 행은 이 맥에서 일어난 사용으로 읽지 않습니다.

보고서에는 "이 데이터베이스에 2023-03-08 20시(UTC)에 시작하는 구간에 이 번들 ID 의 사용 시간이 N초로 기록되어 있고, 이 기록은 기기 이름 X(플랫폼 1, macOS)에 묶여 있다" 처럼 구간·값·기기를 기록 그대로 씁니다.

## 시각 해석

`ZUSAGEBLOCK.ZSTARTDATE` 는 맥 절대 시각(2001-01-01 UTC 기준 초)이고, APOLLO 쿼리는 978307200 을 더해 유닉스 시각으로 바꾼 뒤 `DATETIME(..., 'UNIXEPOCH')` 로 보여 줍니다 [1]. `localtime` 옵션을 쓰지 않아서 결과는 UTC 이고 [1], 현지 시각은 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)을 보고 따로 바꿉니다. 맥 절대 시각을 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에서 다룹니다.

이 시각은 사용 구간이 시작한 때이지 앱을 연 때가 아닙니다. 타임라인에는 "구간 시작" 으로 넣고, 앱이 언제 앞에 있었는지는 초 단위로 남는 다른 기록으로 채웁니다.

## 함정과 한계

- **버전 범위.** APOLLO 쿼리가 확인한 macOS 버전은 10.15 와 10.16(11) 뿐입니다 [1]. 이후 버전에서 표가 바뀌었는지는 검체의 `.schema` 로 확인합니다.
- **두 파일.** Local 과 Cloud 파일의 차이를 확인하지 못했습니다. 한쪽만 읽으면 기록을 놓칠 수 있어서 둘 다 읽고, 행마다 기기 칸을 봅니다.
- **다른 기기의 기록.** `ZCOREDEVICE.ZPLATFORM` 이 2(iOS)나 4(Apple Watch)인 행은 이 맥에서 쓴 기록이 아닐 수 있습니다 [1].
- **개인 정보.** `ZCOREUSER` 에 이름·성·Apple ID·DSID 가 들어 있어서 [1], 보고서에 옮길 때는 조사 범위에 필요한 칸만 씁니다.
- **기능을 끈 경우.** 화면 사용 시간 설정을 끄면 기록이 남지 않는지, 기록을 얼마 동안 두는지는 확인하지 못했습니다. 데이터베이스가 비어 있거나 없다는 사실만으로 앱을 쓰지 않았다고 결론 내리지 않습니다.
- **지운 행.** 지운 행을 찾는 방법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

## 직접 분석해 보기

### 값 하나를 손으로 바꿔 보기

명세로 만든 예시로, `ZSTARTDATE` 값이 699998400 이라면 978307200 을 더한 1678305600 이 유닉스 시각이고, 이 값은 2023-03-08 20:00:00 UTC 입니다. 검체에서 읽은 값도 같은 방법으로 바꾸고, 도구가 보여 준 시각과 한 번 맞춰 봅니다. 칸의 저장 형(정수·실수)은 확인하지 못해서, 헥스로 볼 때는 SQLite 레코드 헤더의 형 코드를 먼저 봅니다.

### SQL로 한 번

사본을 `sqlite3` 같은 공개 도구로 열고, APOLLO 쿼리와 같은 조인으로 뽑습니다. 먼저 `.tables` 와 `.schema ZUSAGETIMEDITEM` 으로 칸이 있는지 확인합니다.

```sql
SELECT DATETIME(B.ZSTARTDATE + 978307200, 'UNIXEPOCH') AS block_start_utc,
       I.ZBUNDLEIDENTIFIER, I.ZDOMAIN, I.ZTOTALTIMEINSECONDS,
       C.ZIDENTIFIER AS category,
       B.ZNUMBEROFPICKUPSWITHOUTAPPLICATIONUSAGE AS pickups_without_app,
       D.ZNAME AS device_name, D.ZIDENTIFIER AS device_id, D.ZPLATFORM,
       U.ZAPPLEID, U.ZDSID
FROM ZUSAGETIMEDITEM I
JOIN ZUSAGECATEGORY C ON I.ZCATEGORY = C.Z_PK
JOIN ZUSAGEBLOCK B ON C.ZBLOCK = B.Z_PK
JOIN ZUSAGE G ON B.ZUSAGE = G.Z_PK
LEFT JOIN ZCOREUSER U ON G.ZUSER = U.Z_PK
LEFT JOIN ZCOREDEVICE D ON G.ZDEVICE = D.Z_PK
ORDER BY B.ZSTARTDATE;
```

iOS 12 형식처럼 `ZPLATFORM` 이나 `ZALTDSID` 칸이 없는 데이터베이스에서는 그 칸을 빼고 실행합니다 [1]. APOLLO 를 쓰면 같은 쿼리를 모듈로 돌릴 수 있고, 결과를 위 SQL 결과와 맞춰 보면 도구를 검증할 수 있습니다. 검증 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [KnowledgeC (knowledgeC.db)](knowledgec/index.md) | 같은 시간 구간에 이 앱이 앞에 있던 기록이 초 단위로 있는지 |
| [바이옴 (Biome)](biome/index.md) | 같은 앱의 사용 기록이 다른 저장소에도 있는지 |
| [통합 로그의 프로세스 실행 기록 (Process Events)](unified-log-process.md) | 구간 안에서 앱이 실제로 실행된 시각 |
| [앱별 네트워크 사용량 (netusage)](../network/netusage.md) | 같은 시간대에 이 앱이 통신한 기록 |
| [어떤 앱을 언제 썼나 (App Usage)](../../04-scenarios/activity/app-usage.md) | 앱 사용 기록을 묶어 읽는 순서 |

## 실습

공개 검체(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 볼륨 전체에서 `RMAdminStore-Local.sqlite` 와 `RMAdminStore-Cloud.sqlite` 를 찾아 경로를 적어 보세요.
2. `.schema` 로 이 페이지의 표와 칸이 모두 있는지 확인하고, 없는 칸을 적어 보세요.
3. `ZCOREDEVICE` 의 행을 모두 뽑아 `ZPLATFORM` 값별로 기기가 몇 대인지 세어 보세요.
4. 사용 시간이 가장 긴 번들 ID 다섯 개를 골라, 같은 구간에 KnowledgeC 기록이 있는지 찾아보세요.

## 참고 문헌

1. APOLLO 모듈 screentime_timed_items.txt (Sarah Edwards) — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/screentime_timed_items.txt
2. APOLLO 저장소 modules 폴더 목록 (GitHub API) — https://api.github.com/repos/mac4n6/APOLLO/contents/modules
