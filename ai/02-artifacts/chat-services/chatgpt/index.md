---
title: "ChatGPT"
parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 70
has_children: true
has_toc: false
---

# ChatGPT (ChatGPT)

ChatGPT 는 웹·Windows·macOS·Android·iOS 에서 쓰는 대화형 AI 서비스이고, 대화 원본은 계정에 묶여 서버에 있지만 모바일 앱은 그 사본을 기기에 평문으로 남기므로, 기기 흔적과 계정 데이터 내보내기를 함께 봐야 대화 내용과 사용 기기를 모두 설명할 수 있습니다.

## 왜 중요한가

ChatGPT 는 여러 기기에서 같은 계정으로 쓰는 서비스라서, 한 기기에 흔적이 없어도 다른 기기나 웹에서 쓴 기록이 계정에 남아 있을 수 있습니다. 서버·기기·동기화에 데이터가 나뉘어 있는 일반 원리는 [AI 서비스의 데이터는 어디에 있나](../../../01-foundations/storage-model/where-data-lives.md)에서 다룹니다.

기기 쪽에도 대화 사본이 남습니다. Tyagi·Gong·Karabiyik(2025)은 ChatGPT 가 Android 와 iOS 에서 대화를 브라우저 데이터와 함께 평문으로 저장한다고 초록에 적었습니다 [13]. Android 앱은 SQLite 데이터베이스에, iOS 앱은 대화마다 JSON 파일 하나에 대화를 두고, 공개 분석기는 복호화 단계 없이 이 파일을 바로 읽습니다 [7][8][9]. ChatGPT 모바일 앱을 처음 포렌식으로 분석한 연구는 Dragonas·Lambrinoudakis·Nakoutis(2024)이고 [12], 이 연구를 인용한 논문들은 Android·iOS·클라우드 저장소에서 흔적을 찾았으며 [14] 캐시된 프롬프트, 접근 토큰, 네트워크 흔적이 나왔다고 요약했습니다 [15]. iLEAPP·RLEAPP 의 ChatGPT 분석기는 설명에 "연구 과제를 바탕으로 했다" 고 적었고, 작성자가 이 논문의 제1저자입니다 [9][10].

기기에 남는 모양은 판마다 다르고 자주 바뀝니다. macOS 앱은 2024-07 보도 당시 대화를 평문으로 저장했다가 그 뒤 업데이트로 암호화했습니다 [1]. 모바일 분석기가 시험한 판도 지금 스토어 판보다 오래돼서(아래 표) 형식이 다를 수 있으므로, 앱 버전과 확인 날짜를 먼저 적고 검체에서 경로와 칸을 다시 확인합니다. 지운 대화와 임시 채팅을 서버에 얼마나 두는지는 조사 시점의 공식 도움말에서 확인하고, 보관 설정의 일반 원리는 [대화 기록 보관 설정과 삭제](../../../01-foundations/storage-model/retention-deletion.md)에서 봅니다.

## 한눈에 보기

개발사 표기는 곳마다 달라서 App Store 에는 "OpenAI OpCo, LLC", Google Play 데이터 안전 페이지에는 "OpenAI" 로 적혀 있습니다 [2][3]. 아래 "공개 도구가 시험한 판" 은 분석기 코드에 적힌 값이고, 스토어의 현재 판보다 오래됐습니다.

