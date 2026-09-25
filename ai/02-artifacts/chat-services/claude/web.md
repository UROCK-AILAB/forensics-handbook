---
title: "Claude 웹 브라우저"
parent: "Claude"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 150
---

# 웹 브라우저 (Web)

브라우저로 claude.ai 에 접속해 쓴 Claude 는 대화를 계정 서버에 저장하고, 사용자 PC 에는 브라우저가 어느 사이트에서나 남기는 방문 기록·쿠키·캐시·사이트 저장소만 남깁니다.

## 무엇이 남나 · 왜 생기나

웹판은 따로 설치하는 프로그램 없이 브라우저 탭 안에서 돌아서, 기기에 남는 흔적은 모두 브라우저가 만든 것입니다. 대화는 계정에 묶여 서버에 저장되고, 개인정보 안내 문서는 사용자가 지운 대화를 대화 목록에서 바로 감추고 서버 저장소에서는 30일 안에 지운다고 설명합니다[2]. 이 문서는 보관과 삭제를 모두 서버 저장소 기준으로 설명하므로, 대화 내용은 브라우저보다 계정 쪽 자료에서 먼저 찾습니다. 보관 기간과 모델 개선 설정은 [Claude](index.md) 허브와 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에 모아 두었습니다.

브라우저 쪽에는 claude.ai 주소를 연 방문 기록, claude.ai 도메인의 쿠키, 받은 페이지 자원이 들어간 캐시가 남고, 사이트가 쓰는 Local Storage·IndexedDB 같은 사이트 저장소도 생길 수 있습니다. 사이트 저장소에 어떤 키가 있는지, 대화 본문이 들어가는지는 공개된 분석 자료가 없어 검체에서 claude.ai 출처 항목을 열어 확인합니다. 저장소의 파일 형식과 위치는 브라우저마다 달라서 아래 브라우저 페이지를 따릅니다.

## 위치

| 흔적 | 어디서 보나 | 알 수 있는 것 | 근거 |
|---|---|---|---|
| 방문 기록 | 브라우저 프로필의 방문 기록 | claude.ai 주소를 연 시각과 횟수 | 브라우저 공통 원리 |
| 쿠키 | 브라우저 쿠키 저장소 | claude.ai 도메인 쿠키가 있었는지, 쿠키에 적힌 시각 | 브라우저 공통 원리 |
| 캐시 | 브라우저 캐시 | 받은 페이지 자원 | 브라우저 공통 원리(대화 내용이 들어가는지는 검체로 확인) |
| 사이트 저장소 | Local Storage·IndexedDB | 검체에서 claude.ai 출처 항목으로 확인 | 공개 분석 자료 없음 |
| 대화 원본 | 계정 서버 | 대화 제목·본문·시각 | [2] |

브라우저별 파일 위치와 형식은 다음 페이지에 있습니다.

| 기기 | 페이지 |
|---|---|
| Windows 의 크롬 계열 | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html), [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html) |
| macOS 의 사파리 | [사파리](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/browsers/safari/index.html), [LevelDB와 IndexedDB](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/leveldb-indexeddb.html) |
| Android 의 크롬 | [크롬 (Chrome for Android)](https://urock-ailab.github.io/forensics-handbook-android/02-artifacts/browsers/chrome/index.html) |
| iPhone·iPad 의 브라우저 | [사파리](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/safari/index.html), [크롬 (Chrome for iOS)](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/chrome.html) |

## 계정 쪽 자료

웹에서는 이니셜 메뉴의 Settings > Privacy 에서 "Export data" 로 계정 데이터를 내보낼 수 있습니다[1]. 대화 본문과 시각이 필요하면 내보내기 자료가 브라우저 흔적보다 직접적이고, 내보내기 파일의 짜임은 [계정 데이터 내보내기](export.md)에서, 수집 절차는 [계정 데이터 내보내기로 수집](../../../03-techniques/acquisition/export-collection.md)에서 다룹니다. 사용자 협조를 받을 수 없으면 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)을 검토합니다.

## 증거로서 의미

**증명하는 것.** 방문 기록에 claude.ai 가 있으면 이 브라우저 프로필에서 그 시각에 claude.ai 주소를 연 기록이 있다고 쓸 수 있습니다. claude.ai 도메인 쿠키가 있으면 이 프로필로 사이트에 접속한 적이 있다고 쓸 수 있습니다. 로그인 세션을 담은 쿠키인지는 쿠키 이름으로 가려야 하는데, 쿠키 이름의 뜻을 밝힌 공개 자료가 없으므로 "로그인했다"까지는 쓰지 않습니다.

**증명하지 못하는 것.** 방문 기록과 쿠키만으로는 무엇을 입력했는지, 어느 계정으로 들어갔는지, 그때 누가 키보드 앞에 있었는지 알 수 없습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 방문 기록이 없어도 쓰지 않았다고 보지 않습니다. 브라우저의 시크릿 창으로 열었을 수 있고, 기록을 지웠을 수 있고, 다른 기기나 데스크톱 앱으로 썼을 수도 있습니다.

