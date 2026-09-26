---
title: "OAuth 토큰 기록"
parent: "아티팩트 · Google Workspace"
nav_order: 330
---

# OAuth 토큰 기록 (Token Audit)

OAuth 토큰 기록은 Workspace 사용자가 제3자 앱에 계정 데이터 접근을 허락하거나 회수한 일, 그리고 그 앱이 사용자 대신 Google API 를 부른 일을 남기는 감사 로그이고, 보고서 API 에서는 `applicationName` 이 `token` 입니다[1][2].

## 무엇을 기록하나 · 왜 생기나

제3자 앱이 주소록·Calendar·Drive 파일 같은 Google 계정 데이터에 접근하도록 허락받을 때마다 이 로그에 기록이 남습니다[2][4]. Google Workspace Marketplace 앱을 열었을 때 앱 이름과 사용한 사람도 이 로그에 들어갑니다[4][6]. OAuth 동의가 무엇이고 토큰이 어떻게 오가는지는 [OAuth 앱과 동의](../../01-foundations/identity/oauth-consent.md)와 [토큰과 세션](../../01-foundations/identity/tokens-sessions.md)에서 다룹니다.

이벤트는 모두 `type` 이 `auth` 이고, 이름은 다섯 가지입니다[1].

| 이벤트 이름 | 뜻 | 관리 콘솔 문장 |
|---|---|---|
| `authorize` | 사용자가 앱에 자기 데이터 접근을 허락함 | `{actor} authorized access to {app_name} for {scope} scopes` |
| `revoke` | 앱의 접근이 회수됨 | `{actor} revoked access to {app_name} for {scope} scopes` |
| `deny` | 앱의 접근 요청이 거부됨 | `{actor} access request to {app_name} for {scope} scopes is denied due to {rejection_type}` |
| `request` | 앱 접근이 요청됨 | `{actor} requested access to {app_name} for {scope} scopes` |
| `activity` | 앱이 사용자 대신 API 를 부름 | `{app_name} called {method_name} on behalf of {actor}` |

관리 콘솔 문장은 화면에 보여 주는 형식이고, 보고서 API 레코드에는 이벤트 이름(`events[].name`)과 매개변수(`events[].parameters[]`)가 들어 있습니다[1][3].

## 위치와 에디션별 차이

2026년 9월 문서 기준입니다.

| 보는 곳 | 담는 것 | 보관·지연 | 에디션·권한 |
|---|---|---|---|
| 관리 콘솔 Reporting > Audit and investigation > OAuth log events | 토큰 이벤트 검색, 기본 최근 7일 표시, Sheets·CSV 내보내기 | 6개월 보관, 지연은 OAuth "Up to a few hours"·Token log events "A couple of hours"[5] | Audit & Investigation 관리자 권한, 검색 대상 사용자의 에디션과 무관[4] |
| 위 화면의 `activity`(Event 값 API call) | 앱이 부른 API 이름·메서드·응답 크기 | 위와 같음 | Enterprise Standard·Plus, Education Standard·Plus, Cloud Identity Premium 에서만[4] |
| Security > Security center > Investigation tool | 같은 데이터를 조건으로 검색·저장 | 위와 같음 | Frontline Standard·Plus, Enterprise Standard·Plus, Education Standard·Plus, Enterprise Essentials Plus, Cloud Identity Premium[4] |
| 보고서 API `activities.list`(`applications/token`) | JSON 활동 레코드 | 한 번에 조회할 수 있는 기간은 최근 180일[2], 지연은 관리 콘솔과 같음[5] | 관리자 권한과 `admin.reports.audit.readonly` 범위[3] |
| Cloud Logging 공유 | `oauth2.googleapis.com` 감사 로그 | Google Cloud 관리 감사 로그 보관 정책을 따르고 관리 콘솔 보관과 다름[7] | Enterprise Standard·Plus, Education Standard·Plus, Voice Premier, Cloud Identity Premium, 최고 관리자가 켬[7] |

관리자는 로그 이벤트를 지우거나 보관 기간을 바꿀 수 없습니다[5]. 보관 기간을 다른 서비스와 비교한 내용은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에 있습니다.

Cloud Logging 으로 공유한 토큰 기록은 서비스 이름이 `oauth2.googleapis.com`, 자원 종류가 `audited_resource` 이고, 관리 활동 (Admin Activity) 기록과 데이터 접근 (Data Access) 기록을 모두 씁니다[6].

