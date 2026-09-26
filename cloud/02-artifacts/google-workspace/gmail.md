---
title: "Gmail 기록과 메일 검색"
parent: "아티팩트 · Google Workspace"
nav_order: 320
---

# Gmail 기록과 메일 검색 (Gmail Log Search)

Google Workspace 의 메일 흔적은 Gmail 로그 이벤트(Gmail log events), BigQuery 로 내보낸 Gmail 로그, 이메일 로그 검색(Email Log Search, ELS) 세 곳에 남고, 셋은 보관 기간·에디션·필드가 서로 달라서 어느 것을 보았는지 먼저 밝혀야 합니다.

## 무엇을 기록하나 · 왜 생기나

Gmail 로그 이벤트는 메일 한 통이 전달되는 단계와 전달된 뒤 사용자가 한 동작을 기록합니다. 보내기·받기·스팸 판정·격리처럼 전달 과정에서 생기는 일뿐만 아니라 처음 열람, 답장, 전달, 휴지통으로 옮김, 영구 삭제, 본문 링크 클릭, 첨부 다운로드까지 다룹니다[1][4]. 관리자는 이 기록으로 메일이 스팸으로 분류된 때, 격리에서 풀린 때 같은 사용자·관리자 활동을 보고, 보안 조사 도구에서 메시지 삭제·격리 같은 조치를 이어서 할 수 있습니다[3].

ELS 는 메일이 왜 제대로 전달되지 않았는지 찾으려고 만든 기능입니다. 발신자·수신자·날짜·Message ID 로 메시지를 찾고, 수신자마다 전달 단계와 전달 뒤 상태(라벨, 위치, 스팸 표시, 삭제 여부)를 보여 줍니다[5][6]. 세 원천 모두 메일 본문은 보여 주지 않습니다. ELS 는 메시지 내용을 볼 수 없고, 내용이 필요하면 규정 준수 규칙·위임·Vault 를 써야 합니다[5]. 보안 조사 도구는 권한과 에디션이 맞으면 메일 내용을 볼 수 있지만, 이 기능은 로그가 아니라 메일함을 들여다보는 기능입니다[3]. 내용 보존은 [Vault와 Takeout](vault-takeout.md) 에서 다룹니다.

## 위치와 버전별 차이

세 원천의 차이를 표로 정리합니다(2026년 9월 문서 기준).

| 원천 | 보는 곳 | 보관 | 들어오기까지 | 에디션·권한 |
|---|---|---|---|---|
| Gmail 로그 이벤트 | 관리 콘솔 Reporting > Audit and investigation > Gmail log events, Security > Security center > Investigation tool, 보고서 API `applicationName=gmail` | 6개월[7] | 몇 분[7] | 감사 및 조사 페이지는 Audit & Investigation 관리자 권한, 보안 조사 도구는 Frontline Standard·Plus, Enterprise Standard·Plus, Education Standard·Plus, Enterprise Essentials Plus, Cloud Identity Premium 과 Security center 관리자 권한[3] |
| BigQuery 내보내기 | 설정한 BigQuery 데이터세트의 `activity_` 표 | 켤 때 과거 활동 자료 180일을 넣어 줌. 표 만료는 아래 설명 참고[9] | 10분 안[9] | Frontline Standard·Plus, Enterprise Standard·Plus, Education Standard·Plus, Enterprise Essentials Plus[8][9] |
| Email Log Search | 관리 콘솔 Reporting > Email Log Search | 30일[7] | - | Frontline Starter·Standard·Plus, Business Starter·Standard·Plus, Enterprise Standard·Plus, Education Fundamentals·Standard·Plus, Nonprofits, G Suite Basic·Business 와 Gmail Settings 관리자 권한[5] |

BigQuery 표의 보관은 설정 문서 안에서도 두 가지로 적혀 있습니다. 표가 자동으로 지워지지 않는다는 문장과, 내보낸 자료의 만료가 기본 60일이라 60일 뒤 Google Cloud 에서 지워진다는 문장이 함께 있습니다[9]. 그래서 BigQuery 에 오래된 Gmail 기록이 있다고 기대하지 말고, 데이터세트와 표의 만료 설정을 BigQuery 콘솔에서 먼저 확인합니다.

