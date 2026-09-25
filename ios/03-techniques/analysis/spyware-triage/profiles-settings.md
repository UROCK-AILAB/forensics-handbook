---
title: "구성 프로파일과 설정으로 찾기"
parent: "악성 코드·스파이웨어 흔적"
grand_parent: "기법 · 분석"
nav_order: 1360
---

# 구성 프로파일과 설정으로 찾기 (Profiles·Settings)

설치된 구성 프로파일, 제한 설정, App Store 밖 앱 서명, 앱 권한과 위치 요청 기록을 백업에서 읽어 기기 설정이 다른 사람이나 조직의 관리 아래 들어가 있는지 확인하는 방법입니다.

## 언제 쓰나

Apple 은 구성 프로파일(configuration profile)이 계정 설정과 기기 기능을 관리하고, 기기의 데이터나 위치 정보에 접근을 허용할 수도 있다고 설명하며, VPN 설정과 메일 계정 설정을 예로 듭니다 [1]. 누군가 기기를 잠시 가져갔다가 돌려줬다는 진술이 있거나, 회사·학교와 관계없는 개인 기기에서 관리 흔적이 보이거나, 감시가 의심되는데 지표 대조에서 걸린 것이 없을 때 이 점검을 합니다. 알려진 스파이웨어 지표와 대조하는 방법은 [스파이웨어 흔적 찾기 (MVT)](spyware-mvt.md) 에서, 가까운 사람이 설치한 감시 앱과 안전 확인(Safety Check) 화면은 [감시 앱 흔적 (Stalkerware)](stalkerware.md) 에서 다룹니다. 구성 프로파일 파일 자체의 구조는 [구성 프로파일과 MDM](../../../02-artifacts/credentials-security/configuration-profiles.md) 페이지가 본문이고, 이 페이지는 감염·감시 점검에 쓰는 순서와 볼 곳을 정리합니다.

이 페이지에서 "(확인 범위: iPhone 13 mini, iOS 27.0)" 가 붙은 경로와 키는 암호화하지 않은 로컬 백업에서 이름만 확인한 것이고, 값은 보지 않았습니다.

## 절차

1. **화면부터 기록합니다.** 아이폰에 설치된 프로파일은 설정 → 일반 → VPN 및 기기 관리 에 나옵니다 [1]. 이 화면을 사진으로 남기되 이 단계에서는 지우지 않습니다. Apple 안내에 따르면 프로파일을 지우면 그 프로파일의 설정과 정보가 모두 지워지고, VPN 프로파일이라면 그 네트워크 접속도 끊깁니다 [1]. 학교나 회사 기기라면 지우기 전에 관리자에게 확인하라고도 안내합니다 [1].

2. **로컬 백업을 받습니다.** 백업 형식과 도메인 이름 읽는 법은 [로컬 백업](../../../01-foundations/backups/local-backup/index.md) 에, 수집 절차는 [모바일 증거 확보](../../acquisition/mobile-acquisition/index.md) 에 있습니다.

3. **구성 프로파일 기록을 엽니다.** 백업 도메인 `SysSharedContainerDomain-systemgroup.com.apple.configurationprofiles` 에 항목이 19개 있었고, 그 가운데 `Library/ConfigurationProfiles/` 아래 plist 는 아래와 같습니다 (확인 범위: iPhone 13 mini, iOS 27.0).

   | 파일 | 관찰한 키 |
   |---|---|
   | `MCProfileEvents.plist` | `ProfileEvents` (list) |
   | `PayloadManifest.plist` | `HiddenProfiles` (list), `OrderedProfiles` (list) |
   | `CloudConfigurationDetails.plist` | `AllowPairing`, `CloudConfigurationUIComplete`, `ConfigurationSource`, `IsSupervised`, `PostSetupProfileWasInstalled` |
   | `MCSettingsEvents.plist` | `EffectiveSettings`, `Restrictions`, `SystemClientRestrictions`, `SystemProfileRestrictions`, `SystemSettings` |
   | `ClientTruth.plist` | 클라이언트 항목마다 `clientRestrictions`, `clientType`, `compliant`, `localizedClientDescription` |
   | `UserSettings.plist` | `assignedObject`, `intersection`, `restrictedBool`, `restrictedValue`, `union` |
   | `PublicInfo/MCMeta.plist` | `LastMDMMigratedBuild`, `LastMigratedBuild` |
   | `AppAccessibilityParameters.plist`, `PayloadDependency.plist`, `ProfileTruth.plist`, `PublicInfo/NamespacedUserSettings.plist` | 관찰 메모에 키가 적혀 있지 않음 |

   `PayloadManifest.plist` 의 `HiddenProfiles` 와 `OrderedProfiles` 목록을 설정 화면에서 찍은 목록과 맞춰 보고, 화면에 없는 항목이 목록에 있는지 봅니다. 사용자 쪽 복사본은 `HomeDomain` 의 `Library/UserConfigurationProfiles/` 아래에 `ClientTruth.plist`, `EffectiveUserSettings.plist`, `PayloadDependency.plist`, `PayloadManifest.plist`, `ProfileTruth.plist`, `PublicInfo/MCMeta.plist`, `PublicInfo/NamespacedUserSettings.plist`, `PublicInfo/PublicEffectiveUserSettings.plist`, `PublicInfo/Truth.plist`, `Truth.plist`, `UserSettings.plist` 로 따로 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 프로파일 원본 파일이 백업의 어디에 어떤 이름으로 남는지는 확인하지 못했습니다.

