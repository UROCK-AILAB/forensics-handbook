---
title: "앱 샌드박스와 권한"
parent: "기반 · 보안 구조"
nav_order: 270
---

# 앱 샌드박스와 권한 (Sandbox·Permissions)

Android 는 앱마다 고유한 리눅스 사용자 ID(UID)를 주고 커널이 그 경계를 지키게 해서 앱끼리 데이터를 나누고, 앱이 경계 밖의 자원을 쓰려면 권한을 받아야 하며 그 부여 상태가 기기에 파일로 남습니다.

## 이 구조가 드러나는 아티팩트

샌드박스는 앱 데이터가 어디에 어떻게 나뉘어 저장되는지를 정하고, 권한은 앱이 무엇에 손댈 수 있었는지를 정합니다. 그래서 [앱 데이터 폴더 구조](../storage/app-data-layout.md), [공용 저장 공간](../storage/shared-storage.md), [설치된 앱](../../02-artifacts/app-usage/packages/index.md), [기기 관리자와 접근성 권한](../../02-artifacts/credentials-security/device-admin-accessibility.md) 페이지를 읽을 때 이 페이지의 내용을 바탕으로 삼습니다. 악성 앱이 어떤 권한을 받았는지 따지는 흐름은 [악성 앱 흔적 분석](../../03-techniques/analysis/malicious-app-triage/index.md) 과 [몰래 설치된 감시 앱](../../04-scenarios/incident/stalkerware.md) 페이지에서 다룹니다.

## 샌드박스가 나누는 방식

Android 는 앱마다 고유한 UID 를 주고 앱을 자기 프로세스 안에서 실행하며, 이 격리는 커널이 리눅스의 사용자·그룹 ID 로 강제합니다. 한 기기에 사용자나 프로필이 여럿이면 같은 앱이라도 사용자마다 UID 가 달라지고, 식은 아래와 같습니다.

```
UID = 100000 × userid + appid
```

앱 데이터도 사용자마다 `/data/user/<userid>` 아래에 따로 두기 때문에, 같은 앱이 주 사용자와 작업 프로필에 모두 설치되어 있으면 데이터가 두 벌로 나뉩니다. 폴더가 실제로 어떻게 놓이는지는 [앱 데이터 폴더 구조](../storage/app-data-layout.md) 페이지를, 로그에 찍힌 UID 를 패키지 이름으로 되돌리는 법은 [패키지 이름과 UID](../value-decoding/package-uid.md) 페이지를 봅니다.

## 버전별로 강화된 점

샌드박스는 UID 로 나누는 방식(DAC, 임의 접근 제어) 위에 버전마다 장치가 하나씩 더해졌습니다. 아래 표는 Android 공식 문서의 앱 샌드박스 설명을 옮긴 것입니다.

| 버전 | 바뀐 점 |
|---|---|
| Android 5.0 | SELinux 가 강제 접근 제어(MAC)로 시스템과 앱 사이를 나눔. 다만 서드파티 앱은 모두 같은 SELinux 문맥을 써서 앱끼리 격리는 주로 UID 에 기댐 |
| Android 6.0 | SELinux 격리가 물리 사용자 경계까지 넓어짐 |
| targetSdkVersion 24 이상 앱 | 앱 홈 디렉터리의 기본 권한이 751 에서 700 으로 바뀜 |
| Android 8.0 | 모든 앱이 seccomp-bpf 필터 아래에서 실행되어 쓸 수 있는 시스템 호출이 제한됨 |
| Android 9 | targetSdkVersion 28 이상인 비특권 앱은 앱마다 따로 SELinux 샌드박스에서 실행 |
| Android 10 | 앱은 파일 시스템을 제한적으로만 봄. `/sdcard/DCIM` 같은 경로에 직접 접근하지 못하고 자기 패키지 전용 경로에는 전부 접근 |

Android 10 이후 저장소 런타임 권한은 MediaStore 를 거쳐 사진·동영상 같은 유형별 모음에 접근하는 것을 제어하고, PDF 같은 파일은 `ACTION_OPEN_DOCUMENT` 같은 인텐트로 사용자가 고른 것만 엽니다. MediaStore 쪽 기록은 [미디어 저장소](../../02-artifacts/media/mediastore/index.md) 페이지에서 다룹니다. Android 11 이후 저장소 권한의 세부 변화와 일회성 권한, 쓰지 않는 앱의 권한 자동 회수는 이번 판에서 공식 문서로 확인하지 못해 다루지 않습니다.

