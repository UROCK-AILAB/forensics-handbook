---
title: "Gemini 계정 데이터 내보내기"
parent: "Gemini"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 330
---

# 계정 데이터 내보내기 (Data Export)

Gemini 대화는 서버의 Gemini 앱 활동 (Gemini Apps Activity) 에 남기 때문에, 계정 주인이 Google Takeout 으로 받는 보관 파일이 대화 내용과 프롬프트 시각을 얻는 주된 길이고, 기기에 남은 보관 파일 자체도 증거가 됩니다.

## 무엇을 기록하나 · 왜 생기나

내보내기는 Google Takeout (takeout.google.com) 에서 Gemini 를 쓰는 계정으로 로그인해 요청합니다. 받을 항목은 둘로 나뉩니다. "Gemini" 를 고르면 Gems 데이터가 들어가고 "My Activity" → "All activity data included" → "Gemini Apps" 를 고르면 채팅과 생성한 미디어, 올린 파일이 들어갑니다 [1]. 대화 기록은 두 번째 항목에 있고, 맞춤 Gem 설정까지 보려면 둘 다 고릅니다.

| 고르는 곳 | 들어가는 것 |
|---|---|
| "Gemini" | Gems 데이터 [1] |
| "My Activity" → "All activity data included" → "Gemini Apps" | 채팅, 생성한 미디어, 올린 파일 [1] |

받는 방법은 이메일로 오는 내려받기 링크(7일 동안 유효)이거나 Google Drive·Dropbox·OneDrive·Box 에 넣는 방식이고, 압축 형식은 .zip 또는 .tgz 에서 고릅니다 [1]. 한 번만 내보낼 수도 있고 정기 내보내기를 걸 수도 있는데, 고급 보호 프로그램 (Advanced Protection) 가입자는 정기 내보내기를 쓸 수 없습니다 [1]. 준비에는 몇 시간에서 며칠이 걸리고, 대부분 당일에 끝납니다 [1].

조사에서는 받는 방법이 흔적의 위치를 정합니다. 이메일 링크로 받았다면 메일함의 안내 메일과 브라우저 다운로드 기록, 다운로드 폴더의 압축 파일을 보고, 클라우드 저장소로 보냈다면 그 저장소와 동기화 폴더를 봅니다. 정기 내보내기가 걸려 있으면 압축 파일이 여러 번 생겼을 수 있습니다.

프롬프트·첨부·생성물을 구분해 읽는 일반 방법은 [프롬프트·첨부·생성물 구분하기](../../../01-foundations/concepts/prompt-attachment-output.md)에 있고, 서비스마다 다른 내보내기 형식을 비교한 내용은 [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md)에 있습니다.

## 위치와 버전별 차이

공개 도구 세 개가 읽는 파일은 보관 파일 안의 My Activity 폴더 아래 Gemini Apps 폴더에 있습니다. 파일 이름은 도구마다 다르게 적었습니다.

| 경로 | 적은 곳 |
|---|---|
| `Takeout/My Activity/Gemini Apps/MyActivity.json` | gemini-to-obsidian 스크립트가 이 경로를 그대로 엽니다(2025-10-02 판) [4]. AI-Conversation-Toolkit 문서도 같은 경로를 적었습니다(2025-12-16 판) [5] |
| `My Activity.json` (띄어 쓴 이름) | remnic 파서는 이 이름을 기본으로 적고 `MyActivity.json` 을 예전 표기라고 적었습니다(2026-06-05 판) [6] |
| `Takeout/Η δραστηριότητά μου/Εφαρμογές Gemini/Ηδραστηριότητάμου.json` | 계정 언어가 그리스어일 때의 예입니다. 폴더와 파일 이름이 계정 언어로 바뀝니다 [5] |

