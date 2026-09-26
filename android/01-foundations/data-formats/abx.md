---
title: "안드로이드 바이너리 XML"
parent: "기반 · 데이터 저장 형식"
nav_order: 210
---

# 안드로이드 바이너리 XML (ABX)

안드로이드 바이너리 XML (Android Binary XML, ABX) 은 시스템이 XML 을 텍스트 대신 이벤트 단위의 바이너리로 쓰는 형식이고, 파일 앞 4바이트 `41 42 58 00`(ASCII `ABX` 와 버전 0)으로 알아봅니다.

## 이 형식을 쓰는 아티팩트

`android.util.Xml` 은 시스템 속성 `persist.sys.binary_xml` 을 보고 기본 출력 형식을 정하는데, 코드에 적힌 기본값은 `true` 입니다(`SystemProperties.getBoolean("persist.sys.binary_xml", true)`). `Xml.resolveSerializer()` 로 XML 을 쓰는 곳은 이 속성이 켜져 있으면 바이너리로, 꺼져 있으면 텍스트로 씁니다. 읽는 쪽인 `Xml.resolvePullParser()` 는 파일 앞 4바이트를 `BinaryXmlSerializer.PROTOCOL_MAGIC_VERSION_0` 과 비교해 같으면 바이너리 파서로, 다르면 텍스트 파서(`newFastPullParser()`)로 읽습니다. 그래서 같은 파일 이름이라도 기기와 설정에 따라 텍스트로도 바이너리로도 나올 수 있고, 시스템은 둘 다 읽습니다.

ABX 의 크기·속도 비교는 설치된 앱 목록인 `packages.xml` 을 기준으로 했고 [2], 이 파일의 해석은 [설치된 앱](../../02-artifacts/app-usage/packages/index.md) 에서 다룹니다. 어떤 시스템 파일이 ABX 로 저장됐는지는 파일마다 앞 4바이트를 보고 판단합니다. 앱의 공유 환경설정 파일은 [설정 XML과 SharedPreferences](shared-preferences.md) 에서 다루듯 대개 텍스트 XML 입니다.

Android 버전이나 제조사(삼성 One UI 포함)만 보고 파일 형식을 단정하지 말고, 파일 앞 4바이트를 직접 보고 판단합니다.

크기와 속도에 대해서는 두 출처의 수치가 조금 다릅니다. `BinaryXmlSerializer` 주석에는 텍스트 방식인 `Xml.newFastSerializer()` 보다 전형적인 `packages.xml` 기준으로 4.3배 빠르고 디스크를 2.4배 덜 쓴다고 적혀 있고 [2], `Xml.java` 의 javadoc 에는 4.4배 빠르고 2.8배 덜 쓴다고 적혀 있습니다 [1].

## 구조

### 파일 머리

| 오프셋 | 길이 | 값 | 뜻 |
|---|---|---|---|
| 0 | 3 | `41 42 58` | ASCII `ABX` (Android Binary XML) |
| 3 | 1 | `00` | 프로토콜 버전 0 |

### 이벤트

머리 뒤로는 XML 을 읽을 때 생기는 이벤트 흐름(문서 시작, 태그 시작, 속성, 태그 끝, 문서 끝 같은 것)을 그 순서대로 적습니다. 이벤트마다 1바이트로 시작하고, 이 바이트의 아래 4비트는 XmlPullParser 토큰 종류이고 위 4비트는 뒤따르는 데이터의 형식입니다. 속성은 XmlPullParser 에 없는 내부 토큰 `ATTRIBUTE = 15` 로 적고, 바로 앞의 태그 시작(START_TAG)에 붙습니다.

문서의 시작과 끝은 `START_DOCUMENT | TYPE_NULL`, `END_DOCUMENT | TYPE_NULL` 로 쓰고, 태그 이름은 `START_TAG | TYPE_STRING_INTERNED`, `END_TAG | TYPE_STRING_INTERNED` 로 쓰면서 이름을 `writeInternedUTF(name)` 로 적습니다.

### 데이터 형식 (위 4비트)

| 이름 | 값 | 위 4비트(헥스) |
|---|---|---|
| TYPE_NULL | `1 << 4` | `0x10` |
| TYPE_STRING | `2 << 4` | `0x20` |
| TYPE_STRING_INTERNED | `3 << 4` | `0x30` |
| TYPE_BYTES_HEX | `4 << 4` | `0x40` |
| TYPE_BYTES_BASE64 | `5 << 4` | `0x50` |
| TYPE_INT | `6 << 4` | `0x60` |
| TYPE_INT_HEX | `7 << 4` | `0x70` |
| TYPE_LONG | `8 << 4` | `0x80` |
| TYPE_LONG_HEX | `9 << 4` | `0x90` |
| TYPE_FLOAT | `10 << 4` | `0xA0` |
| TYPE_DOUBLE | `11 << 4` | `0xB0` |
| TYPE_BOOLEAN_TRUE | `12 << 4` | `0xC0` |
| TYPE_BOOLEAN_FALSE | `13 << 4` | `0xD0` |

참과 거짓은 형식 값 자체가 둘로 나뉘어 있습니다. 정수는 `writeInt`, long 은 `writeLong`, float 과 double 은 `writeFloat`·`writeDouble` 로 원래 형식 그대로 쓰고 텍스트로 바꾸지 않으며, 바이트 배열은 길이를 `writeShort` 로 앞에 둡니다. 바이트 순서와 인턴 문자열(한 번 나온 문자열을 다시 쓸 때의 표기) 규칙은 `FastDataOutput` 코드에 정해져 있습니다.

