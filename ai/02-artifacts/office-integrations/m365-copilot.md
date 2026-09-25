---
title: "Microsoft 365 Copilot"
parent: "아티팩트 · 업무 도구 속 AI"
nav_order: 510
---

# Microsoft 365 Copilot (M365 Copilot)

## 한 줄 요약

Word·Excel·PowerPoint·Outlook·Teams 같은 업무 앱에서 쓴 Copilot 대화는 사용자 Exchange Online 사서함의 숨은 폴더에 저장되고, 조직이 감사를 켜 두었다면 Microsoft Purview 감사 로그에 `CopilotInteraction` 레코드가 따로 남아 어느 앱에서, 어떤 문서를 대상으로, 웹 검색을 썼는지를 알려 줍니다.

확인 날짜는 2026-09이고, 근거는 Microsoft Learn 문서입니다. 괄호 안은 문서의 ms.date 입니다.

- 개인정보 문서 (2026-07-09, 갱신 2026-08-18)
- Copilot·AI 앱 감사 문서 (2026-08-26)
- 감사 로그 보관 정책 문서 (2026-06-19, 갱신 2026-06-24)
- Copilot·AI 앱 보존 문서 (2025-09-23, 갱신 2026-06-25)
- eDiscovery 로 AI 앱 데이터 찾기 문서 (2026-06-19, 갱신 2026-06-29)
- Management Activity API 스키마 문서 (2025-10-15, 갱신 2026-09-02)와 그 하위 CopilotInteraction 스키마 문서 (2023-11-09, 갱신 2025-12-19)

Windows·macOS Office 앱이 기기에 Copilot 대화를 남기는지는 공식 문서에 나오지 않아서, 기기 쪽 흔적은 검체로 확인해야 합니다.

## 무엇을 기록하나 · 왜 생기나

Microsoft 365 Copilot 은 이름이 "Microsoft Copilot" 으로, Microsoft 365 Copilot Chat 은 "Microsoft Copilot Chat" 으로 바뀌었고, 바뀌는 동안 옛 이름도 함께 쓰입니다[1]. 개인 계정으로 쓰는 소비자용 Copilot 과 이름이 비슷하지만 저장 위치와 조회 방법이 달라서, 소비자용은 [Microsoft Copilot](../chat-services/copilot/index.md) 페이지에서 따로 다룹니다.

Word·PowerPoint·Excel·OneNote·Loop·Whiteboard 등에서 Copilot 을 쓰면 사용자 프롬프트와 Copilot 응답, 응답의 근거로 든 인용이 저장됩니다. 문서는 이 내용을 "상호작용 내용 (content of interactions)" 이라 부르고, 쌓인 기록을 "Copilot 활동 기록 (Copilot activity history)" 이라 부릅니다. 이 기록은 조직의 다른 Microsoft 365 콘텐츠와 같은 계약 조건으로 저장하고, 저장할 때 암호화합니다[1]. 저장소의 실체는 사용자 Exchange 사서함입니다. 프롬프트·응답은 AI 앱을 쓴 사용자의 사서함 안 숨은 폴더에 복사되고, 이 폴더는 사용자나 관리자가 직접 여는 곳이 아니라 eDiscovery 로 검색하는 곳입니다[4]. 입력한 텍스트, 미리 채워진 프롬프트를 고른 기록, 응답의 텍스트·링크·참조가 들어가고, 응답을 만드는 중이라는 안내 메시지는 넣지 않습니다[4].

감사 레코드는 이와 따로 생깁니다. 조직이 감사를 켜 두었다면 Copilot 사용은 감사(Standard)에 자동으로 기록되고, 따로 설정할 것은 없습니다[2]. 본문을 담은 사서함 항목과 사용 사실만 담은 감사 레코드는 성격도 보관 체계도 달라서, 조사에서는 둘을 나눠 요청하고 해석합니다. 서버·기기·동기화 사이에서 데이터가 어디에 놓이는지의 일반론은 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다.

## 위치와 버전별 차이

