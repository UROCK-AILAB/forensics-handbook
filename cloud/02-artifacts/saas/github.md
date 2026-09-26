---
title: "GitHub 감사 로그"
parent: "아티팩트 · 업무용 SaaS"
nav_order: 580
---

# GitHub 감사 로그 (GitHub)

GitHub 감사 로그 (audit log) 는 조직과 엔터프라이즈 안에서 누가 저장소를 만들고 지우고 공개로 바꾸고 복제했는지, 어떤 키와 토큰을 더하고 승인했는지를 `범주.작업` 이름으로 남기는 기록이고, 소스 코드 유출과 권한 변경을 조사할 때 먼저 봅니다[1][4].

## 무엇을 기록하나 · 왜 생기나

조직이나 엔터프라이즈의 자원에 영향을 주는 동작을 하면 감사 로그에 이벤트가 한 건 생깁니다[1][4]. 이벤트 이름은 `repo.create` 처럼 범주와 작업을 점으로 이은 모양이고, 사람뿐 아니라 앱·통합·Copilot 같은 에이전트도 행위자가 됩니다[4][5][9]. 기록은 넷으로 나뉩니다.

| 기록 | 담는 것 | 보는 사람 |
|---|---|---|
| 엔터프라이즈 감사 로그 | 엔터프라이즈 계정과 그 안 조직에 관한 이벤트, Git 이벤트(`git.clone` 등) | 엔터프라이즈 소유자[1][12] |
| 조직 감사 로그 | 한 조직에 관한 이벤트 | 조직 소유자[4] |
| 개인 보안 로그 (security log) | 한 개인 계정이 한 동작과 그 계정이 관련된 동작 | 계정 본인[14] |
| GitHub Enterprise Server 인스턴스 감사 로그 | 엔터프라이즈 감사 로그보다 넓은 범위, 시스템 관리 이벤트 포함 | 사이트 관리자[3] |

엔터프라이즈가 Enterprise Managed Users 를 쓰지 않으면 엔터프라이즈 감사 로그에는 엔터프라이즈 계정과 조직 관련 이벤트만 들어가고, 쓰면 사용자 이벤트(보안 로그 이벤트)까지 들어갑니다[12]. Enterprise Managed Users 가 아닌 엔터프라이즈에서는 구성원이 GitHub.com 에 로그인한 일, 개인 계정이 소유한 저장소·gist·프로젝트를 다룬 일, 조직의 공개 저장소를 다룬 일이 엔터프라이즈 감사 로그에 이벤트로도 IP 로도 나오지 않습니다[9].

조사에서 자주 보는 이벤트와 필드는 아래와 같습니다[12][13].

