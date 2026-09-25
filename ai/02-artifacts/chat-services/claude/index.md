---
title: "Claude"
parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 140
has_children: true
has_toc: false
---

# Claude (Claude)

Claude 는 웹·데스크톱(Windows·macOS·Linux)·Android·iOS 에서 같은 계정으로 쓰는 대화형 AI 서비스이고, 대화 원본은 계정 서버에 있지만 휴대전화 앱의 캐시 데이터베이스와 데스크톱 앱의 세션 폴더에도 대화가 남아서 기기 흔적과 계정 데이터 내보내기를 함께 봅니다.

## 왜 중요한가

Claude 는 웹 주소 claude.ai 와 데스크톱 앱, Android 앱, iOS/iPadOS 앱으로 제공되고[2][3][4][5], 데스크톱 앱은 macOS 11(Big Sur) 이상, Windows 10 이상, Ubuntu 22.04 LTS 이상과 Debian 12 이상(x64·arm64)에서 돌아갑니다[2]. 같은 계정으로 여러 기기에서 쓰는 서비스라서, 한 기기에 흔적이 없어도 다른 기기나 웹에서 쓴 기록이 계정에 남아 있을 수 있습니다. 서버·기기·동기화에 데이터가 나뉘는 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다.

휴대전화 앱은 대화·메시지·프로젝트를 앱 안의 캐시 데이터베이스에 두고, 메시지마다 본문과 보낸 쪽, 만든 시각이 들어 있습니다[12][13]. ALEAPP 분석기는 Android 검체 두 개로, iLEAPP 분석기는 iOS 18.7.8 과 iOS 26.5.2 검체로 시험했고 앱 판은 적혀 있지 않아서, 지금 판에서는 표나 칸이 다를 수 있습니다[12][13]. 이름이 캐시인 만큼 계정의 대화가 모두 들어 있다고 단정하지 말고, 내보내기의 대화 수와 맞춰 봅니다.

데스크톱 앱은 Electron 앱이라서 사용자 데이터 폴더가 운영체제마다 정해진 자리에 생기고[10], 그 안의 `claude-code-sessions/` 에는 Cowork 세션의 제목·소유 계정·모델·보관 여부가, `local-agent-mode-sessions/` 에는 Cowork 에이전트 세션의 제목·시스템 프롬프트·허용 목록·소유 계정이 남습니다[11]. Cowork 에이전트 세션은 세션 폴더 안의 `audit.jsonl` 에 사용자·어시스턴트·시스템 이벤트로 된 전체 대화와 실행 비용을 남깁니다[11]. claude-forensics 문서는 Claude Code 의 `.claude` 폴더와 데스크톱 앱 데이터 폴더를 둘 다 수집해야 전체를 볼 수 있다고 적습니다[11]. 같은 폴더에 MCP 설정 파일이 있고, MCP 로그는 Windows 에서는 이 폴더 아래에, macOS 에서는 `~/Library/Logs/Claude/` 에 따로 있습니다[7]. Windows 앱의 패키지 폴더에는 크롬 계열 저장소와 앱이 직접 쓰는 JSON 설정 파일도 보입니다.

서버에 대화가 얼마나 남는지는 설정과 사정에 따라 다릅니다. 개인정보 안내 문서에 적힌 기간은 아래와 같습니다[1].

| 경우 | 서버 쪽 보관 |
|---|---|
| 사용자가 대화를 지움 | 대화 목록에서 바로 사라지고, 서버 저장소에서는 30일 안에 지움 |
| 모델 개선 사용을 켬 | 비식별 형태로 최대 5년 |
| 모델 개선 사용을 끔 | 이전 대화와 새 대화를 이후 학습에 쓰지 않음 |
| 피드백으로 보낸 대화 | 5년 |
| 자동 안전 분류에 걸림 | 입력·출력은 최대 2년, 안전 분류 점수는 최대 7년 |
| 법적 요구·분쟁 해결·이용 정책 위반 대응 | 필요한 만큼 |

시크릿(Incognito) 대화는 모델 개선 사용을 켜 두었어도 개선에 쓰지 않는다고 적혀 있습니다[1]. 서버에 얼마나 두는지는 공개 문서에 없어서 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)으로 확인해야 합니다. 기기 쪽에서는 시크릿 대화도 캐시 데이터베이스에 남고, 시크릿 여부 칸(`is_temporary`, iOS 는 `isTemporary`) 값이 1 입니다[12][13]. iLEAPP 시험 데이터에서는 시크릿 대화의 이름 칸이 비어 있었습니다[13]. 보관 설정의 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

