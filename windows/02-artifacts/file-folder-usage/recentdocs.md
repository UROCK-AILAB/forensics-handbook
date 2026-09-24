# 최근 문서 (RecentDocs)

## 한 줄 요약

최근 문서 (RecentDocs) 는 사용자 하이브 NTUSER.DAT 안의 MRU 목록입니다. 사용자가 최근에 다룬 파일의 이름을 모아 두고, 확장자마다 하위 키를 따로 둡니다. 순서는 MRUListEx 값이 정합니다. 시각은 키마다 하나뿐이고, 항목마다 따로 남지 않습니다.

## 무엇을 기록하나 · 왜 생기나

키 하나에 항목 값이 여러 개 있습니다. Windows Vista 이후에는 항목 값 하나에 두 가지가 들어 있습니다.

- 파일 이름 (UTF-16LE 문자열)
- 그 파일 이름을 담은 셸 항목 (Shell Item)

뿌리 키 아래에는 확장자마다 하위 키가 있습니다. 하위 키에는 그 확장자의 파일만 모입니다.

### 기록이 생기는 계기

Microsoft 문서는 `SHAddToRecentDocs` 함수를 "항목에 접근했다" 는 사실을 시스템에 알리는 함수로 설명합니다. 셸은 이 알림으로 가장 최근에 쓴 항목과 가장 자주 쓴 항목의 목록을 만듭니다. 탐색기에서 파일을 열 때와 공통 파일 대화상자로 열기·저장·새로 만들기를 할 때는 셸이 앱 대신 이 함수를 부릅니다. 함수가 불리는 조건은 [바로가기 파일 (LNK)](lnk.md) 에서 자세히 다룹니다.

RecentDocs 를 해석할 때 알아 둘 점은 다음과 같습니다.

- Microsoft 문서에는 이 함수가 RecentDocs 레지스트리 키를 직접 고친다는 문장이 없습니다. RecentDocs 가 같은 계기로 생긴다는 설명은 널리 쓰이지만, 확인한 자료로 확정하지는 못했습니다.
- 자기 화면으로 파일을 고르는 앱은 이 함수를 직접 불러야 합니다. 부르지 않는 앱으로 다룬 파일은 기록이 남지 않을 수 있습니다.
- 실행 파일 (.exe) 은 XP 이후 최근 문서 목록에서 걸러집니다. 그래서 이 목록은 프로그램 실행 기록이 아닙니다.
- 파일 형식의 클래스 키에 `NoRecentDocs` 값 (REG_SZ, 데이터 없음) 이 있으면 그 형식은 기록하지 않습니다. `*`, `AllFileSystemObjects`, `Folder`, `Directory`, `DesktopBackground` 클래스에는 이 값이 기본으로 들어 있습니다.
- Windows 7 전에는 "열기" (open) 동사만 기록을 만들었습니다. Windows 7 부터는 다른 동사로 다뤄도 사용 기록이 생길 수 있습니다.

## 위치와 버전별 차이

### 위치

| 키 | 담는 것 |
|---|---|
| `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs` | 확장자와 관계없는 최근 파일 목록 |
| `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs\<확장자>` | 그 확장자의 최근 파일 목록 |

- HKCU 는 로그온한 사용자의 NTUSER.DAT 입니다. 그래서 어느 계정의 기록인지 가를 수 있습니다. 하이브 파일의 위치는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.
- winreg-kb 는 하위 키 이름의 예로 `.exe` 와 함께 `Folder` 를 듭니다. `Folder` 하위 키에 폴더만 모인다는 설명은 확인한 자료로 확정하지 못했습니다.
- 뿌리 키와 하위 키가 항목을 몇 개까지 보관하는지는 확인한 자료에 없습니다.

### Windows 버전에 따라 달라지는 점

| Windows | 항목 값의 형태 | 근거 |
|---|---|---|
| 2000 · XP | 문자열 | winreg-kb |
| Vista 이후 | 문자열 + 셸 항목, 순서는 MRUListEx | winreg-kb |
| 11 25H2 | 키가 있었습니다. 값과 하위 키는 0개였습니다 | 관찰 (확인 범위: Windows 11 25H2, PC 한 대) |

Windows 11 에서 키가 비어 있던 PC 의 사정은 아래 "함정과 한계" 에서 다룹니다.

## 구조

MRUList·MRUListEx 를 읽는 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 의 MRU 목록 설명을 따릅니다. 여기서는 RecentDocs 에만 해당하는 점을 적습니다.

### 순서 값 MRUListEx

| 항목 | 내용 |
|---|---|
| 값 이름 | `MRUListEx` |
| 데이터 | 4바이트 리틀 엔디언 정수의 배열 |
| 순서 | 첫 정수가 가장 최근 항목, 두 번째 정수가 그다음 항목입니다 |
| 끝 표시 | -1 (`FF FF FF FF`) |

- 배열의 정수는 항목 값의 이름을 가리킵니다. 항목 값 이름 `0`, `1`, `2` … 는 번호표일 뿐입니다. 이름의 숫자 순서는 시간 순서가 아닙니다.

### 항목 값 (Vista 이후)

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 가변 | 파일 이름. UTF-16LE 이고 끝 문자 (`00 00`) 까지 들어 있습니다 |
| 이름 뒤 | 가변 | 파일 이름을 담은 셸 항목. 없으면 비어 있습니다 |

셸 항목을 푸는 방법은 [셸 아이템](../../01-foundations/shell-document-formats/shell-item-pidl.md) 에서 다룹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 사용자 하이브의 최근 문서 목록에 이 파일 이름이 올라간 적이 있습니다 | 그 계정 앞에 실제로 누가 앉아 있었는지 |
| 같은 키 안에서 항목끼리의 앞뒤 순서 | 두 번째 이후 항목이 각각 언제 들어왔는지 |
| 키가 마지막으로 바뀐 때 (UTC) | 파일을 연 것인지, 저장한 것인지, 새로 만든 것인지 |
| 어느 확장자 하위 키에 이름이 있는지 | 파일의 전체 경로와 볼륨. 파일이 지금도 있는지 |
| | 몇 번 다뤘는지. 내용을 읽거나 고쳤는지 |

- 목록에 없다는 사실로 파일을 다루지 않았다고 단정하지 않습니다. 앱이 함수를 부르지 않았거나, 형식이 `NoRecentDocs` 로 막혀 있거나, 설정이 기록을 막았을 수 있습니다.
- 경로와 볼륨이 필요하면 같은 이름의 바로가기 파일, 점프리스트, 열기·저장 대화상자 기록을 찾습니다. 아래 "교차 검증" 을 봅니다.

### 보고서 문장

아래 이름과 시각은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 A 의 NTUSER.DAT 에서 RecentDocs 의 docx 확장자 하위 키를 보면 MRUListEx 첫 항목이 `plan.docx` 입니다. 이 키의 마지막 기록 시각은 2025-04-02 06:15:30 UTC 입니다."
- 쓰면 안 되는 문장: "사용자 A 가 2025-04-02 15:15 에 plan.docx 를 열었습니다."

## 시각 해석

| 시각 | 어디에 남나 | 무엇을 가리키나 | 형식 |
|---|---|---|---|
| 키의 마지막 기록 시각 | 뿌리 키와 확장자 하위 키마다 하나씩 | 그 키가 마지막으로 바뀐 때 | FILETIME, UTC |

- 항목 값에는 시각이 없습니다. plaso 도 RecentDocs 기록의 시각으로 키의 마지막 기록 시각 하나만 씁니다.
- 키의 마지막 기록 시각은 MRUListEx 첫 항목이 들어간 때와 가깝다고 보는 것이 보통입니다. 확인한 자료가 이 해석을 확정하지는 않습니다. 보고서에는 "키의 마지막 기록 시각" 으로 적고, 첫 항목과 이어 읽는 것은 추정이라고 밝힙니다.
- 뿌리 키와 확장자 하위 키는 시각이 따로 있습니다. 확장자 하위 키의 시각은 그 확장자 목록이 마지막으로 바뀐 때입니다.
- 두 번째 이후 항목의 시각은 이 키만으로 알 수 없습니다. 같은 파일의 바로가기 파일이나 점프리스트 시각을 찾아 맞춰 봅니다.
- 키 시각의 성질은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서, FILETIME 계산은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서, 현지 시각 변환은 [시간대 설정](../system-account/time-zone.md) 에서 다룹니다.

## 함정과 한계

