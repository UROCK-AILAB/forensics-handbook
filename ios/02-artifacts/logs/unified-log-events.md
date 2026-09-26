---
title: "통합 로그에서 찾을 것"
parent: "아티팩트 · 로그"
nav_order: 1090
---

# 통합 로그에서 찾을 것 (Unified Log Events)

통합 로그 (Unified Logs)는 운영체제의 데몬과 앱이 코드에서 남기는 메시지를 한 형식으로 모은 기록이고, 레코드마다 프로세스·subsystem·category·메시지·시각이 붙어 있어서 "그 무렵 어떤 프로세스가 무엇을 적었나" 를 거르고 모아 볼 수 있습니다. 아이폰의 통합 로그는 sysdiagnose 묶음 안의 `system_logs.logarchive` 로 손에 넣습니다.

## 무엇을 기록하나 · 왜 생기나

통합 로그는 macOS 10.12(Sierra, 2016)와 함께 들어왔고 macOS·iOS·watchOS·tvOS 에 모두 있습니다[1]. Apple 기기 전체가 같은 형식을 쓰지만[2], 공개된 분석 자료는 대부분 macOS 기준이라서, 경로·보존 기간 같은 구체값은 macOS 값인지 먼저 따져 보고 읽습니다.

메시지는 개발자가 코드에 넣은 로그 호출에서 나옵니다. 개발자는 기능 영역을 subsystem 으로, 그 안의 부품을 category 로 나누는데, subsystem 은 `com.example.myapp` 같은 역DNS 표기를 씁니다[3]. 운영체제 구성 요소도 같은 방식으로 기록해서, 어느 프로세스가 어떤 기능 영역에서 무엇을 적었는지가 레코드 단위로 남습니다.

### 로그 수준과 디스크에 남는 범위

모든 메시지가 디스크에 남지는 않습니다. 개발자가 고른 로그 수준에 따라 저장 여부가 갈립니다[3].

| 수준 | 디스크 저장 |
|---|---|
| Debug | 디스크에 남지 않습니다[3] |
| Info | 보통 메모리에만 있고, `log` 명령으로 모을 때만 디스크에 씁니다[3] |
| Notice(Default) | 저장 한도 안에서 디스크에 남습니다[3] |
| Error | 저장 한도 안에서 디스크에 남습니다[3] |
| Fault | 저장 한도 안에서 디스크에 남습니다[3] |

기본 설정에서 디스크에 남는 수준은 Default·Error·Fault 뿐입니다[2]. 사후 분석에서 손에 넣는 기록은 대부분 이 세 수준이라고 보고 읽습니다.

### 값 가림

동적 문자열과 복잡한 동적 객체는 기본으로 내용을 가리고, 정수·실수·불린 값은 가리지 않습니다[3]. 개발자는 형식 지정자에 `%{public}` 을 붙여 공개하거나, `%{private}` 로 가리거나, `%{mask.hash}` 로 값 대신 해시만 남기게 할 수 있습니다[3]. 해시만 남은 값은 원래 값을 알 수 없지만, 같은 해시끼리 묶으면 같은 값이 여러 레코드에 나왔는지는 볼 수 있습니다[3].

## 위치와 버전별 차이

### 저장 위치

저장 형식은 두 가지이고, 로그 본문은 `.tracev3` 파일에, 문자열 같은 보조 자료는 `uuidtext` 폴더에 따로 있습니다[2]. 아래 경로는 macOS 기준이고, macOS 에서 `/var` 는 `/private/var` 를 가리키는 링크라서 두 표기는 같은 곳입니다[2].

```
/var/db/diagnostics    (.tracev3)
/var/db/uuidtext       (보조 파일)
```

아이폰 안에서 같은 경로를 쓰는지, `diagnostics` 아래 하위 폴더가 어떻게 나뉘는지는 실제 기기에서 확인해야 합니다. 파일 형식 자체는 [통합 로그 형식](../../01-foundations/data-formats/unified-log.md) 에서 다룹니다.

### 얻는 경로

