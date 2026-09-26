---
title: "브라우저에 들어간 AI"
parent: "아티팩트 · 업무 도구 속 AI"
nav_order: 540
---

# 브라우저에 들어간 AI (Edge Copilot·Chrome Gemini 등)

## 한 줄 요약

Edge 의 Copilot 과 Chrome 의 Gemini·내장 AI 는 브라우저 안에서 도는 AI 기능이고, 기기에 남는 흔적은 대화 본문이 아니라 Edge 의 페이지 접근 정책 값, Edge 프로필의 Copilot 로그인 캐시, Chrome 온디바이스 모델의 설치 흔적입니다.

확인 날짜는 2026-09입니다. 아래 경로와 이름은 검체에서 한 번 더 맞춰 봅니다.

## 무엇을 기록하나 · 왜 생기나

브라우저에 들어간 AI 는 사용자가 보고 있는 페이지를 AI 에 넘길 수 있다는 점이 핵심입니다. Edge 사이드 패널의 Copilot 이 페이지 내용에 접근할지는 관리자 정책으로 정할 수 있고, 이 정책 값이 레지스트리나 macOS 설정에 남습니다. Workspace 사용자의 Gemini in Chrome 은 선택한 탭의 URL 과 페이지 내용을 모아 처리하고, 허락 없이 도메인 밖 사람 검토나 학습에 쓰지 않습니다[5].

Chrome 의 내장 AI 는 이와 달리 모델(Gemini Nano)을 기기에 내려받아 기기 안에서 돌립니다. 모델을 내려받으려면 조건이 맞아야 하고, 내려받은 모델은 Chrome 의 구성요소로 설치됩니다. 그래서 대화 내용보다는 "이 기기에 온디바이스 모델이 있었는가" 가 먼저 확인할 거리가 됩니다.

브라우저 자체의 방문 기록·캐시·프로필 구조는 Windows 판의 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html) 페이지에서 다루고, 여기서는 되풀이하지 않습니다. 브라우저를 직접 조작하는 에이전트형 기능은 [브라우저를 조작하는 AI](../agentic-services/browser-agents.md)에서 다룹니다.

## 위치와 버전별 차이

### Edge 의 Copilot 페이지 접근 정책

`CopilotPageContext` 정책은 Edge 사이드 패널의 Copilot 이 페이지 내용에 접근할지를 정합니다. Windows·macOS 의 Edge 124 이상에서 지원하고 Android·iOS 는 지원하지 않습니다. 프로필 단위 (Per Profile) 정책이고, Entra ID 프로필에만 적용되며 개인 Microsoft 계정(MSA) 프로필에는 적용되지 않습니다.

| OS | 위치 | 이름 | 값 형식 |
|---|---|---|---|
| Windows | 레지스트리 `SOFTWARE\Policies\Microsoft\Edge` (필수 정책 경로만 있고 권장 정책 경로는 없음) | `CopilotPageContext` | `REG_DWORD` (예: `0x00000001`) |
| macOS | 설정 (Preference Key) | `CopilotPageContext` | `<true/>` 형식 |

Windows 관리 템플릿은 `MSEdge.admx` 입니다. 정책을 설정하지 않으면 EU 밖에서는 기본 허용, EU 안에서는 기본 차단이고, 사용자가 Edge 설정에서 켜고 끌 수 있습니다. 사용자가 Edge 설정에서 바꾼 값이 프로필의 `Preferences` 파일에 어떤 키로 남는지는 공개 문서에 없으므로, 시험용 기기에서 설정을 바꾸기 전과 뒤의 파일을 비교해 찾습니다.

기업 데이터 보호 (EDP) 를 쓰는 Copilot 의 페이지 접근은 이 정책이 아니라 `EdgeEntraCopilotPageContext` 가 정합니다. `CopilotPageContext` 를 끄면 `M365LinksAutoOpenCopilotEnabled` 기능도 함께 꺼집니다. 업무 계정으로 Edge 사이드바에서 쓴 Copilot 은 Purview 감사에서 `AppHost` 값 `Edge` 또는 `Bing` 으로 남고, 이 레코드는 [Microsoft 365 Copilot](m365-copilot.md) 페이지에서 다룹니다.

