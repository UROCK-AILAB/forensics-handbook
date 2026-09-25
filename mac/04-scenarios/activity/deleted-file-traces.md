---
title: "지운 파일의 흔적 찾기"
parent: "시나리오 · 행위 재구성"
nav_order: 2320
---

# 지운 파일의 흔적 찾기 (Deleted File Traces)

## 조사 질문

이미 지운 파일이 있었는지, 있었다면 이름·위치·내용 일부와 지운 시점을 어디서 찾을 수 있는지 묻습니다. 유출·내부 조사에서는 지운 문서가 무엇이었는지를, 침해 사고에서는 공격 도구나 결과물을 지웠는지를 확인하는 데 씁니다.

아래 "먼저 확인할 것"에 적은 이유로, 요즘 맥 내장 SSD에서는 지운 파일의 블록을 원시 영역에서 긁어내는 방식이 잘 통하지 않습니다. 그래서 파일 자체보다 파일을 가리키던 다른 기록, 즉 휴지통 정보·파일 시스템 이벤트·섬네일 캐시·최근 항목·스냅숏·앱 데이터베이스의 빈 공간에 남은 이름과 조각을 모으는 방식으로 조사합니다. 복구 기법 자체는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)에서, 흔적을 일부러 지우는 동작은 [증거를 없애려 했나](anti-forensics/index.md)에서 다루고, 이 페이지는 지운 파일 하나를 쫓는 순서와 판단만 다룹니다.

## 먼저 확인할 것

OS 버전은 [OS 버전과 설치 기록](../../02-artifacts/system-account/os-version-install-history.md)에서 확인합니다. 지운 파일 흔적과 관련된 버전 차이는 다음과 같습니다.

| 항목 | 버전 |
|---|---|
| 파일 시스템 이벤트 레코드에 노드 ID 칸 | 10.13 부터 [4] |
| 파일 시스템 이벤트 레코드에 UID 칸 | 14 Sonoma 부터(FSEventsParser 코드 주석 기준) [5] |
| 빠른 보기 섬네일 캐시에서 파일 이름 칸이 없어짐 | 10.15 부터 [7] |
| 타임 머신이 `.DocumentRevisions-V100` 폴더를 백업 | Catalina 까지 [10] |
| FileVault 기본으로 켜짐 | 26.4 이후 맥 [14] |

하드웨어도 함께 확인합니다. Apple 실리콘과 T2 칩을 쓰는 맥은 FileVault 를 켜지 않아도 볼륨이 암호화돼 있고, 볼륨을 지우면 Secure Enclave 가 볼륨 암호화 키를 안전하게 지웁니다 [14]. APFS 는 파일 삭제나 빈 공간 회수 때 TRIM 명령을 메타데이터 변경을 저장한 뒤 비동기로 보냅니다 [15]. 이 두 조건 때문에 볼륨을 지운 뒤나 TRIM 이 끝난 블록에서는 내용을 되살리기 어려운 것으로 보입니다.

