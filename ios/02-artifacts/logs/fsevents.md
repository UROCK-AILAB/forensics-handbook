---
title: "파일 시스템 이벤트"
parent: "아티팩트 · 로그"
nav_order: 1110
---

# 파일 시스템 이벤트 (FSEvents)

파일 시스템 이벤트 (FSEvents)는 fseventsd 가 `/private/var/.fseventsd` 와 `/private/var/mobile/.fseventsd` 폴더에 남기는 경로 단위 변경 기록이고, 어떤 파일이나 폴더가 만들어지고 지워지고 이름이 바뀌었는지를 플래그로 알려 줍니다[1]. 이미 지워진 사진·파일의 경로가 여기 남아 있을 수 있지만, 레코드에 시각이 없어서 날짜는 다른 기록으로 추정해야 합니다. 이벤트 파일은 전체 파일 시스템 추출에서만 얻을 수 있습니다[3].

## 무엇을 기록하나 · 왜 생기나

fseventsd 는 볼륨에서 일어난 파일 시스템 변경 알림을 모아 이벤트 파일로 씁니다. 레코드 하나에는 바뀐 경로, 이벤트 ID, 무엇이 바뀌었는지를 나타내는 플래그가 들어 있고, 레코드 버전에 따라 노드 ID 가 더 붙습니다[1][2]. 변경 종류에는 만들기(Created), 지우기(Removed), 이름 바꾸기·옮기기(Renamed), 내용 바꾸기(Modified), 복제(Cloned) 등이 있습니다[1][3].

기록은 macOS 와 같은 형식이라서 파일 구조, 버전별 레코드 모양, 플래그 비트의 뜻은 macOS 핸드북의 [파일 시스템 이벤트 (FSEvents)](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/fsevents/index.html) 에서 다룹니다. 이 페이지는 아이폰에서 달라지는 위치·수집 조건·해석만 씁니다.

파일이 지워진 뒤에도 그 경로는 Removed 플래그가 켜진 레코드로 남아 있을 수 있습니다[1]. 그래서 사진·동영상이 들어 있는 미디어 영역에서 파일을 지운 흔적을 찾는 데 쓸 수 있습니다[3].

## 위치와 버전별 차이

### 경로

iLEAPP 는 아래 두 폴더를 읽습니다[1].

| 경로 | iLEAPP 의 구분 |
|---|---|
| `/private/var/.fseventsd/` | 데이터 볼륨 쪽 기록 (data volume) |
| `/private/var/mobile/.fseventsd/` | 사용자 영역 쪽 기록 (user space) |

두 폴더의 레코드는 따로 쌓여서 둘 다 읽어야 합니다. iLEAPP 의 iOS 18.7.8 시험 이미지에서는 레코드 26,957건 가운데 데이터 볼륨 쪽이 11,939건, 사용자 영역 쪽이 15,018건이었습니다[1]. 같은 폴더의 `fseventsd-uuid` 파일은 이벤트 파일이 아니어서 분석에서 뺍니다[2].

### 수집 조건

이벤트 파일은 전체 파일 시스템 추출 (Full File System Extraction) 에서만 나오고, 로컬 백업에는 들어 있지 않습니다[3]. 백업에 들어오는 `com.apple.MobileBackup.plist` 에 `FSEventState` 키가 있지만, 이 키에는 경로와 플래그가 없어서 이벤트 레코드 대신 쓸 수 없습니다. 이 키의 하위 키는 [백업 폴더 구조](../../01-foundations/backups/local-backup/structure.md) 에 있습니다. 백업 전반은 [로컬 백업](../../01-foundations/backups/local-backup/index.md), 추출 방식의 차이는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

### iOS 버전

