---
title: "맥 사용 시간 재구성 (켜짐·잠자기·로그인)"
parent: "시나리오 · 행위 재구성"
nav_order: 2360
---

# 맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)

사건 구간에 맥이 켜져 있었는지, 잠자기 상태였는지, 누군가 로그인해 실제로 쓰고 있었는지를 묻는 조사를 다룹니다. utmpx 와 통합 로그로 켜진 구간과 로그인 세션을 나누고, `pmset -g log` 출력으로 잠자기·깨우기 구간을, KnowledgeC 로 화면이 켜지고 앱이 앞에 있던 구간을 찾습니다. 세 층의 구간을 UTC 로 맞춰 한 타임라인에 겹치고, 층마다 어디까지 확인했는지 표시합니다.

## 조사 질문

사건 구간에 맥이 켜져 있었는지, 잠자기 상태였는지, 누군가 로그인해 실제로 쓰고 있었는지를 묻습니다. "켜져 있었다", "깨어 있었다", "사용자가 조작하고 있었다" 는 서로 다른 사실이고 각각을 보여 주는 기록도 다르기 때문에, 이 페이지는 세 층의 기록을 따로 읽은 뒤 한 타임라인에 겹치는 순서를 다룹니다.

## 먼저 확인할 것

먼저 macOS 버전과 시간대를 확인합니다. KnowledgeC 의 `/device/isLocked` 스트림은 macOS 10.15 부터 있어서, 버전에 따라 잠금 상태를 읽을 수 있는지가 달라집니다. 버전은 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../../02-artifacts/system-account/os-version-install-history.md)에서, 시간대는 [시간대와 시계 설정 (Time Zone·NTP)](../../02-artifacts/system-account/time-zone.md)에서 확인합니다.

다음으로 확보 방식을 확인합니다. `pmset -g log` 는 켜져 있는 맥에서 실행하는 명령입니다 [1]. 라이브 확보 때 이 명령의 출력을 받아 두었는지에 따라 잠자기·깨우기 기록을 읽는 길이 달라지고, 라이브 확보 절차는 [라이브 대응 (Live Response)](../../03-techniques/process-acquisition/live-response/index.md)에 있습니다. 사용자 계정 목록과 시계를 바꾼 흔적이 있는지도 함께 확인하며, 시계 조작은 [시스템 시각 바꾸기 (Time Change)](anti-forensics/time-change.md)에서 다룹니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `/private/var/run/utmpx` | 부팅·로그인·로그아웃·종료 레코드 [2] | 아래 utmpx 절 |
| 2 | 통합 로그의 로그인 기록 | `loginwindow` 프로세스와 `com.apple.login` 서브시스템의 로그인·잠금 해제 기록 | [통합 로그에서 찾을 것 (Unified Log Events)](../../02-artifacts/logs/unified-log-events/index.md) |
| 3 | `/private/var/db/diagnostics/shutdown.log` | 종료 관련 기록 | [통합 로그에서 찾을 것 (Unified Log Events)](../../02-artifacts/logs/unified-log-events/index.md) |
| 4 | `pmset -g log` 출력 | 잠자기·깨우기와 그 밖의 전원 관리 이벤트 [1] | [전원·잠자기 기록 (pmset)](../../02-artifacts/logs/power-events.md) |
| 5 | `/Library/Preferences/SystemConfiguration/com.apple.PowerManagement.plist` | 잠자기 타이머 설정 [1] | [전원·잠자기 기록 (pmset)](../../02-artifacts/logs/power-events.md) |
| 6 | KnowledgeC `/display/isBacklit`, `/device/isLocked` | 화면이 켜진 구간, 잠긴 구간 | [KnowledgeC (knowledgeC.db)](../../02-artifacts/execution/knowledgec/index.md) |
| 7 | KnowledgeC `/app/inFocus`, `/app/usage` | 앞에 떠 있던 앱과 앱 사용 구간 | [어떤 앱을 언제 썼나 (App Usage)](app-usage.md) |
| 8 | 전원 로그 | 전원 상태 기록 | [전원 로그 (PowerLog)](../../02-artifacts/execution/powerlog.md) |

utmpx 와 로그인 기록은 "켜졌다·로그인했다" 를, pmset 기록은 "깨어 있었다·잠들었다" 를, KnowledgeC 는 "화면이 켜져 있었고 앱이 앞에 있었다" 를 보여 줍니다. 세 층을 모두 채우지 못해도 되지만, 어느 층까지 확인했는지는 보고서에 밝힙니다.

### utmpx

