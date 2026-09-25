---
title: "MUICache"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 1040
---

# MUICache (MUICache)

## 한 줄 요약

NirSoft 에 따르면 사용자가 새 프로그램을 쓰기 시작할 때 Windows 가 실행 파일의 버전 정보에서 앱 이름을 꺼내 `MuiCache` 키에 경로와 함께 남깁니다. Vista 이후 이 키는 `Software\Classes` 아래에 있습니다. Windows 11 PC 한 대에서 하이브 파일은 NTUSER.DAT 가 아니라 UsrClass.dat 였습니다.

## 무엇을 기록하나 · 왜 생기나

libyal 은 이 키를 다국어 사용자 인터페이스 캐시 (Multilingual User Interface (MUI) cache) 로 부릅니다. NirSoft 의 설명에 따르면 새 응용 프로그램을 쓰기 시작할 때마다 Windows 가 실행 파일의 버전 리소스에서 앱 이름을 꺼내 나중에 쓰려고 `MuiCache` 키에 저장합니다. 항목을 지워도 그 프로그램을 다시 실행하면 항목이 다시 생긴다고 NirSoft 는 적습니다. 사용자 하이브에 있으므로 계정마다 따로 남습니다. 실행 파일의 버전 리소스는 [실행 파일 메타데이터](../embedded-metadata/pe-header-version-info-digital-signature.md) 에서 다룹니다.

## 위치와 버전별 차이

| Windows | 경로 | 하이브 파일 |
|---|---|---|
| XP·2003 | `HKCU\Software\Microsoft\Windows\ShellNoRoam\MUICache` | NTUSER.DAT |
| Vista 이후 | `HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache` | UsrClass.dat (Win11 25H2 한 대에서 확인) |

- 두 경로는 libyal 과 NirSoft 가 같게 적습니다.
- Windows 11 PC 한 대에서 같은 키가 `HKEY_USERS\<SID>_Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache` 로도 열렸습니다. 두 경로의 값 수(218)가 같았습니다.
- 같은 PC 의 하이브 목록에서 `<SID>_Classes` 의 파일은 `C:\Users\<user>\AppData\Local\Microsoft\Windows\UsrClass.dat` 였습니다. 오프라인에서는 UsrClass.dat 를 열고 `Local Settings\Software\Microsoft\Windows\Shell\MuiCache` 로 들어갑니다.
- 같은 PC 에는 XP 용 `ShellNoRoam\MUICache` 키가 없었습니다.

하이브 파일의 구조와 수집 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

## 구조

아래는 Windows 11 PC 한 대에서 본 값의 형태입니다.

```
MuiCache
    LangID                              REG_BINARY  12 04
    <전체 경로>.FriendlyAppName         REG_SZ      <앱 이름>
    <전체 경로>.ApplicationCompany      REG_SZ      <회사 이름>
```

- 값 이름은 실행 파일의 전체 경로 뒤에 `.FriendlyAppName` 이나 `.ApplicationCompany` 를 붙인 형태였습니다.
- 값 수는 `.FriendlyAppName` 120개, `.ApplicationCompany` 97개, `LangID` 하나였습니다.
- `.FriendlyAppName` 경로의 확장자는 .exe 116개, .dll 3개, .bat 1개였습니다.
- `LangID` 는 REG_BINARY `12 04` 였습니다. 리틀 엔디언으로 읽으면 0x0412 입니다. Microsoft 의 언어 ID 표 [MS-LCID] 에서 0x0412 는 한국어(ko-KR)입니다. 이 값이 앱 이름의 언어를 뜻하는지는 확인하지 못했습니다.
- 값마다 붙은 시각은 없습니다. 시간 정보는 키 전체의 마지막 기록 시각 하나뿐입니다.

### 앱 이름과 파일 버전 정보 비교

같은 PC 에서 `.FriendlyAppName` 을 파일의 버전 정보와 맞춰 보았습니다.

