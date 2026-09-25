---
title: "CE 영역과 DE 영역"
parent: "저장 공간 암호화"
grand_parent: "기반 · 저장 구조"
nav_order: 110
---

# CE 영역과 DE 영역 (Credential·Device Encrypted Storage)

파일 단위 암호화를 쓰는 Android 기기는 사용자마다 저장 공간을 두 갈래로 나누는데, 잠금 화면 자격 증명과 묶인 키로 암호화하는 CE 영역과 잠금을 풀기 전에도 쓸 수 있는 DE 영역입니다.

## 두 영역의 차이

CE 영역 (Credential Encrypted Storage) 은 기본 저장 위치이고, 사용자 자격 증명(PIN·비밀번호)과 묶인 키로 암호화되어 사용자가 잠금을 푼 뒤에만 쓸 수 있습니다. DE 영역 (Device Encrypted Storage) 은 다이렉트 부트 (Direct Boot) 중에도 잠금을 푼 뒤에도 쓸 수 있고, 검증 부팅이 성공하면 쓸 수 있는 키로 암호화됩니다. 공식 문서는 DE 영역을 다이렉트 부트 중에 꼭 필요한 정보에만 쓰라고 안내합니다.

| | CE 영역 | DE 영역 |
|---|---|---|
| 쓸 수 있는 때 | 사용자가 잠금을 푼 뒤 | 다이렉트 부트 중과 잠금을 푼 뒤 |
| 키가 묶인 대상 | 사용자 자격 증명(PIN·비밀번호) | 검증 부팅 성공 |
| 쓰임 | 기본 저장 위치 | 다이렉트 부트 중에 꼭 필요한 정보 |
| 도입 | Android 7.0 | Android 7.0 |

CE 영역이 언제 다시 잠기는지, 잠금 화면과 CE 잠금이 어떻게 다른지는 [잠금 해제 전·후 (BFU·AFU)](bfu-afu.md) 페이지에서 다룹니다. 파일 내용과 이름을 암호화하는 방식 자체는 [파일 단위 암호화 (FBE)](fbe.md) 페이지를 봅니다.

## 경로

AOSP 문서가 적은 대표 경로는 아래와 같고, `${user_id}` 자리에는 사용자 ID 가 들어갑니다. 문서에는 이 밖에 FBE 로 암호화하지 않는 폴더(`/data/unencrypted` 등)와 재부팅하면 사라지는 `/data/per_boot`, adoptable storage 쪽 경로도 따로 나뉘어 있습니다.

| 구분 | 경로 |
|---|---|
| CE(사용자별) | `/data/user/${user_id}`, `/data/misc_ce/${user_id}`, `/data/media/${user_id}`, `/data/system_ce/${user_id}`, `/data/vendor_ce/${user_id}` |
| DE(사용자별) | `/data/user_de/${user_id}`, `/data/misc_de/${user_id}`, `/data/system_de/${user_id}`, `/data/vendor_de/${user_id}` |
| 시스템 DE | `/data/app`, `/data/system`, `/data/misc`, `/data/vendor` |

CE 목록에는 `/data/media/${user_id}` 도 들어 있습니다. 이 폴더와 사용자가 보는 공용 저장 공간(/sdcard)이 어떻게 이어지는지는 이 페이지의 출처로 확인하지 못해서 [공용 저장 공간](../shared-storage.md) 페이지에 맡깁니다. 앱 폴더가 `/data/user` 와 `/data/user_de` 아래에 어떻게 놓이는지는 [앱 데이터 폴더 구조](../app-data-layout.md) 페이지를 봅니다.

시스템 아티팩트도 이 구분을 따릅니다. 예를 들어 앱 사용 기록은 `/data/system_ce/${user_id}/usagestats/` 아래에 있어서 CE 경로 목록과 들어맞고, 자세한 내용은 [앱 사용 기록](../../../02-artifacts/app-usage/usagestats/index.md) 페이지에서 다룹니다.

이 경로는 AOSP 문서 기준입니다. 관찰 기기에서는 일반 셸 권한으로 `/data` 아래를 읽지 않아서, 삼성 One UI 에서도 경로가 그대로인지는 확인하지 못했습니다.

## 앱이 DE 영역을 쓰는 방법

앱은 기본적으로 CE 영역에 데이터를 두고, 다이렉트 부트 중에 돌아야 하는 앱만 따로 DE 영역을 씁니다. 아래 API 이름을 앱 소스나 매니페스트에서 보면 그 앱이 DE 영역을 쓴다는 단서가 됩니다.

