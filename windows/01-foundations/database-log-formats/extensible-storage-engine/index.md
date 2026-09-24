# ESE 데이터베이스 (Extensible Storage Engine)

## 한 줄 요약

ESE (Extensible Storage Engine) 는 Windows 에 들어 있는 데이터베이스 엔진입니다. SRUM, IE 웹캐시, Windows 검색 색인, BITS, Active Directory 가 이 엔진으로 데이터를 저장합니다. 분석은 DB 파일과 같은 폴더의 트랜잭션 로그 (Transaction Log) 를 함께 확보하는 데서 시작합니다.

## 왜 중요한가

- 여러 아티팩트가 같은 형식을 씁니다. 형식 하나를 익히면 SRUDB.dat·WebCacheV01.dat·Windows.edb·qmgr.db·ntds.dit 를 같은 방법으로 읽을 수 있습니다.
- 확장자는 앱마다 다릅니다. `.dat`·`.edb`·`.db`·`.dit` 가 모두 쓰입니다. 그래서 확장자가 아니라 파일 헤더로 알아봅니다. 명세에 따르면 파일 오프셋 4 에 서명 바이트 `EF CD AB 89` 가 있습니다. 리틀 엔디언 32비트 값으로 읽으면 `0x89ABCDEF` 입니다.
- ESE 의 옛 이름은 JET Blue 입니다. Microsoft Access 가 쓰는 JET Red 는 이름만 비슷하고 전혀 다른 엔진입니다. 자료나 도구에서 "JET" 이라는 말이 나오면 둘 중 어느 쪽인지 확인합니다.
- 바뀐 내용은 로그에 먼저 쓰입니다. DB 파일에는 그 뒤에 쓰입니다. 곧바로 쓰일 수도 있고 한참 뒤에 쓰일 수도 있습니다. 그래서 DB 파일만 보면 최신 상태가 아닐 수 있습니다. 수집할 때는 DB 가 든 폴더를 통째로 가져옵니다.
- 압수 이미지에서 꺼낸 ESE DB 는 대부분 비정상 종료 (Dirty Shutdown) 상태였습니다(관찰: SRUDB.dat·WebCacheV01.dat·Windows.edb). 이런 DB 를 JET API 로 열려면 먼저 같은 폴더의 로그로 복구해야 합니다. 이미지 안의 로그 사슬이 끊겨 있어 복구가 안 되는 경우도 있었습니다(관찰). 오래된 로그 세대가 지워진 경우였습니다.
- 페이지를 직접 해석하는 방식은 로그 없이 DB 파일을 읽습니다. 다만 로그에만 있고 DB 파일에 아직 들어가지 않은 변경은 이 방식으로 보이지 않습니다. 공개 도구 가운데 Windows 에 들어 있는 esentutl 은 JET API 로 여는 쪽입니다. libesedb 는 페이지를 직접 읽는 쪽입니다.
- 복구하면 DB 파일이 바뀝니다. JET API 로 엔진을 시작하면 복구가 자동으로 돌아갑니다. 그래서 원본의 해시를 먼저 구하고 사본에서만 작업합니다. Microsoft 문서는 정상 종료된 DB 만 안전하게 옮기거나 이름을 바꿀 수 있다고 설명합니다. 비정상 종료 DB 를 꺼낼 때는 로그와 체크포인트 파일도 같은 폴더에 함께 꺼냅니다.
- 비정상 종료와 손상은 다릅니다. 비정상 종료는 로그로 복구할 수 있습니다. 손상 (Corruption) 은 로그로 복구해도 고쳐지지 않습니다. 손상된 DB 는 읽는 방식에 따라 결과 행 수가 달랐습니다. 같은 손상 SRUDB.dat 의 앱 사용량 표에서 도구에 따라 1,612행과 1,742행이 나왔습니다(관찰). B+트리를 끝까지 따라가지 못한 쪽이 적게 냈습니다. 손상된 DB 는 두 가지 이상 방식으로 열어 비교합니다.
- 표와 열의 이름은 앱이 정합니다. Windows 8·10 의 Windows.edb 에서 `SystemIndex_PropertyStore` 표는 열 이름 앞에 숫자 속성 ID 가 붙습니다. ID 끝에 `F` 가 더 붙는 열도 있습니다(예: `4456-System_Kind`, `4631F-System_Search_GatherTime`, 관찰). 속성 이름을 글자 그대로 찾는 도구는 이 표에서 0건을 냈습니다. 표와 열의 정의는 카탈로그에서 먼저 확인합니다.
- 시각 값의 형식도 앱이 정합니다. 한 파일 안에서도 열마다 FILETIME, OLE 날짜처럼 형식이 다를 수 있습니다. 시각 열은 형식을 하나씩 확인하고 바꿉니다.

