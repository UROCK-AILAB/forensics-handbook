---
title: "압축 프로그램 사용 기록"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1410
---

# 압축 프로그램 사용 기록 (7-Zip·WinRAR·Bandizip)

7-Zip 과 WinRAR 는 사용자 레지스트리(HKCU) 아래에 압축 파일 이름과 풀기 경로의 기록을 남깁니다. 7-Zip 은 압축 옵션과 파일 관리자 창에서 본 폴더도 남깁니다. 기록 한 줄마다 시각이 붙지 않으므로, 때는 키의 마지막 기록 시각과 다른 흔적으로 좁힙니다. Bandizip 이 이런 기록을 어디에 두는지는 실제 데이터로 확인합니다.

7-Zip 파일 관리자 값과 WinRAR 값의 공개 설명은 대략적인 메모 수준이므로[3][4], 실제 하이브로 한 번 더 확인합니다.

## 무엇을 기록하나 · 왜 생기나

7-Zip 은 사용자 설정을 `HKEY_CURRENT_USER\Software\7-Zip\` 아래 하위 키에 씁니다. HKEY_CURRENT_USER 에서 `Software\7-Zip\` 뒤에 키 이름을 붙여 키를 엽니다[1]. 이 설정에는 압축 창·풀기 창의 옵션과 함께 경로 기록도 들어갑니다.

WinRAR 도 `HKEY_CURRENT_USER\Software\WinRAR\` 아래에 압축 파일 이름과 경로로 보이는 기록을 남깁니다[4].

두 프로그램이 남기는 것을 모으면 이렇습니다.

- 만든 압축 파일의 경로 (7-Zip ArcHistory)
- 압축을 푼 대상 폴더 (7-Zip PathHistory, WinRAR ExtrPath)
- 압축 형식·수준·암호화 옵션 (7-Zip)
- 7-Zip 파일 관리자 창에서 본 폴더 (7-Zip FolderHistory·PanelPath#)
- 연 압축 파일과 압축 창에 넣은 이름 (WinRAR ArcHistory·ArcName)

HKCU 는 로그온한 사용자의 NTUSER.DAT 라서 어느 계정의 기록인지 알 수 있습니다. 하이브 파일은 [하이브 파일 종류와 위치](../../01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md) 에서 다룹니다.

자료를 빼돌리기 전에 모아서 압축하는 일이 많아서 이 기록은 유출 조사에서 자주 봅니다. 조사 흐름은 [퇴사 전 자료를 모으고 압축했나](../../04-scenarios/exfiltration/data-exfiltration/staging.md) 에서 다룹니다.

## 위치와 버전별 차이

| 프로그램 | 위치 | 참고 문헌 |
|---|---|---|
| 7-Zip | `HKCU\Software\7-Zip\` 아래 `Compression`·`Extraction`·`Options`·`FM` 하위 키와 `Lang` 값 | [1][3] |
| WinRAR | `HKCU\Software\WinRAR\ArcHistory`, `HKCU\Software\WinRAR\DialogEditHistory\ArcName`, `HKCU\Software\WinRAR\DialogEditHistory\ExtrPath` | [4] |
| Bandizip | 실제 데이터와 재현 시험으로 확인 | — |

- 이 기록은 Windows 가 아니라 각 프로그램이 쓰므로 Windows 버전보다 프로그램 버전에 따라 달라질 수 있습니다.
- 7-Zip 값은 공식 저장소의 현재 소스 코드 기준입니다[1]. 값마다 어느 7-Zip 버전에서 들어왔는지는 공식 저장소의 변경 이력으로 확인합니다.
- WinRAR 값이 버전마다 어떻게 다른지는 설치된 버전을 확인한 뒤 실제 하이브에서 봅니다.

### Bandizip

Bandizip 은 제작사가 변경 기록 페이지를 공개합니다[5].

- 변경 기록은 0.0.1(2009-04-06)부터 v7.46(2026-08-21)까지 있습니다.
- 변경 기록에는 기록(history)·최근 목록·레지스트리·ini 의 저장 위치를 밝힌 항목이 드러나 있지 않습니다.
- v6.15(2018-09-19)에 "Zone.Identifier 정보를 복사해 시스템 보안 강화" 라는 항목이 있습니다. 인터넷에서 받은 압축 파일을 풀 때 다운로드 표시를 풀린 파일에 옮기는 기능으로 읽힙니다.
- 명령줄 기능도 여러 번 바뀌었습니다. 예를 들어 v7.17(2021-06-16)에 `-date` 스위치가, v7.26(2022-07-05)에 `/cmdfile` 명령이 추가됐습니다.

Bandizip 이 설치된 분석 대상이라면 사용자 하이브와 프로그램 폴더를 직접 뒤져 기록 위치를 찾습니다. 찾은 위치는 가상 머신에서 같은 버전으로 재현해 확인한 뒤 씁니다.

## 구조

### 7-Zip — Compression 키

`HKCU\Software\7-Zip\Compression` 에는 압축 창의 설정이 들어갑니다[1].

| 값 | 뜻 |
|---|---|
| ArcHistory | 만든 압축 파일의 경로 기록 |
| Archiver | 압축 형식 |
| Level | 압축 수준 |
| ShowPassword | 암호 보이기 설정 |
| EncryptHeaders | 헤더 암호화 설정 |
| Security, AltStreams, HardLinks, SymLinks, PreserveATime | 보안 정보·대체 데이터 스트림·링크·접근 시각을 다루는 설정. 정해 두지 않았으면 값을 지웁니다 |

`Compression\Options\<형식 ID>` 하위 키에는 형식별 압축 옵션이 들어갑니다. 값 이름은 Method, Options, EncryptionMethod, MemUse, Level, Dictionary, Order, BlockSize, NumThreads, TimePrec, MTime, ATime 등입니다[1].

압축 설정을 저장하는 함수는 이렇게 씁니다[1].

1. Level·Archiver·ShowPassword·EncryptHeaders 를 씁니다.
2. ArcHistory 값에 목록 전체를 새로 씁니다. 한 줄을 덧붙이지 않고 값을 통째로 바꿉니다.
3. `Options` 하위 키를 지우고 다시 만듭니다.

이 함수가 어느 때 불리는지(예: 압축 창에서 확인을 누를 때)는 재현 시험으로 확인합니다.

### 7-Zip — Extraction 키

`HKCU\Software\7-Zip\Extraction` 에는 풀기 창의 설정이 들어갑니다[1].

| 값 | 뜻 |
|---|---|
| PathHistory | 풀기 대상 폴더의 기록 |
| ExtractMode | 풀기 방식 |
| OverwriteMode | 덮어쓰기 방식 |
| ShowPassword | 암호 보이기 설정 |
| SplitDest | 대상 폴더 나누기 설정 |
| ElimDup | 겹치는 폴더 줄이기 설정 |
| Security | 보안 정보 설정 |

PathHistory 도 목록 전체를 한 값에 새로 씁니다[1].

### 7-Zip — Options 키

`HKCU\Software\7-Zip\Options` 에는 프로그램 옵션이 들어갑니다[1].

| 값 | 뜻 |
|---|---|
| WorkDirType, WorkDirPath, TempRemovableOnly | 작업 폴더 설정 |
| CascadedMenu, MenuIcons, ContextMenu | 탐색기 오른쪽 메뉴 설정 |
| ElimDupExtract | 풀 때 겹치는 폴더 줄이기 |
| WriteZoneIdExtract | 이름으로 보면 풀 때 Zone.Identifier 를 쓸지 정하는 설정 |

WriteZoneIdExtract 의 값(0·1·2 등)이 무엇을 뜻하는지는 시험 PC 에서 설정을 바꿔 가며 확인합니다. 기본값은 -1(설정 안 됨)입니다[1].

### 7-Zip — 문자열 목록 값

ArcHistory 와 PathHistory 는 한 값에 문자열 목록을 담는 함수(`SetValue_Strings`)로 씁니다. 이 함수는 UTF-16LE 문자열마다 끝에 `00 00` 을 붙여 이어 붙이고, REG_BINARY 로 씁니다. 목록 끝에 따로 붙는 표시는 없습니다[1][2]. 아래 두 가지는 이 저장 방식만으로는 알 수 없습니다.

- 목록 순서(최근 것이 앞인지)
- 최대 개수

그래서 "목록 첫 줄이 가장 최근" 이라고 쓰지 않습니다.

### 7-Zip — 파일 관리자(7zFM) 키

7-Zip 파일 관리자는 `HKCU\Software\7-Zip` 에 `Lang` 값과 `FM` 하위 키를 씁니다. `Lang` 은 언어 태그입니다(예: `en-US`). 비었으면 `-` 입니다[3].

| `FM` 아래 값·하위 키 | 뜻 |
|---|---|
| FolderHistory | 폴더 기록. UTF-16LE 문자열 목록이고 문자열마다 끝 문자가 붙습니다 |
| PanelPath# | 패널이 마지막으로 보던 경로. `#` 은 0·1 같은 숫자입니다. UTF-16LE 문자열입니다 |
| FlatViewArc# | 패널별 설정 |
| FolderShortcuts | 폴더 바로가기 |
| ListMode, Panels, Position | 창 배치 설정 |
| Columns 하위 키 | 형식별 열 설정(REG_BINARY) |

