---
title: "앱 권한 부여 기록"
parent: "설치된 앱"
grand_parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 440
---

# 앱 권한 부여 기록 (Runtime Permissions)

사용자가 앱에 준 위험 권한(런타임 권한)의 현재 상태가 어느 파일에 어떻게 남는지 정리합니다. 내용은 현행 AOSP 기준(frameworks/base 의 main 가지)이고, 출시 버전마다 다를 수 있습니다. 권한 체계 자체는 [앱 샌드박스와 권한](../../../01-foundations/security-model/sandbox-permissions.md) 페이지에서 다룹니다.

## 한 줄 요약

`runtime-permissions.xml` 은 사용자별로 앱마다 런타임 권한의 부여 여부(granted)와 부여 경위를 담은 비트 값(flags)을 적는 파일이고, 파일 위치는 `/data/system/users/` 아래 옛 위치와 권한 모듈의 새 위치 두 곳입니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

앱이 위치·카메라·연락처 같은 권한을 요청하면 사용자가 허용하거나 거부하고, 시스템은 그 결과를 사용자별 파일에 적어 둡니다. 이 파일에는 권한마다 지금 부여된 상태인지와 함께, 사용자가 정했는지·정책이 정했는지·기본으로 줬는지 같은 경위가 flags 비트로 남습니다 [1][3]. 스토커웨어처럼 몰래 설치한 앱이 어떤 권한을 받았는지 볼 때 먼저 확인하는 파일입니다.

## 위치와 버전별 차이

| 위치 | Android 버전 | 내용 |
|---|---|---|
| `/data/system/users/<사용자ID>/runtime-permissions.xml` | Android 10 이하 [7] | 옛 위치(Settings.getUserRuntimePermissionsFile) [1] |
| `/data/misc_de/<사용자ID>/apexdata/com.android.permission/runtime-permissions.xml` | Android 11 부터 [7] | 권한 모듈이 쓰는 새 위치. 같은 폴더에 예비 사본 `runtime-permissions.xml.reservecopy` 도 씁니다 [6] |

ALEAPP 는 두 위치를 함께 찾습니다 [2]. 현행 AOSP 는 먼저 권한 모듈의 저장소에서 읽고, 없으면 옛 파일을 읽은 뒤 새 저장소에 다시 씁니다 [1]. Android 10 에서 11 로 올린 기기에는 두 위치에 파일이 모두 남고, 올린 뒤의 변경은 새 위치에만 적힙니다 [7]. 그래서 두 파일을 비교하면 업그레이드 전의 권한 상태를 볼 수 있습니다. 옛 파일이 남아 있는지는 실제 기기에서 확인합니다.

옛 파일을 읽는 코드는 `Xml.resolvePullParser` 를 쓰기 때문에 옛 위치 파일은 안드로이드 바이너리 XML(ABX)로 저장되어 있을 수 있습니다 [1][4]. 새 위치 파일은 권한 모듈이 `Xml.newSerializer()` 로 쓰는데, 이 함수는 ABX 가 아닌 일반 텍스트 XML 쓰기 도구를 돌려줍니다 [4][6]. 권한 모듈은 파일을 쓴 뒤 본 파일과 예비 사본에 fs-verity 보호를 겁니다 [6]. 삼성 One UI 에서 이 파일의 위치나 형식은 실제 기기로 확인해야 합니다.

ALEAPP 의 runtimePerms 모듈은 Android 16 Pixel 8 Pro 와 Android 15 Poco X7 이미지에서 결과가 "0 rows" 였습니다 [2]. 파일이 없었는지 형식이 달랐는지는 밝혀져 있지 않아서, 최신 기기에서 이 모듈 결과가 비면 파일이 있는지부터 직접 확인합니다.

## 구조

두 위치의 파일은 요소 이름이 다릅니다. 옛 위치는 Settings 의 옛 파일 읽기 코드 기준이고 [1], 새 위치는 권한 모듈의 읽기·쓰기 코드 기준입니다 [6].

