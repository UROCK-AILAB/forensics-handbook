---
title: "볼륨 그룹과 펌링크"
parent: "기반 · 디스크·볼륨"
nav_order: 90
---

# 볼륨 그룹과 펌링크 (Volume Group·Firmlinks)

## 한 줄 요약

macOS 10.15 Catalina 부터 시동 디스크는 읽기 전용 시스템 볼륨과 읽고 쓰는 데이터 볼륨으로 나뉘고, 볼륨 그룹 (Volume Group) 이 두 볼륨을 한 디스크처럼 묶고 펌링크 (Firmlink) 가 두 볼륨의 디렉터리를 이어 붙여 하나의 디렉터리 계층으로 보여 줍니다.

## 이 형식을 쓰는 아티팩트

macOS Catalina 이후 시스템은 "Macintosh HD" 라는 읽기 전용 시스템 볼륨에서 돌아가고, 파일과 데이터는 "Macintosh HD - Data" 라는 다른 볼륨에 저장됩니다[5]. 읽기 전용 시스템 볼륨에는 파일을 저장할 수 없고 명령줄에서 루트(`/`)에도 쓸 수 없어서, 아티팩트 사전에서 다루는 사용자 파일과 앱 데이터는 이미지에서 데이터 볼륨을 열어야 나옵니다. Finder 에는 두 볼륨이 모두 "Macintosh HD" 로 보이지만 디스크 유틸리티에는 따로 보이므로, 사용자 화면에서 본 이름만으로는 어느 볼륨 이야기인지 가를 수 없습니다.

예전 버전에서 Catalina 로 올린 맥은 사정이 조금 다릅니다. 업그레이드할 때 기존 주 볼륨의 역할을 데이터 볼륨으로 바꾸고, 시스템 소프트웨어만 담긴 디렉터리를 걷어 낸 뒤, 시스템 소프트웨어만 담는 빈 볼륨을 새로 만듭니다[4]. 그래서 업그레이드한 맥에서는 데이터 볼륨이 원래 쓰던 볼륨 그대로이고 시스템 볼륨이 새로 만든 볼륨입니다. 업그레이드 때 새 위치로 옮기지 못한 파일은 `/Users/Shared/Relocated Items` 폴더에 들어가고 그 안에 설명 PDF 가 함께 놓입니다. 업그레이드 이전에 시스템 영역에 있던 파일의 흔적을 찾을 때 이 폴더를 먼저 봅니다.

| 항목 | 처음 나온 버전 |
|---|---|
| 읽기 전용 시스템 볼륨, 볼륨 그룹, 펌링크 | macOS 10.15 |
| 볼륨 역할 가운데 상위 10비트 역할 (DATA·BASEBAND 제외) | macOS 10.15 · iOS 13 |
| 서명된 시스템 볼륨 (SSV), 기능 플래그 `APFS_INCOMPAT_SEALED_VOLUME`, 필드 `apfs_integrity_meta_oid`·`apfs_fext_tree_oid` | macOS 11 |

macOS 11 부터는 시스템 볼륨을 서명된 시스템 볼륨 (Signed System Volume, SSV) 으로 보호해서 시스템 볼륨을 더는 암호화할 필요가 없고, 파일볼트를 켜면 데이터 볼륨은 여전히 사용자 비밀로 암호화됩니다. SSV 는 SHA-256 해시를 파일 시스템 메타데이터 트리에 저장하고 그 트리도 다시 해시하며, 루트 노드의 해시를 봉인 (seal) 이라 부릅니다. 봉인 하나가 SSV 의 모든 바이트를 포괄합니다. SSV 는 APFS 스냅숏을 써서, 업데이트가 실패하면 다시 설치하지 않고 이전 시스템 버전으로 돌아갈 수 있습니다. 서명과 무결성 보호 전반은 [서명·공증·무결성 보호](../protection/codesign-notarization-sip.md)에서, 데이터 볼륨 암호화는 [파일볼트](../protection/filevault/index.md)에서 다룹니다.

