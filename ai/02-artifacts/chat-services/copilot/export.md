---
title: "Microsoft Copilot 계정 데이터 내보내기"
parent: "Microsoft Copilot"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 270
---

# 계정 데이터 내보내기 (Data Export)

소비자용 Microsoft Copilot 의 활동 기록은 계정 주인이 개인정보 대시보드에서 CSV 파일로 내보낼 수 있어서, 기기 흔적으로는 알 수 없는 프롬프트와 응답을 얻는 공식 통로가 되고, 내려받은 파일 자체도 기기에 남아 증거가 됩니다.

> 확인 날짜: 2026-09-25. Microsoft 공식 문서(개인정보 처리방침, 활동 기록 안내, 개인정보 대시보드 안내, 개인정보 제어 안내)만 근거로 썼습니다. 개인정보 제어 안내와 활동 기록 안내는 2026-08-18 앱 버전 갱신을 언급합니다. 이 핸드북은 실제 내보내기 파일을 열어 보지 않았고, 이 PC 에서 Copilot 관련 폴더를 관찰하지도 않아서 파일 안의 칸 이름과 구조는 적지 않았습니다.

## 무엇을 받나

Microsoft 는 활동 기록을 "Copilot 과 나눈 대화의 프롬프트와 응답" 이라고 설명하고, 사용자가 이 기록을 개인정보 대시보드(`account.microsoft.com/privacy`)에서 보고 내보내고 지울 수 있다고 밝힙니다. 대시보드에서 들어가는 길은 다음과 같습니다.

```
개인정보 대시보드 → Privacy > Empower your productivity > Copilot > Your Copilot app activity history
```

대시보드는 활동 기록을 두 갈래로 나눠 관리하고, 두 갈래는 따로 내보내고 따로 지웁니다. 한쪽만 받으면 다른 쪽 대화는 빠지니, 계정 주인이 어느 쪽을 썼는지 모를 때는 둘 다 받습니다.

| 갈래 | 들어가는 대화 |
|---|---|
| "Copilot 앱" (예: `copilot.microsoft.com`) | Copilot 앱에서 나눈 대화 |
| "Microsoft 365 앱·Chat" | Excel, OneNote, Outlook, PowerPoint, Teams, Word 안의 Copilot 과, Copilot 앱 안의 Chat |

내보내기 파일 형식은 CSV 입니다. 활동 기록에 이미지가 있으면 대시보드 안내가 별도 문서("How to view images in exports or downloads from the privacy dashboard")를 따르라고 하니, 내보내기에 이미지가 함께 들어갈 수 있습니다. CSV 의 칸 이름, 한 파일에 담기는 범위, 파일을 받기까지 걸리는 시간은 확인하지 못했습니다. 서비스마다 다른 내보내기 형식을 견준 내용은 [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md)에, 프롬프트·첨부·생성물을 가려 읽는 방법은 [프롬프트·첨부·생성물 구분하기](../../../01-foundations/concepts/prompt-attachment-output.md)에 있습니다.

## 들어가는지 모르는 것

내보내기가 계정의 모든 기록을 담는다고 볼 근거는 없습니다. 아래 항목은 공식 문서에 설명이 없어서 검체로 확인해야 합니다.

| 항목 | 알려진 것 | 확인 상태 |
|---|---|---|
| 저장한 메모리(개인화) | 설정 → Personalization → "Saved memories" 옆 "Manage" 에서 하나씩 지우거나 "Delete all memories" 로 지움 | CSV 에 들어가는지 확인하지 못함 |
| 로그인하지 않고 쓴 대화 | 개인정보 안내는 개인 Microsoft 계정으로 로그인했을 때만 적용 | 처리 방식을 확인하지 못함 |
| 대화에 올린 파일 | 공식 문서에 설명 없음 | 내보내기에 들어가는지, 얼마나 보관하는지 확인하지 못함 |
| 회사·학교 계정 대화 | 조직의 보존·eDiscovery·감사 정책을 따름 | 이 대시보드의 대상이 아님 |

"Saved memories" 설정을 꺼도 이미 저장된 메모리는 저절로 지워지지 않는다고 안내합니다. 그래서 설정이 꺼져 있다는 사실만으로 메모리가 비어 있다고 보지 않습니다. Personalization 아래에는 "Web search", "One shared experience", "Allow ads personalization" 켬/끔도 있고, 18세 미만에게는 맞춤 광고를 보여 주지 않는다고 밝힙니다. 회사 계정 쪽 기록은 [Microsoft Purview로 본 Copilot 기록](../../network-enterprise/purview-copilot.md)에서 다룹니다.

## 지우기와 내보내기

전체 삭제는 대시보드에서 "Delete all activity history" 를 누르고, 확인 창 "Are you sure you want to clear your Copilot activity history?" 에서 Clear 를 고르는 순서입니다. 삭제가 서버에서 실제로 언제 끝나는지와 활동 기록을 몇 달 보관하는지는 공식 문서에서 찾지 못했습니다. 대화 하나를 앱이나 웹에서 지우는 방법은 [웹 브라우저](web.md)에 있고, 보관과 삭제의 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에서 봅니다.

조사에서는 두 조작의 순서를 따져 봅니다. 내보내기는 사본을 만들 뿐 서버 기록을 지우지 않지만, 내려받은 뒤 대시보드에서 기록을 지웠다면 기기의 CSV 에만 대화가 남아 있을 수 있습니다. 반대로 지운 뒤에 내보냈다면 CSV 에는 지운 대화가 없습니다.

## 증거로서 의미

