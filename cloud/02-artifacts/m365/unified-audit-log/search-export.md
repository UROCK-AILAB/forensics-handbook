---
title: "검색과 내보내기"
parent: "통합 감사 로그"
grand_parent: "아티팩트 · Microsoft 365"
nav_order: 150
---

# 검색과 내보내기 (Search·Export)

통합 감사 로그는 Purview 포털 검색, `Search-UnifiedAuditLog`, Graph 감사 검색 API, Office 365 관리 활동 API (Management Activity API) 네 경로로 꺼낼 수 있습니다. 경로마다 검색 범위·한 번에 받는 건수·거슬러 갈 수 있는 기간이 달라서, 어느 경로로 받았는지에 따라 빠지는 기록이 생길 수 있습니다.

## 무엇을 꺼내나 · 왜 경로가 여럿인가

네 경로는 모두 같은 통합 감사 로그를 읽습니다[4][5]. 포털 검색이 밑에서 쓰는 명령은 Exchange Online 의 `Search-UnifiedAuditLog` 이라서, 포털에서 할 수 있는 검색은 PowerShell 로도 할 수 있습니다[1]. Graph 감사 검색 API 는 쿼리(`auditLogQuery`)를 만든 뒤 상태가 `succeeded` 가 되면 `records` 로 결과 레코드를 읽는 방식이고[5], 관리 활동 API 는 구독을 걸어 두고 새로 쌓이는 기록을 계속 받아 가는 방식입니다[7]. Microsoft 는 정기적·대량 수집에는 PowerShell 스크립트 대신 관리 활동 API 를 쓰라고 안내합니다[1][3][4].

레코드 한 건의 필드와 AuditData 안의 속성은 [레코드 구조 (AuditData)](record-structure.md)에, 무엇을 찾을지 정하는 작업 이름은 [주요 작업 이름 (Operations)](operations.md)에 있습니다. 로그가 켜져 있는지, 라이선스별로 얼마나 보관하는지는 [통합 감사 로그 허브](index.md)에서 먼저 확인합니다.

## 경로별 차이

아래 표의 값은 Microsoft 문서 기준입니다(포털·내보내기·스크립트 문서 2026-06-19, Graph 문서 2026-08-14, 관리 활동 API 문서 2024-12-03 갱신).

| 경로 | 한 번에 볼 수 있는 기간 | 건수 한도 | 과거 기록 수집 |
|---|---|---|---|
| Purview 포털 검색 | 기본 최근 7일, 한 검색 최대 180일[1] | 내보내기 Standard 50,000행, Premium 1,000,000행[1][2] | 보관 기간 안이면 가능, 180일 넘는 범위는 나눠 검색 |
| `Search-UnifiedAuditLog` | StartDate·EndDate 로 지정[3] | 한 번 호출 기본 100건·최대 5,000건, `ReturnLargeSet` 페이징으로 최대 50,000건[3] | 보관 기간 안이면 가능, 시간 창을 쪼개 반복 |
| Graph 감사 검색 API (`auditLogQuery`) | `filterStartDateTime`·`filterEndDateTime` 으로 지정[5] | — | 검색 작업 단위로 가능 |
| Office 365 관리 활동 API | `startTime`·`endTime` 간격 24시간 이하, `startTime` 은 7일 이내[7] | 처음 분당 2,000요청, 좌석 수·라이선스에 따라 늘고 E5·A5·G5 는 약 두 배[8] | `startTime` 이 7일 이내라 그보다 오래된 콘텐츠는 못 받음, 구독이 꺼져 있으면 목록·콘텐츠 조회 불가[7] |

포털 검색 조건에는 날짜·시간(UTC), 키워드 (Keyword Search), 관리 단위 (Admin Units), 활동의 표시 이름과 작업 이름, 레코드 종류, 사용자, 파일·폴더·사이트(URL 끝 `*` 와일드카드), 워크로드가 있습니다[1]. 작업 이름은 이름 그대로 정확히 적고 여럿이면 쉼표로 잇는데, 틀리게 적으면 결과가 나오지 않습니다[1]. Graph 쿼리의 거름 조건은 `recordTypeFilters`, `keywordFilter`, `serviceFilters`, `operationFilters`, `userPrincipalNameFilters`, `ipAddressFilters`, `objectIdFilters`, `administrativeUnitIdFilters` 이고, 쿼리 상태 `status` 는 `notStarted`·`running`·`succeeded`·`failed`·`cancelled`·`unknownFutureValue` 중 하나입니다[5].