| 경로 | 내용 |
|---|---|
| sysdiagnose 묶음 | 묶음 안에 `system_logs.logarchive` 폴더가 들어 있습니다[4]. 묶음 안의 다른 로그는 [sysdiagnose 안의 로그](sysdiagnose-logs.md) 에서 다룹니다 |
| `log collect` | 실행 중인 시스템에서 `.logarchive` 를 만들고, 다른 macOS 나 분석 도구로 나중에 읽습니다[2]. macOS 에서 실행하는 방법이고, 아이폰을 Mac 에 연결해 받는 방법은 공개 문서에 나와 있지 않습니다 |
| 로컬 백업 | `.tracev3`·`logarchive`·`uuidtext`·`diagnostics` 경로가 들어 있는지는 실제 백업으로 확인합니다 |

sysdiagnose 묶음을 만들고 여는 법은 [sysdiagnose 묶음](../../01-foundations/backups/sysdiagnose.md), 수집 방식끼리의 차이는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

### 로컬 백업에 보이는 로그 관련 도메인

로컬 백업에는 이름에 로그가 들어간 도메인이 세 개 있습니다. 안에 든 파일과 그 뜻은 알려져 있지 않아서 이름만 적습니다.

| 도메인 | 항목 수 |
|---|---|
| `SysSharedContainerDomain-systemgroup.com.apple.logd_helper.FTABHarvest` | 3 |
| `AppDomain-com.apple.EnhancedLogging` | 4 |
| `AppDomainPlugin-com.apple.EnhancedLogging.FollowUpExtension` | 4 |

백업 도메인 구조는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.

### 버전과 보존 기간

| 항목 | 내용 |
|---|---|
| 도입 | macOS 10.12(2016)부터이고 iOS 에도 있습니다[1] |
| 보존 기간과 양 | macOS 기준으로 약 28~30일, 레코드 3천만~5천만 건, logarchive 로 400~800MB(평문으로 풀면 2~9GB)입니다[2]. 아이폰의 보존 기간은 알려져 있지 않습니다 |
| 아이폰에서 찾을 이벤트 | 잠금 해제·앱 실행·네트워크 같은 iOS 이벤트와 그 subsystem 이름은 공개된 목록이 없습니다 |

마지막 줄 때문에 이 페이지는 "이 이벤트는 이 predicate 로 찾는다" 는 목록을 싣지 않고, 아래 "찾는 방법" 에서 다른 아티팩트가 가리킨 프로세스와 시각에서 출발해 통합 로그로 좁혀 가는 방식을 설명합니다.

## 구조

레코드 하나에서 뽑을 수 있는 필드는 다음과 같습니다[1]. 필드 이름은 Mandiant 의 공개 파서 macos-UnifiedLogs 기준입니다.

| 필드 | 알 수 있는 것 |
|---|---|
| 프로세스 ID, 스레드 ID | 기록한 프로세스와 스레드 |
| 활동(Activity) ID, 부모 활동 ID | 같은 작업 흐름에 속한 레코드를 묶는 번호 |
| 메시지 | 개발자가 남긴 글과 값(가린 값 포함) |
| 시각 | 레코드 시각. 파서는 Intel 과 ARM 방식을 따로 처리합니다[1] |
| EUID | 유효 사용자 ID |
| 로그 종류, 이벤트 종류 | 로그 수준과 이벤트 분류 |
| 라이브러리, 프로세스 | 기록 호출이 나온 라이브러리와 실행 파일 |
| subsystem, category | 기능 영역과 그 안의 부품 |
| UUID 여러 개 | 라이브러리·프로세스·부팅을 가리키는 UUID |

