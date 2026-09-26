---
title: "검색 기록"
parent: "스포트라이트"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 860
---

# 검색 기록 (Spotlight Shortcuts)

스포트라이트 검색 기록 (Spotlight Shortcuts)은 사용자가 스포트라이트 검색창에 친 글자와 그 글자로 연 앱·문서를 짝지어 두는 사용자별 plist이고, macOS 버전마다 파일 위치와 이름이 달라서 버전부터 확인하고 찾아야 합니다.

## 무엇을 기록하나 · 왜 생기나

스포트라이트 검색창에서 글자를 치고 결과를 골라 앱이나 문서를 열면, 친 글자와 연 항목이 이 파일에 남습니다 [1]. 볼륨 색인이 파일의 속성을 담는다면 이 파일은 사용자가 직접 친 검색어를 담는 점이 다르고, 색인 쪽은 [색인 저장소 구조 (.Spotlight-V100·store.db)](store-structure.md)에서 다룹니다.

## 위치와 버전별 차이

파일은 사용자 홈 아래에 있고, macOS 버전별 경로는 아래와 같습니다 [1].

| macOS | 경로 |
|---|---|
| 10.9 이하 | `~/Library/Preferences/com.apple.spotlight.plist` (키 `UserShortcuts` 아래) |
| 10.10 ~ 10.14 | `~/Library/Application Support/com.apple.spotlight.Shortcuts` |
| 10.15 | `~/Library/Application Support/com.apple.spotlight/com.apple.spotlight.Shortcuts` |
| 11 ~ 13(버전 범위는 확정되지 않음) | `~/Library/Application Support/com.apple.spotlight/com.apple.spotlight.Shortcuts.v3` |
| 14 이후 | `~/Library/Group Containers/group.com.apple.spotlight/com.apple.spotlight.Shortcuts.v3` |

10.9 이하는 스포트라이트 설정 plist 안의 `UserShortcuts` 키 아래에 기록이 들어 있습니다 [1]. macOS 15와 26에서 경로가 또 바뀌었는지는 공개 자료가 없으니, 그 버전의 검체는 위 경로에 파일이 없으면 비슷한 이름의 파일을 찾아보고 찾은 경로를 확인 범위와 함께 적어 둡니다. 검체 버전의 경로만 보지 말고 표의 다른 경로에도 파일이 있는지 함께 확인합니다.

## 구조

파일은 plist이고, 최상위 사전의 키가 사용자가 친 글자이며 값은 다시 사전입니다 [1]. 값 사전에는 아래 키가 들어 있습니다 [1].

| 키 | 내용 |
|---|---|
| `DISPLAY_NAME` | 연 항목의 표시 이름 |
| `LAST_USED` | 마지막으로 쓴 시각 |
| `URL` | 연 항목의 위치. URL 인코딩돼 있어서 도구가 디코드함 |
| `IDENTIFIER` | 식별자 |
| `PATH` | 10.9 이하에서 `URL` 대신 쓰는 키 |

`IDENTIFIER` 값이 번들 ID인지는 알려져 있지 않습니다. 번들 ID처럼 보이는 값이 나오면 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../../01-foundations/value-decoding/bundle-team-id.md)를 참고해 설치된 앱과 맞춰 봅니다. plist를 읽는 법 자체는 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에서 다룹니다.

## 증거로서 의미

### 증명하는 것

이 파일은 이 사용자 계정의 스포트라이트 검색창에서 어떤 글자를 쳐서 어떤 앱이나 문서를 연 기록이 있었고, 그 항목을 마지막으로 쓴 시각이 언제로 적혀 있는지 보여 줍니다 [1]. 사용자 홈 아래에 있는 파일이라서 어느 계정에서 생긴 기록인지 가를 수 있고, `URL` 이나 `PATH` 로 연 항목이 어디 있었는지 알 수 있습니다.

### 증명하지 못하는 것

키 하나(친 글자)에 항목 하나가 붙는 구조이지만, 같은 글자로 여러 번 열었을 때 앞 기록이 덮이는지, 열었던 횟수가 어딘가에 남는지는 알려져 있지 않습니다. 따라서 이 파일로 "이 시각에 마지막으로 열었다는 기록이 있다" 까지는 말할 수 있어도 사용 횟수나 처음 쓴 때는 말하지 않습니다. 계정에 로그인한 사람이 누구였는지도 이 파일만으로는 알 수 없습니다. 보고서에는 "이 계정의 스포트라이트 검색 기록에 입력 글자 'saf' 로 Safari를 연 항목이 있고 마지막 사용 시각이 이 값으로 적혀 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

