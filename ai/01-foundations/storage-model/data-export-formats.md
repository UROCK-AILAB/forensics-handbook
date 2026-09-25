---
title: "계정 데이터 내보내기 형식"
parent: "기반 · 저장 구조"
nav_order: 20
---

# 계정 데이터 내보내기 형식 (Data Export Formats)

> 확인 날짜: 2026-09. 공식 도움말은 2026-09-25 에 열어 읽었고, Claude 내보내기 도움말의 마지막 수정일은 2026-07-08 입니다. ChatGPT 도움말은 이 쪽을 쓰면서 열지 못해서(접근 거부) ChatGPT 내보내기에 관한 내용은 싣지 않았습니다. 내보내기 파일을 직접 받아 열어 보지는 않았습니다.

## 한 줄 요약

계정 데이터 내보내기 (Data Export) 는 서버 계정에 있는 대화를 사용자가 스스로 내려받는 기능이고, 서비스마다 요청하는 곳·전달 방식·받을 수 있는 사람이 달라서 조사에서는 내보내기 파일이 "언제, 누구의 계정에서, 어떤 경로로" 나왔는지를 함께 기록해야 증거로 쓸 수 있습니다.

## 이 형식을 쓰는 아티팩트

대화 원본이 서버 계정에 있는 채팅 서비스([Claude](../../02-artifacts/chat-services/claude/index.md), [Gemini](../../02-artifacts/chat-services/gemini/index.md), [ChatGPT](../../02-artifacts/chat-services/chatgpt/index.md) 등)에서 원본을 얻는 방법은 사용자 쪽 내보내기와 서비스 회사에 대한 [데이터 요청](../../03-techniques/acquisition/legal-requests.md) 두 가지입니다. 원본이 어디에 있는지 가리는 법은 [AI 서비스의 데이터는 어디에 있나](where-data-lives.md) 에서 다루고, 내보내기를 받아 증거로 보존하는 절차는 [계정 데이터 내보내기로 수집](../../03-techniques/acquisition/export-collection.md) 에서 다룹니다. 이 쪽은 서비스별로 무엇이 어떤 모양으로 오는지를 정리합니다.

## 구조

### 서비스별 내보내기 방식

| 서비스 | 요청하는 곳 | 받는 방식 | 담기는 것 | 파일 모양 |
|---|---|---|---|---|
| Claude(개인 계정) | 웹 또는 데스크톱 앱의 이름 머리글자 → Settings → Privacy → "Export data" [1] | 이메일로 온 내려받기 링크, 전달 뒤 24시간에 만료, 받을 때 로그인 필요 [1] | 대화 데이터와 계정의 사용자 데이터 [1] | 확인 못 함 |
| Claude(Team·Enterprise 조직) | 조직의 Primary Owner 만 요청 가능 [1] | 확인 못 함 | 확인 못 함 | 확인 못 함 |
| Gemini 앱 | Google Takeout(takeout.google.com) [2] | 확인 못 함 | 확인 못 함 | 확인 못 함 |
| ChatGPT | 확인 못 함 | 확인 못 함 | 확인 못 함 | 확인 못 함 |

"확인 못 함" 칸이 많은 까닭은 공개 도움말이 내보내기 파일 안의 파일 이름과 형식을 적어 두지 않았거나, 이 쪽을 쓰면서 문서를 열지 못했기 때문입니다. 칸을 기억이나 다른 서비스의 모양으로 채우지 않았습니다.

### Claude

Claude 개인 사용자는 웹이나 Claude 데스크톱에서 설정의 Privacy 화면으로 들어가 "Export data" 를 눌러 요청하고, iOS·Android 앱에서는 내보내기를 할 수 없습니다 [1]. 요청하면 이메일로 내려받기 링크가 오는데, 링크는 전달된 뒤 24시간이 지나면 만료되고 내려받으려면 그 계정으로 로그인해야 합니다 [1]. 내보낸 데이터는 다른 개인 계정으로 가져올 수 없습니다 [1].

Team·Enterprise 조직에서는 조직의 Primary Owner 만 데이터 내보내기를 할 수 있어서 [1], 조직 계정의 대화가 필요한 조사는 조직 관리자와 함께 진행합니다. 조직 쪽 기록은 [Claude 기업용 감사 로그](../../02-artifacts/network-enterprise/claude-enterprise.md) 도 함께 봅니다.

내보내기 ZIP 안의 파일 이름과 형식(JSON 인지, 대화마다 파일이 따로인지)은 도움말에 적혀 있지 않아 확인하지 못했습니다. 검체로 받은 파일에서 직접 목록을 뜨고, 그 목록을 받은 날짜와 함께 적어 둡니다.

### Gemini

Gemini 앱의 데이터는 Google Takeout 으로 내려받습니다 [2]. Takeout 안 Gemini 항목의 파일 형식은 확인하지 못했습니다. Gemini 는 "Keep Activity" 가 켜져 있을 때 대화를 계정의 "Gemini Apps Activity" 에 저장하는데 [2], 활동을 끈 상태의 대화나 임시 대화가 Takeout 에 들어가는지는 확인하지 못했습니다. 활동 설정별 보관 기간은 [대화 기록 보관 설정과 삭제](retention-deletion.md) 에 있습니다.