`/private/var/run/utmpx` 는 628바이트 레코드가 이어진 파일이고, 첫 레코드는 user 필드에 `utmpx-1.00` 문자열이 들어간 머리 레코드입니다 [2]. 레코드 안 필드는 아래 순서이고, 오프셋은 필드 크기를 순서대로 더한 값입니다.

| 오프셋 | 크기 | 필드 [2] | 내용 |
|---|---|---|---|
| 0 | 256 | user | 사용자 이름(UTF-8) |
| 256 | 4 | terminal_id | 단말 식별자(uint32 LE) |
| 260 | 32 | terminal | 단말 이름(ASCII) |
| 292 | 4 | pid | 프로세스 ID |
| 296 | 4 | type | 레코드 종류 |
| 300 | 4 | date | 초 |
| 304 | 4 | date_microseconds | 마이크로초 |
| 308 | 256 | hostname | 호스트 이름 |
| 564 | 64 | 채움 | — |

type 값은 0(EMPTY)부터 11(SHUTDOWN_TIME)까지 있고, 사용 시간 재구성에 쓰는 값은 2 BOOT_TIME, 6 LOGIN_PROCESS, 7 USER_PROCESS, 8 DEAD_PROCESS, 11 SHUTDOWN_TIME 입니다 [2]. 시각은 1970-01-01 을 기준으로 한 유닉스 시각이고, `date` 에 `date_microseconds` 를 10^-6 곱해 더하면 됩니다 [2][3]. 헥스 편집기로 볼 때는 628바이트 단위로 끊어 오프셋 296 의 type 과 오프셋 300 의 date 를 먼저 읽으면 부팅·로그인 순서가 빠르게 잡힙니다.

utmpx 가 사건 당시의 부팅까지 담고 있는지는 파일 안 가장 이른 BOOT_TIME 레코드로 먼저 추정하고, 담고 있지 않으면 통합 로그 쪽 기록으로 넘어갑니다.

### 전원 관리 기록과 설정

`pmset -g log` 는 잠자기·깨우기와 그 밖의 전원 관리 이벤트의 기록을 보여 주는 명령이고, 이 기록은 관리자와 디버깅 용도입니다 [1]. 라이브 확보 때 함께 받아 두면 좋은 출력은 아래와 같습니다.

| 명령 | 보여 주는 것 [1] |
|---|---|
| `pmset -g log` | 잠자기·깨우기와 그 밖의 전원 관리 이벤트 기록 |
| `pmset -g uuid` | 현재 잠자기/깨우기 UUID. 한 번의 잠자기 주기 안의 기록을 잇는 데 씀 |
| `pmset -g assertions` | 시스템 잠자기·화면 잠자기를 막는 전원 assertion 요약 |
| `pmset -g sched` | 예약된 켜기·깨우기·끄기·잠자기 |
| `pmset -g pslog` | 배터리·UPS 전원 상태 |
| `pmset -g everything` | GETTING 절의 항목 출력을 한 번에 모은 것 |

pmset 으로 바꾼 설정은 `/Library/Preferences/SystemConfiguration/com.apple.PowerManagement.plist` 에 저장됩니다. 설정 이름 `sleep` 은 시스템 잠자기 타이머, `displaysleep` 은 화면 잠자기 타이머이며, 둘 다 분 단위이고 0 이면 꺼져 있다는 뜻입니다 [1]. 이 두 이름은 pmset 명령의 설정 이름이라서 plist 안의 키 이름과 같다고 보지 않고, 실제 plist 에서 어느 키가 어느 설정인지 먼저 확인하고, 최근 버전에서도 파일이 같은 경로에 있는지도 함께 봅니다. 이 값은 사용 흔적이 끊긴 뒤 잠자기 기록이 나타날 때까지의 간격을 해석하는 데 씁니다. 예를 들어 `displaysleep` 이 10 이라면 마지막 조작 뒤 화면이 꺼질 때까지 약 10분 공백이 생기는 것이 설정과 맞는 모습이지만, 설정은 확보 시점의 값이라서 사건 당시에도 같았는지는 따로 확인합니다. 통합 로그에서 잠자기·깨우기를 남기는 프로세스와 문구는 [전원·잠자기 기록 (pmset)](../../02-artifacts/logs/power-events.md)에서 봅니다.

## 분석 흐름

