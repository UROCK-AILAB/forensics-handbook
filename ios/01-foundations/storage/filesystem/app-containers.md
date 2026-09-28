---
title: "앱 컨테이너"
parent: "iOS의 파일 시스템"
grand_parent: "기반 · 저장 구조"
nav_order: 20
---

# 앱 컨테이너 (Bundle·Data·App Group)

iOS 앱은 샌드박스 안의 자기 컨테이너에만 파일을 두고, 실행 파일은 번들 컨테이너에, 데이터는 데이터 컨테이너와 앱 그룹의 공유 컨테이너에 나뉘어 들어갑니다.

## 이 구조를 쓰는 아티팩트

서드파티 앱의 대화·기록 DB 는 앱 컨테이너 안에 있고, Apple 기본 앱의 데이터도 백업에서 앱·그룹 도메인으로 나타납니다(아래 "로컬 백업에서 보이는 모습"). 백업에서 메모 앱의 `NoteStore.sqlite` 는 앱 도메인이 아니라 `AppDomainGroup-group.com.apple.notes` 에, 미리 알림의 `Container_v#/Stores/Data-local.sqlite` 는 `AppDomainGroup-group.com.apple.reminders` 에 들어 있습니다. 앱 하나의 데이터를 빠짐없이 모으려면 데이터 컨테이너뿐만 아니라 그 앱이 속한 앱 그룹과 확장의 컨테이너까지 확인해야 하고, 앱 데이터를 읽는 절차는 [앱 데이터 분석](../../../03-techniques/analysis/app-data-analysis/index.md) 에서 다룹니다.

## 구조

### 컨테이너 종류

앱을 설치하면 샌드박스 안에 번들 컨테이너(앱 번들)와 데이터 컨테이너(앱과 사용자 데이터)가 만들어지고, 앱은 실행 중에 iCloud 컨테이너 같은 추가 컨테이너를 요청해서 쓸 수 있습니다 [6]. 앱은 원칙적으로 자기 컨테이너 밖의 파일에 접근하거나 파일을 만들 수 없습니다 [6].

기기의 실제 경로는 아래와 같습니다 [4][5]. 폴더 이름이 UUID 라서 경로만 보고는 어느 앱의 폴더인지 알 수 없습니다 [4][7].

| 경로 | 담는 것 | 출처 |
|---|---|---|
| `/private/var/containers/Bundle/Application/<UUID>/` | 앱 실행 파일(번들) | [4] |
| `/private/var/mobile/Containers/Data/Application/<UUID>/` | 일반 앱 데이터 | [4] |
| `/private/var/mobile/Containers/Shared/AppGroup/<UUID>/` | 앱 그룹 공유 데이터 | [4][5] |
| `/private/var/mobile/Containers/Data/PluginKitPlugin/<UUID>/` | 확장(플러그인) 데이터 | [4][5] |
| `/private/var/mobile/Containers/Data/InternalDaemon/<UUID>/` | Apple 서비스 | [4][5] |
| `/private/var/containers/Shared/SystemGroup/<UUID>/` | 시스템 그룹 | [4][5] |
| `/private/var/containers/Data/System/<UUID>/` | 시스템 앱·데몬 | [4] |

이 경로들이 어느 볼륨에 속하는지는 [볼륨 구성](volumes.md) 을 봅니다.

### 데이터 컨테이너 안의 폴더

데이터 컨테이너의 하위 폴더와 백업 여부는 아래와 같습니다 [6]. 출처인 Apple 개발자 문서가 보관(archive) 문서라서 앱 번들이 데이터 컨테이너 표에 함께 적혀 있는데, 지금 기기에서는 번들이 별도 컨테이너에 있으므로(위 표) 옛 구조의 흔적으로 읽습니다.

| 폴더 | 담는 것 | 백업 |
|---|---|---|
| `AppName.app` | 앱 번들, 쓸 수 없음 | 안 됨 |
| `Documents/` | 사용자가 만든 내용, 파일 공유로 사용자에게 보일 수 있음 | 됨 |
| `Documents/Inbox` | 다른 앱이 열어 달라고 넘긴 파일, 앱은 읽기·삭제만 가능 | 됨 |
| `Library/` | 사용자 데이터가 아닌 파일 | 됨(Caches 제외) |
| `Library/Application Support` | `Library/` 하위 폴더 | 됨 |
| `Library/Caches` | 캐시, 공간이 부족하면 시스템이 지울 수 있음 | 안 됨 |
| `Library/Preferences` | NSUserDefaults 설정 파일 | 됨 |
| `tmp/` | 임시 파일, 앱이 실행 중이 아닐 때 시스템이 지울 수 있음 | 안 됨 |

