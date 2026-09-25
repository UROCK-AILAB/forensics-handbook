---
title: "그 시각에 어디 있었나"
parent: "시나리오 · 행위 재구성"
nav_order: 1450
---

# 그 시각에 어디 있었나 (Location)

특정 시각에 아이폰이 어디에 있었는지를 기기에 남은 위치 기록으로 되짚는 시나리오입니다. 기록 하나하나의 구조는 위치 아티팩트 페이지에서 다루고, 이 페이지는 "기기가 그곳에 있었다" 는 기록과 "앱이 그 장소를 보여 줬다" 는 기록을 가르고 여러 기록을 겹치는 순서에 집중합니다.

## 조사 질문

"사건 시각에 피의자의 폰이 현장 근처에 있었나", "그날 어디를 거쳐 어디로 갔나", "주장한 알리바이 장소에 실제로 머물렀나" 같은 질문입니다. 위치 기록은 성격이 서로 달라서 먼저 구분하고 읽습니다. 기기가 스스로 잰 좌표(routined 의 위치 캐시), 기기가 학습한 방문(중요 위치, 바이옴 `Location.Visit`), 앱이 보여 준 장소(바이옴 `App.LocationActivity`, 지도 검색), 사진이 찍힌 곳, 일정에 적힌 장소가 모두 "위치" 로 보이지만, 앞의 둘만 기기가 그 자리에 있었다는 기록에 가깝습니다.

## 먼저 확인할 것

**수집 범위**가 가장 큰 갈림길입니다. routined DB 는 표준 백업에 없고 전체 파일 시스템 추출에서만 나온다고 2018년 글이 적었고 [2], 실제로 암호를 걸지 않은 로컬 백업의 DB 목록에는 routined DB 와 Apple 지도의 `MapsSync_0.0.1` 이 없고 설정 파일 HomeDomain `Library/Preferences/com.apple.routined.plist` 만 있었습니다. 바이옴도 전체 파일 시스템 추출에서 다룬 자료만 있습니다 [5]. 로컬 백업만 있다면 아래 "로컬 백업에서 보이는 것" 절의 기록으로 좁혀서 판단합니다.

**설정 상태**도 봅니다. 중요 위치 (Significant Locations) 는 설정의 "개인정보 보호 및 보안 › 위치 서비스 › 시스템 서비스" 에서 켜고 끄며, 최근 간 곳과 얼마나 자주·언제 갔는지, 경로를 기기가 기록하고, 기기 사이 동기화는 종단 간 암호화로 보호합니다 [1]. 사용자가 이 설정을 껐다면 기록이 없는 것이 자연스럽습니다.

**iOS 버전**에 따라 중심 기록이 바뀝니다.

| iOS 버전 | 중심 기록 | 참고할 점 |
|---|---|---|
| iOS 15 까지 | routined 의 `Cache.sqlite`·`Local.sqlite`·`Cloud.sqlite` [2][3] | iOS 15 이미지에서도 `Cache.sqlite` 의 `ZRTCLLOCATIONMO` 표로 위치를 얻었습니다 [3] |
| iOS 16 | 바이옴이 SEGB v1 형식으로 쓰입니다 [12] | 위치 스트림 이름은 이 핸드북에서 확인하지 못했습니다 |
| iOS 17 이후 | 바이옴 `Location.Visit` [4] | SEGB v2 형식입니다 [5] |
| iOS 18 | 바이옴 `App.LocationActivity` 를 iLEAPP 가 iOS 18 기기 세 대로 시험했습니다 [6] | 앱이 기부한 장소 정보입니다 |
| iOS 27 | 스트림 이름과 routined 표 구조를 이 핸드북에서 확인하지 못했습니다 | 검체의 실제 폴더와 공개 도구의 해석을 대조합니다 |

