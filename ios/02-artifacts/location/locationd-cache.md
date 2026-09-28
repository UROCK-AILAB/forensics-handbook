---
title: "locationd 위치 캐시"
parent: "아티팩트 · 위치"
nav_order: 615
---

# locationd 위치 캐시 (cache_encryptedB.db)

아이폰의 위치 서비스 데몬 locationd 는 주변 와이파이 액세스 포인트와 기지국의 좌표를 `cache_encryptedB.db` 라는 SQLite DB 에 받아 둡니다. 이 DB 의 좌표는 대부분 기기가 아니라 액세스 포인트·기지국의 위치라서, 기기가 그 좌표에 있었다는 증거로 바로 쓰지 않고 "그 무렵 기기가 어느 지역의 위치 자료를 들고 있었나" 를 따지는 데 씁니다. 파일은 전체 파일 시스템 추출에서 얻습니다.

## 무엇을 기록하나 · 왜 생기나

GPS 위성 신호만으로 위치를 계산하면 몇 분까지 걸릴 수 있어서, 아이폰은 와이파이 핫스폿과 기지국 자료를 함께 써서 이 시간을 몇 초로 줄입니다 [4]. 그러려면 주변 핫스폿·기지국의 좌표가 기기 안에 있어야 하므로, 기기는 Apple 이 여러 아이폰에서 모은 핫스폿·기지국 위치 DB 의 일부를 내려받아 캐시로 둡니다 [4]. 이 캐시의 좌표는 기기의 과거·현재 위치가 아니라 기기 주변 핫스폿과 기지국의 위치이고, 기기에서 160km(100마일) 넘게 떨어진 것도 들어 있을 수 있습니다 [4].

같은 DB 에는 기기가 모아 둔 기록도 있습니다. 아이폰은 주변 핫스폿과 기지국의 위치에 좌표를 붙여 익명·암호화 형태로 Apple 에 보냅니다 [4]. 이름에 수집 (Harvest) 이 붙은 표에는 좌표와 함께, 표에 따라 신호 세기(`RSSI`), 이동 상태(`MOTIONACTIVITYTYPE`), 번들 ID(`BUNDLEID`) 같은 열이 있어서 [1] 이 수집과 관련 있는 기록일 가능성이 있습니다.

`cache_encryptedB.db` 옆에는 같은 계열 파일이 더 있습니다. `cache_encryptedA.db`·`lockCache_encryptedA.db` 에도 같은 표가 들어갈 수 있고 [1][3], `cache_encryptedC.db` 에는 움직임 상태(`MotionStateHistory`)와 걸음 수(`StepCountHistory`) 기록이 있습니다 [1][7]. 이 페이지는 와이파이·기지국 위치를 담는 A·B 파일을 다룹니다.

## 위치와 버전별 차이

### 경로

| 파일 | 경로 | 근거 |
|---|---|---|
| `cache_encryptedB.db` | `/private/var/root/Library/Caches/locationd/` | [2][3] |
| `cache_encryptedA.db`, `lockCache_encryptedA.db` | `/private/var/root/Library/Caches/locationd/` | [3] |

DB 를 복사할 때는 `-wal`·`-shm` 파일을 함께 가져옵니다. iLEAPP 도 `cache_encryptedB.db*` 형식으로 이 파일들을 같이 찾습니다 [2]. 같은 이름의 `cache_encryptedB.db` 가 `/private/var/mobile/Library/Caches/com.apple.routined/` 에도 있을 수 있어서 [3], 보고서에는 파일 이름만이 아니라 경로 전체를 적습니다.

### 어떤 추출에서 나오나

Apple 은 2011년 4월에 이 캐시를 백업하지 않고, 위치 서비스를 끄면 캐시를 지우고, 다음 주요 iOS 버전에서는 기기 안에서 암호화하겠다고 발표했습니다 [4]. `cache_encryptedB.db` 는 전체 파일 시스템 추출에서 얻는 위치 아티팩트입니다 [7]. 로컬 백업의 `RootDomain :: Library/Caches/locationd/` 에는 `consolidated.db`·`clients.plist` 가 들어가고, 그 내용은 [위치 기록 데몬](routined.md) 에서 다룹니다.

