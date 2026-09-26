---
title: "통합 로그 형식"
parent: "기반 · 데이터 저장 형식"
nav_order: 220
has_children: true
has_toc: false
---

# 통합 로그 형식 (Unified Log)

통합 로그(Unified Log)는 macOS 10.12 Sierra부터 시스템과 앱의 로그를 텍스트 파일 대신 바이너리 파일로 모아 두는 형식이고, 로그 항목(tracev3)과 문장 틀(uuidtext·dsc), 시각 기준(timesync)이 서로 다른 파일에 나뉘어 있어서 세 가지를 함께 모아야 읽을 수 있습니다.

## 왜 중요한가

통합 로그는 macOS 10.12 Sierra(2016)에서 처음 나와 그 전의 Apple System Log(ASL)를 대신했고 [2][3], iOS 10·tvOS 10·watchOS 3 이후에서도 쓸 수 있습니다 [1]. 로그 데이터를 텍스트 로그 파일에 쓰지 않고 메모리와 디스크에 모아 두며, 사람은 Console 앱이나 `log` 명령, Xcode 디버그 콘솔로 봅니다 [1]. 10.12 이전의 로그 형식은 [예전 시스템 로그 (ASL·syslog)](../asl-syslog.md)에서 다룹니다.

시스템 곳곳의 프로세스가 한 저장소에 로그를 남겨서 여러 프로세스의 흔적을 한곳에서 찾을 수 있습니다. 대신 파일이 바이너리이고 문장이 따로 저장되며 시각도 변환해야 해서, 형식을 모르고 도구 결과만 보면 빠진 문장이나 틀어진 시각을 알아채기 어렵습니다. 이 허브의 하위 페이지는 파일이 어떻게 생겼고 무엇이 얼마나 남는지를 다루고, 조사에서 찾을 메시지는 [통합 로그에서 찾을 것 (Unified Log Events)](../../../02-artifacts/logs/unified-log-events/index.md)에서 다룹니다.

## 한눈에 보기

| 구성 | 위치 | macOS 버전 | 알려 주는 것 |
|---|---|---|---|
| tracev3 | `/private/var/db/diagnostics/` 아래 `Persist`·`Special`·`Signpost`·`HighVolume` | 10.12부터. SimpleDump 청크는 12부터 | 어느 프로세스가 언제 어떤 수준의 로그를 남겼는지 |
| timesync | `/private/var/db/diagnostics/timesync/` | 10.12부터 | 로그의 연속 시각을 실제 시각(wall clock)으로 바꾸는 기준, 부팅 구간 |
| uuidtext | `/private/var/db/uuidtext/` 아래 `00`~`FF` | 10.12부터 | 형식 문자열과 그 문자열이 나온 실행 파일 경로 |
| dsc | `/private/var/db/uuidtext/dsc/` | 11까지 v1, 12부터 v2 | 시스템 라이브러리의 형식 문자열 |
| 로깅 설정 | `/Library/Preferences/Logging/Subsystems/` | 10.12부터(구성 프로필 페이로드 기준) | 기본보다 더 많이 기록하게 바꿨는지 |
| 로그 아카이브 | `log collect` 로 만든 `.logarchive` | 프로그램으로 읽는 `OSLogStore` 는 10.15부터 | 수집 시점의 디스크 로그와 메모리 속 로그 |

`/var` 는 `/private/var` 를 가리키는 심볼릭 링크라서 `/var/db/diagnostics/` 와 `/var/db/uuidtext/` 로 적어도 같은 곳입니다 [3]. `/private/var/db/diagnostics/` 에는 tracev3 폴더 말고도 `logdata.statistics.[0-9].txt`, `logd.[0-9].log`, `shutdown.log`, `version.plist` 파일이 있고 [4], 이 파일들의 내용은 이 허브에서 다루지 않습니다.

> 그림 자리: tracev3 항목의 형식 문자열 참조가 uuidtext·dsc 파일로, 연속 시각이 timesync 파일로 이어져 로그 한 줄이 완성되는 흐름

## 읽는 순서

1. [tracev3 파일 구조 (tracev3)](tracev3.md) — 청크 구조와 Firehose 항목, timesync로 시각을 바꾸는 식을 봅니다.
2. [UUID 텍스트와 공유 캐시 (uuidtext·dsc)](uuidtext-dsc.md) — 형식 문자열이 든 두 파일의 구조와, 이 파일이 빠지면 무엇이 안 풀리는지를 봅니다.
3. [보관 기간과 로그 수준 (Persist·Info·Debug)](retention-levels.md) — 수준마다 디스크에 남는지, 용량 한도와 로깅 설정을 바꾼 흔적, 비공개 값을 봅니다.
4. [로그 아카이브 만들고 읽기 (logarchive)](logarchive.md) — `log collect` 로 모으고 `log show`·`OSLogStore`·공개 파서로 읽는 법을 봅니다.

## 함께 볼 페이지

- [통합 로그의 프로세스 실행 기록 (Process Events)](../../../02-artifacts/execution/unified-log-process.md)
- [예전 시스템 로그 (ASL·syslog)](../asl-syslog.md)
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../value-decoding/mac-time-values.md)
- [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md)
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)
- [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)

## 참고 문헌

1. Apple Developer, Logging (os) — https://developer.apple.com/tutorials/data/documentation/os/logging.json
2. Mandiant macos-UnifiedLogs README — https://raw.githubusercontent.com/mandiant/macos-UnifiedLogs/main/README.md
3. Alexander Holcomb (Mandiant), Reviewing macOS Unified Logs (Google Cloud 블로그, 2022-08-31) — https://cloud.google.com/blog/topics/threat-intelligence/reviewing-macos-unified-logs
4. libyal dtformats — Apple Unified Logging and Activity Tracing formats (GitHub 보기) — https://github.com/libyal/dtformats/blob/main/documentation/Apple%20Unified%20Logging%20and%20Activity%20Tracing%20formats.asciidoc
