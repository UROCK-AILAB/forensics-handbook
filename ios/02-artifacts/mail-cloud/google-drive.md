---
title: "구글 드라이브"
parent: "아티팩트 · 메일·클라우드·애플 앱"
nav_order: 1020
---

# 구글 드라이브 (Google Drive)

## 한 줄 요약

아이폰의 구글 드라이브 앱은 앱 안의 저장 구조가 공개 자료로 확인되지 않아서, 로컬 백업에서 앱이 있는지 확인한 뒤 Files 앱 쪽 흔적과 다른 사용 기록을 맞춰 보는 방식으로 분석합니다.

## 무엇을 기록하나 · 왜 생기나

구글 드라이브는 Google LLC 가 내는 클라우드 저장 앱이고, App Store 설명에 따르면 오프라인으로 보기, 카메라로 종이 문서를 스캔해 올리기, 파일·폴더에 권한을 정해 공유하기, 100가지가 넘는 파일 형식 저장·편집을 지원합니다 [4]. 오프라인 보기와 스캔은 기기 안에 파일을 두거나 기기에서 파일을 만드는 기능이라서 앱 컨테이너 안에 파일 목록이나 내려받은 파일이 남을 수 있지만, 그 파일 이름과 DB 구조는 공개 출처에서 확인하지 못했습니다. 그래서 앱 내부 구조는 검체에서 직접 확인할 항목으로 남기고, 여기서는 확인된 흔적을 중심으로 설명합니다.

App Store 개인정보 라벨에는 사용자와 연결된 데이터로 구입 항목, 위치, 연락처 정보, 연락처, 사용자 콘텐츠(사진·비디오·오디오), 검색 기록, 식별자, 사용 데이터, 진단이 적혀 있습니다 [4]. 이 라벨은 개발사가 수집해 처리하는 데이터 종류를 밝힌 것이고, 기기 안에 그 데이터가 남는다는 뜻은 아닙니다.

또 하나 볼 곳은 Files 앱입니다. iOS 의 파일 공급자 확장(File Provider extension)은 내용을 도메인(NSFileProviderDomain) 단위로 나누고, 도메인 하나는 계정 하나나 위치 하나를 나타낼 수 있습니다 [2]. NSFileProviderDomain 은 iOS 11.0 부터 있고, 도메인마다 identifier(고유 식별자), displayName(화면에 보이는 이름), isHidden(사용자에게 보이는지), isDisconnected(도메인은 있지만 확장과 연결이 끊겼는지), userEnabled(사용자가 켰는지 껐는지), isReplicated, supportsSyncingTrash, backingStoreIdentity, userInfo 속성이 붙습니다 [2]. 다른 회사 앱이 파일 공급자 도메인을 등록하면 로컬 백업의 `HomeDomain` 안 `Library/Application Support/FileProvider/` 아래에 앱별 폴더가 생기고 그 안에 `Domains.plist` 가 남습니다(확인 범위: iPhone 13 mini, iOS 27.0). 다만 이번 관찰에서는 다른 회사 앱 이름을 가렸기 때문에, 이 자리에 남은 앱이 구글 드라이브인지는 확인하지 않았습니다.

## 위치와 버전별 차이

| 무엇 | 위치 | 확인 정도 |
|---|---|---|
| 앱 설치 여부와 번들 ID | 백업 최상위 `Info.plist` 의 `Installed Applications`·`Applications` 키, `Manifest.plist` 의 `Applications` 키, `Manifest.db` 의 도메인 이름 | 키 이름 관찰(확인 범위: iPhone 13 mini, iOS 27.0) |
| 앱 컨테이너 안의 메타데이터 DB·캐시·오프라인 파일 | 앱 도메인(`AppDomain-` 로 시작) 안 | 확인 못 함, 검체에서 직접 확인 |
| 파일 공급자 도메인 설정 | `HomeDomain :: Library/Application Support/FileProvider/<앱>/Domains.plist` | 관찰(확인 범위: iPhone 13 mini, iOS 27.0), 어느 앱인지는 가림 |
| Files 앱 설정 | `HomeDomain :: Library/Preferences/com.apple.DocumentManager.defaults.plist` | 관찰(확인 범위: iPhone 13 mini, iOS 27.0) |
| 파일 공급자 작업 자료 | `HomeDomain :: Library/Application Support/FileProvider/<UUID>/wharf/...`, `.../FileProvider/backup/backup_manifest.db` | 관찰(확인 범위: iPhone 13 mini, iOS 27.0), 어느 공급자 것인지 확인 못 함 |

버전에 따라 확인한 내용은 아래와 같습니다.

| 항목 | 내용 | 근거 |
|---|---|---|
| 앱이 요구하는 최소 iOS | iOS 17.0 이상(2026-09 조회 시점) | [4] |
| 조회 시점 앱 버전 | 4.2638.41000 | [4] |
| NSFileProviderDomain | iOS 11.0 부터 | [2] |
| Files 앱 쪽 흔적 | iOS 27.0 에서 관찰 | 확인 범위: iPhone 13 mini, iOS 27.0 |

지금 App Store 버전은 iOS 17.0 이상을 요구하므로 iOS 15·16 기기에서 발견한 앱은 그보다 예전 버전일 수 있고, 예전 버전의 저장 구조도 확인하지 못했습니다.

## 구조

### 앱이 있는지 확인하기

로컬 백업의 `Manifest.db` 에는 아래 표가 있습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
CREATE TABLE Files (fileID TEXT PRIMARY KEY, domain TEXT, relativePath TEXT, flags INTEGER, file BLOB)
CREATE TABLE Properties (key TEXT PRIMARY KEY, value BLOB)
```

도메인 이름은 `AppDomain-`, `AppDomainGroup-`, `AppDomainPlugin-` 뒤에 번들 ID 나 앱 그룹 이름을 붙인 꼴입니다. 관찰한 백업에는 도메인이 1428개 있었고 그중 다른 회사 앱 161개는 메모에서 이름을 가렸기 때문에, 구글 드라이브 앱 도메인의 존재와 내용은 관찰하지 않았습니다(확인 범위: iPhone 13 mini, iOS 27.0). 검체에서는 `Info.plist` 의 설치 앱 목록에서 번들 ID 를 먼저 찾고, 그 번들 ID 가 들어간 도메인을 `Manifest.db` 에서 찾습니다. 번들 ID 와 앱 그룹을 읽는 법은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에, 백업 폴더와 `fileID` 의 관계는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에 있습니다.

### 파일 공급자 도메인 설정 (Domains.plist)

다른 회사 앱의 폴더에서 관찰한 `Domains.plist` 에는 기본 도메인 항목 하나만 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
HomeDomain :: Library/Application Support/FileProvider/<앱>/Domains.plist
NSFileProviderDomainDefaultIdentifier: {Connected, Enabled}
```

같은 폴더 구조를 쓰는 iCloud Drive 의 `Domains.plist` 에는 도메인 항목이 따로 있고, 그 항목의 키는 아래와 같습니다(확인 범위: iPhone 13 mini, iOS 27.0). iCloud Drive 쪽 해석은 [아이클라우드 드라이브](icloud-drive.md) 에서 다룹니다.

```
Connected, DisplayName, Enabled, Hidden, Path, Replicated, SpotlightDomain,
SupportsBackgroundUpload, SupportsRemoteVersions, SupportsSearch,
SupportsStringSearchRequest, SupportsSyncingTrash, UserInfo
```

키 이름을 NSFileProviderDomain 속성과 견주면 DisplayName 은 displayName, Hidden 은 isHidden, Enabled 는 userEnabled, Replicated 는 isReplicated, SupportsSyncingTrash 는 supportsSyncingTrash, UserInfo 는 userInfo 와 짝이 맞아 보입니다. 이 짝은 이름만 비교한 추정이라서 보고서에 쓰려면 검체에서 값을 보고 다시 확인해야 합니다. 다른 회사 앱의 `Domains.plist` 에 계정별 도메인 항목(DisplayName 등)이 남는지도 이번 기기에서는 기본 항목만 보여 확인하지 못했습니다.

### Files 앱 설정 (com.apple.DocumentManager.defaults.plist)

Files 앱 설정 파일에서 공급자와 관련된 키는 아래와 같습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
HomeDomain :: Library/Preferences/com.apple.DocumentManager.defaults.plist
DOCUserDefaultsCachedDisplayNamesBySourceIdentifier: {<앱>, com.apple.CloudDocs.iCloudDriveFileProvider/<UUID>,
    com.apple.DocumentManager.RecentDocuments, com.apple.DocumentManager.SharedItems,
    com.apple.DocumentManager.TrashedItems, com.apple.FileProvider.LocalStorage, ...}
DOCSourceOrderKey (list)
DOCDefaultFileProviderAutomaticKey (list)
DOCDefaultFileProviderIdentifierKey
```

`DOCUserDefaultsCachedDisplayNamesBySourceIdentifier` 안에는 iCloud Drive·최근 항목·공유 항목·휴지통 같은 Apple 쪽 위치와 함께 다른 회사 앱 항목이 섞여 있습니다. 다른 회사 앱 항목이 Files 앱에 연결된 저장소 공급자의 이름을 담아 둔 캐시라는 해석은 이름에서 나온 추정이고, 확인하지 못했습니다.

### 파일 공급자 작업 자료

`HomeDomain` 의 `FileProvider` 폴더 아래에는 아래 DB 와 plist 도 있습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
Library/Application Support/FileProvider/backup/backup_manifest.db
  backup_manifest: relative_path, file_id, doc_id, gen_count, new_file_id, new_doc_id, new_gen_count

Library/Application Support/FileProvider/<UUID>/wharf/wharf/directoryManifest/manifest.db
  manifest: destination_parent_id, destination_id, source_id, source_parent_id, data
  state: rowid, db_uuid

Library/Application Support/FileProvider/<UUID>/wharf/wharf/resources/speculative-set-pacer.plist
  needsRefresh, lastRefreshDate, totalDownloadCount, lastTotalDownloadResetDate,
  lastIndexingBarrier, indexAllStartDate, indexableTypesAge,
  indexableConfigurationStartDate, dailyDownloads, dailyPreventDownloadReasons
```

이 자료가 iCloud Drive 것인지 다른 회사 공급자 것인지는 확인하지 못했습니다. 구글 드라이브 흔적으로 쓰려면 `<UUID>` 폴더가 어느 도메인과 이어지는지 검체에서 먼저 밝혀야 합니다.

## 증거로서 의미

### 증명하는 것

백업의 설치 앱 목록과 앱 도메인에 구글 드라이브가 있으면, 백업을 만든 시점에 그 앱이 기기에 설치되어 있었다는 기록이 됩니다. 앱 컨테이너 안에서 파일 목록이나 내려받은 파일을 찾으면 그 파일이 앱을 거쳐 기기에 있었다는 기록이 되지만, 그 파일이 어떤 동작(열기·내려받기·스캔)으로 생겼는지는 해당 구조를 검체에서 밝힌 뒤에 말할 수 있습니다. 파일 공급자 도메인 항목이 구글 드라이브 것으로 확인되면 Files 앱에서 그 위치를 쓸 수 있게 연결되어 있었다고 말할 수 있습니다.

### 증명하지 못하는 것

앱이 설치되어 있다는 사실만으로는 파일을 올렸거나 공유했다고 말할 수 없습니다. 개인정보 라벨에 적힌 데이터 종류는 기기 안의 기록이 아니라서 증거로 쓰지 않습니다. `Domains.plist` 의 기본 항목(`NSFileProviderDomainDefaultIdentifier`)만으로는 어떤 계정이 연결되었는지 알 수 없습니다. 기기에서 찾지 못한 파일이 드라이브에도 없었다고 쓰지 않습니다.

보고서에는 "구글 드라이브로 자료를 올렸다" 대신 "백업 시점에 구글 드라이브 앱이 설치되어 있었고, 앱 영역에 이런 파일이 남아 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

앱이 내부에 시각을 어떤 형식(Unix 시각, Mac 절대 시각 등)으로 저장하는지는 확인하지 못했습니다. 검체에서 시각으로 보이는 숫자를 찾으면 자릿수와 기준 시점을 여러 형식으로 바꿔 보고, 앱에서 실제로 한 동작의 시각과 견주어 형식을 정합니다. 형식별 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

파일 공급자 쪽 `speculative-set-pacer.plist` 에서는 `lastRefreshDate`·`lastTotalDownloadResetDate` 가 정수로, `indexAllStartDate`·`indexableConfigurationStartDate` 가 날짜 형식으로 저장되어 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0). 값은 읽지 않아서 정수 쪽의 기준 시점은 확인하지 못했고, 이 파일이 어느 공급자 것인지도 모르기 때문에 구글 드라이브 사용 시각으로 바로 쓰지 않습니다.

## 함정과 한계

Windows 용 구글 드라이브의 흔적(`AppData\Local\Google\Drive` 아래 sync_config.db, snapshot.db, cloud_graph.db 등)은 iOS 와 구조가 달라서, 같은 파일 이름을 아이폰에서 찾으면 안 됩니다 [1].

공개 iOS 포렌식 참고 목록(RealityNet iOS-Forensics-References, 2023-04 갱신 기준)에는 구글 드라이브나 다른 회사 클라우드 앱 항목이 없습니다 [3]. 분석 도구에 이 앱을 읽는 기능이 없을 수 있고, 도구가 아무것도 보여 주지 않는다고 기록이 없는 것은 아닙니다. 도구 결과를 믿기 전에 [도구 검증](../../03-techniques/reporting/tool-validation.md) 방식으로 확인합니다.

이번 관찰에서는 다른 회사 앱 이름을 모두 가렸기 때문에, 이 페이지의 파일 공급자 쪽 설명은 모두 "다른 회사 앱 일반" 에 대한 관찰입니다. 구글 드라이브가 파일 공급자 도메인을 어떤 이름으로 등록하는지, 로컬 백업에 앱 영역의 어떤 파일이 들어가는지는 검체에서 직접 확인해야 합니다.

## 직접 분석해 보기

### 헥스로 한 번

