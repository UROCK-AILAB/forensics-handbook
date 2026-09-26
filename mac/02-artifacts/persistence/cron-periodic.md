---
title: "예약 작업"
parent: "아티팩트 · 자동 실행·지속성"
nav_order: 610
---

# 예약 작업 (cron·periodic)

크론 (cron)·앳 (at)·주기 작업 (periodic)은 정해 둔 시각이나 주기에 명령을 돌리는 유닉스 계열의 예약 실행 장치이고, 악성 코드가 지속성 수단으로 쓴 사례가 있어서 설정 파일과 작업 파일을 따로 확인합니다.

## 무엇을 기록하나 · 왜 생기나

세 장치 모두 "무엇을 언제 돌릴지" 를 디스크의 파일에 적어 두는 방식입니다. cron은 crontab 파일에 실행 주기와 명령을 적어 두고 되풀이해서 돌리고, at은 한 번 돌릴 작업을 작업 파일로 남기며, periodic은 일·주·월 단위로 돌릴 스크립트를 폴더에 모아 두고 설정 파일로 조절합니다. AdLoad와 Mughthesec 같은 macOS 악성 코드가 cron을 지속성 수단으로 썼고, at 작업과 periodic 스크립트도 지속성 위치로 쓰입니다 [1]. 윈도우의 작업 스케줄러에 견줄 만한 자리입니다.

파일에 남는 것은 예약 설정이고, 실제로 돌았는지는 이 파일에 남지 않습니다. 이 페이지는 설정이 남는 자리와 그 읽는 법을 다루고, macOS의 주된 자동 실행 장치인 launchd는 [실행 에이전트·데몬 (LaunchAgents·LaunchDaemons)](launchd/index.md)에서 다룹니다.

## 위치와 버전별 차이

### cron

| 경로 | 설명 | 출처 |
|---|---|---|
| `/etc/crontab`, `/private/etc/crontab` | 시스템 crontab | [2] |
| `/usr/lib/cron/tabs/*` | crontab 파일 폴더 | [2] |
| `/private/var/at/tabs/*`, `/var/at/tabs/*` | crontab 파일 폴더 | [2] |
| `/private/var/cron/tabs/*`, `/var/cron/tabs/*` | crontab 파일 폴더 | [2] |

같은 파일이 `/etc/...` 와 `/private/etc/...` 두 형태로 쓰이므로 [2], 이미지에서 어느 경로가 실제 파일이고 어느 경로가 심볼릭 링크인지 확인합니다. 폴더 안 crontab 파일 이름만으로 계정을 단정하지 말고, 파일마다 소유자를 함께 적어 어느 계정의 작업인지 판별합니다.

### at

| 경로 | 출처 |
|---|---|
| `/usr/lib/cron/jobs/*` | [2] |
| `/var/at/jobs` | [1] |

at 작업 파일은 이름이 글자 "a" 로 시작하고 16진수처럼 보이는 문자열이 뒤따릅니다 [1].

### periodic

| 경로 | 설명 | 출처 |
|---|---|---|
| `/etc/periodic/` 아래 `daily`·`weekly`·`monthly` | 주기별 스크립트 폴더 | [1][2] |
| `/etc/defaults/periodic.conf` | 기본 설정 | [1][2] |
| `/etc/periodic.conf` | 설정 | [1][2] |
| `/etc/periodic.conf.local` | 설정 | [2] |
| `/etc/daily.local/*`, `/etc/weekly.local/*`, `/etc/monthly.local/*` | 로컬 추가 스크립트 | [2] |
| `/usr/local/etc/periodic/**` | 추가 스크립트 | [2] |

위 `/etc/...` 경로마다 `/private/etc/...` 형태도 있고, `daily.local` 등은 폴더(`/*`)로 정의돼 있습니다 [2]. 이 이름이 파일일 수도 있으므로 이미지에서는 파일과 폴더 두 경우를 모두 찾습니다. periodic 항목의 참고 자료로 FreeBSD 문서가 걸려 있어 [2], macOS의 periodic은 FreeBSD 계열로 보입니다.

