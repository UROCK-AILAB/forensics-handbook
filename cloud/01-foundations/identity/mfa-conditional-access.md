---
title: "다단계 인증과 조건부 접근"
parent: "기반 · 계정과 인증"
nav_order: 60
---

# 다단계 인증과 조건부 접근 (MFA·Conditional Access)

다단계 인증 기록은 한 로그인이 MFA 를 요구받았는지, 어떤 방법으로 통과하거나 실패했는지, 이미 받은 클레임으로 넘어갔는지를 구분해 주고, 조건부 접근 기록은 그 로그인에 어떤 정책이 평가됐고 결과가 무엇이었는지를 알려 줍니다. 인증 방법을 새로 등록하거나 정책을 바꾼 기록은 침해 뒤 접근을 이어 가려는 흔적일 수 있어서 따로 찾아봅니다.

## 이 형식을 쓰는 아티팩트

다단계 인증 (multifactor authentication, MFA) 은 아는 것(비밀번호), 가진 것(휴대폰·하드웨어 키), 몸의 특징(지문·얼굴) 가운데 둘 이상으로 신원을 확인합니다[1]. 조건부 접근 (Conditional Access) 은 사용자·앱·위치·기기·위험도 같은 조건에 따라 MFA 를 요구하거나 접근을 막는 정책입니다[1][4]. 이 흔적은 서비스마다 세 곳에 나뉘어 남습니다.

| 서비스 | 로그인 때 MFA·정책 결과 | 인증 방법 등록·변경 | 정책 변경 |
|---|---|---|---|
| Microsoft Entra ID | [로그인 로그](../../02-artifacts/m365/entra-logs/index.md)의 `authenticationDetails`·`authenticationRequirement`·`conditionalAccessStatus` | Entra 감사 로그(서비스 Authentication Methods·Core Directory) | Entra 감사 로그(서비스 Conditional Access) |
| AWS | [CloudTrail](../../02-artifacts/aws/cloudtrail/index.md) `ConsoleLogin` 의 `additionalEventData.MFAUsed` | CloudTrail `EnableMFADevice` 등 | IAM 정책 조건([IAM](../../02-artifacts/aws/iam.md) 페이지) |
| Google Workspace | [로그인 기록](../../02-artifacts/google-workspace/login-audit.md)의 `login_challenge_method` | 로그인 기록 `2sv_enroll`·`passkey_enrolled`, 관리 감사의 사용자 설정 | [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md)의 보안 설정 |
| Okta | [시스템 로그](../../02-artifacts/saas/okta.md) `user.authentication.auth_via_mfa` | `user.mfa.factor.*` | `policy.lifecycle.*`·`policy.rule.*` |
| Slack | 해당 없음 | 해당 없음 | [감사 로그](../../02-artifacts/saas/slack.md) `pref.two_factor_auth_changed` |

외부 IdP 로 로그인을 넘기는 페더레이션 사용자는 MFA 를 IdP 에서 하므로 MFA 흔적도 IdP 쪽에 남습니다[11][12]. 이 경우는 [페더레이션과 SSO](federation-sso.md)에서 다룹니다. 토큰에 MFA 클레임이 실려 다음 로그인으로 넘어가는 구조는 [토큰과 세션](tokens-sessions.md)에 있습니다.

## 구조

### Microsoft Entra ID — MFA 를 켜는 방법과 인증 방법

Entra 에서 MFA 를 켜는 방법은 보안 기본값 (security defaults), 조건부 접근 정책, 사용자별 MFA (per-user MFA) 셋이고, 조건부 접근을 쓸 수 있으면 사용자별 MFA 는 권장하지 않습니다[1][2]. 조건부 접근은 Entra ID P1·P2 기능이고, 보안 기본값은 조건부 접근이 없는 Free 테넌트용입니다[2]. 쓸 수 있는 인증 방법은 Microsoft Authenticator, Authenticator Lite, Windows Hello for Business, 패스키(FIDO2), Authenticator 안 패스키, QR 코드, 인증서 기반 인증(MFA 로 설정한 경우), 외부 MFA, 임시 액세스 패스 (Temporary Access Pass, TAP), OATH 하드웨어·소프트웨어 토큰, SMS, 음성 통화입니다[1].

사용자별 MFA 상태는 `Disabled`(기본), `Enabled`, `Enforced` 셋입니다[2]. `Enabled` 인 사용자는 레거시 인증에 비밀번호를 계속 쓸 수 있고, 등록을 마치면 자동으로 `Enforced` 로 바뀌며, `Enforced` 에서는 레거시 앱에 앱 비밀번호가 필요합니다[2]. 조건부 접근으로 MFA 를 요구해도 이 상태는 바뀌지 않아서, 조건부 접근을 쓰는 테넌트에서는 사용자가 `Disabled` 로 보이는 것이 정상입니다[2]. 현재 상태는 Graph beta 의 `GET /users/{id}/authentication/requirements` 응답에 있는 `perUserMfaState` 로 확인합니다[2].

