---
title: "계정 DB 구조"
parent: "계정"
grand_parent: "아티팩트 · 시스템·계정"
nav_order: 330
---

# 계정 DB 구조 (accounts_ce.db·accounts_de.db)

기기에 등록된 계정 목록을 담는 SQLite 파일 두 개의 위치와 표, 시각, 변경 기록을 정리합니다. 소스로 확인한 값은 현행 AOSP 기준(frameworks/base 의 main 가지)이고, 어느 Android 출시 버전에서 바뀌었는지는 대부분 확인하지 못했습니다. 실제 폰에서 본 모양에는 확인 범위를 붙였습니다.

## 한 줄 요약

시스템 서비스 AccountManagerService 가 사용자마다 계정의 이름·종류·권한 부여·가시성을 `accounts_de.db` 에, 비밀번호·인증 토큰·부가 값을 `accounts_ce.db` 에 나눠 적고, DE 쪽 `debug_table` 에는 최대 64줄의 계정 변경 기록을 남깁니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

앱이 AccountManager API 로 계정을 등록하면 시스템 서비스 AccountManagerService 가 그 계정을 관리하고, AccountsDb 가 SQLite 파일 두 개에 나눠 씁니다 [1][2]. 계정은 이름(name)과 종류(type)의 쌍으로 구분하는데, 이름은 보통 이메일 주소이고 type 은 그 계정을 관리하는 인증기(authenticator)를 가리킵니다 [5]. 그래서 구글·삼성 계정만이 아니라 여러 앱이 등록한 계정이 같은 표에 함께 남습니다.

두 파일은 암호화 영역이 다릅니다. CE(Credential Encrypted) 파일에는 비밀번호와 인증 토큰 같은 민감한 값이 들어가고, DE(Device Encrypted) 파일에는 이름·종류·권한 부여·가시성 같은 메타데이터가 들어갑니다 [1]. DE 파일은 잠금 해제 전에도 열리지만 CE 파일은 사용자가 잠금을 푼 뒤에야 서비스가 DE 연결에 붙입니다(ATTACH). 소스에는 이때 `User <id> is unlocked - opening CE database` 라는 로그 문구가 있습니다 [1][2]. CE·DE 영역 자체의 구조는 [저장 공간 암호화 (Encryption)](../../../01-foundations/storage/encryption/index.md) 페이지에 있습니다.

## 위치와 버전별 차이

| 파일 | 흔한 전체 경로 | DB 버전(현행 AOSP) |
|---|---|---|
| `accounts_de.db` | `/data/system_de/<사용자ID>/accounts_de.db` | 3 |
| `accounts_ce.db` | `/data/system_ce/<사용자ID>/accounts_ce.db` | 10 |
| `accounts.db` | 확인하지 못함 | 9 (Android N 이전 구조) |

파일 이름과 버전 값은 AccountsDb 의 상수(CE_DATABASE_NAME, DE_DATABASE_NAME, PRE_N_DATABASE_NAME 등)에서 확인했습니다 [1]. 전체 경로는 ALEAPP 가 찾는 패턴 `*/system_de/*/accounts_de.db*`, `*/system_ce/*/accounts_ce.db*` 에서 읽어 냈고, AOSP 에서 경로를 조립하는 코드는 가져온 파일이 잘려 직접 보지 못했습니다 [3][4]. 패턴 가운데의 `*` 는 사용자 번호 폴더이고 끝의 `*` 로 `-wal`·`-journal` 같은 딸림 파일까지 함께 잡습니다 [3][4]. 사용자 번호 폴더마다 파일이 따로 있어서 다른 사용자나 프로필의 계정은 그 번호의 폴더에서 찾고, 사용자 구성은 [사용자와 프로필 (Multi-user·users)](../users-profiles.md) 페이지에서 확인합니다.

Android N 이전에는 `accounts.db` 한 파일에 모두 담았습니다 [1]. 두 파일로 나뉜 정확한 시점은 상수 이름(PRE_N)으로 짐작할 뿐 문서로 확인하지 못했고, 예전 파일의 경로도 확인하지 못했습니다.

## 구조

### accounts_de.db