| 판 | 위치·식별자 | 공개 도구가 시험한 판 | 알려 주는 것 |
|---|---|---|---|
| 웹 브라우저 | 브라우저 저장소 | 해당 없음 | 방문·다운로드 기록, 사용자가 사용자 스크립트로 따로 뽑은 대화 파일 [6] |
| Windows 앱 | Microsoft Store 제품 ID `9NT1R1C2HH7J`(2026-09-25 제목 "ChatGPT Classic") [4] | 설치된 판은 검체에서 확인 | 설치 흔적 |
| macOS 앱 | `~/Library/Application Support/com.openai.chat`(2024-07 보도 당시 판) [1] | 고친 판의 버전 번호는 보도에 없음 | 보도 당시 판은 평문 대화, 뒤의 판은 암호화한 대화 |
| Android 앱 | 패키지 `com.openai.chatgpt`. `databases/*_conversations.db`(대화·메시지), `files/datastore/*.preferences_pb`(계정·설정), `shared_prefs/analytics-android-oai.xml`(분석 도구 식별자), `cache/files/`(이미지) [7][8] | ALEAPP: 설명에 1.2024.177 까지 시험했다고 적음, 시험 이미지는 Android 15 · vc 2525902 하나 [7][8] | 대화 제목·본문·시각, 계정·요금제·맞춤 지시·채팅 기록 끔 설정, 분석 도구 식별자, 캐시 이미지 |
| iOS 앱 | App Store 항목 `id6448311069`, 2026-09-25 최신 1.2026.258 [2]. 앱 컨테이너의 `Library/Application Support/conversations-*/*.json`(대화), `drafts-*/*.json`(초안), `Library/Preferences/com.openai.chat.StatsigService.plist`·`com.segment.storage.oai.plist`(계정), `tmp/` 아래 `png` 이미지와 `m4a` 음성 입력 [9] | iLEAPP: 설명에 1.2024.178 까지 다룬다고 적음, 대화 시험 이미지는 1.2024.219·1.2024.233, 1.2025.261 시험 이미지는 계정 plist·미디어 분석기에만 적힘 [9] | 대화 본문·시각, 임시 채팅 여부, 맞춤 지시, 작성 중이던 초안, 계정·요금제, 올린 이미지와 음성 입력(다른 앱의 `tmp` 파일이 섞일 수 있음) |
| 계정 데이터 내보내기 | 계정 설정의 내보내기로 받는 ZIP. `conversations.json`, `shared_conversations.json`, `message_feedback.json`, `user.json` [5][10][11] | RLEAPP: 대화·공유·평가 분석기 마지막 검증 2024-07-09 [10], `user.json` 분석기 2026-07-09 갱신 [11] | 메시지의 작성자 역할·작성 시각·본문, 공유 링크와 대화의 연결, 답변 평가, 계정의 이메일·전화번호 |

시각 형식도 파일마다 다릅니다. 내보내기의 `conversations.json` 은 Unix 초이고 `message_feedback.json` 은 ISO 8601 문자열입니다 [10]. Android 대화 데이터베이스의 대화·메시지 시각은 ISO 8601 문자열입니다 [7]. iOS 대화 JSON 은 대화 시각을 2001-01-01 부터 센 초로, 메시지 시각을 Unix 초로 적습니다 [9]. 한 타임라인에 합치기 전에 각 하위 페이지의 시각 해석을 따릅니다.

## 읽는 순서

1. [웹 브라우저](web.md) — 브라우저로 쓴 흔적과 사용자 스크립트로 뽑은 대화 파일을 봅니다.
2. [Windows 앱](windows.md) — Microsoft Store 항목과 설치 흔적을 봅니다.
3. [macOS 앱](macos.md) — 2024-07 평문 저장 보도와 그 뒤 암호화한 판을 가르는 방법을 봅니다.
4. [Android 앱](android.md) — 대화 데이터베이스의 옛 메시지 표와 새 조각 표, 계정·설정 파일, 분석 도구 식별자를 읽습니다.
5. [iOS 앱](ios.md) — 대화 JSON·초안·계정 plist 를 읽고, 다른 앱의 `tmp` 미디어가 섞이는 함정을 봅니다.
6. [계정 데이터 내보내기](export.md) — 내보내기 ZIP 의 네 파일과 `conversations.json` 의 메시지 칸을 읽습니다.

## 함께 볼 페이지

