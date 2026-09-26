---
title: "구성 프로파일"
parent: "아티팩트 · 자동 실행·지속성"
nav_order: 640
---

# 구성 프로파일 (Configuration Profiles·MDM)

## 한 줄 요약

구성 프로파일 (Configuration Profile)은 맥의 설정을 묶어서 한꺼번에 적용하는 설정 꾸러미이고, 기기 관리 (Mobile Device Management, MDM) 서버가 밀어 넣거나 사용자가 설치하며, 다른 자동 실행 위치의 허용 규칙까지 바꿀 수 있어서 지속성 조사 때 설치된 프로파일과 MDM 등록 상태를 함께 확인합니다.

## 무엇을 기록하나 · 왜 생기나

회사나 학교가 관리하는 맥에는 MDM이 보낸 프로파일이 들어 있고, 프로파일 안의 페이로드 (Payload)마다 한 가지 설정 영역을 맡습니다. 예를 들어 시스템 확장을 사용자 승인 없이 허용하는 `com.apple.system-extension-policy` 와 로그인 항목·백그라운드 작업 규칙을 거는 `com.apple.servicemanagement` 가 있어서, 프로파일 하나로 다른 자동 실행 위치의 동작이 달라질 수 있습니다. 앞의 페이로드는 [커널·시스템 확장 (KEXT·System Extension)](kext-system-extension.md)에서, 뒤의 페이로드는 [실행 에이전트·데몬 (LaunchAgents·LaunchDaemons)](launchd/index.md) 아래 백그라운드 작업 관리 페이지에서 다룹니다.

구성 프로파일은 macOS 악성 코드가 지속성을 얻는 방법의 하나입니다. 관리 설정은 `/Library/Managed Preferences` 에 놓이고, 설치된 프로파일은 시스템 환경설정(현재 시스템 설정)의 프로파일 화면에서 볼 수 있습니다 [2]. 사고 조사에서는 정상 관리용 프로파일과 출처를 알 수 없는 프로파일을 가려내는 일이 핵심이고, 이 페이지는 그 확인 방법과 해석을 다룹니다.

## 위치와 버전별 차이

### 위치

| 경로·화면 | 설명 | 출처 |
|---|---|---|
| `/Library/Managed Preferences` | 관리 설정이 놓이는 곳 | [2] |
| 시스템 환경설정(현재 시스템 설정)의 프로파일 화면 | 설치된 프로파일 목록 | [1][2] |

설치된 프로파일 자체가 디스크의 어느 폴더에 저장되는지, MDM 등록 여부를 표시하는 파일이 어디 있는지, `/Library/Managed Preferences` 아래가 사용자별로 어떻게 나뉘는지는 실제 데이터로 확인해야 합니다. 공개 아티팩트 정의 모음인 ForensicArtifacts에도 구성 프로파일·MDM 항목이 없어서 [3], 그 정의만 따라 수집하면 이 자료가 빠집니다.

### 버전별 차이

| macOS | 달라진 점 [1] |
|---|---|
| 10.15 이하 | `profiles` 명령으로 구성 프로파일을 설치할 수 있었던 것으로 보임 (11.0부터 막힘) |
| 11.0 이후 (`profiles` 도구 8.0 이상) | 명령줄로 구성 프로파일을 설치할 수 없고, 시스템 설정의 프로파일 화면에서 추가해야 함. "startup profiles" 는 더 이상 지원하지 않음 |

이 변화 때문에 macOS 11 이후 새로 설치된 프로파일은 사용자가 화면에서 승인했거나 MDM이 밀어 넣은 것일 가능성이 큽니다 [1]. 다른 설치 경로가 없다는 자료는 없으므로, 보고서에서는 "이 두 경로 가운데 하나" 를 단정하지 않고 해석으로 적습니다.

## 구조

프로파일은 여러 페이로드를 담는 꾸러미이고, 페이로드마다 종류 식별자(예: `com.apple.system-extension-policy`)와 그 종류에 맞는 키가 들어갑니다. 프로파일 전체에 공통으로 들어가는 키의 이름과 뜻은 이 페이지에서 다루지 않으므로, 개별 페이로드는 해당 페이지의 키 표로 해석하고 모르는 페이로드는 이름과 값을 그대로 적습니다.

조사에서는 어떤 프로파일이 설치돼 있는지, 각 프로파일에 어떤 페이로드가 들어 있는지, 맥이 MDM에 등록돼 있는지를 봅니다. 이 페이지에서 해석할 수 있는 페이로드는 위 두 가지뿐이라서, 모든 페이로드의 종류를 목록으로 적고 관리 주체가 각각을 설명할 수 있는지부터 확인합니다.

## 증거로서 의미

**증명하는 것.** 프로파일 목록에 어떤 프로파일이 있으면 수집한 시점에 그 프로파일이 설치돼 있었다는 뜻이고, 담긴 페이로드로 어떤 설정이 강제되고 있었는지를 말할 수 있습니다. MDM 등록 상태가 확인되면 그 맥이 원격 관리를 받는 상태였다는 뜻이라서, 다른 지속성 위치에서 본 항목을 사용자 행위로 읽기 전에 관리 정책과 먼저 맞춰 봐야 합니다.

**증명하지 못하는 것.** 프로파일이 있다는 사실만으로 누가 설치했는지, 사용자가 내용을 이해하고 승인했는지는 알 수 없습니다. 프로파일이 허용한 확장이나 항목이 실제로 설치돼 돌았다는 뜻도 아닙니다. MDM에 등록돼 있다는 사실이 그 MDM 서버가 조직의 정상 서버라는 뜻도 아니라서, 관리 주체는 조직 쪽 기록과 맞춰야 합니다.

