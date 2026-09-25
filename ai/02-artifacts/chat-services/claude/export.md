---
title: "Claude 계정 데이터 내보내기"
parent: "Claude"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 200
---

# 계정 데이터 내보내기 (Data Export)

Claude 의 계정 데이터 내보내기는 계정 서버에 있는 대화와 계정 정보를 ZIP 파일로 받는 기능이고, 그 안의 `conversations.json` 에 대화 제목·메시지 본문·보낸 쪽·시각이 들어 있어서 기기 흔적만으로는 알 수 없는 대화 내용을 확인하는 주된 길이 됩니다.

> 확인 날짜: 2026-09-25. Claude 공식 도움말과 개인정보 안내 문서, 공개 도구 claude-to-sqlite 의 설명서와 소스를 바탕으로 썼습니다. 이 핸드북은 실제 내보내기 파일을 열어 보지 않았고, 기기 관찰(Windows 11, 2026-09)에서도 내보내기 파일은 보지 않았습니다. 파일 안의 칸 이름은 공개 도구가 파일을 읽으려고 쓴 이름에서 가져온 것이라 공식 형식 설명이 아닙니다.

## 무엇을 받나 · 왜 생기나

공식 도움말은 개인 Free·Pro·Max 사용자가 웹이나 데스크톱 앱에서 왼쪽 아래 이니셜을 눌러 Settings 의 Privacy 절로 들어간 뒤 "Export data" 로 내보내기를 요청한다고 설명합니다[1]. iOS·Android 앱에는 이 기능이 없어서, 휴대전화로만 쓴 계정이라도 내보내기는 웹이나 PC 에서 요청합니다[1]. Team·Enterprise 요금제에서는 조직의 데이터를 Primary Owner 만 내보낼 수 있습니다[1]. 조직 계정의 활동을 관리자 쪽 기록으로 보는 방법은 [Claude 기업용 감사 로그](../../network-enterprise/claude-enterprise.md)에서 따로 다룹니다.

요청하면 파일을 만드는 데 시간이 조금 걸릴 수 있고, 준비가 끝나면 계정 이메일로 내려받기 링크가 옵니다[1]. 링크는 받은 뒤 24시간이 지나면 만료되고, 내려받으려면 그 계정으로 로그인해야 하며, 만료되면 다시 요청합니다[1]. 도움말은 받는 자료를 "대화 데이터와 사용자 계정 정보" 라고만 적었고 ZIP 안의 파일 이름 목록은 싣지 않았습니다[1]. 내보낸 자료를 다른 개인 계정으로 가져올 수는 없고, 개인 계정을 Team·Enterprise 조직으로 옮길 때는 내보내기 없이 바로 옮긴다고 적었습니다[1].

내보내기는 기기에 있던 파일을 모으는 기능이 아니라 계정에 묶인 서버 쪽 데이터의 사본을 받는 기능입니다. 그래서 기기에서 앱을 지웠거나 기기에 캐시가 남지 않았어도, 계정에 대화가 남아 있으면 보관 파일에 나올 수 있습니다. 기기 쪽 흔적은 [웹 브라우저](web.md), [Windows 앱](windows.md), [macOS 앱](macos.md) 같은 판별 페이지에서 다루고, 서비스마다 다른 내보내기 형식을 견준 내용은 [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md)에 있습니다.

## 위치

받은 파일은 ZIP 이고, 안에 대화를 담은 `conversations.json` 이 있습니다[2][3]. claude-to-sqlite 설명서는 내려받은 파일에 `.zip` 확장자가 빠져 있을 수 있다고 적었으므로[2], 확장자만 보고 거르지 말고 파일 머리로 ZIP 인지 가립니다. 공개 도구 claude-to-sqlite 가 ZIP 안에서 이 이름의 파일을 찾아 읽기 때문에 파일 이름은 그 도구로 확인할 수 있지만[3], 계정 정보나 프로젝트를 담은 다른 파일이 어떤 이름으로 들어 있는지는 확인하지 못했습니다.

