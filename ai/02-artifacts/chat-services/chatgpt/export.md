---
title: "ChatGPT 계정 데이터 내보내기"
parent: "ChatGPT"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 130
---

# 계정 데이터 내보내기 (Data Export)

ChatGPT 계정 설정의 내보내기 기능은 계정에 남은 대화를 ZIP 파일로 받는 기능이고, 그 안의 `conversations.json` 에 메시지의 작성자 역할·작성 시각·본문이 들어 있어서 기기 흔적만으로는 알 수 없는 대화 내용을 확인하는 주된 길이 됩니다.

> 확인 날짜: 2026-09-25. 공개 도구 convoviz 의 설명서, 메시지 모델 소스, 개발 문서(비공식 내보내기 형식 설명, 2026-02 판)를 바탕으로 썼습니다. OpenAI 는 이 파일의 형식을 공개하지 않아서 아래 파일 이름과 칸 이름은 모두 공개 도구 쪽이 실제 내보내기를 보고 정리한 관찰이고 공식 형식 설명이 아닙니다.

## 무엇을 받나 · 왜 생기나

convoviz 설명서는 웹에서 프로필 이름 → Settings → Data controls → Export 순서로 요청하고 "Confirm export" 를 누르면 OpenAI 가 보낸 메일로 ZIP 파일을 받는다고 적었습니다. 대화를 담은 주 데이터 파일은 `conversations.json` 이고, convoviz 개발 문서는 그 밖에 `user.json`(계정 정보), `chat.html`(오프라인으로 보는 HTML), `message_feedback.json`(좋아요·싫어요 평가), `shared_conversations.json`(공유 링크를 만든 대화), 이미지 생성 결과와 사용자가 올린 파일이 함께 들어 있다고 정리했습니다(2026-02 무렵까지의 관찰). 같은 도구의 불러오기 코드는 대화가 `conversations-000.json` 처럼 여러 파일로 나뉜 형식도 읽도록 만들어져 있어서, 파일 구성은 내보낸 시기마다 다를 수 있습니다. 메일 링크가 열리는 기간과 Team·Enterprise 요금제에서 같은 기능을 쓰는지는 시기마다 다를 수 있으므로, 절차를 조사 보고서에 적을 때는 그 시점의 공식 도움말에서 확인합니다.

내보내기는 기기에 있던 파일을 모으는 것이 아니라 계정에 묶인 서버 쪽 데이터를 사본으로 받는 방식입니다. 그래서 기기에서 앱을 지웠거나 기기에 캐시가 없어도, 계정에 대화가 남아 있다면 보관 파일에 나올 수 있습니다. 이 해석은 서버 쪽 사본이라는 성격에서 나온 일반 원리이고 OpenAI 문서로 확인한 내용은 아닙니다. 서비스마다 다른 내보내기 형식을 견준 내용은 [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md)에서 다룹니다.

조직 계정의 대화를 관리자 쪽에서 가져가는 경로는 이 기능과 다르고, [ChatGPT 기업용 감사 기록](../../network-enterprise/chatgpt-enterprise.md)에서 따로 봅니다.

## 구조

convoviz 설명서는 내보낸 대화에 작성자 역할, 작성 시각(`create_time`), 본문 조각(본문에 섞인 미디어 포함), 웹 검색 인용, Canvas 문서, 사용자 지정 지침 (custom instructions) 이 들어 있다고 적었습니다. 메시지 하나를 이루는 칸은 convoviz 의 메시지 모델에서 아래처럼 확인할 수 있습니다.

| 묶음 | 칸 이름 |
|---|---|
| 메시지 | `id`, `author`, `create_time`, `update_time`, `content`, `status`, `end_turn`, `weight`, `metadata`, `recipient` |
| 작성자(`author`) | `role`, `name`, `metadata` |
| 본문(`content`) | `content_type`, `parts`, `text`, `result`, `name`, `content`, `thoughts`, `url`, `domain`, `title` |
| 부가 정보(`metadata`) | `model_slug`, `invoked_plugin`, `is_user_system_message`, `is_visually_hidden_from_conversation`, `user_context_message_data`, `citations`, `search_result_groups`, `attachments` |

