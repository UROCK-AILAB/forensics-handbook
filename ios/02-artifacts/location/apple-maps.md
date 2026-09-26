---
title: "Apple 지도"
parent: "아티팩트 · 위치"
nav_order: 630
---

# Apple 지도 (Apple Maps)

## 한 줄 요약

Apple 지도는 아이폰 기본 지도 앱이고, iOS 14 이후 검색·길찾기 기록은 앱 그룹 폴더의 `MapsSync_0.0.1` DB 에 있는 `ZHISTORYITEM` 표에 남지만, 최근 기록만 남고 첫 시각 값이 실제 검색 시각과 다를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

사용자가 지도에서 장소를 찾거나 길찾기를 하면, 앱은 최근 기록으로 검색어, 찾은 장소, 길찾기 요청을 남깁니다 [1][2]. 이 기록은 "이 사람이 어디를 찾아봤고 어디로 가려 했나" 를 묻는 조사에 쓰입니다. iOS 14 이전 버전에서는 이 기록을 `GeoHistory.mapsdata` 파일에 프로토콜 버퍼로 두었고 [2], iOS 14 부터 `MapsSync_0.0.1` 이라는 SQLite DB 로 옮겨 갔습니다 [2].

## 위치와 버전별 차이

### 파일 위치

iOS 14 에서는 `var/mobile/Containers/Shared/AppGroup/group.com.apple.Maps/Maps/` 아래에 `MapsSync_0.0.1` 과 `MapsSync_0.0.1_deviceLocalCache.db` 가 있습니다 [2]. 실제 파일 시스템에서 `AppGroup` 아래 폴더가 그룹 ID 이름인지 GUID 이름인지는 검체에서 확인합니다. 앱 그룹 폴더를 찾는 법은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에서 다룹니다. iLEAPP 의 지도 모듈은 경로 패턴 `*/MapsSync_0.0.1*` 로 파일을 찾습니다 [1].

iOS 14 에서는 이 데이터가 맥·윈도우에서 만든 암호화한 iTunes 백업에 들어 있었습니다 [2]. 반면 iOS 27.0 에서 암호화하지 않고 뜬 로컬 백업에는 `MapsSync_0.0.1` 이 없습니다. 이 차이가 백업 암호화 여부 때문인지는 공개 자료가 없어 같은 기기에서 두 가지 백업을 떠 비교해야 하고, 백업 형식은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 설명합니다.

### 버전별 기록 위치

| 버전 | 기록 위치 | 근거 |
|---|---|---|
| iOS 14 이전 | `GeoHistory.mapsdata` (프로토콜 버퍼) | [2] |
| iOS 14 | `MapsSync_0.0.1`, 암호화한 iTunes 백업에 들어 있음 | [2] |
| iOS 14.3, 15.0.2, 16.1.1, 16.5, 17.1, 17.3, 17.5.1, 17.6.1, 18.0, 18.3.2, 18.7, 18.7.8 | iLEAPP 지도 모듈의 시험 자료 버전 | [1] |
| iOS 27.0 로컬 백업(암호화 안 함) | `MapsSync_0.0.1` 없음, 도메인과 설정 plist 만 있음 | |

iLEAPP 모듈은 iOS 14.3 부터 18 까지의 시험 자료를 적어 두었고, 표 구조에 따라 쿼리를 세 가지로 나눠 둡니다 [1]. 아래 칸 목록은 그중 가장 새 구조의 쿼리를 따른 것이고, iOS 15 용 쿼리는 `ZLOCATIONDISPLAY` 대신 `ZMIXINMAPITEM.ZNAME` 을 읽고 길찾기 칸(`ZLATITUDE1`, `ZLONGITUDE1`, `ZROUTEREQUESTSTORAGE`)을 읽지 않습니다 [1]. 그래서 검체마다 `.schema` 로 구조를 먼저 확인합니다.

### 로컬 백업에서 보이는 것

