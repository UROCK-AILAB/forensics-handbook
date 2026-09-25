---
title: "앱별 최근 문서"
parent: "최근 항목"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 810
---

# 앱별 최근 문서 (Recent Documents)

앱별 최근 문서는 앱마다 "최근 사용 항목 열기(Open Recent)" 메뉴에 보여 줄 문서 목록을 앱 번들 ID 이름의 파일에 따로 담아 둔 기록이고, 어느 앱이 어떤 문서를 최근 목록에 올렸는지를 앱 단위로 보여 줍니다.

## 무엇을 기록하나

시스템 전체의 최근 문서 목록과 별도로, 앱마다 자기 최근 문서 목록이 있습니다. 목록 파일 이름이 앱의 번들 ID 라서 파일 이름만으로 어느 앱의 목록인지 알 수 있고, 항목마다 대상 문서의 북마크가 들어 있어서 문서 경로와 볼륨을 읽을 수 있습니다 [1][2]. 번들 ID 를 앱 이름으로 바꾸는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../../01-foundations/value-decoding/bundle-team-id.md)에서 다룹니다.

NSDocumentController 에는 Open Recent 메뉴를 다루는 아래 API 가 있습니다 [4].

| API | 설명 |
|---|---|
| `maximumRecentDocumentCount` | 표준 Open Recent 메뉴에 보일 수 있는 최대 개수 |
| `clearRecentDocuments(_:)` | 앱의 최근 문서 목록을 비움 |
| `noteNewRecentDocumentURL(_:)` | URL 이 가리키는 데이터에 맞는 Open Recent 항목을 추가하거나 바꿈 |
| `noteNewRecentDocument(_:)` | 문서에 맞는 Open Recent 항목을 추가하거나 바꿈 |
| `recentDocumentURLs` | 최근 문서 URL 목록 |

이 API 가 아래 `ApplicationRecentDocuments` 폴더의 파일에 기록된다는 공식 문서는 없고, 문서 기반 앱이 문서를 열 때 자동으로 목록에 넣는지도 공개되어 있지 않습니다 [4]. API 와 파일은 이름과 쓰임이 맞아떨어질 뿐, 둘의 관계가 확정된 것은 아닙니다.

## 위치와 버전별 차이

| macOS | 위치 | 출처 |
|---|---|---|
| 10.10 이하(그 전후 앱 포함) | `~/Library/Preferences/<번들 ID>.LSSharedFileList.plist` | [1][2][3] |
| 10.11 이상 | `~/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.ApplicationRecentDocuments/<번들 ID>.sfl` | [2] |
| 10.13 이상 | 같은 폴더의 `<번들 ID>.sfl2` | [2] |
| `.sfl3` 를 쓰는 버전 | 같은 폴더(mac_apt 가 `.sfl3` 에도 같은 경로를 씀). 파일 이름 규칙은 공개 자료 없음 | [1] |

`.sfl3` 가 쓰이기 시작한 버전과 폴더 전체의 버전별 변화는 허브 [최근 항목 (Shared File Lists)](index.md)의 표에 모았습니다. 옛 plist 방식은 ForensicArtifacts 정의에도 `*.LSSharedFileList.plist` 라는 이름(MacOSApplicationsRecentItems)으로 올라 있습니다 [3].

## 구조

`.sfl`·`.sfl2` 이상의 앱별 목록은 다른 최근 항목 파일과 구조가 같아서 항목마다 `Name`, `uuid`, `Bookmark`, `CustomItemProperties` 가 들어 있습니다 [1][2]. 키의 뜻과 북마크를 푸는 법은 [파일 형식 (SFL2·SFL3)](sfl-format.md)에서 다룹니다. mac_apt 는 이 폴더에서 나온 항목의 종류를 `APP_RECENT_DOC` 으로 따로 나눠 적습니다 [1].

옛 `<번들 ID>.LSSharedFileList.plist` 의 키 구성은 아래와 같습니다 [1][2].

```
RecentDocuments
  CustomListItems      (배열, 항목마다 Name, Bookmark)
  MaxAmount
```

mac_apt 는 `~/Library/Preferences` 폴더에서 이름에 `lssharedfilelist` 가 들어 있고 크기가 120바이트를 넘는 plist 만 읽습니다 [1]. 이 크기 기준은 도구가 정한 규칙이라서, 크기가 작은 파일도 원본을 한 번 열어 보면 빈 목록인지 확인할 수 있습니다.

### Apple 이 아닌 앱의 최근 파일 기록

Microsoft Office 처럼 자기 방식으로 최근 파일을 따로 기록하는 앱도 있습니다. Office 의 기록 위치는 아래와 같습니다 [2].

| 앱 | 위치 | 키 |
|---|---|---|
| MS Office 2016 | `~/Library/Containers/com.microsoft.<앱>/Data/Library/Preferences/com.microsoft.<앱>.securebookmarks.plist` | 항목마다 `kBookmarkDataKey`(북마크), `kUUIDKey` |
| MS Office 2011 | `~/Library/Preferences/com.microsoft.office.plist` | `14\File MRU\MSWD`(Word), `14\File MRU\XCEL`(Excel), `14\File MRU\PPT3`(PowerPoint) |

지금 쓰이는 Office 버전에서도 경로와 키가 같은지는 공개 자료가 없어 검체에서 확인합니다. 검체의 Office 버전을 먼저 확인하고, 경로가 다르면 컨테이너 폴더 안에서 `securebookmarks` 이름의 파일을 찾아봅니다.

## 증거로서 의미

