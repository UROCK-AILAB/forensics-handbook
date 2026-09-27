---
title: "SharePoint·OneDrive"
parent: "아티팩트 · Microsoft 365"
nav_order: 250
---

# SharePoint·OneDrive

SharePoint 사이트와 OneDrive 에서 파일을 열고, 내려받고, 동기화하고, 공유하고, 지운 일은 통합 감사 로그에 파일 경로와 함께 남고, 지우거나 고친 파일의 원본은 보존 설정에 따라 서비스 안에 한동안 남습니다.

## 무엇을 기록하나 · 왜 생기나

OneDrive 는 사용자 한 사람의 개인 사이트이고, SharePoint 는 팀·부서 사이트입니다. 두 서비스의 파일 작업은 같은 기록 체계를 쓰고, [통합 감사 로그 (Unified Audit Log)](unified-audit-log/index.md)에 `Workload` 가 `SharePoint` 또는 `OneDrive` 인 레코드로 들어갑니다[6]. 유출 조사에서 "누가 언제 어느 파일을 받아 갔나", "누가 언제 파일을 밖으로 공유했나", "누가 무엇을 지웠나" 를 답하는 기본 자료가 이 기록입니다.

조사에 자주 쓰는 작업 이름 (Operation) 은 다음과 같습니다[1][4]. 전체 목록은 [주요 작업 이름](unified-audit-log/operations.md)에 있습니다.

| 분류 | Operation | 뜻 |
|---|---|---|
| 읽기 | `FileAccessed`, `FileAccessedExtended`, `FilePreviewed` | 파일 열기, 같은 사람이 오래(최대 3시간) 계속 연 경우의 묶음 기록, 미리 보기 |
| 내려받기·동기화 | `FileDownloaded`, `FileSyncDownloadedFull` | 사이트에서 내려받기, OneDrive 동기화 앱(OneDrive.exe)으로 PC 에 받기 |
| 올리기·고치기 | `FileUploaded`, `FileSyncUploadedFull`, `FileModified`, `FileModifiedExtended` | 올리기, 동기화 앱으로 올리기, 내용·속성 고치기 |
| 옮기기 | `FileCopied`, `FileMoved`, `FileRenamed` | 복사, 이동, 이름 바꾸기 |
| 지우기 | `FileRecycled`, `FileDeleted`, `FileDeletedFirstStageRecycleBin`, `FileDeletedSecondStageRecycleBin`, `FileRestored` | 휴지통으로 보내기, 삭제, 휴지통에서 삭제, 2단계 휴지통에서 삭제, 휴지통에서 복원 |
| 판 지우기 | `FileVersionRecycled`, `FileVersionsAllRecycled`, `FileVersionsAllMinorsRecycled` | 버전 기록에서 판 하나·전부·부 버전 전부를 사이트 휴지통으로 보내기 |
| 공유 | `SharingSet`, `AddedToGroup` | 구성원·게스트가 디렉터리에 있는 사용자와 공유, 공유 등으로 SharePoint 그룹에 구성원·게스트 추가 |
| 공유 | `SharingInvitationCreated`, `SharingInvitationAccepted` | 디렉터리에 없는 사용자에게 초대 보내기, 초대 수락 |
| 링크 | `AnonymousLinkCreated`, `AnonymousLinkUsed`, `AnonymousLinkUpdated`, `AnonymousLinkRemoved` | 누구나 링크 (Anyone link) 만들기·사용·변경·삭제 |
| 링크 | `CompanyLinkCreated`, `CompanyLinkUsed` | 조직 안 사람만 쓰는 링크 만들기·사용(게스트는 쓸 수 없음) |
| 링크 | `SecureLinkCreated`, `AddedToSecureLink`, `SecureLinkUsed` | 특정 사용자 링크 (specific people link) 만들기, 링크에 사람 추가, 사용 |
| 권한 | `SharingRevoked`, `SharingInheritanceBroken`, `AccessRequestCreated`, `SiteCollectionAdminAdded` | 공유 해제, 상위 폴더와 권한 분리, 접근 요청, 사이트 모음 관리자 추가 |
| 동기화 제한 | `ManagedSyncClientAllowed`, `UnmanagedSyncClientBlocked` | 허용된 도메인 PC 의 동기화 연결 성공, 허용되지 않은 PC 의 동기화 차단 |
| 검색 | `SearchQueryPerformed` | SharePoint·OneDrive 검색. 따로 켜야 기록됨 |

`SiteCollectionAdminAdded` 는 관리자가 SharePoint 관리 센터나 Microsoft 365 관리 센터에서 다른 사용자의 OneDrive 에 스스로 접근 권한을 줄 때도 남습니다[1]. 관리자가 남의 OneDrive 를 열어 본 사건에서는 이 작업을 먼저 찾습니다.

클라우드 기록과 별도로, 사용자 PC 의 OneDrive 동기화 앱과 Office 도 파일 이름과 시각을 남깁니다. 이 부분은 아래 교차 검증 절에서 다룹니다.

## 위치와 버전별 차이

감사 기록은 통합 감사 로그 하나에 모이고, 보는 방법은 Purview 포털 검색, Exchange Online PowerShell 의 `Search-UnifiedAuditLog`, Graph 감사 검색 API, Office 365 관리 활동 API (Management Activity API) 입니다[6]. 관리 활동 API 에서는 `Audit.SharePoint` 콘텐츠 유형으로 받습니다[15]. 검색 조건과 건수 한도는 [검색과 내보내기](unified-audit-log/search-export.md)에 정리했습니다.

보관 기간은 사용자 라이선스에 따라 다릅니다(2026년 9월 문서 기준)[6][14].

| 라이선스 | SharePoint·OneDrive 감사 기록 보관 |
|---|---|
| Audit (Standard) — E5 가 아닌 Microsoft 365·Office 365 사용자 | 180일. 2023년 10월 17일 이전에 생긴 기록은 90일 |
| Audit (Premium) — Office 365·Microsoft 365 E5, 또는 Purview Suite(옛 E5 Compliance)·E5 eDiscovery and Audit 추가 라이선스 사용자 | 1년. `Workload` 가 `SharePoint`·`OneDrive` 인 기록은 기본 정책으로 1년 보관 |
| 10년 보존 추가 라이선스 + 10년 정책 | 10년. 정책을 만든 뒤 들어온 기록부터 적용 |

사용자 정의 보존 정책이 기본 정책보다 앞서므로, Premium 사용자라도 1년보다 짧은 정책이 걸려 있으면 그만큼만 남습니다[6]. 라이선스별 비교와 정책 확인 방법은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)를 봅니다.

기록 종류 (RecordType) 는 파일 작업이면 `SharePointFileOperation`(6), 공유 작업이면 `SharePointSharingOperation`(14) 이고, 이 밖에 `SharePoint`(4), `OneDrive`(7), `SharePointSearch`(102) 같은 값이 있습니다[2]. `Search-UnifiedAuditLog` 의 `-RecordType` 에는 값을 하나만 줄 수 있어서 파일 작업과 공유 작업을 나눠 검색합니다[13].

## 구조

모든 레코드에 공통으로 있는 `CreationTime`·`UserId`·`ClientIP`·`ObjectId`·`UserKey` 같은 필드는 [레코드 구조](unified-audit-log/record-structure.md)에 있습니다. SharePoint 기록에는 다음 필드가 더 붙습니다[2][3].

| 필드 | 뜻 |
|---|---|
| `Site` | 파일이 있는 사이트의 GUID |
| `SiteUrl` | 사이트 URL |
| `SourceRelativeUrl` | 파일이 들어 있는 폴더의 URL |
| `SourceFileName`, `SourceFileExtension` | 파일 이름과 확장자. 폴더면 확장자는 빈 값 |
| `DestinationRelativeUrl`, `DestinationFileName`, `DestinationFileExtension` | 복사·이동한 대상 위치와 이름. `FileCopied`·`FileMoved` 에만 있음 |
| `ItemType` | 대상 종류. File, Folder, Web, Site, Tenant, DocumentLibrary, Page |
| `EventSource` | `SharePoint` 또는 `ObjectModel` |
| `UserAgent` | 사용자의 클라이언트·브라우저가 보낸 정보 |
| `MachineDomainInfo`, `MachineId` | 동기화 작업의 기기 정보. 요청에 들어 있을 때만 있음 |
| `ApplicationId`, `ApplicationDisplayName` | 작업을 수행한 앱의 ID 와 이름 |
| `IsWorkflow` | SharePoint 워크플로가 일으킨 작업이면 True |

