---
title: "LevelDB 저장소"
parent: "기반 · 데이터베이스·로그 형식"
nav_order: 310
---

# LevelDB 저장소 (LevelDB)

> 위치: 기반 구조 > 데이터베이스·로그 형식

LevelDB 는 키와 값을 한 폴더 안의 여러 파일에 나눠 담는 저장 형식이며, 크롬 계열 브라우저와 여러 Electron 앱이 이 형식을 씁니다.
새 변경은 먼저 로그 파일(`.log`)에 덧붙이고, 로그가 차면 키 순서로 정렬한 표 파일(`.ldb`)로 옮깁니다.
지운 값과 예전 값도 한동안 파일에 남지만, 압축 정리가 돌면 사라질 수 있습니다.

## 이 형식을 쓰는 아티팩트

### 크롬 계열 브라우저

크롬과 크로뮴 계열 브라우저는 IndexedDB 데이터를 LevelDB 에 저장합니다[10]. 판마다 다를 수 있어 실제 데이터로 확인합니다.
아래 폴더도 LevelDB 구성입니다.

| 폴더 (프로필 폴더 기준) | 쓰는 곳 | 들어 있는 파일 |
|---|---|---|
| `Local Storage\leveldb\` | 크롬·엣지 | `CURRENT`, `LOCK`, `LOG`, `LOG.old`, `MANIFEST-000001`, 6자리 번호 `.log`, 6자리 번호 `.ldb` |
| `Session Storage\` | 엣지 | `000003.log`, `CURRENT`, `LOCK`, `LOG`, `LOG.old`, `MANIFEST-000001` |
| `IndexedDB\<출처>_0.indexeddb.leveldb\` | 엣지 | 폴더 이름 예: `https_ntp.msn.com_0.indexeddb.leveldb` |
| `Local Extension Settings\<확장 ID>\` | 브라우저 확장 설정 | `CURRENT`, `LOCK`, `LOG`, `MANIFEST-…`, `*.log`, `*.ldb` |

프로필 폴더는 `%LOCALAPPDATA%\...\User Data\Default\` 입니다.
브라우저마다 다른 경로와 각 폴더 값의 해석, 로컬 스토리지의 키·값 인코딩은 [크롬 계열 브라우저](../../02-artifacts/browsers/chrome-edge-whale/index.md) 에서 다루고, 이 페이지는 LevelDB 겉포장만 다룹니다.

### Electron 앱

LevelDB 를 쓰는 Electron 앱은 아래와 같습니다[10].

- Discord, GitHub Desktop, Signal 데스크톱, Skype, Slack, Microsoft Teams, WebTorrent, WhatsApp 데스크톱, Microsoft Yammer

판마다 바뀔 수 있어 실제 데이터로 확인합니다.
앱별 흔적은 [디스코드](../../02-artifacts/messengers/discord.md), [시그널](../../02-artifacts/messengers/signal.md), [스카이프](../../02-artifacts/messengers/skype.md), [슬랙](../../02-artifacts/messengers/slack.md), [마이크로소프트 팀즈](../../02-artifacts/messengers/teams.md), [왓츠앱 데스크톱](../../02-artifacts/messengers/whatsapp-desktop.md) 페이지에서 다룹니다.
이런 앱이 공통으로 쓰는 폴더 구조는 [크롬 계열 앱 공통 구조](../app-mail-data/chromium-electron-webview2/index.md) 에 있습니다.

### 버전

아래 형식은 google/leveldb 라이브러리의 문서(`doc/`)와 소스(`db/`)를 기준으로 합니다.
Windows 버전에 따라 달라지는지는 공개 자료에 나와 있지 않습니다.

## 구조

> 그림 자리: 쓰기 요청 → `.log` 와 메모리 표 → 로그가 약 4MB 가 차면 레벨 0 `.ldb` → 압축 정리로 레벨 1, 레벨 2 … 로 내려가는 흐름. 옆에 `CURRENT` → `MANIFEST-` → 레벨별 `.ldb` 목록으로 이어지는 화살표

### 파일 구성과 이름

| 파일 | 이름 형식 | 하는 일 |
|---|---|---|
| 로그 파일 (Log File) | `%06llu.log` | 최근 변경을 차례로 덧붙입니다 |
| 표 파일 (Table File) | `%06llu.ldb` | 키 순서로 정렬한 항목을 담습니다. 항목마다 값이나 삭제 표시 (Deletion Marker) 가 붙습니다 |
| 옛 표 파일 | `%06llu.sst` | `.ldb` 와 같은 표 파일입니다 |
| MANIFEST | `MANIFEST-%06llu` | 레벨마다 어떤 표 파일이 있는지 적습니다. 키 범위 같은 메타데이터도 적습니다 |
| CURRENT | 고정 이름 | 최신 MANIFEST 의 파일 이름을 적은 텍스트 파일입니다 |
| LOG, LOG.old | 고정 이름 | 정보 메시지를 적는 텍스트 로그입니다 |
| LOCK | 고정 이름 | 크롬·엣지에서는 0바이트입니다 |
| 임시 파일 | `%06llu.dbtmp` | 임시 파일입니다 |

- `%06llu` 는 10진수 6자리 번호입니다. 모자란 앞자리는 0 으로 채웁니다[4].
- 번호의 예는 `001715.ldb`, `005312.log`, `005313.ldb` 입니다.
- 파일 이름을 해석할 때 LevelDB 는 `.sst` 와 `.ldb` 를 똑같이 표 파일로 봅니다[4].
- MANIFEST 도 로그 형식으로 적습니다. 상태가 바뀔 때마다 그 내용을 덧붙입니다[1].

크롬·엣지의 예는 아래와 같습니다.

크롬·엣지의 `CURRENT` 는 16바이트이고 내용은 `MANIFEST-000001` 입니다. 이 글자는 15바이트라서 1바이트가 더 있습니다. 이 1바이트가 줄바꿈인지는 헥스로 확인합니다.
`LOG` 크기는 크롬이 약 107KB, 엣지가 1,003바이트처럼 서로 다릅니다.

### 레벨과 압축 정리

로그와 표 파일의 관계는 아래와 같습니다[1].

로그 파일과 같은 내용이 메모리에도 있는데, 이것을 메모리 표 (Memtable) 라고 부르며 읽을 때마다 먼저 봅니다.
로그 파일이 기본값으로 약 4MB 가 되면 정렬된 표 파일로 바꾸고 새 로그 파일을 만듭니다.
표 파일은 레벨 (Level) 별로 묶습니다.

| 레벨 | 파일끼리 키 범위 | 크기 한도 |
|---|---|---|
| 0 | 겹칠 수 있습니다 | 크기가 아니라 파일 수로 봅니다. 4개가 되면 압축 정리를 시작합니다[6] |
| 1 | 겹치지 않습니다 | 10MB |
| 2 | 겹치지 않습니다 | 100MB |
| L (1 이상) | 겹치지 않습니다 | 10^L MB |

압축 정리 (Compaction) 는 아래 순서로 돕니다[1].

1. 레벨 L 이 한도를 넘으면 레벨 L 파일 하나를 고릅니다. 레벨 0 에서는 겹치는 파일 여러 개를 함께 고를 수 있습니다.
2. 그 파일과 키 범위가 겹치는 레벨 L+1 파일을 모두 합칩니다.
3. 결과는 2MB 단위 파일로 나눠 씁니다.
4. 합치면서 덮어쓴 옛 값을 버립니다.
5. 삭제 표시도 버립니다. 단, 더 높은 번호의 레벨에 겹치는 항목이 없는 삭제 표시만 버립니다.
6. 압축 정리와 복구가 끝나면 `RemoveObsoleteFiles()` 가 파일을 지웁니다. 현재 것이 아닌 로그 파일과, 어디에서도 참조하지 않는 표 파일이 대상입니다.

### 로그 파일 (.log)

로그 파일은 32KB(32,768바이트) 블록이 이어진 것입니다. 마지막 블록은 덜 찰 수 있습니다[2].
블록 안에는 레코드가 이어집니다.
레코드 머리는 7바이트입니다.

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 4 | 검사합 (checksum) | 종류와 데이터를 덮는 crc32c 입니다. 리틀 엔디언 |
| 4 | 2 | 길이 (length) | 데이터의 바이트 수입니다. 리틀 엔디언 |
| 6 | 1 | 종류 (type) | 아래 표 |
| 7 | 길이 값 | 데이터 (data) | 쓰기 묶음 전체나 그 조각 |

| 종류 값 | 이름 | 뜻 |
|---|---|---|
| 1 | FULL | 사용자 레코드 하나가 통째로 들어 있습니다 |
| 2 | FIRST | 첫 조각입니다 |
| 3 | MIDDLE | 가운데 조각입니다 |
| 4 | LAST | 마지막 조각입니다 |

사용자 레코드 하나가 블록을 넘으면 FIRST·MIDDLE·LAST 로 나눕니다.
레코드는 블록의 마지막 6바이트 안에서 시작하지 않고, 그 남는 자리는 0 으로 채운 꼬리이며 읽는 쪽은 이 꼬리를 건너뜁니다.
블록에 정확히 7바이트가 남으면 데이터가 0바이트인 FIRST 레코드를 쓰고, 나머지는 다음 블록부터 이어 씁니다.

### 쓰기 묶음 (WriteBatch)

로그 레코드의 데이터를 이어 붙이면 쓰기 묶음 하나가 나옵니다[5].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 8 | sequence (fixed64) | 첫 레코드의 순서 번호 (Sequence Number) |
| 8 | 4 | count (fixed32) | 레코드 개수 |
| 12 | 가변 | record × count | 아래 두 가지 가운데 하나 |

- 묶음 머리는 12바이트입니다[5][10].
- 값 쓰기 레코드는 `kTypeValue` 태그, 키, 값 순서입니다.
- 지우기 레코드는 `kTypeDeletion` 태그, 키 순서입니다.
- 키와 값은 varstring 형식입니다. 길이(varint32) 뒤에 그 길이만큼 데이터가 옵니다.
- varint32 는 값 크기에 따라 바이트 수가 달라지는 정수입니다.
- 첫 레코드의 순서 번호는 머리의 sequence 값입니다.
- 뒤 레코드의 순서 번호는 하나씩 1 늘어납니다.
- 모르는 태그를 만나면 LevelDB 는 "unknown WriteBatch tag" 손상 오류를 냅니다.

- fixed64·fixed32 는 가장 낮은 바이트를 먼저 씁니다. 곧 리틀 엔디언입니다[7].
- 태그 값은 `kTypeDeletion` 이 0, `kTypeValue` 가 1 입니다[6].

### 표 파일 (.ldb)

표 파일은 앞에서부터 아래 순서로 이어집니다[3].

| 부분 | 담는 것 |
|---|---|
| 데이터 블록 (Data Block) 여러 개 | 키 순서로 정렬한 키와 값. 압축했을 수 있습니다 |
| 메타 블록 (Meta Block) 여러 개 | 필터 등 |
| 메타인덱스 블록 (Metaindex Block) | 메타 블록 이름마다 블록 핸들 하나 |
| 인덱스 블록 (Index Block) | 데이터 블록마다 한 항목. 키는 그 블록의 마지막 키 이상인 문자열이고, 값은 그 블록의 블록 핸들입니다 |
| 파일 꼬리 (Footer) | 두 블록 핸들과 매직 |

블록 핸들 (BlockHandle) 은 두 값입니다.

- offset(varint64): 블록이 파일 안에서 시작하는 위치
- size(varint64): 블록 크기

파일 꼬리는 파일 끝에 있습니다. 시작 위치는 파일 크기에서 48을 뺀 곳입니다.

| 꼬리 안 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 가변 | metaindex_handle | 메타인덱스 블록의 블록 핸들 |
| 가변 | 가변 | index_handle | 인덱스 블록의 블록 핸들 |
| 가변 | 나머지 | 0 채움 | 앞 두 핸들과 합쳐 40바이트를 채웁니다 |
| 40 | 8 | 매직 (Magic) | `0xdb4775248b80fb57`, 리틀 엔디언 |

- 꼬리 크기는 48바이트입니다. 40바이트와 매직 8바이트를 더한 값과 맞습니다.
- 매직을 디스크 바이트 순서로 쓰면 `57 FB 80 8B 24 75 47 DB` 입니다[10].

블록 안쪽은 아래와 같습니다.

- 블록마다 뒤에 5바이트 블록 꼬리가 붙습니다. 압축 종류 1바이트와 CRC 4바이트입니다[8].
- 압축 종류 값은 0 이 압축 없음, 1 이 Snappy, 2 가 Zstd 입니다[9].
- 크롬 `.ldb` 블록은 Snappy 로 압축돼 있습니다[10].
- 블록 안에서 키 앞부분이 앞 키와 같으면 그 부분을 공유합니다(key sharing).
- 필터 메타 블록은 2KB(base) 범위마다 필터를 하나씩 만듭니다. 필터 데이터 뒤에 필터마다 4바이트 오프셋이 이어집니다. 그 뒤에 오프셋 배열의 시작 위치 4바이트, 맨 끝에 1바이트 lg(base) 가 옵니다[3].

### 내부 키 (Internal Key)

키의 마지막 8바이트는 아래와 같습니다[10].

- 상위 7바이트는 56비트 순서 번호입니다.
- 가장 아래 1바이트는 상태 바이트입니다.
- 상태 바이트가 0 이면 삭제, 1 이면 유효한 값입니다.
- 이 8바이트는 `(순서 번호 << 8) | 종류` 로 묶은 fixed64 입니다[6].
- fixed64 는 리틀 엔디언이라 디스크에서는 상태 바이트가 8바이트 가운데 맨 앞에 옵니다.

로그의 쓰기 묶음에서는 순서 번호가 묶음 머리에 한 번만 나옵니다.
표 파일에서 키를 읽을 때는 이 8바이트로 순서 번호와 삭제 여부를 봅니다.

## 읽는 법

1. 폴더를 통째로 복사하고 사본에서 작업합니다. 이유는 아래 "함정" 에 있습니다.
2. `CURRENT` 를 텍스트로 열어 최신 MANIFEST 이름을 확인합니다.
3. 그 MANIFEST 에서 레벨마다 어떤 표 파일이 있는지 봅니다.
4. `.log` 를 32KB 블록 단위로 읽습니다. 레코드 머리를 차례로 읽고, FIRST·MIDDLE·LAST 조각을 이어 붙여 쓰기 묶음을 얻습니다.
5. 쓰기 묶음 머리의 sequence 와 count 로 레코드마다 순서 번호를 매깁니다.
6. `.ldb` 는 파일 끝 48바이트의 꼬리부터 읽습니다. 꼬리 → 인덱스 블록 → 데이터 블록 순서로 따라갑니다.
7. 블록 꼬리의 압축 종류가 1 이면 Snappy 를 풀어야 읽힙니다.
8. 같은 키가 여러 번 나오면 순서 번호를 비교합니다. 가장 큰 것을 최신 값으로 봅니다.
9. 최신 항목이 삭제 표시면 그 키는 지운 상태로 봅니다.

8번은 순서 번호가 1씩 늘어나는 규칙[5]과 압축 정리 설명[1]에서 끌어낸 해석입니다.

### 헥스로 따라가기

아래 바이트는 명세로 만든 예시입니다. 실제 데이터에서 뽑은 값이 아닙니다.

**표 파일의 꼬리 찾기.** 파일 크기가 0x1000(4,096)바이트인 `.ldb` 를 예로 듭니다.

```
오프셋   바이트                      뜻
0FD0    (가변)                     metaindex_handle — varint64 두 개
....    (가변)                     index_handle — varint64 두 개
....    00 …                       0 채움 (0FD0 부터 여기까지 40바이트)
0FF8    57 FB 80 8B 24 75 47 DB    매직
```

- 꼬리 시작은 0x1000 − 48 = 0x0FD0 이고, 매직 시작은 0x0FD0 + 40 = 0x0FF8 입니다.
- 끝 8바이트를 리틀 엔디언으로 읽으면 `0xdb4775248b80fb57` 이며, 이 값이 아니면 파일이 잘렸거나 표 파일이 아닐 수 있습니다.
- 두 핸들은 varint64 라서 바이트 수가 값마다 다르므로 앞에서부터 차례로 읽습니다.

**로그 파일의 첫 레코드.**

```
오프셋   바이트          칸
0000    xx xx xx xx     검사합 (crc32c. 이 예시에서는 계산하지 않았습니다)
0004    1A 00           길이 = 0x001A = 26
0006    01              종류 = 1 (FULL)
0007    (26바이트)       쓰기 묶음
0021    …               다음 레코드 머리
```

- 길이는 리틀 엔디언이라 `1A 00` 은 26입니다.
- 종류가 FULL 이라 이 레코드 하나가 쓰기 묶음 하나입니다.
- 쓰기 묶음은 0x0007 에서 시작합니다. 앞 8바이트가 sequence, 다음 4바이트가 count 입니다.
- 레코드들은 0x0013 부터 14바이트입니다.
- 다음 레코드 머리는 0x0007 + 26 = 0x0021 에 있습니다.

**블록 경계.** 첫 블록은 0x0000 부터 0x7FFF 까지입니다.

- 레코드가 0x7FF8 에서 끝나면 7바이트(0x7FF9~0x7FFF)가 남습니다. 이 자리에는 데이터 0바이트짜리 FIRST 레코드가 들어갑니다. 내용은 0x8000 부터 이어집니다.
- 레코드가 0x7FF9 에서 끝나면 6바이트(0x7FFA~0x7FFF)가 남습니다. 이 자리는 0 으로 채운 꼬리입니다. 다음 레코드는 0x8000 에서 시작합니다.

## 포렌식에서 중요한 점

### 지운 데이터

- 지우기는 삭제 표시를 더하는 방식입니다[10].
- 압축 정리가 중복을 정리한 뒤에도 이전 레벨 파일에 옛 값과 지운 값이 남아 있을 수 있습니다. 그래서 지운 레코드를 되살릴 수 있습니다[10].
- 압축 정리는 덮어쓴 값과 삭제 표시를 버립니다[1]. 압축 정리가 돈 뒤에는 옛 값이 파일에서 사라질 수 있습니다.
- 쓸모없어진 로그 파일과 표 파일은 라이브러리가 지웁니다[1].
- 지운 파일을 비할당 영역에서 찾는 일반 방법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 있습니다.
- 예전 시점의 폴더는 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 찾아볼 수 있습니다.

### 문자열 검색과 카빙

로그 파일은 키와 값을 압축하지 않아서 문자열 검색과 카빙이 됩니다[10].
`.ldb` 블록은 Snappy 로 압축돼 있으면 풀어야 읽히므로[10], 디스크 전체 문자열 검색만으로는 `.ldb` 안의 값을 놓칠 수 있습니다. 검색 방법은 [파일 내용 검색](../../03-techniques/analysis/content-search/index.md) 을 봅니다.

### 손상

- 로그 레코드마다 crc32c 검사합이 있습니다. 이 값으로 레코드가 온전한지 봅니다.
- 손상을 만나면 다음 32KB 블록 경계로 가서 다시 읽습니다. 추측 없이 레코드 경계를 다시 맞출 수 있습니다[2].
- 쓰기 묶음에서 모르는 태그를 만나면 LevelDB 는 손상 오류를 냅니다. 직접 짠 파서도 이 자리에서 멈추고 표시해 두는 편이 안전합니다.

### 비정상 종료와 다시 열기

LevelDB 는 DB 를 열 때 아래 순서로 복구합니다[1].

1. `CURRENT` 에서 최신 MANIFEST 이름을 읽습니다.
2. 그 MANIFEST 를 읽습니다.
3. 남은 옛 파일을 정리합니다.
4. 로그 내용을 새 레벨 0 표 파일로 바꿉니다.
5. 새 쓰기는 새 로그 파일로 보냅니다. 순서 번호는 복구한 번호를 이어받습니다.

로그가 약 4MB 가 차거나 DB 를 다시 열어야 로그 내용이 표 파일로 옮겨 가므로, 그 전까지 최근 변경은 `.log` 에만 있을 수 있습니다.
엣지 `Session Storage\` 폴더처럼 `.ldb` 없이 `000003.log` 만 있는 경우도 있습니다.

### 시각

로그·쓰기 묶음·표 파일 구조에는 시각 필드가 없습니다[2][5][3].
순서 번호는 쓰기 순서만 알려 줄 뿐 언제 썼는지는 알려 주지 않습니다.
시각이 필요하면 `.log`·`.ldb` 파일 자체의 파일 시스템 시각을 보고([마스터 파일 테이블](../../02-artifacts/filesystem/mft.md) 을 봅니다), 값 안에 앱이 시각을 적었다면 그 값을 따로 풉니다. 형식은 [시각 값 형식](../value-decoding/filetime-unix-webkit-dos-ole.md) 을 봅니다.

- 여러 출처의 시각을 시간순으로 합치는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

## 함정

- **원본 폴더를 LevelDB 라이브러리로 엽니다.** 여는 과정이 로그를 표 파일로 바꾸고 옛 파일을 정리합니다[1]. 그러면 지운 레코드와 옛 값이 사라질 수 있습니다. 이것은 라이브러리 동작에서 끌어낸 해석입니다. 늘 사본에서 작업합니다.
- **파일 번호를 16진수로 읽습니다.** 번호를 16진수로 설명한 자료도 있지만[10], 소스는 `%06llu`, 곧 10진수입니다[4]. 소스를 따릅니다.
- **`.sst` 를 다른 형식으로 봅니다.** `.sst` 도 `.ldb` 와 같은 표 파일입니다.
- **`LOG` 와 `.log` 를 헷갈립니다.** `LOG`·`LOG.old` 는 정보 메시지를 적은 텍스트입니다. 데이터는 번호가 붙은 `.log` 에 있습니다.
- **두 가지 "압축" 을 헷갈립니다.** 블록 압축(Snappy)은 `.ldb` 블록의 크기를 줄입니다. 압축 정리(Compaction)는 레벨끼리 파일을 합치면서 옛 값을 버립니다.
- **MANIFEST 번호로 DB 를 연 횟수를 셉니다.** 설계 문서로는 DB 를 다시 열 때마다 새 번호의 MANIFEST 를 만듭니다[1]. 그런데 크롬 `Local Storage\leveldb\` 에서 `MANIFEST-000001` 을 8월 4일에 만들고 9월 23일에 고친 예가 있습니다. 그 사이 9월 21일자 `LOG.old` 가 있어 DB 를 다시 연 적이 있는데도 번호는 1 그대로였습니다. LevelDB 에는 열 때 기존 MANIFEST 와 로그 파일에 이어 쓰는 `reuse_logs` 옵션이 있습니다[9]. 크롬이 이 옵션을 쓰는지는 공개 자료에 나와 있지 않습니다.
- **`.ldb` 가 없으면 데이터도 없다고 봅니다.** 데이터가 `.log` 에만 있을 수 있습니다.
- **같은 키의 첫 결과를 최신 값으로 봅니다.** 같은 키가 로그와 여러 레벨의 표 파일에 여러 번 나올 수 있습니다. 순서 번호를 비교합니다.
- **도구가 보여 주는 값만 봅니다.** 유효한 값만 보여 주는 도구도 있을 수 있습니다. 삭제 표시와 옛 값을 따로 보여 주는지 확인합니다.

## 도구

아래는 예로만 듭니다. 한 도구의 결과에만 기대지 않습니다.

| 도구 | 쓰임 |
|---|---|
| 헥스 편집기와 짧은 스크립트 | 위 표대로 로그 블록·레코드와 표 파일 꼬리를 나눕니다 |
| LevelDB 라이브러리 (google/leveldb) | 사본에서만 엽니다. 열 때 복구 과정이 돕니다 |
| Snappy 해제 라이브러리 | `.ldb` 데이터 블록을 풉니다 |

흔히 쓰는 공개 도구로 ccl_chrome_indexeddb, plyvel 등이 있습니다.
어느 도구든 사본에서 돌리고, 결과에 삭제 표시와 옛 값이 나오는지 먼저 확인합니다.
두 도구의 결과가 다르면 로그 파일을 넣었는지, 삭제 표시를 어떻게 다뤘는지부터 비교합니다. 검증 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 에 있습니다.

## 참고 문헌

- google/leveldb, *Files / Implementation* (`doc/impl.md`) — https://raw.githubusercontent.com/google/leveldb/main/doc/impl.md
- google/leveldb, *log format* (`doc/log_format.md`) — https://raw.githubusercontent.com/google/leveldb/main/doc/log_format.md
- google/leveldb, *File format* (`doc/table_format.md`) — https://raw.githubusercontent.com/google/leveldb/main/doc/table_format.md
- google/leveldb 소스 `db/filename.cc` — https://raw.githubusercontent.com/google/leveldb/main/db/filename.cc
- google/leveldb 소스 `db/write_batch.cc` — https://raw.githubusercontent.com/google/leveldb/main/db/write_batch.cc
- google/leveldb 소스 `db/dbformat.h` — https://raw.githubusercontent.com/google/leveldb/main/db/dbformat.h
- google/leveldb 소스 `util/coding.h` — https://raw.githubusercontent.com/google/leveldb/main/util/coding.h
- google/leveldb 소스 `table/format.h` — https://raw.githubusercontent.com/google/leveldb/main/table/format.h
- google/leveldb 소스 `include/leveldb/options.h` — https://raw.githubusercontent.com/google/leveldb/main/include/leveldb/options.h
- Alex Caithness, "Hang on! That's not SQLite! Chrome, Electron and LevelDB", CCL Solutions Group, 2020-09-23 — https://www.cclsolutionsgroup.com/post/hang-on-thats-not-sqlite-chrome-electron-and-leveldb
