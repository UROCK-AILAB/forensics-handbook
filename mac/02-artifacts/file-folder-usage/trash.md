---
title: "휴지통"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 890
---

# 휴지통 (.Trash)

파인더에서 지운 파일은 곧바로 없어지지 않고 사용자 홈의 숨김 폴더 `~/.Trash/` 로 옮겨 가며, 그 폴더의 `.DS_Store` 에 항목마다 원래 이름(`ptbN`)과 원래 위치(`ptbL`)가 남을 수 있어서 휴지통 속 파일이 어느 폴더에서 왔는지 짚어 볼 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

사용자가 파일을 Dock 의 휴지통으로 끌거나 Command-Delete 를 누르면 파일은 휴지통으로 옮겨 가고, 휴지통에서 끌어내면 끌어 놓은 자리로 옮겨 가고, 파일 › 되돌려 놓기 (Put Back) 를 고르면 원래 자리로 돌아갑니다 [1]. 되돌려 놓기가 되려면 원래 자리를 어딘가에 적어 두어야 하고, 이 정보는 휴지통 폴더의 `.DS_Store` 에 원래 이름(`ptbN`)과 원래 위치(`ptbL`)로 남습니다 [2].

휴지통은 사용자 동작에 따라 비워지기도 하고 저절로 비워지기도 합니다. 동작별로 휴지통에 남는 것은 아래와 같습니다 [1].

| 동작 | 방법 | 휴지통에 남는 것 |
|---|---|---|
| 휴지통으로 옮기기 | Dock 의 휴지통으로 끌기, Command-Delete | 항목이 휴지통 폴더로 옮겨 감 |
| 되돌려 놓기 | 휴지통에서 끌어내기, 파일 › 되돌려 놓기 | 항목이 휴지통에서 나감 |
| 항목 하나만 비우기 | 휴지통을 열고 항목을 Control-클릭 › 즉시 삭제 (Delete Immediately) | 그 항목만 휴지통에서 지워짐 |
| 휴지통 비우기 | 파인더 창 오른쪽 위 "비우기" 단추, 파인더 메뉴 | 휴지통 속 항목이 지워짐 |
| 30일 뒤 자동 제거 | 파인더 설정 › 고급 › "30일 후 휴지통에서 항목 제거" | 30일 지난 항목이 지워짐 |
| iCloud Drive 항목 | 설정과 관계없이 30일 뒤 자동으로 비워짐 | 30일 지난 항목이 지워짐 |

이 표에서 포렌식에 중요한 줄은 항목 하나만 비우기, 30일 자동 제거, iCloud Drive 세 줄입니다. 휴지통 안에서 항목을 하나씩 골라 지울 수 있어서 휴지통에 남은 항목이 휴지통에 들어갔던 항목 전부라고 말할 수 없고, 30일 자동 제거와 iCloud Drive 규칙 때문에 휴지통이 비어 있어도 사용자가 손으로 비웠다고 말할 수 없습니다.

## 위치와 버전별 차이

| 구분 | 위치 | 출처 |
|---|---|---|
| 사용자 휴지통 | `~/.Trash/` | [2][3][4] |
| ForensicArtifacts 이름 | `MacOSUserTrashDirectory` (별칭 `MacOSUserTrash`), 경로 `%%users.homedir%%/.Trash/*`, 설명 "Contents of the user Trash directories." | [3] |
| 원래 위치 기록 | `~/.Trash/.DS_Store` | [2] |

사용자 휴지통은 계정마다 홈 폴더에 하나씩 있어서, 계정이 여럿이면 계정마다 따로 봅니다. 외장 볼륨이나 다른 볼륨에서 지운 파일이 어디에 모이는지는 공개 자료가 없으므로, 그런 볼륨을 조사할 때는 볼륨 루트의 숨김 폴더를 따로 살펴보고 찾은 경로를 확인 범위와 함께 적습니다.

위 사용자 동작은 macOS 10.15 Catalina 부터 macOS 27 까지에 해당합니다 [1]. macOS 26.5.1 에서는 휴지통 속 일부 파일이 `.DS_Store` 에 들어가지 않은 사례가 있습니다 [2]. 버전마다 휴지통 구조가 다르다는 공개 자료는 없습니다.

