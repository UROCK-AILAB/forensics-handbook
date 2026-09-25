---
title: "이 글·이미지는 AI가 만들었나"
parent: "시나리오 · 사용자와 출처"
nav_order: 1000
---

# 이 글·이미지는 AI가 만들었나 (AI-Generated Content)

## 조사 질문

손에 든 이미지·영상·음성·글 하나를 두고 "AI 가 만들었는가, 만들었다면 어떤 도구로 누가 만들었는가" 를 묻는 조사입니다. 답을 찾는 길은 둘인데, 하나는 파일 자체에 든 출처 표시(C2PA 매니페스트, IPTC 원천 유형 값, 보이지 않는 워터마크)를 읽는 길이고, 다른 하나는 파일을 만든 쪽 기기나 계정에 남은 대화·생성 기록을 찾는 길입니다. 내용만 보고 AI 가 썼는지 가리는 판별기의 한계는 [AI가 만든 글·이미지 판별의 한계](../../03-techniques/analysis/detection-limits.md)에서 따로 다루고, 이 글은 기록으로 확인할 수 있는 흔적에 집중합니다.

## 먼저 확인할 것

**받은 파일이 원본인가.** 출처 표시는 파일 안에 들어 있기도 하고 파일 밖에 따로 두기도 해서, 받은 파일이 원본인지 여러 번 다시 저장한 사본인지에 따라 찾을 수 있는 것이 달라집니다. 먼저 입수 경로와 해시를 적고, 분석은 사본으로 합니다.

**출처 표시가 무엇을 보장하는가.** C2PA 매니페스트(Content Credential)는 자산의 출처 정보를 담은 주장(assertion) 묶음에 디지털 서명을 한 것입니다. 이 표시는 출처 정보가 형식에 맞고 조작되지 않았는지만 알려 주고, 그 정보가 참인지는 판단하지 않습니다.

서명이 멀쩡하다는 결과는 "서명한 쪽이 이렇게 주장했고 그 뒤로 바뀌지 않았다" 까지만 말해 줍니다. 또 출처 표시는 선택 사항이고, 표시가 없는 자산을 덜 믿게 만들려는 장치가 아닙니다. 그래서 표시가 없다는 사실로 사람이 만들었다고 말할 수 없습니다. 매니페스트 구조와 서명 원리는 [AI 생성물의 출처 정보](../../01-foundations/concepts/c2pa-provenance.md)에서 다룹니다.

**어떤 종류의 파일인가.** 이미지·영상·음성은 C2PA 와 워터마크를 모두 찾아볼 수 있습니다. Google 은 SynthID 워터마크를 이미지·오디오·텍스트·영상에 넣습니다. 글에 넣는 곳으로 알려진 것은 Gemini 앱·웹뿐이라서, 다른 서비스에서 만든 글은 만든 쪽 기록을 찾는 길에 더 기대게 됩니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 파일 안의 C2PA 매니페스트, 없으면 워터마크·지문 조회로 찾는 외부 매니페스트 | 서명한 쪽이 밝힌 생성·편집 이력 | [AI 생성물의 출처 정보](../../01-foundations/concepts/c2pa-provenance.md) |
| 2 | 매니페스트 안의 `digitalSourceType` 값(IPTC 원천 유형 어휘) | AI 가 전부 만들었는지, 일부만 보정·합성했는지 | [AI 생성물의 출처 정보](../../01-foundations/concepts/c2pa-provenance.md) |
| 3 | SynthID 워터마크 | Google 생성형 AI 제품에서 나온 결과물인지 | [Gemini](../../02-artifacts/chat-services/gemini/index.md) |
| 4 | 만든 쪽 기기·계정의 대화·생성 기록 | 어떤 프롬프트로 무엇을 만들었는지 | [Midjourney와 이미지 생성 서비스](../../02-artifacts/generative-media/image-generation.md), [로컬 이미지 생성 도구](../../02-artifacts/local-ai/image-gen-local.md) |
| 5 | Claude Code 대화 기록과 `file-history/` | 어떤 파일 변경이 AI 도구 호출에서 나왔는지 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) |
| 6 | 조직이 걸어 둔 훅의 로그 | AI 응답·도구 사용을 따로 남긴 기록 | [Cursor](../../02-artifacts/dev-agents/cursor.md), [MCP 서버와 도구 호출 기록](../../02-artifacts/dev-agents/mcp.md) |
| 7 | 서비스 계정 데이터 내보내기 | 서버에만 있는 대화·생성 원본 | [계정 데이터 내보내기로 수집](../../03-techniques/acquisition/export-collection.md) |

## 분석 흐름

1. **증거를 고정합니다.** 받은 파일의 해시를 적고 입수 경로(메신저로 받았는지, 원본 저장 장치에서 떴는지)를 기록한 뒤, 모든 분석은 사본으로 합니다.

