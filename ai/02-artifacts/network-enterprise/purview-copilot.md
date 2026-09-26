---
title: "Microsoft Purview로 본 Copilot 기록"
parent: "아티팩트 · 네트워크·기업 기록"
nav_order: 800
---

# Microsoft Purview로 본 Copilot 기록 (Purview)

## 한 줄 요약

Microsoft Purview 에는 Copilot 과 AI 앱 사용이 세 가지로 남습니다. 감사 기록은 누가 어느 앱에서 무엇을 근거로 AI 를 썼는지를, 보존 정책으로 사용자 메일함에 모인 사본은 프롬프트와 응답 본문을, DSPM for AI 활동 탐색기는 민감 정보가 오갔는지를 보여 주고, 셋 다 Microsoft 365 테넌트 쪽에만 있습니다.

확인 날짜는 2026-09입니다. PC 에 남는 Copilot 앱 흔적은 [Microsoft Copilot](../chat-services/copilot/index.md), 업무 앱에서 쓴 Copilot 의 기록 성격과 감사 레코드 한 건을 읽는 예시는 [Microsoft 365 Copilot](../office-integrations/m365-copilot.md)에서 다룹니다. 이 페이지는 Purview 쪽 기록의 필드, 보관 기간, 삭제 흐름을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

조직은 Copilot 을 쓰게 하면서 규정 준수, 보존, 내부 조사를 위해 사용 기록을 남겨야 하고, Purview 는 이 일을 세 기능으로 나눠 맡습니다.

**감사 (Audit).** Copilot 과 AI 앱에서 사용자가 한 상호작용은 감사 (Standard) 에 자동으로 기록되고, 조직이 감사를 켜 두었다면 따로 설정할 것이 없습니다[1]. Security Copilot, Copilot in Fabric, Copilot Studio 와 Microsoft Foundry 로 만든 앱처럼 Microsoft 쪽 앱은 모두 감사 (Standard) 에 들어갑니다. 조직 밖 제3자 AI 앱의 기록(`AIAppInteraction`)과 `ConnectedAIAppInteraction` 의 일부는 종량제 (pay-as-you-go) 과금을 켜야 생기고, 180일 보관합니다[1]. 관리자가 Copilot 설정·플러그인·프롬프트북·작업 공간을 바꾼 일도 감사 기록으로 남습니다. 감사 레코드의 `Messages` 필드에는 메시지 ID 와 프롬프트 여부만 들어가고, 스키마에 프롬프트·응답 본문을 담는 필드는 없습니다[5].

**보존 (Retention).** 보존 정책을 걸면 프롬프트와 응답에서 복사한 데이터가 AI 앱을 쓴 사용자의 Exchange 메일함 안 숨은 폴더에 저장됩니다[2]. 이 폴더는 사용자나 관리자가 직접 여는 곳이 아니고, 준수 관리자가 eDiscovery 로 검색하는 곳입니다. 입력한 텍스트, 미리 채운 프롬프트를 고른 기록, 응답의 텍스트·링크·참조가 들어가고, Teams 채팅·채널의 Copilot 은 스레드 요약도 들어갑니다. 응답을 만드는 중이라는 안내 메시지는 저장하지 않습니다. Microsoft 365 Copilot 과 Copilot Studio 가 아닌 앱은 수집 정책 (collection policy) 에서 내용 수집을 켜 두어야 본문이 들어갑니다[2].

**DSPM for AI 활동 탐색기.** 조직이 권장 정책을 켜면 활동 탐색기에 AI interaction, Sensitive info types, AI website visit 같은 이벤트가 보입니다[3]. 이벤트마다 활동 종류와 사용자, 날짜와 시각, AI 앱 분류와 앱, 접근한 앱, 민감 정보 유형, 참조한 파일과 참조한 민감 파일을 보여 줍니다. 프롬프트와 응답은 권한이 있을 때 AI interaction 이벤트 안에서 보이고, Web queries 필터로 웹 검색을 쓴 상호작용을 고르면 그 검색어가 상세 창에 나옵니다. Copilot in Fabric 과 Security Copilot 은 권장 정책과 비슷한 정책이 없으면 감사 이벤트만 남고 프롬프트·응답은 모으지 않습니다. 이 기능은 새 Data Security Posture Management 로 바뀌었고, 위 설명은 바뀌기 전 "classic" 판 기준입니다[3].