iLEAPP 가 이 기록을 시험한 이미지는 iOS 12, 15, 17, 18, 26(26.5.2)이고, 모든 이미지에서 레코드가 나왔습니다[1]. 레코드 버전 서명은 세 가지(`1SLD`, `2SLD`, `3SLD`)이고 iLEAPP 는 셋을 모두 읽습니다[1]. 어느 iOS 버전이 어떤 서명을 쓰는지는 이벤트 파일을 풀어 첫 4바이트로 직접 확인합니다.

## 구조

이벤트 파일은 GZIP 으로 압축한 데이터 여러 개를 이어 붙인 파일이고, 한 파일에 서너 개까지 들어 있습니다[3]. 풀면 12바이트 페이지 헤더 뒤로 레코드가 이어지고, 레코드는 NULL 로 끝나는 경로 뒤에 고정 길이 부분이 붙는 모양입니다[1][2].

| 서명 | 고정 부분 | iLEAPP 가 읽는 형식[1] | iLEAPP 결과 열 |
|---|---|---|---|
| `1SLD` | 12바이트 | `<QI` | Event ID, Event Flags |
| `2SLD` | 20바이트 | `<QIQ` | 위 두 열과 Node ID |
| `3SLD` | 24바이트 | `<QIQI` | 위 세 열과 Record Extra |

`3SLD` 의 마지막 4바이트를 FSEventsParser 는 `fs_uid` 로[2], iLEAPP 는 뜻을 정하지 않은 `Record Extra` 로 보여 줍니다[1]. 아이폰 기록에서는 이 값을 사용자 계정으로 단정하지 않습니다. 오프셋 표와 헥스 예시는 macOS 핸드북의 [파일 형식 (.fseventsd)](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/fsevents/format.html) 에 있습니다.

### 플래그

iLEAPP 는 플래그 4바이트를 리틀엔디언 (little-endian) 으로 읽어 이름을 붙이고, 이름 없는 비트는 `Unknown flag bits` 로 따로 보여 줍니다[1]. 조사에 자주 쓰는 비트는 다음과 같습니다[1].

| 값 (LE) | iLEAPP 이름 |
|---|---|
| 0x00000001 | Created |
| 0x00000002 | Removed |
| 0x00000008 | Renamed or moved |
| 0x00000010 | Content modified |
| 0x00000080 | Directory created |
| 0x00004000 | Item cloned |
| 0x00020000 | Path truncated |
| 0x00800000 | File |
| 0x01000000 | Directory |

FSEventsParser 는 같은 4바이트를 빅엔디언으로 읽어서 16진수가 다르게 보입니다[2]. 두 도구의 값을 한 표에 섞지 않고, 전체 대조표는 macOS 핸드북의 [이벤트 플래그 읽기](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/fsevents/flags.html) 에서 봅니다.

### iLEAPP 의 주제별 묶음

iLEAPP 는 전체 레코드 보고서와 함께, 경로 문자열과 플래그로 거른 보고서를 따로 만듭니다[1].

| 보고서 | 거르는 기준 (경로에 들어 있는 문자열) |
|---|---|
| Communications & Accounts | `sms.db`, `callhistory`, `addressbook`, `/mail/`, `facetime` 등 |
| Updates & Mobile Assets | `mobilesoftwareupdate`, `mobile_installation`, `mobileasset` 등 |
| App Containers | `containers/data/application/`, `containers/shared/appgroup/` 등 |
| Location Services | `locationd`, `routined`, `geoservices` 등 |
| Security | `keychain`, `keybags`, `/tcc/`, `trustd` 등 |
| Restore & Backup | `mobilebackup`, `.obliterated`, `erase_install` 등 |
| Web | `safari`, `/webkit/`, `/cookies/` 등 |
| APT & dpkg | 경로의 한 단계 이름이 `apt`, `dpkg`, `cydia`, `sileo`, `zebra` 인 경우 등 |
| Removed Paths | Removed 플래그(0x00000002)가 켜진 레코드 |

이 묶음은 경로 이름만 보고 거른 것이라 한 레코드가 여러 보고서에 함께 나올 수 있습니다[1].

