---
title: "A/B 슬롯"
parent: "파티션과 저장 영역"
grand_parent: "기반 · 저장 구조"
nav_order: 30
---

# A/B 슬롯 (A/B Slots)

A/B 업데이트를 쓰는 기기는 파티션을 슬롯 A 와 슬롯 B 두 벌로 두고 쓰지 않는 슬롯에 업데이트를 쓰며, Virtual A/B 기기는 부트로더가 쓰는 파티션만 두 벌 두고 나머지는 스냅샷으로 업데이트하기 때문에, 이미지를 볼 때는 어느 슬롯이 현재였는지와 업데이트가 끝났는지를 먼저 확인합니다.

## 이 구조와 관련된 아티팩트

두 슬롯에는 서로 다른 빌드가 들어 있을 수 있어서, [기기 정보와 빌드](../../../02-artifacts/system-account/device-build.md)의 빌드 값을 읽을 때는 어느 슬롯에서 읽었는지를 함께 적습니다. Virtual A/B 의 병합이 끝나지 않았으면 부트로더가 metadata·userdata 와 병합 상태를 담은 파티션을 지우는 명령을 거부하고, 이 점은 [초기화 흔적](../../../02-artifacts/system-account/factory-reset.md)을 해석할 때 참고합니다. 업데이트 흔적은 metadata 파티션과 userdata 에도 남고, 두 파티션의 역할은 [파티션 배치](partition-layout.md)에 있습니다.

## 구조

### A/B 업데이트

A/B 업데이트 (끊김 없는 업데이트, Seamless Updates)는 OTA 업데이트 중에도 부팅할 수 있는 시스템을 디스크에 남겨 두는 방식입니다. 두 벌의 파티션 묶음을 슬롯 A, 슬롯 B 라고 부르고, 실행 중인 시스템은 현재 슬롯에서 돌며 쓰지 않는 슬롯은 평소에 건드리지 않습니다. 백그라운드 데몬인 update_engine 이 현재 슬롯에서 읽고 쓰지 않는 슬롯에 업데이트를 씁니다.

두 벌짜리 파티션은 이름 끝에 슬롯 접미사가 붙습니다.

```
boot_a    boot_b
system_a  system_b
vendor_a  vendor_b
```

빌드에서는 `AB_OTA_UPDATER := true` 로 A/B 를 켜고 `AB_OTA_PARTITIONS := boot system vendor ...` 로 두 벌 둘 파티션을 정합니다. A/B 기기는 별도의 recovery·cache 파티션 없이 동작하고, OTA 패키지를 cache 에 두지 않습니다. 현재 슬롯이 쓰는 파티션은 한 벌뿐인 파티션까지 포함해 OTA 로 업데이트하지 않습니다[1]. userdata·misc·metadata 도 한 벌뿐인 파티션이라 여기에 들어가는 것으로 보입니다.

### 슬롯 상태

슬롯마다 세 가지 상태가 있습니다.

| 상태 | 뜻 |
|---|---|
| bootable | 슬롯에 부팅할 수 있는 시스템이 있음 |
| active | 다음 부팅에 쓸 슬롯 |
| successful | 사용자 공간이 표시한 상태로, 이 슬롯이 부팅·실행·업데이트까지 됨 |

update_engine 은 boot_control HAL (`boot_control.h`)로 부트로더에 지시하고, 이때 쓰는 함수는 `markBootSuccessful()`, `setSlotAsUnbootable()`, `setActiveBootSlot()` 입니다. 부트로더는 슬롯마다 재시도 횟수와 unbootable 표시를 관리합니다.

### 현재 슬롯을 알려 주는 값

현재 슬롯은 속성 `ro.boot.slot_suffix` 의 값 (`_a` 또는 `_b`)으로 알 수 있습니다. 이 값은 커널 명령줄의 `androidboot.slot_suffix` 나 장치 트리의 `/firmware/android/slot_suffix` 로 전달되고, fstab 의 `slotselect` 플래그가 붙은 줄은 현재 슬롯의 파티션을 자동으로 마운트합니다. 부트로더 쪽에서는 fastboot 변수 `current-slot` 이 현재 슬롯을 알려 주고, `has-slot:<partition>` 은 그 파티션이 두 벌인지를 알려 줍니다.

### Virtual A/B

Virtual A/B 는 Android 11 에 도입되었고 버전마다 기능이 늘었습니다.

| Android 버전 | 바뀐 점 |
|---|---|
| 11 | Virtual A/B 도입 |
| 12 | Android 전용 COW 형식으로 압축 지원 |
| 13 | 커널 COW 형식과 dm-snapshot 의존을 없앰, XOR 연산 추가, 사용자 공간 스냅샷이 기본 |

Virtual A/B 에는 동적 파티션용 여분 슬롯이 없고, 업데이트는 변경분을 스냅샷에 쓴 뒤 원래 파티션에 병합 (merge)하는 방식으로 진행하며, 두 벌 두는 파티션은 부트로더가 쓰는 파티션뿐입니다. 동적 파티션의 구조는 [동적 파티션 (super)](super-partition.md)에서 다룹니다.

COW 연산에는 Copy, Replace, Zero, XOR (Android 13 이상)가 있고, 전체 OTA 는 Replace·Zero 만 쓰지만 증분 OTA 는 Copy 도 씁니다. 사용자 공간 데몬 snapuserd 가 Android COW 장치를 읽고 쓰며, dm-user 커널 모듈이 I/O 를 snapuserd 로 보냅니다. 병합은 재부팅 뒤 사용자 공간에서 하고, 병합 도중에 재부팅하면 이어서 합니다.

업데이트 흔적이 남는 자리는 다음과 같습니다.

