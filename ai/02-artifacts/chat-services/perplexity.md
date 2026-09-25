---
title: "Perplexity"
parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 340
---

# Perplexity (Perplexity)

Perplexity 는 질문에 검색 결과를 붙여 답하는 AI 검색 서비스이고, 웹·모바일 앱·Chrome 확장·자체 브라우저 Comet 으로 쓸 수 있어서 어느 형태로 썼는지에 따라 흔적을 찾을 곳이 달라집니다.

웹·모바일 앱의 로컬 저장 구조는 공개된 분석 자료가 없어 검체에서 직접 봐야 합니다.

## 무엇을 기록하나 · 왜 생기나

운영사는 Perplexity AI, Inc. 이고, 검색 엔진은 2022-12-07 에 공개했습니다[1]. 사용자가 질문을 넣으면 서비스가 웹을 검색해 답과 출처를 함께 보여 주고, 질문과 답은 하나의 대화(스레드)로 이어집니다. Excel·Word·PDF 같은 문서를 올려 그 내용까지 함께 찾는 "Internal Knowledge Search" 기능도 있어서[1], 질문 글뿐만 아니라 사용자가 어떤 파일을 서비스에 올렸는지까지 쟁점이 될 수 있습니다. 질문·첨부·생성물을 어떻게 나눠 보는지는 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)에 있습니다.

대화 원본은 서버에 있고, 기기에는 앱이나 브라우저가 받아 둔 사본이 남을 수 있습니다. Comet 에서는 AABF 가 프로필의 IndexedDB 에서 서버 응답 캐시를 읽어 대화 목록, 질문, 답변을 꺼냅니다[2]. 웹과 모바일 앱에 같은 사본이 남는지는 검체에서 확인하므로, 이 쪽은 대화 본문이 기기에 있다는 전제를 두지 않고 접속 흔적과 캐시 조각을 함께 찾는 순서로 씁니다. 서버와 기기 중 어디에 무엇이 있는지 가르는 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

## 위치와 버전별 차이

위키백과에 나온 제공 형태는 웹(perplexity.ai), iOS 앱, Android 앱, Chrome 확장, Comet 브라우저입니다. Comet 은 Chromium 을 바탕으로 만든 브라우저이고, 2025-07 에 일부 사용자에게 먼저 나온 뒤 2025-10 에 누구나 무료로 내려받을 수 있게 됐습니다[1]. Android 용 Assistant 는 2025-01 에, AI 에이전트 "Perplexity Computer" 는 2026-02 에 나왔습니다[1]. 형태마다 흔적이 남는 곳이 달라서 아래처럼 나눠 봅니다.

| 쓰는 형태 | 알려진 로컬 위치 | 먼저 볼 곳 |
|---|---|---|
| Comet 브라우저 (Windows) | `%LOCALAPPDATA%\Perplexity\Comet\UserData` (AABF[2]) | 프로필 폴더 전체. 세부는 [AI 에이전트 브라우저](../agentic-services/ai-browsers.md) |
| 웹(perplexity.ai) | 공개된 분석 자료 없음 | 쓰던 브라우저의 방문 기록·캐시·쿠키·사이트 저장소 |
| Chrome 확장 | 공개된 분석 자료 없음 | Chrome 프로필 안의 확장 폴더와 방문 기록 |
| Windows·macOS 데스크톱 앱 | 위키백과 제공 형태 목록에 없음 | 설치 프로그램 목록과 앱 폴더에서 앱이 있는지부터 봄 |
| Android 앱 | 공개된 분석 자료 없음 | 앱 데이터 폴더 |
| iOS 앱 | 공개된 분석 자료 없음 | 백업·전체 추출본의 앱 컨테이너 |

Comet 에서 AABF 가 읽는 캐시 폴더 이름 `IndexedDB\https_www.perplexity.ai_0.indexeddb.leveldb` 와 Local Storage 출처 `https://www.perplexity.ai` 는 브라우저가 아니라 사이트 주소를 따라 붙은 이름입니다[2]. 그래서 다른 크롬 계열 브라우저로 웹을 썼다면 그 프로필에 같은 이름의 폴더와 출처가 있는지 먼저 보고, 있으면 안을 열어 Comet 과 같은 짜임인지 확인합니다.

