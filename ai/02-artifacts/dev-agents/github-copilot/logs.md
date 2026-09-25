---
title: "로그와 원격 측정"
parent: "GitHub Copilot"
grand_parent: "아티팩트 · 개발 도구·에이전트"
nav_order: 600
---

# 로그와 원격 측정 (Logs·Telemetry)

GitHub Copilot 은 IDE 마다 로그를 남기는 자리가 다르고(VS Code 는 출력 창과 확장 로그 폴더, JetBrains 는 `idea.log`), VS Code 자체의 원격 측정은 `telemetry.telemetryLevel` 설정에 따라 보내는 범위가 달라집니다.

> 확인 날짜: 2026-09. GitHub·VS Code 공식 문서(2026-09-25 열람)와 VS Code 오픈소스 코드(`chatSessionStore.ts`, 그 파일의 마지막 커밋 2026-08-06)를 근거로 썼습니다. 이 PC 에서 Copilot 로그를 관찰한 기록은 없어서 로그 파일의 실제 줄 모양은 확인하지 않았고, Copilot 확장·플러그인 버전도 확인하지 않았습니다.

## 무엇을 기록하나 · 왜 생기나

Copilot 로그는 연결 문제나 오류를 풀려고 남기는 기록이라서, 문서도 문제 해결 순서로 설명합니다. 문서가 로그 보는 법을 안내하는 IDE 는 JetBrains IDE(IntelliJ IDEA, Android Studio, GoLand, PhpStorm, PyCharm, RubyMine, WebStorm, Rider), VS Code, Visual Studio, Xcode, Vim/Neovim 입니다. 로그에 프롬프트나 응답 본문이 들어가는지는 문서에 없어서 확인하지 못했고, 대화 내용 자체는 [Windows](windows.md)에서 다루는 세션 파일에서 찾습니다.

## 위치와 여는 법

| IDE | 여는 법 | 파일·경로 |
|---|---|---|
| VS Code | View → Output 에서 "GitHub Copilot" 채널 선택 | — |
| VS Code | 명령 팔레트 `Developer: Open Extension Logs Folder` | 확장 로그 폴더(OS 별 경로 확인 못 함) |
| VS Code | `Developer: Toggle Developer Tools` → Console 탭 | Electron 로그 |
| JetBrains | Help → Show Log in …(Rider 는 Diagnostic Tools 아래) | `idea.log`(OS 별 경로 확인 못 함) |
| Visual Studio | View → Output 에서 "GitHub Copilot" 선택 | — |
| Xcode | Advanced → Open Copilot Log Folder | 경로는 [macOS](macos.md) |
| Vim/Neovim | `:Copilot status` 로 상태 확인 | 로그 파일 위치 확인 못 함 |

VS Code 안에서는 "GitHub Copilot" 과 "GitHub Copilot Chat" 이 로그 설정 화면에 서로 다른 확장 이름으로 나옵니다.

## 사용자가 켜야 생기는 기록

아래 기록은 평소에는 없고, 사용자가 문서의 안내대로 일부러 켜거나 명령을 돌려야 생깁니다.

| IDE | 켜는 법 | 남는 것 |
|---|---|---|
| VS Code | `Developer: Set Log Level` → "GitHub Copilot Chat" 또는 "GitHub" → Trace | 자세한 로그. 문서는 끝나면 Info 로 되돌리라고 안내 |
| VS Code | `Developer: Chat Diagnostics` | 새 편집기 창에 진단 결과. "Reachability" 절 포함 |
| JetBrains | Help → Diagnostic Tools → Debug Log Settings 에 `#com.github.copilot:trace` 한 줄 추가 | `idea.log` 에 자세한 로그. 네트워크 문제 확인용 |
| JetBrains | Tools → GitHub Copilot → Log Diagnostics | `idea.log` 에 진단 결과. "Reachability" 절 포함 |
| JetBrains | Tools → GitHub Copilot → Log CA Certificates | 신뢰하는 CA 인증서를 PEM 형식으로 `idea.log` 에 남김 |
| Xcode | Advanced → Logging → Verbose Logging | 자세한 로그 |

`idea.log` 에 trace 줄이나 "Reachability" 절, PEM 인증서 덩어리가 있으면 그 무렵 누군가 Copilot 연결 문제를 풀려고 손댔다고 읽을 수 있습니다. 다만 문서에 그렇게 적혀 있지는 않고, 사용자가 켜야 생긴다는 안내를 바탕으로 한 추론이라서 보고서에는 추론이라고 밝혀 씁니다.

## VS Code 가 남기는 세션 저장 흔적

VS Code 소스(2026-08 기준)는 채팅 세션 저장 중 오류가 나면 원격 측정 이벤트 `chatSessionStoreError` 를 보냅니다. 세션 색인을 정리할 때는 trace 수준으로 `ChatSessionStore: Trimmed N old chat sessions from index` 를 남기고, 예전 위치에서 세션을 읽을 때는 info 수준으로 `ChatSessionStore: Read chat session <ID> from previous location` 을 남깁니다. 앞 문장이 보이면 로컬 세션이 400개를 넘어 오래된 세션이 색인에서 빠졌다는 뜻이고, 뒤 문장은 예전 빈 창 위치 같은 옛 폴더의 세션을 읽었다는 뜻입니다. 앞 문장은 trace 수준이라 기본 설정의 로그에서는 보이지 않을 수 있습니다. 이 로그가 어느 파일에 쓰이는지는 확인하지 못했습니다. 색인과 폴더 구조는 [Windows](windows.md)에 있습니다.