기기에서 보관 파일을 찾을 때는 내려받은 위치를 먼저 봅니다. 링크를 이메일로 받아 브라우저로 내려받는 방식이라, 보관 파일이 기기에 있었다면 브라우저 다운로드 기록과 메일 기록에도 흔적이 남을 수 있습니다. 브라우저 다운로드 기록을 읽는 법은 [웹 브라우저](web.md) 페이지가 안내하는 브라우저별 페이지를 따릅니다.

## 구조

claude-to-sqlite 의 소스는 `conversations.json` 을 대화의 배열로 읽고, 대화마다 `account.uuid` 와 `chat_messages` 를 떼어 낸 뒤 나머지 칸은 그대로 표에 넣습니다[3]. 메시지는 대화 안의 `chat_messages` 배열에 들어 있고, 메시지 칸도 그대로 넣습니다[3]. 그래서 아래 칸 이름은 소스가 직접 부르는 이름(`account.uuid`, `chat_messages`, `uuid`, `text`, `sender`)과 설명서가 적은 표 칸[2]을 합친 것이고, 뜻은 이름으로 짐작한 것입니다.

| 묶음 | 칸 이름 | 짐작한 뜻 |
|---|---|---|
| 대화 | `uuid`, `name`, `created_at`, `updated_at` | 대화 ID, 제목, 두 시각 |
| 대화의 계정 | `account.uuid` | 대화가 속한 계정 ID |
| 대화의 메시지 | `chat_messages` | 메시지 배열 |
| 메시지 | `uuid`, `text`, `sender`, `created_at`, `updated_at`, `attachments`, `files` | 메시지 ID, 본문, 보낸 쪽, 두 시각, 첨부, 파일 |

도구는 `sender` 값이 `assistant` 인지 비교해 답변을 가려냅니다[3]. 사용자가 보낸 메시지에 어떤 값이 적히는지는 확인하지 못했습니다. `attachments` 와 `files` 는 도구가 칸 그대로 옮겨 담을 뿐이라 안쪽 구조는 알 수 없고, 첨부한 파일 본문이 들어 있는지, 이름만 들어 있는지도 확인하지 못했습니다. 프롬프트·첨부·생성물을 서로 가려 읽는 일반 방법은 [프롬프트·첨부·생성물 구분하기](../../../01-foundations/concepts/prompt-attachment-output.md)에 있습니다.

아래는 위 칸 이름으로 대화 한 건을 흉내 낸 만든 예시이고, 값은 모두 가짜입니다. 시각 값의 모양은 확인하지 못해서 가짜 글자로 두었습니다.

```json
[
  {
    "uuid": "conv-example-0001",
    "name": "가짜 프로젝트 도토리 일정",
    "created_at": "가짜-시각-1",
    "updated_at": "가짜-시각-2",
    "account": { "uuid": "acct-example-0001" },
    "chat_messages": [
      {
        "uuid": "msg-example-0001",
        "text": "도토리 프로젝트 다음 주 일정을 표로 정리해 줘",
        "sender": "가짜-보낸-쪽",
        "created_at": "가짜-시각-1",
        "updated_at": "가짜-시각-1",
        "attachments": [],
        "files": []
      },
      {
        "uuid": "msg-example-0002",
        "text": "가짜 답변 본문",
        "sender": "assistant",
        "created_at": "가짜-시각-2",
        "updated_at": "가짜-시각-2",
        "attachments": [],
        "files": []
      }
    ]
  }
]
```

생성물의 저장 방식도 눈여겨봅니다. 도구는 메시지 `text` 안에서 `antArtifact` 태그(속성 identifier·type·language·title)와 `antThinking` 태그를 정규식으로 찾아 따로 뽑는데, `sender` 가 `assistant` 인 메시지에서만 찾습니다[3]. 도구를 만들 때의 내보내기에서는 아티팩트가 별도 파일이 아니라 답변 본문 안에 태그로 섞여 있었다는 뜻이고, 지금 내보내기도 그런지는 확인하지 못했습니다. 그래서 본문 안에서 이런 태그를 찾지 못했다고 생성물이 없었다고 보지 않고, 내보낸 날짜와 ZIP 안의 다른 파일을 함께 봅니다.