`SiteUrl`·`SourceRelativeUrl`·`SourceFileName` 을 이으면 `ObjectId` 와 같은 값, 곧 파일의 전체 경로가 됩니다[2][3]. OneDrive 파일이면 `ObjectId` 가 `https://contoso-my.sharepoint.com/personal/사용자_도메인/Documents/...` 모양이라 경로만 보고 어느 사용자의 OneDrive 인지 알 수 있습니다[4].

공유 기록에는 공유 스키마 필드가 더 붙습니다[2][4].

| 필드 | 뜻 |
|---|---|
| `TargetUserOrGroupName` | 공유받은 사용자의 UPN 이나 그룹 이름 |
| `TargetUserOrGroupType` | 공유받은 대상의 종류. 조직 밖 사용자는 `Guest` |
| `EventData` | 그룹 추가, 편집 권한 부여처럼 공유에 뒤따른 내용(XML) |
| `UniqueSharingId` | 공유 작업의 고유 ID |

`TargetUserOrGroupType` 의 값 목록은 문서마다 조금 다릅니다. 관리 활동 API 스키마는 Member·Guest·Group·Partner 로[2], 공유 감사 문서는 Member·Guest·SharePointGroup·SecurityGroup·Partner 로 적습니다[4]. 조직 밖 공유를 거를 때 쓰는 `Guest` 는 두 문서에 같이 있습니다.

아래는 사용자가 자기 OneDrive 의 파일을 브라우저로 내려받은 모양을 만든 예시입니다. 필드 이름은 문서를 따랐고, 값은 모두 지어낸 값입니다.

```json
{
  "CreationTime": "2026-03-02T01:14:07",
  "Id": "3f2a9c1e-0000-4000-8000-000000000001",
  "Operation": "FileDownloaded",
  "OrganizationId": "11111111-2222-3333-4444-555555555555",
  "RecordType": 6,
  "UserType": 0,
  "Workload": "OneDrive",
  "UserId": "user1@contoso.com",
  "ClientIP": "203.0.113.25",
  "ObjectId": "https://contoso-my.sharepoint.com/personal/user1_contoso_com/Documents/영업/2026 계획.xlsx",
  "Site": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "SiteUrl": "https://contoso-my.sharepoint.com/personal/user1_contoso_com/",
  "SourceRelativeUrl": "Documents/영업",
  "SourceFileName": "2026 계획.xlsx",
  "SourceFileExtension": "xlsx",
  "ItemType": "File",
  "EventSource": "SharePoint",
  "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
```

관리 활동 API 스키마는 `ItemType` 을 정수 열거형(1 File, 5 Folder 등)으로 정의하고[2], 감사 속성 문서는 File·Folder 같은 이름으로 설명합니다[3]. 실제 데이터에 숫자와 문자열 가운데 어느 쪽으로 들어 있는지 먼저 봅니다.

## 증거로서 의미

**증명하는 것**

- 이 시각에 이 `UserId` 로 이 경로(`ObjectId`)의 파일에 이 작업이 서비스에 기록되었다는 것[2].
- 파일이 서비스 밖으로 나갔다는 것. `FileDownloaded` 는 사이트에서 받은 일을, `FileSyncDownloadedFull` 은 OneDrive 동기화 앱으로 PC 에 받은 일을 뜻합니다[1].
- 누가 누구에게 공유했는지. 공유 기록의 `UserId` 가 공유한 사람이고 `TargetUserOrGroupName`·`TargetUserOrGroupType` 이 공유받은 대상입니다[4].
- 누구나 링크로 파일에 접근한 일이 있었다는 것과 그 접속 IP. `AnonymousLinkUsed` 는 사용자 신원을 모를 수 있지만 IP 같은 정보는 남습니다[1].
- 파일을 옮기거나 복사한 곳. `FileCopied`·`FileMoved` 에는 대상 폴더와 이름이 있습니다[2].

**증명하지 못하는 것**

