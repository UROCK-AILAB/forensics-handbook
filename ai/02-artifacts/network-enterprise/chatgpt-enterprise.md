---
title: "ChatGPT 기업용 감사 기록"
parent: "아티팩트 · 네트워크·기업 기록"
nav_order: 700
---

# ChatGPT 기업용 감사 기록 (Compliance API)

## 한 줄 요약

조직이 ChatGPT Enterprise 로 쓴 대화와 사용 기록은 OpenAI 서버 쪽에 있고 조직 관리자가 관리 기능으로 가져가는 자료라서, 직원 PC 이미지에서는 찾을 수 없고 조직에 요청해야 합니다.

확인 날짜는 2026-09입니다. 이번 확인에서는 OpenAI 의 기업용 Compliance API 도움말과 관리자 API 문서가 접근 거부(403)로 열리지 않았습니다. 그래서 이 페이지에서 확인된 사실은 모두 Microsoft Learn 문서(Purview DSPM for AI 2025-12-15·갱신 2026-06-25, Copilot·AI 앱 보존 2025-09-23·갱신 2026-06-25, Copilot·AI 앱 감사 2026-08-26)에서 나왔고, OpenAI 쪽 세부는 "확인하지 못함" 으로 따로 적습니다.

## 무엇을 기록하나 · 왜 생기나

기업용 ChatGPT 는 조직이 작업 공간 (workspace) 을 만들고 직원이 조직 계정으로 들어와 쓰는 형태입니다. 조직은 규정 준수와 내부 조사를 위해 직원의 대화와 사용 기록을 모아야 할 때가 있습니다. OpenAI 는 이 목적의 기업 고객용 기능을 Compliance API 라는 이름으로 안내하지만 이번에 그 문서를 열지 못했고, Microsoft Purview 같은 조직의 데이터 보호 제품과 연결하는 커넥터 쪽은 Microsoft 문서로 확인했습니다.

OpenAI 문서를 열지 못해서, Compliance API 가 무엇을 돌려주는지(대화·메시지·사용자·GPT·프로젝트·파일·로그 가운데 어디까지인지), 엔드포인트와 이벤트 이름, 칸 이름, 어느 요금제에서 쓸 수 있는지, API 키를 어떻게 발급하는지, 지운 대화가 API 에 얼마나 남는지, 연동 파트너가 누구인지는 이 페이지에 적지 않습니다. 이 항목이 필요하면 조사 시점에 OpenAI 의 기업 고객용 문서를 직접 확인하고, 확인한 날짜와 판을 보고서에 함께 적습니다.

Microsoft 문서로 확인한 사실은 ChatGPT Enterprise 를 Purview 에 연결하는 경로입니다. Purview DSPM for AI 의 권장 사항에 "Discover and govern interactions with ChatGPT Enterprise AI" 가 있고, 조직이 ChatGPT Enterprise 작업 공간을 등록하면 ChatGPT Enterprise 에 공유된 민감 정보를 탐지할 수 있습니다. "Secure interactions from enterprise apps" 권장 사항은 ChatGPT Enterprise 커넥터 (Connector) 로 들어온 프롬프트와 응답을 규정 준수 목적으로 수집합니다. 조직이 이 연결을 해 두었다면, OpenAI 쪽 자료와 별도로 Microsoft 365 테넌트 쪽에도 ChatGPT Enterprise 사용 기록이 생깁니다.

## 위치와 버전별 차이

| 기록 | 위치 | 누가 가져가나 | 확인 상태 |
|---|---|---|---|
| 대화 원본 | OpenAI 서버 | 조직 관리자(Compliance API 등) | 방향만 맞고 세부는 OpenAI 문서로 확인하지 못함 |
| Compliance API 가 돌려주는 기록 | OpenAI 서버 | 조직 관리자 | 확인하지 못함 |
| Purview 로 수집한 프롬프트·응답 | Microsoft 365 테넌트 | Purview 권한이 있는 관리자 | 확인함(조직이 커넥터를 연결한 경우) |
| Purview DSPM 활동 기록 | Microsoft 365 테넌트 | Purview 권한이 있는 관리자 | 확인함(조직이 작업 공간을 등록한 경우) |
| 직원 PC | — | — | Compliance API 기록은 PC 에 없음 |