claude-to-sqlite 는 내보내기를 SQLite 데이터베이스로 바꾸고, 아래 표를 만듭니다[2]. 이 표는 도구가 만든 결과물이라 원본 형식과 같지 않습니다.

| 표 | 칸 |
|---|---|
| `conversations` | uuid, name, created_at, updated_at, account_id |
| `messages` | uuid, text, sender, created_at, updated_at, attachments, files, conversation_id |
| `artifacts` | id, artifact, identifier, version, type, language, title, content, thinking, conversation_id, message_id |

## 증거로서 의미

**증명하는 것.** `conversations.json` 에 대화가 있으면 내보낸 때 그 계정에 그 대화가 남아 있었다고 쓸 수 있고, `sender` 로 계정 쪽 입력과 답변을 나눠 적을 수 있습니다. `account.uuid` 는 대화가 속한 계정 ID 칸이고, Windows 앱 `config.json` 에는 이름으로 보아 마지막으로 쓴 계정 ID 를 적는 칸 `lastKnownAccountUuid` 가 있어서(확인 범위: Windows 11, 2026-09) 두 값을 맞춰 보면 기기와 계정을 잇는 근거가 됩니다. 두 값이 같은 형식의 ID 인지는 확인하지 못해서, 맞춰 볼 때는 실제 값의 모양부터 확인합니다. 기기에서 보관 파일이 나오면 그 파일이 그 기기에 저장돼 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** 보관 파일에 없는 대화를 처음부터 없었다고 쓸 수는 없습니다. 사용자가 지운 대화는 대화 목록에서 바로 사라지고 서버 저장소에서는 30일 안에 지워지는데[4], 지운 뒤 30일 사이에 내보내면 그 대화가 들어가는지는 확인하지 못했습니다. 시크릿(Incognito) 대화가 내보내기에 들어가는지도 확인하지 못했습니다. 보관 기간 전체는 [Claude](index.md) 허브에, 보관 설정의 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에 있습니다. 계정 기록은 그 계정으로 로그인한 누군가의 활동이라 실제로 누가 입력했는지는 기기 흔적과 함께 따집니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 기기에서 찾은 보관 파일은 JSON 이라 누구든 고칠 수 있어서, 원본인지는 받은 경로와 파일 시각을 함께 봅니다.

## 시각 해석

대화와 메시지에 각각 `created_at` 과 `updated_at` 두 시각 칸이 있지만, 값이 어떤 글자 형식인지, 시간대 표시가 붙는지는 확인하지 못했습니다. 실제 파일에서 값의 모양을 먼저 보고, 알고 있는 대화 시각 하나와 맞춰 본 다음 UTC 인지 현지 시각인지 정합니다. 대화의 `updated_at` 이 무엇이 바뀔 때 바뀌는지(새 메시지, 제목 변경 등)도 문서로 확인하지 못해서, 마지막 메시지의 `created_at` 과 견주어 봅니다.

보관 파일 자체의 시각은 따로 봅니다. ZIP 파일의 파일 시스템 시각은 내려받거나 옮긴 때에 따라 바뀌어서 대화 시각과 다르고, 링크는 받은 뒤 24시간이 지나면 만료되므로[1] 공식 링크로 내려받은 기록이라면 그 시각은 링크 메일을 받은 뒤 24시간 안에 들어갑니다. 메일 도착 시각과 다운로드 기록을 함께 보면 내보내기를 요청한 무렵을 좁힐 수 있습니다. 기기 흔적과 보관 파일 안의 시각을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)을 봅니다.

## 함정과 한계

내보내기는 계정 주인이 로그인해서 요청하고 로그인해서 받는 기능이라[1], 조사에 쓰려면 법적 절차나 당사자 동의 안에서만 계정에 접근합니다. 수집 순서와 받은 파일을 원본 그대로 지키는 방법은 [계정 데이터 내보내기로 수집](../../../03-techniques/acquisition/export-collection.md)에서 다루고, 계정 주인의 협조를 얻을 수 없으면 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)을 검토합니다.