### ChatGPT

ChatGPT 의 내보내기 절차, 파일 이름, 링크 유효 기간은 도움말 문서를 열지 못해 확인하지 못했습니다. 서비스별 내용은 [ChatGPT](../../02-artifacts/chat-services/chatgpt/index.md) 쪽을 보고, 기업용 계정은 [ChatGPT 기업용 감사 기록](../../02-artifacts/network-enterprise/chatgpt-enterprise.md) 을 봅니다.

### 로컬 도구 — 내보내기 대신 원본 파일

대화 원본을 기기에 두는 도구는 서버 내보내기를 거칠 필요 없이 기기의 파일이 곧 원본입니다. Claude Code 는 세션 기록을 `~/.claude/projects/<프로젝트>/<세션>.jsonl` 에 평문으로 남기고 [3], 이 파일을 사본으로 떠서 보존합니다. 기록 구조는 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) 쪽에서 다룹니다. Ollama 는 모델 파일을 `models` 폴더에 두고 [4], 대화를 내보내는 기능이 있는지는 확인하지 못했습니다.

## 읽는 법

1. 내려받은 ZIP 파일은 열기 전에 해시를 구하고, 받은 날짜·시각과 요청한 계정, 링크를 받은 이메일을 함께 기록합니다.
2. 사본에서 ZIP 안의 파일 목록(이름, 크기, ZIP 안에 적힌 수정 시각)을 먼저 뜹니다. 파일 이름과 구성은 서비스와 시점마다 다를 수 있어서 목록 자체를 증거 기록에 붙입니다.
3. 파일 형식을 확장자가 아니라 내용 앞부분으로 확인합니다. JSON 은 `jq` 같은 도구로 최상위 키 목록부터 뽑고, HTML 은 인터넷에 연결되지 않은 환경에서 엽니다.
4. 대화마다 제목·생성 시각·메시지 수 같은 칸이 있다면 한 표로 모아 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) 에 올리고, 기기 쪽 흔적의 시각과 맞춰 봅니다.

## 포렌식에서 중요한 점

**내보내기는 요청한 시점의 사본입니다.** 내보내기 파일은 요청 시점에 계정에 남아 있던 데이터를 담고, 그 전에 사용자가 지웠거나 보관 기간이 지나 서버에서 사라진 대화가 들어가는지는 이 쪽을 쓰면서 확인하지 못했습니다. 그래서 "내보내기에 없다" 는 사실을 "그런 대화를 한 적이 없다" 로 쓰지 않습니다.

**받는 과정 자체가 계정 접근입니다.** Claude 의 내려받기 링크는 로그인해야 쓸 수 있고 24시간 뒤 만료됩니다 [1]. 조사자가 계정 소유자 대신 받으려면 계정에 접근할 권한과 법적 근거가 먼저 있어야 합니다. 권한이 없으면 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) 으로 방향을 바꿉니다.

**모바일만 쓴 사용자도 있습니다.** Claude 는 iOS·Android 앱에서 내보내기를 할 수 없어서 [1], 모바일만 쓰는 사용자라면 웹이나 데스크톱으로 로그인해 요청해야 합니다. 이때 새로 생기는 로그인 기록이 조사 기간의 기록과 섞이지 않도록 요청한 시각을 따로 적어 둡니다.

## 함정

**다른 서비스의 파일 구성을 옮겨 적지 않습니다.** 이 쪽에서 확인한 공개 문서는 내보내기 ZIP 안의 파일 이름을 적어 두지 않았습니다. 인터넷에서 본 파일 이름이나 예전 버전의 구성을 그대로 적으면 검체와 어긋날 수 있어서, 받은 파일에서 본 것만 씁니다.

**내보내기에 들어가지 않는 기록도 있습니다.** 서비스 회사가 안전 검토나 법적 사유로 따로 보관하는 기록이 사용자 내보내기에 들어가는지는 확인하지 못했고, 보관 정책은 [대화 기록 보관 설정과 삭제](retention-deletion.md) 에 정리합니다.

**내보내기 파일의 시각은 기기 시각과 기준이 다를 수 있습니다.** 파일 안 시각 칸이 UTC 인지 현지 시각인지, 초 단위인지 밀리초 단위인지는 서비스 문서에서 확인하지 못했습니다. 값 몇 개를 기기 쪽 기록과 맞춰 본 뒤 기준을 정하고, 그 근거를 보고서에 적습니다.

## 도구

ZIP 해시는 `certutil -hashfile`(Windows), `shasum -a 256`(macOS), `sha256sum`(Linux) 같은 OS 기본 명령으로 구하고, 파일 목록은 7-Zip 같은 공개 압축 도구의 목록 보기로 뜹니다. JSON 은 `jq`, 표로 모을 때는 스프레드시트나 SQLite 로 옮겨 봅니다.

## 참고 문헌

1. Claude Help Center — How can I export my Claude data? — https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-data
2. Gemini Apps Help — Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961?hl=en
3. Claude Code Docs — .claude 폴더 참조 (claude-directory) — https://code.claude.com/docs/en/claude-directory
4. Ollama — FAQ — https://docs.ollama.com/faq
