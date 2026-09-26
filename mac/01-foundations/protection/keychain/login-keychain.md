---
title: "로그인 키체인 파일"
parent: "키체인"
grand_parent: "기반 · 보안·보호"
nav_order: 410
---

# 로그인 키체인 파일 (login.keychain-db)

로그인 키체인은 사용자마다 하나씩 있는 파일 기반 키체인 (file-based keychain)이고, 빅엔디언으로 된 20바이트 파일 머리 뒤로 레코드 종류별 표가 이어지며, 항목의 속성과 암호화된 비밀 값이 그 표의 레코드에 들어 있습니다.

## 이 형식을 쓰는 아티팩트

파일 기반 키체인 형식은 사용자의 로그인 키체인뿐 아니라 시스템 전체가 쓰는 System 키체인에도 쓰이고, System 키체인은 [시스템·로컬 항목 키체인 (System·Local Items)](system-local-items.md)에서 다룹니다. 사용자 키체인 경로는 아래와 같습니다 [2].

```
/Users/<사용자>/Library/Keychains/login.keychain
/Users/<사용자>/Library/Keychains/login.keychain-db
```

확장자는 macOS 10.12에서 `.keychain` 에서 `.keychain-db` 로 바뀌었습니다 [1]. 이 이름 변경이 내부 형식이 바뀐 것을 뜻하는지는 밝혀지지 않았으니 [1], 파일 이름만 보고 형식 차이를 단정하지 않습니다.

iCloud 키체인처럼 동기화하는 항목은 데이터 보호 키체인 (data protection keychain)에 들어가고 이 파일에는 들어가지 않습니다 [4]. 그래서 한 사용자의 저장된 암호를 살필 때 로그인 키체인만 보면 빠지는 항목이 생기고, 두 구현의 차이는 [키체인 (Keychain)](index.md) 허브에 정리해 두었습니다.

## 구조

### 파일 머리 (20바이트)

숫자는 모두 빅엔디언으로 저장합니다 [1].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 시그니처 `kych` [1][3] |
| 4 | 2 | 주 버전(1) |
| 6 | 2 | 부 버전(0) |
| 8 | 4 | 알 수 없음(값은 16) |
| 12 | 4 | 표 배열 (tables array) 오프셋 |
| 16 | 4 | 알 수 없음 |

표마다 머리가 따로 있고, 그 안에 레코드 수와 레코드 오프셋이 들어 있습니다. 레코드 오프셋은 파일 처음이 아니라 표 머리가 시작하는 자리를 기준으로 셉니다 [1].

### 표와 레코드 종류

표 하나에는 한 종류의 레코드가 모이고, 종류 값은 `CSSM_DL_DB_RECORD_*` 상수로 나타냅니다. 응용이 정의한 종류는 최상위 비트 0x80000000이 켜져 있고, 키 표 세 종류는 이 비트가 꺼진 값을 씁니다 [1].

| 값 | 종류 |
|---|---|
| 0x80000000 | GENERIC_PASSWORD (일반 암호) |
| 0x80000001 | INTERNET_PASSWORD (인터넷 암호) |
| 0x80000002 | APPLESHARE_PASSWORD (AppleShare 암호) |
| 0x80001000 | X509_CERTIFICATE (X.509 인증서) |
| 0x80008000 | METADATA |
| 0x0000000F | PUBLIC_KEY (공개 키) |
| 0x00000010 | PRIVATE_KEY (개인 키) |
| 0x00000011 | SYMMETRIC_KEY (대칭 키) |

chainbreaker도 이 여덟 종류의 표를 읽습니다 [3]. 레코드 안의 속성 이름과 뜻은 [항목과 접근 제어 (Items·ACL)](items-acl.md)에서 다룹니다.

### 날짜 속성

생성 시각(`cdat`)과 수정 시각(`mdat`) 속성은 숫자가 아니라 `YYYYMMDDhhmmssZ` 모양의 문자열이고, 끝 문자까지 합쳐 16바이트를 차지합니다 [1]. 끝의 `Z` 가 보여 주듯 UTC 문자열이라서 맥 절대 시각이나 유닉스 시각으로 풀면 틀린 값이 나옵니다. 다른 시각 형식과의 차이는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../value-decoding/mac-time-values.md)에 있습니다.

이 값이 항목을 처음 만든 시각과 마지막으로 바꾼 시각을 그대로 뜻하는지, 동기화하거나 다른 키체인에서 가져올 때 새로 쓰이는지는 공개 자료가 없습니다. 그래서 보고서에는 "이 항목의 `mdat` 속성 값은 이 시각(UTC)이다" 처럼 기록된 값만 씁니다.

### 암호화한 부분

아래 내용은 Apple 공식 명세가 아니라 chainbreaker 코드의 구현입니다 [3]. chainbreaker는 3DES CBC로 풀고, 키는 PBKDF2(SHA-1, 1000회)로 24바이트를 만들며, 블록 크기는 8바이트이고, 소금(salt)은 DB 블롭의 Salt 필드에서 가져옵니다.

| 블롭 | 코드가 읽는 필드 |
|---|---|
| DB 블롭 | StartCryptoBlob, TotalLength, IV, Salt |
| 키 블롭 | CommonBlob.Magic, TotalLength, StartCryptoBlob, IV |

