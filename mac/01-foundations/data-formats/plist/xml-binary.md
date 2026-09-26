---
title: "XML·바이너리 plist"
parent: "속성 목록 파일"
grand_parent: "기반 · 데이터 저장 형식"
nav_order: 140
---

# XML·바이너리 plist (XML·bplist00)

속성 목록 파일 (Property List, plist)은 같은 값 구조를 XML 문서나 바이너리 파일로 저장하고, 바이너리 파일은 첫 8바이트가 `bplist00` 이며 파일 끝 32바이트 트레일러부터 거꾸로 따라 들어가며 읽습니다. 이 페이지는 두 형식의 구조와 손으로 읽는 순서, 손상되거나 손댄 파일을 가려낼 때 쓸 수 있는 읽기 검사 조건을 다룹니다.

## 이 형식을 쓰는 아티팩트

plist에 담을 수 있는 값은 배열(array), 데이터(data), 날짜(date), 사전(dict), 실수(real), 정수(integer), 문자열(string), 참·거짓(true·false)이고 [4], 형식은 XML과 바이너리 두 가지입니다 [1][4]. 앱 설정을 담는 기본 설정 파일은 [기본 설정 도메인과 캐시 (Defaults·cfprefsd)](defaults-cfprefsd.md)에서, 앱이 객체를 통째로 plist에 담는 방식은 [NSKeyedArchiver 풀기 (NSKeyedArchiver)](nskeyedarchiver.md)에서 다루고, 여기서는 두 방식이 공통으로 쓰는 저장 형식만 설명합니다.

바이너리 형식의 설명은 Apple이 공개한 CoreFoundation(CF) 소스를 기준으로 합니다 [1][2]. 이 소스는 저작권 표기가 2014~2015년인 옛 공개판이라서, macOS 10.15 Catalina 이후의 비공개 구현과는 세부가 다를 수 있습니다.

## 구조

### XML 형식

XML plist의 문법은 Apple의 DTD(`https://www.apple.com/DTDs/PropertyList-1.0.dtd`)가 정합니다 [4]. 루트 `plist` 요소 안에는 값이 하나만 들어가고, `version` 속성의 기본값은 `1.0` 입니다 [4]. 사전 `dict` 안에는 문자열 키 `key` 와 값이 한 쌍씩 번갈아 이어집니다 [4].

| 요소 | 내용을 적는 방식 [4] |
|---|---|
| `data` | Base64로 인코딩한 바이트 |
| `date` | ISO 8601의 일부인 `YYYY-MM-DDTHH:MM:SSZ`. 끝의 `Z` 는 UTC이고, 작은 단위는 생략할 수 있어서 그만큼 정밀도가 떨어짐 |
| `integer` | 10진수, 부호를 붙일 수 있음 |
| `real` | `(+\|-)? d+ (. d*)? (E (+\|-) d+)?` 형식의 실수 |
| `true`, `false` | 내용 없는 빈 요소 |

아래는 DTD에 맞춰 만든 예시이고, 실제 파일에서 나온 값이 아닙니다. 파일 머리에 붙는 XML 선언과 문서 형식 선언 줄은 예시에서 뺐습니다.

```xml
<plist version="1.0">
<dict>
  <key>Enabled</key>
  <true/>
  <key>Count</key>
  <integer>3</integer>
  <key>Blob</key>
  <data>AAEC</data>
  <key>Last</key>
  <date>2024-01-02T03:04:05Z</date>
</dict>
</plist>
```

### 바이너리 형식 — 전체 배치

바이너리 plist는 헤더, 객체 테이블, 오프셋 테이블, 트레일러가 이 순서로 붙은 파일이고, 여러 바이트로 된 정수·실수·날짜는 모두 big-endian으로 저장합니다 [1].

| 순서 | 부분 | 크기 | 내용 |
|---|---|---|---|
| 1 | 헤더 | 8바이트 | 매직 `bplist` 6바이트 + 버전 2바이트 (`CFBinaryPlistHeader`) [2] |
| 2 | 객체 테이블 | 가변 | 표식 바이트로 시작하는 객체들 [1] |
| 3 | 오프셋 테이블 | 객체 수 × 항목 크기 | 항목마다 파일 처음부터 객체까지의 바이트 오프셋 [1] |
| 4 | 트레일러 | 32바이트 | 테이블 크기와 위치 (`CFBinaryPlistTrailer`) [2] |

### 헤더와 버전 문자열

CF는 파일을 쓸 때 늘 `bplist00` 을 쓰지만, 읽을 때 받아들이는 머리는 시기마다 달랐습니다 [1].

| 시기(소스 주석 기준) | 읽을 때 받아들이는 머리 |
|---|---|
| Tiger 이전 | `bplist00` 만 |
| Leopard | `bplist00`, `bplist01` |
| Snow Leopard부터 | `bplist0?` (`?` 는 아무 글자 하나) |

