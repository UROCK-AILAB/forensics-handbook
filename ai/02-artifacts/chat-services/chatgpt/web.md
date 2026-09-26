---
title: "ChatGPT 웹 브라우저"
parent: "ChatGPT"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 80
---

# 웹 브라우저 (Web)

브라우저로 쓰는 ChatGPT 는 대화를 서버에서 불러와 탭 안에 보여 주기 때문에, 기기에는 방문 기록·다운로드 기록·브라우저 저장소 같은 브라우저 쪽 흔적과 사용자가 따로 내보낸 파일이 남을 수 있습니다.

주소 모양과 저장소 키는 서비스가 바뀌면 달라질 수 있습니다[1][2].

## 무엇이 남나 · 왜 생기나

웹 판은 따로 설치하는 프로그램 없이 브라우저 탭 안에서 돌아갑니다. 브라우저는 대화를 서버 API 에서 받아 와 화면에 그립니다. API 주소는 아래와 같습니다[1][2].

```
https://chat.openai.com/backend-api/conversation/[id]     chatgpt-exporter 문서 [1]
https://chatgpt.com/backend-api/conversation/[id]         chatgpt-forensic-exporter 코드 [2]
https://chatgpt.com/c/[id]                                chatgpt-forensic-exporter 코드 [2] (대화 화면 주소)
```

`chat.openai.com` 은 옛 도메인이고, ChatGPT 는 `chat.openai.com` 과 `chatgpt.com` 두 도메인에서 모두 열립니다[1][2]. 대화 원본이 어디에 있는지는 [ChatGPT](index.md) 허브에서 정리했고, 서버·기기·동기화의 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다. 이 페이지는 브라우저 쪽에 남는 흔적만 봅니다.

브라우저 흔적은 대부분 ChatGPT 만의 것이 아니고, 어느 웹 서비스를 쓰든 브라우저가 똑같이 남기는 기록입니다. 아래 표는 흔적의 종류와 조사에서 쓰는 곳, 그리고 ChatGPT 에 맞춰 검체에서 볼 것을 정리한 것입니다.

| 흔적 | 조사에서 쓰는 곳 | ChatGPT 에서 볼 것 |
|---|---|---|
| 방문 기록 | 서비스 주소를 연 시각과 횟수 | `chatgpt.com/c/` 로 시작하는 주소가 있는지. 뒤에 붙은 값이 대화 ID 입니다[2] |
| 쿠키 | 그 브라우저 프로필에 로그인 흔적이 있었는지 | 두 도메인의 쿠키 목록. `oai-did` 라는 이름의 쿠키가 있는지[2] |
| Local Storage·IndexedDB | 웹 앱이 브라우저에 남긴 데이터 | Local Storage 의 `oai-did` 는 기기 ID 로 보이는 값입니다[2]. 그 밖의 키와 대화 사본은 검체에서 확인합니다 |
| 캐시 | 받아 온 응답·그림 조각 | `backend-api` 주소의 응답이 캐시에 남았는지 검체에서 확인합니다 |
| 다운로드 기록과 다운로드 폴더 | 서비스에서 내려받은 파일 | 브라우저 공통 |
| 확장 프로그램·사용자 스크립트 | 대화를 파일로 뽑는 도구를 설치했는지 | 아래 "내보내기 도구의 흔적" |

`oai-did` 는 ChatGPT 의 기기 ID 로 보이는 값입니다[2]. 어느 서비스 판에서 쓰는 이름인지 알려져 있지 않으므로, 검체의 Local Storage 와 쿠키에 같은 이름이 있는지 먼저 봅니다. 쿠키와 저장소에는 로그인 세션 값도 함께 남을 수 있는데, 이런 값은 보고서에서 가립니다. 서버에 있는 대화는 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md) 같은 법적 절차로 확보합니다.

## 위치와 OS별 차이

브라우저 프로필 폴더의 위치와 저장 형식은 ChatGPT 가 아니라 브라우저와 OS 에 따라 정해집니다. 쓰인 브라우저를 먼저 가린 뒤 해당 판의 페이지를 따라갑니다.