| 표 | 칸 | 담긴 것 |
|---|---|---|
| `accounts` | `_id` INTEGER PRIMARY KEY, `name` TEXT NOT NULL, `type` TEXT NOT NULL, `previous_name` TEXT, `last_password_entry_time_millis_epoch` INTEGER DEFAULT 0, UNIQUE(name, type) | 계정 목록과 이름을 바꾸기 전의 이름 |
| `grants` | `accounts_id` INTEGER NOT NULL, `auth_token_type` STRING NOT NULL, `uid` INTEGER NOT NULL, UNIQUE(accounts_id, auth_token_type, uid) | 어떤 앱(uid)에 어떤 토큰 종류를 쓰도록 허락했는지 |
| `visibility` | `accounts_id` INTEGER NOT NULL, `_package` TEXT NOT NULL, `value` INTEGER, PRIMARY KEY(accounts_id, _package) | 앱(패키지)별로 이 계정을 보여 주는지 |
| `shared_accounts` | `_id` INTEGER PRIMARY KEY AUTOINCREMENT, `name` TEXT NOT NULL, `type` TEXT NOT NULL, UNIQUE(name, type) | 용도는 이번에 확인하지 못함 |
| `meta` | `key` TEXT PRIMARY KEY NOT NULL, `value` TEXT | 키·값 |
| `debug_table` | `_id` INTEGER, `action_type` TEXT NOT NULL, `time` DATETIME, `caller_uid` INTEGER NOT NULL, `table_name` TEXT NOT NULL, `primary_key` INTEGER PRIMARY KEY | 계정 변경 기록 |

위 칸 정의는 모두 현행 AOSP 의 AccountsDb 에서 가져왔습니다 [1]. `previous_name` 칸은 계정 이름을 바꾸기 전의 이름을 돌려주는 API getPreviousName() 과 짝을 이룹니다 [1][5]. API 26(Android 8.0)부터 getAccounts() 는 호출한 앱에 보이도록 설정된 계정만 돌려주고, 그 설정이 `visibility` 표에 들어갑니다 [5]. `visibility.value` 의 숫자가 각각 무슨 뜻인지는 이번 자료로 확인하지 못해서 보고서에서 숫자의 뜻을 풀어 쓰지 않습니다.

### accounts_ce.db

| 표 | 칸 | 담긴 것 |
|---|---|---|
| `accounts` | `_id` INTEGER PRIMARY KEY AUTOINCREMENT, `name` TEXT NOT NULL, `type` TEXT NOT NULL, `password` TEXT, UNIQUE(name, type) | 계정과 비밀번호 칸 |
| `authtokens` | `_id` INTEGER PRIMARY KEY AUTOINCREMENT, `accounts_id` INTEGER NOT NULL, `type` TEXT NOT NULL, `authtoken` TEXT, UNIQUE(accounts_id, type) | 계정별 인증 토큰 |
| `extras` | `_id` INTEGER PRIMARY KEY AUTOINCREMENT, `accounts_id` INTEGER, `key` TEXT NOT NULL, `value` TEXT, UNIQUE(accounts_id, key) | 인증기가 계정에 붙여 둔 키·값(사용자 데이터) |

`extras` 의 키 이름은 인증기(앱)마다 달라서 공통 목록이 없고, 이번에 구체적인 키도 확인하지 못했습니다 [1]. `password` 와 `authtoken` 칸은 비밀 값이라 보고서에는 값을 옮기지 않고 칸이 비었는지 차 있는지만 적습니다.

### debug_table 의 action_type

현행 AOSP 에 정의된 값은 다음 12가지입니다 [1].

```
action_set_password            action_clear_password
action_account_add             action_account_remove
action_account_remove_de       action_authenticator_remove
action_account_rename          action_called_account_add
action_called_account_remove   action_sync_de_ce_accounts
action_called_start_account_add
action_called_account_session_finish
```

이름으로 보면 `action_called_*` 는 앱이 API 를 부른 사실이고 `action_account_*` 는 표가 실제로 바뀐 사실로 나뉘는 듯하지만, 상수 이름에 기댄 해석이라 확인하지 못했습니다. `_id` 칸은 계정 번호이고(ALEAPP 가 `accounts._id` 와 묶는 칸), `caller_uid` 는 동작을 부른 쪽의 UID 라서 [패키지 이름과 UID (Package Name·UID)](../../../01-foundations/value-decoding/package-uid.md) 페이지의 방법으로 앱에 대응시킵니다 [1][3].

