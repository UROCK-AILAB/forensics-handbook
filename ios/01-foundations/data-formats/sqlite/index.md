---
title: "SQLite 데이터베이스"
parent: "기반 · 데이터 저장 형식"
nav_order: 90
has_children: true
has_toc: false
---

# SQLite 데이터베이스 (SQLite)

iOS 의 메시지·메모·사진 보관함 같은 주요 기록은 SQLite 파일에 들어 있고, 이 허브는 SQLite 파일을 SQL 결과 너머 바이트 수준까지 읽는 데 필요한 네 페이지로 안내합니다.

## 왜 중요한가

관찰한 로컬 백업에서 Apple 영역의 DB 파일만 131개였고, 백업 파일 목록인 `Manifest.db` 도 WAL 곁 파일을 둔 SQLite 였습니다.

SQL 질의는 커밋된 살아 있는 행만 보여 주고, 본 파일만 따로 열면 `-wal` 에 있는 최신 변경마저 빠집니다. 지운 행의 흔적은 페이지 안 빈 블록(freeblock)·빈 페이지 목록(freelist)·할당되지 않은 영역에 남을 수 있어서, 파일 구조를 알아야 이 부분까지 읽을 수 있습니다. 도구 결과만 믿기도 어려운데, 공개 시험용 SQLite 포렌식 말뭉치(Nemetz 외, 2018)는 DB 77개로 되어 있고 그중 27개에 지운 레코드가 들어 있는데, 2018년에 도구 6종을 비교했을 때 77개를 모두 읽은 도구는 없었고 가장 나은 도구가 66개를 읽었습니다.

SQLite 파일인지는 확장자가 아니라 파일 앞 16바이트로 가립니다. 관찰한 백업에는 `.sqlite`, `.db`, `.sqlitedb` 처럼 확장자가 여러 가지였고(예: `HomeDomain :: Library/com.apple.itunesstored/itunesstored_private.sqlitedb`), SQLite 파일은 확장자와 상관없이 `SQLite format 3\000`(헥스 `53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00`)으로 시작합니다.

## 한눈에 보기

SQLite 파일 형식은 iOS 와 상관없는 공통 규격이라, iOS 버전에 따라 달라지는 점은 확인하지 못했습니다. iOS 에 들어 있는 SQLite 의 버전과 컴파일 옵션(secure_delete·auto_vacuum 기본값 등)도 확인하지 못했습니다.

| 파일 | 위치 | iOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 본 DB 파일 | 앱·시스템 영역 곳곳(예: `HomeDomain :: Library/SMS/sms.db`) | 공통 규격 | 커밋된 표와 행, 빈 공간에 남은 지운 레코드 |
| `-wal` | 본 파일과 같은 폴더 | Core Data 저장소는 iOS 7 부터 기본 WAL | 본 파일에 아직 합쳐지지 않은 변경, 덮어쓰이지 않은 옛 페이지 |
| `-shm` | 본 파일과 같은 폴더 | 위와 같음 | WAL 에서 페이지를 찾는 색인 |
| `-journal` | 본 파일과 같은 폴더 | 롤백 저널 방식 DB | 바뀌기 전 원래 페이지 |
| Core Data 저장소 | 예: `AppDomainGroup-group.com.apple.notes :: NoteStore.sqlite` | 관찰 DB 131개 중 52개(iOS 27.0) | `Z_` 관리 표로 엔터티와 행 관계, 이력 추적 표로 변경 기록 |
| `Manifest.db` | 로컬 백업 폴더 최상위, `Manifest.db-wal`·`Manifest.db-shm` 과 함께 | 관찰(iOS 27.0) | 백업에 든 파일 목록(`Files`·`Properties` 표) |

`Manifest.db` 의 표와 칸은 [로컬 백업](../../backups/local-backup/index.md)에서 다룹니다. Apple 은 본 파일만 복사하면 데이터가 빠지거나 어긋날 수 있다고 적고 본 파일과 `-wal` 을 한 묶음으로 다루라고 권하는데, 증거를 옮길 때도 곁 파일을 함께 옮깁니다.

## 읽는 순서

1. [페이지와 레코드 (B-tree·Record)](b-tree-record.md) — 100바이트 파일 헤더, b-tree 페이지, 셀, varint, 레코드의 serial type 을 헥스로 따라갑니다.
2. [WAL과 저널 (WAL·Journal)](wal-journal.md) — 롤백 저널과 WAL 의 구조, 체크포인트, 곁 파일을 바꾸지 않고 읽는 순서를 다룹니다.
3. [지운 레코드 되살리기 (Freelist·Freeblock)](freelist-freeblock.md) — 지운 행이 남는 자리와 복원이 어디까지 되는지, 도구마다 결과가 다른 까닭을 다룹니다.
4. [Core Data 저장소 (Core Data)](core-data.md) — `Z_PK`·`Z_ENT`·`Z_OPT` 칸과 관리 표, 이력 추적 표, Mac 절대 시각을 다룹니다.

## 함께 볼 페이지

- [시각 값 (Mac 절대 시각·Unix·기타)](../../value-decoding/time-values.md) — SQLite 에는 날짜 자료형이 없어 칸마다 기준을 따로 확인합니다.
- [속성 목록 파일 (plist·NSKeyedArchiver)](../plist.md) — Core Data 의 `Z_PLIST` 처럼 plist 를 담은 칸을 풀 때 씁니다.
- [로컬 백업](../../backups/local-backup/index.md) — 백업 안에서 DB 파일을 찾는 법
- [앱 데이터 분석](../../../03-techniques/analysis/app-data-analysis/index.md), [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md), [도구 검증](../../../03-techniques/reporting/tool-validation.md)
- SQLite 를 쓰는 대표 아티팩트: [메시지](../../../02-artifacts/communications/messages/index.md), [메모](../../../02-artifacts/mail-cloud/notes.md), [사진 보관함](../../../02-artifacts/media/photos/index.md)

## 참고 문헌

1. SQLite, "Database File Format" — https://www.sqlite.org/fileformat2.html
2. Apple, Technical Q&A QA1809 "New default journaling mode for Core Data SQLite stores in iOS 7 and OS X Mavericks" — https://developer.apple.com/library/archive/qa/qa1809/_index.html
3. Dirk Pawlaszczyk, Christian Hummert, "Making the Invisible Visible – Techniques for Recovering Deleted SQLite Data Records", International Journal of Cyber Forensics and Advanced Threat Investigations 1(1-3), 27-41, 2021 — https://conceptechint.net/index.php/CFATI/article/download/17/6