## 위치와 버전별 차이

| 기록 | 위치 | 조회 방법 | 본문 |
|---|---|---|---|
| 감사 기록 | Purview 감사 | Purview 포털 → Audit | 없음(메시지 ID 만) |
| 보존 사본 | 사용자 메일함(RecipientTypeDetails `UserMailbox`)의 숨은 폴더 | eDiscovery | 있음 |
| 지웠거나 기간이 끝난 사본 | 같은 메일함의 숨은 폴더 `SubstrateHolds` | eDiscovery | 있음(영구 삭제 전까지) |
| 퇴사자 사본 | 비활성 메일함 (inactive mailbox) | eDiscovery | 있음 |
| Copilot 메모리 | 사용자 메일함, item class `IPM.Contact` | eDiscovery(연락처로 걸림) | 있음 |
| 활동 탐색기 이벤트 | Purview DSPM for AI | Purview 포털 | 권한이 있으면 보임 |

보존 사본이 들어가는 숨은 폴더의 이름은 공개되어 있지 않습니다[2]. 메일함 안에서는 item class 로 앱을 구분합니다[4]. 앱 종류별 앞부분은 아래와 같고, Word·Excel·Teams 같은 앱마다의 item class 는 [Microsoft 365 Copilot](../office-integrations/m365-copilot.md)에서 다룹니다.

| 대상 | item class |
|---|---|
| Microsoft 365 Copilot 전체 | `IPM.SkypeTeams.Message.Copilot.*` |
| Copilot Studio | `IPM.SkypeTeams.Message.Copilot.Studio.*` |
| Copilot in Fabric | `IPM.SkypeTeams.Message.Copilot.Fabric.*` |
| Security Copilot | `IPM.SkypeTeams.Message.Copilot.Security.SecurityCopilot` |
| Entra 에 등록한 앱 | `IPM.SkypeTeams.Message.ConnectedAIApp.Entra.<AppID>` |
| Microsoft Foundry | `IPM.SkypeTeams.Message.ConnectedAIApp.AzureAI.<AzureResourceName>` |
| ChatGPT Enterprise, 로컬 기기에서 쓴 경우 | `IPM.SkypeTeams.Message.ConnectedAIApp.Connector.<ChatGPTEnterprise>` |
| 기타 AI 앱, 로컬 기기에서 쓴 경우 | `IPM.SkypeTeams.Message.ConnectedAIApp.Connector.<AppName>` |
| ChatGPT Enterprise·기타 AI 앱, 브라우저에서 쓴 경우 | `IPM.SkypeTeams.Message.CloudAIApp.SaaS.<AppID>` |
| 회의 도우미 (Facilitator) AI 노트 | `IPM.SkypeTeams.Message.TeamCopilot.AiNotes.Teams` |
| Copilot 메모리 | `IPM.Contact` |

보존 정책을 거는 위치는 예전에는 "Teams chats and Copilot interactions" 한 곳에 묶여 있었고, 지금은 아래 세 곳으로 나뉩니다[2]. 옛 정책을 볼 때는 어느 시기의 설정인지 먼저 확인합니다. 옛 위치에 건 정책은 DSPM for AI 의 정책 화면에 나오지 않습니다[3].

| 보존 위치 | 들어가는 앱 |
|---|---|
| Microsoft Copilot experiences | Microsoft 365 Copilot, Security Copilot, Copilot in Fabric, Copilot Studio |
| Enterprise AI apps | Entra 에 등록한 AI 앱, ChatGPT Enterprise, Microsoft Foundry |
| Other AI apps | ChatGPT, Google Gemini, 개인용 Microsoft Copilot, DeepSeek |