1. **값 이름의 번호를 순서로 읽습니다.** 순서는 MRUListEx 만 정합니다. 값 이름 `0` 이 가장 오래된 항목이라는 보장이 없습니다.
2. **키 시각을 모든 항목에 붙입니다.** 키 시각은 첫 항목에만 조건부로 이어집니다.
3. **빈 키를 "쓰지 않았다" 로 읽습니다.** Windows 11 25H2 PC 한 대에서 다음을 봤습니다. (확인 범위: Windows 11 25H2, PC 한 대)
   - `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced` 의 `Start_TrackDocs` 값이 0 이었습니다.
   - RecentDocs 키는 있었지만 값과 하위 키가 0개였습니다.
   - RecentDocs 키의 마지막 기록 시각은 사용자 프로필을 만든 날과 같았습니다.
   - 같은 PC 에서 [열기·저장 대화상자 기록](comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) 은 조사 당일에도 갱신됐습니다.
   - `%APPDATA%\Microsoft\Windows\Recent` 폴더에는 .lnk 파일이 0개였습니다.

   `Start_TrackDocs` 가 언제 0 이 됐는지는 알 수 없습니다. 그래서 "0 이라서 비었다" 는 인과를 이 관찰만으로 단정하지 못합니다. 설정 앱의 "최근에 연 항목 표시" 토글이 이 값과 같은 것인지도 확인하지 못했습니다. 빈 키를 만나면 이 값을 함께 적어 둡니다.
4. **이 목록을 실행 기록으로 씁니다.** 실행 파일은 걸러집니다. 실행 여부는 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md) 의 흔적으로 봅니다.
5. **끝 표시 뒤를 무시하거나 그대로 읽습니다.** plaso 는 MRUListEx 에서 -1 을 만나면 읽기를 멈춥니다. 끝 표시 뒤에 남은 번호는 보여 주지 않습니다. 도구마다 처리가 다를 수 있으므로 MRUListEx 길이와 값 개수가 맞지 않으면 원시 바이트를 직접 봅니다.
6. **XP 하이브를 Vista 이후 틀로 읽습니다.** 2000·XP 의 항목 값은 문자열뿐입니다. 먼저 [시스템 기본 정보](../system-account/os-version-computer-name-install-date-shutdown-t.md) 로 버전을 확인합니다.

### 지우기와 조작

- **정책으로 로그오프 때 지웁니다.** 정책 "Clear history of recently opened documents on exit" 의 값은 `Software\Microsoft\Windows\CurrentVersion\Policies\Explorer` 키 (사용자 구성) 의 `ClearRecentDocsOnExit` 입니다. Microsoft 문서에 따르면 이 정책은 로그오프 때 최근 문서 바로가기를 지웁니다. 점프리스트의 최근·자주 항목도 지웁니다 ([점프리스트](jump-lists.md)). 프로그램 파일 메뉴 아래의 최근 파일 목록은 지우지 않습니다. 이 정책이 RecentDocs 레지스트리 키도 지우는지는 확인하지 못했습니다.
- **메뉴만 숨깁니다.** 정책 "Remove Recent Items menu from Start Menu" (값 `NoRecentDocsMenu`) 를 켜도 바로가기는 계속 저장됩니다. 메뉴만 보이지 않습니다. 이 값이 켜져 있어도 기록이 없다고 보지 않습니다.
- **기록을 남기지 않는 정책.** Microsoft 문서는 "Do not keep history of recently opened documents" 정책을 이름으로만 언급합니다. 이 정책의 값 이름과 동작은 확인하지 못했습니다.
- **값이나 키를 지웁니다.** 지운 키와 값은 하이브 안 빈 공간이나 트랜잭션 로그에 남을 수 있습니다. 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다. 옛 하이브는 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 winreg-kb 의 설명을 보고 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

먼저 확장자 하위 키의 `MRUListEx` 값입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    02 00 00 00 00 00 00 00 01 00 00 00 FF FF FF FF
```

1. 4바이트씩 끊어 리틀 엔디언으로 읽습니다. 2, 0, 1, -1 입니다.
2. 가장 최근 항목은 값 `2` 이고, 그다음은 값 `0`, 그다음은 값 `1` 입니다.
3. -1 에서 읽기를 멈춥니다. 항목은 3개입니다.

다음은 가장 최근 항목인 값 `2` 의 앞부분입니다. `..` 은 셸 항목이라 줄인 바이트입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    70 00 6C 00 61 00 6E 00 2E 00 64 00 6F 00 63 00
0x10    78 00 00 00 .. .. .. .. .. .. .. .. .. .. .. ..
```

4. 0x00 부터 2바이트씩 UTF-16LE 로 읽습니다. `plan.docx` 입니다.
5. 0x12 의 `00 00` 이 끝 문자입니다.
6. 0x14 부터는 셸 항목입니다. [셸 아이템](../../01-foundations/shell-document-formats/shell-item-pidl.md) 페이지대로 풉니다.
7. 이 키의 마지막 기록 시각을 따로 읽어 둡니다. 항목 값에는 시각이 없기 때문입니다.

