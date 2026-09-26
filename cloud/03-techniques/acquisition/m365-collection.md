---
title: "Microsoft 365 수집 도구"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 640
---

# Microsoft 365 수집 도구 (Microsoft-Extractor-Suite 등)

Microsoft 365 의 감사 로그와 Entra ID 로그를 공개 도구로 받을 때, 도구가 어느 API 를 어떤 단위로 부르고 어디서 레코드를 빠뜨릴 수 있는지를 알고 쓰는 방법입니다.

## 언제 쓰나

테넌트가 로그를 SIEM 같은 장기 저장소로 보내지 않았다면, 사고가 난 뒤 서비스에 남아 있는 로그를 보존 기간이 끝나기 전에 떠야 합니다[16]. Purview 포털에서 검색해 CSV 로 내보낼 수도 있지만, 한 번 검색할 수 있는 날짜 범위가 최대 180일이고 내보내기 건수에도 상한이 있어서[3] 수만 건이 넘는 테넌트에서는 창을 나눠 반복해서 받는 도구를 씁니다. 보존 조치를 먼저 거는 순서는 [로그부터 지키기](log-preservation.md), 조사 전체의 흐름은 [조사 절차](investigation-process.md), AWS·Azure 구독 쪽 수집은 [AWS·Azure·GCP 수집](iaas-collection.md)에서 다룹니다.

이 페이지의 도구는 모두 서비스 API 가 돌려주는 레코드를 받아 파일로 쓰는 도구입니다. 서비스에 남아 있지 않은 기록을 되살리지는 못하므로, 어느 로그가 며칠 남는지는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에서 먼저 확인합니다.

## 통합 감사 로그를 받는 세 경로

도구마다 이름은 달라도 통합 감사 로그 (Unified Audit Log) 를 받는 경로는 아래 셋 가운데 하나입니다. 레코드 구조는 [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md)에서 다룹니다.

| 경로 | 받는 방식 | 한 번에 받는 양 | 순서 |
|---|---|---|---|
| Exchange Online PowerShell `Search-UnifiedAuditLog` | 명령을 부를 때마다 결과를 돌려받음. `-SessionId` 로 같은 검색을 이어서 받음 | 기본 100건, `-ResultSize` 최대 5,000. `-SessionCommand ReturnLargeSet` 으로 이어 받으면 최대 50,000건[1] | `ReturnLargeSet` 은 정렬하지 않음. `ReturnNextPreviewPage` 는 날짜순이지만 최대 5,000건[1] |
| Purview 포털 검색·내보내기 | 검색 작업을 만들고 결과를 CSV 로 내보냄 | 검색 범위 최대 180일. 내보내기 Audit (Standard) 50,000행, Audit (Premium) 1,000,000행[3] | — |
| Microsoft Graph 감사 로그 쿼리 (`security/auditLog/queries`) | 검색 작업을 비동기로 만들고, 상태가 `succeeded` 가 되면 `records` 로 결과를 받음 | 필터 필드 `filterStartDateTime`·`filterEndDateTime`·`recordTypeFilters`·`operationFilters`·`userPrincipalNameFilters`[4] | — |

`Search-UnifiedAuditLog` 는 진행 상황을 레코드마다 붙여 돌려주는데, `ResultIndex` 는 이번 반복의 결과, `ResultCount` 는 모든 반복의 결과이고, `AuditSearchRequestMetadata.moreRecordsAvailable` 은 더 받을 결과가 있는지를 알려 줍니다[1]. DFIR-O365RC 코드는 `ResultIndex` 를 앞 반복까지 받은 건수에 이번 건수를 더한 누적 순번으로 보고 맞춰 봅니다[22]. 같은 `SessionId` 에서 `ReturnLargeSet` 과 `ReturnNextPreviewPage` 를 섞어 쓰면 결과가 10,000건으로 줄어듭니다[1]. 미리 보기 스위치 `-HighCompleteness` 를 주면 오래 걸리는 대신 결과를 더 빠짐없이 돌려주고, 주지 않으면 빠르지만 결과가 빠질 수 있습니다[1]. Microsoft 는 감사 로그를 프로그램으로 내려받을 때 이 명령 대신 Management Activity API 를 쓰도록 권장하고, 21Vianet 이 운영하는 Office 365 에서는 명령은 있지만 결과를 돌려주지 않습니다[1].

