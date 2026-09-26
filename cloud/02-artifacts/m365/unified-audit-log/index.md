---
title: "통합 감사 로그"
parent: "아티팩트 · Microsoft 365"
nav_order: 130
has_children: true
has_toc: false
---

# 통합 감사 로그 (Unified Audit Log)

Microsoft 365 테넌트에서 사용자와 관리자가 한 작업을 서비스 구분 없이 한곳에 모아 두는 로그이고, Microsoft 365 조사는 대부분 여기서 시작합니다.

## 왜 중요한가

통합 감사 로그는 수십 개 Microsoft 서비스에서 일어난 사용자·관리자 작업 수천 종을 테넌트 하나의 로그로 기록합니다[1]. Exchange Online 메일함 접근, SharePoint·OneDrive 파일 작업, Teams 활동, Entra ID 로그인과 디렉터리 변경이 같은 레코드 틀로 들어오므로, 한 계정이 여러 서비스에서 한 일을 한 줄의 시간 순서로 늘어놓을 수 있습니다.

다만 이 로그는 테넌트 설정과 사용자 라이선스에 따라 켜져 있는지, 얼마나 오래 남는지가 달라집니다. 엔터프라이즈(Microsoft 365·Office 365 Enterprise) 조직은 기본으로 켜져 있지만[3], Microsoft 365 Business Basic·Business Standard·Business Premium 같은 중소기업용 라이선스와 엔터프라이즈 무료 체험으로 만든 관리되지 않는 테넌트는 기본으로 꺼져 있어 관리자가 직접 켜야 합니다[4]. 감사 데이터는 감사가 켜져 있어야 감사 로그에 보이고[6], 최근 180일 안에 감사를 켰다면 검색 날짜 범위도 켠 날보다 앞으로 잡을 수 없습니다[3]. 그래서 기록을 읽기 전에 켜진 시점과 보관 기간부터 확인해야 "기록이 없다" 를 "활동이 없었다" 로 잘못 읽지 않습니다.

## 한눈에 보기

### 켜져 있는지 확인하기

| 확인할 것 | 방법 | 읽는 법 |
|---|---|---|
| 지금 켜져 있나 | Exchange Online PowerShell 에서 `Get-AdminAuditLogConfig \| Format-List UnifiedAuditLogIngestionEnabled` | `True` 면 켜짐, `False` 면 꺼짐[4] |
| 같은 명령을 다른 곳에서 친 경우 | Security & Compliance PowerShell 의 `Get-AdminAuditLogConfig` | 켜져 있어도 `UnifiedAuditLogIngestionEnabled` 가 늘 `False` 로 나오므로 판단에 쓰지 않습니다[4] |
| 언제 켜고 껐나 | `Search-UnifiedAuditLog -Operations Set-AdminAuditLogConfig` | AuditData 안 `UnifiedAuditLogIngestionEnabled` 값으로 켬·끔을 가르고, 바꾼 시각·관리자·IP 주소가 레코드에 남습니다[4] |
| 보존 정책 | Security & Compliance PowerShell 의 `Get-UnifiedAuditLogRetentionPolicy \| Sort-Object -Property Priority -Descending \| FL Priority,Name,Description,RecordTypes,Operations,UserIds,RetentionDuration` | 조직이 만든 정책만 나오고 기본 보존 정책은 나오지 않습니다[2] |

`Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true` 로 켜면 적용까지 최대 60분이 걸립니다[4]. 감사를 끄면 Purview 포털 검색과 `Search-UnifiedAuditLog` 가 결과를 돌려주지 않고, Office 365 Management Activity API 와 Microsoft Sentinel 로도 감사 데이터를 받을 수 없습니다[4].

### 보관 기간 (2026년 9월 문서 기준)

보관 기간은 작업을 한 사용자에게 붙은 라이선스로 정해집니다[2].

