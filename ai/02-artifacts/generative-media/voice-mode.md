---
title: "음성 대화 기능"
parent: "아티팩트 · 생성·음성·회의록"
nav_order: 450
---

# 음성 대화 기능 (Voice Mode)

AI 서비스의 음성 대화는 말소리를 서버로 보내 처리하고, 흔적은 서버의 대화·활동 기록, 계정 내보내기의 음성 표시 칸, 휴대폰 앱 폴더의 녹음 파일로 나뉘어 남으며, 어디에 무엇이 남는지는 서비스마다 다릅니다.

분석 도구가 다루는 앱 판이 오래되어 지금 판과 형식이 다를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

음성 대화는 사용자가 말한 소리를 글이나 모델 입력으로 바꾸고 답을 소리로 돌려주는 기능이라, 대화 한 번에 녹음, 받아쓴 글, 모델의 답이 함께 생깁니다. 어느 것을 얼마나 남기는지는 서비스와 계정 설정이 정합니다.

Gemini 앱은 활동 기록 저장(Keep Activity)이 켜져 있으면 오디오 녹음, Gemini Live 대화 기록(transcripts), Gemini Live 에서 공유한 영상·화면을 활동 기록에 저장합니다[1]. 오디오와 Gemini Live 의 영상·화면 공유는 기본값으로 Google 서비스 개선에 쓰지 않고, 사용자가 설정에서 켤 수 있습니다[1]. 사람이 검토하는 대화는 서비스 제공업체로 보내기 전에 계정과 떼어 내고, 사용자가 활동 기록을 지워도 최대 3년 보관합니다[1].

회사 계정으로 쓰는 Microsoft Copilot 은 2025년 11월부터 음성 대화를 새로 시작할 수 있고, 음성 대화의 글 기록(text transcripts)을 일반 Copilot 대화처럼 저장해 보존·eDiscovery·감사 정책을 적용하며, 사용자와 Copilot 의 음성은 저장하지 않습니다[5]. 이 설명은 회사 계정에 대한 것이라, 개인 계정으로 쓰는 Copilot 에 그대로 적용하지 않습니다.

ChatGPT 는 음성 오디오를 서버에 얼마나 보관하는지 밝힌 공식 문서가 없어서, 기록 쪽 흔적으로 봅니다. 계정 내보내기의 메시지에는 `metadata.voice_mode_message` 칸이 있고[2], iOS 앱은 대화 파일의 같은 칸과 함께 앱 폴더의 `tmp/` 아래에 `m4a` 녹음 파일을 둘 수 있습니다[3]. Claude 앱 음성 모드는 공개된 분석 자료가 없어 검체와 계정 내보내기로 확인해야 합니다.

## 위치와 버전별 차이

| 서비스 | 원본이 있는 곳 | 보관 | 기기·내보내기에 남는 것 | 근거 |
|---|---|---|---|---|
| Gemini 앱 | 서버의 활동 기록 | 활동 기록 저장이 켜져 있으면 기본 18개월 뒤 자동 삭제, 3개월·36개월·자동 삭제 안 함으로 바꿀 수 있음. 꺼져 있거나 임시 채팅이면 계정에 72시간 보관 | 기기에 녹음 파일이 남는지는 공개된 분석 자료가 없어 검체로 확인 | Privacy Hub[1] |
| ChatGPT | 서버의 대화 기록 | 공식 문서 없음. 계정 내보내기로 확인 | 내보내기 `conversations.json` 의 `metadata.voice_mode_message`[2], iOS 대화 파일의 `metadata.voice_mode_message`와 `tmp/recordings/*.m4a`·`tmp/*/*.m4a`[3], Android 예전 DB 형식의 `is_voice_message`[4] | RLEAPP·iLEAPP·ALEAPP 코드 |
| Microsoft Copilot(회사 계정) | Microsoft 365 쪽 대화 기록 | 글 기록은 조직의 보존 정책을 따르고, 음성은 저장하지 않음 | 글 기록은 보존·eDiscovery·감사 대상 | Microsoft Learn[5] |
| Meta AI(Ray-Ban Meta 안경) | Meta 계정 클라우드 | "Delete Voice Activity" 로 클라우드의 대화 기록이 지워짐 | Android 앱 `interaction_log.db` 에서 음성 질문이 `<redacted>` 로 바뀌어 있음 | 논문[6] |
| Claude 앱 | 공개된 분석 자료가 없음 | 검체로 확인 | 검체로 확인 | 없음 |

