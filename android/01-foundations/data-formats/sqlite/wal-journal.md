---
title: "WAL과 저널"
parent: "SQLite 데이터베이스"
grand_parent: "기반 · 데이터 저장 형식"
nav_order: 170
---

# WAL과 저널 (WAL·Journal)

SQLite 는 DB 를 고치는 동안 주 파일 옆에 롤백 저널(-journal)이나 WAL(-wal)과 WAL 색인(-shm)을 두고, 이 곁 파일에는 주 파일에 아직 없는 새 내용이나 고치기 전 옛 내용이 남을 수 있습니다. 이 페이지는 세 파일의 구조와 Android 의 기본 저널 설정, 증거를 확보하고 읽을 때 조심할 점을 다룹니다.

## 세 곁 파일

곁 파일은 주 DB 파일과 같은 폴더에 있고, 주 파일 이름 끝에 정해진 말이 붙습니다 [1].

| 곁 파일 | 무엇을 담나 | 언제 생기나 |
|---|---|---|
| `이름-journal` | 롤백 저널 (Rollback Journal). 거래가 바꾸기 전의 원래 페이지 사본 | 롤백 저널 모드에서 쓰기 거래가 있을 때 |
| `이름-wal` | 미리 쓰기 로그 (Write-Ahead Log, WAL). 커밋한 새 페이지 | WAL 모드에서 DB 를 열어 쓸 때 |
| `이름-shm` | WAL 색인 (WAL-index). WAL 에서 페이지를 빨리 찾는 색인 | WAL 모드에서 DB 를 열 때 |

롤백 저널은 "고치기 전" 을, WAL 은 "고친 뒤" 를 담는다는 점이 해석의 출발점입니다. 한 DB 가 어느 모드인지는 파일 머리 오프셋 18·19 로 알 수 있고, 두 값이 2 면 WAL 모드입니다. WAL 모드는 DB 에 저장돼서 다시 열어도 유지됩니다 [1][2]. 머리 필드 전체는 [페이지와 레코드](b-tree-record.md)에 있습니다.

## 롤백 저널 (-journal)

SQLite 는 한 번에 쓰기 거래를 하나만 해서 저널도 하나뿐입니다 [1]. 저널 머리는 아래와 같고, 머리 뒤쪽은 디스크 섹터 크기까지 0 으로 채웁니다 [1].

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0 | 8 | 매직 `d9 d5 05 f9 20 a1 63 d7` |
| 8 | 4 | 페이지 기록 수(−1 이면 파일 끝까지 전부) |
| 12 | 4 | 체크섬 계산에 쓰는 난수(nonce) |
| 16 | 4 | 거래 전 DB 크기(페이지 수) |
| 20 | 4 | 디스크 섹터 크기 |
| 24 | 4 | 페이지 크기 |

머리 뒤에는 페이지 기록이 이어지고, 기록 하나는 페이지 번호(4바이트)와 바뀌기 전 원래 페이지 내용, 체크섬(4바이트)으로 되어 있습니다 [1]. 저널 안의 페이지는 거래가 지우거나 고친 행이 들어 있던 옛 페이지라서, 주 파일에는 없는 행이 여기서 나올 수 있습니다.

거래를 끝낸 뒤 저널을 어떻게 치우는지는 저널 모드 (journal_mode) 가 정합니다 [1].

| 모드 | 거래를 끝낼 때 | 포렌식에서 보는 점(해석) |
|---|---|---|
| DELETE | 저널 파일을 지움 | 파일 시스템의 지운 영역에 내용이 남을 수 있음 |
| TRUNCATE | 파일 길이를 0 으로 자름 | 파일은 남지만 길이가 0 이고, 내용은 파일 시스템 쪽에서 찾아야 함 |
| PERSIST | 머리만 무효값(예: 0)으로 덮음 | 파일 안에 옛 페이지 기록이 그대로 남을 수 있음 |

거래 도중에 멈춰서 복구에 필요한 내용이 남은 저널을 hot journal 이라고 부릅니다 [1]. 이런 저널에는 끝나지 않은 거래가 바꾸기 전의 페이지가 들어 있어서, 전원이 꺼지거나 앱이 비정상으로 끝난 직후 확보한 이미지라면 -journal 파일의 길이와 첫 8바이트를 먼저 봅니다.

아래는 명세로 만든 저널 머리 첫 줄의 예시이고, 실제 파일의 값이 아닙니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f
0000    d9 d5 05 f9 20 a1 63 d7 .. .. .. .. .. .. .. ..   매직 8바이트, 이어서 기록 수·nonce
```

길이가 0 인 -journal 파일이나 첫 8바이트가 이 매직이 아닌 -journal 파일은 TRUNCATE 나 PERSIST 로 이미 끝난 저널일 가능성이 크고, 이 판단은 위 모드 설명에서 끌어낸 해석입니다.

## WAL (-wal)

WAL 파일은 32바이트 머리 뒤에 프레임이 이어지는 구조입니다 [1].

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0 | 4 | 매직. 0x377f0682 면 체크섬이 리틀엔디언, 0x377f0683 이면 빅엔디언 |
| 4 | 4 | 형식 버전 3007000 |
| 8 | 4 | 페이지 크기 |
| 12 | 4 | 체크포인트 순번 |
| 16 | 4 | salt-1 |
| 20 | 4 | salt-2 |
| 24 · 28 | 4 · 4 | 머리 체크섬 |

프레임 (Frame) 하나는 24바이트 프레임 머리와 페이지 한 장입니다 [1].

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0 | 4 | 페이지 번호 |
| 4 | 4 | 커밋 프레임이면 커밋 뒤 DB 크기(페이지 수), 아니면 0 |
| 8 · 12 | 4 · 4 | salt-1 · salt-2 사본 |
| 16 · 20 | 4 · 4 | 누적 체크섬 |

프레임은 salt 두 값이 WAL 머리와 같고 누적 체크섬이 맞을 때만 유효합니다. SQLite 가 페이지를 읽을 때는 WAL 에서 그 페이지의 커밋된 가장 마지막 유효 프레임을 쓰고, 그런 프레임이 없으면 주 파일에서 읽습니다 [1]. 같은 페이지를 여러 번 고쳤다면 옛 버전 프레임도 WAL 에 함께 남아 있을 수 있어서, 프레임을 순서대로 보면 한 행이 어떻게 바뀌었는지 따라갈 수 있습니다.

체크포인트 (Checkpoint) 는 WAL 내용을 주 파일로 옮기는 일이고, 모드는 PASSIVE·FULL·RESTART·TRUNCATE 가 있으며 자동 체크포인트는 PASSIVE 입니다 [2]. 체크포인트가 끝나고 읽는 쪽이 없으면 SQLite 는 salt-1 을 1 올리고 salt-2 를 새 난수로 바꾼 뒤 WAL 을 앞에서부터 다시 쓰고, 보통 파일을 자르지는 않습니다 [1][2]. 그래서 새 salt 와 맞지 않는 뒤쪽 옛 프레임은 무효지만, 덮이기 전까지 바이트는 남을 수 있습니다. 이 옛 프레임은 SQLite 가 읽지 않아서 클라이언트로 DB 를 열어서는 보이지 않고, 헥스나 WAL 을 따로 푸는 도구로 봐야 합니다.

마지막 연결이 닫히면 SQLite 는 체크포인트를 한 번 하고 -wal 과 -shm 을 지웁니다. 다만 앱이 SQLITE_FCNTL_PERSIST_WAL 을 쓰거나 프로세스가 정상으로 끝나지 않으면 WAL 이 남을 수 있습니다 [2].

## WAL 색인 (-shm)

-shm 은 WAL 에서 페이지를 빨리 찾기 위한 색인이고, 일시적인 파일이라 망가지면 WAL 로 다시 만듭니다. 영구 DB 상태에는 들어가지 않습니다 [1]. 바이트 순서는 빅엔디언으로 고정돼 있지 않고 기기 고유 순서를 씁니다. 안에 있는 mxFrame 은 유효 프레임 수이고, 읽는 쪽은 거래를 시작할 때의 값을 기억해 같은 시점을 봅니다 [1]. 분석의 중심은 -wal 이지만, -shm 도 확보할 때 함께 복사해 둡니다.

## Android 의 기본 저널 설정

Android 플랫폼은 SQLite 기본값 몇 가지를 자기 설정으로 바꿔 둡니다. 아래 값은 현행 AOSP 의 config.xml 과 빌드 파일 기준입니다 [5][6].

| 항목 | 값 | 비고 |
|---|---|---|
| WAL 이 아닐 때 기본 저널 모드 (`db_default_journal_mode`) | TRUNCATE | `debug.sqlite.journalmode` 속성이 덮어씀 [4] |
| 저널 크기 한도 (`db_journal_size_limit`) | 524288바이트 | 커밋 뒤 이보다 크면 잘라냄. 플랫폼 SQLite 빌드 기본값은 1048576 [6] |
| 기본 동기화 | FULL | WAL 이 아닐 때 |
| WAL 동기화 | NORMAL | |
| WAL 자동 체크포인트 (`db_wal_autocheckpoint`) | 100페이지 | SQLite 기본은 1000페이지 [2]. `debug.sqlite.wal.autocheckpoint` 속성이 덮어씀 [4] |
| WAL 연결 수 (`db_connection_pool_size`) | 4 | |
| WAL 파일 자르기 기준 (`db_wal_truncate_size`) | 1048576바이트 | WAL 로 열 때 기존 WAL 이 이보다 크면 자름. `debug.sqlite.wal.truncatesize` 속성이 덮어씀 [4] |

PERSIST 는 거래가 끝난 뒤에도 저널에 데이터를 남겨서 SECURE_DELETE 와 잘 맞지 않습니다 [5]. SECURE_DELETE 가 Android 에서 어떻게 켜져 있는지는 [지운 레코드 되살리기](freelist-freeblock.md)에서 다룹니다.

WAL 자르기 기준은 앱이 DB 를 다시 열 때 적용돼서, 확보 전에 앱이 DB 를 다시 열면 큰 WAL 의 옛 프레임이 사라질 수 있습니다. 이 부분은 설정 주석에서 끌어낸 해석입니다.

### 호환 WAL

Android 9 에서 호환 WAL (Compatibility WAL) 이 들어왔습니다. journal_mode=WAL 을 쓰되 DB 하나에 연결을 하나만 유지하는 방식입니다 [3]. AOSP 문서에는 호환 WAL 이 기본으로 켜져 있다고 되어 있습니다 [3]. 앱이 `enableWriteAheadLogging()`·`disableWriteAheadLogging()`·`OpenParams.setJournalMode()` 를 부르면 호환 WAL 을 쓰지 않습니다 [3]. 같은 문서에는 제조사가 `db_compatibility_wal_supported` 리소스를 false 로 덮어써서 끌 수 있다고 되어 있지만, 현행 AOSP config.xml 에는 이 이름이 없습니다 [3][5]. Room 은 API 16 이상이고 저메모리 기기가 아니면 호환 WAL 이 아닌 전체 WAL 을 씁니다 [3].

설정 값 쪽에서는 settings global 의 `sqlite_compatibility_wal_flags` 키가 호환 WAL 을 조정합니다. 값은 쉼표로 나눈 key=value 목록이고, 읽는 키는 `legacy_compatibility_wal_enabled`(기본 false), `wal_syncmode`, `truncate_size`(기본 −1) 세 개입니다. `truncate_size` 가 0 이상이면 위 표의 WAL 자르기 기준보다 이 값이 먼저이고, 프로세스마다 처음 읽은 값을 저장해 두고 씁니다(현행 AOSP 기준) [7][4]. 문서의 "기본 켜짐" 과 AOSP 의 `legacy_compatibility_wal_enabled` 기본값 false 가 서로 달라서, 최신 Android 에서 일반 앱 DB 의 실제 기본 저널 모드는 실제 기기에서 확인합니다. 설정 키를 읽는 법은 [설정 값](../../../02-artifacts/system-account/settings.md)에서 다룹니다.

| 범위 | 내용 |
|---|---|
| Android 9 | 호환 WAL 도입 [3] |
| 현행 AOSP(main) | 위 표의 기본값, `sqlite_compatibility_wal_flags` 키 해석 [4][5][7] |
| Android 16, One UI 8.5 | settings global 에 `sqlite_compatibility_wal_flags` 키가 있음 |
| 그 밖의 버전, One UI 의 따로 바꾼 설정 | 실제 기기에서 settings global 의 키 값과 DB 의 `PRAGMA journal_mode` 로 확인 |

## 포렌식에서 중요한 점

증거를 확보할 때는 주 DB 파일과 -wal·-shm·-journal 을 한꺼번에 복사합니다. DB 파일이 WAL 파일과 떨어지면 이미 커밋한 거래를 잃거나 DB 가 망가질 수 있습니다 [2]. 주 파일만 가져오면 WAL 에만 있던 최근 기록이 빠지고, 이 누락은 결과 화면에서 드러나지 않습니다. 확보 절차는 [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md)에서 다룹니다.

SQLite 3.22.0(2018-01-22)부터는 -shm 과 -wal 이 이미 있고 읽을 수 있거나, 폴더에 쓰기 권한이 있거나, immutable 옵션을 주면 WAL DB 를 읽기 전용으로 열 수 있고, 그 전에는 쓰기 권한이 필요했습니다 [2]. 쓰기 권한이 있는 채로 클라이언트가 DB 를 열고 닫으면 체크포인트가 일어나 WAL 이 주 파일에 합쳐지고 -wal 이 지워질 수 있습니다. 그래서 원본은 해시를 남긴 뒤 손대지 않고, 사본에서만 DB 를 엽니다.

한 DB 에서 볼 수 있는 상태는 세 겹으로 나눠 볼 수 있고, 아래는 위 구조에서 끌어낸 해석입니다. 주 파일은 마지막 체크포인트 시점, 주 파일에 WAL 의 유효 프레임을 얹은 결과는 마지막 커밋 시점, WAL 의 옛 프레임과 저널의 원래 페이지는 그보다 앞선 시점의 내용입니다. 보고서에는 어느 겹에서 나온 행인지 함께 적습니다. 지운 행을 되살리는 다른 자리는 [지운 레코드 되살리기](freelist-freeblock.md)에 있습니다.

## 함정

- -wal 파일이 없다고 WAL 모드가 아니라고 보지 않습니다. 마지막 연결이 정상으로 닫히면 -wal 은 지워지고, 모드는 파일 머리 오프셋 18·19 로 판단합니다.
- WAL 파일 크기로 유효 프레임 수를 셈하면 안 됩니다. 재설정 뒤에도 파일을 자르지 않아서 뒤쪽 프레임이 옛 salt 를 달고 남아 있을 수 있습니다.
- -shm 의 바이트 순서는 기기마다 다를 수 있어서, 다른 기기에서 만든 -shm 을 같은 순서로 읽으면 값이 틀립니다.
- DB 가 암호화돼 있으면 WAL 과 롤백 저널의 페이지도 같은 키로 암호화돼 있습니다. [암호화된 SQLite](sqlcipher.md)를 봅니다.

## 참고 문헌

1. Database File Format — SQLite, https://www.sqlite.org/fileformat2.html
2. Write-Ahead Logging — SQLite, https://www.sqlite.org/wal.html
3. Compatibility write-ahead logging for apps — Android Open Source Project, https://source.android.com/docs/core/perf/compatibility-wal
4. SQLiteGlobal.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/database/sqlite/SQLiteGlobal.java
5. config.xml — AOSP frameworks/base core/res (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/res/res/values/config.xml
6. Android.bp — AOSP external/sqlite dist (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_external_sqlite/main/dist/Android.bp
7. SQLiteCompatibilityWalFlags.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/database/sqlite/SQLiteCompatibilityWalFlags.java
