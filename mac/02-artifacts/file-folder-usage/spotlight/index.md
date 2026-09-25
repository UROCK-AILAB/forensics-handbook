---
title: "스포트라이트"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 830
has_children: true
has_toc: false
---

# 스포트라이트 (Spotlight)

스포트라이트 (Spotlight)는 맥의 파일 내용과 앱 데이터를 검색하려고 만드는 색인이고, 볼륨 색인·사용자 색인·검색창 입력 기록 세 갈래에 파일의 출처와 마지막 사용 시각, 사용자가 친 검색어가 남습니다.

## 왜 중요한가

스포트라이트는 macOS와 iOS 모두에서 파일 시스템 내용과 앱 데이터를 색인하고 [2], 색인에는 항목마다 `kMDItemWhereFroms`(어디서 받았나), `kMDItemLastUsedDate`(마지막 사용) 같은 속성 값이 들어 있습니다 [4][5]. 그래서 파일을 어디서 받았는지, LaunchServices를 거쳐 마지막으로 언제 열었는지를 파일 시스템 시각과 따로 확인할 수 있습니다. 여기에 사용자가 스포트라이트 검색창에 친 글자와 그 글자로 연 앱·문서의 기록이 더해지면 [3], 계정별로 무엇을 찾아 열었는지까지 볼 수 있습니다.

해석은 조심해야 합니다. 볼륨 색인 파일은 SQLite가 아닌 자체 형식이고 공개 명세가 시험한 범위는 macOS 13 Ventura까지라서 [1], 그 뒤 버전에서는 도구 결과가 온전한지 먼저 확인합니다. 한 저장소 안에 유닉스 마이크로초와 Cocoa 시각이 섞여 있고 [1], 도구가 뽑는 속성 가운데 일부는 Apple 문서에 뜻이 적혀 있지 않습니다 [4][5]. 색인은 `mdutil` 명령으로 끄거나 지울 수 있어서 [6], 색인이 비었거나 꺼져 있으면 그 자체를 확인할 사항으로 봅니다.

## 한눈에 보기

| 흔적 | 위치(대표) | macOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 볼륨 색인 저장소 | `/.Spotlight-V100/Store-V2/`, `/System/Volumes/Data/.Spotlight-V100/Store-V2/` 등 [1][4] | 볼륨마다. 부트 볼륨 저장소는 10.15 Catalina의 읽기 전용 볼륨용 [4] | 항목의 식별자·부모 식별자·색인 갱신 시각과 속성 값 [1] |
| 사용자 CoreSpotlight 색인 | `~/Library/Metadata/CoreSpotlight/` 아래 `index.spotlightV3` [1][2][4] | 10.13 이후, 12 이후 보호 등급별 폴더 [2][4] | 사용자 단위 색인 항목과 속성 값 |
| 메타데이터 속성 | 위 두 색인 안 | 공통 속성 문서는 OS X 10.4 이후 기준 [5] | 출처 URL, 마지막 사용 시각, 작성자, 만든 앱 등 [5] |
| 검색 기록 (Spotlight Shortcuts) | 버전마다 다름. 14 이후 `~/Library/Group Containers/group.com.apple.spotlight/` [3] | 10.9 이하부터 14 이후까지 경로가 네 번 바뀜 [3] | 검색창에 친 글자, 연 항목 이름·위치, 마지막 사용 시각 [3] |

공개 도구로는 텍스트 결과를 내는 spotlight_parser [2]와, 사용자·볼륨·iOS 색인을 읽는 mac_apt SPOTLIGHT 플러그인 [4], 검색 기록을 읽는 SPOTLIGHTSHORTCUTS 플러그인 [3]이 있습니다.

## 읽는 순서

1. [색인 저장소 구조 (.Spotlight-V100·store.db)](store-structure.md) — 볼륨·사용자 색인의 버전별 위치와 `store.db` 의 헤더·페이지·레코드 구조, 두 가지 시각 기준을 헥스 예시로 따라가고, `mdutil` 로 색인을 지운 경우도 다룹니다.
2. [메타데이터 속성 (kMDItem)](metadata-attributes.md) — Apple 문서에 있는 속성과 도구만 뽑는 속성을 나누고, 마지막 사용 시각·출처·작성자 값이 증명하는 것과 증명하지 못하는 것을 정리합니다.
3. [검색 기록 (Spotlight Shortcuts)](search-history.md) — 검색창에 친 글자와 연 항목을 담는 plist의 버전별 경로와 키 구조, 해석할 때 확인할 점을 다룹니다.

## 함께 볼 페이지

- [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md) — 검색 기록 파일을 읽을 때
- [압축 형식 (LZFSE·LZ4·zlib)](../../../01-foundations/value-decoding/compression.md) — 색인 페이지의 압축을 풀 때
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md) — 유닉스 시각과 Cocoa 시각을 바꿀 때
- [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../../../01-foundations/disk-volume/volume-group-firmlinks.md) — 데이터 볼륨 쪽 색인 경로를 이해할 때
- [다운로드 출처 속성 (kMDItemWhereFroms)](../../filesystem/where-froms.md) — 내려받은 파일의 출처를 따질 때
- [최근 항목 (Shared File Lists)](../recent-items/index.md) — 문서를 연 기록과 맞춰 볼 때
- [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md) — 색인 폴더나 검색 기록 파일이 지워진 흔적을 찾을 때
- [이 파일을 누가 언제 열었나 (File Access)](../../../04-scenarios/activity/file-access.md)
- [이 파일은 어디서 왔나 (File Origin)](../../../04-scenarios/activity/file-origin.md)
- [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)

## 참고 문헌

1. Apple Spotlight store database file format (libyal/dtformats, Joachim Metz, 0.0.3, 2024-01) — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/Apple%20Spotlight%20store%20database%20file%20format.asciidoc
2. spotlight_parser README (Yogesh Khatri) — https://github.com/ydkhatri/spotlight_parser
3. mac_apt 플러그인 spotlightshortcuts.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/spotlightshortcuts.py
4. mac_apt 플러그인 spotlight.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/spotlight.py
5. Apple, Spotlight Metadata Attributes Reference — Common Attributes (Documentation Archive, 2014-07-15) — https://developer.apple.com/library/archive/documentation/CoreServices/Reference/MetadataAttributesRef/Reference/CommonAttrs.html
6. SS64, mdutil — https://ss64.com/mac/mdutil.html
