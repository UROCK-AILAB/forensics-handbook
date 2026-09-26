---
title: "로그부터 지키기"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 630
---

# 로그부터 지키기 (Log Preservation)

클라우드 로그는 보관 기간이 지나면 사라지고 새로 건 보존 조치는 대개 과거를 채우지 않으므로, 사고를 알게 되면 서비스 안에 남아 있는 과거분을 먼저 떠 두고 앞으로 쌓일 기록은 따로 내보내 둡니다.

## 언제 쓰나

사고를 알게 된 직후, 조사 범위를 다 정하기 전에 씁니다. 클라우드 서비스는 로그를 서비스 회사가 정한 기간만 보관하고, 그 기간은 서비스와 라이선스마다 다릅니다. 기간 표는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 쪽에 모아 두었습니다. 조사를 시작한 뒤에 라이선스를 올리거나 보존 정책을 만들어도 이미 지난 기록은 돌아오지 않습니다. Entra ID 를 무료판에서 P1·P2 로 바꾸면 무료판 보관 기간(7일) 안에 남은 기록만 보이고[9], Purview 의 10년 감사 로그 보존 정책은 정책을 만들기 전에 생긴 로그에는 적용되지 않습니다[17].

그래서 일을 둘로 나눕니다. 하나는 지금 서비스 안에 남아 있는 과거분을 복사하는 일이고, 다른 하나는 앞으로 생길 기록을 조직이 관리하는 저장소로 계속 보내는 일입니다. 두 일은 도구와 한도가 다르고, 둘 사이에 빈 구간이 생기기 쉽습니다. 전체 조사 흐름에서 이 단계가 어디쯤인지는 [조사 절차](investigation-process.md) 에 있습니다.

## 절차

### 1. 로그가 꺼져 있거나 지워진 흔적부터 확인한다

보존하려는 로그가 이미 꺼져 있었다면 떠 둘 기록도 없습니다. 복사를 시작하기 전에 로그 설정이 바뀐 기록이 있는지 먼저 봅니다. 자세한 해석은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md) 시나리오에 있습니다.

| 서비스 | 기록 | 찾는 필드·작업 이름 |
|---|---|---|
| AWS | 트레일 중지·수정·삭제 | CloudTrail 레코드에서 `eventSource` 가 `cloudtrail.amazonaws.com` 이고 `eventName` 이 `StopLogging`·`UpdateTrail`·`DeleteTrail`[26] |
| AWS | VPC 흐름 로그 삭제 | `eventName` 이 `DeleteFlowLogs` 이고 `errorCode` 가 `Success` 이거나 비어 있음[27] |
| AWS | 로그를 담던 S3 버킷 삭제 | `eventName` 이 `DeleteBucket` 이고 `errorCode` 가 `Success` 이거나 비어 있음[28] |
| Microsoft 365 | 통합 감사 로그 끄기·켜기 | 감사를 끄거나 켜면 Exchange 관리 감사 로그에 기록이 남습니다[16]. 설정 명령은 `Set-AdminAuditLogConfig` 이고, Exchange Online PowerShell 에서 `Search-UnifiedAuditLog -Operations Set-AdminAuditLogConfig` 로 찾은 레코드의 `AuditData` 안 `UnifiedAuditLogIngestionEnabled` 값으로 켰는지 껐는지 봅니다[16]. DFIR-O365RC 도 이 작업을 관심 작업 목록에 넣어 둡니다[29] |
| Google Cloud | 잘못 설정된 로그 싱크(sink) | 싱크가 잘못 설정되면 오류 내용을 담은 로그 항목이 생기고, 리소스의 Essential Contacts 에 메일이 갑니다[1] |

Microsoft 365 에서 지금 감사가 켜져 있는지는 Exchange Online PowerShell 에서 확인합니다. Security & Compliance PowerShell 에서 같은 명령을 부르면 감사가 켜져 있어도 값이 늘 `False` 로 나오므로 쓰지 않습니다[16].

```powershell
Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled
```

감사를 끄면 Purview 감사 검색과 `Search-UnifiedAuditLog` 가 결과를 돌려주지 않고, 다시 켜면 반영까지 최대 60분이 걸립니다[16].

### 2. 서비스 안에 남아 있는 과거분을 떠 둔다

과거분을 가장 빨리 받는 경로와 한 번에 받을 수 있는 한도는 아래와 같습니다(2026년 9월 문서 기준). 도구로 자동화하는 방법은 [Microsoft 365 수집 도구](m365-collection.md) 와 [AWS·Azure·GCP 수집](iaas-collection.md) 에 있습니다.

| 서비스 | 경로 | 한도와 조건 |
|---|---|---|
| Microsoft 365 통합 감사 로그 | Purview 포털 감사 검색 → CSV 내보내기 | 검색 범위는 최대 180일이고 날짜·시각은 UTC 입니다[14]. 한 번에 내보내는 건수는 Audit (Standard) 50,000건, Audit (Premium) 1,000,000건이고, 넘으면 파일에서 일부가 빠집니다[15]. 사용자가 많은 테넌트에서 범위를 넓게 잡은 검색은 끝나기까지 최대 48시간이 걸립니다[14] |
| Entra ID 로그인·감사 로그 | Entra 관리 센터 다운로드(CSV 또는 JSON) | 파일 하나에 로그인·프로비저닝 100,000건, 감사 250,000건까지 받고, 이보다 크면 브라우저 다운로드가 시간 초과로 끊길 수 있습니다[10]. 화면에서 열을 줄여도 파일에는 모든 열이 들어가고, 필터를 걸면 필터에 맞는 행만 들어갑니다[10]. Graph 로 받으려면 프리미엄 라이선스가 필요하고, 활동 로그를 보는 최소 역할은 보고서 읽기 권한자(Reports Reader)입니다[10] |
| Azure 활동 로그 | 포털 "Download as CSV", `az monitor activity-log list`, `Get-AzActivityLog` | 기본으로 90일만 보관한 뒤 지웁니다[11]. REST 로 받을 때는 `$filter` 에 `eventTimestamp` 시작값을 반드시 넣고, 시작과 끝이 모두 90일 안에 들어야 합니다[11]. CLI 의 `--max-events` 와 PowerShell 의 `-MaxRecord` 는 받는 건수를 제한하고, 건수가 많으면 내보내기가 오래 걸리므로 기간을 줄여 나눠 받습니다[11] |
| AWS CloudTrail | 트레일이 있으면 트레일 S3 버킷의 로그 파일을 그대로 복사, 없으면 이벤트 기록(Event history) 다운로드 | 이벤트 기록은 최근 90일의 관리 이벤트만 담고, 검색은 계정 하나·리전 하나씩 합니다[19]. 콘솔에서 파일 하나에 200,000건까지 받고, 넘으면 추가 파일을 받습니다[19] |
| AWS CloudWatch Logs | S3 로 내보내기 작업 | 로그가 내보낼 수 있는 상태가 되기까지 최대 12시간이 걸리고, 작업은 24시간이 지나면 시간 초과로 끝납니다[21]. 같은 계정이나 다른 계정의 버킷으로 보낼 수 있습니다[21] |
| Google Cloud Logging | 로그 버킷의 항목을 Cloud Storage 로 복사(copy) | 이미 버킷에 있는 항목을 거슬러 복사할 수 있고, 복사한 항목은 원래 버킷에도 남습니다[1][4]. Logs Explorer 의 다운로드는 10,000건까지입니다[1] |
| Google Workspace | BigQuery 내보내기 설정, Reports API | BigQuery 내보내기를 켜면 활동 데이터 180일, 사용량 데이터 450일의 과거분이 함께 들어옵니다[5]. Reports API 는 `endTime` 을 넣지 않은 요청에서 `startTime` 이 180일보다 전이면 최근 180일만 돌려주고, Gmail 요청은 `startTime`·`endTime` 을 모두 넣고 차이를 30일 이하로 잡아야 합니다[8] |
| Slack | 워크스페이스 내보내기 | 로그가 아니라 메시지 데이터입니다. Free·Pro 는 공개 채널의 메시지와 파일 링크만 받고, Business+ 는 워크스페이스 소유자가 신청해 승인받으면, Enterprise 는 비공개 채널과 DM 까지 받습니다. Free 는 최근 90일의 파일 링크만 받습니다[25]. 감사 로그는 [Slack 감사 로그](../../02-artifacts/saas/slack.md) 쪽에 있습니다 |

