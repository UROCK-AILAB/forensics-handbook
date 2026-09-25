---
title: "기기 관리자와 접근성 권한"
parent: "아티팩트 · 자격 증명·보안 설정"
nav_order: 1250
---

# 기기 관리자와 접근성 권한 (Device Admin·Accessibility)

## 한 줄 요약

기기 관리자 (Device Admin) 는 앱이 잠금·초기화·비밀번호 정책을 다룰 수 있게 하는 권한이고 접근성 서비스 (Accessibility Service) 는 앱이 화면 내용을 읽고 사용자 대신 조작할 수 있게 하는 권한이라서, 조사에서는 어느 앱이 이 둘을 켜 두었는지를 시스템 쪽 `device_policies.xml` 과 settings secure 의 접근성 키에서 확인합니다 [1][2][4].

## 무엇을 기록하나 · 왜 생기나

### 기기 관리자

기기 관리자 앱은 `DeviceAdminReceiver` 를 이어받은 receiver 를 매니페스트에 선언하고, 이 receiver 가 쓸 정책을 별도 XML 에 적습니다 [1]. 앱이 `ACTION_ADD_DEVICE_ADMIN` 인텐트로 활성화 화면을 띄우고 사용자가 허용해야 정책이 적용되며, 허용하지 않으면 앱은 정책 없이 비활성 상태로 남습니다 [1]. 활성 기기 관리자 앱은 관리자를 먼저 해제해야 삭제할 수 있다고 문서에 적혀 있어서 [1], 지워지지 않는 앱이 있으면 기기 관리자인지부터 확인해 볼 만합니다.

정책 XML 에 적을 수 있는 정책과 문서상 뜻은 아래와 같습니다 [1].

| 정책 태그 | 뜻 |
|---|---|
| `force-lock` | 즉시 잠금, 최대 비활동 시간 |
| `wipe-data` | 공장 초기화 |
| `reset-password` | 새 비밀번호 설정 요구 |
| `limit-password` | 비밀번호 조건 |
| `expire-password` | 비밀번호 만료 |
| `encrypted-storage` | 저장소 암호화 요구 |
| `disable-camera` | 카메라 끄기 |
| `watch-login` | 문서의 정책 XML 예에 있으나 이번에 뜻은 따로 확인하지 않음 |

활성화되면 시스템은 관리자 목록을 사용자마다 `device_policies.xml` 에 적습니다 [3][4]. 앱 쪽에서는 `onEnabled`, `onDisableRequested`, `onDisabled`, `onPasswordChanged`, `onPasswordFailed` 콜백을 받고, 시스템은 `ACTION_DEVICE_ADMIN_ENABLED`, `ACTION_DEVICE_ADMIN_DISABLE_REQUESTED` 방송을 보냅니다 [1]. 이 콜백을 받은 앱이 자기 데이터에 무엇을 남기는지는 앱마다 다릅니다.

### 접근성 서비스

접근성 서비스는 장애 등으로 기기를 다루기 어려운 사용자를 돕는 앱이고, 백그라운드에서 돌며 화면 내용을 살피고 사용자 대신 앱과 상호작용합니다 [2]. TalkBack, Switch Access, 음성 제어가 대표적인 예입니다 [2]. 문서에 적힌 능력은 창 내용 관찰(접근성 트리), 스와이프·탭·멀티터치 같은 제스처 실행, 키 이벤트 처리, 버튼 누르기·스크롤 같은 동작 수행이고 [2], 사용자가 설정에서 직접 켜야 돌아갑니다 [2]. 어떤 앱이 켜 두었는지는 settings secure 의 접근성 키에 남습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5).

## 위치와 버전별 차이

### 앱 쪽 선언 (APK)

두 권한 모두 APK 의 매니페스트에 선언이 있어야 켤 수 있습니다. APK 를 읽는 법은 [APK 정보 (AndroidManifest·서명)](../embedded-metadata/apk.md) 페이지에서 다룹니다.

| 권한 | 매니페스트 조건 | 가리키는 설정 XML |
|---|---|---|
| 기기 관리자 | receiver 에 `android:permission="android.permission.BIND_DEVICE_ADMIN"`, intent-filter action `android.app.action.DEVICE_ADMIN_ENABLED` [1] | meta-data `android.app.device_admin` → `<device-admin>` 아래 `<uses-policies>` [1] |
| 접근성 서비스 | service 에 `android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE"`, intent-filter action `android.accessibilityservice.AccessibilityService` [2] | meta-data `android.accessibilityservice` → `<accessibility-service>` [2] |

### 시스템 쪽 기록

