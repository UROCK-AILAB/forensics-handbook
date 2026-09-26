---
title: "Zoom 기록"
parent: "아티팩트 · 업무용 SaaS"
nav_order: 600
---

# Zoom 기록 (Zoom)

Zoom 계정의 로그인·관리 작업·회의 참가·클라우드 녹화 기록은 감사 로그 한 곳에 모이지 않고 보고서(Reports)·대시보드(Dashboard)·클라우드 녹화 API 에 나뉘어 남습니다.

## 무엇을 기록하나 · 왜 생기나

Zoom 은 계정 관리자가 사용량과 보안을 살피도록 웹 포털과 REST API 로 여러 보고서를 내줍니다. 조사에 쓰는 기록은 다섯 갈래입니다. 로그인·로그아웃 보고서는 누가 언제 어느 IP 와 클라이언트로 들어왔는지를, 운영 로그(Operation Logs)는 사용자 추가·계정 설정 변경·녹화 삭제 같은 관리자와 사용자의 작업을 남깁니다[1]. 회의 참가자 보고서와 대시보드는 회의마다 누가 언제 들어오고 나갔는지를 남기고, 대시보드에는 참가자의 기기·IP·PC 이름까지 들어 있습니다[1][2]. 회의 활동 로그(meeting audit trail)는 회의 생성·시작·참가·퇴장·원격 제어·회의 중 채팅을 남기지만, 계정에서 Zoom 지원팀에 요청해 켜야 생깁니다[1]. 클라우드 녹화 API 는 녹화 파일이 언제 만들어졌고 언제 휴지통으로 갔는지를 알려 줍니다[1].

## 위치와 버전별 차이

모든 기록은 Zoom 서버에 있고 `https://api.zoom.us/v2` 아래 REST API 로 받습니다[1][2]. 요금제와 조회 기간 한도가 기록마다 다릅니다.

| 기록 | API | 요금제·조건 | 조회 기간 | 근거 |
|---|---|---|---|---|
| 로그인·로그아웃 보고서 | `GET /report/activities` | Pro 이상 | 최근 6개월 안, 한 번에 한 달 | [1] |
| 운영 로그 | `GET /report/operationlogs` | Pro 이상 | 한 번에 한 달(보관 기간 표기 없음) | [1] |
| 회의 참가자 보고서 | `GET /report/meetings/{meetingId}/participants` | Pro 이상, 두 명 이상 회의 | 표기 없음 | [1] |
| 지난 회의 참가자 | `GET /past_meetings/{meetingId}/participants` | Pro 이상 | 최근 15개월 | [1] |
| 지난 회의 회차 목록 | `GET /past_meetings/{meetingId}/instances` | 끝난 회의만 | 최근 15개월 | [1] |
| 회의 활동 로그 | `GET /report/meeting_activities` | Zoom 지원팀이 기능을 켜야 함 | 한 번에 한 달 | [1] |
| 대시보드 회의 참가자 | `GET /metrics/meetings/{meetingId}/participants` | Business 이상 | 최근 6개월 안, 월 단위 | [2] |
| 클라우드 녹화 목록 | `GET /users/{userId}/recordings` | Pro 이상, 클라우드 녹화 켜짐 | 한 번에 최대 한 달 | [1] |
| 클라우드 녹화 사용량 | `GET /report/cloud_recording` | Pro 이상 | 최근 6개월, 어제까지, 30일 이하 | [1] |

2026년 9월 API Hub 명세 기준입니다. 보고서 API 는 `report:read:admin` 범위(scope)를 쓰고, 지난 회의 API 는 `meeting:read:admin` 또는 `meeting:read`, 대시보드 API 는 `dashboard_meetings:read:admin` 또는 `dashboard:read:admin`, 녹화 목록은 `recording:read:admin` 또는 `recording:read` 를 씁니다[1][2]. 조회 기간 한도를 넘긴 기록은 API 로 다시 받을 수 없으므로, 사건을 알게 되면 먼저 받아 두는 편이 안전합니다. 보존 순서는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)에, 요금제에 따른 차이의 일반론은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md)에 있습니다.

