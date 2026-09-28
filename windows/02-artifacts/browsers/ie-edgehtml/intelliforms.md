---
title: "저장 비밀번호 (IntelliForms)"
parent: "인터넷 익스플로러·옛 엣지"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1830
---

# 저장 비밀번호 (IntelliForms)

IE 7~9 는 웹 폼에 입력한 아이디·비밀번호를 사용자 하이브의 `IntelliForms\Storage2` 키에 사이트별 값으로 저장합니다. 값 이름은 사이트 주소의 SHA1 해시이고, 값 데이터는 그 주소를 추가 엔트로피로 넣어 DPAPI 로 암호화한 것입니다. 그래서 주소를 알아야 비밀번호를 풀 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

IE 는 로그인 폼의 아이디·비밀번호를 자동 완성 (AutoComplete) 용으로 저장할 수 있고, IE 7~9 는 이 값을 `IntelliForms\Storage2` 키에 둡니다. 한 사이트에 아이디·비밀번호 쌍이 여러 개 있을 수 있습니다. HTTP 기본 인증 (Basic Authentication) 창에 넣은 비밀번호는 다른 곳에 저장하는데, IE 7 이후 이 비밀번호는 사용자의 `Credentials` 폴더에 들어갑니다.

Windows 11 25H2 에서는 `IntelliForms` 키에 값도 하위 키도 없고 `Storage2` 도 없을 수 있습니다.

## 위치와 버전별 차이

| IE 버전 | 저장 위치 |
|---|---|
| IE 4~6 | `HKCU\Software\Microsoft\Protected Storage System Provider` (보호 저장소, Protected Storage) |
| IE 7~9 | `HKCU\Software\Microsoft\Internet Explorer\IntelliForms\Storage2` |
| IE 10·11, 엣지 | 실제 데이터로 확인 |
| HTTP 기본 인증 (IE 7 이후) | 아래 표의 `Credentials` 폴더 |

| Windows | HTTP 기본 인증 비밀번호 폴더 |
|---|---|
| XP | `C:\Documents and Settings\<사용자>\Application Data\Microsoft\Credentials` |
| Vista 이후 | `C:\Users\<사용자>\AppData\Roaming\Microsoft\Credentials` |

- 아래 구조는 IE 4~8, Windows XP·Vista·7 기준입니다[2].
- IE 10·11 과 엣지 비밀번호를 다른 PC 의 드라이브에서 되살리려면 그 프로필의 마지막 로그온 비밀번호가 필요합니다[1].
- `Credentials` 폴더의 파일 구조는 [자격 증명 관리자와 볼트](../../credentials/credential-manager-windows-vault.md) 에서 다룹니다.

## 구조

### Storage2 값 이름

값 이름은 사이트 주소에서 아래 순서로 만듭니다.

1. 사이트 주소를 UTF-16(와이드 문자) 문자열로 씁니다. 끝의 0 까지 넣습니다.
2. 이 바이트열의 SHA1 해시를 구합니다. 해시는 20바이트입니다.
3. 20바이트를 16진 문자열 40글자로 바꿉니다.
4. 20바이트를 모두 더한 값의 아래 1바이트를 검사 바이트로 삼습니다.
5. 검사 바이트를 16진 2글자로 바꿔 뒤에 붙입니다.

값 이름은 모두 42글자입니다. 해시는 거꾸로 풀 수 없으므로, 값 이름만 보고 주소를 알아낼 수는 없습니다. 후보 주소의 해시를 구해 값 이름과 맞춰 봅니다.

### Storage2 값 데이터

- 값 데이터는 DPAPI (Data Protection API) 의 `CryptProtectData` 함수로 암호화돼 있습니다.
- 추가 엔트로피 (Additional Entropy) 로 사이트 주소 자체를 넣습니다. 형식은 값 이름을 만들 때와 같은 UTF-16 문자열이고, 끝의 0 까지 넣습니다.
- 그래서 주소를 모르면 풀 수 없고, 방문 기록에 그 주소가 남아 있어야 되살릴 수 있습니다.
- DPAPI 블롭과 마스터 키 구조는 [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) 에서 다룹니다.

풀어낸 데이터는 아래 순서로 이어집니다.

| 순서 | 부분 | 내용 |
|---|---|---|
| 1 | 머리글 | dwSize, dwSecretInfoSize, dwSecretSize |
| 2 | 비밀 정보 머리글 | dwTotalSecrets. 값은 아이디·비밀번호 쌍 수 × 2 입니다 |
| 3 | 항목 목록 | 항목마다 문자열의 위치와 길이 |
| 4 | 문자열 | UTF-16 문자열들. 각각 끝에 0 이 붙습니다 |