키체인을 푸는 수단은 키체인 암호, 메모리에서 얻은 마스터 키, 잠금 해제 파일(SystemKey) 세 가지이고, 셋 다 없으면 메타데이터와 암호화된 내용만 보입니다 [2]. 메모리에서 키를 얻는 과정은 [메모리 분석 (Memory Forensics)](../../../03-techniques/analysis/memory-forensics/index.md)에서, 암호를 모르는 증거를 다루는 방법은 [암호화된 증거 다루기 (Encrypted Evidence)](../../../03-techniques/analysis/encrypted-evidence/index.md)에서 다룹니다.

## 읽는 법

### 헥스로 한 번

아래 바이트는 실제 데이터가 아니라 명세 [1]에 맞춰 만든 예시입니다. 0x08~0x0B의 `00 00 00 10` 은 값 16이 들어가는 필드이지만 뜻은 알려지지 않았고, `??` 는 값도 뜻도 알려지지 않은 필드, `TT` 는 표 배열 오프셋 자리입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
000000  6B 79 63 68 00 01 00 00 00 00 00 10 TT TT TT TT   kych............
000010  ?? ?? ?? ??                                       ....
```

1. 0x00~0x03의 `6B 79 63 68` 은 ASCII로 `kych` 라서 파일 기반 키체인 파일입니다.
2. 0x04~0x05의 `00 01` 은 주 버전 1이고, 0x06~0x07의 `00 00` 은 부 버전 0입니다. 빅엔디언이라 앞 바이트가 높은 자리입니다.
3. 0x0C~0x0F의 `TT TT TT TT` 를 빅엔디언 32비트 정수로 읽어 표 배열이 시작하는 자리를 찾습니다.
4. 표 배열에서 각 표 머리로 가서 레코드 수와 레코드 오프셋을 읽고, 레코드 오프셋에 표 머리의 시작 자리를 더해 레코드를 찾습니다.
5. chainbreaker는 레코드 오프셋이 0이 아니고 4의 배수일 때만 쓸 수 있는 값으로 봅니다(ATOM_SIZE = 4) [3]. 이 조건에 맞지 않는 오프셋이 나오면 손상이나 잘못 읽은 자리를 먼저 의심합니다.

날짜 속성은 `20240101123000Z` 처럼 15글자 뒤에 끝 문자 한 바이트가 붙는 모양이고, 이 값도 형식을 보이려고 만든 예시입니다.

### 공개 도구로 한 번

chainbreaker(n0fate, GPL v2)는 파일 기반 키체인을 읽는 공개 도구이고, 지원 범위는 OS X 10.6 Snow Leopard부터 macOS 13 Ventura까지입니다 [2]. 푸는 수단이 있으면 인터넷 암호, 일반 암호, 개인 키, 공개 키, X.509 인증서, 보안 메모(secure note), AppleShare 암호를 꺼내 보여 주고, 없으면 메타데이터만 보여 줍니다 [2]. 형식을 직접 따라가려면 libyal dtformats 문서 [1]를 함께 봅니다. 도구 결과를 증거로 쓰기 전에 거쳐야 할 확인은 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)에 있습니다.

## 포렌식에서 중요한 점

키체인을 풀 수단이 없어도 메타데이터는 보여서, 이 사용자가 어떤 서비스와 서버에 쓸 계정을 저장해 두었는지 알 수 있습니다 [2]. 비밀 값까지 보려면 풀 수단이 필요하고, 그중 마스터 키는 메모리에서 얻는 수단이라서 메모리를 확보할지를 [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md) 단계에서 먼저 판단합니다. 파일을 옮길 때는 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)의 절차대로 원본을 바꾸지 않고 복사합니다.

이 형식에서 지운 레코드가 어떻게 남는지와 비정상 종료 뒤의 모양은 실제 데이터로 확인해야 합니다.

## 함정

파일 머리의 숫자는 빅엔디언이라서, 리틀엔디언으로 읽으면 표 배열 오프셋부터 틀어집니다. 날짜 속성은 문자열이라서 숫자 시각 변환기에 넣지 않습니다.

암호화 방식은 도구 코드에서 나온 것이라 Apple이 보증한 명세가 아니고, chainbreaker의 지원 범위가 macOS 13 Ventura까지라서 그 뒤 버전의 파일은 결과를 따로 검증합니다. 키체인 접근 (Keychain Access) 앱은 파일 기반 키체인과 데이터 보호 키체인을 함께 보여 주어서 [4], 앱 화면과 파일 분석 결과가 다르면 데이터 보호 키체인 쪽을 함께 확인합니다.

## 참고 문헌

1. libyal dtformats — MacOS keychain database file format — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/MacOS%20keychain%20database%20file%20format.asciidoc
2. chainbreaker README (n0fate) — https://github.com/n0fate/chainbreaker
3. chainbreaker 소스 `chainbreaker/__init__.py` — https://raw.githubusercontent.com/n0fate/chainbreaker/master/chainbreaker/__init__.py
4. Apple, TN3137: On Mac keychain APIs and implementations (2022-11-01) — https://developer.apple.com/tutorials/data/documentation/technotes/tn3137-on-mac-keychains.json