브라우저로 쓴 경우의 일반 흔적은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html), [macOS 사파리](https://urock-ailab.github.io/forensics-handbook-mac/02-artifacts/browsers/safari/index.html), [Android 크롬](https://urock-ailab.github.io/forensics-handbook-android/02-artifacts/browsers/chrome/index.html), [iOS 사파리](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/safari/index.html) 페이지의 방식대로 읽습니다. 데스크톱 앱이 있고 Electron 이나 웹뷰로 만든 앱이라면 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)를 따르고, 어느 틀인지는 수집한 폴더 모양을 보고 판단합니다. 모바일 앱은 [Android 앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html)와 [iOS 데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html)를 먼저 읽고 수집 범위를 정합니다.

앱이 자주 바뀌어서 분석 결과에는 앱·브라우저 버전과 확인 날짜를 꼭 함께 적고, 같은 사건에서도 기기마다 버전이 다를 수 있다는 점을 표에 남깁니다.

## 구조

Comet 프로필의 Local Storage 키(`pplx-next-auth-session`, `comet-sidecar-threads-by-id`), IndexedDB 캐시의 키 모양과 칸 이름(`query_str`, `markdown_block.answer`, `author_id` 등), 세션 쿠키 위치는 [AI 에이전트 브라우저](../agentic-services/ai-browsers.md)의 Comet 절에 표로 있습니다[2]. 이 쪽에서 더 볼 점은 그 캐시에 에이전트 대화만 있지 않다는 것입니다. AABF 코드 주석은 대화마다 붙는 `source` 칸 값이 `entropy` 면 Comet 에이전트 대화, `default` 면 일반 Perplexity 검색, `youtube` 면 위젯에서 시작한 대화라고 적고, AABF 는 에이전트 대화만 결과에 남깁니다(`aabf/parsing/services/comet.py`)[2]. 일반 검색 기록을 찾는 조사라면 AABF 결과만 보지 말고 캐시를 직접 열어 `source` 가 `default` 인 항목까지 봅니다.

웹과 모바일 앱의 저장 구조는 공개된 분석 자료가 없어 검체로 확인해야 합니다. 브라우저로 쓴 경우 사이트 데이터는 브라우저가 정한 공통 저장소에 들어가고, 그 형식은 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html)와 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html) 페이지에서 다룹니다. 검체에서 Perplexity 전용으로 보이는 폴더나 파일을 찾았다면, 이름을 추측으로 풀지 말고 앱 버전과 함께 기록한 뒤 안의 내용을 직접 열어 확인합니다.

## 증거로서 의미

**증명하는 것.** 브라우저 방문 기록에 perplexity.ai 주소가 있으면 그 브라우저 프로필에서 그 시각에 해당 주소를 연 기록이 있다는 뜻이고, 캐시나 사이트 저장소에 대화 조각이 남아 있으면 그 조각을 한때 화면에 불러왔다는 뜻입니다. Comet 캐시에 `author_id`·`author_username` 이 있으면 그 대화를 어느 계정으로 했는지까지 좁힐 수 있습니다[2]. 네트워크 기록에 해당 도메인 접속이 있으면 그 기기나 계정이 그 시간대에 서비스와 통신한 기록이 됩니다. 보고서에는 "이 시각에 이 프로필에서 이 주소를 연 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

**증명하지 못하는 것.** 접속 기록만으로는 무엇을 물었는지, 어떤 파일을 올렸는지 알 수 없습니다. 캐시에서 빠진 대화도 있을 수 있어서, 기기에 흔적이 없다고 대화가 없었다고 말할 수도 없습니다. 계정에 로그인한 사람이 누구인지도 기록이 알려 주지 않아서 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 좁힙니다.

## 시각 해석

기기 쪽 시각은 브라우저나 앱이 남긴 기록의 시각이라서, 저장소마다 기준 시각(UTC 인지 현지 시각인지)과 단위가 다릅니다. Comet 에서는 캐시 항목의 `entry_created_datetime` 이 ISO-8601 문자열, Local Storage 대화 목록의 `updatedAt` 이 유닉스 시각 밀리초, `perplexity_last_event_timestamp` 가 유닉스 시각 초로 들어 있습니다(`aabf/analysis/timestamps.py`)[2]. ISO-8601 문자열은 끝에 시간대 표시가 붙었는지 검체에서 보고 읽습니다. 브라우저 기록의 시각 형식은 각 브라우저 페이지에 있고, 여러 출처의 시각을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다. 서버 쪽 대화 시각은 계정 데이터 내보내기나 수사기관 요청으로 받은 자료에서 확인하고, Perplexity 가 내보내기를 제공하는지와 그 형식은 사건 당시 계정 설정 화면과 도움말에서 확인합니다.

## 함정과 한계

스레드를 지우거나 계정을 없앤 뒤 서버가 얼마나 보관하는지, 익명 모드나 AI 학습 거부 설정이 있는지는 사건 당시의 개인정보 처리방침을 따로 확보해 확인합니다. 다른 서비스의 규칙으로 이 부분을 메우지 않습니다. 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

Comet 캐시 항목에는 `expiry_time` 이 붙어 있고, AABF 는 이 값이 약 30일이라 오래된 대화는 캐시에서 빠질 수 있다고 적습니다[2]. 수집이 늦을수록 기기에서 읽을 수 있는 대화가 줄어들 수 있다는 뜻이라, 캐시에 없는 기간은 서버 쪽 자료로 채웁니다.

