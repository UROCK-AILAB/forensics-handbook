# 자동 복구·저장 안 한 문서 (AutoRecover·UnsavedFiles)

> 상위 페이지: [오피스 사용 흔적 (Microsoft Office)](index.md)

## 한 줄 요약

오피스는 로컬에서 작업 중인 문서를 따로 저장해 두었다가, 앱이 비정상으로 끝나면 다음 실행 때 되살려 보여 줍니다. 이 백업 파일은 사용자 프로필 폴더에 남습니다. 저장하지 않은 작업 내용이 이 파일에만 남아 있을 수 있습니다.

> 이 페이지에서 "(관찰)" 을 붙인 내용은 PC 한 대에서 직접 본 것입니다. 확인 범위: Windows 11 Home 10.0.26200, Microsoft 365 앱 16.0.20326.20158 (클릭 투 런). 다른 버전과 설정에서는 다를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

Microsoft 문서는 두 가지 저장 방식을 나눠 설명합니다.

| 문서를 연 곳 | 저장 방식 | 저장하는 곳 |
|---|---|---|
| 로컬 디스크, 네트워크 공유 폴더 | 자동 복구 (AutoRecover) | AutoRecover 파일 |
| OneDrive, SharePoint | 자동 저장 (AutoSave) | 클라우드의 그 문서 |

그래서 로컬 백업 파일이 남는 쪽은 로컬 디스크나 공유 폴더에서 연 문서입니다. OneDrive·SharePoint 문서의 로컬 사본은 [오피스 문서 캐시 (OfficeFileCache)](officefilecache.md) 에서 다룹니다.

Microsoft 문서가 적은 복구 흐름은 아래와 같습니다.

- Microsoft 는 자동 복구 저장 간격을 5분 이하로 두라고 권합니다.
- Word 는 시작할 때마다 AutoRecover 파일을 찾습니다. 찾으면 [문서 복구] 창에 "문서 이름 [Original]" 이나 "문서 이름 [Recovered]" 로 보여 줍니다.
- 앱이 저장 전에 비정상으로 끝나면 다음 실행 때 [문서 복구] 창이 열립니다.
- 이 창에는 마지막 저장, 마지막 자동 저장 (OneDrive·SharePoint 와 Microsoft 365), 마지막 자동 복구 가운데 하나에서 되살린 파일이 나옵니다.
- 창을 닫을 때 "아니요, 파일을 제거합니다" 와 "예, 나중에 이 파일을 보겠습니다" 가운데 하나를 고릅니다.
- Word 안에서는 파일 > 정보 > 문서 관리 > 저장되지 않은 문서 복구 로 찾습니다.

Microsoft 문서가 적은 파일 종류는 세 가지입니다.

| 파일 | 이름 모양 | 생기는 때 |
|---|---|---|
| 자동 복구 파일 | `*.asd` | 자동 복구가 저장할 때 |
| 백업 복사본 | `Backup of <원래 이름>.wbk` | Word 의 [항상 백업 복사본 만들기] 옵션을 켰을 때 |
| 임시 파일 | `~` 로 시작하는 `*.tmp` | 문서에는 생기는 때가 나오지 않습니다. |

## 위치와 버전별 차이

Microsoft 문서는 Microsoft 365 구독이면 백업 파일을 아래 두 곳에서 찾으라고 안내합니다.

```
C:\Users\<UserName>\AppData\Roaming\Microsoft\Word
C:\Users\<UserName>\AppData\Local\Microsoft\Office\UnsavedFiles
```

