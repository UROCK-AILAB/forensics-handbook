---
title: "주요 작업 이름"
parent: "통합 감사 로그"
grand_parent: "아티팩트 · Microsoft 365"
nav_order: 160
---

# 주요 작업 이름 (Operations)

통합 감사 로그 레코드의 `Operation` 값은 무슨 일이 있었는지를 알려 주는 첫 단서이고, 조사에서 자주 쓰는 작업 이름을 서비스별로 모아 뜻과 기록 조건을 정리합니다.

## 무엇을 기록하나

감사 레코드마다 작업 이름 (Operation) 이 하나씩 붙습니다. Purview 포털의 활동 목록에는 "Sent message" 같은 친근한 이름 (friendly name) 이 보이고, 레코드의 `Operation` 필드와 내보낸 CSV 에는 `Send` 같은 작업 이름이 들어갑니다[1]. Exchange 관리 작업은 실행한 cmdlet 이름이 곧 작업 이름이라서 `Set-Mailbox`, `New-InboxRule` 처럼 기록되고, cmdlet 에 넘긴 인자는 `Parameters` 에 남습니다[2]. 레코드의 다른 필드는 [레코드 구조](record-structure.md)에서 다루고, 작업 이름으로 거르는 방법은 [검색과 내보내기](search-export.md)에서 다룹니다.

작업 이름은 정해진 이름 그대로 넣어야 하고, 틀리게 넣으면 결과가 나오지 않습니다[7]. 아래 표의 이름은 2026년 9월 문서(2026-09-08 갱신) 기준입니다[1].

## Exchange 메일함

| 작업 이름 | 친근한 이름 | 뜻 |
|---|---|---|
| `MailItemsAccessed` | Accessed mailbox items | 메일 클라이언트가 메시지를 bind 하거나 프로토콜이 폴더를 sync 했습니다 |
| `Send` | Sent message | 메시지를 보내거나 회신·전달했습니다 |
| `SendAs` | Sent message using Send As permissions | 다른 사람이 메일함 소유자인 것처럼 보냈습니다 |
| `SendOnBehalf` | Sent message using Send On Behalf permissions | 다른 사람이 소유자를 대신해 보냈습니다 |
| `MoveToDeletedItems` | Moved messages to Deleted Items folder | 메시지를 지워 지운 편지함으로 옮겼습니다 |
| `SoftDelete` | Deleted messages from Deleted Items folder | 지운 편지함에서 지우거나 Shift+Delete 로 지워 복구 가능한 항목 (Recoverable Items) 으로 옮겼습니다 |
| `HardDelete` | Purged messages from the mailbox | 복구 가능한 항목에서도 지웠습니다 |
| `MailboxLogin` | User signed in to mailbox | 사용자가 자기 메일함에 로그인했습니다 |
| `FolderBind` | Accessed Mailbox folder | 폴더에 접근했습니다. 관리자·위임자가 메일함을 열 때도 남습니다 |
| `MessageBind` | Accessed message | 미리 보기 창에서 보거나 관리자가 열었습니다. E5·A5·G5 라이선스가 없는 사용자에게만 있습니다 |
| `AttachmentAccess` | Accessed mailbox attachments | 첨부 파일에 접근했습니다 |
| `SearchQueryInitiated` | Search items in a mailbox | Outlook(Windows·Mac·iOS·Android·웹)이나 Windows 10 메일 앱으로 메일함을 검색했습니다 |
| `New-InboxRule` | Created new inbox rule in Outlook web app | 웹용 Outlook 에서 받은편지함 규칙을 만들었습니다 |
| `Set-InboxRule` | Modified inbox rule from Outlook web app | 웹용 Outlook 에서 규칙을 바꿨습니다 |
| `UpdateInboxRules` | Updated inbox rules from Outlook client | Outlook 클라이언트에서 규칙을 만들거나 바꾸거나 지웠습니다 |
| `Add-MailboxPermission` | Added delegate mailbox permissions | 관리자가 다른 사람 메일함의 FullAccess 권한을 주었습니다 |
| `Remove-MailboxPermission` | Removed delegate mailbox permissions | FullAccess 권한을 거두었습니다 |

메시지를 만들고 보내고 받는 일은 `Create` 로 감사하지 않고, 메일함 폴더를 만드는 일도 감사하지 않습니다[1]. 메일 전송은 `Send` 계열로 남습니다[1].

