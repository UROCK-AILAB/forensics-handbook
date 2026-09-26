---
title: "네이버 지도"
parent: "아티팩트 · 위치"
nav_order: 640
---

# 네이버 지도 (NAVER Map)

## 한 줄 요약

네이버 지도는 NAVER Corp. 가 내는 국내 지도·길찾기 앱이고, 앱 안 파일 구조와 iOS 번들 ID 가 공개된 자료에 없어서, 이 페이지는 앱을 찾아 기록하는 절차와 앱 밖에 남는 공통 위치 흔적을 중심으로 다룹니다.

## 무엇을 기록하나 · 왜 생기나

App Store 의 앱 이름은 "네이버지도 - 장소의 발견과 예약, 내비게이션" 이고, 개발사는 NAVER Corp., App Store ID 는 311867728 입니다 [1]. 앱은 길찾기(내비게이션), 대중교통 길찾기와 도착 알림, 거리뷰, 장소 저장, Clova 음성 명령 기능을 제공합니다 [1]. 사용자가 이런 기능을 쓰면 검색어, 저장한 장소, 길찾기 출발지·도착지 같은 값이 기기나 네이버 서버에 남을 수 있어서, 조사에서는 "어디를 찾아봤고 어디로 가려 했나" 를 묻는 단서가 됩니다.

App Store 의 개인정보 항목에는 추적에 쓰는 데이터로 식별자가, 사용자와 연결된 데이터로 위치(정밀·대략), 연락처 정보, 검색 기록, 사용 데이터, 사진·동영상·사용자 콘텐츠, 진단, 사용자 ID 가 적혀 있습니다 [1]. 이 표시는 개발사가 스스로 밝힌 내용이라서, 위치와 검색 기록이 기기의 어느 파일에 어떤 형식으로 남는지는 따로 확인해야 합니다.

앱 안의 DB·plist 이름, 최근 검색·저장 장소·길찾기 기록을 저장하는 방식, 시각 형식은 실제 데이터로 확인해야 합니다.

## 위치와 버전별 차이

### 앱 식별과 버전

| 항목 | 값 | 근거 |
|---|---|---|
| App Store ID | 311867728 | [1] |
| 개발사 | NAVER Corp. | [1] |
| App Store 표시 앱 판 | 6.10.2 | [1] |
| 설치 가능한 iOS | 16.0 이상 | [1] |
| iOS 번들 ID | 공개 자료 없음 | — |

최신판은 iOS 16.0 이상에만 설치할 수 있어서 [1], iOS 15 기기에는 그보다 예전 판이 있을 수 있습니다. 판마다 저장 구조가 어떻게 다른지 알려져 있지 않으니 기기에 설치된 앱의 판 번호를 먼저 기록해 둡니다.

### 로컬 백업에서 찾기

번들 ID 가 알려져 있지 않으므로, `Manifest.db` 의 `Files` 표에서 도메인 이름에 `naver` 나 `nhn` 이 들어간 것을 모두 뽑아 후보로 삼고, 후보마다 안의 파일을 열어 지도 앱의 것인지 확인합니다.

위치 권한 기록 `RootDomain :: Library/Caches/locationd/clients.plist` 에는 `icom.nhncorp.NaverSearch:` 항목이 있을 수 있는데, 이 항목은 네이버 앱(검색)의 것이고 네이버 지도가 아닙니다. 번들 ID 가 비슷해 보인다고 같은 앱으로 섞지 않고, 네이버 앱은 [네이버 앱](../browsers/naver.md) 에서 따로 다룹니다.

앱 영역 폴더(`Documents/`, `Library/`, `Library/Caches`, `tmp/`)마다 백업에 들어가는 범위가 다르다는 점과 파일 시스템 전체 추출에서 GUID 폴더를 앱과 잇는 방법은 [카카오맵](kakaomap.md) 과 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 설명하고, 네이버 지도에도 같은 방법을 씁니다.

## 구조

앱 안 파일의 이름, 형식, 표·열 이름, 암호화 여부는 공개된 분석 자료가 없습니다. 찾은 파일은 머리 부분으로 형식을 먼저 판별하고, SQLite 면 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), plist 면 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 의 읽는 법을 따릅니다.

앱 밖에서는 두 가지 공통 흔적을 볼 수 있습니다. 첫째, `clients.plist` 에는 앱별 항목이 있고 키에 `Authorization`, `LocationTimeStopped` 등이 있어서 네이버 지도 항목을 찾으면 위치 권한과 위치 사용 흔적을 짐작할 수 있습니다. 이 파일은 [위치 기록 데몬](routined.md) 에서 다룹니다. 둘째, 앱이 위치를 요청한 기록은 [전원 로그](../app-usage/powerlog.md) 에 앱·서비스별로 남습니다 [2].

## 증거로서 의미

**증명하는 것**

- 설치 목록이나 앱 도메인에서 네이버 지도를 찾으면, 수집 시점에 그 기기에 앱이 설치되어 있었다는 사실을 보여 줍니다.
- 앱 영역에서 검색어나 길찾기 기록을 찾았다면, 그 기기의 네이버 지도에 그 장소를 검색하거나 경로를 조회한 기록이 있다는 사실까지 말할 수 있습니다.
- `clients.plist` 나 전원 로그에 네이버 지도 항목이 있으면, 그 앱이 위치 서비스를 쓴 흔적이 있다는 사실을 보여 줍니다.

**증명하지 못하는 것**