- 내려받은 파일을 그 뒤 어디로 보냈는지. 서비스가 파일을 내려보낸 사실까지만 남고, 기기에서 한 일은 기기 쪽 아티팩트로 봅니다.
- 사람이 화면에서 내용을 실제로 봤는지. 브라우저의 미리 받기 (prefetch) 도 `FilePreviewed` 를 남길 수 있고, `FilePreviewed` 와 `FileAccessed` 의 구분이 사용자의 의도를 보장하지 않습니다[1].
- 누구나 링크를 쓴 사람이 누구인지. 링크는 복사해 넘길 수 있어서, 링크를 만든 기록이 있으면 공유되었다고 보는 것까지만 할 수 있습니다[4].
- 기록된 IP 가 사용자 기기의 주소인지. 일부 서비스는 Office on the web 같은 신뢰된 앱의 IP 를 적습니다[2]. 해석은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md)를 봅니다.
- 파일 내용과 무엇을 고쳤는지. 내용은 감사 로그가 아니라 버전 기록, 보존 사본, eDiscovery 로 확인합니다.

보고서에는 "이 계정으로 이 시각에 이 경로의 파일에 `FileDownloaded` 가 기록되어 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

- `CreationTime` 은 UTC 이고, 레코드가 만들어진 시각입니다[2]. Purview 포털 검색 결과의 날짜 열도 UTC 입니다[5]. 여러 로그를 한 줄로 맞추는 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)을 봅니다.
- SharePoint·OneDrive 기록은 보통 작업 뒤 60~90분 안에 검색되지만, Microsoft 는 정해진 시간을 보장하지 않습니다[5]. 사건 직후에 보이지 않는 기록은 나중에 다시 검색합니다.
- `FileAccessed` 는 같은 사용자가 같은 파일을 다시 열어도 5분 동안은 다시 기록하지 않습니다[1]. `FileModified` 도 같은 사용자·같은 문서면 5분을 기다렸다가 다음 기록을 남깁니다[1]. 같은 사람이 오래(최대 3시간) 계속 열거나 고치면 `FileAccessedExtended`·`FileModifiedExtended` 로 묶어 기록합니다[1]. 그래서 기록 건수는 실제로 연 횟수와 같지 않습니다.
- `SecureLinkCreated` 와 그 링크에 사람을 넣은 `AddedToSecureLink` 는 시각이 거의 같습니다[4]. 공유받은 사람은 `AddedToSecureLink` 쪽에서 찾습니다.
- 퇴사자의 OneDrive 는 Entra ID 에서 계정을 지운 때부터 정리가 시작됩니다. 로그인 차단이나 라이선스 회수만으로는 시작하지 않습니다[7]. 정리 흐름은 기본 30일 보존(관리자가 `Set-SPOTenant -OrphanedPersonalSitesRetentionPeriod` 로 바꿀 수 있음), 만료 7일 전 알림 메일, 그 뒤 사이트 모음 휴지통에서 93일입니다[7]. 라이선스가 없는 OneDrive 는 라이선스 없이 93일째 되는 날 자동으로 보관 (archive) 되고, 비용을 내지 않은 보관 상태로 12개월이 지나면 보존 설정·보류와 상관없이 지워질 수 있습니다(2026년 6월 문서 기준)[7].
- 보존 설정이 걸린 사이트에서 지우거나 고친 파일의 원본은 보존 보관 라이브러리 (Preservation Hold library) 에 복사됩니다. 이 라이브러리의 타이머 작업은 들어온 지 30일이 넘은 항목을 7일마다 검사하므로, 보존 기간이 지난 항목이 이 라이브러리에서 지워지기까지 최대 37일이 걸릴 수 있습니다[8]. 여기서 지운 항목은 2단계 휴지통으로 가서 93일 뒤 영구 삭제됩니다[8]. 사용자가 지운 파일은 1단계 휴지통을 거쳐 2단계 휴지통으로 가고, 두 휴지통을 합쳐 93일이 지나면 영구 삭제됩니다[8].

## 함정과 한계