2. **매니페스트를 찾습니다.** C2PA 매니페스트는 보통 파일 안에 넣지만, 파일 밖에 두고 보이지 않는 워터마크나 지문 조회(soft binding)로 다시 찾게 할 수도 있습니다. 파일 안에 매니페스트가 없다고 조사를 끝내지 않고, 워터마크나 지문으로 외부 매니페스트를 찾을 수 있는지까지 확인합니다. 파일 형식마다 매니페스트를 담는 자리가 다르므로, 공개된 C2PA 검증 도구로 읽고 도구 이름과 판을 적어 둡니다.

3. **누가 무엇을 주장했는지 가릅니다.** 서명한 쪽의 주장으로 볼 수 있는 것은 `created_assertions` 에 든 주장뿐이고, `gathered_assertions` 는 다른 곳에서 모아 온 주장입니다. 보고서에 "누가 AI 생성이라고 밝혔다" 고 쓸 때는 그 주장이 어느 쪽에 들어 있는지부터 적습니다.

4. **원천 유형 값을 읽습니다.** AI·기계 학습이 한 동작은 `digitalSourceType` 칸으로 표시하고, 값은 IPTC 원천 유형 어휘(`http://cv.iptc.org/newscodes/digitalsourcetype/`)를 씁니다. 값마다 뜻이 크게 달라서 아래처럼 나눠 읽습니다.

   | 값 | 뜻 |
   |---|---|
   | `trainedAlgorithmicMedia` | 학습된 AI 모델이 만든 미디어 |
   | `compositeWithTrainedAlgorithmicMedia` | 생성형 AI 로 일부를 보정하거나 늘린 미디어(인페인팅·아웃페인팅) |
   | `compositeSynthetic` | 여러 요소를 합성했고 그 가운데 하나 이상이 생성형 AI |
   | `algorithmicMedia` | 학습 데이터 없이 알고리즘만으로 만든 미디어 |
   | `algorithmicallyEnhanced` | 사람이 시켜 알고리즘으로 보정했고 주 내용은 그대로인 미디어 |

   학습된 AI 모델이 처음부터 만든 것을 가리키는 값은 `trainedAlgorithmicMedia` 하나이고, `compositeWithTrainedAlgorithmicMedia`·`compositeSynthetic`·`algorithmicallyEnhanced` 는 다른 요소나 원본이 섞인 경우, `algorithmicMedia` 는 학습된 모델이 아닌 알고리즘으로 만든 경우입니다.

5. **워터마크를 확인합니다.** Google 은 SynthID 를 이미지·영상은 자사 생성형 AI 소비자 제품에, 오디오는 Lyria 와 NotebookLM 팟캐스트 생성에, 텍스트는 Gemini 앱·웹에 넣습니다. 이미지·영상 워터마크는 자르기·필터·프레임 수 변경·손실 압축에, 오디오 워터마크는 잡음·MP3 압축·속도 변경에 버티도록 만들어졌습니다. 확인은 Gemini 앱에 파일을 올려 Google AI 로 만들었는지 묻거나, 기자·미디어 전문가와 시험 중인 SynthID Detector 포털로 합니다. 어느 쪽이든 증거 사본을 외부 서비스에 올리는 일이므로, 사건 규정과 동의 범위를 먼저 확인하고 올린 날짜와 받은 답을 그대로 기록합니다.

6. **만든 쪽 기록을 찾습니다.** 용의 기기나 계정이 있으면 생성 서비스의 대화·생성 기록에서 같은 결과물을 찾습니다. 파일 해시가 같거나 프롬프트와 결과물이 짝지어 남아 있어야 "이 계정에서 만든 것" 이라고 말할 수 있고, 비슷한 주제의 대화가 있다는 것만으로는 부족합니다. 기록이 서버에만 있으면 계정 데이터 내보내기로 받습니다. 대화를 한 사람을 좁히는 절차는 [그 대화를 한 사람이 누구인가](user-attribution.md)에서 다룹니다.

7. **코드라면 수정 전후를 맞춰 봅니다.** Claude Code 의 `projects/*.jsonl` 에는 모든 메시지와 도구 호출, 도구 결과가 들어 있고, `file-history/<session>/` 에는 Claude 가 고친 파일의 수정 전 사본이 남습니다. 도구 호출 기록과 수정 전 사본을 현재 파일과 비교하면 어느 줄을 AI 도구가 바꿨는지 가릴 수 있습니다. 대화 기록에는 `message.model`, `toolUseResult`, `snapshot.trackedFileBackups`, `isSidechain`, `attributionPlugin`, `attributionSkill`, `attributionAgent` 키가 있습니다(Windows 11 기준). `attribution` 으로 시작하는 키는 뜻을 설명한 공개 문서가 없으므로, 보고서에는 값을 그대로 옮기고 해석을 덧붙이지 않습니다.

