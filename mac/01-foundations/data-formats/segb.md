---
title: "SEGB 형식"
parent: "기반 · 데이터 저장 형식"
nav_order: 280
---

# SEGB 형식 (SEGB)

SEGB는 Apple이 바이옴 (Biome) 사건 기록을 쌓는 데 쓰는 바이너리 파일 형식이고, 매직 `SEGB` 가 파일 맨 앞에 있으면 v2, 헤더 끝(오프셋 52)에 있으면 v1이며, 두 판 모두 기록마다 상태 값과 맥 절대 시각을 남깁니다. 이 페이지는 두 판의 헤더·기록·트레일러 구조와 손으로 읽는 순서, 삭제 표시된 기록이 남기는 흔적을 다룹니다.

## 이 형식을 쓰는 아티팩트

Biome은 스트림마다 폴더를 두고 그 안에, 보통은 `local` 폴더 안에 SEGB 파일로 사건 기록을 쌓습니다 [2]. 스트림 폴더의 위치와 어떤 스트림이 무엇을 담는지는 [바이옴 (Biome)](../../02-artifacts/execution/biome/index.md)에서 다루고, 여기서는 파일 하나의 형식만 설명합니다. 기록 안의 데이터(payload)는 대개 protobuf라서 [2], SEGB 구조를 풀어 기록을 꺼낸 다음 스트림마다 protobuf를 따로 해석해야 합니다.

CCL의 ccl-segb 저장소는 스스로를 "Module(s) related to reading SEGB (fka "Biome") data from iOS, mascOS, etc." 라고 설명합니다(mascOS는 원문 오타) [1]. Apple 공식 문서에 SEGB 설명이 있는지는 확인하지 못했고, 이 페이지의 구조는 공개 도구의 소스 코드와 연구자 글에서 가져왔습니다.

### 판마다 등장한 시기

macOS에서 SEGB가 처음 나온 버전과 v1에서 v2로 바뀐 버전은 확인하지 못했습니다. iOS 쪽 자료만 있고, 그마저 자료끼리 다릅니다.

| 판 | iOS 등장 (Cellebrite) [2] | 다른 자료 |
|---|---|---|
| v1 | iOS 15 | Mattia Epifani는 iOS 14를 SEGB를 처음 관찰한 버전으로 적음 [6] |
| v2 | iOS 17에서 도입 | — |

macOS 검체에서는 버전으로 판을 짐작하지 말고, 파일마다 매직 위치를 보고 판을 가립니다.

## 구조

### 판 구분

| 판 | 매직 `SEGB` 위치 [1] |
|---|---|
| v1 | 오프셋 52 (56바이트 헤더의 마지막 4바이트) |
| v2 | 오프셋 0 |

ccl-segb는 v1과 v2를 읽는 모듈을 따로 두고, 공통 모듈이 헤더를 보고 어느 쪽인지 가리며, 둘 다 아니면 ValueError를 냅니다 [1].

### v1

v1은 56바이트 파일 헤더 뒤에 기록이 이어지는 모양입니다 [1].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 데이터 끝 오프셋, uint32 LE |
| 4 | 48 | 이 페이지의 참고 문헌에 설명 없음 |
| 52 | 4 | 매직 `SEGB` |

기록마다 32바이트 헤더가 먼저 오고, ccl-segb 소스는 이를 `<iiddIi` 로 읽습니다 [1].

| 기록 헤더 오프셋 | 크기 | 형 | 내용 |
|---|---|---|---|
| 0 | 4 | int32 | 데이터 길이 |
| 4 | 4 | int32 | 상태 |
| 8 | 8 | double | 시각1 (맥 절대 시각) |
| 16 | 8 | double | 시각2 (맥 절대 시각) |
| 24 | 4 | uint32 | CRC32. 데이터에 zlib crc32를 적용한 값 |
| 28 | 4 | int32 | 미상 |

기록 헤더 뒤에 데이터가 오고, 다음 기록은 8바이트 경계에서 시작합니다 [1].

### v2

v2는 헤더, 기록들, 빈 영역, 트레일러가 이 순서로 붙은 파일이고, v1과 달리 기록의 상태와 시각이 기록 헤더가 아니라 파일 끝 트레일러에 모여 있습니다 [1][2].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 매직 `SEGB` |
| 4 | 4 | 기록 개수, int32 LE |
| 8 | 8 | 파일 생성 시각, double |
| 16 | 16 | Cellebrite 설명으로 내부용 12바이트 + 패딩 4바이트 [2] |

