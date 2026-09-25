---
title: "건강 데이터"
parent: "아티팩트 · 건강·지갑·워치"
nav_order: 1040
---

# 건강 데이터 (Health)

건강 앱이 모아 두는 걸음 수·심박수·수면·운동 기록과 그 기록을 잰 기기 정보를 SQLite 데이터베이스에서 읽고, 백업에 들어가는 조건과 시각 기준을 함께 정리합니다.

## 무엇을 기록하나 · 왜 생기나

아이폰의 건강 앱은 폰 자체의 센서, 짝지은 애플 워치, 건강 데이터에 기록 권한을 받은 다른 앱이 보낸 값을 한곳에 모읍니다. 걸음 수나 몸무게처럼 숫자로 재는 값, 수면처럼 상태로 나누는 값, 운동 한 번의 시간·거리·소모 열량이 따로따로 쌓이고, 각 기록에는 어느 기기와 어느 소프트웨어 빌드에서 나왔는지가 함께 붙습니다[1]. 워치에서 잰 기록도 폰의 건강 데이터베이스로 동기화되어 들어옵니다[3].

사용자가 따로 입력하지 않아도 폰을 들고 다니거나 워치를 차기만 하면 기록이 생긴다는 점에서 조사에 쓸모가 있습니다. 특정 시각에 걸음이 있었는지, 심박이 올라갔는지, 잠들어 있었는지, 워치를 차고 있었는지를 다른 사용 기록과 맞춰 볼 수 있습니다.

건강 앱에는 이 밖에 의료 정보(Medical ID)와 병원에서 받은 건강 기록(임상 기록)도 들어갑니다. 임상 기록에는 어느 앱이 저장했는지를 알려 주는 메타데이터가 붙고, 선택 항목으로 붙는 서명된 사본은 CMS(RFC 5652) 형식입니다[3].

## 위치와 버전별 차이

### 파일

공개 도구 iLEAPP 는 아래 두 파일 이름 패턴으로 건강 데이터베이스를 찾습니다[1]. iLEAPP 는 경로의 끝부분만 맞춰 보기 때문에, 이 페이지에서도 전체 경로는 적지 않습니다.

| 파일 이름 패턴 | iLEAPP 가 읽는 표 |
|---|---|
| `*Health/healthdb_secure.sqlite*` | 주 연결로 열어 `samples`·`objects`·`data_provenances`·운동 표 등을 읽음 |
| `*Health/healthdb.sqlite*` | `healthdb` 라는 이름으로 붙여(ATTACH) `source_devices`·`sources` 를 읽음 |

iLEAPP 는 `healthdb_secure.sqlite` 를 먼저 열고 `healthdb.sqlite` 를 붙여서 조회하므로, 측정 기록은 앞 파일에, 기기·출처 정보는 뒤 파일에 있다고 보고 짠 셈입니다[1]. 이 나눔이 iOS 버전마다 같은지는 확인하지 못했으므로, 실제 검체에서는 두 파일을 모두 열어 표 목록부터 확인합니다.

### 백업에 들어가는 조건

건강 데이터는 Finder(macOS 10.15 이후) 또는 iTunes 로 만든 **암호화한** 로컬 백업에만 들어갑니다[2][3]. 백업을 암호화하지 않으면 건강 데이터가 빠지고, 이 점은 획득 방식을 고를 때부터 따져야 합니다. 로컬 백업의 구조는 [로컬 백업](../../01-foundations/backups/local-backup/index.md)에서 다룹니다.

암호화하지 않은 백업을 실제로 열어 보면 `HealthDomain` 도메인이 있고 항목은 2개였지만, 어떤 파일인지는 기록하지 않았습니다. 같은 백업의 Apple 데이터베이스 파일 목록에는 `healthdb*.sqlite` 가 없었습니다(확인 범위: iOS 27.0). 암호화하지 않은 백업이라 빠진 것으로 보이며, 이 판단은 위 두 공식 문서를 근거로 한 추론입니다. 따라서 건강 데이터베이스가 백업에 없다는 사실만으로 기기에 건강 기록이 없었다고 읽으면 안 됩니다.

같은 백업에는 건강 앱과 관련된 앱 도메인도 있었습니다(확인 범위: iOS 27.0).

| 도메인 |
|---|
| `AppDomain-com.apple.Health` |
| `AppDomain-com.apple.Health.Sleep` |
| `AppDomainGroup-group.com.apple.Health` |
| `AppDomain-com.apple.HealthPrivacyService` |

