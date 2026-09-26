---
title: "브라우저를 조작하는 AI"
parent: "아티팩트 · 에이전트형 서비스"
nav_order: 420
---

# 브라우저를 조작하는 AI (Browser Agents)

브라우저를 조작하는 AI 는 웹 페이지를 읽고 누르고 입력하는 일을 사람 대신 하고, 사용자 PC 의 실제 브라우저를 움직이는 경우 에이전트의 방문과 사람의 방문이 같은 브라우저 프로필에 섞여 남습니다.

## 무엇을 기록하나 · 왜 생기나

브라우저 에이전트는 브라우저가 어디서 도는지에 따라 흔적이 남는 곳이 달라집니다. 서비스 회사 쪽에서 도는 브라우저라면 방문 흔적은 사용자 PC 에 남지 않고, 사용자 PC 의 브라우저를 움직이면 그 브라우저 프로필에 남습니다. 서비스마다 구조가 다르므로, 검체의 브라우저 프로필에 에이전트가 연 사이트가 남았는지를 먼저 확인합니다. ChatGPT 에이전트는 [ChatGPT 에이전트 모드](chatgpt-agent.md)에서 다룹니다.

이 쪽은 사용자 PC 에 설치된 실제 브라우저를 움직이는 방식을 다룹니다. Claude in Chrome 확장, Claude Code 의 Chrome 연결, ChatGPT Atlas 의 에이전트 모드가 여기에 들어갑니다. 에이전트는 사용자의 로그인 상태를 그대로 쓰므로[2], 에이전트가 연 탭과 사람이 연 탭이 같은 프로필 안에서 움직입니다. Comet·Fellou·Genspark 처럼 에이전트를 브라우저 자체에 넣은 제품과 Edge Copilot 은 [AI 에이전트 브라우저](ai-browsers.md)에서 다룹니다.

조사할 흔적은 네 묶음입니다. 브라우저 프로필 안의 방문 기록·탭, 브라우저 확장과 PC 프로그램을 잇는 연결 설정(네이티브 메시징 (Native Messaging) 호스트), 에이전트가 저장한 스크린샷·GIF 같은 파일, 서비스 계정 서버의 대화 기록입니다.

## 위치와 버전별 차이

### Claude in Chrome 확장

Claude 도움말[1]에 따르면 Claude in Chrome 은 Pro, Max, Team, Enterprise 요금제에서 쓸 수 있고, 지원 브라우저는 Google Chrome 뿐이며 다른 Chromium 브라우저와 모바일은 지원하지 않습니다. 반면 Claude Code 연동 문서[2]는 Chrome 과 Edge 에서 쓸 수 있고 Brave·Arc·Vivaldi·Opera 에서도 연결을 잡는다고 적습니다. 두 문서의 범위가 다르므로, Edge 나 Brave 프로필에서 흔적이 나오면 Claude Code 연동 쪽을 먼저 봅니다.

Chrome 웹 스토어의 확장 ID 는 `fcoeoabgfenejglbffodgkkbkcdhcgfn` 이고, Claude Code 와 연결하려면 확장 1.0.36 이상이 필요합니다[2]. 확장은 브라우저 옆 패널, Claude Cowork 세션, Claude Code, Claude 데스크톱 채팅에서 움직입니다. 기능은 웹 페이지 글 읽기, 탭 그룹으로 여러 탭 관리, 작업 흐름 녹화(옆 패널이 Cowork 세션으로 돌 때는 쓸 수 없음), 콘솔 로그 읽기, 예약·반복 작업, 1Password 로그인 연동입니다[1].

대화 원본은 서버 쪽에 있습니다. Max·Team 요금제와 관리자가 켠 Enterprise 요금제(Pro 는 차례로 적용)에서는 옆 패널이 Cowork 세션으로 돌고, 옆 패널 세션이 모두 기록(history)에 나타나며, 옆 패널에서 시작한 세션을 웹·데스크톱 앱·모바일 앱에서 이어 쓸 수 있습니다[1]. 계정 쪽 기록은 [Claude](../chat-services/claude/index.md)와 [Claude 기업용 감사 로그](../network-enterprise/claude-enterprise.md)에서 다룹니다.

