---
title: "압축 형식"
parent: "기반 · 값 읽는 법"
nav_order: 350
---

# 압축 형식 (LZFSE·LZ4·zlib)

## 한 줄 요약

맥에서는 파일 시스템이 사용자 모르게 파일 내용을 압축해 두기도 하고 통합 로그가 기록 묶음을 LZ4 로 압축해 두기도 해서, 블록 표시(magic)와 헤더를 알아보고 풀어야 원래 값을 읽을 수 있습니다.

## 이 형식을 쓰는 아티팩트

분석가가 가장 자주 만나는 곳은 세 군데입니다.

| 쓰는 곳 | 압축 방식 | 알아보는 표시 | 자세한 페이지 |
|---|---|---|---|
| 파일 시스템 투명 압축 (decmpfs) | zlib, LZVN, 압축 안 함 등 | 확장 속성 `com.apple.decmpfs`, magic 0x636d7066 (디스크 바이트 "fpmc") | [HFS+ 구조](../disk-volume/hfs-plus.md), [APFS 구조](../disk-volume/apfs/index.md) |
| 통합 로그 tracev3 파일의 청크셋 (ChunkSet) | LZ4 | 블록 표시 `bv41`, `bv4-`, `bv4$` | [통합 로그 형식](../data-formats/unified-log/index.md) |
| LZFSE 로 압축한 데이터 | LZFSE, LZVN | 블록 표시 `bvx2`, `bvx1`, `bvxn`, `bvx-`, `bvx$` | 이 페이지 |

LZFSE 는 Apple 이 만든 압축 방식이고, Apple 이 참조 구현을 BSD 3-Clause 라이선스로 공개했습니다. 앱이 Apple 의 Compression 프레임워크로 데이터를 압축하면 LZFSE 말고도 여러 방식을 고를 수 있어서, 아래 "Compression 프레임워크의 알고리즘" 절에 목록을 정리했습니다.

어느 macOS 버전부터 투명 압축에 LZFSE 를 쓰는지는 공개 자료가 없어 검체에서 확인합니다.

## 구조

### LZFSE 블록

LZFSE 스트림은 블록이 차례로 이어진 형태이고, 블록마다 4바이트 magic 으로 시작합니다. magic 은 uint32 값이고, 이 값을 리틀 엔디언으로 적으면 파일 안에서 ASCII 글자 "bvx2" 처럼 그대로 보입니다.

| 표시 | uint32 값 | 뜻 |
|---|---|---|
| `bvx$` | 0x24787662 | 스트림 끝 |
| `bvx-` | 0x2d787662 | 압축하지 않은 원본 블록 |
| `bvx1` | 0x31787662 | LZFSE 블록, 표를 압축하지 않음 |
| `bvx2` | 0x32787662 | LZFSE 블록, 표를 압축함 |
| `bvxn` | 0x6e787662 | LZVN 블록 |

블록 헤더는 종류마다 다르지만, `bvx-`·`bvxn`·`bvx1`·`bvx2` 모두 magic 바로 뒤 4바이트가 풀었을 때 크기(n_raw_bytes)입니다. 그래서 블록 종류를 몰라도 이 4바이트로 풀린 뒤의 크기를 먼저 가늠할 수 있습니다.

| 블록 | 헤더 필드 (순서대로) |
|---|---|
| `bvx-` | magic (uint32), n_raw_bytes (uint32) |
| `bvxn` | magic, n_raw_bytes, n_payload_bytes (각 uint32) |
| `bvx1` | magic, n_raw_bytes, n_payload_bytes, n_literals, n_matches, n_literal_payload_bytes, n_lmd_payload_bytes (uint32), literal_bits (int32), literal_state[4] (uint16), lmd_bits (int32), l_state·m_state·d_state (uint16), 빈도표 l_freq·m_freq·d_freq·literal_freq (uint16) |
| `bvx2` | magic, n_raw_bytes (uint32), packed_fields[3] (uint64, 비트 단위로 묶음), 길이가 바뀌는 freq[] (uint8) |

