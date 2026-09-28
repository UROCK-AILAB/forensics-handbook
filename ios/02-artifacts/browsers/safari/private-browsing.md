---
title: "개인 정보 보호 브라우징"
parent: "사파리"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 760
---

# 개인 정보 보호 브라우징 (Private Browsing)

개인 정보 보호 브라우징에서 연 페이지는 History.db 에 남지 않지만, 개인 정보 보호 탭 자체는 SafariTabs.db 에 남을 수 있어서 이 모드를 썼다는 흔적과 열려 있던 탭의 URL 을 찾을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

개인 정보 보호 브라우징(Private Browsing) 때 사파리는 방문한 페이지, 검색 기록, 자동 완성 정보를 기억하지 않고[1], 이 모드에서 방문한 사이트는 History.db 에 저장되지 않습니다(iOS 15 기준)[2]. 그러나 개인 정보 보호 탭은 SafariTabs.db 에 남고[2][3], BrowserState.db 의 `tabs` 표에도 `private_browsing` 열이 있습니다[4].

iOS 17·iPadOS 17 부터는 잠긴 개인 정보 보호 브라우징(Locked Private Browsing)이 생겼습니다[1]. 아이폰에서는 사파리가 앞에서 실행되지 않을 때, 개인 정보 보호 모드에서 다른 모드로 바꿀 때, 기기가 잠길 때 개인 정보 보호 창이 잠기고, 웹페이지를 불러오지 않았거나 소리·영상이 재생 중이면 잠기지 않습니다[1]. 설정은 설정 → 앱 → Safari → 개인 정보 보호 및 보안의 "Face ID(또는 Touch ID)로 개인 정보 보호 브라우징 잠금 해제" 항목입니다[1]. 기본값은 실제 기기에서 확인합니다.

## 위치와 버전별 차이

| iOS 버전 | 흔적이 남는 곳 | 출처 |
|---|---|---|
| iOS 15 | History.db 에는 남지 않고 SafariTabs.db 에 개인 정보 보호 탭이 남습니다 | [2] |
| iOS 16 | SafariTabs.db 의 `parent` 값으로 개인 정보 보호 탭이 나뉘었고, 바이옴 SEGB 파일에는 처음부터 쓰이지 않는 것으로 보였습니다 | [3] |
| iOS 17 이후 | 잠긴 개인 정보 보호 브라우징이 생겼습니다 | [1] |

탭 DB 의 위치와 구조는 [탭과 세션 (Tabs)](tabs.md)에서 다룹니다. 암호화하지 않은 백업에는 SafariTabs.db 와 BrowserState.db 가 없어서, 이런 백업만으로는 개인 정보 보호 탭을 볼 수 없습니다.

## 구조

개인 정보 보호 탭을 가려내는 기준은 자료마다 다르게 적혀 있습니다.

| 기준 | 내용 | 출처 |
|---|---|---|
| 조상 폴더 제목 | SafariTabs.db `bookmarks` 에서 조상 폴더의 `title` 이 대소문자와 상관없이 `private` 또는 `privatepinned` 인 탭이 개인 정보 보호 탭입니다 | [4] |
| `parent` 값 | iOS 16 기기 한 대에서 `parent` 가 12 인 행이 개인 정보 보호 모드 탭이었습니다. 고정값인지는 실제 데이터로 확인합니다 | [3] |
| `private_browsing` 열 | BrowserState.db `tabs` 에 있는 열입니다 | [4] |

`parent` 의 숫자는 기기마다 다를 수 있어서, 숫자보다 폴더 행의 `title` 을 먼저 보는 편이 안전합니다. 이름이 `privatepinned` 인 폴더는 이름으로 짐작하면 개인 정보 보호 모드의 고정 탭으로 보이지만, 이름만으로 뜻을 단정할 수는 없습니다.

사파리 설정 plist 에는 생체 인증·암호와 이어진 이름의 키가 있습니다. AppDomain-com.apple.mobilesafari `Library/Preferences/com.apple.mobilesafari.plist` 의 `BiometricAuthenticationIsAvailable`(bool), `BiometricAuthenticationTypeIfAvailable`(int), `PasscodeIsAvailable`(bool) 이지만, 이 키들만으로 잠긴 개인 정보 보호 브라우징을 설정했는지 판단할 수는 없습니다. 같은 파일의 `WBSPrivacyProxyAvailabilitySubscriberTier`, `WBSPrivacyProxyAvailabilityAccountType`, `WBSPrivacyProxyAvailabilityServiceStatus`, `WBSPrivacyProxyAvailabilityActiveOnDefaultNetwork` 는 이름으로 짐작하면 사설 릴레이와 이어진 키라서, 개인 정보 보호 브라우징을 판단하는 데 쓰지 않습니다.

## 증거로서 의미

**증명하는 것.** SafariTabs.db 에서 개인 정보 보호 폴더 아래에 탭 행이 있으면, 수집 시점에 그 URL 의 개인 정보 보호 탭이 사파리에 저장되어 있었다는 사실을 보여 줍니다[2][4]. 사용자가 개인 정보 보호 모드를 썼다는 흔적이 되고, 방문 기록에 없는 URL 을 찾는 길이 되기도 합니다.

