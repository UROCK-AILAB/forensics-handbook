---
title: "설정 값"
parent: "아티팩트 · 시스템·계정"
nav_order: 370
---

# 설정 값 (Settings Global·Secure·System)

Android 시스템 설정이 어떤 표로 나뉘어 어느 파일에 저장되고, 조사에서 어떤 키를 먼저 보는지를 정리합니다. 값은 현행 AOSP 기준(frameworks/base 의 main 가지)입니다.

시스템 설정은 SettingsProvider 가 system·secure·global·ssaid·config 다섯 표로 관리해 사용자별 시스템 폴더의 XML 파일에 저장하고 [1], 개발자 옵션·adb·기기 준비 상태·위치 설정처럼 사건 당시의 기기 상태를 알 수 있는 값이 여기에 모입니다.

## 무엇을 기록하나 · 왜 생기나

설정 앱에서 바꾸는 값과 시스템 서비스가 스스로 기억해 두는 값은 대부분 SettingsProvider 가 모아 관리합니다. 다섯 표의 역할은 다음과 같습니다 [1].

| 표 | 저장 범위 | 내용 |
|---|---|---|
| global | 기기 전체, 기기 소유자(사용자 0) 아래에 저장 | 비행기 모드·adb 같은 기기 공통 값 |
| secure | 사용자별 | 위치·입력기·잠금 같은 사용자별 값 |
| system | 사용자별 | 화면 꺼짐 시간 같은 사용자 환경 값 |
| ssaid | 사용자별 | 앱별 Android ID. 호출한 앱의 UID 문자열이 키 |
| config | `settings_config.xml` 이 어느 사용자 폴더에 있는지로 확인 | 아래 구조 절의 namespace 태그가 이 표에 쓰임 |

global 설정은 기기 소유자 아래에 저장하고 나머지 설정은 사용자별 시스템 폴더에 저장합니다. global 표는 사용자 0(USER_SYSTEM) 쪽으로만 읽고 쓰기 때문에 global 은 사용자 0 쪽에만 있고 나머지는 사용자 번호 폴더마다 따로 있습니다 [1]. "내용" 열의 예시는 아래 "조사에 쓸 만한 키" 절의 키 이름입니다.

앱별 Android ID(SSAID)는 ssaid 표에 호출한 앱의 UID 문자열을 키로 저장합니다 [1]. 식별자로서의 해석은 [기기 식별자 (Android ID·IMEI·광고 ID)](../../01-foundations/value-decoding/device-identifiers.md) 페이지에 있습니다.

## 위치와 버전별 차이

설정 파일은 사용자별 시스템 폴더(`/data/system/users/<사용자 번호>/`)에 표마다 하나씩 있고, 이름은 `settings_global.xml`, `settings_system.xml`, `settings_secure.xml`, `settings_ssaid.xml`, `settings_config.xml` 입니다 [1]. global 은 사용자 0 폴더에만 생깁니다. ALEAPP 의 settingsSecure 모듈도 같은 규칙으로 `*/system/users/*/settings_secure.xml` 을 읽습니다 [3].

| 항목 | 내용 | 출처·범위 |
|---|---|---|
| 옛 저장 방식 | SQLite 데이터베이스였다가 XML 로 옮김. 소스에 migrateAllLegacySettingsIfNeededLocked(), DROP_DATABASE_ON_MIGRATION = true 가 있음 | [1] |
| 옛 DB 파일 이름과 옮긴 버전 | 옛 버전 기기 이미지의 사용자 시스템 폴더에서 SQLite 파일을 찾아 확인 | |
| 파일 형식 | 글자 XML 또는 ABX. Xml.resolveSerializer 가 기기 설정에 따라 형식을 고르고, ALEAPP 도 ABX 를 따로 읽음 | [2][3] |
| ABX 가 기본이 된 버전 | 버전으로 판단하지 않고 파일 맨 앞 바이트로 글자 XML 인지 ABX 인지 확인 | |
| 뿌리 태그가 없는 파일 | ALEAPP 가 Android 11 파일에서 따로 처리 | [3] |
| 키 개수 | 기기마다 다름(예: global 596개, secure 464개, system 582개) | |

삼성 기기에는 AOSP 소문자 키 사이에 대문자로 쓴 키, `SEM_` 으로 시작하는 키, 삼성 기능 이름이 들어간 키가 섞여 있습니다. 예를 들어 global 에 `Phenotype_boot_count`, `Phenotype_flags`, `SPEN_INPUT_MODE_DEX`, `STANDARD_BOLD_FONT`, secure 에 `IS_SMARTSWITCH_DATA_PRESENT`, `IS_SMARTSWITCH_RESTORE_IN_PROGRESS`, `SUPPORT_BG_AD_RESTRICTION_BY_AI`, `rampart_blocked_adb_cmd`, `rampart_blocked_unknown_apps`, system 에 `IsFotaUpgrade`, `PowerbuttonTapping`, `SEM_VIBRATION_NOTIFICATION_INTENSITY` 가 있습니다. 이런 제조사 키는 뜻을 단정할 수 없어서 이름만 보고 해석하지 않습니다.

