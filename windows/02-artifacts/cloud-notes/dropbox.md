---
title: "드롭박스"
parent: "아티팩트 · 클라우드·노트"
nav_order: 2230
---

# 드롭박스 (Dropbox)

## 한 줄 요약

드롭박스 PC 앱은 동기화 폴더 위치와 계정 종류를 `info.json` 에 적습니다. 앱의 DB 는 확장자가 `.dbx` 인 파일입니다. 2017년 자료에 따르면 이 파일은 암호화한 SQLite 이고, 일부는 암호화하지 않았습니다. DB 를 푸는 키는 사용자 레지스트리에 DPAPI 로 보호해 둡니다. 그래서 DB 를 열려면 먼저 DPAPI 를 풀어야 하고, 이때 사용자 로그인 비밀번호(또는 그 SHA1 해시)나 그 사용자의 DPAPI 마스터 키가 필요합니다 (2017년 자료 기준).

> **(구현)** 표시는 한 포렌식 분석 구현의 소스 코드에 들어 있던 파일·표·칸 이름입니다. 실제 검체나 공개 자료로 확인하지 않았고, 어느 앱 버전 것인지도 모릅니다. 검체에서 찾아볼 후보로만 적습니다.

## 무엇을 기록하나 · 왜 생기나

앱은 이 컴퓨터에 연결한 계정마다 동기화 폴더 위치를 `info.json` 에 적고, 드롭박스 도움말은 다른 프로그램이 동기화 폴더를 찾을 때 이 파일을 읽으라고 안내합니다. 앱은 자기 상태를 `.dbx` 파일에 두는데, 이 파일은 SQLite 암호화 확장 (SQLite Encryption Extension, SEE) 으로 암호화한 SQLite 파일입니다 (2017년 자료). DB 키를 만드는 재료는 사용자 레지스트리의 `ks`, `ks1` 키에 있습니다.

포렌식에서 이 기록을 보는 이유는 아래와 같습니다.

- `info.json` 하나로 동기화 폴더 위치와 개인·회사 계정 여부를 봅니다. 이 파일은 JSON 텍스트라서 바로 읽을 수 있습니다.
- 암호화한 DB 안에는 파일 목록 같은 기록이 있을 수 있습니다. 그러려면 키를 먼저 풀어야 합니다.

## 위치와 버전별 차이

