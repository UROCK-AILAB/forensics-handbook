---
title: "Microsoft 365 Copilot"
parent: "아티팩트 · 업무 도구 속 AI"
nav_order: 480
---

# Microsoft 365 Copilot (M365 Copilot)

## 한 줄 요약

Word·Excel·PowerPoint·Outlook·Teams 같은 업무 앱에서 쓴 Copilot 대화는 조직(테넌트)의 서비스 쪽에 저장되고, 조직이 감사를 켜 두었다면 Microsoft Purview 감사 로그에 `CopilotInteraction` 레코드가 남아 어느 앱에서, 어떤 문서를 근거로, 웹 검색을 썼는지를 알려 줍니다.

확인 날짜는 2026-09이고, 근거는 Microsoft Learn 문서 두 편(개인정보 문서 ms.date 2026-07-09·갱신 2026-08-18, 감사 로그 문서 ms.date 2026-08-26)입니다. 이 핸드북의 기기 관찰에는 Office 앱 폴더가 들어 있지 않아서, 기기 쪽 흔적은 관찰한 사실이 없습니다.

## 무엇을 기록하나 · 왜 생기나

Microsoft 365 Copilot 은 이름이 "Microsoft Copilot" 으로, Microsoft 365 Copilot Chat 은 "Microsoft Copilot Chat" 으로 바뀌는 중이고, 바뀌는 동안 옛 이름도 함께 쓰입니다. 개인 계정으로 쓰는 소비자용 Copilot 과 이름이 비슷하지만 저장 위치와 조회 방법이 다르므로, 소비자용은 [Microsoft Copilot](../chat-services/copilot/index.md) 페이지에서 따로 다룹니다.

Word·PowerPoint·Excel·OneNote·Loop·Whiteboard 등에서 Copilot 을 쓰면 사용자 프롬프트와 Copilot 응답, 응답의 근거로 든 인용을 저장합니다. 문서는 이 내용을 "상호작용 내용 (content of interactions)" 이라 부르고, 쌓인 기록을 "Copilot 활동 기록 (Copilot activity history)" 이라 부릅니다. 이 기록은 조직의 다른 Microsoft 365 콘텐츠와 같은 계약 조건으로 서비스 쪽에 저장되고, 저장할 때 암호화합니다.

감사 기록은 이와 따로 생깁니다. 조직이 감사를 켜 두었다면 Copilot 사용은 감사(Standard)에 자동으로 기록되고, 따로 설정할 것은 없습니다. 대화 본문을 담은 활동 기록과 사용 사실을 담은 감사 기록은 성격이 다르고, 조사에서는 두 가지를 구분해서 요청하고 해석해야 합니다. 서버·기기·동기화 사이에서 데이터가 어디에 놓이는지의 일반론은 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다.

## 위치와 버전별 차이

| 기록 | 위치 | 누가 볼 수 있나 | 비고 |
|---|---|---|---|
| 상호작용 내용(프롬프트·응답·인용) | 테넌트의 서비스 쪽 | 관리자(Content search, Microsoft Purview) | 사서함 안의 구체적인 폴더 이름은 문서에 나오지 않습니다 |
| Teams 에서 Copilot 과 나눈 대화 | 테넌트의 서비스 쪽 | 관리자(위 방법, Teams Export API) | |
| 감사 레코드 | Purview 감사 | 감사 권한이 있는 관리자 | 조직이 감사를 켜 둔 경우에만 생깁니다 |
| 사용자 화면의 활동 기록 | 서비스 쪽 | 사용자 본인(My Account 포털) | 사용자가 프롬프트·응답을 지울 수 있습니다 |
| 기기 쪽 캐시 | 확인하지 못함 | — | Windows·macOS Office 앱의 로컬 캐시나 레지스트리에 대화가 남는지는 문서에 나오지 않습니다 |

대화 원본은 서버(테넌트) 쪽에 있습니다. 기기에 대화 원본이 남는지는 공식 문서에 나오지 않고 이 핸드북에서도 확인하지 않았으므로, 기기 이미지만으로 대화 내용을 찾을 수 있다고 전제하지 않습니다.

