---
title: "앱 지우기"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 1660
---

# 앱 지우기 (App Removal)

기기에서 앱을 지웠는지, 지운 앱이 무엇이고 언제쯤 썼는지를 남은 흔적으로 따라가는 흐름을 정리합니다. 소스에 나온 동작은 현행 AOSP(frameworks/base 의 main 가지) 기준이고, 버전에 따라 다를 수 있습니다.

## 조사 질문

"지금 기기에 없는 앱이 예전에 있었는가, 그 앱을 언제쯤 썼고 언제쯤 지웠는가" 를 묻습니다. 메신저나 감시 앱처럼 앱 자체가 증거인 사건에서 자주 나오는 질문이고, 앱을 지우면 앱 목록에서는 사라지지만 시스템 기록과 공용 저장 공간에는 한동안 흔적이 남을 수 있습니다.

## 먼저 확인할 것

- **Android 버전**: Android 15(API 35)부터 앱을 완전히 지우지 않고 보관(archiving)할 수 있어서 [3], "목록에서 사라진 앱" 이 정말 지운 앱인지 버전부터 봅니다.
- **관리 기기 여부**: 프로필 소유자(profile owner)가 있으면 usagestats 가 지운 앱의 데이터를 지우지 않습니다 [2]. 프로필 소유자가 있는지는 `dumpsys user` 사용자 항목의 `Has profile owner:` 필드에서 봅니다. 업무 프로필은 [보안 폴더와 작업 프로필](../../../01-foundations/security-model/secure-folder-work-profile.md) 에 있습니다.
- **수집 시점**: usagestats 는 앱이 지워진 뒤 기록을 바로 지우지 않고 나중에 정리해서(아래 절), 앱을 지운 직후에 수집했는지가 결과를 가릅니다.
- **수집 범위**: adb 일반 권한 출력만 있는지, 전체 파일 시스템 사본이 있는지 적어 둡니다.

## 앱을 지울 때 남는 것과 사라지는 것

### usagestats 기록

패키지가 지워지면 UsageStatsService 의 PackageMonitor 가 알아채고 `MSG_PACKAGE_REMOVED` 를 거쳐 `onPackageRemoved()` 를 부릅니다 [2]. 이 함수는 기록을 바로 지우지 않고 `UsageStatsIdleService.schedulePruneJob()` 으로 정리 작업(prune job)을 예약합니다 [2]. 그래서 정리 작업이 돌기 전에 수집하면 지운 앱의 기록이 남아 있을 수 있습니다(해석). 작업이 언제 도는지(대기 조건·지연 시간)는 실제 기기로 확인해야 합니다.

데이터베이스 쪽에서는 `UsageStatsDatabase.onPackageRemoved()` 가 패키지 이름과 번호를 잇는 대응표(mappings)에서 그 패키지에 지운 시각(timeRemoved)을 붙여 제거 표시를 하고 mappings 파일을 다시 씁니다 [1]. `pruneUninstalledPackagesData()` 는 디스크의 사용 기록을 모두 읽어 지워진 패키지와 관련된 데이터를 빼고 다시 쓰고, `prunePackagesDataOnUpgrade()` 는 설치 목록에 없는 패키지의 통계(packageStats)와 이벤트(events)를 걸러 냅니다 [1]. 구간 파일은 패키지 이름 대신 mappings 의 번호를 쓰니, mappings 에서 빠진 뒤에는 파일에 번호가 남아 있어도 패키지 이름을 되살리기 어렵습니다(해석). 파일과 mappings 의 구조는 [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) 에 있습니다.

### 공용 저장 공간의 파일

앱이 공용 저장 공간에 만든 미디어 파일은 앱을 지워도 기기에 남습니다 [4]. 앱을 다시 설치하면 이전 설치가 만든 파일은 새 설치의 것으로 보지 않아서, 다시 설치한 앱은 READ_EXTERNAL_STORAGE 권한이 있어야 그 파일에 접근합니다 [4]. 공용 저장 공간에 주인 없는 앱 폴더나 파일이 남아 있으면 지운 앱의 흔적일 수 있습니다(해석). `/sdcard/Android/media` 아래에는 앱별 폴더가 있고, 지운 앱의 폴더가 여기에 남는지는 실제 기기에서 확인합니다. 폴더 구조는 [공용 저장 공간](../../../01-foundations/storage/shared-storage.md) 에 있습니다.