## 구조

휴지통 폴더에는 지운 항목이 그대로 들어 있고, 옆에 놓인 `.DS_Store` 에 항목 이름별 레코드가 있습니다 [2]. `.DS_Store` 파일 형식은 [폴더 보기 파일 (.DS_Store)](ds-store.md)에서 다루고, 휴지통 레코드에 쓰이는 코드는 아래와 같습니다 [2].

| 코드 | 뜻 |
|---|---|
| `ptbN` | 원래 이름 |
| `ptbL` | 원래 위치 (되돌려 놓기 정보) |
| `lg1S` | 논리 크기 |
| `ph1S` | 물리 크기 |
| `modD` (없으면 `moDD`) | 수정 시각 |

`ptbN`, `ptbL` 은 `.DS_Store` 형식 문서에는 없고 mac_apt 에만 나오는 코드라서 [2], 두 코드의 자료형은 형식 문서로 확인할 수 없습니다.

mac_apt 는 `.DS_Store` 레코드와 휴지통 폴더의 실제 항목(최상위만)을 이름으로 맞추고, 맞은 항목에 파일 시스템의 수정·접근·변경·생성 시각을 붙입니다 [2]. `.DS_Store` 에 레코드가 없는 항목도 목록에 따로 넣고 원래 위치 열은 비워 둡니다 [2].

> 그림 자리: `~/.Trash/` 폴더의 실제 항목 목록과 `~/.Trash/.DS_Store` 레코드를 이름으로 맞추는 그림. 양쪽에 다 있는 항목, 폴더에만 있는 항목(원래 위치 빈칸)을 나눠 보여 줌

## 증거로서 의미

**증명하는 것.** 휴지통 폴더에 있는 항목은 그 계정의 휴지통에 지금 그 항목이 있다는 사실이고, 휴지통에 들어온 파일은 내용까지 그대로 남아 있습니다. `.DS_Store` 에 그 이름의 `ptbL` 이 있으면 되돌려 놓기로 돌아갈 원래 위치가 그 폴더라는 기록이라서 [2], "이 파일이 이 폴더에 있다가 휴지통으로 왔다" 는 흐름을 보여 주는 근거가 됩니다. `ptbN` 은 휴지통 안의 이름과 원래 이름이 다를 때 원래 이름을 알려 줍니다 [2].

**증명하지 못하는 것.** 휴지통으로 옮긴 시각을 곧바로 담는 값은 알려져 있지 않습니다. 누가 옮겼는지도 기록에 없어서, 계정 주인이 옮겼다고 말하려면 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../04-scenarios/activity/user-attribution.md)의 방법으로 다른 기록과 맞춥니다. `.DS_Store` 에 레코드가 없다고 그 항목이 휴지통에 없던 것은 아니고 [2], 휴지통이 비어 있다고 사용자가 지운 파일이 없다는 뜻도 아닙니다. 휴지통 안에서 하나씩 지운 항목은 폴더에서 사라집니다. 파인더를 거치지 않고 지운 파일이 휴지통에 들어오는지, 휴지통을 비운 뒤 `.DS_Store` 레코드가 남는지는 실제 데이터로 확인해야 합니다.

보고서에는 "피조사자가 이 파일을 삭제했다" 가 아니라 "이 계정의 휴지통에 이 파일이 있고, 휴지통 `.DS_Store` 는 원래 위치를 이 폴더로 적고 있다" 처럼 적습니다.

## 시각 해석

휴지통에서 쓰는 시각은 두 종류입니다. 하나는 휴지통 속 항목의 파일 시스템 시각(수정·접근·변경·생성)이고, mac_apt 가 레코드에 붙여 주는 값도 이것입니다 [2]. 다른 하나는 `.DS_Store` 레코드의 `modD`·`moDD` 인데, mac_apt 는 이 값을 리틀엔디언 8바이트 실수로 풀어 2001-01-01 기준 맥 절대 시각으로 읽고 [2], `.DS_Store` 형식 문서는 같은 코드를 1904년 기준 `dutc` 로 적어서 해석이 갈립니다. 두 해석의 차이는 [폴더 보기 파일 (.DS_Store)](ds-store.md)의 시각 해석 절에 정리돼 있습니다.