| 묶음 | 이벤트 | 주요 필드 | 조사에서 뜻하는 것 |
|---|---|---|---|
| 복제·내려받기 | `git.clone`, `git.fetch`, `git.push` | `repository_public`, `transport_protocol`, `transport_protocol_name`, `external_id` | 저장소를 복제·가져오기·푸시함. 웹 화면에는 나오지 않고 REST API·스트리밍·JSON/CSV 내보내기로만 봄 |
| 복제·내려받기 | `repo.download_zip` | `visibility`, `public_repo` | 소스 코드 압축 파일을 ZIP 으로 내려받음 |
| API 호출 | `api.request` | `request_method`, `route`, `url_path`, `query_string`, `status_code` | 엔터프라이즈 설정에서 API Request Events 를 켠 경우에만 생기고 스트리밍으로만 받음[11][12] |
| 저장소 | `repo.create`, `repo.destroy` | `visibility`, `request_method` | 저장소를 만들거나 지움 |
| 저장소 | `repo.access` | `previous_visibility`, `visibility` | 저장소 공개 범위를 바꿈 |
| 저장소 | `repo.transfer`, `repo.transfer_outgoing` | `old_user`, `owner`, `new_nwo` | 저장소를 다른 소유자·네트워크로 옮김 |
| 저장소 | `repo.update_member` | `old_permission`, `old_repo_permission`, `new_repo_permission` | 한 사용자의 저장소 권한을 바꿈 |
| 구성원 | `org.add_member`, `org.invite_member`, `org.remove_member`, `org.update_member`, `org.remove_outside_collaborator` | `permission`, `old_permission`, `invitee_email` | 조직에 들이고 내보내고 역할을 바꿈. 2단계 인증 요구 때문에 제거된 경우도 `org.remove_member`·`org.remove_outside_collaborator` 로 남음 |
| 자격 증명 | `public_key.create` | `fingerprint`, `key`, `read_only`, `title` | 계정에 SSH 키, 저장소에 배포 키를 더함 |
| 자격 증명 | `personal_access_token.request_created`, `personal_access_token.access_granted` | `repositories`, `repository_selection`, `user_programmatic_access_name` | 세분화된 개인 액세스 토큰이 조직 자원 접근을 요청하고 승인받음 |
| 자격 증명 | `org_credential_authorization.grant` | `fingerprint`, `managed_hashed_token`, `managed_token_scopes` | 구성원이 SAML·OIDC SSO 에 쓸 자격 증명을 승인함 |
| 앱·연동 | `integration_installation.create`, `org.oauth_app_access_approved`, `hook.create` | `integration`, `oauth_application_name`, `hook_id`, `events` | GitHub App 설치, OAuth 앱 접근 승인, 웹훅 추가 |
| 보안 설정 | `org.disable_two_factor_requirement`, `org.disable_saml`, `business.disable_saml`, `org.disable_oauth_app_restrictions` | `issuer`, `sso_url` | 2단계 인증 요구·SSO·앱 접근 제한을 끔 |
| 보안 설정 | `repository_secret_scanning_push_protection.disable`, `protected_branch.policy_override` | `overridden_codes`, `reasons`, `before`, `after` | 비밀 푸시 차단을 끄거나 브랜치 보호 요건을 건너뜀 |
| 비밀 | `org.create_actions_secret`, `repo.create_actions_secret` | `key`, `visibility` | Actions 비밀을 새로 만듦 |
| 로그 자체 | `org.audit_log_export`, `business.audit_log_export` | `query_phrase` | 감사 로그를 내보냄. 질의가 있었으면 질의와 맞은 건수를 남김 |
| 로그 자체 | `audit_log_streaming.create`, `audit_log_streaming.update`, `audit_log_streaming.destroy`, `audit_log_streaming.check` | `audit_log_stream_sink`, `audit_log_stream_enabled`, `old_s3_bucket`, `new_s3_bucket` | 스트리밍 대상을 더하고 바꾸고(일시정지·켜기·끄기 포함) 지우고 직접 점검함 |

## 위치와 버전별 차이

### 어디서 보나

조직 감사 로그는 조직 Settings 의 사이드바 Archive 에서 Logs → Audit log 로 들어가고, 엔터프라이즈 감사 로그는 엔터프라이즈 Settings → Audit log 에 있습니다[4][6]. 개인 보안 로그는 개인 Settings → Security log 에 있고 JSON·CSV 로 내보낼 수 있습니다[14]. GitHub Enterprise Server 에서는 사이트 관리자가 Site admin 화면에서 인스턴스 감사 로그를 보고, 감사 로그와 시스템 로그를 외부 모니터링 시스템으로 보내는 로그 전달 (log forwarding) 을 설정할 수 있습니다[3].

### 보관 기간(2026년 9월 문서 기준)

| 기록 | 보관 |
|---|---|
| 엔터프라이즈 감사 로그(GitHub Enterprise Cloud) | 최근 180일, Git 이벤트는 7일[1][2] |
| 조직 감사 로그 | 최근 180일[4] |
| 개인 보안 로그 | 최근 90일[14] |
| GitHub Enterprise Server 감사 로그 | 엔터프라이즈 소유자가 따로 정하지 않으면 무기한[2][3] |
| 스트리밍으로 받은 사본 | 받는 저장소의 보관 설정을 따름[11] |

화면과 API 는 기본으로 최근 3개월 이벤트만 보여 주고, 더 오래된 이벤트는 `created` 조건으로 날짜 범위를 줘야 나옵니다[1][2]. 화면에 3개월만 보인다고 보관 기간이 3개월인 것은 아닙니다. 기간과 요금제 차이의 일반 원리는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에 있습니다.

### IP 주소 공개 설정

GitHub 는 기본으로 감사 로그에 행위자의 IP 주소를 보여 주지 않습니다[9][10]. 엔터프라이즈 소유자가 Settings → Audit log 의 Settings 탭에서 "Disclose actor IP addresses in audit logs" 아래 Enable source IP disclosure 를 켜면, 새 이벤트뿐 아니라 이미 있던 이벤트에도 IP 가 나오고 그 엔터프라이즈의 모든 조직 감사 로그에도 나옵니다[9]. 조직 하나만 켜는 설정도 조직 감사 로그 설정에 있고, 2026년 9월 문서 기준 공개 미리보기 기능입니다[10].

켜 두어도 IP 가 없는 이벤트가 있습니다. 조직 감사 로그는 행위자가 조직 구성원·소유자이고 대상이 조직 소유의 비공개·내부 저장소이거나 저장소가 아닌 조직 자원일 때만 IP 를 보여 줍니다[10]. 저장소 맥락이 없는 `api.request`(GraphQL 요청, 사용자나 조직만 가리키는 끝점 요청), 기록된 행위자와 실제 수행자가 다른 일부 이벤트, 봇·자동 시스템이 한 동작에는 IP 가 없습니다[9]. 설정을 켜 두었는지는 같은 설정 화면에서 확인합니다.

## 구조

### 레코드 필드

엔터프라이즈 이벤트 목록의 거의 모든 이벤트에 공통 필드 `@timestamp`, `_document_id`, `action`, `actor`, `actor_id`, `business`, `business_id`, `hashed_token`, `org`, `org_id`, `programmatic_access_type`, `repo`, `repo_id`, `repository`, `repository_id`, `request_access_security_header`, `request_id`, `token_id`, `token_scopes`, `user`, `user_id`, `user_agent` 가 있고, 이벤트마다 `actor_is_agent`, `actor_is_bot`, `created_at`, `oauth_application_id`, `operation_type`, `user_programmatic_access_name` 같은 필드가 더 붙습니다[12].

`actor` 는 동작을 시작한 계정이고 `user` 는 동작의 영향을 받은 사용자입니다[5]. 에이전트가 한 동작이면 `user` 에 에이전트가 대신 일한 사용자 이름이 들어갑니다[5]. `operation_type` 은 create, access, modify, remove, authentication, transfer, restore 가운데 하나입니다[5].

웹 화면 밖(API, Git, 앱)에서 한 동작이면 인증 방법이 함께 남습니다[8]. `hashed_token` 은 인증에 쓴 토큰의 SHA-256 해시를 base64 로 적은 값이고, `programmatic_access_type` 은 인증 종류, `token_scopes` 는 토큰 범위입니다[8]. 이 정보가 남는 인증은 개인 액세스 토큰, OAuth 토큰, GitHub App(설치로 인증하거나 사용자를 대신해 인증), 배포 키, SSH 키이고, SSH 키·배포 키 표시와 Git 이벤트의 토큰 정보 표시는 2026년 9월 문서 기준 공개 미리보기입니다[8].

아래는 REST 응답 예의 모양을 따라 만든 예시입니다. 값은 모두 지어낸 것입니다.

```json
{
  "@timestamp": 1788229207412,
  "action": "repo.access",
  "actor": "example-admin",
  "created_at": 1788229207412,
  "_document_id": "q3Rk9vXbTm2Lp8YwZc1aHg",
  "org": "example-org",
  "repo": "example-org/example-repo",
  "previous_visibility": "private",
  "visibility": "public"
}
```

`@timestamp` 와 `created_at` 은 UTC 기준 에포크 밀리초이고, 위 값 1788229207412 는 2026-09-01T02:20:07.412Z 입니다[6][7].

### 내보내기 파일

