---
title: "Claude 계정 데이터 내보내기"
parent: "Claude"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 200
---

# 계정 데이터 내보내기 (Data Export)

Claude 의 계정 데이터 내보내기는 계정 서버에 있는 대화·프로젝트·메모리·계정 정보를 JSON 파일 묶음으로 받는 기능이고, 기기 흔적만으로는 알 수 없는 대화 본문과 첨부에서 뽑은 글, 생성물까지 확인하는 주된 길입니다.

공식 도움말은 파일 형식을 설명하지 않아서, 칸 이름은 모두 공개 도구가 쓴 이름입니다[1].

## 무엇을 받나 · 왜 생기나

개인 Free·Pro·Max 사용자는 웹이나 데스크톱 앱에서 왼쪽 아래 이니셜을 눌러 Settings 의 Privacy 절로 들어간 뒤 "Export data" 로 내보내기를 요청합니다[1]. iOS·Android 앱에는 이 기능이 없어서, 휴대전화로만 쓴 계정이라도 내보내기는 웹이나 PC 에서 요청합니다[1]. Team·Enterprise 요금제에서는 조직의 데이터를 Primary Owner 만 내보낼 수 있습니다[1]. 조직 계정의 활동을 관리자 쪽 기록으로 보는 방법은 [Claude 기업용 감사 로그](../../network-enterprise/claude-enterprise.md)에서 따로 다룹니다.

요청하면 파일을 만드는 데 시간이 조금 걸릴 수 있고, 준비가 끝나면 계정 이메일로 내려받기 링크가 옵니다[1]. 링크는 받은 뒤 24시간이 지나면 만료되고, 내려받으려면 그 계정으로 로그인해야 하며, 만료되면 다시 요청합니다[1]. 받는 자료는 대화 데이터와 사용자 계정 정보이고, 공식 파일 목록은 공개돼 있지 않습니다[1]. 내보낸 자료를 다른 개인 계정으로 가져올 수는 없고, 개인 계정을 Team·Enterprise 조직으로 옮길 때는 내보내기 없이 바로 옮깁니다[1].

내보내기는 기기에 있던 파일을 모으는 기능이 아니라, 요청한 때 계정에 있던 자료의 사본을 서버가 만들어 보내 주는 기능입니다. 그래서 보관 파일의 내용은 내보낸 시점의 계정 상태를 보여 주고, 기기에 남은 흔적과 같은지는 둘을 맞춰 봐야 압니다. 기기 쪽 흔적은 [웹 브라우저](web.md), [Windows 앱](windows.md), [macOS 앱](macos.md) 같은 판별 페이지에서 다루고, 서비스마다 다른 내보내기 형식을 견준 내용은 [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md)에 있습니다.

## 위치와 버전별 차이

받은 파일은 ZIP 입니다[1][2]. 내려받은 파일에는 `.zip` 확장자가 빠져 있을 수 있으므로[2], 확장자만 보고 거르지 말고 파일 머리로 ZIP 인지 가립니다. 기기에서 보관 파일을 찾을 때는 내려받은 위치를 먼저 봅니다. 링크를 이메일로 받아 브라우저로 내려받는 방식이라, 보관 파일이 기기에 있었다면 브라우저 다운로드 기록과 메일 기록에도 흔적이 남을 수 있습니다.

ZIP 안의 파일은 출처마다 조금씩 다르게 적었습니다. 아래 표에서 날짜는 각 도구 소스 파일의 마지막 커밋 날짜입니다.

