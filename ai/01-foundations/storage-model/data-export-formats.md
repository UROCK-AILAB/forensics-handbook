---
title: "계정 데이터 내보내기 형식"
parent: "기반 · 저장 구조"
nav_order: 20
---

# 계정 데이터 내보내기 형식 (Data Export Formats)

## 한 줄 요약

계정 데이터 내보내기 (Data Export) 는 서버 계정에 있는 대화를 계정 주인이 직접 내려받는 기능이고, 서비스마다 파일 모양(JSON 묶음, 활동 목록, CSV 한 장, HTML 묶음)과 시각 형식이 달라서 받은 파일이 어느 서비스의 어떤 형식인지부터 가린 뒤 읽어야 합니다.

내보내기 형식은 공지 없이 바뀌므로 지금 받은 파일과 다를 수 있습니다.

## 이 형식을 쓰는 아티팩트

대화 원본이 서버 계정에 있는 서비스([ChatGPT](../../02-artifacts/chat-services/chatgpt/index.md), [Claude](../../02-artifacts/chat-services/claude/index.md), [Gemini](../../02-artifacts/chat-services/gemini/index.md), [Microsoft Copilot](../../02-artifacts/chat-services/copilot/index.md), [Meta AI](../../02-artifacts/chat-services/meta-ai-glasses.md))에서 원본을 얻는 길은 계정 주인의 내보내기와 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) 두 가지입니다. 원본이 어디에 있는지 가리는 법은 [AI 서비스의 데이터는 어디에 있나](where-data-lives.md)에서, 내보내기를 받아 증거로 보존하는 절차는 [계정 데이터 내보내기로 수집](../../03-techniques/acquisition/export-collection.md)에서 다룹니다.

이 쪽은 서비스끼리 형식을 견줍니다. 칸 하나하나의 뜻과 만든 예시는 서비스별 내보내기 쪽에 있습니다.

| 서비스 | 칸까지 다루는 쪽 |
|---|---|
| ChatGPT | [ChatGPT 계정 데이터 내보내기](../../02-artifacts/chat-services/chatgpt/export.md) |
| Claude | [Claude 계정 데이터 내보내기](../../02-artifacts/chat-services/claude/export.md) |
| Gemini | [Gemini 계정 데이터 내보내기](../../02-artifacts/chat-services/gemini/export.md) |
| Microsoft Copilot | [Microsoft Copilot 계정 데이터 내보내기](../../02-artifacts/chat-services/copilot/export.md) |
| Meta AI | [Meta AI 앱과 AI 안경](../../02-artifacts/chat-services/meta-ai-glasses.md) |

## 구조

### 서비스별 한눈에 보기

| 서비스 | 요청하는 곳 | 받는 방식 | 파일 모양 | 대화 단위 | 시각 형식 |
|---|---|---|---|---|---|
| ChatGPT | 웹 Settings → Data controls → Export data[6]. 개인정보 포털에서 받는 길도 있음[9] | 이메일로 ZIP[6] | ZIP 안에 JSON 여러 개와 `chat.html`[6] | 대화마다 메시지 나무(`mapping`)[6][7] | 유닉스 초(소수점 포함)[6][7]. `message_feedback.json` 만 ISO-8601 문자열[7] |
| Claude(개인) | 웹·데스크톱 앱의 이름 머리글자 → Settings → Privacy → "Export data". iOS·Android 앱에서는 못 함[1] | 계정 이메일로 링크. 전달 뒤 24시간에 만료되고 받을 때 로그인 필요[1] | ZIP 안에 JSON 네 개[10][11] | 대화마다 메시지 배열(`chat_messages`)과 부모 메시지 칸[10][13] | ISO-8601 UTC, 끝에 `Z`[10][11] |
| Claude(Team·Enterprise) | 조직의 Primary Owner 만 요청[1] | 공식 도움말에 설명 없음 | 개인과 같은 JSON 네 개. 읽는 도구 하나는 ZIP 이 아닌 낱개 JSON 으로 온다고 적음[12] | 개인과 같음. 대화마다 작성 계정 칸[12] | 개인과 같음 |
| Gemini 앱 | Google Takeout 의 "My Activity" → "All activity data included" → "Gemini Apps". Gems 는 "Gemini" 항목[2] | 이메일 링크(7일 유효) 또는 Google Drive·Dropbox·OneDrive·Box. `.zip` 이나 `.tgz`[2] | 활동 목록 파일 하나. HTML 이나 JSON[14] | 대화 없이 활동 한 건씩[15][16] | ISO-8601 UTC, 끝에 `Z`[15][16] |
| Microsoft Copilot(개인) | 개인정보 대시보드 `account.microsoft.com/privacy/copilot` → "Your Copilot activity history" → "Export all activity history"[18] | 대시보드에서 내려받음[18] | CSV 한 장[17][18] | 대화 제목 칸으로만 묶음, ID 없음[17] | 시간대 표시 없는 ISO-8601[17] |
| Meta AI | Meta 계정 센터 (Accounts Center) 의 데이터 내보내기[19] | 논문에 설명 없음 | 분류별 HTML 파일과 미디어 폴더[19] | HTML 표 안의 대화 덩어리[20] | 날짜만 있거나 영문 표기 문자열[20] |