ChatGPT Enterprise 를 Purview 에 연결하는 경로는 [ChatGPT 기업용 감사 기록](chatgpt-enterprise.md)에서 다룹니다.

## 구조

### 감사 기록을 구분하는 필드

`RecordType` 은 포털 화면에서는 이름으로, 레코드 JSON 에서는 `"RecordType":261` 처럼 숫자로 나옵니다[5]. 이름과 숫자의 짝은 Management Activity API 의 AuditLogRecordType 값과 같습니다[6].

| `RecordType` 이름 | 숫자 | `Workload` | 대상 |
|---|---|---|---|
| `CopilotInteraction` | 261 | `Copilot` | Microsoft 가 만든 Copilot(Microsoft 365 Copilot, Cowork, Security Copilot 등) |
| `AIAppInteraction` | 284 | `AIApp` | 조직에 배포하지 않은 제3자 AI 앱 |
| `ConnectedAIAppInteraction` | 328 | `ConnectedAIApp` | 조직 테넌트에 배포·등록한 AI 앱 |
| `TeamCopilotInteraction` | 334 | 공개 자료 없음 | Teams 회의 도우미. `Operation` 은 `AINotesUpdate`, `LiveNotesUpdate`, `TeamCopilotMsgInteraction` |

`ConnectedAIAppInteraction` 은 "조직에 등록한 사용자 정의 Copilot 이나 제3자 AI 앱" 의 기록이지만, Copilot Studio 로 만든 앱은 `RecordType` `CopilotInteraction`, `AppIdentity` `Copilot.Studio.<appId>` 로 남습니다[1]. 조직이 만든 앱이라고 `ConnectedAIAppInteraction` 만 찾으면 Copilot Studio 앱을 빠뜨리므로, 두 값을 함께 검색합니다. 회의 도우미 레코드의 `AppIdentity` 는 `Copilot.TeamCopilot.AINotes`, `Copilot.TeamCopilot.LiveNotes`, `Copilot.TeamCopilot.MeetingModerator`, `Copilot.TeamCopilot.Message` 입니다[1]. 관리자 작업은 `UpdateTenantSettings`, `CreatePlugin`, `DeletePlugin`, `EnablePromptBook` 같은 `Operation` 으로 따로 남습니다.

### 레코드의 짜임

Copilot 감사 레코드는 두 층입니다[5]. 모든 감사 레코드에 공통인 필드가 바깥에 있고, Copilot 에만 있는 필드는 `CopilotEventData` 객체 안에 들어 있습니다. jq 로 거를 때 이 층을 빼먹으면 아무것도 걸리지 않습니다.

| 층 | 필드 |
|---|---|
| 바깥(공통 스키마) | `CreationTime`, `Id`, `Operation`, `OrganizationId`, `RecordType`, `UserKey`, `UserType`, `Version`, `Workload`, `ClientIP`, `UserId` |
| 바깥(Copilot 전용) | `ClientRegion`, `CopilotLogVersion` |
| `CopilotEventData` 안 | `AppHost`, `Contexts`, `ThreadId`, `MessageIds`, `Messages`, `AccessedResources`, `ModelTransparencyDetails`, `AISystemPlugin` |

이 밖에 `AppIdentity`, `AgentId`·`AgentName`·`AgentVersion`, `CapacityId`, `DLPEvaluationDeferred`·`DLPEvaluationDeferredReason` 필드도 있지만[1], 이 필드들이 어느 층에 들어가는지는 공개되어 있지 않습니다[5]. 내보낸 레코드에서 필드의 실제 위치를 먼저 확인합니다(아래 "직접 분석해 보기").

