# 저장 비밀번호 (logins.json·key4.db)

## 한 줄 요약

파이어폭스는 사이트 로그인 정보를 프로필 본 폴더의 `logins.json` 에 저장합니다. 아이디와 비밀번호는 암호화되어 있습니다. 그 값을 푸는 키는 같은 폴더의 `key4.db` 에 들어 있습니다. 어느 사이트에 로그인 정보를 저장했는지는 `logins.json` 의 주소로 바로 알 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

- 파이어폭스는 사용자가 저장하기로 한 로그인 정보를 프로필에 담아 둡니다. 다음에 같은 사이트를 열면 아이디와 비밀번호를 자동으로 채우려는 것입니다.
- 로그인 하나에는 사이트 주소, 암호화한 아이디, 암호화한 비밀번호가 있습니다.
- 아이디와 비밀번호를 푸는 키는 `key4.db` 에 있습니다. 이 키 자체도 암호화되어 있습니다.
- 기본 비밀번호 (primary password) 를 걸어 두면 그 비밀번호를 알아야 키를 풀 수 있습니다. 걸어 두지 않으면 빈 문자열로 키를 만듭니다.

## 위치와 버전별 차이

- 위치는 프로필 본 폴더입니다. 프로필 폴더를 찾는 법은 [프로필 구조 (profiles.ini·prefs.js)](profiles-ini-prefs-js.md) 에서 다룹니다.
- 파일 이름과 암호 방식은 파이어폭스 버전을 따릅니다. 아래는 공개 도구 firepwd 의 설명에서 확인한 것입니다.

| 파이어폭스 판 | 로그인 파일 | 키 파일 |
|---|---|---|
| 32 미만 | `signons.sqlite` | `key3.db` |
| 32 이상 | `logins.json` | `key3.db` |
| 58.0.2 이상 | `logins.json` | `key4.db` |

- Firefox 75.0 이상의 `key4.db` 는 SHA-1, PBKDF2-HMAC-SHA256, AES-256-CBC 를 씁니다.
- Firefox 144.0 이상의 `logins.json` 은 3DES 대신 AES-256 을 씁니다.
- `key3.db` 는 BSD DB 파일입니다. SQL 없이 바이너리로 읽습니다. `key4.db` 는 SQLite 입니다.

## 구조

### `logins.json`

- `logins.json` 은 텍스트 JSON 파일입니다.
- 공개 도구 firepwd 가 읽는 칸은 `hostname`, `encryptedUsername`, `encryptedPassword` 입니다.
- `hostname` 은 평문입니다. 곧 어느 사이트에 로그인 정보를 저장했는지는 값을 풀지 않아도 알 수 있습니다.
- `encryptedUsername`·`encryptedPassword` 는 암호화한 값입니다.
- 그 밖의 칸(`httpRealm`, `formSubmitURL`, `timeCreated`, `timeLastUsed`, `timePasswordChanged`, `timesUsed` 등)과 시각 단위는 이번 조사에서 확인하지 못했습니다.

### `key4.db`

`key4.db` 는 SQLite 파일입니다. 페이지와 레코드를 읽는 법은 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다. 로그인 값을 푸는 키가 여기에 두 조각으로 들어 있습니다.

| 표 | 칸 | 담는 것 |
|---|---|---|
| `metadata` | `item1` | 전역 솔트 (global salt) 입니다 |
| `metadata` | `item2` | 암호화한 확인값입니다. 풀면 `password-check` 문자열이 나옵니다 |
| `nssPrivate` | `a11` | CKA_VALUE 입니다. 암호화한 마스터 키입니다 |
| `nssPrivate` | `a102` | CKA_ID 입니다. 키를 가리키는 식별자입니다 |

- `metadata` 의 행은 `id = 'password'` 로 고릅니다.
- 파이어폭스 비밀번호 키의 CKA_ID 는 `f8000000000000000000000000000001` 입니다. `nssPrivate` 에서 이 식별자를 찾으면 됩니다.
- 확인값(`item2`)을 풀면 `password-check` 뒤에 `02 02` 두 바이트가 붙은 값이 나와야 합니다. 이 값이 맞으면 기본 비밀번호가 맞은 것입니다.
- 전역 솔트와 기본 비밀번호로 중간 키를 만듭니다. 암호 방식 버전에 따라 HMAC-SHA1 이나 PBKDF2-HMAC-SHA256 을 씁니다. 이 중간 키로 마스터 키를 풉니다. 마스터 키로 `logins.json` 의 값을 풉니다.

