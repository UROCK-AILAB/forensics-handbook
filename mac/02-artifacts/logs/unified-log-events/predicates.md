---
title: "자주 쓰는 검색 조건"
parent: "통합 로그에서 찾을 것"
grand_parent: "아티팩트 · 로그"
nav_order: 1760
---

# 자주 쓰는 검색 조건 (Predicates)

`log show` 는 `--predicate` 에 검색 조건 (predicate) 을 받아 프로세스·서브시스템·메시지 문구로 통합 로그를 거르고, 이 페이지는 조건에 쓰는 키와 연산자, 아카이브에 조건을 걸 때의 주의점, 주제별 조건이 있는 곳을 모아 둔 길잡이입니다 [1].

## 무엇을 하나 · 왜 필요한가

통합 로그는 하루에도 메시지가 아주 많이 쌓이고, 원하는 사건만 보려면 어느 프로세스가 어느 서브시스템으로 남긴 메시지인지를 조건으로 걸어야 합니다. `log` 도구의 man 페이지는 `--predicate` 로 조건을 주는 방법을 설명하고, 서브시스템 하나만 보거나 서브시스템과 카테고리를 함께 거는 예를 싣고 있습니다 [1].

```
log show --predicate 'subsystem == "com.example.my_subsystem"'
log show --predicate '(subsystem == "com.example.my_subsystem") && (category == "desired_category")'
```

통합 로그의 저장 위치와 보관 방식은 [통합 로그에서 찾을 것 (Unified Log Events)](index.md)에, 파일 형식은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있습니다.

## 구조 — 조건에 쓰는 키

man 페이지가 조건에 쓸 수 있다고 밝힌 키는 `eventType`, `eventMessage`, `messageType`, `process`, `processImagePath`, `sender`, `senderImagePath`, `subsystem`, `category` 입니다 [1]. 이 가운데 `eventType` 과 `messageType` 은 정해진 값 가운데 하나를 받습니다 [1].

| 키 | 값 |
|---|---|
| `eventType` | `activityCreateEvent`, `activityTransitionEvent`, `logEvent`, `signpostEvent`, `stateEvent`, `timesyncEvent`, `traceEvent`, `userActionEvent` |
| `messageType` | `default`, `info`, `debug`, `error`, `fault` |

## 연산자

man 페이지의 조건 절에는 `==`, `!=`, `ENDSWITH`, `contains[cd]`, `IN { }`, `&&`, `||` 가 나옵니다 [1]. 탐지 규칙을 공개한 자료들은 이 밖에 `AND`, `CONTAINS`(포함), `CONTAINS[c]`(대소문자를 가리지 않는 포함), `BEGINSWITH`(시작 문자열)도 씁니다 [2][3]. 예를 들어 잠금 해제 실패 조건은 세 조건을 `AND` 로 잇고, 경로는 `BEGINSWITH` 로, 메시지는 `CONTAINS[c]` 로 거릅니다 [2].

```
processImagePath BEGINSWITH "/System/Library/CoreServices" AND process == "loginwindow" AND eventMessage CONTAINS[c] "INCORRECT"
```

man 페이지에는 "SHORTHAND-BASED FILTERING" 절도 있어서, `--predicate` 에 `p`(process)·`s`(subsystem)·`c`(category) 같은 줄인 키와 `:`(포함), `:^`(시작), `endswith`, `~/regex/` 같은 줄임 연산자를 쓸 수 있다고 적었습니다 [1]. 다만 이 줄임 문법이 macOS 몇 버전부터 되는지는 확인하지 못했습니다. 보고서나 절차서에 남길 조건은 `==`, `CONTAINS` 같은 위의 연산자로 씁니다.

## 아카이브에 조건 걸기

사후 분석에서는 검체에서 수집한 `.logarchive` 를 `--archive` 로 주고 조건을 함께 겁니다. 기간은 `--start`·`--end` 로 정하거나 `--last` 로 최근 구간만 볼 수 있고, `--last` 에는 `boot` 도 줄 수 있습니다 [1].

