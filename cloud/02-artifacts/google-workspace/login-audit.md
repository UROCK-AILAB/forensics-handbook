---
title: "로그인 기록"
parent: "아티팩트 · Google Workspace"
nav_order: 300
---

# 로그인 기록 (Login Audit)

Google Workspace 사용자가 언제, 어느 IP 에서, 어떤 인증 방법으로 로그인했거나 실패했는지와 비밀번호·복구 정보·2단계 인증처럼 자기 계정에 한 중요한 변경을 남기는 기록입니다.

## 무엇을 기록하나 · 왜 생기나

관리 콘솔에서는 이 기록을 "User log events" 라는 이름으로 보여 주고, 예전 이름은 "Login audit log" 입니다[6][7]. 사용자의 로그인 시도와 함께 사용자가 자기 계정에 한 중요한 작업(비밀번호 변경, 복구용 전화번호·메일 주소 변경, 2단계 인증 등록)을 남깁니다[6]. Google 이 로그인을 의심스럽다고 판단해 막은 일, 계정을 정지한 일, 정부 지원 공격 경고, 도메인 밖으로 메일 자동 전달을 켠 일도 이 기록에 들어갑니다[2].

보고서 API (Reports API) 에서는 `applicationName=login` 으로 가져옵니다[1][2]. 사용자가 SAML 애플리케이션(서비스 공급자, SP)에 로그인한 성공·실패 기록은 따로 `applicationName=saml` 로 남습니다[3][10].

기록의 범위는 좁습니다. 로그인 활동 보고서는 명시적인 비밀번호 로그인과 SAML 기반 SSO 로그인만 감사합니다[1]. 메일 클라이언트나 브라우저가 아닌 앱의 로그인은, 의심스럽다고 판단한 세션에서 나온 프로그램 로그인이 아니면 남지 않습니다[6]. 그런데 이벤트 값에는 `exchange`·`reauth` 같은 로그인 종류도 있고[2] 관리 콘솔 설명에는 OIDC 도 있어서[6], 문서끼리 범위 설명이 어긋납니다. 실제 데이터에서는 `login_type` 값별 개수를 먼저 세어 실제로 어떤 종류가 들어 있는지 확인합니다.

## 위치와 버전별 차이

같은 기록을 네 곳에서 볼 수 있고, 곳마다 모양과 보관 기간이 다릅니다.

| 보는 곳 | 모양 | 조건 |
|---|---|---|
| 관리 콘솔 Reporting > Audit and investigation > User log events | 속성 열이 있는 표, 기본 7일 검색, Sheets·CSV 내보내기 10만 행 | Audit & Investigation 관리자 권한[6] |
| 관리 콘솔 Security > Security center > Investigation tool (데이터 소스 User log events) | 위와 같은 속성, 내보내기 3천만 행 | Security center 관리자 권한. Frontline Standard·Plus, Enterprise Standard·Plus, Education Standard·Plus, Enterprise Essentials Plus, Cloud Identity Premium[6] |
| 보고서 API `activities.list` (`applicationName=login`, `saml`) | JSON 활동 레코드 | 관리자 권한, 범위 `admin.reports.audit.readonly`[4] |
| Cloud Logging 공유 | `LogEntry` (서비스 이름 `login.googleapis.com`)[10] | 최고 관리자가 Account settings > Legal and compliance > Sharing options 에서 켬. User log events 는 모든 계정, SAML log events 는 Enterprise Standard·Plus, Education Standard·Plus, Voice Premier, Cloud Identity Premium[11] |

보관 기간과 지연 시간은 다음과 같습니다(2026년 9월 문서 기준)[7].

| 로그 | 보관 | 지연 |
|---|---|---|
| User log events | 6개월 | 로그인 이벤트는 몇 분, 사용자 계정 이벤트는 수십 분 |
| SAML log events | 6개월 | 몇 분 |
| API 로 받는 감사 데이터 | 6개월 (한 번에 조회하는 기간은 최근 180일까지[1][4]) | 위와 같음 |

관리자는 로그 이벤트를 지우거나 보관 기간을 바꿀 수 없습니다[7]. Cloud Logging 으로 공유한 사본은 관리 콘솔과 다른 Google Cloud 쪽 보관 정책을 따르므로[11], 6개월보다 오래된 로그인 기록이 필요하면 공유가 언제부터 켜져 있었는지를 먼저 확인합니다. Cloud Logging 쪽 보관과 버킷은 [Cloud Audit Logs](../gcp/cloud-audit-logs.md), 서비스별 보관 비교는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에 정리했습니다.

