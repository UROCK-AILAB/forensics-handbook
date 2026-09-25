---
title: "Microsoft Copilot Windows 앱"
parent: "Microsoft Copilot"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 230
---

# Windows 앱 (Windows)

Windows 의 소비자용 Copilot 앱은 패키지 이름이 `Microsoft.Copilot` 인 스토어 앱이고, 기기에서는 설치 흔적과 관리 정책 값을 읽을 수 있지만 대화를 어디에 어떤 형식으로 두는지는 공식 문서에 나오지 않습니다.

## 무엇을 기록하나 · 왜 생기나

Microsoft Store 제품 ID 는 `9NHT9RB2F4HD` 이고 스토어 페이지 제목은 "Microsoft Copilot on Windows" 입니다[6]. 새 Windows 11 PC 에는 앱이 기본으로 깔려 있고, 작업 표시줄이나 시작 메뉴에 고정되어 있습니다[3]. 개인 Microsoft 계정으로 로그인하면 채팅 기록, 이미지 만들기, 긴 대화, 음성 대화를 쓸 수 있습니다[3]. 계정에 쌓인 활동 기록은 [계정 데이터 내보내기](export.md)로 받습니다.

지원 문서는 copilot.com 의 기능 말고도 이 앱에만 있는 기능 일곱 가지를 적습니다[3]. 단축키는 아래 "구조" 절에서 다루고, 나머지 여섯 가지는 아래와 같습니다.

| 기능 | 문서가 적은 동작[3] | 조사에서 볼 점 |
|---|---|---|
| 파일 검색 (File search) | 기기의 파일(동기화된 OneDrive 파일 포함)을 찾아 열고 내용을 묻는다. .docx, .xlsx, .pptx, .txt, .pdf, .json 을 읽는다 | 권한은 앱의 Account → Settings → File Search and File Read 에서 켜고 끈다 |
| 스크린샷 (Take a screenshot) | 입력 창의 + 에서 화면 전체나 일부를 잡아 Copilot 에 올린다 | 화면 내용이 첨부로 넘어간다 |
| Copilot Vision | 화면에 열린 브라우저 창이나 앱을 보고 답한다 | 화면 내용이 서비스로 넘어간다 |
| 웹 내용 보기 (View web content) | 링크를 대화 옆 창에서 연다. 연 탭은 그 대화와 함께 저장된다. 사용자가 켜면 비밀번호와 양식 데이터를 동기화한다 | 대화마다 탭 목록이 남는다. 비밀번호가 있으면 보고서에서 가린다 |
| 깨우기 단어 ("Hey Copilot") | 사용자가 켜야(opt-in) 동작한다 | 설정을 켰는지부터 본다 |
| Windows 설정 도움 | 설정 화면의 해당 항목으로 안내한다 | |

첨부와 생성물을 나눠 보는 기준은 [프롬프트·첨부·생성물 구분하기](../../../01-foundations/concepts/prompt-attachment-output.md)에, 음성 기능의 일반적인 흔적은 [음성 대화 기능](../../generative-media/voice-mode.md)에 있습니다.

## 위치와 버전별 차이

