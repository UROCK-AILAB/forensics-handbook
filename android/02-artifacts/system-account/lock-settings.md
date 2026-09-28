---
title: "잠금 화면 설정"
parent: "아티팩트 · 시스템·계정"
nav_order: 390
---

# 잠금 화면 설정 (Lock Settings)

화면 잠금이 설정되어 있었는지, 어떤 종류였는지, 신뢰 에이전트나 생체 인증을 함께 썼는지를 알려 주는 기록을 정리합니다. 이 페이지는 잠금 방식과 설정 흔적만 다루고, 자격 증명을 알아내거나 잠금을 푸는 방법은 다루지 않습니다. 값은 현행 AOSP 기준(frameworks/base 의 main 가지)입니다.

시스템의 잠금 설정 저장소(LockSettingsStorage)가 잠금 관련 값을 SQLite 파일 `locksettings.db` 의 `locksettings` 표에 사용자 번호와 함께 적고 [1], 화면 잠금과 관련된 나머지 값은 settings 의 secure·system 표에 흩어져 있어서 두 곳을 함께 봐야 잠금 설정 상태를 읽을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

LockSettingsStorage 는 잠금과 관련된 값을 `locksettings` 표에 이름·사용자·값의 쌍으로 적고, 잠금 자격 증명을 보호하는 자료는 사용자별 폴더의 별도 파일(spblob)에 따로 저장합니다 [1].

조사에서 이 기록이 중요한 이유는 기기를 쓴 사람을 가려낼 때 잠금이 걸려 있었는지가 출발점이 되기 때문입니다. 잠금이 없었다면 기기를 손에 쥔 누구나 쓸 수 있었고, 잠금이 있었다면 잠금을 푼 시각이 사람이 기기를 쓴 시각의 단서가 됩니다. 이 판단의 순서는 [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](../../04-scenarios/activity/user-attribution.md) 시나리오에 있습니다.

## 위치와 버전별 차이

| 파일·폴더 | 내용 | 출처 |
|---|---|---|
| `locksettings.db` | 표 `locksettings`, 열 `_id`·`name`·`user`·`value`. 모든 사용자의 값을 한 표에 사용자 번호와 함께 적음 | [1] |
| 사용자별 키 파일 폴더 | 사용자 0 은 `/data/system/`, 다른 사용자는 `/data/system/users/<사용자ID>/` | [1] |
| `gatekeeper.profile.key` | 자식 프로필 잠금(위 사용자별 폴더) | [1] |
| `reboot.escrow.key`, `reboot.escrow.server.blob.key` | 이름으로 보면 재부팅과 관련된 키(앞은 사용자별 폴더, 뒤는 사용자 0 폴더에 하나) | [1] |
| `/data/system_de/<사용자ID>/spblob/` | 잠금 자격 증명을 보호하는 자료(synthetic password) 파일. 사용자 0 도 여기에 있음. 이름은 보호자 ID 를 16진수 16자리로 적고 점 뒤에 상태 이름을 붙인 모양 | [1] |
| `repair-mode/pst` | 수리 모드(metadata 폴더) | [1] |

`locksettings.db` 는 시스템 서비스의 데이터베이스 폴더에 만들어지고, 그 폴더가 `/data/system/` 인지는 실제 기기에서 확인합니다. 현행 소스에는 `gesture.key`, `password.key`, `gatekeeper.pattern.key` 같은 옛 파일 이름이 나오지 않아서 [1], 옛 버전 기기에서는 이 파일들이 있는지 따로 봅니다. CE·DE 영역의 차이는 [저장 공간 암호화 (Encryption)](../../01-foundations/storage/encryption/index.md) 페이지에 있습니다.

삼성 기기는 AOSP 에 없는 잠금 관련 settings 키를 더 씁니다. secure 표에는 다음과 같은 키가 있습니다.

```
lockscreen.disabled               lockscreen.options
lock_screen_lock_after_timeout    lock_screen_show_notifications
lock_screen_allow_private_notifications
lockdown_in_power_menu            sleep_timeout
fingerprint_screen_lock           face_screen_lock
biometrics_strong_enroll_timestamp
trust_agents_initialized          known_trust_agents_initialized
trusted_locations_count           theft_detection_lock_supported
remote_lock_setting               fmm_unlock_recovery
active_unlock_*                   mandatory_biometrics_*
```