ELS 는 BigQuery 내보내기에 들어 있지 않은 별도 기능입니다[8]. 관리자는 로그 이벤트를 지우거나 보관 기간을 바꿀 수 없습니다[7]. Gmail 로그 이벤트는 Google Cloud 의 Cloud Logging 으로 공유되는 로그 목록에 없으므로, Cloud Logging 에서 Gmail 기록을 찾을 수는 없습니다[15]. 다른 Workspace 로그와 견준 보관 기간은 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 에 모아 두었습니다.

보고서 API 로 Gmail 활동을 부를 때는 `startTime` 과 `endTime` 을 둘 다 주어야 하고, 두 값의 차이가 30일을 넘으면 안 됩니다[1][2]. 6개월 보관분을 모두 받으려면 30일 이하 구간으로 나눠 여러 번 요청합니다. 보고서 API 의 공통 요청 방식·레코드 구조는 [관리 콘솔 감사 로그](admin-audit.md) 에 적었습니다.

## 구조

### Gmail 로그 이벤트

보고서 API 에서 Gmail 이벤트의 `type` 은 늘 `delivery_type`, `name` 은 늘 `delivery` 입니다[1]. 이벤트 이름으로는 종류를 가를 수 없어서, 매개변수 `event_info` 안의 정수 `event_info.mail_event_type` 으로 무슨 일이 있었는지 판단합니다[1]. 값은 다음과 같습니다[1][4].

| 값 | 뜻 | 값 | 뜻 |
|---|---|---|---|
| 0 | 전달 중간 단계(보안 조사 도구에 안 보임, `message_info.action_type` 참고) | 18 | 첨부를 Drive 에 저장 |
| 1 | 보냄 | 19 | 메일 속 Drive 항목을 받은 사람의 Drive 에 저장 |
| 2 | 받음 | 20~22 | 메시지 분류 라벨 붙임·바꿈·뗌 |
| 3 | 사용자가 스팸·피싱·스팸 아님으로 직접 분류 | 23~25 | 모든 첨부의 분류 라벨 붙임·바꿈·뗌 |
| 4 | 전달 뒤 Gmail 이 스팸으로 판정 | 26 | 보관처리(archive) |
| 5 | 격리 | 27 | 영구 삭제 |
| 6 | 격리 해제 | 28 | 첨부 미리보기 |
| 7 | 처음 열람 | 29 | 임시 저장 |
| 8 | 읽지 않음으로 표시 | 30 | 전달 실패로 반송 |
| 9 | 처음 답장 | 31 | 열람(처음과 그 뒤 열람 모두) |
| 10 | 처음 전달 | 32 | 메시지 다운로드 |
| 11 | Gmail 계정 전달 설정으로 자동 전달 | 33 | 앱이 사용자 대신 메시지에 접근 |
| 12 | 받은편지함으로 옮김 | 34 | 수신 속도 제한으로 거부·지연 |
| 13 | 휴지통으로 옮김 | 35 | 사용자나 API 가 발송을 시작 |
| 14 | 휴지통에서 꺼냄 | | |
| 15 | 본문 링크 클릭 | | |
| 16 | 첨부 미리보기 중 링크 클릭 | | |
| 17 | 첨부 다운로드 | | |

관리 콘솔과 보안 조사 도구에서는 같은 기록을 속성(attribute)으로 거릅니다[3]. 조사에 자주 쓰는 속성은 Event(Send, View, Link click, Attachment download 같은 동작), Owner(받은 메일은 수신자, 보낸 메일은 발신자), From (Envelope)·From (Header address)·From (Header name), To (Envelope), Subject, Message ID, IP address(메일을 시작했거나 메일과 상호작용한 클라이언트의 IP), Client Type(Web, Android, iOS, POP3 등), Delegate·Has delegate(소유자 대신 동작한 위임 사용자), Actor application info(앱 이름·OAuth 클라이언트 ID·Impersonation), OAuth project ID, Attachment name·Attachment hash(SHA256), Target link URL·Target attachment hash·Target drive ID(사용자가 누른 링크·첨부·Drive 항목), Geo location(릴레이 IP 기준 국가 코드), SPF domain·DKIM domain, Traffic source(내부·외부)입니다[3].