Graph 감사 로그 쿼리의 상태 값은 `notStarted`, `running`, `succeeded`, `failed`, `cancelled`, `unknownFutureValue` 입니다[4](2026년 8월 문서 기준). 검색 작업을 먼저 걸어 두고 결과는 검색 ID 로 나중에 받을 수 있으므로[9], 검색 ID 를 수집 기록에 남겨 둡니다.

## 절차

1. **감사 설정부터 받습니다.** 감사 수집이 꺼져 있거나 감사 우회가 걸린 사서함이 있으면 로그가 비어 있는 이유가 됩니다. 확인할 값과 명령은 [클라우드 포렌식 보고서](../reporting/forensic-report.md)의 감사 설정 단계에 모아 두었습니다. Untitled Goose Tool 은 이 단계에서 `Get-MailboxAuditBypassAssociation`, `Get-AdminAuditLogConfig`, `Get-OrganizationConfig`, `Get-PerimeterConfig`, `Get-TransportRule`, `Get-TransportConfig` 결과를 각각 JSON 파일로 남깁니다[17].

2. **수집 계정과 권한을 정합니다.** 도구마다 인증 방식이 다르고, 수집 계정·앱의 활동도 대상 테넌트 로그에 남습니다. 그 기록을 조사 기록과 구분하는 방법은 [조사 절차](investigation-process.md)에서 다룹니다.

   | 도구 | 인증 | 필요한 권한(도구 문서에 적힌 것) |
   |---|---|---|
   | Microsoft-Extractor-Suite | 조사자가 `Connect-M365`(내부에서 `Connect-ExchangeOnline` 에 매개변수를 그대로 넘김)·`Connect-MgGraph`·`Connect-AzAccount` 로 먼저 로그인[7][15] | 함수마다 다름. Graph 경로의 감사 로그 쿼리는 `AuditLogsQuery.Read.All`[9] |
   | Untitled Goose Tool | 클라우드 전용(온프레미스와 동기화하지 않은) 사용자 계정과 그에 딸린 Exchange Online 서비스 주체. 서비스 주체에 "Allow public client flows" 를 켬[16] | Exchange 역할 `View-Only Audit Logs`·`View-Only Configuration`·`View-Only Recipients`·`User Options`, Graph 애플리케이션 권한 `AuditLog.Read.All`·`Directory.Read.All` 등, Azure 구독 역할 `Reader`·`Storage Blob Data Reader`·`Storage Queue Data Reader`[16] |
   | DFIR-O365RC | 2.0.0(2024년 8월)부터 인증서를 쓰는 Entra 앱으로 앱 전용 접근[21] | `Exchange.ManageAsApp`, `AuditLog.Read.All`, `AuditLogsQuery.Read.All`, Exchange 역할 `View-only audit logs` 등. Graph 로 Entra 로그를 받으려면 테넌트에 Entra ID P1 사용자가 한 명 이상 있어야 함[21] |

   Untitled Goose Tool 의 권한 목록은 읽기 전용 접근 (read-only access) 으로 소개되지만, WindowsDefenderATP 권한 가운데 `Ti.ReadWrite (Application)` 과 `Library.Manage (Application)` 은 이름에 쓰기·관리가 들어 있습니다[16]. 권한 목록은 도구 문서의 설명보다 실제로 부여한 권한 이름으로 기록합니다.

3. **통합 감사 로그를 받습니다.** 도구가 창을 나누는 방식에 따라 받지 못한 구간이 생기는 모양이 다르므로 아래 "도구별 동작" 을 보고 실행 로그를 함께 남깁니다.