- [ChatGPT 에이전트 모드](../../agentic-services/chatgpt-agent.md) — 에이전트 기능으로 실행한 작업의 흔적
- [음성 대화 기능](../../generative-media/voice-mode.md) — iOS 음성 입력 파일과 내보내기의 음성 대화 표시
- [ChatGPT 기업용 감사 기록](../../network-enterprise/chatgpt-enterprise.md) — 조직 계정의 기록을 관리자 쪽에서 가져가는 경로
- [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) — 접속 시각과 기기를 네트워크 쪽에서 확인
- [계정 데이터 내보내기 형식](../../../01-foundations/storage-model/data-export-formats.md) — 서비스마다 다른 내보내기 형식 비교
- [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md) — 기기에 남은 토큰을 보고서에서 다루는 법
- [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md) — 계정 주인의 협조 없이 서버 쪽 기록을 확보하는 절차
- [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md) — 계정 기록과 실제 입력한 사람을 잇는 방법
- 저장 형식 공통 원리 — [Android 앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html), [Android SQLite](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html), [Android 설정 XML과 SharedPreferences](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/shared-preferences.html), [iOS 속성 목록 파일](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/plist.html)

## 참고 문헌

1. 9to5Mac, "ChatGPT for Mac stored conversations in plain text"(2024-07-03, 뒤에 업데이트 덧붙음) — https://9to5mac.com/2024/07/03/chatgpt-macos-conversations-plain-text/
2. App Store, ChatGPT (OpenAI OpCo, LLC) — https://apps.apple.com/us/app/chatgpt/id6448311069 (2026-09-25 열람)
3. Google Play, ChatGPT 데이터 안전 — https://play.google.com/store/apps/datasafety?id=com.openai.chatgpt (2026-09-25 열람)
4. Microsoft Store, ChatGPT Classic (9NT1R1C2HH7J) — https://apps.microsoft.com/detail/9nt1r1c2hh7j (2026-09-25 열람)
5. GitHub, mohamed-chs/convoviz README — https://github.com/mohamed-chs/convoviz (2026-09-25 열람)
6. GitHub, pionxzh/chatgpt-exporter README — https://github.com/pionxzh/chatgpt-exporter (2026-09-25 열람)
7. ALEAPP, `scripts/artifacts/chatgpt.py`(작성 Evangelos Dragonas, 2026-08-01 갱신) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/chatgpt.py
8. ALEAPP, `scripts/artifacts/chatgpt2.py`(작성 Alexis Brignoni, 2026-07-10 갱신) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/chatgpt2.py
9. iLEAPP, `scripts/artifacts/chatgpt.py`(작성 Evangelos Dragonas, 2026-08-21 갱신) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/chatgpt.py
10. RLEAPP, `scripts/artifacts/chatgpt.py`(작성 Evangelos Dragonas, 2024-07-09) — https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/chatgpt.py
11. RLEAPP, `scripts/artifacts/chatGPTaccountInfo.py`(작성 @upintheairsheep2, 2023-08-02, 2026-07-09 갱신) — https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/chatGPTaccountInfo.py
12. Evangelos Dragonas, Costas Lambrinoudakis, Panagiotis Nakoutis, "Forensic analysis of OpenAI's ChatGPT mobile application", Forensic Science International: Digital Investigation, 50 (2024), 301801. https://doi.org/10.1016/j.fsidi.2024.301801 (서지 정보와 [14][15]의 요약으로 인용)
13. Sonali Tyagi, Yufeng Gong, Umit Karabiyik, "Forensic analysis and privacy implications of LLM mobile apps: A case study of ChatGPT, Copilot, and Gemini", Forensic Science International: Digital Investigation, 54 (2025), 301974. https://doi.org/10.1016/j.fsidi.2025.301974 (초록)
14. Sungjo Jeong, Sangjin Lee, Jungheum Park, "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987. https://doi.org/10.1016/j.fsidi.2025.301987
15. Kendall J. Comeaux, Trevor T. Spinosa, Ali Ghosn, Ibrahim Baggili, "Ex Machina: A forensic evaluation of AI companion applications and their evidentiary value", Forensic Science International: Digital Investigation, 56 (2026), 302050. https://doi.org/10.1016/j.fsidi.2026.302050
