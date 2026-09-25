---
title: "Claude Code macOS"
parent: "Claude Code"
grand_parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 540
---

# macOS (macOS)

macOS 에서 Claude Code 는 기록과 설정을 다른 OS 와 같은 `~/.claude/` 와 `~/.claude.json` 에 두지만, 로그인 정보는 키체인에 넣고 키체인에 쓰지 못할 때만 파일로 남깁니다.

> 확인 날짜: 2026-09. 이 페이지는 공식 문서(2026-09-25 열람)만 근거로 썼고, macOS 기기는 직접 관찰하지 않았습니다. 본문의 v2.1.x 같은 번호는 문서 문장을 그대로 옮긴 것입니다.

## 무엇이 남나 · 왜 생기나

macOS 에서도 대화 전문, 입력한 프롬프트 목록, 편집 전 파일 사본은 홈 폴더의 `~/.claude/` 에 남고, 짜임은 [세션 기록 구조](transcripts.md)와 [설정·권한·훅](settings-permissions.md)에서 다룹니다. 이 페이지는 macOS 에서 달라지는 부분, 곧 설치 방식에 따라 옛 버전이 디스크에 남는 방식과 키체인에 들어가는 로그인 정보, 관리 정책 위치를 다룹니다.

## 위치

| 경로 | 담긴 것 |
|---|---|
| `~/.local/bin/claude` | 네이티브 설치의 실행 링크(심볼릭 링크) |
| `~/.local/share/claude/versions/` | 네이티브 설치로 받은 버전들 |
| `~/.claude/` | 사용자 데이터 폴더(기록·설정·캐시) |
| `~/.claude.json` | 로그인 세션, MCP 서버 설정, 프로젝트별 상태, `/config` 전역 값 |
| 로그인 키체인 | 구독 계정 로그인 정보 |
| `~/.claude/.credentials.json` | 키체인에 쓰지 못했을 때의 로그인 정보(파일 모드 0600) |
| `~/.config/anthropic` | Anthropic 프로필 설정(ant CLI, 워크로드 ID 연동) |
| `/Library/Application Support/ClaudeCode/managed-settings.json`, `managed-settings.d/`, `managed-mcp.json` | 관리 정책 파일 |
| 관리 환경설정 도메인 `com.anthropic.claudecode` | MDM 구성 프로파일로 내려온 정책 |

만든 예시로 사용자 `examiner01` 의 기록 파일 경로는 `/Users/examiner01/.claude/projects/` 아래 프로젝트 폴더의 세션 파일이 되고, 네이티브 설치 버전은 `/Users/examiner01/.local/share/claude/versions/` 아래에 있습니다. 프로젝트 폴더 이름을 경로에서 어떻게 바꿔 만드는지는 문서에서 확인하지 못했습니다.

`CLAUDE_CONFIG_DIR` 환경 변수로 데이터 폴더를 옮길 수 있고, 이렇게 옮기면 키체인 항목도 그 폴더에 묶여 따로 생깁니다. 한 사용자 계정에 키체인 항목이 여럿 보이면 데이터 폴더도 여럿일 수 있어서, 셸 설정 파일에서 이 변수를 찾아봅니다.

## 설치 방법별 차이

| 설치 방법 | 옛 버전이 남는 곳 | 업데이트 |
|---|---|---|
| 네이티브 설치기(`install.sh`) | `~/.local/share/claude/versions/` | 스스로 업데이트 |
| Homebrew `claude-code`(stable 채널), `claude-code@latest`(latest 채널) | Homebrew 폴더, `brew cleanup` 전까지 | 스스로 업데이트하지 않음 |
| npm(`@anthropic-ai/claude-code`) | 확인하지 못함 | 확인하지 못함 |