기록은 8바이트 헤더(uint32 CRC32, int32 미상) 뒤에 데이터가 붙은 모양이고 4바이트 경계로 정렬합니다 [1][2]. v2의 CRC32가 어느 범위에 대한 값인지는 이 페이지의 참고 문헌에 적혀 있지 않습니다.

트레일러는 파일 끝에서 (기록 개수 × 16)바이트이고, 항목 하나가 기록 하나를 가리킵니다 [1][2].

| 트레일러 항목 오프셋 | 크기 | 형 | 내용 |
|---|---|---|---|
| 0 | 4 | int32 | 기록 끝 오프셋(헤더 끝 기준) |
| 4 | 4 | int32 | 상태 |
| 8 | 8 | double | 기록 생성 시각 |

### 기록 상태 값

| 값 | 뜻 [1][2] | ccl-segb 처리 [1] |
|---|---|---|
| 1 | Written (기록됨) | 읽음 |
| 3 | Deleted (삭제됨) | 읽음 |
| 4 | Unknown. 코드 주석은 "State 4 is an empty record" | 건너뜀 |

v2 트레일러에는 상태 0에 끝 오프셋도 0인 빈 칸이 끼어 있을 수 있습니다 [1].

## 읽는 법

아래 헥스는 위 표대로 만든 v2 헤더 예시이고 실제 검체에서 나온 값이 아닙니다. `??` 는 참고 문헌에서 뜻을 정하지 않은 바이트입니다.

```
00000000: 53 45 47 42 03 00 00 00 00 00 00 80 93 DC C4 41  SEGB...........A
00000010: ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??  ................
```

1. 오프셋 0에 `53 45 47 42` (`SEGB`)가 있으니 v2입니다. 오프셋 0에 없고 오프셋 52에 있으면 v1이고, 둘 다 없으면 SEGB가 아니거나 헤더가 깨진 파일입니다.
2. 오프셋 4의 `03 00 00 00` 은 리틀엔디언 int32라서 기록 개수는 3입니다.
3. 오프셋 8의 `00 00 00 80 93 DC C4 41` 을 리틀엔디언 double로 읽으면 700000000.0이고, 2001-01-01 00:00:00 UTC부터 그만큼 초를 더하면 2023-03-08 20:26:40 UTC입니다. 이 값이 파일 생성 시각입니다.
4. 트레일러는 파일 끝에서 3 × 16 = 48바이트 앞부터 시작합니다. 항목마다 끝 오프셋·상태·시각을 읽고, 끝 오프셋에 헤더 크기 32를 더하면 파일 처음 기준 위치가 됩니다.
5. 첫 기록은 헤더 바로 뒤(오프셋 32)에서 시작하고, 그 뒤 기록은 앞 기록의 끝을 4바이트 경계로 올린 자리에서 시작한다고 보고 읽습니다. 이 순서는 구성과 정렬 규칙에서 이끌어낸 것이라서, 결과가 이상하면 도구 소스 [1]와 맞춰 봅니다.
6. 기록마다 앞 8바이트(CRC32, 미상)를 건너뛰면 데이터이고, 데이터는 스트림에 맞는 protobuf 정의로 풉니다.

v1은 헤더 오프셋 0의 데이터 끝 오프셋까지를 기록 영역으로 보고, 오프셋 56부터 32바이트 기록 헤더를 읽어 길이만큼 데이터를 꺼낸 뒤 8바이트 경계로 올려 다음 기록으로 갑니다. v1은 CRC32가 데이터에 대한 zlib crc32라고 소스에 적혀 있어서 [1], 꺼낸 데이터로 CRC를 다시 계산해 헤더 값과 맞는지 볼 수 있습니다.

## 포렌식에서 중요한 점

### 삭제 표시와 남는 시각

상태 3(Deleted) 기록도 시각은 남습니다 [1][2]. 기록 내용을 0으로 지운 뒤에도 쓰기 시각은 남아 있을 수 있다고 Epifani가 적고 있어서 [5], 데이터가 비어 있어도 "그 시각에 이 스트림에 기록이 하나 쓰였다" 는 사실은 보고서에 쓸 수 있습니다. 반대로 데이터가 없으면 그 기록이 어떤 앱·사건이었는지는 이 파일만으로 말할 수 없습니다.

v2 트레일러에서는 항목 둘이 같은 끝 오프셋을 가리킬 수 있는데, 기록된 뒤 나중에 삭제 표시가 붙은 기록 같은 경우입니다 [1]. 한 기록이 두 번 세어진 것으로 보지 말고, 같은 자리의 상태가 바뀐 이력으로 읽습니다. 오래된 트레일러 항목이 이미 다시 쓰인 영역을 가리키면 원래 데이터는 남아 있지 않아서 [1], 그 항목의 시각과 상태만 믿고 데이터는 그 자리에 새로 쓰인 기록의 것으로 봅니다.

