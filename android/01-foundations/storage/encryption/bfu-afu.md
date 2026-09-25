---
title: "잠금 해제 전·후"
parent: "저장 공간 암호화"
grand_parent: "기반 · 저장 구조"
nav_order: 100
---

# 잠금 해제 전·후 (BFU·AFU)

기기를 다시 시작한 뒤 사용자가 아직 한 번도 잠금을 풀지 않은 상태를 잠금 해제 전(BFU, Before First Unlock), 한 번 푼 뒤의 상태를 잠금 해제 후(AFU, After First Unlock)라고 부르고, 두 상태는 기기 안에서 복호화된 채 쓸 수 있는 데이터의 범위가 다릅니다.

## 이름과 공식 개념

BFU·AFU 라는 이름은 열어 본 Android 공식 문서에는 나오지 않습니다. 공식 문서는 기기를 켰지만 사용자가 아직 잠금을 풀지 않은 상태를 다이렉트 부트 모드 (Direct Boot mode) 라고 부르고, 이 모드는 Android 7.0(API 24)에서 들어왔습니다. 이 핸드북에서는 BFU 를 다이렉트 부트 모드와 같은 뜻으로 쓰고, AFU 를 첫 잠금 해제 뒤부터 다음 재시작 전까지의 상태로 씁니다.

## 두 상태에서 쓸 수 있는 영역

Android 는 사용자마다 저장 공간을 CE 영역과 DE 영역으로 나누고, 두 영역의 경로와 키는 [CE 영역과 DE 영역](ce-de-storage.md) 페이지에서 다룹니다. 여기서는 CE 영역은 사용자가 잠금을 푼 뒤에만 쓸 수 있고 DE 영역은 다이렉트 부트 중에도 잠금을 푼 뒤에도 쓸 수 있다는 점만 알면 됩니다.

| 상태 | 공식 문서의 이름 | CE 영역 | DE 영역 |
|---|---|---|---|
| BFU | 다이렉트 부트 모드 | 쓸 수 없음 | 쓸 수 있음 |
| AFU | (잠금 해제 뒤) | 쓸 수 있음 | 쓸 수 있음 |

앱은 `UserManager.isUserUnlocked()` 로 사용자가 잠금을 풀었는지 확인합니다 [1].

## 화면 잠김과 CE 잠김은 다릅니다

CE 영역은 사용자가 잠금을 푼 뒤 기기를 다시 시작할 때까지 계속 쓸 수 있고, 그 사이에 잠금 화면이 다시 켜져도 마찬가지입니다. 잠금 화면이 떠 있다고 BFU 인 것은 아니며, CE 영역이 다시 잠기는 계기는 재시작입니다. 전원이 꺼졌다가 다시 켜지는 경우도 재시작이라서, 그 뒤에는 사용자가 다시 잠금을 풀 때까지 BFU 상태로 돌아갑니다.

## 부팅할 때 시스템이 보내는 방송

재시작한 뒤 시스템은 아래 순서로 방송 (Broadcast) 을 보냅니다. 앱이 어느 방송을 받았는지는 그 시점에 쓸 수 있는 영역과 이어집니다.

| 방송 | 보내는 때 |
|---|---|
| `ACTION_LOCKED_BOOT_COMPLETED` | 재시작 뒤, DE 영역만 쓸 수 있을 때 |
| `ACTION_USER_UNLOCKED` | 잠금 해제 직후(포그라운드 프로세스용) |
| `ACTION_BOOT_COMPLETED` | 잠금 해제 뒤(늦게 받아도 되는 백그라운드용) |

## 시스템의 사용자 상태 값

시스템은 사용자마다 실행 상태를 숫자로 관리합니다. 아래 표는 현행 AOSP 기준 `UserState.java` 의 값입니다.

| 값 | 이름 | 소스의 설명 |
|---|---|---|
| -1 | `STATE_NONE` | 사용자 없음(문자열로 바꾸는 대상이 아님) |
| 0 | `BOOTING` | 사용자가 처음 올라오는 중 |
| 1 | `RUNNING_LOCKED` | 잠긴 상태 |
| 2 | `RUNNING_UNLOCKING` | 잠금 해제 중 |
| 3 | `RUNNING_UNLOCKED` | 실행 중(잠금 해제됨) |
| 4 | `STOPPING` | 멈추는 중 |
| 5 | `SHUTDOWN` | `ACTION_SHUTDOWN` 을 보내는 중 |

