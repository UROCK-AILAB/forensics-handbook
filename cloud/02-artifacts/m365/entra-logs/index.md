---
title: "Entra ID 로그"
parent: "아티팩트 · Microsoft 365"
nav_order: 170
has_children: true
has_toc: false
---

# Entra ID 로그 (Entra ID Logs)

Microsoft Entra ID 가 테넌트 안의 로그인과 디렉터리 변경을 남기는 활동 로그 (activity logs) 묶음이고, 누가 언제 어디서 인증했고 계정·앱·권한을 어떻게 바꿨는지 알려 줍니다.

## 왜 중요한가

Microsoft 365 의 계정 침해 조사는 대부분 "그 계정으로 누가, 언제, 어디서 로그인했나" 라는 질문에서 시작하고, 그 답은 Entra ID 로그인 로그에 있습니다. 로그인 뒤에 공격자가 앱을 등록하거나 인증 수단을 바꾸거나 역할을 넘겨받았다면 그 흔적은 Entra ID 감사 로그에 남습니다. 로그인 로그와 감사 로그 항목은 시스템이 만들고, 바꾸거나 지울 수 없습니다[2][4].

Entra ID 로그는 통합 감사 로그 (Unified Audit Log) 와 저장소도, 보관 기간도 따로입니다[1]. 통합 감사 로그에도 Entra ID 이벤트가 레코드 유형 `AzureActiveDirectory`(8), `AzureActiveDirectoryAccountLogon`(9, 더 이상 쓰지 않음), `AzureActiveDirectoryStsLogon`(15), `AadRiskDetection`(294) 로 들어오지만[8], 두 곳의 필드와 보관 기간이 달라서 둘 다 확보해 맞춰 봐야 합니다. 통합 감사 로그 쪽은 [통합 감사 로그](../unified-audit-log/index.md) 에서 다룹니다.

보관 기간이 짧다는 점도 서두를 이유입니다. Entra ID Free 테넌트의 로그인·감사 로그는 7일 뒤에 사라지고, 나중에 Premium 으로 올려도 이미 지난 기록은 돌아오지 않습니다[1]. 사고를 알게 되면 먼저 [로그부터 지키기](../../../03-techniques/acquisition/log-preservation.md) 를 따라 내보냅니다.

## 한눈에 보기

Entra 관리 센터의 활동 로그는 아래처럼 나뉩니다[2][6][7].

| 로그 | 기록하는 것 | 알려 주는 것 |
|---|---|---|
| 로그인 (Sign-ins) | 대화형 사용자, 비대화형 사용자, 서비스 주체 (service principal), 관리 ID (managed identity) 의 로그인 | 계정·앱·리소스·IP·결과·조건부 접근 적용 여부 |
| 감사 (Audit) | 사용자·그룹·앱·라이선스·역할·정책 변경 | 누가 어떤 대상을 어떻게 바꿨는지, 바뀌기 전 값과 뒤 값 |
| 프로비저닝 (Provisioning) | 프로비저닝 서비스가 한 작업(예: ServiceNow 에 그룹 만들기, Workday 에서 사용자 가져오기) | 외부 시스템과 주고받은 계정 동기화 |
| 가입 (Sign-ups, 미리 보기) | 외부 테넌트의 셀프 서비스 가입 시도 | 가입 성공·실패 |
| 위험 탐지·위험 사용자 | Identity Protection 이 위험하다고 판정한 로그인과 사용자 | 위험 유형·수준·처리 상태 |
| Microsoft Graph 활동 로그 | 테넌트 리소스에 들어온 Graph API 요청 | 로그인 뒤 어떤 API 를 호출했는지 |

옛 로그인 화면에는 대화형 사용자 로그인만 나옵니다[2]. 에이전트 (Agent ID) 활동을 담는 로그 유형도 감사·로그인 로그에 새로 들어왔습니다[2].

### 보관 기간과 라이선스

Entra ID 안에 남는 기간은 로그 종류와 라이선스에 따라 다릅니다. 아래 표는 2026년 1월 문서 기준입니다[1].