기능이 켜지는 조건도 기록 해석에 영향을 줍니다. Office 개인정보 설정에서 "콘텐츠를 분석하는 연결된 환경 (connected experiences)" 을 끄면 Excel·OneNote·Outlook·PowerPoint·Word 에서 Copilot 기능이 사라지고, 이 조건은 Windows·Mac·iOS·Android 앱에 모두 적용됩니다. 해당 사용자의 설정이 꺼져 있었다면 그 기간 이 앱들에 Copilot 기록이 없어도 이상하지 않습니다.

## 구조

사용자 상호작용 감사 레코드는 `Operation`·`RecordType`·`Workload` 가 각각 `CopilotInteraction`·`CopilotInteraction`·`Copilot` 입니다. 조직에 등록한 자체·타사 AI 앱은 `ConnectedAIAppInteraction`, 조직 밖 타사 AI 앱은 `AIAppInteraction`(Workload `AIApp`) 으로 따로 남고, 타사 앱 기록은 종량제이고 180일 보관합니다. Teams 회의 도우미 (Facilitator) 는 RecordType `TeamCopilotInteraction` 에 Operation `AINotesUpdate`·`LiveNotesUpdate`·`TeamCopilotMsgInteraction` 으로 남습니다.

해석에 자주 쓰는 칸은 아래와 같습니다. 칸 전체 목록과 조회 절차는 [Microsoft Purview로 본 Copilot 기록](../network-enterprise/purview-copilot.md)에서 다룹니다.

| 칸 | 알려 주는 것 |
|---|---|
| `AppHost` | Copilot 을 부른 앱. 예: `Word`, `Excel`, `PowerPoint`, `Outlook`, `Teams`, `OneNote`, `Loop`, `BizChat`, `Edge`, `Bing` |
| `AppIdentity` | `workloadName.appGroup.appName` 형식. 예: `Copilot.MicrosoftCopilot.Microsoft365Copilot`, `Copilot.MicrosoftCopilot.BizChat`, `Copilot.Studio.` 뒤에 앱 ID |
| `Contexts` | 대화할 때 열려 있던 대상의 ID 와 `Type`. `Type` 예: `docx`, `pptx`, `xlsx`, `TeamsMeeting`, `TeamsChannel`, `TeamsChat` |
| `AccessedResources` | 응답을 만들며 접근한 자원. `SiteUrl`, `Name`, `Type`, `SensitivityLabelId`, `Action`, `PolicyDetails`, `Status`, `XPIADetected` 등 |
| `Messages` | 메시지 `ID`, 프롬프트인지 여부 `IsPrompt`, `JailbreakDetected`, `Size`(지금은 쓰지 않음) |
| `AISystemPlugin` | 쓴 플러그인의 `Name`·`ID`·`Version`. `Id` 가 `BingWebSearch` 이면 Bing 으로 공개 웹을 썼다는 뜻입니다 |
| `ModelTransparencyDetails` | `ModelProviderName`·`ModelName`·`ModelVersion`. 문서에 따르면 Microsoft 365 Copilot 상황에서는 `ModelProviderName` 만 늘 들어가고 `ModelName`·`ModelVersion` 은 없습니다 |
| `AgentId`·`AgentName`·`AgentVersion` | 에이전트를 거친 경우의 에이전트 정보 |

레코드 하나에는 보통 프롬프트와 응답 한 쌍이 들어가고, 프롬프트 하나에 응답이 여럿 붙기도 합니다. `Messages` 칸에는 메시지 ID 와 프롬프트 여부만 들어 있고, 문서의 예시에도 프롬프트 본문은 없습니다. 감사 레코드만으로는 무엇을 물었는지 알 수 없고, 본문이 필요하면 상호작용 내용을 따로 확보해야 합니다. 프롬프트·첨부·생성물을 어떻게 나눠 보는지는 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `CopilotInteraction` 레코드는 그 계정이 어느 앱(`AppHost`)에서 Copilot 과 주고받은 메시지가 있었다는 사실을 보여 줍니다. `Contexts` 와 `AccessedResources` 는 그 대화가 어떤 문서·회의·채팅을 대상으로 했고 어떤 자원에 접근했는지를 보여 주고, `SensitivityLabelId` 가 있으면 민감도 레이블이 붙은 자원이 응답에 쓰였는지까지 확인할 수 있습니다. `AISystemPlugin.Id` 가 `BingWebSearch` 이면 그 상호작용에서 공개 웹 검색을 썼다는 뜻이고, 이때 프롬프트에서 뽑은 검색어가 Bing Search 서비스로 나갑니다. 문서가 밝힌 처리 조건도 보고서에 인용할 수 있는데, 프롬프트·응답·Microsoft Graph 로 접근한 데이터는 기반 LLM 학습에 쓰지 않고, Azure OpenAI 의 남용 감시(사람 검토 포함)는 Copilot 서비스에서 끄고 씁니다.

