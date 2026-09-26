---
title: "인쇄 기록"
parent: "아티팩트 · 외부 장치"
nav_order: 1130
---

# 인쇄 기록 (CUPS)

맥의 인쇄 시스템인 CUPS 가 남기는 스풀 폴더의 작업 파일, 보존 설정, 로그를 읽고 누가 어느 앱에서 무엇을 언제 인쇄했는지 재구성하는 법을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

맥에서 인쇄를 요청하면 CUPS 가 인쇄 작업 (print job)을 받아 스풀 폴더에 파일로 쌓아 두고 프린터로 보냅니다. 작업 하나에는 두 종류의 파일이 생기는데, 제어 파일 (control file)에는 작업 이름·요청한 사용자·프린터·앱·시각 같은 속성이 담기고, 데이터 파일 (data file)에는 인쇄한 문서의 사본이 담깁니다 [3]. 인쇄가 끝난 뒤에도 이 파일들이 한동안 남도록 CUPS 설정이 정해져 있어서 [4], 분석가는 인쇄 이력과 때로는 인쇄한 문서 자체까지 되찾을 수 있습니다.

CUPS 는 이와 별도로 접근 로그 (access_log), 오류 로그 (error_log), 페이지 로그 (page_log) 세 가지 로그의 형식을 정해 두고 있습니다 [5]. 스풀 파일이 사라진 뒤에도 로그에 작업 번호·사용자·프린터가 남을 수 있어서, 두 기록을 함께 봅니다.

수집할 때는 스풀 폴더를 따로 챙깁니다. ForensicArtifacts 의 macOS 정의에는 CUPS·스풀·프린터 항목이 없고 [1], Forensics Wiki 의 Mac OS X 10.9 아티팩트 위치 문서에도 인쇄 항목이 없습니다 [2]. 이런 정의 목록만 따라 수집하면 스풀 폴더가 빠질 수 있습니다.

## 위치와 버전별 차이

| 기록 | 위치 | 비고 | 출처 |
|---|---|---|---|
| 스풀 폴더(제어 파일·데이터 파일) | `/private/var/spool/cups` | mac_apt 이 읽는 경로. CUPS 의 `RequestRoot` 기본값도 `/var/spool/cups` | [3][6] |
| CUPS 설정 파일 폴더 | `/private/etc/cups/` (`cupsd.conf`, `cups-files.conf` 등) | CUPS 의 `ServerRoot` 기본값 `/etc/cups`. 프린터 목록 파일 이름(`printers.conf`)은 실제 기기에서 확인 | [6] |
| 로그 | `/private/var/log/cups/` 아래 `access_log`, `error_log`, `page_log` | CUPS 의 `AccessLog`·`ErrorLog`·`PageLog` 기본값. macOS 에 깔린 값은 실제 기기의 `cups-files.conf` 로 확인 | [6] |

mac_apt 의 인쇄 작업 플러그인은 macOS 버전에 따라 다르게 읽지 않습니다 [3]. macOS 10.15 Catalina 이후 스풀 폴더 구조가 버전마다 다른지는 실제 기기로 확인해야 합니다.

로그와 스풀 폴더의 위치는 cupsd.conf 가 아니라 `cups-files.conf` 의 `AccessLog`·`ErrorLog`·`PageLog`·`RequestRoot` 가 정하고, 위 표의 경로는 CUPS 기본값입니다 [6]. 맥에서는 `/etc`·`/var` 가 `/private` 아래를 가리키므로 표의 경로는 `/private` 로 시작합니다. `PageLog` 에 빈 이름을 적으면 page_log 를 만들지 않습니다 [6]. 그래서 분석할 때는 cups-files.conf 부터 열어 로그와 스풀 위치가 기본과 다른지, page_log 가 꺼져 있지 않은지 봅니다.

## 구조

### 스풀 폴더의 작업 파일

스풀 폴더에서 이름이 `c` 로 시작하는 파일이 제어 파일, `d` 로 시작하는 파일이 데이터 파일입니다. mac_apt 은 크기가 0 인 파일은 건너뜁니다 [3]. 데이터 파일 이름의 `d` 뒤부터 `-` 앞까지가 작업 번호라서, 이 번호로 제어 파일과 짝을 짓습니다 [3]. 파일 이름이 제어 파일은 `c00001`, 데이터 파일은 `d00001-001` 처럼 `c`·`d` 뒤에 다섯 자리 작업 번호가 붙는 형식이라는 설명도 있으니, 자릿수는 실제 파일로 확인합니다.

