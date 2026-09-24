---
title: "탐색기 입력 기록"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1230
---

# 탐색기 입력 기록 (TypedPaths·WordWheelQuery)

## 한 줄 요약

TypedPaths 와 WordWheelQuery 는 사용자 하이브 NTUSER.DAT 의 `Explorer` 키 아래에 있는 입력 목록입니다. TypedPaths 에는 탐색기 주소 표시줄의 경로가, WordWheelQuery 에는 탐색기 검색어가 남는다고 널리 설명됩니다. 두 키 모두 시각은 키마다 하나뿐입니다. 이번에 확인한 자료는 두 키의 뜻을 직접 밝히지 않으므로, 쓰기 전에 대상 버전에서 실험으로 확인합니다.

## 무엇을 기록하나 · 왜 생기나

| 키 | 널리 쓰이는 설명 | 확인한 자료가 밝힌 것 |
|---|---|---|
| TypedPaths | 탐색기 주소 표시줄에 입력한 경로 | 값 이름이 `url1`, `url2` … 인 문자열 목록입니다. plaso 는 인터넷 익스플로러의 TypedURLs 와 같은 틀로 읽습니다 |
| WordWheelQuery | 탐색기 검색 상자에 입력한 검색어 | winreg-kb 는 형식을 "문자열 MRUList 값" 으로 적었습니다 |

다음 설명은 널리 쓰이지만 확인한 자료로는 확정하지 못했습니다. TypedPaths 에는 주소 표시줄에 직접 입력한 경로만 남고 클릭으로 옮겨 간 폴더는 남지 않는다는 설명, `url1` 이 가장 최근 입력이라는 설명과 최대 개수, WordWheelQuery 가 탐색기 검색 상자의 검색어이고 작업 표시줄 검색과 따로 남는다는 설명입니다.

이 설명에 기대 보고서를 쓸 때는 검체와 같은 Windows 버전에서 실험으로 먼저 확인합니다. 실험 방법은 아래 "실습" 에 있습니다.

## 위치와 버전별 차이

### 위치

| 키 | 경로 |
|---|---|
| TypedPaths | `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths` |
| WordWheelQuery | `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery` |

HKCU 는 로그온한 사용자의 NTUSER.DAT 입니다. 하이브 파일의 위치는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

### 자료와 관찰이 다른 점

Windows 11 25H2 PC 한 대에서 본 WordWheelQuery 는 winreg-kb 의 설명과 달랐습니다. (확인 범위: Windows 11 25H2, PC 한 대)

| 항목 | winreg-kb 의 설명 | Windows 11 25H2 관찰 |
|---|---|---|
| 항목 값의 자리 | WordWheelQuery 키 바로 아래 | 키 바로 아래 값은 0개. GUID 이름의 하위 키 `{F9785269-044B-4CA1-8CE5-1D5D31ED6B79}` 아래 |
| 순서 값 | MRUList | MRUListEx (8바이트) |
| 항목 값 | 문자열 | REG_BINARY, UTF-16LE 문자열과 `00 00` |

이 GUID 하위 키가 무엇을 뜻하는지, 어느 버전부터 하위 키로 나뉘었는지는 확인하지 못했습니다. 같은 PC 의 `HKCU\Software\Microsoft\Windows\CurrentVersion\SearchSettings` 에 `IsDeviceSearchHistoryEnabled` 값이 0 으로 있었습니다. 이 값이 WordWheelQuery 기록과 관계있는지는 확인하지 못했습니다.

TypedPaths 는 같은 PC 에서 `url1`~`url13` 이 모두 REG_SZ 였습니다. MRUList 와 MRUListEx 값은 없었습니다. (확인 범위: Windows 11 25H2, PC 한 대)

## 구조

### TypedPaths

| 항목 | 내용 |
|---|---|
| 값 이름 | `url` 뒤에 숫자 (`url1`, `url2` …) |
| 값 형식 | 문자열 (관찰한 PC 에서는 REG_SZ) |
| 순서 값 | 없음 (관찰한 PC) |
| 시각 | 키의 마지막 기록 시각 하나 |

plaso 는 이 키를 `windows_typed_urls` 플러그인으로 읽는데, 인터넷 익스플로러의 `HKCU\Software\Microsoft\Internet Explorer\TypedURLs` 를 읽는 플러그인과 같습니다 ([인터넷 익스플로러·옛 엣지](../browsers/ie-edgehtml/index.md)). 이 플러그인은 값 이름을 정규식 `^url[0-9]+$` (대소문자 무시) 로 고르고, 문자열이면서 비어 있지 않은 값만 씁니다.

순서 값이 없으므로 순서는 값 이름의 번호에서 읽어야 하는데, 번호가 작을수록 최근인지는 확인하지 못했습니다.

### WordWheelQuery

관찰한 PC 의 구조입니다. (확인 범위: Windows 11 25H2, PC 한 대)

| 자리 | 값 | 내용 |
|---|---|---|
| `WordWheelQuery` | 없음 | 키 바로 아래 값은 0개 |
| `WordWheelQuery\{F9785269-…}` | `MRUListEx` | 8바이트 `00 00 00 00 FF FF FF FF`. 항목 1개 (값 `0`) 뒤에 끝 표시 |
| `WordWheelQuery\{F9785269-…}` | `0` | REG_BINARY 10바이트. UTF-16LE 4글자와 `00 00` |

- MRUListEx 를 읽는 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 의 MRU 목록 설명을 따릅니다. 첫 정수가 가장 최근 항목이고, 끝은 -1 입니다.
- plaso 의 일반 문자열 플러그인은 `MRUListEx` 와 값 `0` 이 함께 있는 키를 골라, 이진 값을 UTF-16LE 로 읽습니다. 그래서 GUID 하위 키도 이 플러그인으로 읽힐 수 있습니다. 이 점은 플러그인의 키 선택 규칙에서 나온 추론입니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 사용자 하이브의 목록에 이 문자열이 있습니다 | 그 계정 앞에 실제로 누가 앉아 있었는지 |
| 키가 마지막으로 바뀐 때 (UTC) | 항목마다 언제 입력했는지 |
| WordWheelQuery 에서는 항목끼리의 앞뒤 순서 (MRUListEx) | TypedPaths 항목의 순서 (순서 값이 없고 번호의 뜻이 확인되지 않았습니다) |
| | 입력한 경로가 실제로 있었는지. 그 폴더가 열렸는지 |
| | 검색 결과로 무엇이 나왔는지. 결과를 열었는지 |

기록이 말하는 것은 목록에 이 문자열이 있다는 데까지이고, "직접 입력했다" 는 해석은 위에서 본 대로 확인이 필요합니다. 경로를 입력한 뒤 그 폴더를 실제로 열었는지는 [셸백](shellbags/index.md) 으로 확인합니다.

### 보고서 문장

아래 경로와 시각은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 A 의 NTUSER.DAT 에서 `TypedPaths` 키의 `url1` 값은 `\\fileserver\share` 입니다. 이 키의 마지막 기록 시각은 2025-04-02 06:15:30 UTC 입니다. 같은 Windows 버전의 실험에서 주소 표시줄에 입력한 경로가 이 키에 남는 것을 확인했습니다."
- 쓰면 안 되는 문장: "사용자 A 가 2025-04-02 15:15 에 파일 서버에 접속해 자료를 봤습니다."

## 시각 해석

| 시각 | 어디에 남나 | 무엇을 가리키나 | 형식 |
|---|---|---|---|
| TypedPaths 키의 마지막 기록 시각 | `TypedPaths` 키 | 키가 마지막으로 바뀐 때 | FILETIME, UTC |
| WordWheelQuery 키의 마지막 기록 시각 | `WordWheelQuery` 키와 GUID 하위 키마다 하나씩 | 그 키가 마지막으로 바뀐 때 | FILETIME, UTC |

값마다 시각이 없어서 plaso 도 TypedPaths 기록의 시각으로 키의 마지막 기록 시각 하나만 씁니다. WordWheelQuery 는 상위 키와 GUID 하위 키의 시각을 따로 읽으며, 항목 값이 들어 있는 쪽은 관찰한 PC 에서 GUID 하위 키였습니다.

TypedPaths 는 순서 값이 없어서 키 시각을 어느 값에 이어야 하는지도 정해지지 않습니다. 실험으로 가장 최근 값의 번호를 확인한 뒤에만 이어 읽습니다.
- 키 시각의 성질은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서, FILETIME 계산은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서, 현지 시각 변환은 [시간대 설정](../system-account/time-zone.md) 에서 다룹니다.

## 함정과 한계

1. **WordWheelQuery 키 바로 아래만 봅니다.** 관찰한 PC 에서는 항목이 GUID 하위 키 아래에 있었습니다. 키 바로 아래 값만 읽는 도구는 아무것도 보여 주지 않을 수 있습니다. 하위 키까지 펼쳐 봅니다.
2. **TypedPaths 번호를 확인 없이 순서로 씁니다.** 순서 값이 없고, 번호의 방향은 확인한 자료에 없습니다.
3. **도구가 거른 값을 놓칩니다.** plaso 는 이름이 `url` + 숫자가 아니거나, 문자열이 아니거나, 비어 있는 값을 건너뜁니다. 이런 값이 있는지 원시 키에서 확인합니다.
4. **빈 키를 "쓰지 않았다" 로 읽습니다.** 설정이나 정리 도구가 기록을 막거나 지웠을 수 있습니다. `SearchSettings` 같은 설정 값을 함께 적어 둡니다. 다만 설정과 기록의 관계는 확인하지 못했습니다.
5. **검색어를 행위로 읽습니다.** 검색어가 있다는 것과 그 검색으로 파일을 찾거나 열었다는 것은 다른 일입니다.
6. **다른 입력 기록과 섞습니다.** 실행 창에 입력한 명령은 [실행 창 명령 기록](../execution/runmru.md) 에, 인터넷 익스플로러 주소 입력은 [인터넷 익스플로러·옛 엣지](../browsers/ie-edgehtml/index.md) 에 따로 남습니다. 어느 키에서 나온 값인지 보고서에 적습니다.

### 지우기와 조작

값이나 키를 지우면 하이브 안 빈 공간이나 트랜잭션 로그에 흔적이 남을 수 있고, 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다. 옛 하이브는 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 찾으며, 지금 목록과 비교하면 사라진 항목이 드러납니다. 이 키들을 끄는 정책이나 설정은 확인한 자료에 없습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 관찰한 PC 의 WordWheelQuery 구조를 본떠 만든 예시입니다. 글자 내용은 지어낸 것이고, 실제 검체에서 뽑은 값이 아닙니다.

GUID 하위 키의 `MRUListEx` 값입니다.

```
오프셋  00 01 02 03 04 05 06 07
0x00    00 00 00 00 FF FF FF FF
```

1. 4바이트씩 리틀 엔디언으로 읽으면 0, -1 입니다.
2. 항목은 값 `0` 하나이고, 그 뒤가 끝 표시입니다.

다음은 값 `0` 입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09
0x00    70 00 6C 00 61 00 6E 00 00 00
```

3. 2바이트씩 UTF-16LE 로 읽으면 `plan` 입니다.
4. 0x08 의 `00 00` 이 끝 문자입니다. 4글자 × 2바이트 + 2바이트 = 10바이트로 값 길이와 맞습니다.
5. 상위 키와 GUID 하위 키의 마지막 기록 시각을 따로 적어 둡니다.

TypedPaths 는 값이 REG_SZ 문자열이라 헥스로 풀 부분이 적습니다. 값 이름과 문자열을 모두 적고, 키의 마지막 기록 시각을 함께 적습니다.

### 공개 도구로 한 번

plaso 의 레지스트리 파서는 TypedPaths 를 `windows_typed_urls` 플러그인으로 읽습니다. WordWheelQuery 의 GUID 하위 키는 `mrulistex_string` 플러그인으로 읽힐 수 있습니다. 다른 레지스트리 파서를 써도 됩니다. 도구를 쓸 때는 다음을 확인합니다.

- WordWheelQuery 의 하위 키까지 읽는지 확인합니다.
- TypedPaths 의 값을 어떤 순서로 보여 주는지, 그 순서의 근거가 무엇인지 확인합니다.
- 도구가 건너뛴 값이 없는지 원시 키와 개수를 맞춰 봅니다.
- 시각을 UTC 로 보여 주는지 확인합니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [셸백](shellbags/index.md) | TypedPaths 의 경로를 실제로 열었는지 |
| [윈도 검색 색인 DB](windows-search/index.md) | 검색어에 맞는 파일이 색인에 있었는지 |
| [바로가기 파일 (LNK)](lnk.md) · [점프리스트](jump-lists.md) | 입력하거나 검색한 뒤 그 경로의 파일을 열었는지 |
| [공유 폴더·네트워크 드라이브](../network/network-shares-mapped-drives.md) | 입력한 네트워크 경로가 연결한 공유와 맞는지 |
| [USB 저장장치 흔적](../external-devices/usb-storage-artifacts/index.md) | 입력한 드라이브 문자가 어느 장치였는지 |
| [실행 창 명령 기록](../execution/runmru.md) | 같은 경로를 실행 창으로도 입력했는지 |
| [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 옛 하이브의 목록과 시각 |

## 실습

NIST CFReDS 같은 공개 검체 가운데 사용자 하이브가 든 Windows 이미지를 골라 다음을 풀어 봅니다.

1. 검체의 Windows 버전은 무엇입니까? TypedPaths 에 값이 몇 개 있습니까? 순서 값이 있습니까?
2. WordWheelQuery 키 바로 아래에 값이 있습니까, 하위 키가 있습니까? 하위 키 이름을 적어 봅니다.
3. 두 키의 마지막 기록 시각 (UTC) 을 적어 봅니다. WordWheelQuery 는 상위 키와 하위 키를 따로 적습니다.
4. TypedPaths 의 경로 가운데 셸백에 같은 폴더가 있는 것은 무엇입니까?

두 키의 뜻은 실험용 가상 머신에서 직접 확인합니다. 결과에는 실험한 Windows 버전을 함께 적습니다.

1. 주소 표시줄에 경로 하나를 입력해 이동합니다. 다른 폴더는 클릭으로만 옮겨 갑니다.
2. 새 경로를 하나 더 입력합니다.
3. NTUSER.DAT 를 떠서 TypedPaths 의 값과 번호가 어떻게 바뀌었는지 봅니다. 클릭으로 간 폴더가 남았는지, 새 경로가 `url1` 에 들어갔는지 확인합니다.
4. 탐색기 검색 상자와 작업 표시줄 검색에 서로 다른 검색어를 넣습니다.
5. 다시 하이브를 떠서 WordWheelQuery 어느 키에 어느 검색어가 남았는지 봅니다.

## 참고 문헌

- libyal winreg-kb, "Most recently used (MRU)" — https://raw.githubusercontent.com/libyal/winreg-kb/main/docs/sources/explorer-keys/Most-recently-used.md
- log2timeline plaso, `winreg_plugins/mrulistex.py` — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/winreg_plugins/mrulistex.py
- log2timeline plaso, `winreg_plugins/typedurls.py` — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/winreg_plugins/typedurls.py
