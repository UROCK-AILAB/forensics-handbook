---
title: "관리자 권한 사용"
parent: "통합 로그에서 찾을 것"
grand_parent: "아티팩트 · 로그"
nav_order: 1740
---

# 관리자 권한 사용 (sudo·Authorization)

`sudo` 로 실행한 명령은 통합 로그에 남아서 `process == "sudo"` 나 프로세스 경로 `/usr/bin/sudo` 로 찾을 수 있고, 개인 정보 보호 권한 위반은 `tccd`, 계정 데이터베이스 쪽 동작은 `opendirectoryd` 기록에서 찾습니다 [1][2][3].

## 무엇을 기록하나 · 왜 생기나

터미널에서 `sudo` 로 명령을 실행하면 `sudo` 가 그 사실을 통합 로그에 남깁니다. Mandiant 는 sudo 로 실행한 명령이 통합 로그에 기록된다고 설명하면서, 프로세스 경로 `/usr/bin/sudo` 로 거르고 메시지에 `root` 가 든 것만 보면 범위를 더 좁힐 수 있다고 적었습니다 [2]. CrowdStrike 도 `process == "sudo"` 를 "높은 권한으로 실행한 명령줄 활동을 잡는" 조건으로 소개합니다 [1].

관리자 권한과 가까운 기록은 두 갈래가 더 있습니다. CrowdStrike 는 `process == "tccd"` 를 "권한·접근 위반을 뜻하는 이벤트를 잡는" 조건으로 꼽았고 [1], 관리자용 안내서는 계정 데이터베이스(Open Directory) 동작을 볼 때 프로세스 `opendirectoryd` 와 서브시스템 `com.apple.opendirectoryd`, `com.apple.AccountPolicy` 를 걸라고 적었습니다 [3]. Jamf 는 루트 계정을 켜거나 루트 암호를 바꾼 기록을 잡는 필터(`root_user_enabled_or_password_changed.yaml`)를 공개했지만 [4], 이번에 필터 내용은 열어 보지 않았습니다.

이 핸드북은 사고 대응과 탐지를 위한 자료라서 권한을 얻는 방법은 다루지 않고, 권한을 쓴 뒤 남는 기록과 그 해석만 다룹니다. 통합 로그의 저장 위치와 보관 방식은 [통합 로그에서 찾을 것 (Unified Log Events)](index.md)에 있습니다.

## 위치와 버전별 차이

기록은 다른 통합 로그 메시지와 같은 저장소에 섞여 있습니다. 출처들은 조건이 어느 macOS 버전에 맞는지 밝히지 않았고, 버전에 따라 메시지가 달라지는지도 확인하지 못했습니다. 검체의 버전에서 조건이 실제로 걸리는지 먼저 확인합니다.

## 구조 — 찾는 조건

| 보려는 것 | 조건 | 출처 |
|---|---|---|
| sudo 로 실행한 명령 | `process == "sudo"` | [1] |
| sudo 로 실행한 명령(경로로 거르기) | 프로세스 경로 `/usr/bin/sudo`, 메시지에 `root` | [2] |
| 개인 정보 보호 권한(TCC) 위반 | `process == "tccd"` | [1] |
| 계정 데이터베이스 동작 | 프로세스 `opendirectoryd`, 서브시스템 `com.apple.opendirectoryd`, `com.apple.AccountPolicy` | [3] |

경로 조건을 한 줄로 쓰면 아래와 같고, 연산자 설명은 [자주 쓰는 검색 조건 (Predicates)](predicates.md)에 있습니다.

```
processImagePath == "/usr/bin/sudo" && eventMessage CONTAINS "root"
```

sudo 메시지에 실행 위치·대상 사용자·명령이 어떤 형식으로 들어가는지, 암호를 틀렸을 때 어떤 문구가 남는지는 이번 자료로 확인하지 못했습니다. 권한 확인 대화상자(Authorization Services)를 처리하는 쪽의 프로세스·서브시스템과 메시지 문구도 확인하지 못했고, Mandiant 글도 이 부분은 다루지 않았습니다 [2]. 이 두 가지는 검체에서 메시지를 직접 읽고 형식을 확인한 뒤 씁니다.

## 증거로서 의미

**증명하는 것.** `sudo` 메시지가 있으면 그 시각에 누군가 `sudo` 를 거쳐 명령을 실행하려 했다는 기록이 있다는 뜻이고 [1][2], 메시지에 명령이 보이면 어떤 명령이었는지도 알 수 있습니다. `tccd` 기록은 어떤 프로세스가 개인 정보 보호 권한이 필요한 자원에 접근하려 한 흔적을 찾는 출발점입니다 [1].

