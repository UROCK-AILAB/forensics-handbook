---
title: "메일함 감사와 MailItemsAccessed"
parent: "Exchange Online"
grand_parent: "아티팩트 · Microsoft 365"
nav_order: 220
---

# 메일함 감사와 MailItemsAccessed (Mailbox Auditing)

Exchange Online 메일함에서 소유자·위임자·관리자가 한 작업을 서비스가 기록하고, 그중 `MailItemsAccessed` 는 어떤 메일에 서버 쪽 접근이 있었는지 알려 줍니다.

## 무엇을 기록하나 · 왜 생기나

메일함 감사 (mailbox auditing) 는 모든 조직에서 기본으로 켜져 있고, 새 메일함을 만들면 따로 설정하지 않아도 감사가 시작됩니다[1]. 기록 대상은 메일함에서 일어난 작업(삭제, 이동, 발송, 규칙 변경, 폴더 권한 변경, 메일 접근 등)이고, 레코드는 [통합 감사 로그](../unified-audit-log/index.md)에 들어가 같은 방법으로 검색합니다[1][3]. 메일이 서버를 어떻게 오갔는지는 이 기록이 아니라 [메시지 추적](message-trace.md)에 남습니다.

감사는 작업을 한 사람을 로그인 유형 (sign-in type) 셋으로 나눠 기록합니다[1].

| 로그인 유형 | 해당하는 경우 |
|---|---|
| Owner | 메일함 소유자 계정 |
| Delegate | 다른 메일함에 SendAs·SendOnBehalf·FullAccess 권한을 받은 사용자, FullAccess 를 받은 관리자 |
| Admin | Purview eDiscovery·Exchange Online In-Place eDiscovery 로 메일함을 검색한 경우, MAPI Editor 로 연 경우, ApplicationImpersonation 역할로 다른 사용자를 가장해 접근한 경우 |

관리 API 스키마의 `LogonType` 값은 0 Owner, 1 Admin, 2 Delegated, 3 Transport, 4 SystemService, 5 BestAccess, 6 DelegatedAdmin 입니다[3]. Transport 와 SystemService 는 Microsoft 데이터센터의 전송 서비스와 서비스 계정이고, BestAccess 는 내부용, DelegatedAdmin 은 위임된 관리자입니다[3].

## 켜짐 여부와 감사 작업

### 조직과 메일함의 설정

조직 전체 설정은 Exchange Online PowerShell 에서 확인합니다[1].

```powershell
Get-OrganizationConfig | Format-List AuditDisabled
```

값이 `False` 면 기본 감사가 켜진 상태이고, 이때 `Get-Mailbox` 의 `AuditEnabled` 는 메일함 설정과 상관없이 항상 `True` 로 나옵니다[1]. `Set-OrganizationConfig -AuditDisabled $true` 로 끄면 그 시점부터 어느 메일함 작업도 감사되지 않고, 이미 쌓인 기록은 보존 기간이 끝날 때까지 남습니다[1].

기본 감사가 켜져 있으면 메일함 하나만 끌 수는 없지만, `Set-MailboxAuditBypassAssociation -AuditByPassEnabled $true` 로 특정 사용자를 우회 대상으로 지정하면 그 사용자가 한 작업은 소유자·위임자·관리자 어느 자격이든 기록되지 않습니다[1]. 확인은 아래처럼 하고, `True` 면 우회 대상입니다[1]. Untitled Goose Tool 은 수집할 때 이 설정을 `EXO_MailboxAuditStatus_PowerShell.json` 으로 떠 둡니다[8].

```powershell
Get-MailboxAuditBypassAssociation -Identity user@contoso.com | Format-List AuditByPassEnabled
```

보관 기간은 메일함의 `AuditLogAgeLimit` 가 아니라 Purview 감사 보존 정책이 정합니다[1]. 라이선스별 보관 기간은 [보관 기간과 라이선스](../../../01-foundations/logging/retention-licensing.md)와 [통합 감사 로그](../unified-audit-log/index.md)에 정리돼 있습니다.

### 지원하는 메일함

| 메일함 종류 | 감사 지원 | 기본으로 켜짐 |
|---|---|---|
| 사용자 메일함 | 예 | 예 |
| 공유 메일함 | 예 | 예 |
| Microsoft 365 그룹 메일함 | 예 | 예 |
| 공용 폴더 메일함 | 아니요 | 아니요 |
| 리소스 메일함 | 아니요 | 아니요 |

