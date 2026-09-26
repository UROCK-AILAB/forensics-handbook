---
title: "Dropbox·Box 기록"
parent: "아티팩트 · 업무용 SaaS"
nav_order: 570
---

# Dropbox·Box 기록 (Dropbox·Box)

Dropbox 팀 이벤트 로그와 Box 기업 이벤트는 팀·기업 계정 안에서 누가 언제 어떤 파일을 내려받고, 지우고, 공유했는지를 서비스 쪽에 남기는 감사 기록입니다.

## 무엇을 기록하나 · 왜 생기나

Dropbox 는 팀(Dropbox Business) 계정에서 일어난 로그인·파일 작업·공유·기기 연결·관리자 작업을 팀 이벤트 (Team Event) 로 남기고, 관리자는 `team_log/get_events` API 로 이를 받습니다[1]. 이벤트는 범주 (category) 와 이벤트 유형 (event type) 으로 나뉘고, 범주는 `logins`, `file_operations`, `sharing`, `devices`, `apps`, `members`, `passwords`, `reports`, `data_governance`, `admin_alerting` 등 스물여섯 가지입니다[1].

Box 는 기업 (Enterprise) 안의 모든 사용자 동작을 기업 이벤트 (Enterprise Events) 로 남기고, `GET https://api.box.com/2.0/events` 에 `stream_type` 을 `admin_logs` 또는 `admin_logs_streaming` 으로 주어 받습니다[5][7]. 이 API 는 기업 관리자나 "Run new reports and access existing reports" 권한이 있는 공동 관리자만 부를 수 있습니다[5].

두 서비스 모두 유출 조사에서 "누가 어느 파일을 받아 갔나", "공유 링크를 누가 만들었고 링크로 누가 받았나", "처음 보는 기기나 앱이 계정에 붙었나" 를 답하는 기본 자료입니다. 같은 질문을 Microsoft 365 와 Google Workspace 에서 푸는 방법은 [SharePoint·OneDrive](../m365/sharepoint-onedrive.md), [Drive 기록](../google-workspace/drive-audit.md) 에 있습니다.

조사에 자주 쓰는 이벤트는 다음과 같습니다. Dropbox 는 괄호 안이 범주입니다.

| 알고 싶은 것 | Dropbox `event_type`[1] | Box `event_type`[5][6] |
|---|---|---|
| 로그인 성공·실패 | `login_success`, `login_fail`, `logout` (logins) | `LOGIN`, `FAILED_LOGIN` |
| 관리자가 사용자 계정으로 들어감 | `sign_in_as_session_start`, `sign_in_as_session_end` (logins) | `ADMIN_LOGIN` |
| 처음 보는 기기 | `device_link_success`, `device_unlink`, `device_change_ip_desktop` (devices) | `ADD_LOGIN_ACTIVITY_DEVICE`, `REMOVE_LOGIN_ACTIVITY_DEVICE` |
| 내려받기·보기 | `file_download`, `file_preview` (file_operations) | `DOWNLOAD`, `PREVIEW`, `ITEM_OPEN`, `CONTENT_ACCESS` |
| 올리기·옮기기·이름 바꾸기 | `file_add`, `file_move`, `file_rename` (file_operations) | `UPLOAD`, `MOVE`, `COPY`, `RENAME`, `EDIT` |
| 지우기·되살리기 | `file_delete`, `file_permanently_delete`, `file_restore`, `file_rollback_changes`, `rewind_folder` (file_operations) | `DELETE`, `UNDELETE` |
| 공유 링크 | `shared_link_create`, `shared_link_download` (sharing) | `SHARE`, `UNSHARE`, `ITEM_SHARED_UPDATE`, `SHARE_EXPIRATION`, `SHARED_LINK_SEND` |
| 공유 폴더·협업자 | `shared_folder_create`, `shared_content_add_member`, `shared_content_download` (sharing) | `COLLABORATION_INVITE`, `COLLABORATION_ACCEPT`, `COLLABORATION_REMOVE`, `COLLABORATION_ROLE_CHANGE` |
| 앱·토큰 연결 | `app_link_user`, `app_link_team` (apps) | `USER_AUTHENTICATE_OAUTH2_ACCESS_TOKEN_CREATE`, `OAUTH2_ACCESS_TOKEN_REVOKE`, `ENTERPRISE_APP_AUTHORIZATION_UPDATE` |
| 관리자 권한·보안 설정 | `member_change_admin_role` (members), `password_reset_all` (passwords) | `CHANGE_ADMIN_ROLE`, `DISABLE_MULTI_FACTOR_AUTH`, `ACCESS_GRANTED` |
| 동기화 | — | `ITEM_SYNC`, `ITEM_UNSYNC` |
| 이상 징후 경보·복구 | `ransomware_restore_process_completed` (admin_alerting) | `SHIELD_ALERT`, `CONTENT_WORKFLOW_ABNORMAL_DOWNLOAD_ACTIVITY` |

