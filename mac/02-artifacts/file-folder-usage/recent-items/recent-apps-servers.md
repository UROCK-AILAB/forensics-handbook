---
title: "최근 앱·서버·폴더"
parent: "최근 항목"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 820
---

# 최근 앱·서버·폴더 (Recent Apps·Servers)

최근 앱·서버·폴더 기록은 `com.apple.sharedfilelist` 폴더의 목록 파일(최근 앱·최근 서버·즐겨찾기 볼륨 등)과 파인더·전역 설정 plist 의 "최근" 키들에 흩어져 있고, 사용자가 어떤 앱을 열었고 어느 서버와 폴더에 드나들었는지를 목록 형태로 보여 줍니다.

## 무엇을 기록하나

최근 앱·서버 목록과 파인더의 "최근 폴더", "서버에 연결", "폴더로 이동" 같은 기능은 각자 최근에 쓴 대상을 목록으로 남깁니다. 앱과 서버, 볼륨 목록은 최근 문서와 같은 SFL 파일에 들어 있고, 폴더·검색·열기 대화상자 위치 같은 것은 plist 키에 들어 있습니다 [1][2]. 이 페이지는 두 갈래를 차례로 정리하고, 앱마다 따로 있는 문서 목록은 [앱별 최근 문서 (Recent Documents)](app-recent-documents.md)에서 다룹니다.

## SFL 목록 파일

모두 `~/Library/Application Support/com.apple.sharedfilelist/` 아래에 있고, 아래 이름은 10.13 이상의 `.sfl2` 기준입니다 [1][2].

| 파일 | 내용 |
|---|---|
| `com.apple.LSSharedFileList.RecentApplications.sfl2` | 최근 앱 |
| `com.apple.LSSharedFileList.RecentDocuments.sfl2` | 최근 문서(시스템 전체) |
| `com.apple.LSSharedFileList.RecentServers.sfl2` | 최근 서버 |
| `com.apple.LSSharedFileList.RecentHosts.sfl2` | 최근 호스트(북마크 없음) |
| `com.apple.LSSharedFileList.FavoriteVolumes.sfl2` | 즐겨찾기 볼륨 |
| `…FavoriteItems`, `…FavoriteServers`, `…iCloudItems` | 사이드바 즐겨찾기, 즐겨찾는 서버, iCloud |

`.sfl3` 판 파일로는 `com.apple.LSSharedFileList.RecentDocuments.sfl3` 와 `com.apple.LSSharedFileList.FavoriteVolumes.sfl3` 가 있습니다 [4][5]. 나머지 목록도 같은 규칙으로 이름이 붙는 것으로 보입니다. 버전별 확장자 변화는 허브 [최근 항목 (Shared File Lists)](index.md)에, 파일 안 구조와 북마크 푸는 법은 [파일 형식 (SFL2·SFL3)](sfl-format.md)에 있습니다.

### 최근 서버를 읽는 법

서버 항목도 북마크를 담고 있고, 북마크의 URL 칸(0x1003)이 `file:///` 가 아니라 `smb://`·`afp://`·`ftp://` 같은 값이면 그 URL 이 서버 주소입니다 [1][3]. 그래서 RecentServers 뿐 아니라 RecentDocuments 항목에서도 URL 이 파일 밖을 가리키면 네트워크 공유 위의 문서였다는 단서가 됩니다. 서버 연결 자체의 기록은 [공유 폴더 연결 기록 (SMB·AFP)](../../network/network-shares.md)에서 봅니다.

RecentHosts 항목에는 북마크가 없어서 이름 말고는 읽을 칸이 적습니다 [2]. 10.10(Yosemite) 전의 RecentServers 는 옛 별칭 형식(`Alias`)을 썼고 Yosemite 부터 `Bookmark` 를 씁니다 [1]. 옛 Alias 안의 날짜는 HFS 시각이며 [1], HFS 시각의 기준은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)을 봅니다.

### 10.10 이하의 `com.apple.recentitems.plist`

10.10 이하에서는 같은 목록이 `~/Library/Preferences/com.apple.recentitems.plist` 한 파일에 들어 있었습니다 [1][2].

| 키 | 하위 구조 |
|---|---|
| `RecentApplications` | `CustomListItems`(항목마다 `Name`, `URL`/`Bookmark`/`Alias`), `MaxAmount` |
| `RecentDocuments` | 같음 |
| `RecentServers` | 같음 |
| `Hosts` | 같음 |
| `Applications`, `Documents`, `Servers` | 더 옛 판의 키 이름 |

## 최근 폴더·위치 (plist)

### `~/Library/Preferences/com.apple.finder.plist`

파인더 설정 파일에는 최근에 드나든 폴더와 서버 주소, 입력값이 여러 키에 나뉘어 있습니다 [1][2]. 파인더 설정 파일의 다른 키는 [파인더 설정과 기록 (Finder plist)](../finder-plist.md)에서 다룹니다.

| 키 | 내용 |
|---|---|
| `FXRecentFolders` | 파인더 "최근 폴더". 항목마다 `name`, `file-bookmark`(북마크). 10.9 전에는 `file-data` → `_CFURLAliasData`(Alias) |
| `FXConnectToLastURL` | "서버에 연결" 에 마지막으로 넣은 URL |
| `GoToField`, `GoToFieldHistory` | "폴더로 이동" 에 넣은 값과 그 기록 |
| `RecentMoveAndCopyDestinations` | 최근 이동·복사 대상 폴더 |
| `NSNavLastRootDirectory`, `NSNavLastCurrentDirectory` | 열기·저장 대화상자의 마지막 위치 |
| `SGTRecentFileSearches` | 최근 파인더 검색(항목마다 `name`, `type`) |
| `FXDesktopVolumePositions` | 데스크톱에 나타난 볼륨. 키 이름이 `<볼륨이름>_<16진수>` 모양 |

`FXDesktopVolumePositions` 의 키 이름 뒤쪽 16진수를 mac_apt 는 16진 실수 표기로 풀어 정수로 바꾼 뒤 맥 절대 시각으로 읽고, 이 값을 볼륨 생성 시각으로 씁니다 [1]. 볼륨 이름과 생성 시각이 함께 나오니 외장 장치의 볼륨을 [USB 저장 장치 (USB Storage)](../../external-devices/usb/index.md) 기록과 맞춰 볼 수 있지만, 이 값을 볼륨 생성 시각으로 보는 해석은 도구의 해석이라는 점을 함께 적습니다.

### `~/Library/Preferences/.GlobalPreferences.plist`

전역 설정 파일에서는 `NSNavRecentPlaces`(열기·저장 대화상자의 최근 위치)와 `SGTRecentFileSearches`(최근 검색)를 봅니다 [1]. mac_apt 는 이 파일에서 값이 문자열 `'1'` 이고 이름이 `Apple` 로 시작하지 않는 키를 마운트됐던 볼륨·장치 이름으로 보는데 [1], 이는 도구가 정한 추정 규칙이라서 결과에 나온 이름은 다른 기록으로 한 번 더 확인합니다.

### `~/Library/Preferences/com.apple.sidebarlists.plist` (10.12 이하)

10.12 이하에서는 파인더 사이드바 목록이 이 파일에 있었고, `favoriteservers` → `CustomListItems`(`Name`, `URL`)에 즐겨찾는 서버가, `systemitems` → `VolumesList`(`Name`, `EntryType`, `Alias`, `Visibility`)에 볼륨이 들어 있습니다 [1][2].

### 그 밖에 함께 읽히는 기록

mac_apt 는 `~/.ssh/known_hosts` 와 `known_hosts.old` 의 호스트 이름을 파일 수정 시각과 함께 최근 항목으로 내고 [1], 이 파일의 해석은 [SSH 키와 접속 목록 (SSH Keys·known_hosts)](../../credentials/ssh-keys.md)에서 다룹니다. `~/Library/Application Support/com.apple.spotlight.Shortcuts` 에도 항목(`DISPLAY_NAME`, `LAST_USED`, `URL`)이 남는데 [2], 지금 macOS 에서도 같은 경로인지는 검체에서 확인합니다. 스포트라이트 쪽 기록은 [스포트라이트 (Spotlight)](../spotlight/index.md)를 봅니다.

## 증거로서 의미

**증명하는 것.** RecentApplications 항목은 그 사용자 계정의 최근 앱 목록에 이 앱이 올라간 적이 있다는 기록이고, 북마크 경로로 어느 위치의 앱 번들이었는지도 읽을 수 있습니다. RecentServers 와 `FXConnectToLastURL` 은 사용자 계정에서 이 서버 주소가 쓰였다는 기록이고, `GoToFieldHistory`·`RecentMoveAndCopyDestinations`·`FXRecentFolders` 는 사용자가 이 폴더 경로를 입력하거나 대상으로 고른 적이 있다는 기록입니다. 특히 이동·복사 대상 폴더에 외장 볼륨이나 네트워크 경로가 보이면 [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md) 조사에서 다른 기록과 맞춰 볼 출발점이 됩니다.

**증명하지 못하는 것.** 앱을 언제 몇 번 실행했는지, 서버에 연결이 실제로 성공했는지, 폴더로 옮긴 파일이 무엇인지는 이 기록만으로 알 수 없습니다. `FXConnectToLastURL` 은 마지막 값 하나만 남으니 그 전 주소는 여기서 볼 수 없고, 목록에는 상한(`MaxAmount`)이 적혀 있을 수 있어서 [1][2] 목록에 없다는 사실로 쓴 적이 없다고 말할 수 없습니다.

## 시각 해석

SFL 항목과 파인더 plist 항목에는 "연 시각" 이나 "연결한 시각" 칸이 있다는 근거가 공개 자료에 없습니다. 북마크 안 시각의 뜻과 어림하는 법은 [파일 형식 (SFL2·SFL3)](sfl-format.md)에 정리했습니다. 이 페이지의 기록에서 시각으로 쓸 만한 값은 아래 정도이고, 모두 "그 대상을 쓴 시각" 과는 다른 값입니다.

