---
title: "악성 앱은 어디서 들어왔나"
parent: "시나리오 · 침해 사고"
nav_order: 1750
---

# 악성 앱은 어디서 들어왔나 (Initial Access)

## 조사 질문

"이 앱은 스토어에서 받았나, 파일로 깔았나", "그 APK 파일은 어느 주소에서 내려받았나", "처음 설치된 때가 언제인가" 같은 질문에 답하는 흐름입니다. 수상한 앱이 기기에서 무엇을 했는지는 [악성 앱 흔적 분석](../../03-techniques/analysis/malicious-app-triage/index.md) 에서 다루고, 이 페이지는 앱이 기기에 들어온 길을 세우는 데 집중합니다. 문자에 담긴 링크에서 시작한 사고라면 [스미싱 흔적](smishing.md) 을, 다른 사람이 몰래 깐 감시 앱이 의심되면 [몰래 설치된 감시 앱](stalkerware.md) 을 함께 봅니다.

기록은 어느 패키지가 설치자로 적혔는지, 설치 앱이 출처를 무엇이라고 알렸는지, 설치 파일을 어느 주소에서 받았는지까지 알려 주지만, 누가 설치 버튼을 눌렀는지나 사용자가 속았는지는 알려 주지 않습니다.

## 먼저 확인할 것

- **OS 버전과 제조사** — 이 페이지의 설치 출처 속성과 값은 AOSP 소스의 main 가지로 확인한 것이라서 특정 Android 버전의 값이 아닙니다 [1][2]. `packageSource` 가 몇 번째 버전에 들어왔는지는 확인하지 못했으니, 검체의 Android 버전과 One UI 버전을 먼저 적어 두고 속성이 없는 경우도 염두에 둡니다. 삼성 자동 차단(Auto Blocker)은 One UI 6.0(Android 14) 이후 갤럭시에만 있습니다 [4].
- **시간대와 시각 단위** — 설치 기록 파일의 시각 속성은 16진수로 적은 long 값이고 단위는 소스에 적혀 있지 않지만, `dumpsys package` 는 같은 시각을 날짜 문자열로 바꿔 찍습니다 [2]. 내려받은 파일의 `date_added` 는 유닉스 초라서 [3] 두 기록을 한 줄에 놓기 전에 단위부터 맞춥니다. 값 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md), 기기 시간대는 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md) 에서 봅니다.
- **사용자와 프로필** — `dumpsys package` 는 첫 설치 시각(`firstInstallTime=`)과 설치 이유(`installReason=`)를 사용자별 줄로 찍습니다 [2]. 보안 폴더나 작업 프로필이 있으면 어느 사용자에게 설치됐는지부터 나눠 봅니다([보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md)).
- **수집 범위** — 관찰 기기에는 시스템 앱 486개와 사용자가 설치한 앱 168개가 있었습니다 (확인 범위: Android 16, One UI 8.5). 앱 수가 이 정도라서 설치 시각이나 설치자로 먼저 좁힌 뒤 한 앱씩 봅니다. 설치 기록 파일을 adb 일반 권한으로 읽을 수 있는지는 확인하지 않았으니 확보 방식은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 정합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 설치 기록 파일 `packages.xml` 의 `<package>` 요소 | 설치자, 설치를 요청한 패키지, 설치 앱이 알린 출처, 설치·수정 시각 | [설치된 앱](../../02-artifacts/app-usage/packages/index.md) |
| 2 | `dumpsys package` 의 패키지별 줄과 사용자별 줄 | 1번과 같은 값을 날짜 문자열로 바꾼 모양, 사용자별 첫 설치 시각 | [dumpsys 출력](../../02-artifacts/logs/dumpsys.md) |
| 3 | 미디어 저장소의 내려받은 항목 (`MediaStore.Downloads`) | 설치 파일을 받은 주소와 그 앞 페이지 주소, 파일을 넣은 앱, 추가된 시각 | [미디어 저장소](../../02-artifacts/media/mediastore/index.md) |
| 4 | 브라우저 기록 | 내려받기 전후에 연 페이지 | [크롬](../../02-artifacts/browsers/chrome/index.md), [삼성 인터넷](../../02-artifacts/browsers/samsung-internet.md) |
| 5 | 설치 파일(APK) 자체 | 매니페스트와 서명 | [APK 정보](../../02-artifacts/embedded-metadata/apk.md) |
| 6 | 설치 허용·검사 관련 설정 키 | 출처를 알 수 없는 앱, 검사, adb 와 관련된 설정이 있는지 | [설정 값](../../02-artifacts/system-account/settings.md) |

기록마다 확인된 범위가 달라 아래처럼 나눠 적습니다.

