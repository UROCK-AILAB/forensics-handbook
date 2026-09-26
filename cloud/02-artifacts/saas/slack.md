---
title: "Slack 감사 로그"
parent: "아티팩트 · 업무용 SaaS"
nav_order: 560
---

# Slack 감사 로그 (Slack)

Slack 조직에서 누가, 언제, 어느 IP·클라이언트로 무엇(로그인, 파일 내려받기, 앱 설치, 내보내기, 보존 설정 변경)을 했는지를 작업 이름 단위로 남기는 기록과, 요금제에 따라 그 자리를 대신하는 접근 로그·통합 로그·데이터 내보내기를 다룹니다.

## 무엇을 기록하나 · 왜 생기나

Slack 에는 성격이 다른 기록이 넷 있습니다. 조사할 때는 요금제부터 확인하고, 그 요금제에서 받을 수 있는 기록을 고릅니다.

| 기록 | 받는 곳 | 요금제 | 담는 것 |
|---|---|---|---|
| 감사 로그 (Audit Logs API) | `GET https://api.slack.com/audit/v1/logs`, 조직 대시보드 Audit Logs 화면 | Enterprise | 조직 전체의 사용자·앱 행동을 작업 이름 단위로[1][2] |
| 접근 로그 (access logs) | `team.accessLogs` API, 관리 화면 Access logs | 유료(Pro·Business+·Enterprise) | 사용자·IP·사용자 에이전트 조합별 첫 접근·마지막 접근 시각과 횟수[4][5] |
| 통합 로그 (integration logs) | `team.integrationLogs` API, 내보내기 안의 `integration_logs.json` | 관리자 권한 | 앱·서비스를 추가·제거·활성·비활성·변경한 기록[6][8] |
| 데이터 내보내기 (export) | 관리 화면 Import & export data(Enterprise 는 Organization settings → Security → Exports) → ZIP | 요금제마다 범위가 다름 | 메시지 본문, 파일 링크, 채널·사용자 목록[7][8] |

감사 로그는 조직 소유자가 Slack 안에서 벌어진 행동을 조회하라고 만든 읽기 전용 기록입니다[1]. 쓰기 메서드가 없고, 메시지 내용은 담지 않습니다[1]. 메시지 내용을 감시하려면 eDiscovery·DLP 솔루션을 씁니다[1]. Slack 이 행동이 적절했는지 자동으로 판단하지는 않지만, 통계로 튀는 행동은 `anomaly` 라는 작업 이름으로 따로 남깁니다[1][3]. 감사 로그가 모든 행동을 다 담지는 않고, 지원하는 이벤트는 가능한 감사 이벤트의 일부입니다[1].

## 위치와 버전별 차이

### 감사 로그 API

감사 로그는 Enterprise 요금제에서만 쓸 수 있고, 워크스페이스 단위가 아니라 조직(Enterprise organization) 전체 단위로 동작합니다[1]. 앱은 조직 소유자(Owner)가 조직에 설치해야 하고, 호출에 쓰는 토큰은 조직 소유자에 딸린 사용자 토큰(`xoxp` 로 시작)이어야 하며 `auditlogs:read` 범위가 있어야 합니다[1][2]. 조직 관리자(Administrator) 토큰은 지원하지 않습니다[2].

| 끝점 | 하는 일 | 인증 |
|---|---|---|
| `GET /audit/v1/schemas` | 돌려주는 객체 종류 목록 | 필요 없음 |
| `GET /audit/v1/actions` | 작업 이름 목록과 짧은 설명 | 필요 없음 |
| `GET /audit/v1/logs` | 조직의 감사 이벤트 | 필요 |

`/logs` 는 쿼리 문자열 필터를 받고, 여러 필터는 AND 로 묶입니다[2]. `oldest`·`latest` 는 유닉스 시각 정수이고 양 끝을 포함하며, `limit` 은 최대 9999, `action` 은 쉼표로 최대 30개, `actor` 는 행위자 사용자 ID, `entity` 는 대상 ID 입니다[2]. 2018년 3월 이전 데이터는 없습니다[2]. 한 번에 최대 9,999건을 최신순으로 돌려주고, 그 뒤는 커서로 넘깁니다[2]. 속도 제한은 Tier 3(분당 최대 50회, 가끔 몰리는 호출은 허용)이고, 앱마다가 아니라 조직 전체 한도로 계산합니다[2].

