---
title: "패키지 목록 구조"
parent: "설치된 앱"
grand_parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 420
---

# 패키지 목록 구조 (packages.xml·packages.list)

패키지 관리자(PackageManager)가 `/data/system/` 에 남기는 설치 앱 목록 파일의 짜임새를 정리합니다. 내용은 현행 AOSP 기준(frameworks/base 의 main 가지)이고, 출시 버전마다 다를 수 있습니다. 설치자와 설치 시각 칸의 뜻은 [설치 출처와 설치 시각](install-source-time.md) 페이지에서, 사용자가 준 권한은 [앱 권한 부여 기록](runtime-permissions.md) 페이지에서 다룹니다.

## 한 줄 요약

`packages.xml` 은 기기에 설치된 앱마다 이름·코드 경로·버전·설치자·시각·서명을 한 요소에 적는 설정 파일이고, `packages.list` 는 같은 목록을 한 줄에 한 앱씩 공백으로 나눠 적은 요약본입니다 [1].

## 무엇을 기록하나 · 왜 생기나

패키지 관리자는 설치된 앱의 설정을 이 파일에 적어 두고, 설치된 앱 목록과 함께 업데이트된 시스템 앱의 원래 판과 이름이 바뀐 패키지 기록도 남깁니다 [1]. 사용자마다 다른 상태(그 사용자에게 설치됐는지, 첫 설치 시각, 설치 이유 등)는 이 파일이 아니라 사용자별 `package-restrictions.xml` 에 따로 적습니다 [1]. 그 파일의 칸은 [설치 출처와 설치 시각](install-source-time.md) 페이지에서 설명합니다.

## 위치와 버전별 차이

현행 AOSP 의 Settings 클래스가 `/data/system/` 아래에 두는 파일은 다음과 같습니다 [1].

| 파일 | 담긴 것 |
|---|---|
| `packages.xml` | 설치 앱 전체 목록(본 파일) |
| `packages-backup.xml` | 이전판 사본 |
| `packages.xml.reservecopy` | 예비 사본 |
| `packages.list` | 한 줄에 한 앱씩 적은 요약 목록 |
| `packages-stopped.xml`, `packages-stopped-backup.xml` | 소스에 "Deprecated: Needed for migration" 으로 남아 있고, 내용을 옮긴 뒤 지웁니다 |

`packages-backup.xml` 과 `packages.xml.reservecopy` 는 ResilientAtomicFile 이 쓰는 사본이라서 본 파일과 시점이 다를 수 있습니다 [1].

현행 AOSP 는 이 설정 파일들을 `Xml.resolveSerializer()` 로 쓰고, 시스템 속성 `persist.sys.binary_xml` 의 기본값이 true 라서 기본적으로 안드로이드 바이너리 XML(ABX) 형식으로 저장합니다 [1][2]. 읽을 때는 파일 앞 바이트를 보고 ABX 인지 일반 XML 인지 가리기 때문에, 두 형식이 섞여 있어도 시스템은 둘 다 읽습니다 [2]. ABX 형식은 [안드로이드 바이너리 XML (ABX)](../../../01-foundations/data-formats/abx.md) 페이지에서 다룹니다.

`packages.list` 는 권한 0640, 소유자 SYSTEM_UID, 그룹 PACKAGE_INFO_GID 로 만들어집니다 [1].

## 구조 — packages.xml

### 큰 틀

뿌리 요소는 `<packages>` 이고, 현행 AOSP 의 쓰기 코드(writeLPr)는 아래 순서로 요소를 적습니다 [1].

| 요소 | 담긴 것 |
|---|---|
| `<version>` | 저장소(volumeUuid)마다 하나씩 있고, 속성은 volumeUuid, sdkVersion, databaseVersion, buildFingerprint, fingerprint 입니다 |
| `<verifier device="...">` | 검증기 기기 식별자이고, 값이 있을 때만 씁니다 |
| `<permission-trees>`, `<permissions>` | 앱이 선언한 권한 트리와 권한 목록 |
| `<package>` | 설치된 앱 하나 |
| `<updated-package>` | 업데이트된 시스템 앱의 원래(비활성화된) 시스템판 기록 |
| `<shared-user name="..." userId="...">` | 여러 앱이 함께 쓰는 공유 사용자 ID |
| `<renamed-package new="..." old="...">` | 이름이 바뀐 패키지 |

그 뒤에 도메인 검증 설정과 키셋(keyset) 정보가 붙습니다 [1].

`<version>` 에 적힌 buildFingerprint 는 [기기 정보와 빌드](../../system-account/device-build.md) 페이지의 빌드 지문과 맞춰 볼 수 있습니다.

### package 요소의 속성

현행 AOSP 의 writePackageLPr 가 `<package>` 에 쓰는 속성을 뜻에 따라 묶으면 다음과 같습니다 [1]. "있을 때" 로 표시한 속성은 값이 없으면 아예 적지 않습니다.