ChatGPT 도구의 시험 범위는 다음과 같습니다. RLEAPP 의 내보내기 파서는 2024-07-09 에 마지막으로 검증했습니다[2]. iLEAPP 의 대화 파서는 앱 1.2024.178 까지를 다루고, 시험 이미지는 iOS 17 의 ChatGPT 1.2024.219·1.2024.233 입니다[3]. ALEAPP 의 대화 파서는 1.2024.177 까지 시험했습니다[4]. 2026년 판 앱은 이 범위를 넘으므로 칸 이름과 경로가 그대로인지 검체에서 다시 봅니다.

기기 쪽에서 볼 곳은 운영체제마다 다릅니다. 앱이 마이크를 쓰려면 권한을 받아야 해서, macOS 에서는 [개인 정보 보호 권한](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/credentials/tcc/index.html)에서 어떤 앱이 마이크 권한을 받았는지부터 봅니다. Android 와 iOS 에서는 앱 데이터 폴더에서 캐시나 임시 음성 파일을 찾고, 폴더 구조는 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/app-data-layout.html)와 [데이터 보호](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/data-protection/index.html)를 따릅니다. Windows·macOS 데스크톱 앱이 웹뷰로 만든 앱이면 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)의 캐시·저장소 원리대로 찾습니다.

## 구조

### 서버의 활동 기록과 계정 내보내기

Gemini 의 활동 기록에는 대화와 함께 오디오 녹음, Gemini Live 대화 기록, 영상·화면 공유가 한 계정 아래 쌓이고, Google Takeout 으로 내보낼 수 있습니다[1]. 내보낸 묶음에서 음성 파일이 어느 폴더에 어떤 형식으로 들어 있는지는 공개된 분석 자료가 없어서, 아래 "직접 분석해 보기" 의 시작 바이트 표로 가립니다. 계정 내보내기 형식의 일반 원리는 [계정 데이터 내보내기 형식](../../01-foundations/storage-model/data-export-formats.md)에, 수집 절차는 [계정 데이터 내보내기로 수집](../../03-techniques/acquisition/export-collection.md)에 있습니다.

ChatGPT 계정 내보내기의 `conversations.json` 에서는 메시지마다 `metadata` 아래 `voice_mode_message` 칸을 봅니다. RLEAPP 는 이 칸을 "Voice Chat" 열로 따로 보여 줍니다[2]. 내보내기의 다른 칸은 [ChatGPT 계정 내보내기](../chat-services/chatgpt/export.md)에 있습니다. 내보내기 묶음에 음성 파일이 따로 들어 있는지는 공개된 분석 자료가 없어서, 받은 묶음에서 아래 시작 바이트 표로 직접 찾습니다.

### 휴대폰 앱에 남는 것

iOS 의 ChatGPT 앱은 대화 하나를 `Library/Application Support/conversations-*/` 아래 JSON 파일 하나로 두고, 메시지의 `metadata.voice_mode_message` 를 iLEAPP 가 "Voice Mode Message" 열로 보여 줍니다[3]. 같은 도구의 "ChatGPT - Voice Prompts" 항목은 앱 컨테이너의 `tmp/recordings/*.m4a` 와 `tmp/*/*.m4a` 를 모읍니다[3]. 이 항목에는 주의할 점이 있습니다. 컨테이너를 ChatGPT 표식 파일(`conversations-*` 폴더나 `com.openai.chat` plist)로 가리지 못하면 다른 앱의 `tmp` 녹음까지 섞이고, 도구의 시험 데이터에서 ChatGPT 이미지 세 개는 0행이었고 다른 메신저 앱의 `m4a` 가 2행 나왔습니다[3]. 그래서 경로에 맞는 `m4a` 가 나와도 그 컨테이너가 ChatGPT 것인지 먼저 확인합니다. 파일 구조는 [ChatGPT iOS 앱](../chat-services/chatgpt/ios.md)에 있습니다.

