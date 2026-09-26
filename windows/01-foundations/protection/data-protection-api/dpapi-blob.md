---
title: "DPAPI 블롭 구조"
parent: "DPAPI 구조"
grand_parent: "기반 · 암호 보호"
nav_order: 560
---

# DPAPI 블롭 구조 (DPAPI Blob)

> 위치: [DPAPI 구조 (Data Protection API)](index.md) > DPAPI Blob

## 한 줄 요약

DPAPI 블롭 (Blob) 은 암호문과 그것을 풀 메타데이터를 한 덩어리에 담은 구조입니다.
DPAPI 는 이 블롭을 스스로 저장하지 않고 블롭을 받은 앱이 저장하기 때문에, 블롭은 앱마다 다른 파일이나 레지스트리 값 안에 들어 있습니다.

> 블롭을 실제로 푸는 다섯 단계는 [DPAPI 동작 원리](protect-unprotect.md) 에 있습니다.
> 이 글은 블롭의 바이트가 어떻게 놓이는지를 다룹니다.

## 이 구조가 나오는 곳

브라우저에 저장한 비밀번호, 자격 증명 관리자 항목, 무선 프로필 키 같은 값이 이 블롭으로 감싸여 있습니다. 앱이 CryptProtectData 를 부르면 이 블롭을 돌려받고, 자기 파일이나 레지스트리에 그대로 저장합니다.

자격 증명 저장 위치는 [자격 증명 관리자와 볼트](../../../02-artifacts/credentials/credential-manager-windows-vault.md) 를 봅니다.

## 구조

### 공식 명세가 없다는 점

공식 문서에서 블롭은 속을 알 수 없는(opaque) 구조일 뿐이고, 내부 바이트 배치는 나와 있지 않습니다[1]. 아래 필드 순서는 공식 명세가 아니라 역공학 자료(Windows 7 기준)를 따릅니다[2][3]. Windows 8·10·11 에서는 다를 수 있으니 검체에서 확인합니다.

### 필드 순서

블롭의 필드는 아래 순서로 놓입니다[3]. 길이 칸이 앞에 오는 가변 필드가 많습니다.

| 순서 | 필드 | 뜻 |
|---|---|---|
| 1 | Version | 버전 (4바이트) |
| 2 | GuidCredential | 제공자 GUID (16바이트) |
| 3 | MasterKeyVersion | 마스터키 버전 (4바이트) |
| 4 | GuidMasterKey | 이 블롭을 감싼 마스터키의 GUID (16바이트) |
| 5 | Flags | 플래그 (4바이트) |
| 6 | DescriptionLen · Description | 설명 문자열 길이와 문자열 (UTF-16LE) |
| 7 | CryptAlgo · CryptAlgoLen | 암호 알고리즘 ID 와 키 길이 |
| 8 | SaltLen · Salt | salt 길이와 salt |
| 9 | HMacKeyLen · HMacKey | HMAC 키 길이와 값 |
| 10 | HashAlgo · HashAlgoLen | 해시 알고리즘 ID 와 길이 |
| 11 | HMac 길이 · HMac | 두 번째 HMAC 값 |
| 12 | DataLen · Data | 암호문 길이와 암호문 |
| 13 | SignLen · Sign | 블롭 무결성 서명 |

같은 구조를 cbProviders, arrProviders, arrKeys, idCipherAlgo, idHashAlgo, pbSalt, pbEncData, pbHMAC 로 줄여 부르기도 합니다[2]. arrKeys 가 마스터키 ID 를 여러 개 담을 수 있고 도메인 백업키나 호환 키를 위한 것이라는 추정이 있지만[2], 공개 복호 코드는 마스터키 GUID 를 한 칸(16바이트)만 읽습니다[3].

GUID 형식 자체는 [윈도 식별자 형식](../../value-decoding/sid-guid-clsid-known-folder-id.md) 을 봅니다.

### 무결성 값이 둘이라는 점

끝의 Sign 은 블롭 전체가 바뀌지 않았는지 확인합니다. 이와 별도로 키가 바뀌지 않았는지 확인하는 두 번째 HMAC 이 키로 암호화된 채 들어 있습니다[2].

### 알고리즘 ID 읽기

- CryptAlgo·HashAlgo 는 Microsoft Algorithm ID (ALG_ID) 표를 따릅니다.
- 0x80xx 는 해시입니다. 예로 0x800e 는 CALG_SHA_512, 0x8004 는 CALG_SHA1 입니다.
- 0x66xx 로 시작하는 값은 블록 암호입니다. 예로 0x6610 은 CALG_AES_256 입니다.
- 이 값으로 블롭이 어느 버전 규칙으로 만들어졌는지 짐작합니다.

### 설명 문자열

개발자가 CryptProtectData 에 설명을 NULL 로 주면 DPAPI 는 빈 문자열을 저장합니다[2]. 이 빈 문자열은 UTF-16LE 의 L"" 이고 크기가 2바이트입니다.

문자 인코딩은 [문자 인코딩](../../value-decoding/utf-16le-utf-8-cp949.md) 을 봅니다.