기기 관리자 목록은 `device_policies.xml` 파일에 있고, 소스의 상수 이름은 `DEVICE_POLICIES_XML` 입니다 [4]. 파일은 사용자마다 따로 있고 어느 폴더에 두는지는 소스의 PolicyPathProvider 가 정합니다(현행 AOSP main) [4][5]. 기본값은 시스템 사용자(0 번)가 `/data/system`, 다른 사용자가 `/data/system/users/<사용자 번호>` 이고, 소스 주석에 따르면 기기 소유자 (Device Owner) 파일도 `/data/system` 에, 프로필 소유자 (Profile Owner) 파일은 사용자 폴더에 둡니다 [5]. 그래서 기본 사용자의 파일은 `/data/system/device_policies.xml` 이고, 제조사가 경로를 바꿨을 수 있으니 전체 파일 시스템 사본에서는 파일 이름으로도 한 번 찾습니다. 사용자와 프로필 구조는 [사용자와 프로필 (Multi-user·users)](../system-account/users-profiles.md) 페이지에서 다룹니다.

접근성 설정은 관찰 기기의 settings secure 에 아래 이름의 키로 있었고, 값은 관찰 메모에서 가려져 있습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5).

```
accessibility_enabled
enabled_accessibility_services
accessibility_shortcut_target_service
accessibility_button_mode
accessibility_gesture_targets
accessibility_qs_targets
notified_non_accessibility_category_services
```

이 밖에 확대(magnification)·자막(captioning) 관련 키도 있었습니다. `enabled_accessibility_services` 값이 "패키지/서비스 클래스" 를 `:` 로 이은 문자열이라는 설명은 이번에 문서로 확인하지 못했습니다. 설정 값의 저장 파일과 읽는 법은 [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) 페이지에서 다룹니다.

### 버전별 차이

| 범위 | 차이 |
|---|---|
| Android 9 (API 28) 이후 | 기기 관리자가 일부 정책을 호출하면 사용 중단(deprecated)으로 표시됨 [1]. 어느 정책인지와 Android 10 에서의 동작은 확인하지 못함 |
| Android 14 이후, Headless System User 모드 | 전역 범위 정책만 전면 사용자에게 적용됨 [1] |
| 삼성 One UI | 접근성·기기 관리자 설정 화면 위치와 삼성만의 추가 기록은 확인하지 못함 |

## 구조

### device_policies.xml

활성 관리자 한 개가 `<admin>` 태그 하나로 저장되고, `name` 속성에 컴포넌트 이름이 "패키지/클래스" 모양으로 들어갑니다 [3]. 관리자별 정책은 그 아래에 따로 쓰지만, 하위 태그 이름은 이번에 확인하지 못했습니다. 아래는 소스의 태그 이름으로 만든 모양 예시이고, 실제 검체에서 가져온 값이 아닙니다.

```xml
<admin name="com.example.app/com.example.app.AdminReceiver">
  ... (관리자별 정책, 하위 태그 이름은 확인하지 못함)
</admin>
```

소스에 상수로 정의된 다른 태그 이름은 아래와 같습니다 [3]. 태그마다 무엇을 담는지는 이름 말고는 확인하지 않았습니다.

```
accepted-ca-certificate        lock-task-component         lock-task-features
statusbar                      apps-suspended              secondary-lock-screen
do-not-ask-credentials-on-boot affiliation-id              last-security-log-retrieval
last-bug-report-request        last-network-log-retrieval  admin-broadcast-pending
current-ime-set                owner-installed-ca-cert     initialization-bundle
password-token                 protected-packages          bypass-role-qualifications
keep-profiles-running
```

속성 이름으로는 `value`, `alias`, `id`, `permission-provider`, `name`, `disabled`, `setup-complete`, `provisioning-state`, `permission-policy`, `device-provisioning-config-applied`, `device-paired`, `new-user-disclaimer`, `factory-reset-flags`, `factory-reset-reason` 이 있습니다 [3]. `accepted-ca-certificate` 와 `owner-installed-ca-cert` 는 인증서 쪽 기록이라서 [설치된 인증서 (User Certificates)](user-certificates.md) 페이지에서 함께 봅니다. 파일이 텍스트 XML 로 열리지 않으면 [안드로이드 바이너리 XML (ABX)](../../01-foundations/data-formats/abx.md) 페이지를 봅니다.

기기 소유자·프로필 소유자 정보는 위 폴더에 따로 저장되지만 [5], 그 파일 이름은 이번에 확인하지 못했습니다. 관찰 기기의 `dumpsys user` 에는 사용자마다 `Has profile owner`, `Device policy restrictions`, `Effective restrictions` 줄이 있었고, UserProperties 안에 `mInheritDevicePolicy` 칸이 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 이 줄로 프로필 소유자 유무와 정책에서 나온 제한을 사용자 단위로 볼 수 있습니다. `dumpsys device_policy` 출력의 모양은 이번에 확인하지 못했습니다.

