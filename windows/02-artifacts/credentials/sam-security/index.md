# 레지스트리 속 비밀번호 정보 (SAM·SECURITY)

## 한 줄 요약

Windows 는 계정 비밀번호와 시스템 비밀을 레지스트리 하이브 두 개에 나눠 담습니다. 로컬 계정 해시는 SAM 하이브, 시스템 비밀은 SECURITY 하이브에 있습니다. 둘 다 SYSTEM 하이브의 부트키가 있어야 풉니다.

## 왜 중요한가

이 하이브들에는 로컬 계정 비밀번호의 해시, 이 PC 에서 로그온한 도메인 계정의 캐시 검증자, 서비스·자동 로그온 비밀번호 같은 시크릿이 있습니다. 자동 로그온 설정 값(`AutoAdminLogon` 등)은 SOFTWARE 하이브의 `Winlogon` 키에 있습니다.

값은 그대로 저장되지 않고 여러 겹으로 감싸여 있어서, 읽으려면 부트키부터 순서대로 풀어야 합니다. SAM·SECURITY 의 비밀은 SYSTEM 하이브에서 꺼낸 부트키로 풀기 때문에 세 하이브가 함께 있어야 합니다.

증명하지 못하는 것도 분명합니다. 저장된 해시나 검증자는 계정에 비밀번호가 있었다는 것과 로그온한 적이 있다는 것을 보이지만, 평문 비밀번호를 바로 주지는 않습니다.

## 한눈에 보기

| 하이브 | 담긴 것 | 푸는 데 필요한 것 |
|---|---|---|
| SAM | 로컬 계정의 NT 해시 | 부트키 → samKey → 계정별 DES 또는 AES |
| SECURITY | LSA 시크릿(도구로 켠 자동 로그온 비밀번호 포함), 도메인 캐시 자격증명, 암호화된 LSA 키 | 부트키 → LSA 키 → 각 시크릿·캐시 |
| SYSTEM | 부트키의 재료 (`Lsa` 아래 네 키의 클래스 이름) | — |

- 공개 구현인 Impacket 의 secretsdump.py 는 `HKLM\SAM`, `HKLM\SECURITY`, `HKLM\SYSTEM` 세 하이브를 함께 열어 처리합니다.
- 작업그룹이나 도메인 이름은 SECURITY 하이브의 `Policy\PolPrDmN` 에 있습니다.
- 압수 이미지에서 꺼낸 하이브는 사본에서 작업합니다. 원본을 열면 내용이 바뀔 수 있습니다.
- 하이브 자체의 저장 구조는 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 를 봅니다.

### 버전에 따라 달라지는 점

- SAM 해시를 감싸는 방식은 옛 Windows 가 RC4, 요즘 Windows 가 AES 입니다. 두 방식 모두 계정별 DES 한 겹이 더 있습니다. 나누는 법은 [NTLM 비밀번호 해시](nt-hash.md) 에 있습니다.
- LSA 키가 암호화되어 있는 자리는 Vista 를 경계로 다릅니다. [LSA 시크릿](lsa-secrets.md) 에 있습니다.
- 도메인 캐시는 Vista 이전이 v1, 이후가 v2 입니다. [도메인 캐시 자격증명](mscache-v2.md) 에 있습니다.

## 읽는 순서

부트키가 나머지 셋의 전제입니다. 그래서 부트키를 맨 앞에 둡니다.

1. [부트키 구하기 (SYSTEM Boot Key)](system-boot-key.md) — SYSTEM 하이브의 네 키 클래스 이름으로 16바이트 부트키를 만듭니다. 나머지 세 페이지가 이 열쇠를 씁니다.
2. [NTLM 비밀번호 해시 (NT Hash)](nt-hash.md) — 부트키로 SAM 을 풀어 로컬 계정의 해시를 꺼냅니다. 옛 방식과 새 방식을 나누는 법을 다룹니다.
3. [LSA 시크릿 (LSA Secrets)](lsa-secrets.md) — 부트키로 LSA 키를 풀고, 서비스 비밀·자동 로그온 비밀번호·시스템 열쇠를 읽습니다.
4. [도메인 캐시 자격증명 (MSCache v2)](mscache-v2.md) — LSA 시크릿 NL$KM 으로 도메인 계정의 캐시 검증자를 읽습니다.

## 함께 볼 페이지

- [사용자 계정 (SAM)](../../system-account/sam.md) — 같은 SAM 하이브에서 계정 이름·RID·로그온 정보를 읽습니다. 해시와 계정 이름을 맞출 때 함께 봅니다.
- [자격 증명 관리자와 볼트](../credential-manager-windows-vault.md) — 사용자·시스템이 저장한 다른 비밀을 함께 봅니다.
- [액티브 디렉터리 DB (NTDS.dit)](../ntds-dit.md) — 도메인 계정의 해시는 로컬 SAM 이 아니라 도메인 컨트롤러의 이 DB 에 있습니다.
- [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) — 시스템 DPAPI 를 풀 때 LSA 시크릿 DPAPI_SYSTEM 을 씁니다.
- [로그온·로그오프](../../event-logs/logon-events/index.md) — 비밀번호가 무엇인지가 아니라 언제 로그온했는지를 이벤트 로그로 맞춰 봅니다.
- [암호화 증거 다루기](../../../03-techniques/analysis/encrypted-evidence/index.md) — 해시·검증자를 크래킹으로 되찾는 절차를 다룹니다.
- [계정 탈취와 측면 이동](../../../04-scenarios/incident/credential-theft-lateral-movement/index.md) — 이 하이브의 비밀을 노린 공격을 조사하는 흐름입니다.

## 참고 문헌

- Microsoft Learn, "Configure Windows to automate logon" (자동 로그온 값 위치) — https://learn.microsoft.com/en-us/troubleshoot/windows-server/user-profiles-and-logon/turn-on-automatic-logon
- Impacket, secretsdump.py (세 하이브 처리·복호 흐름) — Fortra. https://raw.githubusercontent.com/fortra/impacket/master/impacket/examples/secretsdump.py