화면에서 내보낸 JSON·CSV 에는 `action`, `actor`, `user`, `actor_location.country_code`, `org`, `repo`, `created_at`, 그리고 이벤트별 값이 `data.email`, `data.hook_id`, `data.events`, `data.events_were`, `data.target_login`, `data.old_user`, `data.team` 처럼 `data.` 아래에 들어갑니다[4][6]. 내보내기에는 압축 100 MB 또는 처리 10분의 한도가 있어서, 큰 범위는 조건으로 나눠 받거나 스트리밍을 씁니다[6].

Git 이벤트는 따로 날짜 범위를 골라 Export Git Events 로 받고, gzip 으로 압축한 줄 단위 JSON 파일(예 `export-avocado-corp-1642896556.json.gz`)로 나옵니다[6]. 웹 화면·REST·GraphQL 로 시작한 Git 동작은 Git 이벤트 내보내기에 들어가지 않습니다[6]. 예를 들어 웹에서 풀 요청을 병합하면 기준 브랜치에 푸시가 일어나지만 그 푸시는 내보내기에 없습니다[6].

### 스트리밍 파일

엔터프라이즈 소유자는 감사 이벤트와 Git 이벤트를 Amazon S3, Azure Blob Storage, Azure Event Hubs, Datadog, Google Cloud Storage, Splunk 로 계속 보낼 수 있고, Microsoft Purview 로는 Copilot 에이전트 세션 이벤트만 보냅니다[11]. 파일로 쌓는 대상에는 `YYYY/MM/DD/HH/MM/<uuid>.json.log.gz` 이름의 압축 JSON 파일이 생깁니다[11]. 스트림은 켠 시점부터의 이벤트만 보내고, 한 번 이상 전달 (at-least-once) 방식이라 같은 이벤트가 두 번 들어올 수 있습니다[11].

## 증거로서 의미

### 증명하는 것

- 특정 GitHub 계정이 특정 시각에 특정 저장소를 복제·ZIP 내려받기·공개 전환·삭제·이전했다는 기록[12].
- 계정에 SSH 키를 더하거나 저장소에 배포 키를 더한 일, 세분화된 개인 액세스 토큰이 조직 자원 접근을 승인받은 일, GitHub App 을 설치하거나 OAuth 앱을 승인한 일[12][13].
- 웹 화면 밖에서 한 동작이면 어떤 토큰으로 했는지. 원문 토큰이나 자격 증명 목록의 `hashed_token` 이 있으면 한 토큰이 한 일을 모아 볼 수 있습니다[8].
- IP 공개가 켜져 있으면 행위자 IP, 내보내기에서는 `actor_location.country_code` 로 나라[4][9].
- 2단계 인증 요구·SSO·비밀 푸시 차단을 끄거나 감사 로그 스트림을 바꾼 일과 그 앞뒤 값[12].

### 증명하지 못하는 것

- 복제하거나 내려받은 코드가 그 뒤 어디로 갔는지는 남지 않습니다.
- Enterprise Managed Users 가 아니면 개인 계정 소유 자원과 조직의 공개 저장소를 다룬 일, GitHub.com 로그인이 엔터프라이즈 감사 로그에 없습니다[9]. 공개 저장소를 누가 복제했는지는 이 로그로 알 수 없습니다.
- IP 공개가 꺼져 있거나 IP 를 보여 주지 않는 이벤트면 IP 로 사람을 좁힐 수 없습니다[9][10].
- GitHub Enterprise Cloud 의 Git 이벤트는 7일만 남아서, 일주일이 지나 시작한 조사에서는 스트리밍 사본이 없으면 `git.clone` 을 찾을 수 없습니다[1][2].
- `api.request` 는 API Request Events 를 켜고 스트리밍한 경우에만 있고, 켜도 보안과 관련된 끝점 요청만 들어갑니다[11][12].
- 계정 이름은 계정을 가리킬 뿐 키보드 앞의 사람을 가리키지 않습니다. 토큰이 새었으면 다른 사람이 같은 `actor` 로 기록됩니다.

보고서에는 "직원이 코드를 가져갔다" 가 아니라 "2026-09-01 02:20 UTC 에 계정 example-user 로 저장소 example-org/example-repo 에 대해 `git.clone` 이 기록되어 있고, `hashed_token` 은 자격 증명 목록의 토큰 하나와 같다" 처럼 기록이 말하는 만큼만 씁니다(만든 예시).

## 시각 해석

`@timestamp`, `created_at` 은 이벤트가 일어난 시각을 UTC 에포크 밀리초로 적은 값입니다[6][7]. 화면 검색의 `created` 조건은 `2026-09-01` 같은 ISO 8601 날짜를 받고, 날짜 뒤에 `THH:MM:SS+00:00` 모양으로 시각과 UTC 오프셋을 붙일 수 있고, `>=`, `<=`, `..` 범위를 쓸 수 있습니다[5]. 보고서에는 원본 밀리초 값과 UTC 로 바꾼 값을 함께 적습니다. 시간대 일반 원리는 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 있습니다.

스트리밍 사본의 파일 경로에도 연·월·일·시·분이 들어가지만, 이 시각은 파일을 쓴 때일 수 있으므로 이벤트 시각은 레코드 안의 값으로 판단합니다. 스트림을 일시정지하면 7일 동안은 쌓아 두었다가 이어서 보내고, 7일을 넘기면 재개 시점에서 일주일 전부터, 3주 이상이면 쌓아 둔 것 없이 재개 시점부터 보냅니다[11]. 오래 멈췄던 스트림에는 빈 구간이 생깁니다.

## 함정과 한계

**화면과 토큰 검색에는 Git 이벤트가 없습니다.** `git.clone`·`git.fetch`·`git.push` 는 웹 화면에 나오지 않습니다[5][12]. REST 는 `include` 인자의 기본값이 `web` 이라서 `include=git` 이나 `include=all` 을 줘야 Git 이벤트가 옵니다[7][15]. `hashed_token` 으로 검색하는 방법은 화면과 REST 모두 Git 이벤트를 돌려주지 않으므로, 토큰으로 Git 동작을 찾으려면 Git 이벤트 내보내기를 받아 그 안의 인증 필드를 봅니다[8].

**본문 검색이 안 됩니다.** 감사 로그는 글자 검색이 안 되고 `action`, `actor`, `created`, `ip`, `operation`, `repository`, `user`, `country` 같은 조건으로만 거릅니다[4][5].

**스트림에는 중복이 있을 수 있습니다.** `_document_id` 가 같은 레코드는 같은 이벤트일 가능성이 있으니, 건수를 셀 때는 이 값으로 겹침을 먼저 봅니다[11][15].

**스트리밍은 과거를 채우지 않습니다.** 사건이 난 뒤 스트리밍을 켜면 그 전 이벤트는 스트림에 없고, 보관 기간 안이라면 API·내보내기로 따로 받아야 합니다[11]. 24시간마다 상태 점검이 돌고, 설정이 잘못된 스트림은 6일 안에 고치지 않으면 이벤트가 버려집니다[11].

**로그를 건드린 흔적.** 스트림을 멈추거나 대상 버킷을 바꾸면 `audit_log_streaming.update` 에 `audit_log_stream_enabled` 와 `old_s3_bucket`·`new_s3_bucket` 같은 앞뒤 값이 남고, 지우면 `audit_log_streaming.destroy` 가 남습니다[12]. 감사 로그를 내보낸 일은 `org.audit_log_export`·`business.audit_log_export` 로 남습니다[12]. 조사 흐름은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)에 있습니다.

## 직접 분석해 보기

**원본 JSON 으로 한 번.** Git 이벤트 내보내기 파일은 줄 단위 JSON 이므로, `gunzip -c` 로 풀어 바로 `jq` 에 넘기면 한 줄에 한 이벤트씩 UTC 시각·작업·계정·저장소·토큰 해시를 뽑을 수 있습니다. 원본 파일의 해시를 먼저 남기고 사본에서 작업합니다.

```bash
gunzip -c export-example-org-1788229207.json.gz \
  | jq -r '[(."@timestamp"/1000 | todate), .action, .actor, .repo, .hashed_token] | @tsv' \
  | sort
```

특정 토큰이 한 일을 찾을 때 원문 토큰이 있으면 먼저 해시를 만들고, 원문이 없으면 엔터프라이즈 자격 증명 목록 (credential inventory) 을 내보낸 CSV 의 `hashed_token` 값을 씁니다[8].

```bash
echo -n TOKEN | openssl dgst -sha256 -binary | base64
```

화면 검색에는 `hashed_token:"값"` 처럼 따옴표로 감싸 넣고, REST 에서는 값을 URI 인코딩해서 넣습니다[8]. 위 명령으로 지어낸 문자열을 해시하면 `eZALYM4obf1VzKsNlLARMmDAOzkWunCZPkjcfecmkwo=` 처럼 44자 base64 값이 나옵니다(만든 예시).

**공식 API 로 한 번.** 조직은 `GET /orgs/{org}/audit-log`, 엔터프라이즈는 `GET /enterprises/{enterprise}/audit-log` 로 받습니다[7][15]. 순서는 다음과 같습니다.

1. 조직 끝점은 조직 소유자만 부를 수 있고, 클래식 개인 액세스 토큰·OAuth 토큰은 `read:audit_log` 범위가 있어야 합니다[15].
2. `phrase` 에 `created:2026-08-01..2026-09-01` 처럼 기간을 넣고, Git 이벤트까지 받으려면 `include=all` 을 붙이고, `per_page=100` 으로 한 번에 최대 100건씩 받습니다[7][15].
3. 응답의 `Link` 헤더에 있는 `after` 커서로 다음 쪽을 이어 받습니다[7].
4. 끝점마다 사용자·IP 조합당 시간당 1,750회 제한이 있으므로, 403·429 응답이 오면 잠시 기다렸다가 다시 부릅니다[7].

```bash
curl -H "Accept: application/vnd.github+json" \
     -H "Authorization: Bearer TOKEN" \
     "https://api.github.com/orgs/example-org/audit-log?phrase=created:2026-08-01..2026-09-01&include=all&per_page=100"
```

**탐지 규칙으로 훑기.** SigmaHQ 에는 `product: github`, `service: audit` 로그용 규칙 15개가 있고, 모두 `action` 값 하나로 거르며, 그 가운데 13개는 감사 로그 스트리밍으로 받은 로그를 요건으로 둡니다[17]. 예를 들어 삭제 규칙은 `codespaces.destroy`, `environment.delete`, `project.delete`, `repo.destroy` 를, 이전 규칙은 `migration.create`, `org.transfer_outgoing`, `org.transfer`, `repo.transfer_outgoing` 을, 새 비밀 규칙은 `codespaces.create_an_org_secret`, `environment.create_actions_secret`, `org.create_actions_secret`, `repo.create_actions_secret` 을 찾습니다[17]. 그 밖에 고위험 설정 끄기, 새 조직 구성원, 외부 협력자, 비밀 푸시 차단 우회·끄기, 자체 호스팅 러너 변경, 비공개 저장소 포크 허용, SSH 인증서 설정 변경, Pages 공개 전환, 저장소 보관 상태 변경, 비밀 스캔 기능 끄기, 오래된 의존성·취약점 알림 끄기 규칙이 있습니다[17]. 규칙을 로그에 돌리는 방법은 [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md)에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 보는 것 |
|---|---|
| [Okta 시스템 로그](okta.md) | SSO 로 GitHub 에 들어왔다면 같은 시각의 인증 기록과 IP |
| [Slack 감사 로그](slack.md) | 저장소 링크·토큰을 주고받은 시각과 복제 시각 |
| [Entra ID 로그](../m365/entra-logs/index.md) | Entra ID 로 SAML·OIDC SSO 를 한다면 `org_credential_authorization.grant` 앞뒤의 로그인 |
| 개인 보안 로그 | Enterprise Managed Users 가 아닐 때 엔터프라이즈 로그에 없는 로그인·개인 자원 동작(계정 본인이 내보내야 함)[14] |
| 단말의 Git 흔적 | 감사 로그의 `git.clone` 시각에 맞는 로컬 저장소 폴더가 어느 PC 에 생겼는지 |

토큰이 새어 나간 경우의 흐름은 [액세스 키가 새어 나갔나](../../04-scenarios/infrastructure/leaked-keys.md), 퇴사 전 대량 복제는 [퇴사자가 자료를 가져갔나](../../04-scenarios/data-leak/departing-employee.md), 여러 서비스의 시각을 한 줄로 세우는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다. 보관 기간이 지나 API 로 받을 수 없는 기록은 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)을 검토합니다. GitHub 는 계정 접근 기록을 법원 명령이나 수색 영장이 있을 때만 내주고, 미국 법집행기관이 공식 요청하면 계정 기록을 최대 90일 보존합니다[16]. 사건 초기에 할 일은 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)에 있습니다.

## 실습

아래 질문은 이 쪽의 만든 예시 레코드와 시험용 GitHub 조직으로 풀어 봅니다.

1. 위 예시 레코드의 `created_at` 을 한국 시각으로 바꾸면 몇 시입니까?
2. 시험 조직에서 비공개 저장소를 복제한 뒤 조직 감사 로그 화면에서 `action:git.clone` 으로 검색하면 무엇이 나옵니까? 같은 이벤트를 REST 로 받으려면 인자를 어떻게 줍니까?
3. 웹에서 풀 요청을 병합한 뒤 Git 이벤트 내보내기를 받으면 그 병합의 푸시가 들어 있습니까? 없다면 병합은 어느 이벤트로 찾습니까?
4. IP 공개를 켜기 전에 생긴 이벤트에도 IP 가 나옵니까? 공개 저장소를 다룬 이벤트는 어떻습니까?
5. 스트림을 열흘 동안 멈췄다가 다시 켰습니다. 멈춘 기간 가운데 어느 구간이 스트림에서 빠지고, 그 구간은 어디서 다시 받습니까?

## 참고 문헌

1. GitHub, "About the audit log for your enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/about-the-audit-log-for-your-enterprise
2. GitHub, github/docs 저장소 재사용 조각 `data/reusables/audit_log/retention-periods.md`, `git-events-retention-period.md`, `only-three-months-displayed.md`. https://github.com/github/docs/blob/main/data/reusables/audit_log/retention-periods.md
3. GitHub, "About the audit log for your enterprise", GitHub Enterprise Server Docs. https://docs.github.com/en/enterprise-server@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/about-the-audit-log-for-your-enterprise
4. GitHub, "Reviewing the audit log for your organization", GitHub Docs. https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization
5. GitHub, "Searching the audit log for your enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/searching-the-audit-log-for-your-enterprise
6. GitHub, "Exporting audit log activity for your enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/exporting-audit-log-activity-for-your-enterprise
7. GitHub, "Using the audit log API for your enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/using-the-audit-log-api-for-your-enterprise
8. GitHub, "Identifying audit log events performed by an access token", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/identifying-audit-log-events-performed-by-an-access-token
9. GitHub, "Displaying IP addresses in the audit log for your enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/displaying-ip-addresses-in-the-audit-log-for-your-enterprise
10. GitHub, "Displaying IP addresses in the audit log for your organization", GitHub Docs. https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/displaying-ip-addresses-in-the-audit-log-for-your-organization
11. GitHub, "Streaming the audit log for your enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/streaming-the-audit-log-for-your-enterprise
12. GitHub, "Audit log events for your enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/audit-log-events-for-your-enterprise
13. GitHub, "Audit log events for your organization", GitHub Docs. https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/audit-log-events-for-your-organization
14. GitHub, "Reviewing your security log", GitHub Docs. https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/reviewing-your-security-log
15. GitHub, "REST API endpoints for organizations — Get the audit log for an organization", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/rest/orgs/orgs
16. GitHub, "GitHub Guidelines for Legal Requests of User Data", GitHub Docs. https://docs.github.com/en/site-policy/other-site-policies/guidelines-for-legal-requests-of-user-data
17. SigmaHQ, GitHub 감사 로그 탐지 규칙(rules/application/github/audit, 15개). https://github.com/SigmaHQ/sigma/tree/master/rules/application/github/audit