## 증거로서 의미

### 증명하는 것

어떤 경로에 만들기·지우기·이름 바꾸기 같은 변경 알림이 기록됐다는 사실과, 같은 볼륨의 다른 레코드와 비교한 앞뒤 순서를 보여 줍니다[1]. 앱 DB 에 행이 없는 파일도 경로가 남아 있으면, 그 경로에 파일이 있었고 Removed 알림이 기록됐다는 근거로 쓸 수 있습니다[1][3].

### 증명하지 못하는 것

레코드에는 시각이 없고, 어떤 프로세스나 사용자가 바꿨는지도 들어 있지 않습니다[1]. Removed 플래그는 파일 시스템 알림일 뿐이라 사용자가 일부러 지웠다는 증거가 되지 않습니다[1]. 앱 컨테이너 경로에 기록이 있다고 그 앱을 실행했거나 사용자가 조작했다는 뜻도 아니고[1], 위치 서비스 경로의 기록에는 좌표가 없어서 기기의 위치를 알려 주지 않습니다[1]. 복원·초기화 관련 경로에 기록이 있어도 그 작업이 끝났다는 증거는 아닙니다[1].

보고서에는 "사진을 지웠다" 가 아니라 "`DCIM` 아래 이 경로에 Removed 플래그가 켜진 레코드가 있고, 이벤트 ID 로 보면 이 기록은 (다른 기록) 뒤에 생겼다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

레코드에는 시각 필드가 없고, 이벤트 ID 는 순서를 알려 줄 뿐 시각이 아닙니다[1][2]. MSAB 글은 이 기록으로 파일이 언제 지워졌는지도 알 수 있다고 설명하지만[3], 그 날짜는 레코드에서 바로 읽는 값이 아니라 아래 방법으로 추정한 값입니다.

FSEventsParser 는 날짜를 두 가지로 추정합니다[2].

1. **이벤트 파일의 수정 시각.** 이벤트 파일마다 파일 시스템의 수정 시각이 있고, 앞 파일과 이 파일의 수정 시각 사이에 이 파일의 레코드가 생겼다고 봅니다. 16진수 16자리로 된 이벤트 파일 이름을 그 파일의 마지막 이벤트 ID 로 읽고, 이 ID 와 수정 시각을 짝지어 이벤트 ID 범위마다 날짜를 붙입니다. 폴더의 첫 파일과 마지막 파일의 수정 시각이 같은 날 같은 시간이면 수정 시각이 보존되지 않았다고 보고 이 방법을 쓰지 않고, 이름이 이 형식이 아닌 파일은 카빙한 GZIP 으로 보고 날짜를 붙이지 않습니다[2].
2. **이름에 날짜가 든 경로.** 파일 이름에 날짜가 들어 있는 로그 파일이 만들어진 레코드를 찾아, 그 이벤트 ID 를 날짜의 기준점으로 씁니다. 그 앞뒤 이벤트 ID 의 레코드는 기준점 날짜 사이에 놓습니다[2].

FSEventsParser 는 이렇게 얻은 날짜를 시각 없이 `approx_dates_plus_minus_one_day` 열에 적고, 시간대 차이로 하루가 어긋날 수 있다고 밝힙니다[2][4]. 두 번째 방법이 찾는 경로는 `private/var/log/asl/` 아래 날짜 이름 파일, `mobile/Library/Logs/CrashReporter/DiagnosticLogs/security.log.` 뒤에 시각이 붙은 파일, `private/var/audit/` 아래 파일 등 여덟 가지로 정해져 있습니다[2]. 아이폰 기록에 이 경로가 없으면, 이름에 날짜가 든 다른 경로(예: 충돌 보고서 `.ips` 파일)를 직접 찾아 같은 방식으로 기준점을 잡습니다. 기준점으로 쓴 경로와 날짜는 보고서에 함께 적습니다.