제어 파일에는 인쇄 표준 프로토콜인 IPP (Internet Printing Protocol)의 속성이 담기고, mac_apt 은 그중 아래 속성을 꺼냅니다 [3].

| IPP 속성 | mac_apt 출력 필드 | 뜻 |
|---|---|---|
| `job-name` | Job | 작업 이름 |
| `job-originating-user-name` | Owner | 인쇄를 요청한 사용자 이름 |
| `job-id` | Job ID | 작업 번호 |
| `DestinationPrinterID` | Destination Printer | 보낸 프린터 |
| `com.apple.print.JobInfo.PMApplicationName` | Application | 인쇄를 요청한 앱 이름 |
| `time-at-creation` | Time of Creation | 작업을 만든 시각 |
| `time-at-processing` | Time at Processing | 처리를 시작한 시각 |
| `time-at-completed` | Time of Completion | 처리를 마친 시각 |
| `copies` | Copies | 부수 |
| `document-format` | Document Format | 데이터 파일의 문서 형식 |
| `job-originating-host-name` | Origin Host Name | 작업을 보낸 호스트 이름 |
| `job-state` | State | 작업 상태 |
| `job-media-sheets-completed` | Sheets printed | 인쇄를 마친 용지 수 |
| `job-printer-state-message` | Printer state msg | 프린터 상태 메시지 |
| `job-printer-state-reasons` | Printer state reason | 프린터 상태 이유 |
| `printer-uri` | PrinterURI | 프린터 주소 |
| `job-uuid` | Job UUID | 작업 UUID |

mac_apt 출력에는 이 밖에 데이터 파일 경로를 적는 Cached_File 필드와 읽은 파일을 적는 Source 필드가 있습니다 [3]. `com.apple.print.JobInfo.PMApplicationName` 은 인쇄를 요청한 앱 이름이고 [3], 뜻 칸의 나머지 값은 속성 이름과 출력 필드 이름을 풀어 쓴 것입니다. 제어 파일 안의 바이트 배치는 실제 파일을 헥스로 열어 확인합니다.

### 보존 설정 (cupsd.conf)

인쇄가 끝난 작업 파일을 얼마나 남길지는 cupsd.conf 의 지시어가 정합니다. 기본값은 아래와 같습니다 [4].

| 지시어 | 뜻 | 기본값 |
|---|---|---|
| `PreserveJobFiles` | 인쇄가 끝난 뒤 작업 파일(문서)을 남길지. 숫자면 그 초만큼 남김 | `86400` (1일) |
| `PreserveJobHistory` | 인쇄가 끝난 뒤 작업 이력을 남길지. `Yes` 면 `MaxJobs` 한도에 이를 때까지 남김 | `Yes` |
| `MaxJobs` | 동시에 허용하는 작업 수. 0이면 무제한 | `500` |
| `AutoPurgeJobs` | 할당량에 더 필요 없는 작업 이력을 자동으로 지울지 | `No` |
| `MaxLogSize` | 로그 파일이 이 크기를 넘으면 교체. 0이면 교체 안 함 | `1048576` (1MB) |
| `LogLevel` | error_log 기록 수준 | `warn` |

두 기본값대로라면 문서 사본인 데이터 파일은 인쇄 뒤 약 하루가 지나면 사라지고, 이력인 제어 파일은 작업 수 한도까지 남습니다 [4]. macOS 에 깔린 cupsd.conf 값은 CUPS 기본값과 다를 수 있으니, 분석할 때는 설정 파일부터 열어 이 지시어들이 바뀌어 있는지 봅니다.

### 로그 형식

세 로그의 형식은 아래와 같습니다 [5].

```
access_log : host group user date-time "method resource version" status bytes ipp-operation ipp-status
error_log  : level date-time message
page_log   : printer user job-id date-time total num-sheets job-billing job-originating-host-name job-name media sides
```

## 증거로서 의미