### 손상과 확인

v1은 기록마다 데이터 CRC32가 있어서 [1], 다시 계산한 값이 다르면 기록이 깨졌거나 바뀐 것을 알 수 있습니다. v2는 트레일러가 파일 끝에 있고 기록 개수로 그 시작을 계산하기 때문에, 파일 끝이 잘리거나 헤더의 기록 개수가 어긋나면 트레일러 전체를 잘못 읽습니다. 이 점은 구조에서 이끌어낸 것이라서, 트레일러 항목의 끝 오프셋이 파일 크기 안에 들어오는지, 상태 값이 0·1·3·4 가운데 하나인지를 확인해 읽은 결과를 거릅니다.

## 함정

- **도구마다 다른 행 수**: iLEAPP은 Deleted 기록을 시각만 있는 행으로 내고 [3], mac_apt는 Deleted 기록을 출력하지 않아서 [4] 같은 파일에서도 결과 행 수가 다를 수 있습니다. 행 수가 다르면 먼저 상태 값을 세어 봅니다.
- **v1의 두 시각**: v1 기록 헤더에는 시각이 두 개 있지만 각각 무엇을 뜻하는지는 참고 자료에 적혀 있지 않습니다. ccl-segb는 v1 기록에 timestamp1·timestamp2를 모두 내주고, v2에는 timestamp2가 없습니다 [1].
- **기준 시각과 시간대**: ccl-segb 소스는 모든 시각을 맥 절대 시각(2001-01-01 00:00:00 기준 초, double)으로 읽고 [1], Cellebrite 글은 v2 시각의 기준을 적지 않았습니다 [2]. ccl-segb는 시간대 없는 날짜·시각 값을 만들고 iLEAPP은 UTC를 붙여 보여 주니 [1][3], 두 도구의 결과를 한 타임라인에 넣을 때는 시간대를 먼저 맞춥니다. 맥 절대 시각을 푸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../value-decoding/mac-time-values.md)에 있습니다.
- **판과 OS 버전**: SEGB 판이 바뀐 시기는 iOS 자료만 있고 자료끼리도 다릅니다 [2][6]. macOS 버전만 보고 판을 정하지 말고 파일마다 매직 위치를 봅니다.

## 도구

ccl-segb는 SEGB v1·v2를 읽는 Python 모듈이고, 명령줄 도구 `ccl_segb_cli.py <파일>` 로 파일 내용을 덤프하거나 미리 볼 수 있습니다 [1]. 기록마다 v1은 data_start_offset, state, data, timestamp1, timestamp2를, v2는 data_start_offset, metadata_offset, 상태 이름, creation(시각), data를 내주니 [1], 데이터 시작 오프셋으로 원본 파일의 같은 자리를 헥스로 열어 결과를 맞춰 볼 수 있습니다. iLEAPP과 mac_apt도 Biome 해석 과정에서 SEGB를 읽지만, 위 함정처럼 삭제 기록을 다루는 방식이 서로 다릅니다 [3][4]. 도구를 검증하는 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)을, 여러 스트림의 기록을 한 시간축에 놓는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)을 따릅니다.

## 참고 문헌

1. CCL (Alex Caithness), ccl-segb — README, ccl_segb1.py, ccl_segb2.py, ccl_segb_common.py — https://github.com/cclgroupltd/ccl-segb
2. Shai Shapira (Cellebrite), "Understanding and Decoding the Newest iOS SEGB Format" (2023-10-16) — https://cellebrite.com/en/understanding-and-decoding-the-newest-ios-segb-format/
3. iLEAPP — scripts/artifacts/biomeInfocus.py, biomeDKInfocus.py, biomeStreams.py, scripts/ilapfuncs.py — https://github.com/abrignoni/iLEAPP
4. mac_apt (Yogesh Khatri), plugins/biome.py v1.1 — https://github.com/ydkhatri/mac_apt/blob/master/plugins/biome.py
5. Mattia Epifani, "84 Streams Later, Part 2: Inside Apple Biome" (2026-07-27) — https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html
6. Mattia Epifani, "84 Streams Later: Exploring the Evolution of Apple Biome in iOS" (2026-07-26) — https://blog.digital-forensics.it/2026/07/84-streams-later-exploring-evolution-of.html