그래서 한국어 계정의 보관 파일은 폴더 이름이 영어가 아닐 수 있고, 파일 이름으로 찾기보다 Takeout 폴더 아래 JSON·HTML 파일을 모두 나열한 뒤 내용으로 구분하는 편이 안전합니다.

형식도 고르기에 따라 다릅니다. JSON 으로 받으려면 "My Activity" 옆의 "Multiple formats" 에서 형식을 JSON 으로 고릅니다 [4]. 받은 파일이 어느 형식인지는 파일 확장자와 첫 바이트로 판별합니다(아래 "직접 분석해 보기").

Gemini 가 Bard 라는 이름이던 때의 기록도 같은 파일에 들어갈 수 있습니다. `header` 가 `"Bard"` 이거나 `products` 에 `Bard` 가 든 레코드는 이름을 바꾸기 전의 Gemini 기록입니다 [4][6].

## 구조

JSON 파일은 레코드를 늘어놓은 배열입니다 [6]. ChatGPT·Claude 내보내기처럼 대화별로 메시지를 묶은 구조가 아니고, 레코드 하나가 사용자의 활동 하나입니다 [5][6]. 도구들이 읽는 필드에는 대화 ID 가 없어서 레코드는 시각으로만 묶을 수 있습니다 [5]. 어느 레코드끼리 한 대화였는지는 실제 파일에서 필드 이름을 보고 따로 확인합니다.

아래는 도구 코드와 문서에 적힌 필드를 모은 것입니다. 한 도구만 읽는 필드도 있으니 실제 파일에 어떤 필드가 있는지 먼저 봅니다.

| 필드 | 내용 | 적은 곳 |
|---|---|---|
| `header` | `"Gemini Apps"`. 다른 서비스(검색·지도·YouTube)를 함께 내보내면 같은 파일에 섞일 수 있어서 이 값으로 거릅니다 | [6] |
| `title` | 앞말이 붙은 프롬프트나 동작 설명. 앞말은 아래 표 | [4][5][6] |
| `text` | 새 형식에서 프롬프트 글이 들어가는 필드 | [6] |
| `titleUrl` | `https://gemini.google.com/...` 모양의 주소 | [4][6] |
| `time` | 프롬프트 시각. ISO 8601 UTC | [5][6] |
| `products` | `["Gemini Apps"]` | [6] |
| `subtitles[].name` | 모델 이름(`Model: ...`) [6], Canvas 본문 [5], 첨부 파일 안내 문구 [5] | [5][6] |
| `safeHtmlItem[].html` | 답변 HTML | [4][5] |
| `details[].name` | 일부 내보내기에서 답변이 들어감 | [6] |
| `attachmentInfo[]` | 첨부. 도구는 항목마다 `url`, `path`, `name` 을 찾습니다 | [4] |
| `attachedFiles`, `imageFile` | 첨부 파일과 이미지 표시 | [5] |

`title` 의 앞말은 활동 종류와 판에 따라 다르고, 계정 언어로도 바뀝니다 [5].

| 앞말 | 뜻 | 적은 곳 |
|---|---|---|
| `Prompted ` | 프롬프트 | [4] |
| `Asked: ` | 예전 내보내기의 프롬프트 | [6] |
| `Submitted query `, `Query submitted ` | 프롬프트 | [5] |
| `Created Gemini Canvas titled ` | Canvas 를 만듦. 뒤에 Canvas 제목 | [5] |
| `Υποβλήθηκε το ερώτημα ` | 그리스어 계정의 프롬프트 | [5] |

이 밖에 `Searched:`, `Typed:` 도 앞말로 쓰입니다 [6].

아래는 만든 예시 레코드입니다. 필드 이름과 앞말은 [4][5][6]을 따랐고 값은 모두 지어낸 것입니다.

```json
[
  {
    "header": "Gemini Apps",
    "title": "Prompted 회의록을 세 줄로 요약해 줘",
    "titleUrl": "https://gemini.google.com/app",
    "time": "2026-03-04T05:06:07.890Z",
    "products": ["Gemini Apps"],
    "subtitles": [{ "name": "Model: 예시 모델" }],
    "safeHtmlItem": [{ "html": "<p>예시 답변입니다.</p>" }]
  }
]
```

