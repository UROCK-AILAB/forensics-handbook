---
title: "APFS 구조"
parent: "기반 · 디스크·볼륨"
nav_order: 0
has_children: true
has_toc: false
---

# APFS 구조 (APFS)

APFS (Apple File System)는 HFS Plus의 뒤를 이은 Apple 플랫폼의 기본 파일 시스템이고, 컨테이너 층과 파일 시스템 층 두 층 안에 파일 메타데이터와 시각, 확장 속성, 스냅숏 정보를 모두 B-트리 레코드로 담습니다 [1].

## 왜 중요한가

이 핸드북이 다루는 아티팩트는 대부분 APFS 볼륨 위의 파일이라서, 이미지에서 plist 하나를 꺼내려 해도 먼저 이 구조를 읽어야 합니다. APFS는 파일 복제, 스냅숏, 암호화, 볼륨 사이의 여유 공간 공유를 지원하고 [1], 이 기능들이 모두 증거를 읽는 방법에 영향을 줍니다. 스냅숏에는 확보 시점보다 앞선 볼륨 상태가 남고, 압축 파일은 압축 정보와 내용이 확장 속성에 들어가며, 복제 파일은 다른 파일과 블록을 나눠 씁니다.

APFS는 저널을 쓰지 않고 copy-on-write로 충돌에 대비하며 [3][4], 디스크의 객체를 제자리에서 고치지 않고 고친 사본을 늘 새 위치에 씁니다 [1]. 지운 파일을 찾을 때는 저널이 아니라 옛 체크포인트와 옛 노드 사본을 살펴보고, 메타데이터에는 Fletcher 체크섬이 붙어 있어 [4] 찾은 블록이 온전한지도 확인할 수 있습니다.

두 층은 숫자를 모두 리틀 엔디언으로 저장하고, 컨테이너 층(`nx_` 접두사) 객체는 `obj_phys_t` 헤더로, 파일 시스템 층(`j_` 접두사) 레코드는 `j_key_t` 로 시작합니다 [1]. 시각은 모두 1970-01-01 00:00 UTC부터 센 나노초라서 [1] 2001년 기준인 맥 절대 시각과 다릅니다.

구조체·필드 이름·상수는 Apple File System Reference 2020-06-22 판에 정의되어 있고 [1], 바이트 오프셋은 이 명세에 없어 libyal 형식 문서에서 찾습니다 [2]. 이 판에는 macOS 11에서 추가된 봉인 볼륨 필드까지 들어 있고, macOS 12 이후 바뀐 점은 들어 있지 않으므로 검체에서 확인합니다. 공개 도구로는 HFS와 APFS 파서를 자체 구현한 mac_apt [5], 지운 파일 복구를 목표로 만든 afro [6]가 있고, afro는 지금 유지보수하지 않습니다 [6].

## 한눈에 보기

| 구조 | 위치 | macOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 컨테이너 슈퍼블록 | 블록 0의 사본과 체크포인트 서술자 영역 [1] | 10.12는 시험판(`NX_INCOMPAT_VERSION1`), 10.13부터 `NX_INCOMPAT_VERSION2` [1] | 블록 크기, 볼륨 목록, 체크포인트 위치, 마운트한 가장 새 소프트웨어 버전 |
| 볼륨 슈퍼블록 | 컨테이너 객체 맵으로 찾음 [1] | 볼륨 그룹 칸은 10.15, 봉인 볼륨 칸은 11에서 추가 [1] | 볼륨 이름과 역할, 볼륨을 만들고 고친 소프트웨어와 그 시각 |
| 체크포인트와 객체 맵 | 체크포인트 서술자·데이터 영역 [1] | | 과거 시점의 컨테이너 상태, 가상 객체의 위치 |
| 파일 시스템 트리 | 볼륨 객체 맵에서 찾는 루트 트리 [1] | 아이노드의 압축 전 크기 칸은 10.15부터 유효 [1] | 아이노드, 디렉터리 항목, 익스텐트, 하드 링크 |
| 시각 | 아이노드와 디렉터리 항목 [1] | 1970 UTC 기준 나노초 [1] | 생성·수정·속성 변경·접근·추가 시각 |
| 확장 속성 | XATTR 레코드 [1] | | 격리 정보, 다운로드 출처, 압축 정보, 심볼릭 링크 대상 |
| 스냅숏 | 스냅숏 메타데이터 트리 [1] | 10.13부터 업데이트 전 스냅숏, 11부터 시스템 스냅숏에서 부팅 [7][8] | 과거 시점의 볼륨 전체 |
| 복제·희소·압축 | 아이노드 플래그, `com.apple.decmpfs` 속성 [1][2] | 복제 정보 칸은 10.13.3에서 추가 [1] | 블록을 나눠 쓰는 파일, 압축 방식과 압축 전 크기 |
| 지운 파일 | 옛 슈퍼블록과 옛 노드, free queue [1] | | 지운 파일의 메타데이터를 찾을 단서 |

