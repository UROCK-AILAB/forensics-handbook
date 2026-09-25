---
title: "구글 플레이 기록"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 540
---

# 구글 플레이 기록 (Play Store)

## 한 줄 요약

Play 스토어 앱(com.android.vending)이 자기 데이터 폴더에 만드는 SQLite DB 세 개에는 스토어가 앱을 처음 받은 시각과 마지막 업데이트 시각, 계정별 소유 기록, 업데이트한 APK 경로가 남아서, 앱이 어떤 경로로 언제 들어왔는지 볼 때 시스템 쪽 설치 기록과 맞춰 보는 자료가 됩니다.

## 무엇을 기록하나 · 왜 생기나

Play 스토어 앱의 패키지 이름은 com.android.vending 이고, 이 앱은 설치·업데이트를 처리하면서 자기 폴더의 databases 아래에 상태를 적어 둡니다. 공개 도구 ALEAPP 가 읽는 파일은 아래 세 개입니다. [1][2][3]

| DB 파일 | 표 | ALEAPP 가 읽는 내용 |
|---|---|---|
| `localappstate.db` | `appstate` | 앱별 설치·업데이트 상태: 처음 받은 시각, 마지막 업데이트 시각, 설치 이유, 자동 업데이트 여부, 계정 |
| `library.db` | `ownership` | 계정별 소유(구매) 기록: 구매 시각, 계정, doc ID |
| `frosting.db` | `frosting` | 업데이트 기록: 마지막 업데이트 시각, 패키지 이름, APK 경로 |

세 DB 는 모두 Google 이 공개 문서로 구조를 정한 파일이 아니라서 스토어 판(version code, 줄여서 vc)이 바뀌면 칸이 달라질 수 있습니다. ALEAPP 도 시험 자료마다 스토어 vc 를 함께 적어 두고, `localappstate.db` 의 설치 이유(install_reason) 칸은 DB 에 있을 때만 읽고 없으면 빈 문자열로 둡니다. [1][2][3]

## 위치와 버전별 차이

ALEAPP 는 세 파일을 아래 패턴으로 찾고, 파일 이름 뒤의 `*` 로 -wal·-journal 같은 딸림 파일도 함께 가져옵니다. [1][2][3]

```
*/com.android.vending/databases/localappstate.db*
*/com.android.vending/databases/library.db*
*/com.android.vending/databases/frosting.db*
```

세 파일은 스토어 앱의 비공개 데이터 폴더에 있어서 앱 샌드박스의 보호를 받습니다. 폴더 구조와 사용자별 폴더는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md)에서, 이런 폴더를 확보하는 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md)에서 다룹니다. ALEAPP 는 찾은 경로에서 사용자 번호를 읽어 결과의 User 칸에 넣으므로, 사용자가 여럿인 기기에서는 이 칸으로 어느 사용자의 스토어 기록인지 나눕니다. [1][2] 딸림 파일에 무엇이 남는지는 공개 자료가 없어 검체에서 확인합니다.

Android 버전·제조사별 칸 차이를 정리한 공개 자료는 없습니다. ALEAPP 의 세 모듈은 Android 10부터 16까지, 삼성 갤럭시(S10·S20·A53)를 포함한 기기 10대의 시험 자료로 시험되었고, 그 범위는 아래와 같습니다. [1][2][3]

| DB | 시험 자료의 Android 범위 | 스토어 vc 범위 | DB 하나의 행 수 |
|---|---|---|---|
| `localappstate.db` | 10~16 | 82481710~85180930 | 56~204행 |
| `library.db` | 10~16 | 82481710~85180930 | 62~162행 |
| `frosting.db` | 10~16 | 82481710~85180930 | 324~555행 |

알려진 버전 차이는 스토어 판에 따라 `appstate` 표에 install_reason 칸이 없을 수 있다는 점입니다. [1]

## 구조

**`localappstate.db` 의 `appstate` 표.** ALEAPP 는 아래 칸을 읽어 User, First Download, Package Name, Title, Install Reason, Last Updated, Auto Update?, Account 순으로 보여 줍니다. [1]