실제 코드는 첫 7바이트 `bplist0` 만 비교합니다 [1]. 소스 주석에는 `v"1?"+ only` 라고 표시한 객체 형식도 있지만, `bplist1` 로 시작하는 버전이 실제로 어디에 쓰이는지 설명한 공개 자료는 없습니다.

### 트레일러 (파일 끝 32바이트)

트레일러는 파일 끝에서 트레일러 크기만큼 앞으로 간 자리에서 읽고, 64비트 값 세 개는 big-endian입니다 [1]. 필드 크기를 더하면 5+1+1+1+8+8+8 = 32바이트입니다 [2].

| 오프셋(트레일러 기준) | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 5 | `_unused` | 쓰지 않음 |
| 5 | 1 | `_sortVersion` | 소스에 설명 없음 |
| 6 | 1 | `_offsetIntSize` | 오프셋 테이블 항목 하나의 바이트 수 |
| 7 | 1 | `_objectRefSize` | 배열·사전 안에서 객체 참조 하나의 바이트 수 |
| 8 | 8 | `_numObjects` | 오프셋 테이블 항목 수, 곧 객체 수 |
| 16 | 8 | `_topObject` | 최상위 객체의 오프셋 테이블 번호 |
| 24 | 8 | `_offsetTableOffset` | 파일 처음부터 오프셋 테이블까지의 거리 |

CF가 파일을 쓸 때 `_topObject` 는 늘 0입니다 [1]. 배열이나 사전은 다른 객체를 파일 오프셋이 아니라 오프셋 테이블 번호로 가리키고, 이 번호 하나의 크기가 `_objectRefSize` 입니다 [1].

### 객체 표식 바이트

객체 테이블의 객체는 모두 표식 바이트(marker) 하나로 시작하고, 윗 4비트가 형식을, 아랫 4비트가 길이나 개수를 나타냅니다 [1][2]. `[v1?+]` 는 소스 주석이 버전 `1?` 이후 전용이라고 표시한 형식입니다.

| 표식(비트) | 값 | 형식 | 뒤따르는 것 |
|---|---|---|---|
| 0000 0000 | 0x00 | null | 없음 `[v1?+]` |
| 0000 1000 | 0x08 | false | 없음 |
| 0000 1001 | 0x09 | true | 없음 |
| 0000 1100 / 1101 | 0x0C / 0x0D | url (기준 URL 없음 / 있음) | `[v1?+]` |
| 0000 1110 | 0x0E | uuid | 16바이트 `[v1?+]` |
| 0000 1111 | 0x0F | fill (채움 바이트) | 없음 |
| 0001 0nnn | 0x1n | int | 2^nnn 바이트, big-endian |
| 0010 0nnn | 0x2n | real | 2^nnn 바이트, big-endian |
| 0011 0011 | 0x33 | date | 8바이트 float64, big-endian |
| 0100 nnnn | 0x4n | data | nnnn = 바이트 수, 1111이면 뒤에 int로 길이 |
| 0101 nnnn | 0x5n | ASCII 문자열 | nnnn = 글자 수, 1111이면 뒤에 int로 길이 |
| 0110 nnnn | 0x6n | 유니코드 문자열 | nnnn = 글자 수(1111이면 int), 글자마다 big-endian 2바이트(UTF-16) |
| 0111 nnnn | 0x7n | UTF-8 문자열 | `[v1?+]` |
| 1000 nnnn | 0x8n | uid | nnnn+1 바이트 |
| 1001 xxxx | — | 쓰지 않음 | |
| 1010 nnnn | 0xAn | array | 개수(1111이면 int), 그다음 객체 참조들 |
| 1011 nnnn | 0xBn | ordset | `[v1?+]` |
| 1100 nnnn | 0xCn | set | 개수 + 객체 참조들. 주석은 `[v1?+]` 로 표시하지만 표식 상수 `kCFBinaryPlistMarkerSet = 0xC0` 은 정의돼 있음 |
| 1101 nnnn | 0xDn | dict | 개수(1111이면 int), 키 참조 전부, 그다음 값 참조 전부 |
| 1110 xxxx, 1111 xxxx | — | 쓰지 않음 | |

사전은 XML과 달리 키 참조 N개가 먼저 모두 나오고 값 참조 N개가 그 뒤에 따로 이어져서, 같은 순번의 키와 값을 짝지어 읽습니다 [1]. uid 형식은 NSKeyedArchiver가 객체 사이 참조에 쓰고, 그 쓰임은 [NSKeyedArchiver 풀기 (NSKeyedArchiver)](nskeyedarchiver.md)에서 다룹니다.

