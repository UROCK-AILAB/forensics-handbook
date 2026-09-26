---
title: "삼성 헬스"
parent: "아티팩트 · 삼성 기기 전용"
nav_order: 1140
---

# 삼성 헬스 (Samsung Health)

## 한 줄 요약

삼성 헬스는 걸음 수와 운동, 심박 같은 건강 기록을 앱 데이터 폴더의 암호화된 SQLite 데이터베이스에 모으고, 운동 기록 한 건 안에는 초 단위 측정값과 GPS 이동 경로가 압축된 JSON 으로 들어 있을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

삼성 헬스의 패키지 이름은 `com.sec.android.app.shealth` 입니다. 이 앱은 사용자가 직접 넣거나 기기가 측정한 건강 자료를 데이터베이스 하나에 모읍니다. 이 데이터베이스에서는 걸음 수, 운동 종류와 시간·거리·칼로리, 운동 중 실시간 기록(초 단위 심박 등), 보폭 종류를 읽을 수 있습니다[1][2].

삼성 헬스 SDK (Samsung Health SDK for Android) 에서 공통 필드를 쓰는 데이터 종류는 45개이고, 걸음 수(StepCount), 심박(HeartRate), 수면(Sleep), 운동(Exercise), 체중(Weight), 키(Height), 혈압(BloodPressure), 혈당(BloodGlucose), 체온(BodyTemperature), 산소포화도(OxygenSaturation), 음식 섭취(FoodIntake), 물 섭취(WaterIntake), 카페인 섭취(CaffeineIntake) 가 그 예입니다[4]. 데이터 종류마다 운동의 "com.samsung.health.exercise" 같은 이름이 붙습니다[3].

SDK 는 다른 앱이 삼성 헬스와 데이터를 주고받는 규칙입니다. 그래서 SDK 필드 이름이 기기 안 데이터베이스의 표 이름·열 이름과 같다고 볼 수 없습니다. 표 이름과 열 이름은 공개 파서 자료에도 나오지 않아 실제 데이터로 확인해야 합니다[1][2].

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 패키지 | `com.sec.android.app.shealth` |
| 주 데이터베이스 | `/data/data/com.sec.android.app.shealth/databases/SecureHealthData.db` |
| 암호화 | 기본으로 암호화되어 있음 |
| 공개 파서의 입력 | 상용 분석 도구로 복호화한 데이터베이스 |

앱 데이터 폴더가 어떻게 짜여 있는지는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 를 봅니다. 공개 파서는 복호화하지 않고, 다른 도구로 이미 복호화한 파일을 받아 읽습니다. 파서 문서에 예로 나오는 `.../SecureHealthData.db/SecureHealthData.db.decrypted` 같은 경로는 추출 도구가 결과물 안에 붙인 이름으로 보이고, 기기 안 원래 경로는 아닌 것으로 보입니다[1].

삼성 헬스 판이나 One UI 판에 따라 경로와 구조가 어떻게 달라지는지는 실제 기기로 확인해야 합니다. 수집 방법에 따라 얻을 수 있는 것은 아래처럼 갈립니다.

| 수집 방법 | 얻을 수 있는 것 |
|---|---|
| 파일 시스템 전체 추출 | `SecureHealthData.db` (암호화된 상태) |
| adb 일반 권한 | 데이터베이스는 못 읽고, 앱 사용 기록에서 삼성 헬스가 실행된 흔적만 볼 수 있음 |

앱 사용 기록을 읽는 법은 [앱 사용 기록](../app-usage/usagestats/index.md) 에서 다룹니다.

## 구조

저장 형식 자체는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 를 봅니다. 실제 표 이름은 공개 자료에 없으므로, 아래는 SDK 가 정의한 필드입니다[3][4]. 이 필드가 기기 안에서 어떤 열 이름으로 저장되는지는 실제 데이터로 확인해야 합니다.