조직 대시보드의 Audit Logs 화면에서도 검색과 CSV·JSON 내보내기를 할 수 있고, 이 화면을 쓴 일 자체도 감사 로그에 남습니다(아래 작업 이름 표)[2].

### 접근 로그

관리 화면 경로는 요금제마다 다릅니다[5].

| 요금제 | 경로 |
|---|---|
| Pro·Business+ | Admin → Workspace settings → Security → Access logs |
| Enterprise | 조직 이름 → Tools & settings → Workspace settings → 워크스페이스 선택 → Access Logs |

API 는 `team.accessLogs` 이고 사용자 토큰의 `admin` 범위가 필요하며, 유료 요금제가 아니면 `paid_only` 오류가 납니다[4]. 조직 토큰으로 부를 때 워크스페이스 ID 를 `team_id` 로 넘기면 팀 사이트와 타사 앱 접근만 오고, `team_id` 를 빼면 데스크톱·모바일·웹을 포함한 조직 전체 접근이 옵니다[4]. Enterprise 의 워크스페이스 화면에는 모바일 세션·웹 방문·타사 앱 행동이 다 나오지 않으므로 API 로 받는 편이 더 완전합니다[5]. 구성원도 자기 계정의 접근 로그를 볼 수 있습니다[5].

### 내보내기와 보존 (2026년 9월 문서 기준)

| 내보내기 범위 | Free | Pro | Business+ | Enterprise |
|---|---|---|---|---|
| 공개 채널 메시지·파일 링크 | 가능 | 가능 | 가능 | 가능 |
| 공개·비공개 채널·DM 전체 | 불가 | 불가 | 신청 후 가능 | 신청 후 가능 |
| 정기 내보내기 | 불가 | 불가 | 신청 후 가능 | 불가 |
| 대화 종류·구성원·워크스페이스별, 사용자 한 명의 모든 대화 | 불가 | 불가 | 불가 | 신청 후 가능 |

Free 요금제는 최근 90일 파일 링크만 내보냅니다[7].

보존 정책은 내보내기에 무엇이 남는지를 바꿉니다[9]. 유료 요금제는 워크스페이스가 있는 동안 보관하는 것이 기본이고, 기간을 정해 자동 삭제하도록 바꿀 수 있습니다[9]. Free 요금제는 "메시지는 1년 보관하되 편집·삭제는 추적하지 않음" 과 "90일 뒤 삭제" 가운데 고릅니다[9]. 삭제 작업은 하루 한 번 돌고, 보존 정책으로 지운 데이터는 영구 삭제입니다[9]. Business+·Enterprise 에서 전체 내보내기 승인을 받았으면 채널에서는 지우고 내보내기로는 남기는 설정이 있습니다[9]. 서비스별 보관 기간 비교는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에 모았습니다.

## 구조

### 감사 이벤트

감사 이벤트 하나는 행위자 (actor), 작업 (action), 대상 (entity), 맥락 (context) 네 덩어리로 되어 있고, 필요할 때 `details` 가 붙습니다[1]. 아래는 문서 예의 모양을 따라 만든 예시입니다.

```json
{
  "id": "5f2c0a1e-3b4d-4e6f-8a9b-0c1d2e3f4a5b",
  "date_create": 1788228787,
  "action": "file_downloaded",
  "actor": {
    "type": "user",
    "user": { "id": "W0EXAMPLE1", "name": "Example User", "email": "user@example.com", "team": "T0EXAMPLE1" }
  },
  "entity": {
    "type": "file",
    "file": { "id": "F0EXAMPLE1", "name": "report.xlsx" }
  },
  "context": {
    "location": { "type": "workspace", "id": "T0EXAMPLE1", "name": "example", "domain": "example" },
    "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "session_id": "123456789012",
    "ip_address": "203.0.113.10"
  }
}
```