크롬 계열 브라우저에서 확장의 저장소는 프로필 안 `Local Extension Settings\<확장 ID>` 와 `IndexedDB\chrome-extension_<확장 ID>_0.indexeddb.leveldb` 에 있고, 공개 도구 AABF 도 BrowserOS 의 에이전트 확장은 두 경로 모두에서, Sigma 의 에이전트 확장은 `Local Extension Settings` 경로에서 찾습니다[5]. Claude in Chrome 확장이 여기에 무엇을 남기는지는 공개된 분석 자료가 없어, 위 경로에 확장 ID `fcoeoabgfenejglbffodgkkbkcdhcgfn` 폴더가 있는지부터 검체로 확인해야 합니다.

동작 방식과 관리 설정도 조사에 쓸모가 있습니다. "Automatically approve" 모드는 계속 작업하면서 동작마다 안전 검사를 하고 승인이 필요할 때 멈춥니다[1]. Enterprise 관리자는 허용 목록과 차단 목록으로 접근할 수 있는 사이트를 제한할 수 있습니다[1]. Claude Code 연동에서 사이트별 권한은 Chrome 확장 설정에서 관리합니다[2].

### Claude Code 의 Chrome 연결

Claude Code 는 작업용 탭을 새로 열고 사용자의 로그인 상태를 함께 씁니다[2]. 브라우저 동작은 사용자 눈에 보이는 Chrome 창에서 실시간으로 일어나고, 로그인 화면이나 CAPTCHA 를 만나면 멈추고 사람에게 넘깁니다. 확장은 Claude 가 연 탭을 세션에 묶인 Chrome 탭 그룹으로 모으고, `/clear` 를 하면 그 그룹을 닫습니다(`/clear` 뒤에도 이어지는 작업이 돌고 있으면 닫지 않습니다). `/resume` 이나 종료 때는 그룹에 빈 새 탭만 있을 때만 닫아서, 세션이 끝난 뒤에도 에이전트가 연 탭이 남아 있을 수 있습니다. 이 탭들의 방문이 사용자 프로필의 방문 기록에 어떻게 남는지는 공개된 자료가 없으므로, 세션 시간대의 방문 기록을 검체에서 확인합니다.

처음 켤 때 Claude Code 는 네이티브 메시징 호스트 설정 파일을 설치하고, 호스트 이름은 `com.anthropic.claude_code_browser_extension` 입니다[2]. 설치 위치는 브라우저와 OS 마다 다릅니다.

