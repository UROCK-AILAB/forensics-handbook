---
title: "NSKeyedArchiver 풀기"
parent: "속성 목록 파일"
grand_parent: "기반 · 데이터 저장 형식"
nav_order: 150
---

# NSKeyedArchiver 풀기 (NSKeyedArchiver)

NSKeyedArchiver는 앱의 객체를 plist로 바꿔 저장하는 방식이고, 객체는 모두 `$objects` 배열 한 곳에 모이며 서로 uid 번호로 가리킵니다. 그래서 plist 뷰어로 열어도 값이 번호로만 보이고, `$top` 에서 시작해 번호를 따라가며 클래스 이름과 키를 붙여 읽어야 앱이 저장한 값을 알아볼 수 있습니다.

## 이 형식을 쓰는 아티팩트

NSKeyedArchiver는 객체를 XML이나 바이너리 plist로 바꿔 저장하고, 출력 형식의 기본값은 바이너리입니다 [1]. 그래서 파일 머리만 보면 여느 바이너리 plist와 같고, 최상위 사전에 아래 키 네 개가 있으면 이 형식으로 봅니다. 바이너리 plist 자체의 구조는 [XML·바이너리 plist (XML·bplist00)](xml-binary.md)에서 다룹니다.

어떤 macOS 파일이 이 형식을 쓰는지, 경로와 버전별 목록은 이 페이지의 참고 문헌으로 확인하지 못해서 적지 않고, 각 아티팩트 페이지에서 다룹니다.

이 페이지의 설명은 Apple이 공개한 swift-corelibs-foundation(리눅스 등에서 쓰는 공개 Foundation) 소스를 기준으로 합니다 [1][2]. 소스 주석에 "OS X only encodes the mapped name" 처럼 macOS 동작에 맞춘 흔적이 있지만 [1], macOS의 Foundation과 모든 세부가 같다고 확인한 것은 아니라서, 검체에서 다른 모습이 보이면 관찰로 적고 확인 범위를 밝힙니다.

## 구조

### 최상위 사전

| 키 | 값 [1] |
|---|---|
| `$archiver` | 아카이버 클래스 이름. 보통 `NSKeyedArchiver` |
| `$version` | 100000 (`NSKeyedArchivePlistVersion`) |
| `$objects` | 보관한 객체를 모두 담은 배열 |
| `$top` | 최상위 인코딩 사전. 키마다 객체 참조(uid)를 담음 |

`$top` 안의 키는 보통 `root` 이고, `archivedData(withRootObject:)` 같은 함수가 이 키(`NSKeyedArchiveRootObjectKey`)를 씁니다 [1]. 앱이 `encode(_:forKey:)` 로 직접 인코딩했다면 그 키 이름이 `$top` 에 들어가서 `root` 가 없을 수도 있습니다 [1]. 소스에는 `NSKeyedArchiverSystemVersion = 2000` 이라는 상수도 있지만 쓰임은 확인하지 못했습니다 [1].

### 참조(uid)와 `$null`

객체끼리의 참조는 plist의 uid 형식이고, 바이너리에서는 표식 `0x8n` 으로 저장하며 CF 안에서는 `CFKeyedArchiverUID` 라고 부릅니다 [1][3]. uid 값은 `$objects` 배열의 번호입니다 [1].

`$objects` 의 0번은 늘 문자열 `$null` 이고, null 참조는 uid 0으로 적습니다 [1]. uid 0을 만나면 0번 객체를 값으로 읽지 말고 "값 없음" 으로 읽습니다.

### 객체 사전과 클래스 정보

클래스 객체 하나는 `$objects` 안의 사전 하나로 저장되고, 이 사전의 `$class` 키는 클래스 정보 사전을 가리키는 uid입니다 [1]. 클래스 정보 사전에는 클래스 이름 `$classname`, 자기 클래스부터 부모 클래스까지 이름을 늘어놓은 배열 `$classes` 가 들어가고, `$classhints` 가 붙기도 합니다 [1]. 클래스 이름을 다른 이름으로 매핑해 둔 경우 macOS는 매핑된 이름 하나만 `$classname` 에 적는다고 소스 주석에 적혀 있습니다 [1].

객체 사전의 나머지 키는 앱이 인코딩할 때 준 키 이름이고, 여기에는 두 가지 규칙이 있습니다 [1].

- 앱의 키가 `$` 로 시작하면 앞에 `$` 를 하나 더 붙여 아카이버 예약 키와 구분합니다(`escapeArchiverKey`). 그래서 `$$` 로 시작하는 키는 원래 `$` 로 시작하던 앱 키이고, 읽을 때는 앞의 `$` 하나를 떼어 냅니다.
- 키 없이 인코딩한 값에는 `$0`, `$1` 처럼 번호 붙은 키가 붙습니다.

### 컬렉션

NSDictionary는 키 배열을 `NS.keys` 에, 값 배열을 `NS.objects` 에 uid 배열로 담고, 두 배열에서 같은 순번끼리 짝을 짓습니다 [2]. 디코더는 `NS.key.0`, `NS.object.0`, `NS.key.1` 처럼 번호 붙은 옛 방식 키도 읽습니다 [2]. 배열을 인코딩할 때는 원소마다 uid를 만들어 uid 배열로 넣습니다 [1].

