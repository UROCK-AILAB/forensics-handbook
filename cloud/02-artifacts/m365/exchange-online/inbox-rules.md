---
title: "받은편지함 규칙과 전달"
parent: "Exchange Online"
grand_parent: "아티팩트 · Microsoft 365"
nav_order: 230
---

# 받은편지함 규칙과 전달 (Inbox Rules·Forwarding)

받은편지함 규칙과 메일함 전달 설정은 메일을 계정 주인 모르게 밖으로 내보내거나 숨기는 데 쓰일 수 있어서, 현재 설정과 감사 로그에 남은 변경 이력을 함께 봐야 하는 흔적입니다.

## 무엇을 기록하나 · 왜 생기나

Exchange Online 에서 메일을 자동으로 다른 곳에 보내는 길은 두 가지입니다. 하나는 사용자가 만드는 받은편지함 규칙 (Inbox Rule) 이고, 다른 하나는 관리자가 메일함에 거는 메일함 전달 (Mailbox Forwarding, SMTP 전달이라고도 함) 입니다[4]. 받은편지함 규칙은 조건에 맞는 메일을 전달하거나, 다른 폴더로 옮기거나, 지우거나, 읽음으로 표시할 수 있습니다[2]. 외부로 자동 전달하는 규칙은 사용자가 일부러 만들기도 하지만 계정이 뚫린 결과로 생기기도 하고[4], 계정을 가로챈 사람은 규칙을 다시 들어오는 발판 (persistence) 으로 쓰기도 합니다[6].

기록은 두 층으로 나뉩니다. 수집하는 순간의 설정은 Exchange Online PowerShell 로 읽고, 누가 언제 규칙과 전달을 만들고 바꿨는지는 통합 감사 로그 (Unified Audit Log) 에서 찾습니다[1][3][8]. 통합 감사 로그 전반과 보관 기간은 [통합 감사 로그](../unified-audit-log/index.md)에 있습니다.

## 위치와 확인 방법

| 알고 싶은 것 | 어디서 | 확인 방법 |
|---|---|---|
| 지금 걸려 있는 받은편지함 규칙 | 메일함 설정 | `Get-InboxRule -Mailbox 사용자`, 숨긴 규칙까지 보려면 `-IncludeHidden`[1] |
| 지금 걸려 있는 메일함 전달 | 메일함 속성 | `Get-Mailbox` 의 `ForwardingAddress`·`ForwardingSmtpAddress`·`DeliverToMailboxAndForward`[3][12] |
| 스위프 규칙 (Sweep Rule) | 메일함 설정 | `Get-SweepRule -Mailbox 사용자`[12] |
| 웹용 Outlook·PowerShell 로 만든 규칙의 생성·수정·삭제 | 통합 감사 로그, RecordType `ExchangeAdmin` | 작업 이름 `New-InboxRule`·`Set-InboxRule`·`Remove-InboxRule`[7][12] |
| Outlook 클라이언트로 만든 규칙의 생성·수정·삭제 | 통합 감사 로그, 메일함 감사 | 작업 이름 `UpdateInboxRules`[7][8] |
| 메일함 전달 설정 변경 | 통합 감사 로그, RecordType `ExchangeAdmin` | 작업 이름 `Set-Mailbox` 등, `Parameters` 에 전달 관련 매개변수[5][12] |
| 실제로 전달된 메일 | 메시지 추적, Defender `EmailEvents` | [메시지 추적](message-trace.md), `ForwardingInformation` 열[9] |
| 의심스러운 전달·조작 규칙 탐지 | Entra ID Protection, Defender for Cloud Apps 경고 | 위험 유형 `suspiciousInboxForwarding`·`mcasSuspiciousInboxManipulationRules`[10][13] |

`Get-InboxRule` 은 Exchange Online 의 View-Only Organization Management 역할 그룹이나 Microsoft Entra ID 의 Global Reader 역할로는 실행되지 않습니다[1]. 읽기 전용 계정만 받은 조사라면 이 명령을 쓸 권한부터 확보해야 합니다.

`UpdateInboxRules` 는 메일함 감사의 기본 작업이라서 Admin·Delegate·Owner 로그온 모두에서 기본으로 기록됩니다[8]. 메일함 감사가 켜지는 조건과 로그온 유형은 [메일함 감사와 MailItemsAccessed](mailbox-auditing.md)에 있습니다.

