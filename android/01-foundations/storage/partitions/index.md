---
title: "파티션과 저장 영역"
parent: "기반 · 저장 구조"
nav_order: 0
has_children: true
has_toc: false
---

# 파티션과 저장 영역 (Partitions)

## 한 줄 요약

Android 기기의 저장소는 하는 일이 정해진 여러 파티션으로 나뉘고, Android 10 이후에는 여러 파티션을 super 하나에 담는 동적 파티션이, 업데이트를 위해서는 파티션을 두 벌 두는 A/B 슬롯이 더해져서, 이미지를 읽기 전에 이 배치부터 알아야 합니다.

## 왜 중요한가

사용자가 설치한 앱과 데이터는 userdata 파티션에 있어서 조사 대부분이 여기서 이루어지지만, userdata 를 풀 키는 metadata 파티션에 있고 기기가 어떤 빌드로 동작했는지는 system·vendor 쪽 파티션에 있습니다. 동적 파티션을 쓰는 기기는 system·vendor 가 파티션 표에 따로 나오지 않아서 super 의 메타데이터를 읽어야 꺼낼 수 있고, A/B 기기는 같은 파티션이 두 벌 있어서 어느 슬롯이 현재였는지를 가려야 합니다. 이 배치를 모르고 이미지를 읽으면 "system 파티션이 없다" 거나 "빌드가 두 개다" 같은 잘못된 결론을 적기 쉽습니다.

## 한눈에 보기

| 영역 | 위치 | Android 버전 | 알려 주는 것 |
|---|---|---|---|
| userdata | 물리 파티션 | 모든 버전 | 사용자가 설치한 앱과 데이터 |
| metadata | 물리 파티션 | 메타데이터 암호화는 Android 9 지원, Android 11 이상 출시 기기는 필수 | userdata 메타데이터 암호화 키의 자리 |
| system·vendor 쪽 | 물리 파티션 또는 super 안의 논리 파티션 | 모든 버전 | 기기의 빌드와 운영체제 구성 |
| super | 물리 파티션 하나 | Android 10 도입 | 논리 파티션의 이름과 블록 범위 |
| `_a`·`_b` 슬롯 | 두 벌짜리 파티션 | A/B 는 Android 10 이전부터, Virtual A/B 는 Android 11 도입 | 현재 슬롯과 업데이트 진행 상태 |

삼성 갤럭시 (One UI)가 동적 파티션과 A/B·Virtual A/B 를 어떻게 쓰는지, 삼성 전용 파티션의 이름은 공개된 자료가 없어 검체에서 확인해야 합니다.

## 읽는 순서

1. [파티션 배치 (boot·system·vendor·userdata)](partition-layout.md) — AOSP 가 나누는 파티션 세 묶음과 각 파티션이 담는 것, metadata 파티션과 userdata 암호화의 관계를 다룹니다.
2. [동적 파티션 (super)](super-partition.md) — super 안에 논리 파티션이 어떻게 들어 있는지와, 메타데이터를 읽어 system·vendor 를 꺼내는 순서를 다룹니다.
3. [A/B 슬롯 (A/B Slots)](ab-slots.md) — 두 벌짜리 파티션과 슬롯 상태, 현재 슬롯을 알려 주는 값, Virtual A/B 의 업데이트 흔적을 다룹니다.

## 함께 볼 페이지

- [파일 시스템 (ext4·F2FS)](../filesystems/index.md) — 파티션 안의 파일 시스템 구조
- [저장 공간 암호화 (Encryption)](../encryption/index.md) — userdata 를 가리는 두 겹의 암호화
- [부트로더와 검증 부팅 (Bootloader·Verified Boot)](../../security-model/verified-boot.md) — vbmeta 가 담는 검증 정보
- [기기 정보와 빌드 (build.prop·Build)](../../../02-artifacts/system-account/device-build.md) — system·vendor 쪽에서 읽는 빌드 정보
- [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md) — 파티션 이미지를 얻는 방법과 한계

## 참고 문헌

1. Partitions overview — AOSP — https://source.android.com/docs/core/architecture/partitions
2. Implement dynamic partitions — AOSP — https://source.android.com/docs/core/ota/dynamic_partitions/implement
3. A/B (seamless) system updates — AOSP — https://source.android.com/docs/core/ota/ab
4. Virtual A/B overview — AOSP — https://source.android.com/docs/core/ota/virtual_ab
5. Metadata encryption — AOSP — https://source.android.com/docs/security/features/encryption/metadata
