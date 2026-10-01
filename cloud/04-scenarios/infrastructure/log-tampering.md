---
title: "로그를 끄거나 지웠나"
parent: "시나리오 · 인프라 침해"
nav_order: 800
---

# 로그를 끄거나 지웠나 (Log Tampering)

클라우드의 기록 장치(트레일·진단 설정·감사 설정·싱크·스트림)를 누가 끄거나 줄였는지, 저장된 로그를 지웠는지, 그랬다면 기록이 빈 기간은 언제부터 언제까지인지 가려내는 조사입니다. 로그 변조 (Log Tampering) 를 볼 때는 "로그가 없다" 가 아니라 "끄는 작업을 한 기록이 있다" 를 찾아야 하고, 서비스마다 있는 끌 수 없는 기록이 그 출발점이 됩니다.

## 조사 질문

- 기록 장치를 끄거나, 기록 범위를 좁히거나, 보관 기간을 줄이거나, 저장된 로그를 지운 작업이 있었나?
- 그 작업을 한 주체·시각·IP 는 무엇인가?
- 기록이 빈 기간은 언제부터 언제까지이고, 그 기간을 어느 기록으로 메울 수 있나?
- 로그가 없는 이유가 조작인가, 처음부터 켜져 있지 않았거나 보관 기간이 지난 것인가?

## 먼저 확인할 것

### 끌 수 없는 기록부터 챙긴다

주요 서비스에는 고객이 끄거나 지울 수 없는 기록이 따로 있고, 로그를 끈 작업은 대개 이 기록에 남습니다. 그래서 이 조사는 "끌 수 없는 기록에서 끄는 작업을 찾고, 빈 기간을 정하고, 그 기간을 다른 원천으로 메우는" 순서로 진행합니다.

| 서비스 | 끌 수 없는 기록 | 보관 | 참고 |
|---|---|---|---|
| AWS | CloudTrail 이벤트 기록 (Event history) — 리전별 관리 이벤트 | 90일 | 트레일·이벤트 데이터 저장소와 별개라 트레일을 바꿔도 영향을 받지 않고, KMS·RDS Data API 이벤트 제외 설정도 적용되지 않습니다[1][2]. |
| Azure | 활동 로그 (Activity Log) | 90일 | 기본으로 수집하고 바꾸거나 지울 수 없습니다[11]. |
| Google Cloud | 관리 활동·시스템 이벤트 감사 로그 | `_Required` 버킷 400일[32] | 늘 기록하고 설정·제외·끄기가 안 되며, Cloud Audit Logs 가 쓴 항목은 바꿀 수 없습니다[22]. 보관 기간은 [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md) 페이지에 있습니다. |
| Google Workspace | 관리 콘솔 로그 등 감사 로그 | 대개 6개월 | 관리자가 로그 데이터를 지우거나 보관 기간을 바꿀 수 없습니다[26]. |

Microsoft 365 통합 감사 로그는 관리자가 끌 수 있지만, 켜고 끈 작업 자체가 감사 기록으로 남습니다[17]. Okta 와 GitHub 는 로그 스트림을 멈추거나 지운 작업이 각 서비스의 감사 로그에 남습니다[27][31]. (2026년 9월 문서 기준)

### 요금제와 기본 설정

처음부터 켜져 있지 않은 기록은 조작의 흔적이 아닙니다. 아래는 "꺼져 있다" 를 곧바로 조작으로 읽으면 안 되는 대표적인 경우입니다(2026년 9월 문서 기준).

| 서비스 | 기본으로 꺼져 있거나 짧은 기록 |
|---|---|
| Microsoft 365 | Business Basic·Standard·Premium 과, 엔터프라이즈 무료 체험을 쓰는 비관리 테넌트는 감사가 기본으로 꺼져 있습니다[17]. |
| Microsoft Entra ID | 감사·로그인 로그 보관이 Free 7일, P1·P2 30일입니다[21]. |
| Google Cloud | BigQuery 를 뺀 데이터 접근 감사 로그는 기본으로 꺼져 있습니다[22]. |
| Azure | 리소스 로그는 진단 설정을 만들기 전에는 수집되지 않습니다[12]. |

요금제별 보관 기간 전체는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 페이지에서 봅니다.

### 수집 전에 보관 설정을 건드리지 않는다

보관 기간을 줄인 경우 실제 삭제까지 유예가 있어서, 발견한 시점에 따라 되살릴 수 있습니다. CloudWatch Logs 는 보관 기간이 지난 이벤트를 보통 72시간 안에 지우고(드물게 더 걸림)[8], Google Cloud 로그 버킷은 보관 기간을 줄이면 7일 동안 만료분을 지우지 않고[24], Azure Log Analytics 는 테이블의 전체 보관 기간을 줄이면 30일 기다린 뒤 지웁니다[13]. 보관 설정을 되돌리거나 사본을 뜨는 절차는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 페이지를 따릅니다. 이때 조사자가 한 설정 변경도 같은 작업 이름으로 기록되므로, 누가 언제 무엇을 바꿨는지 따로 적어 둡니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | AWS CloudTrail 이벤트 기록·트레일 | 트레일 중지·변경·삭제, 이벤트 선택자 변경, 로그 버킷·CloudWatch Logs 변경 | [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md) |
| 2 | CloudTrail 다이제스트 파일 | 로그 파일이 전달되지 않은 시간, 전달 뒤 바뀌거나 지워진 파일 | [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md) |
| 3 | GuardDuty 결과 | 트레일 중지·삭제, 방어 약화 (Defense Impairment) API 이상 호출 | [GuardDuty](../../02-artifacts/aws/guardduty.md) |
| 4 | Azure 활동 로그 | 진단 설정 삭제, Log Analytics 데이터 삭제·작업 영역 삭제, 경고 억제 규칙 | [활동 로그](../../02-artifacts/azure/activity-log.md), [리소스 로그와 진단 설정](../../02-artifacts/azure/resource-logs.md) |
| 5 | Microsoft 365 통합 감사 로그·설정 | 감사 켜기·끄기, 메일함 감사 우회, 짧은 보존 정책 | [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md) |
| 6 | Google Cloud 관리 활동 감사 로그 | 싱크·제외 규칙·로그 버킷 변경, 로그 삭제, 데이터 접근 로그 설정 변경 | [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md) |
| 7 | Okta 시스템 로그·GitHub 감사 로그 | 로그 스트림 끄기·지우기·대상 변경 | [Okta](../../02-artifacts/saas/okta.md), [GitHub](../../02-artifacts/saas/github.md) |
| 8 | 빈 기간을 메울 기록 | 흐름 로그, 보안 경고, 가상 머신 안의 로그 | [VPC 흐름 로그](../../02-artifacts/aws/vpc-flow-logs.md), [Defender](../../02-artifacts/m365/defender-xdr.md) |

## 분석 흐름

### 1. AWS — 트레일과 주변 기록 장치

트레일을 끄거나 바꾼 작업은 `eventSource` 가 `cloudtrail.amazonaws.com` 이고 `eventName` 이 `StopLogging`, `UpdateTrail`, `DeleteTrail` 인 레코드로 남습니다[9][10]. 트레일이 꺼졌다면 그 기간의 관리 이벤트는 이벤트 기록(콘솔, `aws cloudtrail lookup-events` 명령, LookupEvents API)에서 90일 안까지 볼 수 있습니다[1].

트레일을 끄지 않고 기록 범위만 좁혔을 수도 있습니다. 트레일과 이벤트 데이터 저장소는 관리 이벤트를 읽기만·쓰기만 남기거나, KMS·RDS Data API 이벤트를 빼거나, 고급 이벤트 선택자 (Advanced event selectors) 로 `eventName`·`eventType`·`eventSource`·`userIdentity.arn` 값에 따라 넣고 뺄 수 있습니다[2]. 선택자에는 `NotStartsWith` 같은 조건도 쓸 수 있어서 특정 역할 이름으로 시작하는 주체만 빼는 설정이 가능합니다[2]. 그래서 `StopLogging` 이 없어도 `PutEventSelectors` 레코드를 찾아보고, 트레일의 현재 이벤트 선택자를 조회해 빠진 주체나 작업이 있는지 확인합니다.

로그를 쌓는 S3 버킷 쪽 변경도 봅니다. `s3.amazonaws.com` 의 `PutBucketLogging`, `PutLifecycleConfiguration`, `PutReplicationConfiguration`, `PutEncryptionConfiguration` 같은 작업[9], `requestParameters` 에 `Suspended` 가 들어간 `PutBucketVersioning`(버전 관리 중지)[9], `DeleteBucket`[9] 이 대상입니다. 수명 주기 규칙을 바꾸면 당장은 아무것도 사라지지 않고 나중에 로그 파일이 지워지므로, 변경 시각과 삭제 시각이 다를 수 있습니다.

트레일 말고 다른 기록 장치를 끈 작업도 CloudTrail 에 남습니다(2026년 9월 기준 Sigma 규칙의 조건).

| 기록 장치 | eventSource | eventName |
|---|---|---|
| AWS Config | `config.amazonaws.com` | `DeleteDeliveryChannel`, `StopConfigurationRecorder`[9][10] |
| VPC 흐름 로그 | (규칙에 지정 없음) | `DeleteFlowLogs`[9] |
| GuardDuty | `guardduty.amazonaws.com` | `DeleteDetector`, 또는 `requestParameters.enable` 이 `false` 인 `UpdateDetector`[9] |
| CloudWatch Logs | `logs.amazonaws.com` | `DeleteLogGroup`, `DeleteLogStream`, `PutRetentionPolicy`, `DeleteRetentionPolicy`, `DeleteSubscriptionFilter`, `DeleteMetricFilter` 등[7] |

GuardDuty 를 켜 두었다면 결과 (Finding) 로도 드러납니다. `Stealth:IAMUser/CloudTrailLoggingDisabled` 는 트레일 삭제·갱신이 성공했거나 GuardDuty 와 연결된 트레일의 로그 버킷이 지워졌을 때 생기고 기본 심각도는 Low 입니다[6]. `DefenseEvasion:IAMUser/AnomalousBehavior` 는 `DeleteFlowLogs`, `DisableAlarmActions`, `StopLogging` 같은 방어 약화 API 를 평소와 다르게 부른 경우이고 기본 심각도는 Medium 입니다[6][33]. Bedrock 모델 호출 로그를 끈 경우는 `DefenseEvasion:IAMUser/BedrockLoggingDisabled` 로 나옵니다[6].

### 2. AWS — 다이제스트로 빈 기간과 변조 확인

로그 파일 무결성 검증 (Log file integrity validation) 을 켜 두었다면 다이제스트 파일로 로그 파일이 전달 뒤 바뀌었는지·지워졌는지, 어떤 시간에 로그 파일이 전달되지 않았는지를 확인할 수 있습니다[3]. 다이제스트 파일은 한 시간마다 나오고 그 시간에 API 활동이 없어도 나오므로, "이 시간에는 전달된 로그 파일이 없었다" 를 말할 수 있습니다[4]. 파일 구조와 경로는 [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md) 페이지에 있습니다.

빈 기간은 다이제스트 사슬이 끊긴 곳으로 찾습니다. 로깅을 멈추거나 트레일을 지우면 CloudTrail 은 `StopLogging` 이벤트까지 담은 마지막 다이제스트를 보내고, 검증을 끈 동안이나 로깅을 멈춘 동안 전달된 로그 파일에는 다이제스트를 만들지 않습니다[4]. 다시 켜면 이전 다이제스트를 가리키는 필드(`previousDigestS3Bucket`, `previousDigestS3Object`, `previousDigestHashValue`, `previousDigestHashAlgorithm`, `previousDigestSignature`)가 null 인 시작 다이제스트가 생깁니다[4]. 따라서 "마지막 다이제스트의 끝 시각" 과 "다음 시작 다이제스트의 시각" 사이가 빈 기간의 후보입니다.

AWS CLI 는 CloudTrail 이 전달한 위치에 있는 파일만 검증하므로, 다른 곳으로 옮긴 로그는 직접 만든 방법으로 검증해야 합니다[3].

### 3. Azure — 활동 로그에서 진단 설정·보관 변경 찾기

리소스 로그와 활동 로그를 Log Analytics·Storage·Event Hubs 로 보내는 것은 진단 설정 (Diagnostic settings) 이라서, 진단 설정을 지우면 그 뒤로는 리소스 로그가 쌓이지 않습니다[12]. 활동 로그의 `operationName` 에서 다음 작업을 찾습니다[14].

| 작업 이름 | 뜻 |
|---|---|
| `Microsoft.Insights/DiagnosticSettings/Delete` | 리소스 진단 설정 삭제 |
| `Microsoft.Insights/DiagnosticSettings/Write` | 리소스 진단 설정 생성·변경 |
| `Microsoft.Insights/ExtendedDiagnosticSettings/Delete` | 네트워크 흐름 로그 진단 설정 삭제 |
| `Microsoft.OperationalInsights/workspaces/purge/action` | 쿼리로 지정한 데이터를 작업 영역에서 삭제 |
| `Microsoft.OperationalInsights/workspaces/delete` | Log Analytics 작업 영역 삭제 |
| `MICROSOFT.SECURITY/ALERTSSUPPRESSIONRULES/WRITE` | 보안 경고 억제 규칙 생성[15] |

