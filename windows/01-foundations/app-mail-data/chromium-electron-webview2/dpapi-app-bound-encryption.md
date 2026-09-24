---
title: "쿠키·비밀번호 암호화"
parent: "크롬 계열 앱 공통 구조"
grand_parent: "기반 · 앱·메일 데이터 구조"
nav_order: 460
---

# 쿠키·비밀번호 암호화 (DPAPI·App-Bound Encryption)

> 위치: [크롬 계열 앱 공통 구조 (Chromium·Electron·WebView2)](index.md) > 쿠키·비밀번호 암호화

## 한 줄 요약

크롬 계열 앱은 쿠키·비밀번호 같은 값을 AES-256-GCM 으로 암호화하고, 암호화 키는 `Local State` 파일의 `os_crypt` 아래에 둡니다. 키는 데이터 보호 API (DPAPI) 로 보호한 키와 앱 바인딩 암호화 (App-Bound Encryption) 키 두 종류이고, 어느 키로 풀어야 하는지는 암호문 앞 3바이트(`v10`·`v20`)로 가립니다.

## 이 구조를 쓰는 아티팩트

앱 바인딩 암호화가 보호하는 값은 쿠키, 비밀번호, 결제 수단, IBAN, OAuth 토큰입니다 (xaitax 저장소 설명).
값이 든 파일과 칸, 파일마다의 해석은 [크롬 계열 브라우저](../../../02-artifacts/browsers/chrome-edge-whale/index.md) 에서 다룹니다.
`Local State` 파일의 위치와 나머지 키는 [프로필 폴더와 계열 브라우저 구분](user-data-profile-local-state.md) 에서 다룹니다.

`Local State` 에 든 키는 브라우저와 앱이 서로 달랐습니다. 아래 표는 Windows 11(빌드 26200) PC 한 대에서 본 결과입니다 (관찰).

| 앱 | `encrypted_key` | `app_bound_encrypted_key` |
|---|---|---|
| Chrome 153 | 있음 | 있음 |
| Edge 151 | 있음 | 있음 |
| WebView2 앱 3개 (새 Outlook·새 Teams·OneDrive) | 있음 | 없음 |
| Electron 앱 1개 (VS Code) | 있음 | 없음 |

관찰한 WebView2·Electron 앱에는 `encrypted_key` 와 `audit_enabled` 만 있었습니다. 앱 폴더를 찾는 법은 [Electron·WebView2 앱 데이터 위치](teams-discord-slack.md) 에서 다룹니다.

## 구조

> 그림 자리: `v10` 과 `v20` 이 풀리는 길. `v10` 은 사용자 DPAPI → `encrypted_key` → AES-256-GCM. `v20` 은 SYSTEM DPAPI → 사용자 DPAPI → `app_bound_encrypted_key` → (추가 단계, 확인 못 함) → AES-256-GCM. 두 길 모두 쿠키는 복호한 평문 앞 32바이트(도메인 SHA-256)를 떼어 냄

### Local State 의 키 두 개

두 키는 `Local State` 안에 base64 문자열로 들어 있고, base64 를 풀면 앞에 짧은 표시 문자열이 붙어 있습니다.

| 키 | base64 를 푼 앞부분 | 보호 방식 | 이 키로 푸는 암호문 |
|---|---|---|---|
| `os_crypt.encrypted_key` | `DPAPI` | 사용자 DPAPI 로 보호합니다 | `v10` |
| `os_crypt.app_bound_encrypted_key` | `APPB` | 사용자 DPAPI 로 한 번 감싸고, 다시 SYSTEM DPAPI 로 한 번 더 감쌉니다 | `v20` |

표의 보호 방식과 짝은 xaitax 저장소 설명에서 가져왔고, 관찰한 Chrome 153·Edge 151 에서도 base64 를 풀면 앞 바이트가 각각 `DPAPI`, `APPB` 였습니다. `os_crypt.audit_enabled` 키도 있었지만 (관찰) 뜻은 확인하지 못했습니다.

