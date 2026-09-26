---
title: "마스터키 파일"
parent: "DPAPI 구조"
grand_parent: "기반 · 암호 보호"
nav_order: 570
---

# 마스터키 파일 (Master Key·Protect\SID)

> 위치: [DPAPI 구조 (Data Protection API)](index.md) > 마스터키 파일

## 한 줄 요약

마스터키 (Master Key) 는 DPAPI 블롭을 풀 세션키를 만들어 내는 512비트 난수 비밀입니다.
마스터키 자체는 사용자 암호에서 나온 열쇠로 암호화되어 디스크의 마스터키 파일에 들어 있어서, 마스터키 파일과 사용자 암호가 있어야 블롭을 풀 수 있습니다.

> 블롭에서 마스터키 GUID 를 찾는 법은 [DPAPI 블롭 구조](dpapi-blob.md) 에 있습니다.
> 마스터키를 풀어 블롭을 여는 전체 흐름은 [DPAPI 동작 원리](protect-unprotect.md) 에 있습니다.

## 무엇을 담나 · 왜 생기나

마스터키는 512비트 난수이고, 데이터 암복호에 직접 쓰지 않고 세션키를 만드는 데만 씁니다. Windows 는 마스터키를 3개월마다 새로 만들며 이 주기는 코드에 박혀 있습니다. 옛 마스터키는 지우지 않고 사용자 프로필에 계속 보관하는데, 어떤 블롭이 어떤 마스터키를 썼는지 미리 알 방법이 없기 때문입니다.

## 위치와 파일

- 사용자 마스터키 파일 위치는 `%APPDATA%\Microsoft\Protect\{SID}\{GUID}` 입니다.
- 풀어 쓰면 `C:\Users\<사용자>\AppData\Roaming\Microsoft\Protect\S-1-5-21-...\{GUID}` 같은 경로입니다.
- 폴더 이름의 {SID} 는 그 사용자의 SID 입니다.
- 파일 이름의 {GUID} 는 마스터키 ID 입니다.
- SID·GUID 형식은 [윈도 식별자 형식](../../value-decoding/sid-guid-clsid-known-folder-id.md) 을 봅니다.
- 이 폴더에는 마스터키 파일 여러 개와 Preferred 파일이 함께 있습니다.
- [CREDHIST](credhist.md) 파일도 같은 `Microsoft\Protect` 폴더 아래에 있습니다.
- 머신·SYSTEM 계정의 마스터키는 다른 곳에 있습니다. [시스템 DPAPI 키](dpapi-system.md) 를 봅니다.

### Preferred 파일

Preferred 파일은 지금 쓰는 마스터키의 GUID 를 가리키며, 마스터키를 언제 새로 만들지 판단하는 타임스탬프도 함께 들어 있습니다. 이 타임스탬프에는 HMAC 무결성 보호가 없어서 손대면 티가 나지 않습니다.

## 구조

공식 명세는 없습니다. 아래 구조는 역공학 자료(Windows 7 기준)를 따릅니다.

마스터키 파일은 다섯 부분으로 이뤄집니다.

| 부분 | 내용 |
|---|---|
| 헤더 | dwMagic, szKeyGUID (36자, UTF-16LE 문자열, 마스터키 ID), 각 블록 길이 |
| keys info | dwUnknown, cbMasterKey, cbMysteryKey, dwHMACLen (HMAC-SHA1 이면 0x14) |
| 마스터키 블록 | 아래 표 |
| Mystery key 블록 | 정규 복호에서는 쓰지 않습니다. 256비트라 Windows 2000 RC4 호환용으로 추정합니다 |
| 푸터 | dwMagic, credHist GUID (16바이트) |

### 마스터키 블록

마스터키 블록의 필드입니다.

| 필드 | 뜻 |
|---|---|
| dwMagic | 서명 |
| pbSalt (16바이트) | PBKDF2 salt |
| cbIteration | PBKDF2 반복수 |
| idMACAlgo | MAC 해시 알고리즘 ID |
| idCipherAlgo | 마스터키 암호 알고리즘 ID |
| pbCipheredKey | 암호화된 마스터키 + HMAC |