보고서 API 레코드의 공통 필드 `resourceDetails[].id` 는 메일일 때 `"gaia_id/rfc2822_message_id"` 모양입니다[2]. 아래는 명세의 필드 모양을 따라 만든 예시이고, 값은 모두 지어낸 것입니다.

```json
{
  "kind": "audit#activity",
  "id": {
    "time": "2025-09-26T09:35:12.000Z",
    "uniqueQualifier": "-1234567890123456789",
    "applicationName": "gmail",
    "customerId": "C03az79cb"
  },
  "actor": { "callerType": "USER", "email": "user@example.com" },
  "ipAddress": "203.0.113.25",
  "events": [
    {
      "type": "delivery_type",
      "name": "delivery",
      "parameters": [
        {
          "name": "event_info",
          "messageValue": {
            "parameter": [ { "name": "mail_event_type", "intValue": "17" } ]
          }
        }
      ]
    }
  ]
}
```

이 예시는 `user@example.com` 계정이 203.0.113.25 에서 어떤 메일의 첨부를 받은(17) 기록으로 읽습니다. 어떤 메일이었는지는 같은 레코드의 메시지 정보나 `resourceDetails` 로 확인합니다. 보고서 API 에서 Gmail 매개변수로 정의된 것은 `event_info` 뿐이라서, 메시지 쪽 하위 필드 이름은 실제 레코드에서 확인합니다[1].

### BigQuery Gmail 스키마

BigQuery 로 내보낸 Gmail 로그에는 보고서 API 보다 필드가 훨씬 많고, 필드마다 설명이 공개되어 있습니다[4]. 크게 이벤트 정보(`event_info`)와 메시지 정보(`message_info`)로 나뉩니다.

| 필드 | 내용 |
|---|---|
| `event_info.timestamp_usec` | 이벤트가 시작된 시각, 마이크로초 단위 UNIX 시각(필수) |
| `event_info.elapsed_time_usec` | 이벤트에 걸린 시간(마이크로초) |
| `event_info.success` | 성공 여부. 정책이 메시지를 거부하면 false |
| `event_info.mail_event_type` | 위 표의 이벤트 종류 |
| `event_info.client_context.client_type` | WEB, IOS, ANDROID, IMAP, POP3, API |
| `event_info.client_context.session_context.delegate_user_email` | 소유자 대신 동작한 위임 사용자 |
| `message_info.rfc2822_message_id` | 메일 머리글의 Message-ID |
| `message_info.subject` | 제목. 로그가 길거나 걸린 규칙이 많으면 잘릴 수 있음 |
| `message_info.source.address`·`from_header_address`·`from_header_displayname` | 봉투 발신자, 머리글 From 주소·표시 이름 |
| `message_info.source.service`·`selector` | 메일을 만든 서비스(예: `gmail-ui`·`send` 는 Gmail 웹에서 보냄, `gmail-ui`·`autoforward` 는 자동 전달, `google-apps-script`·`user` 는 Apps Script) |
| `message_info.destination.address`·`service`·`selector` | 수신자와 도착한 서비스(수신자마다 반복) |
| `message_info.flattened_destinations` | 모든 수신자를 `service:selector:address` 로 이어 붙인 문자열 |
| `message_info.attachment.file_name`·`file_extension_type`·`sha256`·`malware_family` | 첨부 이름·확장자·SHA256·악성코드 분류 |
| `message_info.connection_info.client_ip` | 메일을 시작한 메일 클라이언트의 IP |
| `message_info.connection_info.smtp_in_connect_ip`·`smtp_out_connect_ip`·`smtp_out_remote_host` | 들어온 SMTP 연결의 원격 IP, 내보낸 SMTP 연결의 원격 IP, 내보낸 연결의 목적지 도메인이나 스마트호스트 |
| `message_info.connection_info.spf_pass`·`dkim_pass`·`dmarc_pass` | 발신자 인증 결과 |
| `message_info.connection_info.ip_geo_country`·`ip_geo_city` | 릴레이 IP 기준 국가 코드·가까운 도시 |
| `message_info.connection_info.is_internal`·`is_intra_domain` | 고객 도메인 안·같은 도메인 안에서 오간 메일인지 |
| `message_info.action_type` | 전달 단계(아래 설명) |
| `message_info.post_delivery_info.action_type` | 전달 뒤 사용자 동작(`action_type` 이 71 일 때만) |
| `message_info.post_delivery_info.interaction.link_url`·`drive_id`·`attachment.*` | 누른 링크, 다룬 Drive 항목, 받은 첨부 |
| `message_info.spam_info.disposition`·`classification_timestamp_usec` | 스팸 판정 결과와 판정 시각 |
| `message_info.triggered_rule_info.*` | 걸린 정책 규칙(규칙 이름, 적용된 조치 등) |
| `message_info.confidential_mode_info.is_confidential_mode` | 비밀 모드로 보낸 메일인지 |
| `message_info.description` | 메시지에 일어난 일을 사람이 읽게 적은 설명 |

