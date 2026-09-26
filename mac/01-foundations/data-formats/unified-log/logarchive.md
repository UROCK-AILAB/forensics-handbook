---
title: "로그 아카이브 만들고 읽기"
parent: "통합 로그 형식"
grand_parent: "기반 · 데이터 저장 형식"
nav_order: 260
---

# 로그 아카이브 만들고 읽기 (logarchive)

`log collect` 로 만드는 `.logarchive` 는 tracev3·uuidtext·timesync 파일을 한 폴더에 모은 패키지이고, 메모리에만 있던 로그까지 담을 수 있어서 켜져 있는 맥에서 통합 로그를 모으거나 다른 맥에서 읽을 때 씁니다.

## 언제 쓰나

켜져 있는 맥에서 증거를 모을 때 `log collect` 로 아카이브를 만들면 디스크의 로그 파일과 함께 메모리에 있던 항목(`logdata.LiveData.tracev3`)도 담깁니다 [2]. 전원을 끈 뒤 뜬 디스크 이미지에는 이 메모리 항목이 없어서, 켜진 맥을 만났을 때 수집 순서에 넣어 둘 만합니다. 수집 순서는 [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md)에서 다룹니다.

디스크 이미지나 수집한 파일을 분석용 맥에서 읽을 때도 같은 폴더 구성을 맞추면 `log show --archive` 로 읽을 수 있고, 맥이 아닌 곳에서는 공개 파서가 아카이브를 읽습니다. 수준마다 메모리와 디스크 중 어디에 남는지는 [보관 기간과 로그 수준 (Persist·Info·Debug)](retention-levels.md)에서 다룹니다.

## 만들기

`log collect` 는 시스템 로그를 `.logarchive` 로 모으고, 만든 아카이브는 나중에 `log` 명령이나 Console 앱으로 봅니다 [1]. 아래처럼 sudo를 붙여 실행합니다 [2].

```
sudo log collect --output ~/system_logs.logarchive
```

주요 옵션은 아래와 같습니다 [1].

| 옵션 | 뜻 |
|---|---|
| `--output` | 저장할 경로. 폴더를 주면 그 안에 `system_logs.logarchive` 를 만들고, 빼면 현재 폴더에 만듦 |
| `--start` | 이 날짜·시각부터 모음 |
| `--last` | 지금부터 이만큼 전까지 모음. 숫자 뒤에 `m`·`h`·`d` |
| `--size` | 모을 양의 대략적인 한도. 숫자 뒤에 `k`·`m`. 실제로는 더 커질 수 있음 |
| `--device`, `--device-name`, `--device-udid` | 연결된 기기에서 모음 |

날짜는 `YYYY-MM-DD`, `YYYY-MM-DD HH:MM:SS`, `YYYY-MM-DD HH:MM:SSZZZZZ` 세 가지 형식으로 적습니다 [1]. `--last` 나 `--size` 로 범위를 줄이면 그 밖의 로그는 아카이브에 들어가지 않아서, 보고서에 수집 명령과 옵션을 그대로 적어 둡니다.

## 구조

`.logarchive` 는 패키지, 곧 폴더이고 Finder에서는 "패키지 내용 보기"로 엽니다 [2]. 안에는 아래 항목이 들어 있습니다 [2][3].

| 항목 | 내용 |
|---|---|
| `00`~`FF`, `dsc` | 형식 문자열이 든 UUID 파일 |
| `Persist`, `HighVolume`, `Signpost`, `Special` | tracev3 파일 |
| `logdata.LiveData.tracev3` | 메모리에 있던 항목 |
| `timesync` | 시각 변환용 파일 |
| `Extra` | logd에 관한 메타데이터. Mandiant 파서 기준으로 읽는 데 꼭 필요하지 않음 |
| `Info.plist` | logd에 관한 메타데이터. Mandiant 파서 기준으로 읽는 데 꼭 필요하지 않음 |

폴더마다 든 파일의 구조는 [tracev3 파일 구조 (tracev3)](tracev3.md)와 [UUID 텍스트와 공유 캐시 (uuidtext·dsc)](uuidtext-dsc.md)에 있습니다.

## 읽기

### log show

`log show --archive` 에 아카이브 경로를 주면 아카이브를 읽고, `log show --file` 에 tracev3 파일 경로를 주면 그 파일 하나만 읽습니다 [1]. `--file` 로 읽는 파일도 문장까지 풀려면 올바른 로그 아카이브나 시스템 로그 폴더 안에 있어야 합니다 [1].

```
log show --archive <아카이브 경로> --predicate '<조건>' --style ndjson
log show --file <tracev3 파일 경로>
```

| 옵션 | 뜻 |
|---|---|
| `--start`, `--end` | 볼 시간 범위 |
| `--last` | 아카이브의 마지막 항목부터 이만큼 전까지. `boot` 를 주면 아카이브에 든 마지막 부팅부터 |
| `--predicate` | NSPredicate 조건으로 거름 |
| `--style` | 출력 형식. default, compact, json, ndjson, syslog |
| `--info`, `--debug` | 해당 수준 메시지도 포함 |
| `--signpost` | signpost 포함 |
| `--timezone` | 출력 시간대. 빼면 항목을 기록할 때의 시간대로 보여 줌 |
| `--color` | 색 표시 |

