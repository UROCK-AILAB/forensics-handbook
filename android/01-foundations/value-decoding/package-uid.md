---
title: "패키지 이름과 UID"
parent: "기반 · 값 읽는 법"
nav_order: 250
---

# 패키지 이름과 UID (Package Name·UID)

## 한 줄 요약

Android 는 앱을 `com.android.chrome` 같은 패키지 이름으로 부르고 숫자 UID 로 실행하는데, 기록마다 남기는 쪽이 달라서 로그와 설정에 남은 UID 를 패키지 이름과 사용자 번호로 되돌려 읽어야 기록을 남긴 주체를 가려낼 수 있습니다.

## 이 형식을 쓰는 아티팩트

앱마다 UID 를 따로 받는 구조와 그 보안상 의미는 [앱 샌드박스와 권한](../security-model/sandbox-permissions.md)에서 다루고, 이 페이지는 값을 읽는 방법만 다룹니다. 아래 칸 이름은 실제 기기에서 본 출력의 모양입니다.

| 기록 | 패키지 이름이 남는 칸 | UID·사용자가 남는 칸 | 자세히 |
|---|---|---|---|
| dumpsys usagestats 이벤트 | `package=`, `class=`, `taskRootPackage=`, `taskRootClass=` | 이벤트 묶음 앞의 `user=#` | [앱 사용 기록](../../02-artifacts/app-usage/usagestats/index.md) |
| dumpsys notification 레코드 | `pkg=`, `opPkg=` | `uid=##### userId=-#` | [알림 기록](../../02-artifacts/app-usage/notification-history.md) |
| dumpsys account "Accounts History" | 없음 | `UID` 칸(4자리와 5자리가 섞임) | [계정](../../02-artifacts/system-account/accounts/index.md) |
| dumpsys package "Known Packages" | 역할별 패키지 이름 | 없음 | [설치된 앱](../../02-artifacts/app-usage/packages/index.md) |
| dumpsys user | 없음 | `UserInfo{…}`, `serialNo`, `parentId` | [사용자와 프로필](../../02-artifacts/system-account/users-profiles.md) |
| 공용 저장 공간 | `/sdcard/Android/media` 아래 폴더 이름 | 없음 | [공용 저장 공간](../storage/shared-storage.md) |
| settings secure | `appprotection_package_uid` 키(뜻은 확인 필요) | 같은 키 | [설정 값](../../02-artifacts/system-account/settings.md) |

실제 기기에서 `/sdcard/Android/media` 아래에는 `com.google.android.gms`, `com.samsung.android.spay` 처럼 패키지 이름을 그대로 쓴 폴더가 있었고, 설치 패키지는 시스템 앱 486개와 사용자가 설치한 앱 168개였습니다.

## 구조

### UID 범위

AOSP 의 `android_filesystem_config.h` 는 UID 와 GID 의 범위를 아래처럼 정합니다[1]. 여기서 "사용자 안의 번호" 는 사용자 번호를 떼어 낸 뒤의 값(앱 ID, appId)입니다.

| 범위(사용자 안의 번호) | 상수 | 뜻 |
|---|---|---|
| 0 | `AID_ROOT` | root |
| 1000 | `AID_SYSTEM` | system server |
| 1001 | `AID_RADIO` | 전화 기능(telephony, RIL) |
| 1002 | `AID_BLUETOOTH` | 블루투스 |
| 1010 | `AID_WIFI` | 와이파이 |
| 1013 | `AID_MEDIA` | mediaserver |
| 2000 | `AID_SHELL` | adb 와 디버그 셸 사용자 |
| 2900~2999 | `AID_OEM_RESERVED_START`~`END` | 제조사 예약 |
| 9999 | `AID_NOBODY` | nobody |
| 10000~19999 | `AID_APP_START`~`AID_APP_END` | 앱 UID ("first app user"~"last app user") |
| 20000~29999 | `AID_SDK_SANDBOX_PROCESS_START`~`END` | SDK 샌드박스 프로세스 UID |
| 20000~29999 | `AID_CACHE_GID_START`~`END` | 캐시 데이터 표시용 GID |
| 30000~39999 | `AID_EXT_GID_START`~`END` | 외부 저장소 데이터 표시용 GID |
| 50000~59999 | `AID_SHARED_GID_START`~`END` | 한 사용자 안에서 앱끼리 공유하는 GID |
| 90000~99999 | `AID_ISOLATED_START`~`END` | 완전히 격리한 샌드박스 프로세스 UID |
| 100000 | `AID_USER_OFFSET` | 사용자마다 UID 범위를 옮기는 간격 |

### 사용자 번호가 들어간 UID

`AID_USER_OFFSET` 이 100000 이라서 사용자마다 UID 범위가 100000 씩 밀립니다[1]. 이 상수에서 다음 식이 나옵니다.

```
UID = 사용자 ID × 100000 + 앱 ID
사용자 ID = UID ÷ 100000 의 몫
앱 ID     = UID ÷ 100000 의 나머지
```