`bvx2` 헤더는 필드 여러 개를 비트 단위로 묶어 uint64 세 개에 넣어 두어서, 헥스 편집기에서 눈으로 필드를 나누기 어렵습니다. 이런 블록은 참조 구현으로 푸는 편이 낫습니다.

### 통합 로그 안의 LZ4 블록

tracev3 파일은 청크가 이어진 형태이고, 청크 헤더는 오프셋 0 에 태그(4바이트), 4 에 서브태그(4바이트), 8 에 데이터 크기(8바이트)가 있고 16 부터 데이터가 이어집니다. 청크 태그에는 0x1000 헤더, 0x6001 Firehose, 0x6002 Oversize, 0x6003 StateDump, 0x6004 SimpleDump, 0x600b Catalog, 0x600d 청크셋(ChunkSet)이 있고, 이 가운데 청크셋을 LZ4 로 압축합니다[4].

| 표시 | 오프셋 4 | 오프셋 8 | 오프셋 12부터 |
|---|---|---|---|
| `bv41` (압축 블록) | 풀었을 때 크기 (4바이트) | LZ4 압축 크기 (4바이트) | 압축 데이터 |
| `bv4-` (압축 안 한 블록) | 크기 | | |
| `bv4$` (스트림 끝) | | | |

LZFSE 의 `bvx-`·`bvx$` 와 LZ4 의 `bv4-`·`bv4$` 는 이름 짓는 규칙이 같아서, 네 번째 글자만 보고도 "압축 안 함"과 "끝"을 구분할 수 있습니다. 청크셋을 푼 뒤 시각 값과 문자열을 읽는 법은 [통합 로그 형식](../data-formats/unified-log/index.md)에서 다룹니다.

### 파일 시스템 투명 압축 (decmpfs)

HFS+ 와 APFS 는 파일 내용을 압축해 두고 읽을 때 저절로 풀어 주는 투명 압축을 지원하고, 이때 파일에 확장 속성 `com.apple.decmpfs` 가 붙습니다. 속성 값은 16바이트 헤더로 시작하고, 헤더 필드는 리틀 엔디언입니다.

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 4 | compression_magic | 0x636d7066 (XNU 소스 주석 "cmpf", 디스크 바이트는 "fpmc") |
| 4 | 4 | compression_type | 압축 형식 번호 |
| 8 | 8 | uncompressed_size | 풀었을 때 크기 |
| 16 | — | attr_bytes | 헤더 뒤에 이어지는 데이터 |

XNU 헤더에는 형식 번호가 CMP_Type1 = 1(속성 안에 압축 안 한 데이터)과 CMP_MAX = 255 만 있고, 나머지 형식은 AppleFSCompression 쪽에서 정합니다[3]. 나머지 번호는 아래와 같습니다[5].

| 번호 | 이름 | 데이터 위치 | 압축 |
|---|---|---|---|
| 3 | ZLIB_ATTR | 속성 안, 헤더 바로 뒤 | zlib |
| 4 | ZLIB_RSRC | 리소스 포크 | zlib |
| 5 | DATALESS | — | — |
| 7 | LZVN_ATTR | 속성 안, 헤더 바로 뒤 | LZVN |
| 8 | LZVN_RSRC | 리소스 포크 | LZVN |
| 9 | RAW_ATTR | 속성 안, 헤더 바로 뒤 | 압축 안 함 |
| 10 | RAW_RSRC | 리소스 포크 | 압축 안 함 |

이름 끝의 `_ATTR` 은 압축 데이터가 `com.apple.decmpfs` 속성 안에서 헤더 바로 뒤에 이어진다는 뜻이고, `_RSRC` 는 데이터가 리소스 포크의 "CMPF" 종류 리소스에 들어 있다는 뜻입니다. 압축 단위(블록) 크기는 65536 바이트입니다[5]. 형식 3 에서는 데이터 첫 바이트가 0xF 이면 실제로는 압축하지 않은 데이터입니다[5].

LZFSE 와 LZBITMAP 형식 번호는 이 표에 없지만, 이 두 방식으로 압축한 투명 압축 파일도 있습니다[6].