| 브라우저 | OS | 위치 |
|---|---|---|
| Chrome | macOS | `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json` |
| Chrome | Linux | `~/.config/google-chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json` |
| Chrome | Windows | 레지스트리 `HKCU\Software\Google\Chrome\NativeMessagingHosts\` |
| Edge | macOS | `~/Library/Application Support/Microsoft Edge/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json` |
| Edge | Linux | `~/.config/microsoft-edge/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json` |
| Edge | Windows | 레지스트리 `HKCU\Software\Microsoft\Edge\NativeMessagingHosts\` |
| Brave | macOS | `~/Library/Application Support/BraveSoftware/Brave-Browser/NativeMessagingHosts/` |
| Brave | Windows | 레지스트리 `HKCU\Software\BraveSoftware\Brave-Browser\NativeMessagingHosts\` |

다른 Chromium 계열 브라우저도 브라우저 이름을 딴 자기 설정 폴더에서 같은 파일을 읽고, Windows 에서는 브라우저마다 레지스트리 키가 따로 있습니다[2]. 위 표의 Brave 행이 그 예입니다.

확장과의 중계 연결은 `bridge.claudeusercontent.com` 을 거칩니다[2]. 조직의 IP 허용 목록이 이 호스트를 막으면 "Browser extension is not connected" 오류가 나서, 프록시·DNS 기록에서 이 이름을 찾으면 연결을 시도한 흔적을 잡을 수 있습니다. Windows 에서는 named pipe 로 연결하고, 이름이 겹치면 EADDRINUSE 오류가 납니다. MCP 서버 이름은 `claude-in-chrome` 이고, 조직은 관리 설정 `deniedMcpServers` 로 이 서버를 막을 수 있습니다. 관리 설정과 MCP 기록 읽는 법은 [Claude Code](../dev-agents/claude-code/index.md)와 [MCP 서버와 도구 호출 기록](../dev-agents/mcp.md)에 있습니다.

에이전트가 파일로 남기는 것도 있습니다[2]. GIF 녹화는 브라우저 동작을 GIF 파일로 저장하는데, 로그인된 화면의 계정 정보까지 그대로 담깁니다. 스크린샷은 `save_to_disk` 옵션을 켜면 파일로 저장하고 Claude 가 저장한 파일 경로를 알려 주며, v2.1.211 전에는 이 옵션을 켜도 파일이 써지지 않았습니다. 파일 업로드 기능은 v2.1.211 이상에서 로컬 파일을 읽어 웹 페이지의 업로드 칸에 넣고, 한 번에 10MB 까지만 올리며 하드 링크가 여러 개인 파일은 거부하고 `Read` 거부 규칙이 걸린 파일은 올리지 않습니다.

연결이 되는 조건도 버전에 따라 다릅니다[2]. `/login` 으로 로그인해야 하고, v2.1.216 부터는 API 키나 `claude setup-token` 토큰으로 인증한 세션에서 Chrome 연결을 끄고, 그 전에는 이런 세션에서 연결을 켤 수는 있었지만 확장에 붙을 때마다 403 오류로 실패했습니다. Bedrock·Google Cloud·Microsoft Foundry 같은 제3자 제공처를 쓰는 세션과 WSL 에서는 쓸 수 없습니다.

### Claude 데스크톱 앱(Windows 스토어 앱)

Claude 데스크톱 스토어 앱 폴더에는 브라우저 연결과 이어지는 파일이 세 가지 있습니다.

```
%LOCALAPPDATA%\Packages\<Claude 패키지>\LocalCache\Roaming\Claude\ChromeNativeHost\chrome-native-host.exe
%LOCALAPPDATA%\Packages\<Claude 패키지>\LocalCache\Roaming\Claude\claude_desktop_config.json
%LOCALAPPDATA%\Packages\<Claude 패키지>\LocalCache\Local\claude-cli-nodejs\Cache\<이름>\mcp-logs-computer-use\<파일>.jsonl
```

`chrome-native-host.exe` 는 이름에 네이티브 호스트가 들어간 실행 파일입니다. 이 파일이 실제로 브라우저에 등록됐는지는 아래 "설정 파일을 찾는 곳" 의 레지스트리 키와 매니페스트의 `path` 값이 이 파일을 가리키는지로 확인합니다. `claude_desktop_config.json` 에는 `preferences.coworkBrowserToolsEnabled`(참·거짓)와 `preferences.coworkPreferredBrowser`(문자열) 키가 있고, 키 이름대로라면 Cowork 에서 브라우저 도구를 켰는지와 어느 브라우저를 골랐는지를 담는 설정입니다. 아래는 모양만 보여 주는 만든 예시입니다.

```json
{
  "preferences": {
    "coworkBrowserToolsEnabled": true,
    "coworkPreferredBrowser": "sample-browser"
  }
}
```

같은 캐시 폴더 아래 다른 MCP 로그 `.jsonl` 에는 `cwd`, `debug`, `sessionId`, `timestamp` 키가 있습니다. `mcp-logs-computer-use` 폴더는 이름에 화면 조작(computer use)이 들어 있고, 여기에 브라우저 동작이 적히는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 스토어 앱 폴더의 나머지 구조는 [Claude](../chat-services/claude/index.md)와 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)(Windows 판)에 있습니다.

### ChatGPT Atlas

ChatGPT Atlas 는 2025-10-21 에 macOS 용으로 먼저 나온 Chromium 기반 브라우저이고, ChatGPT 를 옆 패널 비서로 붙였습니다[3]. 발표 때 Windows·iOS·Android 판이 "곧" 나온다고 했지만, 이 판들이 나왔다는 기록은 없습니다[3]. Plus·Pro 유료 사용자는 선택 기능인 에이전트 모드 (agent mode) 로 ChatGPT 가 웹 사이트를 직접 조작하게 할 수 있습니다.

"browser memories" 도 선택 기능이고, 메모리는 서버에 30일 보관한 뒤 지우며, 웹 내용은 서버에서 요약한 뒤 원문을 바로 지우고 걸러 낸 요약도 7일 안에 지웁니다[3]. OpenAI 는 2026-03 에 Atlas·ChatGPT 데스크톱 앱·Codex 를 한 앱으로 합치겠다고 밝혔고, Atlas 브라우저는 2026-08-09 에 종료됐습니다[3]. 이 날짜들은 위키백과가 출처라서 보고서에 쓸 때는 출처와 열람 날짜를 붙이고 OpenAI 공지로 다시 확인합니다.

Atlas 의 로컬 프로필 경로와 파일 형식은 공개된 분석 자료가 없어 검체로 확인해야 합니다. 검체에서 Atlas 프로필 폴더를 찾으면 `History`, `Local Storage`, `IndexedDB` 같은 크롬 계열 프로필 파일이 있는지부터 보고, 있으면 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html)(Windows 판)의 방법으로 읽습니다.

### 그 밖의 브라우저 에이전트

Perplexity Comet, Fellou, BrowserOS, Sigma, Genspark 같은 AI 에이전트 브라우저와 Edge Copilot 은 [AI 에이전트 브라우저](ai-browsers.md)에서 경로와 토큰 위치를 다룹니다. 브라우저에 기본으로 들어간 AI 기능은 [브라우저에 들어간 AI](../office-integrations/browser-builtin-ai.md), Perplexity 서비스는 [Perplexity](../chat-services/perplexity.md)에서 다룹니다.

## 구조

### 네이티브 메시징 호스트 설정 파일

브라우저 확장은 네이티브 메시징으로 PC 의 프로그램과 이야기하고, 브라우저는 호스트 설정 파일(매니페스트)을 보고 어떤 프로그램을 띄울지 정합니다. 매니페스트는 JSON 이고 필드는 다섯 개입니다[4].

| 필드 | 뜻 |
|---|---|
| `name` | 호스트 이름 |
| `description` | 설명 |
| `path` | 띄울 프로그램 경로 |
| `type` | 통신 방식. `"stdio"` |
| `allowed_origins` | 이 호스트를 부를 수 있는 확장. 확장 ID 로 적고 와일드카드는 쓸 수 없음 |

아래는 필드 모양만 보여 주려고 가짜 이름·경로·확장 ID 로 만든 예시입니다.

```json
{
  "name": "com.example.sample_host",
  "description": "Sample native host",
  "path": "C:\\Users\\sample-user\\AppData\\Local\\SampleAgent\\sample-host.exe",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://abcdefghijklmnopabcdefghijklmnop/"
  ]
}
```

조사에서는 `path` 로 실제 실행 파일을 찾고, `allowed_origins` 의 확장 ID 를 설치된 확장 목록과 맞춰 봅니다.

### 설정 파일을 찾는 곳

Windows 에서는 설치 프로그램이 `HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\NativeMessagingHosts` 나 `HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\NativeMessagingHosts` 아래에 호스트 이름으로 하위 키를 만들고, 그 키의 기본값에 매니페스트 파일 경로를 적습니다[4]. Chrome 은 32비트 레지스트리를 먼저 봅니다.

| OS | 범위 | Chrome | Chromium |
|---|---|---|---|
| macOS | 시스템 전체 | `/Library/Google/Chrome/NativeMessagingHosts/` | `/Library/Application Support/Chromium/NativeMessagingHosts/` |
| macOS | 사용자별 | `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/` | `~/Library/Application Support/Chromium/NativeMessagingHosts/` |
| Linux | 시스템 전체 | `/etc/opt/chrome/native-messaging-hosts/` | `/etc/chromium/native-messaging-hosts/` |
| Linux | 사용자별 | `~/.config/google-chrome/NativeMessagingHosts/` | `~/.config/chromium/NativeMessagingHosts/` |

### 확장과 호스트 프로세스

네이티브 메시징을 쓰는 확장은 자기 manifest 에 `"nativeMessaging"` 권한을 선언해야 합니다[4]. 그래서 프로필에 설치된 확장의 manifest 를 훑어 이 권한이 있는 확장을 모으면 브라우저 에이전트 후보를 가려낼 수 있습니다.

브라우저가 호스트 프로세스를 띄울 때는 부른 쪽 origin(`chrome-extension://` 뒤에 확장 ID)을 인자로 넘기고, Windows 에서는 부모 창 핸들도 넘깁니다[4]. 그래서 명령줄까지 남기는 프로세스 생성 기록이 있으면 그 안에서 확장 ID 를 찾아봅니다. 확장과 호스트는 32비트 길이를 앞에 붙인 JSON 메시지를 표준 입출력으로 주고받고, 호스트가 브라우저로 보내는 메시지 하나는 최대 1MB, 브라우저가 호스트로 보내는 메시지는 최대 64MiB 입니다. 메시지는 표준 입출력으로만 오가므로, 디스크에 남는지는 호스트 프로그램이 따로 로그를 쓰는지에 달려 있고 검체로 확인합니다.