## 런타임 권한이 남는 파일

사용자가 앱에 허용하거나 거부한 런타임 권한은 `runtime-permissions.xml` 에 저장되고, 쓰는 도중 문제가 생길 때를 대비해 `runtime-permissions.xml.reservecopy` 라는 예비 사본도 함께 둡니다(현행 AOSP 기준). 파일이 놓이는 곳은 권한 APEX 모듈(`com.android.permission`)의 사용자별 기기 보호(DE) 데이터 디렉터리입니다. 소스는 이 디렉터리를 APEX 환경 API 로 얻고, 이 API 는 `/data/misc_de/<userid>` 아래 `apexdata/<모듈 이름>` 을 돌려주기 때문에 경로는 `/data/misc_de/<userid>/apexdata/com.android.permission/runtime-permissions.xml` 이 됩니다(현행 AOSP 소스로 조립한 경로이고, 기기에서 직접 확인하지는 않았습니다). DE 영역이 무엇인지는 [저장 공간 암호화](../storage/encryption/index.md) 페이지를 봅니다.

소스가 쓰는 태그와 속성은 아래와 같습니다. 이 예시는 소스의 이름으로 짠 모양일 뿐이고, 실제 기기에서 꺼낸 것이 아니라서 값은 모두 자리 표시입니다.

```xml
<runtime-permissions version="…" fingerprint="…">
  <package name="패키지 이름">
    <permission name="권한 이름" granted="true" flags="16진 정수" />
  </package>
  <shared-user name="공유 사용자 이름">
    <permission name="권한 이름" granted="false" flags="16진 정수" />
  </shared-user>
</runtime-permissions>
```

| 태그 | 속성 | 뜻 |
|---|---|---|
| `runtime-permissions` | `version`, `fingerprint` | 파일 전체의 머리 |
| `package`, `shared-user` | `name` | 권한을 받은 패키지 또는 공유 UID 이름 |
| `permission` | `name`, `granted`, `flags` | 권한 이름, 허용 여부(참·거짓), 상태 플래그(16진 정수) |

Android 14 부터는 본 파일과 예비 사본 둘 다에 fs-verity 보호가 걸립니다. 현행 소스는 일반 XML 직렬화기(`Xml.newSerializer()`)로 쓰기 때문에 텍스트 XML 로 남고, 다른 권한 파일에서 바이너리 XML 을 만나면 [안드로이드 바이너리 XML](../data-formats/abx.md) 페이지대로 읽습니다. Android 10 이전의 옛 위치, 설치 시 권한이 함께 적히는 패키지 목록 파일, 앱옵스 기록 파일의 경로도 이번 판에서 확인하지 못했습니다.

## 기기에서 보이는 설치·검증 흔적

adb 일반 셸 권한으로 `dumpsys package` 를 읽으면 "Known Packages" 절에 역할별 담당 패키지가 나오고, 권한 화면을 맡는 패키지는 `Permission Controller:` 아래에 `com.google.android.permissioncontroller` 로 나옵니다. 같은 절의 `Installer:` 는 `com.google.android.packageinstaller` 이고, `Verifier:` 아래에는 `com.android.vending` 과 `com.samsung.android.sm.devicesecurity` 가 함께 나옵니다.

```
Known Packages:
  Installer:
    com.google.android.packageinstaller
  Verifier:
    com.android.vending
    com.samsung.android.sm.devicesecurity
  Permission Controller:
    com.google.android.permissioncontroller
```

위 출력은 관찰 메모에서 필요한 줄만 옮긴 것입니다. 관찰 기기에는 시스템 앱 486개와 사용자가 설치한 앱 168개가 있었고, 이 숫자는 한 번 관찰한 시점의 값입니다.

설정 값에는 앱 설치 출처와 설치 검증에 이름이 이어지는 키가 있고, 값은 가려서 확인하지 않았습니다.