## 구조

XML 뿌리 태그는 `settings` 이고 설정 하나가 `setting` 태그 하나입니다. 속성은 다음과 같습니다(현행 AOSP 기준) [2].

| 속성 | 담긴 것 |
|---|---|
| `id` | 항목 번호 |
| `name`, `value` | 키와 값 |
| `package` | 값과 함께 적는 패키지 이름 |
| `defaultValue`, `defaultSysSet` | 기본값과 관련된 값 |
| `tag` | 태그 |
| `version` | 버전 |
| `preserve_in_restore` | 복원할 때 값을 보존할지 |
| `valueBase64`, `defaultValueBase64`, `tagBase64` | 값을 이진으로 적을 때의 Base64 판 |

config 쪽에는 `namespaceHashes`·`namespaceHash`(namespace, bannedHash) 태그도 있습니다 [2]. `package` 속성은 그 값을 마지막으로 쓴 패키지로 흔히 읽지만, 이 뜻으로 단정하지는 않습니다.

파일은 AtomicFile 로 쓰고, 백업 파일은 이름 끝에 `.fallback` 을 붙입니다. 원본 파일이 깨지면 서비스가 fallback 파일을 다시 읽고 복사해서 원본을 되살립니다 [2]. 앱 패키지 하나가 쓸 수 있는 설정 크기에는 한도(MAX_BYTES_PER_APP_PACKAGE_LIMITED = 40000)가 있고 `android` 패키지는 예외입니다 [2].

최근 변경 20건(UPDATE·DELETE·PERSIST·INITIALIZE·RESET 과 시각·이름)을 기억하는 mHistoricalOperations 는 디버그 빌드에서만 메모리에 남고 dump 로 나옵니다 [2]. 일반 판매 기기에서는 이 기록이 없다고 보고 찾지 않습니다.

## 조사에 쓸 만한 키

다음 키들은 실제 기기의 settings 목록에 나오는 키입니다. 아래 "볼 거리" 는 키 이름에서 짐작한 방향이고, 값의 뜻은 시험 기기에서 설정을 바꿔 가며 확인합니다.

| 표 | 키 | 볼 거리(이름에서 짐작) |
|---|---|---|
| global | `adb_enabled`, `adb_wifi_enabled`, `adb_allowed_connection_time`, `development_settings_enabled` | USB·무선 디버깅과 개발자 옵션 |
| global | `device_provisioned`, `boot_count` | 초기 설정 완료 여부, 부팅 횟수 |
| global | `airplane_mode_on`, `wifi_on`, `bluetooth_on`, `mobile_data` | 무선 연결 상태 |
| global | `stay_on_while_plugged_in`, `usb_mass_storage_enabled`, `secure_frp_mode` | 충전 중 화면 유지, USB 저장소, 초기화 보호 |
| secure | `android_id`, `bluetooth_name`, `bluetooth_address` | 기기 식별 값 |
| secure | `mock_location`, `location_mode` | 가짜 위치 앱, 위치 설정 |
| secure | `install_non_market_apps` | 출처를 알 수 없는 앱 설치 |
| secure | `default_input_method`, `enabled_input_methods` | 입력기 |
| secure | `user_setup_complete` | 사용자 초기 설정 완료 |
| secure | `backup_enabled`, `backup_transport` | 백업 설정 |
| system | `screen_off_timeout` | 화면 꺼짐 시간 |

주제별 키는 해당 페이지에서 다룹니다. 시각·시간대 키는 [시간대와 시각 설정 (Time Zone)](time-zone.md), 잠금 화면 키는 [잠금 화면 설정 (Lock Settings)](lock-settings.md), 빌드·부팅과 기기 이름 키는 [기기 정보와 빌드 (build.prop·Build)](device-build.md), 사용자·프로필 키는 [사용자와 프로필 (Multi-user·users)](users-profiles.md) 페이지에 있습니다.

## 증거로서 의미

| 기록 | 증명하는 것 | 증명하지 못하는 것 |
|---|---|---|
| 키와 값 | 파일을 확보한 시점에 그 설정이 그 값이었다는 것 | 사건 당시에도 같은 값이었는지, 언제 바뀌었는지 |
| 키가 있음 | 그 키에 값이 한 번은 쓰였다는 것 | 사용자가 직접 바꿨는지(시스템·앱도 씀) |
| 키가 없음 | 확보한 파일에 그 항목이 없다는 것 | 그 기능을 한 번도 쓰지 않았다는 것 |
| `package` 속성 | 값과 함께 그 패키지 이름이 적혀 있다는 것 | 그 앱이 값을 바꿨다는 것 |
| `.fallback` 파일 | 백업 파일이 남아 있었다는 것 | 원본과 다른 시점의 값이라는 것 |

보고서에는 "확보한 settings_global.xml 파일에 adb_enabled 키의 값이 N 으로 기록되어 있다" 처럼 파일·키·값만 적고, 값이 무엇을 뜻하는지는 확인한 근거가 있을 때만 덧붙입니다.