| 필드 | 뜻 |
|---|---|
| `id` | 이벤트 ID |
| `date_create` | 이벤트 시각, 유닉스 초 |
| `action` | 작업 이름(`user_login`, `file_downloaded` 등) |
| `actor.user.id` | 행위자 사용자 ID(`W`·`U` 로 시작) |
| `entity.type` | 대상 종류. 사용자 `W…`, 채널 `C…`, 파일 `F…`, 앱 `A…`, 워크스페이스 `T…`, 엔터프라이즈 `E…` 모양의 ID 가 함께 온다 |
| `context.location.type` | `workspace` 또는 `enterprise` |
| `context.ua`, `context.ip_address`, `context.session_id` | 그때 쓴 사용자 에이전트, IP, 세션 ID |
| `context.app` | 앱이 일으킨 작업일 때만. `id`, `name`, `scopes`, `scopes_bot`, `creator`, `team` |
| `details` | 설정 변경의 이전 값·새 값, 초대한 사람, 이상 판정 이유 등 |

`context.app` 은 예전에 모든 이벤트에 붙고 앱이 아니면 null 이었지만, 지금은 필요할 때만 나옵니다[1]. 행위자 없이 생긴 이벤트는 자리 채움 ID `USLACKUSER`, Slack 보안 담당이 자격 증명을 재설정한 이벤트는 `USLACKSECURITY` 를 행위자로 씁니다[1][2]. 봇 사용자의 메일은 `botuser-T…-A…@slack-bots.com` 모양입니다[1]. Slackbot 이 사용자 대신 한 행동(예: `canvas_edited`)에는 `acting_agent: Slackbot` 과 `agent_message`(`channel_id`, `message_ts`, `thread_ts`)가 붙어, 어떤 대화의 요청으로 한 일인지 이어 볼 수 있습니다[2].

### 조사에 쓰는 작업 이름

작업 이름은 수백 개이고 계속 늘어나므로, 사건마다 `GET /audit/v1/actions` 로 목록을 받아 확인합니다[1][2].

| 묶음 | 작업 이름 |
|---|---|
| 로그인·세션 | `user_login`, `user_login_failed`, `user_logout`, `user_logout_compromised`(손상된 기기라서 로그아웃), `user_session_invalidated`, `user_session_reset_by_admin`, `user_sessions_reset_by_anomaly_event_response`, `bulk_session_reset_by_admin`, `cli_login`, `user_password_reset_requested`, `user_password_reset_slack_security`, `user_email_updated` |
| 계정·권한 | `user_created`, `user_deactivated`, `guest_created`, `role_change_to_admin`, `role_change_to_owner`, `role_change_to_user` |
| 파일 | `file_uploaded`, `file_downloaded`, `file_download_blocked`, `file_shared`, `file_public_link_created`, `file_public_link_revoked` |
| 채널 | `user_channel_join`, `private_channel_converted_to_public`, `channel_email_address_created` |
| 내보내기 | `manual_export_started`·`_completed`·`_downloaded`·`_deleted`, `scheduled_export_*`, `channels_export_*`, `manual_user_export_*`, `corporate_exports_approved`, `corporate_exports_enabled` |
| 감사 로그 화면 사용 | `audit_logs_records_searched`, `audit_logs_export_csv_started`, `audit_logs_export_json_started` |
| 앱 | `app_installed`, `app_scopes_expanded`, `app_approved`, `app_restricted`, `app_uninstalled` |
| 보존·법적 보존 | `pref.public_channel_retention_changed`, `pref.private_channel_retention_changed`, `pref.dm_retention_changed`, `pref.file_retention_changed`, `pref.retention_override_changed`, `channel_retention_changed`, `legal_hold_policy_created`, `legal_hold_policy_released` |
| 보안 설정 | `pref.sso_setting_changed`, `pref.two_factor_auth_changed`, `pref.session_duration_changed`, `pref.block_file_download_for_unapproved_ip`, `team_authorized_ip_range_set`, `pref.anomaly_event_response_changed` |
| 메시지 관리 | `message_tombstoned`, `message_restored`, `message_moderated` |

보존 설정을 바꾼 이벤트의 `details` 에는 이전 값과 새 값이 들어갑니다[2]. 값은 `RETAIN_ALL`(모두 보관, 편집 이력 추적), `RETAIN_MSGS`(모두 보관, 편집 이력 추적 안 함), `EXPIRE_ALL`(메시지와 편집 이력 삭제), `EXPIRE_MSGS`(정한 날수 뒤 삭제)이고, null 이면 `EXPIRE_MSGS` 로 봅니다[2].

### 이상 이벤트

