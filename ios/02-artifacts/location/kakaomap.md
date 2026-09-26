---
title: "카카오맵"
parent: "아티팩트 · 위치"
nav_order: 650
---

# 카카오맵 (KakaoMap)

## 한 줄 요약

카카오맵은 카카오가 내는 국내 지도·길찾기 앱이고, 아이폰에서는 번들 ID `net.daum.maps` 로 앱 영역을 찾아 검색·길찾기·즐겨찾기 흔적을 살펴보지만, 앱 안 파일 구조는 공개된 분석 자료가 없어서 찾는 법과 해석 원칙을 중심으로 다룹니다.

## 무엇을 기록하나 · 왜 생기나

카카오맵은 자동차·대중교통·도보·자전거 길찾기와 앱 안 내비게이션을 제공하고, 버스 번호·정류장·장소를 한 창에서 검색하는 통합 검색이 있습니다 [1]. 즐겨찾기, 친구와 위치 공유, 로드뷰 기능도 있습니다 [2]. 사용자가 이런 기능을 쓰면 검색어, 최근 길찾기의 출발지와 도착지, 즐겨찾기 장소 같은 값이 앱 데이터 영역이나 카카오 서버에 남을 수 있어서, 조사에서는 "이 사람이 어디를 찾아봤고 어디로 가려 했나" 를 묻는 단서가 됩니다.

앱이 요구하는 권한은 위치, 음성 검색용 마이크, 리뷰용 카메라·사진, 알림, 건강 데이터 연동이고 [2], App Store 개인정보 항목에 정밀 위치가 들어 있습니다 [2]. 다만 이 표시는 개발사가 스스로 밝힌 내용이라, 기기에 무엇이 어떤 형식으로 남는지는 따로 확인해야 합니다.

기기 안에서 검색 기록·최근 길찾기·즐겨찾기·내비 주행 기록을 어느 파일에 어떤 형식(SQLite·plist 등)으로 두는지, 즐겨찾기를 카카오 계정과 동기화하고 기기에도 사본을 두는지는 실제 데이터로 확인해야 합니다. 이 페이지는 실제 기기에서 이런 파일을 찾아 기록하는 절차를 다룹니다.

## 위치와 버전별 차이

### 앱 식별

| 항목 | 값 | 근거 |
|---|---|---|
| iOS 번들 ID | `net.daum.maps` | [1] |
| App Store 앱 ID | 304608425 (다음 지도 시절부터 같은 ID) | [1] |
| 최초 출시일 | 2009-02-27 | [1] |
| 판매자 · 분류 | Kakao Corp. · Navigation | [1] |

같은 앱 ID 를 다음 지도 때부터 이어 써서, 오래된 기기나 백업에서 앱 이름이 다르게 보여도 번들 ID 로 같은 앱인지 가릴 수 있습니다. 번들 ID 가 무엇이고 앱 그룹과 어떻게 다른지는 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에서 다룹니다.

### 버전

| 카카오맵 판 | 설치 가능한 iOS | 근거 |
|---|---|---|
| 6.29.2 (2026-09-16 기준 최신판) | iOS 17.0 이상 | [1] |
| 그보다 예전 판 | iOS 15·16 기기에 남아 있을 수 있음 | [1] 의 최소 버전에서 추론 |

최신판을 iOS 15·16 에 설치할 수 없어서, iOS 15·16 기기를 조사할 때는 예전 판의 데이터 구조를 보게 됩니다. 앱 판마다 저장 구조가 어떻게 다른지는 알려져 있지 않아서, 분석 대상의 앱 판 번호를 먼저 기록해 두고 판이 다른 기기의 결과와 섞지 않습니다.

### 로컬 백업에서 찾기

로컬 백업의 `Manifest.db` 에는 `Files` 표가 있고 열은 `fileID`, `domain`, `relativePath`, `flags`, `file` 입니다. 앱 영역의 도메인은 `AppDomain-` 뒤에 번들 ID 를 붙이고, 앱 그룹은 `AppDomainGroup-`, 확장은 `AppDomainPlugin-` 으로 시작합니다. 이 형식에 따르면 카카오맵 앱 영역은 `AppDomain-net.daum.maps` 로 찾습니다. 번들 ID 로 짐작한 이름이므로 실제 백업에 이 도메인이 있는지 확인합니다.

백업의 `Info.plist` 에는 `Installed Applications` 키가 있어서 앱 영역을 찾기 전에 카카오맵이 설치 목록에 있는지 먼저 볼 수 있습니다. 백업 폴더 구조는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 설명합니다.

앱 데이터 영역은 `Documents/`, `Library/`, `tmp/` 로 나뉘고 [3], 백업에 들어가는 범위가 폴더마다 다릅니다.

| 폴더 | 로컬·iCloud 백업 | 근거 |
|---|---|---|
| `Documents/` | 들어감 | [3] |
| `Library/` (`Caches` 제외), `Library/Preferences` | 들어감 | [3] |
| `Library/Caches` | 들어가지 않음(iOS 2.2 이후), 기기 전체 복원 때 시스템이 지움 | [3] |
| `tmp/` | 들어가지 않음 | [3] |

