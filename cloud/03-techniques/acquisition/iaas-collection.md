---
title: "AWS·Azure·GCP 수집"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 650
---

# AWS·Azure·GCP 수집 (Cloud Log Collection)

AWS·Azure·Google Cloud 의 관리 기록을 모을 때는 설정 없이 조회되는 기본 보관분과 조직이 미리 쌓아 둔 저장소를 모두 받고, 계정·리전·구독·프로젝트마다 빠진 곳이 없는지 확인한 뒤 수집 계정과 시각을 적어 둡니다.

## 언제 쓰나

IaaS 에서 계정 탈취, 키 유출, 자원 생성·삭제, 로그 끄기가 의심될 때 제어 평면 (control plane) 기록을 확보하는 단계에서 씁니다. AWS 와 Azure 는 설정하지 않아도 최근 90일의 관리 기록을 조회할 수 있고[1][9], Google Cloud 는 기록이 생긴 프로젝트·폴더·조직의 로그 버킷에 보관 기간 동안 남습니다[16]. 보관 기간이 지난 기록은 날마다 사라지므로 조사를 시작하면 이 기본 보관분부터 받습니다. 그보다 오래된 기록과 데이터 평면 (data plane) 기록은 조직이 사고 전에 트레일·진단 설정·싱크를 만들거나 해당 로그를 켜 두었을 때만 있습니다[3][10][16][17].

지금 있는 로그를 먼저 떠 두고 앞으로 쌓일 로그를 보내는 방법은 [로그부터 지키기](./log-preservation.md), Microsoft 365 와 Entra ID 로그는 [Microsoft 365 수집 도구](./m365-collection.md), 가상 머신 디스크는 [클라우드 가상 머신 수집](./vm-acquisition.md)에서 다룹니다. 보관 기간은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 한 곳에 모아 두었습니다.

## 서비스별로 받을 곳

| 항목 | AWS | Azure | Google Cloud |
|---|---|---|---|
| 설정 없이 조회되는 관리 기록 | 이벤트 기록 (Event history): 계정·리전마다 최근 90일 관리 이벤트[1] | 활동 로그 (Activity log): 90일 보관 후 삭제[9] | 기록이 생긴 프로젝트·폴더·조직의 로그 버킷[16] |
| 오래된 기록이 있을 수 있는 곳 | 트레일 S3 버킷[3], CloudTrail Lake[22] | 진단 설정 목적지(Storage·Log Analytics·Event Hubs)[9][10] | 싱크 목적지(Cloud Storage·BigQuery·Pub/Sub), 사용자 정의 로그 버킷[16] |
| 기본으로 없는 기록 | 데이터 이벤트·Insights·네트워크 활동 이벤트는 이벤트 기록에 없음[1] | 리소스 로그는 리소스마다 진단 설정을 만들어야 수집[11] | BigQuery 말고는 데이터 접근 감사 로그가 기본으로 꺼져 있음[17](→ [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md)) |
| 저장소에 쌓인 파일 단위 | 게시 날짜 폴더 아래 `json.gz`[3] | 한 시간 단위 `PT1H.json`[9] | 한 시간 단위 샤드 JSON[18] |
| 파일 경로 시각의 기준 | 로그 파일을 게시한 날짜[3] | 이벤트를 받은 시각[9] | `timestamp` 기준, 늦게 온 항목은 부록 샤드[18] |
| 지난 기록을 나중에 옮기는 방법 | 트레일 이벤트를 Lake 이벤트 데이터 저장소로 복사(Lake 는 2026-05-31 부터 신규 고객 불가)[22] | 진단 설정은 만든 뒤 90분 안에 흐르기 시작함[10]. 90일 안의 기록은 REST·CLI 로 받아 둠[9] | 로그 버킷에서 Cloud Storage 로 복사[16][17] |

위 값은 2026년 9월 문서 기준입니다. 각 저장소의 경로 모양과 레코드 필드는 [트레일과 이벤트 기록](../../02-artifacts/aws/cloudtrail/trails.md), [활동 로그](../../02-artifacts/azure/activity-log.md), [리소스 로그와 진단 설정](../../02-artifacts/azure/resource-logs.md), [Cloud Audit Logs](../../02-artifacts/gcp/cloud-audit-logs.md)에서 다룹니다.

## 절차

