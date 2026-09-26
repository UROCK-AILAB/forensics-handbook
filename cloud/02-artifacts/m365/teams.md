---
title: "Teams"
parent: "아티팩트 · Microsoft 365"
nav_order: 260
---

# Teams (Teams)

## 한 줄 요약

Microsoft Teams 조사는 세 곳을 봅니다. 팀·채널·멤버·앱을 바꾼 기록은 통합 감사 로그 (Unified Audit Log) 에 RecordType 25 `MicrosoftTeams` 로 남고, 메시지 본문은 Exchange 메일함의 숨은 폴더와 Teams 내보내기 API (Teams Export APIs) 로 찾으며, 기기에는 Teams 앱의 로그와 데이터베이스가 남습니다[1][3][6][7][12].

## 무엇을 기록하나 · 왜 생기나

Teams 기록은 성격이 다른 세 갈래로 나뉩니다.

첫째는 **감사 레코드**입니다. 팀을 만들고 지운 일, 채널을 더하고 지운 일, 채널 설정을 바꾼 일이 통합 감사 로그에 남고, 비공개 채널 (private channel) 에서 일어난 일도 표준 채널과 똑같이 남습니다[1]. 감사 레코드는 누가 무엇을 바꿨는지를 알려 주고, 메시지 본문은 담지 않습니다.

둘째는 **메시지 사본**입니다. Teams 메시지의 1차 저장소는 Azure 기반 채팅 서비스이고, 규정 준수 기능을 위해 Exchange 메일함에 사본을 둡니다[6]. 채팅은 채팅에 참여한 사용자마다 그 사람 메일함의 숨은 폴더에, 채널 메시지는 그룹 메일함의 비슷한 숨은 폴더에 들어갑니다[6]. 이 폴더는 사용자나 관리자가 직접 여는 곳이 아니고, eDiscovery 도구로 검색하는 곳입니다[6]. 보류·보존과 eDiscovery 전반은 [Purview eDiscovery와 보존](purview-ediscovery.md) 에서 다룹니다.

셋째는 **기기의 흔적**입니다. Teams 앱은 사용자 프로필 아래에 데이터베이스와 실행 로그를 남기고, 여기에 주고받거나 열어 본 파일의 이름·경로·시각이 들어갑니다[12].

## 위치와 버전별 차이

### 기록이 사는 곳

| 기록 | 위치 | 꺼내는 방법 |
|---|---|---|
| 감사 레코드 | 통합 감사 로그, RecordType 25 `MicrosoftTeams`. 관리 작업은 57 `MicrosoftTeamsAdmin`[3] | Purview 감사 검색, `Search-UnifiedAuditLog`, 관리 활동 API[1][9] |
| 채팅 메시지 사본 | 참여 사용자 메일함의 숨은 폴더[6] | eDiscovery, 내보내기 API[6][7] |
| 채널 메시지 사본 | 그룹 메일함의 숨은 폴더[6] | eDiscovery, 내보내기 API[6][7] |
| 고치거나 지운 메시지 원본 | 메일함의 숨은 폴더 `SubstrateHolds`[6] | eDiscovery[6] |
| 채팅에 올린 파일, 회의 녹화·녹취 | SharePoint 사이트와 주최자 OneDrive[6] | [SharePoint·OneDrive](sharepoint-onedrive.md) 쪽의 방법 |
| 앱 로그·데이터베이스 | 사용자 PC 의 Teams 앱 폴더[12] | 디스크 이미지나 파일 수집 |

메시지 사본을 담는 메일함은 `RecipientTypeDetails` 값으로 구분합니다[6].

| RecipientTypeDetails | 담는 메시지 |
|---|---|
| `UserMailbox` | 클라우드 사용자의 채팅, 저장 위치를 옮기기 전의 비공개 채널 메시지 |
| `MailUser` | 온프레미스 사용자의 채팅 |
| `GroupMailbox` | 표준 채널 메시지, 저장 위치를 옮긴 뒤의 비공개 채널 메시지 |
| `SubstrateGroup` | 공유 채널 (shared channel) 메시지 |