## 구조

응답은 모두 JSON 이고, 결과가 많으면 `next_page_token` 으로 다음 쪽을 받습니다. 이 토큰은 15분 뒤 만료됩니다[1].

**로그인·로그아웃 보고서** 응답의 `activity_logs[]` 에는 `email`, `time`, `type`, `ip_address`, `client_type`, `version` 이 있습니다[1]. `type` 은 `Sign in` 또는 `Sign out` 이고, `version` 은 Zoom 클라이언트 버전입니다[1].

```json
{
  "from": "2026-08-01T00:00:00Z",
  "to": "2026-08-31T00:00:00Z",
  "activity_logs": [
    {
      "email": "kim@contoso.com",
      "time": "2026-08-14T01:22:05Z",
      "type": "Sign in",
      "ip_address": "203.0.113.24",
      "client_type": "Browser",
      "version": "6.1.0.1234"
    }
  ]
}
```
(만든 예시)

**운영 로그** 응답의 `operation_logs[]` 에는 `time`, `operator`(작업한 사용자), `category_type`, `action`, `operation_detail` 이 있습니다[1]. `category_type` 으로 거를 수 있는 값은 `all`, `user`, `user_settings`, `account`, `billing`, `im`, `recording`, `phone_contacts`, `webinar`, `sub_account`, `role`, `zoom_rooms` 입니다[1]. `operation_detail` 은 사람이 읽는 문장이라 대상 사용자·녹화 이름이 이 안에 들어갑니다.

```json
{ "time": "2026-08-14T02:03:11Z", "operator": "admin@contoso.com",
  "category_type": "recording", "action": "delete",
  "operation_detail": "delete recording - Weekly sync" }
```
(만든 예시)

**회의 참가자 보고서**의 `participants[]` 에는 `id`, `user_id`, `participant_user_id`, `name`, `user_email`, `join_time`, `leave_time`, `duration`, `status`, `failover`, `customer_key`, `bo_mtg_id`(소회의실 ID)가 있고, `include_fields=registrant_id` 를 주면 `registrant_id` 가 붙습니다[1]. `id` 와 `participant_user_id` 는 Zoom 에 로그인해 들어온 참가자라면 그 사용자의 ID 와 같습니다[1]. `user_id` 는 그 회의 안에서만 쓰는 참가자 번호입니다[1]. `status` 는 `in_meeting` 또는 `in_waiting_room` 입니다[1]. 지난 회의 참가자 API 도 거의 같은 모양이고, 내부 사용자인지 알려 주는 `internal_user` 가 더 있습니다[1].

**대시보드 회의 참가자**에는 참가자가 쓴 단말 정보가 들어 있습니다. `ip_address`, `internal_ip_addresses`, `location`, `device`(`Phone`, `H.323/SIP`, `Windows`, `Mac`, `iOS`, `Android` 등), `os`, `os_version`, `pc_name`, `mac_addr`, `harddisk_id`, `domain`(PC 도메인), `network_type`, `connection_type`, `data_center`, `version`, `client`, `browser_name`, `role`(`host`·`attendee`), `leave_reason`, `recording`, `share_desktop`, `share_application`, `share_whiteboard`, `camera`, `microphone`, `speaker`, `participant_uuid` 가 대표 필드입니다[2]. `leave_reason` 에는 `$name left the meeting.`, `$name got disconnected from the meeting.`, `Host ended the meeting.`, `Removed by host.` 같은 문장이 들어갑니다[2]. `type` 인자는 `past`·`pastOne`·`live` 중 하나이고, 주지 않으면 `live` 라서 진행 중인 회의만 나옵니다[2].

**회의 활동 로그**의 `meeting_activity_logs[]` 에는 `meeting_number`, `activity_time`, `operator`(표시 이름), `operator_email`, `activity_category`, `activity_detail` 이 있습니다[1]. 활동 종류는 0 회의 생성, 1 회의 시작, 2 참가, 3 퇴장, 4 원격 제어(Remote control), 5 회의 중 채팅(In-meeting chat), 9 회의 종료이고, -1 은 전체입니다[1].