| OS | 브라우저 | 구조 설명 |
|---|---|---|
| Windows | 크롬·엣지·웨일 등 크롬 계열 | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html) |
| macOS | 사파리 | [사파리](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/browsers/safari/index.html) |
| Android | 크롬 | [크롬 (Chrome for Android)](https://urock-ailab.github.io/forensics-handbook/android/02-artifacts/browsers/chrome/index.html) |
| iOS | 사파리, 크롬 | [사파리](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/browsers/safari/index.html), [크롬 (Chrome for iOS)](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/browsers/chrome.html) |

Local Storage 와 IndexedDB 는 크롬 계열에서 LevelDB 파일로 남아서 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html) 페이지의 읽는 법을 그대로 씁니다. 같은 기기에 전용 앱도 깔려 있다면 앱 쪽 흔적은 [Windows 앱](windows.md), [macOS 앱](macos.md), [Android 앱](android.md), [iOS 앱](ios.md)에서 따로 봅니다.

브라우저가 켜져 있는 동안에는 탭 프로세스 메모리에도 대화가 있을 수 있습니다. 메모리를 떠서 찾는 방법은 [메모리에서 AI 흔적 찾기](../../../03-techniques/analysis/memory-analysis.md)에서 다룹니다.

## 내보내기 도구의 흔적

chatgpt-exporter 는 Tampermonkey 에 올려 쓰는 사용자 스크립트이고 GreasyFork 에서 배포하며 MIT 라이선스입니다[1]. 대화를 Text·HTML·Markdown·PNG·JSON 형식으로 내보낼 수 있고, "Export All" 기능으로 여러 대화를 골라 한꺼번에 내보내거나(JSON 을 ZIP 으로 묶는 선택지 포함) 보관하거나 지울 수 있습니다[1]. 같은 일을 하는 도구는 이것 말고도 있으므로 이름 하나로만 찾지 않습니다.

