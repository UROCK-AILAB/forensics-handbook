---
title: "구성 프로파일과 MDM"
parent: "아티팩트 · 자격 증명·보안 설정"
nav_order: 1120
---

# 구성 프로파일과 MDM (Configuration Profiles·MDM)

## 한 줄 요약

구성 프로파일 (Configuration Profile)은 설정과 권한 정보를 묶어 기기에 설치하는 파일이고, 기기 관리 서비스 (MDM)가 원격으로 넣거나 사용자가 메일·웹에서 받아 직접 설치합니다. 설치 결과는 로컬 백업의 `ConfigurationProfiles` 폴더에 프로파일 목록과 제한 설정 이름으로 남습니다.

## 무엇을 기록하나 · 왜 생기나

기존 방식의 구성 프로파일은 이름이 `.mobileconfig` 로 끝나는 XML 파일이고, 설정과 권한 정보를 담은 페이로드 (payload)로 이뤄집니다 [1]. 같은 일을 JSON 으로 하는 선언형 구성도 있습니다 [1]. 프로파일은 MDM, 이메일 첨부, 웹 링크나 서비스 포털, Apple Configurator 로 설치할 수 있고, 이메일 첨부나 웹에서 받으면 설치를 시작하라는 안내가 뜹니다 [1]. 아이폰에서는 프로파일이 기기 수준에서 모든 사용자에게 적용되고, 사용자 수준 프로파일은 Mac 과 공유 iPad 에만 있습니다 [1].

사용자가 직접 설치할 때는 받은 뒤 설정 앱에서 "Profile Downloaded"(프로파일이 다운로드됨) 또는 "Enroll in [조직 이름]" 을 누르고 오른쪽 위의 설치를 누릅니다 [2]. 받은 뒤 8분 안에 설치하지 않으면 프로파일은 저절로 지워지고, 설치를 기다리는 프로파일은 한 번에 하나라서 두 번째를 받으면 첫 번째를 대신합니다 [2]. [2]는 iOS 에서 도난 기기 보호 (Stolen Device Protection)를 먼저 끄고 설치한 뒤 다시 켜야 한다고 안내합니다. 설치된 프로파일을 보여 주는 설정 화면의 메뉴 이름은 이번 출처로 확인하지 못했습니다.

감독 (Supervision)은 대개 조직이 기기를 소유한다는 뜻이고, 감독된 기기에는 구성과 제한을 더 많이 걸 수 있습니다 [3]. 자동 기기 등록 (Automated Device Enrollment)으로 등록한 아이폰은 iOS 13 부터 자동으로 감독되고(iPadOS 는 13.1 부터), Apple Configurator 로 손수 감독하면 기기가 지워집니다 [3]. 감독된 아이폰의 설정 화면에는 "This iPhone is supervised. [Organization name] can monitor your internet traffic and locate this device." 꼴의 문구가 보이고 [3], 한국어 화면의 문구는 확인하지 못했습니다.

프로파일은 여러 경로로 지워집니다 [1]. 기기 전체를 지우면 모든 프로파일이 없어지고, 자동 기기 등록 기기에서 등록 프로파일을 지우면 거기에 딸린 구성도 함께 없어집니다 [1]. MDM 은 자신이 설치한 프로파일을 지울 수 있고, 사용자는 손으로 설치한 프로파일 대부분을 지울 수 있지만 감독된 기기에서 제거 암호가 걸린 프로파일은 인증을 거쳐야 합니다 [1]. 감독하지 않은 아이폰에서는 기기 암호를 아는 사람이 제거 제한이 걸린 수동 설치 프로파일도 지울 수 있습니다 [1].

## 위치와 버전별 차이

### 버전별로 확인된 범위

| iOS | 확인된 내용 | 출처 |
|---|---|---|
| 13 이후 | 자동 기기 등록 아이폰은 자동으로 감독됨(iPadOS 는 13.1 이후) | [3] |
| 버전 표기 없음 | 프로파일 설치 경로, 적용 범위, 지우는 방법 | [1][2] |
| 27.0 | 로컬 백업 속 도메인, 파일 경로, plist 키 이름과 DB 칸 이름(값은 읽지 않음) | 관찰 |

