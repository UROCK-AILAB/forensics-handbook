---
title: "계정 데이터 내보내기로 수집"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 840
---

# 계정 데이터 내보내기로 수집 (Export Collection)

계정 주인이 서비스의 내보내기 기능으로 서버에 있는 대화와 계정 정보를 받아 넘기는 수집 방법이며, 받은 파일을 곧바로 해시로 고정하고 요청부터 인계까지 시각을 기록합니다.

메뉴 이름과 위치는 앱 업데이트에 따라 바뀌므로, 수집 당일 화면을 보고 기록합니다.

## 언제 쓰나

대화 원본이 서버에 있고 계정 주인이 조사에 협조할 때 씁니다. 피해자 계정이나 회사가 관리하는 계정이 대표적인 예이고, 기기를 확보하지 못했거나 기기 수집만으로 대화를 얻기 어려울 때 쓸모가 있습니다. 계정 주인이 협조하지 않으면 [서비스 회사에 대한 데이터 요청](legal-requests.md)으로 넘어갑니다. 서버 보관 기간이 짧은 서비스가 있으니 [조사 절차](investigation-process.md)의 보관 기간 표를 보고 요청 시점을 정합니다.

받은 파일의 필드와 시각 형식은 서비스마다 다르고, 이 페이지는 받는 순서와 원본을 지키는 방법만 다룹니다. 파일 안을 읽는 법은 [계정 데이터 내보내기 형식](../../01-foundations/storage-model/data-export-formats.md)과 서비스별 내보내기 페이지에 있습니다.

## 절차

### 1. 권한과 동의를 먼저 갖춥니다

내보내기는 계정에 로그인해야 요청할 수 있고, Claude 는 내려받을 때도 로그인해 있어야 합니다[1]. 그래서 수집하는 사람은 계정 주인의 동의나 법적 권한을 먼저 갖추고, 계정 주인이 직접 요청하고 내려받는 과정을 곁에서 기록하는 방식이 무난합니다. 잠금 해제나 보안 우회로 계정에 들어가는 방법은 이 핸드북에서 다루지 않습니다.

### 2. 서비스별로 내보내기를 요청합니다

**Claude (Anthropic).** 왼쪽 아래 이니셜을 누른 뒤 Settings → Privacy → "Export data" 로 요청합니다[1]. 웹과 Claude 데스크톱에서만 할 수 있고, iOS·Android 앱에서는 요청할 수 없습니다[1]. 준비가 끝나면 계정 메일로 내려받기 링크가 오고, 링크는 보낸 때부터 24시간 뒤에 만료됩니다[1]. 개인 Free·Pro·Max 사용자가 쓸 수 있는 기능이고, Team·Enterprise 조직 데이터는 조직의 Primary Owner 만 내보낼 수 있습니다[1]. 개인 내보내기는 ZIP 이고, 그 안에 `conversations.json`, `users.json`, `projects.json`, `memories.json` 이 있습니다[10][11]. 조직 내보내기는 같은 네 파일이 ZIP 이 아닌 낱개 JSON 으로 옵니다[12]. 필드의 뜻은 [Claude 계정 데이터 내보내기](../../02-artifacts/chat-services/claude/export.md)에 있습니다.

**ChatGPT (OpenAI).** chatgpt.com 에 로그인해 왼쪽 아래 프로필 이름 → Settings → Data controls → Export 로 들어가 "Confirm export" 를 누르면, OpenAI 가 보낸 메일에서 `.zip` 파일을 받습니다[5][6]. 개인정보 포털에서 받는 경로도 있고, 이 경로로 받은 파일은 겉 ZIP 안에 `Conversations__*-chatgpt-*.zip` 모양의 ZIP 이 한 겹 더 들어 있습니다[7]. 공식 내보내기는 24~48시간 걸립니다[8]. 메일 링크가 열리는 기간은 공개된 자료가 없어서, 받은 메일의 안내 문구와 그때의 공식 도움말을 기록해 둡니다. 파일 안의 필드는 [ChatGPT 계정 데이터 내보내기](../../02-artifacts/chat-services/chatgpt/export.md)에서 봅니다.

**Gemini 앱 (Google).** 채팅과 채팅에 공유한 파일·영상·화면·사진은 "Gemini 앱 활동"(myactivity.google.com/product/gemini)에 저장되고, 이 정보는 Google Takeout(takeout.google.com)으로 내보냅니다[2]. Takeout 에서 "Deselect all" 을 누른 뒤 "My Activity" 만 고르고, "All activity data included" 에서 "Gemini Apps" 만 남깁니다[13][14]. JSON 으로 받으려면 "My Activity" 옆 "Multiple formats" 에서 형식을 JSON 으로 바꿉니다[13]. Gems 설정처럼 "Gemini" 항목으로 따로 나오는 자료, 받는 방법과 링크 유효 기간은 [Gemini 계정 데이터 내보내기](../../02-artifacts/chat-services/gemini/export.md)에 정리돼 있습니다.

