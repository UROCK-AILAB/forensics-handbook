---
title: "ChatGPT iOS 앱"
parent: "ChatGPT"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 120
---

# iOS 앱 (iOS)

iOS 용 ChatGPT 앱은 대화 하나를 JSON 파일 하나로 앱 컨테이너의 `Library/Application Support/conversations-*/` 에 평문으로 두고, 작성 중인 글은 `drafts-*/` 에, 계정 정보는 `Library/Preferences/` 의 plist 에, 올린 이미지와 음성 입력은 `tmp/` 에 둡니다 [2][3].

이 페이지의 경로와 키는 iOS 17 의 앱 1.2024.2xx 판 기준이고, 지금 판(1.2026.258)은 폴더 이름과 키가 다를 수 있습니다[3].

## 무엇을 기록하나 · 왜 생기나

앱은 계정의 대화를 기기에 사본으로 내려 둡니다. 그래서 컨테이너에는 대화 제목·만든 시각·고친 시각·쓴 모델과 메시지 본문이 남고, 맞춤 지시(custom instructions)와 임시 채팅(temporary chat) 여부, 보내지 않은 초안, 로그인한 계정의 이메일과 요금제도 남습니다 [3].

ChatGPT 는 Android 와 iOS 모두에서 대화를 평문으로 저장합니다 [2]. iLEAPP 분석기도 복호화 단계 없이 JSON 과 plist 를 바로 엽니다 [3].

ChatGPT 모바일 앱을 처음 포렌식으로 분석한 연구[1]에서는 Android·iOS·클라우드 저장소에서 흔적이 나왔고 [6], 그 가운데 캐시된 프롬프트, 접근 토큰, 네트워크 흔적이 있었습니다 [5]. iLEAPP `chatgpt.py` 는 이 연구의 제1저자가 연구 과제를 바탕으로 만든 분석기입니다 [3].

## 위치와 버전별 차이

앱 컨테이너는 전체 파일 시스템 기준으로 `/private/var/mobile/Containers/Data/Application/` 아래 UUID 이름의 폴더입니다. iLEAPP 은 `**/Containers/Data/Application/*/` 패턴으로 찾고, 번들 ID 를 따로 적지 않습니다 [3]. 대신 `conversations-*` 폴더나 이름에 `com.openai.chat` 이 든 plist 가 있는 컨테이너를 ChatGPT 컨테이너로 봅니다.

| 컨테이너 안 경로 | 형식 | 담긴 것 | 근거 |
|---|---|---|---|
| `Library/Application Support/conversations-*/*.json` | JSON, 대화마다 한 파일 | 대화 정보, 설정, 메시지 | [3] |
| `Library/Application Support/drafts-*/*.json` | JSON | 보내지 않은 초안 | [3] |
| `Library/Preferences/com.openai.chat.StatsigService.plist` | plist | 계정 ID, 사용자 ID, 이메일, 요금제 | [3] |
| `Library/Preferences/com.segment.storage.oai.plist` | plist(값 안에 plist 가 하나 더 있음) | 분석 도구(Segment) 사용자 ID·이벤트·속성 | [3] |
| `tmp/photo-*.png`, `tmp/*/*.png` | PNG | 올린 이미지 | [3] |
| `tmp/recordings/*.m4a`, `tmp/*/*.m4a` | M4A | 음성 입력 | [3] |

폴더 이름 `conversations-*`·`drafts-*` 의 별표 자리에 들어가는 값은 실제 기기에서 확인합니다. 같은 모양의 폴더가 여러 개 있으면 폴더별로 따로 읽고, 계정 plist 와 맞춰 봅니다.

파일은 기기의 [데이터 보호](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/data-protection/index.html) 등급에 따라 잠기고, 로그인 정보 같은 비밀 값을 두는 곳의 일반 원리는 [키체인](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/keychain.html)에서 다룹니다. ChatGPT 앱이 키체인에 무엇을 두는지는 실제 기기로 확인해야 합니다.

