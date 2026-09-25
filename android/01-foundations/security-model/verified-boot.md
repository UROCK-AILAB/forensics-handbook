---
title: "부트로더와 검증 부팅"
parent: "기반 · 보안 구조"
nav_order: 280
---

# 부트로더와 검증 부팅 (Bootloader·Verified Boot)

부트로더는 기기가 제조사의 서명을 받은 소프트웨어만 부팅하도록 잠긴 상태와 수정을 허용하는 풀린 상태를 오가고, 검증 부팅 (Verified Boot) 은 부팅할 때마다 그 상태와 소프트웨어의 무결성을 확인해 결과를 색으로 나타냅니다.

## 이 구조가 드러나는 아티팩트

부트로더 상태는 수집한 데이터가 언제부터 남아 있을 수 있는지, 기기에서 도는 소프트웨어를 믿어도 되는지를 판단하는 바탕이 됩니다. 그래서 [초기화 흔적](../../02-artifacts/system-account/factory-reset.md), [기기 정보와 빌드](../../02-artifacts/system-account/device-build.md), [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md), [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 페이지를 읽을 때 이 페이지를 함께 봅니다. 삼성 기기에서만 따로 있는 보안 표시는 [삼성 녹스](samsung-knox.md) 페이지에서 다룹니다.

## 기기 상태와 신뢰 루트

검증 부팅에서 기기 상태는 LOCKED 와 UNLOCKED 두 가지입니다. LOCKED 는 새 소프트웨어를 기기에 굽지 못하게 막고, UNLOCKED 는 수정을 허용합니다. 상태는 fastboot 도구의 잠금·잠금 해제 명령으로 바꾸고, 사용자 데이터를 지키려고 **상태를 바꿀 때마다 데이터 파티션을 지우며** 지우기 전에 사용자에게 확인을 받습니다. 잠금을 풀 때도, 다시 잠글 때도 휴대전화의 모든 개인 데이터를 지운다는 확인 화면이 뜹니다.

신뢰 루트 (root of trust) 는 기기에 저장된 Android 사본을 서명한 암호 키입니다. 공개 키는 기기의 읽기 전용 저장소에 들어 있고 비밀 키는 제조사가 보관합니다. 기기에 따라 사용자가 신뢰 루트를 따로 지정할 수 있는데, 이때는 물리적으로 확인하는 절차가 필요하고, 키를 변조 흔적이 남는 저장소에 두며, 사용자 지정 OS 로 부팅하면 사용자에게 알립니다. Pixel 2 는 이 기능을 `avb_custom_key` 가상 파티션으로 구현했습니다.

## 부팅 상태의 색

부트로더는 기기 상태와 검증 결과에 따라 부팅 상태를 색으로 정하고, 색마다 화면 경고가 다릅니다.

| 색 | 조건 | 화면과 동작 |
|---|---|---|
| GREEN | LOCKED, 사용자 신뢰 루트 없음 | 경고 없이 정상 부팅 |
| YELLOW | LOCKED, 사용자 신뢰 루트 사용 | 부팅할 때마다 경고 화면을 띄우고 10초 뒤 넘어가 부팅을 이어 감. 전원 버튼을 한 번 누르면 멈추고, 한 번 더 누르면 부팅을 이어 감 |
| ORANGE | UNLOCKED | 부트로더가 풀려 소프트웨어 무결성을 보장할 수 없다는 경고를 부팅할 때마다 띄우고, 10초 뒤 넘어가는 방식과 전원 버튼 동작은 YELLOW 와 같음 |
| RED (eio) | 유효한 Android 는 있지만 dm-verity 가 `eio` 모드 | 경고 화면을 띄우고 전원 버튼으로 확인해야 부팅을 이어 감. 30초 안에 확인하지 않으면 전원이 꺼짐 |
| RED (no OS) | 유효한 Android 가 없음 | 경고 화면을 띄우고 부팅하지 않음. 전원 버튼으로 끄거나 30초 안에 확인하지 않으면 전원이 꺼짐 |

## 부트로더가 커널에 넘기는 값

부트로더는 부팅 상태를 `androidboot.verifiedbootstate` 로 커널에 넘기고, 값은 `green`·`yellow`·`orange` 입니다. dm-verity 동작 방식은 `androidboot.veritymode` 로 넘기고, 값은 `eio` 또는 `restart` 입니다. Android 검증 부팅 2.0(AVB) 이 넘기는 값의 이름은 아래와 같습니다.

```
androidboot.vbmeta.device_state
androidboot.vbmeta.digest
androidboot.vbmeta.hash_alg
androidboot.vbmeta.size
androidboot.vbmeta.invalidate_on_error
androidboot.vbmeta.avb_version
androidboot.veritymode
```

`androidboot.vbmeta.device_state` 의 값은 `locked` 또는 `unlocked` 입니다. 나머지 값의 정확한 뜻은 이번 판에서 원문으로 확인하지 못해 이름만 적습니다. 이 값들이 사용자 공간에서 어떤 시스템 속성 이름으로 보이는지도 이번 판의 출처로 확인하지 못했고, 관찰 기기에서 `getprop` 출력도 읽지 않았습니다.

## 롤백 보호

검증 부팅은 롤백 인덱스를 저장해 두고 그보다 오래된 이미지로는 부팅하지 않아서, 알려진 취약점이 있는 이전 버전으로 되돌아가는 것을 막습니다. A/B 파티션을 쓰는 기기는 새 부팅 슬롯이 SUCCESSFUL 로 표시된 뒤에야 롤백 인덱스를 갱신합니다. 파티션 구성은 [파티션과 저장 영역](../storage/partitions/index.md) 페이지를 봅니다.

## 기기에서 보이는 흔적

관찰 기기는 루팅하지 않았고 부트로더가 잠긴 상태였습니다(확인 범위: Android 16, One UI 8.5). adb 일반 셸 권한으로 읽은 설정 값의 global 표에는 개발자 옵션·adb·부팅 횟수와 이름이 이어지는 키가 있었고, 값은 가려서 확인하지 않았습니다(확인 범위: Android 16, One UI 8.5).

```
development_settings_enabled
adb_enabled
adb_wifi_enabled
boot_count
```

이 키들은 부트로더 상태 자체를 적는 곳이 아니고, 이름으로 보아 개발자 옵션과 adb 사용 여부, 부팅 횟수와 이어지는 값입니다. 각 키의 뜻과 값의 형식은 [설정 값](../../02-artifacts/system-account/settings.md) 페이지에서 다룹니다. 개발자 옵션 안의 OEM 잠금 해제 항목이 어떤 설정 키로 남는지는 이번 판에서 확인하지 못했습니다.

## 포렌식에서 중요한 점

아래는 공식 문서의 설명에서 끌어낸 해석이고, 문서에 이 문장 그대로 있지는 않습니다.

상태를 바꿀 때마다 데이터 파티션을 지우는 것이 정상 동작이라서, 부트로더가 한 번이라도 풀렸다가 다시 잠겼다면 그 전의 사용자 데이터는 남아 있지 않은 것이 정상입니다. 기기에 남은 데이터가 이상하게 짧은 기간만 담고 있을 때, 초기화뿐만 아니라 부트로더 상태 변경도 원인 후보로 둡니다. 초기화 흔적을 찾는 법은 [초기화 흔적](../../02-artifacts/system-account/factory-reset.md) 페이지를 봅니다.

기기를 켤 때 나오는 경고 화면은 부팅 상태를 바로 보여 주는 표시입니다. ORANGE 경고는 부트로더가 풀린 기기에서, YELLOW 경고는 사용자가 지정한 신뢰 루트를 쓰는 기기에서 뜨고, 어느 쪽이든 기기에서 도는 소프트웨어가 제조사 서명본이 아닐 수 있다는 전제로 수집 결과를 봅니다. 꺼진 채로 들어온 기기를 켤 때 경고 화면이 보이면 사진으로 남겨 둡니다. 켜진 채로 들어온 기기를 이 화면을 보려고 다시 시작하면 잠금 해제 전 상태로 돌아가서 읽을 수 있는 범위가 좁아질 수 있으니, 재시작 여부는 수집 절차 안에서 정합니다. 잠금 해제 전·후 상태는 [저장 공간 암호화](../storage/encryption/index.md) 페이지에서 다룹니다.

## 함정

삼성 기기의 다운로드 모드 화면 항목, 삼성 부트로더의 경고 문구, 삼성의 롤백 보호 방식, 그리고 삼성 기기에서도 상태를 바꿀 때 데이터를 지우는지는 이번 판에서 삼성 문서로 확인하지 못했습니다. 위 표의 색과 문구는 AOSP 기준이라서 삼성 기기에 그대로 옮기지 않습니다.

키 증명 (key attestation) 에 부팅 상태가 담기는지도 이번 판에서 확인하지 못해 다루지 않습니다.

## 도구

부팅 상태는 기기를 켤 때 나오는 화면으로 먼저 확인하고, adb 일반 셸 권한으로는 `settings list global` 로 위 설정 키를 볼 수 있습니다. 부트로더 상태를 바꾸는 명령은 데이터를 지우기 때문에 증거 기기에서 쓰지 않습니다. 기기 빌드 정보를 읽는 법은 [기기 정보와 빌드](../../02-artifacts/system-account/device-build.md) 페이지를 봅니다.

## 참고 문헌

1. Boot flow (Verified Boot) — Android Open Source Project — https://source.android.com/docs/security/features/verifiedboot/boot-flow
2. Device state (Verified Boot) — Android Open Source Project — https://source.android.com/docs/security/features/verifiedboot/device-state
3. Android Verified Boot 2.0 README (AOSP external/avb, main) — https://android.googlesource.com/platform/external/avb/+/refs/heads/main/README.md