파일 이름에 "encrypted" 가 들어 있지만, 전체 파일 시스템 추출로 얻은 파일은 APOLLO 와 iLEAPP 가 SQLite DB 로 바로 열어 표를 읽습니다 [1][2]. 이 파일이 어느 보호 등급에 속하는지는 이름으로 판단하지 않고, 같은 기기를 잠금 해제 전·후 상태로 추출한 결과에 파일이 들어 있는지로 확인합니다. 등급과 잠금 상태의 관계는 [보호 등급](../../01-foundations/storage/data-protection/protection-classes.md) 과 [BFU·AFU](../../01-foundations/storage/data-protection/bfu-afu.md) 에서 다룹니다.

### consolidated.db 와의 관계

iOS 4 에서는 `consolidated.db` 가 이 캐시를 담았습니다. 이 DB 에 `CellLocation`, `CellLocationLocal`, `CellLocationHarvest`, `WifiLocation`, `WifiLocationHarvest` 표가 있었고, 모든 표에 시각·위도·경도가 있었습니다 [5]. 2011년 4월에 이 파일이 알려졌을 때 Apple 은 캐시가 1년 가까이 쌓인 것을 버그라고 설명했습니다 [4].

`lockCache_encryptedA.db` 와 `cache_encryptedA.db` 는 iOS 4 의 `consolidated.db` 와 비슷한 DB 입니다 [6]. 지금의 `cache_encryptedB.db` 에도 `WifiLocation`, `CellLocation`, `CellLocationLocal` 같은 같은 이름의 표가 있습니다 [1][2]. 반면 최근 로컬 백업의 `consolidated.db` 에는 이 표들 대신 지오펜스(구역) 표가 있어서, 같은 파일 이름을 보고 iOS 4 때와 같은 내용을 기대하면 안 됩니다. 지금의 `consolidated.db` 표 구성은 [위치 기록 데몬](routined.md) 에 있습니다.

### 버전별 차이

| iOS 버전 | 내용 | 근거 |
|---|---|---|
| iOS 4 | `consolidated.db` 에 와이파이·기지국 표 | [5] |
| iOS 8~14 | `WifiLocation`, `CellLocation`, `CellLocationLocal`, `LteCellLocation`, `LteCellLocationLocal`, `CdmaCellLocation` 을 A·B·lockCache 파일에서 읽음. `ScdmaCellLocation` 은 iOS 9 부터 | [1] |
| iOS 8~10 | `WifiLocationHarvest`, `CellLocationHarvest`, `LteCellLocationHarvest`, `CdmaCellLocationHarvest`, `LocationHarvest`, `AppHarvest`, `PassHarvest`, `WtwLocationHarvest`, `IndoorLocationHarvest`, `PressureLocationHarvest`(iOS 9~10), `PoiHarvestLocation`(iOS 10) | [1] |
| iOS 10 | `WifiLocationHarvest` 에 `SCANTIMESTAMP`, `MOTIONVEHICLECONNECTED` 열 | [1] |
| iOS 16.1.1 | 와이파이·기지국 표는 있으나 행 없음, `WifiAssociatedApWifiHarvestTable` 없음 | [2] |
| iOS 17.3 | `WifiLocation` 30,665행, 기지국 행은 모두 LTE | [2] |
| iOS 18.7 | `WifiLocation` 90,783행, `WifiAssociatedApWifiHarvestTable` 122행 | [2] |
| iOS 26 | `WifiLocation` 에 `AlsQueryTimestamp` 열 추가 | [2] |

iOS 16 부터 26 까지의 행 수는 iLEAPP 가 시험한 이미지 한 개씩의 결과입니다 [2]. 행 수는 기기 사용 방식에 따라 크게 달라서, 이 숫자를 기준값으로 쓰지 않습니다.