### 크기와 해시 범위

- Windows XP 기준으로 블롭 크기는 "708비트 + 설명·암호문·MAC 길이" 이고, 블롭 전체를 HMAC(SHA-1) 로 해시합니다[1].
- 뒤 버전의 블롭은 해시 알고리즘이 다를 수 있습니다. HashAlgo 칸을 봅니다.

## 읽는 법 — 헥스로 살펴보기

아래 바이트는 **명세로 만든 예시**입니다. 실제 검체에서 나온 값이 아닙니다. `..` 은 이 설명에 필요 없는 바이트입니다.

블롭 앞쪽에서 마스터키 GUID 와 암호 알고리즘 ID 를 찾는 과정을 보여 줍니다. 설명 문자열은 NULL 로 준 경우(빈 문자열, 2바이트)로 잡았습니다.

```
어느 앱이 저장한 DPAPI 블롭 앞부분 (명세로 만든 예시)
00000000  01 00 00 00 D0 8C 9D DF  01 15 D1 11 8C 7A 00 C0
00000010  4F C2 97 EB 01 00 00 00  (마스터키 GUID 16바이트 ....
00000020  .......................  ....................... )
00000030  00 00 10 66 00 00 00 01  00 00 .. .. .. .. .. ..
```

- 오프셋 0x00 의 01 00 00 00 은 Version 입니다.
- 오프셋 0x04 부터 16바이트가 제공자 GUID 입니다. 이 예시에서는 {DF9D8CD0-1501-11D1-8C7A-00C04FC297EB} 입니다.
- 오프셋 0x14 의 4바이트는 MasterKeyVersion 입니다.
- 오프셋 0x18 부터 16바이트가 마스터키 GUID 입니다. 이 GUID 로 마스터키 파일을 찾습니다.
- 오프셋 0x28 은 Flags, 0x2C 는 설명 길이 (여기서는 02 00 00 00) 입니다. 이 줄은 위 예시에서 생략했습니다.
- 오프셋 0x30 의 00 00 은 빈 설명 문자열입니다.
- 오프셋 0x32 의 10 66 00 00 은 CryptAlgo 입니다. 리틀 엔디언으로 0x6610, 곧 AES-256 입니다.
- 그 뒤 00 01 00 00 은 키 길이 0x100, 곧 256비트입니다.

앞쪽 0x2C 까지는 자리가 고정이지만, 설명 문자열부터는 길이가 달라집니다. 길이 칸을 먼저 읽어 다음 필드 위치를 계산하며 나아갑니다. HashAlgo 는 salt 와 HMAC 키 뒤에 있습니다.

## 포렌식에서 중요한 점

- **말해 주는 것**: 이 블롭이 어느 마스터키 GUID 로 암호화되었는지. GuidMasterKey 로 알 수 있습니다.
- **말해 주는 것**: 어떤 암호·해시 알고리즘을 썼는지. 알고리즘 ID 로 알 수 있습니다.
- **말해 주지 못하는 것**: 블롭 안의 평문. 마스터키 없이는 풀리지 않습니다.
- **말해 주지 못하는 것**: 누가 언제 이 블롭을 만들었는지. 블롭에는 시각 칸이 없습니다.
- 블롭에서 얻은 마스터키 GUID 로 [마스터키 파일](master-key-protect-sid.md) 을 찾아 짝을 맞춥니다.

## 함정

- **설명 문자열 뒤까지 고정 오프셋을 가정합니다.** 설명·salt·HMAC 키 길이에 따라 뒤 필드 위치가 달라집니다.
- **Windows 7 기준 구조를 최신 버전에 그대로 적용합니다.** Windows 8 이후에는 구조가 다를 수 있어 검체에서 확인합니다.
- **무결성 값이 하나뿐이라고 봅니다.** 블롭 끝의 Sign 과 별도로 HMAC 값이 하나 더 들어 있습니다.
- **블롭이 곧 저장 파일이라고 봅니다.** DPAPI 는 블롭을 저장하지 않습니다. 앱마다 저장 위치가 다릅니다.

## 도구

아래 공개 도구는 예로만 듭니다.

| 도구 | 블롭과 관련된 기능 |
|---|---|
| SharpDPAPI (공개 코드) | 블롭에서 마스터키 GUID·알고리즘을 읽고 복호를 시도합니다 |
| 헥스 편집기 | 위 필드 순서대로 길이 칸을 따라가며 직접 읽습니다 |

## 참고 문헌

- Microsoft (NAI Labs), *Windows Data Protection* (2001, Windows XP 기준) — https://learn.microsoft.com/en-us/previous-versions/ms995355(v=msdn.10)
- Elie Bursztein, Jean-Michel Picod, Ruben Sarfati, *Reversing DPAPI and Stealing Windows Secrets Offline*, USENIX WOOT 2010 — https://www.usenix.org/legacy/event/woot10/tech/full_papers/Burzstein.pdf
- impacket, *dpapi.py* (DPAPI_BLOB·MasterKeyFile·CREDHIST 구조체) — https://github.com/fortra/impacket/blob/master/impacket/dpapi.py