## 시각 해석

`setting` 태그의 속성에는 시각 필드가 없어서 [2], 설정별로 언제 바뀌었는지는 이 파일로 알 수 없습니다. 파일 전체의 마지막 수정 시각은 파일 시스템 메타데이터에 남지만 어느 키가 그때 바뀌었는지는 나와 있지 않고, 읽는 법은 [파일 시스템 (ext4·F2FS)](../../01-foundations/storage/filesystems/index.md) 페이지에 있습니다. 설정이 바뀐 시각이 필요하면 로그나 앱 사용 기록처럼 시각이 붙은 다른 기록에서 찾습니다.

## 함정과 한계

settings 파일은 확보 시점의 값만 담고 변경 이력이 없습니다. adb 를 켰다가 끈 경우처럼 사건 뒤에 값을 되돌렸다면 파일에는 되돌린 값만 남고, 판매용 기기에는 변경 기록(mHistoricalOperations)도 없습니다 [2]. 증거를 없애려 한 정황을 볼 때는 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md) 시나리오의 순서로 다른 기록과 맞춰 봅니다.

settings 파일에 제어 문자나 이스케이프하지 않은 `&` 가 들어 있어 XML 파싱이 실패하는 경우가 있습니다 [3]. 일반 XML 파서가 오류를 내면 파일이 손상됐다고 단정하지 말고 원문을 헥스로 먼저 봅니다.

AOSP 에 이름이 있는 키라도 기기의 목록에 나오지 않을 수 있고, 그런 키의 예는 시간대·잠금 화면 페이지에 있습니다. 한 번도 값을 쓰지 않은 키가 목록에서 빠지는지 단정할 수 없어서, 키가 없다는 사실로 기능 사용 여부를 말하지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

파일을 헥스로 열어 첫 바이트를 봅니다. 글자 XML 이면 `3C`(`<`)처럼 사람이 읽을 수 있는 글자로 시작하고, 알아볼 수 없는 바이트로 시작하면 ABX 일 수 있어 [안드로이드 바이너리 XML (ABX)](../../01-foundations/data-formats/abx.md) 페이지의 방법으로 글자 XML 로 바꿉니다. 글자 XML 이라면 항목 하나는 다음 모양입니다. 속성 이름은 소스에서 가져왔고 [2], 값은 설명하려고 만든 예시이며 실제 기기에서 나온 것이 아닙니다.

```xml
<settings>
  <setting id="42" name="device_name" value="Example Phone" package="android" />
</settings>
```

### 공개 도구로 한 번

라이브 기기에서는 adb 일반 권한으로 세 표의 키와 값을 뽑을 수 있습니다.

```sh
adb shell settings list global > settings_global.txt
adb shell settings list secure > settings_secure.txt
adb shell settings list system > settings_system.txt
```

이미지에서는 ALEAPP 의 settingsSecure 모듈이 `android_id`, `bluetooth_name`, `bluetooth_address`, `mock_location` 을 User·Name·Value 열로 뽑아 줍니다 [3]. 이 모듈은 네 키만 보니 나머지 키는 XML 을 직접 읽어 확인합니다.

## 교차 검증

adb·개발자 옵션 값은 [USB 연결 기록 (USB)](../network/usb.md) 과, 무선 연결 값은 [와이파이 설정과 접속 기록 (WifiConfigStore)](../network/wifi.md)·[블루투스 장치 (Bluetooth)](../network/bluetooth.md) 와 맞춰 봅니다. 가짜 위치 앱이나 출처를 알 수 없는 앱 설치와 관련된 값은 [설치된 앱 (packages.xml)](../app-usage/packages/index.md) 의 설치 흔적과 함께 봅니다. 입력기 값은 [삼성 키보드 입력 기록 (Samsung Keyboard)](../samsung/samsung-keyboard.md)·[지보드 입력 기록 (Gboard)](../google-services/gboard.md) 을 고를 때 씁니다.

## 실습

공개된 안드로이드 시험 이미지(NIST CFReDS 에 올라온 모바일 이미지 등)를 구해 다음을 풀어 봅니다.

1. 사용자 번호 폴더마다 settings 파일이 몇 개 있는지, 글자 XML 인지 ABX 인지 적습니다.
2. `.fallback` 파일이 있으면 원본과 키·값을 비교해 다른 항목을 찾습니다.
3. 위 "조사에 쓸 만한 키" 표의 키 가운데 이 이미지에 있는 키와 없는 키를 나눕니다.
4. ALEAPP settingsSecure 결과와 XML 원문의 `android_id` 값을 비교합니다.

## 참고 문헌

1. SettingsProvider.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/packages/SettingsProvider/src/com/android/providers/settings/SettingsProvider.java
2. SettingsState.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/packages/SettingsProvider/src/com/android/providers/settings/SettingsState.java
3. ALEAPP settingsSecure.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/settingsSecure.py
