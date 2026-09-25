---
title: "GitHub Copilot Windows"
parent: "GitHub Copilot"
grand_parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 580
---

# Windows (Windows)

Windows 의 VS Code 에서 GitHub Copilot 채팅은 작업 폴더마다 세션 파일(`.json` 또는 `.jsonl`)로 남고, 세션 목록은 파일이 아니라 VS Code 저장소 서비스의 키 하나에 따로 들어가며, Copilot 관련 설정은 `settings.json` 에 남습니다.

> 확인 날짜: 2026-09. VS Code 공식 문서(2026-09-16 갱신본, 2026-09-25 열람)와 VS Code 오픈소스 코드(`chatSessionStore.ts`, main 브랜치, 그 파일의 마지막 커밋 2026-08-06)를 근거로 썼습니다. 이 PC 에서 Copilot 폴더를 직접 관찰한 기록은 없어서 실물 파일로 확인한 내용은 없습니다. Copilot 확장 버전은 확인하지 않았고, 소스 코드는 바뀔 수 있어서 "2026-08 기준 소스" 라고 밝혀 둡니다.

## 무엇이 남나 · 왜 생기나

VS Code 는 Copilot 채팅 세션을 작업 폴더(워크스페이스) 단위로 묶고, Agents 창에서는 여러 작업 폴더의 세션을 한꺼번에 보여 줍니다. 문서가 구분하는 세션 종류는 로컬 세션, worktree 를 쓰는 Copilot 세션, Claude 세션, Codex 세션, Agent Host 세션, 그리고 Copilot CLI·GitHub Copilot 앱·Claude Code 에서 들어온 외부 세션입니다. 이 가운데 로컬 채팅 세션은 VS Code 사용자 데이터 폴더 안에 파일로 남고, 클라우드 세션과 외부 세션은 목록에 "외부(isExternal)" 로 표시됩니다. 외부 세션의 대화 원본이 PC 에 남는지, 서버에만 있는지는 확인하지 못했습니다.

이 페이지는 Windows 경로와 채팅 파일의 짜임을 다루고, macOS 경로는 [macOS](macos.md)에서, 출력 창·`idea.log`·원격 측정은 [로그와 원격 측정](logs.md)에서 다룹니다.