진단 설정을 다시 만들면 데이터가 흐르기까지 90분 안쪽이 걸리므로[12], 복구 직후의 짧은 공백은 조작이 아닐 수 있습니다. Log Analytics 는 분석 보관 기간을 API·CLI 로 최소 4일까지 줄일 수 있고, 작업 영역 보관이 30일일 때 `immediatePurgeDataOn30Days` 속성을 켜면 30일 뒤 바로 지워 되살릴 수 없습니다[13]. 작업 영역 설정에서 이 두 값을 확인합니다.

가상 머신 안에서 감사를 끈 경우는 Defender for Cloud 경고 "Disabling of auditd logging" 으로 나올 수 있고[16], 머신 안의 기록은 [클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html) 과 [인증 로그](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/logins/auth-log.html) 페이지의 방법으로 봅니다.

### 4. Microsoft 365 — 감사 끄기·우회·짧은 보존

통합 감사 로그를 끄면 Purview 감사 검색, `Search-UnifiedAuditLog`, Office 365 Management Activity API, Microsoft Sentinel 모두에서 결과가 나오지 않습니다[17]. 현재 상태는 Exchange Online PowerShell 에서 확인합니다[17].

```powershell
Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled
```

`True` 면 켜져 있고 `False` 면 꺼져 있습니다[17]. 켜고 끈 기록은 다음 명령으로 찾고, 기록에는 바꾼 시각·관리자·IP 가 있으며 `AuditData` 속성 안의 `UnifiedAuditLogIngestionEnabled` 값으로 켰는지 껐는지 구별합니다[17].

```powershell
Search-UnifiedAuditLog -Operations Set-AdminAuditLogConfig
```

감사를 끄지 않고 특정 계정만 빼는 방법도 있습니다. `AuditBypassEnabled` 가 켜진 계정은 어느 메일함에 접근하거나 무엇을 해도 메일함 감사에 남지 않습니다[19]. 우회가 걸린 계정은 다음 명령으로 봅니다[19].

```powershell
Get-MailboxAuditBypassAssociation -ResultSize unlimited | Format-Table Name,AuditBypassEnabled
```

Microsoft-Extractor-Suite 의 `Get-MailboxAuditStatus` 는 조직 설정(`Get-OrganizationConfig` 의 `AuditDisabled`), 메일함별 감사 설정, 우회 연결을 모아 메일함마다 `Enabled (Organization Policy)`, `Bypassed`, `Disabled` 중 하나로 정리합니다[20].

사용자 정의 감사 보존 정책은 기본 정책보다 우선하므로, 예를 들어 Exchange 메일함 활동에 1년보다 짧은 정책을 만들면 그 짧은 기간만 남습니다[18]. 기간은 7 Days, 30 Days, 6 Months, 9 Months, 1 Year, 3 Years, 5 Years, 7 Years 가운데서 고르고(10 Years 는 추가 라이선스), 우선순위는 1(가장 높음)부터 10000 까지입니다[18]. Security & Compliance PowerShell 에서 현재 정책을 조회해 짧은 정책이 있는지 봅니다(이 명령은 기본 정책은 보여 주지 않습니다)[18].

```powershell
Get-UnifiedAuditLogRetentionPolicy | Sort-Object -Property Priority -Descending | FL Priority,Name,Description,RecordTypes,Operations,UserIds,RetentionDuration
```

Entra ID 로그는 보관이 짧아서 진단 설정으로 내보내 두어야 오래 남습니다. 내보내는 방법은 [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md) 페이지에 있습니다.

### 5. Google Cloud — 싱크·제외 규칙·버킷

로그 설정을 바꾸는 메서드는 권한 유형이 `ADMIN_WRITE` 라서 관리 활동 감사 로그에 남습니다[23]. `protoPayload.methodName` 으로 다음을 찾습니다[23].

