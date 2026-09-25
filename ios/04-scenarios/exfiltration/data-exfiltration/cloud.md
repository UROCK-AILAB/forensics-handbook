---
title: "클라우드로"
parent: "자료를 밖으로 보냈나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 1570
---

# 클라우드로 (Cloud)

아이폰에서 클라우드 저장소로 자료를 올렸는지 가리는 페이지입니다. iCloud Drive, iCloud 사진, iCloud 백업의 세 갈래로 나눠 기기에 남는 흔적을 보고, 다른 회사 클라우드 앱은 연결 여부를 가늠하는 데까지 다룹니다. 다른 유출 경로와 전체 흐름은 허브 [자료를 밖으로 보냈나 (Data Exfiltration)](index.md) 에 있습니다.

## 조사 질문

"이 아이폰에서 클라우드로 올린 파일이 있는가, 그 파일을 다른 사람과 공유했는가" 를 묻습니다. 기기에는 동기화 대기열과 항목 목록, 공유 참여자 같은 기록이 남고, 클라우드 쪽 계정 기록은 [클라우드 데이터 (iCloud·계정 데이터 요청)](../../../03-techniques/acquisition/cloud-data.md) 절차로 따로 얻습니다.

## 먼저 확인할 것

iOS 버전과 시간대를 [기기 정보 (Device Info·Lockdown)](../../../02-artifacts/system-account/device-info.md), [시간대와 시각 설정 (Time Zone)](../../../02-artifacts/system-account/time-zone.md) 에서 확인하고, 기기에 로그인한 계정을 [애플 계정 (Apple Account)](../../../02-artifacts/system-account/apple-account.md) 에서 확인합니다. 파일 시스템 추출에서는 iCloud Drive 메타데이터 폴더가 `/private/var/mobile/Library/Application Support/CloudDocs/` 이고 그 아래 `session/db` 에 `client.db` 와 `server.db` 가 있으며, iCloud Drive 파일 자체는 `/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/` 에 있습니다[1]. 로컬 백업에서도 두 DB 가 `HomeDomain :: Library/Application Support/CloudDocs/session/db/` 아래에 보입니다(확인 범위: iOS 27.0).

[1] 은 iOS 13.7 에서 시험한 자료입니다. 아래 표 이름·칸 이름 가운데 "확인 범위" 가 붙은 것은 iOS 27.0 백업에서 본 것이고, 그 사이 버전에서 이름이 같은지는 확인하지 못했습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `client.db` 의 client_uploads·client_items 표 | 기기에서 iCloud Drive 로 올린 항목과 대기열 상태 | [아이클라우드 드라이브 (iCloud Drive)](../../../02-artifacts/mail-cloud/icloud-drive.md) |
| 2 | `server.db` 의 server_items·공유 참여자 표 | 서버 쪽 항목 목록과 공유 참여자 | [아이클라우드 드라이브 (iCloud Drive)](../../../02-artifacts/mail-cloud/icloud-drive.md) |
| 3 | 파일 앱 설정 plist | 파일 앱에 연결된 파일 공급자 목록 | [설정 값 (Preferences)](../../../02-artifacts/system-account/preferences.md) |
| 4 | `Photos.sqlite`·`syncstatus.plist` | iCloud 사진 동기화 상태, 공유 앨범·참여자 | [사진 보관함 (Photos Library)](../../../02-artifacts/media/photos/index.md) |
| 5 | 백업 설정 plist | iCloud 백업 사용 여부와 마지막 백업 기록 | [아이클라우드 백업 (iCloud Backup)](../../../01-foundations/backups/icloud-backup.md) |
| 6 | 다른 회사 클라우드 앱 DB | 앱마다 다름 | [구글 드라이브 (Google Drive)](../../../02-artifacts/mail-cloud/google-drive.md), [네이버 MYBOX (MYBOX)](../../../02-artifacts/mail-cloud/mybox.md) |

### iCloud Drive

파일 앱으로 iCloud Drive 에 올린 흔적은 `client.db` 의 client_uploads 표에서 찾습니다[1]. 관찰한 백업의 `client.db` 에는 client_items, client_uploads, client_downloads, client_sync_up, client_pkg_upload_items, client_zones, app_libraries, item_errors, item_recursive_properties, tombstones, boot_history 같은 표가 있습니다(확인 범위: iOS 27.0). 그중 유출과 관련된 칸은 아래와 같습니다(확인 범위: iOS 27.0).

| 표 | 칸 |
|---|---|
| client_uploads | throttle_id, zone_rowid, app_library_rowid, throttle_state, retry_count, last_try_stamp, next_retry_stamp, expire_stamp, transfer_queue, transfer_size, transfer_record, transfer_stage, transfer_operation, upload_error, upload_priority |
| client_items(일부) | item_id, item_filename, item_localname, item_parent_id, item_birthtime, item_sharing_options, item_state, item_type, item_lastusedtime, item_trash_put_back_path, version_mtime, version_size, version_device, version_uploaded_assets, version_upload_error, item_creator, version_edited_since_shared |
| item_recursive_properties(일부) | uploaded_size, uploaded_count, needs_upload_size, needs_upload_count, shared_by_me_count, shared_to_me_count |

