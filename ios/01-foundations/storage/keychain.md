---
title: "키체인"
parent: "기반 · 저장 구조"
nav_order: 80
---

# 키체인 (iOS Keychain)

아이폰의 키체인 (Keychain) 은 비밀번호·토큰·인증서·암호 키를 모아 두는 SQLite 데이터베이스이고, 항목마다 메타데이터와 비밀 값을 따로 암호화해 두기 때문에 수집 방식과 백업 암호화 여부에 따라 읽을 수 있는 범위가 크게 달라집니다.

## 이 형식을 쓰는 아티팩트

키체인에는 Safari 비밀번호, Wi-Fi 비밀번호, 인증 토큰, 공유 비밀(TOTP 시드), 인증서와 아이덴티티, 암호 키가 들어갑니다[6]. 시스템이 만드는 항목이 들어가는 보호 등급은 아래와 같습니다[1].

| 보호 등급 | 들어가는 항목 |
|---|---|
| 첫 잠금 해제 후 (After first unlock) | Handoff 광고 암호화 키, iCloud 토큰, iMessage 키, LDAP·CalDAV·CardDAV, 메일 계정, Microsoft Exchange ActiveSync 계정, 소셜 네트워크 계정 토큰, VPN 비밀번호, Wi-Fi 비밀번호 |
| 잠금 해제 중 (When unlocked) | 홈 공유 비밀번호, Safari 책갈피, Safari 비밀번호 |
| 잠금 해제 중·다른 기기로 옮기지 않음 (nonmigratory) | Finder/iTunes 백업 |
| 첫 잠금 해제 후·다른 기기로 옮기지 않음 | VPN 인증서 |
| 항상·다른 기기로 옮기지 않음 | APNs 토큰, Bluetooth 키, iCloud 인증서와 개인 키, SIM PIN |
| 항상 | 나의 찾기 토큰, 음성 사서함 |

(출처: [1])

구성 프로파일로 설치한 항목은 기본으로 "첫 잠금 해제 후·다른 기기로 옮기지 않음" 등급에 들어가지만, iOS 15/iPadOS 15 로 올리기 전에 설치한 항목, 아이덴티티가 아닌 인증서, `com.apple.mdm` 페이로드의 `IdentityCertificateUUID` 가 가리키는 아이덴티티는 "항상" 등급으로 남습니다[1]. 등급 이름과 등급마다 키를 언제 쓸 수 있는지는 [데이터 보호 (Data Protection)](data-protection/index.md) 에서 다룹니다.

이 표에 나오는 항목을 다루는 아티팩트 페이지는 [저장된 암호 (Passwords·iCloud Keychain)](../../02-artifacts/credentials-security/saved-passwords.md), [와이파이 기록 (Wi-Fi)](../../02-artifacts/network/wifi.md), [VPN 설정 (VPN)](../../02-artifacts/network/vpn.md), [구성 프로파일과 MDM (Configuration Profiles·MDM)](../../02-artifacts/credentials-security/configuration-profiles.md), [메일 앱 (Apple Mail)](../../02-artifacts/mail-cloud/apple-mail.md) 입니다.

## 구조

### 기기 안의 데이터베이스

기기 안에서는 `/private/var/Keychains/keychain-2.db` 에 있고[3][6], 자료에 따라 `/var/Keychains/keychain-2.db` 로 적기도 합니다[5]. 항목은 종류마다 표가 따로 있습니다.

| 표 | 담는 항목 | 출처 |
|---|---|---|
| `genp` | 일반 비밀번호 | [3][5] |
| `inet` | 인터넷 비밀번호 | [3][5] |
| `cert` | 인증서 | [3][5] |
| `keys` | 암호 키 | [3][5] |
| `idnt` | 아이덴티티 | [3] 한 곳만 |

표 안의 열 가운데 `agrp` 에는 접근 그룹이, `pdmn` 에는 항목의 접근 가능 등급(`kSecAttrAccessible`)이 들어갑니다[5]. `pdmn` 값 가운데 `dk` 는 `kSecAttrAccessibleAlways`, `dku` 는 `kSecAttrAccessibleAlwaysThisDeviceOnly` 에 대응합니다[5]. 다른 값(`ak`, `ck` 등)의 대응과 생성·수정 시각 열의 이름·형식은 공개 자료끼리 엇갈리니 실제 파일로 확인합니다.

### 두 겹 암호화