| 칸 | 내용 | ALEAPP 처리 |
|---|---|---|
| `package_name` | 패키지 이름 | 그대로 |
| `title` | 앱 제목 | 그대로 |
| `first_download_ms` | 스토어가 처음 받은 시각 | 유닉스 밀리초 → UTC, 0 이거나 비면 빈칸 |
| `last_update_timestamp_ms` | 스토어 기준 마지막 업데이트 시각 | 유닉스 밀리초 → UTC, 0 이거나 비면 빈칸 |
| `install_reason` | 설치 이유(숫자) | 칸이 없으면 빈 문자열 |
| `auto_update` | 자동 업데이트 | '0' 이면 빈칸, '1' 이면 Yes |
| `account` | 스토어에서 쓴 계정 | 그대로 |

install_reason 숫자의 뜻을 정리한 표는 ALEAPP 에도 없고 공개된 공식 정의도 없어서, 검체에서 확인합니다. [1] account 칸 값이 이메일 주소 형식인지도 검체에서 확인합니다.

**`library.db` 의 `ownership` 표.** ALEAPP 는 조건 없이 아래 질의로 전부 읽고, purchase_time 을 UTC 로 바꿔 User, Purchase Time, Account, Doc ID 칸으로 보여 줍니다. [2]

```sql
SELECT purchase_time, account, doc_id FROM ownership
```

**`frosting.db` 의 `frosting` 표.** ALEAPP 는 시각(`last_updated`), 기본 키인 패키지 이름(`pk`), APK 경로(`apk_path`) 세 칸을 조건 없이 읽어 Last Updated Timestamp, App Package Name, APK Path 로 보여 주고, 시각이 0 이면 빈칸으로 둡니다. [3]

```sql
SELECT last_updated, pk, apk_path FROM frosting
```

## 증거로서 의미

**증명하는 것.** `appstate` 표에 어떤 패키지 행이 있으면 이 기기의 스토어 앱이 그 패키지를 다룬 기록이 있다는 뜻이고, 행에 적힌 계정과 두 시각은 스토어가 적어 둔 값입니다. `ownership` 표는 어느 계정에 어떤 doc ID 가 어느 시각에 소유 기록으로 올라 있는지 보여 주고, `frosting` 표는 패키지별로 스토어가 기록한 마지막 업데이트 시각과 APK 경로를 보여 줍니다. [1][2][3]

**증명하지 못하는 것.** 아래 내용은 공개 자료로 밝혀진 것이 없어서 사실로 쓸 수 없고, 검체에서 따로 확인해야 합니다.

- 앱을 지운 뒤에도 세 DB 에 행이 남는지
- 스토어 밖에서(APK 파일을 직접 설치하는 등) 들어온 앱이 `appstate` 에 들어가는지
- `ownership` 에 무료 앱, 다른 기기에서 받은 앱, 앱이 아닌 콘텐츠(책·영화 등)가 섞이는지, doc_id 가 패키지 이름인지
- `frosting` 행이 `appstate` 보다 훨씬 많은 까닭(시스템 앱이 들어가는지)
- Play 스토어 화면의 라이브러리·관리 목록과 DB 의 관계

그래서 `appstate` 에 행이 없다는 사실만으로 "스토어 밖에서 설치했다" 고 결론 내리지 않고, `ownership` 에 행이 있다는 사실만으로 "지금 이 기기에 설치돼 있다" 고 쓰지 않습니다. 보고서에는 "스토어 앱의 `appstate` 표에 이 패키지의 처음 받은 시각이 이 값으로 적혀 있다" 처럼 기록이 말하는 만큼만 적습니다.

## 시각 해석

세 DB 의 시각 칸은 모두 유닉스 밀리초이고 기준은 UTC 이며, ALEAPP 는 값을 1000 으로 나눠 UTC 시각으로 바꿉니다. [1][2][3] 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

