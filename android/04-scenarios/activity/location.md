---
title: "그 시각에 어디 있었나"
parent: "시나리오 · 행위 재구성"
nav_order: 1590
---

# 그 시각에 어디 있었나 (Location)

## 조사 질문

"사건이 난 밤 10시에 이 폰은 어디에 있었나", "그날 오후 회사에서 나와 어디로 갔나", "피의자가 말한 알리바이 장소와 기기 위치가 맞나" 같은 질문에 답하는 흐름입니다. Android 기기에는 좌표와 시각을 한데 적은 기록이 여러 곳에 흩어져 있고, 저장소마다 좌표 형식·시각 단위·정확도·보관 방식이 달라서 이 페이지는 어떤 기록을 어떤 순서로 모아 한 지도 위에 올리는지를 다룹니다.

기록은 "이 시각에 기기가 이 반경 안에 있었다고 적혀 있다" 까지 알려 주고, 기기를 누가 들고 있었는지는 알려 주지 않습니다. 기기 위치는 사람의 위치가 아니라서 사람을 가리는 일은 [그 시각에 폰을 쓴 사람이 누구인가](user-attribution.md) 에서 이어 갑니다. 기지국 위치 기록처럼 통신사가 가진 자료는 이 핸드북에서 다루지 않습니다.

## 먼저 확인할 것

- **OS 버전과 제조사** — 구글 기기 내 위치 기록은 ALEAPP 시험 표본 여러 대에 수백~수천 행이 있었지만 삼성 두 대(Galaxy A53 Android 14, Galaxy S20 Android 13)에서는 0행이었습니다 [2][3]. 삼성 기기에서는 이 저장소가 비어 있을 수 있으므로 원인은 단정하지 말고 다른 기록으로 넘어갈 준비를 합니다.
- **설정** — 구글 타임라인은 계정에서 기본으로 꺼져 있고 사용자가 동의해야 켜집니다 [1]. 관찰 기기의 settings secure 에는 `location_mode`, `mock_location`, `location_changer`, `skyhook_location_enabled`, `trusted_locations_count` 키 이름이, settings global 에는 `assisted_gps_enabled`, `wifi_scan_always_enabled` 키 이름이 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 값과 뜻은 확인하지 못했으므로 키가 있다는 사실만 적고, 값은 [설정 값](../../02-artifacts/system-account/settings.md) 에서 따로 풉니다.
- **시간대** — 저장소마다 시각 단위가 달라 모두 UTC 로 바꾼 뒤 현지 시각을 붙입니다([시각 값](../../01-foundations/value-decoding/time-values.md), [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md)).
- **수집 범위** — 구글 Play 서비스와 지도 앱의 저장소는 앱 데이터 영역에 있어 adb 일반 권한으로는 보이지 않고, 관찰 메모에도 들어 있지 않습니다. 계정 쪽 타임라인은 기기 밖 자료라서 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 의 절차로 따로 받습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 구글 기기 내 위치 기록 (`odlh-storage.db`, `app_semanticlocation_rawsignal_db`) | 머문 곳·이동 구간, 좌표와 정확도가 붙은 개별 위치 | [구글 위치 기록과 타임라인](../../02-artifacts/location/google-timeline.md), [위치 캐시](../../02-artifacts/location/cached-locations.md) |
| 2 | 지도 앱 기록 | 길찾기 목적지, 저장한 장소, 검색어 | [구글 지도](../../02-artifacts/location/google-maps.md), [네이버 지도](../../02-artifacts/location/naver-map.md), [카카오맵](../../02-artifacts/location/kakaomap.md) |
| 3 | 사진 EXIF 위치 | 촬영 순간 한 점의 좌표와 UTC 시각 | [이 사진은 언제 어디서 찍었나](photo-origin.md) |
| 4 | Wi-Fi 연결 기록 | 접속한 네트워크 이름과 마지막 연결 시각, 삼성 기기의 네트워크별 좌표 | [와이파이 설정과 접속 기록](../../02-artifacts/network/wifi.md) |
| 5 | 배터리 사용 기록의 gps·wifi_scan 줄 | 그 시각에 GPS 나 Wi-Fi 검색이 켜졌던 구간(좌표 없음) | [배터리 사용 기록](../../02-artifacts/app-usage/batterystats.md) |
| 6 | 블루투스·생활 앱 기록 | 연결한 블루투스 장치, 주소가 남을 수 있는 생활 앱 | [블루투스 장치](../../02-artifacts/network/bluetooth.md), [배달 앱](../../02-artifacts/korean-apps/delivery-apps.md) |

