---
title: "조사 절차"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 620
---

# 조사 절차 (Investigation Process)

클라우드 조사는 기록이 남을 수 있었는지부터 확인하고, 사라지기 전에 로그를 떠 두고, 조사자 자신의 활동을 따로 적어 둔 뒤에 수집과 분석으로 넘어갑니다.

## 언제 쓰나

Microsoft 365·Google Workspace·AWS·Azure·Google Cloud·업무용 SaaS 에서 사고를 조사할 때 처음 며칠의 순서를 정하는 데 씁니다. 디스크 조사의 절차(증거 확보 → 이미징 → 분석 → 보고)는 [Windows 판 포렌식 조사 절차](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/process-acquisition/investigation-process.html)와 [Linux 판 조사 절차](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/investigation-process.html)에서 다루고, 계정 내보내기로 자료를 받는 경우는 [AI 판 조사 절차](https://urock-ailab.github.io/forensics-handbook/ai/03-techniques/acquisition/investigation-process.html)와 가깝습니다. 이 페이지는 클라우드라서 순서가 달라지는 부분만 다룹니다.

클라우드에서 순서가 달라지는 이유는 셋입니다. 첫째, 증거가 조사자 손이 닿지 않는 서비스 쪽에 있고 서비스가 정한 기간이 지나면 지워집니다. 둘째, 라이선스나 설정에 따라 처음부터 기록되지 않은 활동이 있습니다. 셋째, 조사자가 로그를 조회하고 스냅숏을 뜨는 동작도 같은 로그에 새 레코드로 남습니다. 단말만 봐서는 부족한 이유도 있습니다. 클라우드 드라이브는 일부만 기기에 동기화하고, 판(version)은 클라이언트에 하나만 남고, Google Docs 같은 클라우드 고유 개체 (cloud-native artifact) 는 웹 앱이 상태를 그때그때 내려받아 쓰기 때문에 로컬 저장소에 흔적이 남지 않습니다[4]. Google Docs 는 문서 상태를 사용자 편집 동작의 로그 형태로 유지하는 경우가 많아서, 한 시점의 사본만 뜨면 문서가 바뀌어 온 과정을 놓칩니다[4].

SaaS 조사는 Survey(살피기) → Preserve(보존) → Analyse(분석) → Integrate(합치기) → Interpret(해석) → Document(기록) 여섯 단계로 나눌 수 있습니다[1]. 아래 절차는 이 순서를 따르되, 앞의 두 단계를 클라우드 사정에 맞게 잘게 나눕니다. 증거 보관 연속성 (Chain of custody) 은 획득 (acquisition) · 보존 (preservation) · 접근 (access) 의 모든 단계에서 유지해야 하고, 증거 저장소는 접근 통제, 데이터 보호와 무결성, 모니터링과 경고, 로깅과 감사를 갖춰야 합니다[2].

## 절차

1. **조사 질문과 대상 범위를 정합니다.** 어느 테넌트·구독·계정·프로젝트를, 어느 기간에 대해, 누구의 권한으로 볼지 적습니다. 경계를 나누는 단위는 [테넌트·구독·계정·프로젝트](../../01-foundations/model/tenancy.md)에, 고객과 서비스 회사가 각각 무엇을 책임지는지는 [책임 공유와 조사 범위](../../01-foundations/model/shared-responsibility.md)에 있습니다. 조직이 스스로 받을 수 없는 자료가 필요하면 [서비스 회사에 대한 데이터 요청](legal-requests.md)을 이 단계에서 검토합니다. 서비스 회사의 협조가 없으면 적절한 사용자 자격 증명을 얻은 경우에 한해 사용자 쪽에서 온라인으로 수집하게 되고[3], 이 경로는 법적 권한을 먼저 확인합니다.

2. **기록이 남을 수 있었는지 확인합니다.** 설정이 꺼져 있던 기간에는 기록 자체가 없으므로, 로그를 받기 전에 아래 항목을 먼저 확인해 "없는 기록" 과 "받지 못한 기록" 을 나눕니다. 로그별 보관 기간은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 한 곳에만 정리했습니다.

   | 서비스 | 확인할 것 | 확인 방법·근거 |
   |---|---|---|
   | Microsoft 365 | 통합 감사 로그가 켜져 있었나 | Exchange Online PowerShell 에서 `Get-AdminAuditLogConfig \| Format-List UnifiedAuditLogIngestionEnabled`. Security & Compliance PowerShell 에서는 켜져 있어도 늘 `False` 로 나옵니다. Business Basic·Business Standard·Business Premium 과 엔터프라이즈 무료 체험을 쓰는 비관리 테넌트는 기본으로 꺼져 있습니다[5] |
   | Microsoft 365 | 언제 켰나 | 켜고 끈 기록은 `Search-UnifiedAuditLog -Operations Set-AdminAuditLogConfig` 로 찾고, AuditData 의 `UnifiedAuditLogIngestionEnabled` 값으로 켰는지 껐는지 봅니다. 켠 뒤 적용까지 60분까지 걸리고, 검색할 수 있게 되기까지 몇 시간이 걸릴 수 있습니다[5] |
   | Microsoft 365 | 라이선스와 감사 우회 | Microsoft-Extractor-Suite 의 `Get-LicenseCompatibility` 는 E5·E3 는 SKU 이름, P1·P2 는 서비스 플랜 이름(`AAD_PREMIUM`·`AAD_PREMIUM_P2`)으로 보유 여부를 판단합니다[12]. 사서함 감사 설정은 같은 도구의 `Get-MailboxAuditStatus`[13], Untitled Goose Tool 의 `Get-MailboxAuditBypassAssociation` 결과 파일 `EXO_MailboxAuditStatus_PowerShell.json` 으로 확인합니다[15] |
   | AWS | 트레일이 있었나, 조직 트레일인가 | 트레일이나 이벤트 데이터 스토어가 없으면 이벤트 기록 (Event history) 의 최근 90일 관리 이벤트뿐이고, 이벤트 기록은 계정 하나·리전 하나만 검색합니다[6]. 조직 트레일은 관리 계정과 모든 멤버 계정의 이벤트를 모읍니다[7] |
   | Azure | 진단 설정이 있었나 | 리소스 로그는 기본으로 수집되지 않고 리소스마다 진단 설정이 필요합니다[8]. 활동 로그는 90일 동안 두고 지웁니다[9] |
   | Google Cloud | 데이터 접근 감사 로그를 켰나 | BigQuery 를 빼면 기본으로 꺼져 있습니다(2026년 9월 문서 기준)[10] |
   | Google Workspace | 에디션 | BigQuery 로그 내보내기는 Frontline Standard·Plus, Enterprise Standard·Plus, Education Standard·Plus, Enterprise Essentials Plus 에서만 됩니다(2026년 9월 문서 기준)[11] |

   로그 종류별로 무엇이 기본으로 남는지는 [로그의 종류](../../01-foundations/logging/log-types.md)와 [기록은 어디에 남나](../../01-foundations/model/where-records-live.md)에서 다룹니다. 누군가 로그를 끄거나 지운 흔적은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)에서 찾습니다.

