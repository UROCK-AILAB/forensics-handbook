# 오피스 매크로 (VBA Macro)

## 한 줄 요약

오피스 문서 안에는 VBA 매크로 코드가 들어 있을 수 있습니다. 97-2003 문서는 OLE 구조 안에, 2007 이후 OpenXML 문서는 ZIP 안의 `vbaProject.bin` 에 코드가 들어갑니다(참고 1). 코드 스트림에는 소스 글자와 컴파일된 코드 (P-code) 가 함께 있어서, 둘이 다르면 소스만 읽어서는 판단할 수 없습니다. 인터넷에서 받은 파일의 매크로는 Office 가 기본으로 막습니다(참고 2). 그래서 매크로가 파일에 있다는 것과 매크로가 실행됐다는 것은 따로 확인합니다.

> 이 페이지에서 "(관찰)" 을 붙인 내용은 PC 한 대에서 직접 확인한 것입니다. 확인 범위: Windows 11 (빌드 26200), Microsoft 365 설치본에 들어 있는 Excel 추가 기능 두 개의 사본(`Office16\Library\SOLVER\SOLVER.XLAM`, `Office16\1042\EXPTOOWS.XLA`), Python 3.12.10, oletools 0.60.2 (olefile 0.47). "(oletools 소스)" 는 oletools 0.60.2 의 `olevba.py` 소스 코드와 주석에서 읽은 것입니다. 주석이 MS-OVBA 명세를 인용하지만, 명세 원문과는 대조하지 못했습니다.

## 무엇을 기록하나 · 왜 생기나

- 매크로가 든 문서를 저장하면 VBA 프로젝트가 문서 파일 안에 함께 들어갑니다. 코드는 `vbaProject.bin` 이나 `Macros/VBA/` 저장소 같은 OLE 구조 안에 있습니다(참고 1).
- VBA 프로젝트에는 프로젝트 이름, 모듈 이름, 모듈 소스, 컴파일된 코드, 코드 페이지 같은 값이 남습니다(관찰).
- 문서를 열거나 닫을 때 저절로 실행되는 프로시저 이름이 있습니다. 목록은 아래 "구조" 에 있습니다.
- 사고 대응에서는 첨부 파일이나 받은 문서에 매크로가 있는지, 자동 실행 이름과 의심 키워드가 있는지 먼저 봅니다. 공개 도구 olevba 가 이런 항목을 찾아 줍니다(참고 1).

## 위치와 버전별 차이

### 형식별 위치

| 형식 | 확장자 (참고 1) | 매크로가 있는 곳 |
|---|---|---|
| 97-2003 OLE | Word `.doc`·`.dot`, Excel `.xls`, PowerPoint `.ppt` | 파일 안 OLE 저장소. Excel 추가 기능 `.XLA` 에서는 루트의 `Workbook` 스트림 옆에 `_VBA_PROJECT_CUR` 저장소가 있었습니다(관찰) |
| 2007 이후 OpenXML | `.docm`·`.dotm`·`.xlsm`·`.xlsb`·`.pptm`·`.ppsm` | ZIP 안의 `vbaProject.bin`. Excel 추가 기능 `.XLAM` 에서는 `xl/vbaProject.bin` 이었습니다(관찰) |
| 그 밖에 olevba 가 읽는 형식 | Word 2003 XML, MHTML (`.mht`), Publisher (`.pub`), SYLK (`.slk`) | 이 페이지에서 실물로 보지 않았습니다 |

- `_VBA_PROJECT_CUR` 아래 구성은 `vbaProject.bin` 의 루트와 같았습니다(관찰).
- Word 97-2003 문서의 `Macros` 저장소는 olevba 문서에 이름만 나옵니다(참고 1). 이 페이지에서 실물로 보지 못했습니다.
- `vbaProject.bin` 의 첫 8바이트는 `D0 CF 11 E0 A1 B1 1A E1` 이었습니다(관찰). OLE 복합 파일이라는 뜻입니다. 이 형식은 [OLE 복합 파일](/01-foundations/shell-document-formats/compound-file-binary.md) 에서 다룹니다.

### OpenXML 의 서명 파트 (관찰)

`SOLVER.XLAM` 의 `xl/_rels/vbaProject.bin.rels` 는 서명 파트 세 개를 가리켰습니다.

