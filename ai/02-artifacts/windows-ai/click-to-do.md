---
title: "클릭 투 두"
parent: "아티팩트 · Windows의 AI 기능"
nav_order: 500
---

# 클릭 투 두 (Click to Do)

클릭 투 두는 Copilot+ PC 에서 화면에 보이는 글자와 이미지를 골라 복사·검색·요약 같은 작업을 하게 해 주는 Windows 기능이고, 작업을 마치면 화면 내용을 보관하지 않아서 흔적은 주로 작업을 넘겨받은 앱, 클립보드, 임시 폴더, 정책 레지스트리에 남습니다.

> 기준: Microsoft Learn "Manage Click to Do"(ms.date 2025-12-10, 갱신 2026-08-18)[1], Microsoft 지원 문서 "Click to Do: do more with what's on your screen"(ms.date 2026-04-13, 갱신 2026-08-18)[2], "Policy CSP - WindowsAI"(ms.date 2026-09-10)[3]. 날짜는 문서 갱신 날짜이고 기능 버전이 아닙니다. 공식 문서에 없는 내용(임시 파일 이름, 사용자 설정 값의 저장 위치)은 검체로 확인해야 합니다.

## 무엇을 기록하나 · 왜 생기나

클릭 투 두는 Windows 키를 누른 채 마우스를 클릭하거나 Windows 키 + Q 를 눌러 엽니다. 터치 PC 에서 오른쪽 밀기(right swipe)로 열거나, 캡처 도구(Snipping Tool 11.2411.20.0 이상), 검색 결과, 시작 메뉴, Windows 검색에서 "Click to Do" 를 찾아 열 수도 있습니다[1][2]. 처음 열면 짧은 튜토리얼이 나오고, 메뉴의 "…" 에서 다시 볼 수 있습니다[2].

열리면 화면 스크린샷을 한 장 찍고 기기 안에서 분석해, 고를 수 있는 글자와 이미지를 보여 줍니다[1]. 글자는 광학 문자 인식(OCR)으로 찾고, 글자와 이미지가 있다는 것만 찾을 뿐 그 내용을 해석하지는 않습니다[1][2]. 켜져 있는 동안 커서가 파랑·흰색으로 바뀌고, 닫으면 분석이 끝나며 닫혀 있을 때는 스크린샷을 찍지 않습니다[1][3]. 최소화한 창처럼 화면에 없는 내용은 분석하지 않습니다[1].

하드웨어 기준은 Copilot+ PC 또는 해당하는 Cloud PC, 40 TOPS NPU, 16 GB RAM, 논리 프로세서 8개, 저장소 256 GB 입니다[1]. [Recall](recall.md)도 이 네 가지 숫자는 같지만, Recall 에는 Secured-core, 여유 공간 50 GB, 장치 암호화나 BitLocker, Windows Hello 강화 로그인 보안(ESS)이 더 필요합니다[4]. 클릭 투 두는 사용자에게 기본으로 켜져 있습니다[1].

### 작업 종류와 넘겨받는 곳

고른 내용의 종류에 따라 메뉴가 바뀝니다. 아래 표는 지원 문서[2]가 적은 작업과 그 작업을 맡는 곳입니다.