Android 의 ChatGPT 앱은 예전 DB 형식(`DBMessage.messageNode`)에서 `$.content.is_voice_message` 칸을 두고, ALEAPP 는 이를 "Voice Message" 열(참이면 Yes)로 보여 줍니다[4]. 사용자 설정 파일 `*_user_settings.preferences_pb` 에는 `has_seen_voice_intro`, `has_seen_voice_selection` 값이 있어서, 음성 기능 안내 화면을 본 적이 있는지 알 수 있습니다[4]. 새 DB 형식과 칸은 [ChatGPT Android 앱](../chat-services/chatgpt/android.md)에 있습니다.

Ray-Ban Meta 안경으로 Meta AI 에 한 음성 질문은 짝지은 Android 휴대폰의 Meta AI 앱(`com.facebook.stella`, 논문 시험 판 258.0.0.15.167, Android 14)에 남습니다[6]. `databases/interaction_log.db` 의 `entries` 에는 대화 상태와 AI 응답이 있지만 사용자 음성 질문은 `<redacted>` 로 가려져 있고, `files/assistantLogs/*.json` 에는 음성 명령 메타데이터와 상호작용 ID 가 있습니다[6]. 가려진 질문의 평문은 GraphQL 캐시와 클라우드 내보내기에서 찾고, 자세한 경로는 [Meta AI 앱과 AI 안경](../chat-services/meta-ai-glasses.md)에 있습니다.

### 한 대화에 생기는 기록

음성 대화 한 번이 남길 수 있는 기록을 나누면 다음과 같고, 어느 칸이 실제로 남는지는 서비스와 설정마다 다릅니다.

| 기록 | 뜻 | 근거가 있는 곳 |
|---|---|---|
| 녹음 | 사용자가 말한 소리 | Gemini 활동 기록(저장 켬)[1], ChatGPT iOS `tmp` 의 `m4a`[3]. 회사 계정 Copilot 은 저장하지 않음[5] |
| 받아쓴 글 | 소리를 글로 바꾼 것 | Gemini Live 대화 기록[1], 회사 계정 Copilot 글 기록[5] |
| 음성 표시 | 메시지가 음성으로 오갔다는 표시 | ChatGPT `voice_mode_message`[2][3], `is_voice_message`[4] |
| 공유한 영상·화면 | 대화 중 카메라나 화면을 보여 준 것 | Gemini 활동 기록(저장 켬)[1] |
| 모델의 답 | 글 또는 합성한 소리 | 합성 음성을 따로 저장하는지는 공개된 자료가 없어 검체로 확인 |

## 증거로서 의미

**증명하는 것.** 활동 기록에 녹음이나 Gemini Live 대화 기록이 있으면 그 계정에서 그 시간대에 음성 대화를 했고, 서비스가 그 내용을 이렇게 받아썼다는 뜻입니다. ChatGPT 메시지에 음성 표시 칸이 참으로 남아 있으면 그 메시지가 음성 모드로 오갔다는 기록이 됩니다. 보고서에는 "이 계정의 활동 기록에 이 시각의 Gemini Live 대화 기록이 있고, 그 내용은 다음과 같다" 처럼 기록이 말하는 만큼만 씁니다.

**증명하지 못하는 것.** 녹음이 계정에 남았다고 해서 말한 사람이 계정 주인이라는 뜻은 아니고, 기기 가까이에 있던 다른 사람의 목소리일 수도 있습니다([그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)). 받아쓴 글은 서비스가 소리를 글로 바꾼 결과라서 잘못 받아쓴 말이 섞일 수 있고, 중요한 문장은 녹음이 남아 있으면 녹음과 맞춰 봅니다. 앱 폴더의 `m4a` 는 경로만으로 어느 앱이 만들었는지 정해지지 않습니다[3]. 기록이 없다는 사실도 음성 대화를 하지 않았다는 증거가 되지 않는데, 활동 기록 저장을 껐거나 임시 채팅을 썼거나 자동 삭제 기간이 지났을 수 있고, 회사 계정 Copilot 은 처음부터 음성을 저장하지 않습니다[1][5].