Identity Protection 의 두 탐지는 Microsoft Defender for Cloud Apps 가 준 정보로 오프라인 계산되며, 라이선스 조건이 붙습니다(2026년 4월 문서 기준)[10].

| 탐지 | 위험 유형 값 | 필요한 라이선스 |
|---|---|---|
| Suspicious inbox forwarding | `suspiciousInboxForwarding` | Microsoft Entra ID P2 와 Defender for Cloud Apps 단독 라이선스, 또는 Microsoft 365 E5 와 EMS E5 |
| Suspicious inbox manipulation rules | `mcasSuspiciousInboxManipulationRules` | 위와 같음 |

## 구조

### 받은편지함 규칙의 동작

규칙은 조건, 예외, 동작으로 이뤄집니다. 조건 매개변수에는 `SubjectContainsWords`·`FromAddressContainsWords`·`BodyContainsWords` 같은 것이 있고, 같은 조건 앞에 `ExceptIf` 를 붙이면 예외가 됩니다(예: `ExceptIfSubjectContainsWords`)[2]. 조사에서 먼저 볼 동작은 아래와 같습니다[2].

| 동작 매개변수 | 뜻 | 조사에서 보는 이유 |
|---|---|---|
| `ForwardTo` | 받은 메일을 지정한 수신자에게 전달 | 메일 사본 유출 |
| `ForwardAsAttachmentTo` | 받은 메일을 첨부 파일로 전달 | 메일 사본 유출 |
| `RedirectTo` | 받은 메일을 지정한 수신자에게 리디렉션 | 메일 사본 유출 |
| `DeleteMessage` | 지운 편지함 (Deleted Items) 으로 보냄 | 알림·경고 메일 숨기기 |
| `SoftDeleteMessage`·`PermanentDelete` | 클라우드 서비스에서만 쓸 수 있는 매개변수 | 알림·경고 메일 숨기기 |
| `MoveToFolder` | 지정한 폴더로 옮김 | 잘 안 보는 폴더로 숨기기 |
| `MarkAsRead` | 읽음으로 표시 | 새 메일 알림 없애기 |
| `StopProcessingRules` | 이 규칙에 맞으면 다음 규칙을 처리하지 않음 | 다른 규칙 무력화 |

공개 수집 도구가 규칙을 걸러 내는 기준도 이 동작들입니다. Microsoft-Extractor-Suite 는 규칙마다 `Enabled`·`Priority`·`RuleIdentity`·`StopProcessingRules`·`MoveToFolder`·`RedirectTo`·`ForwardTo`·`ForwardAsAttachmentTo`·`MarkAsRead`·`DeleteMessage`·`SoftDeleteMessage`·`Description`·`InError` 같은 값을 뽑아 저장하고, 전달·리디렉션·삭제 규칙 수를 따로 셉니다[11]. Hawk 는 `DeleteMessage` 가 참이거나 `ForwardTo`·`ForwardAsAttachmentTo`·`RedirectTo` 가운데 하나라도 비어 있지 않은 규칙을 `_Investigate_InboxRules.csv` 로 따로 남깁니다[12].

### 메일함 전달 설정

`Set-Mailbox` 의 전달 매개변수는 세 개입니다[3].

| 매개변수 | 뜻 |
|---|---|
| `ForwardingAddress` | 조직 안 수신자로 전달. 기본값은 비어 있음($null) |
| `ForwardingSmtpAddress` | SMTP 주소로 전달. 보통 검증하지 않은 외부 주소를 넣음. 기본값은 비어 있음 |
| `DeliverToMailboxAndForward` | `$true` 면 메일함에도 넣고 전달, `$false` 면 전달만 하고 메일함에는 넣지 않음. 기본값 `$false` |

`ForwardingAddress` 와 `ForwardingSmtpAddress` 가 둘 다 있으면 `ForwardingSmtpAddress` 는 무시되고 `ForwardingAddress` 로만 전달됩니다[3]. 따라서 `ForwardingSmtpAddress` 에 외부 주소가 적혀 있어도, 같은 메일함에 `ForwardingAddress` 가 있으면 실제 전달 대상은 조직 안 수신자입니다.

### 감사 레코드