| 비교 | 결과 |
|---|---|
| 파일이 아직 있는 `.FriendlyAppName` 74개 | 49개는 파일의 FileDescription 과 같았습니다 |
| 같은 74개 가운데 | 16개는 달랐습니다. Windows 기본 프로그램에는 현지화된 한국어 이름이 들어 있었습니다(예: explorer.exe 는 'Windows 탐색기', 파일의 FileDescription 은 'Windows Explorer') |
| 같은 74개 가운데 | 9개는 파일의 FileDescription 이 비어 있었습니다. 이때는 확장자를 뺀 파일 이름이 들어 있었습니다 |
| `.ApplicationCompany` 62개 | 58개는 파일의 CompanyName 과 같았습니다 |
| `.FriendlyAppName` 120개 | 46개는 그 경로에 파일이 더는 없었습니다 |

## 증거로서 의미

### 증명하는 것

- 이 계정의 MuiCache 에 이 경로와 앱 이름이 있습니다. NirSoft 의 설명대로라면 이 계정으로 이 프로그램을 쓰기 시작한 적이 있습니다.
- 지금은 없는 프로그램도 경로와 이름이 남습니다. 지우거나 옮긴 프로그램의 흔적을 찾을 수 있습니다.
- 값 이름에 전체 경로가 들어 있으므로, 그때 프로그램이 어느 폴더에 있었는지 알 수 있습니다.

### 증명하지 못하는 것

- **언제 썼나.** 값마다 시각이 없습니다.
- **몇 번 썼나.** 횟수 칸이 없습니다.
- **실행했나, 보기만 했나.** 이 캐시가 실행의 증거인지, 탐색기에서 파일을 보기만 해도 생기는지는 이번에 연 자료로 확인하지 못했습니다. "실행했다" 고 쓰려면 다른 실행 흔적으로 받칩니다.
- **지금 그 경로의 파일이 그때와 같은 파일인가.** 경로와 이름만 남고 해시는 없습니다.
- **키보드 앞의 사람.** 하이브가 가리키는 것은 계정입니다. 사람을 좁히는 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.

보고서에는 "이 계정의 MuiCache 에 이 경로의 앱 이름 값이 있다" 처럼 씁니다. 시각을 붙여야 하면 다른 아티팩트의 시각을 근거와 함께 따로 적습니다.

## 시각 해석

값에는 시각이 없고 키의 마지막 기록 시각 (LastWrite) 이 하나 있을 뿐입니다. 이 시각은 키 안의 어떤 값이 마지막으로 바뀐 때를 말할 뿐, 어느 값인지는 말하지 않습니다. 값이 놓인 순서로 쓴 순서를 짐작하는 근거는 이번에 연 자료에 없으므로 순서로 시간 순서를 단정하지 않습니다.

시각이 필요하면 같은 경로를 [BAM·DAM](background-activity-moderator.md), [UserAssist](userassist.md), [프리페치](prefetch/index.md) 에서 찾습니다.

## 함정과 한계