**클라우드 녹화 목록**의 `meetings[]` 에는 회의 `uuid`, `id`, `topic`, `start_time`, `host_id`, `auto_delete`, `auto_delete_date` 가 있고, 그 아래 `recording_files[]` 에 `recording_start`, `recording_end`, `file_type`, `file_size`, `recording_type`, `download_url`, `play_url`, `status` 가 있습니다[1]. `file_type` 이 `CHAT` 이면 회의 중 채팅을 담은 TXT, `TRANSCRIPT` 면 VTT 전사본, `CSV` 면 투표 결과입니다[1]. `trash=true` 로 휴지통을 조회하면 파일마다 `deleted_time` 이 붙습니다[1].

## 증거로서 의미

**증명하는 것**

- 이 Zoom 계정으로 이 시각에 이 IP·클라이언트 종류·버전에서 로그인하거나 로그아웃한 기록이 있다[1].
- 이 운영자 계정이 이 시각에 사용자·설정·녹화에 대해 이런 작업을 한 기록이 있다[1].
- 이 참가자 줄이 이 회의에 이 시각에 들어와 이 시각에 나갔다. 대시보드라면 이 기기·IP·PC 이름·PC 도메인으로 들어왔고, 나간 이유는 이것이다[2].
- 이 참가자가 화면 공유를 썼고, 회의 안에서 녹화 기능이 쓰였다(`share_desktop`, `recording`)[2].
- 녹화 파일이 이 시각 범위로 만들어졌고, 이 시각에 휴지통으로 옮겨졌다[1].

**증명하지 못하는 것**

- 회의에서 오간 말과 화면 내용. 녹화·전사본·채팅 파일이 남아 있을 때만 따로 확인할 수 있습니다.
- 참가자의 실제 신원. `name`·`user_name` 은 표시 이름이라 참가자가 정할 수 있고, 로그인하지 않고 들어온 참가자는 `id` 가 비어 있습니다[1][2].
- 참가자의 실제 위치. `location` 은 IP 로 정한 위치일 가능성이 있습니다. 해석 방법은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md)에 있습니다.
- 내려받은 녹화 파일이 그 뒤 어디로 갔는지.
- 외부 참가자에 대한 자세한 정보. 호스트 계정 밖 사용자는 메일이 빈 문자열로 오고(예외 규칙 있음), `camera`·`microphone`·`speaker`·`mac_addr`·`harddisk_id`·`domain` 도 빈 문자열로 옵니다[1][2].

보고서에는 "2026-08-14 01:22:05 UTC 에 kim@contoso.com 계정으로 203.0.113.24 에서 브라우저로 Zoom 에 로그인한 기록이 있다"처럼 기록이 말하는 만큼만 씁니다(만든 예시).

## 시각 해석

로그인 보고서·운영 로그·참가자 보고서·대시보드의 시각과 녹화 목록의 `start_time` 은 date-time 형식이고 명세 예시는 `2022-03-23T06:58:09Z` 처럼 끝에 `Z` 가 붙은 UTC 입니다[1][2]. 녹화 파일의 `recording_start`·`recording_end`·`deleted_time` 은 형식 표시가 없는 문자열이지만 명세 예시는 `2021-03-18T05:41:36Z` 로 모양이 같습니다[1]. 녹화 목록의 `from`·`to` 는 UTC 날짜('yyyy-mm-dd')이고, 운영 로그의 `from`·`to` 는 'yyyy-MM-dd HH:mm' 처럼 분까지 줄 수 있습니다[1].

회의 활동 로그의 `activity_time` 은 명세 예시가 `2024-03-21 07:09:03:216` 으로 시간대 표시가 없고 밀리초가 콜론 뒤에 붙습니다[1]. 이 값은 같은 회의의 참가자 보고서 `join_time` 과 맞춰 보고 어느 시간대인지 정합니다. 클라우드 녹화의 `TIMELINE` 파일 시각은 호스트가 Zoom 프로필에 정한 시간대로 표시됩니다[1].