멀티지오 (multigeo) 환경에서는 다른 지역의 공유 메일함에 권한을 받은 사용자가 한 작업이 그 공유 메일함의 감사에 남지 않습니다[1].

### 기본으로 감사하는 작업

사용자·공유 메일함에서 기본으로 기록되는 작업은 아래와 같습니다(2026년 9월 문서 기준, 문서 갱신 2026-06-19)[1]. "선택" 은 기록할 수는 있지만 기본으로는 꺼진 작업입니다.

| 작업 | 뜻 | Admin | Delegate | Owner |
|---|---|---|---|---|
| ApplyRecord | 항목에 레코드 레이블을 붙임 | 기본 | 기본 | 기본 |
| AttachmentAccess | Microsoft Graph API 로 첨부 파일에 접근(항상 켜짐) | 기본 | 기본 | 기본 |
| Create | 일정·연락처·초안·메모·작업 폴더에 항목 생성 | 기본 | 기본 | 기본 |
| HardDelete | 복구 가능한 항목 폴더에서 영구 제거 | 기본 | 기본 | 기본 |
| MailItemsAccessed | 메일 프로토콜·클라이언트가 메일 데이터에 접근 | 기본 | 기본 | 기본 |
| MoveToDeletedItems | 지운 편지함으로 이동 | 기본 | 기본 | 기본 |
| SoftDelete | 복구 가능한 항목 폴더로 이동 | 기본 | 기본 | 기본 |
| Update | 메시지나 속성 변경 | 기본 | 기본 | 기본 |
| UpdateCalendarDelegation | 일정 위임 지정 | 기본 | 없음 | 기본 |
| UpdateFolderPermissions | 폴더 권한 변경 | 기본 | 기본 | 기본 |
| UpdateInboxRules | 받은편지함 규칙 추가·삭제·변경 | 기본 | 기본 | 기본 |
| Send | 보내기·회신·전달 | 기본 | 없음 | 기본 |
| SendAs / SendOnBehalf | 위임 권한으로 발송 | 기본 | 기본 | 없음 |
| Copy | 다른 폴더로 복사 | 선택 | 없음 | 없음 |
| FolderBind | 폴더 접근, 관리자·위임자가 메일함을 열 때도 기록 | 선택 | 선택 | 없음 |
| MailboxLogin | 소유자가 메일함에 로그인 | 없음 | 없음 | 선택 |
| MessageBind | 미리 보기 창·관리자 열람(E5·A5·G5 가 아닌 사용자만) | 선택 | 없음 | 없음 |
| Move | 다른 폴더로 이동 | 선택 | 선택 | 선택 |
| RecordDelete | 레코드 레이블 항목을 복구 가능한 항목으로 이동 | 선택 | 선택 | 선택 |
| SearchQueryInitiated | Outlook·Windows 10 메일 앱에서 메일함 검색 | 없음 | 없음 | 선택 |

메시지를 만들고 보내고 받는 일과 폴더를 만드는 일은 `Create` 로 감사되지 않습니다[1]. 위임자의 `FolderBind` 는 24시간 안에 폴더당 한 건으로 합쳐 기록됩니다[1]. 그룹 메일함은 Create·HardDelete·MoveToDeletedItems·SendAs·SendOnBehalf·SoftDelete·Update 만 고정으로 기록하고 바꿀 수 없습니다[1]. 작업 이름과 포털에 보이는 이름의 대응은 [주요 작업 이름](../unified-audit-log/operations.md)에 있고, `UpdateInboxRules` 로 남는 규칙 변경을 해석하는 방법은 [받은편지함 규칙과 전달](inbox-rules.md)에 있습니다.

메일함마다 감사 작업 목록이 바뀌었는지는 `DefaultAuditSet` 으로 봅니다[1].

```powershell
Get-Mailbox -Identity user@contoso.com | Format-List DefaultAuditSet
Get-Mailbox -Identity user@contoso.com | Select-Object -ExpandProperty AuditOwner
Get-Mailbox -Identity user@contoso.com | Select-Object -ExpandProperty AuditDelegate
Get-Mailbox -Identity user@contoso.com | Select-Object -ExpandProperty AuditAdmin
```

`DefaultAuditSet` 이 `Admin, Delegate, Owner` 면 세 유형 모두 Microsoft 가 관리하는 기본 목록을 쓰고 있습니다[1]. 어느 유형이 빠져 있으면 누군가 `Set-Mailbox` 의 `AuditAdmin`·`AuditDelegate`·`AuditOwner` 로 그 유형의 목록을 바꾼 것이고, 값이 비어 있으면 세 유형 모두 바뀐 것입니다[1]. 목록을 바꾼 메일함에는 Microsoft 가 새로 내놓는 기본 작업이 자동으로 더해지지 않습니다[1]. 그룹 메일함에 `-GroupMailbox` 를 붙여 나오는 목록 값은 믿지 않습니다[1].