### Edge 프로필의 Copilot 로그인 캐시

Edge 의 Copilot 은 계정·토큰만 기기에 남기고 대화 본문은 서버에 둡니다[6]. 로그인 정보는 `%LOCALAPPDATA%\Microsoft\Edge\User Data\{profile}\Local Storage\leveldb` 에서 출처 `https://copilot.microsoft.com` 아래의 MSAL 캐시(`msal.2.*` 키, `token.keys`)에 있고, 여기에 테넌트·클라이언트 ID, 범위, `lastUpdatedAt` 이 들어 있습니다[6]. 토큰 본문은 DPAPI 로 암호화돼 있습니다. 공개 도구 AABF(v1.1.260618)로 이 캐시를 읽을 수 있고, 도구 보고서에서는 토큰 본문을 가립니다. 키 구성과 도구의 읽는 방법은 [AI 에이전트 브라우저](../agentic-services/ai-browsers.md)의 Edge 절에서 다루고, 이 쪽에서는 되풀이하지 않습니다. 대화 본문은 기기에 없으므로 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md)으로 받습니다.

### Chrome 의 내장 AI (Gemini Nano)

| 항목 | 내용 |
|---|---|
| 지원 OS | Windows 10·11, macOS 13 이상, Linux, Chromebook Plus 기기의 ChromeOS(Platform 16389.0.0 이상) |
| 저장 공간 | Chrome 프로필이 있는 볼륨에 빈 공간 22GB 이상 |
| 하드웨어 | GPU VRAM 4GB 초과, 또는 RAM 16GB 이상·CPU 4코어 이상 |
| 네트워크 | 처음 내려받을 때만 무제한·비종량 네트워크 필요 |
| 모델 삭제 | 내려받은 뒤 빈 공간이 10GB 아래로 떨어지면 기기에서 지우고, 조건이 다시 맞으면 다시 내려받음 |
| 상태 확인 화면 | `chrome://on-device-internals` (모델 크기, Broker State 탭의 오류) |
| 언어 | Chrome 149 부터 영어·스페인어·일본어·독일어·프랑스어 입출력 |

모델 구성요소가 설치되는 폴더 이름은 옛 방식의 `OptGuideOnDeviceModel`, 뒤에 공개키 16진수가 붙는 `OptGuideManifestModel`, 매니페스트 설정용 `OptimizationGuideModelsManifest` 이고, 구성요소 이름 문자열은 `"Optimization Guide Manifest Component: "` 뒤에 이름이 붙는 형태와 `"Optimization Guide On DeviceModels Manifest"` 입니다[3]. 이 폴더들은 구성요소 사용자 폴더(`DIR_COMPONENT_USER`) 아래에 생깁니다[3]. 이 기준 폴더의 OS 별 경로는 검체의 파일 목록에서 위 폴더 이름을 검색해 찾습니다.

Chrome 의 Gemini 관련 기업 정책 이름과 레지스트리 값, Gemini in Chrome 대화가 기기에 남는지는 Chrome 기업 정책 문서와 검체의 프로필 폴더로 따로 확인합니다. Workspace 계정으로 쓴 경우의 서버 쪽 보관 규칙은 [Google Workspace의 Gemini](workspace-gemini.md)에서 다룹니다.

## 구조

Windows 쪽 정책 값은 레지스트리 값 하나라서 구조가 단순합니다. `REG_DWORD` 는 32비트 정수를 리틀 엔디언 4바이트로 저장하고, 예를 들어 `0x00000001` 은 값 데이터 칸에 `01 00 00 00` 으로 들어갑니다. 레지스트리 하이브 구조와 키의 마지막 쓰기 시각은 Windows 판의 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html)과 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html) 페이지에서 이어 봅니다. macOS 쪽 설정은 속성 목록 파일로 읽고, 형식은 Mac 판의 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/data-formats/plist/index.html) 페이지에서 다룹니다.

Chrome 온디바이스 모델은 위 구성요소 폴더가 있는지부터 확인합니다. 폴더 안의 파일 구성은 검체에서 폴더 목록을 떠서 기록합니다.

## 증거로서 의미

