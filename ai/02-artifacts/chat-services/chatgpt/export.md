---
title: "ChatGPT 계정 데이터 내보내기"
parent: "ChatGPT"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 130
---

# 계정 데이터 내보내기 (Data Export)

ChatGPT 계정 설정의 내보내기 기능으로 받는 ZIP 파일이고, 그 안의 `conversations.json` 에 메시지마다 작성자 역할·작성 시각·본문이 들어 있어서 기기 흔적만으로는 알 수 없는 대화 내용을 확인하는 주된 길이 됩니다.

OpenAI 는 이 파일의 형식을 공개하지 않습니다. 아래 칸 이름은 공개 도구가 정리한 것이라 지금 받는 내보내기와 다를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

웹에서 프로필 이름 → Settings → Data controls → Export 순서로 들어가 "Confirm export" 를 누르면 OpenAI 가 보낸 메일로 ZIP 파일을 받습니다[1][7]. 메일 링크가 열리는 기간과 Team·Enterprise 요금제에서 같은 메뉴를 쓰는지는 시기마다 다를 수 있어서, 보고서에 절차를 적을 때는 그 시점의 공식 도움말에서 확인합니다.

설정 화면 말고 개인정보 포털(privacy.openai.com)에서 받는 경로도 있습니다. 이 포털에서 받은 파일은 겉 ZIP 안에 `Conversations__*-chatgpt-*.zip` 모양의 ZIP 을 한 겹 더 담고, 대화는 그 안에 있습니다[9]. 그래서 겉 ZIP 에 `conversations.json` 이 없으면 안쪽 ZIP 부터 찾아봅니다.

내보내기는 기기에 있던 파일을 모으는 것이 아니라 계정에서 받는 사본입니다. 기기에 무엇이 남았는지와는 따로 보고, 서비스마다 다른 내보내기 형식을 견준 내용은 [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md)에 있습니다. 조직 계정의 대화를 관리자 쪽에서 가져가는 경로는 이 기능과 다르고, [ChatGPT 기업용 감사 기록](../../network-enterprise/chatgpt-enterprise.md)에서 따로 봅니다.

## 위치와 버전별 차이

ZIP 안에서 확인된 파일은 아래와 같습니다. 출처 열의 번호는 그 파일을 적은 자료이고, 자료에 적힌 시기를 함께 붙였습니다.

| 파일·폴더 | 담긴 것 | 출처 |
|---|---|---|
| `conversations.json` | 대화 전체. 대화마다 메시지 나무(`mapping`) | [3] 2026-02 판, [5] 2024-07-09 검증 |
| `conversations-000.json` 처럼 번호 붙은 파일 | 대화를 여러 파일로 나눈 형식 | [4] 2026-02-23 커밋, [9] 2026-09-09 커밋 |
| `user.json` | 계정 ID, 이메일, 유료 요금제 여부, 전화번호 | [3], [6] |
| `message_feedback.json` | 답변에 준 좋아요·싫어요 평가 | [3], [5] |
| `shared_conversations.json` | 공유 링크를 만든 대화 | [3], [5] |
| `chat.html` | 오프라인으로 여는 HTML 보기 화면 | [3] |
| `group_chats.json`, `shopping.json`, `sora.json` | 그룹 채팅, 쇼핑, Sora 동영상 기능 자료. 비어 있는 일이 많음 | [3] 2025 이후 관찰 |
| `model_comparisons.json` | 답변이 더 나은지 묻는 기능("Is this response better or worse?")의 자료 | [3] |
| `textdocs/` | Canvas 문서를 한 파일씩 담은 JSON | [3] |
| `dalle-generations/` | 생성 이미지(`file-*-{uuid}.webp`) | [3] |
| `user-{user_id}/` | 그 밖의 생성 이미지(PNG) | [3] 2025 이후 관찰 |
| 맨 위의 `file-*` | 사용자가 올린 파일(원래 확장자) | [3] |

이미지가 들어 있는지는 출처끼리 다릅니다. convoviz 개발 문서(2026-02 판)는 위 표처럼 생성 이미지와 올린 파일이 들어 있다고 적었고[3], chatgpt-forensic-exporter 설명서(2026-03)는 공식 내보내기가 24~48시간 걸리고 JSON 하나로 오며 이미지가 빠진다고 적었습니다[10]. 그래서 받은 ZIP 에 이미지 폴더가 있는지는 검체에서 직접 확인하고, 보고서에는 내보낸 날짜와 함께 적습니다.