JSON 키는 대소문자를 구분하고, 문서마다 표기가 다릅니다. 감사 문서의 설명은 `ID`·`IsPrompt` 로 쓰지만, 스키마 정의와 두 문서의 예시 레코드는 `Id`·`isPrompt` 이고 `AccessedResources` 의 예시 키는 `listItemUniqueId` 입니다[1][5]. 필터를 쓰기 전에 내보낸 파일에서 키 표기를 확인합니다.

### 필드의 뜻

| 필드 | 담는 것 |
|---|---|
| `AppHost` | 상호작용이 일어난 앱. 예: `BizChat`(Copilot Chat 클라이언트, microsoft365.com/copilot·/chat), `Bing`(Edge 사이드바, Windows Copilot, copilot.cloud.microsoft.com), `Office`(office.com·microsoft365.com), `Word`, `WordOnCanvas`, `OutlookSidepane`, `Teams`, `M365App`, `OfficeCopilotNotebook`, `OfficeCopilotSearchAnswer` |
| `AppIdentity` | `workloadName.appGroup.appName` 형식. 예: `Copilot.MicrosoftCopilot.BizChat`, `Copilot.Security.SecurityCopilot`, `Copilot.Studio.<AppId>`, `ConnectedAIApp.Entra.<AppId>`, `ConnectedAIApp.AzureAI.<AzureResourceName>`, `AIApp.SaaS.<AppName>` |
| `Contexts` | 대화할 때 대상이던 항목의 `Id`·`Type`. `Type` 예: docx, pptx, xlsx, TeamsMeeting, TeamsChannel, TeamsChat |
| `ThreadId` | Copilot 과 사용자의 대화 스레드 ID. 예시 값은 `19:` 로 시작해 `@thread.v2` 로 끝나고, 같은 스레드의 레코드를 모을 때 씁니다 |
| `MessageIds` | Microsoft 내부용으로 예약된 필드 |
| `Messages` | 메시지 `Id` 와 프롬프트 여부 `isPrompt`, `JailbreakDetected`, `Size`(지금은 쓰지 않음). 레코드 하나에 보통 프롬프트·응답 한 쌍이 들어가고, 프롬프트 하나에 응답이 여럿 붙기도 합니다 |
| `AccessedResources` | Copilot 이 읽은 파일·메일·메시지. 하위 필드 `Id`, `SiteUrl`, `listItemUniqueId`, `Type`, `Name`, `SensitivityLabelId`, `Action`(read/create/modify), `PolicyDetails`, `Status`, `XPIADetected` |
| `AISystemPlugin` | 쓴 플러그인의 `Name`·`Id`·`Version`. `Id` 가 `BingWebSearch` 면 Bing 으로 공개 웹을 썼다는 뜻 |
| `ModelTransparencyDetails` | `ModelProviderName`, `ModelName`, `ModelVersion` |
| `AgentId`, `AgentName`, `AgentVersion` | 에이전트를 거친 경우의 에이전트 정보. `AgentId` 예: `CopilotStudio.Declarative.` 뒤에 GUID |
| `ClientRegion`, `ClientIP` | 작업할 때의 사용자 지역, 기기 IP 주소 |
| `DLPEvaluationDeferred` | DLP 평가를 미룬 단계를 비트로 더한 값. 1 Prompt, 2 Response, 4 Grounding, 8 WebGrounding |
| `DLPEvaluationDeferredReason` | 평가를 미룬 이유. `DLPEvaluationDeferred` 가 0 이 아닐 때만 채워집니다. 예: Timeout, Authentication Error, Service Unavailable |
| `CapacityId` | Microsoft Fabric 용량 ID |

`ClientIP` 에는 서비스에 따라 사용자 기기가 아니라 대신 호출한 앱의 IP 가 들어갈 수 있습니다[6].

