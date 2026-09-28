---
title: "오프라인 복호 재료와 절차"
parent: "DPAPI 구조"
grand_parent: "기반 · 암호 보호"
nav_order: 610
---

# 오프라인 복호 재료와 절차 (비밀번호·NT 해시·백업 키)

라이브 PC 에서는 DPAPI 가 알아서 마스터키를 풀어 줍니다.
꺼진 디스크 이미지에서 블롭을 풀려면 마스터키 파일, 사용자 암호(또는 그 해시), 사용자 SID 를 직접 모아야 합니다.
도메인 계정은 사용자 암호 대신 DC 의 백업 개인키로도 풀립니다.

> 마스터키를 푸는 흐름 자체는 [DPAPI 동작 원리](protect-unprotect.md) 의 다섯 단계와 같습니다.
> 이 글은 그 흐름을 오프라인에서 밟을 때 무엇을 모으고 어디를 조심하는지를 다룹니다.

## 필요한 재료

블롭 하나를 오프라인에서 풀려면 네 가지가 필요합니다.

| 재료 | 어디서 얻나 |
|---|---|
| 마스터키 파일 | 사용자 프로필의 `Protect\{SID}` 폴더. [마스터키 파일](master-key-protect-sid.md) 참고 |
| 사용자 로그온 암호 또는 그 해시 | 아래 "암호 대신 해시" 참고 |
| 사용자 SID | 마스터키 폴더 이름. [윈도 식별자 형식](../../value-decoding/sid-guid-clsid-known-folder-id.md) 참고 |
| 풀려는 블롭 | 그 블롭을 저장한 앱의 파일. [DPAPI 블롭](dpapi-blob.md) 참고 |

도메인 계정은 사용자 암호 대신 DC 의 백업 개인키로도 마스터키를 풀 수 있어서, 사용자 암호를 모르는 사건이라도 도메인이면 복호 길이 남아 있을 수 있습니다. [도메인 백업 키](domain-backup-key.md) 를 봅니다.

## 암호 대신 해시 — 로컬과 도메인이 다릅니다

계정 종류에 따라 Pre key 를 만드는 재료가 다릅니다.

| 계정 종류 | Pre key 재료 |
|---|---|
| 로컬 계정 | 사용자 암호(UTF-16LE)의 SHA-1 해시 |
| 도메인 계정 | 사용자 암호의 NT 해시(MD4) |

그래서 암호 원문이 없어도 맞는 해시만 있으면 마스터키를 풀 수 있습니다. 사용자 SID 는 Pre key 를 만들 때 들어가는데, 위 해시를 키로 삼아 SID 문자열(UTF-16LE, 끝에 널 문자)을 HMAC-SHA1 합니다[4]. 그래서 해시가 맞아도 SID 가 틀리면 마스터키가 풀리지 않습니다.

보호된 사용자 (Protected Users) 그룹 계정은 NT 해시에 PBKDF2-SHA256 을 한 번 더 거치는 경로도 있습니다[4]. 이 경로가 적용되는 Windows 버전은 실제 시스템에서 확인해야 합니다.

## Pre key 로 마스터키를 풀 때

Pre key 는 그대로 대칭 키로 쓰지 않고, PBKDF2 의 씨앗으로 넣어 필요한 키 바이트를 만듭니다. 내부 해시가 SHA-1 이면 PBKDF2 는 한 번에 20바이트를 내는데, 3DES 는 키 3개(각 8바이트)와 IV 8바이트, 곧 40바이트가 필요합니다. 그래서 XP·Vista 처럼 3DES 를 쓰는 버전은 PBKDF2 를 두 번 부릅니다. 버전별 암호·반복수는 [마스터키 파일](master-key-protect-sid.md) 의 표에 있습니다.

## 옛 암호로 감싼 마스터키까지 풀기

아직 새 암호로 다시 감싸지 않은 옛 마스터키가 남아 있을 수 있는데, 지금 암호로 [CREDHIST](credhist.md) 를 풀면 이전 암호들의 SHA-1 을 얻고, 그 옛 SHA-1 로 옛 암호에 감싸인 옛 마스터키를 풉니다. 그래서 블롭이 옛 마스터키를 썼어도 CREDHIST 사슬을 거슬러 풀 수 있습니다.

## 마스터키 파생을 느리게 한 이유와 한계

마스터키 파생은 반복수를 크게 두어 일부러 느리게 만들었고, 512비트 난수인 마스터키 자체를 전수 대입으로 찾는 것은 실용적이지 않습니다. 로컬 계정의 암호 해시는 SAM 하이브에 NT 해시로 남고, LM 해시는 Vista 이후 기본으로 저장하지 않습니다. 도메인 계정의 암호 해시는 클라이언트 SAM 이 아니라 DC 에 있습니다. SAM 해시로 암호를 찾는 편이 빨라서 마스터키 파생을 느리게 해도 보안 이득이 크지 않다는 지적이 있습니다[2]. SAM 하이브의 해시는 [레지스트리 속 비밀번호 정보](../../../02-artifacts/credentials/sam-security/index.md) 를 봅니다.

## 시각 해석

Preferred 파일에는 현재 마스터키 GUID 와 갱신 시점을 판단하는 시각이 들어 있는데, 이 시각에는 HMAC 무결성 보호가 없습니다. 그래서 값을 고쳐도 복호 과정에서 드러나지 않습니다. 마스터키 파일 헤더에는 시각 필드가 없습니다[4]. `Protect\{SID}\{GUID}` 파일의 파일 시스템 시각(만든 시각·바꾼 시각)이 무엇을 뜻하는지는 단정할 수 없습니다. 그래서 이 시각을 마스터키 생성·갱신 시각의 근거로 쓸 때는 이 한계를 함께 적습니다.

## 포렌식에서 중요한 점

- **알 수 있는 것**: 재료가 다 모이면 그 블롭이 담은 평문. 이것이 오프라인 복호의 목적입니다.
- **알 수 있는 것**: 어느 사용자의 마스터키로 풀렸는지. 그 데이터가 그 계정과 이어진다는 실마리가 됩니다.
- **알 수 없는 것**: 재료 하나라도 빠지면 나오는 것이 없습니다. 마스터키 파일이나 암호(해시)가 없으면 블롭은 무작위 값으로 남습니다.
- **알 수 없는 것**: 앱이 추가 엔트로피를 썼다면, 그 값을 모르는 한 풀리지 않습니다. [DPAPI 동작 원리](protect-unprotect.md) 를 봅니다.
- 그래서 수집할 때 마스터키 폴더 전체(마스터키 파일·Preferred), CREDHIST 파일, SAM·SECURITY·SYSTEM 하이브를 함께 모읍니다. SAM 해시를 풀려면 SYSTEM 하이브의 [부트 키](../../../02-artifacts/credentials/sam-security/system-boot-key.md) 가 필요합니다.

## 함정

- **블롭만 모으고 마스터키 파일을 빼먹습니다.** 블롭만으로는 풀 수 없습니다.
- **마스터키 하나만 모읍니다.** 블롭이 옛 마스터키를 썼을 수 있습니다. 폴더 전체를 모읍니다.
- **로컬과 도메인을 같게 봅니다.** 로컬은 SHA-1, 도메인은 NT 해시로 Pre key 를 만듭니다.
- **원본 파일을 그대로 다룹니다.** 마스터키 폴더와 하이브의 사본을 만들고 해시를 남긴 뒤 작업합니다.
- **SID 를 틀리게 넣습니다.** SID 는 Pre key 계산에 들어갑니다. 폴더 이름의 SID 를 그대로 씁니다.

## 도구

아래 공개 도구는 예로만 듭니다.

| 도구 | 오프라인 복호와 관련된 기능 |
|---|---|
| SharpDPAPI (공개 코드) | 암호·해시·백업키로 마스터키와 블롭을 오프라인에서 풉니다 |
| impacket `dpapi.py` (공개 코드) | 마스터키 파일·블롭 구조를 읽고 Pre key 를 계산합니다 |
| 헥스 편집기 | 마스터키 파일과 블롭의 바이트를 직접 읽어 재료를 확인합니다 |

## 참고 문헌

- Microsoft (NAI Labs), *Windows Data Protection* (2001, Windows XP 기준) — https://learn.microsoft.com/en-us/previous-versions/ms995355(v=msdn.10)
- Elie Bursztein, Jean-Michel Picod, Ruben Sarfati, *Reversing DPAPI and Stealing Windows Secrets Offline*, USENIX WOOT 2010 — https://www.usenix.org/legacy/event/woot10/tech/full_papers/Burzstein.pdf
- Passcape Software, *Windows DPAPI* (마스터키·CREDHIST 구조) — https://www.passcape.com/index.php?section=docsys&cmd=details&id=28
- Fortra, *impacket* `dpapi.py` (Pre key 계산식·마스터키 파일 헤더) — https://github.com/fortra/impacket/blob/master/impacket/dpapi.py
