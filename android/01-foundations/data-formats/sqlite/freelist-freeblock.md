---
title: "지운 레코드 되살리기"
parent: "SQLite 데이터베이스"
grand_parent: "기반 · 데이터 저장 형식"
nav_order: 180
---

# 지운 레코드 되살리기 (Freelist·Freeblock)

SQLite 에서 행을 지우면 셀 자리는 빈 조각이 되고 비워진 페이지는 빈 페이지 목록으로 들어가는데, 덮이기 전까지는 이 빈 자리에 옛 레코드가 남을 수 있습니다. 이 페이지는 빈 자리의 구조와 되살리는 순서, 그리고 Android 플랫폼 SQLite 가 기본으로 켜 둔 secure_delete 와 자동 정리가 결과를 어떻게 줄이는지를 다룹니다.

## 지운 내용이 남을 수 있는 자리

지운 데이터가 남을 수 있는 자리는 아래 다섯 곳입니다 [1].

| 자리 | 무엇이 남나 | 이 핸드북에서 다루는 곳 |
|---|---|---|
| freelist 잎 페이지 | 통째로 비워진 페이지의 옛 내용 | 이 페이지 |
| freeblock 과 fragment | 지운 셀의 뒷부분 | 이 페이지 |
| 셀 포인터 배열과 셀 내용 영역 사이 | 옛 셀 | 이 페이지 |
| WAL 의 옛 프레임 | 같은 페이지의 앞선 버전 | [WAL과 저널](wal-journal.md) |
| 롤백 저널의 페이지 기록 | 거래가 바꾸기 전 페이지 | [WAL과 저널](wal-journal.md) |

secure_delete 가 꺼져 있으면 지운 내용이 파일에 남습니다. 흔적을 없애려면 secure_delete 를 켜거나 VACUUM 을 해야 합니다 [2].

## freelist (빈 페이지 목록)

쓰지 않는 페이지는 빈 페이지 목록 (Freelist) 에 모입니다. 파일 머리 오프셋 32 에 첫 트렁크 페이지 번호가, 오프셋 36 에 freelist 페이지 총수가 있고, `PRAGMA freelist_count` 로도 빈 페이지 수를 볼 수 있습니다 [1][2].

freelist 는 트렁크 페이지 (Trunk Page) 를 사슬로 잇고, 트렁크 하나가 잎 페이지 (Leaf Page) 여러 개를 가리키는 구조입니다. 트렁크 페이지는 4바이트 빅엔디언 정수의 배열입니다 [1].

| 트렁크 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0 | 4 | 다음 트렁크 페이지 번호(마지막이면 0) |
| 4 | 4 | 이 트렁크에 딸린 잎 페이지 수 L |
| 8 | 4×L | 잎 페이지 번호들 |

새 SQLite 도 옛 버전과 맞추려고 트렁크 배열의 마지막 여섯 칸은 쓰지 않습니다 [1]. 잎 페이지에는 정해진 정보가 없고, SQLite 는 입출력을 줄이려고 잎 페이지를 읽지도 쓰지도 않습니다 [1]. 그래서 secure_delete 가 꺼진 DB 에서는 통째로 비워진 페이지의 옛 B-tree 내용이 잎 페이지에 그대로 남을 수 있고, 이 잎 페이지를 [페이지와 레코드](b-tree-record.md)의 방법대로 페이지 종류 바이트부터 다시 읽으면 옛 행이 나올 수 있습니다.

### 자동 정리 (auto_vacuum)

freelist 에 페이지가 얼마나 남는지는 auto_vacuum 설정에 달려 있습니다 [2].

| 값 | 이름 | 하는 일 |
|---|---|---|
| 0 | NONE (SQLite 기본) | 지워도 파일 크기가 줄지 않고, 빈 페이지는 freelist 에 들어가 다시 쓰임. VACUUM 을 하면 파일 전체를 새로 만듦 |
| 1 | FULL | 커밋마다 freelist 페이지를 파일 끝으로 옮기고 잘라냄. 페이지 안 조각 정리는 하지 않음 |
| 2 | INCREMENTAL | 정리에 필요한 정보는 저장하지만 `PRAGMA incremental_vacuum` 을 불러야 정리함 |

auto_vacuum 은 표를 만들기 전에만 NONE 에서 다른 값으로 바꿀 수 있습니다 [2]. 파일 하나가 어느 설정인지는 머리 오프셋 52 와 64 로 판별합니다. 오프셋 52 가 0 이면 NONE 이고, 0 이 아니면서 오프셋 64 가 0 이면 FULL, 오프셋 64 도 0 이 아니면 INCREMENTAL 입니다 [1]. FULL 인 DB 는 커밋 때마다 빈 페이지를 잘라내서 freelist 잎 페이지에서 건질 것이 적고, 잘려 나간 바이트는 파일 시스템 쪽에서 찾아야 합니다.

## freeblock 과 fragment (페이지 안의 빈 공간)

B-tree 페이지 안의 빈 공간 덩어리를 freeblock 이라고 합니다. freeblock 은 최소 4바이트이고, 앞 2바이트는 다음 freeblock 위치(마지막이면 0), 그다음 2바이트는 머리를 포함한 freeblock 크기입니다. 첫 freeblock 위치는 페이지 머리 오프셋 1 에 있습니다 [1].

fragment 는 셀 내용 영역 안에 떨어져 있는 1~3바이트짜리 빈 공간이고, 한 페이지의 조각 바이트 합계는 페이지 머리 오프셋 7 에 적힙니다. 정상 페이지에서 이 합계는 60 이하입니다 [1].

셀이 지워져 freeblock 이 되면 셀 앞 4바이트가 freeblock 머리로 덮입니다. 표 잎 셀의 앞부분은 페이로드 길이와 rowid, 레코드 머리라서, 되살린 레코드는 이 앞부분이 깨져 있을 수 있습니다 [1].

셀 포인터 배열 끝과 셀 내용 영역 시작 사이의 쓰지 않은 공간에도 옛 셀이 남을 수 있습니다 [1].

아래는 명세로 만든 예시이고, 실제 파일의 값이 아닙니다. [페이지와 레코드](b-tree-record.md)의 예시 셀(rowid 1, 열 값 `hi`·5)이 지워진 뒤 freeblock 이 된 모습입니다.

```
지우기 전   06 01 03 11 01 68 69 05
지운 뒤     00 00 00 08 01 68 69 05
            └─┬─┘ └─┬─┘
         다음 없음  크기 8
```

앞 4바이트가 freeblock 머리로 바뀌어서 페이로드 길이·rowid·레코드 머리 길이·첫 열의 직렬 타입이 사라졌습니다. 남은 `01 68 69 05` 만으로는 열 경계를 알 수 없어서, sqlite_schema 의 sql 열에서 표의 열 순서와 타입을 가져와 "문자열 한 열, 정수 한 열" 이라는 틀을 맞춰 보고서야 `hi` 와 5 를 읽을 수 있습니다. secure_delete 가 켜진 DB 라면 지운 셀 자리가 0 으로 덮여서 이런 흔적도 남지 않습니다.

## secure_delete 와 Android 플랫폼 SQLite

secure_delete 를 켜면 SQLite 는 지운 내용을 0 으로 덮습니다. 기본값은 컴파일 옵션 SQLITE_SECURE_DELETE 가 정하고, 보통은 꺼져 있습니다 [2]. 2017년 8월 즈음 추가된 FAST 모드는 입출력이 늘지 않을 때만 0 으로 덮어서, B-tree 페이지의 옛 내용은 지우지만 freelist 페이지에는 흔적을 남깁니다 [2].

Android 플랫폼에 들어 있는 SQLite 라이브러리(AOSP external/sqlite)는 `-DSQLITE_SECURE_DELETE` 와 `-DSQLITE_DEFAULT_AUTOVACUUM=1` 을 켜고 빌드합니다(현행 AOSP 기준) [3]. 플랫폼 SQLite 로 만든 DB 는 기본으로 지운 내용을 0 으로 덮고, 새로 만든 DB 는 auto_vacuum=FULL 로 커밋마다 빈 페이지를 잘라낸다는 뜻입니다 [2][3].

| 경우 | secure_delete 기본 | auto_vacuum 기본 | 되살리기에서 보는 점 |
|---|---|---|---|
| Android 플랫폼 SQLite(현행 AOSP 기준) | 켜짐 | FULL(1) | freelist·freeblock 에서 건질 것이 적고, WAL·저널의 옛 페이지 사본이 상대적으로 중요해짐 |
| 앱이 따로 넣은 SQLite 라이브러리(SQLCipher 등) | 그 라이브러리의 빌드 설정을 따름 | 그 라이브러리의 빌드 설정을 따름 | 플랫폼 기본값이 적용되지 않아 결과가 앱마다 다름 |
| 어느 경우든 앱이 PRAGMA 로 바꾼 경우 | 앱이 정한 값 | 표를 만들기 전에 정한 값 | 파일 머리 오프셋 52·64 로 auto_vacuum 을 확인 |

이 빌드 옵션이 들어간 Android 버전, 삼성 One UI 가 따로 바꾸는지, 앱이 PRAGMA 로 secure_delete 를 끄는지는 기기와 앱마다 다를 수 있습니다. WAL 에 이미 있는 옛 프레임까지 secure_delete 로 덮이는지도 실제 기기에서 확인합니다. 그래서 앱 DB 하나를 분석할 때는 파일 머리의 auto_vacuum 상태와 freelist 페이지 수를 먼저 읽고, 실제로 잎 페이지와 freeblock 에 0 이 아닌 바이트가 남았는지 헥스로 확인한 뒤 되살리기에 얼마나 기대할지 정합니다.

## 읽는 법

1. 반드시 DB 와 -wal·-shm·-journal 을 함께 뜬 사본에서 작업합니다. 클라이언트가 원본을 열면 체크포인트나 자동 정리가 일어나 빈 자리가 바뀔 수 있습니다.
2. 파일 머리에서 페이지 크기, 예약 공간, 오프셋 32·36(freelist), 52·64(auto_vacuum) 를 읽습니다.
3. 오프셋 32 의 트렁크부터 사슬을 따라가 잎 페이지 번호를 모두 모으고, 잎 페이지마다 첫 바이트가 0x0d 같은 B-tree 페이지 종류인지 봅니다. 그렇다면 옛 표 잎 페이지로 보고 셀을 풉니다.
4. 사용 중인 표 잎 페이지마다 페이지 머리 오프셋 1 에서 freeblock 사슬을 따라가고, 셀 포인터 배열 끝과 셀 내용 영역 시작 사이도 따로 떼어 봅니다.
5. 조각에서 레코드 머리를 찾을 때는 sqlite_schema 의 sql 로 열 수와 타입을 정하고, 직렬 타입 열이 그 틀에 맞는지로 후보를 거릅니다.
6. 되살린 행마다 어느 페이지, 어느 오프셋, 어느 자리(freelist·freeblock·빈 공간)에서 나왔는지 기록합니다.

같은 행이 살아 있는 행과 되살린 행에 모두 나올 수 있습니다. 행을 고치면 옛 셀이 빈 자리에 남고 새 셀이 다른 곳에 들어갈 수 있어서, 되살린 행이 "지운 행" 인지 "고치기 전 행" 인지는 살아 있는 행과 rowid·내용을 맞춰 본 뒤에 판단합니다.

## 결과를 어떻게 해석하나

되살린 레코드는 그 내용이 한때 이 파일에 쓰였다는 것까지만 보여 줍니다. 언제 지웠는지, 누가 지웠는지, 사용자가 직접 지웠는지 앱이 정리하면서 지웠는지는 이 구조만으로 알 수 없습니다. 반대로 되살린 것이 없다고 지운 기록이 없었다고 할 수도 없습니다. Android 플랫폼 SQLite 처럼 secure_delete 와 자동 정리가 켜진 환경에서는 지운 내용이 원래 잘 남지 않기 때문입니다.

보고서에는 "이 DB 의 freelist 잎 페이지 N 에서 이런 열 값을 가진 레코드 조각을 찾았다" 처럼 자리와 내용만 적고, 앞부분이 깨져 열 경계를 추정한 경우에는 추정했다고 밝힙니다. 삭제 데이터를 되살리는 절차 전체는 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md)에서, 조사 흐름은 [지운 대화와 사진 찾기](../../../04-scenarios/activity/deleted-content.md)와 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

## 함정

- freelist 잎 페이지가 모두 옛 표 페이지인 것은 아닙니다. 넘침 페이지나 색인 페이지였을 수 있어서 첫 바이트로 종류를 먼저 구분합니다.
- 되살린 레코드 첫 열이 NULL 이면 INTEGER PRIMARY KEY 열일 수 있고, 실제 값은 rowid 에 있었습니다. rowid 가 freeblock 머리로 덮였다면 이 값은 되살릴 수 없습니다.
- 도구마다 조각을 메우는 방식이 달라서, 결과가 다르면 헥스에서 직접 확인합니다.

## 참고 문헌

1. Database File Format — SQLite, https://www.sqlite.org/fileformat2.html
2. Pragma statements — SQLite, https://www.sqlite.org/pragma.html
3. Android.bp — AOSP external/sqlite dist (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_external_sqlite/main/dist/Android.bp
