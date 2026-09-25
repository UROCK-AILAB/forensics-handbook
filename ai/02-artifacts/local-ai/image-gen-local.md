---
title: "로컬 이미지 생성 도구"
parent: "아티팩트 · 로컬 AI"
nav_order: 750
---

# 로컬 이미지 생성 도구 (Stable Diffusion WebUI·ComfyUI)

Stable Diffusion WebUI 와 ComfyUI 는 이미지 생성 모델을 자기 컴퓨터에서 돌리는 도구이고, 둘 다 기본 설정에서는 만든 이미지 파일 안에 프롬프트와 시드 같은 생성 설정을 글자로 넣어 저장합니다.

> 확인 범위: 공식 문서(AUTOMATIC1111 위키 "Features", ComfyUI README, 둘 다 2026-09-25 열람)와 소스 코드 기준입니다. Stable Diffusion WebUI 는 AUTOMATIC1111 저장소 master 브랜치(마지막 커밋 2024-07-27, 최신 릴리스 v1.10.1), ComfyUI 는 master 브랜치(2026-09-25 커밋, 최신 릴리스 v0.37.0)의 코드 기준입니다. 기기에서 관찰한 값이 아니므로 검체의 판이 다르면 폴더 이름과 설정 이름이 다를 수 있고, 검체의 설정 파일로 먼저 확인합니다.

## 무엇을 기록하나 · 왜 생기나

두 도구는 로컬에서 돌기 때문에 생성 기록이 서비스 회사 서버가 아니라 도구를 깐 폴더에 남습니다. 이미지에 넣어 둔 설정은 도구에서 다시 불러올 수 있게 하려는 기능이고, 조사에서는 이 기능 덕에 이미지 파일 하나로 어떤 프롬프트와 모델로 만들었는지 따라갈 수 있습니다.

Stable Diffusion WebUI(이하 WebUI)는 생성 설정을 한 덩어리 글자로 만들고, 코드와 위키는 이것을 "infotext" 라고 부릅니다. PNG 로 저장하면 이 글자가 `parameters` 라는 키의 텍스트 조각(text chunk)에 들어가고, 화면의 "PNG info" 기능은 이 조각을 읽어 보여 줍니다[1][3]. 사용자가 결과 화면의 Save 버튼을 누르면 이미지를 따로 정한 폴더에 한 번 더 저장하고, 그 폴더의 `log.csv` 에 한 줄을 덧붙입니다[1][4].

ComfyUI 는 모델·프롬프트·처리 단계를 노드로 이은 그래프(워크플로)로 이미지를 만듭니다. 저장 노드가 실행한 그래프를 `prompt` 키에, 화면의 워크플로를 `workflow` 키에 JSON 으로 넣고, 문서는 이 PNG 를 다시 불러오면 워크플로 전체가 시드까지 되살아난다고 적었습니다[2][6][7].

ComfyUI 는 기본으로 오프라인에서 돌고, 사용자가 요청하지 않으면 핵심 부분이 아무것도 내려받지 않는다고 문서에 적혀 있습니다[2]. 다만 유료 Comfy API 노드를 쓰는 워크플로라면 프롬프트가 외부 서비스로 나갈 수 있습니다. 실행 옵션 `--disable-api-nodes` 는 도움말에 "API 노드를 모두 불러오지 않고, 프런트엔드가 인터넷과 통신하지 못하게 한다" 고 적혀 있습니다[8]. 화면 서버는 기본으로 `127.0.0.1` 의 8188 포트에서 듣고, `--listen` 을 주면 다른 주소에서도 접속할 수 있습니다[8]. 온라인 이미지 생성 서비스는 [Midjourney와 이미지 생성 서비스](../generative-media/image-generation.md)에서 다룹니다.

### LLM 채팅 앱이 만들거나 받은 이미지

