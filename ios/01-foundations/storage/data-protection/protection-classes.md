---
title: "보호 등급"
parent: "데이터 보호"
grand_parent: "기반 · 저장 구조"
nav_order: 50
---

# 보호 등급 (Protection Classes)

아이폰의 파일과 키체인 항목에는 저마다 보호 등급이 붙고, 등급마다 기기가 그 등급 키를 언제 버리고 언제까지 메모리에 두는지가 다릅니다.

## 이 구조를 따르는 데이터

데이터 보호는 Apple SoC 가 들어간 기기(iPhone, iPad, Apple silicon Mac, Apple TV, Apple Vision Pro, Apple Watch)의 플래시 저장소에 적용됩니다[2]. 아이폰에서는 데이터 볼륨에 만드는 모든 파일이 대상이라서 메시지·사진·앱 데이터베이스처럼 이 핸드북의 아티팩트 사전에 나오는 파일은 모두 어느 한 등급에 속합니다. 앱이 등급을 따로 정하지 않으면 제3자 앱 데이터는 Class C 로 저장됩니다[1].

키체인 항목도 별도의 등급 체계를 따릅니다. 키체인 자체의 저장 방식은 [키체인 (iOS Keychain)](../keychain.md) 에서 다루고, 이 페이지에서는 등급만 정리합니다.

## 구조

### 파일별 키와 암호화 방식

데이터 볼륨에 파일이 생길 때마다 기기는 새 256비트 키, 곧 파일별 키 (per-file key) 를 만들고, APFS 는 이 키를 파일 조각 (extent) 별 키로 더 나눌 수 있습니다[2]. 칩 세대에 따라 암호화 방식이 다릅니다[2].

| 칩 | 암호화 방식 |
|---|---|
| A14~A18, M1 이후 | AES-256 XTS. 파일별 키를 NIST SP 800-108 KDF 에 통과시켜 씁니다 |
| A9~A13, S5 이후 | AES-128 XTS. 256비트 키를 나눠 씁니다 |

암호화 방식은 iOS 버전이 아니라 칩으로 갈리니, 검체의 기종부터 확인합니다. 기종을 읽는 법은 [기기 정보 (Device Info·Lockdown)](../../../02-artifacts/system-account/device-info.md) 에 있습니다.

### 파일 보호 등급 네 가지

| 등급 | API 이름 | 등급 키를 버리는 때 | 쓰는 곳 |
|---|---|---|---|
| Class A 완전 보호 | `NSFileProtectionComplete` | 잠그고 잠시 뒤. "Require Password" 가 즉시일 때 10초 뒤 | 잠긴 동안 읽을 일이 없는 데이터 |
| Class B 열려 있지 않으면 보호 | `NSFileProtectionCompleteUnlessOpen` | 파일을 닫으면 파일별 키를 메모리에서 지움 | 잠긴 동안에도 써야 하는 파일(예: 메일 첨부를 뒤에서 내려받기) |
| Class C 첫 사용자 인증까지 보호 | `NSFileProtectionCompleteUntilFirstUserAuthentication` | 잠가도 지우지 않음 | 제3자 앱 데이터의 기본 등급 |
| Class D 보호 없음 | `NSFileProtectionNone` | 해당 없음. 등급 키는 UID 로만 보호 | 빠른 원격 삭제를 위한 암호화 |

(출처: [1])

Class A 는 등급 키를 버린 뒤 사용자가 암호나 생체 인증으로 다시 풀 때까지 읽을 수 없습니다[1]. Class B 는 Curve25519 위의 ECDH 로 One-Pass Diffie-Hellman 키 합의를 하고, 합의에 쓴 임시 공개 키를 감싼(wrapped) 파일별 키 옆에 저장합니다[1]. Class C 는 첫 사용자 인증 뒤로는 기기를 잠가도 풀린 등급 키를 메모리에서 지우지 않습니다[1]. Class D 의 등급 키는 UID 로만 보호되고 Effaceable Storage 에 있어서, 이 등급의 암호화는 빠른 원격 삭제 효과만 줍니다[1]. UID 는 [보안 칩과 키 가방 (Secure Enclave·Keybag)](secure-enclave-keybag.md) 에서 설명합니다.

> 그림 자리: 등급 네 개를 세로로 놓고, 잠금 해제 → 잠금 → 파일 닫기 순서로 시간이 흐를 때 각 등급 키가 메모리에 남는지 버려지는지를 막대로 보여 주는 그림

### 키체인 보호 등급

키체인 항목은 파일과 이름이 다른 등급을 따릅니다[4].