도메인 이름을 읽는 법은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md)을 봅니다.

### 버전별 차이

| iOS 버전 | 달라지는 점 |
|---|---|
| iOS 12 이후 | 이중 인증을 켠 계정이면 건강 데이터의 iCloud 동기화에 종단간 암호화를 씁니다[3]. |
| iOS 14 이후 | 의료 정보를 CloudKit 으로 동기화합니다[3]. |
| iOS 15 이후 | iLEAPP 가 `quantity_sample_series`·`quantity_series_data` 표에서 심박수의 개별 측정 시각까지 읽습니다[1]. |

## 구조

### 주요 표와 칸

아래 표는 iLEAPP 가 조회하는 표와 칸을 옮긴 것입니다[1]. 표 전체를 나열한 목록이 아니므로, 검체에서는 `sqlite_master` 로 표 목록을 먼저 뽑아 비교합니다.

| 표 | 칸 | 담는 내용 |
|---|---|---|
| `samples` | `start_date`, `end_date`, `data_id`, `data_type` | 기록 하나의 시작·끝 시각과 종류 |
| `quantity_samples` | `data_id`, `quantity` | 숫자로 재는 값(걸음 수, 몸무게 등) |
| `category_samples` | `data_id`, `value` | 상태로 나누는 값(수면 등) |
| `quantity_sample_series` | `data_id`, `hfd_key`, `count`, `series_identifier` | 여러 번 잰 값을 묶은 연속 측정 |
| `quantity_series_data` | `series_identifier`, `timestamp`, `value` | 연속 측정의 값 하나하나 |
| `workouts` | `data_id`, `activity_type`, `location_type`, `duration`, `total_distance`, `goal_type`, `goal`, `total_energy_burned`, `total_basal_energy_burned` | 운동 한 번의 요약 |
| `workout_activities` | `ROWID`, `owner_id`, `start_date`, `end_date`, `activity_type`, `location_type`, `duration` | 운동 안의 세부 활동 |
| `workout_statistics` | `workout_activity_id`, `data_type`, `quantity` | 세부 활동별 통계 |
| `metadata_values` / `metadata_keys` | `object_id`, `key_id`, `numerical_value`, `string_value` / `ROWID`, `key` | 기록에 붙은 추가 정보 |
| `objects` | `data_id`, `type`, `creation_date`, `provenance` | 기록이 만들어진 시각과 출처 번호 |
| `data_provenances` | `ROWID`, `origin_product_type`, `origin_build`, `local_product_type`, `local_build`, `source_id`, `device_id`, `tz_name` | 기록을 만든 기기 종류·빌드·시간대 |
| `source_devices` | `ROWID`, `name`, `manufacturer`, `model`, `hardware`, `firmware`, `software`, `localIdentifier`, `sync_provenance`, `sync_identity` | 기록한 기기의 이름·모델·펌웨어 |
| `sources` | `ROWID`, `name`, `product_type`, `source_options` | 기록을 보낸 앱이나 기기 |
| `ACHAchievementsPlugin_earned_instances` | `created_date`, `earned_date`, `template_unique_name`, `value_in_canonical_unit`, `value_canonical_unit`, `creator_device` | 활동 배지 획득 기록 |

측정 기록을 기기와 연결할 때는 `objects.provenance` 에서 `data_provenances` 로, 다시 `source_devices` 로 따라갑니다. iLEAPP 는 `samples.data_id = objects.data_id`, `objects.provenance = data_provenances.ROWID`, `data_provenances.device_id = source_devices.ROWID`, `data_provenances.source_id = sources.ROWID` 로 표를 잇습니다[1]. 이렇게 하면 기록마다 기기 이름·모델·펌웨어가 나오고, 폰에서 잰 값인지 워치에서 잰 값인지를 가를 근거가 됩니다.

### 기록 종류 번호

`samples.data_type` 은 기록 종류를 번호로 적습니다. iLEAPP 가 쓰는 번호는 아래와 같고[1], 이 번호가 iOS 버전마다 같은지는 확인하지 못했습니다.

| 번호 | 종류 |
|---|---|
| 2 | 키 |
| 3 | 몸무게 |
| 5 | 심박수 |
| 7 | 걸음 수 |
| 63 | 수면 |
| 70 | 워치 착용 (Watch Worn) |
| 118 | 안정 시 심박수 |
| 173 | 헤드폰 음량 |
| 256 | 손목 온도 |