2025년 말 무렵부터 비공개 채널 메시지의 저장 위치가 사용자 메일함에서 그룹 메일함으로 바뀝니다[6]. 그래서 같은 비공개 채널이라도 옮기기 전 메시지는 참여자 메일함에서, 옮긴 뒤 메시지는 그룹 메일함에서 찾습니다. 회의실용 `RoomMailbox` 같은 다른 메일함 종류는 Teams 보존 정책 대상이 아닙니다[6].

### 라이선스에 따른 차이 (2026년 9월 문서 기준)

| 항목 | Audit (Standard) | Audit (Premium) |
|---|---|---|
| `MessageDeleted`(메시지 삭제) | 남지 않습니다 | 남습니다[2] |
| `MessagesExported`(메시지 내보내기) | 남지 않습니다 | Graph API 로 내보냈을 때 남습니다[2] |
| `AppAccessContext`, `MessageSent` 의 `ParticipantInfo`·`ParticipatingDomainInformation`, `MeetingParticipantDetail` 의 `IsJoinedFromLobby`·`ArtifactShared` | 들어가지 않습니다 | 들어갑니다[5] |
| 감사 레코드 기본 보관 | 180일[5] | 180일. Premium 의 기본 1년 보관 정책은 Workload 가 AzureActiveDirectory·Exchange·OneDrive·SharePoint 인 레코드만 덮습니다[5] |

Premium 기능은 조직이 아니라 사용자에게 라이선스를 할당해야 레코드가 생깁니다[5]. Teams 레코드를 180일보다 길게 두려면 사용자 지정 감사 로그 보존 정책을 만들어야 하고, 10년 보관은 사용자별 추가 라이선스가 있어야 합니다[5]. 보관 기간 전체 표와 확인 방법은 [통합 감사 로그](unified-audit-log/index.md) 에 있습니다.

Teams 통화 기록 (call logs) 은 기본으로 무기한 남고, 보존 정책으로만 지울 수 있습니다[6].

## 구조

### 감사 레코드의 Teams 필드

Teams 감사 레코드는 공통 스키마 위에 아래 필드를 더합니다[3][4]. 공통 필드(CreationTime·UserId·UserType 등)는 [레코드 구조](unified-audit-log/record-structure.md) 에서 다룹니다.

| 필드 | 뜻 |
|---|---|
| `TeamName` · `TeamGuid` | 팀 이름과 팀 ID[3] |
| `ChannelName` · `ChannelGuid` · `ChannelType` | 채널 이름·ID·종류(Standard/Private)[3] |
| `Members` | 팀에 더하거나 뺀 사용자 목록[4]. 항목마다 `UPN`·`Role`·`DisplayName`[3] |
| `AddOnName` · `AddOnGuid` · `AddOnType` | 봇·커넥터·탭 같은 추가 기능. `AddOnType` 은 1 봇, 2 커넥터, 3 탭[3][4] |
| `TabType` | 탭 종류. `Wordpin`, `Sharepointfiles`, `Webpage`, `Extension` 등[4] |
| `MessageId` · `MessageURLs` · `MessageSizeInBytes` | 메시지 ID, 메시지에 들어 있던 URL, UTF-16 기준 메시지 크기[3] |
| `Messages` | 메시지 모음. 항목마다 `Id`, `ChatThreadId`, `ChatName`, `ParentMessageId`, `TeamGuid`, `ChannelGuid`, `SizeInBytes` 등[3] |
| `HostedContents` | 메시지 안의 이미지·코드 조각 같은 호스팅 콘텐츠 ID 와 크기[2][3] |
| `Name` · `OldValue` · `NewValue` | 설정 이벤트에서 바꾼 설정 이름과 전후 값[3] |
| `Organizer` · `CallId` | 회의·통화 주최자와 통화 ID[3] |
| `SubscriptionId` | Graph 변경 알림 구독 ID[3] |
| `AppAccessContext` | 작업을 한 사용자·서비스 주체의 앱 문맥[4] |
| `ParticipantInfo` · `ParticipatingDomainInformation` | 참여자 신원과 참여자 도메인 정보[4] |

`Members` 의 `Role` 값은 문서마다 다릅니다. 감사 속성 문서와 작업 목록의 `MemberRoleChanged` 설명은 1 멤버, 2 소유자, 3 게스트로 적고[2][4], 관리 활동 API 스키마는 0 멤버, 1 소유자, 2 게스트로 적습니다[3]. 그래서 숫자 하나로 역할을 단정하지 말고, 같은 테넌트에서 역할을 이미 아는 사용자(예: 팀을 만든 소유자)의 값과 맞춰 본 뒤 해석합니다.