`LAST_USED` 는 mac_apt가 따로 변환하지 않고 plist 값을 그대로 쓰면서 출력 칸 형식만 날짜로 정해 둡니다 [1]. 그래서 plist 날짜 형식일 가능성이 높지만 확정된 것은 아니니, 파일을 직접 풀어서 값의 형식부터 확인합니다. plist의 날짜 형식과 맥에서 쓰는 시각 체계는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에서 설명합니다. 이 값은 마지막으로 쓴 시각이라서, 그 전에 언제 열었는지는 이 값으로 알 수 없습니다.

## 함정과 한계

키가 친 글자 그대로라서, 사용자가 문장 전체를 쳤는지 결과를 고르기 직전까지 친 앞부분만 남는지가 해석에 영향을 줍니다. 이 점은 알려져 있지 않으니 짧은 키를 보고 사용자가 그 글자만 쳤다고 단정하지 않습니다.

버전마다 파일 이름이 달라서, 한 경로만 보고 파일이 없다고 결론을 내리면 기록을 놓칩니다. 파일이 아예 없거나 비어 있으면 사용자가 스포트라이트로 무엇을 연 일이 없었다고 볼 수도 있지만 파일이 지워졌을 수도 있으니, [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)에서 이 경로의 변경 기록을 함께 봅니다.

## 직접 분석해 보기

### plist 구조로 한 번

아래는 실제 검체가 아니라 키 구조 [1]에 맞춰 만든 예시입니다. 형식이 알려지지 않은 값은 괄호로 두었습니다.

```
{
  "saf" : {
    "DISPLAY_NAME" : "Safari",
    "LAST_USED"    : (마지막 사용 시각),
    "URL"          : (URL 인코딩된 위치),
    "IDENTIFIER"   : (식별자)
  }
}
```

1. 최상위 키 `saf` 는 사용자가 검색창에 친 글자입니다.
2. `DISPLAY_NAME` 과 `URL` 로 그 글자로 연 항목이 무엇이고 어디 있었는지 봅니다. `URL` 은 `%20` 같은 인코딩을 풀어서 읽습니다.
3. `LAST_USED` 값의 형식을 확인하고 UTC로 바꿔 적습니다.

### 공개 도구로 한 번

mac_apt의 SPOTLIGHTSHORTCUTS 플러그인은 위 표의 버전별 경로를 찾아 읽고, 결과를 User, UserTyped, DisplayName, LastUsed, URL, Identifier, Source 칸으로 냅니다 [1].

## 교차 검증

검색창에서 연 앱은 [KnowledgeC (knowledgeC.db)](../../execution/knowledgec/index.md)나 [바이옴 (Biome)](../../execution/biome/index.md)의 앱 사용 기록과, 연 문서는 [최근 항목 (Shared File Lists)](../recent-items/index.md)과 맞춰 봅니다. 연 문서의 색인 속성 가운데 마지막 사용 시각은 [메타데이터 속성 (kMDItem)](metadata-attributes.md)에서 설명하고, 앱 사용 전체를 재구성하는 흐름은 [어떤 앱을 언제 썼나 (App Usage)](../../../04-scenarios/activity/app-usage.md)에 있습니다.

## 실습

macOS 공개 검체(NIST CFReDS 등)에서 아래 질문을 풀어 봅니다.

1. 검체의 macOS 버전을 확인하고, 위 표에서 그 버전의 경로에 파일이 있는지 봅니다. 다른 버전의 경로에도 파일이 남아 있는지 확인합니다.
2. 최상위 키(친 글자)를 모두 적고, 각 키로 연 항목의 `DISPLAY_NAME` 과 디코드한 `URL` 을 나란히 적습니다.
3. `LAST_USED` 값이 어떤 형식으로 저장돼 있는지 확인하고, 가장 최근 항목을 UTC로 바꿔 앱 사용 기록의 시각과 비교합니다.

## 참고 문헌

1. mac_apt 플러그인 spotlightshortcuts.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/spotlightshortcuts.py
