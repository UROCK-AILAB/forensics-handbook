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

보호된 위치까지 읽으려면 수집 도구에 root 권한과 전체 디스크 접근 권한(Full Disk Access)이 모두 있어야 합니다. Aftermath도 실행할 때 이 두 권한을 모두 요구합니다 [1]. 이 권한이 없을 때 어떤 경로가 빠지는지는 시험용 맥에서 권한을 주기 전과 준 뒤의 결과를 비교해 확인하고, 권한 구조는 [개인 정보 보호 권한 (TCC)](../../../02-artifacts/credentials/tcc/index.md)에서 봅니다.

## 절차

1. 결과를 받을 외부 저장 매체를 준비하고, 수집 도구의 이름과 버전을 적습니다.
2. 도구에 root 권한과 전체 디스크 접근 권한을 줍니다. 권한을 주는 조작도 원본 맥에 흔적을 남길 수 있으니, 한 조작과 시각을 그대로 기록해 두고 나중에 사용자 행위와 가릅니다.
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
| 결과 | zip 아카이브 하나 | 쓰기 전에 그 버전으로 시험해 확인 | XLSX, CSV, TSV, JSONL, SQLite |

— 칸은 쓰기 전에 그 도구의 문서와 도움말로 확인합니다.

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

mac_apt는 E01, VMDK, AFF4, DD, split-DD, 압축하지 않은 DMG, SPARSEIMAGE, UAC 수집물, Velociraptor 수집 파일, 마운트된 이미지를 입력으로 받습니다 [3]. 자체 HFS·APFS 파서로 macOS 11 Big Sur의 봉인된(sealed) 볼륨과 macOS 10.15 Catalina 이후 따로 마운트되는 SYSTEM·DATA 볼륨을 처리하고 [3], 암호화된 APFS 이미지는 암호나 복구 키로 엽니다 [3]. 켜져 있는 맥(live machines)도 대상으로 삼을 수 있지만 [3], 그때 전체 디스크 접근 권한이 필요한지는 시험용 맥에서 먼저 확인합니다. 볼륨 구성은 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../../../01-foundations/disk-volume/volume-group-firmlinks.md)에서 봅니다.

### 통합 로그

Aftermath에는 통합 로그 모듈과, predicate를 적은 파일을 넘기는 `--logs` 옵션이 있어서 수집 단계에서 통합 로그를 함께 모을 수 있습니다 [1]. 통합 로그의 저장 형식은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에 있습니다.

## 함정과 한계

논리 수집물에는 도구가 고른 파일만 들어 있습니다. 수집물에 어떤 파일이 없다고 원본 맥에 없었다고 말할 수 없고, 파일 단위 복사라서 지운 파일이 남은 빈 공간도 담기지 않습니다. 지운 데이터를 찾아야 하는 사건이면 [삭제 데이터 복구 (Data Recovery)](../../analysis/data-recovery/index.md)와 이미징 쪽을 함께 검토합니다.

같은 도구라도 권한과 버전에 따라 모이는 범위가 달라집니다. Aftermath는 macOS 12.0 이상을 지원해서 [1] 그보다 옛 맥에는 다른 도구를 찾아야 하고, 전체 디스크 접근 권한 없이 돌린 결과는 보호 위치가 빠졌을 수 있습니다. 새 도구나 새 버전을 현장에 쓰기 전에는 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md)에 따라 시험합니다.

Aftermath 폴더를 지우는 `--cleanup` 옵션을 썼다면 그 사실도 보관 기록에 적습니다 [1]. 현재 네트워크 연결이나 실행 중인 프로세스처럼 수집한 순간의 상태는 다시 뜰 수 없어서, 수집 시각을 결과와 함께 남깁니다.

### 확장 속성을 잃는 곳

맥 파일에는 내용 말고도 확장 속성 (extended attribute, xattr), 리소스 포크, Finder 정보가 붙어 있고, [격리 속성](../../../02-artifacts/filesystem/quarantine/index.md)과 [다운로드 출처](../../../02-artifacts/filesystem/where-froms.md)처럼 조사에 쓰는 값이 여기에 들어 있습니다. 논리 수집은 파일을 복사해 담는 방식이라, 담는 형식·받는 매체·복사 명령·분석 도구 가운데 한 곳에서라도 이 정보를 다루지 못하면 수집물에서 사라지거나 화면에 나오지 않습니다 [4]. APFS가 확장 속성을 저장하는 방식은 [확장 속성 (Extended Attributes)](../../../01-foundations/disk-volume/apfs/extended-attributes.md)에 있습니다.

담는 형식에서는 L01·Lx01이 문제가 됩니다. 두 형식은 EWF 계열의 논리 증거 컨테이너인데, SUMURI 지침서는 이 형식이 파일 메타데이터를 받아 담으면서 정규화하고 그 과정에서 확장 속성·리소스 포크·Finder 정보가 빠지거나 다른 모양으로 바뀐다고 봅니다. 도구 탓이 아니라 형식의 성질이라서 맥 증거에는 L01·Lx01을 쓰지 말라고 권합니다 [4].