iLEAPP 의 경로는 전체 파일 시스템 추출을 기준으로 합니다. 이 컨테이너가 [로컬 백업](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/backups/local-backup/index.html)에 들어가는지도 실제 기기로 확인해야 합니다. 백업에서 이 앱의 흔적이 나오지 않으면 백업에서 빠진 것인지, 앱이 남기지 않은 것인지부터 구분합니다.

### App Store 정보

App Store 페이지의 값은 다음과 같습니다(2026-09-25 기준) [7].

| 항목 | 값 |
|---|---|
| App Store 항목 | `id6448311069` |
| 개발사 | OpenAI OpCo, LLC |
| 버전 | 1.2026.258(페이지에 "1일 전" 출시로 표시, 2026-09-24 무렵) |
| 요구 사양 | iOS 18.0 이상, iPadOS 18.0 이상, visionOS 2.0 이상 |
| 크기 | 238.2 MB |
| 분류·등급 | Productivity, 13+ |

버전 번호는 아래처럼 세 자리이고, 가운데 자리에 연도와 같은 숫자가 들어갑니다.

```
1.2024.178   1.2025.261   1.2026.258
```

같은 항목이 iPad 와 Vision Pro 도 지원해서, 한 계정의 흔적이 iPhone 말고 다른 Apple 기기에도 있을 수 있습니다. macOS 앱은 [macOS 앱](macos.md)에서 따로 다룹니다. 조사할 기기에 깔린 앱의 버전을 먼저 적어 두면, 위 시험 범위와 비교해 도구 결과를 얼마나 믿을지 정할 수 있습니다.

### 개인정보 라벨과 위치

App Store 의 "Data Linked to You" 라벨에는 Health & Fitness, Location, Contact Info, User Content, Search History, Identifiers, Usage Data, Diagnostics 가 적혀 있습니다 [7]. 이 라벨은 개발사가 신고한 수집 항목이라서, 서버로 모으는 데이터의 종류로 읽고 기기에 남는 파일 목록으로 읽지 않습니다.

iOS 에서 ChatGPT 와 Gemini 는 위치 서비스를 꺼 둔 상태에서도 약 0.5마일 안쪽의 위치 데이터를 얻을 수 있습니다 [2]. 그 위치가 기기에 남는지는 앱 컨테이너 안 파일에서 위도·경도 값을 찾아 확인합니다. 위치 서비스를 껐다는 설정만으로 앱이 위치를 몰랐다고 쓰지 않습니다.

### 앱 안 결제 항목

App Store 에 적힌 앱 안 결제 항목의 이름은 ChatGPT Plus, ChatGPT Go, ChatGPT Pro 5x, ChatGPT Pro 20x, 그리고 100·500·1000 Credits 입니다(2026-09-25) [7]. Apple 계정의 구매 기록에 이 이름이 있으면, 계정 plist 의 요금제 값과 함께 그 계정의 요금제를 추정하는 단서가 됩니다.

## 구조

형식별 읽는 법은 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/data-formats/plist.html)에서 다루고, 여기서는 ChatGPT 앱에 해당하는 키만 적습니다.

### 대화 파일: `conversations-*/*.json`

파일 하나가 대화 하나이고, 맨 위 층의 키는 다음과 같습니다 [3].

| JSON 키 | 뜻 |
|---|---|
| `id` | 대화 ID |
| `title` | 대화 제목 |
| `creation_date`, `modification_date` | 대화를 만든 시각, 고친 시각(2001-01-01 기준 초) |
| `configuration.model` | 대화에 쓴 모델 |
| `configuration.is_temporary_chat` | 임시 채팅이면 참 |
| `configuration.custom_instructions.about_model_message` | 맞춤 지시 가운데 모델이 어떻게 답할지 적은 글 |
| `configuration.custom_instructions.about_user_message` | 맞춤 지시 가운데 사용자에 관해 적은 글 |
| `configuration.custom_instructions.active` | 맞춤 지시가 켜져 있었는지 |
| `tree.storage` | 메시지 ID 를 키로 하는 메시지 사전 |

