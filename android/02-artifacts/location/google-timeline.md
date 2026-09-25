---
title: "구글 위치 기록과 타임라인"
parent: "아티팩트 · 위치"
nav_order: 700
---

# 구글 위치 기록과 타임라인 (Timeline)

## 한 줄 요약

구글 지도의 타임라인 (Timeline) 은 사용자가 켜 두면 로그인한 기기마다 방문한 곳과 이동 경로를 자동으로 저장하고 [1], 기기 안에서는 Google Play 서비스 폴더의 SQLite DB 와 LevelDB 에 좌표와 시각이 남아 있어서 "그 시각에 폰이 어디 있었나" 를 따질 때 가장 먼저 찾아볼 기록입니다 [2][3].

## 무엇을 기록하나 · 왜 생기나

구글 설명에 따르면 타임라인은 로그인한 각 기기에서 방문한 곳과 이동 경로를 저장하고, 화면에 보이는 데이터가 기기에서 직접 나오기 때문에 컴퓨터용 지도에서는 타임라인을 쓸 수 없습니다 [1]. 타임라인은 구글 계정에서 기본으로 꺼져 있고, 사용자가 동의해야 켜집니다 [1].

백업을 켜면 지도 앱이 암호화한 사본을 구글 서버에 저장하고, 이 백업으로 다른 기기에 데이터를 옮길 수 있습니다 [1]. 데이터는 자동 삭제 설정에 따라, 또는 사용자가 지울 때까지 남고, 사용자는 "내 Google 활동" 과 휴대폰 지도 앱에서 지울 수 있습니다 [1]. 자동 삭제 기간으로 어떤 선택지가 있는지는 확인하지 못했습니다.

예전 이름인 "위치 기록 (Location History)" 이 "타임라인" 으로 바뀐 시기와, 서버에 두던 기록이 기기 저장으로 옮겨 간 날짜·단계는 이번에 연 자료에서 확인하지 못했습니다. ALEAPP 에 예전 서버형 위치 기록의 기기 쪽 설정을 읽는 ulrUserprefs 모듈이 있다는 것까지만 확인했고 [4], 그 경로와 내용은 읽지 않았습니다.

## 위치와 버전별 차이

기기 안 저장소는 두 곳이고, 파일 주인은 구글 지도 앱이 아니라 Google Play 서비스(`com.google.android.gms`) 입니다 [2][3]. ALEAPP 는 아래 경로 패턴으로 찾습니다.

```
*/com.google.android.gms/databases/odlh-storage.db*
*/com.google.android.gms/app_semanticlocation_rawsignal_db/*
```

첫째 파일은 기기 내 위치 기록 (On Device Location History, ODLH) 을 담은 SQLite DB 이고 [2], 둘째 폴더는 LevelDB 입니다 [3]. 두 저장소가 원재료와 정리된 구간의 관계인지는 확인하지 못했습니다. 앱 데이터 영역은 루팅되지 않은 기기에서 adb 일반 권한으로 읽을 수 없는 곳이고, 짜임새는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 페이지에서 다룹니다.

타임라인을 쓰는 데 필요한 Android 버전과 지도 앱 버전은 구글 도움말에 없었습니다 [1]. 대신 ALEAPP 모듈에 시험한 표본 기기와 결과 행 수가 적혀 있어서 [2][3], 기기에 따라 비어 있을 수 있다는 점을 볼 수 있습니다. 아래 표는 그 일부입니다.

| 표본 기기 | Android | odlh-storage.db 행 수 [2] | rawsignal LevelDB [3] |
|---|---|---|---|
| Pixel 6a | 13 | 393 | 0행 |
| Pixel 7a | 14 | 2102 | 0행 |
| Pixel 8 Pro | 16 | 605 | 1497 |
| POCO X7 | 15 | 3251 | 5033 |
| Galaxy A53 | 14 | 0행 | 0행 |
| Galaxy S20 | 13 | 0행 | 0행 |

