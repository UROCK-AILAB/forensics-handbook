---
title: "보관 기간과 라이선스"
parent: "기반 · 로그 체계"
nav_order: 90
---

# 보관 기간과 라이선스 (Retention·Licensing)

클라우드 로그는 서비스와 요금제가 정한 기간이 지나면 사라지고, 라이선스에 따라서는 처음부터 생기지 않는 기록도 있어서, 로그를 받기 전에 조사할 수 있는 기간과 범위부터 정합니다.

## 이 형식을 쓰는 아티팩트

이 페이지는 파일 형식이 아니라 모든 클라우드 로그에 붙는 세 가지 조건을 다룹니다. 첫째는 레코드가 얼마 동안 남는지(보관 기간, retention)이고, 둘째는 라이선스나 요금제에 따라 레코드가 생기는지이며, 셋째는 조회 경로마다 한 번에 꺼낼 수 있는 기간과 양의 한도입니다. 어느 로그가 기본으로 켜지는지는 [로그의 종류](log-types.md)에서, 로그가 어디에 저장되는지는 [기록은 어디에 남나](../model/where-records-live.md)에서 다룹니다.

이 조건의 영향을 받는 로그는 [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md), [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md), [CloudWatch Logs](../../02-artifacts/aws/cloudwatch-logs.md), [활동 로그](../../02-artifacts/azure/activity-log.md), [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md), [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md), [Okta 시스템 로그](../../02-artifacts/saas/okta.md), [GitHub 감사 로그](../../02-artifacts/saas/github.md), [Dropbox·Box 기록](../../02-artifacts/saas/dropbox-box.md), [Slack 감사 로그](../../02-artifacts/saas/slack.md)입니다.

## 구조

아래 값은 모두 2026년 9월 문서 기준입니다. 보관 기간과 라이선스 조건은 자주 바뀌므로 사건마다 참고 문헌의 원문을 다시 엽니다.

### Microsoft 365 통합 감사 로그

통합 감사 로그 (Unified Audit Log) 의 보관 기간은 테넌트 하나에 값 하나가 아니라, 레코드를 만든 사용자의 라이선스와 레코드의 `Workload` 에 따라 정해집니다[14][15].

| 조건 | 보관 기간 |
|---|---|
| Audit(Standard), 2023년 10월 17일 이후에 생긴 레코드 | 180일[14] |
| Audit(Standard), 2023년 10월 17일 전에 생긴 레코드 | 90일[14] |
| Audit(Premium) 기본 정책: 활동한 사용자에게 Office 365·Microsoft 365 E5, Microsoft Purview Suite(옛 Microsoft 365 E5 Compliance), E5 eDiscovery and Audit 추가 라이선스 가운데 하나가 있고 `Workload` 가 `AzureActiveDirectory`·`Exchange`·`OneDrive`·`SharePoint` 인 레코드 | 1년[14] |
| 위 조건의 사용자가 한 그 밖의 `Workload` 활동 | 180일(사용자 지정 정책으로 바꿀 수 있음)[14] |
| E5 가 아닌 사용자와 게스트 사용자의 레코드 | 180일[14] |
| 서비스 주체·시스템 이벤트·앱 활동처럼 사용자가 아닌 주체의 레코드 | 1년 고정, 사용자 지정 정책이 적용되지 않음[15] |
| 사용자 지정 보존 정책 | 7일·30일·6개월·9개월·1년·3년·5년·7년 중 선택. 7일·30일은 Microsoft 365 E5 가, 3년·5년·7년은 E5 에 더해 10-Year Audit Log Retention 추가 라이선스가 있어야 함[14] |
| 10년 | 레코드를 만든 사용자에게 E5 와 10-Year Audit Log Retention 추가 라이선스가 있고 10년 정책이 있어야 함[14][15] |

레코드의 보관 만료 시점은 감사 파이프라인이 레코드를 넣을 때 그때의 라이선스와 보존 정책으로 정해집니다[15]. 라이선스나 정책을 나중에 바꾸면 그 뒤에 들어오는 레코드에만 적용되고, 이미 들어간 레코드는 달라지지 않습니다[15]. 10년 정책도 정책을 만들기 전에 생긴 레코드는 붙잡지 못합니다[15]. 사용자 지정 정책은 기본 정책보다 우선해서, Exchange 사서함 활동에 1년보다 짧은 정책을 걸면 그 레코드는 짧은 기간만 남습니다[14].

