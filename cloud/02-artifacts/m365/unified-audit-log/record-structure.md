---
title: "레코드 구조 (AuditData)"
parent: "통합 감사 로그"
grand_parent: "아티팩트 · Microsoft 365"
nav_order: 140
---

# 레코드 구조 (AuditData)

통합 감사 로그의 레코드 한 건은 모든 서비스가 같이 쓰는 공통 필드에 서비스별 필드를 덧붙인 JSON 객체이고, 이 객체를 AuditData 라고 부릅니다.

## 무엇을 기록하나

레코드마다 누가(UserId·UserType), 언제(CreationTime), 어느 서비스에서(Workload·RecordType), 무엇을(Operation·ObjectId), 어디서(ClientIP) 했는지가 공통 스키마 (Common schema) 로 들어갑니다[1]. 그 위에 SharePoint·Exchange·Entra·Teams 같은 서비스가 자기 스키마의 필드를 더합니다[1]. 어떤 작업 이름이 어떤 행위를 뜻하는지는 [주요 작업 이름](operations.md) 에서 다루고, 레코드를 꺼내는 방법은 [검색과 내보내기](search-export.md) 에서 다룹니다. JSON 로그를 읽는 일반 원리는 [JSON 로그 읽기](../../../01-foundations/logging/json-logs.md) 를 봅니다.

## 수집 경로마다 다른 모양

같은 레코드라도 꺼낸 경로에 따라 겉모양이 다릅니다.

| 수집 경로 | 겉모양 | 필드 이름 표기 |
|---|---|---|
| Purview 포털 CSV 내보내기 | 열 네 개: CreationDate, UserIds, Operations, AuditData(JSON)[2] | PascalCase |
| `Search-UnifiedAuditLog` 결과를 CSV 로 저장 | 고르는 열에 따라 다름. 문서 예시는 CreationDate, UserIds, RecordType, AuditData[2] | PascalCase |
| Office 365 Management Activity API | 공통 스키마 필드가 JSON 최상위에 그대로 옴[1] | PascalCase |
| Graph Audit Search API (auditLogRecord) | id, createdDateTime, auditLogRecordType, operation, userPrincipalName, clientIp, administrativeUnits 등 바깥 필드와 auditData 객체[3] | camelCase |

CSV 에서는 바깥 열(CreationDate·UserIds)과 AuditData 안의 필드(CreationTime·UserId)가 이름이 비슷해도 다른 자리에 있습니다. `Search-UnifiedAuditLog` 에 `-Formatted` 를 붙이면 정수로 오는 RecordType·Operation 이 설명 문자열로 바뀌고 AuditData 도 읽기 쉽게 바뀝니다[4]. 그래서 같은 사건이라도 한 사본에는 `RecordType` 이 `14`, 다른 사본에는 이름으로 적혀 있을 수 있습니다.

## 공통 필드

| 필드 | 형식 | 뜻 |
|---|---|---|
| Id | GUID | 레코드 고유 ID[1] |
| RecordType | AuditLogRecordType 열거값(정수) | 레코드 종류. 어느 서비스 스키마가 붙는지를 정함[1] |
| CreationTime | 날짜·시각(UTC) | 감사 레코드가 만들어진 시각[1] |
| Operation | 문자열 | 작업 이름. Exchange 관리 작업이면 실행한 cmdlet 이름[1] |
| OrganizationId | GUID | 테넌트 ID. 서비스와 관계없이 같은 값[1] |
| UserType | UserType 열거값 | 작업한 주체의 종류(아래 표)[1][5] |
| UserKey | 문자열 | UserId 를 달리 나타낸 ID(아래 "출처끼리 다른 점")[1][5] |
| Workload | 문자열 | 작업이 일어난 서비스[1] |
| ResultStatus | 문자열 | Succeeded·PartiallySucceeded·Failed. Exchange 관리 작업은 True·False[1] |
| ObjectId | 문자열 | SharePoint·OneDrive 는 파일·폴더 전체 경로, Exchange 관리 작업은 cmdlet 이 바꾼 개체 이름[1] |
| UserId | 문자열 | 작업한 사용자의 UPN. `SHAREPOINT\system`, `NT AUTHORITY\SYSTEM` 같은 시스템 계정도 들어감[1] |
| ClientIP | IPv4·IPv6 | 작업에 쓴 기기의 주소. 예외는 "함정과 한계" 참고[1] |
| Scope | online·onprem | 기록을 보낸 곳. onprem 은 현재 SharePoint 만 보냄[1] |
| AppAccessContext | 객체 모음 | 작업한 사용자·서비스 주체의 앱 문맥[1] |