Purview 안에서 ChatGPT Enterprise 는 따로 분류됩니다. DSPM for AI 활동 탐색기에서는 "Enterprise AI apps" 분류에 들어가고, 보존 정책에서도 "Enterprise AI apps" 위치에 들어갑니다. 개인 계정으로 쓰는 ChatGPT 는 보존 정책의 "Other AI apps" 위치에 따로 있어서, 같은 ChatGPT 라도 조직 계정으로 썼는지 개인 계정으로 썼는지에 따라 보존 정책이 걸리는 위치가 다릅니다. 보존 위치 전체와 숨은 폴더·영구 삭제 흐름은 [Microsoft Purview로 본 Copilot 기록](purview-copilot.md)에서 다룹니다.

직원 PC 쪽에서 볼 수 있는 흔적은 이 페이지가 아니라 앱·브라우저 페이지에 있습니다. 웹·Windows·macOS 앱에 남는 흔적은 [ChatGPT](../chat-services/chatgpt/index.md), 접속 도메인과 네트워크 기록은 [AI 서비스 도메인과 네트워크 기록](network-traces.md)에서 다룹니다. 서버·기기·동기화 사이에서 데이터가 어디에 놓이는지의 일반론은 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

## 구조

Compliance API 의 응답 구조와 칸 이름은 확인하지 못해서 적지 않고, 기억이나 다른 서비스의 칸 이름을 빌려 채우지도 않습니다.

Purview 감사 기록에서 ChatGPT Enterprise 가 어떤 형식으로 남는지도 문서에 직접 나오지 않습니다. Purview 감사는 조직에 등록한 제3자 AI 앱을 `ConnectedAIAppInteraction`, 조직에 배포하지 않은 제3자 AI 앱을 `AIAppInteraction` 으로 기록하는데, ChatGPT Enterprise 가 둘 중 어디로 들어가는지는 확인하지 못했습니다. 조사에서는 내보낸 감사 기록에서 두 RecordType 을 모두 거른 뒤 `AppIdentity` 칸으로 ChatGPT Enterprise 기록을 찾습니다. 두 RecordType 의 뜻, 과금·보관 조건, 칸 목록은 [Microsoft Purview로 본 Copilot 기록](purview-copilot.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 조직이 Purview 에 ChatGPT Enterprise 를 연결해 두었다면, 수집된 프롬프트·응답과 DSPM 활동 기록은 그 조직 계정이 ChatGPT Enterprise 에서 무엇을 주고받았는지와 민감 정보 유형이 걸렸는지를 보여 줍니다. OpenAI 쪽 관리자 자료가 무엇을 담는지는 확인하지 못해서, 실제로 받은 자료의 칸과 기간을 보고 무엇을 증명하는지 판단합니다.

**증명하지 못하는 것.** 조직 계정의 기록이라서 그 시각에 누가 자판 앞에 있었는지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 밝힙니다. 개인 계정 ChatGPT 사용은 Enterprise 관리자 자료에 들어가지 않아서, 관리자 자료에 기록이 없다고 해서 그 직원이 ChatGPT 를 쓰지 않았다고 결론 내리지 않습니다. 개인 계정 사용 여부는 [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md)의 흐름으로 봅니다.

보고서 문장은 "조직이 제공한 ChatGPT Enterprise 관리자 자료에 이 계정이 이 시간대에 대화를 만든 기록이 있다" 처럼 받은 자료가 말하는 범위에서 쓰고, 어느 경로(Compliance API, Purview 수집)로 받은 자료인지 밝힙니다.

## 시각 해석

Compliance API 기록의 시각 칸 이름과 시간대는 확인하지 못했습니다. 자료를 받으면 시각 값에 시간대 표시가 있는지 먼저 확인하고, 같은 대화가 Purview 쪽에도 있다면 두 자료의 시각을 맞춰 보아 기준 시간대를 정합니다. 여러 기록을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **PC 이미지로는 얻을 수 없다.** 관리자 자료는 서버에 있어서 기기 수집 범위 밖이고, 조직의 관리자에게 요청하거나 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)의 절차를 밟아야 합니다.
- **연결하지 않았으면 Purview 에 없다.** Purview 쪽 기록은 조직이 작업 공간을 등록하고 커넥터를 연결했을 때만 생깁니다. 연결하기 전의 사용이 나중에 Purview 로 들어오는지는 확인하지 못해서, 조직에 연결 날짜를 먼저 묻습니다.
- **개인 계정과 조직 계정.** 같은 ChatGPT 라도 계정 종류에 따라 자료가 있는 곳과 보존 정책이 걸리는 위치가 다릅니다. 요청서에 계정 종류를 적습니다.
- **문서가 바뀐다.** 공급사의 관리자 기능은 자주 바뀌고, 이번 확인에서는 OpenAI 문서를 열지 못했습니다. 조사 시점의 문서로 다시 확인합니다.
- **지운 대화.** 사용자가 지운 대화가 관리자 자료에 얼마나 남는지는 확인하지 못했습니다. Purview 로 수집된 사본의 보존·삭제 흐름은 Purview 페이지에서 다룹니다. 보관·삭제의 일반론은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 이 기록은 서버 쪽 자료라서 헥스로 따라갈 파일이 없습니다. 조직에서 받은 자료가 파일로 오면 그 파일이 어떤 형식인지부터 확인하고, 계정 데이터 내보내기 파일과 섞이지 않게 [계정 데이터 내보내기 형식](../../01-foundations/storage-model/data-export-formats.md)의 기준으로 구분합니다.

