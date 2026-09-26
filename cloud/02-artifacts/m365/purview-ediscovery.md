---
title: "Purview eDiscovery와 보존"
parent: "아티팩트 · Microsoft 365"
nav_order: 270
---

# Purview eDiscovery와 보존 (eDiscovery·Retention)

Microsoft 365 에서 지운 메일·파일이 어디에 얼마나 남는지는 보존 설정과 보류가 정하고, 누가 사례를 만들고 검색·내보내기를 했는지는 통합 감사 로그의 eDiscovery 작업으로 남습니다.

## 무엇을 기록하나 · 왜 생기나

이 쪽에서 다루는 흔적은 두 갈래입니다.

첫째는 **보존된 내용**입니다. 전자 증거 개시 (eDiscovery) 는 조사·소송에 쓸 전자 정보를 찾아 넘기는 절차이고, Microsoft Purview eDiscovery 는 Exchange Online, Microsoft Teams, Microsoft 365 그룹, OneDrive, SharePoint, Viva Engage 를 검색 대상으로 삼습니다[1]. 사용자가 메일이나 파일을 지워도 보존 정책 (retention policy)·보존 레이블 (retention label)·보류 (hold) 가 걸려 있으면 영구 삭제가 멈추고, 내용은 사용자에게 보이지 않는 숨은 위치로 옮겨지거나 복사됩니다[5]. 조사자는 이 숨은 위치까지 eDiscovery 검색으로 찾을 수 있습니다[4].

둘째는 **eDiscovery 작업 기록**입니다. 관리자나 eDiscovery 권한을 받은 사용자가 사례를 만들고, 보류를 걸고, 검색·내보내기·검토를 하면 그 작업이 통합 감사 로그 (Unified Audit Log) 에 남습니다[2]. 내부자가 권한을 이용해 다른 사람의 메일을 대량으로 검색해 내려받은 경우도 여기에 남고, 조사자 자신의 수집 작업도 같은 곳에 남습니다.

## 위치와 버전별 차이

### 옛 환경과 새 환경

Microsoft 는 2025년 8월 31일에 클래식 eDiscovery 를 모두 폐지했습니다. 대상은 클래식 콘텐츠 검색 (Content Search), 클래식 eDiscovery (Standard), 클래식 eDiscovery (Premium) 입니다[3]. 그 뒤 클래식 작업 안내는 21Vianet 이 운영하는 중국 Microsoft 365 조직에만 해당합니다[3].

| 항목 | 클래식 환경 | 새 환경 (Purview 포털) |
|---|---|---|
| 중심 단위 | 관리 대상자 (custodian) | 사례 (case)[1] |
| 콘텐츠 검색 | 사례와 별개 기능 | 시스템이 만든 Content Search 사례 안에 들어감[1] |
| 수집 결과 | 컬렉션, 검토 세트에 넣으면 바뀌지 않음 | 통계 (statistics) 가 대신하고, 검색은 검토 세트에 넣은 뒤에도 고칠 수 있음[1] |
| 고급 색인 | 따로 다시 색인 | 검색·검토 세트 추가·내보내기 때 자동 실행[1] |
| 작업 이름 예 | `SearchCreated`, `SearchExported`, `SearchExportDownloaded`[3] | `PurviewSearchAdded`, `PurviewSearchExportJobSubmitted`[2] |
| 감사 기록의 `ClientIP` | 없는 경우가 있음 | 모든 작업에 있음[2] |

2025년 8월 이전 기록을 보는 조사라면 두 환경의 작업 이름이 한 테넌트에 섞여 있을 수 있습니다. 새 환경 작업에는 `ClientIP` 필드가 항상 들어가므로, 이 필드가 있는지로 두 환경을 가를 수 있습니다[2].

### 라이선스

| 구독 | 쓸 수 있는 것 |
|---|---|
| eDiscovery 기본 | 메일함과 사이트를 한 번에 검색해 결과를 내보내고, 사례로 내용을 찾고 보류하고 내보냄[1] |
| Office 365 E5·Microsoft 365 E5 또는 관련 E5 추가 구독 | 위에 더해 프리미엄 기능으로 사례를 관리하고 내용을 분석함[1] |

