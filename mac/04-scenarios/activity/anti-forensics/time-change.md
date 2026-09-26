---
title: "시스템 시각 바꾸기"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 2410
---

# 시스템 시각 바꾸기 (Time Change)

## 조사 질문

누군가 맥의 날짜·시각을 바꿔 파일과 로그에 실제와 다른 시각이 찍히게 했는지, 바꿨다면 언제 어느 방향으로 얼마나 옮겼는지를 묻습니다. 시각이 바뀐 구간의 기록은 모두 해석이 달라지기 때문에, 시각 조작 여부는 다른 타임라인 결론보다 먼저 확인합니다.

## 먼저 확인할 것

먼저 시간대만 바뀐 것인지 시계 자체가 바뀐 것인지 나눕니다. 시간대를 바꾸면 화면에 보이는 현지 시각이 달라지고 시계를 바꾸면 기록에 저장되는 값이 달라져서, 이 페이지에서는 두 경우를 서로 다른 사건으로 나눠 다룹니다. 시간대 설정을 읽는 법은 [시간대와 시계 설정 (Time Zone·NTP)](../../../02-artifacts/system-account/time-zone.md)에 있습니다.

다음으로 macOS 버전과 사용자 계정을 적고, 라이브 시스템을 다루는지 디스크 이미지를 다루는지 확인합니다. 라이브 시스템이라면 `systemsetup -getusingnetworktime` 으로 네트워크 시각 동기가 켜져 있는지, `-getnetworktimeserver` 로 어느 시각 서버를 쓰는지 볼 수 있고, 이 명령은 최소 admin 권한이 필요합니다 [1]. 라이브 대응 순서는 [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md)에 있습니다.

## 시각을 바꾸는 수단

`systemsetup` 에는 날짜·시각과 관련된 조회·설정 옵션이 짝지어 있습니다 [1]. 조사에서는 이 옵션들이 무엇을 바꿀 수 있는지 알아 두고, 어느 설정이 조작 대상이었을지 추정할 때 씁니다.

| 대상 | 조회 | 설정 [1] |
|---|---|---|
| 날짜 | `-getdate` | `-setdate`, 형식 `mm:dd:yy` |
| 시각 | `-gettime` | `-settime`, 형식 `hh:mm:ss` (24시간제) |
| 시간대 | `-gettimezone` | `-settimezone` |
| 네트워크 시각 사용 | `-getusingnetworktime` | `-setusingnetworktime`, 값 `on`·`off` |
| 네트워크 시각 서버 | `-getnetworktimeserver` | `-setnetworktimeserver` |

시각 조작을 의심할 때는 날짜·시각 설정과 함께 네트워크 시각 동기를 끈 흔적도 봅니다. 최근 macOS 에서 `systemsetup` 에 전체 디스크 접근 권한 같은 추가 제약이 있는지, 시스템 설정의 날짜·시간 패널이나 `date` 명령으로 바꾼 경우에 무엇이 남는지, 시각 동기 데몬의 설정·상태 파일이 어디 있는지는 실제 데이터로 확인해야 합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `/private/etc/localtime` | 현재 시간대 [2] | [시간대와 시계 설정 (Time Zone·NTP)](../../../02-artifacts/system-account/time-zone.md) |
| 2 | `/Library/Preferences/.GlobalPreferences.plist` | 사용자가 고른 시간대 도시와 지역 설정 [2] | 아래 "시간대 설정" |
| 3 | `/private/var/run/utmpx` | 로그인·부팅 기록과 시각 변경 전후 레코드 종류 [3] | 아래 "utmpx" |
| 4 | 통합 로그의 timesync 파일 | 부팅마다 연속 시각과 실제 시각의 짝 | [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md) |
| 5 | 파일 시스템·로그·앱 DB 시각 | 기록 사이에 순서가 뒤집히는 곳 | [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) |

### 시간대 설정