### Compression 프레임워크의 알고리즘

compression_algorithm 상수는 아래와 같습니다[2].

| 상수 | 문서 설명 |
|---|---|
| COMPRESSION_LZFSE | Apple 플랫폼에서 권장 |
| COMPRESSION_LZ4 | 빠름 |
| COMPRESSION_LZ4_RAW | 프레임 헤더 없는 LZ4 |
| COMPRESSION_LZMA | 압축률이 높음 |
| COMPRESSION_ZLIB | 다른 플랫폼과 호환 |
| COMPRESSION_BROTLI | 텍스트에 권장 |
| COMPRESSION_LZBITMAP | 최신 CPU 의 벡터 명령을 활용 |
| COMPRESSION_LZMESH | Apple 플랫폼에서 빠른 범용 압축에 권장 |
| COMPRESSION_LZRAVEN | Apple 플랫폼에서 압축률이 높고 해제가 빨라야 할 때 권장 |

COMPRESSION_LZ4 가 내놓는 데이터가 통합 로그의 `bv41` 블록과 같은 형태인지, COMPRESSION_ZLIB 가 zlib 헤더를 붙이는지는 공개 자료가 없으므로, 앱 데이터에서 압축 덩어리를 만나면 이 목록을 후보로 두고 앞 바이트를 하나씩 맞춰 봅니다.

## 읽는 법

아래 헥스는 명세로 만든 예시이고, 특정 검체에서 나온 값이 아닙니다. `NN` 은 값이 들어갈 자리를 뜻합니다.

```text
LZFSE 블록 (bvx2) 앞부분
오프셋  00 01 02 03  04 05 06 07  08 ...
0000    62 76 78 32  NN NN NN NN  NN ...
        "b  v  x  2" n_raw_bytes  packed_fields[3] ...

통합 로그 LZ4 블록 (bv41) 앞부분
오프셋  00 01 02 03  04 05 06 07  08 09 0A 0B  0C ...
0000    62 76 34 31  NN NN NN NN  NN NN NN NN  NN ...
        "b  v  4  1" 풀었을 때 크기 LZ4 압축 크기 압축 데이터
```

한 블록을 읽는 순서는 다음과 같습니다.

1. 처음 4바이트를 ASCII 로 읽어 `bvx`·`bv4` 중 어느 쪽인지, 네 번째 글자가 무엇인지 봅니다.
2. 이어지는 4바이트에서 풀었을 때 크기를 읽습니다. `bv41` 이면 그다음 4바이트가 압축 크기이고, `bvxn`·`bvx1` 이면 n_payload_bytes 가 압축 크기입니다. `bvx2` 는 크기 값이 packed_fields 안에 묶여 있어서 참조 구현으로 읽습니다.
3. 압축 크기만큼 데이터를 떼어 내 해당 방식으로 풉니다. 풀린 길이가 2단계에서 읽은 크기와 맞는지 확인합니다.
4. 블록 끝 다음 바이트에서 다시 1단계로 돌아가고, `bvx$`·`bv4$` 를 만나면 멈춥니다.

decmpfs 파일은 먼저 `com.apple.decmpfs` 속성을 꺼내 오프셋 4 의 형식 번호를 읽습니다. 번호가 `_ATTR` 계열이면 속성 안 오프셋 16 부터 데이터를 읽고, `_RSRC` 계열이면 같은 파일의 리소스 포크에서 데이터를 찾습니다. 풀린 결과의 길이는 오프셋 8 의 uncompressed_size 와 대조합니다.

## 포렌식에서 중요한 점

투명 압축 파일은 파일 시스템 레코드에서 데이터 포크 크기가 0 으로 보여도 내용이 비어 있지 않습니다. 데이터 포크 크기가 0 인데 `com.apple.decmpfs` 속성이 붙어 있으면 내용은 그 속성이나 리소스 포크에 들어 있어서, 크기만 보고 "빈 파일"로 적으면 틀립니다. 실제 크기는 속성 헤더의 uncompressed_size 에서 읽습니다.