| 무엇 | 위치·이름 | 근거 |
|---|---|---|
| 앱 패키지 | 패키지 이름 `Microsoft.Copilot` | 공식 문서[1] |
| 앱 데이터 폴더 | 사용자마다 `%LOCALAPPDATA%\Packages\` 아래 `Microsoft.Copilot_` 로 시작하는 폴더 | 뒷부분 `8wekyb3d8bbwe` 는 공개 스크립트[9]에만 나오고 공식 문서에는 없다. 검체에서 이름을 확인한다 |
| 대화 저장 파일 | 공개된 분석 자료가 없다 | 검체에서 확인한다 |
| 관리 정책 값 | 아래 "구조" 절의 표 | 공식 문서[2] |
| 마이크 권한 값 | NTUSER.DAT `Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone\Microsoft.Copilot_8wekyb3d8bbwe`, 값 `Value`(`Allow`·`Deny`) | 공개 스크립트 코드[9]. 이 키 아래 다른 값은 검체에서 본다 |

앱 폴더 안에서 크롬 계열 저장소(Local Storage, IndexedDB 같은 폴더)가 보이면 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)와 [Electron·웹뷰 앱의 저장 구조](../../../01-foundations/storage-model/electron-webview.md)로 읽습니다. 보호된 값이 나오면 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html)를 참고하고, 이 페이지에서는 값을 여는 방법을 다루지 않습니다.

### 배포 연혁

관리되는 PC 에는 2024년 9월 선택적 미리보기 업데이트와 10월 월간 보안 업데이트(Windows 11), 11월 업데이트(Windows 10)로 들어왔고, 이 업데이트가 예전 "Copilot in Windows" 사이드바를 대신했습니다[1]. 이 업데이트를 설치하면 앱이 자동으로 켜지는데, 그 전에 설치를 막는 그룹 정책을 켜 두었다면 예외입니다[1]. 2025년 5월 선택적 미리보기 업데이트부터는 Windows 11 의 Copilot 키가 사이드바 대신 새 방식으로 동작합니다[1]. 2025년 11월부터 음성 대화를 새로 시작할 수 있다고 회사 계정 대상 문서가 적습니다[1].

### 이름이 비슷한 회사용 앱

회사 계정 PC 에서는 예전 "Microsoft 365 app" 이 "Microsoft Copilot app" 으로 이름을 바꿨고, 소비자용 "Microsoft Copilot" 앱과 이름이 비슷합니다[1]. 화면 이름으로 가르지 않고 패키지 이름으로 가릅니다. 정책 문서의 예시에서 회사용 앱의 AUMID 는 `Microsoft.MicrosoftOfficeHub_8wekyb3d8bbwe!Microsoft.MicrosoftOfficeHub` 이라서, 회사용은 `Microsoft.MicrosoftOfficeHub`, 소비자용은 `Microsoft.Copilot` 로 구분하면 됩니다[2].

회사·학교(Microsoft Entra) 계정은 소비자용 앱에 로그인할 수 없습니다. 로그인하려 하면 기본 브라우저에서 `https://m365.cloud.microsoft/chat` 이 열리므로 그 브라우저 방문 기록에 흔적이 남을 수 있습니다[1]. 회사용 Copilot Chat 은 [Microsoft 365 Copilot](../../office-integrations/m365-copilot.md)과 [Microsoft Purview로 본 Copilot 기록](../../network-enterprise/purview-copilot.md)에서 다룹니다.

## 구조

대화 파일의 짜임은 공개된 분석 자료가 없어서, 이 절은 공식 문서가 밝힌 관리 정책 값만 다룹니다. `TurnOffWindowsCopilot` 과 `SetCopilotHardwareKey` 의 ADMX 는 `WindowsCopilot.admx` 이고, `RemoveMicrosoftCopilotApp` 은 CSP 에 ADMX 이름이 없습니다[2].

| 정책 | 범위 | 레지스트리 | 값 | 적용 OS·에디션 |
|---|---|---|---|---|
| `TurnOffWindowsCopilot` (그룹 정책 "Turn off Windows Copilot") | User | NTUSER.DAT `SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot`, 값 이름 `TurnOffWindowsCopilot` | 정수. 0 기본(허용), 1 끔 | Windows 10 21H2 [10.0.19044.3758] 이후, Windows 10 22H2 KB5032278 [10.0.19045.3758] 이후, Windows 11 22H2 KB5030310 [10.0.22621.2361] 이후, Windows 11 23H2 [10.0.22631] 이후. Pro·Enterprise·Education·IoT Enterprise |
| `SetCopilotHardwareKey` (그룹 정책 "Set Copilot Hardware Key") | User | NTUSER.DAT `SOFTWARE\Policies\Microsoft\Windows\CopilotKey`. 값 이름은 문서에 없다 | 문자열. 키가 열 앱의 AUMID | Windows 11 22H2 KB5044380 [10.0.22621.4391] 이후. Pro·Enterprise·Education·IoT Enterprise |
| `RemoveMicrosoftCopilotApp` | Device, User | 문서에 없다 | 정수. 0 Removal Disabled, 1 Removal Enabled | Windows 11 24H2 [10.0.26100] 이후. 에디션은 아래 설명 |
| AppLocker 패키지 앱 규칙 | 규칙에 따라 | AppLocker 정책 | Publisher `CN=MICROSOFT CORPORATION, O=MICROSOFT CORPORATION, L=REDMOND, S=WASHINGTON, C=US`, Package name `MICROSOFT.COPILOT`, Package version `* (and above)`[1] | 문서에 없다 |

그룹 정책 경로는 `TurnOffWindowsCopilot` 과 `SetCopilotHardwareKey` 가 User Configuration → Administrative Templates → Windows Components → Windows Copilot 이고, `RemoveMicrosoftCopilotApp` 은 문서에 "WindowsAI > AT > WindowsComponents > WindowsAI" 로 적혀 있습니다[1][2]. CSP 경로는 `./User/Vendor/MSFT/Policy/Config/WindowsAI/` 뒤에 정책 이름을 붙이고, `RemoveMicrosoftCopilotApp` 에는 `./Device/...` 경로도 있습니다[2].

