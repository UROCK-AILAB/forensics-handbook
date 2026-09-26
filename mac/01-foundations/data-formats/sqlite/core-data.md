---
title: "Core Data 저장소"
parent: "SQLite 데이터베이스"
grand_parent: "기반 · 데이터 저장 형식"
nav_order: 210
---

# Core Data 저장소 (Core Data)

Core Data의 SQLite 저장소 (NSSQLiteStoreType)는 보통의 SQLite 파일이라서 페이지·레코드 구조를 그대로 읽을 수 있지만, OS X 10.9 Mavericks부터 WAL을 기본으로 쓰고 [1], 큰 이진 값이 저장소 파일 밖으로 빠질 수 있으며 [2], 날짜 칸이 2001년 기준 초로 적히는 예가 있다는 점 [3][4]을 따로 챙겨야 합니다.

## 이 형식을 쓰는 아티팩트

프로그램 실행 흔적을 담은 knowledgeC.db가 Core Data 기반 SQLite DB이고 [4], 표와 칸의 뜻은 [KnowledgeC (knowledgeC.db)](../../../02-artifacts/execution/knowledgec/index.md)에서 다룹니다. 이 페이지는 특정 DB가 아니라 Core Data 저장소라면 공통으로 챙길 점을 모읍니다.

## 저널 방식

iOS 7과 OS X 10.9 Mavericks부터 Core Data SQLite 저장소의 기본 저널 방식은 WAL입니다 [1].

| macOS 버전 | Core Data SQLite 저장소의 기본 저널 방식 |
|---|---|
| OS X 10.9 Mavericks 이후 | WAL [1] |
| macOS 10.15 Catalina 이후 버전별 차이 | 바뀌었다는 공개 자료 없음 |

앱은 `NSSQLitePragmasOption` 에 `journal_mode` 를 `DELETE` 로 넘겨 롤백 저널로 되돌릴 수 있어서 [1], 모든 Core Data 저장소가 WAL이라고 단정하지 않고 DB 헤더 18·19번 바이트로 확인합니다. 헤더 칸은 [페이지와 레코드 (B-tree·Record)](b-tree-record.md)에, WAL 파일 구조는 [WAL과 저널 (WAL·Journal)](wal-journal.md)에 있습니다.

저장소를 복사할 때 본 파일만 복사하고 `-wal` 파일을 빼면 데이터가 빠지거나 어긋나고, `NSObjectInaccessibleException` 이나 "unable to open database file" 오류가 날 수 있습니다 [1]. 그래서 증거를 수집할 때는 `-wal` 과 `-shm` 을 본 파일과 함께 확보합니다.

## 저장소 밖에 놓이는 값

속성의 `allowsExternalBinaryDataStorage` 가 true이면 그 속성 값이 저장소 파일이 아닌 별도 파일에 저장될 수 있고, macOS 10.7 이상에서 쓸 수 있는 설정입니다 [2]. 외부 파일이 놓이는 폴더 이름과 DB 안에서 그 파일을 가리키는 방식은 검체에서 확인해야 합니다. 그래서 Core Data 저장소를 수집할 때는 DB 파일과 딸린 파일만 골라 오지 않고 저장소가 들어 있는 폴더를 통째로 확보해 두고, DB 칸에서 기대한 이진 값이 보이지 않으면 폴더 안의 다른 파일과 맞춰 봅니다.

## 표와 칸 이름

knowledgeC.db에는 ZOBJECT, ZSOURCE, ZSTRUCTUREDMETADATA 같은 표와 ZCREATIONDATE 같은 칸이 있고, 표를 서로 묶을 때 Z_PK와 Z_ENT 칸을 씁니다 [4]. 표와 칸 이름 앞에 Z가 붙는 모양은 knowledgeC.db의 예이고, 이 이름 규칙이나 Z_PK·Z_ENT 칸의 정확한 뜻을 설명한 Apple 공개 문서는 없습니다.

낯선 Core Data 저장소를 처음 열 때는 이름으로 짐작하기보다 작업 사본에서 `sqlite_schema` 를 조회해 실제 표 목록과 `CREATE` 문부터 확인합니다.

```sql
SELECT name, sql FROM sqlite_schema WHERE type = 'table';
```

셸 버전에 따라 `sqlite_schema` 라는 이름이 통하지 않으면 같은 표의 다른 이름인 `sqlite_master` 로 바꿔 씁니다.

## 날짜 칸

Core Data 계열 DB의 날짜 칸은 2001-01-01 00:00:00 UTC부터 센 초, 곧 맥 절대 시각 (Mac Absolute Time)으로 적힙니다(knowledgeC.db 기준 [4]). `NSTimeIntervalSince1970` 은 유닉스 기준 시각(1970-01-01 00:00:00 UTC)부터 Foundation 기준일(2001-01-01 00:00:00 UTC)까지의 초이고 [3], 그 값 978307200을 더하면 유닉스 시각이 됩니다 [4].

```sql
-- [4]에 실린 예. 'LOCALTIME' 을 붙이면 조회하는 컴퓨터의 시간대로 바뀐다
SELECT datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'UNIXEPOCH', 'LOCALTIME') FROM ZOBJECT;

-- UTC 그대로 보려면
SELECT datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'UNIXEPOCH') FROM ZOBJECT;
```

저장된 값은 UTC 기준이라서 보고서에는 UTC로 뽑고 현지 시간대를 따로 밝히는 편이 헷갈리지 않습니다. 모든 날짜 칸이 이 기준을 쓴다고 단정할 수 없으니 칸마다 값의 크기를 보고 기준을 확인하고, 여러 시각 기준을 구별하는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../value-decoding/mac-time-values.md)에서 다룹니다.

## 함정

`-wal` 없이 본 파일만 열면 데이터가 빠지거나 어긋난 채 보일 수 있고 [1], 오류 없이 열리더라도 최신 상태라고 볼 수 없습니다.

Z_PK·Z_ENT 같은 칸 이름을 보고 모든 Core Data 저장소가 같은 표 구성이라고 가정하지 않습니다. 표 구성은 저장소마다 다를 수 있으니 다른 저장소는 `sqlite_schema` 로 구성을 확인한 뒤에 묶습니다.

저장소 밖 파일에 들어간 값은 DB만 복사해서는 나오지 않고 [2], 지운 레코드를 되살렸을 때도 그 레코드가 가리키던 외부 파일이 남아 있는지는 따로 확인해야 합니다. 지운 레코드를 되살리는 방법은 [지운 레코드 되살리기 (Freelist·Freeblock)](freelist-freeblock.md)에 있습니다.

## 참고 문헌

1. Apple Technical Q&A QA1809, New default journaling mode for Core Data SQLite stores in iOS 7 and OS X Mavericks — https://developer.apple.com/library/archive/qa/qa1809/_index.html
2. Apple Developer, NSAttributeDescription.allowsExternalBinaryDataStorage — https://developer.apple.com/tutorials/data/documentation/coredata/nsattributedescription/allowsexternalbinarydatastorage.json
3. Apple Developer, NSTimeIntervalSince1970 — https://developer.apple.com/tutorials/data/documentation/foundation/nstimeintervalsince1970.json
4. Sarah Edwards (mac4n6), Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