- Edge 에는 `os_crypt` 아래 키가 하나 더 있었습니다 (관찰). 이름과 관찰 내용은 [프로필 폴더와 계열 브라우저 구분](user-data-profile-local-state.md) 의 구분 단서 표에 있습니다.
- DPAPI 마스터 키와 블롭 구조는 [DPAPI 구조](../../protection/data-protection-api/index.md) 에서 다룹니다.

### 암호문 앞 3바이트

| 앞 3바이트 | 헥스 | 쓰는 키 |
|---|---|---|
| `v10` | `76 31 30` | `encrypted_key` (DPAPI 로 보호한 키) |
| `v20` | `76 32 30` | `app_bound_encrypted_key` |

두 방식 모두 AES-256-GCM 이고 (xaitax 저장소 설명), 논스 (Nonce) 는 12바이트, 인증 태그 (Authentication Tag) 는 16바이트입니다.

쿠키 DB 형식 버전 24 부터는 쿠키 값을 암호화하기 전에 앞에 도메인의 SHA-256 해시(32바이트)를 붙입니다 (Chromium 소스 `sqlite_persistent_cookie_store.cc`). 그래서 쿠키 값은 복호한 평문의 32바이트 뒤부터입니다. 이 32바이트는 `v10`·`v20` 과 상관없이 쿠키 DB 형식 버전에 따라 붙습니다. xaitax 저장소는 `v20` 쿠키에 32바이트 머리가 있다고만 적었습니다. 소스는 불러올 때 이 해시가 도메인과 맞지 않으면 그 쿠키를 버린다고 적습니다.

암호문 칸 안에서 논스·암호문·태그가 놓인 자리와 칸 이름은 파일마다 다르게 다룹니다. [크롬 계열 브라우저](../../../02-artifacts/browsers/chrome-edge-whale/index.md) 의 쿠키·저장 비밀번호 페이지를 봅니다.

`v10`·`v20` 이 아닌 값도 있을 수 있습니다. 접두사 없이 값 전체를 DPAPI 블롭으로 저장한 옛 방식이 알려져 있지만, 이 방식과 바뀐 버전은 이번에 원 출처로 확인하지 못했습니다.

### 앱 바인딩 암호화

Google 보안 블로그는 2024-07-30 에 "Improving the security of Chrome cookies on Windows" 라는 글을 올렸습니다. 본문은 이번에 가져오지 못해 제목과 날짜만 확인했고, 처음 들어간 브라우저 버전도 이번에 연 자료로 확인하지 못했습니다.

키를 풀 때는 브라우저의 권한 상승 서비스 (Elevation Service) 에 있는 COM 인터페이스를 불러야 합니다. 이름은 `IElevator` 이고, Chrome 144 이후는 `IElevator2` 입니다 (xaitax 저장소 설명). 이 서비스는 자기를 부른 프로그램의 실행 파일 경로를 검사한 뒤에 키를 내주므로 (xaitax 저장소 설명), 브라우저가 아닌 프로그램은 키를 받기 어렵게 만든 구조로 보입니다 (해석).

| 항목 | 내용 (xaitax 저장소 설명) |
|---|---|
| 보호하는 값 | 쿠키, 비밀번호, 결제 수단, IBAN, OAuth 토큰 |
| 쓰는 브라우저 | Chrome, Edge, Brave, Avast Secure Browser |
| Edge 의 차이 | `IElevatorEdge` 처럼 다른 인터페이스 이름을 씁니다 |

- 값 종류마다 언제부터 적용했는지는 확인하지 못했습니다. 자료에 "Chrome 144+" 표기가 있지만 어느 항목에 걸리는지 분명하지 않습니다.

## 읽는 법