이미지는 로컬 확산 모델 도구에서만 나오지 않습니다. LangurTrace 논문은 이미지 생성에 DALL·E 3 를 썼고[5 §4.1], Chatbox 1.11.8(2025-04-05 출시)에서는 생성을 클라우드에서 해도 결과 사본이 `%AppData%/xyz.chatboxapp.app/chatbox-blobs/` 에 남았습니다[5 §4.5, 부록 A]. 논문이 시험한 판 기준이므로 지금 판에서는 검체에서 이 폴더가 있는지 먼저 봅니다. 사용자가 올린 이미지도 같은 폴더에 이름만 달리해 남고, 앱 화면에서 지운 뒤에도 올린 파일과 생성 파일 모두 50개 중 50개를 되살렸습니다[5 §4.5, 표 8]. 논문은 이런 생성 파일이 CSAM 처럼 불법 이미지를 만들거나 퍼뜨린 사건에서 직접 증거가 될 수 있다고 봅니다[5 초록, §4.3, §6.1]. 파일 이름 규칙과 인코딩을 푸는 방법은 [Chatbox](chatbox.md)에 있고, 사용자가 올린 파일은 [Msty](msty.md)의 `attachments` 폴더와 [LM Studio](lm-studio.md)의 `user-files` 폴더에도 남습니다.

## 위치와 버전별 차이

### Stable Diffusion WebUI

WebUI 는 사용자가 저장소를 받은 폴더에서 돌리는 방식이라 고정 설치 경로가 없습니다. 사용자 데이터는 실행 옵션 `--data-dir` 이 가리키는 폴더에 쌓이고, 이 옵션을 주지 않으면 설치 폴더가 그 자리입니다[9]. 아래 경로는 모두 그 폴더 기준입니다.

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `outputs/txt2img-images`, `outputs/img2img-images`, `outputs/extras-images` | 생성 종류별 결과 이미지 | [4] |
| `outputs/txt2img-grids`, `outputs/img2img-grids` | 여러 장을 한 장으로 붙인 격자 이미지 | [4] |
| `outputs/init-images` | img2img 에 넣은 입력 이미지. "Save init images when using img2img" 설정을 켰을 때만 저장 | [4][10] |
| `log/images` | Save 버튼으로 저장한 이미지 | [4] |
| `log/images/log.csv` | Save 버튼을 누를 때마다 덧붙는 기록 | [4] |
| `models` | 모델 폴더. `--models-dir` 로 바꿀 수 있음 | [9] |
| `styles.csv` | 저장해 둔 프롬프트 스타일 | [1] |
| `config.json` | 일반 설정. 위 폴더 경로와 파일 이름 규칙도 여기에 들어감 | [1] |
| `ui-config.json` | 화면 기본값(기본값·슬라이더 범위·체크박스) | [1] |

출력 폴더는 설정에서 바꿀 수 있으므로 `config.json` 의 `outdir_txt2img_samples`, `outdir_save` 같은 값을 먼저 읽고 실제 경로를 정합니다[4]. "Save images to a subdirectory" 설정(`save_to_dirs`)이 기본으로 켜져 있어서, 결과 이미지는 출력 폴더 아래 `[date]` 규칙의 하위 폴더, 즉 `2026-09-25` 같은 날짜 폴더에 들어갑니다[4][3].

파일 이름은 "Images filename pattern" 설정(`samples_filename_pattern`)이 정합니다. 이 값이 비어 있으면, 하위 폴더를 쓰는 기본 상태에서는 `[seed]`, 하위 폴더를 끄면 `[seed]-[prompt_spaces]` 를 씁니다[3]. 위키는 기본값을 `[seed]-[prompt_spaces]` 로 적었으므로 두 설명을 함께 알아 둡니다. "Add number to filename when saving" 설정이 기본으로 켜져 있어서 파일 이름 맨 앞에 다섯 자리 번호가 붙고, 기본 상태의 이름은 `00012-1234567890.png` 꼴이 됩니다(만든 예시)[3][4]. 쓸 수 있는 태그에는 `[seed]`, `[steps]`, `[cfg]`, `[width]`, `[height]`, `[sampler]`, `[model_name]`, `[prompt]` 가 있어서, 설정에 따라 파일 이름에 시드·단계 수·크기·모델 이름·프롬프트가 들어갑니다[1].

### ComfyUI

ComfyUI 는 Windows·macOS 데스크톱 앱과 Windows 휴대용 판(NVIDIA·AMD·Intel GPU 용)으로 배포합니다[2]. 아래는 저장소 폴더 기준이고, `--base-directory` 를 주면 이 폴더들이 그 아래로 옮겨 갑니다[8]. 데스크톱 앱이 데이터를 어디에 두는지는 공개된 분석 자료가 없어서, 검체에서 아래 폴더 이름으로 찾아 확인합니다.

| 경로 | 담긴 것 | 바꾸는 옵션 |
|---|---|---|
| `output` | 저장 노드로 만든 이미지 | `--output-directory` |
| `input` | 입력으로 넣은 이미지 | `--input-directory` |
| `temp` | 미리 보기 노드가 만든 이미지 | `--temp-directory` |
| `user` | 사용자별 데이터. 설정은 `user/default/comfy.settings.json` | `--user-directory` |
| `user/comfyui.db` | 자산 관리용 SQLite 데이터베이스 | `--database-url` |
| `models/checkpoints`, `models/vae` | 체크포인트·VAE 모델 | `--models-directory` |
| `custom_nodes` | 추가로 깐 노드 | |
| `extra_model_paths.yaml` | ComfyUI 폴더 밖의 모델 위치(저장소 맨 위에 예시 파일) | |

폴더 기본값과 옵션은 `folder_paths.py` 와 `comfy/cli_args.py`, 설정 파일 이름은 `app/app_settings.py` 에 있습니다[8][11]. 모델과 추가 노드 폴더는 README 에 나옵니다[2].

저장 노드(SaveImage)는 파일 이름을 `ComfyUI_00001_.png` 꼴로 짓습니다. 앞부분은 노드의 `filename_prefix` 값이고 기본값이 `ComfyUI` 이며, 뒤에 다섯 자리 번호와 밑줄이 붙습니다[6]. `filename_prefix` 에 `%year%`, `%month%`, `%day%`, `%hour%` 같은 변수나 `/` 를 넣으면 날짜 폴더나 하위 폴더를 만들 수 있습니다[11]. 미리 보기 노드(PreviewImage)는 `temp` 폴더에 `ComfyUI_temp_` 와 영문 다섯 자가 붙은 이름으로 저장합니다[6]. 시작할 때 `temp` 폴더를 통째로 지우는 코드가 있으므로(자산 관리 기능이 꺼진 경우)[12], 미리 보기 이미지는 다음 실행 전까지만 남는다고 보고 찾습니다.

`extra_model_paths.yaml` 이 있으면 모델을 ComfyUI 폴더 밖, 예를 들어 WebUI 모델 폴더에 두고 함께 썼을 수 있어서 이 파일에 적힌 경로를 따라가 봅니다[2]. 출력은 16비트 PNG, 32비트 EXR, 10비트 AVIF 도 지원하고[2], 이 형식에 들어가는 메타데이터는 아래 "구조" 에 적습니다.

## 구조

### WebUI 의 infotext

infotext 는 첫 줄에 프롬프트, 다음 줄에 `Negative prompt:` 로 시작하는 제외 프롬프트, 마지막 줄에 `이름: 값` 을 쉼표로 이은 생성 설정이 오는 짜임입니다[13]. 마지막 줄에 들어가는 이름은 아래와 같고, 값이 없는 항목은 빠집니다.

| 항목 | 뜻 | 들어가는 조건 |
|---|---|---|
| `Steps`, `Sampler`, `Schedule type`, `CFG scale`, `Seed`, `Size` | 기본 생성 설정 | 늘 |
| `Model hash`, `Model` | 쓴 체크포인트의 해시와 이름 | 설정 두 개가 기본으로 켜짐 |
| `VAE hash`, `VAE` | 쓴 VAE | 설정 두 개가 기본으로 켜짐 |
| `Denoising strength` | img2img 에서 입력을 얼마나 바꿨는지 | img2img 등 |
| `Init image hash` | 입력 이미지의 MD5 | "Save init images" 를 켰을 때 |
| `Version` | 프로그램 버전 | 기본으로 켜짐 |
| `User` | 로그인한 사용자 이름 | 인증을 쓰고 해당 설정을 켰을 때(기본 꺼짐) |