`ModelTransparencyDetails` 는 시기에 따라 다릅니다. Microsoft 365 Copilot 에서는 `ModelName`·`ModelVersion` 이 없고, 사용자가 모델을 직접 고르면 제공사와 모델 이름이 남지만 Auto 를 고르면 빠질 수 있으며 Cowork 는 제공사 정보를 보여 주지 않습니다[1]. 반면 2023-12 예시 레코드에는 `ModelName` 값이 들어 있습니다[5]. 레코드가 생긴 시기에 따라 필드가 다를 수 있으니, 비교할 때는 같은 시기의 레코드끼리 봅니다.

## 증거로서 의미

**증명하는 것.** 감사 기록은 그 계정이 어느 앱(`AppHost`, `AppIdentity`)에서 AI 와 메시지를 주고받았고, 어떤 문서·회의·채팅(`Contexts`)을 대상으로, 어떤 자원(`AccessedResources`)을 읽었는지를 보여 줍니다. `SensitivityLabelId` 로 민감도 레이블이 붙은 자원이 쓰였는지도 확인할 수 있고, `XPIADetected`·`JailbreakDetected` 처럼 탐지 여부를 담는 필드는 [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md)의 출발점이 됩니다. `ThreadId` 가 같은 레코드를 모으면 한 대화에서 몇 번 주고받았는지 셀 수 있습니다. 보존 사본에는 프롬프트와 응답 본문이 들어 있어서 무엇을 물었고 무엇을 받았는지를 보여 줍니다.

**증명하지 못하는 것.** 감사 기록만으로는 무엇을 입력했는지 알 수 없습니다. 보존 정책이 없던 기간이나 내용 수집을 켜지 않은 앱은 본문이 없고, `ModelTransparencyDetails` 가 비었다고 특정 모델을 쓰지 않았다고 읽지 않습니다. 계정 단위의 기록이라서 그 시각에 누가 자판 앞에 있었는지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 밝힙니다.

보고서 문장은 "이 계정이 이 시간대에 Teams 에서 회의 한 건을 대상으로 Copilot 과 메시지를 주고받은 감사 기록이 있고, 같은 시간대의 보존 사본에 프롬프트 두 건이 있다" 처럼 자료마다 확인되는 범위를 나눠 씁니다.

## 시각 해석

**감사 기록의 시각.** 공통 스키마의 `CreationTime` 은 레코드가 생긴 시각이고 UTC 입니다[6]. 값은 `"CreationTime":"2023-12-13T17:12:36"` 처럼 시간대 표시(Z)가 붙지 않지만, 표시가 없다고 현지 시각으로 읽으면 안 됩니다[5]. 포털 결과 쪽 `CreationDate` 는 `12/13/2023 17:12` 형식이고 초가 없습니다. 내보낸 파일에서 두 값을 나란히 놓고 시각이 같은지 한 번 확인한 뒤 타임라인에 올립니다.

**감사 기록의 보관 기간.** 감사 (Standard) 의 기본 보관은 180일이고, 2023-10-17 이전에 생긴 레코드는 90일입니다[7]. Audit (Premium) 의 기본 1년 정책은 `Workload` 가 `AzureActiveDirectory`, `Exchange`, `OneDrive`, `SharePoint` 인 레코드에만 걸리므로, `Workload` 가 `Copilot` 인 레코드는 E5 조직이라도 사용자 지정 정책이 없으면 180일 보관입니다. 180일을 넘겨 1년까지 두려면 레코드를 만든 사용자에게 E5 계열 라이선스가 있어야 하고, 10년은 추가 라이선스가 있어야 합니다. 보관 기간은 레코드가 감사 파이프라인에 들어올 때 정해지고, 나중에 라이선스나 정책을 바꿔도 이미 들어온 레코드에는 적용되지 않습니다[7]. 사건 날짜가 오래되었다면 그 시기에 어떤 감사 보존 정책이 있었는지부터 확인합니다.