`server.db` 에는 server_items, server_share_items_participants(item_id, zone_rowid, user_key, participant_flags), users(user_key, user_name, user_plist), devices(key, name), server_zones, server_boot_history 같은 표가 있고, server_items 에는 item_filename, item_origname, item_sharing_options, item_sharing_etag, version_size, version_mtime, version_device, shared_children_count, item_creator 칸이 있습니다(확인 범위: iOS 27.0). 공유한 항목의 참여자를 좇을 때는 server_share_items_participants 의 user_key 를 users 표에 잇고, 항목을 만든 기기를 좇을 때는 version_device 를 devices 표와 맞춰 봅니다. 두 연결은 칸 이름으로 짐작한 것이라서, 결과를 보고서에 쓰기 전에 실제 값이 서로 맞는지 확인합니다.

item_sharing_options 값이 공유 여부를 어떻게 나타내는지, item_birthtime·version_mtime·last_try_stamp 같은 시각 칸이 어떤 기준인지는 확인하지 못했습니다. 시각 칸은 [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md) 의 방법으로 후보 기준을 대 보고, 같은 파일의 다른 시각 기록과 맞는 기준을 고릅니다.

`account.1` 파일에는 iCloud Drive 계정의 DSID(숫자 식별자)가 있지만[1], 관찰한 백업에서는 이 파일을 보지 못했습니다(확인 범위: iOS 27.0).

### 파일 앱에 연결된 다른 공급자

`HomeDomain :: Library/Preferences/com.apple.DocumentManager.defaults.plist` 의 `DOCUserDefaultsCachedDisplayNamesBySourceIdentifier` 키에는 파일 앱이 기억하는 공급자 이름 목록이 있습니다(확인 범위: iOS 27.0). 관찰한 목록에는 iCloud Drive 공급자, 로컬 저장소, 공유 항목 같은 Apple 항목과 함께 가려진 다른 회사 앱 항목이 있었습니다.

```text
com.apple.CloudDocs.iCloudDriveFileProvider/<UUID>
com.apple.FileProvider.LocalStorage
com.apple.DocumentManager.SharedItems
```

이 목록으로 다른 회사 클라우드 앱이 파일 앱에 연결된 적이 있는지 가늠할 수는 있지만, 항목이 언제 생기고 지워지는지는 확인하지 못했습니다. iCloud Drive 공급자 설정은 `HomeDomain :: Library/Application Support/FileProvider/com.apple.CloudDocs.iCloudDriveFileProvider/Domains.plist` 에 있고 SupportsBackgroundUpload, Replicated, Path 같은 키가 들어 있습니다(확인 범위: iOS 27.0). 파일 앱의 `smartfolders.db`(filename, fp_folder_item, hotfolders 표)는 앱 그룹 컨테이너에 있고[1], 관찰한 백업에서는 보지 못했습니다. Dropbox 같은 다른 회사 파일 공급자의 오프라인 파일 식별자는 BASE64 로 인코딩되어 있어서[1], 디코딩한 뒤 읽습니다.

### iCloud 사진

`CameraRollDomain :: Media/PhotoData/CPL/syncstatus.plist` 에는 lastSyncDate, initialSyncDate, initialDownloadDate, iCloudLibraryExists, cloudAssetCountPerType, connectedToNetwork, inAirplaneMode 같은 키가 있습니다(확인 범위: iOS 27.0). iCloud 사진을 켜 둔 기기인지, 마지막으로 동기화한 때가 언제인지를 여기서 먼저 봅니다.

`CameraRollDomain :: Media/PhotoData/Photos.sqlite` 에는 업로드 작업 표 ZASSETRESOURCEUPLOADJOB(ZSTATE, ZTYPE, ZLASTMODIFIEDDATE, ZERRORDATA 등), ZASSETRESOURCEUPLOADJOBCONFIGURATION(ZBUNDLEIDENTIFIER, ZCOMPLETIONDATE 등), ZASSETRESOURCEUPLOADJOBREQUEST 가 있습니다(확인 범위: iOS 27.0). 이 표가 iCloud 업로드에 쓰이는지 다른 업로드에 쓰이는지는 확인하지 못했고, ZBUNDLEIDENTIFIER 로 어느 앱이 만든 작업인지를 보는 데까지만 씁니다.