7-Zip 파일 관리자 창 안에서 옮겨 다닌 폴더는 FolderHistory 와 PanelPath# 에서 찾습니다. 압축 파일 속 경로가 이 값에 어떤 모양으로 남는지는 재현 시험으로 확인합니다. 값마다 자료형은 실제 하이브에서 확인합니다[3].

### WinRAR

| 키 | 이름으로 본 뜻 |
|---|---|
| `HKCU\Software\WinRAR\ArcHistory` | 연 압축 파일 기록 |
| `HKCU\Software\WinRAR\DialogEditHistory\ArcName` | 압축 창에 넣은 압축 파일 이름 |
| `HKCU\Software\WinRAR\DialogEditHistory\ExtrPath` | 풀기 대상 경로 |

- 값 이름은 숫자입니다. 자료형은 REG_SZ 입니다[4].
- 위 표의 뜻은 키 이름으로 짐작한 것입니다.
- 값 번호의 순서(0 이 최근인지)는 재현 시험으로 확인합니다.

## 증거로서 의미

### 증명하는 것

- **압축 파일 경로.** 7-Zip ArcHistory 의 경로는 그 계정의 7-Zip 이 압축 파일 경로로 기록한 이름입니다.
- **풀기 대상 폴더.** 7-Zip PathHistory 의 폴더는 그 계정의 7-Zip 이 풀기 대상으로 기록한 폴더입니다.
- **압축 옵션.** EncryptHeaders·EncryptionMethod 같은 값은 마지막으로 저장한 압축 설정을 알려 줍니다. 암호화 옵션을 쓴 적이 있는지 보는 단서입니다.
- **파일 관리자에서 본 폴더.** FolderHistory·PanelPath# 는 7-Zip 파일 관리자 창에서 본 폴더를 알려 줍니다.
- **WinRAR 기록.** 압축 파일 이름과 풀기 경로로 보이는 경로가 남습니다. 뜻은 키 이름으로 짐작한 것이므로 보고서에도 그렇게 적습니다.
- **계정.** 사용자 하이브의 기록이므로 어느 계정에서 썼는지 알려 줍니다.