부팅 UUID 가 필드에 들어 있어서, 같은 부팅 안의 레코드끼리 묶어 재부팅 전후를 나눠 볼 수 있습니다. `.tracev3` 의 블록 구조와 `uuidtext` 로 문자열을 되찾는 과정은 [통합 로그 형식](../../01-foundations/data-formats/unified-log.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

통합 로그 레코드는 그 시각에 그 프로세스가 그 subsystem·category 로 그 메시지를 적었다는 사실을 보여 줍니다. 프로세스 ID·실행 파일·부팅 UUID 가 함께 남아서, 다른 아티팩트가 가리킨 프로세스 이름이 그 부팅 안에서 실제로 돌았는지 확인하는 데 쓸 수 있습니다. 해시로 가린 값도 같은 해시가 여러 번 나왔는지는 보여 줍니다[3].

### 증명하지 못하는 것

Debug 는 디스크에 남지 않고 Info 도 보통 남지 않아서[3], 기록이 없다고 그 일이 없었다고 말할 수 없습니다. 메시지 문구는 개발자가 코드에 넣은 글이라서[3], 메시지가 사용자의 어떤 조작에 대응하는지는 따로 검증해야 합니다. 가린 문자열은 내용을 알려 주지 않습니다. 저장 한도를 넘으면 오래된 기록이 빠질 수 있어서[3], 보존 기간보다 앞선 시점에 대해서는 아무것도 말하지 못합니다.

보고서에는 "사용자가 앱을 열었다" 가 아니라 "이 시각에 이 프로세스가 이 subsystem 으로 이런 메시지를 남긴 기록이 있다" 처럼 레코드로 확인되는 만큼만 씁니다.

## 시각 해석

레코드마다 시각이 있고 공개 파서는 이를 실제 시각(wall clock)으로 바꿔 보여 줍니다. 파서는 Intel 과 ARM 기기의 시각을 따로 처리하고[1], 통합 로그가 시각을 어떤 기준으로 적고 어떻게 실제 시각으로 환산하는지는 알려져 있지 않습니다. 그래서 도구가 출력한 시각을 그대로 옮기기 전에 도구가 UTC 로 찍었는지 분석 PC 의 현지 시각으로 찍었는지 확인하고, 기기의 시간대 설정과 맞춰 봅니다. 시각 값 종류는 [시각 값](../../01-foundations/value-decoding/time-values.md), 기기 시간대는 [시간대와 시각 설정](../system-account/time-zone.md) 에서 다룹니다.

## 함정과 한계

- **macOS 값을 그대로 옮기는 실수.** 경로와 보존 기간(약 28~30일)은 macOS 값이고[2], 아이폰 값은 알려져 있지 않습니다.
- **수준에 따라 빠지는 기록.** 사후 분석에 쓰는 기록은 대부분 Default·Error·Fault 이고[2][3], 상세한 동작은 Debug·Info 에 있는 경우가 많아 비어 보일 수 있습니다.
- **가린 값.** 문자열 인자는 기본으로 가려져서[3] 파일 이름·주소 같은 값이 메시지에 없을 수 있습니다.
- **파서 한계.** macos-UnifiedLogs 는 printf 의 `%m` 같은 오류 코드를 사람이 읽는 글로 바꾸지 않고, 지원하지 않는 사용자 정의 객체는 base64 문자열로 남깁니다[1]. 도구마다 출력이 다를 수 있어서, 결론에 쓰는 레코드는 다른 도구로 한 번 더 확인합니다.
- **획득 시점.** sysdiagnose 는 만든 순간까지의 기록을 담고, 사용자가 만들어야 생깁니다. 사고 뒤 오래 지나 만들면 저장 한도 때문에 관심 시점 기록이 이미 빠졌을 수 있습니다.

## 찾는 방법

아이폰용 이벤트 목록은 공개된 것이 없어서, 통합 로그는 다른 아티팩트에서 이미 좁힌 단서를 확인하고 앞뒤 맥락을 넓히는 데 씁니다. 순서는 다음과 같습니다.

1. 다른 아티팩트에서 관심 프로세스 이름과 시간대를 정합니다. 예를 들어 [sysdiagnose 안의 로그](sysdiagnose-logs.md) 의 Shutdown.log 가 가리킨 프로세스 경로, [충돌·진단 기록](../app-usage/diagnostics.md) 의 충돌 프로세스, [전원 로그](../app-usage/powerlog.md) 의 앱 실행 시간대가 출발점이 됩니다.
2. 그 프로세스 이름으로 레코드를 거르고, 첫 기록과 마지막 기록 시각, 부팅 UUID 를 적습니다.
3. 그 시각 앞뒤 몇 분으로 넓혀 프로세스 조건 없이 다시 보고, 같은 활동 ID 로 묶인 레코드를 따라갑니다.
4. 메시지 안의 낱말로 한 번 더 걸러, 다른 프로세스가 같은 대상을 언급했는지 봅니다.
5. 찾은 레코드는 원본 logarchive 경로·도구 이름과 버전·거른 조건을 함께 기록합니다.

## 직접 분석해 보기

### 헥스로

`.tracev3` 는 블록 단위 형식이고 문자열을 `uuidtext` 에서 되찾아야 해서, 헥스 편집기로 메시지 한 줄을 끝까지 읽으려면 형식 명세가 필요합니다. 이 페이지에는 헥스 예시를 싣지 않고, 헤더와 블록을 따라가는 과정은 [통합 로그 형식](../../01-foundations/data-formats/unified-log.md) 에서 다룹니다.

### 공개 도구로

Mac 에서는 Apple 의 `log show` 로 logarchive 를 읽습니다. 예는 다음과 같고, 수준별 레코드를 모두 보이게 한 뒤 메시지 낱말로 거릅니다[2].

```
log show <파일>.logarchive --info --backtrace --debug --loss --signpost --style syslog --force --predicate 'eventMessage CONTAINS "remote"'
```

predicate 에 `process == "..."` 를 쓰면 프로세스별로 거를 수 있습니다[2]. 흔히 드는 예시 프로세스(sudo·sshd·screensharingd)는 macOS 것이라서 아이폰 분석에서는 1단계에서 정한 프로세스 이름을 넣습니다.

Mac 이 없으면 Mandiant 의 macos-UnifiedLogs(Rust)로 logarchive 를 읽습니다[1]. EC-DIGIT-CSIRC 의 sysdiagnose 분석 도구도 macOS 에서는 Apple `log` 를, Linux 에서는 macos-UnifiedLogs 를 써서 묶음 안의 통합 로그를 읽습니다[4]. 두 도구로 같은 레코드를 뽑아 시각과 메시지가 같게 나오는지 비교하면 도구 검증을 겸할 수 있고, 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [sysdiagnose 안의 로그](sysdiagnose-logs.md) | Shutdown.log 의 재부팅 시각·프로세스 경로와 같은 부팅의 통합 로그 레코드 |
| [충돌·진단 기록](../app-usage/diagnostics.md) | 충돌 시각 앞뒤에 그 프로세스가 남긴 메시지 |
| [전원 로그](../app-usage/powerlog.md) | 앱이 돌았던 시간대와 그 앱 프로세스의 레코드 |
| [KnowledgeC](../app-usage/knowledgec/index.md), [바이옴](../app-usage/biome/index.md) | 앱 사용 기록의 시각과 통합 로그 레코드의 시각 차이 |
| [와이파이 기록](../network/wifi.md) | 네트워크 연결 시각과 관련 프로세스 레코드 |

여러 아티팩트를 한 시간 축에 놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md), 감염 의심 기기에서 쓰는 순서는 [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md) 에서 다룹니다.