### RecordType 에서 자주 보는 값

RecordType 은 서비스 스키마를 가르는 열쇠라서 필터를 걸 때 가장 먼저 씁니다. 아래는 조사에서 자주 만나는 값만 골랐고, 전체 목록은 Management Activity API 스키마 문서의 AuditLogRecordType 표에 있습니다[1].

| 값 | 이름 | 대상 |
|---|---|---|
| 1 | ExchangeAdmin | Exchange 관리 cmdlet |
| 2 | ExchangeItem | 메일함 항목 작업 |
| 6 | SharePointFileOperation | SharePoint 파일 작업 |
| 7 | OneDrive | OneDrive 작업 |
| 8 | AzureActiveDirectory | Entra ID 이벤트 |
| 14 | SharePointSharingOperation | SharePoint 공유 |
| 15 | AzureActiveDirectoryStsLogon | Entra 보안 토큰 서비스(STS) 로그온 |
| 19 | ExchangeAggregatedOperation | 묶어서 기록한 Exchange 메일함 감사 이벤트 |
| 25 | MicrosoftTeams | Teams |
| 50 | ExchangeItemAggregated | MailItemsAccessed 메일함 감사 작업 |
| 261 | CopilotInteraction | Copilot 사용 |
| 296 | AuditRetentionPolicy | 관리자가 Purview 감사 보존 정책을 다룬 작업 |
| 297 | AuditConfig | 관리자가 Purview 감사 설정을 다룬 작업 |

296·297 은 관리자가 감사 보존 정책·설정을 다룬 기록이라서 기록이 비어 있는 이유를 찾을 때 함께 봅니다. 감사를 끄고 켠 흔적은 [통합 감사 로그 허브](index.md) 에서 다룹니다.

### UserType 과 UserKey

UserType 값에 따라 UserKey 에 들어가는 값의 모양이 달라집니다(2026년 2월 문서 기준)[5].

| 값 | UserType | 뜻 | UserKey |
|---|---|---|---|
| 0 | Regular | 관리자 권한이 없는 일반 사용자 | Entra 개체 ID (GUID) |
| 2 | Admin | 조직의 관리자 | Entra 개체 ID (GUID) |
| 3 | DCAdmin | Microsoft 데이터센터 관리자·데이터센터 시스템 계정 | Entra 개체 ID (GUID) |
| 4 | System | 서버 쪽 논리(Windows 서비스·백그라운드 프로세스)가 만든 이벤트 | `00000000-0000-0000-0000-000000000000` |
| 5 | Application | Entra 애플리케이션이 만든 이벤트 | 앱 이름이나 앱 ID, 없으면 빈 문자열 |
| 6 | ServicePrincipal | 서비스 주체 | `00000000-0000-0000-0000-000000000000` |
| 7 | CustomPolicy | 고객이 만들거나 관리하는 정책 | `00000000-0000-0000-0000-000000000000` |
| 8 | SystemPolicy | Microsoft 가 관리하는 정책 | `00000000-0000-0000-0000-000000000000` |
| 9 | PartnerTechnician | 고객 테넌트를 대신해 일하는 파트너 테넌트 사용자(GDAP) | `00000000-0000-0000-0000-000000000000` |
| 10 | Guest | 게스트·익명 사용자 | `00000000-0000-0000-0000-000000000000` |
| 11 | Agent | AI 에이전트 | 에이전트의 Entra 개체 ID (GUID) |

Graph auditLogRecord 의 userType 은 같은 개념을 regular·admin·dcAdmin·system·application·servicePrincipal 같은 문자열로 돌려줍니다[3].

## 서비스별로 붙는 필드

