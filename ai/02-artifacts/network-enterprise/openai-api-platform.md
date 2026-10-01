---
title: "OpenAI API 플랫폼 기록"
parent: "아티팩트 · 네트워크·기업 기록"
nav_order: 785
---

# OpenAI API 플랫폼 기록 (API Platform)

회사가 OpenAI API 로 만든 앱이나 에이전트가 사고에 얽히면, 조직 설정을 누가 바꿨는지는 API 플랫폼 감사 로그 (Audit Logs) 로, 모델에 무엇을 보내고 받았는지는 API 호출 로깅과 저장 객체로, 에이전트가 어떤 순서로 움직였는지는 Agents SDK 트레이스 (trace) 로 확인합니다. 셋 다 OpenAI 서버에 있는 자료라서 조직 관리자에게서 받고, 켜 두지 않았거나 보관 기간이 지나면 남지 않습니다[1][2][3].

ChatGPT 작업 공간 (workspace) 의 대화·감사·인증 기록은 요금제와 전달 경로가 달라서 [ChatGPT 기업용 감사 기록](chatgpt-enterprise.md)에서 다룹니다. 이 페이지는 API 플랫폼 조직만 다룹니다.

## 무엇을 기록하나 · 왜 생기나

API 플랫폼 조직은 ChatGPT 요금제와 따로 움직이는 개발자용 계정입니다. 조직 안에 프로젝트를 만들고, 프로젝트마다 API 키와 서비스 계정 (service account) 을 두고 모델을 부릅니다. 사고 때 볼 자료는 성격이 다른 세 가지입니다.

감사 로그는 조직의 보안·관리 활동을 기록합니다. 로그인, 구성원 초대, API 키와 서비스 계정, 역할과 권한, 프로젝트, IP 허용 목록 같은 네트워크 통제, 인증서와 외부 키, 조직 설정 변경이 여기에 남습니다[1]. OpenAI 관리 API 문서에도 이 기록은 조직의 최근 사용자 행동과 설정 변경을 나열하는 Audit Logs 엔드포인트로 나옵니다[4].

API 호출 로깅은 지원하는 API 호출의 프롬프트, 응답, 사용량 메타데이터를 보관해 조직 관리자가 플랫폼의 로그 화면에서 보게 해 주는 조직 설정입니다. 감사 로그와도, 남용 모니터링 (abuse monitoring) 로그와도 다른 설정입니다[1].

Agents SDK 트레이스는 OpenAI Agents SDK 로 만든 에이전트가 돌 때 SDK 가 스스로 남기는 실행 기록입니다. 에이전트 실행, 모델 호출, 함수 도구 호출, 가드레일 (guardrail) 검사, 핸드오프 (handoff, 다른 에이전트에게 일을 넘김) 를 단위 구간 (span) 으로 남기고, OpenAI 의 Traces 대시보드로 보냅니다[3].

이 셋과 별도로, 앱이 API 로 저장해 둔 응답·대화·파일·벡터 저장소도 증거가 됩니다. 로그가 아니라 앱이 쓰던 데이터라서 보관 기간이 로그와 다릅니다. 아래 "로그 말고 보존할 저장 객체" 절에서 따로 다룹니다.

## 위치와 버전별 차이


| 자료 | 담는 것 | 기본으로 켜져 있나 | 보관 |
|---|---|---|---|
| 감사 로그 | 인증·ID·자격 증명·권한·프로젝트·네트워크 통제·조직 설정 변경 | 꺼져 있음[1] | 정해진 기간 없음[1] |
| API 호출 로깅 | API 요청·응답 내용과 사용량 메타데이터 | 호출 단위로 켜져 있음[1] | 30일[1] |
| Agents SDK 트레이스 | 에이전트 실행, 모델 호출, 도구 호출, 핸드오프, 가드레일 | 켜져 있음[3] | 공개된 기간 없음[1] |
| 저장 객체(Responses·Conversations·Files·벡터 저장소) | 모델 출력, 도구 호출 인자, 대화 상태, 올린 파일 | 앱이 저장했을 때만 | 객체마다 다름[2] |

