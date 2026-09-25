---
title: "UserAssist"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 960
---

# UserAssist (UserAssist)

## 한 줄 요약

사용자 하이브(NTUSER.DAT)의 `UserAssist` 키에 탐색기로 띄운 프로그램과 바로 가기가 남는데, 값 이름은 ROT-13 으로 가려져 있고 값 데이터에는 실행 횟수와 마지막 실행 시각이 들어 있습니다.

## 무엇을 기록하나 · 왜 생기나

libyal 은 이 키를 탐색기(explorer.exe)로 띄운 프로그램의 설정과 데이터를 담는 키로 설명합니다. 사용자 하이브에 있으므로 계정마다 따로 남고, 항목은 GUID 로 된 하위 키 아래 `Count` 키에 값으로 쌓입니다. 값 이름은 프로그램 경로나 바로 가기 경로를 가린 문자열이며 가리는 방법은 "구조" 절에서 다룹니다. 값 데이터에는 실행 횟수와 마지막 실행 시각이 들어 있습니다.

NT4 에는 이 키가 없는 것으로 보입니다. libyal 은 Windows 2000 에서 생긴 것으로 추정합니다.

## 위치와 버전별 차이

```
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist\{GUID}\Count
```

- Windows 11 PC 한 대에서 HKCU 에 해당하는 하이브 파일은 `C:\Users\<user>\NTUSER.DAT` 였습니다.
- 각 GUID 키에는 REG_DWORD `Version` 값이 있습니다. 항목은 하위 키 `Count` 에 있습니다.

| Version | Windows |
|---|---|
| 3 | 2000·XP·2003·Vista |
| 5 | 2008(R2 인지는 불확실)·7·8 |

**GUID 하위 키 (libyal 의 정리)**

| GUID | Windows | 내용 |
|---|---|---|
| `{CEBFF5CD-ACE2-4F4F-9178-9926F41749EA}` | 2008(R2?)·7·8·10 | 실행 파일 실행으로 추정 (libyal 도 확정하지 않음) |
| `{F4E57C4B-2036-45F0-A9AB-443BCFE33D9F}` | 2008(R2?)·7·8·10 | 바로 가기(LNK) 실행으로 추정 (libyal 도 확정하지 않음) |
| `{5E6AB780-7743-11CF-A12B-00AA004AE837}` | 2000·XP·2003·Vista | Microsoft Internet Toolbar |
| `{75048700-EF1F-11D0-9888-006097DEACF9}` | 2000·XP·2003·Vista | ActiveDesktop |
| `{0D6D4F41-2994-4BA0-8FEF-620E43CD2812}` | XP·Vista | IE7 로 추정 |
| `{9E04CAB2-CC14-11DF-BB8C-A2F1DED72085}`, `{A3D53349-6E61-4557-8FC7-0028EDCEEBF6}`, `{F2A1CB5A-E3CC-4A2E-AF9D-505A7009D442}`, `{FA99DFC7-6AC2-453A-A5E2-5E2AFF4507BD}` | 8·10 | 설명 없음 |
| `{B267E3AD-A825-4A09-82B9-EEC22AA3B847}`, `{CAA59E3C-4792-41A5-9909-6A6A8D32490E}` | 8 | 설명 없음 |
| `{BCB48336-4DDD-48FF-BB0B-D3190DACB3E2}` | 8.1 | 설명 없음 |

Windows 11 PC 한 대에서 본 모습은 아래와 같습니다.

- GUID 키는 9개였습니다. 9E04CAB2·A3D53349·B267E3AD·BCB48336·CAA59E3C·CEBFF5CD·F2A1CB5A·F4E57C4B·FA99DFC7 이고, 모두 Version=5 였습니다.
- 항목이 들어 있는 키는 둘뿐이었습니다. CEBFF5CD 에는 72바이트 값이 202개, F4E57C4B 에는 24개 있었습니다.
- 나머지 가운데 6개에는 `UEME_CTLSESSION`(1,612바이트) 값 하나만 있었습니다. B267E3AD 에는 값이 없었습니다.

하이브 파일의 구조와 수집 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

## 구조

### 값 이름 가리기

- `Count` 아래 값 이름은 ROT-13 으로 가려져 있습니다. ASCII 알파벳 `[A-Za-z]` 만 13자리씩 밀고, 숫자와 0x80 이상 문자는 그대로 둡니다.
- Windows 7 베타는 ROT-13 대신 비즈네르 암호 (Vigenère) 를 썼습니다. 키는 `BWHQNKTEZYFSLMRGXADUJOPIVC` 입니다.
- `Settings` 하위 키에 `NoEncrypt`=1 이 있으면 이름을 가리지 않고, `NoLog`=1 이 있으면 기록을 끕니다.
- `Settings` 키는 기본으로는 없으며 Windows 11 PC 한 대에도 없었습니다.

