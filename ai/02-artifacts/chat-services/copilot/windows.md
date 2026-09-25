---
title: "Microsoft Copilot Windows 앱"
parent: "Microsoft Copilot"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 230
---

# Windows 앱 (Windows)

Windows 의 Copilot 앱은 패키지 이름 `Microsoft.Copilot` 인 스토어 앱이라서 설치 흔적과 관리 정책은 찾을 수 있지만, 앱이 대화를 기기 어디에 어떤 형식으로 두는지는 공식 문서에 없습니다.

> 확인 날짜: 2026-09. 이 페이지는 Microsoft 공식 문서(2026-09-25 열람)만 근거로 썼고, 이 PC 에서 Copilot 앱 폴더를 직접 관찰하지 않았습니다. 앱 버전 번호와 최소 Windows 빌드는 확인하지 못했고, 공식 안내 문서들은 2026-08-18 앱 버전 갱신을 언급합니다.

## 무엇을 기록하나 · 왜 생기나

Microsoft Store 제품 ID `9NHT9RB2F4HD`, 스토어 페이지 제목 "Microsoft Copilot on Windows" 인 앱이고, 공식 문서가 AppLocker 규칙에 적는 게시자 값은 `CN=MICROSOFT CORPORATION, O=MICROSOFT CORPORATION, L=REDMOND, S=WASHINGTON, C=US` 입니다. 관리되는 PC 에서는 2024년 9월 선택적 미리보기 업데이트와 10월 보안 업데이트(Windows 11), 11월 업데이트(Windows 10)로 예전 "Copilot in Windows" 사이드바를 대신했고, 새 Windows 11 PC 에는 기본으로 깔려 있다고 안내합니다. 로그인하면 채팅 기록, 이미지 만들기, 긴 대화, 음성 같은 기능을 쓸 수 있고, 계정에 쌓인 활동 기록은 [계정 데이터 내보내기](export.md)로 받습니다.

앱으로 들어가는 입력 경로가 여럿이라서 무엇이 서비스로 갈 수 있는지 먼저 알아 둡니다. 파일 검색 기능은 .docx, .xlsx, .pptx, .txt, .pdf, .json 파일을 읽을 수 있다고 안내하고, Copilot Vision 은 화면에 열려 있는 브라우저 창이나 앱을 보고 답합니다. "Hey Copilot" 깨우기 단어는 사용자가 켜야 동작합니다. 회사 계정 대상 문서는 음성 대화의 글 기록을 일반 대화처럼 저장·관리하고 음성 자체는 저장하지 않는다고 밝히지만, 같은 문장이 소비자용 앱에도 적용되는지는 확인하지 못했습니다. 음성 기능의 일반적인 흔적은 [음성 대화 기능](../../generative-media/voice-mode.md)에서 봅니다. 첨부와 생성물을 나눠 보는 기준은 [프롬프트·첨부·생성물 구분하기](../../../01-foundations/concepts/prompt-attachment-output.md)에 있습니다.

## 위치