서비스 스키마의 필드 가운데 해석에 자주 쓰는 것만 추렸습니다. 각 서비스의 세부 해석은 해당 페이지로 링크합니다.

| 서비스 스키마 | 눈여겨볼 필드 | 자세히 |
|---|---|---|
| Exchange 관리 | Parameters(cmdlet 인자의 Name·Value 모음), ModifiedProperties, ExternalAccess, OriginatingServer[1] | [Exchange Online](../exchange-online/index.md) |
| Exchange 메일함 | LogonType, MailboxOwnerUPN, LogonUserSid, ClientInfoString, ClientIPAddress, SessionId, AppId, ExternalAccess[1] | [Exchange Online](../exchange-online/index.md) |
| Entra STS 로그온 | ApplicationId, DeviceProperties, ErrorCode, LogonError[1] | [Entra ID 로그](../entra-logs/index.md) |
| SharePoint·OneDrive | SiteUrl, SourceRelativeUrl, SourceFileName, SourceFileExtension, UserAgent[5] | [SharePoint·OneDrive](../sharepoint-onedrive.md) |
| Teams | TeamName, TeamGuid, ChannelName, Members, AddOnType[5] | [Teams](../teams.md) |

Exchange 메일함 레코드의 LogonType 은 0 Owner(메일함 주인), 1 Admin, 2 Delegated(대리인), 3 Transport(데이터센터 전송 서비스), 4 SystemService(데이터센터 서비스 계정), 5 BestAccess(내부용), 6 DelegatedAdmin(위임 관리자)입니다[1]. 같은 스키마의 ExternalAccess 는 로그온한 사용자의 도메인이 메일함 주인의 도메인과 다르면 true 입니다[1]. Exchange 관리 레코드의 ExternalAccess 는 뜻이 달라서, True 이면 Microsoft 데이터센터 인력·데이터센터 서비스 계정·위임 관리자가 cmdlet 을 실행한 것입니다[1].

SharePoint 파일 레코드에서는 SiteUrl, SourceRelativeUrl, SourceFileName 을 이으면 ObjectId 와 같은 전체 경로가 됩니다[5]. ObjectId 가 잘려 보이거나 필드가 나뉘어 내보내졌을 때 이 관계로 경로를 다시 맞춥니다.

## 예시 레코드

아래는 공통 필드 모양을 보여 주려고 만든 예시입니다. 모든 ID·주소·이름은 지어낸 값입니다.

```json
{
  "Id": "3f2b9c4e-1a7d-4e2b-9c11-5d0a6e7f8a90",
  "RecordType": 6,
  "CreationTime": "2026-03-14T02:17:45",
  "Operation": "FileDownloaded",
  "OrganizationId": "11111111-2222-3333-4444-555555555555",
  "UserType": 0,
  "UserKey": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "Workload": "SharePoint",
  "ClientIP": "203.0.113.25",
  "ObjectId": "https://contoso.sharepoint.com/sites/Finance/Shared Documents/budget.xlsx",
  "UserId": "kim.minsu@contoso.com",
  "SiteUrl": "https://contoso.sharepoint.com/sites/Finance/",
  "SourceRelativeUrl": "Shared Documents",
  "SourceFileName": "budget.xlsx",
  "SourceFileExtension": "xlsx"
}
```

이 예시에서 RecordType 6 은 SharePoint 파일 작업이고, UserType 0 과 GUID 모양의 UserKey 는 일반 사용자 계정의 작업임을 뜻합니다[1][5].

## 증거로서 의미

**증명하는 것.** 이 테넌트(OrganizationId)에서 이 계정(UserId)으로 이 작업(Operation)이 이 대상(ObjectId)에 대해 서비스에 기록되었고, 레코드가 CreationTime(UTC)에 만들어졌다는 사실입니다[1]. UserType 과 LogonType 으로 사람 계정·시스템·서비스 주체·위임 접근을 가를 수 있습니다[1][5].