## 시각 해석

Gemini 활동 기록의 시각을 화면과 내보내기 파일에서 어느 시간대로 보여 주는지는 공식 문서에 없어서, 검체에서 표기를 먼저 봅니다. 보관 규칙도 시각 해석에 영향을 줍니다. 기본 설정이면 18개월보다 오래된 활동은 이미 지워졌을 수 있고, 활동 기록 저장이 꺼져 있었다면 72시간이 지나면 계정에서 찾을 수 없습니다[1]. 이런 기록이 필요한 사건은 보존 요청을 서둘러야 합니다([서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)).

ChatGPT 내보내기의 메시지 `create_time` 은 유닉스 초이고, RLEAPP 는 UTC 로 바꿔 보여 줍니다[2]. iOS 대화 파일의 메시지 `create_time` 도 유닉스 초입니다[3]. `tmp` 의 `m4a` 는 iLEAPP 가 시각 열 없이 파일 이름과 경로만 보여 주므로[3], 파일 시스템 시각을 대화 파일의 메시지 시각과 맞춰 봅니다.

기기 쪽 흔적(권한 기록, 네트워크 기록)의 시각은 대화 시각을 직접 보여 주지 않지만, 그 시간대에 앱이 마이크를 쓰거나 서비스와 통신했는지를 알려 줍니다. 여러 출처를 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

"서비스 개선에 쓰지 않음" 과 "저장하지 않음" 은 다른 설정입니다. Gemini 에서 오디오를 개선에 쓰지 않는 것이 기본값이어도 활동 기록 저장이 켜져 있으면 녹음은 활동 기록에 남습니다[1]. 반대로 활동 기록 저장을 꺼도 72시간은 계정에 남아서, 설정만 보고 기록이 전혀 없다고 판단하면 안 됩니다. 보관 설정과 삭제의 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

사람이 검토한 Gemini 대화는 활동 기록을 지워도 최대 3년 남지만 계정과 떼어 낸 기록입니다[1]. 이 기록이 필요하면 계정 내보내기가 아니라 법적 절차로 서비스 회사에 요청합니다.

Meta AI 앱은 음성 질문을 기기 DB 에서 가리므로, 기기 DB 만 보고 "질문 내용이 없다" 고 쓰면 안 됩니다[6]. "Delete Voice Activity" 를 쓰면 클라우드의 대화 기록은 지워지지만 AI 로 만든 알림은 남습니다[6].

ChatGPT 의 음성 칸과 경로는 2024년 판 앱으로 시험한 도구 코드에서 왔습니다[2][3][4]. Claude 앱 음성 모드는 공개된 분석 자료가 없으므로, 음성 원본이 남는지는 검체로 확인합니다.

## 직접 분석해 보기

**헥스로 한 번.** 내보내기 묶음이나 앱 폴더에서 확장자가 없거나 낯선 파일을 찾으면 첫 바이트로 음성 파일인지 가립니다. 아래 표는 각 형식의 명세에 적힌 시작 바이트로 만든 예시이고, 특정 검체에서 뜬 값이 아닙니다.

| 형식 | 시작 바이트 | 글자로 보면 |
|---|---|---|
| WAV | 오프셋 0 에 `52 49 46 46`, 오프셋 8 에 `57 41 56 45` | `RIFF` … `WAVE` |
| Ogg(Opus·Vorbis) | 오프셋 0 에 `4F 67 67 53` | `OggS` |
| WebM·Matroska | 오프셋 0 에 `1A 45 DF A3` | (글자 아님) |
| MP4·M4A | 오프셋 4 에 `66 74 79 70` | `ftyp` |
| MP3(ID3 태그 있음) | 오프셋 0 에 `49 44 33` | `ID3` |
| FLAC | 오프셋 0 에 `66 4C 61 43` | `fLaC` |

```
만든 예시(Ogg 명세로 만든 첫 줄)
00000000  4F 67 67 53 00 02 00 00 00 00 00 00 00 00 ...     OggS..........
```