### 로컬 백업에서 볼 곳

관찰한 백업은 Windows 의 Apple 기기 앱으로 만든 암호화하지 않은 로컬 백업이었고, 아래 도메인은 모두 이름과 항목 수만 확인했습니다(확인 범위: iPhone 13 mini, iOS 27.0).

| 백업 도메인 | 항목 수 | 보는 까닭 |
|---|---|---|
| `SysSharedContainerDomain-systemgroup.com.apple.configurationprofiles` | 19 | 프로파일 목록, 감독 여부, 제한 설정 |
| `ManagedPreferencesDomain` | 4 | 관리되는 설정값 |
| `SysContainerDomain-com.apple.remotemanagementd` | 6 | 이름으로 보아 원격 관리 데몬 |
| `SysContainerDomain-com.apple.managedappdistributiond` | 2 | 이름으로 보아 관리 앱 배포 데몬 |
| `SysSharedContainerDomain-systemgroup.com.apple.icloud.findmydevice.managed` | 4 | 나의 찾기 상태로 보이는 키 |
| `MobileDeviceDomain` | 3 | 앱 서명용 프로비저닝 프로파일 DB(아래 "이름이 비슷하지만 다른 것") |

MDM 서버 주소와 등록 시각이 백업의 어느 파일에 남는지는 관찰 메모와 이번에 연 문서 어디에서도 확인하지 못했습니다.

## 구조

### ConfigurationProfiles 폴더

`systemgroup.com.apple.configurationprofiles` 도메인의 `Library/ConfigurationProfiles/` 아래에서 본 파일과 키는 다음과 같습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
CloudConfigurationDetails.plist
  AllowPairing (bool)
  CloudConfigurationUIComplete (bool)
  ConfigurationSource (int)
  IsSupervised (bool)
  PostSetupProfileWasInstalled (bool)
PayloadManifest.plist
  HiddenProfiles (list)
  OrderedProfiles (list)
MCProfileEvents.plist
  ProfileEvents (list)
MCSettingsEvents.plist
  EffectiveSettings: {intersection, restrictedBool, restrictedValue, union}
  Restrictions: {intersection, restrictedBool, union}
  SystemClientRestrictions: {com.apple.lsd.appremoval, com.apple.profiled.appenforced.com.apple.news,
                             com.apple.profiled.trustedcodesigningidentities, com.apple.siri.parsec.HashtagImagesApp}
  SystemProfileRestrictions: {식별자 1개}
  SystemSettings: {restrictedBool, restrictedValue}
ClientTruth.plist
  com.apple.lsd.appremoval: {clientRestrictions, clientType, compliant, localizedClientDescription}
  com.apple.profiled.appenforced.com.apple.news: {clientRestrictions, clientType, compliant, localizedClientDescription}
  com.apple.siri.parsec.HashtagImagesApp: {clientRestrictions, clientType, compliant}
PublicInfo/MCMeta.plist
  LastMDMMigratedBuild (str)
  LastMigratedBuild (str)
UserSettings.plist
  assignedObject, intersection, restrictedBool, restrictedValue, union
