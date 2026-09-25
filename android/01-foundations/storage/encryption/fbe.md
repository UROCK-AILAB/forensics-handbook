---
title: "파일 단위 암호화"
parent: "저장 공간 암호화"
grand_parent: "기반 · 저장 구조"
nav_order: 90
---

# 파일 단위 암호화 (FBE)

## 한 줄 요약

파일 단위 암호화 (File-Based Encryption, FBE) 는 파일마다 다른 키로 파일 내용과 파일 이름을 암호화하는 방식이고, Android 7.0 부터 지원하며 Android 10 이상으로 나오는 기기는 모두 이 방식을 써야 합니다 [1].

## 이 암호화가 걸리는 곳

FBE 에서는 키를 따로따로 풀 수 있어서, 사용자가 잠금을 풀기 전에도 일부 데이터를 쓰는 Direct Boot 가 가능합니다 [1][3]. 사용자마다 잠금 해제 뒤에만 열리는 CE 영역과 부팅 직후에도 열리는 DE 영역이 나뉘는데, 어느 폴더가 어느 쪽인지는 [CE 영역과 DE 영역](ce-de-storage.md) 페이지에 정리했습니다. 예전 방식인 전체 디스크 암호화 (FDE) 와 어떻게 다른지는 허브인 [저장 공간 암호화](index.md) 페이지에 있습니다.

FBE 가 가리는 범위는 파일 내용과 파일 이름까지이고, 디렉터리 구조와 파일 크기, 권한, 생성·수정 시각은 메타데이터 암호화 (Metadata Encryption) 가 따로 맡습니다 [2].

| 보호 대상 | 맡는 기능 | 도입 |
|---|---|---|
| 파일 내용 | FBE | Android 7.0 [1] |
| 파일 이름 | FBE | Android 7.0 [1] |
| 디렉터리 구조, 파일 크기, 권한, 생성·수정 시각 | 메타데이터 암호화 | Android 9 [2][3] |

## 구조

### 커널 쪽 구현 (fscrypt)

커널에서 FBE 를 맡는 부분은 fscrypt 이고, 암호화 정책에는 v1 과 v2 가 있습니다. v1 은 폐기(deprecated) 되었고, v2 는 키를 유도할 때 HKDF-SHA512 를 씁니다. Android 11 이상으로 나오는 기기의 CDD 요건은 v2 로만 맞출 수 있어서 이런 기기의 기본값은 v2 이고, Android 10 이하로 나온 기기는 따로 적지 않으면 v1 을 씁니다 [1]. ext4·F2FS 자체의 구조는 [파일 시스템](../filesystems/index.md) 페이지에서 다룹니다.

### 알고리즘

| 대상 | 쓸 수 있는 알고리즘 | 참고 |
|---|---|---|
| 파일 내용 | `aes-256-xts`(기본), `adiantum` | [1] |
| 파일 이름 | `aes-256-cts`, `aes-256-heh`, `adiantum`, `aes-256-hctr2` | 암호 가속 명령이 있는 기기에는 `aes-256-hctr2` 를 권합니다(Android 14 이상) [1] |
| 메타데이터 | AES-256-XTS(기본), AES 가속이 없는 기기는 Adiantum | [2] |

### fstab 설정

기기가 FBE 를 어떻게 쓸지는 fstab 의 `fileencryption` 항목에서 정하고, 형식은 아래와 같습니다 [1].

```
fileencryption=contents_encryption_mode[:filenames_encryption_mode[:flags]]

예)
fileencryption=aes-256-xts
fileencryption=aes-256-xts:aes-256-cts:inlinecrypt_optimized
```

플래그 자리에는 `v1`, `v2`, `inlinecrypt_optimized`, `emmc_optimized`, `wrappedkey`(또는 `wrappedkey_v0`) 를 쓸 수 있습니다 [1]. 라이브 기기나 펌웨어에서 이 줄을 볼 수 있다면 파일 내용과 이름에 어떤 알고리즘을 썼는지, 정책 버전이 무엇인지를 여기서 바로 읽습니다.

### 키가 놓이는 자리

| 키 | 위치 | 보호 |
|---|---|---|
| 시스템 DE 키 | `/data/unencrypted` | 이 폴더 자체는 암호화하지 않습니다 [1] |
| 사용자 CE 키 | `/data/misc/vold/user_keys/ce/${user_id}` | 시스템 DE 키로 암호화한 곳에 있습니다 [1] |
| 사용자 DE 키 | `/data/misc/vold/user_keys/de/${user_id}` | 시스템 DE 키로 암호화한 곳에 있습니다 [1] |
| 메타데이터 암호화 키 | fstab 예: `keydirectory=/metadata/vold/metadata_encryption` | KeyMint 가 보호합니다 [2] |