감사 로그는 기본으로 꺼져 있어서 사고가 나기 전에 켜 두어야 하고, 한 번 켠 감사 로그는 OpenAI 에 연락하지 않고는 끌 수 없어서 공격자가 끄기 어렵습니다[1]. OpenAI 는 감사 로그의 보관 기간을 정해 두지 않고 영구 보관을 보장하지 않은 채 가능한 만큼 (best-effort) 보관하며, 현재 스키마의 이벤트 종류는 55개 이상입니다[1]. 보관 기간이 보장되지 않으므로 오래된 기록이 필요하면 조직이 평소에 내보내 두어야 하고, 조사를 시작하면 가장 먼저 지금까지의 감사 로그를 내보냅니다.

API 호출 로깅의 기본값은 "모든 프로젝트" 가 아니라 "호출 단위 (per call)" 이고, 조직의 데이터 제어 (Data controls) 설정에서 끄거나 모든 프로젝트로 넓힐 수 있습니다[1]. 보관 기간은 30일입니다[1].

### 로그를 바꾸는 설정

아래 설정은 조직이나 프로젝트 단위로 걸리고, 어떤 기록이 생기는지를 바꿉니다. 조사를 시작할 때 사고 시점에 어느 설정이 걸려 있었는지 먼저 확인합니다.

- **데이터 보존 안 함 (Zero Data Retention, ZDR).** 고객 내용을 남용 모니터링 로그에서 빼고, `/v1/responses` 와 `/v1/chat/completions` 의 `store` 파라미터를 요청이 `true` 로 보내도 늘 `false` 로 다룹니다[2]. ZDR 대상이 아닌 엔드포인트나 기능은 ZDR 을 켜도 앱 상태를 저장할 수 있습니다[2]. ZDR 조직에서는 Agents SDK 트레이스를 쓸 수 없습니다[3]. 감사 로그는 ZDR 과 상관없이 남습니다[1].
- **수정된 남용 모니터링 (Modified Abuse Monitoring).** 모든 API 엔드포인트에서 고객 내용을 남용 모니터링 로그에서 빼고, 나머지 기능은 그대로 둡니다. 이미지·파일 입력은 드물게 로그에 남을 수 있습니다[2]. ZDR 과 다른 설정이라서 `store` 동작은 바뀌지 않습니다. 남용 모니터링 로그는 기본으로 최대 30일 보관하고, 법이 요구하면 더 오래 보관합니다[2].
- **Private Retention with Private Safety Processing (예전 이름 "Eyes Off") 와 Safety Retention.** ZDR 이나 수정된 남용 모니터링을 승인받은 조직이라도 OpenAI 가 특정 모델을 예외로 정하면, 고객 내용이 남을 수 있습니다. Private Retention 에서는 고객 내용을 암호화된 남용 모니터링 로그에 남기되 법이 요구하지 않으면 사람이 보지 않고, Safety Retention 에서는 심각한 위험을 조사하거나 막으려고 분류기가 정책 위반 가능성을 잡은 내용을 남기고 사람이 볼 수 있습니다[2]. 이 두 설정은 고객이 받아 올 수 있는 자료가 아니라 OpenAI 가 쥐고 있는 자료에 관한 것입니다[1]. 이 자료가 필요하면 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)의 절차를 밟습니다.
- **기업 키 관리 (Enterprise Key Management, EKM).** 설정한 뒤 만든 앱 상태를 고객이 AWS KMS, Google Cloud, Azure Key Vault 에 둔 키로 암호화합니다. EKM 을 켠 프로젝트에서 Assistants(`/v1/assistants`) 를 부르면 오류가 납니다[2]. EKM 을 쓰는 조직이면 고객 키를 쓸 수 있어야 저장된 증거를 읽을 수 있습니다[1]. 조직이 키를 폐기했거나 권한을 거뒀는지 확인합니다.
- **데이터 저장 지역 (data residency).** 프로젝트마다 정하고, 새 프로젝트를 만들 때 지역을 고릅니다[2]. 지역 설정은 고객 내용에만 걸리고, 고객 내용이 없는 계정 데이터·메타데이터·사용량 데이터는 선택한 지역 밖에서 처리·저장될 수 있습니다[2]. 법적 요청을 보낼 곳과 관할을 정할 때 프로젝트별 지역을 먼저 봅니다.

## 구조

### 감사 로그 — 사건 유형별로 먼저 볼 이벤트

사건 유형별로 먼저 볼 감사 로그 이벤트는 아래와 같습니다[1]. 이벤트 목록은 바뀔 수 있으므로 조사할 때 OpenAI API 참조 문서의 이벤트 목록과 대조합니다.