시간대는 [시간대와 시계 설정](../../02-artifacts/system-account/time-zone.md)에서 확인합니다. 수집 범위에서는 APFS 스냅숏과 타임 머신 로컬 스냅숏을 함께 확보했는지, `.fseventsd` 와 빠른 보기 캐시, 앱 데이터베이스의 `-wal` 파일까지 들어 있는지 봅니다. 로컬 스냅숏은 보통 24시간 뒤 지워져서 [16] 수집이 늦어질수록 잃는 것이 많습니다([맥 증거 확보](../../03-techniques/process-acquisition/evidence-acquisition/index.md)).

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 남을 수 있는 것 | 링크 |
|---|---|---|---|
| 1 | 휴지통 `~/.Trash/` 와 그 폴더의 `.DS_Store` | 아직 비우지 않은 항목, 원래 이름(`ptbN`)과 원래 위치(`ptbL`) | [휴지통](../../02-artifacts/file-folder-usage/trash.md) |
| 2 | 파일 시스템 이벤트 `.fseventsd` | Removed·Renamed 플래그가 붙은 경로(libyal 문서 값 0x2·0x8, 플래그를 빅엔디언으로 읽는 FSEventsParser 표기로는 0x02000000·0x08000000) [4][5] | [파일 시스템 이벤트](../../02-artifacts/filesystem/fsevents/index.md) |
| 3 | 빠른 보기 섬네일 캐시 | 원본을 지워도 남는 섬네일 | [빠른 보기 섬네일 캐시](../../02-artifacts/file-folder-usage/quicklook-thumbnails.md) |
| 4 | 최근 항목과 Finder plist | 지운 파일을 가리키는 북마크(경로·볼륨 정보) | [최근 항목](../../02-artifacts/file-folder-usage/recent-items/index.md) |
| 5 | 앱 저장 상태 | 창 제목에 남은 문서 이름 | [앱 저장 상태](../../02-artifacts/file-folder-usage/saved-application-state.md) |
| 6 | APFS 스냅숏, 타임 머신 로컬 스냅숏, 옛 체크포인트 | 지우기 전 시점의 파일 시스템 | [스냅숏과 백업 비교](../../03-techniques/analysis/snapshot-diff.md) |
| 7 | 문서 버전 | 고아 조각에서 나오는 옛 내용 | [문서 버전](../../02-artifacts/file-folder-usage/document-revisions.md) |
| 8 | 앱 SQLite 의 freelist·freeblock·WAL | 앱 DB에서 지운 행 | [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) |
| 9 | 바이옴 SEGB | 상태가 3(Deleted)인 기록에도 남는 시각 [18] | [바이옴](../../02-artifacts/execution/biome/index.md) |
| 10 | 격리 이벤트 DB | 받은 파일의 URL·시각 | [격리 속성과 다운로드 기록](../../02-artifacts/filesystem/quarantine/index.md) |
| 11 | 셸 기록 | 터미널에서 친 `rm` 명령 | [터미널 명령 기록](../../02-artifacts/execution/shell-history.md) |
| 12 | 스포트라이트 색인 | 색인에 남은 레코드 | [스포트라이트](../../02-artifacts/file-folder-usage/spotlight/index.md) |

1~5번은 지운 파일의 이름과 위치를 세우는 흔적이라 먼저 보고, 6~8번은 내용을 되찾을 가능성이 있는 곳이라 이름이 정해진 뒤 봅니다. 9~12번은 보강 자료입니다. 격리 이벤트 DB 행과 스포트라이트 레코드가 파일을 지운 뒤에도 남는지는 공개된 분석 자료가 없어서, 남아 있으면 쓰되 없다고 해서 파일이 없었다고 보지 않습니다.

### 휴지통을 읽을 때

Command-Delete 로 휴지통에 넣은 항목은 "되돌려 놓기 (Put Back)"로 복원되고, Control-클릭 뒤 "즉시 삭제"는 휴지통을 거치지 않습니다. 파인더 설정의 고급 탭에서 "30일 후 휴지통에서 항목 제거"를 켤 수 있고, 아이클라우드 드라이브 항목은 이 설정과 관계없이 30일 뒤 비워집니다 [3]. mac_apt 는 `.DS_Store` 레코드와 `.Trash` 안의 실제 항목을 이름으로 맞추는데, macOS 26.5.1 에서는 `.DS_Store` 에 레코드가 없는 휴지통 파일도 있습니다 [1]. `.DS_Store` 의 `modD`·`moDD` 시각은 형식 문서가 1904 기준 1/65536초 값으로 설명하고 mac_apt 는 리틀엔디언 double 맥 절대 시각으로 읽어서 해석이 엇갈립니다 [1][2]. 휴지통에 넣은 시각을 곧바로 담는 값과 외장 볼륨의 휴지통 위치는 공개된 분석 자료가 없어 검체에서 확인합니다.

