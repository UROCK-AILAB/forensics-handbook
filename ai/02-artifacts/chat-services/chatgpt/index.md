---
title: "ChatGPT"
parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 70
has_children: true
has_toc: false
---

# ChatGPT (ChatGPT)

ChatGPT 는 웹·Windows·macOS·Android·iOS 에서 쓰는 대화형 AI 서비스이고, 대화가 계정에 묶여 서버 쪽에 남는 것으로 보여서 기기 흔적과 계정 데이터 내보내기를 함께 봐야 대화 내용과 사용 기기를 모두 설명할 수 있습니다.

> 확인 날짜: 2026-09-25. App Store·Google Play·Microsoft Store 페이지, 공개 도구 설명서, 9to5Mac 보도를 바탕으로 썼습니다. OpenAI 공식 도움말과 개인정보 처리방침은 열람하지 못해서(HTTP 403) 서버 보관 기간과 내보내기 절차의 세부는 공식 문서로 확인하지 못했습니다. 이 핸드북의 기기 관찰(Windows 11, 2026-09)에서도 ChatGPT 폴더·파일·설정 키·DB 는 관찰하지 못했습니다.

## 왜 중요한가

ChatGPT 는 여러 기기에서 같은 계정으로 쓰는 서비스라, 한 기기에서 흔적을 찾지 못해도 다른 기기나 웹에서 쓴 기록이 계정에 남아 있을 수 있습니다. 대화 원본이 서버의 계정 쪽에 있고 기기에는 앱이 남기는 사본·캐시만 있다는 점은 공식 문서로 확인하지 못했지만, 내보내기가 계정 설정에서 서버 데이터를 ZIP 파일로 받는 방식이라서 그렇게 볼 만합니다. 다만 이 점만으로 기기에 대화 사본이 없다고 볼 수는 없습니다. 서버·기기·동기화에 데이터가 나뉘어 있는 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다.

기기 쪽 사본의 모양은 판마다 다르고 자주 바뀝니다. macOS 앱은 2024-07 보도 당시 대화를 평문으로 저장했다가 그 뒤 업데이트로 암호화했는데, 이처럼 같은 앱이라도 버전에 따라 기기에 남는 것이 달라서 앱 버전과 확인 날짜를 먼저 적습니다. 지운 대화와 임시 채팅을 서버에 얼마나 두는지는 공식 도움말을 열지 못해 확인하지 못했고, 조사 때 그 시점의 공식 도움말에서 다시 확인합니다. 보관 설정의 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

## 한눈에 보기

판마다 위치와 확인한 범위가 다릅니다. 개발사 표기도 곳마다 달라서 App Store 에는 "OpenAI OpCo, LLC", Google Play 데이터 안전 페이지에는 "OpenAI" 로 적혀 있습니다.

| 판 | 위치·식별자 | 확인한 버전 | 알려 주는 것 |
|---|---|---|---|
| 웹 브라우저 | 브라우저 저장소(쿠키·저장소 키는 확인하지 못함) | 해당 없음 | 방문·다운로드 기록, 사용자가 따로 내보낸 파일 |
| Windows 앱 | Microsoft Store 제품 ID `9NT1R1C2HH7J`(2026-09-25 제목 "ChatGPT Classic") | 확인하지 못함 | 설치 흔적(데이터 위치는 확인하지 못함) |
| macOS 앱 | `~/Library/Application Support/com.openai.chat`(2024-07 보도 당시 판) | 고친 판의 버전 번호는 보도에 없음 | 보도 당시 판은 평문 대화, 뒤의 판은 암호화한 대화 |
| Android 앱 | 패키지 `com.openai.chatgpt` | 확인하지 못함 | Play 데이터 안전 항목의 수집 범위(기기 데이터 위치는 확인하지 못함) |
| iOS 앱 | App Store 항목 `id6448311069` | 1.2026.258(2026-09-25 기준 최신) | 개인정보 라벨, 앱 내 결제 항목(컨테이너 안 파일은 확인하지 못함) |
| 계정 데이터 내보내기 | 계정 설정의 내보내기로 받는 ZIP, 주 데이터 파일 `conversations.json` | 해당 없음 | 메시지의 작성자 역할·작성 시각·본문 |

## 읽는 순서

1. [웹 브라우저](web.md) — 브라우저로 쓴 흔적과 사용자 스크립트로 뽑은 대화 파일을 봅니다.
2. [Windows 앱](windows.md) — Microsoft Store 항목과, 공개 자료로 확인하지 못한 앱 데이터 위치를 정리합니다.
3. [macOS 앱](macos.md) — 2024-07 평문 저장 보도와 그 뒤 암호화한 판을 가르는 방법을 봅니다.
4. [Android 앱](android.md) — 패키지 이름과 Google Play 데이터 안전 항목을 해석합니다.
5. [iOS 앱](ios.md) — App Store 항목의 버전 형식, 개인정보 라벨, 결제 항목을 봅니다.
6. [계정 데이터 내보내기](export.md) — 내보내기 ZIP 과 `conversations.json` 의 메시지 칸을 읽습니다.

## 함께 볼 페이지

- [ChatGPT 에이전트 모드](../../agentic-services/chatgpt-agent.md) — 에이전트 기능으로 실행한 작업의 흔적
- [ChatGPT 기업용 감사 기록](../../network-enterprise/chatgpt-enterprise.md) — 조직 계정의 기록을 관리자 쪽에서 가져가는 경로
- [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) — 접속 시각과 기기를 네트워크 쪽에서 확인
- [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md) — 서비스마다 다른 내보내기 형식 비교
- [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md) — 계정 주인의 협조 없이 서버 쪽 기록을 확보하는 절차
- [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md) — 계정 기록과 실제 입력한 사람을 잇는 방법

## 참고 문헌

1. 9to5Mac, "ChatGPT for Mac stored conversations in plain text"(2024-07-03, 뒤에 업데이트 덧붙음) — https://9to5mac.com/2024/07/03/chatgpt-macos-conversations-plain-text/
2. App Store, ChatGPT (OpenAI OpCo, LLC) — https://apps.apple.com/us/app/chatgpt/id6448311069 (2026-09-25 열람)
3. Google Play, ChatGPT 데이터 안전 — https://play.google.com/store/apps/datasafety?id=com.openai.chatgpt (2026-09-25 열람)
4. Microsoft Store, ChatGPT Classic (9NT1R1C2HH7J) — https://apps.microsoft.com/detail/9nt1r1c2hh7j (2026-09-25 열람, 제목만 읽힘)
5. GitHub, mohamed-chs/convoviz README — https://github.com/mohamed-chs/convoviz (2026-09-25 열람)
6. GitHub, pionxzh/chatgpt-exporter README — https://github.com/pionxzh/chatgpt-exporter (2026-09-25 열람)