**증명하는 것.** 제어 파일이 남아 있으면 작업 이름, 요청한 계정 이름, 보낸 프린터, 요청한 앱, 작업을 만든·처리한·마친 시각, 부수, 인쇄를 마친 용지 수를 그 파일로 말할 수 있습니다 [3]. 짝이 되는 데이터 파일이 남아 있으면 인쇄한 문서의 사본을 직접 볼 수 있어서, 작업 이름만 보고 짐작하지 않고 내용까지 확인할 수 있습니다 [3]. 스풀 파일이 없어도 page_log 가 남아 있으면 프린터·사용자·작업 번호·시각·매수·작업 이름을 로그로 확인할 수 있습니다 [5].

**증명하지 못하는 것.** `job-originating-user-name` 은 요청한 계정 이름이고, 그 계정을 쓴 사람이 누구인지는 따로 따져야 합니다([그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../04-scenarios/activity/user-attribution.md)). 작업 상태와 인쇄를 마친 용지 수는 인쇄 시스템이 기록한 값이라, 종이가 실제로 나왔는지나 누가 가져갔는지는 이 값으로 알 수 없습니다. 작업 이름이 문서 파일 이름과 같다는 보장은 없고, 데이터 파일이 없으면 무엇을 인쇄했는지는 이름으로만 짐작하게 됩니다.

보고서에는 "이 문서를 인쇄해 가져갔다" 가 아니라 "이 시각에 이 계정이 이 앱에서 이 이름의 작업을 이 프린터로 보냈고, 인쇄 시스템이 몇 장을 마쳤다고 기록했다" 처럼 씁니다.

## 시각 해석

제어 파일의 `time-at-creation`, `time-at-processing`, `time-at-completed` 는 유닉스 시각(1970-01-01 기준 초)입니다 [3]. 유닉스 시각은 시간대와 상관없는 UTC 기준 값이라, 현지 시각으로 보려면 그 맥의 시간대 설정([시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md))을 적용해 바꿉니다. 시각 값을 바꾸는 방식은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

로그의 date-time 은 `[DD/MON/YYYY:HH:MM:SS +ZZZZ]` 형식으로, 사람이 읽는 시각 뒤에 UTC 와의 시간대 차이가 함께 적힙니다 [5]. 타임라인에 넣을 때는 이 차이를 빼서 UTC 로 맞춘 뒤 제어 파일의 시각과 나란히 놓습니다.

## 함정과 한계

기본 설정대로라면 데이터 파일은 약 하루 뒤 사라지고 [4], 로그는 1MB 를 넘으면 교체됩니다 [4]. 인쇄 뒤 시간이 지난 맥에서는 제어 파일이나 로그만 남아 있는 경우를 예상하고, 사라진 데이터 파일은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)로 되찾아 볼 수 있습니다.

`PreserveJobFiles`·`PreserveJobHistory`·`MaxLogSize` 같은 설정은 관리자가 바꿀 수 있어서, 스풀 폴더가 비어 있거나 로그가 짧을 때는 설정 파일부터 봅니다. 기본값과 다르게 바뀌어 있다면 언제 바뀌었는지를 설정 파일의 수정 시각과 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)로 확인하고, 증거를 지우려 한 흔적인지는 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)의 흐름으로 따집니다. 스풀 폴더의 파일만 지우고 로그는 그대로 두었다면 두 기록이 서로 맞지 않게 되어서, 제어 파일과 page_log 의 작업 번호를 맞춰 보면 빠진 작업이 드러날 수 있습니다.

`LogLevel` 은 error_log 의 기록 수준을 정하고 기본값은 `warn` 입니다 [4]. 명세 예시의 `Queued on ... by ...` 줄은 수준이 `I` 인 줄이라 [5], 기본 수준에서 이런 줄이 error_log 에 남는지는 실제 설정과 로그를 보고 확인합니다.

앱 이름으로 사용 이력을 이을 때는 [어떤 앱을 언제 썼나 (App Usage)](../../04-scenarios/activity/app-usage.md)의 기록과 맞춰 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** 스풀 폴더의 제어 파일 하나를 헥스 편집기로 엽니다. 글자 영역에서 `job-name`, `job-originating-user-name`, `com.apple.print.JobInfo.PMApplicationName` 같은 속성 이름을 찾아 그 가까이에 문서 이름·계정 이름·앱 이름이 보이는지 확인합니다. 같은 작업 번호의 데이터 파일은 첫 바이트를 보고, 제어 파일의 `document-format` 값과 맞는 형식인지 비교합니다.