4. **제한 설정을 봅니다.** `UserSettings.plist` 의 하위 키 가운데 앱 설치·삭제, 계정 변경, 서명 신뢰, 웹 필터, 암호 조건을 이름으로 가리키는 키를 먼저 봅니다. 아래 키는 모두 관찰한 백업에 이름이 있었고 (확인 범위: iPhone 13 mini, iOS 27.0), 값은 보지 않았으며 각 키가 정확히 무엇을 제한하는지도 이 페이지에서 확인하지 않았습니다.

   | 상위 키 | 먼저 볼 하위 키 |
   |---|---|
   | `union` | `trustedCodeSigningIdentities`, `blockedAppBundleIDs`, `removedSystemAppBundleIDs`, `managedWebDomains`, `webContentFilterBlacklistedURLs` |
   | `restrictedBool` | `allowAppInstallation`, `allowAppRemoval`, `allowAccountModification`, `allowAirDrop` |
   | `restrictedValue` | `minLength`, `maxInactivity`, `passcodeKeyboardComplexity` |

5. **관리(MDM) 흔적을 봅니다.** `CloudConfigurationDetails.plist` 의 `IsSupervised`, `ConfigurationSource`, `PostSetupProfileWasInstalled` 는 이름으로 보면 감독 여부와 설정 출처를 가리키는 것 같지만, 값이 무엇을 뜻하는지는 확인하지 못했습니다. 관리와 관련된 도메인으로는 `ManagedPreferencesDomain`(항목 4개), `SysContainerDomain-com.apple.remotemanagementd`(항목 6개), `SysContainerDomain-com.apple.managedappdistributiond`(항목 2개)가 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). `ManagedPreferencesDomain` 안에는 `mobile/.GlobalPreferences.plist` 와 `mobile/com.apple.webcontentfilter.plist` 가 있었고, 뒤의 파일에는 `filterBlacklist`, `filterWhitelist`, `restrictWeb`, `useContentFilter`, `limitWebProxies` 같은 키가 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0).

6. **App Store 밖 서명을 봅니다.** `MobileDeviceDomain :: ProvisioningProfiles/mis.db` 에 아래 표가 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0).

   | 표 | 칸 |
   |---|---|
   | `profiles` | `uuid`, `team_id`, `install_time`, `name`, `expires`, `is_for_all_devices`, `is_apple_internal`, `is_local`, `is_beta`, `cms_blob`, `is_der` |
   | `trusted_team_ids` | `team_id`, `signature` |
   | `team_id_info` | `team_id`, `team_name` |
   | `banned_profile_uuids`, `banned_cdhashes`, `online_auth` | 차단·온라인 인증 관련 이름의 표 |

   `profiles` 표의 `team_id` 를 `team_id_info` 의 `team_name` 과 이어 보면 어느 개발자 팀의 서명 프로파일인지 이름을 붙일 수 있습니다. 다만 이 DB 가 기업 배포·개발용으로 App Store 밖에서 설치한 앱의 프로비저닝 프로파일을 기록한다는 해석과 `install_time` 의 시각 기준은 공개 문서로 확인하지 못했습니다. 설치 앱 목록은 MVT Applications 모듈이 백업의 `Info.plist` 에서 뽑고, 이 기록에는 앱의 출처와 설치 정보가 담긴다고 MVT 문서는 설명합니다 [2]. 관찰한 백업의 `Info.plist` 에는 `Installed Applications` 와 `Applications` 키가 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 설치 앱 전반은 [설치된 앱](../../../02-artifacts/app-usage/installed-apps.md) 에서 다룹니다.

7. **권한과 위치 요청을 봅니다.** MVT TCC 모듈은 `/private/var/mobile/Library/TCC/TCC.db` 에서 마이크·카메라·위치 같은 권한의 허용·거부 상태를 뽑습니다 [2]. 이 DB 는 백업에 `HomeDomain :: Library/TCC/TCC.db` 로 있었고, `access` 표에 `service`, `client`, `client_type`, `auth_value`, `auth_reason`, `last_modified` 같은 칸이, 그 밖에 `access_overrides`, `managed_overrides`(`admin_auth_value` 칸 포함), `expired`, `policies` 표가 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). MVT LocationdClients 모듈은 `/private/var/mobile/Library/Caches/locationd/clients.plist` 에서 위치 서비스를 요청한 앱을 뽑습니다 [2]. 이 파일은 백업의 `RootDomain :: Library/Caches/locationd/clients.plist` 에 있었고, 항목 하위 키로 `Authorization`, `BundleId`, `BundlePath`, `Executable`, `BackgroundLocationCapability`, `VisitMonitoring`, `isSystemService`, `LocationTimeStopped` 등이 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 두 파일에서 사용자가 모르는 번들 ID 가 마이크·카메라·위치 권한이나 백그라운드 위치를 받았는지 봅니다.