형식은 공지 없이 바뀝니다. Canvas 용 `textdocs` 가 더해졌고 이미지 포인터 형식도 바뀌었습니다[3]. 2026-07 무렵부터는 일부 메시지에 `status` 와 `weight` 가 빠집니다[2].

## 구조

### 대화 한 건

`conversations.json` 은 대화를 늘어놓은 배열이고, `conversations` 열쇠 아래에 배열을 둔 객체 모양도 있습니다[3]. 대화 한 건의 칸은 아래와 같습니다.

| 칸 | 뜻 | 출처 |
|---|---|---|
| `id` | 대화 ID | [3], [5] |
| `conversation_id` | 대화 ID. `id` 와 같은 값인 일이 많음 | [3], [7] |
| `title` | 대화 제목 | [3], [5] |
| `create_time`, `update_time` | 만든 시각, 마지막 활동 시각 | [3], [5] |
| `current_node` | 화면에 보이던 가지의 마지막 노드 ID | [3] |
| `mapping` | 노드 ID 를 열쇠로 한 메시지 나무 | [3], [5] |
| `moderation_results` | 검토 결과 | [3], [5] |
| `plugin_ids` | 쓴 플러그인 | [5] |
| `gizmo_id`, `gizmo_type` | 맞춤 GPT·프로젝트 ID 와 종류 | [3], [5] |
| `is_archived`, `is_starred`, `pinned_time` | 보관, 별표, 고정한 시각 | [3], [5] |
| `default_model_slug`, `model_slug` | 대화에 쓴 모델 | [3] |
| `voice` | 음성 모드에서 고른 목소리 | [3] |
| `is_do_not_remember`, `memory_scope` | 메모리 학습에서 뺀 대화인지, 메모리 범위 | [3] |
| `safe_urls`, `blocked_urls` | 주소 목록(`safe_urls` 는 설명 없이 이름만 적힘), 이 대화에서 막힌 주소 목록 | [3] |

`gizmo_id` 가 `g-p-` 로 시작하면 프로젝트이고, 나머지는 맞춤 GPT 입니다[10]. 그래서 `gizmo_id` 앞머리로 이 대화가 프로젝트에 속했는지, 맞춤 GPT 로 한 대화인지 가를 수 있습니다.

### 노드와 가지

`mapping` 의 노드마다 `parent`, `children`, `message` 가 있어서 메시지가 부모·자식으로 이어진 나무 모양이 됩니다[3]. 맨 위 노드는 `parent` 가 `null` 이고 `message` 도 `null` 인 일이 많습니다. 답변을 다시 만들거나 질문을 고치면 한 노드에 자식이 여럿 생기고, `current_node` 에서 부모를 따라 올라간 길이 화면에 보이던 대화입니다[3]. 그래서 화면에 보이지 않던 이전 답변이나 고치기 전 질문이 다른 가지에 남아 있을 수 있습니다. `mapping` 은 순서가 없는 사전이라서, 메시지를 모은 뒤 `create_time` 으로 다시 정렬해야 순서가 섭니다[8].

### 메시지

| 묶음 | 칸 이름 | 출처 |
|---|---|---|
| 메시지 | `id`, `author`, `create_time`, `update_time`, `content`, `status`, `end_turn`, `weight`, `metadata`, `recipient` | [2], [3], [5] |
| 작성자(`author`) | `role`, `name`, `metadata` | [2], [5] |
| 본문(`content`) | `content_type`, `parts`, `text`, `language`, `result`, `name`, `content`, `thoughts`, `url`, `domain`, `title` | [2], [5] |
| 부가 정보(`metadata`) | `model_slug`, `invoked_plugin`, `is_user_system_message`, `is_visually_hidden_from_conversation`, `user_context_message_data`, `voice_mode_message`, `citations`, `search_result_groups`, `_cite_metadata`, `attachments` | [2], [3], [5], [7] |

`author.role` 에는 `system`, `user`, `assistant`, `tool` 이 들어가서 사용자가 쓴 메시지, 답변, 도구 결과를 가를 수 있고[3], `function` 이 들어가기도 합니다[2]. 도구 메시지는 `author.name` 에 도구 이름이 들어가고, `dalle.text2im`(이미지 생성), `python`(코드 실행), `bio`(메모리), `web.search`·`web.run`(웹 검색), `canmore.*`(Canvas) 같은 이름이 있습니다[3]. 답변이 도구를 부를 때는 `recipient` 에 도구 이름이 들어가고, 사용자에게 보이는 답변은 `all` 입니다[3].

