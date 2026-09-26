---
title: "Okta 시스템 로그"
parent: "아티팩트 · 업무용 SaaS"
nav_order: 590
---

# Okta 시스템 로그 (Okta)

Okta 조직 (org) 에서 일어난 로그인·다단계 인증·앱 SSO·관리자 설정 변경·API 토큰 사용을 이벤트 하나당 JSON 레코드 하나로 남기는 기록이고, 서비스 안에는 90일치만 남습니다.

## 무엇을 기록하나 · 왜 생기나

Okta 는 여러 업무 앱의 로그인을 대신 처리하는 신원 공급자 (Identity Provider, IdP) 라서, 사용자가 Okta 에 로그인한 일과 Okta 를 거쳐 다른 앱으로 SSO 한 일이 모두 시스템 로그 (System Log) 에 남습니다[1][3]. 관리자가 사용자를 만들거나 비활성화하고, 관리자 역할을 주고, 정책 규칙·네트워크 영역·ID 공급자 설정을 바꾸고, API 토큰을 만들거나 폐기한 일도 같은 로그에 들어갑니다[3]. Okta ThreatInsight 가 악성으로 본 IP 의 요청, 사용자 위험도 변화, 속도 제한 (rate limit) 초과처럼 Okta 가 스스로 판단해 남기는 이벤트도 있습니다[3][5].

이벤트 종류는 `eventType` 이름으로 구별하고, 2026년 9월 카탈로그(release 2026.09.1)에는 1,289개가 있습니다[3]. 카탈로그의 태그 가운데 `oie-only` 는 Okta Identity Engine 조직에서만 생기는 이벤트, `changeDetails` 는 대상 객체에 바뀌기 전후 값이 붙을 수 있는 이벤트라는 뜻입니다[3].

## 위치와 버전별 차이

같은 로그를 세 가지 방법으로 봅니다.

| 보는 곳 | 모양 | 조건·특징 |
|---|---|---|
| 관리 콘솔 Reports > System Log | 개수 그래프, 이벤트 표, 지도 보기, "Download CSV file" 로 표 전체 내려받기 | 기본 필터는 최근 7일, 표시 시간대를 드롭다운으로 고름[7][8] |
| System Log API `GET /api/v1/logs` (listLogEvents) | `LogEvent` JSON 배열 | SSWS API 토큰 또는 OAuth 2.0 범위 `okta.logs.read`, Okta 는 OAuth 를 권장[1][2] |
| 로그 스트리밍 (Log Streaming) | Amazon EventBridge·Splunk Cloud 로 거의 실시간 전송 | 이벤트 거르기·재전송 (replay) 없음, 최소 한 번 전달[9] |

보관은 90일 슬라이딩 창이고(2026년 9월 문서 기준), 더 오래 필요하면 90일이 지나기 전에 내려받아 따로 보관해야 합니다[1][6]. 관리 콘솔에서 90일보다 긴 범위를 지정하면 오류가 나고[8], API 는 질의 자체는 성공하되 `published` 가 창 안에 있는 이벤트만 돌려줍니다[1]. 사고를 늦게 알았다면 수집부터 합니다([로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)). 서비스별 보관 기간 비교는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에 있습니다.

API 인자는 다음과 같습니다[2].

| 인자 | 뜻 | 기본값 |
|---|---|---|
| `since` | 아래쪽 시각 경계. 경계 요청이면 `published`, 폴링 요청이면 내부 저장 시각에 적용 | `until` 의 7일 전 |
| `until` | 위쪽 시각 경계 | 현재 시각 |
| `after` | 다음 쪽 커서. 응답 `Link` 헤더의 `rel="next"` 주소에 들어 있는 불투명한 값 | 없음 |
| `filter` | SCIM 필터 식. `[ ]` 를 뺀 연산자를 씀 | 없음 |
| `q` | 대소문자를 가리지 않는 키워드. 키워드 하나에 40자, 최대 10개 | 없음 |
| `limit` | 한 번에 돌려받을 개수, 0~1000 | 100 |
| `sortOrder` | `ASCENDING` 또는 `DESCENDING` | `ASCENDING` |