`Init image hash` 는 파일 바이트가 아니라 이미지의 픽셀 데이터로 구한 MD5 이고, `outputs/init-images` 에 저장한 입력 이미지의 파일 이름으로도 쓰입니다[13]. 그래서 입력 이미지 파일을 해시 도구로 구한 MD5 와 이 값은 같지 않습니다.

infotext 가 파일에 들어가는 방식은 저장 형식마다 다릅니다[3].

| 저장 형식 | 들어가는 곳 |
|---|---|
| PNG | 텍스트 조각, 키 `parameters` |
| JPEG, WebP, AVIF | EXIF 의 UserComment(유니코드) |
| GIF | 주석(comment) |

PNG 텍스트 조각은 Pillow 라이브러리가 씁니다. 값이 Latin-1 로만 된 글자면 `tEXt` 조각, 한글처럼 Latin-1 밖의 글자가 섞이면 압축하지 않은 `iTXt` 조각(UTF-8)으로 들어갑니다[14]. "Write infotext to metadata of the generated image" 설정(`enable_pnginfo`)은 기본으로 켜져 있고, 끄면 어느 형식에도 infotext 를 넣지 않습니다[3][10]. "Create a text file with infotext next to every generated image" 설정(`save_txt`)을 켜면 이미지 옆에 같은 내용의 `.txt` 파일이 생깁니다(기본 꺼짐)[10].

### WebUI 의 log.csv

`log.csv` 는 UTF-8 CSV 이고, 첫 줄의 열 이름은 아래 11개입니다[4].

```
prompt,seed,width,height,sampler,cfgs,steps,filename,negative_prompt,sd_model_name,sd_model_hash
```

Save 버튼을 한 번 누를 때 한 줄이 붙고, 여러 장을 한꺼번에 저장해도 첫 이미지의 프롬프트·시드·파일 이름만 적습니다[4]. "When using 'Save' button, only save a single selected image" 설정이 기본으로 켜져 있어서 보통은 한 번에 한 장을 저장합니다[10]. "Write log.csv when saving images using 'Save' button" 설정(`save_write_log_csv`)을 끄면 줄을 쓰지 않습니다[10]. 시각 열은 없습니다.

### ComfyUI 의 메타데이터

`prompt` 값은 노드 번호를 키로 하고 노드마다 `class_type`(노드 종류)과 `inputs`(입력값)를 담은 JSON 입니다[15]. 모델 파일 이름과 프롬프트 글자는 해당 노드의 `inputs` 안에 있습니다. `workflow` 값은 화면에 그려진 워크플로 전체이고, ComfyUI 에 불러오면 이 값으로 화면을 되살립니다[2].

| 저장 형식 | 들어가는 곳 |
|---|---|
| PNG | `tEXt` 조각, 키 `prompt`, `workflow` |
| EXR | 헤더의 string 속성, 이름 `prompt`, `workflow` |
| AVIF | EXIF 태그 0x0110 에 `prompt:` 로 시작하는 글자, 0x010F 부터 거꾸로 `workflow:` 등 나머지 키 |

PNG 는 SaveImage 노드[6], EXR·AVIF 는 `comfy_extras/nodes_images.py` 의 저장 코드[7] 기준입니다. JSON 을 Python 의 `json.dumps` 기본값으로 만들기 때문에 한글 같은 글자는 `\ud55c`(한) 처럼 이스케이프한 형태로 들어갑니다[6]. 실행 옵션 `--disable-metadata` 를 주면 저장 노드가 메타데이터를 넣지 않습니다[6][8].