**보존 사본의 삭제 흐름.** Exchange 의 타이머 작업이 숨은 폴더를 주기적으로 검사하고, 한 번 도는 데 보통 1~7일 걸립니다[2]. 기간이 끝났거나 지운 항목은 `SubstrateHolds` 로 가서 최소 1일 머문 뒤, 삭제 대상이면 다음 타이머 작업 때 영구 삭제됩니다. 정책 종류별 흐름은 아래와 같습니다[2].

| 정책 | 사용자가 앱에서 지운 경우 | 앱에 남아 있는 경우 |
|---|---|---|
| 보존 후 삭제 | 바로 `SubstrateHolds` 로 옮겨지고, 보존 기간이 끝난 뒤 다음 타이머 작업 때 영구 삭제 | 기간이 끝나고 보통 1~7일 안에 `SubstrateHolds` 로 복사, 최소 1일 뒤 다음 타이머 작업 때 영구 삭제 |
| 보존만 | 기간이 끝나고 보통 1~7일 안에 `SubstrateHolds` 로 옮겨짐. 영구 보존이면 그대로 남고, 끝나는 날이 있으면 그 뒤 영구 삭제 | 원래 자리에 그대로 남음 |
| 삭제만 | `SubstrateHolds` 로 옮겨져 최소 1일 뒤 다음 타이머 작업 때 영구 삭제 | 기간이 끝나고 보통 1~7일 안에 복사, 최소 1일 뒤 영구 삭제 |

예를 들어 "30일 보존 후 삭제" 정책에서 10일째 지운 프롬프트는 30일이 지난 뒤에야 영구 삭제되고, 그 전까지 eDiscovery 로 찾을 수 있습니다. "1일 뒤 삭제" 정책도 복사와 삭제를 거치느라 영구 삭제까지 16일 걸릴 수 있습니다[2]. 같은 위치의 다른 보존 정책, Litigation Hold, delay hold, eDiscovery hold 가 걸려 있으면 `SubstrateHolds` 에서의 영구 삭제가 멈춥니다.

앱 화면도 이 흐름과 어긋납니다. 채팅 창이나 앱을 닫으면 메시지는 숨겨질 뿐 남아 있고, Microsoft 365 Copilot 메시지가 실제로 지워지는 것은 사용자가 Copilot Chat 에서 대화를 지우거나 전체 기록 삭제를 요청한 경우입니다[2]. 반대로 보존 기간이 끝난 메시지도 삭제 신호가 앱까지 전달되는 사이 잠시 화면에 보일 수 있습니다. 앱에 보이는지 여부는 보존·영구 삭제 상태를 정확히 반영하지 않습니다[2]. 여러 기록을 시간순으로 합치는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **감사가 꺼진 조직, 과금이 꺼진 조직.** 감사를 켜지 않았거나 제3자 AI 앱의 종량제 과금을 켜지 않았다면 해당 기록이 없고, 기록이 없다는 사실이 쓰지 않았다는 뜻은 아닙니다.
- **180일.** Copilot 감사 기록도, 종량제 제3자 AI 앱 기록도 기본 180일이라서, 사건 날짜가 오래되었다면 보존 사본이나 다른 자료로 옮겨 가야 합니다.
- **`RecordType` 이 숫자로 나온다.** 내보낸 JSON 에서는 `RecordType` 이 이름이 아니라 261 같은 숫자라서, 이름으로 거르면 걸리지 않습니다.
- **`AppIdentity` 로 거르기.** Purview 포털에서는 "Activities – operation names" 로 `Operation`·`RecordType`·`Workload` 를 거르거나, "Copilot activities" 의 "Interacted with Copilot" 을 고르거나, `Workload` 를 `Copilot` 으로 고릅니다[1][5]. `AppIdentity` 로 거르려면 내보낸 뒤 오프라인에서 거릅니다.
- **사용자 삭제와 보존.** 사용자가 지운 대화도 `SubstrateHolds` 에 있는 동안이나 보류가 걸려 있는 동안은 eDiscovery 로 찾을 수 있어서, 앱 화면에서 사라졌다고 조직 쪽 사본도 없다고 보지 않습니다. 보관·삭제의 일반론은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.
- **관리자 삭제.** eDiscovery 검색 결과를 Microsoft Graph 의 `purgeData` 로 지울 수 있고, 한 번에 메일함당 10건까지이며 사용자에게는 알림이 가지 않습니다[4]. 지우기 전에 메일함의 보류와 보존 정책을 먼저 풀어야 하고, 지운 항목도 `SubstrateHolds` 에 최소 1일 머뭅니다. 보존 사본이 비어 있다면 그 메일함의 보류·보존 정책이 풀렸던 기간이 있었는지 확인합니다.
- **메모리는 따로 남는다.** Copilot 메모리는 `IPM.Contact` 로 저장되고, Purview 나 eDiscovery 에서 대화·메시지를 지워도 연결된 메모리는 지워지지 않습니다[4].
- **퇴사자.** 계정을 지우면 보존 대상 메시지는 비활성 메일함에 남고, 비활성 메일함이 되기 전에 걸려 있던 보존 정책을 그대로 따릅니다[2]. 퇴사자 조사에서는 비활성 메일함을 검색 범위에 넣습니다.
- **PC 이미지로는 얻을 수 없다.** 세 가지 모두 테넌트 쪽 자료라서 조직의 Purview 관리자에게 요청합니다. 조직 밖 자료가 필요하면 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)을 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** 이 기록은 테넌트 쪽 자료라서 헥스로 따라갈 PC 파일이 없습니다. 대신 감사 기록에서 비트 값으로 된 필드를 손으로 한 번 풀어 봅니다. `DLPEvaluationDeferred` 가 아래처럼 나왔다고 해 봅니다. 값은 문서의 비트 뜻으로 **만든 예시**입니다.