상수 MAX_DEBUG_DB_SIZE 는 64이고, 새 줄을 쓸 자리를 정하는 reserveDebugDbInsertionPoint 가 쓸 위치를 하나씩 올리다가 64로 나눈 나머지로 되돌아가서 `primary_key` 0~63 자리를 돌아가며 덮어씁니다 [1]. 그래서 `primary_key` 순서는 기록 순서와 다를 수 있고, 줄을 시간 순으로 늘어놓을 때는 `time` 칸으로 정렬합니다. DE 쪽 도우미(DeDatabaseHelper)가 이 표를 만들 때 `time` 칸에 색인(timestamp_index)도 함께 만듭니다 [1].

### CE 와 DE 맞추기

잠금 해제 때 CE 를 붙인 다음 syncDeCeAccountsLocked 가 돌아서, DE 에는 없고 CE 에만 남은 계정(findCeAccountsNotInDe)을 CE 표에서 지웁니다. 이때 소스에는 `<n> accounts were previously deleted while user <id> was locked. Removing accounts from CE tables` 라는 로그 문구가 있습니다 [2]. 그래서 잠긴 상태에서 계정을 지우면 DE 에서 먼저 사라지고 CE 는 다음 잠금 해제 때 정리됩니다. 이 정리가 `action_sync_de_ce_accounts` 줄로 남는지는 상수만 확인했고 기록하는 위치는 확인하지 못했습니다 [1][2].

## 라이브 기기에서 본 모양 (dumpsys account)

adb 일반 셸 권한으로 `dumpsys account` 를 실행하면 사용자별 계정 목록과 "Accounts History" 가 나옵니다. 출력은 415줄이었고 모양은 다음과 같습니다(값은 가려져 있고, 대표 줄만 옮겼습니다). (확인 범위: SM-S937N, Android 16, One UI 8.5)

```
User UserInfo{#:<이름>:#c##}:
  Accounts: ##
    Account {name=<이름>, type=<종류>}
  AccountId, Action_Type, timestamp, UID, TableName, Key
  Accounts History
  ##,action_account_add,<날짜> ##:##:##,#####,accounts,##
  ##,action_account_remove,<날짜> ##:##:##,####,accounts,##
  -#,action_called_account_add,<날짜> ##:##:##,#####,accounts,##
  Active Sessions: <값>
  RegisteredServicesCache: <값>
    ServiceInfo: <값>
```

History 머리줄의 순서는 `debug_table` 의 `_id, action_type, time, caller_uid, table_name, primary_key` 와 맞습니다. 이 기기에서 나온 action 은 `action_account_add`, `action_account_remove`, `action_called_account_add`, `action_called_account_remove`, `action_authenticator_remove`, `action_clear_password` 였고, TableName 은 모두 `accounts` 였고, `action_called_account_add` 줄만 AccountId 가 음수였습니다. History 줄을 모두 더하면 64줄이라 MAX_DEBUG_DB_SIZE 와 같았고, "Accounts History" 와 머리줄이 두 번 나온 까닭(사용자별인지 DB 별인지)은 확인하지 못했습니다. (확인 범위: SM-S937N, Android 16, One UI 8.5)

계정 줄은 19개였고, type 이 패키지 이름 모양인 줄과 그렇지 않은 줄이 섞여 있었습니다. 계정 이름 뒤에 괄호로 소속(회사명)이 붙은 줄도 하나 있었는데, 어느 앱의 표기인지와 DB 의 `name` 칸에도 같은 모양으로 들어가는지는 확인하지 못했습니다. (확인 범위: SM-S937N, Android 16, One UI 8.5) dumpsys 를 뽑는 방법은 [dumpsys 출력 (dumpsys)](../../logs/dumpsys.md) 페이지에 있습니다. 루팅하지 않은 기기에서 adb 일반 권한으로 DB 파일 자체를 읽을 수 있는지는 확인하지 못했습니다.

## 증거로서 의미