## 읽는 순서

1. [컨테이너와 볼륨 (Container·Volume)](container-volume.md) — 파티션에서 컨테이너와 볼륨을 찾고, 두 슈퍼블록의 칸과 볼륨 역할, macOS 10.15 이후의 볼륨 배치를 읽습니다.
2. [객체와 체크포인트 (Object·Checkpoint)](object-checkpoint.md) — 객체 헤더와 세 가지 저장 방식, 체크포인트와 객체 맵, B-트리 노드를 따라 마운트 순서를 손으로 밟아 봅니다.
3. [파일 시스템 트리와 아이노드 (FS Tree·Inode)](fs-tree-inode.md) — 레코드 형식과 아이노드·디렉터리 항목·익스텐트·하드 링크 레코드를 읽습니다.
4. [APFS의 시각 네 가지 (Create·Modify·Change·Access)](timestamps.md) — 아이노드 시각 네 개와 `date_added` 의 뜻, 접근 시각 갱신 규칙을 다룹니다.
5. [확장 속성 (Extended Attributes)](extended-attributes.md) — XATTR 레코드의 키와 값, 레코드 안과 데이터 스트림에 저장하는 방식, 관찰된 속성 이름을 정리합니다.
6. [스냅숏 (Snapshots)](snapshots.md) — 스냅숏 메타데이터와 macOS가 스냅숏을 쓰는 곳, 스냅숏 안의 파일을 읽는 순서를 다룹니다.
7. [복제·희소·압축 파일 (Clone·Sparse·Compression)](clone-sparse-compression.md) — 복제 플래그를 믿을 조건, 희소 구간, decmpfs 헤더와 압축 방식 번호를 다룹니다.
8. [지운 파일과 옛 체크포인트 (Deleted Files·Old Checkpoints)](deleted-files.md) — 옛 슈퍼블록과 옛 노드, 공간 관리자와 참조 수를 따라 지운 파일의 단서를 찾는 순서를 다룹니다.

## 함께 볼 페이지

- [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../volume-group-firmlinks.md) — 시스템 볼륨과 데이터 볼륨이 하나처럼 보이는 방식
- [파티션 구조 (GPT·APFS 파티션)](../gpt-partitions.md) — APFS 컨테이너를 담은 파티션을 찾을 때
- [HFS+ 구조 (HFS+)](../hfs-plus.md) — APFS 이전 파일 시스템과 비교할 때
- [디스크 이미지 형식 (DMG·Sparsebundle)](../dmg-sparsebundle.md) — 이미지 파일 안의 APFS를 열 때
- [파일볼트 (FileVault)](../../protection/filevault/index.md) — 암호화된 볼륨을 다룰 때
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../value-decoding/mac-time-values.md) — APFS 시각과 다른 시각 기준을 비교할 때
- [압축 형식 (LZFSE·LZ4·zlib)](../../value-decoding/compression.md) — 압축 파일의 데이터를 풀 때
- [타임 머신 (Time Machine)](../../../02-artifacts/filesystem/time-machine/index.md) — 로컬 스냅숏과 백업 볼륨
- [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md) — APFS 볼륨을 이미지로 만들 때
- [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md) — 지운 파일을 되살릴 때
- [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../../03-techniques/analysis/snapshot-diff.md) — 스냅숏과 현재 상태를 나란히 놓을 때
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) — 파일 시스템 시각으로 타임라인을 만들 때

## 참고 문헌

1. Apple, Apple File System Reference (2020-06-22 판, PDF) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
2. Joachim Metz, libfsapfs — Apple File System (APFS) 형식 문서 (개정 0.0.18, 2026년 8월) — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
3. Apple, Apple File System Guide — Features (보관 문서, 2018-06-04) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/Features/Features.html
4. Apple, Apple File System Guide — Frequently Asked Questions (보관 문서, 2018-06-04) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/FAQ/FAQ.html
5. mac_apt README, Yogesh Khatri (v1.33.2) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/README.md
6. afro (APFS file recovery) README, Jonas Plum — https://raw.githubusercontent.com/cugu/afro/master/README.md
7. Apple Support, About Time Machine local snapshots (102154, 게시 2026-07-06) — https://support.apple.com/en-us/102154
8. Apple Platform Security — Role of Apple File System (게시 2024-12-19) — https://support.apple.com/guide/security/role-of-apple-file-system-seca6147599e/web