```
log show --archive <경로> --start "<시작 시각>" --end "<끝 시각>" --predicate 'process == "sshd"'
```

시각 문자열의 정확한 형식은 man 페이지로 확인하고 씁니다. 출력은 `--style` 로 `default`, `compact`, `json`, `ndjson`, `syslog` 중에서 고를 수 있고 [1], JSON 계열로 뽑으면 다른 도구에 넘기기 쉽습니다. `--timezone` 으로 출력 시간대를 정할 수 있으니 [1] 보고서에는 어느 시간대로 뽑았는지 함께 적습니다.

`--info` 와 `--debug` 를 줘야 해당 수준의 메시지가 출력에 나옵니다 [1]. 다만 Apple 은 Debug 수준 메시지를 디스크에 남기지 않는다고 설명해서 [4], 사후 분석에서는 이 옵션을 줘도 그 메시지가 나오지 않습니다. 로그 수준별로 디스크에 남는 범위는 [허브](index.md)에 정리돼 있습니다.

자주 쓰는 조건은 `~/.logrc` 의 `predicate:` 절에 별칭으로 적어 둘 수 있고, 같은 파일에 기본 인자도 정할 수 있습니다 [1]. 분석용 맥에 별칭을 두면 편하지만, 절차서에는 별칭 대신 조건 전문을 적어 다른 분석가가 그대로 따라 할 수 있게 합니다.

## 주제별 조건

조건과 해석은 주제 페이지에 있고, 여기서는 어디에 있는지만 모읍니다.

| 주제 | 무엇을 거르나 | 페이지 |
|---|---|---|
| 로그인·세션·로그인 키체인·로그인 항목 실행 | `loginwindow`, `logind`, `securityd` 등 | [로그인·로그아웃 (Login·Logout)](login-logout.md) |
| 잠금 해제 실패·Apple Watch 잠금 해제 | `loginwindow`, `com.apple.sharing` | [잠금·잠금 해제·잠자기 (Lock·Sleep)](lock-sleep.md) |
| sudo·TCC·계정 데이터베이스 | `sudo`, `tccd`, `opendirectoryd` | [관리자 권한 사용 (sudo·Authorization)](sudo-authorization.md) |
| SSH·화면 공유 | `sshd`, `screensharingd` | [원격 로그인 (Remote Login)](remote-login.md) |
| 프로세스 실행 | — | [통합 로그의 프로세스 실행 기록 (Process Events)](../../execution/unified-log-process.md) |

이 허브에 주제 페이지가 없는 조건 가운데 공개 자료에 나온 것은 아래와 같습니다. 해석은 오른쪽 페이지에서 다룹니다.

| 목적 | 조건 | 출처 | 함께 볼 페이지 |
|---|---|---|---|
| 커널 확장(macOS 10.15 까지) | `process == "kextd" && sender == "IOKit"` | [3] | [커널·시스템 확장 (KEXT·System Extension)](../../persistence/kext-system-extension.md) |
| Gatekeeper | 프로세스 `syspolicyd`, 서브시스템 `com.apple.syspolicy.exec` | [5] | [실행 정책 평가 기록 (ExecPolicy·Gatekeeper)](../../execution/execpolicy-gatekeeper.md) |
| XProtect | 서브시스템 `com.apple.xprotect` | [5] | [보안 도구 기록 (XProtect)](../xprotect.md) |
| AirDrop | 서브시스템 `com.apple.sharing`, 카테고리 `AirDrop` | [5] | [에어드롭 (AirDrop)](../../external-devices/airdrop.md) |
| MDM | 프로세스 `mdmclient`, 서브시스템 `com.apple.ManagedClient` | [5] | [구성 프로파일 (Configuration Profiles·MDM)](../../persistence/configuration-profiles.md) |