| 파일 | 담긴 것 | 적은 출처(날짜) |
|---|---|---|
| `conversations.json` | 대화와 메시지 배열 | 모든 도구[2][3][5]~[11] |
| `users.json` | 계정 정보 | lordjabez(2026-02)[5], empirica(2026-09)[6], ukogan(2026-02)[9], la-roca(2026-09)[10] |
| `memories.json` | Claude 가 사용자에 대해 기억한 글 | lordjabez[5], empirica[6], ukogan[9], la-roca[10] |
| `projects.json` | 프로젝트 정보와 올린 문서 | lordjabez(2026-02)[5], empirica(2026-09)[6], ukogan(2026-02)[9] |
| `projects/<uuid>.json` | 프로젝트 하나에 파일 하나 | la-roca(2026-09)[10] |
| `design_chats/*.json` | 프로젝트에 묶인 디자인 대화 | la-roca(2026-09)[10] |
| `login_history.json` | 이름만 나옴(도구가 읽지 않는 파일로 적음) | la-roca(2026-09)[10] |

프로젝트가 `projects.json` 한 파일로 오는지, `projects` 폴더 아래 파일 하나씩으로 오는지는 출처끼리 다릅니다. lordjabez·ukogan 도구(2026-02)와 empirica 설명서(2026-09-23)는 앞의 모양을, la-roca 설명서(2026-09-21)는 뒤의 모양을 읽으므로, 검체에서는 ZIP 목록을 먼저 뽑아 어느 모양인지 봅니다. 대화의 메시지 배열 이름도 판마다 달라서, 예전 내보내기는 `chat_messages` 대신 `messages` 를 썼으므로 두 이름을 모두 찾아봅니다[7].

조직(Team·Enterprise) 내보내기도 같은 네 파일(`conversations.json`, `users.json`, `memories.json`, `projects.json`)로 오고, ZIP 이 아닌 JSON 파일 여러 개로 옵니다[9]. ukogan 도구는 조직 내보내기의 대화마다 `account.uuid` 가 있다고 보고, 이 칸이 없는 대화는 건너뜁니다[9].

## 구조

`conversations.json`, `users.json`, `memories.json`, `projects.json` 은 맨 위가 JSON 배열이고[5][9][10], la-roca 가 읽는 `projects/<uuid>.json` 과 `design_chats/*.json` 은 파일마다 JSON 객체 하나입니다[10]. 아래 표의 칸 이름은 도구 소스가 직접 부르는 이름이고, "도구가 읽는 방식" 은 소스에서 그 칸을 어떻게 쓰는지 옮긴 것입니다.

### 대화 (`conversations.json` 의 한 항목)

| 칸 | 도구가 읽는 방식 | 출처 |
|---|---|---|
| `uuid` | 대화 ID | [3][5][8][10] |
| `name` | 대화 제목 | [2][5][7][8][10] |
| `summary` | 대화 요약 글, 없으면 빈 문자열 | [5][10] |
| `created_at`, `updated_at` | 대화 시작과 끝 시각으로 씀 | [2][5][8][10] |
| `account.uuid` | 대화가 속한 계정 ID | [3][5][9] |
| `project_uuid` | 선택 칸. 속한 프로젝트 ID | [5] (2026-02) |
| `chat_messages` | 메시지 배열(예전 판은 `messages`) | [3][5][7][8][10] |

`project_uuid` 는 출처끼리 어긋납니다. lordjabez 모델(2026-02)은 대화에 이 칸을 선택 칸으로 두었지만[5], la-roca 설명서(2026-09)는 개인 내보내기에는 대화와 프로젝트를 잇는 칸이 없어서 대화를 프로젝트에 붙이지 않는다고 적었습니다[10]. 검체에서 이 칸이 있는지 보고, 없으면 대화 제목이나 내용으로 프로젝트 소속을 짐작하지 않습니다.

### 메시지 (`chat_messages` 의 한 항목)

| 칸 | 도구가 읽는 방식 | 출처 |
|---|---|---|
| `uuid` | 메시지 ID | [3][5][8][10] |
| `sender` | `human` 은 사용자, `assistant` 는 답변 | [3][5][7][8][10] |
| `text` | 도구 블록을 빼고 화면용으로 합친 본문 글 | [3][5][6][10] |
| `content` | 블록 배열(아래 표) | [5][6][8] |
| `created_at`, `updated_at` | 메시지 시각 | [2][5][8][10] |
| `parent_message_uuid` | 이 메시지가 이어지는 앞 메시지의 ID | [10] |
| `attachments` | 첨부 배열(아래 표) | [2][5][8][10] |
| `files` | 파일 배열(아래 표) | [2][5][10] |