## 한눈에 보기

> 그림 자리: DB 파일·트랜잭션 로그·체크포인트 파일이 한 폴더에 놓인 모습과, 변경이 로그 → DB 파일 순서로 쓰이는 흐름

### ESE 를 쓰는 주요 파일

| 파일 | 위치 | Windows 버전 | 알려 주는 것 |
|---|---|---|---|
| SRUDB.dat | `%SystemRoot%\System32\sru\SRUDB.dat` | 8 이후 | [SRUM](/02-artifacts/execution/system-resource-usage-monitor/index.md): 앱별 자원 사용, 네트워크 사용량, 네트워크 연결 |
| WebCacheV01.dat | `%LOCALAPPDATA%\Microsoft\Windows\WebCache\WebCacheV01.dat` | IE 10 이후 | [웹캐시 DB](/02-artifacts/browsers/ie-edgehtml/webcachev01-dat.md): 방문 기록, 쿠키, 캐시 목록 |
| Windows.edb | `%ProgramData%\Microsoft\Search\Data\Applications\Windows\Windows.edb` | Vista ~ 10 | [윈도 검색 색인 DB](/02-artifacts/file-folder-usage/windows-search/index.md): 색인된 파일의 속성, 지운 파일의 흔적 |
| qmgr.db | `%ProgramData%\Microsoft\Network\Downloader\qmgr.db` | 10 부터 | [BITS 전송 작업](/02-artifacts/persistence/bits-jobs-qmgr-db.md): 내려받기·올리기 작업과 대상 파일 |
| DataStore.edb | `%SystemRoot%\SoftwareDistribution\DataStore\DataStore.edb` | 확인 전 | [윈도 업데이트 기록](/02-artifacts/system-account/windows-update-cbs-log.md) |
| WindowsMail.MSMessageStore | `%USERPROFILE%\AppData\Local\Microsoft\Windows Mail\WindowsMail.MSMessageStore` | Vista (Windows Mail) | [옛 윈도 메일 프로그램](/02-artifacts/mail/outlook-express-windows-live-mail.md): 메일 폴더 정보 |
| ntds.dit | `%SystemRoot%\NTDS\ntds.dit` (기본 위치) | 도메인 컨트롤러 | [액티브 디렉터리 DB](/02-artifacts/credentials/ntds-dit.md): 도메인 계정과 비밀번호 해시 |

- Windows 10 전의 BITS 는 ESE 가 아닌 `qmgr0.dat`·`qmgr1.dat` 를 씁니다.
- Windows 11 에서는 검색 색인이 SQLite 파일(`Windows.db`·`Windows-gather.db`·`Windows-usn.db`)로 바뀝니다. 어느 빌드부터 바뀌었는지와 두 형식을 구별하는 법은 [위치와 형식 (Windows.edb·Windows.db)](/02-artifacts/file-folder-usage/windows-search/windows-edb-windows-db.md) 에서 다룹니다.
- 라이브 시스템에서는 서비스가 파일을 잠가 두어 그냥 복사되지 않을 수 있습니다. 예를 들어 Windows 10 의 BITS 서비스는 qmgr.db 를 다른 프로그램과 나눠 쓰지 않게 엽니다.
- Exchange 서버의 메일 DB(`.edb`)도 ESE 를 씁니다.

### 같은 폴더에 있는 파일

