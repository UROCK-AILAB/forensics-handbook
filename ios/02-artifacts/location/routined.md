---
title: "위치 기록 데몬"
parent: "아티팩트 · 위치"
nav_order: 610
---

# 위치 기록 데몬 (routined)

## 한 줄 요약

routined 는 아이폰이 지나간 위치 점과 머문 장소를 SQLite DB 세 개(`Cache.sqlite`, `Local.sqlite`, `Cloud.sqlite`)에 쌓는 시스템 데몬이고, 이 DB 들은 파일 시스템 전체 추출에서만 나오며 로컬 백업에는 설정 plist 만 남습니다.

## 무엇을 기록하나 · 왜 생기나

중요 위치 데이터는 routined 데몬이 만듭니다 [1]. 데몬은 기기가 계산한 위치 점을 짧은 기간 모아 두고, 사용자가 드나든 관심 장소와 장소 사이 이동도 기록합니다 [1]. 사용자가 무엇을 저장하지 않아도 기록이 쌓여서, 조사에서는 "그 시각에 기기가 어디 있었나" 를 따질 때 씁니다. 어떤 설정이 켜져 있어야 기록이 생기는지는 확인한 자료가 없습니다.

세 DB 는 쓰임이 다릅니다. `Cache.sqlite` 는 1주일 남짓한 위치 점을 담고, `Local.sqlite` 는 학습된 관심 장소(Location of Interest) 진입·이탈과 이동, 주차 기록을 담고, `Cloud.sqlite` 는 방문과 학습된 장소를 담습니다 [1]. 방문과 학습된 장소는 [중요 위치](significant-locations.md) 에서 자세히 다루고, 이 페이지는 나머지 두 DB 와 데몬 주변 흔적을 다룹니다.

## 위치와 버전별 차이

### 전체 파일 시스템 추출

DB 세 개는 `/private/var/mobile/Library/Caches/com.apple.routined/` 폴더에 있습니다 [1]. 2018년 글은 이 파일들이 표준 백업에는 없고 전체 추출에서만 나온다고 적었고 [1], iOS 15 이미지를 다룬 2022년 글도 같은 경로의 `Cache.sqlite` 에서 `ZRTCLLOCATIONMO` 표로 캐시 위치의 위도·경도·시각을 얻었습니다 [2]. 전체 추출 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

### 로컬 백업

암호화하지 않은 로컬 백업에는 routined DB 가 없었고 다음 흔적만 있었습니다 (확인 범위: iOS 27.0).

| 흔적 | 위치 |
|---|---|
| 설정 plist | `HomeDomain :: Library/Preferences/com.apple.routined.plist` |
| 진단 확장 도메인 | `AppDomainPlugin-com.apple.CoreRoutine.RTDiagnosticExtension` |
| 네트워크 사용 기준 목록 | `HomeDomain :: Library/Preferences/com.apple.osanalytics.addaily.plist` 의 `netUsageBaseline` 안에 `com.apple.routined` |

백업 도메인 체계는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 설명합니다.

### 버전별로 확인한 내용

| 시기·버전 | 확인한 내용 | 근거 |
|---|---|---|
| 2018년 글 | DB 세 개, 전체 추출에서만 얻음 | [1] |
| iOS 15 | `Cache.sqlite` 의 `ZRTCLLOCATIONMO` 표에 캐시 위치 | [2] |
| iOS 27.0 로컬 백업 | DB 없음, 설정 plist 와 진단 확장 도메인만 있음 | (확인 범위: iOS 27.0) |

iOS 16 이후 DB 이름과 표 구조가 어떻게 바뀌었는지는 확인한 자료가 없습니다.

## 구조

### Cache.sqlite

`ZRTCLLOCATIONMO` 표에는 좌표, 시각, 고도, 진행 방향(course), 속도(m/s), 수평·수직 정확도가 있고, 2018년 글의 예시 기기에서는 4만 건이 넘었습니다 [1]. 좌표는 기기가 계산한 추정 위치라서 정확도 칸과 함께 읽어야 하고 [1], 기록은 약 1주일치만 남습니다 [1]. `ZRTHINTMO` 표는 건수가 적지만 시각·좌표·정확도가 있고 역시 약 7일 남습니다 [1].