**증명하는 것.** 앱별 목록에 항목이 있으면, 그 사용자 계정에서 이 번들 ID 의 앱이 이 문서를 최근 문서 목록에 올린 적이 있다는 기록입니다. 시스템 전체 목록과 달리 앱이 정해져 있어서, 같은 문서를 어느 앱으로 다뤘는지 좁히는 데 씁니다. 북마크에서 문서 경로와 볼륨 이름을 읽을 수 있어서 외장 장치나 네트워크 볼륨 위의 문서였는지도 가려 볼 수 있습니다.

**증명하지 못하는 것.** 문서를 연 시각, 연 횟수, 편집했는지, 내용을 보고 저장했는지는 알 수 없습니다. 앱이 표준 API 를 쓰지 않고 자기 방식으로 최근 파일을 관리하면 이 폴더에는 아무것도 남지 않을 수 있어서, 목록에 없다는 사실로 그 앱에서 그 문서를 쓰지 않았다고 말할 수 없습니다. 목록 길이에도 상한이 있어서(`MaxAmount`, `maximumRecentDocumentCount`) 오래된 항목은 목록에서 빠져 있을 수 있습니다 [1][4].

## 시각 해석

항목에 "문서를 연 시각" 칸이 있다는 근거는 공개 자료에 없습니다. 북마크 안의 대상 생성 시각·북마크 생성 시각과 목록 파일의 수정 시각을 어떻게 읽는지는 [파일 형식 (SFL2·SFL3)](sfl-format.md)에 정리했습니다. 앱별 목록은 파일 하나가 앱 하나라서, 목록 파일의 수정 시각을 그 앱의 목록이 마지막으로 바뀐 때로 좁혀 읽을 수 있습니다. 다만 무엇이 바뀌었는지(추가·순서 변경·삭제)는 파일 시각만으로 알 수 없습니다.

## 함정과 한계

- 앱의 "최근 사용 항목 지우기" 를 누르면 목록이 비는 동작은 `clearRecentDocuments(_:)` 설명과 맞습니다 [4]. 목록을 지운 뒤 파일 안이나 디스크에 예전 항목의 흔적이 남는지는 공개 자료가 없어 검체에서 확인합니다.
- 빈 목록 파일은 지금 목록이 비어 있다는 것만 보여 주고, 지워서 빈 것인지 처음부터 비었는지는 이 파일만으로 가릴 수 없습니다.
- 파일 이름은 번들 ID 만 담고 있어서, 파일 이름만으로 어느 버전의 앱이 쓴 항목인지는 알 수 없습니다.
- Office 의 `securebookmarks.plist` 처럼 앱 컨테이너 안에 최근 파일을 따로 두는 앱이 있어서, `com.apple.sharedfilelist` 폴더만 보면 빠지는 기록이 생깁니다 [2].

## 직접 분석해 보기

앱별 목록 파일의 헥스와 북마크 구조는 시스템 목록과 같으니 [파일 형식 (SFL2·SFL3)](sfl-format.md)의 예시를 그대로 따라갑니다. 앱별 목록에서 먼저 할 일은 폴더 안의 파일 이름을 번들 ID 로 모두 적어 두는 것이고, 이 목록이 곧 사용자 계정에서 최근 문서를 남긴 앱 목록입니다.

공개 도구 가운데 mac_apt `RECENTITEMS` 플러그인은 이 폴더와 옛 `LSSharedFileList.plist` 를 함께 읽어 `APP_RECENT_DOC` 종류로 내고 [1], macMRU 는 이 폴더와 함께 MS Office 의 최근 파일 기록도 읽습니다 [2]. 두 도구의 결과를 번들 ID 별로 맞춰 보고, 한쪽에만 있는 항목은 원본 파일을 열어 확인합니다.

## 교차 검증

- [앱 저장 상태 (Saved Application State)](../saved-application-state.md) — 앱을 닫을 때 열려 있던 창·문서 흔적과 맞출 때
- [문서 버전 (DocumentRevisions-V100)](../document-revisions.md) — 문서를 저장한 흔적을 찾을 때
- [KnowledgeC (knowledgeC.db)](../../execution/knowledgec/index.md) — 앱을 쓴 시각을 다른 기록에서 볼 때
- [문서 메타데이터 (iWork·Office)](../../embedded-metadata/iwork-office.md) — 문서 안에 남은 작성·수정 정보와 맞출 때
- [이 파일을 누가 언제 열었나 (File Access)](../../../04-scenarios/activity/file-access.md)

## 실습

NIST CFReDS 같은 공개 검체 가운데 macOS 사용자 폴더가 들어 있는 이미지로 풀어 봅니다.

1. `com.apple.LSSharedFileList.ApplicationRecentDocuments` 폴더의 파일 이름을 모두 적고, 번들 ID 마다 어떤 앱인지 설치된 앱 목록과 맞춰 봅니다.
2. 같은 문서 경로가 두 앱 이상의 목록에 나오는지 찾아보고, 나온다면 각 목록 파일의 수정 시각을 비교합니다.
3. 빈 목록 파일이 있으면, 그 앱의 다른 흔적(저장 상태·실행 기록)이 있는지 확인합니다.

## 참고 문헌

1. mac_apt `plugins/recentitems.py` (RECENTITEMS 1.5, Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/recentitems.py
2. macMRU-Parser `macMRU.py` (Sarah Edwards / mac4n6, 2017) — https://raw.githubusercontent.com/mac4n6/macMRU-Parser/master/macMRU.py
3. ForensicArtifacts `artifacts/data/macos.yaml` — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
4. Apple Developer, NSDocumentController ("Managing the Open Recent Menu") — https://developer.apple.com/tutorials/data/documentation/appkit/nsdocumentcontroller.json