4. **Entra 로그인·감사 로그와 Azure 활동 로그를 받습니다.** Microsoft-Extractor-Suite·Untitled Goose Tool·DFIR-O365RC 는 Entra 로그인·감사 로그를 통합 감사 로그와 따로 Microsoft Graph 로 받습니다[13][18][21]. 로그 구조는 [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md)에서 다룹니다. 조사 범위에 Azure 구독이 들어가면 Microsoft-Extractor-Suite 와 Untitled Goose Tool 로 활동 로그도 받을 수 있고, 두 도구 모두 기본 시작일이 89일 전입니다[14][19]. 활동 로그 읽는 법은 [활동 로그](../../02-artifacts/azure/activity-log.md)에서 다룹니다.

5. **Exchange 쪽 부가 자료를 받습니다.** 받은 편지함 규칙, 사서함 위임 권한, 메시지 추적이 여기에 들어갑니다. 메시지 추적 `Get-MessageTraceV2` 는 최근 90일을 검색할 수 있고, 매개변수 없이 부르면 최근 48시간만, 쿼리 한 번에 10일치만 돌려주며, 결과는 기본 1,000건·최대 5,000건이고 출력 시각은 UTC 입니다[5]. 읽는 법은 [Exchange Online](../../02-artifacts/m365/exchange-online/index.md)에서 다룹니다.

6. **실행 로그와 해시를 남깁니다.** 받은 파일의 해시를 곧바로 계산하고, 도구 실행 로그에서 누락 경고 줄을 찾아 받지 못한 구간을 적습니다. 해시 목록을 만드는 방법과 보고서에 남길 항목은 [클라우드 포렌식 보고서](../reporting/forensic-report.md)에서 다룹니다.

## 도구

### 도구별 동작

| 항목 | Microsoft-Extractor-Suite | Untitled Goose Tool | DFIR-O365RC | Hawk |
|---|---|---|---|---|
| 만든 곳·언어 | Invictus IR, PowerShell[7] | CISA, Python[16] | ANSSI, PowerShell(Docker 이미지 제공)[21] | PowerShell[24] |
| 통합 감사 로그 경로 | `Search-UnifiedAuditLog`(`Get-UAL`) 또는 Graph 감사 로그 쿼리(`Get-UALGraph`)[8][9] | Exchange Online 관리 API 로 `Search-UnifiedAuditLog` 를 `ReturnLargeSet` 으로 부름[17] | `Search-UnifiedAuditLog` 를 `ReturnLargeSet`·`-ResultSize 5000` 으로 부름. Purview(Graph) 경로는 선택[21][22] | — |
| 창 나누기 | 호출당 5,000건 상한 안에서 창 크기를 자동 조절[8] | 세션 결과 수가 `ual_threshold` 를 넘으면 창을 반으로 나눔[17] | 한 시간 단위[23] | — |
| 기본 기간 | `Get-UAL` 오늘부터 180일 전, `Get-UALGraph` 90일 전[8][9] | 어제 끝부터 364일 전[17][20] | 인자로 지정[21] | 최대 365일[25] |
| 저장 형태 | CSV(기본)·JSON·JSONL·SOF-ELK[8] | `AuditData` 만 한 줄에 하나씩 쓴 JSON Lines[17] | JSON[21] | CSV·JSON[24] |