`sender` 값은 `human` 과 `assistant` 두 가지입니다[5][10]. 본문은 `text` 보다 `content` 를 읽어야 합니다. `text` 는 도구 블록을 빼고 화면용으로 편 글이라 `content` 와 내용이 다를 수 있고, empirica 가 잰 메시지 654개 가운데 87개(약 13%)에서 둘이 달랐습니다[6].

### 내용 블록 (`content` 의 한 항목)

| `type` | 칸 | 출처 |
|---|---|---|
| `text` | `text`, `citations` | [5][6][8] |
| `thinking` | `thinking`, `summaries[].summary`, `cut_off`, `alternative_display_type` | [5][8] |
| `tool_use` | `id`, `name`, `input`, `message`, `integration_name`, `display_content` | [5][6] |
| `tool_result` | `tool_use_id`, `name`, `content`, `is_error`, `structured_content`, `message`, `integration_name`, `display_content` | [5][6] |
| `token_budget` | 도구가 읽는 칸 없음 | [5][8] |
| `voice_note` | 도구가 읽는 칸 없음(종류 이름만 나옴) | [8] |

블록마다 `start_timestamp`, `stop_timestamp`, `flags` 칸이 있다는 자료도 있습니다[11]. 한 자료에만 나오는 칸이므로 검체에서 있는지 확인한 뒤 씁니다.

생성물(아티팩트)은 판에 따라 담기는 곳이 다릅니다. 2024년 10월 무렵에는 `sender` 가 `assistant` 인 메시지의 `text` 안에 `antArtifact` 태그(속성 identifier·type·language·title)와 `antThinking` 태그로 들어 있었습니다[3]. 2026년 2월 무렵에는 `name` 이 `artifacts` 인 `tool_use` 블록으로 들어 있고, 그 `input` 에 `command`, `id`, `type`, `title`, `language`, `content`, `old_str`, `new_str`, `version_uuid` 가 있습니다[5]. `command` 가 비어 있으면 lordjabez 도구는 `create` 로 봅니다[5]. 그래서 `text` 만 읽는 도구로는 최근 내보내기의 아티팩트가 보이지 않을 수 있습니다.

### 첨부와 파일

| 배열 | 칸 | 출처 |
|---|---|---|
| `attachments[]` | `file_name`, `file_size`, `file_type`, `extracted_content` | [5][8][11] |
| `files[]` | `file_name` | [5] |

`extracted_content` 에는 첨부에서 뽑아낸 글이 들어 있고, agentsview 는 이 글을 `[Attachment: 파일이름]` 머리를 붙여 메시지 본문 뒤에 이어 붙입니다[8]. 파일 이름 칸은 `file_name`, `filename`, `name` 세 이름으로 나올 수 있습니다[10]. 첨부 원본 파일이 ZIP 안에 따로 들어 있는지는 ZIP 목록으로 확인합니다. 프롬프트·첨부·생성물을 서로 가려 읽는 일반 방법은 [프롬프트·첨부·생성물 구분하기](../../../01-foundations/concepts/prompt-attachment-output.md)에 있습니다.

### 계정·프로젝트·메모리