작업 이름 `anomaly` 는 다른 감사 이벤트와 모양이 같고, `details` 에 판정 이유가 붙습니다[3]. `details.reason` 은 이유 코드 배열이고, 함께 `details.previous_ip_address`, `details.previous_ua`, `details.location`, `details.action_timestamp`, `details.ip_address_details` 가 옵니다[3]. `ip_address_details` 값은 `new-asn`(이 토큰으로 최근 본 적 없는 ASN), `cloud-asn`(사용자에게 드문 클라우드 ASN), `in-ioc-list`(침해 지표 목록에 든 IP)입니다[3]. `previous_ua`·`previous_ip_address` 는 세션을 연 뒤 다른 값으로 접속한 적이 없으면 비어 있습니다[3].

| 이유 코드 | 대상 | 뜻 |
|---|---|---|
| `ip_address`, `asn` | 앱·사용자 | IP 사용 이력에서 벗어남, 의심 ASN(`asn` 은 늘 `ip_address` 와 같이 나옴) |
| `tor` | 앱·사용자 | Tor 출구 노드 사용 |
| `excessive_downloads`, `excessive_file_shares`, `excessive_malware_uploads` | 앱·사용자 | 파일 내려받기·공유·악성 파일 업로드가 지나치게 많음 |
| `session_fingerprint` | 사용자 | 세션 쿠키 시각이 이상하거나 클라이언트 지문이 다름 |
| `unexpected_client`, `spoofed_user_agent`, `unexpected_user_agent`, `user_agent` | 사용자 | 클라이언트·사용자 에이전트가 예상과 다름. `unexpected_client` 이면 `details.detected_client`·`detected_os` 가 붙음 |
| `unexpected_admin_action`, `unexpected_api_call_volume`, `unexpected_scraping`, `unexpected_message_deletion` | 사용자 | 관리자 행동·API 호출량·수집·메시지 삭제가 평소와 다름 |
| `potential_spam` | 사용자 | 방해가 될 만큼 많은 API 호출. `details.api_call_method` 에 `chat.postMessage` 또는 `functions.workflows.publish` |
| `unexpected_credential_testing` | 앱 | 자격 증명 시험으로 보이는 호출 |
| `search_volume` | 사용자 | 수상한 검색량. 재정비 중이며 `5-02-2025` 부로 폐기(deprecated)됨 |

### 접근 로그 항목

접근 로그 한 항목은 개별 접속이 아니라 사용자·IP·사용자 에이전트 조합 하나를 모은 것입니다[4]. 필드는 `user_id`, `username`, `date_first`(그 조합의 첫 기록), `date_last`(가장 최근 기록), `count`(그 조합의 전체 횟수), `ip`, `user_agent`, `isp`, `country`, `region` 이고, `isp`·`country`·`region` 은 IP 로 추정한 값입니다[4]. 실제 로그인뿐 아니라 Slack 을 쓸 때 보통 부르는 API 호출도 셉니다[4]. 새 항목은 로그인, 앱·웹 클라이언트 열기, 새 IP·기기로 로그인, 사용자 대신 앱·봇이 행동할 때 생깁니다[5].

### 통합 로그 항목

서비스면 `service_id`·`service_type`, API 앱이면 `app_id`·`app_type` 이 오고, 공통으로 `user_id`, `user_name`, `channel`, `date`, `change_type`, `scope` 가 있습니다[6]. `change_type` 값은 `added`, `removed`, `enabled`, `disabled`, `expanded`, `updated` 이고, `disabled` 이면 `reason`(`user`, `rate_limits`, `slack`, `errors`, `system`, `admin`, `api_decline`, `deauth`)이 붙습니다[6].

### 내보내기 ZIP

JSON 내보내기 ZIP 에는 `channels.json`(공개 채널), `groups.json`(비공개 채널), `dms.json`, `mpims.json`(그룹 DM), `users.json`(Enterprise 조직이면 `org_users.json`), `integration_logs.json`, `canvases.json`, 콘텐츠 신고가 켜진 Enterprise 면 `content_flags.json` 이 들어갑니다[8]. 대화마다 폴더가 있고, 그 안에 메시지를 보낸 날짜별 JSON 파일이 있습니다[8]. 사용자 한 명의 대화를 TXT 로 내보내면 `channels`, `dms`, `files` 폴더가 생깁니다[8].