삼성 표본 두 대는 두 저장소 모두 0행이었고, Pixel 6a·7a 도 odlh-storage.db 에는 행이 있지만 LevelDB 는 0행이었습니다 [2][3]. 그래서 빈 결과가 삼성 기기에만 나타나는 일은 아니고, 삼성 One UI 에서 저장 위치가 다른지 설정 차이 때문인지도 확인하지 못했습니다. 검체에서 이 두 곳이 비어 있어도 사용자가 이동하지 않았다고 결론 내리면 안 되고, 그 기기에 타임라인이 켜져 있었는지부터 따져야 합니다.

관찰 기기의 공용 저장 공간에는 `/sdcard/Android/media/com.google.android.gms` 폴더가 있었습니다. 그 안에 타임라인과 관련된 파일이 있는지는 확인하지 못했습니다.

## 구조

### odlh-storage.db

SQLite 파일 형식은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에서 다룹니다. ALEAPP 가 읽는 표는 두 개입니다 [2].

| 표 | 칸 | 담긴 것 |
|---|---|---|
| `semantic_segment_table` | `start_timestamp_seconds`, `end_timestamp_seconds`, `segment_type`, `semantic_segment`, `shown_in_timeline`, `is_finalized`, `hierarchy_level`, `segment_id`, `obfuscated_gaia_id` | 타임라인 구간 한 개 |
| `edited_segment_table` | `start_timestamp_seconds`, `end_timestamp_seconds`, `block_start_timestamp_seconds`, `block_end_timestamp_seconds`, `segment_type`, `is_edit_uploaded`, `segment_id`, `obfuscated_gaia_id` | 사용자가 고친 구간과, 그 수정을 올렸는지 여부 |

`semantic_segment` 칸은 프로토콜 버퍼 덩어리이고, 좌표가 들어 있는 구간에서만 위도·경도를 꺼낼 수 있습니다 [2]. ALEAPP 는 필드 경로 3→1→4→5 아래의 1번 필드를 위도로, 2번 필드를 경도로 읽습니다 [2]. 값은 E7 고정소수라서 정수를 10,000,000 으로 나누면 도 단위가 되고, 부호 없는 값으로 읽힌 숫자가 2^31 을 넘으면 2^32 를 빼서 음수로 되돌립니다 [2]. 덩어리를 읽는 일반 방법은 [프로토콜 버퍼 (Protocol Buffers)](../../01-foundations/data-formats/protobuf.md) 페이지에 있습니다.

`segment_type` 은 정수인데 ALEAPP 도 숫자의 뜻을 풀지 않고 그대로 보고합니다 [2]. 어느 숫자가 방문이고 어느 숫자가 이동인지는 확인하지 못했으니 보고서에 이름을 붙이지 않습니다.

### app_semanticlocation_rawsignal_db

LevelDB 의 기록 값마다 프로토콜 버퍼가 들어 있고, ALEAPP 는 필드 1→1 아래를 아래처럼 읽습니다 [3]. LevelDB 자체는 [LevelDB와 IndexedDB](../../01-foundations/data-formats/leveldb-indexeddb.md) 페이지에서 다룹니다.

| 필드 | 뜻 | 단위 |
|---|---|---|
| 1 | 위도 | E7 |
| 2 | 경도 | E7 |
| 3 | 수평 정확도 | ALEAPP 는 1000 으로 나눠 보고 |
| 6 | 시각 | 유닉스 밀리초 |

ALEAPP 결과에는 Timestamp, Rec. Sequence(LevelDB 기록 순번), Latitude, Longitude, Horizontal Acc., Origin(값이 들어 있던 LevelDB 파일) 칸이 나옵니다 [3].

## 증거로서 의미

**증명하는 것**

