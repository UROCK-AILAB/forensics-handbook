---
title: "책임 공유와 조사 범위"
parent: "기반 · 클라우드 조사의 구조"
nav_order: 0
---

# 책임 공유와 조사 범위 (Shared Responsibility)

클라우드에서는 서비스 회사가 물리 설비와 가상화 계층을, 고객이 데이터·계정·접근 정책을 맡기 때문에, 조사하는 쪽이 손에 넣을 수 있는 증거도 이 경계를 따라 나뉩니다[1][2][3].

## 이 형식을 쓰는 아티팩트

책임 공유 모델 (Shared Responsibility Model) 은 파일 형식이 아니라 "누가 어느 층을 설정하고 운영하나" 를 나눈 틀입니다. 조사에서는 이 틀로 두 가지를 정합니다. 하나는 고객이 직접 수집할 수 있는 층(가상 머신 디스크, 계정·권한 설정, 서비스가 내어 주는 감사 로그)이고, 다른 하나는 서비스 회사만 가진 층(물리 호스트, 하이퍼바이저, PaaS·SaaS 의 운영체제)입니다.

이 경계에 걸리는 기록은 다음과 같습니다.

| 기록 | 누가 한 일을 담나 | 다루는 쪽 |
|---|---|---|
| Microsoft 365 통합 감사 로그 | 고객 조직 사용자·앱, 그리고 Customer Lockbox 승인 뒤 Microsoft 엔지니어의 작업 | [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md) |
| Entra ID 로그인 로그 | 고객 테넌트 로그인, Microsoft 지원 담당자·CSP 의 교차 테넌트 로그인 | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md) |
| Google Cloud Access Transparency 로그 | Google 직원이 고객 데이터에 접근한 행동 | [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md) |
| Google Workspace Access transparency 보고서 | Google 지원팀이 사용자 데이터에 접근한 정보 | [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md) |
| Slack 감사 로그 | 고객 조직 사용자, 그리고 Slack 보안 담당자의 자격 증명 재설정 | [Slack 감사 로그](../../02-artifacts/saas/slack.md) |

## 구조

### 서비스 모델별 책임 나눔

Microsoft 는 책임을 영역별로 나눈 표 (responsibility matrix) 를 둡니다(2026년 9월 문서 기준, 문서 갱신 2026-08-24)[2].

| 영역 | 온프레미스 | IaaS | PaaS | SaaS |
|---|---|---|---|---|
| 고객 데이터 | 고객 | 고객 | 고객 | 고객 |
| 구성과 설정 | 고객 | 고객 | 고객 | 고객 |
| 신원과 사용자 | 고객 | 고객 | 고객 | 고객 |
| 클라이언트 장치 | 고객 | 고객 | 고객 | 공유 |
| 애플리케이션 | 고객 | 고객 | 공유 | 공유 |
| 네트워크 통제 | 고객 | 고객 | 공유 | Microsoft |
| 운영체제 | 고객 | 고객 | Microsoft | Microsoft |
| 물리 호스트 | 고객 | Microsoft | Microsoft | Microsoft |
| 물리 네트워크 | 고객 | Microsoft | Microsoft | Microsoft |
| 물리 데이터센터 | 고객 | Microsoft | Microsoft | Microsoft |

이 표에서 IaaS 의 예는 Azure Virtual Machines·Azure Disk Storage·가상 네트워크, PaaS 의 예는 Azure App Service·Azure Functions·Azure SQL Database·Azure Storage, SaaS 의 예는 Microsoft 365·Dynamics 365 입니다[2]. 배포 방식과 상관없이 고객에게 남는 책임은 데이터, 단말 (endpoint), 계정, 접근 관리(RBAC·다단계 인증·조건부 접근)이고, Microsoft 는 물리 보안·물리 네트워크·물리 호스트·하이퍼바이저를, PaaS 와 SaaS 에서는 운영체제·런타임·미들웨어까지 맡습니다[2]. 이 표의 "책임" 은 누가 설정·운영·감시하느냐는 거버넌스 뜻이고 법적 결론이 아닙니다[2].

### 세 회사의 표현 차이

