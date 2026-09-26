---
title: "DPAPI 동작 원리"
parent: "DPAPI 구조"
grand_parent: "기반 · 암호 보호"
nav_order: 550
---

# DPAPI 동작 원리 (Protect·Unprotect)

> 위치: [DPAPI 구조 (Data Protection API)](index.md) > Protect·Unprotect 동작

DPAPI 는 CryptProtectData 함수로 데이터를 암호로 감싸고, CryptUnprotectData 함수로 다시 풉니다.
보호의 뿌리는 사용자의 로그온 자격증명, 보통은 사용자 암호의 해시입니다.
같은 자격증명을 쓴 같은 사용자만, 대개 같은 컴퓨터에서만 다시 풀 수 있습니다.

> 이 글은 DPAPI 가 데이터를 어떻게 감싸고 어떻게 푸는지를 설명합니다.
> 열쇠 계층 전체 그림과 디스크에 남는 파일 목록은 [DPAPI 구조 허브](index.md) 에 있습니다.

## 두 함수가 하는 일

CryptProtectData 는 평문을 받아 속을 알 수 없는(opaque) 보호 블롭을 돌려주고, CryptUnprotectData 는 그 반대로 보호 블롭을 받아 평문을 돌려줍니다. 두 함수는 Crypt32.dll 안에 있고, 부르면 로컬 RPC 로 LSA (Local Security Authority) 를 부릅니다. 이 RPC 는 네트워크로 나가지 않으며 데이터는 그 컴퓨터 안에 남습니다. 최소 지원 버전은 클라이언트 Windows XP, 서버 Windows Server 2003 이고, DPAPI 서비스 자체는 Windows 2000 부터 들어왔습니다.

블롭 자체의 바이트 구조는 [DPAPI 블롭 구조](dpapi-blob.md) 에서 다룹니다.

## CryptProtectData 매개변수

매개변수는 아래 순서로 넣습니다.

| 순서 | 이름 | 뜻 |
|---|---|---|
| 1 | pDataIn | 보호할 평문 |
| 2 | szDataDescr | 설명 문자열. 블롭에 같이 저장됩니다. NULL 을 줄 수 있습니다 |
| 3 | pOptionalEntropy | 추가 엔트로피. NULL 을 줄 수 있습니다 |
| 4 | pvReserved | 반드시 NULL |
| 5 | pPromptStruct | 프롬프트 설정 |
| 6 | dwFlags | 아래 플래그 표 |
| 7 | pDataOut | 결과 블롭 |

- 결과 pDataOut 의 pbData 는 다 쓴 뒤 LocalFree 로 풀어 줍니다.

### 추가 엔트로피 (pOptionalEntropy)

보호할 때 어떤 값을 추가 엔트로피로 넣으면 풀 때도 같은 값을 넣어야 합니다. 이 값은 키를 더 강하게 만들지는 않고, 같은 사용자의 다른 앱이 함부로 풀지 못하게 막는 용도입니다. 그래서 앱마다 자기만 아는 상수를 넣는 경우가 많습니다.

### dwFlags

앱이 쓸 수 있는 플래그입니다.

| 플래그 | 뜻 |
|---|---|
| CRYPTPROTECT_LOCAL_MACHINE | 데이터를 사용자가 아니라 그 컴퓨터에 묶습니다. 그 컴퓨터의 아무 사용자나 풀 수 있습니다 |
| CRYPTPROTECT_UI_FORBIDDEN | UI 를 금지합니다. UI 가 필요하면 실패하고 GetLastError 가 ERROR_PASSWORD_RESTRICTION 을 돌려줍니다 |
| CRYPTPROTECT_AUDIT | 보호·복호 때 감사 기록을 남깁니다. szDataDescr 이 NULL 도 아니고 빈 문자열도 아닐 때만 남습니다 |

CryptUnprotectData 에는 아래 플래그도 있습니다.

| 플래그 | 뜻 |
|---|---|
| CRYPTPROTECT_VERIFY_PROTECTION | 그 컴퓨터의 기본 보호 수준이 블롭의 보호 수준보다 높으면 CRYPT_I_NEW_PROTECTION_REQUIRED 를 돌려줍니다. 다시 보호하라는 뜻입니다 |

Windows XP 기준으로 아래 플래그는 LSA 스레드 전용입니다. 일반 앱은 쓰지 못합니다.

| 플래그 | 뜻 |
|---|---|
| CRYPTPROTECT_SYSTEM | 이 플래그로 보호한 것은 이 플래그로만 풉니다 |
| CRYPTPROTECT_CRED_SYNC | 실제로 암호화하지 않습니다. 마스터키를 다시 읽어 메모리에서 다시 암호화합니다. 암호 변경을 반영할 때 씁니다 |

### 프롬프트 흐름

pPromptStruct 로 화면에 뜨는 프롬프트 흐름은 쓰지 않기로 정해졌고, 2027년 2월에 없어집니다. pPromptStruct 가 NULL 이거나 dwPromptFlags 가 0 이면 화면을 띄우지 않는 경로를 씁니다. 프롬프트 흐름으로 보호했던 데이터는 그 뒤로 풀리지 않습니다.

## 누가 다시 풀 수 있나