키체인 항목은 AES-256-GCM 키 두 개로 암호화하고, 하나는 표 전체에 쓰는 메타데이터 키, 다른 하나는 행마다 다른 비밀 키입니다[1]. 메타데이터는 검색을 빠르게 하려고 메타데이터 키로 암호화하고, 비밀 값(`kSecValueData`)은 비밀 키로 암호화합니다[1]. 메타데이터 키는 Secure Enclave 가 보호하지만 빠르게 조회하려고 응용 프로세서에 캐시해 두고, 비밀 키는 쓸 때마다 Secure Enclave 를 거칩니다[1].

항목의 `data` 열은 앞 4바이트가 버전 번호이고, 그 뒤에 메타데이터와 비밀 값이 각각 감싼 키와 함께 들어 있다는 설명이 있습니다[3]. 한 자료에만 나오는 설명이니, 바이트 단위로 파싱하기 전에 실제 파일로 확인합니다.

> 그림 자리: 키체인 행 하나 안에서 메타데이터(메타데이터 키로 암호화)와 비밀 값(행마다 다른 비밀 키로 암호화)이 나뉘고, 두 키가 각각 Secure Enclave 와 이어지는 모습

### 접근 통제

앱이 키체인 항목에 접근할 때는 `securityd` 데몬이 앱의 `keychain-access-groups`, `application-identifier`, `application-group` 권한(entitlement)을 보고 허락합니다[1]. 항목은 같은 개발자의 앱끼리만 공유할 수 있고, 서드파티 앱의 접근 그룹 앞부분은 Apple Developer Program 이 정해 줍니다[1]. iOS 13.5 부터는 `keychain-access-groups` 권한에 와일드카드(`*`)를 적어 모든 접근 그룹을 한꺼번에 지정할 수 없고, 선언한 그룹을 하나하나 적어야 합니다[5][6]. 접근 그룹과 앱 식별자를 읽는 법은 [번들 ID와 앱 그룹 (Bundle ID·App Group)](../value-decoding/bundle-id-app-group.md) 에 있습니다.

### 로컬 백업 안의 키체인

로컬 백업에서는 키체인이 `KeychainDomain` 의 `keychain-backup.plist` 로 들어가고, iOS 27.0 로컬 백업에서는 이 도메인에 항목이 2개 있습니다. `keychain-backup.plist` 의 최상위 키는 아래와 같습니다.

```
keybag-uuid (str)
genp (list)
inet (list)
cert (list)
keys (list)
```

`genp`·`inet`·`cert`·`keys` 는 기기 안 데이터베이스의 표 이름과 같은 이름의 목록이고, `idnt` 키는 없습니다(iOS 27.0 기준). `keybag-uuid` 가 어느 키 가방을 가리키는지는 실제 백업으로 확인해야 합니다. 백업 폴더 전체의 짜임은 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../backups/local-backup/index.md) 에서 다룹니다.

### 버전별 차이

| iOS 버전 | 바뀐 점 | 출처 |
|---|---|---|
| 7.0.3 | iCloud 키체인 도입 | [6] |
| 12 | `kSecAttrAccessibleAlways`, `kSecAttrAccessibleAlwaysThisDeviceOnly` 사용 중단(deprecated) | [4] |
| 13.5 | 접근 그룹 와일드카드 제거 | [5][6] |
| 15 | 구성 프로파일 항목의 기본 등급이 바뀌는 기준점(그 전에 설치한 항목은 "항상") | [1] |
| 27.0 | 로컬 백업의 `keychain-backup.plist` 최상위 키가 위와 같음 | |

iOS 15 이후 `keychain-2.db` 의 스키마가 어떻게 바뀌었는지, iOS 17 부터 27 사이에 차이가 있는지는 실제 기기로 확인해야 합니다.

## 읽는 법

키체인을 읽을 수 있는 범위는 어떤 경로로 수집했는지에 따라 갈립니다.

| 수집 경로 | 키체인이 들어 있는 모양 | 기기 밖에서 풀 수 있는 범위 |
|---|---|---|
| 잠금 해제된 기기의 전체 파일 시스템 수집 | `keychain-2.db` | 기기에서 항목을 풀어, 수집 시점의 잠금 상태로 접근할 수 있는 등급까지 얻음[6] |
| 암호 건 로컬 백업 | `keychain-backup.plist` | ThisDeviceOnly 를 뺀 항목은 백업 암호로 풀 수 있고, ThisDeviceOnly 항목은 암호를 알아도 풀 수 없음[6] |
| 암호 없는 로컬 백업 | `keychain-backup.plist` | 항목이 기기 고유 하드웨어 키(UID)로 암호화된 채라서 같은 기기에만 복원할 수 있음[2][6] |
| iCloud 백업 | 키체인 사본이 들어 있을 수도, 없을 수도 있음. 들어 있으면 기기 고유 키로 감싼 항목 | 원래 기기에만 복원됨[6] |