**증명하는 것.** 내보낸 CSV 에 대화가 있으면 내보낸 시점에 그 계정의 활동 기록에 그 프롬프트와 응답이 있었다고 쓸 수 있습니다. 기기에서 CSV 파일이 나오면 그 파일이 그 기기에 저장돼 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** CSV 에 없는 대화를 처음부터 없었다고 쓸 수는 없는데, 사용자가 지웠거나 다른 갈래에 있거나 로그인하지 않고 썼을 수 있기 때문입니다. 계정 기록은 그 계정으로 로그인한 누군가의 활동이라서 실제로 입력한 사람은 기기 흔적과 함께 따지고([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)), 어느 기기에서 보냈는지도 CSV 만으로는 단정하지 않습니다. CSV 는 글자 파일이라 누구나 고쳐 저장할 수 있어서, 기기에서 찾은 파일은 받은 경로와 파일 시각을 함께 보고 원본 여부를 판단합니다.

## 시각 해석

CSV 안에 시각 칸이 있는지, 있다면 어떤 형식과 기준(UTC 인지 현지 시각인지)인지는 확인하지 못했습니다. 기기에서 찾은 CSV 의 파일 시스템 시각은 내려받거나 옮긴 때에 따라 바뀌어서 대화 시각이 아니라 파일을 받은 때를 가리킵니다. 브라우저 다운로드 기록과 맞춰 보면 받은 시각을 좁힐 수 있고, 여러 기록을 한 시간 축에 놓는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)을 따릅니다.

## 함정과 한계

내보내기는 계정 주인이 로그인해서 하는 기능이라, 조사에서 쓰려면 계정 주인의 협조나 적법한 절차가 필요합니다. 수집 절차와 받은 파일을 원본 그대로 지키는 방법은 [계정 데이터 내보내기로 수집](../../../03-techniques/acquisition/export-collection.md)에 있고, 계정 주인의 협조를 얻을 수 없거나 내보내기에 없는 기록이 필요하면 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)을 검토합니다.

"Copilot" 이라는 이름이 붙은 제품이 여럿이라서 계정 종류부터 가립니다. 이 페이지의 대시보드 안내는 개인 Microsoft 계정에만 적용되고, 회사용 Copilot Chat 은 [Microsoft 365 Copilot](../../office-integrations/m365-copilot.md)에서 다룹니다. CSV 를 표 계산 프로그램으로 바로 열면 긴 글이 잘리거나 날짜 칸 모양이 바뀔 수 있으니, 원본 파일은 해시를 남기고 사본을 글자 편집기로 먼저 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** CSV 의 칸 구성과 글자 인코딩을 확인하지 못해서 이 페이지에는 헥스 예시를 싣지 않습니다. 검체에서는 파일 앞부분을 헥스로 열어 UTF-8 BOM(`EF BB BF`) 이 있는지부터 보고, 첫 줄의 칸 이름을 기록합니다.

**공개 도구로 한 번.** 받은 CSV 의 해시를 먼저 남기고, 사본을 CSV 를 읽는 공개 도구(예: Python 의 `csv` 모듈)로 읽어 칸 이름과 줄 수를 확인합니다. 아래 코드는 칸 이름을 모르는 상태를 전제로 만든 예시이고, 파일 이름도 가짜입니다.

```python
# 만든 예시: 칸 이름을 가정하지 않고 첫 줄과 줄 수만 확인한다
import csv
with open("copilot_activity_sample.csv", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.reader(f))
print("칸 이름:", rows[0])
print("데이터 줄 수:", len(rows) - 1)
```

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 브라우저 방문·다운로드 기록 | 대시보드를 연 때, CSV 를 받은 때 | [웹 브라우저](web.md) |
| Windows 앱 설치 흔적 | 같은 계정을 앱에서도 썼을 가능성 | [Windows 앱](windows.md) |
| 네트워크 기록 | 서비스와 통신한 시간대 | [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) |
| 서버·기기 저장 원리 | 내보내기에 없는 기록이 어디 있을 수 있나 | [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md) |

## 실습

Copilot 내보내기 파일을 담은 공개 검체는 이번 조사에서 확인하지 못했습니다. 시험용 개인 Microsoft 계정으로 아래 질문을 풀어 봅니다.

1. "Copilot 앱" 갈래와 "Microsoft 365 앱·Chat" 갈래를 따로 내보내면 각 CSV 의 칸 이름은 같습니까?
2. 대화에 이미지를 넣은 뒤 내보내면 이미지는 CSV 안에 어떤 모양으로 남고, 파일이 따로 옵니까?
3. "Saved memories" 에 저장한 메모리가 CSV 에 들어갑니까?
4. CSV 에 시각 칸이 있다면 UTC 입니까, 계정의 현지 시각입니까?

## 참고 문헌

1. Microsoft Privacy Statement (Microsoft Copilot 절), 2026-09 갱신 — https://www.microsoft.com/en-us/privacy/privacystatement
2. Microsoft Copilot for individuals: your privacy controls and choices — https://support.microsoft.com/privacy/microsoft-copilot/privacy-controls
3. Manage your Copilot activity history in the privacy dashboard — https://support.microsoft.com/privacy/manage-your-copilot-activity-history-in-the-privacy-dashboard
4. Microsoft Copilot for individuals: your activity history — https://support.microsoft.com/privacy/microsoft-copilot/activity-history
5. Updated Windows and Microsoft Copilot Chat experience (Microsoft Learn, 2026-08-18 갱신) — https://learn.microsoft.com/en-us/windows/client-management/manage-windows-copilot
