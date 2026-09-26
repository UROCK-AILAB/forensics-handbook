---
title: "기기 식별자"
parent: "기반 · 값 읽는 법"
nav_order: 260
---

# 기기 식별자 (Android ID·IMEI·광고 ID)

Android 기기와 앱에는 Android ID, IMEI 와 일련번호, MAC 주소, 광고 ID, 앱이 스스로 만든 ID 처럼 성격이 다른 식별자가 여럿 남고, 식별자마다 누가 언제 바꿀 수 있는지가 달라서 그 규칙을 알아야 두 기록을 같은 기기나 같은 사용자로 이어도 되는지 판단할 수 있습니다.

## 이 형식을 쓰는 아티팩트

| 식별자 | 바뀌는 때 | 앱이 읽을 수 있나 | 자세히 |
|---|---|---|---|
| Android ID(SSAID) | 앱 서명 키·사용자·기기 조합마다 하나 (Android 8.0 이후) | 읽을 수 있음, 앱마다 값이 다를 수 있음 | 아래 "Android ID" |
| IMEI·하드웨어 일련번호 | 재설정할 수 없음 | Android 10 부터 특권 앱만 | 아래 "IMEI 와 일련번호" |
| MAC 주소 | 무작위화 설정에 따라 달라짐 | Android 6 부터 시스템 앱만 | [와이파이 설정과 접속 기록](../../02-artifacts/network/wifi.md) |
| 광고 ID | 사용자가 재설정할 수 있음 | 읽을 수 있음, 끄면 0 으로 채운 값 | 아래 "광고 ID" |
| 앱 자체 ID(Firebase installation ID, 앱이 만든 UUID) | 앱이 정함 | 그 앱만 | [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md) |
| 블루투스 주소·기기 이름 | 설정과 하드웨어에 따름 | 설정·dumpsys 에서 보임 | [블루투스 장치](../../02-artifacts/network/bluetooth.md) |
| 빌드 지문(build fingerprint) | 시스템 업데이트 때 | dumpsys package 에서 보임 | [기기 정보와 빌드](../../02-artifacts/system-account/device-build.md) |

이 페이지는 식별자의 규칙과 읽는 법만 다루고, 각 식별자가 남는 파일은 링크한 아티팩트 페이지에서 다룹니다.

## 구조

### Android ID

Android 8.0(API 26)부터 앱이 보는 `ANDROID_ID` 는 앱 서명 키와 사용자 단위로 나뉩니다. 앱 서명 키, 사용자, 기기의 조합마다 값이 하나라서, 같은 기기의 같은 사용자라도 서명 키가 다른 앱은 서로 다른 Android ID 를 봅니다[1]. 서명 키가 같으면 앱을 지웠다가 다시 깔아도 값이 바뀌지 않고, 시스템 업데이트로 패키지 서명 키가 바뀌어도 값은 그대로입니다[1].

8.0 으로 OTA 업데이트하기 전에 설치한 앱은 예외입니다. 이런 앱은 OTA 뒤에도 예전 값을 계속 쓰지만, OTA 뒤에 지웠다가 다시 설치하면 값이 바뀝니다[1]. 같은 8.0 변경에서 `Build.SERIAL` 은 사용이 중단됐고, 하드웨어 일련번호는 `READ_PHONE_STATE` 권한이 있어야 `Build.getSerial()` 로 읽을 수 있게 됐습니다. `net.hostname` 시스템 속성을 조회해도 null 이 돌아옵니다[1].

| Android 버전 | Android ID 동작 |
|---|---|
| 8.0 이전에 설치하고 8.0 으로 OTA 한 앱 | 예전 값을 그대로 씀, OTA 뒤 삭제·재설치하면 바뀜 |
| 8.0 이후 | 앱 서명 키·사용자·기기 조합마다 값이 하나 |
| 8.0 이후 같은 서명 키로 재설치 | 바뀌지 않음 |
| 8.0 이후 시스템 업데이트로 서명 키 변경 | 바뀌지 않음 |

settings secure 에는 `android_id` 키가 있습니다. 이 키의 값과 앱마다 나뉜 Android ID 의 관계, 앱별 Android ID 를 저장하는 파일의 이름과 경로, 값의 길이와 표기 방식은 실제 기기에서 확인해야 합니다.

