---
title: "ChatGPT 웹 브라우저"
parent: "ChatGPT"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 80
---

# 웹 브라우저 (Web)

브라우저로 쓰는 ChatGPT 는 대화를 서버에서 불러와 탭 안에 보여 주기 때문에, 기기에는 방문 기록·다운로드 기록·브라우저 저장소 같은 브라우저 쪽 흔적과 사용자가 따로 내보낸 파일이 남을 수 있습니다.

> 확인 날짜: 2026-09. 공개 도구 문서(2026-09-25 열람)를 바탕으로 썼습니다. OpenAI 공식 도움말은 열람하지 못했고, 이 핸드북은 기기에서 ChatGPT 웹 판의 브라우저 저장소를 관찰하지 못했습니다. 그래서 쿠키 이름, 저장소 키, 방문 기록에 남는 대화 주소의 모양은 적지 않았습니다.

## 무엇이 남나 · 왜 생기나

웹 판은 따로 설치하는 프로그램 없이 브라우저 탭 안에서 돌아갑니다. 오픈소스 사용자 스크립트 chatgpt-exporter 의 문서는 대화 하나를 아래 주소에서 받아 JSON 으로 저장한다고 적었고, 이 설명대로라면 브라우저는 대화를 서버 API 에서 받아 와 화면에 그립니다.

```
https://chat.openai.com/backend-api/conversation/[id]
```

이 주소의 `chat.openai.com` 은 도구 문서에 적힌 옛 도메인이고, 같은 문서는 이 스크립트가 `chat.openai.com` 과 `chatgpt.com` 두 곳에서 돌아간다고 적었습니다(2026-09-25 열람). `chatgpt.com` 에서 쓰는 API 주소의 모양은 이번 조사에서 확인하지 못했습니다. 대화 원본이 어디에 있는지는 [ChatGPT](index.md) 허브에서 정리했고, 서버·기기·동기화의 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다. 이 페이지는 브라우저 쪽에 남는 흔적만 봅니다.

브라우저 흔적은 대부분 ChatGPT 만의 것이 아니고, 어느 웹 서비스를 쓰든 브라우저가 똑같이 남기는 기록입니다. 아래 표는 흔적의 종류와 조사에서 쓸 수 있는 쓰임을 정리한 것이고, ChatGPT 에 맞춰 확인한 내용이 있는지도 함께 적었습니다.

| 흔적 | 조사에서 쓰는 곳 | ChatGPT 쪽 확인 상태 |
|---|---|---|
| 방문 기록 | 서비스 주소를 연 시각과 횟수 | 대화 주소의 모양은 확인하지 못함 |
| 쿠키 | 그 브라우저 프로필에 로그인 흔적이 있었는지 | 쿠키 이름은 확인하지 못함 |
| Local Storage·IndexedDB | 웹 앱이 브라우저에 남긴 데이터 | 키 이름, 대화 사본이 있는지 확인하지 못함 |
| 캐시 | 받아 온 응답·그림 조각 | 대화 조각이 남는지 확인하지 못함 |
| 다운로드 기록과 다운로드 폴더 | 서비스에서 내려받은 파일 | 해당 없음(브라우저 공통) |
| 확장 프로그램·사용자 스크립트 | 대화를 파일로 뽑는 도구를 설치했는지 | chatgpt-exporter 문서로 기능 확인 |

## 위치와 OS별 차이

브라우저 프로필 폴더의 위치와 저장 형식은 ChatGPT 가 아니라 브라우저와 OS 에 따라 정해집니다. 쓰인 브라우저를 먼저 가린 뒤 해당 판의 페이지를 따라갑니다.

| OS | 브라우저 | 구조 설명 |
|---|---|---|
| Windows | 크롬·엣지·웨일 등 크롬 계열 | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html) |
| macOS | 사파리 | [사파리](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/browsers/safari/index.html) |
| Android | 크롬 | [크롬 (Chrome for Android)](https://urock-ailab.github.io/forensics-handbook-android/02-artifacts/browsers/chrome/index.html) |
| iOS | 사파리, 크롬 | [사파리](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/safari/index.html), [크롬 (Chrome for iOS)](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/chrome.html) |

Local Storage 와 IndexedDB 는 크롬 계열에서 LevelDB 파일로 남아서 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html) 페이지의 읽는 법을 그대로 씁니다. 같은 기기에 전용 앱도 깔려 있다면 앱 쪽 흔적은 [Windows 앱](windows.md), [macOS 앱](macos.md), [Android 앱](android.md), [iOS 앱](ios.md)에서 따로 봅니다.

## 내보내기 도구의 흔적

chatgpt-exporter 는 Tampermonkey 에 올려 쓰는 사용자 스크립트이고 GreasyFork 에서 배포하며 MIT 라이선스입니다. 문서에 따르면 대화를 Text·HTML·Markdown·PNG·JSON 형식으로 내보낼 수 있고, "Export All" 기능으로 여러 대화를 골라 한꺼번에 내보내거나(JSON 을 ZIP 으로 묶는 선택지 포함) 보관하거나 지울 수 있습니다. 이 도구를 예로 든 까닭은 공개 문서로 기능을 확인할 수 있어서이고, 비슷한 스크립트와 확장 프로그램은 여럿 있을 수 있습니다.

