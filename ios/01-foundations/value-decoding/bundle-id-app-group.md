---
title: "번들 ID와 앱 그룹"
parent: "기반 · 값 읽는 법"
nav_order: 190
---

# 번들 ID와 앱 그룹 (Bundle ID·App Group)

번들 ID 는 앱과 확장을 가리키는 이름이고 앱 그룹 ID 는 여러 앱과 확장이 함께 쓰는 공유 컨테이너의 이름이라서, 두 값을 이어야 앱 하나가 남긴 기록을 빠짐없이 모을 수 있습니다.

## 이 형식을 쓰는 아티팩트

번들 ID (Bundle ID) 는 폴더 이름, 백업 도메인 이름, DB 칸 값의 세 자리에 나타납니다. 기기 파일 시스템에서는 앱 폴더 이름이 UUID 라서 번들 ID 가 폴더 안의 메타데이터 파일에만 들어 있고 [1][2], 로컬 백업에서는 도메인 이름에 번들 ID 가 그대로 붙습니다. 컨테이너 경로와 도메인 종류별 개수는 [iOS의 파일 시스템](../storage/filesystem/index.md) 과 [로컬 백업](../backups/local-backup/index.md) 에서 다룹니다.

관찰한 백업에서 번들 ID 나 관련 식별자를 값으로 담는 칸은 아래와 같습니다. 칸 이름만 확인했고 값은 읽지 않았습니다. sms.db 의 `balloon_bundle_id` 는 메시지 앱 확장의 번들 ID 를, mis.db 의 `team_id` 칸은 개발자 팀 ID 를 담는 칸이고, 나머지 칸이 앱 본체와 확장 가운데 무엇을 적는지는 확인하지 못했습니다.

| 파일 | 표와 칸 |
|---|---|
| `HomeDomain` :: `Library/FrontBoard/applicationState.db` | `application_identifier_tab.application_identifier`, `kvs.application_identifier` |
| `HomeDomain` :: `Library/TCC/TCC.db` | `access.client`·`client_type`, `policies.bundle_id` |
| `RootDomain` :: `Library/Caches/locationd/consolidated.db` | `GeoFence.BundleId`·`OnBehalfBundleId`, `BeaconFences.BundleIdentifier`·`OnBehalfBundleIdentifier` |
| `WirelessDomain` :: `Library/Databases/DataUsage.sqlite` | `ZPROCESS.ZBUNDLENAME`·`ZEXTENSIONNAME`·`ZPROCNAME` |
| `HomeDomain` :: `Library/SMS/sms.db` | `message.balloon_bundle_id` |
| `HomeDomain` :: `Library/Shortcuts/Shortcuts.sqlite` | `ZSHORTCUT.ZASSOCIATEDAPPBUNDLEIDENTIFIER`, `ZSEARCHATTRIBUTIONAPPBUNDLEIDENTIFIER` |
| `MobileDeviceDomain` :: `ProvisioningProfiles/mis.db` | `profiles.team_id`, `team_id_info.team_id`·`team_name`, `trusted_team_ids.team_id` |

백업 폴더 맨 위 파일에도 앱 목록 키가 있어서, Manifest.plist 에는 `Applications` 키가, Info.plist 에는 `Applications`·`Installed Applications` 키가 있었습니다. 이 키들의 하위 구조는 확인하지 못했습니다.

## 구조

### 이름의 모양

번들 ID 는 `com.apple.mobileslideshow`(사진 앱)처럼 점으로 나눈 이름이고, 이 앱의 확장에는 `com.apple.mobileslideshow.photo-picker` 같은 번들 ID 가 따로 붙습니다 [2]. 앱 그룹 (App Group) ID 는 `group.com.apple.notes` 처럼 `group.` 으로 시작한다고 설명하는 자료가 있고 [1], 시스템 그룹은 핵심 iOS 앱이 쓰는 공유 컨테이너입니다 [2].

관찰한 백업의 도메인 이름에서는 아래 네 가지 이름이 보였습니다.

