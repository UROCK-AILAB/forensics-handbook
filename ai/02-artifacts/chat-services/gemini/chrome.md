---
title: "Chrome 통합"
parent: "Gemini"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 320
---

# Chrome 통합 (Gemini in Chrome)

Chrome 에 들어간 Gemini 는 도구 모음의 "Ask Gemini" 버튼으로 열고 현재 탭 내용을 써서 답하는 기능이라서, 대화는 계정의 활동 기록으로 가고 기기에는 Chrome 설정 파일 속 `glic` 로 시작하는 키 같은 흔적이 남을 수 있습니다.

`glic` 키 이름은 Chrome 버전에 따라 바뀔 수 있습니다.

## 무엇이 남나 · 왜 생기나

도움말은 이 기능을 Chromebook Plus, Mac, Windows 에서 쓸 수 있다고 적었고, 최신 Chrome 과 Chrome 로그인이 필요하며 시크릿 모드에서는 쓸 수 없다고 안내합니다. 13세 이상이어야 하고, 18세 미만은 Gemini Live 와 자동 탐색 (auto browse), 마이크·자막 권한을 쓸 수 없습니다. 설정에서 단축키를 켜면 단축키로도 열 수 있습니다. 현재 탭은 기본으로 공유되고 열린 탭은 최대 10개까지 공유할 수 있으며, Workspace 페이지를 공유하면 Gemini 가 Workspace 계정에 바로 접근할 수 있다고 적었습니다.

개인정보 안내는 이 기능이 현재 탭의 페이지 내용과 URL 을 모은다고 적었습니다. 페이지 내용은 잠시 기록되고 Gemini 앱 활동에는 나오지 않지만, 활동 저장 (Keep Activity) 이 켜져 있으면 대화는 활동에 저장됩니다. 그래서 활동 목록에서 대화는 볼 수 있어도 그때 Gemini 가 읽은 페이지 내용까지 볼 수 있다고 기대하지 않습니다. 보관 기간과 삭제 규칙은 [Gemini](index.md) 허브에 있고, 브라우저에 들어간 AI 기능을 제품끼리 견준 내용은 [브라우저에 들어간 AI](../../office-integrations/browser-builtin-ai.md)에서 다룹니다.

## 위치와 구조 — Chromium 소스로 본 설정 키

Chromium 은 이 기능을 안에서 "glic" 라고 부르고, 설정 키 이름을 `chrome/browser/glic/glic_pref_names.h` 파일에 모아 정의합니다. 키는 설치 전체에 하나인 Local State 파일에 들어가는 것과 프로필마다 있는 Preferences 파일에 들어가는 것으로 나뉩니다. 두 파일의 위치와 JSON 구조는 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html)와 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)에서 다룹니다.

| 파일 | 소스에 정의된 키(예) | 짐작할 수 있는 뜻 |
|---|---|---|
| Local State | `glic.launcher_enabled`, `glic.launcher_hotkey`, `glic.hotkey_global_scope_enabled`, `glic.selection_hotkey`, `glic.focus_toggle_hotkey` | 실행 단추와 단축키 설정 |
| Preferences | `glic.pinned_to_tabstrip`, `glic.geolocation_enabled`, `glic.microphone_enabled`, `glic.tab_context_enabled`, `glic.default_tab_context_enabled` | 탭 줄 고정, 위치·마이크·탭 내용 사용 설정 |
| Preferences | `glic.user_status`(사전), `glic.window.last_dimissed_time`(시각), `glic.previous_bounds.x`, `glic.previous_bounds.y`, `glic.zoom_level` | 사용자 상태, 창을 마지막으로 닫은 때, 창 위치와 확대 비율 |
| Preferences | `glic.closed_captioning_enabled`, `glic.media_understanding_enabled`, `glic.shake_trigger_enabled`, `glic.previously_not_allowed`, `glic.marketing_auto_open_count`, `glic.promotion_source_cohort`, `sync.glic_rollout_eligibility` | 자막·미디어 이해·흔들기 실행 설정, 안내 표시와 배포 대상 여부 |
| Preferences(관리 정책이 넣음) | `glic.spark_policy_settings`, `glic.actuation_on_web`, `glic.file_upload_allowed`, `glic.actuation_on_web_allowed_for_urls`, `glic.actuation_on_web_blocked_for_urls`, `glic.gemini_enterprise_settings` | 웹 조작 허용 범위, 파일 올리기 허용, 기업 설정 |
| Preferences | `glic.partition_needs_cookie_sync`, `glic.local_storage_copied_to_main_partition` | 저장 공간 관련 상태 |

표는 소스에 있는 키 가운데 일부만 골랐고, 오른쪽 칸은 키 이름에서 짐작한 뜻입니다. 각 키를 언제 쓰고 바꾸는지는 시험용 프로필에서 설정을 바꿔 보며 확인합니다. `glic.window.last_dimissed_time` 의 `dimissed` 는 소스에 적힌 철자 그대로입니다. 마지막 줄의 두 키는 이름으로 짐작하면 Gemini 창이 따로 떨어진 저장 공간 (partition) 을 쓴 적이 있다는 뜻이고, 그 저장 공간의 폴더 위치는 검체의 프로필 폴더에서 확인합니다.

기업 관리 정책도 있습니다. 정의 파일 `components/policy/resources/templates/policy_definitions/GenerativeAI/GeminiSettings.yaml` 은 제목이 "Settings for Gemini integration" 인 정수 선택형 정책이고, 0 은 허용(기본값), 1 은 사용 안 함입니다. 설정하지 않으면 GenAiDefaultSettings 정책을 따르고, 지원은 Windows·macOS Chrome 137, iOS 139, ChromeOS 144, Android 149 부터입니다. Windows 에서 이 정책 값이 레지스트리 어디에 적히는지는 검체의 정책 키에서 확인합니다.