"대화 단위" 열은 대화를 되짚을 때 무엇을 열쇠로 쓰는지 보여 줍니다. ChatGPT 와 Claude 는 대화 ID 와 메시지 ID 가 있어서 대화를 그대로 되살릴 수 있고, Gemini 와 Copilot 은 ID 가 없어서 시각이나 제목으로 묶어야 합니다.

### ChatGPT

ZIP 맨 위에 `conversations.json`, `user.json`, `chat.html`, `message_feedback.json`, `shared_conversations.json` 이 오고, 2025년 이후 판에는 `group_chats.json`, `shopping.json`, `sora.json` 이 더해졌습니다[6]. 대화 파일이 `conversations-000.json` 처럼 번호 붙은 파일 여러 개로 나뉘어 오기도 하고[9], 개인정보 포털에서 받은 파일은 겉 ZIP 안에 `Conversations__*-chatgpt-*.zip` 모양의 ZIP 이 한 겹 더 들어 있습니다[9].

RLEAPP 분석기는 네 파일을 읽습니다[7][8]. `user.json` 에서는 `id`, `email`, `chatgpt_plus_user`, `phone_number` 를, `shared_conversations.json` 에서는 공유 ID(`id`)와 `conversation_id`, `title`, `is_anonymous` 를 뽑습니다. `message_feedback.json` 에서는 `create_time`, `user_id`, `id`, `conversation_id`, `rating`, `workspace_id`, `content`, `storage_protocol` 을 뽑습니다. RLEAPP 의 대화 분석기는 2024-07-09 을 마지막 검증일로 적었고, 계정 정보 분석기는 2026-07-09 에 마지막으로 고쳤습니다.

같은 내보내기 안에서도 시각 형식이 둘입니다. `conversations.json` 의 `create_time`·`update_time` 은 유닉스 초 숫자이고[6], `message_feedback.json` 의 `create_time` 은 ISO-8601 문자열이라 RLEAPP 도 두 가지를 다른 함수로 바꿉니다[7]. RLEAPP 는 ISO 문자열에 시간대가 없으면 UTC 로 간주합니다[7].

대화 칸(`mapping`, `current_node`, `gizmo_id` 등)과 메시지 칸은 [ChatGPT 계정 데이터 내보내기](../../02-artifacts/chat-services/chatgpt/export.md)에서 다룹니다.

### Claude

ZIP 안의 파일은 `conversations.json`, `users.json`, `projects.json`, `memories.json` 넷이고, 여러 도구가 이 네 이름으로 파일을 찾습니다[10][11][12].

| 파일 | 도구가 읽는 칸 | 출처 |
|---|---|---|
| `conversations.json` | 대화: `uuid`, `name`, `summary`, `created_at`, `updated_at`, `account.uuid`, `project_uuid`, `chat_messages[]` | [10], [13] |
| (메시지) | `uuid`, `text`, `content[]`, `sender`, `created_at`, `updated_at`, `attachments[]`, `files[]`, `parent_message_uuid` | [10], [13] |
| `users.json` | `uuid`, `full_name`, `email_address`, `verified_phone_number` | [10] |
| `projects.json` | `uuid`, `name`, `description`, `is_private`, `is_starter_project`, `prompt_template`, `created_at`, `updated_at`, `creator`, `docs[]`(`uuid`, `filename`, `content`) | [10], [13] |
| `memories.json` | 판마다 모양이 다름. 계정 단위 객체에 `conversations_memory`, `project_memories`, `memory_files[]`, `account_uuid` | [10], [12], [13] |