```

`AppAccessibilityParameters.plist`, `PayloadDependency.plist`, `ProfileTruth.plist`, `PublicInfo/NamespacedUserSettings.plist` 는 키가 비어 보였습니다(확인 범위: iPhone 13 mini, iOS 27.0).

`IsSupervised` 는 이름으로 보아 [3]이 말한 감독 여부에 해당하지만, 값의 정의 문서는 열지 않았습니다. `PayloadManifest.plist` 의 `OrderedProfiles` 는 이름으로 보아 설치된 프로파일의 순서, `HiddenProfiles` 는 화면에 드러나지 않는 프로파일의 목록이고, `MCProfileEvents.plist` 의 `ProfileEvents` 는 프로파일 설치·제거 이벤트 목록으로 보입니다. 다만 목록 안 항목에 어떤 키(설치·삭제 시각 등)가 있는지는 확인하지 못했으니, 이 세 목록은 값을 직접 열어 확인한 만큼만 해석합니다. `MCMeta.plist` 의 두 키는 이름으로 보아 설정을 마지막으로 옮겨 적은 iOS 빌드 번호입니다.

`SystemProfileRestrictions` 아래에는 통신사 이름과 UUID 가 들어간 식별자가 하나 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0). 개인 기기에도 통신사 설정처럼 처음부터 들어 있는 프로파일이 있을 수 있다는 뜻으로 읽히지만, 값을 읽지 않아 무엇인지는 확인하지 못했습니다. 이 목록에 항목이 있다는 사실만으로 사용자가 프로파일을 설치했다고 보지 않습니다.

### UserConfigurationProfiles 폴더

`HomeDomain :: Library/UserConfigurationProfiles/` 아래에도 같은 계열의 이름이 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0). `PayloadManifest.plist`(`HiddenProfiles`, `OrderedProfiles`), `PublicInfo/MCMeta.plist`(`LastMigratedBuild`)와 함께 제한 설정 키가 든 `EffectiveUserSettings.plist`, `PublicInfo/PublicEffectiveUserSettings.plist`, `PublicInfo/Truth.plist`, `Truth.plist` 가 있었고, `ClientTruth.plist`, `PayloadDependency.plist`, `ProfileTruth.plist`, `PublicInfo/NamespacedUserSettings.plist`, `UserSettings.plist` 는 키가 비어 보였습니다. 두 폴더가 어떻게 나뉘어 쓰이는지는 확인하지 못했습니다.

### 제한 설정 키

제한 설정은 `restrictedBool`, `restrictedValue`, `union`, `intersection` 네 묶음으로 나뉘어 있었고, 묶음마다 보인 키 이름의 예는 아래와 같습니다(확인 범위: iPhone 13 mini, iOS 27.0).

| 묶음 | 키 이름 예 |
|---|---|
| `restrictedBool` | `allowAirDrop`, `allowAppInstallation`, `allowAppRemoval`, `allowAccountModification`, `allowAirPrintCredentialsStorage`, `allowAssistant` |
| `restrictedValue` | `maxGracePeriod`, `maxInactivity`, `minLength`, `passcodeKeyboardComplexity`, `simplePasscodeComplexity`, `enforcedSoftwareUpdateDelay`, `safariAcceptCookies` |
| `restrictedValue`(`Truth.plist`·`PublicInfo/Truth.plist` 에만 보임) | `maxFailedAttempts`, `maxPINAgeInDays`, `minComplexChars`, `pinHistory` |
| `union` | `allowedSafariPasswordAutoFillDomains`, `managedWebDomains`, `blockedAppBundleIDs`, `trustedCodeSigningIdentities`, `webContentFilterBlacklistedURLs` |
| `intersection` | `managedEmailDomains`, `webContentFilterWhitelistedURLs`, `appLockBundleIDs` |

이 키들은 걸 수 있는 제한 항목의 전체 목록일 수도 있어서, 키가 있다는 사실만으로 그 제한이 걸렸다고 볼 수 없고 값을 열어 봐야 합니다. `allowedSafariPasswordAutoFillDomains` 는 이름으로 보아 관리 기기에서 암호 자동 완성을 허용하는 도메인이고, 저장된 암호와의 관계는 [저장된 암호](saved-passwords.md) 페이지에 적었습니다.

### ManagedPreferencesDomain

관찰한 백업에서 두 파일의 키는 아래와 같았습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
mobile/.GlobalPreferences.plist
  com.apple.system.SpellCheckAllowed, com.apple.system.AutoCorrectionAllowed,
  com.apple.content-rating.AppRating, com.apple.content-rating.MovieRating,
  com.apple.content-rating.TVShowRating, com.apple.content-rating.ExplicitBooksAllowed,
  com.apple.content-rating.ExplicitMusicPodcastsAllowed, INNextHeartbeatDate, INNextFreshmintRefreshDateKey
mobile/com.apple.webcontentfilter.plist
  filterBlacklist, filterWhitelist, limitWebProxies, noOverridingAllowed, restrictWeb,
  useContentFilter, useContentFilterOverrides, useTransitiveTrust, whitelistEnabled
```

웹 콘텐츠 필터 설정이 MDM 에서 왔는지 [화면 사용 시간](../app-usage/screen-time.md)의 제한에서 왔는지는 확인하지 못했으니, 두 쪽을 함께 봅니다.

