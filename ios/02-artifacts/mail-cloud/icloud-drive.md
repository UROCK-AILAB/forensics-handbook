---
title: "아이클라우드 드라이브"
parent: "아티팩트 · 메일·클라우드·애플 앱"
nav_order: 990
---

# 아이클라우드 드라이브 (iCloud Drive)

## 한 줄 요약

iCloud Drive 는 파일 자체를 `Library/Mobile Documents/com~apple~CloudDocs/` 에, 파일 목록과 올리고 내려받은 기록을 `Library/Application Support/CloudDocs/session/db/` 의 `client.db`·`server.db` 에 남기고, 로컬 백업에는 파일 없이 이 두 DB 와 설정 plist 가 들어갑니다.

## 무엇을 기록하나 · 왜 생기나

iCloud Drive 를 쓰면 기기에는 파일 본체와 함께 "어떤 파일이 서버에 있고, 어떤 파일을 기기에서 올리거나 내려받는 중인지" 를 적은 메타데이터 DB 가 따로 쌓입니다 [1]. `client.db` 의 `client_uploads` 표로 기기에서 올린 파일을 추적할 수 있고, `server.db` 에는 iCloud 에 올라간 파일과 관련 기기 정보가 들어 있습니다 [1]. 동기화하는 사용자의 DSID(숫자 식별자)는 `account.1` 파일에 남고 [1], 이 파일의 정확한 위치는 실제 데이터에서 찾습니다.

기기에 내려받은 파일은 보통 파일로 있고, 내려받지 않은(온라인 전용) 파일은 확장자 `.iCloud` 가 붙은 숨은 plist 파일로 있으며, 이 plist 에 원래 파일의 이름과 크기가 들어 있습니다 [1]. 그래서 기기에 내용이 없는 파일도 이름과 크기는 확인할 수 있습니다.

파일 앱에서 지운 파일 가운데 iCloud Drive 에서 지운 것만 "최근 삭제된 항목" 으로 가고, "나의 iPhone" 에서 지운 파일은 그리로 가지 않습니다 [1]. 이 동작은 iOS 13.7 기준이고 [1], iOS 15 이후 판에서는 실제 데이터로 확인합니다.

iCloud Drive 는 표준 보호에서 전송 중과 서버 저장 시 암호화하고 키를 Apple 이 보관하며, 고급 데이터 보호를 켜면 종단 간 암호화로 바뀌어 키가 사용자의 신뢰하는 기기에만 있습니다 [2]. iCloud 백업은 이미 iCloud 로 동기화되는 iCloud Drive 데이터를 백업에 넣지 않습니다 [3]. 서버 쪽 자료 확보는 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 에서 다룹니다.

## 위치와 버전별 차이

| 무엇 | 위치 | 확인 정도 |
|---|---|---|
| 파일 본체 | 기기 `/private/var/mobile/Library/Mobile Documents/com~apple~CloudDocs/` | [1] (iOS 13.7) |
| 메타데이터 DB | `HomeDomain :: Library/Application Support/CloudDocs/session/db/client.db`, `server.db` | [1] |
| 앱별 iCloud 컨테이너 정보 | `HomeDomain :: Library/Application Support/CloudDocs/session/containers/*.plist` | — |
| 서버 설정 | `HomeDomain :: Library/Application Support/CloudDocs/server-conflig.plist` (파일 이름 철자 그대로) | — |
| 파일 공급자 도메인 | `HomeDomain :: Library/Application Support/FileProvider/com.apple.CloudDocs.iCloudDriveFileProvider/Domains.plist` | — |
| 설정 | `HomeDomain :: Library/Preferences/com.apple.bird.plist`, `com.apple.fileproviderd.plist` | — |

iOS 27.0 로컬 백업에는 `Library/Mobile Documents/com~apple~CloudDocs/` 아래 파일이 들어가지 않고, `Mobile Documents` 쪽에는 `com~apple~shoebox/UbiquitousCards/CatalogOfRecord.plist` 하나만 들어갑니다. 파일 본체가 필요하면 파일 시스템 전체 수집이나 계정 쪽 자료를 검토하고, 수집 방식은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에 있습니다.

관련 백업 도메인은 `AppDomainPlugin-com.apple.CloudDocs.iCloudDriveFileProvider`, `AppDomainPlugin-com.apple.CloudDocs.iCloudDriveFileProviderManaged`, `AppDomainPlugin-com.apple.CloudDocs.MobileDocumentsFileProviderUI`, `AppDomainPlugin-com.apple.CloudDocsUI.CloudSharing`, `AppDomainPlugin-com.apple.CloudDocsUI.DocumentPicker`, `AppDomainGroup-group.com.apple.FileProvider.LocalStorage` 입니다.