### Microsoft Entra ID — 감사 로그 작업 이름

인증 방법과 정책을 바꾸면 Entra 감사 로그에 아래 작업 이름으로 남습니다[3].

| 서비스(감사 로그) | 범주 | 작업 이름 |
|---|---|---|
| Authentication Methods | UserManagement | User registered security info, User updated security info, User deleted security info, User changed default security info, User registered all required security info, User started security info registration, User canceled security info registration, User reviewed security info, Admin registered security info, Admin updated security info, Admin deleted security info, Update per-user multifactor authentication state |
| Authentication Methods | ApplicationManagement | Authentication Methods Policy Update, Authentication Methods Policy Reset, Authentication Strength Policy Create·Update·Delete, MFA Service Policy Update |
| Core Directory | UserManagement | Disable Strong Authentication, Enable Strong Authentication, Create application password for user, Delete application password for user |
| Device Registration Service | UserManagement | Add Passkey (device-bound), Add Windows Hello for Business credential, Add passwordless phone sign-in credential 와 각각의 Delete 짝 |
| Microsoft Entra (Azure MFA) | UserManagement | Fraud reported - user is blocked for MFA, Fraud reported - no action taken |
| Conditional Access | Policy | Add·Update·Delete Conditional Access policy, Add·Update·Delete named location, Add·Update·Delete AuthenticationContextClassReference, Update continuous access evaluation, Update security defaults |

조건부 접근 정책을 바꾼 레코드의 Modified Properties(Log Analytics 에서는 `TargetResources` 아래 `modifiedProperties`)에는 바꾸기 전과 뒤의 정책이 JSON 으로 들어 있습니다[4]. 이 JSON 에는 `displayName`, `conditions.applications.includeApplications`, `conditions.clientAppTypes`, `conditions.users.includeUsers`·`excludeGroups`, `grantControls.builtInControls`(예: `["mfa"]`), `modifiedDateTime` 같은 키가 있어서 두 값을 비교하면 무엇을 바꿨는지 알 수 있습니다[4].

### Microsoft Entra ID — 로그인 로그의 MFA·조건부 접근 필드

| 필드(Graph) | 값 | 뜻 |
|---|---|---|
| `authenticationRequirement` | `singleFactorAuthentication`, `multiFactorAuthentication` | 로그인이 도달한 인증 단계. 1차 인증이 실패하면 조건부 접근 평가 전이라 `singleFactorAuthentication`[5] |
| `authenticationRequirementPolicies` | 목록 | MFA 를 요구한 원천(조건부 접근, 사용자별 MFA, ID Protection, 보안 기본값)[5] |
| `authenticationDetails[].authenticationMethod` | Password, SMS, Voice, Authenticator App, Software OATH token, Satisfied by token, Previously satisfied | 그 단계에 쓴 방법[6] |
| `authenticationDetails[].authenticationMethodDetail` | 전화번호, 기기 이름, 비밀번호 원천(cloud·AD FS·PTA·PHS) | 방법의 세부[6] |
| `authenticationDetails[].authenticationStepRequirement` | primary authentication, multifactor authentication | 이 단계가 채운 요구[6] |
| `authenticationDetails[].authenticationStepResultDetail` | user is blocked, fraud code entered, no phone input - timed out, phone unreachable, claim in token 등 | 성공·실패 이유[6] |
| `authenticationDetails[].succeeded` | true·false | 단계 결과[6] |
| `authenticationMethodsUsed` | SMS, Authenticator App, App Verification code, Password, FIDO, PTA, PHS | 쓴 방법 목록[5] |
| `conditionalAccessStatus` | `success`, `failure`, `notApplied`, `unknownFutureValue` | 조건부 접근 결과[5] |
| `appliedConditionalAccessPolicies` | 목록 | 평가된 정책별 결과. 읽으려면 앱에 조건부 접근 관련 권한이 더 필요[5] |

`mfaDetail` 은 폐기된 필드입니다[5][7]. Log Analytics 로 옮긴 표에서는 `ConditionalAccessPolicies` 열이 대화형 로그인 표 `SigninLogs` 에서는 dynamic, 비대화형 로그인 표 `AADNonInteractiveUserSignInLogs` 에서는 string 이라서 같은 쿼리를 두 표에 그대로 쓰면 안 됩니다[7][8]. OATH 하드웨어 토큰과 소프트웨어 토큰은 둘 다 "OATH verification code" 로 기록됩니다[9].

포털의 정책별 결과는 Success, Failure, Not Applied, Disabled 이고, Disabled 는 로그인 때 정책이 꺼져 있었다는 뜻입니다[9]. 로그인 전체의 조건부 접근 상태가 Success 이면 정책 하나 이상이 그 사용자·앱에 적용되거나 평가됐다는 뜻이고, 다른 조건까지 모두 맞았다는 뜻은 아닙니다[9]. 기기 등록·규정 준수·NPS 커넥터처럼 조건부 접근을 먼저 거칠 수 없는 로그인과 Windows Hello for Business 의 Windows 로그인은 Not Applied 로 나옵니다[9].