모델 파일인 safetensors 의 구조는 [로컬 모델 파일](model-files.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 출력 폴더의 이미지에 생성 설정이 들어 있으면, 그 설정이 적힌 이미지가 그 폴더에 저장되어 있었다고 쓸 수 있습니다. WebUI 의 `log.csv` 에 줄이 있으면 사용자가 Save 버튼으로 이미지를 저장한 기록이 있다고 쓸 수 있고, 이미지를 나중에 지웠어도 CSV 줄은 남습니다. `filename` 열의 파일이 저장 폴더에 없으면 그 이미지를 지웠거나 옮겼다는 단서가 됩니다. 메타데이터의 `Model hash`·`Model` 이나 ComfyUI `prompt` 의 모델 파일 이름은 디스크의 모델 파일과 맞춰 볼 수 있습니다. ComfyUI 의 `input` 폴더와 WebUI 의 `outputs/init-images` 폴더에 있는 파일은 입력으로 넣은 이미지라서, [딥페이크·합성 이미지를 만들었나](../../04-scenarios/misuse/deepfake.md) 같은 조사에서 원본 사진을 찾는 출발점이 됩니다.

**증명하지 못하는 것.** 메타데이터는 글자라서 누구든 고치거나 지울 수 있습니다. 메타데이터의 프롬프트로 그 이미지를 만들었다고 쓰려면 `log.csv`, 출력 폴더 위치, 파일 번호, 파일 시각과 맞는지 확인합니다. `log.csv` 는 Save 버튼을 누른 경우만 적으므로 줄 수를 생성 횟수로 읽지 않습니다. 메타데이터가 없는 이미지를 사람이 만든 이미지라고 보지도 않는데, 두 도구 모두 메타데이터를 끄는 설정이 있기 때문입니다. 이미지만 보고 AI 로 만들었는지 가르는 일의 한계는 [AI가 만든 글·이미지 판별의 한계](../../03-techniques/analysis/detection-limits.md)에서 다룹니다. 다른 기기에서 만든 이미지를 복사해 넣었을 수도 있어서, 출력 폴더에 있다는 사실만으로 그 PC 에서 만들었다고 단정하지 않습니다.

## 시각 해석

infotext, `log.csv`, ComfyUI 메타데이터에는 생성 시각이 들어가지 않습니다[4][6][13]. 시각 단서는 세 가지입니다.

- **날짜 폴더.** WebUI 의 `[date]` 폴더 이름과 ComfyUI 의 `%year%`·`%month%`·`%day%` 는 저장한 PC 의 현지 시각으로 만듭니다[3][11]. 폴더 이름의 날짜는 현지 날짜로 읽습니다.
- **파일 시각.** 도구가 파일을 저장한 때에 가깝고, 복사하거나 옮기면 바뀝니다. UTC 인지 현지 시각인지는 파일 시스템 규칙을 따릅니다.
- **파일 번호.** 두 도구 모두 새 파일 번호를 "그 폴더에 남아 있는 파일 가운데 가장 큰 번호 + 1" 로 정합니다[3][11]. 그래서 번호는 저장 순서를 보여 주고, 중간 번호가 비어 있으면 그 파일이 나중에 지워졌거나 옮겨졌다고 볼 수 있습니다. 반대로 가장 끝 번호 파일을 지우면 다음 저장 때 그 번호를 다시 쓰므로, 끝 번호가 이어진다고 지운 파일이 없다고 단정하지 않습니다.

## 함정과 한계

- **설치 위치.** 두 도구 모두 사용자가 고른 폴더에 깔고, 데이터 폴더를 실행 옵션으로 옮길 수 있습니다. `outputs`, `log/images`, `custom_nodes`, `styles.csv`, `comfy.settings.json` 같은 이름을 디스크 전체에서 찾아 설치 폴더를 먼저 찾고, 실행 바로 가기나 배치 파일에 적힌 옵션도 봅니다.
- **메타데이터가 빠진 이미지.** WebUI 의 `enable_pnginfo` 를 끄거나 ComfyUI 를 `--disable-metadata` 로 돌리면 처음부터 메타데이터가 없습니다. 설정을 확인한 다음에 파일을 다른 프로그램으로 다시 저장했을 가능성을 봅니다.
- **한글 검색.** WebUI 는 한글 프롬프트를 UTF-8 로, ComfyUI 는 `\uXXXX` 이스케이프로 넣습니다. 한글 낱말로 디스크를 검색할 때는 두 형태를 모두 검색어로 씁니다.
- **API 노드.** ComfyUI 워크플로에 API 노드가 있으면 프롬프트가 외부로 나갔을 수 있습니다. `prompt` 의 `class_type` 과 네트워크 기록을 함께 봅니다.
- **추가 노드.** `custom_nodes` 나 WebUI 확장에 깐 코드는 저마다 따로 파일을 쓰거나 통신할 수 있고, 메타데이터 형식을 바꿀 수도 있습니다.
- **워크플로 되살리기.** 이미지를 ComfyUI 에 불러오면 워크플로를 되살리지만, 원본 증거가 아니라 사본을 격리한 분석 환경에서 엽니다.
- **출처 정보와 다름.** 여기서 말하는 생성 설정은 도구가 편의로 넣는 글자이고, 서명으로 위조를 가리는 출처 정보와 다릅니다. 출처 정보는 [AI 생성물의 출처 정보](../../01-foundations/concepts/c2pa-provenance.md)에서 다룹니다.

## 직접 분석해 보기

**헥스로.** PNG 는 8바이트 서명 뒤에 조각이 이어지고, 조각마다 길이(4바이트, 빅 엔디언), 종류(4글자), 내용, CRC(4바이트)가 옵니다. `tEXt` 조각의 내용은 키, 0x00 한 바이트, 값 순서입니다. 아래는 WebUI 가 쓰는 `parameters` 조각을 흉내 낸 만든 예시입니다.

```
00 00 00 2F 74 45 58 74 70 61 72 61 6D 65 74 65  .../tEXtparamete
72 73 00 61 20 72 65 64 20 62 69 63 79 63 6C 65  rs.a red bicycle
0A 53 74 65 70 73 3A 20 32 30 2C 20 53 65 65 64  .Steps: 20, Seed
3A 20 31 32 33 34 35 63 3B D7 AF                 : 12345c;..
```

처음 4바이트 `00 00 00 2F` 는 내용 길이 47바이트이고, 이어서 `tEXt`, 키 `parameters`, 0x00, infotext 가 옵니다. 마지막 4바이트는 CRC 입니다. ComfyUI 는 이 조각들을 IHDR 조각 바로 뒤에 넣는 코드도 있으므로[7], 파일 앞부분에서 `tEXtprompt` 나 `tEXtworkflow` 글자를 먼저 찾아봅니다. 한글이 든 WebUI 이미지는 `iTXtparameters` 로 검색합니다.

**공개 도구로.** ExifTool 로 텍스트 조각과 EXIF 를 한꺼번에 뽑습니다. 파일 이름은 만든 예시입니다.

```
exiftool -a -G1 outputs/txt2img-images/2026-09-25/00012-1234567890.png
```

Python 과 Pillow 가 있는 분석 PC 라면 `Image.open(경로).text` 가 텍스트 조각을 키와 값의 사전으로 돌려줍니다[14]. `log.csv` 는 CSV 를 읽는 도구로 열어 `filename` 열의 파일이 저장 폴더에 있는지 맞춰 봅니다. WebUI 의 "PNG info" 화면이나 ComfyUI 에 이미지를 불러와 읽는 방법도 있지만, 이때도 원본이 아닌 사본을 씁니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [로컬 모델 파일](model-files.md) | 메타데이터에 적힌 모델이 실제로 디스크에 있었는지 |
| [Chatbox](chatbox.md) | LLM 채팅 앱이 만들거나 받은 이미지 |
| [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md) | 입력 이미지와 결과 이미지를 나눠 읽는 기준 |
| [딥페이크·합성 이미지를 만들었나](../../04-scenarios/misuse/deepfake.md) | 입력 이미지와 결과 이미지를 잇는 조사 흐름 |
| [이 글·이미지는 AI가 만들었나](../../04-scenarios/attribution/ai-generated.md) | 이미지 하나의 출처를 묻는 조사 흐름 |
| [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) | 모델 내려받기, API 노드 호출, 8188 포트 접속 |
| [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) | 출력 파일·CSV 줄을 다른 기록과 한 줄로 세우기 |

## 실습

두 도구가 든 공개 검체는 알려진 것이 없어서, 시험용 가상 머신에 직접 깔고 가짜 프롬프트 "a red bicycle on a sample street" 로 이미지를 몇 장 만든 다음 아래 질문을 풀어 봅니다. Chatbox 이미지는 LangurTrace 저장소(`github.com/jeongramon/LangurTrace`)의 `sample_dataset` 으로 풀어 볼 수 있습니다.

1. WebUI 에서 이미지 세 장을 Save 버튼으로 하나씩 저장한 뒤 가운데 한 장을 지우면, `log.csv` 와 파일 번호에는 무엇이 남습니까? 마지막 한 장을 지우고 새로 저장하면 번호는 어떻게 됩니까?
2. 한글 프롬프트로 만든 WebUI 이미지와 ComfyUI 이미지를 헥스로 열면, 한글이 각각 어떤 모양으로 보입니까?
3. ComfyUI 로 만든 PNG 를 메신저로 보냈다가 다시 받으면, `prompt`·`workflow` 조각이 남아 있습니까?
4. `extra_model_paths.yaml` 로 WebUI 모델 폴더를 가리키게 하면, ComfyUI 이미지의 `prompt` 에는 모델 이름이 어떻게 적힙니까?

## 참고 문헌

1. AUTOMATIC1111, stable-diffusion-webui Wiki, "Features", https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Features (2026-09-25 열람)
2. ComfyUI, GitHub README, https://github.com/comfyanonymous/ComfyUI (2026-09-25 열람)
3. AUTOMATIC1111/stable-diffusion-webui, `modules/images.py` (`save_image`, `save_image_with_geninfo`, `get_next_sequence_number`, `FilenameGenerator`), https://github.com/AUTOMATIC1111/stable-diffusion-webui (master, 2026-09-25 열람)
4. AUTOMATIC1111/stable-diffusion-webui, `modules/ui_common.py` (`save_files`)와 `modules/shared_options.py`(출력 폴더·파일 이름 설정), 같은 저장소
5. S. Jeong, S. Lee, J. Park, "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987 (DFRWS APAC 2025), https://doi.org/10.1016/j.fsidi.2025.301987. 시험 환경 Windows 11 Pro 24H2(26100.3775), Chatbox 1.11.8
6. comfyanonymous/ComfyUI, `nodes.py` (`SaveImage`, `PreviewImage`), https://github.com/comfyanonymous/ComfyUI (master, 2026-09-25 열람)
7. comfyanonymous/ComfyUI, `comfy_extras/nodes_images.py` (`inject_png_metadata`, `inject_exr_metadata`, `_avif_exif`), 같은 저장소
8. comfyanonymous/ComfyUI, `comfy/cli_args.py`, 같은 저장소
9. AUTOMATIC1111/stable-diffusion-webui, `modules/paths_internal.py`, 같은 저장소
10. AUTOMATIC1111/stable-diffusion-webui, `modules/shared_options.py` (`enable_pnginfo`, `save_txt`, `save_init_img`, `save_write_log_csv`, `save_selected_only`), 같은 저장소
11. comfyanonymous/ComfyUI, `folder_paths.py` (`get_save_image_path`), `app/app_settings.py`, `app/user_manager.py`, 같은 저장소
12. comfyanonymous/ComfyUI, `main.py`, `app/assets/lifecycle.py` (`cleanup_temp_filesystem`), 같은 저장소
13. AUTOMATIC1111/stable-diffusion-webui, `modules/processing.py` (`create_infotext`, img2img 입력 이미지 저장), 같은 저장소
14. python-pillow/Pillow, `src/PIL/PngImagePlugin.py` (`PngInfo.add_text`, `PngImageFile.text`), https://github.com/python-pillow/Pillow (2026-09-25 열람, 최신 릴리스 12.3.0)
15. comfyanonymous/ComfyUI, `execution.py`, 같은 저장소