저장소마다 형식이 달라 한 표에 모을 때 아래를 먼저 맞춥니다.

| 저장소 | 좌표 형식 | 시각 단위 | 확인된 범위 |
|---|---|---|---|
| `odlh-storage.db` 의 `semantic_segment_table` | protobuf 안의 E7 정수(정수 ÷ 10,000,000) [2] | `start_timestamp_seconds`·`end_timestamp_seconds`, 유닉스 초 [2] | 삼성 표본 두 대 0행 [2] |
| `app_semanticlocation_rawsignal_db` (LevelDB) | E7 정수, 수평 정확도 값이 함께 있음 [3] | 유닉스 밀리초 [3] | 삼성 표본 두 대 0행 [3] |
| 구글 지도 `da_destination_history` DB 의 `destination_history` 표 | E6 정수, 목적지와 출발지 좌표 [4] | 유닉스 밀리초 [4] | 현행 지도 앱에 아직 있는지는 확인하지 못했습니다 |
| 구글 지도 `gmm_myplaces.db` 의 `sync_item` | E6 정수 [5] | 유닉스 밀리초 [5] | 오래된 파일에는 이 표가 없습니다 [5] |
| 구글 지도 검색 기록 `new_recent_history_cache_search.cs` | 검색어 중심 | 유닉스 마이크로초 [6] | 다른 지도 기록과 단위가 다릅니다 |
| 삼성 `wifigeofence.db` 의 `geofence_wifi` | `latitude`·`longitude`, 1000.0·-1.0 은 값 없음 [8] | `time` 칸(단위는 확인하지 못함) | ALEAPP 시험 이미지 Android 10~15 삼성 기기 [8] |

## 분석 흐름

1. **질문의 시간 창을 정합니다.** "밤 10시" 처럼 한 점으로 주어진 질문도 앞뒤로 창을 넓혀 잡습니다. 위치 기록은 연속된 선이 아니라 드문드문 찍힌 점이나 구간이라서, 창 안에 기록이 몇 개 있는지부터 셉니다.

2. **구글 기기 내 위치 기록을 봅니다.** ALEAPP 는 `*/com.google.android.gms/databases/odlh-storage.db*` 를 읽는데, 파일 주인은 지도 앱이 아니라 Google Play 서비스입니다 [2]. `semantic_segment_table` 한 행은 시작·끝 시각이 있는 구간이고 `shown_in_timeline`, `is_finalized` 같은 칸도 함께 있습니다 [2]. 개별 위치 점은 `*/com.google.android.gms/app_semanticlocation_rawsignal_db/*` 의 LevelDB 에 위도·경도·수평 정확도·시각으로 남습니다 [3]. 두 저장소가 어떤 관계인지(원재료와 정리된 구간인지)는 확인하지 못했으므로 둘을 별개 기록으로 표에 올립니다.

3. **지도 앱 기록을 더합니다.** 구글 지도의 길찾기 목적지 기록은 `da_destination_history` DB 의 `destination_history` 표에 목적지와 출발지 좌표, 시각을 남기고 [4], 저장한 장소 `gmm_myplaces.db` 에는 라벨과 좌표가 남습니다 [5]. ALEAPP 는 저장한 장소의 key_string 두 값을 Home·Work 로 표시하지만, 이 대응은 데이터에 적혀 있지 않고 라벨이 붙었다고 실제 집·직장이라는 뜻도 아니라고 모듈 메모에 적었습니다 [5]. 길찾기 목적지는 "가려고 했던 곳" 이고 도착했다는 기록이 아니므로, 도착은 다른 기록으로 확인합니다. 네이버 지도·카카오맵은 공개 도구 모듈이 없어 경로와 표를 확인하지 못했으니 각 앱 페이지를 따라갑니다.

