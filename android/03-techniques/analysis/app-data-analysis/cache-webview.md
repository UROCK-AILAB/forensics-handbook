---
title: "캐시와 웹뷰"
parent: "앱 데이터 분석"
grand_parent: "기법 · 분석"
nav_order: 1390
---

# 캐시와 웹뷰 (Cache·WebView)

앱의 캐시 폴더와 WebView 데이터 폴더에서 앱이 받아 온 콘텐츠와 앱 안에서 연 웹 페이지의 흔적을 찾고, 그 흔적으로 무엇을 알 수 있고 무엇을 알 수 없는지 구분하는 방법입니다.

## 언제 쓰나

앱 자체의 DB 에는 남지 않은 이미지·웹 페이지·응답을 찾을 때 씁니다. 앱 안에 WebView 를 품은 앱은 브라우저가 아니어도 자기 폴더에 웹 방문 기록과 HTTP 캐시를 남길 수 있고, 아래에서 보듯 공개 도구도 그런 기록을 찾아 앱 이름으로 보여 줍니다. 앱 폴더 전체를 살펴보는 순서는 [처음 보는 앱 분석 순서](unknown-apps.md), 브라우저 앱 자체는 [크롬 (Chrome for Android)](../../../02-artifacts/browsers/chrome/index.md) 과 [삼성 인터넷 (Samsung Internet)](../../../02-artifacts/browsers/samsung-internet.md) 페이지에서 다룹니다.

## 캐시의 성격

앱은 캐시 파일을 `cacheDir` 로 얻은 폴더에 두고, 외부 저장소 쪽 캐시는 `externalCacheDir` 를 씁니다 [1]. 내부 저장 공간이 부족하면 Android 가 캐시 파일을 지울 수 있고, 앱이 쓸 수 있는 캐시 크기는 `StorageManager.getCacheQuotaBytes()` 로 확인합니다 [1]. 그래서 캐시에 남은 항목은 시스템이 아직 지우지 않은 것일 뿐이고, 캐시에 없는 URL 은 그 URL 을 받은 적이 없다는 증거가 되지 않습니다 [2]. 캐시는 무엇이 있었는지 보여 줄 수는 있어도, 무엇이 없었는지를 보여 주지는 못합니다.

## WebView 데이터 폴더

ALEAPP 의 chrome.py 는 Chromium 계열 방문 기록 DB 를 아래 경로 패턴으로 찾습니다 [3].

```
*/app_chrome/Default/History*
*/app_sbrowser/Default/History*
*/app_opera/History*
*/app_webview/Default/History*
```

`app_webview` 경로에서 찾은 기록은 경로 속 `<패키지>/app_webview/Default` 의 패키지 폴더 이름을 브라우저 이름 자리에 넣어 보여 주고 [3], 그래서 WebView 기록은 그 WebView 를 품은 앱 이름으로 나옵니다. `app_sbrowser` 경로의 기록은 ALEAPP 가 'Browser' 라는 이름을 붙입니다 [3]. `getDir()` 로 만든 하위 폴더의 조상은 늘 `ApplicationInfo.dataDir` 이고 [1], `app_webview` 같은 `app_` 로 시작하는 폴더도 이 방식으로 생긴 것으로 보입니다.

History DB 는 브라우저와 같은 Chromium 형식이라서, 방문 URL 은 `urls`, 방문 한 번 한 번은 `visits`, 내려받기는 `downloads` 와 `downloads_url_chains`, 검색어는 `keyword_search_terms` 표에 있습니다 [3]. 옛 DB 에는 `downloads` 표의 `tab_url`, `last_access_time` 열이 없을 수 있습니다 [3]. 표와 열의 자세한 해석은 [크롬 (Chrome for Android)](../../../02-artifacts/browsers/chrome/index.md) 페이지에 있고, 시각 값은 1601-01-01 UTC 부터 흐른 마이크로초(WebKit 시각)이며 [2][3] 옮기는 공식은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다. WebView 의 쿠키·Local Storage·IndexedDB 파일 경로는 실제 기기에서 확인하고, IndexedDB 형식은 [LevelDB와 IndexedDB](../../../01-foundations/data-formats/leveldb-indexeddb.md) 페이지를 봅니다.

## HTTP 캐시 구조 (Chromium Simple Cache)

### 어디에 있나

ALEAPP 의 chromiumHttpCache 모듈이 읽는 캐시 폴더는 앱 종류마다 다릅니다 [2].