같은 서비스를 웹·확장·Comet·모바일 앱으로 번갈아 쓰면 흔적이 여러 기기와 프로필에 흩어집니다. 한 곳만 보고 "사용 흔적 없음" 이라고 쓰기 쉬워서, 수집할 때 쓰는 형태를 먼저 모두 적어 둡니다. Comet 이나 AI 에이전트 Perplexity Computer 가 사용자 대신 웹 페이지를 열었다면 사람이 한 동작과 AI 가 한 동작이 같은 기록에 섞일 수 있습니다. Comet 캐시에서는 `source` 칸으로 에이전트 대화를 가를 수 있고, Perplexity Computer 가 무엇을 어디에 남기는지는 공개된 분석 자료가 없어 검체로 확인하면서 [브라우저를 조작하는 AI](../agentic-services/browser-agents.md)의 일반 기준으로 나눠 봅니다.

Comet 의 세션 쿠키 `__Secure-next-auth.session-token` 과 Local Storage 의 `pplx-next-auth-session` 에는 계정 인증 정보와 이메일이 들어 있어서[2] 보고서에서는 가립니다. 서버에 있는 대화 원본은 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) 같은 법적 절차로 받습니다.

## 직접 분석해 보기

**헥스로 한 번.** 캐시나 할당되지 않은 영역에서 서비스 흔적을 찾을 때는 도메인 문자열의 바이트를 찾습니다. 아래는 문자 인코딩 명세대로 만든 예시이고, 검체에서 뜬 바이트가 아닙니다. 저장소에 따라 UTF-8 로 들어가기도 하고 UTF-16LE 로 들어가기도 해서 두 가지를 모두 찾습니다.

```
만든 예시(인코딩 명세로 만든 바이트)
"perplexity.ai"  UTF-8     70 65 72 70 6C 65 78 69 74 79 2E 61 69
"perplexity.ai"  UTF-16LE  70 00 65 00 72 00 70 00 6C 00 65 00 78 00 69 00 74 00 79 00 2E 00 61 00 69 00
```

**공개 도구로 한 번.** 수집한 사본 폴더에서 ripgrep 과 GNU strings 로 도메인이 들어간 파일을 먼저 추립니다. 경로는 만든 예시이고, 원본이 아니라 사본에서만 돌립니다.

```sh
# 만든 예시 경로
CASE=/cases/case-0001/copy/profile-alice
rg -a -l "perplexity.ai" "$CASE"
find "$CASE" -type f -exec sh -c 'strings -el "$1" | grep -q "perplexity.ai" && echo "$1"' _ {} \;
```

찾은 파일은 형식에 맞는 도구로 다시 열어 문맥을 확인하고, 문자열이 있다는 사실만으로 대화 내용이라고 판단하지 않습니다. Comet 프로필이 있으면 AABF 로 계정·대화·답변을 한 번에 뽑아 볼 수 있고, 도구 결과는 검체의 폴더와 맞춰 봅니다. 지운 캐시에서 대화 조각을 되살리는 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)에 있습니다.

## 교차 검증

기기 흔적은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)의 DNS·프록시 기록과 시각을 맞춰 보고, 회사 PC 라면 [보안 제품이 남기는 AI 사용 기록](../network-enterprise/dlp-casb.md)에서 업로드 시도가 잡혔는지 봅니다. 서버 쪽 원본은 [계정 데이터 내보내기로 수집](../../03-techniques/acquisition/export-collection.md)이나 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 확보하고, 기기에서 흔적을 모으는 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)를 따릅니다. 문서를 올렸는지가 쟁점이면 [기밀 자료를 AI에 넣었나](../../04-scenarios/data-leak/confidential-input.md)의 흐름으로 이어 갑니다.

## 실습

시험용 가상 머신과 시험 계정으로 풀어 봅니다.

1. 웹 브라우저로 스레드를 두 개 만들고 하나를 지운 뒤, 브라우저 프로필 사본에서 지운 스레드의 질문 글이 남아 있는지 찾아봅니다.
2. Comet 에서 일반 검색과 에이전트 작업을 한 번씩 한 뒤, IndexedDB 캐시에서 두 대화의 `source` 값이 어떻게 다른지 봅니다.
3. 가짜 내용의 PDF 를 올려 질문하고, 기기에서 올린 흔적(파일 선택 기록, 캐시, 네트워크 기록)을 어디까지 찾을 수 있는지 적어 봅니다.
4. 같은 계정으로 모바일 앱과 웹을 번갈아 쓴 뒤, 기기별로 남은 흔적과 시각을 한 타임라인에 올려 봅니다.
5. 설치한 앱·브라우저의 버전을 적고, 한 달 뒤 같은 실습을 되풀이해 달라진 점을 비교합니다.

## 참고 문헌

1. Perplexity AI — 위키백과(영문, 2차 자료, 2026-09-25 열람) — https://en.wikipedia.org/wiki/Perplexity_AI
2. seturi, AI-Agent-Browser-Forensics (AABF) v1.1.260618, MIT — https://github.com/seturi/AI-Agent-Browser-Forensics. 읽은 파일: `aabf/signatures.py`, `aabf/parsing/services/comet.py`, `aabf/analysis/timestamps.py` (2026-09-25 열람).