| 설정 표 | 키 |
|---|---|
| secure | `install_non_market_apps`, `unknown_sources_default_reversed` |
| global | `package_verifier_user_consent`, `verifier_timeout`, `verifier_timeout_samsung`, `upload_apk_enable` |
| secure | `appprotection_package_uid`, `appprotection_auto_scan_updated`, `appprotection_permission_function_usage` 등 `appprotection_permission_` 으로 시작하는 키 6개 |
| secure | `rampart_blocked_adb_cmd`, `rampart_blocked_unknown_apps`, `rampart_snapshot_adb_enabled` 등 `rampart_` 으로 시작하는 키 |

`appprotection_` 키는 이름으로 보아 삼성의 앱 검사 기능 설정으로 보이고, `rampart_` 키는 삼성의 자동 차단(Auto Blocker) 기능과 이름이 이어져 보이지만, 둘 다 공식 문서로 뜻을 확인하지 못했습니다. 설정 값을 읽는 법은 [설정 값](../../02-artifacts/system-account/settings.md) 페이지를, dumpsys 출력을 읽는 법은 [dumpsys 출력](../../02-artifacts/logs/dumpsys.md) 페이지를 봅니다.

## 포렌식에서 중요한 점

아래는 공식 문서와 소스에서 끌어낸 해석이고, 문서에 이 문장 그대로 있지는 않습니다.

앱 데이터는 앱마다, 또 사용자마다 따로 놓이고, 한 앱의 데이터를 찾을 때는 주 사용자 폴더만 보지 말고 기기에 있는 모든 사용자와 프로필의 폴더를 함께 봐야 합니다. 프로필이 있는지 확인하는 법은 [보안 폴더와 작업 프로필](secure-folder-work-profile.md) 페이지에서 다룹니다.

`runtime-permissions.xml` 은 파일을 마지막으로 쓴 시점에 어떤 권한이 허용된 상태였는지를 보여 주지만, 소스가 쓰는 속성 가운데 시각을 적는 칸은 없어서 권한을 언제 허용했는지는 이 파일만으로 알 수 없습니다. 허용 시각은 시각이 남는 다른 기록에서 따로 찾아야 하고, 여러 기록을 한 줄로 맞추는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 페이지에서 다룹니다. 예비 사본도 본 파일과 함께 수집해 둡니다.

## 함정

권한 파일의 경로를 다른 자료에서 옮겨 적을 때는 조심합니다. 위 경로는 현행 AOSP 소스로 조립한 것이라 버전과 제조사에 따라 다를 수 있고, Android 10 이전의 옛 위치는 확인하지 못했습니다. 보고서에는 확인한 기기와 버전에서 실제로 찾은 경로를 적습니다.

권한 화면을 맡는 패키지 이름은 기기마다 다를 수 있어서, 관찰 기기의 `com.google.android.permissioncontroller` 를 모든 기기의 이름으로 보면 안 됩니다. 이 이름은 `dumpsys package` 의 Known Packages 절에서 기기마다 확인합니다.

설정 키가 있다는 것은 그 기능이 기기에 들어 있다는 뜻일 뿐이고, 사용자가 그 기능을 켰거나 썼다는 뜻은 아닙니다. 값과 그 뜻을 함께 확인하기 전에는 보고서에 기능 사용 여부를 쓰지 않습니다.

## 도구

기기에서 직접 확인할 때는 adb 의 `dumpsys package` 와 `settings list global`·`settings list secure` 를 씁니다. 일반 셸 권한으로는 역할별 담당 패키지와 설정 키를 볼 수 있지만, DE 데이터 디렉터리 안의 `runtime-permissions.xml` 은 수집한 파일 시스템 이미지에서 읽습니다. 수집 방식별로 얻을 수 있는 범위는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지를 봅니다.

## 참고 문헌

1. Application Sandbox — Android Open Source Project — https://source.android.com/docs/security/app-sandbox
2. Work profiles (Managed profiles) — Android Open Source Project — https://source.android.com/docs/devices/admin/managed-profiles
3. RuntimePermissionsPersistenceImpl.java (AOSP packages/modules/Permission, main) — https://android.googlesource.com/platform/packages/modules/Permission/+/refs/heads/main/service/java/com/android/permission/persistence/RuntimePermissionsPersistenceImpl.java
4. ApexEnvironment.java (AOSP frameworks/base, main) — https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/content/ApexEnvironment.java
5. Environment.java (AOSP frameworks/base, main) — https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/os/Environment.java
