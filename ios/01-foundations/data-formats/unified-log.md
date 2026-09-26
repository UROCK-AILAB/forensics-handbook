---
title: "통합 로그 형식"
parent: "기반 · 데이터 저장 형식"
nav_order: 160
---

# 통합 로그 형식 (Unified Log·tracev3)

## 한 줄 요약

통합 로그 (Unified Log) 는 로그 본체인 tracev3 파일과 메시지 문장을 담은 uuidtext·공유 캐시 문자열 파일이 짝을 이루는 이진 형식이고, 시각을 부팅 뒤 흐른 시간으로 적기 때문에 파일 하나만으로는 문장도 실제 시각(wall clock)도 온전히 되살릴 수 없습니다.

Apple 은 이 형식의 공식 명세를 내지 않았습니다.

## 이 형식을 쓰는 아티팩트

통합 로그는 macOS 10.12 에서 처음 나왔고, macOS 뿐만 아니라 iOS·watchOS·tvOS 에도 있습니다[2]. libyal 형식 문서는 macOS 10.12 부터 13 까지를 시험한 결과입니다[1]. iOS 가 어느 버전부터 이 형식을 썼는지 밝힌 공개 자료는 없습니다. 맥과 파일 구조는 같고, iOS 에서는 기기에서 파일을 꺼내 오는 방법이 다릅니다(아래 "읽는 법").

통합 로그는 아래 파일들로 이루어집니다[1].

| 파일 | 위치 | 담는 것 |
|---|---|---|
| tracev3 | `/private/var/db/diagnostics/` 아래 `Persist`, `Special`, `Signpost` 등의 폴더 | 로그 항목 본체 |
| timesync | `/private/var/db/diagnostics/` 아래 `timesync` 폴더 | 부트 UUID 별로 부팅 뒤 시간을 실제 시각으로 바꾸는 정보 |
| uuidtext | `/private/var/db/uuidtext/` 아래, UUID 로 이름 붙은 파일 | 형식 문자열 |
| dsc(공유 캐시 문자열) | `/var/db/uuidtext/dsc/` | 공유 캐시 쪽 형식 문자열 |

형식 문자열은 tracev3 가 아니라 uuidtext·dsc 에 있고, tracev3 에는 그 문자열을 가리키는 정보와 인수가 들어 있습니다. macos-UnifiedLogs 가 "UUID 파일에서 뽑은 메시지(Raw message)" 와 "tracev3 에서 뽑은 메시지 조각(Message entries)" 을 따로 내보내는 것도 이 나뉨 때문입니다[2]. 그래서 tracev3 만 있고 uuidtext 가 없으면 메시지 문장을 온전히 되살리기 어려울 가능성이 큽니다.

통합 로그에서 찾을 사건과 그 뜻은 [통합 로그에서 찾을 것](../../02-artifacts/logs/unified-log-events.md)에서, sysdiagnose 에 함께 들어오는 로그는 [sysdiagnose 안의 로그](../../02-artifacts/logs/sysdiagnose-logs.md)에서 다룹니다.

## 구조

tracev3 파일은 헤더 청크 하나로 시작하고, 그 뒤로 카탈로그 청크와 그 카탈로그에 딸린 청크셋 여러 개가 한 묶음이 되어 되풀이됩니다[1].

| 청크 태그 | 이름 | 내용 |
|---|---|---|
| `0x1000` | 헤더 청크 | 224바이트. 부트 UUID 가 들어 있음 |
| `0x600b` | 카탈로그 | 뒤따르는 청크셋들이 이 카탈로그에 딸림 |
| `0x600d` | 청크셋 | LZ4 로 압축한 데이터 |
| `0x6001` | Firehose | Firehose 청크 |

청크셋 안의 LZ4 데이터는 블록 표지로 구간을 나눕니다[1].

| 블록 표지 | 뜻 |
|---|---|
| `bv41` | 압축한 블록 |
| `bv4-` | 압축하지 않은 블록 |
| `bv4$` | 끝 |

헤더 청크의 부트 UUID(Boot identifier)는 빅 엔디언으로 저장되고, 이 값으로 로그 항목을 특정 부팅과 이어 붙입니다[1]. 헤더 청크 안에서 부트 UUID 가 놓인 오프셋과 나머지 필드 배치는 libyal 문서에서 봅니다[1].

아래는 표지 설명대로 만든 예시입니다. 청크셋 데이터를 헥스로 볼 때 이 네 글자가 ASCII 로 보이면 LZ4 블록의 시작이나 끝이라는 뜻입니다.

```
바이트          ASCII   뜻
62 76 34 31     bv41    압축한 블록 시작
62 76 34 2D     bv4-    압축하지 않은 블록 시작
62 76 34 24     bv4$    끝
```

## 시각

로그 항목의 시각은 실제 시각이 아니라 mach continuous time, 곧 부팅 뒤 흐른 단위 수로 저장되고, timebase(분자/분모)를 곱해 초로 바꿉니다[1]. 그래서 날짜와 시각으로 바꾸려면 그 부팅의 기준점이 따로 있어야 하고, timesync 파일이 부트 UUID 마다 이 기준점을 담습니다[1]. timesync 파일의 필드 배치도 libyal 문서에서 봅니다[1].

macos-UnifiedLogs 는 Intel 과 ARM 두 방식의 시각을 모두 처리합니다[2]. 출력에는 시각(Timestamp)과 함께 시간대(Timezone)와 부트 UUID(Boot UUID) 필드가 있어서[2], 한 줄의 시각이 어느 부팅 기준으로 계산됐는지 따라가 볼 수 있습니다. 다른 아티팩트 시각과 합치는 법은 [시각 값](../value-decoding/time-values.md)과 [타임라인 작성](../../03-techniques/analysis/timeline/index.md)에서 다룹니다.

