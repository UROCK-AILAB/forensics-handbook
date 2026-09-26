---
title: "그 시각에 폰을 쓴 사람이 누구인가"
parent: "시나리오 · 행위 재구성"
nav_order: 1620
---

# 그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)

## 조사 질문

"그 시각에 폰을 조작한 사람이 소유자인가, 폰을 넘겨받은 다른 사람인가" 를 묻는 흐름입니다. [폰 사용 시간 재구성](usage-time.md) 으로 화면이 켜지고 잠금이 풀린 구간을 세웠다면, 이 페이지는 그 구간을 어느 사용자 계정과 어떤 사람에게 이을 수 있는지, 어디까지가 기록이 말하는 범위인지를 따집니다.

먼저 짚을 점은 Android 기록의 단위입니다. 앱 사용 기록(usagestats)은 사용자별 경로(`*/system_ce/*/usagestats*`)에 쌓이고, 공개 도구 ALEAPP 도 결과를 사용자 칸으로 나눕니다 [2]. 이 단위는 기기 안의 "사용자(user ID)" 이지 사람이 아니라서, 기기 안 기록만으로는 "이 사용자 ID 에서 잠금이 풀리고 이 앱이 쓰였다" 까지 말할 수 있습니다. 그 사용자 ID 를 쓴 사람이 누구인지는 기기 안팎의 다른 기록과 시각을 맞춰 좁혀 가는 해석이고, 이 페이지는 그 해석에 쓸 흔적과 한계를 모읍니다. 잠금 해제나 보안 우회 방법은 다루지 않습니다.

## 먼저 확인할 것

- **사용자와 프로필** — 기기에 사용자가 몇 개 있는지, 보안 폴더나 작업 프로필 같은 프로필이 있는지부터 봅니다. `dumpsys user` 에서 주 사용자에는 `isPrimary=true` 가 붙고, 프로필에는 `parentId` 가 붙습니다(프로필 ID 는 세 자리일 수 있습니다). 보안 폴더인지 작업 프로필인지는 프로필의 Type 값으로 가립니다.
- **시간대와 시각 변경** — 사용자 정보의 시각은 벽시계 값과 부팅 후 경과 시간이 섞여 있어 어느 쪽인지 칸마다 가립니다(아래 표). 기기 시각이 옮겨졌는지는 [증거를 없애려 했나](anti-forensics/index.md) 묶음에서 먼저 점검합니다.
- **잠금 설정** — 사건 무렵 잠금 방식이 무엇이었는지에 따라 "잠금이 풀렸다" 는 기록의 무게가 달라집니다. 설정 키 읽는 법은 [잠금 화면 설정](../../02-artifacts/system-account/lock-settings.md) 에 있습니다.
- **수집 범위** — `dumpsys user`, `dumpsys account`, `dumpsys notification` 은 수집 시점의 상태이고, `/data/system/users/` 아래 파일은 전체 파일 시스템을 확보해야 볼 수 있습니다. 확보 방식은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 정합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 사용자 정보 (`/data/system/users/userlist.xml` 과 사용자별 XML, `dumpsys user`) | 기기 안 사용자·프로필 목록, 만든 시각, 마지막 로그인, 마지막으로 앞에 나온 시각 | [사용자와 프로필](../../02-artifacts/system-account/users-profiles.md) |
| 2 | 사용자별 usagestats | 그 사용자 ID 에서 화면·잠금·앱 화면이 바뀐 구간 | [앱 사용 기록](../../02-artifacts/app-usage/usagestats/index.md) |
| 3 | 잠금 관련 설정 키 (`settings secure`·`settings system`) | 사건 무렵 설정된 잠금 방식과 생체 인증 관련 항목의 이름 | [잠금 화면 설정](../../02-artifacts/system-account/lock-settings.md), [설정 값](../../02-artifacts/system-account/settings.md) |
| 4 | 계정 기록 (`dumpsys account` 의 Accounts History) | 계정이 추가·삭제된 시각과 그 동작을 부른 UID | [계정](../../02-artifacts/system-account/accounts/index.md) |
| 5 | 알림 (`dumpsys notification`) | 알림이 생긴 시각, 화면에 보이기 시작한 시각, 본 적 있는지 | [알림 기록](../../02-artifacts/app-usage/notification-history.md) |
| 6 | 무선 기록 (`dumpsys wifi`, `dumpsys bluetooth_manager`) | 다른 서비스가 받은 화면 상태 변화, 블루투스를 켠 주체와 이유 | [와이파이](../../02-artifacts/network/wifi.md), [블루투스 장치](../../02-artifacts/network/bluetooth.md) |

버전과 제조사에 따라 확인된 범위가 다릅니다.

