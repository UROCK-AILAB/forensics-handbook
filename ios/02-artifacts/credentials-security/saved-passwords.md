---
title: "저장된 암호"
parent: "아티팩트 · 자격 증명·보안 설정"
nav_order: 1110
---

# 저장된 암호 (Passwords·iCloud Keychain)

저장된 암호는 키체인에 들어 있는 계정 암호·패스키·인증 코드이고, iOS 18 부터는 암호 (Passwords) 앱이 이를 한곳에 모아 보여 줍니다. 로컬 백업에서는 암호 목록보다 키체인 백업 파일과 암호 앱의 설정·갱신 시각 키가 먼저 눈에 들어옵니다.

## 무엇을 기록하나 · 왜 생기나

iOS 18·iPadOS 18·macOS Sequoia·visionOS 2 부터 암호 앱이 암호와 패스키, 인증 코드를 관리합니다 [2]. 앱 한 곳에서 계정 암호와 패스키, Wi-Fi 암호, 2단계 인증에 쓰는 인증 코드, 약하거나 유출된 암호에 대한 보안 알림을 볼 수 있습니다 [2]. 동기화는 iCloud 키체인 (iCloud Keychain)이 맡아서 승인된 Apple 기기 모두에 암호와 패스키, 그 밖의 계정 정보를 똑같이 맞추고 [2], 공유 그룹 (Shared Groups)으로 가족이나 믿는 연락처와 암호를 나눠 쓰거나 암호 하나를 AirDrop 으로 보낼 수도 있습니다 [2]. iOS 17 이하에서 저장된 암호를 설정 앱의 어느 화면에서 보여 줬는지, 최근 삭제 항목 (Recently Deleted)을 며칠 동안 두는지는 해당 버전 기기에서 확인합니다.

암호가 실제로 들어가는 곳은 키체인이고, 키체인의 저장 방식과 접근 규칙은 [키체인](../../01-foundations/storage/keychain.md) 페이지에서 다룹니다. 이 페이지와 직접 이어지는 사실만 보면, Safari 암호는 잠금 해제 중에만(When unlocked) 쓸 수 있는 보호 등급이고, Wi-Fi 암호는 처음 잠금 해제 뒤(After first unlock) 등급입니다 [3]. 암호 앱 항목 전체가 Safari 암호와 같은 등급인지는 실제 데이터로 확인하고, 등급마다 언제 풀리는지는 [데이터 보호](../../01-foundations/storage/data-protection/index.md) 페이지를 봅니다.

유출 암호 검사 (Password Monitoring)는 저장된 암호를 유출로 알려진 암호 목록과 대조하는 기능이고, 대상은 암호 자동 완성 키체인(Password AutoFill keychain)의 암호입니다 [1]. 가장 흔히 유출된 암호는 기기 안의 목록으로 바로 대조해 서버에 묻지 않고, 덜 흔한 암호는 암호 해시의 앞 15비트만 Apple 서버로 보내 타원 곡선 기반의 비공개 교집합(private set intersection) 방식으로 대조합니다 [1]. 유출 위험이 낮은 암호일수록 Apple 과 나누는 정보가 적도록 설계되어 있습니다 [1]. 재사용하거나 약한 암호를 어떻게 판정하는지는 [1]에 없습니다.

## 위치와 버전별 차이

### 버전별 범위

| iOS | 내용 | 출처 |
|---|---|---|
| 17 이하 | 저장된 암호를 보여 준 화면은 실제 기기에서 확인 | — |
| 18 이후 | 암호 앱이 암호·패스키·인증 코드를 관리 | [2] |
| 27.0 | 로컬 백업 속 키체인 백업 파일, 암호 앱 도메인과 plist 키 이름 | — |

### 로컬 백업에서 볼 곳

iOS 27.0 기기를 Windows 의 Apple 기기 앱으로 암호화하지 않고 백업하면 아래 항목이 들어 있습니다.