### 뜻을 확인하지 못한 항목

아래 항목은 이름이 기기 관리와 관련되어 보이지만 뜻을 확인하지 못했고, 모두 관찰한 백업에서 이름만 확인했습니다(확인 범위: iPhone 13 mini, iOS 27.0).

| 위치 | 키 | 비고 |
|---|---|---|
| `HomeDomain :: Library/Preferences/com.apple.managedconfiguration.profiled.plist` | `MCFeatureHealthDataSubmissionAllowedVersion` (int) | 프로파일 데몬 설정으로 보임 |
| `HomeDomain :: Library/Preferences/com.apple.remotemanagement.ManagedSettingsSubscriber.plist` | `RemovedLegacySystemSharedContainers` (bool) | 원격 관리 설정으로 보임 |
| `HomeDomain :: Library/Preferences/com.apple.managedappdistributiond.plist` | `lastKnownBuild` (str), `LastWeeklyCAEventsPost` (datetime), `dayLockReasons` (int) | 관리 앱 배포 데몬 설정으로 보임 |
| `SysContainerDomain-com.apple.managedappdistributiond :: distributor-preferences-store.plist` | `doNotShowSheetList` (list) | 무엇을 담는지 확인하지 못함 |
| `SysSharedContainerDomain-systemgroup.com.apple.icloud.findmydevice.managed :: Library/Preferences/FMIPStateInfo.plist` | `fmipActive` (bool), `fmipLostModeType` (int) | MDM 분실 모드와의 관계는 확인하지 못함. 나의 찾기는 [나의 찾기](../location/find-my.md) |

### 이름이 비슷하지만 다른 것

`MobileDeviceDomain :: ProvisioningProfiles/mis.db` 는 이름에 "profile" 이 들어가지만, 표 이름으로 보아 구성 프로파일이 아니라 개발자·기업 배포 앱의 서명에 쓰는 프로비저닝 프로파일 (provisioning profile)을 담는 DB 로 보입니다. 연 문서로는 확인하지 못했고, 관찰한 백업의 주요 표는 아래와 같았습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
profiles: uuid, team_id, install_time, name, expires, is_for_all_devices, is_apple_internal, is_local, is_beta, cms_blob, is_der
team_id_info: team_id, team_name
trusted_team_ids: team_id, signature
online_auth: uuid, cdhash, grace_period, last_success_monotonic_time, last_success_reset_count, is_rejected, is_rejected_by_whole_profile
```

그 밖에 `banned_cdhashes`, `banned_profile_uuids`, `certificate_provisioning_cache`, `certificates`, `entitlements_provisioning_cache`, `legacy_profile_grace_periods`, `online_auth_migration_state`, `settings`, `signing_identities`, `xml_profiles_cache` 표가 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0). 앱 서명과 앱 번들은 [앱 번들 정보](../embedded-metadata/app-bundle.md) 페이지에서 다룹니다.

`ProtectedDomain :: trustd/private/TrustStore.sqlite#` 에는 `tsettings` 표(`subj`, `tset`, `data`, `uuid` 와 이름을 가린 칸 1개)가 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0). 이름으로 보아 사용자가 신뢰한 인증서 설정이고 프로파일로 설치한 루트 인증서와 이어질 수 있지만, 확인하지 못했습니다.

## 증거로서 의미

### 증명하는 것

`PayloadManifest.plist` 의 `OrderedProfiles` 에 항목이 있으면 백업 시점에 기기에 프로파일이 있었다는 정황이 되고, 제한 설정 키의 값을 열어 제한이 걸려 있었다면 백업 시점에 그 제한이 적용되고 있었다는 근거로 쓸 수 있습니다. `IsSupervised` 값은 이름으로 보아 기기가 감독 대상인지 보여 주고, 감독은 대개 조직 소유를 뜻하니 [3] 개인 기기인지 조직 기기인지 판단하는 출발점이 됩니다. 사고 대응에서는 사용자가 모르는 사이 메일·웹으로 받은 프로파일이 설정과 권한을 바꿨는지가 확인 대상이라서, 프로파일 목록과 신뢰 인증서, 제한 설정을 함께 봅니다.