정책마다 읽을 때 알아 둘 점이 있습니다.

- **TurnOffWindowsCopilot.** CSP 는 이 정책이 폐지됐고(deprecated) 이후 릴리스에서 빠질 수 있다고 적고, 이 정책이 새 Copilot 경험에는 적용되지 않는다고 밝힙니다[2]. 같은 문서는 사이드바가 들어 있던 이미지에서 업그레이드할 때 Copilot 앱이 설치되지 않게 막는 데에도 이 정책이 적용된다고 적습니다[2]. 관리 문서는 이 정책이 곧 폐지될 예정이라며 대신 AppLocker 를 쓰라고 안내합니다[1].
- **SetCopilotHardwareKey.** 정책을 두지 않으면 그 나라·지역에서 쓸 수 있을 때 Copilot 이 열리고, 정책이 있어도 사용자가 설정에서 키를 바꿀 수 있습니다[2]. 사용자는 설정 → 개인 설정 → 텍스트 입력의 "Customize Copilot key on keyboard"(`ms-settings:personalization-textinput-copilot-hardwarekey`)에서 Search, Custom, 지금 묶인 앱 가운데 고릅니다[1]. 앱 쪽에서는 Account → Settings → Copilot Keyboard Shortcuts 에서 키가 전체 앱을 열지 작은 빠른 보기를 열지 정합니다[3].
- **RemoveMicrosoftCopilotApp.** 세 조건을 모두 채운 기기·사용자에게만 앱을 지웁니다. Microsoft 365 Copilot 과 Microsoft Copilot 이 둘 다 설치되어 있고, 사용자가 직접 설치한 앱이 아니고, 최근 28일 동안 앱을 실행하지 않았어야 합니다[2]. 지운 뒤에도 사용자가 다시 설치할 수 있습니다[2]. Intune 설정 카탈로그를 추적하는 저장소의 같은 정책 설명은 기간을 14일로 적고 있어서(2026-07-13 커밋)[7], CSP(2026-09-23 갱신)와 다릅니다. 에디션도 CSP 표에서는 Pro 가 빠져 있고 본문은 "Enterprise, Professional and Education" 이라고 적어 한 문서 안에서 다릅니다[2]. 레지스트리 위치가 문서에 없으므로 검체의 SOFTWARE 하이브와 NTUSER.DAT 에서 `RemoveMicrosoftCopilotApp` 이름으로 찾아봅니다.
- **AppLocker 규칙.** 앱이 없으면 설치를 막고, 이미 깔려 있으면 실행을 막습니다[1].

## 증거로서 의미

**증명하는 것.** `Microsoft.Copilot` 패키지가 있으면 그 PC 에 소비자용 Copilot 앱이 설치되어 있었다고 쓸 수 있습니다. 정책 키나 AppLocker 규칙이 있으면 그 PC 나 사용자에게 해당 정책이 놓여 있었다고 쓸 수 있습니다. `RemoveMicrosoftCopilotApp` 으로 앱이 지워졌다는 사실이 다른 기록으로 확인되면, 지우기 전 28일(Intune 설명으로는 14일) 동안 앱을 실행한 적이 없고 사용자가 직접 설치한 앱도 아니었다는 조건을 채웠다는 뜻입니다[2][7].

**증명하지 못하는 것.** 새 Windows 11 PC 에는 앱이 기본으로 깔려 있어서, 패키지가 있다는 사실만으로 사용자가 직접 설치했다거나 앱을 썼다고 쓰지 않습니다[3]. `TurnOffWindowsCopilot` 이 1 이라는 사실만으로 새 앱을 쓰지 않았다고 쓰지도 않습니다. 이 정책은 새 Copilot 경험에 적용되지 않기 때문입니다[2]. 대화 내용은 계정 쪽 기록인 [계정 데이터 내보내기](export.md)로 확인하고, 그 계정으로 앉아 있던 사람은 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)에서 따로 따집니다.

## 시각 해석

공식 문서는 이 앱의 시각 기록을 설명하지 않습니다. 패키지 폴더의 파일 시스템 시각은 폴더가 생기고 바뀐 때를 알려 주지만, 기본으로 깔린 앱이라서 폴더가 생긴 시각을 사용자가 앱을 처음 쓴 시각으로 읽지 않습니다. 정책 키의 마지막 기록 시각(LastWrite, UTC)은 그 키가 마지막으로 바뀐 때이고, 정책이 처음 놓인 때와 다를 수 있습니다.

