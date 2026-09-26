---
title: "클라우드 포렌식 보고서"
parent: "기법 · 보고"
nav_order: 720
---

# 클라우드 포렌식 보고서 (Forensic Report)

클라우드 조사 보고서는 찾은 사실 앞에 어느 로그를 어느 기간·어느 라이선스 조건에서 받았는지, 받은 사본이 원본과 같다는 근거, 받지 못한 구간, 시각 기준을 먼저 적습니다.

보고서의 뼈대(사건 개요·수집·분석·결론·부록)와 문장을 쓰는 일반 원칙은 디스크 조사와 같아서 [Windows 판 분석 보고서 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/reporting/forensic-report.html)과 [Linux 판 포렌식 보고서](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/reporting/forensic-report.html)에서 다룹니다. SaaS 내보내기와 감사 로그를 근거로 쓰는 보고서는 [AI 판 포렌식 보고서](https://urock-ailab.github.io/forensics-handbook/ai/03-techniques/reporting/forensic-report.html)와 가깝습니다. 이 페이지는 클라우드 로그가 디스크 이미지와 다른 점 때문에 보고서에 더 적어야 하는 것만 다룹니다.

## 언제 쓰나

Microsoft 365·Google Workspace·AWS·Azure·Google Cloud·업무용 SaaS 의 감사 로그를 근거로 결론을 내는 모든 조사에 씁니다. 디스크 이미지는 수집한 순간의 상태가 통째로 남지만, 클라우드 로그는 서비스가 정한 기간이 지나면 사라지고 라이선스·설정에 따라 처음부터 남지 않은 기록도 있습니다. 그래서 같은 사건이라도 언제, 어느 권한으로, 어느 경로로 받았느냐에 따라 사본의 범위가 달라지고, 보고서는 이 범위를 밝혀야 읽는 사람이 "기록 없음" 을 제대로 해석할 수 있습니다.

## 절차

1. **수집 권한과 범위를 적습니다.** 어느 테넌트·구독·계정·프로젝트를 누구의 권한으로 조회했는지 씁니다. Purview 포털에서 관리 단위 (Administrative unit) 가 배정된 제한 관리자는 그 범위 사용자의 로그만 검색·내보내기 할 수 있고, 사용자가 아닌 주체와 시스템 계정의 로그는 제한 없는 관리자만 볼 수 있습니다[3]. 공급자 협조 없이 사용자 자격 증명으로 받을 때, 공개 API (Open API) 를 쓰는 도구는 서비스 회사가 정한 영역에만 접근해서 중요한 증거를 놓칠 수 있으므로 어느 API 로 받았는지도 적습니다[35]. 고객과 공급자가 무엇을 책임지는지는 [책임 공유와 조사 범위](../../01-foundations/model/shared-responsibility.md)에서 다룹니다.

2. **조사할 수 있는 기간을 문서 값으로 적습니다.** 로그마다 보관 기간이 다르고 라이선스와 설정에 따라 바뀝니다. 아래 표는 2026년 9월 문서 기준이고, 자세한 조건은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에 있습니다.

   | 서비스·로그 | 보관 기간 | 조건 |
   |---|---|---|
   | Microsoft 365 통합 감사 로그, Audit (Standard) | 180일 | 2023년 10월 17일 이전에 생긴 기록은 90일[1] |
   | 통합 감사 로그, Audit (Premium) 기본 정책 | 1년 | `Workload` 가 `AzureActiveDirectory`·`Exchange`·`OneDrive`·`SharePoint` 이고 활동한 사용자에게 E5 계열 라이선스가 있을 때. E5 가 없는 사용자와 게스트는 180일[1] |
   | 통합 감사 로그, 사용자가 아닌 주체 | 1년 고정 | 서비스 주체·시스템·앱 활동. 사용자 지정 보존 정책이 적용되지 않음[2] |
   | 통합 감사 로그, 10년 | 10년 | E5 와 10년 보존 추가 라이선스, 10년 보존 정책. 정책을 만들기 전 기록은 늘어나지 않음[2] |
   | Entra ID 감사·로그인 로그 | Free 7일, P1·P2 30일 | 유료로 바꿔도 이미 지난 기록은 돌아오지 않음[7] |
   | Entra 위험 로그인 | Free 7일, P1 30일, P2 90일 | [7] |
   | Microsoft Graph 활동 로그 | 자체 보관 없음 | 진단 설정으로 저장소·분석 도구에 보낸 것만 남음(P1·P2)[7] |
   | Azure 활동 로그 | 90일 | 진단 설정으로 내보내면 더 길게 보관[9] |
   | Google Workspace 로그 이벤트 대부분 | 6개월 | 관리자가 지우거나 기간을 바꿀 수 없음. Email log search 30일, Vault 로그 이벤트는 기한 없음[11] |
   | Google Cloud `_Required` 버킷 | 400일 | 바꿀 수 없음[13] |
   | Google Cloud `_Default`·사용자 정의 버킷 | 기본 30일 | 프로젝트 버킷은 1~3650일로 바꿀 수 있음[13] |
   | AWS CloudTrail 이벤트 기록 (Event history) | 90일 | 관리 이벤트만, 리전마다 따로. 계속 남기려면 트레일이나 이벤트 데이터 스토어가 필요[19] |
   | Okta System Log API | 최근 90일 | API·SDK 로 받을 수 있는 범위[22] |
   | Slack Audit Logs API | — | Enterprise 요금제 조직에서만 제공[24] |

   Microsoft 365 는 사용자 지정 보존 정책이 기본 정책보다 우선해서, 기본 1년보다 짧은 정책을 만들면 짧은 쪽이 적용됩니다[1]. 테넌트에 걸린 실제 정책은 Purview 포털의 감사 보존 정책 화면에서 확인해 그 값을 적습니다. Google Cloud 로그 버킷의 보존 기간을 줄이면 기간이 지난 로그를 7일 동안 지우지 않고 두지만 조회는 할 수 없고, 그 안에 보존 기간을 다시 늘리면 되살릴 수 있습니다[14]. 수집 직전에 버킷 보존 설정이 바뀌었다면 바뀐 시각과 값을 함께 적습니다.

3. **수집 시점의 감사 설정을 첨부합니다.** 설정이 꺼져 있었다면 기록이 없는 이유가 됩니다. Microsoft 365 의 `UnifiedAuditLogIngestionEnabled` 가 `$false` 면 사용자·관리자 활동이 감사 로그에 기록되지 않고 검색도 되지 않습니다(기본값 `$true`)[6]. 이 값은 Exchange Online PowerShell 의 `Get-AdminAuditLogConfig` 로 확인하고, Security & Compliance PowerShell 에서는 늘 `False` 로 나오므로 어느 셸에서 확인했는지까지 적습니다[5]. 사서함마다 `AuditEnabled`·`AuditBypassEnabled`·`DefaultAuditSet` 을 뽑아 두면 감사 우회 (Audit bypass) 가 걸린 사서함을 보고서에 밝힐 수 있습니다[27]. Google Cloud 의 데이터 접근 감사 로그 (Data Access audit logs) 는 일부 BigQuery 서비스를 빼면 기본으로 꺼져 있고, `DATA_READ`·`DATA_WRITE` 는 켜야 남습니다[15]. Graph 활동 로그는 진단 설정에서 로그 범주를 켠 때부터 모입니다[7].

4. **도구가 받은 범위를 실행 로그로 확인합니다.** 수집 경로마다 한 번에 돌려주는 건수에 상한이 있어서, 상한에 걸린 구간은 일부만 받았을 수 있습니다. 경로별 상한은 아래와 같고, 서로 다른 경로의 값이므로 섞어 쓰지 않습니다.

   | 수집 경로 | 상한 |
   |---|---|
   | `Search-UnifiedAuditLog` | 기본 100건, `-ResultSize` 최대 5,000. `ReturnLargeSet` 은 정렬 없이 최대 50,000건, `ReturnNextPreviewPage` 는 날짜순 최대 5,000건, 같은 세션에서 둘을 섞으면 10,000건[4] |
   | Purview 포털 검색 | 날짜 범위 최대 180일. 내보내기는 Audit (Standard) 50,000행, Audit (Premium) 1,000,000행[3] |
   | Entra 관리 센터 다운로드 | 파일 하나에 로그인·프로비저닝 100,000건, 감사 250,000건[8] |
   | Google Workspace Reports API | `endTime` 이 없고 `startTime` 이 180일보다 이전이면 최근 180일만. Gmail 요청은 두 값이 모두 필요하고 차이가 30일 이하[12] |

   Microsoft-Extractor-Suite 의 `Get-UAL` 은 한 번에 5,000건씩 받다가 결과가 5,000건에 닿으면 구간을 반으로 줄여 다시 받습니다[25]. 가장 짧은 구간에서도 5,000건이 넘으면 실행 로그에 `SOME EVENTS IN THIS RANGE ARE NOT CAPTURED.` 로 끝나는 `[ERROR]` 줄을 남기고 받은 만큼만 쓴 채 넘어가고, 서버 오류로 재시도 횟수를 다 쓰면 `[ERROR] Max retries reached for window` 가 들어간 줄을 남기고 그 구간을 건너뜁니다[25]. 이 두 줄이 있는 구간은 보고서에 "받지 못한 구간" 으로 적습니다. 실행이 끝나면 날짜 범위·총 건수·만든 파일 수·구간 조정 횟수·출력 폴더·처리 시간을 요약해 출력하므로 이 요약도 부록에 넣습니다[25].

5. **받은 사본의 해시를 곧바로 계산합니다.** 이 페이지에서 다루는 서비스 가운데 공급자가 서명한 무결성 증빙을 만들어 주는 것은 AWS CloudTrail 의 로그 파일 무결성 검증 (Log file integrity validation) 입니다. 검증을 켜 두면 한 시간마다 로그 파일의 SHA-256 해시를 담고 SHA-256 with RSA 로 서명한 다이제스트 파일이 생기고, 이것으로 로그 파일이 바뀌지 않았다는 것과 어느 기간에 계정으로 전달된 로그 파일이 없었다는 것까지 주장할 수 있습니다[17]. 다이제스트의 경로·필드·검증 방법은 [트레일과 이벤트 기록](../../02-artifacts/aws/cloudtrail/trails.md)에서 다룹니다. 그 밖의 서비스는 수집한 쪽이 사본의 해시를 계산해 무결성을 보입니다. SaaS 데이터를 보존할 때는 메타데이터까지 포함한 사본을 받고, 사본의 암호 해시를 계산하고, 알려진 정상 사본과 비교하는 방법을 씁니다[33]. 서비스가 파일 메타데이터에 해시를 주면 내려받은 파일의 해시와 맞춰 볼 수 있고, 2016년 기준 Google Drive API 는 파일마다 MD5 를 메타데이터로 돌려줬습니다[34].

   ```bash
   # 받은 파일 전체의 해시 목록을 만들고 목록 파일도 따로 해시해 둔다 (파일 이름은 만든 예시)
   find Output/UnifiedAuditLog -type f -print0 | sort -z | xargs -0 sha256sum > hashes-20260901.txt
   sha256sum hashes-20260901.txt
   ```

6. **시각 기준과 반영 지연을 적습니다.** 로그마다 시각이 기록되는 기준과 조회할 수 있게 되기까지의 지연이 달라서, 조회 범위의 끝 시각과 수집한 시각을 함께 적어야 최근 이벤트가 빠졌을 가능성을 판단할 수 있습니다. 필드별 정규화 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)과 [클라우드 타임라인](../analysis/timeline.md)에서 다룹니다.

   | 서비스 | 시각 필드와 기준 | 반영 지연 |
   |---|---|---|
   | Microsoft 365 통합 감사 로그 | UTC 로 저장. `Search-UnifiedAuditLog` 에 시간대 없이 넣은 값도 UTC 로 해석[4] | Exchange·SharePoint·OneDrive·Teams 는 보통 60~90분, 다른 서비스는 더 길 수 있고 보장하지 않음[3] |
   | Entra 관리 센터에서 받은 파일 | UTC[8] | — |
   | Azure 활동 로그 | `eventTimestamp` 는 서비스가 이벤트를 만든 시각, `submissionTimestamp` 는 조회할 수 있게 된 시각[10] | 두 필드의 차이로 확인 |
   | Google Cloud LogEntry | `timestamp` 는 이벤트 시각, `receiveTimestamp` 는 Logging 이 받은 시각. RFC 3339, 출력은 늘 `Z`[16] | 두 필드의 차이로 확인 |
   | Google Workspace | Reports API `id.time` 은 문서상 UNIX epoch 초, `startTime`·`endTime` 파라미터는 RFC 3339[12] | 로그인·Drive·Gmail 은 몇 분, Groups 는 수십 분~몇 시간, OAuth 는 몇 시간까지. 드물게 보고되지 않는 이벤트도 있음[11] |
   | AWS CloudTrail | `eventTime` 은 요청이 끝난 시각, UTC[20] | 로그 파일 전달은 API 호출 뒤 평균 5분쯤[21] |
   | Okta System Log | `published`. 폴링 요청의 결과는 내부 저장 순서라 `published` 순서가 뒤바뀔 수 있고, `since`·`until` 로 경계를 준 요청은 `published` 순서를 보장[23] | — |
   | Slack Audit Logs API | `date_create` 는 epoch 정수[24] | — |