### 증명하지 못하는 것

프로파일이 있다는 사실만으로 사용자가 직접 설치했다고 말할 수 없는데, MDM 과 Apple Configurator 도 프로파일을 설치하고 [1] 통신사 설정처럼 처음부터 들어 있을 수 있는 항목도 보이기 때문입니다(확인 범위: iPhone 13 mini, iOS 27.0). 백업에 MDM 서버 주소와 등록 시각이 어디 남는지는 확인하지 못해서, 어느 조직이 기기를 관리했는지를 이 페이지의 파일만으로 밝히지 못합니다. 제한 키 이름이 있다는 사실은 제한이 걸렸다는 뜻이 아니고, 프로파일이 지금 없다는 사실도 설치된 적이 없다는 뜻이 아닙니다.

보고서에는 "피의자가 악성 프로파일을 설치했다" 가 아니라 "백업 시점의 프로파일 목록에 이 식별자의 프로파일이 있고, 이 프로파일이 설정한 제한 값은 이러하다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

사용자가 직접 설치하는 프로파일은 받은 뒤 8분 안에 설치해야 하므로 [2], 메일이나 웹에서 받은 시각과 설치 시각은 가깝게 붙습니다. 그래서 설치 시각을 찾았다면 그 앞 몇 분 동안의 메일·메시지·Safari 기록을 먼저 봅니다. 다만 `ProfileEvents` 목록 안에 시각 값이 있는지, 있다면 어떤 기준인지는 확인하지 못했습니다.

`mis.db` 의 `install_time`·`expires`, `managedappdistributiond.plist` 의 `LastWeeklyCAEventsPost` 도 기준 시각을 확인하지 못했습니다. plist 의 날짜 형식은 [속성 목록 파일](../../01-foundations/data-formats/plist.md), 기준 시각을 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지를 보고, 값을 바꿀 때 가정한 기준을 보고서에 함께 적습니다.

## 함정과 한계

기기 전체를 지우면 프로파일이 모두 없어지고 [1], 사용자나 MDM 이 프로파일 하나만 지울 수도 있습니다 [1]. 프로파일을 지운 뒤 `ProfileEvents` 나 다른 파일에 제거 흔적이 남는지는 확인하지 못했으니, 프로파일이 없다는 결과를 보고할 때는 수집 시점과 [초기화와 복원 흔적](../system-account/erase-restore.md)을 함께 적습니다. 감독하지 않은 기기에서는 기기 암호를 아는 사람이 제거 제한이 걸린 수동 설치 프로파일도 지울 수 있어서 [1], 제거 제한이 있었다는 사실이 프로파일이 끝까지 남았다는 근거가 되지는 않습니다.

`HiddenProfiles`, `ProfileEvents`, `ConfigurationSource`, `PostSetupProfileWasInstalled` 같은 키는 이름이 뜻을 짐작하게 하지만 정의 문서를 확인하지 못했습니다. 이 키들로 결론을 낼 때는 시험 기기에서 프로파일을 설치·제거하며 값이 어떻게 바뀌는지 직접 검증한 결과만 씁니다. 관찰은 iOS 27.0 한 대의 백업에서만 했으니 다른 버전에서 파일과 키가 같은지도 따로 확인합니다. 이 페이지는 프로파일이나 감독을 우회하거나 지우는 방법을 다루지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

이 페이지에는 검체에서 뽑은 바이트를 싣지 않습니다. 아래 순서로 직접 따라가 봅니다.

1. 백업의 Manifest.db 에서 `SysSharedContainerDomain-systemgroup.com.apple.configurationprofiles` 도메인의 행을 모두 뽑아 상대 경로와 실제 파일 이름을 짝지어 적습니다. Manifest.db 읽는 법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 페이지에 있습니다.
2. `CloudConfigurationDetails.plist` 를 헥스 편집기로 열어 이진 plist 머리를 확인하고, 객체 영역에서 `IsSupervised` 문자열과 그 값 객체를 찾아 참·거짓 표시 바이트를 읽습니다. 표시 바이트 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 페이지를 따릅니다.
3. `PayloadManifest.plist` 에서 `OrderedProfiles`·`HiddenProfiles` 배열의 원소 개수를 세고, 원소가 어떤 객체 종류인지 확인합니다.
4. `MCProfileEvents.plist` 의 `ProfileEvents` 배열 안 항목을 열어 키 이름을 적고, 날짜 객체가 있으면 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지를 따라 바꿔 봅니다.