`tree.storage` 의 값 하나가 메시지 하나이고, iLEAPP 은 그 안의 `content` 객체에서 아래 키를 읽습니다 [3].

| `tree.storage.메시지ID.content` 아래 키 | 뜻 |
|---|---|
| `author.role` | 쓴 쪽(iLEAPP 열 이름 Author) |
| `content.parts` | 본문 목록. iLEAPP 은 줄바꿈으로 이어 한 칸에 보여 줍니다 |
| `content_type` | 내용 종류 |
| `create_time` | 메시지 시각(Unix 초) |
| `metadata.finish_details.type` | 답이 어떻게 끝났는지 |
| `metadata.voice_mode_message` | 음성 대화에서 나온 메시지인지 |

iLEAPP 은 `metadata` 전체도 문자열로 한 칸에 남깁니다 [3]. iLEAPP 은 `storage` 의 메시지를 한 행씩 꺼낼 뿐이고 메시지 사이의 순서를 따로 정리하지 않습니다. 대화 흐름을 다시 맞출 때는 JSON 을 직접 열어 메시지 객체의 다른 키를 봅니다.

`about_user_message` 와 `about_model_message` 는 사용자가 직접 쓴 글이라서 대화 본문처럼 다룹니다.

### 초안: `drafts-*/*.json`

키는 `conversation_id` 와 `content.text` 입니다 [3]. `conversation_id` 를 대화 파일의 `id` 와 맞추면 어느 대화에 쓰다 만 글인지 알 수 있습니다.

### 계정 정보: `Library/Preferences/` 의 plist

| 파일 | 키 |
|---|---|
| `com.openai.chat.StatsigService.plist` | `accountID`, `userID`, `userEmail`, `planType` |
| `com.segment.storage.oai.plist` | `segment.userId`, `segment.events`, `segment.traits` |

`segment.traits` 는 값 안에 plist 가 하나 더 들어 있는 형태이고, 풀면 `plan_type`, `has_paid_plan`, `workspace_id`, `device_id` 가 나옵니다 [3]. `userEmail` 은 계정 식별에 쓰는 값이라서 보고서에는 필요한 만큼만 싣습니다.

### 올린 이미지와 음성 입력: `tmp/`

iLEAPP 은 `tmp/` 아래 PNG 를 "Media Uploads" 로, M4A 를 "Voice Prompts" 로 모읍니다 [3]. 이 파일들은 대화 JSON 과 이어져 있지 않아서, 파일 하나가 어느 대화에서 왔는지는 파일 시각과 메시지 `create_time` 을 맞춰 추정합니다. 음성 대화의 일반 흔적은 [음성 대화 기능](../../generative-media/voice-mode.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `conversations-*` 폴더에 대화 파일이 있으면 그 계정으로 그 제목의 대화가 있었고, 그 사본이 이 기기에 내려와 있었다고 쓸 수 있습니다. 메시지의 `author.role` 로 쓴 쪽을 나누고, `create_time` 으로 메시지가 만들어진 시각을 알 수 있습니다. `is_temporary_chat` 은 그 대화가 임시 채팅이었는지, `voice_mode_message` 는 음성 대화에서 나온 메시지인지 알려 줍니다. 초안 파일은 보내지 않은 글도 기기에 남았다는 기록이고, 계정 plist 는 이 기기에 로그인한 계정의 이메일과 요금제를 알려 줍니다.

**증명하지 못하는 것.** 대화 파일이 있다는 사실만으로 그 대화를 이 기기에서 입력했다고 쓸 수는 없습니다. 같은 계정을 웹이나 다른 기기에서도 썼다면 그쪽에서 한 대화가 이 폴더에 들어오는지 실제 기기로 가려내야 합니다. 기기에 대화가 없다고 대화를 하지 않았다고 볼 수도 없는데, 앱에서 지웠거나, 앱을 다시 깔았거나, 수집 방법이 컨테이너를 담지 못했을 수 있습니다. `tmp/` 의 이미지·음성은 ChatGPT 컨테이너로 판별됐을 때만 이 앱의 것으로 씁니다(함정과 한계 참고). 기기를 쓴 사람이 누구인지는 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)에서처럼 다른 기록과 맞춥니다.

