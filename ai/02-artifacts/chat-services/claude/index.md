---
title: "Claude"
parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 140
has_children: true
has_toc: false
---

# Claude (Claude)

Claude 는 웹·데스크톱(Windows·macOS·Linux)·Android·iOS 에서 같은 계정으로 쓰는 대화형 AI 서비스이고, 대화 원본은 계정 서버에 있어서 기기 흔적으로 사용 사실을 잡고 계정 데이터 내보내기로 대화 내용을 확인하는 식으로 두 쪽을 함께 봅니다.

> 확인 날짜: 2026-09-25. Claude 공식 도움말과 개인정보 안내 문서, MCP 문서, Google Play·App Store 페이지를 바탕으로 썼습니다. 기기 관찰은 Windows 데스크톱 앱(스토어 판)의 패키지 폴더에서 폴더·파일 이름과 키 이름만 본 것이고 값은 가렸습니다(확인 범위: Windows 11, 2026-09). 웹·macOS·Android·iOS 는 문서로만 확인했습니다.

## 왜 중요한가

Claude 는 웹 주소 claude.ai 와 데스크톱 앱, Android 앱, iOS/iPadOS 앱으로 제공되고[2][3][4][5], 데스크톱 앱은 macOS 11(Big Sur) 이상, Windows 10 이상, Ubuntu 22.04 LTS 이상과 Debian 12 이상(x64·arm64)에서 돌아갑니다[2]. 같은 계정으로 여러 기기에서 쓰는 서비스라, 한 기기에서 흔적을 찾지 못해도 다른 기기나 웹에서 쓴 기록이 계정에 남아 있을 수 있습니다. 로컬 앱 폴더에 대화 본문이 남는지는 문서로 확인하지 못했고, 개인정보 안내 문서는 보관과 삭제를 모두 서버 저장소 기준으로 설명합니다[1]. 서버·기기·동기화에 데이터가 나뉘는 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다.

서버에 대화가 얼마나 남는지는 설정과 사정에 따라 다릅니다. 개인정보 안내 문서에 적힌 기간은 아래와 같습니다[1].

| 경우 | 서버 쪽 보관 |
|---|---|
| 사용자가 대화를 지움 | 대화 목록에서 바로 사라지고, 서버 저장소에서는 30일 안에 지움 |
| 모델 개선 사용을 켬 | 비식별 형태로 최대 5년 |
| 모델 개선 사용을 끔 | 이전 대화와 새 대화를 이후 학습에 쓰지 않음 |
| 피드백으로 보낸 대화 | 5년 |
| 자동 안전 분류에 걸림 | 입력·출력은 최대 2년, 안전 분류 점수는 최대 7년 |
| 법적 요구·분쟁 해결·이용 정책 위반 대응 | 필요한 만큼 |

시크릿(Incognito) 대화는 모델 개선 사용을 켜 두었어도 개선에 쓰지 않는다고 적혀 있지만[1], 시크릿 대화를 서버에 얼마나 두는지와 대화 목록에 나오는지는 확인하지 못했습니다. 보관 설정의 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

기기 쪽에서는 판마다 남는 것이 크게 다릅니다. Windows 앱의 패키지 폴더에는 크롬 계열 저장소와 앱이 직접 쓰는 JSON 설정 파일이 보이고(확인 범위: Windows 11, 2026-09), macOS 앱은 문서로 확인한 MCP 설정·로그와 관리 설정이 주된 흔적입니다. 휴대전화 앱은 앱 데이터 안에 무엇이 남는지 확인하지 못해서 설치 흔적과 스토어의 개인정보 표기를 기준으로 삼습니다.

## 한눈에 보기