보고 전용 (report-only) 정책은 평가만 하고 강제하지 않으며, 결과는 Report-only: Success, Report-only: Failure, Report-only: User action required, Report-only: Not applied 가운데 하나로 로그인 상세의 Conditional Access 탭과 Report-only 탭에 남습니다[10]. "User Actions" 범위 정책은 보고 전용으로 평가할 수 없습니다[10]. 정책 객체의 상태 값은 `enabled`, `disabled`, `enabledForReportingButNotEnforced` 입니다[25].

아래는 비밀번호 뒤 Authenticator 로 MFA 를 한 로그인을 Graph 스키마로 만든 예시입니다. 계정·IP·시각은 지어낸 값이고, 문자열 값의 대소문자는 실제 로그에서 확인합니다.

```json
{
  "createdDateTime": "2026-09-01T01:02:03Z",
  "userPrincipalName": "user@contoso.com",
  "ipAddress": "203.0.113.10",
  "authenticationRequirement": "multiFactorAuthentication",
  "conditionalAccessStatus": "success",
  "authenticationDetails": [
    {
      "authenticationStepDateTime": "2026-09-01T01:02:03Z",
      "authenticationMethod": "Password",
      "authenticationStepRequirement": "Primary authentication",
      "succeeded": true
    },
    {
      "authenticationStepDateTime": "2026-09-01T01:02:21Z",
      "authenticationMethod": "Authenticator App",
      "authenticationStepRequirement": "Multifactor authentication",
      "succeeded": true
    }
  ]
}
```

### Microsoft Entra ID — 오류 코드

로그인 레코드의 결과 코드로 MFA·조건부 접근 때문에 멈춘 로그인을 가를 수 있습니다[11].

| 코드 | 이름 | 뜻 |
|---|---|---|
| 50074 | UserStrongAuthClientAuthNRequiredInterrupt | 강한 인증이 필요한데 MFA 를 통과하지 못함 |
| 50076 | UserStrongAuthClientAuthNRequired | 조건부 접근·사용자별 적용·위치 이동 등으로 MFA 가 필요 |
| 50072·50079 | UserStrongAuthEnrollmentRequired(Interrupt) | 두 번째 요소 등록이 필요 |
| 53003 | BlockedByConditionalAccess | 조건부 접근 정책이 토큰 발급을 막음 |
| 70043 | BadTokenDueToSignInFrequency | 로그인 빈도 검사로 새로 고침 토큰이 만료·무효 |

결과 코드 500121 은 설명 문자열이 "Authentication failed during strong authentication request" 이고, 50074 와 함께 MFA 를 통과하지 못한 로그인을 찾을 때 씁니다[21].

### AWS

콘솔 로그인 레코드(`eventName` 이 `ConsoleLogin`)의 `additionalEventData` 에 `MFAUsed`(`Yes`·`No`)와 MFA 를 썼을 때의 `MFAIdentifier`(MFA 장치 ARN)가 있고, `userIdentity.sessionContext.attributes.mfaAuthenticated` 에도 MFA 여부가 남습니다[12]. 두 값은 IAM 사용자나 루트 사용자가 MFA 를 쓴 요청에만 참이 되고, 페더레이션 사용자의 요청이면 `mfaAuthenticated` 는 `false`, `MFAUsed` 는 `No` 입니다[12]. MFA 장치를 붙이면 `EnableMFADevice` 이벤트가 남고 `requestParameters.serialNumber` 에 장치 ARN 이 들어갑니다[12]. MFA 를 요구하는 역할을 넘겨받을 때는 `AssumeRole` 에 MFA 장치를 가리키는 `SerialNumber` 와 장치가 만든 TOTP 인 `TokenCode` 를 넘깁니다[13]. IAM 사용자·역할별 MFA 기록은 [IAM](../../02-artifacts/aws/iam.md) 페이지에서 다룹니다.

### Google Workspace

로그인 기록(`applicationName=login`)의 MFA 관련 이벤트는 다음과 같습니다[14].

| 이벤트 | 뜻 |
|---|---|
| `2sv_enroll`, `2sv_disable` | 사용자가 2단계 인증을 등록·해제 |
| `passkey_enrolled`, `passkey_removed` | 패스키 등록·제거 |
| `titanium_enroll`, `titanium_unenroll` | 고급 보호 프로그램 등록·해제 |
| `login_challenge` | 로그인 세션 안의 챌린지. 세션 하나의 챌린지를 한 항목으로 묶음 |
| `login_verification` | 신원 확인. `is_second_factor` 가 2단계 인증인지 알려 줌 |