| 기록 | 위치 | 조회 방법 | 본문 |
|---|---|---|---|
| 상호작용 내용(프롬프트·응답·인용) | 사용자 Exchange Online 사서함(RecipientTypeDetails `UserMailbox`)의 숨은 폴더. 폴더 이름은 문서에 나오지 않습니다 | Content search, Purview eDiscovery[1][4] | 있음 |
| 지웠거나 보존 기간이 끝난 항목 | 같은 사서함의 숨은 폴더 `SubstrateHolds` | eDiscovery (영구 삭제 전까지)[4] | 있음 |
| 퇴사자 항목 | 비활성 사서함 (inactive mailbox) | eDiscovery[4] | 있음 |
| Teams 에서 Copilot 과 나눈 대화 | 위와 같은 사서함 | 위 방법, Teams Export API[1] | 있음 |
| Copilot 메모리 | 사서함 항목, item class `IPM.Contact` | eDiscovery (연락처로 걸림)[5] | 메모리 내용 |
| 감사 레코드 | Purview 감사 | 감사 권한이 있는 관리자 | 없음(메시지 ID 만) |
| 사용자 화면의 활동 기록 | 위 상호작용 내용과 같은 저장 데이터 | 사용자 본인이 Copilot Chat·Teams 회의에서 보고, My Account 포털에서 지움[1] | 있음 |

사서함 항목은 앱마다 item class 가 다르고, eDiscovery 에서 이 값으로 앱을 가려 찾습니다[5].

| 앱 | item class |
|---|---|
| Word | `IPM.SkypeTeams.Message.Copilot.Word` |
| Excel | `IPM.SkypeTeams.Message.Copilot.Excel` |
| PowerPoint | `IPM.SkypeTeams.Message.Copilot.Powerpoint` |
| Outlook | `IPM.SkypeTeams.Message.Copilot.Outlook` |
| OneNote | `IPM.SkypeTeams.Message.Copilot.OneNote` |
| Loop | `IPM.SkypeTeams.Message.Copilot.Loop` |
| Whiteboard | `IPM.SkypeTeams.Message.Copilot.Whiteboard` |
| SharePoint | `IPM.SkypeTeams.Message.Copilot.SharePoint` |
| Forms | `IPM.SkypeTeams.Message.Copilot.Forms` |
| Teams 채팅·채널·회의 | `IPM.SkypeTeams.Message.Copilot.Teams` |
| Copilot Chat (BizChat, Teams 안의 Copilot Chat 포함) | `IPM.SkypeTeams.Message.Copilot.BizChat` |
| Microsoft 365 앱 | `IPM.SkypeTeams.Message.Copilot.M365App` |
| WebChat | `IPM.SkypeTeams.Message.Copilot.WebChat` |
| Copilot Studio 앱 | `IPM.SkypeTeams.Message.Copilot.Studio.*` |
| Microsoft 365 Copilot 전체 | `IPM.SkypeTeams.Message.Copilot.*` |
| Teams 회의 도우미 AI 노트 | `IPM.SkypeTeams.Message.TeamCopilot.AiNotes.Teams` |

보존 정책을 거는 위치는 예전에는 "Teams chats and Copilot interactions" 한 곳에 묶여 있었고 지금은 "Microsoft Copilot experiences" 로 분리되었습니다[4]. 옛 정책을 볼 때는 어느 시기의 설정인지 먼저 확인하고, 위치 구분과 삭제 흐름의 자세한 내용은 [Microsoft Purview로 본 Copilot 기록](../network-enterprise/purview-copilot.md)을 봅니다.

기능이 켜지는 조건도 기록 해석에 영향을 줍니다. 조직이 Office 개인정보 설정에서 "콘텐츠를 분석하는 연결된 환경 (connected experiences that analyze your content)" 을 끄면 Excel·OneNote·Outlook·PowerPoint·Word 에서 Copilot 기능이 사라지고, 이 조건은 Windows·Mac·iOS·Android 의 최신판 앱에 모두 적용됩니다[1]. "선택적 연결된 환경" 을 끄면 웹 검색처럼 그 범주에 드는 Copilot 기능이 사라질 수 있습니다[1]. 해당 사용자에게 이런 설정이 걸려 있던 기간이라면 그 앱들에 Copilot 기록이 없어도 이상하지 않습니다.