7. **도구 판정과 원본 레코드를 나눠 적습니다.** 결론 문장에는 원본 레코드의 작업 이름·주체·시각·IP 를 근거로 달고, 도구가 붙인 점수나 표시는 따로 "도구의 해석" 으로 적습니다. 판정 도구의 성격은 아래 도구 절에 있습니다.

## 도구

도구 사용법은 [Microsoft 365 수집 도구](../acquisition/m365-collection.md)와 [AWS·Azure·GCP 수집](../acquisition/iaas-collection.md)에서 다루고, 여기서는 보고서 부록에 남길 것만 정리합니다. 도구 이름과 판, 실행한 함수·명령, 날짜 범위, 실행 로그는 모든 도구에 공통으로 남깁니다.

| 도구 | 대상 | 보고서에 더 남길 것 |
|---|---|---|
| Microsoft-Extractor-Suite | Microsoft 365·Entra·Azure | 출력 형식(CSV·JSON·JSONL·SOF-ELK)과 인코딩, 실행 로그의 `[ERROR]`·`[WARNING]` 줄, 끝 요약[25] |
| Hawk | Microsoft 365·Entra | 날짜 범위(최대 365일)[29]. `_Investigate_` 로 시작하는 파일은 더 볼 만한 항목일 뿐 판정이 아님. 실행한 함수 이름과 사용 지역을 원격 수집함[28] |
| Untitled Goose Tool | Microsoft 365·Entra·Azure | 설정 파일의 `date_start`·`date_end`·`ual_threshold`. `date_start` 를 비우면 보존 기간의 가장 이른 날부터 받음[30] |
| DFIR-O365RC | Microsoft 365·Entra·Azure·Azure DevOps | 사용한 cmdlet. 검색당 50,000건 제한이 있고, Purview 를 쓰는 cmdlet 여러 개가 같은 파일에 쓰면 단순히 이어 붙여 JSON 이 깨질 수 있음[31] |
| ALFA | Google Workspace | `--start-time`·`--end-time`(RFC 3339)으로 준 수집 범위. kill chain 점수는 도구의 해석[32] |
| AWS CLI 로그 검증 | CloudTrail | 검증한 기간과 결과[17] |

