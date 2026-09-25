---
title: "기기 정보와 빌드"
parent: "아티팩트 · 시스템·계정"
nav_order: 310
---

# 기기 정보와 빌드 (build.prop·Build)

기기의 제조사·모델·Android 버전·보안 패치·빌드 지문이 어디에 남고 어떻게 읽는지를 정리합니다. 소스로 확인한 값은 현행 AOSP 기준(frameworks/base 의 main 가지)이라서 어느 출시 버전에서 바뀌었는지는 대부분 확인하지 못했습니다. 실제 폰에서 본 모양에는 확인 범위를 붙였습니다.

## 한 줄 요약

기기를 특정하는 값은 이름이 `ro.` 로 시작하는 시스템 속성에 들어 있고, 앱이 보는 `android.os.Build` 의 필드도 이 속성을 읽어 만들어서 [1], 이미지에서는 build.prop 파일을, 라이브 기기에서는 dumpsys·settings 출력을 함께 봅니다.

## 무엇을 기록하나 · 왜 생기나

`android.os.Build` 클래스는 모델 이름이나 Android 버전 같은 값을 따로 저장하지 않고 시스템 속성에서 읽어 옵니다 [1]. 그래서 앱이 기기 정보를 어떻게 얻든 근원은 같은 속성이고, 분석할 때도 속성 이름을 기준으로 삼으면 도구마다 칸 이름이 달라도 헷갈리지 않습니다.

조사에서 이 값이 필요한 이유는 두 가지입니다. 보고서 첫머리에 어떤 기기를 분석했는지 적어야 하고, 이 핸드북의 다른 페이지들이 Android 버전과 제조사에 따라 해석을 나누기 때문에 어느 표를 따를지 먼저 정해야 합니다. 사용자 식별과 관련된 일련번호·IMEI·Android ID 는 [기기 식별자 (Android ID·IMEI·광고 ID)](../../01-foundations/value-decoding/device-identifiers.md) 페이지에서 다룹니다.

## 위치와 버전별 차이

| 어디서 읽나 | 얻는 것 | 확인 정도 |
|---|---|---|
| 이미지의 `*/system/build.prop`, `*/vendor/build.prop` | 제조사·브랜드·모델·기기 이름·Android 버전·SDK 번호 | ALEAPP Build 모듈이 찾는 경로 [2] |
| 그 밖의 파티션(product, odm 등)의 build.prop | 파티션별 값 | 경로를 공식 문서로 확인하지 못함 |
| `dumpsys package` 맨 앞 "Database versions:" | SDK 번호와 빌드 지문 두 개 | 관찰 (확인 범위: Android 16, One UI 8.5) |
| `dumpsys user` 의 "Last logged in fingerprint:" | 사용자가 마지막으로 로그인할 때의 빌드 지문 | 관찰 (확인 범위: Android 16, One UI 8.5) |
| settings 의 빌드·부팅 관련 키 | 키 이름만 확인, 값의 뜻은 확인하지 못함 | 관찰 (확인 범위: Android 16, One UI 8.5) |

ALEAPP 의 Build 모듈은 `*/vendor/build.prop` 와 `*/system/build.prop` 를 읽고, 두 파일에 같은 항목이 있으면 vendor 쪽 값을 보고합니다 [2]. 뽑는 키는 `ro.product.vendor.manufacturer`·`ro.product.system.manufacturer` 처럼 vendor 와 system 이 짝을 이루는 이름들이고, 버전은 `ro.vendor.build.version.release`, `ro.build.version.release`, `ro.system.build.version.release` 를, SDK 번호는 `ro.vendor.build.version.sdk`, `ro.build.version.sdk` 를 봅니다 [2]. build.prop 가 이미지 안 어느 경로들에 있는지는 이 경로 패턴 말고는 확인하지 못했습니다.

라이브 기기에서 흔히 쓰는 `getprop` 출력은 이번 관찰 자료에 없어서, adb 일반 권한으로 속성이 모두 읽히는지는 확인하지 못했습니다. 대신 adb 일반 권한으로 읽은 `dumpsys package` 출력 맨 앞에 다음 모양의 줄이 있었습니다(값은 가려져 있습니다). (확인 범위: Android 16, One UI 8.5)

```
Database versions:
  Internal:
    sdkVersion=## sdkVersionFull=####### databaseVersion=#
    buildFingerprint=<값> fingerprint=<값>
  External:
```

`buildFingerprint` 와 `fingerprint` 가 각각 무엇을 가리키는지는 출처로 확인하지 못했습니다. `dumpsys user` 의 "Last logged in fingerprint:" 줄은 사용자 파일의 `lastLoggedInFingerprint` 속성과 짝을 이루고, 자세한 내용은 [사용자와 프로필 (Multi-user·users)](users-profiles.md) 페이지에 있습니다.

