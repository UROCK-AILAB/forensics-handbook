---
title: "잠금·잠금 해제·잠자기"
parent: "통합 로그에서 찾을 것"
grand_parent: "아티팩트 · 로그"
nav_order: 1730
---

# 잠금·잠금 해제·잠자기 (Lock·Sleep)

잠금 화면에서 암호를 틀린 기록은 `loginwindow` 메시지로, Apple Watch 로 잠금을 푼 기록은 서브시스템 `com.apple.sharing` 의 `AutoUnlock` 카테고리로 찾을 수 있습니다. 잠금을 Touch ID 로 풀었는지 암호로 풀었는지는 키백 상태 전환 메시지로 구분되고, 맥을 깨운 장치는 `powerd` 메시지에 나옵니다 [1][2][3][6].

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
| 화면 잠금 메시지 | `loginwindow`·화면 보호기 쪽 후보가 거론되지만 문구는 실제 로그에서 확인 |
| 잠자기 진입을 기록하는 문구 | `powerd` 등이 후보로 거론되지만 실제 로그에서 확인 |

## 잠금 해제 방식 구분 (Touch ID·암호)

잠금 화면을 무엇으로 풀었는지는 키백 (keybag) 상태 전환 메시지 한 줄로 구분됩니다. 서브시스템 `com.apple.chrono`, 카테고리 `keybag` 의 `Transition:` 메시지가 Touch ID 로 풀면 `locked -> inBioUnlock`, 암호로 풀면 `locked -> unlocked` 입니다 [6]. 등록되지 않은 지문을 대면 센서 기록만 남고 키백 전환은 없습니다 [6].

| 경우 | 남는 기록 |
|---|---|
| Touch ID 성공 | `AppleMesaSEPDriver` 의 `kAppleBiometricFingerOnEvent`·`kAppleBiometricFingerOffEvent`, `chronod` 의 `Transition: locked -> inBioUnlock`, `biometrickitd` 의 `matchResult:timestamp: MATCH` 와 등록된 지문 템플릿의 UUID [6] |
| 등록 안 된 지문 | 같은 센서 기록, `biometrickitd` 의 `matchResult:timestamp: NO-MATCH`, `coreauthd` 의 `has received no-match`. 키백 전환은 없음 [6] |
| 암호 | `loginwindow` 의 `Attempt #:` 와 `authSuccess`, `opendirectoryd` 의 `Verified password for`, `authd` 의 `authenticated as user … for right 'system.login.screensaver'`, `ControlCenter` 의 `Transition: locked -> unlocked` [6] |

아래는 형식을 보여 주는 예입니다(UUID·프로세스 번호는 만든 예시).

```
chronod[741]: (ChronoServices) [com.apple.chrono:keybag] Transition: locked -> inBioUnlock
biometrickitd[434]: [com.apple.BiometricKit:Daemon-Mesa] matchResult:timestamp: MATCH 503: 11111111-2222-3333-4444-555555555555
ControlCenter[670]: (ChronoServices) [com.apple.chrono:keybag] Transition: locked -> unlocked
```

암호로 풀면 `authd` 가 계정 이름과 받은 권한, 요청한 프로그램을 평문으로 남기지만, Touch ID 로 풀면 계정 이름이 남지 않습니다 [6]. `coreauthd` 는 `has received finger-on`, `has received finger-off`, `has received no-match` 는 남기지만 `has received match` 는 남기지 않아서, `has received no-match` 는 지문 거부만 가리키는 문자열로 쓸 수 있습니다 [6].

무엇이 맥을 깨웠는지는 `powerd` 의 `TurnedOn UserIsActive` 메시지에 나옵니다. `queue.tickle serviceID:` 뒤의 서비스 이름이 깨운 장치이고, 내장 키보드·트랙패드는 `AppleHIDKeyboardEventDriverV2` 로 나옵니다 [6]. 잠금 화면이 뜨면 `loginwindow` 가 보안 입력 (secure event input) 을 켜서, 입력한 암호나 키는 로그에 남지 않습니다 [6].

