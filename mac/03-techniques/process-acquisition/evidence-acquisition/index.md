---
title: "맥 증거 확보"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 1910
has_children: true
has_toc: false
---

# 맥 증거 확보 (Acquisition)

맥의 상태와 기종에 맞춰 확보 방법을 고르고, 방법마다 무엇을 얻는지와 무엇을 기록할지를 다루는 페이지 묶음의 입구입니다.

## 왜 중요한가

Apple silicon 맥과 T2 보안 칩이 달린 인텔 맥은 파일볼트(FileVault)를 꺼 두어도 내장 볼륨이 암호화되어 있고, 이때 볼륨 암호화 키는 보안 영역(Secure Enclave) 안의 하드웨어 UID로만 보호됩니다 [1]. 파일볼트를 켜면 사용자 암호와 하드웨어 UID를 함께 써서 키를 보호하고, 키 처리는 모두 보안 영역 안에서 일어나서 CPU에 키가 직접 드러나지 않습니다 [1]. 올바른 자격 증명이나 복구 키가 없으면 저장 장치를 떼어 다른 컴퓨터에 연결해도 볼륨은 암호화된 채로 남습니다 [1].

이런 맥은 디스크를 떼어 쓰기 방지 장치에 물리고 블록 이미지를 뜨는 전통 방식으로는 내용을 읽을 수 없습니다. 그래서 맥이 켜져 있는지, 잠금이 풀려 있는지, 암호나 복구 키를 아는지, 인텔 맥인지 Apple silicon 맥인지를 먼저 확인하고, 그 조합에 따라 방법을 고릅니다. 방법마다 결과물이 파일 수준(논리) 사본인지 블록 수준 사본인지가 달라서, 보고서에도 이 차이를 적어 둡니다.

## 한눈에 보기

| 방법 | 쓰는 때 | 얻는 것 | 조건·제한 |
|---|---|---|---|
| 논리 수집 | 맥이 켜져 있고 잠금이 풀려 있을 때 | 파일 수준 수집물. Aftermath는 zip 아카이브 하나로 결과를 씁니다 [4] | Aftermath는 root와 전체 디스크 접근 권한(Full Disk Access)이 있어야 실행됩니다 [4] |
| 공유 디스크 모드 (Share Disk) | Apple silicon 맥을 macOS 복구로 시동할 수 있을 때 | 다른 맥의 Finder에서 네트워크 항목으로 접속하는 파일 수준 접근 [3] | 두 맥을 케이블로 연결합니다 [3]. 블록 이미지는 기대하기 어렵습니다 |
| 대상 디스크 모드 (Target Disk Mode) | 인텔 맥을 T 키를 누른 채 켤 수 있을 때 | 다른 맥에 디스크로 나타나는 접근 [2] | Thunderbolt 케이블로 연결합니다 [2] |
| 라이브 이미징 | 맥이 켜져 있고 잠금이 풀려 있을 때 | 디스크 유틸리티로 만든 디스크·폴더 이미지 [8] | 디스크 유틸리티로는 개별 APFS 볼륨의 이미지를 만들 수 없고, Apple silicon·T2 맥에서는 APFS 컨테이너의 이미지도 만들 수 없습니다 [8] |
| 해시와 증거 보관 | 모든 방법 | 수집물의 해시와 이관 기록 | 증거를 다룬 사람, 수집·이관 날짜와 시각, 이관 목적을 기록합니다 [7] |

macOS 버전에 따라 확보 결과를 다루는 방식도 달라집니다.

| macOS | 확보와 관련해 달라지는 점 |
|---|---|
| 10.15 Catalina 이후 | 시스템(SYSTEM) 볼륨과 데이터(DATA) 볼륨이 따로 마운트되고, mac_apt 같은 분석 도구는 두 볼륨을 함께 처리합니다 [6] |
| 11 Big Sur 이후 | 시스템 볼륨이 봉인(sealed)되어 있습니다 [6] |
| 12.0 이상 | Aftermath가 지원하는 범위입니다 [4] |

