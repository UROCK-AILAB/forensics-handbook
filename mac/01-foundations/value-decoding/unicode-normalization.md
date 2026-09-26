---
title: "유니코드 정규화"
parent: "기반 · 값 읽는 법"
nav_order: 340
---

# 유니코드 정규화 (NFD·NFC)

## 한 줄 요약

같은 글자라도 유니코드로 적는 방법이 여러 가지라서 파일 이름의 바이트가 합친 형태(NFC)와 푼 형태(NFD)로 달라질 수 있고, HFS+ 는 이름을 푼 형태로 바꿔 저장하는 반면 APFS 는 받은 형태를 그대로 두고 비교할 때만 정규화하기 때문에, 원시 바이트로 이름을 찾을 때는 두 형태를 모두 찾아야 합니다.

## 이 형식을 쓰는 아티팩트

| 쓰는 곳 | 이름 저장 방식 | 정규화 | 구조 페이지 |
|---|---|---|---|
| HFS+ 카탈로그의 파일·폴더 이름 | `HFSUniStr255` (UTF-16 코드 단위, 최대 255자) | 완전 분해한 정규 순서로 바꿔 저장 | [HFS+ 구조](../disk-volume/hfs-plus.md) |
| APFS 디렉터리 항목 이름 | null 로 끝나는 UTF-8 | 받은 형태 그대로 저장, 정규화 무시 볼륨은 NFD 로 정규화한 이름의 해시를 키에 넣음 | [APFS 구조](../disk-volume/apfs/index.md) |
| APFS 볼륨 이름 `apfs_volname` | null 로 끝나는 UTF-8 | 공개 자료 없음 | [APFS 구조](../disk-volume/apfs/index.md) |

파일 이름 말고 앱이 SQLite·plist 안에 저장한 문자열의 정규화 형태는 앱마다 다를 수 있어 검체에서 확인합니다.

### APFS 정규화 동작의 버전별 차이

APFS 의 정규화 동작은 버전별로 아래와 같습니다(2018-06-04 기준)[2]. 기준 유니코드 판은 9.0 이고, macOS 의 APFS 는 대소문자 무시가 기본이며 대소문자 구분 변형도 있습니다[2].

| 버전 | APFS 정규화 동작 |
|---|---|
| macOS Sierra 개발자 미리보기, iOS 10.3 | 대소문자 구분 APFS 는 정규화를 구분(normalization-sensitive) |
| macOS Sierra 10.12.6, iOS 10.3.3 | 런타임 정규화(runtime normalization)를 쓸 수 있음 |
| macOS High Sierra | 대소문자 구분·무시 두 변형 모두 정규화 무시(normalization-insensitive), 해시를 쓰는 기본 정규화(native normalization) |
| iOS 11 | 정규화 무시. 새로 지운 뒤 복원한 기기는 기본 정규화, 옛 판에서 올린 기기는 런타임 정규화 |

이 설명은 2018년 이후 갱신되지 않아서 macOS 10.15 Catalina 이후 판의 동작은 공식 설명이 없습니다. 조사 대상 볼륨이 정규화를 무시하는지는 버전으로 짐작하지 말고, 아래 "구조" 절의 볼륨 플래그를 직접 읽어 확인합니다.

## 구조

### 합친 형태와 푼 형태

아래 값은 파이썬 표준 라이브러리 `unicodedata` 로 정규화해 뽑은 예시이고, 특정 검체에서 나온 값이 아닙니다. "한글" 두 글자가 NFC 에서는 음절 두 개, NFD 에서는 자모 여섯 개가 되어 UTF-8 바이트 길이가 6바이트에서 18바이트로 늘어납니다.

```text
"한글" NFC  코드 포인트  U+D55C U+AE00
            UTF-8        ED 95 9C  EA B8 80

"한글" NFD  코드 포인트  U+1112 U+1161 U+11AB  U+1100 U+1173 U+11AF
            UTF-8        E1 84 92  E1 85 A1  E1 86 AB  E1 84 80  E1 85 B3  E1 86 AF
```