## MailItemsAccessed

`MailItemsAccessed` 는 Audit (Standard) 기능에 들어 있고, Office 365·Microsoft 365 E3/E5 라이선스 사용자에게 기본으로 켜져 있습니다(2026년 9월 문서 기준, 문서 갱신 2026-06-24)[2]. POP, IMAP, MAPI, EWS, Exchange ActiveSync, REST 를 모두 다루고, 접근 방식은 동기화 (sync) 와 바인드 (bind) 두 가지로 나뉩니다[2]. `MailItemsAccessed` 레코드의 민감도 레이블 (`SensitivityLabel`) 속성은 Audit (Premium) 에서만 제공합니다[4].

| 구분 | Sync | Bind |
|---|---|---|
| 뜻 | 클라이언트가 서버에서 메일 묶음을 내려받음 | 사용자나 클라이언트가 메시지 한 통에 접근 |
| 기록 조건 | Windows·Mac 용 데스크톱 Outlook 으로 접근할 때만 | 모든 프로토콜 |
| 레코드 단위 | 메일 하나하나가 아니라 동기화한 폴더 하나당 한 건 | 2분 안의 바인드를 한 레코드로 묶음 |
| 식별 정보 | 폴더 경로 | 메시지마다 `InternetMessageId` |
| 해석 | 그 폴더의 메일 전부가 노출된 것으로 봄 | 목록에 있는 메시지에 접근이 있었음 |

접근 방식은 `OperationProperties` 안의 `MailAccessType` 에 `Sync` 나 `Bind` 로 적힙니다[2]. 바인드 레코드는 `AuditData` 의 `Folders` 에 폴더별로 메시지를 담고, 묶인 바인드 개수는 `OperationCount` 에 적습니다[2].

같은 바인드가 한 시간 안에 되풀이되면 레코드를 다시 만들지 않고, 동기화도 한 시간 간격으로 걸러 냅니다[2]. 다만 같은 `InternetMessageId` 라도 아래 값 가운데 하나라도 다르면 새 레코드를 만듭니다[2].

| 속성 | 뜻 |
|---|---|
| ClientIPAddress | 클라이언트 IP |
| ClientInfoString | 접근에 쓴 프로토콜과 클라이언트 |
| ParentFolder | 접근한 메일의 전체 폴더 경로 |
| Logon_type | Owner(0), Admin(1), Delegate(2) |
| MailAccessType | Bind 인지 Sync 인지 |
| MailboxUPN | 메일이 있는 메일함의 UPN |
| User | 메일에 접근한 사용자의 UPN |
| SessionId | 세션 식별자 |

## 구조

메일함 감사 레코드의 `RecordType` 은 한 항목에 대한 작업이면 2 `ExchangeItem`, 여러 항목에 걸친 작업(이동·삭제)이면 3 `ExchangeItemGroup` 이고, `MailItemsAccessed` 관련 이벤트는 50 `ExchangeItemAggregated` 입니다[3]. 공통 필드(`CreationTime`, `UserId`, `Operation`, `ResultStatus` 등)는 [레코드 구조](../unified-audit-log/record-structure.md)에 있고, 여기서는 메일함 감사에만 있는 필드를 봅니다[3].

| 필드 | 뜻 |
|---|---|
| LogonType | 메일함에 접근해 작업한 사용자의 유형(0 Owner, 1 Admin, 2 Delegated, 3 Transport, 4 SystemService, 5 BestAccess, 6 DelegatedAdmin) |
| MailboxGuid | 접근한 메일함의 Exchange GUID |
| MailboxOwnerUPN / MailboxOwnerSid | 메일함 소유자의 메일 주소와 SID |
| LogonUserSid / LogonUserDisplayName | 작업한 사용자의 SID 와 표시 이름 |
| ExternalAccess | 로그온 사용자의 도메인과 메일함 소유자의 도메인이 다르면 true |
| ClientInfoString | 브라우저·Outlook 버전·모바일 기기 같은 클라이언트 정보 |
| ClientIPAddress | 작업이 기록될 때 쓴 기기의 IPv4·IPv6 주소 |
| ClientMachineName / ClientProcessName / ClientVersion | Outlook 이 돌아간 컴퓨터 이름, 메일 클라이언트, 버전 |
| SessionId | 세션 고유 식별자 |
| AppId / ClientAppId | 애플리케이션 ID, 요청을 처음 보낸 서비스·프로토콜 ID |
| OperationProperties | 작업별 속성의 Name/Value 모음(`MailAccessType` 등) |
| OperationCount | 묶인 작업의 수 |
| Folders | 묶인 폴더 모음. 폴더마다 `Id`, `Path`, `FolderItems` |
| Folders.FolderItems | 항목마다 `Id`, `ImmutableId`, `InternetMessageId`, `CreationTime`, `Subject`, `SizeInBytes` 등 |

