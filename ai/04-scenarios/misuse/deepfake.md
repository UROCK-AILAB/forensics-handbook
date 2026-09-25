---
title: "딥페이크·합성 이미지를 만들었나"
parent: "시나리오 · 악용"
nav_order: 870
---

# 딥페이크·합성 이미지를 만들었나 (Deepfake)

확인 날짜는 2026-09입니다. 이 쪽에 나오는 얼굴 합성 도구 내용은 공개 문서에서 확인한 것이고, 관찰한 Windows 11 PC 에는 이미지·얼굴 합성 도구 폴더가 없었습니다 (확인 범위: Windows 11, 2026-09). 그래서 도구별 경로는 기기에서 관찰한 값이 아니라 문서에 적힌 이름입니다. 도구는 판이 자주 바뀌어서 이 날짜를 기준으로 읽어야 합니다.

## 조사 질문

실제 인물의 얼굴이나 모습을 합성한 이미지·영상을 용의자가 AI 도구로 만들었는지 묻는 조사입니다. 질문은 두 방향입니다. 용의자 기기에 합성 도구와 원본 사진, 결과물이 있는지를 보고, 문제의 이미지·영상 자체에 AI 생성 출처 정보가 남았는지를 봅니다.

MITRE ATT&CK 의 T1588.007 설명에는 사기·사칭용 합성 미디어를 만드는 쓰임이 들어 있고, 분류 전체는 [피싱 쪽](phishing.md)에 정리했습니다. Google GTIG 의 2025-11-06 보고서는 지하 시장의 AI 도구 광고 항목에 피싱 미끼와 본인 확인(KYC) 우회용 딥페이크·이미지 생성이 있다고 적었고, 북한 UNC1069 가 암호화폐 업계 인물을 사칭하는 딥페이크 이미지·영상을 썼다고도 적었습니다. 이 밖의 서비스 회사별 딥페이크 악용 사례 보고의 세부는 이 쪽에서 확인하지 못했습니다.

## 먼저 확인할 것

클라우드 서비스로 만들었는지 로컬 도구로 만들었는지가 증거 위치를 정합니다. 클라우드 이미지·영상 생성 서비스라면 생성 요청 원본(프롬프트와 올린 얼굴 사진)은 서비스 회사 서버에 있고, 기기에는 접속 흔적과 내려받은 결과물 정도가 남습니다. Gemini 앱의 활동 기록에 올린 사진이 남는 조건은 [Gemini](../../02-artifacts/chat-services/gemini/index.md) 쪽에, 서버 기록을 받는 절차는 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)에 있습니다. 로컬 도구라면 모델 파일·설정 파일·출력 폴더가 기기에 남고 서버 기록은 없습니다.

OS 판과 시간대, 조사할 사용자 계정, 수집 범위를 먼저 정합니다. OS 별 앱 데이터 보호 방식은 [피싱 쪽](phishing.md)의 표를 따릅니다. 로컬 얼굴 합성 도구의 OS 별 설치 위치는 이 쪽에서 확인하지 못했습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 문제의 이미지·영상의 출처 정보 | C2PA 콘텐츠 자격 증명, 워터마크 여부 | [AI 생성물의 출처 정보](../../01-foundations/concepts/c2pa-provenance.md) |
| 2 | 로컬 이미지 생성 도구가 넣은 메타데이터 | 프롬프트·생성 설정 | [로컬 이미지 생성 도구](../../02-artifacts/local-ai/image-gen-local.md) |
| 3 | 얼굴 합성 도구의 모델 폴더와 설치 흔적 | 도구를 설치했는지 | [로컬 모델 파일](../../02-artifacts/local-ai/model-files.md) |
| 4 | 얼굴 합성 도구의 설정 파일 | 대상 파일·출력 위치 | 이 쪽 아래 |
| 5 | 출력 폴더와 원본 사진 | 만든 결과물, 쓴 얼굴 사진 | 이 쪽 아래 |
| 6 | 클라우드 생성 서비스 접속 기록 | 서비스 이용 시각 | [Midjourney와 이미지 생성 서비스](../../02-artifacts/generative-media/image-generation.md), [AI 서비스 도메인과 네트워크 기록](../../02-artifacts/network-enterprise/network-traces.md) |
| 7 | 서비스 회사 서버 기록 | 생성 요청 원본, 올린 사진 | [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) |