이벤트 파일의 수정 시각은 도구가 UTC 로 보여 주는지 현지 시각으로 보여 주는지 먼저 확인합니다. FSEventsParser 는 폴더를 넣으면 수정 시각을 UTC 로 바꿔 적지만, 디스크 이미지를 넣으면 분석 PC 의 시간대로 바꾼 값에 `[UTC]` 를 붙여 적습니다[2]. 현지 시각으로 옮길 때는 기기의 시간대를 적용합니다. 시각 값 종류는 [시각 값](../../01-foundations/value-decoding/time-values.md), 기기 시간대는 [시간대와 시각 설정](../system-account/time-zone.md) 에서 다룹니다.

## 함정과 한계

- **합쳐진 레코드.** 알림은 하나로 합쳐질 수 있고, 그래서 한 레코드에 Created 와 Removed 가 함께 켜지기도 합니다[1]. 두 동작의 순서나 횟수를 레코드 하나로 판단하지 않습니다.
- **잘린 경로.** 경로가 잘린 레코드가 있고, 이때 Path truncated 플래그(0x00020000)가 켜집니다[1]. 잘린 경로는 다른 레코드나 파일 시스템과 맞춰 본 뒤 씁니다.
- **UUID 폴더 이름.** 앱 컨테이너 경로에는 번들 ID 대신 UUID 가 들어 있어서, 컨테이너 메타데이터로 번들 ID 를 이어야 합니다[1]. 방법은 [앱 컨테이너](../../01-foundations/storage/filesystem/app-containers.md) 에 있습니다.
- **많은 레코드.** iLEAPP 시험 이미지 한 개(iOS 17)에서 위치 서비스 경로만 3,569,449건이 나왔습니다[1]. 조사 질문에 맞는 경로와 플래그로 먼저 거른 뒤 봅니다.
- **도구마다 다른 16진수.** 플래그 값을 도구 사이에 옮겨 적으면 비트를 잘못 읽습니다. 어느 도구의 값인지 함께 적습니다.
- **Removed 는 사용자 행위가 아닙니다.** 시스템과 앱이 스스로 지우는 파일이 많아서, iLEAPP 의 Removed Paths 보고서는 시험 이미지 한 개(iOS 17)에서 3,112,884건이 나왔습니다[1]. 조사 대상 경로로 좁혀서 봅니다.

## 직접 분석해 보기

### 헥스로

1. 전체 파일 시스템 추출본에서 두 `.fseventsd` 폴더를 수정 시각을 보존한 채 복사하고 해시를 떠 둡니다.
2. 이벤트 파일의 첫 2바이트가 `1F 8B` 이면 GZIP 입니다.
3. 파일을 풀고 첫 4바이트가 `31 53 4C 44`(`1SLD`), `32 53 4C 44`(`2SLD`), `33 53 4C 44`(`3SLD`) 가운데 무엇인지 봐서 레코드 버전을 정합니다.
4. 12바이트 헤더 뒤의 경로 문자열을 읽고, 경로가 볼륨 맨 위부터 적혔는지 `.fseventsd` 폴더가 있는 위치부터 적혔는지 실제 데이터로 확인합니다.
5. 경로 뒤 NULL 다음 8바이트를 이벤트 ID, 그다음 4바이트를 플래그로 읽습니다. 헥스 예시는 macOS 핸드북의 [파일 형식](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/fsevents/format.html) 을 따릅니다.

아래 표는 iLEAPP 결과의 모양을 보여 주는 만든 예시이고, 경로와 값은 실제 기기에서 나온 것이 아닙니다. 경로 앞부분은 줄였습니다.

| Event ID | Path | Event Flags |
|---|---|---|
| 1715004 | `…/Media/DCIM/100APPLE/IMG_0001.HEIC` | Created \| File |
| 1715968 | `…/Media/DCIM/100APPLE/IMG_0001.HEIC` | Removed \| File |

### 공개 도구로