**시각 기준**은 routined 와 Apple 지도가 Mac 절대 시각이고 [2][7], `App.LocationActivity` 의 만료 시각은 Unix 시각 double 로 읽습니다 [6]. 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 을, 현지 시각은 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md) 을 따릅니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 1 | routined 위치 캐시 — `/private/var/mobile/Library/Caches/com.apple.routined/Cache.sqlite` 의 `ZRTCLLOCATIONMO` 표 [2] | 좌표·시각·고도·진행 방향·속도·정확도, 약 1주일치 [2] | [위치 기록 데몬](../../02-artifacts/location/routined.md) |
| 2 | routined 학습 기록 — 같은 폴더의 `Local.sqlite` [2] | 학습한 관심 장소에 들어가고 나온 때, 이동 시작과 끝, 주차 위치 [2] | [중요 위치](../../02-artifacts/location/significant-locations.md) |
| 3 | 바이옴 `Location.Visit` (iOS 17 이후) — `/private/var/mobile/Library/Biome/streams/restricted/` [4] | 도착·출발 시각, 위도·경도, 수평·수직 정확도, 고도, 신뢰도, 장소 이름·주소·분류·ID, 방문 ID [4]. 적어도 40일은 남는 것으로 보이고 [4], "몇 달" 남는 경우도 있다고 합니다 [5] | [바이옴](../../02-artifacts/app-usage/biome/index.md) |
| 4 | 바이옴 `App.LocationActivity` — 경로 패턴 `*/streams/*/App.LocationActivity/local/*` [6] | 앱이 기부 (donate) 한 NSUserActivity 가운데 장소 정보가 든 것. 기부한 앱의 번들 ID, 활동 종류, URL, 도시, 도로 주소, 우편번호, 제목, 장소 URL [6] | [바이옴](../../02-artifacts/app-usage/biome/index.md) |
| 5 | Apple 지도 — `MapsSync_0.0.1` 의 `ZHISTORYITEM` 표 [7] | 검색·길찾기 기록 [7] | [Apple 지도](../../02-artifacts/location/apple-maps.md) |
| 6 | 나의 찾기 `searchpartyd` 의 `Observations.db` [9] | 주변에서 관찰한 나의 찾기 호환 기기(AirTag 등)와 위치 표 `ObservedAdvertisementLocation`. iOS 16 이후 DB 가 암호화돼 있습니다 [9] | [나의 찾기](../../02-artifacts/location/find-my.md) |
| 7 | 사진 위치 — `Photos.sqlite` 의 `ZASSET.ZLATITUDE`·`ZLONGITUDE` (-180 이면 위치 없음) [10] | 사진이 찍힌 곳 | [이 사진은 언제 어디서 찍었나](photo-origin.md) |
| 8 | 와이파이·블루투스 연결 | 알려진 장소의 네트워크·장치에 붙은 때 | [와이파이 기록](../../02-artifacts/network/wifi.md), [블루투스 장치](../../02-artifacts/network/bluetooth.md) |

전원 로그 (PowerLog) 에도 위치를 요청한 앱·서비스와 요청 종류("Location", "Significant", "Fence", "Visit")가 남는다고 2018년 글이 적었습니다 [2]. 좌표는 아니지만, 어느 앱이 언제 위치를 썼는지 보여 주는 보조 근거로 [전원 로그](../../02-artifacts/app-usage/powerlog.md) 에서 봅니다.

### 로컬 백업에서 보이는 것

암호를 걸지 않은 로컬 백업에서는 아래 파일의 표·칸·키 이름을 확인했습니다. 이름만 확인했고 값의 뜻과 시각 기준은 문서로 확인하지 못해서, 이동 경로의 근거로 쓰기 전에 시험 기기로 대조해야 합니다.

| 파일 | 확인한 이름 | 읽을 때 주의할 점 |
|---|---|---|
| RootDomain `Library/Caches/locationd/consolidated.db` | `GeoFence` 표(`FenceIndex`, `BundleId`, `Name`, `Timestamp`, `Distance` 등), `Vertices` 표(`Latitude`, `Longitude`, `FenceForeignKey`) | 지오펜스(구역) 정의로 보이고, 위치 이력인지는 확인하지 못했습니다 |
| RootDomain `Library/Caches/locationd/clients.plist` | 앱별 항목의 `BundleId`, `Authorization`, `LocationTimeStopped`, `VisitTimeStarted`, `VisitTimeStopped`, `SignificantTimeStarted`, `SignificantTimeStopped` 등 | 앱마다 위치 권한과 사용 시각을 적은 것으로 보이지만 키의 뜻은 확인하지 못했습니다 |
| WirelessDomain `Library/Databases/DataUsage.sqlite` | `ZWIFIDATA` 표(`ZTIMESTAMP`, `ZTIMEAT`, `ZLATITUDE`, `ZLONGITUDE`, `ZLOCACCURACY`, `ZBSSID`, `ZSSID`, `ZRSSI` 등), `ZEVENTSCENE` 표(`ZLATITUDE`, `ZLONGITUDE`, `ZLOCACCURACY`, `ZCOURSE`, `ZSPEED` 등) | 좌표가 언제 채워지는지 확인하지 못했고, iLEAPP 의 데이터 사용량 파서도 두 표를 읽지 않습니다 [11] |
| HomeDomain `Library/Preferences/com.apple.locationaccessstored.plist` | `LastRecordingTime`, `LocationAccessRecordsAge` | 뜻을 확인하지 못했습니다 |
| 캘린더 DB 의 `Location` 표 | `title`, `address`, `latitude`, `longitude` 등 | 일정에 적은 장소이고 실제로 간 곳이 아닙니다. [미리 알림과 캘린더](../../02-artifacts/mail-cloud/reminders-calendar.md) 를 봅니다 |

## 분석 흐름

1. iOS 버전, 시간대, 수집 방법을 적고, 위치 서비스와 중요 위치 설정 상태를 확인합니다. 조사할 시각 앞뒤로 넉넉한 구간을 정합니다.
2. 기기가 잰 좌표부터 봅니다. iOS 15 이하라면 routined `Cache.sqlite` 의 `ZRTCLLOCATIONMO` 에서 구간 안의 좌표를 시각 순으로 뽑고 정확도 칸을 함께 적습니다 [2]. 이 캐시는 약 1주일치라서 [2], 수집 시점에서 오래된 구간은 없을 수 있습니다.
3. 방문 기록을 겹칩니다. `Local.sqlite` 의 들어가고 나온 때 [2] 나 바이옴 `Location.Visit` 의 도착·출발 시각 [4] 으로 "어느 장소에 몇 시부터 몇 시까지" 를 만들고, 2번 좌표와 어긋나지 않는지 봅니다. 바이옴 `remote` 폴더의 기록은 같은 Apple 계정의 다른 기기에서 온 것이라 [13][14] 이 기기의 위치에서 뺍니다.
4. 앱 기록을 붙입니다. `App.LocationActivity` 와 Apple 지도 검색 기록은 사용자가 그 장소를 찾아보거나 앱이 그 장소를 보여 준 흔적이라서, 방문 기록 옆에 "관심을 보인 장소" 로 따로 적습니다. `App.LocationActivity` 는 SEGB 에 쓴 시각(도구 출력의 SEGB Write Timestamp)과 활동 만료 시각이 따로 있고 [6], iLEAPP 는 `local` 폴더만 읽고 `tombstone` 폴더는 건너뜁니다 [6].
5. Apple 지도 `ZHISTORYITEM` 의 시각을 쓸 때는 버전을 확인합니다. iOS 14 로 올린 기기에서 `ZCREATETIME` 이 검색 시각이 아니라 업데이트 시각이었다는 보고가 있습니다 [8].
6. 사진 위치, 와이파이·블루투스 연결, 통화·메시지 시각을 같은 줄에 올려 [타임라인](../../03-techniques/analysis/timeline/index.md) 을 만들고, 서로 다른 기록이 같은 장소를 가리키는 구간만 결론에 씁니다.
7. 전체 파일 시스템 추출이 없고 로컬 백업만 있다면, 위 "로컬 백업에서 보이는 것" 표의 기록으로 할 수 있는 말이 좁다는 점을 보고서에 적습니다. 그 표의 칸은 뜻을 확인하지 못한 것이라서 결론의 근거보다는 추가 수집이 필요하다는 근거로 씁니다. 추출 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 고릅니다.

## 흔한 오판

앱이 보여 준 장소를 "기기가 그곳에 있었다" 로 옮기는 실수가 가장 흔합니다. `App.LocationActivity` 는 앱이 기부한 NSUserActivity 가운데 장소 정보를 담은 것이고 [6], 지도 검색 기록은 검색·길찾기 기록입니다 [7]. 두 기록이 기기의 위치와 같다고 말하는 출처는 이번에 연 자료에 없어서, 보고서에는 "이 앱이 이 장소 정보를 기록했다" 까지만 씁니다.

사진 위치를 사람의 위치로 적는 일도 조심합니다. 사진 위치는 사진이 찍힌 곳이고, 받은 사진이면 다른 사람이 찍은 곳입니다. 캘린더의 `Location` 표도 일정에 적은 장소일 뿐입니다.

