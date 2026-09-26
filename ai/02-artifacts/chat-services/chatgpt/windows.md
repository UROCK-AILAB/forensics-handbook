---
title: "ChatGPT Windows 앱"
parent: "ChatGPT"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 90
---

# Windows 앱 (Windows)

Microsoft Store 에 ChatGPT Windows 앱 항목이 있고, 2026-09-25 에 본 그 항목의 제목은 "ChatGPT Classic" 입니다. 이 앱이 기기에 남기는 파일은 공개된 분석 자료가 없어 검체로 확인해야 합니다.

## 무엇이 남나 · 왜 생기나

Windows 앱은 브라우저 없이 ChatGPT 를 쓰는 데스크톱 앱입니다. 앱이 대화를 기기에 사본으로 남기는지, 남긴다면 암호화하는지는 검체에서 확인합니다. 대화 원본이 어디에 있는지는 [ChatGPT](index.md) 허브에서 정리했고, 이 페이지는 Windows 에서 앱을 찾는 방법과 해석할 때 주의할 점을 다룹니다.

## 스토어 항목과 앱 이름

| 항목 | 값 | 근거 |
|---|---|---|
| Microsoft Store 제품 ID | `9NT1R1C2HH7J` | 스토어 페이지 주소 |
| 페이지 제목(2026-09-25) | ChatGPT Classic | 스토어 페이지 |
| 게시자·버전·요구 사양 | 조사할 때 스토어 페이지에서 확인 | — |

한 기기에 이름이 비슷한 ChatGPT 앱이 여러 개 깔려 있을 수 있으니, 앱 하나를 찾았다고 조사를 끝내지 않고 비슷한 이름의 앱이 더 있는지 봅니다. 스토어 앱의 제목과 구성은 예고 없이 바뀔 수 있어서, 조사할 때 스토어 페이지를 다시 열어 게시자·버전과 함께 날짜를 기록해 둡니다.

## 위치 찾기

스토어로 깐 앱은 사용자 프로필의 `%LOCALAPPDATA%\Packages` 아래 패키지마다 폴더를 하나씩 만들고, 그 안의 `LocalState`, `LocalCache` 같은 하위 폴더에 데이터를 둡니다. 이 구조는 스토어 앱 공통입니다. 앱 안에서 웹 화면을 띄우는 구조라면 [Electron·웹뷰 앱의 저장 구조](../../../01-foundations/storage-model/electron-webview.md)와 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)에서 설명하는 폴더가 생기므로, ChatGPT 앱 폴더에 그런 폴더가 있는지 검체에서 봅니다.

ChatGPT 앱의 패키지 폴더 이름은 공개 자료에 없으니, `Packages` 아래 폴더 이름에 ChatGPT 나 OpenAI 가 들어간 것이 있는지 찾습니다. 이름으로 찾지 못해도 앱이 없었다고 단정하지 않고, 설치된 앱 목록 같은 다른 흔적으로 한 번 더 확인합니다.

## 보호 방식

앱이 로컬 파일을 어떻게 보호하는지는 공개 자료가 없어 검체로 확인해야 합니다. Windows 앱이 로그인 정보나 저장소 키를 보호할 때 흔히 쓰는 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/protection/data-protection-api/index.html)와 [자격 증명 관리자와 볼트](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/credentials/credential-manager-windows-vault.html)는 원리만 참고하고, ChatGPT 앱이 이 방식을 쓴다고 단정하지 않습니다. 토큰이 남을 수 있는 곳의 일반론은 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에 모아 두었습니다.

## 증거로서 의미

**증명하는 것.** 패키지 폴더가 있으면 그 Windows 계정에 앱이 설치돼 있었다고 쓸 수 있습니다. 폴더 안에 사용자가 쓴 흔적(로그인 뒤에 생기는 파일 등)이 있으면 그 계정에서 앱을 실행했다고 쓸 수 있지만, 어떤 파일이 그런 흔적인지는 기기마다 직접 확인해야 합니다.

**증명하지 못하는 것.** 앱 폴더만으로는 무엇을 입력했는지 알 수 없고, 대화 사본이 로컬에 있는지도 검체로 따로 확인해야 합니다. 계정에 로그인된 상태였어도 그 시각에 누가 앱을 썼는지는 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)에서처럼 다른 기록과 맞춰야 합니다. 앱 폴더가 없어도 웹 판이나 다른 기기에서 썼을 수 있어서, 사용하지 않았다는 근거로 쓰지 않습니다.

## 시각 해석

스토어 앱은 업데이트할 때 파일을 다시 쓸 수 있어서, 패키지 폴더와 그 안 파일의 파일 시스템 시각을 처음 설치한 때나 마지막으로 쓴 때로 단정하지 않습니다. 앱 폴더의 시각은 방향만 잡는 데 쓰고, 실제 사용 시각은 네트워크 기록이나 계정 쪽 기록과 맞춥니다. Windows 기록을 한 줄로 세우는 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html)과 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

Windows 에는 이름이 비슷한 AI 앱이 여럿 있습니다. Windows 에 들어 있는 Copilot 은 다른 회사 제품이라 [Microsoft Copilot](../copilot/index.md)에서 따로 다루고, 브라우저에서 쓴 ChatGPT 는 [웹 브라우저](web.md)에서 다룹니다. 앱이 공식 스토어 앱이 아니라 제3자가 만든 비공식 클라이언트일 수도 있으니, 설치 경로와 게시자를 먼저 확인합니다.

앱 내부 파일 구조는 공개된 분석 자료가 없습니다. 실물 기기에서 파일을 찾았다면 확인한 OS·앱 버전·날짜를 함께 적어 두고, 다른 버전에도 같다고 넘겨짚지 않습니다.

## 직접 분석해 보기

앱 내부 형식을 밝힌 자료가 없어서 헥스 예시는 싣지 않았습니다. 파일 하나를 헥스로 열었을 때 읽을 수 있는 글자가 이어지면 평문이고, 바이트가 고르게 흩어져 있으면 암호화했거나 압축한 것이라는 정도는 가를 수 있습니다. 공개 도구는 파일 형식을 확인한 다음에 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html)나 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html) 페이지에서 고릅니다. 기기에서 모을 항목의 전체 목록은 [기기에서 AI 흔적 모으기](../../../03-techniques/acquisition/endpoint-triage.md)에 있습니다.

## 교차 검증

앱 폴더와 함께 [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)으로 같은 시간대의 접속을 보고, 회사 계정이면 [ChatGPT 기업용 감사 기록](../../network-enterprise/chatgpt-enterprise.md)을 확인합니다. 대화 내용은 [계정 데이터 내보내기](export.md)로 확보한 사본과 맞춥니다.

## 실습

ChatGPT Windows 앱을 담은 공개 검체가 없으니 직접 만들어 봅니다. 가상 머신에 앱을 깔고 시험용 계정으로 가짜 대화를 만든 뒤 다음을 풀어 봅니다.

1. `%LOCALAPPDATA%\Packages` 아래에 어떤 이름의 폴더가 새로 생기는지 적습니다.
2. 대화를 만들기 전과 후에 바뀐 파일을 비교해, 대화 내용이 로컬에 남는지 확인합니다.
3. 로그아웃하거나 앱을 지운 뒤 무엇이 남는지 봅니다.

## 참고 문헌

- Microsoft Store, ChatGPT Classic (9NT1R1C2HH7J) — https://apps.microsoft.com/detail/9nt1r1c2hh7j