`sender` 값은 `human` 과 `assistant` 입니다[10]. 예전 내보내기는 메시지 배열 이름이 `chat_messages` 가 아니라 `messages` 라서, 두 이름을 모두 찾아야 합니다[9]. 메시지 본문은 `text` 한 칸과 `content[]` 블록 배열 두 곳에 있고, `content[]` 에는 `text`, `thinking`, `tool_use`, `tool_result` 블록이 들어갑니다[10][11]. `text` 칸은 도구 블록을 빼고 펼친 글이라 두 곳이 다를 수 있고(한 내보내기에서는 메시지 654개 가운데 87개), 그래서 `content[]` 를 읽습니다[11].

첨부는 `attachments[]` 의 `file_name`, `file_size`, `file_type`, `extracted_content` 로 들어가고, `extracted_content` 에는 첨부에서 뽑은 본문 글이 담깁니다[10]. `files[]` 에는 `file_name` 만 있습니다[10].

조직 내보내기에서는 대화의 `account.uuid` 를 `users.json` 의 `uuid` 와 맞춰 사람별로 대화를 나눕니다[12]. 같은 방식으로 `memories.json` 은 `account_uuid` 로, `projects.json` 은 `creator.uuid` 로 사람에 이어집니다[12]. 대화에는 있는데 `users.json` 에 없는 UUID 를 이 도구는 "Departed User", 곧 조직을 떠난 사용자로 표시합니다[12]. 조직 쪽 기록은 [Claude 기업용 감사 로그](../../02-artifacts/network-enterprise/claude-enterprise.md)와 함께 봅니다.

### Gemini

Takeout 의 Gemini 대화는 `Takeout/My Activity/Gemini Apps/` 아래 활동 파일 하나로 옵니다[14][15]. 파일 이름은 `My Activity.json` 이나 예전 표기 `MyActivity.json` 입니다[14][15][16]. 폴더와 파일 이름은 계정 언어를 따라 바뀌어서, 그리스어 계정에서는 `Takeout/Η δραστηριότητά μου/Εφαρμογές Gemini/Ηδραστηριότητάμου.json` 이 됩니다[15]. JSON 으로 받으려면 "My Activity" 옆 "Multiple formats" 에서 JSON 을 골라야 하므로[14], 받은 파일이 HTML 인지 JSON 인지부터 봅니다.

JSON 레코드 한 건은 프롬프트 하나이고, 칸은 아래와 같습니다.

| 칸 | 내용 | 출처 |
|---|---|---|
| `header` | `"Gemini Apps"`. 이름을 바꾸기 전 판은 `"Bard"`. 다른 Google 서비스 활동이 같은 파일에 섞이면 이 값으로 거름 | [16], [14] |
| `title` | 앞말이 붙은 프롬프트. `Prompted `, `Asked`, `Submitted query `, `Created Gemini Canvas titled ` 등 | [14], [15], [16] |
| `text` | 새 판의 프롬프트 칸 | [16] |
| `time` | ISO-8601 UTC. 예: `2025-12-15T10:30:00.000Z` | [15], [16] |
| `titleUrl`, `products` | 대화 주소, 제품 이름 | [16] |
| `subtitles[]` | 모델 이름, Canvas 본문 | [15], [16] |
| `safeHtmlItem[].html` | 답변 HTML | [14], [15] |
| `attachmentInfo[]` | 첨부 정보 | [14] |
| `details[]` | 일부 판에서 답변을 담는다고 적힘 | [16] |

활동을 한 건씩 늘어놓은 목록이라 대화 ID 가 없습니다. silver-gr 도구는 30분 안에 이어진 활동을 한 대화로 묶는데[15], 도구가 추정한 묶음일 뿐 파일에 적힌 대화 경계가 아닙니다.

답변이 파일에 들어가는지는 출처끼리 다릅니다. remnic(2026-06-05 수정)은 "Assistant responses are NOT exported by Takeout" 라고 적었고[16], gemini-to-obsidian(2025-10-02 수정)과 silver-gr(2025-12-16 수정)은 `safeHtmlItem` 을 답변으로 읽습니다[14][15]. 받은 파일에 `safeHtmlItem` 이 있는지 검체에서 보고, 그 결과를 받은 날짜와 함께 적습니다.