system 표에는 `screen_off_timeout`, `db_lockscreen_is_smart_lock`, `lockscreen_sounds_enabled`, `lockscreen_wallpaper`, `lockstar_enabled` 가, global 표에는 `lock_sound`, `unlock_sound`, `trusted_sound` 가 있습니다. `lock_screen_owner_info` 와 `lock_pattern_autolock` 은 목록에 없을 수 있습니다. 이 키들 값의 뜻은 시험 기기에서 설정을 바꿔 가며 확인합니다. settings 파일의 구조는 [설정 값 (Settings Global·Secure·System)](settings.md) 페이지에 있습니다.

## 구조

### locksettings 표의 키

`LockPatternUtils` 에 정의된 키 이름은 다음과 같습니다(현행 AOSP 기준) [2].

| 키 | 비고 |
|---|---|
| `lockscreen.password_type` | 잠금 종류 값 |
| `lockscreen.password_type_alternate` | 폐기됨 |
| `lockscreen.password_salt` | |
| `lockscreen.disabled` | |
| `lockscreen.power_button_instantly_locks` | 전원 버튼으로 바로 잠금 |
| `lockscreen.widgets_enabled` | 폐기됨 |
| `lockscreen.passwordhistory` | |
| `lockscreen.enabledtrustagents`, `lockscreen.knowntrustagents` | 신뢰 에이전트 |
| `lockscreen.istrustusuallymanaged` | |
| `lockscreen.auto_pin_confirm` | |
| `sp-handle` | 소스 상수 CURRENT_LSKF_BASED_PROTECTOR_ID_KEY |
| `pin_enhanced_privacy` | |

비고 칸은 폐기 표시와 상수 이름 말고는 키 이름으로 짐작한 뜻이고, 비고 칸이 빈 키는 이름으로 뜻을 짐작하기 어려운 키입니다.

### 자격 증명 종류 값

LockPatternUtils 의 자격 증명 종류 상수는 다음과 같습니다 [2].

| 값 | 상수 |
|---|---|
| -1 | CREDENTIAL_TYPE_NONE |
| 1 | CREDENTIAL_TYPE_PATTERN |
| 2 | CREDENTIAL_TYPE_PASSWORD_OR_PIN (내부용 옛 통합 값) |
| 3 | CREDENTIAL_TYPE_PIN |
| 4 | CREDENTIAL_TYPE_PASSWORD |

`lockscreen.password_type` 에 들어가는 값이 이 상수인지, 기기 관리 정책(DevicePolicyManager)의 비밀번호 품질 상수인지는 단정할 수 없습니다. 그래서 이 키의 숫자를 위 표로 바로 풀지 않습니다.

### 강한 인증을 요구하는 이유

StrongAuthTracker 는 PIN·패턴·비밀번호 입력을 다시 요구하는 이유를 비트 플래그로 나타냅니다 [2]. 이 값이 파일에 남는지는 실제 기기에서 확인하고, 로그나 덤프에서 이 숫자를 만나면 다음 표로 풉니다.

| 값 | 이유 |
|---|---|
| 0x0 | 필요 없음 |
| 0x1 | 부팅 뒤 |
| 0x2 | 기기 관리자가 즉시 잠금 |
| 0x4 | 사용자 요청 |
| 0x8 | 실패를 거듭해 잠김(lockout) |
| 0x10 | 기기 관리자가 정한 시간 초과 |
| 0x20 | 사용자가 잠금 모드(lockdown)를 켬 |
| 0x80 | 약한 생체 인증만 쓴 시간이 초과 |
| 0x100 | 신뢰 에이전트 만료 |
| 0x200 | 적응형 인증 잠금 |

### 백업 대상 secure 설정

LockSettingsStorage 의 백업 대상에는 잠금 화면 소유자 정보 표시 여부와 그 문구, 패턴 표시 여부 상수(LOCK_PATTERN_VISIBLE)가 있고, `lockscreen.power_button_instantly_locks` 도 함께 들어갑니다 [1]. 이 상수들의 settings 키 문자열은 `lock_screen_owner_info_enabled`, `lock_screen_owner_info`, `lock_pattern_visible_pattern` 입니다 [4].

