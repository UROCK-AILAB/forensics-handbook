---
title: "데이터 보호"
parent: "기반 · 저장 구조"
nav_order: 40
has_children: true
has_toc: false
---

# 데이터 보호 (Data Protection)

아이폰은 저장소의 파일을 하나하나 따로 암호화하고, 파일마다 붙은 보호 등급과 기기의 잠금 상태에 따라 그 파일을 풀 수 있는지가 정해집니다.

## 왜 중요한가

같은 기기라도 잠금 상태와 파일 등급에 따라 읽을 수 있는 데이터가 달라집니다[2][4]. 재부팅 뒤 한 번도 잠금을 풀지 않은 기기와 한 번이라도 푼 기기는 수집할 수 있는 범위가 다르고, 같은 앱 안에서도 파일마다 등급이 다를 수 있습니다. 그래서 "이 기기에서 이 데이터가 나오지 않았다" 는 결과를 "이 데이터가 없었다" 로 읽기 전에, 수집 당시 기기 상태와 해당 파일의 등급부터 확인해야 합니다.

로컬 백업도 이 구조와 이어져 있습니다. 암호화 로컬 백업은 기기 안의 키와는 다른 백업 키 가방으로 다시 암호화하고[3], 키체인처럼 기기에 묶인 데이터는 백업으로 옮겨도 원래 기기 밖에서 쓰기 어렵습니다[3]. 백업을 받았는데 일부가 읽히지 않을 때 원인을 찾는 출발점이 이 묶음입니다.

데이터 보호는 Apple SoC 가 들어간 기기(iPhone, iPad, Apple silicon Mac, Apple TV, Apple Vision Pro, Apple Watch)의 플래시 저장소 데이터에 적용됩니다[1]. 맥과 비교하면, Apple silicon Mac 은 기본 등급이 Class C 이고 파일별 키 대신 볼륨 키를 써서 FileVault 방식을 재현하며[1], macOS 에서 Class A 키는 잠글 때가 아니라 로그아웃할 때 지워집니다[2].

> 그림 자리: 맨 아래 Secure Enclave 와 UID, 그 위에 키 가방과 등급 키 네 개, 맨 위에 파일을 두고, 잠금 상태에 따라 등급 키가 메모리에 남거나 버려지는 흐름을 보여 주는 그림(파일 시스템 키 층은 확인한 자료가 없어 넣지 않음)

## 한눈에 보기

| 주제 | 어디에 남나·어디서 보나 | iOS·칩 | 알려 주는 것 |
|---|---|---|---|
| 보호 등급 | 파일마다 붙는 등급. 로컬 백업에서는 `Manifest.db` 의 `Files` 표 | 칩에 따라 AES-128 XTS 또는 AES-256 XTS | 어떤 파일이 어떤 조건에서 풀리는지 |
| 잠금 해제 전·후 | 기기 상태. 비활성 재부팅은 통합 로그 메시지와 NVRAM 변수 `aks-inactivity` 에 흔적 | 비활성 재부팅은 iOS 18 부터 | 수집 당시 기기가 BFU 였는지 AFU 였는지, 보관 중 재부팅했는지 |
| 보안 칩과 키 가방 | SoC 안의 Secure Enclave. 로컬 백업의 `Manifest.plist` 키 `BackupKeyBag`, `KeychainDomain` 의 `keychain-backup.plist` | Secure Enclave 는 A7 부터 | 어떤 키가 데이터를 보호하는지, 백업이 어느 키 가방으로 암호화됐는지 |

`Manifest.db`, `Manifest.plist`, `keychain-backup.plist` 의 이름은 관찰한 로컬 백업에서 확인했습니다.

## 읽는 순서

1. [보호 등급 (Protection Classes)](protection-classes.md) — 파일 등급 네 가지와 키체인 등급, 등급마다 키를 언제 버리는지, 백업에서 등급 정보가 어디 보이는지를 다룹니다.
2. [잠금 해제 전·후 (BFU·AFU)](bfu-afu.md) — 두 잠금 상태에서 등급별로 무엇이 풀리는지와 iOS 18 의 비활성 재부팅, 그 흔적을 다룹니다.
3. [보안 칩과 키 가방 (Secure Enclave·Keybag)](secure-enclave-keybag.md) — Secure Enclave 와 UID, 키 가방 다섯 가지, 로컬 백업에 남는 키 가방 흔적을 다룹니다.

## 함께 볼 페이지

- [iOS의 파일 시스템 (APFS on iOS)](../filesystem/index.md) — 암호화한 파일이 놓이는 볼륨 구조
- [키체인 (iOS Keychain)](../keychain.md) — 키체인 데이터베이스의 저장 방식
- [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../backups/local-backup/index.md) — `Manifest.db`·`Manifest.plist` 를 포함한 백업 폴더 구조
- [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md) — 기기에서 증거를 확보하는 방식
- [암호와 Face ID 설정 흔적 (Passcode·Biometrics)](../../../02-artifacts/system-account/passcode-biometrics.md) — 암호 설정과 관련된 흔적

## 참고 문헌

1. Data Protection overview — Apple Platform Security — https://support.apple.com/guide/security/data-protection-overview-secf6276da8a/web
2. Data Protection classes — Apple Platform Security — https://support.apple.com/guide/security/data-protection-classes-secb010e978a/web
3. Keybags for Data Protection — Apple Platform Security — https://support.apple.com/guide/security/keybags-for-data-protection-sec6483d5760/web
4. Reverse Engineering iOS 18 Inactivity Reboot — Jiska Classen — https://naehrdine.blogspot.com/2024/11/reverse-engineering-ios-18-inactivity.html