## 실습

sysdiagnose 가 들어 있는 공개 시험 이미지를 구했다면 다음 질문으로 풀어 봅니다. 이미지에 따라 sysdiagnose 가 없을 수 있어서, 먼저 묶음이 있는지부터 확인합니다.

1. `system_logs.logarchive` 에서 가장 오래된 레코드와 가장 최근 레코드의 시각은 언제이고, 그 차이로 보아 이 기기에서 기록이 며칠치 남았습니까?
2. 레코드에 나오는 부팅 UUID 는 몇 개이고, 각 부팅이 시작된 무렵의 시각은 언제입니까?
3. 같은 logarchive 를 `log show` 와 macos-UnifiedLogs 로 읽었을 때 레코드 수와 시각 표기가 같습니까? 다르다면 무엇 때문입니까?
4. 해시로 가린 값 가운데 여러 레코드에 되풀이해 나오는 값이 있습니까? 그 레코드들은 어떤 프로세스가 남겼습니까?

## 참고 문헌

1. Mandiant, macos-UnifiedLogs (GitHub README) — https://github.com/mandiant/macos-UnifiedLogs
2. CrowdStrike, "How to Leverage Apple Unified Log for Incident Response" — https://www.crowdstrike.com/en-us/blog/how-to-leverage-apple-unified-log-for-incident-response/
3. Apple Developer Documentation, "Generating Log Messages from Your Code" — https://developer.apple.com/tutorials/data/documentation/os/generating-log-messages-from-your-code.json
4. EC-DIGIT-CSIRC, sysdiagnose (GitHub README) — https://github.com/EC-DIGIT-CSIRC/sysdiagnose