| 고른 내용 | 작업 | 맡는 곳 |
|---|---|---|
| 텍스트·이미지 | 복사 | 클립보드 |
| 텍스트 | 다른 앱으로 열기(Open with) | 메모장 같은 텍스트 편집기 |
| 텍스트 | 웹 검색 | Microsoft Edge 와 Bing |
| 이메일 주소 | 이메일 보내기 | 기본 메일 앱 |
| 이메일 주소 | Teams 메시지 보내기, Teams 회의 예약 | Teams |
| 웹사이트 주소 | 웹사이트 열기 | 기본 브라우저 |
| 텍스트(조건 있음) | 요약, 글머리표 목록 만들기, 다시 쓰기(Casual·Formal·Refine) | 기기 안의 Phi Silica |
| 텍스트(조건 있음) | Word 의 Copilot 으로 초안 쓰기 | Word 의 Copilot |
| 텍스트(조건 있음) | Reading Coach 연습, 몰입형 리더로 읽기 | Reading Coach |
| 이미지 | 다른 이름으로 저장(Save as) | 사용자가 정한 위치의 이미지 파일 |
| 이미지 | 공유 | 파일 공유 창 |
| 이미지 | 다른 앱으로 열기 | 사진, 캡처 도구, 그림판 같은 앱 |
| 이미지 | Bing 시각 검색 | 기본 브라우저와 Bing |
| 이미지 | 배경 흐림, 개체 지우기 / 배경 제거 | 사진 앱 / 그림판 |
| 텍스트·이미지 | Copilot 에 묻기 | Copilot(회사·학교 기기는 Microsoft Copilot) |

요약, 목록 만들기, 다시 쓰기는 Windows 에 기본으로 들어 있는 소형 언어 모델 Phi Silica 가 NPU 로 기기 안에서 처리하고, 고른 텍스트와 작업 종류가 프롬프트로 Phi Silica 에 들어갑니다[1][2]. 지원 문서는 이 작업이 기본 언어가 영어이고, 10 단어 이상을 골랐고, Microsoft 계정이나 Microsoft Entra 계정으로 로그인해 있을 때 나온다고 적고, Word 의 Copilot 초안과 Reading Coach 작업도 같은 목록에 넣었습니다[2]. Learn 문서는 영어에서 모든 작업을, 프랑스어와 스페인어에서는 요약·목록 만들기·Refine 만 쓸 수 있다고 적습니다[1].

Copilot 에 묻기를 고르면 고른 내용이 Copilot 의 프롬프트 상자에 들어간 채 Copilot 이 열립니다. 회사·학교 조직에 속한 기기에서는 이 작업이 "Ask Microsoft Copilot" 으로 바뀌고 Microsoft 365 라이선스가 필요합니다[2]. Copilot, Word, Teams, 사진 앱을 쓰는 작업은 그 앱이 설치돼 있을 때만 메뉴에 나오고, 사용자는 설정 → 앱 → 작업(Actions)에서 원하지 않는 작업을 끌 수 있습니다[1].

### 지역에 따라 빠지는 작업

지원 문서의 "Click to Do regional variations" 절[2]이 적은 차이는 아래와 같습니다.

| 지역 | 쓸 수 없는 작업 | 달라지는 작업 |
|---|---|---|
| 유럽 경제 지역(EEA) | Bing 시각 검색, 사진 앱·그림판의 고급 이미지 기능(흐림·제거·지우기), Copilot 에 묻기, Teams 작업, Reading Coach 연습, 몰입형 리더, Word 의 Copilot 으로 초안 쓰기 | 웹 검색은 그대로 Edge 와 Bing |
| 중국 | Copilot 에 묻기, Word 의 Copilot 으로 초안 쓰기, 요약, 글머리표 목록 만들기, 다시 쓰기(Formal), 다시 쓰기(Refine) | 웹 검색에 현지 검색 엔진을 쓸 수 있고, Bing 시각 검색도 다를 수 있음 |

다시 쓰기(Casual)는 중국 목록에 없고, EEA 목록에는 다시 쓰기가 아예 없습니다. 기기의 지역과 언어 설정에 따라 메뉴가 달라서[2], 어떤 작업을 할 수 있었는지는 기기 지역을 먼저 보고 판단합니다.

### 기기 밖으로 나가는 것

복사와 Phi Silica 작업은 기기 안에서 끝나고, 사용자가 온라인 작업을 골랐을 때만 고른 내용이 밖으로 나갑니다[1][2]. 웹 검색은 Edge 로 Bing 에 보내고, Bing 시각 검색은 기본 브라우저로 보내며, 웹사이트 열기는 기본 브라우저가 맡습니다[1]. 작업과 그 작업을 맡을 앱을 고른 뒤의 결과는 그 앱의 책임이라고 문서가 적었습니다[1][2]. 그래서 넘겨받은 내용이 서버로 갔는지, 서버에 얼마나 남는지는 그 앱과 서비스 쪽 기록에서 봅니다. 문서는 이와 별도로 "일부 진단 데이터를 모은다" 고만 적고, 어디에 두는지는 적지 않았습니다[1][2].