`message_info.action_type` 은 전달 단계를 숫자로 적습니다. 1 은 인바운드 SMTP 서버가 받음, 2 는 Gmail 이 받아 전달을 준비함(거부 정책을 여기서 평가), 3 은 Gmail 이 메일함에 넣거나 다른 서버로 보냄, 10 은 아웃바운드 SMTP 서버로 내보냄, 14 는 일시 오류로 재시도 예정, 18 은 반송, 19 는 Gmail 이 버림(관리 격리 등), 69 는 사용자가 스팸 분류를 바꿈, 70 은 전달 뒤 스팸·피싱으로 재분류, 71 은 전달 뒤 사용자가 메일함에서 한 동작입니다[4]. 45·46·51·54 는 Google 그룹스 처리 단계이고, 48·49 는 SMTP 릴레이입니다[4].

## 증거로서 의미

**증명하는 것.** Message-ID 로 가리킨 메시지가 언제 어느 발신자에게서 어느 수신자에게 전달되었는지, 전달 단계에서 반송·격리·스팸 판정이 있었는지를 보여 줍니다[4][6]. 전달된 뒤 그 계정에서 열람·답장·전달·휴지통 이동·영구 삭제·링크 클릭·첨부 다운로드 같은 동작이 있었는지, 그 동작이 어느 클라이언트 종류와 IP 에서, 위임 사용자나 앱을 거쳐 일어났는지도 보여 줍니다[1][3][4]. 첨부의 SHA256 은 다른 곳에서 찾은 파일과 같은 파일인지 비교하는 데 씁니다[3][4].

**증명하지 못하는 것.** 메일 본문은 세 원천 어디에도 없습니다[5]. 열람 이벤트로는 메시지를 열었다는 것까지만 알 수 있고, 그 사람이 내용을 읽고 이해했는지는 알 수 없습니다. 기록된 계정으로 동작했다는 것이지 그 계정을 누가 쥐고 있었는지는 알려 주지 않습니다. `mail_event_type` 32(다운로드)는 Thunderbird 같은 POP3 클라이언트의 다운로드만 뜻하고, Gmail 웹의 "Download message" 나 "Show Original" 로 받은 것은 여기에 들어가지 않습니다[4]. 그래서 32 가 없다고 메시지를 파일로 받지 않았다고 쓸 수는 없습니다. 6개월이 지난 Gmail 로그 이벤트와 30일이 지난 ELS 전달 단계는 남아 있지 않습니다[5][7].

## 시각 해석