## 구조

### 볼륨 그룹을 가리키는 값

볼륨 그룹은 데이터 볼륨 하나와 시스템 볼륨 하나로 이루어지고 운영체제는 둘을 한 개체처럼 다룹니다. 화면에도 디스크 하나로 보이고, 두 볼륨이 암호화 상태를 함께 써서 암호화돼 있으면 같은 암호로 둘 다 잠금이 풀립니다[4].

디스크에서는 볼륨 슈퍼블록 (`apfs_superblock_t`) 의 값 몇 개로 볼륨 그룹을 알아봅니다. 아래 오프셋은 볼륨 슈퍼블록 시작 기준입니다[2].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 32 | 4 | 시그니처 "APSB" | 볼륨 슈퍼블록 표시 |
| 964 | 2 | `apfs_role` | 볼륨 역할 (아래 표) |
| 1008 | 16 | `apfs_volume_group_id` | 볼륨이 속한 볼륨 그룹의 UUID |

`apfs_volume_group_id` 는 macOS 10.15 에서 추가된 필드입니다. 볼륨이 그룹에 속하지 않으면 값이 0 이고 선택 기능 플래그 `apfs_features` 에 `APFS_FEATURE_VOLGRP_SYSTEM_INO_SPACE` (0x00000010) 가 없어야 하며, 그룹에 속하면 플래그가 켜지고 값이 0 이 아닙니다. 이 플래그는 시스템 볼륨과 데이터 볼륨을 사용자에게 보이는 볼륨 하나로 마운트하는 기능이고, 짝을 이루는 두 볼륨의 `apfs_volume_group_id` 값이 같습니다[3]. `apfs_features` 의 오프셋은 [컨테이너와 볼륨](apfs/container-volume.md)의 볼륨 슈퍼블록 표에 있습니다.

봉인한 볼륨에는 호환성 플래그 `APFS_INCOMPAT_SEALED_VOLUME` (0x00000020) 이 켜지고, 이 플래그는 볼륨을 수정할 수 없다는 뜻입니다[3].

### 볼륨 역할

한 볼륨의 역할은 하나를 넘지 않습니다. 상위 역할은 `APFS_VOLUME_ENUM_SHIFT` = 6 을 쓴 시프트 식으로 정의되어서[3], 아래 표의 16진 값 가운데 0x0040 이상은 그 식으로 계산한 값입니다.

| 상수 | 값 | 뜻 |
|---|---|---|
| `APFS_VOL_ROLE_NONE` | 0x0000 | 역할 없음 |
| `APFS_VOL_ROLE_SYSTEM` | 0x0001 | 시스템 루트. 보통 `/` 에 마운트하고, iOS 와 macOS 10.15 이후에는 읽기 전용으로 마운트 |
| `APFS_VOL_ROLE_USER` | 0x0002 | 사용자 홈 디렉터리 |
| `APFS_VOL_ROLE_RECOVERY` | 0x0004 | 복구 시스템. HFS+ 의 복구 파티션과 같은 용도 |
| `APFS_VOL_ROLE_VM` | 0x0008 | 가상 메모리 스왑. `/var/vm` 에 마운트 |
| `APFS_VOL_ROLE_PREBOOT` | 0x0010 | 암호화된 볼륨에서 부팅하는 데 필요한 파일 |
| `APFS_VOL_ROLE_INSTALLER` | 0x0020 | OS 설치 프로그램용. 설치 중 로그를 기록 |
| `APFS_VOL_ROLE_DATA` | 1<<6 = 0x0040 | 바뀌는 데이터(사용자 데이터와 바뀌는 시스템 데이터). iOS·macOS 10.15 이후만 |
| `APFS_VOL_ROLE_BASEBAND` | 2<<6 = 0x0080 | 무선 펌웨어. iOS 전용 |
| `APFS_VOL_ROLE_UPDATE` | 3<<6 = 0x00C0 | 소프트웨어 업데이트. iOS 전용 |
| `APFS_VOL_ROLE_XART` | 4<<6 = 0x0100 | 보안 사용자 데이터 접근 관리. iOS 전용 |
| `APFS_VOL_ROLE_HARDWARE` | 5<<6 = 0x0140 | 펌웨어 데이터. iOS 전용 |
| `APFS_VOL_ROLE_BACKUP` | 6<<6 = 0x0180 | 타임 머신 백업. macOS 전용 |
| `APFS_VOL_ROLE_RESERVED_7` | 7<<6 = 0x01C0 | 예약 (본문 정의 이름은 `APFS_VOL_ROLE_SIDECAR`) |
| `APFS_VOL_ROLE_ENTERPRISE` | 9<<6 = 0x0240 | 기업 관리 데이터 |
| `APFS_VOL_ROLE_PRELOGIN` | 11<<6 = 0x02C0 | 로그인 전 시스템 데이터. macOS 전용. 로그인 화면까지 부팅한 뒤 사용자 암호로 암호화 볼륨을 마운트하게 해 줌 |

