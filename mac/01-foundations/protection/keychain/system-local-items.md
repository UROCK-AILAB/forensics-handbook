---
title: "시스템·로컬 항목 키체인"
parent: "키체인"
grand_parent: "기반 · 보안·보호"
nav_order: 420
---

# 시스템·로컬 항목 키체인 (System·Local Items)

키체인 접근 앱에서 로그인 키체인 옆에 보이는 System 키체인은 시스템 전체가 쓰는 파일 기반 키체인이고, Local Items는 사용자마다 하나씩 있는 데이터 보호 키체인 (data protection keychain)의 표시 이름이라서, 두 저장소는 누가 쓰는지와 어떻게 보호하는지가 다릅니다.

## 두 저장소 한눈에 보기

| 구분 | System 키체인 | Local Items (데이터 보호 키체인) |
|---|---|---|
| 구현 | 파일 기반 키체인 [1] | 데이터 보호 키체인 [1] |
| 위치 | `/Library/Keychains/System.keychain` [3] | 공개 자료 없음 |
| 쓰는 쪽 | launchd 데몬 같은 시스템 맥락, 그리고 사용자 맥락의 검색 목록 [1] | 로그인한 사용자 맥락만, 사용자마다 하나 [1] |
| 담는 것 | 네트워크 자격 증명, PKI 인증서(identity) [2] | 인터넷 암호, 일반 암호, 인증서, 키 [1] |
| 푸는 수단 | 잠금 해제 파일 SystemKey [3] | Secure Enclave가 보호하는 키(iOS 중심 설명) [2] |

## System 키체인

### 누가 쓰나

키체인 API는 검색 목록 (search list)에 들어 있는 키체인에서 항목을 찾습니다. 사용자 맥락의 검색 목록에는 그 사용자의 login 키체인과 System 키체인이 들어 있고 기본 키체인은 login이지만, launchd 데몬 같은 시스템 맥락의 검색 목록에는 System 키체인만 있고 그것이 기본 키체인입니다 [1]. 그래서 launchd 데몬처럼 시스템 맥락에서 도는 프로그램이 쓰는 자격 증명은 System 키체인에서 찾습니다.

시스템 키체인은 네트워크 자격 증명과 PKI 인증서를 담고, 이와 별도로 System Roots 키체인이 바꿀 수 없는 루트 CA 인증서를 담습니다 [2].

### 파일과 SystemKey

System 키체인 파일은 [로그인 키체인 파일 (login.keychain-db)](login-keychain.md)과 같은 파일 기반 키체인 형식이라서, 파일 머리와 표 구조는 그 페이지를 따라 읽습니다. System 키체인은 잠금 해제 파일 SystemKey로 풀 수 있고, 이 파일은 흔히 `/var/db/SystemKey` 에 있습니다 [3]. chainbreaker는 SystemKey 파일 전체를 읽어 그 안의 MasterKey 칸을 씁니다 [4].

System 키체인을 분석하려면 SystemKey 파일도 함께 확보해 두어야 비밀 값까지 살필 수 있고, 확보 순서는 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)를 따릅니다.

## Local Items (데이터 보호 키체인)

### 이름과 쓰는 쪽

키체인 접근 앱은 데이터 보호 키체인을 iCloud 키체인이 켜져 있으면 "iCloud Keychain" 으로, 꺼져 있으면 "Local Items" 로 보여 줍니다 [1]. 두 이름은 같은 저장소를 다르게 부른 것이라서, iCloud 키체인을 켜고 끈 설정에 따라 같은 사용자에게서 다른 이름이 보일 수 있습니다.

데이터 보호 키체인은 사용자마다 정확히 하나이고 로그인한 사용자 맥락에서만 쓸 수 있어서, launchd 데몬처럼 사용자 맥락 밖에서 도는 프로그램은 파일 기반 키체인을 써야 합니다 [1]. 반대로 Mac Catalyst 앱과 Mac에서 도는 iOS 앱은 데이터 보호 키체인만 씁니다 [1]. iCloud 키체인 동기화, Touch ID·Face ID 같은 생체 인증으로 항목 보호하기, Secure Enclave로 키 보호하기는 데이터 보호 키체인에서만 됩니다 [1].

### 담는 것과 동기화

데이터 보호 키체인에는 인터넷 암호, 일반 암호, 인증서, 키 네 종류를 모두 담을 수 있지만, iCloud 키체인으로 동기화하는 범위는 버전마다 다릅니다 [1].

| macOS 버전 | 동기화하는 항목 종류 |
|---|---|
| macOS 11 Big Sur 이전 | 암호 종류만 |
| macOS 11 Big Sur 이후 | 네 종류 모두 |