| 파트 | 관계 형식 |
|---|---|
| `vbaProjectSignature.bin` | `.../office/2006/relationships/vbaProjectSignature` |
| `vbaProjectSignatureAgile.bin` | `.../2014/relationships/vbaProjectSignatureAgile` |
| `vbaProjectSignatureV3.bin` | `.../2020/07/relationships/vbaProjectSignatureV3` |

- 97-2003 OLE 파일 안에서 서명이 들어가는 스트림 이름은 확인하지 못했습니다. 관찰한 `EXPTOOWS.XLA` 에는 서명이 없었습니다.
- 서명 파트가 있다는 것과 서명이 유효하다는 것은 다릅니다. 이 페이지에서는 서명 검증을 다루지 않습니다.

### 인터넷에서 받은 파일의 매크로 차단 (참고 2)

Office 는 인터넷에서 받은 파일의 VBA 매크로를 기본으로 막도록 바뀌었습니다. 이 동작은 Windows 용 Office 의 Access·Excel·PowerPoint·Project·Publisher·Visio·Word 에만 해당합니다. Mac·Android·iOS·웹용 Office 는 해당하지 않습니다.

Access·Excel·PowerPoint·Visio·Word 에 적용된 판입니다.

| 업데이트 채널 | 판 | 적용 시작 |
|---|---|---|
| Current Channel (Preview) | 2203 | 2022-04-12 배포 시작 |
| Current Channel | 2206 | 2022-07-27 배포 시작 |
| Monthly Enterprise Channel | 2208 | 2022-10-11 |
| Semi-Annual Enterprise Channel (Preview) | 2208 | 2022-10-11 |
| Semi-Annual Enterprise Channel | 2208 | 2023-01-10 |

- Publisher 는 2023-02-14 부터, Project 는 2024-08-13 부터 적용됐습니다.
- 사건 시점의 Office 채널과 판을 먼저 확인합니다. 적용 전이면 예전 동작을 기준으로 해석합니다.

Office 는 아래 순서로 매크로를 켤지 정합니다(참고 2).

| 단계 | 확인하는 것 | 결과 |
|---|---|---|
| 1 | 파일에 웹 표시 (Mark of the Web, MOTW) 가 있는지. 메일 첨부가 한 예입니다 | 있으면 다음 단계로 갑니다 |
| 2 | 신뢰할 수 있는 위치 (Trusted Location) 에 있는 파일인지 | 그렇다면 매크로를 켜고 엽니다 |
| 3 | 매크로에 디지털 서명이 있고, 신뢰할 수 있는 게시자 인증서가 있는지 | 그렇다면 매크로를 켭니다 |
| 4~5 | 정책이 막거나 허용하는지 | 정책을 그대로 따릅니다 |
| 6 | 이 변경 전에 사용자가 [콘텐츠 사용] 을 눌러 신뢰 문서가 된 파일인지 | 그렇다면 매크로를 켭니다 |
| 7 | 나머지 | 막고 SECURITY RISK 배너를 띄웁니다 |

- 새 SECURITY RISK 배너에는 [콘텐츠 사용] 단추가 없습니다. 예전 SECURITY WARNING 배너에는 이 단추가 있었습니다.
- 정책 이름은 "Block macros from running in Office files from the Internet" 과 "VBA Macro Notification Settings" 입니다. Excel 은 "Macro Notification Settings" 라는 이름을 씁니다.
- 정책은 사용자 구성\정책\관리 템플릿 아래 앱마다 있습니다. Word 의 예는 `Microsoft Word 2016\Word Options\Security\Trust Center` 입니다.
- 이 정책은 Microsoft 365 Apps for enterprise 에서만 쓸 수 있습니다.
- 보안 센터의 매크로 설정 기본값은 "알림과 함께 모든 매크로 사용 안 함" 입니다.
- 설정 값이 남는 레지스트리 경로는 참고 2 에 나오지 않습니다. 사용자별 매크로 설정 값은 [신뢰 문서 기록 (Trust Records)](/02-artifacts/file-folder-usage/microsoft-office/trust-records.md) 에서 다룹니다.

## 구조

### VBA 프로젝트 (관찰)

`vbaProject.bin` 안의 구성입니다.

