---
title: "Gemini 웹 브라우저"
parent: "Gemini"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 290
---

# 웹 브라우저 (Web)

브라우저로 쓰는 Gemini 는 gemini.google.com 에서 돌아가고 대화는 계정의 Gemini 앱 활동 (Gemini Apps Activity) 에 저장되어서, 기기에는 방문 기록·쿠키·브라우저 저장소 같은 브라우저 쪽 흔적만 남을 수 있고 대화 원본은 서버에 있습니다.

> 확인 날짜: 2026-09-25. Google 도움말(개인정보 안내, 활동 관리)을 바탕으로 썼습니다. 방문 기록에 남는 대화 주소의 모양, 쿠키 이름, Local Storage·IndexedDB 키, 캐시에 대화 조각이 남는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다.

## 무엇이 남나 · 왜 생기나

웹 판은 설치 프로그램 없이 브라우저 탭에서 돌아가고, 활동 저장 (Keep Activity) 설정이 켜져 있으면 프롬프트와 대화 내용이 계정 쪽에 저장됩니다. 도움말은 Gemini Live 를 쓴 경우 녹취·음성·파일·이미지·YouTube 영상에 화면 공유와 영상 입력까지 남는다고 적었습니다. 보관 기간, 설정을 껐을 때의 72시간 보관, 사람 검토를 거친 사본 같은 서버 쪽 규칙은 [Gemini](index.md) 허브에 정리했고 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에서 다룹니다.

웹 판을 쓴 흔적을 찾을 때는 아래 주소가 기준이 됩니다. 모두 도움말에 적힌 주소이고, 방문 기록에서 이 주소가 보이면 사용자가 어느 화면을 열었는지 가늠할 수 있습니다.

| 주소 | 화면 | 조사에서 쓰는 곳 |
|---|---|---|
| `gemini.google.com` | Gemini 웹 앱 | 웹 판을 연 시각과 횟수 |
| `myactivity.google.com/product/gemini` | Gemini 앱 활동 목록 | 활동을 보거나 지우는 화면을 열었는지 |
| `https://gemini.google.com/sharing` | 공개 링크 목록 ("Your Public Links") | 대화를 공개 링크로 만든 뒤 관리했는지 |
| `https://gemini.google.com/gems/view` | Gems 관리 화면 ("Gems Manager") | 맞춤 Gem 을 만들거나 고쳤는지 |

활동 목록은 gemini.google.com 안의 Settings & help → Activity 에서도 열 수 있어서, `myactivity.google.com` 방문 기록이 없다고 활동 화면을 열지 않았다고 볼 수는 없습니다.

브라우저 쪽 흔적은 Gemini 만의 것이 아니고 어느 웹 서비스를 쓰든 브라우저가 똑같이 남기는 기록입니다.

| 흔적 | 조사에서 쓰는 곳 |
|---|---|
| 방문 기록 | 위 주소를 연 시각과 횟수 |
| 쿠키 | 그 브라우저 프로필에 Google 계정 로그인 흔적이 있었는지 |
| Local Storage·IndexedDB | 웹 앱이 브라우저에 남긴 데이터 |
| 캐시 | 받아 온 응답·그림 조각 |
| 다운로드 기록과 다운로드 폴더 | 생성한 이미지 등 내려받은 파일 |

이 가운데 대화 하나하나의 주소 모양, 쿠키 이름, 저장소 키 이름, 저장소와 캐시에 대화 사본이 남는지는 시험 계정으로 만든 검체에서 확인해야 합니다.

## 위치와 OS별 차이

브라우저 프로필 폴더의 위치와 저장 형식은 Gemini 가 아니라 브라우저와 OS 가 정합니다. 쓰인 브라우저를 먼저 가린 뒤 해당 판의 페이지를 따라갑니다.

| OS | 브라우저 | 구조 설명 |
|---|---|---|
| Windows | 크롬·엣지·웨일 등 크롬 계열 | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html) |
| macOS | 사파리 | [사파리](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/browsers/safari/index.html) |
| Android | 크롬 | [크롬 (Chrome for Android)](https://urock-ailab.github.io/forensics-handbook-android/02-artifacts/browsers/chrome/index.html) |
| iOS | 사파리, 크롬 | [사파리](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/safari/index.html), [크롬 (Chrome for iOS)](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/chrome.html) |

크롬 계열에서 Local Storage 와 IndexedDB 는 LevelDB 파일로 남아서 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html) 페이지의 읽는 법을 그대로 씁니다. 크롬 도구 모음에서 여는 Gemini 창은 웹 탭과 흔적이 달라서 [Chrome 통합](chrome.md)에서 따로 보고, 휴대폰 앱은 [Android 앱](android.md)과 [iOS 앱](ios.md)에서 봅니다.