| iOS | 내용 | 근거 |
|---|---|---|
| 13.7 | 파일 위치, `client.db`·`server.db`, `.iCloud` 자리표시 파일, 최근 삭제된 항목 동작 | [1] |
| 15~26 | 공개 자료 없음, 실제 데이터로 확인 | — |
| 27.0 | 두 DB 의 표·열 이름, 설정 plist 키 이름 | — |

## 구조

### client.db

`client.db` 에는 아래 표가 있습니다(iOS 27.0).

```
client_items, client_uploads, client_downloads, client_sync_up, client_unapplied_table,
client_pkg_upload_items, client_pkg_upload_sizes, client_zones, client_state,
app_libraries, item_errors, item_recursive_properties, tombstones, boot_history,
backup_detector, aggregated_daily_telemetry, named_throttles_history,
telemetry_failure_counts, fpfs_folders_not_migrated, completed_db_fixups, os_names
```

기기 쪽 파일 목록은 `client_items` 에 있고, 분석에 쓸 만한 열은 아래와 같습니다.

```
client_items (일부)
item_id, item_parent_id, item_filename, item_localname, item_type, item_mode, item_state,
item_birthtime, item_lastusedtime, item_creator_id, item_creator, item_favoriterank,
item_finder_tags, item_user_visible, item_hidden_ext,
item_trash_put_back_parent_id, item_trash_put_back_path,
version_mtime, version_name, version_size, version_device,
version_quarantine_info, version_upload_error, app_library_rowid, zone_rowid
```

`item_id` 와 `item_parent_id` 를 이으면 폴더 구조를 되살릴 수 있고, `app_library_rowid`·`zone_rowid` 로 `app_libraries`·`client_zones` 표와 이어 어느 앱 영역의 파일인지 봅니다. `item_type` 값이 파일과 폴더를 어떻게 나누는지는 실제 데이터로 확인합니다.

올리기와 내려받기 대기열은 `client_uploads`·`client_downloads` 에 있고, 두 표에는 `transfer_size`, `transfer_stage`, `last_try_stamp`, `next_retry_stamp`, `expire_stamp` 열이, 각각 `upload_error`·`download_error` 열이, `client_downloads` 에는 `download_request_stamp` 열이 더 있습니다. 동기화 실패는 `item_errors` 의 `error_domain`, `error_code`, `error_message`, `error_timestamp` 열에 남고, `boot_history` 에는 `date`, `os`, `br`, `bird_schema`, `db_schema`, `device_id` 열이 있습니다. `boot_history` 의 `os` 열은 이름으로 보면 OS 버전을 적은 것 같습니다.

### server.db

`server.db` 에는 `server_items`, `server_zones`, `server_share_items_participants`, `server_state`, `server_boot_history`, `devices`, `users`, `side_car_lookahead`, `rowid_reservations`, `completed_db_fixups` 표가 있습니다.

```
server_items (일부)
item_id, item_parent_id, item_filename, item_origname, item_birthtime, item_creator,
item_lastusedtime, item_trash_put_back_path, version_mtime, version_size,
version_device, quota_used
devices: key, name
users: user_key, user_name, user_plist
```

`server_items` 는 서버에 있는 파일 목록이고 [1], `devices` 표의 `name` 과 `version_device` 열을 이으면 어느 기기가 그 판을 만들었는지 짐작할 수 있지만, 두 열을 잇는 방법은 이름에서 나온 추정이라서 실제 데이터에서 값을 보고 확인합니다. 공유 폴더의 참여자는 `server_share_items_participants` 와 `users` 를 `user_key` 로 이어 봅니다.

휴지통과 관련된 열(`item_trash_put_back_parent_id`, `item_trash_put_back_path`)이 `client_items` 와 `server_items` 양쪽에 있습니다. 이름으로는 휴지통으로 옮긴 항목의 원래 위치로 보입니다.

### 파일 공급자 도메인과 설정 plist

iCloud Drive 가 파일 앱에 등록한 도메인은 아래처럼 남습니다.

```
HomeDomain :: Library/Application Support/FileProvider/com.apple.CloudDocs.iCloudDriveFileProvider/Domains.plist
<UUID>: {Connected, DisplayName, Enabled, Hidden, Path, Replicated, SpotlightDomain,
         SupportsBackgroundUpload, SupportsRemoteVersions, SupportsSearch,
         SupportsStringSearchRequest, SupportsSyncingTrash, UserInfo}
NSFileProviderDomainDefaultIdentifier: {Connected, Enabled}
```

이름으로 보면 `Enabled`·`Connected` 값은 수집 시점에 iCloud Drive 가 파일 앱에 연결되어 켜져 있었는지를 판단하는 단서입니다. 같은 `FileProvider` 폴더의 `backup/backup_manifest.db`, `<UUID>/wharf/wharf/directoryManifest/manifest.db`, `speculative-set-pacer.plist` 는 어느 공급자 것인지 파일 이름만으로 알 수 없고, 구조는 [구글 드라이브](google-drive.md) 에 있습니다.