| 기록 | 확인된 범위 | 비고 |
|---|---|---|
| `packages.xml` 설치 출처 속성 | AOSP main [2] | 버전별로 어느 속성이 있는지는 확인하지 못했습니다 |
| `packageSource` 값 0~4 | AOSP main [1] | 이 값이 추가된 버전은 확인하지 못했습니다 |
| `owner_package_name` 조회 | Android 14 부터 [3] | 앱이 조회할 때 패키지 가시성에 따라 결과를 거릅니다 |
| 삼성 자동 차단 | One UI 6.0(Android 14) 이후 갤럭시 [4] | 문서 최종 수정일 2025-03-07이고, One UI 7·8 에서 달라진 점은 문서에 없습니다 |
| 삼성 기기의 설치·검사 역할 | (확인 범위: Android 16, One UI 8.5) | `dumpsys package` 의 "Known Packages:" 절에서 Installer 는 `com.google.android.packageinstaller`, Verifier 는 `com.android.vending` 과 `com.samsung.android.sm.devicesecurity`, "Developer verification service provider:" 는 `com.google.android.verifier` 였습니다 |

## 분석 흐름

1. **설치자 세 칸을 나눠 읽습니다.** PackageManager 는 설치 기록을 `dataDir/system/packages.xml` 에 쓰고, 같은 폴더에 `packages.xml.reservecopy` 와 `packages.list` 를 둡니다 [2]. `<package>` 요소에는 `installer`, `installerUid`, `updateOwner`, `installerAttributionTag`, `packageSource`, `installInitiator`, `installOriginator` 속성이 있고, `isOrphaned` 와 `installInitiatorUninstalled` 는 값이 true 일 때만 적힙니다 [2]. `installer` 는 기록상 설치자, `installInitiator` 는 설치를 요청한 패키지, `installOriginator` 는 설치를 요청한 패키지가 누구를 대신해 요청했는지를 가리키는 패키지이고, 소스의 필드 이름은 각각 `mInstallerPackageName`, `mInitiatingPackageName`, `mOriginatingPackageName` 입니다 [2][5]. 공개 API 문서도 세 값을 기록상 설치자(installer of record), 설치를 요청한 패키지, 요청한 패키지가 대신한 패키지로 설명합니다 [5]. 세 값이 서로 다르면 어느 앱이 어느 앱을 거쳐 설치했는지 순서를 그려 볼 수 있습니다. 설치자가 바뀐 뒤에 각 칸이 어떻게 남는지는 [설치된 앱](../../02-artifacts/app-usage/packages/index.md) 에서 봅니다.

2. **설치 앱이 알린 출처를 읽습니다.** `packageSource` 는 설치 앱이 `PackageInstaller.SessionParams#setPackageSource(int)` 로 알리는 값이고, 소스 주석은 이 값을 "정보용이며 시스템이 신호로 쓸 수 있다" 고 설명합니다 [1].

   | 값 | 상수 | 뜻 [1] |
   |---|---|---|
   | 0 | `PACKAGE_SOURCE_UNSPECIFIED` | 설치 앱이 `setPackageSource` 를 부르지 않았습니다(기본값) |
   | 1 | `PACKAGE_SOURCE_OTHER` | 다른 상수에 맞지 않는 출처입니다 |
   | 2 | `PACKAGE_SOURCE_STORE` | 앱 스토어가 사용자 대신 설치했습니다 |
   | 3 | `PACKAGE_SOURCE_LOCAL_FILE` | 기기 안의 파일로 설치했고, 소스는 APK 설치를 돕는 파일 관리자를 예로 듭니다 |
   | 4 | `PACKAGE_SOURCE_DOWNLOADED_FILE` | 사용자가 내려받은 파일로 설치했고, 설치 앱이 내려받은 파일임을 알 때 3 대신 씁니다 |

   값을 알리지 않는 설치 앱을 거치면 0 으로 남아서, 0 은 "출처가 수상하다" 가 아니라 "설치 앱이 알리지 않았다" 로 읽습니다.

3. **설치 시각을 세웁니다.** 설치 기록 파일은 `ft`(마지막 수정 시각)와 `ut`(마지막 업데이트 시각)를 16진수 long 으로 쓰고, 읽을 때는 `it`(첫 설치 시각)도 16진수로 읽습니다 [2]. `dumpsys package` 는 패키지별로 `timeStamp=`, `lastUpdateTime=`, `installerPackageName=`, `installerPackageUid=`, `initiatingPackageName=`, `originatingPackageName=`, `packageSource=` 줄을 찍고 `updateOwnerPackageName=`, `installerAttributionTag=` 는 값이 있을 때만 찍으며, 사용자별로 `installReason=`, `dataDir=`, `firstInstallTime=` 을 찍습니다 [2]. 관찰 기기에서 받은 `dumpsys package` 요약에는 이 패키지별 줄이 생략되어 나오지 않았으니 (확인 범위: Android 16, One UI 8.5), 위 줄 이름은 소스 기준으로 보고 검체의 실제 출력에서 다시 확인합니다. 파일의 16진수 값과 `dumpsys` 의 날짜 문자열을 같은 앱에서 나란히 놓으면 파일 값의 단위를 검체에서 직접 맞춰 볼 수 있습니다.