`first_download_ms` 와 `last_update_timestamp_ms` 는 ALEAPP 가 각각 처음 받은 시각과 마지막 업데이트 시각이라고 이름 붙인 값입니다. [1] 이 값이 패키지 관리자가 [설치된 앱](packages/index.md) 기록에 적는 설치·업데이트 시각과 같은 순간을 가리키는지는 공개 자료가 없으니, 두 값이 몇 초~몇 분 어긋나도 곧바로 조작으로 보지 않습니다. 0 이나 빈 값은 ALEAPP 가 빈칸으로 보여 주므로, 결과 화면의 빈칸이 "기록 없음" 인지 "값 0" 인지는 원본 DB 에서 다시 확인합니다. [1][3]

## 함정과 한계

스토어 앱이 업데이트되면 표 구조가 바뀔 수 있어서, 도구가 칸을 못 찾고 빈 결과를 내면 표가 비었는지 칸 이름이 바뀌었는지부터 가립니다. install_reason 처럼 판에 따라 없는 칸이 이미 있습니다. [1]

`ownership` 질의에는 조건이 없어서 ALEAPP 결과에 모든 행이 나오고, 행 종류를 거르는 일은 분석가 몫입니다. [2] 이 표에 앱이 아닌 항목이 섞일 수 있다는 말은 짐작일 뿐이라 보고서에는 쓰지 않습니다.

기기 쪽에서 볼 수 있는 흔적도 해석에 주의합니다. 삼성 기기의 예를 들면 `dumpsys package` 의 "Known Packages:" 절에 Verifier 역할로 com.android.vending 과 com.samsung.android.sm.devicesecurity 가, Installer 역할로 com.google.android.packageinstaller 가 올라 있고, 같은 절에 "Developer verification service provider: com.google.android.verifier" 도 나옵니다. 이 절은 역할을 맡은 패키지를 보여 줄 뿐이라서 개별 앱이 스토어로 들어왔다는 증거가 되지 않습니다.

설정 값에도 Play 스토어나 설치와 이름이 닮은 키가 있습니다. global 에 `phone_play_store_availability`·`default_install_location`·`set_install_location`, secure 에 `install_non_market_apps`·`play_bio_auth_opt_in_displaye_in_suw`·`play_determined_choice_program`·`play_determined_dma_eligibility` 가 있지만, 뜻과 값 형식을 설명한 공개 자료는 없습니다. 키 이름만 보고 뜻을 단정하지 않고, 설정 값 읽는 법은 [설정 값](../system-account/settings.md)을 봅니다.

`dumpsys usagestats` 이벤트에 `type=SHORTCUT_INVOCATION ... shortcutId=AUTO_UPDATE` 줄이 나오기도 하지만, 이 줄만으로는 Play 스토어의 것인지 가릴 수 없어 같은 이벤트의 패키지 이름을 함께 봅니다. adb 일반 권한으로 스토어의 databases 폴더를 읽을 수 있다는 근거는 없으므로, 스토어 DB 를 그 방법으로 얻을 수 있다고 쓰지 않습니다.

## 직접 분석해 보기

**헥스로 한 번.** SQLite 파일의 페이지와 레코드를 헥스로 따라가는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)에서 다루고, 여기서는 시각 값을 알아보는 연습만 합니다. 아래는 설명하려고 고른 값이고 검체에서 나온 값이 아닙니다.

```
10진수   1700000000000            (유닉스 밀리초)
16진수   01 8B CF E5 68 00        (6바이트로 쓴 모양)
÷1000    1700000000               (유닉스 초)
UTC      2023-11-14 22:13:20
```

`appstate` 레코드에서 `first_download_ms` 자리의 바이트를 이렇게 10진수로 읽고 1000 으로 나누면 UTC 시각이 나옵니다. 정수가 레코드 안에 몇 바이트로 어떤 순서로 들어가는지는 SQLite 페이지를 따릅니다.

**공개 도구로 한 번.** 확보한 DB 를 sqlite3 같은 SQLite 도구로 열고 표 구조부터 확인합니다.

```sql
.tables
PRAGMA table_info(appstate);
SELECT package_name, title, first_download_ms, last_update_timestamp_ms, auto_update, account
FROM appstate;
```