하위 6비트 역할과 DATA·BASEBAND 는 모든 macOS·iOS 버전이 지원하고, 나머지 상위 10비트 역할은 macOS 10.15·iOS 13 이후만 지원합니다. 타임 머신 백업 볼륨은 [타임 머신](../../02-artifacts/filesystem/time-machine/index.md)에서 다룹니다.

### inode 번호 공간

`APFS_FEATURE_VOLGRP_SYSTEM_INO_SPACE` 가 켜진 두 볼륨은 inode 번호를 나눠 씁니다. 역할이 DATA 인 볼륨은 `UNIFIED_ID_SPACE_MARK` (0x0800000000000000) 보다 작은 번호를 쓰고, 역할이 SYSTEM 인 볼륨은 그 이상을 씁니다. 두 볼륨 모두 처음 16개 번호는 예약해 둡니다.

| 상수 | 값 | 뜻 |
|---|---|---|
| `ROOT_DIR_INO_NUM` | 2 | 루트 디렉터리 |
| `PRIV_DIR_INO_NUM` | 3 | 비공개 디렉터리 |
| `SNAP_DIR_INO_NUM` | 6 | 스냅숏 디렉터리 |
| `MIN_USER_INO_NUM` | 16 | 사용자 파일이 쓰는 첫 번호 |

그래서 시스템 볼륨의 루트 디렉터리 inode 번호는 `ROOT_DIR_INO_NUM` 에 `UNIFIED_ID_SPACE_MARK` 를 더한 0x0800000000000002 입니다. 도구 출력에서 0x08 로 시작하는 큰 inode 번호를 보면 시스템 볼륨 쪽 객체라고 판단할 수 있습니다.

### 펌링크

펌링크는 심볼릭 링크와 비슷한 새 파일 시스템 객체이고, 심볼릭 링크와 달리 경로를 앞뒤 양방향으로 일관되게 바꿀 수 있습니다[4]. 펌링크는 시스템 볼륨의 디렉터리에서 데이터 볼륨의 디렉터리로 가는 통로이고, 원본 하나에 대상 하나가 짝을 이루며 볼륨 그룹 경계를 넘지 못합니다. 설치 프로그램이 설치할 때 시스템 볼륨에 항목을 만들고 데이터 볼륨의 해당 위치를 가리키게 해서 하나의 디렉터리 계층을 이루고, 사용자와 앱은 이 연결을 알아채지 못합니다. 특정 디렉터리(예: Applications)에 있어야만 하는 앱도 위에서 아래로 찾든 아래에서 위로 거슬러 올라가든 같은 경로를 얻습니다.

두 볼륨을 잇는 확장 속성 이름은 둘입니다[3].

| 상수 | 이름 | 값 |
|---|---|---|
| `FIRMLINK_EA_NAME` | `com.apple.fs.firmlink` | 펌링크의 대상 파일 |
| `SYMLINK_EA_NAME` | `com.apple.fs.symlink` | 심볼릭 링크가 가리키는 데이터 볼륨 위의 대상 파일 |