**Microsoft Copilot.** Microsoft 개인정보 대시보드(`https://account.microsoft.com/privacy/copilot`)의 "Your Copilot activity history" 에서 "Export all activity history" 를 골라 CSV 를 받습니다[16]. 대시보드의 두 부분을 따로 내보내야 하는 점과 파일 구조는 [Copilot 계정 데이터 내보내기](../../02-artifacts/chat-services/copilot/export.md)에 있습니다.

**Claude Code.** 로컬 세션 기록은 계정 내보내기와 따로 기기의 `~/.claude/projects/` 아래에 있습니다[3]. 위에 적은 Claude 내보내기 네 파일과는 별개이므로, 기기 기록은 [기기에서 AI 흔적 모으기](endpoint-triage.md)대로 따로 수집하고 읽는 법은 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md)에서 봅니다.

### 3. 받자마자 고정합니다

Claude 링크는 24시간 뒤 만료되므로 메일을 받으면 바로 내려받습니다[1]. 내려받은 원본 파일은 열거나 압축을 풀기 전에 해시를 계산하고, 원본은 쓰기를 막은 곳에 두고 분석은 사본으로 합니다. 조직 내보내기처럼 JSON 이 낱개로 오면 파일마다 해시를 따로 적습니다. 해시 명령은 [조사 절차](investigation-process.md)의 도구 절에 있습니다.

압축을 푼 사본에서는 들어 있어야 할 파일이 다 왔는지 봅니다. 아래 표는 공개 도구가 찾는 파일 이름이고, 판마다 다를 수 있어서 없는 파일은 "없음" 으로 기록해 둡니다.

| 서비스 | 공개 도구가 찾는 파일 | 출처 |
|---|---|---|
| ChatGPT | `conversations.json` 또는 번호가 붙은 `conversations-000.json` 들, `user.json`, `shared_conversations.json`, `message_feedback.json` | RLEAPP(2024-07-09 검증)[9], Proton[7] |
| Claude | `conversations.json`, `users.json`, `projects.json`, `memories.json` | [10][11][12] |
| Gemini 앱 | `Takeout/My Activity/Gemini Apps/MyActivity.json` 또는 `My Activity.json`. 폴더와 파일 이름은 계정 언어로 바뀜 | [14](2026-07), [15](2026-06) |
| Copilot | `copilot-activity-history.csv`. 이름이 다를 수 있음 | [16] |

Gemini 폴더 이름은 계정 언어를 따릅니다. 예를 들어 그리스어 계정에서는 경로가 `Takeout/Η δραστηριότητά μου/Εφαρμογές Gemini/Ηδραστηριότητάμου.json` 입니다[14]. 그래서 영어 이름으로만 찾지 말고 `My Activity` 아래 JSON 파일을 열어 `header` 값으로 Gemini 레코드인지 봅니다[15]. 이 값은 `"Gemini Apps"` 이고[15], 계정 언어에 따라 바뀌는지는 실제 데이터로 확인합니다.

### 4. 요청부터 인계까지 기록합니다

보관 연속성은 [조사 절차](investigation-process.md)에 적은 RFC 3227 항목을 따르고[4], 내보내기에서는 다음 시각과 값을 더 적어 둡니다.

| 적을 것 | 이유 |
|---|---|
| 요청한 시각과 요청한 화면(웹·데스크톱 등) | 내보내기에 담긴 내용이 어느 시점 기준인지 밝히려고 |
| 요청한 계정과 계정 종류(개인·조직) | 조직 계정은 내보낼 수 있는 사람이 다름 |
| 고른 항목과 형식(Takeout 의 항목, JSON·HTML, .zip·.tgz) | 고르지 않은 항목은 보관 파일에 없음 |
| 메일을 받은 시각과 링크를 연 시각 | 링크 만료 전에 받았음을 보이려고 |
| 파일 이름, 크기, 해시 | 이후 사본과 원본이 같음을 보이려고 |
| 참여한 사람(계정 주인, 수집자) | 누가 계정에 로그인했는지 남기려고 |

아래는 기록 모양을 보여 주려고 새로 만든 예시이고, 계정과 파일 이름, 시각은 모두 지어낸 것입니다.

