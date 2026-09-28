---
title: "네이버 앱"
parent: "아티팩트 · 인터넷·브라우저"
nav_order: 780
---

# 네이버 앱 (NAVER)

네이버 앱은 검색과 웹 보기를 함께 하는 앱이지만, 앱 안에 남는 검색·방문 기록의 파일 구조는 앱 컨테이너를 직접 열어 확인합니다.

## 무엇을 기록하나 · 왜 생기나

App Store 에서 판매자는 NAVER Corp., 앱 ID 는 `id393499958` 이고, 설명에는 검색 홈·콘텐츠·음성 검색·"내 주변" 검색 기능이 적혀 있습니다 [1]. App Store 개인정보 표시에는 사용자와 연결된 데이터로 검색 기록, 방문 기록, 위치(정확한 위치·대략적 위치)가 적혀 있습니다 [1]. 이 표시는 개발자가 알린 수집 범위라서 서버 쪽 수집만 나타낼 뿐이고, 기기 안에 무엇이 어떤 파일로 남는지는 나와 있지 않습니다. 표시 항목은 앱 판마다 바뀔 수 있으니 보고서에 인용할 때는 그 시점 화면을 다시 확인합니다.

앱 안에서 웹 페이지를 열면 WebKit 이 화면을 그립니다. App Store 심사 지침 2.5.6 은 웹을 탐색하는 앱이 WebKit 을 쓰도록 정하고 있고 [2], 자세한 내용은 [크롬](chrome.md) 에 정리했습니다.

## 위치와 버전별 차이

2026년 9월 App Store 판은 12.23.72 이고, 최소 요구 버전은 iOS 17.0 이상입니다 [1]. 이 값은 앱을 고칠 때마다 자주 바뀌니, 분석 대상 기기의 iOS 버전과 앱 판을 먼저 적어 둡니다.

번들 ID 는 분석 대상 기기에서 찾습니다. [설치된 앱](../app-usage/installed-apps.md) 기록에서 번들 ID 와 컨테이너 UUID 를 먼저 찾고, 로컬 백업이라면 `Manifest.db` 의 `Files` 표에서 `AppDomain-` 뒤에 그 번들 ID 가 붙은 도메인을 찾습니다. `Files` 표의 열은 `fileID`, `domain`, `relativePath`, `flags`, `file` 입니다. 번들 ID 와 앱 그룹 컨테이너의 관계는 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 을, 백업 도메인 규칙은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 을 봅니다.

검색 기록·방문 기록이 들어가는 DB 이름, 표·열 이름, plist 키, 앱 그룹 이름은 앱 컨테이너 파일을 열어 확인해야 해서, 이 페이지에는 경로 대신 판별 방법을 적습니다.

## 구조

앱 고유 파일과 별개로, WebKit 을 쓰는 앱의 컨테이너에는 `Library/WebKit/WebsiteData/` 아래 파일이 생길 수 있습니다. Apple 앱(음악·메일·사파리) 컨테이너에는 다음 두 파일이 있습니다.

```
Library/WebKit/WebsiteData/ResourceLoadStatistics/observations.db
Library/WebKit/WebsiteData/EnhancedSecurity/EnhancedSecuritySites.db
```

두 파일 모두 SQLite 이고([SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)), 주요 표와 열은 다음과 같습니다. `observations.db` 에는 이 밖에도 `SubresourceUniqueRedirectsFrom`, `SubresourceUniqueRedirectsTo`, `TopFrameUniqueRedirectsToSinceSameSiteStrictEnforcement` 표가 있습니다.

