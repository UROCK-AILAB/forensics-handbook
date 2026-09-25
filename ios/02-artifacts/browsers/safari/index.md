---
title: "사파리"
parent: "아티팩트 · 인터넷·브라우저"
nav_order: 720
has_children: true
has_toc: false
---

# 사파리 (Safari)

## 한 줄 요약

아이폰 기본 브라우저 사파리는 방문 기록, 탭, 북마크를 `/private/var/mobile/Library/Safari/` 아래의 SQLite DB 여러 개에 나눠 담고, 개인 정보 보호 모드의 탭과 iCloud 로 넘어온 다른 기기의 기록까지 같은 곳에 남깁니다.

## 왜 중요한가

어떤 사이트를 언제 열었는지 묻는 조사에서 아이폰은 사파리부터 봅니다. 방문 한 번마다 시각과 URL 이 남고[2][6], 열려 있던 탭과 닫은 탭, 다른 기기의 탭까지 따로 저장되어서[3] 한 사람의 웹 사용을 여러 방향에서 맞춰 볼 수 있습니다. 다만 기록마다 들어가는 수집 방식이 달라서, 암호화하지 않은 로컬 백업에는 방문 기록이 들어가지 않고[4] 관찰한 백업에서도 탭 DB 가 보이지 않았습니다(확인 범위: iOS 27.0). 그래서 사파리 분석은 어떤 방식으로 수집했는지 확인하는 데서 시작합니다.

## 한눈에 보기

| 무엇 | 위치 | iOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 방문 기록 | 기기 `/private/var/mobile/Library/Safari/History.db`[1][2], 프로필별 `Safari/Profiles/*/History.db`[6] | 프로필별 DB 는 iLEAPP 가 iOS 17 이후용으로 찾습니다[6] | 방문 URL·시각·제목·방문 횟수, 넘겨주기, 이 기기인지 다른 기기인지 |
| 탭 | 같은 폴더의 `SafariTabs.db`, `BrowserState.db`, `CloudTabs.db`[1][3] | iOS 16 부터 BrowserState.db 는 닫은 탭만 담음[5] | 열린 탭·닫은 탭·다른 기기 탭, 마지막으로 본 시각 |
| 북마크 | 기기 `/private/var/mobile/Library/Safari/Bookmarks.db`[1][2], 백업 HomeDomain `Library/Safari/Bookmarks.db`(확인 범위: iOS 27.0) | — | 저장한 URL 과 폴더 구조, iCloud 동기화 상태 |
| 개인 정보 보호 탭 | SafariTabs.db 안의 개인 정보 보호 폴더[3], BrowserState.db `private_browsing` 칸[3] | 잠긴 개인 정보 보호 브라우징은 iOS 17 부터 | 방문 기록에 남지 않는 개인 정보 보호 모드 탭 |
| 내려받기 목록 | `/private/var/mobile/Containers/Data/Application/<GUID>/Library/Safari/Downloads/Downloads.plist`[1] | iOS 15 이미지 기준[1] | 내려받은 파일 목록. 관찰한 백업에는 이 파일이 없었습니다(확인 범위: iOS 27.0) |
| 캐시 | `/private/var/mobile/Containers/Data/Application/<GUID>/Library/Caches/com.apple.mobilesafari/Cache.db`[1] | iOS 15 이미지 기준[1] | 불러온 웹 자원의 캐시 |
| 파비콘 | `/private/var/mobile/Containers/Data/Application/<App_GUID>/Library/Image Cache/Favicons/Favicons.db`[2] | — | 사이트 아이콘 |
| 바이옴 사파리 스트림 | `/private/var/db/biome/streams/restricted/` 아래 `_DKEvent.Safari.History`, SafariPageView 스트림[5] | iOS 16 시험[5] | 방문 기록과 따로 남는 방문·페이지 보기 기록 |

잠긴 개인 정보 보호 브라우징의 버전은 [개인 정보 보호 브라우징 (Private Browsing)](private-browsing.md)에 출처와 함께 있습니다. 바이옴의 SafariPageView 스트림에는 페이지 제목·URL·본문 텍스트와 "기부(donate)" 시각이 담기고, SEGB 파일이 `local` 폴더에 있으면 이 기기의 기록, `remote` 폴더에 있으면 다른 기기에서 동기화된 기록입니다(iOS 16 시험)[5]. 바이옴 형식은 [바이옴 (Biome)](../../app-usage/biome/index.md)과 [SEGB 형식 (SEGB)](../../../01-foundations/data-formats/segb.md)에서 다룹니다.

사파리의 번들 ID 는 `com.apple.mobilesafari` 이고, 관찰한 백업에는 AppDomain-com.apple.mobilesafari 도메인(항목 83개)과 함께 아래 도메인이 있었습니다(확인 범위: iOS 27.0).