| 원천 | 시각 필드 | 형식·시간대 |
|---|---|---|
| 보고서 API | `id.time` | 필드 설명과 문서 예시의 형식이 다르므로 실제 로그의 값 모양으로 판단(자세한 내용은 [관리 콘솔 감사 로그](admin-audit.md)) |
| BigQuery | `event_info.timestamp_usec` | 이벤트가 시작된 시각, 마이크로초 UNIX 시각(UTC 기준 초)[4] |
| BigQuery | `message_info.spam_info.classification_timestamp_usec` | 스팸으로 분류된 시각[4] |
| 감사 및 조사 페이지·보안 조사 도구 | Date | 브라우저의 기본 시간대로 표시. 보안 조사 도구는 최고 관리자가 조사 시간대를 바꿀 수 있고, 그 시간대가 검색 조건과 결과에 함께 적용됨[3] |
| ELS | 요약의 Date | 발송으로 보고된 시각, 또는 그 메시지의 첫 로그 줄이 생긴 시각[6] |
| ELS | 수신자별 전달 단계 시각 | 검색에 쓴 관리 콘솔 기기의 시간대[6] |

BigQuery 표의 하루 파티션(`_PARTITIONTIME`)은 활동 표의 `time_usec` 에서 나오지만, 경계를 UTC 가 아닌 태평양 시간(PT)에 맞춥니다[9]. 한국 시간 기준 하루를 뽑으려고 파티션 하나만 고르면 앞뒤 기록이 빠지므로, 파티션 조건은 넉넉히 주고 `time_usec` 로 다시 거릅니다. ELS 화면 시각은 검색한 사람의 기기 시간대를 따르므로, 캡처나 내보낸 파일을 보고서에 옮길 때는 검색한 기기의 시간대를 함께 적습니다. 여러 원천의 시각을 한 줄로 맞추는 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 에 있습니다.

## 함정과 한계

보안 조사 도구에서는 휴지통에서 아직 지워지지 않은 메시지의 데이터만 검색할 수 있습니다[3]. 사용자가 휴지통까지 비운 메일을 찾을 때는 보안 조사 도구 검색 결과가 비었다고 기록이 없다고 판단하지 말고, 보고서 API·BigQuery 의 `mail_event_type` 27(영구 삭제)을 따로 찾습니다.

사용자 이름을 바꾸면 옛 이름으로는 검색 결과가 나오지 않습니다[3]. 조사 대상 계정의 이름이 바뀐 적이 있으면 [관리 콘솔 감사 로그](admin-audit.md) 에서 `RENAME_USER` 를 먼저 확인합니다.

ELS 는 한 번에 메시지 1,000개, 메시지마다 로그 줄 15,000개까지만 가져옵니다[5]. 메시지 하나는 수신자마다 보통 로그 줄이 5~7개라서 큰 그룹에 보낸 메일은 한도를 넘을 수 있습니다[5]. 결과는 1분에서 1시간까지 걸립니다[5]. 30일보다 오래된 메시지는 그룹 주소로 검색할 수 없고, 수신자 주소와 Message ID 를 둘 다 넣어야 하며, 전달 상태 없이 전달 뒤 상태만 나옵니다[5]. Message ID 로 검색하면 고른 날짜 범위는 무시됩니다[5]. 그룹 주소로 검색한 결과에는 구성원 한 사람 한 사람에게 전달된 정보가 없고, 그룹으로 보낸 메일에는 전달 뒤 상태도 없습니다[5][6].

ELS 에서 발신 IP 로 검색하면 도메인의 공개 발신 IP 대신 Google 발신 서버 IP 가 보일 수 있습니다[5]. Gmail 은 보내는 메일을 Google 서버로 내보내기 때문입니다. 사용자가 메일을 쓴 위치를 알고 싶으면 Gmail 로그 이벤트의 IP address 나 BigQuery `message_info.connection_info.client_ip` 를 봅니다[3][4].

ELS 결과를 CSV 로 내보내면 전달 뒤 세부 정보가 빠지고, 전달 단계마다 한 줄씩 적혀 메시지 수보다 줄이 많습니다[6]. Message ID 열에 `SMTPIN_ADDED_REJECT_SESSION` 이 있고 다른 머리글 열이 N/A 이면 ID 를 정하지 못한 채 SMTP 릴레이가 메시지를 거부한 것입니다[6].

BigQuery `message_info.subject` 와 `from_header_displayname` 은 로그가 길거나 걸린 규칙이 많으면 잘릴 수 있습니다[4]. 2024년 4월에서 7월 사이에 켠 BigQuery 내보내기에는 2024년 4월부터 켠 날까지의 View 이벤트가 없고, 2024년 8월 이후에 켠 내보내기에는 켠 날 기준 6개월 전까지의 View 이벤트가 들어 있습니다[4]. 내보내기를 켠 날짜를 알아 두어야 열람 기록이 없는 이유를 설명할 수 있습니다.

조사자의 검색도 기록으로 남습니다. ELS 로 검색하면 관리 로그에 `EMAIL_LOG_SEARCH` 이벤트가 검색 조건(`EMAIL_LOG_SEARCH_SENDER`, `EMAIL_LOG_SEARCH_RECIPIENT`, `EMAIL_LOG_SEARCH_MSG_ID`, 날짜, IP)과 함께 남습니다[10]. 공격자가 관리자 계정으로 ELS 를 돌린 흔적도 같은 이벤트로 찾으므로, 조사자는 자기 계정과 검색 시각을 따로 적어 두어 자기 기록을 걸러냅니다.

## 직접 분석해 보기

JSON 로그라서 헥스를 따라갈 필요는 없고, 마이크로초 시각을 한 번 손으로 바꿔 봅니다. 아래는 만든 예시 값입니다. `event_info.timestamp_usec` 가 `1758879312000000` 이면 끝의 여섯 자리를 떼어 초로 만든 `1758879312` 를 UTC 로 바꿉니다.

```sh
date -u -d @1758879312 +%Y-%m-%dT%H:%M:%SZ
# 2025-09-26T09:35:12Z
```

공개 도구로는 invictus-ir 의 ALFA 가 보고서 API 로 Gmail 활동을 받습니다[13]. 기본 수집 목록에서는 gmail 이 주석 처리되어 있어 `--logtype=gmail` 로 따로 지정합니다[13].

```sh
alfa acquire --logtype=gmail --start-time=2026-09-01T00:00:00Z --end-time=2026-09-25T00:00:00Z
```

시각은 `2026-09-01` 같은 흔한 형식으로 주어도 RFC 3339 로 바꿔 쓰고, 시간대를 적지 않으면 UTC 로 봅니다[13]. 날짜를 주지 않으면 ALFA 는 최근 30일을 쓰고, 시작·끝 가운데 하나만 주거나 구간이 30일을 넘거나 180일보다 오래된 시각을 주면 오류를 냅니다[13]. 결과는 한 줄에 활동 하나인 JSON 이고, 파일에서 `event_info` 의 `mail_event_type` 값으로 묶어 세면 동작 종류별 건수를 볼 수 있습니다. 원자료를 지키는 절차는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 를 따릅니다.

BigQuery 내보내기가 켜져 있으면 `_PARTITIONTIME` 조건과 시각 조건을 함께 걸고 `event_info.mail_event_type` 과 `message_info.rfc2822_message_id` 로 거릅니다[4][9]. 데이터세트의 표 이름과 열 경로는 BigQuery 콘솔의 스키마 화면에서 확인합니다.

## 교차 검증

- 외부로 자동 전달을 켠 흔적은 로그인 로그의 `email_forwarding_out_of_domain` 에 남습니다[11]. [로그인 기록](login-audit.md) 에서 확인하고, Gmail 로그의 `mail_event_type` 11(자동 전달)과 시각을 맞춰 봅니다.
- 관리자가 만든 메일 라우팅·규칙은 관리 로그 `CREATE_GMAIL_SETTING`·`CHANGE_GMAIL_SETTING`, 격리 해제는 `RELEASE_FROM_QUARANTINE`, 메일 모니터는 `CREATE_EMAIL_MONITOR` 로 남습니다[10][14]. [관리 콘솔 감사 로그](admin-audit.md) 에서 봅니다.
- 앱이 Gmail API 로 메일에 접근했다면 `mail_event_type` 33 과 함께 토큰 로그의 `GMAIL` 제품 구분 활동을 봅니다[1][12]. [OAuth 토큰 기록](token-audit.md) 에 있습니다.
- 메일 속 Drive 항목을 저장한 흔적(18·19)은 [Drive 기록](drive-audit.md) 과 맞춰 봅니다.
- 본문이 필요하면 [Vault와 Takeout](vault-takeout.md) 에서 보존·내보내기를 확인합니다.
- Microsoft 365 에서 같은 역할을 하는 기록은 [Exchange Online](../m365/exchange-online/index.md) 에 있습니다.

