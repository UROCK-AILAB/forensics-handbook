---
title: "파인더 설정과 기록"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 870
---

# 파인더 설정과 기록 (Finder plist)

사용자마다 하나씩 있는 `~/Library/Preferences/com.apple.finder.plist` 에는 파인더가 다음에 다시 쓰려고 적어 둔 최근 폴더, "폴더로 이동" 입력, 이동·복사 대상, 서버 주소, 여러 항목 이름 바꾸기 설정이 들어 있어서, 그 계정이 파인더로 어디를 드나들고 무엇을 했는지 짚어 보는 단서가 됩니다.

## 무엇을 기록하나 · 왜 생기나

파인더 설정 파일 (Finder plist)은 이름 그대로 파인더의 설정 파일이지만, 포렌식에서는 설정값보다 사용자가 최근에 한 동작이 남는 키가 더 쓸모 있습니다. 이 파일에는 최근 폴더(`FXRecentFolders`), "폴더로 이동" 입력칸의 마지막 값과 입력 기록(`GoToField`, `GoToFieldHistory`), 최근 이동·복사 대상(`RecentMoveAndCopyDestinations`), "서버에 연결"에 마지막으로 쓴 주소(`FXConnectToLastURL`), 열기·저장 창의 마지막 폴더가 남습니다 [1]. 바탕화면에 나타났던 볼륨의 아이콘 위치(`FXDesktopVolumePositions`), 최근 파일 검색(`SGTRecentFileSearches`), 여러 항목 이름 바꾸기의 마지막 설정(`BulkRename` 으로 시작하는 키)도 함께 남습니다 [1].

이 키들은 사용자가 파인더에서 무언가를 했을 때 파인더가 적어 두는 값이라서, 앱 실행 기록이나 파일 시스템 기록과는 다른 쪽에서 사용자 동작을 보여 줍니다. 최근 폴더·서버·열기 창 쪽 키는 [최근 항목 (Shared File Lists)](recent-items/index.md)에서 최근 항목 기록과 함께 자세히 다루고, 이 페이지는 파일 전체를 한 번에 살펴보는 길잡이와 다른 페이지에서 다루지 않는 이름 바꾸기 키를 중심으로 씁니다.

휴지통 30일 자동 비우기도 파인더 설정 › 고급의 "30일 후 휴지통에서 항목 제거(Remove items from the Trash after 30 days)"에서 켜고 끕니다 [3]. 이 설정이 휴지통 해석에 어떤 영향을 주는지는 [휴지통 (.Trash)](trash.md)에서 다룹니다.

## 위치와 버전별 차이

파인더 기록은 한 파일에 다 모여 있지 않고 아래 세 파일에 나뉘어 있습니다 [1].

| 파일 | 위치 | 이 페이지와 관련된 키 |
|---|---|---|
| 파인더 설정 | `~/Library/Preferences/com.apple.finder.plist` | 아래 "구조" 표의 키 전부 |
| 전역 설정 | `~/Library/Preferences/.GlobalPreferences.plist` | `SGTRecentFileSearches`, `NSNavRecentPlaces` |
| 사이드바 목록 | `~/Library/Preferences/com.apple.sidebarlists.plist` | `systemitems` › `VolumesList`, `favoriteservers` › `CustomListItems` |

세 파일 모두 사용자 홈 아래에 있어서, 계정이 여럿이면 계정마다 따로 읽습니다. ForensicArtifacts 정의(`macos.yaml`)에는 `com.apple.finder.plist` 를 따로 가리키는 항목이 없으므로 [2], 그 정의로 수집 목록을 짤 때는 이 파일을 따로 챙깁니다.

키마다 어느 macOS 버전부터 있고 어느 버전에서 없어졌는지는 실제 데이터로 확인해야 합니다. 알려진 버전 차이는 `FXRecentFolders` 항목 하나입니다. 옛 항목에는 `file-bookmark`(북마크 데이터) 대신 `file-data` 안에 `_CFURLAliasData`(별칭 데이터)가 들어 있고, macOS 10.9 미만에서 만든 항목으로 보는 해석이 있습니다 [1].

## 구조

파일은 속성 목록 파일이라서 최상위 사전(dict)에 키가 나란히 들어 있고, 파일 형식 자체는 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에서 다룹니다. 주요 키를 기록하는 동작별로 묶으면 아래와 같습니다 [1].

