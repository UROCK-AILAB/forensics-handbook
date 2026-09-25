---
title: "보안 칩과 키 가방"
parent: "데이터 보호"
grand_parent: "기반 · 저장 구조"
nav_order: 70
---

# 보안 칩과 키 가방 (Secure Enclave·Keybag)

보안 칩 (Secure Enclave) 은 기기마다 다른 하드웨어 키를 안에 품고 암호 작업을 따로 맡는 부품이고, 키 가방 (Keybag) 은 그 칩과 사용자 암호로 보호하는 등급 키 묶음입니다. 로컬 백업을 분석할 때 보이는 `BackupKeyBag` 도 이 키 가방 가운데 하나입니다.

## 이 구조와 관련된 데이터

[보호 등급 (Protection Classes)](protection-classes.md) 에서 본 등급 키는 키 가방에 감싼(wrapped) 채 들어 있습니다[1]. 그래서 파일·키체인·백업 어느 쪽을 분석하든 "이 데이터를 어느 키 가방이 보호하는가" 를 먼저 따지게 됩니다. 분석가가 직접 마주치는 곳은 주로 로컬 백업의 `Manifest.plist` 와 키체인 백업 파일입니다.

## 구조

### Secure Enclave

Secure Enclave 는 iPad, iPhone, Mac, Apple TV, Apple Vision Pro, Apple Watch, HomePod 에 들어간 전용 보안 하위 시스템이고, 아이폰에서는 iPhone 5s(A7) 부터 있습니다[2]. 계산은 Secure Enclave Processor(SEP) 가 맡고, SEP 는 Apple 이 고친 L4 마이크로커널을 돌립니다[2]. 난수 생성기(TRNG)는 링 오실레이터에서 얻은 값을 CTR_DRBG 로 후처리합니다[2].

UID 는 제조할 때 SoC 에 새기는 무작위 값이고, A9 부터는 제조 중에 SEP 의 난수 생성기로 만듭니다[2]. UID 와 GID 는 JTAG 같은 디버그 경로로도 볼 수 없고, SEP AES 엔진의 하드웨어 키는 엔진 안에 머물러 sepOS 에도 보이지 않습니다[2].

칩 세대에 따라 더해진 기능이 다르니, 검체의 칩을 먼저 확인합니다.

| 칩 | 더해진 기능 |
|---|---|
| A7 이후 | Secure Enclave |
| A9 이후 | UID 를 제조 중 SEP 난수 생성기로 만듦 |
| A11·S4 이후 | 메모리 보호 엔진에 재생 방지(anti-replay) 값이 더해짐 |
| A12·S4 이후 | 전용 보안 비휘발 저장소 (Secure Storage Component) |
| 2020년 가을 이후 모델 | 2세대 Secure Storage Component. 암호 관련 카운터 잠금 상자(counter lockbox)를 둠 |
| A13 이후 | Boot Monitor. 부팅한 sepOS 해시의 무결성을 더 강하게 보장함 |

(출처: [2])

메모리 보호 엔진은 SEP 메모리를 AES XEX 로 암호화하고 CMAC 으로 인증합니다[2]. 암호 입력 지연이나 UID 와 사용자 암호를 얽는 방식은 이 페이지에서 확인한 자료가 없어 다루지 않습니다.

> 그림 자리: SoC 안의 Secure Enclave(SEP·AES 엔진·UID) 와 칩 밖의 Secure Storage Component, 응용 프로세서를 나란히 두고, UID 가 SEP 밖으로 나가지 않는다는 점을 보여 주는 그림

### 키 가방 다섯 가지

| 키 가방 | 담는 것·쓰는 곳 | 보호 방식 |
|---|---|---|
| 사용자 키 가방 | 평소 쓰는 감싼 등급 키 | A9 이전은 Effaceable Storage 의 키로 암호화, A9 이후는 SEP 재생 방지 값으로 보호하는 locker 에 저장 |
| 기기 키 가방 | 기기 전용 작업용 등급 키 | 단일 사용자 iOS 에서는 사용자 키 가방과 같은 것이고 사용자 암호로 보호 |
| 백업 키 가방 | Finder·iTunes 암호화 백업의 새 키 묶음 | 백업 암호를 PBKDF2 에 1천만 번 돌려 보호 |
| 에스크로 키 가방 | 동기화에 쓰는 컴퓨터나 MDM 이 암호 입력 없이 백업·동기화하게 함 | 기기와 호스트로 나눠 보관, 기기 쪽 데이터는 Class C |
| iCloud 백업 키 가방 | iCloud 백업과 iCloud 키체인 복구용 백업 키체인 | 등급 키가 모두 Curve25519 비대칭 키 |

(출처: [1])

사용자 키 가방은 No Protection 등급으로 저장한 바이너리 plist 파일이고, A9 이전 기기에서는 암호를 바꿀 때 이전 키를 지우고 새로 만듭니다[1]. 맥에서는 경로가 `~/Library/Keychains/[UUID]/user.kb` 이지만[1], 아이폰 기기 안의 경로는 확인하지 못했습니다.

