---
title: "Notion·Atlassian 기록"
parent: "아티팩트 · 업무용 SaaS"
nav_order: 610
---

# Notion·Atlassian 기록 (Notion·Jira·Confluence)

Notion 감사 로그와 Atlassian 의 조직 감사 로그·Confluence 사이트 감사 로그·Jira 사이트 감사 로그가 누가 언제 어떤 페이지를 보고 내보내고 공유 설정을 바꿨는지 알려 주고, 어느 로그가 남는지는 요금제가 정합니다.

## 무엇을 기록하나 · 왜 생기나

문서 협업 도구에서 자료가 새어 나갔는지 볼 때는 페이지를 본 기록, 내보낸 기록, 외부 공유를 켠 기록이 핵심입니다. 두 서비스 모두 이런 동작을 감사 로그 (audit log) 에 남기지만, 무료·하위 요금제에서는 로그 자체가 없거나 관리 설정 변경만 남습니다.

**Notion** 은 Enterprise 요금제 조직에서 조직 소유자가 감사 로그를 봅니다. 누가 어떤 동작을 언제 했는지 기록하고, 가능한 경우 IP 주소도 함께 남깁니다[1]. 이벤트는 페이지, 데이터 소스, 팀스페이스, 워크스페이스, 계정, 양식, Workers, 조직 범주로 나뉩니다[1]. 관리자 토큰 (admin token) 으로 한 동작은 admin bot 을 행위자로 기록하고, Custom Agent 가 실행 중에 만들거나 고치거나 지운 페이지는 에이전트를 행위자로 한 일반 페이지 이벤트로 남으며 실행을 시작한 사람도 메타데이터에 들어갑니다[1].

**Atlassian** 은 세 층으로 기록합니다.

| 로그 | 담는 내용 | 보는 곳 |
|---|---|---|
| 조직 감사 로그 — 조직 관리자 로그 | 조직 수준 설정·사용자·보안 정책 변경 | Atlassian Administration 감사 로그, Events API[2][3][9] |
| 조직 감사 로그 — 앱 관리자 로그 | 앱별 관리자의 설정·권한 변경 | 같은 곳[2] |
| 조직 감사 로그 — 앱 사용자 로그 | 페이지 보기·만들기 같은 일상 동작, API 토큰·제3자 앱 활동 | 같은 곳[2][3] |
| Confluence 사이트 감사 로그 | 스페이스·권한·공개 링크·전역 설정 변경 | Confluence 관리 → Monitoring → Audit log[10] |
| Jira 사이트 감사 로그 | 사용자·스페이스에 영향을 주는 구성 변경, 작업 항목 삭제 | Settings → System → Audit Log, REST[11][12] |

Jira 사이트 감사 로그는 Jira 안의 모든 활동을 기록하려는 로그가 아니고 구성 변경을 기록하는 로그입니다[11]. 사용자가 작업 항목이나 페이지를 본 기록은 조직 감사 로그의 앱 사용자 로그에서 찾습니다.

## 위치와 버전별 차이

### Notion (2026년 9월 문서 기준)

| 항목 | 내용 |
|---|---|
| 요금제 | Enterprise 요금제, 조직 소유자만 열람[1] |
| 시작 시점 | Enterprise 로 올린 때부터 기록하고 그 전 이벤트는 없음[1] |
| 조직 감사 로그 | 워크스페이스 전환기 → Manage organization → Data & Compliance → Audit log. 조직 이벤트는 여기서 Organization 을 골랐을 때만 보임[1] |
| 워크스페이스 감사 로그 | 워크스페이스 이름 → Settings → Audit log[1] |
| 보관 | 최대 365일[1] |
| 내보내기 | CSV. 걸어 둔 필터에 맞는 이벤트만 들어가고, 365일 전부터 내보내는 시각 2시간 전까지 담김[1] |
| 실시간 전송 | Custom SIEM integration. 워크스페이스당 웹훅 하나, JSON, 실패 시 약 24시간 동안 최대 7회 재시도, syslog 없음, 페이지 본문 없음, 조직 이벤트 없음[1] |