라이선스는 보관 기간뿐 아니라 기록이 생기는지에도 영향을 줍니다.

| 항목 | 조건 |
|---|---|
| 감사 로깅 켜짐 | Microsoft 365 조직은 기본으로 켜짐. Microsoft 365 Business Basic·Business Standard·Business Premium 과 엔터프라이즈 무료 평가판으로 만든 관리되지 않는 테넌트는 기본으로 꺼져 있어 직접 켜야 함[16] |
| `MailItemsAccessed` | Audit(Standard) 기능이고, Office 365·Microsoft 365 E3·E5 사용자에게 기본으로 켜짐[19] |
| Premium 전용 속성 | Audit(Premium) 라이선스가 있는 사용자만 일부 활동에 속성이 더 붙음. 예: `MailItemsAccessed` 의 `SensitivityLabel`, Teams `MessageRead`·`MessageSent`·`ChatRetrieved` 등의 `AppAccessContext`[15] |
| 검색 결과 내보내기 | Audit(Standard) 50,000행, Audit(Premium) 1,000,000행까지[17][18] |
| Office 365 Management Activity API 대역폭 | 모든 조직이 분당 2,000 요청에서 시작하고, 좌석 수와 라이선스에 따라 늘어나며, E5·A5·G5 조직은 약 두 배[15] |

Office 365 Management Activity API 는 콘텐츠가 올라온 뒤 7일 안의 것만 돌려주고, 요청의 시작 시각은 7일보다 이전일 수 없으며 시작과 끝의 차이는 24시간 이하여야 합니다[20]. 이 한도는 통합 감사 로그의 보관 기간과 따로 움직입니다.

### Entra ID

Entra ID 의 감사·로그인 로그는 통합 감사 로그와 따로 보관되고, 통합 감사 로그의 보관은 Entra ID 라이선스를 바꿔도 달라지지 않습니다[13].

| 보고서 | Free | P1 | P2 |
|---|---|---|---|
| 감사 로그 | 7일 | 30일 | 30일 |
| 로그인 로그 | 7일 | 30일 | 30일 |
| 다단계 인증 사용 | 30일 | 30일 | 30일 |
| Microsoft Graph 활동 로그 | 없음 | 저장소·분석 도구로 보내야만 남음 | 저장소·분석 도구로 보내야만 남음 |
| 위험한 사용자 | 제한 없음 | 제한 없음 | 제한 없음 |
| 위험한 로그인 | 7일 | 30일 | 90일 |

표의 출처는 [13]입니다. P1·P2 는 구독에 가입할 때부터 수집하고, Free 는 Entra ID 화면을 처음 열거나 보고 API 를 처음 쓸 때부터 수집합니다[13]. Microsoft Graph 활동 로그는 진단 설정에서 그 범주를 켠 때부터 모입니다[13]. Free 에서 P1·P2 로 올려도 이미 지난 데이터는 돌아오지 않아서, 올린 직후에 볼 수 있는 과거는 Free 보관 기간인 7일까지입니다[13]. External ID Basic 요금제의 로그는 7일 보관됩니다[13]. E5·Microsoft Purview Suite·E5 eDiscovery and Audit 추가 라이선스가 있으면 Audit(Premium) 으로 Entra ID 감사 로그를 더 오래 둘 수 있습니다[13].

### Azure

| 기록 | 보관 |
|---|---|
| 활동 로그 | 90일 뒤 삭제, 그 기간에는 양과 상관없이 요금 없음[10] |
| 리소스 로그 | 진단 설정이 없으면 모이지 않고, 모이면 목적지(Log Analytics 작업 영역·저장소 계정·이벤트 허브)의 보관을 따름[10][12] |
| Log Analytics 작업 영역 표 | 기본 30일. `AzureActivity`·`Usage` 와 Application Insights 표는 기본 90일이고 그 기간 요금 없음[11] |
| Log Analytics 분석 보관 (Analytics retention) | 최대 2년(730일). 31일 분석 보관은 수집 요금에 포함[11] |
| Log Analytics 전체 보관 (total retention) | 최대 12년(4,383일). 포털·API 로는 12년, CLI·PowerShell 로는 7년까지 설정됨[11] |

