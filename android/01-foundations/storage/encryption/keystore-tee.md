---
title: "키 저장소와 보안 하드웨어"
parent: "저장 공간 암호화"
grand_parent: "기반 · 저장 구조"
nav_order: 120
---

# 키 저장소와 보안 하드웨어 (Keystore·TEE·StrongBox)

안드로이드 키 저장소 (Android Keystore) 는 암호 키를 기기 밖으로 꺼내기 어렵게 담아 두는 시스템이고, 그 키를 신뢰 실행 환경 (TEE, Trusted Execution Environment) 이나 보안 요소 (SE, Secure Element) 에 묶어 저장 공간 암호화의 바탕이 됩니다.

## 저장 공간 암호화와 이어지는 곳

키 저장소는 앱이 쓰는 키뿐만 아니라 저장 공간 암호화의 키까지 보호합니다. 메타데이터 암호화 키는 KeyMint 가 보호하고, CE 키를 감싸는 합성 비밀번호도 Keystore 키로 한 번 더 암호화합니다. 합성 비밀번호의 흐름은 [CE 영역과 DE 영역](ce-de-storage.md) 페이지를, 메타데이터 암호화는 [파일 단위 암호화 (FBE)](fbe.md) 페이지를 봅니다.

## 키를 꺼내지 못하게 하는 두 가지 방법

키 자료는 내보낼 수 없고, 공식 문서는 이를 두 가지 방법으로 막는다고 설명합니다. 첫째로 키 자료가 앱 프로세스에 들어가지 않고 시스템 프로세스가 대신 연산하며, 둘째로 키 자료를 TEE 나 보안 요소에 묶을 수 있습니다.

TEE 는 SoC 안의 신뢰 실행 환경이고, KeyMint TA 는 이 보안 영역에서 도는 소프트웨어로 대개 ARM SoC 의 TrustZone 안에서 돕니다. 하드웨어 기반 키는 민감한 연산을 사용자 공간이나 커널 공간에서 하지 않게 해서 비밀 키 자료를 지킵니다.

## HAL 버전 역사

키 저장소를 뒷받침하는 하드웨어 추상화 계층 (HAL) 은 버전마다 이름과 기능이 바뀌었습니다.

| Android 버전 | HAL | 들어온 것 |
|---|---|---|
| 5 이하 | Keymaster 0.2·0.3 | 서명·검증, 비대칭 키 |
| 6.0 | Keymaster 1.0 | AES·HMAC, 접근 제어 |
| 7.0 | Keymaster 2 | 키 증명, 버전 묶기 |
| 8.0 | Keymaster 3 | C++ HAL 로 전환, ID 증명 |
| 9 | Keymaster 4 | 내장 보안 요소 지원, 안전한 키 가져오기, 3DES |
| 10 | Keymaster 4.1 | 기기가 잠금 해제된 동안만 쓰는 키, 하드웨어로 감싼 저장 키 |
| 12 | KeyMint | KeyMint HAL 이 Keymaster HAL 을 대체, Rust 로 새로 쓴 `keystore2` 데몬 |
| 13 | KeyMint v2 | Curve25519 서명·키 합의 |

키 증명 (Key Attestation) 은 키와 그 접근 제어를 자세히 적은 공개 키 인증서를 주는 기능이고, ID 증명은 일련번호·제품명·전화 ID 같은 하드웨어 식별자를 제한적으로 증명합니다. 버전 묶기는 옛 버전의 약점을 아는 공격자가 기기를 그 버전으로 되돌리지 못하게 막습니다.

## keystore2 데몬과 저장 위치

`keystore2` 는 Binder API 로 키 저장소 기능을 모두 제공하는 시스템 데몬입니다. 현행 AOSP 소스에서 이 데몬이 키를 두는 폴더는 `/data/misc/keystore` 이고(소스의 `DB_PATH`, 주석 "The path where keystore stores all its keys."), 예전 형식의 키 블롭을 읽는 `LegacyBlobLoader` 도 같은 폴더를 씁니다. `/data/misc` 는 AOSP 문서에서 시스템 DE 경로에 들어갑니다. 이 폴더 안의 파일 이름과 구조는 이 페이지의 출처로 확인하지 못해서 다루지 않습니다.

## StrongBox