Box 의 `ACCESS_GRANTED` 는 사용자가 Box 지원팀에 자기 계정 접근을 허용한 일이고, `CONTENT_ACCESS` 는 인가된 사용자나 Box 앱이 프로그램으로 파일에 접근한 일입니다[5]. 기업 이벤트 안내의 목록에 없는 이벤트도 나올 수 있으므로, 허용 값 전체는 Event 자원 문서의 `event_type` 목록에서 봅니다[5][6].

## 위치와 버전별 차이

두 서비스 모두 기록은 서비스 회사 서버에만 있고, 관리자 권한으로 API 나 관리 콘솔에서 꺼내 옵니다. 받을 수 있는 기간이 흐름·요금제마다 다르므로 사건 날짜부터 확인하고, 필요한 구간은 먼저 받아 둡니다([로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)).

| 서비스 | 받는 곳 | 받을 수 있는 기간 | 순서·중복 |
|---|---|---|---|
| Box | `admin_logs` (Enterprise Event History API) | 최대 1년, `created_after`·`created_before` 로 범위 지정 | 이벤트 시각 순, 중복 없음, 지연이 큼[5][7] |
| Box | `admin_logs_streaming` (Enterprise Event Stream API) | 2주 | 순서 보장 없음, 중복 가능, 지연이 작음[5][7] |
| Box | 관리 콘솔 보고서 내보내기 | 7년 | —[5] |
| Dropbox | `team_log/get_events`, `team_log/get_events/continue` | 공개 명세에 기간이 없음 | 시각 순 정렬 보장 없음[1] |

Box 수치는 2026년 7월 문서 기준입니다. Dropbox 팀 이벤트 로그의 보관 기간은 `get_events` 에 오래된 `time` 범위를 주고 돌아오는 가장 이른 `timestamp` 로 테넌트마다 확인합니다.

Dropbox 는 요금제에 따라 기록되는 범주가 다릅니다. `file_operations` 범주와 이에 해당하는 Paper 이벤트는 모든 Dropbox Business 요금제에 있지 않고, 팀에서 쓸 수 있는지는 `features/get_values` 로 확인합니다[1]. API 호출에는 팀 인증(`auth = "team"`), 범위 `events.read`, 관리자 권한 "Team Auditing" 이 필요합니다[1].

지운 파일을 되살릴 수 있는 기간도 요금제마다 다릅니다(2026년 9월 문서 기준)[3].

| Dropbox 요금제 | 기본 복구 기간 |
|---|---|
| Basic, Plus, Family | 30일 |
| Professional, Essentials, Standard, Business | 180일 |
| Advanced, Business Plus, Enterprise, Education | 365일 |

추가 상품으로 기간이 늘 수 있고, 데이터 폐기 정책 (data disposition policy) 이 걸린 파일은 이보다 일찍 영구 삭제될 수 있습니다[3]. 팀 관리자는 지운 파일 화면에서 본인, 특정 팀원, 모든 사람 가운데 누가 지운 파일을 볼지 고를 수 있습니다[3]. 로그의 기간과 파일 복구 기간은 서로 다른 값이라 따로 확인합니다. 보관 기간 전반은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 에 있습니다.

