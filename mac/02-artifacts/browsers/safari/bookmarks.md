---
title: "북마크와 읽기 목록"
parent: "사파리"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1170
---

# 북마크와 읽기 목록 (Bookmarks·Reading List)

사파리는 북마크(Bookmarks)와 읽기 목록(Reading List)을 한 파일 `Bookmarks.plist` 에 폴더와 항목의 나무 구조로 저장하고, 읽기 목록 항목에는 추가한 시각이 붙어 있어서 사용자가 어떤 주소를 따로 챙겨 두었는지와 읽기 목록에 언제 넣었는지를 알 수 있습니다.

## 무엇을 기록하나

북마크 폴더와 북마크, 읽기 목록 항목이 모두 같은 파일에 들어갑니다. mac_apt 는 폴더 경로에 `com.apple.ReadingList` 가 들어 있는 항목을 읽기 목록으로 보고, 그 항목의 `ReadingList` 사전에서 추가한 시각을 꺼냅니다 [1]. 사용자가 북마크를 추가하거나 읽기 목록에 페이지를 넣을 때 쌓이는 기록이라서, 방문 기록과 달리 "지나간 방문" 이 아니라 "남겨 두려고 한 주소" 를 보여 줍니다.

이 페이지는 공개 도구 mac_apt 가 함께 읽는 자주 방문한 사이트 파일 `TopSites.plist` 도 다룹니다 [1]. 설정 파일에 남는 자주 방문한 사이트 캐시와 설정 파일 위치는 허브 [사파리 (Safari)](index.md)에 있습니다.

## 위치와 버전별 차이

`Bookmarks.plist` 는 사파리 데이터 폴더에 있습니다 [1]. 사파리 데이터 폴더는 `~/Library/Safari/` 와 Safari 15 이후의 컨테이너 쪽 두 곳이고, 파일마다 어느 쪽에 있는지가 다를 수 있어서 둘 다 확인합니다(허브 참고). Safari 17 이후에는 `SafariTabs.db` 의 `bookmarks` 표에 탭과 프로필 정보가 들어가는데 [1], 이름이 같은 이 표로 북마크 자체가 옮겨 갔는지는 확인한 자료에 없습니다. 그 표는 [탭과 세션 (Tabs·Sessions)](tabs-sessions.md)에서 다룹니다.

## 구조

### Bookmarks.plist

파일 맨 위에 형식 번호 `WebBookmarkFileVersion` 이 있고, 폴더는 `Children` 배열에 하위 항목을 담는 식으로 나무가 이어집니다 [1]. 항목의 종류는 `WebBookmarkType` 값으로 나눕니다.

| 키 | 뜻 [1] |
|---|---|
| `WebBookmarkFileVersion` | 파일 형식 번호 |
| `WebBookmarkType` | 항목 종류. 아래 표 |
| `Title` | 폴더 이름 |
| `Children` | 폴더 안의 항목 배열 |
| `URLString` | 북마크 주소 |
| `URIDictionary` → `title` | 북마크 제목 |
| `ReadingList` → `DateAdded` | 읽기 목록 항목의 추가 시각 |

| `WebBookmarkType` 값 | 뜻 [1] |
|---|---|
| `WebBookmarkTypeList` | 폴더 |
| `WebBookmarkTypeLeaf` | 항목(북마크 하나) |
| `WebBookmarkTypeProxy` | 무엇을 가리키는지 확인한 자료에 없음. mac_apt 는 이 종류를 건너뜀 |

`ReadingList` 사전 안의 다른 키(미리보기 글, 읽은 시각 같은 것)는 확인하지 못했습니다. 읽기 목록의 오프라인 사본은 mac_apt 코드 주석에 사파리 폴더의 `ReadingListArchives/{UUID}/Page.webarchive`(plist, 안의 `WebResourceURL` 로 주소를 얻음)로 적혀 있지만 [1], 이 플러그인이 그 파일을 실제로 읽지는 않아서 검체에서 직접 확인합니다. 아래는 위 키로 만든 예시이고, 특정 검체에서 나온 값이 아닙니다.

```text
(루트)
 ├ WebBookmarkFileVersion
 └ Children
    ├ (폴더)                   WebBookmarkType = WebBookmarkTypeList, Title = "(폴더 이름)"
    │  └ Children
    │     └ (항목)             WebBookmarkType = WebBookmarkTypeLeaf
    │                          URLString = "https://example.com/"
    │                          URIDictionary.title = "Example"
    └ (폴더)                   WebBookmarkType = WebBookmarkTypeList, Title = "com.apple.ReadingList"
       └ Children
          └ (항목)             WebBookmarkType = WebBookmarkTypeLeaf
                               URLString = "https://example.org/article"
                               ReadingList.DateAdded = (plist 날짜)
```

plist 를 읽는 법 자체는 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에서 다룹니다.

### TopSites.plist

mac_apt 는 `TopSites.plist` 에서 `DisplayedSitesLastModified`, `BannedURLStrings`, `TopSites` 배열(항목마다 `TopSiteURLString`, `TopSiteTitle`)을 읽습니다 [1]. 이름으로 보면 `DisplayedSitesLastModified` 는 표시 목록을 마지막으로 바꾼 시각이고 `BannedURLStrings` 는 목록에서 뺀 주소지만, 두 키의 뜻을 밝힌 자료는 찾지 못했습니다.

## 증거로서 의미

**증명하는 것.** 북마크 항목이 있으면 이 계정의 사파리 북마크에 이 주소가 이 제목과 폴더 위치로 저장돼 있다는 뜻이고, 읽기 목록 항목이면 `DateAdded` 로 읽기 목록에 넣은 시각까지 알 수 있습니다 [1]. 폴더 이름과 묶음에서 사용자의 관심사를 짐작해 볼 수도 있지만 이는 필자 해석입니다.

**증명하지 못하는 것.** 북마크가 있다고 그 주소를 방문했다는 뜻은 아니고, 방문했다면 그 시각은 [방문 기록 (History.db)](history.md)에서 따로 찾습니다. mac_apt 가 읽는 북마크 키에는 북마크를 추가한 시각이 없어서 [1], 북마크가 언제 생겼는지는 이 파일만으로 말할 수 없습니다. 이 맥에서 직접 추가한 북마크인지도 알 수 없는데, Apple 은 사파리 북마크를 iCloud 에 저장하는 데이터로 다루고 [3], 다른 기기에서 추가한 북마크가 동기화돼 들어왔을 수 있습니다.

## 시각 해석

이 파일에서 확인한 시각 키는 읽기 목록의 `DateAdded` 하나이고, plist 날짜 값입니다 [1]. 사파리의 plist·DB 시각은 대부분 맥 절대 시각(2001-01-01 00:00:00 UTC 기준)이라서 [1] 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다. 파일 자체의 수정 시각은 북마크를 하나라도 바꾸면 달라지는 값이라 어느 항목이 언제 바뀌었는지까지는 알려 주지 않습니다.

## 함정과 한계

**기록 지우기로는 지워지지 않습니다.** Apple 이 밝힌 기록 지우기 대상에는 자주 방문한 사이트 목록이 들어 있지만 북마크와 읽기 목록은 없습니다 [2]. 방문 기록이 비어 있어도 북마크와 읽기 목록은 남아 있을 수 있어서, 기록 지우기가 의심되는 검체에서 이 파일이 주소를 찾는 다른 통로가 됩니다. 지우기 대상 전체는 [방문 기록 (History.db)](history.md)에 정리했습니다.

**iCloud 보호 수준이 방문 기록과 다릅니다.** Apple 설명에 따르면 사파리 북마크는 표준 데이터 보호에서 전송 중과 서버에서 암호화하고 키는 Apple 이 보관하며, 고급 데이터 보호(Advanced Data Protection)를 켰을 때만 종단간 암호화합니다 [3]. 방문 기록·탭 그룹이 표준 보호에서도 종단간 암호화인 것과 다르다는 점만 이 자료로 확인했고 [3], 이 차이를 수사 절차에 어떻게 쓸지는 이 페이지의 범위 밖입니다.

**`WebBookmarkTypeProxy` 를 북마크로 세지 않습니다.** 뜻을 확인하지 못한 종류라서, 북마크 개수를 셀 때는 `WebBookmarkTypeLeaf` 만 셉니다.

## 직접 분석해 보기

아래 코드는 파이썬 표준 라이브러리 `plistlib` 로 나무를 따라 내려가면서 항목마다 폴더 경로, 제목, 주소, 읽기 목록 추가 시각을 출력합니다. 키 이름과 읽기 목록을 가르는 기준(폴더 경로의 `com.apple.ReadingList`)은 mac_apt 를 따랐습니다 [1].

```python
import plistlib

def walk(node, path=""):
    kind = node.get("WebBookmarkType")
    if kind == "WebBookmarkTypeLeaf":
        title = node.get("URIDictionary", {}).get("title", "")
        added = node.get("ReadingList", {}).get("DateAdded")
        tag = "읽기목록" if "com.apple.ReadingList" in path else "북마크"
        print(tag, path or "/", title, node.get("URLString"), added, sep=" | ")
        return
    if kind == "WebBookmarkTypeList":
        path = path + "/" + node.get("Title", "") if node.get("Title") else path
    for child in node.get("Children", []):
        walk(child, path)

with open("Bookmarks.plist", "rb") as f:
    walk(plistlib.load(f))
```

`plistlib` 은 `DateAdded` 를 시간대 정보가 없는 `datetime` 으로 돌려주고 값은 UTC 입니다. macOS 에서는 `plutil -p Bookmarks.plist` 로 나무 전체를 눈으로 훑어볼 수 있고, 공개 도구 mac_apt 의 사파리 플러그인이 같은 파일과 `TopSites.plist` 를 읽습니다 [1]. 코드 결과와 도구 결과의 항목 수가 다르면 `WebBookmarkTypeProxy` 나 빈 폴더를 어떻게 셌는지부터 봅니다.

## 교차 검증

| 함께 볼 것 | 이유 |
|---|---|
| [방문 기록 (History.db)](history.md) | 북마크한 주소를 실제로 언제 열었는지 |
| [탭과 세션 (Tabs·Sessions)](tabs-sessions.md) | `SafariTabs.db` 의 `bookmarks` 표, 열려 있던 탭 |
| [아이클라우드 계정 (iCloud Account)](../../cloud-apps/icloud-account.md) | 동기화에 쓰인 계정 |
| [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md) | 브라우저 흔적을 묶어 읽는 순서 |

## 실습

공개 맥 검체에서 `Bookmarks.plist` 를 찾아 아래 질문을 풀어 봅니다.

1. `WebBookmarkTypeLeaf` 항목은 몇 개이고, 그 가운데 `ReadingList` 가 있는 항목은 몇 개인가
2. 읽기 목록 항목 가운데 가장 최근에 넣은 것은 무엇이고, 그 주소가 방문 기록에도 있는가
3. `WebBookmarkTypeProxy` 항목이 있다면 어떤 키가 함께 들어 있는지 적어 보라
4. `TopSites.plist` 의 주소 목록과 방문 기록의 방문 수 상위 주소를 비교해 보라

## 참고 문헌

1. mac_apt Safari 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/safari.py
2. Apple Support, Safari 사용 설명서(Mac) — Clear your browsing history in Safari on Mac — https://support.apple.com/guide/safari/clear-your-browsing-history-sfri47acf5d6/mac
3. Apple Support, iCloud data security overview (2026-01-05) — https://support.apple.com/en-us/102651