## VS Code 원격 측정

VS Code 는 충돌 보고, 오류 원격 측정, 사용 데이터 세 가지를 모으고, 설정 키 `telemetry.telemetryLevel` 로 보내는 범위를 정합니다.

| 값 | 보내는 것 |
|---|---|
| `all` | 충돌·오류·사용 데이터 |
| `error` | 충돌·오류 |
| `crash` | 충돌만 |
| `off` | 보내지 않음 |

로컬에서 확인하는 방법도 문서에 있습니다. `Developer: Show Telemetry` 는 추적을 켜고 Telemetry 출력 채널을 열며, `Developer: Open Log...` 로 로컬 `telemetry.log` 파일을 열 수 있고, `Developer: Reload Window` 로 추적을 끕니다. `code --telemetry` 를 돌리면 VS Code 가 보낼 수 있는 원격 측정 이벤트 목록을 JSON 으로 뽑습니다. `telemetry.log` 의 OS 별 경로는 확인하지 못했습니다.

문서는 확장이 `telemetry.telemetryLevel` 을 따르지 않고 자체 원격 측정을 할 수 있다고 적고, 확장마다 문서를 보라고 합니다. 같은 문서는 Copilot Chat 이 OpenTelemetry 로 추적·지표·이벤트를 내보낼 수 있다고만 적고 자세한 내용은 따로 두어서, Copilot 확장이 이 설정을 따르는지는 확인하지 못했습니다. 그래서 `settings.json` 에 `off` 가 들어 있어도 Copilot 이 아무것도 보내지 않았다고 결론 내리지 않습니다. 아래는 만든 예시입니다.

```json
{
  "telemetry.telemetryLevel": "error"
}
```

## 서버 쪽 기록

GitHub 가 프롬프트·응답·사용 기록을 얼마나 보관하는지, 학습에 쓰는지는 공식 자료를 열지 못해 확인하지 못했습니다. 조직 요금제(Business·Enterprise)의 감사 로그나 사용 기록에 어떤 항목이 남는지도 확인하지 못했습니다. 서버 쪽 기록을 얻는 일반적인 방법은 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)과 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)를 봅니다.

## 증거로서 의미

Copilot 로그가 있으면 그 IDE 에 Copilot 확장이나 플러그인이 설치돼 돌았다는 흔적이 되고, 사용자가 켜야 생기는 기록은 누군가 문제 해결을 시도했다는 추론의 근거가 됩니다. 원격 측정 설정 값은 그 계정의 VS Code 가 어느 범위까지 보내도록 설정돼 있었는지를 알려 줍니다.

반면 로그로는 어떤 프롬프트를 보냈는지나 제안을 받아들였는지를 증명하지 못합니다. 본문이 로그에 들어가는지 확인하지 못했기 때문이고, 원격 측정 설정도 확장의 자체 원격 측정까지 막았다는 증명이 되지 못합니다.

## 함정과 한계

- 출력 창과 명령 팔레트로 여는 방법은 VS Code 를 실행해야 쓸 수 있어서, 수집한 디스크 이미지에서는 확장 로그 폴더를 파일로 찾아야 합니다. 그 폴더의 OS 별 경로는 확인하지 못했으니 VS Code 사용자 데이터 폴더를 통째로 떠 옵니다.
- trace 수준을 끝나면 Info 로 되돌리라는 안내가 있어서, 수집 시점의 설정이 Info 여도 과거에 trace 로 남긴 로그가 있을 수 있습니다.
- 헥스로 따라갈 만한 로그 형식 명세는 찾지 못해서 이 페이지에는 헥스 예시를 두지 않았습니다.

## 교차 검증

- 세션 파일과 색인 → [Windows](windows.md), [macOS](macos.md)
- 네트워크 기록 → [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)
- 기업 보안 제품 기록 → [보안 제품이 남기는 AI 사용 기록](../../network-enterprise/dlp-casb.md)

## 실습

Copilot 로그가 들어 있는 공개 검체는 확인하지 못해서, 직접 만든 시험 환경(가짜 사용자 `analyst01`)에서 풀어 봅니다.

1. VS Code 에서 로그 수준을 Trace 로 바꾸기 전과 뒤에 확장 로그 폴더의 파일은 어떻게 달라지는가?
2. JetBrains 에서 Log CA Certificates 를 한 번 돌린 뒤 `idea.log` 에서 PEM 덩어리를 찾을 수 있는가?
3. `telemetry.telemetryLevel` 을 `off` 로 둔 채 `Developer: Show Telemetry` 를 켜면 Telemetry 출력 채널에 무엇이 보이는가?

## 참고 문헌

1. Viewing logs for GitHub Copilot in your environment — https://docs.github.com/en/copilot/troubleshooting-github-copilot/viewing-logs-for-github-copilot-in-your-environment
2. microsoft/vscode 소스 `chatSessionStore.ts`(main, 마지막 커밋 2026-08-06) — https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/chat/common/model/chatSessionStore.ts
3. Telemetry — Visual Studio Code(2026-09-16 갱신) — https://code.visualstudio.com/docs/configure/telemetry
