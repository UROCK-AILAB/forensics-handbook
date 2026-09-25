---
title: "구글 백업"
parent: "아티팩트 · 메일·클라우드"
nav_order: 1130
---

# 구글 백업 (Google Backup)

## 한 줄 요약

구글 백업은 Google 계정이 로그인된 기기에서 앱 데이터·통화 기록·연락처·설정·문자를 Google 서버로 올리는 Android 기본 백업 기능이고, 백업 본체는 서버에 있어서 기기에서는 설정 키·상태 파일·로그·계정 기록처럼 "백업이 켜져 있었다, 복원한 적이 있다" 를 가리키는 흔적을 주로 봅니다.

## 무엇을 기록하나 · 왜 생기나

앱 데이터 백업은 두 가지 방식으로 나뉩니다[1]. 자동 백업 (Auto Backup) 은 앱의 파일을 통째로 올리는 방식이고, Android 6.0(API 23) 이상을 대상으로 하는 앱은 따로 설정하지 않아도 참여하지만 앱이 끌 수 있습니다[1][2]. 키-값 백업 (Key-Value Backup) 은 앱이 BackupAgent 를 선언해야 참여하는 방식이라서 기본으로는 꺼져 있습니다[1]. 두 방식 모두 기기에 Google 계정이 로그인되어 있어야 하고, 앱 안에서 따로 로그인할 필요는 없습니다[1].

| 구분 | 자동 백업 | 키-값 백업 |
|---|---|---|
| 쓸 수 있는 버전 | Android 6.0(API 23) 이상 | Android 2.2(API 8) 이상 |
| 참여 | API 23 이상 대상 앱은 기본 참여, 앱이 끌 수 있음 | 기본 꺼짐, 앱이 BackupAgent 를 선언해야 참여 |
| 저장처 | 사용자 Google Drive 안의 비공개 폴더 | Android Backup Service |
| 앱당 한도 | 25MB | 5MB |
| 실행 주기 | 대략 하루 한 번, 백업하는 동안 앱을 종료함 | 여러 앱의 요청을 묶어 몇 시간마다, 앱을 종료하지 않음 |
| 근거 | [1][2] | [1] |

자동 백업은 가장 최근 백업 하나만 보관하고 새 백업을 만들면 이전 것을 지우며, 이 저장분은 사용자의 개인 Google Drive 용량에 들어가지 않습니다[2]. 테스트 문서에는 "클라우드 백업은 앱당 2MB, 기기 간 전송(D2D)은 앱당 2GB(Android 12, API 31 이상)" 라는 다른 값도 나오는데[3], 위 표의 25MB·5MB 와 어떻게 맞춰지는지는 확인하지 못했습니다.

사용자 도움말은 백업 항목으로 앱과 앱 데이터, 통화 기록, 연락처, 기기 설정, SMS·MMS 메시지를 들고, 사진·영상은 Google 포토가, RCS 메시지는 Google 메시지가, 통화 설정과 차단 번호는 Google 전화 앱이 따로 백업한다고 안내합니다[4]. 그래서 사진은 [구글 포토](../media/google-photos.md) 쪽을 봅니다. Android 7.0(API 24) 이상에서는 사용자가 앱에 준 권한도 시스템이 자동으로 백업하고 복원합니다[1].

앱 데이터 가운데 기본으로 들어가는 것은 SharedPreferences 파일, `getFilesDir()`·`getDir()` 아래 파일, `getDatabasePath()` 아래 파일(SQLiteOpenHelper 로 만든 DB 포함), 외부 저장소의 `getExternalFilesDir()` 아래 파일이고, `getCacheDir()`·`getCodeCacheDir()`·`getNoBackupFilesDir()` 아래 파일은 빠집니다[2]. 앱은 매니페스트로 이 범위를 바꿀 수 있습니다(아래 "위치와 버전별 차이").

복원은 앱을 설치할 때마다 일어나는데, Play 스토어에서 설치할 때와 기기 초기 설정 중 이전 앱을 자동으로 설치할 때, `adb install` 로 설치할 때 모두 해당합니다[2]. 복원은 APK 를 설치한 뒤 사용자가 앱을 실행할 수 있게 되기 전에 끝나고[2], 복원된 데이터는 기기 안 앱 폴더에 일반 데이터로 들어갑니다.

## 위치와 버전별 차이

백업 데이터 자체는 Google 서버에 있고 기기에는 없습니다[1][2]. 기기 안에서 백업 상태를 적는 곳은 아래와 같습니다. 경로는 AOSP 소스의 코드 식으로 적었고, 실제 경로는 확인하지 못해 "추정" 으로 표시합니다.

