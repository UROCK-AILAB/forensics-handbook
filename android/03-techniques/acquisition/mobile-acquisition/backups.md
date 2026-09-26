---
title: "백업으로 수집"
parent: "모바일 증거 확보"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1340
---

# 백업으로 수집 (Google 백업·Smart Switch)

기기를 직접 수집하기 어렵거나 기기 수집 결과를 보태야 할 때 백업이 무엇을 담고 무엇을 빼는지 정리합니다. Google 계정 백업, 앱 데이터 자동 백업, 삼성 Smart Switch 가 기기에 남기는 설정 키를 다룹니다.

## 한 줄 요약

백업은 Google 계정에 올리는 길과 기기에서 기기로 옮기는 길로 나뉘고, 앱이 두 길에 서로 다른 규칙을 줄 수 있어 백업에 무엇이 들었는지는 앱과 Android 버전에 따라 다르며, 백업에서 복원한 기기의 앱 데이터는 이전 기기에서 왔을 수 있습니다.

## 언제 쓰나

기기 자체를 수집할 수 없을 때, 기기에서 지워진 기록이 백업에 남아 있는지 볼 때, 복원한 기기의 데이터가 어디서 왔는지 판별할 때 씁니다. Google 계정 백업은 Google 계정에 저장되고 [1], 계정 쪽 데이터를 받는 방법은 [클라우드 데이터](../cloud-data.md) 페이지를 봅니다. 기기에 남은 Google 백업 흔적의 해석은 [구글 백업](../../../02-artifacts/mail-cloud/google-backup.md) 페이지에 있습니다.

## Google 계정 백업에 담기는 것

| 구분 | 항목 |
|---|---|
| 자동으로 담김 | 앱과 앱 데이터, 통화 기록, 연락처, 기기 설정, SMS·MMS [1] |
| Google 앱을 쓸 때 더 담김 | Google 메시지의 RCS 메시지, Google 전화의 전화 설정과 차단 번호, Google 포토의 사진·동영상 [1] |

일부 데이터는 기기 화면 잠금으로 한 번 더 암호화되지만, Google 포토의 사진·동영상과 통신사에서 받은 MMS 미디어는 화면 잠금으로 암호화되지 않습니다 [1]. 무엇이 백업되는지는 설정의 Google 서비스 → 백업 화면에 있는 "백업 세부정보" 에서 볼 수 있습니다 [1]. 삼성 기기에서는 메뉴 이름과 경로가 다를 수 있어 기기에서 확인합니다. 기기를 쓰지 않을 때 백업이 얼마 동안 남는지는 계정 쪽에서 확인합니다.

## 앱 데이터 자동 백업

자동 백업 (Auto Backup) 은 Android 6.0(API 23) 이상을 대상으로 하고 그 위에서 도는 앱이면 따로 설정하지 않아도 들어갑니다 [2]. 앱마다 사용자당 최대 25MB 를 사용자의 Google Drive 안 비공개 폴더에 저장하고, 이 용량은 개인 Drive 용량에 잡히지 않으며 사용자나 기기의 다른 앱은 이 백업을 읽을 수 없습니다 [2]. Android 9 이상에서는 사용자가 백업을 켜고 화면 잠금을 설정했을 때 기기 PIN·패턴·비밀번호로 종단간 암호화합니다 [2].

백업은 사용자가 백업을 켰고, 지난 백업 뒤 24시간 이상 지났고, 기기가 쉬고 있고, Wi-Fi 에 연결돼 있을 때 돕니다 [2]. 모바일 데이터 백업을 허용했다면 Wi-Fi 조건은 빠집니다 [2]. 그래서 백업 안의 앱 데이터는 수집 시점이 아니라 마지막 백업 시점의 상태입니다.

| 구분 | 앱 폴더 |
|---|---|
| 기본으로 포함 | shared preferences 파일, `getFilesDir()`·`getDir()` 의 파일, `getDatabasePath()` 의 파일(SQLiteOpenHelper 로 만든 DB 포함), 외부 저장소의 `getExternalFilesDir()` 폴더 [2] |
| 기본으로 제외 | `getCacheDir()`, `getCodeCacheDir()`, `getNoBackupFilesDir()` 의 파일 [2] |

앱은 `android:allowBackup="false"` 로 백업을 끌 수 있고, 무엇을 넣고 뺄지는 규칙 파일로 정합니다 [2]. 앱 폴더 구조는 [앱 데이터 폴더 구조](../../../01-foundations/storage/app-data-layout.md) 페이지에 있습니다.

| Android 버전 | 규칙 | 수집에 주는 영향 |
|---|---|---|
| 11 이하 | `android:fullBackupContent` [2] | 백업 규칙이 하나 |
| 12 이상 | `android:dataExtractionRules` 로 cloud-backup 과 device-transfer 규칙을 따로 둠 [2] | Google Drive 백업에서는 빠지고 기기 간 전송에서는 옮겨지는 파일이 있을 수 있음 [2] |
| 일부 제조사 기기 | `allowBackup=false` 가 Google Drive 백업만 끄고 기기 간(D2D) 전송은 끄지 않음 [3] | Drive 백업에 없는 앱 데이터가 기기 간 전송으로는 옮겨졌을 수 있음 |