| 종류 | 백업 도메인 이름 예 | 뒤에 붙는 값 |
|---|---|---|
| 앱 | `AppDomain-com.apple.mobilenotes` | 앱 번들 ID |
| 앱 그룹 | `AppDomainGroup-group.com.apple.notes`, `AppDomainGroup-group.com.apple.notes.import` | 그룹 ID |
| 확장(플러그인) | `AppDomainPlugin-com.apple.mobileslideshow.photo-picker` | 확장 번들 ID |
| 시스템 컨테이너·시스템 그룹 | `SysContainerDomain-com.apple.linkd`, `SysSharedContainerDomain-systemgroup.com.apple.bluetooth` | 번들 ID, `systemgroup.` 으로 시작하는 그룹 이름 |

앱 그룹 도메인 92개 가운데 14개는 `group.` 으로 시작하지 않았고, `AppDomainGroup-com.apple.Home.group`, `AppDomainGroup-com.apple.bird`, `AppDomainGroup-com.apple.CoreODI`, `AppDomainGroup-systemgroup.com.apple.accessorysetupkit` 같은 이름이 있었습니다. 그룹 ID 를 `group.` 접두어로만 골라내면 이런 그룹을 놓칩니다.

### 앱과 그룹의 관계

한 앱이 공유 컨테이너를 여러 개 쓰기도 해서, 2020년 글에서는 파일 공유 앱 하나가 4개 넘게, 메일 앱 하나가 2개를 썼고 메신저 앱 두 개도 앱 그룹에 데이터를 두었습니다 [2]. 이 사례는 글에서 옮긴 것이고, 관찰한 백업에서 확인하지는 않았습니다.

앱과 그룹을 잇는 정보는 기기 파일 시스템의 `/private/var/root/Library/MobileContainerManager/containers.sqlite3` 에 있고, `code_signing_data` 표에 담긴 권한(entitlement) 가운데 `com.apple.security.application-groups`·`com.apple.security.system-groups` 키가 앱이 속한 그룹을 알려 줍니다 [1]. 확장과 부모 앱의 관계는 같은 DB 의 `child_bundles` 표에 있고, Khatri 는 캐시·로그를 빼면 앱과 그룹의 관계를 모두 담은 곳이 이 DB 뿐이라고 씁니다 [1]. 관찰한 백업 메모에는 이 DB 가 나오지 않았습니다.

두 블로그 [1][2] 모두 시험한 iOS 버전을 적지 않아서, 이 절의 설명이 어느 iOS 버전까지 맞는지는 확인하지 못했습니다.

## 읽는 법

앱 하나의 기록을 모을 때는 아래 순서를 따릅니다.

1. **번들 ID 를 정합니다.** 기기 파일 시스템이면 UUID 폴더 안의 `.com.apple.mobile_container_manager.metadata.plist` 에서 주인의 번들 ID 나 그룹 ID 를 읽고 [1][2], 로컬 백업이면 도메인 이름에서 바로 읽습니다.
2. **그룹과 확장을 찾습니다.** 기기 파일 시스템에서는 `containers.sqlite3` 의 권한 정보로 그룹을 찾고 [1], 백업에서는 이름이 비슷한 `AppDomainGroup-`·`AppDomainPlugin-` 도메인을 후보로 모읍니다. 백업의 후보는 이름으로 짐작한 것이라서 보고서에는 그렇게 적습니다.
3. **다른 DB 에서 같은 번들 ID 를 찾습니다.** 위 표의 칸을 번들 ID 로 조회해 권한·위치·데이터 사용량 기록을 앱 단위로 묶습니다.

백업 목록에서 확장 번들 ID 를 뽑아 보는 조회입니다.

```sql
SELECT DISTINCT substr(domain, length('AppDomainPlugin-') + 1) AS bundle_id
FROM Files
WHERE domain LIKE 'AppDomainPlugin-%'
ORDER BY bundle_id;
```

DataUsage.sqlite 에서 번들 ID 와 확장 이름, 프로세스 이름을 나란히 보는 조회입니다.

```sql
SELECT ZBUNDLENAME, ZEXTENSIONNAME, ZPROCNAME
FROM ZPROCESS
ORDER BY ZBUNDLENAME;
```

