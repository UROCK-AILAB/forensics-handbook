---
title: "클릭 투 두"
parent: "아티팩트 · Windows의 AI 기능"
nav_order: 470
---

# 클릭 투 두 (Click to Do)

클릭 투 두는 Copilot+ PC 에서 화면에 보이는 글자와 이미지를 알아보고 그 위에서 복사, 검색, 요약 같은 작업을 하게 해 주는 Windows 기능이고, 작업을 마치면 화면 내용을 보관하지 않아서 흔적은 주로 작업을 넘겨받은 앱과 임시 폴더에 남습니다.

> 확인 날짜: 2026-09. 동작 방식과 정책은 Microsoft 공식 문서(Manage Click to Do 는 ms.date 2025-12-10, 2026-08-18 갱신, WindowsAI Policy CSP 는 ms.date 2026-09-10)와 Microsoft 지원 문서로 확인했습니다. 이 핸드북을 쓰면서 클릭 투 두의 파일이나 레지스트리를 직접 관찰하지는 않았고, 프로세스·패키지 이름과 버전 번호는 확인하지 못했습니다.

## 무엇을 기록하나 · 왜 생기나

클릭 투 두는 Windows 키를 누른 채 마우스를 클릭하거나, Windows 키 + Q 를 누르거나, 터치 PC 에서 오른쪽 가장자리를 밀어서 엽니다. 캡처 도구(Snipping Tool 11.2411.20.0 이상), 검색 결과, 시작 메뉴에서도 열 수 있습니다. 열리면 화면 스크린샷을 한 장 찍어 분석하고, 켜져 있는 동안 커서가 파랑·흰색으로 바뀌며, 닫으면 그대로 끝나서 닫혀 있을 때는 스크린샷을 찍지 않습니다. 분석은 늘 기기 안에서 하고 최소화한 창처럼 화면에 없는 내용은 보지 않습니다.

Copilot+ PC 나 그에 해당하는 Cloud PC 에서 돌고, NPU·메모리·논리 프로세서·저장소 최소 기준은 [Recall](recall.md)과 같습니다. 사용자에게는 기본으로 켜져 있습니다.

### 작업 종류

| 대상 | 작업 |
|---|---|
| 여러 형식 공통 | 복사, 다른 앱으로 열기, 웹 검색, Microsoft Copilot 에 묻기 |
| 텍스트 | 요약, 글머리표 목록 만들기, 다시 쓰기(Casual·Formal·Refine), Word 의 Copilot 으로 초안 쓰기, Reading Coach 연습, 몰입형 리더 |
| 이미지 | 공유, 저장, Bing 시각 검색, 사진 앱의 배경 흐림·개체 지우기, 그림판의 배경 제거 |
| 이메일 주소·Teams | 이메일 보내기, 주소 정보 더 보기, Teams 메시지 보내기, Teams 회의 예약 |

요약, 다시 쓰기, 목록 만들기는 Windows 에 기본으로 들어 있는 소형 언어 모델 Phi Silica 가 NPU 로 기기 안에서 처리하고, 사용자가 고른 텍스트와 작업 종류가 프롬프트로 Phi Silica 에 들어갑니다. 이 텍스트 작업은 영어에서 모두 쓸 수 있고, 프랑스어와 스페인어에서는 요약, 목록 만들기, 다시 쓰기(Refine)만 쓸 수 있습니다. Copilot, Word, Teams, 사진 앱처럼 다른 앱을 쓰는 작업은 그 앱이 설치돼 있을 때만 메뉴에 나오고, 사용자는 설정 → 앱 → 작업(Actions) 에서 작업을 하나씩 끌 수 있습니다. EEA 에서는 시각 검색, Copilot 에 묻기, Teams 작업, AI 다시 쓰기가 없고, 중국에서는 요약과 다시 쓰기가 제한됩니다.

### 서버로 나가는 것

로컬 작업인 복사와 Phi Silica 텍스트 작업은 기기 안에서 끝나고, 사용자가 온라인 작업을 골랐을 때만 고른 내용이 밖으로 나갑니다. 웹 검색은 Microsoft Edge 로 Bing 에서 찾고, 시각 검색은 기본 브라우저로 Bing 시각 검색을 열며, 웹사이트 열기는 기본 브라우저가 맡습니다. 작업을 고른 뒤의 결과는 그 작업을 맡은 앱의 책임이라서, 넘겨받은 내용이 서버로 가는지, 서버에 얼마나 남는지는 그 앱과 서비스의 정책을 따릅니다. 이와 따로 일부 진단 데이터는 수집됩니다.

## 위치와 버전별 차이