4. **사진 한 점을 올립니다.** 창 안에서 찍은 사진이 있으면 EXIF 좌표와 GPS UTC 시각을 한 점으로 올립니다. 촬영 순간 한 점이라는 성격만 기억해 두고, 태그를 읽는 방법과 함정은 [이 사진은 언제 어디서 찍었나](photo-origin.md) 에 있습니다.

5. **Wi-Fi 기록으로 장소를 좁힙니다.** `WifiConfigStore.xml` 은 ALEAPP 가 `*/misc**/apexdata/com.android.wifi/WifiConfigStore.xml`(예전에는 `*/misc/wifi/`)에서 찾고, 삼성 기기에는 `semCreationTime`, `semUpdateTime`, `LastConnectedTime` 칸이 있어 ALEAPP 가 유닉스 밀리초로 읽습니다 [7]. 네트워크 이름(SSID)으로 집·회사·카페 같은 장소를 짐작할 수는 있지만 이름은 누구나 붙일 수 있으므로 짐작으로만 적습니다. 삼성 기기의 `wifigeofence.db` 에는 Wi-Fi 네트워크별 `bssid` 와 좌표가 있어 [8] 네트워크를 지도 위의 점으로 옮길 수 있지만, 이 좌표가 언제 어떻게 잡힌 것인지는 확인하지 못했습니다. 관찰 기기의 `dumpsys wifi` 에는 `rec[#]: time=MM-DD HH:MM:SS.mmm processed=... what=CMD_...` 모양의 상태 기록 줄이 있었고 여기에도 연도가 없었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5).

6. **배터리 기록으로 빈틈을 확인합니다.** 관찰 기기의 `dumpsys batterystats` 이력에는 `+gps +state=`, `-gps -state=`, `gps_signal_quality=`, `+wifi_scan`·`-wifi_scan` 같은 줄이 있었고, 시각은 `MM-DD HH:MM:SS.mmm` 모양이며 이력 머리에 `RESET:TIME:` 줄이 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 이 줄로 알 수 있는 것은 "그 시각에 GPS 가 켜져 있었다" 까지이고 좌표와 GPS 를 켠 앱은 이 줄에 없습니다. 위치 기록이 비어 있는 창에서 GPS 가 켜져 있었다면 어딘가에 위치를 남겼을 앱을 찾아볼 단서가 됩니다.

7. **한 지도 위에 올립니다.** 점마다 좌표를 도 단위로 바꾸고, 시각을 UTC 와 현지 시각으로 적고, 정확도(오차 반경)가 있으면 원으로 그립니다. 출처 저장소와 원래 값도 칸으로 남겨 두면 나중에 값을 다시 확인할 수 있습니다. 여러 기록을 한 시간 축에 놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

> 그림 자리: 지도 위에 저장소별 색으로 점과 오차 원을 찍고, 아래에 같은 색의 시간 축을 붙여 점마다 시각을 이어 준 그림

## 흔한 오판

**점을 "그 자리에 서 있었다" 로 읽는 오판**이 흔합니다. 기록에 정확도가 있으면 "이 반경 안에 있었다고 기록됐다" 로 적고, 정확도가 없는 기록은 없다는 사실을 함께 적습니다.

**좌표 형식을 섞는 실수**도 자주 나옵니다. E7 과 E6 을 같은 수로 나누면 좌표가 열 배 어긋나고, 초·밀리초·마이크로초를 섞으면 시각이 크게 어긋납니다 [2][4][6].