참가자 `duration` 은 `leave_time` 에서 `join_time` 을 뺀 초입니다[1]. 참가자가 나갔다가 다시 들어오면 새 `user_id` 로 줄이 따로 생기므로, 한 사람이 회의에 머문 시간은 같은 사람의 줄을 모두 모아 더합니다[1][2]. 참가자가 수백 명인 회의는 집계가 늦어 `duration` 이 0 으로 올 수 있으니 잠시 뒤 다시 받습니다[1]. UTC 와 현지 시각을 섞을 때의 원칙은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 있습니다.

## 함정과 한계

- **회의 ID 만 주면 가장 최근 회차만 나옵니다.** 반복 회의는 `/past_meetings/{meetingId}/instances` 로 회차별 UUID 를 먼저 받고, UUID 로 참가자를 조회합니다[1]. UUID 가 `/` 로 시작하거나 `//` 를 품으면 두 번 URL 인코딩해야 합니다[1].
- **한 명 회의는 기본으로 빠집니다.** 지난 회의 참가자 API 는 계정 설정 "Show one person meetings and webinars on Dashboard and Reports" 가 켜져 있어야 한 명 회의를 돌려주고, 참가자 보고서는 두 명 이상 회의만 다룹니다[1]. 한 명 회의는 대시보드 API 의 `type=pastOne` 으로 봅니다[2].
- **회의 활동 로그가 없으면 기능이 꺼져 있었을 가능성부터 봅니다.** 이 로그는 지원팀이 켜야 생기므로, 없다는 사실만으로 채팅·원격 제어가 없었다고 말할 수 없습니다[1].
- **조회 기간 한도가 서로 다릅니다.** 로그인 보고서와 대시보드는 최근 6개월, 지난 회의 참가자는 최근 15개월입니다[1][2]. 사건 시점에 따라 어떤 기록은 이미 받을 수 없습니다.
- **레거시 HIPAA BAA 계정은 값이 비어 올 수 있습니다.** 참가자 보고서와 대시보드는 이런 계정에서 `user_name`·`ip_address`·`location`·`email` 을 비워 돌려줄 수 있습니다[1][2].
- **IP 는 대시보드에서 봅니다.** 참가자 보고서 API 설명은 `ip_address`·`location` 이 비어 올 수 있다고 적지만 응답 필드 목록에는 이 필드가 없고, 대시보드 응답에만 있습니다[1][2].
- **녹화 휴지통 조회는 날짜로 거를 수 없습니다.** `trash=true` 일 때 `from`·`to` 를 쓰지 않습니다[1].
- **로그인 IP·기기가 낯설어도 비밀번호를 입력했다는 뜻은 아닙니다.** Windows 브라우저에 저장된 자동 로그인 자격 증명을 다른 PC 로 옮기면 비밀번호를 넣지 않고 zoom.us 에 로그인할 수 있습니다(논문이 시험한 브라우저와 사이트 조건)[3]. 로그인 방식은 SSO 를 쓰는 계정이라면 [Okta 시스템 로그](okta.md)나 [페더레이션과 SSO](../../01-foundations/identity/federation-sso.md)의 기록과 함께 봅니다.

## 직접 분석해 보기

**원본 JSON 으로 한 번.** API 로 받은 로그인 보고서 JSON 을 그대로 보관하고, 사본에서 필요한 필드만 뽑습니다. 아래는 `jq` 로 한 줄에 한 이벤트씩 시각·계정·IP·클라이언트를 뽑는 예입니다.

```bash
jq -r '.activity_logs[] | [.time, .email, .type, .ip_address, .client_type, .version] | @tsv' activities_2026-08.json | sort
```

같은 방법으로 운영 로그는 `.operation_logs[] | [.time, .operator, .category_type, .action, .operation_detail]` 을, 대시보드 참가자는 `.participants[] | [.join_time, .leave_time, .user_name, .email, .ip_address, .pc_name, .device, .leave_reason]` 을 뽑습니다. 원본 파일의 해시를 먼저 남겨 두면 뒤에 사본과 대조할 수 있습니다.

