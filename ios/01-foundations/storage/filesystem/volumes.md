---
title: "볼륨 구성"
parent: "iOS의 파일 시스템"
grand_parent: "기반 · 저장 구조"
nav_order: 10
---

# 볼륨 구성 (System·Data·Preboot)

아이폰 저장소는 APFS 컨테이너 안에 여러 볼륨으로 나뉘어 있고, 운영체제는 서명된 시스템 볼륨에, 사용자와 앱의 데이터는 암호화된 Data 볼륨에 들어 있습니다.

## 이 구조를 쓰는 아티팩트

이 핸드북에서 다루는 사용자 아티팩트(메시지·사진·위치·앱 사용 기록 등)는 거의 모두 Data 볼륨에 있습니다. 로컬 백업이 기기 경로를 "도메인 + 상대 경로" 로 적는 방식도 Data 쪽 경로를 기준으로 하고, 시스템 볼륨의 내용은 백업에 도메인으로 나타나지 않습니다(아래 "로컬 백업에서 보이는 범위"). 그래서 어떤 볼륨에 무엇이 있는지 알면, 수집 방법마다 어디까지 볼 수 있는지 미리 가늠할 수 있습니다.

## 구조

### 볼륨 목록

The Eclectic Light Company 의 관찰에 따르면 iOS 18.5 아이폰의 저장소는 APFS 컨테이너 2개로 나뉘고, 첫 컨테이너는 약 351 MB 입니다 [2]. 같은 글은 iPadOS 18.5 아이패드도 함께 비교했습니다.

| 볼륨 | iOS 18.5 (iPhone 15 Pro) | iPadOS 18.5 (iPad Pro 11형 4세대) | 비고 |
|---|---|---|---|
| System | 있음 | 있음 | iOS 15 이상은 서명된 시스템 볼륨 [1] |
| Data | 있음(암호화) | 있음 | 사용자·앱 데이터 |
| Preboot | 있음 | 있음 | |
| xART | 있음 | 있음 | |
| Hardware | 있음 | 있음 | |
| Baseband Data | 있음 | 목록에 없음 | iOS 에만 있음 [2] |
| User | 목록에 없음 | 있음 | iPadOS 에만 있는 것으로 보임 [2] |
| Update | 없음 | 있음 | 아이폰에는 없다고 적음 [2] |

출처: [2]. 첫 컨테이너 크기는 아이패드 쪽이 약 367 MB 입니다.

같은 글은 dyld 캐시와 Safari 를 담은 시스템 크립텍스(cryptex)와 AI 기능용 PFK 볼륨도 있다고 적었지만, 크립텍스가 어느 볼륨의 어느 경로에 있는지는 이번에 확인한 자료에 없습니다. xART·Hardware·Preboot 에 무엇이 들어 있는지도 확인한 자료가 없어 이 쪽에서는 이름만 적습니다. 맥에 있는 Recovery·VM 볼륨은 iOS·iPadOS 에 없습니다 [2].

> 그림 자리: 컨테이너 2개와 그 안의 볼륨(System·Data·Preboot·xART·Hardware·Baseband Data)을 상자로 나눠 보여 주고, Data 볼륨에만 사용자 데이터 표시

### System 볼륨 — 서명된 시스템 볼륨

iOS 15·iPadOS 15 이상에서 시스템 볼륨은 서명된 시스템 볼륨 (Signed System Volume, SSV) 입니다 [1]. 파일 시스템 메타데이터에 데이터 해시의 기대값을 두고, 모든 바이트를 아우르는 루트 해시를 "seal" 이라 부르며, Apple 이 이 seal 에 서명합니다 [1]. iOS·iPadOS 부트로더는 커널을 시작하기 전에 seal 이 온전한지, Apple 이 서명한 값과 맞는지 확인하고, 실행 중에는 커널이 시스템 내용을 검사해서 Apple 의 서명이 맞지 않는 데이터는 코드든 아니든 거부합니다 [1]. iOS·iPadOS 에서는 사용자가 이 보호를 끌 수 없습니다 [1].

시스템 볼륨의 스냅숏과 업데이트 때의 동작은 [시스템 스냅숏과 업데이트](snapshots-updates.md) 에서 다룹니다.

### Data 볼륨 — 암호화와 파일별 키

Data 볼륨은 암호화됩니다 [2]. 데이터 볼륨에 파일을 만들 때마다 256비트 파일별 키가 새로 생기고, A14~A18·M1 이후 칩의 기기는 AES-256 XTS, A9~A13·S5 이후 칩의 기기는 AES-128 XTS 로 암호화합니다 [8]. APFS 는 이 키를 파일 조각(extent) 단위로 더 나눌 수 있어서, 한 파일 안에서도 조각마다 키가 다를 수 있습니다 [8]. 각 파일은 데이터 보호 클래스에 배정되고 클래스 키가 풀렸는지에 따라 접근이 정해지며, 서드파티 앱의 파일도 자동으로 이 보호를 받습니다 [8]. 클래스와 잠금 상태의 관계는 [데이터 보호](../data-protection/index.md) 에서 다룹니다.

앱 데이터가 들어가는 경로와 컨테이너 구조는 [앱 컨테이너](app-containers.md) 에서 다룹니다.

## 읽는 법 — 로컬 백업에서 보이는 범위