웹용 Outlook 이나 PowerShell 로 규칙과 전달을 바꾸면 통합 감사 로그에 Exchange 관리 레코드가 남습니다. 이때 `Operation` 은 실행한 cmdlet 이름이고, `ObjectId` 는 cmdlet 이 바꾼 개체 이름이며, `Parameters` 에는 cmdlet 에 넘긴 매개변수 이름과 값이 이름·값 쌍으로 들어갑니다[5]. Exchange 관리 레코드의 `ResultStatus` 는 True 나 False 이고, `ExternalAccess` 가 False 면 조직 안 사람이 실행한 것이고 True 면 데이터센터 인력·서비스 계정이나 위임 관리자가 실행한 것입니다[5]. 공통 필드는 [레코드 구조](../unified-audit-log/record-structure.md)에 있습니다.

아래는 만든 예시입니다. 사용자·주소·IP·ID 는 모두 지어낸 값입니다.

```json
{
  "CreationTime": "2026-03-02T01:14:09",
  "Id": "00000000-1111-2222-3333-444444444444",
  "Operation": "New-InboxRule",
  "RecordType": 1,
  "ResultStatus": "True",
  "UserId": "kim@contoso.com",
  "ClientIP": "203.0.113.25",
  "ExternalAccess": false,
  "Parameters": [
    { "Name": "Name", "Value": "정리" },
    { "Name": "SubjectContainsWords", "Value": "비밀번호" },
    { "Name": "DeleteMessage", "Value": "True" },
    { "Name": "MarkAsRead", "Value": "True" },
    { "Name": "StopProcessingRules", "Value": "True" }
  ]
}
```

`RecordType` 1 은 `ExchangeAdmin` 입니다[5]. 메일함 전달 변경을 찾을 때 Hawk 는 `ExchangeAdmin` 레코드 가운데 `Set-Mailbox`·`Set-MailUser`·`Set-RemoteMailbox`·`Enable-RemoteMailbox` 작업을 모은 뒤, `Parameters` 에 `ForwardingAddress`·`ForwardingSMTPAddress`·`DeliverToMailboxAndForward` 같은 이름이 있는 것만 남깁니다[12].

## 증거로서 의미

**증명하는 것**

- `Get-InboxRule`·`Get-Mailbox` 결과는 수집한 시점에 그 메일함에 걸려 있던 규칙과 전달 설정입니다.
- `New-InboxRule`·`Set-InboxRule`·`Remove-InboxRule`·`UpdateInboxRules` 레코드는 어느 계정이 어느 시각에 규칙을 만들거나 바꾸거나 지웠다는 기록이고, `Parameters` 에서 조건과 동작을 읽을 수 있습니다[5][7].
- `Set-Mailbox` 레코드의 `Parameters` 는 누가 언제 어떤 전달 주소를 넣었는지 보여 줍니다[5][12].

**증명하지 못하는 것**

- 현재 규칙 목록에는 이미 지운 규칙이 나오지 않습니다. 만들었다 지운 규칙은 감사 로그 이력으로만 찾을 수 있습니다.
- 규칙이나 전달이 설정됐다는 사실은 메일이 실제로 나갔다는 뜻이 아닙니다. 조직이 외부 자동 전달을 막았다면 전달 시도는 반송됩니다[4]. 실제 전달 여부는 [메시지 추적](message-trace.md)과 `EmailEvents` 로 확인합니다[9].
- 감사 레코드의 `UserId` 는 작업을 한 계정이지 그 자리에 앉은 사람이 아닙니다. 같은 시각의 로그인 기록은 [Entra ID 로그](../entra-logs/index.md)에서 봅니다.

보고서에는 "이 시각에 이 계정으로 외부 주소로 전달하는 받은편지함 규칙을 만든 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

감사 레코드의 `CreationTime` 은 레코드가 생긴 시각이고 UTC 입니다[5]. 레코드가 검색에 나타나기까지 걸리는 지연 시간은 [통합 감사 로그](../unified-audit-log/index.md)에서 다룹니다. 규칙을 만든 뒤 수정했다면 수정 레코드가 따로 쌓이므로, 규칙의 최종 모습은 생성 레코드 하나가 아니라 같은 규칙 이름의 레코드를 시간순으로 이어 봐야 합니다. Microsoft-Extractor-Suite 는 전송 규칙 (Transport Rule) 을 수집할 때 `WhenChanged` 값을 UTC 로 바꿔 저장합니다[11]. 클라우드 로그 시각 전반은 [클라우드 로그의 시각](../../../01-foundations/logging/timestamps.md)에 있습니다.

