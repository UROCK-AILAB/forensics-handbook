# 저장 위치와 구조 (NTUSER·UsrClass·BagMRU·Bags)

## 한 줄 요약

셸백 (ShellBags) 은 사용자 하이브 두 개에 BagMRU 와 Bags 라는 두 갈래 키로 남습니다. BagMRU 는 폴더 경로를 키 트리로 적습니다. Bags 는 그 폴더를 어떤 보기 설정으로 열었는지 적습니다. 두 갈래는 NodeSlot 이라는 번호 하나로 이어집니다.

## 무엇을 기록하나 · 왜 생기나

- 탐색기는 폴더마다 창 크기·위치·보기 방식을 기억합니다. 같은 폴더를 다시 열 때 그 설정을 되살리려는 것입니다. (Lo, 2014)
- 설정을 폴더와 짝지으려면 그 폴더가 무엇인지도 적어야 합니다. 그래서 BagMRU 에 폴더를 가리키는 셸 아이템 (Shell Item) 이 남습니다.
- 보기 설정 자체는 Bags 에 남습니다.
- 조사에서 주로 쓰는 쪽은 BagMRU 입니다. 폴더 경로가 여기서 나옵니다.
- Lo 의 실험에서 Vista~8.1 은 폴더를 두 번 클릭해 열지 않아도 셸백을 만들었습니다. 폴더를 고르기만 하거나, 오른쪽 클릭하거나, 이름을 바꾸거나, 복사해도 셸백이 생겼습니다.
- 어떤 동작이 셸백을 만드는지는 [셸백 해석 함정](/02-artifacts/file-folder-usage/shellbags/pitfalls.md) 에서 다룹니다. 이 페이지는 키가 어디에 어떤 모양으로 남는지만 다룹니다.

## 위치와 버전별 차이

### 하이브 파일

| 하이브 | 파일 위치 (Vista 이후) | 실행 중인 시스템에서 보이는 곳 |
|---|---|---|
| NTUSER.DAT | `%UserProfile%\NTUSER.DAT` | `HKCU` |
| UsrClass.dat | `%UserProfile%\AppData\Local\Microsoft\Windows\UsrClass.dat` | `HKCU\Software\Classes` |

- 하이브 파일의 쓰임새와 옛 버전 위치는 [하이브 파일 종류와 위치](/01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md) 에 있습니다.
- UsrClass.dat 옆에도 `UsrClass.dat.LOG1`·`UsrClass.dat.LOG2` 가 있습니다. (확인 범위: Windows 11 25H2)
- 하이브 파일만 뽑지 말고 같은 폴더의 로그 파일도 함께 수집합니다. 까닭은 [트랜잭션 로그와 반영 안 된 변경](/01-foundations/database-log-formats/registry-hive/log1-log2.md) 에 있습니다.

### 키 경로

아래 경로는 하이브 파일을 따로 열었을 때 맨 위 키부터 적은 것입니다. 실행 중인 시스템에서는 UsrClass.dat 경로 앞에 `HKCU\Software\Classes\` 가 붙습니다.

| Windows | NTUSER.DAT 안 | UsrClass.dat 안 | 근거 |
|---|---|---|---|
| XP | `Software\Microsoft\Windows\Shell\BagMRU`·`Bags`<br>`Software\Microsoft\Windows\ShellNoRoam\BagMRU`·`Bags` | 셸백 없음 | winreg-kb, Lo |
| Vista (32비트) | `Software\Microsoft\Windows\Shell\BagMRU`·`Bags` | `Local Settings\Software\Microsoft\Windows\Shell\BagMRU`·`Bags` | Lo |
| Vista (64비트) | 위와 같음 | 위 경로에 더해 `Wow6432Node\Local Settings\Software\Microsoft\Windows\Shell\BagMRU`·`Bags` | Lo |
| 7·8·8.1 | `Software\Microsoft\Windows\Shell\BagMRU`·`Bags` | `Local Settings\Software\Microsoft\Windows\Shell\BagMRU`·`Bags` | Lo |
| 10 | 이 글에서 직접 확인하지 않았습니다 | 이 글에서 직접 확인하지 않았습니다 | — |
| 11 (25H2) | `Software\Microsoft\Windows\Shell\BagMRU`·`Bags` | `Local Settings\Software\Microsoft\Windows\Shell\BagMRU`·`Bags` | 관찰 |

- Vista 의 NTUSER.DAT 에도 `ShellNoRoam` 키가 있었습니다. 그 안에는 `BagMRU Size` 라는 DWORD 값 하나만 있었습니다. (Lo)
- Lo 의 실험에서 Windows 7 부터는 `ShellNoRoam` 을 쓰지 않았습니다.
- winreg-kb 는 UsrClass.dat 쪽에도 `ShellNoRoam\BagMRU` 경로와 `Wow6432Node` 아래 `ShellNoRoam\BagMRU` 경로를 적었습니다. Lo 는 이 키들을 실험에서 찾지 못했습니다. 검체에 이런 키가 있으면 같은 방법으로 읽습니다.
- Windows 11 25H2 PC 한 대에서는 `ShellNoRoam` 키와 `Wow6432Node` 쪽 셸백 키가 둘 다 없었습니다. (확인 범위: Windows 11 25H2)
- Windows 10 은 이 글에서 직접 확인하지 않았습니다. 두 하이브에서 위 경로를 모두 찾아봅니다.

### 하이브마다 담는 폴더

Lo 는 어떤 폴더가 어느 하이브에 남는지 실험으로 나눴습니다. XP 는 하이브가 하나라서 `Shell` 과 `ShellNoRoam` 으로 나뉩니다.

| Windows | NTUSER.DAT `Shell` 에 남은 것 | 다른 쪽에 남은 것 |
|---|---|---|
| XP | 바탕 화면, 윈도 네트워크 폴더, 원격 컴퓨터, 원격 폴더 | NTUSER.DAT `ShellNoRoam`: 바탕 화면, ZIP 파일, 원격 폴더, 로컬 폴더, 특수 폴더, 가상 폴더 |
| Vista·7·8·8.1 | 바탕 화면, 윈도 네트워크 폴더, 원격 컴퓨터, 원격 폴더 | UsrClass.dat: 바탕 화면, ZIP 파일, 원격 폴더, 로컬 폴더, 특수 폴더, 가상 폴더 |

- Vista 이후 로컬 폴더 흔적은 UsrClass.dat 에 남습니다. NTUSER.DAT 만 보면 로컬 폴더를 대부분 놓칩니다.
- 네트워크 쪽 흔적은 NTUSER.DAT 에 남을 수 있습니다. UsrClass.dat 만 보아도 빠지는 것이 생깁니다.
- Windows 11 25H2 PC 한 대에서는 NTUSER.DAT 쪽 BagMRU 에 폴더 항목이 하나도 없었습니다. `NodeSlot` 값 하나와 `Bags\1\Desktop` 키만 있었습니다. 이 PC 에서 네트워크 폴더를 연 적이 있는지는 확인하지 않았습니다. (확인 범위: Windows 11 25H2)

## 구조

> 그림 자리: 왼쪽에 BagMRU 트리(루트 = 바탕 화면, 숫자 하위 키 하나가 폴더 하나), 오른쪽에 `Bags\<번호>` 슬롯. 부모 키의 숫자 값에서 같은 번호 하위 키로 가는 화살표, 각 키의 NodeSlot 에서 `Bags\<번호>` 로 가는 화살표를 함께 그린다.

### BagMRU — 폴더 경로 트리

- BagMRU 키 자체는 바탕 화면 (Desktop) 을 뜻합니다. (Lo)
- BagMRU 아래 숫자 이름 하위 키 하나가 폴더 하나입니다.
- 폴더 이름은 그 폴더의 키 안에 없습니다. 부모 키에서 하위 키와 번호가 같은 값에 들어 있습니다. (Lo)
- 그래서 `BagMRU\0\1\3` 의 경로는 값 세 개를 이어 만듭니다. BagMRU 의 값 `0`, `BagMRU\0` 의 값 `1`, `BagMRU\0\1` 의 값 `3` 입니다.
- 내 문서·제어판·내 PC 같은 최상위 특수 폴더와 가상 폴더는 BagMRU 바로 아래에 생깁니다. (Lo)
- 경로는 셸 네임스페이스 (Shell Namespace) 기준입니다. 드라이브 문자, 네트워크 경로, ZIP 파일 안 경로, 제어판 같은 가상 폴더가 한 트리에 섞입니다.

BagMRU 키 안의 값은 다음과 같습니다.

| 값 이름 | 형식 | 있는 곳 | 내용 | 근거 |
|---|---|---|---|---|
| `0`, `1`, `2` … (10진 숫자) | REG_BINARY | 하위 폴더가 있는 BagMRU 키 | 같은 번호 하위 키가 가리키는 폴더의 셸 아이템 | winreg-kb |
| `MRUListEx` | REG_BINARY | 대부분의 BagMRU 키 (Lo 는 모든 키에 있다고 적었습니다) | 하위 폴더를 최근에 고른 순서. 4바이트 번호 배열이고 0xFFFFFFFF 로 끝납니다 | winreg-kb |
| `NodeSlot` | REG_DWORD | 대부분의 BagMRU 키 | 이 폴더의 보기 설정이 든 `Bags` 하위 키 번호 | winreg-kb, Lo |
| `NodeSlots` | REG_BINARY (관찰) | BagMRU 맨 위 키에만 | 공개 명세에 뜻이 적혀 있지 않습니다 | winreg-kb |

- 숫자 값의 형식은 [셸 아이템 (Shell Item·PIDL)](/01-foundations/shell-document-formats/shell-item-pidl.md) 에서 풉니다.
- Windows 11 25H2 PC 한 대에서는 모든 숫자 값이 같은 모양이었습니다. 셸 아이템 하나 뒤에 목록 끝 표시 0x0000 두 바이트가 붙었습니다. 즉 항목이 하나뿐인 셸 아이템 목록입니다. (확인 범위: Windows 11 25H2)
- `MRUListEx` 읽는 법은 [MRU 목록 읽는 법](/01-foundations/database-log-formats/registry-hive/mrulist-mrulistex.md) 에 있습니다.
- Lo 는 하위 키 번호를 셸백이 만들어진 차례로 설명합니다. `BagMRU\0` 이 처음 만든 폴더이고 `BagMRU\1` 이 두 번째입니다. 최근에 고른 순서는 번호가 아니라 `MRUListEx` 로 봅니다.
- `MRUListEx` 는 같은 부모 아래 형제 폴더끼리의 순서만 알려 줍니다. 다른 부모 아래 폴더와의 앞뒤는 알려 주지 않습니다.

Windows 11 25H2 PC 한 대에서 관찰한 점은 다음과 같습니다. (확인 범위: Windows 11 25H2)

- `NodeSlot` 이 없는 BagMRU 키가 있었습니다. 그런 키에는 모두 하위 키가 있었습니다. 보기 설정 없이 경로 중간 단계로만 남은 폴더로 추정합니다.
- `NodeSlot` 값은 모두 서로 달랐습니다. 값마다 같은 번호의 `Bags` 하위 키가 있었습니다.
- `NodeSlots` 값의 길이는 가장 큰 `Bags` 번호와 같았습니다. 바이트 하나가 슬롯 하나에 대응하는 것으로 보입니다. 바이트 값의 뜻은 확인하지 못했습니다.

### Bags — 보기 설정

- `Bags` 아래 숫자 키 하나가 슬롯 (Slot) 하나입니다.
- 슬롯 번호는 BagMRU 쪽 `NodeSlot` 값과 같습니다. 예를 들어 `NodeSlot` 이 1 이면 `Bags\1` 을 봅니다. (winreg-kb)
- `NodeSlot` 번호는 같은 하이브 안에서만 뜻이 있습니다. NTUSER.DAT 의 `Bags\1` 과 UsrClass.dat 의 `Bags\1` 은 서로 다른 슬롯입니다.

| 키 | 내용 | 근거 |
|---|---|---|
| `Bags\<번호>` | 슬롯 키. 보기 설정은 그 아래 하위 키에 있습니다 | Lo |
| `Bags\<번호>\Shell` | 탐색기 창에서 본 보기 설정 | Lo, winreg-kb |
| `Bags\<번호>\Shell\{폴더 유형 GUID}` | 그 폴더 유형으로 볼 때의 보기 설정 | Lo |
| `Bags\<번호>\ComDlg`, `ComDlg\{폴더 유형 GUID}` | 열기·저장 대화상자 (Common Dialog) 에서 본 보기 설정 | Lo (Vista~8.1) |
| `Bags\<번호>\ComDlgLegacy`, `ComDlgLegacy\{폴더 유형 GUID}` | 옛 모양 대화상자에서 본 보기 설정 | Lo |
| NTUSER.DAT `Bags\1\Desktop` | 바탕 화면의 보기 설정 | Lo |
| `Bags\AllFolders\Shell` | 창 위치 값 모음 | 관찰 (Windows 11 25H2) |

- Lo 의 실험에서 `ComDlg` 는 대화상자로 폴더를 열었다가 닫아야 생겼습니다. 대화상자 안에서 다른 폴더로 옮겨 가도 생겼습니다.
- 그래서 `ComDlg` 가 있는 슬롯은 그 폴더를 대화상자로 다룬 적이 있다는 단서가 됩니다. 대화상자 기록은 [열기·저장 대화상자 기록](/02-artifacts/file-folder-usage/comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) 과 맞춰 봅니다.
- Windows 11 25H2 PC 한 대에서 NTUSER.DAT `Bags\1\Desktop` 에는 `IconLayouts` 값이 있었습니다. 이름으로 보아 바탕 화면 아이콘 배치입니다. 형식은 확인하지 않았습니다. (확인 범위: Windows 11 25H2)

#### `Shell` 키의 값

| 값 | 형식 (관찰) | 내용 | 근거 |
|---|---|---|---|
| `SniffedFolderType` | REG_SZ | 탐색기가 폴더 내용을 보고 고른 폴더 유형 이름. 그림 파일이 있으면 Pictures, 문서가 있으면 Documents 가 됩니다 | Lo |
| `KnownFolderDerivedFolderType` | REG_SZ | Lo 는 이름만 적었습니다. 이름으로 보아 알려진 폴더 (Known Folder) 에서 정한 폴더 유형입니다 | Lo |

- 한 폴더에 폴더 유형 GUID 하위 키가 여럿일 수 있습니다. 지금 쓰는 설정이 어느 GUID 에 있는지는 `SniffedFolderType` 이 알려 줍니다. (Lo)
- Windows 11 25H2 PC 한 대의 `{폴더 유형 GUID}` 키에는 `Mode`·`LogicalViewMode`·`Vid`·`IconSize`·`Sort`·`GroupView`·`GroupByKey:FMTID`·`GroupByKey:PID`·`GroupByDirection`·`FFlags`·`Rev`·`ColInfo` 값이 있었습니다. 이름으로 보아 보기 방식·아이콘 크기·정렬·묶기·열 배치 값입니다. 각 값의 형식은 공개 명세에서 확인하지 못했습니다. (확인 범위: Windows 11 25H2)

#### 폴더 유형 GUID

GUID 와 이름의 짝은 SOFTWARE 하이브의 `Microsoft\Windows\CurrentVersion\Explorer\FolderTypes\{GUID}` 키에 있습니다. (Microsoft Learn) 이름은 그 키의 `CanonicalName` 값에 있었습니다. (확인 범위: Windows 11 25H2) 그래서 검체 자신의 SOFTWARE 하이브로 GUID 를 풀 수 있습니다.

| GUID | `CanonicalName` |
|---|---|
| `{5C4F28B5-F869-4E84-8E60-F11DB97C5CC7}` | Generic |
| `{7D49D726-3C21-4F05-99AA-FDC2C9474656}` | Documents |
| `{B3690E58-E961-423B-B687-386EBFD83239}` | Pictures |
| `{5FA96407-7E77-483C-AC93-691D05850DE8}` | Videos |
| `{885A186E-A440-4ADA-812B-DB871B942259}` | Downloads |
| `{80213E82-BCFD-4C4F-8817-BB27601267A9}` | CompressedFolder |
| `{7FDE1A1E-8B31-49A5-93B8-6BE14CFA4943}` | Generic.SearchResults |
| `{4F01EBC5-2385-41F2-A28E-2C5C91FB56E0}` | StorageProviderGeneric |

- 표의 짝은 Windows 11 25H2 PC 한 대의 SOFTWARE 하이브에서 읽었습니다. Generic·Pictures·Documents 세 GUID 는 Lo 의 설명과도 같습니다.
- Microsoft 는 StorageProvider 로 시작하는 폴더 유형을 Windows 8.1 에서 들어온 저장소 공급자 (Storage Provider) 폴더로 설명합니다.
- Microsoft 는 CompressedFolder 를 .zip 같은 압축 파일 폴더로 설명합니다. 압축 폴더 흔적은 [외부 장치·네트워크·압축 폴더 탐색 흔적](/02-artifacts/file-folder-usage/shellbags/removable-network-zip.md) 에서 다룹니다.
- GUID 를 바이트로 읽는 순서는 [윈도 식별자 형식](/01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에 있습니다.

#### `AllFolders\Shell` 의 창 위치 값

- winreg-kb 는 `Bags\<번호>\Shell` 에 `MinPos1100x705(1).x` 처럼 화면 크기가 이름에 들어간 값을 적었습니다.
- Windows 11 25H2 PC 한 대에서는 이런 값이 `Bags\AllFolders\Shell` 에 있었습니다. 값 이름은 `WinPos<가로>x<세로>x<숫자>(<번호>).left` 꼴이었습니다. 세 번째 숫자의 뜻은 확인하지 못했습니다. (확인 범위: Windows 11 25H2)
- 값 이름에 화면 크기가 여럿 보이면 그 크기의 화면에서 탐색기 창을 쓴 적이 있다고 추정할 수 있습니다. 어떤 모니터였는지는 다른 기록과 맞춰 봅니다.

### 경로를 되살리는 순서

1. NTUSER.DAT 와 UsrClass.dat 를 각각 `.LOG1`·`.LOG2` 까지 반영한 사본으로 엽니다.
2. BagMRU 맨 위 키에서 시작합니다. 이 키가 바탕 화면입니다.
3. `MRUListEx` 를 읽어 번호 순서를 적어 둡니다.
4. 숫자 값마다 셸 아이템을 풀어 이름을 얻습니다.
5. 같은 번호의 하위 키로 내려갑니다. 지금까지의 경로에 이름을 붙이고 3번부터 되풀이합니다.
6. 키마다 `NodeSlot` 을 읽고 `Bags\<NodeSlot>` 을 찾습니다. 폴더 유형과 `ComDlg` 유무를 경로 옆에 적습니다.
7. 키마다 마지막 기록 시각과 셸 아이템 속 시각을 따로 적습니다. 두 시각의 뜻은 [셸백 시각 해석](/02-artifacts/file-folder-usage/shellbags/timestamps.md) 에서 다룹니다.
8. 두 하이브의 결과를 합칩니다. 어느 하이브에서 나온 행인지 열로 남깁니다.

## 증거로서 의미

이 절은 키의 모양에서 나오는 것만 다룹니다. 시각에서 나오는 것은 [셸백 시각 해석](/02-artifacts/file-folder-usage/shellbags/timestamps.md) 에 있습니다.

### 증명하는 것

- BagMRU 에 경로가 있으면, 이 하이브를 쓰는 사용자 환경에서 셸이 그 폴더를 다룬 기록이 있습니다.
- 하이브는 사용자 프로필마다 따로 있습니다. 그래서 어느 프로필의 기록인지 나뉩니다. 프로필과 계정을 잇는 법은 [사용자 프로필 목록 (ProfileList)](/02-artifacts/system-account/profilelist.md) 에 있습니다.
- `Bags\<번호>\ComDlg` 가 있으면 그 폴더를 열기·저장 대화상자에서 다룬 기록이 있습니다.

### 증명하지 못하는 것

- 폴더 안의 파일을 열었다는 사실은 증명하지 못합니다. 셸백은 폴더 단위 기록입니다.
- 사용자가 폴더를 두 번 클릭해 열었다는 사실도 증명하지 못합니다. Vista~8.1 에서는 고르기·오른쪽 클릭·이름 바꾸기·복사로도 셸백이 생겼습니다. (Lo)
- 폴더가 지금도 있다는 뜻이 아닙니다. 폴더를 지워도 셸백은 지워지지 않습니다. (Lo) 이 점을 쓰는 법은 [지운 폴더 흔적 찾기](/02-artifacts/file-folder-usage/shellbags/deleted-folders.md) 에 있습니다.
- 폴더 유형이 실제 내용을 뜻하지는 않습니다. Microsoft 는 폴더 유형이 보기 틀일 뿐이라고 설명합니다. 폴더 내용과 맞는지 따로 검사하지 않는다고도 적습니다.
- 전체 탐색 순서는 알 수 없습니다. `MRUListEx` 는 형제 폴더끼리의 순서만 담습니다.

## 함정과 한계

- **NTUSER.DAT 만 보는 실수.** Vista 이후 로컬 폴더는 UsrClass.dat 에 남습니다. 두 하이브를 모두 읽었는지 도구 설정과 결과에서 확인합니다.
- **반영 안 된 로그.** 하이브 본문에 아직 쓰이지 않은 셸백 변경이 `.LOG1`·`.LOG2` 에 남아 있을 수 있습니다. 로그를 반영하기 전과 후를 비교합니다.
- **번호와 순서를 섞는 실수.** 하위 키 번호는 만든 차례입니다. 최근 순서가 아닙니다. 최근 순서는 `MRUListEx` 로 봅니다.
- **하이브를 건너 NodeSlot 을 잇는 실수.** NTUSER.DAT 의 `NodeSlot` 은 NTUSER.DAT 의 `Bags` 만 가리킵니다.
- **덜 알려진 경로를 빠뜨리는 실수.** Vista 64비트의 `Wow6432Node` 경로와 XP 의 `ShellNoRoam` 경로도 찾아봅니다.
- **같은 이름 폴더.** Lo 의 실험에서 폴더를 지우고 같은 이름으로 다시 만들면 새 폴더가 옛 셸백을 그대로 이어받았습니다. 셸백 경로 하나가 서로 다른 두 폴더를 가리킬 수 있습니다.
- **풀지 못하는 셸 아이템.** libfwsi 명세에도 뜻이 확인되지 않은 칸이 남아 있습니다. 도구마다 모르는 셸 아이템을 다르게 처리할 수 있습니다. 도구 두 개로 풀어 비교합니다. 방법은 [도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md) 에 있습니다.
- **지운 키.** 셸백 키를 지우는 도구가 있습니다. (Lo) 지운 키는 하이브의 빈 공간에 남을 수 있습니다. [지워진 키·값 복구](/01-foundations/database-log-formats/registry-hive/deleted-keys-values.md) 를 함께 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 명세(winreg-kb·libfwsi)로 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

UsrClass.dat 의 `Local Settings\Software\Microsoft\Windows\Shell\BagMRU` 키에 다음 값이 있다고 합시다.

```
값 "0" (REG_BINARY, 22바이트)
14 00 1F 50 E0 4F D0 20 EA 3A 69 10 A2 D8 08 00
2B 30 30 9D 00 00