Safari 사용자 데이터(사용자 이름·암호·카드 번호), Wi-Fi 암호, HomeKit 암호화 키 같은 항목은 동기화 대상이고, iMessage 키처럼 기기에 묶인 항목은 동기화하지 않습니다 [5]. 동기화한 항목은 다른 기기에서 만들어졌을 수 있어서, 이 맥에서 저장했다고 단정하기 전에 [저장된 암호 (Passwords·iCloud Keychain)](../../../02-artifacts/credentials/saved-passwords.md)와 [아이클라우드 계정 (iCloud Account)](../../../02-artifacts/cloud-apps/icloud-account.md)을 함께 봅니다.

### 보호 방식

아래 설명은 iOS를 중심으로 쓴 Apple 플랫폼 보안 설명서에서 나온 것이라서, Mac에서도 똑같이 동작하는지는 검체에서 확인합니다 [2].

키체인은 파일 시스템에 저장한 SQLite 데이터베이스이고, securityd 데몬이 앱의 권한(`keychain-access-groups`, `application-identifier`, `application-group`)을 보고 어떤 앱이 어떤 항목에 접근할지 정합니다 [2]. 항목은 AES-256-GCM 키 두 개로 암호화하는데, 메타데이터에는 표 전체에 쓰는 메타데이터 키 (metadata key)를 쓰고 비밀 값에는 행마다 다른 비밀 키 (secret key)를 씁니다 [2]. 메타데이터 키는 Secure Enclave가 보호하지만 검색을 빠르게 하려고 응용 프로세서에 캐시해 두고, 비밀 키는 늘 Secure Enclave를 거칩니다 [2].

항목마다 언제 꺼낼 수 있는지를 정하는 보호 등급이 붙습니다 [2].

| 보호 등급 | 비고 |
|---|---|
| `kSecAttrAccessibleWhenUnlocked` | |
| `kSecAttrAccessibleAfterFirstUnlock` | |
| `kSecAttrAccessibleAlways` | |
| `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly` | iCloud 키체인으로 동기화하지 않고 백업하지 않으며, 암호를 없애면 쓸 수 없게 됨 |

SQLite 형식 자체는 [SQLite 데이터베이스 (SQLite)](../../data-formats/sqlite/index.md)에서 다루지만, Mac에서 이 데이터베이스 파일의 경로와 표 이름은 공개된 분석 자료가 없어 검체에서 확인해야 합니다.

## 포렌식에서 중요한 점

한 사용자의 자격 증명은 로그인 키체인 파일과 데이터 보호 키체인 두 곳에 나뉘어 있을 수 있고, iCloud 키체인으로 동기화하는 항목은 데이터 보호 키체인에만 들어갑니다 [1]. 비밀 키는 늘 Secure Enclave를 거치므로 [2], 파일 기반 키체인을 암호나 SystemKey로 푸는 방식이 여기에도 통한다고 전제하지 않고, 이런 증거를 다루는 방법은 [암호화된 증거 다루기 (Encrypted Evidence)](../../../03-techniques/analysis/encrypted-evidence/index.md)에서 찾습니다.

## 함정

키체인 접근 앱은 파일 기반 키체인의 항목은 모두 보여 주지만 데이터 보호 키체인에서는 암호 항목만 보여 줍니다 [1]. 그래서 앱 화면의 Local Items에 인증서나 키가 보이지 않아도 저장소에 없다고 결론 내리지 않습니다.

chainbreaker는 파일 기반 키체인만 다루고 iCloud 키체인이나 데이터 보호 키체인은 지원 범위에 없어서 [3], 이 도구로 System 키체인은 읽어도 Local Items는 읽을 수 없는 것으로 보고 계획을 세웁니다.

## 참고 문헌

1. Apple, TN3137: On Mac keychain APIs and implementations (2022-11-01) — https://developer.apple.com/tutorials/data/documentation/technotes/tn3137-on-mac-keychains.json
2. Apple Platform Security — Keychain data protection — https://support.apple.com/guide/security/keychain-data-protection-secb0694df1a/web
3. chainbreaker README (n0fate) — https://github.com/n0fate/chainbreaker
4. chainbreaker 소스 `chainbreaker/__init__.py` — https://raw.githubusercontent.com/n0fate/chainbreaker/master/chainbreaker/__init__.py
5. Apple Platform Security — Keychain data classes (sec0a319b35f) — https://support.apple.com/guide/security/keychain-data-classes-sec0a319b35f/web