## 증거로서 의미

**증명하는 것.** 방문 기록에 `gemini.google.com` 이 있으면 그 브라우저 프로필에서 그 주소를 연 기록이 있다고 쓸 수 있고, 공개 링크 목록이나 Gems 관리 주소가 있으면 그 화면을 열었다고 쓸 수 있습니다. 활동 화면 주소가 있으면 사용자가 활동 목록을 열어 본 기록이 있다고 쓸 수 있습니다.

**증명하지 못하는 것.** 방문 기록은 무엇을 입력했는지 알려 주지 않고, 대화 내용은 서버에 있어서 기기만으로는 확인하기 어렵습니다. 활동 화면을 연 기록이 있어도 그 자리에서 무엇을 지웠는지는 알 수 없고, 로그인 흔적이 있어도 그 시각에 누가 키보드 앞에 있었는지는 따로 따져야 합니다([그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)). 방문 기록이 없다고 쓰지 않았다고 볼 수도 없는데, 시크릿 창을 썼거나 기록을 지웠거나 다른 기기나 앱에서 썼을 수 있기 때문입니다.

## 시각 해석

방문 기록의 시각 형식과 기준(UTC 인지 현지 시각인지)은 브라우저마다 달라서 위 표의 브라우저 페이지를 따릅니다. 탭 하나를 열어 둔 채 여러 번 주고받을 수 있어서, 방문 기록의 시각은 페이지를 연 때에 가깝고 메시지를 보낸 때와 같다고 볼 수 없습니다. 메시지 단위의 시각은 서버 활동 기록에 있고, 이를 받아 보는 방법은 [계정 데이터 내보내기](export.md)에서 다룹니다. 브라우저 시각과 서버 시각을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)을 봅니다.

## 함정과 한계

도움말은 활동을 지우면 화면에서 바로 지우고 저장 시스템에서 영구 삭제 절차를 시작한다고 안내합니다. 그래서 활동 목록에 없는 대화라도 한때 있었다가 지웠을 수 있고, 활동 저장을 꺼 둔 상태의 대화나 임시 채팅은 처음부터 목록에 나오지 않습니다. 목록이 비어 있다는 사실만으로 Gemini 를 쓰지 않았다고 쓰지 않습니다.

`gemini.google.com` 방문은 Gemini 를 쓴 흔적이지만, Google 의 다른 서비스나 Workspace 안에서 Gemini 를 쓴 경우는 다른 흔적을 남깁니다([Google Workspace의 Gemini](../../office-integrations/workspace-gemini.md)). 브라우저 캐시나 저장소에서 대화 조각을 찾는 일반 방법은 [대화 내용 되살리기](../../../03-techniques/analysis/content-recovery.md)에 있지만, Gemini 웹 판에서 조각이 남는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다.

## 직접 분석해 보기

크롬 계열이라면 프로필 폴더의 `History` SQLite 파일을 사본으로 떠서 공개 도구인 DB Browser for SQLite 로 열고, 주소에 `gemini.google.com` 또는 `myactivity.google.com/product/gemini` 가 들어간 행을 찾습니다. 표와 칸 이름, 시각 값을 바꾸는 법은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html)와 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html) 페이지를 따릅니다. 파일을 헥스 편집기로 열어 주소 문자열 `gemini.google.com` 을 찾아보면 지운 행의 흔적이 빈 페이지에 남아 있는지도 가늠할 수 있습니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 계정 데이터 내보내기 | 메시지 단위 활동과 시각 | [계정 데이터 내보내기](export.md) |
| Chrome 통합 설정 | 브라우저 창 안에서 Gemini 를 쓴 흔적 | [Chrome 통합](chrome.md) |
| DNS·프록시 기록 | 같은 시간대에 서비스 도메인에 접속했는지 | [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) |
| 서비스 회사 자료 | 서버에 남은 대화 원본 | [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md) |

## 실습

시험용 Google 계정으로 검체를 만들어 아래 질문을 직접 풀어 봅니다.

1. 웹 판에서 대화를 두 번 나눈 뒤 크롬 `History` 파일을 열면, 대화마다 다른 주소가 남습니까, 아니면 `gemini.google.com` 한 줄만 남습니까?
2. 활동 화면에서 대화 하나를 지운 뒤, 방문 기록과 활동 목록에는 각각 무엇이 남습니까?
3. 시크릿 창에서 같은 일을 했을 때 프로필 폴더에 남는 것이 있습니까?

## 참고 문헌

1. Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961 (2026-09-25 열람)
2. Manage & delete your activity in Gemini Apps - Computer - Gemini Apps Help — https://support.google.com/gemini/answer/13278892 (2026-09-25 열람)