- **NTUSER.DAT 만 수집하면 놓칩니다.** Windows 11 PC 한 대에서 이 키는 UsrClass.dat 에 있었습니다. 사용자 프로필마다 두 하이브를 함께 수집합니다.
- **앱 이름이 파일의 FileDescription 과 다를 수 있습니다.** 현지화된 이름이 들어가거나, 파일 이름이 대신 들어갈 수 있습니다. 앱 이름으로 파일을 찾을 때는 경로를 기준으로 삼습니다.
- **.exe 만 있지 않습니다.** Windows 11 PC 한 대에는 .dll·.bat 경로도 있었습니다.
- **XP 와 Vista 이후의 경로가 다릅니다.** 검체 버전에 맞는 경로를 봅니다.
- **항목은 지울 수 있습니다.** 다만 NirSoft 에 따르면 다시 실행하면 다시 생깁니다. 값이 적거나 없으면 이전 시점 하이브를 [섀도 복사본](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에서 꺼내 비교합니다. 조작 흔적을 찾는 흐름은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에 있습니다.
- **하이브 사본만 보면 최근 변경이 빠질 수 있습니다.** 하이브 로그를 함께 수집합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 값 형식에 맞춰 만든 예시입니다. 특정 검체에서 꺼낸 값이 아닙니다.

**`LangID` 값.**

```
12 04
```

2바이트를 리틀 엔디언으로 읽으면 0x0412 입니다. 언어 ID 표에서 한국어(ko-KR)입니다.

**`.FriendlyAppName` 값 데이터 (REG_SZ, 'Windows 탐색기').**

```
57 00 69 00 6E 00 64 00 6F 00 77 00 73 00 20 00   W.i.n.d.o.w.s. .
D0 D0 C9 C0 30 AE                                  탐 색 기
```

1. REG_SZ 문자열은 UTF-16LE 입니다. 한 글자가 2바이트입니다.
2. `57 00` 은 U+0057, 곧 'W' 입니다.
3. `D0 D0` 은 U+D0D0 '탐', `C9 C0` 은 U+C0C9 '색', `30 AE` 는 U+AE30 '기' 입니다.
4. 한글도 UTF-16LE 로 그대로 들어갑니다. 인코딩은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.

### 공개 도구로 한 번

1. 사용자 프로필에서 UsrClass.dat 와 하이브 로그를 함께 사본으로 뜹니다. XP 검체라면 NTUSER.DAT 를 뜹니다.
2. 레지스트리 뷰어로 `Local Settings\Software\Microsoft\Windows\Shell\MuiCache` 를 엽니다.
3. 값 이름을 `.FriendlyAppName`·`.ApplicationCompany` 로 나눠 경로별로 묶습니다.
4. 켜진 PC 에서는 MuiCache 를 보여 주는 공개 도구로 같은 키를 볼 수 있습니다.
5. 도구 결과의 한 줄을 골라 위 풀이대로 값 데이터를 직접 한 번 읽어 봅니다.
6. 파일이 아직 있으면 파일의 버전 정보(FileDescription·CompanyName)와 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 실행 파일 메타데이터 | 앱 이름이 파일의 버전 정보와 맞는지 봅니다 | [실행 파일 메타데이터](../embedded-metadata/pe-header-version-info-digital-signature.md) |
| BAM | 같은 경로의 최근 실행 시각을 봅니다 | [BAM·DAM](background-activity-moderator.md) |
| UserAssist | 같은 계정이 탐색기로 띄운 횟수와 마지막 실행 시각을 봅니다 | [UserAssist](userassist.md) |
| 심캐시 | 같은 경로의 파일이 시스템에 있었는지 봅니다 | [심캐시](shimcache-appcompatcache.md) |
| 프리페치 | 실행 횟수와 실행 시각을 봅니다 | [프리페치](prefetch/index.md) |
| AmCache | 같은 경로의 실행 파일 기록이 있는지 봅니다 | [AmCache](amcache-hve/index.md) |
| 설치 프로그램 | 지금은 없는 프로그램이 설치 목록에 있었는지 봅니다 | [설치 프로그램](../system-account/uninstall.md) |
| 사용자 프로필 목록 | 하이브가 어느 계정의 것인지 확인합니다 | [사용자 프로필 목록](../system-account/profilelist.md) |

실행 흔적 전체를 엮는 흐름은 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md) 에 있습니다.

## 실습

공개 검체(NIST CFReDS 등)에서 사용자 하이브를 꺼내 아래 질문을 풀어 봅니다.

1. 검체의 Windows 버전으로 보아 어느 하이브의 어느 경로를 열어야 합니까?
2. `.FriendlyAppName` 값은 몇 개입니까? 그 가운데 지금 디스크에 없는 경로는 몇 개입니까?
3. 파일이 남아 있는 항목 하나를 골라 앱 이름과 파일의 FileDescription 을 맞춰 봅니다. 같습니까?
4. 키의 마지막 기록 시각은 언제입니까? 그 무렵 BAM 이나 프리페치에 새로 나타난 프로그램이 있습니까?
5. MuiCache 에만 있고 다른 실행 흔적에는 없는 경로가 있습니까? 그 경로를 "실행했다" 고 쓸 수 있습니까?

## 참고 문헌

1. libyal, *winreg-kb: Multilingual User Interface (MUI) cache* (이름, XP·Vista 이후 키 경로). https://raw.githubusercontent.com/libyal/winreg-kb/main/docs/sources/explorer-keys/MUI-cache.md
2. NirSoft, *MUICacheView* 소개 페이지 (키 경로, 항목이 생기는 때, 지운 뒤 다시 생기는 점). https://www.nirsoft.net/utils/muicache_view.html
3. Microsoft, *[MS-LCID]: Windows Language Code Identifier (LCID) Reference* (0x0412 = 한국어 ko-KR). https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-lcid/a9eac961-e77d-41a6-90a5-ce1a8b0cdb9c
