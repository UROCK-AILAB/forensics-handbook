---
title: "ChatGPT 기업용 감사 기록"
parent: "아티팩트 · 네트워크·기업 기록"
nav_order: 780
---

# ChatGPT 기업용 감사 기록 (Compliance API)

조직이 ChatGPT Enterprise 로 쓴 대화와 사용 기록은 OpenAI 서버에 있고 조직 관리자가 관리 기능으로 가져가는 자료라서, 직원 PC 이미지가 아니라 조직에 요청해서 받습니다.

조직이 Microsoft Purview 를 쓰면 ChatGPT Enterprise 사용 기록 일부를 Purview 에서도 볼 수 있습니다[1][2][3].

## 무엇을 기록하나 · 왜 생기나

기업용 ChatGPT 는 조직이 작업 공간 (workspace) 을 만들고 직원이 조직 계정으로 들어와 쓰는 형태입니다. 조직은 규정 준수와 내부 조사를 위해 직원의 대화와 사용 기록을 모아야 할 때가 있고, OpenAI 쪽 관리자 기능은 Compliance API 라는 이름으로 불립니다.

작업 공간 기록은 컴플라이언스 로그 플랫폼 (Compliance Logs Platform) 에 쌓이고, 조직 관리자는 Compliance API 로 이 기록을 받습니다. 대상은 Enterprise·Edu 작업 공간이고, 플랫폼은 데이터를 30일 동안 보관합니다[4]. 대화 기록에는 사용자 프롬프트와 에이전트 응답이 들어가고, 연결한 앱 (connected app) 의 호출은 따로 기록됩니다[4]. 지금 라이브러리 (Library) 에 있는 파일은 라이브러리 전용 Compliance API 엔드포인트로 받습니다[4]. 어떤 이벤트를 받을 수 있는지, 필드와 보관 기간, 필요한 권한은 Admin API 참조 문서가 기준이라서[5], 조사할 때 그 문서를 직접 열어 보고 확인한 날짜를 보고서에 함께 적습니다.

작업 공간 기록은 네 종류이고[7], 종류마다 답하는 질문이 다릅니다.

| 로그 | 담는 것 | 답하는 질문 |
|---|---|---|
| 대화·컴플라이언스 로그 (Conversation & Compliance Logs) | 사용자 활동과 콘텐츠. 이벤트가 대화, 올린 파일, GPT, 메모리, 사용자 같은 객체를 가리킴 | 어느 계정이 언제 어떤 작업 공간 이벤트를 남겼나, 그 이벤트가 가리키는 대화·파일은 무엇인가 |
| 감사 로그 (ChatGPT Audit Logs) | 관리 설정과 통제의 변경 | 무엇이 언제 바뀌었고, 누가 어떤 대상을 바꿨나 |
| 인증 로그 (Authentication Logs) | ChatGPT 쪽 로그인 기록 | OpenAI 가 인증 활동을 기록했나, 그 뒤 활동을 좁힐 주체·세션 정보는 무엇인가 |
| Codex 사용 로그 (Codex Usage Logs) | 지원하는 Codex 클라이언트·실행 경로의 사용 기록 | 어느 Codex 사용자·세션·활동이 기록됐나 |

감사 로그는 내부자의 악의적 행동, 권한 변경, 작업 공간 통제를 약하게 하려는 시도를 조사할 때 보고, 인증 로그는 계정 탈취와 수상한 로그인을 조사할 때 먼저 봅니다[7].

ChatGPT Enterprise 는 Microsoft Purview 에 연결할 수 있습니다[1]. Purview DSPM for AI 의 권장 사항에 "Discover and govern interactions with ChatGPT Enterprise AI" 가 있고, 조직이 ChatGPT Enterprise 작업 공간을 등록하면 ChatGPT Enterprise 에 공유된 민감 정보를 탐지할 수 있습니다. "Secure interactions from enterprise apps" 권장 사항은 ChatGPT Enterprise 커넥터 (Connector) 로 들어온 프롬프트와 응답을 규정 준수 목적으로 수집합니다. 조직이 이 연결을 해 두었다면 OpenAI 쪽 자료와 별도로 Microsoft 365 테넌트에도 ChatGPT Enterprise 사용 기록이 생깁니다.

## 위치와 버전별 차이

