---
title: "Microsoft Copilot 계정 데이터 내보내기"
parent: "Microsoft Copilot"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 270
---

# 계정 데이터 내보내기 (Data Export)

소비자용 Microsoft Copilot 의 활동 기록은 계정 주인이 개인정보 대시보드에서 CSV 파일 하나로 내보낼 수 있고, 이 파일에는 대화 제목·시각·말한 쪽·본문이 한 줄씩 들어 있어서 기기 흔적으로 알기 어려운 프롬프트와 응답을 얻는 공식 통로가 됩니다.

CSV 칸 구성은 공식 문서에 없고, 아래 내용은 2026년 7월 내보내기 파일 기준입니다[6][7].

## 무엇을 기록하나 · 왜 생기나

활동 기록은 Copilot 과 나눈 대화의 프롬프트와 응답이고, 사용자는 이 기록을 개인정보 대시보드에서 보고 내보내고 지울 수 있습니다[2][3][4]. 내보내기 파일은 계정 주인이 대시보드에서 직접 요청해야 생기므로, 기기에서 이 파일이 나오면 누군가 그 계정으로 내보내기를 요청한 적이 있다는 뜻이 됩니다. 다만 파일은 다른 곳에서 받아 옮겨 왔을 수도 있습니다.

대시보드는 활동 기록을 두 갈래로 나눠 관리하고, 두 갈래는 따로 내보내고 따로 지웁니다[3]. 한쪽만 받으면 다른 쪽 대화가 빠지니, 계정 주인이 어느 쪽을 썼는지 모를 때는 둘 다 받습니다.

| 갈래 | 들어가는 대화 |
|---|---|
| "Copilot 앱" (예: `copilot.microsoft.com`) | Copilot 앱에서 나눈 대화 |
| "Microsoft 365 앱·Chat" | Excel, OneNote, Outlook, PowerPoint, Teams, Word 안의 Copilot 과, Copilot 앱 안의 Chat |

회사·학교 계정의 대화는 이 대시보드가 아니라 조직의 보존·eDiscovery·감사 정책을 따르고, [Microsoft Purview로 본 Copilot 기록](../../network-enterprise/purview-copilot.md)과 [Microsoft 365 Copilot](../../office-integrations/m365-copilot.md)에서 다룹니다.

## 위치와 버전별 차이

대시보드 주소는 `account.microsoft.com/privacy` 이고, 들어가는 길은 다음과 같습니다[3].

```
개인정보 대시보드 → Privacy > Empower your productivity > Copilot > Your Copilot app activity history
```

내보내기는 `https://account.microsoft.com/privacy/copilot` 에서 "Your Copilot activity history" 의 "Export all activity history" 를 고르면 됩니다[6][8]. 이 메뉴가 어느 갈래의 파일을 주는지는 공개 자료에 없으니, 두 갈래를 따로 받아 첫 줄의 칸 이름을 나란히 비교합니다.

받은 파일 이름은 `copilot-activity-history.csv` 입니다[7][8]. 다만 이름이 다를 수 있고 화면 문구와 형식도 바뀔 수 있습니다[8]. 그래서 기기에서 찾을 때는 이름보다 첫 줄의 칸 이름으로 찾습니다. 다른 서비스의 내보내기 형식과 견준 내용은 [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md)에 있습니다.

## 구조

파일 하나에 모든 대화가 들어 있고, 한 줄이 말 한 번입니다. 첫 줄의 칸 이름은 `Conversation,Time,Author,Message` 이고, 이 첫 줄로 형식을 알아볼 수 있습니다[6][7].

| 칸 | 담는 것 | 근거 |
|---|---|---|
| `Conversation` | 대화 제목. 대화를 가르는 유일한 값 | [6] |
| `Time` | 날짜와 시각. `2026-03-02T10:15:07`(만든 예시) 모양이고 시간대 표시가 없음 | [6] |
| `Author` | `Human`(사용자) 또는 `AI`(Copilot) | [6][7] |
| `Message` | 본문. Markdown 이 그대로 들어 있고 여러 줄일 수 있음 | [6] |

파일 모양은 다음과 같습니다[6].

- 맨 앞에 UTF-8 BOM(`EF BB BF`) 이 있습니다.
- 줄과 줄 사이는 CRLF 로 나누고, 따옴표로 묶은 본문 안의 줄바꿈은 LF 입니다.
- 본문에 쉼표·따옴표·빈 줄이 들어가서, 줄 단위로 자르지 말고 RFC 4180 규칙을 따르는 CSV 읽기 도구로 읽어야 합니다.
- 대화 ID 와 메시지 ID 가 없습니다.

아래는 명세만 보고 만든 예시입니다. 제목·시각·본문은 모두 지어낸 값입니다.

```
Conversation,Time,Author,Message
"여행 준비물 정리",2026-03-02T10:15:07,AI,"**준비물:** 여권, 충전기
그 밖에 필요한 것도 알려 드릴까요?"
"여행 준비물 정리",2026-03-02T10:15:07,Human,"2박 3일 여행 준비물 알려 줘"
"엑셀 수식 질문",2026-03-01T21:40:52,AI,"`SUMIF` 를 쓰면 됩니다."
"엑셀 수식 질문",2026-03-01T21:40:52,Human,"조건 맞는 칸만 더하려면?"
```

줄 순서에는 규칙이 둘 있습니다[6]. 첫째, 파일 전체에서도 한 대화 안에서도 최신 줄이 먼저 나옵니다. 둘째, AI 응답 줄과 그 응답을 부른 Human 줄이 같은 시각을 달고 나오는 일이 많고, llm-aggregator.ts 가 본 실제 파일에서는 2613줄 가운데 1290줄이 옆 줄과 시각이 같았습니다. 같은 시각 안에서는 AI 줄이 Human 줄보다 앞에 나오므로 파일 순서가 곧 "최신 것부터" 입니다.

## 증거로서 의미

**증명하는 것.** CSV 에 줄이 있으면, 내보낸 시점에 그 계정의 활동 기록에 그 제목·시각·말한 쪽·본문이 있었다고 쓸 수 있습니다. `Author` 가 `Human` 인 줄은 그 계정 쪽에서 입력한 프롬프트이고, `AI` 인 줄은 Copilot 이 돌려준 응답입니다. 기기에서 CSV 파일이 나오면 그 파일이 그 기기에 저장돼 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** CSV 에 없는 대화를 처음부터 없었다고 쓸 수는 없는데, 사용자가 지웠거나 다른 갈래에 있거나 로그인하지 않고 썼을 수 있기 때문입니다. 계정 기록은 그 계정으로 로그인한 누군가의 활동이라서 실제로 입력한 사람은 기기 흔적과 함께 따지고([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)), CSV 에는 기기나 IP 를 알려 주는 칸이 없어서 어느 기기에서 보냈는지도 이 파일만으로는 단정하지 않습니다. 대화 ID 가 없어서 제목이 같은 대화가 둘이면 CSV 만으로는 둘을 나눌 수 없습니다. CSV 는 글자 파일이라 누구나 고쳐 저장할 수 있으니, 기기에서 찾은 파일은 받은 경로와 파일 시각을 함께 보고 원본인지 판단합니다.

보고서에는 "이 계정의 Copilot 활동 기록 내보내기에 이 제목의 대화가 있고, Human 줄의 시각 값은 이것이다" 처럼 파일이 말하는 만큼만 씁니다.

## 시각 해석

`Time` 칸은 초 단위까지 적고 시간대 표시가 없습니다[6]. 그래서 이 값이 UTC 인지 계정·기기의 현지 시각인지는 파일만 보고 정할 수 없습니다. 시험용 계정으로 시각을 적어 둔 대화를 하나 만든 뒤 내보내서 맞춰 보거나, 같은 대화의 브라우저 방문 기록·네트워크 기록 시각과 비교해 기준을 정합니다.

분석 도구가 시간대 없는 값을 어떻게 읽는지도 따로 확인합니다. llm-aggregator.ts 는 이 값을 JavaScript `Date.parse` 로 읽고 `toISOString` 으로 바꾼 뒤 끝에 `Z` 를 붙여 저장합니다[6]. 원본에 없던 시간대 표시가 도구 출력에 붙는 셈이니, 도구 출력보다 원본 문자열을 기준으로 삼습니다.

같은 시각이 Human 줄과 AI 줄에 함께 붙으므로, 이 시각 값만으로는 프롬프트를 보낸 때와 응답이 끝난 때를 나눌 수 없습니다. 기기에서 찾은 CSV 의 파일 시스템 시각은 대화 시각이 아니라 파일을 받거나 옮긴 때를 가리킵니다. 여러 기록을 한 시간 축에 놓는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)을 따릅니다.

