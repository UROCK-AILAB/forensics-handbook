---
title: "통합 로그의 프로세스 실행 기록"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 780
---

# 통합 로그의 프로세스 실행 기록 (Process Events)

## 한 줄 요약

통합 로그 (Unified Log) 의 기록 하나하나에는 그 기록을 남긴 프로세스의 이름·PID·실행 파일이 붙어 있어서, 어떤 프로그램이 어느 시각에 돌고 있었는지를 간접으로 보여 줍니다.

## 무엇을 기록하나 · 왜 생기나

통합 로그는 프로세스 실행만 따로 적는 감사 로그가 아닙니다. 통합 로그 형식에는 exec·fork·launch 같은 "프로세스 실행 전용" 기록 형식이 없고, 모든 기록은 어떤 프로세스가 남긴 로그 메시지입니다. [2] 그래서 실행 사실은 두 가지로 드러납니다. 하나는 그 프로그램이 스스로 로그를 남긴 경우이고, 다른 하나는 실행을 맡거나 검사한 시스템 프로세스가 그 일을 로그에 적은 경우입니다. 윈도우 보안 로그의 4688 처럼 "프로세스 생성" 을 뜻하는 전용 이벤트는 통합 로그 형식에 없습니다.

기록마다 붙는 프로세스 정보는 Apple 이 정한 속성으로 볼 수 있습니다. `OSLogEntryFromProcess` 프로토콜은 기록을 남긴 프로세스 이름(`process`), 프로세스 번호(`processIdentifier`), 기록을 실제로 찍은 바이너리 이름(`sender`), 스레드 번호(`threadIdentifier`), 활동 번호(`activityIdentifier`) 를 내어 줍니다. [1] 파일 안에서는 여기에 유효 사용자 번호(euid) 와 실행 파일 UUID 까지 들어 있고, 실행 파일 경로는 UUID 텍스트 파일에서 찾습니다. [2]

## 위치와 버전별 차이

프로세스 정보는 통합 로그 본문과 같은 파일에 들어 있어서 따로 챙길 위치가 없습니다. 로그 본문(`.tracev3`)은 `/private/var/db/diagnostics/` 아래에, 실행 파일 경로와 형식 문자열은 `/private/var/db/uuidtext/` 아래에 있고, 폴더 구성·보관 방식은 [통합 로그 형식](../../01-foundations/data-formats/unified-log/index.md) 에서 다룹니다. [7]

| macOS | 이 페이지와 관련된 차이 | 출처 |
|---|---|---|
| 10.12 Sierra | 통합 로그가 처음 나왔고, `log show` 출력 필드는 16개였습니다 | [3][7] |
| 10.15 Catalina | `OSLogEntryFromProcess`·`OSLogStore` 로 프로그램에서 프로세스 속성을 읽을 수 있게 됐고, `log show` 출력 필드가 27개로 늘었습니다 | [1][3][8] |
| 12 Monterey | 공유 캐시 문자열 파일(dsc) 형식이 v2 로 바뀌었고, tracev3 에 SimpleDump 청크가 더해졌습니다 | [2][7] |
| 13 Ventura 이후 | 공개된 형식 명세는 13 까지 다루고, 그 뒤 버전의 변화는 공개 자료가 없습니다 | [2] |

## 구조

### 기록 하나에 붙는 프로세스 속성

| 속성 | Apple 설명 | 형식 |
|---|---|---|
| `process` | 기록을 남긴 프로세스의 이름 | `String` |
| `processIdentifier` | 기록을 남긴 프로세스의 번호(PID) | `pid_t` |
| `sender` | 기록을 남긴 바이너리 이미지의 이름 | `String` |
| `threadIdentifier` | 기록을 남긴 스레드의 번호 | `UInt64` |
| `activityIdentifier` | 기록과 이어진 활동 번호 | `os_activity_id_t` |

이 속성은 `OSLogEntryLog`, `OSLogEntryActivity`, `OSLogEntrySignpost` 에 모두 붙습니다. [1] `process` 는 기록을 남긴 프로세스이고 `sender` 는 그 기록을 실제로 찍은 바이너리라서, 앱이 불러 쓴 라이브러리가 기록을 남기면 둘이 다르게 나옵니다. 누가 이 프로세스를 띄웠는지(부모 프로세스) 나 명령줄 인자를 담는 속성은 이 프로토콜에 없습니다. [1]

`log show` 의 조건식 (predicate) 에서는 같은 정보를 `process`, `processImagePath`, `sender`, `senderImagePath` 로 거릅니다. [5]

### tracev3 안의 프로세스 정보

tracev3 의 카탈로그 (Catalog) 청크에는 프로세스마다 "프로세스 정보 항목" 이 있습니다. [2]

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 4 | 2 | 카탈로그 UUID 배열에서 주 실행 파일 UUID 의 순번 |
| 6 | 2 | 카탈로그 UUID 배열에서 dsc UUID 의 순번(`0xffff` 면 없음) |
| 8 | 8 | proc_id 첫째 수 |
| 16 | 4 | proc_id 둘째 수 |
| 20 | 4 | 프로세스 번호(pid) |
| 24 | 4 | 유효 사용자 번호(euid) |
| 32 | 4 | UUID 정보 항목 수 |

UUID 정보 항목은 16바이트이고, 오프셋 8 에 UUID 순번, 오프셋 10 에 적재 주소의 하위 32비트가 있으며, UUID 배열 뒤에는 서브시스템 항목 수가 옵니다. [2]

로그 메시지를 담는 Firehose 청크는 청크 헤더 첫 바이트부터 세어 오프셋 16 과 24 에 proc_id 의 첫째·둘째 수를 두고, 이 두 수로 카탈로그의 프로세스 정보 항목과 이어집니다. 트레이스포인트마다 오프셋 8 에 스레드 번호(8바이트) 가 따로 있습니다. [2]

실행 파일이나 라이브러리의 경로 문자열은 uuidtext 파일 꼬리(footer) 에 "Image (process or library) path" 로 들어 있고, 항목 서술자의 범위 시작 오프셋과 항목 크기로 찾아갑니다. [2] 정리하면 tracev3 에서 pid·euid·실행 파일 UUID 를 얻고, 그 UUID 로 uuidtext 를 열어 경로를 얻는 순서입니다.

## 증거로서 의미

**증명하는 것**

어떤 기록의 프로세스 정보가 있으면, 그 시각에 그 이름·PID 의 프로세스가 그 실행 파일(경로와 UUID) 로 떠 있으면서 기록을 남겼다고 말할 수 있습니다. 기록을 실제로 찍은 코드는 그 프로세스가 불러 쓴 라이브러리일 수도 있어서, 이 부분은 `sender` 로 따로 봅니다. [1] euid 로 그 프로세스가 어느 사용자 권한으로 돌았는지도 알 수 있고, euid 가 0 이면 루트 권한입니다. [2]

실행을 맡은 시스템 프로세스의 기록은 다른 프로그램의 실행을 간접으로 보여 줍니다. 실행과 이어진 조건의 예는 아래와 같습니다.

| 조건 | 용도 | 출처 |
|---|---|---|
| `process == "sudo"` | 관리자 권한으로 실행한 명령줄 활동 | [3] |
| `process == "sshd"` | SSH 접속 성공·실패와 일반 활동 | [3] |
| `process == "logind"` | 사용자 로그인 | [3] |
| `process == "tccd"` | 권한·접근 위반 | [3] |
| `process == "kextd" && sender == "IOKit"` | 커널 확장 | [3] |
| `process == "screensharingd" \|\| process == "ScreensharingAgent"` | 화면 공유 인증 | [3] |
| 프로세스 `syspolicyd`, 서브시스템 `com.apple.syspolicy.exec` | Gatekeeper 실행 정책 평가 | [9] |

sudo 기록에 명령줄이 남는다는 설명이 있지만 [3], 메시지 문구가 어떤지는 실제 데이터로 확인해야 합니다. 영역별 조건과 메시지는 [통합 로그에서 찾을 것](../logs/unified-log-events/index.md) 에 모아 두었습니다.

**증명하지 못하는 것**

프로세스 속성에는 부모 프로세스와 명령줄 인자가 없어서, 누가·무엇이 그 프로그램을 띄웠는지와 어떤 인자로 띄웠는지는 이 기록만으로 말할 수 없습니다. [1] 앱이 실행되거나 프로세스가 만들어질 때 launchd·RunningBoard·LaunchServices·AMFI 같은 시스템 구성 요소가 어떤 문구를 남기는지는 공개 자료가 없어서, 특정 메시지를 "실행 기록" 으로 단정하려면 같은 macOS 버전에서 직접 확인해야 합니다.

기록이 없다고 실행되지 않았다고 볼 수도 없습니다. Debug 수준은 디스크에 남지 않고 Info 수준은 설정한 경우에만 남으며, 나머지 수준도 저장소가 정해진 크기를 넘으면 오래된 것부터 지워집니다. [6] 로그를 거의 남기지 않는 프로그램은 돌았어도 흔적이 적습니다. 첫 기록의 시각 역시 실행 시각이 아니라 "처음 로그를 남긴 시각" 이라서, 실행 시각은 그보다 앞일 수 있습니다.