검토 세트 (review set) 는 Microsoft 가 제공하는 Azure Storage 위치이고, 검토 세트에 넣은 항목은 원래 위치에서 복사된 고정된 집합이 됩니다[1]. 검토 세트에서는 광학 문자 인식 (OCR), 대화 스레드 모으기, 태그, 분석을 쓸 수 있고, Microsoft 암호화로 보호된 메일·문서는 검색 결과나 검토 세트에 넣을 때 자동으로 복호화됩니다[1]. 어떤 기능이 프리미엄에만 있는지는 2026년 6월 문서 기준으로 기능 표에 나뉘어 있으니 테넌트의 구독과 함께 확인합니다.

### 서비스별 보존 위치

| 서비스 | 지우거나 고친 내용이 가는 곳 | 자세한 설명 |
|---|---|---|
| Exchange Online | 복구 가능한 항목 폴더 (Recoverable Items) 의 하위 폴더[4] | 이 쪽 아래 "구조" |
| SharePoint·OneDrive | 숨은 시스템 위치인 보존 보류 라이브러리 (Preservation Hold library)[7] | [SharePoint·OneDrive](sharepoint-onedrive.md) |
| Teams | 고치거나 지운 메시지의 원본은 복구 가능한 항목의 `SubstrateHolds`[4] | [Teams](teams.md) |

## 구조

### 복구 가능한 항목 폴더 (Exchange Online)

사용자 메일함은 받은 편지함·보낸 편지함 같은 보이는 폴더가 있는 IPM 하위 트리와, 내부 데이터가 있는 non-IPM 하위 트리로 나뉩니다[4]. 복구 가능한 항목 폴더는 non-IPM 하위 트리에 있어서 Outlook 같은 메일 앱에는 보이지 않지만, Exchange 검색이 색인하므로 eDiscovery 로 찾을 수 있습니다[4].

| 하위 폴더 | 들어가는 것 | 사용자에게 보이나 |
|---|---|---|
| `Deletions` | 지운 편지함에서 지운 항목, Shift+Delete 로 지운 항목 | Outlook 의 "지운 항목 복구" 로 보임[4] |
| `Versions` | 보류나 보존 정책이 걸렸을 때 원본과 고치기 전 사본 | 안 보임[4] |
| `Purges` | 소송 보존 (Litigation Hold) 이나 단일 항목 복구가 켜졌을 때 하드 삭제한 항목 | 안 보임[4] |
| `Audits` | 메일함 감사 로그가 켜져 있을 때 감사 항목 | — [4] |
| `DiscoveryHolds` | 원본 위치 보존 (In-Place Hold) 쿼리나 보존 정책에 맞는 하드 삭제 항목 | — [4] |
| `Calendar Logging` | 일정 변경 기록 | 안 보임[4] |
| `SubstrateHolds` | 보류·Teams 채팅 보존 정책이 걸렸을 때 고치거나 지운 Teams 메시지의 원본 | 안 보임[4] |

지운 항목 보관 기간 기본값은 14일이고 메일함마다 최대 30일까지 늘릴 수 있으며, 일정 항목은 120일 뒤에 지워집니다[4]. 소송 보존이나 원본 위치 보존이 걸리면 관리 폴더 도우미 (Managed Folder Assistant) 가 `DiscoveryHolds`·`Deletions`·`Purges` 를 자동으로 비우지 않고, 사용자도 이 폴더에서 항목을 지울 수 없습니다[4].

보류 중인 메일함에서는 쓰기 시 복사 (copy-on-write) 도 켜집니다. 메시지와 게시물은 제목·본문·첨부·보낸 사람과 받는 사람·보낸 날짜와 받은 날짜가 바뀔 때 원본을 `Versions` 에 남기고, 그 밖의 항목은 보이는 속성이 바뀌면 원본을 남깁니다[4]. 폴더 사이 이동과 읽음 표시 변경은 사본을 만들지 않습니다[4].

복구 가능한 항목 폴더에는 할당량이 따로 있습니다. 기본은 경고 20GB·한도 30GB 이고, 보류나 보존 정책이 걸리면 90GB·100GB 로 늘어나며, 보관 사서함 (archive) 이 켜져 있으면 95GB·105GB 가 됩니다[4].

### 보존 규칙이 겹칠 때

한 항목에 보존 설정이 여럿 걸리면 다음 순서로 결과가 정해집니다[5].

1. 보존이 삭제보다 앞섭니다. 사용자가 지워서 기본 화면에서 사라져도 영구 삭제는 멈춥니다.
2. 보존 기간이 가장 긴 설정을 따릅니다.
3. 삭제끼리 부딪히면 항목에 직접 붙은 보존 레이블의 삭제가 보존 정책의 삭제보다 앞섭니다.
4. 그래도 정해지지 않으면 가장 짧은 삭제 기간을 따릅니다.

