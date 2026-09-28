---
title: "원격 로그인"
parent: "통합 로그에서 찾을 것"
grand_parent: "아티팩트 · 로그"
nav_order: 1750
---

# 원격 로그인 (Remote Login)

SSH 로 들어온 접속은 `sshd` 프로세스의 메시지로, 화면 공유 인증은 `screensharingd`·`ScreensharingAgent` 프로세스의 메시지로 찾고, 통합 로그에는 두 경로 모두 성공과 실패가 함께 남습니다 [1].

## 무엇을 기록하나 · 왜 생기나

맥에 원격으로 들어오는 대표 경로는 SSH(원격 로그인)와 화면 공유이고, 접속을 받는 쪽 프로세스가 자기 동작을 통합 로그에 남깁니다. `process == "sshd"` 조건은 SSH 접속의 성공·실패와 그 밖의 SSH 활동을 잡고, `screensharingd`·`ScreensharingAgent` 프로세스 조건은 화면 공유를 거친 인증의 성공·실패를 잡습니다 [1]. SSH 로그온은 `sshd` 프로세스 경로로도 거를 수 있습니다 [2].

침입 조사에서 이 기록은 외부에서 맥에 들어온 시각과 시도 횟수를 추정하는 출발점입니다. 원격 접속 설정과 다른 원격 도구는 [원격 접속 (Remote Access)](../../network/remote-access/index.md)에서, 통합 로그의 저장 위치와 보관 방식은 [통합 로그에서 찾을 것 (Unified Log Events)](index.md)에서 다룹니다.

## 위치와 버전별 차이

기록은 다른 통합 로그 메시지와 같은 저장소에 섞여 있습니다. 아래 조건과 `sshd` 메시지 문구는 버전에 따라 다를 수 있으니, 분석 대상의 버전에서 조건이 실제로 걸리는지 먼저 확인하고 씁니다.

## 구조 — 찾는 조건

| 보려는 것 | 조건 | 출처 |
|---|---|---|
| SSH 활동(성공·실패 포함) | `process == "sshd"` | [1] |
| 화면 공유 인증 성공·실패 | `process == "screensharingd" \|\| process == "ScreensharingAgent"` | [1] |

CrowdStrike 원문 예시는 화면 공유 조건의 따옴표가 어긋나 있으니 위 조건을 쓰고, 실제 맥에서 한 번 돌려 확인한 뒤 씁니다. 연산자 설명은 [자주 쓰는 검색 조건 (Predicates)](predicates.md)에 있습니다.

Mandiant 글은 `sshd` 를 프로세스 경로 `/usr/bin/sshd` 로 거른다고 적었지만 [2], macOS 에 기본으로 들어 있는 `sshd` 는 `/usr/sbin/sshd` 에 있습니다. 경로 조건보다 프로세스 이름 조건(`process == "sshd"`)을 먼저 쓰고, 경로를 쓰려면 분석 대상 기기의 `sshd` 경로부터 확인합니다.

아래 항목은 실제 데이터로 확인해야 합니다.

| 실제 데이터로 확인할 것 | 비고 |
|---|---|
| `sshd` 성공·실패 메시지 문구 | 인증 방식과 사용자·원격 주소가 어떻게 들어가는지 실제 메시지로 확인 |
| 원격 주소가 가려지는지 | 개인정보 가림 규칙상 동적 문자열은 기본값으로 가려짐([허브](index.md)) |
| Apple Remote Desktop·원격 관리 기록 | 기록을 남기는 프로세스·서브시스템부터 확인 |
| 원격 로그인(SSH)을 켠 설정의 기록 위치 | 시험 기기에서 설정을 켜 보고 어디에 기록이 남는지 확인 |

## 증거로서 의미

**증명하는 것.** `sshd` 조건에 걸리는 메시지가 있으면 그 시각에 SSH 접속과 관련된 활동이 있었다는 기록이 있다는 뜻이고 [1], 화면 공유 프로세스의 메시지는 그 시각에 화면 공유 인증을 거친 흔적입니다 [1]. 짧은 간격으로 실패가 이어지면 반복된 인증 시도를 가리킵니다.

