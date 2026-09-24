---
title: "이 파일을 누가 언제 열었나"
parent: "시나리오 · 행위 재구성"
nav_order: 2300
---

# 이 파일을 누가 언제 열었나 (File Access)

## 조사 질문

특정 파일을 어느 사용자가 언제, 어떤 앱으로 열었는지 묻습니다. 유출 사건에서는 빼돌린 문서를 누가 열어 봤는지, 내부 조사에서는 열람 권한이 없는 사람이 문서를 봤는지를 가리는 데 씁니다.

macOS 에서 파일을 "열었다"를 곧바로 적는 흔적은 많지 않습니다. 파일 시스템 이벤트나 문서 버전처럼 파일을 "바꾼" 기록은 여럿이지만, 읽기만 한 동작은 이런 기록에 남지 않습니다. 그래서 연 기록(최근 항목, 마지막으로 연 날짜)과 바꾼 기록을 나눠 모으고, 사용자별 흔적으로 "누가"를 따로 가립니다. 흔적 하나하나의 구조는 각 아티팩트 페이지에서 다루고, 이 페이지는 조사 순서와 판단만 다룹니다.

## 먼저 확인할 것

OS 버전은 [OS 버전과 설치 기록](../../02-artifacts/system-account/os-version-install-history.md)에서 먼저 확인합니다. 버전에 따라 흔적의 형식이 달라서, 아래 차이를 먼저 알고 들어갑니다.

| 항목 | 버전 |
|---|---|
| 최근 항목 `.sfl` → `.sfl2` | 10.11 / 10.13 [8] |
| 빠른 보기 섬네일 캐시에 파일 이름이 들어 있던 옛 형식 | 10.14 이하 [11][12] |
| 빠른 보기 섬네일 캐시 새 형식(inode 만 담음) | 10.15 부터 [11] |
| 빠른 보기 섬네일 캐시가 `ThumbnailsAgent` 아래로 옮겨 감 | 11 부터 [11] |
| 파일 시스템 이벤트 레코드의 UID 칸(3SLD) | 14 Sonoma 부터(FSEventsParser 코드 주석 기준) [14] |

시간대는 [시간대와 시계 설정](../../02-artifacts/system-account/time-zone.md)에서 확인합니다. 흔적마다 시각 기준이 달라서 APFS 파일 시각은 1970-01-01 UTC 기준 나노초, 북마크·빠른 보기 캐시·knowledgeC 는 맥 절대 시각, 문서 버전 DB는 유닉스 초로 적습니다 [5][9][11][10]. 모든 시각을 한 기준으로 바꿔 적어 두어야 대조할 수 있습니다([맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md)).

사용자 범위는 "누가"를 가리는 출발점입니다. `~/Library/` 아래 최근 항목·Finder plist·빠른 보기 캐시·knowledgeC 사용자 DB는 사용자마다 따로 있어서, 흔적이 나온 홈 폴더의 주인을 먼저 그 흔적의 사용자로 봅니다. 이 판단은 필자가 정리한 것이고, 같은 계정을 여러 사람이 썼을 수 있다는 점은 [그 시각에 맥을 쓴 사람이 누구인가](user-attribution.md)에서 따로 따집니다.