| 사건 유형 | 먼저 볼 이벤트 | 알 수 있는 것 |
|---|---|---|
| 계정 탈취 | `login.succeeded`, `login.failed`, `logout.succeeded`, `logout.failed` | 인증 타임라인과 행위자·세션 정보. 접속 주소, 위치, 사용자 에이전트, TLS 지문 포함 |
| 무단 접근 | `invite.sent`, `invite.accepted`, `invite.deleted`, `user.added`, `user.updated`, `user.deleted` | 새로 생기거나 바뀐 조직 접근 권한 |
| 자격 증명 지속성 | `api_key.created`, `api_key.updated`, `api_key.deleted`, `service_account.created`, `service_account.updated`, `service_account.deleted` | 오래 쓰는 프로그램용 접근이나 자격 증명 변조. 새로 만든 서비스 계정의 역할을 함께 확인 |
| 권한 상승 | `role.created`, `role.updated`, `role.deleted`, `role.assignment.created`, `role.assignment.deleted` | 새로 만들거나 넓힌 역할, 더한 권한, 그 역할을 붙인 주체(사용자·서비스 계정 등)와 리소스 |
| 프로젝트 분리 | `project.created`, `project.updated`, `project.archived`, `project.deleted` | 감시하는 프로젝트와 떨어진 곳에 키와 활동을 모으려고 새로 만들거나 바꾼 프로젝트, 프로젝트를 없앤 변경 |
| 로깅 무력화 | `organization.updated` 가운데 `changes_requested` 에 `api_call_logging` 이나 `api_call_logging_project_ids` 가 든 것 | API 호출 내용 로깅을 껐는지, 호출 단위로 좁혔는지, 일부 프로젝트만 남겼는지와 빠진 프로젝트 |
| 네트워크 통제 약화 | `ip_allowlist.created`, `ip_allowlist.updated`, `ip_allowlist.deleted`, `ip_allowlist.config.activated`, `ip_allowlist.config.deactivated` | 네트워크 접근 제한을 넓히거나 없애거나 껐다 켠 일. `allowed_ips` 에 너무 넓은 범위가 있는지 확인 |
| ID 통제 약화 | `scim.enabled`, `scim.disabled`, `group.created`, `group.updated`, `group.deleted` | 사용자 자동 등록·해제(SCIM)와 그룹 관리 변경. 퇴사자 계정 해제를 우회했는지 포함 |
| 키와 인증서 | `certificate.created`, `certificate.updated`, `certificate.deleted`, `certificates.activated`, `certificates.deactivated`, `external_key.registered`, `external_key.removed` | 인증서를 만들고 없앤 이력과 적용 여부 변경, 고객 관리 키를 등록하거나 뺀 일 |
| 파괴 행위와 인프라 | `resource.deleted`, `tunnel.created`, `tunnel.updated`, `tunnel.deleted`, `checkpoint.permission.created`, `checkpoint.permission.deleted` | 리소스 삭제와 인프라 수준의 관리 활동 |

계정 탈취를 조사할 때는 `login.succeeded` 로 들어온 시각과 행위자를 잡은 뒤, 같은 행위자가 이어서 남긴 `user.*`, `project.*`, `api_key.*` 와 역할 이벤트로 넘어갑니다[1]. 방어 약화 (Defense Impairment)[5] 를 의심하면 `scim.disabled`, IP 허용 목록 변경·삭제, 외부 키·인증서 이벤트, 조직 설정 변경, API 호출 로깅 설정 변경을 봅니다[1].

ChatGPT 작업 공간의 인증 로그와 API 플랫폼 감사 로그는 필드가 다릅니다. API 감사 로그에 있는 필드가 ChatGPT 인증 로그에도 있다고 가정하지 않습니다[1].

### API 호출 로깅

켜져 있으면 지원하는 API 호출의 프롬프트, 응답, 사용량 메타데이터가 남고, 조직 관리자는 플랫폼의 로그 화면에서 봅니다[1]. 프롬프트 인젝션, 데이터 유출, 도구 오용처럼 "모델이 무엇을 받고 무엇을 돌려줬나" 를 묻는 사건에서 내용을 확인하는 자료입니다[1]. 로깅을 호출 단위로 둔 조직에서는 모든 호출이 남지 않을 수 있으므로, 사고 시점에 로깅 범위가 어떻게 설정돼 있었는지와 위 표의 `organization.updated` 이력을 함께 봅니다.

