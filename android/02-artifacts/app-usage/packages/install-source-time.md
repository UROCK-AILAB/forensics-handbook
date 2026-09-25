---
title: "설치 출처와 설치 시각"
parent: "설치된 앱"
grand_parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 430
---

# 설치 출처와 설치 시각 (Installer·Install Time)

앱을 누가, 어떤 경로로, 언제 설치했는지 시스템이 남기는 칸을 정리합니다. 소스로 확인한 내용은 현행 AOSP 기준(frameworks/base 의 main 가지)이고, 어느 Android 출시 버전에서 바뀌었는지는 대부분 확인하지 못했습니다. 이 칸들이 들어 있는 파일의 전체 짜임새는 [패키지 목록 구조](packages-xml.md) 페이지에 있습니다.

## 한 줄 요약

설치 출처는 `packages.xml` 의 `<package>` 요소에 설치자·설치 요청 앱·원 출처 같은 여러 칸으로 나뉘어 적히고, 첫 설치 시각과 설치 이유는 현행 AOSP 에서 사용자별 `package-restrictions.xml` 에 적힙니다 [1].

## 무엇을 기록하나 · 왜 생기나

앱을 설치하면 패키지 관리자는 설치를 맡은 앱과 설치를 요청한 앱을 따로 적고, 업데이트 시각과 사용자별 첫 설치 시각을 함께 남깁니다 [1][2]. 앱은 이 값을 InstallSourceInfo 와 PackageInfo 로 받아 보는데, 조사에서는 같은 값을 파일이나 `dumpsys package` 출력으로 읽습니다. 악성 앱이 어디서 들어왔는지, 스토어가 아닌 경로로 설치된 앱이 있는지 볼 때 먼저 확인하는 칸입니다.

## 설치 출처 칸

InstallSourceInfo 의 문서 주석과 Settings 의 쓰기·출력 코드를 맞추면 칸의 대응은 다음과 같습니다 [1][2].

| `packages.xml` 속성 | InstallSourceInfo 이름 | dumpsys 줄 | 뜻 |
|---|---|---|---|
| installer | installingPackageName | `installerPackageName=` | 기록상 설치자 |
| installerUid | | `installerPackageUid=` | 기록상 설치자의 UID |
| installInitiator | initiatingPackageName | `initiatingPackageName=` | 실제로 설치를 요청한 패키지 |
| installOriginator | originatingPackageName | `originatingPackageName=` | 요청 패키지가 누구를 대신해 설치했는지 |
| updateOwner | updateOwnerPackageName | `updateOwnerPackageName=` | 업데이트 소유권이 걸린 앱의 업데이트 주인 |
| installerAttributionTag | | `installerAttributionTag=` | 설치자의 속성 태그 |
| packageSource | packageSource | `packageSource=` | 설치 당시 설치자가 알린 출처 종류 |

설치자(installer)는 `PackageManager#setInstallerPackageName()` 으로 나중에 바뀔 수 있고, 시스템 앱이나 adb 로 설치한 앱, 설치자가 지워진 앱에서는 비어 있을 수 있습니다 [2]. 설치 요청 앱(installInitiator)은 설치자 기록이 바뀌어도 그대로 남지만, 시스템 앱이거나 요청한 앱이 지워졌으면 비어 있을 수 있습니다 [2]. 그래서 두 칸이 다를 때는 설치를 맡은 앱과 요청한 앱이 원래 달랐는지, 설치 뒤에 설치자 기록이 바뀌었는지를 함께 따져 봅니다.

원 출처(installOriginator)는 요청 앱이 알려 주는 값이고 시스템이 검증하지 않습니다 [2]. 예를 들어 내려받은 APK 파일을 패키지 설치 프로그램으로 설치하면, APK 를 내려받은 앱이 이 칸에 들어갈 수 있습니다 [2].

packageSource 는 PackageInstaller.PackageSourceType 값을 정수로 적은 것인데 [2], 숫자와 이름(STORE·LOCAL_FILE·DOWNLOADED_FILE 등)의 대응은 PackageInstaller 소스를 열지 않아 확인하지 못했습니다.