4. **설치 파일이 어디서 왔는지 찾습니다.** 미디어 저장소의 내려받은 항목(`MediaStore.Downloads`)에는 받은 주소 `download_uri` 와 그 주소의 HTTP 리퍼러 `referer_uri` 칸이 있고, 둘 다 문자열입니다 [3]. 모든 미디어 항목에는 내려받은 것인지 표시하는 `is_download`, 항목을 넣은 패키지 `owner_package_name`, 처음 추가된 시각 `date_added`(유닉스 초) 칸이 있습니다 [3]. 3단계의 설치 시각 바로 앞에 추가된 APK 항목을 찾아 두 주소를 적고, `owner_package_name` 으로 어느 앱이 파일을 넣었는지 봅니다. 미디어 저장소 DB 파일의 경로와 크롬 자체의 내려받기 기록은 이번 조사에서 확인하지 못했으니 [미디어 저장소](../../02-artifacts/media/mediastore/index.md) 와 [크롬](../../02-artifacts/browsers/chrome/index.md) 페이지 기준으로 읽습니다.

5. **내려받기 전후의 페이지를 잇습니다.** `referer_uri` 에 적힌 페이지와 같은 시간대의 브라우저 기록, 문자·메신저에서 받은 링크를 나란히 놓습니다. 링크를 받은 쪽은 [스미싱 흔적](smishing.md), 웹 기록을 시간순으로 세우는 법은 [웹 사용 행위 재구성](../activity/web-activity.md) 에 있습니다.

6. **설치를 허용하거나 막는 설정을 봅니다.** 관찰 기기의 설정 키 목록에는 secure 쪽에 `install_non_market_apps`, `unknown_sources_default_reversed` 와 `appprotection_auto_scan_updated`, `appprotection_package_uid`, `appprotection_permission_function_install_auto_scan_agreed`, `appprotection_permission_function_background_auto_scan_agreed` 같은 `appprotection_` 키가 있었고, global 쪽에 `package_verifier_user_consent`, `verifier_timeout`, `verifier_timeout_samsung`, `adb_enabled`, `adb_wifi_enabled` 가 있었습니다 (확인 범위: Android 16, One UI 8.5). 메모에는 키 이름만 있고 값이 없으며 각 키의 뜻과 현재 쓰임은 확인하지 못했으니, 검체에서 값을 읽더라도 "이 키가 이 값이었다" 까지만 적고 기능이 켜져 있었다고 풀어 쓰지 않습니다. `appprotection_` 키가 삼성의 앱 보호 기능과 이어지는지도 이름에서 짐작할 뿐입니다.

7. **삼성 자동 차단의 영향을 따집니다.** 삼성 문서는 "Auto Blocker is only available on Galaxy devices running One UI 6.0 (Android 14) or later, and is enabled by default." 라고 적고 있습니다 [4]. 켜 두면 Google Play 스토어와 Galaxy Store 같은 공식 스토어 앱만 설치되고, USB 케이블로 오는 명령과 USB 소프트웨어 업데이트를 막고, 메시지로 받은 이미지로 위장한 악성 데이터를 막습니다 [4]. "최대 제한(Maximum restrictions)" 을 켜면 앱 보호(설치 중과 설치 뒤의 의심 앱 검사, 백신은 지역마다 다름)가 켜지고, 기기 관리자 앱과 업무 프로필, 첨부 자동 내려받기, 하이퍼링크와 미리보기, 공유 앨범을 막고, 사진을 공유할 때 위치 정보를 지웁니다 [4]. 문서에는 자동 차단이 남기는 기록이나 로그 이야기가 없고 설정 키 이름도 확인하지 못했으니, 검체에서 이 기능이 그때 켜져 있었는지는 다른 근거로 따로 확인합니다.

8. **한 줄로 정리합니다.** 링크를 받은 시각, 파일을 내려받은 시각과 주소, 설치 시각과 설치자 세 칸, 설치 앱이 알린 출처를 시간순으로 적고, 비어 있는 칸은 비어 있다고 남깁니다. 여러 기록을 한 시간 축에 놓는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