### IMEI 와 일련번호

Android 10(API 29)부터 IMEI 와 일련번호는 "재설정할 수 없는 식별자" 로 묶여 읽기가 제한됩니다. 기기 소유자 앱이나 프로필 소유자 앱, 통신사 특권이 있는 앱, 또는 `READ_PRIVILEGED_PHONE_STATE` 권한이 있는 앱만 읽을 수 있습니다[2]. 기기 이미지 안에서 IMEI 가 남는 파일이나 데이터베이스는 실제 기기에서 확인해야 합니다.

### MAC 주소

Android 6 부터 MAC 주소는 시스템 앱만 읽을 수 있고, 서드파티 앱은 읽지 못합니다[2]. Android 11 이상을 대상으로 하는 앱에서는 Passpoint 망의 MAC 무작위화가 Passpoint 프로필 단위로 이뤄집니다[2]. settings global 에는 `non_persistent_mac_randomization_force_enabled` 키가 있고, 이 키의 값과 뜻은 실제 기기에서 확인합니다. 무작위화된 주소가 접속 기록에 어떻게 남는지는 [와이파이 설정과 접속 기록](../../02-artifacts/network/wifi.md)에서 다룹니다.

### 광고 ID

광고 ID 는 사용자가 재설정할 수 있는 식별자입니다. 2021년 말 Google Play 서비스 업데이트부터는 사용자가 Android 설정에서 광고 ID 맞춤설정을 끄면 ID 가 제거되고, 앱이 조회하면 0 으로 채운 문자열을 받습니다[2]. 앱은 광고 ID 를 SSAID·MAC·IMEI 같은 영구 식별자와 연결하지 않고, 사용자 동의 없이 재설정 전후의 광고 ID 를 이어 붙이지 않도록 되어 있습니다[2]. 광고 ID 가 기기 어디에 저장되는지는 실제 기기에서 확인해야 합니다.

### 앱이 스스로 만든 ID

앱이 자기 식별자가 필요할 때는 Firebase installation ID(FID)나 `UUID.randomUUID` 로 만든 GUID 를 쓰고, GUID 는 앱 내부 저장소에 두는 것이 권장 방식입니다[2]. 그래서 앱 데이터 폴더 안에서 그 앱만 쓰는 UUID 가 나올 수 있습니다. 앱 데이터 폴더의 구조는 [앱 데이터 폴더 구조](../storage/app-data-layout.md)에 있습니다.

## 읽는 법

adb 일반 권한으로 읽으면 식별자와 관련된 필드는 아래처럼 보입니다. 이 출력에는 IMEI 와 광고 ID 의 필드가 나오지 않습니다.

| 출력 | 필드·키 | 알려 주는 것 |
|---|---|---|
| settings secure | `android_id` | Android ID 계열 값 |
| settings secure | `bluetooth_address`, `bluetooth_name`, `bluetooth_addr_valid` | 블루투스 주소와 이름 |
| settings global | `device_name`, `default_device_name` | 사용자가 정한 기기 이름과 기본 이름 |
| settings global | `synced_account_name` | 동기화 계정 이름 |
| dumpsys bluetooth_manager "Bluetooth Status" | `address:`, `name:` | 블루투스 주소와 이름 |
| dumpsys package "Database versions" | `buildFingerprint=`, `fingerprint=` | 빌드 지문 |
| dumpsys account | `Account {name=…, type=…}` | 계정 이름과 종류 |

1. 기록에 남은 식별자가 어떤 종류인지 먼저 정합니다. 16진 문자열이라도 Android ID 인지, 광고 ID 인지, 앱이 만든 UUID 인지에 따라 비교 방법이 달라집니다.
2. 기기 쪽 값과 대조합니다. 블루투스 주소처럼 settings 와 dumpsys 두 곳에 나오는 값은 두 곳을 모두 보고 같은지 확인합니다.
3. Android ID 를 대조할 때는 어느 앱이 본 값인지 함께 적습니다. 8.0 이후에는 서명 키가 다른 앱끼리 값이 다르기 때문에, 앱 A 의 기록과 앱 B 의 기록에서 Android ID 가 다르다는 사실만으로 다른 기기라고 보지 않습니다.
4. 광고 ID 가 0 으로만 채워져 있다면 사용자가 광고 ID 맞춤설정을 끈 상태에서 조회했을 가능성을 먼저 생각합니다[2].
5. 계정 이름과 기기 이름은 사용자가 바꿀 수 있는 값이라 보조 단서로만 씁니다. 계정 기록은 [계정](../../02-artifacts/system-account/accounts/index.md)에서 다룹니다.