## 구조

### 감사 레코드를 가르는 값

| `RecordType` 이름 | 숫자 | `Workload` | 대상 |
|---|---|---|---|
| `CopilotInteraction` | 261 | `Copilot` | Microsoft 가 만든 Copilot(Microsoft 365 Copilot, Security Copilot 등). 문서 예시에서는 Copilot Studio 로 만든 앱도 여기에 남습니다 |
| `AIAppInteraction` | 284 | `AIApp` | 조직에 배포하지 않은 타사 AI 앱 |
| `ConnectedAIAppInteraction` | 328 | `ConnectedAIApp` | 조직 테넌트에 배포·등록한 사용자 정의 Copilot·타사 AI 앱 |
| `TeamCopilotInteraction` | 334 | — | Teams 회의 도우미 (Facilitator). `Operation` 은 `AINotesUpdate`·`LiveNotesUpdate`·`TeamCopilotMsgInteraction` |

숫자는 Management Activity API 스키마의 AuditLogRecordType 표에서 왔습니다[6]. 감사 문서의 표는 `RecordType` 을 이름으로 적지만[2], CopilotInteraction 스키마 문서의 예시에서는 AuditData 안과 바깥 목록의 `RecordType` 이 모두 숫자 `261` 입니다[7].

사용자 정의 앱을 모두 `ConnectedAIAppInteraction` 으로 읽으면 틀립니다. 감사 문서의 예시에서 Copilot Studio 로 만든 앱은 `RecordType`·`Operation` 이 `CopilotInteraction` 이고, `AppIdentity` 가 `Copilot.Studio.` 뒤에 앱 GUID 를 붙인 값이며, Teams 에 배포했다면 `AppHost` 가 `Teams` 입니다[2]. 감사(Standard)에 포함되는 것은 Microsoft 앱과 Copilot Studio·Foundry 로 만든 앱이고, 종량제 (pay-as-you-go) 과금은 `AIAppInteraction` 과 일부 `ConnectedAIAppInteraction` 에 적용되며 180일 보관합니다[2].

### 레코드의 짜임

CopilotInteraction 스키마 문서의 레코드 예시(2023-12)를 보면, 한 레코드는 공통 칸 바깥층과 `CopilotEventData` 객체로 나뉩니다[7]. 해석에 쓰는 칸 대부분은 `CopilotEventData` 안에 있어서, 내보낸 JSON 을 걸러 낼 때 경로를 이 객체부터 적어야 합니다.

| 층 | 칸 |
|---|---|
| 바깥층 | `CreationTime`, `Id`, `Operation`, `OrganizationId`, `RecordType`, `UserKey`, `UserType`, `Version`, `Workload`, `ClientIP`, `ClientRegion`, `UserId` |
| `CopilotEventData` 안 | `AppHost`, `Contexts`, `ThreadId`, `MessageIds`, `Messages`, `AccessedResources`, `ModelTransparencyDetails`, `AISystemPlugin` |

스키마 정의에는 이 밖에 `CopilotLogVersion` 이 레코드 칸으로 있습니다[7]. 감사 문서(2026-08-26)는 `AppIdentity`, `AgentId`·`AgentName`·`AgentVersion`, `DLPEvaluationDeferred`, `DLPEvaluationDeferredReason`, `CapacityId` 같은 칸을 더 적지만, 이 칸들이 레코드의 어느 층에 들어가는지는 보여 주지 않습니다[2]. 내보낸 레코드에서 위치를 먼저 확인합니다.

### 해석에 자주 쓰는 칸

