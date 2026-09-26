---
title: "설치 로그"
parent: "아티팩트 · 로그"
nav_order: 1770
---

# 설치 로그 (install.log)

`/private/var/log/install.log` 는 소프트웨어 설치 과정을 적는 로그 파일이고, 무엇을 언제 설치했는지 한 항목씩 남기는 `InstallHistory.plist` 와 짝을 이뤄 설치 시점의 앞뒤 사정을 채워 줍니다 [1].

## 무엇을 기록하나 · 왜 생기나

맥에서 앱 패키지나 운영체제 업데이트를 설치하면 두 군데에 흔적이 남습니다. 설치 결과를 항목 단위로 쌓는 설치 이력 plist 가 하나이고, 설치 과정을 적는 설치 로그가 다른 하나입니다. ForensicArtifacts 정의는 설치 로그를 `MacOSInstallationLogFile`("Software installation log file")로, 설치 이력을 `MacOSInstallationHistoryPlistFile`("Software installation history property list (plist) file")로 따로 등록해 두었습니다 [1].

설치 이력 plist 의 키와 해석은 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../system-account/os-version-install-history.md)이 본문으로 다루고, 이 페이지는 설치 로그 쪽만 다룹니다. 설치 로그에 어떤 프로세스가 무엇을 적는지 설명한 공개 분석 자료는 없어서, 실제 로그를 직접 읽어 확인해야 합니다.

## 위치와 버전별 차이

| 파일 | 경로 | 비고 |
|---|---|---|
| 설치 로그 | `/private/var/log/install.log` (`/var/log/install.log` 와 같은 곳) | ForensicArtifacts `MacOSInstallationLogFile` [1] |
| 설치 이력 | `/Library/Receipts/InstallHistory.plist` | ForensicArtifacts `MacOSInstallationHistoryPlistFile` [1], 본문은 [OS 버전과 설치 기록](../system-account/os-version-install-history.md) |

macOS 10.15 Catalina 이후 버전마다 경로가 같은지 달라졌는지는 공개 자료로 정해지지 않았습니다. 아래 항목도 실제 데이터로 확인해야 합니다.

| 실제 데이터로 확인할 것 | 보는 법 |
|---|---|
| 한 줄의 형식(시각·호스트·프로세스·PID 순서인지) | 파일 앞부분 몇 줄을 읽고 필드 순서를 적어 둡니다 |
| 시각에 시간대 표기가 붙는지 | 시각 뒤에 시차 표기가 있는지 봅니다 |
| 보존 기간과 회전 방식(압축한 옛 파일이 생기는지, 회전 설정이 어디 있는지) | `/private/var/log/` 에 `install.log` 로 시작하는 다른 파일이 있는지 봅니다 |
| XProtect 같은 보안 데이터 갱신도 여기에 남는지 | 보안 데이터 갱신 시기와 같은 시간대의 줄을 찾아봅니다 |
| 같은 내용이 통합 로그에도 남는지 | 같은 시각의 통합 로그 메시지와 맞춰 봅니다 |

## 구조

설치 로그가 어떤 형식으로 적히는지, 줄 단위라면 한 줄에 어떤 필드가 들어가는지 설명한 공개 분석 자료는 없습니다. 분석 대상마다 실제 줄을 읽어 필드 순서와 시각 표기를 확인한 뒤 분석 메모에 적어 둡니다. 확인한 형식은 버전과 함께 적어 두어야 다른 기기와 비교할 때 헷갈리지 않습니다.

## 증거로서 의미

**증명하는 것.** 설치 로그에 어떤 패키지 이름이 적힌 줄이 있으면, 그 시각 무렵 이 맥에서 그 패키지를 설치하는 과정이 돌았다는 기록입니다. 설치 이력 plist 의 한 항목과 같은 시간대의 줄을 찾으면 설치가 한 번 있었다는 사실을 두 기록으로 받칠 수 있습니다.

**증명하지 못하는 것.** 설치 로그는 설치 과정을 적을 뿐이고, 설치한 프로그램이 뒤에 실행됐는지는 설치 로그로 알 수 없습니다. 실행 여부는 [통합 로그의 프로세스 실행 기록 (Process Events)](../execution/unified-log-process.md) 같은 실행 흔적으로 따로 확인합니다. 누가 설치를 시작했는지도 설치 로그만으로 정하지 않고, 그 시각에 로그인한 계정을 다른 기록으로 맞춰 봅니다. 줄이 없다고 설치가 없었다고 단정하지도 않습니다. 보존 기간과 회전 방식이 알려져 있지 않으니, 파일이 덮는 기간부터 먼저 봅니다.