## 함정과 한계

**줄 순서.** 시각으로 정렬하면 같은 시각 안에서 AI 응답이 프롬프트보다 앞에 남습니다. llm-aggregator.ts 는 그래서 시각으로 정렬하지 않고 한 대화의 줄 순서를 그대로 뒤집습니다[6]. ai-suite 의 분할 스킬은 시각으로 오름차순 정렬하고, 같은 시각이면 `Human` 줄을 앞에 둡니다[7]. 한 시각에 Human 줄과 AI 줄이 하나씩이면 두 방법의 결과가 같지만, 한 시각에 줄이 셋 이상이면 달라질 수 있으니 도구가 어느 방법을 쓰는지 확인합니다.

**들어가는지 공식 문서에 설명이 없는 것.** 아래 항목은 검체로 확인합니다.

| 항목 | 공식 문서가 밝힌 것 | 확인하는 법 |
|---|---|---|
| 저장한 메모리(개인화) | 설정 → Personalization → "Saved memories" 옆 "Manage" 에서 하나씩 지우거나 "Delete all memories" 로 지움[2] | 시험 계정에 메모리를 저장한 뒤 내보내서 CSV 에 나오는지 봄 |
| 로그인하지 않고 쓴 대화 | 개인정보 안내는 개인 Microsoft 계정으로 로그인했을 때 적용[2] | 로그인하지 않고 대화한 뒤 같은 기기에서 로그인해 내보내서 그 대화가 나오는지 봄 |
| 대화에 올린 파일·이미지 | 대시보드 안내는 이미지가 있으면 "How to view images in exports or downloads from the privacy dashboard" 문서를 보라고 함[3] | 이미지를 넣은 대화를 내보내서 CSV 안의 모양과 따로 오는 파일이 있는지 봄 |

"Saved memories" 설정을 꺼도 이미 저장된 메모리는 저절로 지워지지 않습니다[2]. 그래서 설정이 꺼져 있다는 사실만으로 메모리가 비어 있다고 보지 않습니다. Personalization 아래에는 "Web search", "One shared experience", "Allow ads personalization" 켬/끔도 있고, 18세 미만에게는 맞춤 광고를 보여 주지 않습니다[2].

**지우기와 내보내기의 순서.** 전체 삭제는 대시보드에서 "Delete all activity history" 를 누르고, 확인 창 "Are you sure you want to clear your Copilot activity history?" 에서 Clear 를 고르는 순서입니다[3]. 서버에서 삭제가 끝나는 시점과 활동 기록의 보관 기간은 공식 문서에 나오지 않으니 필요하면 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)으로 묻습니다. 내보내기는 사본을 만들 뿐 서버 기록을 지우지 않으므로, 내려받은 뒤 대시보드에서 기록을 지웠다면 기기의 CSV 에만 대화가 남아 있을 수 있습니다. 반대로 지운 뒤에 내보냈다면 CSV 에는 지운 대화가 없습니다. 대화 하나를 앱이나 웹에서 지우는 방법은 [웹 브라우저](web.md)에, 보관과 삭제의 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

**수집 조건과 제품 이름.** 내보내기는 계정 주인이 로그인해서 하는 기능이라, 조사에서 쓰려면 계정 주인의 협조나 적법한 절차가 필요합니다. 수집 절차와 받은 파일을 원본 그대로 지키는 방법은 [계정 데이터 내보내기로 수집](../../../03-techniques/acquisition/export-collection.md)에 있습니다. "Copilot" 이라는 이름이 붙은 제품이 여럿이라서 계정 종류부터 가립니다. 이 페이지의 대시보드 안내는 개인 Microsoft 계정에만 적용됩니다.

## 직접 분석해 보기

**헥스로 한 번.** 파일 앞부분을 헥스로 열어 BOM 과 첫 줄을 확인합니다. 아래는 명세[6]로 만든 예시입니다.

```
00000000  EF BB BF 43 6F 6E 76 65 72 73 61 74 69 6F 6E 2C  ...Conversation,
00000010  54 69 6D 65 2C 41 75 74 68 6F 72 2C 4D 65 73 73  Time,Author,Mess
00000020  61 67 65 0D 0A                                   age..
```