| 칸 | 알려 주는 것 |
|---|---|
| `AppHost` | Copilot 을 부른 앱. 아래 표 참고 |
| `AppIdentity` | `workloadName.appGroup.appName` 꼴. 예: `Copilot.MicrosoftCopilot.Microsoft365Copilot`, `Copilot.MicrosoftCopilot.BizChat`, `Copilot.Studio.` 뒤에 앱 ID[2] |
| `Contexts` | 대화할 때 열려 있던 대상의 `Id` 와 `Type`. `Id` 는 SharePoint 파일 ID·경로, Teams 채팅·회의 ID 등이고, `Type` 은 `docx`, `pptx`, `xlsx`, `TeamsMeeting`, `TeamsChannel`, `TeamsChat` 등[2][7] |
| `ThreadId` | 대화 스레드 ID. 문서 예시의 형식은 `19:` 로 시작해 `@thread.v2` 로 끝납니다[7] |
| `Messages` | 메시지 ID 와 프롬프트인지 여부. 한 레코드에 보통 프롬프트·응답 한 쌍이 들어가고, 프롬프트 하나에 응답이 여럿 붙기도 합니다. `JailbreakDetected` 는 탈옥 시도 탐지 여부이고 `Size` 는 지금 쓰지 않습니다[2] |
| `MessageIds` | Microsoft 내부용으로 예약된 칸입니다[7] |
| `AccessedResources` | 응답을 만들며 접근한 파일·메일·메시지. 하위 칸 `Id`, `SiteUrl`, `listItemUniqueId`, `Type`, `Name`, `SensitivityLabelId`, `Action`(read·create·modify), `PolicyDetails`, `Status`, `XPIADetected`[2][7] |
| `AISystemPlugin` | 쓴 플러그인의 `Name`·`Id`·`Version`. `Id` 가 `BingWebSearch` 이면 Bing 으로 공개 웹을 썼다는 뜻입니다. 2023 예시의 값은 `{"Id":"BingWebSearch","Name":"BuiltIn"}` 입니다[2][7] |
| `ModelTransparencyDetails` | `ModelProviderName`·`ModelName`·`ModelVersion`[2] |
| `DLPEvaluationDeferred` | DLP 평가를 미룬 단계를 나타내는 비트 값. 1 Prompt, 2 Response, 4 Grounding, 8 WebGrounding[2] |
| `ClientIP`·`ClientRegion` | 요청한 쪽의 IP 와 지역[6][7] |

`Messages` 의 키 이름은 문서마다 대소문자가 다릅니다. 스키마 정의와 2023 예시는 `Id`·`isPrompt` 이고, 감사 문서(2026-08-26)의 설명은 `ID`·`IsPrompt`, 같은 문서의 예시는 `ID`·`isPrompt` 입니다[2][7]. jq 는 키의 대소문자를 가리므로, 걸러 내기 전에 검체의 실제 키를 확인합니다.

`AppHost` 값 가운데 헷갈리기 쉬운 것은 아래와 같습니다[2].

| `AppHost` | 쓴 곳 |
|---|---|
| `Word`, `Excel`, `PowerPoint`, `OneNote`, `Loop`, `Whiteboard`, `Forms`, `Planner`, `Stream`, `SharePoint`, `Teams` | 그 앱 안의 Copilot |
| `WordOnCanvas`, `PowerPointOnCanvas`, `OutlookOnCanvas` | 옆 창이 아니라 문서·슬라이드·메일 작성 창 안에서 바로 쓴 Copilot |
| `Outlook`, `OutlookSidepane` | Outlook 의 Copilot. `OutlookSidepane` 은 옆 창 |
| `BizChat` | Copilot Chat 클라이언트(Teams 나 앱), microsoft365.com/copilot·/chat |
| `Office` | office.com·microsoft365.com |
| `M365App` | Windows·모바일의 Microsoft 365 앱에서 연 Copilot Chat |
| `Bing` | Edge 브라우저·Edge 사이드바, Windows Copilot, Office 모바일 앱, copilot.cloud.microsoft.com |
| `Edge` | Edge 사이드바에서 쓴 Copilot Chat |
| `OfficeCopilotNotebook`, `OneNoteCopilotNotebook` | Copilot Notebooks |
| `OfficeCopilotSearchAnswer` | Microsoft 365 검색 결과에 붙은 Copilot 답변 |

## 증거로서 의미

**증명하는 것.** `CopilotInteraction` 레코드는 그 계정이 어느 앱(`AppHost`)에서 Copilot 과 메시지를 주고받았다는 사실을 보여 줍니다. `Contexts` 와 `AccessedResources` 로는 그 대화가 어떤 문서·회의·채팅을 대상으로 했고 어떤 자원을 읽거나 만들었는지 알 수 있고, `SensitivityLabelId` 가 있으면 민감도 레이블이 붙은 자원이 응답에 쓰였는지도 확인할 수 있습니다. `ThreadId` 가 같은 레코드를 모으면 한 대화에 속한 상호작용을 묶을 수 있습니다. `AISystemPlugin.Id` 가 `BingWebSearch` 이면 그 상호작용에서 공개 웹 검색을 썼다는 뜻이고, 이때 Copilot 은 프롬프트에서 뽑은 말로 검색어를 만들어 Bing Search 서비스로 보냅니다[1][2]. 사서함 항목은 본문을 담고 있어서 무엇을 물었고 무엇을 받았는지를 보여 줍니다. 문서가 밝힌 처리 조건도 보고서에 인용할 수 있습니다. 프롬프트·응답·Microsoft Graph 로 접근한 데이터는 기반 LLM 학습에 쓰지 않고, Azure OpenAI 의 남용 감시(사람 검토 포함)는 Copilot 서비스에서 끄고 씁니다[1].

**증명하지 못하는 것.** 감사 레코드에는 프롬프트 본문이 없어서 "무엇을 입력했다" 를 증명하지 못하고, 본문은 사서함 항목에서 따로 확보해야 합니다. 프롬프트·첨부·생성물을 나눠 보는 방법은 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)에서 다룹니다. 레코드는 계정의 사용 기록이라서 그 시각에 자판 앞에 누가 있었는지도 따로 밝혀야 하고, 이 문제는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)에서 다룹니다. `ClientIP` 도 서비스에 따라 사용자 기기가 아니라 사용자 대신 서비스를 부른 앱(예: 웹판 Office)의 주소일 수 있다고 스키마 문서가 적습니다[6].

모델 정보도 비어 있을 수 있습니다. 감사 문서는 Microsoft 365 Copilot 상황에서 `ModelProviderName` 만 늘 들어가고 `ModelName`·`ModelVersion` 은 없다고 적습니다[2]. Microsoft Copilot·Copilot Chat 에서 사용자가 모델을 직접 고르면 제공자와 모델 이름이 남지만, Auto 를 고르면 빠질 수 있고 Cowork 는 제공자 정보를 보여 주지 않습니다[2]. 그래서 이 칸이 비었다고 특정 모델을 쓰지 않았다고 결론 내리지 않습니다. Anthropic·OpenAI 모델이 하위 처리자로 쓰일 수 있고 Anthropic 모델은 지금 EU Data Boundary 밖에 있다는 점도, 데이터가 어느 지역에서 처리되었는지를 다룰 때 함께 적습니다[1].

보고서 문장은 "이 계정이 이 시간대에 Word 에서 문서 한 건을 대상으로 Copilot 과 메시지를 주고받은 감사 기록이 있고, 같은 시간대 사서함에 item class `IPM.SkypeTeams.Message.Copilot.Word` 항목이 두 건 있다" 처럼 자료마다 말하는 범위를 나눠 씁니다.

## 시각 해석

감사 레코드의 시각 칸은 바깥층의 `CreationTime` 이고, 스키마 문서는 이 값을 "레코드가 생성된 UTC 시각" 으로 정의합니다[6]. 2023 예시의 값은 `2023-12-13T17:12:36` 처럼 끝에 `Z` 같은 시간대 표시가 없어서, 현지 시각으로 잘못 읽지 않도록 합니다[7]. 같은 예시에서 레코드 목록의 `CreationDate` 는 `12/13/2023 17:12` 처럼 월/일/연도 순서에 분 단위까지만 보여 줍니다[7]. 초까지 맞춰야 하면 AuditData 안의 `CreationTime` 을 씁니다. 다른 기록과 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

보관 기간은 사건 날짜가 오래되었을 때 가장 먼저 따질 점입니다[3].

