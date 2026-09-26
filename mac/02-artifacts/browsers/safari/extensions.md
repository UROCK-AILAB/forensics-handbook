---
title: "확장 (Safari Extensions)"
parent: "사파리"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1200
---

# 확장 (Safari Extensions)

사파리는 설치한 확장의 목록과 켜짐 여부를 `Extensions.plist` 에 적어 두고, Safari 14 이후에는 앱 확장 방식과 웹 확장 방식의 목록을 샌드박스 컨테이너 안에 따로 두어서, 이 계정의 사파리에 어떤 확장이 들어와 켜져 있었는지를 브라우저 쪽에서 확인할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

확장 (Extension) 은 사파리에 기능을 더하는 작은 프로그램이고, 목록 파일에는 확장마다 켜짐 여부가 들어 있습니다 [2]. 켜고 끄는 순간 바로 파일에 쓰는지는 실제 기기로 확인해야 합니다. 확장은 Mac App Store 나 확장을 담은 앱에서 오고, 사파리 설정에서 체크 상자로 켜고 끄며, "제거 (Uninstall)" 를 누르거나 확장을 담은 앱을 지우면 제거됩니다 [1]. 확장마다 웹사이트에 얼마나 접근할지도 도구 막대 버튼에서 고르는데 [1], 목록 파일의 `WebsiteAccess` 키가 이 설정과 관련된 값으로 보입니다 [2]. 이 키는 사전이고, 안의 키와 값이 무엇을 뜻하는지는 알려져 있지 않습니다 [2].

개발자 쪽에서 보면 Safari 웹 확장 (Safari Web Extension) 은 앱 확장 (app extension) 으로 만들어 Mac 앱 안에 넣어 배포하고, App Store 로 내보냅니다 [3]. 크롬·파이어폭스·엣지 확장은 Xcode 에 들어 있는 명령줄 도구 `safari-web-extension-converter` 로 바꿀 수 있고, 이 방식은 macOS 의 Safari 14 이상에서 씁니다 [3]. 그래서 확장의 실체는 목록 파일이 아니라 앱 번들 안의 `.appex` 이고, 목록은 `/Applications` 의 앱과 함께 봅니다. `.appex` 가 앱 번들 안 어느 경로에 들어가는지는 앱 번들을 직접 열어 확인합니다.

설정 파일에는 설정 창에서 마지막으로 고른 확장을 적는 `LastExtensionSelectedInPreferences` 키가 있습니다 [2]. 설정 파일의 위치와 다른 키는 허브 [사파리 (Safari)](index.md)에서 다룹니다.

## 위치와 버전별 차이

옛 방식과 Safari 14 이후 방식은 목록 파일이 다릅니다 [2].

| 구분 | 파일 | 확장마다 읽는 키 | 출처 |
|---|---|---|---|
| 옛 방식 (`.safariextz`) | `~/Library/Safari/Extensions/` 폴더와 그 안의 `Extensions.plist` | `Enabled`, `Apple-signed`, `Archive File Name` | [2][4] |
| Safari 14 이후 앱 확장 | `~/Library/Containers/com.apple.Safari/Data/Library/Safari/AppExtensions/Extensions.plist` | `Enabled`, `WebsiteAccess` | [2] |
| Safari 14 이후 웹 확장 | `~/Library/Containers/com.apple.Safari/Data/Library/Safari/WebExtensions/Extensions.plist` | `Enabled`, `WebsiteAccess` | [2] |

옛 방식의 폴더는 `~/Library/Safari/Extensions/` 이고 [4], 옛 목록은 `~/Library/Safari/Extensions/Extensions.plist` 입니다 [2]. Safari 14 이후 목록은 샌드박스 컨테이너 쪽 사파리 폴더에 있습니다 [2]. 기본 프로필은 위 표의 경로를 쓰고, Safari 17 프로필이 따로 있으면 `SafariTabs.db` 의 프로필 행에서 읽은 `server_id` 값을 폴더 이름으로 끼워 `.../Safari/<server_id>/AppExtensions/Extensions.plist` 처럼 프로필마다 찾습니다 [2]. 프로필 행을 찾는 법은 [탭과 세션 (Tabs·Sessions)](tabs-sessions.md)에서 다룹니다. 옛 사파리 폴더에 `AppExtensions`·`WebExtensions` 가 생기는 버전이 있는지는 알려져 있지 않아서, 두 사파리 폴더를 모두 살펴봅니다.