지도 타일이나 검색 캐시를 카카오맵이 `Library/Caches` 에 둔다면 로컬 백업에는 없고 파일 시스템 전체 추출에서만 보이지만, 카카오맵이 `Caches` 에 실제로 무엇을 두는지는 추출한 데이터로 확인해야 합니다.

### 파일 시스템 추출에서 찾기

파일 시스템 전체 추출에서는 앱 데이터가 `/private/var/mobile/Containers/Data/Application/` 아래 GUID 이름 폴더에 있어서, 폴더 이름만으로는 어느 앱인지 알 수 없습니다. 폴더 안의 `.com.apple.mobile_container_manager.metadata.plist` 에 소유 번들 ID 가 적혀 있으므로 이 파일에서 `net.daum.maps` 를 찾아 카카오맵 폴더를 찾아냅니다 [4]. 같은 plist 가 `Shared/AppGroup/` 와 `Data/PluginKitPlugin/` 아래 GUID 폴더에도 있어서 앱 그룹·확장 폴더도 같은 방법으로 찾습니다 [4]. FrontBoard 의 `ApplicationState.db` 도 GUID 와 앱을 잇지만 `Shared/AppGroup` 경로는 이 DB 에 없습니다 [4]. 이 DB 는 [설치된 앱](../app-usage/installed-apps.md) 에서 자세히 다룹니다. 파일 시스템 추출 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 를 봅니다.

## 구조

카카오맵 앱 영역 안의 파일 이름, 저장 형식, 표·열 이름, 앱 데이터 암호화 여부는 공개된 분석 자료가 없습니다. 기기에서 찾은 파일은 머리 부분으로 형식을 먼저 판별하고, SQLite 면 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), plist 면 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 의 읽는 법을 따릅니다. 앱 안 파일이 암호화되어 있는지 모를 때 기기 쪽 보호 등급부터 짚어 보려면 [데이터 보호](../../01-foundations/storage/data-protection/index.md) 를 봅니다.

안드로이드판에서는 TMAP 과 카카오맵이 데이터를 모두 평문으로 저장합니다 [5]. 이 결과는 안드로이드에서 얻은 것이라 iOS 판도 평문이라고 보면 안 됩니다.

## 증거로서 의미

**증명하는 것**

- 백업의 설치 목록이나 컨테이너 메타데이터 plist 에 `net.daum.maps` 가 있으면, 수집 시점에 그 기기에 카카오맵이 설치되어 있었다는 사실을 보여 줍니다.
- 앱 영역에서 검색어나 길찾기 기록을 찾았다면, 그 기기의 카카오맵에 해당 장소를 검색하거나 경로를 조회한 기록이 있다는 사실까지 말할 수 있습니다.

**증명하지 못하는 것**

- 장소를 검색하거나 길찾기를 조회한 기록은 그곳에 갔다는 증거가 아닙니다. 실제 이동은 [중요 위치](significant-locations.md) 나 [위치 기록 데몬](routined.md) 같은 시스템 위치 기록과 맞춰 봐야 합니다.
- 즐겨찾기가 카카오 계정과 동기화되는지 알려진 자료가 없어서, 기기에 있는 즐겨찾기를 그 기기에서 직접 추가했다고 단정할 수 없습니다.
- 앱을 누가 조작했는지는 앱 데이터만으로 알 수 없습니다. 사용자 판단은 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.

보고서에는 "카카오맵 앱 영역에 이 장소를 검색한 기록이 있고, 기록의 시각 값은 이것이다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

카카오맵이 시각을 유닉스 시각으로 두는지 Mac 절대 시각으로 두는지는 알려져 있지 않습니다. 시각으로 보이는 숫자를 찾으면 자릿수와 기준 시점을 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 따라 구분해 읽고, 같은 행동을 시스템 기록과 맞춰 기준을 확인한 뒤에 보고서에 씁니다. UTC 로 저장했는지 현지 시각으로 저장했는지도 같은 방법으로 확인하고, 기기 시간대는 [시간대와 시각 설정](../system-account/time-zone.md) 에서 봅니다.

## 함정과 한계

로컬 백업만 받았다면 `Library/Caches` 와 `tmp/` 는 처음부터 없어서 [3], 백업에서 캐시 흔적이 없다고 해서 앱을 쓰지 않았다고 볼 수 없습니다. 기기 전체 복원 때 시스템이 `Caches` 를 지우고, iOS 5.0 이후에는 저장 공간이 아주 모자랄 때도 시스템이 이 폴더를 지울 수 있어서 [3] 파일 시스템 추출에서 캐시가 비어 있어도 사용하지 않았다는 뜻은 아닙니다.

앱 판 번호가 다르면 저장 구조가 다를 수 있고 iOS 15·16 기기에는 예전 판이 있을 수 있어서, 다른 기기나 다른 자료에서 얻은 파일 이름·표 이름을 그대로 적용하지 않습니다. 안드로이드 연구 결과를 iOS 에 옮겨 쓰는 일도 같은 이유로 피합니다.