> 그림 자리: 왼쪽부터 "링크 받음 → 페이지 열람 → 파일 내려받음(download_uri·referer_uri) → 설치(installer·installInitiator·packageSource)" 를 시간 축에 놓고, 각 단계 아래에 근거 기록 이름을 적은 그림

## 흔한 오판

**`installer` 값을 "파일을 받은 곳" 으로 읽는 오판**이 흔합니다. `installer` 는 기록상 설치자이고, 설치를 요청한 패키지와 그 요청이 누구를 대신한 것인지는 `installInitiator` 와 `installOriginator` 에 따로 남습니다 [2][5]. 파일을 받은 주소는 미디어 저장소의 `download_uri` 쪽에서 찾습니다 [3].

**`packageSource` 를 시스템이 확인한 사실로 읽는 경우**도 조심합니다. 이 값은 설치 앱이 스스로 알리는 정보용 값이라서 [1], 값이 3이나 4라도 시스템이 파일 출처를 따로 검증했다는 뜻은 아닙니다.

**`owner_package_name` 이 비어 있으면 파일의 주인이 없다고 보는 것**은 지나칩니다. 소유를 믿을 만하게 정할 수 없을 때 NULL 일 수 있다고 소스가 적고 있습니다 [3].

**단위가 다른 시각을 그대로 비교하는 실수**도 있습니다. `date_added` 는 유닉스 초이고 [3], 설치 기록 파일의 시각은 16진수로 적은 long 값이며 단위가 소스에 적혀 있지 않아서 [2], 10진수로 바꾸고 단위를 검체에서 맞춘 뒤에 나란히 놓습니다.

**자동 차단의 흔적이 없으니 꺼져 있었다고 단정하는 것**도 근거가 없습니다. 문서에 이 기능이 남기는 기록 이야기가 없습니다 [4].

## 보고서 문장 예

| 쓰지 않을 문장 | 쓸 문장 |
|---|---|
| 피해자는 ○○ 사이트에서 악성 앱을 내려받아 설치했다. | 미디어 저장소에 ○○일 ○○:○○(UTC ○○:○○)에 추가된 ○○.apk 항목이 있고, 받은 주소(`download_uri`)는 ○○, 리퍼러(`referer_uri`)는 ○○로 기록되어 있습니다. |
| 이 앱은 출처를 알 수 없는 경로로 설치되었다. | 설치 기록에서 ○○ 앱의 설치자(`installer`)는 ○○, 설치를 요청한 패키지(`installInitiator`)는 ○○이고, 설치 앱이 알린 출처(`packageSource`)는 3(`PACKAGE_SOURCE_LOCAL_FILE`)입니다. 이 출처 값은 설치 앱이 스스로 알린 값입니다. |
| 사용자가 보안 기능을 끄고 앱을 깔았다. | 설정 값 ○○ 키가 ○○로 기록되어 있습니다. 이 값이 설치 시점에도 같았는지는 확보한 기록으로 확인되지 않습니다. |

보고서 전체의 틀은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 아티팩트 본문: [설치된 앱 (packages.xml)](../../02-artifacts/app-usage/packages/index.md), [미디어 저장소](../../02-artifacts/media/mediastore/index.md), [APK 정보](../../02-artifacts/embedded-metadata/apk.md), [설정 값](../../02-artifacts/system-account/settings.md), [dumpsys 출력](../../02-artifacts/logs/dumpsys.md), [구글 플레이 기록](../../02-artifacts/app-usage/play-store.md)
- 값 해석: [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md), [시각 값](../../01-foundations/value-decoding/time-values.md)
- 보안 구조: [앱 샌드박스와 권한](../../01-foundations/security-model/sandbox-permissions.md), [삼성 녹스](../../01-foundations/security-model/samsung-knox.md)
- 이어지는 시나리오: [스미싱 흔적](smishing.md), [몰래 설치된 감시 앱](stalkerware.md), [계정 탈취 흔적](account-takeover.md)
- 기법: [악성 앱 흔적 분석](../../03-techniques/analysis/malicious-app-triage/index.md), [타임라인 작성](../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. PackageInstaller.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/content/pm/PackageInstaller.java
2. Settings.java (PackageManager) — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/Settings.java
3. MediaStore.java — AOSP packages/providers/MediaProvider (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_packages_providers_MediaProvider/main/apex/framework/java/android/provider/MediaStore.java
4. Samsung Auto Blocker — Samsung Knox Documentation (2025-03-07 수정) — https://docs.samsungknox.com/admin/fundamentals/whitepaper/samsung-knox-mobile-security/system-security/samsung-auto-blocker/
5. InstallSourceInfo.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/content/pm/InstallSourceInfo.java