| 조건 | 보관 기간 |
|---|---|
| Audit (Standard) — E5 가 아닌 사용자, 게스트 | 180일[1][2] |
| Audit (Standard) 기록 중 2023년 10월 17일 이전에 생긴 것 | 90일 (기본값이 90일에서 180일로 바뀜)[1] |
| Audit (Premium) — Office 365·Microsoft 365 E5, Microsoft Purview Suite(옛 Microsoft 365 E5 Compliance), E5 eDiscovery and Audit 추가 라이선스 사용자의 Workload 가 AzureActiveDirectory·Exchange·OneDrive·SharePoint 인 기록 | 1년 (기본 보존 정책)[1][2] |
| Audit (Premium) 사용자의 그 밖 서비스 기록 | 180일, 보존 정책으로 늘릴 수 있음[1] |
| E5 와 10-Year Audit Log Retention 추가 라이선스, 10년 보존 정책 | 10년, 정책을 만들기 전 기록에는 적용되지 않음[1] |
| 서비스 주체·시스템·앱처럼 사용자가 아닌 주체가 만든 기록 | 1년 고정, 보존 정책이 적용되지 않음[1] |

조직이 만든 보존 정책은 기본 정책보다 앞서므로, 기본 1년보다 짧은 정책을 만들면 그 기록은 짧게 보관됩니다[2]. 보존 정책은 조직당 최대 50개이고, 기간은 7일·30일·6개월·9개월·1년·3년·5년·7년(추가 라이선스가 있으면 10년) 가운데 고르며, 우선순위는 1(가장 높음)부터 10000까지입니다[2]. 라이선스나 정책을 바꾸면 그 뒤로 들어오는 기록의 만료 시각만 바뀌고 이미 들어간 기록에는 소급하지 않습니다[1].

공개 도구 문서의 숫자는 이 표와 다르기도 합니다. DFIR-O365RC README 의 표에는 Exchange Online PowerShell 로 받는 통합 감사 로그가 90일, Purview 쪽이 180일, Management API 가 7일로 되어 있습니다[9]. 그러므로 실제 데이터에서는 가장 오래된 기록의 시각을 직접 확인합니다.

### 꺼내는 경로

| 경로 | 알려 주는 것 |
|---|---|
| Microsoft Purview 포털의 Audit 검색 | 날짜·사용자·작업으로 검색하고 CSV 로 내보냅니다[1][3] |
| Audit Search Graph API | Graph 에서 검색 작업을 만들고 결과 레코드를 받습니다[1] |
| Exchange Online PowerShell `Search-UnifiedAuditLog` | 포털 검색 밑에서 도는 cmdlet 이고 스크립트로 쓸 수 있습니다[1][3][8] |
| Office 365 Management Activity API | SIEM 으로 계속 받아 가는 용도이고, 조회 시작 시각은 7일 이내만 됩니다[5] |

세부 조건과 한도는 [검색과 내보내기](search-export.md) 에 있습니다.

### 기록이 들어오는 시간

Exchange·SharePoint·OneDrive·Teams 같은 핵심 서비스는 보통 이벤트 뒤 60~90분이 지나야 검색 결과에 나오고, 그 밖 서비스는 더 늦을 수 있으며, Microsoft 는 특정 시간을 보장하지 않습니다[3]. 사건 직후 검색에 안 나온 작업은 몇 시간 뒤 다시 검색합니다. 메일함 감사가 기본으로 켜져 있어도 일부 사용자의 메일함 감사 이벤트는 포털 검색이나 Management Activity API 에서 보이지 않을 수 있습니다[3]. 레코드 시각은 UTC 이며 자세한 해석은 [레코드 구조](record-structure.md) 에 있습니다.

### Entra ID 로그와의 관계

Entra ID 의 로그인·감사 로그와 통합 감사 로그는 서로 다른 로그입니다[7]. 통합 감사 로그의 보관은 Purview Audit 가 관리하고 Entra ID 라이선스를 바꿔도 영향을 받지 않습니다[7]. E5 계열 라이선스가 있는 조직은 Purview Audit (Premium) 로 Entra ID 감사 기록을 Entra ID 기본 보관 기간보다 오래 남길 수 있습니다[7]. Entra ID 쪽 보관 기간과 필드는 [Entra ID 로그](../entra-logs/index.md) 에서 다룹니다.