### 앱 데이터베이스 안에 남는 것

APFS 는 객체를 제자리에서 고치지 않고 새 위치에 쓰고 [13], SQLite 는 지운 행이 차지하던 공간을 freelist·freeblock 으로 돌리고 최근 변경을 WAL 파일에 따로 씁니다 [11][12]. SQLite 의 `secure_delete` 는 보통 기본값이 꺼져 있고, 켜져 있으면 지운 내용을 0으로 덮습니다 [12]. 그래서 메시지·브라우저·메모 같은 앱의 DB에서 지운 행은 파일 삭제보다 되찾을 가능성이 높은 편입니다.

## 분석 흐름

1. 조사 대상 파일의 이름이나 경로 단서를 정하고, 휴지통과 그 `.DS_Store` 에서 원래 이름과 위치를 찾습니다.
2. 파일 시스템 이벤트에서 같은 경로의 Removed·Renamed 레코드를 찾습니다. 휴지통으로 옮긴 파일은 지우기가 아니라 이름 바꾸기로 보일 수 있어서, `~/.Trash/` 로 옮겨 간 Renamed 레코드도 함께 봅니다. 레코드에는 시각 칸이 없어서 이벤트 ID 의 순서와 다른 흔적의 시각으로 시점을 좁힙니다 [4].
3. 빠른 보기 섬네일 캐시, 최근 항목, 앱 저장 상태에서 같은 이름이나 inode 를 찾아 파일이 있었다는 근거를 더합니다. 암호화 컨테이너 안에 있던 파일도 캐시에 섬네일이 남을 수 있습니다 [8].
4. 스냅숏과 옛 체크포인트를 열어 지우기 전 시점에 파일이 있었는지 확인하고, 있으면 그 시점의 내용을 확보합니다.
5. 파일이 앱 DB 안의 기록이라면 SQLite 빈 공간과 WAL 에서 지운 행을 찾습니다.
6. 셸 기록의 `rm` 명령, 격리 이벤트 DB의 받은 기록, 바이옴의 상태 3 기록으로 앞뒤 사정을 보강합니다.
7. 모든 시각을 한 [타임라인](../../03-techniques/analysis/timeline/index.md)에 올려 파일이 마지막으로 존재한 시점과 사라진 시점 사이를 좁힙니다.

## 흔한 오판

- **휴지통 `.DS_Store` 에 레코드가 없으면 휴지통을 거치지 않았다고 보는 경우.** 레코드 없이 휴지통에 들어 있는 파일도 있습니다(macOS 26.5.1) [1].
- **`rm -P` 로 지웠으니 덮어썼다고 보는 경우.** 지금 macOS 의 `rm -P` 는 효과가 없고 덮어쓰지 않습니다 [17]. 반대로 덮어쓰지 않았다고 해서 SSD 블록이 남아 있다고 보지도 않습니다. TRIM 과 상시 암호화가 따로 작용합니다.
- **문서 버전이 남아 있으리라 기대하는 경우.** 원본 파일을 지우면 그 문서의 버전도 사라지고, mac_apt 기준으로 고아 조각에서 내용이 나올 수 있을 뿐입니다 [9][10].
- **파일 시스템 이벤트에 기록이 비어 있으면 아무 일도 없었다고 보는 경우.** 이벤트 기록은 root 권한으로 지정한 ID 이전까지 지울 수 있고, 볼륨의 이벤트 기록 UUID 가 바뀌었거나 이벤트 ID 가 이전보다 낮으면 복원·되돌림·삭제가 있었을 수 있습니다 [6]. 이 경우는 [증거를 없애려 했나](anti-forensics/index.md)의 방법으로 따로 봅니다.
- **섬네일이 있으면 사용자가 그 파일을 열었다고 보는 경우.** 섬네일은 폴더를 보기만 해도 생길 수 있어서 [8], 파일이 있었다는 근거로만 씁니다.

## 보고서 문장 예

