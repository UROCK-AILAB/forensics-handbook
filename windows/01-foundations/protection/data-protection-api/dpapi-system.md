---
title: "시스템 DPAPI 키"
parent: "DPAPI 구조"
grand_parent: "기반 · 암호 보호"
nav_order: 590
---

# 시스템 DPAPI 키 (DPAPI_SYSTEM)

> 위치: [DPAPI 구조 (Data Protection API)](index.md) > 시스템 DPAPI 키

## 한 줄 요약

SYSTEM 과 머신 계정은 사용자 암호가 없어서, 이 계정의 마스터키는 사용자 암호 대신 LSA 시크릿 DPAPI_SYSTEM 으로 풉니다.
DPAPI_SYSTEM 을 손에 넣으면 머신 마스터키로 감싼 시스템 비밀을 오프라인에서 풀 수 있습니다.

> 사용자 계정의 마스터키가 암호로 어떻게 풀리는지는 [마스터키 파일](master-key-protect-sid.md) 에 있습니다.
> 이 글은 암호가 없는 계정이 그 자리를 무엇으로 메우는지를 다룹니다.

## 무엇을 담나 · 왜 생기나

SYSTEM 계정과 머신 계정은 사람이 정한 암호가 없지만, 무선 프로필 키나 일부 서비스 비밀처럼 DPAPI 로 데이터를 보호합니다. 암호가 없으니 Pre key 를 만들 재료가 따로 필요하고, 그 재료가 LSA 시크릿 DPAPI_SYSTEM 입니다. LSA 시크릿은 레지스트리의 SECURITY 하이브에 들어 있습니다. [레지스트리 속 비밀번호 정보](../../../02-artifacts/credentials/sam-security/index.md) 를 봅니다.

## 구조

DPAPI_SYSTEM 은 machine key 와 user key 두 부분으로 나뉘고, 각 부분은 20바이트(16진수로 적으면 40자)입니다. 머신 계정이 만든 마스터키는 이 machine key 로 풉니다. 공개 복호 코드(impacket 의 DPAPI_SYSTEM)도 이 값을 Version, MachineKey, UserKey 순으로 읽습니다.

## 위치

머신·SYSTEM 계정의 마스터키는 사용자 프로필이 아니라 시스템 폴더 아래에 있습니다.

- 널리 알려진 경로는 `%WINDIR%\System32\Microsoft\Protect\S-1-5-18\` 와 그 아래 `User\` 입니다.
- 이 정확한 경로는 이 글의 참고 문헌으로 확정하지 못했습니다.
- 한 공개 자료는 systemprofile 과 ServiceProfiles(LocalService) 아래의 `...\Microsoft\Credentials` 맥락을 언급합니다.
- 폴더 이름의 S-1-5-18 은 로컬 SYSTEM 계정의 SID 입니다. [윈도 식별자 형식](../../value-decoding/sid-guid-clsid-known-folder-id.md) 을 봅니다.

## SYSTEM 이 만든 블롭 알아보기

SYSTEM 계정이 만든 마스터키 파일은 푸터의 credHist GUID 가 0x00 입니다. 이 계정에는 암호가 없어 [CREDHIST](credhist.md) 사슬이 없기 때문이며, 그래서 credHist GUID 가 0x00 이면 SYSTEM 이 만든 마스터키로 짐작합니다.

## 포렌식에서 중요한 점

사용자 DPAPI 데이터는 사용자 암호로, 시스템 DPAPI 데이터는 DPAPI_SYSTEM 으로 풉니다. DPAPI_SYSTEM 을 얻으려면 SECURITY 하이브의 LSA 시크릿에 닿아야 하므로 시스템 DPAPI 데이터를 풀려면 SYSTEM·SECURITY 하이브를 함께 모읍니다.

- 무선 프로필의 오프라인 복호가 이 경로를 씁니다. [Wi-Fi 프로필](../../../02-artifacts/network/wlan-profiles.md) 을 봅니다.
- **말해 주는 것**: 이 마스터키가 사용자 것인지 시스템 것인지. credHist GUID 가 0x00 인지로 짐작합니다.
- **말해 주지 못하는 것**: DPAPI_SYSTEM 자체. SECURITY 하이브의 LSA 시크릿 없이는 나오지 않습니다.

## 함정

- **사용자 암호로 시스템 마스터키를 풀려고 합니다.** 시스템 마스터키는 암호가 아니라 DPAPI_SYSTEM 으로 풉니다.
- **SYSTEM 마스터키를 사용자 프로필에서 찾습니다.** 이 마스터키는 시스템 폴더 아래에 있습니다.
- **SECURITY 하이브를 빼고 모읍니다.** DPAPI_SYSTEM 을 얻을 재료가 없어집니다.
- **credHist GUID 0x00 을 손상으로 봅니다.** SYSTEM 계정은 원래 이 값이 0x00 입니다.

## 옛 버전의 위험한 모드

Windows 2000 레거시 모드에서는 마스터키를 로컬 LSA 시크릿에 백업할 수 있었습니다. 이 모드를 켜면 LSA·마스터키·보호 데이터를 함께 훔쳐 마음대로 풀 수 있고, 관리자가 레지스트리를 고쳐야 켜집니다. 이 설명은 2001년 문서(Windows XP 기준)에 있습니다. 뒤 버전에도 이 모드가 남아 있는지는 이 글의 참고 문헌으로 확인하지 못했습니다.

## 도구

아래 공개 도구는 예로만 듭니다.

| 도구 | 시스템 DPAPI 와 관련된 기능 |
|---|---|
| SharpDPAPI (공개 코드) | SECURITY 하이브에서 DPAPI_SYSTEM 을 읽어 머신 마스터키를 풉니다 |
| 헥스 편집기 | 마스터키 파일 푸터의 credHist GUID 가 0x00 인지 확인합니다 |

## 참고 문헌

- Microsoft (NAI Labs), *Windows Data Protection* (2001, Windows XP 기준) — https://learn.microsoft.com/en-us/previous-versions/ms995355(v=msdn.10)
- Elie Bursztein, Jean-Michel Picod, Ruben Sarfati, *Reversing DPAPI and Stealing Windows Secrets Offline*, USENIX WOOT 2010 — https://www.usenix.org/legacy/event/woot10/tech/full_papers/Burzstein.pdf
- GhostPack, *SharpDPAPI* (경로·DPAPI_SYSTEM·백업키) — https://github.com/GhostPack/SharpDPAPI
- impacket, *dpapi.py* (DPAPI_SYSTEM 구조체) — https://github.com/fortra/impacket/blob/master/impacket/dpapi.py