## 구조

보고서 API 레코드의 공통 뼈대(`id`, `actor`, `ipAddress`, `events[]`, `networkInfo`)는 [관리 콘솔 감사 로그](admin-audit.md)에 설명했습니다. 로그인 기록에서 중요한 것은 `events[].type`·`name` 과 매개변수입니다[2].

| type | name | 주요 매개변수 |
|---|---|---|
| `login` | `login_success` | `is_suspicious`, `login_challenge_method`, `login_type` |
| `login` | `login_failure` | `login_challenge_method`, `login_failure_type`(폐기 예정), `login_type` |
| `login` | `login_challenge` | `login_challenge_method`, `login_challenge_status`, `login_type` |
| `login` | `login_verification` | `is_second_factor`, `login_challenge_method`, `login_challenge_status`, `login_type` |
| `login` | `logout` | `login_type` |
| `login` | `risky_sensitive_action_allowed`, `risky_sensitive_action_blocked` | `is_suspicious`, `login_challenge_method`, `login_challenge_status`, `login_type`, `sensitive_action_name` |
| `account_warning` | `suspicious_login`, `suspicious_login_less_secure_app`, `suspicious_programmatic_login` | `affected_email_address`, `login_timestamp` |
| `account_warning` | `account_disabled_hijacked` | `affected_email_address`, `login_timestamp` |
| `account_warning` | `account_disabled_password_leak`, `account_disabled_generic`, `account_disabled_spamming`, `account_disabled_spamming_through_relay` | `affected_email_address` |
| `account_warning` | `user_signed_out_due_to_suspicious_session_cookie` | `affected_email_address` |
| `account_warning` | `passkey_enrolled`, `passkey_removed` | 없음 |
| `2sv_change` | `2sv_enroll`, `2sv_disable` | 없음 |
| `password_change` | `password_edit` | 없음 |
| `recovery_info_change` | `recovery_email_edit`, `recovery_phone_edit`, `recovery_secret_qa_edit` | 없음 |
| `titanium_change` | `titanium_enroll`, `titanium_unenroll` | 없음 (고급 보호 프로그램 (Advanced Protection) 등록·해제) |
| `attack_warning` | `gov_attack_warning` | 없음 |
| `blocked_sender_change` | `blocked_sender` | 없음 |
| `email_forwarding_change` | `email_forwarding_out_of_domain` | 매개변수 목록은 없고, 관리 콘솔 메시지에 전달 대상 주소 `email_forwarding_destination_address` 가 들어감 |

`suspicious_login` 계열 세 이벤트의 관리 콘솔 이름은 "Suspicious login blocked" 처럼 모두 "blocked" 로 끝나므로, 이 이벤트는 Google 이 막은 시도를 뜻합니다[2]. 의심스러운데 성공한 로그인은 `login_success` 에 `is_suspicious` 가 `true` 로 남습니다[2][6].

`login_type` 은 로그인에 쓴 자격 증명 종류이고 값은 `exchange`, `google_password`, `reauth`, `saml`, `unknown` 입니다[2]. `exchange` 는 이미 가진 자격 증명을 다른 종류로 바꾼 것(예: OAuth 토큰을 SID 로)이고, 이미 로그인한 세션과 새 세션이 합쳐졌을 수도 있다는 뜻입니다[2]. `login_challenge_method` 는 `password`, `google_prompt`, `google_authenticator`, `security_key`, `passkey`, `idv_preregistered_phone`, `backup_code`, `device_prompt`, `login_location`, `captcha`, `saml`, `oidc`, `none`, `other` 등 50가지가 넘는 값을 씁니다[2]. `login_challenge_status` 는 `"Challenge Passed."`, `"Challenge Failed."` 가운데 하나이고 빈 문자열이면 결과를 모르는 것입니다[2].

한 로그인 세션에서 만난 도전은 이벤트 하나로 묶입니다[2]. 비밀번호를 두 번 틀리고 세 번째에 맞힌 뒤 보안 키로 2단계 인증을 마치면, `login_success` 하나의 `login_challenge_method` 에 `password` 세 개와 `security_key` 하나가 순서대로 들어갑니다[2]. 아래는 그 모양으로 만든 예시이며 주소·IP·ID 는 모두 지어낸 값입니다.