```text
요청: 2026-09-15 09:05 KST, 웹, 계정 sample.user@example.com (개인)
메일 수신: 2026-09-15 09:40 KST / 링크 열기: 2026-09-15 09:42 KST
파일: export_sample.zip, 크기 (바이트 수), SHA-256 (계산 값)
참여: 계정 주인 박예시(직접 로그인), 수집자 분석관 최가상
```

### 5. 분석으로 넘깁니다

받은 파일의 구조는 [계정 데이터 내보내기 형식](../../01-foundations/storage-model/data-export-formats.md)에서 읽는 법을 보고, 대화 시각은 [AI 사용 타임라인](../analysis/timeline.md)에서 기기 기록과 함께 한 줄로 놓습니다. 프롬프트와 첨부, 생성물을 나눠 보는 기준은 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)에 있습니다.

## 공식 내보내기 대신 쓰는 수집 도구

공식 내보내기를 기다리지 않고 계정 주인이 로그인한 브라우저 세션을 빌려 서비스의 공개되지 않은 서버 API 에서 대화를 받는 공개 도구가 있습니다. chatgpt-forensic-exporter 는 로그인한 Chrome 에 원격 디버깅으로 붙어 ChatGPT 의 대화, 프로젝트, 생성 이미지를 받고, Team·Enterprise 작업 공간도 따로 찾아 받습니다[8]. convoviz 에도 공식 내보내기를 기다리지 않고 최근 대화를 받는 스크립트가 따로 있습니다[5]. 이런 도구를 쓰기 전에 세 가지를 따집니다.

**법적 권한.** 이 도구는 스스로 로그인하지 않고 이미 열린 브라우저 세션에 기댑니다[8]. 그래서 공식 내보내기와 똑같이 계정 주인의 동의나 법적 권한이 먼저 있어야 하고, 그 권한이 공식 기능이 아닌 방법까지 허용하는지도 따집니다. 이 도구는 공개되지 않은 API 를 쓰므로, 서비스 약관을 지켜 자기 데이터를 받는 데에만 씁니다[8]. 기기에 남은 인증 토큰으로 계정에 들어가는 방식은 이 핸드북에서 다루지 않고, 토큰이 남는 곳과 보고서에서 가리는 법은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다.

**위험.** 이 API 는 OpenAI 가 지원하지 않는 주소라서 예고 없이 바뀔 수 있습니다[8]. 원격 디버깅을 켜려면 Chrome 창과 뒤에서 도는 Chrome 프로세스를 모두 끄고 다시 띄워야 합니다[8]. 조사 대상 PC 에서 이렇게 하면 메모리의 브라우저 상태가 사라지고 프로필에 흔적이 더해집니다. 그래서 휘발성 자료는 [기기에서 AI 흔적 모으기](endpoint-triage.md)대로 먼저 확보하고, 이 도구는 수집용 PC 에서 계정 주인이 로그인해 쓰는 편이 안전합니다. 도구가 쓰는 파일은 서버가 준 응답을 그대로 담지 않습니다. 대화 추출 코드는 `current_node` 에서 부모를 따라 올라간 가지만 담고, `system` 메시지와 글이 아닌 본문 조각(이미지 포인터 같은 객체)을 뺀 뒤 `role`, `text`, `message_id`, `create_time` 만 남깁니다[8]. 설명서는 편집한 가지까지 담는다고 적었지만 코드는 한 가지만 따르므로, 다른 가지나 이미지 참조가 필요하면 공식 내보내기의 `mapping` 을 봅니다. 지운 대화는 받을 수 없습니다[8].

**해시 기록.** 이 도구는 대화 JSON 을 쓴 직후 SHA-256 을 계산해 해시 목록 CSV(`chatgpt_conversation_hashes.csv`, 프로젝트는 `projects_all_hashes.csv`)에 적습니다[8]. 코드에 적힌 열은 `json_file`, `conversation_id`, `sha256`, `message_count`, `scraped_at_utc` 이고, 프로젝트 목록에는 `project_name`, `gizmo_id` 가 더 붙습니다[8]. 설명서는 원본 주소도 함께 적는다고 했지만 코드에 적힌 열에는 주소가 없습니다[8]. `scraped_at_utc` 는 수집한 시각이고 UTC 오프셋이 붙은 ISO-8601 문자열이며, 메시지의 `create_time` 은 ChatGPT 가 기록한 시각이라서 둘을 섞지 않습니다[8]. `verify.py` 는 해시를 다시 계산해 목록과 대조하고, 어긋난 파일(Failed), 목록에 있는데 없는 파일(Missing), 목록에 없는 JSON(Untracked)을 따로 분류합니다[8]. 종료 코드는 0(모두 맞음), 1(어긋나거나 없는 파일이 있음), 2(내보내기 폴더나 해시 목록이 없음)입니다[8]. 이 해시는 도구가 다시 쓴 JSON 의 해시이지 서버 응답의 해시가 아니므로, 수집 뒤 파일이 바뀌지 않았음을 보여 줄 뿐 서버 내용과 같음을 보여 주지는 않습니다.