배포 연혁의 날짜(2024년 9~11월, 2025년 5월, 2025년 11월)[1]는 그 기기에 어떤 업데이트가 설치됐는지와 맞춰 볼 때 기준점이 됩니다. 다른 기록과 한 줄로 맞추는 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-windows/03-techniques/analysis/timeline/index.html)과 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)을 따릅니다.

## 함정과 한계

사용자가 "Copilot" 이라고 말하면 예전 사이드바, 소비자용 앱, 회사용 "Microsoft Copilot app", Edge 안의 Copilot, 웹의 copilot.com 가운데 어느 것인지부터 가립니다. Edge 안의 Copilot 은 [브라우저에 들어간 AI](../../office-integrations/browser-builtin-ai.md), 웹에서 쓴 경우는 [웹 브라우저](web.md)에서 봅니다.

Copilot 키를 누른 흔적이 있어도 그 키가 어느 앱에 묶여 있었는지부터 봅니다. `SetCopilotHardwareKey` 가 있어도 사용자가 설정에서 바꿀 수 있으므로[2], 정책 값만으로 그 시점의 대상 앱을 단정하지 않습니다.

음성 대화의 저장 방식은 회사 계정 대상 문서에만 나옵니다. 이 문서는 음성 대화의 글 기록을 일반 대화처럼 저장해 보존·eDiscovery·감사 정책을 적용하고, 사용자와 Copilot 의 음성은 저장하지 않는다고 적습니다[1]. 같은 문서는 "Hey Copilot" 이 기능을 켰고 PC 잠금이 풀려 있을 때만 동작한다고 적고, 관리자가 음성 기능만 따로 끄는 설정은 없다고 밝힙니다[1]. 소비자용 앱에 대한 같은 설명은 공식 문서에 없으므로 그대로 옮겨 쓰지 않습니다.

Purview 보존 정책의 "Other AI apps" 위치에는 "Microsoft Copilot (consumer version)" 이 들어 있고, 조직에 내용을 수집하는 수집 정책(collection policy)이 있어야 프롬프트와 응답이 남습니다[4]. eDiscovery 문서는 Other AI apps 의 item class 를 기기 쪽 상호작용 `IPM.SkypeTeams.Message.ConnectedAIApp.Connector.<AppName>` 과 브라우저 쪽 상호작용 `IPM.SkypeTeams.Message.CloudAIApp.SaaS.<AppID>` 로 나눠 적습니다[5]. Windows 앱에서 한 대화가 어느 쪽으로 들어가는지는 문서에 없으므로, 조직 검체에서 두 item class 를 모두 검색합니다.

AppLocker 규칙은 실행을 막으므로[1], 규칙이 걸린 기간에 실행 흔적이 있으면 규칙이 실제로 적용된 시점과 그 사용자에게 적용됐는지를 다시 맞춰 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** 앱의 대화 파일 형식은 공개된 자료가 없어서, 여기서는 정책 값을 헥스로 읽는 법만 봅니다. 아래는 만든 예시입니다. 레지스트리 편집 도구나 하이브 헥스 보기에서 `TurnOffWindowsCopilot` 의 데이터가 `01 00 00 00` 이면 리틀 엔디언 정수 1, 곧 "끔" 입니다. `CopilotKey` 키 아래 문자열 값은 UTF-16LE 로 적혀 있어서, CSP 예시 AUMID 라면 데이터가 아래처럼 시작합니다.

```text
만든 예시 — "Microsoft." 를 UTF-16LE 로 적은 바이트
4D 00 69 00 63 00 72 00 6F 00 73 00 6F 00 66 00 74 00 2E 00
M     i     c     r     o     s     o     f     t     .
```

`Microsoft.MicrosoftOfficeHub` 로 이어지면 회사용 앱, `Microsoft.Copilot` 으로 이어지면 소비자용 앱을 가리킵니다.