값 "MRUListEx" (REG_BINARY)
00 00 00 00 FF FF FF FF

값 "NodeSlot" (REG_DWORD)
1
```

| 오프셋 | 바이트 | 뜻 |
|---|---|---|
| 0 | `14 00` | 셸 아이템 크기 0x14 = 20바이트 |
| 2 | `1F` | 종류 표시: 루트 폴더 셸 아이템 |
| 3 | `50` | 정렬 번호 0x50. libfwsi 는 My Computer 로 적습니다 |
| 4 | `E0 4F D0 20 … 30 30 9D` | GUID `{20D04FE0-3AEA-1069-A2D8-08002B30309D}` (내 PC) |
| 20 | `00 00` | 셸 아이템 목록 끝 |

- `MRUListEx` 에는 번호 0 하나만 있습니다. 하위 폴더가 하나뿐입니다.
- 그래서 `BagMRU\0` 은 "바탕 화면 > 내 PC" 입니다.
- 맨 위 키의 `NodeSlot` 1 은 바탕 화면의 보기 설정이 `Bags\1` 에 있다는 뜻입니다.

이제 `BagMRU\0` 키에 다음 값이 있다고 합시다.

```
값 "0" (REG_BINARY, 27바이트)
19 00 2F 43 3A 5C 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00