| 파일 | 칸 | 출처 |
|---|---|---|
| `users.json` | `uuid`, `full_name`, `email_address`, `verified_phone_number` | [5][9] |
| 프로젝트 | `uuid`, `name`, `description`, `is_private`, `is_starter_project`, `prompt_template`, `created_at`, `updated_at`, `creator`(안에 `uuid`) | [5][9][10] |
| 프로젝트 문서 | `docs[].uuid`, `docs[].filename`, `docs[].content`(la-roca 는 `file_name`, `created_at` 도 받음) | [5][10] |
| `memories.json`(지금 모양) | `account_uuid`, `conversations_memory`(글), `project_memories`(프로젝트 UUID → 글), `memory_files[]`(`content`, `path`, `updated_at`) | [9][10] |
| `memories.json`(예전 모양) | 항목마다 글 하나. 문자열이거나, `uuid`(또는 `id`)와 글 칸(`memory`·`content`·`text` 가운데 하나), `created_at`, `updated_at` 을 담은 객체 | [6][10] |
| `design_chats/*.json` | `uuid`, `title`, `created_at`, `updated_at`, `project`(`uuid`, `name`), `messages[]`(`uuid`, `role`, `created_at`, `content`) | [10] |

메모리 파일은 모양이 두 가지입니다. `conversations_memory`·`project_memories`·`memory_files` 가운데 하나가 있으면 지금 모양이고, 없으면 예전 모양입니다[10]. empirica 설명서의 예는 `content` 와 `created_at` 만 있는 예전 모양입니다[6]. lordjabez 모델은 `project_memories` 와 `account_uuid` 만 읽습니다[5].

### 만든 예시

아래는 위 칸 이름으로 대화 한 건을 흉내 낸 만든 예시이고, ID·시각·글은 모두 지어낸 값입니다. 실제 파일에는 칸이 더 있을 수 있습니다.

```json
[
  {
    "uuid": "00000000-0000-4000-8000-00000000c001",
    "name": "가짜 프로젝트 도토리 일정",
    "summary": "",
    "created_at": "2026-03-02T01:15:07.123456Z",
    "updated_at": "2026-03-02T01:16:40.654321Z",
    "account": { "uuid": "00000000-0000-4000-8000-00000000a001" },
    "chat_messages": [
      {
        "uuid": "00000000-0000-4000-8000-00000000b001",
        "sender": "human",
        "text": "도토리 일정표를 만들어 줘",
        "content": [{ "type": "text", "text": "도토리 일정표를 만들어 줘" }],
        "created_at": "2026-03-02T01:15:07.123456Z",
        "attachments": [
          { "file_name": "가짜-일정.txt", "file_size": 42, "file_type": "txt",
            "extracted_content": "월: 회의 / 화: 발표" }
        ],
        "files": []
      },
      {
        "uuid": "00000000-0000-4000-8000-00000000b002",
        "parent_message_uuid": "00000000-0000-4000-8000-00000000b001",
        "sender": "assistant",
        "text": "표로 정리했습니다.",
        "content": [
          { "type": "text", "text": "표로 정리했습니다." },
          { "type": "tool_use", "name": "artifacts",
            "input": { "command": "create", "id": "dotori-table", "type": "text/markdown",
                       "title": "도토리 일정", "content": "| 요일 | 일 |" } }
        ],
        "created_at": "2026-03-02T01:15:20.000000Z",
        "attachments": [],
        "files": []
      }
    ]
  }
]
```

이 예시에서 `text` 칸만 읽으면 아티팩트 블록이 보이지 않는다는 점을 눈여겨봅니다.

## 증거로서 의미

**증명하는 것.** `conversations.json` 에 대화가 있으면 내보낸 때 그 계정에 그 대화가 남아 있었다고 쓸 수 있고, `sender` 로 사용자 입력과 답변을 나눠 적을 수 있습니다. `attachments[].extracted_content` 가 있으면 그 글이 대화에 첨부로 들어갔다고 쓸 수 있는데, 이 칸은 뽑아낸 글이라 원본 파일 자체와 같다고 쓰지는 않습니다. `tool_use`·`tool_result` 블록은 그 답변을 만드는 동안 도구를 부른 기록이고, `memories.json` 과 프로젝트 문서의 `docs[].content` 는 계정에 저장된 메모리 글과 프로젝트에 올린 문서 본문을 보여 줍니다.