settings 에서는 global 표에 `database_creation_buildid`, `boot_count`, `Phenotype_boot_count`, `device_name`, `default_device_name` 키가, system 표에 `IsFotaUpgrade` 키가 있었습니다. (확인 범위: Android 16, One UI 8.5) 이름으로 보면 설정 DB 를 만들 때의 빌드, 부팅 횟수, 사용자가 붙인 기기 이름, 무선 업데이트 여부와 관련된 듯하지만 값의 뜻은 확인하지 못했습니다. settings 파일 자체의 구조는 [설정 값 (Settings Global·Secure·System)](settings.md) 페이지에 있습니다.

삼성 기기는 One UI 버전을 따로 표시하지만, 그 값을 담은 삼성 전용 속성 이름은 확인하지 못했습니다. 관찰에 쓴 기기는 Android 16(SDK 36), One UI 8.5, 보안 패치 2026-08-05 입니다. (확인 범위: Android 16, One UI 8.5)

## 구조

`Build` 필드와 속성의 대응은 다음과 같습니다(현행 AOSP 기준) [1].

| Build 필드 | 시스템 속성 |
|---|---|
| ID / DISPLAY | `ro.build.id` / `ro.build.display.id` |
| PRODUCT / DEVICE / BOARD | `ro.product.name` / `ro.product.device` / `ro.product.board` |
| MANUFACTURER / BRAND / MODEL | `ro.product.manufacturer` / `ro.product.brand` / `ro.product.model` |
| BOOTLOADER / HARDWARE | `ro.bootloader` / `ro.hardware` |
| TYPE / TAGS / USER / HOST | `ro.build.type` / `ro.build.tags` / `ro.build.user` / `ro.build.host` |
| VERSION.RELEASE / VERSION.SDK_INT | `ro.build.version.release` / `ro.build.version.sdk` |
| VERSION.INCREMENTAL / VERSION.SECURITY_PATCH | `ro.build.version.incremental` / `ro.build.version.security_patch` |
| VERSION.BASE_OS | `ro.build.version.base_os` |
| TIME | `ro.build.date.utc` × 1000 |
| FINGERPRINT | `ro.build.fingerprint`, 없으면 조립 |
| SOC_MANUFACTURER / SOC_MODEL | SocProperties 의 soc_manufacturer()·soc_model(), 없으면 UNKNOWN |

빌드 지문(fingerprint)은 `ro.build.fingerprint` 가 있으면 그 값을 쓰고, 없으면 다음 순서로 조립합니다 [1].

```
brand/name/device:release/id/incremental:type/tags
```

지문과 빌드 시각은 파티션마다 따로 있습니다. bootimage, odm, product, system_ext, system, vendor 파티션마다 `ro.<파티션>.build.fingerprint` 와 `ro.<파티션>.build.date.utc` 가 있고, 빌드 시각은 이쪽도 1000 을 곱해 밀리초로 씁니다 [1].

`Build.SERIAL` 필드는 현행 AOSP 에서 실제 일련번호를 주지 않고 늘 UNKNOWN 이고, 실제 값은 `Build.getSerial()` 로만 얻고 READ_PRIVILEGED_PHONE_STATE 권한이 필요합니다 [1]. 이 제한이 어느 버전부터인지는 확인하지 못했습니다.

## 증거로서 의미

| 기록 | 증명하는 것 | 증명하지 못하는 것 |
|---|---|---|
| build.prop 의 제조사·모델·버전 값 | 확보한 이미지에 설치되어 있던 소프트웨어가 스스로 밝힌 기기·버전 | 기판 자체가 그 모델이라는 것(속성은 소프트웨어가 적은 값) |
| 보안 패치 값 | 확보 시점의 패치 수준 | 사건 당시의 패치 수준, 언제 업데이트했는지 |
| 빌드 지문과 빌드 시각 | 그 빌드를 만든 시각과 빌드 식별 값 | 기기에 설치한 시각 |
| 파티션별 지문이 서로 다름 | 파티션마다 다른 빌드 값이 적혀 있다는 것 | 부분 업데이트·교체가 있었다는 것(해석 근거를 확인하지 못함) |
| 사용자별 마지막 로그인 지문 | 그 사용자가 마지막으로 로그인할 때의 빌드 | 그 뒤의 업데이트 이력 전체 |

보고서에는 "확보한 이미지의 build.prop 에 모델 SM-XXXX, Android 버전 N, 보안 패치 YYYY-MM-DD 가 기록되어 있다" 처럼 어느 파일의 어느 속성에서 읽었는지까지 적습니다.

## 시각 해석

`ro.build.date.utc` 는 유닉스 초이고 `Build.TIME` 은 여기에 1000 을 곱한 유닉스 밀리초입니다 [1]. 두 값 모두 빌드 서버에서 소프트웨어를 만든 시각이라 기기에서 일어난 일의 시각이 아니고, 업데이트를 설치한 시각으로 읽어서도 안 됩니다. Android 12 부터 자동 시각 설정이 이 빌드 시각보다 이른 시각 제안을 버린다는 점은 [시간대와 시각 설정 (Time Zone)](time-zone.md) 페이지에 있습니다. 숫자를 날짜로 바꾸는 법은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../01-foundations/value-decoding/time-values.md) 페이지를 봅니다.