## 한눈에 보기

| 판 | 위치 | 근거와 시험한 판 | 알려 주는 것 |
|---|---|---|---|
| 웹 브라우저 | claude.ai, 브라우저 프로필 | 해당 없음 | 방문·쿠키·캐시 흔적, 내보내기 파일을 받은 기록 |
| Windows 앱 | 스토어 판 `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\`[10], 그 밖의 설치 `%APPDATA%\Claude\`[7][10], 관리 정책 `HKLM`·`HKCU` 의 `SOFTWARE\Policies\Claude`[8][9] | agentsview 코드(2026-09), 패키지 폴더 관찰(Windows 11, 2026-09) | 처음 실행한 때·마지막으로 본 버전·마지막 계정 ID 같은 설정 값(관찰), MCP 설정과 로그, Cowork·Claude Code 세션 메타데이터와 `audit.jsonl`[11], 관리 정책 |
| macOS 앱 | `~/Library/Application Support/Claude/`[7][10][11], `~/Library/Logs/Claude/`[7], 관리 설정 도메인 `com.anthropic.claudefordesktop`[9] | 공식 문서(2026-09-25 열람), claude-forensics v0.1.1 | MCP 설정과 로그, Cowork·Claude Code 세션 기록, MDM 으로 내린 관리 설정 |
| Linux 앱 | `~/.config/Claude/`[10] | agentsview 코드(2026-09) | Cowork 세션 폴더 `local-agent-mode-sessions/` |
| Android 앱 | 앱 데이터 폴더 `com.anthropic.claude`[3] 안의 `databases/acc_*_claude_cache.db`, `cache/app_start/acc_*/org_*/cache.json`[12] | ALEAPP 분석기(2026-07-21~24 작성, 2026-08-09 갱신, Android 검체 두 개로 시험, 앱 판 기록 없음) | 대화 이름·모델·시크릿 여부, 메시지 본문·보낸 쪽(`human`·`assistant`)·시각, 프로젝트, 계정 이름·이메일 |
| iOS 앱 | 앱 컨테이너 `/private/var/mobile/Containers/Data/Application/` 아래 `Library/Application Support/ClaudeCache/cache_*.sqlite`, `Library/Caches/bootstrap/*.json`[13] | iLEAPP 분석기(2026-08-09 갱신, iOS 18.7.8·26.5.2 로 시험), App Store 판 1.260923.20(2026-09-25 기준, iOS·iPadOS 18.0 이상)[5] | 대화 이름·모델·시크릿 여부, 메시지 본문·보낸 쪽·시각, 프로젝트와 올린 문서 이름, 계정 이름·이메일 |
| 계정 데이터 내보내기 | 웹·데스크톱 앱에서 요청해 이메일 링크로 받는 ZIP[6], 안의 `conversations.json`·`users.json`·`projects.json`·`memories.json`[14] | 공식 도움말(2026-09-25 열람), 공개 내보내기 뷰어 코드 | 대화 제목, 메시지 본문, 보낸 쪽, 시각, 계정, 프로젝트, 메모리 |

Windows 데스크톱 폴더는 출처마다 적은 자리가 다릅니다. claude-forensics 문서(2026-06)는 `\Users\` 아래 사용자 폴더의 `AppData\Roaming\Claude\` 만 적고[11], agentsview 코드(2026-09)는 스토어 판(MSIX) 패키지 경로와 그 밖의 설치에 쓰는 `%APPDATA%\Claude\` 를 따로 적습니다[10]. 검체에서는 두 곳을 모두 찾아봅니다. 조직(Team·Enterprise) 관리자 내보내기도 같은 네 파일 이름을 씁니다[15].

## 읽는 순서

1. [웹 브라우저](web.md) — 브라우저로 claude.ai 를 쓴 흔적과 브라우저별로 찾아볼 곳을 정리합니다.
2. [Windows 앱](windows.md) — 패키지 폴더의 크롬 계열 저장소, 앱 JSON 설정 파일, MCP 로그, 관리 정책을 읽습니다.
3. [macOS 앱](macos.md) — 사용자 라이브러리의 MCP 설정·로그와 MDM 관리 설정을 봅니다.
4. [Android 앱](android.md) — 캐시 데이터베이스의 대화·메시지·프로젝트 표와 계정 JSON 을 읽습니다.
5. [iOS 앱](ios.md) — 앱 컨테이너의 캐시 SQLite 와 bootstrap JSON 을 읽습니다.
6. [계정 데이터 내보내기](export.md) — 내보내기 ZIP 의 네 JSON 파일과 대화·메시지 칸을 읽습니다.

데스크톱 앱의 `claude-code-sessions/`·`local-agent-mode-sessions/` 폴더와 `audit.jsonl` 은 [Claude Code 의 Windows 쪽](../../dev-agents/claude-code/windows.md)에서 다룹니다.

## 함께 볼 페이지

- [Claude Code](../../dev-agents/claude-code/index.md) — 데스크톱 앱에서 시작한 Claude Code·Cowork 세션의 기록
- [MCP 서버와 도구 호출 기록](../../dev-agents/mcp.md) — 데스크톱 앱에 연결한 로컬 도구의 설정과 로그
- [Electron·웹뷰 앱의 저장 구조](../../../01-foundations/storage-model/electron-webview.md) — 데스크톱 앱과 Android 앱 웹뷰의 크롬 계열 저장소
- [Claude 기업용 감사 로그](../../network-enterprise/claude-enterprise.md) — 조직 계정의 활동을 관리자 쪽에서 보는 경로
- [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) — 접속 시각과 기기를 네트워크 쪽에서 확인
- [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md) — 서비스마다 다른 내보내기 형식 비교
- [대화 내용 되살리기](../../../03-techniques/analysis/content-recovery.md) — 캐시·스냅숏에서 대화를 되살리는 방법
- [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md) — 계정 주인의 협조 없이 서버 쪽 기록을 확보하는 절차
- [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md) — 계정 기록과 실제 입력한 사람을 잇는 방법

## 참고 문헌

1. Anthropic Privacy Center, "How long do you store my data?" — https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data (2026-09-25 열람)
2. Claude Help Center, "Install Claude Desktop" — https://support.claude.com/en/articles/10065433-installing-claude-desktop (2026-09-25 열람)
3. Google Play, Claude by Anthropic 상세 페이지(주소의 패키지 ID) — https://play.google.com/store/apps/details?id=com.anthropic.claude (2026-09-25 열람)
4. Google Play, Claude by Anthropic 데이터 보안 — https://play.google.com/store/apps/datasafety?id=com.anthropic.claude (2026-09-25 열람)
5. App Store, Claude by Anthropic — https://apps.apple.com/us/app/claude-by-anthropic/id6473753684 (2026-09-25 열람)
6. Claude Help Center, "How can I export my Claude data?" — https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-data (2026-09-25 열람)
7. Model Context Protocol 문서, "Connect to local MCP servers" — https://modelcontextprotocol.io/docs/develop/connect-local-servers (2026-09-25 열람)
8. Claude Help Center, "Deploy Claude Desktop for Windows" — https://support.claude.com/en/articles/12622703-deploy-claude-desktop-for-windows (2026-09-25 열람)
9. Claude Help Center, "Enterprise configuration for Claude Desktop" — https://support.claude.com/en/articles/12622667-enterprise-configuration-for-claude-desktop (2026-09-25 열람)
10. kenn-io/agentsview, `internal/parser/cowork_paths.go` — https://github.com/kenn-io/agentsview (2026-09-25 열람)
11. forensicdave/claude-forensics v0.1.1, `README.md`, `docs/claude_forensics.md` — https://github.com/forensicdave/claude-forensics (2026-09-25 열람)
12. Brandon Baye, ALEAPP `scripts/artifacts/claude.py`(2026-08-09 갱신) — https://github.com/abrignoni/ALEAPP (2026-09-25 열람)
13. Brandon Baye, iLEAPP `scripts/artifacts/iOSclaude.py`(2026-08-09 갱신) — https://github.com/abrignoni/iLEAPP (2026-09-25 열람)
14. lordjabez/claude-export-viewer, `src/claude_export_viewer/loader.py` — https://github.com/lordjabez/claude-export-viewer (2026-09-25 열람)
15. ukogan/claude-migration-assistant, `js/processing/admin-reader.js` — https://github.com/ukogan/claude-migration-assistant (2026-09-25 열람)