### Local.sqlite

학습된 관심 장소의 진입·이탈, 이동(transition) 시작·끝, 주차한 차의 위치와 주차 기록이 있고, 각 행에 시각, 좌표, 신뢰도, 불확실도, 데이터 점 개수, 프로토콜 버퍼 BLOB 이 있습니다 [1]. 주차 기록에는 CarPlay 연결이 필요한 듯하지만 필수인지는 글쓴이도 확인하지 못했습니다 [1]. 이 파일의 표 이름은 원문으로 확인한 것이 없어서 검체에서 칸 구성으로 찾습니다.

### Cloud.sqlite

방문 진입·이탈과 들어오는·나가는 이동의 시작·끝, 장소 ID, 여러 시각 값, 장소 이름·지오 BLOB 이 있습니다 [1]. 해석은 [중요 위치](significant-locations.md) 에 있습니다. 이름으로 보아 기기 사이 동기화와 관련 있는 파일로 보이지만, 동기화와 파일의 관계는 확인한 자료가 없습니다.

### 설정 plist 의 키

로컬 백업의 `com.apple.routined.plist` 에서 본 키 가운데 조사와 관련 있어 보이는 것은 다음과 같습니다. 값은 가려져 있어 읽지 않았고, 키 이름만 확인했습니다 (확인 범위: iOS 27.0).

| 키 | 형식 |
|---|---|
| `RTAuthorizationManagerCachedLocationServicesEnabled` | bool |
| `RTAuthorizationManagerCachedCoreRoutineClientEnabled` | bool |
| `VisitManagerPreviousPOIVisitDates` | bytes |
| `KnownPlaceIdentifiersLastUpdateDate` | datetime |
| `RTDefaultsFeatureExtractorTrainVisitCount` | int |
| `RTDefaultsFeatureExtractorTrainLocationHistoryCount` | int |
| `RTDefaultsFeatureExtractorTrainParkedCar` | bool |
| `InstantPOIMetricsVisitCount` | int |
| `BlueSkyDailyQualifiedVisits` | int |
| `RTDefaultsLocationContextManagerSyncDates` | bytes |
| `RTAuthorizedLocationEraseInstallInitActivityStartDate` | datetime |
| `LastLaunchDate.CoreRoutineHelperService` | datetime |
| `LearnedLocationEngineTrainDailyMetricsSubmissonAttemptDate` | datetime |
| `RTDefaultsPredictedContextManagerTrainAttemptedDate` | datetime |
| `RTDefaultsSuggestionsManagerSystemVersion` | str |
| `RTDefaultsSafetyCacheActiveSessionZoneCKSyncEngineMetadata` | bytes |
| `BluePOIDailyEventOpportunisticWiFiScanRequestCount` | int |

두 `Cached...Enabled` 키가 위치 서비스와 중요 위치가 켜져 있었는지를 나타내는지, 방문 개수 키가 무엇을 센 값인지는 확인하지 못했습니다. 이름만 보고 "중요 위치가 켜져 있었다" 고 보고서에 쓰지 않고, 같은 설정을 바꿔 본 시험 기기에서 값이 어떻게 달라지는지 확인한 뒤에 씁니다. plist 를 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

### 함께 남는 locationd 흔적

`locationd` 이름이 붙은 파일은 로컬 백업에도 들어 있어서, routined DB 가 없을 때 참고할 수 있습니다 (확인 범위: iOS 27.0).

