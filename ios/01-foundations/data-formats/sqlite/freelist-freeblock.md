---
title: "지운 레코드 되살리기"
parent: "SQLite 데이터베이스"
grand_parent: "기반 · 데이터 저장 형식"
nav_order: 120
---

# 지운 레코드 되살리기 (Freelist·Freeblock)

SQLite 는 행을 지워도 바이트를 곧바로 없애지 않아서, 페이지 안의 빈 블록(freeblock), 빈 페이지 목록(freelist), 할당되지 않은 영역에 지운 레코드가 남을 수 있습니다. 이 페이지는 그 자리를 찾아 읽는 방법과, 되살린 결과를 어디까지 믿을 수 있는지를 다룹니다.

## 이 형식을 쓰는 아티팩트

iOS 의 SQLite 아티팩트라면 어느 것이든 이 방법을 쓸 수 있고, 페이지·셀·레코드 구조는 [페이지와 레코드](b-tree-record.md)를 먼저 보면 됩니다. iOS 의 `sms.db` 같은 DB 에서 얼마나 되살아나는지와 iOS 버전별 차이는 실제 DB 로 확인해야 합니다. 지운 대화·사진을 찾는 조사 전체 흐름은 [지운 대화와 사진 찾기](../../../04-scenarios/activity/deleted-content.md)와 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.

앱이 직접 만든 삭제 기록 표는 SQLite 빈 공간과 다른 층입니다. 예를 들어 `sms.db` 에는 `deleted_messages`(`ROWID`, `guid`)와 `chat_recoverable_message_join`(`chat_id`, `message_id`, `delete_date`, `ck_sync_state`) 같은 표가 있고, 이런 표는 SQL 로 그대로 읽히는 유효한 행입니다. 두 표의 열이 무엇을 뜻하는지는 [메시지](../../../02-artifacts/communications/messages/index.md) 페이지에서 다룹니다.

## 구조 — 지운 데이터가 남는 자리

유효한 레코드, 페이지 헤더, 셀 포인터 배열이 아닌 곳이라면 어디든 지운 흔적이 있을 수 있습니다.

| 자리 | 찾는 법 | 남는 것 |
|---|---|---|
| freeblock | 페이지 헤더 오프셋 1 에서 시작해 연결을 따라간다 | 셀 앞 4바이트를 뺀 나머지 |
| 조각(fragment) | 페이지 헤더 오프셋 7 에 합계만 있다 | 1~3바이트 조각 |
| 할당되지 않은 영역 | 셀 포인터 배열 끝부터 셀 내용 영역 시작까지 | 지운 레코드 조각 |
| freelist 페이지 | 파일 헤더 오프셋 32(첫 트렁크), 36(총수) | 통째로 비워진 페이지의 옛 내용 |
| WAL 프레임·롤백 저널 | [WAL과 저널](wal-journal.md) | 체크포인트 전·덮어쓰기 전 페이지, 변경 전 페이지 |

### freeblock

행을 지우면 셀 앞 4바이트가 freeblock 헤더로 덮입니다. 앞 2바이트는 다음 freeblock 의 위치이고 뒤 2바이트는 이 freeblock 의 길이(4바이트 헤더 포함)입니다. freeblock 은 최소 4바이트이고 위치가 커지는 순서로 연결되며, 마지막 freeblock 은 다음 위치가 0 입니다. 1~3바이트짜리 빈 조각은 freeblock 이 되지 못하고 페이지 헤더 오프셋 7 에 합계만 남는데, 정상 페이지라면 이 합계가 60바이트를 넘지 않습니다.

덮이는 4바이트에는 셀의 페이로드 길이, rowid, 레코드 헤더 길이, 앞쪽 serial type 이 들어 있습니다. varint 길이가 셀마다 달라서 덮이는 필드 수도 그때그때 다르고, 복원이 어디까지 되는지도 여기에 달려 있습니다.

| 덮인 범위 | 복원 |
|---|---|
| 페이로드 길이와 rowid 만 | 레코드 내용은 늘 완전히 복원된다(원래 rowid 는 알 수 없다) |
| 레코드 헤더 길이까지 | 남은 헤더에서 추정할 수 있다 |
| 첫 열의 serial type 까지 | 어려워지고, 이웃 레코드나 스키마로 추정한다 |
| 그보다 더 | 자동 복원이 어렵다 |

