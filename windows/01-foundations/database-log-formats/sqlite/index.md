# SQLite 데이터베이스 (SQLite)

## 한 줄 요약

SQLite 는 데이터베이스 하나를 파일 하나에 담는 형식이고, 브라우저, 메신저, 윈도의 여러 기능이 이 형식으로 기록을 남깁니다. 분석은 주 파일과 그 옆에 생기는 `-wal`·`-journal`·`-shm` 파일을 함께 읽는 데서 시작합니다.

## 왜 중요한가

- 사용자가 무엇을 했는지 보여 주는 기록 가운데 상당수가 SQLite 파일에 있습니다. 브라우저 방문 기록, 윈도 알림, 윈도 타임라인이 그 예입니다.
- Windows 11 은 검색 색인도 SQLite 에 저장하고, Windows 10 까지는 같은 색인을 ESE 형식(`Windows.edb`)에 저장했습니다. 같은 기록이라도 윈도 버전에 따라 읽는 법이 달라집니다. ESE 는 [ESE 데이터베이스](../extensible-storage-engine/index.md) 에서 다룹니다.
- 형식이 운영체제에 매이지 않습니다. 헤더와 B-트리 (B-tree) 페이지 안의 여러 바이트 값은 모두 빅엔디언 (big-endian) 으로 저장되므로, 윈도에서 익힌 읽는 법을 스마트폰이나 macOS 에서 나온 파일에도 그대로 씁니다.
- SQL 로 조회해서 보이는 것은 지금 살아 있는 행뿐이고, 지운 행은 세 자리에 남을 수 있습니다. 빈 페이지 목록인 프리리스트 (Freelist), 페이지 안의 빈 조각인 프리블록 (Freeblock), 셀 포인터 배열과 셀 내용 사이의 비할당 영역 (Unallocated Space) 입니다. 이 자리들은 SQL 로 보이지 않으므로 파일을 직접 읽어야 찾습니다.
- 지운 행이 남는지는 앱 설정에 따라 다릅니다. `secure_delete` 를 켜면 SQLite 가 지운 내용을 0 으로 덮는데 이 설정은 기본으로 꺼져 있습니다. `auto_vacuum` 을 FULL 로 두면 커밋할 때마다 빈 페이지를 파일 끝으로 모아 잘라 냅니다.
- 주 파일만으로는 최신 상태가 아닐 수 있습니다. 쓰기 전 로그 (Write-Ahead Log, WAL) 방식에서는 바뀐 내용이 `-wal` 파일에 먼저 쌓입니다. 이 내용을 주 파일로 옮기는 일을 체크포인트 (Checkpoint) 라고 합니다. 기본 설정에서 체크포인트는 WAL 이 1000 페이지 이상 쌓이는 커밋 때, 또는 마지막 연결이 닫힐 때 일어납니다.
- 원본 파일을 SQLite 로 열기만 해도 파일이 바뀔 수 있습니다. 마지막 연결을 닫을 때 SQLite 는 보통 체크포인트를 하고 `-wal` 파일을 지웁니다. WAL 방식 파일은 읽기 전용으로 열어도, 폴더에 쓰기 권한이 있으면 `-wal`·`-shm` 파일을 만들 수 있습니다. 그래서 해시를 기록한 사본에서 작업합니다. WAL 을 주 파일에 합치기 전 상태도 따로 봐 둡니다.
- 시각의 형식은 SQLite 가 아니라 앱이 정합니다. SQLite 파일 헤더에는 시각 칸이 없습니다. 크롬 계열은 1601년 1월 1일(UTC)부터 센 마이크로초를 씁니다. 파이어폭스 `places.sqlite` 는 1970년 1월 1일(UTC)부터 센 마이크로초를 씁니다. 열마다 기준 시점, 단위, UTC 인지 현지 시각인지를 확인합니다. 변환은 [시각 값 형식](../../value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.
- 도구마다 결과가 다를 수 있습니다. SQLite 포렌식 코퍼스를 만든 연구진은 여러 도구가 내세우는 분석·복구 기능이 적절한 근거로 뒷받침되지 않는다고 지적했습니다. 지운 행을 복구한 결과는 두 가지 이상 방법으로 비교합니다.
- 앱이 파일 전체를 암호화하기도 합니다. SQLCipher 로 암호화한 파일은 첫머리에 `SQLite format 3` 문자열이 없고 파일 전체가 무작위 값처럼 보입니다. 확장자가 `.db` 인데 열리지 않으면 첫 16바이트부터 확인합니다.

## 한눈에 보기

> 그림 자리: 주 파일(`예.db`)과 옆 파일(`예.db-journal`·`예.db-wal`·`예.db-shm`)의 관계. 롤백 저널 방식과 WAL 방식에서 바뀐 페이지가 어느 파일로 먼저 가는지 화살표로 보여 주는 그림

### SQLite 를 쓰는 아티팩트

앱이 만드는 파일은 윈도 버전이 아니라 앱 버전을 따릅니다. 앱별 경로는 각 페이지에 정리합니다.

| 쓰는 곳 | 파일과 위치 | Windows 버전 | 알려 주는 것 |
|---|---|---|---|
| 크롬 계열 브라우저 | 브라우저 프로필 폴더의 `History`·`Login Data`·`Web Data` 등 | 윈도 버전과 무관 | [방문·다운로드](../../../02-artifacts/browsers/chrome-edge-whale/history.md), [쿠키](../../../02-artifacts/browsers/chrome-edge-whale/cookies.md), [저장 비밀번호](../../../02-artifacts/browsers/chrome-edge-whale/login-data.md), [자동완성](../../../02-artifacts/browsers/chrome-edge-whale/web-data-autofill.md) |
| 파이어폭스 | 프로필 폴더의 `places.sqlite`·`cookies.sqlite`·`formhistory.sqlite`·`key4.db` | 윈도 버전과 무관 | [방문·다운로드·즐겨찾기](../../../02-artifacts/browsers/firefox/places-sqlite.md), [쿠키](../../../02-artifacts/browsers/firefox/cookies-sqlite.md), [양식 기록](../../../02-artifacts/browsers/firefox/formhistory-sqlite.md), [저장 비밀번호](../../../02-artifacts/browsers/firefox/logins-json-key4-db.md) |
| 윈도 알림 | `%LOCALAPPDATA%\Microsoft\Windows\Notifications\wpndatabase.db` | Windows 10 1607 이후 | [알림 기록](../../../02-artifacts/execution/wpndatabase-db.md) |
| 윈도 타임라인 | `%LOCALAPPDATA%\ConnectedDevicesPlatform\` 아래 계정별 폴더의 `ActivitiesCache.db` | Windows 10 1803 이후. Windows 11 에서는 기능이 빠졌지만 파일은 남을 수 있음 | [타임라인](../../../02-artifacts/file-folder-usage/activitiescache-db.md) |
| 윈도 검색 색인 | `%ProgramData%\Microsoft\Search\Data\Applications\Windows\` 의 `Windows.db`·`Windows-gather.db`·`Windows-usn.db` | Windows 11 (Windows 10 까지는 ESE 형식) | [위치와 형식](../../../02-artifacts/file-folder-usage/windows-search/windows-edb-windows-db.md) |
| 스토어 앱 설치 목록 | `%ProgramData%\Microsoft\Windows\AppRepository\StateRepository-Machine.srd` | Windows 10·11 | [스토어 앱 설치 목록](../../../02-artifacts/system-account/appx-staterepository.md) |
| Recall | `%LOCALAPPDATA%\CoreAIPlatform.00\UKP\{GUID}\ukg.db` | Windows 11 에서 Recall 을 켠 PC | 캡처한 창과 앱 사용 기록 (이 위키에 따로 페이지 없음) |
| 클라우드·메모 앱 | 원드라이브 `SyncEngineDatabase.db`, 구글 드라이브 메타데이터 DB, 스티커 메모 `plum.sqlite` | 앱 버전을 따름 | [원드라이브 동기화 DB](../../../02-artifacts/cloud-notes/onedrive/syncenginedatabase-db.md), [구글 드라이브](../../../02-artifacts/cloud-notes/drivefs-backup-and-sync.md), [스티커 메모](../../../02-artifacts/cloud-notes/sticky-notes.md) |
| 메신저 | 대화 DB. 암호화한 경우가 많음 | 앱 버전을 따름 | [시그널](../../../02-artifacts/messengers/signal.md), [카카오톡 대화 DB 암호화](../../../02-artifacts/messengers/kakaotalk-pc/chat-db-encryption.md) |

### 주 파일 옆에 생기는 파일

| 파일 | 언제 생기나 | 포렌식에서 보는 점 |
|---|---|---|
| `이름-journal` | 롤백 저널 (Rollback Journal) 방식에서 쓰기 트랜잭션 중 | 바뀌기 전 페이지가 담깁니다. 기본(DELETE) 방식은 커밋할 때 이 파일을 지웁니다. TRUNCATE 방식은 길이를 0 으로 줄이고, PERSIST 방식은 헤더만 0 으로 덮습니다. |
| `이름-wal` | WAL 방식 | 커밋했지만 아직 주 파일로 옮기지 않은 페이지가 있을 수 있습니다. 체크포인트 뒤에도 보통 파일을 자르지 않고 앞에서부터 덮어 씁니다. 그래서 이미 옮긴 옛 페이지 사본이 뒤쪽에 남을 수 있습니다. |
| `이름-shm` | WAL 방식 | WAL 안에서 페이지를 빨리 찾게 돕는 색인입니다. 내용은 임시 값이고, 비정상 종료 뒤에는 WAL 을 읽어 다시 만듭니다. |

주 파일 헤더의 오프셋 18·19 바이트를 보면 어느 방식인지 알 수 있습니다. 값이 1 이면 롤백 저널 방식이고, 2 이면 WAL 방식입니다. WAL 방식은 SQLite 3.7.0(2010년)부터 쓸 수 있습니다.

### 파일 첫머리 알아보기

아래는 명세에 적힌 고정 문자열로 만든 예시입니다. 암호화하지 않은 SQLite 파일은 모두 이 16바이트로 시작합니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

이 문자열이 없고 앞부분이 무작위 값처럼 보이면 암호화를 의심합니다. SQLCipher 는 파일 첫 16바이트에 키를 만들 때 쓰는 무작위 솔트 (Salt) 를 둡니다.

## 읽는 순서

1. [파일·페이지 구조 (B-tree·Record Format)](b-tree-record-format.md) — 100바이트 파일 헤더, 같은 크기로 나뉜 페이지, 표와 색인의 B-트리를 헥스로 따라갑니다. 레코드 머리에 적힌 형식 값으로 열 값을 읽는 법도 다룹니다.
2. [WAL과 롤백 저널 (-wal·-journal·-shm)](wal-journal-shm.md) — 두 방식이 바뀐 내용을 어디에 먼저 쓰는지 비교합니다. 아직 주 파일에 안 들어간 변경과 WAL 뒤쪽에 남은 옛 페이지를 읽는 법을 다룹니다.
3. [파일 안에 남은 지운 레코드 (Freelist·Freeblock)](freelist-freeblock.md) — 지운 행이 남는 세 자리를 찾아갑니다. `secure_delete`·`auto_vacuum`·VACUUM 이 무엇을 지우고 무엇을 남기는지도 나눕니다.
4. [암호화된 SQLite (SQLCipher)](sqlcipher.md) — 암호화된 파일을 알아보는 법과 페이지 단위 암호화 구조를 다룹니다. 키가 없으면 왜 내용을 볼 수 없는지, 키를 구하는 길이 왜 앱마다 다른지도 설명합니다.

## 함께 볼 페이지

- [ESE 데이터베이스 (Extensible Storage Engine)](../extensible-storage-engine/index.md) — SRUM·웹캐시, 그리고 Windows 10 까지의 검색 색인이 쓰는 다른 DB 형식입니다.
- [LevelDB 저장소 (LevelDB)](../leveldb.md) — 크롬 계열 앱이 SQLite 와 나란히 쓰는 저장 형식입니다.
- [크롬 계열 앱 공통 구조 (Chromium·Electron·WebView2)](../../app-mail-data/chromium-electron-webview2/index.md) — 브라우저와 Electron 앱 프로필 폴더의 SQLite 파일 위치를 다룹니다.
- [시각 값 형식 (FILETIME·Unix·WebKit·DOS·OLE)](../../value-decoding/filetime-unix-webkit-dos-ole.md) — 열에 든 숫자를 시각으로 바꿉니다.
- [문자 인코딩 (UTF-16LE·UTF-8·CP949)](../../value-decoding/utf-16le-utf-8-cp949.md) — 헤더 오프셋 56 의 값이 문자열 인코딩을 정합니다. 1 은 UTF-8, 2 는 UTF-16LE, 3 은 UTF-16BE 입니다.
- [레코드 카빙 (Record Carving)](../../../03-techniques/analysis/data-recovery/record-carving.md) — DB 파일 밖(디스크 비할당 영역, 파일 조각)에 흩어진 SQLite 레코드를 찾는 법입니다.
- [선별 수집 (Triage Collection)](../../../03-techniques/process-acquisition/evidence-acquisition/triage-collection.md) — 주 파일을 옆 파일과 함께 수집하는 법을 다룹니다.
- [해시로 무결성 검증 (Hash Verification)](../../../03-techniques/process-acquisition/evidence-acquisition/hash-verification.md) — 사본에서 작업하기 전에 원본 해시를 남깁니다.
- [섀도 복사본 활용 (Volume Shadow Copy Analysis)](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 옛 시점의 DB 파일을 꺼내 지금과 비교합니다.
- [도구 결과 교차 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md) — 지운 행 복구 결과를 여러 방법으로 대조합니다.

## 참고 문헌

- SQLite, "Database File Format" — https://www.sqlite.org/fileformat.html
- SQLite, "Write-Ahead Logging" — https://www.sqlite.org/wal.html
- SQLite, "Pragma statements supported by SQLite" — https://www.sqlite.org/pragma.html
- Zetetic, "SQLCipher Design" — https://www.zetetic.net/sqlcipher/design/
- Kaspersky Securelist, "What makes Windows 11 interesting from a digital forensics perspective" — https://securelist.com/forensic-artifacts-in-windows-11/117680/
- Digital Corpora, "SQLite Forensic Corpus" (Nemetz·Schmitt·Freiling, DFRWS EU 2018 논문의 검체 모음) — https://digitalcorpora.org/corpora/sql/sqlite-forensic-corpus/