로컬 백업에는 지도 관련 도메인으로 `AppDomain-com.apple.Maps`, `AppDomainGroup-group.com.apple.Maps`, 확장 도메인 `AppDomainPlugin-com.apple.Maps.GeneralMapsWidget`, `AppDomainPlugin-com.apple.Maps.MapsIntents`, `AppDomainPlugin-com.apple.Maps.MapsSettingsAppIntents`, `AppDomainPlugin-com.apple.Maps.SiriTrafficIncidents` 가 있습니다. 지도 관련 plist 와 키는 다음과 같습니다.

| 파일 | 키 |
|---|---|
| `AppDomainGroup-group.com.apple.Maps :: Library/Preferences/group.com.apple.Maps.plist` | `AnnouncementsETag`, `AnnouncementsLastUpdated`, `LastAnnouncementsURL`, datetime 형식 키 1개 |
| `HomeDomain :: Library/Preferences/com.apple.Maps.mapssyncd.plist` | `lastsyncdate`(datetime), `osversion`(str), `CKPerBootTasks`, `CKStartupTime` |
| `HomeDomain :: Library/Preferences/com.apple.identityservices.serviceDisablement.plist` | `com.apple.private.alloy.maps`, `com.apple.private.alloy.maps.eta` |
| `InstallDomain :: Library/MobileInstallation/BackedUpState/BackupSystemAppInstallState.plist` | `com.apple.Maps` |

`mapssyncd` 가 지도 기록을 동기화하는 데몬인지, `alloy.maps.eta` 키가 도착 예정 시간 공유와 관련 있는지는 공개 자료가 없습니다.

## 구조

`MapsSync_0.0.1` 에서 기록을 담는 표는 `ZHISTORYITEM`(검색·길찾기 기록)과 `ZMIXINMAPITEM`(지도 항목)입니다 [1][2]. iLEAPP 는 가장 새 구조의 쿼리에서 두 표를 `ZHISTORYITEM.ZMAPITEM = ZMIXINMAPITEM.Z_PK` 로 이어 다음 칸을 읽습니다 [1].

| 표 | 칸 |
|---|---|
| `ZHISTORYITEM` | `ZCREATETIME`, `ZMODIFICATIONTIME`, `Z_PK`, `Z_ENT`, `ZQUERY`, `ZLOCATIONDISPLAY`, `ZLATITUDE`, `ZLONGITUDE`, `ZLATITUDE1`, `ZLONGITUDE1`, `ZROUTEREQUESTSTORAGE`, `ZMAPITEM` |
| `ZMIXINMAPITEM` | `Z_PK`, `ZMAPITEMSTORAGE` |

같은 쿼리에서 iLEAPP 는 `Z_ENT` 값으로 기록 종류를 나눕니다 [1].

| `Z_ENT` | iLEAPP 가 붙인 종류 |
|---|---|
| 12 | 길찾기 |
| 14 | 검색 좌표 |
| 16 | 장소 검색 |

