---
title: "캐시와 웹뷰"
parent: "앱 데이터 분석"
grand_parent: "기법 · 분석"
nav_order: 1250
---

# 캐시와 웹뷰 (Cache·WebKit)

앱이 주고받은 HTTP 응답을 담는 캐시 DB 와, 앱 안의 웹뷰 (WebView) 가 남기는 WebKit 데이터에서 앱이 어느 서버·도메인과 통신했는지 확인합니다.

## 언제 쓰나

앱 자신의 DB 가 비어 있거나 암호화되어 있을 때, 앱이 서버에서 받아 온 응답이 캐시에 남아 있으면 화면에 무엇이 떠 있었는지 짐작할 단서가 됩니다. 앱이 몰래 어떤 도메인에 접속했는지 확인하려는 침해 조사에서도 이 기록을 봅니다. 처음 보는 앱이라면 [처음 보는 앱 분석 순서](unknown-apps.md) 에서 컨테이너를 찾은 다음 이 페이지로 옵니다. Safari 자체의 방문 기록과 탭은 [사파리](../../../02-artifacts/browsers/safari/index.md) 에서 다루고, 이 페이지는 앱 컨테이너 쪽에 생기는 캐시와 WebKit 데이터를 다룹니다.

## 어디에 있나

| 파일 | 위치 | 로컬 백업에서 |
|---|---|---|
| HTTP 캐시 `Cache.db` | 앱 데이터 컨테이너의 `Library/Caches/<번들 ID>/Cache.db`[5] | 들어가지 않음[1] |
| `observations.db` | 앱 컨테이너의 `Library/WebKit/WebsiteData/ResourceLoadStatistics/observations.db` (확인 범위: iPhone 13 mini, iOS 27.0) | 보임 (확인 범위: iPhone 13 mini, iOS 27.0) |
| 로컬 저장소 (LocalStorage) | MVT 기준 `/private/var/mobile/Containers/Data/Application/*/Library/WebKit/WebsiteData/LocalStorage/`[2] | 해시 폴더 두 단계 아래에서 보임 (확인 범위: iPhone 13 mini, iOS 27.0) |
| `full_browsing_session_resourceLog.plist` | MVT WebkitSessionResourceLog 모듈이 읽음[2] | 기기 관찰 메모에 없음 |
| `EnhancedSecuritySites.db` | `Library/WebKit/WebsiteData/EnhancedSecurity/` | 보임 (확인 범위: iPhone 13 mini, iOS 27.0) |

`Library/Caches` 는 다시 만들 수 있는 파일을 두는 곳이고, iOS 2.2 이후 로컬 백업에 들어가지 않습니다. 기기를 완전히 복원하면 지워지고, iOS 5.0 이후에는 저장 공간이 아주 부족할 때 시스템이 이 폴더를 지울 수 있습니다[1]. 그래서 앱의 `Cache.db` 는 보통 전체 파일 시스템 추출에서 봅니다. 실제로 관찰한 백업에서도 앱 컨테이너의 `Library/Caches/<번들 ID>/Cache.db` 는 보이지 않았고, 이름이 `Cache.db` 인 파일은 `AppDomainGroup-group.com.apple.PegasusConfiguration :: EngagedCompletions/Cache.db` 하나였는데 표가 `completion_cache_engagement`, `completion_cache_schema_version` 이라 HTTP 캐시와는 다른 DB 입니다 (확인 범위: iPhone 13 mini, iOS 27.0). 한편 `RootDomain :: Library/Caches/locationd/consolidated.db` 처럼 시스템 영역의 Caches 경로 파일은 백업에 들어 있어서 (확인 범위: iPhone 13 mini, iOS 27.0), "Caches 는 백업에 없다" 는 규칙은 앱 컨테이너에 한해 적용해 읽습니다. 백업에 들어가는 폴더 전체 표는 [처음 보는 앱 분석 순서](unknown-apps.md) 에 있습니다.

## 절차