### 증명하지 못하는 것

- **압축을 끝냈다는 것.** 설정을 저장한 때와 압축을 마친 때가 같다고 볼 수 없습니다. 기록에 경로가 있어도 압축 파일이 실제로 만들어졌는지는 파일 시스템에서 따로 봅니다.
- **압축 파일 속 내용.** 기록에는 압축 파일 경로만 있습니다. 무엇을 넣었는지는 압축 파일이나 다른 흔적에서 봅니다.
- **기록 한 줄마다의 시각.** 값에는 시각이 없습니다.
- **밖으로 보냈다는 것.** 압축 기록은 전송 기록이 아닙니다.
- **누가 조작했는지.** 계정까지만 알려 줍니다.
- **압축하지 않았다는 것.** 기록이 없어도 압축했을 수 있습니다. 다른 압축 프로그램을 썼거나, Windows 기본 명령줄 도구 `tar.exe` 로 압축했거나, 기록을 지웠을 수 있습니다.

보고서에는 "피의자가 기밀 폴더를 압축했다" 가 아니라 이렇게 씁니다. "B 계정의 NTUSER.DAT 에서 7-Zip 압축 기록(ArcHistory)에 `D:\out\p.7z` 가 있다. Compression 키의 마지막 기록 시각은 T 이다. 이는 이 계정의 7-Zip 압축 설정이 T 에 마지막으로 저장됐고, 그때 기록에 이 경로가 있었다는 뜻이다." 경로는 설명을 위한 예입니다.