## 증거로서 의미

**증명하는 것.** 네이티브 메시징 설정 파일이나 레지스트리 키가 있으면 그 사용자 환경에서 브라우저 연결 기능을 한 번 이상 켰다는 뜻입니다. Claude Code 는 처음 켤 때 설정 파일을 설치하기 때문입니다[2]. 확장 ID 가 프로필에 있으면 그 확장을 설치한 적이 있다는 뜻이고, 데스크톱 앱의 `coworkBrowserToolsEnabled`·`coworkPreferredBrowser` 키는 Cowork 브라우저 도구 설정이 있었음을 보여 줍니다. `bridge.claudeusercontent.com` 접속 기록은 그 시간대에 확장 중계 연결이 오간 흔적입니다. GIF·스크린샷 파일은 에이전트가 그 화면을 보았다는 기록이고, 로그인한 계정 정보가 찍혀 있을 수 있습니다.

**증명하지 못하는 것.** 설정 파일이 있다고 해서 특정 날짜에 에이전트가 브라우저를 조작했다고 말할 수는 없습니다. Claude 쪽에는 방문 기록에 에이전트 표시를 따로 남긴다는 공개 자료가 없어서[1][2], 방문 기록의 한 줄이 사람의 클릭인지 에이전트의 동작인지는 기록만으로 가리기 어렵습니다. 반대로 Fellou 는 로컬 데이터베이스 방문 기록에 AI 방문인지 사람 방문인지가 적힌다는 설명이 있으므로[5], 브라우저마다 다르다는 점을 [AI 에이전트 브라우저](ai-browsers.md)에서 확인합니다. 어떤 지시로 무엇을 했는지는 계정 서버의 대화 기록이나 Claude Code 세션 기록에서 확인해야 합니다.