## 함정과 한계

**숨긴 규칙.** `Get-InboxRule` 은 `-IncludeHidden` 을 붙여야 숨긴 규칙까지 돌려줍니다[1]. Untitled Goose Tool 은 `IncludeHidden` 을 켜고 규칙을 받아 `EXO_InboxRules_PowerShell.json` 에 저장하고, Microsoft Graph 의 `/beta/users/사용자ID/mailFolders/inbox/messageRules` 로도 한 번 더 받습니다[14]. Microsoft-Extractor-Suite 와 Hawk 는 `-IncludeHidden` 없이 `Get-InboxRule -Mailbox` 를 부릅니다[11][12]. 어느 도구로 수집했는지에 따라 숨긴 규칙이 결과에서 빠질 수 있습니다.

**PowerShell 이 지우는 클라이언트 규칙.** Exchange PowerShell 로 받은편지함 규칙을 만들거나, 바꾸거나, 지우거나, 켜고 끄면 Outlook 이 비활성화한 클라이언트 쪽 규칙과 보내는 메일 규칙이 지워집니다[2]. 조사 중에 PowerShell 로 규칙을 손대면 증거가 사라지므로, 수집은 읽기 명령으로만 합니다.

**두 개의 작업 이름.** 같은 "규칙 만들기" 가 웹용 Outlook·PowerShell 에서는 `New-InboxRule` 로, Outlook 클라이언트에서는 `UpdateInboxRules` 로 남습니다[7]. 한쪽 이름만 검색하면 나머지 경로로 만든 규칙을 놓칩니다.

**외부 전달 차단.** 아웃바운드 스팸 정책의 자동 전달 설정은 `Automatic - System-controlled`·`On - Forwarding is enabled`·`Off - Forwarding is disabled` 가운데 하나이고, 기본값은 `Automatic - System-controlled` 입니다[4]. 이 값은 2021년에 새 조직과 이 값을 쓰지 않던 조직에서는 `Off` 와 같아졌지만, 이미 쓰던 조직에서는 `On` 과 같을 수 있습니다(2026년 8월 문서 기준)[4]. 끄면 외부로 가는 규칙과 메일함 전달이 모두 막히고, 보낸 사람은 `5.7.520 Access denied, Your organization does not allow external forwarding. Please contact your administrator for further assistance. AS(7555)` 반송 메시지를 받습니다[4]. 원격 도메인 설정이나 메일 흐름 규칙으로도 막을 수 있고, 한쪽이 허용하고 다른 쪽이 막으면 보통 막는 쪽이 이깁니다[4]. 조직 안 사용자끼리의 자동 전달은 이 정책과 상관이 없습니다[4]. 그래서 전달 규칙이 있었다는 사실과 외부로 메일이 나갔다는 사실은 테넌트 정책을 확인한 뒤에야 연결할 수 있습니다.