**길찾기 목적지를 방문 기록으로 읽는 경우**가 있습니다. 목적지 기록은 길찾기에 넣은 목적지와 출발지를 담을 뿐이고 [4], 실제로 갔는지는 다른 기록이 보여 줘야 합니다.

**삼성 기기에서 구글 위치 기록이 비었다고 "위치 기록이 없다" 로 끝내는 것**도 조심합니다. 삼성 표본에서 비어 있던 사례가 있고 [2][3], Wi-Fi·사진·앱 기록에 위치가 남아 있을 수 있습니다.

**`mock_location` 키가 있으니 가짜 위치를 썼다고 보는 것**도 지나칩니다. 관찰 기기에서 확인한 것은 키 이름이 있다는 사실까지이고 (확인 범위: SM-S937N, Android 16, One UI 8.5), 가짜 위치 앱 사용 여부를 판단하는 방법은 이번 자료로 확인하지 못했습니다.

## 보고서 문장 예

| 쓰지 않을 문장 | 쓸 문장 |
|---|---|
| 피의자는 ○○일 22시에 ○○역에 있었다. | 구글 기기 내 위치 기록(`app_semanticlocation_rawsignal_db`)에 ○○일 ○○:○○(UTC ○○:○○) 위도 ○○, 경도 ○○, 수평 정확도 ○○m 로 적힌 기록이 있습니다. 이 기록은 기기의 위치를 보여 주며, 기기를 가진 사람이 누구였는지는 담지 않습니다. |
| 피의자는 그날 ○○에 갔다. | 구글 지도의 길찾기 목적지 기록에 ○○일 ○○:○○ 목적지 ○○(좌표 ○○, ○○)이 있습니다. 목적지 기록은 도착 여부를 담지 않고, 같은 날 그 근처의 위치 기록은 ○○ 에서 찾았습니다(또는 찾지 못했습니다). |
| 그 시각에는 위치 기록이 없어 어디 있었는지 모른다. | ○○:○○~○○:○○ 사이에 좌표가 있는 기록은 확보한 자료에서 찾지 못했습니다. 같은 구간에 배터리 사용 기록의 GPS 켜짐 줄이 ○○건 있습니다. |

보고서 전체의 틀은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 아티팩트 본문: [구글 위치 기록과 타임라인](../../02-artifacts/location/google-timeline.md), [위치 캐시](../../02-artifacts/location/cached-locations.md), [구글 지도](../../02-artifacts/location/google-maps.md), [네이버 지도](../../02-artifacts/location/naver-map.md), [카카오맵](../../02-artifacts/location/kakaomap.md), [와이파이 설정과 접속 기록](../../02-artifacts/network/wifi.md), [블루투스 장치](../../02-artifacts/network/bluetooth.md), [배터리 사용 기록](../../02-artifacts/app-usage/batterystats.md)
- 기반 구조: [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md), [LevelDB와 IndexedDB](../../01-foundations/data-formats/leveldb-indexeddb.md), [시각 값](../../01-foundations/value-decoding/time-values.md)
- 이어지는 시나리오: [이 사진은 언제 어디서 찍었나](photo-origin.md), [그 시각에 폰을 쓴 사람이 누구인가](user-attribution.md)
- 기법: [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md), [타임라인 작성](../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. Google Maps 도움말, "Manage your Google Maps Timeline" (answer 6258979) — https://support.google.com/maps/answer/6258979?hl=en
2. ALEAPP, scripts/artifacts/googleOdlh.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/googleOdlh.py
3. ALEAPP, scripts/artifacts/appSemloc.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/appSemloc.py
4. ALEAPP, scripts/artifacts/googlemaplocation.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/googlemaplocation.py
5. ALEAPP, scripts/artifacts/googleMapsGmm.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/googleMapsGmm.py
6. ALEAPP, scripts/artifacts/googleMapsSearches.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/googleMapsSearches.py
7. ALEAPP, scripts/artifacts/wifiProfiles.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/wifiProfiles.py
8. ALEAPP, scripts/artifacts/samsungWifiDatabases.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/samsungWifiDatabases.py
