---
title: "Midjourney와 이미지 생성 서비스"
parent: "아티팩트 · 생성·음성·회의록"
nav_order: 440
---

# Midjourney와 이미지 생성 서비스 (Midjourney·Image Generation)

서버에서 그림을 만드는 서비스는 프롬프트와 생성 원본을 서버에 두고 기기에는 내려받은 이미지 파일만 남기는 반면, PC 에서 돌리는 도구는 프롬프트·시드 같은 생성 정보를 이미지 파일 안에 함께 적어 둡니다.

로컬 도구의 저장 방식은 판마다 바뀔 수 있으니 분석 대상 기기에 설치된 도구의 판과 맞춰 봅니다.

## 무엇을 기록하나 · 왜 생기나

이미지 생성 서비스는 그림을 어디서 만드느냐에 따라 두 종류로 나뉩니다. Midjourney·ChatGPT·Gemini 처럼 서버에서 만드는 서비스는 프롬프트와 생성한 이미지를 계정에 딸린 서버 기록으로 두고, 기기에는 사용자가 내려받거나 복사한 이미지 파일과 브라우저·앱 흔적이 남습니다. ComfyUI·AUTOMATIC1111 처럼 PC 에서 모델을 돌리는 도구는 만든 그림을 디스크에 바로 저장하고, 생성 정보를 이미지 파일 안에 넣습니다.

그래서 출처를 모르는 이미지 파일 하나를 받았을 때 파일 안의 생성 정보가 첫 단서가 되고, 서버에서 만든 이미지라면 원본과 프롬프트를 찾으러 계정 쪽으로 가야 합니다. 데이터가 서버와 기기에 어떻게 나뉘는지는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에, 프롬프트·첨부·생성물을 가르는 기준은 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)에 있습니다.

Gemini 앱에서는 사용자가 올린 사진 같은 공유 내용도 활동 기록 저장(Keep Activity)이 켜져 있으면 대화와 함께 활동 기록에 저장됩니다("Your chats and what you share with Gemini (like files, videos, screens, and photos) will be saved in your Activity.")[3]. 활동 기록을 얼마나 보관하는지는 [음성 대화 기능](voice-mode.md)과 [Gemini](../chat-services/gemini/index.md) 페이지에서 다룹니다.

## 위치와 버전별 차이

| 종류 | 원본이 있는 곳 | 기기에 남을 수 있는 것 | 근거·확인 방법 |
|---|---|---|---|
| Midjourney (웹 midjourney.com·Discord) | 서버 | 내려받은 이미지, 브라우저 기록 | 공개 기본값·Stealth 모드 조건·보관 기간은 공식 도움말로, 파일 안의 프롬프트·작업 ID 는 받은 파일로 확인 |
| ChatGPT 이미지 생성 | 서버 | 내려받은 이미지, 브라우저·앱 기록 | C2PA(Content Credentials) 정보가 있는지와 그 항목은 받은 파일로 확인 |
| Gemini 앱 | 서버(활동 기록) | 내려받은 이미지 | 올린 사진은 활동 기록 저장이 켜져 있을 때 활동 기록에 저장[3] |
| Grok Imagine (Android 앱 `ai.x.grok`) | 서버 | 재생하면서 쌓인 영상 캐시와 그 색인 DB | ALEAPP 분석기[4], Grok 1.0.71(2025-11-11)로 시험 |
| ComfyUI | PC 의 출력 폴더 | PNG 파일과 그 안의 텍스트 청크 | 소스 코드로 확인[1] |
| AUTOMATIC1111 | PC 의 출력 폴더 | PNG·JPEG·WebP·AVIF·GIF 파일과 그 안의 생성 정보 | 소스 코드로 확인[2] |

서버에서 만든 이미지를 웹에서 내려받으면 파일은 브라우저가 정한 다운로드 폴더에 들어가고, 다운로드 기록은 브라우저 쪽에 남습니다. Windows 의 크롬 계열은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html), macOS 는 [사파리](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/browsers/safari/index.html)와 [격리 속성과 다운로드 기록](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/filesystem/quarantine/index.html)에서 찾는 방법을 다룹니다. Android·iOS 앱에서 저장한 이미지는 기기의 사진 보관함과 앱 폴더에서 파일 시각으로 찾아 확인합니다.