```json
{
  "kind": "audit#activity",
  "id": {
    "time": "2026-03-02T01:14:07.512Z",
    "uniqueQualifier": "-1234567890123456789",
    "applicationName": "login",
    "customerId": "C03az79cb"
  },
  "actor": {"callerType": "USER", "email": "user@example.com", "profileId": "100000000000000000001"},
  "ipAddress": "203.0.113.25",
  "events": [{
    "type": "login",
    "name": "login_success",
    "parameters": [
      {"name": "login_type", "value": "google_password"},
      {"name": "login_challenge_method", "multiValue": ["password", "password", "password", "security_key"]},
      {"name": "is_suspicious", "boolValue": false}
    ]
  }]
}
```

SAML 앱 로그인(`applicationName=saml`)에는 `login_success`·`login_failure` 두 이벤트가 있고, 매개변수로 서비스 공급자 앱 이름 `application_name`, `device_id`, 인증을 누가 시작했는지(`initiated_by` 값 `idp`·`sp`), `orgunit_path`, `saml_status_code` 가 남습니다[3]. 실패에는 `failure_type`(예 `failure_app_not_configured_for_user`, `failure_invalid_sp_id`, `failure_request_denied`, `failure_unknown`)과 `saml_second_level_status_code` 가 더 붙습니다[3]. 보고서 API 에서 `userDeviceInfo` 필드는 `saml` 활동에는 있지만 `login` 활동에는 없습니다[4].

Cloud Logging 으로 공유한 레코드는 모양이 다릅니다. 로그인 기록은 Data Access 감사 로그로만 쓰이고, `logName` 이 `organizations/123/logs/cloudaudit.googleapis.com%2Fdata_access` 로 끝납니다[10]. `protoPayload.methodName` 은 `google.login.LoginService.loginFailure` 처럼 서비스 메서드 이름이고, `protoPayload.metadata.event[].eventName` 은 `login_failure` 처럼 보고서 API 이름과 같습니다[10]. 사용자는 `protoPayload.authenticationInfo.principalEmail`, IP 는 `protoPayload.requestMetadata.callerIp` 에 들어갑니다[10]. SAML 로그인도 서비스 이름은 `login.googleapis.com` 이고 메서드 이름이 `google.apps.login.v1.SamlLoginSucceeded`·`SamlLoginFailed` 입니다[10].

관리 콘솔 표의 속성 가운데 API 필드와 바로 대응하지 않는 것은 다음과 같습니다[6]. "Login time" 은 차단된 의심 로그인의 시도 시각이고, "User agent" 는 기기 결합 세션 자격 증명 (Device Bound Session Credentials, DBSC) 이벤트에만 있습니다. "IP ASN" 은 기본 열에 없어서 열 관리에서 추가해야 보입니다.

## 증거로서 의미

**증명하는 것**

- 그 계정으로 그 시각에 그 IP 에서 로그인 성공·실패·도전·2단계 확인이 있었다는 것[2][6].
- 로그인 세션에서 어떤 인증 방법을 어떤 순서로 거쳤는지(`login_challenge_method`), 2단계 인증을 거쳤는지(`is_second_factor`)[2].
- Google 이 로그인을 의심스럽다고 표시했거나(`is_suspicious`) 막았다는 것(`suspicious_login` 계열)[2].
- 계정 소유자 쪽에서 비밀번호·복구 정보·2단계 인증·패스키를 바꿨다는 것과 그 시각[2].
- 도메인 밖 주소로 메일 자동 전달을 켰다는 것과 전달 대상 주소(`email_forwarding_out_of_domain`)[2].

**증명하지 못하는 것**

- 어느 기기·시스템에서 로그인했는지. 로그인 기록은 로그인 사건만 남기고 어느 시스템을 썼는지는 남기지 않습니다[10].
- 실패 횟수. 짧은 시간 안의 같은 시도는 세션 단위로 묶여, 다섯 번 틀리고 맞힌 경우 실패 한 줄과 성공 한 줄만 남을 수 있습니다[6].
- 메일 클라이언트·비브라우저 앱의 로그인 대부분[6].
- 로그인한 사람이 누구인지. 기록은 계정만 말합니다.
- 기록된 IP 가 실제 위치라는 것. 프록시·VPN 주소일 수 있습니다[4][6].
- 로그인 뒤에 무엇을 했는지. Drive·Gmail·관리 기록과 맞춰 봐야 합니다.
- 훔친 쿠키나 토큰으로 이어 쓴 세션. 새 로그인이 없으면 이 기록에 남지 않고, `exchange` 는 세션이 합쳐졌을 가능성만 알려 줍니다[2].