- 이 문서는 보관 (archived) 처리된 문서입니다 (ms.date 2024-06-06). 지금 버전과 다를 수 있습니다.
- KAPE 의 OfficeAutosave 타깃은 사용자마다 `AppData\Roaming\Microsoft\` 아래 `Word\`, `Excel\`, `Powerpoint\`, `Publisher\` 를 하위 폴더까지 모두 모읍니다.
- AutoRecover 폴더 위치를 정하는 레지스트리 값 이름은 확인하지 못했습니다. 관찰한 PC 의 `Software\Microsoft\Office\<버전>\Word\Options` 키에는 `AutoRecoverySaveIntervalMetadata` (REG_DWORD) 값만 있었고 경로 값은 없었습니다. (관찰)
- 자동 복구의 기본 간격은 확인하지 못했습니다.
- 정상 종료나 저장 때 AutoRecover 파일을 지우는 조건도 확인하지 못했습니다.

## 구조 — 관찰한 PC 에서 본 것

자동 복구 파일 안의 형식은 이 글에서 확인하지 못했습니다. 아래는 폴더와 파일 이름의 모양입니다. (관찰)

- `%LOCALAPPDATA%\Microsoft\Office\UnsavedFiles` 폴더가 없었습니다.
- `%APPDATA%\Microsoft\Word` 에는 `STARTUP` 폴더만 있었고 `.asd` 파일은 없었습니다.
- `%APPDATA%\Microsoft\Excel` 에는 `XLSTART` 말고 폴더가 두 개 더 있었습니다. 폴더 이름은 `<원래 문서 이름><18자리 숫자>` 였습니다.
- 그 폴더마다 파일이 두 개 있었습니다.
  - `<원래 문서 이름>((Unsaved-<18자리 숫자>)).xlsb`
  - `<원래 문서 이름>.csv.lnk`: 원본 CSV 를 가리키는 바로 가기입니다.
- 폴더 이름의 숫자와 `Unsaved-` 뒤 숫자는 서로 달랐습니다. 두 숫자의 뜻은 확인하지 못했습니다.
- `.xlsb` 파일의 마지막 수정 시각은 폴더의 마지막 수정 시각보다 몇 분 일렀습니다.

Excel 의 자동 복구 파일이 `.asd` 가 아니라 `.xlsb` 였다는 것은 이 PC 한 대의 결과입니다. Excel 자동 복구 형식은 공식 자료로 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것**

- 그 사용자 프로필에서 그 이름의 문서를 오피스로 작업한 흔적입니다.
- 파일 안에는 오피스가 그 파일을 쓸 때의 작업 내용이 들어 있을 수 있습니다. 저장한 원본과 내용이 다를 수 있습니다.
- Excel 폴더의 `.lnk` 는 원래 문서가 어디 있었는지 알려 줍니다. (관찰)
- `Backup of <원래 이름>.wbk` 파일이 있으면 그 파일이 생길 때 Word 의 [항상 백업 복사본 만들기] 옵션이 켜져 있었습니다.

**증명하지 못하는 것**

- 파일이 남은 까닭. 비정상 종료 때문인지, 저장하지 않고 닫았기 때문인지 파일만으로 가르지 못합니다. 파일을 지우는 조건을 확인하지 못했습니다.
- 파일이 없다고 작업하지 않았다는 것. 클라우드 문서는 자동 저장을 씁니다. 사용자가 [문서 복구] 창에서 "아니요, 파일을 제거합니다" 를 골랐을 수도 있습니다.
- 사용자가 문서를 끝내 저장했는지.
- 누가 작업했는지.

보고서 문장은 기록이 말하는 만큼만 씁니다.

- 쓰지 않을 문장: "사용자가 sales.csv 를 고치고 저장하지 않았다."
- 쓸 문장: "사용자 kim 의 `AppData\Roaming\Microsoft\Excel` 아래 폴더에 `sales((Unsaved-<숫자>)).xlsb` 파일과 `sales.csv.lnk` 파일이 있다. 바로 가기는 `D:\work\sales.csv` 를 가리킨다. 이는 Excel 이 이 CSV 문서에 대해 이름에 Unsaved 가 들어간 사본을 남긴 기록이다." (예시 문장입니다.)

## 시각 해석

- 자동 복구 파일 안에 시각이 있는지는 확인하지 못했습니다. 시각은 파일시스템에서 읽습니다 ([마스터 파일 테이블](../../filesystem/mft.md)).
- 백업 파일의 생성·수정 시각은 그 백업 파일의 시각입니다. 원본 문서의 시각이 아닙니다.
- 관찰한 PC 에서는 `.xlsb` 수정 시각이 폴더 수정 시각보다 몇 분 일렀습니다. (관찰) 폴더 시각을 백업 파일 시각으로 옮겨 적지 않습니다.
- **18자리 숫자.** 요즘 날짜의 FILETIME 을 10진수로 적으면 18자리입니다. 그래서 시각일 수도 있습니다. 그러나 이 글에서 시각으로 확인하지 못했습니다. 풀어 본 값은 파일시스템 시각과 맞춰 본 뒤에만 씁니다. 푸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.

## 함정과 한계

- **공식 경로와 실제 모양이 다를 수 있습니다.** 공식 문서는 보관 처리됐습니다. 관찰한 PC 에는 `UnsavedFiles` 폴더도, Word 의 `.asd` 파일도 없었고, Excel 은 다른 모양의 파일을 남겼습니다. (관찰)
- **수집 범위를 확인합니다.** KAPE OfficeAutosave 타깃의 폴더는 `Roaming` 아래 네 곳입니다. `UnsavedFiles` 는 `Local` 아래에 있으므로 수집 목록에 따로 넣습니다.
- **폴더 위치가 바뀌었을 수 있습니다.** 위치를 정하는 레지스트리 값을 확인하지 못했습니다. 기본 폴더에 없으면 디스크 전체에서 `*.asd`, `Backup of *.wbk`, `*((Unsaved-*` 이름을 찾습니다.
- **클라우드 문서는 여기 남지 않을 수 있습니다.** OneDrive·SharePoint 문서는 자동 저장을 씁니다. [오피스 문서 캐시 (OfficeFileCache)](officefilecache.md) 를 봅니다.
- **지운 백업 파일.** 지우는 조건을 모르므로 지금 없는 파일도 찾아봅니다. [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 와 [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 을 봅니다.
- **확장자만 믿지 않습니다.** 파일 앞 바이트로 실제 형식을 확인합니다.

## 직접 분석해 보기

자동 복구 파일 안의 형식은 이 글에서 확인하지 못해 헥스 예시를 싣지 않습니다. 아래 절차는 파일을 찾아 모으고 원래 문서와 잇는 데까지입니다.

1. 사용자마다 `AppData\Roaming\Microsoft\` 아래 `Word`·`Excel`·`Powerpoint`·`Publisher` 폴더와 `AppData\Local\Microsoft\Office\UnsavedFiles` 를 하위 폴더까지 모읍니다. KAPE 를 쓴다면 OfficeAutosave 타깃에 `UnsavedFiles` 를 더합니다.
2. 이름 모양으로 거릅니다. `*.asd`, `Backup of *.wbk`, `~*.tmp`, `*((Unsaved-*` 를 찾습니다.
3. 파일마다 앞 바이트를 보고 실제 형식을 적습니다.
4. 폴더 안 `.lnk` 는 바로가기 파서로 풀어 원래 경로를 봅니다 ([바로가기 파일](../lnk.md)).
5. 사본을 격리된 환경에서 열어 내용을 봅니다. 원래 문서가 남아 있으면 내용을 견줍니다.
6. $MFT 와 USN 변경 저널에서 같은 폴더의 지운 파일 이름을 찾습니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [오피스 최근 파일 (File MRU·Place MRU)](file-mru-place-mru.md) | 같은 문서의 최근 사용 기록 |
| [오피스 문서 캐시 (OfficeFileCache)](officefilecache.md) | OneDrive·SharePoint 문서의 로컬 사본 |
| [바로가기 파일](../lnk.md) | 폴더 안 `.lnk` 가 가리키는 원래 경로 |
| [마스터 파일 테이블](../../filesystem/mft.md)·[USN 변경 저널](../../filesystem/usnjrnl.md) | 백업 파일이 생기고 지워진 기록 |
| [윈도 오류 보고](../../execution/wer.md) | 오피스 앱이 비정상으로 끝난 기록 |
| [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 지금은 없는 옛 백업 파일 |

시나리오로 이어서 보려면 [지운 파일의 흔적 찾기](../../../04-scenarios/activity/deleted-file-traces.md) 를 봅니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 오피스를 쓴 사용자 프로필이 있는 이미지를 고릅니다. 오피스를 설치한 가상 머신을 직접 만들어도 됩니다.

1. 사용자마다 위 폴더를 모으고 파일을 종류별로 셉니다.
2. Excel 폴더 안 `.lnk` 가 가리키는 원래 파일이 지금도 있는지 봅니다.
3. 폴더 이름과 파일 이름의 18자리 숫자를 FILETIME 으로 풀어 봅니다. 파일시스템 시각과 맞나요?
4. 가상 머신에서 Word 문서를 고치다 작업 관리자로 Word 를 끝냅니다. 어느 폴더에 어떤 파일이 생기는지 봅니다. 다시 실행해 [문서 복구] 창을 닫은 뒤에도 파일이 남는지 봅니다.
5. Excel 로 같은 실험을 하고 파일 모양을 Word 와 견줍니다.
6. 결과로 보고서 문장을 하나 씁니다. "저장하지 않았다" 가 아니라 기록이 말하는 만큼만 씁니다.

## 참고 문헌

- Microsoft Learn, "How to recover unsaved Word documents" (보관 문서). https://learn.microsoft.com/en-us/office/troubleshoot/word/recover-lost-unsaved-corrupted-document
- Microsoft 지원, "How Word creates and recovers the AutoRecover files". https://support.microsoft.com/topic/how-word-creates-and-recovers-the-autorecover-files-a33ec235-9d68-cf62-e66a-6a740cf51821
- KapeFiles, OfficeAutosave.tkape. https://raw.githubusercontent.com/EricZimmerman/KapeFiles/master/Targets/Windows/OfficeAutosave.tkape