`${user_id}` 자리에는 사용자 ID 가 들어가서, 사용자와 프로필마다 CE 키와 DE 키가 따로 있습니다 [1]. CE 키는 여기에 더해 잠금 화면 자격 증명과 묶인 합성 비밀번호로 한 번 더 보호하는데, 그 흐름은 [CE 영역과 DE 영역](ce-de-storage.md) 페이지에, 이를 받치는 보안 하드웨어는 [키 저장소와 보안 하드웨어](keystore-tee.md) 페이지에 있습니다.

### 메타데이터 암호화

메타데이터 암호화는 커널 모듈 `dm-default-key` 를 쓰고(Android 공통 커널 4.14 이상, Android 11 이상), 하드웨어나 제조사와 상관없는 blk-crypto 틀 위에서 동작합니다 [2]. 키 자료는 `/metadata` 에 마운트하는 16MB 크기의 metadata 파티션에 두고, 이 키는 KeyMint(이전 이름 Keymaster) 가 보호하며 KeyMint 는 다시 검증 부팅 (Verified Boot) 이 보호합니다 [2]. 하드웨어로 감싼 키를 쓰는 기기는 fstab 에 `metadata_encryption=aes-256-xts:wrappedkey` 처럼 적습니다 [2]. 파티션 배치는 [파티션과 저장 영역](../partitions/index.md), 검증 부팅은 [부트로더와 검증 부팅](../../security-model/verified-boot.md) 페이지를 봅니다.

내부 저장소가 FBE 인 기기에서는 외부 저장 장치를 내부 저장소처럼 쓰는 adoptable storage 에도 메타데이터 암호화가 저절로 켜지고, Android 11 이상에서는 `ro.crypto.volume.options` 와 `ro.crypto.volume.metadata.encryption` 속성으로 이 설정을 바꿀 수 있습니다. Android 10 이하로 나온 기기는 `ro.crypto.volume.contents_mode` 같은 예전 속성을 씁니다 [1].

## 읽는 법

FBE 를 쓰는 기기에서는 시스템 속성 `ro.crypto.state` 가 `encrypted`, `ro.crypto.type` 이 `file` 이어야 합니다 [1]. 라이브 기기라면 이 두 속성과 fstab 의 `fileencryption`·`metadata_encryption` 줄을 함께 보면 암호화 방식과 알고리즘을 확인할 수 있고, 확인한 값과 방법은 확보 기록에 남깁니다. 실제 폰(Android 16 기기 ) 관찰에서는 이 속성을 읽지 않아서, 삼성 기기에서 값이 문서와 같게 나오는지는 확인하지 못했습니다.

버전마다 달라진 점은 아래와 같습니다.

| Android | FBE 쪽 변화 |
|---|---|
| 7.0 | FBE 와 Direct Boot 지원 [1] |
| 9 | 메타데이터 암호화 도입 [2][3] |
| 10 | 새로 나오는 기기는 FBE 필수 [1] |
| 11 | 새로 나오는 기기는 내부 저장소 메타데이터 암호화 필수, fscrypt 정책 기본값 v2 [1][2] |
| 삼성 One UI | AOSP 의 FBE 와 다르게 구현한 부분이 있는지 확인하지 못함 |

## 포렌식에서 중요한 점

아래 해석은 출처 문서에 그대로 적힌 문장이 아니라 위 사실에서 끌어낸 것입니다. 잠금이 풀린 기기에서 논리 추출을 하면 운영체제가 복호화한 파일을 받게 되지만, 저장 장치 원본을 키 없이 그대로 읽은 물리 이미지(칩 오프 등)에서는 파일 내용과 이름이 암호문으로 남습니다. 메타데이터 암호화가 켜진 기기라면 디렉터리 구조와 크기, 시각까지 암호문 안에 들어가서, 원본 이미지만으로는 파일 시스템 시각을 읽어 타임라인을 세우기 어렵습니다. 원본 이미지의 빈 영역에서 지운 파일 조각을 찾는 방법도 이런 기기에서는 암호문 조각을 얻는 데 그칠 수 있으니, 복구 결과를 보고서에 쓰기 전에 기기의 암호화 방식부터 적어 둡니다. 확보 방법별 차이는 [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md), 복구 기법은 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 페이지에서 다룹니다.

## 함정

`ro.crypto.type` 이 `file` 이라는 값은 암호화 방식을 알려 줄 뿐이고, 추출하던 순간에 CE 영역이 열려 있었는지는 알려 주지 않습니다. 그 판단은 [잠금 해제 전·후](bfu-afu.md) 페이지의 기준으로 따로 합니다.

"Android 10 이상은 FBE" 라는 규칙은 그 버전으로 새로 나오는 기기에 대한 요건이라서 [1], 더 낮은 버전으로 나와 업데이트를 받은 기기라면 버전 번호만 보고 방식을 단정하지 말고 속성 값을 확인합니다. 알고리즘도 기기마다 고를 수 있으니, 도구가 보여 주는 알고리즘 이름이 이 페이지의 기본값과 다르더라도 fstab 을 먼저 봅니다.

## 참고 문헌

1. File-based encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/file-based
2. Metadata encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/metadata
3. Encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption
