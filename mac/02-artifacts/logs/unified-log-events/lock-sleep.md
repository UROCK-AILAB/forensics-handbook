---
title: "잠금·잠금 해제·잠자기"
parent: "통합 로그에서 찾을 것"
grand_parent: "아티팩트 · 로그"
nav_order: 1730
---

# 잠금·잠금 해제·잠자기 (Lock·Sleep)

잠금 화면에서 암호를 틀린 기록은 `loginwindow` 메시지로, Apple Watch 로 잠금을 푼 기록은 서브시스템 `com.apple.sharing` 의 `AutoUnlock` 카테고리로 찾을 수 있습니다. 잠금·잠금 해제 성공과 잠자기·깨우기를 뜻하는 통합 로그 메시지 문구는 실제 로그로 확인해야 합니다 [1][2][3].

## 무엇을 기록하나 · 왜 생기나

로그인한 뒤에도 맥은 화면을 잠그고 풀거나 잠들고 깨어나기를 되풀이하고, 이 구간을 이어 붙여야 사용자가 언제 맥 앞에 있었는지 그릴 수 있습니다. 통합 로그 쪽 단서는 두 가지입니다.

첫째는 잠금 화면에서 잠금 해제에 실패한 기록입니다. `/System/Library/CoreServices` 아래에서 실행된 `loginwindow` 가 남긴 메시지 중 실패를 뜻하는 알려진 문자열이 든 것을 고르면 됩니다. Jamf Protect 의 `lock_screen_unlock_failure.yaml` 필터가 이 방식으로 기록을 잡습니다 [1][2]. 둘째는 Apple Watch 로 잠금을 푼 기록이고, 서브시스템 `com.apple.sharing` 과 카테고리 `AutoUnlock` 으로 거릅니다 [3].

잠자기와 깨우기 이력은 통합 로그를 거치지 않고 `pmset -g log` 로도 볼 수 있습니다. 이 명령은 잠자기·깨우기와 그 밖의 전원 관리 이벤트 이력을 보여 주고 [4], 자세한 내용은 [전원·잠자기 기록 (pmset)](../power-events.md)에서 다룹니다.

통합 로그의 저장 위치와 보관 방식은 [통합 로그에서 찾을 것 (Unified Log Events)](index.md)에 있습니다.

## 위치와 버전별 차이

기록은 다른 통합 로그 메시지와 같은 저장소에 섞여 있습니다. 아래 조건과 잠금·잠자기 메시지는 macOS 버전마다 다를 수 있습니다. 분석 대상의 버전에서 조건이 실제로 걸리는지 먼저 확인하고 씁니다.

## 구조 — 찾는 조건

| 보려는 것 | 조건 | 출처 |
|---|---|---|
| 잠금 화면 해제 실패 | `processImagePath BEGINSWITH "/System/Library/CoreServices" AND process == "loginwindow" AND eventMessage CONTAINS[c] "INCORRECT"` | [2] |
| Apple Watch 로 잠금 해제 | 서브시스템 `com.apple.sharing`, 카테고리 `AutoUnlock` | [3] |

실패 조건의 `CONTAINS[c]` 는 대소문자를 구분하지 않고 찾는다는 뜻이고, 연산자 설명은 [자주 쓰는 검색 조건 (Predicates)](predicates.md)에 있습니다. `INCORRECT` 가 들어간 실제 메시지 전문은 분석 대상 로그에서 확인합니다.

아래 항목은 찾는 조건을 싣지 않으니 실제 로그에서 확인합니다.

| 실제 로그로 확인할 것 | 비고 |
|---|---|
| 화면 잠금·잠금 해제 성공 메시지 | `loginwindow`·화면 보호기 쪽 후보가 거론되지만 문구는 실제 로그에서 확인 |
| 잠자기·깨우기를 기록하는 프로세스와 문구 | `powerd` 등이 후보로 거론되지만 실제 로그에서 확인 |

## 증거로서 의미

**증명하는 것.** 실패 조건에 걸리는 메시지가 있으면 그 시각에 잠금 화면에서 잠금 해제가 실패했다는 기록이 있다는 뜻이고 [2], 짧은 간격으로 여러 번 나오면 반복된 시도를 가리킵니다. `AutoUnlock` 메시지는 그 무렵 Apple Watch 로 잠금을 푸는 동작이 있었다는 단서입니다 [3].

**증명하지 못하는 것.** 실패 기록만으로는 누가 암호를 입력했는지, 암호를 잘못 기억한 사용자인지 다른 사람인지 구분하지 못합니다. 사용자 이름 같은 문자열은 출력에 `<private>` 로 가려질 수 있습니다 [3]. 실패 기록이 없어도 실패가 없었다고 단정하지 않고, 잠금 해제 성공과 잠자기·깨우기는 실제 로그에서 문구를 확인하기 전까지 다른 아티팩트로 채웁니다.