조사에서는 이런 스크립트나 확장이 설치돼 있으면 사용자가 대화를 파일로 뽑았을 가능성을 두고 다운로드 폴더의 파일과 브라우저 다운로드 기록을 함께 봅니다. 이 해석은 일반론이고 도구 문서가 주장하는 내용은 아닙니다. 문서에 여러 대화를 한꺼번에 지우는 기능도 적혀 있어서, 계정에서 대화가 한꺼번에 사라졌다면 이런 도구를 썼을 가능성도 따져 봅니다. 서비스 설정에서 받는 공식 내보내기 파일은 [계정 데이터 내보내기](export.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 방문 기록에 서비스 주소가 있으면 그 브라우저 프로필에서 그 주소를 연 기록이 있다고 쓸 수 있습니다. 다운로드 폴더에 내보낸 파일이 있으면 그 파일이 기기에 저장돼 있었다고 쓸 수 있고, 확장·사용자 스크립트 목록에 내보내기 도구가 있으면 그 도구가 설치돼 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** 방문 기록은 무엇을 입력했는지 알려 주지 않고, 대화 내용은 서버에 있어서 기기만으로는 확인하기 어렵습니다. 프로필에 로그인 흔적이 있어도 그 시각에 누가 키보드 앞에 있었는지는 따로 따져야 합니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 방문 기록이 없다고 쓰지 않았다고 볼 수도 없는데, 시크릿 창을 썼거나 기록을 지웠거나 다른 기기에서 썼을 수 있기 때문입니다.

## 시각 해석

방문 기록의 시각 형식과 기준(UTC 인지 현지 시각인지)은 브라우저마다 달라서 위 표의 브라우저 페이지를 따릅니다. 탭 하나를 열어 둔 채 여러 번 주고받을 수 있어서, 방문 기록의 시각은 페이지를 연 때에 가깝고 메시지를 보낸 때와 같다고 볼 수 없습니다. 내보낸 파일의 파일 시스템 시각은 파일을 저장한 때를 가리키고 대화한 때를 가리키지 않으며, 대화 시각은 파일 안의 값으로 읽습니다. 여러 출처를 한 줄로 세우는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

도메인 하나로만 걸러 내면 놓칠 수 있습니다. 도구 문서에 적힌 `chat.openai.com` 과 `chatgpt.com` 을 모두 찾아보고, 서비스가 쓰는 도메인 목록은 [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)과 맞춰 봅니다.

브라우저 저장소나 캐시에 대화 사본이 남는지는 확인하지 못해서, 캐시에서 대화를 되살릴 수 있다고 미리 단정하지 않습니다. 되살리는 방법과 한계는 [대화 내용 되살리기](../../../03-techniques/analysis/content-recovery.md)에 있습니다.

브라우저 안에 들어간 AI 기능(엣지의 Copilot 등)이나 브라우저를 조작하는 AI 는 ChatGPT 웹 판과 다른 흔적을 남깁니다. 헷갈리면 [브라우저에 들어간 AI](../../office-integrations/browser-builtin-ai.md)와 [브라우저를 조작하는 AI](../../agentic-services/browser-agents.md)를 봅니다. 회사 계정이라면 기기 밖의 감사 기록이 더 많은 것을 알려 줄 수 있어서 [ChatGPT 기업용 감사 기록](../../network-enterprise/chatgpt-enterprise.md)도 확인합니다.

## 직접 분석해 보기

**헥스로 한 번.** LevelDB 파일이나 캐시 파일을 헥스 편집기로 열어 도메인 문자열을 찾아보면, 그 출처가 남긴 기록이 어느 파일에 있는지 가늠할 수 있습니다. 아래는 ASCII 명세로 만든 예시이고 실제 파일에서 뜬 것이 아닙니다. ASCII 로 찾아지지 않으면 글자마다 `00` 이 끼어드는 UTF-16 모양으로도 찾아봅니다.

```
만든 예시(ASCII 명세로 만든 바이트)
63 68 61 74 2E 6F 70 65 6E 61 69 2E 63 6F 6D     chat.openai.com
```

**공개 도구로 한 번.** 브라우저 기록은 위 표의 브라우저별 페이지에 적힌 공개 도구로 읽습니다. 순서는 다음과 같습니다.

1. 기기에 깔린 브라우저와 프로필을 가립니다.
2. 방문 기록에서 서비스 도메인을 찾아 처음과 마지막 방문 시각, 방문 횟수를 적습니다.
3. 다운로드 기록과 다운로드 폴더에서 같은 시간대에 받은 파일을 찾습니다.
4. 확장 프로그램과 사용자 스크립트 목록에서 대화 내보내기 도구가 있는지 봅니다.
5. Local Storage·IndexedDB 에서 서비스 출처의 기록이 있는지 보고, 있으면 내용을 해석하기 전에 무엇이 들었는지부터 적습니다.

## 교차 검증

기기의 방문 기록은 [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)의 DNS·프록시 기록이나 [보안 제품이 남기는 AI 사용 기록](../../network-enterprise/dlp-casb.md)과 시간대를 맞춰 봅니다. 대화 내용은 기기보다 계정 쪽에 있어서, 적법한 절차 안에서 [계정 데이터 내보내기로 수집](../../../03-techniques/acquisition/export-collection.md)하거나 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)으로 확보해 브라우저 흔적과 맞춥니다.

## 실습

공개 검체 가운데 ChatGPT 웹 사용을 담은 것은 이번에 찾지 못했습니다. 가상 머신에 브라우저를 깔고 시험용 계정으로 가짜 대화를 몇 개 만든 뒤 다음을 풀어 봅니다.

1. 방문 기록에 대화마다 다른 주소가 남는지, 대화를 열 때마다 새 줄이 생기는지 확인합니다.
2. Local Storage·IndexedDB 에 대화 제목이나 본문이 평문으로 남는지 확인합니다.
3. 로그아웃하고 브라우저 기록을 지운 뒤 무엇이 남는지 봅니다.

## 참고 문헌

- GitHub, pionxzh/chatgpt-exporter README — https://github.com/pionxzh/chatgpt-exporter