| 값(10진) | 2진 | 풀이 |
|---|---|---|
| 5 | 0101 | 1 Prompt + 4 Grounding — 프롬프트와 근거 자료의 DLP 평가를 미룸 |
| 10 | 1010 | 2 Response + 8 WebGrounding — 응답과 웹 근거의 DLP 평가를 미룸 |

미룬 이유는 같은 기록의 `DLPEvaluationDeferredReason` 에서 읽고, DLP 쪽 기록은 [보안 제품이 남기는 AI 사용 기록](dlp-casb.md)과 맞춰 봅니다.

**공개 도구로 한 번.** Purview 포털 → Audit 에서 `CopilotInteraction`·`ConnectedAIAppInteraction`·`AIAppInteraction` 을 골라 검색하고 결과를 내보냅니다. 포털에서 내보낸 CSV 라면 레코드 JSON 이 AuditData 열에 문자열로 들어 있으니 먼저 한 줄에 레코드 하나씩 JSON 으로 풀어 둡니다. 그다음 jq 로 필드의 실제 위치부터 확인합니다.

```sh
# 레코드에 들어 있는 칸의 경로를 모두 뽑는다
jq -r '[paths | map(tostring) | join(".")] | .[]' records.jsonl | sort -u

# 웹 검색을 쓴 상호작용의 앱만 뽑는다(CopilotEventData 안쪽 경로)
jq -r 'select(any(.CopilotEventData.AISystemPlugin[]?; .Id == "BingWebSearch"))
       | .CopilotEventData.AppHost' records.jsonl | sort | uniq -c

# 대화(ThreadId)별로 시각(UTC)을 늘어놓는다
jq -r '[.CopilotEventData.ThreadId, .CreationTime] | @tsv' records.jsonl | sort
```

