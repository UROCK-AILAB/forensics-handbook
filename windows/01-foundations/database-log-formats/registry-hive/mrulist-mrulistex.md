# MRU 목록 읽는 법 (MRUList·MRUListEx)

> 위치: [레지스트리 하이브 구조](index.md) > MRU 목록 읽는 법

## 한 줄 요약

MRU 목록 (Most Recently Used list) 은 최근에 쓴 항목 여러 개를 레지스트리 키 하나에 모아 두는 저장 방식입니다. 항목의 순서는 항목과 따로, MRUList 또는 MRUListEx 라는 값 하나에 적습니다. MRUList 는 글자로 순서를 적고, MRUListEx 는 4바이트 숫자로 순서를 적습니다.

## 이 형식을 쓰는 아티팩트

MRU 목록은 대부분 사용자 하이브 NTUSER.DAT 와 UsrClass.dat 에 있습니다. 하이브 파일의 위치는 [하이브 파일 종류와 위치](system-software-sam-security-ntuser-dat-usrclass.md) 에 있습니다.

아래 표의 키는 NTUSER.DAT 의 `Software\Microsoft\Windows\CurrentVersion\Explorer\` 아래 경로입니다. 셸백만 경로를 따로 적었습니다.

| 아티팩트 | 키 | 순서 값 | 항목 데이터 | 해석 페이지 |
|---|---|---|---|---|
| 실행 창 명령 | `RunMRU` | MRUList | 문자열 | [실행 창 명령 기록 (RunMRU)](../../../02-artifacts/execution/runmru.md) |
| 최근 문서 | `RecentDocs`, `RecentDocs\<확장자>` | MRUListEx (Vista 이후) | 문자열 + 셸 아이템 | [최근 문서 (RecentDocs)](../../../02-artifacts/file-folder-usage/recentdocs.md) |
| 열기·저장 대화상자 | `ComDlg32\OpenSavePidlMRU\<확장자>` | MRUListEx | 셸 아이템 목록 | [열기·저장 대화상자 기록](../../../02-artifacts/file-folder-usage/comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) |
| 대화상자가 마지막으로 연 폴더 | `ComDlg32\LastVisitedPidlMRU` | MRUListEx | 문자열 + 셸 아이템 목록 | [열기·저장 대화상자 기록](../../../02-artifacts/file-folder-usage/comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) |
| 대화상자 창 크기 | `ComDlg32\CIDSizeMRU` | MRUListEx | UTF-16 문자열로 시작하는 이진 값 | [열기·저장 대화상자 기록](../../../02-artifacts/file-folder-usage/comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) |
| 연결 프로그램 목록 | `FileExts\<확장자>\OpenWithList` | MRUList | 문자열 | — |
| 셸백 | NTUSER.DAT `Software\Microsoft\Windows\Shell\BagMRU`, UsrClass.dat `Local Settings\Software\Microsoft\Windows\Shell\BagMRU` | MRUListEx | 셸 아이템 한 개 | [셸백 저장 위치와 구조](../../../02-artifacts/file-folder-usage/shellbags/ntuser-usrclass-bagmru-bags.md) |

- 셸백의 BagMRU 에는 값마다 같은 번호의 하위 키가 있고, 하위 키마다 MRUListEx 가 또 있어서 폴더 트리를 이룹니다.
- 항목 데이터에 든 셸 아이템은 [셸 아이템 (Shell Item·PIDL)](../../shell-document-formats/shell-item-pidl.md) 에서 풉니다.

### Windows 버전별 차이

같은 기능이라도 Windows Vista 를 경계로 키 이름과 순서 값이 바뀐 경우가 있습니다. 아래 표는 winreg-kb 의 정리를 따릅니다.

| 기능 | Windows 2000·XP | Windows Vista 이후 |
|---|---|---|
| 최근 문서 | `RecentDocs`: MRUList, 문자열 | `RecentDocs`: MRUListEx, 문자열 + 셸 아이템 |
| 열기·저장 대화상자 | `OpenSaveMRU`: MRUList, 문자열 | `OpenSavePidlMRU`: MRUListEx, 셸 아이템 목록 |
| 마지막으로 연 폴더 | `LastVisitedMRU`: MRUList, 문자열 | `LastVisitedPidlMRU`: MRUListEx, 문자열 + 셸 아이템 목록 |
| 실행 창 명령 | `RunMRU`: MRUList, 문자열 | `RunMRU`: MRUList, 문자열 (winreg-kb 는 Vista 까지 적었습니다) |

- winreg-kb 는 `OpenSavePidlMRU` 와 `LastVisitedPidlMRU` 를 Vista·7 기준으로 적었습니다.
- Windows 11 에서도 `OpenSavePidlMRU`·`LastVisitedPidlMRU`·`CIDSizeMRU`·`BagMRU` 는 MRUListEx 를 썼습니다. 순서 값과 항목 값은 모두 REG_BINARY 였습니다. (확인 범위: Windows 11 25H2)

## 구조

### MRUList

| 항목 | 내용 |
|---|---|
| 값 이름 | `MRUList` |
| 값 형식 | REG_SZ |
| 데이터 | UTF-16LE 글자의 배열입니다. 글자 하나가 항목 값 하나의 이름입니다. |
| 끝 표시 | 0x0000 |
| 순서 | 첫 글자가 가장 최근 항목입니다. |
| 항목 값 이름 | 소문자 한 글자 (`a`, `b`, `c` …) |
| 항목 값 형식 | 문자열 목록은 REG_SZ, 이진 목록은 REG_BINARY |

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 2 | 가장 최근 항목의 값 이름 (UTF-16LE 글자 한 개) |
| 2 | 2 | 두 번째로 최근인 항목의 값 이름 |
| … | 2 | … |
| 2 × n | 2 | 끝 표시 0x0000 |

- 목록에 담는 최대 개수는 목록을 만드는 프로그램이 정합니다. Microsoft 문서의 `MRUINFO` 구조체에서 `uMax` 가 이 값입니다.
- MRUList 는 항목 이름에 글자 하나를 쓰므로, 쓸 수 있는 이름 수만큼만 항목을 담을 수 있습니다.

### MRUListEx

| 항목 | 내용 |
|---|---|
| 값 이름 | `MRUListEx` |
| 값 형식 | REG_BINARY (winreg-kb 의 BagMRU 설명. Windows 11 25H2 의 다른 키에서도 확인) |
| 데이터 | 4바이트 리틀 엔디언 정수의 배열입니다. 정수 하나가 항목 값 하나의 이름입니다. |
| 끝 표시 | 0xFFFFFFFF (-1) |
| 순서 | 첫 정수가 가장 최근 항목입니다. |
| 항목 값 이름 | 10진 숫자 문자열 (`0`, `1`, `2` …) |

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 가장 최근 항목의 값 이름 숫자 |
| 4 | 4 | 두 번째로 최근인 항목의 값 이름 숫자 |
| … | 4 | … |
| 4 × n | 4 | 끝 표시 0xFFFFFFFF |

- 정수를 10진 문자열로 바꾸면 항목 값 이름이 됩니다. 정수 2 는 값 `2` 를 가리킵니다.
- 끝 표시가 제자리에 있으면 항목 수는 (데이터 바이트 수 ÷ 4) − 1 입니다.

### 항목 데이터 형식

항목 값에 무엇이 들었는지는 키마다 다릅니다. winreg-kb 는 네 가지로 나눴습니다.

| 형식 | 내용 | 쓰는 키 예 |
|---|---|---|
| 문자열 | UTF-16LE 문자열입니다. 끝 문자가 붙습니다. | `RunMRU` |
| 셸 아이템 목록 | 셸 아이템 목록 (Shell Item List) 입니다. | `OpenSavePidlMRU` |
| 문자열 + 셸 아이템 | UTF-16LE 파일 이름 뒤에 셸 아이템 한 개가 이어집니다. 셸 아이템은 비어 있을 수 있습니다. | `RecentDocs` (Vista 이후) |
| 문자열 + 셸 아이템 목록 | UTF-16LE 문자열 뒤에 셸 아이템 목록이 이어집니다. 첫 셸 아이템은 비어 있을 수 있습니다. | `LastVisitedPidlMRU` |

- 문자열과 셸 아이템 사이에 길이 칸은 없습니다. 문자열의 끝 문자 (0x0000) 를 찾아야 셸 아이템이 어디서 시작하는지 압니다.

> 그림 자리: MRUListEx 키 하나를 그린 그림. 왼쪽에 MRUListEx 값의 4바이트 칸들(2, 0, 1, FFFFFFFF)을 두고, 칸마다 화살표로 값 `2`·`0`·`1` 을 가리킨다. 값 `2` 에는 "가장 최근" 표시와 키 마지막 기록 시각을 붙이고, 나머지 값에는 시각이 없음을 표시한다.

## 읽는 법

1. 키 안에서 `MRUList` 또는 `MRUListEx` 값을 찾습니다. 둘 다 없으면 이 방식의 목록이 아닙니다.
2. 순서 값을 앞에서부터 끝 표시까지 풉니다. MRUList 는 2바이트씩, MRUListEx 는 4바이트씩 읽습니다.
3. 풀어 낸 이름 순서대로 같은 이름의 항목 값을 읽습니다. 첫 번째가 가장 최근입니다.
4. 항목 데이터를 키에 맞는 형식으로 풉니다. 셸 아이템이 있으면 셸 아이템 페이지의 방법으로 풉니다.
5. 순서 값에 없는 항목 값과, 순서 값에는 있는데 실제로 없는 항목 값을 따로 적어 둡니다.
6. 키의 마지막 기록 시각을 적습니다. 이 시각은 첫 번째 항목에만 조건을 달아 연결합니다. 조건은 아래 "시각" 절에 있습니다.
7. BagMRU 처럼 하위 키가 있으면 항목과 같은 번호의 하위 키로 내려가서 1번부터 다시 합니다.

### 헥스로 한 번 따라가기

아래 바이트는 명세로 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

MRUList 값의 데이터입니다.

```
63 00 61 00 62 00 00 00
```

- `63 00` 은 글자 `c`, `61 00` 은 `a`, `62 00` 은 `b` 입니다.
- `00 00` 은 끝 표시이고, 순서는 `c` → `a` → `b` 입니다. 값 `c` 가 가장 최근 항목이고, 값 `b` 가 가장 오래된 항목입니다.

MRUListEx 값의 데이터입니다.

```
02 00 00 00 00 00 00 00 01 00 00 00 FF FF FF FF
```

- 16바이트를 4바이트씩 나누면 네 칸이고, 마지막 칸 `FF FF FF FF` 는 끝 표시라서 항목은 세 개입니다.
- 순서는 `2` → `0` → `1` 이고, 값 `2` 가 가장 최근 항목입니다.

### 목록이 바뀌는 방식

MRUList 는 comctl32.dll 의 MRU 함수가 쓰는 저장 형식입니다. Microsoft 는 이 목록을 정의하는 구조체 (MRUINFO) 를 문서에 올렸지만, 그 구조체는 헤더 파일에 없다고 적었고 목록을 고치는 순서도 자세히 적지 않았습니다. 아래 동작은 Wine 이 같은 저장 형식으로 다시 구현한 코드를 따른 것입니다. Zhu 외 (2009) 의 논문도 MRUList·MRUListEx 키가 같은 규칙으로 바뀐다고 정리했습니다.

- 목록에 이미 있는 항목을 다시 쓰면 순서 값만 바뀝니다. 그 항목의 이름이 맨 앞으로 옵니다. 항목 값은 다시 쓰지 않습니다.
- 새 항목이 들어오고 자리가 남아 있으면 새 이름으로 값을 만듭니다. 그 이름이 순서 맨 앞에 옵니다.
- 새 항목이 들어오고 목록이 가득 찼으면 가장 오래된 항목의 이름을 다시 씁니다. 그 값의 데이터를 새 항목으로 덮어쓰고, 그 이름을 순서 맨 앞으로 옮깁니다.

아래 표는 최대 개수가 3 이고 순서가 `cab` 인 목록의 예입니다.

| 동작 | 순서 값 (전 → 후) | 항목 값 |
|---|---|---|
| 이미 있는 `a` 를 다시 씀 | `cab` → `acb` | 바뀌지 않음 |
| 새 항목이 들어옴 (가득 참) | `cab` → `bca` | 가장 오래된 `b` 의 데이터를 새 항목으로 덮어씀 |
| 새 항목이 들어옴 (최대 개수가 4 라서 자리가 남음) | `cab` → `dcab` | 값 `d` 가 새로 생김 |

- 목록을 만들 때 `MRU_CACHEWRITE` 표시를 켜면, 바뀐 순서를 레지스트리에 바로 쓰지 않습니다. 새 항목이 들어오거나 목록을 닫을 때 씁니다. 그동안 메모리의 순서와 레지스트리의 순서가 다를 수 있습니다.
- MRUListEx 를 쓰는 셸 구현은 공개 문서를 찾지 못했습니다.
- Windows 11 에서는 가장 큰 번호가 순서 맨 앞에 있지 않은 목록이 여럿 있었습니다. 번호가 클수록 최근 항목이라고 읽으면 틀립니다. (확인 범위: Windows 11 25H2, `OpenSavePidlMRU`·`LastVisitedPidlMRU`·`CIDSizeMRU`)

## 포렌식에서 중요한 점

### 시각

레지스트리 키에는 시각이 키의 마지막 기록 시각 (Last Write Time) 하나뿐이고, FILETIME 형식의 UTC 값입니다. 자세한 내용은 [키 마지막 기록 시각 (Last Write Time)](last-write-time.md) 에 있습니다.

항목을 추가하거나 다시 쓰면 순서 값을 다시 기록하는데 (Wine 구현 기준), 값을 기록하면 키의 마지막 기록 시각이 바뀝니다. 그래서 이 시각은 보통 첫 번째 항목이 마지막으로 쓰인 때에 가깝습니다. 키 안의 다른 값이나 하위 키를 지워도 이 시각이 바뀌는데, Windows 10 의 RecentDocs 에서 이런 경우가 보고됐고 이때 키 시각은 첫 번째 항목의 사용 시각보다 늦습니다.

두 번째 이후 항목에는 시각이 없어서, 순서로 알 수 있는 것은 "바로 앞 항목보다 먼저 마지막으로 쓰였다" 는 것뿐입니다. 바로 앞 항목의 시각을 다른 곳에서 알면 그 시각이 뒤 항목의 상한이 되고, RecentDocs 에서는 확장자 하위 키의 시각을 루트 키의 순서와 맞춰 보면서 이 방법으로 범위를 좁힙니다.

### 옛 상태와 비교하기

섀도 복사본이나 옛 백업에 같은 하이브가 있으면 두 시점의 목록을 비교할 수 있고, 두 시점 사이에 바뀐 항목은 그 사이에 쓰인 것입니다. Zhu 외 (2009) 는 이 비교 규칙을 두 가지로 정리했습니다.
  1. 예전 목록에서 어떤 항목보다 최근이던 항목이 새 목록에서 그 항목보다 오래된 쪽에 있으면, 그 항목은 두 시점 사이에 다시 쓰인 것입니다. 예전 목록에 없던 항목도 그 사이에 쓰인 것입니다.
  2. 그렇게 찾은 항목보다 더 최근 쪽에 있는 항목도 모두 그 사이에 쓰인 것입니다.
예를 들어 순서가 `cab` 에서 `acb` 로 바뀌었다면 두 시점 사이에 `a` 를 다시 쓴 것입니다. 이 규칙으로는 "확실히 바뀐 항목" 만 가릴 수 있고, 이미 맨 앞에 있던 항목을 다시 쓰면 순서가 그대로라서 알 수 없습니다.

섀도 복사본을 다루는 법은 [섀도 복사본 활용 (Volume Shadow Copy Analysis)](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에 있습니다.

### 지운 항목과 덮어쓴 항목

사용자가 목록을 지우면 항목 값이나 키 전체가 사라집니다. 지운 값과 키, 그리고 가득 찬 목록에서 덮어쓴 옛 데이터는 하이브의 빈 셀에 남아 있을 수 있습니다. 찾는 방법은 [지워진 키·값 복구 (Deleted Keys·Values)](deleted-keys-values.md) 에 있습니다. 빈 셀에서 찾은 항목 값에는 순서 정보가 없어서 그 값이 목록의 몇 번째였는지는 알 수 없습니다.

### 비정상 종료

마지막 변경이 하이브 본 파일에 반영되지 않고 트랜잭션 로그에만 있을 수 있으므로, 로그를 반영하지 않고 읽으면 최근 변경이 빠진 옛 목록이 보입니다. 순서 값이 없는 이름을 가리키거나 순서 값에 없는 항목 값이 있으면 먼저 로그 반영 여부를 확인합니다. 로그 반영은 [트랜잭션 로그와 반영 안 된 변경 (.LOG1·.LOG2)](log1-log2.md) 에 있습니다.

## 함정

- 값 이름의 글자·숫자 순서는 시간 순서가 아닙니다. 가득 찬 목록은 가장 오래된 이름을 다시 씁니다. 그래서 `a` 나 `0` 이 가장 최근 항목일 수 있습니다.
- 키의 마지막 기록 시각을 목록의 모든 항목에 붙이면 안 됩니다. 이 시각은 첫 번째 항목에만 조건부로 연결됩니다.
- 같은 항목을 여러 번 써도 항목은 하나만 남습니다. 목록으로는 몇 번 썼는지 알 수 없습니다.
- 목록에는 최대 개수가 있습니다. 오래된 항목은 밀려서 사라집니다. 목록에 없다고 해서 쓰지 않았다는 뜻은 아닙니다.
- 목록에 올랐다고 사용자가 직접 열었다는 뜻은 아닙니다. Windows 10 의 RecentDocs 는 파일을 만들기만 해도 항목이 생기고, 상위 폴더 항목도 함께 생긴다고 보고됐습니다. 키마다 무엇이 항목을 만드는지는 각 아티팩트 페이지에서 확인합니다.
- 최근 목록인데 이 방식이 아닌 키가 있습니다. [TypedURLs](../../../02-artifacts/browsers/ie-edgehtml/typedurls-typedurlstime.md) 는 순서 값 없이 `url1`, `url2` … 이름을 씁니다. 새 주소가 들어오면 기존 값의 이름을 하나씩 뒤로 밀어서 다시 씁니다. 이런 키는 값 이름의 번호가 곧 순서입니다.
- 이런 키는 새 항목 하나만 들어와도 모든 값을 다시 쓰므로, 두 시점을 비교할 때 바뀐 값이 모두 사용자가 쓴 항목은 아닙니다.
- 탐색기 주소창 기록인 TypedPaths 에도 순서 값이 없었습니다. (확인 범위: Windows 11 25H2) 해석은 [탐색기 입력 기록 (TypedPaths·WordWheelQuery)](../../../02-artifacts/file-folder-usage/typedpaths-wordwheelquery.md) 에 있습니다.
- 끝 표시에서 읽기를 멈춰야 합니다. 끝 표시 뒤에 바이트가 더 있거나 끝 표시가 없으면 도구마다 결과가 다를 수 있습니다. 이런 경우에는 원시 바이트를 직접 확인합니다.

## 도구

- RegRipper 는 RunMRU·RecentDocs·ComDlg32 같은 키마다 플러그인이 있습니다. 플러그인은 순서 값을 풀어서 순서대로 보여 줍니다.
- Registry Explorer 에는 MRU 키를 순서대로 풀어 보여 주는 플러그인이 있습니다.
- regipy·python-registry 같은 파이썬 라이브러리로 값을 꺼내면 순서 값을 직접 풀 수 있습니다. 위 "헥스로 한 번 따라가기" 의 방법 그대로입니다.
- 도구가 순서 값에 없는 항목 값을 보여 주는지, 끝 표시 뒤를 어떻게 다루는지는 도구마다 다릅니다. 두 가지 이상 도구로 결과를 맞춰 봅니다. 방법은 [도구 결과 교차 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md) 에 있습니다.

## 참고 문헌

1. libyal, "Most recently used (MRU)", Windows Registry Knowledge Base (winreg-kb). https://winreg-kb.readthedocs.io/en/latest/sources/explorer-keys/Most-recently-used.html
2. Microsoft Learn, "MRUINFO structure". https://learn.microsoft.com/en-us/windows/win32/shell/mruinfo
3. Yuandong Zhu, Pavel Gladyshev, Joshua James, "Temporal Analysis of Windows MRU Registry Keys", Advances in Digital Forensics V (IFIP), 2009. https://opendl.ifip-tc6.org/db/conf/ifip11-9/df2009/ZhuGJ09.pdf
4. Wine 프로젝트, comctl32 의 MRU 함수 구현 (`CreateMRUListW`·`AddMRUData` 등). https://github.com/wine-mirror/wine/tree/master/dlls/comctl32
5. Lee Whitfield, "Updates to the RecentDocs Key in Windows 10", Forensic 4:cast, 2019. https://forensic4cast.com/2019/03/the-recentdocs-key-in-windows-10/
6. 4n6k, "Forensics Quickie: Pinpointing Recent File Activity - RecentDocs", 2014. https://www.4n6k.com/2014/02/forensics-quickie-pinpointing-recent.html