**증명하는 것.** `CopilotPageContext` 값이 있으면 그 기기나 프로필에 Copilot 의 페이지 접근을 정하는 관리 정책이 걸려 있었다는 사실을 보여 줍니다. 정책이 없다면 기본 동작(EU 밖 허용, EU 안 차단)과 사용자 설정이 적용된다는 점까지 설명할 수 있습니다. 온디바이스 모델 구성요소 폴더가 있다면 그 기기에서 모델을 내려받은 적이 있다고 해석할 수 있습니다. 다만 이 해석은 Chromium 소스의 폴더 이름에서 끌어낸 추론이라서, 보고서에도 추론이라고 밝힙니다. Edge `Local Storage` 에 출처 `https://copilot.microsoft.com` 의 `msal.2.*` 키가 있으면 그 프로필에서 Copilot 에 로그인한 적이 있다고 볼 수 있습니다[6].

**증명하지 못하는 것.** 정책 값은 관리자가 정한 허용·차단 조건일 뿐이라서, 사용자가 실제로 Copilot 에 페이지를 넘겼는지는 보여 주지 못합니다. 개인 Microsoft 계정 프로필에는 이 정책이 적용되지 않으므로, 정책이 차단으로 걸려 있어도 개인 프로필에서의 사용까지 막혔다고 결론 내리지 않습니다. 온디바이스 모델이 있어도 어떤 사이트나 기능이 그 모델을 불렀는지, 무엇을 입력했는지는 알 수 없습니다. 반대로 모델 폴더가 없다고 쓴 적이 없다는 뜻도 아닌데, 빈 공간이 10GB 아래로 떨어지면 Chrome 이 모델을 지우기 때문입니다. 조건이 다시 맞으면 모델을 다시 내려받으므로, 폴더의 만든 시각이 처음 내려받은 시각이라고 단정하지도 않습니다.

보고서 문장은 "이 기기의 Edge 정책에 Copilot 페이지 접근 설정이 있었다" 나 "Chrome 온디바이스 모델 구성요소 이름의 폴더가 있었다" 처럼 남은 기록만큼만 씁니다.

## 시각 해석

Windows 의 정책 값에는 값마다 시각이 붙지 않고, 키 단위의 마지막 쓰기 시각(UTC)만 있습니다. 이 시각은 그 키 아래 다른 값이 바뀌어도 바뀌므로, `CopilotPageContext` 가 그 시각에 설정되었다고 단정하지 않습니다. 온디바이스 모델 폴더의 만든 시각·수정 시각은 모델을 내려받거나 갱신한 시점과 가까울 수 있지만, 구성요소 갱신 방식은 공개 문서에 나오지 않아서 참고로만 씁니다. 여러 출처를 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **정책 두 개.** Entra ID 프로필의 사이드 패널 Copilot 페이지 접근은 `CopilotPageContext`, 기업 데이터 보호를 쓰는 Copilot 은 `EdgeEntraCopilotPageContext` 가 정합니다. 하나만 보고 판단하지 않습니다.
- **프로필 단위.** 정책이 프로필 단위라서, 같은 기기라도 프로필마다 적용 여부가 다를 수 있습니다. 어느 프로필에서 쓴 기록인지 먼저 가립니다.
- **모바일.** Android·iOS 의 Edge 는 이 정책을 지원하지 않아서, 모바일 기기에서는 같은 흔적을 찾지 않습니다.
- **문서 날짜 불일치.** Chrome 내장 AI 문서는 갱신 표시가 2025-05-20 인데 본문에 Chrome 149 언급이 있어, 표시 날짜와 내용 시점이 맞지 않을 수 있습니다. 인용할 때는 확인한 날짜(2026-09)를 함께 적습니다.
- **모델 자동 삭제.** 빈 공간이 10GB 아래로 떨어지면 모델을 지우므로, 모델 폴더가 없다는 사실만으로 과거 사용을 부정하지 않습니다.

## 직접 분석해 보기

**헥스로 한 번.** 아래는 `REG_DWORD` 명세로 **만든 예시**입니다. 정책 값 `CopilotPageContext` 에 `0x00000001` 이 들어 있을 때, 레지스트리 값 데이터 칸은 이렇게 보입니다.