| 기록 | 확인된 범위 | 비고 |
|---|---|---|
| 사용자 정보 파일과 XML 속성 이름 | 현행 AOSP 기준 [3] | 사용자별 파일 이름이 사용자 ID 를 딴 XML 인지는 검체에서 확인합니다 |
| `dumpsys user` 칸 | | 주 사용자의 Created 칸이 `<unknown>` 으로 찍힐 수 있습니다 |
| 삼성 보안 폴더 | 공개 자료 없음 | 보안 폴더가 어떤 사용자 ID 를 쓰는지, 그 안의 앱 사용이 따로 쌓이는지는 [보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md) 에서 봅니다 |

## 분석 흐름

1. **사용자와 프로필을 나눕니다.** 현행 AOSP 에서 사용자 정보는 `/data/system/users/` 아래 목록 파일 `userlist.xml` 과 사용자별 XML 에 있고 [3], 사용자별 XML 에는 아래 속성이 있습니다.

   | XML 속성 | 시각 기준 | 언제 바뀌나 |
   |---|---|---|
   | `created` | 벽시계 | 사용자를 만들 때 |
   | `lastLoggedIn` | 벽시계 | 공개 자료 없음 |
   | `lastLoggedInFingerprint` | 시각 값이 아님 | 공개 자료 없음 |
   | `lastEnteredForeground` | 벽시계 밀리초 | 사용자가 시작될 때와 사용자 전환 때 그 시각으로 바뀜 |

   소스에는 이 밖에 부팅 후 경과 시간으로 적는 `startRealtime`(사용자가 시작된 때)과 `unlockRealtime`(사용자 잠금이 풀린 때)이 있어, 재부팅하면 기준점이 바뀝니다 [3]. `dumpsys user` 에는 Created, Last logged in, Last logged in fingerprint, Start time, Unlock time, Last entered foreground 칸이 있지만, 이 칸들이 위 속성과 하나씩 대응한다는 공개 자료는 없어 그렇게 단정하지 않습니다. 사건 시각의 활동이 어느 사용자 ID 에 쌓였는지부터 가리고, 프로필의 활동을 주 사용자의 활동과 합치지 않습니다.

2. **그 사용자 ID 의 사용 구간을 가져옵니다.** [폰 사용 시간 재구성](usage-time.md) 의 흐름대로 화면·잠금·앱 구간을 세우고, 사건 시각이 그 구간 안에 드는지 봅니다. 잠금이 풀린 기록 `KEYGUARD_HIDDEN` 에는 `package` 와 `flags` 칸만 있고, 이 이벤트는 "보통 사용자가 잠금을 풀 때" 생길 뿐이라서 [1] PIN·지문·얼굴 가운데 무엇으로 누가 풀었는지는 이 기록에 없습니다. 어떤 생체 인증으로 풀었는지 따로 남는 기록은 공개 자료가 없어 검체에서 확인합니다.

3. **잠금 방식을 확인합니다.** `settings secure` 에는 `lockscreen.disabled`, `lockscreen.options`, `lock_screen_lock_after_timeout`, `fingerprint_screen_lock`, `face_screen_lock`, `biometrics_strong_enroll_timestamp`, 여러 `active_unlock_*`, `aware_lock_enabled` 같은 키가 있고, `settings system` 에는 `screen_off_timeout`, `db_lockscreen_is_smart_lock`, `automatic_unlock` 같은 키가 있습니다. 각 키의 뜻은 이름으로 짐작하지 말고 [잠금 화면 설정](../../02-artifacts/system-account/lock-settings.md) 의 근거로 확인합니다. 잠금 방식이 아예 없거나 신뢰 장치·얼굴로 풀리는 설정이었다면, `KEYGUARD_HIDDEN` 이 이런 경우를 구분해 주지 않아 [1] "잠금이 풀렸다" 가 곧 "비밀번호를 아는 사람이 풀었다" 가 되지 않습니다.

4. **계정 흔적으로 사람과 잇는 단서를 찾습니다.** `dumpsys account` 에는 계정 목록(`Account {name=..., type=...}` 모양)과 "Accounts History" 가 있고, 기록의 칸 머리는 아래와 같습니다.

   ```
   AccountId, Action_Type, timestamp, UID, TableName, Key
   ```

   `Action_Type` 에는 `action_account_add`, `action_account_remove`, `action_called_account_add`, `action_called_account_remove`, `action_authenticator_remove`, `action_clear_password` 같은 값이 나옵니다. 사건 구간 가까이에 계정이 추가·삭제된 기록이 있으면 그 계정이 누구의 것인지가 사람을 좁히는 단서가 될 수 있지만, 이 부분은 기록이 아니라 해석이라서 보고서에서도 해석으로 나눠 적습니다.

5. **알림과 무선 기록으로 같은 시각을 한 번 더 찍습니다.** `dumpsys notification` 알림 항목에는 `mCreationTimeMs`, `mVisibleSinceMs`, `mUpdateTimeMs`, `seen` 칸과 `posttimeToFirstClickMs`, `posttimeToDismissMs`, `airtimeMs` 가 든 `stats` 줄이 있습니다. `dumpsys wifi` 에는 `what=CMD_SCREEN_STATE_CHANGED screen=...` 줄이, `dumpsys bluetooth_manager` 의 "Enable log:" 에는 `Package [android] requested to [Enable]. Reason is SYSTEM_BOOT` 모양의 줄이 남습니다. 알림 칸 하나하나의 뜻은 공개 자료가 없으니, 이 기록들은 usagestats 가 세운 구간과 같은 시각에 다른 서비스도 화면 변화를 기록했는지 확인하는 데 씁니다. 연결된 블루투스 기기(시계·차량 등)가 사람을 가리는 단서가 되는지는 사건마다 따로 따집니다.

