---
title: "도메인 캐시 자격증명"
parent: "레지스트리 속 비밀번호 정보"
grand_parent: "아티팩트 · 자격증명"
nav_order: 2900
---

# 도메인 캐시 자격증명 (MSCache v2)

> 위치: [레지스트리 속 비밀번호 정보 (SAM·SECURITY)](index.md) > 도메인 캐시 자격증명

## 한 줄 요약

도메인 캐시 자격증명 (Domain Cached Credentials) 은 도메인 계정으로 로그온한 기록을 PC 안에 남긴 것으로, 도메인 컨트롤러에 닿지 못해도 로그온할 수 있게 남겨 둡니다. 요즘 방식을 MSCache v2 라고 부릅니다.

## 무엇을 담나 · 왜 생기나

노트북은 회사 밖에서도 도메인 계정으로 로그온해야 할 때가 있는데, 그때 도메인 컨트롤러 (Domain Controller) 에 닿지 못하면 비밀번호를 맞춰 볼 상대가 없습니다. 그래서 로그온에 성공한 도메인 계정의 검증 값을 PC 안에 캐시하고, 다음에 오프라인이면 이 캐시 값으로 로그온을 대조합니다.

## 위치와 버전별 차이

캐시는 SECURITY 하이브의 `Cache` 키 아래 `NL$1`, `NL$2` … 처럼 번호 붙은 값에 있고, 기본 설정이면 `NL$10` 까지입니다. 같은 키의 `NL$Control`, `NL$IterationCount` 는 캐시 항목이 아닙니다. 각 항목은 `NL_RECORD` 구조입니다.

빈 자리도 값으로 남습니다. IV 가 모두 0 인 항목이 빈 자리입니다. 그래서 `NL$` 값의 개수를 로그온한 계정 수로 세지 않습니다.

캐시 값은 암호문이고 푸는 열쇠는 LSA 시크릿 NL$KM 입니다. NL$KM 은 [LSA 시크릿](lsa-secrets.md) 에서 다룹니다. Vista 이후는 NL$KM 의 17~32번째 바이트를 열쇠로, 각 항목의 IV 를 써서 AES-CBC 로 풉니다.

| 방식 | 이름 | 쓰는 Windows |
|---|---|---|
| v1 | DCC · mscash | Vista 이전 |
| v2 | DCC2 · mscash2 | Vista 이후 |

## 몇 개까지, 몇 번 반복하나

- 몇 개까지 캐시할지는 `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon` 의 `CachedLogonsCount` 값이 정합니다. 형식은 REG_SZ 입니다.

| 설정 | 뜻 |
|---|---|
| 기본값 | 10 |
| 범위 | 0 ~ 50 |
| 0 | 캐시를 끔 |
| 50 초과 | 50 으로 제한 |

모든 Windows 가 기본으로 10개를 캐시하며, Windows Server 2008 만 예외입니다. 값을 바꾸면 재부팅한 뒤에 적용됩니다.

반복 횟수는 `Cache\NL$IterationCount` 로 정하며, 이 값이 없으면 10240회입니다. 이 값은 반복 횟수를 그대로 적은 것이 아닙니다. 값이 10240 이하면 1024 를 곱하고, 넘으면 아래 10비트를 버린 값이 반복 횟수입니다. MSCache v2 는 보통 10240회로 계산하지만, 반복 횟수를 바꾼 PC 에서는 이 기본값과 다를 수 있습니다.

## 구조 — MSCache v2 만드는 법

MSCache v2 는 DCC2 나 mscash2 라고도 부릅니다. 두 단계로 만듭니다.

1단계 — DCC1 만들기
- NT 해시를 만듭니다. 비밀번호를 UTF-16-LE 로 인코딩한 뒤 MD4 를 겁니다.
- 사용자 이름을 소문자로 바꿔 UTF-16-LE 로 인코딩합니다.
- NT 해시 뒤에 그 사용자 이름을 붙이고 다시 MD4 를 겁니다.
- 이 결과가 DCC1 입니다. DCC1 은 mscash 라고도 부릅니다.