펌링크를 표시하는 inode 플래그, 펌링크 목록을 담은 파일의 위치, 데이터 볼륨의 마운트 위치, 펌링크로 이어진 디렉터리 목록은 명세에 나오지 않으므로 실제 데이터로 확인해야 합니다.

## 읽는 법

아래 헥스는 명세로 만든 예시이고, 실제 디스크에서 나온 값이 아닙니다. `NN` 은 값이 들어갈 자리를 뜻합니다.

```text
볼륨 슈퍼블록 (블록 시작 기준)
오프셋   00 01 02 03 ...
0020     41 50 53 42          "APSB" 시그니처 (오프셋 32)
...
03C4     NN NN                apfs_role (오프셋 964, 2바이트)
...
03F0     NN NN NN NN NN NN NN NN NN NN NN NN NN NN NN NN
                              apfs_volume_group_id (오프셋 1008, 16바이트)
```

볼륨 그룹을 확인하는 순서는 다음과 같습니다.

1. 컨테이너에서 볼륨 슈퍼블록을 모두 찾고, 오프셋 32 에 "APSB" 가 있는지 확인합니다. 컨테이너를 찾는 법은 [파티션 구조](gpt-partitions.md)에서, 컨테이너 안에서 볼륨을 따라가는 법은 [APFS 구조](apfs/index.md)에서 다룹니다.
2. 오프셋 964 의 `apfs_role` 을 위 역할 표와 맞춰 SYSTEM(0x0001) 과 DATA(0x0040) 볼륨을 고릅니다.
3. 두 볼륨의 오프셋 1008 `apfs_volume_group_id` 가 0 이 아니고 서로 같은지 확인합니다. 같으면 한 볼륨 그룹입니다.
4. `apfs_features` 에 `APFS_FEATURE_VOLGRP_SYSTEM_INO_SPACE` 가 켜져 있는지 보고, macOS 11 이후 이미지라면 시스템 볼륨에 `APFS_INCOMPAT_SEALED_VOLUME` 이 켜져 있는지도 봅니다.
5. 파일 목록을 읽을 때 inode 번호가 `UNIFIED_ID_SPACE_MARK` 이상이면 시스템 볼륨, 아래면 데이터 볼륨 객체로 나눕니다.

두 볼륨 모두 APFS 라서 시각 값은 1970-01-01 00:00:00 UTC 부터 센 나노초를 64비트 정수로 적고 윤초는 셈에 넣지 않습니다. 이 정수의 부호는 명세가 `uint64_t` 로[3], libyal 문서가 부호 있는 정수로[2] 적어 자료끼리 다릅니다. 변환하는 법은 [맥의 시각 값](../value-decoding/mac-time-values.md)에서 다룹니다.

## 포렌식에서 중요한 점

시동 디스크 이미지에는 볼륨이 적어도 둘 들어 있고, 분석 도구가 두 볼륨을 합쳐 한 트리로 보여 주는지는 도구마다 다릅니다. 그래서 처리한 볼륨 목록에 역할이 DATA 인 볼륨이 들어 있는지 먼저 확인합니다. 시스템 볼륨만 열면 사용자 데이터가 하나도 없는 것처럼 보이고, 데이터 볼륨만 열면 라이브 시스템에서 보던 경로와 모양이 달라 보입니다. 펌링크가 시스템 볼륨의 항목을 데이터 볼륨의 해당 위치로 이어 주기 때문에, 라이브 대응에서 적은 경로가 이미지에서는 데이터 볼륨의 다른 위치에 있을 수 있습니다. 라이브 대응과 이미지 분석 결과를 맞출 때는 [라이브 대응](../../03-techniques/process-acquisition/live-response/index.md)의 기록과 볼륨별 경로를 함께 적어 둡니다.

지운 파일을 찾는 곳도 대부분 데이터 볼륨입니다. 읽기 전용 시스템 볼륨에는 사용자가 파일을 저장할 수 없어서, 사용자 활동에서 생긴 삭제 흔적은 데이터 볼륨의 빈 영역과 메타데이터에서 찾습니다. 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.

