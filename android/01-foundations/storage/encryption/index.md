---
title: "저장 공간 암호화"
parent: "기반 · 저장 구조"
nav_order: 80
has_children: true
has_toc: false
---

# 저장 공간 암호화 (Encryption)

Android 는 사용자 데이터를 디스크에 쓰기 전에 대칭 키로 자동 암호화하고 읽을 때 자동 복호화하고, Android 10 이상으로 새로 나오는 기기는 파일 단위 암호화를 써야 합니다.

## 왜 중요한가

암호화 방식과 기기의 잠금 상태에 따라 수집한 데이터가 평문인지 암호문인지가 갈립니다. 공식 문서의 설명에서 끌어낸 해석으로는, 잠금이 풀린 기기에서 논리 추출한 데이터는 복호화된 파일이고, 칩을 떼어 내는 방식처럼 저장 매체만 읽은 물리 이미지에는 암호문만 남습니다. 수집 결과에서 어떤 앱 데이터가 비어 있을 때 그 이유가 삭제인지 암호화인지 가려내려면 이 구조를 먼저 알아야 하고, 수집 방식에 따른 차이는 [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지에서 다룹니다.

Android 의 저장 공간 암호화는 두 가지입니다. 전체 디스크 암호화 (FDE, Full-Disk Encryption) 는 Android 5.0 ~ 9 에서 지원했고, 기기 비밀번호로 보호하는 키 하나로 userdata 파티션 전체를 보호합니다. 파일 단위 암호화 (FBE, File-Based Encryption) 는 Android 7.0 부터 지원하고, 파일마다 다른 키로 암호화해 키를 따로따로 풀 수 있어서 잠금 해제 전에도 일부 데이터를 쓰는 다이렉트 부트 (Direct Boot) 가 가능합니다. Android 10 이상으로 새로 나오는 기기는 FBE 를 써야 하고 FDE 는 쓸 수 없습니다. 삼성 One UI 가 AOSP 와 다르게 구현한 부분은 이 묶음의 출처로 확인하지 못했고, 삼성 고유 보안 구조는 [삼성 녹스](../../security-model/samsung-knox.md) 페이지를 봅니다.

## 한눈에 보기

| 주제 | 위치 | Android 버전 | 알려 주는 것 |
|---|---|---|---|
| 파일 단위 암호화 | userdata 파티션의 파일 내용·이름 | 7.0 부터, 10 이상 새 기기 필수 | 암호화 알고리즘, fstab 설정, 시스템 속성 |
| 메타데이터 암호화 | 디렉터리 구조·크기·권한·시각, 키는 `/metadata` 파티션 | 9 부터, 11 이상 새 기기 필수 | FBE 가 보호하지 않는 정보의 암호화 |
| 잠금 해제 전·후 | 기기의 실행 상태 | 7.0 부터 | 수집 시점에 복호화된 채 쓸 수 있는 범위 |
| CE 영역과 DE 영역 | `/data/user`, `/data/user_de` 등 사용자별 경로 | 7.0 부터 | 경로마다 잠금 해제가 필요한지 |
| 키 저장소 | `keystore2` 데몬이 관리하고 키는 TEE·보안 요소에 묶음 | 6.0 ~ 13 사이에 여러 번 바뀜 | 키가 어디에 묶여 있는지 |

버전별로 들어온 기능을 모으면 아래와 같습니다. 키 저장소 HAL 의 버전별 차이는 [키 저장소와 보안 하드웨어](keystore-tee.md) 페이지에 자세히 있습니다.

| Android 버전 | 저장 공간 암호화 | 키 저장소 |
|---|---|---|
| 5.0 ~ 9 | FDE 지원 | |
| 7.0 | FBE·다이렉트 부트 도입 | Keymaster 2(키 증명, 버전 묶기) |
| 9 | 메타데이터 암호화 도입 | Keymaster 4, StrongBox(API 28) |
| 10 | 새 기기 FBE 필수 | Keymaster 4.1 |
| 11 | 새 기기 메타데이터 암호화 필수, fscrypt 정책 기본값 v2 | |
| 12 | | KeyMint HAL 이 Keymaster HAL 을 대체, `keystore2` 데몬 |
| 13 | | KeyMint HAL v2 |

## 읽는 순서

1. [파일 단위 암호화 (FBE)](fbe.md) — 파일 내용과 이름을 암호화하는 방식, fscrypt 정책, 메타데이터 암호화, 키 파일 위치를 다룹니다.
2. [잠금 해제 전·후 (BFU·AFU)](bfu-afu.md) — 재시작 뒤 첫 잠금 해제를 기준으로 기기 상태를 나누고, 그 상태가 기기에 어떻게 기록되는지 다룹니다.
3. [CE 영역과 DE 영역 (Credential·Device Encrypted Storage)](ce-de-storage.md) — 사용자별 저장 공간이 어느 경로에서 두 갈래로 나뉘는지, CE 키를 어떻게 보호하는지 다룹니다.
4. [키 저장소와 보안 하드웨어 (Keystore·TEE·StrongBox)](keystore-tee.md) — 키를 기기 밖으로 꺼내지 못하게 하는 구조와 HAL 버전 역사를 다룹니다.

## 함께 볼 페이지

- [파티션과 저장 영역](../partitions/index.md) — userdata·metadata 파티션
- [파일 시스템 (ext4·F2FS)](../filesystems/index.md) — 암호화가 얹히는 파일 시스템
- [앱 데이터 폴더 구조](../app-data-layout.md) — `/data/user` 와 `/data/user_de` 아래 앱 폴더
- [부트로더와 검증 부팅](../../security-model/verified-boot.md) — DE 키를 쓸 수 있게 되는 조건과 KeyMint 보호
- [보안 폴더와 작업 프로필](../../security-model/secure-folder-work-profile.md) — 기본 사용자 말고 다른 사용자의 저장 공간
- [잠금 화면 설정](../../../02-artifacts/system-account/lock-settings.md) — CE 키와 묶이는 잠금 화면 자격 증명의 설정

## 참고 문헌

1. Encryption (개요) — Android Open Source Project — https://source.android.com/docs/security/features/encryption
2. File-based encryption — Android Open Source Project — https://source.android.com/docs/security/features/encryption/file-based
3. Metadata encryption — Android Open Source Project — https://source.android.com/docs/security/features/encryption/metadata
4. Hardware-backed Keystore — Android Open Source Project — https://source.android.com/docs/security/features/keystore
5. Android Keystore system — Android Developers — https://developer.android.com/privacy-and-security/keystore
