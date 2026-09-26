---
title: "사진 보관함"
parent: "아티팩트 · 사진·미디어"
nav_order: 540
has_children: true
has_toc: false
---

# 사진 보관함 (Photos Library)

아이폰 사진 앱은 사진·동영상 파일을 `Media/DCIM` 과 `Media/PhotoData` 아래 폴더에 두고, 파일마다 날짜·촬영 정보·앨범·공유·삭제 상태를 Photos.sqlite 한 DB 에 적으며, iCloud 사진 동기화 상태는 따로 plist 에 남깁니다.

## 왜 중요한가

사진은 조사에서 자주 핵심 증거가 되고, 파일만 보면 알 수 없는 내력이 Photos.sqlite 에 남습니다. 이 기기 카메라로 찍은 사진인지, 공유 앨범이나 iCloud, 다른 사람이 "나와 공유됨" 으로 보낸 경로에서 들어온 사진인지를 DB 의 값으로 구분할 수 있고[1], 지운 사진도 30일 동안은 DB 에 삭제 표시만 붙은 채 남습니다. 다만 값의 뜻 대부분은 Apple 명세가 아니라 공개 쿼리와 도구 자료에서 왔고, 표와 열 이름도 버전마다 바뀌어서 분석할 때마다 DB 를 직접 열어 확인하는 편이 안전합니다.

## 한눈에 보기

| 무엇 | 위치 | iOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 사진 DB | 기기 `/private/var/mobile/Media/PhotoData/Photos.sqlite`[1][2], 백업 CameraRollDomain `Media/PhotoData/Photos.sqlite` | 전 버전(자산 표 이름은 버전마다 다름) | 자산별 날짜, 들어온 경로, 촬영 정보, 앨범, 공유, 삭제·가려짐 상태 |
| 나와 공유됨 보관함 | 기기 `/private/var/mobile/Library/Photos/Libraries/Syndication.photoslibrary/database/Photos.sqlite`[2] | — | 메시지 등으로 "나와 공유됨" 에 들어온 사진. iLEAPP 는 Ph25~26 파서로 읽습니다[2] |
| 앱별 사진 보관함 | 백업 HomeDomain `Library/Preferences/com.apple.assetsd.plist` 의 `PLBackgroundMigrationPaths` 에 `com.apple.GenerativePlayground` 의 `.photoslibrary` 경로가 있습니다 | — | 앱마다 사진 보관함이 따로 있을 수 있다는 단서. 그 파일이 백업의 어느 도메인에 들어가는지는 실제 백업에서 확인합니다 |
| iCloud 사진 상태 | 백업 CameraRollDomain `Media/PhotoData/CPL/` 의 `syncstatus.plist`, `DownloadCounts.plist`, `metrics.plist`, `mobileCPL.plist`, `cloudphotos-#.#.plist` | — | 이름으로 보면 iCloud 사진 동기화 시각과 개수. 키는 아래 표에 있습니다 |
| DCIM 번호 | 백업 CameraRollDomain `Media/PhotoData/MISC/DCIM_APPLE.plist` 의 `DCIMLastDirectoryNumber`, `DCIMLastFileNumber` | — | 이름으로 보면 마지막 DCIM 폴더·파일 번호. 값의 뜻은 공개된 자료가 없습니다 |
| 사진 앱 내부 설정 | 백업 CameraRollDomain `Media/PhotoData/private/com.apple.assetsd/appPrivateData.plist`, `Media/PhotoData/private/com.apple.mobileslideshow/appPrivateData.plist`, `Media/PhotoData/Journals/MigrationHistory.plist` | — | 사진 앱과 사진 서비스의 내부 상태 |
| iCloud 사진 데몬 설정 | 백업 HomeDomain `Library/Preferences/com.apple.cloudphotod.plist` 에 `CPLCloudKitCoordinator-com.apple.photos.cloud` 키 | — | iCloud 사진 연결 설정으로 보이는 값 |

사진 파일 자체가 백업의 어느 경로에 들어가는지는 실제 백업에서 확인합니다. 백업 도메인을 찾는 법은 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md)에서 다룹니다.

사진 파일이 놓이는 기기 경로는 아래와 같고[1], 들어온 경로마다 폴더가 다릅니다. Photos.sqlite 에서 이 경로를 구분하는 `ZSAVEDASSETTYPE` 값은 [사진 DB 구조 (Photos.sqlite)](photos-sqlite.md)에 있습니다.