클릭 투 두 자체의 작업 이력 저장소가 있다는 공식 설명은 없습니다. 문서가 적은 로컬 파일은 내용을 그림판 같은 다른 앱으로 넘길 때 만드는 임시 파일 하나뿐이고, 위치는 아래와 같습니다. 피드백을 보낼 때도 임시 파일이 생길 수 있고, 둘 다 오래 보관하지 않는다고 적혀 있습니다. 임시 파일의 이름 규칙과 확장자는 확인하지 못했습니다.

```
C:\Users\{username}\AppData\Local\Temp
```

조직은 `DisableClickToDo` 정책으로 클릭 투 두를 끌 수 있고, 켜면 구성 요소와 진입점이 모두 사라집니다. 레지스트리 키와 ADMX 는 Recall 정책과 같습니다.

| 항목 | 값 |
|---|---|
| 레지스트리 키 | `SOFTWARE\Policies\Microsoft\Windows\WindowsAI` |
| 값 이름 | `DisableClickToDo` |
| 범위 | 장치·사용자 |
| 값 | 0 켜짐(기본), 1 꺼짐 |
| ADMX | `WindowsCopilot.admx` |
| CSP 문서의 적용 OS 표기 | Windows Insider Preview |

사용자가 끄는 곳은 설정 → 개인 정보 및 보안 → Click to Do 이지만, 이 토글을 어디에 저장하는지는 확인하지 못했습니다. 실행 횟수나 시각 같은 사용 흔적이 이벤트 로그나 앱 사용 기록에 남는지도 확인하지 못했습니다.

## 구조

자체 기록이 알려지지 않아서, 작업마다 흔적을 찾아갈 곳으로 구조를 정리합니다. 아래 표는 공식 문서가 적은 작업 흐름에서 끌어낸 것이고 검체로 확인하지 않았습니다.

| 고른 작업 | 넘겨받는 곳 | 찾아볼 흔적 |
|---|---|---|
| 웹 검색 | Microsoft Edge 와 Bing | Edge 방문 기록의 Bing 검색 |
| 시각 검색, 웹사이트 열기 | 기본 브라우저와 Bing | 기본 브라우저 방문 기록 |
| Copilot 에 묻기 | Microsoft Copilot | Copilot 쪽 대화 기록 |
| Word 의 Copilot 으로 초안 | Word | Word 문서와 Copilot 기록 |
| Teams 메시지·회의 예약 | Teams | Teams 메시지·일정 |
| 사진 앱·그림판 편집, 다른 앱으로 열기 | 해당 앱 | 임시 폴더 파일의 MFT·USN 기록, 그 앱이 저장한 파일 |
| 복사, 요약, 다시 쓰기, 목록 만들기 | 기기 안(Phi Silica) | 클릭 투 두 쪽 기록은 알려진 것 없음 |

## 증거로서 의미

**증명하는 것.** 정책 키에 `DisableClickToDo`=1 이 있으면 조직이 클릭 투 두를 막았다는 사실과 그 범위(장치 또는 사용자)를 알려 줍니다. 임시 폴더에 다른 앱으로 넘긴 파일의 흔적이 있고, 그 시각이 사진 앱이나 그림판에서 파일을 연 시각과 맞으면 클릭 투 두로 화면 일부를 넘겼을 가능성을 뒷받침합니다. 다만 임시 파일 이름 규칙을 몰라서 이 연결은 시각과 정황으로 세우는 추정이고, 보고서에는 "이 시각에 임시 폴더에 이미지 파일이 생겼고 곧이어 그림판이 이 파일을 열었다" 처럼 기록이 말하는 만큼만 씁니다.

**증명하지 못하는 것.** 클릭 투 두는 작업 뒤 화면 내용을 보관하지 않아서, 사용자가 어떤 화면에서 무엇을 골랐는지를 클릭 투 두 쪽 기록으로 보일 수 없습니다. 복사나 기기 안 요약처럼 다른 앱으로 넘기지 않은 작업은 알려진 흔적이 없습니다. Edge 방문 기록의 Bing 검색이나 Copilot 대화가 있어도 그것만으로 클릭 투 두를 거쳤는지, 사용자가 직접 입력했는지는 가를 수 없습니다. 정책이 켜져 있지 않다고 사용자가 클릭 투 두를 썼다는 뜻도 아닙니다.

## 시각 해석

클릭 투 두 자체에서 쓸 수 있는 시각은 알려진 것이 없습니다. 쓸 수 있는 시각은 임시 폴더 파일의 생성·삭제 시각(MFT, USN 저널), 넘겨받은 앱의 기록 시각, 정책 키의 마지막 쓰기 시각입니다. 브라우저 방문 기록과 파일 시스템 시각은 저장 방식과 기준 시간대가 제각각이라서, 한 타임라인에 올릴 때 각 기록의 시간 형식을 따로 확인하고 UTC 로 맞춥니다.

## 함정과 한계