```
(루트)
├─ PROJECT          글자로 된 프로젝트 정보
├─ PROJECTwm
├─ PROJECTlk
├─ VBA\
│   ├─ dir          압축된 프로젝트·모듈 목록
│   ├─ _VBA_PROJECT
│   ├─ __SRP_0, __SRP_1 …
│   └─ <모듈 이름>   모듈마다 스트림 하나. 스트림 이름 = 모듈 이름
└─ <폼 이름>\        사용자 폼마다 저장소 하나 (예: dlgFinish 아래 CompObj, VBFrame, f, o 와 하위 저장소)
```

- `__SRP_n` 스트림이 무엇을 담는지는 확인하지 못했습니다.

### PROJECT 스트림 (관찰)

글자로 된 줄 목록입니다. `SOLVER.XLAM` 에서 본 줄의 모양입니다.

| 줄 | 예 |
|---|---|
| 프로젝트 ID | `ID="{GUID}"` |
| 문서 모듈 | `Document=ThisWorkbook/&H00000000`, `Document=Sheet2/&H00000000` |
| 일반 모듈 | `Module=…` |
| 폼 | `BaseClass=…` |
| 클래스 모듈 | `Class=…` |
| 프로젝트 이름 | `Name="Solver"` |
| 그 밖 | `HelpContextID="0"`, `VersionCompatible32="393222000"` |
| 보호 관련으로 보이는 세 줄 | `CMG="…"`, `DPB="…"`, `GC="…"` |
| 절 | `[Host Extender Info]`, `[Workspace]` (모듈마다 창 위치 숫자) |

- `SOLVER.XLAM` 의 ID 는 모두 0 인 GUID 였습니다. `EXPTOOWS.XLA` 의 ID 는 `{2D87F468-…}` 로 시작하는 실제 GUID 였습니다.
- CMG·DPB·GC 가 무엇을 뜻하는지, 어떤 방식으로 암호화하는지는 확인하지 못했습니다.

### _VBA_PROJECT 스트림 (관찰)

| 파일 | 첫 바이트 |
|---|---|
| `SOLVER.XLAM` | `CC 61 B5 00 00 03 00` |
| `EXPTOOWS.XLA` | `CC 61 A3 00 00 01 00` |

- 앞 2바이트 `CC 61` 은 두 파일이 같았습니다. 그 뒤 2바이트(0x00B5, 0x00A3)는 달랐습니다.
- 이 값이 어떤 Office 판에 대응하는지는 확인하지 못했습니다.

### dir 스트림 (관찰)

- 첫 바이트가 `01` 이고 압축돼 있었습니다. `SOLVER.XLAM` 은 2,130바이트였고, 풀면 6,211바이트였습니다.
- 푼 뒤에는 레코드가 이어집니다. 관찰한 레코드는 번호 2바이트, 크기 4바이트, 값으로 이뤄졌습니다. 모든 레코드가 이 모양인지는 명세 원문과 대조하지 못했습니다.
- 압축 조각 하나는 머리 2바이트와 데이터 4,096바이트로, 최대 4,098바이트입니다(oletools 소스).

| 번호 | 이름 | `SOLVER.XLAM` | `EXPTOOWS.XLA` |
|---|---|---|---|
| 0x0001 | SYSKIND | 3 | 1 |
| 0x0002 | LCID | 0x0409 | 0x0409 |
| 0x0003 | CODEPAGE | 1252 | 1252 |
| 0x0004 | 프로젝트 이름 | `Solver` | |

- `EXPTOOWS.XLA` 는 한국어 폴더(1042)에 있었지만 CODEPAGE 는 1252 였습니다. 폴더 언어로 코드 페이지를 짐작하지 않습니다.
- SYSKIND 값은 0 = 16비트 Windows, 1 = 32비트 Windows, 2 = Macintosh, 3 = 64비트 Windows 로 읽습니다(oletools 소스).

모듈마다 아래 레코드가 있습니다.

| 번호 | 내용 |
|---|---|
| 0x0019 | 모듈 이름 |
| 0x001A | 스트림 이름 |
| 0x0031 | MODULEOFFSET. 모듈 스트림 안에서 소스가 시작하는 위치 |
| 0x0021 또는 0x0022 | 모듈 종류 |

- 0x0021 은 일반 (procedural) 모듈이고, 0x0022 는 문서·클래스·디자이너 모듈입니다(oletools 소스).
- 실제 파일에서 `ThisWorkbook`·`Sheet` 는 0x0022, `RibbonX_Callbacks`·`VBA_Functions` 는 0x0021 이었습니다(관찰).

### 모듈 스트림: P-code 와 소스 (관찰)

모듈 스트림의 앞부분은 소스가 아닙니다.

- `SOLVER.XLAM` 의 `modLocalize` 스트림은 3,448바이트였고, MODULEOFFSET 은 2,698 이었습니다.
- 2,698 위치의 바이트는 `01` 이었습니다. 여기부터 풀면 `Attribute VB_Name = "modLocalize"` 로 시작하는 소스 글자가 나왔습니다.
- 그 앞 2,698바이트는 컴파일된 코드 (P-code) 영역입니다. oletools 는 이 영역을 pcodedmp 로 풀어 읽습니다(oletools 소스).

> 그림 자리: 모듈 스트림 하나를 가로 막대로 그리고, 0 ~ MODULEOFFSET 구간을 P-code, MODULEOFFSET 부터 끝까지를 압축된 소스(첫 바이트 01)로 나눠 표시. dir 스트림의 0x0031 레코드에서 화살표로 경계를 가리킴

### 자동 실행 이름 (oletools 소스)

olevba 가 자동 실행 후보로 찾는 이름입니다.

| 앱 | 언제 | 이름 |
|---|---|---|
| Word | 열 때 | `AutoExec`, `AutoOpen`, `DocumentOpen` |
| Word·Publisher | 열 때 | `Document_Open` |
| Word | 닫을 때 | `AutoExit`, `AutoClose`, `Document_Close`, `DocumentBeforeClose` |
| Word | 새 문서 | `AutoNew`, `Document_New`, `NewDocument` |
| Word | 내용이 바뀔 때 | `DocumentChange` |
| Excel | 열 때 | `Auto_Open`, `Workbook_Open`, `Workbook_Activate` |
| Excel | 닫을 때 | `Auto_Close`, `Workbook_Close`, `Workbook_BeforeClose` |
| Excel | 시트를 계산할 때 | `Worksheet_Calculate` |
| ActiveX 컨트롤 | 컨트롤 이벤트 | `…_Click`, `…_Change`, `…_GotFocus`, `…_Painted` 등 |

### olevba 가 찾는 것과 표시 (참고 1)

- 자동 실행 매크로(`AutoOpen`, `Auto_Open`, `Workbook_Open` 등)를 찾습니다.
- 의심 키워드(`Shell`, `URLDownloadToFileA`, `Lib`, `Environ` 등)를 찾습니다.
- 침해 지표 (IOC) 로 URL·IP 주소·메일 주소·실행 파일 이름을 찾습니다.
- 난독화 흔적으로 Hex·Base64·StrReverse·Dridex 문자열과 VBA 식을 찾습니다.
- 형식 표시는 `OLE`, `OpX`(OpenXML), `XML`(Word 2003 XML), `MHT` 입니다.
- 플래그는 `M`(매크로), `A`(자동 실행), `S`(의심 키워드), `I`(IOC), `H`·`B`·`D`·`V`(Hex·Base64·Dridex·VBA 문자열) 입니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 파일 안에 VBA 프로젝트와 모듈이 있습니다 | 매크로가 실행됐는지 |
| 자동 실행 이름의 프로시저가 있습니다 | 사용자가 매크로를 켰는지 |
| 모듈 소스와 P-code 에 적힌 코드 | 코드가 악성인지. 정상 파일도 플래그를 받습니다(관찰) |
| olevba 가 소스와 P-code 가 다르다고 판정했습니다 | 누가 일부러 소스를 바꿨는지. 정상 파일도 이 판정을 받았습니다(관찰) |
| 서명 파트가 있습니다 | 서명이 유효한지, 게시자를 신뢰했는지 |
| 프로젝트 이름, 모듈 이름, 코드 페이지 | 누가, 언제 코드를 썼는지 |

### 보고서 문장

아래 파일 이름은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "`invoice.xlsm` 의 `xl/vbaProject.bin` 에는 VBA 모듈 두 개가 있습니다. 그 가운데 `ThisWorkbook` 모듈에 `Workbook_Open` 프로시저가 있습니다. 이 파일에는 `Zone.Identifier` 스트림이 있고 ZoneId 는 3 입니다."
- 쓰면 안 되는 문장: "사용자가 invoice.xlsm 을 열어 악성 매크로를 실행했다."

## 시각 해석

- 이 페이지에서 살펴본 VBA 스트림(`PROJECT`, `dir`, 모듈 스트림)에서는 코드를 쓴 시각이나 실행한 시각을 담은 칸을 찾지 못했습니다(관찰).
- OpenXML 파일의 ZIP 항목 시각은 관찰한 파일에서 모두 1980-01-01 00:00:00 이었습니다(관찰). 이 값으로 작성 시각을 말하지 않습니다.
- OLE 저장소 디렉터리 항목의 시각은 [OLE 복합 파일](/01-foundations/shell-document-formats/compound-file-binary.md) 에서 다룹니다.
- 문서를 만든 시각·저장한 시각은 [오피스 문서 속성 (OOXML docProps)](/02-artifacts/embedded-metadata/document-metadata/ooxml-docprops.md) 과 [옛 오피스 문서 속성 (OLE SummaryInformation)](/02-artifacts/embedded-metadata/document-metadata/ole-summaryinformation.md) 에서 봅니다.
- 매크로를 켠 기록은 [신뢰 문서 기록 (Trust Records)](/02-artifacts/file-folder-usage/microsoft-office/trust-records.md) 에서 봅니다. 그 값의 시각이 무엇을 뜻하는지도 그 페이지에서 다룹니다.
- 사건 시점이 위 차단 표의 적용 시작보다 앞이면, 사용자가 예전 배너의 [콘텐츠 사용] 단추를 누를 수 있었습니다(참고 2).

## 함정과 한계

1. **olevba 플래그만으로 악성이라고 씁니다.** Microsoft 365 설치본의 추가 기능 두 개가 모두 `MASIHB` 플래그를 받았습니다(관찰). `SOLVER.XLAM` 은 `OpX:MASIHB--`, `EXPTOOWS.XLA` 는 `OLE:MASIHB--` 였습니다.
2. **자동 실행 판정을 그대로 믿습니다.** `EXPTOOWS.XLA` 에서는 `btnCancel_Click`, `cmbListRanges_Change` 가 자동 실행으로 잡혔습니다(관찰). ActiveX 이벤트 이름 규칙에 걸린 것입니다.
3. **의심 키워드 목록을 결론으로 씁니다.** 같은 파일에서 `Open`, `run`, `create`, `Call`, `Windows`, `Lib`, `Chr`, `System`, Hex 문자열, Base64 문자열이 의심 키워드로 잡혔습니다. IOC 로는 `ExpToOWS.dll` 이 잡혔습니다(관찰). 코드를 직접 읽어 확인합니다.
4. **스톰핑 판정을 악성의 증거로 씁니다.** olevba 0.60.2 는 P-code 의 키워드와 소스의 키워드를 비교해 VBA 스톰핑 (VBA Stomping) 을 판정합니다(oletools 소스). 판정 문구는 "VBA Stomping was detected: the VBA source code and P-code are different, this may have been used to hide malicious code" 입니다(관찰). 정상 파일인 `EXPTOOWS.XLA` 도 이 판정을 받았습니다(관찰).
5. **OpenXML 파일에서 스톰핑 판정이 없으면 안심합니다.** ZIP 안의 `vbaProject.bin` 에 대해서는 "For now, VBA stomping cannot be detected for files in memory" 라는 경고만 내고 판정하지 않았습니다(관찰). `vbaProject.bin` 을 파일로 꺼내 다시 검사하면 판정하는지는 확인하지 않았습니다.
6. **소스만 읽습니다.** 모듈 스트림에는 소스 앞에 P-code 영역이 있습니다(관찰). Office 가 어떤 조건에서 소스 대신 P-code 를 실행하는지는 확인하지 못했습니다.
7. **웹 표시가 없으면 안에서 만든 파일이라고 봅니다.** 웹 표시는 NTFS 에 저장한 파일에만 붙고 FAT32 에는 붙지 않습니다(참고 2). 기본으로는 인터넷·제한된 사이트 영역에서 온 파일에만 붙습니다(참고 2). OneDrive·SharePoint 에서 [데스크톱 앱에서 열기] 로 연 파일, OneDrive 동기화 클라이언트가 내려받은 파일, OneDrive 와 동기화되는 알려진 폴더(바탕 화면·문서·사진·스크린샷·카메라 롤)의 파일에도 붙지 않습니다(참고 2).
8. **ZoneId 가 있으면 모두 막혔다고 봅니다.** ZoneId 2(신뢰할 수 있는 사이트)는 기본으로 막지 않고, 3(인터넷)은 막습니다(참고 2). ZoneId 값 전체는 [다운로드 출처 표시 (Zone.Identifier)](/02-artifacts/filesystem/zone-identifier.md) 에서 다룹니다.
9. **신뢰할 수 있는 위치의 파일을 같은 기준으로 봅니다.** 신뢰할 수 있는 위치에 저장한 파일은 웹 표시 검사를 건너뜁니다(참고 2).
10. **네트워크 공유 파일을 로컬 파일처럼 봅니다.** IP 주소로 연 공유의 파일은, 그 공유가 신뢰할 수 있는 사이트나 로컬 인트라넷 영역에 없으면 매크로가 막힙니다(참고 2).
11. **Excel 추가 기능을 문서와 같게 봅니다.** `.xla`·`.xlam` 은 웹 표시가 있으면 서명이나 게시자 신뢰로도 풀리지 않습니다. 2016년 MS16-088 이후 그렇습니다(참고 2).
12. **압축 파일·디스크 이미지 안에서 꺼낸 파일에도 웹 표시가 있다고 봅니다.** ISO·ZIP·7z 같은 컨테이너가 웹 표시를 안쪽 파일로 넘기는지는 참고 2 에 없습니다. 이 페이지에서도 확인하지 못했습니다.