**Outlook 규칙과 사용자 지정 양식.** 규칙 동작이 응용 프로그램을 실행하거나, 규칙이 EXE·ZIP 파일이나 URL 을 가리키거나, Outlook 프로세스 ID 에서 새 프로세스가 시작되면 규칙이 악용됐을 가능성이 있습니다[6]. 사용자 지정 양식 (Custom Form) 은 `IPM.Note.이름` 형태의 자체 메시지 클래스로 저장되고, 대개 Personal Forms Library 나 받은편지함 폴더에 있습니다[6]. 이 흔적은 클라우드 쪽 규칙 목록만으로는 드러나지 않을 수 있어 사용자 PC 도 함께 봐야 합니다. PC 의 `HKEY_CURRENT_USER\Software\Microsoft\Office\16.0\Outlook\Security\` (Outlook 2013 은 `15.0`) 아래 `EnableUnsafeClientMailRules` 값이 1 이면 "응용 프로그램 시작" 동작을 막는 보안 패치가 무력화된 상태이고, 0 이면 그 동작이 꺼진 상태입니다[6]. 패치가 들어간 판은 Outlook 2016 16.0.4534.1001 이상, Outlook 2013 15.0.4937.1000 이상입니다[6].

## 직접 분석해 보기

**PowerShell 로 현재 상태 뜨기.** 조사 대상 메일함마다 아래를 실행해 결과를 파일로 남깁니다. 설정을 바꾸는 `New-`·`Set-`·`Remove-`·`Enable-`·`Disable-` 명령은 쓰지 않습니다.

```powershell
Get-InboxRule -Mailbox kim@contoso.com -IncludeHidden | Export-Clixml inboxrules_kim.xml
Get-Mailbox -Identity kim@contoso.com | Select-Object UserPrincipalName,ForwardingAddress,ForwardingSmtpAddress,DeliverToMailboxAndForward
Get-SweepRule -Mailbox kim@contoso.com
```

결과에서 `ForwardTo`·`ForwardAsAttachmentTo`·`RedirectTo` 에 조직 밖 주소가 있는 규칙, `DeleteMessage`·`SoftDeleteMessage`·`MoveToFolder`·`MarkAsRead` 를 함께 쓰는 규칙, 이름이 짧거나 의미 없는 규칙을 먼저 봅니다.

**감사 로그로 이력 찾기.** 규칙 이력은 `Search-UnifiedAuditLog -RecordType ExchangeAdmin -Operations New-InboxRule` 처럼 작업 이름으로 찾고, `Set-InboxRule`·`Remove-InboxRule` 도 같은 방식으로 찾습니다[12]. `UpdateInboxRules` 는 메일함 감사 레코드라서 `-Operations UpdateInboxRules` 로 따로 찾습니다. 받은 레코드의 `AuditData` 를 JSON 으로 풀어 `Parameters` 의 이름·값을 열로 펼치면 규칙 조건과 동작을 표로 볼 수 있습니다. 검색 명령과 한 번에 받을 수 있는 양은 [검색과 내보내기](../unified-audit-log/search-export.md)에 있습니다.

**공개 도구.** Hawk 의 `Get-HawkUserInboxRule`·`Get-HawkUserEmailForwarding`·`Get-HawkTenantAdminInboxRuleCreation`·`Get-HawkTenantAdminInboxRuleModification`·`Get-HawkTenantAdminInboxRuleRemoval`·`Get-HawkTenantAdminEmailForwardingChange` 가 현재 상태와 이력을 나눠 받습니다[12]. 전달 변경 이력은 `Simple_Forwarding_Changes.csv`·`Forwarding_Changes.csv`·`Forwarding_Recipients.csv` 로 나옵니다[12]. Microsoft-Extractor-Suite 의 `Get-MailboxRules`·`Get-TransportRules`, Untitled Goose Tool 의 Exchange 수집도 규칙을 받습니다[11][14]. 도구 설치와 인증은 [Microsoft 365 수집 도구](../../../03-techniques/acquisition/m365-collection.md)에 있습니다. 테넌트 전체에서 Outlook 규칙과 사용자 지정 양식을 뽑는 `Get-AllTenantRulesAndForms.ps1` 은 `MailboxRulesExport-yyyy-MM-dd.csv` 와 `MailboxFormsExport-yyyy-MM-dd.csv` 를 만들고, 규칙 파일에서 `ActionType` 이 `ID_ACTION_CUSTOM` 이거나 `IsPotentiallyMalicious` 가 `TRUE` 이거나 `ActionCommand` 에 응용 프로그램·EXE·ZIP·URL 이 있으면 먼저 봅니다[6]. 이 스크립트는 2021년 1월부터 보관 처리된 상태이고, 154~158행의 접속 방식은 2023년 7월부터 쓸 수 없어 그 줄을 지우고 Exchange Online PowerShell 에 먼저 접속한 뒤 실행해야 합니다[6].

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 로그인 로그 | 규칙을 만든 시각 앞뒤로 그 계정이 어디서 로그인했는지 | [Entra ID 로그](../entra-logs/index.md) |
| 위험 탐지 | `suspiciousInboxForwarding`·`mcasSuspiciousInboxManipulationRules` 발생 여부 | [Entra ID 로그](../entra-logs/index.md) |
| 메일함 감사 | 규칙 생성 전후의 메일 열람(`MailItemsAccessed`)·삭제 | [메일함 감사와 MailItemsAccessed](mailbox-auditing.md) |
| 메시지 추적 | 전달 대상 주소로 메일이 실제로 나갔는지, 반송됐는지 | [메시지 추적](message-trace.md) |
| Defender `EmailEvents` | `ForwardingInformation` 열의 전달한 사용자·전달 유형(JSON)[9] | [Defender 경고와 기록](../defender-xdr.md) |
| 경고 정책 | `eventSource` 가 `SecurityComplianceCenter`, `eventName` 이 `Suspicious inbox forwarding` 인 경고[13] | [탐지 규칙으로 로그 검색하기](../../../03-techniques/analysis/detection-rules.md) |

조직이 온프레미스 메일을 Microsoft 365 로 거쳐 보낸다면, 온프레미스에서 자동 전달된 메일은 `X-MS-Exchange-Inbox-Rules-Loop` 헤더가 있는지를 조건으로 한 메일 흐름 규칙으로 추적합니다[4]. 클라우드 계정의 자동 전달 사용자는 Auto forwarded messages 보고서에서 볼 수 있습니다[4]. 규칙 생성·로그인·메일 흐름을 한 줄로 엮는 방법은 [클라우드 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

## 실습

시험용 테넌트에서 아래 질문을 풀어 봅니다.

1. 웹용 Outlook 에서 규칙 하나, Outlook 클라이언트에서 규칙 하나를 만든 뒤, 통합 감사 로그에서 각각 어떤 작업 이름으로 남는지 찾아봅니다.
2. 숨긴 규칙이 있는 메일함에서 `Get-InboxRule` 을 `-IncludeHidden` 없이 한 번, 붙여서 한 번 실행해 결과 개수를 비교합니다.
3. 한 메일함에 `ForwardingAddress` 와 `ForwardingSmtpAddress` 를 둘 다 넣고, 메시지 추적에서 메일이 어느 주소로 갔는지 확인합니다.
4. 규칙을 만들었다가 지운 뒤, 현재 규칙 목록과 감사 로그에서 각각 무엇이 남는지 비교합니다.

## 참고 문헌

1. Microsoft, "Get-InboxRule", office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Get-InboxRule.md
2. Microsoft, "New-InboxRule", office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/New-InboxRule.md
3. Microsoft, "Set-Mailbox", office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Set-Mailbox.md
4. Microsoft Learn, "Outbound spam policies — external email forwarding" (2026-08-18 갱신). https://learn.microsoft.com/en-us/defender-office-365/outbound-spam-policies-external-email-forwarding
5. Microsoft Learn, "Office 365 Management Activity API schema" (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
6. Microsoft Learn, "Detect and remediate Outlook rules and custom forms injection attacks" (2026-07-03 갱신). https://learn.microsoft.com/en-us/defender-office-365/detect-and-remediate-outlook-rules-forms-attack
7. Microsoft Learn, "Audit log activities" (2026-09-08 갱신). https://learn.microsoft.com/en-us/purview/audit-log-activities
8. Microsoft Learn, "Manage mailbox auditing" (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-mailboxes
9. Microsoft Learn, "EmailEvents" (2026-09-02 갱신). https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-emailevents-table
10. Microsoft Learn, "What are risk detections?" (2026-04-22 갱신). https://learn.microsoft.com/en-us/entra/id-protection/concept-identity-protection-risks
11. Invictus IR, Microsoft-Extractor-Suite (Scripts/Get-Rules.ps1). https://github.com/invictus-ir/Microsoft-Extractor-Suite
12. T0pCyber, Hawk (Hawk/functions/User/Get-HawkUserInboxRule.ps1, Get-HawkUserEmailForwarding.ps1, Hawk/functions/Tenant/Get-HawkTenantAdminInboxRule*.ps1, Get-HawkTenantAdminEmailForwardingChange.ps1). https://github.com/T0pCyber/hawk
13. SigmaHQ, "Suspicious Inbox Forwarding" (rules/cloud/m365/threat_management/microsoft365_susp_inbox_forwarding.yml). https://github.com/SigmaHQ/sigma
14. CISA, Untitled Goose Tool (goosey/m365_datadumper.py). https://github.com/cisagov/untitledgoosetool
