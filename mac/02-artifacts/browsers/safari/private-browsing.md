---
title: "개인 정보 보호 브라우징"
parent: "사파리"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1210
---

# 개인 정보 보호 브라우징 (Private Browsing)

개인 정보 보호 브라우징 (Private Browsing) 은 방문 기록·자동 완성·다운로드 목록·쿠키 변경을 남기지 않는 사파리 창이라서 평소 보던 파일이 대부분 비어 있지만, 닫은 창 목록의 `IsPrivateWindow` 표시와 컴퓨터에 남는 내려받은 파일처럼 거꾸로 따라갈 실마리는 남습니다.

## 무엇을 남기지 않나

개인 정보 보호 창은 아래처럼 동작합니다(macOS 27, Safari 27.0 기준) [1]. 앞선 버전에서도 동작이 같은지는 해당 버전의 기기로 확인해야 합니다.

| Apple 이 밝힌 동작 | 비어 있게 되는 곳 |
|---|---|
| 방문한 웹페이지와 자동 완성 정보를 저장하지 않음 | [방문 기록 (History.db)](history.md) |
| 최근 검색을 스마트 검색 필드 결과에 넣지 않음 | 설정 파일의 최근 검색 키([사파리 (Safari)](index.md)) |
| 열린 페이지를 iCloud 에 저장하지 않아 다른 기기의 "모든 탭" 에 보이지 않음 | [탭과 세션 (Tabs·Sessions)](tabs-sessions.md)의 iCloud 탭 |
| 받은 항목을 다운로드 목록에 넣지 않음. 파일은 컴퓨터에 남음 | [다운로드 (Downloads.plist)](downloads.md) |
| 쿠키와 웹사이트 데이터의 변경을 저장하지 않음 | [캐시와 웹 데이터 (Cache·WebKit)](cache-webkit.md)의 쿠키 |
| 개인 정보 보호 창을 Handoff 로 넘기지 않음 | [연속성과 유니버설 클립보드 (Continuity·Handoff)](../../cloud-apps/continuity.md) |
| 고급 추적 방지를 자동으로 켬(지문 수집 업체 연결 차단, URL 의 추적 인자 제거) | 해당 없음 |

오른쪽 열은 각 항목이 닿는 이 핸드북의 아티팩트입니다. "저장하지 않는다" 는 해당 기록 파일에 쓰지 않는다는 뜻으로 읽을 수 있지만, 메모리나 임시 파일에 잠시라도 올라가지 않는다는 뜻으로까지 읽지는 않습니다.

## 위치와 버전별 차이

개인 정보 보호 브라우징만 쓰는 파일은 알려져 있지 않고, 남는 흔적은 다른 사파리 파일 안에 섞여 있습니다. 알려진 곳은 `~/Library/Safari/RecentlyClosedTabs.plist` 입니다 [2]. 이 파일의 `ClosedTabOrWindowPersistentStates` 배열에는 닫힌 탭이나 창마다 항목이 있고, 항목 안 `PersistentState` 사전의 `IsPrivateWindow` 키가 개인 정보 보호 창이었는지를 나타냅니다 [2]. `PersistentStateType` 이 0 이면 탭 하나라서 `PersistentState` 에 `TabURL`·`TabTitle` 이 있고, 그 밖의 값이면 창이라서 `TabStates` 배열의 탭마다 `TabURL`·`TabTitle` 이 있습니다. 창의 `IsPrivateWindow` 값은 그 안의 탭 모두에 해당합니다 [2]. 이 파일의 구조와 다른 키는 [탭과 세션 (Tabs·Sessions)](tabs-sessions.md)에서 다룹니다. 이 키가 어느 버전부터 있는지, 개인 정보 보호 창에서 연 탭의 URL 이 실제로 이 파일에 남는지는 실제 기기로 확인해야 합니다.

## 증거로서 의미

**증명하는 것.** `RecentlyClosedTabs.plist` 에 `IsPrivateWindow` 가 참인 항목이 있으면 닫은 창이 개인 정보 보호 창이었다는 뜻이고 [2], 그 계정의 사파리에서 개인 정보 보호 창을 쓴 적이 있다는 실마리가 됩니다. 다운로드 폴더 등에 목록에 없는 파일이 있고 다른 기록이 그 파일을 사파리와 잇는다면, 개인 정보 보호 창에서 받았을 가능성을 볼 수 있습니다. 개인 정보 보호 창에서 받은 파일도 컴퓨터에는 남기 때문입니다 [1].

**증명하지 못하는 것.** 방문 기록·다운로드 목록·쿠키가 비어 있다는 사실만으로는 개인 정보 보호 창을 썼다고 말할 수 없습니다. 방문 기록과 다운로드 목록은 기록 지우기로도 비고([방문 기록 (History.db)](history.md) 참고), 다른 브라우저를 썼을 수도 있기 때문입니다. 반대로 개인 정보 보호 창을 쓴 흔적을 찾았더라도 그 창에서 어느 사이트를 봤는지는 이 흔적만으로 알 수 없습니다. 보고서에는 "이 계정의 사파리 최근 닫은 창 기록에 개인 정보 보호 창으로 표시된 항목이 있다" 처럼 씁니다.

## 시각 해석