네이티브 설치에서 `~/.local/bin/claude` 는 `versions/` 안의 한 버전을 가리키는 심볼릭 링크입니다. 업데이트는 백그라운드에서 받고 다음 실행부터 적용되므로, 링크가 가리키는 곳은 마지막으로 쓴 버전이 아니라 다음 실행에 쓸 버전일 수 있습니다. 사용자가 링크를 자기 스크립트나 링크로 바꾼 경우에는 어느 버전이 필요한지 가릴 수 없어 설치한 모든 버전을 디스크에 남기고, v2.1.207 전에는 업데이트할 때마다 바꾼 링크를 다시 덮어썼습니다. 링크를 바꾸지 않은 보통 설치에서 옛 버전이 모두 남는다는 문서 설명은 찾지 못했습니다. Homebrew 로 깐 경우에는 `brew cleanup` 을 돌리기 전까지 옛 버전이 남아서, 버전 폴더 목록으로 어떤 버전을 거쳐 왔는지 가늠해 볼 수 있습니다. 실행 파일은 "Anthropic PBC" 가 서명하고 Apple 공증을 받았습니다.

## 로그인 정보 보호

macOS 에서는 로그인 정보를 암호화된 [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html)에 넣습니다. SSH 세션처럼 키체인이 잠겨 쓰기를 거부하면 `~/.claude/.credentials.json` 에 파일 모드 0600 으로 대신 저장하고, 이 파일은 [Windows](windows.md)의 같은 이름 파일처럼 평문입니다. 원격 접속으로만 쓰던 Mac 에서 이 파일이 나온다면 키체인 쓰기 실패와 관련이 있을 수 있지만, 파일 하나로 접속 방식을 단정하지는 않습니다.

키체인 항목의 서비스 이름은 확인하지 못했습니다. 키체인 안의 값을 여는 방법은 이 페이지에서 다루지 않고, 항목이 있었다는 사실과 생성·수정 시각만 기록합니다. 토큰이 남는 다른 곳은 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에 모아 두었습니다.

## 관리 정책

관리 정책은 `/Library/Application Support/ClaudeCode/` 아래 파일이나 MDM 구성 프로파일로 내려옵니다. 구성 프로파일은 관리 환경설정 도메인 `com.anthropic.claudecode` 를 쓰고, 그 안의 최상위 키는 `managed-settings.json` 과 같습니다. 관리 환경설정을 읽는 법은 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/plist/index.html) 페이지를 참고합니다. 여러 소스 사이의 순서는 [설정·권한·훅](settings-permissions.md)에서 다룹니다.

## 버전에 따라 달라지는 곳

| 항목 | 문서가 밝힌 차이 |
|---|---|
| 붙여 넣은 이미지·첨부 이미지 | v2.1.274 이하는 `~/.claude/image-cache/` 아래 세션별 폴더, 그 뒤는 `CLAUDE_CODE_TMPDIR` 이 정하는 임시 폴더 아래 세션별 `images/`(macOS 에서 실제로 풀리는 경로는 확인하지 못함) |
| 권한 거부 규칙 | v2.1.268 부터 `/etc` 가 `/private/etc` 로 풀리는 것처럼 심볼릭 링크 폴더를 거쳐 적은 거부·묻기 규칙을 실제 위치에도 적용(macOS·Linux) |

이미지가 `image-cache` 에 없다고 첨부가 없었다고 보지 않고, 먼저 설치 버전을 확인합니다.

## 증거로서 의미

**증명하는 것.** 버전 폴더와 실행 링크가 있으면 그 사용자 계정에 Claude Code 를 설치한 흔적이 있다고 쓸 수 있습니다. 버전 폴더 목록은 디스크에 남은 버전만 보여 주고, 거쳐 온 버전 전부라고 보지는 않습니다. 관리 정책 파일이나 구성 프로파일이 있으면 그 Mac 에 정책이 놓여 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** 키체인 항목과 데이터 폴더는 그 계정으로 누가 작업했는지 알려 주지 않습니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 클라우드에서 돈 세션은 이 Mac 에 기록이 없을 수 있고, 로컬 기록은 기본 30일 뒤 지워집니다.

