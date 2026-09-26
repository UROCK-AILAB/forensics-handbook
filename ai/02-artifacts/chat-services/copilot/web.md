---
title: "Microsoft Copilot 웹 브라우저"
parent: "Microsoft Copilot"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 220
---

# 웹 브라우저 (Web)

소비자용 Microsoft Copilot 을 브라우저에서 쓰면 기기에는 주로 브라우저의 방문 기록과 저장소가 남고, 대화 원본을 보고 내려받는 공식 통로는 계정의 개인정보 대시보드입니다.

## 무엇을 기록하나 · 왜 생기나

웹 주소는 `copilot.microsoft.com` 이고, 개인 Microsoft 계정으로 로그인해 쓰는 소비자용 서비스입니다. Copilot 은 프롬프트와 위치, 언어, 관련 설정을 써서 답을 만들고, 일부 시장에서는 대화 기록을 개인화에도 씁니다. 계정의 활동 기록은 사용자가 개인정보 대시보드에서 보고 내보내고 지울 수 있습니다. 대시보드는 활동 기록을 "Copilot 앱"(`copilot.microsoft.com`)과 "Microsoft 365 앱·Chat" 두 갈래로 나눠 관리하고, 웹에서 나눈 대화는 앞쪽 갈래에 들어갑니다. 내보내기 절차와 파일은 [계정 데이터 내보내기](export.md)에서 다룹니다.

기기 쪽 흔적은 브라우저가 사이트를 열 때 남기는 일반 기록입니다. 방문 기록, 쿠키, 캐시, Local Storage·IndexedDB 같은 사이트 저장소가 여기에 들지만, 이 가운데 어디에 대화 내용이 남는지, 어떤 키 이름을 쓰는지는 공식 문서에 나오지 않아 검체로 확인해야 합니다. 대화 사본이 기기에 남는지도 검체로 가려야 하므로, 이 페이지는 방문 사실과 서버 쪽 기록을 중심으로 씁니다.

회사·학교(Microsoft Entra) 계정은 소비자용 Copilot 에 로그인하지 못하고, 브라우저에서 `https://m365.cloud.microsoft/chat` 으로 넘어갑니다[5]. 이 주소는 기업 데이터 보호 약정이 붙는 별개 제품이라서 [Microsoft 365 Copilot](../../office-integrations/m365-copilot.md)과 [Microsoft Purview로 본 Copilot 기록](../../network-enterprise/purview-copilot.md)에서 따로 봅니다. Edge 사이드바처럼 브라우저 안에 들어간 Copilot 은 [브라우저에 들어간 AI](../../office-integrations/browser-builtin-ai.md)에서 다룹니다.

조직이 수집 정책을 두면 소비자용 Copilot 대화도 조직 쪽에 남을 수 있습니다. Microsoft Purview 보존 정책의 위치 목록에는 "Other AI apps" 아래 "Microsoft Copilot (consumer version)" 이 있고, 이 갈래의 프롬프트와 응답은 조직에 내용을 잡도록 설정한 수집 정책(collection policy)이 있을 때만 보존 대상이 됩니다[6]. 잡힌 메시지는 AI 앱을 쓴 사용자의 Exchange Online 사서함 안 숨은 폴더에 저장되고, 관리자는 이 폴더를 eDiscovery 로 검색합니다[6]. "Other AI apps" 의 브라우저 대화는 eDiscovery 에서 item class `IPM.SkypeTeams.Message.CloudAIApp.SaaS.<AppID>` 로 찾습니다[7]. 이 사건에서 실제로 대화가 잡혔는지는 조직의 Purview 수집 정책과 검색 결과로 확인합니다.

## 위치

| 어디 | 무엇을 보나 | 근거 |
|---|---|---|
| 브라우저 방문 기록 | `copilot.microsoft.com`, `m365.cloud.microsoft` 방문 | 도메인은 공식 문서. 대화별 ID 가 URL 에 붙는지는 검체로 확인 |
| 쿠키·캐시·Local Storage·IndexedDB | 로그인 상태와 화면 데이터 | 대화 내용이 들어 있는지와 키 이름은 검체로 확인 |
| 개인정보 대시보드(`account.microsoft.com/privacy`) | 계정의 Copilot 활동 기록 | 공식 문서[4] |
| 조직 사용자의 Exchange Online 사서함 숨은 폴더 | 조직이 수집 정책으로 잡은 소비자용 Copilot 프롬프트·응답 | 공식 문서[6][7]. 수집 정책이 있을 때만 |

브라우저 저장소의 파일 위치와 읽는 법은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html)와 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html) 페이지를 따르고, 서버와 기기 가운데 어디에 무엇이 있는지의 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md)에 모아 두었습니다.

## 관련 설정

설정에는 "Bring over your browsing data from Microsoft Edge" 켬/끔이 있고, 지금은 미국에 기반한 Microsoft 계정만 이 설정을 쓸 수 있습니다. 대화 하나는 채팅 목록에서 대화를 고르고 "…More" → "Delete" 로 지우고, 대화 전체는 개인정보 대시보드의 Copilot 활동 기록 관리에서 지웁니다[4]. 삭제와 보관의 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)를 함께 봅니다.

## 증거로서 의미