| 항목 | 소스 기준 위치 | 실제 경로 | 근거 |
|---|---|---|---|
| 상태 폴더(시스템 사용자) | `new File(Environment.getDataDirectory(), "backup")` | 보통 `/data/backup` 으로 추정 | [6] |
| 준비 폴더(시스템 사용자) | `new File(Environment.getDownloadCacheDirectory(), "backup_stage")` | 보통 `/cache/backup_stage` 로 추정. A/B 기기에서 위치는 확인하지 못함 | [6] |
| 다른 사용자의 상태·준비 폴더 | `Environment.getDataSystemCeDirectory(userId)` 아래 `backup`, `backup_stage` | `/data/system_ce/` 아래 사용자 ID 폴더로 추정 | [6] |
| 사용자별 상태의 다른 사본 | 시스템 사용자 상태 폴더 아래 사용자 ID 이름의 하위 폴더(`getStateDirInSystemDir`) | — | [6] |
| 설정 키 | Settings.Secure 의 `backup_*` 키 | 아래 "구조" | [5], 기기 관찰 |

상태 폴더는 `/data` 아래라서 일반 adb 권한으로는 읽을 수 없을 것으로 보지만, 이번 시험 기기에서 시도해 보지는 않았습니다. 여러 사용자와 프로필이 있는 기기라면 사용자마다 상태가 따로 있으므로 [사용자와 프로필](../system-account/users-profiles.md) 과 함께 봅니다.

버전에 따라 달라지는 점은 다음과 같습니다.

| Android 버전 | 바뀐 점 | 근거 |
|---|---|---|
| 2.2(API 8) 이상 | 키-값 백업 | [1] |
| 6.0(API 23) 이상 | 자동 백업 | [1][2] |
| 7.0(API 24) 이상 | 앱 권한도 자동으로 백업·복원 | [1] |
| 9 이상 | 기기의 PIN·패턴·비밀번호로 백업을 종단 간 암호화 | [2][4] |
| 11 이하 | 백업 규칙을 매니페스트의 `android:fullBackupContent` 로 줌 | [2] |
| 12(API 31) 이상 | 규칙을 `android:dataExtractionRules` 로 주고, 안에서 `cloud-backup` 과 `device-transfer` 를 따로 적음. 테스트 문서의 D2D 앱당 2GB 값도 이 버전부터 | [2][3] |
| 12(API 31) 이상 대상 앱 | 일부 제조사 기기에서 `android:allowBackup="false"` 가 클라우드 백업만 끄고 기기 간 전송은 끄지 않음 | [2] |
| 삼성 One UI | 구글 백업과 따로 삼성 클라우드와 스마트스위치가 있음. 시험 기기에서 스마트스위치 관련 설정 키 이름을 확인함. One UI 에서 구글 백업 메뉴의 위치와 이름은 확인하지 못함 | 기기 관찰 |

도움말은 설정 → Google 서비스 → 모든 서비스 에서 백업을 관리하라고 안내하고, 일부 단계는 Android 9 이상에서만 된다고 적혀 있습니다[4]. 삼성 클라우드 쪽은 [삼성 클라우드와 원드라이브](samsung-cloud-onedrive.md) 에서 다룹니다.

## 구조

### 상태 폴더 안의 파일

AOSP 의 `UserBackupManagerService` 가 상태 폴더 안에 두는 파일·폴더 이름은 아래와 같습니다[5]. 파일 안의 바이트 구조는 이번에 연 자료에 없어서 적지 않습니다.

| 이름 | 소스에 적힌 쓰임 |
|---|---|
| `pending` | 저널 폴더 |
| `ancestral` | 토큰 파일. 기록 버전 상수 `CURRENT_ANCESTRAL_RECORD_VERSION = 1` |
| `processed` | 처리한 패키지 저널 |
| `fb-schedule` | 전체 백업 일정. 상수 `SCHEDULE_FILE_VERSION = 1` |
| `serial_id` | 이름만 확인 |

같은 소스에는 토큰 두 가지가 있는데, `mAncestralToken` 은 복원에 쓴 이전 데이터셋의 토큰이고 `mCurrentToken` 은 현재 백업 토큰입니다[5].

### 설정 키

소스는 Settings.Secure 의 `BACKUP_TRANSPORT`, `BACKUP_AUTO_RESTORE`(기본값 1 로 읽음), `USER_SETUP_COMPLETE` 키를 참조합니다[5]. 시험 기기에서 settings 목록을 읽었을 때 아래 키 이름이 보였고, 값은 가려져 있어 보지 못했습니다.