| 묶음 | 속성 |
|---|---|
| 이름·경로 | name, realName(있을 때), codePath, nativeLibraryPath·primaryCpuAbi·secondaryCpuAbi·cpuAbiOverride(있을 때) |
| 플래그 | publicFlags, privateFlags(정수) |
| 시각 | ft, ut, loadingCompletedTime(모두 16진수) |
| 버전 | version(versionCode), targetSdkVersion, baseRevisionCode(있을 때) |
| 사용자 ID | userId(공유 사용자가 아닐 때) 또는 sharedUserId, isSdkLibrary |
| 설치 출처 | installer, installerUid, updateOwner, installerAttributionTag, packageSource, isOrphaned, installInitiator, installInitiatorUninstalled, installOriginator |
| 그 밖의 상태 | restrictUpdateHash(Base64, 있을 때), scannedAsStoppedSystemApp, volumeUuid, categoryHint, updateAvailable, forceQueryable, pendingRestore, debuggable, isLoading, pageSizeCompat(있을 때), loadingProgress, domainSetId, appMetadataFilePath, appMetadataSource |

설치 출처 묶음의 뜻은 [설치 출처와 설치 시각](install-source-time.md) 페이지에 있습니다.

`<package>` 아래에는 공유·정적 라이브러리 사용(`uses-sdk-lib`, `uses-static-lib`), 서명(`sigs`), 설치 요청 앱의 서명(`install-initiator-sigs`), 키셋(`proper-signing-keyset`, `upgrade-keyset`, `defined-keyset`), `mime-group`, `split-version` 하위 요소가 붙습니다 [1].

현행 writePackageLPr 는 `<package>` 아래에 권한 목록(`<perms>`)을 쓰지 않습니다. 다만 읽는 코드(readInstallPermissionsLPr)는 남아 있어서 옛 파일의 `<perms>` 는 읽습니다 [1].

### 시각 속성의 형식

ft, ut, loadingCompletedTime 은 attributeLongHex 로 쓰기 때문에 일반 XML 로 풀면 16진수 문자열로 보입니다 [1]. 값은 유닉스 에포크 밀리초입니다 [3]. 읽는 코드는 ft 가 없거나 0 이면 옛 속성 ts 를 10진수로 읽습니다 [1].

ft 는 패키지 설정의 getLastModifiedTime() 값이고 dumpsys 에서는 `timeStamp=` 라는 이름으로 찍힙니다 [1]. ut 과 첫 설치 시각의 뜻은 [설치 출처와 설치 시각](install-source-time.md) 페이지에서 설명합니다.

## 구조 — packages.list

`packages.list` 는 한 줄에 앱 하나를 적고, 칸은 공백으로 나눕니다. 현행 AOSP 의 writePackageListLPrInternal 이 쓰는 칸의 순서는 다음과 같습니다 [1].

| 순서 | 칸 | 값 |
|---|---|---|
| 1 | 패키지 이름 | |
| 2 | UID | |
| 3 | 디버그 가능 | 1 또는 0 |
| 4 | 데이터 경로 | 사용자 0 기준 하나만 적습니다 |
| 5 | seinfo | |
| 6 | 보조 GID 목록 | 쉼표로 나누고, 없으면 `none` |
| 7 | 셸에서 프로파일 가능 | 1 또는 0 |
| 8 | longVersionCode | |
| 9 | 플랫폼에서 프로파일 가능 | 1 또는 0 |
| 10 | 설치자 | 시스템 앱은 `@system`, product 파티션 앱은 `@product`, 설치자 이름이 있으면 그 이름, 없으면 `@null` |

이 형식은 native 코드(system/core/libpackagelistparser)가 읽습니다 [1]. 데이터 경로 칸은 사용자 0 의 경로만 적기 때문에, 다른 사용자나 프로필의 설치 상태는 이 파일로 알 수 없습니다 [1]. APEX 와 메타데이터가 없는 패키지는 적지 않고, 데이터 경로에 공백이 있는 앱도 건너뜁니다 [1].

이 파일은 임시 파일(`.tmp`)과 JournaledFile 로 통째로 다시 쓰기 때문에, 지운 앱의 줄은 다음에 파일을 쓸 때 사라집니다 [1]. UID 와 패키지 이름을 이어 주는 방법은 [패키지 이름과 UID](../../../01-foundations/value-decoding/package-uid.md) 페이지를 봅니다.

## 라이브 기기에서 보이는 모양 (dumpsys package)

`dumpsys package` 맨 앞 "Database versions:" 아래 "Internal:" 절은 `packages.xml` 의 `<version>` 값을 찍습니다 [1]. 실제 출력에서는 "Internal:" 아래에 `sdkVersion=`, `sdkVersionFull=`, `databaseVersion=` 이 한 줄에, `buildFingerprint=`, `fingerprint=` 가 다음 줄에 찍히고, "External:" 아래는 비어 있을 수 있습니다. `sdkVersionFull` 은 현행 AOSP main 의 Settings.java 에는 없는 칸이라, 제조사가 넣은 칸이거나 다른 버전의 코드일 수 있습니다.