`MailItemsAccessed` 는 해석할 때 묶음 규칙을 알아야 합니다. bind 는 2분 안에 일어난 것을 레코드 하나로 묶어 `Folders` 에 메시지별 `InternetMessageId` 를 넣고 묶은 개수를 `OperationCount` 에 적습니다[3]. 같은 bind 는 1시간 안이면 다시 남기지 않고 sync 도 1시간 간격으로 거릅니다[3]. 자세한 해석은 [Exchange Online](../exchange-online/index.md) 페이지에서 다룹니다.

전달 설정은 받은편지함 규칙과 별개로 Exchange 관리 작업에 남습니다. `Set-Mailbox` 레코드의 `Parameters` 에 `ForwardingSMTPAddress`·`ForwardingAddress`·`DeliverToMailboxAndForward` 가 들어 있는지 보면 됩니다[8]. 감사 기능을 끄고 켠 기록은 `Set-AdminAuditLogConfig` 로 남고, `UnifiedAuditLogIngestionEnabled` 값으로 켬과 끔을 가릅니다[6].

## SharePoint·OneDrive 파일

| 작업 이름 | 뜻 |
|---|---|
| `FileAccessed` | 사용자나 시스템 계정이 파일에 접근했습니다. 같은 사용자·같은 파일은 5분 동안 다시 남기지 않습니다 |
| `FileAccessedExtended` | 같은 사람이 오래(최대 3시간) 계속 접근할 때 `FileAccessed` 대신 남습니다 |
| `FileModified` | 내용이나 속성을 바꿨습니다. 같은 사용자·같은 문서는 5분 기다렸다가 다음 레코드를 남깁니다 |
| `FileModifiedExtended` | 같은 사람이 오래(최대 3시간) 계속 고칠 때 남습니다 |
| `FilePreviewed` | 파일을 미리 봤습니다. 이미지 갤러리 보기처럼 한 번의 동작에 많이 남습니다 |
| `FileDownloaded` | 사이트에서 문서를 내려받았습니다 |
| `FileSyncDownloadedFull` | OneDrive 동기화 앱(OneDrive.exe)으로 PC 에 파일을 받았습니다 |
| `FileUploaded` | 사이트 폴더에 문서를 올렸습니다 |
| `FileCopied` · `FileMoved` · `FileRenamed` | 복사·이동·이름 바꾸기 |
| `FileRecycled` | 파일을 SharePoint 휴지통으로 옮겼습니다 |
| `FileDeleted` | 사이트에서 문서를 지웠습니다 |
| `FileDeletedFirstStageRecycleBin` | 사이트 휴지통에서 지웠습니다 |
| `FileDeletedSecondStageRecycleBin` | 2단계 휴지통에서 지웠습니다 |
| `SearchQueryPerformed` | SharePoint 나 OneDrive 에서 검색했습니다. 보류·보존 정책을 적용하는 서비스 계정도 남기고, 기록하려면 따로 켜야 합니다 |

`FileSyncDownloadedPartial` 은 옛 동기화 앱(Groove.exe)과 함께 폐지됐습니다[1]. 파일 작업 레코드의 해석은 [SharePoint·OneDrive](../sharepoint-onedrive.md) 페이지에서 다룹니다.

## 공유

| 작업 이름 | 뜻 |
|---|---|
| `SharingSet` | 디렉터리에 있는 사용자(멤버·게스트)와 파일·폴더·사이트를 공유했습니다. `AddedToGroup` 이 흔히 함께 남습니다 |
| `SharingInvitationCreated` | 디렉터리에 없는 사용자와 공유했습니다. 공유 대상이 사이트일 때만 남습니다 |
| `SharingInvitationAccepted` | 초대를 수락해 접근 권한을 받았습니다 |
| `AnonymousLinkCreated` · `AnonymousLinkUpdated` · `AnonymousLinkRemoved` | 로그인 없이 쓰는 링크를 만들거나 바꾸거나 지웠습니다 |
| `AnonymousLinkUsed` | 익명 사용자가 링크로 접근했습니다. 신원은 모를 수 있지만 IP 주소는 남습니다 |
| `CompanyLinkCreated` · `CompanyLinkUsed` | 조직 전체 링크를 만들거나 썼습니다. 게스트는 이 링크를 쓸 수 없습니다 |
| `SecureLinkCreated` · `AddedToSecureLink` · `SecureLinkUsed` | 특정 사용자 링크를 만들고, 대상을 추가하고, 썼습니다 |
| `SharingRevoked` · `SharingInvitationRevoked` | 공유를 해제하거나 초대를 거두었습니다 |
| `AccessRequestCreated` | 권한 없는 사용자가 접근을 요청했습니다 |