**Microsoft-Extractor-Suite.** `Get-UAL` 은 먼저 최근 60분을 한 번 떠 보고 그 건수로 처음 창 크기를 정한 뒤, 창 하나에 3,000건(`-TargetEventsPerWindow`, 기본값)을 목표로 창을 늘리고 줄입니다[8]. 결과가 5,000건에 닿으면 창을 반으로 줄여 다시 받고, 창의 최소 크기는 0.1분입니다[8]. 최소 창에서도 5,000건에 닿거나 서버 오류로 재시도를 다 쓰면 실행 로그에 `[ERROR]` 줄을 남기고 넘어가며, 그 줄의 모양은 [클라우드 포렌식 보고서](../reporting/forensic-report.md)에 있습니다. 출력 파일 이름은 `UAL-` 뒤에 창의 시작·끝을 `yyyyMMddHHmmss` 로 붙인 형태라서 시간대 표시가 없습니다[8]. 실행 로그의 창 시각은 대부분 UTC 로 바꿔 `K` 서식(시간대 표시)을 붙여 적지만, 재시도를 다 써서 창을 건너뛰는 줄은 바꾸지 않은 시각을 `yyyy-MM-dd HH:mm:ss` 로 적습니다[8]. `Get-MailboxAuditLog` 와 `Get-AdminAuditLog` 는 별도 명령을 부르지 않고 `Get-UAL` 에 `RecordType` 을 각각 `ExchangeItem`·`ExchangeAdmin` 으로 넘깁니다[11]. `Get-UALGraph` 는 기본으로 beta 엔드포인트 `https://graph.microsoft.com/beta/security/auditLog/queries` 를 쓰고 `-UseV1` 을 주면 v1.0 을 쓰며, `-SkipDownload` 로 검색만 걸어 검색 ID 를 `scanId.txt` 에 남기고 `-SearchId` 로 나중에 받을 수 있습니다[9]. Entra 로그인 로그는 `https://graph.microsoft.com/beta/auditLogs/signIns`, 감사 로그는 `https://graph.microsoft.com/v1.0/auditLogs/directoryAudits` 에서 받습니다[13]. `Get-AllEvidence` 는 시작하기 전에 `Get-OrganizationConfig`, `Search-UnifiedAuditLog -ResultSize 1`, `Get-MgContext` 로 각 연결과 권한을 확인한 뒤 여러 수집 작업을 차례로 돌립니다[10].

**Untitled Goose Tool.** 설정 파일 `.conf` 의 `[filters]` 에 `date_start`·`date_end`(YYYY-MM-DD)를 적고, `[variables]` 의 `ual_threshold`(100~50,000, 기본 5,000)와 `max_ual_tasks`(기본 5)로 세션당 결과 수와 동시 작업 수를 정하며, `[azure]`·`[entraid]`·`[m365]`·`[mde]` 절의 항목을 켜서 받을 것을 고릅니다[16]. 통합 감사 로그는 세션에서 받은 결과 수가 `ResultCount` 와 같을 때만 `ual_시작_끝.json`(콜론은 `_` 로 바꿈) 파일로 쓰고, 어디까지 받았는지를 `.ual_state`·`.ual_bounds` 에 남겨 멈춘 뒤 이어서 받습니다[17]. Entra 로그인 로그는 `/beta/auditLogs/signIns` 를 `source` 값 `adfs`(대화형)·`rt`(비대화형)·`sp`(서비스 주체)·`msi`(관리 ID)로 나눠 하루씩 받고 `{source}_signin_log_{날짜}.json` 에 씁니다[18]. 받은 편지함 규칙은 `Get-InboxRule -IncludeHidden` 결과와 Graph 결과를 둘 다 남기는데, 두 결과가 서로 다른 정보를 보여 주기 때문입니다[16][17].

**DFIR-O365RC.** 한 시간 창마다 `ReturnLargeSet` 으로 최대 50,000건을 받고, 창의 `ResultCount` 가 50,000을 넘으면 실행 로그에 `More than 50000 ... events between ... - some events will be missing` 경고를 남깁니다[22][23]. `ResultCount` 가 0 이거나 `ResultIndex` 가 -1 이면 서버 시간 초과 때문일 수 있다는 오류를 내고 멈춥니다[22]. `Search-O365` 로 사용자를 지정하면 사서함 감사 로그도 `Search-MailboxAuditLog` 로 함께 찾는데, 라이선스와 설정에 따라 일부 사서함 기록이 통합 감사 로그에 없을 수 있기 때문입니다[21]. 이 명령은 클라우드에서 폐기될 예정입니다[6]. 결과는 모두 JSON 이고, 통합 감사 로그는 `O365_unified_audit_logs/YYYY-MM-DD/UnifiedAuditLog_테넌트_YYYY-MM-DD_HH-00-00.json`, Entra 로그인은 `azure_ad_signin/YYYY-MM-DD/AADSigninLog_테넌트_YYYY-MM-DD_HH-00-00.json` 에 씁니다[21]. `Get-O365Light` 는 관심 작업만 골라 받으며, `-operationsSet` 값으로 `all`, `allButAzureAD`, `ExchangeOnly`, `OneDrive_Sharepoint_Teams_YammerOnly`, `AzureADOnly`, `SecurityAlertsOnly`, `Devices` 를 받습니다[23].

**Hawk.** `Start-HawkTenantInvestigation` 으로 테넌트 전체를, `Start-HawkUserInvestigation` 으로 사용자 단위를 조사하고, 이름이 `_Investigate_` 로 시작하는 파일에 더 볼 만한 항목을 모읍니다[24]. 날짜 범위는 365일을 넘을 수 없고 `-DaysToLookBack` 은 1~365 입니다[25].

### 출처끼리 다른 점

- **메시지 추적 기간.** Microsoft-Extractor-Suite 의 `Get-MessageTraceLog` 설명에는 "Only 10 days of history is available" 라고 적혀 있지만 기본 시작일은 90일 전이고 10일씩 끊어 받습니다[12]. `Get-MessageTraceV2` 문서는 검색 가능 기간을 90일, 쿼리 한 번의 범위를 10일로 적었습니다[5]. 문서 값을 기준으로 삼으면 됩니다.
- **Graph 감사 로그 쿼리의 안정성.** Microsoft-Extractor-Suite 는 v1.0 과 beta 모두 안정성 문제가 있었고 beta 가 더 안정적이라는 이유로 beta 를 기본으로 씁니다[9]. DFIR-O365RC 문서는 같은 Purview 경로를 백엔드 버그 때문에 "unusable for now" 로 적었습니다[21]. 이 경로로 받았다면 같은 기간을 `Search-UnifiedAuditLog` 로도 받아 건수를 맞춰 봅니다.
- **Untitled Goose Tool 의 기본 기간.** 설정 파일 설명은 `date_start` 를 비우면 보존 기간의 가장 이른 날부터 받는다고 적었지만[16], 통합 감사 로그를 받는 코드는 날짜가 없을 때 어제 끝 시각부터 364일 전까지를 범위로 씁니다[17][20]. 실제 범위는 실행 로그의 시작·끝 값으로 적습니다.
- **도구 문서의 보존 기간 표.** 도구 문서마다 경로별로 받을 수 있는 기간을 따로 적어 두어 공식 보존 기간과 기준이 다릅니다. 두 값을 비교한 내용은 [클라우드 포렌식 보고서](../reporting/forensic-report.md)의 함정 절에 있습니다.

## 함정과 한계