## 구조

### Dropbox 팀 이벤트

`get_events` 결과에는 `events`, `cursor`, `has_more` 가 있습니다[1]. `events` 는 시각 순으로 정렬되어 있지 않고, `has_more` 는 `events` 가 비어 있어도 `true` 일 수 있으므로 `has_more` 가 `false` 가 될 때까지 `get_events/continue` 로 이어 받습니다[1]. 한 번에 받는 개수 `limit` 은 1~1000(기본 1000)이고, `account_id` 를 주면 그 계정이 행위자(actor)·맥락(context)·참여자(participants) 중 하나인 이벤트만 옵니다[1]. `category` 와 `event_type` 을 함께 주면 `invalid_filters` 오류가 납니다[1].

이벤트 하나(TeamEvent)의 필드는 다음과 같습니다[1].

| 필드 | 뜻 |
|---|---|
| `timestamp` | 동작이 일어난 시각 |
| `event_category`, `event_type` | 범주와 이벤트 유형 |
| `actor` | 실제로 동작한 주체: `admin`, `anonymous`, `app`, `dropbox`(Dropbox 가 한 동작), `reseller`, `user` 중 하나. 사용자면 `account_id`, `display_name`, `email` |
| `origin` | 동작이 나온 곳: `geo_location`(`city`, `region`, `country`, `ip_address`) 과 `access_method` |
| `context` | 누구를 대신해 한 동작인지: `team_member`, `team`, `non_team_member`, `trusted_non_team_member`, `organization_team`, `anonymous` |
| `involve_non_team_member` | 행위자나 영향받은 사용자 가운데 팀 밖 사람이 있으면 `true` |
| `participants` | 영향받은 사용자·그룹(행위자와 `context` 사용자는 빠짐) |
| `assets` | 관련 파일·폴더 등: `file`, `folder`, `paper_document`, `paper_folder`, `showcase_document` |
| `details` | 이벤트 유형마다 다른 세부 필드 |

`access_method` 는 `end_user`(데스크톱·모바일·웹 세션과 `session_id`), `api`(`request_id`), `admin_console`, `content_manager`, `enterprise_console`, `sign_in_as` 가운데 하나이고, API 로 한 동작이면 `origin` 은 API 클라이언트를 가리킵니다[1]. 파일 경로는 `path` 의 `contextual`(이벤트 맥락 기준 전체 경로) 과 `namespace_relative`(네임스페이스 기준 경로) 두 가지로 적힙니다[1].

`details` 에는 이벤트마다 필요한 값이 들어갑니다. `login_fail` 에는 `login_method`, `error_details`, `is_emm_managed` 가 있고[1], `login_method` 값은 `password`, `saml`, `google_oauth`, `apple_oauth`, `microsoft_oauth`, `kakao_oauth`, `passkey`, `qr_code`, `two_factor_authentication`, `web_session` 등입니다[1]. `shared_link_download` 에는 링크 주인 `shared_link_owner` 가 들어갑니다[1].

### Box 기업 이벤트

응답은 `chunk_size`, `next_stream_position`, `entries` 로 되어 있고, `entries` 가 이벤트 목록입니다[6]. `limit` 은 기본 100, 최대 500 이고, `stream_position` 을 `now` 로 주면 빈 목록과 최신 위치를, `0` 이나 null 로 주면 처음부터 모든 이벤트를 돌려줍니다[7]. `event_type` 거르기는 `admin_logs` 계열에서만 되고, `created_after`·`created_before` 는 `admin_logs` 에서만 됩니다[7]. 이벤트 하나(Event)의 필드는 다음과 같습니다[6][8].

