---
title: "SQLite 데이터베이스"
parent: "기반 · 데이터 저장 형식"
nav_order: 170
has_children: true
has_toc: false
---

# SQLite 데이터베이스 (SQLite)

SQLite 데이터베이스는 표와 인덱스를 B-트리 페이지에 담은 파일 하나와, 그 옆에 붙는 저널·WAL 파일로 이루어진 저장 형식이고, 현재 행뿐 아니라 지운 레코드와 과거 버전의 페이지까지 파일 안팎에 남을 수 있습니다 [1][2].

## 왜 중요한가

프로그램 실행 흔적을 담은 knowledgeC.db처럼 macOS의 기록 가운데 SQLite 파일로 된 것이 있고 [4], 이런 DB에서는 SQL로 현재 행을 조회하는 데 그치지 않고 빈 페이지와 빈 공간, 저널·WAL까지 살펴봅니다. 프리리스트로 넘어간 리프 페이지를 SQLite가 읽지도 쓰지도 않고 [1], WAL에는 같은 페이지의 여러 버전이 남기 때문입니다 [2].

한편 다루는 방법에 따라 증거가 바뀌기 쉬운 형식이기도 합니다. DB를 여는 것만으로 핫 저널이 롤백되거나 [1] WAL이 DB 파일로 합쳐지고 지워질 수 있어서 [2], 수집과 열기 순서를 먼저 정해 두어야 합니다. 이 형식은 OS와 상관없이 같아서 [1] 윈도우나 다른 OS에서 익힌 SQLite 분석 방법을 그대로 쓸 수 있습니다.

## 한눈에 보기

| 파일 | 위치 | macOS 버전 | 알려 주는 것 |
|---|---|---|---|
| DB 본 파일 | 앱마다 다름. 파일 첫 16바이트가 `SQLite format 3\000` [1] | 형식 자체는 버전과 무관 [1] | 표·인덱스의 현재 내용, 프리리스트와 프리블록에 남은 지운 레코드 |
| `-journal` | DB와 같은 디렉터리 [1] | — | 롤백 저널. 트랜잭션 전의 페이지 원본 |
| `-wal` | DB와 같은 디렉터리 [1] | Core Data 저장소는 OS X 10.9 Mavericks부터 WAL이 기본 [3] | 아직 DB 파일로 옮기지 않은 페이지와 그 과거 버전 |
| `-shm` | DB와 같은 디렉터리 [1] | — | WAL 인덱스. 복구에는 필요 없음 |

macOS 10.15 Catalina 이후 버전마다 SQLite 저장 방식이나 기본 저널 방식이 바뀌었다는 공개 자료는 없습니다. macOS에 들어 있는 SQLite의 버전과 컴파일 옵션은 실제 기기에서 확인합니다.

## 읽는 순서

1. [페이지와 레코드 (B-tree·Record)](b-tree-record.md) — 100바이트 DB 헤더와 B-트리 페이지 헤더, 셀과 레코드의 직렬 타입을 오프셋 표와 헥스 예시로 따라갑니다.
2. [WAL과 저널 (WAL·Journal)](wal-journal.md) — 롤백 저널과 WAL, WAL 인덱스의 구조와 체크포인트, 증거를 열 때 바뀔 수 있는 부분을 다룹니다.
3. [지운 레코드 되살리기 (Freelist·Freeblock)](freelist-freeblock.md) — 프리리스트와 프리블록에 지운 레코드가 남는 방식, 남는 양을 정하는 설정, 공개 복구 도구와 결과 해석을 정리합니다.
4. [Core Data 저장소 (Core Data)](core-data.md) — Core Data가 만든 SQLite 저장소의 저널 방식과 저장소 밖 파일, 표 이름과 날짜 열을 읽을 때 챙길 점을 다룹니다.

## 함께 볼 페이지

- [속성 목록 파일 (Property List)](../plist/index.md) — SQLite와 함께 macOS 기록을 담는 다른 저장 형식
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../value-decoding/mac-time-values.md) — DB 열의 시각 기준을 가려낼 때
- [KnowledgeC (knowledgeC.db)](../../../02-artifacts/execution/knowledgec/index.md) — Core Data 기반 SQLite DB의 예
- [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md) — DB와 딸린 파일을 함께 확보할 때
- [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md) — 지워진 DB 파일이나 저널 파일을 파일 시스템에서 찾을 때
- [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md) — 복구 도구의 결과를 손으로 푼 결과와 맞춰 볼 때
- [지운 파일의 흔적 찾기 (Deleted File Traces)](../../../04-scenarios/activity/deleted-file-traces.md)

## 참고 문헌

1. SQLite, Database File Format — https://www.sqlite.org/fileformat.html
2. SQLite, Write-Ahead Logging — https://www.sqlite.org/wal.html
3. Apple Technical Q&A QA1809, New default journaling mode for Core Data SQLite stores in iOS 7 and OS X Mavericks — https://developer.apple.com/library/archive/qa/qa1809/_index.html
4. Sarah Edwards (mac4n6), Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