보고서에는 "이 앱을 실행했다" 가 아니라 "이 시각(UTC)에 PID 몇 번, 실행 파일 경로 무엇인 프로세스가 로그를 남긴 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

tracev3 의 시각은 연속 시각 (continuous time) 이고, 헤더나 timesync 부팅 기록의 Mach timebase 분자·분모로 환산한 다음 부팅 UUID 가 맞는 timesync 기록으로 실제 시각(wall clock)을 구합니다. [2] timesync 기록의 실제 시각 값은 1970년 기준 유닉스 나노초라서 결과는 UTC 이고, 인텔 맥은 Mach 시각을 나노초로, Apple Silicon 은 틱으로 적어서 나노초로 바꿔야 정확한 시각이 나옵니다. [2][7] 재부팅을 넘어 시각을 맞추려면 `timesync` 폴더가 같이 있어야 합니다. `log show` 는 `--timezone` 옵션으로 출력 시간대를 정하니, 보고서에는 어느 시간대로 뽑았는지 함께 적습니다. [5] 변환식과 필드 오프셋은 [통합 로그 형식](../../01-foundations/data-formats/unified-log/index.md) 에서 다룹니다.

## 함정과 한계

`process` 와 `sender` 를 헷갈리면 라이브러리 이름을 앱 이름으로 잘못 적게 됩니다. `sender` 가 `IOKit` 이나 `Security` 처럼 프레임워크 이름으로 나오는 기록은 그 프레임워크를 불러 쓴 `process` 가 주인입니다. [1][3]

tracev3 만 떼어 오고 uuidtext 폴더를 빠뜨리면 실행 파일 경로와 메시지 문구가 풀리지 않습니다. [2][7] 동적 문자열은 기본값으로 `<private>` 로 가려져서 메시지 안의 경로·사용자 이름이 보이지 않을 수 있고, 가림 설정과 수준 설정은 [통합 로그 형식](../../01-foundations/data-formats/unified-log/index.md) 에서 다룹니다. [6]

로그는 지울 수 있습니다. `log` 명령에는 로그 데이터를 지우는 `erase` 하위 명령이 있어서, 활동이 이어져야 할 구간에 기록이 통째로 비어 있으면 삭제를 의심해 볼 만합니다. [5] 다만 용량에 따라 오래된 기록이 밀려나는 것과 구별해야 하니, 비어 있는 구간 앞뒤의 파일 시각과 다른 아티팩트를 같이 봅니다.

공개 필터를 그대로 믿어서도 안 됩니다. Jamf Protect 저장소는 `sudo_access_failed_incorrect_password`, `gatekeeper_file_access_rejections_and_user_bypasses`, `gatekeeper_file_access_scan_activity`, `xprotect_remediator_scan_activity`, `login_through_login_window_with_password_success` 같은 실행·보안 관련 필터를 제품의 Telemetry 기능으로 옮기며 목록에서 뺐습니다. [4] 기록 규모도 3천만~5천만 건에 이를 만큼 커서 [3], 조건 없이 살펴보기보다 프로세스·경로 조건으로 먼저 좁힙니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세의 필드 배치로 만든 카탈로그 프로세스 정보 항목 예시이고, 특정 기기에서 나온 값이 아닙니다. 위 표에서 뺀 필드(오프셋 0 항목 번호, 2·28 은 뜻이 알려지지 않은 필드) 은 `..` 로 두었고, 바이트 순서는 리틀엔디언으로 적었으니 원문 명세와 함께 확인합니다.

```text
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0000    .. .. .. .. 01 00 FF FF 34 12 00 00 00 00 00 00
0010    78 56 00 00 F4 01 00 00 F5 01 00 00 .. .. .. ..
0020    00 00 00 00
```

| 오프셋 | 바이트 | 읽은 값 |
|---|---|---|
| 4 | `01 00` | 주 실행 파일 UUID 는 카탈로그 UUID 배열의 1번 |
| 6 | `FF FF` | dsc UUID 없음 |
| 8 | `34 12 00 00 00 00 00 00` | proc_id 첫째 수 0x1234 |
| 16 | `78 56 00 00` | proc_id 둘째 수 0x5678 |
| 20 | `F4 01 00 00` | pid 500 |
| 24 | `F5 01 00 00` | euid 501 |
| 32 | `00 00 00 00` | UUID 정보 항목 0개 |

