---
title: "관리 콘솔 감사 로그"
parent: "아티팩트 · Google Workspace"
nav_order: 290
---

# 관리 콘솔 감사 로그 (Admin Audit)

관리 콘솔 감사 로그는 Google Workspace 관리자가 관리 콘솔 (Admin console) 에서 사용자·역할·보안 설정을 바꾼 일을 남기는 기록이고, 바뀌기 전 값과 바뀐 값까지 함께 남아 권한 변화를 따라갈 때 가장 먼저 봅니다[2][12].

## 무엇을 기록하나 · 왜 생기나

관리자가 사용자를 추가하거나 Workspace 서비스를 켜면 관리 콘솔 감사 로그에 한 건이 생깁니다[12][16]. 관리 콘솔 화면에서는 "Admin log events", 보고서 API (Reports API) 에서는 applicationName `admin`, Cloud Logging 으로 공유한 사본에서는 서비스 이름 `admin.googleapis.com` 으로 부릅니다[2][12][16]. 관리자는 이 기록을 지우거나 보관 기간을 바꿀 수 없습니다[11].

이벤트는 유형(`events[].type`)으로 묶입니다. 이벤트 이름 목록에 있는 유형은 `APPLICATION_SETTINGS`, `CALENDAR_SETTINGS`, `CHAT_SETTINGS`, `CHROME OS_SETTINGS`, `CONTACTS_SETTINGS`, `DELEGATED_ADMIN`, `DOCS_SETTINGS`, `DOMAIN_SETTINGS`, `EMAIL_SETTINGS`, `GROUP_SETTINGS`, `LICENSES_SETTINGS`, `MOBILE_SETTINGS`, `ORG_SETTINGS`, `SECURITY_SETTINGS`, `SITES_SETTINGS`, `USER_SETTINGS` 입니다[3]. 위임 관리 이벤트는 부록 페이지와 Cloud Logging 에서 `DELEGATED_ADMIN_SETTINGS` 로 나오고, Chrome OS 설정도 Cloud Logging 에서는 밑줄을 쓴 `CHROME_OS_SETTINGS` 입니다[3][7][16]. 실제 로그에서는 두 철자를 모두 검색합니다.

조사에서 자주 보는 이벤트는 아래와 같고, 이름과 매개변수는 보고서 API 가 돌려주는 값입니다.