| 기록 | 위치 | 누가 가져가나 | 확인 방법 |
|---|---|---|---|
| 대화 원본 | OpenAI 서버 | 조직 관리자 | 조직에 요청하고, 받을 수 있는 범위는 Admin API 참조 문서로 확인[5] |
| Compliance API 가 돌려주는 기록 | OpenAI 서버(컴플라이언스 로그 플랫폼) | Compliance API 키가 있는 조직 관리자 | 30일 보관[4]. `event_type` 별로 JSONL 로 받음[5] |
| Purview 로 수집한 프롬프트·응답 | Microsoft 365 테넌트 | Purview 권한이 있는 관리자 | 조직이 커넥터를 연결했는지 먼저 확인[1] |
| Purview DSPM 활동 기록 | Microsoft 365 테넌트 | Purview 권한이 있는 관리자 | 조직이 작업 공간을 등록했는지 먼저 확인[1] |
| 직원 PC | — | — | 관리자 기능의 기록은 서버 쪽 자료라서 PC 수집 범위 밖 |

Purview 는 ChatGPT Enterprise 를 따로 분류합니다. DSPM for AI 활동 탐색기에서는 "Enterprise AI apps" 분류에 들어가고[1], 보존 정책에서도 "Enterprise AI apps" 위치에 들어갑니다[2]. 개인 계정으로 쓰는 ChatGPT 는 보존 정책의 "Other AI apps" 위치에 따로 있어서[2], 같은 ChatGPT 라도 조직 계정으로 썼는지 개인 계정으로 썼는지에 따라 보존 정책이 걸리는 위치가 다릅니다. 보존 위치 전체와 숨은 폴더·영구 삭제 흐름은 [Microsoft Purview로 본 Copilot 기록](purview-copilot.md)에서 다룹니다.

요금제에 따라 받을 수 있는 로그가 다르고, 대상은 Enterprise·Edu 작업 공간입니다[4]. 네 종류 로그는 요금제마다 한꺼번에 받을 수 있거나 없습니다[7].

| 요금제 | 네 종류 로그 | 보관 |
|---|---|---|
| 개인·Business | 받을 수 없음 | — |
| Enterprise·Edu | 받을 수 있음 | 30일 |
| Healthcare | 감사 기능은 문서에 있으나, 컴플라이언스 플랫폼 권한과 받을 수 있는 종류는 테넌트에서 따로 확인 | — |
| FedRAMP | 2026-08-04 기준 로그 엔드포인트를 쓸 수 없음. 예전 사용자·대화 자료는 받을 수 있고, Codex 는 API 키 경로를 따름 | — |

API 플랫폼 (API Platform) 기록은 ChatGPT 요금제와 상관없이 따로 있습니다[7]. 조직이 API 플랫폼도 쓴다면 그쪽 감사 로그·API 호출 기록·에이전트 추적은 [OpenAI API 플랫폼 기록](openai-api-platform.md)에서 다룹니다.

직원 PC 에 남는 흔적은 앱·브라우저 페이지에서 다룹니다. 웹·Windows·macOS 앱의 흔적은 [ChatGPT](../chat-services/chatgpt/index.md), 접속 도메인과 네트워크 기록은 [AI 서비스 도메인과 네트워크 기록](network-traces.md)에 있습니다. 서버·기기·동기화 사이에서 데이터가 어디에 놓이는지의 일반론은 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

## 구조

Compliance API 는 먼저 `https://api.chatgpt.com/v1/compliance/workspaces/{작업 공간 ID}/logs` 에서 로그 목록을 받고, 목록의 `data[].id` 마다 `.../logs/{id}` 로 로그 파일을 내려받습니다[6]. 목록 요청에는 `event_type`·`limit`·`after` 를 넘기고, `after` 는 시간대가 붙은 ISO 8601 시각입니다[5][6]. 목록 응답의 `has_more` 가 `true` 이면 `last_end_time` 을 다음 `after` 로 넘겨 이어 받습니다[6]. OpenAI 문서의 예시에는 `event_type` 값으로 `AUTH_LOG` 가 나옵니다[5]. 첫 인자가 작업 공간 ID 가 아니라 `org-` 로 시작하는 조직 ID 이면, 같은 스크립트가 `/organizations/{조직 ID}/logs` 경로로 조직 단위 로그를 받습니다[6].

다른 `event_type` 값과 로그 한 줄 안의 필드 이름은 Admin API 참조 문서와 받은 자료에서 확인합니다[5]. 다른 서비스의 필드 이름을 빌려 짐작으로 채우지 않습니다.