매개변수 `login_challenge_method` 에는 `password`, `google_authenticator`, `google_prompt`, `security_key`, `security_key_otp`, `passkey`, `backup_code`, `idv_preregistered_phone`, `offline_otp`, `device_prompt`, `saml`, `oidc` 같은 값이 여럿 들어가고, `login_challenge_status` 는 "Challenge Passed." 또는 "Challenge Failed." 입니다[14]. 비밀번호를 두 번 틀린 뒤 맞히고 보안 키로 2단계 인증을 한 로그인은 `login_success` 한 항목의 `login_challenge_method` 에 `password`, `password`, `password`, `security_key` 가 차례로 들어갑니다[14].

관리 감사(`applicationName=admin`)의 보안 설정에는 2단계 인증 허용·강제(`ALLOW_STRONG_AUTHENTICATION`, `ENFORCE_STRONG_AUTHENTICATION`), 허용 방법 변경(`CHANGE_ALLOWED_TWO_STEP_VERIFICATION_METHODS`), 등록 기간·빈도·유예 기간·시작일 변경(`CHANGE_TWO_STEP_VERIFICATION_ENROLLMENT_PERIOD_DURATION`, `..._FREQUENCY`, `..._GRACE_PERIOD_DURATION`, `..._START_DATE`), 컨텍스트 인식 액세스 (Context-Aware Access) 켜기·앱 지정·오류 메시지 변경(`TOGGLE_CAA_ENABLEMENT`, `CHANGE_CAA_APP_ASSIGNMENTS`, `CHANGE_CAA_ERROR_MESSAGE`)이 남습니다[15]. 컨텍스트 인식 액세스는 Entra 조건부 접근과 비슷한 자리에 있는 기능입니다. 관리자가 특정 사용자에게 한 조치는 사용자 설정 쪽에 `TURN_OFF_2_STEP_VERIFICATION`, `USER_ENROLLED_IN_TWO_STEP_VERIFICATION`, `USER_PUT_IN_TWO_STEP_VERIFICATION_GRACE_PERIOD`, `GENERATE_2SV_SCRATCH_CODES`, `DELETE_2SV_SCRATCH_CODES`, `SECURITY_KEY_REGISTERED_FOR_USER`, `REVOKE_SECURITY_KEY`, `PASSKEY_REVOKED`, `UNENROLL_USER_FROM_STRONG_AUTH`, `UNENROLL_USER_FROM_TITANIUM` 으로 남습니다[16].

### Okta·Slack

Okta 시스템 로그의 MFA 이벤트는 `user.authentication.auth_via_mfa`, `user.mfa.factor.activate`, `user.mfa.factor.deactivate`, `user.mfa.factor.reset_all`, `user.mfa.attempt_bypass`, `system.push.send_factor_verify_push`(푸시를 보낼 때마다), `user.account.report_suspicious_activity_by_enduser` 이고, 정책 변경은 `policy.lifecycle.update`, `policy.rule.update`, `policy.rule.deactivate` 입니다[17]. `auth_via_mfa` 는 Okta Classic 조직에서는 두 번째 요소 검증에만, Identity Engine 조직에서는 첫 번째와 두 번째 요소 모두에 남습니다[17]. 사용자가 Okta Verify 푸시를 거절한 기록은 Classic V1 API 에서는 `user.mfa.okta_verify.deny_push` 이고, Identity Engine 에서는 `auth_via_mfa` 가 이유 `INVALID_CREDENTIALS` 로 실패한 기록입니다[17].

Slack 감사 로그의 `pref.two_factor_auth_changed` 는 2단계 인증 요구가 바뀐 기록이고 `details` 에 이전 값과 새 값이 있으며, `pref.two_factor_prevent_sms_changed` 는 SMS 사용 허용이 바뀐 기록입니다[18].

## 읽는 법

Entra 로그인 한 건에서는 `authenticationRequirement` 로 MFA 를 요구받았는지 보고, `authenticationDetails` 로 실제 단계와 방법과 결과를 본 뒤, `conditionalAccessStatus` 와 정책별 결과로 어느 정책이 요구했는지를 확인합니다. `authenticationMethod` 가 "Previously satisfied" 나 "Satisfied by token" 이면 그 시각에 MFA 를 새로 한 것이 아니라 이전 MFA 클레임으로 넘어간 것입니다[6]. 포털에서 한 줄인 MFA 로그인이 Azure Monitor 로 옮긴 로그에서는 같은 `correlationId` 를 가진 여러 줄로 나뉘므로, 틀린 코드 입력이나 응답 시간 초과 같은 중간 단계를 보려면 `correlationId` 로 묶어 읽습니다[9].