| 유형 | 이벤트 이름 | 주요 매개변수 | 조사에서 뜻하는 것 |
|---|---|---|---|
| `USER_SETTINGS` | `CREATE_USER`, `DELETE_USER`, `UNDELETE_USER`, `SUSPEND_USER`, `UNSUSPEND_USER`, `RENAME_USER` | `USER_EMAIL`, `NEW_VALUE`(`RENAME_USER` 의 새 이름) | 계정을 만들거나 지우거나 멈추거나 이름을 바꿈[4] |
| `USER_SETTINGS` | `CHANGE_PASSWORD`, `CHANGE_PASSWORD_ON_NEXT_LOGIN` | `USER_EMAIL`, `OLD_VALUE`·`NEW_VALUE`(다음 로그인 때 바꿔야 하는지, true·false) | 관리자가 사용자 비밀번호를 바꾸거나 다음 로그인 때 바꾸게 함[4] |
| `USER_SETTINGS` | `GRANT_ADMIN_PRIVILEGE`, `REVOKE_ADMIN_PRIVILEGE`, `GRANT_DELEGATED_ADMIN_PRIVILEGES` | `USER_EMAIL`, `NEW_VALUE`(위임 관리자 권한) | 관리자 권한을 주거나 거두고, 위임 관리자 권한을 줌[4] |
| `USER_SETTINGS` | `TURN_OFF_2_STEP_VERIFICATION`, `GENERATE_2SV_SCRATCH_CODES`, `REVOKE_SECURITY_KEY`, `UNENROLL_USER_FROM_TITANIUM` | `USER_EMAIL` | 사용자의 2단계 인증을 끄거나 백업 코드를 만들고, 보안 키를 취소하거나 고급 보호 (Advanced Protection) 에서 뺌[4] |
| `USER_SETTINGS` | `ADD_RECOVERY_EMAIL`, `ADD_RECOVERY_PHONE` | `USER_EMAIL` | 복구 수단을 더함[4] |
| `USER_SETTINGS` | `CREATE_EMAIL_MONITOR` | `USER_EMAIL`, `EMAIL_MONITOR_DEST_EMAIL`, `BEGIN_DATE_TIME`, `END_DATE_TIME` | 한 사용자에 대해 `EMAIL_MONITOR_DEST_EMAIL` 주소로 가는 메일 모니터를 만듦[4] |
| `USER_SETTINGS` | `CREATE_DATA_TRANSFER_REQUEST`, `DOWNLOAD_USERLIST_CSV` | `USER_EMAIL`, `DESTINATION_USER_EMAIL`, `APPLICATION_NAME` | 자료를 다른 사용자에게 넘기는 요청을 만들거나 사용자 목록을 CSV 로 내려받음[4] |
| `DELEGATED_ADMIN_SETTINGS` | `CREATE_ROLE`, `DELETE_ROLE`, `ADD_PRIVILEGE`, `REMOVE_PRIVILEGE`, `ASSIGN_ROLE`, `UNASSIGN_ROLE` | `ROLE_NAME`, `PRIVILEGE_NAME`, `USER_EMAIL`, `ORG_UNIT_NAME` | 관리자 역할을 만들고 권한을 붙이고 사람에게 줌[7] |
| `SECURITY_SETTINGS` | `ENFORCE_STRONG_AUTHENTICATION` | `SETTING_NAME`, `OLD_VALUE`, `NEW_VALUE`, `ORG_UNIT_NAME` | 조직의 2단계 인증 강제를 바꿈[5] |
| `SECURITY_SETTINGS` | `ADD_TO_TRUSTED_OAUTH2_APPS`, `ALLOW_SERVICE_FOR_OAUTH2_ACCESS` | `OAUTH2_APP_ID`, `OAUTH2_APP_NAME`, `OAUTH2_SERVICE_NAME` | 외부 앱을 신뢰 목록에 넣거나 한 서비스의 API 접근을 허용함(2026년 8월 뒤 이름이 바뀜, 아래 참고)[5][13] |
| `DOMAIN_SETTINGS` | `AUTHORIZE_API_CLIENT_ACCESS`, `REMOVE_API_CLIENT_ACCESS` | `API_CLIENT_NAME`, `API_SCOPES`, `DOMAIN_NAME` | API 클라이언트에 조직 접근을 허용하거나 없앰[6] |
| `DOMAIN_SETTINGS` | `TOGGLE_SSO_ENABLED`, `CHANGE_SSO_SETTINGS` | `DOMAIN_NAME`, `NEW_VALUE` | SSO 를 켜고 끄거나 SSO 설정을 바꿈[6] |
| `APPLICATION_SETTINGS` | `CHANGE_APPLICATION_SETTING` | `APPLICATION_NAME`, `SETTING_NAME`, `OLD_VALUE`, `NEW_VALUE`, `ORG_UNIT_NAME` | 서비스 설정값을 바꿈[8] |
| `EMAIL_SETTINGS` | `CREATE_GMAIL_SETTING`, `CHANGE_GMAIL_SETTING`, `EMAIL_LOG_SEARCH`, `EMAIL_UNDELETE` | `SETTING_NAME`, `EMAIL_LOG_SEARCH_SENDER`, `EMAIL_LOG_SEARCH_RECIPIENT` | Gmail 설정을 만들거나 바꾸고, 메일 로그를 검색하거나 사용자 메일 복원을 시작함[9] |
| `DOCS_SETTINGS` | `TRANSFER_DOCUMENT_OWNERSHIP`, `DRIVE_DATA_RESTORE` | `USER_EMAIL`, `NEW_VALUE` | 문서 소유자를 다른 사용자로 바꾸거나 사용자의 Drive 자료 복원을 시작함[10] |

관리 콘솔 화면에는 같은 이벤트가 문장으로 보입니다. 예를 들어 `CHANGE_APPLICATION_SETTING` 은 `For {APPLICATION_NAME}, {SETTING_NAME} changed from {OLD_VALUE} to {NEW_VALUE}`, `AUTHORIZE_API_CLIENT_ACCESS` 는 `API client access to your organization from client {API_CLIENT_NAME} authorized for scopes {API_SCOPES}` 틀로 표시됩니다[6][8]. 이 문장은 화면 표시용이고, API·내보내기 자료에는 이벤트 이름과 매개변수로 들어옵니다.

Cloud Logging 사본에는 위 유형 말고도 `ALERT_CENTER`, `SECURITY_INVESTIGATION`, `DEVICE_SETTINGS`, `LABELS`, `AI_CLASSIFICATION_SETTINGS` 유형이 있고, 메서드 이름은 `google.admin.AdminService.grantAdminPrivilege` 처럼 `google.admin.AdminService.` 뒤에 동작을 붙인 모양입니다[16]. 알림 삭제(`alertCenterBatchDeleteAlerts`), 보안 조사 도구 검색(`securityInvestigationQuery`), 조사 도구에서 본문 열람(`securityInvestigationContentAccess`)도 이 목록에 있습니다[16].

## 위치와 버전별 차이

### 어디서 보나

| 경로 | 받는 모양 | 조건(2026년 9월 문서 기준) |
|---|---|---|
| 관리 콘솔 Reporting > Audit and investigation > Admin log events | 화면 표, Sheets·CSV 내보내기 최대 100,000행 | Audit & Investigation 관리자 권한, 기본 검색 범위 최근 7일[12] |
| Security > Security center > Investigation tool, 데이터 원본 Admin log events | 화면 표, 내보내기 최대 3천만 행 | Frontline Standard·Plus, Enterprise Standard·Plus, Education Standard·Plus, Enterprise Essentials Plus, Cloud Identity Premium[12] |
| 보고서 API `activities.list` | JSON, 활동 한 건이 레코드 하나 | 권한 범위 `https://www.googleapis.com/auth/admin.reports.audit.readonly`[1] |
| BigQuery 내보내기 | 일별 `activity_` 표의 행[19] | Frontline Standard·Plus, Enterprise Standard·Plus, Education Standard·Plus, Enterprise Essentials Plus[14] |
| Cloud Logging 공유 | `LogEntry` 안의 `protoPayload` | 모든 계정에서 Admin 로그를 공유할 수 있음. 최고 관리자가 Account settings > Legal and compliance > Sharing options 에서 켬[15] |

관리 콘솔 검색은 대상 사용자의 Workspace 에디션과 관계없이 모든 사용자를 대상으로 할 수 있습니다[12]. 보고서 API 요청은 `GET https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/admin` 모양이고, `all` 자리에 관리자 한 명의 기본 메일 주소를 넣으면 그 관리자가 한 일만 받습니다[2].

### 보관 기간과 지연 시간

Workspace 감사 로그 전체의 보관 기간을 이 페이지에 모아 둡니다. 다른 서비스와의 비교는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에 있습니다. 2026년 9월 문서 기준입니다.

| 로그 | 보관 | 기록에서 조회까지 걸리는 시간 |
|---|---|---|
| Admin log events | 6개월[11] | 몇 분[11] |
| User log events(옛 이름 Login audit log) | 6개월[11] | 로그인 이벤트는 몇 분, 사용자 계정 이벤트는 수십 분[11] |
| Drive log events | 6개월[11] | 몇 분[11] |
| Gmail log events | 6개월[11] | 몇 분[11] |
| Email Log Search | 30일[11] | 해당 없음 |
| OAuth Token log events | 6개월[11] | Token 로그는 두어 시간, OAuth 는 몇 시간까지[11] |
| SAML log events | 6개월[11] | 몇 분[11] |
| Vault log events | 무기한(Indefinite)[11] | 몇 분[11] |
| Takeout 등 표에 없는 로그 | 대체로 6개월[11] | Takeout 시작은 거의 바로, 끝은 자료 크기에 따라 며칠까지[11] |
| API 로 받는 감사 자료 | 6개월[11] | 위와 같음 |

보고서 API 로 받을 수 있는 기간은 최근 180일이고[2], `endTime` 을 주지 않으면 `startTime` 부터 지금까지, `startTime` 이 180일보다 오래되면 최근 180일만 돌려줍니다[1]. 드물게 적힌 시간보다 늦게 들어오거나 아예 보고되지 않는 이벤트도 있을 수 있습니다[11].

관리 콘솔 밖에 따로 쌓은 사본은 보관 규칙이 다릅니다. Cloud Logging 으로 공유한 사본은 Google Cloud 쪽 관리 활동 감사 로그 보관 정책을 따르고, 공유를 끄면 새 자료만 멈추며 이미 넘어간 자료는 그 보관 기간까지 남습니다[15][16]. 관리 콘솔 감사 로그는 Cloud Logging 에서 관리 활동 (Admin Activity) 로그로만 기록되므로 조직의 `_Required` 버킷에 들어가고, 이 버킷의 보관 기간은 바꿀 수 없습니다[16]. 버킷 보관 기간 값은 [Cloud Audit Logs](../gcp/cloud-audit-logs.md)에 있습니다. BigQuery 자료에는 활동 자료 180일치 과거 기록이 들어 있습니다[14].

## 구조

### 보고서 API 레코드

보고서 API 는 활동 (activity) 하나를 레코드 하나로 돌려주고, 활동 안에 이벤트가 하나 이상 들어 있습니다[1]. 아래는 문서의 응답 예시 모양을 따라 만든 예시이고, 메일 주소·IP·ID 는 모두 지어낸 값입니다[1][2].

```json
{
  "kind": "audit#activity",
  "id": {
    "time": "2026-09-14T02:31:07.412Z",
    "uniqueQualifier": "-4817203958817261234",
    "applicationName": "admin",
    "customerId": "C03az79cb"
  },
  "actor": {
    "callerType": "USER",
    "email": "admin@example.com",
    "profileId": "114455667788990011223"
  },
  "ownerDomain": "example.com",
  "ipAddress": "203.0.113.25",
  "networkInfo": {
    "ipAsn": [64500],
    "regionCode": "KR"
  },
  "events": [
    {
      "type": "USER_SETTINGS",
      "name": "GRANT_DELEGATED_ADMIN_PRIVILEGES",
      "parameters": [
        { "name": "NEW_VALUE", "value": "Help Desk Admin" },
        { "name": "USER_EMAIL", "value": "user@example.com" }
      ]
    }
  ]
}
```

| 필드 | 뜻 |
|---|---|
| `id.time` | 활동이 일어난 시각[1] |
| `id.uniqueQualifier` | 같은 시각에 활동이 여럿일 때 구별하는 int64 값[1] |
| `id.applicationName`, `id.customerId` | 로그 종류(`admin`)와 Workspace 계정 식별자[1] |
| `actor.email` | 동작한 사람의 기본 메일 주소. 메일 주소가 없는 주체면 빠짐[1] |
| `actor.profileId` | 동작한 사람의 Workspace 프로필 ID. Workspace 사용자가 아니면 없거나 자리 표시 값 `105250506097979753968` 일 수 있음[1] |
| `actor.callerType` | 주체 종류. `KEY` 일 때만 `actor.key` 에 OAuth 2LO 요청자의 consumer key 나 로봇 계정 식별자가 들어감[1] |
| `actor.applicationInfo` | 앱이 동작했을 때 `oauthClientId`, `applicationName`, `impersonation`(사용자로 가장했는지)[1] |
| `ipAddress` | 동작한 사람의 IP. IPv4·IPv6 모두 올 수 있음[1] |
| `networkInfo` | `ipAsn[]`, `regionCode`(ISO 3166-1 alpha-2), `subdivisionCode`(ISO 3166-2)[1] |
| `events[].type`, `events[].name` | 이벤트 유형과 이름[1] |
| `events[].parameters[]` | `name` 과 값 필드 `value`·`multiValue`·`intValue`·`multiIntValue`·`boolValue`·`messageValue`·`multiMessageValue`[1] |

`userDeviceInfo` 필드는 Drive·Chrome·SAML 같은 일부 applicationName 에만 있고 `admin` 에는 없습니다[1]. 관리 콘솔 화면의 Actor 열에는 메일 주소 대신 License manager(관리자 동작으로 사용자 라이선스가 바뀐 경우), Service account 나 Anonymous(서비스 계정 관리자가 한 동작)가 보일 수 있습니다[12].

### BigQuery 와 Cloud Logging 의 이름

같은 기록이라도 받는 경로마다 이름이 다릅니다. 보고서 API 는 매개변수 이름을 대문자(`NEW_VALUE`)로 주고[4], BigQuery 내보내기는 `event_name`, `admin.old_value`, `admin.new_value`, `admin.setting_name` 열을 씁니다[13]. Cloud Logging 사본은 `protoPayload.metadata.event[]` 아래에 `eventName`·`eventType`·`parameter[]` 를 두고, 시각 식별자를 `protoPayload.metadata.activityId.timeUsec`·`uniqQualifier` 로 둡니다[16]. `LogEntry` 쪽 필드 읽는 법은 [Cloud Audit Logs](../gcp/cloud-audit-logs.md)에 있습니다.

## 증거로서 의미

### 증명하는 것

- 어느 관리자 계정(`actor.email`)이 언제(`id.time`) 어느 IP(`ipAddress`)에서 어떤 사용자·역할·설정을 바꿨는지[1][4].
- 설정이 무엇에서 무엇으로 바뀌었는지(`OLD_VALUE`·`NEW_VALUE`), 어느 조직 단위에 걸린 설정인지(`ORG_UNIT_NAME`)[5][8].
- 사람이 아니라 앱이 한 동작인지, 그 앱이 사용자로 가장했는지(`actor.applicationInfo.oauthClientId`·`impersonation`)[1][12].
- 관리자가 메일 로그 검색, 보안 조사 도구 검색·본문 열람, 알림 삭제를 했다는 것[9][16].

### 증명하지 못하는 것

- 그 관리자 계정을 실제로 누가 조작했는지. 기록은 계정까지만 말합니다.
- 동작한 사람의 실제 위치. `ipAddress` 는 프록시나 VPN 주소일 수 있습니다[1].
- groups.google.com 처럼 관리 콘솔 밖에서 바꾼 그룹 설정. 이 변경은 Enterprise Groups 감사 로그에 남습니다[16].
- 사용자가 스스로 자기 계정에 한 일(비밀번호 변경, 2단계 인증 등록). 이 기록은 [로그인 기록](./login-audit.md)에 있습니다.
- 권한을 받은 뒤 실제로 그 권한을 썼는지. 쓴 흔적은 해당 서비스의 로그에서 따로 찾습니다.

## 시각 해석

보고서 API 문서의 응답 예시는 `id.time` 을 `2011-06-17T15:39:18.460Z` 처럼 `Z` 로 끝나는 RFC 3339 UTC 문자열로 보여 주지만, 같은 문서 묶음의 필드 설명은 "UNIX epoch time in seconds" 라고 적습니다[1][2]. 두 설명이 다르므로 실제 로그의 값 모양을 보고 판단합니다. 문자열 끝이 `Z` 이면 UTC 입니다.

`id.time` 은 관리자가 동작한 시각이고, 조회할 수 있게 되는 시각은 몇 분 늦습니다[11]. Cloud Logging 사본에는 작업 시각 `timestamp` 와 Cloud Logging 이 받은 시각 `receiveTimestamp` 가 따로 있고, 문서 예시에서는 두 값이 1시간 35분쯤 벌어져 있습니다[16]. 타임라인에는 `timestamp`(또는 `activityId.timeUsec`, 마이크로초 단위 UNIX 시각)를 씁니다[16].

관리 콘솔 화면의 Date 는 보는 사람 브라우저의 기본 시간대로 표시됩니다[12]. 보안 조사 도구에서는 최고 관리자가 조사 시간대를 바꿀 수 있고, 그 시간대가 검색 조건과 결과에 함께 적용됩니다[12]. 화면에서 내보낸 CSV 를 쓸 때는 내보낸 사람의 시간대를 함께 기록해 둡니다.

BigQuery 표는 `time_usec` 열로 하루 단위 파티션(`_PARTITIONTIME`)을 만드는데, 파티션 경계를 UTC 가 아닌 태평양 시간 (Pacific Time) 에 맞춥니다[14]. UTC 기준 하루치를 뽑으려면 파티션 조건만 쓰지 말고 `time_usec` 로 다시 거릅니다[14]. 여러 클라우드의 시각을 맞추는 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 있습니다.

## 함정과 한계

**2026년 8월 전후로 이벤트 이름이 다릅니다.** Google 은 관리 로그 이벤트 이름과 유형 일부를 바꾸고 있고, 2026년 8월까지는 옛 이름과 새 이름이 함께 나오다가 그 뒤에는 새 이름만 남습니다[13]. OAuth 앱 허용·차단 목록 이벤트(`ADD_TO_TRUSTED_OAUTH2_APPS`, `ADD_TO_BLOCKED_OAUTH2_APPS`, `ADD_TO_LIMITED_OAUTH2_APPS`)는 `CHANGE_APP_ACCESS` 로, `ALLOW_SERVICE_FOR_OAUTH2_ACCESS`·`DISALLOW_SERVICE_FOR_OAUTH2_ACCESS` 는 `CHANGE_API_ACCESS` 로 바뀝니다[13]. Drive 설정을 상속값에서 덮어쓰거나 상속으로 되돌린 일은 전에는 `CHANGE_DOCS_SETTING` 에 `INHERIT_FROM_PARENT` 값으로 남았고, 바뀐 뒤에는 `APPLICATION_SETTINGS` 유형의 `CREATE_APPLICATION_SETTING`·`CHANGE_APPLICATION_SETTING`·`DELETE_APPLICATION_SETTING` 으로 남습니다[13]. 저장해 둔 조사는 옛 이벤트 기준이라 2026년 8월 뒤에는 동작을 멈춥니다[13]. 기간이 이 경계에 걸치면 옛 이름과 새 이름을 모두 검색합니다.

**조사하는 사람의 흔적도 섞입니다.** 메일 로그 검색(`EMAIL_LOG_SEARCH`)과 보안 조사 도구 사용(`securityInvestigationQuery` 등)도 관리 로그에 남습니다[9][16]. 조사에 쓴 계정과 시각을 따로 적어 두면 나중에 걸러낼 수 있습니다.

**`eventName` 필터는 활동을 통째로 돌려줍니다.** 보고서 API 에 `eventName` 을 주면 그 이벤트가 든 활동을 돌려주고, 그 활동 안의 다른 이벤트도 함께 옵니다[2]. 건수를 셀 때는 활동이 아니라 `events[]` 를 펼쳐서 셉니다.

**이름을 바꾼 사용자는 옛 이름으로 검색되지 않습니다.** OldName@example.com 을 NewName@example.com 으로 바꾸면 옛 주소로 한 검색에는 결과가 나오지 않습니다[12]. `RENAME_USER` 이벤트로 이름 변경 이력을 먼저 확인합니다[4]. 지운 사용자는 메일 주소로 `userKey` 를 지정할 수 없고, Directory API `users.list` 에 `showDeleted=true` 를 주어 받은 ID 를 `userKey` 로 씁니다[1].

**받는 경로마다 자료가 다릅니다.** BigQuery 에는 필터 없는 전체 자료만 있고, 보고서 API 의 `orgUnitID` 필터에 해당하는 열이 없습니다[14]. 같은 BigQuery 설정 문서에 "표는 자동으로 지워지지 않는다" 는 문장과 "내보낸 자료의 기본 만료는 60일" 이라는 문장이 함께 있으므로, 데이터 세트의 표 만료 설정을 직접 확인합니다[14].

**탐지 규칙의 필드 이름은 수집한 로그 형식에 맞춰야 합니다.** SigmaHQ 의 Workspace 관리 규칙은 `eventService: admin.googleapis.com`, `eventName`, `new_value`, `setting_name` 처럼 평평한 필드를 쓰고, 같은 분류의 로그인 규칙은 Cloud Logging 의 `protoPayload.*` 필드를 씁니다[18]. 보고서 API JSON 이나 BigQuery 표에 규칙을 돌리려면 필드 이름을 바꿔 맞춥니다. 규칙을 옮기는 방법은 [탐지 규칙으로 로그 검색하기](../../03-techniques/analysis/detection-rules.md)에 있습니다.

### 지우기·조작

관리자는 로그 이벤트를 지우거나 보관 기간을 줄일 수 없습니다[11]. 그래서 흔적을 없애려는 시도는 다른 모양으로 남습니다. 알림 센터에서 알림을 지우면 `alertCenterBatchDeleteAlerts` 가 관리 로그에 남고, Cloud Logging 공유를 끄면 그 뒤 새 자료만 Cloud 로 넘어가지 않을 뿐 관리 콘솔 쪽 기록은 그대로입니다[15][16]. 공개 분석 도구 ALFA 는 `ALERT_CENTER_BATCH_DELETE_ALERTS`·`ALERT_CENTER_DELETE_ALERT` 를 방어 회피, `CREATE_EMAIL_MONITOR`·`CREATE_GMAIL_SETTING` 을 메일 수집으로 분류합니다[17]. 조사 흐름은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)에 있습니다.

## 직접 분석해 보기

### 원문 JSON 을 한 번 따라가기

보고서 API 로 특정 이벤트만 받는 요청은 문서 예시와 같은 모양입니다[4].

```text
GET https://admin.googleapis.com/admin/reports/v1/activity/users/all/applications/admin?eventName=GRANT_ADMIN_PRIVILEGE&maxResults=10
```

기간을 정할 때는 `startTime`·`endTime` 에 `2026-09-01T00:00:00.000Z` 같은 RFC 3339 값을 줍니다[2]. 받은 레코드는 다음 순서로 읽습니다.

1. `id.applicationName` 이 `admin` 인지 보고, `id.time` 의 모양으로 시각 형식을 정합니다.
2. `actor.callerType`·`actor.email` 로 사람인지, `actor.applicationInfo` 가 있으면 어느 앱이 동작했는지 봅니다.
3. `ipAddress`·`networkInfo` 를 같은 관리자의 [로그인 기록](./login-audit.md) IP 와 맞춰 봅니다.
4. `events[]` 를 하나씩 펼쳐 `type`·`name` 을 위 표와 맞추고, `parameters[]` 에서 `USER_EMAIL`·`OLD_VALUE`·`NEW_VALUE` 를 꺼냅니다.

한 줄에 활동 하나인 JSON 파일이라면 `jq` 로 특정 이벤트만 뽑을 수 있습니다.

```bash
jq -c 'select(any(.events[]; .name=="GRANT_ADMIN_PRIVILEGE" or .name=="GRANT_DELEGATED_ADMIN_PRIVILEGES"))
       | {time: .id.time, actor: .actor.email, ip: .ipAddress, events: [.events[] | {name, parameters}]}' admin.json
```

### 공개 도구

ALFA 는 보고서 API 로 Workspace 감사 로그를 받아 분석하는 공개 도구입니다[17]. `alfa acquire --logtype=admin` 은 `data/` 아래 UTC 기준 `yymmdd.HHMMSS` 이름의 폴더에 `admin.json` 을 만들고, 한 줄에 활동 하나를 JSON 으로 씁니다[17]. `--user` 로 관리자 한 명만, `--start-time`·`--end-time` 으로 기간을 정하는데, 시간대를 적지 않은 값은 UTC 로 봅니다[17]. 한 페이지당 결과 수(`--max-results`)는 기본값이자 최댓값이 1000이고, 429·5xx 응답은 간격을 늘려 가며 다시 요청합니다[17]. `alfa analyze` 는 기본으로 해롭지 않다고 보는 활동을 걸러 내므로(`--no-filter` 로 끔), 증거 보존용 원자료는 `acquire` 결과를 씁니다[17].

탐지 규칙으로는 SigmaHQ 의 Workspace 관리 규칙 7개가 있습니다[18]. 관리자 권한 부여(`GRANT_ADMIN_PRIVILEGE`·`GRANT_DELEGATED_ADMIN_PRIVILEGES`), 도메인 API 접근 허용(`AUTHORIZE_API_CLIENT_ACCESS`), 2단계 인증 강제 해제(`ENFORCE_STRONG_AUTHENTICATION`·`ALLOW_STRONG_AUTHENTICATION` 에 `new_value` 가 `false`), 역할 변경·삭제(`DELETE_ROLE`·`RENAME_ROLE`·`UPDATE_ROLE`), 역할 권한 삭제(`REMOVE_PRIVILEGE`), 앱 제거(`REMOVE_APPLICATION`·`REMOVE_APPLICATION_FROM_WHITELIST`), 접근 수준 변경(`CHANGE_APPLICATION_SETTING` 에 `setting_name` 이 `ContextAwareAccess` 로 시작)을 찾습니다[18].

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [로그인 기록](./login-audit.md) | 관리 작업 직전에 그 관리자 계정이 어느 IP 에서 로그인했는지, 2단계 인증을 거쳤는지 |
| [OAuth 토큰 기록](./token-audit.md) | `AUTHORIZE_API_CLIENT_ACCESS` 로 허용한 클라이언트가 그 뒤 실제로 어떤 범위로 자료에 접근했는지 |
| [Drive 기록](./drive-audit.md) | `TRANSFER_DOCUMENT_OWNERSHIP`·`DRIVE_DATA_RESTORE` 뒤 파일 쪽에 남은 소유자 변경·복원 |
| [Gmail 기록과 메일 검색](./gmail.md) | `CREATE_GMAIL_SETTING`·`CREATE_EMAIL_MONITOR` 뒤 메일이 실제로 다른 주소로 나갔는지 |
| [Vault와 Takeout](./vault-takeout.md) | 관리자가 Vault 로 자료를 내보내거나 사용자 자료를 옮긴 일 |
| [Cloud Audit Logs](../gcp/cloud-audit-logs.md) | 같은 조직의 Google Cloud 쪽에서 같은 관리자 계정이 한 IAM 변경 |

권한 변화를 시간 순서로 엮는 절차는 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md), 권한 상승 조사 흐름은 [권한을 올렸나](../../04-scenarios/infrastructure/privilege-escalation.md), 다른 기록과 시간순으로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다. 보고서에는 "관리자가 권한을 넘겼다" 가 아니라 "이 시각에 이 관리자 계정으로 이 사용자에게 이 역할을 준 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 실습

Workspace 감사 로그가 들어 있는 공개 데이터는 드뭅니다. 시험용 Workspace 테넌트나 위의 만든 예시 레코드로 풀어 봅니다.

