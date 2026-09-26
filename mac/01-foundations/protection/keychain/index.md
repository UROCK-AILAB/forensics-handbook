---
title: "키체인"
parent: "기반 · 보안·보호"
nav_order: 400
has_children: true
has_toc: false
---

# 키체인 (Keychain)

키체인은 macOS가 암호와 인증서, 키를 담아 두는 저장소이고, 옛 Mac OS에서 온 파일 기반 키체인 (file-based keychain)과 iOS에서 온 데이터 보호 키체인 (data protection keychain) 두 구현이 한 맥 안에 함께 있습니다.

## 왜 중요한가

키체인 접근 (Keychain Access) 앱은 암호, 패스키, 인증 코드와 인증서를 다룹니다 [4]. 파일 기반 키체인은 풀 수단이 없어도 항목의 계정·서비스·서버 같은 메타데이터가 보여서 [3], 사용자가 어떤 서비스에 쓸 계정을 저장해 두었는지 알 수 있고, 비밀 값은 푸는 수단이 있을 때만 볼 수 있습니다.

두 구현은 파일 형식, 보호 방식, 접근 제어가 모두 달라서 한쪽만 보면 항목을 놓칩니다. macOS의 키체인 API는 옛 Mac OS에서 온 Keychain, Mac OS X부터 있던 SecKeychain, iOS에서 와서 Mac OS X 10.6부터 쓸 수 있는 SecItem 세 가지입니다 [1]. Keychain과 SecKeychain API는 늘 파일 기반 키체인을 쓰고, SecItem은 기본으로 파일 기반 키체인을 쓰다가 `kSecUseDataProtectionKeychain` 이나 `kSecAttrSynchronizable` 을 true로 주면 데이터 보호 키체인을 씁니다 [1].

파일 기반 키체인은 폐기로 가는 중이지만 공식으로 폐기되지는 않았고, `SecKeychainCreate` 는 macOS 12 SDK에서 폐기(deprecated)됐습니다 [1]. iCloud 키체인 같은 새 기능은 데이터 보호 키체인에서만 되고 [1], 그래서 iCloud 키체인으로 동기화한 암호는 로그인 키체인 파일이 아니라 데이터 보호 키체인에서 찾습니다.

## 한눈에 보기

| 저장소 | 구현 | 위치 | 알려 주는 것 |
|---|---|---|---|
| 로그인 키체인 | 파일 기반 | `/Users/<사용자>/Library/Keychains/login.keychain-db` [3] | 사용자가 저장한 계정·서비스·서버, 인증서와 키, 항목의 날짜 속성 |
| System 키체인 | 파일 기반 | `/Library/Keychains/System.keychain` [3] | 네트워크 자격 증명과 PKI 인증서 [5] |
| Local Items 또는 iCloud Keychain | 데이터 보호 | 실제 기기에서 확인 | 로그인한 사용자의 암호·인증서·키, iCloud 키체인으로 동기화한 항목 |

| macOS 버전 | 달라진 점 |
|---|---|
| Mac OS X 10.6 | SecItem API를 지원하기 시작 [1] |
| OS X 10.9 | 데이터 보호 키체인이 iCloud 키체인과 함께 들어옴 [1] |
| macOS 10.12 | 파일 기반 키체인 확장자가 `.keychain` 에서 `.keychain-db` 로 바뀜 [2] |
| macOS 11 | 데이터 보호 키체인이 암호뿐 아니라 네 종류 항목을 모두 동기화 [1] |
| macOS 12 SDK | `SecKeychainCreate` 폐기 [1] |

## 읽는 순서

1. [로그인 키체인 파일 (login.keychain-db)](login-keychain.md) — 파일 기반 키체인의 파일 머리와 표, 날짜 속성, 암호화한 부분을 오프셋 표와 헥스 예시로 따라갑니다.
2. [시스템·로컬 항목 키체인 (System·Local Items)](system-local-items.md) — System 키체인과 SystemKey, 그리고 Local Items라는 이름으로 보이는 데이터 보호 키체인의 쓰임과 보호 방식을 비교합니다.
3. [항목과 접근 제어 (Items·ACL)](items-acl.md) — 항목 종류와 4글자 속성 이름, ACL과 키체인 접근 그룹의 차이, 증거로 쓸 때 조심할 점을 정리합니다.

## 함께 볼 페이지

- [저장된 암호 (Passwords·iCloud Keychain)](../../../02-artifacts/credentials/saved-passwords.md) — 키체인에 담긴 암호를 아티팩트로 다룰 때
- [파일볼트 (FileVault)](../filevault/index.md) — 키체인 파일이 놓인 볼륨의 암호화
- [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../codesign-notarization-sip.md) — 접근 그룹을 정하는 코드 서명 권한
- [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md) — 키체인 파일과 SystemKey를 확보할 때
- [메모리 분석 (Memory Forensics)](../../../03-techniques/analysis/memory-forensics/index.md) — 메모리에서 키체인 마스터 키를 찾을 때
- [암호화된 증거 다루기 (Encrypted Evidence)](../../../03-techniques/analysis/encrypted-evidence/index.md)
- [정보 탈취 악성 코드 (Infostealer)](../../../04-scenarios/incident/infostealer.md)

## 참고 문헌

1. Apple, TN3137: On Mac keychain APIs and implementations (2022-11-01) — https://developer.apple.com/tutorials/data/documentation/technotes/tn3137-on-mac-keychains.json
2. libyal dtformats — MacOS keychain database file format — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/MacOS%20keychain%20database%20file%20format.asciidoc
3. chainbreaker README (n0fate) — https://github.com/n0fate/chainbreaker
4. Apple, Keychain Access User Guide — What is Keychain Access — https://support.apple.com/guide/keychain-access/what-is-keychain-access-kyca1083/mac
5. Apple Platform Security — Keychain data protection — https://support.apple.com/guide/security/keychain-data-protection-secb0694df1a/web