- **작업자가 사람이 아닐 수 있습니다.** `UserId` 가 `SHAREPOINT\system` 이면 시스템 계정이고, `app@sharepoint` 이면 조직 전체 권한을 가진 앱이 사용자·관리자·서비스를 대신해 한 작업입니다[2][3]. eDiscovery 보류나 보존 정책을 적용할 때 서비스 계정이 `SearchQueryPerformed` 를 남기기도 합니다[1]. Insider Risk Management 에서 사례를 만들고 콘텐츠 탐색기를 켜도 `FileAccessed` 가 생기며, 이 기록은 `ApplicationId` 값으로 구분할 수 있습니다[1].
- **조사하는 쪽의 작업도 남습니다.** 관리자가 퇴사자의 OneDrive 에 접근 권한을 주면 `SiteCollectionAdminAdded` 가 남으므로[1], 수집 경위를 보고서에 적어 조사자의 기록과 사건 당사자의 기록을 나눕니다.
- **초대 기록은 사이트 공유에만 남습니다.** 디렉터리에 없는 사용자와 공유할 때 `SharingInvitationCreated` 는 공유 대상이 사이트일 때만 기록되고, 파일은 `AnonymousLinkCreated`·`SecureLinkCreated`·`AddedToSecureLink` 로 남습니다[4]. 외부 사용자가 특정 사용자 링크로 파일을 열면 `FileAccessed` 가 남습니다[4].
- **공유 한 번이 기록 여러 건을 만듭니다.** 디렉터리에 있는 사용자와 공유하면 SharePoint 가 먼저 그 사용자를 SharePoint 그룹에 넣어 `AddedToGroup` 을 남기고, 이어 `SharingSet` 을 남깁니다[4]. 사용자가 파일 공유 링크를 처음 만들 때는 그 사용자의 OneDrive 에 시스템 그룹이 생기면서 `GroupAdded` 도 남습니다[1].
- **폐지된 작업 이름이 있습니다.** `FileSyncDownloadedPartial`·`FileSyncUploadedPartial` 은 옛 동기화 앱(Groove.exe)과 함께 폐지되었습니다[1]. 오래된 기록과 요즘 기록을 비교할 때 이름이 달라진 것을 활동이 사라진 것으로 읽지 않습니다.
- **검색 작업 이름은 출처마다 다릅니다.** 감사 작업 문서에는 SharePoint 검색이 `SharepointSearchQueryInitiated` 와 `SearchQueryPerformed` 로 실려 있고[1], Hawk 는 `SearchQueryInitiatedSharePoint` 로 검색합니다[11]. SharePoint 검색 기록은 Audit (Premium) 라이선스를 받은 사용자에게만 남습니다[6]. 받은 데이터에 실제로 들어 있는 `Operation` 값을 먼저 확인하고 그 값으로 검색합니다.
- **휴지통은 eDiscovery 로 찾을 수 없습니다.** 휴지통은 색인되지 않아서 검색되지 않고, eDiscovery 보류도 휴지통 안 내용을 붙잡지 못합니다[7][8]. 지운 파일은 휴지통 단계와 보존 보관 라이브러리를 따로 봅니다. 보류와 검색은 [Purview eDiscovery와 보존](purview-ediscovery.md)을 봅니다.
- **보존 사본이 모든 판을 갖고 있지는 않습니다.** 처음 편집할 때는 새 내용이 보존 보관 라이브러리에 복사되지 않으므로, 모든 판을 남기려면 사이트에 버전 관리가 켜져 있어야 합니다[8]. 버전 관리는 기본으로 주 버전을 최소 500개 남깁니다[8]. 2022년 7월 이후에는 한 파일의 판들을 보존 보관 라이브러리에 파일 하나로 저장하고, 그 전에 복사된 판은 따로 된 파일로 남아 있습니다[8].
- **경고 이름은 감사 작업 이름이 아닙니다.** `Unusual volume of file deletion`, `Suspicious OAuth app file download activities` 는 Defender for Cloud Apps 의 이상 탐지 경고 이름이고, Sigma 규칙도 이 경고 이름으로 찾습니다[12]. 경고가 없다고 대량 삭제·대량 다운로드가 없었던 것은 아니므로 감사 기록에서 작업 이름으로 직접 셉니다.

## 직접 분석해 보기

**원자료를 한 번 직접 읽기.** 감사 기록의 `AuditData` 만 한 줄에 하나씩 저장한 JSON 파일이 있으면, 반출과 공유에 해당하는 작업만 골라 시각·작업자·작업·IP·경로·공유 대상을 뽑아 봅니다.

```sh
jq -r 'select(.Operation | test("^(FileDownloaded|FileSyncDownloadedFull|FileCopied|FileMoved|SharingSet|SharingInvitation|AnonymousLink|CompanyLink|SecureLink|AddedToSecureLink)"))
  | [ .CreationTime, .UserId, .Operation, (.ClientIP // ""), .ObjectId,
      (.TargetUserOrGroupName // ""), (.TargetUserOrGroupType // "") ]
  | @tsv' auditdata.jsonl | sort
```

조직 밖 공유만 보려면 `TargetUserOrGroupType` 이 `Guest` 인 줄을 고릅니다[4]. 같은 `ObjectId` 로 `FileUploaded`·`FileAccessed`·`AnonymousLinkCreated`·`AnonymousLinkUsed` 를 이어 보면 파일 하나가 올라와서 밖으로 나가기까지의 흐름이 나옵니다. `AuditData` 를 CSV 로 내보낸 경우 JSON 펼치는 방법과 주의점은 [JSON 로그 읽기](../../01-foundations/logging/json-logs.md)와 [검색과 내보내기](unified-audit-log/search-export.md)를 봅니다.

**PowerShell 로 범위를 좁혀 받기.** `Search-UnifiedAuditLog` 의 `-ObjectIds` 에 사이트 URL 과 와일드카드를 주면 사이트 하나, 또는 OneDrive 하나의 기록만 받을 수 있습니다[5].

```powershell
Search-UnifiedAuditLog -StartDate "2026-03-01 00:00:00z" -EndDate "2026-03-08 00:00:00z" `
  -RecordType SharePointSharingOperation `
  -ObjectIds "https://contoso-my.sharepoint.com/personal/user1_contoso_com/*" `
  -SessionId "case01" -SessionCommand ReturnLargeSet -ResultSize 5000
```

**공개 도구로 받기.** Microsoft-Extractor-Suite 의 `Get-UAL` 은 `-UserIds`·`-RecordType`·`-Operations`·`-ObjectIds` 로 거르고 결과를 CSV·JSON 등으로 저장합니다[10]. Hawk 의 `Get-HawkUserSharePointSearchQuery` 는 사용자 한 명의 SharePoint 검색 기록을 뽑습니다[11]. 도구별 수집 방식과 건수 한도는 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md)를 봅니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 | 링크 |
|---|---|---|
| Entra ID 로그인 로그 | 파일 작업 직전에 같은 계정이 어디서, 어떤 앱으로 로그인했는지 | [Entra ID 로그](entra-logs/index.md) |
| Defender XDR 의 CloudAppEvents | 같은 활동을 IP 위치·익명 프록시 여부 같은 정보와 함께 다시 보기, 대량 다운로드·삭제 경고 | [Defender 경고와 기록](defender-xdr.md) |
| Purview 보존·eDiscovery | 지우거나 고친 파일의 원본과 판, 보류 상태 | [Purview eDiscovery와 보존](purview-ediscovery.md) |
| Teams | 채팅에서 공유한 파일과 회의 녹음이 놓이는 OneDrive 위치 | [Teams](teams.md) |
| 사용자 PC 의 OneDrive·Office 흔적 | 클라우드에서 받은 파일이 실제로 그 PC 에 왔는지 | 아래 설명 |

Windows 에서 Microsoft 365 를 시험한 연구에서는 OneDrive 동기화 앱의 흔적이 `%UserProfile%/AppData/Local/Microsoft/OneDrive/settings/Personal` 또는 `settings/Business` 폴더에 남았습니다[9]. 이 시험에서 `[UserCid].dat` 에는 웹과 앱에서 한 OneDrive 작업(동기화·내려받기·올리기·열기)마다 파일 이름과 시각이 남았고, `SafeDelete.db`(SQLite) 에는 OneDrive 폴더의 파일 목록이 파일 이름만으로 남았습니다[9]. 같은 연구에서 Office 의 `UsageMetricStore/FileActivityStoreV3` 아래 파일에도 로컬 클라우드 저장소 파일을 열거나 만든 기록이 파일 이름·경로와 함께 남았습니다[9]. 감사 로그의 `FileSyncDownloadedFull` 과 PC 쪽 파일 목록이 맞으면 "받았다" 에서 "그 PC 에 있었다" 까지 말할 수 있습니다.

Google Workspace 의 같은 성격 기록은 [Drive 기록](../google-workspace/drive-audit.md)과 비교해 볼 수 있습니다. 조사 흐름은 [외부 공유 링크로 새어 나갔나](../../04-scenarios/data-leak/external-sharing.md), [퇴사자가 자료를 가져갔나](../../04-scenarios/data-leak/departing-employee.md), [클라우드 저장소에서 자료를 빼 갔나](../../04-scenarios/data-leak/storage-exfiltration.md)를 봅니다. 여러 기록을 시간순으로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)을 봅니다.

## 실습

시험용 Microsoft 365 테넌트에서 사용자 둘과 게스트 하나로 기록을 만든 뒤 풀어 봅니다.

1. 한 사용자가 자기 OneDrive 파일에 누구나 링크를 만들고, 로그인하지 않은 브라우저로 그 링크를 엽니다. `AnonymousLinkCreated` 와 `AnonymousLinkUsed` 의 `UserId`·`ClientIP` 는 각각 무엇으로 남나요?
2. 같은 파일을 게스트에게 특정 사용자 링크로 공유하고 게스트가 엽니다. `SecureLinkCreated`·`AddedToSecureLink`·`FileAccessed` 가운데 게스트의 주소는 어느 기록에 있고, 세 기록의 시각 차이는 얼마인가요?
3. 파일 하나를 1분 간격으로 세 번 열고 10분 뒤 다시 엽니다. `FileAccessed` 는 몇 건 남나요?
4. 파일을 휴지통으로 보내고, 휴지통에서 지우고, 2단계 휴지통에서 지웁니다. 단계마다 남는 작업 이름을 차례대로 적어 보세요.
5. 동기화 앱으로 폴더를 받은 PC 에서 `SafeDelete.db` 의 파일 목록과 감사 로그의 `FileSyncDownloadedFull` 목록을 맞춰 봅니다. 한쪽에만 있는 파일은 왜 생겼나요?

## 참고 문헌

1. Microsoft, "Audit log activities", Microsoft Learn (2026-09-08 갱신). https://learn.microsoft.com/en-us/purview/audit-log-activities
2. Microsoft, "Office 365 Management Activity API schema", Microsoft Learn (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
3. Microsoft, "Detailed properties in the audit log", Microsoft Learn (2026-02-18 갱신). https://learn.microsoft.com/en-us/purview/audit-log-detailed-properties
4. Microsoft, "Use sharing auditing in the audit log", Microsoft Learn (2026-06-24 갱신). https://learn.microsoft.com/en-us/purview/audit-log-sharing
5. Microsoft, "Search the audit log", Microsoft Learn (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-search ; "Search-UnifiedAuditLog", MicrosoftDocs/office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Search-UnifiedAuditLog.md
6. Microsoft, "Learn about auditing solutions in Microsoft Purview", Microsoft Learn (2026-05-18 갱신). https://learn.microsoft.com/en-us/purview/audit-solutions-overview
7. Microsoft, "OneDrive retention and deletion", Microsoft Learn (2026-06-23 갱신). https://learn.microsoft.com/en-us/sharepoint/retention-and-deletion
8. Microsoft, "Learn about retention for SharePoint and OneDrive", Microsoft Learn (2025-09-22 갱신). https://learn.microsoft.com/en-us/purview/retention-policies-sharepoint
9. Jihun Joun, Sangjin Lee, Jungheum Park, "Data remnants analysis of document files in Windows: Microsoft 365 as a case study", Forensic Science International: Digital Investigation 46 (2023) 301612 (DFRWS APAC 2023). https://doi.org/10.1016/j.fsidi.2023.301612
10. Invictus Incident Response, Microsoft-Extractor-Suite (Get-UAL.ps1). https://github.com/invictus-ir/Microsoft-Extractor-Suite
11. T0pCyber, Hawk (Get-HawkUserSharePointSearchQuery.ps1). https://github.com/T0pCyber/hawk
12. SigmaHQ, Sigma 규칙 rules/cloud/m365/threat_management (microsoft365_unusual_volume_of_file_deletion.yml, microsoft365_susp_oauth_app_file_download_activities.yml). https://github.com/SigmaHQ/sigma
13. Microsoft, "Export, configure, and view audit log records", Microsoft Learn (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-export-records
14. Microsoft, "Manage audit log retention policies", Microsoft Learn (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
15. Microsoft, "Office 365 Management Activity API reference", Microsoft Learn (2024-12-03 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference
