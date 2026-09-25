---
title: "계정 탈취 흔적"
parent: "시나리오 · 침해 사고"
nav_order: 1780
---

# 계정 탈취 흔적 (Account Takeover)

## 조사 질문

"이 폰에서 계정이 언제 추가되거나 지워졌나", "비밀번호가 지워지거나 바뀐 기록이 있나", "어느 앱이 계정 추가나 삭제를 요청했나" 같은 질문에 답하는 흐름입니다. 이 페이지는 기기의 계정 관리자(AccountManager)가 남기는 기록을 중심으로 보고, 가짜 페이지에 계정 정보를 넣게 된 앞 단계는 [스미싱 흔적](smishing.md) 에서, 자동 완성이나 입력 방법을 가로챈 앱이 의심되면 [몰래 설치된 감시 앱](stalkerware.md) 에서 봅니다.

기기 기록은 계정이 기기에 추가되고 지워진 때와 그 일을 요청한 UID 까지 알려 주지만, 서비스 서버에서 누가 로그인했는지나 다른 기기에서 무슨 일이 있었는지는 알려 주지 않습니다. Google 계정의 최근 보안 활동이나 삼성 계정 로그인 기록 같은 서버 쪽 기록은 이번 조사에서 확인하지 못했고, 확보 방법은 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 에서 봅니다.

## 먼저 확인할 것

- **OS 버전** — 현행 AOSP 는 계정 데이터베이스를 `accounts_ce.db`(CE)와 `accounts_de.db`(DE) 두 개로 나누고, Android 7(N)보다 앞선 버전은 `accounts.db` 하나를 썼습니다(소스의 `PreNDatabaseHelper`) [1]. 두 파일의 전체 경로는 이번 조사에서 확인하지 못했으니 [계정](../../02-artifacts/system-account/accounts/index.md) 페이지 기준으로 찾고, CE 와 DE 영역의 차이는 [저장 공간 암호화](../../01-foundations/storage/encryption/index.md) 에서 봅니다.
- **시간대와 시각 형식** — 계정 변경 기록의 `time` 칸은 DATETIME 으로 선언되어 있지만, 들어가는 값의 형식은 AccountsDb 소스에 없습니다 [1]. 관찰 기기의 `dumpsys account` 는 이 시각을 숫자가 아니라 한글이 섞인 날짜 문자열 뒤에 시:분:초를 붙인 모양으로 찍었고 (확인 범위: SM-S937N, Android 16, One UI 8.5), 어느 시간대로 표시했는지는 확인하지 못했습니다. 기기 시간대는 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md) 에서 확인합니다.
- **사용자와 프로필** — 관찰 기기의 `dumpsys account` 는 `User UserInfo{...}` 줄로 사용자를 나눈 뒤 그 아래에 계정 목록을 찍었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 보안 폴더나 작업 프로필이 있으면 사용자마다 따로 봅니다([사용자와 프로필](../../02-artifacts/system-account/users-profiles.md)).
- **수집 범위** — 계정 변경 기록은 최대 64행만 남습니다 [1]. 사고가 오래전이면 그 사이 다른 계정 변경이 쌓여 기록이 밀려났을 수 있으니, 기기를 넘겨받으면 계정을 더 추가하거나 지우지 않은 채 먼저 확보합니다. 확보 방식은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 정합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `dumpsys account` 의 계정 목록 | 사용자별로 지금 기기에 있는 계정의 이름과 종류 | [계정](../../02-artifacts/system-account/accounts/index.md) |
| 2 | DE 의 `accounts` 표 | 계정 이름·종류, 이전 이름, 마지막 비밀번호 입력 시각 | [계정](../../02-artifacts/system-account/accounts/index.md) |
| 3 | DE 의 `debug_table` (계정 변경 기록) | 계정 추가·삭제·비밀번호 변경과 그 요청, 시각, 부른 UID | [계정](../../02-artifacts/system-account/accounts/index.md) |
| 4 | DE 의 `grants`·`visibility` 표 | 계정 ID 와 UID·패키지를 잇는 행 | [계정](../../02-artifacts/system-account/accounts/index.md) |
| 5 | CE 의 `authtokens`·`extras` 표 | 계정별로 저장된 인증 토큰과 추가 값 | [계정](../../02-artifacts/system-account/accounts/index.md) |
| 6 | 계정·잠금 관련 설정 키 | 관련 설정이 있는지 | [설정 값](../../02-artifacts/system-account/settings.md) |
| 7 | 저장된 암호 | 기기에 저장된 로그인 정보 | [저장된 암호](../../02-artifacts/credentials-security/saved-passwords.md) |

## 분석 흐름

