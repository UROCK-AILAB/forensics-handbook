---
title: "MFA 피로 공격을 당했나"
parent: "시나리오 · 계정 침해"
nav_order: 760
---

# MFA 피로 공격을 당했나 (MFA Fatigue)

비밀번호를 가진 누군가가 다단계 인증 (MFA) 푸시 요청을 거듭 보내 사용자가 결국 승인하게 만들었는지를 로그로 가려내는 순서를 다룹니다. Microsoft Entra ID, Okta, Google Workspace 를 중심으로 쓰고, Azure·Google Cloud·AWS 콘솔처럼 이 계정으로 들어가는 서비스는 로그인한 뒤의 흔적을 이어서 봅니다.

## 조사 질문

- 사용자가 요청하지 않은 MFA 요청이 짧은 간격으로 여러 번 갔나?
- 그 요청들은 어떻게 끝났나(거부, 무응답, 승인)?
- 승인된 요청이 있다면 그 로그인은 어느 IP·장치·앱에서 시작됐고, 그 뒤 무엇을 했나?
- 사용자가 요청을 의심 활동으로 신고했나?
- 승인 뒤에 새 인증 방법을 등록하거나 MFA 설정을 바꿨나?

MFA 요청이 갔다는 것은 1차 인증(대개 비밀번호)을 이미 통과했다는 뜻이어서, 탐지 규칙도 이 상황을 "공격자가 비밀번호를 가졌을 수 있다" 는 신호로 봅니다[10][11]. 비밀번호가 어디서 새었는지는 로그인 로그 밖의 질문입니다.

## 먼저 확인할 것

**사건 당시 사용자가 본 화면을 정합니다.** Entra 에서는 Authenticator 푸시 알림 전부에 숫자 일치 (number matching) 가 적용되어, 사용자가 로그인 화면의 숫자를 앱에 넣어야 승인됩니다[1]. 다만 예외가 있어서 사용자가 "승인" 만 누르는 화면이었을 수도 있습니다.

| 경로 | 사용자가 본 응답 방식 |
|---|---|
| 브라우저(Edge·Chrome·Safari) 로그인 | 숫자 입력[1] |
| Authenticator 와 같은 장치에서 Teams·Outlook 같은 Microsoft 앱으로 로그인 | 숫자 대신 Yes/No[1] |
| AD FS 어댑터, Windows Server 에 숫자 일치 업데이트(2022 KB5007205, 2019 KB5007206, 2016 KB5006669)가 없을 때 | Approve/Deny[1] |
| NPS 확장 1.2.2216.1 이상 | TOTP 코드 입력. TOTP 방법을 등록하지 않은 사용자는 Approve/Deny[1] |
| NPS 확장 1.0.1.40 이전 | Approve/Deny[1] |
| Apple Watch·Android 웨어러블 | 숫자 일치를 지원하지 않아 휴대폰에서 승인[1] |

**기록이 남는 기간을 확인합니다.** 요청이 수십 번 반복돼도 보관 기간이 지나면 남지 않습니다. 아래 표는 2026년 9월 문서 기준이고, 전체 표는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 에 있습니다. 로그를 먼저 확보하는 방법은 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 에 있습니다.

| 서비스 | 기록 | 기본 보관 |
|---|---|---|
| Microsoft Entra | 로그인 로그·감사 로그 | Free 7일, P1·P2 30일. Free 에서 P1 으로 올려도 지난 기록은 7일치만 보임[8] |
| Microsoft Entra | MFA 사용 기록 | 모든 판 30일[8] |
| Microsoft Entra | 위험한 로그인 | Free 7일, P1 30일, P2 90일. 위험한 사용자는 위험이 해소될 때까지 남음[8] |
| Okta | 시스템 로그 | 90일이 넘은 기록은 API 가 돌려주지 않음[14] |
| Google Workspace | 사용자 로그 이벤트(예전 이름 Login audit log) | 6개월[17] |