복원은 Play 스토어, 기기 초기 설정, `adb install` 로 앱을 설치할 때 일어나고, APK 를 설치한 뒤 사용자가 앱을 열기 전에 데이터가 복원됩니다 [2]. 따라서 복원한 기기의 앱 데이터는 그 기기에서 처음 생긴 것이 아니라 이전 기기에서 온 것일 수 있습니다. adb 로 받는 백업은 [ADB로 볼 수 있는 것](adb.md) 페이지에 따로 정리했습니다.

## 기기에 남는 백업 관련 키

기기 설정에는 백업에 관련된 이름의 키가 아래처럼 있습니다. 각 값의 뜻과 시각 형식을 설명한 공개 자료가 없으니, 보고서에는 키가 있다는 사실까지만 씁니다.

| 어디서 | 키 이름 |
|---|---|
| settings secure | `backup_enabled`, `backup_auto_restore`, `backup_transport`, `backup_encryption_opt_in_displayed`, `backup_manager_constants`, `backup_enabled:com.android.calllogbackup`, `backup_enabled:com.android.providers.telephony`, `mms_backup_enabled`, `mms_backup_in_progress`, `mms_backup_last_completed`, `user_full_data_backup_aware` |
| settings global | `backup_agent_timeout_parameters` |

현행 AOSP 에서 설정을 백업하는 패키지 이름은 `com.android.providers.settings` 입니다 [4]. 설정 값을 읽는 법은 [설정 값](../../../02-artifacts/system-account/settings.md) 페이지에 있습니다.

## 삼성 Smart Switch

Smart Switch 가 어떤 데이터를 옮기는지, 무선·케이블·PC 중 어떤 방식으로 연결하는지, PC 백업을 어디에 어떤 형식으로 남기는지는 판마다 다를 수 있어 삼성 안내와 실제 기기로 확인합니다.

삼성 기기의 설정에는 Smart Switch 와 삼성 쪽 백업·복원에 관련된 이름의 키가 아래처럼 있습니다. 이름에서 뜻을 짐작할 수는 있지만 값의 뜻을 설명한 공개 자료가 없으니, 보고서에도 키가 있다는 사실까지만 씁니다.

| 어디서 | 키 이름 |
|---|---|
| settings global | `smartswitch_bnr_count`, `smartswitch_data_exist_samsungnote`, `smartswitch_data_exist_securefolder`, `smartswitch_transfer_completed`, `smartswitch_transfer_start_in_oobe`, `SecureWifiBackupExist` |
| settings secure | `IS_SMARTSWITCH_DATA_PRESENT`, `IS_SMARTSWITCH_RESTORE_IN_PROGRESS`, `wifi_ap_settings_cloud_backup_restoring`, `wifi_ap_settings_smart_switch_restoring` |

삼성 클라우드 앱의 흔적은 [삼성 클라우드와 원드라이브](../../../02-artifacts/mail-cloud/samsung-cloud-onedrive.md) 페이지에서 다룹니다.

## 함정과 한계

백업에 없는 앱 데이터를 두고 기기에 원래 없었다고 말할 수 없습니다. 앱이 백업을 껐거나 규칙으로 뺐을 수 있고, 캐시 폴더처럼 기본으로 빠지는 곳도 있으며, 앱마다 25MB 한도도 있습니다 [2]. Google Drive 백업과 기기 간 전송은 규칙이 다를 수 있어서 [2][3], 한쪽 결과로 다른 쪽을 짐작하지 않습니다. 종단간 암호화한 백업과 화면 잠금으로 한 번 더 암호화한 데이터는 [1][2], 계정 쪽에서 받더라도 내용을 읽을 수 있는지 따로 확인해야 합니다.

## 결과를 어떻게 해석하나

백업에서 나온 기록은 마지막 백업 시점까지의 상태이고, 복원한 기기에서 나온 앱 데이터는 이전 기기에서 만들어졌을 수 있습니다. 파일 시각이나 첫 기록 시각이 기기 개통보다 앞서면 복원을 먼저 의심하고, 기기 간 전송 관련 키가 있는지 함께 봅니다. 보고서에는 아래처럼 씁니다.

> 기기의 (앱) 데이터에 (시각) 의 기록이 있으나, 이 기기에는 백업·기기 간 전송과 관련된 설정 키가 있어 이 기록이 이 기기에서 만들어졌는지 다른 기기에서 복원됐는지는 이 자료만으로 가를 수 없습니다.

## 참고 문헌

1. Back up or restore data on your Android device — Google Android Help, https://support.google.com/android/answer/2819582?hl=en
2. Back up user data with Auto Backup — Android Developers, https://developer.android.com/identity/data/autobackup
3. Behavior changes: apps targeting Android 12 — Android Developers, https://developer.android.com/about/versions/12/behavior-changes-12
4. UserBackupManagerService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/backup/java/com/android/server/backup/UserBackupManagerService.java