| 키 | 기록하는 동작 | 값의 모양 |
|---|---|---|
| `FXRecentFolders` | 파인더 "최근 폴더" | 배열. 항목마다 `name` 과 `file-bookmark` |
| `GoToField` | "폴더로 이동" 입력칸의 마지막 값 | 값 하나 |
| `GoToFieldHistory` | "폴더로 이동" 입력 기록 | 문자열 배열 |
| `RecentMoveAndCopyDestinations` | 최근 이동·복사 대상 | 문자열 배열 |
| `FXConnectToLastURL` | "서버에 연결"에 마지막으로 쓴 주소 | 값 하나 |
| `NSNavLastRootDirectory`, `NSNavLastCurrentDirectory` | 열기·저장 창의 마지막 폴더 | 값 하나씩 |
| `FXDesktopVolumePositions` | 바탕화면에 나타났던 볼륨의 아이콘 위치 | 볼륨마다 키 하나. 키 이름이 `<볼륨이름>_<16진 숫자>` 형식 |
| `SGTRecentFileSearches` | 최근 파일 검색 | 배열. 항목마다 `name`, `type` |
| `BulkRename` 으로 시작하는 키 | 여러 항목 이름 바꾸기의 마지막 설정 | 아래 표 |

`file-bookmark` 안의 경로와 볼륨 정보는 [파일 참조 데이터 (Alias·Bookmark)](../../01-foundations/value-decoding/alias-bookmark.md)의 방법으로 풉니다.

### 여러 항목 이름 바꾸기 키

파인더에서 여러 파일을 골라 한꺼번에 이름을 바꾸면, 그때 넣은 설정이 `BulkRename` 으로 시작하는 키에 남습니다 [1]. 키는 아래 여덟 개이고, 오른쪽 풀이는 키 이름으로 짐작한 뜻입니다.

| 키 | 키 이름으로 짐작한 뜻 |
|---|---|
| `BulkRenameName` | 새 이름에 쓴 글자 |
| `BulkRenameAddNumberTo` | 번호를 붙인 자리 |
| `BulkRenameAddTextText` | 덧붙인 글자 |
| `BulkRenameAddTextTo` | 글자를 덧붙인 자리 |
| `BulkRenamePlaceNumberAt` | 번호를 둔 자리 |
| `BulkRenameStartIndex` | 번호를 시작한 수 |
| `BulkRenameFindText` | 찾을 글자 |
| `BulkRenameReplaceText` | 바꿔 넣을 글자 |

`BulkRenameFindText` 와 `BulkRenameReplaceText` 에 남은 글자는 사용자가 파일 이름에서 무엇을 지우거나 바꾸려 했는지 보여 줄 수 있어서, 파일 이름을 한꺼번에 바꿔 자료를 숨기려 한 정황을 따질 때 먼저 봅니다.

### 바탕화면 볼륨 키

`FXDesktopVolumePositions` 는 볼륨마다 키가 하나라서 키 이름 앞쪽만 모아도 이 계정의 바탕화면에 나타났던 볼륨 이름 목록이 나옵니다 [1]. mac_apt 는 키 이름에서 마지막 `_` 뒤 값을 16진 실수 표기(`float.fromhex`)로 읽어 정수로 바꾼 뒤 2001-01-01 기준 맥 절대 시각으로 읽고 "볼륨 생성 날짜(VolumeCreationDate)" 라고 적습니다 [1]. 이 값을 볼륨 생성 시각으로 보는 것은 mac_apt 의 해석이라서, 보고서에 쓸 때는 도구의 해석이라고 함께 밝힙니다.

## 증거로서 의미

**증명하는 것.** 키에 값이 있으면 그 계정의 파인더가 어느 때인가 그 값을 적어 두었다는 뜻입니다. `GoToFieldHistory` 에 있는 경로는 "폴더로 이동" 에 그 경로를 넣은 기록이고, `RecentMoveAndCopyDestinations` 의 경로는 이동이나 복사 대상으로 쓰인 폴더이며, `FXConnectToLastURL` 은 "서버에 연결" 에 마지막으로 넣은 주소입니다 [1]. `SGTRecentFileSearches` 의 `name` 은 파인더에서 검색한 글자이고, `BulkRename` 키는 마지막으로 한 여러 항목 이름 바꾸기의 설정입니다 [1].