### Agents SDK 트레이스

Python 판 Agents SDK 는 기본으로 트레이스를 남기고, 아래 구간을 자동으로 기록합니다[3].

| 구간 | 기록하는 것 |
|---|---|
| 트레이스 전체 | 러너 (runner) 한 번의 실행 |
| `task_span()` | 러너 호출 한 번 |
| `turn_span()` | 모델 차례 한 번 |
| `agent_span()` | 에이전트 실행 |
| `generation_span()` | 모델 호출 |
| `function_span()` | 함수 도구 호출 |
| `guardrail_span()` | 가드레일 검사 |
| `handoff_span()` | 다른 에이전트로 넘긴 일 |
| `transcription_span()`, `speech_span()` | 음성을 글로, 글을 음성으로 바꾼 일 |

트레이스는 세 가지 방법으로 끌 수 있습니다. 환경 변수 `OPENAI_AGENTS_DISABLE_TRACING=1`, 코드 전체에 거는 `set_tracing_disabled(True)`, 실행마다 거는 `RunConfig.tracing_disabled` 입니다[3]. `add_trace_processor()` 는 OpenAI 로 보내는 기본 경로에 처리기를 더하고, `set_trace_processors()` 는 기본 처리기를 통째로 바꿉니다[3]. 그래서 OpenAI Traces 대시보드에 트레이스가 없으면, 에이전트를 돌린 서버의 환경 변수·설정 파일·소스 코드에서 위 이름을 찾고, 다른 곳으로 보낸 트레이스가 있는지 확인합니다.

## 로그 말고 보존할 저장 객체

로그가 가리키는 앱 객체에도 증거가 들어 있습니다. Responses 와 Conversations 에는 모델 출력, 도구 호출 인자, 대화 상태가 남을 수 있고, Files 에는 사고에 쓰인 민감한 내용이나 악성·주입 내용이 있을 수 있으며, 벡터 저장소나 Assistants 리소스는 앱이 그것을 썼을 때 앞뒤 사정을 알려 줍니다[1].

| 객체 | 앱 상태 보관 |
|---|---|
| Responses (`store=true`) | 최소 30일[2]. ZDR 에서는 저장하지 않음[2] |
| Conversations | 지울 때까지[2] |
| Files | 지울 때까지. API·대시보드에서 지우거나 `expires_after` 로 자동 삭제[2] |
| 벡터 저장소 | 지울 때까지[2] |
| Assistants·Threads 관련 객체 | 지운 뒤 30일 지나 서버에서 삭제. 지우지 않으면 계속 보관[2] |
| 코드 인터프리터·호스티드 셸 컨테이너 | 컨테이너가 만료되거나 지워지면 삭제[2] |

보관 기간이 객체와 설정마다 다르고 그 객체를 가리킨 로그의 보관 기간과도 다르므로, 관련 객체를 찾으면 로그 보관 기간을 믿지 말고 일찍 보존합니다[1]. 저장된 객체로 내용과 상태는 알 수 있지만 어떻게 쓰였는지는 알 수 없습니다. 파일이 저장돼 있다고 모델이 그 파일을 읽었다는 뜻이 아니고, 도구 호출 기록이 있다고 그 뒤의 실제 작업이 성공했다는 뜻도 아닙니다[1].

## 도구·네트워크 설정으로 그때 가능했던 일 정하기

도구 설정은 증거가 아니지만, 사고 당시 그 환경에서 무엇이 가능했는지 범위를 정해 줍니다. 조직 관리자는 MCP 도구, 웹 검색, 파일 검색, 이미지 생성, 코드 인터프리터를 각각 끄거나, 모든 프로젝트에 켜거나, 고른 프로젝트에만 켤 수 있습니다[1].

MCP 와 웹 검색은 조직 밖으로 데이터가 오가는 길을 엽니다[1]. 원격 MCP 서버는 제3자 서비스라서 거기로 보낸 데이터는 그 서비스의 보관 정책을 따르고, 네트워크로 제3자에게 보낸 데이터도 마찬가지입니다[2]. 해당 프로젝트에서 MCP 가 켜져 있었다면 어느 MCP 서버를 썼는지 확인하고, 그 서버 쪽 기록은 [MCP 서버와 도구 호출 기록](../dev-agents/mcp.md)의 방법으로 따로 받습니다.