사용자가 모르는 MFA 요청을 신고하는 기능(Report suspicious activity)을 쓰면 세 곳에 남습니다[19]. 로그인 로그에는 사용자가 거부한 로그인으로 Authentication details 결과가 "MFA denied" 로, 감사 로그에는 활동 유형으로, 위험 탐지에는 탐지 유형 User Reported Suspicious Activity·위험 수준 High·원천 End user reported(`riskEventType` 은 `userReportedSuspiciousActivity`)로 남습니다[19]. 비밀번호 없는 인증을 한 사용자는 High 위험으로 표시되지 않습니다[19]. 요청한 기기와 승인한 기기의 위치 근접도 등을 보고 사회공학 승인을 가려내는 위험 탐지 Suspicious MFA authentication approval(`authenticatorPhishing`)은 실시간으로 계산되는 프리미엄 탐지입니다[20]. MFA 승인 요청이 반복된 사건을 따라가는 순서는 [MFA 피로 공격](../../04-scenarios/account-compromise/mfa-fatigue.md)에 있습니다.

정책 변경은 감사 로그에서 서비스를 Conditional Access 로 거르거나 Log Analytics 에서 아래처럼 뽑은 뒤, 바꾸기 전과 뒤의 JSON 을 비교합니다[4].

```kusto
AuditLogs
| where OperationName == "Update Conditional Access policy"
```

사용자를 정책 제외 그룹에 넣으면 정책은 그대로이고 그룹 구성원만 바뀌므로, `excludeGroups` 에 있는 그룹 ID 를 뽑아 그 그룹의 "Add member to group" 기록도 함께 봅니다[3][4].

AWS 에서는 `ConsoleLogin` 의 `MFAUsed` 를 보되, 페더레이션 사용자의 로그인이면 MFA 여부를 IdP 쪽 기록([페더레이션과 SSO](federation-sso.md))에서 확인합니다. Google Workspace 에서는 로그인 한 건의 `login_challenge_method` 목록 전체를 읽어 비밀번호만 있었는지, 두 번째 요소가 있었는지를 봅니다.

## 포렌식에서 중요한 점

### 증명하는 것과 증명하지 못하는 것

이 기록은 그 로그인에서 MFA 를 요구받았는지, 어떤 방법으로 어떤 결과가 나왔는지, 어느 조건부 접근 정책이 평가됐고 결과가 무엇이었는지를 보여 줍니다. 감사 로그는 인증 방법·사용자별 MFA 상태·정책이 언제 어느 계정으로 바뀌었는지를 보여 줍니다.

MFA 를 통과했다는 기록이 계정 주인이 직접 통과했다는 뜻은 아닙니다. 반복 요청에 지친 승인이나 피싱 페이지를 거친 승인도 같은 성공 기록으로 남으므로, 승인 시각과 위치, 위험 탐지, 그 뒤 활동을 함께 봐야 합니다. 이전 MFA 클레임으로 충족된 로그인은 그 시각에 MFA 를 한 것이 아닙니다[6]. 페더레이션 사용자의 AWS `MFAUsed` 가 `No` 인 것은 IdP 에서 MFA 를 하지 않았다는 뜻이 아닙니다[12]. Report-only 결과는 정책이 실제로 막았다는 뜻이 아니고[10], 사용자별 MFA 상태가 `Disabled` 인 것은 MFA 를 쓰지 않는다는 뜻이 아닙니다[2].

### 시각

Entra 로그인 레코드의 `createdDateTime` 은 로그인을 시작한 시각이고, `authenticationStepDateTime` 은 인증 단계마다의 시각이며 둘 다 UTC 입니다[5][6]. 단계별 시각을 비교하면 비밀번호 입력과 MFA 승인 사이에 걸린 시간을 알 수 있습니다. 관리 센터의 로그인 로그 화면은 날짜·시각을 로그인 사용자가 아니라 화면을 보는 관리자의 시간대로 바꿔 보여 줍니다[9]. 도구로 뽑은 조건부 접근 정책의 `CreatedDateTime`·`ModifiedDateTime` 은 정책 객체의 값이라서 마지막으로 바뀐 시각만 알려 주고, 누가 무엇을 바꿨는지는 감사 로그로 확인합니다[25].

Google Workspace 의 `login_challenge` 는 한 로그인 세션의 챌린지를 한 항목으로 묶기 때문에 챌린지마다 따로 된 시각은 없습니다[14]. 클라우드 로그의 시각 형식과 지연은 [클라우드 로그의 시각](../logging/timestamps.md)에서 다룹니다.

### 보관 기간

2026년 9월 문서 기준으로 Entra 로그인 로그와 감사 로그는 Free 7일, P1·P2 30일 보관되고, MFA 사용 보고는 모든 라이선스에서 30일, 위험 로그인은 Free 7일·P1 30일·P2 90일, 위험 사용자는 위험을 해결할 때까지 남습니다[22]. 감사 로그를 기본 보관 기간보다 오래 두려면 진단 설정으로 다른 곳에 옮겨 둬야 합니다[4]. P2 가 없는 테넌트는 위험 탐지 이름 대신 "Additional risk detected" 만 받습니다[20]. Okta 시스템 로그 API 는 90일보다 오래된 기록을 돌려주지 않습니다[23]. 서비스별 보관 기간 전체는 [보관 기간과 라이선스](../logging/retention-licensing.md)에 있습니다.

### 지우기·조작