eDiscovery 보류가 걸린 항목은 첫째 규칙을 따르므로 어떤 보존 정책이나 레이블로도 영구 삭제되지 않고, 보류를 풀면 그때부터 다시 보존 규칙을 따릅니다[5]. 보존 잠금 (Preservation Lock) 을 건 정책은 관리자도 끄거나 지우거나 약하게 바꿀 수 없습니다[5].

Exchange 에서는 타이머 작업이 복구 가능한 항목 폴더를 주기적으로 검사해 남길 이유가 없는 항목을 하드 삭제하며, 이 작업은 한 번 도는 데 최대 7일이 걸리고 메일함에 데이터가 10MB 이상 있어야 보존 설정이 적용됩니다[6]. 보존 기간이 끝난 항목은 기본 14일 안에 영구 삭제되고, 이 값은 30일까지 늘릴 수 있습니다[6]. 퇴사자 계정을 지울 때 메일함에 보존 정책이 걸려 있으면 비활성 메일함 (inactive mailbox) 이 되고, 그 내용은 계속 eDiscovery 검색 대상입니다[6].

### eDiscovery 감사 기록

eDiscovery 작업 기록은 통합 감사 로그의 한 레코드 유형으로 남습니다. 클래식 기준으로 포털 작업은 `RecordType` 24, eDiscovery cmdlet 작업은 18 이고[3], Hawk 는 `Search-UnifiedAuditLog -RecordType 'Discovery'` 로 이 기록을 모읍니다[9]. 레코드의 공통 필드는 [레코드 구조](unified-audit-log/record-structure.md) 에 있고, 여기서는 eDiscovery 기록에만 있는 필드를 봅니다.

| 필드 | 뜻 |
|---|---|
| `CaseId`, `CaseName` | 만들거나 바꾸거나 지운 사례의 GUID 와 이름[2] |
| `ObjectId`, `ObjectName`, `ObjectType` | 작업 대상인 검색·보류·검토 세트의 GUID·이름·종류[2] |
| `DataSources` | 작업에 걸린 원본 ID·이름·위치[2] |
| `QueryText`, `QueryId` | 검색 통계·검토 세트 추가 같은 작업에 쓴 쿼리 문자열과 그 GUID[2] |
| `ExportName`, `JobId` | 내보내기 이름, eDiscovery 처리 작업의 GUID[2] |
| `Settings`, `ExtendedProperties` | 작업에 쓴 설정, 바뀐 멤버 목록 같은 추가 정보[2] |
| `Item` | 작업 대상 항목 이름, 예를 들어 검토 세트에서 연 문서 이름[2] |
| `UserCancelled` | 사용자가 작업을 취소했는지[2] |
| `StartTime`, `CreationTime` | 작업 시작 시각과 기록 생성 시각, 둘 다 UTC[2] |
| `ClientIP` | 작업한 기기의 IP, 새 환경 작업에는 항상 있음[2] |

클래식 기록에는 `ExchangeLocations`, `SharepointLocations`, `PublicFolderLocations`, `Exclusions`, `Query`, `Parameters` 가 들어갈 수 있고, 모든 eDiscovery 작업의 `SecurityComplianceCenterEventType` 은 0 입니다[3].

조사에서 자주 보는 작업 이름은 다음과 같습니다. 전체 목록은 [작업 이름](unified-audit-log/operations.md) 과 참고 문헌 [2][3] 에 있습니다.