## 시각 해석

- **값에는 시각이 없습니다.** ArcHistory·PathHistory 는 문자열 목록만 담습니다[1].
- **키의 마지막 기록 시각을 씁니다.** 레지스트리 키마다 마지막 기록 시각이 있습니다. 읽는 법은 [키 마지막 기록 시각](../../01-foundations/database-log-formats/registry-hive/last-write-time.md) 에서 다룹니다.
- **7-Zip Compression 키.** 저장할 때마다 ArcHistory 전체를 다시 쓰고 `Options` 하위 키도 다시 만듭니다. 그래서 이 키의 마지막 기록 시각은 "압축 설정을 마지막으로 저장한 때" 입니다. 목록 속 특정 경로를 기록한 때가 아닙니다. 이 해석은 소스 코드에서 끌어낸 것입니다.
- **7-Zip Extraction 키.** PathHistory 도 전체를 다시 씁니다. 같은 방식으로 읽습니다. 저장 함수가 어느 때 불리는지는 재현 시험으로 확인합니다.
- **WinRAR 키.** 키 안의 값 하나가 바뀌면 키의 마지막 기록 시각도 바뀝니다. 어느 값이 그때 바뀌었는지는 시각만으로 알 수 없습니다.
- **7-Zip FM 키.** PanelPath# 같은 값을 언제 쓰는지는 재현 시험으로 확인합니다. FM 키의 시각을 "그 폴더를 본 시각" 이라고 쓰지 않습니다.

## 함정과 한계