상대가 디렉터리에 게스트 계정으로 있으면 SharePoint 가 곧바로 상대를 SharePoint 그룹에 넣으면서 `AddedToGroup` 을 남기고, 디렉터리에 없으면 초대를 보내는데 이때 `SharingInvitationCreated` 는 공유 대상이 사이트일 때만 남습니다[5]. 특정 사용자 링크로 공유한 상대는 `AddedToSecureLink` 레코드의 `TargetUserOrGroupName` 에 들어 있습니다[5]. 외부 사용자가 특정 사용자 링크로 파일을 열면 `FileAccessed` 가 남으므로, 외부 공유를 찾을 때는 `TargetUserOrGroupType` 이 `Guest` 인 레코드부터 거르면 됩니다[5].

## Teams

| 작업 이름 | 친근한 이름 | 기록 조건 |
|---|---|---|
| `TeamCreated` · `TeamDeleted` | Created team · Deleted team | |
| `MemberAdded` · `MemberRemoved` | Added members · Removed members | 연합 채팅은 참여한 모든 테넌트에 남습니다 |
| `MessageSent` | Posted new message | 공개 미리 보기이고, 채팅은 게스트·연합·익명 사용자가 있을 때만 남습니다 |
| `MessageRead` · `MessagesListed` · `ChatRetrieved` · `MessageUpdated` · `MessageHostedContentRead` | Read a message 등 | Microsoft Graph API 로 했을 때만 남고 Teams 클라이언트에서 한 일은 남지 않습니다 |
| `ChatCreated` | Created a chat | Graph API 로 했을 때만 남습니다 |
| `MessageDeleted` | Deleted a message | Audit (Premium) 전용입니다 |
| `MeetingDetail` · `MeetingParticipantDetail` | Added details about Teams meeting 등 | 참가자 기록은 이제 참가한 테넌트에도 공유됩니다 |

에이전트·봇과 한 활동은 감사 레코드가 남지 않습니다[1]. Entra ID·Microsoft 365 관리 센터·Groups Graph API 로 팀 멤버를 바꾸면 Teams 감사 레코드에는 실제 작업자가 아니라 기존 팀 소유자가 작업자로 보입니다[9]. 메시지 본문을 찾는 방법은 [Teams](../teams.md) 페이지에서 다룹니다.

## Entra ID 와 그 밖의 작업

Entra 로그인은 통합 감사 로그에도 `UserLoggedIn` 과 `UserLoginFailed` 로 들어오고, 실패 사유는 `ErrorCode`(AADSTS 코드, 0 이면 성공)와 `LogonError` 에 있습니다[1][2]. 로그인 레코드의 `ResultStatus` 가 `Succeeded` 여도 HTTP 요청이 성공했다는 뜻일 뿐 로그인 성공은 아니라서, `LogonError` 를 함께 봐야 합니다[2]. 로그인 자체를 깊게 볼 때는 [Entra ID 로그](../entra-logs/index.md)를 씁니다.

공개 탐지 규칙에서 MFA 해제는 작업 이름에 `Disable Strong Authentication.` 이 들어가는지로 찾고, 메일 위협 판정은 `Workload` 가 `ThreatIntelligence` 이고 `Operation` 이 `TIMailData` 인 레코드로 찾습니다[10]. 페더레이션 도메인 추가는 Exchange 관리 작업 `Add-FederatedDomain` 으로 찾습니다[10].

eDiscovery 작업은 `CaseAdded`, `CaseUpdated`, `CaseClosed`, `HoldCreated`, `HoldUpdated`, `ReviewSetCopied` 처럼 사례·보류 단위로 남습니다[1]. 조사자가 한 검색·보류도 여기에 남으니 [Purview eDiscovery와 보존](../purview-ediscovery.md)에서 수집 경위와 함께 봅니다.

## 기본으로 남지 않거나 조건이 붙는 작업