- 검색이나 길찾기 기록은 그곳에 갔다는 증거가 아닙니다. 실제 이동은 [중요 위치](significant-locations.md) 와 [위치 기록 데몬](routined.md) 으로 확인합니다.
- 저장한 장소가 네이버 계정과 동기화되는지 알려진 자료가 없어서, 기기에 있는 저장 장소를 그 기기에서 직접 추가했다고 단정할 수 없습니다.
- 누가 앱을 조작했는지는 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 따로 따집니다.

보고서에는 "네이버 지도 앱 영역에 이 장소를 검색한 기록이 있고, 기록의 시각 값은 이것이다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

앱이 시각을 유닉스 시각으로 두는지 Mac 절대 시각으로 두는지는 알려져 있지 않습니다. 시각으로 보이는 숫자를 찾으면 자릿수와 기준 시점을 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 따라 판별하고, 같은 행동을 시스템 기록과 맞춰 기준을 확인한 뒤에 씁니다. UTC 인지 현지 시각인지도 같은 방법으로 확인하고, 기기 시간대는 [시간대와 시각 설정](../system-account/time-zone.md) 에서 봅니다.

## 함정과 한계

번들 ID 가 알려져 있지 않아서, 이름이 비슷한 네이버 앱이나 다른 네이버 서비스 앱의 흔적을 네이버 지도로 잘못 잇기 쉽습니다. 후보 도메인은 안의 파일 내용으로 확인한 뒤에만 네이버 지도로 적습니다.

개인정보 항목에 위치와 검색 기록이 사용자와 연결된 데이터로 적혀 있어서 [1], 기기에 없는 기록은 계정 데이터 요청으로 확인할 수 있는지 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 에서 검토합니다. 앱을 지웠거나 기록을 지운 것이 의심되면 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름을 따릅니다.

## 직접 분석해 보기

### 헥스로 한 번

찾은 파일을 복사본으로 옮긴 뒤 헥스 편집기로 첫 부분을 보고 형식을 판별합니다. 검색해 본 장소 이름을 UTF-8 바이트로 바꿔 파일 안에서 찾으면, 형식을 모르는 파일에서도 검색어가 평문으로 들어 있는지 확인할 수 있습니다. 한글 검색어를 UTF-8 바이트로 찾는 예시는 [Apple 지도](apple-maps.md) 에 있습니다.

### 공개 도구로 한 번

로컬 백업이면 `Manifest.db` 를 `sqlite3` 로 열고 후보 도메인을 뽑습니다.

```sql
SELECT fileID, domain, relativePath
FROM Files
WHERE lower(domain) LIKE '%naver%' OR lower(domain) LIKE '%nhn%'
ORDER BY domain, relativePath;
```

결과에서 지도 앱으로 보이는 도메인을 골라 파일을 꺼내고, [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md) 의 절차대로 파일마다 형식·시각 값·내용을 기록합니다. 찾은 번들 ID, 파일 이름, 표 이름은 기기의 iOS 버전과 앱 판 번호와 함께 적어 두어야 다음 조사에서 비교할 수 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [KnowledgeC](../app-usage/knowledgec/index.md) · [바이옴](../app-usage/biome/index.md) | 앱을 앞에 띄운 시각 |
| [화면 사용 시간](../app-usage/screen-time.md) | 앱 사용 시간 |
| [설치된 앱](../app-usage/installed-apps.md) | 설치 여부와 번들 ID |
| [전원 로그](../app-usage/powerlog.md) | 앱이 위치를 요청한 시간대 |
| [알림 기록](../app-usage/notifications.md) | 대중교통 도착 알림 같은 앱 알림 |
| [중요 위치](significant-locations.md) · [위치 기록 데몬](routined.md) | 실제로 머문 장소와 이동 |
| [Apple 지도](apple-maps.md) · [카카오맵](kakaomap.md) | 다른 지도 앱으로 같은 장소를 찾았는지 |

## 실습

공개 시험 이미지(NIST CFReDS 등)에 네이버 지도가 없으면, 연습용 기기에 앱을 깔고 장소 몇 곳을 검색·저장한 뒤 백업을 떠서 풀어 봅니다.

1. `Manifest.db` 에서 `naver`·`nhn` 이 들어간 도메인은 몇 개이고, 그중 네이버 지도의 것은 어느 것입니까? 그렇게 판단한 근거는 무엇입니까?
2. 네이버 지도의 번들 ID 는 무엇이고, `clients.plist` 에 그 번들 ID 항목이 있습니까?
3. 검색한 장소 이름을 앱 영역 파일에서 찾을 수 있습니까? 찾았다면 어떤 형식의 파일입니까?
4. 저장한 장소 기록에 시각 값이 있다면 어느 기준으로 읽어야 검색한 시각과 맞습니까?
5. 같은 시각대에 KnowledgeC 나 바이옴에 네이버 지도 사용 기록이 있습니까?

## 참고 문헌

1. App Store(한국), "네이버지도 - 장소의 발견과 예약, 내비게이션" — https://apps.apple.com/kr/app/%EB%84%A4%EC%9D%B4%EB%B2%84%EC%A7%80%EB%8F%84-%EC%9E%A5%EC%86%8C%EC%9D%98-%EB%B0%9C%EA%B2%AC%EA%B3%BC-%EC%98%88%EC%95%BD-%EB%82%B4%EB%B9%84%EA%B2%8C%EC%9D%B4%EC%85%98/id311867728
2. Sarah Edwards, mac4n6.com, "On the Tenth Day of APOLLO ... iOS Location Analysis" (2018-12-23) — http://www.mac4n6.com/blog/2018/12/23/on-the-tenth-day-of-apollo-my-true-love-gave-to-me-an-oddly-detailed-map-of-my-recent-travels-ios-location-analysis