자원을 누가 만들었는지는 활동 로그에만 남기 때문에, 90일이 지나면 진단 설정으로 내보내 둔 사본에서만 찾을 수 있습니다[10]. 전체 보관 기간을 줄이면 Azure Monitor 는 30일을 기다린 뒤 데이터를 지웁니다[11]. 30일 보관으로 설정한 작업 영역에도 데이터가 31일까지 남을 수 있습니다[11].

### AWS

| 기록 | 보관 |
|---|---|
| CloudTrail 이벤트 기록 (Event history) | 리전별 최근 90일 관리 이벤트, 보기 요금 없음[1]. 새로 기록하기 시작한 이벤트 종류는 90일이 지나야 90일치가 모두 채워짐[1] |
| CloudTrail 트레일 | S3 버킷에 원하는 만큼 둘 수 있고, S3 수명 주기 규칙으로 자동 보관·삭제를 정함[2] |
| CloudTrail Lake 이벤트 데이터 저장소 | "1년 연장 가능" 요금제는 기본 366일·최대 3,653일, "7년" 요금제는 기본·최대 2,557일[5]. 보관 여부는 레코드의 `eventTime` 으로 판단[4] |
| CloudWatch Logs 로그 그룹 | 기본 무기한[6]. `retentionInDays` 값은 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653 가운데 하나[7] |
| VPC 흐름 로그 | CloudWatch Logs 나 S3 로 보내므로 목적지의 보관 설정을 따름[8] |
| S3 서버 접근 로그 | CloudWatch Logs 로그 그룹이나 S3 범용 버킷으로 보내므로 목적지의 보관 설정을 따름[9] |

트레일이 S3 버킷에 로그 파일을 전달하지 못하면 CloudTrail 은 30일 동안 다시 전달을 시도합니다[2]. CloudTrail Lake 는 2026년 5월 31일부터 새 고객을 받지 않으므로, 그 전에 쓰던 계정에만 이벤트 데이터 저장소가 있을 수 있습니다[3].

### Google Cloud

Cloud Logging 은 로그를 로그 버킷 (log bucket) 에 담고, 보관 기간은 버킷마다 정해집니다[25].

| 버킷 | 자원 | 기본 보관 | 바꾸기 |
|---|---|---|---|
| `_Required` | 프로젝트·폴더·조직 | 400일 | 바꿀 수 없음 |
| `_Default` | 폴더·조직 | 30일 | 바꿀 수 없음 |
| `_Default` | 프로젝트 | 30일 | 1~3650일 |
| 사용자 정의 | 프로젝트 | 30일 | 1~3650일 |

표의 출처는 [25]입니다. Admin Activity·System Event 감사 로그는 `_Required` 에, 켜 둔 Data Access 감사 로그와 Policy Denied 감사 로그는 `_Default` 에 들어갑니다[24]. 2023년 4월 1일부터는 `_Default` 와 사용자 정의 버킷에서 기본 보관 기간을 넘겨 둔 로그에 요금이 붙습니다[25]. 폴더·조직에는 사용자 정의 버킷을 만들 수 없고 버킷 보관 기간을 늘릴 수도 없어서, 폴더·조직 단위 로그를 오래 두려면 싱크 (sink) 로 다른 목적지에 보내야 합니다[27]. 버킷을 잠그면(lock) 되돌릴 수 없고, 버킷 안 모든 항목이 보관 기간을 채우기 전에는 버킷을 지울 수 없습니다[26].

### Google Workspace

Google Workspace 의 로그 이벤트는 관리자가 지우거나 보관 기간을 바꿀 수 없습니다[21].