### 지우기와 조작

- 사용자는 파일 속성 > 일반 탭의 [차단 해제] (Unblock) 로 웹 표시를 지울 수 있습니다. PowerShell `Unblock-File` 도 같습니다. 둘 다 ZoneId 값을 지웁니다(참고 2). 지운 흔적을 찾는 법은 [다운로드 출처 표시 (Zone.Identifier)](/02-artifacts/filesystem/zone-identifier.md) 에서 다룹니다.
- 신뢰할 수 있는 위치로 옮긴 파일은 웹 표시 검사를 건너뜁니다(참고 2). 파일 경로가 신뢰할 수 있는 위치 안인지 확인합니다.
- 소스와 P-code 가 다르면 소스만 읽는 도구로는 실제 코드를 놓칠 수 있습니다. olevba 판정 문구도 이 가능성을 적었습니다(관찰). P-code 를 함께 읽습니다.
- 일부러 흔적을 지운 정황은 [증거를 없애려 했나](/04-scenarios/activity/anti-forensics/index.md) 에서 다른 흔적과 함께 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

1. OpenXML 파일이면 ZIP 을 풀어 `vbaProject.bin` 을 꺼냅니다. Excel 파일에서는 `xl/vbaProject.bin` 이었습니다(관찰).
2. 첫 8바이트가 `D0 CF 11 E0 A1 B1 1A E1` 인지 봅니다(관찰). 97-2003 파일이면 파일 전체가 이 형식입니다.
3. OLE 저장소를 따라가 `PROJECT` 스트림을 읽습니다. 글자로 된 줄이므로 헥스 편집기의 글자 칸에서 바로 읽힙니다.
4. `VBA\dir` 스트림의 첫 바이트가 `01` 인지 봅니다. 압축돼 있으므로 도구로 풉니다.
5. 푼 `dir` 에서 레코드를 차례로 읽습니다. 아래는 레코드 구조에 맞춰 만든 예시입니다. 실제 검체에서 뽑은 값이 아니고, 숫자는 리틀 엔디언으로 적었습니다.

```
04 00 | 06 00 00 00 | 53 6F 6C 76 65 72
번호    크기           값
0x0004  6바이트        "Solver" (프로젝트 이름)
```

6. 모듈마다 0x0019(모듈 이름)와 0x0031(MODULEOFFSET) 레코드를 찾습니다.
7. 모듈 스트림을 열어 MODULEOFFSET 위치로 갑니다. 그 바이트가 `01` 인지 봅니다.
8. 그 위치부터 도구로 풀어 `Attribute VB_Name = "<모듈 이름>"` 으로 시작하는지 확인합니다.
9. MODULEOFFSET 앞쪽은 P-code 영역입니다. 소스와 따로 풀어 비교합니다.

### 공개 도구로 한 번

oletools 의 olevba 를 예로 듭니다(참고 1).