### HFS+

HFS+ 의 파일 이름 자료형 `HFSUniStr255` 는 `UInt16 length` 와 `UniChar unicode[255]` 로 이루어지고, `UniChar` 는 UInt16 유니코드 문자라서 이름은 최대 255자입니다[1]. HFS+ 는 이름을 저장할 때 완전 분해(정규 분해)해 정규 순서로 둡니다[1].

HFS+ 는 이름을 대소문자를 가리지 않고 비교하고, 비교할 때 무시하는 유니코드 문자가 있습니다. 대소문자를 구분하는 변형인 HFSX 도 이름은 완전 분해·정규 순서로 저장하지만 비교할 때 무시하는 문자가 없습니다.

| 형식 | 서명·버전 | 이름 비교 |
|---|---|---|
| HFS+ | `H+`, 버전 4 | 대소문자 무시, 일부 문자 무시 |
| HFSX | `HX`, 버전 5 | 카탈로그 B-트리 헤더 `keyCompareType` 으로 정함: `kHFSCaseFolding`(0xCF) 대소문자 무시, `kHFSBinaryCompare`(0xBC) 구분 |

### APFS

APFS 는 파일 이름의 정규화 형태를 그대로 보존하고, 정규화한 형태의 해시로 정규화 무시를 구현합니다[2]. HFS+ 는 정규화한 형태를 디스크에 저장해 같은 효과를 냈습니다[2].

볼륨이 정규화를 무시하는지는 볼륨 슈퍼블록 `apfs_incompatible_features` 필드의 비트로 알 수 있습니다[3].

| 플래그 | 값 | 뜻 |
|---|---|---|
| `APFS_INCOMPAT_CASE_INSENSITIVE` | 0x00000001 | 대소문자 무시 볼륨 |
| `APFS_INCOMPAT_NORMALIZATION_INSENSITIVE` | 0x00000008 | 정규화 무시, 명세 표현으로 "Normalization insensitivity is part of hashing filenames" |

디렉터리 항목 키는 두 가지입니다. `j_drec_key_t` 는 이름 길이와 이름만 담고, `j_drec_hashed_key_t` 는 길이와 해시를 합친 `name_len_and_hash` 뒤에 이름을 담습니다.

| `name_len_and_hash` 비트 | 내용 |
|---|---|
| 아래 10비트 (`J_DREC_LEN_MASK`) | 이름 길이, null 포함 |
| 위 22비트 (`J_DREC_HASH_MASK` = 0xfffff400, `J_DREC_HASH_SHIFT` = 10) | 이름 해시 |

해시 계산 순서는 다음과 같습니다[3].

1. null 로 끝나는 UTF-8 파일 이름에서 시작합니다.
2. 정규 분해(NFD)로 정규화합니다.
3. null 로 끝나는 UTF-32 로 바꿉니다.
4. CRC-32C 를 계산합니다.
5. 비트를 뒤집습니다.
6. 아래 22비트만 남깁니다.

대소문자 무시 볼륨에서 해시를 내기 전에 대소문자 접기(case folding)를 하는지는 공개 자료가 없어 검체에서 확인합니다.

## 읽는 법

파일 이름을 읽을 때는 먼저 볼륨이 HFS+ 인지 APFS 인지 가립니다. HFS+ 라면 카탈로그 레코드의 이름은 UTF-16 코드 단위의 NFD 형태이고, 바이트 순서는 [HFS+ 구조](../disk-volume/hfs-plus.md)에서 확인합니다. APFS 라면 디렉터리 항목의 이름은 UTF-8 이고 형태는 NFC 일 수도 NFD 일 수도 있어서, 바이트를 그대로 적어 두고 비교할 때만 한쪽으로 정규화합니다.

APFS 디렉터리 항목 키가 해시를 담은 형태이면 `name_len_and_hash` 의 아래 10비트로 이름 길이를 읽고, 위 22비트는 이름의 해시로 따로 적어 둡니다. 볼륨 슈퍼블록의 `apfs_incompatible_features` 에서 0x00000008 비트가 켜져 있으면 이 볼륨은 정규화 무시 볼륨입니다.

