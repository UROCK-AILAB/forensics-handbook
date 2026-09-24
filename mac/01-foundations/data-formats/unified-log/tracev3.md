---
title: "tracev3 파일 구조"
parent: "통합 로그 형식"
grand_parent: "기반 · 데이터 저장 형식"
nav_order: 230
---

# tracev3 파일 구조 (tracev3)

tracev3 파일은 16바이트 머리가 붙은 청크(chunk)가 이어진 바이너리 파일이고, 로그 한 줄의 문장 대신 형식 문자열을 가리키는 참조와 Mach 연속 시각이 들어 있어서 문자열 파일과 timesync 파일을 함께 읽어야 사람이 읽는 로그로 풀립니다.

## 이 형식을 쓰는 곳

통합 로그는 로그 항목을 담는 tracev3 파일, 항목의 메타데이터와 형식 문자열을 담는 UUID 파일, 시각 메타데이터를 담는 timesync 파일 세 가지로 이뤄집니다 [3]. 이 페이지는 tracev3와 timesync를 다루고, 문자열 쪽은 [UUID 텍스트와 공유 캐시 (uuidtext·dsc)](uuidtext-dsc.md)에서 다룹니다.

tracev3 파일은 아래 네 폴더에 나뉘어 들어 있고, timesync 파일은 같은 상위 폴더의 `timesync` 폴더에 `.timesync` 확장자로 하나 이상 있습니다 [1][3].

```
/private/var/db/diagnostics/Persist/
/private/var/db/diagnostics/Special/
/private/var/db/diagnostics/Signpost/
/private/var/db/diagnostics/HighVolume/
/private/var/db/diagnostics/timesync/
```

`/var` 는 `/private/var` 를 가리키는 심볼릭 링크라서 `/var/db/diagnostics/` 로 적어도 같은 곳입니다 [3]. timesync 폴더 이름을 libyal 문서는 소문자 `timesync` 로, Mandiant 글은 `Timesync` 로 적었고 [1][3], 실제 대소문자는 이 두 자료로 가리지 못했습니다. 폴더마다 어떤 로그가 들어가는지 밝힌 공식 설명과 tracev3 파일 이름을 짓는 규칙도 참고 문헌에서 찾지 못했습니다. 폴더별 파일 크기와 개수 관측값은 [보관 기간과 로그 수준 (Persist·Info·Debug)](retention-levels.md)에 있습니다.

## 버전과 하드웨어에 따른 차이

| 항목 | 내용 | 출처 |
|---|---|---|
| libyal 문서가 형식을 확인한 범위 | macOS 10.12 ~ 13 | [1] |
| SimpleDump 청크(0x6004) | macOS 12 Monterey에서 추가 | [3] |
| Mach 시각 단위 | 인텔 맥은 나노초, Apple Silicon 맥은 틱(tick)이라서 나노초로 바꿔야 함 | [3] |

macOS 14 이후 형식은 이 표의 자료가 다루지 않아서, 새 버전 검체는 도구가 그 버전을 지원하는지부터 확인합니다.

## 구조

### 청크 머리 (16바이트)

모든 청크는 같은 머리로 시작하고, 청크는 64비트(8바이트) 경계에 맞춰 놓입니다 [1][2].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 청크 태그 |
| 4 | 4 | 서브 태그 |
| 8 | 8 | 데이터 크기 |
| 16 | - | 데이터 |

### 청크 태그

| 태그 | 이름 | 담는 것 |
|---|---|---|
| 0x1000 | Header | 파일 전체의 시각 기준값과 시스템 정보 |
| 0x600b | Catalog | UUID 배열, 서브시스템 문자열, 프로세스 정보 항목 |
| 0x600d | ChunkSet | LZ4로 압축한 블록 |
| 0x6001 | Firehose | 로그 항목(트레이스포인트) |
| 0x6002 | Oversize | 한 항목에 다 들어가지 않는 큰 데이터. Firehose 트레이스포인트가 참조함 |
| 0x6003 | StateDump | 프로세스 상태 덤프. 바이너리 plist·protobuf·사용자 정의 형식의 상태 데이터와 제목 |
| 0x6004 | SimpleDump | 서브시스템 문자열과 메시지 문자열을 청크 안에 직접 담음(macOS 12부터) |

태그 값과 각 청크의 설명은 libyal 문서에서 가져왔습니다 [1][2]. tracev3 파일은 Header 청크 하나로 시작하고, 뒤로 Catalog 청크와 그 Catalog에 딸린 ChunkSet 청크가 되풀이되며, 새 Catalog 청크가 나오면 앞의 Catalog를 대신합니다 [2].

### Header 청크 (0x1000)