ALFA 는 이벤트를 `config/event_to_mitre.yml` 의 대응표로 MITRE ATT&CK 클라우드 기법에 붙이고, 시간 순서로 이어지는 공격 단계를 찾아 0~1 사이 점수(1 이 완전한 사슬)를 매기며, 계산에 쓰는 상수는 `config/config.yml` 에 고정돼 있습니다[32]. Hawk 는 결론을 대신 내리지 않고 결론에 필요한 데이터를 빨리 모으는 것을 목표로 합니다[28]. 어느 쪽이든 보고서에서는 점수나 표시가 아니라 그 밑의 레코드를 근거로 씁니다. 탐지 규칙으로 걸러 낸 결과도 같은 방식으로 다루고, 규칙 쪽 설명은 [탐지 규칙으로 로그 검색하기](../analysis/detection-rules.md)에 있습니다.

## 함정과 한계

- **도구가 표시하는 보존 기간.** Microsoft-Extractor-Suite 의 라이선스 확인 기능은 SKU 이름에 E5 가 있으면 365일, E3 이면 180일, 나머지는 90일로 표시하고, Entra 로그는 E3·E5·P1·P2 가 하나라도 있으면 30일, 없으면 7일로 출력합니다[26]. 반면 Purview 문서는 E5 여부를 활동한 사용자 단위로 보고 워크로드마다 다르게 적용합니다[1]. DFIR-O365RC 문서의 표도 통합 감사 로그를 Exchange Online PowerShell 로 90일, Purview 로 180일, Office 365 Management API 로 7일로 적었는데, 이 값은 수집 경로별로 받을 수 있는 기간이라 공식 보존 기간과 기준이 다릅니다[31]. 보고서의 보존 기간은 문서 기준 날짜와 함께 공식 문서 값을 쓰고, 실제로 받은 범위는 실행 로그로 적습니다.
- **파일 이름의 시각.** `Get-UAL` 은 실행 로그의 건수·상한 줄에는 구간 경계를 UTC 로 바꿔 쓰지만, 재시도 초과 줄, 출력 파일 이름(`UAL-` 뒤의 시작·끝 시각), 끝 요약의 날짜 범위에는 변환하지 않은 값을 씁니다[25]. 파일 이름의 시각을 UTC 로 단정하지 않습니다.
- **`-AuditDataOnly` 로 받은 파일.** `Get-UAL` 에 이 스위치를 주면 `AuditData` 만 남고 겉을 감싸는 속성은 빠집니다[25]. 보고서에 어느 형태로 받았는지 적습니다.
- **깨진 JSON.** 여러 cmdlet 이 같은 JSON 파일에 이어 쓰면 파싱이 안 될 수 있습니다[31]. 해시를 계산한 원본 파일은 그대로 두고, 파싱하려고 고친 사본은 별도 파일과 해시로 남깁니다.
- **보존 정책은 거슬러 올라가지 않습니다.** Entra 를 유료로 바꾸거나[7] Purview 10년 보존 정책을 만들어도[2] 이미 지난 기록은 돌아오지 않습니다. 조사를 시작한 뒤 라이선스를 올렸다면 그 시각을 적습니다.
- **반영 지연.** 사건 직후에 뽑은 결과에는 최근 이벤트가 아직 없을 수 있습니다[3][11]. 조회 범위의 끝 시각과 수집 시각을 함께 적고, 필요하면 지연 시간이 지난 뒤 다시 받습니다.
- **인증 정보가 든 산출물.** Untitled Goose Tool 은 자격 증명을 `.auth`, 인증 토큰·쿠키를 `.ugt_auth` 파일에 둡니다[30]. 산출물 폴더를 통째로 넘기지 말고 이런 파일은 빼서 따로 다룹니다.
- **옮긴 CloudTrail 로그.** AWS CLI 는 CloudTrail 이 전달한 자리에 있는 파일만 검증하고, 다른 곳으로 옮긴 로그는 따로 만든 도구로 검증해야 합니다[17]. 다이제스트가 늦게 전달되거나, 처리 지연으로 원래 다이제스트에 들어가지 못한 로그 파일을 나중에 담는 `_backfill` 다이제스트가 올 수 있고, 전달 오류 뒤 다시 보내는 동안에는 순서가 뒤바뀌어 사슬이 잠시 끊겨 보일 수 있어서, 한 시간짜리 다이제스트 하나가 없다고 곧바로 삭제로 보지 않습니다[18].
- **상용 도구의 수집 범위.** OneDrive 를 대상으로 한 시험에서 Magnet AXIOM 5.10.0.30634 는 Recent·Personal Vault·Recycle Bin 을, Cellebrite UFED Cloud 7.49.0.28 은 Recent·Personal Vault 를 받지 못했고 Recycle Bin 은 폴더 메타데이터 없이 일부만 받았습니다[35]. 같은 시험에서 OneDrive 공개 API 로는 Personal Vault 에 일부만 접근할 수 있었고 Recycle Bin 에는 접근할 수 없었습니다[35]. 어떤 도구의 어느 판으로 어느 범주를 받았는지 보고서에 적습니다.
- **내용이 바뀌지 않고 내려받혔음을 보이는 방법.** 수집 과정을 녹화하고 모든 과정을 로그로 남겨 이를 보이는 방법은 앞으로의 연구 과제로 제안된 단계입니다[35]. 수집 명령·실행 로그·해시 목록을 함께 남기는 것이 현실적인 근거입니다.
- **보존 조치의 시각.** 미국 민사 소송의 소송 대비 보존 (Litigation hold) 기간에 증거가 사라지거나 바뀌면 증거 인멸 (Spoliation) 으로 제재를 받을 수 있고, 당사자가 공급자와 짜고 문서를 조작하는 위협도 연구됐습니다[36]. 보존 조치를 언제, 어떤 방법으로 했는지 적어 두면 이런 다툼에 답할 수 있습니다. 보존 조치 방법은 [로그부터 지키기](../acquisition/log-preservation.md)에서 다룹니다.