## 시각 해석

보고서 API 의 `id.time` 은 활동이 일어난 시각입니다. 필드 설명은 "UNIX epoch time in seconds" 라고 적었지만 가이드의 응답 예시는 `2011-06-17T15:39:18.460Z` 처럼 `Z` 로 끝나는 RFC 3339 UTC 문자열이라 문서끼리 다릅니다[4][5]. 실제 데이터에서 값의 모양을 보고 판단합니다. 같은 시각의 활동이 여럿이면 `id.uniqueQualifier` 로 구별합니다[4].

`suspicious_login`·`suspicious_login_less_secure_app`·`suspicious_programmatic_login`·`account_disabled_hijacked` 의 `login_timestamp` 는 마이크로초 단위 정수입니다[2]. 이 값은 로그인을 시도한 시각이라 경고 이벤트가 기록된 `id.time` 과 다를 수 있습니다[6]. 문서에는 기준 시점이 적혀 있지 않으므로, 실제 값이 요즘 날짜의 UNIX 시각(마이크로초, 16자리)과 자릿수가 맞는지 보고 1,000,000 으로 나눠 초로 바꿉니다.

관리 콘솔의 Date 열은 브라우저의 기본 시간대로 표시됩니다[6]. 보안 조사 도구는 최고 관리자가 조사 시간대를 바꿀 수 있고, 그 시간대가 검색 조건과 결과에 함께 적용됩니다[6]. 화면을 캡처해 보고서에 넣을 때는 어느 시간대로 표시됐는지 함께 적습니다.

Cloud Logging 레코드에는 시각이 셋 있습니다. `timestamp` 는 로그인 시각, `protoPayload.metadata.activityId.timeUsec` 은 같은 시각을 마이크로초 UNIX 시각으로 쓴 값, `receiveTimestamp` 는 Cloud Logging 이 받은 시각입니다[10]. 문서 예시에서는 `timestamp` 2021-09-24T16:16:57.183212Z 와 `receiveTimestamp` 2021-09-24T17:51:25.034361197Z 사이가 1시간 35분쯤 벌어져 있습니다[10]. 타임라인에는 `timestamp` 를 씁니다.

관리 콘솔 사용자 목록의 "Last sign in" 은 "2 minutes ago" 같은 대략값이고 지연이 몇 시간에서 3일까지 납니다[8]. 정확한 시각이 필요하면 이 열 대신 로그인 기록을 봅니다. 클라우드 로그 시각 일반은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 정리했습니다.

## 함정과 한계

- 로그아웃 이벤트는 실제로 어떤 방식으로 로그인했든 관리 콘솔에서 Login type 이 Google Password 로 보입니다[6].
- 조직 SSO 프로필(레거시 SAML)을 쓰는 사용자가 모르는 기기나 IP 에서 SAML 로그인하거나 위험 평가가 높으면, 로그인이 성공해도 Google Password 유형의 실패 로그인이 하나 남을 수 있습니다[6]. 이 실패를 비밀번호 대입 흔적으로 읽지 않습니다.
- 패스키처럼 새로 추가된 도전 종류는 2024년 9월 30일 전에 만들어진 기록의 기존 `other` 값과 어긋나 보일 수 있습니다[6].
- 사용자 이름을 바꾸면 옛 이름으로는 검색 결과가 나오지 않습니다[6]. 이름 변경 이력은 [관리 콘솔 감사 로그](admin-audit.md)의 `RENAME_USER` 로 찾습니다.
- 의심 로그인 알림은 보통 Google 이 사용자에게 추가 도전을 먼저 내고, 사용자가 실패하거나 포기했을 때 관리자에게 갑니다[9]. Mail Fetcher 로 다른 Gmail 계정의 메일을 가져올 때도 알림이 생길 수 있습니다[9].
- 외부 IdP 로 SAML·OIDC 로그인을 하면 비밀번호와 다단계 인증 판단은 IdP 쪽에서 일어납니다. Workspace 기록의 `login_type`·`login_challenge_method` 에는 `saml`·`oidc` 처럼 IdP 의 어설션을 냈다는 사실만 남으므로[2] IdP 로그를 함께 봅니다([페더레이션과 SSO](../../01-foundations/identity/federation-sso.md), [Okta 시스템 로그](../saas/okta.md)).
- 드물게 지연이 문서 값보다 길거나 이벤트가 아예 보고되지 않을 수 있습니다[7]. 수집 직전 몇 시간의 기록은 나중에 다시 받아 비교합니다.
- 보고서 API 로 한 번에 받을 수 있는 기간은 최근 180일입니다[4]. 지운 사용자는 메일 주소를 `userKey` 로 쓸 수 없고, Directory API `users.list` 에 `showDeleted=true` 를 붙여 받은 ID 를 `userKey` 로 씁니다[4].