보고서에는 "`install.log` 에 이 시각, 이 패키지 이름이 든 줄이 있고, 같은 시각 `InstallHistory.plist` 에 같은 이름의 항목이 있다" 처럼 두 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

줄마다 붙은 시각이 UTC 인지 현지 시각인지, 시간대 표기가 붙는지는 실제 데이터로 확인해야 합니다. 분석 대상의 시간대 설정을 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)에서 먼저 확인하고, 설치 이력 plist 의 `date` 값과 같은 설치를 맞춰 보며 두 시각이 어떤 차이로 어긋나는지 재어 봅니다. 차이가 시간 단위로 딱 떨어지면 한쪽이 현지 시각일 가능성을 의심하고, 그 판단은 보고서에 분석가의 해석이라고 밝혀 둡니다. plist 날짜 값을 읽는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

## 함정과 한계

- **공개 자료가 적습니다.** 공개 자료로 정해진 것은 경로와 설치 이력 plist 와의 짝뿐입니다 [1]. 줄 형식, 기록하는 프로세스, 보존 기간은 실제 데이터로 확인한 범위만 씁니다.
- **파일 교체와 삭제.** 관리자 권한이 있으면 로그 파일을 고치거나 비울 수 있다고 보고 분석합니다. 파일 시스템 시각과 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)로 파일이 언제 바뀌었는지 함께 봅니다.
- **설치 이력과의 불일치.** 한쪽에만 설치가 보이면 곧바로 조작으로 보지 않습니다. 한쪽의 옛 기록이 이미 지워졌거나, 두 기록이 다루는 설치 종류가 다를 수 있습니다.
- **이미지 복사본의 경로.** `/var/log` 는 `/private/var/log` 를 가리키는 경로라서, 이미지에서는 `private/var/log/` 아래를 찾습니다.

## 직접 분석해 보기

**헥스로 한 번.** 파일 앞부분을 헥스 편집기로 열어 사람이 읽는 문자가 줄바꿈으로 끊겨 이어지는지 확인합니다. 텍스트가 아니라 압축 데이터처럼 보이면 확장자와 달리 압축본일 수 있으니, [압축 형식 (LZFSE·LZ4·zlib)](../../01-foundations/value-decoding/compression.md)을 참고해 형식부터 구분합니다. 첫 줄의 시각 부분을 골라 시차 표기가 있는지 눈으로 봅니다.

**공개 도구로 한 번.** 헥스로 보아 텍스트 파일이면 `grep` 같은 기본 도구로 검색할 수 있습니다.

1. 이미지에서 `private/var/log/install.log` 와 같은 폴더의 비슷한 이름 파일을 모두 꺼냅니다.
2. 설치 이력 plist 에서 확인할 항목의 표시 이름이나 패키지 식별자를 고릅니다.
3. 그 이름으로 설치 로그를 검색해 같은 시간대의 줄을 모읍니다.
4. 줄의 시각과 설치 이력 항목의 `date` 를 나란히 적고, 차이를 기록합니다.

> 그림 자리: 설치 이력 plist 한 항목과, 같은 시간대의 설치 로그 줄을 나란히 놓은 비교 표

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../system-account/os-version-install-history.md) | 같은 설치의 항목과 시각 |
| [소프트웨어 업데이트 기록 (Software Update)](../system-account/software-update.md) | 업데이트 검사·설치 시점 |
| [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) | 설치된 앱이 실제로 남아 있는지 |
| [보안 도구 기록 (XProtect)](xprotect.md) | 보안 데이터 갱신 시기 |
| [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) | 설치로 생긴 파일의 생성 흔적 |

## 실습

NIST CFReDS 처럼 공개된 맥 시험 이미지를 하나 골라 아래 질문을 풀어 봅니다.

1. `install.log` 한 줄의 필드 순서와 시각 표기는 어떻게 되어 있고, 그 이미지의 macOS 버전은 무엇인가?
2. 파일의 첫 줄과 마지막 줄 시각으로 보면 이 로그가 덮는 기간은 어디부터 어디까지인가?
3. 설치 이력 plist 의 항목 하나를 골라, 같은 시간대의 설치 로그 줄을 찾을 수 있는가? 두 시각의 차이는 얼마인가?
4. 설치 이력에는 있는데 설치 로그에는 없는 설치가 있다면, 그 이유로 무엇을 먼저 의심하는가?

## 참고 문헌

1. ForensicArtifacts, artifacts/data/macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