### 할당되지 않은 영역

셀 포인터 배열 끝과 셀 내용 영역 시작 사이에도 지운 레코드 조각이 남을 수 있습니다. 마지막에 넣은 레코드를 지우면 셀 내용 영역의 시작 위치가 옮겨지면서 그 레코드가 이 영역에 들어가고, SQLite 가 페이지를 정리(조각 모음)할 때도 옛 내용이 이 영역으로 밀려납니다.

### freelist

통째로 빈 페이지는 freelist 에 들어갑니다. 파일 헤더 오프셋 32 가 첫 트렁크 페이지, 36 이 freelist 페이지 총수입니다. 트렁크 페이지는 4바이트 정수 배열로, 다음 트렁크 페이지 번호, 잎 포인터 수 L, 잎 페이지 번호 L 개가 차례로 들어 있습니다.

freelist 잎 페이지는 정보를 담지 않는 페이지라서, SQLite 는 입출력을 줄이려고 잎 페이지를 읽지도 쓰지도 않습니다[1]. 그래서 비워진 페이지의 옛 내용이 그대로 남을 수 있고, 잎 페이지의 옛 모습이 b-tree 페이지였다면 [페이지와 레코드](b-tree-record.md)의 방법으로 셀을 풀어 볼 수 있습니다.

### 복원 여지를 줄이는 설정

| 설정 | 동작 | 확인하는 곳 |
|---|---|---|
| auto_vacuum = NONE | 빈 페이지를 freelist 에 두고 다시 쓴다 | 파일 헤더 오프셋 52 가 0 |
| auto_vacuum = FULL | 커밋마다 freelist 페이지를 파일 끝으로 옮기고 잘라 낸다 | 오프셋 52 가 0 이 아니고 64 가 0 |
| auto_vacuum = INCREMENTAL | 정보만 저장하고 자동으로 정리하지 않는다 | 오프셋 52·64 가 0 이 아님 |
| secure_delete = 1 | 지운 내용을 0 으로 덮어쓴다 | 파일에 기록되지 않음 |
| secure_delete = FAST | 입출력이 늘지 않을 때만 덮어써서, b-tree 페이지의 옛 내용은 지우지만 freelist 페이지에는 흔적을 남긴다 | 파일에 기록되지 않음 |

auto_vacuum 을 NONE 에서 켜려면 표를 만들기 전이거나 VACUUM 을 실행해야 하고, FULL 로 켜져 있으면 빈 페이지를 파일 끝으로 모아 잘라 내서 freelist 쪽 복원 여지가 줄어듭니다. 이 설정은 페이지 단위로만 정리하니, 사용 중인 페이지 안의 freeblock 까지 지우지는 않습니다. secure_delete 기본값은 컴파일 옵션 `SQLITE_SECURE_DELETE` 로 정해지며 보통 꺼져 있습니다. iOS 시스템 SQLite 의 secure_delete·auto_vacuum 기본값과 컴파일 옵션은 공개된 자료가 없습니다.

## 읽는 법

### 헥스로 한 번 따라가기

아래 바이트는 규격을 보고 만든 예시입니다. [페이지와 레코드](b-tree-record.md)의 예시 페이지에서 rowid 7 인 셀(페이지 안 0x0ff8)을 지웠고, 셀 8바이트가 통째로 freeblock 이 되었다고 가정합니다.

```
지우기 전 0x0ff8:  06 07 03 01 11 05 68 69
지운 뒤   0x0ff8:  00 00 00 08 11 05 68 69
                   └ 다음 freeblock 0, 길이 8
페이지 헤더 오프셋 1:  0f f8   (첫 freeblock 위치)
```

앞 4바이트가 덮이면서 페이로드 길이(`06`), rowid(`07`), 헤더 길이(`03`), 첫 열의 serial type(`01`)이 사라졌고, 둘째 열의 serial type `11`(2바이트 TEXT)과 본문 `05 68 69` 는 남았습니다. 첫 열의 serial type 까지 덮였으니 위 표의 세 번째 경우에 해당하고, 이웃 셀(0x0ff0)의 헤더가 `03 01 11` 인 것을 근거로 "첫 열은 1바이트 정수 5, 둘째 열은 TEXT hi" 라고 추정합니다. 이 추정은 이웃 레코드가 같은 모양이라는 가정에 기댄 것이라, 보고서에는 추정이라고 적습니다.