MFA 를 끄거나 방법을 바꾸는 조작은 그 자체가 감사 로그에 남습니다. Entra 에서 사용자별 MFA 를 해제하면 Core Directory 의 "Update user" 레코드에서 수정 속성 `StrongAuthenticationRequirement` 의 새 값에 `State":0` 이 들어가고[21], "Disable Strong Authentication" 작업도 남습니다[3]. 관리자가 TAP 를 붙이면 "Admin registered security info" 레코드에 "Admin registered temporary access pass method for user" 가 남습니다[21]. 인증서 기반 인증을 켜면 "Authentication Methods Policy Update" 의 수정 속성에 `AuthenticationMethodsPolicy` 가, 새 루트 인증 기관을 넣으면 "Set Company Information" 의 새 값에 `TrustedCAsForPasswordlessAuth` 가 남습니다[21]. 공격자가 MFA 를 우회하려고 정책을 바꾼 흔적은 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md)와 같은 방법으로 바뀐 앞뒤 값을 비교해 찾습니다.

## 함정

**MFA 가 다시 뜨지 않는 정상 경우가 있습니다.** "MFA 기억" 기능은 브라우저에 지속 쿠키를 심어 정해진 기간 동안 그 브라우저에서 MFA 를 다시 묻지 않고, 다른 브라우저를 쓰거나 쿠키를 지우면 다시 묻습니다[19]. 이 기능은 B2B 사용자와 조건부 접근의 로그인 빈도 제어와 함께 쓸 수 없습니다[19]. AD FS 의 keep me signed in 과 함께 쓰면 기억 기간이 끝나 Entra 가 MFA 를 새로 요구해도 AD FS 가 원래 MFA 클레임과 날짜가 든 토큰을 돌려줍니다[19]. 신뢰할 수 있는 IP (trusted IPs) 범위에서는 MFA 를 묻지 않으므로 사내 IP 에서 MFA 없이 성공한 로그인은 정상일 수 있습니다[19]. 이 기능은 P1 이 필요하고, 범위는 50개까지이며, 클라우드 MFA 에서는 공용 IP 만 넣을 수 있습니다[19].

**로그인 빈도는 즉시 적용되지 않습니다.** 로그인 빈도 기본값은 90일 굴러가는 창이고, Entra 가입·하이브리드 가입 기기에서는 PRT 가 4시간마다 갱신되며 로그인 빈도는 PRT 마지막 갱신 시각과 비교합니다[24]. 브라우저의 백그라운드 작업은 다음 사용자 조작까지, 기밀 클라이언트의 비대화형 로그인은 다음 대화형 로그인까지 로그인 빈도 적용이 미뤄집니다[24]. 그래서 정책 시간이 지났는데도 토큰이 쓰인 기록이 보일 수 있습니다.

**처음 기록된 Authentication details 는 틀릴 수 있습니다.** 집계가 끝나기 전에는 "satisfied by claim in the token" 이 잘못 표시되거나 Primary authentication 줄이 빠질 수 있습니다[9]. 사건 직후 받은 사본과 나중에 받은 사본이 다르면 나중 값을 씁니다.

**레거시 인증은 MFA 를 거치지 않습니다.** 사용자별 MFA `Enabled` 상태에서도 레거시 인증은 비밀번호로 계속 동작합니다[2]. `clientAppUsed` 가 Exchange ActiveSync, IMAP, MAPI, SMTP, POP 같은 값인 로그인[5]과 `userAgent` 에 `BAV2ROPC`·`CBAinPROD`·`CBAinTAR` 가 든 성공 로그인[21]을 따로 뽑아 봅니다.

**`AuthenticationRequirement` 의 정의가 문서마다 다릅니다.** Graph 문서는 로그인이 도달한 단계라고 설명하고[5], Log Analytics 표 문서는 로그인에 필요했던 가장 높은 단계라고 설명합니다[7]. 이전 MFA 클레임으로 요구가 이미 충족돼 리소스가 MFA 를 다시 요구하지 않은 경우처럼 실제로 한 인증과 값이 다를 수 있습니다[9]. 차이는 [토큰과 세션](tokens-sessions.md)에서 자세히 다룹니다.

**탐지 규칙의 표기가 원문과 다릅니다.** SigmaHQ 규칙은 조건부 접근 작업 이름을 "Add conditional access policy" 처럼 소문자로 적고[21] Entra 문서는 "Add Conditional Access policy" 로 적습니다[3]. 조건부 접근 정책을 바꿀 수 있는 그룹에 구성원을 넣은 기록을 찾는 규칙은 작업 이름을 "Add member from group" 으로 적고[21], Entra 문서의 작업 이름은 "Add member to group" 입니다[3]. AWS 규칙은 `MFAUsed` 를 `'NO'` 로 찾지만[21] 레코드 값은 `No` 입니다[12]. 규칙을 그대로 쓰면 대소문자를 구분하는 도구에서 놓칠 수 있으니 [탐지 규칙으로 로그 검색하기](../../03-techniques/analysis/detection-rules.md)에서처럼 값을 원문과 맞춥니다.