| 메서드 | 뜻 |
|---|---|
| `google.logging.v2.ConfigServiceV2.DeleteSink`, `UpdateSink` | 로그를 밖으로 보내는 싱크 삭제·변경 |
| `google.logging.v2.ConfigServiceV2.CreateExclusion`, `UpdateExclusion` | 특정 로그를 버킷에 넣지 않는 제외 규칙 생성·변경 |
| `google.logging.v2.ConfigServiceV2.UpdateBucket`, `UpdateBucketAsync`, `DeleteBucket` | 로그 버킷 보관 기간 변경·삭제 |
| `google.logging.v2.ConfigServiceV2.UpdateSettings` | 로그 설정 변경 |
| `google.logging.v2.LoggingServiceV2.DeleteLog` | 로그 삭제 |

로그 탐색기에서 쓰는 쿼리의 모양은 다음과 같습니다[23].

```text
protoPayload.methodName="google.logging.v2.ConfigServiceV2.CreateExclusion"
```

데이터 접근 감사 로그는 Cloud Resource Manager API 의 `setIamPolicy` 로 빈 `auditConfigs:` 를 넣은 IAM 정책을 설정하면 프로젝트 전체에서 꺼집니다(일부 BigQuery 로그 제외)[25]. 이 경우 프로젝트 IAM 정책을 바꾼 기록 전후의 정책을 비교해 `auditConfigs` 가 비었는지 확인합니다.

로그 버킷은 지워도 바로 사라지지 않습니다. 보관 기간을 줄이면 7일 동안 만료분을 지우지 않고(조회는 안 되지만 보관 기간을 다시 늘리면 되살아남), 버킷을 지우면 `DELETE_REQUESTED` 상태로 7일 머무는 동안에도 로그가 계속 들어옵니다[24]. 잠긴 버킷은 모든 항목이 보관 기간을 채우기 전에는 지울 수 없습니다[24].

### 6. Okta·GitHub — 로그 스트림

Okta 시스템 로그의 `eventType` 에서 `system.log_stream.lifecycle.deactivate`, `system.log_stream.lifecycle.delete`, `system.log_stream.lifecycle.update` 를 찾습니다[27]. 이 가운데 `deactivate` 는 사용자뿐 아니라 Okta 도 할 수 있으므로 행위자가 누구인지 확인합니다[27]. Workflows 실행 로그 스트리밍을 끈 경우는 `workflows.user.execution_log_stream_connection.deactivate` 로 남습니다[27]. 시스템 로그는 90일 동안만 조회됩니다[28].

GitHub Enterprise 감사 로그의 `action` 에서 `audit_log_streaming.destroy`(엔드포인트 삭제)와 `audit_log_streaming.update`(일시 정지·켜기·끄기 등 설정 변경)를 찾습니다[31]. `update` 기록에는 `audit_log_stream_enabled` 와, 대상을 바꾼 경우 `old_s3_bucket`·`new_s3_bucket` 같은 이전·새 대상 필드가 있습니다[31]. 스트림을 멈추면 7일 동안은 버퍼가 남아 잃는 데이터가 없고, 7일을 넘기면 재개 시점 1주 전부터 다시 보내며, 3주 이상 멈추면 버퍼 없이 재개 시점부터 새로 시작합니다[30]. 감사 로그 자체는 180일, Git 이벤트는 7일 동안 남습니다[29].

### 7. 빈 기간을 메운다

끄는 작업을 찾았으면 그 시각부터 다시 켠 시각까지를 빈 기간으로 정하고, 끌 수 없는 기록(이벤트 기록·활동 로그·`_Required` 버킷)과 흐름 로그, GuardDuty·Defender 결과, 가상 머신 안의 로그로 그 기간을 메웁니다. 모든 원천의 시각을 UTC 로 맞춰 시간순으로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 과 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 페이지에 있습니다. 끄는 작업을 한 주체가 어떻게 그 권한을 얻었는지는 [권한을 올렸나](privilege-escalation.md), 그 자격 증명이 어디서 왔는지는 [액세스 키가 새어 나갔나](leaked-keys.md) 로 이어서 봅니다.

## 증명하는 것 / 증명하지 못하는 것

기록 장치를 끄거나 바꾼 레코드(`StopLogging`, `Microsoft.Insights/DiagnosticSettings/Delete`, `Set-AdminAuditLogConfig`, `DeleteSink`, `audit_log_streaming.update` 등)는 이 주체가 이 시각에 이 설정을 바꿨다는 것을 보여 줍니다. CloudTrail 다이제스트는 어떤 시간에 로그 파일이 전달되지 않았는지, 전달된 파일이 그 뒤로 바뀌지 않았는지를 보여 줍니다[3].