| 로그 | Entra ID Free | Entra ID P1 | Entra ID P2 |
|---|---|---|---|
| 감사 로그 | 7일 | 30일 | 30일 |
| 로그인 로그 | 7일 | 30일 | 30일 |
| 다단계 인증 사용 기록 | 30일 | 30일 | 30일 |
| Microsoft Graph 활동 로그 | 제공 안 함 | 저장소·분석 도구로 보내야 남음 | 저장소·분석 도구로 보내야 남음 |
| 위험 사용자 | 제한 없음 | 제한 없음 | 제한 없음 |
| 위험 로그인 | 7일 | 30일 | 90일 |

기록을 모으기 시작하는 시점도 다릅니다. P1·P2 는 구독을 시작할 때부터 모으고, Free 는 Entra ID 화면을 처음 열거나 보고 API 를 처음 쓸 때부터 모읍니다[1]. Graph 활동 로그는 진단 설정에서 그 범주를 켠 뒤부터 모읍니다[1]. 위험 사용자는 위험이 해결될 때까지 지워지지 않습니다[1].

이보다 오래 두려면 진단 설정 (Diagnostic settings) 으로 Log Analytics 작업 영역·Azure 저장소 계정·Event Hubs 로 보냅니다[6]. 이 경로로 보내면 이벤트를 약 5분 단위로 묶어 한 메시지로 보내고, 감사 이벤트 하나는 약 2KB, 로그인 이벤트 하나는 평균 11.5KB 를 차지합니다[6]. Microsoft 365 E5·Office 365 E5 등 Purview Audit (Premium) 을 쓰는 조직은 Entra ID 감사 로그를 Purview 보존 정책으로 더 길게 둘 수도 있습니다[1]. 보관 기간을 서비스끼리 견준 표는 [보관 기간과 라이선스](../../../01-foundations/logging/retention-licensing.md) 에 있습니다.

### 받는 경로

| 경로 | 형식·범위 | 조건 |
|---|---|---|
| Entra 관리 센터 내려받기 | CSV·JSON, 로그인·프로비저닝은 파일 하나에 100,000건, 감사는 250,000건 | 화면에서 고른 열과 상관없이 모든 열을 내보내고, 필터는 적용됨[5] |
| Microsoft Graph API | `beta/auditLogs/signIns`, `v1.0/auditLogs/directoryAudits`, `beta/auditLogs/provisioning`[10][11] | Premium 라이선스 필요, 최소 역할은 Reports Reader[5] |
| 진단 설정 | Log Analytics 표(`SigninLogs`, `AADNonInteractiveUserSignInLogs` 등)[13][14]·저장소 계정·Event Hubs[6] | 미리 보내 둔 기록만 Entra ID 보관 기간이 지나도 남음[1] |

공개 수집 도구 가운데 Microsoft-Extractor-Suite 는 `signInEventTypes` 필터로 대화형·비대화형·서비스 주체·관리 ID 로그인을 골라 받고[10], Untitled Goose Tool 은 로그인·감사·프로비저닝 로그를 beta 엔드포인트로 받습니다[11]. DFIR-O365RC 는 Graph 로 Entra ID 로그를 받으려면 P1 라이선스 사용자가 테넌트에 한 명 이상 있어야 하고, 앱에 `AuditLog.Read.All` 권한이 필요합니다[12]. 도구별 사용법은 [Microsoft 365 수집 도구](../../../03-techniques/acquisition/m365-collection.md) 에서 다룹니다.

경로마다 필드 이름 표기가 다릅니다. Graph 는 `createdDateTime` 처럼 소문자로 시작하고, Log Analytics 표는 `CreatedDateTime` 처럼 대문자로 시작합니다[13][15]. 검체를 받으면 실제 키 이름부터 확인하고 검색식을 맞춥니다.

### 시각

내려받은 파일의 시각은 UTC 입니다[5]. 관리 센터 화면은 로그인한 사용자가 아니라 화면을 보는 사람의 시간대로 시각을 보여 주므로[16], 화면을 캡처한 자료와 내려받은 파일을 섞으면 몇 시간씩 어긋날 수 있습니다. Graph 활동 로그는 대부분 30분 안에, 드물게는 2시간 뒤에 목적지에 도착합니다[7]. 시각을 다루는 공통 원리는 [클라우드 로그의 시각](../../../01-foundations/logging/timestamps.md) 에 있습니다.

## 읽는 순서