`RecentlyClosedTabs.plist` 의 `PersistentState` 에는 닫은 시각 `DateClosed` 가 들어 있고, 창 항목이면 `TabStates` 의 탭마다 `DateClosed` 가 따로 있습니다 [2]. 사파리 plist 의 시각은 대부분 맥 절대 시각(2001-01-01 00:00:00 UTC 기준)입니다 [2]. 따라서 `IsPrivateWindow` 가 참인 항목이 있으면 그 창을 닫은 때를 UTC 로 얻을 수 있고, 창을 연 때나 그 안에서 머문 시간은 이 값으로 알 수 없습니다. 값을 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에서 다룹니다.

## 함정과 한계

**"비었음" 과 "쓰지 않음" 을 구별하지 못합니다.** 방문 기록 쪽에서 보면 개인 정보 보호 브라우징과 기록 지우기는 둘 다 빈자리를 남깁니다. 기록 지우기가 무엇을 지우는지는 [방문 기록 (History.db)](history.md)에서 다루고, 두 경우를 가르는 순서는 [개인 정보 보호 브라우징으로 무엇을 했나 (Private Browsing)](../../../04-scenarios/activity/private-browsing.md)에서 다룹니다.

**`IsPrivateWindow` 는 도구가 읽는 키입니다.** 이 키의 뜻은 분석 도구 mac_apt 의 해석이고 Apple 이 밝힌 것이 아닙니다 [2]. 닫은 창 기록은 최근 것만 남는 목록으로 보여서, 오래전에 쓴 개인 정보 보호 창은 이미 밀려났을 수 있습니다. 목록에 몇 개까지 남는지는 시험 기기에서 창을 여러 번 닫아 보고 확인합니다.

**여기서 다루지 않는 것.** 개인 정보 보호 창 잠금, 메모리·스왑·SQLite WAL 에 남는 흔적, 통합 로그에 남는 기록은 실제 기기로 확인해야 합니다. 실행 중인 맥을 다룬다면 [메모리 분석 (Memory Forensics)](../../../03-techniques/analysis/memory-forensics/index.md)을 검토할 수 있습니다.

## 직접 분석해 보기

사본을 macOS 에서 `plutil -p RecentlyClosedTabs.plist` 로 열어 `IsPrivateWindow` 를 찾아봅니다. 파이썬 표준 라이브러리 `plistlib` 로는 아래처럼 항목을 차례로 따라가며, 개인 정보 보호 창 표시와 닫은 시각, 탭 주소를 출력할 수 있습니다 [2].

```python
import plistlib

with open("RecentlyClosedTabs.plist", "rb") as f:
    plist = plistlib.load(f)

for item in plist.get("ClosedTabOrWindowPersistentStates", []):
    state = item.get("PersistentState") or {}
    private = state.get("IsPrivateWindow", False)
    if item.get("PersistentStateType") == 0:          # 탭 하나
        tabs = [state]
    else:                                             # 창: 안의 탭들
        tabs = state.get("TabStates", [])
    for t in tabs:
        print(private, t.get("DateClosed", state.get("DateClosed")),
              t.get("TabURL"), t.get("TabTitle"), sep=" | ")
```

`DateClosed` 가 plist 날짜로 읽히면 `plistlib` 은 시간대 정보가 없는 `datetime` 으로 돌려주는데, 값은 UTC 입니다. 공개 도구로는 mac_apt 의 사파리 플러그인이 이 파일을 읽어 `IsPrivateWindow` 를 표시합니다 [2]. 개인 정보 보호 창 항목은 `TabURL` 이 비어 있는지 채워져 있는지 분석 대상마다 확인합니다.

## 교차 검증

| 함께 볼 것 | 이유 |
|---|---|
| [탭과 세션 (Tabs·Sessions)](tabs-sessions.md) | `RecentlyClosedTabs.plist` 구조 |
| [다운로드 (Downloads.plist)](downloads.md) | 목록에 없는 받은 파일 |
| [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md) | 파일 쪽에서 본 출처 |
| [다운로드 출처 속성 (kMDItemWhereFroms)](../../filesystem/where-froms.md) | 파일에 남은 출처 주소 |
| [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md) | 다운로드 폴더에 파일이 생긴 때 |
| [개인 정보 보호 브라우징으로 무엇을 했나 (Private Browsing)](../../../04-scenarios/activity/private-browsing.md) | 여러 흔적을 묶어 따지는 순서 |

## 실습

공개 맥 시험 이미지에서 사파리 파일을 모아 아래 질문을 풀어 봅니다.

1. `RecentlyClosedTabs.plist` 에 `IsPrivateWindow` 가 참인 항목이 있는가. 있다면 닫은 시각은 UTC 로 언제인가
2. 그 항목에 `TabURL`·`TabTitle` 이 남아 있는가
3. 다운로드 폴더에 있지만 `Downloads.plist` 에 없는 파일이 있는가. 있다면 다른 기록으로 그 출처를 설명할 수 있는가
4. 방문 기록이 빈 구간이 있다면, 그 구간을 기록 지우기와 개인 정보 보호 브라우징 가운데 어느 쪽으로 설명할 근거가 있는가

## 참고 문헌

1. Apple Support, Safari 사용 설명서(Mac) — Browse privately in Safari on Mac — https://support.apple.com/guide/safari/browse-privately-ibrw1069/mac
2. mac_apt Safari 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/safari.py
