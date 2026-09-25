---
title: "Claude 기업용 감사 로그"
parent: "아티팩트 · 네트워크·기업 기록"
nav_order: 790
---

# Claude 기업용 감사 로그 (Audit Logs)

## 한 줄 요약

Claude Enterprise 조직은 로그인, 구성원 초대, 프로젝트·대화·파일의 생성과 삭제 같은 활동을 최근 180일치 감사 로그로 내보낼 수 있고, 이 로그는 서버에만 있어서 PC 이미지가 아니라 조직의 Owner 에게서 받아야 합니다.

확인 날짜는 2026-09이고, 근거는 Claude 도움말 센터의 "How to access audit logs" 문서(2026-06-15)입니다. PC 쪽 흔적은 기기 관찰 결과입니다(확인 범위: Windows 11, 2026-09).

## 무엇을 기록하나 · 왜 생기나

감사 로그는 조직 관리자가 계정과 데이터에 어떤 일이 있었는지 돌아보려고 남기는 기록이고, Enterprise 요금제 조직만 쓸 수 있습니다. 기록 대상은 대화 내용이 아니라 활동입니다. 누가 언제 로그인했는지, 누구를 초대하고 내보냈는지, SSO·도메인 설정을 언제 바꿨는지, 프로젝트·대화·파일을 언제 만들고 지웠는지가 남습니다.

대화와 프로젝트의 제목과 내용은 감사 로그에 들어가지 않고 고유 식별자만 들어갑니다. 대화의 입력과 출력이 필요하면 Primary Owner 가 따로 하는 "데이터 내보내기" 로 가져가야 하고, 그 형식은 [계정 데이터 내보내기 형식](../../01-foundations/storage-model/data-export-formats.md)에서 다룹니다. 감사 로그와 데이터 내보내기는 서로 다른 자료라서, 조사에서는 둘을 따로 요청하고 식별자로 이어 붙입니다. 조직 내보내기에서 대화를 사람별로 나누는 방법과 `users.json` 에 없는 사용자를 가려내는 방법은 [계정 데이터 내보내기](../chat-services/claude/export.md)에서 다룹니다[2].

Team 요금제, Claude Code, API 콘솔의 감사 기록은 이 도움말 문서의 범위 밖이라 이 페이지에서 다루지 않습니다. Claude Code 가 기기에 남기는 기록은 [Claude Code](../dev-agents/claude-code/index.md) 페이지에 있습니다.

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 쓸 수 있는 조직 | Enterprise 조직 |
| 내보내는 사람 | 조직의 Owner·Primary Owner |
| 내보내는 곳 | **Organization settings → Data and Privacy** 의 "Export logs" |
| 받는 방법 | 다운로드 링크가 이메일로 오고, 24시간 안에 받아야 함 |
| 범위 | 최근 180일 |
| 파일 형식 | 도움말에 없음. 받은 파일의 첫 바이트로 CSV 인지 JSON 인지 확인 |
| 다른 경로 | 감사 로그 이벤트는 Compliance API 로도 제공됨. 고객 관리 암호화 키를 쓰는 Enterprise 조직은 "Export logs" 버튼을 쓸 수 없음 |

도움말은 고객 관리 암호화 키를 쓰는 Enterprise 조직이 "Export logs" 버튼으로 내보낼 수 없다고 적었습니다[1]. 이런 조직에는 Compliance API 로 받은 자료를 요청합니다.

감사 로그는 서버에만 있고 PC 이미지에서는 얻을 수 없습니다. PC 에서 볼 수 있는 Claude 데스크톱 앱의 `Network` 폴더(확인 범위: Windows 11, 2026-09)는 접속 흔적일 뿐 감사 로그가 아니고, 그 내용은 [AI 서비스 도메인과 네트워크 기록](network-traces.md)에서 다룹니다. 앱과 웹에 남는 흔적은 [Claude](../chat-services/claude/index.md) 페이지를 봅니다.

## 구조

### 기록마다 들어가는 칸

| 칸 | 담는 것 |
|---|---|
| `created_at` | 이벤트가 생긴 시각 |
| `actor_info` | 활동을 한 사용자 |
| `event` | 이벤트 이름 |
| `event_info` | 이벤트의 세부 정보 |
| `entity_info` | 대상(대화·프로젝트·파일 등)의 식별 정보 |
| `ip_address` | 요청이 들어온 IP 주소 |
| `device_id` | 기기 식별자 |
| `user_agent` | 요청한 클라이언트의 사용자 에이전트 문자열 |
| `client_platform` | 클라이언트 플랫폼 |