### 공개 도구로 한 번

plist 는 plist 를 읽는 공개 도구(예: Python 표준 라이브러리 plistlib)로 열어 위 구조 절의 키와 값을 확인합니다. `mis.db` 와 `TrustStore.sqlite#` 는 SQLite 를 여는 공개 도구(예: sqlite3 명령줄 도구)로 열어 표 구조를 먼저 확인하고, `cms_blob` 처럼 이진 값이 든 칸은 따로 저장해 형식을 확인합니다. 도구가 보여 준 해석과 헥스로 본 값을 맞춰 보는 절차는 [도구 검증](../../03-techniques/reporting/tool-validation.md) 페이지를 봅니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [VPN 설정](../network/vpn.md) | 프로파일과 함께 들어온 VPN 설정 |
| [사파리](../browsers/safari/index.md) | 프로파일을 받은 웹 페이지 방문 기록과 시각 |
| [메일 앱](../mail-cloud/apple-mail.md) | 프로파일을 첨부한 메일의 수신 시각 |
| [메시지](../communications/messages/index.md) | 프로파일 링크가 든 메시지 |
| [설치된 앱](../app-usage/installed-apps.md) | 관리 앱과 기업 배포 앱 |
| [화면 사용 시간](../app-usage/screen-time.md) | 웹 콘텐츠 필터와 앱 제한의 출처 |
| [암호와 Face ID 설정 흔적](../system-account/passcode-biometrics.md) | 암호 정책 제한과 도난 기기 보호 설정 |
| [초기화와 복원 흔적](../system-account/erase-restore.md) | 프로파일이 사라진 시점과 기기 지우기 |
| [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md) | 모르는 프로파일과 신뢰 인증서 점검 |
| [악성 코드는 어디서 들어왔나](../../04-scenarios/incident/initial-access.md) | 메일·웹으로 받은 프로파일이 첫 진입점인지 |
| [스미싱 흔적](../../04-scenarios/incident/smishing.md) | 문자 링크로 받은 프로파일 |

## 실습

공개 검체(NIST CFReDS 등)의 아이폰 이미지나 백업으로 아래 질문을 풀어 봅니다. 검체가 개인 기기라면 MDM 흔적이 없을 수 있으니, 없으면 없다는 사실과 그 근거로 본 파일을 적는 것까지 연습합니다.

1. 검체의 iOS 버전과 수집 방식을 확인하고, 이 페이지의 도메인 표에 있는 도메인과 항목 수를 검체와 비교합니다.
2. `CloudConfigurationDetails.plist` 의 `IsSupervised` 값을 읽고, 이 값만으로 조직 기기라고 쓸 수 있는지 보고서 문장으로 적어 봅니다.
3. `PayloadManifest.plist` 의 `OrderedProfiles`·`HiddenProfiles` 원소를 모두 적고, 각 원소가 통신사 설정처럼 기본으로 들어 있는 것인지 사용자가 설치한 것인지 가려 봅니다.
4. 제한 설정 키 가운데 값이 기본값과 다른 것을 찾아 목록으로 만들고, [화면 사용 시간](../app-usage/screen-time.md) 흔적과 맞춰 봅니다.
5. 시험 기기에 직접 만든 프로파일을 설치했다가 지운 뒤 백업을 두 번 떠서 `ProfileEvents` 가 어떻게 바뀌는지 비교해 봅니다.

## 참고 문헌

1. Apple Platform Deployment — Intro to device management profiles — https://support.apple.com/guide/deployment/intro-to-mdm-profiles-depc0aadd3fe/web
2. Apple Support — Install a configuration profile on iPhone, iPad, or Apple Vision Pro (102400) — https://support.apple.com/en-us/102400
3. Apple Platform Deployment — About Apple device supervision — https://support.apple.com/guide/deployment/about-device-supervision-dep1d89f0bff/web