아래 표는 특정 앱이 아니라 식을 따라 만든 예시입니다.

| 사용자 ID | 앱 ID | UID | 자릿수 |
|---|---|---|---|
| 0 | 10123 | 10123 | 5 |
| 10 | 10123 | 1010123 | 7 |
| 100 | 10123 | 10010123 | 8 |
| 10 | 1000 | 1001000 | 7 |

UID 의 자릿수만 봐도 대강의 성격이 드러납니다. 사용자 0 에서는 4자리가 시스템 쪽 번호이고 5자리가 앱 범위이며, 7자리 이상이면 사용자 0 이 아닌 다른 사용자나 프로필의 번호입니다.

### 패키지 관리자 파일

패키지 관리자 설정 코드(`Settings.java`)는 `/data/system` 을 기준 폴더로 쓰고, 아래 파일을 다룹니다[2].

| 경로 | 비고 |
|---|---|
| `/data/system/packages.xml` | 설치된 패키지 설정 |
| `/data/system/packages.xml.reservecopy` | 예비 사본 |
| `/data/system/packages-backup.xml` | 백업 사본 |
| `/data/system/packages.list` | 권한 0640, 소유자 `SYSTEM_UID`, 그룹 `PACKAGE_INFO_GID` |
| `/data/system/packages-stopped.xml` | 중지된 패키지 |
| `/data/system/users/<userId>/package-restrictions.xml` | 사용자별 패키지 상태, 첫 설치 시각(`first-install-time`)도 여기에 있음 |

현재 AOSP 는 이 파일들을 [안드로이드 바이너리 XML](../data-formats/abx.md)로 쓸 수 있습니다[2]. `packages.xml` 안의 칸 이름과 `packages.list` 한 줄의 칸 구성은 이번 조사에서 원문 줄로 확인하지 못했고, [설치된 앱](../../02-artifacts/app-usage/packages/index.md)에서 다룹니다. 첫 설치 시각처럼 16진수로 적힌 값을 읽는 방법은 [시각 값](time-values.md)에 있습니다.

## 읽는 법

1. UID 를 100000 으로 나눠 사용자 ID 와 앱 ID 로 나눕니다.
2. 앱 ID 를 위 범위 표에 대 봅니다. 10000~19999 라면 일반 앱이고, 1000~9999 라면 시스템 쪽 번호이며, 90000~99999 라면 격리 프로세스입니다.
3. 앱 ID 가 앱 범위라면 같은 기기의 패키지 관리자 파일이나 dumpsys package 출력에서 그 번호를 쓰는 패키지를 찾습니다.
4. 사용자 ID 가 0 이 아니라면 dumpsys user 출력이나 사용자 목록에서 그 번호가 어떤 사용자나 프로필인지 확인합니다.

```
UID 1010123 을 읽는 예 (식으로 만든 예시)
  1010123 ÷ 100000 = 몫 10, 나머지 10123
  → 사용자 ID 10 의 앱 ID 10123
  → 사용자 10 이 어떤 프로필인지 dumpsys user 로 확인
  → 앱 ID 10123 을 쓰는 패키지를 패키지 관리자 기록에서 찾음
```

실제 기기의 dumpsys user 에는 주 사용자 `UserInfo{#:xxx:#c##} serialNo=# isPrimary=true` 와 함께 `UserInfo{###:xxx:#####} serialNo=### isPrimary=false parentId=#` 처럼 부모가 있는 세 자리 ID 의 프로필이 하나 더 있었습니다. 이 프로필에 속한 앱의 UID 는 식대로라면 여덟 자리가 됩니다. 이 프로필이 삼성 보안 폴더인지는 확인하지 못했고, 프로필을 가려내는 방법은 [보안 폴더와 작업 프로필](../security-model/secure-folder-work-profile.md)에서 다룹니다.

## 포렌식에서 중요한 점

UID 는 기록을 남긴 쪽이 앱인지 시스템인지를 가르는 첫 단서입니다. 실제 기기의 dumpsys account "Accounts History" 에서는 같은 계정 제거 동작(`action_account_remove`)에도 `UID` 칸에 4자리 값과 5자리 값이 모두 나왔습니다. 범위 표로 보면 4자리는 시스템 쪽이고 5자리는 사용자 0 의 앱 범위라서[1], 계정 변경을 앱이 직접 요청했는지 시스템 구성 요소가 처리했는지 나눠 보는 출발점이 됩니다. 기록 하나가 사람의 조작을 뜻하는지는 이 칸만으로 정하지 않고 다른 기록과 함께 봅니다.

UID 2000 은 adb 와 디버그 셸 사용자에게 정해진 번호입니다[1]. 이 핸드북의 기기 관찰도 adb 셸에서 UID 2000 으로 읽었습니다. 기록에 UID 2000 이 남아 있다면 adb 나 셸을 거친 동작일 수 있어서, 조사 대상 기간에 개발자 옵션이나 adb 연결 흔적이 있는지 함께 확인합니다. 조사자가 수집하면서 남긴 기록과 섞이지 않도록 수집 시각도 따로 적어 둡니다.