보고서에는 "이 기기의 ChatGPT 앱 컨테이너에 이 계정의 대화 파일 N 개와 메시지 M 건이 있고, 가장 이른 메시지 생성 시각은 이렇다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

| 값 | 형식 | 근거 |
|---|---|---|
| 대화 파일의 `creation_date`, `modification_date` | 2001-01-01 00:00:00 UTC 기준 초. iLEAPP 은 978307200 을 더해 Unix 초로 바꾼 뒤 UTC 로 보여 줍니다 | [3][4] |
| 메시지의 `create_time` | Unix 초, UTC | [3][4] |

두 형식의 기준 시점이 달라서, 한 파일 안에서도 대화 시각과 메시지 시각을 같은 방식으로 바꾸면 31년쯤 어긋납니다. iLEAPP 은 두 값을 정수로 바꾼 뒤 변환해 초 아래 자리를 버리고, 값이 0 이거나 비어 있으면 빈칸으로 둡니다 [3].

`modification_date` 는 대화를 연 시각으로 읽지 않고 메시지 하나하나의 `create_time` 을 함께 봅니다. 무엇이 바뀔 때 이 값이 갱신되는지는 시험 기기에서 대화를 열거나 메시지를 보내 보고 값이 바뀌는지로 확인합니다. 컨테이너 안 파일의 파일 시스템 시각도 동기화나 캐시 갱신 때 바뀔 수 있어서 대화한 시각으로 바로 옮기지 않습니다.