메시지에는 `type`, `user`, `text`, `ts` 가 있고, 하위 유형 (subtype) 으로 `bot_message`, `message_changed`, `message_deleted`, `channel_join`, `channel_leave`, `channel_name`, `channel_archive`, `file_share` 같은 값이 붙습니다[8]. 보존 정책이 편집·삭제 기록을 남기게 되어 있으면, 편집된 메시지는 편집한 날짜 파일에 `subtype: message_changed`, `previous.text`(원래 글), `original_ts`, `editor_id` 로 남고, 삭제된 메시지는 삭제한 날짜 파일에 빈 `text` 와 `previous.text`, `original_ts` 로 남습니다[8].

## 증거로서 의미

**증명하는 것**

- 어느 계정(행위자 ID)이 어느 시각(`date_create`)에 어느 대상(파일·채널·앱·사용자)에 어떤 작업을 했다는 Slack 쪽 기록과, 그때 쓴 IP·사용자 에이전트·세션 ID[1].
- 앱이 한 작업이면 어느 앱이 어떤 범위로 했는지(`context.app`)[1].
- 공개 링크를 만든 일, 내보내기를 시작하고 내려받은 일, 보존 설정을 바꾼 일과 그 이전 값[2].
- 접근 로그로는 한 계정이 어떤 IP·클라이언트 조합으로 처음과 마지막에 언제 들어왔고 몇 번 접근했는지[4].
- 내보내기에 편집·삭제 기록이 있으면 원래 글과 편집·삭제 시각[8].

**증명하지 못하는 것**

- 메시지 본문은 감사 로그에 없습니다[1]. 본문은 내보내기로 따로 봐야 합니다.
- `file_downloaded` 는 "내려받았거나 Slack 안에서 봤다" 는 뜻이라 기기에 저장했는지 화면에서 보기만 했는지 가를 수 없습니다[2].
- 감사 로그는 모든 행동을 담지 않으므로, 작업 이름이 없다고 그 행동이 없었다고 말할 수 없습니다[1].
- 접근 로그의 `country`·`region`·`isp` 는 추정값이라 실제 위치를 증명하지 않습니다[4]. IP·위치 해석의 일반론은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md)에 있습니다.
- `anomaly` 는 Slack 의 통계 판정이지 침해가 있었다는 증명이 아닙니다[1][3].

## 시각 해석

| 값 | 형식 | 비고 |
|---|---|---|
| 감사 로그 `date_create`, 필터 `oldest`·`latest` | 유닉스 초(정수) | UTC 기준 epoch[1][2] |
| `anomaly` 의 `details.action_timestamp` | 16자리 정수 | 단위 표기 없음. 예 값 `1644428253989994` 를 마이크로초로 읽으면 같은 레코드의 `date_create`(1644428305)보다 51초 앞서므로, 판정 대상 행동의 시각을 마이크로초로 적은 값일 가능성이 있습니다[3] |
| 접근 로그 `date_first`·`date_last` | 유닉스 초 | 조합별 첫·마지막 시각만 있음[4] |
| 통합 로그 `date` | 유닉스 초를 담은 문자열(예 `"1392163200"`) | [6] |
| 메시지 `ts`, `original_ts` | 소수점 아래 여섯 자리가 붙은 유닉스 초 문자열(예 `"1355517523.000005"`) | 편집·삭제 레코드에서는 `ts` 가 편집·삭제 시각, `original_ts` 가 원래 메시지 시각[8] |
| TXT 내보내기 | `[2020-04-20 13:47:27]` 모양 | GMT[8] |

접근 로그는 조합마다 첫 시각과 마지막 시각만 남으므로 그 사이의 개별 접속 시각은 알 수 없습니다[4]. 사용 중인 계정의 접근 로그 화면은 5~10분마다 갱신됩니다[5]. 조직에서 실제로 받을 수 있는 가장 오래된 감사 기록은 `oldest` 를 과거로 두고 받아 가장 오래된 `date_create` 로 확인합니다. 유닉스 시각과 시간대를 다루는 법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 정리했습니다.

## 함정과 한계

- Enterprise 가 아니면 감사 로그 API 가 없습니다[1]. Pro·Business+ 조사는 접근 로그, 통합 로그, 내보내기로 합니다.
- 조직 관리자 토큰으로는 감사 로그를 부를 수 없고 조직 소유자 토큰이어야 합니다[2]. 수집 권한을 미리 정해 둡니다.
- `user_channel_join` 에서 초대받아 들어간 경우 초대한 사람이 `details` 에 들어가고 `context` 도 초대한 사람의 것입니다[2]. 이 이벤트의 IP·사용자 에이전트를 들어간 사람의 것으로 읽으면 틀립니다.
- eDiscovery 앱이 일으킨 파일 내려받기는 행위자가 앱을 설치한 사용자로 남습니다[1]. 앱 설치자가 직접 내려받았다고 쓰기 전에 `context.app` 을 봅니다.
- 개요 문서에는 `file_downloaded_blocked`, 작업 목록에는 `file_download_blocked` 로 이름이 달리 적혀 있습니다[1][2]. 실제 데이터에 나오는 값을 세어 보고 필터를 짭니다.
- 통합 로그 API 인자 `change_type` 의 허용값에는 `expanded` 가 없지만 응답 값 목록에는 있습니다[6]. `expanded` 로 거르지 말고 전부 받은 뒤 나눕니다.
- 신뢰 ASN·CIDR 허용 목록에 든 곳에서 온 접속은 이상으로 표시되지 않습니다[3]. `anomaly` 가 없다는 결론을 내기 전에 `admin.audit.anomaly.allow.getItem` 으로 허용 목록을 확인합니다.
- `limit` 보다 많은 건수가 올 수 있고(같은 시각 기록), 기본 정렬이 최신순입니다[2]. 건수로 수집 완료를 판단하지 말고 커서가 끝날 때까지 받습니다.
- 보존 정책이 편집·삭제를 추적하지 않으면 내보내기에 수정·삭제 흔적이 없고, 보존 정책으로 지운 기간은 폴더 자체가 없습니다[8]. 정책을 바꾼 일은 `pref.*_retention_changed` 로 남으므로 삭제 흔적이 비어 있으면 이 작업 이름부터 찾습니다[2]. 로그 자체를 지우거나 줄이는 흔적의 일반론은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md)에 있습니다.
- 내보내기는 스레드 답글과 채널 메시지를 구분하지 않습니다(TXT)[8].

## 직접 분석해 보기

### 원시 레코드로 한 번

위 만든 예시 레코드에서 `date_create` 1788228787 을 UTC 로 바꾸면 2026-09-01 02:13:07 입니다. 행위자 `W0EXAMPLE1` 이 `context.location.type` 이 `workspace` 인 곳에서 파일 `F0EXAMPLE1` 에 `file_downloaded` 를 했고, `context.app` 이 없으므로 앱이 아니라 사용자 세션 `123456789012` 에서 일어난 작업입니다. 같은 `session_id` 로 앞뒤 레코드를 모으면 로그인부터 이어지는 한 세션의 흐름을 볼 수 있습니다.

```sh
# 시각 바꾸기
date -u -d @1788228787
# 받은 감사 로그(JSON)에서 한 계정의 파일 관련 작업만 시각순으로
jq -r '.entries[] | select(.actor.user.id=="W0EXAMPLE1") | select(.action|startswith("file_"))
  | [(.date_create|todate), .action, .entity.file.id, .context.ip_address, .context.session_id] | @tsv' logs.json | sort
```

### 공개 도구로 한 번

이 서비스의 기록은 공식 API 와 관리 화면으로 받습니다. 감사 로그는 `/audit/v1/logs` 를 `oldest`·`latest` 로 기간을 잘라 커서가 끝날 때까지 받고, 같은 기간의 `/audit/v1/actions` 응답도 함께 보관합니다[2]. 유료 요금제면 `team.accessLogs` 를 `before` 에 받은 가장 오래된 값을 넣어 가며 과거로 넘기고[4], `team.integrationLogs` 로 앱 변경 기록을 받습니다[6]. 받은 원본은 메타데이터까지 그대로 사본으로 두고 해시를 계산해 무결성을 확인할 수 있게 합니다[10]. 보존 절차는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md), Slack 에 기록을 요청하는 절차는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)에 있습니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| 신원 공급자 로그인 기록([Okta 시스템 로그](okta.md), [Entra ID 로그](../m365/entra-logs/index.md), [Google Workspace 로그인 기록](../google-workspace/login-audit.md)) | Slack `user_login` 의 IP·시각과 SSO 로그인이 맞물리는지 |
| 접근 로그 ↔ 감사 로그 | 같은 IP·사용자 에이전트 조합이 `user_login` 과 `date_first`·`date_last` 범위에 함께 나오는지 |
| 통합 로그 ↔ 감사 로그 `app_*` | 앱 추가·범위 확장 시각과 설치한 사용자가 같은지. 동의 흐름은 [OAuth 앱과 동의](../../01-foundations/identity/oauth-consent.md) |
| 내보내기 메시지 ↔ `file_shared`·`file_public_link_created` | 파일을 공유한 대화와 시각 |
| 엔드포인트 기록(브라우저 방문 기록, 내려받은 파일) | `file_downloaded` 가 실제 저장으로 이어졌는지 |