| 파일 | 표 | 열 |
|---|---|---|
| `observations.db` | `ObservedDomains` | `domainID`, `registrableDomain`, `lastSeen`, `hadUserInteraction`, `mostRecentUserInteractionTime`, `grandfathered`, `isPrevalent`, `isVeryPrevalent`, `dataRecordsRemoved`, `timesAccessedAsFirstPartyDueToUserInteraction`, `timesAccessedAsFirstPartyDueToStorageAccessAPI`, `isScheduledForAllButCookieDataRemoval`, `mostRecentWebPushInteractionTime` |
| `observations.db` | `OperatingDates` | `year`, `month`, `monthDay` |
| `observations.db` | `TopFrameUniqueRedirectsFrom` | `targetDomainID`, `fromDomainID` |
| `observations.db` | `TopFrameUniqueRedirectsTo` | `sourceDomainID`, `toDomainID` |
| `observations.db` | `SubframeUnderTopFrameDomains` | `subFrameDomainID`, `lastUpdated`, `topFrameDomainID` |
| `observations.db` | `SubresourceUnderTopFrameDomains` | `subresourceDomainID`, `lastUpdated`, `topFrameDomainID` |
| `observations.db` | `TopFrameLinkDecorationsFrom` | `toDomainID`, `lastUpdated`, `fromDomainID` |
| `observations.db` | `TopFrameLoadedThirdPartyScripts` | `topFrameDomainID`, `subresourceDomainID` |
| `observations.db` | `StorageAccessUnderTopFrameDomains` | `domainID`, `topLevelDomainID` |
| `observations.db` | `TopLevelDomains` | `topLevelDomainID` |
| `EnhancedSecuritySites.db` | `sites` | `site`, `enhanced_security_state`, `last_modified` |

`ObservedDomains` 는 주소 전체가 아니라 `registrableDomain` 열에 도메인을 적고, 다른 표는 `domainID` 번호로 이 표를 가리킵니다. 네이버 앱 컨테이너에 같은 파일이 생기는지는 실제 데이터로 확인합니다.

## 증거로서 의미

**증명하는 것.** 네이버 앱 컨테이너에서 `observations.db` 를 찾았다면 `registrableDomain` 은 그 앱의 WebKit 데이터에 그 도메인이 적혀 있다는 것을 보여 주고, `hadUserInteraction` 은 열 이름대로 사용자 조작이 있었는지를 적는 열입니다. 위치 권한이 있는 앱은 시스템 위치 서비스의 `Library/Caches/locationd/clients.plist`(RootDomain) 에 번들 ID 로 한 항목씩 적히고, 앱 항목의 키 이름은 `BundleId`, `BundlePath`, `ClientStorageToken`, `Executable`, `PluginBundleIds`, `SupportedAuthorizationMask`, `SuppressShowingInSettings`, `Tombstones`, `VersionVector` 등입니다. 그래서 "내 주변" 검색처럼 위치를 쓰는 기능이 있는 앱이 이 파일에 적혀 있는지 볼 수 있습니다.

**증명하지 못하는 것.** 도메인 단위 기록은 어떤 페이지를 봤는지, 무엇을 검색했는지 알려 주지 않습니다. App Store 개인정보 표시에 검색 기록이 있다고 해서 기기 안에 검색어가 남는다고 볼 수 없고, 반대로 기기에서 검색어를 찾지 못했다고 해서 검색하지 않았다고 쓸 수도 없습니다.

보고서에는 "네이버에서 무엇을 검색했다" 가 아니라 "네이버 앱 컨테이너의 이 파일에 이 도메인 기록이 있다" 처럼 파일과 열을 밝혀 씁니다.

## 시각 해석

`observations.db` 의 `lastSeen`, `mostRecentUserInteractionTime`, `lastUpdated` 와 `EnhancedSecuritySites.db` 의 `last_modified` 가 어떤 기준의 시각인지는 실제 데이터로 확인해야 합니다. 값의 크기로 기준을 짐작하는 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있고, 다른 기록의 시각과 맞춰 본 뒤에 보고서에 씁니다. `OperatingDates` 는 열이 `year`, `month`, `monthDay` 로 나뉘어 날짜만 적는 표입니다.

## 함정과 한계

App Store 표시대로 검색 기록을 사용자와 연결해 수집한다면 기기 밖에도 기록이 있을 수 있지만, 이 핸드북은 기기 흔적만 다룹니다. 서버 데이터를 받는 절차는 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 를 봅니다.

앱이 없다는 것만으로 기록이 없다고 판단하지 말고, 앱 밖의 흔적(아래 교차 검증)을 봅니다.