1. [로그인 로그 (Sign-in Logs)](sign-in-logs.md) — 대화형·비대화형·서비스 주체·관리 ID 로그인의 필드와 해석. 응용 프로그램·사용자·IP 등이 같은 비대화형 로그인을 한 줄로 묶는 방식과, 기밀 클라이언트의 비대화형 로그인 IP 가 실제 요청 주소가 아닌 처음 토큰을 받은 주소로 남는 경우[3], 오류 코드를 다룹니다.
2. [감사 로그 (Audit Logs)](audit-logs.md) — 디렉터리 변경 기록의 구조와 주요 활동 이름. 누가 무엇을 바꿨는지(`initiatedBy`, `targetResources`)를 읽는 법을 다룹니다.
3. [위험 탐지 (Identity Protection)](identity-protection.md) — 위험 탐지 유형과 라이선스별로 보이는 범위. P2 가 없으면 대부분의 탐지가 상세 없이 `generic`("Additional risk detected") 으로만 보입니다[9].

## 함께 볼 페이지

로그인 뒤에 메일·파일에서 한 일은 [통합 감사 로그](../unified-audit-log/index.md) 와 [Exchange Online](../exchange-online/index.md) 에서 찾습니다. Graph 활동 로그의 `SignInActivityId` 를 로그인 로그의 `UniqueTokenIdentifier` 와 맞추면 어느 로그인으로 받은 토큰이 어떤 API 요청을 했는지 이을 수 있습니다[7]. 이 연결은 [토큰과 세션](../../../01-foundations/identity/tokens-sessions.md) 을 알면 이해하기 쉽습니다.

- [다단계 인증과 조건부 접근](../../../01-foundations/identity/mfa-conditional-access.md)
- [OAuth 앱과 동의](../../../01-foundations/identity/oauth-consent.md)
- [IP·사용자 에이전트·위치 정보](../../../01-foundations/logging/ip-ua-geo.md)
- [이상한 로그인 가려내기](../../../03-techniques/analysis/suspicious-sign-ins.md)
- [권한 변화 따라가기](../../../03-techniques/analysis/permission-changes.md)
- [클라우드 타임라인](../../../03-techniques/analysis/timeline.md)
- [Defender 경고와 기록](../defender-xdr.md)

## 참고 문헌

1. Microsoft, "Microsoft Entra data retention" (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
2. Microsoft, "What are Microsoft Entra sign-in logs?" (ms.date 2025-11-07). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-ins.md
3. Microsoft, "Non-interactive user sign-ins" (ms.date 2026-02-09). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-noninteractive-sign-ins.md
4. Microsoft, "What are Microsoft Entra audit logs?" (ms.date 2026-06-05). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-audit-logs.md
5. Microsoft, "How to download logs in Microsoft Entra ID" (ms.date 2024-11-08). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/howto-download-logs.md
6. Microsoft, "Microsoft Entra activity log integration options and considerations" (ms.date 2025-05-27). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-log-monitoring-integration-options-considerations.md
7. Microsoft, "Microsoft Graph activity logs" (갱신 2026-07-04). https://learn.microsoft.com/en-us/graph/microsoft-graph-activity-logs-overview
8. Microsoft, "Office 365 Management Activity API schema" (갱신 2026-08-26). https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
9. Microsoft, "What are risk detections?" (갱신 2026-04-22). https://learn.microsoft.com/en-us/entra/id-protection/concept-identity-protection-risks
10. invictus-ir, Microsoft-Extractor-Suite, `Scripts/Get-AzureEntraGraphLogs.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureEntraGraphLogs.ps1
11. CISA, Untitled Goose Tool, `goosey/entra_id_datadumper.py`. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/entra_id_datadumper.py
12. ANSSI-FR, DFIR-O365RC, `README.md`. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/README.md
13. Microsoft, "SigninLogs" (Azure Monitor Logs 표 참조, 갱신 2026-08-27). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
14. Microsoft, "AADNonInteractiveUserSignInLogs" (Azure Monitor Logs 표 참조, 갱신 2026-08-27). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadnoninteractiveusersigninlogs
15. Microsoft, "signIn resource type" (Microsoft Graph v1.0, 갱신 2025-11-28). https://learn.microsoft.com/en-us/graph/api/resources/signin
16. Microsoft, "Learn about the sign-in log activity details" (ms.date 2026-03-04). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
