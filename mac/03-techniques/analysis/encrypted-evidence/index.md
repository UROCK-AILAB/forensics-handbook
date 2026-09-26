---
title: "암호화된 증거 다루기"
parent: "기법 · 분석"
nav_order: 2170
has_children: true
has_toc: false
---

# 암호화된 증거 다루기 (Encrypted Evidence)

맥 증거에서 만나는 암호화를 디스크 전체(파일볼트), 디스크 이미지 파일(암호 걸린 DMG·스파스 번들), 키체인 셋으로 나누고, 각각을 어떤 순서로 확인하고 여는지 안내합니다.

## 왜 중요한가

T2·Apple silicon 맥은 파일볼트를 켜지 않아도 내장 볼륨이 암호화돼 있고, 볼륨 암호화 키는 Secure Enclave 안의 하드웨어 UID로 보호됩니다 [FV-1]. 이 UID는 Secure Enclave 밖의 소프트웨어도, JTAG 같은 디버그 인터페이스도 읽지 못합니다 [FV-5]. 따라서 이런 맥은 디스크만 떼어 이미지를 떠서는 열 수 없고, 암호화는 이미지를 분석할 때가 아니라 획득 방법을 정할 때부터 함께 따집니다.

세 가지 암호화는 서로 이어져 있기도 합니다. 파일볼트 개인 복구 키는 키체인에 저장되고 [FV-1], 암호 걸린 디스크 이미지는 복호 비밀이 든 키체인 파일로도 열 수 있어서 [1], 키체인을 연 결과가 다른 두 증거를 여는 수단이 될 수 있습니다. 이 핸드북은 암호를 대입해 알아내는 방법을 다루지 않고, 암호화된 증거를 알아보고 합법적으로 얻은 풀 수단으로 연 뒤 그 결과를 해석하는 데까지만 다룹니다.

## 한눈에 보기

| 대상 | 위치 | macOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 파일볼트(CoreStorage) | 디스크의 CoreStorage 물리 볼륨, "Recovery HD" 파티션의 `EncryptedRoot.plist.wipekey` | 10.7 Lion 도입, libfvde 시험 범위 10.7~10.15 [3] | 옛 맥 디스크의 잠긴 볼륨과 그 키 구조 |
| 파일볼트(APFS) | APFS 컨테이너 안 볼륨 | macOS 10.13 이후 [FV-2], macOS 11 이후 시스템 볼륨은 서명된 시스템 볼륨이고 데이터 볼륨만 암호화 [FV-1] | 데이터 볼륨의 잠금 상태, 살아 있는 맥에서는 `fdesetup` 으로 사용자와 복구 키 설정 |
| 암호 걸린 디스크 이미지 | 사용자 폴더·외장 저장장치의 `.dmg`, `.sparseimage`, `.sparsebundle` 등 | `hdiutil` 기본 암호화(AES-128 CBC, 512바이트 블록)는 OS X 10.7 이후 [1] | 사용자가 따로 암호를 걸어 담아 둔 자료 |
| 파일 기반 키체인 | `/Users/<사용자>/Library/Keychains/login.keychain-db`, `/Library/Keychains/System.keychain` | 파일 이름이 macOS 10.12부터 `.keychain` 에서 `.keychain-db` 로 바뀜 [KC-1] | 저장된 암호·인증서, 풀기 전에도 계정·서비스·서버 |
| 데이터 보호 키체인 | Local Items·iCloud Keychain | macOS 10.9에서 iCloud 키체인과 함께 도입 [KC-3] | Secure Enclave를 거치는 항목 |

공개 도구도 지원 범위에 선이 있습니다. 예로 apfs-fuse는 T2 칩 맥 내장 드라이브의 하드웨어 암호화 볼륨을 지원하지 않습니다 [9]. 도구가 열지 못한 결과를 "암호가 틀렸다" 로 읽기 전에 도구의 지원 범위부터 확인합니다.

## 읽는 순서

1. [파일볼트 이미지 열기 (FileVault)](filevault-images.md) — CoreStorage와 APFS 파일볼트를 가르고, 살아 있는 맥에서 `fdesetup` 으로 상태를 기록한 뒤 사본을 읽기 전용으로 연결하는 순서
2. [암호 걸린 디스크 이미지 (Encrypted DMG)](encrypted-dmg.md) — `encrcdsa`·`cdsaencr` 시그니처로 암호 걸린 이미지를 골라내고 `hdiutil` 로 읽기 전용으로 붙이는 방법
3. [키체인 풀기 (Keychain)](keychain-decryption.md) — 풀기 전에 읽을 수 있는 메타데이터와 풀 수단이 있어야 보이는 암호 값을 나눠 분석하는 순서

## 함께 볼 페이지

- [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md) — 키 계층, 복구 키, Secure Enclave 구조
- [키체인 (Keychain)](../../../01-foundations/protection/keychain/index.md) — 키체인 파일 머리·표·속성 구조
- [디스크 이미지 형식 (DMG·Sparsebundle)](../../../01-foundations/disk-volume/dmg-sparsebundle.md) — 암호화하지 않은 이미지 형식
- [맥 증거 확보 (Acquisition)](../../process-acquisition/evidence-acquisition/index.md) — 암호화된 맥의 획득 방법
- [라이브 대응 (Live Response)](../../process-acquisition/live-response/index.md) — 끄기 전에 남겨 둘 것
- [메모리 분석 (Memory Forensics)](../memory-forensics/index.md) — 메모리에 남는 키 자료
- [저장된 암호 (Passwords·iCloud Keychain)](../../../02-artifacts/credentials/saved-passwords.md) — 키체인을 연 뒤 읽을 아티팩트

## 참고 문헌

- [1] hdiutil(1) man 페이지(2020-12-09 판) — https://keith.github.io/xcode-man-pages/hdiutil.1.html
- [3] libyal libfvde, FileVault Drive Encryption (FVDE) 형식 문서 — https://raw.githubusercontent.com/libyal/libfvde/main/documentation/FileVault%20Drive%20Encryption%20(FVDE).asciidoc
- [9] apfs-fuse README (sgan81) — https://github.com/sgan81/apfs-fuse
- [FV-1] Apple Platform Security, Volume encryption with FileVault in macOS — https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/web
- [FV-2] Apple Platform Security, Managing FileVault in macOS — https://support.apple.com/guide/security/managing-filevault-sec8447f5049/web
- [FV-5] Apple Platform Security, The Secure Enclave — https://support.apple.com/guide/security/secure-enclave-sec59b0b31ff/web
- [KC-1] libyal dtformats, MacOS keychain database file format — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/MacOS%20keychain%20database%20file%20format.asciidoc
- [KC-3] Apple, TN3137: On Mac keychain APIs and implementations(2022-11-01) — https://developer.apple.com/tutorials/data/documentation/technotes/tn3137-on-mac-keychains.json