수집 범위에서는 파일의 확장 속성까지 보존했는지 확인합니다. 확장 속성은 NFS 로 복사하면 모두 벗겨지고, FAT·exFAT 같은 맥 고유가 아닌 파일 시스템으로 복사하면 숨은 그림자 파일로 따로 떨어질 수 있습니다 [2]. `/System/Volumes/Data/.fseventsd` 와 `/System/Volumes/Data/.DocumentRevisions-V100/` 가 수집 범위에 들어 있는지도 봅니다([맥 증거 확보](../../03-techniques/process-acquisition/evidence-acquisition/index.md)).

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 파일의 `com.apple.lastuseddate#PS` 속성과 스포트라이트 `kMDItemLastUsedDate` | 파일을 마지막으로 연 날짜 | [스포트라이트](../../02-artifacts/file-folder-usage/spotlight/index.md) |
| 2 | 최근 문서 `com.apple.LSSharedFileList.RecentDocuments.sfl2`(`.sfl3`), 앱별 `ApplicationRecentDocuments` 폴더 | 최근 연 문서의 북마크와 연 앱 | [최근 항목](../../02-artifacts/file-folder-usage/recent-items/index.md) |
| 3 | `com.apple.finder.plist`, `.GlobalPreferences.plist` 의 `NSNavRecentPlaces` | 최근 폴더·이동 위치·검색어, 열기·저장 창의 최근 위치 | [파인더 설정과 기록](../../02-artifacts/file-folder-usage/finder-plist.md) |
| 4 | 마이크로소프트 오피스 `securebookmarks.plist` | 오피스 앱의 최근 파일 | [최근 항목](../../02-artifacts/file-folder-usage/recent-items/index.md) |
| 5 | 앱 저장 상태 `~/Library/Saved Application State/` | 창 제목, 미리보기·파인더가 열어 둔 파일과 폴더 | [앱 저장 상태](../../02-artifacts/file-folder-usage/saved-application-state.md) |
| 6 | knowledgeC `/app/activity` | 앱 안에서 보거나 편집하던 항목 제목 | [KnowledgeC](../../02-artifacts/execution/knowledgec/index.md) |
| 7 | 빠른 보기 섬네일 캐시 `index.sqlite` | 섬네일을 쓴 시각 `last_hit_date` 와 `hit_count` | [빠른 보기 섬네일 캐시](../../02-artifacts/file-folder-usage/quicklook-thumbnails.md) |
| 8 | 문서 버전 `db.sqlite` | 저장할 때마다 생긴 버전과 `generation_add_time` | [문서 버전](../../02-artifacts/file-folder-usage/document-revisions.md) |
| 9 | 파일 시스템 이벤트 `.fseventsd` | 만들기·고치기·이름 바꾸기·지우기 | [파일 시스템 이벤트](../../02-artifacts/filesystem/fsevents/index.md) |
| 10 | 통합 로그의 `tccd` 기록 | 개인 정보 보호 권한 확인과 접근 위반 | [개인 정보 보호 권한](../../02-artifacts/credentials/tcc/index.md) |
| 11 | APFS 파일 시각과 `date_added` | 만들기·수정·변경·접근 시각, 폴더에 들어온 시각 | [APFS 구조](../../01-foundations/disk-volume/apfs/index.md) |

1~6번은 "열었다"에 가까운 흔적이라 먼저 보고, 7~11번은 앞의 결과를 보강하거나 파일을 바꾼 시점을 세울 때 봅니다. 오피스 파일 경로는 오피스 2016 기준으로 `~/Library/Containers/com.microsoft.<앱>/Data/Library/Preferences/com.microsoft.<앱>.securebookmarks.plist` 입니다 [8].

### 파일 자체에 남는 "마지막으로 연 날짜"

파인더의 "마지막으로 열어 본 날짜 (Last opened)"는 확장 속성 `com.apple.lastuseddate` 의 날짜를 보여 줍니다 [3]. 이 속성은 전체 이름이 `com.apple.lastuseddate#PS` 라서 P·S 두 플래그가 붙어 있고, 편집한 파일에서 흔히 보입니다(분석 범위: macOS 15.0, 26.0 Tahoe) [1][2]. P 는 공유할 때 보존하지 않는다(NO_EXPORT)는 뜻이고 S 는 동기화할 수 있다(SYNCABLE)는 뜻입니다 [4]. 값의 이진 형식과 언제 붙고 언제 바뀌는지는 이 핸드북이 연 자료 어디에도 적혀 있지 않아서, 값을 읽을 때는 파인더에 보이는 날짜와 대조해 확인합니다.

스포트라이트 속성 `kMDItemLastUsedDate` 는 파일을 마지막으로 쓴 날짜·시각이고, 더블클릭처럼 LaunchServices 가 파일을 열 때마다 자동으로 갱신됩니다 [6]. 두 값이 늘 같은지는 확인하지 못했습니다. mac_apt 가 색인에서 함께 뽑는 `kMDItemUseCount`·`kMDItemUsedDates` 는 Apple 문서에 뜻이 적혀 있지 않습니다 [7].

확장 속성을 바꾸거나 권한 같은 메타데이터를 바꿔도 파일 데이터는 그대로라서 수정 시각이 바뀌지 않고, 데이터를 바꿀 때만 수정 시각이 바뀝니다 [3]. APFS 접근 시각은 볼륨에 `APFS_FEATURE_STRICTATIME`(0x8)이 켜져 있으면 읽을 때마다 갱신되지만, 꺼져 있으면 접근 시각이 수정 시각보다 이를 때만 갱신됩니다 [5]. 기본 볼륨에서 이 플래그가 켜져 있는지는 확인하지 못해서, 접근 시각 하나로 "열었다"를 단정하지 않습니다.

