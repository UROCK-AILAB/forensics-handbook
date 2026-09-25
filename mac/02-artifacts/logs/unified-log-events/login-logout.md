---
title: "로그인·로그아웃"
parent: "통합 로그에서 찾을 것"
grand_parent: "아티팩트 · 로그"
nav_order: 1720
---

# 로그인·로그아웃 (Login·Logout)

통합 로그에서 로그인은 로그인 과정에 관여하는 `loginwindow`·`logind`·`securityd` 가 남긴 메시지를 골라 찾고, 이 메시지로 로그인과 세션 시작·종료 시점을 추정합니다 [1][2][3].

## 무엇을 기록하나 · 왜 생기나

로그인에는 여러 프로세스가 관여하고, 각 프로세스는 자기 동작을 통합 로그에 남깁니다. 로그인 쪽에서 볼 대상은 네 갈래입니다. 사용자 로그인은 프로세스 `loginwindow` 와 서브시스템 `com.apple.login` 으로 거릅니다 [3]. `logind` 프로세스 메시지로는 사용자 로그인 이벤트를, `securityd` 의 `Session ` 메시지로는 세션 생성과 종료를 잡습니다 [1]. `loginwindow` 가 `Security` 를 거쳐 남긴 메시지는 로그인 키체인이 풀린 기록입니다 [1].

로그인 직후 무엇이 자동으로 실행됐는지도 여기서 볼 수 있습니다. 서브시스템 `com.apple.loginwindow.logging` 의 `performAutolaunch` 메시지는 로그인 항목을 실행한 기록입니다 [2]. 로그인 항목 자체를 어디에 등록하는지는 [로그인 항목 (Login Items)](../../persistence/login-items.md)에서 다룹니다.

통합 로그가 어디에 어떤 형식으로 저장되고 얼마나 오래 남는지는 [통합 로그에서 찾을 것 (Unified Log Events)](index.md)과 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있습니다.

## 위치와 버전별 차이

기록은 다른 통합 로그 메시지와 같은 저장소에 섞여 있고, 로그인만 모아 둔 파일은 따로 없습니다. `logind` 가 macOS 몇 버전부터 있는지, 버전마다 로그인 메시지 문구가 어떻게 달라지는지는 공개 자료가 없습니다. 아래 조건은 적용 버전이 알려져 있지 않아서, 검체의 macOS 버전에서 실제로 걸리는지 먼저 확인하고 씁니다. 버전은 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../../system-account/os-version-install-history.md)에서 확인합니다.

## 구조 — 찾는 조건

| 보려는 것 | 조건 | 출처 |
|---|---|---|
| 사용자 로그인 | 프로세스 `loginwindow`, 서브시스템 `com.apple.login` | [3] |
| 사용자 로그인 이벤트 | `process == "logind"` | [1] |
| 세션 생성·종료 | `process == "securityd" && eventMessage CONTAINS "Session " && subsystem == "com.apple.securityd"` | [1] |
| 로그인 키체인 잠금 해제 | `process == "loginwindow" && sender == "Security"` | [1] |
| 로그인 항목 실행 | 서브시스템 `com.apple.loginwindow.logging`, 메시지에 `performAutolaunch` | [2] |

로그인 항목 실행의 서브시스템과 메시지 문구 두 조건을 한 줄로 합치면 아래처럼 쓸 수 있습니다. `CONTAINS` 같은 연산자는 [자주 쓰는 검색 조건 (Predicates)](predicates.md)에서 설명합니다.

```
subsystem == "com.apple.loginwindow.logging" && eventMessage CONTAINS "performAutolaunch"
```

메시지는 아래와 같은 모양이고, 실행한 앱의 경로와 `shouldHide` 값이 한 줄에 들어 있습니다 [2].

```
LaunchItemsInSharedFileListRef | performAutolaunch, launching: /Applications/LuLu.app, shouldHide: 0
```

`loginwindow` 가 로그아웃을 시작하거나 마칠 때 남기는 메시지의 정확한 문구는 공개 자료가 없습니다. 로그아웃 시점은 세션 종료 조건으로 먼저 좁히고, 검체에서 실제 문구를 확인한 뒤 보고서에 옮깁니다.

## 증거로서 의미

**증명하는 것.** 위 조건에 걸리는 메시지가 있으면 그 시각에 해당 프로세스가 로그인·세션·키체인 잠금 해제와 관련된 동작을 기록했다는 뜻입니다 [1]. `performAutolaunch` 메시지는 그 시각에 어떤 앱을 로그인 항목으로 실행했는지 알려 주고 [2], 지속성 조사에서 로그인 직후 뜬 프로그램을 확인할 때 쓸모가 있습니다.