| 작업 | 조건 |
|---|---|
| `FolderBind`, `MailboxLogin`, `SearchQueryInitiated`, `Copy`, `Move` | 메일함 감사의 기본 작업 목록에 없어 관리자가 켜야 남습니다[4] |
| `MessageBind` | E5·A5·G5 가 없는 사용자에게만 있습니다[1][4] |
| `MailItemsAccessed` | Audit (Standard) 기능이고 E3·E5 사용자에게 기본으로 켜집니다(2026-06-24 문서 기준)[3] |
| `MessageDeleted`(Teams) | Audit (Premium) 전용입니다[1] |
| Teams 메시지 읽기 계열 | Graph API 로 했을 때만 남습니다[1] |

메일함마다 실제로 켜진 작업은 Exchange Online PowerShell 에서 `Get-Mailbox -Identity 대상 | Format-List DefaultAuditSet` 과 `Select-Object -ExpandProperty AuditOwner`(AuditDelegate·AuditAdmin 도 같음)로 확인합니다[4]. 작업 목록을 사용자 지정하면 새 기본 작업이 자동으로 더해지지 않습니다[4].

## 증거로서 의미

**증명하는 것.** 이 테넌트의 서비스가 이 시각에 이 계정으로 이 작업을 처리했다는 사실입니다. 예를 들어 `FileDownloaded` 는 서비스가 그 파일을 내려보냈다는 뜻이고, `AnonymousLinkUsed` 는 그 IP 주소에서 익명 링크로 접근했다는 뜻입니다[1].

**증명하지 못하는 것.** 사람이 내용을 실제로 읽었는지는 알 수 없습니다. `MailItemsAccessed` 의 sync 레코드는 폴더 단위로 남아 폴더 안 메시지를 하나하나 열었는지 알려 주지 않고, 동기화로 내려받은 뒤 오프라인에서 읽은 것은 감사하지 못합니다[3]. 내려받은 파일을 기기에서 어떻게 썼는지, Teams 클라이언트에서 메시지를 읽었는지도 이 로그로는 알 수 없습니다[1]. 작업 이름이 없다고 그 일이 없었다고 말할 수도 없는데, 기본 작업 목록 밖이거나 라이선스 조건에 걸리거나 감사가 꺼져 있었을 수 있기 때문입니다[4][6].

## 시각 해석

작업 레코드의 `CreationTime` 은 UTC 이고, 기록 지연과 수집 경로별 시각 필드 차이는 [레코드 구조](record-structure.md)와 [검색과 내보내기](search-export.md)에서 다룹니다. 작업 이름별로 신경 쓸 것은 묶음 규칙입니다. `FileAccessed`·`FileModified` 는 5분, `MailItemsAccessed` bind 는 2분 묶음과 1시간 중복 제거, 위임자의 `FolderBind` 는 24시간에 폴더당 한 건이라서, 레코드 시각은 첫 접근 시각에 가깝고 그 뒤 반복된 접근은 시각이 따로 남지 않을 수 있습니다[1][3].

## 함정과 한계

- 레코드 수를 접근 횟수로 읽으면 안 됩니다. 5분·2분·1시간·24시간 묶음 규칙 때문에 실제 접근이 더 많을 수 있습니다[1][3].
- 검색 관련 작업 이름은 출처마다 다릅니다. Microsoft 의 감사 활동 목록은 메일함 검색을 `SearchQueryInitiated`, SharePoint 검색을 메일함 표에서 `SharepointSearchQueryInitiated`, 파일 표에서 `SearchQueryPerformed` 로 적었고[1], Hawk 는 `SearchQueryInitiatedExchange`·`SearchQueryInitiatedSharePoint` 로 조회합니다[8]. 받은 데이터에서 실제 `Operation` 값을 먼저 뽑아 보고 거르면 됩니다.
- `Add-MailboxPermission` 의 작업자가 `NT AUTHORITY\SYSTEM` 이나 `NT SERVICE\MSExchangeAdminApiNetCore(Microsoft.Exchange.AdminApi.NetCore)` 이면 Exchange 서비스의 예약 유지보수이고, `Administrator@apcprd03.prod.outlook.com` 은 Microsoft 지원 인력의 진단 도구 실행과 관련이 있습니다[1].
- `UpdateInboxRules` 는 Outlook 클라이언트에서 만든 규칙·바꾼 규칙·지운 규칙을 한 작업 이름으로 남깁니다[1]. 현재 규칙 목록과 대조해야 무엇이 바뀌었는지 가릴 수 있습니다.
- 메일함 감사 우회(`Set-MailboxAuditBypassAssociation`)가 걸린 사용자는 메일함 작업이 남지 않습니다[4].

