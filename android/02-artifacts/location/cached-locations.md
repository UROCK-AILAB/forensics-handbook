---
title: "위치 캐시"
parent: "아티팩트 · 위치"
nav_order: 710
---

# 위치 캐시 (Cached Locations)

## 한 줄 요약

위치 캐시 (Cached Locations) 는 앱이 따로 저장하지 않아도 시스템과 Google Play 서비스 쪽에 남는 위치 흔적을 한데 묶은 말이고, 구형 기기의 `cache.cell`·`cache.wifi` 파일처럼 좌표와 시각이 함께 남는 것부터 배터리 기록의 GPS 켜짐·꺼짐 줄처럼 시각만 남는 것까지 종류마다 알려 주는 범위가 다릅니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

폰은 GPS 말고도 기지국과 와이파이로 위치를 어림하고, 그 결과를 저장해 두는 곳이 몇 군데 있습니다. 이 페이지에서 다루는 흔적은 네 가지이고, 좌표가 남는지 여부가 서로 다릅니다.

| 흔적 | 좌표 | 시각 | 기기 |
|---|---|---|---|
| `cache.cell`·`cache.wifi` 파일 | 있음(도 단위 실수) | 있음(유닉스 밀리초) | 구형 기기 [1] |
| Play 서비스 rawsignal LevelDB | 있음(E7 정수) | 있음(유닉스 밀리초) | 현행 기기 표본 일부 [2] |
| 위치 관련 설정 키 | 없음 | 없음 | 관찰 기기 |
| 배터리 기록의 GPS 줄 | 없음 | 있음 | 관찰 기기 |

rawsignal LevelDB 는 좌표와 시각이 여러 건 쌓이는 캐시 성격의 저장소지만 구글 타임라인과 같은 Play 서비스 폴더에 있어서, 경로·구조·표본은 [구글 위치 기록과 타임라인 (Timeline)](google-timeline.md) 페이지에서 한 번에 다룹니다. 이 페이지는 나머지 세 가지를 설명합니다.

## 위치와 버전별 차이

### cache.cell · cache.wifi

ALEAPP 의 cachelocation 모듈은 아래 두 파일을 읽습니다 [1].

```
*/com.google.android.location/files/cache.cell/cache.cell
*/com.google.android.location/files/cache.wifi/cache.wifi
```

패키지 이름이 `com.google.android.location` 이고, 구형 구글 네트워크 위치 제공자의 폴더입니다 [1]. 모듈은 2021년에 만들어졌고 시험 표본 정보가 없으며 [1], 이 파일이 Android 10 이후 기기에 아직 생기는지는 확인하지 못했습니다. 그래서 이 파일은 구형 기기에서 볼 수 있는 흔적으로 소개하고, 현행 기기에서 없다고 해서 이상하다고 보지 않습니다.

### 설정 키

관찰 기기의 설정 값에는 이름에 위치가 들어간 키가 세 영역에 흩어져 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 키 이름만 확인했고 값과 뜻은 확인하지 못했으며, 삼성 전용 키인지 AOSP 에도 있는 키인지도 확인하지 못했습니다.

| 영역 | 키 이름 |
|---|---|
| settings global | `assisted_gps_enabled`, `location_background_throttle_interval_ms`, `location_ignore_settings_package_whitelist`, `location_popup_sim_off_count`, `obtain_paired_device_location` |
| settings secure | `location_mode`, `location_changer`, `mock_location`, `gs_location_state`, `skyhook_location_enabled`, `trusted_locations_count` |
| settings system | `user_agree_to_use_location_service`, `emergency_location_sharing_enabled`, `gps_noti_sound_enabled`, `clock_weather_location_exist` |

설정 값을 뽑고 읽는 법은 [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) 페이지에 있습니다.

### 배터리 기록의 GPS 줄

관찰 기기의 `dumpsys batterystats` 출력 앞부분 "Battery History" 에는 GPS 가 켜지고 꺼진 줄과 GPS 신호 품질 줄이 있었고, 와이파이 스캔이 시작되고 끝난 줄도 함께 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 값은 가려져 있어서 모양만 보여 줍니다.

```
##-## ##:##:##.### ### +gps +state=<값>
##-## ##:##:##.### ### -gps -state=<값>
##-## ##:##:##.### ### gps_signal_quality=<값>
##-## ##:##:##.### ### +wifi_scan
##-## ##:##:##.### ### -wifi_scan
```