### 보관(archiving)은 지운 것이 아님

| 방식 | Android 버전 | 지우는 것 | 남는 것 |
|---|---|---|---|
| 일반 제거 | 모든 버전 | 앱 | 공용 저장 공간의 미디어 파일 [4], 정리 작업 전까지의 usagestats 기록 [2] |
| OS 수준 보관 (`PackageInstaller.requestArchive()`) | Android 15(API 35) 이상 | APK, 캐시 파일 | 사용자 데이터, 런처 목록의 보관 표시 [3] |

보관을 요청하려면 REQUEST_DELETE_PACKAGES 권한이 필요합니다 [3]. 보관된 앱은 LauncherApps API 에 계속 나오고 화면에는 보관됨 표시가 붙으며, 사용자가 누르면 설치 앱(installer)에 복원(requestUnarchive) 요청이 가고 복원은 `ACTION_PACKAGE_ADDED` 방송으로 알 수 있습니다 [3]. 구글 플레이는 이보다 먼저(2023년) App Bundle 로 올린 앱의 자동 보관을 발표했으니 [3], 사용자가 쓰지 않아 자동으로 보관된 앱을 "지웠다" 로 적지 않습니다. 삼성 기기에서 보관이 어떻게 보이는지는 실제 기기로 확인해야 합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 설치된 앱 목록 | 지금 설치된 앱, 보관 상태, 설치 출처 | [설치된 앱](../../../02-artifacts/app-usage/packages/index.md) |
| 2 | usagestats | 정리 전이라면 지운 앱의 사용 이벤트, mappings 의 제거 표시 | [앱 사용 기록](../../../02-artifacts/app-usage/usagestats/index.md) |
| 3 | 공용 저장 공간 | 지운 앱이 남긴 미디어 파일과 폴더 | [공용 저장 공간](../../../01-foundations/storage/shared-storage.md) |
| 4 | 알림 기록 | 지운 앱이 보낸 알림 | [알림 기록](../../../02-artifacts/app-usage/notification-history.md) |
| 5 | 배터리·데이터 사용 기록 | 그 앱이 돌거나 통신한 흔적 | [배터리 사용 기록](../../../02-artifacts/app-usage/batterystats.md), [데이터 사용량](../../../02-artifacts/network/netstats.md) |
| 6 | 구글 플레이 기록 | 계정에 설치 이력이 남았는지 | [구글 플레이 기록](../../../02-artifacts/app-usage/play-store.md) |

플레이 스토어 기록에 지운 앱이 남는지는 실제 기기에서 확인합니다. 앱 데이터를 남기고 지우는 제거 방식은 이 페이지에서 다루지 않습니다.

### adb 일반 권한으로 보이는 필드

adb 일반 권한 출력에서 볼 필드는 아래와 같습니다. 제조사가 추가한 필드·키가 섞여 있어 기기마다 다를 수 있습니다.

| 출력 | 필드·키 |
|---|---|
| `dumpsys package` 의 "Known Packages:" | `Installer:`(com.google.android.packageinstaller), `Uninstaller:`(비어 있음), `Verifier:`(com.android.vending, com.samsung.android.sm.devicesecurity) |
| `dumpsys usagestats` 이벤트 줄 | `time="..." type=... package=... class=... flags=...`, STANDBY_BUCKET_CHANGED 줄의 `standbyBucket=` 와 `reason=` |
| `settings secure` | `install_non_market_apps`, `fixed_delete_mode_rule`, `fixed_delete_reminder` |
| `settings global` | `package_verifier_user_consent`, `verifier_timeout`, `verifier_timeout_samsung` |

`fixed_delete_*` 키의 뜻을 밝힌 공개 자료는 없습니다. `dumpsys package` 에 지워진 패키지 이력을 보여 주는 절이 있는지는 실제 기기의 출력에서 확인합니다.