3. **조사자 활동을 적어 둘 기록부를 만듭니다.** 수집에 쓸 계정, 수집용 애플리케이션·서비스 주체의 이름과 ID, 조사용 AWS 계정 ID, 실행한 도구·명령과 시각(UTC)을 수집 전에 정하고 실행할 때마다 적습니다. 조사자의 동작이 조사 대상 로그에 공격자 활동과 같은 작업 이름으로 남기 때문입니다. 대표 경우는 아래 "조사자 활동이 남기는 기록" 표에 모았습니다. 아래는 기록부의 한 줄을 보인 만든 예시입니다.

   | 시각(UTC) | 수집 주체 | 대상 | 동작 | 결과 |
   |---|---|---|---|---|
   | 2026-09-02 01:20 | 앱 `IR-Collector` (앱 ID 11111111-2222-3333-4444-555555555555) | contoso.onmicrosoft.com | 통합 감사 로그 2026-03-01~2026-09-01 수집 시작 | 실행 로그 `ual-run.log` |

4. **격리·차단 조치와 수집 순서를 맞춥니다.** 계정 잠금이나 인스턴스 중지는 증거를 지우거나 조사자의 조회를 막을 수 있습니다. 조치마다 시각을 기록부에 적고, 지워질 증거는 조치 전에 확보합니다. 자세한 영향은 아래 "함정과 한계" 절에 있습니다.