- AppDomainGroup-group.com.apple.safari, AppDomain-com.apple.SafariViewService, AppDomainGroup-com.apple.SafariSearchUploadWorker
- AppDomainPlugin-com.apple.mobilesafari 아래 SafariActionExtension, SafariDiagnosticExtension, SafariLinkExtension, SafariShareExtension, SafariWidgetExtension
- AppDomainPlugin-com.apple.safari.SafariUsageRetentionExtension, AppDomainPlugin-com.apple.parsec.SafariBrowsingAssistantWorker, AppDomainPlugin-com.apple.unilog.SafariSearchUploadWorker

사파리 설정 plist 는 AppDomain-com.apple.mobilesafari `Library/Preferences/` 아래 `com.apple.mobilesafari.plist`, `com.apple.Safari.History.plist`, `com.apple.SafariViewService.plist` 등과 HomeDomain `Library/Preferences/` 아래 `com.apple.SafariBookmarksSyncAgent.plist`, `com.apple.SafariCloudHistoryPushAgent.plist`, `com.apple.Safari.SafeBrowsing.plist` 등으로 나뉘어 있었습니다(확인 범위: iOS 27.0). 각 키는 주제에 맞는 하위 페이지에서 다룹니다. 번들 ID 와 백업 도메인의 관계는 [번들 ID와 앱 그룹 (Bundle ID·App Group)](../../../01-foundations/value-decoding/bundle-id-app-group.md)에 있습니다.

> 그림 자리: 기기의 `Library/Safari/` 폴더에 있는 DB 다섯 개와 앱 컨테이너 쪽 파일, 그리고 암호화하지 않은 백업에 실제로 들어가는 것과 빠지는 것

## 읽는 순서

1. [방문 기록 (History.db)](history.md) — `history_visits`·`history_items` 를 이어 방문을 읽는 법, 이 기기와 다른 기기의 방문을 가르는 `origin`, 두 가지 시각 기준, History.db 가 없는 백업에서 볼 다른 DB 를 다룹니다.
2. [탭과 세션 (Tabs)](tabs.md) — SafariTabs.db·BrowserState.db·CloudTabs.db 가 각각 맡는 탭과 BLOB 칸 안의 plist, 버전마다 바뀐 시각 기준을 다룹니다.
3. [북마크와 읽기 목록 (Bookmarks·Reading List)](bookmarks-reading-list.md) — 암호화하지 않은 백업에도 들어가는 Bookmarks.db 의 표와 칸, 폴더를 따라가는 법, 읽기 목록을 가려낼 때 확인할 점을 다룹니다.
4. [개인 정보 보호 브라우징 (Private Browsing)](private-browsing.md) — 방문 기록에는 없지만 탭 DB 에 남는 개인 정보 보호 탭을 찾는 기준과 잠긴 개인 정보 보호 브라우징을 다룹니다.

## 함께 볼 페이지

다른 브라우저는 [크롬 (Chrome for iOS)](../chrome.md)과 [네이버 앱 (NAVER)](../naver.md)에서 다룹니다. 사파리 밖에 남는 방문 흔적은 [바이옴 (Biome)](../../app-usage/biome/index.md)과 [KnowledgeC (knowledgeC.db)](../../app-usage/knowledgec/index.md)에서, 저장된 웹 암호는 [저장된 암호 (Passwords·iCloud Keychain)](../../credentials-security/saved-passwords.md)에서 찾습니다.

DB 와 값을 읽는 바탕은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md), [속성 목록 파일 (plist·NSKeyedArchiver)](../../../01-foundations/data-formats/plist.md), [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md), [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md)에 있습니다.

조사 흐름은 [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md), [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md), [스미싱 흔적 (Smishing)](../../../04-scenarios/incident/smishing.md)에서 이어집니다.

## 참고 문헌

1. iOS 15 Image Forensics Analysis and Tools Comparison - Native Apps (blog.digital-forensics.it, 2023-10) — https://blog.digital-forensics.it/2023/10/ios-15-image-forensics-analysis-and.html
2. Forensafe, iOS Safari Browser — https://forensafe.com/blogs/iOSSafari.html
3. iLEAPP `scripts/artifacts/safariTabs.py` (abrignoni/iLEAPP, main) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/safariTabs.py
4. Apple 지원, "About encrypted backups on your iPhone, iPad, or iPod touch" — https://support.apple.com/en-us/108353
5. D20 Forensics, "iOS 16 - Breaking Down the Biomes (Part 4) - Surfin' with Safari" (2022-09-28) — https://blog.d204n6.com/2022/09/ios-16-breaking-down-biomes-part-4.html
6. iLEAPP `scripts/artifacts/safariHistory.py` (abrignoni/iLEAPP, main) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/safariHistory.py