1. macOS 버전과 시간대, 계정 목록을 적고, 라이브 확보 때 받은 `pmset -g` 출력이 있는지 확인합니다.
2. utmpx 를 읽어 BOOT_TIME·SHUTDOWN_TIME 으로 켜져 있던 구간을 나누고, 그 안에 USER_PROCESS·DEAD_PROCESS 레코드로 로그인 세션을 표시합니다.
3. 통합 로그에서 `loginwindow`·`com.apple.login` 기록과 잠금 해제 실패 기록을 읽어 2단계의 세션을 보강하고, `shutdown.log` 로 종료 시점을 맞춰 봅니다. 통합 로그 시각은 마크 연속 시각을 timesync 로 실제 시각 시계(wall clock) 기준 시각으로 바꾼 값이라서, 변환에 쓴 timesync 파일이 해당 부팅을 담고 있는지 확인합니다.
4. `pmset -g log` 출력이 있으면 켜져 있던 구간 안에서 잠자기·깨우기 구간을 나눕니다. `pmset -g uuid` 는 확보 시점에 진행 중인 잠자기 주기의 UUID 하나만 보여 주므로 [1], 이 값은 확보 직전 주기의 기록을 찾는 데만 씁니다. 출력이 없으면 [전원·잠자기 기록 (pmset)](../../02-artifacts/logs/power-events.md)의 방법으로 디스크 기록을 찾습니다.
5. KnowledgeC 의 `/display/isBacklit` 과 `/device/isLocked` 로 깨어 있던 구간 안에서 화면이 켜져 있고 잠기지 않은 구간을 찾습니다.
6. `/app/inFocus` 와 `/app/usage` 로 5단계 구간 안에서 실제로 앞에 떠 있던 앱을 확인합니다.
7. 모든 구간을 UTC 로 맞춰 한 타임라인에 겹치고, 층마다 "확인함", "기록 없음", "확인 못 함" 을 표시합니다. 타임라인은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)을 따릅니다.

> 그림 자리: 켜짐(부팅~종료), 깨어 있음(깨우기~잠자기), 사용 중(화면 켜짐·잠금 해제·앱 앞에 있음) 세 층을 위아래로 겹친 막대 타임라인

## 흔한 오판

맥이 켜져 있었다는 기록을 사용자가 쓰고 있었다는 증거로 보는 경우가 많습니다. 전원 assertion 이 잠자기를 막거나 [1] 예약된 깨우기가 걸려 있으면 [1] 사람이 조작하지 않아도 맥이 깨어 있을 수 있어서, 사용 여부는 화면·잠금·앞에 떠 있던 앱 기록까지 확인한 뒤에 말합니다.

로그인 세션이 길게 이어진 것을 그 시간 내내 사용한 것으로 보는 것도 오판입니다. USER_PROCESS 레코드부터 DEAD_PROCESS 레코드까지는 세션이 열려 있던 구간일 뿐이고, 그 안에 화면이 꺼지거나 잠긴 구간이 있을 수 있습니다.

utmpx 에 사건 당시 레코드가 없다고 해서 그때 맥이 꺼져 있었다고 보지 않습니다. 레코드가 없으면 "이 파일로는 판단할 수 없다" 까지만 말하고 다른 층의 기록으로 넘어갑니다.

## 보고서 문장 예

- "`/private/var/run/utmpx` 에 YYYY-MM-DD HH:MM:SS UTC 의 BOOT_TIME 레코드와 HH:MM:SS UTC 의 사용자 A USER_PROCESS 레코드가 있습니다. 이 기록으로 이 시각에 맥이 켜졌고 계정 A 의 세션이 열렸다는 점은 확인되지만, 이 세션 동안 계속 조작했는지는 이 파일로 판단할 수 없습니다."
- "KnowledgeC 의 `/display/isBacklit` 기록에 HH:MM 부터 HH:MM UTC 까지 화면이 켜진 구간이 있고, 같은 구간 `/app/inFocus` 에 앱 X 가 앞에 있던 기록이 있습니다."

## 함께 볼 페이지

- [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](user-attribution.md) — 세션을 연 계정을 사람과 잇는 방법
- [어떤 앱을 언제 썼나 (App Usage)](app-usage.md) — 사용 구간 안의 앱 사용
- [화면 사용 시간 (Screen Time)](../../02-artifacts/execution/screen-time.md) — 앱별 사용 시간 기록
- [로그인 창 설정 (loginwindow)](../../02-artifacts/system-account/loginwindow.md) — 자동 로그인과 마지막 사용자 설정

## 참고 문헌

1. pmset(1) man page (Xcode man page 미러, keith.github.io — Apple 호스팅 아님) — https://keith.github.io/xcode-man-pages/pmset.1.html
2. mac_apt `plugins/utmpx.py` (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/utmpx.py
3. mac_apt `plugins/helpers/common.py` (ReadMacAbsoluteTime·ReadAPFSTime·ReadUnixTime) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/helpers/common.py
