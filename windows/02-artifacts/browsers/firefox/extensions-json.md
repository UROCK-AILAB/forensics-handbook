---
title: "확장 프로그램 (extensions.json)"
parent: "파이어폭스"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1780
---

# 확장 프로그램 (extensions.json)

파이어폭스는 프로필에 설치한 확장 프로그램 (Extension) 을 비롯한 추가 기능 (Add-on) 목록을 `extensions.json` 에 JSON 으로 적어 두며, 추가 기능마다 식별자, 판, 켜짐·꺼짐 상태, 설치·갱신 시각, 권한 정보가 남고 파이어폭스 밖에서 설치한 추가 기능인지도 따로 표시합니다.

## 무엇을 기록하나 · 왜 생기나

파이어폭스는 설치한 추가 기능의 정보를 데이터베이스로 관리하며, 이 데이터베이스의 JSON 파일 이름은 `extensions.json` 입니다(`FILE_JSON_DB`)[1]. 파일 맨 위에는 `schemaVersion` 과 `addons` 가 있고, `addons` 는 추가 기능 목록을 담은 배열입니다. 스키마 버전은 설정 `extensions.databaseSchema` 에도 적히고, 추가 기능마다 저장하는 필드는 `PROP_JSON_FIELDS` 목록이 정합니다[1]. 악성 확장은 브라우저 안에서 방문 페이지를 엿보거나 바꿀 수 있어서 침해 조사에서 확장 목록을 봅니다.

## 위치와 버전별 차이

- 파일은 프로필 폴더에서 찾습니다. 프로필 폴더를 찾는 법은 [프로필 구조 (profiles.ini·prefs.js)](profiles-ini-prefs-js.md) 에서 다룹니다.
- 본 폴더와 로컬 폴더 중 어느 쪽에 있는지는 실제 데이터에서 확인합니다.
- 아래 필드 목록은 파이어폭스 소스 main 가지(2026-09-23 기준)의 것입니다[1]. 예전 출시판에 어느 필드가 있었는지는 실제 데이터에서 확인합니다.
- 분석을 시작할 때 `schemaVersion` 값을 먼저 적어 둡니다. 도구 결과가 이상하면 이 값부터 봅니다.
- 추가 기능 파일 자체가 어느 폴더에 어떤 이름으로 저장되는지는 실제 프로필 폴더에서 확인합니다.

## 구조

### 필드 목록

`PROP_JSON_FIELDS` 에 있는 필드는 아래와 같습니다[1].

`id`, `syncGUID`, `version`, `type`, `loader`, `updateURL`, `installOrigins`, `manifestVersion`, `optionsURL`, `optionsType`, `optionsBrowserStyle`, `aboutURL`, `defaultLocale`, `visible`, `active`, `userDisabled`, `appDisabled`, `embedderDisabled`, `pendingUninstall`, `installDate`, `updateDate`, `applyBackgroundUpdates`, `path`, `skinnable`, `sourceURI`, `releaseNotesURI`, `softDisabled`, `foreignInstall`, `strictCompatibility`, `locales`, `targetApplications`, `targetPlatforms`, `signedState`, `signedTypes`, `signedDate`, `seen`, `dependencies`, `incognito`, `userPermissions`, `optionalPermissions`, `requestedPermissions`, `icons`, `iconURL`, `blocklistAttentionDismissed`, `blocklistState`, `blocklistURL`, `startupData`, `previewImage`, `hidden`, `installTelemetryInfo`, `recommendationState`, `rootURI`

### 먼저 볼 필드

| 필드 | 뜻 |
|---|---|
| `id` | 추가 기능의 식별자입니다 |
| `version` | 추가 기능의 판입니다 |
| `type` | 추가 기능의 종류입니다. 들어가는 값은 실제 데이터에서 확인합니다 |
| `active` | 지금 켜져 돌아가는지입니다 |
| `userDisabled` | 사용자가 껐는지입니다 |
| `appDisabled` | 프로그램이 껐는지입니다. 호환되지 않거나 서명이 없거나 차단 목록에 올랐을 때 꺼집니다 |
| `softDisabled` | 차단 목록의 약한 차단으로 꺼졌는지입니다 |
| `foreignInstall` | 파이어폭스 밖에서 설치했는지입니다 |
| `visible` | 같은 `id` 가 여럿일 때 우선하는 판인지입니다 |
| `installDate` | 설치 시각입니다 |
| `updateDate` | 갱신 시각입니다 |
| `signedState` | 서명 상태입니다 |
| `signedDate` | 서명 시각입니다 |

아래 필드는 뜻을 설명한 공개 자료가 없어 이름으로 짐작한 뜻만 적습니다. 실제 값을 보고 판단합니다.

| 필드 | 이름으로 짐작한 뜻 |
|---|---|
| `sourceURI` | 추가 기능 파일을 받아 온 주소 |
| `path`·`rootURI` | 추가 기능 파일의 위치 |
| `userPermissions`·`optionalPermissions`·`requestedPermissions` | 추가 기능이 쓰거나 요청한 권한 |
| `incognito` | 사생활 보호 창에서 돌아가는지 |
| `pendingUninstall` | 삭제를 기다리는 중인지 |

### `signedState` 의 이름

서명 상태에는 `SIGNEDSTATE_SYSTEM`, `SIGNEDSTATE_PRIVILEGED`, `SIGNEDSTATE_SIGNED`, `SIGNEDSTATE_NOT_REQUIRED` 같은 이름이 있습니다[1]. 이름마다 어떤 숫자 값인지는 공개 자료가 없습니다.

### 설치 위치 이름

파이어폭스는 추가 기능을 설치한 위치를 아래 이름으로 나눕니다[1].

| 이름 | 뜻 |
|---|---|
| `app-profile` | 사용자 프로필 |
| `app-builtin` | 파이어폭스에 내장된 것 |
| `app-system-addons` | 시스템 추가 기능 |
| `app-temporary` | 임시로 설치한 것 |
| `app-system-share`·`app-system-local` | 유닉스 계열의 시스템 공용 위치 |

- 이 이름은 각 항목의 `location` 필드에 들어갑니다. `PROP_JSON_FIELDS` 목록에는 없지만 저장할 때(`toJSON()`) 설치 위치 이름을 `location` 으로 덧붙입니다.
- `location` 이 `app-profile` 이 아닌 항목은 사용자 프로필 밖에서 온 추가 기능입니다.
- Windows 레지스트리로 설치하는 위치의 이름과 그 레지스트리 경로는 실제 기기에서 확인합니다.

## 증거로서 의미

### 증명하는 것

- 항목이 있으면 파이어폭스가 이 파일을 쓸 때 그 추가 기능이 이 프로필에 등록돼 있었습니다.
- `installDate`·`updateDate` 는 설치·갱신 무렵을 가리킵니다. 다만 파이어폭스가 시작할 때 새로 찾아낸 추가 기능은 두 필드에 추가 기능 파일의 수정 시각을 넣습니다. 이때는 실제 설치 시각과 다를 수 있습니다.
- `foreignInstall` 이 참이면 파이어폭스 밖에서 설치한 추가 기능입니다. 다른 프로그램이 확장을 심은 경우를 가릴 때 `location` 과 함께 먼저 봅니다.
- `active`·`userDisabled`·`appDisabled` 로 파일을 쓴 시점의 켜짐·꺼짐 상태와 끈 주체를 구분합니다.

### 증명하지 못하는 것

- 사용자가 직접 설치했다는 것은 증명하지 못합니다. 내장·시스템 추가 기능도 목록에 오릅니다.
- `foreignInstall` 은 파이어폭스 밖에서 설치했다는 표시일 뿐입니다. 어느 프로그램이나 사람이 설치했는지는 알려 주지 않습니다.
- 추가 기능이 언제 실제로 돌았는지, 무엇을 했는지는 알 수 없습니다.
- 지운 추가 기능이 이 파일에 남는지는 알려져 있지 않습니다. 목록에 없다고 설치한 적이 없다고 단정하지 않습니다.
- 키보드 앞의 사람이 누구인지는 알 수 없습니다.

보고서에는 "악성 확장을 설치했다" 대신 "이 프로필의 `extensions.json` 에 `id` X, 판 Y 인 항목이 있다. `foreignInstall` 은 true 이고 `installDate` 는 Z(UTC) 이다. 파일을 쓴 시점에 `active` 는 true 였다" 처럼 씁니다.

## 시각 해석

- `installDate`·`updateDate`·`signedDate` 는 1970년 1월 1일 00:00 UTC 부터 센 밀리초입니다[1].
- 실제 데이터에서 [$MFT](../../filesystem/mft.md) 의 파일 시각과 맞춰 이 단위를 확인합니다.
- 시작할 때 새로 찾아낸 추가 기능은 `installDate`·`updateDate` 에 파일 수정 시각을 넣습니다. 이 값은 실제 설치 시각과 다를 수 있습니다.
- [places.sqlite](places-sqlite.md) 같은 SQLite 파일의 시각은 대부분 마이크로초입니다. 이 파일은 밀리초이므로 섞어 읽지 않습니다.
- `active` 같은 상태 필드에는 시각이 붙지 않습니다. 상태는 이 파일을 마지막으로 쓴 무렵의 것입니다.
- 이 파일의 마지막 수정 시각은 파이어폭스가 목록을 마지막으로 다시 쓴 때입니다.
- 변환은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다. 여러 기록을 한 시간 축에 놓을 때는 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 을 따릅니다.

## 함정과 한계

- **원본 프로필로 브라우저를 켜지 않습니다.** 파이어폭스를 켜면 추가 기능 상태와 이 파일이 바뀔 수 있습니다. 해시를 기록한 사본으로 분석합니다.
- **밀리초와 마이크로초를 섞지 않습니다.** 밀리초 값을 마이크로초로 나누면 1970년 1월 무렵의 엉뚱한 날짜가 나옵니다.
- **상태 필드의 뜻을 판마다 확인합니다.** 위 뜻은 최신 판 기준입니다. 옛 판에서 같은 필드의 뜻이 같은지 실제 데이터에서 확인합니다.
- **내장·시스템 추가 기능을 사용자 설치로 오해하지 않습니다.** 목록에는 사용자가 설치하지 않은 추가 기능도 있습니다.
- **이름만 보고 정상 확장이라고 판단하지 않습니다.** 널리 쓰는 확장과 이름이 같아 보여도 `id`, 서명 상태, 받아 온 주소를 따로 봅니다.
- **이 파일 하나로 끝내지 않습니다.** 추가 기능과 관련한 파일이 이것 말고도 있을 수 있습니다. 프로필 폴더에서 추가 기능 이름이나 `id` 가 든 파일을 따로 찾습니다.

## 직접 분석해 보기

### 텍스트로 한 번

`extensions.json` 은 텍스트 JSON 이므로 헥스 대신 텍스트로 읽습니다. 아래는 위 필드 목록으로 만든 예시입니다. 실제 데이터에서 나온 값이 아닙니다. 값이 판마다 다른 필드는 `…` 로 둡니다.

```json
{
  "schemaVersion": …,
  "addons": [
    {
      "id": "example@example.org",
      "version": "1.0",
      "type": …,
      "active": true,
      "userDisabled": false,
      "appDisabled": false,
      "foreignInstall": true,
      "location": "app-profile",
      "installDate": 1706788800000,
      "updateDate": 1706788800000,
      "signedState": …
    }
  ]
}
```

```
installDate = 1706788800000 (밀리초)
1706788800000 ÷ 1,000 = 1706788800 초 (1970-01-01 부터)
→ 2024-02-01 12:00:00 UTC

같은 값을 마이크로초로 잘못 읽으면:
1706788800000 ÷ 1,000,000 = 1706788.8 초
→ 1970-01-20 18:06:28 UTC (틀린 날짜)
```

### 공개 도구로 한 번

사본으로 뜬 `extensions.json` 을 JSON 처리 도구 jq 로 읽는 예입니다.

```
jq -r '.addons[] | [.id, .version, .location, .active, .userDisabled, .appDisabled, .foreignInstall,
  ((.installDate // 0) / 1000 | floor | todate),
  ((.updateDate  // 0) / 1000 | floor | todate)] | map(tostring) | @tsv' extensions.json
```

- `installDate` 를 1,000 으로 나눠 1970년 기준 초로 바꾼 뒤 UTC 시각으로 적습니다.
- 값이 비어 있는 필드는 `1970-01-01T00:00:00Z` 로 나옵니다. 이런 행은 원본 값을 따로 봅니다.
- 어느 JSON 뷰어로 열어도 같은 필드를 볼 수 있습니다. 도구가 시각을 어떻게 변환했는지 위 결과와 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 방문·다운로드·즐겨찾기 | `installDate` 무렵에 추가 기능 배포 페이지를 열거나 파일을 내려받았는지 봅니다 | [places.sqlite](places-sqlite.md) |
| $MFT·$UsnJrnl | 추가 기능 파일과 이 파일을 만들고 고친 시각을 봅니다 | [$MFT](../../filesystem/mft.md), [$UsnJrnl](../../filesystem/usnjrnl.md) |
| 설치 프로그램 | `foreignInstall` 확장과 같은 무렵에 설치한 프로그램을 봅니다 | [설치 프로그램](../../system-account/uninstall.md) |
| 프로그램 실행 흔적 | 같은 무렵에 실행한 설치 파일을 봅니다 | [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md) |
| 크롬 계열 확장 | 같은 확장을 다른 브라우저에도 설치했는지 봅니다 | [크롬 계열 브라우저](../chrome-edge-whale/index.md) |

브라우저 확장을 심어 자리를 잡는 수법은 [악성코드 지속성(자동실행) 찾기](../../../04-scenarios/incident/persistence.md) 에서 다른 자동실행 위치와 함께 봅니다.

## 실습

파이어폭스를 쓴 공개 실습 데이터(NIST CFReDS 등)에서 프로필 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. `schemaVersion` 은 몇입니까? 추가 기능은 모두 몇 개입니까?
2. `foreignInstall` 이 true 인 항목이 있습니까? 그 항목의 `location` 은 무엇입니까? 그 `installDate` 무렵에 설치한 프로그램은 무엇입니까?
3. `active` 가 false 인 항목을 골라 `userDisabled` 와 `appDisabled` 중 어느 쪽이 참인지 봅니다. 누가 끈 것입니까?
4. `installDate` 를 UTC 시각으로 바꿔 시간순으로 늘어놓습니다. 방문 기록에서 같은 무렵의 페이지를 찾아봅니다.

## 참고 문헌

1. Mozilla, *XPIDatabase.sys.mjs* (파이어폭스 소스, main 가지 — 파일 이름, 최상위 키, 필드 목록, 설치 위치 이름과 `location` 필드, 상태 필드, 서명 상태 이름, 시각 단위, 새로 찾은 추가 기능의 날짜를 파일 수정 시각으로 넣는 코드). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/toolkit/mozapps/extensions/internal/XPIDatabase.sys.mjs