보통은 데이터를 보호한 사용자와 같은 사용자만, 대개 그 사용자가 쓰던 같은 컴퓨터에서만 풉니다. 로밍 프로필 (Roaming Profile) 사용자는 네트워크의 다른 컴퓨터에서도 풀 수 있습니다.

## 세션키를 만드는 법

DPAPI 는 마스터키를 데이터 암호에 바로 쓰지 않습니다.
데이터마다 세션키 (블롭키) 를 새로 만듭니다.
아래는 Windows XP 기준 방식입니다. 난수 길이와 해시 알고리즘은 뒤 버전에서 달라집니다.

1. 16바이트 난수를 만듭니다.
2. 그 난수와 마스터키를 함께 SHA-1 로 해시합니다.
3. 추가 엔트로피와 선택 암호가 있으면 CryptHashData 로 그 해시에 덧붙입니다.
4. CryptDeriveKey 로 세션키를 얻습니다.

세션키는 저장하지 않고 블롭에는 위 16바이트 난수만 저장합니다. 그래서 마스터키를 알면 난수로 세션키를 다시 만들 수 있습니다.

무결성 보호도 함께 붙습니다.

블롭에 MAC (Message Authentication Code) 을 붙이며, Windows XP 기준으로는 HMAC(SHA-1) 입니다. 블롭이 바뀌었을 때 돌려주는 오류 코드는 일정하지 않고, 경우에 따라 깨진 결과를 돌려주며 성공할 수도 있습니다. 그래서 복호가 성공했다는 것만으로 블롭이 온전하다고 단정하지 않습니다.

## 읽는 법 — 블롭을 푸는 다섯 단계

복호 흐름은 다섯 단계입니다.

1. 블롭에서 마스터키 GUID 를 꺼냅니다.
2. 그 GUID 로 마스터키 파일을 찾아 salt 와 반복수를 얻습니다. 옛 암호로 암호화된 마스터키면 [CREDHIST](credhist.md) 를 풀어 맞는 SHA-1 을 찾습니다.
3. 그 SHA-1 과 salt·반복수로 Pre key 를 계산합니다.
4. Pre key 로 마스터키를 풉니다.
5. 마스터키와 블롭의 salt(추가 엔트로피가 있으면 그 값도)로 블롭키를 계산해 데이터를 풉니다.

- 마스터키 파일의 구조와 salt·반복수 자리는 [마스터키 파일](master-key-protect-sid.md) 에 있습니다.
- SYSTEM·머신 계정은 암호가 없어 2단계가 다릅니다. [시스템 DPAPI 키](dpapi-system.md) 를 봅니다.
- 오프라인에서 이 다섯 단계를 밟는 데 필요한 재료와 절차는 [오프라인 복호 재료와 절차](nt.md) 에 있습니다.

## 포렌식에서 중요한 점

- DPAPI 로 보호한 데이터를 풀려면 사용자 계정의 비밀 (암호나 그 해시) 이 있어야 하며, 데이터만 있으면 풀 수 없습니다. 그래서 보호된 데이터를 모을 때는 마스터키 파일도 함께 모읍니다.
- 추가 엔트로피를 쓴 앱의 데이터는 그 앱이 넣은 엔트로피 값을 알아야 풀립니다.
- CRYPTPROTECT_LOCAL_MACHINE 로 보호한 데이터는 사용자 암호가 아니라 그 컴퓨터의 비밀로 풀립니다.
- 어떤 사용자가 보호했는지는 블롭에 나와 있지 않습니다. 어느 사용자의 마스터키로 풀렸는지를 보고 알아냅니다.

## 함정

- **데이터 블롭만 모으고 마스터키 파일을 빼먹습니다.** 이러면 풀 재료가 없습니다.
- **추가 엔트로피를 잊습니다.** 엔트로피를 쓴 블롭은 그 값 없이는 풀리지 않습니다. 앱마다 값이 다릅니다.
- **사용자 DPAPI 와 머신 DPAPI 를 헷갈립니다.** LOCAL_MACHINE 로 보호한 것은 사용자 암호로 풀리지 않습니다.
- **RPC 라는 말을 네트워크 통신으로 오해합니다.** 이 RPC 는 로컬에서만 돕니다.

## 도구

아래 공개 도구는 예로만 듭니다. 한 도구의 결과에만 기대지 않습니다.

| 도구 | DPAPI 와 관련된 기능 |
|---|---|
| SharpDPAPI (공개 코드) | 마스터키와 블롭을 오프라인에서 푸는 흐름을 보여 줍니다 |
| DPAPImk2john 계열 (공개 코드) | 마스터키 파일에서 크래킹용 해시 문자열을 뽑습니다 |
| 헥스 편집기 | 블롭과 마스터키 파일의 바이트를 직접 읽습니다 |

## 참고 문헌

- Microsoft Learn, *CryptProtectData function (dpapi.h)* — https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata
- Microsoft (NAI Labs), *Windows Data Protection* (2001, Windows XP 기준) — https://learn.microsoft.com/en-us/previous-versions/ms995355(v=msdn.10)
- Elie Bursztein, Jean-Michel Picod, Ruben Sarfati, *Reversing DPAPI and Stealing Windows Secrets Offline*, USENIX WOOT 2010 — https://www.usenix.org/legacy/event/woot10/tech/full_papers/Burzstein.pdf