1. **지금 있는 계정을 적습니다.** 관찰 기기의 `dumpsys account` 는 사용자 줄 아래 `Accounts: ##` 머리줄을 찍고, 계정마다 `Account {name=..., type=...}` 줄을 찍었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). DE 의 `accounts` 표에는 `_id`, `name`, `type`, `previous_name`, `last_password_entry_time_millis_epoch` 칸이 있고 [1], 마지막 칸은 기본값 0 인 INTEGER 이며 이름대로라면 유닉스 밀리초입니다. 모르는 계정이 있거나 `previous_name` 에 값이 있으면 다음 단계에서 그 계정의 `_id` 로 기록을 찾습니다.

2. **계정 변경 기록을 읽습니다.** `debug_table` 에는 `_id`(계정 ID), `action_type`(TEXT), `time`(DATETIME), `caller_uid`(INTEGER), `table_name`(TEXT), `primary_key`(INTEGER PRIMARY KEY) 칸이 있고 `time` 에 인덱스가 걸려 있습니다 [1]. `dumpsys account` 는 이 표를 "AccountId, Action_Type, timestamp, UID, TableName, Key" 머리줄과 "Accounts History" 줄 아래에 한 줄에 쉼표로 여섯 칸씩, `time` 순서로 찍습니다 [1]. 관찰 기기에서 본 줄은 아래 모양이었고, 값은 가려져 있습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5).

   ```
   AccountId, Action_Type, timestamp, UID, TableName, Key
   Accounts History
   ##,action_account_add,<<한글>>:##:##,#####,accounts,##
   ##,action_called_account_remove,<<한글>>:##:##,#####,accounts,##
   -#,action_called_account_add,<<한글>>:##:##,#####,accounts,##
   ```

3. **실제 변경과 요청을 나눕니다.** `action_type` 은 두 무리로 나뉩니다 [1].

   | 무리 | 값 | 소스 설명 |
   |---|---|---|
   | 실제 변경 | `action_set_password`, `action_clear_password`, `action_account_add`, `action_account_remove`, `action_account_remove_de`, `action_authenticator_remove`, `action_account_rename` | 인증기(authenticator)가 부르는 동작이라서 UID 는 인증기의 것입니다 |
   | 요청 | `action_called_account_add`, `action_called_account_remove`, `action_sync_de_ce_accounts`, `action_called_start_account_add`, `action_called_account_session_finish` | 인증에 실패해 계정이 들어가지 않아도 누가 불렀는지 남깁니다 |

   관찰 기기의 기록 줄에서는 `action_called_account_remove`, `action_account_remove`, `action_account_add`, `action_authenticator_remove`, `action_called_account_add`, `action_clear_password` 가 보였습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 요청 줄 바로 뒤에 같은 계정의 실제 변경 줄이 있으면 요청이 이루어진 것이고, 요청 줄만 있으면 요청은 있었지만 실제 변경 기록은 없는 것으로 적습니다. 관찰 기기에서는 `action_called_account_add` 줄의 첫 칸이 `-#` 처럼 음수로 찍혔는데 (확인 범위: SM-S937N, Android 16, One UI 8.5), 계정이 아직 만들어지기 전의 값으로 보이지만 확인하지는 못했습니다.

4. **부른 쪽을 앱으로 풉니다.** `caller_uid` 를 패키지 이름으로 바꾸는 법은 [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md) 에 있습니다. 요청 줄의 UID 는 계정 추가나 삭제를 부른 앱이고, 실제 변경 줄의 UID 는 인증기라는 점을 나눠 적습니다 [1]. 요청한 앱이 기본 제공 앱이 아니면 그 앱이 들어온 경로를 [악성 앱은 어디서 들어왔나](initial-access.md) 에서 이어 봅니다.

5. **기록이 밀려났는지 따집니다.** `debug_table` 은 최대 64행(`MAX_DEBUG_DB_SIZE = 64`)이고, 64행이 차면 `time` 이 가장 오래된 행을, 같으면 `primary_key` 가 작은 행을 `INSERT OR REPLACE` 로 덮어씁니다 [1]. 관찰 기기의 요약에 적힌 기록 줄 수를 모두 더하면 64로 이 한도와 맞았습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 다만 "Accounts History" 머리줄이 두 번 나와서 한 표를 두 번 찍은 것인지 두 표인지는 확인하지 못했습니다. 기록이 64행으로 꽉 차 있으면 가장 오래된 줄의 시각보다 앞선 일은 이 표에서 확인할 수 없다고 적습니다.

6. **접근 허락과 토큰을 봅니다.** DE 의 `grants` 표에는 `accounts_id`, `auth_token_type`, `uid` 칸이, `visibility` 표에는 `accounts_id`, `_package`, `value` 칸이 있습니다 [1]. 칸 이름으로 보아 앞은 계정별로 어느 UID 에 어떤 토큰 종류를 허락했는지, 뒤는 패키지별로 계정을 보여 줄지를 담는 표로 보이지만 이번 조사에서 뜻을 확인하지는 않았습니다. CE 의 `authtokens` 표에는 `_id`, `accounts_id`, `type`, `authtoken` 이, `extras` 표에는 `_id`, `accounts_id`, `key`, `value` 가 있습니다 [1]. 이 표에 모르는 UID 나 패키지가 있으면 그 앱을 4단계처럼 풀어 봅니다. CE 의 `accounts` 행을 지우면 트리거가 그 계정의 `authtokens` 와 `extras` 행도 지웁니다 [1].