**의심 활동 신고 기능이 켜져 있었는지 봅니다.** Entra 의 의심 활동 신고 (Report suspicious activity) 는 Entra ID > Authentication methods > Settings 에서 켜고, 값이 Microsoft managed 이면 꺼진 상태입니다[2]. 이 기능은 2025년 3월 1일에 없어진 옛 기능(Block/unblock users, Fraud alert, Notifications)을 대신합니다[2]. 꺼져 있었다면 사용자가 거부해도 신고 기록은 생기지 않습니다[3].

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | Entra 로그인 로그의 MFA 단계(`authenticationDetails`, `status`, `ResultType`) | 요청 횟수, 단계마다 거부·무응답·성공, 시도한 IP·앱 | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md) |
| 2 | Entra ID Protection 위험 탐지 | 사용자 신고(`userReportedSuspiciousActivity`), 수상한 MFA 승인(`authenticatorPhishing`) | [이상한 로그인 가려내기](../../03-techniques/analysis/suspicious-sign-ins.md) |
| 3 | Okta 시스템 로그 | 푸시 발송, 거부, MFA 성공·실패, 사용자 신고 | [Okta 시스템 로그](../../02-artifacts/saas/okta.md) |
| 4 | Google Workspace 로그인 기록 | 로그인 확인 요청 방법과 결과 | [로그인 기록](../../02-artifacts/google-workspace/login-audit.md) |
| 5 | Entra 감사 로그, Okta·Google 의 인증 방법 변경 이벤트 | 승인 뒤 새 인증 방법 등록, MFA 설정 변경 | [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md) |
| 6 | 승인 뒤 활동: UAL, CloudTrail, 관리 콘솔 기록 | 로그인한 뒤 한 일 | [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md), [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md) |

## 분석 흐름

1. **사용자 한 명의 로그인 기록을 시각 순으로 뽑습니다.** Graph 로 받을 때는 beta `signIn` 리소스를 씁니다. v1.0 리소스에는 `authenticationDetails`·`authenticationRequirement` 가 없습니다[6][22]. beta 도 필터를 주지 않으면 대화형 로그인만 돌려주고, 비대화형 로그인은 `signInEventTypes/any(t: t eq 'nonInteractiveUser')` 로 따로 받아야 합니다[6]. Microsoft-Extractor-Suite 의 `Get-AzureEntraGraphLogs` 는 이 필터를 유형별로 넣어 받습니다[19]. 수집 도구 비교는 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md) 에 있습니다.

2. **MFA 단계만 추려 결과를 셉니다.** `authenticationDetails` 의 각 단계에는 `authenticationMethod`(Password, SMS, Voice, Authenticator App 등), `authenticationStepDateTime`, `authenticationStepResultDetail`, `succeeded` 가 있습니다[5]. `authenticationStepResultDetail` 에는 "no phone input - timed out", "fraud code entered", "user is blocked" 같은 이유가 들어갑니다[5]. 사용자가 요청을 신고하면 결과 상세가 "MFA denied" 로 나옵니다[2]. 아래는 한 계정에 무응답이 이어지다 승인으로 끝난 모양을 보이려고 만든 예시입니다.

    | createdDateTime (UTC) | ipAddress | authenticationMethod | authenticationStepResultDetail | succeeded |
    |---|---|---|---|---|
    | 2026-09-10T01:12:04Z | 203.0.113.24 | Authenticator App | no phone input - timed out | false |
    | 2026-09-10T01:14:40Z | 203.0.113.24 | Authenticator App | no phone input - timed out | false |
    | 2026-09-10T01:17:15Z | 203.0.113.24 | Authenticator App | MFA denied | false |
    | 2026-09-10T01:31:02Z | 203.0.113.24 | Authenticator App | — | true |

    한 번의 로그인 시도 안에서도 MFA 이벤트가 여러 개 생깁니다. Entra 관리 센터에는 한 줄로 보이지만 Azure Monitor(Log Analytics)에는 `correlationId` 가 같은 여러 줄로 들어갑니다[4]. 푸시 횟수를 셀 때는 어느 화면·표에서 셌는지 함께 적습니다.

3. **오류 코드로 실패의 종류를 나눕니다.** `ResultType` 0 은 성공이고 나머지는 실패입니다[21]. MFA 와 관련된 코드는 50074(강한 인증이 필요한데 MFA 를 통과하지 못함), 50076(MFA 가 필요해 다시 요청), 50079(MFA 등록이 필요함)이고, 50126 은 비밀번호가 틀린 경우입니다[7]. 50158 은 추가 확인 페이지로 넘어갔다는 뜻일 뿐 그것만으로 실패가 아닙니다[7]. Sigma 규칙 `azure_mfa_interrupted` 는 50074 와 함께 `ResultType: 500121`, `ResultDescription` 에 "Authentication failed during strong authentication request" 가 든 기록을 찾지만[11], Microsoft 오류 코드 목록 페이지에는 500121 이 없어서[7] 검체의 `ResultDescription` 문구로 뜻을 확인합니다. `azure_mfa_denies` 규칙은 `AuthenticationRequirement` 가 `multiFactorAuthentication` 이고 `Status` 에 "MFA Denied" 가 든 기록을 찾습니다[10]. 규칙을 로그에 돌리는 방법은 [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md) 에 있습니다.