조직 내보내기에서는 대화의 `account.uuid` 를 `users.json` 의 `uuid` 와 맞춰 사람별로 대화를 나눌 수 있고, 메모리는 `account_uuid`, 프로젝트는 `creator.uuid` 로 같은 사람에게 묶습니다[9]. ukogan 도구는 대화에는 있는데 `users.json` 에 없는 UUID 를 "[Departed User]"(떠난 사용자)로 표시합니다[9]. 그 사람이 실제로 조직을 떠났는지는 조직의 인사·계정 기록으로 확인합니다.

기기와 계정을 이을 때는 Windows 앱 `config.json` 의 `lastKnownAccountUuid`(Windows 11 기준, [Windows 앱](windows.md) 참고)와 대화의 `account.uuid` 를 맞춰 봅니다. 두 값이 같은 모양의 ID 인지부터 실제 값으로 보고 맞춥니다. 기기에서 보관 파일이 나오면 그 파일이 그 기기에 저장돼 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** 보관 파일에 없는 대화를 처음부터 없었다고 쓸 수는 없습니다. 사용자가 지운 대화는 대화 목록에서 바로 사라지고 서버 저장소에서는 30일 안에 지워집니다[4]. 지운 뒤 30일 사이의 내보내기와 시크릿(Incognito) 대화가 보관 파일에 들어가는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 보관 기간 전체는 [Claude](index.md) 허브에, 보관 설정의 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

계정 기록은 그 계정으로 로그인한 누군가의 활동이라, 실제로 누가 입력했는지는 기기 흔적과 함께 따집니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 기기에서 찾은 보관 파일은 JSON 이라 누구든 고칠 수 있어서, 원본인지는 받은 경로와 파일 시각을 함께 봅니다.

## 시각 해석

시각 칸은 ISO 8601(RFC 3339) 문자열입니다[6][8][11]. agentsview 는 대화의 `created_at`·`updated_at` 을 나노초까지 받는 RFC 3339 형식으로 풀고, 풀리지 않으면 가져오기 전체를 오류로 멈춥니다[8]. 값은 `2024-07-18T21:23:35.731874Z`[11], `2026-01-15T10:30:00Z`[6] 처럼 끝에 `Z` 가 붙고, `Z` 는 UTC 라는 표시입니다. 소수점 아래 자릿수는 예마다 다르므로 자릿수를 가정하지 말고 검체에서 값의 모양을 먼저 봅니다.

대화의 `updated_at` 은 마지막 메시지 시각이라는 설명이 있습니다[11]. 한 자료에만 나오는 설명이므로, 마지막 메시지의 `created_at` 과 견주어 보고 씁니다. la-roca 는 대화의 `created_at`·`updated_at` 을 시작과 끝으로 보고 둘 사이를 대화 길이로 계산합니다[10].

메시지 순서는 배열 순서만 믿지 않습니다. 메시지에 `parent_message_uuid` 가 있어서 한 사용자 메시지에 답변이 여러 개 달리는 가지가 생길 수 있고, la-roca 는 이 칸으로 질문과 답을 짝지은 뒤 시각 순으로 늘어놓으며 다른 답변은 가지를 합치지 않고 따로 둡니다[10].

보관 파일 자체의 시각은 따로 봅니다. ZIP 파일의 파일 시스템 시각은 내려받거나 옮긴 때에 따라 바뀌어서 대화 시각과 다르고, 링크는 받은 뒤 24시간이 지나면 만료되므로[1] 공식 링크로 내려받은 기록이라면 그 시각은 링크 메일을 받은 뒤 24시간 안에 들어갑니다. 메일 도착 시각과 다운로드 기록을 함께 보면 내보내기를 요청한 무렵을 좁힐 수 있습니다. 기기 흔적과 보관 파일 안의 시각을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)을 봅니다.

## 함정과 한계