| 백업 위치 | 알려 주는 것 |
|---|---|
| `KeychainDomain :: keychain-backup.plist` | 키체인 백업. 도메인 안 항목은 2개 |
| `AppDomain-com.apple.Passwords :: Library/Preferences/com.apple.Passwords.plist` | 암호 앱의 설정과 갱신 시각으로 보이는 키. 도메인 안 항목은 5개 |
| `AppDomainPlugin-com.apple.Passwords.DataMigration`, `AppDomainPlugin-com.apple.Passwords.PasswordManagerAppIntentsExtension`, `AppDomainPlugin-com.apple.Passwords.PasswordSettingsAppIntentsExtension` | 암호 앱 확장 도메인. 각각 항목 4개 |
| `AppDomain-com.apple.mobilesafari :: Library/Preferences/com.apple.mobilesafari.plist` | 유출 암호 경고 검사로 보이는 이름의 키 |
| `AppDomain-com.apple.mobilesafari :: Library/Preferences/com.apple.Safari.PasswordBreachAgent.plist` | 유출 검사 구성의 갱신 시각으로 보이는 키 |
| `HomeDomain :: Library/Preferences/com.apple.Safari.PasswordBreachAgent.plist` | 위와 같은 이름의 파일이 HomeDomain 에도 있음 |
| `HomeDomain :: Library/Preferences/com.apple.WebUI.plist` | 암호·신용카드 자동 완성 기본값으로 보이는 키 |
| `RootDomain :: Library/Preferences/com.apple.security.cloudkeychainproxy#.keysToRegister.plist` | 이름으로 보면 iCloud 키체인 동기화 프록시 설정 |

기기 안 키체인 DB 파일의 경로는 파일 시스템 추출본에서 직접 확인하고, 확인한 경로만 보고서에 씁니다.

## 구조

### keychain-backup.plist

iOS 27.0 백업에서 최상위 키는 아래 다섯 개입니다.

```
keybag-uuid (str)
genp (list)
inet (list)
cert (list)
keys (list)
```

키체인 항목 종류(item class)에는 일반 암호 `kSecClassGenericPassword`, 인터넷 암호 `kSecClassInternetPassword`, 인증서 `kSecClassCertificate`, 키 `kSecClassKey`, 인증서와 개인 키를 묶은 신원 `kSecClassIdentity` 가 있습니다 [4]. 목록 이름 `genp`·`inet`·`cert`·`keys` 는 앞의 네 종류와 이름 모양이 같지만, 짧은 이름과 상수를 짝지은 표는 [4]에 없습니다. `keybag-uuid` 는 이름으로 보면 키 가방 (keybag)의 식별자이고, 키 가방은 [데이터 보호](../../01-foundations/storage/data-protection/index.md) 페이지에서 다룹니다. Safari 와 암호 앱의 암호가 `genp` 와 `inet` 가운데 어느 쪽에 들어가는지는 실제 데이터에서 항목을 열어 확인합니다.

암호화하지 않은 백업에도 `keychain-backup.plist` 가 들어 있습니다. 백업 암호를 걸었는지에 따라 키체인이 어떻게 보호되고 어떤 항목이 백업에 들어가는지는 [로컬 백업](../../01-foundations/backups/local-backup/index.md)과 [키체인](../../01-foundations/storage/keychain.md) 페이지에서 다룹니다.

### 암호 앱 설정 plist

`com.apple.Passwords.plist` 의 키는 아래와 같고, 이 밖에 키가 2개 더 있습니다.

```
WBSPrivacyProxyAvailabilitySubscriberTier (bool)
WBSSecurityRecommendationsBiomeDonationLastDate (datetime)
WBSPrivacyProxyAvailabilityTraffic (int)
WebsiteNameProviderLastUpdateTime (datetime)
WBSRemoteAutoFillQuirksLastUpdateTime (datetime)
ShowServiceNamesInPasswords (bool)
shouldShowAppOnboardingView (bool)
WBSPrivacyProxyAvailabilityServiceStatus (int)
WBSPrivacyProxyAvailabilityActiveOnDefaultNetwork (bool)
WBSPrivacyProxyAvailabilityAccountType (int)
WBSPasswordWarningTopFraudTargetsLastUpdate (datetime)
```

키는 설정값과 갱신 시각뿐이고 저장된 암호 목록은 이 plist 에 없습니다. `WBSSecurityRecommendationsBiomeDonationLastDate` 는 이름으로 보면 보안 권장 사항을 [바이옴](../app-usage/biome/index.md)에 넘긴 마지막 시각이고, `shouldShowAppOnboardingView` 는 첫 실행 안내 화면을 띄울지 정하는 값으로 보입니다. 두 키 모두 공개된 정의가 없어 이름으로 짐작한 뜻입니다.

