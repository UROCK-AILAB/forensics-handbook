---
title: "통합 로그 타임라인"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 2050
---

# 통합 로그 타임라인 (Unified Log)

통합 로그(Unified Log)를 로그 아카이브로 모으고 조사할 시간 구간만 기계가 읽기 쉬운 형식으로 뽑아, 파일 시스템 타임라인과 같은 시간 축에 올리는 방법을 다룹니다.

## 언제 쓰나

파일 시각은 무엇이 바뀌었는지는 알려 주지만 어느 프로세스가 무슨 일을 했는지는 알려 주지 않아서, 그 빈자리를 통합 로그로 채웁니다. 통합 로그는 macOS 10.12 Sierra 에서 도입됐고 [2], 항목마다 시각, PID, EUID, 프로세스 경로, 라이브러리 경로, 이벤트 종류, 로그 종류, 서브시스템, 카테고리가 함께 남습니다 [2]. tracev3·uuidtext·timesync 파일이 어떻게 생겼는지는 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md) 에서, 조사에서 찾을 메시지는 [통합 로그에서 찾을 것 (Unified Log Events)](../../../02-artifacts/logs/unified-log-events/index.md) 에서 다루고, 이 페이지는 시각을 믿을 수 있게 뽑아 타임라인에 넣는 절차만 봅니다.

## 로그 시각이 만들어지는 방식

로그 항목에는 실제 시각(wall clock)이 바로 적혀 있지 않습니다. 파이어호스(firehose) 항목의 시각은 청크에 적힌 8바이트 기준 연속 시각에 항목의 6바이트 차이값을 더한 부팅 뒤 카운터(마크 연속 시각)이고, 도구는 이 값을 timesync 파일의 부트 레코드·동기화 레코드에 적힌 실제 시각과 타임베이스로 바꿔 보여 줍니다 [1]. timesync 파일이 없으면 tracev3 헤더에 적힌 실제 시각과 타임베이스로 계산하고 [1], 인텔 맥은 마크 시각이 나노초지만 애플 실리콘 맥은 틱이라서 타임베이스로 나노초로 바꿔야 합니다 [2]. 바꾸는 식과 레코드 오프셋은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md) 에서, 다른 출처와 기준 시점을 맞추는 일은 [시각 정규화 (Time Normalization)](time-normalization.md) 에서 봅니다.

tracev3 만 따로 떼어 오면 시각을 온전히 되살리지 못할 수 있습니다. 그래서 수집할 때 `/private/var/db/diagnostics/` 폴더 전체(`timesync/` 포함)와 `/private/var/db/uuidtext/` 를 함께 가져오거나 로그 아카이브(`.logarchive`)로 한꺼번에 모읍니다 [1].

## 절차

1. **수집 범위와 방법을 정합니다.** 실행 중인 맥이라면 `log collect` 로 로그 아카이브를 만들고, `--output` 에 디렉터리를 주면 그 안에 `system_logs.logarchive` 가 생깁니다 [3]. `--start`·`--last`·`--size` 로 범위를 좁힐 수 있지만 [3], 사고 시각이 확실하지 않으면 범위를 좁히지 않고 모은 뒤 조회할 때 자릅니다. 이미지라면 위 두 폴더를 통째로 복사합니다. 수집 순서는 [라이브 대응 (Live Response)](../../process-acquisition/live-response/index.md) 을 따릅니다.

   ```sh
   log collect --output /분석/수집/
   ```

2. **양을 가늠합니다.** Mandiant 가 관찰한 예로는 Persist 폴더에 약 10.5MB 파일이 약 52개 있고, 10.5MB tracev3 하나에 약 30만~40만 건, 시스템 하나에 1,800만~5,000만 건이 남았습니다 [2]. 고정된 한도가 아니라 관찰값이지만, 전체를 한 번에 사람이 읽을 양은 아니라서 다음 단계에서 시간 구간부터 자릅니다.

3. **시간 구간과 표시 시간대를 정해 뽑습니다.** `log show` 에 `--archive` 로 아카이브를 주고 `--start`·`--end` 로 구간을 자르며, 날짜는 `"YYYY-MM-DD"`, `"YYYY-MM-DD HH:MM:SS"`, `"YYYY-MM-DD HH:MM:SSZZZZZ"` 형식으로 씁니다 [3]. `--timezone` 은 로컬 시간대나 지정한 시간대(tzset(3))로 보여 주는 옵션이고, 주지 않으면 항목이 기록될 당시의 시간대로 보여 줍니다 [3]. 그래서 다른 출처와 합칠 파일은 `--timezone UTC` 로 뽑아 둡니다. 시간대를 붙이지 않은 `--start`·`--end` 값을 어느 시간대로 읽는지는 정해져 있지 않아서, 구간 값에도 `+00:00` 처럼 오프셋을 붙입니다. 기본 출력은 default 수준 메시지만 보여 주고 info·debug 수준은 `--info`·`--debug` 를 줘야 나와서 [3], 타임라인용으로 뽑을 때는 둘 다 붙입니다.

   ```sh
   log show --archive /분석/수집/system_logs.logarchive \
     --start "2024-03-01 09:00:00+00:00" --end "2024-03-01 12:00:00+00:00" \
     --info --debug --timezone UTC --style ndjson > /분석/ul_0900-1200.ndjson
   ```