6. **기기 밖 자료와 시각을 맞춥니다.** 기기 안 기록은 사용자 ID 까지만 가리키니, 사람을 특정하려면 CCTV, 다른 기기의 기록, 위치 자료, 진술처럼 기기 밖 자료와 1~5단계의 시각을 맞춥니다. 위치는 [그 시각에 어디 있었나](location.md) 에서, 여러 자료를 한 시간 축에 놓는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 봅니다.

7. **결론의 높이를 정합니다.** "이 사용자 ID 에서 이런 기록이 있다" 는 기록이 말하는 사실이고, "그 사람이 썼다" 는 여러 기록을 맞춘 해석입니다. 보고서에는 두 층을 나눠 적습니다.

> 그림 자리: 아래에서 위로 "기기 기록(사용자 ID)", "사용자 ID 와 계정·잠금 설정", "기기 밖 자료", "사람" 네 층을 쌓고, 층을 올라갈수록 해석이 더해진다는 점을 보여 주는 그림

## 흔한 오판

**잠금이 풀린 기록을 소유자가 쓴 증거로 읽는 오판**이 가장 흔합니다. `KEYGUARD_HIDDEN` 은 잠금 화면이 걷혔다는 사실만 담고, 풀린 방법과 사람은 담지 않습니다 [1].

**사용자 ID 를 사람과 같게 보는 경우**도 있습니다. 한 사람이 여러 프로필을 쓸 수 있고, 여러 사람이 한 사용자 ID 로 폰을 돌려 쓸 수도 있습니다.

**프로필 안의 활동을 주 사용자 기록에 섞는 경우**가 있습니다. usagestats 경로가 사용자별이라서 [2] 프로필의 앱 사용은 그 프로필 사용자 ID 쪽에서 따로 봐야 한다고 해석할 수 있지만, 삼성 보안 폴더에서 실제로 그렇게 쌓이는지는 검체에서 확인합니다.

**부팅 후 경과 시간을 벽시계 시각으로 옮기는 실수**도 조심합니다. `startRealtime` 과 `unlockRealtime` 은 부팅 뒤 흐른 시간이라서 [3] 부팅 시각을 모르면 날짜로 바꿀 수 없습니다.

**계정이 등록돼 있다는 이유로 그 계정 주인이 그 시각에 썼다고 보는 경우**도 지나칩니다. 계정 목록은 수집 시점의 상태이고, 기록 시각의 조작자를 알려 주지 않습니다.

## 보고서 문장 예

| 쓰지 않을 문장 | 쓸 문장 |
|---|---|
| 피의자가 ○○:○○에 자신의 지문으로 폰 잠금을 풀었다. | 기기의 앱 사용 기록에 따르면, 기기 시각 기준 ○○일 ○○:○○에 사용자 ID ○의 잠금 화면이 숨겨진 기록(`KEYGUARD_HIDDEN`)이 있습니다. 이 기록에는 잠금을 푼 방법과 사람이 담겨 있지 않습니다. |
| 폰을 쓴 사람은 소유자다. | 같은 시각 무렵 이 기기에 등록된 ○○ 계정의 추가 기록이 있고, 기기 밖 자료(○○)에서 소유자가 같은 시각 ○○에 있었던 기록이 확인됩니다. 이 두 기록을 맞춰 보면 소유자가 조작했을 가능성이 높다고 판단하며, 이 판단은 해석입니다. |
| 보안 폴더에서도 같은 사람이 활동했다. | 기기에는 주 사용자 외에 프로필 사용자(ID ○○○)가 하나 있고, 이 프로필의 기록은 주 사용자 기록과 따로 분석했습니다. |

보고서 전체의 틀은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 아티팩트 본문: [사용자와 프로필](../../02-artifacts/system-account/users-profiles.md), [계정](../../02-artifacts/system-account/accounts/index.md), [잠금 화면 설정](../../02-artifacts/system-account/lock-settings.md), [알림 기록](../../02-artifacts/app-usage/notification-history.md), [dumpsys 출력](../../02-artifacts/logs/dumpsys.md)
- 기반 구조: [보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md)
- 이어지는 시나리오: [폰 사용 시간 재구성](usage-time.md), [그 시각에 어디 있었나](location.md), [계정 탈취 흔적](../incident/account-takeover.md)

## 참고 문헌

1. UsageEvents.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/app/usage/UsageEvents.java
2. ALEAPP usagestats.py — abrignoni/ALEAPP (main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/usagestats.py
3. UserManagerService.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/UserManagerService.java