| 기록 | 증명하는 것 | 증명하지 못하는 것 |
|---|---|---|
| DE·CE 의 `accounts` 행 | 파일을 확보한 시점에 그 사용자 공간에 이 name·type 쌍의 계정이 등록되어 있었다는 것 | 계정을 언제 추가했는지(추가 시각 칸이 없음), 계정 주인이 기기 사용자인지 |
| `previous_name` | 이름을 바꾼 적이 있고 바꾸기 전 이름이 무엇이었는지 | 언제 바꿨는지 |
| `grants`·`visibility` | 어떤 앱에 토큰 사용 허락이나 계정 보이기 설정이 있었다는 것 | 그 앱이 토큰으로 무엇을 했는지 |
| `debug_table` 줄 | 남아 있는 범위 안에서 어느 시각에 어느 UID 가 계정 추가·삭제 같은 동작을 했다는 것 | 64줄보다 오래된 일, 사람이 직접 조작했는지 |
| CE `authtokens` 행 | 그 종류의 토큰이 저장되어 있었다는 것 | 그 서비스에 실제로 접속했다는 것 |

보고서에는 "이 기기의 주 사용자 계정 DB 에 이 이름과 종류의 계정이 등록되어 있었고, 변경 기록에는 이 시각에 이 UID 의 계정 추가 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

`accounts.last_password_entry_time_millis_epoch` 는 이름대로 유닉스 에포크 밀리초이고, ALEAPP 도 유닉스 밀리초를 UTC 로 바꿔 보여 줍니다 [1][3]. 기본값이 0이라서 0이면 값이 한 번도 채워지지 않은 상태이고, 어떤 동작 때 이 값을 새로 쓰는지는 소스로 확인하지 못했습니다. 숫자를 날짜로 바꾸는 법은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

`debug_table.time` 은 칸 형식이 DATETIME 이고 AccountManagerService 에 `SimpleDateFormat("yyyy-MM-dd HH:mm:ss")` 가 있어서 사람이 읽는 문자열로 들어갑니다 [1][2]. 받은 소스 부분에는 이 형식에 시간대를 따로 주는 코드가 없었고, 자바 기본 동작대로라면 기기의 기본 시간대(현지 시각)가 됩니다. 기록을 쓰는 함수 본문은 직접 보지 못해서 현지 시각인지 UTC 인지는 확인하지 못했습니다. ALEAPP 는 이 문자열을 사람이 읽는 형식에서 UTC 로 바꿔 보여 주는데 [3], 문자열이 현지 시각이라면 시간대 차이만큼 어긋날 수 있으니 [시간대와 시각 설정 (Time Zone)](../time-zone.md) 과 다른 기록의 시각을 맞춰 보고 정합니다. dumpsys 의 History 줄도 시각이 `<날짜> ##:##:##` 모양으로 초 단위까지만 있고 밀리초는 없었습니다. (확인 범위: SM-S937N, Android 16, One UI 8.5)

## 함정과 한계

ALEAPP 의 Accounts_de 모듈은 `accounts` 와 `debug_table` 을 `accounts._id = debug_table._id` 로 묶어(INNER JOIN) 계정별 기록을 시각 순으로 뽑습니다 [3]. 계정을 지우면 `accounts` 행이 사라져서 이렇게 묶으면 지워진 계정의 기록이 결과에서 빠지니, 삭제를 찾을 때는 `debug_table` 을 통째로 따로 봅니다.

CE 에만 있고 DE 에는 없는 계정은 잠긴 상태에서 지워진 뒤 아직 정리되지 않은 계정일 수 있습니다. 반대로 DE 만 확보하면 비밀번호·토큰 칸은 볼 수 없고, CE 는 잠금 해제 뒤에만 열리는 영역이라 확보 상태에 따라 아예 없을 수 있습니다. 확보 방식에 따른 차이는 [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지를 봅니다.

`debug_table` 은 최대 64줄이라 계정을 오래전에 추가했다면 추가 기록이 남아 있지 않을 수 있고, 추가 기록이 없다고 해서 계정이 원래부터 있었다고 말할 수도 없습니다. 지운 행이 SQLite 빈 공간이나 WAL 에 남는지는 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) 와 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md) 페이지의 방법으로 따로 확인하고, 그래서 `-wal`·`-journal` 파일도 함께 확보합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 명세로 만든 예시이고 실제 기기에서 나온 값이 아닙니다. DE 의 `accounts` 표에 `_id`=1, `name`="user@example.com", `type`="com.example", `previous_name` 없음, `last_password_entry_time_millis_epoch`=0 인 행이 테이블 잎 페이지의 셀로 들어가면 다음과 같습니다.