`session/containers/` 에는 앱별 iCloud 컨테이너 plist 가 많고, 파일 이름은 `<팀ID>.<번들ID>.plist` 또는 `com.apple.*.plist` 형식이며 키는 `BRContainerName`, `BRContainerDocumentTypes`, `BRContainerVersionNumber` 같은 `BRContainer` 계열입니다. 이 목록으로 iCloud Drive 를 쓰는 앱이 무엇인지 짐작할 수 있지만, 이 목록만으로 앱이 설치되어 있었다거나 실제로 썼다고 말하지는 않습니다.

설정 plist 가운데 `com.apple.bird.plist` 에는 `optimize-storage`(bool), `didDropCoreSpotlightIndex`(bool), `CKStartupTime`(int)이, `com.apple.fileproviderd.plist` 에는 `LocalStorageStubDomainEnabled`(bool), `iCDPackageExtensions`(list)가, `server-conflig.plist` 에는 `etag`, `default`, `com.apple.CloudDocs.recovery` 같은 키가 있습니다. `bird` 는 iCloud Drive 데몬 이름으로 알려져 있고, `optimize-storage` 는 이름으로 보면 "iPhone 저장 공간 최적화" 설정과 이어질 가능성이 있습니다.

## 증거로서 의미

### 증명하는 것

`client_items`·`server_items` 의 행은 수집 시점에 그 이름·크기의 파일이 iCloud Drive 에 있었다는 기록이고, 기기에 본체가 없어도 `.iCloud` 자리표시 파일이 있으면 이름과 크기를 확인할 수 있습니다 [1]. `client_uploads` 의 행은 기기가 그 파일을 올리려 한 기록이고 [1], `item_errors` 의 행은 동기화가 실패한 기록입니다. `Domains.plist` 는 iCloud Drive 가 파일 앱에 연결되어 있었는지를 보여 줍니다.

### 증명하지 못하는 것

iCloud Drive 목록에 있는 파일이 이 기기에서 만들어졌다고 바로 말할 수 없고, 같은 계정을 다른 기기나 웹에서도 썼다면 그쪽에서 올린 파일일 수 있습니다. 올리기 대기열에 행이 있다고 올리기가 끝났다는 뜻은 아니고, 행이 없다고 올린 적이 없다는 뜻도 아닙니다. "나의 iPhone" 에서 지운 파일은 최근 삭제된 항목에 남지 않아서 [1], 그 폴더가 비어 있다고 지운 파일이 없었다고 쓰지 않습니다.

보고서에는 "파일을 iCloud 로 빼돌렸다" 대신 "수집 시점에 iCloud Drive 목록에 이 이름·크기의 파일이 있고, 기기의 올리기 기록에 이 항목이 있다" 처럼 씁니다.

## 시각 해석

`item_birthtime`, `version_mtime`, `item_lastusedtime`, `*_stamp`, `error_timestamp` 열의 시각 기준(Unix 초, Mac 절대 시각, 나노초 등)은 공개 자료가 없습니다. 실제 데이터에서는 열마다 자릿수를 보고 여러 기준으로 바꿔 본 뒤, 파일 앱에 보이는 수정 날짜나 [KnowledgeC](../app-usage/knowledgec/index.md) 의 앱 사용 시각과 비교해 기준을 정합니다. 변환 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

이름만 보면 `item_birthtime` 은 파일을 만든 시각, `version_mtime` 은 그 판을 고친 시각, `item_lastusedtime` 은 마지막으로 연 시각처럼 보이지만, 무엇이 바뀔 때 각 열이 바뀌는지는 공개 자료가 없습니다. 시험 기기에서 파일을 만들고, 고치고, 열어 본 뒤 열 값이 어떻게 바뀌는지 보고 나서 보고서에 씁니다.

## 함정과 한계

열의 뜻과 동작은 iOS 13.7 기준으로 알려져 있고 [1], iOS 27.0 에서 알려진 것은 표 이름뿐입니다. 그 사이 버전에서 무엇이 바뀌었는지는 공개 자료가 없어서, 버전이 다른 기기에서는 표 목록부터 새로 뽑아 봅니다.

두 DB 는 수집 시점의 상태를 적은 것이라서, 지운 파일의 행은 없어졌을 수 있습니다. `tombstones` 표나 SQLite 의 빈 페이지·`-wal` 파일에 흔적이 남는지는 공개 자료가 없고, 찾아보는 방법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 있습니다.