4. **1차 인증이 통과됐는지 확인합니다.** MFA 가 필요한 로그인이라도 1차 인증이 실패하면 조건부 접근이 MFA 요구를 평가하지 않아서 `authenticationRequirement` 가 `singleFactorAuthentication` 으로 남습니다[4]. 이런 시도에는 푸시가 가지 않았으므로 요청 횟수에서 뺍니다. 조건부 접근과 MFA 요구의 관계는 [다단계 인증과 조건부 접근](../../01-foundations/identity/mfa-conditional-access.md) 에 있습니다.

5. **위험 탐지를 봅니다.** 사용자가 요청을 의심 활동으로 신고하면 사용자 위험이 High 가 되고, 위험 탐지 보고서에 Detection type "User Reported Suspicious Activity"(Source: End user reported)로, Graph 에는 `riskEventType` `userReportedSuspiciousActivity` 로 남으며, 감사 로그의 Activity type 에도 나옵니다[2]. 비밀번호 없는 인증을 쓴 사용자는 High 로 올라가지 않습니다[2]. `authenticatorPhishing`(Suspicious MFA authentication approval)은 낯선 ASN·브라우저·장치·GPS 위치, 인증을 요청한 장치와 승인한 장치 사이의 거리를 보고 실시간으로 High 위험을 매기는 탐지이고 P2 가 필요합니다[3]. 라이선스 조건은 문서마다 다르게 적혀 있습니다.

    | 문서 | `userReportedSuspiciousActivity` 조건 |
    |---|---|
    | MFA 설정 문서 | P1 테넌트에서도 위험 탐지 보고서·로그인 로그·감사 로그에 나옴[2] |
    | 위험 탐지 문서 | Premium, 라이선스 P2, 오프라인 계산[3] |

    Free·P1 테넌트에서는 프리미엄 탐지가 `generic` 으로만 보입니다[3]. 테넌트에서 실제로 무엇이 보이는지는 ID Protection > Dashboard > Risk detection 화면이나 Graph `riskDetection` 으로 확인합니다[2]. Untitled Goose Tool 은 `identityProtection/riskDetections`·`identityProtection/riskyUsers` 를 받아 둡니다[20].

6. **Okta 와 Google Workspace 를 씁니다.** Okta 는 푸시를 보낼 때마다 `system.push.send_factor_verify_push` 를 남깁니다[13]. 거부는 조직의 엔진에 따라 이름이 다릅니다. Classic(V1 API)에서는 `user.mfa.okta_verify.deny_push` 이고, Identity Engine(OIE)에서는 `user.authentication.auth_via_mfa` 에 이유 `INVALID_CREDENTIALS` 로 남습니다[13]. `user.authentication.auth_via_mfa` 는 Classic 에서는 2차 인증에만, OIE 에서는 1차·2차 인증 모두에 생깁니다[13]. 사용자가 신고하면 `user.account.report_suspicious_activity_by_enduser` 가 남고[13][15], ThreatInsight 가 악성 IP 로 판단한 요청은 `security.threat.detected` 로 남습니다[13]. 시각 순으로 정렬할 때는 경계 있는 요청(since·until)을 씁니다. 폴링 요청은 내부 저장 시각 순이라 `published` 순서와 다를 수 있습니다[14].

    Google Workspace 에서는 `login_challenge` 이벤트의 `login_challenge_method` 가 확인 방법(`google_prompt`, `google_authenticator`, `security_key`, `passkey`, `backup_code` 등)을, `login_challenge_status` 가 결과("Challenge Passed." 또는 "Challenge Failed.", 빈 문자열은 알 수 없음)를 남깁니다[16]. `login_verification` 의 `is_second_factor` 는 2단계 인증 여부를 알려 줍니다[16]. 사용자가 Google 메시지(`google_prompt`)를 거부한 흔적은 `google_prompt` 이면서 "Challenge Failed." 인 기록이 짧은 간격으로 이어지는지로 검체에서 확인합니다. 로그인 이벤트는 몇 분 안에 조회됩니다[17].