8. **조직 훅 로그를 봅니다.** Cursor 의 `hooks.json` 에는 `afterAgentResponse`, `postToolUse`, `beforeSubmitPrompt` 같은 훅 키가 있고, Claude Code `settings.json` 에도 `hooks.PreToolUse`, `hooks.UserPromptSubmit` 같은 키가 있습니다. 조직이 이 훅에 AI 응답이나 도구 사용을 기록하는 명령을 걸어 두었다면, 그 명령이 쓴 로그가 사용자 기기의 대화 기록과 따로 남는 증거가 됩니다.

9. **결론의 수위를 정합니다.** 서명이 멀쩡한 매니페스트와 AI 원천 유형 값, 만든 쪽 기록이 모두 맞으면 가장 강하게 쓸 수 있고, 표시 하나만 있으면 그 표시가 말하는 만큼만 씁니다. 아무 표시도 기록도 없으면 "판단할 기록이 없다" 로 씁니다.

## 흔한 오판

**표시가 없으니 사람이 만들었다고 보는 경우.** C2PA 표시는 선택 사항이고, 매니페스트가 파일 밖에 있을 수도 있습니다. 표시가 없다는 결과는 "이 파일에서 출처 표시가 나오지 않았다" 이상을 말하지 않습니다.

**서명이 멀쩡하니 내용이 사실이라고 보는 경우.** C2PA 검증은 출처 정보가 형식에 맞고 조작되지 않았는지만 확인하고, 사진 속 장면이 실제로 있었는지는 판단하지 않습니다.

**모아 온 주장을 서명자의 주장으로 읽는 경우.** `gathered_assertions` 에 든 내용은 서명한 쪽이 만든 주장이 아니므로, 이 부분만 근거로 "서명자가 AI 생성이라고 밝혔다" 고 쓰지 않습니다.

**일부 보정을 전부 생성으로 읽는 경우.** `compositeWithTrainedAlgorithmicMedia` 나 `algorithmicallyEnhanced` 는 사람이 만든 원본에 AI 가 손댄 경우를 포함하고, `trainedAlgorithmicMedia` 와 같은 뜻이 아닙니다.

**SynthID 가 안 나오니 AI 가 아니라고 보는 경우.** SynthID 는 Google 제품이 넣는 워터마크입니다. 검출되지 않았다는 결과는 다른 회사 모델이나 워터마크를 넣지 않는 도구로 만들었을 가능성을 지우지 못합니다.

## 보고서 문장 예

아래 문장은 형식을 보여 주려고 만든 예시이고, 파일 이름과 값은 모두 가짜입니다.

> 제출받은 이미지 `sample_photo_01.jpg` 에는 C2PA 매니페스트가 들어 있고 서명 검증은 성공하였다. 서명자가 만든 주장(`created_assertions`)의 원천 유형 값은 `compositeWithTrainedAlgorithmicMedia` 로, 서명한 쪽이 이 이미지를 생성형 AI 로 일부 보정·확장한 것으로 표시하였음을 뜻한다. 이 결과는 이미지 속 장면이 실제로 있었는지를 판단하지 않는다.

> 제출받은 음성 파일 `sample_voice_02.mp3` 에서는 C2PA 매니페스트가 나오지 않았다. 이 결과만으로 AI 생성 여부를 판단할 수 없으며, 파일을 만든 것으로 지목된 계정의 생성 기록은 입수하지 않은 상태이다.

## 함께 볼 페이지

- [AI 생성물의 출처 정보](../../01-foundations/concepts/c2pa-provenance.md) — C2PA 매니페스트 구조, 워터마크 원리
- [AI가 만든 글·이미지 판별의 한계](../../03-techniques/analysis/detection-limits.md) — 내용 기반 판별기의 한계
- [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md) — 대화 기록 안에서 생성물을 가리는 법
- [딥페이크·합성 이미지를 만들었나](../misuse/deepfake.md) — 합성 이미지를 만든 쪽을 조사할 때
- [AI 에이전트가 무엇을 실행했나](../agents/agent-actions.md) — 에이전트가 바꾼 파일을 따라갈 때
- [그 대화를 한 사람이 누구인가](user-attribution.md) — 만든 계정 뒤의 사람을 좁힐 때
- [AI 관련 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) — 결론 수위와 문장

## 참고 문헌

- C2PA, C2PA Explainer 2.2. https://spec.c2pa.org/specifications/specifications/2.2/explainer/Explainer.html (2026-09-25 확인)
- IPTC, NewsCodes — Digital Source Type. http://cv.iptc.org/newscodes/digitalsourcetype/ (2026-09-25 확인)
- Google DeepMind, SynthID. https://deepmind.google/models/synthid/ (2026-09-25 확인)
- Anthropic, Claude Code Docs — Explore the .claude directory (application data). https://code.claude.com/docs/en/claude-directory (2026-09-25 확인)