## 시각 해석

방문 기록과 쿠키 시각의 형식과 기준 시간대는 브라우저마다 달라서 각 브라우저 페이지의 시각 절을 따릅니다. 방문 시각은 페이지를 연 때이고 메시지를 보낸 때가 아닙니다. 탭 하나를 오래 열어 두고 여러 대화를 이어 갈 수 있어서, 방문 기록 한 줄을 대화 하나로 세지 않습니다. 대화와 메시지마다의 시각은 내보내기 자료에서 읽고([계정 데이터 내보내기](export.md)), 두 자료를 한 줄로 맞추는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

브라우저의 시크릿 창과 Claude 의 시크릿 대화 (Incognito chat) 는 서로 다른 기능입니다. 브라우저 시크릿 창은 브라우저 쪽 기록을 줄이는 기능이고, Claude 의 시크릿 대화는 서비스 안의 대화 방식입니다. 개인정보 안내 문서는 Claude 의 시크릿 대화를 모델 개선 설정을 켜 두었어도 개선에 쓰지 않는다고 설명하지만[2], 시크릿 대화를 얼마나 보관하는지와 대화 목록에 보이는지는 그 시점의 공식 도움말에서 따로 확인합니다.

대화를 지우면 목록에서는 바로 사라지고 서버 저장소에서는 30일 안에 지웁니다[2]. 이 설명대로라면 목록에 없는 대화도 지운 지 30일이 지나지 않았으면 서버 쪽에 아직 남아 있을 수 있습니다. 지운 대화가 내보내기 자료에 들어가는지는 공개된 자료가 없어, 시험용 계정에서 대화를 지운 뒤 내보내 보고 확인합니다.

Windows 데스크톱 앱은 앱 패키지 폴더 안에 크롬 계열 저장소를 따로 두어서, 브라우저 프로필만 보면 앱으로 쓴 흔적을 놓칩니다([Windows 앱](windows.md)). macOS 앱의 저장 위치는 [macOS 앱](macos.md)에서 다룹니다. 반대로 브라우저에 들어간 다른 회사의 AI 기능이 남긴 기록과 claude.ai 방문을 섞지 않도록 [브라우저에 들어간 AI](../../office-integrations/browser-builtin-ai.md)도 함께 봅니다.

## 직접 분석해 보기

claude.ai 가 브라우저에 두는 값은 공개된 분석 자료가 없어서 이 페이지에는 헥스 예시를 싣지 않습니다. 브라우저 파일을 헥스로 따라가는 방법은 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html)와 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html) 페이지에 있습니다. 공개 도구로는 다음 순서로 봅니다.

1. 브라우저를 닫은 상태에서 프로필 폴더를 통째로 사본으로 뜹니다. 데이터베이스 옆의 저널·WAL 파일도 함께 가져옵니다.
2. 방문 기록 데이터베이스를 SQLite 도구(예: DB Browser for SQLite)로 열어 주소에 claude.ai 가 들어간 줄만 거릅니다.
3. 쿠키 저장소에서 claude.ai 도메인의 쿠키가 있는지, 쿠키에 적힌 시각이 방문 기록과 맞는지 봅니다.
4. 사이트 저장소 폴더에서 claude.ai 출처에 해당하는 항목이 있는지 LevelDB 도구로 확인합니다.
5. 계정 데이터 내보내기 자료가 있으면 대화 시각과 방문 시각을 나란히 놓습니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 브라우저 기록을 지웠어도 DNS·프록시 쪽에 남은 접속 |
| [계정 데이터 내보내기](export.md) | 대화 제목·본문·시각 |
| [Claude 기업용 감사 로그](../../network-enterprise/claude-enterprise.md) | 조직 계정이면 관리자 쪽 기록 |
| [Windows 앱](windows.md), [macOS 앱](macos.md) | 같은 PC 에서 데스크톱 앱으로도 썼는지 |

## 실습

직접 만든 시험용 브라우저 프로필이나 공개 검체(NIST CFReDS 등)의 브라우저 프로필로 다음을 풀어 봅니다.

1. 방문 기록에서 claude.ai 를 처음 연 시각과 마지막으로 연 시각은 언제이고, 그 시각은 UTC 인가 현지 시각인가?
2. claude.ai 도메인 쿠키의 시각과 방문 기록 시각이 어긋난다면, 무엇이 먼저 생겼고 그 차이를 어떻게 설명할 수 있는가?
3. 같은 PC 에 데스크톱 앱 폴더도 있다면, 브라우저 흔적과 앱 흔적 가운데 어느 쪽이 더 최근인가?

## 참고 문헌

1. How can I export my Claude data? (Claude Help Center) — https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-data
2. How long do you store my data? (Anthropic Privacy Center) — https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data