| 앱 종류 | ALEAPP 가 읽는 폴더 |
|---|---|
| 브라우저 (Chrome, Samsung Internet, Brave, Cromite, Edge 등) | `cache/Cache/Cache_Data` |
| Opera | `cache/cache` |
| WebView 로 화면을 그리는 DuckDuckGo | `cache/WebView/<프로필>/HTTP Cache/Cache_Data` |

ALEAPP 시험 이미지에서는 `cache/Cache/Cache_Data` 모양을 브라우저만 썼고, WebView 를 품은 앱은 `cache/WebView` 아래에 캐시를 두었습니다 [2]. 이 모듈은 DuckDuckGo 가 아닌 앱의 `cache/WebView` 는 읽지 않아서 [2], 다른 앱의 WebView 캐시는 분석가가 직접 찾아 형식을 확인한 뒤 읽습니다.

### 파일 구성

항목 파일의 이름은 16진수 16자리 뒤에 `_0` 이나 `_1` 이 붙은 모양입니다 [2]. `_0` 파일은 아래 순서로 적힙니다(Chromium `net/disk_cache/simple/simple_entry_format.h`) [2].

| 순서 | 부분 | 내용 |
|---|---|---|
| 1 | SimpleFileHeader | magic `0xfcfb6d1ba7725c30`, 버전, key 길이, key 해시 |
| 2 | key | 캐시 키 문자열 |
| 3 | stream 1 | 응답 본문 |
| 4 | EOF 기록 | stream 1 의 끝 |
| 5 | stream 0 | 직렬화한 응답 정보(HttpResponseInfo) |
| 6 | key 의 SHA-256 | 있을 때만 |
| 7 | 두 번째 EOF 기록 | magic `0xf4fa6f45970d41d8`, flags, CRC, stream 크기 |

`_1` 파일은 같은 머리 뒤에 stream 2 를 담습니다 [2]. SimpleFileHeader 와 EOF 기록은 모두 리틀 엔디언 24바이트(8바이트 magic 뒤에 4바이트 필드 네 개, 마지막 필드는 채움)이고, 두 번째 EOF 기록의 flags 에 key SHA-256 표시 비트가 켜져 있을 때만 32바이트 해시가 붙습니다 [2]. 헥스로 따라갈 때는 파일 끝의 EOF 기록부터 거꾸로 읽어 stream 0 의 위치를 잡습니다.

stream 0 은 flags 로 시작하고, flags 의 31번 비트가 켜져 있으면 추가 flags 가 이어집니다. 그 뒤에 요청 시각과 응답 시각이 1601-01-01 UTC 부터 흐른 마이크로초로 적히고, 추가 flags 의 2번 비트가 켜져 있으면 원래 응답 시각이 하나 더 붙은 다음, NUL 로 나뉜 응답 헤더가 옵니다 [2]. 본문(stream 1, stream 2)은 서버가 보낸 그대로라서 `Content-Encoding` 이 적용된 상태, 곧 압축된 상태일 수 있습니다 [2]. 본문을 열어 볼 때는 stream 0 의 응답 헤더에서 인코딩을 먼저 확인합니다.

key 는 `credential_key/post_key/[isolation_key]url` 모양입니다. 세 번째 부분이 `_dk_` 로 시작하면 마지막 공백 뒤가 URL 이고 그 앞은 네트워크 격리 키입니다(Chromium `net/http/http_cache.cc` 의 `GenerateCacheKey`) [2].

### 색인 파일

`index-dir/the-real-index` 파일에는 항목마다 해시·마지막 사용 시각·크기가 있고, 캐시를 마지막으로 고친 시각도 함께 적힙니다. magic 은 `0x656e74657220796f` 이고, ALEAPP 시험 이미지에서 버전은 9 였습니다 [2]. 색인이 가리키는 항목 수와 실제 `_0` 파일 수는 다를 수 있고(색인을 적은 뒤 항목이 늘거나 지워진 경우), 시험 이미지의 색인 55개 가운데 5개가 달랐습니다 [2].

## 절차