| 필드 | 뜻 |
|---|---|
| `created_at` | 이벤트 객체가 만들어진 시각 |
| `recorded_at` | 이벤트가 데이터베이스에 기록된 시각 |
| `event_id` | 이벤트 ID. 중복을 거를 때 씀 |
| `created_by` | 동작한 사용자(`id`, `name`, `login`). 로그인하지 않은 사용자는 `id` 가 `2` |
| `event_type` | 이벤트 유형 |
| `session_id` | 동작한 사용자의 세션. 모든 이벤트에 있지는 않음 |
| `source` | 이벤트를 일으킨 자원. 파일이면 `item_type`, `item_id`, `item_name`, `parent`, `owned_by`, 분류가 붙은 파일이면 `classification` |
| `additional_details` | 사용자가 어떻게 동작했는지 등 추가 정보. 기업 이벤트에만 있고 모든 이벤트에 있지는 않음 |

Box 이벤트에는 IP 주소 전용 필드가 없습니다[6]. IP 나 접속 방법이 필요하면 실제 데이터의 `additional_details` 와 `source` 에 무엇이 들어 있는지 이벤트 유형별로 먼저 확인합니다.

아래는 Event 자원 문서의 모양을 따라 만든 예시입니다. 값은 모두 지어낸 것입니다.

```json
{
  "type": "event",
  "created_at": "2026-09-01T11:13:07-07:00",
  "recorded_at": "2026-09-01T11:13:41-07:00",
  "event_id": "3c1f0b7a9e2d4c6b8a0f1e3d5c7b9a1f2e4d6c8b",
  "created_by": { "type": "user", "id": "20260901", "name": "Kim Example", "login": "user@example.com" },
  "event_type": "DOWNLOAD",
  "session_id": "5e7a9c1b3d5f7a9c1b3d5f",
  "source": {
    "item_type": "file",
    "item_id": "9000000001",
    "item_name": "budget-2027.xlsx",
    "parent": { "type": "folder", "name": "Finance", "id": "8000000001" },
    "owned_by": { "type": "user", "id": "20260001", "name": "Admin Example", "login": "admin@contoso.com" }
  }
}
```

## 증거로서 의미

**증명하는 것.** 이 계정(또는 익명 사용자·앱·관리자 대리 세션)이 이 시각에 이 파일에 대해 내려받기·보기·삭제·공유 링크 만들기 같은 동작을 했다고 서비스가 기록했다는 사실입니다. Dropbox 는 여기에 접근 방법(데스크톱·모바일·웹·API·관리 콘솔·`sign_in_as`)과 IP·지역 정보가 더해져, 같은 계정의 동작이 어느 세션에서 나왔는지 가를 수 있습니다[1]. `actor` 가 `admin` 이거나 `access_method` 가 `sign_in_as` 이면 관리자가 한 동작이고, `actor` 가 `app` 이면 앱이 한 동작입니다[1]. Box 에서 `created_by` 의 `id` 가 `2` 이면 로그인하지 않은 사용자이고, 열린 공유 링크로 로그인 없이 파일을 받은 경우가 그 예입니다[5].

**증명하지 못하는 것.** 내려받은 파일이 그 뒤 어디로 갔는지는 이 기록에 없고, 받은 PC·휴대폰의 흔적을 따로 봐야 합니다. Box 익명 사용자(`id` 2)가 누구인지는 이 기록만으로 알 수 없습니다[5]. Dropbox 의 `geo_location` 은 IP 에 붙은 지역 정보일 가능성이 있어 실제 위치의 증거로 쓰기 어렵고, IP 해석의 한계는 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md) 에 있습니다. 로그인 기록이 있다고 해서 비밀번호를 입력했다는 뜻도 아닙니다. Windows 브라우저의 자동 로그인 정보를 다른 PC 로 옮기면 Dropbox·Box 웹에 자동 로그인할 수 있었다는 시험 결과가 있어[11], 새 기기·새 IP 의 로그인이 비밀번호 입력 없이 생겼을 가능성도 있습니다.

## 시각 해석