Gemini 는 "Keep Activity" 가 켜져 있을 때 대화를 계정의 "Gemini Apps Activity" 에 저장합니다[3]. 활동 설정별 보관 기간은 [대화 기록 보관 설정과 삭제](retention-deletion.md)에 있습니다.

### Microsoft Copilot

소비자용 Copilot 은 활동 기록을 CSV 한 장으로 내보내고, 파일 이름은 보통 `copilot-activity-history.csv` 이고, 다를 수도 있습니다[18].

2026년 7월 내보내기 파일의 모양은 다음과 같습니다[17].

- 첫 줄은 `Conversation,Time,Author,Message` 이고 파일 앞에 UTF-8 BOM(`EF BB BF`)이 붙습니다.
- `Author` 값은 `Human` 과 `AI` 입니다.
- `Time` 은 `2026-07-26T23:20:56` 같은 모양이고 시간대 표시가 없습니다.
- 줄 구분은 CRLF 이고 칸 안의 줄바꿈은 LF 입니다.
- 줄은 최신 것부터 나옵니다. 파일 전체와 대화 안 모두 그렇습니다.
- 대화 ID 와 메시지 ID 가 없어서 대화는 `Conversation` 칸의 제목으로만 가립니다.

한 실제 파일에서는 2613줄 가운데 1290줄이 옆 줄과 시각이 같았습니다[17]. AI 줄과 그 앞 Human 줄이 같은 초를 쓰기 때문이고, 그래서 시각으로 정렬하면 답변이 질문보다 앞에 올 수 있습니다. 시간 순서로 보려면 정렬하지 말고 파일 순서를 뒤집습니다[17]. 칸별 해석은 [Microsoft Copilot 계정 데이터 내보내기](../../02-artifacts/chat-services/copilot/export.md)에 있습니다.

### Meta AI

Meta 계정 센터에서 받은 클라우드 내보내기는 분류별 HTML 파일로 옵니다(Android 14, Meta AI 앱 `com.facebook.stella` 258.0.0.15.167 기준)[19]. 파일은 아래와 같습니다(표 5).

| 경로 | 담긴 것 |
|---|---|
| `meta_ai_profile/your_ai_conversations.html` | 사용자 프롬프트, AI 응답, 대화 시각·날짜 |
| `meta_ai_profile/your_meta_ai_profile.html` | 사용자 이름, 계정 만든 날짜, 마지막 갱신 시각 |
| `meta_ai_app/meta_ai_media.html` | 미디어를 기기 일련번호와 날짜에 연결 |
| `posts/media/your_posts/` | AI 대화에 입력으로 쓴 이미지 |
| `meta_ai_app/connected_devices.html` | 음성 상호작용 메타데이터, "Hey Meta" 설정, 기기 설정 |
| `meta_ai_app/app_settings.html` | 앱과 짝지은 기기의 마지막 설정 |

기기의 `interaction_log.db` 에서는 사용자 음성 질의가 `<redacted>` 로 가려져 있었지만, 클라우드 내보내기에는 프롬프트가 남았습니다[19]. 논문 팀이 만든 ALEAPP 플러그인 Meta-AI-Parser 는 `*/meta_ai_profile/*.html` 과 `*/meta_ai_app/*.html` 을 찾아 읽습니다[20]. 이 코드는 대화 HTML 에서 `You` 와 `Meta AI` 를 말한 쪽으로 가르고, 대화 날짜는 HTML 안의 `Conversation with Meta AI_` 로 시작하는 `.txt` 이름에서 뒤에 붙은 `두 자리-두 자리-네 자리` 날짜를 가져옵니다[20]. 미디어 시각은 `Jan 05, 2026 3:04 pm` 같은 영문 문자열(만든 예시)로 읽고 시간대 표시가 없습니다[20]. 기기 쪽 흔적은 [Meta AI 앱과 AI 안경](../../02-artifacts/chat-services/meta-ai-glasses.md)에서 다룹니다.

### 로컬 도구 — 내보내기 대신 원본 파일

