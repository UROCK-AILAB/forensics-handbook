---
title: "바로가기 항목"
parent: "AmCache"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 900
---

# 바로가기 항목 (InventoryApplicationShortcut)

## 한 줄 요약

Amcache.hve 의 `Root\InventoryApplicationShortcut` 키에는 호환성 인벤토리가 시작 메뉴 같은 폴더에서 찾은 바로가기(LNK) 파일이 하나씩 하위 키로 남습니다. 옛 판에는 LNK 경로 하나만 있고, 새 판에는 대상 경로와 앱 식별자가 더 있습니다. 이 기록은 "그 바로가기가 있었다" 는 뜻입니다. 실행했다는 뜻이 아닙니다.

## 무엇을 기록하나 · 왜 생기나

윈도의 호환성 인벤토리는 설치된 프로그램과 실행 파일 목록을 모아 Amcache.hve 에 적습니다. 바로가기 목록은 예약 작업 Microsoft Compatibility Appraiser 가 채웁니다. ANSSI 는 10.0.16299 판 라이브러리(Windows 10 1709 에 처음 실림)부터 이 작업이 시작 메뉴 폴더를 훑는다고 확인했습니다. 이 작업은 시작 메뉴에서 LNK 파일만 골라 이 키에 넣습니다.

그래서 이 키로 검사한 때에 어떤 바로가기가 어느 폴더에 있었는지 알 수 있고, 새 판이라면 그 바로가기가 가리킨 파일과 연결된 설치 프로그램 식별자도 알 수 있습니다.

시작 메뉴 바로가기는 대개 설치 프로그램이 만듭니다. 그래서 이 키는 설치 흔적을 보강하는 데 주로 씁니다. 다만 Zimmerman 은 MSI 나 설치 프로그램이 아닌 다른 프로그램이 직접 만든 바로가기도 들어온 것을 보고했습니다.

Amcache.hve 의 위치와 누가 언제 쓰는지는 [AmCache](index.md) 허브에서 다룹니다. 여기서는 바로가기 키만 다룹니다.

## 위치와 버전별 차이

키 위치는 `%WinDir%\AppCompat\Programs\Amcache.hve` 의 `Root\InventoryApplicationShortcut` 입니다. 이 키의 모양은 Windows 버전보다 호환성 라이브러리의 판을 따릅니다([구조와 버전별 차이](structure-versions.md)).

| 자료 | 확인한 곳 | 하위 키 안의 값 | 나온 폴더 |
|---|---|---|---|
| 10.0.16299 판 라이브러리 (Win10 1709) | ANSSI 2019 | LNK 전체 경로 하나 | 모든 사용자 시작 메뉴 `C:\ProgramData\Microsoft\Windows\Start Menu` |
| Windows Server 2016 표본 하이브 (2019년 수집, 라이브러리 판 모름) | 공개 파서 저장소(frnsc-amcache)에 실린 표본 | `ShortcutPath` (REG_SZ) 하나 | 모든 사용자 시작 메뉴, 사용자별 시작 메뉴, 공용 바탕 화면 `C:\Users\Public\Desktop` |
| 2025년 설명 | Kaspersky Securelist | `ShortcutPath`·`ShortcutTargetPath`·`ShortcutProgramId` | 사용자별 시작 메뉴·바탕 화면이라고 설명합니다 |
| Windows 11 빌드 26200 (한 대) | 관찰 | `ShortcutPath`·`ShortcutTargetPath`·`ShortcutAumid`·`ShortcutProgramId` (모두 REG_SZ), 이름 없는 기본값 (REG_DWORD) | 대부분 모든 사용자·사용자별 시작 메뉴 |
| Windows 11 24H2·25H2 | Microsoft Learn | 진단 이벤트가 캐시 안의 "application shortcut" 개수를 셉니다 | — |

- 10.0.16299 보다 앞선 판의 하이브에는 이 키가 없습니다(ANSSI).
- 값이 넷으로 늘어난 판이 어느 것인지 밝힌 공개 연구는 찾지 못했습니다. 검체마다 값 목록을 먼저 확인합니다.
- 공개 파서 소스(frnsc-amcache)도 위의 값 네 개를 읽습니다.
- 이 페이지가 확인한 Microsoft Learn 문서에는 이 값들의 설명이 없습니다. 이 문서로는 바로가기 항목이 지금의 인벤토리 캐시에도 있다는 사실만 확인됩니다.

