---
title: "AI가 만든 글·이미지 판별의 한계"
parent: "기법 · 분석"
nav_order: 800
---

# AI가 만든 글·이미지 판별의 한계 (Detection Limits)

글이나 이미지 하나만 보고 AI 가 만들었는지 가리는 방법(출처 메타데이터, 보이지 않는 워터마크, 생성 도구가 남긴 정보, 문체 특징)마다 무엇을 말해 주고 무엇을 말해 주지 못하는지 정리하고, 결론을 결과물 자체보다 생성 기록 쪽에서 찾는 순서를 설명합니다.

> 확인 날짜: 2026-09. C2PA 는 명세 설명서 2.2 판을 기준으로 씁니다(사이트에는 2.4 판까지 올라 있습니다). 서비스별 적용 여부는 자주 바뀌고, OpenAI 이미지의 C2PA 적용 범위와 OpenAI 글 분류기에 관한 공지는 이번에 열지 못해 적지 않습니다. 판별은 파일 자체를 보는 일이라 OS 에 따라 방법이 달라지지 않지만, 생성 기록을 찾는 곳은 OS 와 앱마다 다릅니다.

## 언제 쓰나

"이 이미지는 AI 가 만든 것인가", "이 보고서나 피싱 메일 문구를 AI 로 썼나" 를 물을 때 씁니다. 결과물만 손에 있고 만든 사람의 기기나 계정은 아직 없는 단계에서 특히 자주 나오는 질문입니다. 전체 조사 흐름은 [이 글·이미지는 AI가 만들었나](../../04-scenarios/attribution/ai-generated.md)에 있고, 이 페이지는 그 가운데 판별 방법 하나하나의 한계를 다룹니다.

## 절차

### 1. 질문을 기록으로 답할 수 있는 모양으로 바꿉니다

"AI 가 만들었나" 는 결과물만으로 답이 나오지 않는 경우가 많아서, 먼저 "이 파일에 AI 생성 표시가 있나", "이 표시에 누가 서명했나", "이 사람의 기기나 계정에 이 결과물을 만든 기록이 있나" 처럼 기록으로 답할 수 있는 질문으로 나눕니다. 앞의 두 질문은 파일만으로 답할 수 있고, 마지막 질문은 기기나 계정을 확보해야 답할 수 있습니다.

### 2. 받은 파일을 그대로 고정합니다

출처 정보와 워터마크는 파일을 다시 저장하거나 잘라 내면 깨지거나 사라질 수 있습니다. C2PA 명세 설명서는 C2PA 를 모르는 도구로 자르기 같은 편집을 하면 출처 정보가 갱신되지 않을 수 있다고 적습니다. 그래서 받은 원본 파일의 해시를 먼저 계산하고, 모든 검사는 사본으로 합니다. 메신저나 SNS 를 거친 사본밖에 없다면 그 사실을 기록에 남깁니다.

### 3. 출처 메타데이터(C2PA)를 확인합니다

C2PA 매니페스트(Content Credential)는 자산의 출처에 관한 주장(assertion) 묶음에 디지털 서명을 한 것이고, AI 가 한 동작은 `digitalSourceType` 칸으로 표시합니다. 자주 보는 값은 IPTC 어휘의 `trainedAlgorithmicMedia`(학습된 AI 모델이 만든 미디어)와 `compositeWithTrainedAlgorithmicMedia`(생성형 AI 로 보정·확장한 합성물)입니다. 구조와 값 목록은 [AI 생성물의 출처 정보](../../01-foundations/concepts/c2pa-provenance.md)에 있습니다.

C2PA 로 판별할 때 한계는 네 가지입니다. 첫째, 검증은 출처 정보가 형식에 맞고 변조되지 않았는지만 보여 줄 뿐 내용이 참인지 판단하지 않는다고 설명서가 분명히 적습니다. 둘째, 서명자에게 귀속되는 것은 `created_assertions` 에 든 주장뿐이고 `gathered_assertions` 는 모아 온 것이라서, 어느 쪽에 든 주장인지 나눠 읽어야 합니다. 셋째, 신뢰 판단은 서명자가 C2PA Trust List 에 있는지를 확인하는 일이지 서명자의 말이 옳다는 보증이 아닙니다. 넷째, 출처 표시는 선택 사항이고 표시가 없는 자산을 덜 믿게 하려는 것이 아니라고 명시해서, 매니페스트가 없다고 사람이 만든 것이라는 뜻이 되지 않습니다.

### 4. 보이지 않는 워터마크를 확인합니다

Google SynthID 는 Google 생성형 AI 가 만든 이미지·영상·오디오·텍스트에 보이지 않는 워터마크를 넣고, 텍스트는 생성 중 단어별 확률 점수를 조정하는 방식으로 넣습니다. 이미지·영상 워터마크는 자르기, 필터, 프레임 속도 변경, 손실 압축을 견디도록 설계했다고 Google 이 설명합니다. 확인 방법은 Gemini 앱에 파일을 올려 Google AI 로 만들거나 바꿨는지 묻는 것과, 기자·미디어 전문가 대상으로 시험 중인 SynthID Detector 포털입니다.