파일 시스템 시각 가운데 어느 값이 휴지통으로 옮길 때 바뀌는지는 실제 데이터로 확인해야 합니다. 휴지통으로 옮기는 동작은 같은 볼륨 안에서 파일을 다른 폴더로 옮기는 일이라서 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) 같은 다른 흔적에 이름 바꾸기·옮기기로 남을 가능성이 있고, 이 부분도 실제 데이터로 확인해야 합니다. 시각을 UTC 에서 현지 시각으로 옮길 때는 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md)에서 확인한 시간대를 씁니다.

## 함정과 한계

- **`.DS_Store` 만 믿는 경우.** macOS 가 휴지통 폴더의 일부 파일을 `.DS_Store` 에 넣지 않을 때가 있습니다(macOS 26.5.1) [2]. 레코드 목록과 폴더 목록을 둘 다 봅니다.
- **최상위만 맞추는 경우.** mac_apt 는 휴지통 폴더의 최상위 항목만 레코드와 맞춥니다 [2]. 폴더째 지운 경우 그 안의 파일은 따로 살펴봐야 합니다.
- **빈 휴지통을 사용자 행위로 읽는 경우.** 30일 자동 제거 설정이 켜져 있거나 iCloud Drive 에서 지운 항목이면 사용자가 손대지 않아도 휴지통이 비워집니다 [1]. 이 설정이 어느 키로 저장되는지는 공개 자료가 없어서, 설정 상태는 [파인더 설정과 기록 (Finder plist)](finder-plist.md)을 볼 때 함께 살피고 보고서에는 확정하지 못했다고 적습니다.
- **남은 항목을 전부로 읽는 경우.** 휴지통 안의 항목은 하나씩 골라 즉시 삭제할 수 있으므로 [1], 휴지통에 남은 항목만 보고 지운 파일 목록을 만들지 않습니다.
- **다른 볼륨의 휴지통.** 외장 볼륨의 휴지통 위치를 설명한 공개 자료는 없습니다. 사용자 홈의 `.Trash` 만 보면 다른 볼륨에서 지운 파일을 놓칠 수 있습니다.
- **숨김 폴더를 빼고 수집하는 경우.** `.Trash` 와 그 안의 `.DS_Store` 는 이름이 점으로 시작해서, 숨김 파일을 건너뛰는 수집 방법으로는 빠집니다.
- **지우기와 조작.** 휴지통을 비운 뒤의 파일은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)나 [타임 머신 (Time Machine)](../filesystem/time-machine/index.md), 스냅숏에서 찾고, 일부러 지운 정황은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)의 흐름으로 판단합니다.

## 직접 분석해 보기

`~/.Trash/` 폴더 전체를 작업 폴더로 복사하되, 파일 시스템 시각을 보려면 원본 이미지에서 시각을 먼저 뽑아 둡니다.

### 헥스로 한 번

아래 바이트는 `.DS_Store` 형식 문서의 레코드 틀과 mac_apt 의 코드 이름에 맞춰 만든 예시이고, 실제 데이터에서 나온 값이 아닙니다. 휴지통 속 `memo.txt` 에 붙은 `ptbL` 레코드가 시작되는 부분입니다.

```
레코드 앞부분 (예시)
00 00 00 08                                  파일 이름 길이 = 8글자
00 6D 00 65 00 6D 00 6F 00 2E 00 74 00 78 00 74   "memo.txt" (빅엔디언 UTF-16)
70 74 62 4C                                  코드 "ptbL"
..                                           자료형과 값 (아래 설명)

"ptbN" 을 ASCII 바이트로 적은 모양
70 74 62 4E
```

실제 파일에서는 `70 74 62 4C`(`ptbL`)와 `70 74 62 4E`(`ptbN`)를 헥스 검색하면 휴지통 레코드를 바로 짚을 수 있고, 그 앞쪽을 거슬러 올라가면 휴지통 안의 이름이 나옵니다. 두 코드는 형식 문서에 없어서 코드 뒤에 오는 자료형이 정해져 있지 않으므로, 뒤따르는 4글자 자료형 코드를 읽고 [폴더 보기 파일 (.DS_Store)](ds-store.md)의 자료형 표대로 값을 풉니다.

### 공개 도구로 한 번

mac_apt 의 `TRASH` 플러그인을 돌리면 휴지통 폴더 항목과 `.DS_Store` 레코드를 맞춘 표에 원래 이름·원래 위치·크기·시각이 함께 나옵니다 [2]. 도구 결과를 손으로 확인하려면 mac_apt 가 쓰는 파이썬 패키지 `ds_store` 로 두 코드만 추려 봅니다 [2].

```python
import os
from ds_store import DSStore

trash = "Trash_copy"          # 복사해 둔 ~/.Trash 폴더
records = {}
with DSStore.open(os.path.join(trash, ".DS_Store"), "r") as d:
    for e in d:
        if e.code in (b"ptbL", b"ptbN"):
            records.setdefault(e.filename, {})[e.code.decode()] = e.value

for name in sorted(os.listdir(trash)):
    if name == ".DS_Store":
        continue
    info = records.get(name, {})
    print(name, info.get("ptbN", ""), info.get("ptbL", "(레코드 없음)"))
```

`(레코드 없음)` 으로 나온 항목이 앞에서 본 "`.DS_Store` 에 들어가지 않은 파일" 입니다. 코드 값을 바이트로 비교할지 문자열로 비교할지는 패키지 판마다 다를 수 있으니, 결과가 비면 `e.code` 를 먼저 찍어 봅니다.

## 교차 검증

- [폴더 보기 파일 (.DS_Store)](ds-store.md) — 레코드 형식과 시각 해석
- [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) — 파일이 원래 위치에서 휴지통으로 옮겨 간 흔적과 휴지통을 비운 흔적을 찾을 때
- [타임 머신 (Time Machine)](../filesystem/time-machine/index.md), [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md) — 휴지통에서 사라진 파일이 백업이나 스냅숏에 남았는지 볼 때
- [아이클라우드 드라이브 (iCloud Drive·CloudDocs)](../cloud-apps/icloud-drive.md) — 지운 항목이 iCloud Drive 쪽이었는지 볼 때
- [파인더 설정과 기록 (Finder plist)](finder-plist.md) — 원래 위치로 나온 폴더가 최근 폴더나 이동 대상에도 나오는지 볼 때
- [지운 파일의 흔적 찾기 (Deleted File Traces)](../../04-scenarios/activity/deleted-file-traces.md), [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md) — 이 기록을 쓰는 조사 흐름

## 실습

NIST CFReDS 같은 공개 시험 데이터 가운데 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 계정마다 `~/.Trash/` 에 항목이 몇 개 있나요? `.DS_Store` 레코드가 있는 항목과 없는 항목으로 나눠 보세요.
2. `ptbL` 로 나온 원래 위치 가운데 사용자 홈 밖(외장 볼륨, 네트워크 경로)을 가리키는 것이 있나요?
3. `ptbN` 과 휴지통 안의 이름이 다른 항목이 있나요? 있다면 두 이름이 어떻게 다른지 보세요.
4. 휴지통 속 항목의 파일 시스템 시각 네 가지를 뽑고, 같은 파일 이름이 FSEvents 에 언제 나타나는지 비교해 보세요.
5. 휴지통이 비어 있다면 스냅숏이나 백업 속 `.Trash` 에 항목이 남아 있는지 찾아보세요.

## 참고 문헌

1. Apple 지원, "Delete files and folders on Mac" (Mac 사용 설명서) — https://support.apple.com/guide/mac-help/delete-files-and-folders-on-mac-mchlp1093/mac
2. mac_apt `plugins/trash.py` (TRASH 1.0, Yogesh Khatri, 2026) — https://github.com/ydkhatri/mac_apt/blob/master/plugins/trash.py
3. ForensicArtifacts `artifacts/data/macos.yaml` — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/macos.yaml
4. Forensics Wiki, "Mac OS X 10.9 artifacts location" — https://forensics.wiki/mac_os_x_10.9_artifacts_location/