`content.content_type` 은 본문 종류이고, 값에는 `text`, `multimodal_text`, `code`, `execution_output`, `sonic_webpage`(웹 검색으로 긁어 온 쪽 본문), `system_error`, `reasoning_recap`, `thoughts`, `tether_quote`, `tether_browsing_display` 가 있습니다[3]. 본문은 대개 `content.parts` 에 있는데, 이 배열에는 글자열과 객체가 섞여 들어갑니다. 객체는 이미지 참조 같은 것이라서 본문은 글자열만 골라 읽습니다[8].

사용자 지정 지침 (custom instructions) 은 `metadata.is_user_system_message` 가 붙은 메시지이고[3], 실제 지침 글은 `metadata.user_context_message_data` 의 `about_user_message`(사용자에 대해 적은 글)와 `about_model_message`(답변 방식에 대해 적은 글)에 들어 있습니다[5]. 음성 모드로 주고받은 메시지에는 `metadata.voice_mode_message` 가 붙고[5], 음성 기능의 흔적은 [음성 대화 기능](../../generative-media/voice-mode.md)에서 함께 봅니다.

### 첨부·이미지·인용

올린 파일은 `metadata.attachments[]` 에 `id`, `mime_type`, `name`, `size` 로 남습니다[7]. 이미지는 `multimodal_text` 본문의 `parts` 안에 `content_type: "image_asset_pointer"` 객체로 들어가고, `asset_pointer`, `size_bytes`, `width`, `height` 와 생성 이미지면 `metadata.dalle.prompt` 가 붙습니다[3]. 이미지 포인터는 예전에는 `file-service://` 로, 2026-02 무렵에는 `sediment://` 로 시작합니다[3]. 포인터 뒤의 파일 ID 가 ZIP 안 `file-*` 파일 이름과 어떻게 이어지는지는 검체에서 맞춰 보고, 생성 이미지 전반은 [Midjourney와 이미지 생성 서비스](../../generative-media/image-generation.md)에서 봅니다.

웹 인용은 형식이 두 가지입니다. 하나는 `metadata._cite_metadata.metadata_list[]` 의 `url`, `title`, `text` 이고[7], 요즘 형식은 `citations` 에 `start_ix`, `end_ix` 로 본문 위치를 가리킵니다[3]. 프롬프트·첨부·생성물을 서로 가려 읽는 일반 방법은 [프롬프트·첨부·생성물 구분하기](../../../01-foundations/concepts/prompt-attachment-output.md)에 있습니다.

### 부속 파일

| 파일 | 칸 | 출처 |
|---|---|---|
| `user.json` | `id`, `email`, `chatgpt_plus_user`, `phone_number` | [3], [6] |
| `shared_conversations.json` | `id`(공유 ID), `conversation_id`, `title`, `is_anonymous` | [5] |
| `message_feedback.json` | `create_time`, `user_id`, `id`, `conversation_id`, `rating`, `workspace_id`, `content`, `storage_protocol` | [5] |

`message_feedback.json` 의 `id` 는 메시지 ID 입니다[5]. `shared_conversations.json` 의 `conversation_id` 와 `message_feedback.json` 의 `conversation_id` 로 `conversations.json` 의 대화를 찾아 이을 수 있습니다.

### 만든 예시

아래는 위 칸 이름으로 대화 한 건을 줄여 흉내 낸 만든 예시이고, ID·시각·본문은 모두 가짜입니다.

```json
[
  {
    "id": "c0ffee00-0000-4000-8000-000000000001",
    "title": "도토리 일정",
    "create_time": 1700000000.123,
    "update_time": 1700000300.456,
    "current_node": "node-0003",
    "gizmo_id": "g-p-00000000000000000000000000000000",
    "mapping": {
      "node-0002": {
        "id": "node-0002",
        "parent": "node-0001",
        "children": ["node-0003"],
        "message": {
          "id": "node-0002",
          "author": { "role": "user", "name": null, "metadata": { } },
          "create_time": 1700000000.789,
          "content": { "content_type": "text", "parts": ["가짜 프로젝트 도토리 일정 정리해 줘"] },
          "status": "finished_successfully",
          "metadata": { "attachments": [ ] },
          "recipient": "all"
        }
      }
    }
  }
]
```