## 위치와 버전별 차이

클릭 투 두만의 작업 이력 저장소가 있다는 공식 설명은 없습니다. 공식 문서가 적은 로컬 기록은 아래 세 가지입니다.

| 기록 | 위치 | 근거 |
|---|---|---|
| 앱으로 넘길 때 만드는 임시 파일 | `C:\Users\{username}\AppData\Local\Temp` | [1][2] |
| 피드백을 보낼 때 만드는 임시 파일 | 위치는 문서에 없음 | [1][2] |
| 관리 정책 `DisableClickToDo` | SOFTWARE 하이브와 사용자 NTUSER.DAT 의 정책 키 | [1][3] |

그림판처럼 다른 앱으로 정보를 보낼 때 클릭 투 두는 전달을 마치려고 이 폴더에 임시 파일을 만듭니다[1][2]. 지원 문서는 이 이미지 파일이 "처리가 완전히 끝나거나 새 작업을 시작할 때까지" 남을 수 있고, 오래 보관하지는 않는다고 적습니다[2]. 파일 이름 규칙과 확장자는 공식 문서에 없어서 검체로 확인해야 합니다.

### 관리 정책

조직은 `DisableClickToDo` 정책으로 클릭 투 두를 끌 수 있고, 정책을 켜면 구성 요소와 진입점이 모두 사라집니다[1][3].

| 항목 | 값 |
|---|---|
| CSP 경로 | `./Device/Vendor/MSFT/Policy/Config/WindowsAI/DisableClickToDo`, `./User/Vendor/MSFT/Policy/Config/WindowsAI/DisableClickToDo` |
| Group Policy | 컴퓨터 구성과 사용자 구성 각각 관리 템플릿 → Windows 구성 요소 → Windows AI → Disable Click to Do |
| 레지스트리 키 | `SOFTWARE\Policies\Microsoft\Windows\WindowsAI` |
| 값 이름 | `DisableClickToDo` |
| 형식 | int |
| 값 | 0 켜짐(기본), 1 꺼짐 |
| ADMX | `WindowsCopilot.admx` |
| 적용 에디션 | Pro, Enterprise, Education, IoT Enterprise / IoT Enterprise LTSC |
| CSP 문서의 적용 OS 표기 | Windows Insider Preview |