칸 이름은 문서에 나온 그대로이고, `actor_info`·`event_info`·`entity_info` 안에 어떤 하위 칸이 들어가는지는 문서에 나오지 않습니다.

### 이벤트 분류

문서 표에 나온 이벤트 이름을 성격별로 묶으면 아래와 같습니다. 조사 질문에 따라 어느 묶음을 먼저 볼지 정합니다.

| 묶음 | 이벤트 이름 |
|---|---|
| 로그인·계정 | `user_signed_in_sso`, `user_signed_in_google`, `user_signed_in_apple`, `user_signed_out`, `user_requested_magic_link`, `user_attempted_magic_link_verification`, `user_sent_phone_code`, `user_verified_phone_code`, `user_name_changed` |
| 대화·파일 | `conversation_created`, `conversation_renamed`, `conversation_deleted`, `file_uploaded` |
| 프로젝트 | `project_created`, `project_renamed`, `project_deleted`, `project_visibility_changed`, `project_document_created`, `project_document_deleted` |
| 조직 구성원 | `org_user_invite_sent`, `org_user_invite_re_sent`, `org_user_invite_accepted`, `org_user_invite_rejected`, `org_user_invite_deleted`, `org_user_deleted` |
| SSO·도메인 | `org_sso_add_initiated`, `org_sso_connection_activated`, `org_sso_connection_deactivated`, `org_sso_connection_deleted`, `org_sso_toggled`, `org_jit_toggled`, `org_domain_add_initiated`, `org_domain_verified` |
| 데이터 내보내기 | `org_data_export_started`, `org_data_export_completed` |

## 증거로서 의미

**증명하는 것.** 로그인 이벤트는 그 계정이 언제 어떤 방식(SSO·Google·Apple·매직 링크)으로 들어왔는지를, `ip_address`·`device_id`·`user_agent`·`client_platform` 은 어느 네트워크와 클라이언트에서 들어왔는지를 보여 줍니다. `file_uploaded` 는 그 계정이 파일을 올린 시각을, `conversation_deleted`·`project_document_deleted` 는 지운 시각을 보여 주고, `org_data_export_started`·`org_data_export_completed` 는 조직 데이터를 누가 언제 내보냈는지를 보여 줍니다.

**증명하지 못하는 것.** 제목과 내용이 없어서 어떤 파일을 올렸는지, 대화에서 무엇을 물었는지는 감사 로그만으로 알 수 없고, 데이터 내보내기 자료를 받아 식별자로 맞춰 봐야 합니다. 계정 단위의 기록이라서 그 시각에 누가 자판 앞에 있었는지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 밝힙니다. 개인 계정이나 Team 요금제로 쓴 Claude 는 이 감사 로그에 들어가지 않아서, 기록이 없다고 해서 그 직원이 Claude 를 쓰지 않았다고 결론 내리지 않습니다.

보고서 문장은 "조직이 내보낸 감사 로그에 이 계정이 이 시각에 이 IP 에서 파일을 한 건 올린 기록이 있다" 처럼 기록이 말하는 범위에서 씁니다.

## 시각 해석

시각 칸은 `created_at` 이지만 값의 형식과 시간대는 문서에 나오지 않습니다. 받은 파일에서 값에 시간대 표시가 붙어 있는지 먼저 확인하고, 같은 시간대의 PC 기록(예: 데스크톱 앱의 쿠키 시각, 네트워크 기록)과 맞춰 보아 기준 시간대를 정합니다. 범위가 최근 180일이고 링크가 24시간 뒤 만료되어서, 사건 날짜가 오래되었다면 요청을 서둘러야 하고 받은 날짜를 보고서에 적어 범위를 밝힙니다. 여러 기록을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **180일.** 범위 밖의 이벤트는 내보내기에 들어가지 않습니다. 보존 기간이 필요하면 조직의 보관 설정과 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)의 일반론을 함께 봅니다.
- **내용이 없다.** `conversation_created` 가 있어도 대화 내용은 들어 있지 않습니다. 데이터 내보내기와 함께 요청합니다.
- **지우기.** 사용자가 대화나 프로젝트 문서를 지워도 `conversation_deleted`·`project_document_deleted` 이벤트가 남아서, 지운 시각 자체가 단서가 됩니다.
- **조사 쪽 내보내기도 남는다.** 조직 데이터 내보내기는 `org_data_export_started`·`org_data_export_completed` 이벤트로 남습니다. 조사를 위해 Owner 가 한 내보내기를 조사 대상의 행동으로 잘못 읽지 않도록 요청 날짜와 요청한 사람을 따로 적어 둡니다. 감사 로그를 내보낸 일 자체가 이벤트로 남는지는 문서에 나오지 않습니다.
- **IP 와 기기.** `ip_address` 는 VPN·회사 게이트웨이를 거치면 개인 기기를 가리키지 않습니다. `device_id` 가 PC 쪽 어떤 값과 이어지는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다.