Android 의 Grok 앱은 Grok Imagine 영상을 재생하면서 캐시를 남기고, ALEAPP 은 캐시 색인에 적힌 원래 URL 이 `https://assets.grok.com/users/` 로 시작하면 사용자 생성 영상(User Generated), 그 밖은 공개 영상(Public)으로 나눕니다[4]. 이 분석기는 Grok 1.0.71(2025-11-11)로 시험했고 지금 판과 구조가 다를 수 있습니다[4]. 캐시 경로·표·시각 해석은 [그 밖의 서비스 (DeepSeek·Grok 등)](../chat-services/other-services.md)에 있습니다.

ComfyUI 는 저장 노드(SaveImage)의 결과를 `folder_paths.get_output_directory()` 가 돌려주는 출력 폴더에, 미리보기 노드(PreviewImage)의 결과를 `folder_paths.get_temp_directory()` 가 돌려주는 임시 폴더에 저장합니다[1]. 두 폴더와 AUTOMATIC1111 의 출력 폴더는 실행 인자와 설정에 따라 달라질 수 있어서, 분석 대상 기기의 설정과 실제 폴더를 함께 봅니다. 로컬 도구의 설치 폴더와 설정은 [로컬 이미지 생성 도구](../local-ai/image-gen-local.md)에서 다룹니다.

## 구조

### 이미지 파일 안의 생성 정보

| 도구 | 파일 형식 | 들어가는 곳 | 키 | 담기는 것 |
|---|---|---|---|---|
| ComfyUI | PNG | 텍스트 청크 | `prompt` | 실행한 노드 그래프를 JSON 문자열로 바꾼 것[1] |
| ComfyUI | PNG | 텍스트 청크 | `extra_pnginfo` 의 각 키 | 키마다 값을 JSON 문자열로 바꾼 것[1] |
| AUTOMATIC1111 | PNG | 텍스트 청크 | `parameters` | 프롬프트·시드·단계 수 등 생성 정보[2] |
| AUTOMATIC1111 | JPEG·WebP·AVIF | EXIF UserComment | (키 없음, unicode 인코딩) | PNG 의 `parameters` 와 같은 생성 정보[2] |
| AUTOMATIC1111 | GIF | GIF 주석 | `comment` | 같은 생성 정보[2] |

ComfyUI 는 `metadata.add_text("prompt", json.dumps(prompt))` 로 노드 그래프를 넣고, `extra_pnginfo` 에 들어온 키도 하나씩 같은 방법으로 넣습니다[1]. `extra_pnginfo` 에 어떤 키가 들어오는지는 `nodes.py` 가 정하지 않아서, 실제 파일에서 청크 키 목록을 먼저 봅니다. `prompt` 값은 사람이 입력한 문장 하나가 아니라 노드 그래프 전체라서, 프롬프트 문장은 그래프 안 어느 노드의 입력값으로 들어 있고 JSON 을 풀어 노드를 따라가야 보입니다.

AUTOMATIC1111 의 `read_info_from_image()` 는 PNG 의 `parameters`, EXIF UserComment, GIF 의 `comment` 순서로 생성 정보를 찾습니다[2]. 분석할 때도 이 세 곳을 차례로 보면 이 도구가 남긴 정보를 빠뜨리지 않습니다.

### 파일 이름

ComfyUI 의 저장 파일 이름은 기본 접두사 `ComfyUI` 뒤에 다섯 자리 번호를 붙인 모양이라 첫 파일이 `ComfyUI_00001_.png` 가 되고, 미리보기 파일은 접두사 뒤에 `_temp_` 와 임의 글자 다섯 개를 더 붙여 임시 폴더에 둡니다[1]. 번호가 이어지는 파일 묶음은 한 출력 폴더에서 차례로 만든 결과일 가능성이 높고, 번호가 빈 자리는 지운 파일을 찾는 단서가 될 수 있지만, 접두사를 바꿔 저장했을 수도 있어서 빈 번호만으로 삭제를 단정하지 않습니다.

AUTOMATIC1111 의 파일 이름 패턴 기본값은 기본 폴더에 저장할 때 `[seed]-[prompt_spaces]`, 하위 폴더에 나눠 저장(save_to_dirs)할 때 `[seed]` 이고, 번호를 붙이는 설정이면 이 앞에 다섯 자리 번호와 `-` 가 붙습니다[2]. 그래서 이미지 안의 생성 정보를 지웠더라도 파일 이름에 시드와 프롬프트 앞부분이 남아 있을 수 있습니다.

```
ComfyUI_{5자리 번호}_.png          ComfyUI 저장 파일(기본 접두사)
{접두사}_temp_{임의 5글자}...      ComfyUI 미리보기 파일(임시 폴더)
{번호}-[seed]-[prompt_spaces]      AUTOMATIC1111 기본 폴더 저장 패턴
{번호}-[seed]                      AUTOMATIC1111 하위 폴더 저장 패턴
```