| Cloud Logging 기록 종류 | `methodName` |
|---|---|
| Admin Activity | `google.identity.oauth2.Deny`, `google.identity.oauth2.GetToken`, `google.identity.oauth2.Request`, `google.identity.oauth2.RevokeToken` |
| Data Access | `google.identity.oauth2.GetTokenInfo` |

Cloud Logging 레코드의 공통 구조는 [Cloud Audit Logs](../gcp/cloud-audit-logs.md)에서 다룹니다.

로그와 별도로 지금 살아 있는 토큰의 상태를 보여 주는 곳이 두 군데 있습니다. Directory API 의 `tokens` 자원은 사용자별로 제3자 앱에 발급한 토큰 목록을 돌려주고[8], 관리 콘솔 Security > Access and data control > API controls 의 Accessed apps 목록은 조직 안에서 Google 데이터에 접근한 앱과 사용자 수를 보여 줍니다[9].

## 구조

보고서 API 가 돌려주는 활동 레코드의 공통 필드(`id`, `actor`, `ipAddress`, `events[]`)와 시각 형식은 [관리 콘솔 감사 로그](./admin-audit.md)에서 다룹니다. 토큰 기록에서 더 볼 것은 `events[].parameters[]` 에 든 매개변수입니다[1].

| 매개변수 | 들어 있는 이벤트 | 뜻 |
|---|---|---|
| `app_name` | 다섯 이벤트 모두 | 접근을 허락·회수한 앱 이름 |
| `client_id` | 다섯 이벤트 모두 | 앱의 OAuth 클라이언트 ID |
| `client_type` | 다섯 이벤트 모두 | 클라이언트 종류 |
| `scope` | `authorize`, `revoke`, `deny`, `request` | 허락·회수한 범위 (scope) |
| `scope_data` | `authorize`, `revoke`, `deny`, `request` | 범위 데이터(message 형식) |
| `rejection_type` | `deny` | 거부 까닭 |
| `app_request_info`, `requester_email` | `request` | 요청 종류와 요청한 사람의 메일 주소 |
| `api_name`, `method_name` | `activity` | 앱이 부른 API 와 메서드 |
| `num_response_bytes` | `activity` | 응답 크기(바이트) |
| `product_bucket` | `activity` | 호출이 속한 제품 묶음 |

값이 정해진 매개변수는 아래 값만 씁니다[1].

- `client_type`: `WEB`, `NATIVE_ANDROID`, `NATIVE_IOS`, `NATIVE_DESKTOP`, `NATIVE_APPLICATION`, `NATIVE_CHROME_EXTENSION`, `NATIVE_DEVICE`, `NATIVE_UNIVERSAL_WINDOWS_PLATFORM`, `NATIVE_SONY`, `CONNECTED_DEVICE`, `TYPE_UNSPECIFIED`
- `rejection_type`: `EXPLICIT_ADMIN_BLOCK`(관리자가 앱을 차단), `SCOPE_BLOCK`(제한된 서비스에 접근 시도), `CAA_FOR_OIDC_BLOCK`, `EDU_UNDERAGE_BLOCK`
- `app_request_info`: `APP_REQUEST_TYPE_DELEGATED`, `APP_REQUEST_TYPE_INDIVIDUAL`
- `product_bucket`: `GMAIL`, `DRIVE`, `CALENDAR`, `CONTACTS`, `GSUITE_ADMIN`, `IDENTITY`, `VAULT`, `GROUPS`, `TASKS`, `CLASSROOM`, `CLOUD_SEARCH`, `COMMUNICATIONS`, `APPS_SCRIPT_API`, `APPS_SCRIPT_RUNTIME`, `GPLUS`, `OTHER`

아래는 `authorize` 한 건을 보고서 API 레코드 모양대로 만든 예시입니다. 고객 ID 는 문서 예시 값이고 나머지 값은 지어낸 것입니다.

```json
{
  "kind": "audit#activity",
  "id": {
    "time": "2026-03-02T01:15:42.118Z",
    "uniqueQualifier": "-4719201835560123456",
    "applicationName": "token",
    "customerId": "C03az79cb"
  },
  "actor": { "email": "user@example.com", "profileId": "100000000000000000001" },
  "ipAddress": "203.0.113.24",
  "events": [{
    "type": "auth",
    "name": "authorize",
    "parameters": [
      { "name": "app_name", "value": "Example Mail Sync" },
      { "name": "client_id", "value": "123456789012-abc.apps.googleusercontent.com" },
      { "name": "client_type", "value": "WEB" },
      { "name": "scope", "value": "https://mail.google.com/" }
    ]
  }]
}
```