## 읽는 순서

1. [확보 방법 고르기 (T2·Apple Silicon)](choosing-method.md) — 암호화 구조와 부팅 보안 설정을 보고, 맥의 상태별로 쓸 수 있는 방법을 판단표로 고릅니다.
2. [논리 수집 (Logical Collection)](logical-collection.md) — Aftermath [4]·UAC [5] 같은 공개 수집 도구로 켜진 맥에서 파일을 모으고, mac_apt [6] 같은 도구로 수집물을 분석하는 흐름을 봅니다.
3. [공유 모드와 대상 디스크 모드 (Share Disk·Target Disk Mode)](share-disk-target-disk.md) — 꺼진 맥의 디스크를 다른 맥에서 여는 두 방식의 절차와 얻을 수 있는 범위를 봅니다.
4. [라이브 이미징 (Live Imaging)](live-imaging.md) — 켜진 맥에서 디스크 유틸리티로 이미지를 만드는 방법과 형식별 차이, 막혀 있는 길을 봅니다.
5. [해시와 증거 보관 (Hash·Chain of Custody)](hash-chain-of-custody.md) — 수집물의 해시를 남기고 이관 기록을 적는 방법을 봅니다.

## 함께 볼 페이지

- [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md) — 볼륨 암호화 키를 어떻게 보호하는지 자세히 설명합니다.
- [암호화된 증거 다루기 (Encrypted Evidence)](../../analysis/encrypted-evidence/index.md) — 확보한 이미지가 암호화되어 있을 때 이어서 봅니다.
- [라이브 대응 (Live Response)](../live-response/index.md) — 켜진 맥에서 수집 전에 할 일을 다룹니다.
- [조사 절차 (Investigation Process)](../investigation-process.md) — 증거 확보가 조사 전체의 어느 단계에 들어가는지 봅니다.
- [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md)와 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../../../01-foundations/disk-volume/volume-group-firmlinks.md) — 시스템 볼륨과 데이터 볼륨이 나뉘는 구조를 설명합니다.
- [디스크 이미지 형식 (DMG·Sparsebundle)](../../../01-foundations/disk-volume/dmg-sparsebundle.md) — 디스크 유틸리티가 만드는 이미지 파일의 구조를 설명합니다.
- [개인 정보 보호 권한 (TCC)](../../../02-artifacts/credentials/tcc/index.md) — 수집 도구에 준 전체 디스크 접근 권한이 어디에 기록되는지 봅니다.
- [도구 검증 (Tool Validation)](../../reporting/tool-validation.md)과 [포렌식 보고서 (Forensic Report)](../../reporting/forensic-report.md) — 수집 도구를 검증하고 확보 과정을 보고서에 적는 방법을 다룹니다.

## 참고 문헌

1. Apple, "Volume encryption with FileVault in macOS", Apple Platform Security — https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/web
2. Apple, "Transfer files between two Mac computers using target disk mode" (HT201462) — https://support.apple.com/HT201462
3. Apple, "Use macOS Recovery on a Mac with Apple silicon", Mac User Guide — https://support.apple.com/guide/mac-help/macos-recovery-a-mac-apple-silicon-mchl82829c17/mac
4. Jamf, aftermath README (GitHub) — https://github.com/jamf/aftermath
5. tclahr, uac README (GitHub) — https://github.com/tclahr/uac
6. ydkhatri, mac_apt README (GitHub) — https://github.com/ydkhatri/mac_apt
7. NIST CSRC Glossary, "chain of custody" — https://csrc.nist.gov/glossary/term/chain_of_custody
8. Apple, "Create a disk image using Disk Utility on Mac", Disk Utility User Guide — https://support.apple.com/guide/disk-utility/create-a-disk-image-dskutl11888/mac