| 경우 | 기본 보관 |
|---|---|
| 감사(Standard), 2023-10-17 이후 생긴 레코드 | 180일 |
| 감사(Standard), 2023-10-17 이전 생긴 레코드 | 90일 |
| 감사(Premium) 기본 정책 | Workload 가 AzureActiveDirectory·Exchange·OneDrive·SharePoint 인 레코드만 1년. Workload `Copilot` 은 여기에 들지 않아 180일 |
| 사용자 지정 보관 정책 | E5 계열 라이선스가 있는 사용자는 1년까지, 10년 추가 라이선스가 더 있으면 10년까지 |
| 타사 AI 앱(종량제) | 180일[2] |

E5 라이선스가 있는 조직이라도 Copilot 레코드를 1년 두려면 사용자 지정 정책이 따로 있어야 합니다. 보관 기간은 레코드가 감사 파이프라인에 들어올 때 정해지고, 나중에 라이선스나 정책을 바꿔도 이미 들어온 레코드에는 적용되지 않습니다[3]. 그래서 조직의 지금 정책이 아니라 사건 당시의 정책을 확인합니다.

사서함 항목은 시각보다 삭제 흐름을 알아야 해석할 수 있습니다. 보존 정책이 걸린 사서함에서 사용자가 대화를 지우면 항목이 `SubstrateHolds` 로 옮겨지고, 보존 기간이 끝난 뒤 그 폴더에 최소 1일 머물면 보통 1~7일 간격으로 도는 타이머 작업이 영구 삭제합니다. 보존 기간이 끝났는데 앱에 남아 있는 항목은 `SubstrateHolds` 로 복사된 뒤 같은 과정을 거치고, 문서 예시에서는 1일 뒤 삭제하는 정책이라도 영구 삭제까지 16일이 걸릴 수 있습니다. 그래서 지운 시각과 항목이 사라진 시각이 며칠 어긋날 수 있습니다[4]. 자세한 흐름은 [Microsoft Purview로 본 Copilot 기록](../network-enterprise/purview-copilot.md)에 있습니다.

## 함정과 한계

- **감사가 꺼진 조직.** 감사 레코드는 조직이 감사를 켜 둔 경우에만 생기고, 레코드가 없다는 사실이 사용하지 않았다는 뜻은 아닙니다.
- **앱 화면과 보존 상태는 다르다.** Copilot 메시지는 창이나 앱을 닫아도 숨겨질 뿐 그대로 있습니다. 실제로 지워지는 경우는 사용자가 Copilot Chat 에서 대화를 지우거나 전체 기록 삭제를 요청할 때이고, 이때도 항목은 `SubstrateHolds` 로 먼저 갑니다[4]. 문서는 앱에 보이는지 여부가 보존·삭제 상태를 정확히 나타내지 않는다고 적습니다[4]. 같은 사서함에 다른 보존 정책, Litigation Hold, delay hold, eDiscovery hold 가 걸려 있으면 영구 삭제가 멈춥니다[4]. 보관과 삭제의 일반론은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에서 다룹니다.
- **감사 레코드와 사서함 항목은 보관 체계가 다르다.** 감사 레코드는 감사 보관 정책을 따르고[3], 사서함 항목은 보존 정책과 `SubstrateHolds` 삭제 흐름을 따릅니다[4]. 사용자가 My Account 포털에서 활동 기록을 지웠을 때[1] 감사 레코드가 어떻게 되는지는 공개 문서에 나오지 않아서 시험용 테넌트나 검체로 확인해야 합니다.
- **메모리는 대화와 따로 남는다.** Copilot 메모리는 `IPM.Contact` 항목으로 저장되고, Purview 나 eDiscovery 에서 대화·메시지를 지워도 연결된 메모리는 지워지지 않습니다[5].
- **퇴사자.** 계정을 지우면 보존 대상 메시지는 비활성 사서함에 남고, 떠나기 전에 걸려 있던 보존 정책을 계속 따릅니다[4].
- **`AppHost` 가 `Bing` 인 경우.** Edge 사이드바, Windows Copilot, Office 모바일 앱, copilot.cloud.microsoft.com 에서 쓴 Copilot Chat 이 `Bing` 으로 남아서, 값만 보고 검색 엔진을 썼다고 읽지 않습니다[2]. 웹 검색 여부는 `AISystemPlugin` 으로 따로 봅니다. 브라우저 쪽 흔적은 [브라우저에 들어간 AI](browser-builtin-ai.md)에서 다룹니다.
- **`AppIdentity` 로 거르기.** Purview 포털에서는 "Activities – operation names" 로 거르고, `AppIdentity` 로 거르려면 내보낸 뒤 오프라인에서 걸러야 합니다[2].
- **레코드 모양이 시기마다 다르다.** 2023 예시에는 `ModelTransparencyDetails` 에 `"ModelName":"DEEP_LEO"` 가 들어 있지만, 지금 감사 문서는 Microsoft 365 Copilot 상황에 `ModelName` 이 없다고 적습니다[2][7]. 오래된 레코드와 최근 레코드를 섞어 볼 때는 칸 유무를 기간별로 따로 셉니다.
- **이름 혼동.** 이름이 바뀌는 중이라서 관리 화면·문서·사용자 진술에서 같은 기능을 다른 이름으로 부를 수 있습니다.