`scope` 의 형식은 문자열(string)입니다[1]. 범위가 여러 개일 때 검체에서 `value` 와 `multiValue` 가운데 어느 칸에 들어 있는지 먼저 확인합니다.

Directory API 의 토큰 자원에는 `clientId`, `scopes[]`, `userKey`, `anonymous`(익명 클라이언트 ID 를 쓰는 앱이면 `true`), `displayText`(앱 이름), `nativeApp`(데스크톱·모바일에 설치한 앱이면 `true`), `kind`(늘 `admin#directory#token`), `etag` 가 있습니다[8]. 발급 시각을 담는 필드는 없습니다[8].

## 증거로서 의미

**증명하는 것.** `authorize` 레코드는 어느 계정이 어느 시각에 어느 앱(`client_id`·`app_name`)에 어떤 범위를 허락했는지 보여 줍니다[1][4]. `revoke` 는 접근이 끊긴 시각을, `deny` 는 관리자 정책 때문에 앱이 막혔다는 것과 그 까닭을 보여 줍니다[1]. `activity` 가 남는 에디션이라면 앱이 사용자 대신 어느 API 의 어느 메서드를 불렀고 응답이 몇 바이트였는지까지 보여 줍니다[1][4]. IP 주소는 접근을 허락·회수한 사용자의 주소이고, 프록시나 VPN 주소일 수도 있습니다[4].

**증명하지 못하는 것.** 앱이 받은 데이터의 내용은 남지 않고, `num_response_bytes` 는 크기만 알려 줍니다[1]. `activity` 가 없는 에디션에서는 허락 뒤에 앱이 실제로 데이터를 읽었는지 이 로그로 알 수 없습니다[4]. 앱을 누가 만들었는지도 이 로그에는 없고, `client_id` 로 API controls 에서 앱 정보(개인정보 처리방침·지원 정보·확인 상태)를 따로 확인합니다[9]. 토큰이 다른 곳으로 새어 나가 쓰였는지는 `activity` 의 IP·클라이언트 종류로 짐작할 수 있을 뿐입니다. 토큰 만료처럼 사용자가 직접 하지 않은 이벤트에는 IP 가 없을 수 있습니다[4].

보고서에는 "2026-03-02 01:15 UTC 에 user@example.com 계정으로 클라이언트 ID 123456789012-abc 앱에 `https://mail.google.com/` 범위를 허락한 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다(예시 값은 만든 것입니다).

## 시각 해석

보고서 API 의 `id.time` 은 이벤트가 일어난 시각입니다. 필드 설명(UNIX epoch 초)과 문서 예시(RFC 3339)의 형식이 서로 달라서[3] 검체의 값 모양을 보고 판단하고, 자세한 내용은 [관리 콘솔 감사 로그](./admin-audit.md)에 있습니다. 관리 콘솔 OAuth log events 화면의 Date 는 브라우저의 기본 시간대로 보여 주므로, 화면을 내보낸 파일과 API 로 받은 UTC 값을 섞을 때 시간대를 먼저 맞춥니다[4]. 여러 로그의 시각을 맞추는 방법은 [클라우드의 시각](../../01-foundations/logging/timestamps.md)에서 다룹니다.

지연 시간은 OAuth 항목이 "Up to a few hours", Token log events 항목이 "A couple of hours" 이고 관리 콘솔과 보고서 API 에 똑같이 적용되므로, 토큰 기록은 몇 시간 늦게 들어온다고 보면 됩니다[5]. 드물게 이보다 더 늦거나 아예 보고되지 않는 이벤트가 있을 수 있습니다[5]. 사고 직후에 조회해서 `authorize` 가 없다면 몇 시간 뒤에 다시 조회합니다.

API controls 화면은 더 늦습니다. 제3자 앱 정보는 허락 뒤 보통 24~48시간 뒤에 나타나고, Accessed apps 목록은 토큰을 발급·회수하고 48시간 뒤에 갱신됩니다[9].

## 함정과 한계

- **로그와 현재 상태는 다릅니다.** Directory API `tokens.list` 는 사용자가 지금 발급해 둔 토큰만 돌려주고 발급 시각 필드가 없으며[8], API controls 의 Accessed apps 는 앱별 사용자 수와 요청한 서비스만 보여 줍니다[9]. 이미 회수한 토큰은 이 목록에서 사라지므로 과거의 허락은 토큰 기록에서 찾습니다.
- **관리자가 한 회수는 관리 로그에 남습니다.** 관리자가 사용자의 토큰을 회수하면 Admin 로그에 `REVOKE_3LO_TOKEN`(매개변수 `APP_ID`·`USER_EMAIL`)이나 `REVOKE_3LO_DEVICE_TOKENS` 가 남습니다[10]. Directory API `tokens.delete` 는 그 사용자가 그 앱에 발급한 모든 액세스 토큰을 지웁니다[8].
- **정책을 바꾸면 토큰이 한꺼번에 사라집니다.** 서비스 접근을 Restricted 로 바꾸면 신뢰하지 않은 앱은 멈추고 토큰이 회수됩니다[9]. 회수 이벤트가 한 시각에 몰려 있으면 먼저 Admin 로그에서 앱 접근 설정 변경을 찾습니다. 옛 이벤트 이름 `ADD_TO_TRUSTED_OAUTH2_APPS`·`ADD_TO_BLOCKED_OAUTH2_APPS`·`ADD_TO_LIMITED_OAUTH2_APPS` 는 `CHANGE_APP_ACCESS` 로, `ALLOW_SERVICE_FOR_OAUTH2_ACCESS`·`DISALLOW_SERVICE_FOR_OAUTH2_ACCESS` 는 `CHANGE_API_ACCESS` 로 이름이 바뀌었으므로 두 이름을 함께 찾습니다[11][12].
- **도메인 전체 위임은 토큰 기록에 없습니다.** 서비스 계정에 도메인 전체 권한을 주는 작업은 Admin 로그의 `AUTHORIZE_API_CLIENT_ACCESS`(매개변수 `API_CLIENT_NAME`·`API_SCOPES`·`DOMAIN_NAME`)로 남습니다[13][15]. 앱이 사용자를 가장해 한 작업은 보고서 API 레코드의 `actor.applicationInfo.impersonation` 이 `true` 로 드러납니다[3]. 관리 설정 변경을 따라가는 방법은 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md)에 있습니다.
- **탐지 규칙 공백.** SigmaHQ 의 Google Workspace 규칙에는 토큰 기록을 대상으로 한 규칙이 없습니다[15]. ALFA 는 `authorize` 를 MITRE ATT&CK 의 애플리케이션 액세스 토큰 탈취와 대체 인증 수단 사용으로, `activity` 를 애플리케이션 액세스 토큰을 쓴 측면 이동으로 분류합니다[14]. 이 분류는 정상 앱의 동의와 호출에도 똑같이 붙으므로 그 자체로 침해의 근거가 되지 않습니다.
- **이름 바꾼 사용자.** 사용자 이름을 바꾸면 관리 콘솔에서 옛 이름으로는 검색 결과가 나오지 않습니다[4].

## 직접 분석해 보기

보고서 API 로 받은 원본 JSON 을 먼저 보존하고, 그 사본으로 분석합니다. 보존 순서는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)에 있습니다. 호출 모양은 아래와 같고, `eventName` 을 붙이면 특정 이벤트만 받습니다[2]. 특정 앱만 볼 때는 `eventName` 과 함께 `filters=client_id==클라이언트ID` 처럼 이벤트 매개변수로 거릅니다[3]. `applicationInfoFilter` 는 `actor.applicationInfo` 의 `oauthClientId` 를 거르는 매개변수라 `client_id` 매개변수와는 다른 칸입니다[3].

```text
GET https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/token?maxResults=25
GET https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/token?eventName=revoke&maxResults=25
```

공개 도구 ALFA 는 보고서 API 를 불러 활동 한 건을 한 줄로 저장하고, 결과는 수집 시각(UTC)으로 이름 붙인 `data/` 아래 폴더의 `token.json` 에 쌓입니다[14]. `--start-time`·`--end-time` 에 시간대를 붙이지 않으면 UTC 로 봅니다[14].

```sh
alfa acquire --logtype=token --start-time 2026-03-01T00:00:00Z --end-time 2026-03-08T00:00:00Z
```

한 줄 한 활동인 파일에서 이벤트별로 시각·계정·IP·앱·범위를 뽑습니다. 매개변수는 `value`·`multiValue`·`intValue` 가운데 값이 든 칸을 씁니다[3].

```sh
jq -r '
  .id.time as $t | .actor.email as $u | (.ipAddress // "-") as $ip
  | .events[]
  | (reduce (.parameters // [])[] as $x ({}; .[$x.name] = ($x.value // $x.multiValue // $x.intValue))) as $p
  | [$t, $u, $ip, .name, $p.client_id, $p.app_name, ($p.scope|tostring), ($p.method_name // "-"), ($p.num_response_bytes // "-")]
  | @tsv' token.json | sort
```