| 로그 이벤트·보고서 | 보관 |
|---|---|
| Admin, Drive, Gmail, User 로그 이벤트(옛 이름 Login audit log), OAuth Token, SAML, Calendar, Chat, Meet, Groups, Rules, Gemini for Workspace 로그 이벤트 | 6개월[21] |
| API 로 가져오는 감사 데이터 | 6개월[21] |
| Email log search | 30일[21] |
| Meet quality tool | 30일, 28일이 지난 회의는 관리 콘솔에 표시되지 않음[21] |
| Vault 로그 이벤트 | 무기한[21] |
| Customer·User 사용량 데이터(API) | 15개월[21] |
| Entities 사용량 데이터(API) | 30일[21] |
| Chrome 앱·확장 사용 보고서, Chrome 버전 보고서 | 12개월[21] |

표에 없는 보고서와 로그 이벤트는 대체로 6개월이고, Devices 로그 이벤트는 구독에 따라 제공 여부가 다릅니다[21]. 로그와 사용량 보고서는 BigQuery 로 내보낼 수 있고, 이 기능은 Frontline Standard·Plus, Enterprise Standard·Plus, Education Standard·Plus, Enterprise Essentials Plus 에디션에서만 됩니다[22]. BigQuery 로 내보낼 때 Admin·Calendar·Groups 로그는 모든 사용자 것이 나가지만, Drive·Device 로그는 Cloud Identity Premium·Frontline Plus·Enterprise 에디션 등이 있는 도메인이 아니면 해당 라이선스를 받은 사용자 것만 나갑니다[22].

### 업무용 SaaS

| 서비스 | 기록 | 보관·요금제 조건 |
|---|---|---|
| Okta | 시스템 로그 (System Log) | 90일. 그보다 오래된 기간을 묻는 질의도 성공하지만 90일 안의 결과만 돌아옴[28] |
| GitHub Enterprise Cloud | 엔터프라이즈 감사 로그 | 180일, Git 이벤트는 7일. 화면은 기본으로 최근 3개월만 보여 주고 그 이전은 `created` 로 날짜 범위를 지정[29] |
| GitHub Enterprise Server | 감사 로그 | 엔터프라이즈 소유자가 따로 정하지 않으면 무기한[29] |
| Box | Enterprise Events | `stream_type` 이 `admin_logs` 면 1년, `admin_logs_streaming` 이면 2주[30] |
| Slack | 액세스 로그 | Pro·Business+·Enterprise 요금제에서 소유자·관리자가 봄[32]. `team.accessLogs` 는 유료 요금제에서만 되고 무료면 `paid_only` 오류[31] |
| Slack | 감사 로그 API (Audit Logs API) | Enterprise 요금제에서만, 워크스페이스가 아닌 Enterprise 조직 단위로 동작[33] |

Slack 로그의 보관 기간은 [Slack 감사 로그](../../02-artifacts/saas/slack.md)에서 다룹니다.

## 읽는 법

보관 조건은 서비스 문서만 보고 정하지 않고, 조사 대상 테넌트·계정의 실제 설정을 읽어 정합니다.

1. **조사할 기간을 표와 대조합니다.** 사건 추정 시각이 위 표의 보관 기간 밖이면 그 로그는 원본 서비스에서 더는 나오지 않으므로, 내보내 둔 사본(저장소 계정, S3 버킷, BigQuery, SIEM)이 있는지부터 찾습니다.
2. **Microsoft 365 는 감사가 켜져 있었는지와 보존 정책을 읽습니다.** 감사 켜짐 여부는 Exchange Online PowerShell 에서 아래 첫 명령으로 보고, `True` 면 켜진 것입니다[16]. 같은 cmdlet 을 Security & Compliance PowerShell 에서 실행하면 늘 `False` 로 나오므로 결과를 믿으면 안 됩니다[16]. 사용자 지정 보존 정책은 Security & Compliance PowerShell 에서 두 번째 명령으로 보고, 기본 보존 정책은 이 명령과 Purview 대시보드 어디에도 나오지 않습니다[14].

   ```powershell
   Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled
   Get-UnifiedAuditLogRetentionPolicy | Sort-Object -Property Priority -Descending | FL Priority,Name,Description,RecordTypes,Operations,UserIds,RetentionDuration
   ```