| 회사 | 표현 | 서비스 모델 구분 | 고객에게 늘 남는 것 |
|---|---|---|---|
| AWS | 서비스 회사 몫은 클라우드의 보안 (Security of the Cloud), 고객 몫은 클라우드 안의 보안 (Security in the Cloud)[1] | 고른 서비스에 따라 고객 몫이 달라짐. EC2 는 게스트 운영체제·설치한 앱·보안 그룹 설정이 고객 몫, S3·DynamoDB 는 AWS 가 인프라·운영체제·플랫폼을 운영[1] | 데이터(암호화 선택 포함), 자산 분류, IAM 권한[1] |
| Microsoft | 책임 표와 늘 남는 책임 (Responsibilities you always retain)[2] | 온프레미스·IaaS·PaaS·SaaS 네 칸[2] | 데이터, 단말, 계정, 접근 관리[2] |
| Google Cloud | 책임 공유에 공동 운명 (shared fate) 을 더함[3] | IaaS·PaaS·SaaS 에 FaaS(서버리스)를 따로 두고, FaaS 의 책임 목록은 SaaS 와 비슷함(2023-08-21 검토 문서 기준)[3] | 접근 정책과 데이터[3] |

서버리스 함수의 자리는 출처마다 다릅니다. Google Cloud 는 Cloud Run functions 를 FaaS 로 두고 SaaS 와 비슷하게 보지만[3], Microsoft 는 Azure Functions 를 PaaS 의 예로 듭니다[2]. 결론은 같아서, 세 회사 모두 데이터와 접근 정책을 고객 몫으로 둡니다[1][2][3].

### 책임 경계와 조사 범위

| 층 | 고객이 관리하나 | 조사에서 얻는 방법 |
|---|---|---|
| 데이터·계정·권한·설정 | 모든 모델에서 고객[1][2][3] | 서비스가 내어 주는 감사 로그·로그인 로그·설정 조회. [기록은 어디에 남나](./where-records-live.md) |
| 게스트 운영체제·앱(IaaS) | 고객[1][2] | 가상 머신 디스크·메모리·운영체제 로그를 고객이 직접 수집. [클라우드 가상 머신 수집](../../03-techniques/acquisition/vm-acquisition.md) |
| 운영체제·런타임(PaaS·SaaS) | 서비스 회사[2] | 파일 시스템·프로세스 흔적은 고객 쪽 증거가 아니고, 서비스의 감사 로그·API 로 조사 |
| 물리 호스트·하이퍼바이저 | 서비스 회사[1][2] | 고객이 수집할 수 없음. 서비스 회사에 요청. [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) |
| 클라이언트 장치 | 고객(SaaS 에서는 공유)[2] | 단말 포렌식. [Windows 조사 절차](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/process-acquisition/investigation-process.html) |

서비스가 내어 주는 기록의 범위도 서비스 회사가 정합니다. Slack 감사 로그 API 는 가능한 감사 이벤트 가운데 일부만 지원하고[12], Google Cloud 에는 아직 감사 로그를 내지 않는 서비스가 있어서, 대상 서비스가 감사 로그를 내는지 서비스 목록에서 먼저 확인합니다[13]. Azure 리소스 로그는 기본으로 수집되지 않고 리소스마다 진단 설정을 만들어야 합니다[14].

## 읽는 법

책임 공유의 반대편, 곧 서비스 회사 직원과 서비스 자체가 한 일도 고객 쪽 로그에 남는 경우가 있습니다. 조사에서는 레코드마다 "고객 조직 사람이 한 일인가, 서비스 회사 쪽이 한 일인가" 를 먼저 가립니다.

### Microsoft 365 통합 감사 로그의 UserType

통합 감사 로그 공통 스키마의 `UserType` 은 작업을 한 사용자 종류를 정수로 적습니다[9].

| 값 | 이름 | 뜻 |
|---|---|---|
| 0 | Regular | 관리자 권한이 없는 일반 사용자 |
| 1 | Reserved | 예약값, 쓰지 않음 |
| 2 | Admin | 고객 조직의 관리자 |
| 3 | DCAdmin | Microsoft 데이터센터 관리자 또는 데이터센터 시스템 계정 |
| 4 | System | 서버 쪽 논리(Windows 서비스, 백그라운드 프로세스)가 만든 이벤트 |
| 5 | Application | Microsoft Entra 애플리케이션이 만든 이벤트 |
| 6 | ServicePrincipal | 서비스 주체 |
| 7 | CustomPolicy | 고객이 만들거나 관리하는 정책 |
| 8 | SystemPolicy | Microsoft 가 관리하는 정책 또는 시스템 정책 |
| 9 | PartnerTechnician | GDAP 에서 고객 테넌트를 대신해 일하는 파트너 테넌트 사용자 |
| 10 | Guest | 게스트 또는 익명 사용자 |

