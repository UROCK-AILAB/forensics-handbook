---
title: "보안 도구 기록"
parent: "아티팩트 · 로그"
nav_order: 1800
---

# 보안 도구 기록 (XProtect)

XProtect 는 macOS 에 들어 있는 악성 코드 방어 기능이고, 서명으로 찾는 검사와 감염을 치우는 XProtect Remediator, 행위로 찾는 XProtect Behaviour Service 가 함께 움직이며, 행위 탐지 기록은 SQLite 데이터베이스 `XPdb` 에 남습니다 [1][2][3].

## 무엇을 기록하나 · 왜 생기나

XProtect 는 YARA 시그니처로 악성 코드를 찾고, 알려진 악성 코드를 찾으면 실행을 막고 휴지통으로 옮긴 뒤 Finder 에서 사용자에게 알립니다 [1]. 어떤 시점에 검사하는지와 시그니처 번들의 판을 확인하는 방법은 [악성 코드 흔적 분석 (Malware Triage)](../../03-techniques/analysis/malware-triage/index.md)에서 다루고, 이 페이지는 검사와 치료, 행위 탐지가 시스템에 남기는 흔적을 다룹니다.

서명 검사와 별도로 치료 엔진이 있어, Apple 이 자동으로 보내는 갱신을 바탕으로 이미 들어온 악성 코드를 지우고 그 뒤에도 주기적으로 감염을 검사합니다 [1]. 알려지지 않은 악성 코드를 행위로 찾는 엔진도 있고 [1], 사용자가 동의했다면 실행 파일을, 앱 번들 안의 파일이면 번들 전체를 Apple 에 표본으로 올립니다 [1].

행위 탐지를 맡는 XProtect Behaviour Service(XBS)는 macOS 13 Ventura 에서 들어왔고, 서명 기반 검사를 보완합니다 [3]. XBS 는 Bastion 이라는 규칙에 걸린 행위를 SQLite 데이터베이스 `/var/protected/xprotect/XPdb` 에 기록합니다 [3]. 2024년 6월 기준으로 XBS 는 기록만 하고 막지는 않았고, Apple 에는 보고하지만 사용자에게는 알리지 않았습니다 [3]. 그래서 사용자가 전혀 모르는 탐지가 XPdb 에만 남아 있을 수 있습니다. 그 뒤 판에서 막는 동작이 더해졌을 수 있으니 분석 대상의 판을 함께 봅니다.

## 위치와 버전별 차이

### 구성 요소와 경로

아래 경로는 macOS 26 Tahoe 기준입니다 [2].

| 구성 요소 | 경로 | 출처 |
|---|---|---|
| XProtect 번들(주) | `/var/protected/xprotect/XProtect.bundle` | [2] |
| XProtect 번들(대체) | `/Library/Apple/System/Library/CoreServices/XProtect.bundle` | [2] |
| XProtect Remediator | `/Library/Apple/System/Library/CoreServices/XProtect.app` (안에 `XProtectRemediatorMRTv3` 모듈) | [2] |
| Bastion 규칙 | `XProtect.app` 안의 `bastion.sb`, `BastionMeta.plist` | [2][3] |
| XBS 기록 데이터베이스 | `/var/protected/xprotect/XPdb` | [2][3] |
| Gatekeeper 데이터베이스 | `/private/var/db/gkopaque.bundle/Contents/Resources/gkopaque.db` | [2][4] |
| Gatekeeper 데이터베이스 | `/private/var/db/gke.bundle/Contents/Resources/gk.db`, `gke.auth` | [2] |

`gkopaque.db` 는 Gatekeeper 의 설정(opaque configuration) 데이터베이스입니다 [4]. Gatekeeper 가 실행을 평가한 기록은 [실행 정책 평가 기록 (ExecPolicy·Gatekeeper)](../execution/execpolicy-gatekeeper.md)에서 다룹니다.

### 버전별 차이

| macOS 버전 | 달라진 점 | 출처 |
|---|---|---|
| 13 Ventura | XBS 도입 | [3] |
| 13.5 (2023년 7월 24일) | Bastion 규칙 4개. 2023년 9월에 5개 | [3] |
| XProtect Remediator 137 판 | 12번째 Bastion 규칙이 들어옴 | [3] |
| 15 Sequoia 이후 | XProtect 번들이 두 곳에 있음. 자세한 내용은 [악성 코드 흔적 분석 (Malware Triage)](../../03-techniques/analysis/malware-triage/index.md) | — |
| 26 Tahoe | 주 XProtect 번들을 iCloud 의 CloudKit 연결로도 갱신하도록 바뀜 | [2] |

XProtect Remediator 가 처음 들어온 버전은 공개 자료가 없어, 10.15~12 기기에 Remediator 가 있는지는 실제 기기에서 확인합니다.

### 갱신 주기