3. **사용자별 라이선스를 적어 둡니다.** 통합 감사 로그는 레코드를 만든 사용자의 라이선스로 보관 기간이 갈리므로, 조사 대상 계정마다 E5 계열과 10년 추가 라이선스가 있는지 확인합니다[14]. Entra ID 는 테넌트의 P1·P2 여부와 진단 설정이 있는지를 봅니다[13].
4. **Azure 는 작업 영역 표마다 보관 기간을 읽습니다.** 읽으려면 `Microsoft.OperationalInsights/workspaces/tables/read` 권한이 필요하고, Log Analytics Reader 역할에 이 권한이 있습니다[11]. Azure PowerShell 은 `Get-AzOperationalInsightsTable`, Azure CLI 는 `az monitor log-analytics workspace table show`, REST 는 작업 영역의 `tables` 끝점으로 읽습니다[11].
5. **AWS 는 목적지 설정을 읽습니다.** CloudWatch Logs 는 로그 그룹마다 `retentionInDays` 를 보고, 보관 정책이 없는 로그 그룹은 만료되지 않습니다[6][7]. 트레일은 목적지 S3 버킷의 수명 주기 규칙을 보고, VPC 흐름 로그·S3 서버 접근 로그는 목적지(CloudWatch Logs 로그 그룹이나 S3 버킷)의 보관 설정을 봅니다[2][8][9].
6. **Google Cloud 는 버킷 목록을 읽습니다.** 아래 첫 명령의 `RETENTION_DAYS` 열이 보관 일수이고 `LOCKED` 열이 잠금 여부이며, 두 번째 명령은 버킷 하나의 보관 일수를 `retentionDays` 로 보여 줍니다[26].

   ```bash
   gcloud logging buckets list
   gcloud logging buckets describe _Default --location=global
   ```

7. **받은 로그의 가장 오래된 레코드 시각을 적습니다.** 문서의 보관 기간과 실제로 받은 범위가 다를 수 있으므로 보고서에는 실제 값을 씁니다. 이 단계는 [기록은 어디에 남나](../model/where-records-live.md)의 읽는 법에서 다룹니다.

## 포렌식에서 중요한 점

### 증명하는 것

보관 설정과 라이선스 기록은 "이 기간, 이 사용자의 이 활동은 기록되어 있어야 한다" 는 기대 범위를 정해 줍니다. 기대 범위 안에 있어야 할 레코드가 없으면 로깅이 꺼져 있었거나 보관 설정이 바뀌었을 가능성이 있고, 이 경우 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)의 절차로 넘어갑니다.

### 증명하지 못하는 것

보관 기간이 지나 기록이 없는 기간은 활동이 없었다는 증거가 되지 못합니다. 보고서에는 "이 테넌트의 통합 감사 로그는 2026년 3월 1일 이후 레코드만 남아 있어, 그 전의 활동은 이 로그로 판단할 수 없습니다" 처럼 조사할 수 있었던 기간을 적습니다(날짜는 만든 예시). 같은 테넌트 안에서도 E5 사용자의 Exchange 레코드는 1년, E5 가 아닌 사용자와 게스트의 레코드는 180일 남으므로, 사용자 한 명의 기록이 남아 있다고 다른 사용자도 같은 기간이 남았다고 볼 수 없습니다[14].

### 소급되지 않는 변경

라이선스를 올리거나 보존 정책을 늘리는 일은 앞으로 들어올 레코드에만 적용됩니다. Entra ID 는 Free 에서 P1·P2 로 올려도 지난 로그가 돌아오지 않고, 통합 감사 로그도 레코드가 들어올 때 만료 시점이 정해집니다[13][15]. 사건을 알게 된 뒤 라이선스를 사는 것으로는 과거 기록을 되살리지 못하므로, 먼저 지금 남은 로그를 내보내 지킵니다. 절차는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)에서, Microsoft 365 의 보존 기능은 [Purview eDiscovery와 보존](../../02-artifacts/m365/purview-ediscovery.md)에서 다룹니다.

### 보관 설정이 바뀐 흔적

보관 기간을 줄이는 일은 결과만 보면 로그를 지운 것과 같습니다. CloudWatch Logs 는 보관 기간이 지난 이벤트에 삭제 표시를 한 뒤 보통 72시간 안에 지우고, 삭제 표시된 이벤트는 `storedBytes` 값에서 빠집니다[6]. 통합 감사 로그는 짧은 사용자 지정 정책이 기본 정책보다 우선합니다[14]. Log Analytics 는 전체 보관을 줄여도 30일을 기다린 뒤 지우므로, 그 안에 발견하면 설정을 되돌려 데이터를 지킬 수 있습니다[11]. Google Cloud 버킷이 잠겨 있으면 보관 기간을 채우기 전에는 버킷을 지울 수 없습니다[26].