파일 검색과 코드 인터프리터는 사용자나 앱이 읽고 처리할 수 있는 데이터를 넓힙니다. 파일 검색은 조직이 연결한 데이터에서 내용을 찾아오고, 코드 인터프리터는 코드를 실행해 올리거나 만든 파일을 처리합니다[1]. 컨테이너 네트워크 모드는 컨테이너에서 도는 도구가 밖으로 접속할 수 있는지를 정하고, 위험이 큰 설정입니다[1]. 켜져 있었다면 외부 목적지, 데이터 전송, 도구가 일으킨 네트워크 활동이 사건과 관계있는지 봅니다.

지금 보이는 설정은 사고 당시 설정과 다를 수 있습니다. 설정 화면을 확인 시각과 함께 기록하고, 그 사이 설정을 바꾼 기록이 감사 로그에 있는지 함께 봅니다.

## 증거로서 의미

**증명하는 것.** 감사 로그로 어느 행위자가 언제 API 키·서비스 계정·역할·프로젝트·네트워크 통제·조직 설정을 바꿨는지 알 수 있습니다[1]. API 호출 로깅이 켜져 있었다면 그 호출에서 모델이 받은 입력과 돌려준 출력을, 트레이스가 있다면 에이전트가 어떤 순서로 모델과 도구를 불렀고 어디서 다른 에이전트로 넘겼는지를 알 수 있습니다[1][3].

**증명하지 못하는 것.** 트레이스가 없다고 에이전트가 돌지 않았다는 뜻이 아닙니다. 트레이스는 끄거나 다른 처리기로 돌릴 수 있고, ZDR 조직에서는 OpenAI 가 보관하는 트레이스가 없습니다[1][3]. API 호출 로깅이 없는 것도 호출이 없었다는 뜻이 아니고, 로깅이 꺼져 있었거나 그 프로젝트가 범위에서 빠졌을 수 있습니다. 도구 호출이 기록돼 있어도 그 도구가 바깥 시스템에서 실제로 무엇을 했는지는 그 시스템의 기록으로 확인합니다[1]. API 키로 들어온 요청은 키를 가진 누구나 보낼 수 있으므로, 키를 누가 썼는지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 밝힙니다.

OpenAI 쪽 기록만으로 사건 전체를 알 수는 없고, ID 제공자, 엔드포인트, 클라우드, 앱, 저장소, MCP 서버 기록이 함께 필요합니다[1]. 보고서 문장은 "조직이 제공한 API 플랫폼 감사 로그에 이 사용자가 이 시각에 새 API 키를 만든 `api_key.created` 이벤트가 있다" 처럼 받은 자료로 확인되는 만큼만 쓰고, 어느 자료(감사 로그, API 호출 로깅, 트레이스, 저장 객체)에서 나온 것인지 밝힙니다.

## 시각 해석

감사 로그·호출 로그·트레이스의 시각 필드 이름과 단위, 시간대는 받은 자료에서 직접 확인합니다. 감사 로그의 로그인 시각은 ID 제공자의 로그인 기록과, 트레이스의 모델·도구 호출 시각은 에이전트를 돌린 서버 로그와 맞춰 보아 기준을 정합니다. 여러 기록을 시간순으로 합치는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **사고 뒤에 켜면 늦다.** 감사 로그는 기본으로 꺼져 있고[1], 켜기 전의 활동은 남지 않습니다. 조직이 감사 로그를 언제 켰는지부터 확인합니다.
- **호출 로깅은 공격 대상이다.** 감사 로그와 달리 API 호출 로깅은 끌 수 있어서, 증거인 동시에 안티포렌식의 표적입니다[1]. `organization.updated` 의 `changes_requested` 에 `api_call_logging` 이나 `api_call_logging_project_ids` 가 있으면 누가 언제 무엇으로 바꿨는지 확인합니다.
- **ZDR 과 수정된 남용 모니터링을 헷갈리기 쉽다.** 둘 다 남용 모니터링 로그에서 고객 내용을 빼지만, `store` 를 강제로 `false` 로 바꾸는 것은 ZDR 뿐입니다[2]. 저장 객체가 없다는 해석은 어느 설정이었는지에 따라 달라집니다.
- **PC 이미지로는 얻을 수 없다.** 감사 로그·호출 로그·트레이스는 OpenAI 서버에 있어서 조직 관리자에게 요청하고, OpenAI 만 가진 자료는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 받습니다. 개발자 PC 나 서버에 남은 API 키와 환경 변수는 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에서 다룹니다.
- **문서가 바뀐다.** 이벤트 목록, 기본값, 보관 기간은 판마다 바뀔 수 있으므로 조사 시점의 OpenAI 문서로 다시 확인하고 확인 날짜를 적습니다. 보관·삭제의 일반론은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 이 기록은 서버 쪽 자료라서 헥스로 따라갈 파일이 없습니다. 조직에서 받은 자료가 파일로 오면 형식(JSON, JSON Lines, CSV)부터 확인합니다.