### 모든 데이터 종류의 공통 필드

| SDK 필드 | 뜻 |
|---|---|
| `UUID` | 데이터마다 붙는 고유 ID, 10~36자 |
| `CREATE_TIME` | 헬스 데이터 저장소에 만들어진 시각, UTC 밀리초 |
| `UPDATE_TIME` | 고친 시각, UTC 밀리초. 처음에는 `CREATE_TIME` 과 같음 |
| `PACKAGE_NAME` | 데이터를 넣은 앱 |
| `DEVICE_UUID` | 데이터를 만든 기기의 식별자, 반드시 들어감 |
| `CUSTOM` | 압축한 JSON |

### 운동(Exercise) 필드

| SDK 필드 | 뜻 |
|---|---|
| `START_TIME`, `END_TIME` | 운동 시작·끝 시각, UTC 밀리초 |
| `TIME_OFFSET` | 시간대와 서머타임을 반영한 차이, 밀리초 |
| `DURATION` | 운동 시간, 밀리초 |
| `DISTANCE` | 거리, 미터 |
| `CALORIE` | 소모 열량, 킬로칼로리 |
| `EXERCISE_TYPE` | 운동 종류 번호. 0 은 사용자가 정의한 종류 |
| `LIVE_DATA` | 심박·케이던스·속도·파워·거리를 담은 압축 JSON 바이트, 최대 1000KB |
| `LOCATION_DATA` | WGS 84 좌표로 적은 이동 경로를 담은 압축 JSON 바이트, 최대 1000KB |
| `ADDITIONAL` | 수영장 정보처럼 운동마다 다른 세부 내용 |

운동 중 실시간 기록은 데이터베이스 안에 GZIP 으로 압축한 JSON 덩어리로 들어 있습니다[1][2]. SDK 필드의 "압축 JSON" 이 이 GZIP 덩어리일 가능성이 있지만, 같은 열인지는 실제 데이터로 확인해야 합니다. 운동 종류는 번호로만 남아서 삼성 SDK 의 번호표와 맞춰 봐야 이름을 알 수 있습니다.

## 증거로서 의미

### 증명하는 것

운동 기록 한 건은 기록된 시작·끝 시각에 그 종류의 운동이 삼성 헬스에 기록되어 있다는 뜻입니다. `LOCATION_DATA` 가 채워져 있으면 그 운동 동안의 이동 경로가 좌표로 함께 남아 있어서, 운동 기록 한 건이 위치 기록 역할까지 합니다. `LIVE_DATA` 에는 심박 같은 값이 초 단위로 남아서 운동 도중 언제 멈췄고 언제 빨라졌는지를 따라갈 수 있습니다.

`PACKAGE_NAME` 은 어느 앱이 데이터를 넣었는지를 가리킵니다. `DEVICE_UUID` 로는 워치 같은 다른 기기에서 온 기록을 폰에서 잰 기록과 구분할 수 있을 것으로 보입니다[4].

### 증명하지 못하는 것

기록에는 기기와 앱만 나오고 사람은 나오지 않아서, 그 시각에 누가 폰이나 워치를 지니고 있었는지는 이 기록만으로 알 수 없습니다([그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)). 다른 앱도 삼성 헬스에 데이터를 넣을 수 있어서, 한 기록이 기기 센서로 잰 값인지 다른 앱이 넣은 값인지는 `PACKAGE_NAME` 과 `DEVICE_UUID` 를 보고 따로 판단해야 합니다. 암호화를 풀지 못하면 내용은 하나도 읽을 수 없고, adb 일반 권한으로 얻는 앱 사용 기록은 앱을 연 흔적일 뿐 운동이나 걸음을 보여 주지 않습니다.

보고서에는 "피의자가 이 길을 뛰었다" 가 아니라 "이 시각에 이 기기의 삼성 헬스에 이 종류의 운동 기록이 있고, 그 기록에 이 경로가 좌표로 들어 있다" 처럼 씁니다.