1. **수집 계정과 시작 시각을 적습니다.** 조사용 자격 증명(IAM 역할, 서비스 주체, 서비스 계정)의 이름·ID 와 수집을 시작한 UTC 시각을 기록합니다. 수집 도구의 API 호출과 도구가 만드는 자원도 대상 로그에 새 레코드로 남기 때문입니다. 예를 들어 Invictus-AWS 는 결과를 내려받는 옵션을 쓰지 않으면 조사 대상 리전에 결과용 S3 버킷을 만들어 거기에 씁니다[8]. 키 유출 대응으로 `AWSCompromisedKeyQuarantineV3` 정책이 붙은 자격 증명은 `cloudtrail:LookupEvents` 가 거부되므로 수집에 쓸 수 없습니다[7].

2. **범위를 목록으로 만듭니다.** AWS 는 계정과 켜져 있는 리전, Azure 는 테넌트·관리 그룹·구독, Google Cloud 는 조직·폴더·프로젝트를 모두 나열합니다. 계층 구조는 [테넌트·구독·계정·프로젝트](../../01-foundations/model/tenancy.md)에서 다룹니다. AWS 이벤트 기록은 한 번에 한 계정·한 리전만 검색하므로[1], 리전 목록이 곧 조회 횟수가 됩니다. Azure 활동 로그는 구독 수준 말고도 테넌트 수준 이벤트(관리 그룹·구독 생성 같은 작업)가 따로 있어 API 를 달리 불러야 합니다[9]. Google Cloud 는 기록이 생긴 프로젝트·폴더·조직의 버킷에 저장되므로[16], 프로젝트만 읽으면 조직·폴더 수준 기록이 빠집니다.

3. **설정 없이 조회되는 기본 보관분을 먼저 받습니다.** 보관 기간이 지난 기록은 날마다 사라집니다.
   - AWS: 리전마다 `LookupEvents` 로 받습니다. 한 번에 최대 50건을 돌려주고 나머지는 `NextToken` 으로 이어 받으며, 계정·리전마다 초당 2회를 넘으면 스로틀링 오류가 납니다[2]. 콘솔에서 내려받으면 파일 하나에 200,000건까지 들어갑니다[1].
   - Azure: 구독마다 `az monitor activity-log list` 나 REST 로 받습니다. REST 의 `$filter` 에는 `eventTimestamp` 시작값이 반드시 있어야 하고 시작과 끝이 모두 90일 안에 있어야 합니다[9].
   - Google Cloud: `gcloud logging read` 에 시각 조건을 넣어 프로젝트·폴더·조직마다 받습니다[19][21].

   ```bash
   # 만든 예시: 구독 ID·시각은 지어낸 값
   az monitor activity-log list \
     --subscription "00000000-0000-0000-0000-000000000000" \
     --start-time "2026-07-01T00:00:00Z" --end-time "2026-09-26T00:00:00Z"

   # 만든 예시: 시각 조건을 넣지 않으면 최근 1일만 읽는다
   gcloud logging read 'timestamp>="2026-07-01T00:00:00Z" AND timestamp<"2026-09-26T00:00:00Z"' \
     --organization=123456789012 --order=asc --format=json
   ```

4. **조직이 쌓아 둔 저장소를 찾아 통째로 복사합니다.**
   - AWS: 트레일 설정에서 버킷과 접두사를 확인하고 `AWSLogs` 아래 폴더를 모두 받습니다. 관리·데이터 이벤트(`CloudTrail`) 말고도 `CloudTrail-Insight`·`CloudTrail-NetworkActivity`·`CloudTrail-Aggregated` 폴더가 따로 있습니다[3]. 조직 트레일은 관리 계정과 모든 멤버 계정의 이벤트를 모으므로[4], 멤버 계정을 조사할 때도 조직 관리 계정 쪽 버킷을 확인합니다. 다이제스트 파일도 함께 받아 두면 전달 뒤 변경 여부를 검증할 수 있습니다(→ [트레일과 이벤트 기록](../../02-artifacts/aws/cloudtrail/trails.md)).
   - Azure: 구독·관리 그룹·리소스의 진단 설정 목록에서 목적지를 확인하고, Storage 목적지는 `insights-activity-logs`·`insights-logs-{범주}` 컨테이너를 받습니다[9][11]. 리소스마다 진단 설정은 최대 5개라서[10] 한 리소스의 로그가 여러 목적지에 나뉘어 있을 수 있습니다.
   - Google Cloud: 싱크 목록에서 목적지를 확인합니다. 가로채기 집계 싱크 (intercepting aggregated sink) 의 필터에 맞은 항목은 그 싱크의 목적지로 가고, 기록이 생긴 프로젝트에서는 `_Required` 싱크로만 가서 그 프로젝트의 다른 싱크(`_Default` 포함)로는 가지 않습니다[16]. 로그 버킷에 남아 있는 항목은 Cloud Storage 로 복사해 과거분을 옮길 수 있고, 복사해도 원래 버킷에 그대로 남습니다[16][17]. Logs Explorer 다운로드는 10,000건까지라서 그보다 많으면 싱크나 Cloud Storage 복사로 받습니다[16].