SUMURI 지침서는 받는 매체가 exFAT·FAT·NTFS이면 이 파일 시스템이 담지 못하는 속성이 없어지고, 나중에 되돌릴 수 없다고 봅니다 [4]. 맥에서 FAT·exFAT 볼륨으로 복사하면 속성이 원래 파일 옆의 `._` 파일로 옮겨 가기는 하지만([애플더블 파일 (AppleDouble)](../../../02-artifacts/filesystem/appledouble.md)), 원래 파일과 따로 있는 숨김 파일이라 결과물을 옮기거나 해시할 때 함께 다뤄야 합니다.

복사 명령은 옵션에 따라 결과가 달라집니다. SUMURI 지침서는 cp·rsync·tar·ZIP 모두 보존 옵션 없이 쓰면 확장 속성을 잃는다고 봅니다 [4]. 명령마다 설명서에 적힌 보존 방법은 아래와 같습니다.

| 명령 | 확장 속성을 보존하는 방법 | 근거 |
|---|---|---|
| macOS `cp` | `-p` 를 주면 수정 시각·권한과 함께 ACL과 확장 속성(리소스 포크 포함)도 보존합니다. `-X` 를 주면 확장 속성과 리소스 포크를 복사하지 않습니다. | [6] |
| `ditto` | Mac OS X 10.5부터 리소스 포크·확장 속성·ACL 보존이 기본입니다. `--norsrc` 를 주면 따로 지정하지 않는 한 확장 속성과 ACL도 함께 빠집니다. | [5] |
| `ditto -c -k` (zip으로 묶기) | `--sequesterRsrc` 를 주면 리소스 포크와 HFS 메타데이터를 zip 안 `__MACOSX` 폴더에 담고, ditto로 풀 때 이 폴더를 찾아 되살립니다. | [5] |
| macOS `tar` (bsdtar) | 묶을 때는 `--xattrs`·`--mac-metadata` 가 기본입니다. 풀 때는 root로 실행할 때만 기본이고, 일반 사용자로 풀면 확장 속성을 넣지 않습니다. | [7] |
| rsync 3.x | `-a` 에 확장 속성이 들어가지 않아서 `-X` (`--xattrs`)를 따로 줍니다. | [8] |
| openrsync | Apple 전용 옵션 `-E` (`--extended-attributes`)가 확장 속성·리소스 포크·ACL을 복사하고, `-a` 에는 들어가지 않습니다. | [9] |

macOS `tar` 설명서로는 묶을 때 확장 속성이 기본으로 들어가서 SUMURI 지침서의 설명과 다릅니다. 다만 일반 사용자 권한으로 풀면 기본으로 빠지므로, tar 수집물은 푸는 쪽 권한과 옵션도 기록합니다. rsync는 구현마다 옵션 이름이 달라서, 쓰기 전에 그 맥의 `man rsync` 로 어느 옵션을 받는지 확인합니다.

분석 도구가 확장 속성을 읽지 못하면 수집물에 속성이 들어 있어도 화면에 나오지 않습니다 [4]. 수집물에서 격리 속성이나 다운로드 출처가 보이지 않을 때는 속성이 원래 없는 것인지 도구가 읽지 못하는 것인지 다른 도구로 한 번 더 확인합니다.

그래서 논리 수집물은 APFS나 HFS+로 포맷한 매체에 담고, 이미지로 묶을 때는 DMG나 sparseimage·sparsebundle처럼 macOS가 그대로 마운트하는 형식을 씁니다. SUMURI 지침서는 이 형식들이 확장 속성을 정규화하지 않아서 그대로 보존하고, HFS+는 macOS 27에서도 암호화하지 않은 볼륨이면 계속 지원된다고 봅니다 [4]. 각 이미지 형식의 구조는 [디스크 이미지 형식 (DMG·Sparsebundle)](../../../01-foundations/disk-volume/dmg-sparsebundle.md)에서 다룹니다.

## 결과를 어떻게 해석하나

수집물의 각 항목은 "그 도구가 그 시각에 그 권한으로 읽은 결과" 입니다. 보고서에는 "Aftermath(버전)를 root와 전체 디스크 접근 권한으로 실행해, 수집 시각에 이 파일이 이 경로에 있었다" 처럼 도구·권한·시각을 붙여 씁니다. 수집물에서 뽑은 시각을 이어 붙이는 방법은 [타임라인 작성 (Timeline)](../../analysis/timeline/index.md)에서 다룹니다.

## 참고 문헌

1. jamf/aftermath README (GitHub) — https://github.com/jamf/aftermath
2. tclahr/uac README (GitHub) — https://github.com/tclahr/uac
3. ydkhatri/mac_apt README (GitHub) — https://github.com/ydkhatri/mac_apt
4. SUMURI, Mac Forensics Best Practices Guide, 2026 Edition (2026-09) — https://sumuri.com/
5. ditto(1) macOS 설명서 — https://keith.github.io/xcode-man-pages/ditto.1.html
6. cp(1) macOS 설명서 — https://keith.github.io/xcode-man-pages/cp.1.html
7. bsdtar(1) macOS 설명서 — https://keith.github.io/xcode-man-pages/bsdtar.1.html
8. rsync(1) 설명서 (rsync 3.x) — https://download.samba.org/pub/rsync/rsync.1
9. openrsync(1) macOS 설명서 — https://keith.github.io/xcode-man-pages/openrsync.1.html