## 구조

### 와이파이 위치 (WifiLocation)

한 행이 액세스 포인트 하나의 위치입니다. 이 행은 기기가 그 액세스 포인트에 연결했다는 뜻이 아닙니다 [2].

| 열 | 내용 |
|---|---|
| `Timestamp` | Mac 절대 시각 [1][2] |
| `AlsQueryTimestamp` | iOS 26 에 생긴 두 번째 시각 [2] |
| `MAC` | 액세스 포인트의 BSSID 를 정수로 저장한 값 [2] |
| `Latitude`, `Longitude`, `Altitude` | 액세스 포인트 좌표와 고도 [1][2] |
| `HorizontalAccuracy`, `VerticalAccuracy` | 수평·수직 정확도 [1][2] |
| `Speed`, `Course` | 속도·진행 방향. -1 이 들어 있을 수 있음 [2] |
| `Channel`, `Confidence`, `Score`, `Reach`, `InfoMask` | 채널과 부가 값 [1][2] |

### 기지국 위치

기지국 표는 통신 방식마다 따로 있고, 한 행이 기지국 하나의 위치입니다 [2].

| 표 | 통신 방식 | 식별 열 |
|---|---|---|
| `CellLocation`, `CellLocationLocal` | GSM·UMTS | `MCC`, `MNC`, `LAC`, `CI`, `UARFCN`, `PSC` |
| `LteCellLocation`, `LteCellLocationLocal` | LTE | `MCC`, `MNC`, `TAC`, `CI`, `UARFCN`, `PID` |
| `NrCellLocation` | 5G NR | `MCC`, `MNC`, `TAC`, `CI`, `NRARFCN`, `PID` |
| `ScdmaCellLocation` | TD-SCDMA | `MCC`, `MNC`, `LAC`, `CI`, `UARFCN`, `PSC` |
| `CdmaCellLocation`, `CdmaCellLocationLocal` | CDMA | `MCC`, `SID`, `NID`, `BSID`, `ZONEID`, `BANDCLASS`, `CHANNEL`, `PNOFFSET` |

`MCC` 는 국가 코드 (Mobile Country Code), `MNC` 는 통신사 코드 (Mobile Network Code) 이고, `LAC`·`TAC` 는 기지국이 속한 지역 코드, `CI` 는 기지국(셀) 번호입니다. 모든 기지국 표에 `Timestamp`, `Latitude`, `Longitude`, `Altitude`, `HorizontalAccuracy`, `VerticalAccuracy`, `Speed`, `Course`, `Confidence` 가 함께 있습니다 [1][2]. 이름 끝에 `Local` 이 붙은 표가 붙지 않은 표와 무엇이 다른지는 실제 데이터에서 두 표의 행을 비교해 판단합니다.

### 연결한 액세스 포인트 (WifiAssociatedApWifiHarvestTable)

표 이름으로 보면 기기가 연결(association)한 액세스 포인트를 모은 표입니다 [2]. 열은 `Timestamp`, `ScanTimestamp`, `Latitude`, `Longitude`, `MAC`, `Rssi`, `Channel`, `HorizontalAccuracy`, `Altitude`, `VerticalAccuracy`, `LoiType` 입니다 [2]. 시각이 두 개라서 스캔한 시각과 기록을 만든 시각을 따로 볼 수 있습니다 [2]. 좌표가 그때의 기기 위치인지 액세스 포인트 위치인지는 표 이름만으로 정할 수 없고, `LoiType` 은 정수 코드입니다 [2].

### 와이파이 타일 (WifiTileHeader)

한 행이 기기가 들고 있던 와이파이 위치 자료 한 구역(타일)입니다 [2]. `SouthwestLatitude`·`SouthwestLongitude` 는 구역의 남서쪽 모서리이고, `DeltaLatitude`·`DeltaLongitude` 가 구역 크기라서 [2] 좌표를 구역 가운데로 읽으면 안 됩니다. 시각 열은 `GenerationTimestamp`(만든 시각)와 `AccessTimestamp`(마지막으로 접근한 시각)이고, `TileX`, `TileY`, `ExpirationAge`, `NumberOfInputPoints`, `Version`, `Flags` 같은 열이 함께 있습니다 [2].