## 구조

### 하위 키 이름

하위 키 하나가 LNK 파일 하나입니다. 이름은 `파일 이름|16진수` 꼴입니다.

- ANSSI 가 보인 예는 `wireshark.lnk|ee4ba020` 입니다. 뒤쪽 16진수가 8자리입니다.
- 공개 표본과 Windows 11 한 대에서 앞쪽은 대개 LNK 파일 이름을 소문자로 바꾼 뒤 앞 16자에서 자른 값이었습니다. 뒤쪽 16진수는 대개 16자리였습니다. 앞자리 0 이 빠진 듯한 15자리도 있었습니다.
- 뒤쪽 16진수를 어떻게 계산하는지는 공개된 자료에서 찾지 못했습니다. 이 16진수로는 경로를 되살릴 수 없으므로 경로는 `ShortcutPath` 에서 읽습니다.

이름이 16자에서 잘리므로 이름이 비슷한 바로가기끼리 앞부분이 같아질 수 있습니다. 하위 키 이름으로 바로가기를 가리지 말고 `ShortcutPath` 값으로 가립니다.

### 값

| 값 | 형식 | 뜻 | 근거 |
|---|---|---|---|
| `ShortcutPath` | REG_SZ | LNK 파일의 전체 경로. 검사할 때의 위치입니다 | ANSSI, Securelist, 표본 |
| `ShortcutTargetPath` | REG_SZ | 바로가기가 가리킨 대상 경로 | Securelist |
| `ShortcutProgramId` | REG_SZ | 연결된 설치 프로그램의 식별자. [설치 프로그램 항목](inventoryapplication.md)의 하위 키 이름과 맞춰 봅니다 | Securelist |
| `ShortcutAumid` | REG_SZ | 값 이름으로 보아 앱 사용자 모델 ID (AppUserModelID) 입니다. 작업 표시줄이 창과 바로가기를 한 앱으로 묶을 때 쓰는 식별자입니다 | 파서 소스, 관찰 |
| 이름 없는 기본값 | REG_DWORD | 뜻을 확인하지 못했습니다 | 관찰 (Win11 한 대) |

Windows 11 한 대에서 본 모습은 다음과 같습니다(확인 범위: Windows 11 빌드 26200 한 대).

모든 하위 키에 값 다섯 개가 다 있었는데, `ShortcutTargetPath`·`ShortcutAumid` 는 몇 항목에서 비어 있었고 `ShortcutProgramId` 는 절반이 넘는 항목에서 비어 있었습니다.

LNK 파일 자체의 구조는 [바로가기 형식](../../../01-foundations/shell-document-formats/shell-link-lnk.md)에서 다룹니다. 이 키에는 LNK 안의 시각·볼륨 정보·셸 아이템이 없습니다.

> 그림 자리: `Root\InventoryApplicationShortcut\<파일 이름|16진수>` 하위 키 하나를 펼쳐, 옛 판(값 하나)과 새 판(값 네 개와 기본값)을 나란히 보여 주는 그림. `ShortcutProgramId` 가 InventoryApplication 하위 키로 이어지는 화살표 포함

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 인벤토리가 검사할 때 이 경로에 이 LNK 파일이 있었습니다 | 바로가기를 눌러 프로그램을 실행했는지 |
| (새 판) 그 LNK 가 가리킨 대상 경로 | 대상 파일이 실제로 있었는지 |
| (새 판) 인벤토리가 이 바로가기를 어느 설치 프로그램에 묶었는지 | LNK 를 누가, 언제 만들었는지 |
| 사용자별 시작 메뉴 경로라면 그 사용자 프로필 폴더 안에 바로가기가 있었습니다 | 조사 시점에도 LNK 가 남아 있는지 |
| | 이 PC 에 있던 바로가기 전체. 검사하지 않는 폴더의 LNK 는 들어오지 않습니다 |

바로가기를 최근에 열었다는 뜻으로 이 키를 읽는 설명도 있습니다. 그러나 이 키에는 LNK 를 연 시각이 없습니다. 실행을 말하려면 아래 교차 검증 표의 실행 흔적이 따로 있어야 합니다.

사용자별 시작 메뉴 경로에는 프로필 폴더 이름이 들어 있습니다. 이 이름으로 사용자 SID 를 찾을 수 있습니다([사용자 프로필 목록](../../system-account/profilelist.md)). `C:\ProgramData` 와 공용 바탕 화면의 바로가기는 특정 사용자와 묶이지 않습니다.

### 보고서 문장

아래 경로와 시각은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "Amcache.hve 의 InventoryApplicationShortcut 에 `C:\Users\<사용자>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Tool\Tool.lnk` 항목이 있습니다. 이 하위 키의 마지막 기록 시각은 2025-03-14 01:23:45 UTC 입니다. 늦어도 이 무렵에는 이 경로에 바로가기가 있었던 것으로 봅니다."
- 쓰면 안 되는 문장: "사용자가 2025-03-14 01:23:45 에 Tool 바로가기를 만들고 실행했습니다."

## 시각 해석

이 키의 값에는 시각이 없습니다. 쓸 수 있는 시각은 하위 키의 마지막 기록 시각 (Last Write Time) 하나입니다. 이 시각은 UTC 기준 FILETIME 입니다([키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md), [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)).

이 시각은 인벤토리가 하위 키를 쓴 때입니다. LNK 파일이 생긴 때가 아닙니다. Qazeer 노트도 이 시각이 LNK 파일의 NTFS 시각 넷 가운데 어느 것과도 맞지 않는 것 같다고 적습니다. 그런데 하위 키를 언제 다시 쓰는지는 판마다 달랐습니다.

| 관찰 | 하위 키 시각의 모습 | 읽는 법 |
|---|---|---|
| 2019년 공개 표본 (Windows Server 2016) | 몇 개의 무리로 나뉩니다. 한 무리는 같은 분 안에 몰려 있습니다. 한 사용자의 시작 메뉴 바로가기가 모두 한 무리였습니다. 상위 키 시각은 하위 키들보다 한 달 넘게 뒤였습니다 | 뒤의 검사가 이미 있는 하위 키를 다시 쓰지 않은 것으로 보입니다. 하위 키 시각은 처음 기록한 때에 가깝습니다 |
| Windows 11 빌드 26200 한 대 | 모든 하위 키가 같은 분 안에 있었습니다 | 검사할 때마다 모두 다시 쓴 것으로 보입니다. 하위 키 시각은 마지막 검사 때입니다 |

그래서 시각을 해석하기 전에 먼저 하위 키 시각을 분 단위로 묶어 봅니다.

- 모든 하위 키가 한 시각에 몰려 있으면 그 시각은 마지막 검사 시각입니다. 개별 바로가기가 언제 생겼는지는 알 수 없습니다.
- 여러 무리로 나뉘면 각 무리가 한 번의 검사일 수 있습니다. 이때 하위 키 시각은 "늦어도 이때는 있었다" 는 하한으로만 씁니다.
- 같은 분에 [실행 파일 항목](inventoryapplicationfile.md)이 함께 몰려 있는지도 봅니다. 공개 표본에서는 한 사용자의 바로가기 무리와 같은 분에 실행 파일 항목도 여럿 기록돼 있었습니다.

검사는 예약 작업이 돌 때만 합니다. 그래서 LNK 가 생긴 때와 하위 키 시각 사이에는 검사 간격만큼 틈이 생길 수 있습니다. 예약 작업의 실행 기록은 [예약 작업](../../persistence/scheduled-tasks/index.md)에서 확인합니다.

## 함정과 한계

1. **실행 증거로 씁니다.** 이 키는 바로가기가 있었다는 기록입니다. ANSSI 는 이 키를 찾은 LNK 파일 목록으로만 설명합니다. Kaspersky 도 이 키를 다른 자료와 함께 봐야 실행을 말할 수 있는 키로 분류합니다.
2. **하위 키 이름으로 경로를 짐작합니다.** 이름은 파일 이름의 앞 16자만 남깁니다. 폴더도 들어 있지 않습니다. 경로는 `ShortcutPath` 에서 읽습니다.
3. **대소문자로 비교합니다.** 공개 표본에서 사용자별 경로는 `c:\users\…` 처럼 앞부분이 소문자였습니다. 모든 사용자 경로는 `C:\ProgramData\…` 로 대문자였습니다. 다른 기록과 경로를 맞출 때는 대소문자를 가리지 않고 비교합니다.
4. **`ShortcutProgramId` 짝을 믿고 끝냅니다.** Kaspersky 는 이 값으로 InventoryApplication 항목을 찾으라고 설명합니다. 그러나 Windows 11 한 대에서 값이 있는 항목을 하위 키 이름과 글자 그대로 맞춰 보니 짝이 나오지 않았습니다. 원인(표기 차이인지, 이미 지운 프로그램인지)은 확인하지 못했습니다. 짝이 없으면 [설치 프로그램 (Uninstall)](../../system-account/uninstall.md)에서 다시 찾아봅니다.
5. **검사 범위를 전체로 봅니다.** 이 키에는 검사하는 폴더의 LNK 만 들어옵니다. 검사 폴더는 판마다 다릅니다. 검체에서 실제로 나온 경로로 범위를 가늠합니다. 최근 문서 폴더의 LNK 는 [바로가기 파일 (LNK)](../../file-folder-usage/lnk.md)에서 따로 봅니다.
6. **값이 빠진 판을 오류로 봅니다.** 옛 판에는 `ShortcutPath` 하나만 있습니다. 대상 경로가 없다고 해서 하이브가 손상된 것이 아닙니다.
7. **도구 출력만 봅니다.** 아래 "공개 도구로 한 번" 에서 보듯 도구마다 읽는 값이 다릅니다.

### 지우기와 조작

- **LNK 파일을 지웁니다.** LNK 를 지운 뒤 다음 검사에서 하위 키가 빠지는지 밝힌 공개 연구는 찾지 못했습니다. Qazeer 노트는 지금은 없는 LNK 도 이 키에 남아 있을 수 있다고 적습니다. LNK 가 지워진 기록은 [$UsnJrnl](../../filesystem/usnjrnl.md)과 [$MFT](../../filesystem/mft.md)에서 찾습니다.
- **하위 키나 하이브를 지웁니다.** 지운 키는 하이브 안의 비할당 셀에 남을 수 있습니다([지워진 키·값 복구](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md)). 아직 주 파일에 들어가지 않은 변경은 `.LOG1`·`.LOG2` 에 있습니다([트랜잭션 로그](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md)). 옛 하이브는 [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)에서 찾습니다.
- **키 시각을 바꿉니다.** 키 마지막 기록 시각은 따로 바꿀 수 있습니다. 조작 흔적을 가리는 법은 [키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md)에서 다룹니다. 같은 무리의 다른 하위 키와 시각이 동떨어진 항목이 있으면 의심해 봅니다.
- **검사 폴더 밖에 바로가기를 둡니다.** 이 키에는 남지 않습니다. 다른 기록으로 찾아야 합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 레지스트리 하이브 형식 명세를 보고 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다. 하위 키 이름의 16진수와 셀 오프셋도 지어낸 값입니다. 값이 하나인 옛 판 모양입니다. 셀·키 노드·값 구조의 자세한 설명은 [하이브 내부 구조](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)를 봅니다.

오프셋은 셀 맨 앞(셀 크기 칸)부터 센 값입니다. 명세 표의 오프셋에 4 를 더한 값과 같습니다.

**하위 키의 키 노드 (nk) 셀**

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    90 FF FF FF 6E 6B 20 00 80 66 9A BA 7F 94 DB 01
0x10    00 00 00 00 20 10 00 00 00 00 00 00 00 00 00 00
0x20    FF FF FF FF FF FF FF FF 01 00 00 00 48 3A 00 00
0x30    78 0F 00 00 FF FF FF FF 00 00 00 00 00 00 00 00
0x40    18 00 00 00 86 00 00 00 00 00 00 00 19 00 00 00
0x50    74 6F 6F 6C 2E 6C 6E 6B 7C 30 31 32 33 34 35 36
0x60    37 38 39 61 62 63 64 65 66 00 00 00 00 00 00 00
```

1. `90 FF FF FF` 는 부호 있는 정수 -112 입니다. 음수이므로 쓰는 중인 셀이고, 크기는 112바이트입니다.
2. `6E 6B` 는 `nk` 서명입니다. 다음 `20 00` 은 플래그 0x0020 입니다. 키 이름이 ASCII 로 저장됐다는 뜻입니다.
3. 0x08 부터 8바이트 `80 66 9A BA 7F 94 DB 01` 이 마지막 기록 시각입니다. 리틀 엔디언으로 읽으면 0x01DB947FBA9A6680 입니다.
4. 이 값은 1601-01-01 00:00:00 UTC 부터 100나노초 단위로 센 수입니다. 날짜로 바꾸면 2025-03-14 01:23:45 UTC 입니다. 한국 시각으로는 같은 날 10:23:45 입니다.
5. 0x18 의 `00 00 00 00` 은 하위 키 개수 0 입니다. 바로가기 하위 키는 더 내려가지 않습니다.
6. 0x28 의 `01 00 00 00` 은 값 개수 1 입니다. 새 판이라면 이 자리에 4 나 5 가 나옵니다. 0x2C 의 `48 3A 00 00` 은 값 목록의 위치입니다.
7. 0x4C 의 `19 00` 은 키 이름 길이 25바이트입니다. 0x50 부터 25바이트를 읽으면 `tool.lnk|0123456789abcdef` 입니다.

**값 (vk) 셀**

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    D8 FF FF FF 76 6B 0C 00 86 00 00 00 58 3A 00 00
0x10    01 00 00 00 01 00 00 00 53 68 6F 72 74 63 75 74
0x20    50 61 74 68 00 00 00 00
```