## 결과를 어떻게 해석하나

**증명하는 것.** 감사 로그 레코드는 "이 시각(UTC)에 이 계정·주체로 이 작업이 기록되었다" 까지를 보여 줍니다. 다이제스트로 검증한 CloudTrail 로그 파일은 전달된 뒤 바뀌지 않았다는 것, 특정 자격 증명이 특정 API 활동을 했다는 것, 어느 기간에 계정으로 전달된 로그 파일이 없었다는 것을 보여 줍니다[17].

**증명하지 못하는 것.** 계정이나 자격 증명을 실제로 쓴 사람이 누구인지는 로그만으로 알 수 없고, CloudTrail 검증도 "특정 자격 증명이" 한 일까지만 보여 줍니다[17]. 로그가 없다는 사실만으로 활동이 없었다고 할 수도 없습니다. 보존 기간이 지났거나, 로그가 기본으로 꺼져 있었거나, 감사 우회가 걸렸거나, 도구가 건너뛴 구간이거나, 아직 반영되지 않았을 수 있고, Google Workspace 는 드물게 이벤트가 아예 보고되지 않기도 합니다[11]. Slack Audit Logs API 는 메시지 내용을 보여 주지 않고 가능한 감사 이벤트의 일부만 지원하므로, 여기에 없다고 그 행동이 없었다고 하지 않습니다[24]. 로그를 끄거나 지운 흔적을 찾는 방법은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)에서 다룹니다.