| 흔적 | 위치 |
|---|---|
| 스냅샷 메타데이터 | `/metadata/ota` |
| COW 이미지 | `/data/gsi/ota` 또는 super 의 빈 공간 |
| 병합 상태 | misc 파티션 (libbootloader_message) |

설정 쪽에서는 속성 `ro.virtual_ab.compression.xor.enabled` 와 `ro.virtual_ab.userspace.snapshots.enabled` (Android 13 이상 기본)가 있고, 빌드는 `virtual_ab_ota.mk` 를 상속하며 Android 13 이상의 압축은 `virtual_ab_ota/vabc_features.mk` 를 씁니다. 압축 방식은 `PRODUCT_VIRTUAL_AB_COMPRESSION_METHOD := lz4` 처럼 정합니다.

## 읽는 법

1. 이미지의 파티션 이름에 `_a`·`_b` 가 붙어 있는지 봅니다. 부트로더가 쓰는 파티션만 두 벌이면 Virtual A/B 일 수 있고, 슬롯 접미사가 없으면 A/B 를 쓰지 않는 기기일 수 있습니다.
2. 수집 기록에 `ro.boot.slot_suffix` 값이 있으면 현재 슬롯을 그 값으로 정합니다. 값이 없으면 어느 슬롯을 분석했는지를 보고서에 "확인 못 함"으로 남깁니다.
3. Virtual A/B 기기라면 `/metadata/ota` 와 `/data/gsi/ota` 에 스냅샷 흔적이 있는지 보고, 병합 상태는 misc 파티션에 있다는 점을 기억해 둡니다.
4. 두 슬롯의 빌드가 다르면 현재 슬롯의 빌드를 기준으로 삼고, 다른 슬롯은 업데이트 전후의 비교 자료로 둡니다.

Android 16·One UI 8.5 기기의 설정에는 settings global 의 `ota_disable_automatic_update`, `galaxy_system_update`, `galaxy_system_update_use_wifi_only` 와 settings system 의 `IsFotaUpgrade` 같은 업데이트 관련 키가 있습니다. 이 키들은 슬롯 상태를 나타내는 값이 아니고, 값의 뜻은 실제 기기에서 확인해야 합니다. 설정 값 읽는 법은 [설정 값](../../../02-artifacts/system-account/settings.md)에서 다룹니다.

## 포렌식에서 중요한 점

`/metadata/ota` 나 `/data/gsi/ota` 에 스냅샷 흔적이 남아 있으면 최근 OTA 가 진행 중이었거나 병합이 끝나지 않았을 가능성이 있습니다. 파일 이름과 시각을 읽는 기준은 실제 기기에서 확인해야 합니다. 병합이 끝나지 않은 상태에서 만든 이미지는 원래 파티션만 읽으면 업데이트가 반영되지 않은 내용일 수 있습니다. 두 해석 모두 추정이므로 보고서에는 추정이라고 밝혀 적습니다.

병합 상태가 MERGING 이나 SNAPSHOTTED 인 동안 부트로더가 metadata·userdata 와 병합 상태를 담은 파티션의 지우기 (erase·wipe)를 거부해야 하고, MERGING 상태에서는 현재 슬롯을 바꾸는 명령도 거부합니다[4]. 이 동작은 부트로더 단계의 지우기에 관한 것이라서 설정 메뉴의 초기화까지 막는다고 볼 근거는 없습니다. 초기화 시도와 업데이트 시점이 겹치는 사건에서는 이 동작을 함께 적어 두고, 초기화 흔적 자체는 [초기화 흔적](../../../02-artifacts/system-account/factory-reset.md)에서 확인합니다.

successful 상태는 사용자 공간이 슬롯을 표시한 결과이고 사용자가 기기를 조작했다는 기록은 아닙니다. 슬롯 상태와 병합 상태는 기기를 다시 켜거나 업데이트가 진행되면 바뀌기 때문에, 수집 중에는 슬롯 상태를 바꾸는 조작을 하지 않고 수집 전후의 상태를 기록합니다. 수집 절차는 [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md)에서 다룹니다.

## 함정

`ro.virtual_ab.enabled` 와 `ro.build.ab_update` 속성은 참고 문헌의 AOSP 문서에 나오지 않는 값이라, A/B 나 Virtual A/B 여부를 판단하는 근거로 쓰지 않습니다. 삼성 기기가 어느 방식을 쓰는지는 실제 기기에서 확인해야 합니다.

| 항목 | AOSP 문서 | 삼성 갤럭시 (One UI) |
|---|---|---|
| A/B·Virtual A/B·비 A/B 가운데 무엇을 쓰나 | 기기마다 다름 | 실제 기기에서 확인 |
| Android 16 기기의 슬롯 여부 | — | 실제 기기에서 확인 |
| 슬롯 접미사 | `_a`·`_b` | 실제 기기에서 확인 |

## 도구

기기 안의 진단 도구 snapshotctl 은 `dump` 명령으로 Virtual A/B 스냅샷 상태를 보여 주고, 부트로더 쪽에서는 fastboot 변수 `current-slot` 으로 현재 슬롯을 확인합니다. 슬롯을 바꾸거나 업데이트 상태를 고치는 명령은 이 핸드북에서 다루지 않습니다.

## 참고 문헌

1. A/B (seamless) system updates — AOSP — https://source.android.com/docs/core/ota/ab
2. Implement A/B updates — AOSP — https://source.android.com/docs/core/ota/ab/ab_implement
3. Virtual A/B overview — AOSP — https://source.android.com/docs/core/ota/virtual_ab
4. Implement Virtual A/B — AOSP — https://source.android.com/docs/core/ota/virtual_ab/implement