### 유출 암호 경고로 보이는 키

`com.apple.mobilesafari.plist` 에는 아래 키가 있습니다.

```
lastPasswordWarningManagerUpdate (datetime)
lastPasswordWarningManagerUpdateHasNewWarnings (bool)
lastPasswordWarningManagerUpdateHashes (list)
PasscodeIsAvailable (bool)
```

이름으로 보면 유출 암호 경고를 마지막으로 검사한 시각과 새 경고가 생겼는지를 적은 값 같고, 공개된 정의는 없습니다. `com.apple.Safari.PasswordBreachAgent.plist` 에서는 mobilesafari 쪽에 `WBSPasswordBreachConfigurationBagLastUpdate` 하나가, HomeDomain 쪽에 `WBSPasswordBreachConfigurationBagLastUpdate`·`WBSPasswordWarningTopFraudTargetsLastUpdate` 가 있습니다. 이 키들이 앞에서 설명한 유출 암호 검사[1]와 어떻게 이어지는지는 시험 기기로 확인해야 합니다.

### 뜻이 밝혀지지 않은 항목

아래 항목도 같은 백업에 들어 있는 이름입니다. 이름은 암호·자격 증명과 관련되어 보이지만 공개된 정의가 없어, 뜻은 실제 데이터로 확인해야 합니다.

| 위치 | 키·항목 | 비고 |
|---|---|---|
| `AppDomain-com.apple.CredentialSharingService`, `AppDomainPlugin-com.apple.CredentialSharingService.ShareableCredentialsMessagesExtension` | 백업 도메인 | 공유 그룹·암호 공유와 이어지는지는 이름으로 본 짐작 |
| `AppDomain-com.apple.SubcredentialUIService`, `AppDomainPlugin-com.apple.SubcredentialUIService.SubcredentialInvitationMessagesExtension` | 백업 도메인 | 무엇을 담는지 공개 자료 없음 |
| `AppDomain-com.apple.AutoFillSuggestions` | 백업 도메인(항목 4개) | 무엇을 담는지 공개 자료 없음 |
| `HomeDomain :: Library/Preferences/com.apple.WebUI.plist` | `DefaultValueForPasswordAndCreditCardAutoFill` (bool) | 자동 완성 기본값으로 보임 |
| `HomeDomain :: Library/Preferences/com.apple.onetimepasscodes.plist` | `DeleteVerificationCodes` (bool) | "사용 후 인증 코드 삭제" 설정으로 보임 |
| `HomeDomain :: Library/BulletinBoard/VersionedSectionInfo.plist` | `sectionInfo` 안의 `com.apple.Passwords` | 알림 설정 항목. 알림 해석은 [알림 기록](../app-usage/notifications.md) |
| `HomeDomain :: Library/Preferences/com.apple.AppleMediaServices.plist` | `AMSSharedStoreReviewMetrics-com.apple.Passwords: {session-count, session-start-date}` | 앱을 연 횟수로 보임. 공개 자료 없음 |
| `RootDomain :: Library/Preferences/com.apple.security.cloudkeychainproxy#.keysToRegister.plist` | `AlwaysKeys`, `DSID`, `EnsurePeerRegistration`, `FirstUnlockKeys`, `KeyAccountUUID`, `PendingKeys`, `SyncBackupPeerIDs`, `SyncPeerIDs`, `UnlockedKeys` | 키마다 뜻은 공개 자료 없음. `DSID` 는 계정 식별자일 수 있어 [애플 계정](../system-account/apple-account.md)과 맞춰 봄 |
| `HomeDomain :: Library/Accounts/Accounts#.sqlite` | `ZCREDENTIALITEM` 표: `Z_PK, Z_ENT, Z_OPT, ZPERSISTENT, ZEXPIRATIONDATE, ZACCOUNTIDENTIFIER, ZSERVICENAME` | 계정 자격 증명 항목의 메타데이터로 보이고, 열 이름에 비밀 값은 없음 |

## 증거로서 의미

### 증명하는 것

