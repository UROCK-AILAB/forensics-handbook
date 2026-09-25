---
title: 처음
nav_order: -100
permalink: /
---

# AI 서비스 디지털 포렌식 핸드북

ChatGPT·Claude·Copilot·Gemini 같은 AI 서비스를 쓰면 기기와 계정에 어떤 흔적이 남는지, 그 흔적을 어떻게 읽고 해석하는지 정리한 한국어 핸드북입니다. 포렌식을 공부하는 사람과 현업에서 사건을 분석하는 사람을 위해 작성했습니다.

같은 서비스라도 Windows·macOS·Android·iOS 마다 저장 위치와 보호 방식이 다르므로, 주요 서비스는 OS 별로 나눠 설명합니다. 대화 원본이 서버에만 남는 경우가 많아서, 계정 데이터 내보내기와 기업용 감사 기록도 함께 다룹니다.

AI 앱은 자주 바뀝니다. 이 핸드북은 2026년 9월 기준입니다. OS 자체의 저장 구조는 [Windows](https://urock-ailab.github.io/forensics-handbook-windows/)·[macOS](https://urock-ailab.github.io/forensics-handbook-mac/)·[Android](https://urock-ailab.github.io/forensics-handbook-android/)·[iOS](https://urock-ailab.github.io/forensics-handbook-ios/) 핸드북에서 다룹니다.

## 구성

핸드북은 네 갈래로 나뉩니다.

| 갈래 | 다루는 것 |
|---|---|
| **기반 구조** | AI 서비스의 데이터가 서버·기기 중 어디에 있는지, Electron·웹뷰 앱 저장 구조, 계정 데이터 내보내기 형식, API 키가 남는 곳, AI 생성물 출처 정보(C2PA) |
| **아티팩트 사전** | ChatGPT·Claude·Copilot·Gemini(OS 별), 국내 서비스, 업무 도구 속 AI, Claude Code·Copilot·Cursor 같은 개발 도구, Ollama 같은 로컬 AI, 네트워크·기업용 감사 기록 |
| **분석 기법** | 서비스 회사에 대한 데이터 요청, 내보내기로 수집, 기기에서 흔적 모으기, 타임라인, 대화 내용 되살리기, AI 생성물 판별의 한계, 프롬프트 인젝션 사고 분석 |
| **조사 시나리오** | "기밀 자료를 AI에 넣었나", "AI 에이전트가 무엇을 실행했나" 같은 질문 하나에 여러 기록을 엮어 답하는 흐름 |

큰 주제는 허브 페이지에서 전체를 보여 주고, 하위 페이지에서 OS 별로 자세히 다룹니다.

## 페이지 구성

아티팩트 페이지는 대체로 아래 순서로 씁니다.

1. 무엇을 기록하고, 그 기록이 왜 생기는지
2. 저장 위치 — OS·앱 버전마다 다른 점
3. 구조 — 파일·표·칸 이름, 설정 키
4. 증거로 쓸 때 — 증명할 수 있는 것과 없는 것
5. 시각 읽기 — 언제 바뀌는지, 어떤 기준 시각을 쓰는지
6. 함정과 한계 — 서버에만 있는 것, 자주 하는 오해, 지웠을 때 남는 흔적
7. 직접 분석하기 — 파일을 직접 열어 한 번, 공개 도구로 한 번
8. 함께 볼 기록 — 다른 기록과 맞춰 보기
9. 실습 질문과 참고 자료

## 읽는 법

- 처음이라면 [AI 서비스의 데이터는 어디에 있나](01-foundations/storage-model/where-data-lives.md)부터 읽기를 권합니다.
- 사건을 앞에 두고 있다면 조사 시나리오에서 질문을 고르면 됩니다. 예: [기밀 자료를 AI에 넣었나](04-scenarios/data-leak/confidential-input.md), [AI 에이전트가 무엇을 실행했나](04-scenarios/agents/agent-actions.md)
- 특정 서비스만 궁금하다면 아래 목차에서 바로 찾으면 됩니다.

## 표기

- 명세나 공식 문서로 확인한 사실은 그대로 씁니다.
- 기기에서 본 내용은 Windows 11 기준입니다. 앱 판에 따라 달라지는 경로와 칸은 그 자리에 판을 적습니다.
- 확인되지 않은 것은 쓰지 않습니다. 버전·기기마다 다를 수 있는 것은 분석가가 직접 확인하는 방법을 적습니다.
- 특정 회사 제품을 편들지 않고 같은 기준으로 씁니다.
- 용어는 처음 나올 때 "한국어 (English)"로 한 번 적습니다.

# 목차


## 기반 구조

### 저장 구조

- [AI 서비스의 데이터는 어디에 있나 (서버·기기·동기화)](01-foundations/storage-model/where-data-lives.md)
- [Electron·웹뷰 앱의 저장 구조 (Electron·WebView2·WKWebView)](01-foundations/storage-model/electron-webview.md)
- [계정 데이터 내보내기 형식 (Data Export Formats)](01-foundations/storage-model/data-export-formats.md)
- [API 키와 토큰이 남는 곳 (API Keys·Tokens)](01-foundations/storage-model/api-keys-tokens.md)
- [대화 기록 보관 설정과 삭제 (Retention·Deletion)](01-foundations/storage-model/retention-deletion.md)

### 기본 개념

- [프롬프트·첨부·생성물 구분하기 (Prompt·Attachment·Output)](01-foundations/concepts/prompt-attachment-output.md)
- [AI 생성물의 출처 정보 (C2PA·Content Credentials·워터마크)](01-foundations/concepts/c2pa-provenance.md)

## 아티팩트 사전

### 대화형 AI 서비스

- [ChatGPT (ChatGPT)](02-artifacts/chat-services/chatgpt/index.md)
  - [웹 브라우저 (Web)](02-artifacts/chat-services/chatgpt/web.md)
  - [Windows 앱 (Windows)](02-artifacts/chat-services/chatgpt/windows.md)
  - [macOS 앱 (macOS)](02-artifacts/chat-services/chatgpt/macos.md)
  - [Android 앱 (Android)](02-artifacts/chat-services/chatgpt/android.md)
  - [iOS 앱 (iOS)](02-artifacts/chat-services/chatgpt/ios.md)
  - [계정 데이터 내보내기 (Data Export)](02-artifacts/chat-services/chatgpt/export.md)
- [Claude (Claude)](02-artifacts/chat-services/claude/index.md)
  - [웹 브라우저 (Web)](02-artifacts/chat-services/claude/web.md)
  - [Windows 앱 (Windows)](02-artifacts/chat-services/claude/windows.md)
  - [macOS 앱 (macOS)](02-artifacts/chat-services/claude/macos.md)
  - [Android 앱 (Android)](02-artifacts/chat-services/claude/android.md)
  - [iOS 앱 (iOS)](02-artifacts/chat-services/claude/ios.md)
  - [계정 데이터 내보내기 (Data Export)](02-artifacts/chat-services/claude/export.md)
- [Microsoft Copilot (Copilot)](02-artifacts/chat-services/copilot/index.md)
  - [웹 브라우저 (Web)](02-artifacts/chat-services/copilot/web.md)
  - [Windows 앱 (Windows)](02-artifacts/chat-services/copilot/windows.md)
  - [macOS 앱 (macOS)](02-artifacts/chat-services/copilot/macos.md)
  - [Android 앱 (Android)](02-artifacts/chat-services/copilot/android.md)
  - [iOS 앱 (iOS)](02-artifacts/chat-services/copilot/ios.md)
  - [계정 데이터 내보내기 (Data Export)](02-artifacts/chat-services/copilot/export.md)
- [Gemini (Gemini)](02-artifacts/chat-services/gemini/index.md)
  - [웹 브라우저 (Web)](02-artifacts/chat-services/gemini/web.md)
  - [Android 앱 (Android)](02-artifacts/chat-services/gemini/android.md)
  - [iOS 앱 (iOS)](02-artifacts/chat-services/gemini/ios.md)
  - [Chrome 통합 (Gemini in Chrome)](02-artifacts/chat-services/gemini/chrome.md)
  - [계정 데이터 내보내기 (Data Export)](02-artifacts/chat-services/gemini/export.md)
- [Perplexity (Perplexity)](02-artifacts/chat-services/perplexity.md)
- [뤼튼 (Wrtn)](02-artifacts/chat-services/wrtn.md)
- [클로바X (CLOVA X)](02-artifacts/chat-services/clova-x.md)
- [에이닷 (A.)](02-artifacts/chat-services/adot.md)
- [그 밖의 서비스 (DeepSeek·Grok 등)](02-artifacts/chat-services/other-services.md)
- [AI 컴패니언 앱 (Replika·Character.AI 등)](02-artifacts/chat-services/companion-apps.md)
- [Meta AI 앱과 AI 안경 (Meta AI·Ray-Ban Meta)](02-artifacts/chat-services/meta-ai-glasses.md)

### 에이전트형 서비스

- [ChatGPT 에이전트 모드 (ChatGPT Agent)](02-artifacts/agentic-services/chatgpt-agent.md)
- [브라우저를 조작하는 AI (Browser Agents)](02-artifacts/agentic-services/browser-agents.md)
- [AI 에이전트 브라우저 (Comet·Fellou 등)](02-artifacts/agentic-services/ai-browsers.md)

### 생성·음성·회의록

- [Midjourney와 이미지 생성 서비스 (Midjourney·Image Generation)](02-artifacts/generative-media/image-generation.md)
- [음성 대화 기능 (Voice Mode)](02-artifacts/generative-media/voice-mode.md)
- [AI 회의록 앱 (클로바노트·Otter 등)](02-artifacts/generative-media/meeting-notes.md)

### 번역 AI

- [파파고 (Papago)](02-artifacts/translation/papago.md)
- [DeepL (DeepL)](02-artifacts/translation/deepl.md)

### Windows의 AI 기능

- [Recall (Recall)](02-artifacts/windows-ai/recall.md)
- [클릭 투 두 (Click to Do)](02-artifacts/windows-ai/click-to-do.md)

### 업무 도구 속 AI

- [Microsoft 365 Copilot (M365 Copilot)](02-artifacts/office-integrations/m365-copilot.md)
- [Google Workspace의 Gemini (Workspace Gemini)](02-artifacts/office-integrations/workspace-gemini.md)
- [협업 도구의 AI 기능 (Notion AI·Slack AI 등)](02-artifacts/office-integrations/workspace-ai-features.md)
- [브라우저에 들어간 AI (Edge Copilot·Chrome Gemini 등)](02-artifacts/office-integrations/browser-builtin-ai.md)

### 개발 도구·에이전트

- [Claude Code (Claude Code)](02-artifacts/dev-agents/claude-code/index.md)
  - [Windows (Windows)](02-artifacts/dev-agents/claude-code/windows.md)
  - [macOS (macOS)](02-artifacts/dev-agents/claude-code/macos.md)
  - [세션 기록 구조 (Transcripts)](02-artifacts/dev-agents/claude-code/transcripts.md)
  - [설정·권한·훅 (Settings·Permissions·Hooks)](02-artifacts/dev-agents/claude-code/settings-permissions.md)
- [GitHub Copilot (VS Code·JetBrains)](02-artifacts/dev-agents/github-copilot/index.md)
  - [Windows (Windows)](02-artifacts/dev-agents/github-copilot/windows.md)
  - [macOS (macOS)](02-artifacts/dev-agents/github-copilot/macos.md)
  - [로그와 원격 측정 (Logs·Telemetry)](02-artifacts/dev-agents/github-copilot/logs.md)
- [Cursor (Cursor)](02-artifacts/dev-agents/cursor.md)
- [Codex CLI (Codex)](02-artifacts/dev-agents/codex-cli.md)
- [Gemini CLI (Gemini CLI)](02-artifacts/dev-agents/gemini-cli.md)
- [MCP 서버와 도구 호출 기록 (MCP)](02-artifacts/dev-agents/mcp.md)

### 로컬 AI

- [Ollama (Ollama)](02-artifacts/local-ai/ollama.md)
- [LM Studio (LM Studio)](02-artifacts/local-ai/lm-studio.md)
- [Chatbox (Chatbox)](02-artifacts/local-ai/chatbox.md)
- [Msty (Msty)](02-artifacts/local-ai/msty.md)
- [Jan (Jan)](02-artifacts/local-ai/jan.md)
- [GPT4All (GPT4All)](02-artifacts/local-ai/gpt4all.md)
- [AnythingLLM (AnythingLLM)](02-artifacts/local-ai/anythingllm.md)
- [로컬 이미지 생성 도구 (Stable Diffusion WebUI·ComfyUI)](02-artifacts/local-ai/image-gen-local.md)
- [로컬 모델 파일 (GGUF·safetensors)](02-artifacts/local-ai/model-files.md)

### 네트워크·기업 기록

- [AI 서비스 도메인과 네트워크 기록 (DNS·Proxy·SNI)](02-artifacts/network-enterprise/network-traces.md)
- [ChatGPT 기업용 감사 기록 (Compliance API)](02-artifacts/network-enterprise/chatgpt-enterprise.md)
- [Claude 기업용 감사 로그 (Audit Logs)](02-artifacts/network-enterprise/claude-enterprise.md)
- [Microsoft Purview로 본 Copilot 기록 (Purview)](02-artifacts/network-enterprise/purview-copilot.md)
- [보안 제품이 남기는 AI 사용 기록 (DLP·CASB)](02-artifacts/network-enterprise/dlp-casb.md)

## 분석 기법

### 조사 절차·증거 확보

- [조사 절차 (Investigation Process)](03-techniques/acquisition/investigation-process.md)
- [서비스 회사에 대한 데이터 요청 (Legal Requests)](03-techniques/acquisition/legal-requests.md)
- [계정 데이터 내보내기로 수집 (Export Collection)](03-techniques/acquisition/export-collection.md)
- [기기에서 AI 흔적 모으기 (Endpoint Triage)](03-techniques/acquisition/endpoint-triage.md)

### 분석

- [AI 사용 타임라인 (Timeline)](03-techniques/analysis/timeline.md)
- [대화 내용 되살리기 (캐시·스냅숏·알림)](03-techniques/analysis/content-recovery.md)
- [메모리에서 AI 흔적 찾기 (Memory Analysis)](03-techniques/analysis/memory-analysis.md)
- [AI가 만든 글·이미지 판별의 한계 (Detection Limits)](03-techniques/analysis/detection-limits.md)
- [프롬프트 인젝션 사고 분석 (Prompt Injection)](03-techniques/analysis/prompt-injection.md)

### 보고

- [AI 관련 포렌식 보고서 (Forensic Report)](03-techniques/reporting/forensic-report.md)

## 조사 시나리오

### 정보 유출

- [기밀 자료를 AI에 넣었나 (Confidential Data Input)](04-scenarios/data-leak/confidential-input.md)
- [회사가 허용하지 않은 AI를 썼나 (Shadow AI)](04-scenarios/data-leak/shadow-ai.md)

### 악용

- [AI로 피싱·사기 문구를 만들었나 (Phishing)](04-scenarios/misuse/phishing.md)
- [AI로 악성 코드를 만들었나 (Malware Development)](04-scenarios/misuse/malware-development.md)
- [딥페이크·합성 이미지를 만들었나 (Deepfake)](04-scenarios/misuse/deepfake.md)

### AI 에이전트

- [AI 에이전트가 무엇을 실행했나 (Agent Actions)](04-scenarios/agents/agent-actions.md)
- [에이전트가 자격 증명을 건드렸나 (Agent Credentials)](04-scenarios/agents/agent-credentials.md)

### 사용자와 출처

- [그 대화를 한 사람이 누구인가 (User Attribution)](04-scenarios/attribution/user-attribution.md)
- [이 글·이미지는 AI가 만들었나 (AI-Generated Content)](04-scenarios/attribution/ai-generated.md)
