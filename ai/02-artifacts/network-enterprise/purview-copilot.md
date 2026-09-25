---
title: "Microsoft Purview로 본 Copilot 기록"
parent: "아티팩트 · 네트워크·기업 기록"
nav_order: 720
---

# Microsoft Purview로 본 Copilot 기록 (Purview)

## 한 줄 요약

Microsoft Purview 에는 Copilot 과 AI 앱 사용이 세 갈래로 남는데, 감사 기록은 누가 어느 앱에서 무엇을 근거로 AI 를 썼는지를, 보존 정책으로 모은 사본은 프롬프트와 응답 본문을, DSPM for AI 활동 탐색기는 민감 정보가 오갔는지를 보여 주고, 모두 Microsoft 365 테넌트 쪽에만 있습니다.

확인 날짜는 2026-09입니다. 근거는 Microsoft Learn 문서 세 편(Copilot·AI 앱 감사 2026-08-26, Copilot·AI 앱 보존 2025-09-23·갱신 2026-06-25, DSPM for AI classic 판 2025-12-15·갱신 2026-06-25)입니다. PC 에 남는 Copilot 앱 흔적은 이번 확인 범위에 들지 않았습니다.

## 무엇을 기록하나 · 왜 생기나

조직은 Copilot 을 쓰게 하면서 규정 준수, 보존, 내부 조사를 위해 사용 기록을 남겨야 하고, Purview 는 이 일을 세 가지 기능으로 나눠 맡습니다.

**감사 (Audit).** Copilot 과 AI 앱에서 사용자가 한 상호작용은 감사 (Standard) 에 자동으로 기록되고, 조직이 감사를 켜 두었다면 따로 설정할 것이 없습니다. Security Copilot, Copilot in Fabric, Copilot Studio 앱, Microsoft Foundry 같은 Microsoft 앱은 감사 (Standard) 에 포함되고, 제3자 AI 앱 기록은 종량제 (pay-as-you-go) 과금을 켜야 생기며 180일 보관합니다. 감사 기록에는 메시지 ID 만 있고 프롬프트·응답 본문은 없습니다.

**보존 (Retention).** 프롬프트·응답 본문은 사용자 Exchange 메일함의 숨은 폴더에 복사되고, 이 폴더는 사용자나 관리자가 직접 열어 보는 곳이 아니라 eDiscovery 로 검색하는 곳입니다. 입력한 텍스트, 미리 채운 프롬프트를 고른 기록, 응답의 텍스트·링크·참조가 들어가고, 응답을 만드는 중이라는 안내 메시지는 저장하지 않습니다. Microsoft 365 Copilot 과 Copilot Studio 가 아닌 앱은 수집 정책에서 "내용 수집" 을 켜야 본문이 들어갑니다.

**DSPM for AI 활동 탐색기.** 조직이 권장 정책을 켜면 AI interaction, Sensitive info types, AI website visit 같은 이벤트가 보이고, 활동 종류·사용자·날짜와 시각·AI 앱 분류·앱·접근한 앱·민감 정보 유형·참조 파일을 보여 줍니다. 프롬프트·응답은 권한이 있을 때 AI interaction 이벤트 안에서 보입니다. Copilot in Fabric 과 Security Copilot 은 정책이 없으면 감사 이벤트만 남고 프롬프트·응답은 모으지 않습니다. 확인한 문서는 "classic" 판이고, 문서는 이 기능이 새 Data Security Posture Management 로 바뀌었다고 적습니다.

Microsoft 365 Copilot 을 업무 앱에서 쓸 때 무엇이 남는지는 [Microsoft 365 Copilot](../office-integrations/m365-copilot.md), 개인 계정으로 쓰는 Copilot 은 [Microsoft Copilot](../chat-services/copilot/index.md)에서 다룹니다. 이 페이지는 Purview 쪽 기록의 칸과 보존 흐름을 다룹니다.

## 위치와 버전별 차이

| 기록 | 위치 | 조회 방법 | 본문 |
|---|---|---|---|
| 감사 기록 | Purview 감사 | Purview 포털 → Audit | 없음(메시지 ID 만) |
| 보존 사본 | 사용자 메일함(`UserMailbox`)의 숨은 폴더 | eDiscovery | 있음 |
| 지운 뒤 대기 중인 사본 | 같은 메일함의 `SubstrateHolds` 숨은 폴더 | eDiscovery | 있음 |
| 퇴사자 사본 | 비활성 메일함 (inactive mailbox) | eDiscovery | 있음 |
| 활동 탐색기 이벤트 | Purview DSPM for AI | Purview 포털 | 권한이 있으면 보임 |