4. **기계가 읽는 형식으로 저장합니다.** `--style` 값은 `default`, `compact`, `json`, `ndjson`, `syslog` 가 있고, `default` 는 시각을 마이크로초와 시간대 오프셋까지, `compact` 는 밀리초까지 보여 줍니다 [3]. 다른 출처와 합칠 때는 줄마다 항목 하나가 들어가는 `ndjson` 이 다루기 쉽습니다. 명령과 옵션, 사용한 맥의 macOS 버전을 결과 파일 옆에 함께 적어 둡니다.

5. **조건으로 좁힙니다.** `--predicate` 에는 `subsystem`, `category`, `process`, `eventMessage`, `messageType`, `eventType`, `sender` 같은 키를 씁니다 [3]. 예를 들어 소프트웨어 업데이트 기록은 서브시스템 `com.apple.SoftwareUpdateMacController` 로 좁힙니다 [2].

   ```sh
   log show --archive /분석/수집/system_logs.logarchive --info --debug --timezone UTC \
     --predicate 'subsystem == "com.apple.SoftwareUpdateMacController"'
   ```

6. **기준점이 될 사건을 먼저 찍습니다.** 기준점으로 쓰기 좋은 사건에는 로그인 항목 실행(서브시스템 `com.apple.loginwindow.logging`, 메시지 `performAutolaunch`), sudo 실행(프로세스 경로 `/usr/bin/sudo`), DNS 조회(`mDNSResponder`, 서브시스템 `com.apple.mDNSResponder`), 소프트웨어 업데이트가 있습니다 [2]. 이런 사건을 먼저 시간 축에 찍으면 파일 시각이나 FSEvents 순서를 그 사이에 끼워 넣기 쉬워지고, 더 많은 메시지는 [통합 로그에서 찾을 것 (Unified Log Events)](../../../02-artifacts/logs/unified-log-events/index.md) 에서 고릅니다.

7. **파일 시스템 타임라인과 합칩니다.** UTC 로 뽑은 로그 항목을 [파일 시스템 타임라인 (APFS·FSEvents)](filesystem-timeline.md) 의 결과와 한 표에 넣고, 줄마다 어느 출처에서 왔는지 적는 열을 둡니다.

> 그림 자리: 통합 로그의 로그인 항목 실행·sudo 실행 같은 기준점 사이에 APFS 파일 시각이 끼어 들어간 한 시간 구간의 타임라인

## 도구

`log` 명령 말고 공개 파서로는 Mandiant `macos-unifiedlogs`(https://github.com/mandiant/macos-UnifiedLogs)가 있고, 로그 아카이브와 실행 중인 시스템을 읽어 CSV 로 내보냅니다 [2]. 한 가지 도구로 뽑은 시각만 믿지 말고, 같은 구간을 `log show` 와 공개 파서로 한 번씩 뽑아 기준점 몇 개의 시각이 같은지 맞춰 봅니다.

## 함정과 한계

비공개(private) 데이터는 기본으로 가려져서 DNS 기록 같은 곳에서 호스트 이름이 보이지 않을 수 있고, 프로파일을 설치해 가림을 풀어도 그 뒤 기록부터 적용되고 과거 기록은 그대로입니다 [2].

`log show` 가 기본으로 default 수준만 보여 준다는 점을 잊으면 [3] info·debug 항목이 통째로 빠진 타임라인이 되고, 조회 결과가 비어 있다고 그 시간에 아무 일도 없었다고 말할 수 없습니다. macOS 12 Monterey 에서 `/private/var/db/uuidtext/dsc` 파일 형식이 바뀌어서 [2], 다른 버전의 맥에서 수집한 로그를 읽을 때는 도구가 그 형식을 읽는지 먼저 봅니다.

`log erase` 는 선택한 로그 데이터를 지우고, 인자가 없으면 주 로그 저장소와 진행 중(inflight) 로그 데이터를 지웁니다 [3]. 타임라인에서 특정 구간만 기록이 비어 있으면 이런 삭제 가능성도 함께 따지고, 셸 기록과 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md) 의 다른 흔적으로 확인합니다. 이벤트 종류에 `Loss` 가 있지만 [2] 이 종류가 기록 손실 구간을 뜻한다고 단정할 수 없어서, 이 항목만으로 결론을 내리지 않습니다. `log config` 로 로깅 설정을 시스템 전체나 서브시스템 단위로 바꿀 수 있어서 [3], 기대한 메시지가 없으면 설정이 바뀌었는지도 봅니다.

## 결과를 어떻게 해석하나

로그 항목의 시각은 연속 시각을 실제 시각으로 바꾼 값이라서, 보고서에는 어떤 도구로 어느 시간대로 뽑았는지를 함께 적습니다. 로그 한 줄로는 "그 시각에 이 프로세스가 이 메시지를 남겼다" 는 것을 알 수 있고, 그 프로세스를 사람이 직접 실행했는지나 메시지 내용이 실제로 이뤄졌는지는 다른 기록과 맞춰 봐야 합니다.

보고서 문장은 "통합 로그에 2024-03-01 10:15 UTC 무렵 `/usr/bin/sudo` 프로세스가 남긴 항목이 있다" 처럼 기록으로 확인되는 만큼만 쓰고, 누가 명령을 쳤는지는 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md) 의 기록으로 따로 확인합니다.

## 참고 문헌

1. libyal dtformats — Apple Unified Logging and Activity Tracing formats — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
2. Mandiant (Alexander Holcomb), Reviewing macOS Unified Logs (2022-08-31) — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
3. log(1) man 페이지 — https://keith.github.io/xcode-man-pages/log.1.html