| 영역 | 키 이름 | 비고 |
|---|---|---|
| secure | `backup_enabled`, `backup_transport`, `backup_auto_restore` | 백업 켜짐, 전송 경로, 자동 복원 |
| secure | `backup_encryption_opt_in_displayed`, `backup_manager_constants`, `user_full_data_backup_aware` | 뜻은 이름으로만 짐작 |
| secure | `backup_enabled:com.android.calllogbackup`, `backup_enabled:com.android.providers.telephony` | 패키지별 키 |
| secure | `mms_backup_enabled`, `mms_backup_in_progress`, `mms_backup_last_completed` | 값 형식(시각 단위 등)은 확인하지 못함 |
| secure | `com.google.android.gms.tapandpay.tokenization.CACHED_BACKUP_STATUS`, `wifi_ap_settings_cloud_backup_restoring` | 뜻은 확인하지 못함 |
| secure | `IS_SMARTSWITCH_DATA_PRESENT`, `IS_SMARTSWITCH_RESTORE_IN_PROGRESS` | 삼성 스마트스위치 쪽 흔적 |
| global | `backup_agent_timeout_parameters`, `SecureWifiBackupExist`, `setup_type` | 뜻은 이름으로만 짐작 |
| global | `smartswitch_bnr_count`, `smartswitch_transfer_completed`, `smartswitch_transfer_start_in_oobe` | 삼성 스마트스위치 쪽 흔적 |

테스트 문서에는 `backup_local_transport_parameters`, `backup_enable_d2d_test_mode`(Android 12 이상) 같은 키도 나오지만[3] 시험 기기 목록에서는 보지 못했습니다. settings 값을 읽는 법과 저장 파일은 [설정 값](../system-account/settings.md) 에서 다룹니다.

### 전송 경로 이름

`backup_transport` 에는 백업을 어디로 보내는지 가리키는 전송 경로 (transport) 이름이 들어갑니다. 테스트 문서가 드는 이름은 아래 셋입니다[3].

```text
com.google.android.gms/.backup.BackupTransportService      대부분 기기의 클라우드 전송 (GMS Transport)
com.android.localtransport/.LocalTransport                 로컬 테스트용 전송
com.google.android.gms/.backup.migrate.service.D2dTransport  기기 간 전송 (D2D)
```

시험 기기의 `backup_transport` 에 실제로 어떤 이름이 들어 있었는지는 값이 가려져 있어 알 수 없습니다.

### 로그

테스트 문서는 백업 관련 logcat 태그로 `BackupManagerService`, `PFTBT`, `Backup` 을 들고[3], AOSP 의 `UserBackupManagerService` 도 `BackupManagerService` 쪽 `TAG` 상수를 로그 태그로 씁니다[5]. 문서에 나오는 메시지 예는 `PFTBT` 태그로 찍히는 용량 초과 때의 "Transport rejected backup", `BackupManagerService` 태그로 찍히는 앱 기동이 10초를 넘었을 때의 "Timeout waiting for agent", 그리고 "Full backup not currently possible" 입니다[3]. logcat 을 읽는 법은 [logcat](../logs/logcat.md) 에 있습니다. `dumpsys backup` 의 출력 모양은 이번에 확인하지 못했고 시험 기기 관찰에도 없습니다.

## 증거로서 의미

**증명하는 것.** `backup_enabled` 와 `backup_transport` 값은 수집 시점에 기기의 백업 설정이 어떻게 되어 있었는지 보여 주고, 패키지별 `backup_enabled:` 키는 통화 기록 백업 패키지(com.android.calllogbackup)나 문자 제공자(com.android.providers.telephony)가 백업 대상으로 등록되어 있었다는 흔적입니다. 구글 백업은 Google 계정 로그인이 전제라서[1], [계정](../system-account/accounts/index.md) 의 추가 기록은 백업이 가능해진 시작점을 좁히는 데 씁니다. 소스에서 `mAncestralToken` 이 복원에 쓴 이전 데이터셋의 토큰이라서[5] `ancestral` 파일이 있으면 이 기기가 이전 백업에서 복원된 적이 있다는 쪽으로 읽을 수 있지만, 파일 안 구조를 확인하지 못해 단정하지는 않습니다.