Header 청크는 크기가 224바이트이고 Mach timebase 분자·분모, 연속 시각(continuous time), POSIX 초, 시간대 오프셋, 서머타임 플래그가 들어 있습니다 [1]. 시간대 오프셋은 UTC와의 차이를 분으로 적은 부호 있는 정수인데, 부호가 거꾸로라서 -60이 UTC+1을 뜻합니다 [2]. 안쪽에는 아래 하위 청크가 있습니다 [2].

| 하위 태그 | 이름 | 담는 것 |
|---|---|---|
| 0x6100 | Continuous time | Mach 연속 시각 |
| 0x6101 | System information | 빌드 버전, 하드웨어 모델 문자열 |
| 0x6102 | Generation | 부팅 UUID, logd PID, 종료 상태 |
| 0x6103 | Time zone | 시간대 정보 파일 경로 |

### Catalog 청크 (0x600b)

Catalog 청크에는 UUID 배열과 서브시스템 문자열, 프로세스 정보 항목, 청크 메타데이터가 들어 있습니다 [1]. 아래 오프셋은 청크 오프셋 16, 곧 데이터 영역 첫 바이트부터 셉니다 [2].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 2 | 서브시스템 문자열 오프셋 |
| 2 | 2 | 프로세스 정보 항목 오프셋 |
| 4 | 2 | 프로세스 정보 항목 수 |
| 6 | 2 | 하위 청크 오프셋 |
| 8 | 2 | 하위 청크 수 |
| 10 | 6 | 알 수 없음 |
| 16 | 8 | 가장 이른 Firehose 시각 |
| 24 | 16×n | 카탈로그 UUID 배열(빅엔디언) |

### ChunkSet 청크 (0x600d)

ChunkSet 청크의 데이터는 LZ4 블록으로 들어 있고, 블록마다 앞에 붙은 표지 문자열로 종류를 가립니다 [1]. LZ4 자체는 [압축 형식 (LZFSE·LZ4·zlib)](../../value-decoding/compression.md)에서 설명합니다.

| 표지 | 뜻 | 뒤따르는 머리 |
|---|---|---|
| `bv41` | 압축 블록 | 비압축 크기, 압축 크기 |
| `bv4-` | 비압축 블록 | 비압축 크기 |
| `bv4$` | 스트림 끝 | 없음 |

### Firehose 청크 (0x6001)

Firehose 청크는 로그 항목이 실제로 들어 있는 곳입니다. 아래 오프셋은 청크 처음부터 세고, 48바이트부터 트레이스포인트(tracepoint)가 이어집니다 [2].

| 청크 오프셋 | 크기 | 내용 |
|---|---|---|
| 16 | 8 | proc_id 첫 번째 수 |
| 24 | 4 | proc_id 두 번째 수 |
| 28 | 1 | TTL |
| 29 | 1 | collapsed 플래그 |
| 32 | 2 | 공개 데이터 크기 |
| 34 | 2 | 비공개 데이터 가상 오프셋 |
| 38 | 1 | 스트림 종류(persist·special·memory·signpost) |
| 40 | 8 | 기준 연속 시각(Mach) |
| 48 | - | 트레이스포인트 |

비공개 데이터가 없으면 가상 오프셋 칸에 4096(0x1000)이 들어가고, 있으면 비공개 데이터는 청크 끝쪽에 붙습니다 [2].

트레이스포인트 하나의 앞부분은 아래와 같습니다 [1].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 1 | 레코드 종류 |
| 1 | 1 | 로그 종류 |
| 2 | 2 | 플래그 |
| 4 | 4 | 형식 문자열 참조 |
| 8 | 8 | 스레드 ID |
| 16 | 6 | 연속 시각 차이 |
| 22 | 2 | 데이터 크기 |

레코드 종류 값은 activity 0x02, trace 0x03, log 0x04, signpost 0x06, loss 0x07입니다 [1]. 로그 종류 값은 아래와 같고, 수준마다 디스크에 남는지는 [보관 기간과 로그 수준 (Persist·Info·Debug)](retention-levels.md)에서 다룹니다 [2].

| 값 | 로그 종류 |
|---|---|
| 0x00 | default |
| 0x01 | info (activity 레코드에서는 create) |
| 0x02 | debug |
| 0x03 | useraction (activity 레코드에서만 보임) |
| 0x10 | error |
| 0x11 | fault |
| 0x40~0x42 | signpost, 스레드 범위 |
| 0x80~0x82 | signpost, 프로세스 범위 |
| 0xc0~0xc2 | signpost, 시스템 범위 |

플래그 칸의 문자열 위치 값(strings file type)은 형식 문자열을 어느 파일에서 찾을지 알려 줍니다 [2]. 찾아간 파일의 구조는 [UUID 텍스트와 공유 캐시 (uuidtext·dsc)](uuidtext-dsc.md)에 있습니다.