**공식 API 로 한 번.** Zoom 이 공개한 REST API 가 이 기록을 받는 표준 도구입니다. 받는 순서는 다음과 같습니다.

1. `report:read:admin`(지난 회의는 `meeting:read:admin`, 대시보드는 `dashboard:read:admin`, 녹화는 `recording:read:admin`) 범위가 있는 관리자 앱으로 접근합니다[1][2].
2. `GET /report/activities?from=2026-08-01&to=2026-08-31` 처럼 한 달씩 나눠 로그인 보고서를 받고, `next_page_token` 이 빌 때까지 이어 받습니다[1].
3. 운영 로그는 `category_type=all` 로 같은 방식으로 받습니다[1].
4. 관심 회의는 `/past_meetings/{meetingId}/instances` 로 회차 UUID 를 모은 뒤, 회차마다 참가자 보고서와 대시보드(`type=past`)를 받습니다[1][2].
5. 관련 사용자의 녹화 목록을 한 달씩, 그리고 `trash=true` 로 한 번 더 받습니다[1].

웹 포털의 Reports·Dashboard 화면에서도 같은 내용을 볼 수 있지만, 사건 기록으로 남기려면 API 응답 원본을 보관하는 편이 낫습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 보는 것 |
|---|---|
| [Okta 시스템 로그](okta.md) | SSO 로 Zoom 에 들어왔다면 같은 시각의 인증 기록과 IP |
| [Slack 감사 로그](slack.md) | 회의 링크를 주고받은 시각과 회의 참가 시각 |
| [Dropbox·Box 기록](dropbox-box.md) | 녹화 파일을 내려받은 뒤 다른 저장소로 올렸는지 |
| 단말의 Zoom 클라이언트 흔적 | 대시보드 `pc_name`·`mac_addr` 가 가리키는 PC 에서 클라이언트를 실행한 흔적 |
| [이상한 로그인 가려내기](../../03-techniques/analysis/suspicious-sign-ins.md) | 로그인 보고서의 낯선 IP·클라이언트 버전 |

여러 서비스의 시각을 한 줄로 늘어놓는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다. API 로 받을 수 없는 기간의 기록은 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)을 검토합니다.

## 실습

아래 질문은 이 쪽의 만든 예시 레코드와 Zoom 개발자 계정의 시험 계정으로 풀어 봅니다.

1. 위 로그인 보고서 예시에서 로그인 시각을 한국 시각으로 바꾸면 몇 시입니까?
2. 같은 참가자가 회의에서 세 번 끊겼다 다시 들어왔습니다. 참가자 보고서에 줄이 몇 개 생기고, 머문 시간은 어떻게 계산합니까?
3. 운영 로그에 `category_type` 이 `recording`, `action` 이 `delete` 인 줄이 있습니다. 녹화 목록에서 무엇을 조회해 삭제 대상과 시각을 맞춰 봅니까?
4. 회의 활동 로그가 비어 있습니다. 채팅이 없었다고 쓰기 전에 무엇을 확인합니까?
5. 대시보드에서 외부 참가자의 `mac_addr` 가 비어 있습니다. 이것만으로 어떤 결론을 내릴 수 있습니까?

## 참고 문헌

1. Zoom, "Meetings API" OpenAPI 3.0 명세(API Hub, 2026년 9월 기준), https://developers.zoom.us/api-hub/meetings/methods/endpoints.json
2. Zoom, "Accounts API" OpenAPI 3.0 명세(API Hub, 2026년 9월 기준), https://developers.zoom.us/api-hub/accounts/methods/endpoints.json
3. Uk Hur, Soojin Kang, Giyoon Kim, Jongsung Kim, "A study on cloud data access through browser credential migration in Windows environment", Forensic Science International: Digital Investigation 45 (2023) 301568 (DFRWS USA 2023). https://doi.org/10.1016/j.fsidi.2023.301568