`DisableClickToDo` 정책은 Recall 안에서 도는 클릭 투 두(Click to Do in Recall)에는 영향이 없습니다. Recall 에서 저장된 스냅숏을 열면 그 스냅숏 위에서 클릭 투 두가 돌기 때문에, 정책으로 막은 기기에서도 Recall 이 켜져 있으면 스냅숏 위의 클릭 투 두는 쓸 수 있습니다. Manage Recall 문서는 이때 스냅숏의 글자를 복사하거나 그림을 jpeg 를 받는 앱으로 보낼 수 있다고 적었습니다. 이 경우 분석 대상은 지금 화면이 아니라 이미 저장한 스냅숏이라서 작업 시각과 화면에 보였던 시각이 다를 수 있습니다.

웹 검색은 기본 브라우저가 아니라 Edge 로 가고 시각 검색과 웹사이트 열기는 기본 브라우저로 가서, 한 사용자의 클릭 투 두 흔적이 브라우저 두 개에 나뉘어 남을 수 있습니다. 임시 파일은 오래 보관하지 않아서 수집이 늦으면 파일이 이미 없을 수 있고, 이때는 USN 저널과 MFT 에 남은 기록을 봅니다. 문서가 말하는 진단 데이터 수집은 기기 밖으로 가는 것이라 로컬 사용 기록으로 쓸 수 있는지는 알 수 없습니다.

## 직접 분석해 보기

**헥스로 한 번.** 정책 값 `DisableClickToDo` 는 0 또는 1 이고, 레지스트리의 REG_DWORD 값은 리틀 엔디언 4바이트로 저장됩니다. 아래는 값 1 을 명세대로 만든 예시이고, 검체에서 뜬 바이트가 아닙니다. 하이브 안에서 값 이름 `DisableClickToDo` 를 찾고, 그 값의 데이터가 이 4바이트인지 봅니다.

```
명세로 만든 예시(REG_DWORD 1)
01 00 00 00
```

**공개 도구로 한 번.** SOFTWARE 하이브와 사용자의 NTUSER.DAT 를 Registry Explorer 같은 레지스트리 도구로 열어 `SOFTWARE\Policies\Microsoft\Windows\WindowsAI` 아래 `DisableClickToDo` 값과 키의 마지막 쓰기 시각을 적습니다. 임시 폴더는 MFTECmd 같은 공개 도구로 `$MFT` 와 `$UsnJrnl:$J` 를 풀어 해당 사용자의 `AppData\Local\Temp` 경로에서 생겼다 지워진 이미지 파일을 찾고, 그 시각을 그림판·사진 앱 실행 흔적과 나란히 놓습니다. Edge 와 크롬 계열 브라우저의 방문 기록을 읽는 방법은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html)에 있습니다.

## 교차 검증

스냅숏 위에서 도는 경우와 하드웨어 기준은 [Recall](recall.md)에서, Copilot 에 묻기로 넘어간 내용은 [Microsoft Copilot](../chat-services/copilot/index.md)에서, Word 의 Copilot 초안은 [Microsoft 365 Copilot](../office-integrations/m365-copilot.md)에서 이어 봅니다. Bing 검색과 시각 검색이 네트워크에 남긴 흔적은 [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md)에서 다루고, 흩어진 시각을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다. 화면에서 고른 텍스트가 프롬프트로 들어간 경우 프롬프트와 생성물을 가르는 기준은 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)에 있습니다.

## 실습

공개 검체에 클릭 투 두 흔적이 들어 있는지는 확인하지 못했습니다. 시험용 Copilot+ PC 가 있다면 다음 질문으로 풀어 봅니다.

1. 화면의 이미지를 클릭 투 두로 그림판에 넘긴 뒤 임시 폴더에 어떤 파일이 어떤 이름으로 생기는지, 얼마 뒤 사라지는지 USN 저널로 확인합니다.
2. 기본 브라우저를 Edge 가 아닌 브라우저로 둔 채 웹 검색과 시각 검색을 한 번씩 하고, 각각 어느 브라우저 방문 기록에 남는지 봅니다.
3. `DisableClickToDo` 를 1로 둔 뒤 Windows 키 + Q 와 Recall 스냅숏 위에서 각각 클릭 투 두가 열리는지 봅니다.
4. 기기 안 요약만 한 경우와 다른 앱으로 넘긴 경우를 비교해 파일 시스템에 남는 차이를 적습니다.

## 참고 문헌

1. Manage Click to Do for Windows clients (Microsoft Learn) — https://learn.microsoft.com/en-us/windows/client-management/manage-click-to-do
2. Click to Do: do more with what's on your screen (Microsoft Support) — https://support.microsoft.com/en-us/windows/click-to-do-do-more-with-what-s-on-your-screen-6848b7d5-7fb0-4c43-b08a-443d6d3f5955
3. WindowsAI Policy CSP (Microsoft Learn) — https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-windowsai
4. Manage Recall for Windows clients (Microsoft Learn) — https://learn.microsoft.com/en-us/windows/client-management/manage-recall