1. 위 예시 레코드에서 권한을 준 계정, 권한을 받은 계정, 준 역할 이름을 찾아 보세요. 이 레코드만으로 권한을 받은 사람이 그 권한을 썼다고 말할 수 있나요?
2. 시험용 테넌트에서 사용자 하나에 위임 관리자 역할을 주고, 관리 콘솔 Admin log events 와 보고서 API 결과에 같은 일이 어떤 이름으로 나오는지 비교해 보세요. 화면의 Date 와 API 의 `id.time` 은 몇 시간 차이가 나나요?
3. 같은 사용자의 이름을 바꾼 뒤 옛 주소로 검색하면 무엇이 나오나요? `RENAME_USER` 기록에서 옛 주소와 새 주소를 어떻게 찾나요?
4. 서비스 설정 하나를 바꿨다가 되돌리고, `OLD_VALUE`·`NEW_VALUE` 가 두 기록에서 어떻게 뒤바뀌는지 확인해 보세요. 2026년 8월 전후 기록이라면 이벤트 이름도 같나요?
5. Cloud Logging 공유를 켠 테넌트라면 같은 이벤트를 Logs Explorer 에서 찾아 `timestamp` 와 `receiveTimestamp` 의 차이를 재 보세요.

## 참고 문헌

1. Google, "Method: activities.list", Admin SDK Reports API 참조 (Last updated 2026-09-03). https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
2. Google, "Admin Activity Report", Admin SDK Reports API 가이드 (Last updated 2026-09-03). https://developers.google.com/workspace/admin/reports/v1/guides/manage-audit-admin
3. Google, "Admin event names", Admin SDK Reports API 부록 (Last updated 2026-09-03). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-event-names
4. Google, "User Settings Admin events", Admin SDK Reports API 부록 (Last updated 2026-09-03). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-user-settings
5. Google, "Security Settings Admin events", Admin SDK Reports API 부록 (Last updated 2026-09-03). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-security-settings
6. Google, "Domain Settings Admin events", Admin SDK Reports API 부록 (Last updated 2026-09-03). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-domain-settings
7. Google, "Delegated Admin Settings Admin events", Admin SDK Reports API 부록 (Last updated 2026-09-03). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-delegated-admin-settings
8. Google, "Application Settings Admin events", Admin SDK Reports API 부록 (Last updated 2026-09-03). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-application-settings
9. Google, "Gmail Settings Admin events", Admin SDK Reports API 부록 (Last updated 2026-09-03). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-gmail-settings
10. Google, "Docs Settings Admin events", Admin SDK Reports API 부록 (Last updated 2026-09-03). https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-docs-settings
11. Google, "Data retention and lag times", Google Workspace 관리자 도움말 (Last updated 2026-09-25). https://support.google.com/a/answer/7061566
12. Google, "Admin log events", Google Workspace 관리자 도움말 (Last updated 2026-09-18). https://support.google.com/a/answer/4579579
13. Google, "Admin log event changes", Google Workspace 관리자 도움말 (Last updated 2026-09-18). https://knowledge.workspace.google.com/admin/reports/admin-log-event-changes
14. Google, "Set up service log exports to BigQuery", Google Workspace 관리자 도움말 (Last updated 2026-09-18). https://knowledge.workspace.google.com/admin/reports/set-up-service-log-exports-to-bigquery
15. Google, "Share data with Google Cloud services", Google Workspace 관리자 도움말 (Last updated 2026-09-18). https://support.google.com/a/answer/9320190
16. Google Cloud, "Audit logs for Google Workspace", Cloud Logging 문서 (Last updated 2026-09-25). https://cloud.google.com/logging/docs/audit/gsuite-audit-logging
17. Invictus Incident Response, ALFA — Automated Audit Log Forensic Analysis for Google Workspace (README.md, alfa/cmdline.py, alfa/main/collector.py, alfa/config/config.yml, alfa/config/internals.yml, alfa/utils/mappings.yml). https://github.com/invictus-ir/ALFA
18. SigmaHQ, Google Workspace 탐지 규칙(rules/cloud/gcp/gworkspace/admin, login). https://github.com/SigmaHQ/sigma/tree/master/rules/cloud/gcp/gworkspace
19. Google, "About reporting logs and BigQuery", Google Workspace 관리자 도움말 (Last updated 2026-09-18). https://knowledge.workspace.google.com/admin/reports/about-reporting-logs-and-bigquery