| 값 | 이름 | 찾아갈 파일 |
|---|---|---|
| 0x0002 | main_exe | uuidtext 파일, proc_id로 찾음 |
| 0x0004 | shared_cache | dsc 파일 |
| 0x0008 | absolute | uuidtext 파일, 참조로 찾음 |
| 0x000a | uuid_relative | uuidtext 파일, 식별자로 찾음 |
| 0x000c | large_shared_cache | dsc 파일 |

### Oversize 청크 (0x6002)

한 로그 항목에 다 들어가지 않는 큰 데이터는 Oversize 청크에 따로 두고, Firehose 트레이스포인트가 데이터 참조 값으로 이 청크를 가리킵니다 [2]. 오프셋은 청크 처음부터 셉니다 [2].

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 16 | 8 | proc_id 첫 번째 수 |
| 24 | 4 | proc_id 두 번째 수 |
| 28 | 1 | TTL |
| 29 | 3 | 예약 |
| 32 | 8 | 시각 |
| 40 | 4 | 데이터 참조 |
| 44 | 2 | 데이터 크기 |
| 46 | 2 | 비공개 데이터 크기 |
| 48 | - | 데이터 항목 |

### timesync 파일

timesync 파일에는 부팅 레코드와 동기 레코드가 들어 있고, 두 레코드는 앞 2바이트 서명으로 가립니다 [2].

부팅 레코드 (서명 `\xb0\xbb`, 48바이트)

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 2 | 서명 |
| 2 | 2 | 레코드 크기(48) |
| 4 | 4 | 알 수 없음 |
| 8 | 16 | 부팅 UUID |
| 24 | 4 | timebase 분자 |
| 28 | 4 | timebase 분모 |
| 32 | 8 | 시각(1970 기준 나노초, 또는 0) |
| 40 | 4 | 시간대 오프셋(분) |
| 44 | 4 | 서머타임 플래그 |

동기 레코드 (서명 `Ts`, 32바이트)

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 2 | 서명 |
| 2 | 2 | 레코드 크기(32) |
| 4 | 4 | 알 수 없음 |
| 8 | 8 | 커널 시각(Mach 연속 시각) |
| 16 | 8 | 시각(1970 기준 나노초) |
| 24 | 4 | 시간대 오프셋(분) |
| 28 | 4 | 서머타임 플래그 |

## 읽는 법

1. 파일 첫 바이트부터 16바이트 청크 머리를 읽어 태그와 데이터 크기를 얻습니다.
2. 태그가 0x600d(ChunkSet)이면 데이터 영역의 블록을 `bv41`·`bv4-`·`bv4$` 표지에 따라 풉니다.
3. 데이터 끝을 8바이트 경계로 올린 자리에서 다음 청크 머리를 읽고, 파일 끝까지 되풀이합니다.
4. Firehose 트레이스포인트에서 문자열 위치 플래그와 형식 문자열 참조를 읽어 uuidtext 또는 dsc 파일에서 형식 문자열을 찾습니다.
5. 연속 시각을 timebase 분자·분모와 timesync 레코드로 벽시계 시각으로 바꿉니다.

5번의 변환식은 libyal 문서에 두 가지로 적혀 있습니다 [2].

```
timesync 없음:  실제 시각 = 헤더 시각 + 연속 시각 × (분자 ÷ 분모)
timesync 있음:  실제 시각 = 동기 레코드 시각
                         + (연속 시각 − 동기 레코드 연속 시각) × (분자 ÷ 분모)
```

timesync 파일은 tracev3 파일과 부팅 UUID가 같은 것을 쓰고, 그 안에서 연속 시각에 맞는 동기 레코드를 고르며, 맞는 동기 레코드가 없으면 부팅 레코드를 기준(연속 시각 0)으로 씁니다 [2]. Apple이 변환 방법을 문서로 밝히지 않아서 libyal 문서도 이 식을 관찰한 동작으로 적었고, 소수점을 버리는지 올리는지도 모른다고 적었습니다 [2]. 벽시계 시각은 유닉스 시각, 곧 1970년 1월 1일 기준 나노초로 들어 있습니다 [2]. 트레이스포인트의 6바이트 연속 시각 차이는 Firehose 청크의 기준 연속 시각에서 떨어진 값이라서 [2], 둘을 더한 값을 위 식의 연속 시각으로 씁니다. 직접 계산한 값은 도구 결과와 맞춰 봅니다. 맥에서 쓰는 여러 시각 기준은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../value-decoding/mac-time-values.md)에서 비교합니다.

## 포렌식에서 중요한 점