보관 연속성 기록에는 누가, 언제 시작하고 끝냈는지, 무엇을 몇 건 받았는지, 어떤 도구와 판·방법으로 받았는지, `verify.py` 결과를 남깁니다[8]. 이 목록을 위 4단계 표에 더하고, `export_verification_summary.txt` 와 해시 목록, `verify.py` 출력도 원본과 함께 해시로 고정합니다.

## 도구

공식 내보내기의 요청과 내려받기에는 서비스 화면과 브라우저만 쓰고, 받은 파일의 해시는 운영체제에 들어 있는 명령으로 계산합니다. 받은 JSON 은 `jq` 같은 JSON 도구로 필요한 키만 골라 볼 수 있습니다. 공개 분석 도구도 있습니다. RLEAPP 의 `chatgpt.py`(2024-07-09 검증)는 ChatGPT 보관 파일의 `conversations.json`, `shared_conversations.json`, `message_feedback.json` 을 읽고, `chatGPTaccountInfo.py`(최종 수정 2026-07-09)는 `user.json` 을 읽습니다[9]. 그 뒤에 바뀐 필드는 도구 결과에 안 나올 수 있어서, 도구 결과보다 원본 파일을 먼저 확인합니다.

## 함정과 한계

내보내기는 요청한 시점에 서버가 보관하던 내용만 담습니다. 계정 주인이 요청 전에 대화를 지웠다면 그 대화는 빠질 수 있고, 지운 대화를 서버에서 없애는 기간과 서비스별 보관 기간은 [조사 절차](investigation-process.md)와 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다. Gemini 앱에서 활동 저장을 끈 동안의 채팅은 계정에 72시간 보관됩니다[2]. 이런 채팅이 Takeout 보관 파일에 들어가는지는 시험용 계정으로 72시간 안에 내보내 보고 확인합니다.

보관 파일에 무엇이 들어가는지도 출처마다 다릅니다. ChatGPT 는 convoviz 개발 문서(v3.0, 2026-02-05)가 생성 이미지 폴더(`dalle-generations/`)와 올린 파일(`file-*`)이 들어 있다고 적었고[17], chatgpt-forensic-exporter 설명서(2026-03)는 이미지가 빠진다고 적었습니다[8]. 자세한 내용은 [ChatGPT 계정 데이터 내보내기](../../02-artifacts/chat-services/chatgpt/export.md)에 있습니다. Gemini 는 remnic 코드 주석(2026-06)이 Takeout 에 답변이 들어가지 않는다고 적었고[15], gemini-to-obsidian(2025-10)과 AI-Conversation-Toolkit(2026-07)은 레코드의 `safeHtmlItem` 을 답변으로 읽습니다[13][14]. 받은 보관 파일에 이미지 폴더나 답변 필드가 있는지 직접 보고, 보고서에는 내보낸 날짜와 함께 적습니다.

Takeout 에서 "Gemini Apps" 만 고르지 않으면 같은 `My Activity` 파일에 다른 Google 서비스 기록이 섞일 수 있어서, `header` 값으로 Gemini 레코드만 거릅니다[15]. 예전 보관 파일에는 이 값이 `"Bard"` 인 레코드가 있을 수 있습니다[15].

Claude 는 모바일 앱에서 내보내기를 요청할 수 없어서, 계정 주인이 모바일만 쓴다면 웹이나 데스크톱으로 로그인해 요청해야 합니다[1]. 조직 계정은 Primary Owner 만 내보낼 수 있어서 조직 담당자의 협조가 필요합니다[1]. 내보내기 링크가 계정 메일로 가므로 메일 계정에 들어갈 수 없으면 받을 수 없고, 24시간 안에 내려받지 못하면 다시 요청해야 합니다[1]. 다시 요청하면 그 사이에 바뀐 대화가 반영되므로 두 번째 파일의 요청 시각도 따로 적습니다.

## 결과를 어떻게 해석하나