로그 파일 이름은 세 글자 기본 이름 (Base Name) 으로 시작합니다. 기본값은 `edb` 이고, 앱이 바꿀 수 있습니다. 예를 들어 WebCache 폴더의 로그는 `V01` 로 시작합니다. 확장자에는 옛 규칙과 새 규칙이 있습니다. Vista 이후에는 새 규칙이 기본이지만 앱이 옛 규칙을 고를 수 있습니다. Windows 10 의 BITS 폴더에는 옛 규칙의 `edb.log` 가 있습니다. Windows 10 이후 Windows Search 는 새 규칙의 `.jtx`·`.jcp` 를 썼습니다(관찰). 복구할 때는 이 이름 규칙을 맞춰야 엔진이 로그를 찾습니다.

| 파일 | 옛 이름 | 새 이름 | 하는 일 |
|---|---|---|---|
| 트랜잭션 로그 | `<base>.log`, `<base>XXXXX.log` | `<base>.jtx`, `<base>XXXXX.jtx` | DB 에 한 작업을 적습니다. 확장자 앞에 번호가 없는 파일이 지금 쓰는 로그입니다. 다 차면 16진수 세대 번호가 붙은 이름으로 바뀝니다(예: `edb00001.log`). |
| 임시 로그 | `<base>tmp.log` | `<base>tmp.jtx` | 다음 로그를 미리 만들어 둔 파일입니다. 쓸모 있는 내용이 없습니다. |
| 예약 로그 | `res1.log`, `res2.log` (Server 2003 까지) | `<base>RESXXXXX.jrs` (Vista 부터) | 디스크가 꽉 찰 때를 대비해 미리 만든 파일입니다. 쓸모 있는 내용이 없습니다. |
| 체크포인트 | `<base>.chk` | `<base>.jcp` | 로그의 어디까지가 DB 파일에 반영됐는지 적습니다. 이 지점 뒤의 로그만 복구에 쓰입니다. |
| 플러시 맵 | 없음 | `<DB 이름>.jfm` (Windows 10 1607 부터) | 디스크에 실제로 쓰이지 않은 쓰기를 알아내려고 두는 파일입니다. 없으면 엔진이 새로 만듭니다. |

순환 로깅 (Circular Logging) 을 켜 두면 엔진이 복구에 더는 필요 없는 로그를 스스로 지웁니다. 전체 백업을 해도 옛 로그가 지워집니다. 그래서 폴더에 모든 세대의 로그가 남아 있지 않을 수 있습니다.

### Windows 버전에 따라 달라지는 점

| Windows 버전 | 달라진 점 |
|---|---|
| 2000 | ESE 가 Windows 구성 요소로 들어옵니다. |
| XP | 비정상 종료 상태를 "Dirty Shutdown" 이라고 부르기 시작합니다. 그 전 이름은 "Inconsistent" 입니다. 옛 자료에서는 두 말을 같은 뜻으로 읽습니다. |
| Vista | 로그·체크포인트의 새 이름 규칙(`.jtx`·`.jcp`·`.jrs`)이 기본이 됩니다. |
| 7 | 페이지 크기로 2·16·32 KiB 도 쓸 수 있게 됩니다. 긴 값 열을 압축할 수 있게 됩니다. |
| 8 | SRUM 이 SRUDB.dat 에 기록을 남기기 시작합니다. |
| 10 | BITS 가 작업 목록을 ESE 파일(qmgr.db)에 저장합니다. 1607(Anniversary Update)부터 DB 옆에 플러시 맵 파일(`.jfm`)이 생깁니다. |
| 11 | Windows Search 가 SQLite 로 바뀝니다. 헤더의 파일 형식 리비전에 새 값이 나타납니다(명세 기준: 21H2 는 `0xC8`). |

## 읽는 순서