### iOS 8~10 의 수집 표

`LocationHarvest` 에는 `TRIPID`, `MCC`, `MNC`, `RAT`, `CONTEXT`, `BUNDLEID`, `BUNDLEIDS`, 이동 상태 열이 있고, `AppHarvest` 에는 `BUNDLEID`, `STATE`, `AGE`, `ROUTINEMODE`, `LOCATIONOFINTERESTTYPE`, `SIG` 가 있습니다 [1]. `WifiLocationHarvest` 에는 `MAC`, `CHANNEL`, `HIDDEN`, `RSSI`, `AGE` 와 이동 상태 열이 있습니다 [1]. 번들 ID 열이 있는 표는 어떤 앱이 위치를 쓰던 때의 기록일 가능성이 있어서, 오래된 iOS 기기에서는 앱별 위치 사용을 따지는 데 도움이 됩니다.

## 증거로서 의미

**증명하는 것**

- `WifiLocation`·기지국 표의 행은 그 BSSID·기지국의 좌표가 기록된 시각에 이 기기의 캐시에 있었다는 것을 보여 줍니다.
- 캐시에 든 좌표가 모인 지역은 기기가 그 무렵 위치 자료를 받은 지역을 보여 줍니다. 받은 자료는 기기 주변 핫스폿·기지국이라서 [4], 기기가 있었던 넓은 지역을 좁히는 데 씁니다.
- `WifiAssociatedApWifiHarvestTable` 의 행은 표 이름대로라면 기기가 연결한 액세스 포인트의 BSSID 와 스캔 시각을 보여 줍니다 [2]. [와이파이 기록](../network/wifi.md) 의 연결 기록과 맞으면 연결 사실을 뒷받침합니다.
- iOS 8~10 의 `AppHarvest`·`LocationHarvest` 번들 ID 는 그 시각에 위치와 함께 기록된 앱을 보여 줍니다 [1].

**증명하지 못하는 것**

- `WifiLocation`·기지국 표의 좌표는 기기 위치가 아닙니다 [2][4][5]. "기기가 이 좌표에 있었다" 고 쓰지 않습니다.
- `WifiLocation` 에 BSSID 가 있어도 기기가 그 액세스 포인트에 연결했다는 뜻은 아닙니다 [2].
- 캐시에 든 액세스 포인트는 기기에서 160km 넘게 떨어져 있을 수도 있어서 [4], 좌표 하나로 기기가 있던 동네를 정할 수 없습니다.
- 행이 없다고 기기가 그 지역에 없었다는 뜻은 아닙니다. iOS 16.1.1 이미지처럼 표는 있는데 행이 하나도 없는 경우도 있습니다 [2].

보고서에는 "이 기기의 locationd 캐시(`cache_encryptedB.db`)에 이 시각으로 이 BSSID 와 좌표가 기록되어 있고, 이 좌표는 액세스 포인트의 위치다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`Timestamp`·`ScanTimestamp`·`GenerationTimestamp`·`AccessTimestamp` 는 2001-01-01 00:00:00 UTC 부터 센 초, 곧 Mac 절대 시각입니다. 978307200 을 더하면 유닉스 시각이 되고 [1][2], 값 자체가 UTC 기준입니다. 현지 시각으로 바꿀 때는 [시간대와 시각 설정](../system-account/time-zone.md) 을 확인하고, 형식 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

시각 열에 -1 이 들어 있을 수 있습니다. 이 값을 그대로 바꾸면 2000-12-31 23:59:59 UTC 가 나오는데, 실제 사건 시각이 아니므로 빈 값으로 둡니다. iLEAPP 도 이 값을 빈 칸으로 보여 줍니다 [2].