7. **승인된 로그인 하나를 골라 뒤를 따라갑니다.** 성공한 로그인의 IP·장치·앱이 실패가 이어지던 시도와 같은지 봅니다. 같은 IP 에서 실패가 이어지다 성공으로 끝났다면 같은 시도자가 승인을 받아 낸 것일 가능성이 있습니다. 그 로그인의 `sessionId` 로 뒤이은 비대화형 로그인과 메일·파일 활동을 잇는 방법은 [토큰을 훔쳐 로그인했나](token-theft.md) 에, 메일함 규칙·전달 설정을 보는 순서는 [메일 계정을 빼앗겨 송금 사기를 당했나](bec.md) 에 있습니다. Azure 포털은 Entra 로그인을, Google Cloud 콘솔은 Google 계정 로그인을 거치므로 같은 기록에서 시작합니다. AWS 콘솔 로그인은 CloudTrail `ConsoleLogin` 의 `additionalEventData.MFAUsed`(Yes/No)와 `MFAIdentifier` 로 MFA 를 썼는지 남깁니다[18]. 이 값은 IAM 사용자나 루트 사용자가 MFA 를 썼을 때만 Yes 가 되고 페더레이션 사용자는 No 로 남으므로[18], 페더레이션으로 들어왔다면 MFA 요청은 연결된 ID 공급자의 로그에서 찾습니다.

8. **승인 뒤 발판을 만들었는지 봅니다.** Entra 감사 로그에서 `User registered security info`, `User changed default security info`, `Admin registered security info`, `Update per-user multifactor authentication state`, `Restore multifactor authentication on all remembered devices`, `Authentication Methods Policy Update` 를 찾습니다[9]. Sigma `azure_change_to_authentication_method` 는 `LoggedByService: 'Authentication Methods'`, `OperationName: 'User registered security info'` 로 새 인증 방법 등록을 찾습니다[12]. Okta 에서는 `user.mfa.factor.activate`·`user.mfa.factor.deactivate`·`user.mfa.factor.reset_all` 을[13], Google Workspace 에서는 `2sv_enroll`·`2sv_disable` 을 봅니다[16].

9. **한 타임라인으로 합칩니다.** Entra 의 `createdDateTime`·`authenticationStepDateTime` 은 UTC 입니다[5][6]. 서비스마다 시각 표기와 늦게 들어오는 정도가 달라서 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 과 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 의 방법으로 합칩니다. IP 의 위치 정보를 해석할 때는 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md) 를 봅니다.

## 흔한 오판

**거부 한 번을 공격으로 봅니다.** 사용자가 로그인하다가 실수로 거부를 누르는 일이 있어서, Sigma 규칙도 이를 오탐 사례로 적어 둡니다[10]. 피로 공격으로 볼 근거는 사용자가 로그인하지 않은 시간대에 같은 IP 에서 요청이 짧은 간격으로 이어지는 모양입니다.

**화면에 따라 요청 횟수가 달라집니다.** 관리 센터의 한 줄이 Log Analytics 에서는 여러 줄이 됩니다[4]. 두 값을 섞어 쓰면 횟수가 부풀거나 줄어듭니다.

**숫자 일치가 켜져 있으니 피로 공격이 불가능하다고 봅니다.** 같은 장치의 Microsoft 앱 로그인, 업데이트 전 AD FS 어댑터, 옛 NPS 확장에서는 Yes/No 나 Approve/Deny 로 응답합니다[1]. 사건 당시 로그인이 어느 경로였는지 로그인 기록의 앱·프로토콜로 확인합니다.

**신고 기록이 없으니 사용자가 신고하지 않았다고 봅니다.** 신고 기능이 꺼져 있으면 탐지가 생기지 않고[3], 사용자 정의 인사말이 없으면 전화로 신고하는 코드는 0 입니다[2]. 기능 설정과 사용자 진술을 함께 봅니다.

**Okta 에 `deny_push` 가 없으니 거부가 없었다고 봅니다.** OIE 조직에서는 거부가 `user.authentication.auth_via_mfa` 의 실패로 남습니다[13].