### 증명하는 것 / 증명하지 못하는 것

레코드 한 건은 "이 시각(UTC)에 이 사용자 ID 로 이 작업이 이 서비스에 기록되었다" 를 보여 줍니다. 감사가 꺼져 있던 기간, 보관 기간이 지난 기간, 기록이 아직 들어오지 않은 시간대에는 레코드가 없어도 활동이 없었다고 말할 수 없습니다. 누군가 감사를 끄거나 보존 기간을 줄였다면 그 사실 자체가 `Set-AdminAuditLogConfig` 작업이나 보존 정책 변경 기록으로 남을 수 있으므로 함께 찾아봅니다. 레코드 형식(RecordType) 목록에는 보존 정책을 뜻하는 `AuditRetentionPolicy`(296)와 감사 설정을 뜻하는 `AuditConfig`(297)가 있습니다[10].

## 읽는 순서

1. [레코드 구조 (AuditData)](record-structure.md) — 모든 레코드에 공통으로 들어가는 필드와 서비스별로 붙는 AuditData 필드, 시각 필드의 뜻을 다룹니다.
2. [검색과 내보내기 (Search·Export)](search-export.md) — 포털·`Search-UnifiedAuditLog`·Graph·Management Activity API 로 기록을 꺼낼 때의 한도와, 결과가 조용히 잘리는 경우를 다룹니다.
3. [주요 작업 이름 (Operations)](operations.md) — 메일함·파일·공유·Teams·로그인 작업 이름과, 같은 작업이 몇 분 동안 한 번만 기록되는 경우처럼 해석에 조심할 점을 다룹니다.

## 함께 볼 페이지

- [보관 기간과 라이선스 (Retention·Licensing)](../../../01-foundations/logging/retention-licensing.md) — 여러 클라우드 서비스의 보관 기간을 한곳에서 비교합니다.
- [클라우드 로그의 시각 (Timestamps·Time Zones)](../../../01-foundations/logging/timestamps.md)
- [JSON 로그 읽기 (JSON Log Records)](../../../01-foundations/logging/json-logs.md) — AuditData 는 JSON 입니다.
- [Entra ID 로그](../entra-logs/index.md), [Exchange Online](../exchange-online/index.md), [SharePoint·OneDrive](../sharepoint-onedrive.md), [Teams](../teams.md), [Purview eDiscovery와 보존](../purview-ediscovery.md), [Defender 경고와 기록](../defender-xdr.md)
- [로그부터 지키기 (Log Preservation)](../../../03-techniques/acquisition/log-preservation.md) — 보관 기간이 지나기 전에 먼저 받아 둡니다.
- [Microsoft 365 수집 도구 (Microsoft-Extractor-Suite 등)](../../../03-techniques/acquisition/m365-collection.md)
- [클라우드 타임라인 (Timeline)](../../../03-techniques/analysis/timeline.md)
- [메일 계정을 빼앗겨 송금 사기를 당했나 (BEC)](../../../04-scenarios/account-compromise/bec.md), [로그를 끄거나 지웠나 (Log Tampering)](../../../04-scenarios/infrastructure/log-tampering.md)

## 참고 문헌

1. Microsoft, "Learn about auditing solutions in Microsoft Purview" (2026-05-18 갱신). https://learn.microsoft.com/en-us/purview/audit-solutions-overview
2. Microsoft, "Manage audit log retention policies" (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
3. Microsoft, "Search the audit log" (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-search
4. Microsoft, "Turn auditing on or off" (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-enable-disable
5. Microsoft, "Office 365 Management Activity API reference" (2024-12-03 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference
6. Microsoft, "Search the audit log for events in Microsoft Teams" (2026-04-14 갱신). https://learn.microsoft.com/en-us/purview/audit-teams-audit-log-events
7. Microsoft, "Microsoft Entra data retention" (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
8. Microsoft, "Search-UnifiedAuditLog". https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Search-UnifiedAuditLog.md
9. ANSSI-FR, DFIR-O365RC README. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/README.md
10. Microsoft, "Office 365 Management Activity API schema" (2026-08-26 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