1. **`Local State` 를 함께 수집합니다.** 쿠키·비밀번호 DB 만 있으면 키가 없습니다. 같은 User Data 폴더의 `Local State` 를 반드시 같이 가져옵니다.
2. **키 종류를 확인합니다.** 사본의 `Local State` 를 JSON 으로 열고 `os_crypt` 아래 키를 봅니다. `app_bound_encrypted_key` 가 없으면 `v20` 값도 없을 가능성이 큽니다 (해석). 그래도 DB 값을 직접 확인합니다.
3. **base64 를 풀어 앞부분을 봅니다.** `encrypted_key` 는 `DPAPI` 로, `app_bound_encrypted_key` 는 `APPB` 로 시작해야 합니다.
4. **DB 의 암호문 앞 3바이트를 셉니다.** 행마다 `v10`·`v20`·그 밖의 값을 세어 둡니다. 한 DB 에 두 방식이 섞일 수 있는지는 이번에 확인하지 못했습니다. 그래서 행마다 봅니다.
5. **`v10` 을 풉니다.** 사용자 DPAPI 마스터 키로 `encrypted_key` 의 `DPAPI` 뒤 부분을 풉니다. 그 결과가 AES-256-GCM 키입니다. DPAPI 마스터 키를 푸는 데 무엇이 필요한지는 [DPAPI 구조](../../protection/data-protection-api/index.md) 를 봅니다.
6. **`v20` 을 풉니다.** SYSTEM DPAPI 로 한 겹, 사용자 DPAPI 로 한 겹을 벗겨야 합니다. 그 뒤에 가공 단계가 더 있다는 설명이 있지만 이번에 확인하지 못했습니다. 쿠키 DB 형식 버전이 24 이상이면 쿠키의 복호한 평문 앞 32바이트를 떼어 냅니다. `v10` 쿠키도 같습니다.
7. **기록합니다.** 쓴 키의 종류, 마스터 키의 출처, 복호한 행 수와 못 푼 행 수를 적습니다.

### 헥스로 한 번 따라가기

아래 바이트는 **문자 코드로 만든 예시**입니다.
실제 검체에서 옮긴 값이 아닙니다.
`??` 는 파일마다 다른 바이트입니다.

```
encrypted_key 를 base64 로 푼 앞부분 (예시)
오프셋    00 01 02 03 04 05 06 07
00000000  44 50 41 50 49 ?? ?? ??   D P A P I 뒤에 사용자 DPAPI 로 보호한 값

app_bound_encrypted_key 를 base64 로 푼 앞부분 (예시)
00000000  41 50 50 42 ?? ?? ?? ??   A P P B 뒤에 두 겹으로 감싼 값

DB 의 암호문 칸 앞부분 (예시)
00000000  76 31 30 ?? ?? ?? ?? ??   v10 뒤에 논스·암호문·태그
00000000  76 32 30 ?? ?? ?? ?? ??   v20 뒤에 논스·암호문·태그
```

base64 규칙으로 셈하면 JSON 텍스트에서도 바로 알아볼 수 있습니다.

- `DPAPI` 로 시작하는 바이트열을 base64 로 적으면 첫 6글자가 늘 `RFBBUE` 입니다.
- `APPB` 로 시작하는 바이트열을 base64 로 적으면 첫 5글자가 늘 `QVBQQ` 입니다.

그 뒤 글자는 이어지는 바이트에 따라 달라지지만, 앞 글자만으로 `Local State` 를 텍스트로만 열어도 두 키가 어느 쪽인지 가릴 수 있습니다.

## 포렌식에서 중요한 점

### 디스크 이미지만 있을 때

아래는 xaitax 저장소 설명에서 끌어낸 해석입니다. 검체마다 결과가 다를 수 있습니다.

`v10` 은 사용자 DPAPI 마스터 키만 풀면 되고, `v20` 은 SYSTEM DPAPI 까지 풀어야 합니다. `v20` 은 그 뒤 가공 단계가 더 있다는 설명이 있으나 확인하지 못했으므로, 한 방식이 풀렸다고 다른 방식도 풀린다고 보지 않습니다.

관찰한 WebView2·Electron 앱에는 DPAPI 키만 있었으니 이런 앱은 사용자 DPAPI 로 풀릴 가능성이 큽니다. 그래도 값 앞 3바이트를 직접 확인합니다.

- 암호화한 증거 전반을 다루는 절차는 [암호화 증거 다루기](../../../03-techniques/analysis/encrypted-evidence/index.md) 에서 다룹니다.