plist 는 XML 로도, 바이너리로도 저장됩니다. 바이너리 plist 는 파일 맨 앞 8바이트가 `bplist00` 이라서 헥스 편집기로 열면 아래처럼 보입니다. 아래는 명세로 만든 예시이고 검체에서 나온 값이 아닙니다.

```
00000000  62 70 6C 69 73 74 30 30  ...                      bplist00...
```

`Domains.plist` 나 `com.apple.DocumentManager.defaults.plist` 를 꺼냈을 때 이 머리말이 보이면 바이너리 plist 로 읽고, `<?xml` 로 시작하면 XML 로 읽습니다. 오프셋 표와 객체 구조는 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 따라갑니다.

### 공개 도구로 한 번

1. 백업의 `Manifest.db` 를 사본으로 떠서 sqlite3 로 엽니다. 파일 공급자 도메인 설정과 Files 앱 설정의 `fileID` 를 찾습니다.

   ```sql
   SELECT fileID, domain, relativePath FROM Files
   WHERE domain = 'HomeDomain'
     AND (relativePath LIKE 'Library/Application Support/FileProvider/%/Domains.plist'
          OR relativePath = 'Library/Preferences/com.apple.DocumentManager.defaults.plist');
   ```

2. 설치 앱 목록에서 확인한 번들 ID 로 앱 도메인과 파일 수를 봅니다(`번들ID` 자리에 실제 값을 넣습니다).

   ```sql
   SELECT domain, COUNT(*) FROM Files
   WHERE domain LIKE 'AppDomain%번들ID%' GROUP BY domain;
   ```

3. 찾은 plist 를 Python 표준 라이브러리로 읽어 키와 값을 봅니다.

   ```python
   import plistlib
   with open("Domains.plist", "rb") as f:
       for k, v in plistlib.load(f).items():
           print(k, v)
   ```

4. 앱 도메인 안의 SQLite·plist 파일은 이름을 모르는 상태에서 시작하므로, 파일 머리말로 형식을 가른 뒤 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md) 절차로 표와 칸의 뜻을 밝힙니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [설치된 앱](../app-usage/installed-apps.md) | 앱이 설치되어 있었는지 |
| [앱 스토어 기록](../app-usage/app-store.md) | 앱을 언제 받았는지 |
| [KnowledgeC](../app-usage/knowledgec/index.md)·[바이옴](../app-usage/biome/index.md)·[화면 사용 시간](../app-usage/screen-time.md) | 앱을 언제 앞에 띄워 썼는지 |
| [앱별 데이터 사용량](../network/data-usage.md) | 앱이 주고받은 데이터 양 |
| [알림 기록](../app-usage/notifications.md) | 공유·업로드 관련 알림이 왔는지 |
| [사진 보관함](../media/photos/index.md) | 앱에 넘긴 사진이 기기에 남았는지 |
| [아이클라우드 드라이브](icloud-drive.md) | 같은 파일 공급자 구조를 쓰는 Apple 쪽 비교 |
| [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) | 기기 밖 계정 자료를 확보하는 절차 |

자료 유출을 의심하는 사건이라면 [자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에서 이 흔적들을 어떤 순서로 맞추는지 봅니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 구글 드라이브 앱이 설치된 iOS 검체가 있는지 먼저 확인하고, 있으면 아래 질문을 풀어 봅니다.

1. 설치 앱 목록에서 구글 드라이브의 번들 ID 를 찾고, 그 번들 ID 로 시작하는 도메인이 `Manifest.db` 에 몇 개 있는지 셉니다.
2. `HomeDomain` 의 `FileProvider` 폴더 아래에 구글 드라이브 폴더가 있는지, 있다면 `Domains.plist` 에 기본 항목 말고 다른 도메인 항목이 있는지 봅니다.
3. `com.apple.DocumentManager.defaults.plist` 의 `DOCUserDefaultsCachedDisplayNamesBySourceIdentifier` 에 구글 드라이브 항목이 있는지 봅니다.
4. 앱 도메인 안에서 SQLite 파일을 모두 찾아 표 이름을 적고, 파일 이름이나 시각으로 보이는 칸이 있는 표를 고릅니다.
5. 4번에서 고른 시각 칸을 KnowledgeC·바이옴의 앱 사용 시각과 견주어, 어떤 시각 형식인지 정합니다.

## 참고 문헌

1. Forensafe, "Blog - Google Drive" (Windows 10 기준 내용) — https://forensafe.com/blogs/googledrive.html
2. Apple Developer Documentation, "NSFileProviderDomain" — https://developer.apple.com/tutorials/data/documentation/fileprovider/nsfileproviderdomain.json
3. RealityNet, "iOS-Forensics-References" (GitHub) — https://github.com/RealityNet/iOS-Forensics-References
4. App Store, "Google Drive" — https://apps.apple.com/us/app/google-drive/id507874739