### 팀·채널·앱 작업

메시지·멤버 작업의 기록 조건은 [주요 작업 이름](unified-audit-log/operations.md#teams) 에 정리되어 있습니다. 아래는 그 표에 없는 Teams 작업 가운데 조사에 자주 쓰는 것입니다[2].

| 작업 이름 | 친근한 이름 | 남는 때 |
|---|---|---|
| `TeamsSessionStarted` | User signed in to Teams | Teams 클라이언트에 로그인할 때. 토큰을 새로 고치는 일은 남지 않습니다 |
| `ChannelAdded` · `ChannelDeleted` | Added channel · Deleted channel | 채널을 만들거나 지울 때 |
| `MemberRoleChanged` | Changed role of members in team | 팀 소유자가 멤버 역할을 바꿀 때 |
| `TeamSettingChanged` | Changed team setting | 팀 소유자가 공개·비공개, 이름, 설명 등을 바꿀 때 |
| `TeamsTenantSettingChanged` | Changed organization setting | 관리자가 조직 전체 Teams 설정을 바꿀 때 |
| `BotAddedToTeam` · `ConnectorAdded` · `TabAdded` | Added bot to team 등 | 팀에 봇을, 채널에 커넥터·탭을 더할 때 |
| `AppInstalled` · `AppPublishedToCatalog` | Installed app · Published app | 앱을 설치하거나 카탈로그에 올릴 때 |
| `MessageCreatedHasLink` · `MessageEditedHasLink` | Sent a message with a URL link in Teams 등 | URL 이 든 메시지를 보내거나 고칠 때 |
| `MessageReadReceiptReceived` | Received Read Receipt on a message | 읽음 확인을 받을 때. 채팅 스레드와 어디까지 읽었는지가 들어갑니다 |
| `MessagesExported` | Exported messages | Graph API 로 메시지를 내보낼 때(Premium) |
| `SubscribedToMessages` | Subscribed to message change notifications | 앱이 Graph 로 메시지 변경 알림을 구독할 때 |
| `CallParticipantDetail` | Added information about call participants | 통화 참여자, 참여·퇴장 시각, 연결 정보. 참여한 모든 테넌트에 남습니다 |
| `InviteSent` · `InviteeResponded` | Sent invitation for shared channel 등 | 공유 채널 초대를 보내거나 응답할 때(공개 미리 보기) |
| `TeamsImpersonationDetected` · `SecurityRiskInCallDetected` | Detected impersonation attempt 등 | 외부 발신자·통화에서 사칭 위험을 감지할 때 |

`MeetingParticipantDetail` 에는 참가자별 참여·퇴장 시각과 녹화 시작·중지 시각이 들어가고, 화면 공유를 누가 언제 시작하고 멈췄는지, 제어권을 누가 요청하고 수락했는지도 들어갑니다[2].

### 내보내기 API 로 받은 메시지

내보내기 API 는 1:1 채팅, 그룹 채팅, 회의 채팅, 채널 메시지를 Graph 의 `chatMessage` 형식으로 돌려줍니다[7]. 메시지마다 `id`, 답글 관계를 나타내는 `replyToId`, `from`, `messageType`, `createdDateTime`, `lastModifiedDateTime`, `deletedDateTime`, `subject`, `body`, `chatId`, `attachments`, `mentions` 가 있습니다[7]. 첨부 파일은 메타데이터로 들어가고 본문 안에 링크로 들어가는 경우도 있어서, 파일을 찾을 때는 본문 URL 이 아니라 `attachments` 모음을 씁니다[7].

"사용자 A 가 사용자 B 를 채팅에 추가하고 기록을 공유했다" 같은 시스템 메시지인 제어 메시지 (control message) 도 시각과 함께 받을 수 있지만, 회의와 관련된 제어 메시지는 받을 수 없습니다[7]. 반응(하트·좋아요 등)과 반응을 바꾼 이력도 들어갑니다[7]. 조직에 Teams 보존 정책이 걸려 있으면 채팅과 공개·공유 채널 게시물의 편집 이력까지 받을 수 있습니다[7].

## 증거로서 의미

**증명하는 것.** 감사 레코드는 이 계정으로 이 팀·채널에 이 작업(멤버 추가, 설정 변경, 앱 설치 등)을 한 기록이 서비스에 남았다는 사실을 보여 줍니다[2][3]. `MeetingParticipantDetail`·`CallParticipantDetail` 은 어떤 사용자 ID 가 회의·통화에 언제 들어오고 나갔는지를 보여 줍니다[2]. `MessageRead`·`MessagesListed` 같은 읽기 작업은 Graph API 로 메시지를 가져간 기록이라서, 앱이나 스크립트가 대화를 대량으로 가져간 흔적을 찾을 때 씁니다[2]. 메일함의 메시지 사본과 `SubstrateHolds` 는 앱에서 사라진 메시지의 원본과 고치기 전 내용을 보여 줍니다[6].

**증명하지 못하는 것.** Teams 클라이언트에서 메시지를 읽은 일은 감사 로그에 남지 않으므로, 읽기 레코드가 없다고 해서 사람이 대화를 보지 않았다고 할 수 없습니다[2]. `MessageSent` 는 게스트·연합·익명 사용자가 있는 채팅에서만 남으므로, 조직 내부 채팅에서 메시지를 보낸 사실은 감사 로그가 아니라 메시지 사본으로 확인합니다[2]. Entra ID·Microsoft 365 관리 센터·Groups Graph API 로 멤버를 바꾸면 Teams 감사 레코드와 General 채널에는 실제로 바꾼 사람이 아니라 기존 팀 소유자가 작업자로 보이므로, 멤버 변경의 작업자는 Entra ID 나 Microsoft 365 그룹 감사 로그에서 확인합니다[1]. 에이전트·봇과 주고받은 활동은 감사 레코드가 남지 않습니다[2].

보고서에는 "이 시각에 이 계정이 이 팀에 이 사용자를 게스트로 추가한 감사 기록이 있다" 처럼 레코드가 말하는 만큼만 씁니다.

## 시각 해석

감사 레코드의 `CreationTime` 은 UTC 이고 레코드가 만들어진 시각입니다[3]. Teams 같은 핵심 서비스의 레코드는 보통 일이 일어나고 60~90분 뒤에 검색되고, Microsoft 는 특정 시간을 보장하지 않습니다[8]. 그래서 방금 일어난 일을 찾을 때는 몇 시간 뒤에 다시 검색합니다. `Search-UnifiedAuditLog` 의 `-StartDate`·`-EndDate` 에 시간대 없이 값을 넣으면 UTC 로 해석합니다[9].

내보내기 API 문서의 날짜 필터 예시는 `lastModifiedDateTime` 에 끝이 `Z` 인 UTC 값을 넣습니다[7]. 날짜 필터는 `lastModifiedDateTime` 으로 걸기 때문에, 기간을 정해 내보내면 그 기간에 만들었거나 고친 메시지가 함께 나옵니다[7]. 응답의 메시지 순서는 어떤 시각 기준으로도 정렬되어 있다고 보장하지 않으므로, 받은 뒤 직접 정렬합니다[7].

사용자를 채팅에 새로 추가하면 그 사람과 공유한 메시지 사본이 그 사람 메일함에 들어가지만, 메시지의 생성 날짜는 바뀌지 않고 모든 사용자에게 같습니다[6]. 따라서 한 사용자의 메일함에 있는 메시지의 생성 날짜가 그 사용자가 채팅에 들어온 날보다 앞서도 이상한 일이 아닙니다.

앱 로그의 시각이 UTC 인지 현지 시각인지는 검체의 로그 줄과 PC 시간대 설정을 대조해 정합니다. 클라우드 기록과 기기 기록을 한 줄로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 을 봅니다.

## 함정과 한계

- **앱 화면은 보존 상태를 반영하지 않습니다.** 사용자가 메시지를 지우면 앱에서는 바로 사라지지만, 보존 정책이 걸려 있으면 21일 동안은 `SubstrateHolds` 로 옮겨지지 않고, 옮겨진 뒤에도 최소 1일은 남습니다[6]. Litigation Hold·eDiscovery 보류나 같은 위치의 다른 Teams 보존 정책이 걸린 메일함에서는 `SubstrateHolds` 의 영구 삭제가 멈추고, 앱에 보이지 않는 메시지도 eDiscovery 로 찾을 수 있습니다[6].
- **보존 정책 타이머 작업은 한 번 도는 데 보통 1~7일이 걸립니다.** "1일 뒤 삭제" 정책이라도 eDiscovery 검색에서 사라지기까지 16일이 걸릴 수 있습니다[6].
- **보존 정책이 지운 메시지는 대화의 모든 사용자 앱에서 사라집니다.** 다른 조직 사용자처럼 보존 기간이 더 긴 사람도 앱에서는 볼 수 없지만, 그 사람 메일함의 사본은 남아 있을 수 있습니다[6].
- **보존 정책이 담지 않는 것이 있습니다.** 코드 조각, 모바일 앱의 음성 메모, 썸네일, 공지 이미지, 이모티콘 반응은 Teams 보존 정책으로 남지 않습니다[6]. Teams 에서 주고받은 메일과 파일도 Teams 보존 정책 대상이 아니고, 사용자 채팅의 파일과 회의 녹화·녹취는 주최자 OneDrive 를 위치로 넣은 정책이 있어야 합니다[6].
- **외부 사용자의 메시지는 다른 곳에 있습니다.** 게스트 계정으로 들어온 외부 사용자의 메시지는 조직 사용자 메일함과 게스트 계정의 그림자 메일함 (shadow mailbox) 에 함께 들어가고, 그림자 메일함에는 보존 정책이 적용되지 않습니다[6]. 다른 Microsoft 365 조직 계정으로 들어온 사용자의 사본은 그 조직 메일함에 있습니다[6].
- **내보내기 API 로 받을 수 있는 기간이 짧습니다.** 사용자가 지운 메시지는 지운 뒤 21일까지, 지운 팀·채널과 지운 사용자·비활성 사용자의 메시지는 30일까지 받을 수 있습니다[7]. 30일이 지난 팀·채널은 완전히 지워져 메시지를 받을 수 없습니다[7].
- **감사는 켠 뒤부터만 남습니다.** 감사를 켜기 전의 Teams 활동은 검색되지 않습니다[1]. 감사 켜짐 여부와 끄고 켠 기록을 확인하는 방법은 [통합 감사 로그](unified-audit-log/index.md) 에 있습니다.
- **포털 검색 결과가 5,000건이면 더 있을 수 있습니다.** 결과가 5,000건이면 더 있다고 보고 조건을 좁혀 다시 검색하거나 전체 결과를 내려받습니다[1].
- **정부 클라우드는 작업마다 사정이 다릅니다.** `MeetingDetail`·`MeetingParticipantDetail` 은 GCC·GCC High·DoD·에어갭 환경에서도 남는 작업으로 표시되어 있으므로, 정부 클라우드 테넌트에서는 작업 목록의 각주를 함께 봅니다[2].

## 직접 분석해 보기

### 감사 레코드 한 건 따라가기

아래는 게스트를 팀에 추가한 `MemberAdded` 레코드를 스키마에 맞춰 만든 예시입니다. 이름·ID·주소는 모두 지어낸 값입니다.

```json
{
  "CreationTime": "2026-03-02T01:15:42",
  "Id": "5f3c2a10-0000-4000-8000-000000000001",
  "Operation": "MemberAdded",
  "OrganizationId": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
  "RecordType": 25,
  "UserId": "owner@contoso.com",
  "UserType": 0,
  "Members": [
    { "UPN": "partner@example.com", "Role": 3, "DisplayName": "Partner User" }
  ],
  "TeamName": "Project Falcon",
  "TeamGuid": "0f1e2d3c-4b5a-4968-8776-655443322110",
  "ChannelName": "General"
}
```

읽는 순서는 이렇습니다. `RecordType` 25 로 Teams 레코드인지 확인하고[3], `Operation` 으로 멤버 추가임을 봅니다[2]. `CreationTime` 은 UTC 이므로 현지 시각으로 옮길 때는 시간대를 더합니다[3]. `UserId` 가 실제로 멤버를 추가한 사람인지는 같은 시각 전후의 Entra ID 감사 로그와 Microsoft 365 그룹 감사 기록을 보고 판단합니다. 관리 도구로 바꿨다면 여기에는 기존 소유자가 나오기 때문입니다[1]. `Members` 의 `Role` 이 3 이면 감사 속성 문서 기준으로 게스트이고, 관리 활동 API 스키마 기준으로는 정의되지 않은 값이므로, 앞의 "구조" 절처럼 같은 테넌트의 다른 레코드와 맞춰 봅니다[3][4]. UPN 의 도메인이 조직 도메인과 다르면 외부 사용자를 들인 기록입니다.

### 공개 도구

**감사 레코드.** Exchange Online PowerShell 에서 `Search-UnifiedAuditLog -RecordType MicrosoftTeams` 로 Teams 레코드만 뽑고, `-Operations MemberAdded,MemberRoleChanged` 처럼 작업 이름을 좁힙니다[9]. Microsoft-Extractor-Suite 의 `Get-UAL` 은 `-RecordType` 으로 기록 종류를 고르며, 미리 묶어 둔 `-Group` 은 Exchange·Azure·Sharepoint·Skype·Defender 뿐이라 Teams 는 `-RecordType MicrosoftTeams` 로 따로 지정합니다[10]. DFIR-O365RC 의 `Get-O365Light` 에서 `-operationsSet OneDrive_Sharepoint_Teams_YammerOnly` 를 고르면 Teams 작업으로는 `TeamSettingChanged`·`TeamsTenantSettingChanged`·`MemberRoleChanged`·`AppInstalled` 만 가져오고 `MemberAdded`·`MessageSent` 는 목록에 없으므로, 멤버·메시지 조사에는 전체 레코드를 따로 받습니다[11]. 수집 도구를 고르는 기준은 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md) 에서 다룹니다.