| 기록 | 위치 | 근거 |
|---|---|---|
| `info.json` | `%APPDATA%\Dropbox\info.json` 또는 `%LOCALAPPDATA%\Dropbox\info.json` | 드롭박스 도움말 |
| `.dbx` 파일 | `\Users\<사용자>\AppData\Local\Dropbox\` 와 그 하위 폴더 `instance_db`, `instance1` | 2017년 자료 |
| `instance_db` 안 파일의 키 재료 | `HKCU\SOFTWARE\Dropbox\ks` 의 `Client` 값 | 2017년 자료 |
| `instance1` 과 최상위 `.dbx` 파일의 키 재료 | `HKCU\SOFTWARE\Dropbox\ks1` 의 `Client` 값 | 2017년 자료 |
| `sync_history.db` | `%LOCALAPPDATA%\Dropbox\instance<N>\sync_history.db` | 구현 |

- `%APPDATA%` 는 보통 `C:\Users\<사용자>\AppData\Roaming`, `%LOCALAPPDATA%` 는 `C:\Users\<사용자>\AppData\Local` 입니다.
- `HKCU` 는 사용자 `NTUSER.DAT` 하이브입니다.

| 기준 | 내용 |
|---|---|
| `info.json` | 드롭박스 도움말에 지금 적혀 있는 방식입니다 |
| `.dbx` 암호화와 키 저장 | 2017-04-30 자료입니다. 지금 버전 앱에서도 같은지는 확인하지 못했습니다 |
| 새 버전 파일 | `sync_history.db` 같은 이름은 구현에서만 보았습니다 |

## 구조

### `info.json`

| 키 | 뜻 |
|---|---|
| `personal` | 개인 계정 (최상위 키). 도움말은 최상위 키가 계정 종류를 뜻한다고 적습니다 |
| `business` | 회사 계정 (최상위 키) |
| `path` | 동기화 폴더 위치 |
| `host` | 사용자 계정과 컴퓨터 한 쌍을 가리키는 고유 식별자. 도움말 예시에서는 숫자입니다 |
| `is_team` | 팀에 속했는지 여부 (참·거짓) |
| `subscription_type` | 요금제. 예: `Basic`, `Business` |

`path`, `host`, `is_team`, `subscription_type` 네 키는 `personal` 과 `business` 아래에 각각 들어갑니다. 이 컴퓨터에서 회사 계정과 개인 계정을 연결했으면 최상위 키가 두 개 보이고, 계정이 하나거나 두 계정을 연결하지 않았으면 하나만 보입니다.

아래는 도움말의 키 설명으로 만든 예시입니다. 값은 자리만 표시했습니다.

```json
{
  "personal": {
    "path": "<동기화 폴더 경로>",
    "host": <고유 식별자>,
    "is_team": <참·거짓>,
    "subscription_type": "<요금제>"
  },
  "business": {
    "path": "<동기화 폴더 경로>",
    "host": <고유 식별자>,
    "is_team": <참·거짓>,
    "subscription_type": "<요금제>"
  }
}
```

### `.dbx` 파일과 키 (2017년 자료)

`.dbx` 파일은 SEE 로 암호화한 SQLite 파일이지만, 모든 `.dbx` 가 그런 것은 아니어서 그냥 SQLite 인 것도, base64 파일인 것도 있습니다.

`Client` 값은 DPAPI blob 이고, 앞에는 (버전, 길이) 데이터가, 뒤에는 HMAC 이 붙어 있습니다. DPAPI 를 풀 때는 고정 엔트로피 `d114a55212655f74bd772e37e64aee9b` 를 씁니다. blob 을 풀면 사용자 키가 나오지만 그것만으로는 `.dbx` 를 풀지 못하고, 사용자 키에 PBKDF2(반복 1066회, 고정 솔트 `0D638C092E8B82FC452883F95F355B8E`)를 한 번 더 걸어 DB 키를 만듭니다. DPAPI 를 풀려면 사용자 로그인 비밀번호(또는 그 SHA1 해시)나 그 사용자의 DPAPI 마스터 키가 있어야 합니다. 자료의 저자는 "DBX 보안은 전적으로 DPAPI 보안에 기대고 있다" 고 적었습니다.

```
HKCU\SOFTWARE\Dropbox\ks1   값 Client
  [ 버전·길이 ][ DPAPI blob ][ HMAC ]
                  │  DPAPI 풀기 (고정 엔트로피, 비밀번호·SHA1 해시·마스터 키 가운데 하나 필요)
                  ▼
               사용자 키
                  │  PBKDF2 (반복 1066회, 고정 솔트)
                  ▼
               DB 키  →  instance1 과 최상위 .dbx 풀기

