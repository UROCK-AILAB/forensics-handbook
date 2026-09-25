---
title: "삭제 데이터 복구"
parent: "기법 · 분석"
nav_order: 2120
has_children: true
has_toc: false
---

# 삭제 데이터 복구 (Data Recovery)

macOS 에서 지운 데이터가 남을 수 있는 네 층, 곧 APFS 파일 시스템, 앱의 SQLite 데이터베이스, 파일 시스템을 거치지 않는 원시 영역, 그리고 이 모두를 지우는 저장 장치 쪽 동작을 묶어 안내합니다.

## 왜 중요한가

조사에서 중요한 파일이나 대화 기록이 지워져 있을 때, 무엇을 되찾을 수 있고 무엇은 되찾을 수 없는지를 먼저 가려야 시간을 헛되이 쓰지 않고 보고서에도 한계를 정확히 적을 수 있습니다. APFS 는 디스크의 객체를 제자리에서 고치지 않고 늘 새 위치에 써서 [1] 옛 메타데이터가 한동안 남을 수 있고, SQLite 는 지운 내용을 기본으로 0 으로 덮지 않아서 [2] 파일 안에 지운 레코드가 남을 수 있습니다.

반대로 APFS 는 파일을 지우거나 빈 공간을 회수할 때 TRIM 을 비동기로 보내고 [3], Apple 실리콘·T2 Mac 은 FileVault 를 켜지 않아도 볼륨이 암호화돼 있습니다 [4]. 그래서 요즘 Mac 내장 SSD 에서는 지운 파일의 블록을 통째로 되살리기보다 스냅샷, 옛 체크포인트, SQLite 내부 잔재처럼 살아 있는 볼륨 안에 남은 흔적을 찾는 편이 더 현실적입니다.

## 한눈에 보기

| 층 | 보는 곳 | 조건·버전 | 알려 주는 것 |
|---|---|---|---|
| APFS 파일 시스템 | 체크포인트 설명 영역의 옛 컨테이너 수퍼블록, 오브젝트 맵, 스냅샷 | 명세는 2020-06-22 판 기준 | 지운 파일의 이름·크기·시각이 어느 시점까지 있었는지, 조건이 맞으면 내용 |
| SQLite 데이터베이스 | freelist 페이지, 페이지 안 freeblock, -wal 파일, 롤백 저널 | secure_delete·auto_vacuum 설정에 따라 다름 | 앱 DB 에서 지운 레코드의 값, WAL 세대별 옛 페이지 |
| 원시 영역 | 복호된 볼륨의 빈 공간, 암호화되지 않은 외장 매체 | 내장 저장소는 복호가 먼저 | 이름 없는 파일과 조각, APFS·SQLite 구조 조각 |
| 저장 장치 동작 | TRIM, 상시 암호화, 키 삭제 | Apple 실리콘·T2 는 상시 암호화, macOS 26.4 이후 FileVault 기본 켜짐 | 복구를 기대할 수 있는지와 못 하는 이유 |

## 읽는 순서

1. [APFS에서 지운 파일 (APFS)](apfs-deleted-files.md) — 옛 체크포인트와 스냅샷, 오브젝트 맵을 따라 이전 시점의 파일 시스템 트리에서 지운 파일을 찾습니다.
2. [SQLite 레코드 되살리기 (SQLite)](sqlite-records.md) — 살아 있는 DB 파일 안의 freelist·freeblock 과 WAL·롤백 저널에서 지운 레코드를 읽습니다.
3. [카빙 (Carving)](carving.md) — 파일 시스템 메타데이터 없이 원시 영역에서 시그니처와 구조로 파일·조각을 꺼내고, 이 방법이 통하는 조건을 봅니다.
4. [트림과 복구 한계 (TRIM)](trim.md) — TRIM·상시 암호화·키 삭제가 복구를 어떻게 막는지와 그 뒤에도 남는 기회를 정리합니다.

처음 보는 사건이라면 4번으로 기대치부터 정하고 1·2번으로 넘어가며, 3번은 앞의 방법으로 찾지 못한 것을 찾는 마지막 단계로 둡니다.

## 함께 볼 페이지

지운 파일을 조사 질문에서 출발해 따라가려면 [지운 파일의 흔적 찾기 (Deleted File Traces)](../../../04-scenarios/activity/deleted-file-traces.md) 와 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md) 시나리오를 봅니다. 아직 지우지 않은 사본은 [휴지통 (.Trash)](../../../02-artifacts/file-folder-usage/trash.md), [문서 버전 (DocumentRevisions-V100)](../../../02-artifacts/file-folder-usage/document-revisions.md), [타임 머신 (Time Machine)](../../../02-artifacts/filesystem/time-machine/index.md), [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../snapshot-diff.md) 에서 찾고, 삭제 시각은 [파일 시스템 이벤트 (FSEvents)](../../../02-artifacts/filesystem/fsevents/index.md) 로 좁힙니다.

저장 구조는 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md) 와 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) 에, 암호화된 볼륨을 다루는 방법은 [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md) 와 [암호화된 증거 다루기 (Encrypted Evidence)](../encrypted-evidence/index.md) 에, 이미지를 뜨는 방법은 [맥 증거 확보 (Acquisition)](../../process-acquisition/evidence-acquisition/index.md) 에 있습니다.

## 참고 문헌

1. Apple, Apple File System Reference (2020-06-22) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
2. SQLite, Pragma statements (secure_delete, auto_vacuum, freelist_count) — https://www.sqlite.org/pragma.html
3. Apple, Apple File System Guide — Frequently Asked Questions (2018-06-04) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/FAQ/FAQ.html
4. Apple, Apple Platform Security (2026년 8월) — https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf
