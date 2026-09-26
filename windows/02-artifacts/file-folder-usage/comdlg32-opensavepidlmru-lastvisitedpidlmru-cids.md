---
title: "열기·저장 대화상자 기록"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1220
---

# 열기·저장 대화상자 기록 (ComDlg32: OpenSavePidlMRU·LastVisitedPidlMRU·CIDSizeMRU)

## 한 줄 요약

공통 파일 대화상자 (Common File Dialog) 로 파일을 열거나 저장하면, 사용자 하이브 NTUSER.DAT 의 `ComDlg32` 키 아래에 MRU 목록이 쌓입니다. OpenSavePidlMRU 에는 고른 파일이 확장자별로 남고, LastVisitedPidlMRU 와 CIDSizeMRU 에는 프로그램 이름으로 보이는 문자열이 남습니다. 시각은 키마다 하나뿐입니다.

## 무엇을 기록하나 · 왜 생기나

공통 파일 대화상자는 여러 앱이 함께 쓰는 "열기"·"다른 이름으로 저장" 창입니다. 이 창으로 파일을 열거나, 저장하거나, 새로 만들면 셸이 앱 대신 `SHAddToRecentDocs` 함수를 부릅니다[3]. 그 결과로 생기는 최근 항목 바로가기와 점프리스트는 [바로가기 파일 (LNK)](lnk.md) 과 [점프리스트](jump-lists.md) 에서 다룹니다.

`ComDlg32` 키를 누가 언제 쓰는지는 공개 문서에 나와 있지 않습니다. 키 이름과, 대화상자를 쓸 때 여러 키의 시각이 함께 바뀌는 모습으로 보아 대화상자를 쓴 일이 계기로 보입니다.

`ComDlg32` 아래 하위 키마다 남는 것은 다음과 같습니다.

| 하위 키 | 순서 값 | 항목 데이터 | 알려 주는 것 |
|---|---|---|---|
| `OpenSavePidlMRU\<확장자>` | MRUListEx | 셸 항목 목록 (Shell Item List) | 대화상자에서 고른 파일의 경로 |
| `LastVisitedPidlMRU` | MRUListEx | 문자열 + 셸 항목 목록 | 프로그램 이름으로 보이는 문자열과 폴더 경로 |
| `CIDSizeMRU` | MRUListEx | 문자열로 시작하는 이진 값 | 프로그램 이름으로 보이는 문자열 |
| `FirstFolder` | MRUListEx | 문자열 | 프로그램 이름으로 보이는 문자열과 경로 |

## 위치와 버전별 차이

모든 하위 키는 `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32` 아래에 있습니다. HKCU 는 로그온한 사용자의 NTUSER.DAT 이므로 계정마다 따로 남습니다.

| 하위 키 | Windows | 형식 | 참고 문헌 |
|---|---|---|---|
| `OpenSaveMRU\<확장자>` | 2000 · XP | 문자열 값 + MRUList | [1] |
| `OpenSavePidlMRU\<확장자>` | Vista 부터 | 셸 항목 목록 값 + MRUListEx | [1] |
| `LastVisitedMRU` | 2000 · XP | 문자열 값 + MRUList | [1] |
| `LastVisitedPidlMRU` | Vista · 7 로 적혀 있음 | 문자열 + 셸 항목 목록 | [1] |
| `CIDSizeMRU` | Vista 로 적혀 있음 | MRUListEx + 숫자 항목. 예시 값은 실행 파일 이름으로 시작합니다 | [1] |
| `FirstFolder` | 버전 표기 없음 | UTF-16LE 문자열 | [1] |

Windows 11 25H2 에서는 다음과 같습니다.

- `ComDlg32` 아래에 `CIDSizeMRU`, `FirstFolder`, `LastVisitedPidlMRU`, `OpenSavePidlMRU` 네 개가 있습니다.
- `OpenSaveMRU` 와 `LastVisitedMRU` 는 없습니다.
- `OpenSavePidlMRU` 아래에는 `*` 키와 확장자별 키 (pdf·xlsx·png 등) 가 있습니다.

공개 자료에 Vista·7 까지만 적힌 키도 Windows 11 에 그대로 있습니다. 확장자 하위 키 이름에는 `exe` 같은 확장자와 함께 `*` 가 있습니다[1]. `*` 키가 확장자와 관계없이 모든 항목을 모은다는 설명은 공개 자료로 확정되지 않았습니다.

## 구조

MRUList·MRUListEx 를 읽는 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 의 MRU 목록 설명을 따릅니다. 셸 항목 목록을 푸는 방법은 [셸 아이템](../../01-foundations/shell-document-formats/shell-item-pidl.md) 에서 다룹니다.

### 순서 값

- MRUList 는 UTF-16LE 글자의 배열입니다. 첫 글자가 가장 최근 항목이고, 끝은 `00 00` 입니다.
- MRUListEx 는 4바이트 리틀 엔디언 정수의 배열입니다. 첫 정수가 가장 최근 항목이고, 끝은 -1 (`FF FF FF FF`) 입니다.
- 값 이름 `0`, `1`, `2` … 는 번호표일 뿐입니다. 순서는 MRUListEx 가 정합니다. 예를 들어 `CIDSizeMRU` 의 MRUListEx 가 01, 02, 07, 00, 06 … 순일 수 있습니다.

MRUListEx 길이는 (항목 수 + 1) × 4 바이트이고 마지막 4바이트는 `FF FF FF FF` 입니다. Windows 11 25H2 의 예는 다음과 같습니다.

| 키 | MRUListEx 길이 | 항목 수 |
|---|---|---|
| `CIDSizeMRU` | 72바이트 | 17 |
| `LastVisitedPidlMRU` | 64바이트 | 15 |
| `OpenSavePidlMRU\pdf` | 84바이트 | 20 |
| `FirstFolder` | 8바이트 | 1 |

한 키가 항목을 몇 개까지 두는지는 공개 자료에 나와 있지 않습니다. pdf 키에 값 `0`~`19` 로 20개가 든 예가 있습니다.

### OpenSavePidlMRU 값

- 값 전체가 셸 항목 목록입니다[2]. plaso 는 `mrulistex_shell_item_list` 플러그인으로 이 키의 하위 키를 읽습니다.
- `OpenSavePidlMRU\pdf` 값은 첫 바이트부터 바로 셸 항목입니다. 첫 셸 항목이 크기 0x0014, 종류 0x1F 인 예가 있습니다.
- 셸 항목 목록을 끝까지 풀면 파일의 경로가 나옵니다.

### LastVisitedPidlMRU 값

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 가변 | 문자열. UTF-16LE 이고 끝 문자 (`00 00`) 까지 들어 있습니다 |
| 문자열 뒤 | 가변 | 경로를 담은 셸 항목 목록. 설정이 안 됐으면 첫 셸 항목이 비어 있습니다 |

- plaso 도 이 키를 "문자열 + 셸 항목 목록" 형식으로 읽습니다[2].
- 앞부분 문자열은 대화상자를 부른 프로그램의 실행 파일 이름이라는 해석이 널리 쓰이지만, 공개 문서로 확정되지 않았습니다.
- 앞부분은 실행 파일 이름 모양의 UTF-16LE 문자열과 `00 00` 이고, 바로 뒤가 셸 항목입니다. 첫 셸 항목이 크기 0x003A, 종류 0x1F 인 예가 있습니다.

### CIDSizeMRU 값

이 키는 Vista 의 키로 알려져 있습니다. 값은 UTF-16LE 실행 파일 이름과 `00 00` 으로 시작하고, 그 뒤는 0 이며, 0x208 (520) 부근부터 0 이 아닌 값이 있습니다[1]. 각 필드의 뜻은 공개 자료에 나와 있지 않습니다. Windows 11 25H2 의 값도 같은 모양입니다.

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 가변 | 실행 파일 이름 모양의 UTF-16LE 문자열과 `00 00` |
| 문자열 뒤 ~ 519 | 가변 | 모두 0 |
| 520 | 72 | 0 이 아닌 값. 뜻은 알려져 있지 않습니다 |

Windows 11 25H2 에서 값은 REG_BINARY 이고 길이는 592바이트입니다. 앞 520바이트는 UTF-16 글자 260개 자리입니다. 뒤 72바이트가 창 크기나 위치라는 해석은 근거가 없으므로 보고서에 이 72바이트를 해석해 쓰지 않습니다.
- plaso 의 일반 문자열 플러그인 (`mrulistex_string`) 은 BagMRU·OpenSavePidlMRU·StreamMRU 를 뺀 키 가운데 `MRUListEx` 와 값 `0` 이 함께 있는 키를 읽습니다. 이진 데이터는 UTF-16LE 로 풉니다[2]. 그래서 CIDSizeMRU 의 앞쪽 이름도 이 플러그인으로 읽힐 것으로 보입니다. 이 점은 플러그인의 키 선택 규칙에서 나온 추론입니다.

### FirstFolder 값

이 키는 UTF-16LE 문자열을 담습니다[1]. Windows 11 25H2 에서는 MRUListEx (8바이트) 와 값 `0` (REG_BINARY 208바이트) 이 있습니다. 값 `0` 은 실행 파일 이름 모양의 UTF-16LE 문자열과 `00 00` 으로 시작하고, 그 뒤에 `C:\` 로 시작하는 UTF-16LE 경로 문자열이 이어집니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 사용자 하이브의 대화상자 기록에 이 경로가 올라간 적이 있습니다 (OpenSavePidlMRU) | 그 계정 앞에 실제로 누가 앉아 있었는지 |
| 같은 키 안에서 항목끼리의 앞뒤 순서 | 두 번째 이후 항목이 각각 언제 들어왔는지 |
| 키가 마지막으로 바뀐 때 (UTC) | 파일을 연 것인지, 저장한 것인지 |
| 프로그램 이름 모양의 문자열과 폴더 경로의 짝 (LastVisitedPidlMRU) | OpenSavePidlMRU 의 어느 파일을 어느 프로그램으로 골랐는지 |
| | 파일이 지금도 있는지. 내용을 읽거나 고쳤는지 |

- 열기와 저장을 구분하지 못하는 이유가 있습니다. 대화상자로 열기·저장·새로 만들기를 하면 셸이 모두 같은 함수를 부릅니다[3]. 값 안에도 열기와 저장을 가르는 필드가 알려져 있지 않습니다.
- OpenSavePidlMRU 값에는 프로그램 이름이 없습니다. LastVisitedPidlMRU 항목과 짝을 맞추는 규칙은 문서화돼 있지 않습니다. 짝을 맞출 때는 아래 "시각 해석" 의 방법을 쓰고 추정이라고 밝힙니다.
- 앱이 공통 대화상자를 쓰지 않으면 이 키에 기록이 없습니다. 목록에 없다고 파일을 다루지 않았다고 단정하지 않습니다.
- LastVisitedPidlMRU 나 CIDSizeMRU 의 프로그램 이름은 실행 기록이 아닙니다. 실행 여부는 따로 확인합니다.

### 보고서 문장

아래 이름과 시각은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 A 의 NTUSER.DAT 에서 `OpenSavePidlMRU` 의 pdf 확장자 하위 키를 보면, MRUListEx 첫 항목이 `E:\Work\plan.pdf` 입니다. 이 키의 마지막 기록 시각은 2025-04-02 06:15:30 UTC 입니다. 같은 초에 `LastVisitedPidlMRU` 키도 바뀌었고, 그 첫 항목은 `editor.exe` 와 `E:\Work` 입니다."
- 쓰면 안 되는 문장: "사용자 A 가 2025-04-02 15:15 에 editor.exe 로 USB 의 plan.pdf 를 열었습니다."

## 시각 해석

| 시각 | 어디에 남나 | 무엇을 가리키나 | 형식 |
|---|---|---|---|
| 키의 마지막 기록 시각 | `ComDlg32` 아래 키와 하위 키마다 하나씩 | 그 키가 마지막으로 바뀐 때 | FILETIME, UTC |

- 항목 값에는 시각이 없습니다. 이 키들에서 쓸 수 있는 시각은 키의 마지막 기록 시각뿐입니다[2].
- 키 시각은 첫 항목에만 조건부로 이어집니다. 두 번째 이후 항목에는 붙이지 않습니다.
- `OpenSavePidlMRU\*`, `LastVisitedPidlMRU`, `CIDSizeMRU` 세 키의 마지막 기록 시각이 초까지 같을 수 있습니다. 대화상자를 한 번 쓰면 여러 키가 함께 바뀌는 것으로 보입니다.
- 그래서 시각이 같은 키들의 첫 항목끼리 짝을 지어 "어느 프로그램으로 어느 파일을" 을 추정할 수 있습니다. 첫 항목에만 쓸 수 있고, 추정이라고 밝힙니다.
- 상위 키 `OpenSavePidlMRU` 와 하위 키 `OpenSavePidlMRU\pdf` 의 시각은 서로 다를 수 있습니다. 상위 키 시각은 하위 키가 바뀔 때 함께 움직이지 않습니다. 시각은 항목이 들어 있는 하위 키에서 읽습니다.
- 키 시각의 성질은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서, FILETIME 계산은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서, 현지 시각 변환은 [시간대 설정](../system-account/time-zone.md) 에서 다룹니다.

## 함정과 한계

1. **값 이름의 번호를 순서로 읽습니다.** 순서는 MRUListEx 만 정합니다.
2. **상위 키 시각을 씁니다.** `OpenSavePidlMRU` 상위 키의 시각은 하위 키의 사건 시각이 아닙니다.
3. **키 시각을 모든 항목에 붙입니다.** 키 시각은 첫 항목에만 이어집니다.
4. **LastVisitedPidlMRU 의 문자열을 실행 파일 이름으로 단정합니다.** 널리 쓰는 설명이지만 공개 문서로 확정되지 않았습니다. 실행 흔적과 맞춰 본 뒤에 씁니다.
5. **CIDSizeMRU 의 뒤 72바이트를 해석합니다.** 뜻이 알려져 있지 않습니다.
6. **RecentDocs 가 비었으니 대화상자 기록도 없다고 봅니다.** `Start_TrackDocs` 값이 0 이고 [최근 문서](recentdocs.md) 가 비어 있어도 ComDlg32 키는 갱신될 수 있습니다.
7. **셸 항목 목록 풀이를 도구 하나에 맡깁니다.** 값 한두 개는 원시 바이트로 풀어 도구가 보여 준 경로와 맞춰 봅니다.
8. **알려지지 않은 점을 사실로 씁니다.** 다음은 공개 자료로 정해지지 않았습니다.
   - `*` 키의 정확한 뜻
   - 한 키가 두는 최대 항목 수
   - `LastVisitedPidlMRULegacy` 라는 키가 있는지, 있다면 어느 버전인지
   - ComDlg32 키를 쓰는 주체와 시점

### 지우기와 조작

- 이 키들을 지우거나 끄는 정책은 공개 자료에 나와 있지 않습니다.
- 값이나 키를 지우면 하이브 안 빈 공간이나 트랜잭션 로그에 흔적이 남을 수 있습니다. 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.
- MRUListEx 가 가리키는 번호와 실제 값이 맞지 않으면 원시 바이트를 직접 봅니다. plaso 는 -1 에서 읽기를 멈추므로 끝 표시 뒤에 남은 번호를 보여 주지 않습니다. MRUListEx 가 가리키는 값이 없으면 경고를 남깁니다.
- 옛 하이브는 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 찾습니다. 지금 목록과 비교하면 사라진 항목이 드러납니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 형식 설명[1]을 따라 만든 예시입니다. 실제 데이터에서 뽑은 값이 아닙니다. 셸 항목의 크기와 종류 값은 Windows 11 25H2 의 모양을 본떴습니다.

먼저 `LastVisitedPidlMRU` 의 `MRUListEx` 값입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    01 00 00 00 02 00 00 00 00 00 00 00 FF FF FF FF
```