보고서에는 "이 시간대에 이 브라우저 프로필에 이 사이트 방문 기록이 있고, 같은 시간대에 브라우저 연결 기능의 흔적이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

네이티브 메시징 설정 파일은 기능을 처음 켤 때 만들어지므로[2], 파일 생성 시각은 처음 켠 시각의 후보입니다. 다시 쓰는 조건은 공개된 자료가 없어서 수정 시각을 처음 켠 시각으로 읽지 않습니다. Windows 에서는 호스트 이름 하위 키의 마지막 기록 시각을 함께 봅니다.

브라우저 방문 기록의 시각 형식과 기준 시각은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html)(Windows 판)에 있습니다. GIF·스크린샷 파일은 파일 시스템 시각으로 저장 시점을 잡습니다. MCP 로그에는 `timestamp` 키가 있고, 형식과 기준 시각은 검체의 값을 파일 시스템 시각과 맞춰 확인합니다. 여러 기록을 한 줄로 합치는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

사람과 에이전트의 방문이 한 프로필에 섞여 남아서 방문 기록만으로는 둘을 가르기 어렵습니다. 둘을 가를 단서는 에이전트가 연 탭 그룹, 네이티브 메시징 설정 파일과 실행 파일, `bridge.claudeusercontent.com` 연결, GIF·스크린샷 파일이고, 이 단서들이 겹치는 시간대를 좁혀 가며 판단합니다. `/clear` 를 하면 탭 그룹이 닫히므로[2], 수집 시점에 탭 그룹이 없어도 에이전트를 쓰지 않았다고 볼 수는 없습니다.