좌표 하나를 점으로 읽는 실수도 있습니다. routined 와 `Location.Visit` 에는 정확도 칸이 따로 있어서 [2][4], 좌표는 그 반경 안 어딘가라는 뜻으로 적고 지도에도 반경을 함께 그립니다.

기록이 없다는 사실을 "그곳에 없었다" 로 읽는 일도 있습니다. 중요 위치 설정이 꺼져 있었을 수 있고, routined 위치 캐시는 약 1주일치만 남고 [2], routined DB 는 표준 백업에 들어가지 않는다고 보고됐으며 [2] 관찰한 암호 없는 백업에도 없었습니다.

## 보고서 문장 예

> 바이옴 `Location.Visit` 스트림의 `local` 폴더에 도착 시각 (시각, UTC), 출발 시각 (시각, UTC), 위도·경도 (값), 수평 정확도 (값) m 인 방문 기록이 있습니다. 이 기록은 이 기기가 해당 시간 동안 그 좌표 주변 반경 안에 머물렀다고 기기가 판단했음을 보여 주며, 기기를 누가 지니고 있었는지는 보여 주지 않습니다.

> 바이옴 `App.LocationActivity` 스트림에 (번들 ID) 가 (시각, UTC) 에 (장소 이름·주소) 를 담은 활동을 기부한 기록이 있습니다. 이 기록은 이 앱이 해당 장소 정보를 다뤘음을 보여 주며, 기기가 그 장소에 있었음을 보여 주지는 않습니다.

## 함께 볼 페이지

- [중요 위치 (Significant Locations)](../../02-artifacts/location/significant-locations.md)
- [위치 기록 데몬 (routined)](../../02-artifacts/location/routined.md)
- [Apple 지도 (Apple Maps)](../../02-artifacts/location/apple-maps.md)
- [네이버 지도 (NAVER Map)](../../02-artifacts/location/naver-map.md), [카카오맵 (KakaoMap)](../../02-artifacts/location/kakaomap.md)
- [이 사진은 언제 어디서 찍었나 (Photo Origin)](photo-origin.md)
- [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](user-attribution.md)
- [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. Apple Legal, "Location Services & Privacy" (2026-02-11) — https://www.apple.com/legal/privacy/data/en/location-services/
2. Sarah Edwards (mac4n6), "On the Tenth Day of APOLLO ... iOS Location Analysis" (2018-12-23) — http://www.mac4n6.com/blog/2018/12/23/on-the-tenth-day-of-apollo-my-true-love-gave-to-me-an-oddly-detailed-map-of-my-recent-travels-ios-location-analysis
3. stark4n6, "Magnet User Summit 2022 CTF - iPhone" (2022-06) — https://www.stark4n6.com/2022/06/magnet-user-summit-2022-ctf-iphone.html
4. digital-forensics.it, "84 Streams Later, Part 2: Inside Apple Biome" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html
5. digital-forensics.it, "84 Streams Later: Exploring the Evolution of Apple Biome in iOS" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-exploring-evolution-of.html
6. iLEAPP, `scripts/artifacts/biomeAppLocationActivity.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/biomeAppLocationActivity.py
7. iLEAPP, `scripts/artifacts/mapsSync.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/mapsSync.py
8. Heather Mahalik, Smarter Forensics, "Rotten to the Core? Nah, iOS14 is Mostly Sweet" (2020-09) — https://smarterforensics.com/2020/09/rotten-to-the-core-nah-ios14-is-mostly-sweet/
9. The Binary Hick, "Further Observations – More on iOS Search Party" (2025-08-19) — https://thebinaryhick.blog/2025/08/19/further-observations-more-on-ios-search-party/
10. iLEAPP, `scripts/artifacts/photosMetadata.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/photosMetadata.py
11. iLEAPP, `scripts/artifacts/DataUsage.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/DataUsage.py
12. Be-binary 4n6, "Beyond the C — SEGB and Biome Forensics with crush" (2026-05) — https://bebinary4n6.blogspot.com/2026/05/beyond-c-segb-and-biome-forensics-with.html
13. iLEAPP, `scripts/artifacts/biomeInfocus.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/biomeInfocus.py
14. Magnet Forensics, "Bringing it Back With Biome Data" — https://www.magnetforensics.com/blog/bringing-it-back-with-biome-data/