7. **관련 설정 키를 적어 둡니다.** 관찰 기기의 settings global 키 목록에는 `secure_frp_mode`, `device_provisioned`, `synced_account_name`, `first_launch_samsung_account_menu` 가, secure 쪽에는 `remote_lock_setting`, `biometrics_strong_enroll_timestamp`, `lock_screen_lock_after_timeout`, `credential_service_primary` 가 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 키 이름만 확인했고 뜻은 이름으로 짐작할 뿐이라서, 값을 읽더라도 "이 키가 이 값이었다" 까지만 적습니다. 자동 완성과 자격 증명 서비스 키는 [몰래 설치된 감시 앱](stalkerware.md) 에서, 잠금 설정은 [잠금 화면 설정](../../02-artifacts/system-account/lock-settings.md) 에서 봅니다.

8. **서버 쪽 기록과 맞춥니다.** 기기 기록에서 세운 추가·삭제 시각을 서비스 쪽 로그인 기록과 나란히 놓으면 다른 기기에서 먼저 로그인한 뒤 이 기기의 계정이 지워졌는지 같은 순서를 따질 수 있습니다. 서버 기록을 받는 법은 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 에, 한 시간 축에 놓는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

> 그림 자리: `debug_table` 한 줄을 여섯 칸으로 나눠 "계정 ID → accounts 표의 _id", "UID → 패키지 이름" 으로 화살표를 잇고, 요청 줄과 실제 변경 줄을 다른 색으로 구분한 그림

## 흔한 오판

**`action_called_*` 줄을 실제 변경으로 읽는 오판**이 흔합니다. 요청 줄은 인증에 실패해 계정이 들어가지 않아도 남습니다 [1].

**실제 변경 줄의 UID 를 변경을 일으킨 앱으로 적는 실수**도 있습니다. 소스 주석대로 이 UID 는 인증기의 것이라서 [1], 누가 요청했는지는 앞선 요청 줄에서 찾습니다.

**기록에 없으니 그 전에는 계정 변경이 없었다고 보는 것**은 근거가 없습니다. 64행이 차면 가장 오래된 행부터 덮어써서 [1] 오래된 일은 남지 않습니다.

**토큰 행이 없으니 토큰을 쓴 적이 없다고 보는 것**도 지나칩니다. 계정을 지우면 트리거가 그 계정의 토큰 행도 함께 지웁니다 [1].

**`dumpsys account` 의 시각 문자열을 그대로 옮기는 경우**에도 주의합니다. 관찰 기기에서는 날짜 문자열로 찍혔고 시간대 표시는 확인하지 못했습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). DB 파일을 확보했다면 `time` 칸의 원래 값과 대조해 적습니다.

## 보고서 문장 예

| 쓰지 않을 문장 | 쓸 문장 |
|---|---|
| 해커가 피해자의 계정을 탈취해 폰에서 지웠다. | 계정 변경 기록(`debug_table`)에 ○○일 ○○:○○ UID ○○(패키지 ○○)의 계정 삭제 요청(`action_called_account_remove`)과 이어진 계정 삭제(`action_account_remove`)가 있습니다. 이 기록은 기기 안의 계정 변경을 보여 주며, 서비스 서버에서 누가 로그인했는지는 담지 않습니다. |
| 악성 앱이 계정 비밀번호를 바꿨다. | 같은 기록에 ○○일 ○○:○○ 계정 ID ○○의 비밀번호 지움(`action_clear_password`)이 있고, 이 줄의 UID ○○는 인증기의 UID 입니다. |
| 그 전에는 계정에 아무 일도 없었다. | 계정 변경 기록은 최대 64행만 남고, 확보한 기록의 가장 오래된 줄은 ○○일 ○○:○○입니다. 그 전의 변경은 이 기록으로 확인할 수 없습니다. |

보고서 전체의 틀은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 아티팩트 본문: [계정 (Accounts)](../../02-artifacts/system-account/accounts/index.md), [저장된 암호](../../02-artifacts/credentials-security/saved-passwords.md), [잠금 화면 설정](../../02-artifacts/system-account/lock-settings.md), [설정 값](../../02-artifacts/system-account/settings.md), [dumpsys 출력](../../02-artifacts/logs/dumpsys.md)
- 기반 구조: [저장 공간 암호화](../../01-foundations/storage/encryption/index.md), [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md)
- 이어지는 시나리오: [스미싱 흔적](smishing.md), [몰래 설치된 감시 앱](stalkerware.md), [악성 앱은 어디서 들어왔나](initial-access.md)
- 기법: [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md), [타임라인 작성](../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. AccountsDb.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/accounts/AccountsDb.java