NSArray·NSString·NSDate·NSData 같은 다른 클래스가 어떤 키 이름을 쓰는지, NSDate에 어떤 기준의 시각을 넣는지는 이 페이지의 참고 문헌으로 확인하지 못했습니다. 이런 클래스는 검체에서 본 키를 관찰로 적고, 시각 값의 기준은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../value-decoding/mac-time-values.md)과 대조해 판단합니다.

## 읽는 법

아래는 NSDictionary 하나를 `archivedData(withRootObject:)` 로 보관했을 때의 모양을 명세 [1][2]에 맞춰 만든 예시이고, 실제 검체에서 나온 값이 아닙니다. `$objects` 안의 순번과 문자열의 표현 방식은 설명을 위해 정한 것이라 실제 파일과 다를 수 있습니다.

```
$archiver = "NSKeyedArchiver"
$version  = 100000
$top      = { root: uid(1) }
$objects  = [
  0: "$null"
  1: { NS.keys: [uid(2)], NS.objects: [uid(3)], $class: uid(4) }
  2: "Mode"
  3: "Dark"
  4: { $classname: "NSDictionary", $classes: ["NSDictionary", "NSObject"] }
]
```

1. `$archiver` 와 `$version` 을 보고 NSKeyedArchiver 형식인지 확인합니다.
2. `$top` 에서 시작점을 찾습니다. 여기서는 `root` 가 uid 1을 가리키고, `root` 가 없으면 `$top` 의 다른 키를 모두 시작점으로 삼습니다.
3. `$objects[1]` 로 가서 `$class` 가 가리키는 `$objects[4]` 를 읽고, `$classname` 이 `NSDictionary` 라서 사전으로 풉니다.
4. `NS.keys` 와 `NS.objects` 의 같은 순번을 짝지어 `$objects[2]` 와 `$objects[3]` 을 읽고, 결과는 `Mode` 가 `Dark` 인 사전 하나입니다.
5. 값이 다시 uid이면 같은 방법으로 따라가고, uid 0은 값 없음으로 적습니다.

## 포렌식에서 중요한 점

`$classes` 에는 부모 클래스 이름까지 들어가서 [1], 앱이 만든 고유 클래스라도 어떤 표준 클래스를 이어받았는지 알 수 있고, 처음 보는 클래스를 풀 때 실마리가 됩니다. 처음 보는 클래스는 객체 사전의 키 이름과 값의 형식을 그대로 옮겨 적고, 키의 뜻을 짐작으로 채우지 않습니다.

바이너리 plist 수준의 손상 판단(트레일러·오프셋 테이블 검사, uid 값의 상한)은 [XML·바이너리 plist (XML·bplist00)](xml-binary.md)의 검사 조건을 먼저 적용합니다. 그 검사를 통과한 파일에서 uid가 `$objects` 배열 길이를 벗어나거나 `$class` 가 클래스 정보 사전이 아닌 객체를 가리키면, 아카이브 수준에서 어긋난 파일로 보고 그 부분을 따로 기록합니다.

## 함정

- **`root` 가 없는 아카이브**: 앱이 다른 키로 인코딩하면 `$top` 에 `root` 가 없습니다 [1]. `root` 만 찾는 스크립트는 이런 파일에서 빈 결과를 내니, `$top` 의 키를 모두 확인합니다.
- **`$$` 키**: 앱 키가 `$` 로 시작하면 `$` 가 하나 더 붙어 있습니다 [1]. 보고서에는 앞의 `$` 하나를 뗀 원래 키 이름을 쓰고, 원본에 적힌 모양도 함께 남깁니다.
- **uid와 정수**: uid는 일반 정수와 다른 형식(표식 `0x8n`)입니다 [3]. 형식을 가리지 않고 값만 보여 주는 도구에서는 uid가 평범한 숫자로 보여서, 참조 번호를 설정값으로 잘못 읽을 수 있습니다.
- **번호 붙은 옛 키**: 사전이 `NS.keys`·`NS.objects` 대신 `NS.key.0`·`NS.object.0` 모양으로 들어 있을 수 있습니다 [2].
- **구현 차이**: 이 페이지는 공개 Foundation 소스 기준입니다 [1][2]. macOS가 만든 아카이브에서 다른 키가 보이면 관찰로 적습니다.

## 도구

NSKeyedArchiver 파일도 plist라서 plist를 읽는 도구로 열 수 있고, 그 뒤에 위 순서대로 uid를 따라가면 됩니다. 이 형식을 풀어 주는 공개 도구의 이름과 기능은 이 페이지의 참고 문헌으로 확인하지 못해서 적지 않고, 어떤 도구를 쓰든 결과에서 한두 객체를 골라 `$objects` 번호를 손으로 따라가 맞춰 봅니다. 검증 방법은 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)을 따릅니다.

## 참고 문헌

1. Apple swift-corelibs-foundation, NSKeyedArchiver.swift — https://raw.githubusercontent.com/apple/swift-corelibs-foundation/main/Sources/Foundation/NSKeyedArchiver.swift
2. Apple swift-corelibs-foundation, NSDictionary.swift — https://raw.githubusercontent.com/apple/swift-corelibs-foundation/main/Sources/Foundation/NSDictionary.swift
3. Apple CF 공개 소스, CFBinaryPList.c — https://raw.githubusercontent.com/apple-oss-distributions/CF/main/CFBinaryPList.c