여러 서비스의 기록을 한 시간축에 놓는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)에 있고, 퇴사자 유출 사건에서 이 기록을 쓰는 순서는 [퇴사자가 자료를 가져갔나](../../04-scenarios/data-leak/departing-employee.md)에서 이어집니다. 비슷한 업무 메신저 기록은 [Teams](../m365/teams.md)를 봅니다.

## 실습

아래 질문은 만든 예시 기록을 두고 푸는 문제입니다.

1. `file_downloaded` 가 한 사용자에게 5분 동안 200건 있고, 같은 시간대에 `anomaly`(`excessive_downloads`)가 있다. 보고서에 "파일 200개를 빼돌렸다" 고 쓸 수 있는가? 무엇을 더 확인해야 하는가?
2. `user_channel_join` 레코드의 `context.ip_address` 가 203.0.113.50 이고 `details` 에 다른 사용자가 있다. 이 IP 는 누구의 것인가?
3. Business+ 워크스페이스에서 한 달 전 삭제된 메시지를 찾아야 한다. 어떤 기록을 어떤 순서로 보는가? 보존 설정이 도중에 바뀌었는지는 무엇으로 확인하는가?
4. 사건 기간에 `anomaly` 가 하나도 없다. 이상 접속이 없었다고 결론 내리기 전에 확인할 것은?
5. 접근 로그에 한 조합의 `date_first` 가 사건 한 달 전, `date_last` 가 사건 당일, `count` 가 340 이다. 사건 당일 몇 번 접속했는지 말할 수 있는가?

보고서 문장은 "2026-09-01 02:13:07 UTC 에 계정 user@example.com 으로 파일 F0EXAMPLE1 에 대해 `file_downloaded` 가 기록되어 있다(IP 203.0.113.10). 이 작업 이름은 내려받기와 보기를 구분하지 않는다" 처럼 기록으로 확인되는 만큼만 씁니다(만든 예시). 요금제·보존 설정 때문에 비어 있는 구간은 "기록이 없다" 가 아니라 "이 요금제·설정에서는 기록되지 않는다" 로 씁니다. 보고서 전체 틀은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)를 봅니다.

## 참고 문헌

1. Slack, "Monitoring workspace events with the Audit Logs API". https://api.slack.com/admins/audit-logs
2. Slack, "Audit Logs API endpoints & actions". https://api.slack.com/admins/audit-logs-call
3. Slack, "Audit logs anomaly events". https://api.slack.com/admins/audit-logs-anomaly
4. Slack, "team.accessLogs method". https://api.slack.com/methods/team.accessLogs
5. Slack 도움말, "View access logs for your workspace". https://slack.com/help/articles/360002084807-View-access-logs-for-your-workspace
6. Slack, "team.integrationLogs method". https://docs.slack.dev/reference/methods/team.integrationLogs
7. Slack 도움말, "Export your workspace data". https://slack.com/help/articles/201658943-Export-your-workspace-data
8. Slack 도움말, "How to read Slack data exports". https://slack.com/help/articles/220556107-How-to-read-Slack-data-exports
9. Slack 도움말, "Customize message and file retention policies". https://slack.com/help/articles/203457187-Customize-message-and-file-retention-policies
10. Eoghan Casey, "SaaS Forensics & Response: Forensic Preservation, Recovery, and Analysis of SaaS Data", DFRWS USA 2023 발표(Baltimore, 2023-07-11). https://dfrws.org/presentation/saas-forensics-and-response/