**증명하지 못하는 것.** 실제 로그로 문구를 확인하기 전에는 메시지 하나만 보고 인증이 성공했는지 단정하지 않습니다. 사용자 이름은 `<private>` 로 가려질 수 있고 [3] 원격 주소도 가려질 수 있어서, 어느 계정으로, 어디서 들어왔는지 메시지만으로 정하지 못합니다. 기록이 없어도 원격 접속이 없었다고 단정하지 않습니다. 통합 로그는 크기 한도를 넘으면 오래된 메시지부터 지우고, 조사 기간이 보관 범위를 벗어날 수 있습니다([허브](index.md)).

보고서에는 "이 시각 사이에 `sshd` 가 남긴 메시지가 이만큼 있고, 그중 실패로 읽히는 메시지가 이만큼이다" 처럼 프로세스와 개수를 밝혀 씁니다.

## 시각 해석

원격 접속 시각은 네트워크 장비나 상대 서버의 기록과 맞춰 볼 때가 많아서, 양쪽을 UTC 로 맞춘 뒤 비교합니다. 통합 로그 시각의 계산 방법은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있고, `log show` 는 `--timezone` 옵션으로 출력 시간대를 정할 수 있습니다 [4].

## 함정과 한계

- **공개 필터 목록의 변화.** Jamf 는 "화면 공유 연결" 필터를 자체 기능으로 옮기면서 공개 목록에서 뺐습니다 [3]. 공개 필터 목록에 없다고 해서 그 기록이 통합 로그에 없다는 뜻은 아닙니다.
- **경로 조건.** `/usr/bin/sshd` 경로 조건을 그대로 쓰면 결과가 비어 나올 수 있습니다. 결과가 없으면 조건부터 의심합니다.
- **로컬 로그인과 구분.** 로그인 창에서 한 로그인은 [로그인·로그아웃 (Login·Logout)](login-logout.md)에서 다룹니다.
- **원격 세션 안의 권한 사용.** SSH 로 들어온 뒤 `sudo` 를 쓴 기록은 [관리자 권한 사용 (sudo·Authorization)](sudo-authorization.md)에서 이어 봅니다.

## 직접 분석해 보기

헥스로 따라가는 방법은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있고, 여기서는 도구로 조건을 걸어 봅니다.

1. 분석 대상의 `.logarchive` 를 준비합니다.
2. `sshd` 조건으로 메시지를 뽑습니다 [4]. 따옴표는 실제 맥에서 한 번 돌려 확인합니다.

```
log show --archive <경로> --predicate 'process == "sshd"' --style ndjson
```

3. 결과 메시지를 읽고, 성공·실패를 뜻하는 문구와 사용자·원격 주소가 보이는지 가려졌는지 사건 기록에 적습니다.
4. 화면 공유 조건도 같은 방식으로 돌리고, 공개 파서 Mandiant `unifiedlog_parser` 로 푼 CSV 와 결과 수를 비교합니다 [2].

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [원격 접속 (Remote Access)](../../network/remote-access/index.md) | 원격 로그인·화면 공유 설정 상태 |
| [SSH 키와 접속 목록 (SSH Keys·known_hosts)](../../credentials/ssh-keys.md) | 공개 키 등록과 접속 기록의 앞뒤 |
| [방화벽 (Application Firewall)](../../network/application-firewall.md) | 들어오는 연결 허용 설정 |
| [터미널 명령 기록 (zsh_history·bash_sessions)](../../execution/shell-history.md) | 접속 뒤 실행한 명령 |

침입 조사 전체 흐름은 [원격 접속 침입 확인 (Remote Intrusion)](../../../04-scenarios/incident/remote-intrusion.md)에 있습니다.

## 실습

공개 시험 데이터(NIST CFReDS 등)에 `.logarchive` 나 통합 로그 폴더가 들어 있으면 풀어 봅니다.

1. `sshd` 조건에 걸린 메시지가 있는지, 있다면 가장 이른 것과 가장 늦은 것의 시각을 적어 보세요.
2. 메시지에서 원격 주소가 보이는지, 가려졌는지 확인해 보세요.
3. 화면 공유 조건의 결과가 있다면 SSH 기록과 시각이 겹치는지 맞춰 보세요.

## 참고 문헌

1. CrowdStrike, How to Leverage Apple Unified Log for Incident Response — https://www.crowdstrike.com/blog/how-to-leverage-apple-unified-log-for-incident-response/
2. Mandiant(Google Cloud), Reviewing macOS Unified Logs — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
3. jamf/jamfprotect, unified_log_filters — https://github.com/jamf/jamfprotect/tree/main/unified_log_filters
4. log(1) man page — https://keith.github.io/xcode-man-pages/log.1.html