## 위치

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `%APPDATA%\Code\User\settings.json` | 사용자 설정(Copilot·채팅 설정 키 포함) | 문서 |
| `%APPDATA%\Code\User\profiles\<profile ID>\settings.json` | 프로필별 설정. 그 프로필에서 설정을 바꿨을 때만 생김 | 문서 |
| 작업 폴더 루트의 `.vscode\settings.json` | 작업 폴더 설정. 여러 폴더 작업 영역이면 작업 영역 설정 파일 안에 들어감 | 문서 |
| `<workspaceStorage>\<작업영역 ID>\chatSessions\` | 폴더를 연 창의 채팅 세션 파일 | 소스(2026-08) |
| `<globalStorage>\emptyWindowChatSessions\` | 폴더 없이 연 빈 창의 채팅(기본 프로필) | 소스(2026-08) |
| `<workspaceStorage>\no-workspace\chatSessions\` | 예전 빈 창 채팅 위치. 지금은 읽기만 함 | 소스(2026-08) |
| `<globalStorage>\transferredChatSessions\` | 다른 작업 영역으로 넘긴 세션 | 소스(2026-08) |

표의 `<workspaceStorage>` 와 `<globalStorage>` 는 VS Code 코드 안의 경로 변수(workspaceStorageHome, globalStorageHome)입니다. User 폴더가 `%APPDATA%\Code\User` 라는 것은 문서로 확인했지만, 그 아래 실제 폴더 이름이 `workspaceStorage`·`globalStorage` 인지는 확인하지 못했습니다. 수집할 때는 `%APPDATA%\Code\User` 아래를 통째로 떠서 `chatSessions` 라는 이름의 폴더를 찾는 편이 안전합니다.

JetBrains IDE 의 Copilot 플러그인이 채팅 기록을 PC 에 남기는지, 남긴다면 어디에 두는지는 확인하지 못했습니다. 흔히 `github-copilot` 폴더라고 부르는 로그인·설정 폴더의 위치와 파일 이름도 확인하지 못했고, JetBrains 쪽에서 확인된 흔적은 로그 파일 `idea.log` 뿐이라서 [로그와 원격 측정](logs.md)에서 다룹니다.

## 구조

### 세션 파일

세션 파일 이름은 `<세션 ID>.json` 또는 `<세션 ID>.jsonl` 입니다. 소스 주석에 `<1.109 flat JSON file`, `>=1.109 append log` 라고 적혀 있어서, VS Code 1.109 전에는 세션마다 JSON 한 파일로 쓰고 1.109 부터는 줄을 덧붙이는 JSONL 로그로 씁니다. JSONL 저장은 설정 `chat.useLogSessionStorage` 가 false 가 아니면 쓰고 기본값은 켜짐입니다. 작업 영역을 옮기면 VS Code 가 `.json`·`.jsonl` 파일을 새 저장 폴더로 옮깁니다.

| VS Code 버전 | 세션 파일 형식 | 조건 |
|---|---|---|
| 1.109 전 | 세션마다 JSON 한 파일(`.json`) | — |
| 1.109 부터 | 줄을 덧붙이는 로그(`.jsonl`) | `chat.useLogSessionStorage` 가 false 가 아닐 때(기본 켜짐) |

세션 파일 안의 줄마다 어떤 키가 들어가는지는 이 페이지의 근거 자료에서 확인하지 못했습니다. 소스에서 파일을 따로 암호화하는 부분은 보지 못했지만, 암호화 여부를 확정하지는 못했습니다.

### 세션 목록(색인)

세션 목록은 폴더 안 파일이 아니라 VS Code 저장소 서비스의 키 `chat.ChatSessionStore.index` 에 들어갑니다. 폴더를 연 창이면 작업 영역 범위, 빈 창이면 애플리케이션 범위에 쓰고, 다른 작업 영역으로 넘긴 세션 목록은 프로필 범위의 키 `ChatSessionStore.transferIndex` 에 둡니다. 이 저장소 서비스가 디스크의 어느 파일에 쓰는지(예를 들어 SQLite 파일인지)는 확인하지 못했습니다.

색인은 `version` 과 `entries` 로 이뤄지고, `entries` 는 세션 ID 를 키로 삼아 항목을 담습니다. 한 항목의 칸은 아래와 같습니다.

| 칸 | 뜻 |
|---|---|
| `sessionId` | 세션 ID. 세션 파일 이름과 맞춰 볼 수 있음 |
| `title` | 세션 제목. 없으면 "New Chat" 이 들어감 |
| `lastMessageDate` | 마지막 메시지 시각(숫자) |
| `timing`, `stats`, `lastResponseState` | 시간 정보, 통계, 마지막 응답 상태 |
| `initialLocation` | 세션을 처음 연 자리 |
| `hasPendingEdits` | 적용하지 않은 편집이 남았는지 |
| `workingDirectory` | 작업 폴더 |
| `isEmpty` | 빈 세션인지 |
| `isExternal` | 클라우드·외부 세션인지 |
| `permissionLevel` | 권한 수준 |
| `inputState` | 외부 세션에서 보내지 않은 입력(텍스트, 모드, 고른 모델 등). 첨부는 비움 |

아래는 칸 이름만 소스에서 가져오고 값은 새로 지어낸 예시입니다.

```json
{ "version": 1, "entries": { "demo-session-0001": { "sessionId": "demo-session-0001", "title": "New Chat", "lastMessageDate": 1234567890, "isEmpty": false, "isExternal": false } } }
```

로컬 세션은 색인에 400개까지 두고, 넘치면 `lastMessageDate` 가 오래된 것부터 색인에서 지웁니다. 외부 세션은 이 계산에서 빠집니다. 빈 세션은 지우고, 예전에 옮겨 온 빈 세션은 `isEmpty` 로 걸러 냅니다.

### 설정 키

Copilot 과 채팅 세션 관련 설정은 위 `settings.json` 들에 남습니다. 문서에 나오는 키는 `github.copilot.chat.summarizeAgentConversationHistory.enabled`, `chat.viewSessions.enabled`, `chat.viewSessions.orientation`, `chat.agentSessions.showExternal`, `chat.agentSessions.autoMarkAsDoneMergedSessionsAfterDays`, `chat.agentSessions.autoDeleteArchivedMergedSessionsAfterDays`, `sessions.showApplicationBadge`, `chat.agentsControl.enabled` 입니다. 병합된 세션을 자동으로 정리하려면 자동 정리 설정 두 개를 모두 켜야 하고 기본은 꺼짐이며, 문서가 권하는 값은 15일입니다. 아래는 만든 예시입니다.

```json
{
  "chat.useLogSessionStorage": true,
  "chat.agentSessions.autoMarkAsDoneMergedSessionsAfterDays": 15,
  "chat.agentSessions.autoDeleteArchivedMergedSessionsAfterDays": 15
}
```

## 보관·삭제·내보내기

세션은 보관(archive)과 영구 삭제로 나뉩니다. 문서에 따르면 보관은 세션을 지우지 않지만, worktree 세션이면 커밋하지 않은 변경을 세션 브랜치에 커밋한 뒤 worktree 폴더를 지웁니다. 삭제는 되돌릴 수 없고, 커밋하지 않은 채 worktree 에만 있던 파일은 잃을 수 있다고 적혀 있습니다. 삭제할 때 디스크의 세션 파일까지 지우는지는 확인하지 못했습니다.

`Chat: Export Chat...` 명령을 쓰면 세션의 프롬프트와 응답 전부를 JSON 파일로 내보내고, 그 파일은 사용자가 고른 자리에 생깁니다. 가져오기 방법은 문서에 없습니다. 내보낸 파일의 일반적인 해석은 [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md)을 봅니다.

로그인 토큰을 Windows 자격 증명 관리자에 두는지 같은 저장 방식은 확인하지 못했습니다. 토큰이 흔히 남는 자리는 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에, 자격 증명 관리자의 구조는 [자격 증명 관리자와 볼트](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/credentials/credential-manager-windows-vault.html)에 있습니다.

## 증거로서 의미

세션 파일이 있으면 그 작업 폴더에서 VS Code 채팅 세션이 열렸고 기록이 저장됐다는 뜻이고, 색인의 `workingDirectory`·`title`·`lastMessageDate` 로 어느 폴더에서 언제쯤 대화했는지를 좁힐 수 있습니다. `.jsonl` 파일은 VS Code 1.109 이후 버전이 썼다는 단서가 되고, `transferredChatSessions` 폴더의 파일은 세션을 다른 작업 영역으로 넘긴 흔적입니다. 사용자가 고른 자리에 채팅을 내보낸 JSON 파일이 있으면 내보내기를 했다는 흔적으로 읽을 수 있습니다.

증명하지 못하는 것도 분명합니다. 세션 파일은 어느 Windows 계정 폴더에 기록이 남았는지를 알려 줄 뿐 키보드 앞에 누가 있었는지는 알려 주지 않고, 이 판단은 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)에서 다룹니다. 모델이 제안한 코드를 사용자가 실제로 받아들였는지, 외부·클라우드 세션의 대화 원본이 무엇이었는지도 세션 파일만으로는 확인되지 않습니다.

## 시각 해석

색인의 `lastMessageDate` 는 숫자 값이지만 단위와 기준 시간대는 확인하지 못했습니다. 그래서 파일 시스템 시각과 나란히 놓고 맞는지 본 다음에 보고서에 씁니다. JSONL 파일은 줄을 덧붙일 때마다 수정 시각이 바뀌어서 마지막 대화 무렵과 가깝게 움직일 수 있지만, 작업 영역을 옮길 때 VS Code 가 파일을 새 폴더로 옮기기 때문에 파일 시각이 원래 대화 시각과 다를 수 있습니다. 여러 출처를 한 줄로 세우는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

- 색인은 로컬 세션을 400개까지만 두어서, 색인에 없는 세션이 곧 지워진 세션이라는 뜻은 아닙니다. 색인에서 빠질 때 세션 파일도 함께 지우는지는 확인하지 못했으니, 색인 항목 개수와 `chatSessions` 폴더의 파일 개수를 따로 세어 비교합니다.
- 제목이 "New Chat" 이면 제목이 비어 있던 세션입니다. 제목으로 대화 내용을 짐작하지 않습니다.
- 한 PC 에 `.json` 과 `.jsonl` 이 섞여 있을 수 있습니다. 1.109 전에 쓴 세션이 남아 있거나 `chat.useLogSessionStorage` 를 꺼 둔 경우이고, 어느 쪽인지는 설정 파일로 가립니다.
- 이 페이지의 경로와 칸 이름은 2026-08 소스 기준이라서, 다른 버전의 VS Code 에서는 이름이 다를 수 있습니다.

## 직접 분석해 보기

세션 파일은 평문 JSON·JSONL 이라서 헥스 편집기로 열면 형식부터 가를 수 있습니다. JSON 명세상 파일은 `{`(바이트 `7B`)로 시작하고, JSONL 은 한 줄에 JSON 값 하나를 두고 줄바꿈(바이트 `0A`)으로 나눕니다. 아래는 명세로 만든 예시이고 실제 세션 파일의 바이트가 아닙니다.

```
7B 22 61 22 3A 31 7D 0A 7B 22 61 22 3A 32 7D 0A    {"a":1}.{"a":2}.
```

공개 도구로는 PowerShell 로 세션 폴더를 찾고, jq 같은 JSON 도구로 한 줄씩 읽습니다. 아래 명령은 만든 예시이고, 원본이 아니라 떠 온 사본에서 돌립니다.

```powershell
# 만든 예시: 사본을 E:\case01\AppData\Roaming\Code\User 에 떠 왔다고 가정
Get-ChildItem E:\case01\AppData\Roaming\Code\User -Recurse -Directory -Filter chatSessions
Get-ChildItem E:\case01\AppData\Roaming\Code\User -Recurse -Include *.json,*.jsonl |
  Where-Object { $_.DirectoryName -match 'ChatSessions' } |
  Select-Object FullName, Length, CreationTimeUtc, LastWriteTimeUtc
```

## 교차 검증

- 작업 폴더 설정 `.vscode\settings.json` 과 색인의 `workingDirectory` 를 맞춰 봅니다.
- VS Code 출력 창과 trace 로그의 세션 관련 문장은 [로그와 원격 측정](logs.md)에서 봅니다.
- 네트워크 쪽 흔적은 [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)으로 확인합니다.
- 외부 세션이 Claude Code 에서 왔다면 [Claude Code](../claude-code/index.md)의 기록과 맞춰 봅니다.

## 실습

Copilot 채팅 기록이 들어 있는 공개 검체는 확인하지 못해서, 직접 만든 시험 환경(가짜 사용자 `analyst01`, 가짜 작업 폴더 `C:\work\demo-app`)에서 풀어 봅니다.

1. 작업 폴더를 열고 채팅을 두 번, 빈 창에서 한 번 했을 때 `chatSessions` 와 `emptyWindowChatSessions` 에 파일이 몇 개 생기는가?
2. 세션 하나를 보관하고 다른 하나를 삭제한 뒤 폴더의 파일 개수는 어떻게 달라지는가?
3. `chat.useLogSessionStorage` 를 false 로 바꾸고 새 세션을 열면 파일 확장자가 바뀌는가?
4. `Chat: Export Chat...` 로 내보낸 JSON 과 원래 세션 파일은 무엇이 같고 무엇이 다른가?

## 참고 문헌

1. Manage agent sessions in VS Code(2026-09-16 갱신) — https://code.visualstudio.com/docs/copilot/chat/chat-sessions
2. microsoft/vscode 소스 `chatSessionStore.ts`(main, 마지막 커밋 2026-08-06) — https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/chat/common/model/chatSessionStore.ts
3. User and workspace settings — Visual Studio Code(2026-09-16 갱신) — https://code.visualstudio.com/docs/configure/settings