`/private/etc/localtime` 은 시간대를 가리키고, 이 파일은 심볼릭 링크가 가리키는 경로나 tzfile 내용으로 읽습니다 [2]. `/Library/Preferences/.GlobalPreferences.plist` 에는 `com.apple.preferences.timezone.selected_city` 키가 있고 그 안에 `CountryCode`, `Latitude`, `Longitude`, `Name`, `RegionalCode`, `TimeZoneName`, `Version` 이 들어 있으며, 같은 파일에 `com.apple.TimeZonePref.Last_Selected_City`, `Country`, `AppleLocale` 도 있습니다 [2]. 두 곳의 시간대가 서로 다르거나 사건 당시 사용자의 위치와 맞지 않으면 시간대를 바꾼 적이 있는지 확인할 단서가 되지만, 이 값들만으로는 시계 자체를 바꿨는지 알 수 없습니다.

### utmpx

`/private/var/run/utmpx` 는 고정 크기 레코드가 이어진 파일이고, 레코드 구조는 아래와 같습니다 [3]. 오프셋은 필드 크기를 차례로 더해 계산한 값이라 레코드 안의 위치만 뜻합니다. 파일의 첫 레코드는 user 필드에 `utmpx-1.00` 문자열이 든 머리 레코드이고, 실제 기록은 그다음 레코드부터 이어집니다 [3].

| 레코드 안 오프셋 | 크기 | 필드 | 내용 [3] |
|---|---|---|---|
| 0 | 256 | user | 문자열 (UTF-8) |
| 256 | 4 | terminal_id | 정수 (리틀 엔디언, 부호 없음) |
| 260 | 32 | terminal | 문자열 (ASCII) |
| 292 | 4 | pid | 정수 |
| 296 | 4 | type | 정수, 레코드 종류 |
| 300 | 4 | date | 정수, 유닉스 시각 (초) |
| 304 | 4 | date_microseconds | 정수, 마이크로초 |
| 308 | 256 | hostname | 문자열 (UTF-8) |
| 564 | 64 | (패딩) | — |

필드 크기를 모두 더하면 레코드 하나가 628바이트입니다. `date + date_microseconds × 10^-6` 이 유닉스 시각이고 [3], 유닉스 시각은 UTC 기준이라 현지 시각으로 바꿀 때는 위에서 확인한 시간대를 씁니다. 시각 값 읽는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

type 필드의 값과 이름은 아래와 같습니다 [3].

| 값 | 이름 | 값 | 이름 |
|---|---|---|---|
| 0 | EMPTY | 6 | LOGIN_PROCESS |
| 1 | RUN_LVL | 7 | USER_PROCESS |
| 2 | BOOT_TIME | 8 | DEAD_PROCESS |
| 3 | OLD_TIME | 9 | ACCOUNTING |
| 4 | NEW_TIME | 10 | SIGNATURE |
| 5 | INIT_PROCESS | 11 | SHUTDOWN_TIME |

OLD_TIME(3)과 NEW_TIME(4)은 utmpx 형식에서 시각을 바꾸기 전과 바꾼 뒤를 적는 레코드 종류이고, 두 레코드가 짝으로 있으면 시각 변경의 직접 근거가 됩니다. 다만 macOS 가 시각을 바꿀 때 실제로 이 레코드를 쓰는지는 실제 데이터로 확인해야 합니다. `/private/var/run` 이 재부팅 때 비워지는지도 알려져 있지 않아서, utmpx 가 사건 당시의 부팅까지 담고 있는지는 파일 안의 BOOT_TIME 레코드로 먼저 추정합니다. mac_apt 는 결과를 User, Terminal_ID, Terminal, PID, Type, Type_Name, Date, Hostname 필드로 내놓습니다 [3].

## 분석 흐름

