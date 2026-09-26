---
title: "파일볼트"
parent: "기반 · 보안·보호"
nav_order: 360
has_children: true
has_toc: false
---

# 파일볼트 (FileVault)

파일볼트는 APFS 볼륨을 AES-XTS로 암호화하는 macOS의 볼륨 암호화 기능이고 [1], 조사에서는 디스크를 읽을 수 있는지와 누가 풀 수 있는지, 조직이 복구 키를 맡겨 두었는지를 가늠하는 출발점이 됩니다.

## 왜 중요한가

맥 디스크 이미지를 받으면 가장 먼저 부딪히는 질문이 "이 볼륨을 읽을 수 있는가" 이고, 답은 기종과 파일볼트 설정에 따라 갈립니다. T2 칩을 단 인텔 맥과 Apple silicon 맥은 파일볼트를 켜지 않아도 볼륨이 이미 암호화돼 있고 볼륨 키를 기기 고유의 하드웨어 UID로 보호하며, 파일볼트를 켜면 여기에 사용자 암호가 더해져 부팅할 때 자격 증명을 묻습니다 [1]. T2 칩이 없는 인텔 맥은 Secure Enclave 보호 없이 이동식 저장장치 암호화와 같은 방식을 씁니다 [1]. 그래서 "파일볼트 꺼짐" 이라는 설정만 보고 평문 디스크라고 판단하면 확보 계획이 틀어집니다.

보호 범위도 버전에 따라 다릅니다. macOS 10.15에서는 시스템 볼륨과 데이터 볼륨을 모두 암호화로 보호하고, macOS 11 이후에는 시스템 볼륨을 서명된 시스템 볼륨 (Signed System Volume, SSV)으로 보호하며 데이터 볼륨만 암호화로 보호합니다 [1]. 두 볼륨이 어떻게 한 볼륨처럼 보이는지는 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../../disk-volume/volume-group-firmlinks.md)에 있습니다.

조직이 관리하는 맥이라면 복구 키를 MDM에 맡겨 둔 흔적이 볼륨 밖 파일과 구성 프로파일에 남고, 이 흔적으로 잠긴 볼륨을 정식 경로로 풀 수 있는지 판단할 수 있습니다.

## 한눈에 보기

| 위치 | macOS 버전 | 알려 주는 것 |
|---|---|---|
| APFS 컨테이너·볼륨 키백 | 10.13 이후 (APFS 파일볼트) [2] | 감싼 VEK·KEK, 볼륨을 풀 수 있는 사용자 UUID, 개인 복구 키 설정 여부 |
| 볼륨 슈퍼블록 `apfs_fs_flags` | 10.13 이후 | 소프트웨어 암호화 볼륨인지 처음 가려내기 |
| `/var/db/FileVaultPRK.dat` | 10.13 이후 | MDM 복구 키 에스크로를 설정했던 기기 |
| 구성 프로파일의 파일볼트 페이로드 | 10.9 이후 (10.13 이후 에스크로 페이로드) | 파일볼트를 켜게 한 정책, 복구 키 처리 방식 |
| `/Library/Keychains/FileVaultMaster.keychain` | 공개 자료 없음 | 기관 복구 키를 쓰도록 한 흔적 |
| 기기의 보안 칩 (T2·Apple silicon) | — | 디스크만 떼어 내 풀 수 있는지 가늠 |

관리 기능이 들어온 버전은 아래와 같습니다 [2].

| 항목 | 버전 |
|---|---|
| APFS 파일볼트 구현 | macOS 10.13 이후 |
| 부트스트랩 토큰 도입 | macOS 10.15 |
| 부트스트랩 토큰 MDM 에스크로 | macOS 10.15.4 이후 |
| 부트스트랩 토큰으로 로그인 사용자에게 보안 토큰 부여 | macOS 11 이후 |
| SSH로 파일볼트 잠금 해제 | macOS 26 이후 (Apple silicon) |

이 허브는 APFS 파일볼트만 다룹니다. macOS 10.12 이하의 HFS+ 볼륨에서 쓰던 CoreStorage 방식과 파일볼트를 켜고 끌 때 남는 로그·설정 파일은 다루지 않습니다.

## 읽는 순서

1. [키 계층 (VEK·KEK)](key-hierarchy.md) — VEK·KEK·미디어 키가 어떻게 이어지는지, 컨테이너·볼륨 키백과 슈퍼블록 플래그의 구조와 오프셋을 다룹니다.
2. [복구 키 (Recovery Key)](recovery-key.md) — 개인·기관·iCloud 복구 키가 어떻게 다른지, MDM 에스크로 페이로드와 `/var/db/FileVaultPRK.dat` 가 무엇을 증명하는지 다룹니다.
3. [보안 칩과 데이터 보호 (T2·Apple Silicon·Secure Enclave)](secure-enclave.md) — 하드웨어 UID와 Secure Enclave가 키를 어떻게 지키는지, 기종별 차이와 증거 확보에 주는 영향을 다룹니다.

## 함께 볼 페이지

- [APFS 구조 (APFS)](../../disk-volume/apfs/index.md) — 컨테이너·볼륨·슈퍼블록의 기본 구조
- [키체인 (Keychain)](../keychain/index.md) — 개인 복구 키와 기관 복구 키가 저장되는 곳
- [구성 프로파일 (Configuration Profiles·MDM)](../../../02-artifacts/persistence/configuration-profiles.md) — 파일볼트 페이로드가 든 프로파일을 찾는 법
- [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md) — 암호화된 맥을 확보하는 순서
- [암호화된 증거 다루기 (Encrypted Evidence)](../../../03-techniques/analysis/encrypted-evidence/index.md) — 잠긴 볼륨을 만났을 때의 판단

## 참고 문헌

1. Apple Platform Security — Volume encryption with FileVault in macOS — https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/web
2. Apple Platform Security — Managing FileVault in macOS — https://support.apple.com/guide/security/managing-filevault-sec8447f5049/web
