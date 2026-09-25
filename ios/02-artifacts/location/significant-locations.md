---
title: "중요 위치"
parent: "아티팩트 · 위치"
nav_order: 600
---

# 중요 위치 (Significant Locations)

## 한 줄 요약

중요 위치는 아이폰이 사용자가 자주 가는 곳과 그곳에 간 시각·경로를 배워 두는 시스템 기능이고, 기록은 위치 기록 데몬(routined)이 만드는 SQLite DB 에 방문과 학습된 장소로 남지만, 2018년 글 기준으로 파일 시스템 전체 추출에서만 얻을 수 있고 시간이 지나면 만료됩니다.

## 무엇을 기록하나 · 왜 생기나

Apple 설명에 따르면, 이 기능을 켠 기기와 같은 Apple 계정으로 iCloud 에 로그인한 기기는 최근에 간 곳, 그곳에 얼마나 자주 언제 갔는지, 거기까지 간 경로를 기록해서 사용자에게 의미 있는 장소와 경로를 배웁니다 [1]. 현재 설정 이름은 "Significant Locations & Routes"(중요 위치 및 경로)이고, 설정의 개인정보 보호 및 보안 → 위치 서비스 → 시스템 서비스 안에 있습니다 [1]. 같은 시스템 서비스 목록에는 Routing and Traffic, Improve Location Accuracy, Suggestions & Search, Share My Location, Emergency Calls & SOS 같은 항목이 나란히 있어서 [1], 중요 위치는 여러 위치 기반 시스템 서비스 가운데 하나입니다.

시스템은 배운 장소를 사진의 추억 만들기 같은 개인화 기능에 쓰고, 사용자가 중요 위치를 켜고 앱에 위치 권한을 주면 앱에도 "Visited Places", "Preferred Routes and Predicted Destinations" 같은 정보를 넘깁니다 [1]. 기기 사이 동기화는 종단간 암호화라서 Apple 이 내용을 읽을 수 없다고 Apple 은 설명합니다 [1].

포렌식에서 이 기능이 중요한 까닭은 사용자가 따로 저장하지 않아도 머문 장소와 머문 시간이 쌓인다는 데 있습니다. 실제로 이 기록을 만드는 쪽은 위치 기록 데몬(routined)이고, 데몬이 쓰는 파일 전체의 구조는 [위치 기록 데몬](routined.md) 에서 다룹니다. 이 페이지는 그중 중요 위치에 해당하는 방문과 학습된 장소 기록을 해석하는 데 집중합니다.

## 위치와 버전별 차이

### 어디에 있나

2018년 글 기준으로, 중요 위치 데이터는 `/private/var/mobile/Library/Caches/com.apple.routined/` 폴더의 SQLite DB 에 있고 방문 기록은 그중 `Cloud.sqlite` 에 있습니다 [3]. 같은 글은 이 데이터가 백업으로는 나오지 않고 파일 시스템 전체 추출에서만 얻을 수 있다고 적었습니다 [3]. 전체 추출 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

실제 아이폰의 암호화하지 않은 로컬 백업에서도 `com.apple.routined` 의 DB 파일은 백업 DB 목록에 없었고, 설정 plist `HomeDomain :: Library/Preferences/com.apple.routined.plist` 만 있었습니다 (확인 범위: iOS 27.0). 백업을 암호화했다면 결과가 달라지는지는 확인하지 못했습니다. 로컬 백업의 도메인 체계는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 설명합니다.

### 버전별로 확인한 내용

| 시기·버전 | 확인한 내용 | 근거 |
|---|---|---|
| 2018년 글 | `routined` 폴더의 `Cloud.sqlite` 에 방문 기록, 전체 추출에서만 얻음 | [3] |
| iOS 15~18 | 방문 기록 표 구조가 바뀌었는지 확인한 자료 없음 | — |
| iOS 27.0 로컬 백업 | `routined` DB 없음, 설정 plist 만 있음 | (확인 범위: iOS 27.0) |
| 2026년 Apple 문서 | 설정 이름 "Significant Locations & Routes", 동기화는 종단간 암호화 | [1] |

iOS 15 이후 방문 기록을 담는 파일 이름이 바뀌었다는 자료를 검색 결과에서 보았지만 원문으로 확인하지 못해서, 이 페이지에는 파일 이름을 적지 않습니다. 검체에서는 `routined` 폴더 안의 DB 를 모두 열어 아래 구조와 맞는 표를 찾습니다.

## 구조