로그 쪽은 CUPS 문서의 예시로 필드를 나눠 봅니다. 아래 두 줄은 명세에 실린 예시이고 실제 기기에서 나온 값이 아닙니다 [5].

```
I [20/May/1999:19:18:28 +0000] [Job 1] Queued on 'DeskJet' by 'mike'.
DeskJet root 1 [20/May/1999:19:21:06 +0000] total 2 acme-123 localhost myjob na_letter_8.5x11in one-sided
```

첫 줄은 error_log 로, 수준 `I`, 시각, 메시지 순서입니다. 둘째 줄은 page_log 로, 형식에 맞춰 나누면 아래와 같습니다.

| 필드 | 값 |
|---|---|
| printer | `DeskJet` |
| user | `root` |
| job-id | `1` |
| date-time | `[20/May/1999:19:21:06 +0000]` |
| total, num-sheets | `total 2` |
| job-billing | `acme-123` |
| job-originating-host-name | `localhost` |
| job-name | `myjob` |
| media | `na_letter_8.5x11in` |
| sides | `one-sided` |

**공개 도구로 한 번.** mac_apt 의 PRINTJOBS 플러그인을 확보한 이미지에 돌리면 스풀 폴더의 제어 파일마다 위 표의 필드가 한 줄씩 나오고, 데이터 파일이 있으면 Cached_File 필드에 그 경로가 적힙니다 [3]. 결과의 Job ID 와 로그의 작업 번호를 맞춰 보고, 제어 파일의 세 시각을 UTC 로 바꾼 로그 시각과 나란히 놓아 봅니다.

## 교차 검증

인쇄한 문서가 어디서 왔는지는 [이 파일은 어디서 왔나 (File Origin)](../../04-scenarios/activity/file-origin.md)로, 인쇄 직전에 그 문서를 열었는지는 [최근 항목 (Shared File Lists)](../file-folder-usage/recent-items/index.md)과 [이 파일을 누가 언제 열었나 (File Access)](../../04-scenarios/activity/file-access.md)로 확인합니다. 데이터 파일 안의 글자를 찾을 때는 [콘텐츠 검색 (Content Search)](../../03-techniques/analysis/content-search.md)을, 인쇄가 자료 유출의 한 경로였는지는 [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md)를 봅니다. 인쇄 시각을 다른 기록과 한 줄로 늘어놓는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)에 있고, 스풀 폴더가 비었을 때 통합 로그에 인쇄 흔적이 있는지는 [통합 로그에서 찾을 것 (Unified Log Events)](../logs/unified-log-events/index.md)에서 찾아봅니다.

## 실습

문서를 몇 장 인쇄해 본 테스트 맥, 또는 공개 시험 자료(NIST CFReDS 등)의 맥 이미지로 아래 질문을 풀어 봅니다.

1. `/private/var/spool/cups` 에 `c`·`d` 로 시작하는 파일이 있는가? 이름에서 작업 번호를 읽을 수 있는가?
2. 제어 파일에서 작업 이름, 요청한 계정, 앱 이름, 세 시각을 찾을 수 있는가? 세 시각을 UTC 와 현지 시각으로 바꾸면 각각 언제인가?
3. 데이터 파일의 형식은 제어 파일의 `document-format` 값과 맞는가?
4. 인쇄하고 하루가 지난 뒤 데이터 파일과 제어 파일 중 무엇이 남아 있는가? 그 맥의 cupsd.conf 에서 `PreserveJobFiles`·`PreserveJobHistory` 값은 무엇인가?
5. 로그 폴더에 page_log 가 있는가? 있다면 제어 파일의 작업 번호와 로그의 job-id 가 맞는가?

## 참고 문헌

1. ForensicArtifacts — artifacts/data/macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
2. Forensics Wiki — Mac OS X 10.9 Artifacts Location — https://forensics.wiki/mac_os_x_10.9_artifacts_location
3. mac_apt (Yogesh Khatri) — plugins/printjobs.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/printjobs.py
4. CUPS — cupsd.conf(5) man page — https://www.cups.org/doc/man-cupsd.conf.html
5. CUPS — cupsd-logs(5) man page — https://www.cups.org/doc/man-cupsd-logs.html
6. CUPS — cups-files.conf(5) man page — https://www.cups.org/doc/man-cups-files.conf.html