## 증거로서 의미

**증명하는 것.** 보관 파일에 `header` 가 `"Gemini Apps"` 인 레코드가 있으면 그 계정의 Gemini 앱 활동에 그 프롬프트가 그 시각으로 기록돼 있었다고 쓸 수 있습니다. 레코드에 답변 HTML 이나 Canvas 본문이 있으면 그 내용도 계정 기록에 남아 있었다고 쓸 수 있고, 생성한 미디어와 올린 파일이 있으면 그 계정에 그 파일이 남아 있었다고 쓸 수 있습니다 [1]. 기기에 보관 파일이 있으면 그 파일이 기기에 저장돼 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** 보관 파일에 없는 대화를 처음부터 없었다고 쓸 수는 없는데, 지웠거나 활동 저장을 꺼 두었거나 임시 채팅을 썼을 수 있기 때문입니다. 레코드에 대화 ID 가 없어서, 두 프롬프트가 같은 대화 창에서 나왔다고 파일만으로 말할 수는 없습니다. 계정 기록은 그 계정으로 로그인한 누군가의 활동이라서, 실제로 누가 입력했는지는 기기 흔적과 함께 따져야 합니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 기기에서 찾은 보관 파일은 사용자가 고친 뒤 다시 압축했을 수도 있어서, 원본인지는 받은 경로와 파일 시각을 함께 봅니다.

## 시각 해석

`time` 은 프롬프트 시각이고, ISO 8601 형식에 끝에 `Z` 가 붙은 UTC 입니다(예: `2025-12-15T10:30:00.000Z`, `2026-02-14T09:30:00.000Z`) [5][6]. remnic 은 `Z`, `+00:00`, `-00:00` 으로 끝나지 않는 값을 오류로 거부합니다 [6]. 답변은 프롬프트와 같은 레코드에 들어 있고 시각 필드는 `time` 하나뿐이라서, 답변 시각은 따로 적히지 않습니다 [5].

보관 파일 자체의 시각은 따로 봅니다. 압축 파일의 파일 시스템 시각은 내려받거나 옮긴 때에 따라 바뀌고, 요청한 때와 파일을 만든 때 사이에 시간이 걸려서 요청 시각과도 다를 수 있습니다 [1]. 기기 흔적과 보관 파일의 시각을 시간순으로 합치는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)을 봅니다.

## 함정과 한계

**답변이 들어가는지는 출처끼리 다릅니다.** remnic 파서(2026-06-05 판)는 "Takeout 이 답변을 내보내지 않는다" 고 적고 프롬프트만 읽습니다 [6]. gemini-to-obsidian(2025-10-02 판)과 AI-Conversation-Toolkit(문서 2025-12-16 판, 코드 2026-07-07 판)은 `safeHtmlItem[].html` 을 답변으로 읽고 [4][5], 이미지 생성 같은 일부 활동에는 답변 글이 없을 수 있습니다 [5]. 판이나 계정에 따라 다를 수 있으니 실제 파일에서 `safeHtmlItem` 이 있는 레코드 수를 세어 봅니다.

**도구가 대화를 묶는 방식은 추정입니다.** 대화 ID 가 없어서 gemini-to-obsidian 과 AI-Conversation-Toolkit 은 30분 넘게 비는 곳을 대화 경계로 잡아 레코드를 묶습니다 [4][5]. 이렇게 만든 "대화" 는 도구가 시각으로 나눈 것이라, 보고서에 대화 단위를 쓸 때는 이 점을 밝힙니다.