Purview 감사는 조직에 등록한 제3자 AI 앱을 `ConnectedAIAppInteraction`, 조직에 배포하지 않은 제3자 AI 앱을 `AIAppInteraction` 으로 기록합니다[3]. ChatGPT Enterprise 가 둘 가운데 어느 쪽으로 남는지는 문서에 나오지 않아서, 내보낸 감사 기록에서 두 RecordType 을 모두 거른 뒤 `AppIdentity` 필드로 ChatGPT Enterprise 기록을 찾습니다. 두 RecordType 의 뜻, 과금·보관 조건, 필드 목록은 [Microsoft Purview로 본 Copilot 기록](purview-copilot.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 조직이 Purview 에 ChatGPT Enterprise 를 연결해 두었다면, 수집된 프롬프트·응답과 DSPM 활동 기록으로 그 조직 계정이 ChatGPT Enterprise 에서 무엇을 주고받았는지와 민감 정보 유형이 걸렸는지를 알 수 있습니다. OpenAI 쪽 로그로 알 수 있는 것은 로그마다 다릅니다. 대화·컴플라이언스 로그로 한 계정과 시각을 작업 공간 이벤트에 묶고, 그 이벤트가 가리키는 대화·파일을 찾을 수 있습니다. 감사 로그로는 관리 설정이 언제 바뀌었고 누가 어떤 대상을 바꿨는지 알 수 있고, 인증 로그로는 ChatGPT 쪽에 로그인이 기록됐는지와 그 주체·세션을 알 수 있습니다. Codex 사용 로그로는 어느 Codex 사용자·세션·활동이 기록됐는지 알 수 있습니다[7].

**증명하지 못하는 것.** 파일 다운로드 이벤트로는 파일이 기기까지 내려갔다는 것만 알 수 있고, 그 파일을 열었거나 실행했는지는 기기 쪽 기록으로 확인합니다[7]. 감사 로그에는 모델 요청과 생성된 답, 기기 활동이 없고, 인증 로그에는 SSO·MFA 같은 ID 공급자 (IdP) 의 판단이 들어 있지 않습니다[7]. 그래서 로그인 과정 전체는 조직의 IdP 로그로 되살립니다. 이 기록만으로는 호스팅된 환경의 파일 작업, 셸 명령, 브라우저 조작, 도구 호출, 승인을 하나하나 다 추적할 수 없습니다[4]. 조직 계정의 기록이라서 그 시각에 누가 자판 앞에 있었는지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 밝힙니다. 개인 계정 ChatGPT 는 조직 작업 공간 밖에서 쓰는 것이라서, 관리자 자료에 기록이 없다는 것만으로 그 직원이 ChatGPT 를 쓰지 않았다고 결론 내리지 않습니다. 개인 계정 사용 여부는 [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md)의 흐름으로 봅니다.

보고서 문장은 "조직이 제공한 ChatGPT Enterprise 관리자 자료에 이 계정이 이 시간대에 대화를 만든 기록이 있다" 처럼 받은 자료로 확인되는 범위에서 쓰고, 어느 경로(Compliance API, Purview 수집)로 받은 자료인지 밝힙니다.

### 조사 시작점별로 볼 로그

조사를 시작한 신호에 따라 먼저 볼 ChatGPT 쪽 로그는 아래와 같습니다[7]. API 플랫폼 쪽은 [OpenAI API 플랫폼 기록](openai-api-platform.md)에서 다룹니다.

| 조사 시작점 | 답할 질문 | 볼 로그 |
|---|---|---|
| 계정 탈취 | 공격자가 들어왔나, 들어와서 무엇을 했나 | 인증 로그(로그인 활동), 대화 로그(그 뒤의 사용자 활동) |
| 접근 유지·권한 상승 | 오래 쓸 접근 경로를 만들었거나 권한을 높였나 | 감사 로그(관리·접근 변경) |
| 방어 약화 (Defense Impairment)[8] | 로깅·ID·네트워크 통제를 약하게 했나 | 감사 로그(보안·관리 변경) |
| 데이터 노출 | 어떤 데이터가 OpenAI 로 갔고, 모델이 무엇을 받고 돌려줬나 | 대화 로그(프롬프트와 응답, 남아 있으면 파일·GPT·메모리) |
| 에이전트·Codex 악용 | 에이전트가 무엇을 시도했고, 누가 시작했고, 무엇이 실행됐나 | Codex 사용 로그(받을 수 있는 이벤트·경로·스키마·보관·권한부터 확인), 대화 로그(프롬프트와 응답, 남아 있으면 파일·GPT·메모리) |

## 시각 해석

Compliance API 는 로그 목록을 받을 때 시간대가 붙은 ISO 8601 시각을 `after` 로 받고, 응답의 `last_end_time` 을 다음 요청의 `after` 로 씁니다[5][6]. 로그 한 줄 안의 시각 필드 이름과 시간대는 Admin API 참조 문서와 받은 자료로 확인합니다. 시각 값에 시간대 표시가 있는지 먼저 보고, 같은 대화가 Purview 쪽에도 있다면 두 자료의 시각을 맞춰 보아 기준 시간대를 정합니다. 여러 기록을 시간순으로 합치는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **PC 이미지로는 얻을 수 없다.** 관리자 자료는 서버에 있어서 기기 수집 범위 밖이고, 조직의 관리자에게 요청하거나 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)의 절차를 밟습니다.
- **연결하지 않았으면 Purview 에 없다.** Purview 쪽 기록은 조직이 작업 공간을 등록하고 커넥터를 연결했을 때 생깁니다[1]. 연결하기 전의 사용이 나중에 Purview 로 들어오는지는 문서에 나오지 않으므로, 조직에 연결 날짜를 묻고 받은 자료의 가장 이른 시각과 비교해 봅니다.
- **30일이 지나면 플랫폼에 없다.** 컴플라이언스 로그 플랫폼은 데이터를 30일 동안 보관하고, 더 오래 둬야 하는 조직은 전자증거개시 (eDiscovery)·DLP·SIEM·데이터 레이크로 계속 내보내야 합니다[4]. 플랫폼의 보관 기간이 조직의 보관 정책을 대신하지 않으므로[5], 30일보다 오래된 기간은 조직이 내보내 둔 사본이 있는지부터 묻습니다.
- **로그와 객체는 보관 규칙이 다르다.** 프로젝트 파일, 잠깐 올린 파일, 저장된 메모리, 컴플라이언스 이벤트, 동기화한 앱 데이터는 보관·삭제 규칙이 각각 따로 있습니다[4]. 그래서 파일은 이미 지워졌는데 그 파일을 가리키는 이벤트는 남아 있을 수 있습니다[7]. 이벤트가 가리키는 대화·파일은 찾는 대로 먼저 보존합니다.
- **인증 로그는 API 플랫폼 감사 로그와 필드가 다르다.** API 플랫폼 감사 로그 문서에 나오는 필드가 ChatGPT 인증 로그에도 있다고 가정하지 않습니다[7]. API 플랫폼 감사 로그는 [OpenAI API 플랫폼 기록](openai-api-platform.md)에서 다룹니다.
- **API 키로 쓴 Codex.** API 키로 인증한 Codex 활동은 ChatGPT 작업 공간 기록이 아니라, 연결된 API 조직과 그 데이터 설정을 기준으로 범위를 정합니다[7].
- **개인 계정과 조직 계정.** 같은 ChatGPT 라도 계정 종류에 따라 자료가 있는 곳과 보존 정책이 걸리는 위치가 다릅니다. 요청서에 계정 종류를 적습니다.
- **문서가 바뀐다.** 공급사의 관리자 기능은 자주 바뀌므로 조사 시점의 OpenAI·Microsoft 문서로 다시 확인하고 확인 날짜를 적습니다.
- **지운 대화.** 대화와 파일의 보관 정책은 작업 공간 요금제, 관리자 설정, 쓰는 기능에 따라 정해지므로[4], 지운 대화가 얼마나 남는지는 조직의 보관 설정부터 확인합니다. Purview 로 수집된 사본의 보존·삭제 흐름은 [Microsoft Purview로 본 Copilot 기록](purview-copilot.md)에서 다룹니다. 보관·삭제의 일반론은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 이 기록은 서버 쪽 자료라서 헥스로 따라갈 파일이 없습니다. 조직에서 받은 자료가 파일로 오면 어떤 형식인지부터 확인하고, 계정 데이터 내보내기 파일과 섞이지 않게 [계정 데이터 내보내기 형식](../../01-foundations/storage-model/data-export-formats.md)의 기준으로 구분합니다.

**공개 도구로 한 번.** OpenAI 는 Compliance API 로그를 내려받는 Bash·PowerShell 스크립트를 공개합니다[5]. `event_type` 과 시작 시각을 주면 스크립트가 페이지를 넘겨 가며 로그를 모두 받아 JSONL 로 표준 출력에 씁니다[5][6].

```sh
COMPLIANCE_API_KEY=<KEY> ./download_compliance_files.sh "<workspace_id>" AUTH_LOG 100 "<after>" > output.jsonl
```

받은 JSONL 은 jq 로 한 줄씩 읽고, 필드 이름은 Admin API 참조 문서와 맞춰 봅니다. Purview 에서 내보낸 감사 기록은 jq 같은 공개 도구로 `RecordType` 이 `ConnectedAIAppInteraction` 이나 `AIAppInteraction` 인 줄만 거른 뒤 `AppIdentity` 를 모아 봅니다. 거르는 식의 예는 [Microsoft 365 Copilot](../office-integrations/m365-copilot.md) 페이지에 있습니다.

## 교차 검증

- [Microsoft Purview로 본 Copilot 기록](purview-copilot.md) — 조직이 연결해 둔 경우의 감사·보존 기록
- [보안 제품이 남기는 AI 사용 기록](dlp-casb.md) — DLP 가 ChatGPT 로 가는 민감 정보를 막거나 기록했는지
- [AI 서비스 도메인과 네트워크 기록](network-traces.md) — 같은 시간대에 `*.chatgpt.com`·`*.openai.com` 접속이 있었는지
- [ChatGPT](../chat-services/chatgpt/index.md) — 직원 PC·브라우저에 남은 흔적
- [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) — 관리자 자료를 조사 질문에 쓰는 흐름
- [OpenAI API 플랫폼 기록](openai-api-platform.md) — 같은 조직이 API 플랫폼도 쓰면 그쪽 감사 로그·API 호출 기록·에이전트 추적
- 조직의 IdP 로그 — 인증 로그에 없는 SSO·MFA 판단[7]
- 개발자 PC·저장소·빌드 파이프라인 기록 — Codex 사용 로그에 남은 활동이 실제 코드 변경·명령 실행으로 이어졌는지[7]

