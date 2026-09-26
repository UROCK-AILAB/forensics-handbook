---
title: "AI 생성물의 출처 정보"
parent: "기반 · 기본 개념"
nav_order: 60
---

# AI 생성물의 출처 정보 (C2PA·Content Credentials·워터마크)

AI 생성물의 출처 정보는 파일에 붙어 서명으로 보호되는 출처 정보 묶음(C2PA Manifest, Content Credential)과 콘텐츠 안에 보이지 않게 섞여 들어가는 워터마크 두 종류로 남고, 둘은 무엇을 증명하는지와 어떻게 사라지는지가 다릅니다.

C2PA 내용은 명세 설명서 2.2 판 기준입니다 [1].

## 이 형식을 쓰는 아티팩트

출처 정보는 AI 로 만든 이미지·영상·오디오·텍스트 같은 생성물 자체에 붙거나 섞여 들어갑니다. 앱 폴더나 설정에 남는 흔적이 아니라서 OS 별 저장 위치로 나누지 않고, Windows·macOS·Android·iOS 어디에서 발견한 파일이든 같은 방법으로 읽습니다. 생성물이 대화 기록 안에서 어떻게 구분되는지는 [프롬프트·첨부·생성물 구분하기](prompt-attachment-output.md) 에서 다룹니다.

Google 은 생성물에 워터마크를 넣습니다. Google DeepMind 의 SynthID 는 AI 생성 콘텐츠에 보이지 않는 워터마크를 넣고 찾아내는 도구로 이미지·영상·오디오·텍스트를 대상으로 하고, Gemini 앱, Lyria(음악), NotebookLM 의 팟캐스트 기능을 비롯한 Google 의 소비자용 생성형 AI 제품에 들어가 있습니다 [2]. 텍스트에는 생성하는 동안 단어별 확률 점수를 조정하는 방식으로 워터마크를 넣습니다 [2]. SynthID 를 언제부터 적용했는지는 공개되지 않았으므로, 어떤 생성물에 워터마크가 들어갔는지는 파일마다 탐지 도구로 확인합니다.

다른 서비스가 C2PA 출처 정보나 워터마크를 넣는지는 그 서비스의 공식 자료와 실제 파일의 Manifest 로 확인합니다. 서비스별 내용은 [Midjourney와 이미지 생성 서비스](../../02-artifacts/generative-media/image-generation.md), [ChatGPT](../../02-artifacts/chat-services/chatgpt/index.md), [Microsoft Copilot](../../02-artifacts/chat-services/copilot/index.md), [Gemini](../../02-artifacts/chat-services/gemini/index.md), [Claude](../../02-artifacts/chat-services/claude/index.md) 페이지에서 다룹니다.

## 구조

### 두 방식 비교

| | C2PA 출처 정보 | 워터마크 |
|---|---|---|
| 들어가는 자리 | 파일에 붙은 서명된 정보 | 콘텐츠 안에 섞여 들어감 |
| 콘텐츠와 묶는 방식 | 자산 내용의 암호 해시로 묶는 하드 바인딩 (hard binding) | 소프트 바인딩 (soft binding) 으로 출처 정보를 다시 찾는 데 쓰기도 함 |
| 바뀌었을 때 | 자산이나 출처 정보를 조금만 바꿔도 해시가 맞지 않음 | SynthID 는 자르기·필터·손실 압축 등을 견딤 |
| 근거 | [1] | [1][2] |

소프트 바인딩은 보이지 않는 워터마크나 지문 (fingerprint) 조회로 출처 정보 묶음을 다시 찾는 방식이고, 메타데이터가 떨어져 나가도 찾을 수 있게 하려고 둡니다 [1]. SynthID 가 C2PA 의 소프트 바인딩으로 쓰이는지는 공개되지 않았으므로 두 가지를 별개로 봅니다. SynthID 가 견디는 변형은 이미지·영상에서는 자르기, 필터, 프레임 속도 변경, 손실 압축이고, 오디오에서는 잡음 추가, MP3 압축, 속도 변경입니다 [2].

