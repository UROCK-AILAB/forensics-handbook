---
title: "다운로드"
parent: "사파리"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1160
---

# 다운로드 (Downloads.plist)

사파리는 내려받은 항목의 목록을 `Downloads.plist` 의 `DownloadHistory` 배열에 적어 두고, 항목마다 받은 주소, 저장한 경로, 시작·끝 시각, 받은 크기가 들어 있어서 파일이 어디서 와서 어디에 저장됐는지를 브라우저 쪽에서 확인할 수 있습니다.

## 무엇을 기록하나

사파리가 내려받은 항목 하나가 배열 항목 하나로 들어갑니다 [1][2]. 목록은 기록일 뿐이라서 파일 자체와는 따로 움직입니다. 기록 지우기를 하면 다운로드 목록은 지워지지만 내려받은 파일은 남고 [3], 개인 정보 보호 브라우징에서 받은 항목은 처음부터 목록에 들어가지 않지만 파일은 컴퓨터에 남습니다 [4]. 두 경우 모두 "목록에 없음" 이 "받지 않음" 을 뜻하지 않습니다.

받은 파일을 저장할 기본 폴더는 사파리 설정 파일의 `DownloadsPath` 키에 있습니다 [2]. 설정 파일의 위치와 다른 설정 키는 허브 [사파리 (Safari)](index.md)에서 다룹니다.

## 위치와 버전별 차이

이 파일은 `~/Library/Safari/Downloads.plist` 에 있습니다 [5]. Safari 15 이후에는 사용자 데이터가 컨테이너 `~/Library/Containers/com.apple.Safari/Data/Library/Safari` 에 있을 수도 있어서 [2], 두 위치를 모두 봅니다.

## 구조

파일은 plist 이고 최상위 키 `DownloadHistory` 가 항목 사전의 배열입니다 [1][2]. plist 를 읽는 법 자체는 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에서 다룹니다.

```text
DownloadHistory                       배열
 └ 항목                               사전 하나 = 받은 항목 하나
    ├ DownloadEntryURL                받은 주소
    ├ DownloadEntryPath               저장한 경로
    ├ DownloadEntryDateAddedKey       시작 시각(plist 날짜)
    ├ DownloadEntryDateFinishedKey    끝난 시각(plist 날짜)
    ├ DownloadEntryProgressBytesSoFar
    ├ DownloadEntryProgressTotalToLoad
    └ DownloadEntryRemoveWhenDoneKey
```

위 틀은 plaso 가 읽는 키로 만든 그림이고 [1], 실제 파일에는 이보다 많은 키가 있을 수 있습니다. `DownloadEntryIdentifier` 같은 다른 키는 실제 데이터로 확인합니다.

| 키 | 뜻 |
|---|---|
| `DownloadEntryURL` | 받은 주소 [1] |
| `DownloadEntryPath` | 파일을 저장한 경로 [1] |
| `DownloadEntryDateAddedKey` | 다운로드를 시작한 시각 [1] |
| `DownloadEntryDateFinishedKey` | 다운로드가 끝난 시각 [1] |
| `DownloadEntryProgressBytesSoFar` | 이름으로 보면 지금까지 받은 바이트 수 [1] |
| `DownloadEntryProgressTotalToLoad` | 이름으로 보면 받을 전체 바이트 수 [1] |
| `DownloadEntryRemoveWhenDoneKey` | 이름으로 보면 "끝나면 목록에서 제거" 설정. 동작은 실제 기기로 확인 [1] |

## 증거로서 의미

**증명하는 것.** 항목이 있으면 이 사용자 계정의 사파리 다운로드 목록에 이 주소에서 받아 이 경로에 저장한 항목이 올라 있다는 뜻입니다. 두 시각 키로 받기 시작한 때와 끝난 때를, 경로로 저장 위치와 파일 이름을 알 수 있습니다 [1]. 받은 바이트 수와 전체 크기가 서로 다르면 다운로드가 중간에 멈췄을 가능성을 볼 수 있지만, 두 키의 뜻은 이름에서 미루어 본 것이라 다른 기록과 함께 확인합니다.

**증명하지 못하는 것.** `DownloadEntryPath` 는 받을 때의 경로라서 지금 그 자리에 파일이 있다는 뜻이 아니고, 파일을 연 적이 있는지도 이 목록으로는 알 수 없습니다. 거꾸로 목록에 없다고 해서 사파리로 받지 않았다고 쓸 수도 없는데, 기록 지우기와 개인 정보 보호 브라우징 두 경우 모두 파일은 남고 목록만 비기 때문입니다 [3][4]. 보고서에는 "이 계정의 사파리 다운로드 목록에 이 주소에서 받아 이 경로에 저장한 항목이 있고, 끝난 시각은 이때(UTC)다" 처럼 씁니다.

## 시각 해석