`WifiLocation.Timestamp` 는 기기가 그 액세스 포인트에 간 시각이 아닙니다. iOS 4 의 같은 표에서는 시각이 Apple 서버에서 자료를 받아 온 때를 나타냈고 [5], 이 캐시는 Apple 이 모은 DB 에서 내려받은 것이라 [4] 지금도 같은 뜻일 가능성이 있습니다. 그래서 이 시각을 기기가 그 자리에 간 시각으로 읽지 않습니다. iOS 26 의 `AlsQueryTimestamp` 는 `Timestamp` 와 따로 저장되므로 [2] 두 시각을 모두 적고, 둘이 얼마나 차이 나는지 실제 데이터에서 비교합니다.

`WifiTileHeader` 의 `GenerationTimestamp` 는 구역 자료를 만든 때, `AccessTimestamp` 는 마지막으로 접근한 때라서 [2], 한 구역을 여러 날에 걸쳐 쓰면 두 값이 크게 벌어질 수 있습니다.

## 함정과 한계

**좌표의 주인을 헷갈리기 쉽습니다.** `WifiLocation`·기지국 표는 액세스 포인트·기지국의 위치이고, 수집 표는 표마다 다를 수 있습니다. 표마다 누구의 좌표인지 먼저 정하고 나서 지도에 찍습니다. 기기 위치 점이 필요하면 [위치 기록 데몬](routined.md) 의 `Cache.sqlite` 를 봅니다.

**남는 기간은 실제 데이터로 확인합니다.** Apple 은 2011년에 이 자료를 7일 넘게 둘 필요가 없다고 밝혔습니다 [4]. 2014년 발표에서 Zdziarski 는 자기 휴대폰의 `lockCache_encryptedA.db`·`cache_encryptedA.db` 시각이 약 60일에 걸쳐 있었다고 밝혔습니다 [6]. 표마다 가장 오래된 시각과 가장 최근 시각을 적어 두고, 그 범위 밖은 "기록 없음" 이 아니라 "캐시에 남지 않음" 으로 씁니다.

**열이 버전마다 바뀝니다.** iOS 26 에서 `AlsQueryTimestamp` 가 생겼고 [2], CDMA 표에는 `MNC` 가 없습니다 [2]. 쿼리를 쓰기 전에 `PRAGMA table_info(WifiLocation)` 처럼 표마다 열을 먼저 확인합니다.

**`MAC` 은 정수입니다.** BSSID 가 정수로 저장되어 있어서 [2] 16진수 6바이트로 바꿔야 [와이파이 기록](../network/wifi.md) 의 BSSID 와 맞출 수 있습니다. 앞자리 0 이 빠지지 않게 12자리로 채웁니다.

**지운 행이 남아 있을 수 있습니다.** 오래된 행이 정리되면 SQLite 빈 페이지나 WAL 파일에 조각이 남을 수 있습니다. 복구하는 법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 읽기

SQLite 는 실수 값을 8바이트 big-endian IEEE 754 로, 정수는 크기에 맞는 바이트 수로 저장합니다. 아래 두 값은 만든 예시입니다.

```
시각 (Timestamp, 실수)
41 C7 3E ED 80 00 00 00   -> 780000000.0 (Mac 절대 시각)
780000000 + 978307200 = 1758307200 (유닉스 시각)
-> 2025-09-19 18:40:00 UTC

BSSID (MAC, 정수)
73588229205 = 0x001122334455
-> 00:11:22:33:44:55
```

레코드 머리의 형식 코드로 실수·정수를 구분하는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에 있습니다.

### 공개 도구로 읽기

`sqlite3` 로 사본을 열어 표 목록과 열을 먼저 확인합니다.

```sql
.tables
PRAGMA table_info(WifiLocation);

SELECT datetime(Timestamp + 978307200, 'unixepoch') AS 시각_UTC,
       printf('%012x', MAC) AS bssid_hex,
       Latitude, Longitude, HorizontalAccuracy, Channel
FROM WifiLocation
WHERE Timestamp > 0
ORDER BY Timestamp;
```

`bssid_hex` 에 두 자리마다 콜론을 넣으면 보통 쓰는 BSSID 형식이 됩니다. iLEAPP 의 `locationdCacheEncryptedB.py` 는 와이파이 위치, 연결한 액세스 포인트, 기지국, 와이파이 타일을 네 보고서로 나눠 보여 주고 [2], APOLLO 의 `locationd_cacheencryptedAB_*` 모듈은 iOS 8~14 의 표를 표마다 읽습니다 [1]. 도구 결과 가운데 한 행은 위 쿼리로 직접 풀어 맞춰 봅니다. 검증 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [위치 기록 데몬](routined.md) | 기기 자신의 위치 점, 로컬 백업의 `consolidated.db`·`clients.plist` |
| [중요 위치](significant-locations.md) | 방문과 학습된 장소 |
| [와이파이 기록](../network/wifi.md) | 연결한 네트워크와 BSSID |
| [전원 로그](../app-usage/powerlog.md) | 같은 시간대에 위치를 요청한 앱·서비스 |
| [카메라 사진과 메타데이터](../media/dcim-exif.md) | 사진 촬영 위치 |

여러 위치 기록을 시간순으로 합치는 방법은 [그 시각에 어디 있었나](../../04-scenarios/activity/location.md) 에서 다룹니다.

## 실습

공개 시험 이미지(NIST CFReDS 등) 가운데 아이폰 전체 추출이 있는 것으로 풀어 봅니다.

1. `/private/var/root/Library/Caches/locationd/` 에 `cache_encrypted` 로 시작하는 파일이 몇 개 있고, 기기의 iOS 버전은 무엇입니까?
2. `cache_encryptedB.db` 의 표 가운데 행이 있는 표는 무엇입니까?
3. `WifiLocation` 에서 가장 오래된 시각과 가장 최근 시각은 며칠 차이입니까?
4. `WifiLocation` 의 BSSID 하나를 16진수로 바꿔, [와이파이 기록](../network/wifi.md) 의 연결 기록에 같은 BSSID 가 있는지 찾습니다.
5. 같은 시간대의 `routined` `Cache.sqlite` 위치 점과 `WifiLocation` 좌표는 몇 km 떨어져 있습니까?

## 참고 문헌

1. mac4n6/APOLLO, `modules/locationd_cacheencryptedAB_wifilocation.txt`, `_celllocation.txt`, `_ltecelllocation.txt`, `_cdmacelllocation.txt`, `_scdmacelllocation.txt`, `_celllocationlocal.txt`, `_wifilocationharvest.txt`, `_locationharvest.txt`, `_appharvest.txt` 외, `modules/locationd_cacheencryptedC_motionstatehistory.txt`, `_stepcounthistory.txt` (GitHub) — https://github.com/mac4n6/APOLLO/tree/master/modules
2. abrignoni/iLEAPP, `scripts/artifacts/locationdCacheEncryptedB.py` (GitHub) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/locationdCacheEncryptedB.py
3. mac4n6/Mac-Locations-Scraper, `README.md` (GitHub) — https://github.com/mac4n6/Mac-Locations-Scraper
4. Apple, "Apple Q&A on Location Data" (2011-04-27) — https://www.apple.com/newsroom/2011/04/27Apple-Q-A-on-Location-Data/
5. David Schuetz, "Analysis of iOS Location Data from Multiple Devices" (2011-04-25) — https://darthnull.org/analysis-of-ios-location-data/
6. Jonathan Zdziarski, "Identifying Back Doors, Attack Points, and Surveillance Mechanisms in iOS Devices" (2014) — https://www.zdziarski.com/blog/wp-content/uploads/2014/07/iOS_Backdoors_Attack_Points_Surveillance_Mechanisms_Moved.pdf
7. Mattia Epifani, "Exploring Data Extraction from iOS Devices: What Data You Can Access and How" (2025-09-30) — https://blog.digital-forensics.it/2025/09/exploring-data-extraction-from-ios.html