Exchange Online 메일처럼 로그가 아닌 사용자 데이터는 보존 방식이 다르고, [Purview eDiscovery와 보존](../../02-artifacts/m365/purview-ediscovery.md) 과 [Vault와 Takeout](../../02-artifacts/google-workspace/vault-takeout.md) 에서 다룹니다.

### 3. 앞으로 쌓일 기록을 내보낸다

과거분을 떠 둔 뒤에는 새로 생기는 기록이 보관 기간을 넘겨 사라지지 않도록 조직이 관리하는 곳으로 계속 보냅니다. 이 조치들은 대부분 건 뒤부터만 기록을 보내고, 목적지에 기록이 도착하기 시작하기까지도 시간이 걸립니다.

| 서비스 | 조치 | 걸기 전 기록 | 도착하기 시작하는 때 |
|---|---|---|---|
| Google Cloud | 로그 싱크 | 보내지 않습니다. 싱크를 만들기 전에 받은 항목은 보내지 않고, 설정이 잘못된 싱크는 고친 뒤 도착한 항목만 보냅니다[1] | Cloud Storage 로 보내는 싱크는 한 시간 단위로 묶어 쓰고, 첫 항목이 보이기까지 2~3시간이 걸립니다[3] |
| Google Cloud | 로그 버킷 보존 기간 늘리기 | 늘린 기간은 앞으로만 적용되고, 이미 보존 기간이 끝난 로그는 되살릴 수 없습니다[2] | — |
| Azure | 진단 설정(diagnostic settings) | 설정한 뒤부터 보냅니다. 리소스마다 진단 설정은 5개까지 만들 수 있습니다[12] | 만든 뒤 90분 안에 목적지로 흐르기 시작합니다[12] |
| Azure | 활동 로그를 진단 설정으로 Log Analytics 에 보내기 | 진단 설정을 만든 뒤부터 보냅니다[12]. 활동 로그는 90일이 지나면 지워지므로 그 앞 구간은 2단계 경로로 받습니다[11] | 진단 설정과 같이 90분 안에 흐르기 시작하고[12], Log Analytics 보존 기간은 최대 12년까지 늘릴 수 있습니다[11] |
| Microsoft Entra | Microsoft Graph 활동 로그 | 진단 설정에서 해당 로그 범주를 켠 때부터 모읍니다[9] | — |
| AWS | CloudTrail 트레일 | 이벤트 기록의 90일을 넘겨 계속 남기려면 트레일이나 이벤트 데이터 스토어를 만듭니다[19] | — |
| AWS | CloudTrail Lake 로 트레일 이벤트 복사 | 트레일에 이미 쌓인 이벤트를 이벤트 데이터 스토어로 복사해 그 시점의 사본을 만들 수 있습니다[20]. CloudTrail Lake 는 2026년 5월 31일부터 새 고객을 받지 않고, 기존 고객은 계속 씁니다[20] | — |
| AWS | CloudWatch Logs 구독(subscription) | 계속 보관하는 용도로는 S3 내보내기를 되풀이하지 말고 구독을 쓰도록 안내합니다[21] | — |
| AWS | GuardDuty 결과 S3 내보내기 | 결과는 90일 보관합니다[23] | 새 결과는 생긴 뒤 약 5분 안에 내보내고, 기존 결과의 갱신은 설정한 주기(기본 6시간, 15분·1시간으로 바꿀 수 있음)로 내보냅니다[23] |
| Google Workspace | BigQuery 내보내기 | 켤 때 과거 180일(활동)이 함께 들어옵니다[5] | 활동 로그는 대개 10분 안에 들어오고, 사용량 로그는 처음 설정할 때 48시간, 그 뒤에는 보통 1~3일 늦습니다[5] |

BigQuery 내보내기를 끄면 새 데이터만 들어오지 않고, 이미 있는 데이터는 Reports API 같은 다른 경로로 볼 수 있습니다[5].

### 4. 복사본을 바꿀 수 없게 둔다

복사한 로그를 담은 저장소에도 수정·삭제를 막는 설정을 겁니다.

- Azure: 진단 설정의 목적지인 Storage 계정에 불변(immutable) 정책을 걸어 수정을 막을 수 있습니다[12]. 디스크 스냅숏을 증거로 보관하는 예시 구조는 전용 구독의 불변 Blob 저장소에 사본을 두고 해시 값은 전용 Key Vault 에 두는 방식입니다[31]. 이 구조는 [클라우드 가상 머신 수집](vm-acquisition.md) 에서 다룹니다.
- AWS: CloudWatch Logs 는 S3 Object Lock 보존 기간이 걸린 버킷이나 SSE-KMS 로 암호화한 버킷으로 내보낼 수 있고, DSSE-KMS 로 암호화한 버킷으로는 내보낼 수 없습니다[21].
- Google Cloud: 로그 버킷을 잠그면(lock) 보존 정책도 함께 잠기고, 버킷 안의 모든 항목이 보존 기간을 채우기 전에는 버킷을 지울 수 없습니다[2]. 잠금은 되돌릴 수 없고 콘솔에서는 걸 수 없으며, gcloud 나 Logging API 로 겁니다[2].

```bash
gcloud logging buckets update BUCKET_ID --location=LOCATION --locked
```

받은 파일의 해시를 계산해 기록하는 방법과 공급자가 주는 무결성 증빙은 [클라우드 포렌식 보고서](../reporting/forensic-report.md) 에서 다룹니다.

### 5. 보존 조치를 기록한다

각 조치마다 누가, 어느 계정으로, 언제, 어느 구간을 받았는지 적습니다. 싱크·진단 설정·트레일을 만든 시각은 그 경로로 보존된 범위가 시작하는 시각이므로 함께 적습니다. 조사자가 만든 설정과 내려받기도 그 서비스의 로그에 남기 때문에, 이 기록이 있어야 나중에 조사자의 활동과 공격자의 활동을 가를 수 있습니다. 이 부분은 [조사 절차](investigation-process.md) 에 자세히 있습니다.

## 도구

서비스가 주는 도구만으로 이 절차를 모두 할 수 있습니다. Microsoft 365 는 Purview 포털과 Exchange Online PowerShell(`Get-AdminAuditLogConfig`), Entra ID 는 관리 센터 다운로드와 Graph, Azure 는 포털·Azure CLI(`az monitor activity-log list`)·Azure PowerShell(`Get-AzActivityLog`), AWS 는 CloudTrail 콘솔의 이벤트 기록과 CloudWatch Logs 내보내기 작업, Google Cloud 는 gcloud(`gcloud logging buckets update`)와 Logs Explorer, Google Workspace 는 관리 콘솔의 BigQuery 내보내기와 Reports API 를 씁니다. 여러 로그를 한 번에 받는 공개 도구(Microsoft-Extractor-Suite, Untitled Goose Tool, DFIR-O365RC, Invictus-AWS 등)는 [Microsoft 365 수집 도구](m365-collection.md) 와 [AWS·Azure·GCP 수집](iaas-collection.md) 에서 비교합니다.

## 함정과 한계

보존 조치를 건 시각이 곧 그 경로로 보존된 범위의 시작입니다. 싱크, 진단 설정, Entra 라이선스 변경은 과거를 채우지 않으므로[1][9][12], 과거분은 2단계의 경로로 따로 받아야 합니다. BigQuery 내보내기는 과거 180일을 채워 주지만 그보다 앞선 기록은 들어오지 않습니다[5].

AWS CloudWatch Logs 는 보존 기간에 닿은 로그를 바로 지우지 않고 보통 72시간 안에 지우며, 드물게 더 늦을 수도 있습니다[22]. 보존 기간이 지났지만 아직 지워지지 않은 로그가 있는 로그 그룹의 보존 기간을 늘려도, 그 로그는 새 보존 날짜가 지난 뒤 72시간 안에 지워집니다[22]. 보존 기간 값은 1일부터 3653일 사이의 정해진 값 가운데 고르고, 기한 없이 두려면 `DeleteRetentionPolicy` 를 씁니다[22].

Google Cloud 로그 버킷의 보존 기간을 줄이면 7일 유예 기간 동안 기간이 지난 로그를 지우지 않지만, 그동안 조회할 수는 없고 보존 기간을 다시 늘려야 접근이 돌아옵니다[2].

Google Workspace 관리자는 로그 이벤트를 지우거나 보관 기간을 바꿀 수 없습니다[7]. 그래서 Workspace 에서 로그가 비어 있다면 누가 지웠을 가능성보다 보관 기간이 지났을 가능성을 먼저 봅니다.

Google Vault 의 보존 조치(hold)가 지키는 대상은 Gmail, Groups, Chat, Drive, Voice, Gemini 앱 데이터이고 감사 로그는 목록에 없습니다[6]. 홀드를 지우거나 대상자를 홀드에서 빼면 다른 홀드에 걸리지 않은 데이터는 곧바로 보존 규칙을 따르고, 사용자가 30일보다 오래전에 지운 데이터는 곧바로 제거될 수 있습니다[6].

Workspace BigQuery 테이블의 날짜 파티션은 UTC 가 아니라 태평양 시간(PT) 기준으로 나뉩니다[5]. 파티션 날짜로 하루를 자르면 UTC 하루와 어긋나므로 `time_usec` 로 다시 거릅니다. 같은 문서 안에서 내보낸 테이블이 "자동으로 지워지지 않는다" 는 설명과 "내보낸 데이터의 기본 만료가 60일" 이라는 설명이 함께 나오므로[5], BigQuery 데이터 세트의 테이블 만료 설정을 직접 확인합니다.

Google Cloud 에서 조건이 같거나 겹치는 싱크가 여럿이면 Cloud Storage 에 같은 항목이 여러 번 쓰일 수 있고, Logging 은 중복 제거를 보장하지 않습니다[3]. AWS CloudWatch Logs 를 S3 로 내보낸 파일 안에서는 시간순 정렬이 보장되지 않습니다[21].

Azure 리소스 로그는 저장 후 전달 구조라 트랜잭션 보장이 없고 작은 손실이 생길 수 있습니다[13]. S3 서버 접근 로그도 완전성과 적시성을 보장하지 않아 레코드가 늦게 오거나 오지 않거나 중복될 수 있습니다[24]. 이런 로그에서 한 건이 비어 있다고 그 요청이 없었다고 볼 수는 없습니다.

Exchange Online 에서 사용자가 지운 항목은 기본으로 14일, 최대 30일까지 복구 가능한 항목(Recoverable Items)에 남습니다[18]. 사용자가 만든 폴더를 Shift-Delete 로 지우면 소송 보존(Litigation Hold)이 걸려 있어도 폴더 자체는 복구되지 않고 내용만 Recoverable Items\Deletions 로 옮겨집니다[18].

소송 보존(litigation hold) 기간에 증거를 일부러 잃거나 바꾸거나 없애면 증거 인멸(spoliation)로 제재받을 수 있고, 클라우드에서는 소송 당사자가 서비스 회사와 짜고 보존 대상 문서를 바꿀 수도 있습니다[30]. 그래서 복사본에는 4단계의 불변 설정과 해시 기록을 함께 남깁니다.

## 결과를 어떻게 해석하나

보존 조치 뒤 목적지에 쌓인 레코드는, 목적지 설정·불변 정책·해시 기록이 함께 남아 있으면 그 서비스가 남긴 기록의 사본이라고 말할 수 있습니다. 2단계에서 받은 파일은 받은 시각에 서비스 안에 남아 있던 기록만 담습니다.

이 절차로는 보존 조치 이전 구간이 완전했는지 증명할 수 없습니다. 조치 사이의 빈 구간도 증명하지 못하는데, Azure 진단 설정은 흐르기 시작하기까지 최대 90분[12], Cloud Storage 로 보내는 Google Cloud 싱크는 첫 항목까지 2~3시간[3], CloudWatch Logs 는 내보낼 수 있게 되기까지 최대 12시간[21]이 걸립니다. 받은 파일의 건수가 내보내기 한도(Purview 50,000건·1,000,000건, Entra 100,000건·250,000건, CloudTrail 이벤트 기록 200,000건)와 같다면 잘린 것일 가능성이 있으므로 구간을 나눠 다시 받습니다[10][15][19].

보고서에는 "2026-09-20 03:00 UTC 부터 조직 저장소로 진단 설정 로그를 보냈다" 처럼 조치 시각과 범위를 쓰고, 그 앞 구간은 어느 경로로 언제 받았는지 따로 적습니다. 시각 표기와 지연은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 에서 다룹니다. (위 시각은 만든 예시입니다.)

## 참고 문헌

1. Google Cloud, "Route log entries" (Last updated 2026-09-25). https://cloud.google.com/logging/docs/routing/overview
2. Google Cloud, "Configure log buckets" (Last updated 2026-09-25). https://cloud.google.com/logging/docs/buckets
3. Google Cloud, "View logs routed to Cloud Storage" (Last updated 2026-09-25). https://cloud.google.com/logging/docs/export/storage
4. Google Cloud, "Best practices for Cloud Audit Logs". https://cloud.google.com/logging/docs/audit/best-practices
5. Google Workspace Admin Help, "Set up service log exports to BigQuery" (Last updated 2026-09-23). https://knowledge.workspace.google.com/admin/reports/set-up-service-log-exports-to-bigquery
6. Google Workspace Admin Help, "Get started with holds in Google Vault" (Last updated 2026-09-18). https://knowledge.workspace.google.com/vault/holds/get-started-with-holds-in-google-vault
7. Google Workspace Admin Help, "Data retention and lag times" (Last updated 2026-09-25). https://support.google.com/a/answer/7061566
8. Google Workspace Admin SDK, "Method: activities.list" (Last updated 2026-09-09). https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
9. Microsoft Entra, "Microsoft Entra data retention" (ms.date 01/06/2026). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
10. Microsoft Entra, "How to download logs in Microsoft Entra ID" (ms.date 11/08/2024). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/howto-download-logs.md
11. Azure Monitor, "Activity Log in Azure Monitor" (ms.date 05/04/2026). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
12. Azure Monitor, "Diagnostic Settings in Azure Monitor" (ms.date 03/31/2026). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/data-collection/diagnostic-settings.md
13. Azure Monitor, "Resource logs in Azure Monitor" (ms.date 07/17/2025). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs.md
14. Microsoft Purview, "Search the audit log" (Last updated 2026-06-19). https://learn.microsoft.com/en-us/purview/audit-search
15. Microsoft Purview, "Export, configure, and view audit log records" (Last updated 2026-06-19). https://learn.microsoft.com/en-us/purview/audit-log-export-records
16. Microsoft Purview, "Turn auditing on or off" (Last updated 2026-06-19). https://learn.microsoft.com/en-us/purview/audit-log-enable-disable
17. Microsoft Purview, "Learn about auditing solutions in Microsoft Purview" (Last updated 2026-05-18). https://learn.microsoft.com/en-us/purview/audit-solutions-overview
18. Microsoft, "Recoverable Items folder in Exchange Online" (Last updated 2026-07-13). https://learn.microsoft.com/en-us/exchange/security-and-compliance/recoverable-items-folder/recoverable-items-folder
19. AWS, "Working with CloudTrail event history". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
20. AWS, "Working with AWS CloudTrail Lake". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake.html
21. AWS, "Exporting log data to Amazon S3". https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/S3Export.html
22. AWS, "PutRetentionPolicy" (CloudWatch Logs API Reference). https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutRetentionPolicy.html
23. AWS, "Exporting generated GuardDuty findings to Amazon S3 buckets". https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_exportfindings.html
24. AWS, "Logging requests with server access logging". https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html
25. Slack, "Export your workspace data". https://slack.com/help/articles/201658943-Export-your-workspace-data
26. SigmaHQ, "AWS CloudTrail Important Change" (aws_cloudtrail_disable_logging.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_disable_logging.yml
27. SigmaHQ, "AWS VPC Flow Logs Deleted" (aws_cloudtrail_vpc_flow_logs_deleted.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_vpc_flow_logs_deleted.yml
28. SigmaHQ, "AWS Bucket Deleted" (aws_cloudtrail_bucket_deleted.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_cloudtrail_bucket_deleted.yml
29. ANSSI-FR, DFIR-O365RC, Get-O365.ps1. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/Get-O365.ps1
30. Shams Zawoad, Ragib Hasan, John Grimes, "LINCS: Towards building a trustworthy litigation hold enabled cloud storage system", Digital Investigation 14 (2015) S55–S67, DFRWS 2015 USA. DOI 10.1016/j.diin.2015.05.014
31. Microsoft Azure Architecture Center, "Computer forensics chain of custody in Azure". https://learn.microsoft.com/en-us/azure/architecture/example-scenario/forensics/
