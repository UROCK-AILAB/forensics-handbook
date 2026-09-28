---
title: "SQLite 레코드 되살리기"
parent: "삭제 데이터 복구"
grand_parent: "기법 · 분석"
nav_order: 1320
---

# SQLite 레코드 되살리기 (SQLite)

아이폰 앱 DB 에서 지운 행은 지움 표시만 붙은 채 남아 있거나, 파일 안의 빈 페이지(freelist)·페이지 안 빈 조각(freeblock)·WAL 프레임에 옛 판으로 남을 수 있고, 이 페이지는 그 자리를 차례로 찾아 읽는 방법을 다룹니다.

## 언제 쓰나

메시지·사진·메모 같은 앱 DB 에서 사용자가 지웠다고 하는 항목을 찾을 때 씁니다. 작업은 두 단계로 나뉘는데, 먼저 일반 쿼리로 보이는 "지움 표시가 붙은 행" 을 확인하고, 그다음 SQL 로는 보이지 않는 조각을 파일 구조를 따라 읽습니다. 조각이 얼마나 남는지는 DB 설정과 체크포인트 시점에 따라 크게 다르고, iOS 12 이후 지운 레코드를 되살릴 가능성이 매우 낮다는 업체 설명도 있습니다 [2]. 그래서 조각 읽기는 "남아 있으면 찾는다" 정도로 기대하고 시작하는 편이 맞고, 흔적이 사라지는 경로는 [복구가 안 되는 이유](limits.md) 에 정리했습니다.

SQLite 파일 형식 전체는 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md) 에서 설명하고, 이 페이지는 복구에 필요한 필드만 다시 짚습니다.

## 먼저 볼 곳: 지움 표시가 남은 행

Apple 앱의 DB 가운데 여럿은 지운 항목을 바로 없애지 않고 휴지통 상태나 지운 시각을 열에 적어 둡니다. 아래 표는 로컬 백업에 든 DB 의 표·열 이름입니다. 열 값의 뜻(예: 어떤 숫자가 휴지통 상태인지)과 날짜 열의 시각 기준은 시험 기기에서 직접 지워 보고 값이 어떻게 바뀌는지 확인한 뒤에 해석합니다. 표의 열 목록은 전부가 아닐 수 있어서, 표에 없다고 그 열이 없다고 볼 수는 없습니다.

| DB (도메인 :: 경로) | 표와 열 |
|---|---|
| `HomeDomain :: Library/SMS/sms.db` | `chat_recoverable_message_join`(chat_id, message_id, delete_date, ck_sync_state), `recoverable_message_part`(chat_id, message_id, part_index, delete_date, part_text, ck_sync_state), `deleted_messages`(ROWID, guid), `sync_deleted_messages`·`sync_deleted_attachments`(ROWID, guid, recordID), `sync_deleted_chats`(ROWID, guid, recordID, timestamp), `unsynced_removed_recoverable_messages`(ROWID, chat_guid, message_guid, part_index), `scheduled_messages_pending_cloudkit_delete`(ROWID, guid, recordID), `chat` 표의 is_recovered·is_deleting_incoming_messages |
| `CameraRollDomain :: Media/PhotoData/Photos.sqlite` | `ZASSET` 의 ZTRASHEDSTATE·ZTRASHEDREASON·ZCLOUDDELETESTATE, `ZADDITIONALASSETATTRIBUTES` 의 ZPTPTRASHEDSTATE, `ZGENERICALBUM`·`ZINTERNALRESOURCE`·`ZTRANSIENTINTERNALRESOURCE` 의 ZTRASHEDSTATE·ZTRASHEDDATE |
| `AppDomainGroup-group.com.apple.notes :: NoteStore.sqlite` | `ZICCLOUDSYNCINGOBJECT` 의 ZMARKEDFORDELETION·ZISRECOVERINGFROMTRASH |
| `HomeDomain :: Library/Notes/notes.sqlite` | `ZNOTE` 의 ZDELETEDFLAG |
| `AppDomainGroup-group.com.apple.reminders :: Container_v#/Stores/Data-local.sqlite`, `Data-<UUID>.sqlite` | `ZREMCDREMINDER`·`ZREMCDSAVEDATTACHMENT`·`ZREMCDSAVEDREMINDER`·`ZREMCDTEMPLATE` 의 ZMARKEDFORDELETION |
| `HomeDomain :: Library/Voicemail/voicemail.db` | `deleted` 표(`voicemail` 표와 열이 같고 trashed_date 가 있음) |
| `HomeDomain :: Library/Calendar/Calendar.sqlitedb` | `ResourceChange` 의 delete_count·deleted_summary·deleted_start_date |
| `HomeDomain :: Library/Safari/Bookmarks.db` | `bookmarks` 의 deleted |
| `HomeDomain :: Library/Shortcuts/Shortcuts.sqlite`, `Library/Shortcuts/ExternalTriggers/ExternalTriggers.sqlite` | `ZVCVOICESHORTCUTMANAGEDOBJECT` 의 ZISMARKEDASDELETED |