Entra 관련 이벤트에서는 관리자가 한 작업도 `UserType` 이 0 으로 남으므로, 누가 했는지는 `UserId` 로 확인합니다[9]. `UserId` 에는 `SHAREPOINT\system`, `NT AUTHORITY\SYSTEM` 같은 시스템 계정도 들어가고, SharePoint 에서는 조직 전체 작업 권한을 받은 앱을 뜻하는 `app@sharepoint` 가 들어갈 수 있습니다[9].

### Customer Lockbox 기록

Customer Lockbox 는 Microsoft 엔지니어가 고객 콘텐츠에 접근하기 전에 고객 승인을 받게 하는 기능이고, Exchange Online·SharePoint Online·OneDrive for Business·Teams·Windows 365 를 대상으로 합니다(문서 갱신 2025-02-03)[8]. 승인 흐름에서는 두 종류의 레코드가 통합 감사 로그에 남습니다[8].

| 레코드 | 날짜 | IP 주소 | 사용자 | 활동 | 항목 |
|---|---|---|---|---|---|
| 고객 승인자의 승인·거부 | 승인·거부한 시각 | 승인자가 쓴 컴퓨터의 IP | 서비스 계정 `BOXServiceAccount@[customerforest].prod.outlook.com` | `Set-AccessToCustomerDataRequest` | Lockbox 요청의 GUID |
| 승인 뒤 Microsoft 엔지니어의 작업 | 작업한 시각 | 엔지니어가 쓴 컴퓨터의 IP | `Microsoft Operator` | 엔지니어가 한 작업 이름 | 비어 있음 |

거부된 요청이면 승인 레코드의 `ApprovalDecision` 매개변수 값이 `Deny` 입니다[8]. Exchange Online PowerShell 에서는 다음처럼 찾습니다[8].

```powershell
Search-UnifiedAuditLog -StartDate 2026-09-01 -EndDate 2026-09-26 -Operations Set-AccessToCustomerDataRequest
Search-UnifiedAuditLog -StartDate 2026-09-01 -EndDate 2026-09-26 -UserIds "Microsoft Operator"
```

내보낸 CSV 에서는 `Operations` 열을 `Set-AccessToCustomerDataRequest` 로, `UserIds` 열을 `Microsoft Operator` 로 거르고, 세부 속성은 `AuditData` 열의 JSON 에서 봅니다[8].

Customer Lockbox 를 쓸 수 있는지는 요금제에 달려 있습니다(2025년 2월 문서 기준)[8].

| 요금제 | Customer Lockbox |
|---|---|
| Microsoft 365·Office 365 E5 | 포함 |
| 그 밖의 요금제 | Information Protection and Compliance 또는 Advanced Compliance 추가 구독이 있을 때 |
| 정부용 | Microsoft 365·Office 365 G5 에 포함 |

켜져 있는지는 Microsoft 365 관리 센터의 Settings > Org Settings > Security & Privacy > Customer Lockbox 에서 "Require approval for all data access requests" 가 선택됐는지로 확인하고, 요청 이력은 관리 센터의 Support > Customer Lockbox Requests 에서 봅니다[8].

### Entra 로그인 로그의 교차 테넌트 접근 유형

로그인 로그의 교차 테넌트 접근 유형 (crossTenantAccessType) 은 테넌트 경계를 넘은 로그인의 종류를 적습니다[10][11]. 값이 `microsoftSupport` 이면 Microsoft 외부 테넌트에 있는 Microsoft 지원 담당자가 한 교차 테넌트 로그인이고, `serviceProvider` 이면 CSP 같은 관리자가 고객을 대신해 그 고객 테넌트에 한 로그인입니다[10]. 경계를 넘지 않은 로그인은 `none` 입니다[11]. 이 필드는 Microsoft Graph 베타 signIn 리소스에 있으며[11], 홈 테넌트·리소스 테넌트 필드는 [테넌트·구독·계정·프로젝트](./tenancy.md)에서 다룹니다.

### Google 의 Access Transparency

Google Cloud 의 Access Transparency 로그는 Google 직원이 고객 데이터에 접근할 때 한 행동을 기록하고, 대상 리소스와 행동, 행동 시각, 이유, 접근자 정보(물리 위치, 고용 법인, 직무 범주)를 담습니다[4]. Cloud Audit Logs 가 고객 조직 구성원의 행동을 기록하는 것과 달리, Access Transparency 로그는 Google 직원의 행동을 기록합니다[4]. 로그 ID 는 `cloudaudit.googleapis.com/access_transparency` 이고 `_Required` 싱크로 갑니다[5]. 로그를 내는 서비스는 Google 의 지원 서비스 (Supported services) 목록에서 확인합니다[4]. 접근 전에 고객이 승인하게 하는 기능은 Access Approval 로 따로 있습니다[4].