5. **탐지 결과처럼 보관 기간이 짧은 자료를 함께 받습니다.** GuardDuty 결과는 90일 보관입니다[6]. 결과 형식은 [GuardDuty](../../02-artifacts/aws/guardduty.md)에서 다룹니다.

6. **빠진 곳을 점검합니다.** 리전·구독·프로젝트별 건수와 받은 기간의 처음·끝 시각을 표로 만들어, 0건이거나 기간이 짧은 곳을 다시 조회합니다. 스로틀링이나 HTTP 오류가 난 구간은 도구 로그에서 찾아 다시 받습니다.

7. **해시를 뜨고 기록합니다.** 받은 파일마다 해시를 계산하고, 수집 계정·명령·기간·건수와 함께 적습니다. 보고서에 남길 항목은 [클라우드 포렌식 보고서](../reporting/forensic-report.md)에 있습니다.

## 도구

| 도구 | 대상 | 받는 방식 | 알아 둘 점 |
|---|---|---|---|
| Invictus-AWS | AWS | CloudTrail 은 `lookup_events` 로 이벤트 기록을 페이지마다 받아 `{eventID}.json` 파일로 저장. S3·CloudTrail 은 첫 리전 한 곳에서만, 나머지 서비스(WAFv2·VPC·Elastic Beanstalk·Route 53·RDS·CloudWatch·GuardDuty·Inspector2·Macie2)는 리전마다[8] | 트레일 버킷을 읽는 코드는 주석 처리됨. 시작·끝을 연-월-일로만 받음. VPC 흐름 로그는 내용이 아니라 목적지 버킷 이름만 모음[8] |
| Microsoft-Extractor-Suite `Get-ActivityLogs` | Azure 구독 활동 로그 | `Microsoft.Insights/eventtypes/management/values`(api-version 2015-04-01)를 `eventTimestamp` 필터로 호출. 기본 기간은 오늘부터 89일 전~지금, 기본은 모든 구독[12] | 테넌트 수준 이벤트는 `Get-DirectoryActivityLogs` 가 따로 받음(기본 90일)[12] |
| Untitled Goose Tool | Azure 구독 활동 로그·진단 설정 | 구독마다 하루 단위로 `azure_activity_log_날짜.json` 을 쓰고 상태 파일로 이어 받기. 기본 기간은 89일 전 0시~오늘 0시(UTC)[14] | 필요한 역할: `Reader`, `Storage Blob Data Reader`, `Storage Queue Data Reader`[13] |
| DFIR-O365RC `Get-AzRMActivityLogs` | Azure 구독 활동 로그 | 고른 구독의 활동 로그 전체, 90일[15] | 구독에 `Microsoft.Insights/eventtypes/*` 를 읽는 `Reader` 역할 필요[15] |
| libcloudforensics `GoogleCloudLog` | Google Cloud | 프로젝트마다 `entries.list` 를 `resourceNames: projects/ID`, `orderBy: timestamp desc` 로 호출[20] | 프로젝트 단위라서 폴더·조직 수준 기록은 따로 받아야 함[16][20] |

도구가 만든 파일은 원래 형식을 바꾼 것일 수 있습니다. Invictus-AWS 는 `LookupEvents` 응답의 `CloudTrailEvent` 문자열만 풀어 저장하므로 트레일 파일과 필드 구성이 같은지 확인해야 하고[8], Goose 는 SDK 객체를 사전으로 바꿔 한 줄에 하나씩 씁니다[14]. 원래 응답이나 원본 파일을 함께 보관하면 도구 변환 문제를 나중에 가려낼 수 있습니다.

## 함정과 한계

- **이벤트 기록 기반 수집은 좁습니다.** 이벤트 기록과 `LookupEvents` 는 한 리전의 최근 90일 관리 이벤트(`LookupEvents` 는 Insights 이벤트 포함)만 돌려주므로 데이터 이벤트와 다른 리전 활동은 이 경로로 받을 수 없습니다[1][2]. Invictus-AWS 는 CloudTrail 을 첫 리전에서만 조회하므로[8], 다른 리전의 관리 이벤트는 따로 받아야 합니다. 글로벌 서비스 이벤트와 콘솔 로그인이 남는 리전은 [트레일과 이벤트 기록](../../02-artifacts/aws/cloudtrail/trails.md)에 정리되어 있습니다.
- **기간 끝이 날짜로 잘립니다.** `LookupEvents` 의 `EndTime` 은 그 시각 이전(같은 시각 포함) 이벤트만 돌려주는데[2], Invictus-AWS 는 끝 날짜를 그날 0시로 넘깁니다[8]. Goose 도 기본 끝을 오늘 0시(UTC)로 잡습니다[14]. 두 도구 모두 끝 날짜 당일의 이벤트가 빠질 수 있으니 하루 뒤를 끝으로 줍니다.
- **`gcloud logging read` 기본값은 하루치입니다.** `--freshness` 기본값이 `1d` 이고 내림차순·시각 조건 없는 필터에서만 적용되므로[19], 필터에 `timestamp` 조건을 넣습니다[21]. 기본 순서도 최신 먼저(`desc`)입니다[19].
- **파일 경로로 기간을 자르면 늦게 온 기록이 빠집니다.** CloudTrail 날짜 폴더는 로그 파일을 게시한 날짜이고[3], Azure `PT1H.json` 은 그 시간에 받은 이벤트를 생성 시각과 상관없이 덧붙이며[9], Google Cloud 는 `timestamp` 와 `receiveTimestamp` 가 다른 시간 창이면 부록 샤드로 보냅니다[18]. 사건 기간보다 앞뒤로 넉넉히 받은 뒤 레코드 안의 시각으로 다시 거릅니다. 시각 필드 비교는 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에서 다룹니다.
- **파일 안 순서를 믿지 않습니다.** CloudTrail 로그 파일은 API 호출을 순서대로 쌓은 기록이 아니고[5], Google Cloud 샤드 파일 안의 정렬도 보장되지 않습니다[18]. 합친 뒤 시각으로 정렬합니다.
- **같은 이벤트가 여러 번 들어옵니다.** Azure 는 관리 그룹과 하위 구독에 모두 진단 설정이 있으면 이벤트가 중복되고, 테넌트 수준 이벤트에도 리소스 관리 이벤트가 겹칠 수 있습니다[9]. Google Cloud 는 필터가 겹치는 싱크가 여럿이면 같은 항목을 여러 번 씁니다[18]. 건수를 셀 때는 모든 필드의 해시로 같은 레코드를 가려 중복을 걷어 냅니다[9].
- **보존 조치는 과거를 채우지 않습니다.** Azure 진단 설정은 만든 뒤 90분 안에 흐르기 시작하고[10], Google Cloud 싱크는 만들기 전에 받은 항목을 보내지 않습니다[16]. 조사 중에 만든 설정의 목적지에는 설정 이전 기록이 없습니다.
- **리소스 로그는 완전하지 않을 수 있습니다.** Azure 리소스 로그는 저장 후 전달 구조라서 트랜잭션 보장이 없고 작은 손실이 생길 수 있습니다[11].
- **조사자의 호출도 기록입니다.** 수집 도구가 만든 S3 버킷, 서비스 주체, 조회 호출은 대상 로그에 남습니다[8][13]. 수집 계정·시각을 적어 두지 않으면 타임라인에서 공격자 활동과 섞입니다.

## 결과를 어떻게 해석하나

**증명하는 것.** 받은 관리 기록은 그 서비스가 해당 UTC 시각에 해당 주체의 제어 평면 호출을 기록했다는 사실을 보여 줍니다. 트레일 다이제스트나 수집 직후 계산한 해시가 있으면 수집 이후 파일이 바뀌지 않았음을 보일 수 있습니다. Azure 활동 로그는 자원을 만든 사람이 남는 유일한 곳이라서[9] 자원 생성 주체를 밝히는 근거가 됩니다.