정책 범위가 장치와 사용자 둘 다라서, 같은 키 경로가 SOFTWARE 하이브(장치 쪽)와 사용자의 NTUSER.DAT(사용자 쪽)에 따로 생길 수 있습니다[3]. Securelist 도 Recall 설정을 설명하면서 WindowsAI 정책 키가 사용자 하이브의 `Software\Policies\Microsoft\Windows\WindowsAI\` 에 있다고 적었습니다[5]. Recall 정책도 같은 키와 같은 ADMX 를 쓰므로, 이 키 아래의 다른 값은 [Recall](recall.md) 쪽에서 봅니다.

### 사용자가 끈 경우

사용자는 설정 → 개인 정보 및 보안 → Click to Do 에서 켜고 끌 수 있고, 기능을 지울 수는 없습니다[2]. 끄면 Windows 키 + 클릭, Windows 키 + Q, 오른쪽 밀기로는 열리지 않습니다. 캡처 도구 같은 곳에는 여는 메뉴가 계속 보일 수 있고, 누르면 "Couldn't open Click to Do" 오류가 납니다[2]. 이 설정 값을 어디에 저장하는지는 공식 문서에 없어서, 검체에서 설정을 바꾸기 전후의 레지스트리와 파일을 비교해 찾아야 합니다.

## 구조

클릭 투 두의 자체 기록 형식은 공개되지 않았습니다. 그래서 구조는 "고른 작업마다 흔적이 어디로 가는가" 로 정리합니다. 아래 표의 "맡는 곳" 은 지원 문서[2]에서 왔고, "찾아볼 흔적" 은 그 앱이 보통 남기는 기록을 가리키는 것이라 검체에서 확인해야 합니다.

| 고른 작업 | 맡는 곳 | 찾아볼 흔적 |
|---|---|---|
| 복사 | 클립보드 | 클립보드 기록(켜져 있을 때), 붙여 넣은 쪽 앱의 기록 |
| 다른 이름으로 저장 | 사용자가 정한 위치 | 새로 생긴 이미지 파일과 그 파일 시스템 시각 |
| 그림판·사진 앱 편집, 이미지 다른 앱으로 열기 | 해당 앱 | 임시 폴더 파일의 MFT·USN 기록, 그 앱이 저장한 파일 |
| 텍스트 다른 앱으로 열기 | 메모장 같은 텍스트 편집기 | 그 편집기의 기록 |
| 웹 검색 | Edge 와 Bing | Edge 방문 기록의 Bing 검색 |
| Bing 시각 검색, 웹사이트 열기 | 기본 브라우저 | 기본 브라우저 방문 기록 |
| 이메일 보내기 | 기본 메일 앱 | 메일 앱의 임시 보관함·보낸 편지함 |
| Teams 메시지·회의 예약 | Teams | Teams 메시지·일정 |
| Copilot 에 묻기 | Copilot 또는 Microsoft Copilot | [Microsoft Copilot](../chat-services/copilot/index.md) 대화 기록, 회사 기기는 [Microsoft Purview로 본 Copilot 기록](../network-enterprise/purview-copilot.md) |
| Word 의 Copilot 으로 초안 | Word | [Microsoft 365 Copilot](../office-integrations/m365-copilot.md) 기록과 Word 문서 |
| 요약, 목록 만들기, 다시 쓰기 | 기기 안의 Phi Silica | 공개된 기록 위치 없음 |

## 증거로서 의미

**증명하는 것.** 정책 키에 `DisableClickToDo`=1 이 있으면 관리자가 클릭 투 두를 막았다는 사실과 그 범위(장치 하이브인지 사용자 하이브인지)를 알 수 있습니다. 다른 이름으로 저장한 이미지 파일은 사용자가 정한 위치에 남으므로, 파일의 생성 시각은 그 시각에 이미지 파일이 만들어졌다는 기록이 됩니다. 임시 폴더에 이미지 파일이 생긴 시각과 그림판·사진 앱이 파일을 연 시각이 맞으면, 클릭 투 두로 화면 일부를 넘겼을 가능성을 뒷받침합니다. 다만 임시 파일 이름 규칙이 공개되지 않아서 이 연결은 시각과 정황으로 세우는 추정이고, 보고서에는 "이 시각에 임시 폴더에 이미지 파일이 생겼고 곧이어 그림판이 이 파일을 열었다" 처럼 기록이 말하는 만큼만 씁니다.

**증명하지 못하는 것.** 클릭 투 두는 작업 뒤 화면 내용을 보관하지 않아서, 사용자가 어떤 화면에서 무엇을 골랐는지 클릭 투 두 쪽 기록으로는 보여 줄 수 없습니다[1][2]. 기기 안 요약·다시 쓰기의 결과는 공개된 저장 위치가 없습니다. Edge 방문 기록의 Bing 검색, Copilot 대화, 저장한 이미지 파일이 있어도 그것만으로는 클릭 투 두를 거쳤는지 사용자가 직접 했는지 가를 수 없습니다. 정책 값이 없거나 0 이라는 사실도 사용자가 클릭 투 두를 썼다는 뜻이 아니고, 쓸 수 있었다는 뜻일 뿐입니다.

## 시각 해석

클릭 투 두 자체의 기록 시각은 공개된 것이 없습니다. 쓸 수 있는 시각은 임시 폴더와 저장 위치 파일의 생성·삭제 시각(MFT, USN 저널), 넘겨받은 앱의 기록 시각, 정책 키의 마지막 쓰기 시각입니다. 정책 키의 마지막 쓰기 시각은 그 키 아래 어떤 값이 바뀐 시각이라서, `DisableClickToDo` 가 바뀐 시각이라고 단정하지 않습니다. 같은 키에 Recall 정책 값도 들어가기 때문입니다[3]. MFT·USN·레지스트리 시각은 UTC 로 저장하지만 브라우저와 앱 기록은 형식과 기준 시간대가 제각각이라서, 한 타임라인에 올릴 때 기록마다 시간 형식을 확인하고 UTC 로 맞춥니다.

## 함정과 한계

`DisableClickToDo` 정책은 Recall 안의 클릭 투 두(Click to Do in Recall)에는 적용되지 않습니다[1][4]. Recall 에서 저장된 스냅숏을 열면 그 스냅숏 위에서 클릭 투 두가 돌고, 스냅숏의 글자를 복사하거나 그림을 jpeg 파일을 지원하는 앱으로 보낼 수 있습니다[4]. 그래서 정책으로 막은 기기에서도 Recall 이 켜져 있으면 스냅숏 위의 클릭 투 두는 쓸 수 있고, 이때 다루는 내용은 지금 화면이 아니라 저장된 스냅숏이라서 작업 시각과 그 화면이 보였던 시각이 다를 수 있습니다.

웹 검색은 기본 브라우저와 상관없이 Edge 로 가고, 시각 검색과 웹사이트 열기는 기본 브라우저로 갑니다[1]. 기본 브라우저가 Edge 가 아니면 한 사용자의 클릭 투 두 흔적이 브라우저 두 개에 나뉘어 남습니다.

임시 파일은 처리가 끝나거나 새 작업을 시작할 때까지만 남을 수 있어서[2], 수집이 늦으면 파일이 이미 없을 수 있습니다. 이때는 USN 저널과 MFT 에 남은 생성·삭제 기록을 봅니다.

사용자가 설정에서 끈 경우와 정책으로 막은 경우는 흔적이 다릅니다. 정책은 레지스트리 정책 키에 값이 남지만, 사용자 설정 값의 저장 위치는 공개되지 않았습니다.

KapeFiles 와 Velociraptor 교환 저장소에는 클릭 투 두 전용 항목이 없습니다. KapeFiles 의 `WindowsCopilotRecall.tkape` 는 Recall 폴더 `C:\Users\*\AppData\Local\CoreAIPlatform.00\UKP\` 만 모으고[6], Velociraptor 교환 저장소의 `Windows.System.Recall.AllWindowEvents`, `Windows.System.Recall.WindowCaptureEvent` 도 Recall 용입니다[7]. 그래서 임시 폴더, 정책 하이브, 넘겨받은 앱의 기록은 따로 수집 대상에 넣어야 합니다.

## 직접 분석해 보기

**헥스로 한 번.** `DisableClickToDo` 는 CSP 형식이 int 이고 값은 0 또는 1 입니다[3]. CSP 는 레지스트리 값 형식을 적지 않으므로, 하이브 안에서 값 이름 `DisableClickToDo` 를 찾아 값 형식부터 봅니다. 형식이 REG_DWORD 이면 데이터는 리틀 엔디언 4바이트이고, 아래는 값 1 을 그 형식대로 만든 예시라서 검체에서 뜬 바이트가 아닙니다.

```
만든 예시(REG_DWORD 1)
01 00 00 00
```

**공개 도구로 한 번.** SOFTWARE 하이브와 사용자마다의 NTUSER.DAT 를 Registry Explorer 같은 레지스트리 도구로 열고, 두 하이브 모두에서 `Policies\Microsoft\Windows\WindowsAI` 아래 `DisableClickToDo` 값과 키의 마지막 쓰기 시각을 적습니다. 임시 폴더는 MFTECmd 같은 공개 도구로 `$MFT` 와 `$UsnJrnl:$J` 를 풀어 해당 사용자의 `AppData\Local\Temp` 에서 생겼다 지워진 이미지 파일을 찾고, 그 시각을 그림판·사진 앱 실행 흔적과 나란히 놓습니다. Edge 와 크롬 계열 브라우저의 방문 기록을 읽는 방법은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html)에 있습니다.

## 교차 검증

스냅숏 위에서 도는 경우와 같은 정책 키의 Recall 값은 [Recall](recall.md)에서, Copilot 에 묻기로 넘어간 내용은 [Microsoft Copilot](../chat-services/copilot/index.md)에서 봅니다. 회사 기기의 Ask Microsoft Copilot 과 Word 의 Copilot 초안은 [Microsoft 365 Copilot](../office-integrations/m365-copilot.md)과 [Microsoft Purview로 본 Copilot 기록](../network-enterprise/purview-copilot.md)에서 이어 봅니다. Bing 검색과 시각 검색이 네트워크에 남긴 흔적은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)에서 다루고, 흩어진 시각을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)과 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-windows/03-techniques/analysis/timeline/index.html)에 있습니다. 화면에서 고른 텍스트가 프롬프트로 들어간 경우 프롬프트와 생성물을 가르는 기준은 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)에 있습니다.

## 실습

시험용 Copilot+ PC 에서 다음 질문으로 풀어 봅니다.

1. 화면의 이미지를 클릭 투 두로 그림판에 넘긴 뒤 임시 폴더에 어떤 이름과 확장자의 파일이 생기는지, 새 작업을 시작하면 사라지는지 USN 저널로 봅니다.
2. 기본 브라우저를 Edge 가 아닌 브라우저로 둔 채 웹 검색과 시각 검색을 한 번씩 하고, 각각 어느 브라우저 방문 기록에 남는지 봅니다.
3. `DisableClickToDo` 를 장치 쪽과 사용자 쪽에 각각 1 로 둔 뒤, Windows 키 + Q 와 Recall 스냅숏 위에서 클릭 투 두가 열리는지 봅니다.
4. 설정 → 개인 정보 및 보안 → Click to Do 를 끄기 전후로 레지스트리를 비교해 사용자 설정이 어디에 바뀌는지 찾습니다.
5. 기기 안 요약만 한 경우와 다른 앱으로 넘긴 경우를 비교해 파일 시스템에 남는 차이를 적습니다.

## 참고 문헌

1. Microsoft Learn, "Manage Click to Do" (ms.date 2025-12-10, 갱신 2026-08-18) — https://learn.microsoft.com/en-us/windows/client-management/manage-click-to-do
2. Microsoft Support, "Click to Do: do more with what's on your screen" (ms.date 2026-04-13, 갱신 2026-08-18) — https://support.microsoft.com/en-us/windows/ai/ai-features/click-to-do-do-more-with-what-s-on-your-screen
3. Microsoft Learn, "Policy CSP - WindowsAI" (ms.date 2026-09-10, 갱신 2026-09-23), DisableClickToDo 절 — https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-windowsai
4. Microsoft Learn, "Manage Recall" (ms.date 2025-12-10) — https://learn.microsoft.com/en-us/windows/client-management/manage-recall
5. Kirill Magaskin, "What makes Windows 11 interesting from a digital forensics perspective", Securelist (2025-10-14, 수정 2026-08-13) — https://securelist.com/forensic-artifacts-in-windows-11/117680/
6. EricZimmerman/KapeFiles — https://github.com/EricZimmerman/KapeFiles, `Targets/Windows/WindowsCopilotRecall.tkape`
7. Velocidex/velociraptor-docs — https://github.com/Velocidex/velociraptor-docs, `content/exchange/artifacts/Windows.System.Recall.AllWindowEvents.yaml`, `content/exchange/artifacts/Windows.System.Recall.WindowCaptureEvent.yaml`