| 파일 | 본 내용 |
|---|---|
| `RootDomain :: Library/Caches/locationd/clients.plist` | 앱·서비스별 항목. 키에 `Authorization`, `LocationTimeStopped`, `ReceivingLocationInformationTimeStopped`, `VisitMonitoring`, `VisitTimeStarted`, `VisitTimeStopped`, `SignificantTimeStarted`, `SignificantTimeStopped`, `SLC` 등이 있음 |
| `RootDomain :: Library/Caches/locationd/consolidated.db` | 표 `GeoFence`(`FenceIndex`, `BundleId`, `Name`, `Timestamp`, `Distance`, `DesiredAccuracy`, `MonitorFlags`, `OnBehalfBundleId` 등), `Vertices`(`Latitude`, `Longitude`, `FenceForeignKey`), `BeaconFences`, `FenceHandOffDeviceId`, `TableInfo` |
| `HomeDomain :: Library/Preferences/com.apple.locationaccessstored.plist` | 키 `LastRecordingTime`(str), `LocationAccessRecordsAge`(int) |
| `HomeDomain :: Library/Preferences/com.apple.locationd.plist` | 키 `LastSystemVersion`, `CLSilo.Version`, `ObsoleteDataDeleted` |

`clients.plist` 의 `VisitMonitoring`·`Visit...`·`Significant...`·`SLC` 키는 방문 감시나 중요 위치 변경 감시를 쓰는 클라이언트 표시로 보이지만 뜻은 확인하지 못했습니다. `consolidated.db` 는 표 이름으로 보아 지오펜스(구역) 정의를 담고 있고, 위치 이력을 담는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것**

- `Cache.sqlite` 의 위치 점은 그 시각에 기기가 스스로 계산한 위치와 정확도를 보여 줍니다.
- `Local.sqlite` 의 진입·이탈은 시스템이 기기가 학습된 장소에 들어가고 나왔다고 판단한 시각을 보여 줍니다.
- 로컬 백업의 설정 plist 와 진단 확장 도메인은 이 기기에 routined 가 동작한 흔적이 있다는 정도를 보여 줍니다.

**증명하지 못하는 것**

- 위치 점은 기기 위치이지 사람 위치가 아닙니다. 누가 들고 있었는지는 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 따로 따집니다.
- 기록이 비어 있는 시간대가 기기가 꺼져 있었거나 위치 서비스가 꺼져 있었다는 뜻은 아닙니다. 기록이 모든 위치를 담지는 않습니다 [1].
- plist 키 이름만으로 설정 상태를 확정할 수 없습니다.

보고서에는 "이 기기의 routined 캐시에 이 시각, 이 좌표가 수평 정확도 몇 m 로 기록되어 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

[1] 은 시각 형식을 따로 밝히지 않았습니다. 표 이름으로 보아 Core Data 형식 DB 이고 Core Data 의 날짜 칸은 보통 Mac 절대 시각이라서, 978307200 을 더해 유닉스 시각으로 바꿔 보고 [3] 값이 그럴듯한 날짜인지 확인합니다. Mac 절대 시각은 UTC 기준이라 현지 시각으로 바꿀 때는 [시간대와 시각 설정](../system-account/time-zone.md) 을 확인하고, 형식 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

`Cache.sqlite` 의 시각은 위치 점을 얻은 때이고, `Local.sqlite` 의 진입·이탈 시각은 시스템이 판단한 경계라서 두 값을 같은 성격으로 섞지 않습니다. plist 의 `datetime` 키는 데몬이 어떤 작업을 마지막으로 시도하거나 갱신한 시각으로 보이지만, 각 키가 언제 바뀌는지는 확인하지 못했습니다.

## 함정과 한계

캐시는 약 1주일치만 남아서 [1] 확보가 늦을수록 앞쪽 기록이 사라집니다. 확보 시각을 기록해 두고, 캐시에서 가장 오래된 시각과 함께 보고서에 적습니다.

로컬 백업만 있으면 DB 자체가 없어서 위치 이력을 이 페이지 방식으로 재구성할 수 없습니다 [1] (확인 범위: iOS 27.0). 그럴 때는 locationd 흔적과 사진 위치, 앱 기록으로 범위를 좁힙니다.

모든 행은 추정 위치이고 정확도 값이 크면 반경이 넓습니다. 도로 옆 건물처럼 가까운 두 장소를 가를 때 정확도 칸을 빼고 좌표만 인용하면 오판하기 쉽습니다.