1. **캐시 폴더와 WebView 폴더를 통째로 확보합니다.** 캐시는 저장 공간이 부족하면 지워질 수 있어서 [1], 켜져 있는 기기라면 되도록 일찍 확보합니다. 확보 방식은 [모바일 증거 확보 (Acquisition)](../../acquisition/mobile-acquisition/index.md) 페이지를 봅니다.
2. **앱마다 캐시 모양을 구분합니다.** 위 표처럼 브라우저형(`cache/Cache/Cache_Data`)인지 WebView 형(`cache/WebView` 아래)인지 보고, `index-dir/the-real-index` 와 `_0`·`_1` 파일이 있으면 `_0` 파일 앞머리의 magic 을 확인해 Simple Cache 인지 확인합니다.
3. **색인과 항목 파일을 따로 셉니다.** 색인에 있는 해시 수와 `_0` 파일 수를 비교해 차이를 적어 둡니다.
4. **항목마다 key·응답 시각·응답 헤더를 뽑습니다.** key 에서 URL 을, stream 0 에서 응답 시각과 헤더를 얻고, 색인이 있으면 마지막 사용 시각을 붙입니다.
5. **본문은 필요한 항목만 풉니다.** 응답 헤더의 인코딩대로 풀고, 이미지나 문서가 나오면 파일 형식을 따로 확인합니다.
6. **History DB 와 맞춰 봅니다.** 같은 앱 폴더에 WebView 의 History DB 가 있으면 방문 기록과 캐시 응답 시각을 한 시간 축에 올리고, 방법은 [타임라인 작성 (Timeline)](../timeline/index.md) 에 있습니다.

## 도구

ALEAPP 는 chrome.py 로 History DB 를, chromiumHttpCache.py 로 Simple Cache 를 읽습니다 [2][3]. 폴더 목록에는 exoplayerCaches.py(동영상 재생 캐시), imagemngCache.py, cachelocation.py, browserCachechrome.py, browserCachefirefox.py 같은 캐시 관련 모듈도 있습니다 [4]. 이미지 로딩·통신 라이브러리가 만드는 캐시 폴더는 [처음 보는 앱 분석 순서](unknown-apps.md) 대로 형식부터 구분합니다.

## 함정과 한계

ALEAPP 시험 이미지에서 캐시 항목 147,256개 가운데 stream 0 이 빈 항목이 28개, EOF 기록 없이 끝나 건너뛴 파일이 5개, 색인이 없어 마지막 사용 시각을 구하지 못한 항목이 19,826개였습니다 [2]. 항목 수가 많아도 모든 항목에 시각이 붙지는 않아서, 결과표에 시각이 빈 항목은 빈 채로 두고 이유를 적습니다.

ALEAPP 가 WebView 캐시를 DuckDuckGo 것만 읽는다는 점을 잊으면, 다른 앱의 WebView 캐시가 도구 결과에 없다는 이유로 없다고 잘못 볼 수 있습니다 [2]. 브라우저 이름도 도구가 경로에서 붙인 것입니다. chrome.py 는 경로에 `brave`, `microsoft`, `opera`, `android.chrome` 이 들어 있는지를 `app_webview` 보다 먼저 검사해서, 예를 들어 패키지 이름에 `microsoft` 가 들어간 앱의 WebView 기록에는 앱 이름 대신 Edge 가 붙습니다 [3]. 그래서 보고서에는 도구가 붙인 이름 대신 경로 속 패키지 폴더 이름을 적습니다.

## 결과를 어떻게 해석하나

캐시 항목은 그 URL 을 응답 시각에 받아 왔거나 다시 확인(재검증)했다는 기록이고, 페이지가 화면에 표시됐다는 뜻은 아닙니다 [2]. 캐시는 방문 기록이 아니라서 [2], 사용자가 그 페이지를 봤는지는 History DB 나 [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) 같은 다른 기록과 맞춰 본 만큼만 말합니다. 웹 사용 전체를 재구성하는 흐름은 [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md) 페이지에 있습니다.

> `(패키지 이름)` 앱의 WebView HTTP 캐시에 `(URL)` 항목이 있고, 응답 시각은 (시각) UTC 입니다. 이 항목은 앱이 그 시각에 해당 URL 의 응답을 받았거나 재검증했다는 기록이며, 화면에 표시됐는지는 이 기록만으로 알 수 없습니다.

## 참고 문헌

1. Access app-specific files — Android Developers, https://developer.android.com/training/data-storage/app-specific
2. ALEAPP chromiumHttpCache.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chromiumHttpCache.py
3. ALEAPP chrome.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chrome.py
4. ALEAPP scripts/artifacts 폴더 목록(GitHub API) — https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