### 로컬 얼굴 합성 도구: Deep-Live-Cam

Deep-Live-Cam README 에 따르면 `models` 폴더에 얼굴 보정용 `gfpgan-1024.onnx` 와 얼굴 교체용 `inswapper_128_fp16.onnx` 두 모델 파일을 두고, 모델은 Hugging Face 저장소에서 내려받습니다. 실행에는 Python 3.11~3.14, pip, git, ffmpeg 가 필요하고 Windows 에서는 Visual Studio 2022 런타임도 필요하며, `onnxruntime` 이나 그 변형(`onnxruntime-gpu`, `-directml`, `-openvino`, `-coreml`)을 씁니다. 이 두 모델 파일 이름과 필요한 구성 요소가 기기에서 도구 설치를 찾는 단서입니다.

영상 모드의 결과물은 대상 영상 이름을 딴 폴더에 저장됩니다. 웹캠 모드는 OBS 같은 캡처 도구로 화면을 잡도록 README 가 안내해서, 사용자가 녹화하지 않았다면 결과 파일이 없을 수 있습니다. 파일이 실제로 안 생기는지는 확인하지 못했습니다. README 에서 결과물에 워터마크를 넣는다는 설명은 찾지 못했습니다 (확인 날짜: 2026-09). 면책 문구에는 나체·잔혹물 같은 부적절한 미디어 처리를 막는 검사가 들어 있다고 적혀 있지만 구현 세부는 문서에 없습니다.

### 로컬 얼굴 합성 도구: FaceFusion

FaceFusion 의 설정 파일 `facefusion.ini` 에는 아래 절과 키가 있습니다.

| 절 | 키 |
|---|---|
| `[paths]` | `temp_path`, `jobs_path`, `target_path`, `output_path` |
| `[patterns]` | `output_pattern` |
| `[output_creation]` | `output_image_quality`, `output_video_encoder` 등 |
| `[download]` | `download_providers`, `download_scope` |
| `[execution]` | `execution_providers` |
| `[processors]` | `face_swapper_model`, `face_enhancer_model`, `lip_syncer_model`, `deep_swapper_model`, `age_modifier_model`, `expression_restorer_model` 등 |

사용자가 `target_path`, `output_path`, `jobs_path` 에 값을 넣었다면 대상 파일과 출력 위치를 찾는 단서가 됩니다. `[processors]` 절에는 얼굴 교체·얼굴 보정·입 모양 맞추기 같은 처리별 모델 키가 있습니다. 아래는 모양을 보여 주려고 만든 예시이고 경로는 가짜입니다.

```ini
; 만든 예시 (경로는 가짜)
[paths]
target_path = D:\sample\target_clip.mp4
output_path = D:\sample\out
```

기본값이 비어 있는지, 모델을 저장하는 폴더 이름이 무엇인지는 확인하지 못했습니다. 설정 파일에는 콘텐츠 검사(NSFW) 관련 키가 없고, 코드 안에 검사가 있는지는 확인하지 못했습니다.

### 결과물의 출처 정보

C2PA 콘텐츠 자격 증명 (Content Credentials)과 `digitalSourceType` 값, 워터마크의 뜻은 [AI 생성물의 출처 정보](../../01-foundations/concepts/c2pa-provenance.md)에서 설명합니다. ComfyUI·AUTOMATIC1111 이 PNG 에 프롬프트와 생성 설정을 넣는 방식과 그 기능을 끄는 옵션은 [로컬 이미지 생성 도구](../../02-artifacts/local-ai/image-gen-local.md)에 있습니다. 주요 클라우드 서비스가 만든 이미지에 C2PA·SynthID 가 실제로 들어가는지와 c2patool 사용법은 이 쪽에서 확인하지 못했습니다.

## 분석 흐름