### 제약

ABX 는 UTF-8 만 지원하고, `byte[]` 나 `String` 같은 길이가 바뀌는 값은 65,535바이트까지만 담으며, 네임스페이스·접두사·속성(properties)·옵션은 지원하지 않습니다 [2]. 현재 코드는 `frameworks/libs/modules-utils` 의 `com.android.modules.utils.BinaryXmlSerializer` 에 있고, 예전 경로인 `frameworks/base/core/java/com/android/internal/util/BinaryXmlSerializer.java` 는 main 브랜치에 없습니다.

### 헥스로 따라가 보기

아래는 위 표만으로 만든 예시이고, 특정 기기에서 꺼낸 바이트가 아닙니다.

```
41 42 58 00    'A' 'B' 'X' + 프로토콜 버전 0
...
6F             ATTRIBUTE(15 = 0x0F) | TYPE_INT(0x60)   → 정수 속성
2F             ATTRIBUTE(0x0F)      | TYPE_STRING(0x20) → 문자열 속성
8F             ATTRIBUTE(0x0F)      | TYPE_LONG(0x80)   → long 속성
CF / DF        ATTRIBUTE(0x0F)      | TYPE_BOOLEAN_TRUE / FALSE → 참·거짓 속성
```

이벤트 바이트를 만나면 아래 4비트로 이벤트 종류를, 위 4비트로 뒤에 올 값의 형식을 읽습니다. 속성 이벤트 바이트 뒤에는 속성 이름이 `writeInternedUTF` 로 먼저 오고 그 뒤에 값이 옵니다. 예를 들어 `6F` 를 만나면 앞 태그에 붙는 정수 속성이 시작된 것이고, 이름 다음에 `writeInt` 로 쓴 정수가 이어집니다. 참·거짓 속성은 형식 값이 곧 값이라 이름 뒤에 값 바이트가 따로 없습니다.

## 읽는 법

시스템이 하는 방식을 그대로 따릅니다. 파일 앞 4바이트가 `41 42 58 00` 이면 ABX 로, 아니면 텍스트 XML 로 읽습니다. ABX 라면 텍스트 XML 로 바꿔 주는 변환 도구로 풀고, 풀린 결과는 일반 XML 처럼 태그와 속성을 읽습니다. 처음 쓰는 변환 도구라면 위 형식 표와 맞게 푸는지, 예를 들어 `TYPE_INT` 속성이 숫자로, `TYPE_BOOLEAN_TRUE` 속성이 참으로 나오는지 알려진 파일로 확인합니다.

풀린 텍스트에 담긴 시각 값의 단위는 파일마다 다르고, [시각 값](../value-decoding/time-values.md) 에서 단위를 확인합니다.

## 포렌식에서 중요한 점

정수·long 형식으로 적은 속성은 숫자를 텍스트로 바꾸지 않고 원래 형식 그대로 쓰기 때문에, 이미지 전체에서 시각이나 번호를 10진 문자열로 찾으면 ABX 파일 안의 그런 값은 걸리지 않습니다. 키워드 검색으로 놓친 값이 ABX 안에 있을 수 있으니, 숫자를 찾을 때는 파일을 먼저 텍스트로 바꾼 뒤 찾습니다. 검색 방법은 [콘텐츠 검색](../../03-techniques/analysis/content-search.md) 에서 다룹니다.

ABX 파일은 앞 4바이트가 늘 같아서, 비할당 영역에서 조각을 찾을 때 파일 머리 표시로 쓸 수 있습니다. 조각을 되살리는 방법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

같은 파일 이름이 기기나 설정에 따라 텍스트로도 바이너리로도 나올 수 있어서, 백업이나 다른 시점의 이미지와 비교할 때 형식이 다르다는 사실만으로 파일이 조작됐다고 보면 안 됩니다. 비교는 두 파일을 모두 텍스트로 바꾼 뒤 내용으로 합니다.

## 함정

편집기에서 깨져 보이는 `.xml` 파일을 손상된 파일로 오해하기 쉽습니다. 앞 4바이트가 `ABX` 로 시작하면 정상적인 바이너리 XML 입니다.

변환 도구가 내놓는 텍스트는 원래 기기에 있던 텍스트가 아니라 도구가 새로 만든 표현입니다. 들여쓰기나 줄바꿈처럼 도구가 정하는 부분이 있으니, 보고서에는 원본이 ABX 였고 어떤 도구로 바꿨는지 함께 적습니다.

## 도구

ABX 를 텍스트로 바꾸는 변환 도구가 필요합니다. 어떤 도구를 쓰든 위 형식 표와 알려진 파일로 결과를 맞춰 봅니다. 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다. 머리 4바이트를 확인하는 일은 헥스 편집기로 충분합니다.

## 참고 문헌

1. Xml.java (android.util.Xml) — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/util/Xml.java
2. BinaryXmlSerializer.java — AOSP frameworks/libs/modules-utils (main), https://android.googlesource.com/platform/frameworks/libs/modules-utils/+/refs/heads/main/java/com/android/modules/utils/BinaryXmlSerializer.java