1. **앱의 HTTP 캐시를 엽니다.** `Cache.db` 는 일반 SQLite 3 DB 이고, 표는 `cfurl_cache_blob_data`, `cfurl_cache_response`, `cfurl_cache_receiver_data`, `cfurl_cache_schema_version` 네 개입니다[5]. 요청·응답 본문은 HTTP Content-Encoding 을 푼 상태 그대로 저장되고, 헤더와 HTTP 메서드 같은 메타데이터는 바이너리 plist 로 직렬화되어 저장됩니다[5]. 각 표의 칸 이름과 시각 형식은 이 핸드북에서 아직 확인하지 못해서, 질의하기 전에 표 구조부터 봅니다.

   ```text
   sqlite3 Cache.db
   .tables
   .schema cfurl_cache_response
   .schema cfurl_cache_receiver_data
   .schema cfurl_cache_blob_data
   ```

   메타데이터 칸의 바이너리 plist 는 [속성 목록 파일](../../../01-foundations/data-formats/plist.md) 의 방법으로 풀고, DB 의 지운 영역은 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md) 를 참고해 봅니다.

2. **본문과 헤더를 맞춰 봅니다.** 헤더에는 압축 인코딩이 원래대로 적혀 있지만 본문은 이미 풀린 상태라서 둘이 맞지 않습니다[5]. 본문을 그대로 열면 되고, 헤더의 `Content-Encoding` 이나 `Content-Length` 를 기준으로 본문을 다시 풀거나 길이를 검사하면 어긋납니다.

3. **웹뷰가 접속한 도메인을 봅니다.** MVT 문서는 WebkitResourceLoadStatistics 모듈이 `observations.db` 에서 뽑는 기록이 앱이 접속한 도메인 이름과 시각을 보여 줄 것이라고 적습니다[2]. 관찰한 백업에서 이 파일은 `AppDomain-com.apple.Music`, `AppDomain-com.apple.mobilemail`, `AppDomain-com.apple.mobilesafari` 각각의 `Library/WebKit/WebsiteData/ResourceLoadStatistics/observations.db` 와 `AppDomain-com.apple.mobilesafari :: Library/WebKit/com.apple.purplebuddy/WebsiteData/ResourceLoadStatistics/observations.db` 에 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). Safari 뿐 아니라 웹뷰를 쓰는 앱 컨테이너에도 생긴다는 뜻이라서, 조사 대상 앱의 도메인에서도 같은 경로를 찾아봅니다.

   `ObservedDomains` 표의 칸은 `domainID`, `registrableDomain`, `lastSeen`, `hadUserInteraction`, `mostRecentUserInteractionTime`, `grandfathered`, `isPrevalent`, `isVeryPrevalent`, `dataRecordsRemoved`, `timesAccessedAsFirstPartyDueToUserInteraction`, `timesAccessedAsFirstPartyDueToStorageAccessAPI`, `isScheduledForAllButCookieDataRemoval`, `mostRecentWebPushInteractionTime` 입니다 (확인 범위: iPhone 13 mini, iOS 27.0).

   ```sql
   SELECT registrableDomain, lastSeen, hadUserInteraction,
          mostRecentUserInteractionTime, dataRecordsRemoved
   FROM ObservedDomains
   ORDER BY lastSeen DESC;
   ```

   그 밖에 `OperatingDates(year, month, monthDay)`, `StorageAccessUnderTopFrameDomains`, `SubframeUnderTopFrameDomains`, `SubresourceUnderTopFrameDomains`, `SubresourceUniqueRedirectsFrom`, `SubresourceUniqueRedirectsTo`, `TopFrameLinkDecorationsFrom`, `TopFrameLoadedThirdPartyScripts`, `TopFrameUniqueRedirectsFrom`, `TopFrameUniqueRedirectsTo`, `TopFrameUniqueRedirectsToSinceSameSiteStrictEnforcement`, `TopLevelDomains` 표가 있고, `SubframeUnderTopFrameDomains` 와 `SubresourceUnderTopFrameDomains` 에는 `lastUpdated` 칸이 있습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 이 표들의 칸 의미는 확인하지 못했습니다.

4. **로컬 저장소를 봅니다.** MVT 의 WebkitLocalStorage 모듈은 `WebsiteData/LocalStorage/` 아래 파일을 읽습니다[2]. 관찰한 백업의 Safari 로컬 저장소는 `AppDomain-com.apple.mobilesafari :: Library/WebKit/WebsiteData/Default/<해시>/<해시>/LocalStorage/localstorage.sqlite` 로, 해시 폴더 두 단계 아래에 있었고 표는 `ItemTable(key, value)` 였습니다 (확인 범위: iPhone 13 mini, iOS 27.0). MVT 문서에 적힌 경로와 모양이 달라서, 도구가 파일을 찾지 못하면 `LocalStorage` 라는 폴더 이름으로 컨테이너 전체를 검색합니다. 해시 폴더 두 단계가 각각 무엇을 뜻하는지, 이 구조가 어느 iOS 버전부터 생겼는지는 확인하지 못했습니다.