**증명하지 못하는 것.** 설정 키는 "켜져 있었다" 까지만 말하고, 실제로 어느 날 백업이 끝났는지, 서버에 무엇이 올라갔는지는 말하지 않습니다. 자동 백업은 최근 것 하나만 남기므로[2] 서버에 과거 시점의 데이터가 남아 있다고 기대할 수도 없습니다. 복원된 앱 데이터는 이전 기기에서 만든 데이터일 수 있어서, 앱 폴더 안의 대화·기록이 이 기기에서 만들어졌다고 곧바로 쓰지 않습니다. 시험 기기의 계정 목록은 계정 종류 값이 가려져 있어, 거기에 Google 계정이 있었는지는 이번 관찰로 알 수 없습니다.

## 시각 해석

자동 백업은 사용자가 백업을 켜 두었고, 마지막 백업 뒤 24시간 이상 지났고, 기기가 유휴 상태이고, Wi-Fi 에 연결되어 있을 때(모바일 데이터 백업을 켜지 않은 경우) 실행됩니다[2]. 문서는 실제로는 대개 매일 밤 이 조건이 맞는다고 설명하고, 네트워크에 한 번도 연결하지 않으면 백업이 전혀 되지 않을 수도 있다고 적습니다[2]. 그래서 백업이 일어난 시각은 사용자가 무언가를 조작한 시각이 아니라 이 조건이 맞은 시각으로 읽습니다. 도움말은 백업이 끝나기까지 최대 24시간 걸릴 수 있다고 안내합니다[4].

`mms_backup_last_completed` 는 이름으로 보아 MMS 백업이 끝난 시각일 수 있지만 값의 단위와 기준(UTC 인지 현지 시각인지)은 확인하지 못했습니다. 시험 기기의 `dumpsys account` 에서 Accounts History 의 `timestamp` 칸은 날짜와 시:분:초 모양으로 보였지만 시간대는 확인하지 못했습니다. 복원한 앱의 파일 시각이 새 기기에 설치한 시각 근처로 모일 가능성이 있지만 확인하지 못했으니, 보고서에 쓰기 전에 시험 기기로 복원해 보고 확인합니다. 시각 값 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 을 봅니다.

## 함정과 한계

화면 잠금 암호화 때문에 서버 쪽 데이터를 읽을 수 있는 범위가 달라집니다. Android 9 이상은 기기의 PIN·패턴·비밀번호로 백업을 종단 간 암호화하고[2], 도움말은 "일부 데이터는 기기의 화면 잠금으로 추가 암호화된다" 고 설명하면서 Google 포토와 MMS 미디어는 여기서 빠진다고 적습니다[4]. 이 암호화가 수사 기관의 클라우드 자료 확보 범위에 어떤 영향을 주는지는 이번 자료에 나오지 않습니다. 클라우드 쪽 자료를 다루는 방법은 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 를 봅니다.

앱이 백업에서 빠졌는지는 설정 키로 알 수 없고 앱 매니페스트를 봐야 합니다. `allowBackup`, `fullBackupContent`, `dataExtractionRules` 값으로 그 앱 데이터가 백업에 들어갈 수 있었는지 판단하는데, Android 12 이상 대상 앱은 일부 제조사 기기에서 `allowBackup="false"` 여도 기기 간 전송은 막히지 않는다는 점을 함께 따집니다[2]. 매니페스트를 읽는 법은 [APK 정보](../embedded-metadata/apk.md) 에 있습니다.

이름에 backup 이 들어간 설정 키가 모두 구글 백업 흔적은 아닙니다. 시험 기기의 global 영역에는 `dc_backup_animator_duration_scale` 같은 키가, system 영역에는 `backup_dark_mode`, `backup_screen_off_timeout` 같은 키가 있었는데, 이름만 보고 구글 백업과 묶지 않습니다. 삼성 기기라면 스마트스위치로 옮긴 흔적(`smartswitch_*`, `IS_SMARTSWITCH_*`)과 구글 백업 복원을 구분해서 적어야 합니다.

logcat 버퍼는 짧게 유지되는 것으로 알려져 있지만 이번 자료로 확인하지는 않았으므로, 백업 로그가 필요하면 기기를 받자마자 먼저 떠 둡니다. `/sdcard/Android/media` 아래에 `com.google.android.gms` 폴더가 있었지만 백업과 관련이 있는지는 확인하지 못했습니다. 흔히 "기기를 오래 쓰지 않으면 57일 뒤 백업이 지워진다" 고 말하지만 이번에 연 문서에는 이 내용이 없어 쓰지 않습니다.

증거 기기에서 `bmgr enable`, `bmgr backupnow`, `bmgr run` 같은 명령은 쓰지 않습니다. 테스트 문서에 나오는 개발자용 명령이고[3], 실행하면 기기의 백업 상태가 바뀝니다. 읽기 명령인 `bmgr list transports` 만 씁니다.

## 직접 분석해 보기