표 이름 앞의 `Z` 와 `Z_PK`·`Z_ENT` 칸으로 보아 Core Data 형식 DB 이고, Core Data 형식 DB 에는 `Z_PRIMARYKEY` 표(`Z_ENT`, `Z_NAME`, `Z_SUPER`, `Z_MAX`)가 있습니다. `Z_ENT` 번호가 모든 버전에서 같은지는 공개 자료가 없어서, 검체의 `Z_PRIMARYKEY` 에서 번호와 개체 이름을 먼저 맞춰 본 뒤 위 표를 적용합니다. iLEAPP 는 `ZROUTEREQUESTSTORAGE` 를 프로토콜 버퍼로 풀어 길찾기 도착지 주소를 꺼내고, `ZMAPITEMSTORAGE` 도 프로토콜 버퍼로 풀어 주소 요소를 꺼냅니다 [1]. 필드 번호의 뜻은 공개 명세가 없어서, [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 의 읽는 법대로 필드를 풀어 검색어·주소와 맞춰 봅니다. SQLite 구조는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것**

- `ZHISTORYITEM` 행은 이 기기의 지도 앱 기록에 그 검색어나 장소, 길찾기 요청이 있다는 사실을 보여 줍니다.
- `ZMODIFICATIONTIME` 은 이름으로 보아 그 기록이 마지막으로 바뀐 시각이지만, 무엇이 바뀔 때 갱신되는지는 공개 자료가 없습니다.

**증명하지 못하는 것**

- 장소를 검색하거나 길찾기를 한 기록은 그곳에 갔다는 증거가 아닙니다. 실제 이동은 [중요 위치](significant-locations.md) 와 [위치 기록 데몬](routined.md) 으로 확인합니다.
- 기록이 없다고 검색하지 않았다고 볼 수 없습니다. iOS 14 시험에서는 최근 기록 15개 정도, 길찾기와 검색 3~5번만 남았습니다 [2].
- 누가 검색했는지는 이 기록만으로 알 수 없고 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 따로 따집니다.

보고서에는 "이 기기의 지도 앱 기록에 이 검색어가 있고, 기록의 수정 시각은 이것이다" 처럼 어떤 시각 칸을 인용했는지 밝혀 씁니다.

## 시각 해석

`ZCREATETIME` 과 `ZMODIFICATIONTIME` 은 Mac 절대 시각이고, iLEAPP 는 978307200 을 더해 유닉스 시각으로 바꿉니다 [1]. Mac 절대 시각은 UTC 기준이라 현지 시각은 [시간대와 시각 설정](../system-account/time-zone.md) 으로 바꾸고, 형식 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

iOS 14 로 업데이트한 기기에서는 `ZCREATETIME` 이 검색한 시각이 아니라 iOS 14 로 업데이트한 시각일 수 있고, 그때 실제 검색 시각은 `GeoHistory.mapsdata` 에서 찾습니다 [2]. 여러 행의 `ZCREATETIME` 이 같은 시각에 몰려 있으면 기록을 옮긴 시각일 수 있어서, 업데이트 이력과 견줘 보고 생성 시각을 검색 시각으로 인용하지 않습니다.

## 함정과 한계

최근 기록만 남아서 [2] 오래된 검색은 기기에 없을 가능성이 큽니다. 함께 있는 `MapsSync_0.0.1_deviceLocalCache.db` [2] 가 무엇을 담는지는 공개 자료가 없고, 확보할 때는 두 파일과 각각의 `-wal` 파일을 함께 가져옵니다.

`Z_ENT` 번호는 iLEAPP 가 쓰는 값이고 [1] 버전마다 같다는 공개 자료가 없어서, 검체에서 `Z_PRIMARYKEY` 로 확인하지 않고 번호만으로 종류를 나누면 잘못 분류할 수 있습니다.

로컬 백업만 있으면 기록 DB 가 없을 수 있습니다. 기록을 지운 흔적을 의심할 때는 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름을 따릅니다.

## 직접 분석해 보기

### 헥스로 검색어 찾기

`ZQUERY` 같은 글자 칸은 SQLite 레코드 안에 UTF-8 로 들어 있습니다. 아래는 SQLite 레코드 형식 명세로 만든 예시이고, 실제 검체 값이 아닙니다.

```
1F                              -> 글자 칸 형식 코드 (9바이트 글자: 9 x 2 + 13 = 31)
EA B0 95 EB 82 A8 EC 97 AD      -> "강남역" (UTF-8)
```

DB 사본을 헥스 편집기로 열고 찾을 검색어를 UTF-8 바이트로 바꿔 검색하면, 지운 행이 빈 공간에 남아 있을 때도 글자를 찾을 수 있습니다. 찾은 위치 앞뒤의 레코드 머리를 푸는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), 복구 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

### 공개 도구로 읽기

