---
title: "NTLM 비밀번호 해시"
parent: "레지스트리 속 비밀번호 정보"
grand_parent: "아티팩트 · 자격증명"
nav_order: 2880
---

# NTLM 비밀번호 해시 (NT Hash)

> 위치: [레지스트리 속 비밀번호 정보 (SAM·SECURITY)](index.md) > NTLM 비밀번호 해시

## 한 줄 요약

NT 해시 (NT Hash) 는 로컬 계정의 비밀번호를 MD4 로 줄인 값으로, SAM 하이브 안에 계정마다 하나씩 들어 있습니다. 꺼내려면 [부트키](system-boot-key.md) 로 여러 겹을 벗겨야 합니다.

## 무엇을 담나 · 왜 생기나

Windows 는 로컬 계정의 비밀번호를 평문으로 두지 않고, 대신 비밀번호를 줄인 NT 해시를 SAM 하이브에 적어 둡니다. 로그온할 때 입력한 비밀번호로 같은 해시를 만들어 저장된 값과 맞춰 봅니다. NT 해시는 비밀번호를 UTF-16-LE 로 인코딩한 뒤 MD4 를 걸어 만듭니다. 문자 인코딩은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 을 봅니다.

## 위치와 버전별 차이

로컬 계정 해시는 SAM 하이브의 `SAM\Domains\Account\Users\<RID>` 아래에 있고, 항목은 RID (상대 식별자, Relative Identifier) 별로 하나입니다. 각 항목에는 `F` 값과 `V` 값이 있는데 암호화된 해시는 `V` 값에 들어 있습니다. `Users` 아래 하위 키 이름은 RID 를 16진수로 적은 것입니다(예: `000001F4` 는 RID 500). RID 는 계정 SID 의 마지막 숫자이며, SID 는 [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 을 봅니다.

SAM 해시를 감싸는 방식은 Windows 버전에 따라 다릅니다. 방식을 나누는 표시는 두 군데에 있습니다.

- samKey 쪽: `SAM\Domains\Account` 키(계정별 키가 아님)의 `F` 값 안 키 데이터(Key0) 첫 바이트
- 계정 해시 쪽: 각 계정 `V` 값 안 NT 해시 자리의 세 번째 바이트

| 표시 값 | 감싼 방식 |
|---|---|
| 0x01 | 옛 방식. RC4(+MD5) 로 감쌈 |
| 0x02 | 새 방식. AES-128-CBC 로 감쌈 |

- 두 방식 모두 마지막에 계정별 DES 한 겹이 더 있습니다.
- 새 방식은 Windows Server 2016 무렵부터 쓰였고, 일부 Windows 10·Server 2012 R2 에서도 쓰였다는 보고가 있습니다. Windows 버전으로 짐작하지 않고 위 표시 값으로 방식을 나눕니다.

## 여러 겹을 벗기는 순서

1. 부트키를 먼저 만듭니다. 만드는 법은 [부트키 구하기](system-boot-key.md) 에 있습니다.
2. 부트키만으로는 바로 못 풉니다. 먼저 "해시된 부트키 (samKey)" 를 만듭니다.
3. 옛 방식(0x01)이면 samKey 를 푸는 RC4 키를 MD5 로 얻습니다. 재료는 `Account` 의 `F` 안 솔트, QWERTY 상수, 부트키, DIGITS 상수를 이 순서로 이은 것입니다. 그 RC4 키로 키 데이터를 풀면 samKey 가 나옵니다.
4. 새 방식(0x02)이면 부트키를 열쇠로, `F` 안의 솔트를 IV 로 써서 키 데이터를 AES 로 풉니다. 이 경우 두 상수는 쓰지 않습니다.
5. samKey 로 각 계정의 해시 데이터를 풉니다. 옛 방식은 RC4, 새 방식은 AES 입니다.
6. 마지막으로 계정별 DES 한 겹을 더 벗깁니다. 이 DES 키의 재료가 RID 입니다. 그래서 부트키가 같아도 계정마다 다른 열쇠가 나옵니다.

두 상수는 고정 문자열입니다. 두 문자열 모두 끝에 널 바이트(0x00) 하나가 붙습니다.

- QWERTY 상수: `!@#$%^&*()qwertyUIOPAzxcvbnmQQQQQQQQQQQQ)(*@&%`
- DIGITS 상수: `0123456789012345678901234567890123456789`

## 증거로서 의미 — 증명하는 것 / 증명하지 못하는 것

- 증명하는 것: 하이브를 수집한 시점에 그 계정에 설정된 비밀번호의 해시입니다.
- 해시 자리가 비어 있으면 Impacket 은 빈 비밀번호의 NT 해시(`31d6cfe0d16ae931b73c59d7e0c089c0`)를 대신 적습니다. 이 값이 보이면 해시가 없거나 비밀번호가 빈 것이므로, 비밀번호가 설정되었다고 단정하지 않습니다.
- 증명하지 못하는 것: 평문 비밀번호 자체입니다. NT 해시에서 비밀번호를 되찾으려면 사전 대입이나 크래킹이 따로 필요합니다.
- 증명하지 못하는 것: 그 비밀번호로 실제 로그온한 시각입니다. 해시는 비밀번호가 무엇인지만 담고, 언제 썼는지는 담지 않습니다. 로그온 시각은 [로그온·로그오프](../../event-logs/logon-events/index.md) 에서 찾습니다.

## 시각 해석

로컬 계정이 만들어진 시각은 레지스트리에 직접 적혀 있지 않아서 흔히 그 계정 SID 의 `NTUSER.DAT` 생성 시각으로 짐작합니다. 다만 `NTUSER.DAT` 는 프로필이 처음 만들어질 때 생기므로, 계정을 만든 뒤 한참 지나 처음 로그온했다면 이 시각은 계정 생성보다 늦습니다. 이 값은 짐작이므로 보고서에 추정값이라고 밝힙니다. 계정을 언제 만들고 바꿨는지는 [계정 생성·변경 이벤트](../../event-logs/account-management-events.md) 로 맞춰 봅니다.

## 함정과 한계

- 방식 표시를 확인하지 않고 한 방식만 가정하면 엉뚱한 값이 나옵니다. 0x01 과 0x02 를 먼저 나눕니다.
- 세 하이브를 함께 모읍니다. SAM 만으로는 부트키가 없어 풀지 못합니다.

## 직접 분석해 보기

- 헥스로 한 번: SAM 하이브를 열어 `SAM\Domains\Account` 의 `F` 값에서 키 데이터 첫 바이트로 0x01 과 0x02 를 나눕니다. 이어서 `Users` 아래 RID 하위 키의 `V` 값을 확인합니다.
- 공개 도구로 한 번: 아래 도구는 예로만 듭니다.

| 도구 | NT 해시와 관련된 기능 |
|---|---|
| Impacket 의 secretsdump.py (공개 코드) | 부트키로 SAM 을 풀어 계정별 NT 해시를 냅니다 |
| 하이브 뷰어 | `Users` 아래 RID 별 `F`·`V` 값을 직접 확인합니다 |

## 교차 검증 — 함께 볼 아티팩트

- [부트키 구하기 (SYSTEM Boot Key)](system-boot-key.md) — 이 페이지의 전제입니다.
- [사용자 계정 (SAM)](../../system-account/sam.md) — 같은 SAM 하이브에서 계정 이름·RID·로그온 정보를 읽습니다. 계정 이름과 해시를 이 페이지로 맞춥니다.
- [액티브 디렉터리 DB (NTDS.dit)](../ntds-dit.md) — 도메인 계정의 해시는 로컬 SAM 이 아니라 도메인 컨트롤러의 이 DB 에 있습니다.

## 참고 문헌

- Impacket, secretsdump.py (SAM 복호 흐름·QWERTY·DIGITS 상수) — Fortra. https://raw.githubusercontent.com/fortra/impacket/master/impacket/examples/secretsdump.py
- passlib.hash.msdcc (NT 해시 = MD4 of UTF-16-LE) — Passlib. https://passlib.readthedocs.io/en/stable/lib/passlib.hash.msdcc.html