Google Workspace 에서는 보고서 API 의 Access transparency 보고서가 Google 지원팀이 계정의 사용자 데이터에 접근한 정보를 돌려주고, 접근자의 home office 와 접근 이유 같은 매개변수를 담습니다[6].

### Slack 의 특수 행위자

Slack 감사 로그에서 행위자 ID 가 `USLACKSECURITY` 이면 Slack 보안 담당자가 고객 대신 자격 증명을 재설정한 것이고, `USLACKUSER` 이면 행위자 없이 발생한 이벤트에 넣은 자리 표시입니다[12].

## 포렌식에서 중요한 점

### 증명하는 것

- `Set-AccessToCustomerDataRequest` 레코드는 고객 조직의 승인자가 특정 Lockbox 요청을 승인하거나 거부했다는 것을 보여 줍니다[8].
- `UserIds` 가 `Microsoft Operator` 인 레코드, `crossTenantAccessType` 이 `microsoftSupport` 인 로그인, Access Transparency 로그 항목은 서비스 회사 쪽 사람이 그 시각에 고객 테넌트나 데이터에 손을 댄 기록입니다[4][8][10].
- 책임 표는 어느 층의 증거를 고객이 직접 수집할 수 있는지 판단하는 근거가 됩니다. IaaS 에서는 게스트 운영체제가 고객 몫이라 디스크와 운영체제 로그를 고객이 수집할 수 있습니다[1][2].

### 증명하지 못하는 것

- 책임 표는 누가 설정·운영할 책임이 있는지를 보여 줄 뿐 어떤 로그가 있는지를 보장하지 않고, 법적 결론도 아닙니다[2].
- Customer Lockbox 가 꺼져 있거나 요금제에 없으면 승인 흐름 레코드는 생기지 않으므로, `Set-AccessToCustomerDataRequest` 가 없다는 것만으로 Microsoft 엔지니어의 접근이 없었다고 쓸 수 없습니다[8].
- Access Transparency 는 지원 서비스 목록에 있는 서비스에서만 로그를 냅니다[4]. 목록 밖 서비스에 항목이 없다는 것은 접근이 없었다는 뜻이 아닙니다.
- Customer Lockbox 는 수사기관 같은 제3자의 데이터 요청을 막는 기능이 아닙니다[8]. 그런 요청과 그 처리 기록은 고객 쪽 감사 로그의 범위 밖일 가능성이 있습니다.

### 시각

통합 감사 로그의 `CreationTime` 은 레코드가 만들어진 UTC 시각입니다[9]. Lockbox 승인 레코드의 시각은 승인·거부한 시각이고, 승인 뒤 엔지니어의 작업은 승인 시각부터 4시간 안에 일어나며, 엔지니어에게 주는 권한은 최대 4시간입니다[8]. 요청은 12시간 안에 응답하지 않으면 만료됩니다[8]. 그래서 `Microsoft Operator` 레코드는 가장 가까운 앞선 승인 레코드와 4시간 창으로 짝을 맞춰 봅니다. Google Workspace 의 Access Transparency 로그 이벤트는 몇 분 안에 들어옵니다(2026년 9월 문서 기준)[7]. 서비스별 시각 형식과 지연은 [클라우드 로그의 시각](../logging/timestamps.md)과 각 아티팩트 쪽에서 다룹니다.

## 함정

- "SaaS 라서 서비스 회사가 다 기록해 준다" 는 오해가 흔합니다. SaaS 에서도 데이터와 접근 정책은 고객 몫이고[2][3], 감사 수집 설정은 고객 설정이라 꺼져 있을 수 있습니다[17]. 기본으로 남는 기록과 켜야 남는 기록은 [기록은 어디에 남나](./where-records-live.md)에서, 보관 기간은 [보관 기간과 라이선스](../logging/retention-licensing.md)에서 다룹니다.
- `UserType` 3(DCAdmin)·4(System) 레코드나 `microsoftSupport` 로그인을 공격자로 오인하기 쉽습니다. 반대로 공격 흔적을 "Microsoft 내부 작업" 으로 치워 두는 실수도 생깁니다. 서비스 회사 쪽 작업이라고 판단하기 전에 Lockbox 승인 레코드, 고객이 연 지원 요청 번호와 대조합니다[8][9][10].
- Entra 관련 이벤트는 관리자 작업도 `UserType` 0 으로 남아서, `UserType` 만으로 관리자 작업을 거르면 빠집니다[9].
- 공개 API 로 보이는 범위도 서비스 회사가 정합니다. 2022년 OneDrive 개인 계정을 대상으로 한 연구에서 공개 API 로는 Personal Vault 에 일부만 접근할 수 있었고 휴지통 (Recycle Bin) 에는 전혀 접근할 수 없었으며, 상용 도구들도 전용 클라이언트에 보이는 자료를 모두 모으지 못했습니다[15]. 서비스 회사가 협조하면 서비스 회사를 거쳐 자료를 받을 수 있고, 협조하지 않으면 사용자 쪽에서 온라인으로 수집해야 합니다[15]. 요청 절차는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)에서 다룹니다.
- 사고 대응은 고객과 서비스 회사의 책임이 쉽게 나뉘지 않는 영역이고, 많은 사고는 서비스 회사의 협조가 있어야 조사할 수 있습니다[3]. 조사 초기에 서비스 회사 지원 요청을 열어 둘지 [조사 절차](../../03-techniques/acquisition/investigation-process.md)에서 정합니다.
- 클라이언트 장치는 SaaS 에서도 고객 몫이 남습니다[2]. 브라우저·동기화 앱 같은 단말 쪽 흔적은 운영체제별 판에서 다루고, IaaS 가상 머신 안쪽은 [Linux 클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html)도 함께 봅니다.