로컬 백업이라면 먼저 `Manifest.plist` 의 `IsEncrypted` 키로 어느 줄에 해당하는지 확인하고, 같은 파일에는 `WasPasscodeSet`·`BackupKeyBag` 키도 있습니다. 암호화하지 않은 백업에서도 키체인만은 UID 에서 나온 키로 보호된 채 남고, 그래서 백업 암호를 설정했을 때만 키체인 항목이 새 기기로 옮겨집니다[2]. 따라서 암호화하지 않은 백업이면 `keychain-backup.plist` 가 들어 있어도 기기 밖에서 항목 내용을 읽을 수 없습니다[2][6]. 암호화 백업이라도 다른 기기로 옮기지 않는 (nonmigratory) 항목은 UID 에서 나온 키로 감싼 채 남아 원래 기기에만 복원됩니다[2].

iCloud 키체인 항목은 이미 클라우드에 있어 iCloud 백업에는 들어가지 않고[6], iCloud 키체인을 복구할 때 쓰는 백업 키체인은 비대칭 키(Curve25519)를 쓰는 iCloud 백업 키 가방이 보호합니다[2]. 기기에서 가져올 수 없는 계정 쪽 자료는 [클라우드 데이터 (iCloud·계정 데이터 요청)](../../03-techniques/acquisition/cloud-data.md) 에서 다룹니다. 수집 방식 자체는 [모바일 증거 확보 (Acquisition)](../../03-techniques/acquisition/mobile-acquisition/index.md) 를 봅니다.

## 포렌식에서 중요한 점

`kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly` 등급 항목은 iCloud 키체인에 동기화되지 않고, 백업되지 않고, 에스크로 키 가방에도 들어가지 않으며, 기기 암호를 없애거나 재설정하면 쓸 수 없게 됩니다[1]. 백업에서 이 등급 항목을 찾지 못했다고 앱이 그런 항목을 쓰지 않았다고 볼 수는 없고, 암호 설정 흔적은 [암호와 Face ID 설정 흔적 (Passcode·Biometrics)](../../02-artifacts/system-account/passcode-biometrics.md) 에서 확인합니다.

이 등급은 백업에 들어가되 원래 기기에만 복원되는 다른 ThisDeviceOnly 등급[1][6]과 다른 이야기라서, 보고서에서 두 등급을 섞어 쓰지 않습니다.

지운 키체인 항목을 되살릴 수 있는지, 비정상 종료 뒤 데이터베이스가 어떻게 남는지는 실제 데이터로 확인해야 합니다. `keychain-2.db` 도 SQLite 파일이라 일반적인 복구 방법은 [SQLite 데이터베이스 (SQLite)](../data-formats/sqlite/index.md) 를 따르지만, 되살린 행도 메타데이터와 비밀 값이 암호문이라는 점은 같습니다.

로컬 백업에는 키체인 주변 설정으로 보이는 파일과 키가 더 있습니다. 아래는 로컬 백업에 있는 파일과 키 이름이고, 각 키와 값의 뜻을 밝힌 공개 자료는 없습니다.