### 특수 값 이름

| 이름 (ROT-13 을 푼 뒤) | 뜻 |
|---|---|
| `UEME_CTLSESSION` | 세션 식별자 |
| `UEME_CTLCUACount:ctor` | — |
| `UEME_RUNCPL` | 제어판 애플릿 |
| `UEME_RUNPATH` | 실행 프로그램 |
| `UEME_RUNPIDL` | PIDL·바로 가기로 실행 |
| `UEME_RUNWMCMD` | 실행 명령 |
| `UEME_UIHOTKEY` | 단축키 |
| `UEME_UIQCUT` | 빠른 실행 |
| `UEME_UISCUT` | 바탕 화면 바로 가기 |
| `UEME_UITOOLBAR` | 탐색기 도구 모음 |

### 풀어 본 값 이름의 형태

Windows 11 PC 한 대에서 ROT-13 을 푼 값 이름은 네 가지 형태였습니다.

- 알려진 폴더 (Known Folder) GUID 로 시작하는 경로
- `C:\…` 로 시작하는 전체 경로
- 앱 사용자 모델 ID (AppUserModelID). `…!App` 처럼 이름에 `!` 가 들어 있습니다
- `UEME_` 로 시작하는 이름

F4E57C4B(바로 가기) 키의 항목은 `UEME_` 이름 두 개를 빼면 모두 알려진 폴더 GUID 로 시작하는 .lnk 경로였습니다. 시작 메뉴와 작업 표시줄 고정 폴더의 바로 가기였습니다.

같은 PC 에서 SHGetKnownFolderPath 로 푼 알려진 폴더 GUID 는 아래와 같습니다.

| GUID | 풀린 경로 |
|---|---|
| `{6D809377-6AF0-444B-8957-A3773F02200E}` | `C:\Program Files` |
| `{7C5A40EF-A0FB-4BFC-874A-C0F2E0B9FA8E}` | `C:\Program Files (x86)` |
| `{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}` | `C:\WINDOWS\system32` |
| `{F38BF404-1D43-42F2-9305-67DE0B28FC23}` | `C:\WINDOWS` |
| `{0139D44E-6AFE-49F2-8690-3DAFCAE6FFB8}` | `C:\ProgramData\Microsoft\Windows\Start Menu\Programs` |
| `{A77F5D77-2E2B-44C3-A6A2-ABA601054A51}` | 사용자 `AppData\Roaming\Microsoft\Windows\Start Menu\Programs` |
| `{9E3995AB-1F9C-4F13-B827-48B24B6C7174}` | 사용자 `AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\User Pinned` |

알려진 폴더 ID 의 일반 구조는 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에서 다룹니다.

### 값 데이터

**Version 3 (16바이트)**

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 세션 식별자 |
| 4 | 4 | 실행 횟수 |
| 8 | 8 | 마지막 실행 시각 (FILETIME) |

**Version 5 (72바이트)**

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 알 수 없음. libyal 은 0, -1, 1 을 보았습니다 |
| 4 | 4 | 실행 횟수 |
| 8 | 4 | 알 수 없음. "포커스 횟수" 로 부르는 자료가 있습니다 |
| 12 | 4 | 알 수 없음. "포커스 시간" 으로 부르는 자료가 있습니다. GUID 마다 뜻이 다를 수 있습니다 |
| 16~55 | 40 | 알 수 없음. 4바이트씩 부동소수점으로 보이는 값(0.0 또는 -1.0)이 이어집니다 |
| 56 | 4 | 알 수 없음. 가끔 -1 입니다 |
| 60 | 8 | 마지막 실행 시각 (FILETIME). 없으면 0 |
| 68 | 4 | 알 수 없음 (0) |

- 오프셋 8·12 의 "포커스 횟수·포커스 시간" 은 libyal 이 확정하지 않은 해석입니다.
- `UEME_CTLSESSION` 은 Version 3 에서 8바이트, Version 5 에서 1,612바이트입니다. 1,612바이트 안에는 532바이트 레코드 세 개가 오프셋 0x10·0x224·0x438 에 있습니다.

Windows 11 PC 한 대의 CEBFF5CD 키에서 본 값은 아래와 같습니다.

항목 202개 가운데 201개는 오프셋 0 의 값이 11 이었고 나머지 하나(`UEME_CTLCUACount:ctor`)는 -1 이었습니다. 같은 키 `UEME_CTLSESSION` 의 첫 4바이트도 11 이었지만 두 값이 같은 뜻인지는 확인하지 못했습니다. 실행 횟수(오프셋 4)가 1 이상인 항목은 16개뿐이었습니다. 113개는 실행 횟수가 0 인데 오프셋 60 에 시각이 있었고, 73개는 시각이 0 이었습니다.