보고서에는 "이 시각 사이에 `loginwindow` 가 잠금 해제 실패 문자열이 든 메시지를 세 번 남겼다" 처럼 횟수와 프로세스를 밝혀 씁니다.

## 시각 해석

잠금·잠자기 구간을 그릴 때는 통합 로그 시각과 `pmset -g log` 시각을 한 시간대로 맞춰야 합니다. 통합 로그 시각의 계산 방법은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있고, `log show` 는 `--timezone` 옵션으로 출력 시간대를 정할 수 있습니다 [5]. 한 번의 잠자기 주기 안에서 잠자기와 깨우기 기록을 잇는 방법은 [전원·잠자기 기록 (pmset)](../power-events.md)에 있습니다.

## 함정과 한계

- **성공 기록의 빈칸.** 잠금 해제 성공, 잠자기 진입, 깨우기를 뜻하는 통합 로그 문구는 실제 로그에서 후보 프로세스의 메시지를 직접 읽고 뜻을 확인하기 전에는 보고서에 쓰지 않습니다.
- **로그인과 잠금 해제의 혼동.** 둘 다 `loginwindow` 쪽 기록이라 섞이기 쉽고, 로그인 쪽 조건은 [로그인·로그아웃 (Login·Logout)](login-logout.md)에 있습니다.
- **Jamf 필터 문자열.** `INCORRECT` 는 Jamf 가 실패로 본 알려진 문자열이고 [2], 모든 실패 메시지를 다 잡는다는 보장은 없습니다.
- **보관 기간.** 통합 로그는 크기 한도를 넘으면 오래된 메시지부터 지웁니다. 조사 기간이 로그 보관 범위 안에 드는지 먼저 봅니다([허브](index.md)).

## 직접 분석해 보기

헥스로 따라가는 방법은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있고, 여기서는 도구로 조건을 걸어 봅니다.

1. 분석 대상의 `.logarchive` 를 준비합니다.
2. 실패 조건을 걸어 메시지를 뽑습니다 [5]. 따옴표는 실제 맥에서 한 번 돌려 확인합니다.

```
log show --archive <경로> --predicate 'processImagePath BEGINSWITH "/System/Library/CoreServices" AND process == "loginwindow" AND eventMessage CONTAINS[c] "INCORRECT"'
```

3. 결과 메시지 전문을 읽고, 실패를 뜻하는 문구가 무엇인지 사건 기록에 적습니다.
4. `subsystem == "com.apple.sharing" AND category == "AutoUnlock"` 으로 Apple Watch 잠금 해제 기록을 뽑아 실패 기록과 시각순으로 합칩니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [전원·잠자기 기록 (pmset)](../power-events.md) | 잠자기·깨우기 시각과 잠금 해제 시도의 앞뒤 |
| [KnowledgeC (knowledgeC.db)](../../execution/knowledgec/index.md) | 기기 잠금과 화면 켜짐 기록 |
| [전원 로그 (PowerLog)](../../execution/powerlog.md) | 전원 상태 변화 |
| [로그인·로그아웃 (Login·Logout)](login-logout.md) | 잠금 해제 전후의 세션 기록 |

사용 구간을 하나로 이어 붙이는 흐름은 [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](../../../04-scenarios/activity/usage-time.md)에 있습니다.

## 실습

공개 시험 데이터(NIST CFReDS 등)에 `.logarchive` 나 통합 로그 폴더가 들어 있으면 풀어 봅니다.

1. 잠금 해제 실패 조건에 걸린 메시지가 몇 개인지, 가장 짧은 간격은 몇 초인지 적어 보세요.
2. 실패 메시지의 전문을 읽고 실패를 뜻하는 문구를 찾아 보세요.
3. 실패 시각 앞뒤에 KnowledgeC 의 기기 잠금 기록이 있는지 맞춰 보세요.

## 참고 문헌

1. jamf/jamfprotect, unified_log_filters — https://github.com/jamf/jamfprotect/tree/main/unified_log_filters
2. jamf/jamfprotect, lock_screen_unlock_failure.yaml — https://raw.githubusercontent.com/jamf/jamfprotect/main/unified_log_filters/lock_screen_unlock_failure.yaml
3. Mac logging and the log command: A guide for Apple admins — https://www.iru.com/blog/mac-logging-and-the-log-command-a-guide-for-apple-admins
4. SS64, pmset — https://ss64.com/mac/pmset.html
5. log(1) man page — https://keith.github.io/xcode-man-pages/log.1.html