| 하는 일 | 새 환경 작업[2] | 클래식 작업 (cmdlet)[3] |
|---|---|---|
| 사례 만들기·지우기 | `CaseAdded`, `CaseRemoved` | `CaseAdded` (`New-ComplianceCase`), `CaseRemoved` |
| 사례 멤버 바꾸기 | `CaseMembersUpdated` | `CaseMemberAdded`, `CaseMemberRemoved`, `CaseMemberUpdated` |
| 보류 만들기·바꾸기·지우기 | `HoldCreated`, `HoldUpdated`, `HoldRemoved` | `HoldCreated` (`New-CaseHoldRule`), `HoldUpdated`, `HoldRemoved` |
| 검색 만들기·고치기·지우기 | `PurviewSearchAdded`, `PurviewSearchUpdated`, `PurviewSearchDeleted` | `SearchCreated` (`New-ComplianceSearch`), `SearchUpdated`, `SearchRemoved` |
| 검색 실행·통계·샘플 | `PurviewSearchStatisticsJobSubmitted`, `PurviewSearchSampleJobSubmitted`, `SampleResultsViewed` | `SearchStarted` (`Start-ComplianceSearch`), `SearchPreviewed`, `PreviewItemListed` |
| 내보내기 | `PurviewSearchExportJobSubmitted`, `ReviewSetExportJobSubmitted`, `PurviewSearchExportJobDeleted` | `SearchExported` (`New-ComplianceSearchAction`), `SearchExportDownloaded`, `RemovedSearchExported` |
| 한 항목 내려받기·열기 | `ReviewSetDocumentViewed` | `PreviewItemDownloaded` |
| 검색 결과 삭제 | — | `SearchResultsPurged` (`New-ComplianceSearchAction -Purge`) |
| 검토 세트 | `ReviewSetAdded`, `PurviewSearchAddToReviewSetJobSubmitted`, `ReviewSetDocumentsTaggedById` | — |

클래식 `SearchExportDownloaded` 는 사용자가 검색 결과를 자기 컴퓨터로 내려받은 기록이고, 그 전에 `SearchExported` 가 먼저 있어야 합니다[3]. 새 환경 표에는 "내려받음" 에 해당하는 작업이 따로 없으므로, 새 환경에서는 `PurviewSearchExportJobSubmitted` 로 내보내기를 시작한 사람과 `ExportName` 을 확인하고 내려받은 사실은 다른 기록과 맞춰 봅니다.

## 증거로서 의미

**증명하는 것**

- 복구 가능한 항목 폴더·보존 보류 라이브러리에서 찾은 항목은 사용자가 지우거나 고치기 전에 그 내용이 메일함·사이트에 있었다는 것을 보여 줍니다. `Versions` 에 있는 사본은 제목·본문·첨부 같은 속성이 나중에 바뀌었다는 것을 보여 줍니다[4].
- eDiscovery 감사 기록은 어떤 계정이 어느 시각에 어떤 사례에서 어떤 쿼리로 검색하고, 보류를 걸거나 풀고, 결과를 내보냈는지를 보여 줍니다[2][3].
- `HoldRemoved` 는 그 시각에 보류가 풀려 해당 위치가 다시 일반 삭제 흐름으로 돌아갔다는 것을 보여 줍니다[2][3].

**증명하지 못하는 것**

- eDiscovery 결과에 항목이 없다고 해서 그 항목이 없었다는 뜻은 아닙니다. 보존이 걸리기 전에 영구 삭제된 항목은 찾을 수 없고, OneDrive 휴지통은 색인되지 않아 검색도 보류도 그 안의 내용을 찾지 못합니다[8].
- 사용자가 만든 폴더를 Shift+Delete 로 지우면 보류 중이어도 폴더 자체는 되살릴 수 없고, 안의 항목만 `Deletions` 로 갑니다[4]. 폴더 구조는 사라질 수 있습니다.
- 내보내기 작업 기록은 결과 묶음을 만든 사실까지만 보여 주고, 그 파일이 어디로 옮겨졌는지는 보여 주지 않습니다.
- eDiscovery 감사 기록에는 사례 멤버 변경(`CaseMembersUpdated`, 클래식 `CaseMemberAdded` 등)과 클래식 eDiscovery 관리자 변경(`CaseAdminAdded` 등)이 남습니다[2][3]. 누가 eDiscovery 권한을 갖게 되었는지 전체는 역할과 역할 할당에서 따로 봅니다(아래 "공개 도구").

## 시각 해석

eDiscovery 감사 기록의 `CreationTime` 과 `StartTime` 은 UTC 입니다[2]. 클래식 기준으로 `CreationTime` 은 작업이 끝난 시각, `StartTime` 은 작업을 시작한 시각이라서[3], 오래 걸린 검색이나 내보내기는 두 값의 차이가 큽니다.

감사 기록이 검색에 나타나기까지 시간이 걸립니다. 클래식 기준으로 포털 eDiscovery 작업은 30분 안에, eDiscovery cmdlet 작업은 최대 24시간 뒤에 나타납니다[3]. 방금 한 작업이 보이지 않으면 시간을 두고 다시 검색합니다. 감사 로그 전체의 기록 지연과 포털 표시 시간대는 [검색과 내보내기](unified-audit-log/search-export.md) 에 정리했습니다.