### 버전별 차이

경로마다 쓰이는 macOS 버전과 macOS 10.15 이후 버전 사이의 차이는 실제 데이터로 확인해야 합니다. cron을 띄우는 launchd 작업이 무엇인지, crontab이 있을 때만 cron이 도는지, cron이 작업을 돌리려면 전체 디스크 접근 권한이 필요한지, at 작업을 돌리는 장치가 기본으로 꺼져 있는지, periodic을 부르는 launchd 작업과 실행 시각도 조사 대상 버전에서 따로 확인합니다. 그래서 파일이 있다는 사실과 그 파일이 조사 대상 버전에서 실행되는 설정이라는 사실을 따로 놓고 봅니다.

## 구조

crontab은 한 줄에 실행 주기와 실행할 명령을 적는 텍스트 파일이고, 조사에서는 명령 부분이 무엇을 부르는지(스크립트 경로, 내려받기 명령, 숨김 폴더의 실행 파일)를 봅니다. 주기 필드를 해석해 보고서에 적을 때는 cron 문서에서 필드 읽는 법을 확인합니다.

periodic 스크립트 폴더에는 원래 들어 있는 스크립트가 있을 수 있어서, 파일 이름만 보고 이상 여부를 판별하기 어렵습니다. 같은 macOS 버전의 깨끗한 설치본과 목록·내용을 맞춰 보고, 설정 파일은 기본 설정(`/etc/defaults/periodic.conf`)과 덮어쓰는 설정(`/etc/periodic.conf`, `/etc/periodic.conf.local`)을 나눠서 비교합니다.

at 작업 파일의 내부 구조와 파일 이름에 들어 있는 16진수 부분의 뜻은 실제 데이터로 확인해야 합니다.

## 증거로서 의미

**증명하는 것.** crontab이나 at 작업 파일, periodic 스크립트가 있으면 수집한 시점에 그 명령을 예약해 둔 설정이 디스크에 있었다는 뜻이고, 적힌 명령과 그 명령이 부르는 파일 경로를 말할 수 있습니다. 파일의 소유자로 어느 계정의 작업인지도 좁힐 수 있습니다.

**증명하지 못하는 것.** 설정이 있다는 사실은 명령이 실제로 돌았다는 뜻이 아니고, 위에서 적은 대로 cron·at·periodic이 조사 대상 버전에서 켜져 있는지도 이 파일로는 알 수 없습니다. 누가 설정을 넣었는지도 파일만으로는 판별할 수 없습니다.

보고서에는 "이 경로의 crontab에 이 명령을 되풀이해 돌리는 줄이 있었다" 처럼 쓰고, 실행 여부는 실행 흔적과 맞춘 뒤에 따로 씁니다.

## 시각 해석

설정이 들어간 시기는 파일 시스템 시각과 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)로 좁히고, crontab 안의 주기 필드는 "언제 돌도록 예약됐나" 를 알려 줄 뿐 "언제 적었나" 를 알려 주지 않는다는 점을 나눠서 씁니다. periodic 실행 결과가 로그 파일로 남는지는 실제 데이터로 확인합니다.

## 함정과 한계

경로가 여러 형태로 적혀 있어서, 한 형태만 검색하면 심볼릭 링크 때문에 같은 파일을 두 번 세거나 반대로 놓칠 수 있습니다. 이미지에서는 실제 파일의 경로를 한 번 정해 두고 같은 파일인지 확인한 뒤 세어야 합니다.

periodic 폴더와 설정 파일에는 원래 들어 있는 내용이 있어서, 기준본 없이 보면 정상 스크립트를 악성으로 잘못 보거나 기존 스크립트 안에 한 줄 끼워 넣은 변경을 놓칠 수 있습니다. 파일 목록뿐만 아니라 내용까지 기준본과 비교합니다.

