---
title: "구글 계정 흔적"
parent: "계정"
grand_parent: "아티팩트 · 시스템·계정"
nav_order: 340
---

# 구글 계정 흔적 (Google Account)

구글 계정이 기기에 남기는 시스템 쪽 흔적을 정리합니다. 계정 DB 의 표 구조는 [계정 DB 구조 (accounts_ce.db·accounts_de.db)](accounts-db.md) 페이지에 있고, 이 페이지는 그 위에 더해 볼 동기화 기록과 설정 키, 패키지를 다룹니다. 값은 현행 AOSP(frameworks/base 의 main 가지) 기준입니다.

구글 계정도 다른 계정처럼 계정 DB 의 `accounts` 표에 name·type 쌍으로 남고, 계정과 동기화 대상의 조합마다 설정과 상태를 적는 `/data/system/sync/` 파일, 구글 서비스 이름이 붙은 설정 키와 패키지가 그 곁에 남습니다 [1][4].

## 무엇을 기록하나 · 왜 생기나

구글 계정을 기기에 추가하면 AccountManager 에 계정으로 등록되어 `accounts_de.db`·`accounts_ce.db` 의 `accounts` 표에 이름과 종류가 들어갑니다 [1]. 구글 계정의 type 값은 `com.google` 입니다. GoogleAuthUtil.GOOGLE_ACCOUNT_TYPE 상수의 값이 `com.google` 이고, AccountManager 를 부를 때 이 값으로 구글 계정 종류를 가리킵니다 [5]. 그래도 보고서에는 실물 DB 의 type 값을 직접 보고 판단한 근거를 함께 적습니다. ALEAPP 의 계정 모듈은 Android 10~16 의 Pixel·Samsung Galaxy 기기 표본 데이터를 대상으로 합니다 [2][3].

계정 DB 와 따로, 동기화 관리자(SyncStorageEngine)는 계정 이름·종류와 동기화 대상(authority, 예: 연락처 제공자)의 조합마다 동기화를 켰는지와 마지막으로 성공·실패한 시각을 파일에 적습니다 [4]. 이 파일은 구글 계정만의 것이 아니고 동기화를 쓰는 모든 계정이 함께 쓰지만, 이 핸드북에서는 이 페이지에 모아 두고 다른 계정 페이지에서는 여기로 링크합니다.

## 위치와 버전별 차이

| 위치 | 담긴 것 | 근거 |
|---|---|---|
| `accounts_de.db`·`accounts_ce.db` | 계정 이름·종류, 권한 부여, 토큰 | 현행 AOSP 기준 [1] |
| `/data/system/sync/accounts.xml` | 계정·동기화 대상별 설정 | 현행 AOSP 기준 [4] |
| `/data/system/sync/status` | 동기화 상태(마지막 성공·실패 시각 등) | 현행 AOSP 기준 [4] |
| `/data/system/sync/stats` | 동기화 통계 | 현행 AOSP 기준 [4] |
| `dumpsys package` 의 Known Packages | 구글 설치 도우미·서비스 패키지의 역할 | |
| `/sdcard/Android/media/com.google.android.gms/` | 폴더가 있을 수 있음 | |
| `settings` 의 구글·동기화 관련 키 | 키 이름(뜻은 공개 자료 없음) | |

동기화 파일은 SyncStorageEngine 이 `<dataDir>/system/sync` 폴더(SYNC_DIR_NAME = "sync")에 두고, 흔히 `/data/system/sync/` 입니다 [4]. 예전 파일 이름 `status.bin`·`stats.bin` 도 상수로 남아 있어서 예전 버전 기기에서는 이 이름도 함께 찾습니다 [4]. 이름이 바뀐 Android 버전을 밝힌 공개 자료는 없습니다. 루팅하지 않은 기기에서 adb 일반 권한으로 이 폴더를 읽을 수 있는지는 기기마다 확인합니다.

구글 서비스 앱(com.google.android.gms)과 Play 스토어(com.android.vending) 안의 계정 관련 DB 경로와 표 이름은 공개된 분석 자료가 없어 실제 기기로 확인해야 합니다.

## 구조 — 동기화 파일

### accounts.xml

| 요소 | 속성 | 뜻 |
|---|---|---|
| `accounts` (루트) | `version`, `nextAuthorityId`, `offsetInSeconds` | 파일 전체 값 |
| `authority` | `id`, `user`, `enabled`, `account`, `type`, `authority`, `syncable` | 계정 이름(account)·종류(type)와 동기화 대상(authority) 조합 하나의 설정 |
| `listenForTickles` | `user`, `enabled` | 사용자별로 전체 자동 동기화(마스터 동기화)를 켰는지 |
| `periodicSync` | `period`, `flex` | 주기 동기화 설정 |
| `extra` (`periodicSync` 안) | `name`, `type`, `value1`, `value2` | 주기 동기화에 붙은 값 |