### 쓰이는 ASN.1 OID

`key4.db` 와 `logins.json` 의 암호화 값 안에는 어떤 방식을 썼는지 알려 주는 ASN.1 식별자 (OID) 가 들어 있습니다. firepwd 의 설명에서 확인한 값은 아래와 같습니다.

| OID | 뜻 |
|---|---|
| 1.2.840.113549.1.12.5.1.3 | 3DES 기반 PBE |
| 1.2.840.113549.1.5.13 | PBES2 |
| 1.2.840.113549.1.5.12 | PBKDF2 |
| 1.2.840.113549.2.9 | hmacWithSHA256 |
| 2.16.840.1.101.3.4.1.42 | AES-256-CBC |

## 증거로서 의미

### 증명하는 것

- `logins.json` 에 행이 있으면 이 프로필에 그 사이트의 로그인 정보가 저장돼 있었습니다. 사용자가 직접 저장했는지, 다른 브라우저에서 가져왔는지, 동기화로 받았는지는 다른 흔적으로 따로 가립니다.
- `hostname` 이 평문이므로 어느 사이트에 계정을 저장했는지는 값을 풀지 않아도 목록으로 뽑을 수 있습니다.
- 확인값이 빈 기본 비밀번호로 풀리면 이 프로필에는 기본 비밀번호가 걸려 있지 않습니다.

### 증명하지 못하는 것

- 저장된 값이 지금도 맞는 비밀번호라는 뜻은 아닙니다. 사용자가 사이트에서 비밀번호를 바꿨을 수 있습니다.
- 로그인 정보를 저장했다고 실제로 그 사이트에 로그인했다는 뜻은 아닙니다.
- 키보드 앞의 사람이 누구인지는 알 수 없습니다.
- 기본 비밀번호가 걸려 있으면 그 비밀번호 없이는 값을 풀 수 없습니다. 확인값 비교가 이 점을 뒷받침합니다.

보고서에는 "그 사이트에 로그인했다" 대신 "이 프로필의 `logins.json` 에 그 사이트의 저장 로그인이 있고, 저장 아이디는 이 값이다" 처럼 씁니다. 값을 풀지 못했으면 사이트 목록만 씁니다.

## 시각 해석

- `logins.json` 의 시각 칸(`timeCreated`·`timeLastUsed`·`timePasswordChanged`)은 1970년 기준 밀리초로 알려져 있습니다. 이번 조사에서 소스로 확인하지는 못했습니다. 검체에서 다른 아티팩트의 시각과 맞춰 확인합니다.
- 변환은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.

## 함정과 한계

- **원본을 브라우저로 열지 않습니다.** 파이어폭스로 프로필을 열면 파일이 바뀝니다. 해시를 기록한 사본으로 분석합니다.
- **`logins.json` 과 `key4.db` 는 짝입니다.** 값을 풀려면 두 파일이 같은 프로필의 것이어야 합니다. 한쪽만 수집하면 값을 풀 수 없습니다.
- **기본 비밀번호가 걸려 있으면 그 비밀번호가 필요합니다.** 확인값이 빈 문자열로 풀리지 않으면 기본 비밀번호가 걸린 것입니다. 이때는 사이트 목록만 뽑을 수 있습니다. 암호를 다루는 절차는 [암호화 증거 다루기](../../../03-techniques/analysis/encrypted-evidence/index.md) 를 참고합니다.
- **키를 못 풀어도 할 수 있는 일이 많습니다.** `hostname` 은 평문입니다. 어느 사이트에 계정을 저장했는지 목록으로 뽑아 다른 흔적과 맞춰 봅니다.
- **Windows 계정 비밀번호 없이도 풀 수 있습니다.** 기본 비밀번호가 없으면 firepwd 는 `key4.db` 와 `logins.json` 두 파일만으로 값을 풉니다. 크롬 계열은 사용자 [DPAPI](../../../01-foundations/protection/data-protection-api/index.md) 로 키를 보호하므로 Windows 쪽 키가 필요합니다. 두 방식을 섞어 생각하지 않습니다.
- **버전마다 암호 방식이 다릅니다.** `key4.db` 인지 `key3.db` 인지, 3DES 인지 AES-256 인지 먼저 확인합니다. 도구가 옛 방식만 알면 새 파일에서 실패합니다.
- **지운 로그인은 `logins.json` 에서 사라집니다.** 옛 로그인을 찾으려면 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md), 섀도 복사본, 메모리도 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