백업에 암호 앱 도메인과 `com.apple.Passwords.plist` 가 있고 그 안에 갱신 시각 키가 있으면, 그 기기에 암호 앱이 있었고 앱 관련 작업이 한 번 이상 돌았다는 정황이 됩니다. 정상적인 수집 절차로 키체인 항목을 읽을 수 있었다면, 그 계정의 암호나 패스키가 수집 시점의 키체인에 있었다는 근거로 쓸 수 있습니다. 유출 경고로 보이는 키에 시각 값이 있으면 그 시각 무렵에 경고 검사가 돌았다는 정황으로 볼 수 있지만, 키의 뜻이 밝혀지지 않았으니 보고서에는 키 이름과 값만 적습니다.

### 증명하지 못하는 것

iCloud 키체인이 승인된 기기 모두에 암호를 맞추고 공유 그룹으로 다른 사람과 암호를 나눠 쓸 수 있어서 [2], 키체인에 암호가 있다는 사실만으로 이 기기 사용자가 이 기기에서 그 암호를 입력했다고 말할 수 없습니다. 암호가 저장되어 있다는 사실은 그 계정으로 로그인했다는 뜻도 아니니, 로그인 여부는 해당 앱이나 서비스의 기록으로 따로 확인합니다. 암호 앱의 설정 키와 갱신 시각 키는 어떤 계정의 암호가 있었는지 알려 주지 않고, 암호화하지 않은 백업에서 암호 목록을 읽지 못했다고 해서 기기에 저장된 암호가 없었다고 결론 내리지 않습니다.

보고서에는 "피의자가 이 계정 암호를 저장했다" 가 아니라 "수집 시점의 키체인에 이 서비스 이름의 인터넷 암호 항목이 있고, 이 항목은 iCloud 키체인으로 동기화된 것일 수 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`com.apple.Passwords.plist`, `com.apple.mobilesafari.plist`, `com.apple.Safari.PasswordBreachAgent.plist` 의 datetime 값이 어떤 기준으로 저장되는지는 실제 데이터로 확인합니다. 이진 plist 의 날짜 형식은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 페이지를, 기준 시각을 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지를 봅니다.

이름에 `LastUpdate`·`LastDate` 가 들어간 키는 이름으로 보면 설정이나 목록을 받아 온 시각이라서, 사용자가 화면을 만진 시각으로 읽지 않습니다. `ZCREDENTIALITEM` 의 `ZEXPIRATIONDATE` 도 기준 시각이 알려져 있지 않으니 값을 바꿀 때 어떤 기준을 가정했는지 보고서에 함께 적습니다.

## 함정과 한계

암호를 걸지 않은 백업에서도 키체인 백업 파일은 보이지만, 파일이 있다는 사실과 안의 항목을 읽을 수 있다는 사실은 별개입니다. 백업 암호를 걸었는지는 Manifest.plist 로 먼저 확인하고, 어떤 항목이 암호 건 백업에만 들어가는지는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 페이지를 따릅니다. 기기에만 묶인(ThisDeviceOnly) 항목은 백업으로 복사될 때 늘 기기 UID 로 보호되어 다른 기기에 복원하면 쓸 수 없고 [3], 동기화 규칙까지 포함한 자세한 내용은 [키체인](../../01-foundations/storage/keychain.md) 페이지에 있습니다. 그래서 백업에서 읽지 못한 항목이 기기에도 없었다고 보지 않습니다.

관리 기기에서는 구성 프로파일의 `allowedSafariPasswordAutoFillDomains` 처럼 암호 자동 완성과 관련되어 보이는 제한 키가 있어서, 자동 완성이 일부 도메인에서만 됐다면 [구성 프로파일과 MDM](configuration-profiles.md) 페이지의 제한 설정도 확인합니다. 이 키의 뜻은 공개된 정의가 없어 실제 데이터로 확인합니다.

암호 앱은 iOS 18 부터 있고 [2], 그 이전 버전 기기에서는 이 페이지의 암호 앱 도메인과 키가 없을 수 있습니다. 반대로 이 페이지의 백업 항목과 키 이름은 iOS 27.0 기준이니, 다른 버전에서 같은 키가 있는지는 실제 기기에서 확인합니다. 이 페이지는 잠금 해제나 암호를 꺼내는 방법을 다루지 않고, 수집 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지를 따릅니다.

## 직접 분석해 보기

### 헥스로 한 번

이 페이지에는 실제 기기에서 뽑은 바이트를 싣지 않습니다. 아래 순서로 직접 따라가 봅니다.