대화 원본을 기기에 두는 도구는 서버 내보내기를 거칠 필요 없이 기기의 파일이 곧 원본입니다. Claude Code 는 세션 기록을 `~/.claude/projects/<프로젝트>/<세션>.jsonl` 에 평문으로 남기고[4], 이 파일을 사본으로 떠서 보존합니다. 기록 구조는 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md)에서 다룹니다. Ollama 는 모델 파일을 `models` 폴더에 두고[5], 자세한 것은 [Ollama](../../02-artifacts/local-ai/ollama.md)에 있습니다.

## 읽는 법

1. 내려받은 파일은 열기 전에 해시를 구하고, 받은 날짜·시각과 요청한 계정, 링크를 받은 이메일을 함께 기록합니다.
2. 파일 앞 몇 바이트로 겉 형식을 가립니다. ZIP 은 `50 4B 03 04` 로 시작하고[21], Copilot CSV 는 BOM `EF BB BF` 뒤에 `Conversation,Time,Author,Message` 가 옵니다[17]. JSON 은 공백을 건너뛴 첫 글자가 `[` 이나 `{` 입니다.
3. 사본에서 압축 안의 파일 목록(이름, 크기, 압축 안에 적힌 수정 시각)을 먼저 뜹니다. 파일 구성은 서비스와 시점마다 달라서 목록 자체를 증거 기록에 붙입니다.
4. 위 표의 파일 이름으로 서비스를 가립니다. `conversations.json` 은 ChatGPT 와 Claude 가 함께 쓰는 이름이라, 곁에 `user.json`(ChatGPT)이 있는지 `users.json`(Claude)이 있는지로 나눕니다[6][10]. 안쪽 모양으로 가리려면 ChatGPT 대화에는 `mapping` 이, Claude 대화에는 `chat_messages` 가 있는지 봅니다[6][10].
5. JSON 은 `jq` 같은 도구로 최상위 키 목록부터 뽑고, HTML 은 인터넷에 연결되지 않은 환경에서 엽니다.
6. 시각 칸을 서비스별 형식에 맞게 UTC 로 바꾼 뒤 한 표로 모아 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 올리고, 기기 쪽 흔적의 시각과 맞춰 봅니다.

## 포렌식에서 중요한 점

**내보내기는 요청 시점의 사본입니다.** 요청한 때와 보관 파일을 만든 때 사이에 바뀐 데이터는 빠질 수 있습니다[2]. 사용자가 이미 지운 대화가 내보내기에 들어가는지는 서비스 문서에 적혀 있지 않습니다. 그래서 "내보내기에 없다" 를 "그런 대화를 한 적이 없다" 로 쓰지 않습니다.

**지우는 동작마다 클라우드에 남는 것이 다릅니다.** Ray-Ban Meta 논문의 실험에서는 앱에서 미디어를 지우자 뒤에 받은 내보내기의 `meta_ai_media.html` 과 `posts/media/your_posts/` 에서도 사라졌고, "Delete Voice Activity" 를 쓰자 대화 기록이 빠졌습니다[19]. 그런데 AI 로 만든 알림은 대화 기록을 지우고 안경을 초기화한 뒤에도 `reminders.html` 에 남았습니다[19]. 이 결과는 그 실험 환경의 관찰이라서, 다른 서비스에 옮겨 적지 않습니다.

