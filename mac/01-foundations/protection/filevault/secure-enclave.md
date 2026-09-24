---
title: "보안 칩과 데이터 보호"
parent: "파일볼트"
grand_parent: "기반 · 보안·보호"
nav_order: 390
---

# 보안 칩과 데이터 보호 (T2·Apple Silicon·Secure Enclave)

T2 칩을 단 인텔 맥과 Apple silicon 맥은 파일볼트 키를 Secure Enclave 안에서만 다루고, 파일볼트를 켜지 않았어도 볼륨 키를 기기마다 다른 하드웨어 UID로 보호합니다.

## 이 구조를 쓰는 맥

Secure Enclave가 있는 맥은 Apple T1 칩을 단 MacBook Pro(2016–2017), T2 칩을 단 모든 인텔 맥, M1 이후 모든 Apple silicon 맥입니다 [3]. 파일볼트 문서 [1]는 이 가운데 T2와 Apple silicon만 언급하고, T1 맥의 Secure Enclave가 파일볼트 키를 다루는지는 이 페이지의 근거 자료로 확인하지 못했습니다.

| 맥 | 파일볼트 키 보호 | 파일볼트를 끈 상태 |
|---|---|---|
| T2 인텔 맥, Apple silicon 맥 | 키 처리를 모두 Secure Enclave에서 하고 암호화 키가 CPU에 직접 드러나지 않음 [1] | 볼륨은 이미 암호화돼 있고 VEK를 하드웨어 UID로만 보호함 [1] |
| T2 칩이 없는 인텔 맥 | 이동식 저장장치 암호화와 같은 방식이고 Secure Enclave 보호가 없음 [1] | — |

Apple 문서는 파일볼트를 켜기 전에 추가했다가 지운 데이터가 암호화되지 않은 채 남아 포렌식 복구 도구로 되살릴 수 있다고 적습니다 [1]. 이 문장이 어느 기종에 해당하는지 원문이 따로 밝히지 않으니, 조사할 때는 기기 종류와 파일볼트를 켠 시점을 함께 확인한 뒤 적용합니다.

APFS 명세는 하드웨어 암호화를 지원하는 기기의 내장 저장장치에 하드웨어 암호화를 쓰고, 외장 저장장치와 하드웨어 암호화를 지원하지 않는 기기의 내장 저장장치에는 소프트웨어 암호화를 쓴다고 적습니다 [2]. 하드웨어 암호화에서는 커널만 내장 저장장치와 통신하고, 명세는 소프트웨어 암호화만 설명합니다 [2]. 명세의 하드웨어 암호화 기기 목록에는 "macOS (with T2 security chip)" 가 들어 있지만, 2020-06-22 판 명세에는 Apple silicon 언급이 없습니다 [2]. 소프트웨어 암호화의 키백 구조는 [키 계층 (VEK·KEK)](key-hierarchy.md)에서 다룹니다.

## 구조

### 하드웨어 키

UID는 A9 이후 칩에서 제조 중에 Secure Enclave 안의 난수 발생기(TRNG)가 만들어 퓨즈에 기록합니다 [3]. JTAG 같은 디버그 인터페이스로 읽을 수 없고, Secure Enclave 밖의 소프트웨어는 접근할 수 없으며, 기기의 다른 식별자와도 관계가 없습니다 [3]. GID는 같은 SoC를 쓰는 모든 기기에 공통인 키입니다 [3]. Secure Enclave AES 엔진이 쓰는, UID와 GID에서 파생한 하드웨어 키는 sepOS에도 드러나지 않습니다 [3].

### 암호화 엔진

시스템 AES 엔진은 NAND 플래시와 시스템 메모리 사이의 DMA 경로에 있어서 데이터를 회선 속도로 암호화하고 복호하며, 풀린 키를 소프트웨어에 드러내지 않습니다 [3]. 메모리 보호 엔진은 Secure Enclave가 쓰는 DRAM을 AES(XEX 모드)와 CMAC으로 보호하고 부팅할 때마다 임시 키를 새로 만듭니다. A11/S4 이후에는 리플레이 방지가 더해졌고, A14/M1 이후에는 임시 키를 두 개 씁니다 [3].

### 보안 비휘발 저장소