**50158 을 실패로 셉니다.** 이 코드 하나만으로는 사용자가 로그인에 실패한 것이 아닙니다[7].

## 보고서 문장 예

기록이 말하는 만큼만 씁니다. 아래 값은 모두 만든 예시입니다.

- "2026-09-10 01:12부터 01:31(UTC)까지 IP 203.0.113.24 에서 계정 kim@contoso.com 으로 로그인을 시도한 기록이 4건 있습니다. 앞의 3건은 Authenticator App 단계에서 실패했고(결과 상세 no phone input - timed out 2건, MFA denied 1건), 01:31 의 시도는 같은 단계가 성공으로 기록되어 있습니다."
- "01:17 의 거부는 위험 탐지 보고서에 User Reported Suspicious Activity 로 남아 있습니다."
- "이 기록만으로는 사용자가 요청의 출처를 알고 승인했는지, 실수로 승인했는지 알 수 없습니다. 비밀번호가 새어 나간 경로도 이 기록에 나타나지 않습니다."

보고서 틀은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- [토큰과 세션](../../01-foundations/identity/tokens-sessions.md) — 승인 뒤 받은 토큰이 얼마나 오래 쓰이는지
- [토큰을 훔쳐 로그인했나](token-theft.md) — 승인된 세션이 다른 곳에서 다시 쓰였는지
- [메일 계정을 빼앗겨 송금 사기를 당했나](bec.md) — 로그인 뒤 메일함에서 한 일
- [악성 OAuth 앱에 동의했나](illicit-consent.md) — 로그인 뒤 앱 동의로 발판을 만든 경우
- [이상한 로그인 가려내기](../../03-techniques/analysis/suspicious-sign-ins.md)

## 참고 문헌

1. Microsoft, "How number matching works in multifactor authentication push notifications for Microsoft Authenticator" (2025-11-06). https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-mfa-number-match
2. Microsoft, "Configure Microsoft Entra multifactor authentication settings" (2026-02-27). https://learn.microsoft.com/en-us/entra/identity/authentication/howto-mfa-mfasettings
3. Microsoft, "What are risk detections?" (2026-04-22). https://learn.microsoft.com/en-us/entra/id-protection/concept-identity-protection-risks
4. Microsoft, "Sign-in log activity details" (concept-sign-in-log-activity-details.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
5. Microsoft, "authenticationDetail resource type" (Microsoft Graph beta). https://learn.microsoft.com/en-us/graph/api/resources/authenticationdetail?view=graph-rest-beta
6. Microsoft, "signIn resource type" (Microsoft Graph beta). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
7. Microsoft, "Microsoft Entra authentication and authorization error codes" (2025-02-03). https://learn.microsoft.com/en-us/entra/identity-platform/reference-error-codes
8. Microsoft, "Microsoft Entra data retention" (reference-reports-data-retention.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
9. Microsoft, "Microsoft Entra audit log activity reference" (reference-audit-activities.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
10. SigmaHQ, azure_mfa_denies.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/signin_logs/azure_mfa_denies.yml
11. SigmaHQ, azure_mfa_interrupted.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/signin_logs/azure_mfa_interrupted.yml
12. SigmaHQ, azure_change_to_authentication_method.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/audit_logs/azure_change_to_authentication_method.yml
13. Okta, "Event types" (okta-event-types.csv). https://developer.okta.com/docs/okta-event-types.csv
14. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
15. SigmaHQ, okta_suspicious_activity_enduser_report.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/identity/okta/okta_suspicious_activity_enduser_report.yml
16. Google, "Login Audit Activity Events", Admin SDK Reports API (2026-09-03). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/login
17. Google, "Data retention and lag times", Google Workspace Admin Help. https://support.google.com/a/answer/7061566?hl=en
18. AWS, "AWS Management Console sign-in events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-aws-console-sign-in-events.html
19. Invictus Incident Response, Microsoft-Extractor-Suite, Scripts/Get-AzureEntraGraphLogs.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-AzureEntraGraphLogs.ps1
20. CISA, Untitled Goose Tool, goosey/entra_id_datadumper.py. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/entra_id_datadumper.py
21. Microsoft, "SigninLogs" table reference, Azure Monitor. https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
22. Microsoft, "signIn resource type" (Microsoft Graph v1.0). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-1.0