- **7-Zip 파일 관리자와 WinRAR 값의 공개 설명은 대략적인 메모입니다[3][4].** 이 값들은 실제 하이브로 확인한 뒤 씁니다.
- **목록 순서를 짐작하지 않습니다.** 7-Zip 목록과 WinRAR 값 번호를 두고 "가장 최근에 만든 압축 파일" 같은 말은 재현 시험으로 확인한 뒤에만 씁니다.
- **숫자 값은 원시 바이트로 확인합니다.** 하이브의 REG_DWORD 를 문자열로 받는 도구는 부호 없는 10진수로 보여 줍니다. -1 같은 값이 큰 수로 보일 수 있습니다.
- **프리페치와 겹치는 해석은 그 페이지를 따릅니다.** 압축 도구는 시작하자마자 대상 파일과 폴더를 읽습니다. 그래서 7-Zip 의 .pf 참조 목록에 대상 이름이 남을 수 있습니다. 쓸 문장과 쓰지 않을 문장은 [참조 파일·폴더 목록 활용](../execution/prefetch/referenced-files.md) 에서 다룹니다.
- **탐색기로 연 ZIP 은 여기에 남지 않습니다.** 탐색기 안에서 ZIP 속 폴더를 연 흔적은 셸백에 남습니다. [외부 장치·네트워크·압축 폴더 탐색 흔적](shellbags/removable-network-zip.md) 에서 다룹니다.
- **Zone.Identifier 를 옮겨 적을 수 있습니다.** 7-Zip 에는 WriteZoneIdExtract 설정이 있습니다. Bandizip 은 v6.15 부터 Zone.Identifier 정보를 복사합니다[5]. 풀린 파일의 Zone.Identifier 는 그 파일을 직접 내려받았다는 뜻이 아닐 수 있습니다. 압축 파일에서 옮겨 적었을 수 있습니다. [다운로드 출처 표시](../filesystem/zone-identifier.md) 와 함께 봅니다.
- **지운 기록.** 사용자가 키나 값을 지울 수 있습니다. 지운 키·값을 되살리는 방법은 [지워진 키·값 복구](../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md) 와 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에서 다룹니다.
- **Bandizip 기록은 실제 데이터로 찾습니다.** Bandizip 기록이 보이지 않는다고 Bandizip 을 쓰지 않았다고 말할 수 없습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 7-Zip FolderHistory 의 형식 설명[3]을 따라 만든 예시입니다. 실제 데이터에서 나온 값이 아닙니다. 두 폴더 `C:\a` 와 `D:\b` 가 기록됐다고 가정했습니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00   43 00 3A 00 5C 00 61 00 00 00 44 00 3A 00 5C 00
0x10   62 00 00 00
```

1. 두 바이트씩 UTF-16LE 글자로 읽습니다. `43 00` 은 `C`, `3A 00` 은 `:`, `5C 00` 은 `\` 입니다.
2. 0x08 의 `00 00` 은 끝 문자입니다. 첫 문자열 `C:\a` 가 여기서 끝납니다.
3. 0x0A 부터 둘째 문자열 `D:\b` 가 이어지고 0x12 의 `00 00` 에서 끝납니다.
4. 목록 끝에 무엇이 더 붙는지는 실제 값의 원시 바이트로 확인합니다.
5. 두 경로 가운데 어느 쪽이 최근인지는 이 바이트만으로 판단하지 않습니다.

ArcHistory·PathHistory 도 같은 모양입니다. REG_BINARY 값에 끝 문자가 붙은 UTF-16LE 문자열을 이어 붙입니다[2]. 실제 하이브에서는 원시 바이트로 한 번 더 확인합니다. 키의 마지막 기록 시각은 하이브의 키 레코드에 있습니다. 위치는 [하이브 내부 구조](../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md) 에서 다룹니다.

### 공개 도구로 한 번

사용자의 NTUSER.DAT 를 복사해 공개 하이브 뷰어(예: Registry Explorer, RegRipper)로 엽니다. `Software\7-Zip`·`Software\WinRAR` 아래 키와 값을 봅니다. 키마다 마지막 기록 시각을 적습니다. 문자열 목록 값은 헥스 보기로도 확인합니다.

값 이름의 뜻은 7-Zip 소스 코드의 `ZipRegistry.cpp` 와 맞춰 봅니다. 도구가 보여 준 목록 개수와 원시 바이트의 문자열 개수가 같은지 봅니다. 차이가 나면 헥스로 돌아갑니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 점 |
|---|---|
| [프리페치 (Prefetch)](../execution/prefetch/index.md) | 압축 프로그램의 실행 흔적과 시작 직후 읽은 파일·폴더를 봅니다 |
| [UserAssist](../execution/userassist.md) | 탐색기에서 압축 프로그램을 실행한 기록을 봅니다 |
| [BAM·DAM](../execution/background-activity-moderator.md) | 압축 프로그램 실행 파일의 마지막 실행 시각을 봅니다 |
| [바로가기 파일 (LNK)](lnk.md) | 기록된 압축 파일을 연 흔적이 있는지 봅니다 |
| [점프리스트 (Jump Lists)](jump-lists.md) | 압축 프로그램으로 연 파일 목록을 봅니다 |
| [최근 문서 (RecentDocs)](recentdocs.md) | 압축 파일 확장자의 최근 문서를 봅니다 |
| [열기·저장 대화상자 기록](comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) | 대화상자에서 고른 압축 파일·폴더가 남았는지 봅니다 |
| [외부 장치·네트워크·압축 폴더 탐색 흔적](shellbags/removable-network-zip.md) | 탐색기 안에서 ZIP 속 폴더를 연 흔적을 봅니다 |
| [다운로드 출처 표시 (Zone.Identifier)](../filesystem/zone-identifier.md) | 풀린 파일에 Zone.Identifier 가 옮겨졌는지 봅니다 |
| [USN 변경 저널 ($UsnJrnl)](../filesystem/usnjrnl.md) | 기록된 경로에 압축 파일이 만들어지거나 지워진 기록을 봅니다 |
| [프로세스 생성 (4688)](../event-logs/4688.md) | 명령줄 압축 도구를 실행한 기록을 봅니다 |

유출 조사 전체 흐름은 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에서 다룹니다.

## 실습

공개 실습 이미지에 압축 프로그램이 설치돼 있는지 먼저 확인합니다. 없으면 Windows 가상 머신에 7-Zip 과 WinRAR 를 설치해 직접 시험합니다. 시험 전에 프로그램 버전을 적어 둡니다.

1. 7-Zip 으로 폴더 하나를 압축하되 헤더 암호화를 켭니다. `Compression` 키와 `Options` 하위 키에 어떤 값이 생겼습니까?
2. 압축 창을 열었다가 취소합니다. ArcHistory 와 키의 마지막 기록 시각이 바뀌었습니까?
3. 이름을 바꿔 가며 여러 번 압축합니다. ArcHistory 에서 최근 경로는 앞에 옵니까, 뒤에 옵니까? 몇 개까지 남습니까?
4. 압축 창의 확인 단추로 풀 때와 탐색기 오른쪽 메뉴로 풀 때를 나눠 시험합니다. PathHistory 는 각각 바뀝니까?
5. 7-Zip 파일 관리자로 압축 파일 속 폴더를 엽니다. FolderHistory·PanelPath# 에 어떤 모양의 경로가 남습니까?
6. 인터넷에서 받은 압축 파일을 7-Zip 과 WinRAR 로 각각 풉니다. 풀린 파일에 Zone.Identifier 가 붙었습니까?
7. WinRAR 로 압축하고 풉니다. ArcHistory·ArcName·ExtrPath 의 값 번호는 어떤 순서로 쌓입니까?
8. 같은 시험의 프리페치 참조 목록과 레지스트리 기록을 맞춰 봅니다.

## 참고 문헌

- Igor Pavlov, 7-Zip 공식 소스 `CPP/7zip/UI/Common/ZipRegistry.cpp` — https://raw.githubusercontent.com/ip7z/7zip/main/CPP/7zip/UI/Common/ZipRegistry.cpp
- Igor Pavlov, 7-Zip 공식 소스 `CPP/Windows/Registry.cpp` (`SetValue_Strings`) — https://raw.githubusercontent.com/ip7z/7zip/main/CPP/Windows/Registry.cpp
- libyal, winreg-kb "7-Zip" (application keys) — https://raw.githubusercontent.com/libyal/winreg-kb/main/docs/sources/application-keys/7-Zip.md
- libyal, winreg-kb "WinRAR" (application keys) — https://raw.githubusercontent.com/libyal/winreg-kb/main/docs/sources/application-keys/WinRAR.md
- Bandisoft, Bandizip Version History — https://en.bandisoft.com/bandizip/history/