## 증거로서 의미

**증명하는 것.** 파일 안에 `parameters` 나 `prompt` 텍스트 청크가 있으면 그 파일은 이런 정보를 넣는 도구로 저장했을 가능성이 높고, 청크 안의 프롬프트·시드·설정값은 어떤 입력으로 그림을 만들었는지 보여 줍니다. 서버 서비스에서는 계정의 생성 기록이 프롬프트와 결과를 잇는 원본이고, 기기의 다운로드 기록은 그 계정에서 만든 이미지를 이 기기로 가져왔다는 흔적입니다. 보고서에는 "이 파일의 PNG 텍스트 청크 `parameters` 에 이런 프롬프트와 시드가 적혀 있다" 처럼 파일에서 확인되는 만큼만 씁니다.

**증명하지 못하는 것.** 생성 정보는 누가 만들었는지, 이 PC 에서 만들었는지 알려 주지 않고, 다른 곳에서 만든 파일을 내려받거나 복사했을 수도 있습니다. 텍스트 청크와 EXIF 는 일반 편집 도구로 넣고 뺄 수 있어서 적힌 프롬프트가 실제 생성 입력과 같다는 보장도 없습니다. 반대로 생성 정보가 없다고 생성 이미지가 아니라고 볼 수도 없는데, ComfyUI 는 `args.disable_metadata` 가 켜지면 메타데이터를 넣지 않고[1], 화면 캡처처럼 픽셀만 다시 저장한 파일에는 원래 파일의 청크가 따라가지 않습니다. 이미지가 AI 로 만든 것인지 판단하는 일의 한계는 [AI가 만든 글·이미지 판별의 한계](../../03-techniques/analysis/detection-limits.md)에 있습니다.

## 시각 해석

이미지 파일의 파일 시스템 시각은 그 파일이 이 디스크에 저장되거나 복사된 때를 가리키고, 로컬 도구가 바로 저장한 파일이면 생성 직후 시각과 가깝습니다. 내려받은 파일의 시각은 다운로드 시각이라 서버에서 만든 시각과 다르고, 서버의 생성 시각은 계정 기록에만 있습니다. 생성 정보 텍스트에 시각이 있는지는 실제 파일의 청크 내용을 보고 판단합니다. Grok 영상 캐시의 두 시각은 뜻이 서로 달라서 [그 밖의 서비스 (DeepSeek·Grok 등)](../chat-services/other-services.md)의 시각 해석을 따릅니다. 여러 출처의 시각을 시간순으로 합치는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

서버 서비스의 원본은 기기에 없어서, 프롬프트와 생성 목록이 필요하면 [계정 데이터 내보내기로 수집](../../03-techniques/acquisition/export-collection.md)하거나 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)을 거쳐야 합니다. 생성 결과를 다른 사용자에게 보여 주는 서비스라면 다른 계정에서도 같은 이미지를 받을 수 있어서, 이미지를 가진 사람을 만든 사람으로 볼 수 없습니다. Midjourney 의 공개 기본값과 요금제별 조건은 사건 당시의 공식 도움말로 확인합니다. Grok 영상 캐시도 마찬가지로, 캐시에 있다는 사실만으로 그 기기에서 만들었다고 볼 수 없습니다.

C2PA 정보나 워터마크는 로컬 도구의 텍스트 청크와 다른 방식이라 따로 봐야 하고, 이 정보가 어떻게 들어가고 어떻게 사라지는지는 [AI 생성물의 출처 정보](../../01-foundations/concepts/c2pa-provenance.md)에서 다룹니다. 서버 서비스에서 받은 이미지에 C2PA 정보가 있는지는 받은 파일에서 직접 확인합니다.

AUTOMATIC1111 의 파일 이름 패턴은 사용자가 바꿀 수 있어서 기본값과 다른 이름이 나와도 이상한 일이 아니고, 시드 숫자만으로 같은 도구에서 만든 이미지라고 단정할 수도 없습니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래는 PNG 명세의 청크 구조에 따라 만든 예시이고, 실제 파일에서 뜬 바이트가 아닙니다. 키 `parameters` 와 본문 `red toy car, Seed: 1234` 도 만든 값입니다. 오프셋은 파일 처음이 아니라 청크 시작부터 셉니다.

```
만든 예시(PNG 명세로 만든 tEXt 청크)
00000000  00 00 00 22 74 45 58 74 70 61 72 61 6D 65 74 65   ..."tEXtparamete
00000010  72 73 00 72 65 64 20 74 6F 79 20 63 61 72 2C 20   rs.red toy car,
00000020  53 65 65 64 3A 20 31 32 33 34 FD 46 B7 AE         Seed: 1234.F..
```