도구마다 본문을 읽는 방식이 달라서 같은 파일에서 다른 결과가 나옵니다. claude-to-sqlite 는 아티팩트를 `text` 안에서만 찾고[3], Proton 파서와 la-roca 는 `text` 가 비었을 때만 `content` 의 글 블록을 읽으며[7][10], agentsview 는 `content` 의 `text`·`thinking` 블록을 먼저 읽고 `tool_use`·`tool_result`·`voice_note`·`token_budget` 은 화면 내용에서 뺍니다[8]. Proton 파서는 사용자(`human`) 메시지만 뽑습니다[7]. 그래서 도구 결과에 도구 호출이나 아티팩트가 없다고 대화에 그런 일이 없었다고 쓰지 않고, 원본 JSON 의 `content` 배열을 직접 봅니다.

배열 순서대로 메시지를 늘어놓는 도구(agentsview 는 배열 번호를 순서로 씀[8])로 보면 가지가 있는 대화가 한 줄로 보입니다. 다시 생성한 답변이나 고친 질문이 섞여 있을 수 있으므로 `parent_message_uuid` 로 가지를 나눠 봅니다.

내보내기는 계정 주인이 로그인해서 요청하고 로그인해서 받는 기능이라[1], 조사에 쓰려면 법적 절차나 당사자 동의 안에서만 계정에 접근합니다. 수집 순서와 받은 파일을 원본 그대로 지키는 방법은 [계정 데이터 내보내기로 수집](../../../03-techniques/acquisition/export-collection.md)에서 다루고, 계정 주인의 협조를 얻을 수 없으면 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)을 검토합니다. `users.json` 에는 이메일과 인증된 전화번호 칸이 있으므로[5] 보고서에 옮길 때 필요한 만큼만 싣습니다.

내보내기 형식은 서비스가 공지 없이 바꿀 수 있습니다. 칸이 없거나 더 있다고 파일이 손상됐거나 고쳐졌다고 바로 보지 않고 내보낸 날짜와 함께 판단합니다. 이 페이지의 표는 2024년 10월부터 2026년 9월까지의 도구 소스를 모은 것이라, 지금 파일과는 다를 수 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 보관 파일을 헥스 편집기로 열어 확장자와 관계없이 앞 4바이트가 ZIP 로컬 파일 머리 `50 4B 03 04`(`PK..`)인지 확인하고, ZIP 목록에서 위 표의 파일과 폴더가 어느 모양으로 들어 있는지 적습니다. 압축을 푼 `conversations.json` 은 JSON 배열이라 앞머리가 아래처럼 읽을 수 있는 글자로 보입니다(만든 예시이고, 칸 순서는 실제 파일과 다를 수 있습니다).

```
00000000  5B 7B 22 75 75 69 64 22 3A 22 30 30 30 30 30 30  [{"uuid":"000000
```

**공개 도구로 한 번.** lordjabez/claude-export-viewer 는 ZIP 을 그대로 받아 네 파일을 읽고 대화·생각 과정·도구 사용·아티팩트를 HTML 로 보여 줍니다[5]. claude-to-sqlite 는 `conversations.json` 을 읽어 SQLite 파일을 만들고, 만들어지는 표는 아래 세 개입니다(2024년 10월 20일 판 기준)[2]. 도구는 대화의 `account.uuid` 를 `account_id` 로 옮기고 메시지는 칸을 그대로 넣으면서 없는 칸을 새로 만들므로(`alter=True`), 최근 내보내기에서는 표에 칸이 더 생길 수 있습니다[3]. `artifacts` 표는 `text` 안의 태그에서만 뽑으므로 최근 내보내기의 `tool_use` 아티팩트는 이 표에 들어가지 않습니다[3]. 이 표는 도구가 만든 결과물이라 원본 형식과 같지 않습니다.

| 표 | 칸 |
|---|---|
| `conversations` | uuid, name, created_at, updated_at, account_id |
| `messages` | uuid, text, sender, created_at, updated_at, attachments, files, conversation_id |
| `artifacts` | id, artifact, identifier, version, type, language, title, content, thinking, conversation_id, message_id |