## 함정

- **2023년 10월 17일 경계.** 통합 감사 로그 Audit(Standard) 는 이 날짜 전에 생긴 레코드가 90일, 뒤에 생긴 레코드가 180일이라 오래된 사건에서는 두 규칙이 섞입니다[14].
- **조회 경로의 한도는 보관 기간과 다릅니다.** Office 365 Management Activity API 는 최근 7일 콘텐츠만 주고[20], Google Workspace Reports API 는 `endTime` 없이 180일보다 이전의 `startTime` 을 주면 최근 180일만 주며, Gmail 요청은 시작과 끝 차이가 30일 이하여야 합니다[23].
- **오류 없이 줄어든 결과.** Okta 는 90일보다 오래된 기간을 물어도 질의가 성공하고 90일 안의 결과만 옵니다[28]. 통합 감사 로그 검색 결과를 CSV 로 내보낼 때 50,000행(Premium 1,000,000행)을 넘으면 파일에 일부 레코드가 빠집니다[18].
- **화면 기본값.** GitHub 감사 로그 화면은 기본으로 3개월만 보여 주므로 보관 기간 180일 전체를 보려면 날짜 범위를 지정합니다[29].
- **CloudWatch Logs 의 72시간.** 보관 기간이 지나 삭제 표시만 된 이벤트는 그 사이에 보관 기간을 늘리면 새 보관 기간이 끝난 뒤 72시간 안에 지워집니다[6][7].
- **폴더·조직 로그.** Google Cloud 폴더·조직의 `_Default` 버킷은 30일에서 늘릴 수 없습니다[25][27].
- **도구 기본값과 문서 값의 차이.** Microsoft-Extractor-Suite 의 `Get-UAL` 은 시작일 기본값이 오늘에서 180일 전이고, DFIR-O365RC 는 Purview 로 180일이 넘는 범위를 요청하면 멈춥니다[34][35]. Untitled Goose Tool 은 기본으로 어제까지 364일을 요청하므로, E5 가 아닌 사용자의 레코드는 앞쪽 기간이 비어 있을 수 있습니다[36][14]. Microsoft-Extractor-Suite `Get-Licenses` 의 `Retention` 열은 SKU 이름으로 정한 값(E5 365 days, E3 180 days, 그 밖 90 days)이라서 현재 문서의 Audit(Standard) 180일과 다릅니다[34][14]. 보고서에는 문서 값과 실제로 받은 범위를 씁니다.

## 도구

Microsoft 365 에서는 Microsoft-Extractor-Suite 가 테넌트 라이선스 목록(`Get-Licenses`), 사용자별 라이선스(`Get-LicensesByUser`), E5·P2·P1·E3 유무에 따른 기능 제한(`Get-LicenseCompatibility`), 사서함 감사 설정(`Get-MailboxAuditStatus`)을 뽑아 줍니다[34]. 통합 감사 로그를 받을 때 DFIR-O365RC 는 Purview 로 180일 넘는 범위를 받지 않고, Untitled Goose Tool 은 기본으로 364일 범위를 요청합니다[35][36]. 도구별 수집 방법은 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md)에서 다룹니다.

AWS·Azure·Google Cloud 는 별도 도구보다 각 클라우드의 명령줄 도구로 보관 설정을 읽는 편이 정확합니다. 위 읽는 법의 `Get-AzOperationalInsightsTable`·`az monitor log-analytics workspace table show`·`gcloud logging buckets describe` 가 그 예이고, 수집 전체 절차는 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md)에서 다룹니다.

함께 볼 페이지: [로그의 종류](log-types.md), [기록은 어디에 남나](../model/where-records-live.md), [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md), [Purview eDiscovery와 보존](../../02-artifacts/m365/purview-ediscovery.md), [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md), [클라우드 로그의 시각](timestamps.md).