백업 키 가방은 암호화 백업을 만들 때마다 새 키 묶음으로 새로 만들고, 백업 데이터를 그 키로 다시 암호화합니다[1]. 다른 기기로 옮길 수 없는 키체인 항목은 암호화 백업 안에서도 UID 에서 파생한 키로 감싼 채 남고, 암호화하지 않은 백업에서는 파일은 암호화되지 않지만 키체인은 UID 파생 키로 보호된 채입니다[1]. 키체인 등급과 "ThisDeviceOnly" 항목은 [보호 등급 (Protection Classes)](protection-classes.md) 에 정리했습니다.

에스크로 키 가방은 MDM 이 암호를 원격으로 지울 수 있게 하는 데도 씁니다[1]. 업데이트를 위한 잠금 해제 토큰은 사람이 지켜보는 업데이트용이 20분 뒤, 무인 업데이트용이 최대 16시간 뒤 만료되고, 기기를 잠글 때마다 없애고 풀 때마다 다시 만듭니다[1].

## 읽는 법 — 로컬 백업에서 보이는 흔적

관찰한 로컬 백업의 `Manifest.plist` 에는 `IsEncrypted`, `Version`, `Containers`, `Date`, `SystemDomainsVersion`, `WasPasscodeSet`, `Lockdown`, `Applications`, `BackupKeyBag` 키가 있습니다. 이 백업은 암호화하지 않은 백업인데도 `BackupKeyBag` 키가 있었고, `ManifestKey` 라는 키는 목록에 없었습니다. 따라서 `BackupKeyBag` 이 있다는 것만으로 암호화 백업이라고 판단하지 않고, 암호화 여부는 `IsEncrypted` 키로 따로 봅니다.

iMazing 의 설명으로는 암호화 백업에서 `Manifest.db` 자체도 별도 키로 암호화하고, 기기가 등급별 키로 암호화해 보낸 데이터를 컴퓨터는 받은 그대로 저장합니다[3]. 그 별도 키가 어느 plist 키에 들어 있는지는 이번에 확인하지 못했습니다.

키체인 백업은 `KeychainDomain` 의 `keychain-backup.plist` 에 있고, 최상위 키는 아래와 같습니다.

```
keybag-uuid (str)
genp (list)
inet (list)
cert (list)
keys (list)
```

이름으로 보아 `keybag-uuid` 는 키 가방 UUID, 나머지는 키체인 항목 종류별 목록으로 보이지만, 정의를 밝힌 문서는 확인하지 못했습니다. 백업 폴더 전체의 구조는 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../backups/local-backup/index.md) 에 있습니다.

## 포렌식에서 중요한 점

UID 는 디버그 경로로도 볼 수 없고[2], Apple 은 다른 기기로 옮길 수 없는 키체인 항목이 암호화 백업 안에서도 UID 파생 키로 감싼 채 남는다고 설명합니다[1]. 로컬 백업을 받았더라도 키체인 안의 비밀 값까지 읽을 수 있는지는 백업 암호화 여부와 항목의 등급에 따라 갈립니다.

키체인이 비암호화 백업에 들어가는지를 두고는 자료끼리 말이 다릅니다. iMazing 은 키체인·건강·Safari 기록·통화 기록 등은 백업 암호화를 켜야 백업된다고 쓰고[3], Apple 은 암호화하지 않은 백업에서도 키체인이 UID 파생 키로 보호된 채라고 씁니다[1]. 관찰한 비암호화 백업에도 `keychain-backup.plist` 가 있었습니다. 셋을 합치면 "비암호화 백업에도 키체인 파일은 있지만 원래 기기 밖에서는 풀 수 없다" 로 읽히지만, 해석이니 보고서에서 단정하지 않습니다.

## 함정

- 암호화 백업의 키 가방은 기기 안의 사용자 키 가방과 다른 것입니다. 백업을 만들 때마다 새 키로 만듭니다[1].
- 에스크로 키 가방의 기기 쪽 데이터는 Class C 등급입니다[1]. 이 등급이 잠금 상태에 따라 어떻게 풀리는지는 [잠금 해제 전·후 (BFU·AFU)](bfu-afu.md) 에서 봅니다.
- 키체인 백업 파일이 있다고 비밀 값이 들어 있다고 보지 않습니다. 파일의 존재와 풀 수 있는지는 따로입니다.

## 참고 문헌

1. Keybags for Data Protection — Apple Platform Security — https://support.apple.com/guide/security/keybags-for-data-protection-sec6483d5760/web
2. The Secure Enclave — Apple Platform Security — https://support.apple.com/guide/security/secure-enclave-sec59b0b31ff/web
3. How Apple's iOS BackupAgent Creates and Transfers Encrypted Backups to Your Computer — iMazing (2026-05-07 갱신) — https://imazing.com/guides/ios-backupagent