- **상한에 걸린 창은 일부만 남습니다.** Microsoft-Extractor-Suite 는 최소 창에서도 5,000건(호출 상한)에 닿으면, DFIR-O365RC 는 한 시간 창이 50,000건(세션 상한)을 넘으면 받은 만큼만 쓰고 넘어갑니다[8][22]. 도구 출력만 보면 빈틈이 드러나지 않으므로 실행 로그를 결과와 함께 보관합니다.
- **파일 안의 순서는 시간순이 아닙니다.** `ReturnLargeSet` 결과는 정렬되지 않으므로[1] 파일 안 레코드 순서를 발생 순서로 읽지 않고, 타임라인은 레코드의 시각 필드로 다시 정렬합니다. 정렬 방법은 [클라우드 타임라인](../analysis/timeline.md)에서 다룹니다.
- **`AuditData` 만 남기면 감싸는 속성이 빠집니다.** Untitled Goose Tool 은 항상, Microsoft-Extractor-Suite 는 `-AuditDataOnly` 를 주면 `CreationDate`·`UserIds`·`Operations` 같은 바깥 속성을 버리고 `AuditData` JSON 만 씁니다[8][17]. Purview 에서 내보낸 CSV 는 `CreationDate`, `UserIds`, `Operations`, `AuditData` 네 열로 되어 있어서[2] 두 결과를 비교할 때는 열 구성이 다르다는 점을 먼저 맞춥니다.
- **같은 레코드가 두 번 들어올 수 있습니다.** Untitled Goose Tool 코드에는 통합 감사 로그 API 가 가끔 중복 결과를 돌려준다는 주석과 `AuditData` 의 `Id` 로 중복을 세는 코드가 있지만, 저장 전에 중복을 지우는 부분은 주석으로 막혀 있습니다[17]. 여러 도구의 결과를 합칠 때도 `Id` 로 중복을 확인합니다.
- **파일 이름의 날짜는 현지 날짜일 수 있습니다.** Untitled Goose Tool 은 실행 PC 의 현지 날짜(`datetime.now()`)로 하루 경계를 만들고 뒤에 `Z` 를 붙여 UTC 처럼 보냅니다[18]. 실행 PC 의 시간대가 UTC 가 아니면 하루 창과 파일 이름의 날짜가 UTC 날짜와 어긋날 가능성이 있습니다. Entra 로그의 기본 범위 끝이 실행한 날 00:00 이라서, 실행 당일 로그는 기본 범위에 들어가지 않습니다[18]. Microsoft-Extractor-Suite 의 통합 감사 로그 파일 이름에도 시간대 표시가 없습니다[8]. 레코드의 시각 필드 기준은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에서 다룹니다.
- **`-StartDate`·`-EndDate` 에 시각을 빼면 자정이 됩니다.** 날짜만 주면 12:00 AM 이 쓰이고, 시작과 끝에 같은 날짜만 넣으면 결과가 없습니다[1]. 시간대 없는 값은 UTC 로 해석합니다[1].
- **사서함 감사 기록이 검색에 안 나올 수 있습니다.** 사서함 감사가 기본으로 켜져 있어도 일부 사용자의 사서함 감사 이벤트가 Purview 검색이나 Management Activity API 에 나오지 않을 수 있습니다[3].
- **Excel 로 펼치면 뒤쪽 속성이 빠질 수 있습니다.** Power Query 로 `AuditData` 를 열로 펼치면 앞 1,000행에 있는 속성만 열이 됩니다[2]. 분석은 JSON 그대로 하거나, 작업 이름으로 먼저 걸러 행을 줄인 뒤 펼칩니다.
- **결과 폴더에 인증 자료가 섞입니다.** Untitled Goose Tool 은 토큰·쿠키를 `.ugt_auth`, 자격 증명을 `.auth` 에 두고 기본으로는 입력한 비밀번호로 암호화하며, `--insecure` 를 주면 암호화하지 않습니다[16]. DFIR-O365RC 는 PFX 인증서 파일을 씁니다[21]. 결과를 넘길 때 이런 파일은 빼서 따로 다룹니다.
- **원격 수집이 있는 도구가 있습니다.** Hawk 는 실행한 함수 이름과 사용 지역을 원격 수집한다고 밝히고 있어서[24], 격리한 조사 환경의 정책과 맞는지 확인합니다.
- **대량 작업을 켜면 양이 크게 늘어납니다.** DFIR-O365RC 의 `-mailboxLogin` 은 `MailboxLogin`, `-userLogin` 은 `UserLoggedIn`·`UserLoginFailed` 를 추가하는데, 도구가 양이 많을 수 있다고 경고합니다[23]. 창이 상한에 걸리기 쉬워지므로 이 작업은 기간을 좁혀 따로 받습니다.

## 결과를 어떻게 해석하나