**증명하지 못하는 것.** 메시지 형식을 확인하지 못해서, 메시지 하나만 보고 명령이 성공했는지 실패했는지 단정하지 않습니다. 사용자 이름 같은 문자열은 `<private>` 로 가려질 수 있고 [3], 그러면 어느 계정이 `sudo` 를 썼는지 메시지만으로 정하지 못합니다. 조건에 걸리는 기록이 없어도 권한 사용이 없었다고 단정하지 않습니다. 통합 로그는 크기 한도를 넘으면 오래된 메시지부터 지우기 때문입니다([허브](index.md)).

보고서에는 "이 시각에 `sudo` 프로세스가 `root` 가 든 메시지를 남겼고, 메시지에 이 명령이 보인다" 처럼 기록에 있는 만큼만 씁니다.

## 시각 해석

sudo 기록은 셸 기록이나 감사 로그와 맞춰 볼 때가 많아서, 모두 한 시간대로 맞춘 뒤 비교합니다. 통합 로그 시각의 계산 방법은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있고, `log show` 는 `--timezone` 옵션으로 출력 시간대를 정할 수 있습니다 [5].

## 함정과 한계

- **메시지 형식 미확인.** sudo 성공·실패 문구와 형식을 확인하지 못했습니다. 한 검체에서 확인한 형식을 다른 버전 검체에 그대로 적용하지 않습니다.
- **권한 확인 대화상자의 빈칸.** 앱이 관리자 암호를 묻는 대화상자 쪽 기록은 이번 자료로 조건을 확인하지 못했습니다. 이 경로의 지속성 위치는 [그 밖의 지속성 위치 (Login Hook·Authorization Plugin·Emond)](../../persistence/other-persistence.md)에서 다룹니다.
- **Jamf 필터 목록의 변화.** Jamf 는 "사용자 인증 이벤트" 필터를 자체 기능으로 옮기면서 공개 목록에서 뺐습니다 [4]. 공개 필터 목록에 없다고 해서 그 기록이 통합 로그에 없다는 뜻은 아닙니다.
- **TCC 해석.** `tccd` 기록의 뜻과 권한 데이터베이스는 [개인 정보 보호 권한 (TCC)](../../credentials/tcc/index.md)에서 다룹니다.

## 직접 분석해 보기

헥스로 따라가는 방법은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있고, 여기서는 도구로 조건을 걸어 봅니다.

1. 검체의 `.logarchive` 를 준비합니다.
2. `sudo` 조건으로 메시지를 뽑습니다 [5]. 따옴표는 실제 맥에서 한 번 돌려 확인합니다.

```
log show --archive <경로> --predicate 'process == "sudo"' --style ndjson
```

3. 결과 메시지를 몇 개 읽고, 명령과 대상 사용자가 어떤 모양으로 들어 있는지 사건 기록에 적습니다.
4. 공개 파서 Mandiant `unifiedlog_parser` 로 같은 아카이브를 CSV 로 풀고 [2], 프로세스 경로가 `/usr/bin/sudo` 인 줄만 골라 `log show` 결과와 수를 비교합니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [터미널 명령 기록 (zsh_history·bash_sessions)](../../execution/shell-history.md) | 같은 시각에 셸 기록에도 `sudo` 명령이 있는지 |
| [감사 로그 (OpenBSM Audit)](../openbsm-audit.md) | 같은 시각의 감사 기록 |
| [사용자 계정 (Local Accounts)](../../system-account/user-accounts/index.md) | 관리자 그룹 소속과 루트 계정 상태 |
| [개인 정보 보호 권한 (TCC)](../../credentials/tcc/index.md) | `tccd` 기록과 권한 데이터베이스의 변경 |

침해 사고에서 권한 상승 흔적을 따라가는 흐름은 [권한 상승과 TCC 우회 흔적 (Privilege·TCC Bypass)](../../../04-scenarios/incident/privilege-tcc-bypass.md)에 있습니다.

## 실습

공개 검체(NIST CFReDS 등)에 `.logarchive` 나 통합 로그 폴더가 들어 있으면 풀어 봅니다.

1. `sudo` 조건에 걸린 메시지가 몇 개인지, 가장 이른 것과 가장 늦은 것의 시각을 적어 보세요.
2. 메시지에 보이는 명령을 셸 기록과 맞춰 보고, 한쪽에만 있는 명령을 찾아 보세요.
3. `tccd` 조건의 결과에서 접근을 요청한 프로세스 이름을 모아 보세요.

## 참고 문헌

1. CrowdStrike, How to Leverage Apple Unified Log for Incident Response — https://www.crowdstrike.com/blog/how-to-leverage-apple-unified-log-for-incident-response/
2. Mandiant(Google Cloud), Reviewing macOS Unified Logs — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
3. Mac logging and the log command: A guide for Apple admins — https://www.iru.com/blog/mac-logging-and-the-log-command-a-guide-for-apple-admins
4. jamf/jamfprotect, unified_log_filters — https://github.com/jamf/jamfprotect/tree/main/unified_log_filters
5. log(1) man page — https://keith.github.io/xcode-man-pages/log.1.html