`key4.db` 의 확인값을 풀면 아래 문자열이 나와야 합니다. 이 값은 명세로 만든 예시입니다. 특정 검체에서 나온 값이 아닙니다.

```
70 61 73 73 77 6F 72 64 2D 63 68 65 63 6B 02 02
= "password-check" + 02 02
```

- 빈 기본 비밀번호로 확인값을 풀어 이 바이트가 나오면 기본 비밀번호가 걸려 있지 않다는 뜻입니다.
- `nssPrivate` 에서 CKA_ID 가 `f8000000000000000000000000000001` 인 행을 찾으면 그 행의 CKA_VALUE 가 암호화한 마스터 키입니다.

### 공개 도구로 한 번

- `logins.json` 과 `key4.db` 를 함께 사본으로 뜹니다. 두 파일은 짝이라 함께 있어야 합니다.
- firepwd 는 NSS 라이브러리 없이 파이썬(pyasn1, PyCryptodome)으로 `key3.db`·`key4.db` 와 `logins.json` 을 읽습니다. 기본 비밀번호가 빈 프로필이면 이 도구로 사이트별 아이디와 비밀번호를 얻습니다.
- 도구가 뽑은 `hostname` 목록을 `logins.json` 을 텍스트로 열어 직접 센 사이트 수와 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 쿠키 | 같은 사이트의 로그인 쿠키가 있는지, 그 시각을 봅니다 | [쿠키 (cookies.sqlite)](cookies-sqlite.md) |
| 방문·다운로드·즐겨찾기 | 저장한 사이트를 실제로 방문한 기록이 있는지 봅니다 | [places.sqlite](places-sqlite.md) |
| 양식 기록 | 로그인 창에 친 아이디가 양식 기록에도 남았는지 봅니다 | [양식 기록 (formhistory.sqlite)](formhistory-sqlite.md) |
| 자격 증명 관리자와 볼트 | 같은 사이트의 자격 증명이 윈도 쪽에도 저장됐는지 봅니다 | [자격 증명 관리자와 볼트](../../credentials/credential-manager-windows-vault.md) |
| 다른 브라우저 저장 비밀번호 | 같은 사이트 계정을 다른 브라우저에도 저장했는지 봅니다 | [크롬 계열 저장 비밀번호](../chrome-edge-whale/login-data.md) |

## 실습

파이어폭스를 쓴 공개 검체(NIST CFReDS 등)에서 프로필 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. `logins.json` 을 텍스트로 열어 `hostname` 을 모읍니다. 몇 개 사이트의 로그인이 저장돼 있습니까?
2. 키 파일이 `key4.db` 입니까, `key3.db` 입니까? 파이어폭스 판을 짐작할 수 있습니까?
3. `key4.db` 의 `metadata` 확인값을 빈 기본 비밀번호로 풀 수 있습니까? 기본 비밀번호가 걸려 있습니까?
4. 저장한 사이트를 방문 기록·쿠키와 맞춰 봅니다. 로그인은 저장했는데 방문 기록에 없는 사이트가 있습니까?

## 참고 문헌

1. lclevy, *firepwd — README* (GitHub — 버전별 파일, CKA_ID, ASN.1 OID, 공개 도구 설명). https://github.com/lclevy/firepwd
2. lclevy, *firepwd.py* (master 가지 — `metadata`·`nssPrivate` 조회, 확인값, `logins.json` 칸, 키 풀이 흐름). https://raw.githubusercontent.com/lclevy/firepwd/master/firepwd.py