이 페이지의 칸 이름은 한 공개 도구의 소스와 설명서에 기댄 것이라, 도구를 만들 때의 내보내기 모양을 보여 줄 뿐 지금 파일에 어떤 칸이 더 있는지는 알려 주지 않습니다. 내보내기 형식은 서비스가 공지 없이 바꿀 수 있어서, 칸이 없거나 더 있다고 파일이 손상됐거나 고쳐졌다고 바로 보지 않고 내보낸 날짜와 함께 판단합니다. 도구가 보여 주는 결과보다 원본 JSON 을 먼저 확인합니다.

Team·Enterprise 계정은 사용자 본인이 아니라 Primary Owner 가 조직 단위로 내보내서[1], 받은 자료의 범위가 개인 내보내기와 다를 수 있습니다. 조직 내보내기 파일의 짜임은 확인하지 못했습니다.

## 직접 분석해 보기

**헥스로 한 번.** 보관 파일을 헥스 편집기로 열어 확장자와 관계없이 앞머리가 ZIP 형식의 머리 글자 `PK` 로 시작하는지 확인하고, 압축을 푼 `conversations.json` 앞부분에 JSON 의 대괄호와 `uuid`, `chat_messages` 같은 칸 이름이 읽을 수 있는 글자로 보이는지 확인합니다. 이 핸드북은 실제 보관 파일을 열지 않아서 바이트 예시는 싣지 않았습니다.

**공개 도구로 한 번.** claude-to-sqlite 는 내보내기의 `conversations.json` 을 읽어 위 세 표를 담은 SQLite 파일을 만드는 공개 도구입니다[2]. 만든 데이터베이스는 SQLite 를 읽는 아무 도구로 열 수 있고, 읽는 법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html) 페이지를 봅니다. 변환 결과는 검색하기 편한 사본으로만 쓰고, 보고서의 근거는 원본 `conversations.json` 에서 칸을 직접 확인해 적습니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 브라우저 방문·다운로드 기록 | 보관 파일을 받은 때, 웹판 사용 흔적 | [웹 브라우저](web.md) |
| 데스크톱 앱 설정 | 기기에서 마지막으로 쓴 계정 ID, 처음 실행한 때 | [Windows 앱](windows.md), [macOS 앱](macos.md) |
| 휴대전화 앱 | 기기에 설치한 흔적(내보내기는 없음) | [Android 앱](android.md), [iOS 앱](ios.md) |
| 네트워크 기록 | 대화 시각 무렵의 접속 | [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) |

## 실습

Claude 보관 파일을 담은 공개 검체는 이번 조사에서 확인하지 못했습니다. 시험용 계정으로 가짜 대화를 만들고 내보내기를 받아 아래 질문을 풀어 봅니다.

1. ZIP 안에 `conversations.json` 말고 어떤 파일이 들어 있습니까?
2. 알고 있는 대화 시각과 `created_at` 값을 맞춰 보면 값의 형식과 기준 시간대는 무엇입니까?
3. 사용자가 보낸 메시지의 `sender` 에는 어떤 값이 적힙니까?
4. 아티팩트를 만든 대화를 내보내면 생성물이 답변 본문 안의 태그로 나옵니까, 따로 나옵니까?
5. 대화 하나를 지운 직후 다시 내보내면 그 대화가 빠집니까?

## 참고 문헌

1. Claude Help Center, "How can I export my Claude data?" — https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-data (2026-09-25 열람)
2. GitHub, simonw/claude-to-sqlite README — https://github.com/simonw/claude-to-sqlite (2026-09-25 열람)
3. GitHub, simonw/claude-to-sqlite cli.py 소스 — https://raw.githubusercontent.com/simonw/claude-to-sqlite/main/claude_to_sqlite/cli.py (2026-09-25 열람)
4. Anthropic Privacy Center, "How long do you store my data?" — https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data (2026-09-25 열람)
