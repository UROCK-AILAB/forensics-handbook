---
title: "논리 수집"
parent: "맥 증거 확보"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1930
---

# 논리 수집 (Logical Collection)

논리 수집은 켜져 있는 맥에서 조사에 필요한 파일과 시스템 정보를 파일 단위로 골라 모으는 방법이고, 공개 도구로는 Aftermath와 UAC가 있으며 mac_apt가 그 결과를 받아 분석합니다 [1][2][3].

## 언제 쓰나

맥이 켜져 있고 잠금이 풀려 있을 때 씁니다. T2·Apple silicon 맥에서 이 상태가 왜 중요한지는 [확보 방법 고르기 (T2·Apple Silicon)](choosing-method.md)에서 다루고, 디스크나 폴더를 통째로 이미지로 뜨는 방법은 [라이브 이미징 (Live Imaging)](live-imaging.md)에서 다룹니다. 두 방법을 함께 쓸 때 어떤 휘발성 정보를 먼저 모을지는 [라이브 대응 (Live Response)](../live-response/index.md)을 따릅니다.

보호된 위치까지 읽으려면 수집 도구에 root 권한과 전체 디스크 접근 권한(Full Disk Access)이 모두 있어야 합니다. Aftermath도 실행할 때 이 두 권한을 모두 요구합니다 [1]. 이 권한이 없을 때 빠지는 경로는 공개된 분석 자료가 없어 시험용 맥에서 확인하고, 권한 구조는 [개인 정보 보호 권한 (TCC)](../../../02-artifacts/credentials/tcc/index.md)에서 봅니다.

## 절차

1. 결과를 받을 외부 저장 매체를 준비하고, 수집 도구의 이름과 버전을 적습니다.
2. 도구에 root 권한과 전체 디스크 접근 권한을 줍니다. 권한을 주는 조작이 원본 맥에 남기는 흔적은 공개된 분석 자료가 없어서, 한 조작과 시각을 그대로 기록해 두고 나중에 사용자 행위와 가릅니다.
3. 출력 위치를 외부 매체로 정해 도구를 실행합니다. Aftermath는 출력 위치를 정하지 않으면 `/tmp` 에 결과를 써서 [1], 기본값 그대로 두면 증거 맥의 디스크에 쓰게 됩니다.
4. 수집이 끝나면 곧바로 결과물의 해시를 계산해 기록합니다. 방법은 [해시와 증거 보관 (Hash·Chain of Custody)](hash-chain-of-custody.md)에 있습니다.
5. 결과물의 사본을 분석 도구에 넣습니다. Aftermath 결과는 Aftermath의 분석 옵션으로, UAC 결과는 mac_apt로 바로 읽을 수 있습니다 [1][3].

## 도구

세 도구를 나란히 놓으면 아래와 같습니다.

| 항목 | Aftermath [1] | UAC (Unix-like Artifacts Collector) [2] | mac_apt [3] |
|---|---|---|---|
| 하는 일 | 수집과 수집물 분석 | 수집 | 수집물·이미지 분석 |
| 지원 OS | macOS 12.0 이상 | AIX, ESXi, FreeBSD, Linux, macOS, NetBSD, NetScaler, OpenBSD, Solaris | Python 3.10 이상(64비트)에서 실행 |
| 설치 | 서명·공증된 Aftermath.pkg, `/usr/local/bin/` 에 설치 | 설치 없이 내려받아 실행 | — |
| 라이선스 | MIT | Apache 2.0 | — |
| 결과 | zip 아카이브 하나 | 공개 자료 없음 | XLSX, CSV, TSV, JSONL, SQLite |

— 는 공개 자료에 없는 칸입니다.

### Aftermath

Aftermath는 artifacts, filesystem, network, persistence, processes, system reconnaissance, unified logs 모듈로 나눠 모읍니다 [1]. 모으는 항목에는 구성 프로파일, 브라우저 데이터(Arc, Brave, Chrome, Edge, Firefox, Safari), LaunchAgents·LaunchDaemons, TCC 데이터베이스, 셸 기록, 현재 네트워크 연결 등이 있습니다 [1]. 옵션은 아래와 같습니다 [1].

