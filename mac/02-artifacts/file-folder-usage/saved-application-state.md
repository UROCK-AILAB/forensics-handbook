---
title: "앱 저장 상태"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 910
---

# 앱 저장 상태 (Saved Application State)

macOS 앱은 다음에 다시 열 때 창을 되살리려고 앱마다 `.savedState` 폴더에 창 목록과 창 내용을 저장하고, 여기에 창 제목·열려 있던 폴더·열려 있던 파일이 남아서 어떤 앱으로 무엇을 보고 있었는지 알려 줍니다.

## 무엇을 기록하나 · 왜 생기나

앱을 끄고 다시 열면 전에 열려 있던 창이 그대로 다시 열리는데, 이 동작에 쓰는 창 정보가 앱별 `.savedState` 폴더에 남습니다. 시스템 설정 › 데스크탑 및 Dock 의 "앱 종료 시 윈도우 닫기 (Close windows when quitting an application)" 를 켜면 앱을 끌 때 창을 닫고, 다음에 앱을 열 때 창이 자동으로 다시 열리지 않습니다 [2].

폴더 안의 `windows.plist` 에는 창마다 창 제목과 창 번호가 들어 있어서, 문서 이름이나 웹 페이지 제목이 창 제목으로 남을 수 있습니다 [1]. 함께 놓인 `data.data` 는 창 내용을 암호화해 담은 파일이고, 이를 풀면 파인더 창이 가리키던 폴더나 미리보기가 열어 둔 파일이 나옵니다 [1].

## 위치와 버전별 차이

상태 폴더는 사용자마다 아래 두 곳에 있습니다 [1].

```
~/Library/Saved Application State/<번들ID>.savedState/
~/Library/Containers/<컨테이너>/Data/Library/Saved Application State/<번들ID>.savedState/
```

두 번째 경로는 샌드박스 앱의 컨테이너 안쪽입니다. 폴더 이름의 번들 ID 로 어느 앱의 상태인지 알 수 있고, 번들 ID 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md)를 봅니다. `Saved Application State` 안의 항목이 폴더가 아니라 심볼릭 링크일 때가 있고, 이때는 링크가 가리키는 폴더를 따라가서 읽습니다 [1].

버전별 차이는 공개 자료가 없습니다. Catalina 이후에 키 이름이나 암호화 방식이 바뀌었는지, 창 되살리기 설정이 어느 plist 키에 저장되는지는 검체에서 확인하고, 아래 구조와 다른 모습이 나오면 macOS 버전과 함께 기록합니다.

## 구조

폴더 안에는 `windows.plist` 와 `data.data` 가 있습니다 [1].

### windows.plist

창마다 사전(dict) 하나가 들어간 배열이고, plist 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)을 따릅니다. 주요 키는 아래와 같습니다 [1].

| 키 | 뜻 |
|---|---|
| `NSTitle` | 창 제목. 문서 이름이나 웹 페이지 제목이 나올 수 있음 |
| `NSWindowID` | 창 번호 |
| `NSDataKey` | 이 창의 `data.data` 레코드를 푸는 AES 키 |
| `NSDockMenu` | Dock 아이콘을 오른쪽 클릭하면 나오는 메뉴 항목(`name`, 하위 메뉴 `sub`) |

MS Office 앱은 `NSDockMenu` 의 `Open Recent` 아래에 최근 문서가 들어 있어서 [1], 암호를 풀지 않고도 최근 문서 이름을 볼 수 있습니다.

### data.data

`data.data` 는 레코드가 이어진 파일이고, 레코드마다 16바이트 머리 뒤에 암호화된 본문이 옵니다 [1].

| 위치 | 길이 | 내용 |
|---|---|---|
| 0x00 | 8 | 매직 `NSCR1000` |
| 0x08 | 4 | 창 번호 (빅엔디언) |
| 0x0C | 4 | 레코드 길이 (빅엔디언, 머리 포함) |
| 0x10 | 나머지 | AES-CBC 로 암호화한 본문 |

본문은 머리의 창 번호와 `NSWindowID` 가 같은 `windows.plist` 항목에서 `NSDataKey` 를 꺼내 키로 쓰고, 0으로 채운 16바이트를 IV 로 써서 풉니다 [1]. 풀린 본문은 아래 순서로 이어집니다 [1].

| 순서 | 내용 |
|---|---|
| 1 | 4바이트 (뜻 모름) |
| 2 | 이름 길이 (4바이트, 빅엔디언) |
| 3 | 이름 (예: `_NSWindow`) |
| 4 | `rchv` |
| 5 | 길이 (4바이트, 빅엔디언) |
| 6 | NSKeyedArchiver plist |

풀어 낸 창 정보에서 앱마다 아래 값을 꺼낼 수 있습니다 [1].

| 폴더 | 꺼내는 값 | 뜻 |
|---|---|---|
| `com.apple.finder.savedState` | `WindowState` › `TargetURL` | 파인더 창에 열려 있던 폴더 |
| `com.apple.Preview.savedState` | `currentMediaContainerFileReferenceURL` › `NS.relative` | 미리보기에 열려 있던 파일 |
| `com.vmware.fusion.savedState` | `restorationID` | VMware Fusion 창 식별 값 |

> 그림 자리: `windows.plist` 의 창 항목(`NSWindowID`, `NSDataKey`)과 `data.data` 레코드 머리의 창 번호를 이어, 키로 본문을 풀고 NSKeyedArchiver plist 에서 `TargetURL` 을 꺼내는 흐름

## 증거로서 의미

**증명하는 것.** 폴더가 있으면 그 번들 ID 의 앱이 이 계정에서 창 상태를 저장한 적이 있다는 기록입니다. `NSTitle` 에 문서 이름이나 웹 페이지 제목이 있으면 상태를 저장한 시점에 그 제목의 창이 열려 있었고, 파인더의 `TargetURL` 이나 미리보기의 `NS.relative` 가 나오면 그 폴더나 파일이 창에 열려 있었다는 기록입니다 [1]. MS Office 앱의 `Open Recent` 항목은 그 앱이 최근 문서로 보여 주던 이름입니다 [1].

**증명하지 못하는 것.** 창마다 따로 시각이 없어서 [1] 창을 언제 열었는지, 얼마나 오래 열어 두었는지는 이 기록만으로 알 수 없습니다. 창이 열려 있었다는 사실이 사용자가 그 내용을 읽었다는 뜻은 아니고, 경로가 남아 있다고 해서 그 파일이 지금도 그 자리에 있다는 뜻도 아닙니다. 폴더가 없거나 비어 있어도 앱을 쓰지 않았다고 말할 수 없는데, "앱 종료 시 윈도우 닫기" 설정을 켜면 창이 다시 열리지 않기 때문입니다 [2]. 설정을 켰을 때 폴더가 생기지 않는지·지워지는지, 시스템이 이 폴더를 언제 지우는지는 공개 자료가 없어 검체에서 확인합니다.

보고서에는 "이 시각 무렵 저장된 파인더 창 상태에 이 폴더가 열린 창이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

폴더 안에 창별 시각 값은 없고, mac_apt 는 `windows.plist` 파일의 수정 시각을 "Source Last Modified Date" 로 적습니다 [1]. 이 값은 파일 시스템 시각이라서 앱이 창 상태를 마지막으로 다시 쓴 때를 가리키고, 창 제목 하나하나가 생긴 때가 아닙니다. 파일 시스템 시각을 읽는 법과 기준은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 봅니다. `data.data` 의 파일 시각도 함께 뽑아 두면 두 파일이 같은 때 다시 쓰였는지 견줄 수 있습니다.

## 함정과 한계

- **샌드박스 경로를 빼는 경우.** 샌드박스 앱의 상태는 `~/Library/Containers` 아래에 있어서 [1], 홈의 `Saved Application State` 만 보면 빠집니다.
- **심볼릭 링크를 따라가지 않는 경우.** 폴더 대신 링크가 놓인 경우가 있어서 [1], 링크만 복사하고 대상을 빼면 내용이 없습니다. 수집할 때 링크와 대상을 모두 가져옵니다.
- **창 제목을 파일 이름으로 단정하는 경우.** `NSTitle` 은 창 제목이라서 [1] 문서 이름일 수도, 웹 페이지 제목일 수도, 앱이 붙인 다른 문구일 수도 있습니다.
- **수정 시각을 창 열린 시각으로 읽는 경우.** "Source Last Modified Date" 는 `windows.plist` 파일 하나의 시각입니다 [1].
- **키를 잘못 짝짓는 경우.** 레코드마다 창 번호에 맞는 `NSDataKey` 로 풀어야 하고 [1], 다른 창의 키로 풀면 알아볼 수 없는 바이트가 나옵니다.
- **지우기와 조작.** 사용자가 폴더를 지우거나 창 되살리기를 끄는 설정을 켤 수 있지만 [2], 그 흔적이 어디에 남는지는 공개 자료가 없습니다. 폴더가 비어 있는 정황은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)의 흐름으로 다른 기록과 함께 판단합니다.

## 직접 분석해 보기

사용자 계정마다 `~/Library/Saved Application State/` 와 `~/Library/Containers/` 아래의 `Saved Application State` 를 링크 대상까지 포함해 작업 폴더로 복사하고, 원본 이미지에서 두 파일의 파일 시스템 시각을 먼저 뽑아 둡니다.

### 헥스로 한 번

아래 바이트는 mac_apt 가 읽는 레코드 머리 구조에 맞춰 만든 예시이고, 실제 검체에서 나온 값이 아닙니다.

```
data.data 레코드 머리 (예시)
4E 53 43 52 31 30 30 30     "NSCR1000" 매직
00 00 00 2A                 창 번호 = 0x2A = 42 (빅엔디언)
00 00 01 10                 레코드 길이 = 0x110 = 272바이트 (머리 16바이트 포함)
.. .. ..                    암호화된 본문 (272 - 16 = 256바이트)
```

실제 파일에서는 `4E 53 43 52 31 30 30 30` 을 헥스 검색하면 레코드 시작을 짚을 수 있고, 레코드 길이만큼 건너뛰면 다음 레코드가 나옵니다. 창 번호 42 에 맞는 `NSDataKey` 는 `windows.plist` 에서 `NSWindowID` 가 42 인 항목에서 찾습니다.

### 공개 도구로 한 번

mac_apt 의 `SAVEDSTATE` 플러그인(1.2)은 두 경로를 찾아 `windows.plist` 와 `data.data` 를 읽고, 창 제목·Dock 메뉴·파인더와 미리보기의 경로를 표로 내놓습니다 [1]. 결과를 손으로 확인하려면 파이썬으로 레코드를 끊어 풀어 봅니다. 아래 예시는 AES 풀이에 `pycryptodome` 패키지를 씁니다.

```python
import plistlib, struct
from Crypto.Cipher import AES

state = "com.apple.finder.savedState"      # 복사해 둔 폴더
with open(f"{state}/windows.plist", "rb") as f:
    windows = plistlib.load(f)
keys = {w["NSWindowID"]: w["NSDataKey"] for w in windows if "NSDataKey" in w}
for w in windows:
    print(w.get("NSWindowID"), w.get("NSTitle"))

data = open(f"{state}/data.data", "rb").read()
pos = 0
while pos + 16 <= len(data) and data[pos:pos + 8] == b"NSCR1000":
    win_id, length = struct.unpack(">II", data[pos + 8:pos + 16])
    body = data[pos + 16:pos + length]
    if win_id in keys:
        plain = AES.new(keys[win_id], AES.MODE_CBC, iv=b"\x00" * 16).decrypt(body)
        name_len = struct.unpack(">I", plain[4:8])[0]
        name = plain[8:8 + name_len]
        rest = plain[8 + name_len:]            # b"rchv" + 길이 4바이트 + plist
        if rest[:4] == b"rchv":
            plist_len = struct.unpack(">I", rest[4:8])[0]
            archived = plistlib.loads(rest[8:8 + plist_len])
            print(win_id, name, list(archived.get("$objects", []))[:10])
    pos += length
```

풀린 plist 는 NSKeyedArchiver 형식이라서 `$objects` 안에서 `TargetURL` 이나 `NS.relative` 에 해당하는 문자열을 찾아 읽습니다. 본문 끝의 채움 바이트를 어떻게 처리하는지는 공개 자료가 없으니, 복호가 실패하거나 끝부분이 어긋나면 mac_apt 결과와 견주어 봅니다.

## 교차 검증

- [최근 항목 (Shared File Lists)](recent-items/index.md), [파인더 설정과 기록 (Finder plist)](finder-plist.md) — 창에 열려 있던 파일·폴더가 최근 항목이나 최근 폴더에도 나오는지
- [문서 버전 (DocumentRevisions-V100)](document-revisions.md) — 미리보기처럼 버전을 남기는 앱이면 같은 파일의 버전이 언제 추가됐는지
- [KnowledgeC (knowledgeC.db)](../execution/knowledgec/index.md), [바이옴 (Biome)](../execution/biome/index.md) — 그 앱을 언제 썼는지 시각을 보탤 때
- [사파리 (Safari)](../browsers/safari/index.md), [크롬·엣지·웨일 (Chromium 계열)](../browsers/chromium/index.md) — 창 제목이 웹 페이지 제목으로 보일 때 방문 기록과 맞춰 볼 때
- [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) — `windows.plist` 와 `data.data` 가 다시 쓰인 때를 더 촘촘히 볼 때
- [어떤 앱을 언제 썼나 (App Usage)](../../04-scenarios/activity/app-usage.md), [이 파일을 누가 언제 열었나 (File Access)](../../04-scenarios/activity/file-access.md) — 이 기록을 쓰는 조사 흐름

## 실습

NIST CFReDS 같은 공개 검체 가운데 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 계정마다 `.savedState` 폴더가 몇 개 있나요? 홈의 `Saved Application State` 와 컨테이너 안쪽으로 나눠 세어 보세요.
2. 폴더 대신 심볼릭 링크로 놓인 항목이 있나요? 링크가 가리키는 곳은 어디인가요?
3. `NSTitle` 가운데 파일 이름으로 보이는 것과 웹 페이지 제목으로 보이는 것을 나눠 보세요.
4. 파인더의 `TargetURL` 로 나온 폴더가 지금 파일 시스템에 있나요?
5. `windows.plist` 의 수정 시각 무렵 KnowledgeC 나 바이옴에 그 앱의 사용 기록이 있는지 비교해 보세요.

## 참고 문헌

1. mac_apt `plugins/savedstate.py` (SAVEDSTATE 1.2, Yogesh Khatri) — https://github.com/ydkhatri/mac_apt/blob/master/plugins/savedstate.py
2. Apple 지원, "Change Desktop & Dock settings on Mac" (Mac 사용 설명서) — https://support.apple.com/guide/mac-help/change-desktop-dock-settings-mchlp1119/mac