tracev3 파일에는 문장 본문이 없고 형식 문자열 참조만 있어서, tracev3만 떼어 오면 로그를 끝까지 풀 수 없습니다. 수집할 때 uuidtext 폴더를 같이 가져와야 하는 까닭은 [UUID 텍스트와 공유 캐시 (uuidtext·dsc)](uuidtext-dsc.md)에서 설명합니다. timesync 파일이 있고 없음에 따라 시각 변환식이 달라져서 [2], 수집할 때 `timesync` 폴더도 빠뜨리지 않습니다.

Header 청크의 하위 청크에는 빌드 버전과 하드웨어 모델 문자열, 부팅 UUID, logd PID, 종료 상태가 들어 있어서 [2] 로그 파일이 어떤 모델의 어느 빌드에서 어느 부팅 구간에 쓰였는지 맞춰 볼 수 있습니다. timesync 레코드에도 부팅 UUID가 있어서 [2] 부팅마다 레코드를 나눠 볼 수 있습니다. 빌드 버전은 조사 대상 맥의 OS 버전 기록과 맞춰 보고, 그 기록은 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../../../02-artifacts/system-account/os-version-install-history.md)에 있습니다.

Catalog 청크의 가장 이른 Firehose 시각 칸은 [2] 파일마다 로그가 언제부터 시작하는지 빠르게 가늠할 때 씁니다. 오래된 메시지는 저장소 용량 한도에 따라 지워지고, 그 규칙은 [보관 기간과 로그 수준 (Persist·Info·Debug)](retention-levels.md)에서 다룹니다. 로그를 일부러 지운 흔적을 어떻게 가늠하는지는 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

## 함정

Apple Silicon 맥은 Mach 시각을 틱으로 기록해서 나노초로 바꿔야 하고 [3], 이 변환을 하지 않는 도구로 읽으면 시각이 틀어집니다. 도구가 인텔과 ARM 시각을 모두 지원하는지 확인합니다. Apple Silicon의 timebase 분자·분모 값은 참고 문헌에서 확인하지 못했고, 검체의 Header 청크나 timesync 부팅 레코드에 적힌 값을 그대로 씁니다.

시간대 오프셋과 서머타임 플래그는 Header 청크와 timesync 레코드에 따로 들어 있습니다 [1][2]. libyal 문서는 저장된 시각이 UTC로 보이고 `log` 도구는 현지 시간대로 바꿔 보여 준다고 적었으므로 [2], 보고서에 적을 때 UTC로 적었는지 현지 시각으로 적었는지 밝힙니다. 조사 대상 맥의 시간대 설정은 [시간대와 시계 설정 (Time Zone·NTP)](../../../02-artifacts/system-account/time-zone.md)에서 확인합니다.

libyal 문서가 확인한 범위는 macOS 10.12~13이라서 [1] 그 뒤 버전에서는 칸 배치가 달라졌을 수 있습니다. StateDump·SimpleDump 청크는 libyal 문서에도 알 수 없는 칸이 남아 있어서 [2], 이 청크에서 나온 값을 해석할 때는 도구 결과를 그대로 믿지 말고 같은 시각의 다른 로그 항목과 맞춰 봅니다.

## 도구

Apple의 `log show --file` 로 tracev3 파일 하나를 열 수 있고, 문장까지 풀려면 그 파일이 로그 아카이브나 시스템 로그 폴더 안에 있어야 합니다 [5]. 사용법은 [로그 아카이브 만들고 읽기 (logarchive)](logarchive.md)에 있습니다. 맥이 아닌 곳에서는 Mandiant의 공개 파서 macos-unifiedlogs(Rust)가 라이브 시스템과 로그 아카이브를 CSV·JSON으로 바꾸고 인텔과 ARM 시각을 모두 다룹니다 [3][4]. 맥에서는 `log raw-dump -f` 로 tracev3 파일을, `log raw-dump -t` 로 timesync 폴더를 가공 전 모양으로 볼 수 있습니다 [2]. 헥스로 직접 따라갈 때는 이 페이지의 표와 libyal 문서 원문 [2]를 옆에 두고 청크 머리부터 읽습니다.

## 참고 문헌

1. libyal dtformats — Apple Unified Logging and Activity Tracing formats (GitHub 보기) — https://github.com/libyal/dtformats/blob/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
2. 같은 문서 raw 본문 — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
3. Alexander Holcomb (Mandiant), Reviewing macOS Unified Logs (Google Cloud 블로그, 2022-08-31) — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
4. Mandiant macos-UnifiedLogs README — https://raw.githubusercontent.com/mandiant/macos-UnifiedLogs/main/README.md
5. SS64, macOS `log` 명령 설명 — https://ss64.com/mac/log.html
