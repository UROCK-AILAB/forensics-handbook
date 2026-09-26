---
title: "복구 키"
parent: "파일볼트"
grand_parent: "기반 · 보안·보호"
nav_order: 380
---

# 복구 키 (Recovery Key)

파일볼트 복구 키는 사용자 암호 대신 KEK를 풀 수 있는 두 번째 열쇠이고, 개인 복구 키·기관 복구 키·iCloud 복구 키 세 종류가 있으며, 조직이 관리하는 맥이라면 복구 키를 맡겨 둔 흔적이 볼륨 밖 파일과 구성 프로파일에 남습니다.

## 이 구조를 쓰는 곳

복구 키는 [키 계층 (VEK·KEK)](key-hierarchy.md)에서 설명한 KEK를 푸는 방법 가운데 사용자 암호를 뺀 나머지 셋입니다 [3]. 사용자가 암호를 잊었을 때 recoveryOS나 로그인 창(Shift-Option-Return)에서 복구 키를 넣어 볼륨을 풀 수 있습니다 [1].

| 종류 | 내용 | 근거 |
|---|---|---|
| 개인 복구 키 (Personal Recovery Key, PRK) | 24자리 무작위 숫자·문자. 볼륨을 처음 암호화할 때 만듦 | [1][3] |
| 기관 복구 키 (Institutional Recovery Key, IRK) | 예전 이름은 "FileVault Master identity". Apple은 이제 기관 관리용으로 권장하지 않고 PRK를 쓰라고 안내함. IRK용 `Certificate` 키는 Apple silicon 맥에서 지원하지 않음 | [2][5] |
| iCloud 복구 키 | Apple 지원과 함께 쓰는 키. 공개 명세에 구조 없음 | [3] |

## 구조

### 볼륨 키백 속 개인 복구 키

PRK는 볼륨 키백에 사용자 UUID 대신 아래 고정 UUID로 기록됩니다 [3].

```
APFS_FV_PERSONAL_RECOVERY_KEY_UUID = EBC6C064-0000-11AA-AA11-00306543ECAC
```

PRK도 사용자 암호와 같은 방식으로 KEK를 풀고, 그 KEK로 VEK를 풉니다 [3]. 키백 항목의 배치와 태그는 [키 계층 (VEK·KEK)](key-hierarchy.md)에 있습니다.

### 사용자 쪽 보관

PRK는 키체인에 저장되고, 암호(Passwords) 앱에서 볼 수 있습니다 [1]. iCloud 키체인을 켜 두면 복구 키가 iCloud 키체인으로 동기화되고, iCloud를 쓰지 않으면 사용자가 직접 보관해야 합니다 [1]. 암호 앱에서 복구 키를 보여 주는 동작이 어느 macOS 버전부터인지는 실제 기기에서 확인해야 합니다. 키체인 파일 자체는 [키체인 (Keychain)](../keychain/index.md), 동기화한 암호 항목은 [저장된 암호 (Passwords·iCloud Keychain)](../../../02-artifacts/credentials/saved-passwords.md)에서 다룹니다.

IRK 쪽 키체인 파일은 `/Library/Keychains/FileVaultMaster.keychain` 이고, 아래 `com.apple.MCX.FileVault2` 페이로드에서 `UseKeychain` 이 true이고 인증서 정보를 넣지 않았을 때 시스템이 이 키체인을 씁니다 [5].

### MDM 에스크로 페이로드

조직은 모바일 기기 관리 (Mobile Device Management, MDM) 구성 프로파일로 복구 키를 맡겨 두게 할 수 있습니다. 프로파일 파일과 설치 기록을 찾는 법은 [구성 프로파일 (Configuration Profiles·MDM)](../../../02-artifacts/persistence/configuration-profiles.md)에 있고, 여기서는 파일볼트 관련 페이로드의 키만 정리합니다.

`com.apple.security.FDERecoveryKeyEscrow` 는 macOS 10.13 이후 페이로드이고, 시스템 범위 프로파일에만 넣을 수 있으며 기기당 하나만 둡니다 [4].

| 키 | 형식 | 뜻 [4] |
|---|---|---|
| `Location` | 문자열, 필수 | 파일볼트를 켤 때 사용자에게 보여 주는 복구 키 보관 위치 설명 |
| `EncryptCertPayloadUUID` | 문자열, 필수 | 복구 키를 암호화할 인증서 페이로드 |
| `DeviceKey` | 문자열, 선택 | 관리자가 조회할 때 쓰는 식별자. 없으면 일련번호를 씀 |

이 페이로드가 있으면 시스템이 PRK를 지정한 인증서로 암호화해 CMS 봉투로 감싼 뒤 `/var/db/FileVaultPRK.dat` 에 저장하고, 이 파일은 프로파일을 만든 쪽만 복호할 수 있습니다 [4]. MDM 서버는 SecurityInfo 명령으로 이 값을 가져갑니다 [4]. 예전 페이로드 `com.apple.security.FDERecoveryRedirect` 는 폐지됐지만 호환을 위해 설치는 됩니다 [4].

`com.apple.MCX.FileVault2` 는 macOS 10.9에 도입된 페이로드이고, macOS 10.15부터는 사용자 승인 MDM이 있어야 씁니다 [5].