보고서에는 "이 식별자의 프로파일이 설치돼 있었고, 이 종류의 페이로드가 들어 있었다" 처럼 쓰고, 설치 주체는 다른 기록으로 확인한 뒤에 따로 씁니다.

## 시각 해석

프로파일이 언제 설치되고 언제 지워졌는지를 알려 주는 시각 필드는 공개된 분석 자료가 없습니다. 그래서 시기는 `/Library/Managed Preferences` 아래 파일의 파일 시스템 시각과 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)로 좁히고, MDM 관련 통합 로그는 [통합 로그에서 찾을 것 (Unified Log Events)](../logs/unified-log-events/index.md)에서 찾습니다. 프로파일을 설치·제거할 때 남는 로그 문구도 알려진 자료가 없으므로, 찾은 로그를 설치 시각으로 적을 때는 문구의 뜻을 따로 확인합니다.

## 함정과 한계

관리되는 맥에는 정상 프로파일이 여럿 들어 있어서, 프로파일이 있다는 사실만으로 이상하다고 보지 않습니다. 조직의 MDM 관리자에게서 배포한 프로파일 목록을 받아 식별자와 페이로드를 맞추고, 목록에 없는 것만 따로 조사합니다.

macOS 11 이후 명령줄 설치가 막혔다는 내용은 man 페이지 정리본에 나온 것이라서 [1], 버전에 기대는 해석은 조사 대상 맥의 `profiles` 도구 버전과 함께 적습니다.

지우기 쪽에서 보면, `profiles` 명령에는 `remove` 동사가 있어서 [1] 프로파일은 지울 수 있고, 수집 시점에 없다는 사실이 과거에도 없었다는 뜻은 아닙니다. 지난 상태는 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md)로 확인하고, 명령을 친 흔적은 [터미널 명령 기록 (zsh_history·bash_sessions)](../execution/shell-history.md)에서 찾습니다. 라이브 대응 중에 `remove`·`renew`·`sync` 처럼 상태를 바꿀 수 있는 동사는 실행하지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

`/Library/Managed Preferences` 아래 파일을 헥스 편집기로 열어 앞머리로 XML plist인지 바이너리 plist인지, 아니면 다른 형식인지부터 구분합니다. 이 폴더의 파일 형식은 공개된 자료가 없으므로, 형식을 구분한 뒤에 plist라면 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)의 순서대로 읽고, 페이로드 식별자 문자열(예: `com.apple.system-extension-policy`)을 검색해 위치를 잡습니다.

### 공개 도구로 한 번

실행 중인 시스템에서는 macOS 기본 명령 `profiles` 로 확인합니다. 동사는 `help`, `list`, `show`, `remove`, `status`, `sync`, `renew`, `validate`, `version` 이고, 옵션은 `-type`, `-user`, `-all`, `-password`, `-forced`, `-cached`, `-verbose`, `-path`, `-identifier`, `-uuid`, `-output` 이며, `-type` 값은 `configuration`, `provisioning`, `enrollment`(DEP/MDM), `bootstraptoken` 입니다 [1]. 조사에는 아래처럼 읽기만 하는 조합을 씁니다.

```
profiles list
profiles show
profiles status -type enrollment
```

각 조합의 출력 모양은 버전마다 다를 수 있으므로, 출력은 가공하지 말고 그대로 저장해 두고 이미지에서 꺼낸 파일과 맞춰 봅니다. 실행 중인 시스템에서 명령을 칠 때의 원칙은 [라이브 대응 (Live Response)](../../03-techniques/process-acquisition/live-response/index.md)을 따릅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 |
|---|---|
| [커널·시스템 확장 (KEXT·System Extension)](kext-system-extension.md) | 시스템 확장 허용 페이로드의 키와 해석 |
| [실행 에이전트·데몬 (LaunchAgents·LaunchDaemons)](launchd/index.md) | BTM 기록에 남는 MDM 페이로드와 로그인 항목 규칙 |
| [통합 로그에서 찾을 것 (Unified Log Events)](../logs/unified-log-events/index.md) | MDM 관련 기록 |
| [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) | 관리 설정 파일이 바뀐 순서 |

지속성 위치를 한꺼번에 살펴보는 순서는 [악성 코드 지속성 찾기 (Persistence)](../../04-scenarios/incident/persistence.md)에 있습니다.

## 실습

NIST CFReDS 같은 공개 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 이미지의 macOS 버전을 적고, 버전 표에서 명령줄 설치가 가능했던 버전인지 정합니다.
2. `/Library/Managed Preferences` 가 있는지, 있다면 안의 파일 목록과 형식, 파일 시스템 시각을 적습니다.
3. 파일 안에서 페이로드 식별자로 보이는 문자열을 모두 뽑아, 이 핸드북에서 해석할 수 있는 것과 없는 것을 나눕니다.
4. 시스템 확장이나 로그인 항목 규칙이 들어 있다면, 해당 페이지의 기록과 맞춰 실제로 그 규칙에 걸린 항목이 있는지 봅니다.

## 참고 문헌

1. SS64, "profiles" (macOS man 페이지 정리) — https://ss64.com/mac/profiles.html
2. Phil Stokes, "How Malware Persists on macOS" (SentinelOne, 2022-10-27 갱신) — https://www.sentinelone.com/blog/how-malware-persists-on-macos/
3. ForensicArtifacts, artifacts/data/macos.yaml (main 브랜치) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