## 라이브 기기에서 보는 잠금 해제 흔적

`dumpsys user` 에는 사용자마다 `State: RUNNING_UNLOCKED` 와 `Unlock time: <값>` 줄이 있습니다. 이름으로 보면 사용자 저장 공간(CE 영역)이 잠금 해제된 상태와 그 시각의 단서입니다. `Unlock time` 은 부팅 뒤 흐른 시간(SystemClock.elapsedRealtime)으로 적고 출력할 때는 지금과의 차이를 "얼마 전" 모양으로 찍으며 [3], 사용자를 멈추거나 재부팅하면 0 으로 돌아갑니다. 이 값은 사용자 공간을 여는 단계(onUserUnlocking)에서만 적어서 [3], 화면 잠금을 풀 때마다 바뀌는 값으로 읽지 않습니다. 출력 전체 모양은 [사용자와 프로필 (Multi-user·users)](users-profiles.md) 페이지에 있습니다.

`dumpsys usagestats` 의 최근 이벤트에는 `KEYGUARD_HIDDEN` 이벤트가 있습니다. 이름으로 보면 잠금 화면이 사라진 때를 보여 주는 이벤트이고, 이벤트 형식과 보존 기간은 [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) 페이지에 있습니다.

## 증거로서 의미

| 기록 | 증명하는 것 | 증명하지 못하는 것 |
|---|---|---|
| `locksettings` 의 잠금 관련 행 | 확보 시점에 그 사용자에게 잠금 관련 값이 적혀 있었다는 것 | 사건 당시에도 같은 잠금이 걸려 있었는지 |
| spblob 파일이 있음 | 잠금 자격 증명과 관련된 보호 자료가 있었다는 것 | 잠금 종류, 비밀 값 |
| 신뢰 에이전트·생체 인증 키 | 그 기능이 설정되었거나 초기화되었다는 것 | 특정 시각에 그 방식으로 잠금을 풀었다는 것 |
| `KEYGUARD_HIDDEN` 이벤트 | 그 시각에 잠금 화면이 사라졌다는 것 | 누가 풀었는지, 어떤 방식(PIN·생체·신뢰 에이전트)으로 풀었는지 |
| `Unlock time` | 이번 부팅 뒤 그 사용자 공간이 잠금 해제된 때(출력 시각 기준 "얼마 전") | 그 뒤의 잠금 해제 이력, 이전 부팅의 기록 |

보고서에는 "확보 시점에 주 사용자에게 화면 잠금 관련 값이 설정되어 있었고, 이 시각에 잠금 화면이 사라진 기록이 있다" 처럼 쓰고, 잠금을 푼 사람이나 방식은 다른 근거가 있을 때만 적습니다.

## 시각 해석

`locksettings` 표의 열에는 시각이 없어서 잠금을 언제 설정했는지는 이 표로 알 수 없습니다 [1]. settings 의 `biometrics_strong_enroll_timestamp` 는 이름에 시각이 들어 있지만 단위와 기준은 같은 기기의 다른 기록과 시각을 맞춰 보고 확인합니다. usagestats 이벤트의 시각 해석은 usagestats 페이지를, 숫자를 날짜로 바꾸는 법은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../01-foundations/value-decoding/time-values.md) 페이지를 봅니다.

## 함정과 한계

잠금이 설정되어 있었다고 해서 사건 당시 기기가 잠겨 있었다는 뜻은 아닙니다. 신뢰 에이전트가 켜져 있었다면 잠금 화면이 입력 없이 넘어갔을 수 있고, `trusted_locations_count`, `db_lockscreen_is_smart_lock` 같은 키가 이와 관련돼 보이지만 값의 뜻은 단정할 수 없습니다.

자격 증명 종류 값과 `lockscreen.password_type` 값을 섞어 읽기 쉽습니다. 두 값이 같은 체계라고 단정할 수 없으니 숫자만 보고 "PIN 이었다" 고 쓰지 않습니다.