**헥스로 한 번.** `ancestral`, `fb-schedule` 같은 상태 파일은 소스에 기록 버전 상수만 보이고 바이트 배치를 적은 자료를 이번에 열지 못해서, 이 페이지에는 헥스 예시를 싣지 않습니다. 전체 파일 시스템 이미지에서 상태 폴더를 찾았다면 형식을 짐작하기 전에 파일 첫 바이트부터 헥스 편집기로 보고, 앞쪽에 버전 값 1 로 읽히는 필드가 있는지부터 소스 상수와 맞춰 봅니다. 저장 형식이 [안드로이드 바이너리 XML](../../01-foundations/data-formats/abx.md) 이나 [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 인지도 이 단계에서 가립니다.

**공개 도구로 한 번.** adb 일반 권한으로 읽을 수 있는 것부터 봅니다. 시험 기기에서는 settings 목록과 `dumpsys account` 를 일반 셸 권한으로 읽을 수 있었습니다. 전송 경로 목록은 테스트 문서의 읽기 명령으로 봅니다[3].

```text
adb shell bmgr list transports
adb logcat -d | grep -E "BackupManagerService|PFTBT|Backup"
```

settings 에서는 위 "설정 키" 표의 이름을 찾아 값을 적고, `dumpsys account` 에서는 Accounts History 표의 `action_account_add`, `action_account_remove` 행을 찾아 계정이 언제 붙고 떨어졌는지 적습니다. 계정 기록을 읽는 자세한 방법은 [계정](../system-account/accounts/index.md) 과 [dumpsys 출력](../logs/dumpsys.md) 에 있습니다. ALEAPP 같은 공개 도구가 이 흔적을 파싱하는지는 쓰는 도구의 판에서 확인합니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [계정](../system-account/accounts/index.md) | Google 계정이 붙은 시각과 떨어진 시각 |
| [설정 값](../system-account/settings.md) | `backup_*`, `smartswitch_*` 키 값 |
| [설치된 앱](../app-usage/packages/index.md) | 복원과 함께 설치된 앱과 설치 시각 |
| [초기화 흔적](../system-account/factory-reset.md) | 초기화 뒤 초기 설정 중에 복원했는지 |
| [통화 기록](../communications/call-log.md), [문자](../communications/messages/index.md) | 백업 대상 패키지 키와 기기 안 기록의 기간 |
| [logcat](../logs/logcat.md) | `BackupManagerService`, `PFTBT` 태그 줄 |
| [삼성 클라우드와 원드라이브](samsung-cloud-onedrive.md) | 삼성 쪽 백업·이전과 구분 |
| [구글 드라이브](google-drive.md) | 같은 계정의 드라이브 사용 흔적 |

기기를 새로 바꾼 사용자의 앱 데이터가 어디서 왔는지 따질 때는 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 와 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 도 함께 봅니다.

## 실습

NIST CFReDS 같은 곳에서 구할 수 있는 공개 안드로이드 검체로 아래 질문을 풀어 봅니다.

1. settings 에서 `backup_enabled`, `backup_transport`, `backup_auto_restore` 값을 찾고, 전송 경로가 위 세 이름 가운데 어느 것인지 봅니다.
2. 이름이 `backup_enabled:` 로 시작하는 키를 모두 찾아 어떤 패키지가 등록되어 있는지 적습니다.
3. 파일 시스템 이미지라면 상태 폴더를 찾아 `ancestral`, `fb-schedule`, `pending` 이 있는지 보고, 있으면 첫 바이트를 헥스로 봅니다.
4. Google 계정이 추가된 시각과 주요 앱의 설치 시각을 한 표에 놓고, 복원으로 설치된 것처럼 보이는 앱 묶음이 있는지 봅니다.
5. `smartswitch_*` 키 값으로 삼성 스마트스위치로 옮긴 흔적과 구글 백업 복원을 나눠 적습니다.

## 참고 문헌

1. Back up user data — Android Developers. https://developer.android.com/identity/data/backup
2. Back up user data with Auto Backup — Android Developers. https://developer.android.com/identity/data/autobackup
3. Test backup and restore — Android Developers. https://developer.android.com/identity/data/testingbackup
4. Back up or restore data on your Android device — Android 도움말(Google). https://support.google.com/android/answer/2819582?hl=en
5. UserBackupManagerService.java — AOSP frameworks/base (main). https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/backup/java/com/android/server/backup/UserBackupManagerService.java
6. UserBackupManagerFiles.java — AOSP frameworks/base (main). https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/backup/java/com/android/server/backup/UserBackupManagerFiles.java
