# DPAPI 구조 (Data Protection API)

## 한 줄 요약

DPAPI 는 앱이 비밀을 암호로 감쌀 때 쓰는 운영체제 수준의 공통 서비스입니다.
보호의 뿌리는 사용자의 로그온 자격증명, 보통은 사용자 암호의 해시입니다.
그래서 DPAPI 로 보호한 데이터는 데이터만으로는 풀리지 않고, 마스터키 파일과 사용자 비밀이 함께 있어야 풀립니다.

## 왜 중요한가

- DPAPI 는 앱이 저마다 암호화를 새로 짜지 않도록 마련한 공통 보호 장치입니다.
- 무선 프로필 키와 일부 서비스 비밀이 DPAPI 로 보호됩니다.
- 그래서 이런 비밀을 오프라인에서 풀려면 DPAPI 의 열쇠 계층을 이해해야 합니다.
- DPAPI 는 CryptProtectData 함수로 감싸고 CryptUnprotectData 함수로 풉니다.
- 두 함수는 Crypt32.dll 에 있고, 부르면 로컬 RPC 로 LSA (Local Security Authority) 를 부릅니다.
- 이 RPC 는 네트워크로 나가지 않습니다. 데이터는 그 컴퓨터 안에 남습니다.
- DPAPI 서비스는 Windows 2000 부터 들어왔습니다. 지금 Microsoft 함수 문서가 적은 최소 지원 버전은 클라이언트 Windows XP, 서버 Windows Server 2003 입니다.

## 열쇠 계층

DPAPI 는 데이터를 사용자 암호로 바로 감싸지 않습니다. 열쇠를 여러 겹 거칩니다.

> 그림 자리: 사용자 암호 → Pre key → 마스터키(512비트 난수) → 블롭키(세션키) → 실제 데이터 로 이어지는 열쇠 계층. 각 단계에서 무엇을 무엇으로 감싸는지 화살표로 보여 주는 그림

- 사용자 암호(해시)에서 Pre key 를 만듭니다.
- Pre key 로 마스터키를 풉니다.
- 마스터키는 직접 암복호에 쓰지 않습니다. 512비트 난수이고, 여기서 데이터마다 블롭키(세션키)를 만듭니다.
- 블롭키로 실제 데이터를 풉니다.
- 스마트카드로 로그온하면 뿌리가 암호 해시가 아니라 다른 자격증명입니다.

## 한눈에 보기 — 디스크에 남는 것

DPAPI 는 보호 블롭 자체를 저장하지 않습니다. 블롭은 그 데이터를 만든 앱이 저장합니다. DPAPI 가 프로필과 시스템 영역에 남기는 것은 아래와 같습니다.

| 남는 것 | 위치 | 알려 주는 것 |
|---|---|---|
| 마스터키 파일 | `%APPDATA%\Microsoft\Protect\{SID}\{GUID}` | 블롭을 풀 512비트 마스터키를 사용자 암호로 감싼 것 |
| Preferred 파일 | 같은 폴더 | 지금 쓰는 마스터키 GUID 와 갱신 시각 |
| CREDHIST 파일 | 사용자 프로필의 `Microsoft\Protect` 폴더 아래 | 이전 암호들의 해시 사슬 |
| DPAPI_SYSTEM | SECURITY 하이브의 LSA 시크릿 | 머신·SYSTEM 계정 마스터키를 풀 재료 |
| 도메인 백업 본 | 마스터키 파일 안(도메인 가입 PC) | DC 개인키로 풀 두 번째 경로 |
| 보호 블롭 | 앱이 정한 파일 | 실제로 보호된 데이터 |

- 파일 구조는 대부분 공식 명세가 없습니다. 아래 하위 페이지의 바이트 구조는 역공학 자료로 확인한 것이며, 확인 범위는 Windows 7 까지입니다.
- SID·GUID 형식은 [윈도 식별자 형식](../../value-decoding/sid-guid-clsid-known-folder-id.md) 을 봅니다.

## 읽는 순서

아래 순서로 읽으면 데이터 한 조각이 어떻게 풀리는지 처음부터 끝까지 따라갈 수 있습니다.

1. [DPAPI 동작 원리 (Protect·Unprotect)](protect-unprotect.md) — 두 함수가 하는 일, 매개변수와 플래그, 블롭을 푸는 다섯 단계를 다룹니다.
2. [DPAPI 블롭 구조 (DPAPI Blob)](dpapi-blob.md) — 앱이 저장하는 보호 블롭의 필드 순서와 알고리즘 ID 를 헥스로 따라갑니다.
3. [마스터키 파일 (Master Key·Protect\SID)](master-key-protect-sid.md) — 마스터키를 사용자 암호로 감싼 파일의 구조와 버전별 알고리즘을 다룹니다.
4. [비밀번호 변경 기록 (CREDHIST)](credhist.md) — 암호를 바꿀 때마다 자라는 해시 사슬과 그 쓰임을 다룹니다.
5. [시스템 DPAPI 키 (DPAPI_SYSTEM)](dpapi-system.md) — 암호가 없는 SYSTEM·머신 계정이 마스터키를 무엇으로 푸는지 다룹니다.
6. [도메인 백업 키 (Domain Backup Key)](domain-backup-key.md) — 도메인 가입 PC 의 두 번째 복호 경로를 다룹니다.
7. [오프라인 복호 재료와 절차 (비밀번호·NT 해시·백업 키)](nt.md) — 꺼진 디스크에서 블롭을 풀 때 무엇을 모으고 어디를 조심하는지 다룹니다.

## 함께 볼 페이지

- [Wi-Fi 프로필 (WLAN Profiles)](../../../02-artifacts/network/wlan-profiles.md) — 무선 키의 오프라인 복호가 DPAPI 열쇠 계층을 씁니다.
- [자격 증명 관리자와 볼트 (Credential Manager·Windows Vault)](../../../02-artifacts/credentials/credential-manager-windows-vault.md) — 저장된 자격증명이 DPAPI 로 보호됩니다.
- [레지스트리 속 비밀번호 정보 (SAM·SECURITY)](../../../02-artifacts/credentials/sam-security/index.md) — 사용자 암호 해시와 DPAPI_SYSTEM 이 여기 있습니다.
- [윈도 식별자 형식 (SID·GUID·CLSID·KnownFolderID)](../../value-decoding/sid-guid-clsid-known-folder-id.md) — 마스터키 폴더 이름과 파일 이름을 읽습니다.
- [문자 인코딩 (UTF-16LE·UTF-8·CP949)](../../value-decoding/utf-16le-utf-8-cp949.md) — 암호를 해시하기 전 UTF-16LE 로 바꾸는 이유를 봅니다.
- [암호화 증거 다루기 (Encrypted Evidence)](../../../03-techniques/analysis/encrypted-evidence/index.md) — 풀 수 있는 것과 없는 것을 나누는 실무 절차입니다.

## 참고 문헌

- Microsoft Learn, *CryptProtectData function (dpapi.h)* — https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata
- Microsoft (NAI Labs), *Windows Data Protection* (2001, Windows XP 기준) — https://learn.microsoft.com/en-us/previous-versions/ms995355(v=msdn.10)
- Elie Bursztein, Jean-Michel Picod, Ruben Sarfati, *Reversing DPAPI and Stealing Windows Secrets Offline*, USENIX WOOT 2010 — https://www.usenix.org/legacy/event/woot10/tech/full_papers/Burzstein.pdf