출처: [6]. 설정 파일의 형식은 [속성 목록 파일](../../data-formats/plist.md) 에서 다룹니다.

### 앱 그룹

앱 그룹 (App Group) 은 앱과 그 확장이 공유 컨테이너로 데이터를 나누는 방법입니다 [5]. 그룹 ID 는 `group.com.apple.notes`, `group.com.apple.notes.import` 처럼 `group.` 으로 시작하고 앱의 entitlements 에 정의됩니다 [5]. 번들 ID 와 그룹 ID 의 이름 규칙은 [번들 ID와 앱 그룹](../../value-decoding/bundle-id-app-group.md) 에서 다룹니다.

## 읽는 법 — UUID 폴더를 번들 ID 로 잇기

기기에서 뽑은 파일 시스템에서는 UUID 폴더가 어느 앱의 것인지부터 알아내야 하고, 아래 세 곳을 씁니다.

1. **컨테이너 메타데이터 plist.** 각 컨테이너 폴더 맨 위에 `.com.apple.mobile_container_manager.metadata.plist` 가 있고, 여기에 번들 ID(그룹 컨테이너면 그룹 ID)가 들어 있습니다 [4][5].
2. **applicationState.db.** `/private/var/mobile/Library/FrontBoard/applicationState.db` 가 앱 컨테이너 UUID 와 번들 ID 를 이어 주지만, 앱 그룹 경로 정보는 없습니다 [4]. 백업에서는 `HomeDomain` 의 `Library/FrontBoard/applicationState.db` 로 들어 있고, 표는 `application_identifier_tab(id, application_identifier)`, `key_tab(id, key)`, `kvs(id, application_identifier, key, value)`, `schema(version)` 입니다. `key` 의 값 목록과 `value` 의 형식은 실제 파일로 확인합니다.
3. **containers.sqlite3.** `/private/var/root/Library/MobileContainerManager/containers.sqlite3` 의 `child_bundles` 표에는 확장과 부모 앱의 관계가, `code_signing_data` 표에는 entitlements 를 담은 바이너리 plist 가 있고, 그 안의 `com.apple.security.application-groups` 키에 앱이 속한 그룹 ID 목록이 있습니다 [5]. 이 파일은 로컬 백업의 `RootDomain` 에 없을 수 있어 기기 파일 시스템에서 찾습니다.

설치된 앱 목록을 만드는 방법은 [설치된 앱](../../../02-artifacts/app-usage/installed-apps.md) 에서 다룹니다.

## 로컬 백업에서 보이는 모습

로컬 백업은 UUID 폴더 이름 대신 번들 ID 로 도메인 이름을 붙입니다 [7]. 기기가 앱 폴더 이름으로 UUID 를 쓰기 때문이고, `AppDomain-` 뒤에는 번들 ID 가, `SysContainerDomain-`·`SysSharedContainerDomain-` 뒤에는 컨테이너 이름이 붙습니다 [7]. 백업에는 그룹 도메인과 확장 도메인도 있고, `AppDomainGroup-` 뒤에 그룹 ID 가, `AppDomainPlugin-` 뒤에 확장 이름(번들 ID 와 같은 형식)이 붙습니다.

예를 들어 도메인이 모두 1428개인 백업에서 설치 앱 등 161개를 뺀 Apple 기본 도메인 1267개를 종류별로 세면 아래와 같습니다.

| 도메인 종류 | Apple 도메인 수 | 예(항목 수) |
|---|---|---|
| `AppDomain-` | 237 | 대부분 항목 3~4개 |
| `AppDomainGroup-` | 92 | `group.com.apple.notes`(85), `group.com.apple.iBooks`(35), `group.com.apple.reminders`(24), `group.com.apple.safari`(5), `group.com.apple.notes.import`(3) |
| `AppDomainPlugin-` | 875 | |
| `SysContainerDomain-` | 19 | `com.apple.linkd`(141), `com.apple.lsd`(9), `com.apple.springboard`(5), `com.apple.appstored`(4) |
| `SysSharedContainerDomain-` | 29 | `systemgroup.com.apple.configurationprofiles`(19), `systemgroup.com.apple.mobile.installationhelperlogs`(5), `systemgroup.com.apple.lsd`(3) |

