---
title: "동적 파티션"
parent: "파티션과 저장 영역"
grand_parent: "기반 · 저장 구조"
nav_order: 20
---

# 동적 파티션 (super)

## 한 줄 요약

Android 10 이후 기기는 system·vendor·product 같은 파티션을 super 라는 물리 파티션 하나 안에 논리 파티션으로 담고, 각 논리 파티션의 이름과 블록 범위는 super 안의 메타데이터에 적혀 있어서, 이미지에서 system 이나 vendor 를 꺼내 보려면 이 메타데이터부터 읽어야 합니다.

## 이 형식을 쓰는 아티팩트

super 가 담는 논리 파티션에는 사용자가 만든 데이터가 없고, 사용자 흔적은 [파티션 배치](partition-layout.md)에서 설명한 userdata 에 있습니다. super 안의 system·vendor·product 이미지는 기기가 어떤 빌드로 동작했는지 확인할 때 보며, 빌드 정보를 읽는 법은 [기기 정보와 빌드](../../../02-artifacts/system-account/device-build.md)에, 이미지가 바뀌지 않았는지 확인하는 검증 부팅 정보는 [부트로더와 검증 부팅](../../security-model/verified-boot.md)에 있습니다. Virtual A/B 기기에서는 업데이트용 COW 이미지가 super 의 빈 공간에 놓일 수 있어서, 업데이트 흔적을 볼 때도 super 를 함께 봅니다. 그 내용은 [A/B 슬롯](ab-slots.md)에서 다룹니다.

## 구조

### 도입과 구현

동적 파티션 (Dynamic Partitions)은 Android 10 에 도입되었고, AOSP 구현 문서는 "Android 10 으로 출시하는 기기는 super 라는 파티션을 만든다"고 적습니다. AOSP 파티션 개요 문서에는 Android 11 이상 기기가 지원할 수 있다고 적혀 있지만, 이 페이지는 도입 버전을 구현 문서의 Android 10 으로 씁니다.

super 안의 메타데이터에는 동적 파티션마다 이름과 블록 범위가 적혀 있고, 커널은 리눅스 device-mapper 의 dm-linear 모듈로 그 블록 범위를 논리 파티션 하나로 이어 보여 줍니다. A/B 기기에서도 super 는 하나뿐이라서 super_a·super_b 를 따로 두지 않고, 슬롯은 super 안에서 다룹니다.

> 그림 자리: 물리 파티션 super 안에 system·vendor·product 논리 파티션이 블록 범위로 나뉘어 들어 있고, 맨 앞에 메타데이터가 있는 모습

### 동적이 될 수 있는 파티션

| 구분 | 파티션 |
|---|---|
| 동적 파티션이 될 수 있음 | system, vendor, product, system_ext, odm |
| 물리 파티션으로 남음 | 부트로더가 쓰는 파티션 (boot, dtbo, vbmeta 등) |

### 빌드 설정과 fstab

새로 출시하는 기기와 동적 파티션을 나중에 들인 업그레이드 (retrofit) 기기는 설정이 다릅니다.

| 기기 | 설정 |
|---|---|
| Android 10 이상으로 출시 | `PRODUCT_USE_DYNAMIC_PARTITIONS := true`, super 크기는 `BOARD_SUPER_PARTITION_SIZE`, 파티션 묶음은 `BOARD_SUPER_PARTITION_GROUPS` |
| 업그레이드 기기 | 기존 파티션을 이어 쓰고 `PRODUCT_RETROFIT_DYNAMIC_PARTITIONS := true` 와 `BOARD_SUPER_PARTITION_METADATA_DEVICE` 를 씁니다 |

fstab 에서 논리 파티션 줄의 fs_mgr 플래그에는 `logical` 과 `first_stage_mount` 가 있어야 하고, 두 플래그 모두 Android 10 에 도입되었습니다.

### super 메타데이터 형식

메타데이터 형식은 AOSP liblp 의 헤더 `metadata_format.h` 에 정의되어 있습니다. 이 페이지의 상수와 칸 이름은 모두 그 헤더에서 가져왔습니다.

| 상수 | 값 | 뜻 |
|---|---|---|
| `LP_PARTITION_RESERVED_BYTES` | 4096 | super 맨 앞의 예약 영역 크기 |
| `LP_METADATA_GEOMETRY_SIZE` | 4096 | geometry 영역 크기 |
| `LP_METADATA_GEOMETRY_MAGIC` | 0x616c4467 | geometry 를 알아보는 매직 값 |
| `LP_METADATA_HEADER_MAGIC` | 0x414C5030 | 메타데이터 헤더를 알아보는 매직 값 |
| 메타데이터 버전 | MAJOR 10, MINOR 0~2 | 헤더가 정의한 버전 범위 |

geometry 구조 (`LpMetadataGeometry`)의 칸은 다음 순서로 정의되어 있습니다.

```
magic, struct_size, checksum[32], metadata_max_size, metadata_slot_count, logical_block_size
```

파티션 표의 한 줄 (`LpMetadataPartition`)에는 다음 칸이 있습니다. `name` 은 36바이트이고 영숫자와 밑줄만 씁니다. `first_extent_index` 와 `num_extents` 는 extent 목록에서 이 파티션이 쓰는 범위를 가리키고, `group_index` 는 파티션이 속한 묶음을 가리킵니다.

```
name[36], attributes, first_extent_index, num_extents, group_index
```

`attributes` 칸의 비트는 다음과 같습니다.