첫 명령의 결과로 `AppIdentity` 같은 필드가 바깥에 있는지 `CopilotEventData` 안에 있는지 보고, 그 경로로 `Copilot.`, `ConnectedAIApp.`, `AIApp.` 앞부분별 개수를 셉니다. 레코드 한 건을 필드별로 읽는 예는 [Microsoft 365 Copilot](../office-integrations/m365-copilot.md)에 있습니다. 본문이 필요하면 eDiscovery 에서 대상 사용자 메일함을 검색 범위로 잡고, 위 표의 item class 조건으로 찾습니다. 결과를 PST 로 내보내면 대화 한 건이 메일처럼 From/To 머리글을 달고 나오고, 머리글 읽는 법도 같은 페이지에서 다룹니다.

## 교차 검증

- [Microsoft 365 Copilot](../office-integrations/m365-copilot.md) — 업무 앱에서 쓴 Copilot 의 기록 성격, 앱별 item class, 레코드 예시
- [보안 제품이 남기는 AI 사용 기록](dlp-casb.md) — 제3자 AI 사이트 방문과 DLP 기록
- [AI 서비스 도메인과 네트워크 기록](network-traces.md) — 같은 시간대에 PC 에서 Copilot 관련 통신이 있었는지
- [ChatGPT 기업용 감사 기록](chatgpt-enterprise.md) — ChatGPT Enterprise 연결 기록
- [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) — `AccessedResources`·민감 정보 유형을 조사 질문에 쓰는 흐름

## 실습

Purview 기록은 테넌트 쪽 자료라서 공개된 디스크 이미지로는 풀 수 없고, 시험용 테넌트에서 풀어 봅니다.

1. 보존 정책 없이 Copilot 과 대화한 뒤 지우고, eDiscovery 로 찾을 수 있는지 봅니다. 보존 정책을 건 뒤 같은 일을 하고 비교합니다.
2. "1일 뒤 삭제" 정책을 걸고 대화가 `SubstrateHolds` 를 거쳐 영구 삭제되기까지 며칠 걸리는지 적습니다. 그동안 같은 대화의 감사 레코드는 그대로 있는지도 봅니다. 감사 레코드와 메일함 사본은 보관 체계가 따로입니다.
3. Teams 회의에서 회의 도우미를 쓰고 `TeamCopilotInteraction`(334) 레코드의 `Operation`·`AppIdentity` 를 확인합니다.
4. 내보낸 레코드의 `CreationTime` 과 포털의 `CreationDate` 를 나란히 놓고 시간대가 같은지 봅니다.
5. 활동 탐색기의 AI interaction 이벤트와 감사 기록의 `CopilotInteraction` 이 같은 상호작용을 가리키는지 시각과 사용자로 맞춰 봅니다.

## 참고 문헌

1. Audit logs for Copilot and AI applications — Microsoft Learn (ms.date 2026-08-26) — https://learn.microsoft.com/en-us/purview/audit-copilot
2. Learn about retention for Copilot and AI apps — Microsoft Learn (ms.date 2025-09-23, 갱신 2026-06-25) — https://learn.microsoft.com/en-us/purview/retention-policies-copilot
3. Learn how Microsoft Purview Data Security Posture Management for AI provides data security and compliance protections for Copilots and other generative AI apps (classic) — Microsoft Learn (ms.date 2025-12-15, 갱신 2026-06-25) — https://learn.microsoft.com/en-us/purview/dspm-for-ai
4. Search for and delete AI application data in eDiscovery — Microsoft Learn (ms.date 2026-06-19, 갱신 2026-06-29) — https://learn.microsoft.com/en-us/purview/edisc-search-copilot-data
5. Copilot interaction events overview (CopilotInteraction schema) — Microsoft Learn, Office 365 Management API (ms.date 2023-11-09, 갱신 2025-12-19) — https://learn.microsoft.com/en-us/office/office-365-management-api/copilot-schema
6. Office 365 Management Activity API schema — Microsoft Learn (ms.date 2025-10-15, 갱신 2026-09-02) — https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
7. Manage audit log retention policies — Microsoft Learn (ms.date 2026-06-19, 갱신 2026-06-24) — https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