## 증거로서 의미

**증명하는 것.** 프로필의 Preferences 에 `glic` 키가 있고 값이 기본값과 다르면, 그 프로필에서 해당 설정이 바뀐 적이 있다고 쓸 수 있습니다. 관리 정책으로 들어가는 키나 GeminiSettings 정책 값이 있으면 조직이 이 기능을 허용했는지 막았는지 판단할 근거가 됩니다.

**증명하지 못하는 것.** 설정 키는 대화 내용을 담지 않아서, 무엇을 물었는지는 계정 활동 기록에서 확인해야 합니다. 어떤 키가 있다는 사실만으로 사용자가 Gemini 창을 연 적이 있다고 쓸 수 없는데, Chrome 이 기본값이나 배포 대상 여부를 스스로 적었을 수도 있기 때문입니다. Gemini 가 읽은 탭의 페이지 내용은 활동 목록에 나오지 않아서 어느 페이지를 읽혔는지는 방문 기록과 맞춰 짐작할 뿐입니다.

## 시각 해석

소스에서 시각 값으로 정의된 키는 `glic.window.last_dimissed_time` 이고, 이름대로라면 Gemini 창을 마지막으로 닫은 때입니다. 이 값이 Preferences 파일에 어떤 형식으로 적히는지, UTC 인지 현지 시각인지는 검체에서 창을 닫은 시각과 맞춰 확인합니다. 마지막 한 번만 남는 값이라서 이전 사용 시각은 여기서 알 수 없고, Preferences 파일은 다른 설정이 바뀔 때도 다시 쓰여서 파일 수정 시각을 Gemini 사용 시각으로 읽지 않습니다.

## 함정과 한계

키 이름은 2026-09 main 브랜치 기준이고, 분석할 기기의 Chrome 버전에서는 없거나 이름이 다를 수 있습니다. 시크릿 모드에서는 이 기능을 쓸 수 없어서 시크릿 창의 흔적을 찾을 이유는 없지만, 같은 사람이 일반 창의 Gemini 와 [웹 브라우저](web.md)의 gemini.google.com 을 번갈아 썼을 수 있어서 두 흔적을 함께 봅니다. 자동 탐색처럼 브라우저를 대신 조작하는 기능의 흔적은 [브라우저를 조작하는 AI](../../agentic-services/browser-agents.md)에서 다룹니다.

## 직접 분석해 보기

Preferences 와 Local State 는 JSON 텍스트 파일이라서 헥스보다 텍스트 편집기나 공개 도구 jq 로 여는 편이 쉽습니다. Chrome 설정 파일은 점으로 나눈 키 이름을 JSON 안의 겹친 객체로 적어서, `glic.window.last_dimissed_time` 은 `glic` 객체 안의 `window` 객체 안에서 찾습니다. 아래는 명세(소스의 키 이름)를 보고 만든 예시이고 값은 모두 지어낸 것이라, 실제 파일의 값 형식과 다를 수 있습니다.

```json
{
  "glic": {
    "pinned_to_tabstrip": true,
    "microphone_enabled": false,
    "tab_context_enabled": true,
    "zoom_level": 0,
    "window": {
      "last_dimissed_time": "(만든 예시 값)"
    }
  }
}
```

jq 로는 프로필 폴더의 Preferences 사본에서 `jq '.glic' Preferences` 처럼 `glic` 객체만 뽑아 볼 수 있습니다. 여러 프로필이 있으면 프로필마다 따로 확인하고, 설치 전체 설정은 Local State 에서 같은 방식으로 봅니다.

## 교차 검증

| 함께 볼 기록 | 알려 주는 것 | 링크 |
|---|---|---|
| 계정 데이터 내보내기 | 대화 내용과 메시지 시각 | [계정 데이터 내보내기](export.md) |
| Chrome 방문 기록 | Gemini 에 공유했을 법한 탭의 주소와 시각 | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html) |
| 보안 제품 기록 | 기업 환경에서 AI 기능 사용을 막거나 남긴 기록 | [보안 제품이 남기는 AI 사용 기록](../../network-enterprise/dlp-casb.md) |
| 허용되지 않은 AI 사용 조사 | 정책과 실제 사용 흔적을 맞춰 보는 흐름 | [회사가 허용하지 않은 AI를 썼나](../../../04-scenarios/data-leak/shadow-ai.md) |

## 실습

시험용 계정과 Chrome 으로 검체를 직접 만들어 아래 질문을 풀어 봅니다.

1. Gemini 를 한 번도 열지 않은 프로필과 한 번 연 프로필의 Preferences 에서 `glic` 객체는 어떻게 다릅니까?
2. Gemini 창을 닫은 뒤 `glic.window.last_dimissed_time` 값은 어떤 형식으로 적히고, 창을 닫은 시각과 맞습니까?
3. 탭 공유를 끈 뒤 `glic.tab_context_enabled` 값이 바뀝니까?

## 참고 문헌

1. Use Gemini in Chrome - Computer - Google Chrome Help — https://support.google.com/chrome/answer/16283624 (2026-09-25 열람)
2. Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961 (2026-09-25 열람)
3. Chromium glic_pref_names.h — https://raw.githubusercontent.com/chromium/chromium/main/chrome/browser/glic/glic_pref_names.h (2026-09-25 열람)
4. Chromium 정책 정의 GeminiSettings.yaml — https://raw.githubusercontent.com/chromium/chromium/main/components/policy/resources/templates/policy_definitions/GenerativeAI/GeminiSettings.yaml (2026-09-25 열람)