## 참고 문헌

1. AWS, "Working with CloudTrail event history", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
2. AWS, "How CloudTrail works", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/how-cloudtrail-works.html
3. AWS, "Working with AWS CloudTrail Lake", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake.html
4. AWS, "CloudTrail Lake concepts and terminology", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake-concepts.html
5. AWS, "Managing CloudTrail Lake costs", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake-manage-costs.html
6. AWS, "Working with log groups and log streams", Amazon CloudWatch Logs User Guide. https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html
7. AWS, "PutRetentionPolicy", Amazon CloudWatch Logs API Reference. https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutRetentionPolicy.html
8. AWS, "Flow log records", Amazon VPC User Guide. https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html
9. AWS, "Logging requests with server access logging", Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html
10. Microsoft, "Activity log in Azure Monitor" (ms.date 2026-05-04). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
11. Microsoft, "Manage data retention in a Log Analytics workspace" (ms.date 2026-09-02). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/data-retention-configure.md
12. Microsoft, "Azure resource logs" (ms.date 2025-07-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs.md
13. Microsoft, "Microsoft Entra data retention" (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
14. Microsoft, "Manage audit log retention policies" (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
15. Microsoft, "Learn about auditing solutions in Microsoft Purview" (2026-05-18 갱신). https://learn.microsoft.com/en-us/purview/audit-solutions-overview
16. Microsoft, "Turn auditing on or off" (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-enable-disable
17. Microsoft, "Search the audit log" (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-search
18. Microsoft, "Export, configure, and view audit log records" (2026-06-19 갱신). https://learn.microsoft.com/en-us/purview/audit-log-export-records
19. Microsoft, "Use MailItemsAccessed to investigate compromised accounts" (2026-06-24 갱신). https://learn.microsoft.com/en-us/purview/audit-log-investigate-accounts
20. Microsoft, "Office 365 Management Activity API reference" (2024-12-03 갱신). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference
21. Google, "Data retention and lag times", Google Workspace Admin Help (2026-09-25 갱신). https://support.google.com/a/answer/7061566
22. Google, "About reporting logs and BigQuery", Google Workspace Knowledge Center (2026-09-18 갱신). https://knowledge.workspace.google.com/admin/reports/about-reporting-logs-and-bigquery
23. Google, "Method: activities.list", Admin SDK Reports API (2026-09-09 갱신). https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
24. Google Cloud, "Cloud Audit Logs overview" (2026-09-25 갱신). https://cloud.google.com/logging/docs/audit
25. Google Cloud, "Quotas and limits", Cloud Logging (2026-09-25 갱신). https://cloud.google.com/logging/quotas
26. Google Cloud, "Configure log buckets", Cloud Logging (2026-09-25 갱신). https://cloud.google.com/logging/docs/buckets
27. Google Cloud, "Routing and storage overview", Cloud Logging (2026-09-25 갱신). https://cloud.google.com/logging/docs/routing/overview
28. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
29. GitHub, docs 저장소 재사용 문단 `data/reusables/audit_log/retention-periods.md`·`git-events-retention-period.md`·`only-three-months-displayed.md`. https://github.com/github/docs/blob/main/data/reusables/audit_log/retention-periods.md
30. Box, "Enterprise events", Box Developer Documentation. https://developer.box.com/guides/events/enterprise-events/for-enterprise/
31. Slack, "team.accessLogs method". https://api.slack.com/methods/team.accessLogs
32. Slack, "View access logs for your workspace", Slack Help Center. https://slack.com/help/articles/360002084807-View-access-logs-for-your-workspace
33. Slack, "Audit Logs API". https://api.slack.com/admins/audit-logs
34. Invictus Incident Response, Microsoft-Extractor-Suite (`Scripts/Get-UAL.ps1`, `Scripts/Get-ProductLicenses.ps1`, `Scripts/Get-AuditLogSettings.ps1`). https://github.com/invictus-ir/Microsoft-Extractor-Suite
35. ANSSI, DFIR-O365RC (`DFIR-O365RC/Get-O365.ps1`). https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/Get-O365.ps1
36. CISA, Untitled Goose Tool (`goosey/m365_datadumper.py`). https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/m365_datadumper.py