API 요청은 두 종류로 나뉘고 정렬 기준이 다릅니다[1]. `until` 을 비우고 `ASCENDING` 으로 보내면 폴링 요청 (polling request) 이고, 이벤트가 로그에 실제로 저장된 내부 시각 (persistence time) 순으로 나오므로 `published` 순서와 어긋날 수 있으며 `next` 링크가 끝없이 붙습니다. `since` 와 `until` 을 모두 주면 경계 요청 (bounded request) 이고, `published` 로 거르고 정렬하며 마지막 쪽에는 `next` 링크가 없습니다. 경계 요청에서도 늦게 들어온 이벤트는 드물게 빠질 수 있습니다[1]. 질의 하나의 제한 시간은 30초입니다[1].

## 구조

`LogEvent` 레코드의 최상위 필드는 `actor`, `authenticationContext`, `client`, `debugContext`, `displayMessage`, `eventType`, `legacyEventType`, `outcome`, `published`, `request`, `securityContext`, `severity`, `target`, `transaction`, `uuid`, `version` 입니다[2]. 조사에 자주 쓰는 하위 필드는 다음과 같습니다.

| 필드 | 내용 |
|---|---|
| `actor.id`·`type`·`alternateId`·`displayName` | 동작을 한 주체. 사용자면 `alternateId` 에 메일 주소 모양의 값이 들어감[2][4] |
| `target[]` | 동작을 받은 객체 배열. 항목마다 `id`, `type`(`User`, `AppInstance` 등), `alternateId`, `displayName`, `detailEntry`, 일부 이벤트는 `changeDetails.from`·`to`[2] |
| `client.ipAddress`·`userAgent`·`zone`·`device`·`geographicalContext` | HTTP 요청을 보낸 쪽. `zone` 은 클라이언트 위치가 해당하는 네트워크 영역 이름, `userAgent` 는 `rawUserAgent`·`os`·`browser`[2] |
| `client.id` | OAuth 요청이면 OAuth 클라이언트 ID, SSWS 토큰 요청이면 요청한 에이전트 ID[2] |
| `authenticationContext.externalSessionId` | 사용자 세션 ID 대신 쓰는 값[2] |
| `authenticationContext.credentialType`·`credentialProvider`·`authenticationProvider` | 쓴 자격 증명 종류(`PASSWORD`, `OTP`, `ASSERTION` 등)와 그것을 처리한 쪽[2] |
| `outcome.result`·`reason` | 결과(`SUCCESS`, `FAILURE`, `SKIPPED`, `ALLOW`, `DENY`, `CHALLENGE`, `UNKNOWN`, `RATE_LIMIT`, `DEFERRED`, `SCHEDULED`, `ABANDONED`, `UNANSWERED`)와 이유(예 `INVALID_CREDENTIALS`)[2] |
| `securityContext` | 요청 IP 의 `asNumber`, `asOrg`, `isp`, `domain`, 알려진 프록시에서 왔는지(`isProxy`), `risk`, `userBehaviors`[2] |
| `request.ipChain[]` | 프록시를 거친 경우 클라이언트 IP, 프록시1, 프록시2 순서의 IP 목록. 항목마다 `ip`, `geographicalContext`, `version`, `source`[2] |
| `transaction.id`·`type`·`detail` | 이벤트를 만든 요청. `type` 은 웹 요청 `WEB` 또는 비동기 작업 `JOB`, API 토큰으로 한 동작이면 `detail.requestApiTokenId` 에 토큰 ID[2] |
| `debugContext.debugData` | 이벤트마다 다른 자유 형식 값(예 `requestId`, `requestUri`, `url`, `threatSuspected`)[2][4] |
| `legacyEventType` | 예전 Events API 의 `objectType` 값(예 `core.user_auth.login_failed`)[2][10] |

HTTP 요청에서 나온 이벤트가 아니면 `client` 는 비어 있고, `request` 는 남지만 `ipChain` 이 빈 배열입니다[2]. `requestApiTokenId` 에 들어가는 토큰 ID 는 관리 콘솔 Security > API 에 보이는 값과 같습니다[2]. 로그의 `clientSecret` 속성 값은 해시로 가려져 있어 실제 인증에 쓴 값이 아닙니다[2][7].