### 절차

1. 본 파일과 곁 파일을 함께 복사하고 복사본만 엽니다.
2. 파일 헤더 오프셋 32·36·52·64 를 읽고, `sqlite3` 셸의 `PRAGMA freelist_count;` 와 `PRAGMA auto_vacuum;` 결과와 맞춰 봅니다.
3. 테이블 잎 페이지마다 페이지 헤더 오프셋 1 에서 freeblock 연결을 따라가고, 오프셋 7 의 조각 합계와, 셀 포인터 배열 끝부터 셀 내용 영역 시작까지의 할당되지 않은 영역을 살핍니다.
4. freelist 트렁크 페이지를 따라가 잎 페이지 번호를 모으고, 잎 페이지의 옛 내용을 b-tree 페이지처럼 풀어 봅니다.
5. WAL 프레임과 롤백 저널의 페이지도 같은 방법으로 풉니다.
6. 되살린 레코드의 serial type 순서가 어느 표의 열 순서와 맞는지 `sqlite_schema` 의 `sql` 과 비교해, 레코드가 어느 표의 것인지 정합니다.

## 포렌식에서 중요한 점

되살린 레코드로 알 수 있는 것은 "이 DB 에 언젠가 이 내용의 레코드가 있었다"까지입니다. freeblock·freelist 구조에는 시각 필드가 없어서 언제 지웠는지는 레코드 안의 시각 값이나 다른 아티팩트로 따로 맞춰야 하고, rowid 가 덮였다면 원래 rowid 도 알 수 없습니다.

`DROP` 으로 표를 통째로 지우면 freeblock 정보도 덮여서 셀 포인터로는 지운 레코드를 찾을 수 없습니다. 반대로 빈 공간에서 아무것도 나오지 않았다고 해서 지운 적이 없다고 말할 수는 없는데, auto_vacuum·secure_delete·덮어쓰기가 흔적을 없앨 수 있기 때문입니다. 지우기 흔적을 조사 전체에서 어떻게 해석하는지는 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

## 함정

오버플로 페이지가 지운 뒤 다른 용도(테이블 내부 페이지 0x05 등)로 다시 쓰이면, 되살린 레코드에 다른 데이터가 섞이는데도 도구가 이를 알아채지 못할 수 있습니다. 지운 페이지 일부가 새 표의 레코드로 덮여 한 페이지에 두 표의 레코드가 함께 보인 사례도 있어서, 절차 6번처럼 레코드마다 어느 표의 것인지 다시 확인해야 합니다.

secure_delete 는 파일 헤더에 기록되는 설정이 아니라서, 분석 컴퓨터에서 복사본을 열고 `PRAGMA secure_delete;` 를 실행하면 기기가 아니라 분석 컴퓨터 SQLite 의 값이 나옵니다.

도구마다 결과 차이가 큽니다. FQLite 를 만든 연구진의 2021년 시험(공개 시험용 말뭉치의 27개 DB, 지운 레코드 278개)에서 bring2lite 는 52.9% 를 되살렸고, FQLite 는 모두 되살렸습니다[3]. 한 도구의 결과만으로 "되살릴 것이 없다"고 결론 내리지 말고, [도구 검증](../../../03-techniques/reporting/tool-validation.md)의 방법으로 알려진 결과가 있는 DB 에 먼저 돌려 봅니다.

## 도구

공개 도구로는 위 비교에 나온 FQLite 와 bring2lite 가 있고, `sqlite3` 셸로 PRAGMA 값을, 헥스 편집기로 freeblock 과 freelist 페이지를 직접 확인합니다.

## 참고 문헌

1. SQLite, "Database File Format" — https://www.sqlite.org/fileformat2.html
2. SQLite, "Pragma statements supported by SQLite" — https://www.sqlite.org/pragma.html
3. Dirk Pawlaszczyk, Christian Hummert, "Making the Invisible Visible – Techniques for Recovering Deleted SQLite Data Records", International Journal of Cyber Forensics and Advanced Threat Investigations 1(1-3), 27-41, 2021 — https://conceptechint.net/index.php/CFATI/article/download/17/6