macOS 11 이후 시스템 볼륨은 APFS 스냅숏 위에서 돌아가고 업데이트가 실패하면 이전 시스템 버전으로 돌아갈 수 있어서, 이미지에 시스템 버전이 둘 이상 남아 있을 수 있습니다. 스냅숏끼리 비교하는 법은 [스냅숏과 백업 비교](../../03-techniques/analysis/snapshot-diff.md)에서 다룹니다. macOS 10.15 에서는 두 볼륨이 암호화 상태를 함께 써서 같은 암호로 둘 다 풀리지만[4], macOS 11 이후에는 시스템 볼륨을 암호화하지 않고 데이터 볼륨만 사용자 비밀로 암호화하므로[1] 암호를 풀어야 하는 쪽은 데이터 볼륨입니다. 암호화된 이미지를 다루는 법은 [암호화된 증거 다루기](../../03-techniques/analysis/encrypted-evidence/index.md)에서 다룹니다.

## 함정

Finder 에 보이는 이름 "Macintosh HD" 는 두 볼륨을 함께 가리켜서, 보고서에는 볼륨 이름과 함께 `apfs_role` 값이나 볼륨 UUID 를 적어 어느 볼륨인지 밝힙니다. 볼륨 이름은 사용자가 바꿀 수 있으므로, 이름에 " - Data" 가 붙어 있는지로 역할을 판단하지 않고 `apfs_role` 로 판단합니다.

펌링크와 심볼릭 링크는 둘 다 다른 곳을 가리키지만 확장 속성 이름이 달라서, `com.apple.fs.firmlink` 와 `com.apple.fs.symlink` 를 섞어 읽지 않습니다. 펌링크 목록 파일이나 데이터 볼륨 마운트 위치처럼 이 페이지에 적지 않은 경로는 사건마다 이미지에서 직접 확인한 뒤 씁니다.

`APFS_VOL_ROLE_RECOVERY` 볼륨은 HFS+ 시절 복구 파티션과 같은 용도라서, 오래된 맥에서 온 이미지라면 같은 용도의 영역이 APFS 볼륨이 아니라 별도 파티션일 수 있습니다. 파티션 유형은 [파티션 구조](gpt-partitions.md), HFS+ 볼륨은 [HFS+ 구조](hfs-plus.md)에서 다룹니다. 펌링크를 만들거나 볼륨 그룹을 바꿀 때 통합 로그에 어떤 서브시스템으로 남는지는 실제 통합 로그에서 확인해야 합니다.

## 도구

| 도구 | 쓰임 |
|---|---|
| Apple File System Reference (명세) | 볼륨 역할, 기능 플래그, inode 번호 공간, 펌링크 확장 속성 이름의 기준 |
| libyal libfsapfs 와 그 APFS 문서 | 볼륨 슈퍼블록 필드 오프셋을 확인하고 APFS 볼륨을 읽을 때 씁니다 |
| 헥스 편집기 | 위 읽는 법 순서대로 `apfs_role` 과 `apfs_volume_group_id` 를 직접 확인합니다 |

도구 이름은 예로 든 것이고, 도구가 볼륨을 합쳐 보여 주는지 따로 보여 주는지는 [도구 검증](../../03-techniques/reporting/tool-validation.md) 방식으로 확인합니다.

## 참고 문헌

1. Apple Platform Security — Signed system volume security, https://support.apple.com/guide/security/signed-system-volume-security-secd698747c9/web
2. libyal libfsapfs — Apple File System (APFS), https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
3. Apple, Apple File System Reference (2020-06-22 판), https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
4. Apple WWDC19 Session 710 — What's New in Apple File Systems, https://developer.apple.com/videos/play/wwdc2019/710/
5. Apple Support — About the read-only system volume in macOS Catalina or later (HT210650), https://support.apple.com/en-us/HT210650