배터리 기록 전체의 짜임새는 [배터리 사용 기록 (batterystats)](../app-usage/batterystats.md) 페이지에서 다룹니다.

## 구조

`cache.cell`·`cache.wifi` 는 빅엔디언 바이너리 파일이고, ALEAPP 코드 기준 구조는 아래와 같습니다 [1]. ALEAPP 코드 주석에는 이 파싱 방법을 2011년 Spreitzenbarth 의 글 "decoding cache.cell and cache.wifi files" 에서 가져왔다고 적혀 있지만 [1], 그 글은 열어 보지 않았습니다.

| 위치 | 크기 | 뜻 |
|---|---|---|
| 파일 머리 +0 | 2바이트(short) | version |
| 파일 머리 +2 | 2바이트(short) | entries(항목 수) |
| 항목 +0 | 2바이트(short) | 키 길이 |
| 항목 +2 | 키 길이만큼 | 키 |
| 키 뒤 +0 | 4바이트(int) | accuracy |
| 키 뒤 +4 | 4바이트(int) | confidence |
| 키 뒤 +8 | 8바이트(double) | latitude |
| 키 뒤 +16 | 8바이트(double) | longitude |
| 키 뒤 +24 | 8바이트(부호 없는 64비트) | readtime |

항목은 entries 수만큼 이어집니다. 위도·경도는 도 단위 실수가 그대로 들어 있어서 따로 나눌 필요가 없습니다 [1]. 키에 어떤 값(기지국 식별자, 와이파이 주소 등)이 어떤 모양으로 들어 있는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것**

`cache.cell`·`cache.wifi` 의 항목 하나는 readtime 시각에 위치 제공자가 그 키에 대해 저장해 둔 좌표와 정확도입니다. 배터리 기록의 `+gps`·`-gps` 줄은 그 시각에 기기 GPS 가 켜지고 꺼졌다는 기록이라서, 누군가 위치를 쓰던 시간대를 좁히는 데 쓸 수 있습니다. 설정 키는 위치 기능이 어떤 상태였는지 알아보는 출발점입니다.

**증명하지 못하는 것**

캐시 항목의 좌표는 기지국이나 와이파이의 어림 위치일 수 있어서 폰이 그 좌표에 정확히 있었다는 뜻은 아닙니다. 캐시에 항목이 있다고 해서 사용자가 위치를 조회했다는 뜻도 아닙니다. 배터리 기록의 GPS 줄에는 좌표가 없어서 (확인 범위: SM-S937N, Android 16, One UI 8.5) 어디에 있었는지는 알려 주지 않고, 이 줄만으로 어느 앱이 GPS 를 켰는지 알 수 있는지도 확인하지 못했습니다. 설정 키 값이 무엇을 뜻하는지 확인하지 못했으니 `mock_location` 같은 키도 이름만 보고 가짜 위치를 썼다고 판단하지 않습니다.

## 시각 해석

`cache.cell`·`cache.wifi` 의 readtime 은 유닉스 밀리초이고, ALEAPP 는 1000 으로 나눠 UTC 로 바꿉니다 [1]. 값을 읽는 일반 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

배터리 기록의 줄은 `MM-DD HH:MM:SS.mmm` 모양이라서 줄 안에 연도가 없고, 시간대 표기도 줄에 없습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 같은 출력에는 `RESET:TIME:` 으로 시작하는 줄이 있었고 (확인 범위: SM-S937N, Android 16, One UI 8.5), 이 줄이 기준 시각을 알려 주는지는 [배터리 사용 기록 (batterystats)](../app-usage/batterystats.md) 페이지에서 확인합니다. 현지 시각으로 옮기기 전에 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 에서 기기 시간대를 먼저 봅니다.

## 함정과 한계

첫째, `cache.cell`·`cache.wifi` 는 구형 패키지의 파일이라서 현행 기기에는 없을 수 있지만, 언제부터 생기지 않는지는 확인하지 못했습니다. 없다는 사실을 삭제 흔적으로 읽지 않습니다.

둘째, 배터리 기록은 명령을 실행한 때의 출력이고 보관 용량이 정해져 있습니다. 관찰 기기의 "Battery History" 머리줄에도 "used of" 모양으로 버퍼 사용량이 찍혔습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 오래된 GPS 줄이 없다는 사실은 그 시간대에 GPS 를 쓰지 않았다는 뜻이 아닐 수 있습니다.

