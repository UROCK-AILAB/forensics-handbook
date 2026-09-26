---
title: "Google Workspace의 Gemini"
parent: "아티팩트 · 업무 도구 속 AI"
nav_order: 520
---

# Google Workspace의 Gemini (Workspace Gemini)

회사·학교 계정으로 Docs·Sheets·Slides·Drive·Gmail·Meet 옆 패널이나 Gemini 앱에서 쓴 Gemini 대화는 Google 서버에 있고, 보관 기간은 관리자가 정하며, 조사는 관리자 쪽 Vault 와 감사 로그에서 시작합니다.

확인 날짜는 2026-09이고, 근거는 Google 의 "Generative AI in Google Workspace Privacy Hub"(마지막 갱신 2026-08-14) 한 편입니다. 기기 쪽 흔적은 실제 기기에서 확인해야 합니다.

## 무엇을 기록하나 · 왜 생기나

Workspace 계정의 Gemini 는 쓰는 곳에 따라 저장 규칙이 셋으로 갈립니다. Docs·Sheets·Slides·Drive·Gmail·Meet 안의 옆 패널에서 쓰는 "Workspace 앱 속 Gemini", Workspace 계정으로 들어가는 "Gemini 앱", 그리고 프롬프트와 응답을 세션이 끝나면 보관하지 않는 "Gemini Notebook" 입니다. 앞의 두 경우는 Google 서버에 남는 대화의 보관 기간을 관리자가 정하고, Gemini Notebook 은 노트북 자체는 사용자가 지우거나 Google Takeout 으로 내보낼 수 있지만 프롬프트와 응답은 남기지 않습니다.

개인 Google 계정으로 쓰는 Gemini 는 계정 종류와 관리 주체가 달라서 [Gemini](../chat-services/gemini/index.md) 페이지에서 따로 다룹니다. 조사를 시작할 때 그 대화가 개인 계정의 것인지 Workspace 계정의 것인지부터 구분해야, 어디에 요청하고 어떤 보관 규칙을 적용할지가 정해집니다.

## 위치와 버전별 차이

| 쓰는 곳 | 대화 원본 | 보관 기간 | 삭제 |
|---|---|---|---|
| Workspace 앱 속 Gemini(Docs·Sheets·Slides·Drive·Gmail·Meet 옆 패널) | Google 서버 | 관리자가 정한 대로 90일에서 무기한까지 | 관리자가 막지 않으면 사용자가 직접 지울 수 있습니다 |
| Gemini 앱(Workspace 계정) | Google 서버 | 관리자가 정한 대로 최대 36개월, 기본값 18개월 | 자동 삭제는 3·18·36개월 중에서 고릅니다 |
| Gemini Notebook | 프롬프트·응답은 세션이 끝나면 보관하지 않음 | — | 노트북은 사용자가 지우거나 Takeout 으로 내보낼 수 있습니다 |
| Workspace 사용자의 Gemini in Chrome | 선택한 탭의 URL 과 페이지 내용을 모아 처리 | 문서에 나오지 않음 | — |

문서에 나오는 대화 원본의 위치는 Google 서버뿐이라서, 조사는 서버 쪽 자료를 중심으로 짭니다. 브라우저나 기기에 대화 본문이 남는지는 문서에 나오지 않으므로 실제 기기에서 직접 확인합니다. 문서가 Takeout 내보내기를 적은 곳은 Gemini Notebook 뿐이라서, Workspace 앱 속 Gemini 나 Gemini 앱 대화를 사용자 쪽 내보내기로 받으려면 먼저 실제로 내려받아 대화가 들어 있는지 봅니다. 내보내기 일반론은 [계정 데이터 내보내기로 수집](../../03-techniques/acquisition/export-collection.md)에서 다룹니다.

Chrome 안에서 Workspace 계정으로 쓰는 Gemini 는 브라우저 쪽 흔적과 함께 봐야 해서 [브라우저에 들어간 AI](browser-builtin-ai.md)에서 다룹니다.

## 구조

문서에 나오는 관리자 조회 경로는 두 가지입니다. 관리자는 Google Vault 로 Workspace 앱 속 Gemini 대화를 포함한 Workspace 데이터의 보존을 관리하고, 관리자용 감사 로그로 Gemini 사용과 상호작용을 추적할 수 있다고 문서에 적혀 있습니다.

Vault 에서 Gemini 대화를 가리키는 데이터 종류 이름과 감사 로그의 로그 이름·이벤트 이름·필드 이름은 문서에 나오지 않습니다. 레코드 구조는 관리 콘솔에서 실제로 내보낸 결과의 머리글로 확인합니다.

## 증거로서 의미

**증명하는 것.** Vault 로 보존·검색한 대화는 그 Workspace 계정이 Gemini 에 입력한 프롬프트와 받은 응답을 보여 줍니다. 감사 로그는 그 계정이 Gemini 를 쓴 사실을 관리자 쪽 기록으로 뒷받침합니다. 문서가 밝힌 처리 조건도 보고서에 인용할 수 있는데, 허락 없이 도메인 밖에서 사람이 검토하거나 생성형 AI 모델 학습에 쓰지 않는다고 되어 있고, Gemini in Chrome 도 같은 조건을 적습니다.

**증명하지 못하는 것.** 보관 기간이 지났거나 사용자가 지운 대화는 서버에서 찾지 못할 수 있고, 이때 대화가 없다는 사실이 사용하지 않았다는 뜻은 아닙니다. Gemini Notebook 은 세션이 끝나면 보관하지 않으므로 서버 기록이 없어도 이상하지 않습니다. 계정 기록만으로는 그 시각에 누가 자판 앞에 있었는지 알 수 없고, 이 문제는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)에서 다룹니다.

보고서 문장은 "이 Workspace 계정에서 이 기간에 Gemini 에 보낸 프롬프트 몇 건이 Vault 에 보존되어 있다" 처럼 기록으로 확인되는 범위에서 씁니다.

## 시각 해석

Vault 내보내기나 감사 로그의 시각 필드와 시간대는 문서에 나오지 않습니다. 내보낸 결과를 받으면 시각 값에 시간대 표시가 있는지 먼저 확인하고, 관리 콘솔 화면에 보이는 시각이 보는 사람의 시간대로 바뀌어 표시되는지도 함께 확인합니다. 여러 출처를 시간순으로 합치는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **보관 설정 확인이 먼저.** Workspace 앱 속 Gemini 는 90일부터 무기한까지, Gemini 앱은 3·18·36개월 중 하나로 정해집니다. 사건 날짜와 조직의 보관 설정을 먼저 맞춰 보지 않으면 "기록이 없다" 를 잘못 해석합니다. 보관과 삭제의 일반론은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에서 다룹니다.
- **사용자 삭제.** 관리자가 막지 않으면 사용자가 Workspace 앱 속 Gemini 대화를 직접 지울 수 있습니다. 조직의 Vault 보존 규칙이 사용자 삭제보다 앞서는지는 그 조직의 설정으로 확인합니다.
- **계정 혼동.** 같은 사람이 개인 Google 계정과 Workspace 계정을 한 브라우저에서 함께 쓰면, 어느 계정의 Gemini 를 썼는지에 따라 보관 규칙과 요청할 곳이 달라집니다.
- **문서 주소 이동.** 옛 도움말 주소(support.google.com/a/answer/15706919)는 knowledge.workspace.google.com 으로 넘어갑니다. 보고서에 인용할 때는 넘어간 뒤의 주소와 갱신 날짜를 적습니다.

## 직접 분석해 보기

**헥스로 한 번.** 대화 원본이 서버에 있고 기기 쪽 저장 파일은 구조가 공개되지 않았으므로, 헥스로 따라갈 파일은 실제 기기에서 직접 찾아야 합니다. 기기 이미지만 있는 사건이라면 브라우저 방문 기록에서 Workspace 앱과 Gemini 를 쓴 시간대를 먼저 좁히고, 방법은 Windows 판의 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html) 페이지를 따릅니다.

**공개 도구로 한 번.** Vault 와 감사 로그는 관리 콘솔에서 내보내 받습니다. 내보낸 결과를 스프레드시트나 jq 같은 공개 도구로 열어, 계정과 기간으로 거른 뒤 Gemini 관련 항목만 남깁니다. 거를 열은 내보낸 파일의 머리글을 보고 정합니다.

## 교차 검증

- [Gemini](../chat-services/gemini/index.md) — 개인 계정 Gemini 와 구분하기
- [브라우저에 들어간 AI](browser-builtin-ai.md) — Chrome 안에서 쓴 Gemini
- [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) — 같은 시간대의 통신
- [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) — 조직 밖에서 자료를 받아야 할 때
- [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md) — 조사 질문으로 쓰는 흐름

## 실습

공개 시험 이미지(NIST CFReDS 등)를 쓸 때는 그 설명에 Workspace Gemini 기록이 들어 있는지 먼저 봅니다. 시험용 Workspace 가 있다면 아래 질문을 직접 풀어 봅니다.

1. Docs 옆 패널에서 Gemini 에게 질문한 뒤, Vault 에서 그 대화를 찾을 수 있는지 확인합니다.
2. 같은 계정으로 Gemini 앱에서 질문하고, 관리 콘솔의 보관 설정(기본 18개월)이 어디에 표시되는지 봅니다.
3. 관리자용 감사 로그에서 방금 한 사용이 어떤 이름의 이벤트로 남는지 확인하고, 그 필드 이름을 기록해 둡니다.
4. 사용자가 대화를 지운 뒤 Vault 검색 결과가 달라지는지 비교합니다.

## 참고 문헌

1. Generative AI in Google Workspace Privacy Hub — https://knowledge.workspace.google.com/admin/gemini/generative-ai-in-google-workspace-privacy-hub?hl=en