installInitiatorUninstalled 가 true 이면 설치를 요청한 패키지가 그 뒤에 지워졌다는 뜻이고, isOrphaned 는 설치자 기록이 고아가 된 상태를 나타냅니다 [1]. isOrphaned 가 켜지는 정확한 조건은 확인하지 못했습니다. `<package>` 아래 `install-initiator-sigs` 요소에는 설치를 요청한 패키지의 서명이 저장됩니다 [1]. `packages.list` 마지막 칸에도 설치자가 적히는데, 형식은 [패키지 목록 구조](packages-xml.md) 페이지에 있습니다.

### 기기에서 본 설치 관련 앱과 설정 키

`dumpsys package` 의 "Known Packages:" 절에서 Installer 는 `com.google.android.packageinstaller`, Verifier 는 `com.android.vending` 과 `com.samsung.android.sm.devicesecurity`, "Developer verification service provider" 는 `com.google.android.verifier` 였습니다 (확인 범위: Android 16, One UI 8.5). 설치자 칸의 값을 이 목록과 맞춰 보면 기기에 지정된 설치 프로그램이 설치를 맡았는지 가릴 수 있습니다.

설정 값 가운데 settings secure 에 `install_non_market_apps` 키가, settings global 에 `package_verifier_user_consent`, `verifier_timeout`, `verifier_timeout_samsung`, `default_install_location`, `set_install_location`, `upload_apk_enable` 키가 있었습니다 (확인 범위: Android 16, One UI 8.5). 관찰 메모에는 값이 가려져 있고 각 키의 뜻도 확인하지 못했습니다. 설정 값을 읽는 방법은 [설정 값](../../system-account/settings.md) 페이지를 봅니다.

## 설치 시각 칸

| 시각 | 저장 위치 (현행 AOSP 기준) | dumpsys 줄 |
|---|---|---|
| 첫 설치 시각 | 사용자별 `package-restrictions.xml` 의 `<pkg>` 요소 first-install-time(16진수) | `firstInstallTime=` |
| 마지막 업데이트 시각 | `packages.xml` 의 `<package>` 요소 ut(16진수) | `lastUpdateTime=` |
| 마지막 수정 시각 | `packages.xml` 의 `<package>` 요소 ft(16진수) | `timeStamp=` |

첫 설치 시각은 예전에 `packages.xml` 의 `<package>` 요소 it 속성(16진수)에 패키지별로 적었고, 현행 AOSP 는 사용자별로 옮겼습니다. 소스 주석에 "we migrated from per package firstInstallTime to per user-state" 라고 적혀 있습니다 [1]. 사용자별 값이 0(없음)이면 OTA 전 `packages.xml` 의 it 값을 대신 쓰는데, OTA 로 정보가 사라지는 것을 막으려는 코드입니다 [1]. 사용자별로 옮긴 Android 버전은 확인하지 못했습니다. ft 의 뜻은 [패키지 목록 구조](packages-xml.md) 페이지에서 다룹니다.

## 설치 이유와 사용자별 상태

`package-restrictions.xml` 은 `<package-restrictions>` 아래에 앱마다 `<pkg>` 요소를 두고, 켜고 끈 컴포넌트는 `<enabled-components>`·`<disabled-components>` 아래 `<item>` 으로 적습니다 [1]. 사용자별 파일은 `/data/system/users/<사용자ID>/` 아래에 있습니다 [1].

`<pkg>` 요소에 붙는 속성 가운데 설치와 관련된 것은 다음과 같습니다 [1].

| 속성 | 뜻 |
|---|---|
| inst | 이 사용자에게 설치되지 않았으면 false |
| nl | 한 번도 실행하지 않음(not launched) |
| stopped | 멈춘 상태 |
| hidden, suspended, distraction_flags | 숨김·정지 상태 |
| enabled, enabledCaller | 사용 가능 상태와 마지막으로 끈 호출자 |
| instant-app, virtual-preload | 인스턴트 앱, 가상 사전 설치 |
| install-reason | 설치 이유(아래 표) |
| first-install-time | 이 사용자의 첫 설치 시각(16진수) |
| uninstall-reason | 삭제 이유(아래 표) |
| ceDataInode, deDataInode, harmful-app-warning, splash-screen-theme, min-aspect-ratio | 그 밖의 상태 |
| 하위 요소 archive-state | 앱 보관 상태와 archive-time(16진수) |