관리 활동 API 의 콘텐츠 종류 (content type) 는 `Audit.AzureActiveDirectory`, `Audit.Exchange`, `Audit.SharePoint`, 나머지 워크로드 전부인 `Audit.General`, 그리고 `DLP.All` 입니다[7]. 구독을 만든 뒤 첫 블롭이 나오기까지 최대 12시간 걸리고, 7일이 지난 콘텐츠는 받을 수 없습니다[7]. 그래서 사고가 난 뒤 몇 달 전 기록을 모으는 데는 맞지 않고, 평소 SIEM 으로 계속 옮겨 두는 용도에 맞습니다.

### 검색 작업과 권한

포털에서 검색을 누르면 검색 작업 (Search job) 이 생기고, 상태는 Queued, In Progress, Completed 순으로 바뀝니다[1]. 계정 하나가 동시에 돌릴 수 있는 작업은 10개이고 그중 조건 없는 작업은 1개뿐이며, 사용자가 많은 테넌트에서 넓게 잡은 작업은 끝나는 데 최대 48시간 걸릴 수 있습니다[1]. 완료된 검색 작업은 30일 동안 남습니다[1]. 검색 작업을 지우면 작업 정의와 결과만 사라지고 감사 기록 자체는 남습니다[1].

감사 로그를 검색하려면 Audit Logs 또는 View-Only Audit Logs 역할이 필요합니다[1]. 관리 단위가 지정된 관리자(제한된 관리자)는 자기 관리 단위 안 사용자가 만든 기록만 검색·내보내기할 수 있고, 사용자가 아닌 주체나 시스템 계정이 만든 기록은 관리 단위 제한이 없는 관리자만 봅니다[1]. 제한된 관리자에게는 Exchange 의 `Set-Mailbox`·`Set-MailboxPlan`·`SupervisionBulkEmailExclusion`, 엔드포인트 DLP 의 `FileCreated`·`FileDeleted` 같은 작업도 검색되지 않습니다[1].

## 구조 — 내보낸 파일의 모양

포털에서 내보낸 CSV 와 `Search-UnifiedAuditLog` 결과를 `Export-Csv` 로 저장한 파일에는 `CreationDate`, `UserIds`, `Operations`(cmdlet 예시에서는 `RecordType`), `AuditData` 열이 있고, `AuditData` 열에 레코드 전체가 JSON 객체로 들어 있습니다[2]. 포털 화면의 결과 열은 Date (UTC), IP Address, User, Record type, Activity, Item, Admin Units, Details 입니다[1].

Graph 감사 검색 API 가 돌려주는 `auditLogRecord` 에는 `createdDateTime`, `operation`, `auditLogRecordType`, `clientIp`, `objectId`, `organizationId`, `administrativeUnits` 가 따로 있고 레코드별 세부 감사 데이터는 `auditData` 에 들어 있습니다[6]. 같은 기록이라도 경로마다 필드 이름 표기가 달라서, 여러 경로로 받은 결과를 합칠 때는 `AuditData` 안의 `Id`·`CreationTime` 으로 맞춰 봅니다([레코드 구조](record-structure.md) 참고).

## 증거로서 의미

**증명하는 것**: 내보낸 파일의 행은 검색 시점에 그 조건으로 조회된 감사 기록이 있었다는 것을 보여 줍니다. 레코드 안의 사용자·작업·시각이 말하는 범위는 [레코드 구조](record-structure.md)와 같습니다.

**증명하지 못하는 것**: 결과에 행이 없다고 해서 그 활동이 없었다는 뜻은 아닙니다. 건수 한도에서 잘렸거나, 제한된 관리자로 검색했거나, 기록이 아직 들어오지 않았거나, `-HighCompleteness` 없이 빠른 검색을 했을 수 있습니다[1][3]. 키워드 검색은 공통 스키마로 색인한 내용만 찾고 `AuditData` 본문은 찾지 않아서, 본문에만 있는 값으로는 걸리지 않습니다[1].

보고서에는 "2026-03-02 00:00 ~ 2026-03-09 00:00 (UTC) 범위를 관리 단위 제한 없는 계정으로 `ReturnLargeSet` 을 써서 조회했고, 한 창에서 5,000건 한도에 닿은 적이 없다" 처럼 검색 조건과 계정·방법을 함께 적습니다(만든 예시).

## 시각 해석