Photos.sqlite 와 NoteStore.sqlite 에는 Core Data 변경 기록 표인 `ACHANGE`(ZCHANGETYPE, ZENTITY, ZENTITYPK, ZTRANSACTIONID, ZCOLUMNS 등)와 `ATRANSACTION` 도 있습니다. 지운 항목의 변경이 이 표에 얼마나 오래 남는지는 실제 데이터로 확인합니다.

메시지 쪽은 열 이름만 보면 `chat_recoverable_message_join` 과 `recoverable_message_part` 가 iOS 16 부터 생긴 "최근 삭제된 항목" 보관과 이어져 보이지만, 이 대응은 공식 문서에 나오지 않습니다. `HomeDomain :: Library/Preferences/com.apple.madrid.plist` 의 `LocalDBStats` 안에는 deletedMessages·deletedChats·deletedAttachments·deletedRecoverableMessages 같은 개수 키가 있고, 같은 plist 에 `Server.TotalRecords.recoverableMessageDeleteZone` 키도 있습니다. 이 개수를 DB 에서 센 행 수와 비교하면 복구 결과가 얼마나 빠졌는지 가늠할 수 있습니다.

iOS 16 의 "보내기 취소" 와 "편집" 은 `message` 표의 text 열을 비웁니다. 보내기 취소는 보낸 뒤 2분 안에, 편집은 15분 안에만 할 수 있고, 둘 다 바뀐 시각이 따로 남으며, 편집은 고칠 때마다 시각이 붙은 이전 판 기록을 남깁니다 [3]. 이 시각을 담는 열 이름은 실제 데이터로 확인하고, 지워진 본문을 다른 파일에서 찾은 사례는 [카빙](carving.md) 에 있습니다. 표의 날짜 열을 읽을 때는 [시각 값](../../../01-foundations/value-decoding/time-values.md) 을 보고 기준을 먼저 정합니다.

## 조각이 남는 자리

SQL 로 보이지 않는 옛 행은 세 곳에 남을 수 있습니다. 첫째는 통째로 비워진 페이지가 들어가는 freelist 이고, SQLite 는 freelist 의 잎(leaf) 페이지를 정보가 없는 페이지로 보고 읽지도 쓰지도 않습니다 [1]. 그래서 지우기 전 내용이 덮이지 않고 남을 수 있습니다. 둘째는 사용 중인 잎 표 페이지 안의 freeblock 과 빈 공간인데, 지운 셀의 포인터는 셀 포인터 배열에서 빠지지만 셀 내용은 그 자리에 남을 수 있습니다. 이 부분은 공식 명세에서 따라 나오는 원리이므로 실제 파일마다 확인합니다. 셋째는 WAL 파일로, 같은 페이지의 옛 판이 여러 프레임으로 남아 있으면 프레임을 따로 읽어 지우기 전 행을 볼 수 있습니다 [1][2].

복구에 쓰는 오프셋은 아래와 같습니다 [1].

| 자리 | 오프셋 | 내용 |
|---|---|---|
| 파일 머리 | 0 | 16바이트 `SQLite format 3\0` |
| 파일 머리 | 16 | 페이지 크기 2바이트(빅엔디언, 512~32768 사이의 2의 거듭제곱, 1 이면 65536) |
| 파일 머리 | 32 / 36 | 첫 freelist trunk 페이지 번호 4바이트 / freelist 페이지 총수 4바이트 |
| freelist trunk 페이지 | 0 / 4 / 8~ | 다음 trunk 페이지 번호 / 잎 포인터 개수 L / 잎 페이지 번호 L개(모두 4바이트 정수) |
| b-tree 페이지 머리 | 0 | 페이지 종류(0x02 내부 인덱스, 0x05 내부 표, 0x0a 잎 인덱스, 0x0d 잎 표) |
| b-tree 페이지 머리 | 1 / 3 / 5 / 7 | 첫 freeblock 위치 / 셀 개수 / 셀 내용 시작 위치 / 조각난 빈 바이트 수 |
| b-tree 페이지 머리 | 8 | 오른쪽 끝 자식 페이지 번호(내부 페이지만) |
| freeblock | 0 / 2 | 다음 freeblock 위치 2바이트 / 크기 2바이트(4바이트 머리 포함) |
| 잎 표 셀 | — | 페이로드 길이 varint → rowid varint → 페이로드 → (넘치면) 첫 overflow 페이지 번호 4바이트 |
| overflow 페이지 | 0 | 다음 overflow 페이지 번호 4바이트, 나머지는 내용 |