기록이 꺼진 동안 무슨 일이 있었는지는 이 기록만으로 알 수 없어서 다른 원천으로 메워야 합니다. 처음부터 켜져 있지 않았던 기록과 보관 기간이 지나 사라진 기록은 설정 변경 레코드가 남지 않으므로, 조작이 있었다고 말할 근거가 되지 않습니다.

## 흔한 오판

- **로그가 없으니 지웠다고 판단한다.** 요금제에 따라 기본으로 꺼져 있거나(Microsoft 365 Business 요금제[17], Google Cloud 데이터 접근 로그[22]) 보관 기간이 짧은(Entra ID Free 7일[21]) 경우가 있습니다. 설정 변경 기록이 있을 때만 "껐다" 고 씁니다.
- **Security & Compliance PowerShell 결과로 감사가 꺼졌다고 본다.** 이 환경에서 `Get-AdminAuditLogConfig` 를 부르면 `UnifiedAuditLogIngestionEnabled` 가 켜져 있어도 늘 `False` 로 나오므로, Exchange Online PowerShell 에서 다시 확인합니다[17].
- **다이제스트 사슬이 끊겼으니 누가 멈췄다고 본다.** 버킷 정책 오류나 서비스 장애로 다이제스트가 빠질 수 있고, 다시 전달되는 동안에는 순서가 뒤바뀌어 잠깐 끊겨 보일 수 있습니다[4]. `get-trail-status` 의 `LatestDigestDeliveryError` 값과 `StopLogging` 레코드를 함께 봅니다[4].
- **`StopLogging` 이 없으니 로깅은 온전했다고 본다.** 이벤트 선택자로 특정 주체나 작업만 뺄 수 있습니다[2].
- **Sigma 규칙이 잡은 레코드를 모두 성공으로 본다.** `aws_cloudtrail_disable_logging` 규칙은 `errorCode` 를 보지 않아 실패한 시도도 잡고, 2025년에 나온 `DeleteFlowLogs`·`DeleteBucket`·GuardDuty 규칙은 `errorCode` 가 `Success` 이거나 null 인 레코드만 잡습니다[9]. CloudTrail 레코드의 `errorCode` 는 요청이 오류를 돌려줄 때만 있는 필드이므로[5], 성공 여부는 `errorCode` 가 없는지로 판단합니다.
- **조사자가 한 설정 변경을 공격자 행위로 섞는다.** 보관 기간을 늘리거나 스트림을 다시 켠 대응 작업도 같은 작업 이름으로 남으므로 타임라인에 따로 표시합니다.

## 보고서 문장 예

아래 계정·시각·IP 는 만든 예시입니다.

- "2026-03-04 02:17:09 UTC 에 `arn:aws:iam::123456789012:user/ops-admin` 주체가 IP 203.0.113.25 에서 트레일 `org-trail` 에 대해 `StopLogging` 을 호출한 기록이 CloudTrail 이벤트 기록에 있다. 같은 트레일의 다음 시작 다이제스트는 2026-03-04 06:00 UTC 구간이며, 그 사이 이 트레일에 전달된 로그 파일은 없다."
- "2026-03-05 11:02 UTC 에 admin@contoso.com 계정이 IP 198.51.100.7 에서 `Set-AdminAuditLogConfig` 를 실행했고, 해당 감사 기록의 `UnifiedAuditLogIngestionEnabled` 값은 False 다. 이 시각부터 감사가 다시 켜진 시각까지 통합 감사 로그에는 기록이 없다."
- "테넌트는 Business Standard 요금제이고 감사를 켜거나 끈 기록이 없으므로, 통합 감사 로그가 비어 있는 것은 기본 설정에 따른 것으로 보이며 조작 여부는 이 기록으로 판단할 수 없다."

보고서 전체의 짜임은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 페이지에 있습니다.

## 함께 볼 페이지

- [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) — 보관 설정을 되돌리고 사본을 뜨는 절차
- [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md) — 이벤트 기록·활동 로그·감사 로그 내려받기
- [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md) — 통합 감사 로그와 감사 설정 수집
- [탐지 규칙으로 로그 검색하기](../../03-techniques/analysis/detection-rules.md) — Sigma 규칙을 로그에 돌리는 법
- [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) — 서비스·요금제별 보관 기간
- [권한을 올렸나](privilege-escalation.md), [액세스 키가 새어 나갔나](leaked-keys.md), [채굴용 자원을 만들었나](cryptomining.md) — 로그를 끄는 작업과 함께 자주 나오는 행위