수면 기록의 `category_samples.value` 가 어떤 값일 때 깨어 있음이고 어떤 값일 때 렘수면인지는 이번 자료로 확인하지 못했습니다.

### 설정 파일

건강 데이터베이스와 따로, 백업의 `HomeDomain` 안 `Library/Preferences/` 에 건강 관련 설정 파일이 있었습니다(확인 범위: iOS 27.0). 키 이름만 확인했고 값과 의미는 읽지 않았습니다. 설정 파일 형식은 [속성 목록 파일](../../01-foundations/data-formats/plist.md)에서 다룹니다.

| 파일 | 확인한 키 |
|---|---|
| `com.apple.health.shared.plist` | `HealthExperience.healthKitDatabaseIdentifierKey`, `HealthExperience.PreviousOSVersion`, `HealthExperience.PreviousOSBuild`, `HealthExperience.CurrentOSVersionMajorUpdateDate`, `HealthExperience.CurrentOSVersionMinorUpdateDate`, `HealthExperience.CurrentOSBuildUpdateDate`(날짜), `HealthSharingPreferences_<UUID>_Notifications_alerts`·`_updates`·`_significantChanges`, `PredictiveGenerationLastRun`, `MinimumCompatibleSleepScoreAlgorithmVersion`, `MaximumCompatibleSleepScoreAlgorithmVersion` |
| `com.apple.healthd.plist` | `ShowMedicalIdOnWatch`(참·거짓), `HDPeriodicCountryMonitor_LastCheckAttemptDate`, `HDDatabasePruningLastAttemptDateKey`(날짜), `HKHRAFibBurdenSevenDayAnalysisStartingMinute`, 이름이 가려진 날짜 키 여러 개 |
| `com.apple.healthappd.plist` | `datesOfLastBackgroundGenerationSuccess`, `numberOfAttemptsSinceLastGenerationSuccess` |
| `com.apple.healthrecordsd.plist` | `ClinicalSharingAdHocSyncState` |
| `com.apple.private.health.heart-rhythm.plist` | `HKElectrocardiogramOnboardingCompleted` |
| `com.apple.private.health.feature-availability.plist` | `ExpireElectrocardiogramRecording`, `ExpireBackgroundAtrialFibrillationDetection`, `ExpireAFibBurden`, `ExpireHypertensionNotifications`, `DisableOxygenSaturationRecording`, `DisableSleepApneaNotifications`(각각 `ruleIdentifier`, `userInfo` 를 담은 사전) |

이 밖에 `com.apple.private.health.age-gating.plist`, `com.apple.private.health.bloodPressureJournal.plist`(`BloodPressureJournalTimeZoneName`), `com.apple.private.health.menstrual-cycles.plist`, `com.apple.private.health.mental-health.plist` 와 심전도·고혈압 알림·수면 무호흡 알림·손목 온도·산소포화도 등의 `com.apple.private.health.feature-properties.*.companion.plist` 파일도 있었습니다.

`PreviousOSVersion` 과 업데이트 날짜 키는 OS 업데이트 이력을 짚는 단서가 될 수 있고, `HKElectrocardiogramOnboardingCompleted` 같은 키는 사용자가 해당 건강 기능을 켰는지 판단하는 데 쓸 수 있습니다. 두 가지 모두 키 이름에서 끌어낸 추론이라, 값을 읽고 다른 기록과 맞춰 본 뒤에 씁니다.

## 증거로서 의미

**증명하는 것**

- 특정 시각 범위에 걸음 수·심박수·수면 같은 기록이 이 데이터베이스에 저장되어 있다는 사실
- 기록마다 출처로 적힌 기기 이름·모델·펌웨어와 기록 당시 시간대 이름(`data_provenances.tz_name`)[1]
- 운동 기록의 시작·끝 시각, 운동 종류, 시간, 거리, 소모 열량[1]

**증명하지 못하는 것**

- 기록을 만든 사람이 기기 주인이라는 사실. 워치나 폰을 다른 사람이 들고 있었어도 기록은 똑같이 쌓입니다.
- 측정값이 실제 몸 상태와 맞는다는 사실. 센서가 잰 값이고, 다른 앱이 써 넣은 값도 섞입니다.
- 데이터베이스에 없는 시간대에 기기를 쓰지 않았다는 사실. 건강 기록이 빠진 이유는 여러 가지이고, 아래 함정 절에서 다룹니다.