8. **차단 모드 상태를 봅니다.** MVT GlobalPreferences 모듈은 `/private/var/mobile/Library/Preferences/.GlobalPreferences.plist` 에서 차단 모드(Lockdown Mode) 상태 등을 뽑습니다 [2]. 상태를 담는 키 이름은 확인하지 못했습니다.

9. **시간순으로 모읍니다.** MVT ProfileEvents 모듈은 설정 앱에서 프로파일을 새로 설치하거나 지운 때를 시간순으로 뽑고, ConfigurationProfiles 모듈은 설치된 구성 프로파일의 자세한 정보를 뽑습니다 [2]. ProfileEvents 모듈이 읽는 파일이 `MCProfileEvents.plist` 인지는 문서에서 확인하지 못했습니다. 뽑은 사건은 [타임라인 작성](../timeline/index.md) 방식으로 기기를 넘겨받은 시기, 진술한 시기와 나란히 놓습니다.

## 도구

MVT(Mobile Verification Toolkit)의 ConfigurationProfiles, ProfileEvents, Applications, TCC, LocationdClients, GlobalPreferences 모듈이 이 페이지의 파일 대부분을 읽습니다 [2]. 모듈이 다루지 않는 파일(`UserSettings.plist`, `CloudConfigurationDetails.plist`, `mis.db` 등)은 plist 뷰어와 sqlite3 같은 공개 도구로 직접 엽니다. 읽는 법은 [속성 목록 파일](../../../01-foundations/data-formats/plist.md) 과 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md) 에 있습니다.

## 함정과 한계

항목이 있다는 사실만으로 수상하다고 보면 안 됩니다. 사용자가 직접 프로파일을 설치하지 않은 개인 기기로 보이는 관찰 기기에서도 `MCSettingsEvents.plist` 의 `SystemProfileRestrictions` 아래에 통신사 이름이 들어간 `com.apple.` 형식 프로파일 식별자가 1개, `SystemClientRestrictions` 아래에 `com.apple.lsd.appremoval` 같은 Apple 시스템 항목이 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). `ClientTruth.plist` 에도 `com.apple.lsd.appremoval`, `com.apple.profiled.appenforced.com.apple.news` 같은 시스템 클라이언트 항목이 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 식별자가 `com.apple.` 로 시작하는지, 통신사나 Apple 기본 항목인지를 먼저 가르고 나머지를 봅니다.

이 페이지의 키는 이름만 확인했고, `ConfigurationSource` 숫자의 뜻이나 `IsSupervised` 가 감독 여부를 그대로 나타내는지는 확인하지 못했습니다. `TCC.db` 의 `last_modified`, `mis.db` 의 `install_time` 도 어떤 기준의 시각인지 확인하지 못했고, 보고서에 시각을 쓰기 전에 [시각 값](../../../01-foundations/value-decoding/time-values.md) 의 방법으로 알려진 사건과 맞춰 봐야 합니다. 관찰은 암호화하지 않은 백업에서 했고, 감독 기기에서 사용자가 지울 수 없는 프로파일이 있는지도 확인하지 못했습니다. 조사 전에 누군가 프로파일을 지웠다면 Apple 안내대로 그 설정과 정보가 지워지고 [1], `MCProfileEvents.plist` 같은 사건 기록이나 사용자 쪽 복사본에 무엇이 남는지는 검체로 따로 확인해야 합니다.

## 결과를 어떻게 해석하나

이 점검으로 증명할 수 있는 범위는 "이 백업 시점에 이 식별자의 구성 프로파일이 설치 목록에 있었다", "이 번들 ID 가 위치 권한을 받은 기록이 있다" 까지입니다. 누가 프로파일을 설치했는지, 설치한 사람이 그 설정으로 무엇을 봤는지는 이 기록만으로 증명하지 못합니다. 보고서에는 "`PayloadManifest.plist` 의 프로파일 목록에 설정 화면에 표시되지 않은 식별자 1개가 있다" 처럼 파일과 키 이름을 밝혀 기록이 말하는 만큼만 씁니다. 모르는 프로파일이 VPN 이라면 [VPN 설정](../../../02-artifacts/network/vpn.md), 계정 쪽 흔적은 [애플 계정](../../../02-artifacts/system-account/apple-account.md) 과 함께 봅니다.

## 참고 문헌

1. Review and delete configuration profiles — Apple Personal Safety User Guide — https://support.apple.com/guide/personal-safety/review-and-delete-configuration-profiles-ips327569a75/web
2. Records extracted by mvt-ios — Mobile Verification Toolkit — https://docs.mvt.re/en/latest/ios/records/