iLEAPP 의 FSEvents 모듈은 두 경로의 이벤트 파일을 모두 읽어 `Event ID`, `Path`, `Event Flags`, `Event Flags (Hex)`, `Item Type`, `Node ID`, `Record Extra`, `Format Version`, `Source File` 열로 보여 주고, 위의 주제별 보고서를 함께 만듭니다[1].

FSEventsParser(버전 4.1)는 `.fseventsd` 폴더를 통째로 넣어 `1SLD`·`2SLD`·`3SLD` 를 읽고 날짜 추정 열을 붙입니다[2]. 하위 폴더는 찾아 들어가지 않아서[4] 두 폴더를 따로 넣어 돌립니다. 폴더를 복사하면서 파일 수정 시각이 모두 복사한 때로 바뀌면, 수정 시각으로 날짜를 추정하는 첫 번째 방법이 빠집니다[2].

두 도구의 결과를 맞춰 볼 때는 이벤트 ID 와 경로로 행을 짝짓고, 플래그 16진수는 비교하지 않습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [사진 보관함](../media/photos/index.md) | Removed 가 켜진 `DCIM` 경로의 파일이 `Photos.sqlite` 에 남아 있는지, 휴지통 상태 열이 어떤지 |
| [카메라 사진과 메타데이터](../media/dcim-exif.md) | 같은 경로 파일의 EXIF 촬영 시각이 Created 레코드의 추정 날짜 범위와 맞는지 (촬영 시각과 파일이 만들어진 때는 다를 수 있음) |
| [설치된 앱](../app-usage/installed-apps.md) | App Containers 보고서의 컨테이너 UUID 와 번들 ID 짝 |
| [충돌·진단 기록](../app-usage/diagnostics.md) | 이름에 시각이 든 `.ips` 파일 경로를 날짜 기준점으로 쓰기 |
| [통합 로그에서 찾을 것](unified-log-events.md) | 추정한 날짜 범위에 같은 경로나 같은 앱이 남긴 로그 |
| [초기화와 복원 흔적](../system-account/erase-restore.md) | Restore & Backup 보고서의 `.obliterated`·`erase_install` 경로 |

지운 파일의 내용을 되찾는 일은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md), 날짜를 추정한 레코드를 다른 기록과 한 시간 축에 놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다. 지우기 행위를 따지는 순서는 [메시지·사진 지우기](../../04-scenarios/activity/anti-forensics/content-deletion.md) 에 있습니다.

## 실습

전체 파일 시스템 추출본이 들어 있는 공개 시험 이미지를 구했다면 다음 질문으로 풀어 봅니다.

1. `/private/var/.fseventsd/` 와 `/private/var/mobile/.fseventsd/` 에 이벤트 파일이 몇 개씩 있고, 레코드 버전 서명은 무엇입니까?
2. `DCIM` 아래 경로 가운데 Removed 플래그가 켜진 파일은 몇 개이고, 그중 `Photos.sqlite` 에 남아 있지 않은 파일은 무엇입니까?
3. 이름에 날짜가 든 경로를 하나 골라 기준점으로 삼으면, 2번 레코드는 어느 날짜 범위에 들어갑니까?
4. 같은 레코드를 iLEAPP 와 FSEventsParser 로 읽었을 때 플래그 16진수가 어떻게 다르게 보입니까?

## 참고 문헌

1. iLEAPP, `fileSystemEvents.py` — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/fileSystemEvents.py
2. FSEventsParser 4.1 소스 (Nicole Ibrahim) — https://github.com/dlcowen/FSEventsParser/blob/master/FSEParser_V4.1.py
3. Johan Persson, MSAB, "Hidden gems in Apple iOS digital forensics" (2024-03-21) — https://www.msab.com/blog/hidden-gems-in-apple-ios-digital-forensics/
4. FSEventsParser README — https://github.com/dlcowen/FSEventsParser/blob/master/README.md
