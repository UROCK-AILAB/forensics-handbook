---
title: "보안 칩과 데이터 보호"
parent: "파일볼트"
grand_parent: "기반 · 보안·보호"
nav_order: 390
---

# 보안 칩과 데이터 보호 (T2·Apple Silicon·Secure Enclave)

T2 칩을 단 인텔 맥과 Apple silicon 맥은 파일볼트 키를 Secure Enclave 안에서만 다루고, 파일볼트를 켜지 않았어도 볼륨 키를 기기마다 다른 하드웨어 UID로 보호합니다.

## 이 구조를 쓰는 맥

Secure Enclave가 있는 맥은 Apple T1 칩을 단 MacBook Pro(2016–2017), T2 칩을 단 모든 인텔 맥, M1 이후 모든 Apple silicon 맥입니다 [3]. 이 가운데 파일볼트 키를 Secure Enclave에서 다루는 맥은 T2 맥과 Apple silicon 맥입니다 [1].

| 맥 | 파일볼트 키 보호 | 파일볼트를 끈 상태 |
|---|---|---|
| T2 인텔 맥, Apple silicon 맥 | 키 처리를 모두 Secure Enclave에서 하고 암호화 키가 CPU에 직접 드러나지 않음 [1] | 볼륨은 이미 암호화돼 있고 VEK를 하드웨어 UID로만 보호함 [1] |
| T2 칩이 없는 인텔 맥 | 이동식 저장장치 암호화와 같은 방식이고 Secure Enclave 보호가 없음 [1] | — |

파일볼트를 켜기 전에 추가했다가 지운 데이터는 암호화되지 않은 채 남아 포렌식 복구 도구로 되살릴 수 있습니다 [1]. 이것이 어느 기종에 해당하는지는 따로 밝혀져 있지 않으니, 조사할 때는 기기 종류와 파일볼트를 켠 시점을 함께 확인한 뒤 적용합니다.

하드웨어 암호화를 지원하는 기기의 내장 저장장치는 하드웨어 암호화를 쓰고, 외장 저장장치와 하드웨어 암호화를 지원하지 않는 기기의 내장 저장장치는 소프트웨어 암호화를 씁니다 [2]. 하드웨어 암호화에서는 커널만 내장 저장장치와 통신하고, 명세는 소프트웨어 암호화만 설명합니다 [2]. 명세의 하드웨어 암호화 기기 목록에는 "macOS (with T2 security chip)" 가 들어 있지만, 2020-06-22 판 명세에는 Apple silicon 언급이 없습니다 [2]. 소프트웨어 암호화의 키백 구조는 [키 계층 (VEK·KEK)](key-hierarchy.md)에서 다룹니다.

## 구조

### 하드웨어 키

UID는 A9 이후 칩에서 제조 중에 Secure Enclave 안의 난수 발생기(TRNG)가 만들어 퓨즈에 기록합니다 [3]. JTAG 같은 디버그 인터페이스로 읽을 수 없고, Secure Enclave 밖의 소프트웨어는 접근할 수 없으며, 기기의 다른 식별자와도 관계가 없습니다 [3]. GID는 같은 SoC를 쓰는 모든 기기에 공통인 키입니다 [3]. Secure Enclave AES 엔진이 쓰는, UID와 GID에서 파생한 하드웨어 키는 sepOS에도 드러나지 않습니다 [3].

### 암호화 엔진

시스템 AES 엔진은 NAND 플래시와 시스템 메모리 사이의 DMA 경로에 있어서 데이터를 회선 속도로 암호화하고 복호하며, 풀린 키를 소프트웨어에 드러내지 않습니다 [3]. 메모리 보호 엔진은 Secure Enclave가 쓰는 DRAM을 AES(XEX 모드)와 CMAC으로 보호하고 부팅할 때마다 임시 키를 새로 만듭니다. A11/S4 이후에는 리플레이 방지가 더해졌고, A14/M1 이후에는 임시 키를 두 개 씁니다 [3].

### 보안 비휘발 저장소