**증명하지 못하는 것.** 이 키들에는 항목마다 시각이 없어서, 그 동작을 언제 했는지는 이 파일만으로 말할 수 없습니다. 이동·복사 대상 경로는 어떤 파일을 옮겼는지 알려 주지 않고, 이름 바꾸기 키는 어느 파일의 이름을 바꿨는지 알려 주지 않습니다. 동작이 끝까지 성공했는지, 그 경로가 지금도 있는지, 누가 키보드 앞에 있었는지도 이 파일로는 알 수 없습니다. 값이 하나뿐인 키(`GoToField`, `FXConnectToLastURL`, `BulkRename` 키)는 마지막 값만 남으므로 그전 값은 다른 기록에서 찾아야 합니다.

보고서에는 "피조사자가 이 폴더로 파일을 복사했다" 가 아니라 "이 계정의 파인더 설정 파일에 이 경로가 최근 이동·복사 대상으로 남아 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

위 키 가운데 시각으로 풀리는 값은 `FXDesktopVolumePositions` 키 이름 뒤쪽의 16진 값 하나이고, 앞 절에서 본 대로 이 값을 볼륨 생성 시각으로 보는 해석은 도구의 해석입니다 [1]. 2001-01-01 기준 맥 절대 시각을 UTC 로 바꾸는 방법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따르고, `file-bookmark` 안에 든 날짜는 [파일 참조 데이터 (Alias·Bookmark)](../../01-foundations/value-decoding/alias-bookmark.md)에서 다룹니다.

그 밖의 키에는 시각이 없어서, 파일 시스템이 적은 이 plist 파일의 수정 시각을 함께 봅니다. 다만 수정 시각은 파일 전체를 마지막으로 쓴 때일 뿐이라서 어느 키가 그때 바뀌었는지는 알려 주지 않습니다.

## 함정과 한계

- **한 파일만 읽는 경우.** 최근 파일 검색(`SGTRecentFileSearches`)은 `.GlobalPreferences.plist` 에도 있고, 볼륨·서버 목록은 사이드바 목록 파일에도 있어서 [1], 파인더 설정 파일 하나만 보면 기록이 빠집니다.
- **배열 순서를 시간순으로 읽는 경우.** 배열 키의 항목 순서가 최근 순서인지는 파일만으로 알 수 없습니다. 순서만 보고 "먼저 갔다·나중에 갔다" 를 말하지 않습니다.
- **옛 모양의 최근 폴더 항목.** `file-bookmark` 가 없는 항목은 별칭 데이터로 읽어야 해서 [1], 북마크만 푸는 도구는 이런 항목을 건너뛸 수 있습니다.
- **도구의 해석을 사실처럼 옮기는 경우.** 볼륨 키의 16진 값을 "볼륨 생성 시각" 이라고 단정하지 않습니다 [1].
- **지우기와 조작.** 설정 파일을 지우거나 값을 바꾸면 이 기록은 사라지거나 달라지고, 파일 안에는 그런 일이 있었다는 표시가 따로 남지 않습니다. 키가 비어 있다고 그 동작을 하지 않았다고 말할 수 없으며, 예전 값은 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md)의 방법으로 스냅숏이나 백업 속 같은 파일과 비교해 찾습니다.

## 직접 분석해 보기

원본을 바로 열지 말고 `com.apple.finder.plist`, `.GlobalPreferences.plist`, `com.apple.sidebarlists.plist` 를 작업 폴더에 복사한 뒤 사본을 엽니다.

### 헥스로 한 번

바이너리 plist 의 키 이름은 ASCII 글자로 들어 있어서, 헥스 편집기에서 글자를 검색하면 키가 어디쯤 있는지 먼저 짚을 수 있습니다. 아래는 키 이름을 ASCII 로 적은 모양이고, 특정 파일에서 나온 바이트가 아니라 글자를 바이트로 옮겨 적은 예시입니다.

```
"GoToFieldHistory" 를 ASCII 바이트로 적은 모양 (예시)
47 6F 54 6F 46 69 65 6C 64 48 69 73 74 6F 72 79
G  o  T  o  F  i  e  l  d  H  i  s  t  o  r  y

"BulkRename" 을 ASCII 바이트로 적은 모양 (예시)
42 75 6C 6B 52 65 6E 61 6D 65
B  u  l  k  R  e  n  a  m  e
```