아래는 로그인 실패 한 건의 모양으로 만든 예시이고, 사용자·IP·ID 는 모두 지어낸 값입니다.

```json
{
  "uuid": "3f0c2a8e-1b7d-4c55-9e21-6a0d4b7f9c10",
  "published": "2026-03-02T01:14:07.512Z",
  "eventType": "user.session.start",
  "legacyEventType": "core.user_auth.login_failed",
  "displayMessage": "User signs in to Okta",
  "version": "0",
  "actor": {"id": "00u1abcdEFGHijkl2345", "type": "User", "alternateId": "user@example.com", "displayName": "Example User"},
  "client": {
    "ipAddress": "203.0.113.25",
    "userAgent": {"rawUserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "os": "Windows 10", "browser": "CHROME"}
  },
  "authenticationContext": {"credentialType": "PASSWORD", "externalSessionId": null, "authenticationStep": 0},
  "outcome": {"result": "FAILURE", "reason": "INVALID_CREDENTIALS"},
  "securityContext": {"asNumber": 64500, "asOrg": "example", "isp": "exampleISP", "domain": "example.com", "isProxy": false},
  "request": {"ipChain": [{"ip": "203.0.113.25", "version": "V4", "source": null}]},
  "transaction": {"type": "WEB", "id": "Zx1aBcDeFgHiJkLmNoPqRsAAAB0", "detail": {}},
  "target": []
}
```

JSON 로그를 읽는 일반 방법은 [JSON 로그 읽기](../../01-foundations/logging/json-logs.md)에 있습니다.

## 조사에 쓰는 이벤트

| 갈래 | eventType | 뜻 |
|---|---|---|
| 로그인·세션 | `user.session.start` | Okta 로그인. 실패는 `outcome.result` 가 `FAILURE`[1][3] |
| | `user.session.end`, `user.session.clear` | 로그아웃, 세션 지움[3] |
| | `user.session.access_admin_app` | 관리 콘솔 접근[3] |
| | `user.session.context.change` | 세션을 쓰는 맥락이 처음과 크게 달라져 정책을 다시 평가해야 할 수 있음[3] |
| | `security.session.detect_client_roaming` | 세션이 다른 곳으로 옮겨 다님(roaming)을 감지[3] |
| | `user.session.impersonation.initiate`, `.grant` | 대리 세션 시작, 대리 권한 허용[3] |
| 인증 | `user.authentication.sso` | 앱으로 SSO. 실패해도 생김[3] |
| | `user.authentication.auth_via_mfa` | MFA 인증. Classic 조직은 2차 인증만, Identity Engine 조직은 1차·2차 모두[3] |
| | `user.authentication.auth_via_IDP`, `user.authentication.verify` | 외부 IdP 로 인증, 사용자 신원 확인[3] |
| | `policy.evaluate_sign_on` | 어느 로그인 정책 규칙을 평가했고 결과가 `ALLOW`·`CHALLENGE`·`DENY` 가운데 무엇인지[3] |
| MFA·계정 | `user.mfa.factor.deactivate`, `user.mfa.factor.reset_all` | 인증 수단 하나 또는 전부 해제[3] |
| | `user.mfa.attempt_bypass` | 인증 수단 우회 시도[3] |
| | `user.account.lock`, `user.account.reset_password` | 계정 자동 잠김, 비밀번호 재설정[3] |
| | `user.account.report_suspicious_activity_by_enduser` | 사용자가 수상한 활동을 신고[3] |
| 권한·설정 | `user.account.privilege.grant`, `group.privilege.grant`, `iam.resourceset.bindings.add` | 사용자·그룹 관리자 권한 부여, 관리자 역할 할당 생성[3] |
| | `system.api_token.create`, `.revoke` | 범위 없는 (unscoped) API 토큰 생성, API 토큰 폐기[3] |
| | `system.idp.lifecycle.create` | ID 공급자 추가[3] |
| | `policy.rule.update`, `zone.deactivate`, `zone.delete` | 정책 규칙 변경, 네트워크 영역 비활성·삭제[3] |
| | `user.lifecycle.create`, `application.user_membership.add` | 사용자 생성, 앱에 사용자 할당[3] |
| 위협 | `security.threat.detected` | ThreatInsight 가 악성으로 본 IP 의 요청. 이유는 `outcome.reason`[3] |
| | `user.risk.change` | 사용자 위험 수준 변화[3] |
| 로그 자체 | `system.log_stream.lifecycle.create`, `.deactivate` | 로그 스트림 생성, 비활성[3] |
| 속도 제한 | `system.org.rate_limit.warning`, `.violation`, `core.concurrency.org.limit.violation` | 조직 단위 속도·동시 요청 한도 근접·초과[5] |