공유 앨범과 공유 보관함은 ZSHARE, ZSHAREPARTICIPANT, ZSHAREPOST, ZCLOUDSHAREDALBUMINVITATIONRECORD, ZCLOUDFEEDENTRY 표에 남고, ZSHAREPARTICIPANT 에는 ZEMAILADDRESS, ZPHONENUMBER, ZACCEPTANCESTATUS, ZPARTICIPANTROLE 같은 칸이 있습니다(확인 범위: iOS 27.0). 사진 한 장 단위로는 ZADDITIONALASSETATTRIBUTES 표에 ZSHARECOUNT, ZPENDINGSHARECOUNT, ZSHARETYPE 칸이 있지만(확인 범위: iOS 27.0) 값의 뜻은 확인하지 못했습니다. 표 사이의 연결은 [사진 보관함 (Photos Library)](../../../02-artifacts/media/photos/index.md) 을 따릅니다.

### iCloud 백업

기기 전체를 iCloud 로 백업했는지는 `HomeDomain :: Library/Preferences/com.apple.mobile.ldbackup.plist` 의 CloudBackupEnabled, LastCloudBackupDate(정수), LastCloudBackupTZ, RequiresEncryption, WillEncrypt, Version 키에서 봅니다(확인 범위: iOS 27.0). `HomeDomain :: Library/Preferences/com.apple.MobileBackup.plist` 의 BackupStateInfo 에는 date, isCloud, state, progress, errors, backupAttemptCount 같은 하위 키가 있습니다(확인 범위: iOS 27.0). LastCloudBackupDate 값의 시각 기준은 확인하지 못했고, 옆에 있는 LastCloudBackupTZ 와 함께 적어 둡니다.

## 분석 흐름

1. iOS 버전·시간대·로그인 계정을 적고 조사 기간을 정합니다.
2. `client.db` 의 client_uploads 에서 transfer_size·retry_count·upload_error 칸을 보고, client_items 에서 item_filename·version_size 와 version_uploaded_assets·version_upload_error 칸을 함께 봅니다. 두 표를 잇는 칸은 확인하지 못해서, 파일 이름과 크기는 client_items 쪽에서 읽습니다.
3. item_recursive_properties 의 uploaded_count·shared_by_me_count 로 올린 항목과 내가 공유한 항목의 규모를 가늠합니다.
4. `server.db` 에서 같은 파일 이름의 server_items 행과 공유 참여자를 찾습니다.
5. 파일 앱 공급자 목록으로 다른 회사 클라우드 앱이 연결된 적이 있는지 보고, 있으면 그 앱의 아티팩트 페이지로 넘어갑니다.
6. 사진이 의심 자료이면 `syncstatus.plist` 와 `Photos.sqlite` 의 공유 표를 봅니다.
7. iCloud 백업 설정과 마지막 백업 시각을 적고, 필요하면 [클라우드 데이터 (iCloud·계정 데이터 요청)](../../../03-techniques/acquisition/cloud-data.md) 절차로 서버 쪽 기록을 요청합니다.
8. 찾은 시각을 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) 에 올리고 앱별 셀룰러 송신량([앱별 데이터 사용량 (DataUsage.sqlite)](../../../02-artifacts/network/data-usage.md))과 겹쳐 봅니다.

## 흔한 오판

iCloud Drive 폴더에 파일이 있다고 해서 사용자가 그 파일을 일부러 올렸다고 쓰지 않습니다. 파일이 동기화 대상에 들어 있었다는 사실과 사용자가 업로드 동작을 했다는 사실은 따로 입증합니다.

client_uploads 에 행이 없다고 올린 적이 없다고 판단하지 않습니다. 이 표가 업로드를 마친 뒤에도 행을 남기는지는 확인하지 못했고, 완료된 항목은 client_items 와 `server.db` 쪽에서 찾습니다.

iCloud 백업 설정 기록은 백업 기능을 쓴 흔적일 뿐, 특정 자료를 골라 보냈다는 근거가 되지 않습니다.

## 보고서 문장 예

> `client.db` 의 client_items 표에 파일 이름이 ○○이고 크기(version_size)가 ○○바이트인 항목이 있고, `server.db` 의 server_items 표에 같은 이름의 항목이 있습니다. 이 기록은 해당 파일이 이 기기의 iCloud Drive 동기화 대상에 들어 있었다는 사실을 보여 주며, 사용자가 업로드를 직접 실행했는지는 이 기록만으로 알 수 없습니다.

> `com.apple.mobile.ldbackup.plist` 의 CloudBackupEnabled 값이 참이고 LastCloudBackupDate 값이 ○○입니다. 이 값의 시각 기준은 확인하지 못해서 원래 값을 함께 적습니다.

## 함께 볼 페이지

- [아이클라우드 드라이브 (iCloud Drive)](../../../02-artifacts/mail-cloud/icloud-drive.md)
- [메신저로 (Messenger)](messenger.md), [메일로 (Email)](email.md), [에어드롭으로 (AirDrop)](airdrop.md), [PC 동기화로 (PC Sync)](pc-sync.md)
- [계정 탈취 흔적 (Account Takeover)](../../incident/account-takeover.md)
- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)

## 참고 문헌

1. D20 Forensics, "iOS - The Files App" — https://blog.d204n6.com/2020/09/ios-files-app.html