## 증거로서 의미

### 증명하는 것

- 이 계정의 UserAssist 에 이 프로그램이나 바로 가기의 항목이 있습니다. libyal 의 설명대로라면 그 계정 문맥에서 탐색기를 거쳐 띄운 기록입니다.
- 실행 횟수가 1 이상이고 시각이 있으면, 그 횟수와 마지막 실행 시각을 기록이 말하는 만큼 쓸 수 있습니다.
- 값 이름에 경로가 들어 있으므로, 띄울 때 프로그램이나 바로 가기가 어느 폴더에 있었는지 알 수 있습니다.

### 증명하지 못하는 것

- **처음 실행한 때.** 일부 자료는 이 시각을 처음 실행 시각으로 소개합니다. libyal 은 Version 3·5 모두 마지막 실행 시각으로 적습니다. 이 페이지는 libyal 을 따릅니다.
- **탐색기를 거치지 않은 실행.** 명령줄 등 다른 방법으로 띄운 프로그램이 여기에 남는지는 이번에 연 자료로 확인하지 못했습니다. 항목이 없다고 실행하지 않은 것은 아닙니다.
- **포커스 횟수·포커스 시간.** 확정되지 않은 해석입니다. 보고서에 사용 시간으로 쓰지 않습니다.
- **실행 횟수 0 에 시각이 있는 항목의 뜻.** 이번에 확인하지 못했습니다. 이런 항목을 "한 번도 실행하지 않았다" 로도, "실행했다" 로도 단정하지 않습니다.
- **키보드 앞의 사람.** 하이브가 가리키는 것은 계정입니다. 사람을 좁히는 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.

보고서에는 "이 계정의 UserAssist 에 이 경로의 항목이 있고, 실행 횟수는 N, 마지막 실행 시각은 이 시각으로 기록돼 있다" 처럼 씁니다.

## 시각 해석

- 시각은 FILETIME 이고 UTC 로 읽습니다. 변환은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
- Version 3 은 오프셋 8, Version 5 는 오프셋 60 에서 시각을 읽습니다.
- 시각이 0 이면 기록된 실행 시각이 없는 것입니다.
- 시각은 마지막 실행 시각입니다. 같은 프로그램을 여러 번 띄웠다면 앞선 실행 시각은 여기에 없습니다.

## 함정과 한계