값 "MRUListEx" (REG_BINARY)
00 00 00 00 FF FF FF FF

값 "NodeSlot" (REG_DWORD)
2
```

| 오프셋 | 바이트 | 뜻 |
|---|---|---|
| 0 | `19 00` | 셸 아이템 크기 0x19 = 25바이트 |
| 2 | `2F` | 종류 표시. 0x70 으로 거르면 0x20 이라 볼륨 셸 아이템입니다. 0x01 비트는 이름이 있다는 뜻입니다 |
| 3 | `43 3A 5C 00` 뒤로 0 | 볼륨 이름 `C:\`. 20바이트 칸에 ASCII 로 들어 있습니다 |
| 23 | `00 00` | libfwsi 가 뜻을 확인하지 못한 칸 |
| 25 | `00 00` | 셸 아이템 목록 끝 |

- 따라서 `BagMRU\0\0` 은 "바탕 화면 > 내 PC > C:\" 입니다.
- 이 폴더의 보기 설정은 `NodeSlot` 2 가 가리키는 `Bags\2` 에 있습니다.
- `BagMRU\0\0` 아래 하위 키가 있으면 그 값은 `C:\` 아래 폴더입니다. 그 값은 파일 항목 셸 아이템 (종류 0x31 등) 입니다. 그 안의 이름과 시각은 [셸 아이템 (Shell Item·PIDL)](/01-foundations/shell-document-formats/shell-item-pidl.md) 에서 풉니다.

### 공개 도구로 한 번

- 셸백 전용 공개 도구로는 Eric Zimmerman 의 ShellBags Explorer 와 명령줄판 SBECmd 가 있습니다. RegRipper 에도 셸백 플러그인이 있습니다.
- 도구가 낸 경로 한두 개를 위 순서대로 손으로 따라가 봅니다. 폴더 이름과 `NodeSlot` 이 맞는지 확인합니다.
- 도구가 UsrClass.dat 와 NTUSER.DAT 를 둘 다 읽었는지 봅니다. 로그 파일을 반영했는지도 봅니다.
- 이름을 풀지 못한 항목이 있으면 그 값의 바이트를 직접 봅니다. 종류 표시 바이트로 어떤 셸 아이템인지부터 가립니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 점 |
|---|---|
| [열기·저장 대화상자 기록 (ComDlg32)](/02-artifacts/file-folder-usage/comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) | `ComDlg` 가 있는 슬롯의 폴더를 대화상자에서 실제로 골랐는지 |
| [탐색기 입력 기록 (TypedPaths·WordWheelQuery)](/02-artifacts/file-folder-usage/typedpaths-wordwheelquery.md) | 주소창에 경로를 직접 입력했는지 |
| [바로가기 파일 (LNK)](/02-artifacts/file-folder-usage/lnk.md) · [점프리스트 (Jump Lists)](/02-artifacts/file-folder-usage/jump-lists.md) | 셸백의 폴더 안에서 파일을 열었는지 |
| [마스터 파일 테이블 ($MFT)](/02-artifacts/filesystem/mft.md) · [폴더 인덱스와 슬랙 ($I30)](/02-artifacts/filesystem/i30.md) | 그 폴더가 디스크에 있는지, 있었는지 |
| [사용자별 장치 연결 (MountPoints2)](/02-artifacts/external-devices/usb-storage-artifacts/mountpoints2.md) | 셸백의 볼륨이 어떤 외부 장치였는지 |

## 실습

NIST CFReDS 같은 공개 검체의 사용자 프로필에서 풀어 볼 질문입니다.

1. NTUSER.DAT 와 UsrClass.dat 의 BagMRU 에서 각각 폴더가 몇 개 나옵니까? 로컬 폴더는 어느 쪽에 많습니까?
2. `.LOG1`·`.LOG2` 를 반영하기 전과 후에 BagMRU 키 개수가 달라집니까?
3. 경로 하나를 골라 `NodeSlot` 으로 `Bags` 슬롯을 찾습니다. 슬롯의 폴더 유형 GUID 를 같은 검체의 SOFTWARE 하이브 `FolderTypes` 에서 풀어 봅니다. `SniffedFolderType` 과 같습니까?
4. `NodeSlot` 이 없는 BagMRU 키가 있습니까? 있다면 그 키에 하위 키가 있습니까?
5. `ComDlg` 가 있는 슬롯을 찾아 그 폴더가 열기·저장 대화상자 기록에도 나오는지 확인합니다.

## 참고 문헌

- Joachim Metz, "Most recently used (MRU)" (winreg-kb) — https://github.com/libyal/winreg-kb/blob/main/docs/sources/explorer-keys/Most-recently-used.md
- Vincent Lo, "Windows ShellBag Forensics in Depth", SANS Institute GCFA Gold 논문 (2014) — https://www.sans.org/white-papers/34545/
- Joachim Metz, "Windows Shell Item format specification" (libfwsi) — https://github.com/libyal/libfwsi/blob/main/documentation/Windows%20Shell%20Item%20format.asciidoc
- Microsoft Learn, "FOLDERTYPEID (Shlguid.h)" — https://learn.microsoft.com/en-us/windows/win32/shell/foldertypeid