내보내기 파일은 그 계정에 이런 대화가 서버 기준으로 남아 있었다는 기록이고, 그 대화를 계정 주인 본인이 입력했다는 증명은 아닙니다. 누가 입력했는지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 기기 흔적과 맞춰 봅니다. Claude 조직 내보내기에서는 대화의 `account.uuid` 를 `users.json` 의 `uuid` 와 맞춰 사람별로 나눌 수 있고, `users.json` 에 없는 UUID 를 공개 도구는 떠난 사용자("[Departed User]")로 표시합니다[12]. 그러니 조직 내보내기에서는 `users.json` 을 빼지 말고 함께 보존합니다.

기기 기록에는 있는데 내보내기에는 없는 대화는 서버에서 지워졌거나 보관 기간이 지난 것일 수 있습니다. 반대로 내보내기에만 있는 대화는 다른 기기나 웹에서 한 대화이거나, 기기 기록이 자동 정리된 것일 수 있습니다. 차이가 보이면 어느 쪽 설명이 맞는지 보관 설정과 삭제 흔적으로 따져 봅니다. 비공식 수집 도구로 받은 파일은 도구가 고른 가지와 필드만 담고 있어서, 그 파일에 없는 메시지를 서버에 없었다고 쓰지 않습니다.

## 참고 문헌

1. Claude Help Center, "How can I export my Claude data?". https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-data (2026-09-25 열람)
2. Google, "Gemini Apps Privacy Hub". https://support.google.com/gemini/answer/13594961?hl=en (2026-09-25 열람)
3. Claude Code 문서, "Data usage". https://code.claude.com/docs/en/data-usage (2026-09-25 열람)
4. D. Brezinski, T. Killalea, "RFC 3227 — Guidelines for Evidence Collection and Archiving (BCP 55)", 2002-02. https://www.rfc-editor.org/rfc/rfc3227
5. GitHub, mohamed-chs/convoviz, README.md — https://github.com/mohamed-chs/convoviz (2026-09-25 열람)
6. GitHub, kninami/chatgptForensics, README.md — https://github.com/kninami/chatgptForensics (2026-09-25 열람)
7. GitHub, ProtonMail/WebClients, applications/lumo/src/app/features/aiPaperTrail/parsers/zipConversations.ts — https://github.com/ProtonMail/WebClients (2026-09-25 열람)
8. GitHub, loucdg/chatgpt-forensic-exporter, README.md, chatgpt_export_conversations_api.py, chatgpt_export_projects_api.py, verify.py (마지막 커밋 2026-03-28) — https://github.com/loucdg/chatgpt-forensic-exporter (2026-09-25 열람)
9. GitHub, abrignoni/RLEAPP, scripts/artifacts/chatgpt.py(검증 2024-07-09), scripts/artifacts/chatGPTaccountInfo.py(최종 수정 2026-07-09) — https://github.com/abrignoni/RLEAPP (2026-09-25 열람)
10. GitHub, lordjabez/claude-export-viewer, src/claude_export_viewer/loader.py (마지막 커밋 2026-02-12) — https://github.com/lordjabez/claude-export-viewer (2026-09-25 열람)
11. GitHub, EmpiricaAI/empirica, docs/reference/api/CLAUDE_AI_PARSER.md — https://github.com/EmpiricaAI/empirica (2026-09-25 열람)
12. GitHub, ukogan/claude-migration-assistant, js/processing/admin-reader.js (마지막 커밋 2026-02-13) — https://github.com/ukogan/claude-migration-assistant (2026-09-25 열람)
13. GitHub, Coryrichter94/gemini-to-obsidian, README.md, gemini_to_obsidian.py (마지막 커밋 2025-10-02) — https://github.com/Coryrichter94/gemini-to-obsidian (2026-09-25 열람)
14. GitHub, silver-gr/AI-Conversation-Toolkit, docs/gemini-extractor.md, scripts/gemini_extractor.py (마지막 커밋 2026-07-16) — https://github.com/silver-gr/AI-Conversation-Toolkit (2026-09-25 열람)
15. GitHub, joshuaswarren/remnic, packages/import-gemini/src/parser.ts (파일 마지막 수정 2026-06-05) — https://github.com/joshuaswarren/remnic (2026-09-25 열람)
16. GitHub, MaxAnkum/copilot-history-memory-mart, README.md (마지막 커밋 2025-09-21) — https://github.com/MaxAnkum/copilot-history-memory-mart (2026-09-25 열람)
17. GitHub, mohamed-chs/convoviz, docs/dev/chatgpt-spec.md "ChatGPT User Data Export Specification (Unofficial)" v3.0(2026-02-05) — https://github.com/mohamed-chs/convoviz/blob/main/docs/dev/chatgpt-spec.md (2026-09-25 열람)