`kextd` 는 macOS 11 Big Sur 에서 `kernelmanagerd` 로 바뀌어서, 11 이후 검체에서는 커널 확장 조건이 비어 나올 수 있습니다. 프로세스와 서브시스템만 적힌 항목은 `process == "syspolicyd"` 처럼 키 하나씩 조건으로 바꿔 쓰고, 둘을 `&&` 로 이을지는 검체에서 결과를 보며 정합니다.

## 함정과 한계

- **따옴표.** 조건 전체는 셸의 작은따옴표로, 조건 안의 문자열은 큰따옴표로 감쌉니다. 공개 자료의 예시 중에는 따옴표가 어긋난 것도 있어서 [3], 옮겨 쓴 조건은 실제 맥에서 한 번 돌려 확인합니다.
- **버전.** 공개 자료의 조건은 대부분 적용 버전을 밝히지 않습니다. 검체의 macOS 버전에서 결과가 비면 조건부터 의심합니다.
- **가려진 값.** 동적 문자열은 기본값으로 `<private>` 로 가려지고([허브](index.md)), `eventMessage CONTAINS` 로 가려진 부분의 문자열을 찾으면 걸리지 않을 수 있습니다.
- **권한.** `sudo` 없이 `log show` 를 돌릴 때 보이는 범위가 달라지는지는 확인하지 못했습니다. 라이브 시스템에서 돌릴 때는 권한을 기록에 남깁니다.
- **메시지 확인.** 공개 자료의 조건은 대부분 프로세스·서브시스템 수준에서 거르는 데 그쳐서, 걸린 메시지를 읽어 뜻을 확인하는 단계를 건너뛰지 않습니다.

## 직접 분석해 보기

1. 검체의 `.logarchive` 에 조건 없이 `--last` 로 짧은 구간만 뽑아, 출력에 어떤 키가 보이는지 확인합니다 [1].
2. `--style ndjson` 으로 같은 구간을 뽑아 `process`, `subsystem`, `category` 값이 어떻게 들어 있는지 봅니다 [1].
3. 주제 페이지의 조건을 하나 골라 걸고, 결과 수를 적어 둡니다.
4. 공개 파서 Mandiant `unifiedlog_parser` 로 같은 아카이브를 CSV 로 풀고 [6], 같은 프로세스 이름으로 걸렀을 때 결과 수가 `log show` 와 같은지 비교합니다. 도구 검증 방법은 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)에 있습니다.

## 실습

공개 검체(NIST CFReDS 등)에 `.logarchive` 나 통합 로그 폴더가 들어 있으면 풀어 봅니다.

1. `messageType == "error"` 조건으로 뽑은 메시지를 프로세스별로 세어, 가장 많은 프로세스 셋을 적어 보세요.
2. `--info` 를 줄 때와 주지 않을 때 결과 수가 달라지는지 비교해 보세요.
3. 주제별 표의 조건 중 하나를 `--timezone` 을 바꿔 가며 뽑고, 시각 표시가 어떻게 달라지는지 확인해 보세요.

## 참고 문헌

1. log(1) man page — https://keith.github.io/xcode-man-pages/log.1.html
2. jamf/jamfprotect, lock_screen_unlock_failure.yaml — https://raw.githubusercontent.com/jamf/jamfprotect/main/unified_log_filters/lock_screen_unlock_failure.yaml
3. CrowdStrike, How to Leverage Apple Unified Log for Incident Response — https://www.crowdstrike.com/blog/how-to-leverage-apple-unified-log-for-incident-response/
4. Apple Developer, Generating Log Messages from Your Code — https://developer.apple.com/tutorials/data/documentation/os/generating-log-messages-from-your-code.json
5. Mac logging and the log command: A guide for Apple admins — https://www.iru.com/blog/mac-logging-and-the-log-command-a-guide-for-apple-admins
6. Mandiant(Google Cloud), Reviewing macOS Unified Logs — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