1. [파일 구조 (Page·B+Tree·Catalog)](/01-foundations/database-log-formats/extensible-storage-engine/page-b-tree-catalog.md) — 첫 페이지의 파일 헤더와 둘째 페이지의 헤더 사본, 고정 크기 페이지, 표를 이루는 B+트리를 헥스로 따라갑니다. 모든 표·열 정의가 든 카탈로그 (MSysObjects) 를 읽는 법도 다룹니다.
2. [트랜잭션 로그와 비정상 종료 상태 (edb.log·Dirty Shutdown)](/01-foundations/database-log-formats/extensible-storage-engine/edb-log-dirty-shutdown.md) — 헤더의 상태 값을 읽는 법을 다룹니다. 명세에 따르면 2 는 비정상 종료, 3 은 정상 종료 (Clean Shutdown) 입니다. 로그로 복구할지, 로그 없이 읽을지 고르는 기준도 설명합니다.
3. [긴 값과 압축 열 (Long Value·Compressed Column)](/01-foundations/database-log-formats/extensible-storage-engine/long-value-compressed-column.md) — 페이지보다 큰 값은 여러 조각으로 나뉘어 따로 저장됩니다. 조각 경계를 잘못 계산하면 오류 없이 값이 망가집니다(관찰: 6,000바이트 값이 11,158바이트로 나온 사례). 7비트·XPRESS·LZ4 같은 열 압축도 다룹니다.
4. [파일 안에 남은 지운 레코드 (Deleted Records)](/01-foundations/database-log-formats/extensible-storage-engine/deleted-records.md) — 지운 레코드가 페이지 안에 남는 경우와 찾는 법, 그 한계를 다룹니다.

## 함께 볼 페이지

- [SQLite 데이터베이스 (SQLite)](/01-foundations/database-log-formats/sqlite/index.md) — Windows 11 검색 색인처럼 ESE 에서 SQLite 로 옮겨 간 데이터를 읽습니다.
- [레지스트리 하이브 구조 (Registry Hive)](/01-foundations/database-log-formats/registry-hive/index.md) — 로그에 먼저 쓰고 주 파일에 나중에 쓰는 같은 구조를 다룹니다.
- [SRUM 해석 함정 (1시간 단위 기록·레지스트리 임시 저장)](/02-artifacts/execution/system-resource-usage-monitor/1.md) — ESE 파일에 아직 들어가지 않은 데이터가 어디 머무는지 다룹니다.
- [시각 값 형식 (FILETIME·Unix·WebKit·DOS·OLE)](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) — 열마다 다른 시각 값을 읽습니다.
- [윈도 압축 형식 (LZNT1·Xpress·Xpress Huffman)](/01-foundations/value-decoding/lznt1-xpress-xpress-huffman.md) — 압축 열을 풀 때 필요합니다.
- [레코드 카빙 (Record Carving)](/03-techniques/analysis/data-recovery/record-carving.md) — DB 가 열리지 않을 때 페이지에서 레코드를 직접 찾습니다.
- [섀도 복사본 활용 (Volume Shadow Copy Analysis)](/03-techniques/analysis/volume-shadow-copy-analysis.md) — 옛 시점의 DB 와 로그를 꺼내 지금과 비교합니다.
- [선별 수집 (Triage Collection)](/03-techniques/process-acquisition/evidence-acquisition/triage-collection.md) — 잠긴 DB 를 로그와 함께 수집하는 법을 다룹니다.
- [도구 결과 교차 검증 (Tool Validation)](/03-techniques/reporting/tool-validation.md) — 손상 DB 를 여러 방식으로 읽고 결과를 맞춰 봅니다.

## 참고 문헌

- Microsoft Learn, "Extensible Storage Engine" — https://learn.microsoft.com/en-us/windows/win32/extensible-storage-engine/extensible-storage-engine
- Microsoft Learn, "Extensible Storage Engine Files" — https://learn.microsoft.com/en-us/windows/win32/extensible-storage-engine/extensible-storage-engine-files
- Joachim Metz, "Extensible Storage Engine (ESE) Database File (EDB) format specification" (libesedb) — https://github.com/libyal/libesedb/blob/main/documentation/Extensible%20Storage%20Engine%20(ESE)%20Database%20File%20(EDB)%20format.asciidoc
- Joachim Metz, ESE Database File Knowledge Base (esedb-kb: SRUM·MSIE web cache·Windows Update·Windows Mail 문서) — https://github.com/libyal/esedb-kb/tree/main/documentation
- Mandiant, "Back in a Bit: Attacker Use of the Windows Background Intelligent Transfer Service" — https://cloud.google.com/blog/topics/threat-intelligence/attacker-use-of-windows-background-intelligent-transfer-service/
- Kaspersky Securelist, "What makes Windows 11 interesting from a digital forensics perspective" — https://securelist.com/forensic-artifacts-in-windows-11/117680/