## 시각 해석

| SDK 필드 | 값 | 무엇이 바뀔 때 바뀌나 |
|---|---|---|
| `START_TIME`, `END_TIME` | UTC 밀리초 | 운동을 시작하고 끝낸 때 |
| `CREATE_TIME` | UTC 밀리초 | 헬스 데이터 저장소에 기록이 만들어진 때 |
| `UPDATE_TIME` | UTC 밀리초 | 기록을 고친 때. 처음에는 `CREATE_TIME` 과 같음 |
| `TIME_OFFSET` | 밀리초 차이 | 기록 당시 시간대와 서머타임을 반영한 값 |

운동한 때는 `START_TIME`·`END_TIME` 이고 `CREATE_TIME` 은 저장소에 들어간 때라서, 두 시각이 다르면 기록이 나중에 들어왔을 수 있습니다. 두 값을 섞지 말고 따로 적습니다. `UPDATE_TIME` 이 `CREATE_TIME` 과 다르면 기록이 한 번 이상 고쳐졌다는 뜻입니다.

현지 시각은 `TIME_OFFSET` 으로 맞출 수 있지만, 이 값을 더하는지 빼는지는 공개 자료에 풀어 적혀 있지 않습니다. 기기 시간대를 알고 있는 기록 한 건으로 먼저 방향을 확인하고 나머지에 적용합니다([시간대와 시각 설정](../system-account/time-zone.md)). 유닉스 밀리초를 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

## 함정과 한계

데이터베이스가 기본으로 암호화되어 있어서, 파일을 확보해도 복호화 수단이 없으면 분석이 거기서 멈춥니다. 공개 파서도 이미 복호화한 파일을 받습니다.

표 이름과 열 이름이 공개 자료에 없어서, SDK 필드 이름으로 데이터베이스를 검색하면 아무것도 나오지 않을 수 있습니다. 먼저 표 목록을 보고, 압축 덩어리가 든 열은 아래 "헥스로 한 번" 처럼 머리 바이트로 찾습니다. `LIVE_DATA`·`LOCATION_DATA` 는 압축을 풀기 전에는 SQLite 도구에서 뜻 없는 바이트로만 보이고, 한 건에 최대 1000KB 까지 들어갈 수 있습니다.

`EXERCISE_TYPE` 이 0 이면 사용자가 정의한 운동이라서 번호표로 이름을 알 수 없습니다. 삼성 헬스 판마다 구조가 어떻게 달라지는지, 워치에서 온 기록이 폰에 언제 들어오는지는 실제 데이터로 확인해야 합니다. 지운 기록이 어떻게 남는지도 알려진 것이 없어서, 복호화한 데이터베이스에서 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 방법으로 따로 찾아봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 GZIP 형식 명세로 만든 예시이고, 실제 기기에서 나온 값이 아닙니다. 복호화한 데이터베이스에서 GZIP 으로 압축한 JSON 열은 이런 머리 바이트로 시작합니다.

```
1F 8B          GZIP 표지
08             압축 방식 8 (deflate)
00             플래그
00 00 00 00    수정 시각 (0 이면 기록하지 않음)
00             추가 플래그
..             운영체제 번호
.. .. ..       압축된 본문
(끝 8바이트)   CRC-32 와 압축 전 길이
```

표 이름을 모를 때는 이 머리 바이트로 열을 찾습니다. 아래 쿼리는 한 표의 한 열을 검사하는 예이고, 표와 열 이름은 표 목록을 보고 바꿔 넣습니다.

```sql
SELECT rowid, length(칸이름) FROM 표이름
WHERE typeof(칸이름) = 'blob' AND hex(substr(칸이름, 1, 3)) = '1F8B08';
```

찾은 BLOB 을 파일로 꺼내 gzip 으로 풀면 JSON 글이 나오고, 그 안에서 심박이나 좌표 값을 읽습니다.