포털의 날짜·시간 조건과 Date (UTC) 열은 UTC 입니다[1]. `Search-UnifiedAuditLog` 는 기록을 UTC 로 저장하고, 시간대 없이 넣은 `-StartDate`·`-EndDate` 값도 UTC 로 받아들입니다[3]. 현지 시각으로 범위를 잡으려면 `"2018-05-06 14:30:00z"` 처럼 UTC 로 적거나 `(Get-Date "5/6/2018 9:30 AM").ToUniversalTime()` 으로 바꿔서 넣습니다[3]. 내보낸 CSV 의 `CreationDate` 열이 UTC 인지는 같은 행 `AuditData` 안의 `CreationTime` 과 견주어 검체에서 확인합니다.

Graph `createdDateTime` 은 활동을 수행한 시각입니다[6]. 관리 활동 API 의 `contentCreated` 는 블롭을 받을 수 있게 된 시각이지 이벤트 시각이 아니고, 블롭 안 이벤트는 순서가 보장되지 않아 앞 블롭보다 이른 이벤트가 뒤 블롭에 들어 있을 수 있습니다[7]. 핵심 서비스(Exchange·SharePoint·OneDrive·Teams) 기록은 보통 이벤트 뒤 60~90분 지나야 검색되고, 그보다 늦는 서비스도 있습니다[1]. 방금 일어난 일은 몇 시간 뒤 다시 검색합니다.

## 함정과 한계

- **한도에서 조용히 잘림**: 포털 내보내기가 한도(Standard 50,000행, Premium 1,000,000행)를 넘으면 CSV 에 일부만 들어갑니다[2]. 날짜 범위를 쪼개거나 사용자·작업으로 좁혀 여러 번 내보냅니다[2].
- **세션 명령 섞기**: 같은 `SessionId` 에서 `ReturnLargeSet` 과 `ReturnNextPreviewPage` 를 번갈아 쓰면 결과가 10,000건으로 줄어듭니다[3]. `ReturnLargeSet` 은 정렬되지 않은 결과를 주고, `ReturnNextPreviewPage` 는 날짜순이지만 5,000건까지만 줍니다[3].
- **완전성 스위치**: `-HighCompleteness`(미리 보기 기능)를 빼면 검색은 빠르지만 결과가 빠질 수 있고, 넣으면 더 완전한 대신 훨씬 오래 걸립니다[3]. 이 스위치는 모든 조직에서 쓸 수 있지는 않습니다[3].
- **RecordType 하나만**: `-RecordType` 에는 값을 하나만 넣을 수 있어서, 여러 종류가 필요하면 종류마다 다시 실행해 이어 붙입니다[2].
- **Excel 펼치기 누락**: Power Query 로 `AuditData` 를 열로 펼치면 앞 1,000행에 나온 속성만 열이 되고, 그 뒤 레코드에만 있는 속성은 빠집니다[2].
- **내보내기 실패**: 방화벽이 Azure Front Door 도메인(`azurefd.net`)을 막으면 내보내기가 되지 않습니다[2].
- **결과 수 차이**: 작업 상세 화면의 총 건수는 중복을 뺀 값이라 검색 작업 목록의 수보다 적을 수 있고, 검색 작업 목록의 총 결과 수는 100,000건을 넘으면 근삿값으로 표시됩니다[1].
- **180일 범위**: 보관 기간이 180일보다 길어도 포털 한 검색으로는 180일까지만 잡히므로 기간을 나눠 검색합니다[1].

## 직접 분석해 보기

`Search-UnifiedAuditLog` 로 받을 때는 긴 기간을 짧은 시간 창으로 쪼개고, 창마다 새 `SessionId` 에 `-SessionCommand ReturnLargeSet -ResultSize 5000` 을 주어 결과가 0건이 될 때까지 되풀이합니다[3][4]. 진행은 결과의 `ResultIndex`(이번 반복의 결과 위치)와 `ResultCount`(모든 반복을 합친 결과 수), `AuditSearchRequestMetadata.moreRecordsAvailable` 로 봅니다[3]. Microsoft 가 내놓은 예시 스크립트는 60분 창에 5,000건씩 받고, 마지막 행의 `ResultIndex` 가 `ResultCount` 와 같아지면 다음 창으로 넘어갑니다[4].