보존 정책을 거는 위치는 세 가지로 나뉩니다. 예전에는 "Teams chats and Copilot interactions" 한 위치에 묶여 있었고 지금은 분리되어서, 옛 정책을 볼 때는 어느 시기의 설정인지 먼저 확인합니다.

| 보존 위치 | 들어가는 앱 |
|---|---|
| Microsoft Copilot experiences | Microsoft 365 Copilot, Security Copilot, Copilot in Fabric, Copilot Studio |
| Enterprise AI apps | Entra 에 등록한 AI 앱, ChatGPT Enterprise, Microsoft Foundry |
| Other AI apps | ChatGPT, Google Gemini, 개인용 Microsoft Copilot, DeepSeek |

ChatGPT Enterprise 를 Purview 에 연결하는 경로는 [ChatGPT 기업용 감사 기록](chatgpt-enterprise.md)에서 다룹니다.

## 구조

### 감사 기록을 가르는 세 칸

| `RecordType` | `Workload` | 대상 |
|---|---|---|
| `CopilotInteraction` | `Copilot` | Microsoft 가 만든 Copilot. Copilot·Cowork 상호작용의 `Operation` 도 `CopilotInteraction` |
| `ConnectedAIAppInteraction` | `ConnectedAIApp` | 조직에 등록한 사용자 정의·제3자 AI 앱 |
| `AIAppInteraction` | `AIApp` | 조직에 배포하지 않은 제3자 AI 앱 |
| `TeamCopilotInteraction` | — | Teams 회의 도우미 (Facilitator). `Operation` 은 `AINotesUpdate`, `LiveNotesUpdate`, `TeamCopilotMsgInteraction` |

관리자 작업은 `UpdateTenantSettings`, `CreatePlugin`, `DeletePlugin`, `EnablePromptBook` 같은 `Operation` 으로 따로 남습니다.

### 주요 칸

| 칸 | 담는 것 |
|---|---|
| `AppHost` | 상호작용이 일어난 앱. 예: `BizChat`, `Bing`, `Office`, `Word`, `Excel`, `PowerPoint`, `Outlook`, `Teams`, `Edge`, `M365App`, `OneNote` |
| `AppIdentity` | `workloadName.appGroup.appName` 꼴. 예: `Copilot.MicrosoftCopilot.BizChat`, `Copilot.Security.SecurityCopilot`, `Copilot.Studio.<AppId>`, `ConnectedAIApp.Entra.<AppId>`, `AIApp.SaaS.<AppName>` |
| `Contexts` | 대화할 때 대상이던 항목의 `ID`·`Type`. `Type` 예: docx, TeamsChat, TeamsMeeting |
| `AccessedResources` | Copilot 이 읽은 파일·메일·메시지. 하위 칸 `ID`, `SiteUrl`, `ListItemUniqueId`, `Type`, `Name`, `SensitivityLabelId`, `Action`(read/create/modify), `PolicyDetails`, `Status`, `XPIADetected` |
| `Messages` | 메시지 `ID`, 프롬프트인지 여부 `IsPrompt`, `JailbreakDetected`, `Size`(지금은 쓰지 않음) |
| `AISystemPlugin` | 쓴 플러그인의 `Name`·`ID`·`Version`. `Id` 가 `BingWebSearch` 면 웹 검색을 썼다는 뜻 |
| `ModelTransparencyDetails` | `ModelProviderName`, `ModelName`, `ModelVersion` |
| `AgentId`, `AgentName`, `AgentVersion` | 에이전트를 거친 경우의 에이전트 정보 |
| `ClientRegion` | 클라이언트 지역 |
| `DLPEvaluationDeferred` | DLP 평가를 미룬 대상을 나타내는 비트 값. 1 Prompt, 2 Response, 4 Grounding, 8 WebGrounding |
| `DLPEvaluationDeferredReason` | 평가를 미룬 이유 |