- **ROT-13 을 풀지 않고 찾으면 놓칩니다.** 예를 들어 `cmd.exe` 는 값 이름에 `pzq.rkr` 로 들어 있습니다. 키워드 검색은 이름을 푼 뒤에 합니다.
- **GUID 안의 알파벳도 바뀝니다.** GUID 의 A~F 도 ROT-13 대상입니다. 숫자는 그대로입니다. 그래서 가려진 GUID 는 N~S 와 숫자로 보입니다.
- **알려진 폴더 GUID 를 경로로 풀어야 합니다.** 사용자 폴더 쪽 GUID 는 계정마다 실제 경로가 다릅니다. 위 표는 한 PC 에서 푼 결과입니다.
- **Version 마다 오프셋이 다릅니다.** Version 3 표로 72바이트 값을 읽으면 엉뚱한 숫자가 나옵니다. 먼저 GUID 키의 `Version` 값을 봅니다.
- **실행 횟수가 1 이상인 항목은 드뭅니다.** Windows 11 PC 한 대에서 202개 가운데 16개뿐이었습니다. 실행 횟수만 보고 항목을 거르면 대부분을 놓칩니다.
- **기록을 끄거나 가림을 풀 수 있습니다.** `Settings` 키의 `NoLog`=1 은 기록을 끄고, `NoEncrypt`=1 은 이름 가리기를 끕니다. 기본으로는 없는 키이므로, 있다면 누가 언제 만들었는지 봅니다. 조작 흔적을 찾는 흐름은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에 있습니다.
- **값은 지울 수 있습니다.** 값이 적거나 없으면 이전 시점 하이브를 [섀도 복사본](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에서 꺼내 비교합니다.
- **하이브 사본만 보면 최근 변경이 빠질 수 있습니다.** 하이브 로그를 함께 수집합니다. 반영 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 libyal 명세로 만든 예시입니다. 특정 검체에서 꺼낸 값이 아닙니다.

**값 이름 풀기.**

```
HRZR_PGYFRFFVBA                          →  UEME_CTLSESSION
{1NP14R77-02R7-4R5Q-O744-2RO1NR5198O7}   →  {1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}
```

1. 알파벳마다 13자리를 밉니다. H→U, R→E, Z→M 입니다.
2. `_`·`-`·`{`·`}` 와 숫자는 그대로 둡니다.
3. 두 번째 줄을 풀면 알려진 폴더 GUID 가 나옵니다. 한 PC 에서 이 GUID 는 `C:\WINDOWS\system32` 로 풀렸습니다.

**Version 5 값 데이터 72바이트 (실행 횟수 3 으로 만든 예시).**

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    00 00 00 00 03 00 00 00 00 00 00 00 00 00 00 00
0x10    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0x20    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0x30    00 00 00 00 00 00 00 00 00 00 00 00 00 C0 89 76
0x40    45 3C DA 01 00 00 00 00
```

1. 오프셋 4 의 `03 00 00 00` 은 실행 횟수 3 입니다.
2. 오프셋 16~59 는 뜻을 모르는 칸입니다. 이 예시에서는 0 으로 채웠습니다.
3. 오프셋 60(0x3C)부터 8바이트 `00 C0 89 76 45 3C DA 01` 을 리틀 엔디언으로 읽으면 `0x01DA3C457689C000` 입니다.
4. FILETIME 으로 바꾸면 2024-01-01 00:00:00(UTC) 입니다. 마지막 실행 시각입니다.
5. 오프셋 68 의 4바이트는 알 수 없는 값(0)입니다. 값 전체는 0x48, 곧 72바이트입니다.

### 공개 도구로 한 번

1. 사용자 프로필에서 NTUSER.DAT 와 하이브 로그를 함께 사본으로 뜹니다.
2. 레지스트리 뷰어로 `Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist` 를 엽니다.
3. GUID 키마다 `Version` 값과 `Count` 의 값 개수를 적습니다. `Settings` 키가 있는지도 봅니다.
4. ROT-13 과 Version 5 구조를 풀어 주는 공개 레지스트리 도구로 목록을 뽑습니다.
5. 도구 결과의 한 줄을 골라 위 풀이대로 값 이름과 시각을 직접 한 번 읽어 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 바로가기 파일 | F4E57C4B 항목의 .lnk 가 가리키는 대상을 봅니다 | [바로가기 파일](../file-folder-usage/lnk.md) |
| 점프리스트 | 같은 앱으로 연 파일을 봅니다 | [점프리스트](../file-folder-usage/jump-lists.md) |
| 작업표시줄 사용 기록 | 같은 앱을 작업 표시줄에서 다룬 횟수를 봅니다 | [작업표시줄 사용 기록](featureusage.md) |
| BAM | 같은 계정의 최근 실행 시각을 봅니다 | [BAM·DAM](background-activity-moderator.md) |
| MUICache | 같은 계정이 쓰기 시작한 프로그램 이름을 봅니다 | [MUICache](muicache.md) |
| 심캐시 | 같은 경로의 파일이 시스템에 있었는지 봅니다 | [심캐시](shimcache-appcompatcache.md) |
| 프리페치 | 실행 횟수와 여러 번의 실행 시각을 봅니다 | [프리페치](prefetch/index.md) |
| 사용자 프로필 목록 | 하이브가 어느 계정의 것인지 확인합니다 | [사용자 프로필 목록](../system-account/profilelist.md) |

실행 흔적 전체를 엮는 흐름은 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md) 에 있습니다.

## 실습

공개 검체(NIST CFReDS 등)에서 사용자 NTUSER.DAT 를 꺼내 아래 질문을 풀어 봅니다.

1. GUID 키의 `Version` 값은 3 입니까, 5 입니까? 검체의 Windows 버전과 맞습니까?
2. CEBFF5CD 키와 F4E57C4B 키에는 값이 몇 개씩 있습니까?
3. 실행 횟수가 가장 큰 항목은 무엇입니까? 그 항목의 마지막 실행 시각을 직접 FILETIME 으로 바꿔 봅니다.
4. 실행 횟수가 0 인데 시각이 있는 항목은 몇 개입니까?
5. `Settings` 키가 있습니까? 있다면 `NoLog`·`NoEncrypt` 값은 무엇입니까?
6. 같은 프로그램의 프리페치 마지막 실행 시각과 UserAssist 의 시각은 얼마나 차이 납니까?

## 참고 문헌

1. libyal, *winreg-kb: User Assist key* (키 위치, 생긴 시기, GUID 하위 키, Version, ROT-13·비즈네르 가리기, `Settings` 의 `NoEncrypt`·`NoLog`, 특수 값 이름, Version 3·5 값 구조, 마지막 실행 시각). https://raw.githubusercontent.com/libyal/winreg-kb/main/docs/sources/explorer-keys/User-assist.md