`security.threat.detected` 의 `outcome.result` 는 ThreatInsight 설정에 따라 `ALLOW`(기록만 하고 요청은 통과), `DENY`(차단), `RATE_LIMIT`(속도 제한 계산에서 뺌) 가운데 하나입니다[3]. Identity Engine 조직의 `policy.evaluate_sign_on` 한 건에는 전역 세션 정책과 인증 정책 결과가 함께 들어가고, Classic 조직에서는 로그인 정책과 앱 로그인 정책이 따로 두 건 남습니다[3].

## 증거로서 의미

**증명하는 것**

- 그 Okta 계정으로 그 시각에 로그인 시도가 있었고, 결과(`outcome.result`)와 이유(`outcome.reason`)가 무엇이었는지[2][3].
- 요청이 온 IP, 프록시 여부, AS 번호·기관, 걸린 네트워크 영역[2].
- 어느 로그인 정책 규칙을 평가했고 추가 인증을 요구했는지(`policy.evaluate_sign_on`)[3].
- 어느 앱으로 SSO 를 시도했는지(`user.authentication.sso` 의 `target`)[3].
- 관리자가 어떤 사용자·그룹·역할·정책·영역·IdP 설정을 바꿨는지, `changeDetails` 가 있으면 바뀌기 전후 값[2][3].
- API 토큰으로 한 동작이면 어느 토큰으로 했는지(`transaction.detail.requestApiTokenId`)[2].

**증명하지 못하는 것**

- SSO 뒤 그 앱 안에서 무엇을 했는지. 앱 쪽 로그를 봐야 합니다([Slack](slack.md), [GitHub](github.md), [Microsoft 365 통합 감사 로그](../m365/unified-audit-log/index.md)).
- 실제 위치. `geographicalContext` 는 요청을 보낸 곳의 위치 값이지만 위치를 구하지 못하면 비고, `securityContext` 는 요청 IP 의 평판 정보입니다[2]. 둘 다 사람이 실제로 있던 곳을 증명하지 않습니다. 해석 방법은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md)에 있습니다.
- 계정을 쓴 사람이 누구인지. 기록은 계정과 세션만 말합니다.
- `debugData` 에 어떤 키가 없다는 사실의 의미. 키 이름과 값은 릴리스마다 바뀔 수 있어 약속된 형식이 아닙니다[2].
- 90일보다 오래된 일. 서비스에 남아 있지 않으므로 따로 받아 둔 사본이나 SIEM 을 찾아야 합니다[1][6].

## 시각 해석

`published` 는 이벤트가 공개된 시각이고[2], `2026-03-02T01:14:07.512Z` 처럼 밀리초까지 쓴 ISO 8601 UTC 문자열입니다[4]. 타임라인에는 이 값을 씁니다. 폴링 요청은 내부 저장 시각 순으로 이벤트를 주므로, 받은 순서대로 늘어놓으면 `published` 가 뒤섞일 수 있습니다[1]. 받은 뒤에는 반드시 `published` 로 다시 정렬합니다.

관리 콘솔은 고른 시간대로 시각을 보여 주므로[8], 화면에서 옮긴 시각이나 콘솔에서 내려받은 CSV 를 API JSON 과 섞을 때는 어느 시간대였는지 먼저 확인합니다. 로그 스트림은 순서가 뒤섞이거나 같은 이벤트가 두 번 올 수 있어, 순서는 `data.events.published` 로 맞추고 중복은 `eventId` 로 거릅니다[9]. 스트림은 최대 지연을 보장하지 않고 받는 쪽 서비스가 지연을 더할 수 있습니다[9]. 클라우드 로그 시각 일반은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 정리했습니다.

## 함정과 한계

- 전체를 옮길 때 `since`·`until` 로 기간을 직접 잘라 가며 받으면 이벤트가 빠지거나 겹칠 수 있습니다[1]. `since` 만 주고 `next` 링크를 끝까지 따라갑니다.
- `target` 배열 안에서 위치(첫 번째, 두 번째)로 값을 찾으면 안 됩니다. 대상 종류가 늘 같은 자리에 있지 않으므로 `type` 으로 찾습니다[2].
- 로그인 실패는 세션이 생기지 않아 `externalSessionId` 가 `null` 입니다[1]. 세션 ID 로만 묶으면 실패 이벤트가 빠집니다.
- Okta 시스템 행위자가 사용자 대신 한 동작은 `externalSessionId` 가 다를 수 있습니다[1]. 이런 이벤트는 `authenticationContext.rootSessionId` 로 한데 묶습니다[1]. 이 필드는 API 명세의 응답 예에는 나오지만 `LogAuthenticationContext` 속성 목록에는 없으므로[2], 검체에 실제로 있는지 먼저 봅니다.
- 로그 스트림 대상이 응답하지 않으면 Okta 는 전달을 두 번 시도해 실패하면 스트림을 끄고 `system.log_stream.lifecycle.deactivate` 를 남깁니다[9]. 관리자가 다시 켜기 전까지는 전송이 멈추고 재전송 기능도 없습니다[9]. SIEM 에 빈 구간이 있으면 이 이벤트부터 찾고, 빈 구간은 90일 안이라면 API 로 채웁니다. 누가 일부러 껐는지는 같은 이벤트의 `actor` 로 가립니다([로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)).
- `user.authentication.auth_via_mfa` 는 Classic 과 Identity Engine 에서 생기는 범위가 달라, 두 조직의 개수를 그대로 비교하면 안 됩니다[3].
- 관리 콘솔의 `contains` 연산자는 `debugContext.debugData.url`·`requestUri` 에 쓸 수 없습니다[8]. `changeDetails` 와 그 안의 `from`·`to` 도 질의 조건으로 쓸 수 없습니다[2].
- 조회 가이드의 오류 예시에는 "180 days" 라는 문구가 있지만, 같은 가이드의 보관 절과 다른 문서는 모두 90일입니다[1][6][8]. 보관 기간은 90일로 봅니다.

## 직접 분석해 보기

**원자료 한 줄 읽기.** API 응답을 한 줄에 이벤트 하나인 JSON 으로 저장해 두고 한 줄을 열어 다음 순서로 읽습니다.

1. `published` 를 적고 끝에 `Z` 가 있는지 봅니다.
2. `eventType` 과 `displayMessage` 로 무슨 일인지 정합니다. 옛 이름이 필요하면 `legacyEventType` 을 봅니다.
3. `actor.alternateId`·`id` 와 `target[]` 의 `type`·`alternateId` 를 적습니다.
4. `outcome.result`·`reason` 을 봅니다.
5. `client.ipAddress`, `request.ipChain`, `securityContext.isProxy`·`asOrg` 로 요청 출처를 적습니다.
6. `authenticationContext.externalSessionId`, `transaction.id`, `transaction.detail.requestApiTokenId` 를 적어 둡니다. 이 세 값이 다른 이벤트와 묶는 열쇠입니다.

**이벤트 묶기.** 같은 `externalSessionId` 는 같은 사용자 세션, 같은 `transaction.id` 는 한 요청으로 함께 생긴 이벤트입니다[1]. 한 세션 안에 요청 여러 개, 한 요청 안에 이벤트 여러 개가 들어갈 수 있으므로[1] 세션 → 요청 → 이벤트 순으로 묶어 봅니다. 특정 API 토큰이 한 일은 다음처럼 모읍니다(토큰 ID 는 만든 예시).

```text
GET /api/v1/logs?since=2026-02-01T00:00:00.000Z&until=2026-03-01T00:00:00.000Z&filter=transaction.detail.requestApiTokenId eq "00T1abcdEFGHijkl2345"
```

조회 가이드에 있는 필터 모양으로 로그인 실패만 받거나(`eventType eq "user.session.start" and outcome.result eq "FAILURE"`), 특정 IP 의 이벤트만 받을 수 있습니다(`client.ipAddress eq "..."`)[1]. `eventType sw "..."`·`co`·`ew` 처럼 앞·가운데·끝 글자로도 거릅니다[1]. 실제 요청에서는 필터 식을 URL 인코딩합니다.

**관리 콘솔.** Reports > System Log 에서 기간과 시간대를 정하고 검색창에 같은 식(예 `eventType eq "user.authentication.sso"`, `outcome.reason eq "Authentication failed: bad username or password"`)을 넣은 뒤 "Download CSV file" 로 표를 받습니다[7][8]. 이벤트를 펼쳐 Client 나 Request > IPChain 의 IP 에서 필터 아이콘을 누르면 그 IP 의 이벤트만 남습니다[8].

**탐지 규칙.** SigmaHQ 의 Okta 규칙 21개는 `product: okta`, `service: okta` 로그 원본에 LogEvent 필드 경로를 그대로 씁니다[10]. 조사에 바로 쓰는 것은 다음과 같습니다.

| 규칙 | 조건 |
|---|---|
| Okta User Session Start Via An Anonymising Proxy Service | `eventType: user.session.start` 이고 `securityContext.isProxy: 'true'` |
| Okta Admin Functions Access Through Proxy | `debugContext.debugData.requestUri` 에 `admin` 이 들어 있고 `securityContext.isProxy: 'true'` |
| Okta FastPass Phishing Detection | `eventType: user.authentication.auth_via_mfa`, `outcome.result: FAILURE`, `outcome.reason: 'FastPass declined phishing attempt'` |
| Okta New Admin Console Behaviours | `eventType: policy.evaluate_sign_on`, `target.displayName: 'Okta Admin Console'`, `debugContext.debugData.behaviors` 나 `debugContext.debugData.logOnlySecurityData` 에 `POSITIVE` |
| Potential Okta Password in AlternateID Field | `legacyEventType: core.user_auth.login_failed` 인데 `actor.alternateId` 가 메일 주소나 `0oa` 로 시작하는 값이 아님 |
| Okta User Account Locked Out | `displayMessage: Max sign in attempts exceeded` |
| MFA 해제, 관리자 역할 할당, API 토큰 생성·폐기, IdP 생성, 네트워크 영역 비활성·삭제, 정책·규칙 변경, 위협 감지, 사용자 신고, 사용자 생성 | `eventType` 하나 또는 몇 개(위 이벤트 표에 없는 `policy.lifecycle.update`·`.delete` 도 씀) |

Potential Okta Password in AlternateID Field 규칙은 사용자가 아이디 칸에 비밀번호를 넣어 그 비밀번호가 로그에 남은 경우를 찾습니다[10]. 이 규칙에 걸린 레코드의 `actor.alternateId` 에는 실제 비밀번호가 들어 있을 가능성이 있습니다. 이런 레코드는 보고서·공유 자료에서 가립니다. 규칙 적용 방법은 [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md)에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 보는 것 |
|---|---|
| SSO 대상 앱의 로그 ([Slack](slack.md), [GitHub](github.md), [Dropbox·Box](dropbox-box.md), [Zoom](zoom.md), [Notion·Atlassian](notion-atlassian.md)) | `user.authentication.sso` 직후 같은 사용자·IP 로 앱 안의 활동이 있는지 |
| [Entra ID 로그](../m365/entra-logs/index.md), [Google Workspace 로그인 기록](../google-workspace/login-audit.md) | Okta 와 페더레이션한 경우 그쪽에 남은 SAML 로그인과 시각·IP 가 맞는지 |
| 같은 Okta 로그의 관리자 이벤트 | 의심 로그인 뒤 MFA 해제·관리자 권한 부여·API 토큰 생성·정책 변경이 이어졌는지 |
| 외부 SIEM 에 스트리밍한 사본 | 90일이 지난 구간, 스트림이 꺼졌던 구간 |

페더레이션 구조는 [페더레이션과 SSO](../../01-foundations/identity/federation-sso.md), 세션과 토큰의 관계는 [토큰과 세션](../../01-foundations/identity/tokens-sessions.md)에 있습니다. 이상한 로그인과 권한 변화를 가려내는 절차는 [이상한 로그인 가려내기](../../03-techniques/analysis/suspicious-sign-ins.md)와 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md), 여러 로그를 한 줄로 늘어놓는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)을 봅니다.

## 실습

위의 만든 예시 레코드와 Okta 개발자용 시험 조직에서 받은 로그로 풀어 봅니다.

1. 예시 레코드는 성공인가 실패인가? 어느 두 필드를 보고 판단했고, `externalSessionId` 가 `null` 인 이유는 무엇인가?
2. 폴링 요청으로 받은 파일을 받은 순서 그대로 타임라인에 넣었다. 무엇이 틀어질 수 있고 어떻게 바로잡는가?
3. `user.session.start` 성공 뒤 몇 분 안에 `user.mfa.factor.reset_all` 과 `system.api_token.create` 가 있다. 세 이벤트가 같은 사람의 동작인지 어느 필드로 확인하는가?
4. SIEM 에서 사흘 동안 Okta 이벤트가 비어 있다. 어떤 이벤트를 먼저 찾고, 빈 구간은 어디서 채우는가?
5. 넉 달 전의 관리자 역할 할당을 확인해야 한다. Okta 에서 직접 받을 수 있는가? 받을 수 없다면 어디를 찾는가?

보고서 문장 예는 "2026-03-02 01:14:07 UTC 에 user@example.com 계정으로 IP 203.0.113.25 에서 비밀번호 로그인에 실패한 기록(`outcome.reason` INVALID_CREDENTIALS)이 있다" 처럼 기록이 말하는 만큼만 씁니다(만든 예시). 계정 탈취 흐름은 [토큰을 훔쳐 로그인했나](../../04-scenarios/account-compromise/token-theft.md)와 [MFA 피로 공격을 당했나](../../04-scenarios/account-compromise/mfa-fatigue.md)에서 이어집니다.

## 참고 문헌

1. Okta, "System Log query", Okta Developer 문서(저장소 마지막 커밋 2025-12-16). https://developer.okta.com/docs/reference/system-log-query/ (원문 https://github.com/okta/okta-developer-docs/blob/master/packages/@okta/vuepress-site/docs/reference/system-log-query/index.md)
2. Okta, Okta Management API OpenAPI 명세 `management-minimal.yaml`(info.version 2026.08.4) — `listLogEvents`, `LogEvent` 스키마. https://github.com/okta/okta-management-openapi-spec/blob/master/dist/current/management-minimal.yaml
3. Okta, "Event Types" 카탈로그(release 2026.09.1)와 태그 설명. https://github.com/okta/okta-developer-docs/blob/master/packages/@okta/vuepress-site/data/event-types.json , https://github.com/okta/okta-developer-docs/blob/master/packages/@okta/vuepress-site/docs/reference/api/event-types/index.md
4. Okta, 이벤트 훅 구현 가이드의 이벤트 객체 예. https://github.com/okta/okta-developer-docs/blob/master/packages/@okta/vuepress-site/docs/guides/event-hook-implementation/main/nodejs/event-object.md
5. Okta, "System Log events for rate limits". https://github.com/okta/okta-developer-docs/blob/master/packages/@okta/vuepress-site/docs/reference/rl-system-log-events/index.md
6. Okta, "Monitor Okta". https://github.com/okta/okta-developer-docs/blob/master/packages/@okta/vuepress-site/docs/concepts/monitor/index.md
7. Okta 도움말, "System Log". https://help.okta.com/en-us/content/topics/reports/reports_syslog.htm
8. Okta 도움말, "System Log filters and search". https://help.okta.com/en-us/content/topics/reports/syslog-filters.htm
9. Okta 도움말, "Log streaming". https://help.okta.com/oie/en-us/content/topics/reports/log-streaming/about-log-streams.htm
10. SigmaHQ, Okta 탐지 규칙(`rules/identity/okta/`). https://github.com/SigmaHQ/sigma/tree/master/rules/identity/okta