**예전 기능과 새 기능의 기록이 섞입니다.** Entra 의 옛 Fraud alert·Block/unblock·Notifications 기능은 2025년 3월 1일에 없어지고 Report suspicious activity 로 바뀌었습니다[19]. 그 전 기록은 감사 작업 "Fraud reported - user is blocked for MFA" 로, 그 뒤 기록은 위험 탐지 `userReportedSuspiciousActivity` 로 남을 수 있습니다[3][19]. Okta 의 `auth_via_mfa` 도 Classic 과 Identity Engine 에서 기록 범위가 다릅니다[17].

**푸시 승인 방식은 경로마다 다릅니다.** Authenticator 푸시 알림에는 모두 번호 일치 (number matching) 가 켜져 있어서 사용자가 알림에 화면의 숫자를 입력해야 승인됩니다[26]. NPS 확장은 번호 일치를 지원하지 않고, 1.2.2216.1 판부터는 TOTP 방법을 등록한 사용자에게 승인·거부 대신 TOTP 를 요구합니다[26]. 1.0.1.40 부터 그 앞 판까지는 레지스트리를 바꿔야 TOTP 를 요구하고, 1.0.1.40 보다 앞 판은 승인·거부 방식을 씁니다[26].

## 도구

Microsoft-Extractor-Suite 의 `Get-ConditionalAccessPolicies` 는 `Get-MgIdentityConditionalAccessPolicy -All` 로 정책을 받아 상태·만든 시각·바꾼 시각·포함·제외 사용자와 그룹·앱·위치·클라이언트 앱 종류·위험 수준·허용 제어·지속 브라우저·로그인 빈도를 CSV 로 내고, `Get-MFA` 는 `v1.0/users/{id}/authentication/methods` 의 `@odata.type` 으로 사용자별 등록 방법을 세고 `v1.0/reports/authenticationMethods/userRegistrationDetails` 도 받습니다[25]. DFIR-O365RC 는 `Get-MgBetaReportAuthenticationMethodUserRegistrationDetail` 로 등록 상세를 받고(P1 필요), `Get-MgBetaUserAuthenticationMethod` 로 사용자별 방법을 받습니다[27]. Untitled Goose Tool 은 `conditionalAccess/policies`, `conditionalAccess/namedLocations`, `conditionalAccess/authenticationContextClassReferences`, `policies/authenticationMethodsPolicy` 를 받습니다[28]. Hawk 는 `Get-MgRiskDetection` 으로 위험 탐지를 받습니다[29]. 수집 순서는 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md)를 봅니다.

SigmaHQ 의 Azure 로그인 로그 규칙에는 MFA 거부(`AuthenticationRequirement` 가 `multiFactorAuthentication` 이고 상태에 "MFA Denied"), 조건부 접근 차단(53003), 단일 요소만 요구된 성공 로그인, MFA 없는 기기 등록(`Device Registration Service` 로그인이 `conditionalAccessStatus` 성공인데 `multiFactorAuthentication` 이 아님)이 있습니다[21]. 통합 감사 로그 규칙은 `UserLoggedIn` 중 `ApplicationId` 가 `9ba1a5c7-f17a-4de9-a1f1-6178c8d51223` 이고 `RequestType` 이 `Cmsi:Cmsi` 인 성공 로그인을 조건부 접근을 거치지 않은 로그인 후보로 봅니다(Intune 기기 등록인 `ObjectId` `0000000a-0000-0000-c000-000000000000` 은 뺌)[21]. Google Workspace 규칙은 `ENFORCE_STRONG_AUTHENTICATION`·`ALLOW_STRONG_AUTHENTICATION` 의 새 값이 `false` 인 기록과 `CHANGE_APPLICATION_SETTING` 중 설정 이름이 `ContextAwareAccess` 로 시작하는 기록을 찾고[21], Okta 규칙은 `user.mfa.factor.deactivate`·`reset_all`, `policy.rule.update`·`delete`, `zone.deactivate`·`delete`, `auth_via_mfa` 실패 중 이유가 "FastPass declined phishing attempt" 인 기록을 찾습니다[30]. 이상한 로그인을 고르는 전체 흐름은 [이상한 로그인 가려내기](../../03-techniques/analysis/suspicious-sign-ins.md)에 있습니다.

## 참고 문헌