Dropbox 의 `timestamp` 는 `%Y-%m-%dT%H:%M:%SZ` 형식이라 초 단위이고 끝의 `Z` 가 UTC 를 뜻합니다(예: `2017-01-25T15:51:30Z`)[1][2]. 동작이 일어난 시각을 뜻하지만 결과가 시각 순이 아니므로, 받은 뒤 `timestamp` 로 다시 정렬합니다[1]. 커서가 만료되면 `reset` 오류와 함께 커서가 마지막으로 돌려준 이벤트의 대략적인 시각이 오고, 이 시각부터 `get_events` 를 다시 부르면 됩니다[1].

Box 에는 `created_at`(이벤트가 만들어진 때)과 `recorded_at`(데이터베이스에 기록된 때) 두 시각이 있고, 둘 다 `2022-12-12T10:53:43-08:00` 처럼 UTC 와의 차이가 붙은 ISO 8601 형식입니다[6]. 사건 시각은 `created_at` 으로 적고, 타임라인에 넣을 때는 UTC 로 바꿉니다. `admin_logs` 는 늦게 도착하는 이벤트가 있어 거의 실시간으로 받으면 거르는 시간 범위를 지나 도착한 이벤트를 놓칠 수 있습니다[5]. 그러므로 사건 직후에 받은 사본은 시간이 지난 뒤 같은 범위로 한 번 더 받아 개수를 맞춰 봅니다. 여러 서비스의 시각을 맞추는 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 에 있습니다.

## 함정과 한계

- Dropbox 는 요금제에 따라 `file_operations` 범주가 없으므로, 내려받기 기록이 없다는 사실만으로 내려받지 않았다고 쓸 수 없습니다[1]. 팀에서 이 범주를 쓸 수 있는지 `features/get_values` 로 먼저 확인하고, 쓸 수 없으면 보고서에 "이 요금제에서는 파일 작업이 기록되지 않는다" 로 씁니다[1].
- Dropbox 이벤트의 여러 속성에는 과거 데이터가 빠져 있을 수 있고(historical data gap), 원본 이벤트를 읽다 오류가 나면 가져온 만큼만 담은 `MissingDetails` 가 남습니다[1].
- Box `admin_logs_streaming` 은 같은 이벤트를 두 번 이상, 순서 없이 돌려줄 수 있으므로 `event_id` 로 중복을 걸러야 건수가 맞습니다[5]. 2주가 지난 사건은 `admin_logs`(1년)나 관리 콘솔 보고서(7년)로 받습니다[5].
- Box `get-events` 문서의 `event_type` 설명에는 `adming_logs_streaming` 이라는 오타가 있습니다[7]. 실제 값은 `admin_logs_streaming` 입니다[5].
- rclone 으로 Dropbox 를 복사한 시험에서 파일 시각은 남았지만 폴더 시각은 모두 복사 명령을 실행한 시각이 되었고, Dropbox 클라이언트나 웹으로 받으면 원래 시각이 남았습니다[9]. 수집한 사본의 폴더 시각을 사건 시각으로 읽지 않습니다. rclone 은 공유 폴더·휴지통 같은 서비스 고유 기능을 지원하지 않고 API 에 기대므로, API 로 보이지 않는 파일은 빠질 가능성이 있습니다[9].
- 서비스가 달라도 이벤트 이름이 비슷해 보이지만 뜻이 같지는 않습니다. Box 의 `PREVIEW`·`ITEM_OPEN`·`DOWNLOAD` 와 Dropbox 의 `file_preview`·`file_download` 는 각 서비스 문서의 설명대로 따로 해석합니다.

## 직접 분석해 보기

**원자료를 한 번 직접 읽기.** Box 에서 받은 응답을 한 줄에 응답 하나씩 저장했다면, `event_id` 로 중복을 없애고 `created_at` 을 UTC 로 바꿔 정렬합니다. `jq` 로는 다음과 같습니다.