DB 를 사본으로 열 때는 `-wal` 파일을 함께 가져옵니다. 지운 행을 찾는 법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 시각 읽기

SQLite 는 실수 값을 8바이트 big-endian IEEE 754 로 저장합니다. 아래는 명세로 만든 예시이고 실제 검체 값이 아닙니다.

```
41 C7 D7 84 00 00 00 00   -> 800000000.0 (Mac 절대 시각)
800000000 + 978307200 = 1778307200 (유닉스 시각)
-> 2026-05-09 06:13:20 UTC
```

`ZRTCLLOCATIONMO` 의 행을 헥스로 보면 레코드 머리의 형식 코드 다음에 이런 8바이트 실수가 이어질 수 있고, 위도·경도·시각이 실수로 저장되어 있다면 값의 크기로 서로 가려낼 수 있습니다. 레코드 머리를 푸는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에 있습니다.

### 공개 도구로 읽기

`sqlite3` 명령행 도구로 `Cache.sqlite` 사본을 열어 표 구조를 먼저 확인하고, 칸 이름을 검체에서 확인한 것으로 바꿔 시각을 풉니다.

```sql
.schema ZRTCLLOCATIONMO
SELECT datetime(시각_칸 + 978307200, 'unixepoch') AS 시각_UTC,
       위도_칸, 경도_칸, 수평정확도_칸, 속도_칸
FROM ZRTCLLOCATIONMO
ORDER BY 시각_칸;
```

공개 분석 도구를 쓸 때도 도구가 보여 주는 결과 가운데 한 행은 위 방법으로 직접 풀어 맞춰 봅니다. 검증 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [중요 위치](significant-locations.md) | 방문과 학습된 장소 |
| [전원 로그](../app-usage/powerlog.md) | 위치 결정 방식(Wi-Fi·GPS), 위치를 요청한 앱·서비스와 요청 종류("Location", "Significant", "Fence", "Visit") [1] |
| [와이파이 기록](../network/wifi.md) | 같은 시간대의 무선 네트워크 |
| [카메라 사진과 메타데이터](../media/dcim-exif.md) | 사진 촬영 위치 |
| [통합 로그에서 찾을 것](../logs/unified-log-events.md) | 위치 서비스 관련 시스템 이벤트 |
| [나의 찾기](find-my.md) | 기기 위치 조회와 위치 공유 |

여러 위치 기록을 한 줄로 세우는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 과 [그 시각에 어디 있었나](../../04-scenarios/activity/location.md) 에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등) 가운데 아이폰 전체 추출이 있는 것으로 풀어 봅니다.

1. `com.apple.routined` 폴더에 DB 가 몇 개 있고, 검체의 iOS 버전은 무엇입니까?
2. `ZRTCLLOCATIONMO` 가 있다면 가장 오래된 행과 가장 최근 행 사이는 며칠입니까?
3. 수평 정확도가 가장 큰 행과 가장 작은 행을 골라 지도에 찍으면 반경이 얼마나 다릅니까?
4. `Local.sqlite` 에서 진입·이탈 기록 하나를 골라, 그 시간대의 `Cache.sqlite` 위치 점과 맞는지 확인합니다.
5. 같은 검체의 로컬 백업이 있다면 `clients.plist` 에서 `VisitMonitoring` 키가 있는 항목은 몇 개입니까?

## 참고 문헌

1. Sarah Edwards, mac4n6.com, "On the Tenth Day of APOLLO ... iOS Location Analysis" (2018-12-23) — http://www.mac4n6.com/blog/2018/12/23/on-the-tenth-day-of-apollo-my-true-love-gave-to-me-an-oddly-detailed-map-of-my-recent-travels-ios-location-analysis
2. stark4n6, "Magnet User Summit 2022 CTF - iPhone" (2022-06) — https://www.stark4n6.com/2022/06/magnet-user-summit-2022-ctf-iphone.html
3. abrignoni/iLEAPP, `scripts/artifacts/mapsSync.py` (GitHub) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/mapsSync.py
