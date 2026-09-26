---
title: "박스 드라이브"
parent: "아티팩트 · 클라우드·노트"
nav_order: 2260
---

# 박스 드라이브 (Box Drive)

박스 드라이브는 Box 클라우드 저장소를 탐색기 폴더처럼 보여 주는 Windows 앱입니다. 앱 메타데이터는 `AppData\Local\Box\Box\` 아래에 있고, 사용자 파일은 기본으로 `C:\Users\<USER>\Box\` 에 있습니다. 메타데이터 DB 에는 파일 목록, 동기화 사건, 로그인 정보가 남습니다.

> 아래 DB·열 설명은 Windows 10 과 2021년 무렵 앱 판 기준입니다[2]. 그 뒤 판에서는 구조가 다를 수 있어 실제 데이터로 확인합니다.

## 무엇을 기록하나 · 왜 생기나

박스 드라이브 폴더에는 로컬에 있는 파일과 필요할 때 내려받는(on-demand) 클라우드 파일이 함께 보이는데, 이렇게 보여 주려고 앱이 파일·폴더 목록과 동기화 상태를 로컬 DB 에 적어 둡니다. 이 DB 에는 아래 정보가 남습니다[2].

  - 파일·폴더 이름, 부모 폴더, 크기, 만든·고친 시각
  - 이름 바꾸기 같은 로컬 동기화 사건
  - 앱 로그
  - 로그인 이름, 회사(Enterprise) 이름, 동기화 폴더 같은 설정
옛 제품 Box Sync 는 다른 폴더를 씁니다(아래 표).

## 위치와 버전별 차이

| 제품 | 앱 메타데이터 | 사용자 파일 기본 위치 |
|---|---|---|
| 박스 드라이브 | `C:\Users\<USER>\AppData\Local\Box\Box\` (하위 폴더까지) | `C:\Users\<USER>\Box\` |
| Box Sync (옛 제품) | `C:\Users\<USER>\AppData\Local\Box Sync\` | `C:\Users\<USER>\Box Sync\` |

- 사용자는 사용자 파일 폴더 위치를 바꿀 수 있습니다.
- 바뀐 위치는 아래 파일에서 찾습니다[1].
  - 박스 드라이브: `Box_Streem` 로그
  - Box Sync: `sync_root_folder.txt`
- `Box_Streem` 로그의 정확한 폴더와 파일 이름 형식, 로컬 캐시 폴더 위치는 공개 자료에 나오지 않습니다. 메타데이터 폴더를 하위 폴더째 모은 뒤 그 안에서 찾습니다.

### 클라우드 파일을 보여 주는 방식

- 박스 드라이브 폴더의 파일이 모두 로컬에 있지는 않습니다. 이 폴더를 모으면 on-demand 클라우드 파일까지 내려받게 됩니다[1].
- 박스 드라이브가 Windows Cloud Files API 로 이 동작을 하는지, 자체 파일 시스템 드라이버를 쓰는지는 공개 자료에 나오지 않습니다.
- 실제 기기에서는 SyncRootManager 키에 Box 공급자 이름으로 시작하는 항목이 있는지 봅니다. 키 위치와 읽는 법은 [클라우드 동기화 공통 구조](cloud-files-api-syncrootmanager.md) 에 정리합니다.

## 구조

### 메타데이터 DB 파일

- 박스 파일·캐시 파일·가상 파일 정보는 `streemfs.db` 에 있습니다[2]. 이 이름은 `streemsfs.db` 로 적힌 자료도 있어 철자는 실제 데이터로 확인합니다.
- 실제 기기에서는 메타데이터 폴더에서 `streem` 으로 시작하는 `.db` 파일을 찾습니다.
- 파일 형식은 파일 머리로 구분합니다. SQLite 머리이면 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 방법으로 읽습니다.

### 도구가 보여 주는 항목 묶음

아래 묶음과 항목 이름은 블로그의 도구가 붙인 표시 이름입니다. 실제 표·열 이름이 아닙니다.

| 묶음 | 항목 |
|---|---|
| Box FS Nodes | Last Consistent Size, Creation Date, Item Last Access Date, Item Name, Parent Folder, Is File, Modification Date, Size, Is Dirty Data |
| Box Items | Creation Date, Item Type, Parent Folder, Item Name, Item Size, Last Update Date |
| Box Local Events | Creation Date, Item Old Name, Sync Event Type, Base Name, Last Update Date, Item Native Type, Item Size |
| Box Local Items | Creation Date, Item Type, Parent Folder, Item Size, Last Update Date, Item Name |
| Box Logs | Logged Date, Log Level, Component, Source File, Log Message, Process, Offset |
| Box Preferences | Display Username, Last Modified Time, Last Sync time, Box Homepage, Enterprise Name, Is Startup Completed, Currently Logged In, Sync Directory, Is First Run, Login Name |

각 묶음이 어느 DB 파일의 어느 표에서 오는지, 실제 표·열 이름과 시각 저장 형식은 공개 자료에 나오지 않습니다. 그래서 실제 데이터에서는 DB 마다 표 목록을 먼저 뽑고, 위 항목 이름과 뜻이 맞는 열을 찾아 짝을 짓습니다.

## 증거로서 의미

### 증명하는 것

- 메타데이터 폴더와 DB 가 있으면 그 사용자 프로필에서 박스 드라이브가 돈 적이 있습니다.
- 파일 목록 항목(이름, 부모 폴더, 크기, 시각)으로 그 계정 저장소에 어떤 파일·폴더가 보였는지 알 수 있습니다.
- "Item Old Name" 과 "Sync Event Type" 항목이 있으므로 이름 바꾸기 같은 동기화 사건을 볼 수 있을 것으로 보입니다[2].
- 설정 쪽의 로그인 이름, 회사 이름, 동기화 폴더로 어느 계정이 어느 폴더를 썼는지 좁힐 수 있을 것으로 보입니다[2].

### 증명하지 못하는 것

- 목록에 파일이 있다고 그 파일 내용이 이 PC 에 내려왔다는 뜻은 아닙니다. 박스 드라이브 폴더에는 로컬에 없는 파일도 보입니다.
- "Item Last Access Date" 가 사용자가 파일을 연 때인지는 공개 자료에 나오지 않습니다.
- 묶음 이름에 "Local" 이 붙어 있지만, 사건을 누가 어느 기기에서 일으켰는지 구분하는 항목은 공개 자료에 나오지 않습니다.
- 로그인 이름은 계정을 가리킵니다. 그 시각에 PC 앞에 앉은 사람은 따로 밝힙니다([그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)).

보고서에는 "X 파일을 Box 에 올렸다" 대신 이렇게 씁니다. "박스 드라이브 메타데이터 DB 에 이름이 X 인 항목이 있고, 그 항목의 만든 시각 열 값은 Y 이다. 이 열이 서버 시각인지 로컬 시각인지는 확인하지 못했다."

## 시각 해석

- DB 에는 Creation Date, Modification Date, Last Update Date, Logged Date 같은 시각 항목이 있습니다[2]. 시각이 어떤 단위·기준으로 저장되는지, UTC 인지 현지 시각인지는 공개 자료에 나오지 않습니다.
- 값의 자릿수로 형식을 먼저 짐작합니다. 자릿수로 형식을 구분하는 법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- 짐작한 변환이 맞는지는 시각을 아는 사건(예: 조사 중 직접 만든 파일, 로그의 앱 시작 줄)과 맞춰 봅니다.
- 파일 목록의 만든·고친 시각이 서버 쪽 값인지, 로컬 파일 시스템 값인지도 실제 데이터로 확인합니다.

## 함정과 한계

- **라이브 수집에서 서버 내려받기가 일어날 수 있습니다.** 사용자 파일 폴더를 모으면 로컬에 없던 클라우드 파일까지 내려옵니다. 수집 권한 범위를 먼저 확인하거나, PC 를 네트워크에서 뗀 뒤 모읍니다.
- **내려받기는 PC 에 새 흔적을 남길 수 있습니다(추론).** 라이브로 모았다면 수집 시각 뒤의 파일 생성·변경 기록은 조사관이 만든 것일 수 있습니다. 수집 시각을 기록해 둡니다.
- **사용자 파일 폴더는 옮길 수 있습니다.** 기본 위치에 폴더가 없다고 앱을 쓰지 않은 것이 아닙니다.
- **DB 이름 철자가 자료마다 다릅니다.** 한 이름으로만 찾으면 놓칩니다.
- **도구 표시 이름을 실제 열 이름으로 적지 않습니다.** 보고서에는 실제 데이터에서 확인한 표·열 이름을 씁니다.
- **앱 판이 바뀌었을 수 있습니다.** 위 설명은 2021년 Windows 10 기준입니다[2]. 앱 판이 다르면 파일·열이 다를 수 있습니다.
- **옛 제품 Box Sync 를 따로 찾습니다.** 폴더 이름이 달라서 박스 드라이브 위치만 보면 놓칩니다.

## 직접 분석해 보기

### 헥스로 한 번

DB 내부 구조를 설명한 공개 자료는 없습니다. 헥스로는 파일 형식과 문자열 위치를 확인하는 데까지만 봅니다.

1. 메타데이터 폴더를 하위 폴더째 사본으로 뜹니다. 분석은 사본에서만 합니다.
2. `.db` 파일을 헥스 편집기로 열어 맨 앞이 SQLite 머리 문자열인지 봅니다. 머리 구조는 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에 있습니다.
3. 같은 이름으로 시작하는 `-wal`·`-journal`·`-shm` 파일이 있는지 봅니다. 있으면 함께 둡니다. 곁 파일의 뜻은 [WAL과 롤백 저널](../../01-foundations/database-log-formats/sqlite/wal-journal-shm.md) 에 있습니다.
4. 사용자 파일 폴더 경로의 일부(예: 사용자 이름과 `Box`)를 UTF-8 과 UTF-16LE 로 각각 검색합니다. 어느 파일에 동기화 폴더 경로가 적혀 있는지 찾는 단계입니다. 인코딩 차이는 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에 있습니다.
5. 조사 대상 파일 이름 하나를 같은 방법으로 검색해, 그 이름이 어느 DB 에 들어 있는지 확인합니다.

### 공개 도구로 한 번

- KAPE 대상 `BoxDrive_Metadata` 는 메타데이터 폴더를 모읍니다.
- KAPE 대상 `BoxDrive_UserFiles` 는 사용자 파일 폴더를 모읍니다. 위 "함정" 의 경고가 이 대상에 붙어 있습니다.
- DB 가 SQLite 이면 SQLite 명령줄 도구(sqlite3) 같은 공개 도구로 엽니다. 먼저 `.tables` 로 표 목록을, `.schema` 로 열 이름을 뽑습니다.
- 뽑은 열 이름을 위 "도구가 보여 주는 항목 묶음" 표와 맞춰, 어떤 표가 파일 목록·동기화 사건·설정을 담는지 정합니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 클라우드 동기화 공통 구조 | Box 가 SyncRootManager 에 등록돼 있는지, 동기화 폴더가 어디인지 봅니다 | [클라우드 동기화 공통 구조](cloud-files-api-syncrootmanager.md) |
| 설치 프로그램 | 박스 드라이브·Box Sync 가 설치된 적이 있는지 봅니다 | [설치 프로그램](../system-account/uninstall.md) |
| 프리페치 | 박스 드라이브 실행 파일이 언제 실행됐는지 봅니다 | [프리페치](../execution/prefetch/index.md) |
| SRUM | 그 시간대에 박스 드라이브가 네트워크로 얼마나 주고받았는지 봅니다 | [SRUM](../execution/system-resource-usage-monitor/index.md) |
| USN 변경 저널 | 사용자 파일 폴더에서 파일이 언제 생기고 이름이 바뀌었는지 봅니다 | [USN 변경 저널](../filesystem/usnjrnl.md) |
| 마스터 파일 테이블 | 사용자 파일 폴더 안 파일의 NTFS 시각을 봅니다 | [마스터 파일 테이블](../filesystem/mft.md) |
| 자료 유출 시나리오 | 클라우드 저장소를 다른 흔적과 묶어 해석하는 순서를 봅니다 | [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md) |

## 실습

박스 드라이브나 Box Sync 가 깔린 공개 시험 데이터(NIST CFReDS 등)를 구해 아래 질문을 풀어 봅니다.

1. `AppData\Local\Box\Box\` 와 `AppData\Local\Box Sync\` 가운데 무엇이 있습니까? 둘 다 있습니까?
2. 메타데이터 폴더에서 `streem` 으로 시작하는 `.db` 파일의 정확한 이름은 무엇입니까? 파일 머리는 SQLite 입니까?
3. 표 목록을 뽑아, 위 묶음 표의 "Box FS Nodes"·"Box Local Events"·"Box Preferences" 와 뜻이 맞는 표를 찾습니다.
4. 설정 쪽 표에서 로그인 이름과 동기화 폴더 경로를 찾습니다. 기본 위치와 같습니까?
5. 시각 열 하나를 골라 단위를 짐작하고, 그 파일의 NTFS 시각과 비교합니다. 몇 초 차이입니까?
6. 이름 바꾸기 사건이 있으면 옛 이름과 새 이름을 적고, USN 변경 저널의 같은 파일 기록과 맞춰 봅니다.

## 참고 문헌

1. Eric Zimmerman 외, KapeFiles GitHub 저장소 (커밋 ed0f9c7), `Targets/Apps/BoxDrive_Metadata.tkape`, `Targets/Apps/BoxDrive_UserFiles.tkape` — https://github.com/EricZimmerman/KapeFiles
2. Forensafe, "Box" 블로그 (2021-05-27) — https://www.forensafe.com/blogs/box.html