### 켜진 PC 를 다룰 때

앱 바인딩 키는 브라우저의 권한 상승 서비스를 거쳐야 풀리는데, 이 서비스는 그 PC 에서만 돌아갑니다.

- 켜진 PC 에서 무엇을 먼저 확보할지는 [라이브 응답](../../../03-techniques/process-acquisition/live-response/index.md) 에서 다룹니다.

### 지운 값과 옛 값

암호문 칸은 DB 파일 안에 있고, 지운 행이 남는 자리는 [SQLite 데이터베이스](../../database-log-formats/sqlite/index.md) 에서 다룹니다. 지운 행에서 건진 암호문도 앞 3바이트로 방식을 가린 뒤 같은 키로 풉니다.

`Local State` 의 키가 바뀌면 옛 암호문은 지금 키로 풀리지 않을 수 있어서, 옛 `Local State` 는 [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에서 찾습니다. 키가 언제 바뀌는지는 확인하지 못했습니다.

### 보고서에 쓸 문장

복호한 값은 "수집 시점에 이 프로필의 DB 에 저장돼 있던 값" 이고, 언제 저장했는지와 언제 썼는지는 DB 의 시각 칸으로 따로 판단합니다. 못 푼 행이 있으면 행 수와 방식(`v10`·`v20`)을 함께 적습니다.

## 함정

- **DB 만 수집합니다.** `Local State` 가 없으면 `v10` 도 풀 수 없습니다.
- **모든 앱이 같은 키 구성이라고 봅니다.** 관찰한 브라우저에는 키가 두 개, WebView2·Electron 앱에는 하나였습니다. 폴더마다 `Local State` 를 봅니다.
- **`v20` 을 `v10` 방식으로 풉니다.** 키가 다르고 감싼 겹수도 다릅니다.
- **쿠키의 앞 32바이트를 값으로 적습니다.** 쿠키 DB 형식 버전 24 부터는 `v10`·`v20` 모두 복호한 평문 앞 32바이트가 도메인 해시입니다.
- **Chrome 용 도구를 Edge 에 그대로 씁니다.** Edge 는 권한 상승 서비스의 인터페이스 이름이 다릅니다. 도구가 어느 브라우저를 지원하는지 먼저 봅니다.
- **도입 버전 숫자로 방식을 짐작합니다.** 흔히 도는 도입 버전은 이번에 원 출처로 확인하지 못했습니다. `Local State` 의 키와 값 앞 3바이트를 직접 봅니다.
- **`APPB` 키가 있으니 모든 값이 `v20` 이라고 봅니다.** 관찰한 PC 에서 `v10`·`v20` 비율은 확인하지 않았습니다. 행마다 셉니다.

## 도구

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| 텍스트 편집기, JSON 조회 도구(jq 등) | `Local State` 의 `os_crypt` 키를 봅니다 |
| base64 변환 도구, 헥스 편집기 | 키의 앞부분(`DPAPI`·`APPB`)과 암호문 앞 3바이트를 봅니다 |
| SQLite 조회 도구 | 암호문 칸을 뽑아 방식별로 셉니다 |
| DPAPI 를 오프라인으로 푸는 공개 도구 | 사용자·SYSTEM 마스터 키로 키를 풉니다. 도구가 `v20` 을 지원하는지 먼저 확인합니다 |

복호 결과가 도구마다 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 참고 문헌

- GitHub xaitax, *Chrome App-Bound Encryption Decryption* (README. 연구용 도구 저장소이며 형식 설명만 참고했습니다) — https://github.com/xaitax/Chrome-App-Bound-Encryption-Decryption
- Chromium source, `net/extras/sqlite/sqlite_persistent_cookie_store.cc` (버전 기록 주석) — https://github.com/chromium/chromium/blob/main/net/extras/sqlite/sqlite_persistent_cookie_store.cc
- Google Security Blog, *Improving the security of Chrome cookies on Windows* (2024-07-30. 제목과 날짜만 확인) — https://security.googleblog.com/2024/07/improving-security-of-chrome-cookies-on.html