1. `D8 FF FF FF` 는 -40 입니다. 쓰는 중인 40바이트 셀입니다.
2. `76 6B` 는 `vk` 서명입니다. `0C 00` 은 값 이름 길이 12바이트입니다.
3. `86 00 00 00` 은 데이터 크기 134바이트입니다. 맨 위 비트가 0 이므로 데이터는 다른 셀에 있습니다.
4. `58 3A 00 00` 이 그 데이터 셀의 위치입니다.
5. `01 00 00 00` 은 값 형식 1, 곧 REG_SZ 입니다. 다음 `01 00` 은 값 이름이 ASCII 라는 플래그입니다.
6. 0x18 부터 12바이트가 값 이름 `ShortcutPath` 입니다.
7. 데이터 셀에는 UTF-16LE 문자열이 있습니다. 134바이트는 66글자와 끝의 널 문자 2바이트입니다. 이 예에서는 `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Tool\Tool.lnk` 입니다.

> 그림 자리: nk 셀의 마지막 기록 시각(0x08)·값 개수(0x28)·키 이름(0x50)과 vk 셀의 데이터 크기·형식·값 이름을 색으로 나눠, 데이터 셀의 UTF-16LE 경로로 이어지는 모습을 보여 주는 그림

### 공개 도구로 한 번

레지스트리 하이브를 읽는 공개 도구면 어느 것이든 이 키를 볼 수 있습니다. Registry Explorer, RegRipper, python-registry, regipy 가 그 예입니다. AmcacheParser, Dissect, Velociraptor 처럼 Amcache 를 따로 풀어 주는 도구도 있습니다.

전용 도구를 쓸 때는 어느 값을 읽는지 확인합니다. 2026년 9월에 공개 소스를 확인한 결과는 다음과 같습니다.

| 도구 | 바로가기 항목에서 읽는 것 |
|---|---|
| AmcacheParser | 하위 키 이름, 첫 번째 값 하나, 하위 키 시각 |
| Dissect (amcache 플러그인) | `ShortcutPath`, 하위 키 시각 |
| Velociraptor (Windows.Forensics.Amcache) | `ShortcutPath`, 하위 키 시각 |
| frnsc-amcache | 값 네 개, 하위 키 시각 |

그래서 새 판 하이브를 앞의 세 도구로만 보면 `ShortcutTargetPath`·`ShortcutProgramId`·`ShortcutAumid` 를 놓칩니다. 첫 번째 값만 읽는 도구는 값 순서에 따라 엉뚱한 값을 보여 줄 수도 있습니다. 하위 키 몇 개는 일반 레지스트리 뷰어로 열어 모든 값을 직접 확인합니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