1. 문제의 이미지·영상을 원본 그대로 확보하고 해시를 기록합니다.
2. 파일에서 C2PA 출처 정보와 생성 도구 메타데이터를 찾습니다.
3. 용의자 기기에서 얼굴 합성 모델 파일(`inswapper_128_fp16.onnx` 같은 이름), Python·ffmpeg·onnxruntime 설치 흔적, 도구 설정 파일을 찾습니다.
4. 설정 파일의 대상·출력 경로를 따라가 원본 얼굴 사진과 결과물을 찾고, 문제의 파일과 같은 파일이 있는지 해시로 비교합니다.
5. 클라우드 서비스 접속 기록이 있으면 시각을 타임라인에 올리고 서버 기록을 요청합니다.
6. 도구 설치 시각, 원본 사진 저장 시각, 결과물 생성 시각, 유포 시각을 한 타임라인에 놓습니다.

## 흔한 오판

C2PA 정보나 워터마크가 없다고 AI 로 만들지 않았다고 판정하는 일이 가장 흔합니다. Deep-Live-Cam README 에는 워터마크를 넣는다는 설명이 없고, 출처 정보가 남지 않거나 떨어져 나가는 경우는 [AI 생성물의 출처 정보](../../01-foundations/concepts/c2pa-provenance.md)에서 설명합니다. 판별 도구의 한계는 [AI가 만든 글·이미지 판별의 한계](../../03-techniques/analysis/detection-limits.md)에서 봅니다.

기기에 얼굴 합성 도구가 설치돼 있다는 사실만으로 문제의 파일을 그 도구로 만들었다고 쓰지 않습니다. 설정 파일의 경로나 출력 폴더의 파일처럼 문제의 파일과 이어지는 흔적이 있어야 합니다.

실시간 웹캠 모드로 쓴 경우 결과 파일이 없을 수 있어서, 출력 파일이 없다는 사실로 사용하지 않았다고 결론 내리지 않습니다.

Claude Code 세션 파일에는 `toolUseResult.isImage` 라는 키가 있지만 뜻을 확인하지 못했습니다 (확인 범위: Windows 11, 2026-09). 키 이름만 보고 이미지 생성 흔적으로 읽지 않습니다.

## 보고서 문장 예

아래 문장은 형식을 보여 주려고 만든 예시이고, 경로와 이름은 가짜입니다.

> 용의자 기기의 `D:\sample\tools\models` 폴더에 얼굴 교체용 모델 파일 이름과 같은 `inswapper_128_fp16.onnx` 가 있습니다. 같은 기기의 설정 파일 `target_path` 에는 `D:\sample\target_clip.mp4` 가 적혀 있습니다. 이 기록은 얼굴 합성 도구를 설치하고 해당 파일을 대상으로 설정한 적이 있음을 보여 주지만, 문제의 영상을 이 도구로 만들었는지는 결과물 비교로 따로 확인해야 합니다.

> 문제의 이미지에서 C2PA 출처 정보와 생성 도구 메타데이터가 확인되지 않습니다. 이는 AI 로 만들지 않았다는 뜻이 아니고, 이 파일만으로는 생성 방법을 판단할 수 없다는 뜻입니다.

## 함께 볼 페이지

- [AI로 피싱·사기 문구를 만들었나](phishing.md)
- [AI로 악성 코드를 만들었나](malware-development.md)
- [이 글·이미지는 AI가 만들었나](../attribution/ai-generated.md)
- [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)
- [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)
- [AI 관련 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)

## 참고 문헌

1. Google Cloud Blog(GTIG), "GTIG AI Threat Tracker: Advances in Threat Actor Usage of AI Tools" (2025-11-06) — https://cloud.google.com/blog/topics/threat-intelligence/threat-actor-usage-of-ai-tools
2. MITRE ATT&CK, T1588.007 Obtain Capabilities: Artificial Intelligence (v1.1, 수정 2026-05-12) — https://attack.mitre.org/techniques/T1588/007/
3. GitHub facefusion/facefusion, `facefusion.ini` (master) — https://raw.githubusercontent.com/facefusion/facefusion/master/facefusion.ini
4. GitHub hacksider/Deep-Live-Cam README — https://github.com/hacksider/Deep-Live-Cam