## 증거로서 의미

**증명하는 것.** `conversations.json` 에 대화가 있으면 내보낸 때 그 계정에 그 대화가 남아 있었다고 쓸 수 있고, `author.role` 로 계정 쪽 입력과 답변을 나눠 적을 수 있습니다. `metadata.attachments` 가 있으면 그 메시지에 그 이름의 파일이 첨부된 기록이 있다고 쓸 수 있고, `user_context_message_data` 가 있으면 그 계정에 그런 사용자 지정 지침이 설정돼 있었다고 쓸 수 있습니다. `shared_conversations.json` 에 대화가 있으면 그 대화로 공유 링크를 만든 기록이 있다고 쓸 수 있습니다. 기기에서 보관 파일이 나오면 그 파일이 그 기기에 저장돼 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** 보관 파일에 없는 대화를 처음부터 없었다고 쓸 수는 없는데, 사용자가 지웠거나 임시 채팅을 썼을 수 있기 때문입니다. 지운 대화는 받을 수 없습니다[10]. 지운 대화와 임시 채팅을 서버에 얼마나 두는지는 조사 시점의 OpenAI 공식 도움말에서 확인하고, 보관 설정의 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

계정 기록은 그 계정으로 로그인한 누군가의 활동입니다. `user.json` 의 이메일과 전화번호는 계정 주인을 가리키지만 실제로 누가 입력했는지는 말해 주지 않아서, 기기 흔적과 함께 따집니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 이 두 칸은 개인정보라서 보고서에서는 필요한 만큼만 적고 나머지는 가립니다. 기기에서 찾은 보관 파일은 JSON 이라 누구든 고칠 수 있어서, 원본인지는 받은 경로와 파일 시각을 함께 봅니다.

## 시각 해석

| 칸 | 형식 | 기준 | 출처 |
|---|---|---|---|
| 대화 `create_time`, `update_time` | 소수점이 붙은 유닉스 초 | UTC | [3], [5] |
| 메시지 `create_time`, `update_time` | 소수점이 붙은 유닉스 초. 값이 `null` 인 메시지도 있음 | UTC | [3], [5], [8] |
| 대화 `pinned_time` | 유닉스 초 | UTC | [3] |
| `message_feedback.json` 의 `create_time` | ISO-8601 글자열 | 글자열에 붙은 시간대 표시를 따름 | [5] |

유닉스 초는 1970-01-01 UTC 부터 센 초라서 기준이 UTC 입니다. 대화·메시지 시각은 유닉스 초이고, 피드백 시각은 ISO-8601 입니다[5]. RLEAPP 는 피드백 시각에 시간대 표시가 없으면 UTC 로 두기 때문에, 원본 글자열 끝에 `Z` 나 `+00:00` 이 붙었는지 먼저 봅니다. 같은 ZIP 안에서도 파일마다 시각 형식이 달라서, 한 줄로 세우기 전에 형식을 맞춥니다.

대화의 `update_time` 은 마지막 활동 시각이라서[3], 대화를 처음 연 때가 아니라 마지막으로 무엇이 바뀐 때에 가깝습니다. 알고 있는 대화 시각 하나와 맞춰 본 다음 보고서에 씁니다.

보관 파일 자체의 시각은 따로 봅니다. ZIP 파일의 파일 시스템 시각은 내려받거나 옮긴 때에 따라 바뀌어서 내보내기를 요청한 시각이나 대화 시각과 다릅니다. 기기 흔적과 보관 파일 안의 시각을 시간순으로 합치는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)을 봅니다.

## 함정과 한계

**도구가 바꾼 시각.** kninami 도구는 유닉스 초를 `datetime.fromtimestamp()` 로 바꾸는데[7], 이 함수는 분석 PC 의 현지 시각을 돌려줍니다. 그래서 이 도구의 엑셀 결과를 그대로 옮기면 분석 PC 의 시간대가 섞입니다. 도구 결과의 시각은 원본 JSON 의 숫자와 한 번 맞춰 봅니다.

**도구가 숨긴 메시지.** 보기 도구는 화면에 안 보이던 메시지를 뺍니다. convoviz 개발 문서의 숨김 규칙은 `is_visually_hidden_from_conversation` 이 붙은 메시지, 사용자 지정 지침이 아닌 `system` 메시지, `execution_output`·`tether_quote`·`multimodal_text` 가 아닌 `tool` 메시지, `all` 이 아닌 곳으로 보낸 답변, 생각 과정(`thoughts`, `reasoning_recap`)과 검색 상태 표시(`tether_browsing_display`)를 뺍니다[3]. 원본 JSON 에는 이 메시지들이 남아 있어서, 도구 결과에 없다고 파일에 없는 것이 아닙니다.