2단계 — DCC2 만들기
- PBKDF2-HMAC-SHA1 을 돌립니다.
- 비밀은 1단계의 DCC1 입니다.
- 솔트는 소문자 사용자 이름을 UTF-16-LE 로 인코딩한 값입니다.
- 반복은 10240회, 결과는 16바이트입니다.

사용자 이름은 대소문자를 구분하지 않습니다. 도메인을 뗀 이름만 씁니다. 예로 `Administrator` 를 쓰고 `SOMEDOMAIN\Administrator` 를 쓰지 않습니다.

## 증거로서 의미 — 증명하는 것 / 증명하지 못하는 것

- 증명하는 것: 그 도메인 계정이 이 PC 에서 로그온한 적이 있다는 것입니다.
- 증명하지 못하는 것: 평문 비밀번호입니다. 이 값은 검증자 (Verifier) 라서 비밀번호를 되돌려 주지 않습니다. 되찾으려면 크래킹이 필요합니다.
- 캐시 값이 Impacket 에서는 `$DCC2$반복횟수#사용자이름#해시` 형태로 나옵니다. 이 형태는 크래킹 도구에 넣는 입력으로 씁니다.

## 함정과 한계

- 검증자를 NT 해시와 헷갈리지 않습니다. 이 값은 NT 해시와 사용자 이름으로 다시 만든 오프라인 로그온 검증자입니다.
- 캐시 검증자는 비밀번호를 바꿔도 바로 갱신되지 않을 수 있습니다. 클라우드에서 비밀번호를 바꿔도 그 PC 의 검증자는 그대로여서, 그 PC 에서는 옛 비밀번호로 로그온할 수 있습니다. 그래서 캐시 값이 지금 도메인 비밀번호와 같다고 단정하지 않습니다.
- SECURITY 하이브만으로는 못 풉니다. NL$KM 을 얻으려면 LSA 키가, LSA 키를 풀려면 SYSTEM 하이브의 부트키가 필요합니다.

## 직접 분석해 보기

- 헥스로 한 번: SECURITY 하이브를 열어 `Cache` 아래 `NL$1` 부터의 항목과 `NL$IterationCount` 를 확인합니다.
- 공개 도구로 한 번: 아래 도구는 예로만 듭니다.

| 도구 | 도메인 캐시와 관련된 기능 |
|---|---|
| Impacket 의 secretsdump.py (공개 코드) | NL$KM 으로 캐시를 풀어 `$DCC2$` 형태로 냅니다 |
| 하이브 뷰어 | `Cache` 아래 NL$ 항목과 `CachedLogonsCount` 를 확인합니다 |

## 교차 검증 — 함께 볼 아티팩트

- [LSA 시크릿 (LSA Secrets)](lsa-secrets.md) — 캐시를 푸는 열쇠 NL$KM 이 여기 있습니다.
- [부트키 구하기 (SYSTEM Boot Key)](system-boot-key.md) — NL$KM 을 얻는 사슬의 맨 앞입니다.
- [로그온·로그오프](../../event-logs/logon-events/index.md) — 도메인 계정이 언제 로그온했는지는 이벤트 로그로 맞춰 봅니다.
- [계정 탈취와 측면 이동](../../../04-scenarios/incident/credential-theft-lateral-movement/index.md) — 캐시 자격증명을 노린 공격을 조사하는 흐름입니다.

## 참고 문헌

- Microsoft Learn, "Cached domain logon information" (CachedLogonsCount·검증자·비밀번호 변경) — https://learn.microsoft.com/en-us/troubleshoot/windows-server/user-profiles-and-logon/cached-domain-logon-information
- passlib.hash.msdcc2 (MSCache v2·10240회 반복·사용자 이름 규칙) — Passlib. https://passlib.readthedocs.io/en/stable/lib/passlib.hash.msdcc2.html
- passlib.hash.msdcc (MSCache v1·NT 해시) — Passlib. https://passlib.readthedocs.io/en/stable/lib/passlib.hash.msdcc.html
- Impacket, secretsdump.py (NL_RECORD·NL$KM 복호·출력 형태) — Fortra. https://raw.githubusercontent.com/fortra/impacket/master/impacket/examples/secretsdump.py