버전 차이도 결론을 바꿉니다. v2.1.211 전에는 `save_to_disk` 를 켜도 스크린샷 파일이 써지지 않았으므로[2], 그 전 버전 환경에서는 스크린샷 파일이 없어도 이상하지 않습니다. v2.1.216 부터는 API 키 인증 세션에서 Chrome 연결을 끄므로, 인증 방식과 버전을 함께 확인합니다.

문서마다 지원 범위가 다릅니다. Claude 도움말[1]은 Chrome 만 지원한다고 적고 Claude Code 문서[2]는 Edge·Brave 등도 연결된다고 적어서, 한 문서만 보고 "이 브라우저에서는 쓸 수 없다" 고 단정하지 않습니다. Atlas 의 출시·종료 날짜는 위키백과[3]가 출처라서 보고서에 쓸 때는 출처와 열람 날짜를 붙입니다.

사용자가 시키지 않은 동작이 기록에 보이면 에이전트가 읽은 웹 페이지 속 지시도 원인 후보에 넣습니다. 2025-10 에 LayerX Security 가 교차 사이트 요청 위조(CSRF)로 ChatGPT 메모리에 숨은 지시를 몰래 넣는 문제("ChatGPT Tainted Memories")를 공개했으므로[3], 사고 조사에서는 계정에 남은 메모리 내용도 살펴볼 대상에 넣습니다. 분석 방법은 [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md)에 있습니다.

GIF·스크린샷 파일과 브라우저 쿠키에는 로그인한 계정 정보가 담길 수 있어서, 보고서에 옮길 때는 계정 식별 값과 인증 값을 가립니다. 남는 곳과 다루는 원칙은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다.

## 직접 분석해 보기

**헥스로.** 매니페스트는 평문 JSON 이라 헥스로 열면 첫 바이트부터 글자가 그대로 보입니다. 아래는 위의 만든 예시 파일 첫 16바이트를 옮긴 만든 예시이고, 줄바꿈이 LF 라고 가정했습니다(CRLF 면 `0A` 앞에 `0D` 가 붙습니다).

```
00000000  7B 0A 20 20 22 6E 61 6D 65 22 3A 20 22 63 6F 6D   {.  "name": "com
```

`7B` 는 `{`, `22 6E 61 6D 65 22` 는 `"name"` 이고, 이어지는 값이 호스트 이름입니다. 파일 이름과 `name` 값, 레지스트리 하위 키 이름이 서로 맞는지 확인합니다.

**공개 도구로.** 살아 있는 Windows 에서는 `reg query "HKCU\Software\Google\Chrome\NativeMessagingHosts" /s` 로 등록된 호스트를 모두 보고, Edge·Brave 키도 같은 방법으로 봅니다. 떠 온 이미지에서는 사용자 `NTUSER.DAT` 를 공개 레지스트리 도구(예: Registry Explorer, RegRipper)로 열어 같은 경로를 봅니다. macOS·Linux 에서는 위 표의 `NativeMessagingHosts` 폴더 목록을 뽑습니다. 그다음 매니페스트의 `allowed_origins` 확장 ID 를 브라우저 프로필의 확장 목록과 맞추고, 확장 manifest 에 `"nativeMessaging"` 권한이 있는지 봅니다. 프로필 구조는 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html)(Windows 판)에 있습니다.