dwTotalSecrets 를 2 로 나누면 그 사이트에 저장한 쌍의 수가 나옵니다.

### HTTP 기본 인증 비밀번호

- `Credentials` 폴더의 자격 증명 가운데 대상 이름이 `Microsoft_WinInet_` 으로 시작하는 것입니다.
- 자격 증명 종류 값은 1 입니다.
- 추가 엔트로피는 GUID 문자열 `abe2869f-9b47-4cd9-a358-c22904dba7f7` 의 각 글자에 4 를 곱해 만든 74바이트입니다.
- 풀면 `아이디:비밀번호` 형태의 문자열이 나옵니다.
- 이 비밀번호를 되살리려면 관리자 권한이 필요합니다[1].

## 증거로서 의미

### 증명하는 것

- 이 사용자 하이브에 어떤 사이트의 저장 비밀번호 값이 있었습니다.
- 후보 주소의 해시가 값 이름과 맞으면, 그 값이 어느 주소에 대한 것인지 확정할 수 있습니다.
- 풀어낸 데이터로 그 사이트에 저장한 아이디가 무엇이고 몇 쌍인지 알 수 있습니다.

### 증명하지 못하는 것

- 저장한 아이디·비밀번호로 로그인이 성공했는지는 알 수 없습니다.
- 저장한 비밀번호가 지금도 맞는지는 알 수 없습니다.
- 값 하나만으로 언제 저장했는지는 알 수 없습니다.
- 주소를 찾지 못한 값은 어느 사이트의 것인지 말할 수 없습니다.

보고서에는 "이 계정의 IntelliForms\Storage2 에 이 주소의 해시와 맞는 값이 있고, 풀어낸 아이디는 이것이다" 처럼 씁니다. 비밀번호 자체는 조사에 필요한 만큼만 적습니다.

## 시각 해석

- 저장 시점을 좁힐 때는 `Storage2` 키의 마지막 기록 시각 (LastWrite) 과 같은 주소의 방문 기록 시각을 함께 봅니다.
- 키의 마지막 기록 시각은 키 안의 어느 값이 바뀌어도 바뀝니다. 그래서 특정 사이트를 저장한 시각으로 단정하지 않습니다.
- 방문 기록 시각은 [웹캐시 DB](webcachev01-dat.md) 와 [index.dat](index-dat.md) 에서 읽습니다.

## 함정과 한계

- **주소가 한 글자만 달라도 해시가 다릅니다.** IE 가 해시 전에 주소를 소문자로 바꾸는지는 시험 기기에서 재현해 확인합니다. 해시가 맞지 않으면 방문 기록에 남은 주소를 끝 `/` 유무, 대소문자, 경로 차이를 바꿔 가며 맞춰 봅니다.
- **주소를 못 찾으면 풀 수 없습니다.** 방문 기록을 지웠다면 [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 의 옛 방문 기록에서 주소 후보를 찾습니다.
- **DPAPI 를 풀 열쇠가 필요합니다.** 다른 PC 의 드라이브나 이미지에서 풀려면 사용자의 마스터 키와 로그온 비밀번호가 필요합니다. 오프라인으로 푸는 절차는 [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) 에서 다룹니다.
- **IE 10 이후는 이 키가 비어 있을 수 있습니다.** 위 구조는 IE 4~8 기준이고[2], IE 10 이후 저장 위치는 실제 데이터로 확인합니다. 빈 `IntelliForms` 키를 "저장 비밀번호 없음" 으로 단정하지 않고, [자격 증명 관리자와 볼트](../../credentials/credential-manager-windows-vault.md) 도 함께 봅니다.
- **HTTP 기본 인증 비밀번호는 레지스트리에 없습니다.** `Credentials` 폴더를 따로 수집해야 합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 값은 명세대로 계산한 예시입니다. 실제 IE 가 저장한 값이 아닙니다. 주소도 지어낸 주소입니다.

**1) 주소를 UTF-16LE 로 쓰고 끝에 0 을 붙입니다.** 주소는 `https://www.example.com/` 입니다.

```
68 00 74 00 74 00 70 00 73 00 3A 00 2F 00 2F 00   h.t.t.p.s.:././.
77 00 77 00 77 00 2E 00 65 00 78 00 61 00 6D 00   w.w.w...e.x.a.m.
70 00 6C 00 65 00 2E 00 63 00 6F 00 6D 00 2F 00   p.l.e...c.o.m./.
00 00                                             (끝의 0)
```

