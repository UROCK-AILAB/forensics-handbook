---
title: "UUID 텍스트와 공유 캐시"
parent: "통합 로그 형식"
grand_parent: "기반 · 데이터 저장 형식"
nav_order: 240
---

# UUID 텍스트와 공유 캐시 (uuidtext·dsc)

통합 로그의 문장 틀인 형식 문자열은 tracev3 파일이 아니라 `/private/var/db/uuidtext/` 아래의 uuidtext 파일과 공유 캐시 문자열(dsc) 파일에 들어 있고, 두 파일이 없으면 로그 항목을 끝까지 풀 수 없습니다.

## 이 형식을 쓰는 곳

통합 로그 항목에는 전체 문장이 아니라 형식 문자열을 가리키는 참조만 들어 있고, 문자열 본문은 uuidtext 파일과 dsc 파일에 따로 있습니다 [2]. 어느 파일을 찾아갈지는 Firehose 항목의 문자열 위치 플래그(strings file type)가 정하는데, main_exe·absolute·uuid_relative 값이면 uuidtext 파일로, shared_cache·large_shared_cache 값이면 dsc 파일로 갑니다 [2]. 플래그의 16진수 값과 Firehose 항목의 칸 배치는 [tracev3 파일 구조 (tracev3)](tracev3.md)에 있습니다.

## 위치

```
/private/var/db/uuidtext/00/ ~ /private/var/db/uuidtext/FF/
/private/var/db/uuidtext/dsc/
```

uuidtext 파일은 UUID 앞 두 글자(16진수 `00`~`FF`)를 이름으로 쓴 하위 폴더에 들어 있고, dsc 파일은 `dsc` 하위 폴더에 있습니다 [1][4]. `/var/db/uuidtext/` 로 적어도 같은 곳입니다 [4]. uuidtext 파일 이름은 UUID의 나머지 16진수 30글자라서, 예를 들어 `AB/414C1EC0233A05AF22029CC5E160EA` 는 UUID `AB414C1E-C023-3A05-AF22-029CC5E160EA` 를 뜻합니다 [2]. dsc 파일은 UUID 32글자를 그대로 이름으로 씁니다 [2]. 로그 아카이브 안에도 같은 `00`~`FF`·`dsc` 폴더가 들어가고, 아카이브 구성은 [로그 아카이브 만들고 읽기 (logarchive)](logarchive.md)에서 다룹니다.

## 버전별 차이

dsc 파일의 형식 버전은 macOS 10.12~11 Big Sur에서 1.0이고 macOS 12 Monterey와 13 Ventura에서 2.0이며, 2.0에서는 범위 설명자와 UUID 설명자의 칸이 넓어졌습니다 [2]. Mandiant 글도 macOS 12에서 dsc 파일 형식이 바뀌었다고 적었습니다 [4]. uuidtext 파일은 참고 문헌에 버전별 차이가 적혀 있지 않습니다.

## 구조

### uuidtext 파일

uuidtext 파일은 16바이트 머리 뒤에 항목 설명자 배열이 오고, 파일 끝에 이미지 경로 문자열이 붙은 모양입니다 [2].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 서명 `\x99\x88\x77\x66` (리틀엔디언 정수로 0x66778899) |
| 4 | 4 | 값 2. 주 버전으로 보이나 확인 안 됨 |
| 8 | 4 | 값 1. 부 버전으로 보이나 확인 안 됨 |
| 12 | 4 | 항목 수 |
| 16 | 8×n | 항목 설명자 배열 |

항목 설명자 하나는 8바이트입니다 [2].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 범위 시작 오프셋 |
| 4 | 4 | 항목 크기 |

파일 끝(footer)에는 UTF-8로 쓰고 NULL로 끝나는 이미지 경로 문자열이 있어서, 이 파일의 문자열이 어느 실행 파일이나 라이브러리에서 왔는지 알 수 있습니다 [2].

### dsc 파일

dsc 파일은 dyld 공유 캐시에 든 시스템 라이브러리들의 형식 문자열을 담고, 머리 뒤에 범위 설명자와 UUID 설명자가 옵니다 [2].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 서명 `hcsd` |
| 4 | 2 | 주 버전 |
| 6 | 2 | 부 버전 |
| 8 | 4 | 범위 수 |
| 12 | 4 | UUID 수 |

범위 설명자는 버전마다 칸 순서와 크기가 다릅니다 [2].

| 버전 | 크기 | 칸 (앞에서부터, 괄호는 바이트 수) |
|---|---|---|
| v1 | 16바이트 | UUID 설명자 번호(4), dsc 범위 오프셋(4), 데이터 오프셋(4), 범위 크기(4) |
| v2 | 24바이트 | dsc 범위 오프셋(8), 데이터 오프셋(4), 범위 크기(4), UUID 설명자 번호(8) |

UUID 설명자는 범위가 어느 이미지(라이브러리)에 속하는지 알려 줍니다 [2].