StrongBox 는 KeyMint HAL 을 내장 보안 요소나 통합 보안 영역(iSE)으로 구현한 것으로, TEE 보다 격리와 변조 저항이 강합니다. Android 9(API 28)부터 쓸 수 있고, 자체 CPU·보안 저장소·진짜 난수 생성기·패키지 변조와 무단 사이드로드 방어·보안 타이머·재부팅 알림 핀(GPIO 상당)을 갖춰야 합니다.

지원하는 알고리즘은 RSA 2048, AES 128·256, ECDSA·ECDH P-256, HMAC-SHA256(키 8~64바이트), Triple DES 입니다. 앱은 `FEATURE_STRONGBOX_KEYSTORE` 로 기기가 StrongBox 를 지원하는지 확인하고, 키를 만들 때는 `KeyGenParameterSpec.Builder.setIsStrongBoxBacked()` 를, 가져올 때는 `KeyProtection.Builder.setIsStrongBoxBacked()` 를 씁니다. 지원하지 않는 기기에서는 `StrongBoxUnavailableException` 이 납니다.

## 키가 어디에 있는지 확인하는 API

| API | 알려 주는 것 |
|---|---|
| `KeyInfo.getSecurityLevel()` | 키가 놓인 보안 수준(`TRUSTED_ENVIRONMENT` 또는 `STRONGBOX` 면 보안 하드웨어). Android 10(API 29) 이상을 대상으로 한 앱 |
| `KeyInfo.isInsideSecureHardware()` | 키가 보안 하드웨어 안에 있는지. Android 9(API 28) 이하를 대상으로 한 앱 |
| `setUserAuthenticationParameters(duration, authType)` | 인증 뒤 일정 시간 동안 허용할지, 연산마다 인증할지 정합니다 |
| `KeyInfo.isUserAuthenticationRequirementEnforcedBySecureHardware()` | 사용자 인증 조건을 보안 하드웨어가 강제하는지 |

앱 소스를 분석할 때 이 이름이 보이면 그 앱이 키 저장소에 키를 두고 보안 하드웨어나 사용자 인증에 묶는다는 단서가 됩니다.

## 포렌식에서 중요한 점

아래 내용은 공식 문서의 설계 설명에서 끌어낸 해석이고, 문서에 이 문장 그대로 있지는 않습니다. 키 자료를 내보낼 수 없고 TEE 나 보안 요소에 묶을 수 있게 설계되어 있어서, 이미지에 `/data/misc/keystore` 폴더가 들어 있더라도 그 안에서 바로 쓸 수 있는 키 자료를 얻는다고 기대하기 어렵습니다. 앱이 키 저장소의 키로 데이터를 암호화해 두었다면 이미지에서 꺼낸 파일만으로는 내용을 읽지 못할 수 있어서, 분석할 때 암호화 여부를 먼저 확인해 두어야 결과가 비어 있는 이유를 설명할 수 있습니다. 앱 데이터를 분석하는 절차는 [앱 데이터 분석](../../../03-techniques/analysis/app-data-analysis/index.md) 페이지를 봅니다.

## 함정

관찰 기기에서 읽은 `dumpsys package` 요약에는 기능 목록이 없어서, 관찰 기기가 `FEATURE_STRONGBOX_KEYSTORE` 를 지원하는지는 확인하지 못했습니다. 삼성 갤럭시가 StrongBox 를 어떤 하드웨어로 구현하는지도 이 페이지의 출처로 확인하지 못했고, 삼성 고유 보안 구조는 [삼성 녹스](../../security-model/samsung-knox.md) 페이지에 맡깁니다. 키 저장소 폴더 경로는 현행 AOSP 소스 기준이라서, 옛 버전이나 제조사 기기에서는 따로 확인해야 합니다. KeyMint 를 보호하는 검증 부팅은 [부트로더와 검증 부팅](../../security-model/verified-boot.md) 페이지를 봅니다.

## 참고 문헌

1. File-based encryption — Android Open Source Project — https://source.android.com/docs/security/features/encryption/file-based
2. Hardware-backed Keystore — Android Open Source Project — https://source.android.com/docs/security/features/keystore
3. Android Keystore system — Android Developers — https://developer.android.com/privacy-and-security/keystore
4. Metadata encryption — Android Open Source Project — https://source.android.com/docs/security/features/encryption/metadata
5. keystore2/src/globals.rs (AOSP system/security, main) — https://android.googlesource.com/platform/system/security/+/refs/heads/main/keystore2/src/globals.rs