### 공개 도구로 한 번

plaso 의 레지스트리 파서는 RecentDocs 키와 그 하위 키를 "문자열 + 셸 항목" 형식으로 읽습니다. 플러그인 이름은 `mrulistex_string_and_shell_item` 입니다. 다른 레지스트리 파서를 써도 됩니다. 도구를 쓸 때는 다음을 확인합니다.

- 도구가 보여 준 순서가 MRUListEx 를 푼 순서와 같은지 확인합니다.
- 도구가 키 시각을 항목마다 붙여서 보여 주지 않는지 확인합니다.
- 시각을 UTC 로 보여 주는지, 분석 PC 의 현지 시각으로 바꿔 보여 주는지 확인합니다.
- 끝 표시 뒤에 남은 항목을 어떻게 처리하는지 확인합니다.
- 키 한두 개는 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [바로가기 파일 (LNK)](lnk.md) | Recent 폴더에 같은 이름의 바로가기가 있는지. 바로가기에는 경로·볼륨·대상 시각이 남습니다 |
| [점프리스트](jump-lists.md) | 어느 앱의 목록에 같은 파일이 있는지. 항목마다 갱신 시각이 있습니다 |
| [열기·저장 대화상자 기록](comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) | 공통 대화상자로 다룬 파일의 경로. RecentDocs 가 비어도 이쪽은 남을 수 있습니다 |
| [오피스 사용 흔적](microsoft-office/index.md) | 오피스 앱이 따로 남긴 최근 파일 목록 |
| [셸백](shellbags/index.md) | 그 파일이 있던 폴더를 탐색기로 연 흔적 |
| [윈도 타임라인](activitiescache-db.md) | 같은 파일을 연 활동 기록이 있는지 |
| [마스터 파일 테이블](../filesystem/mft.md) · [USN 변경 저널](../filesystem/usnjrnl.md) | 같은 이름의 파일이 어디에 있었고 언제 바뀌었는지 |
| [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 옛 하이브의 목록. 지금 목록과 비교하면 사라진 항목이 드러납니다 |

여러 기록을 합쳐 읽는 순서는 [이 파일을 누가 언제 열었나](../../04-scenarios/activity/file-access.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 사용자 하이브가 든 Windows 이미지를 골라 다음을 풀어 봅니다.

1. 검체의 Windows 버전은 무엇입니까? 항목 값이 문자열뿐입니까, 셸 항목이 붙어 있습니까?
2. RecentDocs 뿌리 키의 MRUListEx 를 직접 풀어 항목을 순서대로 적어 봅니다. 값 이름의 번호 순서와 어디서 달라집니까?
3. 확장자 하위 키는 몇 개입니까? 각 하위 키의 첫 항목과 마지막 기록 시각 (UTC) 을 표로 적어 봅니다.
4. 뿌리 키의 첫 항목과 확장자 하위 키의 첫 항목이 같은 파일입니까? 두 키의 시각을 비교해 봅니다.
5. 첫 항목과 같은 이름의 바로가기 파일이 Recent 폴더에 있습니까? 바로가기 파일의 시각과 키 시각은 얼마나 떨어져 있습니까?
6. `Explorer\Advanced` 의 `Start_TrackDocs` 값과 정책 키의 `ClearRecentDocsOnExit` 값이 있습니까? 있다면 목록 상태와 함께 적어 봅니다.

실험용 가상 머신이 있으면 탐색기로 파일을 열고, 메모장 같은 앱의 대화상자로 파일을 저장해 봅니다. 앞뒤로 NTUSER.DAT 를 떠서 어느 키가 바뀌는지 비교합니다. 결과에는 실험한 Windows 버전을 함께 적습니다.

## 참고 문헌

- libyal winreg-kb, "Most recently used (MRU)" — https://raw.githubusercontent.com/libyal/winreg-kb/main/docs/sources/explorer-keys/Most-recently-used.md
- log2timeline plaso, `winreg_plugins/mrulistex.py` — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/winreg_plugins/mrulistex.py
- Microsoft Learn, "SHAddToRecentDocs function (shlobj_core.h)" — https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shaddtorecentdocs
- Microsoft Learn, "ADMX_StartMenu Policy CSP" — https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-admx-startmenu