| 무엇 | 위치·이름 | 확인 상태 |
|---|---|---|
| 앱 패키지 | 패키지 이름 `Microsoft.Copilot` | 공식 문서로 확인 |
| 앱 데이터 폴더 | `%LOCALAPPDATA%\Packages\` 아래 `Microsoft.Copilot` 로 시작하는 폴더 | 폴더 이름 뒷부분(게시자 해시)과 안의 구성은 확인하지 못함 |
| 대화 캐시·DB·로그 | 없음 | 위치와 형식 모두 확인하지 못함 |
| 관리 정책 | 아래 "관리 정책" 절 | 정책 이름은 확인, 레지스트리 경로·값 이름은 확인하지 못함 |

앱이 웹뷰로 화면을 그린다면 저장소 짜임은 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)와 [Electron·웹뷰 앱의 저장 구조](../../../01-foundations/storage-model/electron-webview.md)를 따르겠지만, Copilot 앱이 어떤 방식으로 화면을 그리는지는 확인하지 못했습니다. 앱 폴더 안에서 보호된 값이 나오면 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html) 페이지를 참고하고, 이 페이지에서는 값을 여는 방법을 다루지 않습니다.

## 여는 방법과 단축키

앱은 Copilot 키나 Windows 키 + C 로 엽니다. 2025년 5월 선택적 미리보기 업데이트부터 Windows 11 의 Copilot 키는 예전 사이드바 대신 새 방식으로 동작하는데, 회사 계정 대상 문서는 키를 누르면 가벼운 프롬프트 상자가 열리고 길게 누르면 음성 컨트롤러가 열린다고 설명합니다. 단축키 동작은 앱의 Account → Settings → Copilot Keyboard Shortcuts 에서 바꾸고, Copilot 키가 어느 앱을 열지는 Windows 설정 화면 `ms-settings:personalization-textinput-copilot-hardwarekey`("Customize Copilot key on keyboard")에서 사용자가 고릅니다. Copilot 키를 누른 흔적이 있어도 그 키가 Copilot 앱에 묶여 있었는지부터 확인합니다.

## 관리 정책

| 정책 | 이름·경로 | 뜻 |
|---|---|---|
| 레거시 끄기 정책 | 그룹 정책 "Turn Off Windows Copilot", MDM `TurnOffWindowsCopilot` | 곧 폐지 예정 |
| 설치·실행 막기 | AppLocker 규칙(패키지 이름 `MICROSOFT.COPILOT`) | 레거시 정책 대신 쓰라고 안내하고, 없는 앱은 설치를, 깔린 앱은 실행을 막음 |
| Copilot 키 대상 앱 | CSP `./User/Vendor/MSFT/Policy/Config/WindowsAI/SetCopilotHardwareKey` | 키가 열 앱을 지정 |
| 같은 설정의 그룹 정책 | User Configuration → Administrative Templates → Windows Components → Windows Copilot → Set Copilot Hardware Key | 위와 같음 |

이 정책 값이 레지스트리 어디에 어떤 값 이름으로 기록되는지는 확인하지 못해서, 정책 흔적은 그룹 정책·MDM 배포 기록이나 AppLocker 규칙 쪽에서 찾습니다. AppLocker 로 막혀 있었다면 그 기간의 실행 흔적이 없는 편이 자연스럽고, 막혀 있는데 실행 흔적이 있으면 정책 적용 시점부터 다시 봅니다.

## 이름이 헷갈리는 제품

회사 계정 PC 에서는 예전 "Microsoft 365 app" 이 "Microsoft Copilot app" 으로 이름을 바꿨고, 소비자용 "Microsoft Copilot" 앱과 이름이 비슷합니다. 화면에 보이는 이름으로 판단하지 않고 패키지 이름으로 구분합니다. 회사·학교(Microsoft Entra) 계정은 소비자용 Copilot 앱에 로그인할 수 없고, 회사용 Copilot Chat 은 [Microsoft 365 Copilot](../../office-integrations/m365-copilot.md)과 [Microsoft Purview로 본 Copilot 기록](../../network-enterprise/purview-copilot.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `Microsoft.Copilot` 패키지가 있으면 그 PC 에 소비자용 Copilot 앱이 설치되어 있었다고 쓸 수 있습니다. AppLocker 규칙이나 Copilot 키 정책이 있으면 그 PC 에 해당 정책이 놓여 있었다고 쓸 수 있습니다.

**증명하지 못하는 것.** 새 Windows 11 PC 에는 앱이 기본으로 깔려 있어서, 패키지가 있다는 사실만으로 사용자가 직접 설치했다거나 앱을 썼다고 쓰지 않습니다. 대화 내용은 기기에서 위치를 확인하지 못했고, 계정 쪽 기록은 [계정 데이터 내보내기](export.md)로 확인합니다. 그 계정으로 앉아 있던 사람은 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)를 따로 따져 봅니다.

## 시각 해석

앱 고유의 시각 기록은 확인하지 못했습니다. 패키지 폴더가 생기고 바뀐 시각은 파일 시스템 시각으로 보지만, 기본으로 깔린 앱이라서 폴더 시각이 사용자가 앱을 쓴 시각과 맞는다고 볼 근거가 없고, 사용 시각으로 읽지 않습니다. 다른 기록과 한 줄로 맞추는 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-windows/03-techniques/analysis/timeline/index.html)과 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)을 따릅니다.

## 함정과 한계

이 페이지에는 기기 관찰이 없어서 앱 폴더 안의 실제 모양은 검체에서 확인합니다. 예전 사이드바, 새 앱, Edge 안의 Copilot, 회사용 "Microsoft Copilot app" 은 서로 다른 흔적을 남기니, 사용자가 "Copilot" 이라고 말하면 어느 것인지부터 가립니다. Edge 안의 Copilot 은 [브라우저에 들어간 AI](../../office-integrations/browser-builtin-ai.md), 웹에서 쓴 경우는 [웹 브라우저](web.md)에서 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** 앱의 로컬 파일 형식을 확인하지 못해서 이 페이지에는 헥스 예시를 싣지 않습니다.

**공개 도구로 한 번.** 살아 있는 PC 에서는 공식 문서에 나오는 명령으로 설치 여부만 읽습니다. 이 명령은 문서의 제거 스크립트 첫 줄이지만, 여기서는 설치 흔적 확인용으로만 씁니다.

```powershell
# 설치된 Copilot 앱 패키지를 읽기만 한다(지우지 않는다)
Get-AppxPackage -Name "Microsoft.Copilot"
```

결과에서 패키지 버전과 설치 폴더를 기록합니다. 디스크 이미지에서는 사용자마다 `%LOCALAPPDATA%\Packages\` 아래에서 `Microsoft.Copilot` 으로 시작하는 폴더를 찾아 파일 시스템 시각을 적습니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 |
|---|---|
| [계정 데이터 내보내기](export.md) | 서버에 남은 프롬프트·응답 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 앱이 서비스와 통신한 시간대 |
| [Recall](../../windows-ai/recall.md) | Recall 을 켠 PC 라면 Copilot 창이 찍힌 스냅숏 |
| [기기에서 AI 흔적 모으기](../../../03-techniques/acquisition/endpoint-triage.md) | 앱 폴더와 정책을 함께 모으는 순서 |

## 실습

시험용 Windows 11 PC 와 개인 Microsoft 계정으로 직접 만든 검체에서 다음을 풀어 봅니다. 한 번도 열지 않은 기본 설치 상태와 로그인해 대화한 뒤의 상태에서 `Microsoft.Copilot` 패키지 폴더는 무엇이 달라지는가? Copilot 키 대상 앱을 바꾼 뒤 어느 기록에서 그 변경을 찾을 수 있는가?

## 참고 문헌

1. Updated Windows and Microsoft Copilot Chat experience (Microsoft Learn, 2026-08-18 갱신) — https://learn.microsoft.com/en-us/windows/client-management/manage-windows-copilot
2. Getting started with Copilot on Windows — https://support.microsoft.com/topic/1159c61f-86c3-4755-bf83-7fbff7e0982d
3. Microsoft Store: Microsoft Copilot on Windows (제목만 확인) — https://apps.microsoft.com/detail/9NHT9RB2F4HD
