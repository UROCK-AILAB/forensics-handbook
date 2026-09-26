---
title: "파티션 배치"
parent: "파티션과 저장 영역"
grand_parent: "기반 · 저장 구조"
nav_order: 10
---

# 파티션 배치 (boot·system·vendor·userdata)

Android 기기의 저장소는 하는 일이 정해진 여러 파티션으로 나뉘고, 사용자 흔적은 대부분 userdata 에 있지만 그 userdata 를 풀 키는 metadata 파티션에, 기기의 빌드와 운영체제 구성은 system·vendor 쪽 파티션에 있어서 셋을 함께 알아야 합니다.

## 이 배치와 관련된 아티팩트

사용자가 설치한 앱과 그 데이터는 userdata 파티션에 있습니다. 앱 데이터 폴더와 공용 저장 공간의 아티팩트는 모두 여기서 나오며, 폴더 구조는 [앱 데이터 폴더 구조](../app-data-layout.md)와 [공용 저장 공간](../shared-storage.md)에서 다룹니다. 기기가 어떤 빌드로 동작했는지는 system·vendor 쪽 이미지와 관련이 있고, 빌드 정보를 읽는 법은 [기기 정보와 빌드](../../../02-artifacts/system-account/device-build.md)에 있습니다.

## 구조

### 파티션 세 묶음

파티션은 system 쪽, vendor 쪽, 업데이트하지 않는 파티션의 세 묶음으로 나뉩니다[1]. system 쪽은 한 묶음으로, vendor 쪽은 또 다른 한 묶음으로 업데이트하도록 권장하고, userdata 처럼 업데이트하지 않는 파티션은 OTA 가 건드리지 않습니다. system·vendor·product 같은 파티션은 Android 10 이후 기기에서 super 파티션 안의 논리 파티션으로 들어갈 수 있는데, 그 구조는 [동적 파티션 (super)](super-partition.md)에서 다룹니다. 이름 끝에 `_a`·`_b` 가 붙은 두 벌짜리 파티션은 [A/B 슬롯](ab-slots.md)에서 설명합니다.

**system 쪽 파티션**

| 파티션 | 담는 것 |
|---|---|
| boot | GKI (Generic Kernel Image). Android 12 이하로 출시한 기기는 generic ramdisk 도 여기에 둡니다 |
| init_boot | generic ramdisk. Android 13 이상에서 씁니다 |
| system | OEM 제품용 system 이미지 |
| system_ext | system 을 확장하는 시스템 자원과 모듈 |
| system_dlkm | GKI 커널 모듈 |
| product | 다른 파티션에 묶이지 않는 제품별 모듈 |
| pvmfw | 보호된 가상 머신 (protected VM)에서 가장 먼저 실행되는 펌웨어 |
| generic_bootloader | 공통 부트로더 |

generic ramdisk 는 Android 12 이하로 출시한 기기에서는 boot 에 있고, init_boot 가 있는 Android 13 이상 기기에서는 init_boot 로 옮겨 갑니다.

**vendor 쪽 파티션**

| 파티션 | 담는 것 |
|---|---|
| vendor_boot | 제조사 부팅 코드 |
| recovery | OTA 업데이트 중에 부팅하는 recovery 이미지 |
| misc | recovery 가 쓰는 영역으로 크기는 4KB 이상입니다 |
| vbmeta | 모든 파티션의 검증 부팅 (Verified Boot) 정보 |
| vendor | AOSP 로 배포하기 어려운 제조사 전용 바이너리 |
| vendor_dlkm | 제조사 커널 모듈. vendor 를 건드리지 않고 모듈만 업데이트할 때 씁니다 |
| odm | ODM 이 SoC BSP 에 더한 맞춤 |
| odm_dlkm | ODM 커널 모듈 |
| radio | 라디오 소프트웨어. 전용 파티션에 둘 때만 있습니다 |

**업데이트하지 않는 파티션**

| 파티션 | 담는 것 |
|---|---|
| cache | 임시 데이터. 끊김 없는 업데이트 (A/B)를 쓰는 기기에는 없어도 됩니다 |
| userdata | 사용자가 설치한 앱과 데이터, 사용자 맞춤 데이터 |
| metadata | 메타데이터 암호화를 쓸 때 그 키. 크기는 16MB 이상입니다 |

vbmeta 가 담는 검증 부팅 정보가 무엇을 확인하는지는 [부트로더와 검증 부팅](../../security-model/verified-boot.md)에서 다룹니다.

### metadata 파티션과 userdata 암호화

메타데이터 암호화 (Metadata Encryption)는 Android 9 에서 지원을 시작했고, Android 11 이상으로 출시한 기기는 내부 저장소에서 반드시 켜야 합니다. 이 암호화가 가리는 것은 폴더 구조와 파일 크기, 권한, 생성·수정 시각이고, 파일 내용과 이름은 파일 단위 암호화 (File-Based Encryption, FBE) 키로 따로 암호화합니다. 두 암호화가 어떻게 겹치는지는 [저장 공간 암호화](../encryption/index.md)에서 다룹니다.