**증명하지 못하는 것.** UserId 는 자격 증명을 쓴 계정일 뿐 키보드 앞의 사람을 뜻하지 않습니다. ClientIP 가 사용자 기기의 주소라는 보장이 없습니다[1]. ResultStatus 가 Succeeded 여도 서비스에 따라 작업 결과가 성공이었다는 뜻이 아닐 수 있습니다[1]. 레코드가 없다는 사실만으로 작업이 없었다고 할 수 없고, 감사 설정·보존 기간·라이선스를 함께 확인해야 합니다([통합 감사 로그 허브](index.md)).

## 시각 해석

CreationTime 은 UTC 이고, 감사 레코드가 만들어진 시각입니다[1][5]. Graph auditLogRecord 의 createdDateTime 은 활동이 일어난 시각입니다[3]. Management Activity API 의 contentCreated 는 레코드를 담은 묶음(blob)을 받을 수 있게 된 시각이라서 이벤트 시각으로 쓰면 안 됩니다[6]. 핵심 서비스(Exchange·SharePoint·OneDrive·Teams)의 레코드는 보통 이벤트 뒤 60~90분이 지나야 검색되고, Microsoft 는 특정 시간을 보장하지 않습니다[7].

내보낸 파일을 도구로 읽을 때는 시각이 현지 시각으로 바뀌지 않았는지, 실제 데이터에서 한 건을 골라 포털 화면의 Date (UTC) 열과 맞춰 봅니다[7]. 여러 로그를 시간순으로 합치는 방법은 [클라우드 로그의 시각](../../../01-foundations/logging/timestamps.md) 과 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html) 을 봅니다.

## 함정과 한계

**ResultStatus 를 로그인 결과로 읽기.** Entra STS 로그온 레코드에서 Succeeded 는 HTTP 요청이 성공했다는 뜻일 뿐 로그인이 성공했다는 뜻이 아닙니다[1]. 로그인 성공 여부는 같은 레코드의 ErrorCode(0 이면 성공, 실패면 AADSTS 코드)와 LogonError 로 판단합니다[1].

**ClientIP 가 비었거나 다른 주소.** 일부 서비스는 사용자 기기의 주소가 아니라, 사용자 대신 서비스를 부른 신뢰 앱(예: 웹용 Office)의 주소를 남깁니다[1]. Entra 관련 이벤트는 IP 를 남기지 않아 ClientIP 가 null 입니다[1][5]. IP 해석은 [IP·사용자 에이전트·위치 정보](../../../01-foundations/logging/ip-ua-geo.md) 를 봅니다.

**관리자 작업이 일반 사용자로 보임.** Entra 관련 이벤트는 관리자가 한 작업도 UserType 0(Regular)으로 기록합니다[5]. 관리자인지는 UserType 이 아니라 UserId 가 가리키는 계정의 역할로 따로 확인합니다.

**시스템 계정이 작업자로 보임.** UserId 에 `NT AUTHORITY\SYSTEM`, `SHAREPOINT\system` 같은 시스템 계정이 올 수 있습니다[1]. 이런 레코드를 사람의 행위로 옮겨 적지 않습니다.

**Excel 로 펼칠 때 필드가 빠짐.** Power Query 로 AuditData 를 열로 펼치면 CSV 의 처음 1,000행에 있는 속성만 열로 만들어서, 뒤쪽 레코드에만 있는 필드는 사라집니다[2]. RecordType 별로 나눠 펼치거나, JSON 을 직접 읽는 도구를 씁니다.

**표기 차이.** 같은 필드가 PowerShell·API 에서는 PascalCase(ClientIP), Graph 에서는 camelCase(clientIp)로 옵니다[1][3]. 탐지 규칙이나 스크립트를 옮길 때 필드 이름부터 맞춥니다.

### 출처끼리 다른 점

UserKey 설명이 문서마다 다릅니다. Management Activity API 스키마 문서는 SharePoint·OneDrive·Exchange 사용자 이벤트의 UserKey 를 passport unique ID(PUID)로 설명하고[1], Purview 의 속성 설명 문서는 GUID 형식이나 16진수 형식의 Entra 개체 ID 로 설명합니다[5]. 실제 데이터에서 값이 GUID 모양인지 16진수 문자열인지 보고, 같은 사용자의 Entra 개체 ID 와 대조해 판단합니다.