워터마크 검사의 한계는 범위에 있습니다. SynthID 는 Google 모델이 만든 결과물에 넣는 표시라서, 검출되지 않았다는 결과는 "Google 모델의 워터마크가 보이지 않는다" 까지만 말하고 다른 회사 모델이나 로컬 모델로 만들었을 가능성은 그대로 남습니다. 워터마크가 어떤 편집까지 견디는지는 만든 쪽의 설명이고, 이 핸드북에서 따로 시험하지 않았습니다. 워터마크(soft binding)는 콘텐츠 안에 섞여 들어가고 C2PA 메타데이터(hard binding)는 파일에 붙은 서명된 정보라서, 두 검사의 결과가 서로 다를 수 있다는 점도 함께 적습니다.

### 5. 생성 도구가 파일에 남긴 정보를 확인합니다

로컬 이미지 생성 도구는 파일 안에 생성 정보를 남기는 경우가 있습니다. ComfyUI 의 저장 노드는 PNG 텍스트 청크에 `prompt` 키로 노드 그래프를 JSON 문자열로 넣고, AUTOMATIC1111 은 PNG 텍스트 청크 `parameters` 나 JPEG·WebP 의 EXIF UserComment 에 프롬프트·시드 같은 생성 정보를 넣습니다. 이런 정보가 있으면 강한 단서가 되지만, ComfyUI 는 메타데이터를 끄는 옵션(`disable_metadata`)이 있어 정보가 없다고 생성 이미지가 아니라고 볼 수 없습니다. 파일 이름에 남는 모양과 출력 폴더는 [로컬 이미지 생성 도구](../../02-artifacts/local-ai/image-gen-local.md)에 있고, 클라우드 서비스 쪽은 [Midjourney와 이미지 생성 서비스](../../02-artifacts/generative-media/image-generation.md)에 있습니다. 헥스 편집기로 볼 때는 파일 안에서 `prompt`·`parameters` 같은 키워드 문자열을 찾고, 그 뒤에 이어지는 텍스트를 읽습니다.

### 6. 글(텍스트)은 문체 특징을 의심 근거로만 씁니다

글을 복사해 다른 곳에 붙이면 출처 표시가 따라가는지는 이 핸드북에서 확인하지 못했고, 텍스트 워터마크는 SynthID 처럼 특정 회사 모델의 결과물에만 해당합니다. 글만으로 AI 작성 여부를 판정하는 판별기의 정확도 자료는 이번에 확인하지 못해 수치를 적지 않습니다.

문체 특징이 어떻게 쓰이는지는 보안 업계 사례에서 볼 수 있습니다. Microsoft 위협 인텔리전스는 2025년 9월 SVG 첨부로 퍼진 피싱 캠페인을 분석하면서, 영어 설명 단어 뒤에 무작위 16진수를 붙인 긴 이름, 필요 이상으로 잘게 나눈 모듈, 격식 있고 일반적인 주석 같은 특징을 LLM 이 만든 코드의 표시로 들었습니다. 그래도 차단은 이런 AI 특징이 아니라 자기 앞으로 보내고 실제 수신자는 숨은 참조로 넣은 발송 방식, PDF 로 위장한 SVG, 알려진 피싱 도메인 같은 기존 신호로 했다고 적고, "AI 가 만든 코드도 사람이 만든 공격과 같은 행동·인프라의 경계 안에서 움직인다" 고 정리했습니다. MITRE ATT&CK 도 말이 안 되는 주석을 근거로 LLM 이 만든 것으로 본 악성 코드(LazyWiper) 사례를 싣고 있는데, 이 역시 주석 모양을 보고 내린 판단입니다. 이런 특징은 "AI 로 만들었을 가능성을 살펴볼 까닭" 으로만 쓰고, 증명 수단으로 쓰지 않습니다.

### 7. 결론은 생성 기록에서 찾습니다

결과물에서 확정을 얻지 못하면 만든 쪽의 기록으로 갑니다. 코딩 도구라면 Claude Code 대화 기록(`~/.claude/projects/<프로젝트>/<세션>.jsonl`)에 모든 메시지, 도구 호출, 도구 결과가 남아서 어떤 파일 변경이 AI 도구 호출에서 나왔는지 대조할 수 있고, `file-history/<세션>/` 의 편집 전 사본과 비교하면 에이전트가 바꾼 부분을 가릴 수 있습니다. 다만 체크포인트는 Claude 의 편집 도구로 바꾼 파일만 추적하고 Bash 명령으로 바꾼 파일이나 사람이 직접 고친 부분은 잡지 않아서, 사본에 없는 변경을 사람이 했다고 단정하지 않습니다. 이 PC 의 대화 기록에는 `message.model`, `attributionPlugin`, `attributionSkill`, `attributionAgent`, `isSidechain` 키가 있었지만(확인 범위: Windows 11, 2026-09) `attribution*` 키의 뜻은 공식 문서로 확인하지 못했습니다. 웹 서비스라면 대화 원본이 서버에 있어 [계정 데이터 내보내기로 수집](../acquisition/export-collection.md)이나 [서비스 회사에 대한 데이터 요청](../acquisition/legal-requests.md)으로 얻습니다. 사건 갈래별 흐름은 [AI로 피싱·사기 문구를 만들었나](../../04-scenarios/misuse/phishing.md), [AI로 악성 코드를 만들었나](../../04-scenarios/misuse/malware-development.md), [딥페이크·합성 이미지를 만들었나](../../04-scenarios/misuse/deepfake.md)에 있습니다.