**메시지.** 내보내기 API 는 사용자 채팅과 팀 채널을 아래처럼 요청하고, `lastModifiedDateTime` 으로 기간을 거릅니다[7]. 애플리케이션 권한 `Chat.Read.All`(채팅), `ChannelMessage.Read.All`(채널), `User.Read.All`(사용자 목록)을 관리자가 승인해야 하고, 내보낼 사용자에게 Teams 라이선스가 있어야 합니다[7]. `$top` 은 250 이하로 권장하고, 응답에 `@odata.nextLink` 가 있으면 끝날 때까지 이어서 요청합니다[7].

```
GET https://graph.microsoft.com/v1.0/users/{id}/chats/getAllMessages?$top=50&$filter=lastModifiedDateTime gt 2026-03-01T00:00:00Z and lastModifiedDateTime lt 2026-03-08T00:00:00Z
GET https://graph.microsoft.com/v1.0/teams/{id}/channels/getAllMessages
```

내보내기 API 로 메시지를 가져가면 `MessagesExported` 감사 레코드가 남을 수 있으므로(Premium), 조사 중 수집한 기록과 다른 사람이 가져간 기록을 구분하려면 수집한 계정·앱과 시각을 적어 둡니다[2]. 보존 정책과 보류로 남은 사본까지 찾을 때는 eDiscovery 를 씁니다([Purview eDiscovery와 보존](purview-ediscovery.md)).