convoviz 개발 문서에 따르면 `author.role` 에는 `system`, `user`, `assistant`, `tool` 같은 값이 들어가서 사용자가 쓴 메시지와 답변, 도구 결과를 가를 수 있고, `content.content_type` 에는 `text`, `multimodal_text`, `code`, `execution_output`, `thoughts` 같은 본문 종류가 들어갑니다. 같은 문서는 `metadata.model_slug` 를 답변을 만든 모델, `is_user_system_message` 를 사용자 지정 지침, `citations` 를 인용, `attachments` 를 첨부 정보로 설명합니다. 이 뜻풀이도 도구 쪽 관찰이라서, 보고서에는 실제 파일에서 값을 확인한 범위만 씁니다. 프롬프트·첨부·생성물을 서로 가려 읽는 일반 방법은 [프롬프트·첨부·생성물 구분하기](../../../01-foundations/concepts/prompt-attachment-output.md)에 있습니다.

convoviz 개발 문서는 `conversations.json` 을 대화 목록으로 보고, 대화 한 건에 `title`, `create_time`, `update_time`, `current_node`, `mapping` 칸이 있다고 적었습니다. `mapping` 은 노드 ID 를 열쇠로 한 사전이고, 노드마다 `parent`, `children`, `message` 가 있어서 메시지가 부모·자식으로 이어진 나무 모양이 됩니다. 답변을 다시 만들거나 질문을 고치면 한 노드에 자식이 여럿 생기고, `current_node` 에서 부모를 따라 올라간 길이 화면에 보이던 대화입니다. 그래서 화면에 보이지 않던 이전 답변이나 고치기 전 질문이 다른 가지에 남아 있을 수 있습니다(도구 쪽 관찰, 공식 확인 아님).

아래는 위 칸 이름으로 노드 하나를 흉내 낸 만든 예시이고, ID·시각·본문은 모두 가짜입니다.

```json
"node-0002": {
  "id": "node-0002",
  "parent": "node-0001",
  "children": ["node-0003"],
  "message": {
    "id": "node-0002",
    "author": { "role": "user", "name": null, "metadata": { } },
    "create_time": 1700000000.123,
    "content": { "content_type": "text", "parts": ["가짜 프로젝트 도토리 일정 정리해 줘"] },
    "status": "finished_successfully",
    "metadata": { "attachments": [ ] },
    "recipient": "all"
  }
}
```

convoviz 소스에는 "ChatGPT exports from ~July 2026 omit status/weight on some messages" 라는 주석이 있습니다. 2026-07 무렵부터 일부 메시지에 `status` 와 `weight` 가 빠졌다는 뜻이고, 내보내기 형식이 공지 없이 바뀔 수 있다는 근거가 됩니다. 그래서 칸이 없다고 파일이 손상됐거나 고친 것이라고 바로 보지 않고, 내보낸 날짜와 함께 판단합니다.

## 증거로서 의미

**증명하는 것.** `conversations.json` 에 대화가 있으면 내보낸 때 그 계정에 그 대화가 남아 있었다고 쓸 수 있고, `author.role` 로 계정 쪽 입력과 답변을 나눠 적을 수 있습니다. 기기에서 보관 파일이 나오면 그 파일이 그 기기에 저장돼 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** 보관 파일에 없는 대화를 처음부터 없었다고 쓸 수는 없는데, 사용자가 지웠거나 임시 채팅을 썼을 수 있기 때문입니다. 지운 대화와 임시 채팅을 서버에 얼마나 두는지는 조사 시점의 OpenAI 공식 도움말에서 확인하고, 보관 설정의 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에 있습니다. 계정 기록은 그 계정으로 로그인한 누군가의 활동이라서 실제로 누가 입력했는지는 기기 흔적과 함께 따집니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 기기에서 찾은 보관 파일은 JSON 이라 누구든 고칠 수 있어서, 원본인지는 받은 경로와 파일 시각을 함께 봅니다.

## 시각 해석

대화와 메시지에는 `create_time` 과 `update_time` 두 시각 칸이 있습니다. convoviz 개발 문서는 이 값을 소수점이 붙은 유닉스 시각(1970-01-01 UTC 부터 센 초)으로 적었고, 유닉스 시각이면 기준은 UTC 입니다. 대화의 `update_time` 은 그 대화에서 마지막으로 활동한 시각으로 설명돼 있습니다. 이 설명도 공개 도구 쪽 관찰이라서, 실제 파일에서 값의 모양을 먼저 보고 알고 있는 대화 시각 하나와 맞춰 본 다음 보고서에 씁니다.