## 직접 분석해 보기

**원자료 한 줄 읽기.** 보고서 API 응답은 `items` 배열에 활동을 담고[4], ALFA 가 저장한 파일은 한 줄에 활동 하나인 JSON 입니다[13]. 활동 하나를 열어 다음 순서로 읽습니다.

1. `id.applicationName` 이 `login` 인지 `saml` 인지 봅니다.
2. `id.time` 의 모양(RFC 3339 문자열인지 정수인지)과 `Z` 가 붙었는지 봅니다.
3. `actor.email` 과 `ipAddress` 를 적고, `networkInfo.regionCode`·`ipAsn` 이 있으면 함께 적습니다[4].
4. `events[].name` 과 매개변수를 읽습니다. `login_challenge_method` 는 `multiValue` 배열이라 순서를 그대로 옮깁니다.
5. `account_warning` 이벤트면 `login_timestamp` 를 초로 바꿔 `id.time` 과 비교합니다.

**보고서 API 로 거르기.** 의심스러운데 성공한 로그인만 가져오려면 다음처럼 요청합니다[1].

```text
GET https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/login?eventName=login_success&filters=is_suspicious==true&maxResults=25
```

`actorIpAddress` 로 특정 IP 의 활동만, `networkInfoFilter=regionCode="IN"` 모양으로 지역을 걸러 받을 수도 있습니다[4].

**공개 도구 ALFA.** ALFA (Automated Audit Log Forensic Analysis for Google Workspace) 는 보고서 API 로 로그를 받습니다[13]. `alfa acquire --logtype=login` 과 `--logtype=saml` 로 각각 받고, `--user` 로 사용자를, `--start-time`·`--end-time` 으로 기간을 정합니다[13]. 시간대를 붙이지 않은 시각은 UTC 로 봅니다[13]. 로그 종류마다 `login.json` 같은 파일이 한 줄 한 활동으로 저장됩니다[13]. ALFA 의 분석 단계는 기본으로 무해한 활동을 걸러 내므로(`--no-filter` 로 끔), 원자료 보존은 acquire 결과 파일로 합니다[13].

**Cloud Logging.** 공유가 켜져 있으면 Logs Explorer 에서 `protoPayload.serviceName="login.googleapis.com"` 으로 거릅니다. 쿼리와 수집 방법은 [Cloud Audit Logs](../gcp/cloud-audit-logs.md)를 봅니다.

**탐지 규칙.** SigmaHQ 에는 로그인 기록용 규칙이 세 개 있고, 모두 Cloud Logging 형식 필드 `protoPayload.serviceName: 'login.googleapis.com'` 와 `protoPayload.metadata.event.eventName` 을 씁니다[12]. `suspicious_login`·`suspicious_login_less_secure_app`·`suspicious_programmatic_login` 을 잡는 규칙, `gov_attack_warning` 규칙, `email_forwarding_out_of_domain` 규칙(T1114.003)입니다[12]. 보고서 API JSON 에 쓰려면 필드 이름을 `id.applicationName`·`events[].name` 으로 바꿔야 합니다. 규칙 적용 방법은 [탐지 규칙](../../03-techniques/analysis/detection-rules.md)에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 보는 것 |
|---|---|
| [관리 콘솔 감사 로그](admin-audit.md) | 관리자가 비밀번호를 재설정했는지(`CHANGE_PASSWORD`), 2단계 인증을 껐는지, 로그인 쿠키를 초기화했는지. 사용자 본인의 `password_edit` 와 구별합니다 |
| [OAuth 토큰 기록](token-audit.md) | 의심 로그인 뒤에 새 앱 권한 부여가 이어졌는지 |
| [Gmail 기록과 메일 검색](gmail.md) | `email_forwarding_out_of_domain` 뒤 실제로 메일이 외부로 나갔는지 |
| [Drive 기록](drive-audit.md) | 같은 IP·같은 시간대에 파일 다운로드·공유가 있었는지 |
| IdP 로그 ([Okta](../saas/okta.md), [Entra ID 로그](../m365/entra-logs/index.md)) | SAML 로그인 전에 IdP 에서 어떤 인증을 거쳤는지 |