| 옛 위치 요소 | 새 위치 요소 | 속성 | 담긴 것 |
|---|---|---|---|
| `<runtime-permissions>` | `<runtime-permissions>` | version, fingerprint | 뿌리 요소. 옛 파일은 version 이 없으면 P→Q 업그레이드(UPGRADE_VERSION)로 봅니다 |
| `<pkg>` | `<package>` | name | 앱 하나 |
| `<shared-user>` | `<shared-user>` | name | 공유 사용자 하나 |
| `<item>` | `<permission>` | name, granted, flags | 앱이나 공유 사용자 아래의 권한 하나 |

새 위치 파일은 flags 를 `Integer.toHexString()` 으로 쓰고 16진수로 읽기 때문에, 파일에는 `0x` 없는 16진수 문자열로 보입니다 [6]. ALEAPP 의 runtimePerms 모듈은 요소 이름을 구분하지 않고 하위 요소의 name·granted·flags 를 읽어서, 경로에서 뽑은 사용자와 요소 종류, 이름, 권한, granted, flags 를 표로 냅니다. flags 는 풀지 않고 그대로 냅니다 [2].

### flags 비트

flags 의 각 비트는 PackageManager 의 FLAG_PERMISSION_* 상수로 정의되어 있습니다 [3].

| 비트 | 이름 | 뜻 |
|---|---|---|
| 0x1 | USER_SET | 사용자가 현재 상태로 정했고, 앱은 다시 요청할 수 있음 |
| 0x2 | USER_FIXED | 사용자가 정하고 고정해서 앱이 더는 요청할 수 없음 |
| 0x4 | POLICY_FIXED | 기기 정책이 정해서 앱도 사용자도 바꿀 수 없음 |
| 0x8 | REVOKE_ON_UPGRADE (REVOKED_COMPAT) | 옛 앱 호환을 위해 부여 상태로 두되 실제 접근은 막음 |
| 0x10 | SYSTEM_FIXED | 시스템 구성요소라서 현재 상태로 고정 |
| 0x20 | GRANTED_BY_DEFAULT | 기본 기능을 위해 기본으로 부여(예: 전화 앱의 전화 권한) |
| 0x40 | REVIEW_REQUIRED | targetSdk 가 M 보다 낮은 앱은 실행 전 검토가 필요하고, 그 이상은 시스템이 요청 창을 띄울 수 있음 |
| 0x80 | REVOKE_WHEN_REQUESTED | 앱이 요청하지 않았는데 시스템이 자동으로 넣었고, 앱이 요청하면 거둠 |
| 0x100 | USER_SENSITIVE_WHEN_GRANTED | 부여된 권한의 사용을 사용자에게 잘 보이게 표시 |
| 0x200 | USER_SENSITIVE_WHEN_DENIED | 거부된 권한에 대해 같은 표시 |
| 0x800 | RESTRICTION_INSTALLER_EXEMPT | 설치자가 제한 권한의 예외를 줌 |
| 0x1000 | RESTRICTION_SYSTEM_EXEMPT | 시스템이 제한 권한의 예외를 줌 |
| 0x2000 | RESTRICTION_UPGRADE_EXEMPT | 업그레이드 때 제한 권한의 예외를 줌 |
| 0x4000 | APPLY_RESTRICTION | 권한이 비활성이고, 보호 데이터 대신 빈 결과를 돌려줌 |
| 0x8000 | GRANTED_BY_ROLE | 앱이 역할(role)을 맡아서 부여됨 |
| 0x10000 | ONE_TIME | 일회성 권한이라 앱이 쉬면 자동으로 거둠 |
| 0x20000 | AUTO_REVOKED | 자동 거둠(auto-revoke)으로 거둬짐 |
| 0x80000 | SELECTED_LOCATION_ACCURACY | 선택한 위치 정확도(예: ACCESS_FINE_LOCATION 에 있으면 정밀 위치를 고름) |

0x400 과 0x40000 은 이 목록에 정의가 없습니다. 권한 컨트롤러가 쓰는 예약 비트는 따로 정의되어 있습니다 [3].

## 라이브 기기에서 보이는 모양 (dumpsys package)

`dumpsys package` 는 권한을 아래 형식으로 찍습니다 [1][3].

```
<권한>: granted=<true|false>, flags=[ USER_SET|USER_FIXED ]
```

비트 이름은 permissionFlagToString() 으로 바꾸고, 이 변환 목록에 없는 비트는 숫자로 찍습니다. SELECTED_LOCATION_ACCURACY 도 변환 목록에 없어서 숫자로 나옵니다 [1][3]. 설치 권한(install permissions)도 같은 형식이고, 사용자 0 과 다를 때만 `, userId=` 와 사용자 번호가 붙습니다 [1].

같은 출력의 "Known Packages:" 절에는 권한 컨트롤러 패키지가 "Permission Controller:" 로 찍힙니다(예: `com.google.android.permissioncontroller`).

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 파일을 쓴 시점에 앱에 권한이 부여되어 있었는지 | 권한을 언제 줬거나 거뒀는지(파일에 시각 필드가 없습니다) |
| 사용자가 정했는지, 정책·시스템·기본값·역할로 부여됐는지 | 앱이 그 권한으로 실제로 데이터에 접근했는지 |
| 사용자가 고정(USER_FIXED)해서 다시 묻지 않게 했는지 | 권한을 준 사람이 기기 주인인지 |

권한 모듈이 새 위치 파일에 쓰는 값은 version, fingerprint 와 권한마다 name, granted, flags 뿐이고, 권한을 준 시각이나 거둔 시각은 쓰지 않습니다 [6]. 옛 파일 읽기 코드에도 시각 필드는 없습니다 [1]. 그래서 보고서에는 "이 파일로는 부여 시각을 알 수 없다" 고 쓰고, 파일 자체의 수정 시각은 마지막으로 파일을 다시 쓴 때일 뿐이라서 특정 권한의 부여 시각으로 쓰지 않습니다. 권한을 실제로 쓴 기록은 앱 작업(appops) 쪽 흔적이고, ALEAPP 에는 appops·appOpsAccesses·appOpsModes·permissionAccessState 모듈이 있습니다 [5].

보고서 문장은 "앱이 위치를 추적했다" 가 아니라 "이 파일을 쓴 시점에 이 앱에는 정밀 위치 권한이 부여되어 있었고, flags 에 USER_SET 이 켜져 있었다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 함정과 한계

granted 가 true 여도 REVOKE_ON_UPGRADE(0x8)가 켜져 있으면 실제 접근은 막혀 있고, APPLY_RESTRICTION(0x4000)이 켜져 있으면 보호 데이터 대신 빈 결과를 받습니다 [3]. 그래서 granted 필드 하나만 보고 권한이 유효했다고 쓰지 않고 flags 를 함께 풉니다.

GRANTED_BY_DEFAULT, SYSTEM_FIXED, POLICY_FIXED, GRANTED_BY_ROLE 이 켜진 권한은 사용자가 고른 것이 아니라 기본값·시스템·정책·역할로 부여된 것입니다 [3]. 사용자가 권한을 허용했다고 쓰려면 USER_SET 이나 USER_FIXED 같은 사용자 쪽 비트를 근거로 삼습니다.

ONE_TIME 권한은 앱이 쉬면 자동으로 거두고, AUTO_REVOKED 는 시스템이 거둔 표시라서 [3], 확보 시점에 권한이 없다고 해서 예전에도 없었다고 볼 수는 없습니다. 이 파일은 현재 상태만 적고 이력 필드가 없으니, 한 번 줬다가 거둔 이력은 업그레이드 전 옛 파일이나 다른 기록과 맞춰 봅니다.

## 직접 분석해 보기

### 파일로 따라가기