## 포렌식에서 중요한 점

식별자는 서로 다른 기록을 한 기기나 한 사용자로 묶는 데 쓰이지만, 식별자마다 바뀌는 조건이 달라서 묶어도 되는 범위가 다릅니다. 재설정할 수 없는 IMEI 와 하드웨어 일련번호는 기기를 가리키는 데 쓸 수 있지만 Android 10 이후 일반 앱은 읽지 못하기 때문에[2], 앱 데이터에서 이 값이 나오지 않는다고 이상한 일은 아닙니다. Android ID 는 같은 서명 키의 앱 안에서 재설치를 넘어 이어지고[1], 광고 ID 는 사용자가 언제든 재설정할 수 있어서[2] 오래전 기록과 최근 기록의 값이 다르더라도 다른 기기라는 뜻은 아닙니다.

공장 초기화 때 Android ID 가 바뀌는지는 공식 문서에 적혀 있지 않습니다. 초기화 전후 기록을 식별자로 이을 때는 이 점을 보고서에 밝히고, 초기화 흔적 자체는 [초기화 흔적](../../02-artifacts/system-account/factory-reset.md)에서 따로 확인합니다.

보고서에는 "같은 기기다" 대신 "앱 A 의 기록과 앱 B 의 기록에 같은 블루투스 주소가 남아 있다" 처럼 기록으로 확인되는 만큼만 씁니다. 기기를 쓴 사람을 가려내는 흐름은 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)에 있습니다.

## 함정

다중 사용자와 프로필이 있는 기기에서는 Android ID 가 사용자 단위로도 나뉩니다[1]. 같은 앱이라도 주 사용자와 다른 프로필에서 본 값이 다를 수 있어서, 값을 비교하기 전에 어느 사용자의 기록인지 확인합니다. 사용자 번호를 읽는 방법은 [패키지 이름과 UID](package-uid.md)에 있습니다.

8.0 이전에 설치하고 OTA 로 올라온 앱은 예전 규칙의 값을 계속 쓸 수 있습니다[1]. 오래 쓴 기기라면 앱마다 규칙이 달랐을 수 있으니 설치 시점을 [설치된 앱](../../02-artifacts/app-usage/packages/index.md)에서 함께 봅니다.

MAC 주소가 무작위화돼 있으면 접속 기록의 주소가 하드웨어 주소와 다를 수 있습니다. 네트워크 장비 쪽 기록과 대조할 때 무작위화 여부를 먼저 확인합니다.

광고 ID 가 재설정되면 앞뒤 값이 달라지고, 앱도 사용자 동의 없이 두 값을 잇지 않도록 되어 있습니다[2]. 그래서 광고 ID 하나로 긴 기간의 활동을 한 사람에게 묶지 않습니다.

## 도구

- `adb shell settings list secure`, `settings list global`: 실행 중인 기기에서 식별자와 관련된 키를 봅니다. 값은 수집 시점의 상태입니다.
- `adb shell dumpsys bluetooth_manager`, `dumpsys package`, `dumpsys account`: 블루투스 주소, 빌드 지문, 계정 목록을 봅니다. 출력의 모양은 [dumpsys 출력](../../02-artifacts/logs/dumpsys.md)에서 다룹니다.
- 설정 값이 파일로 남은 경우에는 [설정 XML과 SharedPreferences](../data-formats/shared-preferences.md)나 [안드로이드 바이너리 XML](../data-formats/abx.md)에 나온 방법으로 읽습니다.

식별자는 개인 정보라서 보고서와 작업 기록에 옮길 때 필요한 범위만 남기고, 수집 기록을 다루는 방법은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md)를 따릅니다.

## 참고 문헌

1. Android Developers — Android 8.0 Behavior Changes (Privacy) — https://developer.android.com/about/versions/oreo/android-8.0-changes
2. Android Developers — Best practices for unique identifiers — https://developer.android.com/identity/user-data-ids
