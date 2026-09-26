---
title: "구글 지도"
parent: "아티팩트 · 위치"
nav_order: 720
---

# 구글 지도 (Google Maps)

## 한 줄 요약

구글 지도 (Google Maps) 앱 폴더에는 길찾기 목적지, 길찾기 URL, 저장한 장소, 검색 기록이 서로 다른 파일에 남고, 파일마다 좌표를 적는 방식과 시각 단위가 달라서 하나씩 풀어 한 줄로 맞춰야 "무엇을 찾아보고 어디로 가려 했나" 를 말할 수 있습니다 [1][2][3].

## 무엇을 기록하나 · 왜 생기나

패키지 이름은 `com.google.android.apps.maps` 이고 [1][2][3], 사용자가 장소를 검색하고 길찾기를 하고 장소를 저장하는 동안 앱이 자기 폴더에 기록을 남깁니다. 공개 도구 ALEAPP 가 읽는 기록은 네 가지입니다.

| 기록 | 파일 | 좌표 | 시각 |
|---|---|---|---|
| 길찾기 목적지 | `databases/da_destination_history` | E6 정수, 목적지·출발지 | 유닉스 밀리초 [1] |
| 길찾기 URL | `databases/gmm_storage.db` | URL 안의 숫자 | ALEAPP 는 읽지 않음 [2] |
| 저장한 장소 | `databases/gmm_myplaces.db` | E6 정수 | 유닉스 밀리초 [2] |
| 검색 기록 | `files/new_recent_history_cache_search.cs` | 프로토콜 버퍼 안 | 유닉스 마이크로초 [3] |

사용자가 켠 타임라인 기록은 지도 앱이 아니라 Google Play 서비스 폴더에 있어서 [구글 위치 기록과 타임라인 (Timeline)](google-timeline.md) 페이지에서 따로 다룹니다. ALEAPP 에는 googleLastTrip, googleInitiatedNav, googlemapaudio, googlemapaudioTemp 모듈도 있습니다 [4].

## 위치와 버전별 차이

ALEAPP 는 아래 경로 패턴으로 찾습니다 [1][2][3]. 앱 데이터 영역은 루팅되지 않은 기기에서 adb 일반 권한으로 읽을 수 없고, 짜임새는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 페이지에서 다룹니다.

```
*/com.google.android.apps.maps/databases/da_destination_history*
*/com.google.android.apps.maps/databases/gmm_storage.db*
*/com.google.android.apps.maps/databases/gmm_myplaces.db*
*/com.google.android.apps.maps/files/new_recent_history_cache_search.cs
```

ALEAPP 모듈에 적힌 시험 표본을 보면 기록마다 남는 정도가 다릅니다. 아래 표는 그 일부이고, 빈칸은 모듈에 그 기기 표본이 적혀 있지 않은 칸입니다.

| 표본 기기 | Android | gmm_storage.db [2] | gmm_myplaces.db [2] | 검색 기록 [3] |
|---|---|---|---|---|
| Galaxy S10 | 10 | 2행 | 0행 | 10행 |
| Galaxy S20 | 13 | 1행 | 1행 | 1행 |
| Galaxy A53 | 14 | 0행 | | |
| Pixel 7a | 14 | 4행 | 0행 | 6행 |
| Pixel 8 Pro | 16 | 0행 | 1행 | |

`da_destination_history` 를 읽는 ALEAPP 모듈은 2021년에 만들어졌고 표본 정보가 없습니다 [1]. 현행 지도 앱에 이 DB 가 아직 있는지는 검체에서 확인합니다. 오래된 `gmm_myplaces.db` 에는 `sync_item` 표가 없어서 ALEAPP 가 읽지 못합니다 [2].

## 구조

SQLite 파일 형식은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), 덩어리 안을 읽는 법은 [프로토콜 버퍼 (Protocol Buffers)](../../01-foundations/data-formats/protobuf.md) 페이지에서 다룹니다.

### da_destination_history

표 `destination_history` 에 칸 `time`, `dest_lat`, `dest_lng`, `dest_title`, `dest_address`, `source_lat`, `source_lng` 이 있습니다 [1]. 목적지와 출발지 좌표가 따로 들어 있고, 좌표는 E6 정수라서 끝 여섯 자리 앞에 소수점을 넣어 읽습니다 [1].

### gmm_storage.db