도메인 이름의 짜임과 fileID 규칙은 [로컬 백업](../backups/local-backup/index.md) 에서, DB 조회 방법은 [SQLite 데이터베이스](../data-formats/sqlite/index.md) 에서 다룹니다.

## 포렌식에서 중요한 점

번들 ID 는 여러 아티팩트를 한 앱으로 묶는 열쇠라서, 권한 기록·위치 기록·데이터 사용량처럼 서로 다른 DB 에 흩어진 행을 같은 앱의 기록으로 엮을 수 있습니다. 앱 데이터가 데이터 컨테이너가 아니라 그룹 컨테이너에 있는 경우도 있어서 [2], 앱 도메인만 보고 앱 데이터가 없다고 쓰지 않습니다.

백업에 앱 도메인이 있으면 그 앱의 데이터가 백업 대상이었다는 뜻일 뿐이고, 앱을 언제 설치하고 썼는지는 [설치된 앱](../../02-artifacts/app-usage/installed-apps.md) 과 [KnowledgeC](../../02-artifacts/app-usage/knowledgec/index.md) 같은 기록으로 따로 확인합니다. mis.db 는 `ProvisioningProfiles` 아래에 있고 개발자 팀 ID 칸이 보였지만, 이 칸으로 앱의 출처를 판단하는 방법은 이번 자료로 확인하지 못했습니다. 앱 출처를 살피는 절차는 [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md) 에서 다룹니다.

## 함정

- **그룹 ID 가 모두 `group.` 으로 시작하지 않습니다.** 관찰한 백업에서도 접두어가 없거나 `systemgroup.` 으로 시작하는 그룹이 있었습니다.
- **이름이 비슷하다고 같은 앱의 그룹이라고 단정하지 않습니다.** 그룹 ID 와 앱 번들 ID 의 관계는 권한 정보로 확인해야 하고, 그룹 ID 에 개발자 팀 ID 접두어가 붙는지는 Apple 개발자 문서를 열지 못해 확인하지 못했습니다.
- **UUID 폴더 이름은 기기마다 다릅니다.** 재설치·업데이트·복원 뒤에 UUID 가 바뀌는지는 확인하지 못했으니, 여러 시점의 자료를 비교할 때는 UUID 대신 번들 ID 로 맞춥니다.
- **applicationState.db 만으로는 그룹을 알 수 없습니다.** 이 DB 는 앱 UUID 와 번들 ID 를 이어 주지만 앱 그룹 경로 정보는 없습니다 [2].
- **칸 이름이 같은 뜻이라는 보장이 없습니다.** consolidated.db 의 `OnBehalfBundleId` 처럼 이름만으로 뜻을 짐작할 수 있는 칸도 뜻은 확인하지 못했으니, 보고서에는 칸 이름과 값을 그대로 적습니다.

## 도구

iLEAPP 의 appGrouplisting 모듈은 `*/Containers/Shared/AppGroup/*/` 와 `*/Containers/Data/PluginKitPlugin/*/` 아래의 `.com.apple.mobile_container_manager.metadata.plist` 를 찾아 `MCMMetadataIdentifier` 키를 읽고, Bundle ID·Type(AppGroup 또는 PluginKitPlugin)·Directory GUID·Path 를 표로 냅니다 [3]. Type 은 상위 폴더 이름으로 가리고 [3], 메타데이터 plist 의 다른 키는 확인하지 못했습니다. 로컬 백업은 Manifest.db 를 SQLite 도구로 열어 도메인 이름으로 조회하면 됩니다.

## 참고 문헌

1. Yogesh Khatri's forensic blog (swiftforensics) — iOS Application Groups & Shared data (2021-01) — http://www.swiftforensics.com/2021/01/ios-application-groups-shared-data.html
2. D20 Forensics — iOS - Tracking Bundle IDs for Containers, Shared Containers, and Plugins (2020-09) — https://blog.d204n6.com/2020/09/ios-tracking-bundle-ids-for-containers.html
3. iLEAPP (Alexis Brignoni) — scripts/artifacts/appGrouplisting.py (main 브랜치) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/appGrouplisting.py