AI 에이전트 브라우저가 함께 깔린 검체라면 AABF[5]로 어떤 에이전트 브라우저가 있는지 먼저 가려냅니다. AABF 는 1.1.260618 판(2026-06 빌드) 기준으로 Comet·Fellou·Edge·BrowserOS·Sigma·Genspark 여섯 개를 찾는 도구이고 Windows 10/11 에서 돌리며, Claude in Chrome 과 Atlas 는 대상에 없습니다. 지금 판의 브라우저와 경로가 다를 수 있으니 도구 결과는 검체의 폴더와 맞춰 봅니다. AABF 에는 남은 토큰으로 서버 API 를 부르는 기능도 있는데, 서버 쪽 자료는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) 같은 법적 절차로 받습니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 브라우저 방문 기록·탭 | 에이전트가 연 사이트(사람 방문과 섞임) | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html) |
| 프록시·DNS 기록 | `bridge.claudeusercontent.com` 접속 시간대 | [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) |
| Claude Code 세션 기록 | 브라우저 도구를 부른 지시와 결과 | [Claude Code](../dev-agents/claude-code/index.md) |
| MCP 설정·로그 | `claude-in-chrome` 서버 사용과 차단 설정 | [MCP 서버와 도구 호출 기록](../dev-agents/mcp.md) |
| 계정 서버 기록 | 옆 패널 세션 대화 원본 | [Claude](../chat-services/claude/index.md) |
| 업로드한 파일 | 에이전트가 웹에 올린 로컬 파일 | [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) |
| 에이전트 브라우저 프로필 | Comet·Fellou 등에서 에이전트가 한 작업 | [AI 에이전트 브라우저](ai-browsers.md) |

`save_to_disk` 로 스크린샷을 저장하면 Claude 가 그 파일 경로를 알려 주므로[2], Claude Code 세션 기록에 그 경로가 남아 있으면 실제 파일과 맞춥니다. 에이전트가 무엇을 했는지 전체 흐름을 짜는 절차는 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md)에 있습니다.

## 실습

NIST CFReDS 같은 공개 검체 모음에서 브라우저 에이전트 흔적을 담은 검체를 먼저 찾아보고, 없으면 조사용 계정과 가상 머신으로 시험 환경을 만들어 아래 질문을 풀어 봅니다.

1. 브라우저 연결 기능을 처음 켜기 전과 뒤에 레지스트리(또는 `NativeMessagingHosts` 폴더)를 비교해, 새로 생긴 키·파일과 그 시각을 적습니다.
2. 에이전트에게 공개 사이트 두 곳을 열게 하고 사람이 한 곳을 직접 연 뒤, 방문 기록만으로 셋을 구분할 수 있는지, 어떤 다른 기록이 있어야 구분되는지 정리합니다.
3. `/clear` 를 한 뒤와 세션을 그냥 끝낸 뒤 탭 그룹과 탭이 어떻게 남는지 비교합니다.
4. 스크린샷을 파일로 저장하게 한 뒤 저장된 파일의 시각과 세션 기록의 시각을 맞춰 봅니다.
5. Claude in Chrome 확장을 쓰기 전과 뒤에 프로필의 `Local Extension Settings` 와 `IndexedDB` 아래 확장 ID 폴더가 생기는지 비교합니다.

## 참고 문헌

1. Getting started with Claude in Chrome (Claude 도움말) — https://support.claude.com/en/articles/12012173-getting-started-with-claude-in-chrome (2026-09-25 열람)
2. Use Claude Code with Chrome — https://code.claude.com/docs/en/chrome (2026-09-25 열람)
3. ChatGPT Atlas (Wikipedia) — https://en.wikipedia.org/wiki/ChatGPT_Atlas (2026-09-25 열람)
4. Native messaging (Chrome for Developers) — https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging (2026-09-25 열람)
5. AABF (AI Agent Browser Forensics), 1.1.260618 — https://github.com/seturi/AI-Agent-Browser-Forensics , `aabf/signatures.py`, `aabf/identification/identify.py`, `README.md`, `pyproject.toml` (2026-09-25 열람)