결과에서 볼 것은 세 가지입니다. 같은 `client_id` 의 `authorize` 뒤에 `activity` 가 이어지는지, 그 `activity` 의 IP 가 사용자가 평소 로그인하는 IP 와 같은지, `revoke` 가 언제 나오는지입니다. IP 를 해석할 때 주의할 점은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md)에 있습니다.

현재 남은 토큰은 Directory API `tokens.list` 로 사용자마다 받고[8], 조직 전체는 API controls 의 Accessed apps 목록에서 Download list 로 CSV 를 받습니다[9].

## 교차 검증

- 허락 직전의 로그인은 [로그인 기록](./login-audit.md)에서 찾습니다. 로그인 IP 와 `authorize` IP 를 나란히 놓습니다.
- `activity` 의 `product_bucket` 이 `DRIVE` 나 `GMAIL` 이면 같은 시간대의 [Drive 기록](./drive-audit.md)과 [Gmail 기록과 메일 검색](./gmail.md)을 봅니다.
- 앱 신뢰·차단, 도메인 전체 위임, 관리자의 토큰 회수는 [관리 콘솔 감사 로그](./admin-audit.md)에서 봅니다.
- Microsoft 365 에서 같은 역할을 하는 기록은 [Entra ID 로그](../m365/entra-logs/index.md)에 있습니다.
- 여러 로그를 시간순으로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)에, 조사 흐름은 [악성 OAuth 앱에 동의했나](../../04-scenarios/account-compromise/illicit-consent.md)와 [토큰을 훔쳐 로그인했나](../../04-scenarios/account-compromise/token-theft.md)에 있습니다.

## 실습

시험용 Workspace 도메인에서 테스트 계정으로 앱 하나에 Gmail 읽기 범위를 허락하고, 몇 번 쓴 뒤 계정 설정에서 접근을 회수한 다음 아래 질문을 풀어 봅니다.

1. `authorize` 와 `revoke` 레코드의 `id.time` 은 각각 언제이고, 관리 콘솔 화면의 Date 와 몇 시간 차이가 나는가?
2. 허락 직후와 몇 시간 뒤에 조회한 결과가 다른가? 레코드가 처음 보인 때를 적어 둔다.
3. 에디션에 `activity` 가 남는다면 `method_name` 과 `num_response_bytes` 로 앱이 무엇을 얼마나 불렀는지 정리할 수 있는가?
4. 회수 전과 후에 `tokens.list` 결과는 어떻게 달라지고, 회수한 뒤 토큰 기록에는 무엇이 남는가?
5. `scope` 값은 레코드의 어느 칸(`value`·`multiValue`)에 들어 있는가?

## 참고 문헌

1. Google, "OAuth Token Audit Activity Events", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/token
2. Google, "Reports API: Authorization Tokens Activity Report", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/guides/manage-audit-tokens
3. Google, "Method: activities.list", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
4. Google, "OAuth log events", Google Workspace Admin Help. https://support.google.com/a/answer/6124308
5. Google, "Data retention and lag times", Google Workspace Admin Help. https://support.google.com/a/answer/7061566
6. Google Cloud, "Google Workspace audit logging", Cloud Logging. https://cloud.google.com/logging/docs/audit/gsuite-audit-logging
7. Google, "Share data with Google Cloud services", Google Workspace Admin Help. https://support.google.com/a/answer/9320190
8. Google, "REST Resource: tokens", Admin SDK Directory API. https://developers.google.com/workspace/admin/directory/reference/rest/v1/tokens
9. Google, "Control which third-party & internal apps access Google Workspace data", Google Workspace Admin Help. https://knowledge.workspace.google.com/admin/apps/control-which-third-party-and-internal-apps-access-google-workspace-data
10. Google, "Admin Audit Activity Events - User Settings", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-user-settings
11. Google, "Admin Audit Activity Events - Security Settings", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-security-settings
12. Google, "Admin log event changes", Google Workspace Admin Help. https://knowledge.workspace.google.com/admin/reports/admin-log-event-changes
13. Google, "Admin Audit Activity Events - Domain Settings", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-domain-settings
14. Invictus IR, ALFA (Automated Audit Log Forensic Analysis for Google Workspace), `alfa/cmdline.py`·`alfa/main/collector.py`·`alfa/utils/mappings.yml`. https://github.com/invictus-ir/ALFA
15. SigmaHQ, Google Workspace 규칙 모음과 gcp_gworkspace_granted_domain_api_access.yml. https://github.com/SigmaHQ/sigma/tree/master/rules/cloud/gcp/gworkspace
