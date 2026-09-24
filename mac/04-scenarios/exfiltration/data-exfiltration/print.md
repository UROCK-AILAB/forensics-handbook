---
title: "인쇄로"
parent: "자료를 밖으로 빼돌렸나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 2520
---

# 인쇄로 (Print)

## 조사 질문

이 맥에서 자료를 인쇄해 종이로 들고 나갔는지 묻습니다. macOS 인쇄는 CUPS가 맡고, mac_apt는 CUPS 스풀 폴더에 남은 인쇄 작업을 읽어 프린터로 보낸 파일과 명령 정보를 뽑습니다 [1]. 제어 파일에는 작업 이름·요청한 계정·인쇄한 앱·시각이, 로그에는 작업 번호·사용자·시각이 작업 단위로 남아서, 다른 경로보다 "무엇을 언제 내보냈나"에 가까운 기록을 얻을 수 있습니다. 다만 인쇄한 종이를 누가 가져갔는지는 맥 기록이 말하지 못하는 부분이라, 기록은 인쇄 작업이 있었다는 데까지만 씁니다. 경로마다 공통으로 쓰는 판단 원칙은 [자료를 밖으로 빼돌렸나](index.md) 허브에 있습니다.

스풀 파일의 속성 목록, 보존 설정, 로그 형식은 [인쇄 기록 (CUPS)](../../../02-artifacts/external-devices/cups-printing.md) 페이지에서 다루고, 이 페이지는 그 기록들을 유출 조사에 어떤 순서로 쓰는지만 다룹니다.

## 먼저 확인할 것

OS 버전과 시간대는 [OS 버전과 설치 기록](../../../02-artifacts/system-account/os-version-install-history.md)과 [시간대와 시계 설정](../../../02-artifacts/system-account/time-zone.md)에서 먼저 확인합니다. 인쇄 기록은 시각 기준이 두 가지라서 특히 시간대가 중요합니다. 제어 파일의 `time-at-creation`·`time-at-processing`·`time-at-completed`는 mac_apt가 유닉스 시각으로 읽는 값이고 [1], CUPS 로그는 `[DD/MON/YYYY:HH:MM:SS +ZZZZ]` 형식으로 현지 시각과 시간대를 함께 적습니다 [2]. 두 기록을 대조하기 전에 한 기준으로 바꿔 둡니다([맥의 시각 값](../../../01-foundations/value-decoding/mac-time-values.md)).

스풀 폴더와 로그는 시스템 영역에 있어서 맥 전체에 하나이고, 사용자는 제어 파일의 `job-originating-user-name`과 page_log의 user 칸으로 가립니다 [1][2]. 수집 범위에는 아래 세 곳이 들어 있어야 합니다. 자동 수집 도구가 쓰는 정의에서 인쇄 항목이 빠져 있을 수 있어서(허브의 수집 주의 참고), 수집 목록을 직접 확인합니다.

| 대상 | 경로 | 근거 |
|---|---|---|
| 스풀 폴더 | CUPS 기본 `RequestRoot`는 `/var/spool/cups`이고, mac_apt는 `/private/var/spool/cups`를 읽습니다 | [3][1] |
| 로그 | 기본 `/var/log/cups/access_log`, `/var/log/cups/error_log`, `/var/log/cups/page_log` | [3] |
| 설정 | `/etc/cups/cupsd.conf` | [인쇄 기록](../../../02-artifacts/external-devices/cups-printing.md) |