하이브를 열 때는 `.LOG1`·`.LOG2` 를 함께 가져와 반영합니다. 도구가 로그를 반영했는지도 확인합니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [바로가기 파일 (LNK)](../../file-folder-usage/lnk.md) | `ShortcutPath` 의 LNK 가 아직 있으면 그 안의 대상 경로·대상 파일 시각·볼륨 정보 |
| [$MFT](../../filesystem/mft.md) · [$UsnJrnl](../../filesystem/usnjrnl.md) | LNK 파일이 생기고 지워진 시각. 하위 키 시각이 이보다 뒤인지 |
| [설치 프로그램 항목 (InventoryApplication)](inventoryapplication.md) · [설치 프로그램 (Uninstall)](../../system-account/uninstall.md) | 바로가기를 만든 설치 프로그램과 설치 날짜 |
| [실행 파일 항목 (InventoryApplicationFile)](inventoryapplicationfile.md) | `ShortcutTargetPath` 와 같은 경로의 실행 파일 항목과 SHA-1 |
| [스토어 앱 설치 목록 (AppX·StateRepository)](../../system-account/appx-staterepository.md) | `ShortcutAumid` 가 앱 패키지와 이어지는지 |
| [UserAssist](../userassist.md) · [프리페치](../prefetch/index.md) | 바로가기 대상이 실제로 실행됐는지. UserAssist 는 바로가기를 거친 실행도 따로 적습니다 |
| [점프리스트 (Jump Lists)](../../file-folder-usage/jump-lists.md) | 그 앱으로 연 파일. 앱을 실제로 썼는지 |
| [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 옛 Amcache.hve 의 바로가기 목록. 지금 목록과 비교하면 새로 생기거나 빠진 바로가기를 알 수 있습니다 |

여러 기록을 합쳐 실행을 판단하는 순서는 [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md)에서 다룹니다. Amcache 전체의 해석 함정은 [AmCache 해석 함정](sha1.md)을 봅니다.

## 실습

**공개 표본 하이브.** frnsc-amcache 저장소의 `artifacts` 폴더에 Amcache.hve 표본이 있습니다. `Root\DeviceCensus` 값으로 보면 Windows Server 2016 평가판에서 나온 하이브입니다.

1. `Root\InventoryApplicationShortcut` 아래 하위 키 하나에 값이 몇 개 있습니까? 이 표본은 옛 판과 새 판 가운데 어느 쪽에 가깝습니까?
2. `ShortcutPath` 를 모두 뽑아 폴더별로 나눠 보십시오. 사용자 프로필 폴더는 몇 개가 보입니까?
3. 하위 키 이름의 앞부분이 파일 이름 앞 16자와 모두 맞는지 확인해 보십시오.
4. 하위 키 시각을 분 단위로 묶어 보십시오. 무리가 몇 개입니까? 각 무리에 어느 사용자의 바로가기가 들어 있습니까?
5. 4번의 각 무리와 같은 분에 `InventoryApplicationFile` 항목도 기록돼 있는지 확인해 보십시오.

**직접 만든 Windows 10·11 가상 머신.**

1. 시작 메뉴의 `Programs` 폴더와 바탕 화면에 LNK 를 하나씩 만들고 만든 시각을 적어 둡니다.
2. 작업 스케줄러의 `\Microsoft\Windows\Application Experience\` 폴더에서 호환성 평가 작업을 찾아 실행합니다. 작업 이름은 빌드마다 다를 수 있습니다. Windows 11 빌드 26200 한 대에서는 `Microsoft Compatibility Appraiser Exp` 만 있었습니다.
3. 하이브를 꺼내 두 LNK 가 모두 들어왔는지 봅니다. 하위 키 시각과 LNK 를 만든 시각을 비교합니다.
4. LNK 하나를 지우고 작업을 다시 실행합니다. 하위 키가 빠지는지, 남은 하위 키들의 시각이 다시 쓰였는지 확인합니다.

## 참고 문헌

- Blanche Lagny (ANSSI), "Analysis of the AmCache" v2, 2019 — https://cyber.gouv.fr/documents/632/anssi-coriin_2019-analysis_amcache-v2.pdf
- Eric Zimmerman, "(Am)cache still rules everything around me (part 2 of 1)", binary foray, 2017 — https://binaryforay.blogspot.com/2017/10/amcache-still-rules-everything-around.html
- Cristian Souza (Kaspersky), "AmCache artifact: forensic value and a tool for data extraction", Securelist, 2025 — https://securelist.com/amcache-forensic-artifact/117622/
- Qazeer, InfoSec Notes, "Amcache" — https://notes.qazeer.io/dfir/windows/_artefacts_overview/amcache
- Microsoft Learn, "Required diagnostic events and fields for Windows 11, versions 25H2 and 24H2" (AmiTelCacheChecksum 이벤트) — https://learn.microsoft.com/en-us/windows/privacy/required-diagnostic-events-fields-windows-11-24h2
- ForensicRS, frnsc-amcache (파서 소스와 표본 하이브) — https://github.com/ForensicRS/frnsc-amcache