### C2PA 용어

| 용어 | 뜻 |
|---|---|
| Manifest (Content Credential) | 자산의 출처에 관한 정보 묶음으로, 하나 이상의 assertion 으로 이뤄지고 진위와 무결성을 지키려고 디지털 서명한 것 |
| 진술 (Assertion) | 자산에 대한 진술을 담은 자료 구조이고 Manifest 의 일부 |
| 청구 (Claim) | 서명자가 책임지는 `created_assertions` 와 서명자가 책임지지 않는 `gathered_assertions` 로 나뉨 |
| 콘텐츠 바인딩 (Content binding) | 디지털 콘텐츠를 특정 자산의 특정 Manifest 에 묶는 정보 |
| 서명 | 표준 X.509 인증서를 쓰고, SHA2-256 같은 표준 해시와 Merkle 트리 비슷한 방식을 씀 |
| 신뢰 목록 (C2PA Trust List) | C2PA 가 관리하는 서명자 목록으로, 웹 브라우저나 PDF 뷰어가 따로 두는 신뢰 목록과 비슷함 |

모든 내용의 근거는 [1] 입니다.

### AI 생성을 나타내는 값

C2PA 는 AI 가 한 동작을 `digitalSourceType` 필드로 표시합니다 [1]. 이 필드에 들어가는 값은 IPTC 의 디지털 출처 유형 어휘(`http://cv.iptc.org/newscodes/digitalsourcetype/`)에서 가져오고, AI 와 관련된 값은 아래 둘입니다 [3].

| 값 | 뜻 |
|---|---|
| `trainedAlgorithmicMedia` | 실제로 찍거나 녹음한 자료로 학습한 AI 모델이 만든 콘텐츠 |
| `compositeWithTrainedAlgorithmicMedia` | 생성형 AI 모델로 덧붙이거나 고치거나 보정한 콘텐츠(인페인팅·아웃페인팅 등) |

### 파일 안의 위치

Manifest 가 파일 형식별로 어느 부분에 어떤 컨테이너로 들어가는지, 원격 Manifest 를 어떻게 가리키는지는 설명서가 아니라 C2PA 기술 명세 본문에서 다룹니다. 오프셋이나 개별 assertion 이름이 필요하면 분석 대상 파일이 따른 판의 기술 명세 본문을 보고 확인합니다.

## 읽는 법

1. 원본 파일을 해시와 함께 보존하고 사본으로 작업합니다. C2PA 를 모르는 도구로 자르기 같은 편집을 하면 출처 정보가 갱신되지 않을 수 있어서 [1], 사본을 편집 도구로 열어 다시 저장하지 않습니다.
2. C2PA 를 읽는 도구로 Manifest 가 있는지 봅니다.
3. Manifest 가 있으면 서명이 유효한지와 서명자가 신뢰 목록에 있는지를 확인합니다.
4. 하드 바인딩의 해시가 지금 파일 내용과 맞는지 봅니다. 맞지 않으면 서명한 뒤에 자산이나 출처 정보가 바뀐 것입니다.
5. `digitalSourceType` 과 동작 기록을 읽어 AI 가 처음부터 만든 것인지, 다른 콘텐츠를 AI 로 고친 것인지 구분합니다. 서명자가 책임지는 `created_assertions` 와 그렇지 않은 `gathered_assertions` 가운데 어디에 적힌 내용인지도 함께 적습니다.
6. Manifest 가 없으면 워터마크를 확인합니다. SynthID 는 기자·미디어 전문가를 대상으로 초기 시험 중인 SynthID Detector 포털에서 확인하거나, 이미지·영상·오디오는 Gemini 앱에 올려 Google AI 로 만들거나 바꿨는지 물어볼 수 있습니다 [2]. 두 방법 모두 증거 파일을 외부 서비스에 올리는 일이라서 조사 규칙상 허용되는지를 먼저 확인합니다.

## 포렌식에서 중요한 점