## 직접 분석해 보기

**헥스 대신 텍스트로 한 번.** 대화 원본과 감사 레코드 모두 테넌트 쪽 자료라서, 이 아티팩트는 헥스로 따라갈 기기 파일이 없습니다. 대신 내보낸 감사 레코드 한 건을 텍스트로 읽어 봅니다. 아래는 CopilotInteraction 스키마 문서 예시[7]의 짜임을 따라 **만든 예시**이고, 값은 모두 지어낸 것입니다.

```json
{
  "CreationTime": "2026-03-04T05:06:07",
  "Id": "11111111-2222-3333-4444-555555555555",
  "Operation": "CopilotInteraction",
  "OrganizationId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "RecordType": 261,
  "UserType": 0,
  "Version": 1,
  "Workload": "Copilot",
  "ClientIP": "203.0.113.10",
  "ClientRegion": "KR",
  "UserId": "user01@sample-tenant.example",
  "CopilotEventData": {
    "AppHost": "Word",
    "Contexts": [ { "Id": "https://sample-tenant.example/sites/proj/plan.docx", "Type": "docx" } ],
    "AccessedResources": [ { "Action": "Read", "Name": "budget.xlsx", "Type": "xlsx",
                             "SensitivityLabelId": "00000000-0000-0000-0000-000000000001" } ],
    "AISystemPlugin": [ { "Id": "BingWebSearch", "Name": "BuiltIn" } ],
    "Messages": [ { "Id": "1700000000001", "isPrompt": true },
                  { "Id": "1700000000002", "isPrompt": false } ],
    "MessageIds": [],
    "ModelTransparencyDetails": [],
    "ThreadId": "19:sampleThread0001@thread.v2"
  }
}
```

이 레코드에서는 2026-03-04 05:06:07 UTC 에 Word 에서 불렀고, 열려 있던 문서는 docx 한 건이며, 응답을 만들며 레이블이 붙은 xlsx 한 건을 읽었고, 웹 검색을 썼고, 프롬프트 한 건과 응답 한 건이 오갔다는 것까지 읽을 수 있습니다. 프롬프트 본문은 어디에도 없습니다.

**공개 도구로 한 번.** 내보낸 JSON 은 jq 같은 공개 도구로 거릅니다. 칸이 `CopilotEventData` 안에 있으므로 경로를 그 객체부터 적어야 하고, 바깥층에 `.AppHost` 로 적으면 아무것도 걸리지 않습니다. 웹 검색을 쓴 상호작용의 시각과 앱만 뽑으려면 아래처럼 씁니다.

```sh
jq -c 'select(any(.CopilotEventData.AISystemPlugin[]?; .Id == "BingWebSearch"))
       | {CreationTime, AppHost: .CopilotEventData.AppHost, ThreadId: .CopilotEventData.ThreadId}' records.jsonl
```

프롬프트 수는 키 대소문자가 다를 수 있어서 두 가지를 함께 보고, `-s` 로 레코드 전체를 한 번에 셉니다.

```sh
jq -s '[.[].CopilotEventData.Messages[]? | select(.isPrompt // .IsPrompt)] | length' records.jsonl
```