## 도구

C2PA 매니페스트는 C2PA 검증 도구(오픈소스 `c2patool` 등)로 읽을 수 있지만, 이번에 사용법 문서를 열지 못해 명령을 적지 않고 도구 문서를 직접 확인하기를 권합니다. PNG 텍스트 청크와 EXIF 는 헥스 편집기나 공개 메타데이터 도구로 읽습니다. SynthID 는 위에서 적은 두 경로 말고 공개된 검사 방법을 확인하지 못했습니다. 어느 도구를 쓰든 도구 이름과 버전, 검사한 파일의 해시를 결과와 함께 적습니다.

## 함정과 한계

가장 흔한 오판은 "표시가 없다 → 사람이 만들었다" 입니다. C2PA 는 선택 사항이고, 워터마크는 넣은 회사의 모델에만 있으며, 로컬 도구는 메타데이터를 끌 수 있어서 세 검사가 모두 비어도 AI 생성 가능성은 남습니다. 거꾸로 표시가 있어도 서명한 쪽의 주장일 뿐이고, 서명자가 신뢰 목록에 있다는 사실이 내용의 참을 보증하지 않습니다.

다시 저장하고 옮긴 파일은 검사 결과가 약해집니다. C2PA 를 모르는 도구로 편집하면 출처 정보가 갱신되지 않을 수 있고, 워터마크가 견딘다는 편집의 범위는 만든 쪽의 설명이라 독립적으로 확인한 값이 아닙니다.

사람과 AI 가 함께 만든 결과물이 많습니다. `compositeWithTrainedAlgorithmicMedia` 같은 값은 사람 작업에 AI 보정을 더한 경우를 따로 표시하고, 코드도 에이전트 편집과 사람 편집이 한 파일에 섞입니다. "AI 가 만들었다/아니다" 두 갈래로 답하지 말고 어느 부분이 어떤 기록으로 이어지는지 나눠 씁니다.

## 결과를 어떻게 해석하나

판별 결과는 검사한 방법과 그 방법이 말할 수 있는 범위를 함께 적어야 의미가 있습니다. C2PA 가 있으면 "누가 서명한 어떤 주장이 들어 있다" 를, SynthID 가 검출되면 "Google 의 확인 경로가 Google AI 생성·편집 표시를 보고했다" 를, 로컬 도구 메타데이터가 있으면 "이 파일에 생성 도구의 설정 정보가 들어 있다" 를 쓰고, 셋 다 없으면 "확인한 방법으로는 AI 생성 표시를 찾지 못했다" 로 씁니다. 누가 그 결과물을 만들었는지는 파일이 아니라 기기·계정 기록이 답할 문제라서, [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)로 넘깁니다.

보고서 문장은 다음처럼 씁니다(만든 예시).

- 좋은 예: "제출된 이미지 `sample_photo.jpg`(SHA-256 해시는 부록에 기재)에서 C2PA 매니페스트를 찾지 못했고, PNG·EXIF 생성 정보도 없었습니다. 이 결과는 이미지가 AI 로 만들어지지 않았다는 뜻이 아니며, 확인한 방법의 범위에서 AI 생성 표시가 발견되지 않았다는 뜻입니다."
- 피할 예: "판별 결과 이 이미지는 사람이 찍은 사진으로 확인되었다."

## 참고 문헌

- C2PA Specifications — Explainer 2.2. https://spec.c2pa.org/specifications/specifications/2.2/explainer/Explainer.html
- IPTC NewsCodes — Digital Source Type. http://cv.iptc.org/newscodes/digitalsourcetype/
- Google DeepMind — SynthID. https://deepmind.google/technologies/synthid/
- ComfyUI `nodes.py` (SaveImage·PreviewImage). https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/nodes.py
- AUTOMATIC1111 stable-diffusion-webui `modules/images.py`. https://raw.githubusercontent.com/AUTOMATIC1111/stable-diffusion-webui/master/modules/images.py
- Microsoft Security Blog, "AI vs. AI: Detecting an AI-obfuscated phishing campaign" (2025-09-24). https://www.microsoft.com/en-us/security/blog/2025/09/24/ai-vs-ai-detecting-an-ai-obfuscated-phishing-campaign/
- MITRE ATT&CK — T1588.007 Obtain Capabilities: Artificial Intelligence. https://attack.mitre.org/techniques/T1588/007/
- Claude Code Docs — Explore the .claude directory. https://code.claude.com/docs/en/claude-directory
- Claude Code Docs — Checkpointing. https://code.claude.com/docs/en/checkpointing