predicate 조건에는 `eventMessage`, `eventType`, `messageType`, `process`, `processImagePath`, `sender`, `senderImagePath`, `subsystem`, `category` 필드를 씁니다 [1]. 조사에서 자주 찾는 서브시스템과 메시지는 [통합 로그에서 찾을 것 (Unified Log Events)](../../../02-artifacts/logs/unified-log-events/index.md)과 [통합 로그의 프로세스 실행 기록 (Process Events)](../../../02-artifacts/execution/unified-log-process.md)에서 다룹니다.

`--info`·`--debug` 를 붙이지 않으면 그 수준 메시지는 결과에 나오지 않아서 [1], 아카이브에 있는 info·debug 항목을 보려면 두 옵션을 붙입니다. 출력 시각은 `--timezone` 에 따라 달라지고 이 옵션을 빼면 항목을 기록할 때의 시간대로 나오므로 [1], 결과를 다른 로그와 합칠 때는 시간대를 밝혀 맞추고, 여러 로그를 한 줄로 세우는 법은 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)에서 다룹니다.

### 그 밖의 하위 명령

`log` 에는 `show` 와 `collect`, `config` 말고도 저장소나 아카이브의 이벤트 분포를 보여 주는 `stats`, 실시간으로 보는 `stream`, 로그 데이터를 지우는 `erase` 가 있습니다 [1]. `stats` 로 아카이브의 이벤트 분포를 먼저 보면 어느 프로세스와 서브시스템의 로그가 많은지 가늠하고 나서 predicate를 짤 수 있습니다.

### 프로그램으로 읽기 (OSLogStore)

macOS 10.15부터는 `OSLogStore` 로 로그를 프로그램에서 읽을 수 있습니다 [4]. `init(url:)` 로 아카이브를 열고 `local()` 로 현재 맥의 저장소를 열며, `position(date:)` 같은 메서드로 시작 위치를 잡은 뒤 `getEntries(with:at:matching:)` 에 NSPredicate를 넘겨 항목을 받습니다 [4]. 받은 항목은 `OSLogEntryLog`, `OSLogEntrySignpost`, `OSLogEntryActivity`, `OSLogEntryBoundary` 가운데 하나입니다 [4].

### 맥이 아닌 곳에서 읽기

Mandiant의 공개 파서 macos-unifiedlogs에 든 `unifiedlog_iterator` 는 로그 아카이브를 JSONL·CSV로 바꾸고 라이브 시스템도 읽습니다 [3]. 이 도구는 오류 코드를 사람이 읽는 문장으로 바꾸지 않고 숫자 그대로 내고, 지원하지 않는 사용자 정의 객체는 base64로 냅니다 [3]. Mandiant는 이 파서를 macOS 10.12~12에서 시험했습니다 [2]. 도구 결과를 `log show` 결과와 맞춰 보는 법은 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 증거로서 의미

아카이브로 알 수 있는 범위는 수집한 시점에 저장소와 메모리에 남아 있던 로그까지입니다. 용량 한도로 이미 지워진 로그는 아카이브에도 없고, `--last`·`--size` 로 범위를 줄였다면 그만큼 빠집니다.

`log erase` 는 로그 데이터를 지우는 명령이고, 옵션 없이 쓰면 주 저장소와 아직 기록 중인 로그를, `--all` 을 붙이면 TTL 로그와 fault·error 내용까지 지웁니다 [1]. 그래서 로그가 있어야 할 기간에 공백이 보이면 이 명령을 쓴 흔적일 가능성도 따져 봅니다. 공백만으로는 삭제를 단정하지 않고, 용량 한도에 따른 정상 삭제와 가려 보려면 다른 기록과 맞춰 봐야 합니다. 그 방법은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

## 함정

`log show` 와 공개 파서는 같은 항목을 다른 모양으로 보여 줄 수 있습니다. 공개 파서는 오류 코드를 숫자로, 사용자 정의 객체를 base64로 내서 [3] `log show` 결과와 글자 그대로 맞지 않을 수 있고, 가려진 비공개 값도 도구에 따라 다르게 보입니다. 비공개 값이 가려지는 규칙은 [보관 기간과 로그 수준 (Persist·Info·Debug)](retention-levels.md)에 있습니다.

`log show` 는 자기가 이해하지 못하는 더 새 시스템 버전의 데이터를 만나면 오류 코드 65(EX_DATAERR)로 끝나므로 [1], 분석용 맥의 macOS가 조사 대상보다 오래되면 아카이브를 읽지 못할 수 있습니다.

아카이브를 복사하거나 옮길 때 UUID 파일 폴더나 `timesync` 폴더가 빠지면 문장이나 시각이 제대로 풀리지 않습니다. uuidtext 폴더가 빠진 경우는 [UUID 텍스트와 공유 캐시 (uuidtext·dsc)](uuidtext-dsc.md)에서, timesync가 빠진 경우는 [tracev3 파일 구조 (tracev3)](tracev3.md)에서 다룹니다.

## 참고 문헌

1. SS64, macOS `log` 명령 설명 — https://ss64.com/mac/log.html
2. Alexander Holcomb (Mandiant), Reviewing macOS Unified Logs (Google Cloud 블로그, 2022-08-31) — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
3. Mandiant macos-UnifiedLogs README — https://raw.githubusercontent.com/mandiant/macos-UnifiedLogs/main/README.md
4. Apple Developer, OSLogStore — https://developer.apple.com/tutorials/data/documentation/oslog/oslogstore.json