**공개 도구로 한 번.** 내보낸 감사 로그가 JSON 이면, 필드 구조를 짐작하지 않고 이벤트 이름 문자열로 먼저 거릅니다. 예를 들어 자격 증명 지속성을 볼 때는 `grep -E '"(api_key|service_account)\.(created|updated|deleted)"' audit_logs.jsonl` 처럼 찾은 뒤, 걸린 줄을 jq 로 열어 행위자와 시각 필드를 확인합니다. 파일 이름은 만든 예시입니다. 트레이스는 에이전트를 돌린 서버에서 `grep -rn -E 'OPENAI_AGENTS_DISABLE_TRACING|set_tracing_disabled|tracing_disabled|set_trace_processors'` 로 소스·설정·환경 파일을 찾아 트레이스를 끄거나 다른 곳으로 보냈는지 확인합니다.

## 교차 검증

- [ChatGPT 기업용 감사 기록](chatgpt-enterprise.md) — 같은 회사의 ChatGPT 작업 공간 쪽 기록
- [AI 서비스 도메인과 네트워크 기록](network-traces.md) — 같은 시간대에 `api.openai.com` 등으로 나간 접속
- [보안 제품이 남기는 AI 사용 기록](dlp-casb.md) — 프록시·DLP 가 API 호출을 기록했는지
- [MCP 서버와 도구 호출 기록](../dev-agents/mcp.md) — 에이전트가 부른 외부 도구 서버 쪽 기록
- [Codex CLI](../dev-agents/codex-cli.md) — 개발자 PC 에 남은 코딩 에이전트 기록
- [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md), [에이전트가 자격 증명을 건드렸나](../../04-scenarios/agents/agent-credentials.md), [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) — 이 기록을 조사 질문에 쓰는 흐름
- [프롬프트 인젝션 사고 분석](../../03-techniques/analysis/prompt-injection.md) — 호출 로그와 저장 객체에서 주입된 내용을 찾는 법

## 실습

이 기록은 서버 쪽 자료라서 공개 시험 이미지로는 풀기 어렵습니다. 시험용 API 조직이 있다면 아래 질문을 직접 풀어 봅니다.

1. 감사 로그를 켠 뒤 API 키를 만들고 지워, `api_key.created` 와 `api_key.deleted` 이벤트에 어떤 행위자·시각 필드가 남는지 확인합니다.
2. 데이터 제어 설정에서 API 호출 로깅 범위를 바꾸고, `organization.updated` 이벤트의 `changes_requested` 에 무엇이 남는지 확인합니다.
3. Agents SDK 로 도구 하나를 부르는 에이전트를 돌린 뒤, `OPENAI_AGENTS_DISABLE_TRACING=1` 을 걸고 한 번 더 돌려 Traces 대시보드에 두 번째 실행이 남지 않는지 확인합니다.
4. `store=true` 로 만든 응답과 올린 파일을 지운 뒤, 감사 로그와 호출 로그에 그 객체를 가리키는 기록이 남는지 확인합니다.

## 참고 문헌

1. Invictus Incident Response, Frontier Forensics: OpenAI, Version 1.0 (2026-08) — https://www.invictus-ir.com/
2. Data controls in the OpenAI platform — OpenAI API 문서 — https://developers.openai.com/api/docs/guides/your-data
3. Tracing — OpenAI Agents SDK (Python) 문서 — https://openai.github.io/openai-agents-python/tracing/
4. Admin APIs — OpenAI API 문서 — https://developers.openai.com/api/docs/guides/admin-apis
5. Defense Impairment, Tactic TA0112 — MITRE ATT&CK (v19, 생성 2026-04-14) — https://attack.mitre.org/tactics/TA0112/