- `olevba -t <파일>` 은 한 줄 요약을 보여 줍니다. 형식과 플래그가 `OpX:MASIHB--` 같은 모양으로 나옵니다(관찰).
- `olevba -a <파일>` 은 자동 실행 이름, 의심 키워드, IOC, 스톰핑 판정을 항목별로 보여 줍니다(관찰).
- P-code 는 pcodedmp 로 읽습니다(oletools 소스).
- 모든 작업은 사본에서 합니다. 판정은 코드를 직접 읽어 확인한 뒤에 씁니다.
- 실행 중인 시스템에서는 `notepad <파일>:Zone.Identifier` 로 웹 표시를 열어 `[ZoneTransfer]` 절의 ZoneId 를 볼 수 있습니다(참고 2). 이미지에서 읽는 법은 [다운로드 출처 표시 (Zone.Identifier)](/02-artifacts/filesystem/zone-identifier.md) 를 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [다운로드 출처 표시 (Zone.Identifier)](/02-artifacts/filesystem/zone-identifier.md) | 파일에 웹 표시가 있는지, ZoneId 가 몇인지 |
| [신뢰 문서 기록 (Trust Records)](/02-artifacts/file-folder-usage/microsoft-office/trust-records.md) | 사용자가 경고 단추를 눌렀는지, 매크로를 켰는지 |
| [오피스 사용 흔적](/02-artifacts/file-folder-usage/microsoft-office/index.md) | 문서를 연 기록 |
| [오피스 문서 속성 (OOXML docProps)](/02-artifacts/embedded-metadata/document-metadata/ooxml-docprops.md) · [옛 오피스 문서 속성 (OLE SummaryInformation)](/02-artifacts/embedded-metadata/document-metadata/ole-summaryinformation.md) | 같은 문서의 작성자·저장 시각 |
| [아웃룩](/02-artifacts/mail/outlook/index.md) | 문서가 메일 첨부로 들어왔는지 |
| [프로세스 생성 (이벤트 1)](/02-artifacts/event-logs/sysmon/1.md) | 문서를 연 시각 뒤로 오피스 프로세스가 다른 프로세스를 만들었는지 |
| [의심 실행 파일 선별](/03-techniques/analysis/code-signing-yara.md) | 여러 문서를 규칙으로 한꺼번에 선별하기 |

악성 문서가 들어온 경로를 좇는 순서는 [악성코드는 어디서 들어왔나](/04-scenarios/incident/initial-access.md) 에서 다룹니다. 파일의 출처를 좁히는 순서는 [이 파일은 어디서 왔나](/04-scenarios/activity/file-origin.md) 를 봅니다.

## 실습

**직접 만든 Windows 10·11 가상 머신**에서 해 봅니다. 매크로는 메시지 상자만 띄우는 무해한 코드로 직접 만듭니다.

1. `Workbook_Open` 에 메시지 상자 한 줄을 넣은 `.xlsm` 을 만들어 olevba `-t` 와 `-a` 로 검사해 보십시오. 어떤 플래그가 나옵니까?
2. 같은 파일을 웹 서버에 올렸다가 브라우저로 내려받아 여십시오. 어떤 배너가 나옵니까? ZoneId 는 몇입니까?
3. 파일 속성에서 [차단 해제] 를 누른 뒤 다시 여십시오. 배너가 어떻게 바뀝니까? `Zone.Identifier` 스트림은 남아 있습니까?
4. [콘텐츠 사용] 을 누른 뒤 `TrustRecords` 키에 어떤 값이 생겼는지 보십시오.
5. `vbaProject.bin` 을 꺼내 모듈 스트림의 MODULEOFFSET 위치 바이트를 헥스로 확인해 보십시오.

**NIST CFReDS 같은 공개 검체의 Windows 디스크 이미지**로도 풀어 봅니다.

1. 사용자 폴더에서 `.docm`·`.xlsm`·`.doc`·`.xls` 파일을 찾아 매크로가 든 파일을 가려내 보십시오. 몇 개입니까?
2. 매크로가 든 파일에 자동 실행 이름이 있습니까? 그 파일에 웹 표시가 있습니까?
3. 같은 파일 경로가 `TrustRecords` 에 있습니까? 없다면 매크로가 실행됐는지 어떤 기록으로 더 확인할 수 있을지 적어 보십시오.

## 참고 문헌

1. oletools wiki, "olevba" — https://github.com/decalage2/oletools/wiki/olevba
2. Microsoft Learn, "Macros from the internet are blocked by default in Office" — https://learn.microsoft.com/en-us/microsoft-365-apps/security/internet-macros-blocked