| 버전 | 크기 | 칸 (앞에서부터, 괄호는 바이트 수) |
|---|---|---|
| v1 | 28바이트 | 텍스트 오프셋(4), 텍스트 크기(4), 이미지 UUID(16, 빅엔디언), 이미지 경로 오프셋(4) |
| v2 | 32바이트 | 텍스트 오프셋(8), 텍스트 크기(4), 이미지 UUID(16, 빅엔디언), 이미지 경로 오프셋(4) |

이미지 UUID는 빅엔디언으로 적혀 있어서, 도구가 보여 주는 UUID와 헥스 편집기에서 읽은 바이트를 맞춰 볼 때 바이트 순서를 뒤집지 않습니다. UUID 표기는 [식별자 읽기 (UUID·UID·GUID)](../../value-decoding/uuid-uid.md)에서 설명합니다.

## 읽는 법

### 헥스로 한 번

아래는 명세의 칸 배치로 만든 예시이고 실제 검체에서 나온 값이 아닙니다. libyal 문서가 uuidtext 파일의 바이트 순서를 리틀엔디언으로 적어서 [2] 숫자 칸도 리틀엔디언으로 적었습니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    99 88 77 66 02 00 00 00 01 00 00 00 02 00 00 00
0x10    00 10 00 00 40 00 00 00 40 10 00 00 20 00 00 00
```

1. 0x00~0x03의 `99 88 77 66` 은 uuidtext 서명입니다.
2. 0x04~0x07의 `02 00 00 00` 은 2, 0x08~0x0B의 `01 00 00 00` 은 1이고, libyal 문서는 이 두 칸을 형식 버전으로 짐작만 했습니다.
3. 0x0C~0x0F의 `02 00 00 00` 은 항목 수 2라서 0x10부터 8바이트 설명자가 두 개 옵니다.
4. 첫 설명자는 범위 시작 오프셋 0x1000, 항목 크기 0x40이고, 둘째 설명자는 범위 시작 오프셋 0x1040, 항목 크기 0x20입니다.
5. 파일 맨 끝에서 거꾸로 NULL 바이트를 찾아 그 앞의 UTF-8 문자열을 읽으면 이미지 경로가 나옵니다.

dsc 파일은 첫 4바이트가 `68 63 73 64`(`hcsd`)라서 서명만으로 uuidtext와 가려낼 수 있고, 머리의 주 버전이 1이면 v1 표를, 2이면 v2 표를 씁니다 [2]. 맥에서는 `log raw-dump -s` 로 dsc 파일을 가공 전 모양으로 볼 수 있습니다 [2].

### 공개 도구로 한 번

Apple의 `log show` 로 대상 맥이나 로그 아카이브를 읽는 법은 [로그 아카이브 만들고 읽기 (logarchive)](logarchive.md)에 있습니다. Mandiant의 macos-unifiedlogs도 tracev3와 함께 uuidtext·dsc 파일을 읽어 문장을 채웁니다 [3].

## 포렌식에서 중요한 점

uuidtext·dsc 파일이 빠지면 파서가 문자열을 다 뽑지 못합니다 [3]. 디스크 이미지 대신 파일만 골라 수집할 때는 `/private/var/db/diagnostics/` 와 함께 `/private/var/db/uuidtext/` 를 통째로 가져옵니다. 수집 범위를 정하는 법은 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)에서 다룹니다.

uuidtext 파일 끝의 이미지 경로와 dsc 파일의 UUID 설명자는 어떤 실행 파일이나 라이브러리가 로그를 남겼는지 알려 줍니다 [2]. 도구 결과에 나온 프로세스 이름만 믿지 말고 이 이미지 경로를 함께 보면, 같은 이름을 쓴 다른 실행 파일을 가려내는 데 도움이 됩니다. 실행 파일 자체를 확인하는 법은 [악성 코드 흔적 분석 (Malware Triage)](../../../03-techniques/analysis/malware-triage/index.md)에서 다룹니다.

## 함정

문자열 파일이 빠졌거나 맞지 않을 때 도구가 어떻게 표시하는지는 도구마다 다르고 참고 문헌이 정리하지 않았습니다. 결과 문장이 비어 있거나 형식 문자열만 보이면 로그가 없었다고 보지 말고 uuidtext·dsc 수집이 빠졌는지 먼저 확인합니다.

값이 `<private>` 로 보이는 항목은 문자열 파일 문제와 따로 봐야 하고, 가려지는 규칙은 [보관 기간과 로그 수준 (Persist·Info·Debug)](retention-levels.md)에서 다룹니다.

## 참고 문헌

1. libyal dtformats — Apple Unified Logging and Activity Tracing formats (GitHub 보기) — https://github.com/libyal/dtformats/blob/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
2. 같은 문서 raw 본문 — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
3. Mandiant macos-UnifiedLogs README — https://raw.githubusercontent.com/mandiant/macos-UnifiedLogs/main/README.md
4. Alexander Holcomb (Mandiant), Reviewing macOS Unified Logs (Google Cloud 블로그, 2022-08-31) — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