| 판 | 위치·식별자 | 확인한 버전 | 알려 주는 것 |
|---|---|---|---|
| 웹 브라우저 | claude.ai, 브라우저 프로필(사이트 저장소의 키는 확인하지 못함) | 해당 없음 | 방문·쿠키·캐시 흔적, 내보내기 파일을 받은 기록 |
| Windows 앱 | MSIX 패키지 폴더의 `LocalCache\Roaming\Claude\`(관찰, 확인 범위: Windows 11, 2026-09), 문서상 `%APPDATA%\Claude\`, `HKLM`·`HKCU` 의 `SOFTWARE\Policies\Claude`[7][8][9] | 확인하지 못함(관찰한 PC 의 버전 값은 가림) | 처음 실행한 때·마지막으로 본 버전·마지막 계정 ID 같은 설정 값, MCP 설정과 로그, 관리 정책 |
| macOS 앱 | `~/Library/Application Support/Claude/`, `~/Library/Logs/Claude/`, 관리 설정 도메인 `com.anthropic.claudefordesktop`[7][9] | 확인하지 못함 | MCP 설정과 로그, MDM 으로 내린 관리 설정 |
| Android 앱 | 패키지 ID `com.anthropic.claude`[3] | 확인하지 못함 | 설치 흔적, Play 데이터 보안 표기[4](앱 데이터 안의 파일은 확인하지 못함) |
| iOS 앱 | App Store 항목 `id6473753684` | 1.260923.20(2026-09-25 기준), iOS·iPadOS 18.0 이상[5] | 설치 흔적, App Store 개인정보 표기(컨테이너 안의 파일은 확인하지 못함) |
| 계정 데이터 내보내기 | 웹·데스크톱 앱에서 요청해 이메일 링크로 받는 ZIP, 안의 `conversations.json`[6] | 해당 없음 | 대화 제목, 메시지 본문, 보낸 쪽, 시각 |

Linux 데스크톱 앱은 지원 OS 만 확인했고, 이 허브에 따로 페이지를 두지 않았습니다.

## 읽는 순서

1. [웹 브라우저](web.md) — 브라우저로 claude.ai 를 쓴 흔적과 브라우저별로 찾아볼 곳을 정리합니다.
2. [Windows 앱](windows.md) — MSIX 패키지 폴더의 크롬 계열 저장소, 앱 JSON 설정 파일, MCP 로그, 관리 정책을 읽습니다.
3. [macOS 앱](macos.md) — 사용자 라이브러리의 MCP 설정·로그와 MDM 관리 설정을 봅니다.
4. [Android 앱](android.md) — 패키지 ID 로 설치 흔적을 찾고 Play 데이터 보안 표기를 해석합니다.
5. [iOS 앱](ios.md) — App Store 항목의 버전과 개인정보 표기를 봅니다.
6. [계정 데이터 내보내기](export.md) — 내보내기 ZIP 과 `conversations.json` 의 대화·메시지 칸을 읽습니다.

## 함께 볼 페이지

- [Claude Code](../../dev-agents/claude-code/index.md) — 데스크톱 앱에서 시작한 Claude Code 세션의 기록
- [MCP 서버와 도구 호출 기록](../../dev-agents/mcp.md) — 데스크톱 앱에 연결한 로컬 도구의 설정과 로그
- [Claude 기업용 감사 로그](../../network-enterprise/claude-enterprise.md) — 조직 계정의 활동을 관리자 쪽에서 보는 경로
- [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) — 접속 시각과 기기를 네트워크 쪽에서 확인
- [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md) — 서비스마다 다른 내보내기 형식 비교
- [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md) — 계정 주인의 협조 없이 서버 쪽 기록을 확보하는 절차
- [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md) — 계정 기록과 실제 입력한 사람을 잇는 방법

## 참고 문헌

1. Anthropic Privacy Center, "How long do you store my data?" — https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data (2026-09-25 열람)
2. Claude Help Center, "Install Claude Desktop" — https://support.claude.com/en/articles/10065433-installing-claude-desktop (2026-09-25 열람)
3. Google Play, Claude by Anthropic 상세 페이지(주소의 패키지 ID 만 확인) — https://play.google.com/store/apps/details?id=com.anthropic.claude (2026-09-25 열람)
4. Google Play, Claude by Anthropic 데이터 보안 — https://play.google.com/store/apps/datasafety?id=com.anthropic.claude (2026-09-25 열람)
5. App Store, Claude by Anthropic — https://apps.apple.com/us/app/claude-by-anthropic/id6473753684 (2026-09-25 열람)
6. Claude Help Center, "How can I export my Claude data?" — https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-data (2026-09-25 열람)
7. Model Context Protocol 문서, "Connect to local MCP servers" — https://modelcontextprotocol.io/docs/develop/connect-local-servers (2026-09-25 열람)
8. Claude Help Center, "Deploy Claude Desktop for Windows" — https://support.claude.com/en/articles/12622703-deploy-claude-desktop-for-windows (2026-09-25 열람)
9. Claude Help Center, "Enterprise configuration for Claude Desktop" — https://support.claude.com/en/articles/12622667-enterprise-configuration-for-claude-desktop (2026-09-25 열람)