같은 방식으로 `.CopilotEventData.Contexts[].Type` 을 모으면 어떤 종류의 문서를 대상으로 썼는지 셀 수 있습니다. 스키마 문서 예시처럼 내보낸 목록에서 레코드가 AuditData 칸에 JSON 문자열로 들어 있다면[7], 그 칸을 먼저 JSON 으로 풀어야 합니다(jq 에서는 `fromjson`).

## 교차 검증

- [Microsoft Purview로 본 Copilot 기록](../network-enterprise/purview-copilot.md) — 보존 위치 구분, `SubstrateHolds` 삭제 흐름, DSPM for AI 활동 탐색기
- [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) — 같은 시간대에 Copilot 관련 통신이 있었는지
- [보안 제품이 남기는 AI 사용 기록](../network-enterprise/dlp-casb.md) — DLP 가 같은 문서를 막거나 기록했는지, `DLPEvaluationDeferred` 와 맞춰 보기
- [브라우저에 들어간 AI](browser-builtin-ai.md) — `AppHost` 가 `Bing`·`Edge` 인 레코드의 브라우저 쪽 흔적
- [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) — `AccessedResources`·민감도 레이블을 조사 질문에 쓰는 흐름
- [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) — 테넌트 밖에서 자료를 받아야 할 때

## 실습

이 자료는 테넌트 쪽에만 있어서 PC 이미지로 된 공개 검체로는 풀 수 없고, 시험용 테넌트가 있을 때 아래 질문을 풀어 봅니다.

1. Word 에서 문서를 연 채 Copilot 에게 요약을 시키고, 생긴 `CopilotInteraction` 레코드의 `AppHost`·`Contexts`·`ThreadId` 를 확인합니다. 같은 대화에서 한 번 더 물었을 때 `ThreadId` 가 같은지 봅니다.
2. 같은 질문을 웹 검색을 켠 채 다시 하고, `AISystemPlugin` 이 어떻게 달라지는지 비교합니다.
3. 포털 목록의 `CreationDate` 와 AuditData 의 `CreationTime` 을 나란히 놓고, 포털이 어느 시간대로 보여 주는지 확인합니다.
4. Copilot Chat 에서 대화를 지운 뒤 감사 레코드가 그대로 남는지 보고, eDiscovery 에서 item class `IPM.SkypeTeams.Message.Copilot.BizChat` 으로 검색해 같은 대화가 `SubstrateHolds` 에서 며칠 동안 걸리는지 적습니다.
5. eDiscovery 결과를 PST 로 내보내고, 프롬프트 항목과 응답 항목의 From/To 가 어떻게 붙는지 확인합니다. 문서에 따르면 프롬프트는 From 이 사용자의 기본 SMTP 주소, To 가 Copilot 앱 이름(예: Microsoft 365 Chat, 호스트 앱 이름, WebChat)이고 응답은 그 반대이며, Copilot 앱 이름은 메일을 받을 수 있는 주소가 아닙니다[5].

## 참고 문헌

1. Data, Privacy, and Security for Microsoft Copilot — Microsoft Learn (2026-07-09, 갱신 2026-08-18) — https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
2. Audit logs for Copilot and AI applications — Microsoft Learn (2026-08-26) — https://learn.microsoft.com/en-us/purview/audit-copilot
3. Manage audit log retention policies — Microsoft Learn (2026-06-19, 갱신 2026-06-24) — https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
4. Learn about retention for Copilot and AI apps — Microsoft Learn (2025-09-23, 갱신 2026-06-25) — https://learn.microsoft.com/en-us/purview/retention-policies-copilot
5. Search for and delete AI application data in eDiscovery — Microsoft Learn (2026-06-19, 갱신 2026-06-29) — https://learn.microsoft.com/en-us/purview/edisc-search-copilot-data
6. Office 365 Management Activity API schema — Microsoft Learn (2025-10-15, 갱신 2026-09-02) — https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
7. CopilotInteraction (Copilot interaction events overview) — Microsoft Learn (2023-11-09, 갱신 2025-12-19) — https://learn.microsoft.com/en-us/office/office-365-management-api/copilot-schema