버전 `00` 의 정수에는 따로 정한 규칙이 있습니다 [1]. 1·2·4바이트 정수는 부호 없는 값으로, 8바이트(와 16바이트) 정수는 부호 있는 값으로 읽고, 음수는 `00` 에서 늘 8바이트로 씁니다. 가장 짧은 표현이 아니어도 되고, 지금은 마지막 64비트만 의미가 있습니다. 정수는 16바이트까지 받아들이고, 쓸 때 128비트 수는 표식 `0x14` 뒤에 16바이트를 붙입니다 [1]. CF가 쓰는 정수는 값 크기에 맞춰 1·2·4·8바이트 가운데 가장 짧은 것을 고릅니다 [1].

### 날짜 값

바이너리의 date 객체에는 `CFAbsoluteTime`, 곧 2001년 1월 1일 00:00:00부터 지난 초를 float64로 넣고, CF는 쓸 때 `CFDateGetAbsoluteTime` 값을 그대로 넣습니다 [1][3]. `CFDate.h` 주석은 기준 시각을 "00:00:00 1 January 2001" 로만 적지만 [3], Apple의 `CFAbsoluteTime` 문서는 기준을 "1 Jan 2001 00:00:00 GMT" 로 밝히고 있어서 [5] 이 값은 현지 시각이 아니라 UTC 기준으로 풉니다. 1970년 기준 유닉스 시각과의 차이를 계산하면 978,307,200초이고, 헤더에는 이 차이를 담는 상수 `kCFAbsoluteTimeIntervalSince1970` 이 선언돼 있지만 값은 적혀 있지 않습니다 [3]. 다른 시각 형식과 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../value-decoding/mac-time-values.md)에서 다룹니다.

XML의 `date` 는 UTC(`Z`) 문자열이고 초 단위까지만 적습니다 [4].

## 읽는 법