패키지 관리자 파일은 원본 외에 `packages-backup.xml` 과 `packages.xml.reservecopy` 같은 사본이 따로 있습니다[2]. 원본이 손상됐거나 내용이 비정상일 때 사본과 비교해 볼 수 있지만, 각 사본이 언제 만들어지고 언제 지워지는지는 이 페이지에서 확인하지 못했습니다.

## 함정

같은 숫자가 UID 로도 GID 로도 쓰입니다. 20000 은 SDK 샌드박스 프로세스 UID 의 시작이면서 캐시 데이터 표시용 GID 의 시작이기도 하고[1], 50000 대 공유 GID 와 30000 대 외부 저장소 GID 는 앱 UID 가 아닙니다. 파일 소유자 칸인지 그룹 칸인지 먼저 확인하고 나서 범위 표에 대 봅니다.

90000 대 격리 프로세스 UID 와 20000 대 SDK 샌드박스 UID 는 앱 범위 밖이라서, 앱 ID 로 바로 패키지를 찾을 수 없습니다. 이 번호가 어느 앱에서 나온 프로세스인지 잇는 방법은 이 페이지에서 확인하지 못했습니다.

UID 와 패키지의 대응은 수집한 시점의 패키지 관리자 기록으로 확인한 결과입니다. 과거 기록에 남은 UID 가 그때도 같은 패키지였다고 단정하지 않고, 앱을 지운 뒤 같은 번호가 다른 앱에 다시 쓰이는지도 이 페이지에서 확인하지 못했습니다. 공유 UID(sharedUserId)로 여러 패키지가 UID 하나를 함께 쓰는 동작도 1차 자료로 확인하지 못해서, UID 하나에 패키지가 여럿 나오면 따로 확인합니다.

dumpsys notification 레코드의 `userId` 칸에는 `-#` 처럼 음수가 찍힌 레코드가 있었습니다. 음수는 사용자 번호 범위에 들어가지 않으니, 이 값을 특정 사용자로 옮겨 적지 않고 뜻을 확인한 뒤에 씁니다.

역할별 기본 패키지는 제조사 앱이 함께 끼어 있어 한 역할에 둘 이상이 나올 수 있습니다. 실제 기기의 dumpsys package "Known Packages" 절은 아래와 같았습니다.

| 역할 | 패키지 |
|---|---|
| System | `android` |
| Setup Wizard | `com.google.android.setupwizard` |
| Installer | `com.google.android.packageinstaller` |
| Verifier | `com.android.vending`, `com.samsung.android.sm.devicesecurity` |
| Browser | `com.android.chrome` |
| System Text Classifier | `com.google.android.ext.services`, `com.samsung.android.smartsuggestions` |
| Permission Controller | `com.google.android.permissioncontroller` |
| Wellbeing | `none` |
| Configurator | `com.google.android.gms` |
| App Predictor | `com.google.android.as` |
| Companion | `com.android.companiondevicemanager` |
| Recents | `com.sec.android.app.launcher` |
| Developer verification service provider | `com.google.android.verifier` |

`/sdcard/Android/media` 아래에 패키지 이름 폴더가 있다고 해서 그 앱이 지금 설치돼 있다고 보지 않습니다. 폴더 이름은 패키지 목록과 대조해서 확인합니다.

## 도구

- `adb shell dumpsys package`, `adb shell dumpsys user`: 살아 있는 기기에서 패키지와 사용자 목록을 봅니다. 출력은 수집 시점의 상태입니다.
- 패키지 관리자 파일을 이미지에서 읽을 때는 파일이 바이너리 XML 인지 먼저 확인하고, 그렇다면 [안드로이드 바이너리 XML](../data-formats/abx.md)에 나온 방법으로 텍스트로 바꿉니다.
- 몫과 나머지는 Python `divmod(uid, 100000)` 한 줄로 셈합니다.

UID 를 패키지로 바꾸는 과정을 도구에 맡겼다면 결과 몇 개를 위 식으로 손으로 셈해 맞춰 봅니다. 앱 ID 가 여러 기록에서 어떻게 이어지는지는 [어떤 앱을 언제 썼나](../../04-scenarios/activity/app-usage.md)와 [악성 앱 흔적 분석](../../03-techniques/analysis/malicious-app-triage/index.md)에서 다룹니다.

## 참고 문헌

1. AOSP platform/system/core — libcutils/include/private/android_filesystem_config.h — https://raw.githubusercontent.com/aosp-mirror/platform_system_core/main/libcutils/include/private/android_filesystem_config.h
2. AOSP platform/frameworks/base — services/core/java/com/android/server/pm/Settings.java — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/Settings.java