```
값 이름 : CopilotPageContext
값 형식 : REG_DWORD
값 데이터: 01 00 00 00        ; 리틀 엔디언 → 0x00000001
```

값 데이터를 앞에서부터 읽으면 `01 00 00 00` 이고, 뒤집어 읽어야 `0x00000001` 이 됩니다.

**공개 도구로 한 번.** Windows 이미지라면 RECmd·Registry Explorer 같은 공개 도구로 하이브를 열어 `SOFTWARE\Policies\Microsoft\Edge` 아래에 `CopilotPageContext`·`EdgeEntraCopilotPageContext` 가 있는지 찾고, 키의 마지막 쓰기 시각을 함께 적습니다. 정책 키는 기기 쪽 SOFTWARE 하이브와 사용자별 NTUSER.DAT 어느 쪽에나 있을 수 있으므로 둘 다 봅니다. Chrome 은 `chrome://on-device-internals` 화면에서 모델 크기와 상태를 확인하고, 이미지에서는 파일 목록에서 `OptGuideOnDeviceModel`·`OptGuideManifestModel` 이름을 검색합니다.

## 교차 검증

- [Microsoft 365 Copilot](m365-copilot.md) — Edge 사이드바에서 업무 계정으로 쓴 Copilot 의 감사 레코드
- [AI 에이전트 브라우저](../agentic-services/ai-browsers.md) — Edge `Local Storage` 의 Copilot MSAL 캐시를 읽는 방법
- [Google Workspace의 Gemini](workspace-gemini.md) — Workspace 계정으로 쓴 Gemini in Chrome 의 서버 쪽 보관
- [AI 서비스 도메인과 네트워크 기록](../network-enterprise/network-traces.md) — 같은 시간대의 통신, 모델을 처음 내려받은 시점
- [로컬 모델 파일](../local-ai/model-files.md) — 기기에 내려받은 모델 파일 일반
- [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md) — 정책 값과 실제 사용을 비교하는 흐름

## 실습

공개 검체(NIST CFReDS 등)를 쓸 때는 이 정책 값이나 모델 폴더가 들어 있는지 검체 설명과 파일 목록으로 먼저 확인하고, 없으면 시험용 기기에서 아래 질문을 직접 풀어 봅니다.

1. Edge 에 `CopilotPageContext` 정책을 걸고 레지스트리에서 값과 키의 마지막 쓰기 시각을 확인하고, 정책을 바꾼 뒤 시각이 어떻게 달라지는지 비교합니다.
2. 같은 기기에서 Entra ID 프로필과 개인 계정 프로필을 나란히 두고, 정책이 어느 프로필에 적용되는지 확인합니다.
3. Chrome 내장 AI 요구 조건을 만족하는 기기에서 `chrome://on-device-internals` 를 열어 모델 상태를 보고, 파일 시스템에서 구성요소 폴더가 어디에 생기는지 찾아 기록합니다.
4. 빈 공간을 10GB 아래로 줄인 뒤 모델 폴더가 사라지는지, 사라진다면 어떤 흔적이 남는지 봅니다.

## 참고 문헌

1. Microsoft Edge Browser Policy Documentation CopilotPageContext | Microsoft Learn — https://learn.microsoft.com/en-us/deployedge/microsoft-edge-browser-policies/copilotpagecontext
2. Get started with built-in AI | Chrome for Developers — https://developer.chrome.com/docs/ai/get-started
3. chromium/chromium: optimization_guide_on_device_model_installer.cc (GitHub) — https://github.com/chromium/chromium/blob/main/chrome/browser/component_updater/optimization_guide_on_device_model_installer.cc
4. Audit logs for Copilot and AI applications | Microsoft Learn — https://learn.microsoft.com/en-us/purview/audit-copilot
5. Generative AI in Google Workspace Privacy Hub — https://knowledge.workspace.google.com/admin/gemini/generative-ai-in-google-workspace-privacy-hub?hl=en
6. seturi, AI-Agent-Browser-Forensics (AABF) v1.1.260618, MIT — https://github.com/seturi/AI-Agent-Browser-Forensics. 파일: `aabf/signatures.py`(EDGE 항목), `aabf/parsing/services/edge.py`