```
21 01                                      페이로드 길이 33, rowid 1
06 00 2D 23 00 08                          레코드 머리(머리 길이 6, 칸 5개의 형식)
75 73 65 72 40 65 78 61 6D 70 6C 65 2E 63 6F 6D   "user@example.com"
63 6F 6D 2E 65 78 61 6D 70 6C 65                  "com.example"
```

`_id` 는 INTEGER PRIMARY KEY 라서 값이 rowid 로 들어가고 레코드 안에는 NULL(형식 0)로 적힙니다. `2D`(45)는 16바이트 문자열, `23`(35)은 11바이트 문자열이고, `previous_name` 은 NULL(0), 기본값 0 은 정수 0을 뜻하는 형식 8이라 본문에 바이트가 없습니다. 형식 번호를 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) 페이지에 있습니다.

### 공개 도구로 한 번

사본을 `sqlite3` 로 열어 다음처럼 봅니다. CE 쪽은 비밀 값 칸을 빼고 뽑습니다.

```sql
-- accounts_de.db
SELECT _id, name, type, previous_name, last_password_entry_time_millis_epoch FROM accounts;
SELECT primary_key, _id, action_type, time, caller_uid, table_name FROM debug_table ORDER BY time;
SELECT accounts_id, _package, value FROM visibility;
SELECT accounts_id, auth_token_type, uid FROM grants;

-- accounts_ce.db
SELECT a._id, a.type, a.name, t.type AS token_type
FROM accounts a JOIN authtokens t ON a._id = t.accounts_id;
```

ALEAPP 에는 Accounts_de, Accounts_ce, Authentication tokens 모듈이 있습니다 [3][4]. Accounts_ce 는 `SELECT type, name, password FROM accounts` 를 쓰고, Authentication tokens 는 `accounts` 와 `authtokens` 를 `accounts._id = authtokens.accounts_id` 로 묶어 토큰 값까지 뽑으니 결과를 보고서에 붙일 때 비밀 값 칸을 가립니다 [4].

## 교차 검증

계정별로 무엇을 더 볼지는 [구글 계정 흔적 (Google Account)](google-account.md) 과 [삼성 계정 흔적 (Samsung Account)](samsung-account.md) 에 있고, 계정별 동기화 설정 파일도 구글 계정 페이지에서 다룹니다. `action_authenticator_remove` 처럼 인증기 앱이 사라진 기록은 [설치된 앱 (packages.xml)](../../app-usage/packages/index.md) 의 설치·삭제 흔적과 맞춰 보고, `caller_uid` 도 같은 곳에서 패키지로 바꿉니다. 계정 추가·삭제 시각은 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) 에 넣어 앱 사용 기록과 나란히 봅니다.

## 실습

공개 안드로이드 검체(NIST CFReDS 에 올라온 모바일 이미지 등)를 구해 다음을 풀어 봅니다.

1. 사용자 번호 폴더마다 `accounts_de.db` 가 있는지 찾고, 각 파일의 계정 type 을 모두 적어 봅니다.
2. `debug_table` 의 줄 수를 세고 64줄을 채웠는지 확인한 다음, 가장 오래된 줄의 시각이 어디까지 내려가는지 봅니다.
3. `debug_table` 을 통째로 뽑은 결과와 ALEAPP 의 Accounts_de 결과를 비교해, JOIN 때문에 빠진 줄(지운 계정)이 있는지 찾습니다.
4. CE 가 있다면 CE 와 DE 의 `accounts` 행을 비교해 한쪽에만 있는 계정이 있는지 확인합니다.
5. `debug_table.time` 을 같은 시간대의 다른 기록과 맞춰 보고, 이 검체에서 현지 시각으로 적혔는지 판단해 봅니다.

## 참고 문헌

1. AccountsDb.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/accounts/AccountsDb.java
2. AccountManagerService.java — AOSP frameworks/base (GitHub 미러, main, 일부만 읽음), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/accounts/AccountManagerService.java
3. ALEAPP accounts_de.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/accounts_de.py
4. ALEAPP accounts_ce.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/accounts_ce.py
5. AccountManager — Android Developers API 참조, https://developer.android.com/reference/android/accounts/AccountManager