```sh
jq -s -r '
  def utc: if endswith("Z") then fromdate else
    capture("^(?<d>.{19})(?<s>[+-])(?<h>[0-9]{2}):(?<m>[0-9]{2})$") as $c
    | ($c.d + "Z" | fromdate) - ((if $c.s == "-" then -1 else 1 end) * (($c.h | tonumber) * 3600 + ($c.m | tonumber) * 60))
  end;
  [.[].entries[]] | unique_by(.event_id) | sort_by(.created_at | utc) | .[]
  | [(.created_at | utc | todate), .created_at, .recorded_at, .created_by.login, .created_by.id,
     .event_type, (.source.item_name // ""), (.source.item_id // "")] | @tsv' box_events.jsonl
```

`created_by.id` 가 `2` 인 줄은 익명 내려받기이므로, 같은 `item_id` 에 `SHARE` 가 언제 있었는지 거슬러 봅니다. `recorded_at` 이 `created_at` 보다 크게 늦은 줄이 있으면 늦게 도착한 이벤트입니다.

Dropbox 는 `events` 목록을 모두 모은 뒤 `timestamp` 로 정렬부터 합니다. 이벤트 유형·행위자 같은 union 값이 JSON 에 어떤 모양으로 적히는지는 받은 파일 첫 줄에서 확인한 뒤 거르는 식을 짭니다.

```sh
jq -s -r '[.[].events[]] | sort_by(.timestamp) | .[] | [.timestamp, (.origin.geo_location.ip_address // "")] | @tsv' dropbox_events.jsonl
```

**API 로 범위를 좁혀 받기.** Dropbox 는 `account_id` 로 한 사람의 이벤트만, `category` 또는 `event_type` 으로 한 종류만 받을 수 있습니다[1]. Box 는 `stream_type=admin_logs` 에 `created_after`·`created_before` 로 기간을, `event_type` 에 쉼표로 이은 목록(예: `DOWNLOAD,SHARE`)으로 종류를 좁힙니다[7].

**공개 도구.** 두 서비스 모두 공식 API 와 관리 콘솔 보고서 내보내기가 기본 수집 수단입니다. CATCH 는 공개 API 와 내부 API 를 함께 써서 인증·탐색·거르기·수집 네 단계로 클라우드 저장소 자료를 모으는 틀이고, 공개 API 로 Google Drive·Dropbox·OneDrive·Box 를 수집하는 kumodd 같은 앞선 도구를 함께 정리합니다[10]. rclone 은 OAuth 토큰으로 Dropbox 같은 원격 저장소를 복사하거나 읽기 전용으로 붙이는 도구이고, 설정 파일 `rclone.conf` 에 토큰이 들어 있습니다[9]. 수집한 로그를 다른 서비스 로그와 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| Dropbox `app_link_user`·`app_link_team`, Box `USER_AUTHENTICATE_OAUTH2_ACCESS_TOKEN_CREATE` | 수집 도구·외부 앱이 계정에 붙은 시각. rclone 같은 제3자 도구로 접근하면 연결된 앱으로 등록됩니다[9]. 동의 흐름은 [OAuth 앱과 동의](../../01-foundations/identity/oauth-consent.md) |
| Dropbox `device_link_success`·`device_change_ip_desktop`, Box `ADD_LOGIN_ACTIVITY_DEVICE` | 처음 보는 기기가 붙은 시각과 그 직후의 내려받기 |
| Dropbox `shared_link_create` → `shared_link_download`, Box `SHARE` → 익명 `DOWNLOAD` | 링크를 만든 사람과 링크로 받은 사람의 순서. 시나리오는 [외부 공유 링크로 새어 나갔나](../../04-scenarios/data-leak/external-sharing.md) |
| Dropbox `file_delete`·`file_permanently_delete`·`rewind_folder`, Box `DELETE`·`UNDELETE` | 지운 뒤 복구 기간 안에 되살릴 수 있는지와 되돌린 흔적 |
| IdP 로그인 기록(Okta 등) | SSO 로 들어왔다면 IdP 쪽 로그인 시각·IP. [Okta 시스템 로그](okta.md) |
| 단말의 동기화 클라이언트·브라우저 흔적 | 서비스에서 받은 파일이 어느 PC 에 남았는지. [Windows 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html) |