로그를 뽑을 때는 `--info` 와 `--debug` 를 함께 줍니다. 둘 가운데 하나라도 빠지면 위 메시지 대부분이 빠집니다 [5][6].

```
log show --archive <경로> --style syslog --info --debug --start "2026-08-27 09:00:00" --end "2026-08-27 09:10:00"
```

찾을 문자열은 `chrono:keybag] Transition:`, `matchResult:timestamp:`, `has received no-match`, `queue.tickle serviceID:`, `Attempt #:`, `for right 'system.login.screensaver'` 입니다 [6]. `MATCH` 만으로 찾으면 `NO-MATCH` 도 걸리므로 `grep -w` 를 쓰거나 문자열 전체로 찾습니다.

위 문자열은 macOS 26.6.2(25G83) Apple 실리콘 맥 한 대에서 계정 하나, 등록 지문 하나로 Touch ID 해제 10번, 등록 안 된 지문 5번, 암호 해제 5번을 해서 확인된 것입니다 [6]. 다른 버전이나 계정·지문이 여럿인 맥에서는 같은 문자열이 나오는지 실제 로그로 먼저 확인합니다. 서로 다른 프로세스가 1초 안에 남긴 메시지의 순서는 각 프로세스가 기록한 순서일 뿐 일이 일어난 순서가 아니고, 지문을 뗄 때 나오는 `_sensorState` 값은 같은 동작에서도 4 와 5 로 달라서 지표로 쓰지 않습니다 [6].

## 증거로서 의미

**증명하는 것.** 실패 조건에 걸리는 메시지가 있으면 그 시각에 잠금 화면에서 잠금 해제가 실패했다는 기록이 있다는 뜻이고 [2], 짧은 간격으로 여러 번 나오면 반복된 시도를 가리킵니다. `AutoUnlock` 메시지는 그 무렵 Apple Watch 로 잠금을 푸는 동작이 있었다는 단서입니다 [3].

**증명하지 못하는 것.** 실패 기록만으로는 누가 암호를 입력했는지, 암호를 잘못 기억한 사용자인지 다른 사람인지 구분하지 못합니다. 사용자 이름 같은 문자열은 출력에 `<private>` 로 가려질 수 있습니다 [3]. 실패 기록이 없어도 실패가 없었다고 단정하지 않습니다. Touch ID 로 풀었다는 기록은 등록된 지문으로 풀었다는 뜻이지, 그 지문의 주인이 누구인지는 알려 주지 않습니다.

보고서에는 "이 시각 사이에 `loginwindow` 가 잠금 해제 실패 문자열이 든 메시지를 세 번 남겼다" 처럼 횟수와 프로세스를 밝혀 씁니다.

## 시각 해석

잠금·잠자기 구간을 그릴 때는 통합 로그 시각과 `pmset -g log` 시각을 한 시간대로 맞춰야 합니다. 통합 로그 시각의 계산 방법은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있고, `log show` 는 `--timezone` 옵션으로 출력 시간대를 정할 수 있습니다 [5]. 한 번의 잠자기 주기 안에서 잠자기와 깨우기 기록을 잇는 방법은 [전원·잠자기 기록 (pmset)](../power-events.md)에 있습니다.

## 함정과 한계

- **버전마다 다른 문구.** 잠금 해제 방식을 가르는 문자열은 macOS 26.6.2 에서 확인된 것이고 [6], 잠자기 진입 문구는 실제 로그에서 뜻을 확인하기 전에는 보고서에 쓰지 않습니다.
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
6. Tim Korver, "Touch ID vs password unlock in the Apple Unified Log (macOS 26)", Thesis Friday #26 (2026-08-28) — https://thesisfriday.com/thesis-friday-26-same-unlock-three-different-stories/