| 옵션 | 하는 일 |
|---|---|
| `-o`, `--output` | 결과를 쓸 위치. 지정하지 않으면 `/tmp` |
| `--deep`, `-d` | 시각 메타데이터를 얻는 파일 시스템 스캔(시간과 메모리를 많이 씀) |
| `--analyze` | 수집한 zip을 분석(수집한 DB 파싱 결과, 파일 타임라인, storyline) |
| `--pretty` | 터미널 출력에 색을 입힘 |
| `--collect-dirs` | 원본 파일 그대로 덤프할 디렉터리 지정(공백으로 구분) |
| `--cleanup` | 기본 위치의 Aftermath 폴더 삭제 |
| `--disable` | 일부 수집 끄기(browsers, databases, filesystem, proc-info, ul 등 또는 all) |
| `--logs` | 통합 로그 predicate를 적은 텍스트 파일 지정 |
| `--es-logs` | 모을 Endpoint Security 이벤트 지정(기본 create, exec, mmap) |

옵션 이름과 동작은 버전마다 바뀔 수 있어서, 쓰기 전에 그 버전의 도움말로 다시 확인합니다.

### UAC

UAC는 실행 중인 프로세스 정보, 실행 중인 프로세스와 실행 파일의 해시, 파일·디렉터리 상태로 만든 bodyfile, 시스템·사용자 데이터와 설정 파일, 로그를 모읍니다 [2]. 수집 범위는 `ir_triage`, `full`, 사용자 정의 프로파일로 고릅니다 [2]. 메모리 획득은 리눅스에서만 되고 macOS에서는 되지 않습니다 [2]. 출력 형식, 수집 로그를 남기는 방식, macOS에서 root와 전체 디스크 접근 권한이 필요한지는 쓰기 전에 그 버전으로 시험해 확인합니다.

### mac_apt

mac_apt는 E01, VMDK, AFF4, DD, split-DD, 압축하지 않은 DMG, SPARSEIMAGE, UAC 수집물, Velociraptor 수집 파일, 마운트된 이미지를 입력으로 받습니다 [3]. 자체 HFS·APFS 파서로 macOS 11 Big Sur의 봉인된(sealed) 볼륨과 macOS 10.15 Catalina 이후 따로 마운트되는 SYSTEM·DATA 볼륨을 처리하고 [3], 암호화된 APFS 이미지는 암호나 복구 키로 엽니다 [3]. 켜져 있는 맥(live machines)도 대상으로 삼을 수 있지만 [3], 그때 전체 디스크 접근 권한이 필요한지는 공개 자료가 없어 시험용 맥에서 확인합니다. 볼륨 구성은 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../../../01-foundations/disk-volume/volume-group-firmlinks.md)에서 봅니다.

### 통합 로그

Aftermath에는 통합 로그 모듈과, predicate를 적은 파일을 넘기는 `--logs` 옵션이 있어서 수집 단계에서 통합 로그를 함께 모을 수 있습니다 [1]. 통합 로그의 저장 형식은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있습니다.

## 함정과 한계

논리 수집물에는 도구가 고른 파일만 들어 있습니다. 수집물에 어떤 파일이 없다고 원본 맥에 없었다고 말할 수 없고, 파일 단위 복사라서 지운 파일이 남은 빈 공간도 담기지 않습니다. 지운 데이터를 찾아야 하는 사건이면 [삭제 데이터 복구 (Data Recovery)](../../analysis/data-recovery/index.md)와 이미징 쪽을 함께 검토합니다.

같은 도구라도 권한과 버전에 따라 모이는 범위가 달라집니다. Aftermath는 macOS 12.0 이상을 지원해서 [1] 그보다 옛 맥에는 다른 도구를 찾아야 하고, 전체 디스크 접근 권한 없이 돌린 결과는 보호 위치가 빠졌을 수 있습니다. 새 도구나 새 버전을 현장에 쓰기 전에는 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md)에 따라 시험합니다.

Aftermath 폴더를 지우는 `--cleanup` 옵션을 썼다면 그 사실도 보관 기록에 적습니다 [1]. 현재 네트워크 연결이나 실행 중인 프로세스처럼 수집한 순간의 상태는 다시 뜰 수 없어서, 수집 시각을 결과와 함께 남깁니다.

## 결과를 어떻게 해석하나

수집물의 각 항목은 "그 도구가 그 시각에 그 권한으로 읽은 결과" 입니다. 보고서에는 "Aftermath(버전)를 root와 전체 디스크 접근 권한으로 실행해, 수집 시각에 이 파일이 이 경로에 있었다" 처럼 도구·권한·시각을 붙여 씁니다. 수집물에서 뽑은 시각을 이어 붙이는 방법은 [타임라인 작성 (Timeline)](../../analysis/timeline/index.md)에서 다룹니다.

## 참고 문헌

1. jamf/aftermath README (GitHub) — https://github.com/jamf/aftermath
2. tclahr/uac README (GitHub) — https://github.com/tclahr/uac
3. ydkhatri/mac_apt README (GitHub) — https://github.com/ydkhatri/mac_apt