### 공개 도구로 한 번

1. 파일 시스템 전체 추출본에서 `SecureHealthData.db` 를 딸린 파일까지 함께 복사합니다.
2. 기관이 쓰는 분석 도구로 복호화한 사본을 만듭니다. 원본 파일은 그대로 둡니다.
3. 공개 도구 Samsung Secure Health Data Parser 에 복호화한 사본을 넣어 걸음 수와 운동, 실시간 기록을 뽑습니다.
4. 같은 사본을 SQLite 도구로 열어 운동 기록 몇 건을 골라, 시각과 거리 값이 파서 결과와 같은지 맞춰 봅니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [앱 사용 기록](../app-usage/usagestats/index.md) | 운동 기록 시각 앞뒤로 삼성 헬스를 연 흔적 |
| [위치 캐시](../location/cached-locations.md), [구글 위치 기록과 타임라인](../location/google-timeline.md) | `LOCATION_DATA` 의 경로와 같은 시각의 다른 위치 기록 |
| [배터리 사용 기록](../app-usage/batterystats.md) | 운동 시각에 GPS 가 켜진 기록 |
| [블루투스 장치](../network/bluetooth.md) | 워치 같은 연결 기기가 있었는지 |

삼성 전용 흔적으로는 `com.samsung.android.mcfds` 의 `context_engine_database` 와 `SleepDetection.db` 도 있습니다[5]. 이름으로 보면 수면 기록과 맞춰 볼 후보이고, 내용은 실제 데이터로 확인해야 합니다. 여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 을, 위치를 묻는 조사 흐름은 [그 시각에 어디 있었나](../../04-scenarios/activity/location.md) 를 봅니다.

## 실습

공개된 시험 이미지 가운데 삼성 헬스를 쓴 삼성 기기 이미지를 골라 아래 질문을 풀어 봅니다. 공개 이미지에는 복호화 수단이 없을 수 있어서, 1번에서 막히면 그 사실을 기록하는 것까지가 실습입니다.

1. `SecureHealthData.db` 가 있습니까? 첫 16바이트가 SQLite 표지로 시작합니까, 아니면 암호화되어 알아볼 수 없습니까?
2. 복호화한 사본이 있다면, 표 목록 가운데 운동과 걸음 수를 담은 표는 무엇입니까?
3. GZIP 머리 바이트로 시작하는 BLOB 은 어느 표의 어느 열에 있고, 풀어 보면 어떤 JSON 키가 나옵니까?
4. 운동 기록 한 건의 시작·끝 시각을 UTC 와 현지 시각으로 적고, 같은 시각의 앱 사용 기록과 맞춰 봅니다.

## 참고 문헌

1. breakpointforensics, Samsung-Secure-Health-Data-Parser- README — https://github.com/breakpointforensics/Samsung-Secure-Health-Data-Parser-/blob/main/README.md
2. Breakpoint Forensics, "Samsung Secure Health Data Parser — A Forensic Tool for Parsing & Analyzing Samsung Secure Health Databases" (2024-11-06) — https://breakpointforensics.com/2024/11/06/samsung-secure-health-data-parser-a-forensic-tool-for-parsing-analyzing-samsung-secure-health-databases/
3. Samsung Developers, Samsung Health SDK for Android, HealthConstants.Exercise — https://developer.samsung.com/health/android/data/api-reference/com/samsung/android/sdk/healthdata/HealthConstants.Exercise.html
4. Samsung Developers, Samsung Health SDK for Android, HealthConstants.Common — https://developer.samsung.com/health/android/data/api-reference/com/samsung/android/sdk/healthdata/HealthConstants.Common.html
5. Mattia Epifani, "Beyond the Known: A Call to Forensic Research on Samsung Android Artifacts" (2025-11-07) — https://blog.digital-forensics.it/2025/11/beyond-known-call-to-forensic-research.html