항목이 복구 가능한 항목 폴더로 옮겨진 시각은 메일함 감사의 `SoftDelete`·`HardDelete` 기록으로 봅니다([메일함 감사](exchange-online/mailbox-auditing.md)).

## 함정과 한계

- **감사 항목도 보존 공간을 씁니다.** 복구 가능한 항목 폴더가 할당량에 차면 항목을 지울 수도, 고치기 전 사본을 남길 수도 없고, 메일함 감사 항목도 `Audits` 에 저장되지 않습니다[4]. 보류가 없는 메일함은 경고 할당량에 닿으면 오래된 항목부터 먼저 지웁니다[4].
- **보류를 풀면 보존이 끝납니다.** 사례를 지우려면 보류부터 풀어야 하므로[2][3], 보류가 있던 사례라면 `CaseRemoved` 앞에 `HoldRemoved` 가 있습니다. 조사 대상 계정에 사례·보류 권한이 있었다면 이 순서를 확인합니다.
- **검색 후 삭제 기능이 있습니다.** eDiscovery 로 메일·Teams 채팅·Copilot 과 AI 앱 데이터를 검색해 지울 수 있습니다[1]. 클래식에서는 `SearchResultsPurged` 로 남습니다[3].
- **경고 정책은 따로 켜야 합니다.** `eDiscovery search started or exported` 경고로 PST 내보내기를 찾으려면 이 경고 정책이 켜져 있어야 합니다[11]. 경고 정책이 꺼져 있으면 기록 내용에서 `New-ComplianceSearchAction`·`Export`·`pst` 문자열을 함께 찾습니다[11].
- **조사자 작업도 섞입니다.** 조사팀이 수집하면서 만든 사례·검색·내보내기도 같은 기록에 남으므로, 수집 경위를 보고서에 적어 두고 조사팀 계정의 작업을 먼저 걸러 냅니다.
- **감사 기록 자체의 보존 기간**은 통합 감사 로그 규칙을 따릅니다([통합 감사 로그](unified-audit-log/index.md)).

## 직접 분석해 보기

### 감사 기록 한 줄 따라가기

아래는 새 환경에서 검색 결과 내보내기를 시작한 기록을 필드 이름에 맞춰 만든 예시입니다. 값은 모두 지어낸 것입니다.

```json
{
  "CreationTime": "2026-03-04T02:17:45",
  "Operation": "PurviewSearchExportJobSubmitted",
  "RecordType": 24,
  "UserId": "analyst@contoso.com",
  "ClientIP": "203.0.113.25",
  "CaseName": "HR-2026-001",
  "CaseId": "11111111-2222-3333-4444-555555555555",
  "ObjectName": "Mailbox keyword search",
  "ObjectType": "Search",
  "ExportName": "Export-0304",
  "QueryText": "subject:\"quarterly plan\"",
  "DataSources": "user01@contoso.com"
}
```

읽는 순서는 이렇습니다. `CreationTime` 이 UTC 이므로 조사 기준 시간대로 바꿉니다. `ClientIP` 가 있으니 새 환경 작업이고, `UserId` 가 조사팀 계정인지 확인합니다. `CaseName`·`ObjectName`·`QueryText`·`DataSources` 로 누구의 메일함을 어떤 조건으로 검색했는지 보고, 같은 `CaseId` 로 앞뒤 기록을 모아 사례 생성부터 내보내기까지 순서를 세웁니다.

### 공개 도구

- **Hawk** 의 `Get-HawkTenantEDiscoveryLog` 는 `RecordType` Discovery 기록을 모아 `eDiscoveryLogs` 와 줄인 `Simple_eDiscoveryLogs` 를 CSV·JSON 으로 남깁니다[9]. `Get-HawkTenantEDiscoveryConfiguration` 은 `New-MailboxSearch`·`Search-Mailbox` 가 든 관리 역할을 `EDiscoveryRoles` 로, 그 역할의 할당을 `CustomEDiscoveryRoles` 로 CSV·JSON 에 남깁니다[10].
- **Untitled Goose Tool** 은 `New-MailboxSearch`·`Search-Mailbox` 를 포함한 관리 역할을 찾아 역할 항목 (`Get-ManagementRoleEntry`) 과 역할 할당 (`Get-ManagementRoleAssignment`) 을 JSON 으로 저장합니다[12].
- 포털에서는 Purview 포털의 감사 (Audit) 검색에서 eDiscovery 작업을 골라 검색하고 CSV 로 내보낼 수 있습니다[3]. 수집 도구 전반은 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md) 에 있습니다.