```powershell
# 만든 예시: 2026-03-02 00:00~01:00(UTC) 60분 창 하나를 받는다
$start = [datetime]"2026-03-02T00:00:00Z"
$end   = $start.AddHours(1)
$sid   = [guid]::NewGuid().ToString()
do {
  $r = Search-UnifiedAuditLog -StartDate $start -EndDate $end `
       -SessionId $sid -SessionCommand ReturnLargeSet -ResultSize 5000
  $r | Select-Object CreationDate,UserIds,RecordType,AuditData |
       Export-Csv .\ual.csv -Append -NoTypeInformation
} while ($r -and $r[-1].ResultIndex -lt $r[0].ResultCount)
```

한 창의 `ResultCount` 가 50,000 을 넘으면 그 창은 더 잘게 나눠야 합니다.

공개 도구도 같은 원리로 창을 나눕니다. Microsoft-Extractor-Suite 의 `Get-UAL` 은 창 하나에 목표 3,000건을 두고, 받은 건수가 5,000건 한도에 닿으면 창을 절반으로 줄여 다시 받으며, 가장 작은 창에서도 5,000건 이상이면 로그에 `[ERROR] ... has 5000+ events` 를 남깁니다[9]. 출력은 CSV·JSON·JSONL·SOF-ELK 형식이고 병합하면 `UAL-Combined.csv` 같은 파일이 됩니다[9]. 도구로 받은 결과를 쓸 때는 이 오류·경고 줄이 있는지 먼저 확인합니다. DFIR-O365RC 는 `ReturnLargeSet` 과 `-ResultSize 5000` 으로 받고 한 창이 50,000건을 넘는지 확인합니다[10]. 도구별 수집 설정은 [Microsoft 365 수집 도구](../../../03-techniques/acquisition/m365-collection.md)에서 다룹니다.

Graph 감사 검색 API 는 Microsoft-Extractor-Suite 가 기본으로 `https://graph.microsoft.com/beta/security/auditLog/queries` 를 쓰고 `-UseV1` 을 주면 v1.0 을 씁니다[9]. 이 경로로 받으려면 `AuditLogsQuery.Read.All` 권한이 필요합니다[10]. DFIR-O365RC 는 이 경로가 아직 베타이고 백엔드 버그 때문에 지금은 쓸 수 없다고 봅니다[10]. 두 도구의 판단이 달라서, Graph 로 받은 결과는 같은 기간을 `Search-UnifiedAuditLog` 로 받은 건수와 견주어 봅니다.

## 교차 검증

- 같은 기간·조건을 두 경로(예: 포털 내보내기와 `Search-UnifiedAuditLog`)로 받아 건수와 `AuditData` 안 `Id` 목록을 비교하면 잘린 부분이 드러납니다.
- 결과가 비었을 때는 [통합 감사 로그 허브](index.md)에서 로그 켜짐 여부·보관 기간·`Set-AdminAuditLogConfig` 기록을 함께 봅니다.
- 로그인·디렉터리 변경은 통합 감사 로그와 따로 보관되는 [Entra ID 로그](../entra-logs/index.md)에서도 확인합니다.
- 여러 경로 결과를 한 시간 축에 놓는 방법은 [클라우드 타임라인](../../../03-techniques/analysis/timeline.md)을 봅니다.

## 참고 문헌

1. Microsoft, "Search the audit log", Microsoft Learn (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-search
2. Microsoft, "Export, configure, and view audit log records", Microsoft Learn (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-export-records
3. Microsoft, "Search-UnifiedAuditLog", office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Search-UnifiedAuditLog.md
4. Microsoft, "Use a PowerShell script to search the audit log", Microsoft Learn (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-search-script
5. Microsoft, "auditLogQuery resource type", Microsoft Graph (2026-08-14 갱신). https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogquery
6. Microsoft, "auditLogRecord resource type", Microsoft Graph (2026-08-14 갱신). https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogrecord
7. Microsoft, "Office 365 Management Activity API reference", Microsoft Learn (2024-12-03 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference
8. Microsoft, "Learn about auditing solutions in Microsoft Purview", Microsoft Learn (2026-05-18 갱신). https://learn.microsoft.com/en-us/purview/audit-solutions-overview
9. Invictus Incident Response, Microsoft-Extractor-Suite (`Scripts/Get-UAL.ps1`, `Scripts/Get-UALGraph.ps1`). https://github.com/invictus-ir/Microsoft-Extractor-Suite
10. ANSSI, DFIR-O365RC (`README.md`, `DFIR-O365RC/DFIR-O365RC.psm1`). https://github.com/ANSSI-FR/DFIR-O365RC