레코드(페이로드)는 머리 크기 varint, 열마다 하나씩인 serial type varint, 값 순서로 이어집니다. varint 는 1~9바이트이고 바이트의 윗비트가 "다음 바이트가 이어진다" 는 표시입니다. serial type 은 0 이 NULL, 1~6 이 크기가 다른 정수, 7 이 실수, 8·9 가 정수 0·1 이고, 12 이상의 짝수 N 은 길이 (N-12)/2 인 BLOB, 13 이상의 홀수 N 은 길이 (N-13)/2 인 TEXT 입니다 [1]. 조각난 빈 바이트 수는 정상 페이지에서 60 을 넘지 않으므로 [1], 이 값이 이보다 크면 페이지가 손상됐거나 읽기가 어긋났다고 보고 다시 확인합니다.

WAL 은 32바이트 머리로 시작하고, 머리에는 0 에 매직 값 0x377f0682 또는 0x377f0683, 4 에 버전 3007000, 8 에 페이지 크기, 12 에 체크포인트 순번, 16·20 에 salt-1·salt-2, 24·28 에 체크섬이 있습니다. 그 뒤로 24바이트 머리와 페이지 1개로 이뤄진 프레임이 이어지는데, 프레임 머리는 0 에 페이지 번호, 4 에 커밋 표시(커밋 프레임이면 커밋 뒤 DB 페이지 수, 아니면 0), 8·12 에 salt, 16·20 에 누적 체크섬이 있습니다. 프레임은 salt 가 WAL 머리와 같고 체크섬이 맞아야 유효하고, 커밋 표시가 있는 프레임에서 트랜잭션이 확정됩니다 [1].

## 절차

1. DB 파일을 같은 이름의 `-wal`·`-shm` 파일과 함께 확보하고 해시를 남긴 뒤, 사본에서만 작업합니다. 로컬 백업 최상위에는 `Manifest.db` 와 함께 `Manifest.db-wal`·`Manifest.db-shm` 이 있을 수 있지만, `sms.db-wal` 같은 앱 DB 의 WAL 파일은 백업에 없을 수 있습니다. 백업에 `-wal` 파일이 없으면 WAL 프레임은 볼 수 없으므로, WAL 프레임까지 봐야 하면 [모바일 증거 확보](../../acquisition/mobile-acquisition/index.md) 에서 파일 시스템 단위 수집을 검토합니다.
2. SQL 로 열기 전에 원본 상태 그대로 한 벌을 더 복사해 두고, 조각 읽기는 그 사본에서 헥스로 합니다.
3. 파일 머리에서 페이지 크기(16), 첫 freelist trunk 페이지(32), freelist 페이지 총수(36)를 읽습니다. 총수가 0 이면 freelist 에서 읽을 페이지가 없습니다.
4. trunk 페이지를 따라가며 잎 페이지 번호를 모두 적고, 각 잎 페이지를 페이지 크기 단위로 잘라 레코드 모양이 있는지 살펴봅니다. 살펴보는 요령은 [카빙](carving.md) 에 있습니다.
5. 페이지 종류가 0x0d 인 잎 표 페이지마다, 오프셋 1 에서 시작하는 freeblock 사슬과 셀 포인터 배열 끝(머리 8바이트 + 셀 개수 × 2)부터 셀 내용 시작 위치 사이의 빈 공간을 읽습니다.
6. 찾은 바이트를 레코드로 풀고, 열 수와 값 종류를 `sqlite_master` 의 CREATE TABLE 문과 비교해 어느 표의 행인지 정합니다. freeblock 머리 4바이트는 빈 조각의 맨 앞에 자리 잡으므로, freeblock 안의 옛 셀은 앞쪽 몇 바이트가 온전하지 않다고 보고 읽습니다.
7. WAL 은 머리의 매직 값과 salt 를 확인한 뒤 프레임을 차례로 읽고, 유효한 프레임을 페이지 번호별로 모아 판마다 비교합니다. 옛 판에는 있고 새 판과 본 DB 에는 없는 행이 지운 행 후보입니다. 커밋 표시가 붙은 프레임까지 오지 못한 프레임은 확정되지 않은 변경이라 따로 적습니다.
8. 후보를 지워지지 않은 행과 비교해(같은 rowid·guid 가 지금도 있는지) 중복을 걸러 내고, 찾은 자리(페이지 번호·페이지 안 오프셋·WAL 프레임 번호)를 함께 기록합니다.

