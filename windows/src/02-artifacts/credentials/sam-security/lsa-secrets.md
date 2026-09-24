# LSA 시크릿 (LSA Secrets, 자동 로그온 비밀번호 포함)

> 위치: [레지스트리 속 비밀번호 정보 (SAM·SECURITY)](index.md) > LSA 시크릿

## 한 줄 요약

LSA 시크릿 (LSA Secrets) 은 Windows 가 서비스 비밀번호나 시스템 열쇠를 담아 두는 저장소로, SECURITY 하이브에 있으며 자동 로그온 비밀번호가 여기서 나오기도 합니다.

## 무엇을 담나 · 왜 생기나

Windows 는 서비스 계정 비밀번호, 시스템 DPAPI 열쇠, 도메인 캐시 복호 열쇠처럼 사람이 다시 입력하지 않아도 되는 비밀을 어딘가 적어 두어야 하고, 그 자리가 LSA 시크릿입니다. 각 시크릿은 SECURITY 하이브에 이름을 달고 들어갑니다.

## 위치와 버전별 차이

LSA 시크릿은 SECURITY 하이브의 `Policy\Secrets\<이름>\CurrVal\default` 에 있으며 암호문이라서, 풀려면 LSA 키 (LSA Key) 가 먼저 필요합니다. LSA 키도 암호화되어 하이브에 있고, 자리는 Windows 버전에 따라 다릅니다.

| Windows 버전 | LSA 키가 암호화되어 있는 곳 |
|---|---|
| Vista 이후 | `Policy\PolEKList\default` |
| Vista 이전 | `Policy\PolSecretEncryptionKey\default` |

## 푸는 순서 (Vista 이후)

1. [부트키](system-boot-key.md) 를 먼저 만듭니다.
2. `PolEKList` 값을 `LSA_SECRET` 구조로 읽고, 그 안 EncryptedData 의 앞 32바이트를 떼어 둡니다.
3. 임시 키를 만듭니다. 부트키 뒤에 그 32바이트를 1000번 이어 붙인 것을 SHA256 에 넣습니다.
4. 그 임시 키로 EncryptedData 의 나머지를 AES-CBC 로 풉니다.
5. 푼 결과를 `LSA_SECRET_BLOB` 로 읽습니다. 그 Secret 칸의 52바이트째부터 32바이트가 LSA 키입니다.
6. LSA 키로 각 시크릿의 `CurrVal\default` 를 풉니다.

## 구조

시크릿 값은 `LSA_SECRET` 구조로 시작하고, 이 안에 EncKeyID(16바이트), EncAlgorithm, Flags, EncryptedData 가 차례로 있습니다. EncryptedData 를 풀면 `LSA_SECRET_BLOB` 구조가 나오는데, 길이 칸과 용도를 모르는 12바이트 뒤의 Secret 칸에 실제 시크릿이 있습니다. 이 구조 이름과 흐름은 공개 구현인 Impacket 에서 확인했습니다.

## 자동 로그온 비밀번호

자동 로그온 (Automatic Logon) 을 켜면 비밀번호가 어딘가 저장되며, 저장되는 자리는 켜는 방법에 따라 두 갈래입니다.

| 켜는 방법 | 비밀번호가 저장되는 곳 | 형태 |
|---|---|---|
| 레지스트리 편집기로 값을 직접 넣음 | `Winlogon` 키의 `DefaultPassword` | 평문 문자열 |
| Sysinternals 의 Autologon 도구로 켬 | LSA 시크릿 | 암호문 (LSA 키로 풂) |

평문으로 들어간 `DefaultPassword` 는 Authenticated Users 그룹이 원격으로 읽을 수 있다고 Microsoft 문서가 밝힙니다. 자동 로그온 설정 값은 SOFTWARE 하이브의 `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon` 아래에 있어 SECURITY 하이브가 아니므로 따로 모읍니다. `DefaultPassword` 문자열이 없으면 Windows 가 `AutoAdminLogon` 을 1 에서 0 으로 바꾼다고 Microsoft 문서가 밝힙니다.