**기기.** Windows 에서 Teams 앱은 `%UserProfile%/AppData/Local/Packages/MicrosoftTeams/_[random]/LocalCache/Microsoft/MSTeams` 와 `~/MSTeams/Logs` 아래에 `Launcher_[date]_[time].log`, `MSTeams_[date]_[time].log` 를 남기고, 두 로그에는 파일 이름·파일 경로·시각이 들어갑니다[12]. `app_settings.json` 에는 처음 실행한 시각 같은 앱 설정과, Teams 로 마지막에 연 문서의 파일 이름·경로가 들어갑니다[12]. Teams 데이터는 IndexedDB 의 `[random].ldb`·`[random].log` 에 들어가고, 내려받거나 본 파일 이름은 UTF-16 리틀 엔디언으로 저장됩니다[12]. 헥스 편집기에서 파일 이름을 찾을 때는 UTF-16LE 로 검색합니다.

## 교차 검증

| 함께 볼 기록 | 잇는 값 | 확인하는 것 |
|---|---|---|
| [감사 로그 (Entra ID)](entra-logs/audit-logs.md) | 그룹 ID(`TeamGuid`), 대상 UPN, 시각 | 관리 도구로 한 멤버 변경의 실제 작업자[1] |
| [로그인 로그](entra-logs/sign-in-logs.md) | 계정, 시각 | `TeamsSessionStarted` 전후의 로그인 위치·방식 |
| [SharePoint·OneDrive](sharepoint-onedrive.md) | 파일 이름, 시각 | 채팅·채널에 올린 파일의 접근·공유 기록 |
| [Purview eDiscovery와 보존](purview-ediscovery.md) | 메일함, `SubstrateHolds` | 지우거나 고친 메시지 원본과 보류 상태 |
| [주요 작업 이름](unified-audit-log/operations.md) | `Operation` | 메시지·멤버 작업의 기록 조건 |
| [Defender 경고와 기록](defender-xdr.md) | 계정, 시각 | 같은 계정에 대한 보안 경고 |