## 분석 흐름

1. 대상 파일의 경로, 볼륨, 파일 번호(inode)를 확정합니다. 뒤 단계에서 이름이 없는 흔적과 맞출 때 이 값을 씁니다.
2. 파일 자체에서 `com.apple.lastuseddate#PS`, 스포트라이트 `kMDItemLastUsedDate`, APFS 시각을 뽑습니다.
3. 사용자마다 최근 문서 목록과 앱별 최근 문서 목록에서 파일 경로를 찾아 어느 앱으로 열었는지 봅니다. 북마크에는 경로(0x1004), 볼륨 이름(0x2010), 볼륨 UUID(0x2011), 북마크를 만든 사용자 이름·UID(0xc011·0xc012) 칸이 있어서 외장·네트워크 볼륨의 파일인지와 계정을 함께 확인할 수 있습니다 [9]. 칸을 읽는 법은 [파일 참조 데이터](../../01-foundations/value-decoding/alias-bookmark.md)에 있습니다.
4. 앱 저장 상태의 창 제목과 knowledgeC `/app/activity` 의 항목 제목에서 파일 이름을 찾습니다.
5. 빠른 보기 섬네일 캐시에서 파일을 찾습니다. macOS 10.15 이후 캐시에는 inode 만 있어서 1단계의 파일 번호로 맞춥니다 [11].
6. 문서 버전과 파일 시스템 이벤트에서 같은 파일을 저장하거나 바꾼 흔적을 찾아, 연 흔적과 시각이 이어지는지 봅니다.
7. "누가"를 가립니다. 사용자별 흔적은 홈 폴더 주인을 보고, macOS 14 이후 파일 시스템 이벤트는 레코드의 UID 4바이트를 보고 [14], 통합 로그 기록은 붙어 있는 euid 를 봅니다 [15].
8. 1~7단계의 시각을 한 [타임라인](../../03-techniques/analysis/timeline/index.md)에 올려 로그인 구간과 겹치는지 확인합니다.

3~8단계의 순서는 공개 자료의 절차가 아니라 필자가 정리한 방법입니다. 흔적 하나로 결론을 내지 않고, 연 흔적·바꾼 흔적·사용자 세 가지가 서로 맞는지로 판단합니다.

## 흔한 오판

- **섬네일이 있으면 파일을 열었다고 보는 경우.** 빠른 보기 섬네일은 폴더를 아이콘 보기 등으로 보기만 해도 생길 수 있습니다 [13].
- **파일 시스템 이벤트에서 "열기"를 찾는 경우.** 파일 시스템 이벤트의 플래그는 Created·Removed·InodeMetaMod·Renamed·Modified 같은 변경만 다루고 읽기는 없으며, 레코드에 시각 칸도 없습니다 [14]. "바꿨다"의 근거로만 씁니다.
- **수정 시각이 그대로라서 손대지 않았다고 보는 경우.** 확장 속성과 권한을 바꿔도 수정 시각은 그대로입니다 [3].
- **최근 항목의 순서나 `DateLastSeen` 을 연 시각으로 읽는 경우.** 최근 항목에 연 시각 칸이 있다는 근거는 없고, `CustomItemProperties` 의 `com.apple.LSSharedFileList.DateLastSeen` 은 mac_apt 가 뽑지만 언제 갱신되는지 확인하지 못했습니다 [8]. 앱이 `clearRecentDocuments` 로 목록을 비울 수도 있어서 목록에 없다고 열지 않았다고 보지도 않습니다 [10].
- **문서 버전이 없으면 열지 않았다고 보는 경우.** 문서 버전은 버전 기능을 지원하는 앱(미리보기·TextEdit·Pages·Numbers 등)이 저장할 때만 생기고, 열기만 하면 생기지 않습니다 [10].
- **북마크의 사용자 칸을 연 사람으로 단정하는 경우.** 0xc011·0xc012 는 북마크를 만든 사용자이고, 이 값이 파일을 연 사용자와 늘 같은지는 확인하지 못했습니다 [9].

## 보고서 문장 예

> 사용자 ○○의 최근 문서 목록(`RecentDocuments.sfl2`)에 "○○.docx" 를 가리키는 북마크가 있고, 같은 사용자의 앱별 최근 문서 목록에서는 이 파일이 번들 ID "○○" 앱 목록에 들어 있습니다. 파일의 `com.apple.lastuseddate#PS` 속성에는 ○○○○년 ○월 ○일 ○시 ○분(UTC로 바꾼 시각)이 적혀 있습니다. 이 기록들로 이 계정에서 파일을 연 흔적은 확인할 수 있지만, 그 시각에 키보드 앞에 있던 사람이 누구인지는 정할 수 없습니다.