앱 영역이 비어 있거나 앱이 설치 목록에 없을 때 지우기를 의심한다면 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름으로 확인합니다. 서버에만 있는 기록은 기기에서 볼 수 없고, 계정 데이터 요청은 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 에서 다룹니다.

## 직접 분석해 보기

앱 안 파일 구조가 알려져 있지 않으므로, 먼저 카카오맵 영역에 무슨 파일이 있는지 목록을 뽑는 데서 시작합니다. 로컬 백업이면 `Manifest.db` 를 SQLite 명령행 도구(`sqlite3` 등)로 열고 다음 질의로 도메인과 상대 경로를 뽑습니다.

```sql
SELECT fileID, domain, relativePath, flags
FROM Files
WHERE domain = 'AppDomain-net.daum.maps'
   OR domain LIKE 'AppDomainGroup-%'
   OR domain LIKE 'AppDomainPlugin-%'
ORDER BY domain, relativePath;
```

앱 그룹과 확장 도메인의 그룹 ID 는 카카오맵의 알려진 값이 없어서 위 질의는 전체 그룹·확장 도메인을 뽑고, 결과에서 카카오 쪽으로 보이는 이름을 눈으로 고릅니다. 뽑은 파일은 해당 `fileID` 로 백업 폴더에서 찾아 복사본으로 옮긴 뒤 헥스 편집기로 첫 부분을 보고 형식을 판별합니다. 형식별 머리 부분 값과 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 와 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에 있습니다.

파일 시스템 추출이면 `/private/var/mobile/Containers/Data/Application/` 아래 폴더마다 `.com.apple.mobile_container_manager.metadata.plist` 를 열어 `net.daum.maps` 가 적힌 폴더를 찾습니다 [4]. 찾은 뒤에는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md) 의 절차대로 파일마다 형식·시각 값·내용을 기록합니다. 이렇게 찾은 파일 이름과 표 이름은 기기의 iOS 버전과 카카오맵 판 번호를 함께 적어 두어야 다음 조사에서 비교할 수 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [KnowledgeC](../app-usage/knowledgec/index.md) · [바이옴](../app-usage/biome/index.md) | 번들 ID `net.daum.maps` 로 앱을 언제 앞에 띄웠는지 |
| [화면 사용 시간](../app-usage/screen-time.md) | 카카오맵 사용 시간 |
| [설치된 앱](../app-usage/installed-apps.md) | 설치 여부와 컨테이너 GUID |
| [중요 위치](significant-locations.md) · [위치 기록 데몬](routined.md) | 실제로 머문 장소와 이동 |
| [알림 기록](../app-usage/notifications.md) | 카카오맵이 보낸 알림 |
| [Apple 지도](apple-maps.md) · [네이버 지도](naver-map.md) | 다른 지도 앱으로 같은 장소를 찾았는지 |

앱 실행·사용 시각은 앱 자체 기록과 별도로 시스템 흔적에서 번들 ID 로 찾아 보강할 수 있고, 여러 기록을 시간순으로 합치는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 과 [그 시각에 어디 있었나](../../04-scenarios/activity/location.md) 에서 다룹니다.

## 실습

공개 시험 이미지(NIST CFReDS 등)를 쓸 때는 카카오맵이 들어 있는지부터 확인하고, 없으면 연습용 기기에 앱을 깔고 몇 가지 장소를 검색한 뒤 백업을 떠서 풀어 봅니다.

1. 백업 `Info.plist` 의 `Installed Applications` 에 `net.daum.maps` 가 있습니까?
2. `Manifest.db` 에서 `AppDomain-net.daum.maps` 도메인에 파일이 몇 개 있고, 어떤 폴더(`Documents/`, `Library/`)에 몰려 있습니까?
3. 검색한 장소 이름을 앱 영역 파일에서 찾을 수 있습니까? 찾았다면 그 파일은 어떤 형식이고, 시각 값은 어느 기준으로 읽어야 맞습니까?
4. 같은 시각대에 KnowledgeC 나 바이옴에 카카오맵 사용 기록이 있습니까?
5. 파일 시스템 추출이 있다면 `Library/Caches` 에 백업에 없던 파일이 있습니까?

## 참고 문헌

1. Apple, iTunes Search API 조회 결과 — 카카오맵(id 304608425, 한국 스토어) — https://itunes.apple.com/lookup?id=304608425&country=kr
2. App Store — KakaoMap - Korea No.1 Map — https://apps.apple.com/kr/app/kakaomap-korea-no-1-map/id304608425?l=en
3. Apple Developer, File System Programming Guide — File System Basics — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html
4. Christopher Vance, Magnet Forensics, "iOS - Tracking Bundle IDs for Containers, Shared Containers, and Plugins" (2020-09-29) — https://www.magnetforensics.com/blog/ios-tracking-bundle-ids-for-containers-shared-containers-and-plugins/
5. 박귀은·강수진·김종성, 「안드로이드 환경에서의 지도 애플리케이션 아티팩트 분석 및 복호화 방안 연구」, 디지털포렌식연구 16(2), 2022, 163–184쪽 — https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002859568