위 이름은 현행 AOSP 의 SyncStorageEngine 기준입니다 [4]. 요소 이름 상수 `listenForTickles` 와 따로 속성 이름 상수 `listen-for-tickles` 도 있는데, 속성 쪽은 예전 파일을 읽을 때 쓰는 이름으로 보입니다. 아래는 명세로 만든 뼈대 예시이고 값은 비워 두었습니다.

```xml
<accounts version="…" nextAuthorityId="…" offsetInSeconds="…">
  <authority id="…" user="…" enabled="…" account="…" type="…" authority="…" syncable="…" />
</accounts>
```

현행 AOSP 는 이 파일을 Xml.resolveSerializer 가 돌려주는 직렬화기로 쓰는데, 이 함수는 기기 설정에 따라 글자 XML 대신 바이너리 XML 을 고를 수 있습니다 [4]. 그래서 파일을 열었을 때 글자로 읽히지 않으면 [안드로이드 바이너리 XML (ABX)](../../../01-foundations/data-formats/abx.md) 인지 확인합니다.

### status 와 stats

`status` 파일에는 동기화 대상마다 SyncStatusInfo 가 들어가고, 필드는 `lastSuccessTime`, `lastSuccessSource`, `lastFailureTime`, `lastFailureSource`, `lastFailureMesg`, `initialFailureTime`, `pending`, `initialize`, `periodicSyncTimes` 와 통계(`totalStats`, `todayStats`, `yesterdayStats`)입니다 [4]. 현행 AOSP 는 `status` 를 프로토콜 버퍼(ProtoOutputStream)로 쓰고 [4], `stats` 파일은 동기화 통계를 담습니다. `stats` 의 바이트 단위 형식과 프로토콜 버퍼 필드 번호는 공개 자료가 없어 실제 파일로 확인해야 합니다.

## 설정 키와 패키지

`settings` 세 영역에는 구글이나 계정·동기화와 관련된 이름의 키가 있을 수 있습니다. 키가 있다는 사실 말고, 값의 뜻을 밝힌 공개 자료는 없습니다.

| 영역 | 키 | 알려진 것 |
|---|---|---|
| secure | `com.google.android.gms.tapandpay.oobe.OOBE_PHENOTYPE_STATUS`, `com.google.android.gms.tapandpay.tokenization.CACHED_BACKUP_STATUS` | 키 이름만 |
| global | `gms_checkin_timeout_min`, `master_sync_status`, `synced_account_name` | 키 이름만. `synced_account_name` 이 구글 계정을 가리키는지 삼성 계정을 가리키는지는 실제 기기에서 확인 |
| system | `contact_default_account`, `sync_disabled_accounts_with_hash` | 키 이름만. 뜻은 공개 자료 없음 |

`dumpsys package` 의 Known Packages 에는 Setup Wizard 로 `com.google.android.setupwizard`, Configurator 로 `com.google.android.gms`, Verifier 로 `com.android.vending` 이 나올 수 있고, `/sdcard/Android/media/` 아래에는 `com.google.android.gms` 폴더가 있을 수 있습니다. 설정 키를 읽는 법은 [설정 값 (Settings Global·Secure·System)](../settings.md) 페이지에 있습니다.

## 증거로서 의미

| 기록 | 증명하는 것 | 증명하지 못하는 것 |
|---|---|---|
| 계정 DB 의 구글 계정 행 | 확보 시점에 그 사용자 공간에 이 계정이 등록되어 있었다는 것 | 언제 추가했는지, 누가 썼는지 |
| `accounts.xml` 의 `authority` | 이 계정과 동기화 대상 조합에 동기화 설정이 있었고, 켜져 있었는지 | 무엇을 주고받았는지 |
| `status` 의 성공·실패 시각 | 그 시각에 이 조합의 동기화가 성공하거나 실패했다는 기록이 있다는 것 | 사람이 직접 동기화를 시작했는지(`*Source` 값의 뜻은 공개 자료 없음) |
| 설정 키 이름 | 그 키가 설정에 있다는 것 | 키의 뜻, 계정 가입이나 로그인 여부 |

보고서에는 "이 시각에 이 계정과 연락처 제공자 조합의 동기화가 성공한 기록이 있다" 처럼 쓰고, "이 시각에 연락처를 올렸다" 처럼 기록보다 넓게 쓰지 않습니다.