## 직접 분석해 보기

Exchange Online PowerShell 에서 작업 이름 여러 개를 한 번에 거를 수 있습니다. 시간대 없이 준 날짜는 UTC 로 해석하고, `-ResultSize` 는 최대 5,000 입니다[11].

```powershell
# 만든 예시: 사용자와 기간은 지어낸 값
Search-UnifiedAuditLog -StartDate "2026-09-01 00:00:00z" -EndDate "2026-09-02 00:00:00z" `
  -UserIds user1@contoso.com `
  -Operations New-InboxRule,Set-InboxRule,UpdateInboxRules,Set-Mailbox,Add-MailboxPermission `
  -ResultSize 5000
```

`MailItemsAccessed` 는 sync 와 bind 를 `AuditData` 문자열로 가를 수 있습니다[3].

```powershell
Search-UnifiedAuditLog -StartDate "2026-09-01 00:00:00z" -EndDate "2026-09-02 00:00:00z" `
  -UserIds user1@contoso.com -Operations MailItemsAccessed -ResultSize 5000 |
  Where-Object { $_.AuditData -like '*"MailAccessType","Value":"Sync"*' }
```

작업 이름 목록을 모를 때는 기간을 좁혀 전체를 받은 뒤 `Operation` 값별 개수부터 셉니다. 수집 도구 쪽 방법은 [검색과 내보내기](search-export.md)를 봅니다.

## 교차 검증

| 작업 | 함께 볼 기록 |
|---|---|
| `New-InboxRule`·`UpdateInboxRules`·`Set-Mailbox` | 현재 받은편지함 규칙과 메일함 전달 설정, 메시지 추적 — [Exchange Online](../exchange-online/index.md) |
| `UserLoggedIn`·`UserLoginFailed` | Entra 로그인 로그 — [Entra ID 로그](../entra-logs/index.md) |
| `FileDownloaded`·`FileSyncDownloadedFull` | 내려받은 PC 의 OneDrive 클라이언트 흔적 — [SharePoint·OneDrive](../sharepoint-onedrive.md) |
| Teams 멤버 변경 | Entra·Microsoft 365 그룹 감사 기록 — [Teams](../teams.md) |
| `Set-AdminAuditLogConfig` | 감사가 꺼져 있던 기간 — [통합 감사 로그](index.md) |

## 참고 문헌

1. Microsoft, "Audit log activities", Microsoft Learn (2026-09-08 갱신). https://learn.microsoft.com/en-us/purview/audit-log-activities
2. Microsoft, "Office 365 Management Activity API schema", Microsoft Learn (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
3. Microsoft, "Use MailItemsAccessed to investigate compromised accounts", Microsoft Learn (2026-06-24 갱신). https://learn.microsoft.com/en-us/purview/audit-log-investigate-accounts
4. Microsoft, "Manage mailbox auditing", Microsoft Learn (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-mailboxes
5. Microsoft, "Use sharing auditing in the audit log", Microsoft Learn (2026-06-24 갱신). https://learn.microsoft.com/en-us/purview/audit-log-sharing
6. Microsoft, "Turn auditing on or off", Microsoft Learn (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-enable-disable
7. Microsoft, "Search the audit log", Microsoft Learn (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-search
8. T0pCyber, Hawk (Get-HawkTenantAdminEmailForwardingChange, Get-HawkUserExchangeSearchQuery, Get-HawkUserSharePointSearchQuery). https://github.com/T0pCyber/hawk
9. Microsoft, "Search the audit log for events in Microsoft Teams", Microsoft Learn (2026-04-14 갱신). https://learn.microsoft.com/en-us/purview/audit-teams-audit-log-events
10. SigmaHQ, Sigma 탐지 규칙 (rules/cloud/m365/audit, rules/cloud/m365/exchange). https://github.com/SigmaHQ/sigma
11. Microsoft, "Search-UnifiedAuditLog", Exchange PowerShell 문서. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Search-UnifiedAuditLog.md