> 사용자 ○○의 `~/.Trash/.DS_Store` 에 원래 이름 "○○.xlsx", 원래 위치 "○○" 인 레코드가 있고, 휴지통 폴더에는 같은 이름의 파일이 없습니다. 파일 시스템 이벤트에는 같은 경로에 Removed 플래그가 붙은 레코드가 있고, ○○○○년 ○월 ○일(UTC로 바꾼 날짜)에 만든 APFS 스냅숏에는 이 파일이 남아 있습니다. 이 기록들로 파일이 이 맥에 있었고 이후 지워졌다는 점은 확인할 수 있지만, 누가 지웠는지와 정확한 삭제 시각은 정할 수 없습니다.

## 함께 볼 페이지

- [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md) — 스냅숏·체크포인트·SQLite 잔재 복구 방법
- [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md) — 두 시점을 비교하는 법
- [휴지통 (.Trash)](../../02-artifacts/file-folder-usage/trash.md) — 휴지통 구조
- [증거를 없애려 했나 (Anti-Forensics)](anti-forensics/index.md) — 흔적 지우기 동작 찾기
- [이 파일을 누가 언제 열었나 (File Access)](file-access.md) — 지우기 전의 사용 흔적

## 참고 문헌

1. mac_apt `plugins/trash.py` (TRASH 1.0, Yogesh Khatri) — https://github.com/ydkhatri/mac_apt/blob/master/plugins/trash.py
2. Wim Lewis, "DSStoreFormat" (Mac::Finder::DSStore) — https://metacpan.org/dist/Mac-Finder-DSStore/view/DSStoreFormat.pod
3. Apple 지원, "Delete files and folders on Mac" — https://support.apple.com/guide/mac-help/delete-files-and-folders-on-mac-mchlp1093/mac
4. libyal dtformats — MacOS File System Events Disk Log Stream format — https://github.com/libyal/dtformats/blob/main/documentation/MacOS%20File%20System%20Events%20Disk%20Log%20Stream%20format.asciidoc
5. FSEventsParser 4.1 (Nicole Ibrahim) — https://raw.githubusercontent.com/dlcowen/FSEventsParser/master/FSEParser_V4.1.py
6. Apple, File System Events Programming Guide — Using the File System Events API — https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/FSEvents_ProgGuide/UsingtheFSEventsFramework/UsingtheFSEventsFramework.html
7. mac_apt QuickLook 플러그인 quicklook.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/quicklook.py
8. Patrick Wardle, "Cache Me Outside: apple's 'quicklook' cache may leak encrypted data" (Objective-See, 2018-06-15) — https://objective-see.org/blog/blog_0x30.html
9. mac_apt `plugins/documentrevisions.py` — https://github.com/ydkhatri/mac_apt/blob/master/plugins/documentrevisions.py
10. The Eclectic Light Company, "Managing macOS versioning and the DocumentRevisions-V100 folder" (2025-09-08) — https://eclecticlight.co/2025/09/08/managing-macos-versioning-and-the-documentrevisions-v100-folder/
11. SQLite, Database File Format — https://www.sqlite.org/fileformat2.html , SQLite, Write-Ahead Logging — https://www.sqlite.org/wal.html
12. SQLite, Pragma statements — https://www.sqlite.org/pragma.html
13. Apple, Apple File System Reference (2020-06-22) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
14. Apple, Apple Platform Security (2026년 8월) — https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf
15. Apple, Apple File System Guide — Frequently Asked Questions (2018-06-04) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/FAQ/FAQ.html
16. The Eclectic Light Company, "What can you do with Time Machine backups on APFS?" (2022-07-19) — https://eclecticlight.co/2022/07/19/what-can-you-do-with-time-machine-backups-on-apfs/
17. SS64 — macOS `rm` 명령 — https://ss64.com/mac/rm.html
18. ccl-segb (CCL Forensics, Alex Caithness) — https://github.com/cclgroupltd/ccl-segb