화면 필터는 Organization, Date, Person or agent, Event, Teamspace, Related 입니다[1]. 워크스페이스에서 빠진 사용자도 Removed 표시와 함께 Person or agent 로 검색되고, 지운 사용자나 이름을 바꾼 사용자를 찾을 때는 내보낸 감사 로그를 쓰는 편이 낫습니다[1]. Teamspace 필터와 SIEM 이벤트의 팀스페이스 정보는 2026년 8월 9일 이후 이벤트부터 온전합니다[1]. Related 필터는 한 동작이 만든 이벤트 묶음을 보여 줍니다. 예를 들어 페이지를 옮기면 Page moved 와 권한 변경 이벤트가 함께 생깁니다[1].

### Atlassian 조직 감사 로그 (2026-08-12 게시 문서 기준)

Atlassian Guard(Standard 또는 Premium) 구독이나 Enterprise 요금제가 하나도 없으면 조직 수준 로그는 이벤트를 저장하지도 보여 주지도 않고, 나중에 요금제를 올려도 그 전 이벤트는 되살아나지 않습니다[3]. 조직 관리자 로그는 Guard Standard, Cloud Enterprise, Guard Premium 에서 남습니다[2]. Confluence 와 Jira 의 앱 로그(API 토큰·앱 활동 로그 포함)는 요금제에 따라 다음처럼 갈립니다[2].

| Confluence·Jira | Guard Standard | Guard Standard + Cloud Premium | Cloud Enterprise | Guard Premium |
|---|---|---|---|---|
| 앱 관리자 로그 | 없음 | 있음 | 있음 | 있음 |
| 앱 사용자 로그 | 없음 | 없음 | 있음 | 있음 |

| 항목 | 내용 |
|---|---|
| 화면 | 기본 최근 7일, 날짜를 바꾸면 최대 180일[3] |
| 보관 | 최대 180일, 그보다 오래된 활동은 지워지고 되살릴 수 없음[3] |
| 검색 | 사용자 이름·메일 주소·활동 이름·사이트 이름. 정확한 단어로만 찾음. 사이트 관리자에게는 검색창이 없음[3] |
| 내보내기 | 메일로 받는 CSV, 최근 180일 중 최대 10,000건, 필터를 걸면 걸린 것만. 메일 속 링크는 하루 뒤 만료[5] |
| API | Organizations REST API 의 Events API, 범위 `read:events:admin`[9] |
| 웹훅 | 조직당 최대 3개, JSON, 비동기 전송[7] |
| 이벤트 제외 | 이벤트 유형별로 저장을 끌 수 있음. Confluence·Jira 의 제3자 앱 API 요청 이벤트는 기본으로 꺼져 있음[8] |
| 앱 안 데이터 | Confluence 페이지 제목·Jira 작업 항목 식별자를 저장할지(Stored / Not Stored) 설정[6] |

Atlassian Government cloud 에서는 앱 안 데이터 활동이 조직 감사 로그에 없습니다[6]. 감사 로그에는 데이터 상주 (data residency) 가 적용되지 않습니다[6]. API 토큰 활동처럼 관리 계정 (managed account) 에 묶인 항목이 있어서, 조직 도메인을 등록하고 그 도메인의 계정을 조직 관리로 가져와 두지 않으면 일부 활동이 보이지 않습니다[3].

### Confluence·Jira 사이트 감사 로그

| 항목 | Confluence Cloud[10] | Jira Cloud[11][12] |
|---|---|---|
| 필요한 권한 | Confluence 관리자 | Administer Jira 전역 권한 |
| 없는 요금제 | Free | 모든 Jira 앱이 Free 일 때 |
| 보관 | 기본 1년, 1~12개월로 설정(한 달은 31일). 매주 같은 요일·시각에 설정보다 오래된 항목을 지움 | Actions → Audit Log Settings 에서 보관 기간(예: 6개월)을 정함 |
| 내보내기 | 전체 로그를 CSV 로 | CSV 최대 100,000건, 넘으면 최신 것만. 화면 필터와 상관없이 전체가 들어감 |
| 기록하지 않는 것 | 콘텐츠 편집(버전 기록에서 봄), 콘텐츠 위치 변경 | 구성 변경이 아닌 일상 활동 |

Jira 는 2024년 8월에 감사 로그를 손봤고, 그 전에 생긴 이벤트는 일부 보이지 않을 수 있습니다[11]. Jira 감사 로그 설정에서는 LDAP 같은 외부 사용자 디렉터리의 이벤트를 보일지도 정합니다[11].

## 구조

### Notion

감사 로그는 누가 어떤 동작을 언제 했는지와, 가능한 경우 IP 주소를 담습니다[1]. 페이지 이벤트에는 대상 페이지의 공개 범위 (audience) 가 붙고, 값은 Private, Shared internally, Shared externally(게스트나 통합 봇과 공유), Shared to web 가운데 하나이며 CSV 에 열로 들어갑니다[1]. CSV 열 이름과 SIEM JSON 페이로드의 필드 이름은 내보낸 파일의 머리글과 SIEM 이 받은 원본 JSON 에서 확인합니다.

조사에 자주 쓰는 이벤트는 다음과 같습니다(화면 이름 그대로)[1].

| 범주 | 이벤트 | 뜻 |
|---|---|---|
| 페이지 | Page viewed | 사용자가 페이지를 봤거나 통합·외부 AI 도구가 페이지 데이터를 읽음 |
| 페이지 | Page edited, Page created, Page moved | 사용자·통합·외부 AI 도구가 내용을 고치거나 만들거나 옮김 |
| 페이지 | Page exported | 사용자가 페이지를 내보냄 |
| 페이지 | File downloaded / File uploaded | 파일을 열었거나 내려받음 / 올림 |
| 페이지 | Page shared to web, Page permission update | 웹 공개를 켜거나 끔 / 구성원·게스트 권한이 바뀜 |
| 페이지 | Page moved to trash, Page permanently deleted | 휴지통 이동 / 완전 삭제(사용자가 하거나 30일 뒤, Enterprise 는 정한 기간 뒤 자동) |
| 페이지 | Private content transferred | 떠난 사용자의 비공개 페이지를 다른 사용자에게 넘김 |
| 워크스페이스 | Workspace content exported | 페이지 하나 또는 워크스페이스 전체를 내보냄 |
| 워크스페이스 | Export toggled, Public page sharing toggled | 내보내기 허용 / 웹 공개 허용을 켜거나 끔 |
| 워크스페이스 | Member invited, Member removed, Member role updated, Guest removed | 구성원 변화 |
| 워크스페이스 | Integration created, Integration secret reset, Integration permission updated | 통합 앱 추가·비밀 토큰 재발급·권한 변경 |
| 워크스페이스 | MCP server connected, MCP allowlist disabled, User information read | 외부 AI 도구 연결·허용 목록 해제·사용자 정보 읽기 |
| 워크스페이스 | SCIM token generated, Audit Log exported, Content search results exported | SCIM 토큰 발급 / 감사 로그 내보내기 / 콘텐츠 검색 결과 내보내기 |
| 계정 | Login, Logout | 언제 어디서 로그인·로그아웃했는지 |
| 계정 | Password changed, MFA TOTP toggled, Email changed, Granted support access | 계정 보안 변경 |
| 조직 | SAML settings updated, IP allowlist created, updated, or deleted, Admin role assigned | SSO·IP 제한·관리자 역할 변경 |
| 조직 | Legal hold content exported, Organization audit log exported | 법적 보존 자료 내보내기 / 조직 감사 로그 내보내기 |

### Atlassian 조직 감사 로그

화면 표의 열은 활동, 날짜·시각, 행위자(사용자 또는 Atlassian 시스템), 앱, 위치, IP 주소이고, 상세 패널에서 활동의 JSON 을 복사할 수 있습니다[3]. Events API 응답의 이벤트 한 건은 다음 모양입니다(문서 스키마를 따라 만든 예시이고, 값은 모두 지어낸 것입니다)[9].

```json
{
  "id": "(이벤트 ID)",
  "type": "events",
  "attributes": {
    "time": "2026-09-01T02:13:07.412Z",
    "processedAt": "2026-09-01T02:13:09.105Z",
    "action": "(활동 식별자)",
    "actor": {
      "id": "(계정 ID)",
      "name": "Example User",
      "email": "user@example.com",
      "auth": { "authType": "(인증 유형)", "tokenId": "(토큰 ID)", "tokenLabel": "(토큰 이름)" },
      "onBehalfOf": { "id": "(계정 ID)", "name": "", "email": "" },
      "app": { "id": "(앱 ID)", "type": "(앱 유형)", "attributes": {} }
    },
    "context": [ { "id": "(대상 ID)", "type": "(대상 유형)", "attributes": {} } ],
    "container": [ { "id": "(사이트·스페이스 ID)", "type": "(유형)", "attributes": {} } ],
    "location": { "ip": "203.0.113.10", "geo": "", "countryName": "", "regionName": "", "city": "" }
  },
  "message": { "content": "(사람이 읽는 설명)", "format": "(형식)" }
}
```

| 필드 | 뜻 |
|---|---|
| `attributes.time` | 활동이 일어난 시각 |
| `attributes.processedAt` | Atlassian 이 이벤트를 처리한 시각. `/events-stream` 응답에만 있음 |
| `attributes.action` | 활동 식별자. 화면 이름은 `/event-actions` 의 `displayName` 으로 맞춤 |
| `attributes.actor` | 행위자 계정. `auth` 에 `authType`·`tokenId`·`tokenLabel`, 대리 실행이면 `onBehalfOf`, 앱이 한 동작이면 `app` |
| `attributes.context` / `container` | 동작 대상 / 대상이 속한 사이트·스페이스 |
| `attributes.location` | `ip`, `geo`, `countryName`, `regionName`, `city` |

API 는 네 가지입니다[9]. `GET https://api.atlassian.com/admin/v1/orgs/{orgId}/events` 는 `q`, `from`, `to`, `action`, `actor`, `ip`, `product`, `location` 으로 세밀하게 거르고, `…/events-stream` 은 `from`, `to`, `sortOrder`, `cursor` 로 시간 순서대로 훑으며, `…/events/{eventId}` 는 한 건을, `…/event-actions` 는 활동 이름 목록을 줍니다. `/events` 는 2025년 5월 말부터 사용자당·경로당 분당 10회로 제한하므로 대량 수집에는 `/events-stream` 을 씁니다[9].

조사에 쓰는 활동 이름은 "Audit log activities database" 에서 찾습니다[4]. 예를 들면 다음과 같습니다.

| 갈래 | 활동 이름 |
|---|---|
| 로그인 | Logged in to account, Logged out of account |
| 보기 | Viewed Confluence page, Viewed Confluence blog, Viewed Jira issue |
| 편집·삭제 | Created Confluence page, Edited Confluence page, Deleted Jira issue |
| 내보내기 | Completed Confluence space export, Downloaded Confluence space export, Downloaded Confluence page export |
| 공유·권한 | Added Confluence space permission, Changed Confluence public link permissions |
| 토큰 | Viewed API token, Created API token, Exported API tokens |
| 관리 | Exported organization audit log, Changed authentication policy for domain |
| 제3자 앱 | Third-party app Confluence API request, Third-party app Jira API request(App actions 범주) |
| AI | Confluence Page Generated AI Content |

Completed Confluence space export 는 내보내기 파일이 만들어진 것이고 Downloaded Confluence space export 는 그 파일을 받아 간 것이라, 둘을 나눠 봅니다[4].

### Jira 사이트 감사 레코드

`/rest/api/3/auditing/record` 는 `offset`, `limit`, `filter`, `from`, `to` 를 받고, 권한은 Administer Jira, OAuth 2.0 범위는 클래식 `manage:jira-configuration` 이나 세분 범위 `read:audit-log:jira`·`read:user:jira` 입니다[12]. 레코드 한 건은 다음 모양입니다(문서 예시를 본떠 만든 예시)[12].

```json
{
  "id": 1042,
  "summary": "User added to group",
  "created": "2026-09-01T02:20:31.508+0000",
  "category": "group management",
  "eventSource": "",
  "remoteAddress": "198.51.100.23",
  "authorAccountId": "(계정 ID)",
  "objectItem": { "id": "(사용자 ID)", "name": "(사용자)", "typeName": "USER" },
  "associatedItems": [ { "id": "example-group", "name": "example-group", "typeName": "GROUP" } ],
  "changedValues": [ { "fieldName": "(바뀐 필드)", "changedFrom": "", "changedTo": "" } ]
}
```

`filter` 는 `summary`, `category`, `eventSource`, `objectItem.name`·`parentName`·`typeName`, `changedValues.changedFrom`·`changedTo`, `remoteAddress` 에서 찾습니다[12]. 작업 항목을 지우면 사이트에서 완전히 사라지고, 감사 로그에는 지운 사용자와 시각이 남으므로 "work item deleted" 나 작업 항목 키로 찾습니다[11].

## 증거로서 의미

**증명하는 것**

- 특정 계정이 특정 시각에 페이지를 본 기록: Notion Page viewed[1], Atlassian Viewed Confluence page·Viewed Jira issue(앱 사용자 로그가 남는 요금제일 때)[2][4].
- 내보내기와 내려받기: Notion Page exported·Workspace content exported·File downloaded[1], Atlassian Downloaded Confluence space export[4].
- 외부로 여는 설정 변경: Notion Page shared to web·Public page sharing toggled[1], Atlassian Changed Confluence public link permissions[4], Confluence 사이트 로그의 공개 링크 켜기·끄기[10].
- 권한·구성원·토큰·통합 변화와 감사 로그 자체를 내보낸 기록[1][4][11].
- 접속 IP 주소: Notion 은 가능한 경우에만[1], Atlassian 은 `location.ip`[9], Jira 사이트 레코드는 `remoteAddress`[12].

**증명하지 못하는 것**

- 페이지 본문과 무엇을 고쳤는지: Notion SIEM 페이로드에는 페이지 내용이 없고[1], Confluence 사이트 감사 로그는 편집을 기록하지 않습니다[10]. 편집 내용은 페이지 버전 기록에서 봅니다.
- Notion File downloaded 만으로는 파일을 열어 본 것인지 내려받은 것인지 가를 수 없습니다[1].
- 행위자가 사람인지: Page viewed 는 통합이나 외부 AI 도구가 읽어도 남고[1], Atlassian 은 행위자가 Atlassian 시스템일 수 있습니다[3]. 행위자 이름·유형을 먼저 봅니다.
- 기록이 없다는 사실만으로 행동이 없었다고 할 수 없습니다. 요금제가 낮거나, 요금제를 올리기 전이거나, 이벤트 제외를 켠 기간이면 로그가 원래 남지 않습니다[1][3][8].
- Custom Agent 가 실행 중에 한 일을 실행 단위로 모은 기록은 Notion 감사 로그에 없습니다[1].

## 시각 해석

Atlassian Events API 의 `time` 은 밀리초까지 적은 ISO 8601 UTC(`Z`) 값이고, `/events-stream` 에는 처리 시각 `processedAt` 이 따로 있습니다[9]. 두 값이 다르면 `time` 을 활동 시각으로, `processedAt` 을 수집 순서를 가늠하는 값으로 씁니다. Jira 사이트 레코드의 `created` 는 문서 예시에서 `2014-03-19T18:45:42.967+0000` 처럼 오프셋이 콜론 없이 붙어 있어[12], 콜론이 있는 ISO 8601 만 받는 도구는 이 값을 읽지 못할 수 있습니다. Notion 과 Confluence 사이트 로그의 CSV 시각이 UTC 인지 내보낸 사람의 현지 시각인지는, 시각을 아는 동작(예: 시험 계정 로그인)을 하나 남기고 CSV 에 찍힌 값과 비교해 확인합니다. 시간대를 맞추는 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 에 있습니다.

두 서비스 모두 동작 뒤 로그에 나타나기까지 시간이 걸립니다. Notion 감사 로그는 동작 뒤 화면에 나타나기까지 시간이 걸릴 수 있고, 실시간으로 받으려면 SIEM 연동을 씁니다[1]. Notion 내보내기는 내보내는 시각 2시간 전까지만 담습니다[1]. Atlassian 은 새 활동이 나타나기까지 몇 분 걸릴 수 있습니다[3]. 방금 일어난 일을 확인할 때는 조금 뒤에 다시 조회합니다.

보관 창은 로그마다 다릅니다.

| 로그 | 보관 | 문서 기준 |
|---|---|---|
| Notion 감사 로그 | 최대 365일[1] | 2026년 9월 문서 기준 |
| Atlassian 조직 감사 로그 | 최대 180일, 내보내기도 180일·10,000건[3][5] | 2026-02-26·2026-07-08 게시 |
| Confluence 사이트 감사 로그 | 기본 1년, 1~12개월 설정, 매주 정리[10] | 2026년 9월 문서 기준 |
| Jira 사이트 감사 로그 | 관리자가 정한 기간[11] | 2026년 9월 문서 기준 |

보관 기간이 지나기 전에 내보내 두는 절차는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 에 있습니다.

## 함정과 한계

- **요금제를 올린 시점 전은 비어 있습니다.** Notion·Atlassian 모두 올린 뒤부터 기록합니다[1][3]. 조사 대상 기간과 요금제 변경일을 먼저 맞춰 봅니다.
- **Notion SIEM 만 보면 조직 이벤트를 놓칩니다.** SAML 설정, IP 허용 목록, 관리자 역할 변경, 대부분의 관리자 API 활동은 조직 이벤트라 SIEM 으로 가지 않습니다[1]. 조직 감사 로그에서 Organization 을 골라 따로 봅니다.
- **Atlassian 이벤트 제외.** 제외한 유형은 그 기간 저장되지 않고 나중에 다시 켜도 채워지지 않습니다[8]. 제3자 앱 API 요청은 기본으로 제외되어 있어서[8], 통합 앱이 자료를 읽었는지 볼 때는 이 설정부터 확인합니다. 설정은 조직 감사 로그 Settings 의 Event Exclusion 탭에서 봅니다[8].
- **앱 안 데이터를 Not Stored 로 두면** 감사 로그에 Confluence 페이지 제목과 Jira 작업 항목 식별자가 없습니다[6]. 이때는 `context` 의 ID 를 앱 쪽 자료와 맞춰 대상을 찾습니다.
- **Last active 는 감사 로그와 다릅니다.** 관리 화면의 Last active 는 사용자가 앱 페이지를 2초 이상 본 마지막 시각이라 감사 로그 활동 시각과 어긋날 수 있습니다[6].
- **Confluence 사이트 로그 보관을 줄이면** 다음 주 정리 때 오래된 항목이 지워집니다[10]. 사이트 감사 로그 Settings 에서 지금 보관 기간이 몇 달인지 먼저 확인합니다[10].
- **Jira CSV 내보내기는 필터를 무시하고 최신 100,000건까지만** 담습니다[11]. 이벤트가 많은 사이트에서 오래된 구간이 필요하면 REST 로 `from`·`to` 를 나눠 받습니다[12].
- **Jira 사용자 관리 화면에서 한 변경은 Author 에 사용자 이름이 보이지 않는** 알려진 문제가 있습니다[11]. 사용자 생성·그룹 배정의 행위자는 조직 감사 로그와 함께 봅니다.
- **웹훅 전송은 빠질 수 있습니다.** Atlassian 웹훅은 최대 3번 재시도하고, 시간 순서를 보장하지 않으며, 같은 ID 로 두 번 올 수 있고, 공개된 서비스 수준 목표가 없습니다[7]. Notion SIEM 은 약 24시간 동안 7회까지 재시도합니다[1]. 받는 쪽이 오래 멈췄다면 SIEM 사본에 빈 구간이 있을 가능성이 있으므로, 서비스 화면이나 API 에서 같은 기간을 다시 받아 맞춰 봅니다. 중복은 이벤트 ID 로 걸러 냅니다.
- **자동 로그인 이전.** Windows 에서 브라우저가 저장한 자동 로그인 자격 증명을 다른 PC 로 옮기면, 논문이 시험한 브라우저 조건에서 Notion·Trello 웹에 자동 로그인할 수 있었습니다[14]. 로그인 기록의 기기나 IP 가 평소와 다르다고 해서 비밀번호가 새었다고 단정하지 않습니다. 세션과 토큰은 [토큰과 세션](../../01-foundations/identity/tokens-sessions.md) 에서 다룹니다.

## 직접 분석해 보기

이 로그들은 서비스 서버에만 있어서 디스크 헥스로 따라갈 대상이 없고, 내보낸 CSV 와 API 가 돌려준 JSON 을 원본으로 보관한 뒤 사본으로 분석합니다. JSON 을 읽는 요령은 [JSON 로그 읽기](../../01-foundations/logging/json-logs.md) 에 있습니다.

1. **Atlassian Events API.** `read:events:admin` 범위로 인증해 `/events-stream` 을 `from`·`to` 로 나눠 받고, 응답의 `links.next` 를 따라 끝까지 받습니다[9]. 받은 파일은 해시를 남겨 둡니다. 시간순 표로 펼칠 때는 `jq` 를 씁니다.

   ```sh
   jq -r '.data[] | [.attributes.time, .attributes.action, .attributes.actor.email, .attributes.location.ip] | @tsv' events.json
   ```

   `action` 값을 화면 이름으로 바꾸려면 `/event-actions` 응답의 `displayName` 과 맞춥니다[9].

2. **Jira 사이트 감사 레코드.** `/rest/api/3/auditing/record?from=…&to=…` 을 `offset` 을 늘려 가며 받습니다[12].

   ```sh
   jq -r '.records[] | [.created, .summary, .category, .authorAccountId, .remoteAddress] | @tsv' jira_audit.json
   ```

3. **Notion CSV.** 조직 감사 로그와 각 워크스페이스 감사 로그를 날짜 필터만 걸어 내보냅니다[1]. 머리글에서 시각·행위자·이벤트·IP·공개 범위 열을 찾고, 행위자가 사람인지 통합·에이전트·admin bot 인지 먼저 나눕니다.

4. **Confluence·Jira 사이트 CSV.** 각 관리 화면에서 전체를 내보냅니다[10][11]. 두 CSV 와 조직 감사 로그를 한 타임라인에 놓는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에 있습니다.

SigmaHQ 에는 자체 설치형 Bitbucket 감사 로그 규칙이 있습니다[13]. 이 규칙들은 `product: bitbucket`, `service: audit` 로그의 `auditType.category`·`auditType.action` 을 보고(예: `Data pipeline` / `Full data export triggered`, `Authentication` / `User login failed`), 규칙마다 Basic 또는 Advance 로그 수준이 필요합니다[13]. Cloud 조직 감사 로그와는 필드 구조가 다릅니다. 규칙을 로그에 거는 방법은 [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md) 에 있습니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [Okta 시스템 로그](okta.md) | SSO 로 들어왔다면 같은 시각의 인증 기록과 IP. SAML 흐름은 [페더레이션과 SSO](../../01-foundations/identity/federation-sso.md) |
| [Slack 감사 로그](slack.md) | 내보낸 파일이나 페이지 링크를 메시지로 넘겼는지 |
| [Dropbox·Box 기록](dropbox-box.md), [SharePoint·OneDrive](../m365/sharepoint-onedrive.md), [Drive 기록](../google-workspace/drive-audit.md) | 내보낸 파일이 다른 저장소로 올라갔는지 |
| [GitHub 감사 로그](github.md) | Jira·Confluence 와 같은 계정·토큰으로 저장소를 복제했는지 |
| [OAuth 앱과 동의](../../01-foundations/identity/oauth-consent.md) | Notion 통합·MCP 연결, Atlassian 제3자 앱이 받은 권한 |
| [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md) | `location.ip`·`remoteAddress` 를 해석할 때 |
| 페이지 버전 기록 | 감사 로그가 담지 않는 편집 내용 |

퇴사 직전 대량 내보내기는 [퇴사자가 자료를 가져갔나](../../04-scenarios/data-leak/departing-employee.md), 웹 공개·공개 링크는 [외부 공유 링크로 새어 나갔나](../../04-scenarios/data-leak/external-sharing.md), 감사 로그 설정 변경은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md) 에서 이어집니다. 서비스 회사에 기록을 요청하는 절차는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) 에 있습니다.

## 실습

아래 기록은 모두 만든 예시입니다(계정 user@example.com, IP 203.0.113.10·198.51.100.23).

| 시각(UTC) | 서비스 | 행위자 | 활동 |
|---|---|---|---|
| 2026-09-01 01:58 | Atlassian | user@example.com | Logged in to account |
| 2026-09-01 02:05 | Atlassian | user@example.com | Completed Confluence space export |
| 2026-09-01 02:13 | Atlassian | user@example.com | Downloaded Confluence space export |
| 2026-09-01 02:20 | Notion | user@example.com | Workspace content exported |
| 2026-09-01 02:31 | Notion | user@example.com | Page shared to web |

1. 02:05 와 02:13 기록은 각각 무엇을 말하고, 스페이스 내보내기 파일을 받아 간 시각은 언제라고 쓸 수 있습니까?
2. Atlassian 기록의 `location.ip` 와 Notion 기록의 IP 가 다르면 무엇을 더 봐야 합니까?
3. 02:31 이후 Page shared to web 이 다시 꺼졌는지 확인하려면 어떤 이벤트를 찾습니까? 그 페이지를 외부 사람이 실제로 열었는지는 이 로그로 말할 수 있습니까?
4. 같은 계정의 Notion SIEM 사본에 02:20 기록이 없고 화면에는 있다면 어떤 원인을 먼저 의심합니까?
5. 이 조직이 Guard Standard 만 쓴다면 위 Atlassian 기록 가운데 어느 것이 남지 않을 수 있는지 요금제 표와 활동 목록으로 따져 봅니다.

보고서에는 "2026-09-01 02:13 UTC 에 계정 user@example.com 으로 Confluence 스페이스 내보내기 파일을 내려받은 기록이 있다(IP 203.0.113.10)" 처럼 기록이 말하는 만큼만 씁니다(만든 예시). 문장 짜는 요령은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 참고 문헌

1. Notion, "Audit log", Notion Help Center. https://www.notion.com/help/audit-log
2. Atlassian, "What activities does the audit log include?" (2026-08-12 게시). https://support.atlassian.com/security-and-access-policies/docs/accessing-audit-log-activities/
3. Atlassian, "View audit log activities" (2026-02-26 게시). https://support.atlassian.com/security-and-access-policies/docs/view-audit-log-activities/
4. Atlassian, "Audit log activities database" (2026-05-26 게시). https://support.atlassian.com/security-and-access-policies/docs/audit-log-activities-database/
5. Atlassian, "Export audit log" (2026-07-08 게시). https://support.atlassian.com/security-and-access-policies/docs/export-audit-logs/
6. Atlassian, "In-app data settings" (2025-10-21 게시). https://support.atlassian.com/security-and-access-policies/docs/track-organization-activities-from-the-audit-log/
7. Atlassian, "Send audit log activities to another tool using webhooks" (2025-10-24 게시). https://support.atlassian.com/security-and-access-policies/docs/learn-more-about-audit-log-webhooks/
8. Atlassian, "Manage event exclusions from your audit log" (2025-11-06 게시). https://support.atlassian.com/security-and-access-policies/docs/manage-event-exclusions-from-your-audit-log/
9. Atlassian, "The Organizations REST API — Events". https://developer.atlassian.com/cloud/admin/organization/rest/api-group-events/
10. Atlassian, "View the audit log", Confluence Cloud. https://support.atlassian.com/confluence-cloud/docs/view-the-audit-log/
11. Atlassian, "Audit activities in Jira", Jira Cloud administration. https://support.atlassian.com/jira-cloud-administration/docs/audit-activities-in-jira-applications/
12. Atlassian, "The Jira Cloud platform REST API — Audit records". https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-audit-records/
13. SigmaHQ, Bitbucket audit rules. https://github.com/SigmaHQ/sigma/tree/master/rules/application/bitbucket/audit
14. Uk Hur, Soojin Kang, Giyoon Kim, Jongsung Kim, "A study on cloud data access through browser credential migration in Windows environment", Forensic Science International: Digital Investigation 45 (2023) 301568. https://doi.org/10.1016/j.fsidi.2023.301568