**2) 이 50바이트의 SHA1 해시를 구합니다.**

```
C4 A8 D5 F2 D0 39 04 3E 3B E0 82 09 B6 DF A2 36 0A 3F FA F4
```

**3) 20바이트를 모두 더합니다.** 합은 2760(0xAC8)이고, 아래 1바이트는 `C8` 입니다.

**4) 값 이름을 만듭니다.**

```
C4A8D5F2D039043E3BE08209B6DFA2360A3FFAF4C8
```

이 예시는 16진 글자를 대문자로 적었습니다. 실제 값 이름과 맞출 때는 대소문자를 구분하지 않고 비교합니다. 같은 계산을 PowerShell 로 하면 아래와 같습니다.

```powershell
$u = "https://www.example.com/"
$b = [Text.Encoding]::Unicode.GetBytes($u + [char]0)
$h = [Security.Cryptography.SHA1]::Create().ComputeHash($b)
$c = ($h | Measure-Object -Sum).Sum % 256
(($h | ForEach-Object { $_.ToString("X2") }) -join "") + ([int]$c).ToString("X2")
```

방문 기록에서 뽑은 주소 목록을 이 계산에 넣고, `Storage2` 의 값 이름과 같은 것을 찾습니다.

### 공개 도구로 한 번

1. 사용자 NTUSER.DAT 와 하이브 로그, `Credentials` 폴더, DPAPI 마스터 키 폴더를 사본으로 뜹니다.
2. 레지스트리 뷰어로 `Software\Microsoft\Internet Explorer\IntelliForms\Storage2` 의 값 이름 목록을 뽑습니다.
3. 방문 기록의 주소로 해시를 계산해 값 이름과 짝을 맞춥니다.
4. 공개 복원 도구를 쓰면 주소 짝 맞추기와 복호를 한 번에 할 수 있습니다. 도구가 찾은 주소 하나를 골라 위 계산으로 값 이름이 맞는지 직접 확인합니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 웹캐시 DB | IE 10 이후 방문 기록에서 해시에 넣을 주소 후보를 찾습니다 | [웹캐시 DB (WebCacheV01.dat)](webcachev01-dat.md) |
| 옛 기록 파일 | IE 9 이전 방문 기록에서 주소 후보를 찾습니다 | [옛 기록 파일 (index.dat)](index-dat.md) |
| 주소창 입력 주소 | 사용자가 직접 입력한 주소를 후보에 더합니다 | [주소창 입력 주소](typedurls-typedurlstime.md) |
| 자격 증명 관리자와 볼트 | HTTP 기본 인증 비밀번호와 다른 웹 자격 증명을 봅니다 | [자격 증명 관리자와 볼트](../../credentials/credential-manager-windows-vault.md) |
| DPAPI 구조 | 값 데이터를 풀 마스터 키를 찾습니다 | [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) |
| 사용자 계정 | 오프라인 복호에 필요한 계정 정보를 봅니다 | [사용자 계정](../../system-account/sam.md) |
| 다른 브라우저 | 같은 사이트의 비밀번호를 다른 브라우저에도 저장했는지 봅니다 | [크롬 계열 브라우저](../chrome-edge-whale/index.md), [파이어폭스](../firefox/index.md) |

## 실습

Windows 7 에서 IE 8·9 를 쓴 공개 시험 데이터(NIST CFReDS 등)에서 사용자 프로필을 꺼내 아래 질문을 풀어 봅니다.

1. `IntelliForms\Storage2` 에 값이 몇 개 있습니까? 값 이름은 모두 42글자입니까?
2. 방문 기록에서 뽑은 주소로 해시를 계산하면 몇 개의 값 이름과 짝이 맞습니까?
3. 짝을 못 찾은 값이 있다면, 주소 표기를 어떻게 바꿔야 맞습니까?
4. 풀어낸 데이터의 dwTotalSecrets 는 얼마입니까? 그 사이트에 저장한 쌍은 몇 개입니까?
5. `Credentials` 폴더에 대상 이름이 `Microsoft_WinInet_` 으로 시작하는 자격 증명이 있습니까?

## 참고 문헌

1. NirSoft, *IE PassView* (버전별 저장 위치, 주소가 필요한 이유, 다른 드라이브에서 되살릴 때의 조건, 관리자 권한 조건). https://www.nirsoft.net/utils/internet_explorer_password.html
2. SecurityXploded, IE 비밀번호 저장·복호 방식 설명 글 (Storage2 값 이름·값 데이터 구조, 추가 엔트로피, HTTP 기본 인증 비밀번호). https://securityxploded.com/iepasswordsecrets.php