보고서에 파일 이름을 옮길 때는 화면에 보이는 글자만 적지 말고, 원래 바이트나 코드 포인트를 함께 적어 두면 다른 도구·다른 운영체제에서 같은 이름을 찾을 때 형태 차이로 놓치지 않습니다.

## 포렌식에서 중요한 점

디스크 이미지에서 원시 바이트로 파일 이름을 찾을 때는 NFC 와 NFD 두 형태로 모두 찾습니다. APFS 는 이름을 받은 그대로 저장해서 같은 볼륨 안에서도 파일마다 형태가 다를 수 있고, HFS+ 는 UTF-16 NFD 형태로 저장해서 UTF-8 로 만든 검색어로는 걸리지 않습니다. 위 예시처럼 한글 이름은 NFC 와 NFD 의 바이트가 전혀 겹치지 않아서, 한 형태로만 찾으면 결과가 없어도 이름이 없었다고 말할 수 없습니다. 검색어를 만드는 방법은 [콘텐츠 검색](../../03-techniques/analysis/content-search.md)에서 다룹니다.

정규화 무시 APFS 볼륨에서는 같은 폴더에 NFC 와 NFD 로만 다른 두 이름이 같은 이름으로 취급되는 것으로 보입니다. 반대로 정규화를 구분하던 초기 APFS 볼륨에서는 눈으로 같은 이름 두 개가 한 폴더에 있을 수 있어서, 이름이 겹쳐 보이면 바이트를 비교해 봅니다.

지운 파일의 이름을 복구할 때 APFS 해시 키의 해시 값은 이름을 확인하는 검산으로 쓸 수 있습니다. 복구한 이름을 위 여섯 단계대로 계산해 남은 해시와 맞으면 이름 조각이 제대로 이어졌다고 볼 근거가 됩니다. 다만 대소문자 접기 여부가 알려져 있지 않아서, 대소문자 무시 볼륨에서는 해시가 맞지 않아도 이름이 틀렸다고 단정하지 않습니다. 복구 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.

## 함정

같은 이름이 도구마다 다르게 보일 수 있습니다. 어떤 도구는 이름을 NFC 로 바꿔 보여 주고 어떤 도구는 저장된 바이트 그대로 보여 주면, 두 도구의 결과를 문자열로 맞춰 볼 때 서로 없는 파일처럼 나옵니다. 도구 결과를 합치기 전에 한쪽 형태로 정규화하고, 어느 도구가 어떤 형태로 내놓는지는 [도구 검증](../../03-techniques/reporting/tool-validation.md) 방식으로 확인합니다.

APFS 정규화 동작의 공식 설명은 2018년 FAQ 에 머물러 있고, 볼륨 이름 `apfs_volname` 의 정규화 여부와 앱 데이터 안 문자열의 형태는 공개 자료가 없습니다. 이런 곳에서 형태를 가정해야 하면 실제 바이트를 한 번 보고 정합니다.

## 도구

| 도구 | 쓰임 |
|---|---|
| 파이썬 `unicodedata` (표준 라이브러리) | `unicodedata.normalize("NFC", s)`, `unicodedata.normalize("NFD", s)` 로 두 형태를 만들어 검색어를 준비하고, 이름을 비교하기 전에 한쪽으로 맞춥니다 |
| 헥스 편집기 | 이름 바이트를 직접 보고 NFC 인지 NFD 인지, UTF-8 인지 UTF-16 인지 가립니다 |

## 참고 문헌

1. Apple, Technical Note TN1150: HFS Plus Volume Format, https://developer.apple.com/library/archive/technotes/tn/tn1150.html
2. Apple, Apple File System Guide — Frequently Asked Questions (갱신 2018-06-04), https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/FAQ/FAQ.html
3. Apple, Apple File System Reference (2020-06-22 판), https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