| 값 | 뜻 | 기준 |
|---|---|---|
| 목록 파일·plist 의 수정 시각 | 파일이 마지막으로 바뀐 때 | 파일 시스템 시각 |
| `FXDesktopVolumePositions` 키 이름의 16진수 | mac_apt 가 볼륨 생성 시각으로 읽는 값 [1] | 맥 절대 시각(도구 해석) |
| `known_hosts` 수정 시각 | 파일이 마지막으로 바뀐 때 [1] | 파일 시스템 시각 |
| Spotlight Shortcuts `LAST_USED` | 항목의 마지막 사용 값 [2] | 공개 자료 없음 |

## 함정과 한계

- 같은 사실이 여러 곳에 겹쳐 남습니다. 파인더에서 서버에 연결하면 RecentServers 와 `FXConnectToLastURL` 에 함께 보일 수 있고, 두 곳의 값이 다르면 어느 쪽이 더 나중에 바뀌었는지 파일 수정 시각으로 따집니다.
- 10.12 이하의 `com.apple.sidebarlists.plist`, 10.10 이하의 `com.apple.recentitems.plist` 처럼 이전 버전 파일이 업그레이드한 뒤에도 남아 있을 수 있어서, 검체의 macOS 버전과 파일 형식이 맞지 않으면 예전 기록일 가능성을 먼저 봅니다.
- RecentHosts 는 북마크가 없어서 경로·볼륨으로 교차 확인하기 어렵습니다 [2].
- `.GlobalPreferences.plist` 의 볼륨 이름 추정과 `FXDesktopVolumePositions` 의 시각은 mac_apt 가 정한 해석이라서, 보고서에는 도구 이름과 해석 근거를 함께 적습니다 [1].

## 직접 분석해 보기

SFL 목록 파일은 [파일 형식 (SFL2·SFL3)](sfl-format.md)의 헥스 예시대로 북마크를 풀고, RecentServers 에서는 0x1003 URL 칸을 먼저 봅니다. 파인더·전역 설정 plist 는 바이너리 plist 를 읽는 도구로 열어 위 표의 키를 찾고, 값이 북마크나 Alias 데이터이면 [파일 참조 데이터 (Alias·Bookmark)](../../../01-foundations/value-decoding/alias-bookmark.md)의 방법으로 풉니다. plist 를 여는 법은 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에서 다룹니다.

공개 도구로는 mac_apt `RECENTITEMS` 플러그인이 이 페이지의 SFL 파일, 파인더·전역 설정 plist, `known_hosts` 를 한 번에 읽고 [1], macMRU 는 SFL 파일과 관련 plist, Spotlight Shortcuts 를 읽습니다 [2]. `FXConnectToLastURL` 처럼 한 줄짜리 값은 도구 결과에서 빠지기 쉬우니 원본 plist 에서도 한 번 찾아봅니다.

## 교차 검증

- [공유 폴더 연결 기록 (SMB·AFP)](../../network/network-shares.md) — 최근 서버 주소가 실제 연결 기록과 맞는지
- [USB 저장 장치 (USB Storage)](../../external-devices/usb/index.md) — 즐겨찾기 볼륨·데스크톱 볼륨 이름을 장치 기록과 맞출 때
- [SSH 키와 접속 목록 (SSH Keys·known_hosts)](../../credentials/ssh-keys.md)
- [KnowledgeC (knowledgeC.db)](../../execution/knowledgec/index.md) — 최근 앱 목록의 앱을 쓴 시각을 찾을 때
- [어떤 앱을 언제 썼나 (App Usage)](../../../04-scenarios/activity/app-usage.md)
- [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md)

## 실습

NIST CFReDS 같은 공개 검체 가운데 macOS 사용자 폴더가 들어 있는 이미지로 풀어 봅니다.

1. RecentServers 목록과 `com.apple.finder.plist` 의 `FXConnectToLastURL` 을 모두 읽고, 두 값이 같은지 다른지 확인합니다.
2. `RecentMoveAndCopyDestinations` 와 `GoToFieldHistory` 에 나온 경로 가운데 사용자 폴더 밖(외장 볼륨·네트워크)을 가리키는 것을 골라 봅니다.
3. `FXDesktopVolumePositions` 의 볼륨 이름을 즐겨찾기 볼륨 목록, 북마크의 볼륨 이름과 맞춰 봅니다.

## 참고 문헌

1. mac_apt `plugins/recentitems.py` (RECENTITEMS 1.5, Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/recentitems.py
2. macMRU-Parser `macMRU.py` (Sarah Edwards / mac4n6, 2017) — https://raw.githubusercontent.com/mac4n6/macMRU-Parser/master/macMRU.py
3. mac_alias 문서, "Mac Bookmark Format" — https://mac-alias.readthedocs.io/en/latest/bookmark_fmt.html
4. exhume_artefacts `src/parsers/macos/sharedfilelist.rs` (forensicxlab) — https://github.com/forensicxlab/exhume_artefacts/blob/main/src/parsers/macos/sharedfilelist.rs
5. MacOS-Velociraptor-Collectors README (MrJayTechie) — https://github.com/MrJayTechie/MacOS-Velociraptor-Collectors