iCloud 백업에는 iCloud Drive 파일이 들어가지 않아서 [3], iCloud 백업만 받았다면 iCloud Drive 파일은 따로 확보해야 합니다. 고급 데이터 보호가 켜진 계정은 iCloud Drive 데이터가 종단 간 암호화되어 있고 [2], 계정 쪽 자료 요청 절차는 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 에서 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

`.iCloud` 자리표시 파일은 plist 라서 [1], 바이너리 plist 라면 맨 앞 8바이트가 `bplist00` 입니다. 아래는 plist 형식으로 만든 예시이고 실제 데이터에서 나온 값이 아닙니다.

```
00000000  62 70 6C 69 73 74 30 30  ...                      bplist00...
```

`<?xml` 로 시작하면 XML plist 로 읽습니다. 이 plist 안에서 원래 파일 이름과 크기를 찾는 방법, 객체 표와 오프셋을 따라가는 방법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에 있습니다.

### 공개 도구로 한 번

1. 로컬 백업이라면 `Manifest.db` 에서 두 DB 와 곁가지 파일을 찾아 함께 복사합니다.

   ```sql
   SELECT fileID, relativePath FROM Files
   WHERE domain = 'HomeDomain'
     AND relativePath LIKE 'Library/Application Support/CloudDocs/session/db/%';
   ```

2. `client.db` 를 sqlite3 로 열어 파일 목록과 올리기 대기열을 봅니다. 시각 열은 기준을 확인하기 전까지 원래 값 그대로 둡니다.

   ```sql
   SELECT item_id, item_parent_id, item_filename, version_size,
          item_birthtime, version_mtime, item_lastusedtime, version_device
   FROM client_items;
   SELECT throttle_id, transfer_size, transfer_stage, last_try_stamp, upload_error
   FROM client_uploads;
   ```

   `client_uploads` 의 행이 `client_items` 의 어느 열과 이어지는지는 공개 자료가 없습니다. 두 표를 따로 읽고, 값의 모양을 보고 잇는 열을 찾습니다.

3. `server.db` 에서 서버 쪽 목록과 기기 이름을 봅니다.

   ```sql
   SELECT item_filename, item_origname, version_size, version_device FROM server_items;
   SELECT key, name FROM devices;
   ```

4. `Domains.plist` 와 설정 plist 는 Python `plistlib` 으로 열어 키 값을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [애플 계정](../system-account/apple-account.md) | 동기화한 Apple 계정 |
| [앱별 데이터 사용량](../network/data-usage.md) | 올리기 무렵 주고받은 데이터 양 |
| [KnowledgeC](../app-usage/knowledgec/index.md)·[바이옴](../app-usage/biome/index.md) | 파일 앱을 앞에 띄워 쓴 시각 |
| [문서 메타데이터](../embedded-metadata/documents.md) | 파일 안에 적힌 작성자·작성 시각 |
| [메모](notes.md) | 같은 iCloud 계정으로 동기화한 다른 데이터 |
| [구글 드라이브](google-drive.md) | 같은 파일 공급자 구조를 쓰는 다른 회사 앱 |
| [아이클라우드 백업](../../01-foundations/backups/icloud-backup.md) | iCloud 백업에 들어가는 것과 빠지는 것 |

자료 유출을 의심하는 사건이라면 [자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에서, 지운 파일을 찾는 사건이라면 [지운 대화와 사진 찾기](../../04-scenarios/activity/deleted-content.md) 에서 이 흔적을 어떤 순서로 맞추는지 봅니다.

## 실습

NIST CFReDS 같은 공개 시험 이미지 가운데 iCloud Drive 를 쓴 iOS 이미지가 있는지 먼저 확인하고, 있으면 아래 질문을 풀어 봅니다.

1. `client.db` 와 `server.db` 의 표 목록을 뽑아 위 표 목록과 비교하고, 없는 표와 새로 생긴 표를 적습니다.
2. `client_items` 에서 `item_parent_id` 를 따라 폴더 구조를 되살리고, 가장 깊은 폴더가 몇 단계인지 셉니다.
3. `item_birthtime` 값 하나를 Unix 초와 Mac 절대 시각 두 가지로 바꿔 보고, 어느 쪽이 그럴듯한 날짜인지 판단합니다.
4. `server_items` 에만 있고 `client_items` 에는 없는 파일 이름이 있는지 찾습니다.
5. 파일 시스템 전체 수집본이라면 `Mobile Documents/com~apple~CloudDocs/` 에서 `.iCloud` 파일을 찾아 plist 안의 이름·크기를 `server_items` 의 값과 비교합니다.

## 참고 문헌

1. D20 Forensics, "iOS - The Files App" — https://blog.d204n6.com/2020/09/ios-files-app.html
2. Apple 지원 102651, "iCloud data security overview" — https://support.apple.com/en-us/102651
3. Apple 지원 108770, "What does iCloud back up?" — https://support.apple.com/en-us/108770