**증명하지 못하는 것.** 감사 레코드는 프롬프트 본문을 담지 않아서 "무엇을 입력했다" 를 증명하지 못합니다. 계정의 사용 기록일 뿐이라서 그 시각에 자판 앞에 누가 있었는지도 따로 밝혀야 하고, 이 문제는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)에서 다룹니다. Microsoft Copilot·Copilot Chat 에서 사용자가 모델을 직접 고르면 모델 제공자와 모델 이름이 남지만, Auto 를 고르면 빠질 수 있고 Cowork 는 제공자 정보를 보여 주지 않습니다. Word 같은 Microsoft 365 Copilot 앱 상황에서는 `ModelName` 이 원래 들어가지 않습니다. 그래서 이 칸이 비었다고 특정 모델을 쓰지 않았다고 결론 내리지 않습니다. Anthropic·OpenAI 모델이 하위 처리자로 쓰일 수 있고 Anthropic 모델은 EU Data Boundary 밖에 있다는 점도, 데이터가 어느 지역에서 처리되었는지를 다룰 때 함께 적습니다.

보고서 문장은 "이 계정이 이 시간대에 Word 에서 문서 한 건을 대상으로 Copilot 과 메시지를 주고받은 감사 기록이 있다" 처럼 기록이 말하는 범위에서 씁니다.

## 시각 해석

이 페이지의 출처에는 감사 레코드의 시각 칸 이름과 시간대가 나오지 않습니다. 내보낸 파일을 받으면 시각 값에 시간대 표시가 붙어 있는지 먼저 확인하고, 다른 기록과 한 줄로 세울 때는 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)의 방법대로 기준 시간대를 하나로 맞춥니다. 감사(Standard)의 기본 보관 기간도 출처에 숫자가 없어서, 사건 날짜가 오래되었다면 조직의 보관 설정을 먼저 확인합니다.

## 함정과 한계

- **감사가 꺼진 조직.** 감사 레코드는 조직이 감사를 켜 둔 경우에만 생기고, 레코드가 없다는 사실이 사용하지 않았다는 뜻은 아닙니다.
- **사용자 삭제.** 사용자는 My Account 포털(myaccount.microsoft.com)에서 Copilot 활동 기록의 프롬프트·응답을 지울 수 있습니다. 활동 기록에서 사라진 대화가 감사 레코드나 Purview 보존 정책으로 남는지는 조직 설정에 따라 다르고, 보존 정책은 Purview 에서 Copilot 대화에 걸 수 있습니다. 보관과 삭제의 일반론은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에서 다룹니다.
- **`AppHost` 가 `Bing` 인 경우.** Edge 사이드바, Windows 의 Copilot, Office 모바일 앱, copilot.cloud.microsoft.com 에서 쓴 경우 `AppHost` 가 `Bing` 으로 남을 수 있어서, 값만 보고 검색 엔진을 썼다고 읽지 않습니다. 브라우저 쪽 흔적은 [브라우저에 들어간 AI](browser-builtin-ai.md)에서 다룹니다.
- **`AppIdentity` 로 거르기.** Purview 포털에서는 "Activities – operation names" 로 거르고, `AppIdentity` 로 거르려면 내보낸 뒤 오프라인에서 걸러야 합니다.
- **이름 혼동.** 이름이 바뀌는 중이라서 관리 화면·문서·사용자 진술에서 같은 기능을 다른 이름으로 부를 수 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 대화 원본이 서버 쪽에 있고 기기 쪽 저장 파일이 확인되지 않아서, 이 아티팩트는 헥스로 따라갈 파일이 없습니다. 대신 내보낸 감사 레코드를 텍스트로 한 번 읽어 봅니다. 아래는 감사 로그 문서의 칸 이름으로 **만든 예시**이고, 값은 모두 가짜이며 칸이 겹쳐 들어가는 모양은 설명을 위해 줄였습니다.