**증명하지 못하는 것.** 개인 정보 보호 모드의 방문은 History.db 에 남지 않아서[2] 그 탭에서 몇 페이지를 거쳤는지, 언제 처음 열었는지는 방문 기록으로 알 수 없습니다. 이미 닫은 개인 정보 보호 탭이 남는다고 볼 수 없으므로, 탭 DB 에 없다고 이 모드를 쓰지 않았다고 말할 수도 없습니다. 잠긴 개인 정보 보호 브라우징의 설정 여부도 plist 키로 판단할 수 없습니다.

보고서에는 "수집 시점에 SafariTabs.db 의 개인 정보 보호 탭 묶음에 이 URL 의 탭이 저장되어 있었다" 처럼 씁니다.

## 시각 해석

개인 정보 보호 탭에도 일반 탭과 같은 열과 이진 속성이 있어서, 마지막으로 본 시각은 [탭과 세션 (Tabs)](tabs.md)의 시각 해석 절과 같은 방식으로 바꿉니다. 방문 기록이 남지 않아서 이 모드를 언제 썼는지는 주로 탭의 시각으로 추정하게 되고, 바꾼 결과가 수집 시각보다 앞인지 꼭 확인합니다.

## 함정과 한계

- iOS 15 도구 비교에서 한 상용 도구는 탭 정보를 읽었지만 개인 정보 보호 탭을 개인 정보 보호 모드가 아니라고 잘못 표시했습니다[2]. 도구가 붙인 표시를 그대로 옮기지 말고 폴더 제목과 `private_browsing` 값을 직접 봅니다.
- `parent` 가 12 라는 기준은 iOS 16 기기 한 대의 값이라[3] 다른 기기에 그대로 쓰지 않습니다.
- 바이옴 SEGB 파일에는 개인 정보 보호 탭의 기록이 처음부터 쓰이지 않는 것으로 보입니다(iOS 16 기준)[3]. 바이옴에 없다고 이 모드를 쓰지 않았다고 보지 않습니다.

## 직접 분석해 보기

SafariTabs.db 사본을 sqlite3 로 열고, 먼저 개인 정보 보호 폴더 행을 찾습니다.

```sql
SELECT id, parent, title FROM bookmarks
WHERE lower(title) IN ('private', 'privatepinned');
```

그다음 그 폴더 아래로 내려가며 모든 탭을 모읍니다. iLEAPP 처럼 조상 폴더 제목으로 판정하는 방식을[4] 재귀 질의로 옮긴 예입니다.

```sql
WITH RECURSIVE sub(id) AS (
  SELECT id FROM bookmarks WHERE lower(title) IN ('private', 'privatepinned')
  UNION
  SELECT b.id FROM bookmarks b JOIN sub ON b.parent = sub.id
)
SELECT b.id, b.parent, b.title, b.url, b.order_index,
       length(b.local_attributes) AS la_len
FROM bookmarks b JOIN sub ON b.id = sub.id
WHERE b.url IS NOT NULL
ORDER BY b.parent, b.order_index;
```

BrowserState.db 가 있으면 `SELECT title, url, last_viewed_time FROM tabs WHERE private_browsing = 1;` 로 개인 정보 보호 탭 후보를 보되, 이 열의 값이 1 일 때 개인 정보 보호 탭이라는 뜻은 같은 기기의 SafariTabs.db 결과와 맞춰 확인합니다. 공개 도구로는 iLEAPP 의 사파리 탭 모듈이 같은 판정을 하므로[4] 직접 모은 탭 수와 비교합니다.

> 그림 자리: SafariTabs.db `bookmarks` 표에서 `private`·`privatepinned` 폴더 행 아래로 개인 정보 보호 탭 행이 이어지는 모양

## 교차 검증

같은 URL 이 [방문 기록 (History.db)](history.md)에 없는지 확인하면 개인 정보 보호 모드에서만 연 페이지를 가려낼 수 있습니다. 바이옴의 사파리 스트림은 [바이옴 (Biome)](../../app-usage/biome/index.md)에서 다루고, 조사 흐름은 [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md)과 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)를 따릅니다.

## 실습

직접 만든 시험 기기나 NIST CFReDS 같은 곳에 공개된 iOS 시험 데이터로 아래를 풀어 봅니다.

1. 개인 정보 보호 모드에서 탭 두 개를 열어 둔 채 수집하고, SafariTabs.db 에서 두 탭이 어느 폴더 아래에 있는지 찾습니다.
2. 1번 탭의 URL 이 History.db 에 있는지 확인합니다.
3. 그 데이터의 `parent` 값이 iOS 16 기기의 값(12)과 같은지 비교합니다.
4. 도구 하나로 같은 데이터를 읽어 개인 정보 보호 탭 표시가 직접 찾은 결과와 맞는지 확인합니다.

## 참고 문헌

1. Apple 지원, "How to use Locked Private Browsing in Safari" — https://support.apple.com/en-us/105028
2. iOS 15 Image Forensics Analysis and Tools Comparison - Native Apps (blog.digital-forensics.it, 2023-10) — https://blog.digital-forensics.it/2023/10/ios-15-image-forensics-analysis-and.html
3. D20 Forensics, "iOS 16 - Breaking Down the Biomes (Part 4) - Surfin' with Safari" (2022-09-28) — https://blog.d204n6.com/2022/09/ios-16-breaking-down-biomes-part-4.html
4. iLEAPP `scripts/artifacts/safariTabs.py` (abrignoni/iLEAPP, main) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/safariTabs.py