**공개 도구로 한 번.** Compliance API 응답 형식은 확인하지 못해서 도구 예시를 적지 않습니다. Purview 에서 내보낸 감사 기록은 jq 같은 공개 도구로 `RecordType` 이 `ConnectedAIAppInteraction` 이나 `AIAppInteraction` 인 줄만 거른 뒤 `AppIdentity` 를 모아 봅니다. 거르는 식의 예는 [Microsoft 365 Copilot](../office-integrations/m365-copilot.md) 페이지에 있습니다.

## 교차 검증

- [Microsoft Purview로 본 Copilot 기록](purview-copilot.md) — 조직이 연결해 둔 경우의 감사·보존 기록
- [보안 제품이 남기는 AI 사용 기록](dlp-casb.md) — DLP 가 ChatGPT 로 가는 민감 정보를 막거나 기록했는지
- [AI 서비스 도메인과 네트워크 기록](network-traces.md) — 같은 시간대에 `*.chatgpt.com`·`*.openai.com` 접속이 있었는지
- [ChatGPT](../chat-services/chatgpt/index.md) — 직원 PC·브라우저에 남은 흔적
- [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) — 관리자 자료를 조사 질문에 쓰는 흐름

## 실습

공개 검체(NIST CFReDS 등)에 ChatGPT Enterprise 관리자 자료가 들어 있는지는 확인하지 않았습니다. 시험용 작업 공간과 Purview 테넌트가 있다면 아래 질문을 직접 풀어 봅니다.

1. 작업 공간을 Purview 에 등록하기 전과 뒤에 같은 대화를 하고, DSPM 활동 탐색기에 어느 쪽 대화만 보이는지 확인합니다.
2. 수집된 ChatGPT Enterprise 기록이 감사 기록에서 `ConnectedAIAppInteraction` 과 `AIAppInteraction` 가운데 어느 쪽으로 남는지 확인하고, 그때의 `AppIdentity` 값을 적습니다.
3. 같은 PC 에서 개인 계정 ChatGPT 로 대화하고, 조직 쪽 자료 어디에도 남지 않는지 확인합니다.

## 참고 문헌

1. Learn how Microsoft Purview Data Security Posture Management for AI provides data security and compliance protections (classic) — Microsoft Learn (2025-12-15, 갱신 2026-06-25) — https://learn.microsoft.com/en-us/purview/dspm-for-ai
2. Learn about retention for Copilot and AI apps — Microsoft Learn (2025-09-23, 갱신 2026-06-25) — https://learn.microsoft.com/en-us/purview/retention-policies-copilot
3. Audit logs for Copilot and AI applications — Microsoft Learn (2026-08-26) — https://learn.microsoft.com/en-us/purview/audit-copilot