HKCU\SOFTWARE\Dropbox\ks    값 Client  →  같은 과정  →  instance_db 안 파일 풀기
```

- DPAPI blob 과 마스터 키 구조는 [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) 에 있습니다.
- 같은 저자는 복호 도구 모음 decwindbx 를 공개했습니다. 저장소에는 `dbx-key-win-dpapi.py`, `dbx-key-win-live.py`, `dbx-key-win-live.ps1`, `sqlite3dbx` 폴더 등이 있습니다.

### `.dbx` 안 표 (구현)

| 파일 | 표 | 칸 |
|---|---|---|
| `config.dbx` | `config` | `key` 가 `email` 인 행에 계정 메일이 있습니다 |
| `filecache.dbx` | `file_journal` | `local_filename`, `local_timestamp`, `local_size`, `local_mtime`, `local_ctime`, `server_path` |
| `filecache.dbx` | `deleted_fileids` | `server_path`, `date_added` |

`instance.dbx` 라는 이름도 구현에 있었습니다.

### 새 버전 파일 (구현)

구현은 `%LOCALAPPDATA%\Dropbox\instance<N>\sync_history.db` 를 암호화하지 않은 SQLite 로 봅니다. 이 파일에는 표 `sync_history` 가 있고, 칸 `local_path`, `file_event_type`, `direction`, `timestamp` 가 있습니다 (구현). `direction` 은 올리기·내려받기 방향으로 짐작하는데 값 목록은 확인하지 못했습니다. 흔히 거론하는 `aggregation.dbx`, `home.db`, `nucleus.sqlite3` 같은 이름도 이번에 확인하지 못했습니다.

- SQLite 파일을 읽는 법은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에 있습니다.

## 증거로서 의미

### 증명하는 것

- `info.json` 이 있으면, 이 Windows 사용자 프로필에서 드롭박스 계정을 연결한 적이 있습니다.
- `path` 로 동기화 폴더가 어디 있었는지 봅니다.
- 최상위 키로 개인 계정과 회사 계정 가운데 무엇을 연결했는지 봅니다.
- `is_team` 과 `subscription_type` 으로 팀 소속 여부와 요금제를 봅니다.
- `host` 는 사용자 계정과 컴퓨터 조합을 가리킵니다. 같은 계정이 쓴 다른 컴퓨터와 이 컴퓨터를 가르는 데 쓸 수 있습니다 (도움말 설명에서 짐작).
- `ks`, `ks1` 키가 있으면 이 사용자 프로필에 드롭박스 DB 키 재료가 적힌 적이 있습니다 (2017년 자료 기준).

### 증명하지 못하는 것

- 도움말이 설명한 `info.json` 키에는 계정 메일과 시각이 없습니다. 어느 메일 계정인지는 다른 기록에서 찾습니다.
- `host` 값을 드롭박스 서버 쪽 기록과 맞춰 보는 방법은 확인하지 못했습니다.
- 동기화 폴더에 파일이 있다고 그 파일을 올렸다고 단정하지 않습니다. 동기화는 앱이 스스로 합니다.
- 암호화한 DB 를 풀지 못하면 파일 단위 기록은 볼 수 없습니다.
- 구현에서 본 표와 칸으로 무엇을 증명할 수 있는지는 검체에서 이름과 뜻을 확인한 뒤에 판단합니다.

## 시각 해석

- `info.json` 의 키에는 시각이 없습니다.
- `info.json` 파일의 파일 시스템 시각이 무엇이 바뀔 때 바뀌는지는 확인하지 못했습니다.
- 구현에서 본 시각 칸(`local_timestamp`, `local_mtime`, `local_ctime`, `date_added`, `timestamp`)은 단위와 시간대를 확인하지 못했습니다.
- 값의 자릿수로 단위를 먼저 가립니다. 방법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- `local_mtime`, `local_ctime` 은 이름으로 보면 로컬 파일의 시각입니다. `mtime` 은 수정 시각으로 보이지만, `ctime` 이 만든 시각인지 메타데이터를 바꾼 시각인지는 이름만으로 알 수 없습니다. 같은 파일의 MFT 시각과 맞춰 본 뒤에 뜻을 정합니다.

## 함정과 한계

- **자료가 오래됐습니다.** 암호화와 키 저장 방식은 2017년 자료입니다. 지금 버전 앱에서도 같은지 확인하지 못했습니다. 검체의 앱 버전을 먼저 적고, 그 버전에서 키 위치가 맞는지 확인합니다.
- **`info.json` 은 두 곳을 봅니다.** `%APPDATA%` 와 `%LOCALAPPDATA%` 가운데 한쪽에만 있을 수 있습니다.
- **모든 `.dbx` 가 암호화돼 있지는 않습니다.** 파일 앞머리를 먼저 보고 SQLite 인지, base64 인지, 암호화한 파일인지 가립니다. SQLite 파일 머리 모양은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에 있습니다.
- **오프라인에서는 DPAPI 부터 풀어야 합니다.** 2017년 자료는 사용자 로그인 비밀번호(또는 그 SHA1 해시)나 그 사용자의 DPAPI 마스터 키가 필요하다고 적습니다. 셋 다 없으면 이 자료의 방법으로는 풀지 못합니다. 비밀번호 없이 다루는 방법은 [암호화 증거 다루기](../../03-techniques/analysis/encrypted-evidence/index.md) 에 있습니다.
- **살아 있는 PC 에서 키를 뽑을 때는 기록을 남깁니다.** decwindbx 에는 이름에 `live` 가 붙은 스크립트가 있습니다. 살아 있는 PC 에서 도구를 돌리면 PC 에 흔적이 남습니다. 절차는 [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) 을 따릅니다.
- **클라우드 파일 API 사용 여부를 모릅니다.** 드롭박스가 Windows 에서 이 API 로 온라인 전용 파일을 만드는지는 확인하지 못했습니다. `SyncRootManager` 에 드롭박스 공급자 키가 있는지, 동기화 폴더 파일의 특성이 어떤지 검체에서 확인합니다. 방법은 [클라우드 동기화 공통 구조](cloud-files-api-syncrootmanager.md) 에 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

**`Client` 값 배치.** 아래는 2017년 자료의 설명으로 그린 배치입니다. 실제 바이트가 아니며, 각 부분의 길이는 검체에서 확인합니다.

```
HKCU\SOFTWARE\Dropbox\ks1  값 Client
+--------------+------------------------------+--------+
| 버전 · 길이  | DPAPI blob                   | HMAC   |
+--------------+------------------------------+--------+
```

1. 값 데이터를 바이트로 내보냅니다.
2. 앞머리 다음부터 DPAPI blob 이 시작합니다. blob 의 머리 모양은 [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) 에서 보고 시작 자리를 맞춥니다.
3. blob 이 끝난 뒤 남는 바이트가 HMAC 입니다.

**고정 값.** 자료에 나온 두 값을 바이트 순서대로 적으면 아래와 같습니다. 둘 다 16바이트입니다.

```
DPAPI 엔트로피:  d1 14 a5 52 12 65 5f 74 bd 77 2e 37 e6 4a ee 9b
PBKDF2 솔트:     0d 63 8c 09 2e 8b 82 fc 45 28 83 f9 5f 35 5b 8e
```

도구 설정에 이 값을 넣을 때 문자열로 넣는지 바이트로 넣는지 도구 설명을 따릅니다.

**`info.json`.** 텍스트 편집기로 열어 최상위 키가 몇 개인지, `path` 가 가리키는 폴더가 디스크에 있는지 봅니다.

### 공개 도구로 한 번

1. 사용자 프로필에서 `info.json` 두 위치와 `AppData\Local\Dropbox\` 폴더 전체를 사본으로 뜹니다.
2. 사용자 `NTUSER.DAT` 와 트랜잭션 로그를 사본으로 뜹니다. 레지스트리 하이브 뷰어로 `SOFTWARE\Dropbox\ks`, `SOFTWARE\Dropbox\ks1` 의 `Client` 값을 내보냅니다.
3. 사용자 DPAPI 마스터 키 폴더를 함께 모읍니다. 위치는 [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) 에 있습니다.
4. decwindbx 로 키를 풉니다. 이름으로 보면 오프라인 DPAPI 용 스크립트와 살아 있는 PC 용 스크립트가 따로 있습니다. 쓰는 법은 저장소 설명을 따릅니다.
5. 푼 키로 `.dbx` 사본을 엽니다. 표 이름 목록을 먼저 보고, 위 구현 후보가 실제로 있는지 확인합니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 클라우드 동기화 공통 구조 | `SyncRootManager` 에 드롭박스 공급자 키가 있는지 봅니다 | [클라우드 동기화 공통 구조](cloud-files-api-syncrootmanager.md) |
| DPAPI 구조 | `Client` 값의 blob 과 마스터 키를 풉니다 | [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) |
| 설치 프로그램 | 드롭박스 앱을 깔았는지, 언제 깔았는지 봅니다 | [설치 프로그램](../system-account/uninstall.md) |
| 셸백·바로가기 파일 | `path` 아래 폴더를 둘러보거나 파일을 연 기록을 찾습니다 | [셸백](../file-folder-usage/shellbags/index.md), [바로가기 파일](../file-folder-usage/lnk.md) |
| 마스터 파일 테이블 | 동기화 폴더 파일의 시각과 특성을 봅니다 | [마스터 파일 테이블](../filesystem/mft.md) |
| SRUM | 앱별 네트워크 송수신 양을 봅니다 | [SRUM](../execution/system-resource-usage-monitor/index.md) |

반출 여부를 따지는 흐름은 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에 있습니다.

## 실습

드롭박스를 쓴 공개 검체(NIST CFReDS 등)나 직접 만든 시험 PC 에서 아래 질문을 풀어 봅니다.

1. `info.json` 은 `%APPDATA%` 와 `%LOCALAPPDATA%` 가운데 어디에 있습니까? 최상위 키는 몇 개입니까?
2. `path` 가 가리키는 폴더가 디스크에 있습니까? 폴더 안 파일 수는 몇 개입니까?
3. `AppData\Local\Dropbox\` 아래 `.dbx` 파일 가운데 그냥 SQLite 로 열리는 것, base64 인 것, 암호화한 것은 각각 몇 개입니까?
4. `NTUSER.DAT` 에 `SOFTWARE\Dropbox\ks`, `ks1` 키가 있습니까? 없다면 검체의 앱 버전은 무엇입니까?
5. 키를 풀었다면 `.dbx` 안의 표 이름을 이 페이지의 구현 후보와 맞춰 봅니다. 없는 이름은 무엇입니까?
6. `sync_history.db` 같은 암호화하지 않은 SQLite 가 `instance<N>` 폴더에 있습니까?

## 참고 문헌

1. dfirfpi (Francesco Picasso), "Brush up on Dropbox DBX decryption" (2017-04-30) — http://blog.digital-forensics.it/2017/04/brush-up-on-dropbox-dbx-decryption.html
2. dfirfpi/decwindbx, GitHub 저장소 — https://github.com/dfirfpi/decwindbx
3. Dropbox 도움말, 동기화 폴더 경로를 프로그램으로 찾는 법(info.json) — https://help.dropbox.com/installs/locate-dropbox-folder