로컬 백업은 볼륨을 통째로 담지 않고, 기기 경로를 "도메인 + 상대 경로" 로 바꿔 파일 단위로 담습니다 [7]. 백업 안의 파일 이름은 `sha1(domain + '-' + relativePath)` 이고 [7], 도메인과 상대 경로의 목록은 `Manifest.db` 의 `Files` 표에 있습니다(칸: `fileID`, `domain`, `relativePath`, `flags`, `file`) (확인 범위: iOS 27.0). 백업 형식 자체는 [로컬 백업](../../backups/local-backup/index.md) 에서 다룹니다.

도메인은 Data 쪽 경로에 대응합니다 [7]. 아래 표의 "관찰 항목 수" 는 관찰한 백업 한 개의 `Files` 행 수라서 기기와 사용 상태에 따라 달라집니다.

| 백업 도메인 | 기기 경로 [7] | 관찰 항목 수 |
|---|---|---|
| HomeDomain | `/var/mobile` | 1979 |
| MediaDomain | `/var/mobile` 아래 | 303 |
| CameraRollDomain | `/var/mobile` 아래 | 173 |
| RootDomain | `/var/root` | 58 |
| WirelessDomain | `/var/wireless` | 21 |
| SystemPreferencesDomain | `/var/preferences` | 11 |
| DatabaseDomain | `/var/db` | 9 |
| ManagedPreferencesDomain | `/var/Managed Preferences` | 4 |
| KeychainDomain | `/var/Keychains` | 2 |

관찰 항목 수의 확인 범위: iOS 27.0.

관찰한 백업에는 이 밖에 HealthDomain, InstallDomain, KeyboardDomain, MobileDeviceDomain, ProtectedDomain, TonesDomain 도 하나씩 있었지만, 이 도메인들의 기기 경로는 이번에 확인한 자료에 없습니다 (확인 범위: iOS 27.0). 앱별 도메인(`AppDomain-`, `AppDomainGroup-` 등)은 [앱 컨테이너](app-containers.md) 에서 다룹니다.

`/System`, `/usr` 처럼 시스템 볼륨에 있는 내용에 대응하는 도메인은 관찰한 백업에 없었습니다 (확인 범위: iOS 27.0). 그 이유를 설명한 공식 자료는 확인하지 못했습니다.

## 포렌식에서 중요한 점

시스템 볼륨은 부팅 전과 실행 중에 서명 검사를 거치고 iOS 에서는 사용자가 이 보호를 끌 수 없어서 [1], 사용자 활동의 흔적은 Data 볼륨에서 찾습니다. 스파이웨어 조사에서 무엇을 먼저 보는지는 [악성 코드·스파이웨어 흔적](../../../03-techniques/analysis/spyware-triage/index.md) 에서 다룹니다.

Data 볼륨의 파일은 만들 때마다 새로 생긴 파일별 키로 암호화되고 키가 조각 단위로 나뉠 수도 있어서 [8], 볼륨을 다룰 때는 암호화된 블록과 풀린 파일 내용을 구분해야 합니다. 지운 데이터를 찾는 방법은 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

## 함정

- **볼륨 목록은 관찰 기록입니다.** 위 볼륨 표는 한 필자가 iOS 18.5 기기 한 대씩에서 본 목록이고 [2], Apple 이 iOS 버전별 볼륨 목록을 표로 공개한 자료는 이번에 확인하지 못했습니다. 다른 버전·기종에서는 볼륨이 더하거나 빠질 수 있습니다.
- **로컬 백업으로 볼륨 구성을 확인할 수는 없습니다.** 백업에는 도메인과 상대 경로만 있고 볼륨·스냅숏 정보가 없습니다 (확인 범위: iOS 27.0).
- **fskit 확장 도메인을 볼륨 정보로 읽지 않습니다.** 관찰한 백업에 `AppDomainPlugin-com.apple.fskit.apfs`, `AppDomainPlugin-com.apple.fskit.exfat`, `AppDomainPlugin-com.apple.fskit.hfs`, `AppDomainPlugin-com.apple.fskit.msdos` 가 각각 항목 4개씩 있었지만 (확인 범위: iOS 27.0) 이름만 확인했고 내용과 역할은 확인하지 못했습니다.
- **마운트 위치는 따로 확인해야 합니다.** Data 볼륨과 Preboot 가 어느 경로에 마운트되는지는 이번에 확인한 자료에 없습니다. 이 쪽의 경로는 백업 도메인 대응표 [7] 의 경로만 적었습니다.

## 참고 문헌

- [1] Signed system volume security — Apple Platform Security Guide. https://support.apple.com/guide/security/signed-system-volume-security-secd698747c9/web
- [2] Boot disk structure in macOS, iOS and iPadOS, and AI cryptexes — The Eclectic Light Company (2025-06-20). https://eclecticlight.co/2025/06/20/boot-disk-structure-in-macos-ios-and-ipados-and-ai-cryptexes/
- [7] A deep dive into the iOS backup/restore system — GitHub Gist (leminlimez). https://gist.github.com/leminlimez/c602c067349140fe979410ef69d39c28
- [8] Data Protection overview — Apple Platform Security Guide. https://support.apple.com/guide/security/data-protection-overview-secf6276da8a/web