2018년 글이 설명한 방문 기록에는 시각 값이 여러 개 있고, 방문 시작과 끝, 방문 기록을 만든 시각과 만료되는 시각, 학습된 장소를 만든 시각과 만료되는 시각이 따로 있습니다 [3]. 행마다 위치 불확실도와 신뢰도 값도 함께 있어서 [3] 좌표 하나를 확정된 점으로 읽지 않고 반경과 확률을 함께 읽습니다.

장소 쪽 정보는 BLOB 두 개에 들어 있습니다 [3].

| BLOB | 담긴 내용 | 형식 |
|---|---|---|
| 장소 이름 | 주소, 도시, 주, 업체명 | [3] 에 형식 설명 없음 |
| 장소 지오(geo) | 좌표 | 프로토콜 버퍼, 좌표는 8바이트 실수(big-endian) |

프로토콜 버퍼를 읽는 법은 [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 에서 다룹니다. 표 이름과 칸 이름은 원문으로 확인한 자료가 없어서, 검체에서는 시각 칸이 여러 개이고 신뢰도·불확실도 칸과 BLOB 칸이 함께 있는 표를 찾아 방문 기록으로 판단합니다. DB 가 Core Data 형식이라면 `Z_PRIMARYKEY` 표의 `Z_NAME` 칸으로 개체 이름을 먼저 확인할 수 있습니다(Core Data 형식 DB 에 이 표가 있다는 점은 확인 범위: iOS 27.0). SQLite 구조 자체는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 를 봅니다.

## 증거로서 의미

**증명하는 것**

- 방문 기록이 있으면, 기기가 그 시간대에 그 장소 부근에 머물렀다고 판단한 기록이 있다는 사실을 보여 줍니다. 판단의 정확도는 같은 행의 불확실도·신뢰도가 말해 줍니다.
- 학습된 장소가 있으면, 시스템이 그 장소를 사용자에게 의미 있는 곳으로 분류했다는 사실을 보여 줍니다.

**증명하지 못하는 것**

- 기기가 그곳에 있었다는 기록일 뿐, 기기 주인이 들고 있었다는 뜻은 아닙니다. 사용자 판단은 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.
- 기록이 없다고 그곳에 가지 않았다고 볼 수 없습니다. 2018년 글도 잘 맞는 편이지만 모든 위치가 있지는 않다고 적었습니다 [3].
- 같은 계정의 여러 기기가 기록을 동기화하는데 [1], 파일에 있는 방문이 이 기기에서 생겼는지 다른 기기에서 넘어왔는지는 확인한 자료가 없습니다. 기기가 여러 대인 사건에서는 이 점을 보고서에 밝힙니다.

보고서에는 "이 기기의 중요 위치 기록에 이 시간대, 이 좌표 반경 안에 머문 방문이 신뢰도 얼마로 남아 있다" 처럼 씁니다.

## 시각 해석

[3] 은 시각 형식을 따로 밝히지 않았습니다. `routined` DB 는 Core Data 형식으로 보이고 Core Data 의 날짜 칸은 보통 Mac 절대 시각이지만, 검체에서는 값의 크기로 먼저 확인합니다. Mac 절대 시각은 2001-01-01 00:00:00 UTC 부터 센 초라서, 978307200 을 더하면 유닉스 시각이 되고 [4] 결과는 UTC 입니다. 현지 시각으로 바꿀 때는 [시간대와 시각 설정](../system-account/time-zone.md) 에서 기기 시간대를 확인하고, 시각 형식 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

방문 기록의 시각 값은 뜻이 다 다릅니다. 방문 시작·끝은 머문 구간이고, 생성 시각은 시스템이 그 기록을 만든 때이며, 만료 시각은 기록을 지울 예정 시각입니다 [3]. 생성 시각이 도착 시각과 같다는 자료는 없어서, 생성 시각을 도착 시각으로 쓰지 않습니다.

## 함정과 한계

기록은 시간이 지나면 만료되고 [3], Apple 문서 두 곳([1], [2])에서는 보존 기간이나 목록 지우기 방법을 설명한 문구를 찾지 못했습니다. 그래서 오래된 날짜의 방문이 없다고 해서 사용자가 지웠다고 볼 수 없고, 가능한 한 빨리 기기를 확보하는 편이 낫습니다 [3]. 의도적으로 지운 흔적을 찾을 때는 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름을 따릅니다.

로컬 백업만 받은 사건에서는 방문 기록이 처음부터 없습니다 (확인 범위: iOS 27.0). 이때 중요 위치가 켜져 있었는지 알려 줄 만한 키 후보가 `com.apple.routined.plist` 에 있지만, 키의 뜻은 확인하지 못했고 그 목록은 [위치 기록 데몬](routined.md) 에 정리했습니다.

2018년 글 이후의 표 구조는 확인한 자료가 없어서, 다른 버전 검체에서 얻은 표·칸 이름을 그대로 쓰지 않고 검체의 iOS 버전을 함께 적어 둡니다.

## 직접 분석해 보기

### 헥스로 좌표 읽기

장소 지오 BLOB 안의 좌표는 8바이트 big-endian 실수입니다 [3]. 아래는 IEEE 754 배정밀도 명세로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다.

```
40 42 C8 83 12 6E 97 8D   -> 37.5665  (위도 예시)
40 5F BE 97 8D 4F DF 3B   -> 126.978  (경도 예시)
```

BLOB 을 헥스 편집기로 열고 `40 4x`, `40 5x`, `40 6x` 로 시작하는 8바이트 묶음을 찾아 실수로 풀면 한국 부근 좌표인지 가늠할 수 있습니다(경도 128도 이상은 `40 60` 으로 시작합니다). 다만 프로토콜 버퍼에서는 필드 번호와 형식을 알리는 바이트가 값 앞에 붙어서, 위치를 정확히 잡으려면 [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 의 읽는 법대로 필드를 차례로 풀어 갑니다.

### 공개 도구로 읽기

`sqlite3` 명령행 도구나 DB Browser for SQLite 같은 SQLite 열람기로 `routined` 폴더의 DB 사본을 열고, 표 목록에서 방문·장소로 보이는 표를 고른 뒤 시각 칸을 다음처럼 바꿔 봅니다. 표와 칸 이름은 검체에서 확인한 것으로 바꿔 씁니다.

```sql
SELECT datetime(시작_시각_칸 + 978307200, 'unixepoch') AS 시작_UTC,
       datetime(끝_시각_칸   + 978307200, 'unixepoch') AS 끝_UTC,
       신뢰도_칸, 불확실도_칸
FROM 방문_표
ORDER BY 시작_시각_칸;
```

DB 는 반드시 사본으로 열고, 함께 있는 `-wal` 파일도 같이 복사해 둡니다. WAL 을 다루는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 설명합니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [위치 기록 데몬](routined.md) | 같은 폴더의 캐시 위치 점, 학습된 관심 장소 진입·이탈, 주차 위치 |
| [전원 로그](../app-usage/powerlog.md) | 위치를 요청한 앱·서비스와 요청 종류 |
| [카메라 사진과 메타데이터](../media/dcim-exif.md) | 같은 시간대에 찍은 사진의 촬영 위치 |
| [와이파이 기록](../network/wifi.md) | 같은 시간대에 붙은 무선 네트워크 |
| [Apple 지도](apple-maps.md) | 그 장소를 검색하거나 길찾기를 했는지 |
| [나의 찾기](find-my.md) | 위치 공유와 기기 위치 조회 흔적 |

여러 기록을 시간순으로 맞추는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 과 [그 시각에 어디 있었나](../../04-scenarios/activity/location.md) 에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등) 가운데 아이폰 파일 시스템 전체 추출이 있는 것을 골라 풀어 봅니다.

1. `/private/var/mobile/Library/Caches/com.apple.routined/` 폴더에 어떤 DB 가 있고, 검체의 iOS 버전은 무엇입니까?
2. 방문 기록으로 보이는 표를 찾았다면, 시각 칸은 몇 개이고 각 칸은 무엇을 뜻한다고 판단했습니까?
3. 가장 오래된 방문과 가장 최근 방문 사이는 며칠입니까? 만료 시각 칸과 견주면 보존 기간을 어림할 수 있습니까?
4. 방문 하나를 골라 지오 BLOB 에서 좌표를 직접 풀고, 도구가 보여 주는 좌표와 같은지 확인합니다.
5. 같은 검체의 로컬 백업이 있다면 `routined` DB 가 백업에 있습니까?

## 참고 문헌

1. Apple, "Location Services & Privacy" (2026-02-11) — https://www.apple.com/legal/privacy/data/en/location-services/
2. Apple Support, "About privacy and Location Services in iOS, iPadOS, and watchOS" (2026-05-20) — https://support.apple.com/en-us/102515
3. Sarah Edwards, mac4n6.com, "On the Tenth Day of APOLLO ... iOS Location Analysis" (2018-12-23) — http://www.mac4n6.com/blog/2018/12/23/on-the-tenth-day-of-apollo-my-true-love-gave-to-me-an-oddly-detailed-map-of-my-recent-travels-ios-location-analysis
4. abrignoni/iLEAPP, `scripts/artifacts/mapsSync.py` (GitHub) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/mapsSync.py