5. **지금 있는 로그부터 떠 둡니다.** 새로 켠 설정이나 새로 만든 내보내기는 대부분 과거를 채우지 않으므로, 이미 있는 기록의 사본과 앞으로 쌓일 기록의 내보내기를 나눠 챙깁니다. 서비스별 방법은 [로그부터 지키기](log-preservation.md)에 있습니다.

6. **수집합니다.** Microsoft 365·Entra 는 [Microsoft 365 수집 도구](m365-collection.md), AWS·Azure·Google Cloud 의 제어 평면 로그는 [AWS·Azure·GCP 수집](iaas-collection.md), 가상 머신 디스크는 [클라우드 가상 머신 수집](vm-acquisition.md)을 따릅니다. 게스트 운영체제 안쪽의 메모리·파일 수집은 [Linux 판 클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html)과 [Linux 판 라이브 응답 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/live-response.html)에서 다룹니다.

7. **받은 사본의 해시와 받지 못한 구간을 기록합니다.** 해시 계산, CloudTrail 다이제스트 검증, 도구 실행 로그에서 누락 구간을 찾는 방법은 [클라우드 포렌식 보고서](../reporting/forensic-report.md)에 모았습니다.

8. **분석하고 보고합니다.** 여러 서비스의 로그를 한 시간축에 올리는 방법은 [클라우드 타임라인](../analysis/timeline.md), 탐지 규칙으로 걸러 내는 방법은 [탐지 규칙으로 로그 검색하기](../analysis/detection-rules.md)에 있습니다. 타임라인에서는 3단계 기록부의 주체·시각과 겹치는 레코드를 먼저 표시해 조사자 활동을 걸러 냅니다.

### 조사자 활동이 남기는 기록

| 조사자의 동작 | 남는 기록 | 근거 |
|---|---|---|
| DFIR-O365RC 2.0.0 이후 판으로 수집 | 수집 전에 `New-Application` 으로 Entra 애플리케이션을 만들고, 만들고 지울 때 높은 권한 계정으로 여러 번 로그인합니다[16]. 이 도구가 관심 작업으로 모으는 Entra 작업에도 `Add application`, `Add service principal`, `Add service principal credentials`, `Consent to application` 이 들어 있어서 조사자의 앱 등록이 같은 이름으로 잡힙니다[17] | [16][17] |
| Untitled Goose Tool 설정 | `Create_SP.ps1 -AppName GooseApp -Create` 로 서비스 주체를 만들고 `-Delete` 로 지웁니다[14] | [14] |
| Microsoft 365 eDiscovery 검색·PST 내보내기 | SigmaHQ 규칙이 `eventSource: SecurityComplianceCenter` 이면서 `eventName: 'eDiscovery search started or exported'`, `status: success` 인 기록[19], 또는 `eventSource: SecurityComplianceCenter` 이면서 Payload 에 `New-ComplianceSearchAction`·`Export`·`pst` 가 모두 든 기록[20]을 탐지합니다. DFIR-O365RC 의 관심 작업에도 `SearchCreated`·`SearchExported` 가 있습니다[17] | [17][19][20] |
| Invictus-AWS 로 수집 | 결과를 내려받는 옵션을 주지 않으면 조사하는 리전에 결과용 S3 버킷을 만들어(`create_s3_if_not_exists`) 결과를 씁니다[18] | [18] |
| AWS 스냅숏을 조사용 계정에 공유 | `eventSource: ec2.amazonaws.com`, `eventName: ModifySnapshotAttribute` 는 SigmaHQ 가 스냅숏 유출 규칙으로 탐지합니다[21]. 공유받은 쪽이 복사하거나 볼륨을 만들면 소유 계정 CloudTrail 에 `SharedSnapshotCopyInitiated`·`SharedSnapshotVolumeCreated` 가 남습니다[22] | [21][22] |
| AWS 에서 스냅숏을 여러 개 생성 | GuardDuty `Exfiltration:IAMUser/AnomalousBehavior`(기본 심각도 High)는 `CreateSnapshot` 같은 관리 API 호출이 평소와 다를 때 생깁니다[23]. 조사자의 대량 스냅숏도 이 결과를 부를 가능성이 있습니다 | [23] |
| Azure 디스크 사본·명령 실행 | 디스크 SAS 발급은 `Microsoft.Compute/disks/beginGetAccess/action`, 철회는 `Microsoft.Compute/disks/endGetAccess/action`, 스냅숏 생성·수정은 `Microsoft.Compute/snapshots/write`, 스냅숏 SAS 발급은 `Microsoft.Compute/snapshots/beginGetAccess/action`, 게스트 명령 실행은 `Microsoft.Compute/virtualMachines/runCommand/action` 권한에 해당합니다[24]. Azure 감사 로그는 누가 언제 스냅숏을 떴는지 남깁니다[2] | [2][24] |
| Google Cloud 스냅숏·이미지·직렬 포트 | `v1.compute.disks.createSnapshot`·`v1.compute.snapshots.insert`·`v1.compute.images.insert` 는 ADMIN_WRITE 라서 관리 활동 감사 로그에 남고, `v1.compute.instances.getSerialPortOutput` 은 DATA_READ 라서 데이터 접근 감사 로그를 켠 경우에만 남습니다[10][25] | [10][25] |