**도구가 따르는 가지.** chatgpt-forensic-exporter 설명서는 고친 가지(edit branches)까지 뽑는다고 적었지만, 대화 추출 코드는 `current_node` 에서 부모를 따라 올라간 가지만 담습니다[10]. convoviz 개발 문서의 예시 코드도 같은 방식입니다[3]. 다른 가지에 남은 메시지는 원본 `mapping` 에서 따로 봅니다.

**칸 이름의 흔들림.** 대화 ID 칸 이름을 RLEAPP 는 `id` 로[5], kninami 는 `conversation_id` 로 읽습니다[7]. 칸이 하나 없다고 파일이 손상됐거나 고친 것이라고 바로 보지 않고, 내보낸 날짜와 함께 판단합니다. 도구가 시험한 판도 다릅니다. RLEAPP 파서는 2024-07-09 에 마지막으로 검증했다고 적었고[5], `user.json` 파서는 2026-07-09 에 고쳤습니다[6]. 그 뒤에 바뀐 칸은 도구 결과에 안 나올 수 있어서, 도구 결과보다 원본 JSON 을 먼저 확인합니다.

**공식 내보내기가 아닌 파일.** 기기에서 발견한 대화 파일이 모두 공식 내보내기에서 나온 것은 아닙니다. 브라우저 사용자 스크립트로 대화를 하나씩 파일로 뽑은 경우는 [웹 브라우저](web.md) 페이지에서 다룹니다. chatgpt-forensic-exporter 같은 도구는 로그인한 브라우저 세션을 빌려 공개되지 않은 서버 API 에서 대화, 프로젝트, 생성 이미지를 받습니다[10]. 이 도구가 만든 대화 JSON 은 `messages` 배열에 `role`, `text`, `create_time` 을 담고 수집 시각 `scraped_at_utc` 를 붙인 자체 형식이라서 공식 `conversations.json` 과 모양이 다릅니다. 파일 이름과 형식이 공식 보관 파일과 같은지부터 가립니다.

**수집 권한.** 내보내기는 계정 주인이 로그인해서 요청하는 기능이라, 조사에 쓰려면 법적 절차나 당사자 동의 안에서만 계정에 접근합니다. 위와 같은 비공식 API 수집 도구는 OpenAI 가 지원하지 않는 주소를 쓰고, 주소가 예고 없이 바뀔 수 있습니다[10]. 이런 도구를 쓸 수 있는지는 수집 권한의 범위와 서비스 약관을 먼저 따지고, 도구가 파일마다 남기는 SHA-256 해시 목록(`*_hashes.csv`)과 수집 시각도 함께 보존합니다. 수집 순서와 받은 파일을 원본 그대로 지키는 방법은 [계정 데이터 내보내기로 수집](../../../03-techniques/acquisition/export-collection.md)에서, 세션 토큰이 남는 곳과 보고서에서 가리는 법은 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에서 다룹니다. 계정 주인의 협조를 얻을 수 없으면 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)을 검토합니다.

## 직접 분석해 보기

**헥스로 한 번.** 보관 파일을 헥스 편집기로 열어 앞머리가 ZIP 형식의 머리 글자 `50 4B 03 04`(`PK..`)로 시작하는지 확인합니다. 압축을 푼 `conversations.json` 은 맨 앞 글자가 배열을 뜻하는 `[`(`5B`)인지, 객체를 뜻하는 `{`(`7B`)인지 보면 위에 적은 두 모양 가운데 어느 쪽인지 알 수 있습니다. 이어서 `"mapping"`, `"create_time"` 같은 칸 이름을 글자로 찾아, `create_time` 뒤의 숫자가 10자리 정수에 소수점이 붙은 유닉스 초 모양인지 봅니다.