아래는 바인드 레코드의 `AuditData` 를 줄인 만든 예시입니다. 값은 모두 지어낸 것이고, 필드 이름은 관리 API 스키마[3]를, `OperationProperties` 모양은 검색 필터[2]를 따릅니다.

```json
{
  "CreationTime": "2026-03-02T01:15:42",
  "Id": "3f2b6c1e-0a4d-4e8b-9c7a-5d1e2f3a4b5c",
  "Operation": "MailItemsAccessed",
  "RecordType": 50,
  "ResultStatus": "Succeeded",
  "UserId": "kim@contoso.com",
  "MailboxOwnerUPN": "kim@contoso.com",
  "LogonType": 0,
  "ExternalAccess": false,
  "ClientIPAddress": "203.0.113.25",
  "SessionId": "8a1c2d3e-4f50-6172-8394-a5b6c7d8e9f0",
  "OperationCount": 2,
  "OperationProperties": [
    { "Name": "MailAccessType", "Value": "Bind" }
  ],
  "Folders": [
    {
      "Id": "LgAAAAB0example",
      "Path": "\\Inbox",
      "FolderItems": [
        { "InternetMessageId": "<a1b2c3@mail.example.com>", "SizeInBytes": 48213 },
        { "InternetMessageId": "<d4e5f6@mail.example.com>", "SizeInBytes": 10240 }
      ]
    }
  ]
}
```

## 증거로서 의미

**증명하는 것**

- 레코드의 시각에 그 `UserId`·`LogonType` 으로 그 메일함에서 그 작업이 서비스에 기록됐다는 사실입니다.
- 바인드 레코드면 그 세션·IP·클라이언트로 `FolderItems` 에 적힌 `InternetMessageId` 메시지에 서버 쪽 접근이 있었다는 사실입니다[2].
- 동기화 레코드면 그 폴더 전체가 클라이언트로 내려갔을 수 있다는 사실이고, 그 폴더의 메일은 전부 노출된 것으로 봅니다[2].
- `LogonType` 과 `MailboxOwnerUPN`·`UserId` 를 비교하면 소유자가 한 일인지, 위임자나 관리자가 남의 메일함에서 한 일인지 가를 수 있습니다[3].

**증명하지 못하는 것**

- 사람이 메일을 실제로 읽었는지는 알 수 없습니다. `MailItemsAccessed` 는 읽었다는 표시가 없어도 접근만 있으면 기록합니다[2].
- 동기화로 내려받은 뒤 인터넷을 끊고 로컬에서 읽은 것은 감사되지 않습니다[2].
- 레코드가 없다는 사실만으로 접근이 없었다고 할 수 없습니다. 감사를 끄거나, 우회 대상으로 지정하거나, 작업 목록을 바꾸거나, 보존 기간이 지났을 수 있습니다[1].
- 레코드 수는 접근 횟수가 아닙니다. 2분 묶음과 한 시간 중복 제거를 거친 결과입니다[2].

보고서에는 "2026-03-02 01:15(UTC) 무렵 203.0.113.25 에서 kim@contoso.com 계정의 세션으로 메시지 2통에 바인드 접근한 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다(만든 예시).

## 시각 해석

`CreationTime` 은 UTC 이고 레코드가 만들어진 시각입니다[3]. 바인드는 2분 안의 접근을 한 레코드로 묶으므로, 레코드 시각 하나가 그 2분 동안의 여러 접근을 대표합니다[2]. 한 시간 안에 같은 조건으로 되풀이된 접근은 레코드가 없으므로, 레코드 사이의 빈 시간이 접근이 없었던 시간이라고 보면 안 됩니다[2]. Exchange 감사 레코드는 보통 이벤트 뒤 60~90분 안에 검색되지만 Microsoft 는 특정 시간을 보장하지 않습니다[5]. 시간대 변환과 로그 지연의 일반 원리는 [클라우드 로그의 시각](../../../01-foundations/logging/timestamps.md)을 봅니다.