## 시각 해석

동기화 관리자가 적는 이벤트 시각은 `System.currentTimeMillis()` 기준이라 유닉스 에포크 밀리초(UTC)입니다 [4]. 계정 DB 의 시각 열과 변경 기록의 시간대 문제는 [계정 DB 구조](accounts-db.md) 페이지의 "시각 해석" 절에 있고, 계정 DB 의 `accounts` 표에는 계정을 추가한 시각 열이 없습니다 [1].

## 함정과 한계

GMS 내부 DB 는 공식 자료가 없으니, 다른 도구 결과를 옮길 때도 실물 파일에서 한 번 더 확인합니다. `synced_account_name` 처럼 이름만 보고 구글 계정 설정이라고 단정하기 쉬운 키도 어느 계정을 가리키는지 실제 기기에서 확인합니다.

`status` 의 필드는 마지막 성공·실패 시각과 통계라서 지난 동기화를 한 건씩 다시 따라가려면 다른 기록이 필요하고, 기기를 초기화하거나 계정을 지운 뒤의 모습은 [초기화 흔적 (Factory Reset)](../factory-reset.md) 과 계정 DB 의 변경 기록을 함께 봅니다. 서버 쪽에 남은 기록은 [클라우드 데이터 (Google Takeout 등)](../../../03-techniques/acquisition/cloud-data.md) 절차로 따로 확보합니다.

## 직접 분석해 보기

계정 DB 를 헥스와 `sqlite3` 로 읽는 법은 [계정 DB 구조](accounts-db.md) 페이지에 있습니다. 구글 계정 행을 찾을 때는 type 값을 미리 정해 거르지 말고 모든 type 을 먼저 봅니다.

```sql
SELECT _id, name, type FROM accounts ORDER BY type, name;
```

`accounts.xml` 은 사본을 글 편집기로 열어 `authority` 요소 가운데 `account` 속성이 대상 계정인 것을 모으고, `enabled` 와 `syncable` 을 표로 옮깁니다. 공개 파서로는 ALEAPP 의 Accounts_de, Accounts_ce 모듈이 계정 DB 를 읽습니다 [2][3]. 라이브 기기라면 [dumpsys 출력 (dumpsys)](../../logs/dumpsys.md) 의 `dumpsys account` 로 계정 목록을 먼저 봅니다.

## 교차 검증

구글 계정으로 쓰는 앱의 데이터는 [지메일 (Gmail)](../../mail-cloud/gmail.md), [구글 드라이브 (Google Drive)](../../mail-cloud/google-drive.md), [구글 포토 (Google Photos)](../../media/google-photos.md), [구글 플레이 기록 (Play Store)](../../app-usage/play-store.md), [구글 백업 (Google Backup)](../../mail-cloud/google-backup.md) 에서 보고, 저장된 암호는 [저장된 암호 (Google 비밀번호 관리자·Samsung Pass)](../../credentials-security/saved-passwords.md) 에서 봅니다. `contact_default_account` 같은 연락처 쪽 흔적은 [연락처 (contacts2.db)](../../communications/contacts.md) 와 맞춰 보고, 계정이 다른 사람 손에 넘어간 정황을 볼 때는 [계정 탈취 흔적 (Account Takeover)](../../../04-scenarios/incident/account-takeover.md) 시나리오를 따릅니다.

## 실습

공개된 안드로이드 시험 자료(NIST CFReDS 에 올라온 모바일 이미지 등)를 구해 다음을 풀어 봅니다.

1. 계정 DB 의 모든 type 을 뽑고, 그중 구글 계정으로 판단한 행과 판단한 근거를 적어 봅니다.
2. `accounts.xml` 에서 그 계정의 `authority` 요소를 모두 찾아 동기화 대상별로 켜짐·꺼짐을 표로 만들어 봅니다.
3. `status` 를 읽을 수 있다면 마지막 성공 시각을 날짜로 바꾸고, 같은 시각 근처에 그 앱의 사용 기록이 있는지 봅니다.

## 참고 문헌

1. AccountsDb.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/accounts/AccountsDb.java
2. ALEAPP accounts_de.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/accounts_de.py
3. ALEAPP accounts_ce.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/accounts_ce.py
4. SyncStorageEngine.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/content/SyncStorageEngine.java
5. GoogleAuthUtil — Google Play services 참조 문서(Android 4.4 문서 사본), https://docs.huihoo.com/android/4.4/reference/com/google/android/gms/auth/GoogleAuthUtil.html