위의 확장 사용 방식은 macOS 10.15 Catalina 부터 macOS 27 까지에 해당합니다 [1]. 프로필마다 목록이 따로 있으니 켜짐 상태도 프로필마다 따로 적힐 수 있습니다 [2]. 개인 정보 보호 창에서 따로 켜지는지는 실제 기기로 확인해야 합니다.

## 구조

두 방식 모두 plist 이고, 읽는 법 자체는 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에서 다룹니다. 아래 그림은 mac_apt 가 읽는 키로 만든 것이라 [2], 실제 파일에는 키가 더 있을 수 있습니다.

```text
옛 방식: Extensions/Extensions.plist
 └ Installed Extensions (배열)
    └ 확장 항목 (사전)
       ├ Enabled              켜짐 여부
       ├ Apple-signed         Apple 서명 여부(이름으로 본 뜻)
       └ Archive File Name    .safariextz 파일 이름

Safari 14 이후: AppExtensions/Extensions.plist, WebExtensions/Extensions.plist
 └ 최상위 사전의 키 하나가 확장 하나 (키 = mac_apt 가 확장 이름으로 쓰는 값)
    ├ Enabled                 켜짐 여부
    └ WebsiteAccess           웹사이트 접근 설정 (사전, 안의 키·값 뜻은 확인 못 함)
```

Safari 14 이후 파일의 최상위 키가 확장의 번들 ID 인지 표시 이름인지는 알려져 있지 않아서, 실제 파일의 값을 보고 판단합니다.

## 증거로서 의미

**증명하는 것.** 목록에 항목이 있으면 파일을 마지막으로 저장한 때 이 계정의 사파리에 그 확장이 등록돼 있었고, `Enabled` 로 켜져 있었는지 꺼져 있었는지를 알 수 있습니다 [2]. 옛 방식에서는 `Archive File Name` 으로 설치한 `.safariextz` 파일 이름을, `Apple-signed` 로 서명 표시를 볼 수 있습니다 [2]. 사고 대응에서는 모르는 확장이 켜져 있는지, 웹사이트 접근 설정이 넓게 잡혀 있는지를 먼저 봅니다.

**증명하지 못하는 것.** 목록의 키에는 시각 값이 없어서 언제 설치했는지, 언제 켜고 껐는지는 이 목록만으로 알 수 없습니다. 켜져 있었다는 기록으로는 확장이 어느 사이트에서 무엇을 했는지 알 수 없고, 확장이 실제로 동작했다는 증거도 되지 않습니다. 확장을 제거하면 목록에서 항목이 어떻게 되는지 알려져 있지 않아서, 목록에 없다고 해서 설치한 적이 없다고 쓰지 않습니다. 보고서에는 "이 계정의 사파리 웹 확장 목록에 이 확장이 켜진 상태로 적혀 있다" 처럼 씁니다.

## 시각 해석

목록 파일 안에는 시각 키가 없습니다 [2]. 그래서 시간 정보는 `Extensions.plist` 자체의 파일 시각, 확장을 담은 앱이 설치된 시각, 파일 시스템 변경 기록에서 따로 구해야 하는데, 어느 쪽이 설치 시각과 맞는지는 정해져 있지 않아 여러 기록을 함께 놓고 봅니다. 파일 시각을 읽는 법은 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md), 변경 기록은 [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)에서 다룹니다.

## 함정과 한계

**목록만 보고 끝내지 않습니다.** 확장은 앱과 함께 오고, 앱을 지우면 확장도 제거됩니다 [1]. 목록과 `/Applications` 의 앱을 나란히 놓아야 확장을 담은 앱이 무엇이고 지금도 있는지 알 수 있는데, 앱 번들 안의 `.appex` 경로는 앱 번들을 직접 열어 확인합니다.