**도구가 레코드를 버릴 수 있습니다.** AI-Conversation-Toolkit 은 `title` 에 프롬프트 문구나 Canvas 문구가 들어 있는 레코드만 읽고 나머지는 버립니다 [5]. 이 도구의 영어 프롬프트 검사는 `'Submitted query' in title.lower()` 라서 소문자로 바꾼 제목에서 대문자로 시작하는 문구를 찾고, 그래서 영어 프롬프트 레코드가 걸리지 않을 수 있습니다(2026-07-07 커밋 판 코드) [5]. gemini-to-obsidian 은 `Prompted ` 만 떼어 내고 [4], remnic 은 `text` 가 없을 때 `title` 에서 `Asked:` 같은 앞말을 뗍니다 [6]. 계정 언어가 영어가 아니거나 앞말이 다르면 도구 출력에서 레코드가 빠지니, 원본 JSON 의 레코드 수와 도구 출력의 수를 맞춰 봅니다.

**도구 출력의 시각에는 시간대 표시가 없을 수 있습니다.** gemini-to-obsidian 은 UTC 로 읽은 시각을 시간대 표시 없이 `created: 2025-09-12 13:13:35` 모양으로 씁니다 [4]. 출력 파일만 보고 현지 시각으로 읽지 않도록 원본 `time` 값과 대조합니다.

**첨부 필드 이름이 도구마다 다릅니다.** gemini-to-obsidian 은 `attachmentInfo` 를 읽고, 적힌 경로에 파일이 없으면 Takeout 폴더 전체에서 같은 파일 이름을 찾습니다 [4]. AI-Conversation-Toolkit 은 `attachedFiles`, `imageFile`, 그리고 `subtitles` 의 첨부 안내 문구를 봅니다 [5]. 실제 파일에서 첨부 필드 이름과 보관 파일 안의 첨부 파일 위치를 직접 확인합니다.

**보관 파일에 모든 기록이 들어간다고 볼 수 없습니다.** 내보내기는 사본을 만드는 일이고 서버의 활동을 지우지 않습니다. 아래 경우는 보관 파일에서 빠지거나 다른 곳에 있을 수 있습니다.

| 경우 | 내용 | 실제 파일로 확인할 점 |
|---|---|---|
| 요청 뒤 바뀐 데이터 | 요청한 때와 보관 파일을 만든 때 사이에 바뀐 데이터는 빠질 수 있음 [1] | 요청 시각과 보관 파일 생성 시각의 간격 |
| 활동 저장을 끈 동안의 대화 | 72시간 보관되지만 활동 목록에 보이지 않음 [2][3] | 그 기간의 레코드가 보관 파일에 있는지 |
| Labs 의 Gems(Opal 실험) | Gemini 앱의 일부가 아니고 Google Drive 의 "Opal" 폴더에 저장, 활동에 나오지 않음 [2][3] | Drive 항목으로 따로 내보내야 하는지 |
| 사람 검토를 거친 사본 | 최대 3년 보관, 사용자가 활동을 지워도 남음 [2][3] | 보관 파일에 들어가는지 공개 문서에 적혀 있지 않아 서버 쪽 요청으로 다룸 |

보관 기간과 사람 검토 사본의 규칙은 [Gemini](index.md) 허브와 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에 정리했습니다. 보관 파일에 없는 기록이 서버에 남아 있을 수 있어서, 필요하면 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)을 함께 검토합니다.

**수집에는 권한이 필요합니다.** 내보내기는 계정 주인이 로그인해서 요청하는 기능이라, 조사에서 쓰려면 계정 주인의 협조나 적법한 절차가 필요합니다. 수집 절차와 보관 파일을 원본 그대로 지키는 방법은 [계정 데이터 내보내기로 수집](../../../03-techniques/acquisition/export-collection.md)에서 다룹니다.

## 직접 분석해 보기