| 키 | 형식 | 뜻 [5] |
|---|---|---|
| `Enable` | 문자열 | "On" 또는 "Off" |
| `Defer` | 불리언 | true면 지정한 사용자가 로그아웃할 때까지 켜기를 미룸 |
| `UseRecoveryKey` | 불리언 | 기본 true. PRK를 만들고 보여 줌 |
| `ShowRecoveryKey` | 불리언 | false면 켠 뒤 PRK를 보여 주지 않음 |
| `OutputPath` | 문자열 | 복구 키와 컴퓨터 정보를 담은 plist를 저장할 위치 |
| `Certificate` | 데이터 | IRK를 만들 때 쓰는 DER 인증서. 이 키는 Apple silicon 맥에서 지원하지 않음 |
| `UseKeychain` | 불리언 | true이고 인증서 정보가 없으면 `/Library/Keychains/FileVaultMaster.keychain` 을 씀 |
| `DeferForceAtUserLoginMaxBypassAttempts` | 정수 | 사용자가 파일볼트 켜기를 건너뛸 수 있는 최대 횟수(-1~9999) |
| `DeferDontAskAtUserLogout` | 불리언 | true면 로그아웃할 때 켜기를 묻지 않음. macOS 10.10 이후 |
| `ForceEnableInSetupAssistant` | 불리언 | 설정 지원이 처음 설정할 때 파일볼트를 켜게 함. macOS 14.0 이후, 자동 등록(DEP) 기기 전용, 보안 토큰이 있는 관리자 필요 |

### 부트스트랩 토큰

부트스트랩 토큰 (Bootstrap Token)은 복구 키와 다른 값이지만 같은 MDM 에스크로 흐름에 들어 있어서 함께 봅니다. 이 토큰은 macOS 10.15에 들어왔고, macOS 10.15.4 이후에는 처음 로그인할 때 만들어 MDM에 맡겨 두며, macOS 11 이후에는 이 토큰으로 맥에 로그인하는 모든 사용자에게 보안 토큰을 줍니다 [2]. 이렇게 쓰려면 기기가 Apple School Manager나 Apple Business에 등록돼 있어야 합니다 [2]. 보안 토큰 자체는 [키 계층 (VEK·KEK)](key-hierarchy.md)에서 다룹니다.

## 읽는 법

볼륨 키백을 풀어 파싱할 수 있으면 `EBC6C064-0000-11AA-AA11-00306543ECAC` 항목이 있는지로 PRK를 설정했는지 판단할 수 있지만, 키 값 자체는 이 항목에서 나오지 않습니다 [3]. 볼륨 밖에서는 `/var/db/FileVaultPRK.dat` 와 설치된 구성 프로파일의 두 페이로드를 찾고, 프로파일 plist는 [속성 목록 파일 (Property List)](../../data-formats/plist/index.md)의 방법으로 읽습니다.

## 포렌식에서 중요한 점

이 흔적들이 증명하는 것과 증명하지 못하는 것은 아래처럼 나뉩니다.

| 흔적 | 증명하는 것 | 증명하지 못하는 것 |
|---|---|---|
| 볼륨 키백의 PRK UUID 항목 | 이 볼륨에 PRK가 설정돼 있음 [3] | 복구 키의 값, 복구 키를 실제로 쓴 적이 있는지 |
| `/var/db/FileVaultPRK.dat` | MDM 복구 키 에스크로가 설정됐던 기기임 [4] | 파일 시각이 파일볼트를 켠 시점인지(공개 자료 없음) |
| `Certificate`·`UseKeychain` 이 든 프로파일 | IRK를 쓰도록 관리한 흔적 [5] | IRK가 실제로 만들어졌는지. `Certificate` 키는 Apple silicon 맥에서 지원하지 않음 [5] |
| `OutputPath` 가 있는 프로파일 | 복구 키와 컴퓨터 정보를 담은 plist를 그 위치에 두도록 설정했음 [5] | 그 plist 안에 복구 키가 평문으로 들어 있는지, plist 안의 키 이름 |

`/var/db/FileVaultPRK.dat` 는 프로파일을 만든 쪽만 복호할 수 있습니다 [4]. 조직이 사건 당사자라면 MDM 관리자에게서 에스크로한 복구 키를 받는 쪽이 정식 경로이고, 이 과정은 [암호화된 증거 다루기 (Encrypted Evidence)](../../../03-techniques/analysis/encrypted-evidence/index.md)의 절차를 따릅니다.

`OutputPath` 로 지정한 위치에 plist가 남아 있으면 복구 키와 컴퓨터 정보가 들어 있을 수 있으니 [5], 그 파일을 찾으면 민감한 증거로 다루고 보고서에 값을 그대로 옮기지 않습니다.

## 함정

복구 키를 바꾸거나 다시 만든 흔적과 복구 키로 잠금을 푼 기록이 어디에 남는지는 공개된 자료가 없습니다. 그래서 PRK 항목이 있다는 사실만으로 "복구 키로 풀었다" 고 쓰지 않습니다. `OutputPath` plist의 기본 경로와 키 이름은 `fdesetup` 명령의 설명서와 실제 데이터로 확인합니다.

`Certificate` 키로 IRK를 지정한 프로파일이 있어도 Apple silicon 맥에서는 이 키를 지원하지 않으니 [5], 기기 종류를 [컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)](../../../02-artifacts/system-account/computer-name-hardware.md)에서 먼저 확인합니다.

## 참고 문헌

1. Apple Platform Security — Volume encryption with FileVault in macOS — https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/web
2. Apple Platform Security — Managing FileVault in macOS — https://support.apple.com/guide/security/managing-filevault-sec8447f5049/web
3. Apple, Apple File System Reference (2020-06-22 판, PDF) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
4. Apple device-management 저장소 — com.apple.security.FDERecoveryKeyEscrow.yaml — https://raw.githubusercontent.com/apple/device-management/release/mdm/profiles/com.apple.security.FDERecoveryKeyEscrow.yaml
5. Apple device-management 저장소 — com.apple.MCX.FileVault2.yaml — https://raw.githubusercontent.com/apple/device-management/release/mdm/profiles/com.apple.MCX.FileVault2.yaml