보고서에는 "피의자가 그 시각에 걸었다" 가 아니라 "이 시각 범위에 이 모델의 기기가 걸음 수 기록을 남겼다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

`samples.start_date`·`end_date`, 운동 시각, `objects.creation_date` 는 Mac 절대 시각, 곧 2001-01-01 00:00:00 UTC 부터 센 초로 저장되어 있고 iLEAPP 도 이 기준으로 바꿉니다[1]. 값 자체는 UTC 기준이라서, 사람이 읽는 현지 시각으로 옮길 때는 `data_provenances.tz_name` 에 적힌 기록 당시 시간대를 함께 봅니다. 여행이나 시간대 변경이 있으면 기록마다 시간대 이름이 다를 수 있습니다. 시각 값을 바꾸는 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md)에, 기기 시간대 설정은 [시간대와 시각 설정](../system-account/time-zone.md)에 있습니다.

`start_date` 와 `end_date` 는 측정한 구간이고, `creation_date` 는 데이터베이스에 기록이 만들어진 시각입니다. 워치에서 잰 값이 나중에 폰으로 넘어오면 두 시각이 벌어질 수 있으므로, 행위가 일어난 시각을 말할 때는 측정 구간을 씁니다. 이 벌어짐은 동기화 방식에서 끌어낸 추론이라 검체에서 직접 확인합니다.

`quantity_series_data.timestamp` 도 iLEAPP 는 같은 함수(`convert_cocoa_core_data_ts_to_utc`)로 Mac 절대 시각에서 바꿉니다[1]. 검체에서는 바꾼 값이 같은 기록의 `samples.start_date`~`end_date` 구간 안에 들어가는지 한 번 맞춰 봅니다.

## 함정과 한계

**암호화하지 않은 백업에는 없습니다.** 앞에서 본 것처럼 건강 데이터는 암호화한 로컬 백업에만 들어갑니다[2][3]. 획득 보고서에는 백업 암호화 여부를 반드시 적습니다.

**잠긴 기기에서는 접근이 끊깁니다.** 건강 데이터의 데이터 보호 등급은 "Protected Unless Open" 이라서 기기를 잠그고 10분이 지나면 접근이 끊기고, 권한 같은 관리 데이터는 "Protected Until First User Authentication" 등급입니다[3]. 등급별 의미는 [데이터 보호](../../01-foundations/storage/data-protection/index.md)에서 다룹니다.

**아직 합쳐지지 않은 기록이 있을 수 있습니다.** 잠긴 상태에서 생긴 기록은 "Protected Unless Open" 등급의 임시 저널 파일에 두었다가 본 데이터베이스에 합친 뒤 지웁니다[3]. 그래서 획득 시점에 따라 본 데이터베이스에 아직 들어가지 않은 기록이 저널에 남아 있을 수 있고, 이 부분은 공식 문서의 동작 설명에서 끌어낸 추론입니다.

**다른 기기의 기록이 섞입니다.** iCloud 동기화를 켜면 같은 계정의 다른 기기에서 온 기록이 함께 들어올 수 있습니다. 이 역시 동기화 설명[3]에서 끌어낸 추론이라서, 기록마다 출처 기기를 확인한 뒤에 폰 주인의 행위로 묶습니다.

**번호의 뜻은 버전마다 확인합니다.** `data_type` 번호와 수면 값의 뜻은 iLEAPP 기준이고, iOS 버전마다 같은지는 확인하지 못했습니다. 새 버전 검체에서는 알려진 기록(예: 조사관이 직접 입력한 몸무게)으로 번호를 한 번 맞춰 봅니다.

**지우기·조작.** `com.apple.healthd.plist` 에 `HDDatabasePruningLastAttemptDateKey` 라는 날짜 키가 있었지만(확인 범위: iOS 27.0), 이 키가 무엇을 지운 시각인지는 확인하지 못했습니다. 사용자가 건강 기록을 지웠을 때 데이터베이스에 어떤 흔적이 남는지도 이번 자료로는 확인하지 못했고, SQLite 에서 지운 행을 찾는 일반 방법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)와 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)를 봅니다.

## 직접 분석해 보기

### 시각 값 한 번 손으로 바꾸기

아래는 명세로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다. `samples.start_date` 에 `700000000` 이 들어 있다고 하면 2001-01-01 00:00:00 UTC 에 700,000,000초를 더해 2023-03-08 20:26:40 UTC 가 나옵니다. 유닉스 시각으로 옮기려면 두 기준 사이의 차이인 978,307,200초를 더해 `1678307200` 을 얻고, 한국 시간(UTC+9)으로는 2023-03-09 05:26:40 입니다.