| 등급 | 쓸 수 있는 때 |
|---|---|
| `kSecAttrAccessibleWhenUnlocked` | 잠금이 풀려 있는 동안 |
| `kSecAttrAccessibleAfterFirstUnlock` | 재부팅 뒤 첫 인증을 한 뒤 |
| `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly` | 암호가 설정돼 있을 때. 동기화·백업하지 않음 |
| `kSecAttrAccessibleAlways` | 언제나. Apple 이 권하지 않는 방식 |

(출처: [4])

이름 끝이 "ThisDeviceOnly" 인 항목은 백업으로 복사될 때 UID 로 보호되어 다른 기기에 복원하면 쓸 수 없습니다[4]. 키체인 항목에는 Face ID·Touch ID·암호 요구를 붙일 수 있고, 생체 등록이 바뀌면 접근을 막도록 할 수도 있습니다[4]. Apple 문서[4]는 Safari 암호, Wi-Fi 암호, 메일 계정 같은 시스템 항목이 어느 등급인지 표로 밝혀 두었으니, 특정 항목의 등급이 필요하면 원문 표를 직접 확인합니다.

## 읽는 법 — 로컬 백업에서

로컬 백업의 `Manifest.db` 에는 `Files` 표가 있고, 칸은 `fileID`, `domain`, `relativePath`, `flags`, `file`(BLOB) 입니다. iMazing 의 설명으로는 `Manifest.db` 에 도메인·경로·flags·크기·해시 같은 파일 메타데이터와 함께 암호화·보호 속성이 들어 있습니다[3]. 관찰한 백업에서는 `file` 칸 안쪽의 키 이름까지 읽지 않았고, 이 페이지에서도 그 키 이름은 다루지 않습니다. 백업 폴더 전체의 구조는 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../backups/local-backup/index.md) 에서 봅니다.

관찰한 백업의 설정 plist 가운데 이름에 파일 보호가 들어간 키가 몇 개 있습니다. 각 키의 뜻을 설명한 문서는 확인하지 못했으니, 이름만 보고 기기의 등급 설정을 판단하지 않습니다.

| 도메인 | 파일 | 키(형식) |
|---|---|---|
| `HomeDomain` | `Library/Preferences/com.apple.itunesstored.plist` | `NeedsFileProtectionClassMigration` (bool) |
| `AppDomain-com.apple.PosterBoard` | `Library/Preferences/com.apple.PosterBoard.unprotectedUserDefaults.plist` | `PBF_RESET_FILE_PROTECTIONS` (bool) |
| `HomeDomain` | `Library/Preferences/com.apple.passd.plist` | `PassesDirectoryFileProtectionFixed` (bool) |
| `AppDomain-com.apple.mobilesafari` | `Library/Preferences/com.apple.mobilesafari.plist` | `SafariFileProtectionEnabled` (bool) |

## 포렌식에서 중요한 점

등급은 파일마다 앱이 정하고, 같은 앱 안에서도 파일마다 다를 수 있습니다. 그래서 같은 기기에서 같은 시각에 수집해도 어떤 파일은 읽히고 어떤 파일은 읽히지 않을 수 있고, 어느 쪽이 될지는 수집 당시 잠금 상태와 겹쳐서 정해집니다. 잠금 상태별로 어떤 등급이 풀리는지는 [잠금 해제 전·후 (BFU·AFU)](bfu-afu.md) 에 정리했습니다.

## 함정

- "제3자 앱 데이터의 기본 등급은 Class C" 는 앱이 등급을 따로 정하지 않았을 때의 이야기입니다[1]. 메신저처럼 민감한 데이터를 다루는 앱은 더 높은 등급을 골랐을 수 있으니, 기본값만 믿고 특정 파일의 등급을 단정하지 않습니다.
- Class D 도 암호화는 되어 있습니다. "보호 없음" 이라는 이름은 사용자 암호로 보호하지 않는다는 뜻이고, 등급 키는 UID 로 보호됩니다[1].
- 파일 보호 등급과 키체인 보호 등급은 이름과 체계가 따로입니다. 보고서에서 "Class C" 와 `AfterFirstUnlock` 을 섞어 쓰지 않습니다.

## 참고 문헌

1. Data Protection classes — Apple Platform Security — https://support.apple.com/guide/security/data-protection-classes-secb010e978a/web
2. Data Protection overview — Apple Platform Security — https://support.apple.com/guide/security/data-protection-overview-secf6276da8a/web
3. How Apple's iOS BackupAgent Creates and Transfers Encrypted Backups to Your Computer — iMazing (2026-05-07 갱신) — https://imazing.com/guides/ios-backupagent
4. Keychain data protection — Apple Platform Security — https://support.apple.com/guide/security/keychain-data-protection-secb0694df1a/web
