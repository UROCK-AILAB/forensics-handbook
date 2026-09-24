# 메가 (MEGA)

## 한 줄 요약

MEGA 데스크톱 앱(MEGAsync)은 `AppData\Local\Mega Limited\MEGAsync\` 에 설정 파일, 로그, SQLite 상태 DB 를 두고, 동기화 폴더 안에는 숨은 `Rubbish` 폴더를 만듭니다. 동기화 때문에 지워지거나 덮어쓰인 로컬 파일은 이 폴더의 날짜 폴더로 옮겨집니다.

> **(코드)** 표시는 MEGA 가 공개한 소스 코드(MEGAsync 커밋 22e72f5, MEGA SDK 커밋 b93cc67)에서 읽은 동작입니다. 코드에 그렇게 쓰여 있다는 뜻이고, 실제 검체에서 본 것은 아닙니다. 앱 버전이 다르면 다를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

MEGAsync 는 로컬 폴더와 MEGA 클라우드 폴더를 동기화하면서, 계정의 파일·폴더 정보를 로컬 SQLite DB 에 캐시하고 전송 대기열과 동기화 폴더별 상태도 DB 를 따로 만들어 둡니다 (코드). 앱 로그는 텍스트로 남기고 오래된 로그는 번호를 붙여 압축해 둡니다 (코드). 동기화 때문에 로컬에서 사라질 파일은 바로 지우지 않고 `Rubbish` 폴더로 옮기며, 탐색기의 탐색 창과 `Links` 폴더에 동기화 폴더를 등록합니다 (코드).

## 위치와 버전별 차이

### 데이터 폴더

- KAPE 대상 파일은 `C:\Users\<USER>\AppData\Local\Mega Limited\MEGAsync\` 를 하위 폴더까지 모읍니다.
- 앱은 조직 이름 `Mega Limited`, 앱 이름 `MEGAsync` 로 Qt 의 표준 데이터 위치(AppLocalDataLocation)를 씁니다 (코드). Windows 에서는 이 위치가 위 경로와 같습니다(KAPE 경로와 코드를 맞춰 본 추론).
- SDK 가 상태 DB 를 만드는 기준 폴더도 이 데이터 폴더입니다 (코드).
- 최근 제품 이름 "MEGA Desktop App" 이 MEGAsync 와 같은 앱인지는 확인하지 못했습니다.

### 데이터 폴더 안 파일 (코드)

| 파일 | 내용 |
|---|---|
| `MEGAsync.cfg` | 설정 파일. INI 형식이며 값이 암호화돼 있습니다 |
| `MEGAsync.cfg.bak` | 설정 백업. 설정을 저장할 때마다 지우고 새로 복사합니다 |
| `MEGAsync.cfg.lock` | 잠금 파일 |
| `logs\MEGAsync.log` | 지금 쓰는 로그 |
| `logs\MEGAsync.0.log`, `MEGAsync.1.log` … | 돌린 로그. gzip 으로 압축돼 있지만 이름은 `.log` 그대로입니다 |
| `megaclient_statecache15_<이름>.db` | 계정 상태 DB (SQLite) |
| `megasync.nogfx` | 이 파일이 있으면 미리보기(썸네일)를 만들지 않습니다 |

- 돌린 로그는 기본 50개까지 둡니다. 환경 변수 `MEGA_MAX_ROTATE_LOGS` 로 개수를 바꿀 수 있습니다 (코드).
- 디버그 모드를 켜면 바탕 화면에도 `MEGAsync.log` 를 만듭니다 (코드).
- 동기화 설정 파일은 이름이 `megaclient_syncconfig_` 로 시작하고, 내용이 암호화돼 있습니다 (코드). 이 파일의 저장 폴더는 확인하지 못했습니다.

### 상태 DB 이름과 판 번호

- 상태 DB 이름은 `megaclient_statecache<판 번호>_<이름>.db` 꼴입니다 (코드).
- 지금 판 번호는 15 입니다. 14 판 파일이 있으면 앱이 새 이름으로 옮겨 씁니다 (코드).
- `<이름>` 자리에는 세션 ID 일부를 Base64 로 바꾼 값이 들어갑니다. 폴더 링크로 로그인했다면 그 링크의 공개 핸들이 들어갑니다 (코드).
- `<이름>` 앞에 `status_`(상태)나 `transfers_`(전송 대기열)가 붙은 DB 도 있습니다 (코드). 예: `megaclient_statecache15_transfers_<이름>.db`
- 동기화 폴더마다 상태 DB 가 따로 있습니다. 이 DB 의 이름 부분은 (파일 시스템 ID, 원격 폴더 핸들, 사용자 ID)를 Base64 로 바꾼 값입니다 (코드).

## 구조

### 상태 DB 와 곁 파일

- 상태 DB 는 저널 방식으로 WAL 을 씁니다 (코드). 그래서 `.db-wal`·`.db-shm` 파일이 함께 생길 수 있습니다. 곁 파일의 뜻은 [WAL과 롤백 저널](../../01-foundations/database-log-formats/sqlite/wal-journal-shm.md) 에 있습니다.
- SQLite 파일 전체를 암호화하는 코드는 찾지 못했습니다. 곧 파일은 일반 SQLite 도구로 열릴 것으로 보이지만(코드에서 추론), 파일 안의 일부 표는 레코드 내용을 따로 암호화합니다(아래 `statecache` 표).

### nodes 표 (코드)

| 칸 | 내용 |
|---|---|
| `nodehandle` | 노드(파일·폴더) 핸들 |
| `parenthandle` | 부모 노드 핸들 |
| `name` | 노드의 표시 이름. 복호된 파일·폴더 이름을 텍스트로 넣습니다 |
| `fingerprint`, `origFingerprint` | 지문 값 |
| `type`, `share`, `fav`, `flags`, `counter`, `label` | 코드에 이름만 확인했습니다 |
| `ctime`, `mtime` | int64 시각 값(아래 "시각 해석") |
| `node` | BLOB. 내용 형식은 확인하지 않았습니다 |
| `description`, `tags` | 노드 설명과 태그를 텍스트로 넣습니다 |

- 이 밖에 계산용 가상 칸 `mimetypeVirtual`·`fingerprintVirtual`·`sizeVirtual`·`s3keyVirtual` 이 있습니다.
- `name` 칸이 텍스트이므로 계정의 클라우드 파일·폴더 이름 목록을 이 표에서 바로 볼 수 있습니다(코드에서 추론). 실제 검체에서 평문으로 보이는지는 확인하지 못했습니다.
- `parenthandle` 을 따라 `nodehandle` 로 올라가면 폴더 경로를 다시 세울 수 있습니다(칸 이름에서 추론).

### statecache 표 (코드)

칸은 `id`(INTEGER)와 `content`(BLOB) 두 개입니다. 앱이 레코드 내용을 저장하기 전에 PaddedCBC 로 암호화하므로, 세션 키 없이 `content` 를 읽을 수 없습니다(코드에서 추론).

### 로컬 휴지통 폴더 Rubbish (코드)

Windows 에서 동기화 폴더 안 로컬 휴지통 폴더 이름은 `Rubbish` 이고, macOS·Linux 에서는 `.debris` 입니다. 앱이 이 폴더를 숨김 속성으로 만들고, 동기화를 해제하면 숨김을 풉니다.

동기화 중 지워지거나 덮어쓰인 로컬 파일은 `Rubbish\YYYY-MM-DD\` 로 옮기며, 날짜는 로컬 시각입니다. 그 날짜 폴더에 같은 이름이 이미 있으면 `Rubbish\YYYY-MM-DD\YYYY-MM-DD HH.MM.SS.<번호>\` 하위 폴더를 만들어 넣습니다. 클라우드 쪽에서는 휴지통(Rubbish Bin) 아래에 `SyncDebris` 폴더와 날짜(`YYYY-MM-DD`) 하위 폴더를 만듭니다. 앱 설정 화면에는 이 폴더를 비우는 기능이 있습니다.

> 그림 자리: 동기화 폴더 → 숨은 `Rubbish` → `YYYY-MM-DD` 날짜 폴더 → (이름이 겹칠 때) `YYYY-MM-DD HH.MM.SS.<번호>` 하위 폴더로 이어지는 모양

### 설정 파일 암호화 (코드)

- `MEGAsync.cfg` 는 INI 형식입니다.
- 키 이름은 SHA-1 해시(16진 문자열)로 바꿔 저장합니다.
- 값은 XOR 을 거친 뒤 Windows DPAPI(`CryptProtectData`, 사용자 범위, 추가 엔트로피 사용)로 암호화하고, Base64 로 적습니다.
- 해시·XOR 에 쓰는 키 재료는 현재 사용자 토큰의 SID 에 고정 시드를 XOR 한 뒤 SHA-1 한 값입니다.
- Windows 에서는 이 키 재료를 설정 파일 안에 `LocalStorageKey` 라는 항목으로 저장해 둡니다.
- 오프라인 이미지에서 값을 풀려면 그 사용자의 DPAPI 마스터 키가 필요합니다(코드에서 추론). 마스터 키를 푸는 재료와 절차는 [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) 에 정리합니다.
- 풀었을 때 어떤 설정 값(계정 이메일, 동기화 목록 등)이 나오는지는 확인하지 못했습니다.

### 레지스트리·탐색기 흔적 (코드)

| 흔적 | 내용 |
|---|---|
| `%USERPROFILE%\Links\<동기화 이름>.lnk` | 동기화 폴더를 추가할 때 만듭니다. 설명 문자열은 `MEGAsync synchronized folder` 입니다 |
| `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{uuid}` | 기본값 `MEGA`. 탐색 창에 동기화 폴더를 등록합니다 |
| `HKCU\Software\Classes\CLSID\{uuid}` | 기본값은 동기화 이름입니다 |
| `HKCU\Software\Classes\CLSID\{uuid}\Instance\InitPropertyBag` | `TargetFolderPath` 값이 동기화 폴더 경로입니다 |
| `Software\Microsoft\Windows\CurrentVersion\Uninstall\MEGAsync` | 제거 정보 키입니다. 어느 하이브에 만드는지는 확인하지 않았습니다 |
| `Explorer\StartupApproved` 아래 | 자동 시작 승인 여부를 읽고 씁니다. 정확한 하위 키 이름은 확인하지 못했습니다 |

- 동기화 폴더에 폴더 아이콘 설정(`SHGetSetFolderCustomSettings`)을 씁니다. 이 설정이 `desktop.ini` 로 남는지는 확인하지 못했습니다.
- MEGAsync 와 SDK 코드에서 Cloud Files API 호출(`CfRegisterSyncRoot`, `StorageProviderSyncRootManager`)을 찾지 못했습니다. 곧 동기화 폴더의 파일은 자리표시자가 아닌 실제 파일이고, SyncRootManager 에 등록되지 않는 것으로 보입니다(코드에서 추론). 검체로는 확인하지 못했습니다. 공통 구조는 [클라우드 동기화 공통 구조](cloud-files-api-syncrootmanager.md) 에 있습니다.

## 증거로서 의미

### 증명하는 것

- 데이터 폴더, 제거 정보 키, 탐색 창 등록이 있으면 그 사용자 프로필에 MEGAsync 가 설치된 적이 있습니다.
- `TargetFolderPath` 값과 `Links\<동기화 이름>.lnk` 로 동기화 폴더의 이름과 경로를 알 수 있습니다.
- nodes 표의 `name`·`parenthandle` 로 계정 클라우드의 파일·폴더 이름과 트리를 볼 수 있습니다(코드에서 추론).
- `Rubbish\YYYY-MM-DD\` 폴더 이름은 로컬 파일이 그 날(로컬 시각) 휴지통 폴더로 옮겨졌다는 기록입니다(코드에서 추론).
- `YYYY-MM-DD HH.MM.SS.<번호>` 하위 폴더가 있으면 옮긴 시각을 초 단위로 좁힐 수 있습니다(코드에서 추론).
- 로그 파일이 있으면 로그가 덮는 기간에 앱이 돌았다는 근거가 됩니다.

### 증명하지 못하는 것

- nodes 표에 이름이 있다고 그 파일이 이 PC 로 내려왔다는 뜻은 아닙니다. 이 표는 계정 클라우드의 목록입니다(코드에서 추론).
- `Rubbish` 날짜는 로컬에서 파일이 옮겨진 날입니다. 지우기를 이 PC 의 사용자가 했는지, 다른 기기나 웹에서 한 일이 동기화로 내려왔는지는 폴더 이름만으로 가리지 못합니다.
- `statecache` 표의 내용은 세션 키 없이 읽지 못합니다.
- 설정 파일의 값은 DPAPI 마스터 키 없이 읽지 못합니다.
- nodes 표의 `ctime`·`mtime` 이 서버에서 받은 값인지, 로컬에서 정한 값인지 확인하지 못했습니다.

보고서에는 "X 파일을 지웠다" 대신 이렇게 씁니다. "동기화 폴더 안 숨은 `Rubbish\2024-01-01\` 폴더에 X 파일이 있다. 앱 코드상 이 폴더 이름은 동기화 중 로컬 파일을 휴지통 폴더로 옮긴 날(로컬 시각)이다."

## 시각 해석

| 값 | 형식 | 기준 |
|---|---|---|
| nodes 표 `ctime`, `mtime` | int64 `m_time_t`. `time(NULL)` 로 만드는 Unix 초입니다 (코드) | Unix 초는 1970-01-01 00:00 UTC 부터 센 값입니다. 서버 값인지 로컬 값인지는 확인하지 못했습니다 |
| `Rubbish\YYYY-MM-DD\` 폴더 이름 | 날짜 | 로컬 시각입니다 (코드) |
| `YYYY-MM-DD HH.MM.SS.<번호>` 하위 폴더 이름 | 날짜·시각 | 같은 코드 부분에서 만듭니다. 폴더의 NTFS 만든 시각과 맞춰 시간대를 확인합니다 |
| `Rubbish` 안 폴더·파일의 NTFS 시각 | FILETIME | UTC. [마스터 파일 테이블](../filesystem/mft.md) 참고 |

- 로그 줄의 시각 형식은 확인하지 못했습니다.
- 폴더 이름의 로컬 날짜를 UTC 시각과 한 줄에 놓을 때는 PC 의 [시간대 설정](../system-account/time-zone.md) 을 먼저 봅니다.
- 변환 방법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.

## 함정과 한계

- **돌린 로그는 gzip 입니다.** `MEGAsync.0.log` 같은 파일은 이름이 `.log` 라도 텍스트 편집기로 열면 깨져 보입니다. 먼저 gzip 으로 풉니다.
- **`Rubbish` 는 숨은 폴더입니다.** 숨김 파일을 보이지 않게 둔 채 훑으면 놓칩니다. 이미지의 파일 목록에서 `\Rubbish\` 경로로 찾습니다.
- **`Rubbish` 는 비울 수 있습니다.** 설정 화면에 비우기 기능이 있습니다. 폴더가 비었다고 옮긴 일이 없었던 것은 아닙니다. [USN 변경 저널](../filesystem/usnjrnl.md) 과 [지운 파일의 흔적 찾기](../../04-scenarios/activity/deleted-file-traces.md) 로 확인합니다.
- **동기화를 해제하면 숨김이 풀립니다.** 숨김이 풀린 `Rubbish` 는 동기화 해제 뒤일 수 있습니다(코드에서 추론).
- **`.cfg.bak` 은 저장할 때마다 새로 만듭니다.** 옛 설정을 오래 담아 두는 파일로 보지 않습니다.
- **SyncRootManager 로만 찾으면 놓칩니다.** MEGAsync 는 Cloud Files API 를 쓰지 않는 것으로 보입니다(코드에서 추론). 데이터 폴더, 탐색 창 등록, `Links` 바로가기로 찾습니다.
- **디버그 로그는 바탕 화면에 있을 수 있습니다.** 데이터 폴더만 모으면 놓칩니다.
- **코드와 검체는 다를 수 있습니다.** 이 글의 많은 내용은 특정 커밋의 코드 기준입니다. 설치된 앱 버전을 먼저 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

1. 데이터 폴더를 하위 폴더째 사본으로 뜹니다. 동기화 폴더의 `Rubbish` 도 따로 떠 둡니다.
2. `megaclient_statecache15_<이름>.db` 를 헥스 편집기로 열어 맨 앞이 SQLite 머리 문자열인지 봅니다. 머리가 보이면 파일 전체 암호화는 없다는 코드 추론과 맞습니다. 머리 구조는 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에 있습니다.
3. 조사 대상 파일 이름 하나를 UTF-8 로 검색합니다. 찾으면 nodes 표의 `name` 이 평문으로 남는다는 뜻입니다. 같은 이름을 `.db-wal` 에서도 찾아봅니다.
4. `ctime` 값을 Unix 초로 바꿉니다. 아래는 계산 예시이며 검체 값이 아닙니다.

```
ctime = 1704067200
→ 1970-01-01 00:00:00 UTC 부터 1704067200 초
→ 2024-01-01 00:00:00 UTC
```

5. `logs\MEGAsync.0.log` 를 헥스로 열어 앞부분이 글자로 읽히는지 봅니다. 읽히지 않으면 gzip 으로 풀어서 다시 봅니다.

### 공개 도구로 한 번

- KAPE 대상 `Megasync` 는 데이터 폴더 전체를 모읍니다.
- SQLite 명령줄 도구(sqlite3) 같은 공개 도구로 상태 DB 를 엽니다. 먼저 `.schema nodes` 로 칸 이름이 위 표와 같은지 확인합니다.
- 칸이 같으면 아래처럼 뽑습니다.

```sql
SELECT nodehandle, parenthandle, name, type,
       datetime(ctime, 'unixepoch') AS ctime_utc,
       datetime(mtime, 'unixepoch') AS mtime_utc