**공개 도구로 한 번.** RLEAPP 의 `chatgpt.py` 는 `conversations.json`, `shared_conversations.json`, `message_feedback.json` 을 읽어 대화 목록, 메시지, 공유, 피드백 표를 만들고, `chatGPTaccountInfo.py` 는 `user.json` 을 읽습니다[5][6]. 메시지 표에는 사용자 지정 지침과 음성 표시 칸이 따로 나옵니다. convoviz 는 MIT 라이선스의 공개 도구이고, 내보내기 ZIP 을 대화별 Markdown 파일로 바꾸고 사용 경향 그래프와 자주 쓴 낱말 그림을 만듭니다[1]. 도구 결과는 읽기 편한 사본으로만 쓰고, 보고서의 근거는 원본 `conversations.json` 에서 칸을 직접 확인해 적습니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 브라우저 방문·다운로드 기록 | 보관 파일을 받은 때, 웹 판 사용 흔적 | [웹 브라우저](web.md) |
| 앱 흔적 | 기기에서 쓴 판과 버전, 기기에 남은 대화 사본 | [Windows 앱](windows.md), [macOS 앱](macos.md), [Android 앱](android.md), [iOS 앱](ios.md) |
| 네트워크 기록 | 대화 시각 무렵의 접속 | [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) |
| 조직 감사 기록 | Team·Enterprise 계정의 관리자 쪽 기록 | [ChatGPT 기업용 감사 기록](../../network-enterprise/chatgpt-enterprise.md) |

## 실습

시험용 계정으로 가짜 대화를 만들고 내보내기를 받아 아래 질문을 풀어 봅니다.

1. ZIP 안의 파일 구성이 위 표와 같습니까? 대화가 한 파일입니까, 여러 파일로 나뉘어 있습니까? 이미지 폴더가 있습니까?
2. 알고 있는 대화 시각과 `create_time` 값을 맞춰 보면 유닉스 초(UTC)가 맞습니까? `message_feedback.json` 의 시각에는 시간대 표시가 붙어 있습니까?
3. 답변을 한 번 다시 만든 대화에서 `mapping` 의 가지는 몇 개이고, `current_node` 를 따라가면 어느 가지가 나옵니까?
4. 프로젝트 안에서 만든 대화의 `gizmo_id` 는 어떤 글자로 시작합니까?
5. 사용자 지정 지침을 넣은 뒤 대화하면 `user_context_message_data` 에 무엇이 남습니까?
6. 모든 메시지에 `status` 와 `weight` 가 있습니까?

## 참고 문헌

1. GitHub, mohamed-chs/convoviz, README.md — https://github.com/mohamed-chs/convoviz (2026-09-25 열람)
2. GitHub, mohamed-chs/convoviz, convoviz/models/message.py — https://github.com/mohamed-chs/convoviz/blob/main/convoviz/models/message.py (2026-07-07 커밋, 2026-09-25 열람)
3. GitHub, mohamed-chs/convoviz, docs/dev/chatgpt-spec.md "ChatGPT User Data Export Specification (Unofficial)" v3.0(2026-02-05) — https://github.com/mohamed-chs/convoviz/blob/main/docs/dev/chatgpt-spec.md (2026-09-25 열람)
4. GitHub, mohamed-chs/convoviz, convoviz/io/loaders.py (2026-02-23 커밋) — https://github.com/mohamed-chs/convoviz/blob/main/convoviz/io/loaders.py (2026-09-25 열람)
5. GitHub, abrignoni/RLEAPP, scripts/artifacts/chatgpt.py (작성 Evangelos Dragonas, 검증 2024-07-09) — https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/chatgpt.py (2026-09-25 열람)
6. GitHub, abrignoni/RLEAPP, scripts/artifacts/chatGPTaccountInfo.py (최종 수정 2026-07-09) — https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/chatGPTaccountInfo.py (2026-09-25 열람)
7. GitHub, kninami/chatgptForensics, README.md, parse_data.py (2024-05) — https://github.com/kninami/chatgptForensics (2026-09-25 열람)
8. GitHub, ProtonMail/WebClients, applications/lumo/src/app/features/aiPaperTrail/parsers/chatgpt.ts — https://github.com/ProtonMail/WebClients (2026-09-25 열람)
9. GitHub, ProtonMail/WebClients, applications/lumo/src/app/features/aiPaperTrail/parsers/zipConversations.ts (2026-09-09 커밋) — https://github.com/ProtonMail/WebClients (2026-09-25 열람)
10. GitHub, loucdg/chatgpt-forensic-exporter, README.md, chatgpt_export_projects_api.py, chatgpt_export_conversations_api.py, chatgpt_download_images.py, verify.py (2026-03) — https://github.com/loucdg/chatgpt-forensic-exporter (2026-09-25 열람)
