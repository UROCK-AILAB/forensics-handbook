---
title: "프로토콜 버퍼"
parent: "기반 · 데이터 저장 형식"
nav_order: 170
---

# 프로토콜 버퍼 (Protocol Buffers)

## 한 줄 요약

프로토콜 버퍼 (Protocol Buffers, protobuf) 는 필드 번호와 값만 이어 붙인 이진 직렬화 형식이고, 필드 이름과 선언 형식은 파일에 들어 있지 않아 스키마(`.proto`) 없이 읽으면 번호와 값의 겉모양까지만 알 수 있습니다.

인코딩 규칙은 protobuf 공식 문서에 공개돼 있고[1], 이 페이지의 구조 설명은 그 문서를 따릅니다.

## 이 형식을 쓰는 아티팩트

iOS 에서 이 형식을 가장 자주 만나는 곳은 [바이옴](../../02-artifacts/app-usage/biome/index.md)입니다. 바이옴의 [SEGB](segb.md) 파일은 기록마다 헤더 뒤에 protobuf 페이로드를 붙이고[2][3], iOS 16 에서 쓰던 protobuf 구조를 iOS 17 에서도 그대로 쓰는 스트림이 많습니다[2]. Apple 이 이 페이로드의 스키마를 공개하지 않았기 때문에, 바이옴 페이로드는 대개 스키마 없이 필드 번호로 읽습니다.

그 밖의 iOS 아티팩트 가운데 어디가 protobuf 를 쓰는지는 이 페이지의 출처로 확인하지 못했습니다. 예를 들어 실제 아이폰 로컬 백업의 `AppDomainGroup-group.com.apple.notes` 영역에는 `NoteStore.sqlite` 가 있고, 그 안 `ZICNOTEDATA` 표에 `ZDATA` 칸이 있습니다. 값을 읽지 않았기 때문에 이 칸이 protobuf 인지는 알 수 없고, 메모 본문의 저장 방식은 [메모](../../02-artifacts/mail-cloud/notes.md)에서 다룹니다. plist 의 bytes 값처럼 겉으로 형식을 알 수 없는 이진 값을 만나면 protobuf 도 후보에 넣고 아래 규칙으로 맞춰 봅니다. plist 쪽 사례는 [속성 목록 파일](plist.md)에 있습니다.

## 구조

### 태그

protobuf 메시지는 "태그 + 값" 이 되풀이되는 모양입니다. 태그는 varint 하나이고, 값은 `(필드 번호 << 3) | wire type` 입니다[1]. 곧 태그의 아래 3비트가 wire type 이고, 나머지 위 비트가 필드 번호입니다.

| wire type | 이름 | 싣는 선언 형식 | 값 모양 |
|---|---|---|---|
| 0 | VARINT | int32, int64, uint32, uint64, sint32, sint64, bool, enum | varint |
| 1 | I64 | fixed64, sfixed64, double | 8바이트 |
| 2 | LEN | string, bytes, 하위 메시지, packed repeated | 길이 varint + 내용 |
| 3 | SGROUP | 그룹 시작(사용 중단) | — |
| 4 | EGROUP | 그룹 끝(사용 중단) | — |
| 5 | I32 | fixed32, sfixed32, float | 4바이트 |

### varint

varint 는 바이트마다 맨 위 비트(MSB)가 "다음 바이트도 이어진다" 는 표시이고, 아래 7비트가 값입니다. 7비트 묶음은 작은 쪽부터 이어 붙입니다(리틀 엔디언)[1].

sint32·sint64 는 음수를 작은 수로 적으려고 ZigZag 방식을 씁니다. 양수는 짝수로, 음수는 홀수로 바꿔 저장하고, 32비트는 `(n << 1) ^ (n >> 31)` 로 바꿉니다[1]. 이 식을 따르면 0 은 0, -1 은 1, 1 은 2, -2 는 3 으로 저장됩니다.

### LEN

wire type 2 는 태그 뒤에 길이 varint 가 오고, 그 길이만큼 내용이 이어집니다[1]. 내용이 문자열인지, 그냥 바이트 열인지, 또 하나의 protobuf 메시지인지는 이 바이트만으로 정해지지 않습니다.

### 명세가 정한 읽기 규칙

필드 순서는 정해져 있지 않아서 해석기는 어떤 순서로 와도 읽어야 합니다[1]. 반복 필드가 아닌 필드가 여러 번 나오면 숫자와 문자열은 마지막에 나온 값을 씁니다[1].

## 읽는 법

아래는 공식 문서의 인코딩 규칙대로 만든 헥스 예시이고, 특정 파일에서 나온 값이 아닙니다.

```
바이트                          풀이
08                              태그 0x08 = 0000 1000 → 필드 번호 1, wire type 0 (VARINT)
96 01                           0x96 = 1001 0110 → MSB 1(이어짐), 값 비트 001 0110 = 22
                                0x01 = 0000 0001 → MSB 0(끝),     값 비트 000 0001 = 1
                                작은 쪽부터 이어 붙임: 1 × 128 + 22 = 150
12                              태그 0x12 = 0001 0010 → 필드 번호 2, wire type 2 (LEN)
07                              길이 7
74 65 73 74 69 6E 67            내용 7바이트 (ASCII 로 읽으면 "testing")
```