**증명하지 못하는 것.** 기록은 계정이 로그인했다는 사실까지만 말하고, 누가 키보드 앞에 있었는지는 말하지 않습니다. 사용자 이름 같은 문자열은 기본값으로 가려져서 출력에 `<private>` 로 나올 수 있고 [3][4], 이때는 메시지만으로 어느 계정인지 정하지 못합니다. 조건에 걸리는 기록이 없다고 해서 로그인이 없었다고 단정하지도 않습니다. 통합 로그는 저장 한도를 넘으면 오래된 메시지부터 지우고, Info·Debug 수준 메시지는 디스크에 남지 않을 수 있습니다(자세한 내용은 [허브](index.md)).

보고서에는 "이 시각에 `logind` 가 로그인 관련 메시지를 남겼고, 같은 분에 `loginwindow` 가 로그인 키체인을 푼 기록이 있다" 처럼 프로세스와 메시지를 밝혀 씁니다.

## 시각 해석

`log show` 가 보여 주는 시각은 통합 로그의 시각 값을 벽시계 시각으로 바꾼 결과이고, 그 계산 방법은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있습니다. 출력 시간대는 `--timezone` 옵션으로 정할 수 있으니 [5], 보고서에는 어느 시간대로 출력했는지 함께 적습니다. 검체의 시간대 설정은 [시간대와 시계 설정 (Time Zone·NTP)](../../system-account/time-zone.md)에서 확인합니다.

## 함정과 한계

- **메시지 문구는 검체에서.** 이 페이지의 조건은 프로세스·서브시스템 수준이고, 로그인·로그아웃을 뜻하는 메시지 문구는 공개 자료가 없습니다. 조건에 걸린 메시지를 하나씩 읽고 뜻을 확인합니다.
- **잠금 해제와 로그인 구분.** 화면 잠금을 푸는 동작도 `loginwindow` 쪽 기록을 남깁니다. 잠금 해제는 [잠금·잠금 해제·잠자기 (Lock·Sleep)](lock-sleep.md)에서 따로 다룹니다.
- **원격 로그인은 별도.** SSH·화면 공유로 들어온 접속은 다른 프로세스가 기록하고, [원격 로그인 (Remote Login)](remote-login.md)에서 다룹니다.
## 직접 분석해 보기

통합 로그 파일을 헥스로 따라가는 방법은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에서 다루고, 여기서는 도구로 조건을 걸어 봅니다.

1. 검체에서 수집한 `.logarchive` 를 준비합니다. 수집 방법은 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)에 있습니다.
2. `log show` 에 아카이브와 조건을 함께 줍니다 [5]. 명령의 따옴표는 실제 맥에서 한 번 돌려 확인합니다.

```
log show --archive <경로> --predicate 'process == "logind"' --style ndjson
```

3. 세션 생성·종료와 키체인 잠금 해제 조건도 같은 방식으로 돌리고, 세 결과를 시각순으로 합쳐 봅니다.
4. 공개 파서 Mandiant `unifiedlog_parser` 로 같은 아카이브를 CSV 로 풀어 [2], `log show` 결과와 메시지 수·시각이 같은지 비교합니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [로그인 창 설정 (loginwindow)](../../system-account/loginwindow.md) | 로그인 창 설정 값과 로그인 기록이 어긋나지 않는지 |
| [사용자 계정 (Local Accounts)](../../system-account/user-accounts/index.md) | 가려진 사용자 이름을 계정 목록과 대조 |
| [로그인 항목 (Login Items)](../../persistence/login-items.md) | `performAutolaunch` 로 실행한 앱이 등록된 위치 |
| [KnowledgeC (knowledgeC.db)](../../execution/knowledgec/index.md) | 로그인 직후 앱 사용 기록이 이어지는지 |

사용 시간 전체를 재구성하는 흐름은 [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](../../../04-scenarios/activity/usage-time.md)과 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)에 있습니다.

## 실습

공개 검체(NIST CFReDS 등)에 `.logarchive` 나 통합 로그 폴더가 들어 있으면 풀어 봅니다.

1. `logind` 조건으로 나온 메시지 중 가장 이른 것과 가장 늦은 것의 시각을 적어 보세요.
2. 세션 생성·종료 조건의 결과에서 세션이 시작되고 끝난 쌍을 찾아 보세요.
3. `performAutolaunch` 메시지가 있다면 실행된 앱이 로그인 항목 목록에도 있는지 확인해 보세요.

## 참고 문헌

1. CrowdStrike, How to Leverage Apple Unified Log for Incident Response — https://www.crowdstrike.com/blog/how-to-leverage-apple-unified-log-for-incident-response/
2. Mandiant(Google Cloud), Reviewing macOS Unified Logs — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
3. Mac logging and the log command: A guide for Apple admins — https://www.iru.com/blog/mac-logging-and-the-log-command-a-guide-for-apple-admins
4. jamf/jamfprotect, unified_log_filters — https://github.com/jamf/jamfprotect/tree/main/unified_log_filters
5. log(1) man page — https://keith.github.io/xcode-man-pages/log.1.html