IP 와 위치 정보를 해석하는 법은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md), 이상한 로그인을 가려내는 절차는 [이상한 로그인 가려내기](../../03-techniques/analysis/suspicious-sign-ins.md)에 있습니다. 여러 기록을 한 줄로 늘어놓는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)을 봅니다.

## 실습

위의 만든 예시 레코드와, 시험용 Workspace 테넌트에서 받은 로그로 풀어 봅니다.

1. 예시 레코드에서 비밀번호를 몇 번 입력했고 마지막 인증 수단은 무엇인가? 이 레코드만으로 "비밀번호를 두 번 틀렸다" 고 보고서에 쓸 수 있는가?
2. 같은 계정에 `suspicious_login` 과 몇 분 뒤 `login_success`(`is_suspicious` 가 `true`)가 있다. 두 이벤트는 각각 무엇을 말하고, 타임라인에는 어느 시각 값을 써야 하는가?
3. `logout` 의 Login type 이 Google Password 로 보인다. 이 사용자가 SAML 로 로그인했을 가능성을 배제할 수 있는가?
4. `email_forwarding_out_of_domain` 이 있다. 전달 대상 주소는 어디에서 보이고, 실제 전달 여부는 어느 기록으로 확인하는가?
5. 7개월 전의 로그인을 확인해야 한다. 관리 콘솔과 보고서 API 외에 어디를 확인해야 하는가?

보고서 문장 예는 "2026-03-02 01:14:07 UTC 에 user@example.com 계정으로 IP 203.0.113.25 에서 비밀번호와 보안 키를 거친 로그인 성공 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다(만든 예시). 계정 탈취 사건 전체의 흐름은 [메일 계정을 빼앗겨 송금 사기를 당했나](../../04-scenarios/account-compromise/bec.md)와 [토큰을 훔쳐 로그인했나](../../04-scenarios/account-compromise/token-theft.md)에서 이어집니다.

## 참고 문헌

1. Google, "Reports API: Login Activity Report", 2026-09-03 갱신. https://developers.google.com/workspace/admin/reports/v1/guides/manage-audit-login
2. Google, "Login Audit Activity Events", 2026-09-03 갱신. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/login
3. Google, "SAML Audit Activity Events", 2025-03-25 갱신. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/saml
4. Google, "Method: activities.list", 2026-09-03 갱신. https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
5. Google, "Reports API: Admin Activity Report", 2026-09-03 갱신. https://developers.google.com/workspace/admin/reports/v1/guides/manage-audit-admin
6. Google Workspace 관리자 도움말, "User log events", 2026-09-18 갱신. https://support.google.com/a/answer/4580120
7. Google Workspace 관리자 도움말, "Data retention and lag times", 2026-09-25 갱신. https://support.google.com/a/answer/7061566
8. Google Workspace 관리자 도움말, "View your users' last sign-in", 2026-09-18 갱신. https://knowledge.workspace.google.com/admin/reports/view-your-users-last-sign-in
9. Google Workspace 관리자 도움말, "About admin alerts for suspicious login activity", 2026-09-18 갱신. https://knowledge.workspace.google.com/admin/reports/about-admin-alerts-for-suspicious-login-activity
10. Google Cloud, "Google Workspace audit logging", 2026-09-25 갱신. https://cloud.google.com/logging/docs/audit/gsuite-audit-logging
11. Google Workspace 관리자 도움말, "Share data with Google Cloud services", 2026-09-18 갱신. https://support.google.com/a/answer/9320190
12. SigmaHQ, Google Workspace 로그인 탐지 규칙(`rules/cloud/gcp/gworkspace/login/`). https://github.com/SigmaHQ/sigma/tree/master/rules/cloud/gcp/gworkspace
13. Invictus IR, ALFA — Automated Audit Log Forensic Analysis for Google Workspace. https://github.com/invictus-ir/ALFA