이미지를 도구 없이 바이트 단위로 카빙하면 투명 압축 파일의 내용은 원문으로 나오지 않습니다. `bvx` 계열 표시는 LZFSE 스트림의 위치를, `bv41` 은 통합 로그 청크셋의 압축 블록 위치를 알려 주므로, 지운 영역이나 비할당 영역에서 이 표시를 찾아 블록째 떼어 낸 뒤 풀어 볼 수 있습니다. 다만 decmpfs 의 zlib·LZVN 데이터 앞에도 이런 표시가 붙는지는 공개 자료가 없어서, 투명 압축 파일 조각을 이 표시만으로 모두 찾을 수 있다고 보지 않습니다. 블록 헤더에 풀었을 때 크기가 적혀 있어서, 푼 결과가 그 크기와 맞지 않으면 블록이 잘렸거나 덮어쓰였다고 의심할 수 있습니다. 카빙과 복구 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.

키워드 검색도 같은 영향을 받습니다. 압축된 파일과 통합 로그 청크셋은 풀기 전에는 원문 문자열이 드러나지 않아서, 원시 이미지에 문자열 검색을 돌린 결과에 없다고 해서 그 문자열이 디스크에 없었다고 말할 수 없습니다. 검색 범위를 정하는 법은 [콘텐츠 검색](../../03-techniques/analysis/content-search.md)에서 다룹니다.

## 함정

decmpfs 헤더 필드는 리틀 엔디언이라서[5], magic 0x636d7066 은 원시 바이트에서 `66 70 6D 63`, 곧 ASCII "fpmc" 로 보입니다. XNU 주석의 "cmpf" 로 찾으면 놓치므로 "fpmc" 로 찾고, 찾은 뒤 뒤따르는 형식 번호가 위 표의 값인지 확인해서 우연히 맞은 바이트를 걸러 냅니다.

위 형식 번호 표에는 LZFSE·LZBITMAP 번호가 없으므로, 이 표에 없는 번호를 만났다고 손상으로 단정하지 않습니다. 도구 결과에서 내용이 비어 있는 파일을 만나면 `com.apple.decmpfs` 속성이 있는지, 형식 번호가 무엇인지 직접 확인합니다. 도구가 어떤 형식을 지원하는지는 [도구 검증](../../03-techniques/reporting/tool-validation.md) 방식으로 확인합니다.

## 도구

| 도구 | 쓰임 |
|---|---|
| lzfse 참조 구현 (Apple 공개, BSD 3-Clause) | `bvx` 계열 블록 구조의 기준이고, 블록을 풀 때 씁니다 |
| The Sleuth Kit | 소스에 decmpfs 형식 번호와 압축 단위 정의가 있어서 투명 압축 파일을 읽을 때 기준으로 삼습니다 |
| libyal dtformats 문서 | tracev3 청크와 `bv41` 블록 구조를 확인할 때 봅니다 |
| libfshfs | HFS+ 투명 압축 파일 정보를 다루는 공개 라이브러리입니다 |

도구 이름은 예로 든 것이고, 결과가 의심스러우면 위 헥스 순서대로 블록 하나를 직접 따라가 봅니다.

## 참고 문헌

1. lzfse/lzfse — src/lzfse_internal.h (Apple LZFSE 참조 구현), https://raw.githubusercontent.com/lzfse/lzfse/master/src/lzfse_internal.h
2. Apple Developer Documentation — compression_algorithm, https://developer.apple.com/tutorials/data/documentation/compression/compression_algorithm.json
3. apple-oss-distributions/xnu — bsd/sys/decmpfs.h, https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/sys/decmpfs.h
4. libyal/dtformats — Apple Unified Logging and Activity Tracing formats (판 0.0.10, 2023년 6월), https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
5. The Sleuth Kit — tsk/fs/decmpfs.h, https://raw.githubusercontent.com/sleuthkit/sleuthkit/develop/tsk/fs/decmpfs.h
6. libyal/libfshfs — Hierarchical File System (HFS) 문서 (개정 이력 0.0.17), https://github.com/libyal/libfshfs/blob/main/documentation/Hierarchical%20File%20System%20(HFS).asciidoc