보고서의 수집 부분에는 아래 항목을 채웁니다.

| 항목 | 적을 내용 |
|---|---|
| 수집 권한 | 조회한 계정, 역할, 관리 단위 제한 여부 |
| 조사 가능 기간 | 로그별 보관 기간(문서 기준 날짜), 테넌트 보존 정책 |
| 기록이 없었던 이유 | 수집 시점의 감사 설정, 꺼져 있던 로그, 감사 우회 사서함 |
| 받지 못한 구간 | 실행 로그의 오류 줄, 상한에 걸린 구간, 도구가 받지 못한 범주 |
| 무결성 | 해시 목록과 그 해시, CloudTrail 다이제스트 검증 결과 |
| 시각 기준 | 필드별 기준(UTC 여부), 조회 범위 끝 시각, 수집 시각 |

결론 문장은 기록으로 확인되는 만큼만 씁니다. 아래 값은 모두 만든 예시입니다.

- 쓰지 않음: "kim@contoso.com 사용자가 2026년 9월 1일 고객 명부를 빼돌렸다."
- 씀: "통합 감사 로그에 2026-09-01 02:14:07 UTC 부터 02:31:52 UTC 사이에 kim@contoso.com 계정으로 203.0.113.25 에서 `FileDownloaded` 작업 42건이 기록되어 있다. 이 계정을 실제로 사용한 사람은 이 기록만으로 특정할 수 없다."
- 씀: "2026-08-20 09:00 UTC 부터 10:00 UTC 까지는 수집 도구가 5,000건 상한에 걸려 일부만 받았으므로, 이 구간에서 해당 작업이 없다고 판단하지 않았다."