| 값 이름 | 뜻 |
|---|---|
| AutoAdminLogon | 자동 로그온 켜짐(1)·꺼짐(0) |
| DefaultUserName | 자동으로 로그온할 계정. 다른 사용자가 콘솔로 로그온하면 마지막 로그온 사용자로 바뀔 수 있음 |
| DefaultDomainName | 그 계정의 도메인 |
| DefaultPassword | 평문 비밀번호 (직접 넣은 경우) |

## 눈여겨볼 시크릿 이름

| 이름 | 담긴 것 | 이어지는 페이지 |
|---|---|---|
| DPAPI_SYSTEM | 시스템 DPAPI 열쇠 | [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) |
| NL$KM | 도메인 캐시 자격증명을 푸는 열쇠 | [도메인 캐시 자격증명 (MSCache v2)](mscache-v2.md) |

- NL$KM 은 `Policy\Secrets\NL$KM\CurrVal\default` 에 있습니다.

## 증거로서 의미 — 증명하는 것 / 증명하지 못하는 것

- 증명하는 것: 그 이름의 시크릿이 이 컴퓨터에 저장되어 있다는 것입니다. `DefaultPassword` 가 평문으로 있으면 그 자체가 비밀번호입니다.
- 증명하지 못하는 것: 시크릿을 언제 넣고 언제 썼는지입니다. 복호 흐름에서 쓰는 칸에는 사용 시각이 없습니다.
- 증명하지 못하는 것: `DefaultUserName` 값만으로 자동 로그온 계정이라고 단정하지 못합니다. 이 값은 마지막으로 로그온한 사용자를 뜻하기도 합니다.

## 함정과 한계

- SECURITY 하이브만으로는 못 풉니다. LSA 키를 푸는 데 SYSTEM 하이브의 부트키가 필요합니다.
- 자동 로그온 비밀번호는 `Winlogon\DefaultPassword` 와 LSA 시크릿 두 곳을 모두 봅니다.
- 하이브는 사본에서 작업합니다.
- 작업그룹·도메인 이름은 같은 SECURITY 하이브의 `Policy\PolPrDmN` 에 있는데, 이 값은 시크릿과 다른 항목입니다.

## 직접 분석해 보기

- 헥스로 한 번: SECURITY 하이브를 열어 `Policy\PolEKList\default` 와 `Policy\Secrets` 아래 이름들을 확인합니다.
- 공개 도구로 한 번: 아래 도구는 예로만 듭니다.

| 도구 | LSA 시크릿과 관련된 기능 |
|---|---|
| Impacket 의 secretsdump.py (공개 코드) | 부트키로 LSA 키를 풀고 각 시크릿을 냅니다 |
| 하이브 뷰어 | `Policy\Secrets` 아래 시크릿 이름과 `Winlogon` 값을 확인합니다 |

## 교차 검증 — 함께 볼 아티팩트

- [부트키 구하기 (SYSTEM Boot Key)](system-boot-key.md) — LSA 키를 푸는 전제입니다.
- [도메인 캐시 자격증명 (MSCache v2)](mscache-v2.md) — NL$KM 시크릿을 열쇠로 씁니다.
- [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) — DPAPI_SYSTEM 시크릿을 시스템 비밀 복호에 씁니다.
- [자격 증명 관리자와 볼트](../credential-manager-windows-vault.md) — 사용자·시스템이 저장한 다른 비밀을 함께 봅니다.

## 참고 문헌

- Microsoft Learn, "Configure Windows to automate logon" (자동 로그온 값·평문 위험) — https://learn.microsoft.com/en-us/troubleshoot/windows-server/user-profiles-and-logon/turn-on-automatic-logon
- Impacket, secretsdump.py (LSA 키 복호 흐름·구조 이름·NL$KM) — Fortra. https://raw.githubusercontent.com/fortra/impacket/master/impacket/examples/secretsdump.py