처음 4바이트 `00 00 00 22` 는 빅엔디언 길이 34이고, 키 10바이트와 구분용 `00` 1바이트, 본문 23바이트를 더한 값입니다. 그다음 4바이트 `74 45 58 74` 가 청크 종류 `tEXt`, 이어서 키와 `00`, 본문이 오고, 마지막 4바이트 `FD 46 B7 AE` 는 청크 종류부터 본문까지로 계산한 CRC 입니다. PNG 파일은 `89 50 4E 47 0D 0A 1A 0A` 로 시작하고 그 뒤에 청크가 이어지며, 헥스 편집기에서 `parameters`, `prompt` 같은 키를 ASCII 로 찾으면 청크 자리로 바로 갈 수 있습니다. 텍스트 청크에는 압축한 `zTXt` 와 UTF-8 을 쓰는 `iTXt` 도 있어서, 실제 파일에서 어느 종류로 들어갔는지 먼저 봅니다. 압축한 청크는 ASCII 검색에 본문이 걸리지 않습니다.

**공개 도구로 한 번.** 사본에서 ExifTool 로 모든 텍스트 청크와 EXIF 를 뽑습니다. 파일 이름은 만든 예시입니다.

```sh
exiftool -a -G1 -s ComfyUI_00001_.png
exiftool -a -G1 -s -UserComment made-example.jpg
```

ComfyUI 의 `prompt` 값은 JSON 문자열이라 값만 떼어 jq 로 펼치면 노드별 입력을 읽을 수 있습니다. 결과에 청크가 하나도 없으면 메타데이터를 끈 채 저장했거나, 다른 도구에서 다시 저장했거나, 애초에 이런 정보를 넣지 않는 서비스에서 받은 파일일 수 있습니다.

## 교차 검증

로컬 도구로 만들었다면 [로컬 이미지 생성 도구](../local-ai/image-gen-local.md)의 출력 폴더와 설정, [로컬 모델 파일](../local-ai/model-files.md)에 남은 모델 파일을 함께 보고, 서버 서비스라면 브라우저 방문·다운로드 기록과 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)으로 그 시간대에 서비스에 접속했는지 맞춰 봅니다. AI 개발 도구가 이미지를 다룬 흔적은 도구 기록에 따로 남을 수 있는데, Claude Code 세션 기록의 도구 결과에는 `toolUseResult.isImage` 라는 참·거짓 키가 있었습니다. 이 키의 뜻은 공식 문서에 설명이 없어서 같은 줄의 도구 결과 내용과 맞춰 보고 판단하고, 기록 구조는 [Claude Code](../dev-agents/claude-code/index.md) 페이지에 있습니다. 합성 이미지 사건을 처음부터 따라가는 흐름은 [딥페이크·합성 이미지를 만들었나](../../04-scenarios/misuse/deepfake.md)와 [이 글·이미지는 AI가 만들었나](../../04-scenarios/attribution/ai-generated.md)에 있습니다.

## 실습

시험용 가상 머신에서 가짜 프롬프트로 이미지를 만들어 풀어 봅니다.

1. ComfyUI 로 같은 그림을 메타데이터를 켠 채 한 번, `disable_metadata` 를 켠 채 한 번 저장하고 ExifTool 결과를 비교합니다.
2. AUTOMATIC1111 에서 PNG 와 JPEG 로 각각 저장하고, 생성 정보가 텍스트 청크와 EXIF UserComment 중 어디에 들어갔는지 확인합니다.
3. 생성 이미지를 화면 캡처로 다시 저장하고, 원래 파일의 청크가 남는지 봅니다.
4. 서버 서비스에서 만든 이미지를 내려받아 파일 안에 프롬프트·작업 ID·C2PA 정보 같은 메타데이터가 있는지 확인합니다.

## 참고 문헌

1. ComfyUI `nodes.py` (SaveImage·PreviewImage) — https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/nodes.py
2. AUTOMATIC1111 stable-diffusion-webui `modules/images.py` — https://raw.githubusercontent.com/AUTOMATIC1111/stable-diffusion-webui/master/modules/images.py
3. Gemini Apps Privacy Hub (Google 도움말, 2026-09-24 갱신) — https://support.google.com/gemini/answer/13594961?hl=en
4. ALEAPP, Grok 분석기(Damien Attoe, Grok 1.0.71 시험, 2025-11-14 작성·2026-08-01 갱신) — https://github.com/abrignoni/ALEAPP , `scripts/artifacts/Grok.py`