salt 와 반복수는 비밀이 아니며 마스터키 파일에 평문으로 들어 있습니다. 마스터키에도 변조 방지 HMAC(SHA-1) 이 붙습니다.


- 헤더 필드 이름은 자료마다 표기가 다릅니다. dwVersion (Windows 2000 이면 1, 이후면 2), dwPolicy (해시 알고리즘을 정하는 플래그), 각 키 크기 필드로 적는 자료도 있습니다[3].
- 공개 복호 코드(impacket 의 MasterKeyFile)는 헤더 뒤 블록을 마스터키, 백업 키, CREDHIST, 도메인 키 순으로 읽고, 헤더에 각 블록 길이(MasterKeyLen·BackupKeyLen·CredHistLen·DomainKeyLen)를 둡니다[5]. 위 표의 Mystery key 는 이 백업 키 자리에, 푸터는 CREDHIST 블록 자리에 해당합니다.

### 푸터의 credHist GUID

푸터의 credHist GUID 는 이 마스터키를 암호화할 때 쓴 암호의 GUID 이고, CREDHIST 파일 안의 GUID 와 이어집니다[2]. SYSTEM 계정은 암호가 없어 이 GUID 가 0x00 입니다.

## 마스터키를 푸는 흐름

로그온 암호에서 마스터키를 푸는 순서입니다.

1. 로그온 암호를 SHA-1 로 해시합니다. 이 해시가 로그온 자격증명입니다.
2. 그 해시로 Pre key 를 만듭니다. 이 자리에 사용자 SID 가 함께 들어갑니다[2].
3. Pre key 와 salt(16바이트)·반복수로 PBKDF2 를 돌려 대칭 키를 얻습니다.
4. 그 대칭 키로 마스터키를 풉니다. 대칭 암호는 버전에 따라 3DES 또는 AES 입니다.

- 옛 암호로 암호화된 마스터키면, 먼저 [CREDHIST](credhist.md) 를 풀어 그 옛 암호의 SHA-1 을 얻습니다.
- 도메인 계정은 SHA-1 대신 NT 해시(MD4)를 씁니다.
- 오프라인에서 이 흐름을 밟는 재료 목록은 [오프라인 복호 재료와 절차](nt.md) 에 있습니다.

## 위치와 버전별 차이

마스터키를 암호화하는 알고리즘은 Windows 버전마다 다릅니다.

| Windows | 암호 | MAC 해시 | PBKDF2 반복수 |
|---|---|---|---|
| 2000 | RC4 | SHA-1 | 1회 |
| XP | 3DES-CBC | HMAC-SHA1 | 4000회 |
| Vista | 3DES-CBC | HMAC-SHA1 | 24000회 |
| 7 | AES256-CBC | HMAC-SHA512 | 가변(약 5600) |

- 반복수는 레지스트리에서 조정할 수 있습니다. 값은 `HKEY_LOCAL_MACHINE\Software\Microsoft\Cryptography\Protect\Providers\{GUID}` 의 MasterKeyIterationCount 입니다.
- Windows XP 기준으로 이 값은 4000 아래로 내릴 수 없습니다[1].
- Windows 8·10·11 의 알고리즘은 실제 데이터로 확인해야 합니다.

## 읽는 법 — 헥스로 살펴보기

아래 바이트는 **명세로 만든 예시**입니다. 실제 데이터에서 나온 값이 아닙니다. `..` 은 이 설명에 필요 없는 바이트입니다.

마스터키 블록에서 salt 와 반복수를 찾는 과정을 보여 줍니다.

```
마스터키 파일의 마스터키 블록 일부 (명세로 만든 예시)
00000000  (dwMagic)   A1 B2 C3 D4  E5 F6 07 18  29 3A 4B 5C   .......)... salt 16바이트
00000010  6D 7E 8F 90  E0 15 00 00  0E 80 00 00  10 66 00 00   .....(반복수)(MAC)(암호)
```