```json
{
  "RecordType": "CopilotInteraction",
  "Operation": "CopilotInteraction",
  "Workload": "Copilot",
  "AppHost": "Word",
  "AppIdentity": "Copilot.MicrosoftCopilot.Microsoft365Copilot",
  "Contexts": [ { "ID": "https://sample-tenant.example/sites/proj-hana/plan.docx", "Type": "docx" } ],
  "AccessedResources": [ { "Name": "plan.docx", "SensitivityLabelId": "00000000-0000-0000-0000-000000000000", "XPIADetected": false } ],
  "AISystemPlugin": [ { "Id": "BingWebSearch", "Name": "BingWebSearch" } ],
  "Messages": [ { "ID": "msg-0001", "IsPrompt": true }, { "ID": "msg-0002", "IsPrompt": false } ],
  "ModelTransparencyDetails": [ { "ModelProviderName": "SampleProvider" } ]
}
```

이 예시에서는 `AppHost` 로 Word 에서 불렀고, `Contexts` 로 대상이 docx 문서 한 건이고, `AISystemPlugin` 으로 웹 검색을 썼고, `Messages` 로 프롬프트 한 건과 응답 한 건이 오갔다는 것까지 읽을 수 있습니다. 프롬프트 본문은 어디에도 없습니다.

**공개 도구로 한 번.** 내보낸 JSON 은 jq 같은 공개 도구로 거를 수 있습니다. 예를 들어 `jq 'select(.AISystemPlugin[]?.Id == "BingWebSearch") | .AppHost'` 로 웹 검색을 쓴 상호작용의 앱만 뽑고, 같은 방식으로 `Contexts[].Type` 을 모아 어떤 종류의 문서를 대상으로 썼는지 셉니다. 내보낸 파일에서 레코드가 한 칸 안에 문자열로 들어 있다면 먼저 그 칸을 JSON 으로 풀어야 합니다.

## 교차 검증

- [Microsoft Purview로 본 Copilot 기록](../network-enterprise/purview-copilot.md) — 감사 레코드 전체 칸과 조회 절차
- [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) — 같은 시간대에 Copilot 관련 통신이 있었는지
- [보안 제품이 남기는 AI 사용 기록](../network-enterprise/dlp-casb.md) — DLP 가 같은 문서를 막거나 기록했는지
- [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) — `AccessedResources`·민감도 레이블을 조사 질문에 쓰는 흐름
- [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) — 테넌트 밖에서 자료를 받아야 할 때

## 실습

공개 검체(NIST CFReDS 등)에 Copilot 감사 레코드가 들어 있는지는 확인하지 않았습니다. 시험용 테넌트가 있다면 아래 질문을 직접 풀어 봅니다.

1. Word 에서 문서를 연 채 Copilot 에게 요약을 시키고, 생긴 `CopilotInteraction` 레코드의 `AppHost`·`Contexts` 가 무엇인지 확인합니다.
2. 같은 질문을 웹 검색을 켠 채 다시 하고, `AISystemPlugin` 이 어떻게 달라지는지 비교합니다.
3. Copilot Chat 에서 모델을 직접 고른 경우와 Auto 를 고른 경우에 `ModelTransparencyDetails` 가 어떻게 다른지 봅니다.
4. My Account 포털에서 활동 기록을 지운 뒤, 감사 레코드가 그대로 남는지 확인합니다.

## 참고 문헌

1. Data, Privacy, and Security for Microsoft Copilot | Microsoft Learn — https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
2. Audit logs for Copilot and AI applications | Microsoft Learn — https://learn.microsoft.com/en-us/purview/audit-copilot