강한 인증을 요구하는 이유에 기기 관리자가 거는 잠금(0x2, 0x10)이 들어 있을 만큼 기기 관리자 앱도 잠금에 관여해서, 잠금을 건 주체가 사용자인지 앱인지는 [기기 관리자와 접근성 권한 (Device Admin·Accessibility)](../credentials-security/device-admin-accessibility.md) 페이지와 함께 봅니다. 업무 프로필이나 보안 폴더의 잠금은 주 사용자와 따로 있을 수 있어서 [보안 폴더와 작업 프로필 (Secure Folder·Work Profile)](../../01-foundations/security-model/secure-folder-work-profile.md) 페이지를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 명세로 만든 예시이고 실제 기기에서 나온 값이 아닙니다. 표 정의는 `_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, user INTEGER, value TEXT` 입니다 [1]. `name`="lockscreen.disabled", `user`=0, `value`="0" 인 행이 rowid 1 로 테이블 잎 페이지에 들어가면 셀은 다음과 같습니다.

```
19 01                                            페이로드 길이 25, rowid 1
05 00 33 08 0F                                   레코드 머리(머리 길이 5, 칸 4개의 형식)
6C 6F 63 6B 73 63 72 65 65 6E 2E 64 69 73 61 62  "lockscreen.disab"
6C 65 64                                         "led"
30                                               "0"
```

`_id` 는 INTEGER PRIMARY KEY 라서 rowid 와 같은 값이고 레코드 안에는 NULL(`00`)로 적힙니다. `33`(51)은 19바이트 문자열, `08` 은 정수 0 이라 본문에 바이트가 없고, `0F`(15)는 1바이트 문자열입니다. 확보한 파일에서도 먼저 `sqlite_master` 에서 표 정의를 확인합니다. 형식 번호를 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md) 페이지에 있습니다.

### 공개 도구로 한 번

사본을 `sqlite3` 로 열어 표 정의와 키 목록을 봅니다. 비밀 값과 관련된 키는 값을 보고서에 옮기지 않고 행이 있는지만 적습니다.

```sql
SELECT sql FROM sqlite_master WHERE name = 'locksettings';
SELECT name, user, value FROM locksettings
WHERE name NOT IN ('lockscreen.password_salt', 'lockscreen.passwordhistory')
ORDER BY user, name;
```

라이브 기기에서는 settings 와 dumpsys 에서 잠금 관련 줄을 추립니다.

```sh
adb shell settings list secure | grep -iE 'lock|trust|biometric|screen_lock'
adb shell dumpsys user | grep -E 'UserInfo|State:|Unlock time:'
adb shell dumpsys usagestats | grep -E 'KEYGUARD_'
```

## 교차 검증

잠금 해제 시각은 [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) 의 화면 켜짐·앱 전환 이벤트와 [폰 사용 시간 재구성 (Usage Time)](../../04-scenarios/activity/usage-time.md) 시나리오로 이어 봅니다. 공장 초기화 뒤 다시 설정한 기기인지는 [초기화 흔적 (Factory Reset)](factory-reset.md) 을, 사용자·프로필 구성은 [사용자와 프로필 (Multi-user·users)](users-profiles.md) 을 봅니다.

## 실습

공개된 안드로이드 시험 자료(NIST CFReDS 에 올라온 모바일 이미지 등)를 구해 다음을 풀어 봅니다.

1. `locksettings.db` 를 찾아 표 정의를 적고, 열이 `name`·`user`·`value` 말고 더 있는지 확인합니다.
2. 사용자 번호별로 어떤 키가 있는지 표로 만들고, 비밀 값과 관련된 키는 값 대신 "있음" 으로 적습니다.
3. `lockscreen.password_type` 값이 무엇인지 적고, 이미지 설명서에 적힌 잠금 방식과 비교해 어느 상수 체계와 맞는지 확인해 봅니다.
4. 사용자별 폴더에 `spblob` 폴더가 있는지, 파일 이름이 어떤 모양인지 봅니다.

## 참고 문헌

1. LockSettingsStorage.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/locksettings/LockSettingsStorage.java
2. LockPatternUtils.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/com/android/internal/widget/LockPatternUtils.java
3. UserManagerService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/UserManagerService.java
4. Settings.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/provider/Settings.java