그룹 도메인 이름이 모두 `group.` 으로 시작하지는 않습니다. `AppDomainGroup-com.apple.Home.group`, `AppDomainGroup-com.apple.bird` 처럼 접두사가 없는 것과 `AppDomainGroup-systemgroup.com.apple.accessorysetupkit` 처럼 `systemgroup.` 으로 시작하는 것도 있습니다.

번들 컨테이너(`.app`)는 백업되지 않아서 [6], 백업에서는 앱 실행 파일을 볼 수 없습니다. 앱이 설치되어 있었다는 흔적은 아래 파일과 키에서 볼 수 있습니다.

| 위치 | 내용 |
|---|---|
| `InstallDomain` :: `Library/MobileInstallation/BackedUpState/SystemAppInstallState.plist`, `BackupSystemAppInstallState.plist` | 키는 번들 ID(예: `com.apple.iBooks`, `com.apple.VoiceMemos`, `com.apple.mobilesafari`), 값은 정수. 값의 뜻은 단정하지 않고 값만 기록 |
| `HomeDomain` :: `Library/Preferences/com.apple.mobile.installation.plist` | 키 `ExtensionDataContainerParentIDUpdateVersion`(정수) |
| 백업 폴더의 `Manifest.plist` | `Applications`, `Containers` 키. 안의 구조는 실제 파일로 확인 |
| 백업 폴더의 `Info.plist` | `Installed Applications`, `Applications` 키 |
| `MobileDeviceDomain` :: `ProvisioningProfiles/mis.db` | 파일이 있음 |

## 포렌식에서 중요한 점

`Library/Caches` 와 `tmp/` 는 백업 대상이 아니고 시스템이 지울 수 있는 폴더라서 [6], 로컬 백업만으로 조사하면 이 두 폴더의 캐시·임시 파일은 처음부터 빠져 있습니다. 백업에 파일이 없다는 사실만으로 앱이 그 파일을 만들지 않았다고 쓰지 않습니다. 백업의 범위와 한계는 [로컬 백업](../../backups/local-backup/index.md) 에서 다룹니다.

`Documents/Inbox` 에는 다른 앱이 열어 달라고 넘긴 파일이 들어가고 앱은 이 파일을 읽거나 지울 수만 있어서 [6], 파일이 앱 밖에서 들어왔는지 따질 때 함께 볼 폴더입니다.

## 함정

- **앱 데이터가 데이터 컨테이너에만 있지 않습니다.** Spark·WhatsApp·Signal 같은 앱은 2020년 기준으로 데이터를 `Data/Application` 이 아니라 `Shared/AppGroup` 에 두었고 [4], 백업에서도 메모와 미리 알림의 DB 가 그룹 도메인에 들어 있습니다.
- **UUID 는 기기마다 다릅니다.** 폴더 이름만으로 앱을 판단하지 말고, 위 "읽는 법" 의 파일로 번들 ID 를 확인합니다.
- **백업 도메인과 기기 경로의 대응을 짐작하지 않습니다.** `AppDomainGroup-` 이 `Shared/AppGroup` 에, `SysContainerDomain-` 이 `Data/System` 에 대응한다고 단정할 수 없으니, 보고서에는 백업 도메인 이름을 그대로 적습니다.
- **개발자 문서는 보관 문서입니다.** 폴더별 백업 여부 표 [6] 는 옛 문서의 설명이라서, 새 iOS 에서 달라진 부분이 있을 수 있습니다.

## 참고 문헌

- [4] iOS - Tracking Bundle IDs for Containers, Shared Containers, and Plugins — D20 Forensics (2020-09). https://blog.d204n6.com/2020/09/ios-tracking-bundle-ids-for-containers.html
- [5] iOS Application Groups & Shared data — Yogesh Khatri's forensic blog (2021-01). http://www.swiftforensics.com/2021/01/ios-application-groups-shared-data.html
- [6] File System Basics — File System Programming Guide, Apple Developer Documentation Archive. https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html
- [7] A deep dive into the iOS backup/restore system — GitHub Gist (leminlimez). https://gist.github.com/leminlimez/c602c067349140fe979410ef69d39c28