**헥스로 한 번.** 보관 파일을 풀기 전에 압축 파일의 해시를 남기고, 푼 뒤 Takeout 폴더 아래 파일을 모두 나열합니다. 활동 파일로 보이는 파일의 첫 바이트가 `5B`(`[`)이면 JSON 배열이고, `3C`(`<`)이면 HTML 입니다. JSON 이면 앞부분에서 `"header"` 와 `"Gemini Apps"` 문자열을 찾아 레코드 경계를 봅니다. 파일 이름과 폴더 이름이 영어가 아니어도 이 방법으로 가릴 수 있습니다.

**도구로 한 번.** JSON 파일이면 `jq` 로 레코드 수와 필드를 먼저 셉니다. 아래 명령은 Gemini 레코드 수, 필드 이름별 개수, 답변 HTML 이 있는 레코드 수를 차례로 보여 줍니다.

```sh
jq '[.[] | select(.header=="Gemini Apps" or .header=="Bard")] | length' MyActivity.json
jq '[.[] | keys[]] | group_by(.) | map({(.[0]): length}) | add' MyActivity.json
jq '[.[] | select(.safeHtmlItem)] | length' MyActivity.json
```

그다음 AI-Conversation-Toolkit 의 `scripts/gemini_extractor.py` [5] 나 gemini-to-obsidian [4] 같은 변환 도구로 읽기 쉬운 글로 바꿉니다. 도구 출력은 위 "함정과 한계" 대로 레코드 수와 시각을 원본과 맞춰 본 뒤에 씁니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 브라우저 방문·다운로드 기록 | 웹 판 사용 시각, 보관 파일을 받은 때 | [웹 브라우저](web.md) |
| Chrome 설정 키 | 브라우저 안의 Gemini 창 사용 설정 | [Chrome 통합](chrome.md) |
| 휴대폰 앱 흔적 | 설치와 권한 | [Android 앱](android.md), [iOS 앱](ios.md) |
| 보관 설정과 삭제 원리 | 기록이 빠지는 이유 | [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md) |
| 시각 정렬 | 기기 흔적과 `time` 값을 한 줄로 세우기 | [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md) |

## 실습

시험용 계정으로 보관 파일을 만들어 아래 질문을 풀어 봅니다.

1. "Gemini" 항목과 "Gemini Apps" 활동 항목을 따로 내보내면 각 보관 파일에 무엇이 들어갑니까?
2. 계정 언어를 한국어로 두고 내보내면 활동 폴더와 파일 이름, `title` 앞말은 어떻게 나옵니까?
3. 답변 HTML(`safeHtmlItem`)이 있는 레코드는 몇 개이고, 이미지 생성 레코드에는 무엇이 들어갑니까?
4. 활동 저장을 끈 상태에서 나눈 대화가 72시간 안에 요청한 보관 파일에 들어갑니까?
5. 한 대화 창에서 30분 넘게 쉬었다가 이어 물으면 변환 도구는 그 대화를 몇 개로 나눕니까?

## 참고 문헌

1. Google, "Download your Gemini Apps data" — https://support.google.com/gemini/answer/16920332?hl=en (2026-09-25 열람)
2. Google, "Gemini Apps Privacy Hub" — https://support.google.com/gemini/answer/13594961 (2026-09-25 열람)
3. Google, "Manage & delete your activity in Gemini Apps" — https://support.google.com/gemini/answer/13278892 (2026-09-25 열람)
4. Coryrichter94/gemini-to-obsidian — https://github.com/Coryrichter94/gemini-to-obsidian , `README.md`, `gemini-to-obsidian.py` (2025-10-02 커밋 판)
5. silver-gr/AI-Conversation-Toolkit — https://github.com/silver-gr/AI-Conversation-Toolkit , `docs/gemini-extractor.md`(2025-12-16 커밋 판), `scripts/gemini_extractor.py`(2026-07-07 커밋 판)
6. joshuaswarren/remnic — https://github.com/joshuaswarren/remnic , `packages/import-gemini/src/parser.ts` (2026-06-05 커밋 판)