```
Mac 절대 시각   700000000
+ 978307200   = 1678307200 (유닉스 시각)
→ 2023-03-08 20:26:40 UTC
→ 2023-03-09 05:26:40 KST
```

### SQL 로 기록과 기기 묶어 보기

iLEAPP 의 조인식을 따라 짠 예시 쿼리입니다[1]. `healthdb_secure.sqlite` 를 열고 `healthdb.sqlite` 를 붙인 상태에서 돌리며, 검체에서 결과가 비거나 어긋나면 `objects.provenance` 와 `data_provenances.ROWID` 의 값을 먼저 눈으로 비교합니다.

```sql
ATTACH DATABASE 'healthdb.sqlite' AS healthdb;

SELECT datetime(s.start_date + 978307200, 'unixepoch') AS start_utc,
       datetime(s.end_date   + 978307200, 'unixepoch') AS end_utc,
       s.data_type, q.quantity,
       p.tz_name, d.name, d.model, d.firmware
FROM samples s
LEFT JOIN quantity_samples q ON q.data_id = s.data_id
LEFT JOIN objects o          ON o.data_id = s.data_id
LEFT JOIN data_provenances p ON p.ROWID   = o.provenance
LEFT JOIN healthdb.source_devices d ON d.ROWID = p.device_id
WHERE s.data_type = 7            -- 걸음 수 (iLEAPP 기준)
ORDER BY s.start_date;
```

### 공개 도구

iLEAPP 의 건강 모듈은 위 두 파일 패턴을 찾아 걸음 수·심박수·수면·운동·배지 등을 표로 뽑고, 시각은 Mac 절대 시각에서 UTC 로 바꿔 보여 줍니다[1]. 도구 결과는 위 SQL 결과와 몇 행을 골라 맞춰 보고, 어긋나면 원본 표를 기준으로 삼습니다. 도구 검증 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md)에 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 내용 |
|---|---|
| [애플 워치 연결](apple-watch.md) | 워치에서 온 기록인지, 워치가 짝지어져 있었는지 |
| [KnowledgeC](../app-usage/knowledgec/index.md)·[바이옴](../app-usage/biome/index.md) | 같은 시각에 화면을 켜고 앱을 썼는지 |
| [전원 로그](../app-usage/powerlog.md) | 같은 시각에 기기가 켜져 있었는지 |
| [중요 위치](../location/significant-locations.md) | 운동·걸음 기록과 이동 기록이 맞는지 |
| [시간대와 시각 설정](../system-account/time-zone.md) | `tz_name` 과 기기 시간대 설정이 맞는지 |

여러 기록을 한 줄로 놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md)을, 기록한 사람이 누구인지 따지는 흐름은 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)를 봅니다.

## 실습

공개 검체(NIST CFReDS 등)에서 아이폰 이미지를 구해 아래 질문을 풀어 봅니다. 검체에 따라 건강 데이터베이스가 없을 수 있고, 그럴 때는 첫 질문의 답을 기록하는 것으로 충분합니다.

1. 검체가 전체 파일 시스템 이미지인지, 암호화한 백업인지, 암호화하지 않은 백업인지 확인하고, 그에 따라 건강 데이터베이스가 있어야 하는지를 먼저 판단합니다.
2. `healthdb.sqlite` 와 `healthdb_secure.sqlite` 의 표 목록을 비교하고, 측정 기록과 기기 정보가 iLEAPP 의 나눔대로 들어 있는지 적습니다.
3. 걸음 수 기록 하나를 골라 `source_devices` 까지 따라가 기기 이름과 모델을 확인합니다.
4. `data_provenances.tz_name` 에 시간대가 몇 가지 나오는지 세고, 시간대가 바뀐 시점을 찾습니다.
5. iLEAPP 결과의 한 행을 골라 SQL 로 구한 시각과 같은지 확인합니다.

## 참고 문헌

1. iLEAPP, `scripts/artifacts/health.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/health.py
2. Apple Support, "About encrypted backups on your iPhone, iPad, or iPod touch" — https://support.apple.com/en-us/108353
3. Apple Platform Security, "Protecting access to user's health data" — https://support.apple.com/guide/security/protecting-access-to-users-health-data-sec88be9900f/web