| 대상 | 주기 | 받는 경로 | 출처 |
|---|---|---|---|
| XProtect 데이터 (XProtectPlistConfigData) | 거의 매주 | 예전 버전은 Software Update, Tahoe 는 CloudKit 연결로도 받음 | [2] |
| XProtect Remediator | 대개 한 달 안팎 | Software Update 나 그 대체 경로 | [2] |
| Bastion 규칙 | 불규칙 | — | [2] |

수동으로 갱신하는 명령은 `sudo xprotect update` 인데 [2], 조사 중인 맥에서 돌리면 보안 데이터가 바뀌어 사고 당시 상태를 잃으니 수집을 마치기 전에는 돌리지 않습니다.

## 구조

### XPdb

XPdb 는 SQLite 데이터베이스이고 [3], 읽는 방법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)와 같습니다. 표 이름과 열 이름, 시각 값의 형식은 공개 자료가 없으니, 실제 데이터의 스키마를 먼저 뽑아 보고 열의 뜻은 값을 보며 확인합니다.

### Bastion 규칙이 보는 행위

규칙은 `syspolicyd` 가 `bastion.sb` 설정을 써서 적용하고, Spotlight 색인처럼 정상적으로 같은 행위를 하는 프로세스는 예외로 두어 오탐을 막습니다 [3]. 2024년 6월 기준 12개 규칙이 보는 행위를 묶으면 아래와 같고, 표의 이름은 규칙의 정식 이름이 아니라 행위의 종류입니다 [3].

| 묶음 | 보는 행위 |
|---|---|
| 개인 데이터 접근 | 브라우저 데이터 접근, 메시지·Teams·Slack 데이터 접근, 격리(Quarantine) 이벤트 데이터베이스 접근, 정보 탈취형 악성 코드의 접근 시도 |
| 네트워크 | 소켓 ioctl 명령 사용 |
| 권한·설정 변경 | 숨은 권한 도우미(privileged helper), Safari 확장 수정 |
| 숨은 파일과 지속성 | Adload 행위(2개), Application Support 안의 숨은 지속성, Shared 폴더의 숨은 파일과 숨은 실행(2개) |

`BastionMeta.plist` 안의 키는 공개 자료가 없습니다. 규칙 목록은 판마다 늘어났으니 분석 대상의 `bastion.sb` 와 `BastionMeta.plist` 를 함께 수집해 그때 어떤 규칙이 있었는지 확인합니다.

## 증거로서 의미

**증명하는 것.** XPdb 에 기록이 있으면 그 무렵 XBS 규칙에 걸린 행위가 있었다는 뜻이고, 2024년 6월 기준으로는 탐지해도 막지 않았으니 [3] 기록된 행위가 끝까지 실행됐을 수 있습니다. 휴지통에 들어간 파일과 Finder 알림은 XProtect 가 알려진 악성 코드를 막은 흔적일 수 있지만, 이 알림과 휴지통 이동이 어느 로그에 남는지는 공개 자료가 없어 실제 데이터로 확인해야 합니다. 수집한 번들과 규칙 파일은 수집 시점의 XProtect 판을 보여 줍니다.

**증명하지 못하는 것.** XPdb 에 기록이 없다고 악성 행위가 없었다고 말할 수는 없습니다. 규칙이 보는 행위는 정해져 있고 규칙 수도 판마다 다르니, 탐지가 없었다는 것은 그 판의 시그니처와 규칙에 걸린 것이 없었다는 뜻일 뿐입니다. 2024년 6월 기준으로 XBS 는 사용자에게 알리지 않았으니 [3], XPdb 기록만으로 사용자가 탐지를 알았다고 할 수도 없습니다.

보고서에는 "이 시각 무렵 이 프로세스가 브라우저 개인 데이터에 접근하는 행위가 XBS 규칙에 걸려 XPdb 에 기록됐다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

XPdb 의 시각 값이 맥 절대 시각인지 유닉스 시각인지는 공개 자료가 없습니다. 값을 뽑은 뒤 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)의 방법으로 두 해석을 모두 해 보고, 같은 무렵의 통합 로그나 파일 시스템 기록과 맞는 쪽을 택합니다. 어느 쪽을 택했는지와 그 근거는 보고서에 적습니다.

XProtect 판과 갱신 시각은 사고 당시 어떤 규칙이 돌았는지 가르는 기준이 되고, 데이터는 거의 매주, Remediator 는 대개 한 달 안팎으로 바뀌니 [2] 수집 시점의 판이 사고 당시 판과 다를 수 있습니다. 갱신 이력은 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../system-account/os-version-install-history.md)과 [소프트웨어 업데이트 기록 (Software Update)](../system-account/software-update.md)에서 찾습니다.

## 함정과 한계