**테스트용 임시 설치가 있습니다.** macOS 사파리에서는 테스트용으로 웹 확장 폴더를 임시로 설치할 수 있습니다 [3]. 이렇게 넣은 확장이 디스크와 설정에 어떤 흔적을 남기는지는 알려져 있지 않아서, 목록에 없는 확장이 동작했을 가능성을 목록만으로 지우지 않습니다.

**여러 위치를 모두 봅니다.** 옛 목록과 Safari 14 이후 목록은 다른 폴더에 있고, 프로필이 여럿이면 프로필마다 목록이 따로 있습니다 [2]. 기본 프로필 폴더 하나만 보고 "확장 없음" 으로 적으면 틀릴 수 있습니다.

## 직접 분석해 보기

사본을 macOS 에서 `plutil -p Extensions.plist` 로 열면 키와 값을 사람이 읽을 수 있는 모양으로 볼 수 있습니다. 아래 파이썬 예는 옛 방식과 Safari 14 이후 파일을 구분하지 않고 `Enabled` 키가 있는 사전을 모두 찾아 그 위치와 함께 출력하고, mac_apt 가 읽는 키만 골랐습니다 [2].

```python
import plistlib, sys

KEYS = ("Enabled", "WebsiteAccess", "Apple-signed", "Archive File Name")

def walk(node, path="/"):
    if isinstance(node, dict):
        if "Enabled" in node:
            print(path, {k: node.get(k) for k in KEYS if k in node})
        for k, v in node.items():
            walk(v, f"{path}{k}/")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]/")

with open(sys.argv[1], "rb") as f:
    walk(plistlib.load(f))
```

Safari 14 이후 파일에서는 출력의 경로 부분 첫 항목이 확장을 가리키는 최상위 키이므로, 그 값을 확장을 담은 앱의 번들 ID 와 맞춰 봅니다. 번들 ID 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../../01-foundations/value-decoding/bundle-team-id.md)에서 다룹니다. 공개 도구로는 mac_apt 의 사파리 플러그인이 옛 방식과 Safari 14 이후 목록을 함께 읽습니다 [2]. 도구가 읽지 않는 키가 있는지 `plutil -p` 출력과 한 번 비교해 봅니다.

## 교차 검증

| 함께 볼 것 | 이유 |
|---|---|
| [설치한 앱과 영수증 (Applications·Receipts)](../../system-account/installed-apps-receipts.md) | 확장을 담은 앱이 언제 어디서 설치됐는지 |
| [앱 번들 정보 (Info.plist·Code Signature)](../../embedded-metadata/app-bundle.md) | 앱 번들 안의 확장과 서명 |
| [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../../01-foundations/protection/codesign-notarization-sip.md) | 확장을 담은 앱의 서명 확인 |
| [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md) | 목록 파일과 앱이 바뀐 때 |
| [방문 기록 (History.db)](history.md) | 확장이 켜진 뒤 방문한 사이트 |
| [악성 코드는 어디서 들어왔나 (Initial Access)](../../../04-scenarios/incident/initial-access.md) | 수상한 확장의 유입 경로를 따지는 순서 |

## 실습

공개 맥 시험 이미지에서 사파리 폴더와 컨테이너 쪽 사파리 폴더를 뒤져 아래 질문을 풀어 봅니다.

1. `Extensions`, `AppExtensions`, `WebExtensions` 폴더 가운데 어느 것이 있고, 각각 어느 경로(프로필 폴더 포함)에 있는가
2. 목록에 적힌 확장은 몇 개이고, 그 가운데 `Enabled` 가 켜진 것은 무엇인가
3. 목록의 확장마다 그 확장을 담은 앱을 `/Applications` 에서 찾을 수 있는가
4. 설정 파일의 `LastExtensionSelectedInPreferences` 값은 목록의 어느 확장과 맞는가

## 참고 문헌

1. Apple Support, Safari 사용 설명서(Mac) — Use Safari extensions on your Mac — https://support.apple.com/guide/safari/use-safari-extensions-sfri32508/mac
2. mac_apt Safari 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/safari.py
3. Apple Developer, Safari web extensions (문서 JSON) — https://developer.apple.com/tutorials/data/documentation/safariservices/safari-web-extensions.json
4. ForensicArtifacts 정의 파일 webbrowser.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
