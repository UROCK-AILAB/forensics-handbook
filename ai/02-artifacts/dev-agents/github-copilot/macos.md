---
title: "GitHub Copilot macOS"
parent: "GitHub Copilot"
grand_parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 590
---

# macOS (macOS)

macOS 의 VS Code 에서 GitHub Copilot 설정과 채팅 기록은 `~/Library/Application Support/Code/User` 아래에 모이고, Xcode 용 Copilot 은 따로 `~/Library/Logs/GitHubCopilot/` 에 로그를 남깁니다.

> 확인 날짜: 2026-09. VS Code·GitHub 공식 문서(2026-09-25 열람)와 VS Code 오픈소스 코드(`chatSessionStore.ts`, 그 파일의 마지막 커밋 2026-08-06)를 근거로 썼습니다. macOS 기기를 관찰한 기록은 없어서 실물 파일로 확인한 내용은 없고, Copilot 확장·Xcode 용 Copilot 의 버전도 확인하지 않았습니다.

## 무엇이 남나 · 왜 생기나

VS Code 는 채팅 세션을 저장하는 코드가 OS 와 상관없이 같아서, 세션 파일 폴더 이름(`chatSessions`, `emptyWindowChatSessions`, `transferredChatSessions`)과 `.json`·`.jsonl` 형식, 세션 목록 키 `chat.ChatSessionStore.index` 는 macOS 에서도 같습니다. 그 짜임과 해석은 [Windows](windows.md)에서 다루고, 이 페이지는 macOS 에서 달라지는 경로와 Xcode 용 Copilot 을 다룹니다. 출력 창·`idea.log`·원격 측정은 [로그와 원격 측정](logs.md)에 있습니다.

## 위치

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `$HOME/Library/Application Support/Code/User/settings.json` | VS Code 사용자 설정(Copilot·채팅 설정 키 포함) | 문서 |
| `$HOME/Library/Application Support/Code/User/profiles/<profile ID>/settings.json` | 프로필별 설정 | 문서 |
| 작업 폴더 루트의 `.vscode/settings.json` | 작업 폴더 설정 | 문서 |
| `~/Library/Logs/GitHubCopilot/` | Xcode 용 Copilot 로그 폴더 | 문서 |
| `~/Library/Logs/GitHubCopilot/github-copilot-for-xcode.log` | Xcode 용 Copilot 의 최근 로그 파일 | 문서 |

채팅 세션 폴더가 User 폴더 아래 어디에 생기는지는 코드 안에서 경로 변수(workspaceStorageHome, globalStorageHome)로만 확인했습니다. 문서로 확인한 범위는 `Code/User` 폴더까지이고, 그 아래가 `workspaceStorage/...` 같은 이름인지는 확인하지 못했습니다. 수집할 때는 `~/Library/Application Support/Code/User` 를 통째로 떠서 `chatSessions` 라는 이름의 폴더를 찾습니다.

참고로 Linux 의 사용자 설정은 `$HOME/.config/Code/User/settings.json`, 프로필별 설정은 `$HOME/.config/Code/User/profiles/<profile ID>/settings.json` 입니다.

## Xcode 용 Copilot

Xcode 용 Copilot 앱에서 Advanced → Open Copilot Log Folder 를 누르면 위 로그 폴더가 열리고, Advanced → Logging → Verbose Logging 스위치를 켜면 더 자세한 로그를 남깁니다. 사용자가 일부러 켜는 로그를 어떻게 읽을지는 [로그와 원격 측정](logs.md)에서 다룹니다. 로그 줄의 형식과 로그에 프롬프트·응답 본문이 들어가는지는 확인하지 못했습니다.

## JetBrains IDE

macOS 의 JetBrains IDE 에서는 Help → Show Log in Finder 로 `idea.log` 를 엽니다. 실제 경로는 확인하지 못했고, 이 로그에 남는 Copilot 관련 줄은 [로그와 원격 측정](logs.md)에서 다룹니다. JetBrains 플러그인이 채팅 기록을 PC 에 남기는지는 확인하지 못했습니다.

## 로그인 정보 보호

Copilot 로그인 토큰이 키체인에 들어가는지는 확인하지 못했습니다. 키체인의 구조와 수집할 때 조심할 점은 [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html)에, 토큰이 흔히 남는 자리는 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다. 채팅 세션 파일을 따로 암호화한다는 내용은 소스에서 보지 못했지만, 암호화 여부를 확정하지는 못했습니다.

## 증거로서 의미

`Code/User` 아래의 세션 파일과 설정 파일이 증명하는 것과 증명하지 못하는 것은 Windows 와 같아서 [Windows](windows.md)의 해당 절을 봅니다. macOS 에서 더 볼 수 있는 기록은 Xcode 용 Copilot 로그인데, 이 로그 파일이 있으면 그 사용자 계정에서 Xcode 용 Copilot 을 설치해 실행한 적이 있다고 읽을 수 있습니다. 반대로 로그 파일만으로는 어떤 코드를 제안받았는지, 제안을 받아들였는지를 알 수 없습니다.

## 시각 해석

macOS 에서는 파일 시스템 시각에 더해 파일 시스템 이벤트 기록으로 세션 파일이 언제 생기고 바뀌었는지를 맞춰 볼 수 있습니다. 구조는 [파일 시스템 이벤트](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/filesystem/fsevents/index.html)에, 여러 기록을 한 줄로 세우는 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-mac/03-techniques/analysis/timeline/index.html)과 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다. 색인의 `lastMessageDate` 를 읽을 때 조심할 점은 [Windows](windows.md)의 시각 해석 절과 같습니다.

## 함정과 한계

Xcode 용 Copilot 로그 폴더와 VS Code 의 `Code/User` 폴더는 서로 다른 제품의 기록이라서, 한쪽이 비어 있다고 다른 쪽도 없다고 보지 않습니다.

## 실습

Copilot 기록이 들어 있는 공개 macOS 검체는 확인하지 못해서, 직접 만든 시험 계정(가짜 사용자 `analyst01`, 가짜 작업 폴더 `~/work/demo-app`)에서 풀어 봅니다.

1. VS Code 에서 채팅을 한 뒤 `~/Library/Application Support/Code/User` 아래 어느 폴더에 `chatSessions` 가 생기는가?
2. Xcode 용 Copilot 에서 Verbose Logging 을 켜기 전과 뒤에 `github-copilot-for-xcode.log` 의 크기와 줄 모양은 어떻게 달라지는가?
3. 파일 시스템 이벤트 기록에서 세션 파일이 처음 생긴 때와 색인의 `lastMessageDate` 를 나란히 놓으면 어떻게 맞는가?

## 참고 문헌

1. User and workspace settings — Visual Studio Code(2026-09-16 갱신) — https://code.visualstudio.com/docs/configure/settings
2. microsoft/vscode 소스 `chatSessionStore.ts`(main, 마지막 커밋 2026-08-06) — https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/chat/common/model/chatSessionStore.ts
3. Viewing logs for GitHub Copilot in your environment — https://docs.github.com/en/copilot/troubleshooting-github-copilot/viewing-logs-for-github-copilot-in-your-environment