도구 출력은 서비스 API 가 돌려준 레코드의 사본입니다. 도구가 붙인 표시(Hawk 의 `_Investigate_` 파일 같은 것)는 도구의 해석이고, 보고서의 근거는 그 밑의 레코드입니다[24]. 통합 감사 로그에서 어떤 작업이 없다는 결과는 "그 작업이 없었다" 가 아니라 "받은 범위와 그 시점의 감사 설정에서 해당 레코드가 없었다" 까지만 뜻합니다. 그래서 결과를 쓸 때는 받은 기간, 사용한 경로(`Search-UnifiedAuditLog`·Graph·포털), 누락 경고가 난 창, 수집 시점의 감사 설정을 함께 적습니다.

두 도구나 두 경로로 같은 기간을 받았다면 `AuditData` 의 `Id` 로 합친 뒤 건수를 비교합니다. 한쪽에만 있는 레코드가 있으면 상한에 걸린 창, 시간대 경계, 반영 지연 가운데 무엇 때문인지 실행 로그로 먼저 확인합니다. 받은 레코드로 의심스러운 작업을 걸러 내는 방법은 [탐지 규칙으로 로그 검색하기](../analysis/detection-rules.md), 보고서 문장은 [클라우드 포렌식 보고서](../reporting/forensic-report.md)에서 다룹니다. 다른 판의 공통 절차는 [Windows 포렌식 조사 절차](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/process-acquisition/investigation-process.html)를 봅니다.

## 참고 문헌

1. Microsoft, `Search-UnifiedAuditLog`, Exchange PowerShell 문서. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Search-UnifiedAuditLog.md
2. Microsoft, Export, configure, and view audit log records (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-export-records
3. Microsoft, Search the audit log (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-search
4. Microsoft, auditLogQuery resource type, Microsoft Graph (2026-08-14 갱신). https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogquery
5. Microsoft, `Get-MessageTraceV2`, Exchange PowerShell 문서. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Get-MessageTraceV2.md
6. Microsoft, `Search-MailboxAuditLog`, Exchange PowerShell 문서. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Search-MailboxAuditLog.md
7. Invictus IR, Microsoft-Extractor-Suite, README. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/README.md
8. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-UAL.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-UAL.ps1
9. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-UALGraph.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-UALGraph.ps1
10. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-AllEvidence.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AllEvidence.ps1
11. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-MailboxAuditLog.ps1`, `Scripts/Get-AdminAuditLog.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-MailboxAuditLog.ps1 , https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AdminAuditLog.ps1
12. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-MessageTraceLog.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-MessageTraceLog.ps1
13. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-AzureEntraGraphLogs.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureEntraGraphLogs.ps1
14. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-AzureActivityLogs.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureActivityLogs.ps1
15. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Connect.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Connect.ps1
16. CISA, Untitled Goose Tool, README. https://github.com/cisagov/untitledgoosetool/blob/develop/README.md
17. CISA, Untitled Goose Tool, `goosey/m365_datadumper.py`. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/m365_datadumper.py
18. CISA, Untitled Goose Tool, `goosey/entra_id_datadumper.py`. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/entra_id_datadumper.py
19. CISA, Untitled Goose Tool, `goosey/azure_dumper.py`. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/azure_dumper.py
20. CISA, Untitled Goose Tool, `goosey/utils.py`. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/utils.py
21. ANSSI, DFIR-O365RC, README. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/README.md
22. ANSSI, DFIR-O365RC, `DFIR-O365RC/DFIR-O365RC.psm1`. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/DFIR-O365RC.psm1
23. ANSSI, DFIR-O365RC, `DFIR-O365RC/Get-O365.ps1`. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/Get-O365.ps1
24. T0pCyber, Hawk, README. https://github.com/T0pCyber/hawk/blob/master/README.md
25. T0pCyber, Hawk, `Hawk/functions/Tenant/Start-HawkTenantInvestigation.ps1`. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Start-HawkTenantInvestigation.ps1