Azure 는 위 권한 이름이 활동 로그의 작업 이름에 어떤 문자열로 나타나는지 실제 데이터로 확인한 뒤 걸러 냅니다.

## 도구

| 대상 | 공개 도구 | 조사 절차에서 쓰는 곳 |
|---|---|---|
| Microsoft 365·Entra·Azure | Microsoft-Extractor-Suite[32], Untitled Goose Tool[14], DFIR-O365RC[16], Hawk[31] | 2단계 설정 확인, 6단계 수집. 자세한 동작은 [Microsoft 365 수집 도구](m365-collection.md) |
| Google Workspace | ALFA: `alfa acquire` 로 감사 로그를 받고 `--start-time`·`--end-time` 에 RFC 3339 시각을 줍니다[30] | 6단계 수집 |
| AWS | Invictus-AWS[18] | 6단계 수집. 한계는 [AWS·Azure·GCP 수집](iaas-collection.md) |
| 여러 서비스 | SigmaHQ 규칙[19][20][21] | 8단계 분석. [탐지 규칙으로 로그 검색하기](../analysis/detection-rules.md) |

어느 도구든 서비스 API 가 돌려준 범위만 받습니다. 도구마다 기본 기간과 상한이 달라서 한 도구의 결과로 "없음" 을 판단하지 않고, 실행 로그를 함께 보관합니다.

## 함정과 한계