## 함정과 한계

ALEAPP Build 모듈은 vendor 와 system 값이 다르면 vendor 값을 보고해서 [2], 두 파일의 값이 실제로 다를 때 한쪽만 보고 판단하게 됩니다. 결과를 옮기기 전에 두 파일을 직접 열어 비교합니다.

build.prop 는 확보 시점의 소프트웨어 상태만 보여 줍니다. 무선 업데이트를 거치면 값이 새 빌드로 바뀌어서, 사건 당시의 버전을 말하려면 사용자별 마지막 로그인 지문이나 앱 오류 기록 같은 다른 기록의 시각과 맞춰 봐야 합니다. `IsFotaUpgrade`, `database_creation_buildid` 같은 settings 키도 이런 단서가 될 수 있어 보이지만 값의 뜻을 확인하지 못해서 보고서에 해석을 적지 않습니다.

속성 값은 소프트웨어가 적은 것이라, 펌웨어가 바뀌지 않았다는 점은 이 값만으로 말하지 않고 [부트로더와 검증 부팅 (Bootloader·Verified Boot)](../../01-foundations/security-model/verified-boot.md) 페이지의 흔적과 함께 봅니다. `ro.build.type`, `ro.build.tags` 에 어떤 값이 들어가는지는 이번 자료로 확인하지 못해서 판매용 빌드인지 가리는 근거로 쓰지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

build.prop 는 ALEAPP 가 속성 이름으로 값을 뽑는 글자 파일이고 [2], 한 줄에 `이름=값` 을 적는 모양이 흔히 알려져 있지만 이번 자료에서 형식 명세를 따로 확인하지는 않았습니다. 아래는 그 모양으로 만든 예시이고 실제 기기에서 나온 값이 아닙니다.

```
72 6F 2E 62 75 69 6C 64 2E 64 61 74 65 2E 75 74   ro.build.date.ut
63 3D 31 37 30 30 30 30 30 30 30 30 0A            c=1700000000.
```

`3D` 는 `=`, `0A` 는 줄바꿈입니다. 값 1700000000 은 유닉스 초라서 2023-11-14 22:13:20 UTC 이고, 같은 기기에서 `Build.TIME` 은 1700000000000 이 됩니다 [1].

### 공개 도구로 한 번

이미지에서 build.prop 를 모두 찾아 같은 키를 나란히 뽑아 봅니다.

```sh
find ./extract -name build.prop
grep -H -E '^ro\.(product\.(vendor|system)\.model|build\.version\.(release|security_patch)|build\.fingerprint|build\.date\.utc)=' $(find ./extract -name build.prop)
```

ALEAPP 의 Build 모듈 결과와 이 목록을 비교해 vendor 와 system 의 값이 다른 키가 있는지 확인합니다 [2]. 라이브 기기에서는 `adb shell dumpsys package` 출력 맨 앞의 "Database versions:" 부분과 `adb shell dumpsys user` 의 지문 줄을 옮겨 둡니다. dumpsys 를 뽑는 방법은 [dumpsys 출력 (dumpsys)](../logs/dumpsys.md) 페이지에 있습니다.

## 교차 검증

사용자별 마지막 로그인 지문과 사용자 생성 시각은 [사용자와 프로필 (Multi-user·users)](users-profiles.md) 에서, 앱 설치 시각은 [설치된 앱 (packages.xml)](../app-usage/packages/index.md) 에서 확인해 업데이트 전후를 가릅니다. 공장 초기화 뒤 다시 설정한 기기인지는 [초기화 흔적 (Factory Reset)](factory-reset.md) 과 함께 봅니다. 앱 오류 기록에 빌드 지문이 함께 적히는 경우가 있는지는 [앱 오류·종료 기록 (DropBox·tombstones·ANR)](../app-usage/crash-records.md) 에서 확인합니다.

## 실습

공개 안드로이드 검체(NIST CFReDS 에 올라온 모바일 이미지 등)를 구해 다음을 풀어 봅니다.

1. 이미지 안의 build.prop 를 모두 찾아 경로를 적고, 각 파일의 `ro.build.version.release` 값이 같은지 비교합니다.
2. system 과 vendor 의 빌드 지문을 비교하고, 다르다면 어느 부분(버전·incremental·날짜)이 다른지 적습니다.
3. `ro.build.date.utc` 를 날짜로 바꾸고, 그 날짜보다 이른 시각이 찍힌 기록이 이미지 안에 있는지 찾아봅니다.
4. ALEAPP Build 모듈이 보고한 값이 어느 파일의 값인지 1번 결과로 확인합니다.

## 참고 문헌

1. Build.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/os/Build.java
2. ALEAPP build.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/build.py