| 비트 | 이름 | 뜻 (헤더 주석) |
|---|---|---|
| `1<<0` | READONLY | 쓰기 불가 |
| `1<<1` | SLOT_SUFFIXED | 이름에 슬롯 접미사를 붙임 |
| `1<<2` | UPDATED | 스냅샷 기반 업데이트로 만들어지거나 바뀐 파티션 |
| `1<<3` | DISABLED | 비활성 |

extent 가 가리키는 대상은 두 종류이고, LINEAR (0)는 dm-linear 로 super 의 블록 범위를 잇고 ZERO (1)는 dm-zero 로 0 을 채운 범위를 만듭니다.

헤더 주석에 따르면 super 는 맨 앞 4096바이트를 예약해 두고, 그 뒤에 geometry, 예비 geometry, 메타데이터, 예비 메타데이터, 논리 파티션 데이터를 차례로 둡니다. 메타데이터 사본마다 정확한 바이트 오프셋은 `metadata_max_size` 와 `metadata_slot_count` 에 따라 달라지므로 이 페이지에서는 값을 정해 적지 않습니다.

## 읽는 법

이미지에 system·vendor 가 따로 없고 super 만 있으면 동적 파티션을 쓰는 기기이고, 이 판단은 [파티션 배치](partition-layout.md)의 읽는 법과 같습니다. 논리 파티션을 꺼내는 순서는 다음과 같습니다.

1. super 앞부분에서 geometry 매직 값 0x616c4467 을 찾고, geometry 의 `logical_block_size` 와 `metadata_max_size` 를 읽습니다. 매직 값을 바이트 단위로 찾을 때는 저장 바이트 순서를 헤더 정의에 맞춰 확인합니다.
2. 메타데이터 헤더 매직 값 0x414C5030 과 버전 (MAJOR 10, MINOR 0~2)을 확인합니다. 버전이 이 범위를 벗어나면 도구가 형식을 잘못 읽을 수 있습니다.
3. 파티션 표에서 이름과 `attributes` 를 읽고, `first_extent_index` 와 `num_extents` 로 그 파티션의 extent 를 찾습니다.
4. LINEAR extent 가 가리키는 super 의 블록 범위를 순서대로 이어 붙이고 ZERO extent 는 0 으로 채워서 논리 파티션 이미지를 만듭니다.
5. 만든 이미지의 파일 시스템을 [파일 시스템 (ext4·F2FS)](../filesystems/index.md)의 방법으로 읽습니다.

## 포렌식에서 중요한 점

A/B 기기에서는 super 하나 안에 이름에 슬롯 접미사가 붙은 논리 파티션이 함께 있을 수 있고, `SLOT_SUFFIXED` 비트가 그 표시입니다. 이때 어느 쪽이 기기가 실제로 부팅한 슬롯이었는지는 super 메타데이터만으로 정하지 않고 [A/B 슬롯](ab-slots.md)의 방법으로 확인합니다.

`UPDATED` 비트는 헤더 주석대로 스냅샷 기반 업데이트로 만들어지거나 바뀐 파티션이라는 표시이고, 이 비트로 업데이트 시각이나 업데이트 내용까지 알 수 있는지는 확인하지 못했습니다. 보고서에는 "이 논리 파티션에 UPDATED 표시가 있다" 처럼 기록이 말하는 만큼만 적습니다.

Virtual A/B 기기는 COW 이미지를 super 의 빈 공간에 둘 수 있어서, 메타데이터가 가리키지 않는 영역도 비어 있다고 단정하지 않습니다. geometry 에는 `checksum` 칸이 있어서 geometry 가 손상되었는지 확인할 때 씁니다. 손상된 메타데이터로 만든 논리 파티션 이미지는 블록이 엉뚱하게 이어질 수 있고, 그 위에서 읽은 파일 시스템 결과도 믿기 어렵습니다.

## 함정

업그레이드 기기는 새 super 파티션 대신 기존 파티션을 이어 쓰기 때문에, 파티션 표에서 super 라는 이름을 찾지 못했다고 곧바로 동적 파티션이 아니라고 적지 않습니다. 논리 파티션이 실행 중인 기기에서 어느 장치 경로로 나타나는지는 이 조사에서 확인하지 못했고, 물리 파티션 경로는 [파티션 배치](partition-layout.md)에 있습니다.

| 항목 | AOSP 문서 | 삼성 갤럭시 (One UI) |
|---|---|---|
| super 파티션 사용 | Android 10 이상으로 출시한 기기는 만듦 | 확인 못 함 |
| super 안의 논리 파티션 목록 | system, vendor, product, system_ext, odm 가운데 | 확인 못 함 |

SM-S937N (Android 16, One UI 8.5)의 기기 관찰 메모에는 파티션 목록이나 super 정보가 없어서, 이 기기의 super 구성은 이 페이지에서 말하지 않습니다.

## 도구

구조의 기준은 AOSP liblp 의 `metadata_format.h` 입니다. 이 조사에서 super 를 풀어 주는 도구의 이름과 동작은 문서로 확인하지 못했고, 어떤 도구를 쓰든 파티션 이름, extent 수, 속성 비트를 헤더 정의에 따라 직접 읽은 값과 대조합니다. 대조하는 방법은 [도구 검증](../../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 참고 문헌

1. Implement dynamic partitions — AOSP — https://source.android.com/docs/core/ota/dynamic_partitions/implement
2. liblp metadata_format.h — AOSP system/core — https://android.googlesource.com/platform/system/core/+/refs/heads/main/fs_mgr/liblp/include/liblp/metadata_format.h
3. Partitions overview — AOSP — https://source.android.com/docs/core/architecture/partitions
4. Implement Virtual A/B — AOSP — https://source.android.com/docs/core/ota/virtual_ab/implement