지우기 쪽에서 보면, 예약 파일은 수집한 시점의 상태만 보여 주기 때문에 crontab이 없다는 사실이 과거에도 없었다는 뜻은 아닙니다. 지난 상태는 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md)로 확인하고, crontab을 고친 명령을 친 흔적은 [터미널 명령 기록 (zsh_history·bash_sessions)](../execution/shell-history.md)에서 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

crontab과 periodic 설정은 텍스트라서 헥스로 볼 일이 적지만, 한 번은 헥스 편집기로 열어 줄바꿈 문자와 보이지 않는 문자를 확인합니다. 텍스트 편집기에서 보이지 않는 제어 문자나 아주 긴 공백 뒤에 붙은 명령은 헥스로 보면 드러납니다. at 작업 파일도 먼저 헥스로 열어 텍스트인지 아닌지부터 구분합니다. 이 설명은 일반적인 방법이고 특정 기기에서 나온 값이 아닙니다.

### 공개 도구로 한 번

ForensicArtifacts 정의 파일 [2]은 공개 아티팩트 정의 모음이라서, 수집 목록을 짤 때 위 경로를 그대로 옮겨 빠짐없이 챙길 수 있습니다. 가져온 파일은 아래 순서로 봅니다.

1. cron·at·periodic 경로마다 파일이 있는지, 있다면 소유자·권한·파일 시스템 시각을 적습니다.
2. crontab과 at 작업 파일에서 명령 부분을 뽑아, 부르는 스크립트·실행 파일이 이미지에 있는지 찾습니다.
3. periodic 폴더와 설정 파일을 같은 버전의 기준본과 비교해 늘어난 파일과 바뀐 줄을 가려냅니다.
4. 부르는 파일마다 서명과 출처를 확인합니다.

실행 중인 시스템에서 확인할 때의 원칙은 [라이브 대응 (Live Response)](../../03-techniques/process-acquisition/live-response/index.md)을 따릅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 |
|---|---|
| [실행 에이전트·데몬](launchd/index.md) | 같은 시기에 심어진 다른 자동 실행 |
| [그 밖의 지속성 위치 (Login Hook·Authorization Plugin·Emond)](other-persistence.md) | 흔히 쓰이지 않는 다른 자동 실행 |
| [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) | 예약 파일과 부르는 파일이 만들어지고 바뀐 순서 |
| [통합 로그의 프로세스 실행 기록 (Process Events)](../execution/unified-log-process.md) | 예약된 명령이 실제로 실행됐는지 |
| [감사 로그 (OpenBSM Audit)](../logs/openbsm-audit.md) | 켜져 있었다면 파일 쓰기와 프로세스 실행 기록 |
| [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md) | 명령이 부르는 파일이 어디서 내려받은 것인지 |

지속성 위치를 한꺼번에 살펴보는 순서는 [악성 코드 지속성 찾기 (Persistence)](../../04-scenarios/incident/persistence.md)에 있습니다.

## 실습

NIST CFReDS 같은 공개 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 위치 표의 경로 가운데 이미지에 실제로 있는 것과 심볼릭 링크인 것을 구분해 적습니다.
2. crontab이나 at 작업 파일이 있다면 소유자와 명령을 적고, 명령이 부르는 파일이 이미지에 있는지 봅니다.
3. periodic 폴더의 스크립트 목록을 적고, 같은 macOS 버전의 설치본과 다른 파일이 있는지 봅니다.
4. 찾은 파일의 파일 시스템 시각을 다른 지속성 위치의 시각과 한 줄에 놓고 같은 시각대에 바뀐 것이 있는지 봅니다.

## 참고 문헌

1. Phil Stokes, "How Malware Persists on macOS" (SentinelOne, 2022-10-27 갱신) — https://www.sentinelone.com/blog/how-malware-persists-on-macos/
2. ForensicArtifacts, artifacts/data/macos.yaml (main 브랜치) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