App Store 페이지의 출시 표시는 "1일 전" 처럼 상대 시각이라서, 날짜로 적을 때는 페이지를 본 날짜를 함께 적고 "무렵" 으로 씁니다. 기기의 여러 기록을 시간순으로 합치는 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/ios/03-techniques/analysis/timeline/index.html)과 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **다른 앱의 미디어가 섞입니다.** iLEAPP 은 ChatGPT 표식 파일(`conversations-*` 폴더나 `com.openai.chat` plist)로 컨테이너를 찾았을 때만 그 컨테이너의 `tmp/` 로 결과를 좁힙니다 [3]. 표식이 없으면 경로 패턴에 맞는 다른 앱의 미디어까지 나오고, 분석기의 시험 이미지에서도 메신저·사진 보관 앱 같은 다른 앱의 PNG·M4A 가 결과로 나왔습니다. ChatGPT 가 깔린 세 시험 이미지에서는 두 결과 모두 0행이었습니다. 결과의 파일 경로에서 컨테이너 UUID 를 먼저 확인합니다.
- **시험 범위가 좁습니다.** 대화를 읽은 시험 판은 1.2024.219 와 1.2024.233 이고, 2026-09-25 의 App Store 판은 1.2026.258 입니다 [3][7]. 폴더 이름이나 키가 바뀌면 도구가 조용히 0행을 낼 수 있어서, 결과가 비면 `Library/Application Support/` 의 폴더 목록부터 봅니다.
- **키가 있는 층을 확인합니다.** iLEAPP 은 `content_type` 을 `tree.storage.메시지ID.content` 층에서, 본문은 그 아래 `content.parts` 에서 읽습니다 [3]. 판에 따라 층이 다르면 도구 결과의 열이 비므로, 빈 칸이 많으면 JSON 을 직접 엽니다.
- **토큰.** 모바일 앱에서는 접근 토큰이 나올 수 있습니다 [5]. 나오면 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에 따라 보고서에서 가립니다. 서버에 있는 대화는 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)이나 [계정 데이터 내보내기](export.md)로 확보합니다.
- **지운 대화.** 대화가 파일 단위라서 지운 대화는 파일째 사라질 수 있습니다. 파일 시스템의 빈 공간에서 JSON 조각을 찾는 방법은 [내용 복구](../../../03-techniques/analysis/content-recovery.md)에 있습니다.
- **수집 범위.** 컨테이너는 수집 방법에 따라 얻을 수도 있고 못 얻을 수도 있습니다. 폴더가 비어 보이면 앱 동작 때문인지 수집 범위 때문인지부터 구분합니다. 수집 범위를 정하는 방법은 [기기에서 AI 흔적 모으기](../../../03-techniques/acquisition/endpoint-triage.md)에 있습니다.
- **브라우저로 쓴 경우.** 사파리나 크롬으로 쓴 ChatGPT 는 앱이 아니라 [웹 브라우저](web.md) 흔적으로 남고, 그쪽 기록은 [사파리](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/browsers/safari/index.html)와 [크롬 (Chrome for iOS)](https://urock-ailab.github.io/forensics-handbook/ios/02-artifacts/browsers/chrome.html)에서 읽습니다.
- **App Store 값은 바뀝니다.** 이 페이지의 버전·크기·요구 사양은 2026-09-25 의 값이라서, 보고서에 인용할 때는 페이지를 다시 열어 날짜와 함께 적습니다.

## 직접 분석해 보기

### 헥스로 한 번

대화 파일은 평문 JSON 이라서 헥스로 열면 첫 바이트부터 `{"` 가 보입니다. 아래는 만든 예시이고, 키 순서는 실제 파일마다 다릅니다.

```
00000000  7B 22 69 64 22 3A 22 30 30 30 30 61 61 61 61 2D  {"id":"0000aaaa-
00000010  31 31 31 31 2D 32 32 32 32 2D 33 33 33 33 2D 34  1111-2222-3333-4
00000020  34 34 34 35 35 35 35 36 36 36 36 22 2C 22 74 69  44455556666","ti
```

첫 글자가 `{` 가 아니면 파일이 잘렸거나 다른 형식이므로, 파일 크기와 끝부분부터 봅니다.

### 구조를 따라 한 번

아래는 만든 예시로, 위 구조 절의 키를 한 파일에 모은 것입니다.

```json
{
  "id": "0000aaaa-1111-2222-3333-444455556666",
  "title": "예시 대화",
  "creation_date": 780000000,
  "modification_date": 780000060,
  "configuration": {
    "model": "example-model",
    "is_temporary_chat": false,
    "custom_instructions": {
      "about_user_message": "예시 사용자 소개",
      "about_model_message": "예시 답변 방식",
      "active": true
    }
  },
  "tree": {
    "storage": {
      "msg-0001": {
        "content": {
          "author": {"role": "user"},
          "content": {"parts": ["예시 질문"]},
          "content_type": "text",
          "create_time": 1758307210,
          "metadata": {"voice_mode_message": false}
        }
      }
    }
  }
}
```

`creation_date` 780000000 에 978307200 을 더하면 Unix 초 1758307200 이 되고, 이는 2025-09-19 18:40:00 UTC 입니다. 메시지의 `create_time` 1758307210 은 이미 Unix 초라서 그대로 바꾸면 2025-09-19 18:40:10 UTC 입니다. 두 값을 같은 줄에 놓아 대화를 만든 지 10초 뒤에 첫 메시지가 생겼다고 맞춰 볼 수 있습니다.

명령줄에서 jq 로 같은 값을 뽑으려면 다음처럼 씁니다.

```
jq -r '[.id, .title, (.creation_date + 978307200 | floor | todate)] | @tsv' conversation.json
jq -r '.tree.storage | to_entries[] | [.key, .value.content.author.role, (.value.content.create_time | floor | todate), (.value.content.content.parts | map(tostring) | join(" "))] | @tsv' conversation.json
```

### 공개 도구로 한 번

iLEAPP 에 전체 파일 시스템 추출본을 넣으면 "ChatGPT" 분류 아래에 대화 정보(Conversations Metadata), 메시지(Conversations), 초안(Draft Conversations), 계정 정보(Preferences), 올린 이미지(Media Uploads), 음성 입력(Voice Prompts)이 따로 나옵니다 [3]. 도구가 보여 주는 값은 위 jq 결과와 맞춰 봅니다.

## 교차 검증

기기의 대화 사본은 [계정 데이터 내보내기](export.md)로 받은 같은 대화와 제목·시각을 맞추고, 대화 파일의 `id` 가 내보내기의 대화 ID 와 같은지도 실제 데이터로 맞춰 봅니다. 접속 시간대는 [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md)으로 봅니다. 같은 계정을 쓴 Android 기기가 있으면 [Android 앱](android.md)의 대화 사본과도 맞추고, 음성으로 대화했다면 [음성 대화 기능](../../generative-media/voice-mode.md)도 함께 봅니다. 서비스 전체에서 대화 원본이 어디에 있는지는 [ChatGPT](index.md) 허브에 정리돼 있습니다.

## 실습

iLEAPP 시험 이미지(`felix_ios17`, `otto_ios17`, `dexter_ios18`)는 내려받는 곳이 공개돼 있지 않습니다 [3]. 시험용 기기에 앱을 깔고 시험용 계정으로 가짜 대화를 만든 뒤 전체 파일 시스템을 추출해 다음을 풀어 봅니다.

1. `Library/Application Support/` 에 생긴 `conversations-*` 폴더의 파일 수가 앱에 보이는 대화 수와 같은지 봅니다.
2. 대화 하나의 `creation_date` 와 첫 메시지의 `create_time` 을 각각 UTC 로 바꿔, 둘의 차이가 앱에서 대화를 시작한 흐름과 맞는지 봅니다.
3. 임시 채팅을 하나 연 뒤 다시 추출해, 대화 파일이 생기는지와 `is_temporary_chat` 값이 무엇인지 적습니다.
4. 글을 쓰다 보내지 않고 앱을 닫은 뒤 `drafts-*` 폴더에 그 글이 남는지 봅니다.
5. 이미지 하나를 올리고 음성으로 한 번 말한 뒤 `tmp/` 에 PNG·M4A 가 생기는지, 시간이 지나면 없어지는지 봅니다.
6. 같은 기기로 로컬 백업을 만들어 위 파일들이 백업에 들어가는지 비교합니다.

## 참고 문헌

1. Evangelos Dragonas, Costas Lambrinoudakis, Panagiotis Nakoutis, "Forensic analysis of OpenAI's ChatGPT mobile application", Forensic Science International: Digital Investigation, 50 (2024), 301801. https://doi.org/10.1016/j.fsidi.2024.301801
2. Sonali Tyagi, Yufeng Gong, Umit Karabiyik, "Forensic analysis and privacy implications of LLM mobile apps: A case study of ChatGPT, Copilot, and Gemini", Forensic Science International: Digital Investigation, 54 (2025), 301974. https://doi.org/10.1016/j.fsidi.2025.301974 (초록)
3. iLEAPP, `scripts/artifacts/chatgpt.py`(작성 Evangelos Dragonas, 2026-08-21 갱신) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/chatgpt.py
4. iLEAPP, `scripts/ilapfuncs.py`(`webkit_timestampsconv`, `convert_ts_int_to_utc`) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/ilapfuncs.py
5. Kendall J. Comeaux, Trevor T. Spinosa, Ali Ghosn, Ibrahim Baggili, "Ex Machina: A forensic evaluation of AI companion applications and their evidentiary value", Forensic Science International: Digital Investigation, 56 (2026), 302050. https://doi.org/10.1016/j.fsidi.2026.302050 (2절 관련 연구)
6. Sungjo Jeong, Sangjin Lee, Jungheum Park, "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987. https://doi.org/10.1016/j.fsidi.2025.301987 (2.1절)
7. App Store, ChatGPT (OpenAI OpCo, LLC) — https://apps.apple.com/us/app/chatgpt/id6448311069