**증명하는 것.** 방문 기록에 `copilot.microsoft.com` 이 있으면 그 브라우저 프로필이 그 시각에 이 주소를 열었다고 쓸 수 있습니다. 대시보드에서 내보낸 활동 기록에 대화가 있으면 그 계정으로 그 프롬프트와 응답을 주고받은 기록이 서버에 있다고 쓸 수 있습니다. 조직의 eDiscovery 검색에서 위 item class 의 항목이 나오면 그 사서함 사용자의 소비자용 Copilot 대화를 조직이 수집한 기록이 있다고 쓸 수 있습니다.

**증명하지 못하는 것.** 방문 기록만으로는 프롬프트를 실제로 보냈는지, 무엇을 물었는지, 어느 계정으로 로그인했는지 알 수 없습니다. 브라우저 프로필과 계정은 그 앞에 앉은 사람을 알려 주지 않아서, 사람을 가리는 일은 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)를 따릅니다. 조직 사서함에 항목이 없어도 수집 정책이 없었거나 범위 밖이었을 수 있어서, 대화가 없었다는 근거가 되지 않습니다.

## 시각 해석

방문 기록의 시각 형식과 기준 시간대는 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html) 페이지를 따릅니다. 방문 시각은 페이지를 연 시각이지 대화를 보낸 시각이 아닙니다. 대화별 ID 가 URL 에 붙는지는 검체로 확인하고, 확인하기 전에는 방문 기록 한 줄을 대화 하나와 짝짓지 않습니다. 대화 시각은 내보낸 활동 기록에서 찾고, 그 파일의 시각 칸 이름과 기준은 [계정 데이터 내보내기](export.md)에서 검체로 확인합니다.

## 함정과 한계

서비스에서 대화를 지우는 조작과 브라우저 방문 기록을 지우는 조작은 서로 다른 곳에서 일어나서, 한쪽만 지워진 상태가 나올 수 있습니다. 방문 기록이 없다고 쓰지 않았다고 보지 않고, 대시보드에 대화가 없다고 대화가 없었다고 보지도 않습니다. 개인 계정용 개인정보 안내는 개인 Microsoft 계정으로 로그인했을 때만 적용되고, 회사 계정 대화는 조직의 보존·감사 정책을 따르니 계정 종류부터 가립니다. 방문 기록에 `m365.cloud.microsoft` 가 보이면 소비자용이 아닌 회사용 제품일 수 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 브라우저 저장소에 Copilot 대화가 어떤 형식으로 남는지는 공개된 분석 자료가 없어 검체로 확인해야 하므로, 여기에는 헥스 예시를 싣지 않습니다. 방문 기록 데이터베이스를 헥스로 따라가는 방법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html) 페이지에 있습니다.

**공개 도구로 한 번.** 브라우저 방문 기록 사본을 SQLite 도구로 열고 URL 칸에서 `copilot.microsoft.com` 과 `m365.cloud.microsoft` 를 찾아 방문 시각과 횟수를 뽑습니다. 원본 파일은 직접 열지 않고, 브라우저를 닫은 상태에서 뜬 사본으로 작업합니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 |
|---|---|
| [계정 데이터 내보내기](export.md) | 서버에 남은 프롬프트·응답 |
| [Microsoft Purview로 본 Copilot 기록](../../network-enterprise/purview-copilot.md) | 조직이 수집 정책으로 잡은 대화 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 브라우저 기록을 지웠을 때 남는 DNS·프록시 접속 |
| [Windows 앱](windows.md) | 같은 계정을 앱에서도 썼는지 |
| [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md) | 방문·대화·파일 활동을 한 시간 축에 놓기 |

## 실습

시험용 개인 Microsoft 계정으로 직접 만든 검체에서 다음을 풀어 봅니다. 방문 기록에 남은 `copilot.microsoft.com` 방문 시각과 내보낸 활동 기록의 대화 시각은 몇 분 차이가 나는가? 대화 하나를 "…More" → "Delete" 로 지운 뒤 방문 기록과 내보내기 결과는 각각 어떻게 달라지는가?

## 참고 문헌

1. Microsoft Privacy Statement (Microsoft Copilot 절), 2026-09 갱신 — https://www.microsoft.com/en-us/privacy/privacystatement
2. Microsoft Copilot for individuals: your privacy controls and choices — https://support.microsoft.com/privacy/microsoft-copilot/privacy-controls
3. Microsoft Copilot for individuals: your data, privacy, and responsible AI — https://support.microsoft.com/privacy/microsoft-copilot/overview
4. Manage your Copilot activity history in the privacy dashboard — https://support.microsoft.com/privacy/manage-your-copilot-activity-history-in-the-privacy-dashboard
5. Updated Windows and Microsoft Copilot Chat experience (Microsoft Learn) — https://learn.microsoft.com/en-us/windows/client-management/manage-windows-copilot
6. Learn about retention for Copilot & AI apps (Microsoft Learn, ms.date 2025-09-23) — https://learn.microsoft.com/en-us/purview/retention-policies-copilot
7. Search for and delete AI application data in eDiscovery (Microsoft Learn, ms.date 2026-06-19) — https://learn.microsoft.com/en-us/purview/edisc-search-copilot-data