보존된 메일·파일 내용은 eDiscovery 검색으로 찾아 내보냅니다. 검색 대상에 복구 가능한 항목 폴더가 들어가는지, 내보내기 설정에 부분 색인 항목을 넣었는지를 수집 기록에 남깁니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [메일함 감사](exchange-online/mailbox-auditing.md) | 보존된 메일이 언제 누가 지웠는지 (`SoftDelete`, `HardDelete`), 다른 사람 메일함 접근 |
| [SharePoint·OneDrive](sharepoint-onedrive.md) | 보존 보류 라이브러리, 휴지통과 버전 |
| [Teams](teams.md) | 지우거나 고친 채팅이 `SubstrateHolds` 로 가는 흐름 |
| [Entra ID 로그](entra-logs/index.md) | eDiscovery 작업 계정의 로그인 IP·시각과 역할 변경 |
| [Defender 경고와 기록](defender-xdr.md) | eDiscovery 검색·내보내기 경고 |
| [클라우드 타임라인](../../03-techniques/analysis/timeline.md) | 사례 생성·보류·내보내기와 삭제 기록을 한 줄로 세우기 |

## 실습

Microsoft 365 개발자·평가판 테넌트에서 만든 계정으로 풀어 봅니다.

1. 한 메일함에 보류를 건 뒤 메일 하나의 제목을 고치고 다른 메일을 Shift+Delete 로 지웁니다. eDiscovery 검색에서 두 메일이 각각 어느 하위 폴더에 나타나는지 확인합니다.
2. 사례를 만들고 검색·통계·내보내기를 차례로 한 뒤, 감사 로그에서 `CaseId` 가 같은 기록을 모아 작업 이름과 `CreationTime`·`StartTime` 차이를 표로 정리합니다.
3. 보류를 풀고 사례를 지운 뒤 `HoldRemoved`·`CaseRemoved` 의 순서와 간격을 확인합니다.
4. 보고서 문장으로 "이 계정이 이 시각에 이 사례에서 이 쿼리로 내보내기를 시작한 기록이 있다" 처럼 기록이 말하는 만큼만 적어 봅니다([클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)).

## 참고 문헌

1. Microsoft, "Learn about eDiscovery", Microsoft Learn, 2026-06-29 갱신. https://learn.microsoft.com/en-us/purview/edisc
2. Microsoft, "Audit log activities" (eDiscovery activities), Microsoft Learn, 2026-09-08 갱신. https://learn.microsoft.com/en-us/purview/audit-log-activities
3. Microsoft, "Search for eDiscovery (classic) activities in the audit log", Microsoft Learn, 2025-02-12 갱신. https://learn.microsoft.com/en-us/purview/ediscovery-search-for-activities-in-the-audit-log
4. Microsoft, "Recoverable Items folder in Exchange Online", Microsoft Learn, 2026-07-13 갱신. https://learn.microsoft.com/en-us/exchange/security-and-compliance/recoverable-items-folder/recoverable-items-folder
5. Microsoft, "Learn about retention policies and retention labels", Microsoft Learn, 2026-07-22 갱신. https://learn.microsoft.com/en-us/purview/retention
6. Microsoft, "Learn about retention for Exchange", Microsoft Learn, 2025-09-26 갱신. https://learn.microsoft.com/en-us/purview/retention-policies-exchange
7. Microsoft, "Learn about retention for SharePoint and OneDrive", Microsoft Learn, 2025-09-22 갱신. https://learn.microsoft.com/en-us/purview/retention-policies-sharepoint
8. Microsoft, "OneDrive retention and deletion", Microsoft Learn, 2026-06-23 갱신. https://learn.microsoft.com/en-us/sharepoint/retention-and-deletion
9. T0pCyber, Hawk, `Get-HawkTenantEDiscoveryLog.ps1`. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Get-HawkTenantEDiscoveryLog.ps1
10. T0pCyber, Hawk, `Get-HawkTenantEDiscoveryConfiguration.ps1`. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Get-HawkTenantEDiscoveryConfiguration.ps1
11. SigmaHQ, "PST Export Alert Using eDiscovery Alert", "PST Export Alert Using New-ComplianceSearchAction". https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/threat_management/microsoft365_pst_export_alert.yml , https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/threat_management/microsoft365_pst_export_alert_using_new_compliancesearchaction.yml
12. CISA, Untitled Goose Tool, `goosey/m365_datadumper.py` (`dump_ediscovery_info`). https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/m365_datadumper.py