1. Microsoft, "How it works: Microsoft Entra multifactor authentication" (ms.date 2025-03-04). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/authentication/concept-mfa-howitworks.md
2. Microsoft, "Enable per-user Microsoft Entra multifactor authentication to secure sign-in events", Microsoft Learn (2025-07-13 갱신). https://learn.microsoft.com/en-us/entra/identity/authentication/howto-mfa-userstates
3. Microsoft, "Microsoft Entra audit log activity reference" (ms.date 2025-03-25). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
4. Microsoft, "Use audit logs to troubleshoot Conditional Access policy changes", Microsoft Learn (2026-03-25 갱신). https://learn.microsoft.com/en-us/entra/identity/conditional-access/troubleshoot-policy-changes-audit-log
5. Microsoft, "signIn resource type", Microsoft Graph beta, Microsoft Learn (2025-11-28 갱신). https://learn.microsoft.com/en-us/graph/api/resources/signin?view=graph-rest-beta
6. Microsoft, "authenticationDetail resource type", Microsoft Graph beta, Microsoft Learn (2026-07-04 갱신). https://learn.microsoft.com/en-us/graph/api/resources/authenticationdetail?view=graph-rest-beta
7. Microsoft, "SigninLogs", Azure Monitor Logs 표 참조, Microsoft Learn (2026-08-27 갱신). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
8. Microsoft, "AADNonInteractiveUserSignInLogs", Azure Monitor Logs 표 참조, Microsoft Learn (2026-08-27 갱신). https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadnoninteractiveusersigninlogs
9. Microsoft, "Learn about the sign-in log activity details" (ms.date 2026-03-04). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/concept-sign-in-log-activity-details.md
10. Microsoft, "What is Conditional Access report-only mode?", Microsoft Learn (2026-06-01 갱신). https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-report-only
11. Microsoft, "Microsoft Entra authentication and authorization error codes", Microsoft Learn (2025-02-03 갱신). https://learn.microsoft.com/en-us/entra/identity-platform/reference-error-codes
12. AWS, "AWS Management Console sign-in events", AWS CloudTrail User Guide. https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference-aws-console-sign-in-events.html
13. AWS, "AssumeRole", AWS Security Token Service API Reference. https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html
14. Google, "Login Audit Activity Events", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/login
15. Google, "Admin Audit Activity Events - Security Settings", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-security-settings
16. Google, "Admin Audit Activity Events - User Settings", Admin SDK Reports API (2026-09-03 갱신). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-user-settings
17. Okta, "Event types" (okta-event-types.csv). https://developer.okta.com/docs/okta-event-types.csv
18. Slack, "Audit Logs API actions". https://api.slack.com/admins/audit-logs-call
19. Microsoft, "Configure Microsoft Entra multifactor authentication settings", Microsoft Learn (2026-02-27 갱신). https://learn.microsoft.com/en-us/entra/identity/authentication/howto-mfa-mfasettings
20. Microsoft, "What are risk detections?", Microsoft Entra ID Protection, Microsoft Learn (2026-04-22 갱신). https://learn.microsoft.com/en-us/entra/id-protection/concept-identity-protection-risks
21. SigmaHQ, 클라우드 탐지 규칙: rules/cloud/azure/audit_logs(azure_mfa_disabled, azure_user_account_mfa_disable, azure_tap_added, azure_ad_certificate_based_authencation_enabled, azure_ad_new_root_ca_added, azure_aad_secops_new_ca_policy_addedby_bad_actor, azure_group_user_addition_ca_modification), rules/cloud/azure/signin_logs(azure_mfa_denies, azure_mfa_interrupted, azure_conditional_access_failure, azure_ad_only_single_factor_auth_required, azure_ad_device_registration_or_join_without_mfa, azure_ad_suspicious_signin_bypassing_mfa), rules/cloud/m365/audit/microsoft365_bypass_conditional_access, rules/cloud/aws/cloudtrail/aws_cloudtrail_console_login_success_without_mfa, rules/cloud/gcp/gworkspace/admin(gcp_gworkspace_mfa_disabled, gcp_gworkspace_application_access_levels_modified). https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/
22. Microsoft, "Microsoft Entra data retention" (ms.date 2026-01-06). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
23. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
24. Microsoft, "Conditional Access adaptive session lifetime policies", Microsoft Learn (2026-04-08 갱신). https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-session-lifetime
25. Invictus Incident Response, Microsoft-Extractor-Suite(Scripts/Get-ConditionalAccessPolicy.ps1, Scripts/Get-MFAStatus.ps1). https://github.com/invictus-ir/Microsoft-Extractor-Suite
26. Microsoft, "How number matching works in MFA push notifications for Authenticator", Microsoft Learn (2025-11-06 갱신). https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-mfa-number-match
27. ANSSI, DFIR-O365RC(Get-AADUsers.ps1). https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/Get-AADUsers.ps1
28. CISA, Untitled Goose Tool(goosey/entra_id_datadumper.py). https://github.com/cisagov/untitledgoosetool
29. T0pCyber, Hawk(Hawk/functions/Tenant/Get-HawkTenantRiskDetections.ps1). https://github.com/T0pCyber/hawk
30. SigmaHQ, Okta 탐지 규칙(okta_mfa_reset_or_deactivated, okta_policy_rule_modified_or_deleted, okta_network_zone_deactivated_or_deleted, okta_fastpass_phishing_detection). https://github.com/SigmaHQ/sigma/tree/master/rules/identity/okta