`semantic_segment_table` 한 행은 시작 시각과 끝 시각이 붙은 구간 한 개이고, 좌표를 꺼낼 수 있으면 그 구간에 기기가 기록한 위치가 있다는 뜻입니다. rawsignal 쪽 한 건은 특정 밀리초 시각에 기기가 남긴 좌표와 정확도입니다. `edited_segment_table` 에 행이 있으면 누군가 타임라인 구간을 고쳤다는 기록이고, `is_edit_uploaded` 로 그 수정이 서버에 올라갔는지를 볼 수 있습니다 [2]. 타임라인은 기본으로 꺼져 있는 기능이라서 [1], 기록이 쌓여 있다면 그 계정에서 누군가 기능을 켠 적이 있다는 정황으로 볼 수 있습니다.

**증명하지 못하는 것**

좌표는 폰의 위치이지 사람의 위치가 아니고, 누가 폰을 들고 있었는지는 알려 주지 않습니다. 정확도 값이 있을 때는 그 반경 안 어딘가라는 뜻이라서 특정 건물 안에 있었다고까지 말하기는 어렵습니다. `segment_type` 의 뜻을 모르니 "머물렀다" 와 "지나갔다" 를 이 칸만으로 가를 수 없고, 기록이 없는 시간대가 "움직이지 않았다" 나 "그곳에 없었다" 를 뜻하지도 않습니다.

## 시각 해석

odlh-storage.db 의 시각은 칸 이름대로 유닉스 초이고, ALEAPP 는 UTC 로 바꿉니다 [2]. 한 구간에는 시작과 끝 두 시각이 있고, `edited_segment_table` 에는 `block_start_timestamp_seconds`·`block_end_timestamp_seconds` 가 더 있습니다 [2]. rawsignal LevelDB 의 시각은 유닉스 밀리초입니다 [3]. 두 저장소는 시각 단위가 달라서, 한 타임라인에 올릴 때 단위를 맞추지 않으면 1000 배 어긋난 날짜가 나옵니다. 값을 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md), 현지 시각으로 옮길 때 확인할 것은 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 페이지에 있습니다.

## 함정과 한계

첫째, 이 페이지의 경로·표·필드 번호는 ALEAPP 가 이렇게 읽는다는 사실이고, 모든 Play 서비스 판에서 그렇게 저장한다는 보증은 아닙니다 [2][3]. ALEAPP 는 이 모듈의 참고 자료로 "Cellebrite Location Booklet 2025" 를 적었지만 [2], 그 자료는 열어 보지 않았습니다.

둘째, 삼성 표본에서는 두 저장소가 모두 비어 있었고, 픽셀 표본 가운데에도 LevelDB 가 빈 기기가 있었습니다 [2][3]. 빈 결과가 나오면 원인을 확인하지 못한 상태라는 점을 보고서에 적습니다.

셋째, 사용자는 지도 앱과 "내 Google 활동" 에서 타임라인을 지울 수 있고 자동 삭제도 설정할 수 있습니다 [1]. 지운 뒤 기기 DB 에 무엇이 남는지는 확인하지 못했고, SQLite 에서 지운 행이 어디에 남을 수 있는지는 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md) 페이지에서 다룹니다. 구간을 고친 흔적은 `edited_segment_table` 에 남으니 [2], 조작을 의심할 때는 이 표부터 봅니다. 지우기·고치기를 조사하는 흐름은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md) 에 있습니다.

넷째, 서버 백업은 암호화한 사본이라서 [1] 기기 없이 서버 쪽만으로 무엇을 얻을 수 있는지는 확인하지 못했습니다. Google Takeout 으로 받는 타임라인 형식도 확인하지 못했고, 클라우드 쪽 확보 절차는 [클라우드 데이터 (Google Takeout 등)](../../03-techniques/acquisition/cloud-data.md) 페이지에서 다룹니다.

## 직접 분석해 보기

### 값으로 한 번