## 실습

이 기록은 서버 쪽 자료라서 기기 이미지로 된 공개 시험 데이터로는 풀기 어렵습니다. 시험용 작업 공간과 Purview 테넌트가 있다면 아래 질문을 직접 풀어 봅니다.

1. 작업 공간을 Purview 에 등록하기 전과 뒤에 같은 대화를 하고, DSPM 활동 탐색기에 어느 쪽 대화만 보이는지 확인합니다.
2. 수집된 ChatGPT Enterprise 기록이 감사 기록에서 `ConnectedAIAppInteraction` 과 `AIAppInteraction` 가운데 어느 쪽으로 남는지 확인하고, 그때의 `AppIdentity` 값을 적습니다.
3. 같은 PC 에서 개인 계정 ChatGPT 로 대화하고, 조직 쪽 자료 어디에도 남지 않는지 확인합니다.
4. 시험용 Enterprise 작업 공간에서 파일을 올린 뒤 지우고, 그 파일을 가리키는 이벤트가 Compliance API 로그에 남는지 확인합니다.
5. 같은 계정으로 로그인한 직후 `AUTH_LOG` 로그를 받고, 로그인 시각이 IdP 로그의 시각과 몇 초 차이 나는지 비교합니다.

## 참고 문헌

1. Learn how Microsoft Purview Data Security Posture Management for AI provides data security and compliance protections (classic) — Microsoft Learn (2025-12-15, 갱신 2026-06-25) — https://learn.microsoft.com/en-us/purview/dspm-for-ai
2. Learn about retention for Copilot and AI apps — Microsoft Learn (2025-09-23, 갱신 2026-06-25) — https://learn.microsoft.com/en-us/purview/retention-policies-copilot
3. Audit logs for Copilot and AI applications — Microsoft Learn (2026-08-26) — https://learn.microsoft.com/en-us/purview/audit-copilot
4. ChatGPT Work admin FAQ — OpenAI — https://learn.chatgpt.com/docs/enterprise/work-admin-faq
5. Compliance API and audit events — OpenAI — https://learn.chatgpt.com/docs/enterprise/compliance-api
6. download_compliance_files.sh (Compliance API 로그 내려받기 스크립트) — OpenAI — https://learn.chatgpt.com/downloads/compliance-api/download_compliance_files.sh
7. Invictus Incident Response, Frontier Forensics: OpenAI, Version 1.0 (2026-08) — https://www.invictus-ir.com/
8. Defense Impairment, Tactic TA0112 — MITRE ATT&CK (v19, 생성 2026-04-14) — https://attack.mitre.org/tactics/TA0112/