## 직접 분석해 보기

**CSV 를 직접 읽기.** 포털에서 내보낸 CSV 의 AuditData 열에는 레코드마다 JSON 객체가 들어 있습니다[2]. 아래는 PowerShell 로 열을 풀어 공통 필드만 뽑는 예입니다.

```powershell
Import-Csv .\audit_export.csv | ForEach-Object {
  $d = $_.AuditData | ConvertFrom-Json
  [pscustomobject]@{
    CreationTime = $d.CreationTime; RecordType = $d.RecordType
    Operation = $d.Operation; UserId = $d.UserId; UserType = $d.UserType
    ClientIP = $d.ClientIP; ObjectId = $d.ObjectId; ResultStatus = $d.ResultStatus
  }
} | Export-Csv .\audit_flat.csv -NoTypeInformation
```

바깥 열 CreationDate 와 AuditData 안의 CreationTime 을 나란히 두고 두 값이 같은 시각을 가리키는지 한 번 확인해 두면, 뒤에 다른 도구로 만든 결과와 맞출 때 기준이 됩니다.

**공개 도구.** Microsoft-Extractor-Suite 의 `Get-UAL`(`Search-UnifiedAuditLog` 기반)과 `Get-UALGraph`(Graph Audit Search 기반)는 레코드를 CSV·JSON·JSONL·SOF-ELK 형식으로 저장합니다[8]. 수집 경로에 따라 필드 표기가 PascalCase 와 camelCase 로 갈리므로 두 결과를 합칠 때 위의 "수집 경로마다 다른 모양" 표를 기준으로 맞춥니다. 수집 도구 전반은 [Microsoft 365 수집 도구](../../../03-techniques/acquisition/m365-collection.md) 에서 다룹니다.

## 교차 검증

Entra 관련 레코드는 ClientIP 가 비어 있으므로 같은 시각의 [Entra ID 로그](../entra-logs/index.md) 로그인 기록에서 IP·기기·앱을 채웁니다. 메일함 레코드의 LogonType·ClientInfoString 은 [Exchange Online](../exchange-online/index.md) 의 메일함 감사 설명과 함께 읽습니다. 파일 레코드의 ObjectId 는 [SharePoint·OneDrive](../sharepoint-onedrive.md) 의 버전 기록·휴지통과 맞춰 봅니다.

## 실습

1. 내보낸 CSV 에서 RecordType 이 15 인 레코드를 골라 ResultStatus 와 ErrorCode 를 나란히 놓습니다. ResultStatus 가 Succeeded 인데 ErrorCode 가 0 이 아닌 레코드가 있나요?
2. UserType 이 0 이 아닌 레코드를 모아 UserType 별로 UserId 를 세어 봅니다. 사람 계정이 아닌 주체가 어떤 작업을 가장 많이 했나요?
3. SharePoint 파일 레코드 한 건에서 SiteUrl, SourceRelativeUrl, SourceFileName 을 이어 ObjectId 와 같은지 확인합니다.
4. 같은 기간을 포털 CSV 와 Graph Audit Search 로 각각 받아 같은 Id 의 레코드를 찾고, 필드 이름과 시각 표기가 어떻게 다른지 비교합니다.

## 참고 문헌

1. Microsoft, "Office 365 Management Activity API schema", Microsoft Learn (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
2. Microsoft, "Export, configure, and view audit log records", Microsoft Learn (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-export-records
3. Microsoft, "auditLogRecord resource type", Microsoft Graph 문서 (2026-08-14 갱신). https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogrecord
4. Microsoft, "Search-UnifiedAuditLog", office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Search-UnifiedAuditLog.md
5. Microsoft, "Detailed properties in the audit log", Microsoft Learn (2026-02-18 갱신). https://learn.microsoft.com/en-us/purview/audit-log-detailed-properties
6. Microsoft, "Office 365 Management Activity API reference", Microsoft Learn (2024-12-03 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference
7. Microsoft, "Search the audit log", Microsoft Learn (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-search
8. invictus-ir, Microsoft-Extractor-Suite. https://github.com/invictus-ir/Microsoft-Extractor-Suite