| 도메인 :: 경로 | 키·열 이름 |
|---|---|
| RootDomain :: `Library/Preferences/com.apple.security.cloudkeychainproxy#.keysToRegister.plist` | `AlwaysKeys`, `DSID`, `EnsurePeerRegistration`, `FirstUnlockKeys`, `KeyAccountUUID`, `PendingKeys`, `SyncBackupPeerIDs`, `SyncPeerIDs`, `UnlockedKeys` |
| HomeDomain :: `Library/Preferences/com.apple.security.ctkd-db.plist` | `classes`, `tokens`, `registeredTokens` (안쪽 이름 `com.apple.pivtoken`, `com.apple.secelemtoken`) |
| ProtectedDomain :: `trustd/private/com.apple.security.exception_reset_counter.plist` | `ExceptionResetCount`, `Version` |
| CameraRollDomain :: `Media/PhotoData/CPL/syncstatus.plist` | `keychainCDPEnabled` |
| HomeDomain :: `Library/Preferences/.GlobalPreferences.plist` | `PKKeychainVersionKey` |
| HomeDomain :: `Library/Preferences/com.apple.email.maild.plist` | `EDLegacyKeychainCleanupCompleted` |
| HomeDomain :: `Library/Preferences/com.apple.MobileBackup.plist` | `NotifyDaemonNextTimeKeyBagIsUnlocked` |
| HomeDomain :: `Library/Preferences/com.apple.NanoRegistry.NRLaunchNotificationController.volatile.plist` | `com.apple.mobile.keybagd.first_unlock.enabled`, `com.apple.security.secureobjectsync.viewschanged.enabled` |
| AppDomainGroup-group.com.apple.notes :: `NoteStore.sqlite` | `ZICCLOUDSYNCINGOBJECT` 표의 `ZHASMISSINGKEYCHAINITEM` 열 |

이 밖에 `AppDomainPlugin-com.apple.security.AKSDiagnosticExtension` 도메인도 있습니다(항목 4개). `cloudkeychainproxy` 파일은 이름으로 보면 iCloud 키체인 동기화 쪽 설정 같지만 이를 설명한 공개 자료는 없으니, 보고서에는 "이런 이름의 키가 있다" 까지만 씁니다. 파일 형식은 [속성 목록 파일 (plist·NSKeyedArchiver)](../data-formats/plist.md) 에서 다룹니다.

## 함정

- 백업에 `keychain-backup.plist` 가 있다고 비밀번호를 얻을 수 있다고 보지 않습니다. 파일이 들어 있는지와 풀 수 있는지는 따로이고, 풀 수 있는 범위는 백업 암호화 여부와 항목 등급으로 정해집니다[2][6].
- 기기 안 파일을 복사해 SQLite 로 열면 표 이름은 보여도, 메타데이터와 비밀 값이 모두 암호문이라 기기 밖에서 바로 읽을 수 있는 내용은 적을 것으로 보입니다. [1] 의 구조 설명에서 나오는 해석입니다.
- 파일 보호 등급과 키체인 보호 등급은 이름과 체계가 다르고, `pdmn` 열의 짧은 값도 공개 자료로 대응이 밝혀진 것은 `dk`·`dku` 두 개뿐입니다[5]. 나머지 값의 뜻은 실제 데이터로 확인한 뒤 씁니다.
- 기기 안 경로를 `/private/var` 와 `/var` 로 섞어 적는 자료가 있으니 보고서에는 실제 수집본에서 본 경로를 씁니다.
- iCloud 키체인 항목은 iCloud 백업에 들어가지 않으니[6], iCloud 백업에 없다는 사실만으로 계정에도 없다고 쓰지 않습니다.

## 도구

표 이름과 `keychain-backup.plist` 의 최상위 키는 SQLite 뷰어와 plist 뷰어로 누구나 확인할 수 있지만, 항목 내용을 읽으려면 기기의 키나 백업 암호가 있어야 합니다. 도구가 키체인 항목을 보여 준다면 어떤 수집 경로에서 어떤 키로 풀었는지 도구 기록으로 확인하고, 결과를 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 기준으로 다른 방법과 맞춰 봅니다. 이 핸드북은 잠금 해제나 암호 우회 절차를 다루지 않습니다.

## 참고 문헌

1. Keychain data protection — Apple Platform Security — https://support.apple.com/guide/security/keychain-data-protection-secb0694df1a/web
2. Keybags for Data Protection — Apple Platform Security — https://support.apple.com/guide/security/keybags-for-data-protection-sec6483d5760/web
3. Keychain - How items are stored — Shindan KB (RandoriSec) — https://kb.shindan.io/kb/ios/keychain/keychain_items_storage/
4. iOS Keychain — Analyst (bakerst221b) — https://bakerst221b.com/docs/artefacts/apple/keychain/
5. Stealing your app's keychain entries from locked iPhone — Securing — https://www.securing.pl/en/stealing-your-apps-keychain-entries-from-locked-iphone/
6. Extracting and Decrypting iOS Keychain: Physical, Logical and Cloud Options Explored — ElcomSoft blog (2020) — https://blog.elcomsoft.com/2020/08/extracting-and-decrypting-ios-keychain-physical-logical-and-cloud-options-explored/