## 함정과 한계

- **감사 설정 자체를 먼저 봅니다.** `AuditDisabled`, `Get-MailboxAuditBypassAssociation`, `DefaultAuditSet` 을 확인하지 않고 "기록이 없다" 고 쓰면 안 됩니다[1]. Exchange 관리 작업 레코드는 `Operation` 에 실행한 cmdlet 이름이 적히므로[3], `Set-OrganizationConfig`·`Set-MailboxAuditBypassAssociation`·`Set-Mailbox` 로 설정을 바꾼 기록도 함께 검색합니다.
- **기본 감사가 켜져 있어도 일부 사용자의 메일함 감사 이벤트가 Purview 검색이나 관리 API 에서 보이지 않을 수 있습니다**[5].
- **라이선스에 따라 기록이 다릅니다.** `MailItemsAccessed` 는 Audit (Standard) 기능이고 E3/E5 사용자에게 기본으로 켜집니다(2026년 9월 문서 기준)[2]. 다만 Hawk 의 `Get-HawkUserMailItemsAccessed` 주석에는 E5·G5 라이선스와 고급 감사 (Advanced Auditing) 가 필요하다고 적혀 있어 출처끼리 다르므로, 조사 대상 계정의 라이선스와 실제 레코드로 확인합니다[7]. `MessageBind` 는 E5·A5·G5 가 아닌 사용자에게만 있습니다[1]. `SearchQueryInitiated` 는 소유자 작업 가운데 기본으로 꺼진 작업이고[1], Exchange Online 검색 기록은 Audit (Premium) 이벤트입니다[4]. Hawk 는 이 기록을 `SearchQueryInitiatedExchange` 작업 이름으로 검색합니다[7].
- **복구 가능한 항목 폴더가 가득 차면** 메일함의 `Audits` 하위 폴더에 감사 항목을 더 저장할 수 없습니다[9]. 보존·보류와 복구 가능한 항목 폴더 구조는 [Purview eDiscovery와 보존](../purview-ediscovery.md)에 있습니다.
- **`IsThrottled`**: Microsoft-Extractor-Suite 는 `OperationProperties` 에서 `MailAccessType` 과 함께 `IsThrottled` 값을 따로 뽑습니다[6]. 이 값의 뜻은 실제 데이터에서 다른 필드와 함께 확인한 뒤 해석합니다.
- **검색 cmdlet 두 가지**: `Search-MailboxAuditLog` 는 온프레미스 Exchange 와 Exchange Online 양쪽에 있고 메일함 하나 이상의 감사 기록을 검색하지만, 클라우드 서비스에서는 폐지될 예정입니다[10]. 다른 서비스 기록과 한 흐름으로 보려면 `Search-UnifiedAuditLog` 로 통합 감사 로그를 검색합니다[2].

## 직접 분석해 보기

### PowerShell 로 한 번

Exchange Online PowerShell 에서 아래처럼 동기화와 바인드를 나눠 뽑습니다[2]. 날짜와 사용자는 만든 예시입니다.

```powershell
$r = Search-UnifiedAuditLog -StartDate 2026-03-01 -EndDate 2026-03-03 `
       -UserIds kim@contoso.com -Operations MailItemsAccessed -ResultSize 5000