**계정과 사람을 잇는 칸이 있습니다.** ChatGPT `user.json` 에는 이메일과 전화번호가[8], Claude `users.json` 에는 이름·이메일·인증 전화번호가 있습니다[10]. 조직 Claude 내보내기에서는 `account.uuid` 로 대화를 쓴 계정을 가를 수 있습니다[12]. 다만 이 칸들은 대화를 한 계정을 알려 줄 뿐 자판 앞에 앉은 사람을 알려 주지 않으므로, [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 기기 쪽 흔적과 맞춥니다.

**받는 과정 자체가 계정 접근입니다.** Claude 의 내려받기 링크는 로그인해야 쓸 수 있고 24시간 뒤 만료됩니다[1]. 조사자가 계정 주인 대신 받으려면 계정에 접근할 권한과 법적 근거가 먼저 있어야 하고, 권한이 없으면 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 방향을 바꿉니다. Claude 는 iOS·Android 앱에서 내보내기를 할 수 없어서[1], 모바일만 쓰는 사용자라도 웹이나 데스크톱으로 로그인해 요청해야 합니다. 이때 새로 생기는 로그인 기록이 조사 기간의 기록과 섞이지 않도록 요청한 시각을 따로 적습니다.

**기기에 남은 내보내기 파일도 증거입니다.** 내보내기는 계정 주인이 요청해야 생기므로, 기기에서 이 파일이 나오면 그 계정으로 누군가 내보내기를 요청한 적이 있다는 뜻입니다. 다만 파일은 다른 곳에서 받아 옮겨 왔을 수도 있어서, 브라우저 다운로드 기록과 메일함의 안내 메일로 받은 경로를 확인합니다.

## 함정

**같은 이름, 다른 형식.** `conversations.json` 은 ChatGPT 와 Claude 가 함께 쓰는 이름이고, Proton 의 불러오기 코드도 두 서비스의 ZIP 을 같은 함수로 엽니다[9]. 파일 이름만 보고 서비스를 정하지 말고 곁의 파일과 안쪽 키로 가립니다.

**시각의 기준이 서비스마다 다릅니다.** ChatGPT 대화는 유닉스 초, ChatGPT 피드백과 Claude·Gemini 는 ISO-8601 문자열입니다[6][7][10][16]. Copilot CSV 와 Meta HTML 의 시각에는 시간대 표시가 없어서[17][20], 값 몇 개를 기기 쪽 기록과 맞춰 본 뒤 기준을 정하고 그 근거를 보고서에 적습니다. 압축 파일 안에 적힌 수정 시각은 MS-DOS 형식이라[21] 시간대 정보가 없습니다.

**도구가 분석 PC 의 시간대를 섞을 수 있습니다.** kninami 의 ChatGPT 분석 스크립트는 유닉스 초를 `datetime.fromtimestamp()` 로 바꾸는데[23], 이 함수는 시간대를 주지 않으면 분석 PC 의 현지 시각을 돌려줍니다. 결과 표의 시각이 UTC 인지 도구 설명과 코드로 확인하고 적습니다.

**본문을 한 칸만 읽으면 빠집니다.** Claude 메시지의 `text` 칸만 읽으면 도구 호출과 결과가 빠지고[11], Gemini `title` 에 붙은 앞말을 지우지 않으면 프롬프트 첫머리가 달라집니다[14][16].

**이미지가 들어 있는지는 출처끼리 다릅니다.** convoviz 명세(2026-02)는 ChatGPT ZIP 에 생성 이미지 폴더와 올린 파일이 들어 있다고 적었고[6], chatgpt-forensic-exporter 설명서는 공식 내보내기가 이미지를 빼고 JSON 하나로 온다고 적었습니다[22]. 받은 파일에 이미지가 있는지 검체에서 보고 날짜와 함께 적습니다.

**다른 서비스의 파일 구성을 옮겨 적지 않습니다.** 위 표의 구성은 도구가 읽은 시점의 것입니다. 받은 파일의 목록과 다르면 받은 파일을 따르고, 차이를 보고서에 적습니다.

## 도구

해시는 `certutil -hashfile`(Windows), `shasum -a 256`(macOS), `sha256sum`(Linux) 같은 OS 기본 명령으로 구하고, 압축 안의 파일 목록은 7-Zip 같은 공개 압축 도구의 목록 보기로 뜹니다. JSON 은 `jq` 로 보고, 표로 모을 때는 스프레드시트나 SQLite 로 옮깁니다.

서비스별 공개 분석기는 아래와 같습니다. 모두 비공식 형식을 거꾸로 읽어 낸 것이라, 시험한 날짜보다 뒤에 받은 파일은 칸이 빠지거나 늘었는지 먼저 봅니다.

| 대상 | 도구 | 시험·수정 시점 |
|---|---|---|
| ChatGPT | RLEAPP `chatgpt.py`, `chatGPTaccountInfo.py`[7][8] | 대화 분석기 검증 2024-07-09, 계정 정보 분석기 수정 2026-07-09 |
| Claude | claude-export-viewer[10], la-roca[13], claude-migration-assistant(조직 내보내기)[12] | 2026-02-12, 2026-08-21, 2026-02-12 수정 |
| Gemini | gemini-to-obsidian[14], AI-Conversation-Toolkit[15], remnic[16] | 2025-10-02, 2025-12-16, 2026-06-05 수정 |
| Copilot | llm-aggregator.ts[17] | 2026년 7월 실제 파일로 확인, 2026-07-27 수정 |
| Meta AI | Meta-AI-Parser(ALEAPP 플러그인)[20] | 2026-04-12 수정. 논문은 앱 258.0.0.15.167 로 실험 |

## 참고 문헌

1. Claude Help Center — How can I export my Claude data? (2026-07-08 수정) — https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-data
2. Gemini Apps Help — Download your Gemini Apps data — https://support.google.com/gemini/answer/16920332?hl=en
3. Gemini Apps Help — Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961?hl=en
4. Claude Code Docs — .claude 폴더 참조 (claude-directory) — https://code.claude.com/docs/en/claude-directory
5. Ollama — FAQ — https://docs.ollama.com/faq
6. mohamed-chs/convoviz, `docs/dev/chatgpt-spec.md` "ChatGPT User Data Export Specification (Unofficial)" v3.0(2026-02-05, 파일 수정 2026-08-26) — https://github.com/mohamed-chs/convoviz
7. abrignoni/RLEAPP, `scripts/artifacts/chatgpt.py` (작성 Evangelos Dragonas, 검증 2024-07-09) — https://github.com/abrignoni/RLEAPP
8. abrignoni/RLEAPP, `scripts/artifacts/chatGPTaccountInfo.py` (2026-07-09 수정) — https://github.com/abrignoni/RLEAPP
9. ProtonMail/WebClients, `applications/lumo/src/app/features/aiPaperTrail/parsers/zipConversations.ts`(2026-09-09 수정), `claude.ts`(2026-07-23 수정) — https://github.com/ProtonMail/WebClients
10. lordjabez/claude-export-viewer, `src/claude_export_viewer/models.py`, `loader.py` (2026-02-12 수정) — https://github.com/lordjabez/claude-export-viewer
11. EmpiricaAI/empirica, `docs/reference/api/CLAUDE_AI_PARSER.md` (2026-09-23 수정) — https://github.com/EmpiricaAI/empirica
12. ukogan/claude-migration-assistant, `js/processing/admin-reader.js` (2026-02-12 수정) — https://github.com/ukogan/claude-migration-assistant
13. thellmwhisperer/la-roca, `pkg/parsers/claude_web.go` (2026-08-21 수정) — https://github.com/thellmwhisperer/la-roca
14. Coryrichter94/gemini-to-obsidian, `README.md` 와 변환 스크립트 (2025-10-02 수정) — https://github.com/Coryrichter94/gemini-to-obsidian
15. silver-gr/AI-Conversation-Toolkit, `docs/gemini-extractor.md` (2025-12-16 수정) — https://github.com/silver-gr/AI-Conversation-Toolkit
16. joshuaswarren/remnic, `packages/import-gemini/src/parser.ts` (2026-06-05 수정) — https://github.com/joshuaswarren/remnic
17. vladsadovsky/llm-aggregator.ts, `electron/services/import/archive/parsers/copilotCsv.ts` (2026-07-27 수정) — https://github.com/vladsadovsky/llm-aggregator.ts
18. MaxAnkum/copilot-history-memory-mart, `README.md` — https://github.com/MaxAnkum/copilot-history-memory-mart ; baneeishaque/ai-suite, copilot-activity-history-split `SKILL.md` — https://github.com/baneeishaque/ai-suite
19. Panta, S., Alsmadi, R., Baggili, I., "Seeing the Evidence: A Forensic Framework for Analyzing Ray-Ban Meta AI Smart Glasses", Forensic Science International: Digital Investigation (2026), DFRWS USA 2026 — https://dfrws.org/presentation/seeing-the-evidence-a-forensic-framework-for-analyzing-ray-ban-meta-ai-smart-glasses/
20. BiTLab-BaggiliTruthLab/Meta-AI-Parser, `meta_ai.py` (2026-04-12 수정) — https://github.com/BiTLab-BaggiliTruthLab/Meta-AI-Parser
21. PKWARE, APPNOTE.TXT — .ZIP File Format Specification 6.3.10 (2022-11-01), 4.3.7 로컬 파일 머리의 서명 `0x04034b50`, 4.4.6 날짜·시각 칸 — https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT
22. loucdg/chatgpt-forensic-exporter, `README.md` — https://github.com/loucdg/chatgpt-forensic-exporter
23. kninami/chatgptForensics, `README.md`, `parse_data.py` — https://github.com/kninami/chatgptForensics