1. 4바이트씩 리틀 엔디언으로 읽으면 1, 2, 0, -1 입니다.
2. 가장 최근 항목은 값 `1` 입니다. 항목은 3개이고, 길이는 (3 + 1) × 4 = 16바이트입니다.

다음은 값 `1` 의 앞부분입니다. `..` 은 셸 항목이라 줄인 바이트입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    65 00 64 00 69 00 74 00 6F 00 72 00 2E 00 65 00
0x10    78 00 65 00 00 00 3A 00 1F .. .. .. .. .. .. ..
```

3. 0x00 부터 UTF-16LE 로 읽으면 `editor.exe` 입니다.
4. 0x14 의 `00 00` 이 문자열의 끝입니다.
5. 0x16 부터 셸 항목 목록입니다. 첫 셸 항목의 크기는 `3A 00` 곧 0x003A (58바이트) 이고, 종류 값은 0x18 의 `1F` 입니다.
6. 첫 셸 항목은 0x16 부터 58바이트이므로 다음 셸 항목은 0x50 에서 시작합니다. 이어지는 풀이는 [셸 아이템](../../01-foundations/shell-document-formats/shell-item-pidl.md) 페이지를 따릅니다.
7. `OpenSavePidlMRU` 의 값은 이 문자열 부분 없이 오프셋 0 부터 셸 항목 목록입니다.
8. `LastVisitedPidlMRU`, `CIDSizeMRU`, `OpenSavePidlMRU\*` 키의 마지막 기록 시각을 나란히 적어 봅니다. 시각이 같은 키가 있는지 봅니다.

### 공개 도구로 한 번

plaso 의 레지스트리 파서가 이 키들을 읽습니다.

- `OpenSavePidlMRU` 의 하위 키는 `mrulistex_shell_item_list` 플러그인이 셸 항목 목록으로 읽습니다.
- `LastVisitedPidlMRU` 는 "문자열 + 셸 항목 목록" 형식으로 읽습니다.
- `CIDSizeMRU` 같은 나머지 MRUListEx 키는 `mrulistex_string` 플러그인이 UTF-16LE 로 읽는 것으로 보입니다.

다른 레지스트리 파서를 써도 됩니다. 도구를 쓸 때는 다음을 확인합니다.

- `*` 키와 확장자 키를 따로 보여 주는지 확인합니다.
- 키 시각을 상위 키에서 가져오는지, 하위 키에서 가져오는지 확인합니다.
- 셸 항목 목록에서 푼 경로가 원시 바이트와 맞는지 한두 개 확인합니다.
- 시각을 UTC 로 보여 주는지 확인합니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [최근 문서](recentdocs.md) | 같은 파일 이름이 확장자별 목록에 있는지 |
| [바로가기 파일 (LNK)](lnk.md) · [점프리스트](jump-lists.md) | 같은 대화상자 사용으로 생긴 바로가기와 앱별 목록. 점프리스트는 어느 앱인지 알려 줍니다 |
| [셸백](shellbags/index.md) | 대화상자로 드나든 폴더 |
| [프리페치](../execution/prefetch/index.md) · [UserAssist](../execution/userassist.md) · [BAM·DAM](../execution/background-activity-moderator.md) | LastVisitedPidlMRU 의 프로그램이 그 무렵 실제로 실행됐는지 |
| [마스터 파일 테이블](../filesystem/mft.md) · [USN 변경 저널](../filesystem/usnjrnl.md) | 저장이라면 그 시각 무렵 파일이 생기거나 바뀐 기록 |
| [USB 저장장치 흔적](../external-devices/usb-storage-artifacts/index.md) · [공유 폴더·네트워크 드라이브](../network/network-shares-mapped-drives.md) | 경로의 드라이브 문자나 네트워크 경로가 어느 장치·공유인지 |
| [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 옛 하이브의 목록과 시각 |

여러 기록을 합쳐 읽는 순서는 [이 파일을 누가 언제 열었나](../../04-scenarios/activity/file-access.md) 와 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 실습 이미지 가운데 사용자 하이브가 든 Windows 이미지를 골라 다음을 풀어 봅니다.

1. 이미지의 Windows 버전은 무엇입니까? `ComDlg32` 아래에 `OpenSaveMRU` 계열이 있습니까, `OpenSavePidlMRU` 계열이 있습니까?
2. `OpenSavePidlMRU` 아래 확장자 키를 모두 적어 봅니다. 각 키의 첫 항목 경로와 마지막 기록 시각 (UTC) 을 표로 만듭니다.
3. 경로 가운데 이동식 드라이브나 네트워크 경로를 가리키는 것이 있습니까?
4. `LastVisitedPidlMRU` 의 항목을 순서대로 풀어 문자열과 폴더를 짝지어 적습니다.
5. 시각이 초까지 같은 키가 있습니까? 있다면 그 키들의 첫 항목끼리 짝을 지어 봅니다. 이 짝이 추정인 이유를 한 줄로 적습니다.
6. `CIDSizeMRU` 값 하나의 길이와 앞쪽 문자열을 확인합니다. 위에서 본 592바이트 틀과 같습니까?

실험용 가상 머신이 있으면 앱 두 개로 파일을 하나씩 열고 하나씩 저장해 봅니다. 동작마다 NTUSER.DAT 를 떠서 어느 키의 시각과 순서가 바뀌는지 비교합니다. 결과에는 실험한 Windows 버전을 함께 적습니다.

## 참고 문헌

- libyal winreg-kb, "Most recently used (MRU)" — https://raw.githubusercontent.com/libyal/winreg-kb/main/docs/sources/explorer-keys/Most-recently-used.md
- log2timeline plaso, `winreg_plugins/mrulistex.py` — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/winreg_plugins/mrulistex.py
- Microsoft Learn, "SHAddToRecentDocs function (shlobj_core.h)" — https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shaddtorecentdocs