표 `gmm_storage_table` 에 칸 `rowid`, `_data`(바이너리), `_key_pri` 가 있습니다 [2]. `_data` 바이트에서 `/dir/` 로 시작하는 길찾기 URL 조각에 출발 위도·경도가 있고, `!1d` 뒤의 숫자가 도착 경도, `!2d` 뒤의 숫자가 도착 위도입니다 [2]. 순서가 경도 먼저라는 점을 놓치면 위도와 경도가 뒤바뀝니다.

### gmm_myplaces.db

표 `sync_item` 에 칸 `key_string`, `latitude`, `longitude`, `sync_item`(프로토콜 버퍼), `timestamp` 가 있습니다 [2]. `latitude`·`longitude` 는 E6 정수라서 0.000001 을 곱하고, 그 밖의 라벨·주소·URL 은 `sync_item` 덩어리의 필드 6 아래에서 읽습니다 [2].

| 필드 | 뜻 |
|---|---|
| 6 → 7 | 라벨 |
| 6 → 2 | 주소 |
| 6 → 6 | URL |

ALEAPP 는 `key_string` 이 `0:0` 이면 Home, `1:0` 이면 Work 로 표시하지만, 이 대응은 데이터에 적혀 있지 않고 근거도 없습니다 [2]. 라벨이 붙었다고 실제 집이나 직장이라는 뜻은 아닙니다 [2].

### new_recent_history_cache_search.cs

파일 앞 8바이트를 건너뛴 뒤를 프로토콜 버퍼로 읽습니다 [3]. 그 8바이트의 뜻은 알려져 있지 않습니다. 항목마다 아래 필드가 있습니다 [3].

| 필드 | 뜻 |
|---|---|
| 2 | 검색 시각 |
| 4 → 1 | 장소 이름 |
| 4 → 5, 또는 4 → 6 → 1 | 좌표 |
| 11 | URL |

## 증거로서 의미

**증명하는 것**

`destination_history` 한 행은 그 시각에 이 앱에서 목적지를 정한 기록이고, 출발지 좌표가 함께 있으면 그때 폰이 있던 곳을 어림하는 단서가 됩니다. 검색 기록 한 항목은 그 시각에 앱에서 장소를 찾아본 기록입니다. `gmm_myplaces.db` 한 행은 저장한 장소 하나의 좌표와 라벨이고, 행마다 시각 값이 붙어 있습니다. `gmm_storage.db` 의 길찾기 URL 은 출발지와 도착지 좌표 쌍을 알려 줍니다.

**증명하지 못하는 것**

목적지를 정하거나 검색했다는 기록은 그곳에 실제로 갔다는 증거가 아닙니다. 출발지 좌표도 길찾기에서 사용자가 고른 출발지일 수 있어서, 확인하지 않고 폰의 위치로 쓰면 안 됩니다. `gmm_storage.db` 의 URL 에는 ALEAPP 가 시각을 읽지 않으니 [2] 언제 한 길찾기인지는 다른 기록으로 맞춰야 합니다. Home·Work 표시는 도구가 붙인 이름이라서 [2] 그곳이 실제 주소나 직장이라는 근거가 되지 않습니다. 저장한 장소는 계정에 동기화되는 기록일 수 있어서, 이 기기에서 저장했는지는 따로 확인해야 합니다.

## 시각 해석

같은 앱 안에서 기록마다 단위가 다릅니다. `destination_history.time` 과 `sync_item.timestamp` 는 유닉스 밀리초이고 [1][2], 검색 기록의 필드 2 는 유닉스 마이크로초라서 1,000,000 으로 나눠야 초가 됩니다 [3]. 검색 기록을 밀리초로 잘못 나누면 먼 미래의 날짜가 나와서 한눈에 알아챌 수 있지만, 여러 기록을 한 타임라인에 올릴 때는 단위를 먼저 맞춥니다. 유닉스 시각은 UTC 기준이고, 값을 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md), 현지 시각으로 옮기는 기준은 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 페이지에 있습니다.

`sync_item.timestamp` 가 장소를 처음 저장한 때인지 마지막으로 동기화한 때인지는 알려져 있지 않습니다. 보고서에는 "이 행의 시각 값" 이라고만 씁니다.

## 함정과 한계

첫째, 이 페이지의 경로·표·필드 번호는 ALEAPP 가 이렇게 읽는다는 사실이고, 모든 지도 앱 판에서 그렇게 저장한다는 보증은 아닙니다. 표본에서도 같은 파일이 기기에 따라 0행이었습니다 [2].