설치 이유(install-reason)의 값은 PackageManager 에 정의되어 있습니다 [3]. 값이 0 이면 속성을 아예 쓰지 않습니다 [1].

| 값 | 이름 | 뜻 |
|---|---|---|
| 0 | INSTALL_REASON_UNKNOWN | 알 수 없음 |
| 1 | INSTALL_REASON_POLICY | 기업 정책으로 설치 |
| 2 | INSTALL_REASON_DEVICE_RESTORE | 다른 기기에서 복원하며 설치 |
| 3 | INSTALL_REASON_DEVICE_SETUP | 기기 설정 중 설치 |
| 4 | INSTALL_REASON_USER | 사용자가 시작한 설치 |
| 5 | INSTALL_REASON_ROLLBACK | RollbackManager 가 시작한 롤백(@hide) |

삭제 이유(uninstall-reason)는 0 이 UNINSTALL_REASON_UNKNOWN, 1 이 UNINSTALL_REASON_USER_TYPE 입니다 [3]. USER_TYPE 의 뜻은 문서 주석을 확인하지 않아 쓰지 않습니다.

`dumpsys package` 에서는 사용자별로 `installReason=`, `dataDir=`, `firstInstallTime=`, `uninstallReason=` 줄이 찍히고, 보관 상태가 있으면 `archiveTime=`·`unarchiveInstallerTitle=` 줄이 붙습니다 [1]. 관찰 메모에는 패키지별 줄이 생략되어 있어서 실제 폰에서 이 줄의 모양은 확인하지 못했습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 기록상 어느 패키지가 설치를 맡았고 어느 패키지가 요청했는지 | 사람이 직접 설치 버튼을 눌렀다는 것(설치 이유 4 도 "사용자가 시작한" 설치라는 시스템 분류일 뿐입니다) |
| 이 사용자에게 처음 설치된 시각과 마지막 업데이트 시각 | 앱을 실행했다는 것(실행 여부는 nl 속성과 [앱 사용 기록](../usagestats/index.md)으로 봅니다) |
| 복원·기업 정책·기기 설정 중 설치처럼 설치 경로의 분류 | 원 출처(installOriginator)가 사실이라는 것(시스템이 검증하지 않는 값입니다) |

설치자 칸이 비어 있는 것만으로 adb 설치라고 단정하지 않습니다. 시스템 앱이거나 설치자가 지워진 경우에도 비어 있을 수 있기 때문입니다 [2].

## 시각 해석

`packages.xml` 과 `package-restrictions.xml` 의 시각 칸은 16진수 문자열이고, ALEAPP 는 이 값을 유닉스 에포크 밀리초로 보고 UTC 로 바꿉니다 [4]. 바꾸는 계산은 [패키지 목록 구조](packages-xml.md) 페이지의 예시를 따르고, 시각 값 일반은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지를 봅니다. `dumpsys package` 는 시각을 `yyyy-MM-dd HH:mm:ss` 꼴로 찍어서 밀리초가 잘리고 시간대 표시가 없습니다 [1]. 어느 시간대로 찍히는지는 확인하지 못했기 때문에, 파일 값과 한 번 맞춰 본 뒤에 쓰는 편이 안전합니다.

첫 설치 시각은 사용자별로 적기 때문에 같은 앱이라도 사용자마다 다를 수 있습니다 [1]. 설치 이유가 2(복원)인 앱은 이 기기에 복원하며 설치한 앱이라서, 첫 설치 시각을 원래 기기에서 처음 설치한 때로 읽지 않습니다.

## 함정과 한계

ALEAPP 의 packageInfo 는 ft·it·ut 를 "ft", "Install Time", "Update Time" 칸으로 내고, "Install Time" 은 `packages.xml` 의 it 속성입니다 [4]. 현행 AOSP 는 첫 설치 시각을 `package-restrictions.xml` 에 적기 때문에, it 가 없는 새 파일에서는 이 칸이 빌 수 있습니다. 실물로 확인한 것이 아니라 소스에서 나온 추론이라서, 빈칸을 보면 `package-restrictions.xml` 의 first-install-time 을 직접 확인합니다.

설치자 기록은 설치 뒤에 바뀔 수 있고 [2], 원 출처는 요청 앱이 알려 준 값이라서 [2] 두 칸 모두 단독 근거로 쓰지 않습니다. installSessions 라는 ALEAPP 모듈 이름으로 알 수 있듯 설치 세션 기록이 따로 있지만 [5], 파일 경로와 내용은 확인하지 못했습니다.

## 직접 분석해 보기

### 파일로 따라가기

1. `/data/system/packages.xml` 과 `/data/system/users/` 아래 사용자별 `package-restrictions.xml` 을 함께 확보합니다. ABX 로 저장되어 있으면 [안드로이드 바이너리 XML (ABX)](../../../01-foundations/data-formats/abx.md) 페이지의 방법으로 먼저 풉니다.
2. `packages.xml` 에서 찾는 앱의 `<package>` 요소를 열어 installer, installInitiator, installOriginator, packageSource, ut 를 적어 둡니다.
3. 같은 이름의 `<pkg>` 요소를 사용자별 파일에서 찾아 inst, nl, install-reason, first-install-time 을 읽습니다.
4. 16진수 시각을 밀리초로 바꿔 UTC 로 적고, 설치자와 요청 앱이 다르면 둘 다 보고서에 남깁니다.

아래는 명세로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다.

```
<pkg name="com.example.app" install-reason="4" first-install-time="199172c4000" />
install-reason 4 = INSTALL_REASON_USER
0x199172c4000   = 1757030400000 (유닉스 밀리초) = 2025-09-05 00:00:00 UTC
```

### 공개 도구로 따라가기

ALEAPP 의 packageInfo 모듈로 `packages.xml` 을 읽어 설치자와 시각 칸을 표로 봅니다 [4]. ALEAPP 에는 packageRestrictions·packageUserStates·installSessions 모듈도 있지만 [5] 이번에 내용을 열지 않아서, 사용자별 칸은 위의 손 확인 결과와 맞춰 봅니다.

## 교차 검증

- [구글 플레이 기록 (Play Store)](../play-store.md) — 설치자가 스토어일 때 스토어 쪽 설치 기록
- [APK 정보 (AndroidManifest·서명)](../../embedded-metadata/apk.md) — 설치된 APK 의 서명과 `install-initiator-sigs` 비교
- [공용 저장 공간 (Shared Storage·/sdcard)](../../../01-foundations/storage/shared-storage.md) — 내려받은 APK 파일이 남았는지
- [악성 앱은 어디서 들어왔나 (Initial Access)](../../../04-scenarios/incident/initial-access.md), [몰래 설치된 감시 앱 (Stalkerware)](../../../04-scenarios/incident/stalkerware.md) — 이 칸을 쓰는 조사 시나리오

## 실습

`/data/system/` 폴더가 들어 있는 공개 검체(NIST CFReDS 등)나 직접 만든 시험 기기의 추출본으로 풀어 봅니다.

1. 사용자가 설치한 앱 가운데 installer 와 installInitiator 가 서로 다른 앱이 있습니까?
2. installer 가 비어 있는 앱은 시스템 앱입니까, 아니면 다른 이유가 보입니까?
3. `packages.xml` 에 it 속성이 남아 있습니까? 남아 있다면 사용자별 first-install-time 과 같습니까?
4. install-reason 이 2(복원)인 앱의 첫 설치 시각은 기기 설정 시기와 어떤 관계입니까?

## 참고 문헌

1. Settings.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/Settings.java
2. InstallSourceInfo.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/content/pm/InstallSourceInfo.java
3. PackageManager.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/content/pm/PackageManager.java
4. ALEAPP packageInfo.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/packageInfo.py
5. ALEAPP scripts/artifacts 목록 — GitHub API, https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