`EF BB BF` 가 UTF-8 BOM 이고, 첫 줄 끝의 `0D 0A` 가 CRLF 입니다. 본문 안으로 들어가면 따옴표(`22`) 안에서 `0A` 만 나오는 곳이 칸 안의 줄바꿈입니다. 첫 줄이 이와 다르면 형식이 바뀐 것이니 칸 이름을 새로 기록합니다.

**공개 도구로 한 번.** 받은 CSV 의 해시를 먼저 남기고, 사본을 Python 의 `csv` 모듈로 읽습니다. 아래 코드는 만든 예시이고 파일 이름도 가짜입니다. 대화 제목별로 줄을 모은 뒤 줄 순서를 뒤집어 시간 순서로 돌리고, 같은 시각을 단 줄이 몇 개인지 셉니다.

```python
# 만든 예시: 제목별로 묶고 파일 순서를 뒤집어 시간 순서로 본다
import csv
from collections import defaultdict

with open("copilot_activity_sample.csv", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.reader(f))

print("칸 이름:", rows[0])          # Conversation,Time,Author,Message 인지 확인
talks = defaultdict(list)
for title, time, author, message in rows[1:]:
    talks[title].append((time, author, message))

for title, lines in talks.items():
    lines.reverse()                  # 최신 것부터 → 오래된 것부터
    ties = sum(1 for a, b in zip(lines, lines[1:]) if a[0] == b[0])
    print(title, "줄", len(lines), "같은 시각 이웃", ties)
    for time, author, message in lines:
        print(" ", time, author, message[:40].replace("\n", " "))
```

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 브라우저 방문·다운로드 기록 | 대시보드를 연 때, CSV 를 받은 때, 대화 시각의 기준 | [웹 브라우저](web.md), [크롬 계열 브라우저 (Windows 판)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html) |
| Windows 앱 흔적 | 같은 계정을 앱에서도 썼을 가능성 | [Windows 앱](windows.md) |
| 네트워크 기록 | 서비스와 통신한 시간대 | [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) |
| 첨부와 생성물 | 본문 속 프롬프트·첨부·생성물을 가르는 법 | [프롬프트·첨부·생성물 구분하기](../../../01-foundations/concepts/prompt-attachment-output.md) |
| 서버·기기 저장 원리 | 내보내기에 없는 기록이 어디 있을 수 있나 | [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md) |

## 실습

Copilot 내보내기 파일을 담은 공개 검체가 없어서, 시험용 개인 Microsoft 계정으로 직접 만들어 풉니다.

1. 시각을 적어 둔 대화를 하나 만든 뒤 내보내면 `Time` 값은 UTC 입니까, 계정이나 기기의 현지 시각입니까?
2. "Copilot 앱" 갈래와 "Microsoft 365 앱·Chat" 갈래를 따로 내보내면 첫 줄의 칸 이름은 같습니까?
3. 제목이 같은 대화를 두 번 만들면 CSV 에서 둘을 가를 수 있습니까?
4. 대화에 이미지를 넣은 뒤 내보내면 이미지는 `Message` 안에 어떤 모양으로 남고, 파일이 따로 옵니까?
5. "Saved memories" 에 저장한 메모리가 CSV 에 들어갑니까?

## 참고 문헌

1. Microsoft Privacy Statement (Microsoft Copilot 절), 2026-09 갱신 — https://www.microsoft.com/en-us/privacy/privacystatement
2. Microsoft Copilot for individuals: your privacy controls and choices — https://support.microsoft.com/privacy/microsoft-copilot/privacy-controls
3. Manage your Copilot activity history in the privacy dashboard — https://support.microsoft.com/privacy/manage-your-copilot-activity-history-in-the-privacy-dashboard
4. Microsoft Copilot for individuals: your activity history — https://support.microsoft.com/privacy/microsoft-copilot/activity-history
5. Updated Windows and Microsoft Copilot Chat experience (Microsoft Learn, 2026-08-18 갱신) — https://learn.microsoft.com/en-us/windows/client-management/manage-windows-copilot
6. vladsadovsky/llm-aggregator.ts, `electron/services/import/archive/parsers/copilotCsv.ts` (2026-07-27 수정) — https://github.com/vladsadovsky/llm-aggregator.ts
7. baneeishaque/ai-suite, `.agents/skills/copilot-activity-history-split/SKILL.md` (2026-08-07 수정) — https://github.com/baneeishaque/ai-suite
8. MaxAnkum/copilot-history-memory-mart, `README.md` (2025-09-20 수정) — https://github.com/MaxAnkum/copilot-history-memory-mart