- 위 예시에서 salt 는 오프셋 0x04 부터 16바이트입니다.
- 그 다음 4바이트 0xE0 0x15 0x00 0x00 은 반복수입니다. 리틀 엔디언으로 0x15E0, 곧 5600 입니다.
- 이 값은 Windows 7 규칙과 맞습니다.
- 기본값만 보면 4000 은 XP, 24000 은 Vista 규칙입니다. 반복수는 레지스트리로 바꿀 수 있어 버전 판단의 보조 근거로만 씁니다.

실제 오프셋은 앞쪽 헤더·keys info 길이에 따라 달라집니다. 위 숫자는 배치를 보여 주는 예시입니다.

## 포렌식에서 중요한 점

- **알 수 있는 것**: 이 파일이 어느 사용자의 것인지. 폴더 이름의 SID 로 알 수 있습니다.
- **알 수 있는 것**: 마스터키를 어떤 알고리즘·반복수로 감쌌는지.
- **알 수 있는 것**: 이 마스터키를 어느 암호(GUID)로 감쌌는지. 푸터의 credHist GUID 로 알 수 있습니다.
- **알 수 없는 것**: 마스터키 자체. 사용자 암호나 그 해시 없이는 풀리지 않습니다.
- **알 수 없는 것**: 이 키를 만든 정확한 시각. 파일 안에는 신뢰할 시각 필드가 없습니다.
- 마스터키 파일을 모을 때는 같은 폴더의 Preferred·CREDHIST 파일도 함께 모읍니다.

## 시각 해석

Preferred 파일의 타임스탬프는 마스터키를 새로 만들 시점을 판단하는 데 씁니다[2]. 이 값이 만든 시각인지 만료 시각인지는 실제 데이터로 확인해야 합니다. 이 타임스탬프에는 HMAC 보호가 없어 조작될 수 있습니다.

`Protect\{SID}\{GUID}` 파일의 파일 시스템 시각(만든 시각·바꾼 시각)이 무엇을 뜻하는지도 공개된 분석 자료가 없습니다. 그래서 이 시각을 마스터키 생성 시각의 근거로 쓸 때는 이 한계를 보고서에 함께 적습니다.

## 함정

- **옛 마스터키를 지운다고 봅니다.** Windows 는 옛 마스터키를 지우지 않고 남깁니다.
- **마스터키 하나만 모읍니다.** 블롭이 옛 마스터키를 썼을 수 있습니다. 폴더 전체를 모읍니다.
- **반복수를 버전 판단에만 씁니다.** 반복수는 레지스트리로 바꿀 수 있습니다.
- **Preferred 타임스탬프를 확정 시각으로 씁니다.** 이 값은 무결성 보호가 없습니다.
- **로컬 계정과 도메인 계정을 같게 봅니다.** 로컬은 SHA-1, 도메인은 NT 해시(MD4)로 Pre key 를 만듭니다.

## 도구

아래 공개 도구는 예로만 듭니다.

| 도구 | 마스터키와 관련된 기능 |
|---|---|
| SharpDPAPI (공개 코드) | 마스터키 파일을 읽고 암호·백업키로 복호를 시도합니다 |
| DPAPImk2john 계열 (공개 코드) | 마스터키 파일에서 크래킹용 해시 문자열을 뽑습니다 |
| 헥스 편집기 | 다섯 부분 구조를 따라가며 salt·반복수를 직접 읽습니다 |

## 참고 문헌

- Microsoft (NAI Labs), *Windows Data Protection* (2001, Windows XP 기준) — https://learn.microsoft.com/en-us/previous-versions/ms995355(v=msdn.10)
- Elie Bursztein, Jean-Michel Picod, Ruben Sarfati, *Reversing DPAPI and Stealing Windows Secrets Offline*, USENIX WOOT 2010 — https://www.usenix.org/legacy/event/woot10/tech/full_papers/Burzstein.pdf
- Passcape Software, *Windows DPAPI* (마스터키·CREDHIST 구조) — https://www.passcape.com/index.php?section=docsys&cmd=details&id=28
- GhostPack, *SharpDPAPI* (경로·복호 흐름) — https://github.com/GhostPack/SharpDPAPI
- impacket, *dpapi.py* (MasterKeyFile·MasterKey 구조체) — https://github.com/fortra/impacket/blob/master/impacket/dpapi.py