1. 백업 폴더의 Manifest.db 에서 `KeychainDomain` 과 `keychain-backup.plist` 에 해당하는 행을 찾아 실제 파일 이름을 얻습니다. Manifest.db 읽는 법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 페이지에 있습니다.
2. 그 파일을 헥스 편집기로 열어 맨 앞 머리가 이진 plist 형식인지 확인합니다. 형식 머리와 오프셋 표 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 페이지를 따릅니다.
3. 객체 영역에서 `keybag-uuid`, `genp`, `inet`, `cert`, `keys` 문자열을 찾고, 각 키가 가리키는 값 객체가 문자열인지 배열인지 표시 바이트로 확인합니다.
4. `com.apple.Passwords.plist` 도 같은 방법으로 열어 `LastUpdateTime` 이 들어간 키의 날짜 객체를 찾고, [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지를 따라 바꿔 봅니다.

### 공개 도구로 한 번

Manifest.db 와 `Accounts#.sqlite` 는 SQLite 를 여는 공개 도구(예: sqlite3 명령줄 도구)로 열어 표와 열 이름을 확인합니다. plist 는 plist 를 읽는 공개 도구(예: Python 표준 라이브러리 plistlib)로 열어 위 구조 절의 키를 찾고, 도구가 datetime 값을 어떤 시간대로 보여 주는지 함께 적어 둡니다. 도구가 보여 주는 해석과 헥스로 본 값을 한 번씩 맞춰 보는 절차는 [도구 검증](../../03-techniques/reporting/tool-validation.md) 페이지를 봅니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [키체인](../../01-foundations/storage/keychain.md) | 키체인 저장 방식, 접근 그룹, 동기화·백업 규칙 |
| [사파리](../browsers/safari/index.md) | 암호를 쓴 웹사이트의 방문 기록과 시각 |
| [와이파이 기록](../network/wifi.md) | 암호 앱에 보이는 Wi-Fi 암호와 실제 연결 기록 |
| [애플 계정](../system-account/apple-account.md) | iCloud 키체인 동기화에 쓰인 계정 |
| [바이옴](../app-usage/biome/index.md) | 보안 권장 사항과 앱 사용 흔적 |
| [구성 프로파일과 MDM](configuration-profiles.md) | 암호 자동 완성 관련 제한 설정 |
| [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) | 기기 밖의 iCloud 키체인·계정 데이터 |
| [계정 탈취 흔적](../../04-scenarios/incident/account-takeover.md) | 유출 경고 시각과 계정 이상 징후 |

## 실습

공개 시험 데이터(NIST CFReDS 등)의 아이폰 이미지나 백업으로 아래 질문을 풀어 봅니다. 분석 대상의 iOS 버전이 18 보다 낮으면 암호 앱 흔적이 없을 수 있으니, 없으면 없다는 사실과 그 이유를 적는 것까지 연습합니다.

1. 분석 대상의 iOS 버전과 수집 방식, 백업이라면 백업 암호를 걸었는지를 확인합니다.
2. Manifest.db 에서 `KeychainDomain` 과 `AppDomain-com.apple.Passwords` 의 항목 수를 세어 이 페이지의 항목 수와 비교합니다.
3. `keychain-backup.plist` 의 최상위 키를 적고, 목록마다 항목이 몇 개인지 세어 봅니다.
4. `com.apple.Passwords.plist` 와 `com.apple.mobilesafari.plist` 의 datetime 값을 바꿔 보고, 이 값들을 사용자 행위로 쓸 수 없는 이유를 보고서 문장으로 적어 봅니다.
5. 시험 기기에서 유출 암호 경고가 생긴 뒤 `lastPasswordWarningManagerUpdateHasNewWarnings` 값이 바뀌는지 확인해 키의 뜻을 검증해 봅니다.

## 참고 문헌

1. Apple Platform Security — Password Monitoring — https://support.apple.com/guide/security/password-monitoring-sec78e79fc3b/web
2. Apple Support — Use the Passwords app on your iPhone (120758) — https://support.apple.com/en-us/120758
3. Apple Platform Security — Keychain data protection — https://support.apple.com/guide/security/keychain-data-protection-secb0694df1a/web
4. Apple Developer Documentation (Security) — Item class keys and values — https://developer.apple.com/documentation/security/item-class-keys-and-values