**공개 도구로 한 번.** 디스크 이미지에서는 사용자마다 NTUSER.DAT 를 레지스트리 뷰어(예: Registry Explorer)로 열어 위 정책 키와 마이크 권한 키를 보고, 각 키의 마지막 기록 시각을 적습니다. 파일 시스템에서는 `%LOCALAPPDATA%\Packages\` 아래 `Microsoft.Copilot_` 로 시작하는 폴더를 찾아 시각과 안의 폴더 구성을 기록합니다. KapeFiles 에는 이 앱 전용 수집 항목(target)이 없고, 이름이 비슷한 `Targets/Windows/WindowsCopilotRecall.tkape` 는 Recall 폴더 `C:\Users\*\AppData\Local\CoreAIPlatform.00\UKP\` 만 모읍니다(2026-09-18 커밋 기준)[8]. 그래서 앱 폴더는 수집 목록에 따로 넣습니다.

살아 있는 PC 에서는 관리 문서에 나오는 명령으로 설치 여부를 읽습니다[1]. 이 명령은 문서의 제거 스크립트 첫 줄이지만, 여기서는 읽기에만 씁니다.

```powershell
# 설치된 Copilot 앱 패키지를 읽기만 한다(지우지 않는다)
Get-AppxPackage -Name "Microsoft.Copilot"
```

결과의 패키지 버전과 설치 폴더를 기록하고, 같은 명령을 `Microsoft.MicrosoftOfficeHub` 로 한 번 더 돌려 회사용 앱이 함께 있는지 봅니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 |
|---|---|
| [계정 데이터 내보내기](export.md) | 서버에 남은 프롬프트·응답 |
| 브라우저 방문 기록([크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html)) | Entra 계정 로그인 시도로 열린 `m365.cloud.microsoft/chat` |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 앱이 서비스와 통신한 시간대 |
| [Microsoft Purview로 본 Copilot 기록](../../network-enterprise/purview-copilot.md) | 수집 정책이 있는 조직에서 남은 프롬프트·응답 |
| [Recall](../../windows-ai/recall.md) | Recall 을 켠 PC 라면 Copilot 창이 찍힌 스냅숏 |
| [기기에서 AI 흔적 모으기](../../../03-techniques/acquisition/endpoint-triage.md) | 앱 폴더와 정책 키를 함께 모으는 순서 |

## 실습

시험용 Windows 11 PC 와 개인 Microsoft 계정으로 직접 만든 검체에서 다음을 풀어 봅니다.

1. 한 번도 열지 않은 기본 설치 상태와, 로그인해 대화한 뒤의 상태에서 `Microsoft.Copilot_` 패키지 폴더는 무엇이 달라지는가?
2. 웹 내용 보기로 링크를 몇 개 연 뒤, 대화와 함께 저장된 탭 목록이 패키지 폴더 안에 남는가, 남는다면 어느 파일인가?
3. 설정에서 Copilot 키 대상 앱을 바꾸면 NTUSER.DAT 의 어느 키가 바뀌는가? 정책 키 `CopilotKey` 와는 어떻게 다른가?
4. 음성 대화를 한 번 한 뒤 `ConsentStore\microphone\Microsoft.Copilot_8wekyb3d8bbwe` 키 아래에 어떤 값이 생기는가?

## 참고 문헌

1. Microsoft Learn, "Updated Windows and Microsoft Copilot Chat experience" (ms.date 2025-11-20, 갱신 2026-08-18) — https://learn.microsoft.com/en-us/windows/client-management/manage-windows-copilot
2. Microsoft Learn, "Policy CSP - WindowsAI" (ms.date 2026-09-10, 갱신 2026-09-23) — https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-windowsai
3. Microsoft Support, "Getting started with Copilot on Windows" (ms.date 2026-08-17) — https://support.microsoft.com/en-us/microsoft-copilot/getting-started-with-copilot-on-windows
4. Microsoft Learn, "Learn about retention for Copilot and AI apps" (ms.date 2025-09-23, 갱신 2026-06-25) — https://learn.microsoft.com/en-us/purview/retention-policies-copilot
5. Microsoft Learn, "Search for and delete AI application data in eDiscovery" (ms.date 2026-06-19, 갱신 2026-06-29) — https://learn.microsoft.com/en-us/purview/edisc-search-copilot-data
6. Microsoft Store, "Microsoft Copilot on Windows" — https://apps.microsoft.com/detail/9NHT9RB2F4HD
7. pl4nty/intune-change-tracking — https://github.com/pl4nty/intune-change-tracking , `DCv2/Settings/device_vendor_msft_policy_config_windowsai_removemicrosoftcopilotapp.json` (2026-07-13 커밋)
8. EricZimmerman/KapeFiles — https://github.com/EricZimmerman/KapeFiles , `Targets/Windows/WindowsCopilotRecall.tkape`
9. memstechtips/Winhance — https://github.com/memstechtips/Winhance , `src/Winhance.Core/Features/Optimize/Models/PrivacyOptimizations.cs`