**증명하지 못하는 것.** 켜지 않은 로그 범주(데이터 이벤트, 진단 설정이 없는 리소스 로그, 기본으로 꺼진 데이터 접근 감사 로그)의 활동, 조회하지 않은 리전·구독·프로젝트·조직 수준의 활동, 기본 보관 기간과 보존 조치 사이 틈의 활동은 이 자료로 판단할 수 없습니다. 따라서 "해당 기간에 활동이 없었다" 가 아니라 "수집한 범위(계정·리전·기간 명시)에서 해당 작업 기록이 없다" 로 씁니다. 자격 증명을 실제로 쓴 사람이 누구인지도 이 기록만으로는 알 수 없습니다.

모은 기록을 합쳐 읽는 방법은 [클라우드 타임라인](../analysis/timeline.md), 로그를 끄거나 지운 흔적은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)에서 다룹니다. 가상 머신 안쪽 수집은 Linux 판의 [클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html)과 [라이브 응답 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/live-response.html)을 봅니다.

## 참고 문헌

1. AWS, "Working with CloudTrail event history", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
2. AWS, "LookupEvents", AWS CloudTrail API Reference. https://docs.aws.amazon.com/awscloudtrail/latest/APIReference/API_LookupEvents.html
3. AWS, "Getting and viewing your CloudTrail log files", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/get-and-view-cloudtrail-log-files.html
4. AWS, "Creating a trail for an organization", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/creating-trail-organization.html
5. AWS, "Log EBS direct APIs calls using AWS CloudTrail", Amazon EBS User Guide. https://docs.aws.amazon.com/ebs/latest/userguide/logging-ebs-apis-using-cloudtrail.html
6. AWS, "Exporting generated GuardDuty findings to Amazon S3 buckets", Amazon GuardDuty User Guide. https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_exportfindings.html
7. AWS, "AWSCompromisedKeyQuarantineV3", AWS Managed Policy Reference. https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSCompromisedKeyQuarantineV3.html
8. Invictus Incident Response, Invictus-AWS, source/main/logs.py. https://github.com/invictus-ir/Invictus-AWS/blob/main/source/main/logs.py
9. Microsoft, "Activity Log in Azure Monitor", azure-monitor-docs (ms.date 2026-05-04). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
10. Microsoft, "Diagnostic Settings in Azure Monitor", azure-monitor-docs (ms.date 2026-03-31). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/data-collection/diagnostic-settings.md
11. Microsoft, "Resource logs in Azure Monitor", azure-monitor-docs (ms.date 2025-07-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs.md
12. Invictus Incident Response, Microsoft-Extractor-Suite, Get-AzureActivityLogs.ps1·Get-AzureDirectoryActivityLogs.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureActivityLogs.ps1 , https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureDirectoryActivityLogs.ps1
13. CISA, Untitled Goose Tool, README.md. https://github.com/cisagov/untitledgoosetool/blob/develop/README.md
14. CISA, Untitled Goose Tool, goosey/azure_dumper.py. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/azure_dumper.py
15. ANSSI-FR, DFIR-O365RC, README.md. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/README.md
16. Google Cloud, "Route log entries", Cloud Logging 문서(2026-09-25 갱신). https://cloud.google.com/logging/docs/routing/overview
17. Google Cloud, "Best practices for Cloud Audit Logs", Cloud Logging 문서(2026-09-25 갱신). https://cloud.google.com/logging/docs/audit/best-practices
18. Google Cloud, "View logs routed to Cloud Storage", Cloud Logging 문서(2026-09-25 갱신). https://cloud.google.com/logging/docs/export/storage
19. Google Cloud, "gcloud logging read", Google Cloud SDK Reference(2026-09-15 갱신). https://cloud.google.com/sdk/gcloud/reference/logging/read
20. Google, cloud-forensics-utils(libcloudforensics), providers/gcp/internal/log.py. https://github.com/google/cloud-forensics-utils/blob/main/libcloudforensics/providers/gcp/internal/log.py
21. Google Cloud, "Logging query language", Cloud Logging 문서(2026-09-25 갱신). https://cloud.google.com/logging/docs/view/logging-query-language
22. AWS, "Working with AWS CloudTrail Lake", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake.html