아래는 ALEAPP 의 변환 규칙 [2] 으로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다. 위도 필드에서 정수 375665000(16진수 `16 64 31 68`) 이 나오면 10,000,000 으로 나눠 37.5665000 도가 됩니다. 경도 필드에서 부호 없는 값 3074126721(16진수 `B7 3B 73 81`) 이 나오면 2^31 보다 크니 2^32 를 빼서 -1220840575 가 되고, 나누면 -122.0840575 도입니다.

```
위도  0x16643168 = 375665000   → 375665000 / 10^7 = 37.5665000
경도  0xB73B7381 = 3074126721  → 3074126721 - 2^32 = -1220840575
                                → -1220840575 / 10^7 = -122.0840575
```

DB 사본을 SQLite 도구로 열어 구간 시각부터 훑어볼 수 있습니다. 아래 질의는 위 구조 표로 만든 예시입니다.

```sql
SELECT segment_id,
       datetime(start_timestamp_seconds, 'unixepoch') AS start_utc,
       datetime(end_timestamp_seconds, 'unixepoch')   AS end_utc,
       segment_type, shown_in_timeline, is_finalized
FROM semantic_segment_table
ORDER BY start_timestamp_seconds;
```

좌표는 `semantic_segment` 칸의 바이트를 꺼내 프로토콜 버퍼 도구로 풀고, 위 경로의 필드를 찾아 위 규칙대로 바꿉니다. 같은 폴더의 `-wal` 파일도 함께 복사해야 하는 이유는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에 있습니다.

### 공개 도구로 한 번

ALEAPP 의 googleOdlh 모듈이 odlh-storage.db 를 [2], appSemloc 모듈이 rawsignal LevelDB 를 [3] 읽어 표로 만들어 줍니다. 도구가 낸 좌표 몇 개를 위 방식으로 직접 풀어 맞춰 보면 부호 처리와 단위가 맞는지 확인할 수 있고, 그 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 페이지에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [위치 캐시 (Cached Locations)](cached-locations.md) | 같은 시간대에 GPS 가 켜진 기록과 다른 위치 흔적이 있는지 |
| [구글 지도 (Google Maps)](google-maps.md) | 타임라인 구간 앞뒤로 길찾기·검색 기록이 있는지 |
| [카메라 사진과 메타데이터 (DCIM·EXIF)](../media/dcim-exif.md) | 같은 시각에 찍은 사진의 위치가 구간 좌표와 맞는지 |
| [와이파이 설정과 접속 기록 (WifiConfigStore)](../network/wifi.md) | 그 시간대에 접속한 네트워크가 장소와 어울리는지 |
| [계정 (Accounts)](../system-account/accounts/index.md) | 기기에 로그인한 구글 계정이 무엇인지 |

여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md), 조사 흐름은 [그 시각에 어디 있었나 (Location)](../../04-scenarios/activity/location.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 검체에 `com.google.android.gms` 앱 데이터가 들어 있으면 아래 질문을 풀어 봅니다.

1. odlh-storage.db 가 있습니까? 있다면 `semantic_segment_table` 에서 가장 이른 구간과 가장 늦은 구간은 언제입니까?
2. `segment_type` 값별로 행이 몇 개씩 있고, 좌표를 꺼낼 수 있는 구간은 그중 몇 개입니까?
3. `edited_segment_table` 에 행이 있다면, 고친 구간의 시각이 원래 구간 중 어느 것과 겹칩니까?
4. rawsignal LevelDB 의 좌표 가운데 하나를 골라, 같은 시각을 포함하는 ODLH 구간이 있는지 찾아봅니다.

## 참고 문헌

1. Google Maps 도움말, "Manage your Google Maps Timeline" (answer 6258979) — https://support.google.com/maps/answer/6258979?hl=en
2. ALEAPP — scripts/artifacts/googleOdlh.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/googleOdlh.py
3. ALEAPP — scripts/artifacts/appSemloc.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/appSemloc.py
4. ALEAPP — scripts/artifacts 폴더 목록 — https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
