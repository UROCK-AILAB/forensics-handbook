---
title: "서비스 회사에 대한 데이터 요청"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 660
---

# 서비스 회사에 대한 데이터 요청 (Legal Requests)

기업 클라우드에서는 조직이 스스로 받을 수 있는 기록을 먼저 받고, 서비스 회사에 대한 법적 요청은 조직 밖의 기록이 필요할 때 씁니다. 큰 클라우드 회사는 기업 고객 데이터를 달라는 요청을 받으면 그 고객 조직에 직접 요청하도록 돌려보내려 하고, 고객에게 요청 사실을 알립니다[1][2].

이 페이지는 법률 자문이 아니고, 조사자가 요청 경로를 고르고 받은 자료를 해석하는 데 필요한 사실만 모았습니다. 요청서를 쓰고 내는 절차는 관할 기관과 법무 담당의 안내를 따릅니다. 개인 계정을 대상으로 한 Google 의 법적 절차별 제공 자료 표, 사용자 통지, 긴급 공개는 [AI 판의 서비스 회사에 대한 데이터 요청](https://urock-ailab.github.io/forensics-handbook/ai/03-techniques/acquisition/legal-requests.html)에 있고, 여기서는 기업이 쓰는 IaaS·Microsoft 365·Google Workspace·업무용 SaaS 관점만 다룹니다.

## 언제 쓰나

조직이 테넌트나 계정의 주인이면 감사 로그, 메일함, 저장소 사본은 관리자 권한으로 직접 받을 수 있습니다. AWS 에서는 고객이 자기 콘텐츠를 통제하고, 저장 리전·암호화·접근 권한을 고객이 정합니다[1]. 그래서 서비스 회사에 대한 요청은 다음 경우에 씁니다.

- 조사 대상이 조직 밖의 계정입니다. 예를 들어 공격자가 쓴 개인 메일 계정, 자료를 옮겨 받은 외부 저장소 계정, 조직에 속하지 않은 GitHub 계정이 그렇습니다.
- 조직이 볼 수 없는 회사 쪽 기록이 필요합니다. 계정 가입 때의 IP, 결제 정보 같은 가입자 정보가 여기에 들어갑니다[2][6].
- 수사기관이 조직 모르게 자료를 받아야 합니다. 이때는 요청에 비공개 명령이 붙는지가 통지 여부를 가릅니다(아래 "함정과 한계").

서비스 회사가 협조하지 않는 경우에는 적절한 사용자 자격 증명을 얻었을 때에 한해 사용자 쪽에서 온라인으로 수집하는 경로가 있습니다[9]. 서비스 회사가 공식으로 내놓은 공개 API (open API) 는 회사가 정한 범위에만 접근할 수 있어서, 공개 API 에만 기대는 도구로는 저장된 자료를 모두 받지 못할 수 있습니다[9]. 이 경로도 법적 권한을 먼저 확인해야 합니다.

## 절차

1. **조직이 스스로 받을 수 있는 것부터 받습니다.** 감사 로그의 보존 조치는 [로그부터 지키기](log-preservation.md), Microsoft 365 수집은 [Microsoft 365 수집 도구](m365-collection.md), AWS·Azure·Google Cloud 기록은 [AWS·Azure·GCP 수집](iaas-collection.md)에 있습니다. 메일·문서 내용은 Microsoft 365 에서는 [Purview eDiscovery](../../02-artifacts/m365/purview-ediscovery.md) 사건 안에서 검색·보존·검토·내보내기를 하고[8], Google Workspace 에서는 [Vault](../../02-artifacts/google-workspace/vault-takeout.md) 로 내보냅니다[7].
2. **조직 밖에 남은 기록을 정리합니다.** 계정 이름, 메일 주소, 저장소 이름, 관련 시각처럼 요청 대상을 좁히는 식별자를 모읍니다. Microsoft 는 민사 요청이 특정 계정과 식별자를 겨냥하도록 요구하고[2], GitHub 는 사용자·조직·저장소 이름, 관련 URL, 필요한 기록의 종류를 적어 달라고 합니다[6].
3. **회사가 공개한 정책에서 요청 종류와 받을 수 있는 자료를 확인합니다.** 회사마다 내용(content)과 비내용(non-content)을 나누는 기준과 필요한 법적 절차가 다릅니다(아래 표).
4. **보존 요청이 필요한지 판단합니다.** 보존 요청(preservation request)은 법적 절차를 밟는 동안 회사가 특정 정보의 사본을 떼어 두게 하는 요청입니다[4]. 요청한 시각을 기록해 둡니다.
5. **국외 회사면 경로를 확인합니다.** 회사의 법인과 준거법에 따라 국제 형사사법 공조 경로가 필요할 수 있습니다(아래 "국외 회사에 요청할 때"). 한국 수사기관의 경로와 양식은 관계 기관의 안내를 확인합니다.
6. **받은 자료를 증거로 보관합니다.** 받은 날짜, 요청 문서 번호, 파일 해시를 기록하고, 조직이 직접 받은 기록과 같은 방식으로 [보고서](../reporting/forensic-report.md)에 출처를 남깁니다.

### 회사별 기업 데이터 요청 처리

| 회사 | 기업·고객 데이터 요청 처리 | 고객 통지 | 문서 기준 |
|---|---|---|---|
| AWS | 법이나 정부 기관의 유효하고 구속력 있는 명령을 따라야 할 때만 고객 콘텐츠를 공개합니다. 정부 기관이 고객 콘텐츠를 요구하면 고객에게 직접 요청하도록 돌려보내려 하고, 지나치게 넓은 명령에는 이의를 제기합니다[1]. | 공개가 강제되면 법으로 금지되지 않는 한 고객에게 합리적인 사전 통지를 합니다[1]. | 2026년 9월 문서 기준 |
| Microsoft | 기업 데이터 요청은 기업 자체에서 받도록 늘 돌려보내려 합니다[2]. 보고서의 "기업 고객"은 Microsoft 365·Dynamics 365 같은 상용 클라우드를 50석 넘게 사거나 Azure 구독을 산 조직입니다[2]. | 법으로 금지되지 않는 한 기업 고객에게 사전 통지하고, 비공개 명령이 끝나면 통지합니다[2]. | 2025년 7~12월 보고서 |
| Google | 요청에 대한 대응은 서비스 제공 주체에 따라 다르고, 대부분의 서비스는 Google LLC(미국법) 또는 Google Ireland Limited(아일랜드법)입니다[3]. | 공개 전에 계정으로 메일을 보내고, 조직이 관리하는 계정이면 계정 관리자에게 알립니다[3]. | 2026년 9월 문서 기준 |
| GitHub | 사용자 동의가 있으면 비공개 계정 정보를 사용자(조직 계정이면 소유자)나 사용자가 서면으로 지정한 제3자에게 줍니다[6]. | 공개 전에 인증된 메일 주소로 법적 문서 사본을 보내 알립니다[6]. | 정책 저장소 최종 커밋 2026-03-26 |
| Dropbox | 특정 사람과 수사에 좁혀지지 않은 광범위한 요청에 저항합니다[5]. | 통지를 원칙으로 하지만 비공개 명령이 붙는 경우가 많고, 명령이 끝나면 알릴 수 있습니다[5]. | 2026년 9월 문서 기준 |

Okta·Zoom·Box·Slack 같은 다른 업무용 SaaS 는 각 회사의 법 집행 요청 안내와 투명성 보고서를 요청 전에 확인합니다.

Microsoft 가 공개한 2025년 7~12월 수치로는 전 세계 수사기관의 기업 고객 관련 요청 190건 가운데 96건(51%)이 거부·철회·자료 없음·고객에게 돌려보냄으로 끝났고, 94건(49%)은 공개가 강제됐습니다[2]. 강제된 94건 중 45건은 고객 콘텐츠 공개였고 그중 31건이 미국 수사기관 요청이었으며, 49건은 기본 가입자 정보·IP 로그 같은 비내용 공개였습니다[2]. 같은 기간 상용·공공·교육 고객의 Azure 콘텐츠 데이터를 공개한 건은 없습니다[2]. 이 수치는 그 보고 기간의 값이라서 다른 기간에는 달라집니다.

### 요청 종류와 받을 수 있는 자료

회사가 공개한 구분은 대체로 "가입자 정보 → 접속 기록·비내용 → 내용" 순서로 필요한 법적 절차가 무거워집니다. 아래는 각 회사가 공개한 구분이고, Google·GitHub 는 미국법 기준, Microsoft 는 미국 절차나 그 나라에서 그에 준하는 절차 기준입니다.

| 회사 | 가벼운 절차로 받는 자료 | 중간 | 가장 무거운 절차가 필요한 자료 |
|---|---|---|---|
| Microsoft | 비내용(기본 가입자 정보: 메일 주소, 이름, 주·국가·우편번호, 가입 때 IP, 그 밖에 IP 접속 기록, 결제 정보): 소환장(subpoena)이나 법원 명령[2] | — | 내용(메일 본문, OneDrive 에 저장한 사진·문서 등): 영장(warrant)이나 그에 준하는 절차[2] |
| Google | 가입자 등록 정보와 일부 IP 주소: 소환장[3] | 메일의 To·From·CC·BCC·Timestamp 필드 같은 비내용 기록: 형사 사건에서 법원 명령[3] | 메일·문서·사진 같은 통신 내용: 수색영장[3] |
| GitHub | 계정에 연결된 이름·메일 주소, 결제 정보, 가입·해지 날짜, 가입 때 IP·날짜·시각, 특정 시각이나 사건에 계정 접속에 쓴 IP: 소환장[6] | 계정 접속 기록, 계정·비공개 저장소 설정, 사용자·IP 별 분석 데이터, 보안 접속 기록: 18 U.S.C. 2703(d) 법원 명령이나 수색영장[6] | 비공개 저장소 내용, 비밀 Gist, 비공개 저장소의 이슈·위키, 인증·암호화에 쓰는 키: 수색영장만[6] |

AWS 는 고객 콘텐츠와 계정 정보를 나눕니다. 고객 콘텐츠는 고객이 AWS 서비스에 올려 처리·저장·호스팅하는 소프트웨어(머신 이미지 포함)·데이터·텍스트·오디오·영상·이미지와 그 계산 결과이고, 계정 정보는 계정을 만들고 관리할 때 낸 이름·사용자 이름·전화번호·메일 주소·결제 정보입니다[1]. 리소스 식별자, 메타데이터 태그, 접근 통제, 권한 설정은 고객 콘텐츠에 들어가지 않습니다[1].

조직 계정은 따로 봐야 합니다. GitHub 는 소환장으로 조직 계정을 요청하면 소유자의 이름·메일 주소와 조직 계정을 만든 날짜·IP 만 주고, 다른 구성원의 정보는 그 사용자에 대한 후속 요청이 있어야 줍니다[6]. 민간 당사자(정부가 아닌 소송 당사자)는 Microsoft 에 유효한 소환장이나 법원 명령을 내야 하고, 내용을 요청하려면 계정 소유자의 구체적인 동의가 있어야 합니다[2].

### 보존 요청

| 회사 | 보존 요청에 대해 공개한 내용 |
|---|---|
| Google | 요청 시점에 Google 이 가진 정보에만 적용되고, 앞으로 생길 정보에는 적용되지 않습니다. 보존 요청만으로는 정보를 공개하지 않고, 공개하려면 법적 명령이 다시 와야 합니다[4]. |
| GitHub | 미국 수사기관이 공식 형사 수사와 관련해 요청하면 법원 명령 등이 나올 때까지 계정 기록을 최대 90일 보존합니다[6]. |
| Microsoft | 영국 당국이 미국·영국 데이터 접근 협정에 따라 보내는 요청에는 보존 요청도 있습니다[2]. |

보존 요청은 요청 시각 이후의 기록을 붙잡지 못합니다[4]. 조직이 할 수 있는 로그 보존 조치를 먼저 하고([로그부터 지키기](log-preservation.md)), 회사가 가진 기록도 보관 기간이 지나면 없어진다는 점은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에서 서비스별로 확인합니다.

### 국외 회사에 요청할 때

- **GitHub**: 캘리포니아에 있는 미국 회사라서 외국 당국의 법적 절차에 따라 데이터를 줄 의무가 없습니다. 외국 수사기관은 미국 법무부 형사국 국제업무국(Office of International Affairs)에 연락하고, GitHub 는 형사사법공조조약(MLAT)이나 촉탁서(letter rogatory)를 거쳐 미국 법원이 낸 요청에 응합니다[6].
- **Google**: 형사사법공조조약은 두 나라 이상이 형사 수사 같은 법적 문제에서 서로 돕는 방식을 정한 조약이고, 한 나라 정부가 다른 나라 정부를 통해 그 나라 회사의 정보를 구하는 경로입니다[4]. Google LLC 는 미국 밖 정부의 요청이 미국법, 요청국의 법, GNI(Global Network Initiative) 원칙, Google 정책에 모두 맞을 때 정보를 줄 수 있습니다[3]. Google Ireland 에 온 아일랜드 밖 정부의 요청은 아일랜드법, 아일랜드에 적용되는 EU 법(GDPR 포함), 요청국의 법, GNI 원칙, Google 정책에 모두 맞아야 합니다[3].
- **Microsoft**: 미국 CLOUD Act 는 미국과 최소한의 접점이 있는 서비스 회사에게 수사기관이 데이터가 어디 있든 회사가 "소유·보관·통제"하는 데이터를 공개하도록 강제할 수 있음을 분명히 했고, 그 전에 적용되던 법적·개인정보 보호 장치는 그대로 적용됩니다[2]. 2025년 하반기 190건과 관련해 Microsoft 는 미국 밖에 데이터를 저장한 미국 외 기업 고객 3곳의 콘텐츠를 미국 수사기관에 주었습니다[2]. CLOUD Act 데이터 접근 협정은 상대국이 미국에 있는 개인이나 단체를 겨냥하는 데 쓸 수 없고, 형사사법공조조약 절차는 그대로 남아 있습니다[2].
- **AWS**: 고객이 고른 리전 밖으로 콘텐츠를 옮기거나 복제하지 않지만, 고객이 시작한 서비스를 제공하는 데 필요하거나 법·정부의 구속력 있는 명령을 따를 때는 예외입니다[1].

한국 수사기관이 국외 회사에 요청하는 경로와 양식은 관계 기관의 안내를 확인합니다.

## 도구

서비스 회사에 대한 요청 자체에는 도구가 없고, 요청 대신 조직이 쓰는 수집 도구가 이 페이지의 앞 단계입니다.

| 목적 | 쓰는 것 | 자세한 페이지 |
|---|---|---|
| Microsoft 365 메일·문서 보존과 내보내기 | Purview eDiscovery 사건(검색·보존·검토·내보내기)[8] | [Purview eDiscovery와 보존](../../02-artifacts/m365/purview-ediscovery.md) |
| Google Workspace 데이터 보존과 내보내기 | Vault 사건(matter)·보존(hold)·내보내기[7] | [Vault와 Takeout](../../02-artifacts/google-workspace/vault-takeout.md) |
| 개인 Google 계정 자료 | 계정 주인이 Takeout 으로 만든 보관 파일[4] | [AI 판의 계정 데이터 내보내기로 수집](https://urock-ailab.github.io/forensics-handbook/ai/03-techniques/acquisition/export-collection.html) |
| 감사 로그 | 각 서비스의 감사 로그 수집 경로 | [Microsoft 365 수집 도구](m365-collection.md), [AWS·Azure·GCP 수집](iaas-collection.md) |

계정 주인은 Takeout 으로 만든 자료를 누구에게나 넘길 수 있지만, Google 은 정부 기관이 요청하면 그 계정 주인을 위한 요청이라도 긴급한 경우가 아니면 유효한 법적 절차를 요구합니다[4]. Vault 내보내기 파일은 내보내기를 시작한 뒤 15일 동안만 받을 수 있고, 내보내기에는 모든 파일의 MD5 값을 적은 "File checksums" 파일이 들어 있습니다[7].

## 함정과 한계

1. **요청 사실이 조사 대상에게 알려질 수 있습니다.** AWS·Microsoft·Google·GitHub 는 공개 전에 고객이나 계정 주인에게 알리는 것을 원칙으로 하고[1][2][3][6], Google 은 조직이 관리하는 계정이면 관리자에게 알립니다[3]. 조사 대상이 테넌트 관리자이거나 관리자 메일함에 접근할 수 있으면 통지를 받을 가능성이 있습니다. 통지를 막는 것은 요청에 붙은 비공개 명령이고, 명령이 끝나면 통지가 나갈 수 있습니다[2][3][5].
2. **보존 요청은 요청 시점까지만 붙잡습니다[4].** 요청하기 전 보관 기간이 지나 지워진 기록은 되돌릴 수 없고, 요청한 뒤에 생긴 기록은 보존 대상이 아닙니다.
3. **회사가 줄 수 있는 자료도 회사가 모은 것뿐입니다.** GitHub 에서는 사용자가 넣지 않아도 되는 항목이라 비어 있거나, 처음부터 모으지 않았거나 보관하지 않은 정보가 있을 수 있습니다[6].
4. **조직 계정 요청은 소유자에 대한 자료로 끝날 수 있습니다.** 구성원마다 따로 요청해야 하는 회사가 있습니다[6].
5. **공개 API 에만 기대는 수집은 회사가 정한 범위에 묶입니다[9].** 사용자 자격 증명으로 받는 경로는 쓰기 전에 법적 권한부터 확인해야 합니다.
6. **공개 정책과 수치는 바뀝니다.** 이 페이지의 정책은 위 표의 문서 기준 시점 값이라서 요청 직전에 각 회사의 현재 안내를 다시 확인합니다.
7. **내보내기 파일은 기간이 지나면 지워집니다.** Vault 내보내기처럼 받을 수 있는 기간이 정해진 경로는 받는 즉시 해시를 기록하고 보관합니다[7].

## 결과를 어떻게 해석하나

서비스 회사가 준 자료는 요청을 처리한 시점에 회사가 보관하던 기록입니다. 자료에 어떤 기록이 없다는 것은 처음부터 활동이 없었다는 뜻이 아니고, 삭제·보관 기간 만료·요청 범위 밖일 가능성을 함께 따져야 합니다.

가입자 정보와 접속 IP 는 그 계정이 어느 네트워크에서 쓰였는지까지 알려 주고, 그 계정을 누가 썼는지는 알려 주지 않습니다. 보고서에는 "이 계정에 이 시각 이 IP 로 접속한 기록이 회사 제공 자료에 있다" 처럼 기록으로 확인되는 만큼만 씁니다. 회사 자료의 시각은 조직이 직접 받은 감사 로그와 [클라우드 타임라인](../analysis/timeline.md)에 합쳐 비교하고, 시간대 표기는 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 따라 UTC 로 맞춥니다. 회사 자료에 시간대가 적혀 있지 않으면 회사에 확인하고, 확인한 내용을 보고서에 남깁니다.

함께 볼 페이지: [조사 절차](investigation-process.md), [책임 공유와 조사 범위](../../01-foundations/model/shared-responsibility.md), [기록은 어디에 남나](../../01-foundations/model/where-records-live.md), [Linux 판 조사 절차](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/investigation-process.html).

## 참고 문헌

1. Amazon Web Services, "Data Privacy FAQ". https://aws.amazon.com/compliance/data-privacy-faq/
2. Microsoft, "Government Requests for Customer Data Report"(Law Enforcement Requests Report, 2025년 7~12월 보고 기준). https://www.microsoft.com/en-us/corporate-responsibility/law-enforcement-requests-report
3. Google, "How Google handles government requests for user information". https://policies.google.com/terms/information-requests?hl=en
4. Google, Transparency Report Help Center, "Requests for User Information FAQs". https://support.google.com/transparencyreport/answer/9713961?hl=en
5. Dropbox, "Transparency at Dropbox — Our Guiding Principles". https://www.dropbox.com/transparency/principles
6. GitHub, "GitHub Guidelines for Legal Requests of User Data"(site-policy 저장소). https://github.com/github/site-policy/blob/main/Policies/other-site-policies/guidelines-for-legal-requests-of-user-data.md
7. Google Workspace Help, "Export data from Vault" https://knowledge.workspace.google.com/vault/exports/export-data-from-vault , "Vault export contents" https://knowledge.workspace.google.com/vault/exports/vault-export-contents
8. Microsoft Learn, "Learn about eDiscovery"(Microsoft Purview). https://learn.microsoft.com/en-us/purview/edisc
9. Jihyeok Yang, Jieon Kim, Jewan Bang, Sangjin Lee, Jungheum Park, "CATCH: Cloud Data Acquisition through Comprehensive and Hybrid Approaches", Forensic Science International: Digital Investigation 43 (2022) 301442, DFRWS APAC 2022. DOI: 10.1016/j.fsidi.2022.301442