## 실습

만든 테스트 테넌트에서 다음 질문을 풀어 봅니다.

1. Teams 앱에서 팀에 게스트를 추가하고, Microsoft 365 관리 센터에서 다른 사용자를 같은 팀에 추가한 뒤, 두 `MemberAdded` 레코드의 `UserId` 를 비교합니다.
2. 같은 레코드의 `Members.Role` 값을 소유자·멤버·게스트별로 모아, 이 테넌트에서 숫자와 역할이 어떻게 대응하는지 표로 만듭니다.
3. 내부 사용자끼리 채팅과, 게스트가 있는 채팅에 각각 메시지를 보낸 뒤 `MessageSent` 가 어느 쪽에만 남는지 확인합니다.
4. 보존 정책을 건 채팅에서 메시지를 고치고 지운 뒤, 앱 화면·내보내기 API·eDiscovery 검색 결과를 날짜별로 비교합니다.
5. 같은 PC 의 `MSTeams_[date]_[time].log` 에서 채팅으로 받은 파일 이름을 찾고, 로그 시각을 감사 레코드의 UTC 시각과 맞춰 PC 의 시간대를 추정합니다.

## 참고 문헌

1. Microsoft, "Search the audit log for events in Microsoft Teams", Microsoft Learn, 2026-04-14 갱신. https://learn.microsoft.com/en-us/purview/audit-teams-audit-log-events
2. Microsoft, "Audit log activities", Microsoft Learn, 2026-09-08 갱신. https://learn.microsoft.com/en-us/purview/audit-log-activities
3. Microsoft, "Office 365 Management Activity API schema", Microsoft Learn, 2026-08-26 갱신. https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
4. Microsoft, "Detailed activity properties in the audit log", Microsoft Learn, 2026-02-18 갱신. https://learn.microsoft.com/en-us/purview/audit-log-detailed-properties
5. Microsoft, "Learn about auditing solutions in Microsoft Purview", Microsoft Learn, 2026-05-18 갱신. https://learn.microsoft.com/en-us/purview/audit-solutions-overview
6. Microsoft, "Learn about retention for Microsoft Teams", Microsoft Learn, 2026-06-03 갱신. https://learn.microsoft.com/en-us/purview/retention-policies-teams
7. Microsoft, "Export content with the Microsoft Teams Export APIs", Microsoft Learn, 2026-07-20 갱신. https://learn.microsoft.com/en-us/microsoftteams/export-teams-content
8. Microsoft, "Search the audit log", Microsoft Learn, 2026-06-19 갱신. https://learn.microsoft.com/en-us/purview/audit-search
9. Microsoft, `Search-UnifiedAuditLog`, office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Search-UnifiedAuditLog.md
10. Invictus Incident Response, Microsoft-Extractor-Suite, `Scripts/Get-UAL.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite
11. ANSSI-FR, DFIR-O365RC, `DFIR-O365RC/Get-O365.ps1`. https://github.com/ANSSI-FR/DFIR-O365RC
12. Jihun Joun, Sangjin Lee, Jungheum Park, "Data remnants analysis of document files in Windows: Microsoft 365 as a case study", Forensic Science International: Digital Investigation 46 (2023) 301612 (DFRWS APAC 2023). https://doi.org/10.1016/j.fsidi.2023.301612