## 참고 문헌

1. Microsoft, "Manage audit log retention policies", Microsoft Learn (Last updated 2026-06-19). https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
2. Microsoft, "Learn about auditing solutions in Microsoft Purview", Microsoft Learn (Last updated 2026-05-18). https://learn.microsoft.com/en-us/purview/audit-solutions-overview
3. Microsoft, "Search the audit log", Microsoft Learn (Last updated 2026-06-19). https://learn.microsoft.com/en-us/purview/audit-search
4. MicrosoftDocs, "Search-UnifiedAuditLog". https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Search-UnifiedAuditLog.md
5. MicrosoftDocs, "Get-AdminAuditLogConfig". https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Get-AdminAuditLogConfig.md
6. MicrosoftDocs, "Set-AdminAuditLogConfig". https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Set-AdminAuditLogConfig.md
7. MicrosoftDocs, "Microsoft Entra data retention" (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
8. MicrosoftDocs, "How to download logs in Microsoft Entra ID" (ms.date 2024-11-08). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/howto-download-logs.md
9. MicrosoftDocs, "Activity Log in Azure Monitor" (ms.date 2026-05-04). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
10. MicrosoftDocs, "Azure Activity Log event schema" (ms.date 2026-03-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
11. Google, "Data retention and lag times", Google Workspace Admin Help (Last updated 2026-09-25). https://support.google.com/a/answer/7061566
12. Google, "Method: activities.list", Admin SDK Reports API (Last updated 2026-09-09). https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
13. Google Cloud, "Quotas and limits", Cloud Logging (Last updated 2026-09-25). https://cloud.google.com/logging/quotas
14. Google Cloud, "Configure log buckets", Cloud Logging (Last updated 2026-09-25). https://cloud.google.com/logging/docs/buckets
15. Google Cloud, "Enable Data Access audit logs" (Last updated 2026-09-25). https://cloud.google.com/logging/docs/audit/configure-data-access
16. Google Cloud, "LogEntry", Cloud Logging API (Last updated 2026-09-04). https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry
17. AWS, "Validating CloudTrail log file integrity". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html
18. AWS, "CloudTrail digest file structure". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-digest-file-structure.html
19. AWS, "Working with CloudTrail event history". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
20. AWS, "CloudTrail record contents for management, data, and network activity events". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-record-contents.html
21. AWS, "Getting and viewing your CloudTrail log files". https://docs.aws.amazon.com/awscloudtrail/latest/userguide/get-and-view-cloudtrail-log-files.html
22. Okta, "Monitor Okta" (okta-developer-docs). https://github.com/okta/okta-developer-docs/blob/master/packages/@okta/vuepress-site/docs/concepts/monitor/index.md
23. Okta, "System Log query" (okta-developer-docs). https://github.com/okta/okta-developer-docs/blob/master/packages/@okta/vuepress-site/docs/reference/system-log-query/index.md
24. Slack, "Audit Logs API". https://api.slack.com/admins/audit-logs
25. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-UAL.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-UAL.ps1
26. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-ProductLicenses.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-ProductLicenses.ps1
27. Invictus IR, Microsoft-Extractor-Suite, `Scripts/Get-AuditLogSettings.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AuditLogSettings.ps1
28. T0pCyber, Hawk, README. https://github.com/T0pCyber/hawk/blob/master/README.md
29. T0pCyber, Hawk, `Start-HawkTenantInvestigation.ps1`. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Start-HawkTenantInvestigation.ps1
30. CISA, Untitled Goose Tool, README. https://github.com/cisagov/untitledgoosetool/blob/develop/README.md
31. ANSSI, DFIR-O365RC, README. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/README.md
32. Invictus IR, ALFA, README. https://github.com/invictus-ir/ALFA/blob/main/README.md
33. Eoghan Casey, "SaaS Forensics & Response: Forensic Preservation, Recovery, and Analysis of SaaS Data", DFRWS USA 2023 발표. https://dfrws.org/presentation/saas-forensics-and-response/
34. Marco Scarito, Mattia Epifani, Francesco Picasso, "Life on Clouds, a Forensics Overview", DFRWS EU 2016 발표. https://dfrws.org/presentation/life-on-clouds-a-forensics-overview/
35. Jihyeok Yang, Jieon Kim, Jewan Bang, Sangjin Lee, Jungheum Park, "CATCH: Cloud Data Acquisition through Comprehensive and Hybrid Approaches", Forensic Science International: Digital Investigation 43 (2022) 301442. DOI 10.1016/j.fsidi.2022.301442
36. Shams Zawoad, Ragib Hasan, John Grimes, "LINCS: Towards building a trustworthy litigation hold enabled cloud storage system", Digital Investigation 14 (2015) S55–S67. DOI 10.1016/j.diin.2015.05.014