## 분석 흐름

1. 지금 설치된 앱 목록을 뽑고, 보관 상태인 앱을 따로 표시합니다.
2. usagestats 의 이벤트와 mappings 에서 지금 목록에 없는 패키지 이름을 찾습니다. mappings 의 제거 표시에 붙은 시각은 그 패키지를 지운 무렵의 단서가 됩니다(해석).
3. 공용 저장 공간에서 설치된 어느 앱에도 속하지 않는 폴더와 미디어 파일을 찾고, 파일 시각을 적어 둡니다.
4. 알림 기록, 배터리·데이터 사용 기록에서 같은 패키지 이름이 나오는지 봅니다.
5. 여러 기록에서 그 패키지가 마지막으로 나오는 시각을 한 표에 놓아 "이 무렵 이후로 흔적이 없다" 는 경계를 잡습니다. 여러 기록을 한 시간 축에 놓는 법은 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 에 있습니다.
6. 지운 앱의 데이터 자체를 되살려야 하면 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 로 넘어갑니다.

## 흔한 오판

**usagestats 에 없으니 그 앱을 쓴 적이 없다고 보는 경우.** 앱을 지우면 정리 작업이 그 앱의 통계와 이벤트를 지우고 [1][2], 지우지 않은 앱의 이벤트도 보관 기간이 지나면 사라집니다(기간은 [앱 사용 기록](../../../02-artifacts/app-usage/usagestats/index.md) 참고). 기록이 없다는 사실은 사용하지 않았다는 증거가 되지 못합니다.

**구간 파일에 남은 번호를 아무 이름에나 맞추는 경우.** mappings 에서 빠진 뒤의 번호는 이름을 되살리기 어렵고 [1], 다른 시점의 mappings 로 맞추면 엉뚱한 패키지를 가리킬 수 있습니다(해석).

**보관된 앱을 지운 앱으로 적는 경우.** Android 15 이상의 보관은 사용자 데이터를 남기고 [3], 자동 보관은 사용자가 지우려고 한 행위가 아닐 수 있습니다.

**공용 저장 공간의 파일이 지운 앱의 것이라고 단정하는 경우.** 폴더 이름과 파일 내용이 그 앱을 가리키더라도, 다른 앱이 같은 이름으로 만들었을 가능성을 파일 메타데이터와 함께 따집니다.

## 보고서 문장 예

> 수집 시점에 (패키지) 는 설치 목록에 없었습니다. usagestats 의 mappings 에는 이 패키지에 기기 시계 기준 (시각) 의 제거 표시가 있고, 공용 저장 공간의 (폴더) 에 이 패키지 이름의 폴더와 파일 (개수) 개가 남아 있습니다. 이 기록은 그 무렵 이 앱이 기기에서 제거되었다는 것과 맞지만, 누가 제거했는지는 이 기록만으로 알 수 없습니다.

## 함께 볼 페이지

- 이 묶음 전체의 길잡이는 [증거를 없애려 했나](index.md) 이고, 기기 전체를 지운 경우는 [초기화](factory-reset.md), 앱은 두고 대화·사진만 지운 경우는 [메시지·사진 지우기](content-deletion.md) 를 봅니다.
- 앱 사용 시각을 재구성하는 흐름은 [어떤 앱을 언제 썼나](../app-usage.md), 감시 앱을 지운 흔적은 [몰래 설치된 감시 앱](../../incident/stalkerware.md) 과 [악성 앱 흔적 분석](../../../03-techniques/analysis/malicious-app-triage/index.md) 에 있습니다.
- 패키지 이름과 UID 를 잇는 법은 [패키지 이름과 UID](../../../01-foundations/value-decoding/package-uid.md) 에 있습니다.

## 참고 문헌

1. UsageStatsDatabase.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsDatabase.java
2. UsageStatsService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usage/java/com/android/server/usage/UsageStatsService.java
3. Android 15 features and APIs overview — Android Developers, https://developer.android.com/about/versions/15/features
4. Access media files from shared storage — Android Developers, https://developer.android.com/training/data-storage/shared/media