- **자격 증명 격리 정책이 조사를 막습니다.** AWS 는 IAM 사용자 자격 증명이 노출되면 관리형 정책 `AWSCompromisedKeyQuarantineV3` 를 붙이고, 이 정책의 거부 목록에 `cloudtrail:LookupEvents`·`ec2:RunInstances`·`iam:CreateAccessKey` 등이 들어 있습니다(정책 수정 시각 2026-03-16 16:27 UTC)[26]. 이 정책이 붙은 자격 증명으로는 이벤트 기록을 조회할 수 없으므로 별도 조사용 자격 증명을 씁니다. 이 정책은 떼지 말고 AWS 가 연 지원 사례의 안내를 따르도록 되어 있습니다[26].
- **세션 취소 뒤의 거부 오류.** IAM 역할의 세션을 취소하면 `AWSRevokeOlderSessions` 인라인 정책이 붙어 지정 시각 전에 발급된 임시 자격 증명이 모두 무효가 되고, 그 역할을 쓰는 모든 사용자에게 적용되며 저장하지 않은 작업을 잃을 수 있습니다[27]. 취소 시각을 적어 두지 않으면 그 뒤에 쏟아지는 접근 거부 기록을 공격자 활동으로 잘못 읽을 가능성이 있습니다.
- **멈추면 사라지는 저장소.** EC2 인스턴스 스토어 볼륨의 데이터는 인스턴스를 중지·최대 절전·종료하면 블록이 암호학적으로 지워지고, 재부팅에서는 남습니다[28]. 인스턴스 스토어가 붙은 인스턴스는 멈추기 전에 게스트 안에서 먼저 수집합니다.
- **SAS 가 열려 있으면 VM 이 켜지지 않습니다.** Azure 디스크의 SAS URL 이 활성인 동안 VM 을 시작하면 `There is an active shared access signature outstanding for disk diskname` 오류가 납니다[29]. 복구 담당과 일정을 맞추고, SAS 를 발급·철회한 시각을 기록부에 적습니다.
- **조사자의 조치가 경고를 일으킵니다.** eDiscovery 내보내기[19][20], 스냅숏 공유[21], 대량 스냅숏[23]은 탐지 규칙과 같은 작업이라서 보안 운영 쪽에 알리지 않으면 새 사고로 처리될 수 있습니다.
- **대상 환경에 자원을 만드는 도구.** 수집용 앱·서비스 주체[14][16], 결과용 버킷[18]은 대상 환경에 남습니다. 수집이 끝나면 지웠는지와 지운 시각까지 기록부에 적습니다.
- **단말 흔적만으로는 부족합니다.** 부분 동기화, 클라이언트에 하나만 남는 판, 로컬 저장소에 흔적이 없는 클라우드 고유 개체 때문에 단말 분석은 서비스 쪽 기록과 함께 봐야 합니다[4].

## 결과를 어떻게 해석하나

**증명하는 것.** 수집한 레코드는 "그 서비스가 그 시각(UTC)에 그 주체로 그 작업을 기록했다" 까지를 보여 줍니다. 조사자 기록부와 해시 목록이 있으면 수집한 사본이 언제 어떤 경로로 만들어졌는지도 보일 수 있습니다. Azure 감사 로그는 스냅숏을 뜬 주체와 시각을 남기고, 해시 값은 사본의 무결성을 확인하는 데 씁니다[2].

**증명하지 못하는 것.** 계정이나 자격 증명을 실제로 쓴 사람은 기록만으로 특정하지 못합니다. 기록이 없는 구간도 활동이 없었다는 뜻이 아닙니다. 설정이 꺼져 있었거나(2단계), 보관 기간이 지났거나, 도구가 상한에 걸려 일부만 받았을 수 있습니다. 조사자 활동과 공격자 활동도 3단계 기록부가 없으면 구분하기 어렵습니다. 같은 작업 이름(`Add service principal`, `ModifySnapshotAttribute` 등)으로 남기 때문입니다.

보고서의 수집 부분에 무엇을 채울지, 결론 문장을 어떻게 쓸지는 [클라우드 포렌식 보고서](../reporting/forensic-report.md)에 있습니다. 조사자 활동은 다음처럼 따로 적습니다. 아래 값은 모두 만든 예시입니다.

- "2026-09-02 01:20 UTC 에 조사자가 만든 앱 `IR-Collector` 의 서비스 주체 생성 기록(`Add service principal`)은 조사 활동이므로 분석에서 제외했다."

## 참고 문헌