보안 저장 구성요소 (Secure Storage Component)는 A12/S4 이후에 들어갔습니다 [3]. 2020년 가을 이전에 나온 A12·A13·S4·S5 기기는 1세대를 쓰고, 2020년 가을 이후에 나온 A12·A13·S5 기기와 A14 이후·S6 이후·M1 이후 기기는 2세대를 씁니다 [3].

2세대의 카운터 락박스 (counter lockbox)에는 128비트 salt, 128비트 암호 검증값, 8비트 카운터, 8비트 최대 시도 값이 들어 있습니다 [3]. 암호를 시도할 때마다 카운터가 오르고 최대치를 넘으면 락박스를 지우며, 짝지어진 Secure Enclave에서 온 시도만 받습니다 [3]. 보안 저장 구성요소가 없던 이전 방식은 Secure Enclave에서만 접근하는 EEPROM을 썼고, 전용 하드웨어 보안 기능은 없었습니다 [3].

### T2와 M1 이후 비교

T2 인텔 맥과 M1 이후 맥의 Secure Enclave는 아래처럼 다릅니다 [3].

| 항목 | T2 (인텔 맥) | M1 이후 |
|---|---|---|
| 메모리 보호 엔진 | 암호화·인증 | 암호화·인증·리플레이 방지 |
| 보안 비휘발 저장소 | EEPROM | 보안 저장 구성요소 2세대 |
| AES 엔진 | DPA 대책·잠금 가능 시드 비트 | DPA 대책·잠금 가능 시드 비트 |
| 공개 키 가속기 (PKA) | OS 결합 키 | OS 결합 키·Boot Monitor |

Apple silicon 맥이 쓰는 데이터 보호 등급과 볼륨 키는 [키 계층 (VEK·KEK)](key-hierarchy.md)의 보호 등급 표와 함께 봅니다.

## 암호 입력 횟수 제한

맥을 켤 때 로그인 화면에서 받는 암호 시도는 10번까지이고, 몇 번 틀린 뒤부터는 다음 시도까지 기다려야 하는 시간이 점점 늘어 최대 8시간이 됩니다 [4]. 이 대기 시간은 Secure Enclave가 걸고, 대기 중에 재시동해도 풀리지 않고 그 구간의 타이머가 처음부터 다시 돌아갑니다 [4]. Secure Enclave가 거는 제한이라서, Secure Enclave가 없는 맥에는 이 절의 숫자를 그대로 옮기지 않습니다.

로그인 화면의 10번을 다 쓰면 recoveryOS로 재시동해 10번을 더 시도할 수 있습니다 [4]. 그것도 다 쓰면 설정해 둔 파일볼트 복구 수단(iCloud 복구, 파일볼트 복구 키, 기관 복구 키)으로 10번을 더 시도할 수 있고, 이렇게 더해지는 시도는 최대 30번입니다 [4]. Apple 문장만으로는 30번이 복구 수단마다 10번씩인지 분명하지 않은데, SUMURI 지침서는 복구 수단마다 10번씩, 모두 최대 30번으로 봅니다 [7]. 더해진 시도까지 다 쓰면 Secure Enclave가 볼륨 복호와 암호 확인 요청을 더는 처리하지 않고, 디스크의 데이터는 되살릴 수 없게 됩니다 [4]. 기다리면 풀리는 잠금이 아니라서, 현장에서 암호를 짐작해 넣어 보는 일은 증거를 없앨 수 있습니다.

로그인에 성공한 뒤에는 이 제한을 적용하지 않고, 재시동하면 다시 적용합니다 [4]. 악성 코드가 사용자 암호를 계속 틀리게 넣어 데이터를 영구히 잃게 만드는 일을 막으려는 설계입니다 [4].

### 로그인된 화면에서 확인하기

이미 로그인된 화면을 만났다면 파일볼트 상태와 암호를 아래 두 명령으로 확인합니다.

```sh
fdesetup status
dscl . -authonly <사용자>
```

`fdesetup status` 는 파일볼트의 현재 상태를 알려 주고, 상태를 보는 일부 명령은 root 없이 실행할 수 있습니다 [5]. SUMURI 지침서는 `status` 를 권한 없이 실행해 켜짐(On)·꺼짐(Off)을 확인하는 명령으로 봅니다 [7]. 나머지 `fdesetup` 명령은 [조사 절차 (Investigation Process)](../../../03-techniques/process-acquisition/investigation-process.md)에서 다룹니다.