Tahoe 에서는 Gatekeeper Compatibility Data 를 여전히 내려받아 설치하지만 파일은 어디에도 보이지 않고, 예전 방식의 흔적만 남은 것이라는 해석이 있습니다 [2]. 그래서 설치 기록에는 있는데 파일이 없다고 곧바로 삭제 조작을 의심하지 말고, 원래 그런 동작인지 먼저 따져 봅니다.

Tahoe 는 주 XProtect 번들을 Software Update 말고 iCloud 의 CloudKit 연결로도 갱신하니 [2], 예전처럼 설치 기록에서만 XProtect 갱신을 찾으면 일부를 놓칠 수 있습니다. 설치 로그에 XProtect 갱신이 남는지는 공개 자료가 없어 분석 대상의 [설치 로그 (install.log)](install-log.md)에서 확인합니다.

XProtect Remediator 의 실행 주기와 실행을 맡는 LaunchDaemon 이름, 검사 결과가 남는 통합 로그 카테고리는 공개 자료가 없어 실제 데이터로 확인해야 합니다. 통합 로그에서 XProtect 쪽 메시지를 찾는 조건은 [통합 로그에서 찾을 것 (Unified Log Events)](unified-log-events/index.md)에 있습니다.

XPdb 설명은 2024년 6월 기준이라 [3], 그 뒤 판에서 기록 방식이 바뀌었을 수 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

XPdb 사본을 헥스 편집기로 열어 파일 앞부분이 SQLite 머리글인지 보고, 페이지 크기와 쓰기 앞 로그(WAL) 파일이 옆에 있는지 확인합니다. 머리글 필드의 오프셋과 WAL 을 합치는 방법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에 있습니다.

### 공개 도구로 한 번

1. 이미지에서 `/var/protected/xprotect/` 폴더 전체와 `XProtect.app` 안의 `bastion.sb`, `BastionMeta.plist` 를 복사합니다. XPdb 옆에 같은 이름으로 시작하는 파일이 있으면 함께 복사합니다.
2. 복사본을 SQLite 명령행 도구(예: `sqlite3`)로 열어 `.tables` 와 `.schema` 로 표와 열을 확인합니다.
3. 시각으로 보이는 열을 두 방식으로 바꿔 보고, 같은 무렵의 다른 기록과 맞춰 봅니다.
4. 탐지된 경로가 있으면 그 파일의 격리 속성, 휴지통 기록, 실행 흔적을 이어서 찾습니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 |
|---|---|
| [실행 정책 평가 기록 (ExecPolicy·Gatekeeper)](../execution/execpolicy-gatekeeper.md) | 같은 파일을 Gatekeeper 가 평가한 기록 |
| [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md) | 탐지된 파일이 어디서 왔는지 |
| [휴지통 (.Trash)](../file-folder-usage/trash.md) | XProtect 가 휴지통으로 옮긴 파일 |
| [통합 로그에서 찾을 것 (Unified Log Events)](unified-log-events/index.md) | XProtect 쪽 로그 메시지 |
| [설치 로그 (install.log)](install-log.md) | 보안 데이터 갱신 시기 |
| [실행 에이전트·데몬 (LaunchAgents·LaunchDaemons)](../persistence/launchd/index.md) | 지속성 규칙에 걸린 항목의 실제 설정 |

정보 탈취형 악성 코드를 조사하는 흐름은 [정보 탈취 악성 코드 (Infostealer)](../../04-scenarios/incident/infostealer.md)에, 지속성을 살펴보는 흐름은 [악성 코드 지속성 찾기 (Persistence)](../../04-scenarios/incident/persistence.md)에 있습니다.

## 실습

NIST CFReDS 같은 공개 시험 데이터에서 macOS 13 이후 이미지를 골라 아래 질문을 풀어 봅니다.

1. `/var/protected/xprotect/XPdb` 가 있나요? 있다면 표는 몇 개이고, 시각으로 보이는 열은 어느 방식으로 해석하면 다른 기록과 맞나요?
2. 이미지의 `bastion.sb` 와 `BastionMeta.plist` 를 열어 보면 이 페이지의 12개 규칙 목록 가운데 어떤 행위에 해당하는 내용이 보이나요?
3. XProtect 번들이 두 경로 중 어디에 있나요? 이미지의 macOS 버전과 맞나요?

## 참고 문헌

1. Apple Platform Security Guide, "Protecting against malware in macOS" — https://support.apple.com/guide/security/protecting-against-malware-sec469d47bd8/web
2. Howard Oakley, "Silently updated security data files in Tahoe" (The Eclectic Light Company, 2025-09-19) — https://eclecticlight.co/2025/09/19/silently-updated-security-data-files-in-tahoe/
3. Howard Oakley, "What do XProtect BehaviourService and Bastion rules do?" (The Eclectic Light Company, 2024-06-28) — https://eclecticlight.co/2024/06/28/what-do-xprotect-behaviourservice-and-bastion-rules-do/
4. ForensicArtifacts — artifacts/data/macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
