---
title: "통합 로그 수집"
parent: "라이브 대응"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 2010
---

# 통합 로그 수집 (log collect)

켜진 맥의 통합 로그 저장소를 `log collect` 로 `.logarchive` 하나에 떠서 옮기고, 분석 장비에서 `log show --archive` 로 읽습니다.

## 언제 쓰나

통합 로그 (Unified Log)는 디스크에 남는 기록이지만, 이 핸드북은 디스크 이미지를 뜨기 전에 따로 떠 두는 쪽을 권하고 그 까닭은 [휘발성 순서 (Order of Volatility)](order-of-volatility.md)에 있습니다. 디스크 이미지를 뜰 수 없거나 시간이 부족할 때도 로그만큼은 이 방법으로 먼저 확보합니다. 저장 형식은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에서, 무엇을 찾을지는 [통합 로그에서 찾을 것 (Unified Log Events)](../../../02-artifacts/logs/unified-log-events/index.md)에서 다룹니다.

로그 저장소는 주 저장소인 `/var/db/diagnostics` 와 UUID로 참조하는 `/var/db/uuidtext` 두 곳이고 [1], `log collect` 는 이 저장소를 `.logarchive` 로 묶습니다.

## 절차

1. 로그 수준 설정이 바뀌어 있지 않은지 봅니다. `log config` 는 root 가 필요하고 `--status` 로 현재 설정을, `--mode` 로 설정 바꾸기를, `--reset` 으로 되돌리기를 다룹니다 [1]. 조사 중에는 `--status` 만 쓰고 출력은 수집 기록에 붙입니다.

   ```
   sudo log config --status
   ```

2. 저장소 요약을 떠 둡니다. `log stats` 는 `--overview`, `--per-book`, `--per-file` 로 저장소를 요약하고, `--process` 나 `--predicate` 로 좁힐 수 있습니다 [1].

   ```
   sudo log stats --overview
   ```

3. 로그를 모읍니다. 시스템 전체를 모으려면 root 가 필요하고, 경로를 주지 않으면 현재 폴더에 `system_logs.logarchive` 를 만듭니다 [1]. 조사 대상 디스크를 덜 건드리도록 이 핸드북은 `--output` 으로 수집용 외부 매체를 가리킵니다.

   ```
   sudo log collect --output <수집 매체>/system_logs.logarchive
   ```

4. 범위를 줄여야 할 때만 기간이나 양을 정합니다. `--start` 는 그 시각부터, `--last` 는 최근 기간만(예 `2m`, `3h`), `--size` 는 대략의 데이터 양만 모읍니다 [1]. `--start` 의 형식은 `"YYYY-MM-DD"`, `"YYYY-MM-DD HH:MM:SS"`, `"YYYY-MM-DD HH:MM:SSZZZZZ"` 세 가지이고 [1], 시간대가 헷갈리지 않도록 이 핸드북은 마지막 형식을 씁니다.
5. 만든 아카이브의 해시를 뜨고 수집 시각과 함께 적습니다. 기록 방법은 [라이브 대응 (Live Response)](index.md)에 있습니다.
6. 분석 장비에서 아카이브를 읽습니다. info·debug 수준은 기본으로 꺼져 있어서 `--info`, `--debug` 를 주어야 나오고, `--style` 은 default·compact·json·ndjson·syslog 가운데 고르며, `--timezone` 으로 표시 시간대를 정합니다 [1].

   ```
   log show --archive system_logs.logarchive --info --debug --style ndjson
   log show --archive system_logs.logarchive --predicate 'process == "<프로세스 이름>"'
   ```

## 도구

`log collect` 의 옵션은 아래와 같습니다 [1].

| 옵션 | 하는 일 |
|---|---|
| `--output path` | 저장할 파일 또는 폴더 |
| `--start date/time` | 그 시각부터 |
| `--last num[s\|m\|h\|d]` | 최근 기간만 |
| `--size num [k\|m]` | 대략의 데이터 양 |
| `--device`, `--device-name name`, `--device-udid UDID` | 연결된 기기에서 수집 |
| `--predicate` | NSPredicate 조건식으로 거름 |
| `--directory directory` | 다른 로그 저장소에서 수집. `/var/db/diagnostics` 와 같은 구조여야 함 |

`log show` 와 `log collect` 의 조건식에는 `eventType`, `eventMessage`, `messageType`, `process`, `processImagePath`, `sender`, `senderImagePath`, `subsystem`, `category` 같은 이름을 씁니다 [1]. 공개 수집 도구의 예로 Jamf Aftermath는 `--logs` 에 조건식 파일을 주어 통합 로그를 골라 모읍니다 [2].

## 함정과 한계

`--last`, `--size`, `--start`, `--predicate` 로 범위를 줄이면 그 밖의 기록은 아카이브에 들어가지 않고, 나중에 다른 시간대나 프로세스를 봐야 할 때 되돌릴 수 없습니다. 범위를 줄였다면 준 옵션을 그대로 수집 기록에 적어 둡니다.

로그를 지우는 `log erase` 명령에는 `--all` 과 `--uuidtext` 옵션이 있고 [1], `log config` 로 로그 수준을 바꿀 수도 있습니다 [1]. 이 두 명령을 쓴 뒤 어떤 흔적이 남는지는 공개된 분석 자료가 없으므로, 1단계의 설정 확인과 2단계의 요약을 이런 가능성을 따질 때 비교할 자료로 남깁니다. 지우기를 의심하는 조사 흐름은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에 있습니다.

`log collect` 에 root 말고 [전체 디스크 접근 권한 (Full Disk Access)](full-disk-access.md)이 따로 필요한지는 공개 자료에 나와 있지 않습니다. 같은 macOS 버전의 시험용 맥에서 미리 돌려 보고, 결과 아카이브에 빠진 기간이 없는지 `log stats` 요약과 맞춰 봅니다.

## 결과를 어떻게 해석하나

아카이브는 수집한 순간 저장소에 남아 있던 기록만 담습니다. 이른 시각의 기록이 없거나 중간이 비어 있어도 곧바로 누가 지웠다고 보지 않고, 보관 기간과 로그 수준 때문에 원래 남지 않았을 수 있는지를 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에서 먼저 확인합니다. info·debug 수준 기록이 안 보이면 `log show` 에 `--info`·`--debug` 를 주었는지부터 봅니다 [1].

로그 한 줄은 그 프로세스가 그 시각에 그 문장을 남겼다는 기록이라서, 보고서에는 "이 시각에 이 프로세스가 이런 로그를 남겼다" 까지만 쓰고 사용자가 한 행동은 다른 아티팩트와 맞춰 판단합니다. 표시 시각은 `--timezone` 설정에 따라 달라서, 보고서에 옮길 때는 어떤 시간대로 읽었는지 함께 적고 [타임라인 작성 (Timeline)](../../analysis/timeline/index.md)의 다른 기록과 기준을 맞춥니다.

## 참고 문헌

1. log(1) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/log.1.html
2. Jamf, Aftermath README (GitHub) — https://github.com/jamf/aftermath