iLEAPP 를 돌리면 위치(Location) 분류에서 지도 기록을 보여 줍니다 [1]. 같은 결과를 `sqlite3` 로 직접 뽑아 맞춰 볼 때는 iLEAPP 가 읽는 칸을 그대로 씁니다.

```sql
SELECT Z_ENT, Z_NAME FROM Z_PRIMARYKEY;

SELECT datetime(h.ZCREATETIME + 978307200, 'unixepoch')       AS 생성_UTC,
       datetime(h.ZMODIFICATIONTIME + 978307200, 'unixepoch') AS 수정_UTC,
       h.Z_PK, h.Z_ENT, h.ZQUERY, h.ZLOCATIONDISPLAY,
       h.ZLATITUDE, h.ZLONGITUDE, h.ZLATITUDE1, h.ZLONGITUDE1,
       h.ZROUTEREQUESTSTORAGE, m.ZMAPITEMSTORAGE
FROM ZHISTORYITEM h
LEFT JOIN ZMIXINMAPITEM m ON h.ZMAPITEM = m.Z_PK
ORDER BY h.ZCREATETIME;
```

`ZLATITUDE`·`ZLONGITUDE` 와 `ZLATITUDE1`·`ZLONGITUDE1` 이 각각 무엇의 좌표인지는 공개 자료가 없어서, 길찾기 행에서 두 쌍을 지도에 찍어 출발지·도착지와 맞는지 확인한 뒤에 해석합니다. 도구 결과를 직접 확인하는 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [중요 위치](significant-locations.md) · [위치 기록 데몬](routined.md) | 검색한 장소에 실제로 갔는지 |
| [KnowledgeC](../app-usage/knowledgec/index.md) · [바이옴](../app-usage/biome/index.md) | 지도 앱을 앞에 띄운 시각 |
| [미리 알림과 캘린더](../mail-cloud/reminders-calendar.md) | 캘린더 `Location` 표(`title`, `address`, `latitude`, `longitude`, `mapkit_handle`, `radius` 등)의 일정 장소 |
| [연락처](../communications/contacts.md) | `ABPerson` 표의 `MapsData` 칸 |
| [시리](../input-assistant/siri.md) | 음성으로 길찾기를 요청한 흔적 |
| [카카오맵](kakaomap.md) · [네이버 지도](naver-map.md) | 다른 지도 앱으로 같은 장소를 찾았는지 |

캘린더 `Location` 표와 연락처 `MapsData` 칸이 지도 앱과 어떻게 이어지는지는 공개 자료가 없어, 지도와 연결되는 흔적 후보로만 봅니다.

## 실습

공개 검체(NIST CFReDS 등)나 연습용 기기로 풀어 봅니다.

1. 검체의 iOS 버전은 무엇이고, `MapsSync_0.0.1` 은 어느 폴더에 있습니까?
2. `Z_PRIMARYKEY` 에서 `Z_ENT` 12, 14, 16 에 해당하는 개체 이름은 무엇입니까?
3. `ZCREATETIME` 이 같은 시각에 몰린 행이 있습니까? 있다면 그 시각은 iOS 업데이트 시각과 가깝습니까?
4. 연습용 기기에서 장소 세 곳을 검색하고 길찾기를 한 번 한 뒤, 추가된 행의 `Z_ENT` 와 시각을 기록합니다.
5. 같은 기기의 로컬 백업을 암호화한 것과 암호화하지 않은 것 두 가지로 떠서, `MapsSync_0.0.1` 이 어느 쪽에 들어가는지 비교합니다.

## 참고 문헌

1. abrignoni/iLEAPP, `scripts/artifacts/mapsSync.py` (GitHub, 2026-07-31 수정) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/mapsSync.py
2. Heather Mahalik, Smarter Forensics, "Rotten to the Core? Nah, iOS14 is Mostly Sweet" (2020-09) — https://smarterforensics.com/2020/09/rotten-to-the-core-nah-ios14-is-mostly-sweet/