## 함께 볼 페이지

- [최근 항목 (Shared File Lists)](../../02-artifacts/file-folder-usage/recent-items/index.md) — 최근 문서 목록의 구조
- [파일 참조 데이터 (Alias·Bookmark)](../../01-foundations/value-decoding/alias-bookmark.md) — 북마크 칸 읽는 법
- [파일 시스템 이벤트 (FSEvents)](../../02-artifacts/filesystem/fsevents/index.md) — 파일 변경 기록
- [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](user-attribution.md) — 계정과 사람을 잇는 법
- [이 문서의 날짜를 믿을 수 있나 (Document Date)](document-date.md) — 파일 시각을 믿을 수 있는지
- [이 파일은 어디서 왔나 (File Origin)](file-origin.md) — 파일을 받은 경로

## 참고 문헌

1. Howard Oakley, "Which extended attributes does macOS Tahoe preserve?" (2025-12-17) — https://eclecticlight.co/2025/12/17/which-extended-attributes-does-macos-tahoe-preserve/
2. Howard Oakley, "The secret life of the xattr" (2026-04-24) — https://eclecticlight.co/2026/04/24/the-secret-life-of-the-xattr/
3. Howard Oakley, "What changes a file's modification date, and what doesn't?" (2020-03-27) — https://eclecticlight.co/2020/03/27/what-changes-a-files-modification-date-and-what-doesnt/
4. Apple 오픈소스 copyfile, xattr_flags.c·xattr_flags.h — https://raw.githubusercontent.com/apple-oss-distributions/copyfile/main/xattr_flags.c , https://raw.githubusercontent.com/apple-oss-distributions/copyfile/main/xattr_flags.h
5. Apple, Apple File System Reference (2020-06-22) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
6. Apple, Spotlight Metadata Attributes Reference — Common Attributes (2014-07-15) — https://developer.apple.com/library/archive/documentation/CoreServices/Reference/MetadataAttributesRef/Reference/CommonAttrs.html , Apple Developer, Common Metadata Attribute Keys (MDItem) — https://developer.apple.com/tutorials/data/documentation/coreservices/file_metadata/mditem/common_metadata_attribute_keys.json
7. mac_apt 플러그인 spotlight.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/spotlight.py
8. mac_apt `plugins/recentitems.py` — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/recentitems.py , macMRU-Parser `macMRU.py` (Sarah Edwards) — https://raw.githubusercontent.com/mac4n6/macMRU-Parser/master/macMRU.py
9. mac_alias 문서, "Mac Bookmark Format" — https://mac-alias.readthedocs.io/en/latest/bookmark_fmt.html
10. mac_apt `plugins/documentrevisions.py`·`plugins/savedstate.py` — https://github.com/ydkhatri/mac_apt/blob/master/plugins/documentrevisions.py , The Eclectic Light Company, "Managing macOS versioning and the DocumentRevisions-V100 folder" (2025-09-08) — https://eclecticlight.co/2025/09/08/managing-macos-versioning-and-the-documentrevisions-v100-folder/ , Apple Developer, NSDocumentController — https://developer.apple.com/tutorials/data/documentation/appkit/nsdocumentcontroller.json
11. mac_apt QuickLook 플러그인 quicklook.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/quicklook.py
12. Mari DeGrazia, "QuickLook thumbnails.data parser" (az4n6, 2016-10) — https://az4n6.blogspot.com/2016/10/quicklook-thumbnailsdata-parser.html
13. Patrick Wardle, "Cache Me Outside: apple's 'quicklook' cache may leak encrypted data" (Objective-See, 2018-06-15) — https://objective-see.org/blog/blog_0x30.html
14. libyal dtformats — MacOS File System Events Disk Log Stream format — https://github.com/libyal/dtformats/blob/main/documentation/MacOS%20File%20System%20Events%20Disk%20Log%20Stream%20format.asciidoc , FSEventsParser 4.1 (Nicole Ibrahim) — https://raw.githubusercontent.com/dlcowen/FSEventsParser/master/FSEParser_V4.1.py
15. libyal dtformats — Apple Unified Logging and Activity Tracing formats — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