셋째, 설정 키는 이름만 확인한 상태입니다. 키 값을 보고서에 쓰려면 같은 기기 설정 화면이나 소스 코드로 뜻부터 확인합니다.

넷째, 사진 EXIF 위치, 와이파이 접속 기록 같은 다른 위치 흔적은 이 페이지에서 조사하지 않았고, 아래 교차 검증 표의 페이지에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 위 구조 표 [1] 로 만든 예시이고, 실제 검체에서 나온 바이트가 아닙니다. 항목 하나짜리 파일에서 머리와 항목의 숫자 부분을 보면 이렇습니다(키 4바이트는 내용이 확인되지 않아 `xx` 로 둡니다).

```
00 01 00 01                    version = 1, entries = 1
00 04                          키 길이 = 4
xx xx xx xx                    키
00 00 00 1E                    accuracy   = 30
00 00 00 4B                    confidence = 75
40 42 C8 83 12 6E 97 8D        latitude   = 37.5665 (double)
40 5F BE 97 8D 4F DF 3B        longitude  = 126.978 (double)
00 00 01 8B CF E5 68 00        readtime   = 1700000000000 ms
                                          → 2023-11-14 22:13:20 UTC
```

실제 파일에서도 머리 4바이트로 항목 수를 먼저 읽고, 항목마다 키 길이만큼 건너뛴 뒤 32바이트를 위 순서대로 읽습니다. 항목 수만큼 읽었는데 파일이 남거나 모자라면 파일이 잘렸거나 구조가 다른 판일 수 있습니다. ALEAPP 는 항목 수에 32 를 곱한 값이 파일 크기보다 작을 때만 파일을 읽고, 그렇지 않으면 손상된 파일로 보고 건너뜁니다 [1]. 도구 결과가 비어 있으면 이 조건에 걸렸는지부터 헥스로 확인합니다.

### 공개 도구로 한 번

ALEAPP 의 cachelocation 모듈이 두 파일을 찾아 좌표·정확도·시각 표를 만들어 줍니다 [1]. 헥스로 읽은 항목 한두 개와 도구 결과를 맞춰 보는 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 페이지에 있습니다. 배터리 기록은 `dumpsys batterystats` 출력이나 [버그 리포트 (bugreport)](../logs/bugreport.md) 안의 같은 부분에서 `gps` 가 들어간 줄만 걸러 시각 순으로 놓고, `+gps` 와 다음 `-gps` 를 짝지어 GPS 가 켜져 있던 구간을 만듭니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [구글 위치 기록과 타임라인 (Timeline)](google-timeline.md) | GPS 가 켜진 구간에 좌표 기록이 있는지 |
| [구글 지도 (Google Maps)](google-maps.md) | 같은 시간대에 길찾기·검색을 했는지 |
| [와이파이 설정과 접속 기록 (WifiConfigStore)](../network/wifi.md) | 와이파이 스캔 구간과 접속 기록이 맞는지 |
| [카메라 사진과 메타데이터 (DCIM·EXIF)](../media/dcim-exif.md) | GPS 가 켜진 시각에 찍은 사진에 위치가 있는지 |
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | GPS 가 켜진 때 앞에 있던 앱이 무엇인지 |

조사 흐름은 [그 시각에 어디 있었나 (Location)](../../04-scenarios/activity/location.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 검체로 아래 질문을 풀어 봅니다.

1. `com.google.android.location` 폴더가 있습니까? 있다면 `cache.cell` 과 `cache.wifi` 의 머리에 적힌 항목 수는 각각 몇 개입니까?
2. 헥스로 읽은 첫 항목의 readtime 을 UTC 로 바꾸면 언제이고, ALEAPP 결과와 같습니까?
3. 검체에 버그 리포트가 들어 있다면 `+gps` 줄과 `-gps` 줄은 각각 몇 개이고, 짝이 맞지 않는 줄이 있습니까?
4. 검체의 설정 값에서 위 표의 키 가운데 어떤 키가 있고, 관찰 기기와 다른 키가 있습니까?

## 참고 문헌

1. ALEAPP — scripts/artifacts/cachelocation.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/cachelocation.py
2. ALEAPP — scripts/artifacts/appSemloc.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/appSemloc.py