`DownloadEntryDateAddedKey` 와 `DownloadEntryDateFinishedKey` 는 plist 날짜 값이고, 앞의 것은 시작 시각, 뒤의 것은 끝난 시각입니다 [1]. 사파리의 plist·DB 시각은 대부분 맥 절대 시각(2001-01-01 00:00:00 UTC 기준)으로 저장돼 있고 [2], 읽어 낸 값을 현지 시각으로 옮길 때는 분석 대상의 시간대 설정을 따로 확인합니다. 값을 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md), 시간대 설정은 [시간대와 시계 설정 (Time Zone·NTP)](../../system-account/time-zone.md)을 봅니다.

## 함정과 한계

목록과 파일이 따로 움직인다는 점이 가장 큰 함정입니다. 목록에 있는 파일이 휴지통에 가 있거나 이름이 바뀌었을 수 있고, 목록에 없는 파일이 다운로드 폴더에 남아 있을 수도 있습니다 [3][4]. 그래서 목록은 파일 쪽 흔적과 늘 함께 읽습니다. 받은 파일에 붙는 격리 속성과의 관계는 [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md)에서 다룹니다.

`DownloadEntryPath` 에 적힌 폴더가 설정 키 `DownloadsPath` 의 폴더와 다르면 사용자가 저장 위치를 바꿨거나 그때마다 골랐을 수 있으니, 설정 파일이 언제 바뀌었는지와 함께 봅니다.

## 직접 분석해 보기

사본을 macOS 에서 `plutil -p Downloads.plist` 로 열면 사람이 읽을 수 있는 모양으로 볼 수 있습니다. 다른 운영체제에서는 파이썬 표준 라이브러리 `plistlib` 로 같은 일을 할 수 있고, 아래 코드는 plaso 가 읽는 키만 골라 출력합니다 [1].

```python
import plistlib

with open("Downloads.plist", "rb") as f:
    data = plistlib.load(f)

for e in data.get("DownloadHistory", []):
    print(e.get("DownloadEntryDateAddedKey"),
          e.get("DownloadEntryDateFinishedKey"),
          e.get("DownloadEntryURL"),
          e.get("DownloadEntryPath"),
          e.get("DownloadEntryProgressBytesSoFar"),
          e.get("DownloadEntryProgressTotalToLoad"),
          sep=" | ")
```

`plistlib` 은 plist 날짜를 시간대 정보가 없는 `datetime` 으로 돌려주는데, 값은 UTC 입니다. 공개 도구로는 plaso 의 사파리 Downloads.plist 플러그인이 같은 키를 읽어 두 날짜를 시작·끝 시각으로 해석하고 [1], mac_apt 도 이 파일을 읽습니다 [2]. 도구가 읽지 않는 키가 파일에 있는지 `plutil -p` 출력과 한 번 비교해 봅니다.

## 교차 검증

| 함께 볼 것 | 이유 |
|---|---|
| [방문 기록 (History.db)](history.md) | 받기 직전에 연 페이지, 기록 지우기 여부 |
| [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md) | 파일 쪽에서 본 출처 |
| [다운로드 출처 속성 (kMDItemWhereFroms)](../../filesystem/where-froms.md) | 파일에 남은 출처 주소 |
| [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md) | 저장 경로에 파일이 생기고 옮겨진 흔적 |
| [휴지통 (.Trash)](../../file-folder-usage/trash.md) | 목록에 있는 파일이 지워졌는지 |
| [개인 정보 보호 브라우징 (Private Browsing)](private-browsing.md) | 목록에 안 남는 다운로드 |
| [이 파일은 어디서 왔나 (File Origin)](../../../04-scenarios/activity/file-origin.md) | 파일 출처를 묶어 따지는 순서 |

## 실습

공개 맥 시험 이미지에서 `Downloads.plist` 를 찾아 아래 질문을 풀어 봅니다.

1. `DownloadHistory` 에 항목이 몇 개 있고, 가장 최근 항목의 끝난 시각은 UTC 로 언제인가
2. 각 항목의 `DownloadEntryPath` 에 지금도 파일이 있는가. 없다면 휴지통이나 다른 폴더에서 같은 이름을 찾을 수 있는가
3. 받은 바이트 수와 전체 크기가 다른 항목이 있는가
4. 다운로드 폴더에 있지만 목록에는 없는 파일을 하나 골라, 다른 기록으로 그 출처를 설명해 보라

## 참고 문헌

1. plaso Safari Downloads.plist 플러그인 소스 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/plist_plugins/safari_downloads.py
2. mac_apt Safari 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/safari.py
3. Apple Support, Safari 사용 설명서(Mac) — Clear your browsing history in Safari on Mac — https://support.apple.com/guide/safari/clear-your-browsing-history-sfri47acf5d6/mac
4. Apple Support, Safari 사용 설명서(Mac) — Browse privately in Safari on Mac — https://support.apple.com/guide/safari/browse-privately-ibrw1069/mac
5. ForensicArtifacts 정의 파일 webbrowser.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