스키마 없이 풀 때는 아래 순서로 갑니다.

1. 첫 바이트부터 varint 하나를 읽어 태그로 삼고, 아래 3비트로 wire type, 나머지로 필드 번호를 얻습니다.
2. wire type 에 맞게 값을 건너뜁니다. 0 은 varint 하나, 1 은 8바이트, 5 는 4바이트, 2 는 길이 varint 를 읽고 그 길이만큼입니다.
3. LEN 값은 먼저 그 안을 다시 protobuf 로 풀어 봅니다. 태그와 길이가 끝까지 어긋나지 않고 딱 맞아떨어지면 하위 메시지일 가능성이 높고, 어긋나면 문자열이나 바이트 열로 봅니다. 이 판단은 추정이라서 결과에 "추정" 이라고 적습니다.
4. 같은 필드 번호가 여러 번 나오면 반복 필드인지, 마지막 값만 쓰는 필드인지 스키마 없이는 가릴 수 없으므로 나온 값을 모두 기록해 둡니다.

## 포렌식에서 중요한 점

스키마 없이 읽으면 알 수 있는 것은 필드 번호와 wire type 뿐입니다[1]. 이 한계에서 두 가지가 따라 나옵니다. wire type 2 하나가 문자열·bytes·하위 메시지를 모두 싣기 때문에 LEN 필드의 겉모양만으로는 셋을 가를 수 없고, wire type 1 하나가 double 과 fixed64 를 모두 싣기 때문에 I64 필드도 실수인지 정수인지 가를 수 없습니다[1]. 보고서에는 "필드 7 의 값" 처럼 번호로 적고, 뜻을 붙일 때는 무엇을 근거로 붙였는지 함께 씁니다.

I64 필드에 들어 있는 double 이 시각일 때가 있습니다. 바이옴 페이로드를 분석한 사례에서는 이런 값을 Mac 절대 시각으로 읽기도 하지만, 이 페이지의 출처로 일반 규칙으로 확인한 것은 아닙니다. 같은 값을 double 로도, 정수로도 읽어 보고, 그럴듯한 날짜가 나오는지 [시각 값](../value-decoding/time-values.md)의 기준 시점들로 바꿔 본 뒤 같은 기기의 다른 기록과 맞춰 봅니다.

protobuf 메시지 자체에는 삭제 표시나 끝 표시가 없습니다. 레코드가 지워졌는지는 protobuf 가 아니라 그것을 담은 그릇이 알려 주므로, SEGB 안의 페이로드라면 [SEGB](segb.md) 트레일러의 상태 값을 봅니다. 담는 그릇이 잘려 페이로드 끝이 사라지면 마지막 태그의 길이가 파일 끝을 넘게 되고, 그 필드부터는 값을 믿을 수 없습니다.

## 함정

같은 필드 번호라도 메시지 종류가 다르면 뜻이 다릅니다. 한 바이옴 스트림에서 알아낸 번호의 뜻을 다른 스트림에 옮겨 쓰지 않습니다.

필드 순서가 정해져 있지 않으므로[1] "첫 번째 필드가 시각이었다" 처럼 위치로 뜻을 정하지 않습니다. 번호로 정합니다.

짧은 LEN 값은 우연히 protobuf 로도 풀릴 수 있습니다. 예를 들어 ASCII 문자열의 첫 바이트가 그럴듯한 태그처럼 보이면, 문자열을 하위 메시지로 잘못 풀어 엉뚱한 필드들이 생깁니다. 풀린 결과를 ASCII 로도 한 번 보고, 사람이 읽을 수 있는 문장이 나오면 문자열 쪽을 먼저 의심합니다.

## 도구

이 페이지를 쓰며 연 출처에서는 스키마 없이 protobuf 를 푸는 특정 도구를 확인하지 못했습니다. 위 규칙대로 직접 풀거나, [바이옴](../../02-artifacts/app-usage/biome/index.md)처럼 아티팩트 페이지에서 소개하는 해석 도구를 쓰고, 도구 결과를 헥스 몇 바이트로 직접 맞춰 보는 절차는 [도구 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다. SEGB 파일에서 페이로드를 잘라 내는 일은 ccl-segb 같은 공개 도구가 하고, 그 설명은 [SEGB](segb.md)에 있습니다.

## 참고 문헌

1. Protocol Buffers 공식 문서 — Encoding — https://protobuf.dev/programming-guides/encoding/
2. Cellebrite — Understanding and Decoding the Newest iOS SEGB Format — https://cellebrite.com/en/blog/understanding-and-decoding-the-newest-ios-segb-format/
3. D20 Forensics — iOS 16 - Now You 'C' It, Now You Don't -- Breaking Down The Biomes Part 1 — https://blog.d204n6.com/2022/09/ios-16-now-you-c-it-now-you-dont.html