FROM nodes;
```

- 레지스트리 보기 도구로 `NTUSER.DAT` 와 `UsrClass.dat` 를 열어 `NameSpace\{uuid}` 와 `CLSID\{uuid}\Instance\InitPropertyBag` 을 봅니다. 하이브 읽는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 바로가기 파일 | `Links\<동기화 이름>.lnk` 의 대상 경로와 시각을 봅니다 | [바로가기 파일](../file-folder-usage/lnk.md) |
| 설치 프로그램 | `Uninstall\MEGAsync` 로 설치 사실과 판을 봅니다 | [설치 프로그램](../system-account/uninstall.md) |
| 로그온 자동실행 | `StartupApproved` 와 자동 시작 등록을 봅니다 | [로그온 자동실행](../persistence/run-runonce-startup-folder.md) |
| DPAPI 구조 | 설정 파일 값을 풀 재료를 봅니다 | [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) |
| USN 변경 저널 | 파일이 `Rubbish` 로 옮겨진 시각을 봅니다 | [USN 변경 저널](../filesystem/usnjrnl.md) |
| 마스터 파일 테이블 | `Rubbish` 날짜 폴더의 NTFS 만든 시각을 봅니다 | [마스터 파일 테이블](../filesystem/mft.md) |
| SRUM | 그 시간대에 MEGAsync 가 네트워크로 얼마나 주고받았는지 봅니다 | [SRUM](../execution/system-resource-usage-monitor/index.md) |
| 프리페치 | MEGAsync 실행 시각을 봅니다 | [프리페치](../execution/prefetch/index.md) |
| 자료 유출 시나리오 | 클라우드 업로드를 다른 흔적과 묶어 봅니다 | [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md) |

## 실습

MEGAsync 가 깔린 공개 검체(NIST CFReDS 등)를 구하거나, 시험용 PC 에 앱을 깔고 시험용 계정으로 동기화해 본 뒤 아래 질문을 풀어 봅니다.

1. 데이터 폴더의 `megaclient_statecache` DB 는 몇 개입니까? 판 번호는 몇입니까? `status_`·`transfers_` 가 붙은 DB 가 있습니까?
2. nodes 표에서 파일 이름이 평문으로 보입니까? `parenthandle` 을 따라 파일 하나의 전체 경로를 세워 봅니다.
3. `logs` 폴더의 로그 파일은 몇 개입니까? 번호 붙은 로그를 풀어 첫 줄과 마지막 줄의 시각을 적습니다.
4. 동기화 폴더에서 `Rubbish` 를 찾습니다. 숨김 속성이 켜져 있습니까? 날짜 폴더는 몇 개입니까?
5. 날짜 폴더 하나의 이름과 그 폴더의 NTFS 만든 시각(UTC)을 비교합니다. 시간대만큼 차이가 납니까?
6. `UsrClass.dat` 에서 `TargetFolderPath` 를 찾아 `Links` 폴더 바로가기의 대상 경로와 맞춰 봅니다.

## 참고 문헌

1. Eric Zimmerman 외, KapeFiles GitHub 저장소 (커밋 ed0f9c7), `Targets/Apps/Megasync.tkape` — https://github.com/EricZimmerman/KapeFiles
2. MEGA, MEGAsync 데스크톱 앱 소스 저장소 (커밋 22e72f5) — https://github.com/meganz/MEGAsync
3. MEGA, MEGA SDK 소스 저장소 (커밋 b93cc67) — https://github.com/meganz/sdk