## 참고 문헌

1. AWS, "Working with CloudTrail event history", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
2. AWS, "Logging management events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-management-events-with-cloudtrail.html
3. AWS, "Validating CloudTrail log file integrity", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html
4. AWS, "CloudTrail digest file structure", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-digest-file-structure.html
5. AWS, "CloudTrail record contents for management, data, and network activity events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
6. AWS, "GuardDuty IAM finding types", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-iam.html
7. AWS, "Logging Amazon CloudWatch Logs API and console operations in AWS CloudTrail", Amazon CloudWatch Logs User Guide. https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/logging_cw_api_calls_cwl.html
8. AWS, "Working with log groups and log streams", Amazon CloudWatch Logs User Guide. https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html
9. SigmaHQ, AWS CloudTrail 탐지 규칙(aws_cloudtrail_disable_logging, aws_s3_data_management_tampering, aws_disable_bucket_versioning, aws_cloudtrail_bucket_deleted, aws_config_disable_recording, aws_cloudtrail_vpc_flow_logs_deleted, aws_cloudtrail_guardduty_detector_deleted_or_updated). https://github.com/SigmaHQ/sigma/tree/master/rules/cloud/aws/cloudtrail
10. Invictus Incident Response, Invictus-AWS (source/files/queries.yaml). https://github.com/invictus-ir/Invictus-AWS
11. Microsoft, "Activity log in Azure Monitor" (ms.date 2026-05-04). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
12. Microsoft, "Diagnostic settings in Azure Monitor" (ms.date 2026-03-31). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/data-collection/diagnostic-settings.md
13. Microsoft, "Manage data retention in a Log Analytics workspace" (ms.date 2026-09-02). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/data-retention-configure.md
14. Microsoft, "Azure permissions for Monitor", Azure RBAC 문서. https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/monitor
15. SigmaHQ, Azure 활동 로그 탐지 규칙(azure_suppression_rule_created). https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_suppression_rule_created.yml
16. Microsoft, "Alerts for Linux machines", Microsoft Defender for Cloud 문서. https://learn.microsoft.com/en-us/azure/defender-for-cloud/alerts-linux-machines
17. Microsoft, "Turn auditing on or off", Microsoft Purview 문서. https://learn.microsoft.com/en-us/purview/audit-log-enable-disable
18. Microsoft, "Manage audit log retention policies", Microsoft Purview 문서. https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
19. Microsoft, "Get-MailboxAuditBypassAssociation", Exchange PowerShell 문서. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Get-MailboxAuditBypassAssociation.md
20. Invictus Incident Response, Microsoft-Extractor-Suite (Scripts/Get-AuditLogSettings.ps1). https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AuditLogSettings.ps1
21. Microsoft, "Microsoft Entra data retention" (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
22. Google Cloud, "Cloud Audit Logs overview" (Last updated 2026-09-25). https://cloud.google.com/logging/docs/audit
23. Google Cloud, "Cloud Logging audit logging" (Last updated 2026-09-25). https://cloud.google.com/logging/docs/audit-logging
24. Google Cloud, "Configure log buckets" (Last updated 2026-09-25). https://cloud.google.com/logging/docs/buckets
25. Google Cloud, "Enable Data Access audit logs" (Last updated 2026-09-25). https://cloud.google.com/logging/docs/audit/configure-data-access
26. Google, "Data retention and lag times", Google Workspace 관리자 고객센터. https://support.google.com/a/answer/7061566
27. Okta, "Event types" (okta-event-types.csv). https://developer.okta.com/docs/okta-event-types.csv
28. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
29. GitHub, "Audit log for an enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/about-the-audit-log-for-your-enterprise
30. GitHub, "Streaming the audit log for your enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/streaming-the-audit-log-for-your-enterprise
31. GitHub, "Audit log events for your enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/audit-log-events-for-your-enterprise
32. Google Cloud, "Quotas and limits", Cloud Logging 문서 (Last updated 2026-09-25). https://cloud.google.com/logging/quotas
33. MITRE ATT&CK, "Disable or Modify Tools: Disable or Modify Cloud Log, T1685.002" (v19, Last Modified 2026-05-12). https://attack.mitre.org/techniques/T1685/002/
