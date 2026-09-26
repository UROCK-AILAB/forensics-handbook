---
title: "ChatGPT macOS 앱"
parent: "ChatGPT"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 100
---

# macOS 앱 (macOS)

macOS 용 ChatGPT 앱은 2024-07 보도 당시 대화를 `~/Library/Application Support/com.openai.chat` 에 평문으로 저장했고, 그 뒤 업데이트로 저장한 대화를 암호화했습니다. 그래서 조사할 때는 앱 버전부터 확인합니다.

지금 판의 암호화 방식과 키를 두는 곳은 공개된 분석 자료가 없습니다.

## 무엇이 남나 · 왜 생기나

2024-07-03 보도 당시 macOS 용 ChatGPT 앱은 대화를 사용자 라이브러리의 `Application Support` 아래 `com.openai.chat` 폴더에 평문으로 저장했고, macOS 샌드박스를 쓰지 않았습니다. 그 뒤 OpenAI 는 Mac 에 저장한 대화를 암호화하는 새 앱을 내놓았습니다. 고친 앱의 버전 번호는 알려져 있지 않습니다.

이 일로 macOS 앱은 적어도 한동안 대화 사본을 기기에 남겼다는 것을 알 수 있습니다. 대화 원본이 서버에 있다는 점과 서비스 전체의 정리는 [ChatGPT](index.md) 허브에 있습니다.

## 위치와 버전별 차이

| 시기 | 대화 저장 위치 | 저장 상태 | 샌드박스 |
|---|---|---|---|
| 2024-07 보도 당시 판 | `~/Library/Application Support/com.openai.chat` | 평문 | 쓰지 않음 |
| 보도 뒤 업데이트한 판 | 검체에서 확인 | 암호화(방식은 검체에서 확인) | 검체에서 확인 |

두 판을 가르는 버전 번호가 알려져 있지 않아서, 기기에 깔린 앱 버전을 먼저 적고 그 판이 보도 전인지 뒤인지를 설치·업데이트 시기와 함께 따집니다. 앱 버전은 앱 번들의 정보 파일에서 읽고, 이 파일의 형식은 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/data-formats/plist/index.html) 페이지에서 설명합니다. 앱을 App Store 에서 받았는지 직접 내려받았는지도 검체에서 따로 확인합니다.

지금 판이 샌드박스를 쓴다면 저장 위치가 보도 당시와 다를 수 있습니다. 그래서 표의 경로에 아무것도 없다고 앱을 쓰지 않았다고 보지 않고, 사용자 라이브러리에서 `com.openai.chat` 이 이름에 들어간 폴더를 더 찾아봅니다.

## 보호 방식

지금 판이 무엇으로 암호화하는지, 키를 어디에 두는지는 공개된 분석 자료가 없습니다. macOS 앱이 비밀 값을 둘 때 흔히 쓰는 [키체인](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/protection/keychain/index.html)의 원리는 그 페이지를 참고하되, ChatGPT 앱이 키체인을 쓴다고 단정하지 않습니다. 이 핸드북은 암호화한 대화를 푸는 방법을 다루지 않고, 파일이 평문인지 암호문인지 가르는 데까지만 봅니다. 대화 내용이 필요하면 [계정 데이터 내보내기](export.md)나 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)처럼 적법한 절차로 계정 쪽 사본을 확보합니다.

## 증거로서 의미

**증명하는 것.** 보도 당시 판의 평문 대화 파일이 남아 있으면 그 파일에 그 대화 내용이 기록돼 있었다고 쓸 수 있습니다. 앱 폴더가 있으면 그 macOS 사용자 계정에서 앱을 설치했거나 실행한 흔적이 있다고 쓸 수 있습니다.

**증명하지 못하는 것.** 파일에 대화가 있어도 그 계정으로 누가 입력했는지는 따로 따져야 합니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 암호화한 판에서는 파일이 있다는 사실만으로 대화 내용을 말할 수 없습니다. 평문 파일이 없다고 대화를 하지 않았다고 볼 수도 없는데, 업데이트한 판이거나 다른 기기·웹에서 썼을 수 있기 때문입니다.

## 시각 해석

앱 폴더 안 파일의 파일 시스템 시각은 앱이 파일을 다시 쓸 때마다 바뀔 수 있어서, 대화한 시각으로 바로 옮기지 않습니다. 폴더가 처음 생긴 때와 파일이 바뀐 흐름은 [파일 시스템 이벤트](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/fsevents/index.html)로 보강할 수 있고, 여러 기록을 시간순으로 합치는 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/analysis/timeline/index.html)과 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에서 다룹니다. 앱 업데이트 시기를 알면 보도 전 판이 언제까지 기기에 있었는지 가늠할 수 있습니다.

## 함정과 한계

업데이트할 때 예전 평문 파일을 암호화해 바꿔 썼는지, 지웠는지, 그대로 두었는지는 공개 자료에 없습니다. 그래서 업데이트한 기기에 평문 파일이 남아 있다고도, 없다고도 미리 단정하지 않고 실제로 찾아봅니다. 백업이나 이전 사본에 보도 당시 판의 폴더가 남아 있을 수도 있습니다.

이 보도는 2024-07 의 앱을 다룬 것이라 지금 판의 저장 구조를 알려 주지 않습니다. 기기에서 새로 확인한 내용은 macOS 버전, 앱 버전, 확인 날짜를 붙여 적습니다.

## 직접 분석해 보기

**헥스로 한 번.** 폴더 안 파일의 형식은 공개된 자료가 없습니다. 파일을 헥스 편집기로 열어 앞부분에 읽을 수 있는 글자(영문, UTF-8 한글, JSON 의 중괄호 등)가 이어지면 평문이고, 처음부터 바이트가 고르게 흩어져 있으면 암호화했거나 압축한 것이라고 가를 수 있습니다. 파일 앞머리에 SQLite 같은 알려진 형식의 머리 글자가 보이면 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/data-formats/sqlite/index.html) 페이지를 따라 읽습니다.

**공개 도구로 한 번.** 앱 번들의 정보 파일은 plist 를 읽는 공개 도구로 열어 버전을 적고, 앱 폴더의 파일은 형식을 확인한 다음 그 형식에 맞는 도구로 엽니다.

## 교차 검증

앱을 직접 내려받아 깔았다면 [격리 속성과 다운로드 기록](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/quarantine/index.html)에 설치 파일을 받은 기록이 남았을 수 있습니다. 같은 시간대의 접속은 [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)으로 보고, 브라우저로 쓴 흔적은 [웹 브라우저](web.md)에서 따로 봅니다.

## 실습

ChatGPT macOS 앱을 담은 공개 검체가 없으면 시험용 Mac 이나 가상 머신에 앱을 깔고 시험용 계정으로 가짜 대화를 만든 뒤 다음을 풀어 봅니다.

1. 앱 버전을 적고, `~/Library/Application Support/com.openai.chat` 이 생기는지 확인합니다.
2. 대화를 만든 뒤 바뀐 파일을 찾아 평문인지 암호문인지 가릅니다.
3. 앱을 지운 뒤 사용자 라이브러리에 무엇이 남는지 봅니다.

## 참고 문헌

- 9to5Mac, "ChatGPT for Mac stored conversations in plain text"(2024-07-03, 뒤에 업데이트 덧붙음) — https://9to5mac.com/2024/07/03/chatgpt-macos-conversations-plain-text/