| 들어온 경로 | 기기 경로 |
|---|---|
| 이 기기 카메라 | `/private/var/mobile/Media/DCIM/<*>APPLE` |
| 편집본 | `/private/var/mobile/Media/PhotoData/Mutations/DCIM/<*>APPLE` |
| iCloud 사진 | `/private/var/mobile/Media/PhotoData/CPLAssets/<group*>` |
| 공유 앨범 | `/private/var/mobile/Media/PhotoData/PhotoCloudSharingData/<personID>/<shared_album_GUID>/` |
| iCloud 공유 링크 | `/private/var/mobile/Media/PhotoData/CMMAssets/<zShare-UUID>/` |
| 썸네일 | `/private/var/mobile/Media/PhotoData/Thumbnails/V2/` 아래 |

`Media/PhotoData/CPL/` 의 plist 에는 아래 키가 있습니다. 키의 뜻은 공개된 자료가 없어서 이름으로 짐작합니다.

| 파일 | 키 |
|---|---|
| `syncstatus.plist` | `accountFlags`, `accountPartitionType`, `cloudAssetCountPerType`(`public.image`, `public.movie`), `cloudAssetCountPerTypeLastCheckDate`, `connectedToNetwork`, `hasBatteryBudgetKey`, `hasCellularBudgetKey`, `hasValidSystemBudgetKey`, `iCloudLibraryClientIsNotAuthenticated`, `iCloudLibraryExists`, `inAirplaneMode`, `initialDownloadDate`, `initialSyncDate`, `keychainCDPEnabled`, `lastSyncDate`, `unBlockedReason` |
| `DownloadCounts.plist` | `CountKeyImages`, `CountKeyVideos` |
| `metrics.plist` | `BlockedSessionsCount`, `DASUnBlockedCount`, `PoorSystemConditionsBlockedCount`, `ThunderingHerdBlockedCount`, `TotalSessionsCount` |
| `mobileCPL.plist` | `storeUUID` |

`initialSyncDate`, `lastSyncDate` 는 이름으로 보면 iCloud 사진의 첫 동기화와 마지막 동기화 시각이라서, iCloud 사진이 켜져 있었는지 추정할 때 Photos.sqlite 의 `ZCLOUDLOCALSTATE` 와 함께 봅니다. plist 를 읽는 법은 [속성 목록 파일 (plist·NSKeyedArchiver)](../../../01-foundations/data-formats/plist.md)에 있습니다.

> 그림 자리: 기기 경로의 `Media/DCIM`·`Media/PhotoData` 폴더와 백업 CameraRollDomain·HomeDomain 에 사진 DB 와 부속 plist 가 어떻게 나뉘어 들어가는지

## 읽는 순서

1. [사진 DB 구조 (Photos.sqlite)](photos-sqlite.md) — `ZASSET` 과 촬영 정보·원본 파일·편집 기록 표를 잇는 법, 들어온 경로를 구분하는 값, 날짜 열을 바꾸는 법을 다룹니다.
2. [앨범과 공유 앨범 (Albums·Shared Albums)](albums-shared.md) — `ZGENERICALBUM` 과 연결 표, 공유 앨범의 댓글·초대·피드, iCloud 링크 공유와 공유 사진 보관함을 다룹니다.
3. [최근 삭제된 항목 (Recently Deleted)](recently-deleted.md) — 30일 보관과 `ZTRASHEDSTATE` 삭제 표시, 가려진 항목, iCloud 로 넘어온 삭제를 구분하는 어려움을 다룹니다.

## 함께 볼 페이지

사진 파일 안의 EXIF 와 HEIC 는 [카메라 사진과 메타데이터 (DCIM·EXIF·HEIC)](../dcim-exif.md)에서, 화면 캡처는 [스크린샷과 화면 녹화 (Screenshots·Screen Recording)](../screenshots.md)에서 다룹니다. 메시지로 주고받은 사진은 [메시지 (iMessage·SMS)](../../communications/messages/index.md), 주변 기기와 주고받은 사진은 [에어드롭 (AirDrop)](../../network/airdrop.md)에서 봅니다.

DB 와 값을 읽는 바탕은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md), [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md), [데이터 보호 (Data Protection)](../../../01-foundations/storage/data-protection/index.md)에 있습니다.

조사 흐름은 [이 사진은 언제 어디서 찍었나 (Photo Origin)](../../../04-scenarios/activity/photo-origin.md), [지운 대화와 사진 찾기 (Deleted Content)](../../../04-scenarios/activity/deleted-content.md), [자료를 밖으로 보냈나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md)에서 이어집니다.

## 참고 문헌

1. The Forensic Scooter (Scott Koenig), "Local Photo Library Photos.sqlite Query Documentation & Notable Artifacts" (2022-05-02) — https://theforensicscooter.com/2022/05/02/photos-sqlite-query-documentation-notable-artifacts/
2. The Forensic Scooter, "iLEAPP Parsers & Photos.sqlite Queries" (2024-05-18) — https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/