둘째, 좌표 방식이 셋으로 나뉩니다. DB 칸은 E6 정수이고 [1][2], URL 은 문자열 안에 숫자가 적혀 있으며 [2], 검색 기록은 프로토콜 버퍼 안에 도 단위 실수(double)로 들어 있습니다 [3]. 타임라인 쪽 기록은 E7 정수라서, 두 앱의 좌표를 비교할 때 자릿수를 맞추지 않으면 열 배 어긋납니다.

셋째, Home·Work 라벨을 그대로 보고서에 옮기지 않습니다 [2].

넷째, 사용자가 앱에서 기록을 지웠을 때 이 파일들에 무엇이 남는지는 공개 자료가 없어 검체에서 확인합니다. SQLite 에서 지운 행을 찾는 방법은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md) 페이지에 있고, 원본이 아니라 사본을 열고 `-wal` 파일도 함께 복사합니다.

## 직접 분석해 보기

### 값과 SQL 로 한 번

아래는 위 구조로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다. `dest_lat` 이 37566500 이면 끝 여섯 자리 앞에 소수점을 넣어 37.566500 도가 되고, `time` 이 1700000000000 이면 1000 으로 나눈 1700000000 초가 2023-11-14 22:13:20 UTC 입니다.

```sql
SELECT datetime(time / 1000, 'unixepoch') AS utc_time,
       dest_title, dest_address,
       dest_lat / 1000000.0   AS dest_lat_deg,
       dest_lng / 1000000.0   AS dest_lng_deg,
       source_lat / 1000000.0 AS src_lat_deg,
       source_lng / 1000000.0 AS src_lng_deg
FROM destination_history
ORDER BY time;
```

`gmm_storage.db` 는 `_data` 칸을 헥스로 열어 `/dir/` 문자열을 찾고, 그 뒤에서 `!1d`·`!2d` 를 찾아 숫자를 읽습니다. 검색 기록 파일은 헥스 편집기로 열어 앞 8바이트를 떼어 낸 나머지를 프로토콜 버퍼 도구에 넘기고, 필드 2 의 정수를 1,000,000 으로 나눠 초로 바꿉니다.

### 공개 도구로 한 번

ALEAPP 의 googlemaplocation 모듈이 `da_destination_history` 를 [1], googleMapsGmm 모듈이 `gmm_storage.db` 와 `gmm_myplaces.db` 를 [2], googleMapsSearches 모듈이 검색 기록을 [3] 표로 만들어 줍니다. 도구가 낸 좌표 몇 개를 위처럼 직접 풀어 맞춰 보는 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 페이지에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [구글 위치 기록과 타임라인 (Timeline)](google-timeline.md) | 길찾기 목적지 근처에 뒤이어 방문 구간이 있는지 |
| [위치 캐시 (Cached Locations)](cached-locations.md) | 길찾기 시각 뒤에 GPS 가 켜진 구간이 있는지 |
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | 검색·길찾기 시각에 지도 앱이 앞에 있었는지 |
| [크롬 (Chrome for Android)](../browsers/chrome/index.md) | 같은 장소를 브라우저에서도 찾아봤는지 |
| [계정 (Accounts)](../system-account/accounts/index.md) | 저장한 장소가 동기화될 구글 계정이 무엇인지 |

앱 폴더를 체계적으로 살피는 방법은 [앱 데이터 분석 (App Data Analysis)](../../03-techniques/analysis/app-data-analysis/index.md), 조사 흐름은 [그 시각에 어디 있었나 (Location)](../../04-scenarios/activity/location.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 검체에 `com.google.android.apps.maps` 폴더가 있으면 아래 질문을 풀어 봅니다.

1. 위 네 파일 가운데 어느 파일이 있고, 각각 기록이 몇 건입니까?
2. `destination_history` 에서 가장 최근 목적지는 어디이고, 출발지 좌표는 목적지에서 대략 얼마나 떨어져 있습니까?
3. 검색 기록의 가장 이른 시각과 가장 늦은 시각은 언제이고, 마이크로초를 밀리초로 잘못 나누면 어떤 날짜가 나옵니까?
4. `gmm_myplaces.db` 에 `key_string` 이 `0:0` 인 행이 있다면, 다른 기록 가운데 그 좌표 근처에 자주 나오는 곳이 있습니까?

## 참고 문헌

1. ALEAPP — scripts/artifacts/googlemaplocation.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/googlemaplocation.py
2. ALEAPP — scripts/artifacts/googleMapsGmm.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/googleMapsGmm.py
3. ALEAPP — scripts/artifacts/googleMapsSearches.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/googleMapsSearches.py
4. ALEAPP — scripts/artifacts 폴더 목록 — https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