유효한 C2PA 출처 정보는 신뢰 목록에 있는 서명자가 서명했다는 것과, 하드 바인딩 해시가 맞으면 서명한 뒤로 자산이 바뀌지 않았다는 것을 보여 줍니다. 하지만 검증 결과는 출처 정보의 형식이 맞고 변조되지 않았다는 것만 알려 줄 뿐 적힌 내용이 참인지 판단하지 않으므로 [1], 출처 정보에 적힌 제작 과정은 서명자의 진술로 다룹니다.

출처 정보가 없다는 사실은 사람이 만들었다는 증거가 되지 못합니다. C2PA 는 메타데이터가 떨어져 나가도 출처 정보를 다시 찾으려고 소프트 바인딩을 두고, C2PA 를 모르는 도구로 편집하면 출처 정보가 갱신되지 않을 수 있습니다 [1]. 워터마크도 보이지 않는 신호라서 탐지 결과는 탐지 도구와 그 도구를 만든 회사의 설명에 기대게 되며, AI 생성 여부를 판별하는 방법 전반의 한계는 [AI가 만든 글·이미지 판별의 한계](../../03-techniques/analysis/detection-limits.md) 에서 다룹니다.

보고서에는 "이 이미지는 AI 가 만들었다" 가 아니라 "이 파일에는 서명자 누구의 C2PA 출처 정보가 있고, 서명은 유효하며, `digitalSourceType` 이 `trainedAlgorithmicMedia` 로 적혀 있다" 처럼 기록으로 확인되는 만큼만 씁니다. 누가 그 생성물을 만들었는지는 출처 정보만으로 정해지지 않고 기기와 계정의 사용 흔적을 함께 봐야 하며, 이 흐름은 [이 글·이미지는 AI가 만들었나](../../04-scenarios/attribution/ai-generated.md) 와 [딥페이크·합성 이미지를 만들었나](../../04-scenarios/misuse/deepfake.md) 에서 다룹니다.

## 함정

- **검증 통과를 내용의 진실로 읽지 않습니다.** 신뢰 목록에 있는 서명자라는 사실과 적힌 내용이 사실이라는 것은 별개입니다 [1].
- **"출처 정보 없음" 을 "AI 아님" 으로 읽지 않습니다.** 편집·변환 과정에서 출처 정보가 빠지거나 갱신되지 않을 수 있습니다 [1].
- **AI 생성과 AI 합성을 나누어 씁니다.** `trainedAlgorithmicMedia` 와 `compositeWithTrainedAlgorithmicMedia` 는 뜻이 달라서 [3], AI 로 고친 사진을 "AI 가 만든 이미지" 로 적으면 기록보다 나간 말이 됩니다.
- **워터마크와 C2PA 를 한 가지로 묶지 않습니다.** 워터마크는 콘텐츠 안에 섞이고 C2PA 는 파일에 붙은 서명된 정보라서 [1][2], 한쪽 결과로 다른 쪽을 대신 말하지 않습니다.
- **서비스 적용 범위를 짐작하지 않습니다.** 어느 서비스가 언제부터 어떤 생성물에 출처 정보를 넣는지는 공식 자료로 확인한 범위만 씁니다.

## 도구

C2PA 출처 정보는 C2PA 를 읽는 공개 도구(예: c2patool, Content Credentials 확인 사이트)로 보고, 워터마크는 넣은 회사가 제공하는 탐지 도구로 확인합니다. SynthID 는 SynthID Detector 포털과 Gemini 앱으로 확인합니다 [2]. 도구를 쓸 때는 결과와 함께 도구 이름·버전·확인 날짜를 기록합니다.

## 참고 문헌

1. C2PA Specifications — Explainer (2.2) — https://spec.c2pa.org/specifications/specifications/2.2/explainer/Explainer.html
2. Google DeepMind — SynthID — https://deepmind.google/technologies/synthid/
3. IPTC — Digital Source Type vocabulary — https://cv.iptc.org/newscodes/digitalsourcetype/