## 도구

책임 경계에서 고객 몫 설정이 어떤 상태인지 먼저 수집해 두면, 어떤 기록이 있어야 하고 어떤 기록은 처음부터 없는지 가를 수 있습니다.

| 도구 | 기능 | 알려 주는 것 |
|---|---|---|
| Microsoft-Extractor-Suite | `Get-MailboxAuditStatus` | 메일함 감사 설정[16] |
| Microsoft-Extractor-Suite | `Get-Licenses`, `Get-LicenseCompatibility` | 테넌트 라이선스와 E5·P2·P1·E3 유무에 따른 기능 제한[16] |
| DFIR-O365RC | `Get-AdminAuditLogConfig` 결과의 `UnifiedAuditLogIngestionEnabled` 확인 | 통합 감사 로그 수집이 꺼져 있는지(꺼져 있으면 오류로 알림)[17] |

Customer Lockbox 레코드는 위 `Search-UnifiedAuditLog` 로 찾고, 수집 도구의 사용법은 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md)에서 다룹니다.

## 참고 문헌

1. AWS, "Shared Responsibility Model". https://aws.amazon.com/compliance/shared-responsibility-model/
2. Microsoft, "Shared responsibility in the cloud", Microsoft Learn (2026-08-24 갱신). https://learn.microsoft.com/en-us/azure/security/fundamentals/shared-responsibility
3. Google Cloud, "Shared responsibilities and shared fate on Google Cloud", Cloud Architecture Center (2023-08-21 검토). https://cloud.google.com/architecture/framework/security/shared-responsibility-shared-fate
4. Google Cloud, "Overview of Access Transparency". https://cloud.google.com/assured-workloads/access-transparency/docs/overview
5. Google Cloud, "Route log entries", Cloud Logging. https://cloud.google.com/logging/docs/routing/overview
6. Google, "REST Resource: activities", Reports API. https://developers.google.com/workspace/admin/reports/v1/reference/activities
7. Google, "Data retention and lag times", Google Workspace Admin Help. https://support.google.com/a/answer/7061566
8. Microsoft, "Microsoft Purview Customer Lockbox", Microsoft Learn (2025-02-03 갱신). https://learn.microsoft.com/en-us/purview/customer-lockbox-requests
9. Microsoft, "Office 365 Management Activity API schema", Microsoft Learn. https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
10. Microsoft, "Learn about the sign-in log activity details", MicrosoftDocs/entra-docs. https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
11. Microsoft, "signIn resource type (beta)", Microsoft Graph. https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
12. Slack, "Audit Logs API". https://api.slack.com/admins/audit-logs
13. Google Cloud, "Cloud Audit Logs overview", Cloud Logging. https://cloud.google.com/logging/docs/audit
14. Microsoft, "Resource logs in Azure Monitor", MicrosoftDocs/azure-monitor-docs. https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs.md
15. Jihyeok Yang, Jieon Kim, Jewan Bang, Sangjin Lee, Jungheum Park, "CATCH: Cloud Data Acquisition through Comprehensive and Hybrid Approaches", Forensic Science International: Digital Investigation 43 (2022) 301442. https://doi.org/10.1016/j.fsidi.2022.301442
16. invictus-ir, Microsoft-Extractor-Suite, README.md. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/README.md
17. ANSSI-FR, DFIR-O365RC, DFIR-O365RC/Get-O365.ps1. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/Get-O365.ps1