## 실습

공개 데이터가 없으므로 위 JSON 예시와 표로 풀고, 시험용 테넌트가 있으면 직접 메일을 주고받아 확인합니다.

1. 예시 레코드의 `mail_event_type` 17 을 보고서에 쓸 때 "첨부 파일을 유출했다" 가 아니라 기록으로 확인되는 만큼만 적으면 어떤 문장이 되는지 써 봅니다.
2. 사용자가 Gmail 웹에서 "Show Original" 로 메시지를 받았다고 말합니다. Gmail 로그에서 무엇을 찾을 수 있고, 무엇을 찾을 수 없는지 나눠 봅니다.
3. 45일 전에 받은 메일의 전달 경로를 ELS 로 찾으려면 어떤 값이 있어야 하고, 결과에서 무엇이 빠지는지 적어 봅니다.
4. BigQuery 에서 한국 시간 9월 26일 하루의 Gmail 기록을 뽑을 때 `_PARTITIONTIME` 조건을 어떻게 잡아야 빠지는 기록이 없는지 따져 봅니다.
5. 시험용 테넌트에서 메일을 보내고, 열고, 링크를 누르고, 휴지통을 비운 뒤 보안 조사 도구와 보고서 API 결과를 비교해 어느 쪽에 무엇이 남는지 적어 봅니다.

송금 사기 조사에서 이 기록을 어떤 순서로 쓰는지는 [메일 계정을 빼앗겨 송금 사기를 당했나](../../04-scenarios/account-compromise/bec.md), 여러 로그를 시간순으로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에 있습니다.

## 참고 문헌

1. Google, "Gmail Activity Events", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/gmail
2. Google, "Method: activities.list", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/reference/rest/v1/activities/list
3. Google, "Gmail log events", Google Workspace Admin Help. https://knowledge.workspace.google.com/admin/reports/gmail-log-events
4. Google, "Schema for Gmail logs in BigQuery", Google Workspace Admin Help. https://knowledge.workspace.google.com/admin/reports/schema-for-gmail-logs-in-bigquery
5. Google, "Find messages with Email Log Search", Google Workspace Admin Help. https://support.google.com/a/answer/2604578
6. Google, "Understand Email Log Search results", Google Workspace Admin Help. https://knowledge.workspace.google.com/admin/gmail/advanced/understand-email-log-search-results
7. Google, "Data retention and lag times", Google Workspace Admin Help. https://support.google.com/a/answer/7061566
8. Google, "About reporting logs and BigQuery", Google Workspace Admin Help. https://knowledge.workspace.google.com/admin/reports/about-reporting-logs-and-bigquery
9. Google, "Set up service log exports to BigQuery", Google Workspace Admin Help. https://knowledge.workspace.google.com/admin/reports/set-up-service-log-exports-to-bigquery
10. Google, "Admin Audit Activity Events - Email Settings", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-gmail-settings
11. Google, "Login Audit Activity Events", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/login
12. Google, "OAuth Token Audit Activity Events", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/token
13. invictus-ir, ALFA, README.md, alfa/cmdline.py, alfa/main/collector.py, alfa/config/config.yml. https://github.com/invictus-ir/ALFA
14. Google, "Admin Audit Activity Events - User Settings", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-user-settings
15. Google Cloud, "Audit logs for Google Workspace", Cloud Logging. https://cloud.google.com/logging/docs/audit/gsuite-audit-logging