### 헥스로 한 번 따라가기

아래는 SQLite 명세로 만든 예시이고 실제 데이터에서 나온 바이트가 아닙니다. 표는 `CREATE TABLE t (n INTEGER, body TEXT)` 이고, 행 하나(rowid 7, n = 42, body = "hello")가 들어 있던 셀을 지웠다고 가정합니다.

```
지우기 전 셀(11바이트)
09 07 03 01 17 2A 68 65 6C 6C 6F
│  │  │  │  │  │  └ "hello"
│  │  │  │  │  └ n 값 0x2A = 42
│  │  │  │  └ serial type 0x17 = 23 → TEXT, (23-13)/2 = 5바이트
│  │  │  └ serial type 0x01 → 1바이트 정수
│  │  └ 레코드 머리 크기 3
│  └ rowid 7
└ 페이로드 길이 9

freeblock 이 된 뒤
00 00 00 0B 17 2A 68 65 6C 6C 6F
└ 다음 freeblock 없음(0) · 크기 11
```

freeblock 머리가 앞 4바이트를 덮어서 페이로드 길이·rowid·레코드 머리 크기·첫 serial type 이 사라졌지만, 남은 `17` 과 값 바이트로 "5바이트 TEXT" 와 "hello" 를 다시 알아낼 수 있습니다. 표의 열 구성을 알면 바로 앞의 `2A` 가 n 값이라고 추정할 수 있고, 이런 추정은 보고서에 추정이라고 밝혀 적습니다.

## 도구

헥스 편집기로 오프셋을 직접 따라가는 방법이 가장 확실하고, 지워지지 않은 행과 스키마는 SQLite 명령줄 도구(sqlite3) 같은 공개 도구로 사본에서 읽습니다. 예를 들어 사본에서 `SELECT chat_id, message_id, delete_date FROM chat_recoverable_message_join;` 처럼 지움 표시 표를 먼저 봅니다. 지운 레코드를 찾아 주는 공개 도구도 있지만 도구마다 freelist·freeblock·WAL 을 다루는 범위가 다르므로, 명세로 만든 시험 DB 로 결과를 먼저 비교해 봅니다([도구 검증](../../reporting/tool-validation.md)).

## 함정과 한계

- DB 설정(secure_delete·auto_vacuum)과 VACUUM·체크포인트에 따라 조각이 아예 없을 수 있습니다. 경로별 설명은 [복구가 안 되는 이유](limits.md) 에 있습니다.
- freelist 잎 페이지에는 어느 표의 행이든 들어올 수 있어서, 열 구성이 비슷한 두 표의 행을 헷갈릴 수 있습니다.
- 옛 행이 overflow 페이지로 넘쳤다면 overflow 페이지도 freelist 로 갔을 수 있고, 이때 긴 값의 뒷부분이 끊깁니다.
- 지움 표시 열의 값 뜻과 날짜 열의 시각 기준은 버전이 바뀌면 달라질 수 있으니 같은 iOS 버전의 시험 기기로 확인합니다.

## 결과를 어떻게 해석하나

freelist·freeblock·WAL 에서 찾은 레코드로 알 수 있는 것은 "이 파일 안에 한때 이런 행이 있었다" 까지입니다. 언제 지웠는지, 누가 지웠는지, 사용자가 그 내용을 봤는지는 조각만으로 알 수 없고, 지움 표시 열의 시각이나 [타임라인](../timeline/index.md) 의 다른 기록과 맞춰 봐야 합니다. 보고서에는 "sms.db 사본의 freelist 잎 페이지(페이지 번호)에서 이런 열 구성의 레코드 조각을 찾았다" 처럼 찾은 자리와 함께 쓰고, 조각을 찾지 못했다면 "지운 적이 없다" 가 아니라 "이 파일에는 조각이 남아 있지 않았다" 로 씁니다.

## 참고 문헌

1. Database File Format — SQLite — https://www.sqlite.org/fileformat2.html
2. The Five Ways to Recover iPhone Deleted Data — ElcomSoft blog (2021-11) — https://blog.elcomsoft.com/2021/11/the-five-ways-to-recover-iphone-deleted-data/
3. iOS 16 - "Paul unsent a message." ... OR DID HE?! — D20 Forensics blog (2022-09) — https://blog.d204n6.com/2022/09/ios-16-paul-unsent-message-or-did-he.html