$r | Where-Object { $_.AuditData -like '*"MailAccessType","Value":"Sync"*' }
$r | Where-Object { $_.AuditData -like '*"MailAccessType","Value":"Bind"*' }
```

먼저 동기화 레코드의 `ClientIPAddress`·`ClientInfoString`·`SessionId` 가 의심 활동의 IP·클라이언트와 같은지 봅니다[2]. 같은 문맥의 동기화가 있으면 메일함 전체가 넘어간 것으로 보고 범위를 잡고, 없으면 바인드 레코드의 `InternetMessageId` 목록으로 접근한 메시지를 하나씩 추립니다[2]. 추린 `InternetMessageId` 로 [메시지 추적](message-trace.md)이나 eDiscovery 에서 메시지를 찾아 내용이 민감한지 확인합니다.

검색 범위와 결과 건수 한도, 대량 내보내기 방법은 [검색과 내보내기](../unified-audit-log/search-export.md)에 있습니다.

### 공개 도구로 한 번

- **Microsoft-Extractor-Suite**: `Get-MailItemsAccessed.ps1` 의 `Get-Sessions` 는 `Search-UnifiedAuditLog -Operations "MailItemsAccessed"` 를 사용자·IP 조건으로 부르고, `SessionId`, `ClientIPAddress`, `MailAccessType`, `IsThrottled`, `OperationCount` 를 표로 만듭니다[6]. 세션·IP 조건으로 부르는 `Get-MessageIDs` 는 바인드면 `Folders.FolderItems` 의 `InternetMessageId`·`SizeInBytes` 를, 동기화면 `Folders.Path` 와 함께 "N/A (Sync - entire folder)" 를 적습니다[6].
- **Hawk**: `Get-HawkUserMailItemsAccessed` 는 `Search-UnifiedAuditLog -Operations 'MailItemsAccessed' -UserIds` 로, `Get-HawkUserMailSendActivity` 는 `-Operations 'Send'` 로 사용자별 기록을 모읍니다[7].
- **Untitled Goose Tool**: 감사 우회 설정(`Get-MailboxAuditBypassAssociation`)과 메일함 권한 등 Exchange 설정을 함께 떠 둡니다[8].

수집 도구의 설치와 권한은 [Microsoft 365 수집 도구](../../../03-techniques/acquisition/m365-collection.md)를 봅니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 |
|---|---|
| [Entra ID 로그](../entra-logs/index.md) | 같은 IP·시간대의 로그인, 세션이 시작된 방법 |
| [받은편지함 규칙과 전달](inbox-rules.md) | `UpdateInboxRules`·`New-InboxRule` 뒤에 실제로 만들어진 규칙 |
| [메시지 추적](message-trace.md) | `Send`·`SendAs` 기록과 실제로 나간 메일 |
| [Purview eDiscovery와 보존](../purview-ediscovery.md) | 복구 가능한 항목에 남은 삭제 메일, 조사자 자신의 검색 기록 |
| [클라우드 타임라인](../../../03-techniques/analysis/timeline.md) | 여러 로그를 UTC 로 맞춰 시간순으로 합치는 방법 |

## 실습

위의 만든 예시 레코드와 명령으로 아래 질문을 풀어 봅니다.

1. 예시 레코드에서 `LogonType` 이 0 이고 `UserId` 와 `MailboxOwnerUPN` 이 같습니다. 이 접근을 위임자 접근으로 볼 수 있는지 판단해 보세요.
2. `OperationCount` 가 2 인 레코드 하나를 보고 "2026-03-02 01:15:42 에 메일 2통을 읽었다" 고 쓰면 어디가 틀렸는지 두 가지를 짚어 보세요.
3. 같은 계정에 `MailAccessType` 이 `Sync` 인 레코드가 의심 IP 에서 한 건 있다면 노출 범위를 어떻게 잡아야 하는지 설명해 보세요.
4. 의심 기간에 어떤 레코드도 나오지 않을 때 확인할 설정 세 가지를 꼽아 보세요.

## 참고 문헌

1. Microsoft Learn, "Manage mailbox auditing", 2026-06-19 갱신. https://learn.microsoft.com/en-us/purview/audit-mailboxes
2. Microsoft Learn, "Use MailItemsAccessed to investigate compromised accounts", 2026-06-24 갱신. https://learn.microsoft.com/en-us/purview/audit-log-investigate-accounts
3. Microsoft Learn, "Office 365 Management Activity API schema", 2026-08-26 갱신. https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
4. Microsoft Learn, "Learn about auditing solutions in Microsoft Purview", 2026-05-18 갱신. https://learn.microsoft.com/en-us/purview/audit-solutions-overview
5. Microsoft Learn, "Search the audit log", 2026-06-19 갱신. https://learn.microsoft.com/en-us/purview/audit-search
6. invictus-ir, Microsoft-Extractor-Suite, `Scripts/Get-MailItemsAccessed.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite
7. T0pCyber, Hawk, `Get-HawkUserMailItemsAccessed.ps1`, `Get-HawkUserMailSendActivity.ps1`, `Get-HawkUserExchangeSearchQuery.ps1`. https://github.com/T0pCyber/hawk
8. CISA, Untitled Goose Tool, `goosey/m365_datadumper.py`. https://github.com/cisagov/untitledgoosetool
9. Microsoft Learn, "Recoverable Items folder in Exchange Online", 2026-07-13 갱신. https://learn.microsoft.com/en-us/exchange/security-and-compliance/recoverable-items-folder/recoverable-items-folder
10. Microsoft, "Search-MailboxAuditLog", office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Search-MailboxAuditLog.md