## 직접 분석해 보기

**헥스로 한 번.** 감사 로그는 서버에서 내보내는 자료라서 헥스로 따라갈 PC 파일이 없고, 내보낸 파일의 형식도 문서에 나오지 않았습니다. 받은 파일의 첫 몇 바이트를 헥스로 보고 텍스트 표(CSV)인지 JSON 인지부터 확인한 뒤 알맞은 도구로 엽니다.

**공개 도구로 한 번.** 파일 형식이 도움말에 없어서 특정 도구 명령 대신 읽는 순서를 보입니다. 아래는 문서의 칸 이름으로 **만든 예시**이고 값은 모두 가짜입니다.

| `created_at` | `actor_info` | `event` | `entity_info` | `ip_address` | `client_platform` |
|---|---|---|---|---|---|
| (시각 1) | user-sample-01 | `user_signed_in_sso` | — | 198.51.100.23 | (웹) |
| (시각 2) | user-sample-01 | `conversation_created` | conv-0000-aaaa | 198.51.100.23 | (웹) |
| (시각 3) | user-sample-01 | `file_uploaded` | file-0000-bbbb | 198.51.100.23 | (웹) |
| (시각 4) | user-sample-01 | `conversation_deleted` | conv-0000-aaaa | 203.0.113.7 | (데스크톱) |

이 예시에서는 로그인 뒤 대화를 만들고 파일을 올렸고, 나중에 다른 IP 와 다른 클라이언트에서 같은 대화를 지웠다는 흐름까지 읽을 수 있습니다. 파일 이름과 대화 내용은 어디에도 없어서, `conv-0000-aaaa` 같은 식별자로 데이터 내보내기 자료를 찾아 맞춰 봅니다. CSV 로 받았다면 스프레드시트나 Python 의 csv 모듈로, JSON 으로 받았다면 jq 로 `event` 칸을 기준으로 거릅니다.

## 교차 검증

- [계정 데이터 내보내기로 수집](../../03-techniques/acquisition/export-collection.md) — 감사 로그의 식별자로 대화 내용을 찾는 흐름
- [AI 서비스 도메인과 네트워크 기록](network-traces.md) — 같은 시각에 PC 에서 `*.claude.ai` 접속이 있었는지
- [Claude](../chat-services/claude/index.md) — 앱·브라우저에 남은 흔적
- [보안 제품이 남기는 AI 사용 기록](dlp-casb.md) — `file_uploaded` 시각에 DLP 기록이 있는지
- [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) — 조직이 협조하지 않거나 범위 밖 자료가 필요할 때

## 실습

감사 로그는 조직이 서버에서 내보내는 자료라서 PC 이미지 검체로는 풀 수 없고, 시험용 Enterprise 조직에서 아래 질문을 풀어 봅니다.

1. 감사 로그를 내보내고 파일 형식과 `created_at` 값의 시간대 표시를 확인합니다.
2. 대화를 만들고 파일을 올린 뒤 지우고, 세 이벤트가 같은 `entity_info` 식별자로 이어지는지 봅니다.
3. 웹과 데스크톱 앱에서 각각 로그인하고 `client_platform`·`user_agent`·`device_id` 가 어떻게 다른지 비교합니다.
4. 감사 로그를 내보낸 뒤 다시 내보내고, 첫 내보내기가 로그에 이벤트로 남는지 확인합니다.

## 참고 문헌

1. How to access audit logs (Audit Logs in Claude Enterprise) — Claude 도움말 센터 (2026-06-15) — https://support.claude.com/en/articles/9970975-how-to-access-audit-logs
2. ukogan/claude-migration-assistant, `js/processing/admin-reader.js` — https://github.com/ukogan/claude-migration-assistant