1. 두 위치의 `runtime-permissions.xml` 을 모두 확보합니다. 옛 위치 파일이 ABX 이면 [안드로이드 바이너리 XML (ABX)](../../../01-foundations/data-formats/abx.md) 페이지의 방법으로 먼저 풉니다.
2. 찾는 앱의 `<package name="...">`(옛 파일은 `<pkg name="...">`)를 열고, 앱이 공유 사용자에 속해 있으면 `<shared-user>` 쪽도 봅니다. 공유 사용자 여부는 [패키지 목록 구조](packages-xml.md) 페이지의 sharedUserId 로 확인합니다.
3. `<permission>`(옛 파일은 `<item>`)마다 name, granted, flags 를 적고 flags 를 위 표로 비트마다 풉니다.

아래는 소스의 쓰기 형식으로 만든 예시이고, 실제 기기에서 나온 값이 아닙니다.

```
<permission name="android.permission.ACCESS_FINE_LOCATION" granted="true" flags="80301" />
0x80301 = 0x80000 SELECTED_LOCATION_ACCURACY
        | 0x00200 USER_SENSITIVE_WHEN_DENIED
        | 0x00100 USER_SENSITIVE_WHEN_GRANTED
        | 0x00001 USER_SET
```

### 공개 도구로 따라가기

ALEAPP 의 runtimePerms 모듈은 두 위치의 파일을 찾아 사용자·앱·권한·granted·flags 를 표로 냅니다 [2]. flags 는 풀지 않고 그대로 나오기 때문에 위 표로 직접 풉니다. 라이브 기기에서는 `dumpsys package` 의 `runtime permissions:` 절이 비트 이름을 붙여 보여 주니, 파일에서 푼 결과와 맞춰 봅니다.

## 교차 검증

- [설치 출처와 설치 시각](install-source-time.md) — 권한을 받은 앱이 언제, 어떤 경로로 설치됐는지
- [기기 관리자와 접근성 권한 (Device Admin·Accessibility)](../../credentials-security/device-admin-accessibility.md) — 함께 확인할 다른 권한 설정
- [앱 사용 기록 (usagestats)](../usagestats/index.md) — 권한을 받은 앱이 실제로 움직였는지
- [몰래 설치된 감시 앱 (Stalkerware)](../../../04-scenarios/incident/stalkerware.md), [악성 앱 흔적 분석 (Malicious App Triage)](../../../03-techniques/analysis/malicious-app-triage/index.md) — 이 기록을 쓰는 조사

## 실습

사용자 데이터가 들어 있는 공개 시험 데이터(NIST CFReDS 등)나 직접 만든 시험 기기의 추출본으로 풀어 봅니다.

1. 옛 위치와 새 위치 가운데 어느 쪽에 파일이 있고, 옛 위치 파일은 ABX 로 저장되어 있습니까?
2. 사용자가 설치한 앱 하나를 골라 권한마다 granted 와 flags 를 적고, 사용자가 직접 정한 권한과 기본으로 받은 권한을 나눠 보십시오.
3. granted 가 true 인데 REVOKE_ON_UPGRADE 나 APPLY_RESTRICTION 이 켜진 권한이 있습니까?
4. 같은 기기의 라이브 `dumpsys package` 출력이 있다면, 파일에서 푼 비트 이름과 출력의 flags 가 같습니까?

## 참고 문헌

1. Settings.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/Settings.java
2. ALEAPP runtimePerms.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/runtimePerms.py
3. PackageManager.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/content/pm/PackageManager.java
4. Xml.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/util/Xml.java
5. ALEAPP scripts/artifacts 목록 — GitHub API, https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
6. RuntimePermissionsPersistenceImpl.java — AOSP packages/modules/Permission (main), https://android.googlesource.com/platform/packages/modules/Permission/+/refs/heads/main/service/java/com/android/permission/persistence/RuntimePermissionsPersistenceImpl.java
7. D20 Forensics, "Android - Roles and Permissions (Android 10/11)", https://blog.d204n6.com/2021/01/android-roles-and-permissions-android.html