Firehose 청크의 오프셋 16·24 에서 같은 0x1234·0x5678 을 찾으면 그 청크의 메시지가 이 프로세스의 것이고, 카탈로그 UUID 배열 1번의 UUID 로 uuidtext 파일을 열어 꼬리의 경로 문자열을 읽으면 실행 파일 경로가 나옵니다. [2]

### 공개 도구로 한 번

맥에서는 수집한 아카이브에 조건을 걸어 봅니다. [5]

```sh
log show --archive system_logs.logarchive \
  --predicate 'process == "sudo"' --style ndjson --timezone UTC

log show --archive system_logs.logarchive \
  --predicate 'processImagePath BEGINSWITH "/Users/"' --style ndjson --timezone UTC
```

두 번째 조건은 사용자 폴더 안에서 돈 실행 파일이 남긴 기록을 모읍니다. 맥이 아닌 곳에서는 Mandiant `macos-unifiedlogs` 의 `unifiedlog_parser` 로 아카이브를 CSV·JSON 으로 풀고 프로세스 이름·경로 필드로 거릅니다. [7] 프로그램에서 읽을 때는 macOS 10.15 이후 `OSLogStore` 로 아카이브를 열고 기록마다 `process`·`processIdentifier`·`sender` 를 꺼냅니다. [1][8]

## 교차 검증

| 함께 볼 아티팩트 | 채워 주는 것 |
|---|---|
| [KnowledgeC](knowledgec/index.md) | 앱이 화면 앞에 있던 구간 |
| [바이옴](biome/index.md) | 최근 macOS 의 앱 사용 기록 |
| [실행 정책 평가 기록](execpolicy-gatekeeper.md) | 처음 실행할 때 받은 검사 |
| [격리 속성과 다운로드 기록](../filesystem/quarantine/index.md) | 실행 파일이 어디서 왔는지 |
| [터미널 명령 기록](shell-history.md) | 명령줄과 인자 |
| [감사 로그](../logs/openbsm-audit.md) | 통합 로그에 없는 실행 감사 기록 |
| [충돌·진단 보고서](diagnostic-reports.md) | 죽은 프로세스의 경로와 시각 |
| [실행 에이전트·데몬](../persistence/launchd/index.md) | 자동으로 뜨는 프로그램의 등록 |

통합 로그의 시각은 다른 아티팩트와 한 줄로 늘어놓을 때 가장 쓸모가 커서, [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 과 [어떤 앱을 언제 썼나](../../04-scenarios/activity/app-usage.md) 로 이어집니다.

## 실습

NIST CFReDS 같은 공개 시험 자료 가운데 `/private/var/db/diagnostics/` 와 `/private/var/db/uuidtext/` 가 들어 있거나 `.logarchive` 가 딸린 것을 골라 아래 질문을 풀어 봅니다.

1. 사용자 폴더 아래 경로에서 실행된 프로세스가 남긴 기록이 있나요? 있다면 가장 이른 기록과 가장 늦은 기록의 UTC 시각은 언제인가요?
2. 그 프로세스의 euid 는 무엇이고, 어느 계정에 해당하나요?
3. 같은 기록에서 `process` 와 `sender` 가 다른 경우를 찾고, 어느 쪽이 앱이고 어느 쪽이 라이브러리인지 설명해 보세요.
4. `process == "sudo"` 기록과 터미널 명령 기록을 나란히 놓으면 시각이 맞나요?
5. uuidtext 폴더를 빼고 tracev3 만 파서에 넣으면 출력의 어느 필드가 비나요?

## 참고 문헌

1. Apple Developer — OSLogEntryFromProcess — https://developer.apple.com/tutorials/data/documentation/oslog/oslogentryfromprocess.json
2. libyal dtformats — Apple Unified Logging and Activity Tracing formats — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
3. CrowdStrike — How to Leverage Apple Unified Log for Incident Response (2020-08-25) — https://www.crowdstrike.com/blog/how-to-leverage-apple-unified-log-for-incident-response/
4. jamf/jamfprotect — unified_log_filters — https://github.com/jamf/jamfprotect/tree/main/unified_log_filters
5. SS64 — macOS `log` 명령 — https://ss64.com/mac/log.html
6. Apple Developer — Generating Log Messages from Your Code — https://developer.apple.com/tutorials/data/documentation/os/generating-log-messages-from-your-code.json
7. Alexander Holcomb (Mandiant) — Reviewing macOS Unified Logs (2022-08-31) — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
8. Apple Developer — OSLogStore — https://developer.apple.com/tutorials/data/documentation/oslog/oslogstore.json
9. Mac logging and the log command: A guide for Apple admins — https://www.iru.com/blog/mac-logging-and-the-log-command-a-guide-for-apple-admins