바이너리 plist 는 키와 값을 따로 떨어진 객체로 두고 번호로 잇기 때문에, 키 이름을 찾은 뒤 값까지 가려면 오프셋 표를 따라가야 합니다. 이 과정은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)의 순서대로 밟습니다. 검색에 `BulkRename` 을 넣으면 여덟 키가 모두 걸리므로, 이름 바꾸기 기록이 있는지 한 번에 가려낼 수 있습니다.

### 공개 도구로 한 번

맥에서는 `plutil -p com.apple.finder.plist` 로 사본 전체를 사람이 읽는 모양으로 볼 수 있고, 다른 운영체제에서는 파이썬 표준 라이브러리 `plistlib` 로 필요한 키만 뽑습니다.

```python
import plistlib

with open("com.apple.finder.plist", "rb") as f:
    p = plistlib.load(f)

for key in ("GoToField", "GoToFieldHistory", "RecentMoveAndCopyDestinations",
            "FXConnectToLastURL", "NSNavLastRootDirectory",
            "NSNavLastCurrentDirectory", "SGTRecentFileSearches"):
    if key in p:
        print(key, "=", p[key])

# 여러 항목 이름 바꾸기 설정
for key, value in p.items():
    if key.startswith("BulkRename"):
        print(key, "=", value)

# 바탕화면에 나타났던 볼륨 이름 (키 이름의 마지막 "_" 앞부분)
for key in p.get("FXDesktopVolumePositions", {}):
    print("volume:", key.rsplit("_", 1)[0])
```

mac_apt 의 `RECENTITEMS` 플러그인을 돌리면 세 파일의 키를 한 표로 모아 주고 `file-bookmark` 도 풀어 주므로 [1], 손으로 뽑은 값과 도구 결과를 맞춰 보는 데 씁니다.

## 교차 검증

- [최근 항목 (Shared File Lists)](recent-items/index.md) — 최근 폴더·서버·열기 창 기록을 최근 항목 목록과 함께 볼 때
- [폴더 보기 파일 (.DS_Store)](ds-store.md) — 이동 대상이나 최근 폴더로 나온 폴더를 파인더가 실제로 다뤘는지 볼 때
- [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) — 이동·복사·이름 바꾸기가 언제 일어났는지 시각을 찾을 때
- [USB 저장 장치 (USB Storage)](../external-devices/usb/index.md) — 바탕화면 볼륨 이름을 외장 장치 기록과 맞출 때
- [공유 폴더 연결 기록 (SMB·AFP)](../network/network-shares.md) — `FXConnectToLastURL` 의 서버 주소를 연결 기록과 맞출 때
- [스포트라이트 (Spotlight)](spotlight/index.md) — 최근 검색 글자를 스포트라이트 쪽 기록과 비교할 때
- [이 파일을 누가 언제 열었나 (File Access)](../../04-scenarios/activity/file-access.md), [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) — 이 파일을 쓰는 조사 흐름

## 실습

NIST CFReDS 같은 공개 시험 데이터 가운데 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 계정마다 `com.apple.finder.plist` 가 있나요? 있다면 이 페이지 "구조" 표의 키 가운데 어느 것이 들어 있나요?
2. `GoToFieldHistory` 와 `RecentMoveAndCopyDestinations` 에 나온 경로 가운데 사용자 홈 밖(외장 볼륨, 네트워크 경로)을 가리키는 것은 무엇인가요?
3. `FXDesktopVolumePositions` 의 볼륨 이름 목록을 뽑고, 같은 이름이 USB 기록이나 사이드바 목록 파일에도 있는지 확인해 보세요.
4. `SGTRecentFileSearches` 를 `com.apple.finder.plist` 와 `.GlobalPreferences.plist` 에서 각각 읽어 보고, 두 값이 같은지 다른지 비교해 보세요.
5. `BulkRename` 키가 있다면 `BulkRenameReplaceText` 나 `BulkRenameName` 에 남은 글자를 담은 파일 이름이 FSEvents 이름 바꾸기 기록에 있는지 찾아보세요.

## 참고 문헌

1. mac_apt `plugins/recentitems.py` (RECENTITEMS 1.5, Yogesh Khatri) — https://github.com/ydkhatri/mac_apt/blob/master/plugins/recentitems.py
2. ForensicArtifacts `artifacts/data/macos.yaml` — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/macos.yaml
3. Apple 지원, "Delete files and folders on Mac" (Mac 사용 설명서) — https://support.apple.com/guide/mac-help/delete-files-and-folders-on-mac-mchlp1093/mac
