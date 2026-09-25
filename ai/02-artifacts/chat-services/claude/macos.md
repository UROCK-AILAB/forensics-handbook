---
title: "Claude macOS 앱"
parent: "Claude"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 170
---

# macOS 앱 (macOS)

macOS 의 Claude 데스크톱 앱은 다운로드 페이지에서 받아 응용 프로그램 폴더에서 실행하는 앱이고, 문서로 확인한 기기 흔적은 사용자 라이브러리 아래의 MCP 설정 파일과 로그, 그리고 MDM 으로 내려받는 관리 설정입니다. 대화 원본은 계정 서버에 있습니다.

> 확인 날짜: 2026-09. 공식 도움말과 MCP 문서, App Store 페이지(2026-09-25 열람)만 근거로 썼습니다. macOS 기기는 직접 관찰하지 않았고, 앱 버전별 차이도 확인하지 못했습니다.

## 무엇이 남나 · 왜 생기나

데스크톱 앱은 claude.ai 와 같은 계정으로 로그인해 쓰는 앱이라서, 대화는 서버에 저장됩니다. 로컬 앱 폴더에 대화 본문이 남는지는 문서로 확인하지 못했습니다. 앱은 macOS 11(Big Sur) 이상에서 돌고, 다운로드 페이지에서 받은 파일을 열어 설치한 뒤 응용 프로그램(Applications) 폴더에서 실행하며, 업데이트는 앱 안에서 합니다[1]. 받는 파일의 형식은 도움말에 적혀 있지 않았습니다. 로컬 MCP 서버를 연결하면 사용자 라이브러리 아래에 그 설정과 연결 로그가 남습니다[2].

Windows 앱에서는 앱 폴더 안에 크롬 계열 저장소와 앱 JSON 파일이 있는 것을 관찰했지만([Windows 앱](windows.md)), macOS 의 `~/Library/Application Support/Claude/` 아래에도 같은 폴더가 있는지는 확인하지 못했습니다. Windows 쪽 파일 이름을 macOS 에 그대로 옮겨 찾되, 찾은 것만 보고서에 씁니다.

## 위치

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `/Applications/` 아래의 앱 번들 | 설치한 앱 | 문서[1](번들 이름은 확인하지 못함) |
| `~/Library/Application Support/Claude/claude_desktop_config.json` | 로컬 MCP 서버 설정 | 문서[2] |
| `~/Library/Logs/Claude/mcp.log` | MCP 연결과 실패 기록 | 문서[2] |
| `~/Library/Logs/Claude/mcp-server-<서버 이름>.log` | 그 서버가 표준 오류로 낸 출력 | 문서[2] |
| 환경설정 도메인 `com.anthropic.claudefordesktop` | MDM 으로 내려받는 관리 설정 | 문서[3] |

MCP 설정 파일과 로그의 해석은 [MCP 서버와 도구 호출 기록](../../dev-agents/mcp.md)에서 다룹니다. Windows 판에서는 같은 이름의 `claude_desktop_config.json` 에 앱 환경설정도 함께 들어 있었는데(확인 범위: Windows 11, 2026-09), macOS 파일도 그런지는 확인하지 못했습니다.

## 관리 설정

조직은 Jamf Pro·Kandji·Intune 같은 MDM 의 구성 프로필로 환경설정 도메인 `com.anthropic.claudefordesktop` 에 관리 설정을 내려보내고, 쓸 수 있는 키는 Windows 정책과 같은 목록입니다[3]. 키 목록은 [Windows 앱](windows.md)의 관리 정책 절에 있습니다. 구성 프로필이 기기에 떨어뜨리는 실제 plist 파일 경로는 확인하지 못했고, macOS 용 기업 배포 안내 글은 이번에 열어 보지 않았습니다. 관리 설정 plist 를 찾았다면 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/plist/index.html)의 방법으로 읽습니다.

로그인 정보를 키체인에 넣는지, 넣는다면 항목 이름이 무엇인지는 확인하지 못했습니다. 키체인의 구조와 보호 방식은 [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 응용 프로그램 폴더에 앱이 있고 `~/Library/Application Support/Claude/` 가 있으면 이 macOS 사용자 계정에 앱을 설치하고 실행한 흔적이 있다고 쓸 수 있습니다. MCP 설정과 `~/Library/Logs/Claude` 의 로그가 있으면 로컬 MCP 서버를 연결했거나 연결하려 한 기록이 있다고 쓸 수 있고, 관리 설정이 있으면 기기에 조직 정책이 놓여 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** 기기 파일로 대화 본문을 확인할 수 있는지는 알지 못하고, 앱을 누가 조작했는지도 알 수 없습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 대화 내용이 필요하면 웹이나 데스크톱 앱에서 받는 [계정 데이터 내보내기](export.md)를 씁니다.

## 시각 해석

업데이트는 앱 안에서 이뤄지고[1] 그때 앱 번들의 파일 시스템 시각이 바뀔 수 있어서, 번들 시각을 처음 설치한 때로 보지 않습니다. 처음 받은 때는 설치 파일의 다운로드 흔적에서 찾는 편이 낫고, 받은 파일에 붙는 격리 속성과 다운로드 기록은 [격리 속성과 다운로드 기록](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/filesystem/quarantine/index.html)에서 다룹니다. 폴더가 생기고 지워진 순서는 [파일 시스템 이벤트](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/filesystem/fsevents/index.html)로, 여러 시각을 한 줄로 맞추는 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-mac/03-techniques/analysis/timeline/index.html)과 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)으로 봅니다. MCP 로그 줄의 시각 형식은 확인하지 못해서 값을 보고 판단합니다.

## 함정과 한계

App Store 의 Claude 앱은 iPhone·iPad 호환만 표기돼 있고 Mac 호환 표기는 없었습니다[4]. Mac 에서 발견한 Claude 흔적은 이 페이지의 데스크톱 앱이나 [웹 브라우저](web.md)에서 나온 것인지부터 가립니다. 응용 프로그램 폴더에 앱이 없어도 사용자 라이브러리의 폴더와 로그가 남아 있을 수 있어서, 앱을 지웠다면 라이브러리 쪽을 따로 봅니다. 터미널에서 쓰는 Claude Code 는 기록을 다른 곳에 남기고 [Claude Code](../../dev-agents/claude-code/index.md)에서 다룹니다.

## 직접 분석해 보기

macOS 기기를 관찰하지 않아서 헥스 예시는 싣지 않습니다. 공개 도구로는 다음 순서로 봅니다.

1. 사용자 라이브러리의 `Application Support/Claude` 와 `Logs/Claude` 를 사본으로 뜹니다.
2. `claude_desktop_config.json` 을 jq 같은 JSON 도구로 열어 최상위 키를 뽑고, MCP 서버 설정이 있는지 봅니다.
3. 로그 파일 이름에 나온 서버 이름과 설정 파일의 서버 이름을 맞춰 봅니다.
4. 관리 설정을 찾았다면 `plutil -p` 로 plist 를 읽어 키를 확인합니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [격리 속성과 다운로드 기록](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/filesystem/quarantine/index.html) | 설치 파일을 받은 때와 받은 곳 |
| [통합 로그 형식](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/unified-log/index.html) | 앱 실행과 관련된 시스템 기록 |
| [MCP 서버와 도구 호출 기록](../../dev-agents/mcp.md) | 연결한 로컬 도구 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 앱이 접속한 시각 |
| [계정 데이터 내보내기](export.md) | 대화 본문과 시각 |

## 실습

직접 만든 시험용 macOS 가상 머신이나 공개 검체(NIST CFReDS 등)의 Mac 이미지로 다음을 풀어 봅니다.

1. `~/Library/Application Support/Claude/` 아래에 어떤 폴더와 파일이 있고, Windows 앱에서 관찰한 이름과 무엇이 같고 다른가?
2. 설치 파일의 격리 속성에 남은 다운로드 시각과 앱 폴더가 처음 생긴 시각은 얼마나 떨어져 있는가?
3. `~/Library/Logs/Claude` 에 `mcp-server-` 로 시작하는 로그가 있다면, 그 서버가 설정 파일에도 남아 있는가?

## 참고 문헌

1. Install Claude Desktop (Claude Help Center) — https://support.claude.com/en/articles/10065433-installing-claude-desktop
2. Connect to local MCP servers (Model Context Protocol 문서) — https://modelcontextprotocol.io/docs/develop/connect-local-servers
3. Enterprise configuration for Claude Desktop (Claude Help Center) — https://support.claude.com/en/articles/12622667-enterprise-configuration-for-claude-desktop
4. Claude by Anthropic — App Store — https://apps.apple.com/us/app/claude-by-anthropic/id6473753684