만든 데이터베이스를 읽는 법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html) 페이지를 봅니다. 변환 결과는 검색하기 편한 사본으로만 쓰고, 보고서의 근거는 원본 JSON 에서 칸을 직접 확인해 적습니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 브라우저 방문·다운로드 기록 | 보관 파일을 받은 때, 웹판 사용 흔적 | [웹 브라우저](web.md) |
| 데스크톱 앱 설정 | 기기에서 마지막으로 쓴 계정 ID, 처음 실행한 때 | [Windows 앱](windows.md), [macOS 앱](macos.md) |
| 휴대전화 앱 | 기기에 설치한 흔적(내보내기는 없음) | [Android 앱](android.md), [iOS 앱](ios.md) |
| 조직 감사 로그 | 조직 계정의 활동 기록 | [Claude 기업용 감사 로그](../../network-enterprise/claude-enterprise.md) |
| 네트워크 기록 | 대화 시각 무렵의 접속 | [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) |

## 실습

공개 검체 목록(NIST CFReDS 등)에서 Claude 내보내기를 담은 검체를 먼저 찾아보고, 없으면 시험용 계정으로 가짜 대화를 만들고 내보내기를 받아 아래 질문을 풀어 봅니다.

1. ZIP 안의 프로젝트 자료는 `projects.json` 한 파일입니까, `projects` 폴더입니까? `login_history.json` 이 있다면 어떤 칸이 들어 있습니까?
2. 알고 있는 대화 시각과 `created_at` 값을 맞춰 보면 UTC 와 몇 시간 차이가 납니까?
3. 아티팩트를 만든 대화에서 `text` 와 `content` 는 어떻게 다릅니까?
4. 답변을 다시 생성한 대화에서 `parent_message_uuid` 는 어떻게 가지를 이룹니까?
5. 대화 하나를 지운 직후 다시 내보내면 그 대화가 빠집니까?

## 참고 문헌

1. Claude Help Center, "How can I export my Claude data?" — https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-data (2026-09-25 열람)
2. simonw/claude-to-sqlite, README — https://github.com/simonw/claude-to-sqlite (2026-09-25 열람)
3. simonw/claude-to-sqlite, `claude_to_sqlite/cli.py` (마지막 커밋 2024-10-21) — https://github.com/simonw/claude-to-sqlite
4. Anthropic Privacy Center, "How long do you store my data?" — https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data (2026-09-25 열람)
5. lordjabez/claude-export-viewer, `README.md`, `src/claude_export_viewer/loader.py`, `src/claude_export_viewer/models.py`, `tests/test_models.py` (마지막 커밋 2026-02-12) — https://github.com/lordjabez/claude-export-viewer
6. EmpiricaAI/empirica, `docs/reference/api/CLAUDE_AI_PARSER.md` (마지막 커밋 2026-09-23) — https://github.com/EmpiricaAI/empirica
7. ProtonMail/WebClients, `applications/lumo/src/app/features/aiPaperTrail/parsers/claude.ts` (마지막 커밋 2026-07-23) — https://github.com/ProtonMail/WebClients
8. kenn-io/agentsview, `internal/parser/claude_ai.go` (마지막 커밋 2026-08-21) — https://github.com/kenn-io/agentsview
9. ukogan/claude-migration-assistant, `js/processing/admin-reader.js` (마지막 커밋 2026-02-12) — https://github.com/ukogan/claude-migration-assistant
10. thellmwhisperer/la-roca, `pkg/parsers/claude_web.go`(마지막 커밋 2026-08-21), `pkg/parsers/registry.go`, `pkg/parsers/claude_web_test.go`, `docs/ingest.md`(마지막 커밋 2026-09-21) — https://github.com/thellmwhisperer/la-roca
11. pauldavis/2brain, `docs/reference/claude-export-format.md` (마지막 커밋 2025-11-04) — https://github.com/pauldavis/2brain