1. Eoghan Casey, "SaaS Forensics & Response: Forensic Preservation, Recovery, and Analysis of SaaS Data", DFRWS USA 2023 발표. https://dfrws.org/presentation/saas-forensics-and-response/
2. Microsoft, "Computer forensics chain of custody in Azure", Azure Architecture Center. https://learn.microsoft.com/en-us/azure/architecture/example-scenario/forensics/
3. Jihyeok Yang, Jieon Kim, Jewan Bang, Sangjin Lee, Jungheum Park, "CATCH: Cloud Data Acquisition through Comprehensive and Hybrid Approaches", Forensic Science International: Digital Investigation 43 (2022) 301442. DOI 10.1016/j.fsidi.2022.301442
4. Vassil Roussev, Shane McCulley, "Forensic Analysis of Cloud-Native Artifacts", DFRWS EU 2016 발표. https://dfrws.org/presentation/forensic-analysis-of-cloud-native-artifacts/
5. Microsoft, "Turn auditing on or off", Microsoft Learn (Last updated 2026-06-19). https://learn.microsoft.com/en-us/purview/audit-log-enable-disable
6. AWS, "Working with CloudTrail event history". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
7. AWS, "Creating a trail for an organization". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/creating-trail-organization.html
8. MicrosoftDocs, "Resource logs in Azure Monitor" (ms.date 2025-07-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/logs/resource-logs.md
9. MicrosoftDocs, "Activity Log in Azure Monitor" (ms.date 2026-05-04). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
10. Google Cloud, "Best practices for Cloud Audit Logs" (Last updated 2026-09-25). https://cloud.google.com/logging/docs/audit/best-practices
11. Google, "About reporting logs and BigQuery", Google Workspace Admin Help (Last updated 2026-09-18). https://knowledge.workspace.google.com/admin/reports/about-reporting-logs-and-bigquery
12. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-ProductLicenses.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-ProductLicenses.ps1
13. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-AuditLogSettings.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AuditLogSettings.ps1
14. CISA, Untitled Goose Tool, README. https://github.com/cisagov/untitledgoosetool/blob/develop/README.md
15. CISA, Untitled Goose Tool, `goosey/m365_datadumper.py`. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/m365_datadumper.py
16. ANSSI, DFIR-O365RC, README. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/README.md
17. ANSSI, DFIR-O365RC, `DFIR-O365RC/Get-O365.ps1`. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/Get-O365.ps1
18. Invictus IR, Invictus-AWS, `source/main/logs.py`. https://github.com/invictus-ir/Invictus-AWS
19. SigmaHQ, "PST Export Alert Using eDiscovery Alert", `rules/cloud/m365/threat_management/microsoft365_pst_export_alert.yml`. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/threat_management/microsoft365_pst_export_alert.yml
20. SigmaHQ, "PST Export Alert Using New-ComplianceSearchAction", `rules/cloud/m365/threat_management/microsoft365_pst_export_alert_using_new_compliancesearchaction.yml`. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/threat_management/microsoft365_pst_export_alert_using_new_compliancesearchaction.yml
21. SigmaHQ, "AWS Snapshot Backup Exfiltration", `rules/cloud/aws/cloudtrail/aws_snapshot_backup_exfiltration.yml`. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/aws/cloudtrail/aws_snapshot_backup_exfiltration.yml
22. AWS, "Share an Amazon EBS snapshot". https://docs.aws.amazon.com/ebs/latest/userguide/ebs-modifying-snapshot-permissions.html
23. AWS, "GuardDuty IAM finding types". https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-iam.html
24. Microsoft, "Azure permissions for Compute", Microsoft Learn. https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/compute
25. Google Cloud, "Compute Engine audit logging" (Last updated 2026-09-24). https://cloud.google.com/compute/docs/logging/audit-logging
26. AWS, "AWSCompromisedKeyQuarantineV3", AWS Managed Policy Reference. https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSCompromisedKeyQuarantineV3.html
27. AWS, "Revoke IAM role temporary security credentials". https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_revoke-sessions.html
28. AWS, "Data persistence for Amazon EC2 instance store volumes". https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-store-lifetime.html
29. Microsoft, "Download a Windows VHD from Azure", Microsoft Learn (Last updated 2026-09-03). https://learn.microsoft.com/en-us/azure/virtual-machines/windows/download-vhd
30. Invictus IR, ALFA, README. https://github.com/invictus-ir/ALFA/blob/main/README.md
31. T0pCyber, Hawk, README. https://github.com/T0pCyber/hawk/blob/master/README.md
32. Invictus IR, Microsoft-Extractor-Suite, README. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/README.md