`PRAGMA table_info` 결과에 install_reason 이 없으면 그 칸을 뺀 질의로 읽습니다. 같은 폴더를 ALEAPP 에 넣으면 세 모듈(InstalledappsVending, InstalledappsLibrary, "App Updates (Frosting.db)")이 "Installed Apps" 분류에 결과를 냅니다. [1][2][3] 도구 결과와 직접 질의 결과의 행 수를 맞춰 보면 도구가 빠뜨린 행이 있는지 가릴 수 있고, 이 절차는 [도구 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 내용 |
|---|---|
| [설치된 앱](packages/index.md) | 패키지 관리자가 적은 설치·업데이트 시각과 설치 출처를 스토어 DB 의 시각·패키지 목록과 맞춰 봅니다 |
| 시스템의 설치 출처 정보 (InstallSourceInfo) | 설치를 요청한 패키지, 설치 책임 패키지(installer of record), 업데이트 소유 패키지를 스토어 기록과 맞춰 봅니다 [4] |
| [계정](../system-account/accounts/index.md) | `appstate`·`ownership` 의 account 값이 기기에 등록된 계정과 같은지 봅니다 |
| [앱 사용 기록](usagestats/index.md) | 처음 받은 시각 뒤에 그 앱을 실제로 쓴 기록이 있는지 봅니다 |
| [APK 정보](../embedded-metadata/apk.md) | `frosting` 의 APK 경로에 있는 파일의 서명·버전을 확인합니다 |

Android 는 앱마다 어떻게 설치됐는지를 InstallSourceInfo 로 알려 주고, `PackageManager#getInstallSourceInfo(String)` 로 얻습니다. 항목은 설치를 요청한 패키지(getInitiatingPackageName)와 그 서명 정보(getInitiatingPackageSigningInfo), 요청한 패키지가 누구를 대신했는지(getOriginatingPackageName), 설치 책임 패키지(getInstallingPackageName), 업데이트 소유 패키지(getUpdateOwnerPackageName), 설치 당시의 출처 정보(getPackageSource)이고, 해당 값이 없으면 null 입니다. (현행 AOSP 기준) [4] 스토어로 받은 앱이면 설치 책임 패키지가 com.android.vending 으로 나올 것으로 보이지만, 이를 밝힌 공개 문서는 없으니 검체에서 확인합니다.

앱이 어디서 들어왔는지를 묻는 조사라면 [악성 앱은 어디서 들어왔나](../../04-scenarios/incident/initial-access.md), 앱을 언제 썼는지를 묻는 조사라면 [어떤 앱을 언제 썼나](../../04-scenarios/activity/app-usage.md)에서 이 기록의 쓰임새를 이어서 봅니다.

## 실습

공개 검체(NIST CFReDS 등)의 Android 이미지 가운데 Play 스토어 데이터 폴더가 들어 있는 것을 골라 아래 질문을 풀어 봅니다.

1. 세 DB 가 모두 있는지, -wal 파일이 함께 있는지 확인하고, `appstate` 표에 install_reason 칸이 있는지 봅니다.
2. `appstate` 의 행 수와 `frosting` 의 행 수를 세고, `frosting` 에만 있는 패키지가 어떤 앱인지 설치된 앱 목록과 맞춰 봅니다.
3. 한 앱을 골라 `first_download_ms`, `last_update_timestamp_ms`, `frosting` 의 시각을 UTC 로 바꾸고, 설치된 앱 기록의 설치·업데이트 시각과 얼마나 차이 나는지 적습니다.
4. `ownership` 의 계정 값이 몇 종류인지 세고 기기의 계정 목록과 비교합니다.
5. ALEAPP 결과와 직접 SQL 질의 결과의 행 수가 같은지 확인합니다.

## 참고 문헌

1. ALEAPP installedappsVending.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/installedappsVending.py
2. ALEAPP installedappsLibrary.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/installedappsLibrary.py
3. ALEAPP frosting.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/frosting.py
4. AOSP InstallSourceInfo.java (platform_frameworks_base, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/content/pm/InstallSourceInfo.java