보안 저장 구성요소 (Secure Storage Component)는 A12/S4 이후에 들어갔습니다 [3]. 2020년 가을 이전에 나온 A12·A13·S4·S5 기기는 1세대를 쓰고, 2020년 가을 이후에 나온 A12·A13·S5 기기와 A14 이후·S6 이후·M1 이후 기기는 2세대를 씁니다 [3].

2세대의 카운터 락박스 (counter lockbox)에는 128비트 salt, 128비트 암호 검증값, 8비트 카운터, 8비트 최대 시도 값이 들어 있습니다 [3]. 암호를 시도할 때마다 카운터가 오르고 최대치를 넘으면 락박스를 지우며, 짝지어진 Secure Enclave에서 온 시도만 받습니다 [3]. 보안 저장 구성요소가 없던 이전 방식은 Secure Enclave에서만 접근하는 EEPROM을 썼고, 전용 하드웨어 보안 기능은 없었습니다 [3].

### T2와 M1 이후 비교

| 항목 | T2 (인텔 맥) | M1 이후 |
|---|---|---|
| 메모리 보호 엔진 | 암호화·인증 | 암호화·인증·리플레이 방지 |
| 보안 비휘발 저장소 | EEPROM | 보안 저장 구성요소 2세대 |
| AES 엔진 | DPA 대책·잠금 가능 시드 비트 | DPA 대책·잠금 가능 시드 비트 |
| 공개 키 가속기 (PKA) | OS 결합 키 | OS 결합 키·Boot Monitor |

표는 Apple Platform Security의 Secure Enclave 설명 [3]을 옮긴 것입니다. Apple silicon 맥이 쓰는 데이터 보호 등급과 볼륨 키는 [키 계층 (VEK·KEK)](key-hierarchy.md)의 보호 등급 표와 함께 봅니다.

## 포렌식에서 중요한 점

Apple 문서는 T2·Apple silicon 맥에서 떼어 낸 저장 매체가 직접 대입 공격(brute-force)으로부터 보호된다고 적습니다 [1]. UID가 Secure Enclave 밖으로 나오지 않는다는 설명 [3]과 VEK가 파일볼트를 끈 상태에서도 UID로 보호된다는 설명 [1]을 합치면, 이 맥들의 내장 디스크는 칩오프나 디스크 단독 이미지만으로는 원래 기기 없이 풀 수 없다는 추론이 나옵니다. 이 결론은 두 문서를 합친 추론이고 Apple이 한 문장으로 확인한 사실이 아니라서, 보고서에 쓸 때도 추론이라고 밝힙니다.

이런 맥을 켜진 상태로 만났다면 끄기 전에 무엇을 먼저 확보할지 판단해야 하고, 켜진 기기를 다루는 법은 [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md), 확보 방식 선택은 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md), 잠긴 볼륨을 만났을 때의 판단은 [암호화된 증거 다루기 (Encrypted Evidence)](../../../03-techniques/analysis/encrypted-evidence/index.md)에서 다룹니다. 기기에 T2 칩이 있는지, Apple silicon인지는 [컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)](../../../02-artifacts/system-account/computer-name-hardware.md)에서 먼저 확인합니다.

## 함정

"파일볼트가 꺼져 있다" 는 사실이 "디스크가 평문이다" 를 뜻하지 않습니다. T2·Apple silicon 맥은 파일볼트를 켜지 않아도 볼륨이 암호화돼 있고, 차이는 KEK에 사용자 암호가 더해지느냐입니다 [1].

맥에서 암호를 몇 번 틀리면 지연이나 잠금이 걸리는지 같은 구체 수치는 이 페이지의 근거 자료로 확인하지 못했습니다. 카운터 락박스의 구조 [3]만으로 파일볼트의 시도 한도를 적지 않습니다.

APFS 명세 [2]는 2020-06-22 판이고 Apple silicon 언급이 없으며, 하드웨어 암호화 방식 자체도 설명하지 않습니다. 명세의 소프트웨어 복호 절차를 T2·Apple silicon 내장 디스크에 그대로 적용할 수 있다고 보지 않습니다.

## 참고 문헌

1. Apple Platform Security — Volume encryption with FileVault in macOS — https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/web
2. Apple, Apple File System Reference (2020-06-22 판, PDF) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
3. Apple Platform Security — The Secure Enclave — https://support.apple.com/guide/security/secure-enclave-sec59b0b31ff/web