보관 파일 자체의 시각은 따로 봅니다. ZIP 파일의 파일 시스템 시각은 내려받거나 옮긴 때에 따라 바뀌어서 내보내기를 요청한 시각이나 대화 시각과 다릅니다. 기기 흔적과 보관 파일 안의 시각을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)을 봅니다.

## 함정과 한계

내보내기는 계정 주인이 로그인해서 요청하는 기능이라, 조사에 쓰려면 법적 절차나 당사자 동의 안에서만 계정에 접근합니다. 수집 순서와 받은 파일을 원본 그대로 지키는 방법은 [계정 데이터 내보내기로 수집](../../../03-techniques/acquisition/export-collection.md)에서 다루고, 계정 주인의 협조를 얻을 수 없으면 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)을 검토합니다.

이 페이지의 칸 이름은 한 공개 도구의 모델에 기댄 것이고, 그 도구 소스에도 형식이 바뀐 일을 적은 주석이 있습니다. 다른 도구로 읽을 때 칸이 빠지거나 이름이 다르게 보일 수 있어서, 도구가 보여 주는 결과보다 원본 JSON 을 먼저 확인합니다.

기기에서 발견한 대화 파일이 모두 공식 내보내기에서 나온 것은 아닙니다. 브라우저 사용자 스크립트로 대화를 하나씩 파일로 뽑은 경우도 있고, 그 흔적은 [웹 브라우저](web.md) 페이지에서 다룹니다. 파일 이름과 형식이 공식 보관 파일과 같은지부터 가립니다.

## 직접 분석해 보기

**헥스로 한 번.** 보관 파일을 헥스 편집기로 열어 앞머리가 ZIP 형식의 머리 글자 `PK` 로 시작하는지 확인하고, 압축을 푼 `conversations.json` 은 앞부분에 JSON 의 괄호와 칸 이름이 읽을 수 있는 글자로 보이는지 확인합니다.

**공개 도구로 한 번.** convoviz 는 MIT 라이선스의 공개 도구이고, 내보내기 ZIP 을 대화별 Markdown 파일로 바꾸고 사용 경향 그래프와 자주 쓴 낱말 그림을 만듭니다. 변환 결과에 모든 가지가 나오는지는 도구 버전마다 다를 수 있으므로, 다른 가지에 남은 메시지는 원본 `mapping` 에서 따로 봅니다. 변환 결과는 읽기 편한 사본으로만 쓰고, 보고서의 근거는 원본 `conversations.json` 에서 칸을 직접 확인해 적습니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 브라우저 방문·다운로드 기록 | 보관 파일을 받은 때, 웹 판 사용 흔적 | [웹 브라우저](web.md) |
| 앱 흔적 | 기기에서 쓴 판과 버전 | [Windows 앱](windows.md), [macOS 앱](macos.md), [Android 앱](android.md), [iOS 앱](ios.md) |
| 네트워크 기록 | 대화 시각 무렵의 접속 | [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) |

## 실습

시험용 계정으로 가짜 대화를 만들고 내보내기를 받아 아래 질문을 풀어 봅니다.

1. ZIP 안의 파일 구성이 위에 적은 목록과 같습니까? 대화가 한 파일입니까, 여러 파일로 나뉘어 있습니까?
2. 알고 있는 대화 시각과 `create_time` 값을 맞춰 보면 유닉스 초(UTC)가 맞습니까?
3. 답변을 한 번 다시 만든 대화에서 `mapping` 의 가지는 몇 개입니까?
4. 대화 하나를 지운 뒤 다시 내보내면 그 대화가 빠집니까?
5. 모든 메시지에 `status` 와 `weight` 가 있습니까?

## 참고 문헌

1. GitHub, mohamed-chs/convoviz README — https://github.com/mohamed-chs/convoviz (2026-09-25 열람)
2. GitHub, convoviz 메시지 모델 소스(message.py) — https://raw.githubusercontent.com/mohamed-chs/convoviz/main/convoviz/models/message.py (2026-09-25 열람)
3. GitHub, convoviz 개발 문서 "ChatGPT User Data Export Specification (Unofficial)" v3.0(2026-02-05) — https://github.com/mohamed-chs/convoviz/blob/main/docs/dev/chatgpt-spec.md (2026-09-25 열람)
4. GitHub, convoviz 불러오기 소스(loaders.py) — https://github.com/mohamed-chs/convoviz/blob/main/convoviz/io/loaders.py (2026-09-25 열람)