퇴사자 조사 흐름은 [퇴사자가 자료를 가져갔나](../../04-scenarios/data-leak/departing-employee.md), 저장소에서 대량으로 빼 간 흐름은 [클라우드 저장소에서 자료를 빼 갔나](../../04-scenarios/data-leak/storage-exfiltration.md) 에 있습니다. 서비스 회사에 자료를 요청할 때는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) 을 봅니다. Dropbox 는 정부의 자료 요청이 특정 개인·수사에 한정되어야 하고, 콘텐츠 요청은 내기 전에 법원이 검토·승인해야 한다는 원칙을 두고 있습니다[4].

## 실습

아래 질문은 만든 예시 상황입니다.

1. Box `admin_logs_streaming` 으로 받은 2주치 자료의 `DOWNLOAD` 건수가 같은 기간 `admin_logs` 로 받은 건수보다 많습니다. 원인과 건수를 맞추는 방법을 적어 봅니다.
2. Box `DOWNLOAD` 이벤트의 `created_by.id` 가 `2` 입니다. 이 파일에 대해 더 찾아볼 이벤트와 보고서에 쓸 수 있는 문장을 정해 봅니다.
3. Dropbox Standard 팀에서 퇴사자의 `file_download` 가 한 건도 없습니다. "내려받지 않았다" 고 쓸 수 있는지, 무엇을 먼저 확인할지 적어 봅니다.
4. Dropbox `file_download` 이벤트의 `access_method` 가 `sign_in_as` 이고, 몇 분 앞에 `sign_in_as_session_start` 가 있습니다. 이 내려받기를 누구의 동작으로 적을지 정해 봅니다.
5. rclone 으로 복사한 Dropbox 사본의 폴더 시각이 모두 같은 날입니다. 이 시각을 사건 타임라인에 넣어도 되는지 판단해 봅니다.

보고서 문장은 "2026-09-01 18:13:07 UTC 에 계정 user@example.com 으로 파일 budget-2027.xlsx 에 대한 `DOWNLOAD` 이벤트가 기록되어 있다(만든 예시)" 처럼 기록으로 확인되는 만큼만 씁니다. 쓰는 방법은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 참고 문헌

1. Dropbox, "team_log.stone", dropbox-api-spec. https://github.com/dropbox/dropbox-api-spec/blob/master/team_log.stone
2. Dropbox, "common.stone" (`DropboxTimestamp`), dropbox-api-spec. https://github.com/dropbox/dropbox-api-spec/blob/master/common.stone
3. Dropbox Help Center, "How to recover deleted files and folders". https://help.dropbox.com/delete-restore/recover-deleted-files-folders
4. Dropbox, "Our Guiding Principles", Transparency. https://www.dropbox.com/transparency/principles
5. Box Developer, "Enterprise events". https://developer.box.com/guides/events/enterprise-events/for-enterprise/
6. Box Developer, "Event" resource. https://developer.box.com/reference/resources/event/
7. Box Developer, "List user and enterprise events" (GET /events). https://developer.box.com/reference/get-events/
8. Box Developer, "Event triggers". https://developer.box.com/guides/events/event-triggers/
9. Frank Breitinger, Xiaolu Zhang, Darren Quick, "A forensic analysis of rclone and rclone's prospects for digital forensic investigations of cloud storage", Forensic Science International: Digital Investigation 43 (2022) 301443. https://doi.org/10.1016/j.fsidi.2022.301443
10. Jihyeok Yang, Jieon Kim, Jewan Bang, Sangjin Lee, Jungheum Park, "CATCH: Cloud Data Acquisition through Comprehensive and Hybrid Approaches", Forensic Science International: Digital Investigation 43 (2022) 301442. https://doi.org/10.1016/j.fsidi.2022.301442
11. Uk Hur, Soojin Kang, Giyoon Kim, Jongsung Kim, "A study on cloud data access through browser credential migration in Windows environment", Forensic Science International: Digital Investigation 45 (2023) 301568. https://doi.org/10.1016/j.fsidi.2023.301568