## 시각 해석

기록 안의 시각은 [세션 기록 구조](transcripts.md)를 따릅니다. 폴더가 언제 생기고 바뀌었는지는 [파일 시스템 이벤트](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/filesystem/fsevents/index.html)에서 `~/.claude/` 와 `~/.local/share/claude/versions/` 경로를 찾아 맞춰 봅니다. 버전 폴더가 새로 생긴 시각은 업데이트 시각을 가늠하는 데 쓸 수 있지만, 스스로 업데이트하는 설치에서는 사용자가 그 시각에 앱을 켰다는 뜻까지는 아닙니다.

## 함정과 한계

이 페이지에는 기기 관찰이 없어서, 파일이 실제로 어떤 모양인지는 검체에서 확인합니다. `CLAUDE_CONFIG_DIR` 로 옮긴 데이터 폴더는 `~/.claude/` 에 없고 키체인 항목도 따로 있습니다. Homebrew 설치는 `brew cleanup` 을 돌리면 옛 버전이 사라지고, `/logout` 은 로그인 정보를 지우므로, 버전 폴더나 로그인 정보가 없다는 사실만으로 쓰지 않았다고 보지 않습니다.

## 직접 분석해 보기

**헥스로 한 번.** 파일로 남은 `.credentials.json` 은 평문 JSON 이라서 [Windows](windows.md) 페이지의 헥스 예시와 같은 방법으로 읽습니다.

**공개 도구로 한 번.** 살아 있는 Mac 에서는 기본 명령으로 서명과 설치 버전을 읽기만 합니다. 아래 사용자 이름은 만든 예시입니다.

```sh
# 만든 예시: 사용자 examiner01
codesign --verify --verbose /Users/examiner01/.local/bin/claude
readlink /Users/examiner01/.local/bin/claude
ls -la /Users/examiner01/.local/share/claude/versions/
ls -la "/Library/Application Support/ClaudeCode/"
```

## 교차 검증

폴더 시각은 [FSEvents](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/filesystem/fsevents/index.html)와, 기록 시각은 [macOS 타임라인](https://urock-ailab.github.io/forensics-handbook-mac/03-techniques/analysis/timeline/index.html)과 맞춰 봅니다. 모델 호출이 나간 시간대는 [네트워크 기록](../../network-enterprise/network-traces.md)으로, 에이전트가 실행한 명령과 바꾼 파일은 [AI 에이전트가 무엇을 실행했나](../../../04-scenarios/agents/agent-actions.md)로 이어 봅니다.

## 실습

공개 검체에 Claude Code 흔적이 들어 있는지는 확인하지 못했습니다. 시험용 Mac 이나 가상 머신에 직접 깔아 만든 검체로 풀어 봅니다.

1. 네이티브 설치로 두 번 업데이트한 뒤 `versions/` 에는 무엇이 남고, 실행 링크는 어디를 가리킵니까?
2. SSH 로 접속해 로그인했을 때와 화면 앞에서 로그인했을 때 `.credentials.json` 이 생기는지 비교해 봅니다.
3. `CLAUDE_CONFIG_DIR` 을 지정해 로그인하면 키체인 항목은 몇 개가 됩니까?
4. FSEvents 에서 `~/.claude/projects/` 아래 파일이 처음 생긴 시각과 기록 첫 줄의 시각은 얼마나 차이 납니까?

## 참고 문헌

1. Settings files and precedence — https://code.claude.com/docs/en/settings
2. .claude 폴더 파일·폴더 참조(claude-directory) — https://code.claude.com/docs/en/claude-directory
3. Deploy managed settings — https://code.claude.com/docs/en/managed-settings
4. Authentication — https://code.claude.com/docs/en/authentication
5. Configure permissions — https://code.claude.com/docs/en/permissions
6. Advanced setup — https://code.claude.com/docs/en/setup