아래 바이트는 실제 데이터가 아니라 명세 [1][2]에 맞춰 만든 예시입니다. 최상위 사전 하나에 키 `key` 와 값 `true` 가 한 쌍 들어 있는 51바이트 파일입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
000000  62 70 6C 69 73 74 30 30 D1 01 02 53 6B 65 79 09   bplist00...Skey.
000010  08 0B 0F 00 00 00 00 00 00 01 01 00 00 00 00 00   ................
000020  00 00 03 00 00 00 00 00 00 00 00 00 00 00 00 00   ................
000030  00 00 10                                          ...
```

1. 첫 8바이트 `62 70 6C 69 73 74 30 30` 이 `bplist00` 이라서 바이너리 plist입니다.
2. 파일 끝 32바이트(0x13~0x32)를 트레일러로 읽습니다. 0x19의 `_offsetIntSize` 는 1, 0x1A의 `_objectRefSize` 는 1, 0x1B~0x22의 `_numObjects` 는 3, 0x23~0x2A의 `_topObject` 는 0, 0x2B~0x32의 `_offsetTableOffset` 은 0x10입니다.
3. 오프셋 테이블은 0x10에서 시작하고 항목 크기가 1바이트라서 `08 0B 0F` 세 항목을 읽고, 객체 0·1·2가 각각 0x08·0x0B·0x0F에 있습니다.
4. 최상위 객체는 `_topObject` 0번이라서 0x08로 갑니다. 표식 `D1` 은 윗 4비트가 1101(dict)이고 아랫 4비트가 1이라서 한 쌍짜리 사전이고, 참조 크기가 1바이트라서 키 참조 `01`, 값 참조 `02` 가 차례로 이어집니다.
5. 객체 1(0x0B)의 표식 `53` 은 ASCII 문자열 3글자라서 `6B 65 79`, 곧 `key` 이고, 객체 2(0x0F)의 `09` 는 true입니다.
6. 길이를 맞춰 봅니다. 헤더 8 + 객체 데이터 8(3+4+1) + 오프셋 테이블 3 + 트레일러 32 = 51바이트라서 파일 크기와 같습니다.

## 포렌식에서 중요한 점

CF는 바이너리 plist를 읽기 전에 아래 조건을 검사하고, 하나라도 어긋나면 읽기에 실패합니다 [1]. 도구가 파일을 열지 못할 때 어느 조건에 걸렸는지 손으로 따져 보면, 파일이 잘렸는지, 뒤에 다른 바이트가 붙었는지, 값이 어긋났는지를 가려낼 수 있습니다.

| 검사 대상 | 통과 조건 [1] |
|---|---|
| 파일 길이 | 트레일러 크기 + 8 + 1 이상 |
| 객체 수 | 1 이상 |
| `_topObject` | 객체 수보다 작음 |
| `_offsetTableOffset` | 9 이상 |
| `_offsetIntSize`, `_objectRefSize` | 1 이상 |
| 전체 길이 | 8 + 객체 데이터 크기 + 오프셋 테이블 크기 + 트레일러 크기와 같음 |
| 참조 크기 | `_objectRefSize` 로 객체 수를 나타낼 수 있어야 함 |
| 오프셋 항목 크기 | `_offsetIntSize` 로 오프셋 테이블 위치까지 닿을 수 있어야 함 |

전체 길이 검사 때문에 이 판의 CF는 뒤에 쓰레기 바이트가 붙은 파일을 받아들이지 않습니다 [1]. 트레일러를 파일 끝에서 읽는 구조라서, 비할당 영역에서 카빙한 조각은 끝을 정확히 잘라야 합니다. 트레일러 값으로 따지면 파일 끝은 `_offsetTableOffset` + `_numObjects` × `_offsetIntSize` + 32 자리이고, 이 계산은 위 길이 검사를 거꾸로 적용한 것입니다.

그 밖의 읽기 규칙도 손상이나 조작을 따질 때 쓸 수 있습니다. 중첩 깊이가 15를 넘으면 순환 참조를 막으려고 방문한 객체를 모아 검사하고, 사전의 키는 기본형(primitive) 객체여야 하며, uid 값이 32비트 부호 없는 정수의 최댓값을 넘으면 읽기에 실패합니다 [1]. 트레일러의 `_unused` 바이트가 0이 아니어서 실패하는 경우는 Leopard뿐이고 Tiger 이전과 Leopard 이후에는 이 검사가 없어서 [1], 이 5바이트에 다른 값이 있어도 지금의 읽기 결과만으로는 드러나지 않습니다.

CF가 쓴 파일이라면 머리는 `bplist00`, `_topObject` 는 0이고 정수는 가장 짧은 크기로 들어 있습니다 [1]. 이와 다른 파일은 이 판의 CF가 아닌 다른 프로그램이 썼을 가능성을 따져 볼 단서가 되지만, 최신 macOS의 쓰기 동작은 이 판과 다를 수 있어서 이것만으로 조작을 단정하지 않습니다.

## 함정

- **정수 부호**: 버전 `00` 에서 1·2·4바이트 정수는 부호 없이, 8바이트 정수는 부호 있게 읽습니다 [1]. 같은 비트라도 크기에 따라 음수가 되기도 하고 안 되기도 해서, 직접 짠 파서는 이 규칙을 따라야 도구 결과와 맞습니다.
- **유니코드 문자열 길이**: 표식의 nnnn은 바이트 수가 아니라 UTF-16 글자 수라서 실제 바이트는 그 두 배입니다 [1].
- **사전의 순서**: 키와 값이 번갈아 나오지 않고 키 참조 묶음 뒤에 값 참조 묶음이 옵니다 [1].
- **날짜 정밀도**: 바이너리 날짜는 float64 초이고 XML 날짜는 초 단위 문자열입니다 [1][4]. XML 날짜는 초 단위까지만 적어서 바이너리를 XML로 바꾸면 초 아래 값이 사라질 수 있으니, 초 아래 값이 필요하면 원본 바이너리 값을 기준으로 삼습니다.
- **소스의 판**: 이 페이지의 바이너리 규칙은 2014~2015년 공개판 CF 소스 기준입니다 [1][2]. 최신 macOS 데이터에서 다른 모습을 보면 관찰로 적고 확인 범위를 밝힙니다.
- **변환본과 원본**: 형식을 바꾸는 도구는 새 파일을 만들기 때문에 원본의 바이트 배치(오프셋 테이블, 채움 바이트, 쓰지 않는 자리)가 사본에 그대로 남는다고 볼 수 없습니다. 변환은 작업 사본으로 하고, 위 검사 조건은 원본 파일로 따집니다.

## 도구

plist를 보여 주거나 형식을 바꾸는 도구는 어떤 것을 쓰든 결과에서 한두 값을 골라 위 읽는 법 순서대로 헥스와 맞춰 보고, 도구를 검증하는 방법은 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)을 따릅니다. 지워진 plist를 되살리는 방법은 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.

## 참고 문헌

1. Apple CF 공개 소스, CFBinaryPList.c (저작권 2000-2014/2015) — https://raw.githubusercontent.com/apple-oss-distributions/CF/main/CFBinaryPList.c
2. Apple CF 공개 소스, ForFoundationOnly.h (CFBinaryPlistHeader·CFBinaryPlistTrailer·표식 상수) — https://raw.githubusercontent.com/apple-oss-distributions/CF/main/ForFoundationOnly.h
3. Apple CF 공개 소스, CFDate.h — https://raw.githubusercontent.com/apple-oss-distributions/CF/main/CFDate.h
4. Apple, PropertyList-1.0.dtd — https://www.apple.com/DTDs/PropertyList-1.0.dtd
5. Apple Developer Documentation, CFAbsoluteTime — https://developer.apple.com/documentation/corefoundation/cfabsolutetime
