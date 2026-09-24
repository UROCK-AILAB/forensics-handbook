---
title: "라이브 이미징"
parent: "맥 증거 확보"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1950
---

# 라이브 이미징 (Live Imaging)

라이브 이미징은 켜져 있고 잠금이 풀린 맥에서 디스크나 폴더의 내용을 이미지 파일로 떠내는 방법이고, 암호나 복구 키가 없는 T2·Apple silicon 맥에서는 풀린 데이터를 이미지로 얻을 거의 유일한 때라고 판단합니다 [1].

## 언제 쓰나

맥이 켜져 있고 잠금이 풀려 있으며, 필요한 파일만 골라 모으는 [논리 수집 (Logical Collection)](logical-collection.md)보다 넓게 떠야 할 때 씁니다. 맥을 끄면 왜 이 기회를 잃는지와 방법을 고르는 순서는 [확보 방법 고르기 (T2·Apple Silicon)](choosing-method.md)에 있습니다. 휘발성 정보를 먼저 모으는 순서는 [라이브 대응 (Live Response)](../live-response/index.md)을 따릅니다.

## 절차

아래는 macOS에 들어 있는 디스크 유틸리티로 이미지를 만드는 절차입니다.

1. 맥의 상태와 시각, 결과를 받을 외부 저장 매체를 기록합니다. 이미지 파일은 외부 매체에 씁니다.
2. 디스크 유틸리티에서 File > New Image를 고릅니다. 메뉴에는 "Blank Image", "Image from [장치 이름]", "Image from Folder" 가 있습니다 [4].
3. 떠낼 대상을 고릅니다. 개별 APFS 볼륨은 이미지로 만들 수 없고("You can't create images of individual APFS volumes"), Apple silicon·T2 맥에서는 APFS 컨테이너도 이미지로 만들 수 없어서 [4], 필요한 사용자 폴더나 데이터를 "Image from Folder" 로 뜨는 쪽이 현실적이라고 판단합니다.
4. 형식은 Read-only(UDRO)를 고릅니다. 만든 뒤 바꿀 수 없는 형식이라서 [4] 증거 사본에 맞습니다.
5. 이미지를 다 만들면 곧바로 해시를 계산해 보관 기록에 적습니다. 방법은 [해시와 증거 보관 (Hash·Chain of Custody)](hash-chain-of-custody.md)에 있습니다.

## 도구

### 디스크 유틸리티의 이미지 형식

디스크나 볼륨에서 이미지를 만들 때 고를 수 있는 형식은 아래와 같습니다 [4].

| 형식 | 성질 |
|---|---|
| Read-only (UDRO) | 만든 뒤 바꿀 수 없음 |
| Read-only Compressed (ULFO) | 압축한 읽기 전용 |
| RAW Image | 만든 뒤 항목을 더하거나 지우거나 고칠 수 있음 |
| DVD/CD master | CD·DVD 크기에 맞춘 이미지 |

빈 이미지를 만들 때는 두 읽기 전용 형식 대신 데이터에 따라 커지는 읽기·쓰기 형식인 Sparse Bundle(UDSB)과 Apple Sparse Image(ASIF)가 나오고, 폴더에서 만들 때는 HFS+·ISO·UDF를 함께 담는 Hybrid image도 고를 수 있습니다 [4]. 암호화 팝업 메뉴도 있지만 고를 수 있는 암호 강도는 확인하지 못했고, ASIF가 어느 macOS 버전에서 추가됐는지도 확인하지 못했습니다. 각 형식의 구조는 [디스크 이미지 형식 (DMG·Sparsebundle)](../../../01-foundations/disk-volume/dmg-sparsebundle.md)에서 다룹니다.

### 그 밖의 방법

명령줄에서 raw 디스크 장치를 직접 읽는 방법, 폴더를 명령줄로 이미지로 만드는 방법, APFS 로컬 스냅숏으로 시점을 고정한 뒤 복사하는 방법도 생각할 수 있습니다. 다만 이 방법들이 요구하는 권한(root, SIP, 전체 디스크 접근 권한), 원본 맥에 남기는 흔적, T2·Apple silicon 맥의 물리 디스크를 켜진 상태에서 읽을 때 암호문이 나오는지 평문이 나오는지를 이번에 확인한 자료로 따져 보지 못해서 절차로 싣지 않습니다. 쓰기 전에 같은 기종의 시험용 맥에서 결과를 확인하고 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md)에 따라 기록합니다. 스냅숏의 성질은 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../analysis/snapshot-diff.md)와 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md)에서 봅니다.

### 메모리

UAC는 메모리 획득이 리눅스에서만 되고 macOS에서는 되지 않는다고 적습니다 [2]. 맥 메모리를 수집하는 도구의 현황은 이번에 확인하지 못했고, 메모리 쪽은 [메모리 분석 (Memory Forensics)](../../analysis/memory-forensics/index.md)에서 이어 봅니다.

## 함정과 한계

Apple 안내는 "You can't create images of individual APFS volumes. You can't create images of APFS containers on Mac computers with Apple silicon or an Apple T2 Security Chip." 이라고 적습니다 [4]. 그래서 T2·Apple silicon 맥에서는 디스크 유틸리티로 내장 APFS 볼륨이나 컨테이너를 통째로 이미징할 수 없습니다. "Image from Folder" 로 얻은 결과는 블록 단위 사본이 아니라 폴더에 든 파일의 사본이고, 지운 파일이 남은 빈 공간은 담기지 않습니다.

이미지를 만드는 동안에도 맥은 돌아가고 있어서 파일이 바뀔 수 있습니다. 이미지 작업을 시작한 시각과 끝난 시각을 함께 적어, 그 사이의 변경이 사본에 섞였을 수 있다는 점을 보고서에 밝힙니다.

압축 형식을 고를 때는 분석 도구가 읽을 수 있는지도 봅니다. mac_apt의 입력 목록에는 압축하지 않은 DMG만 적혀 있어서 [3], Read-only Compressed(ULFO)로 만든 이미지를 mac_apt에 바로 넣을 수 있는지는 미리 확인합니다. mac_apt의 다른 입력 형식은 [논리 수집 (Logical Collection)](logical-collection.md)에 정리했습니다.

## 결과를 어떻게 해석하나

라이브 이미지는 "잠금이 풀린 상태에서 그 시각의 파일 시스템이 보여 준 내용" 입니다. 보고서에는 "켜져 잠금이 풀린 맥에서 디스크 유틸리티로 이 폴더를 Read-only(UDRO) 이미지로 만들었고, 작업은 이 시각에 시작해 이 시각에 끝났다" 처럼 상태·도구·형식·대상·시각을 적습니다. 이미지 안의 파일 시각을 해석하는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)과 [타임라인 작성 (Timeline)](../../analysis/timeline/index.md)에서 다룹니다.

## 참고 문헌

1. Volume encryption with FileVault in macOS (Apple Platform Security) — https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/web
2. tclahr/uac README (GitHub) — https://github.com/tclahr/uac
3. ydkhatri/mac_apt README (GitHub) — https://github.com/ydkhatri/mac_apt
4. Create a disk image using Disk Utility on Mac (Disk Utility User Guide) — https://support.apple.com/guide/disk-utility/create-a-disk-image-dskutl11888/mac