1. 시간대 설정 두 곳을 읽어 현재 시간대를 정하고, 사건 당시 사용자의 위치와 맞는지 봅니다.
2. utmpx 를 파서로 읽고, 헥스 편집기로도 첫 머리 레코드 다음부터 628바이트 단위로 끊어 type 필드(레코드 안 오프셋 296)를 차례로 읽어 OLD_TIME·NEW_TIME 레코드가 있는지 확인합니다.
3. 레코드가 있으면 두 레코드의 date 값 차이로 시각을 얼마나, 어느 방향으로 옮겼는지 계산하고, 앞뒤 BOOT_TIME·USER_PROCESS 레코드와 순서가 맞는지 봅니다.
4. 통합 로그의 timesync 파일에서 부팅별 연속 시각과 실제 시각의 짝을 확인합니다. 실제 시각 시계(wall clock)가 뛰어도 연속 시각은 계속 늘어나므로, 두 값을 대조하면 시각이 갑자기 뛴 곳을 찾을 수 있을 것으로 보입니다.
5. 파일 시스템 시각, 로그 시각, 앱 데이터베이스 시각을 한 타임라인에 올려, 나중에 만든 파일이 더 이른 시각을 지니는 것처럼 순서가 뒤집히는 곳을 찾습니다.
6. 찾은 구간마다 "시간대만 달랐다", "시계가 앞뒤로 움직였다", "판단할 근거가 없다" 중 어디에 해당하는지 적고, 그 구간에 걸린 다른 결론을 다시 검토합니다.

> 그림 자리: 연속 시각은 일정하게 늘어나는데 실제 시각 시계 값이 한 지점에서 과거로 뛰는 모양을 나란히 그린 그래프

## 흔한 오판

현지 시각으로 표시한 두 도구의 결과가 어긋날 때 시계 조작으로 보는 경우가 많습니다. 도구마다 시간대를 적용하는 방식이 달라 생긴 차이일 수 있어서, 모든 시각을 UTC 로 맞춘 뒤에도 순서가 뒤집히는지 먼저 확인합니다.

OLD_TIME·NEW_TIME 레코드가 없다고 해서 시각을 바꾸지 않았다고 보지도 않습니다. macOS 가 이 레코드를 쓰는지, utmpx 가 부팅을 넘어 남는지가 알려져 있지 않아서, 레코드가 없으면 "이 파일에서는 근거를 찾지 못했다" 까지만 말합니다.

기록 사이 순서가 한 곳에서 한 번 뒤집혔다고 곧바로 조작으로 보지도 않습니다. 한 곳의 어긋남만으로는 시각 조작과 다른 원인을 가려낼 수 없어서 여러 종류의 기록에서 같은 구간이 함께 어긋나는지 확인하고, 문서 날짜를 따로 따지는 방법은 [이 문서의 날짜를 믿을 수 있나 (Document Date)](../document-date.md)에 있습니다.

## 보고서 문장 예

- "`/private/var/run/utmpx` 에 OLD_TIME 레코드(YYYY-MM-DD HH:MM:SS UTC)와 NEW_TIME 레코드(YYYY-MM-DD HH:MM:SS UTC)가 이어서 기록돼 있습니다. 두 값의 차이로 보면 이 시점에 누군가 시스템 시각을 약 N시간 과거로 옮긴 기록입니다."
- "확보한 자료에서 시스템 시각을 바꾼 직접 기록은 찾지 못했습니다. 다만 utmpx 의 보존 범위를 확인하지 못해, 이 결과만으로 시각을 바꾸지 않았다고 판단할 수는 없습니다."

## 함께 볼 페이지

- [증거를 없애려 했나 (Anti-Forensics)](index.md) — 이 허브의 다른 수단과 전체 흐름
- [로그 지우기 (Log Clearing)](log-clearing.md) — 시각 조작과 로그 공백이 함께 보일 때
- [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](../usage-time.md) — 부팅·로그인 기록으로 시각을 맞춰 볼 때
- [전원·잠자기 기록 (pmset)](../../../02-artifacts/logs/power-events.md) — 시각이 뛴 구간 앞뒤의 전원 상태

## 참고 문헌

1. SS64 — macOS `systemsetup` 명령 — https://ss64.com/mac/systemsetup.html
2. mac_apt `plugins/basicinfo.py` — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/basicinfo.py
3. mac_apt `plugins/utmpx.py` (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/utmpx.py