`Library/WebKit/WebsiteData/` 파일은 네이버 앱만의 것이 아니고 WebKit 을 쓰는 앱이면 어디에나 생길 수 있습니다(예: 음악·메일·사파리). 그래서 파일 경로만 보지 말고 파일이 들어 있는 백업 도메인(`AppDomain-...`) 으로 어느 앱의 기록인지 확인합니다.

같은 네이버 계열이라도 네이버 지도와 네이버 MYBOX 는 다른 앱이라서 따로 봅니다. [네이버 지도](../location/naver-map.md), [네이버 MYBOX](../mail-cloud/mybox.md) 를 봅니다.

## 직접 분석해 보기

파일 구조를 모르는 앱은 컨테이너 파일을 하나씩 열어 형식부터 구분합니다. 전체 절차는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md) 에서 다룹니다.

**헥스로 한 번.** 아래는 명세로 만든 예시이고 실제 기기에서 뽑은 값이 아닙니다. 확장자가 없는 파일도 맨 앞 바이트로 형식을 구분할 수 있습니다. SQLite 는 `SQLite format 3` 과 0x00 으로 시작하고, 이진 plist 는 `bplist00` 으로 시작합니다.

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
00000000  62 70 6C 69 73 74 30 30                            bplist00
```

SQLite 로 보이면 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), plist 로 보이면 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 방식으로 읽습니다.

**공개 도구로 한 번.** 로컬 백업이라면 사본 `Manifest.db` 에서 도메인별 파일 목록을 뽑습니다. 번들 ID 는 분석 대상 기기의 설치 앱 기록에서 확인한 값을 넣습니다.

```sql
SELECT fileID, relativePath FROM Files
WHERE domain LIKE 'AppDomain-%'   -- 확인한 번들 ID 로 좁힌다
ORDER BY relativePath;
```

찾은 `observations.db` 는 사본을 SQLite 셸로 열어 다음처럼 도메인 목록을 봅니다.

```sql
SELECT domainID, registrableDomain, lastSeen, hadUserInteraction, mostRecentUserInteractionTime
FROM ObservedDomains
ORDER BY lastSeen;
```

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [설치된 앱](../app-usage/installed-apps.md) | 번들 ID 와 컨테이너 UUID |
| [KnowledgeC](../app-usage/knowledgec/index.md), [바이옴](../app-usage/biome/index.md) | 네이버 앱이 앞에 떠 있던 시간대 |
| [화면 사용 시간](../app-usage/screen-time.md) | 그날 앱 사용 시간 |
| [알림 기록](../app-usage/notifications.md) | 네이버 앱 알림 |
| [앱별 데이터 사용량](../network/data-usage.md) | 앱이 그 무렵 통신했는지 |
| [사파리](safari/index.md), [크롬](chrome.md) | 같은 도메인을 다른 브라우저에서도 열었는지 |

여러 앱의 웹 기록을 한 흐름으로 묶는 방법은 [웹 사용 행위 재구성](../../04-scenarios/activity/web-activity.md) 에 있습니다.

## 실습

공개 시험 데이터(NIST CFReDS 등) 가운데 네이버 앱이 설치된 것을 골라 다음을 풀어 봅니다.

1. 설치 앱 기록에서 네이버 앱의 번들 ID 를 찾고, `Manifest.db` 에서 그 도메인 파일을 모두 뽑아 봅니다.
2. 뽑은 파일을 맨 앞 바이트로 SQLite·plist·그 밖으로 나눠 봅니다.
3. 컨테이너에 `Library/WebKit/WebsiteData/` 가 있는지, 있다면 `ObservedDomains` 에 어떤 도메인이 있는지 적어 봅니다.
4. `locationd/clients.plist` 에 네이버 앱 항목이 있는지 확인해 봅니다.

## 참고 문헌

1. App Store (한국), 네이버 - NAVER (2026-09-25 열람) — https://apps.apple.com/kr/app/%EB%84%A4%EC%9D%B4%EB%B2%84-naver/id393499958
2. Apple Developer, App Review Guidelines (2.5.6) — https://developer.apple.com/app-store/review/guidelines/