`ModelTransparencyDetails` 는 앱에 따라 비는 경우가 있습니다. Microsoft 365 Copilot 에서는 `ModelName`·`ModelVersion` 이 없고, 사용자가 모델을 직접 고르면 제공사와 모델 이름이 남을 수 있지만 "Auto" 를 고르면 없을 수 있으며, Cowork 는 제공사 정보를 보여 주지 않습니다.

## 증거로서 의미

**증명하는 것.** 감사 기록은 그 계정이 어느 앱(`AppHost`, `AppIdentity`)에서 AI 와 메시지를 주고받았고, 어떤 문서·회의·채팅(`Contexts`)을 대상으로, 어떤 자원(`AccessedResources`)을 읽었는지를 보여 줍니다. `SensitivityLabelId` 로 민감도 레이블이 붙은 자원이 쓰였는지도 확인할 수 있고, `XPIADetected`·`JailbreakDetected` 처럼 탐지 여부를 담는 칸은 [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md)의 출발점이 됩니다. 보존 사본에는 프롬프트와 응답 본문이 들어 있어서 무엇을 물었고 무엇을 받았는지를 보여 줍니다.

**증명하지 못하는 것.** 감사 기록만으로는 무엇을 입력했는지 알 수 없습니다. 보존 정책이 없던 기간이나 "내용 수집" 을 켜지 않은 앱은 본문이 없고, `ModelTransparencyDetails` 가 비었다고 특정 모델을 쓰지 않았다고 읽지 않습니다. 계정 단위의 기록이라서 그 시각에 누가 자판 앞에 있었는지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 밝힙니다.

보고서 문장은 "이 계정이 이 시간대에 Teams 에서 회의 한 건을 대상으로 Copilot 과 메시지를 주고받은 감사 기록이 있고, 같은 시간대의 보존 사본에 프롬프트 두 건이 있다" 처럼 자료마다 말하는 범위를 나눠 씁니다.

## 시각 해석

확인한 문서에는 감사 기록의 시각 칸 이름과 시간대가 나오지 않아서, 내보낸 파일의 시각 값에 시간대 표시가 붙어 있는지 먼저 확인합니다. 보존 사본은 시각보다 삭제 흐름을 알아야 해석할 수 있습니다. 보존 기간이 끝나거나 사용자가 지우면 사본이 `SubstrateHolds` 숨은 폴더로 옮겨지고, 이 폴더에 최소 1일 머문 뒤 보통 1~7일 주기로 도는 타이머 작업이 영구 삭제합니다. `SubstrateHolds` 에 있는 동안은 eDiscovery 로 찾을 수 있어서, 문서는 "1일 뒤 삭제" 정책도 실제 영구 삭제까지 16일 걸릴 수 있다고 적습니다. 다른 보존 정책, Litigation Hold, delay hold, eDiscovery hold 가 걸려 있으면 영구 삭제가 멈춥니다.

사용자가 앱에서 대화를 지운 시각과 사본이 사라진 시각은 이렇게 어긋날 수 있고, 앱 화면에 보이는지 여부도 보존·삭제 상태를 정확히 반영하지 않습니다. 여러 기록을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **감사가 꺼진 조직, 과금이 꺼진 조직.** 감사를 켜지 않았거나 제3자 AI 앱의 종량제 과금을 켜지 않았다면 해당 기록이 없고, 기록이 없다는 사실이 쓰지 않았다는 뜻은 아닙니다.
- **180일.** 제3자 AI 앱 감사 기록은 180일 보관이라서 사건 날짜가 오래되었다면 보존 사본이나 다른 자료로 옮겨 가야 합니다.
- **`AppIdentity` 로 거르기.** Purview 포털에서는 "Activities – operation names" 로 거르고, `AppIdentity` 로 거르려면 내보낸 뒤 오프라인에서 거릅니다.
- **사용자 삭제와 보존.** 사용자가 지운 대화도 `SubstrateHolds` 에 있는 동안이나 보류가 걸려 있는 동안은 eDiscovery 로 찾을 수 있어서, 앱 화면에서 사라졌다고 조직 쪽 사본도 없다고 보지 않습니다. 보관·삭제의 일반론은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.
- **퇴사자.** 계정을 지우면 보존 대상 메시지는 비활성 메일함에 남습니다. 퇴사자 조사에서는 비활성 메일함을 검색 범위에 넣습니다.
- **PC 이미지로는 얻을 수 없다.** 세 갈래 모두 테넌트 쪽 자료라서 조직의 Purview 관리자에게 요청합니다.