**공개 도구로 한 번.** ChatGPT 는 계정 내보내기를 RLEAPP 로, iOS 전체 파일 시스템 추출을 iLEAPP 로, Android 추출을 ALEAPP 로 돌려 음성 표시 열과 "ChatGPT - Voice Prompts" 결과를 봅니다[2][3][4]. 형식을 가린 음성 파일은 사본에서 FFmpeg 의 ffprobe 로 길이, 코덱, 컨테이너 태그를 봅니다. 파일 이름은 만든 예시입니다.

```sh
ffprobe -hide_banner -show_format -show_streams made-example-audio.m4a
```

결과의 길이는 녹음이 얼마나 이어졌는지를 보여 줍니다. 컨테이너 태그에 시각이 있으면 대화 기록의 시각과 맞춰 보되, 파일을 다시 인코딩하면 태그 시각이 바뀌거나 사라질 수 있습니다.

## 교차 검증

서비스별 대화 기록 구조는 [Gemini](../chat-services/gemini/index.md), [ChatGPT](../chat-services/chatgpt/index.md), [Claude](../chat-services/claude/index.md), [Windows 용 Copilot](../chat-services/copilot/windows.md), [Microsoft 365 Copilot](../office-integrations/m365-copilot.md), [Meta AI 앱과 AI 안경](../chat-services/meta-ai-glasses.md) 페이지와 함께 봅니다. 음성 대화를 한 시간대에 서비스와 통신했는지는 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)으로 맞춰 봅니다. 회의 녹음을 받아쓰는 앱은 음성 대화와 저장 방식이 달라서 [AI 회의록 앱](meeting-notes.md)에서 따로 다루고, 기기에서 흔적을 모으는 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)에 있습니다.

## 실습

AI 음성 대화의 흔적이 든 공개 검체는 알려진 것이 없어서, 시험용 계정과 시험용 기기로 풀어 봅니다.

1. Gemini 앱에서 활동 기록 저장을 켜고 Gemini Live 로 짧은 가짜 대화를 한 뒤, Google Takeout 으로 내보내 녹음과 대화 기록이 어떤 파일로 들어오는지 확인합니다.
2. 같은 대화를 임시 채팅으로 한 번 더 하고, 내보내기 결과에서 무엇이 달라지는지 비교합니다.
3. iOS 의 ChatGPT 앱으로 음성 대화를 한 뒤 전체 파일 시스템을 추출해, `tmp/recordings/` 에 `m4a` 가 생기는지와 대화 JSON 의 `voice_mode_message` 값이 어떻게 남는지 봅니다.
4. ChatGPT 계정 내보내기를 받아 `conversations.json` 에서 `voice_mode_message` 가 붙은 메시지를 찾고, 묶음 안에 음성 파일이 따로 있는지 위 시작 바이트 표로 가립니다.

## 참고 문헌

1. Gemini Apps Privacy Hub (Google 도움말, 2026-09-24 갱신) — https://support.google.com/gemini/answer/13594961?hl=en
2. GitHub, abrignoni/RLEAPP, `scripts/artifacts/chatgpt.py`(작성 Evangelos Dragonas, 검증 2024-07-09) — https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/chatgpt.py
3. GitHub, abrignoni/iLEAPP, `scripts/artifacts/chatgpt.py`(작성 Evangelos Dragonas, 2026-08-21 갱신) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/chatgpt.py
4. GitHub, abrignoni/ALEAPP, `scripts/artifacts/chatgpt.py`(작성 Evangelos Dragonas, 2026-08-01 갱신) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/chatgpt.py
5. Microsoft Learn, "Updated Windows and Microsoft Copilot Chat experience" (ms.date 2025-11-20, 갱신 2026-08-18), "Copilot key and voice in Microsoft Copilot" 절 — https://learn.microsoft.com/en-us/windows/client-management/manage-windows-copilot
6. Shishir Panta, Ruba Alsmadi, Ibrahim Baggili, "Seeing the Evidence: A Forensic Framework for Analyzing Ray-Ban Meta AI Smart Glasses", DFRWS USA 2026 발표 논문(4.3절, 표 4·5, 삭제·초기화 실험)