로그 경로는 설정으로 표준 오류나 syslog로 바꿀 수 있어서 [3], 폴더가 비어 있으면 설정부터 봅니다. 인쇄한 문서 파일과 작업 기록을 얼마 동안 남길지도 cupsd.conf 설정을 따르고, 그 기본값은 [인쇄 기록](../../../02-artifacts/external-devices/cups-printing.md) 페이지에 정리해 두었습니다. 사건에서 시간이 꽤 지났다면 데이터 파일은 이미 사라지고 제어 파일이나 로그만 남아 있을 수 있어서(필자 해석), 확보를 서두릅니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 스풀 폴더의 제어 파일(c#####) | 작업 이름·요청한 계정·프린터·인쇄한 앱·만든/처리한/마친 시각·부수 | [인쇄 기록](../../../02-artifacts/external-devices/cups-printing.md) |
| 2 | 스풀 폴더의 데이터 파일(d#####) | 실제로 인쇄한 내용의 사본 | [인쇄 기록](../../../02-artifacts/external-devices/cups-printing.md) |
| 3 | page_log | 프린터·사용자·작업 번호·시각·매수·작업 이름 | [인쇄 기록](../../../02-artifacts/external-devices/cups-printing.md) |
| 4 | access_log·error_log | 스케줄러에 들어온 요청, 진행과 오류 | [인쇄 기록](../../../02-artifacts/external-devices/cups-printing.md) |
| 5 | 최근 항목·앱 사용 기록 | 인쇄하기 전에 그 문서를 연 흔적 | [최근 항목](../../../02-artifacts/file-folder-usage/recent-items/index.md), [어떤 앱을 언제 썼나](../../activity/app-usage.md) |

mac_apt는 스풀 폴더에서 크기가 0보다 큰 파일만 보고, 데이터 파일 이름의 `d` 뒤 숫자('-' 앞까지)를 작업 번호로 삼아 같은 번호의 제어 파일과 짝을 짓습니다 [1]. 제어 파일은 IPP 요청 형식이고, 인쇄한 앱은 `com.apple.print.JobInfo.PMApplicationName` 속성에 들어 있습니다 [1].

page_log는 로그 형식 문서에서 인쇄한 쪽수를 적는 로그로 설명하지만 [2], 업스트림 CUPS 문서로는 `PageLogFormat`의 기본값이 빈 문자열이고 이 경우 페이지 기록이 꺼집니다 [4]. macOS 기본 설정에서 page_log가 쌓이는지는 확인하지 못해서, 검체마다 파일이 있는지부터 봅니다.

## 분석 흐름

1. 스풀 폴더의 파일 목록을 뽑아 작업 번호마다 제어 파일과 데이터 파일을 짝짓습니다.
2. 제어 파일에서 `job-name`, `job-originating-user-name`, `job-originating-host-name`, `printer-uri`, `com.apple.print.JobInfo.PMApplicationName`, `time-at-*` 값을 뽑아 작업마다 한 줄로 정리합니다.
3. 데이터 파일이 남아 있으면 제어 파일의 `document-format`과 맞는 방식으로 열어, 인쇄한 내용이 대상 문서와 같은지 확인합니다.
4. page_log가 있으면 작업 번호를 1~2단계 목록과 맞춰 봅니다. 로그에는 있는데 스풀 폴더에 없는 작업은 보존 기간이 지났거나 지워진 작업이라, 설정 값과 [증거를 없애려 했나](../../activity/anti-forensics/index.md)의 흐름으로 어느 쪽인지 따집니다.
5. 작업 이름에 문서 이름이 들어 있으면 그 이름으로 원본 파일을 찾고, 인쇄 시각 앞뒤로 그 파일을 연 흔적을 최근 항목과 앱 사용 기록에서 찾습니다.
6. 1~5단계의 시각을 한 [타임라인](../../../03-techniques/analysis/timeline/index.md)에 올려, 문서를 연 흔적과 인쇄 작업이 한 시간대에 이어지는지 봅니다.

1~3단계는 mac_apt가 스풀 파일을 읽는 방식을 따른 것이고 [1], 4~6단계는 필자가 정리한 방법입니다.

## 흔한 오판

- **인쇄 작업 기록만으로 "종이로 가져갔다"고 쓰는 경우.** 인쇄 기록은 작업을 프린터로 보냈다는 사실까지만 말합니다. 출력물을 누가 가져갔는지는 프린터 쪽 기록이나 출입 기록 같은 맥 밖의 자료로 따로 확인합니다.
- **작업 이름을 파일 이름으로 확정하는 경우.** 작업 이름이 언제나 원본 파일 이름과 같은지는 확인하지 못했습니다. 데이터 파일 내용이나 파일 접근 흔적으로 같은 문서인지 확인한 뒤에 파일과 잇습니다.
- **PDF로 저장한 것을 실제 인쇄로 읽는 경우.** PDF로 저장하는 가상 인쇄가 CUPS 작업으로 남는지는 확인하지 못했습니다. 작업이 있다면 `printer-uri`와 `DestinationPrinterID`로 실제 프린터인지 먼저 봅니다.
- **page_log가 없으면 인쇄하지 않았다고 보는 경우.** 페이지 기록이 설정에 따라 꺼져 있을 수 있어서, 로그가 없다는 사실만으로는 아무것도 말하지 못합니다.
- **로그 시각을 UTC로 읽는 경우.** CUPS 로그 시각은 현지 시각이고 시간대가 뒤에 붙어 있어서 [2], 제어 파일의 유닉스 시각과 그대로 견주면 시간대만큼 어긋납니다.

## 보고서 문장 예

> 스풀 폴더의 제어 파일 c○○○○○에 작업 이름 "○○.docx", 요청 계정 "○○", 인쇄한 앱 "○○"이 기록되어 있고, 작업을 마친 시각은 ○○○○년 ○월 ○일 ○시 ○분(UTC)입니다. 같은 작업 번호의 데이터 파일에는 대상 문서와 같은 내용이 들어 있습니다. 이 기록들은 이 계정으로 인쇄 작업을 보낸 사실까지만 보여 주며, 출력물을 누가 가져갔는지는 이 맥의 기록으로 정할 수 없습니다.

## 함께 볼 페이지

- [인쇄 기록 (CUPS)](../../../02-artifacts/external-devices/cups-printing.md) — 스풀 파일 속성, 보존 설정, 로그 형식
- [이 파일을 누가 언제 열었나 (File Access)](../../activity/file-access.md) — 인쇄 전에 문서를 연 흔적
- [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../activity/user-attribution.md) — 요청 계정과 실제 사람을 잇는 방법

## 참고 문헌

1. mac_apt, plugins/printjobs.py (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/printjobs.py
2. CUPS, "cupsd-logs(5)" — https://www.cups.org/doc/man-cupsd-logs.html
3. CUPS, "cups-files.conf(5)" — https://www.cups.org/doc/man-cups-files.conf.html
4. CUPS, "cupsd.conf(5)" — https://www.cups.org/doc/man-cupsd.conf.html