이런 스크립트나 확장이 설치돼 있으면 사용자가 대화를 파일로 뽑았을 수 있으므로, 다운로드 폴더의 파일과 브라우저 다운로드 기록을 함께 봅니다. 이런 도구에는 여러 대화를 한꺼번에 지우는 기능도 있어서[1], 계정에서 대화가 한꺼번에 사라졌다면 이런 도구를 썼는지도 따져 봅니다. 서비스 설정에서 받는 공식 내보내기 파일은 [계정 데이터 내보내기](export.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 방문 기록에 서비스 주소가 있으면 그 브라우저 프로필에서 그 주소를 연 기록이 있다고 쓸 수 있습니다. 주소가 `chatgpt.com/c/` 모양이면 뒤에 붙은 대화 ID 를 계정 쪽 자료와 맞춰 볼 수 있습니다. 다운로드 폴더에 내보낸 파일이 있으면 그 파일이 기기에 저장돼 있었다고 쓸 수 있고, 확장·사용자 스크립트 목록에 내보내기 도구가 있으면 그 도구가 설치돼 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** 방문 기록은 무엇을 입력했는지 알려 주지 않고, 대화 내용은 서버에 있어서 기기만으로는 확인하기 어렵습니다. 프로필에 로그인 흔적이 있어도 그 시각에 누가 키보드 앞에 있었는지는 따로 따져야 합니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 방문 기록이 없다고 쓰지 않았다고 볼 수도 없는데, 시크릿 창을 썼거나 기록을 지웠거나 다른 기기에서 썼을 수 있기 때문입니다.

## 시각 해석

방문 기록의 시각 형식과 기준(UTC 인지 현지 시각인지)은 브라우저마다 달라서 위 표의 브라우저 페이지를 따릅니다. 탭 하나를 열어 둔 채 여러 번 주고받을 수 있어서, 방문 기록의 시각은 페이지를 연 때에 가깝고 메시지를 보낸 때와 같다고 볼 수 없습니다. 내보낸 파일의 파일 시스템 시각은 파일을 저장한 때를 가리키고 대화한 때를 가리키지 않으며, 대화 시각은 파일 안의 값으로 읽습니다. 여러 출처를 한 줄로 세우는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

도메인 하나로만 걸러 내면 놓칠 수 있습니다. `chat.openai.com` 과 `chatgpt.com` 을 모두 찾아보고, 서비스가 쓰는 도메인 목록은 [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)과 맞춰 봅니다.

브라우저 저장소나 캐시에 대화 사본이 남는지는 공개된 분석 자료가 없어 검체로 확인해야 하므로, 캐시에서 대화를 되살릴 수 있다고 미리 단정하지 않습니다. 되살리는 방법과 한계는 [대화 내용 되살리기](../../../03-techniques/analysis/content-recovery.md)에 있습니다.

브라우저 안에 들어간 AI 기능(엣지의 Copilot 등)이나 브라우저를 조작하는 AI 는 ChatGPT 웹 판과 다른 흔적을 남깁니다. 헷갈리면 [브라우저에 들어간 AI](../../office-integrations/browser-builtin-ai.md)와 [브라우저를 조작하는 AI](../../agentic-services/browser-agents.md)를 봅니다. 회사 계정이라면 기기 밖의 감사 기록이 더 많은 것을 알려 줄 수 있어서 [ChatGPT 기업용 감사 기록](../../network-enterprise/chatgpt-enterprise.md)도 확인합니다.

## 직접 분석해 보기

**헥스로 한 번.** LevelDB 파일이나 캐시 파일을 헥스 편집기로 열어 도메인 문자열을 찾아보면, 그 출처가 남긴 기록이 어느 파일에 있는지 가늠할 수 있습니다. 아래는 ASCII 명세로 만든 예시이고 실제 파일에서 뜬 것이 아닙니다. ASCII 로 찾아지지 않으면 글자마다 `00` 이 끼어드는 UTF-16 모양으로도 찾아봅니다.

```
만든 예시(ASCII 명세로 만든 바이트)
63 68 61 74 67 70 74 2E 63 6F 6D                 chatgpt.com
63 68 61 74 2E 6F 70 65 6E 61 69 2E 63 6F 6D     chat.openai.com
6F 61 69 2D 64 69 64                              oai-did
```

**공개 도구로 한 번.** 브라우저 기록은 위 표의 브라우저별 페이지에 적힌 공개 도구로 읽습니다. 순서는 다음과 같습니다.

1. 기기에 깔린 브라우저와 프로필을 가립니다.
2. 방문 기록에서 서비스 도메인을 찾아 처음과 마지막 방문 시각, 방문 횟수를 적고, `chatgpt.com/c/` 주소가 있으면 대화 ID 를 따로 적습니다.
3. 다운로드 기록과 다운로드 폴더에서 같은 시간대에 받은 파일을 찾습니다.
4. 확장 프로그램과 사용자 스크립트 목록에서 대화 내보내기 도구가 있는지 봅니다.
5. Local Storage·IndexedDB·쿠키에서 서비스 출처의 기록이 있는지 보고, 있으면 내용을 해석하기 전에 무엇이 들었는지부터 적습니다.

## 교차 검증

기기의 방문 기록은 [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)의 DNS·프록시 기록이나 [보안 제품이 남기는 AI 사용 기록](../../network-enterprise/dlp-casb.md)과 시간대를 맞춰 봅니다. 대화 내용은 기기보다 계정 쪽에 있어서, 적법한 절차 안에서 [계정 데이터 내보내기로 수집](../../../03-techniques/acquisition/export-collection.md)하거나 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)으로 확보해 브라우저 흔적과 맞춥니다. 방문 기록에서 뽑은 대화 ID 는 계정 내보내기 파일의 대화 ID 와 맞춰 봅니다.

## 실습

가상 머신에 브라우저를 깔고 시험용 계정으로 가짜 대화를 몇 개 만든 뒤 다음을 풀어 봅니다.

1. 방문 기록에 대화마다 다른 주소가 남는지, 대화를 열 때마다 새 줄이 생기는지 확인합니다.
2. Local Storage·IndexedDB 에 대화 제목이나 본문이 평문으로 남는지, `oai-did` 키가 있는지 확인합니다.
3. 로그아웃하고 브라우저 기록을 지운 뒤 무엇이 남는지 봅니다.

## 참고 문헌

1. pionxzh, chatgpt-exporter README (2026-09-25 열람) — https://github.com/pionxzh/chatgpt-exporter
2. loucdg, chatgpt-forensic-exporter, `chatgpt_export_conversations_api.py` — https://github.com/loucdg/chatgpt-forensic-exporter