## 직접 분석해 보기

**헥스로 한 번.** 이 기록은 테넌트 쪽 자료라서 헥스로 따라갈 PC 파일이 없습니다. 대신 감사 기록에서 비트 값으로 된 칸을 손으로 한 번 풀어 봅니다. `DLPEvaluationDeferred` 가 아래처럼 나왔다고 해 봅니다. 값은 문서의 비트 뜻으로 **만든 예시**입니다.

| 값(10진) | 2진 | 풀이 |
|---|---|---|
| 5 | 0101 | 1 Prompt + 4 Grounding — 프롬프트와 근거 자료의 DLP 평가를 미룸 |
| 10 | 1010 | 2 Response + 8 WebGrounding — 응답과 웹 근거의 DLP 평가를 미룸 |

미룬 이유는 같은 기록의 `DLPEvaluationDeferredReason` 에서 읽고, DLP 쪽 기록은 [보안 제품이 남기는 AI 사용 기록](dlp-casb.md)과 맞춰 봅니다.

**공개 도구로 한 번.** Purview 포털 → Audit 에서 "Activities – operation names" 로 `CopilotInteraction`·`ConnectedAIAppInteraction`·`AIAppInteraction` 을 골라 검색하고 결과를 내보냅니다. 내보낸 파일은 jq 나 Python 같은 공개 도구로 `AppIdentity` 앞부분(`Copilot.`, `ConnectedAIApp.`, `AIApp.`)별로 개수를 세어 어떤 종류의 AI 를 썼는지 나눕니다. JSON 한 건을 읽는 예는 [Microsoft 365 Copilot](../office-integrations/m365-copilot.md) 페이지에 있습니다. 본문이 필요하면 eDiscovery 에서 대상 사용자 메일함을 검색 범위로 잡고 Copilot 상호작용을 찾습니다.

## 교차 검증

- [Microsoft 365 Copilot](../office-integrations/m365-copilot.md) — 업무 앱에서 쓴 Copilot 의 기록 성격
- [보안 제품이 남기는 AI 사용 기록](dlp-casb.md) — 제3자 AI 사이트 방문과 DLP 기록
- [AI 서비스 도메인과 네트워크 기록](network-traces.md) — 같은 시간대에 PC 에서 `*.copilot.microsoft.com` 접속이 있었는지
- [ChatGPT 기업용 감사 기록](chatgpt-enterprise.md) — ChatGPT Enterprise 연결 기록
- [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) — `AccessedResources`·민감 정보 유형을 조사 질문에 쓰는 흐름

## 실습

공개 검체(NIST CFReDS 등)에 Purview 기록이 들어 있는지는 확인하지 않았습니다. 시험용 테넌트가 있다면 아래 질문을 직접 풀어 봅니다.

1. 보존 정책 없이 Copilot 과 대화한 뒤 지우고, eDiscovery 로 찾을 수 있는지 확인합니다. 보존 정책을 건 뒤 같은 일을 하고 비교합니다.
2. "1일 뒤 삭제" 정책을 걸고 대화가 `SubstrateHolds` 를 거쳐 영구 삭제되기까지 며칠 걸리는지 적습니다.
3. Teams 회의에서 회의 도우미를 쓰고 `TeamCopilotInteraction` 기록의 `Operation` 을 확인합니다.
4. 활동 탐색기의 AI interaction 이벤트와 감사 기록의 `CopilotInteraction` 이 같은 상호작용을 가리키는지 시각과 사용자로 맞춰 봅니다.

## 참고 문헌

1. Audit logs for Copilot and AI applications — Microsoft Learn (2026-08-26) — https://learn.microsoft.com/en-us/purview/audit-copilot
2. Learn about retention for Copilot and AI apps — Microsoft Learn (2025-09-23, 갱신 2026-06-25) — https://learn.microsoft.com/en-us/purview/retention-policies-copilot
3. Learn how Microsoft Purview Data Security Posture Management for AI provides data security and compliance protections (classic) — Microsoft Learn (2025-12-15, 갱신 2026-06-25) — https://learn.microsoft.com/en-us/purview/dspm-for-ai