## 읽는 법

iOS 에서 로그를 꺼내는 방법은 두 가지가 공개돼 있습니다[3].

1. Mac 에 기기를 연결하고 아래 명령으로 logarchive 묶음을 만듭니다. 같은 일을 하는 제3자 공개 도구도 있습니다[3].

   ```
   sudo log collect --device --output <이름>.logarchive
   ```

2. 전체 파일 시스템 추출본이 있으면 `/private/var/db/diagnostics` 와 `/private/var/db/uuidtext` 를 꺼내 `.logarchive` 묶음 폴더에 넣고, 원본 iOS 버전에 맞는 `OSArchiveVersion` 정수를 담은 `Info.plist` 를 함께 넣습니다[3]. 추출 방식 자체는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md)에서 다룹니다.

묶음을 만든 뒤에는 두 가지 방법으로 읽습니다. 하나는 Mac 의 `log show` 로 JSON 으로 바꾼 뒤 iLEAPP 로 SQLite 에 넣어 조회하는 방법이고, 이때 Timestamp, Process ID, Subsystem, Category, Event Message, Trace ID 필드를 뽑습니다[3].

```
log show --style json <이름>.logarchive > logarchive.json
```

다른 하나는 Mandiant 가 공개한 러스트 해석기 macos-UnifiedLogs 로, 여러 운영체제에서 실행되고 결과를 JSONL 이나 CSV 로 냅니다[2]. 출력 필드는 아래와 같습니다[2].

| 묶음 | 필드 |
|---|---|
| 누가 | Process ID, Thread ID, EUID, Process, Process UUID, Library, Library UUID |
| 무엇을 | Log Message, Raw message, Message entries, Log Type, Event Type, Subsystem, Category |
| 어떤 흐름에서 | Activity ID, Parent Activity ID |
| 언제 | Timestamp, Timezone, Boot UUID |

## 포렌식에서 중요한 점

로그 양이 매우 많습니다. 1초 동안 1만 4천 건에서 3만 건 넘게 쌓인 예가 있고, 1.63GB 짜리 logarchive 를 JSON 으로 바꾸니 29.19GB 가 된 예도 있습니다[3]. 변환 결과를 담을 저장 공간과 시간을 미리 잡고, 조사 시간대와 프로세스·Subsystem 으로 범위를 좁혀 읽는 편이 현실적입니다.

tracev3 와 uuidtext 는 짝으로 다뤄야 합니다. 둘 중 하나만 확보하면 메시지 문장이나 시각 계산의 일부를 잃을 수 있어서, 파일 시스템에서 꺼낼 때는 두 폴더를 함께 꺼내고 해시를 따로 남깁니다.

지운 로그나 손상된 tracev3 를 복구하는 동작은 공개된 분석 자료가 없습니다. 청크셋이 LZ4 블록 단위로 나뉘어 있으므로 파일 일부가 망가져도 `bv41`·`bv4-` 표지를 찾아 남은 블록만 풀어 볼 여지는 있지만, 검증된 절차는 아닙니다.

## 함정

macos-UnifiedLogs 는 printf 오류 코드를 뜻으로 풀지 않고 번호 그대로 두며, 지원하지 않는 객체는 base64 로 내보냅니다[2]. 출력에 숫자나 base64 가 보이면 해석 실패가 아니라 도구가 풀지 않은 값일 수 있습니다.

아이폰 로컬 백업에는 이름에 로그가 들어간 영역이 있습니다. 도메인 `AppDomainPlugin-com.apple.DiagnosticExtensions.CrashLogs`, `SysSharedContainerDomain-systemgroup.com.apple.mobile.installationhelperlogs`, 그리고 `WirelessDomain` 의 `Library/Preferences/com.apple.AppleBasebandManager.plist` 안의 `systemlogs.mode` 키가 그 예입니다. 이들이 통합 로그와 직접 관련 있다는 공개 자료는 없으므로, 이름만 보고 통합 로그를 확보했다고 적지 않습니다. tracev3 가 백업에 들어 있는지는 실제 백업으로 확인합니다. 충돌 기록은 [충돌·진단 기록](../../02-artifacts/app-usage/diagnostics.md)에서 다룹니다.

개인정보를 가리는 표시(`<private>`)가 붙는 조건과 로그 수준별 보관 기간은 실제 기기로 확인합니다. 어떤 사건의 로그가 없다는 사실만으로 그 사건이 없었다고 쓰지 않습니다.

## 도구

Mac 의 `log` 명령(`log collect`, `log show`)이 logarchive 를 만들고 읽는 기본 수단이고[3], iLEAPP 가 JSON 결과를 SQLite 로 옮겨 조회를 돕습니다[3]. Mac 이 없는 환경에서는 macos-UnifiedLogs 가 tracev3·uuidtext·dsc 를 직접 풉니다[2]. 두 방법으로 얻은 결과를 서로 대조해 도구를 검증하는 절차는 [도구 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 참고 문헌

1. libyal dtformats — Apple Unified Logging and Activity Tracing formats — https://github.com/libyal/dtformats/blob/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
2. Mandiant — macos-UnifiedLogs (GitHub README) — https://github.com/mandiant/macos-UnifiedLogs
3. Alexis Brignoni (Initialization vectors) — Extraction, Processing, & Querying Apple Unified Logs from an iOS Device (2025-05) — https://abrignoni.blogspot.com/2025/05/extraction-processing-querying-apple.html
