---
title: "최근 항목"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 790
has_children: true
has_toc: false
---

# 최근 항목 (Shared File Lists)

최근 항목 (Shared File Lists)은 사용자마다 최근에 쓴 문서·앱·서버와 즐겨찾기 볼륨 같은 목록을 `~/Library/Application Support/com.apple.sharedfilelist/` 폴더에 목록별 파일로 남긴 기록이고, 항목마다 대상 파일의 북마크가 들어 있어서 파일이 지금 없어도 경로와 볼륨을 읽을 수 있습니다.

## 왜 중요한가

최근 항목은 "이 사용자 계정에서 이 파일·앱·서버가 최근 목록에 올라간 적이 있다" 를 보여 주는 기록이라서, 파일 사용 흔적을 찾을 때 먼저 여는 곳 가운데 하나입니다. 항목의 북마크에는 경로뿐 아니라 볼륨 이름·UUID·크기가 들어 있어서 외장 저장 장치나 네트워크 공유 위의 파일을 구분할 수 있고 [1], 북마크 안의 경로는 대상 파일이 지금 있는지와 상관없이 읽을 수 있습니다. 윈도우의 RecentDocs·점프 목록과 쓰임이 비슷하다고 보면 이해가 쉽습니다.

해석은 조심해야 합니다. 항목마다 "파일을 연 시각" 필드가 있다는 근거는 공개 자료에 없고, 목록 길이에도 상한이 있을 수 있습니다 [2]. 그래서 최근 항목만으로 "언제 열었다" 를 단정하지 않고, "이 목록에 이 대상이 있었다" 를 확인한 뒤 다른 기록으로 시각을 채웁니다.

## 한눈에 보기

macOS 버전에 따라 저장 위치와 형식이 아래처럼 바뀌었습니다 [2].

| macOS | 위치·파일 |
|---|---|
| 10.10 이하 | `~/Library/Preferences/com.apple.recentitems.plist` |
| 10.11 이상 | `~/Library/Application Support/com.apple.sharedfilelist/` 안의 `.sfl` |
| 10.13 이상 | 같은 폴더의 `com.apple.LSSharedFileList.<목록이름>.sfl2` |
| 공개 자료 없음 | 같은 폴더의 `.sfl3`(예: `com.apple.LSSharedFileList.RecentDocuments.sfl3`) [5][6] |

`.sfl3` 가 어느 macOS 버전부터 쓰이는지는 공개 자료가 없습니다. `.sfl4` 도 있으며 [4], mac_apt 는 `.sfl2`~`.sfl4` 를 한 함수로 읽습니다 [1].

| 항목 | 내용 |
|---|---|
| 목록 종류 | RecentDocuments, RecentApplications, RecentServers, RecentHosts, FavoriteVolumes, FavoriteItems, FavoriteServers, ProjectsItems, iCloudItems, ApplicationRecentDocuments [1][2] |
| 앱별 목록 | 하위 폴더 `com.apple.LSSharedFileList.ApplicationRecentDocuments/` 에 앱 번들 ID 이름의 파일 [1][2] |
| 형식 | NSKeyedArchiver 로 저장한 바이너리 plist, 항목마다 대상의 북마크 데이터 [1][5] |
| 알려 주는 것 | 목록에 오른 문서·앱·서버·볼륨, 대상 경로, 볼륨 이름·UUID·크기, 대상 파일 생성 시각, 북마크를 만든 사용자 |
| 알려 주지 않는 것 | 파일을 연 시각과 횟수, 내용을 봤는지, 서버 연결이 성공했는지 |
| 공개 도구 | mac_apt `RECENTITEMS`(`.sfl`, `.sfl2`~`.sfl4`) [1], macMRU(`.sfl`·`.sfl2`) [2], SFL-Parser(`.sfl3`·`.sfl4`) [4], exhume_artefacts(`.sfl`~`.sfl3`) [5] |

수집 정의를 쓸 때 주의할 점이 있는데, ForensicArtifacts 정의에는 `com.apple.recentitems.plist` 와 `*.LSSharedFileList.plist` 만 있고 `.sfl` 계열 경로는 없어서 [3], 이 정의만으로 수집하면 10.11 이후의 목록 파일이 빠집니다.

## 읽는 순서

1. [파일 형식 (SFL2·SFL3)](sfl-format.md) — NSKeyedArchiver 틀, 형식별 루트·항목 키, 북마크의 머리·TOC·키 번호와 big-endian 날짜를 헥스 예시로 따라갑니다.
2. [앱별 최근 문서 (Recent Documents)](app-recent-documents.md) — 앱마다 따로 있는 Open Recent 목록의 위치와 옛 plist, Office 의 최근 파일 기록을 다룹니다.
3. [최근 앱·서버·폴더 (Recent Apps·Servers)](recent-apps-servers.md) — 최근 앱·서버·즐겨찾기 볼륨 목록과, 파인더·전역 설정 plist 에 남는 최근 폴더·검색·서버 주소를 정리합니다.

## 함께 볼 페이지

- [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md) — 바이너리 plist 와 NSKeyedArchiver 를 읽을 때
- [파일 참조 데이터 (Alias·Bookmark)](../../../01-foundations/value-decoding/alias-bookmark.md) — 북마크·Alias 형식 전체
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md) — 북마크 안 날짜를 바꿀 때
- [파인더 설정과 기록 (Finder plist)](../finder-plist.md)
- [USB 저장 장치 (USB Storage)](../../external-devices/usb/index.md) — 북마크의 볼륨 정보를 장치 기록과 맞출 때
- [공유 폴더 연결 기록 (SMB·AFP)](../../network/network-shares.md)
- [이 파일을 누가 언제 열었나 (File Access)](../../../04-scenarios/activity/file-access.md)
- [지운 파일의 흔적 찾기 (Deleted File Traces)](../../../04-scenarios/activity/deleted-file-traces.md)

## 참고 문헌

1. mac_apt `plugins/recentitems.py` (RECENTITEMS 1.5, Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/recentitems.py
2. macMRU-Parser `macMRU.py` (Sarah Edwards / mac4n6, 2017) — https://raw.githubusercontent.com/mac4n6/macMRU-Parser/master/macMRU.py
3. ForensicArtifacts `artifacts/data/macos.yaml` — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
4. SFL-Parser README (Hochschule für Polizei Baden-Württemberg) — https://github.com/mb4n6/SFL-Parser
5. exhume_artefacts `src/parsers/macos/sharedfilelist.rs` (forensicxlab) — https://github.com/forensicxlab/exhume_artefacts/blob/main/src/parsers/macos/sharedfilelist.rs
6. MacOS-Velociraptor-Collectors README (MrJayTechie) — https://github.com/MrJayTechie/MacOS-Velociraptor-Collectors