5. **나머지 WebKit 파일을 확인합니다.** MVT 의 WebkitSessionResourceLog 모듈은 `full_browsing_session_resourceLog.plist` 에서 방문한 도메인이 불러온 리소스 기록을 뽑습니다[2]. `EnhancedSecuritySites.db` 는 `AppDomain-com.apple.Music` 과 `AppDomain-com.apple.mobilesafari` 에서 보였지만 표 구조는 메모에 없고, Safari 사이트별 설정 `AppDomainGroup-group.com.apple.safari :: Library/Safari/PerSitePreferences.db` 도 보였습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 쿠키 파일의 위치와 형식은 이 핸드북에서 아직 확인하지 못했습니다.

## 도구

MVT 는 CacheFiles 모듈로 디스크에 있는 이름이 `Cache.db` 인 DB 를 모두 읽어 앱과 시스템 서비스가 보낸 HTTP 요청·응답을 뽑고, WebkitResourceLoadStatistics·WebkitLocalStorage·WebkitSessionResourceLog 모듈로 WebKit 데이터를 읽습니다[2]. 도구가 정해 둔 경로와 실제 백업의 경로가 다를 수 있어서(4단계), 결과가 비어 있으면 `sqlite3` 로 파일을 직접 열어 확인합니다.

## 함정과 한계

앱의 `Library/Caches` 는 로컬 백업에 들어가지 않고 시스템이 공간이 부족할 때 지울 수도 있어서[1], 캐시가 없다는 사실만으로 사용자가 지웠다거나 앱을 쓰지 않았다고 볼 수 없습니다. 전체 파일 시스템 추출에서도 캐시는 수집 시점에 남아 있던 것만 보여 줍니다.

`observations.db` 의 `lastSeen`, `mostRecentUserInteractionTime` 이 유닉스 초인지 Mac 절대 시각인지는 확인하지 못했습니다. 값 하나를 두 방식으로 모두 바꿔 보고 다른 기록과 맞는 쪽을 고르되, 그 판단 근거를 보고서에 남깁니다. 변환 방법은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 에 있습니다.

`observations.db` 는 Safari 가 아닌 앱 컨테이너에도 생겨서 (확인 범위: iPhone 13 mini, iOS 27.0), 음악 앱이나 메일 앱의 `observations.db` 에 있는 도메인을 Safari 방문 기록으로 읽으면 안 됩니다. 어느 도메인 아래 파일인지를 늘 함께 적습니다.

`Cache.db` 의 헤더와 본문이 어긋나는 점[5] 때문에, 본문 크기를 헤더의 `Content-Length` 와 비교해서 파일이 잘렸다고 판단하면 틀립니다.

## 결과를 어떻게 해석하나

`Cache.db` 의 행은 앱이 그 URL 에 요청을 보냈고 응답을 받아 캐시에 저장했다는 기록이지만, 사용자가 그 화면을 보았다거나 직접 요청했다는 증명은 아닙니다. 앱이 배경에서 받아 둔 응답일 수도 있습니다. 시스템 서비스도 HTTP 캐시를 남기므로[2], 도구가 모아 준 결과에서는 어느 컨테이너의 `Cache.db` 인지 함께 확인합니다. `observations.db` 의 도메인은 그 앱 컨테이너의 웹뷰가 해당 도메인의 리소스를 불러온 흔적이고, 칸 이름에 사용자 상호작용이 들어 있어도 칸의 정확한 뜻을 확인하기 전에는 "사용자가 방문했다" 로 쓰지 않습니다.

보고서에는 "번들 ID `com.example.app` 의 HTTP 캐시에 이 도메인에서 받은 응답이 저장되어 있고, 저장된 본문에는 이러한 내용이 있다" 처럼 기록이 말하는 만큼만 씁니다. 통신 시각과 통신량은 [앱별 데이터 사용량](../../../02-artifacts/network/data-usage.md) 과, 웹 사용 전체 흐름은 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md) 과 함께 맞춰 봅니다.

## 참고 문헌

- [1] Apple Developer, File System Programming Guide — File System Basics (보관 문서) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html
- [2] MVT 문서, iOS Records — https://docs.mvt.re/en/latest/ios/records/
- [5] Silent Signal Techblog, "iOS HTTP cache analysis for abusing APIs and forensics" (2016-05-06) — https://blog.silentsignal.eu/2016/05/06/ios-http-cache-analysis-for-abusing-apis-and-forensics/