소스는 이 값을 BFU·AFU 라는 이름과 직접 연결하지 않습니다. 다만 `RUNNING_LOCKED` 와 `RUNNING_UNLOCKED` 는 사용자가 잠금을 풀었는지를 나타내는 이름이라서, 수집 시점의 상태를 적을 때 근거로 쓸 수 있습니다.

## 기기에 남는 흔적

adb 일반 셸 권한으로 `dumpsys user` 를 읽으면 기본 사용자 블록의 `State:` 줄에 현재 상태 이름이 나오고, 같은 블록에 `Start time:`, `Unlock time:`, `Last logged in:` 칸이 있습니다. 관찰 기기에서는 이 줄이 `State: RUNNING_UNLOCKED` 였고, 다른 칸의 값은 가려서 확인하지 않았습니다.

```
Current user: #
Users:
  UserInfo{#:xxx:#c##} serialNo=# isPrimary=true
    State: RUNNING_UNLOCKED
    Last logged in: (가림)
    Start time: (가림)
    Unlock time: (가림)
```

위 출력은 관찰 메모에서 필요한 줄만 옮긴 것이고, `#` 와 `(가림)` 은 가린 자리입니다. `Unlock time` 은 이름으로 보아 잠금 해제 시각을 적는 칸이지만, 어떤 시계를 기준으로 어떤 형식으로 적는지는 확인하지 못했습니다. dumpsys 출력을 읽는 방법은 [dumpsys 출력](../../../02-artifacts/logs/dumpsys.md) 페이지를 봅니다.

앱 사용 기록의 이벤트에도 `KEYGUARD_SHOWN`·`KEYGUARD_HIDDEN` 줄이 있어서 잠금 화면이 나타나고 사라진 시각의 흔적이 남습니다. 이 이벤트의 해석은 [앱 사용 기록](../../../02-artifacts/app-usage/usagestats/index.md) 페이지에서 다룹니다.

설정 값에는 재시작·잠금과 이름이 이어지는 키가 있습니다. 이름만 확인했고, 각 키가 무엇을 기록하는지는 공식 문서로 확인하지 못했습니다.

- global: `boot_count`, `add_users_when_locked`
- secure: `lockdown_in_power_menu`, `lock_screen_lock_after_timeout`, `theft_detection_lock_supported`, `remote_lock_setting`, `fmm_unlock_recovery`

설정 값을 읽는 법은 [설정 값](../../../02-artifacts/system-account/settings.md) 페이지를, 잠금 방식과 관련된 설정은 [잠금 화면 설정](../../../02-artifacts/system-account/lock-settings.md) 페이지를 봅니다.

## 포렌식에서 중요한 점

아래 내용은 공식 문서의 설명에서 끌어낸 해석이고, 문서에 이 문장 그대로 있지는 않습니다. BFU 상태에서는 기기 안에서도 CE 영역을 쓸 수 없어서 복호화된 채 읽을 수 있는 범위가 DE 영역으로 좁아지고, AFU 상태에서는 CE 영역까지 쓸 수 있습니다. 압수한 기기가 AFU 상태라도 재시작하면 BFU 로 돌아가기 때문에, 기기를 받은 시점의 상태와 그 뒤 재시작 여부를 기록해 두어야 결과의 차이를 설명할 수 있습니다. 수집 절차 전체는 [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지에서 다룹니다.

## 함정

잠금 화면이 떠 있는 기기를 BFU 라고 단정하면 안 되고, `KEYGUARD_SHOWN`·`KEYGUARD_HIDDEN` 이벤트도 화면 잠금의 흔적일 뿐 CE 영역이 잠기거나 풀린 시각을 뜻하지 않습니다. `dumpsys user` 의 상태 값은 명령을 실행한 순간의 상태라서, 이 값만으로 그 이전에 재시작이 있었는지는 알 수 없습니다. 어떤 앱이 DE 영역에 무엇을 두는지는 앱마다 달라서, BFU 상태에서 읽히는 앱 데이터의 범위도 앱마다 다릅니다.

## 도구

- `adb shell dumpsys user`: 사용자별 상태 이름과 시각 칸
- `adb shell dumpsys usagestats`: 잠금 화면 표시·해제 이벤트
- `adb shell settings list global`, `adb shell settings list secure`: 설정 키와 값

## 참고 문헌

1. Support Direct Boot mode — Android Developers — https://developer.android.com/privacy-and-security/direct-boot
2. UserState.java (AOSP frameworks/base, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/am/UserState.java