### 접근성 서비스 설정 XML

APK 안의 `<accessibility-service>` XML 에는 아래 속성이 올 수 있고, 이 속성을 보면 서비스가 어떤 능력을 요청했는지 알 수 있습니다 [2].

| 속성 | 뜻 |
|---|---|
| `accessibilityEventTypes` | 받을 이벤트 종류. `typeAllMask` 면 모든 이벤트 |
| `accessibilityFlags`, `accessibilityFeedbackType`, `notificationTimeout` | 문서 예에 나오지만 뜻은 따로 확인하지 않음 |
| `canRetrieveWindowContent` | 화면 구조를 읽으려면 `true` 여야 함 |
| `canPerformGestures` | 제스처를 보내려면 `true` 여야 함 |
| `settingsActivity` | 문서 예에 나오지만 뜻은 따로 확인하지 않음 |

## 증거로서 의미

**증명하는 것**

`device_policies.xml` 에 `<admin>` 이 있으면 그 파일을 쓸 때 해당 컴포넌트가 활성 기기 관리자였다는 뜻이고, APK 의 정책 XML 을 함께 보면 그 앱이 초기화·잠금·비밀번호 정책 가운데 무엇을 요청했는지 알 수 있습니다. 문서상 사용자가 허용해야 활성화되니 [1], 활성 상태라면 기기에서 누군가 허용 화면을 거쳤다고 볼 수 있습니다. 접근성 쪽도 사용자가 설정에서 켜야 돌아가니 [2], `enabled_accessibility_services` 에 어떤 서비스가 있으면 그 기기에서 누군가 켰다는 기록이 되고, 설정 XML 에 `canRetrieveWindowContent="true"` 가 있으면 그 서비스가 화면 구조를 읽을 수 있게 선언돼 있다는 뜻입니다.

**증명하지 못하는 것**

두 기록 모두 누가 허용했는지는 알려 주지 않고, 언제 켰는지도 이번에 확인한 범위에서는 파일 안에 남지 않습니다. 능력을 선언했다는 사실은 그 능력을 실제로 썼다는 증거가 아니라서, 화면을 읽었다거나 제스처를 보냈다고 쓰려면 앱 자체의 데이터나 로그 같은 다른 기록이 필요합니다. 기기 관리자나 접근성 권한을 쓰는 앱이 곧 악성 앱이라는 뜻도 아닙니다. TalkBack 같은 보조 앱도 접근성 권한을 쓰고 [2], 기기 관리자 정책도 문서상 비밀번호·잠금을 관리하려고 만든 기능입니다 [1].

현재 설정만 보이니, 한때 켰다가 끈 앱은 이 두 곳에서 드러나지 않을 수 있습니다. 관리자 앱 패키지가 사라지면 서비스가 "Admin package %s not found for user %d, removing active admin" 로그를 남기고 활성 관리자에서 뺀다는 코드가 있어서 [4], 로그가 남아 있다면 사라진 관리자 앱의 단서가 됩니다. 이 로그가 logcat 에 어느 태그로 찍히는지는 확인하지 못했습니다.

## 시각 해석

`<admin>` 태그에 활성화 시각이 들어 있다고 확인하지는 못했습니다. `last-security-log-retrieval` 같은 시각 값은 long 으로 저장하지만 [3] 단위가 밀리초인지는 확인하지 못했으니, 날짜로 바꿀 때는 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지의 방법으로 여러 단위를 시험하고 기기의 다른 기록과 맞춰 봅니다.

활성화 시점을 가늠할 때는 `device_policies.xml` 파일의 수정 시각, 앱 설치 시각, 설정 화면을 연 기록을 모아 보는 방법이 있지만, 파일 수정 시각은 관리자 추가 말고 다른 정책 변경으로도 바뀔 수 있다고 보고 추정으로만 씁니다. 접근성 설정의 시각도 같은 이유로 설정 파일 수정 시각만으로 정하지 않습니다.

## 함정과 한계

첫째, `device_policies.xml` 은 사용자마다 따로 있어서 `/data/system` 한 곳에서 관리자를 못 찾았다고 기기 전체에 기기 관리자가 없다고 결론 내리면 안 되고, `/data/system/users/` 아래 사용자 폴더도 모두 봅니다 [5]. 기기 소유자 파일의 이름은 이번에 확인하지 못했습니다.

둘째, 관찰 기기의 접근성 키 값은 가려져 있었습니다. 키가 있다는 사실은 서비스가 켜져 있다는 뜻이 아니고, 값을 직접 읽어야 합니다.

셋째, Android 13 의 "제한된 설정" 과 `isAccessibilityTool` 속성은 이번에 연 문서에 나오지 않아 다루지 않습니다.

넷째, 삼성 One UI 에서 기기 관리자·접근성에 관한 추가 기록이 있는지는 확인하지 못했습니다. 녹스 구조는 [삼성 녹스 (Samsung Knox)](../../01-foundations/security-model/samsung-knox.md), 작업 프로필은 [보안 폴더와 작업 프로필 (Secure Folder·Work Profile)](../../01-foundations/security-model/secure-folder-work-profile.md) 페이지에서 다룹니다.

## 직접 분석해 보기

### 설정 키와 dumpsys 로 한 번

adb 일반 셸 권한으로 settings secure 목록과 `dumpsys user` 를 읽을 수 있고, 관찰 기기의 키 이름과 줄 모양도 이렇게 얻었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5).

```
adb shell settings list secure
adb shell dumpsys user
```

settings 출력에서 `enabled_accessibility_services`, `accessibility_enabled`, `accessibility_shortcut_target_service` 값을 기록하고, `dumpsys user` 에서 사용자마다 `Has profile owner` 와 `Device policy restrictions` 줄을 기록합니다. dumpsys 출력의 일반 성질은 [dumpsys 출력 (dumpsys)](../logs/dumpsys.md) 페이지에서 다룹니다.

### 파일과 APK 로 한 번

전체 파일 시스템 사본이 있으면 `device_policies.xml` 을 찾아 `<admin name="...">` 값을 모두 적고, 텍스트로 열리지 않으면 ABX 로 풀어 읽습니다. 그다음 `name` 속성과 `enabled_accessibility_services` 값에 나온 패키지의 APK 를 apktool 같은 공개 도구로 풀어, 매니페스트에서 `BIND_DEVICE_ADMIN`·`BIND_ACCESSIBILITY_SERVICE` 선언과 meta-data 가 가리키는 XML 을 찾고 요청한 정책과 능력을 표로 정리합니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [설치된 앱 (packages.xml)](../app-usage/packages/index.md) | 관리자·접근성 앱의 설치 시각, 설치 경로, 설치한 앱 |
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | 활성화 무렵 설정 앱이나 해당 앱이 화면에 올라왔는지 |
| [logcat (logcat)](../logs/logcat.md) | 관리자 추가·제거와 관련된 로그가 남아 있는지 |
| [잠금 화면 설정 (Lock Settings)](../system-account/lock-settings.md) | 비밀번호 정책을 요청한 관리자가 있을 때 잠금 설정이 바뀌었는지 |
| [초기화 흔적 (Factory Reset)](../system-account/factory-reset.md) | `wipe-data` 정책을 요청한 관리자가 있을 때 초기화 흔적이 있는지 |

조사 흐름은 [악성 앱 흔적 분석 (Malicious App Triage)](../../03-techniques/analysis/malicious-app-triage/index.md), [몰래 설치된 감시 앱 (Stalkerware)](../../04-scenarios/incident/stalkerware.md), [악성 앱은 어디서 들어왔나 (Initial Access)](../../04-scenarios/incident/initial-access.md) 에서 다룹니다. 권한 체계 전반은 [앱 샌드박스와 권한 (Sandbox·Permissions)](../../01-foundations/security-model/sandbox-permissions.md) 페이지에 있습니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 검체에서 아래 질문을 풀어 봅니다.

1. 검체에 `device_policies.xml` 이 있습니까? 있다면 `<admin>` 이 몇 개이고, `name` 속성의 패키지는 무엇입니까?
2. 그 패키지의 APK 정책 XML 에서 요청한 정책은 무엇이고, 그 가운데 `wipe-data` 나 `force-lock` 이 있습니까?
3. settings secure 의 `enabled_accessibility_services` 값에는 어떤 서비스가 있고, 각 서비스의 설정 XML 에서 `canRetrieveWindowContent` 와 `canPerformGestures` 값은 무엇입니까?
4. 관리자·접근성 앱의 설치 시각과 `device_policies.xml` 파일 수정 시각은 얼마나 떨어져 있습니까?

## 참고 문헌

1. Device administration overview — Android Developers — https://developer.android.com/work/device-admin
2. Create your own accessibility service — Android Developers — https://developer.android.com/guide/topics/ui/accessibility/service
3. DevicePolicyData.java (AOSP frameworks/base, main) — https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/services/devicepolicy/java/com/android/server/devicepolicy/DevicePolicyData.java
4. DevicePolicyManagerService.java (AOSP frameworks/base, main) — https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/services/devicepolicy/java/com/android/server/devicepolicy/DevicePolicyManagerService.java
5. PolicyPathProvider.java (AOSP frameworks/base, main) — https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/services/devicepolicy/java/com/android/server/devicepolicy/PolicyPathProvider.java