`dscl . -authonly` 는 지정한 사용자의 암호가 맞는지 확인하고, 명령줄에 암호를 주지 않으면 프롬프트를 띄워 암호를 받습니다 [6]. SUMURI 지침서는 암호가 맞으면 아무것도 출력하지 않고 틀리면 `eDSAuthFailed` 가 나온다고 보고, 로그인된 세션에서는 위 제한을 적용하지 않으니 이 확인이 시도 횟수를 쓰지 않는다고 봅니다 [7].

암호는 명령줄 인자로 넣지 않고 프롬프트에 입력합니다. 명령줄에 넣으면 셸 기록에 남고 [7], 프로세스 실행 기록에도 암호 문자열이 남을 수 있습니다([정보 탈취 악성 코드 (Infostealer)](../../../04-scenarios/incident/infostealer.md) 참고). 확인은 한 번만 하고, 실행한 명령과 시각, 결과를 현장 기록에 남깁니다 [7].

## 포렌식에서 중요한 점

T2·Apple silicon 맥에서 떼어 낸 저장 매체는 직접 대입 공격(brute-force)으로부터 보호됩니다 [1]. UID는 Secure Enclave 밖으로 나오지 않고 [3], VEK는 파일볼트를 끈 상태에서도 UID로 보호됩니다 [1]. 두 사실을 합치면 이 맥들의 내장 디스크는 칩오프나 디스크 단독 이미지만으로는 원래 기기 없이 풀 수 없다고 볼 수 있습니다. 이 결론은 추론이고 Apple이 한 문장으로 밝힌 사실이 아니라서, 보고서에 쓸 때도 추론이라고 밝힙니다.

이런 맥을 켜진 상태로 만났다면 끄기 전에 무엇을 먼저 확보할지 판단해야 하고, 켜진 기기를 다루는 법은 [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md), 확보 방식 선택은 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md), 잠긴 볼륨을 만났을 때의 판단은 [암호화된 증거 다루기 (Encrypted Evidence)](../../../03-techniques/analysis/encrypted-evidence/index.md)에서 다룹니다. 기기에 T2 칩이 있는지, Apple silicon인지는 [컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)](../../../02-artifacts/system-account/computer-name-hardware.md)에서 먼저 확인합니다.

## 함정

"파일볼트가 꺼져 있다" 는 사실이 "디스크가 평문이다" 를 뜻하지 않습니다. T2·Apple silicon 맥은 파일볼트를 켜지 않아도 볼륨이 암호화돼 있고, 차이는 KEK에 사용자 암호가 더해지느냐입니다 [1].

카운터 락박스의 구조 [3]만으로 맥의 파일볼트 시도 한도를 판단하지 않습니다. 맥에서 암호를 몇 번 틀리면 대기 시간이 걸리고 데이터를 잃는지는 위 "암호 입력 횟수 제한" 절에서 Apple이 밝힌 숫자로 판단합니다 [4].

APFS 명세 [2]는 2020-06-22 판이고 Apple silicon 언급이 없으며, 하드웨어 암호화 방식 자체도 설명하지 않습니다. 명세의 소프트웨어 복호 절차를 T2·Apple silicon 내장 디스크에 그대로 적용할 수 있다고 보지 않습니다.

## 참고 문헌

1. Apple Platform Security — Volume encryption with FileVault in macOS — https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/web
2. Apple, Apple File System Reference (2020-06-22 판, PDF) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
3. Apple Platform Security — The Secure Enclave — https://support.apple.com/guide/security/secure-enclave-sec59b0b31ff/web
4. Apple Platform Security — Passcodes and passwords (2024-12-19 판) — https://support.apple.com/guide/security/passcodes-and-passwords-sec20230a10d/web
5. fdesetup(8) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/fdesetup.8.html
6. dscl(1) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/dscl.1.html
7. SUMURI, Mac Forensics Best Practices Guide, 2026 Edition (2026-09) — https://sumuri.com/