| API·속성 | 하는 일 |
|---|---|
| `createDeviceProtectedStorageContext()` | DE 영역을 쓰는 Context 를 만듭니다 |
| 매니페스트 속성 `directBootAware` | 구성 요소를 다이렉트 부트 중에도 실행할 수 있다고 표시합니다 |
| `moveSharedPreferencesFrom()`, `moveDatabaseFrom()` | CE·DE 사이로 SharedPreferences 와 DB 를 옮깁니다 |

앱이 DE 영역으로 옮긴 파일은 `/data/user_de` 아래에 있고, 잠금 해제 전에도 기기 안에서 복호화된 채 쓰일 수 있는 자리입니다. 어떤 앱이 무엇을 DE 영역에 두는지는 앱마다 달라서, 이 페이지에서는 개별 앱 목록을 다루지 않습니다.

## CE 키를 지키는 방식 (합성 비밀번호)

CE 키는 합성 비밀번호 (Synthetic Password) 로 보호하고, AOSP 문서는 그 과정을 아래처럼 설명합니다. 기기가 Weaver HAL 을 갖췄는지에 따라 2·3단계가 갈립니다.

1. 사용자의 잠금 화면 지식 요소(LSKF: PIN·패턴·비밀번호)를 scrypt 로 늘립니다.
2. Weaver HAL 이 있는 기기는 늘린 값을 보안 요소나 TEE 에 둔 Weaver 비밀과 짝짓고, Weaver 가 없는 기기는 늘린 값을 Gatekeeper 비밀번호로 씁니다. 두 경우 모두 이 단계에서 시도 횟수를 제한합니다.
3. 합성 비밀번호는 두 번 암호화합니다. Weaver 기기는 늘린 LSKF 와 Weaver 비밀로 유도한 소프트웨어 키로 한 번, 인증에 묶이지 않은 Keystore 키로 또 한 번 암호화합니다. Gatekeeper 기기는 늘린 LSKF 와 secdiscardable 파일의 해시로 유도한 소프트웨어 키로 한 번, Gatekeeper 등록에 인증이 묶인 Keystore 키로 또 한 번 암호화합니다.

3단계의 Keystore 키가 어떤 보안 하드웨어에 놓이는지는 [키 저장소와 보안 하드웨어 (Keystore·TEE·StrongBox)](keystore-tee.md) 페이지를, CE·DE 키 파일이 저장되는 위치는 [파일 단위 암호화 (FBE)](fbe.md) 페이지를 봅니다.

## 사용자마다 따로 있는 CE·DE

경로에 `${user_id}` 가 들어가는 것처럼 CE·DE 영역은 사용자마다 따로 있습니다. 관찰 기기의 `dumpsys user` 출력에는 기본 사용자(`isPrimary=true`) 말고도 사용자 ID 가 세 자리 이상이고 `isPrimary=false`, `parentId=#` 인 사용자가 하나 더 있었습니다. 이 사용자가 보안 폴더인지 다른 기능인지는 값이 가려져 있어 확인하지 못했고, 이런 사용자에게도 따로 CE·DE 영역이 있다고 보면 경로 표의 `${user_id}` 자리에 그 ID 가 들어갑니다. 여러 사용자와 프로필은 [사용자와 프로필](../../../02-artifacts/system-account/users-profiles.md) 페이지를, 보안 폴더는 [보안 폴더와 작업 프로필](../../security-model/secure-folder-work-profile.md) 페이지를 봅니다.

## 함정

DE 영역이라고 암호화되지 않은 것은 아니고, 검증 부팅이 성공해야 쓸 수 있는 키로 암호화되어 있습니다. 같은 앱이라도 CE 영역과 DE 영역에 파일을 나눠 둘 수 있어서, `/data/user/${user_id}` 만 보고 앱 데이터를 다 봤다고 판단하면 `/data/user_de` 쪽 파일을 놓칩니다. 기본 사용자 말고 다른 사용자가 있는 기기에서는 사용자 ID 마다 경로를 따로 확인해야 합니다.

## 참고 문헌

1. File-based encryption — Android Open Source Project — https://source.android.com/docs/security/features/encryption/file-based
2. Support Direct Boot mode — Android Developers — https://developer.android.com/privacy-and-security/direct-boot