현행 AOSP 기준으로 패키지마다 찍히는 줄의 이름은 `appId=`, `pkg=`, `codePath=`, `versionCode=`, `timeStamp=`, `lastUpdateTime=`, `installerPackageName=` 등이고, 권한은 `declared permissions:`, `requested permissions:`, `install permissions:`, `runtime permissions:` 절로 나뉩니다 [1]. dumpsys 의 시각은 `yyyy-MM-dd HH:mm:ss` 꼴이라 밀리초가 잘리고 시간대 표시가 없어서 [1], 정밀한 시각은 파일의 16진수 값으로 확인합니다. 출력을 뽑는 방법은 [dumpsys 출력](../../logs/dumpsys.md) 페이지를 봅니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 파일을 쓴 시점에 시스템이 이 패키지를 설치된 앱으로 알고 있었다는 것 | 그 사용자가 앱을 실행했거나 사용했다는 것 |
| 코드 경로·버전·서명 같은 설치본의 정체 | 지금은 지운 앱이 예전에 있었다는 것(`packages.list` 에서는 지운 앱의 줄이 다음 쓰기에서 사라집니다) |
| 업데이트된 시스템 앱과 이름이 바뀐 패키지의 기록 | 여러 사용자 중 누구에게 설치됐는지(`package-restrictions.xml` 을 함께 봐야 합니다) |

## 함정과 한계

`packages.xml` 이 ABX 로 저장되어 있으면 텍스트 편집기나 일반 XML 도구로는 깨진 글자만 보이기 때문에, 파일을 먼저 일반 XML 로 풀어야 합니다. 본 파일과 `packages-backup.xml`·`packages.xml.reservecopy` 는 시점이 다를 수 있어서, 사본에만 있는 패키지가 보이면 어느 파일에서 나온 값인지 보고서에 밝힙니다.

ALEAPP 의 permissions 모듈 중 "Package and Shared User" 표는 `<package>` 아래 `<perms>` 에서 권한을 뽑는데 [4], 현행 쓰기 코드는 `<perms>` 를 쓰지 않기 때문에 새 파일에서는 이 표가 빌 수 있습니다.

`packages.list` 는 사용자 0 기준이고 APEX 와 일부 앱을 빼고 적어서, 이 파일의 줄 수를 설치 앱 수로 보고하면 틀릴 수 있습니다.

## 직접 분석해 보기

### 파일로 따라가기

1. `/data/system/` 에서 `packages.xml`, `packages-backup.xml`, `packages.xml.reservecopy`, `packages.list` 를 함께 확보합니다. 확보 방법은 [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지를 봅니다.
2. `packages.xml` 의 첫 바이트가 `<` 로 시작하는 일반 XML 이 아니면 ABX 로 보고, [안드로이드 바이너리 XML (ABX)](../../../01-foundations/data-formats/abx.md) 페이지의 방법으로 풉니다.
3. 찾는 앱의 `<package name="...">` 요소에서 codePath, version, installer, ft, ut 를 읽습니다.
4. 16진수 시각을 10진수 밀리초로 바꾼 다음 UTC 로 바꿉니다.

아래는 명세로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다.

```
ft="1990292d000"
0x1990292d000 = 1756684800000 (유닉스 밀리초)
             = 2025-09-01 00:00:00 UTC
```

`packages.list` 는 공백으로 나누어 위 표의 순서대로 읽으면 되고, 마지막 칸으로 설치자를 바로 볼 수 있습니다.

### 공개 도구로 따라가기

ALEAPP 의 packageInfo 모듈은 `packages.xml` 이 ABX 이면 먼저 풀고(checkabx·abxread) 패키지 정보를 표로 냅니다 [3]. permissions 모듈은 `<permissions>` 아래 항목의 name, package, protection 속성을 뽑습니다 [4]. 도구 결과의 시각은 위의 손 계산 값과 한 번 맞춰 봅니다.

## 교차 검증

- [설치 출처와 설치 시각](install-source-time.md) — 같은 `<package>` 요소의 설치자와 사용자별 첫 설치 시각
- [앱 사용 기록 (usagestats)](../usagestats/index.md) — 설치된 앱이 실제로 화면에 나왔는지
- [APK 정보 (AndroidManifest·서명)](../../embedded-metadata/apk.md) — codePath 에 있는 APK 의 서명과 매니페스트

## 실습

`/data/system/` 폴더가 들어 있는 공개 검체(NIST CFReDS 등)나 직접 만든 시험 기기의 추출본으로 풀어 봅니다.

1. `packages.xml` 은 ABX 입니까, 일반 XML 입니까?
2. `<version>` 의 buildFingerprint 는 빌드 정보와 같습니까?
3. `<package>` 요소 수와 `packages.list` 줄 수는 몇 개씩이고, 차이가 난다면 어떤 패키지가 빠졌습니까?
4. `<updated-package>` 로 남은 시스템 앱은 무엇이고, 같은 이름의 `<package>` 와 codePath 가 어떻게 다릅니까?

## 참고 문헌

1. Settings.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/Settings.java
2. Xml.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/util/Xml.java
3. ALEAPP packageInfo.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/packageInfo.py
4. ALEAPP permissions.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/permissions.py