키의 위치는 userdata 의 fstab 줄에 `keydirectory=/metadata/vold/metadata_encryption` 으로 적혀 있습니다. 키는 KeyMint (예전 이름 Keymaster)가 보호하고 KeyMint 는 검증 부팅이 보호합니다. 커널에서는 dm-default-key 모듈이 이 암호화를 맡고, 기본 알고리즘은 AES-256-XTS 이지만 AES 가속이 없는 기기는 Adiantum 을 쓸 수 있습니다. fstab 에서는 `metadata_encryption=` 플래그로 설정합니다.

metadata 파티션의 fstab 예는 다음과 같습니다[3].

```
/dev/block/by-name/metadata /metadata ext4 noatime,nosuid,nodev,discard,sync wait,formattable,first_stage_mount,check
```

### 파일 시스템

AOSP 가 보안 패치를 자주 내는 파일 시스템은 ext4, f2fs, exfat (커널 5.10 이상), vfat, EROFS, incfs, fuse 이고, sdcardfs 는 커널 4.14 이하만 지원하며 폐기되었습니다. Android 는 커널에 fscrypt (파일 단위 암호화)와 fsverity 지원을 요구하고, Android 13 부터 사용자 공간은 GKI 에 들어간 파일 시스템만 씁니다. 어느 파티션이 어느 파일 시스템인지는 기기마다 다르고, 각 파일 시스템의 구조는 [파일 시스템 (ext4·F2FS)](../filesystems/index.md)에서 다룹니다.

### 장치 경로

물리 파티션의 블록 장치는 위 fstab 예처럼 이름으로 찾을 수 있습니다.

```
/dev/block/by-name/<이름>
```

super 안의 논리 파티션이 어느 장치 경로로 나타나는지는 실제 기기에서 확인합니다.

## 읽는 법

이미지나 수집 보고서에서 파티션 목록을 받으면 먼저 이름을 위의 세 묶음에 나눠 넣습니다. userdata 와 metadata 는 사용자 데이터를 풀 때 짝으로 필요하고, system·vendor 쪽은 빌드를 확인하고 검증 부팅 정보와 대조할 때 봅니다. init_boot 가 있으면 ramdisk 를 boot 와 따로 두는 Android 13 이후 방식이고, 목록에 system·vendor 가 없고 super 만 있으면 동적 파티션을 쓰는 기기입니다. 이름에 `_a`·`_b` 가 붙어 있으면 두 벌 가운데 어느 쪽이 현재 슬롯이었는지를 [A/B 슬롯](ab-slots.md)의 방법으로 확인합니다.

루팅하지 않은 기기에서 adb 일반 권한으로 얻는 출력에도 파티션 배치의 흔적이 보입니다. `dumpsys package` 의 Libraries 목록에는 `/system/framework` 와 `/system_ext/framework` 아래의 jar 경로가 나옵니다.

## 포렌식에서 중요한 점

조사에서 주로 보는 곳은 userdata 입니다. 메타데이터 암호화를 쓰는 기기에서 암호를 풀지 못한 userdata 이미지는 파일 내용과 이름뿐 아니라 폴더 구조, 크기, 시각도 읽을 수 없고, 그래서 지운 파일 복구나 파일 시스템 시각 분석도 복호화가 된 뒤에야 시작할 수 있습니다. 복구 방법은 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.

키가 metadata 파티션에 있으므로[3], metadata 파티션을 잃거나 지우면 userdata 를 풀 수 없을 것으로 보입니다. 문서에 직접 적힌 내용은 아니므로 보고서에는 추정이라고 밝혀 적습니다.

misc 파티션은 recovery 가 쓰는 작은 영역이지만 Virtual A/B 기기에서는 업데이트 병합 상태도 여기에 남습니다. 그 내용은 [A/B 슬롯](ab-slots.md)에서 다룹니다.

## 함정

파티션의 수와 이름은 제조사와 기기마다 다르고, AOSP 문서의 목록은 기준일 뿐 모든 기기에 똑같이 있지는 않습니다. cache 는 A/B 기기에 없을 수 있고, radio 는 전용 파티션을 쓸 때만 있습니다. 동적 파티션을 쓰는 기기에서는 system·vendor 가 파티션 표에 따로 나오지 않으므로 "system 파티션이 없다"고 적기 전에 super 를 확인합니다.

| 항목 | AOSP 문서 | 삼성 갤럭시 (One UI) |
|---|---|---|
| 파티션 묶음과 이름 | 위 표 | 실제 기기에서 확인 |
| 제조사 전용 파티션 (EFS, persist 등) | 문서 범위 밖 | 실제 기기에서 확인 |
| 파티션별 파일 시스템 | 기기마다 다름 | 실제 기기에서 확인 |

## 참고 문헌

1. Partitions overview — AOSP — https://source.android.com/docs/core/architecture/partitions
2. Implement Virtual A/B — AOSP — https://source.android.com/docs/core/ota/virtual_ab/implement
3. Metadata encryption — AOSP — https://source.android.com/docs/security/features/encryption/metadata
4. Android kernel file system support — AOSP — https://source.android.com/docs/core/architecture/android-kernel-file-system-support
