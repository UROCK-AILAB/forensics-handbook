# 캐시 (Cache)

> 상위 허브: [크롬 계열 브라우저 (Chrome·Edge·Whale 등)](index.md)

## 한 줄 요약

크롬 계열 브라우저는 웹에서 받은 이미지·스크립트·HTML 을 프로필 폴더의 `Cache\Cache_Data` 에 저장합니다. 항목마다 자원 URL, 응답 헤더, 받은 내용, 항목을 만든 시각, 마지막으로 쓴 시각이 남습니다. Chrome 86 부터는 키에 그 자원을 불러온 최상위 사이트도 들어갑니다. 그래서 방문 기록을 지운 PC 에서도 "어느 사이트를 열었을 때 무엇을 받았나" 를 되짚을 수 있지만, 캐시 항목은 브라우저가 자원을 받았다는 기록일 뿐 사용자가 그 화면을 봤다는 기록은 아닙니다.

## 무엇을 기록하나 · 왜 생기나

브라우저는 같은 자원을 다시 받지 않으려고 HTTP 응답을 디스크에 저장해 둡니다. 이 저장소를 HTTP 캐시 (HTTP Cache) 라고 합니다. 서버가 `Cache-Control: no-store` 로 저장을 막은 응답은 남지 않습니다.

캐시 항목 하나에는 다음이 남습니다.

- **키 (Key)**: 자원 URL 입니다. 요즘 버전은 URL 앞에 분할 정보가 붙습니다.
- **스트림 0**: 응답 헤더, 요청·응답 시각, 서버 주소입니다.
- **스트림 1**: 받은 본문입니다. 이미지·HTML·스크립트 파일 그 자체입니다.
- **항목 머리 (EntryStore)**: 항목을 만든 시각, 사용 횟수, 스트림 크기와 위치가 있습니다.
- **순위 노드 (Rankings Node)**: 마지막으로 쓴 시각이 있습니다. 브라우저는 이 값으로 오래 안 쓴 항목부터 지웁니다.

캐시 크기에는 디스크 빈 공간을 보고 정하는 상한이 있고, 상한을 넘으면 오래 안 쓴 항목부터 지웁니다 (Chromium 설계 문서). 그래서 캐시에는 최근 자원이 주로 남습니다.

저장 형식 자체(블록 파일, 주소 체계, Simple Cache)는 [캐시 형식 (Blockfile·Simple Cache)](../../../01-foundations/app-mail-data/chromium-electron-webview2/blockfile-simple-cache.md)에서 다룹니다. 이 페이지는 해석에 필요한 만큼만 짚습니다.

## 위치와 버전별 차이

경로는 프로필 폴더(`User Data\<프로필>`) 기준입니다. 브라우저마다 User Data 가 어디 있는지, 프로필 이름을 어떻게 찾는지는 [프로필 폴더와 계열 브라우저 구분](../../../01-foundations/app-mail-data/chromium-electron-webview2/user-data-profile-local-state.md)에서 다룹니다.

| 폴더 (프로필 기준) | 담는 것 | 형식 |
|---|---|---|
| `Cache\Cache_Data` | HTTP 캐시. 이 페이지의 주제입니다 | blockfile: `index`, `data_0`~`data_3`, `f_xxxxxx` |
| `Code Cache\js` · `Code Cache\wasm` | 스크립트와 WebAssembly 를 컴파일한 결과 | Simple Cache: `index`, `index-dir\the-real-index`, `<16자리 hex>_0` |
| `GPUCache` | 그래픽 셰이더 캐시 | blockfile |
| `Service Worker\CacheStorage` | 사이트가 Cache API 로 스스로 저장한 응답 | 사이트별 폴더 아래 Simple Cache 와 `index.txt` |
| `Service Worker\ScriptCache` | 서비스 워커 스크립트 | Simple Cache |

- 위 표의 폴더 이름과 형식은 Windows 11 25H2 한 대의 Chrome 153 과 Edge 151 에서 확인했습니다 (관찰). 두 브라우저가 같았습니다.
- 같은 PC 의 `Cache` 폴더 안에는 `No_Vary_Search` 폴더도 있었습니다 (관찰). 이 글은 이 폴더를 다루지 않습니다.
- `%LOCALAPPDATA%` 는 Vista 이후 `C:\Users\<사용자>\AppData\Local` 입니다. 캐시 구조는 Windows 버전보다 브라우저 버전에 따라 달라집니다.

| 구분 | 차이 | 근거 |
|---|---|---|
| 옛 버전 | HTTP 캐시 파일을 `Cache` 폴더 바로 아래에 두었습니다. 옛 검체와 옛 문서에는 이 경로가 나옵니다 | 옛 포렌식 자료 |
| 요즘 버전 | `Cache\Cache_Data` 아래에 둡니다 | 관찰 (Chrome 153·Edge 151) |
| Chrome 86 부터 | 키에 최상위 사이트와 프레임 사이트가 들어갑니다. 이것을 캐시 분할 (Cache Partitioning) 이라고 합니다 | Chrome 개발자 블로그 |
| Windows 판 형식 | 기본은 blockfile 입니다. Android 는 Simple Cache 가 기본입니다 | Chromium 설계 문서·소스 |
| 옛 엣지 (EdgeHTML)·IE | 전혀 다른 형식입니다. [쿠키·캐시 폴더 (INetCookies·INetCache)](../ie-edgehtml/inetcookies-inetcache.md)를 봅니다 | |

캐시 위치가 기본값과 다를 수 있습니다.

- 관리 정책 `DiskCacheDir` 로 캐시 폴더를 옮길 수 있습니다 (Chromium 소스 `profile_network_context_service.cc`). Chrome 정책은 `HKLM\SOFTWARE\Policies\Google\Chrome` 과 HKCU 의 같은 경로에 있습니다.
- Chromium 에는 캐시 형식을 바꾸는 실험 설정 (`DiskCacheBackendExperiment`) 이 있습니다. 소스에서 기본값은 꺼짐입니다. 그래도 형식은 폴더 안 파일 이름으로 확인합니다. `data_0` 이 있으면 blockfile, `index-dir` 와 `_0` 파일이 있으면 Simple Cache 입니다.
- Teams·Discord·Slack 같은 Electron·WebView2 앱도 Chromium 의 캐시를 씁니다. 앱 폴더 안의 캐시를 브라우저 캐시로 착각하지 않습니다. 위치는 [Electron·WebView2 앱 데이터 위치](../../../01-foundations/app-mail-data/chromium-electron-webview2/teams-discord-slack.md)를 봅니다.

## 구조

### 파일 구성

| 파일 | 내용 |
|---|---|
| `index` | 키 해시로 항목을 찾는 표입니다. 머리 0x08 에 항목 수, 0x28 에 캐시를 만든 시각이 있습니다 |
| `data_0` | 순위 노드를 담습니다. 블록 하나가 36바이트입니다 |
| `data_1` | 256바이트 블록입니다. 항목 머리와 작은 스트림을 담습니다 |
| `data_2` · `data_3` | 1KB · 4KB 블록입니다. 더 큰 스트림을 담습니다 |
| `f_xxxxxx` | 16KB 보다 큰 스트림을 따로 둔 파일입니다. 파일 머리가 없습니다 |

- 블록 파일은 8,192바이트 머리 뒤에 블록이 이어집니다. 블록 n 은 `8192 + n × 블록 크기` 에 있습니다.
- 한 항목이 가리키는 곳은 4바이트 캐시 주소 (Cache Address) 로 적힙니다. 주소를 푸는 법은 아래 "직접 분석해 보기" 에서 한 번 따라갑니다.
- 관찰한 두 브라우저의 `index` 머리 버전은 3.0, `data_1` 머리 버전은 2.0 이었습니다 (확인 범위: Chrome 153·Edge 151).

### 키 읽기

요즘 키는 이런 모양입니다. 아래 주소는 설명을 위해 만든 예입니다.

```
1/0/_dk_https://example.com https://example.com https://cdn.example.net/img/logo.png
```

Chromium 소스(`net/http/http_cache.cc`)에 적힌 키 형식은 `자격 증명 표시/업로드 번호/[분할 키]URL` 입니다.

| 부분 | 예 | 뜻 |
|---|---|---|
| 첫 숫자 | `1` | 보통 1 입니다. 쿠키 없이 보낸 요청을 따로 나누는 기능이 켜지면 그런 요청은 0 입니다 |
| 둘째 숫자 | `0` | 업로드 데이터 식별 번호입니다. POST 처럼 본문을 보낸 요청이면 0 이 아닐 수 있습니다 |
| `_dk_` | | 분할 키가 붙었다는 표시입니다 (double key) |
| `s_` · `cn_` | | 소스 상수 이름으로 `s_` 는 하위 프레임 문서, `cn_` 은 다른 사이트에서 넘어온 최상위 페이지 이동입니다 |
| 최상위 사이트 | `https://example.com` | 주소창에 떠 있던 페이지의 사이트입니다 |
| 프레임 사이트 | `https://example.com` | 자원을 부른 프레임의 사이트입니다 |
| 자원 URL | `https://cdn.example.net/img/logo.png` | 받은 자원의 주소입니다 |

- 사이트는 `scheme://등록 도메인` 단위입니다. 하위 도메인과 포트는 빠집니다 (Chrome 개발자 블로그).
- URL 의 `#` 뒷부분과 URL 안의 사용자 이름·비밀번호는 키에 넣지 않습니다 (Chromium 소스).
- 한 Chrome 153 프로필의 `data_1` 에서 키를 모아 보니 대부분 `1/0/_dk_` 로 시작했습니다. `s_`·`cn_` 이 붙은 키, 둘째 숫자가 0 이 아닌 키, `_dk_` 가 없는 키도 조금 있었습니다. Edge 151 프로필도 거의 모든 키에 `_dk_` 가 있었습니다 (확인 범위: Windows 11 25H2 한 대).
- 항목 머리 안에는 키를 159바이트까지 적습니다. 더 긴 키는 따로 저장하고 머리의 `long_key` 칸에 주소를 적습니다. 분할 키는 길어서 이런 경우가 흔합니다.

### 스트림 0 — 응답 정보

스트림 0 은 Chromium 의 Pickle 형식으로 적은 응답 정보입니다. 요즘 소스(`http_response_info.cc`)가 적는 순서는 다음과 같습니다.

1. 플래그
2. 요청 시각 (request_time)
3. 응답 시각 (response_time)
4. 첫 응답 시각 (original_response_time)
5. 응답 헤더. 상태 줄(`HTTP/1.1 200` 등)과 헤더 줄이 들어갑니다
6. 인증서와 TLS 정보
7. Vary 정보
8. 서버 주소와 포트
9. ALPN 으로 정한 프로토콜 (`h2` 등) 과 그 밖의 연결 정보

- 칸 구성은 버전마다 늘었기 때문에 이 페이지는 고정 오프셋을 적지 않습니다.
- 서버 주소는 그 자원을 받아 온 소켓의 상대 주소이며 (소스 주석), 프록시를 거쳤다면 프록시 주소일 수 있습니다.

### 스트림 1 — 본문

- 본문은 서버가 보낸 바이트 그대로입니다. 서버가 `Content-Encoding: gzip`·`br` 등으로 눌러 보냈으면 눌린 채 남습니다. 먼저 스트림 0 에서 `Content-Encoding` 을 보고 풉니다.
- 동영상처럼 일부 구간만 받은 자원은 부모 항목과 자식 항목으로 나뉘어 저장될 수 있습니다. 항목 플래그 1 은 부모, 2 는 자식입니다 (libyal 명세). 이런 자원은 파일 전체가 없을 수 있습니다.

### Code Cache 는 무엇이 다른가

`Code Cache\js` 항목은 원본 스크립트가 아니라 스크립트를 컴파일한 결과입니다.

- 키는 스크립트 URL, 그 스크립트를 쓴 사이트(origin lock), 분할 키를 `" \n"` 으로 이은 문자열입니다 (소스 `generated_code_cache.cc`). 관찰한 파일에서는 키가 `_key` 로 시작했습니다.
- 스트림 0 앞에는 응답 시각(8바이트)과 데이터 크기(4바이트)가 있습니다 (소스).
- 스크립트가 컴파일되었다는 것은 그 사이트의 스크립트가 이 프로필에서 실제로 실행 단계까지 갔다는 뜻으로 볼 수 있지만, 브라우저가 언제 컴파일 결과를 저장하는지는 버전마다 다를 수 있습니다. 이 점은 검체에서 HTTP 캐시와 함께 맞춰 봅니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 프로필의 브라우저가 이 URL 의 자원을 받아 저장했습니다 | 사용자가 그 자원이나 페이지를 화면에서 봤는지 |
| 받은 내용 그 자체. 페이지 모습을 일부 되살릴 수 있습니다 | 누가 키보드 앞에 있었는지 |
| 그 자원을 부를 때 최상위에 떠 있던 사이트 (분할 키가 있을 때) | 그 사이트를 몇 번, 언제 모두 방문했는지. 한 자원은 한 항목만 남습니다 |
| 항목을 만든 시각과 마지막으로 쓴 시각 | 캐시에 없으니 방문하지 않았다는 것 |
| 응답을 보낸 서버의 주소, 콘텐츠 형식, 서버가 적은 시각 | 사용자가 무엇을 올리거나 보냈는지. 캐시에는 응답만 남고 요청 본문은 남지 않습니다 |
| 그 시각 PC 시계와 서버 시계의 차이 (아래 시각 해석) | 파일을 내려받아 저장했는지. 다운로드는 [방문·다운로드 기록](history.md)에서 봅니다 |

사용자가 열지 않은 자원도 캐시에 남습니다.

페이지 안의 광고·추적 스크립트·다른 도메인 이미지가 함께 남고, 브라우저는 사용자가 누르기 전에 페이지를 미리 불러올 수 있습니다 (미리 로드). 확장 프로그램과 서비스 워커도 요청을 보내며, 백그라운드 탭과 세션 복원으로 다시 연 탭도 자원을 받습니다. 복원 흐름은 [세션·탭 복원](sessions.md)을 봅니다.

### 보고서 문장

아래 주소와 시각은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 A 프로필의 Chrome 캐시에 `https://cdn.example.net/img/logo.png` 항목이 있습니다. 키에 적힌 최상위 사이트는 `https://example.com` 입니다. 항목을 만든 시각은 2025-03-14 02:00:05 UTC 입니다. 이 시각 즈음 이 프로필의 브라우저가 `example.com` 사이트를 연 상태에서 이 이미지를 받은 기록이 있습니다."
- 쓰면 안 되는 문장: "사용자가 2025-03-14 11시에 example.com 에 접속해 로고 이미지를 보았습니다."

## 시각 해석

캐시의 내부 시각은 모두 1601-01-01 00:00 UTC 부터 센 마이크로초입니다. 8바이트 리틀 엔디언입니다. 흔히 WebKit 시각이라고 부르는 형식입니다. 변환은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다. 내부 시각은 그 순간의 PC 시계로 적습니다.

| 시각 | 자리 | 언제 적나 | 기준 |
|---|---|---|---|
| 캐시를 만든 시각 | `index` 머리 0x28 | `index` 파일을 새로 만들 때 | UTC, PC 시계 |
| 항목을 만든 시각 (creation_time) | 항목 머리 0x18 | 항목을 만들 때. 소스는 이 칸에 그때의 현재 시각을 넣습니다 | UTC, PC 시계 |
| 마지막 사용 시각 (last_used) | 순위 노드 0x00 | 항목을 쓸 때마다 갱신합니다 | UTC, PC 시계 |
| 순위 노드 두 번째 칸 | 순위 노드 0x08 | 옛 명세는 "마지막 수정 시각" 이라 부릅니다. 요즘 소스는 이 칸 이름을 `no_longer_used_last_modified` 로 바꿨습니다 | 판단 근거로 쓰지 않습니다 |
| 요청 시각 (request_time) | 스트림 0 | 요청을 보낼 때. 캐시 항목을 서버에 다시 확인하면 그 시각으로 바뀝니다 | UTC, PC 시계 |
| 응답 시각 (response_time) | 스트림 0 | 응답 헤더를 받을 때. 다시 확인하면 바뀝니다 | UTC, PC 시계 |
| 첫 응답 시각 (original_response_time) | 스트림 0 | 다시 확인한 것을 빼고 처음 받은 응답의 시각입니다 | UTC, PC 시계 |
| `Date` 헤더 | 스트림 0 헤더 | 서버가 응답을 만들 때 | GMT, 서버 시계 |
| `Last-Modified` 헤더 | 스트림 0 헤더 | 서버가 알려 준 자원 수정 시각입니다 | GMT, 서버 시계 |

- 요청·응답 시각의 뜻은 Chromium 소스 `http_response_info.h` 주석을 따랐습니다. 주석에는 "캐시된 응답은 마지막으로 다시 확인한 시각" 이라고 적혀 있습니다.
- 항목을 만든 시각은 "처음 받은 때" 에 가깝습니다. 요청·응답 시각은 "마지막으로 서버에 확인한 때" 에 가깝습니다. 마지막 사용 시각은 "마지막으로 캐시에서 꺼낸 때" 에 가깝습니다. 세 값을 나눠서 적습니다.
- `Last-Modified` 는 서버 쪽 파일 이야기입니다. 사용자 행위 시각이 아닙니다.
- 현지 시각으로 바꿀 때는 [시간대 설정](../../system-account/time-zone.md)을 씁니다.

### PC 시계 확인에 쓰기

응답 시각은 PC 시계로, `Date` 헤더는 서버 시계로 적습니다. 두 값은 보통 몇 초 안쪽으로 붙어 있습니다.

- 두 값이 크게 벌어지면 그때 PC 시계가 틀렸을 수 있습니다.
- CDN 이 저장해 둔 응답을 주면 `Date` 가 과거일 수 있습니다. 이때는 `Age` 헤더(초)를 더해서 비교합니다.
- 한 항목이 아니라 여러 서버의 여러 항목에서 같은 방향의 차이가 나오는지 봅니다.
- 시계 조작 여부의 판단 흐름은 [시스템 시각을 바꿨나](../../../04-scenarios/activity/anti-forensics/system-time-change.md)와 [시간대·시계 오차 보정](../../../03-techniques/analysis/timeline/time-normalization.md)을 봅니다.

## 함정과 한계

1. **캐시에 나온 URL 을 방문한 페이지로 봅니다.** 대부분은 페이지가 부른 부속 자원입니다. 사용자가 연 페이지는 분할 키의 최상위 사이트로 좁힙니다. 그래도 미리 로드한 페이지일 수 있습니다.
2. **키 전체를 URL 로 읽습니다.** `1/0/_dk_…` 를 그대로 URL 칸에 넣는 도구가 있을 수 있습니다. 최상위 사이트·프레임 사이트·자원 URL 을 나눠서 적습니다.
3. **본문이 깨졌다고 봅니다.** `Content-Encoding` 으로 눌린 채 저장된 본문일 수 있습니다. 헤더를 먼저 봅니다. 풀고 난 뒤 형식은 [파일 형식 식별](../../../03-techniques/analysis/content-search/file-signature.md)로 확인합니다.
4. **옛 문서의 "마지막 수정 시각" 칸을 씁니다.** 요즘 소스는 이 칸을 더 쓰지 않는다는 이름으로 바꿨습니다. 마지막 사용 시각과 스트림 0 의 시각을 씁니다.
5. **지운 항목이 `data_N` 안에 남아 있으리라 기대합니다.** 요즘 소스는 항목 하나를 지울 때 그 블록을 0 으로 덮습니다 (`block_files.cc` 의 `DeleteBlock`). 16KB 가 넘는 스트림은 `f_` 파일을 통째로 지웁니다. 그래서 지운 항목은 캐시 파일 안보다 파일시스템에서 찾습니다. `f_` 파일은 [$MFT](../../filesystem/mft.md)와 [비할당 영역](../../../03-techniques/analysis/data-recovery/unallocated-slack-space.md)에 흔적이 남을 수 있습니다.
6. **분석 PC 의 브라우저로 캐시 HTML 을 엽니다.** HTML 안의 링크가 외부 자원을 다시 불러옵니다. 분석 PC 의 캐시가 바뀌고 상대 서버에 접속 기록이 남습니다. 네트워크를 끊은 환경에서 텍스트나 헥스로 봅니다.
7. **실행 중인 브라우저의 캐시를 그대로 복사합니다.** 브라우저가 파일을 쓰는 중이면 복사본이 앞뒤가 안 맞을 수 있습니다. 실행 중 Chrome 의 `data_1` 을 어떤 방식은 열지 못했고 다른 방식은 읽었습니다 (관찰). 가능하면 브라우저를 닫은 뒤나 디스크 이미지에서 꺼냅니다.
8. **캐시에 없으니 그 사이트를 안 갔다고 봅니다.** `no-store` 응답, 상한을 넘어 지운 항목, 사용자가 비운 캐시, 시크릿 창이 모두 빈자리를 만듭니다.
9. **시크릿 창의 흔적을 캐시에서 찾습니다.** 시크릿 (Off-the-Record) 프로필은 HTTP 캐시를 메모리에만 둡니다 (Chromium 소스). 켜져 있는 PC 라면 [메모리 분석](../../../03-techniques/analysis/memory-forensics/index.md)으로 찾습니다. 흐름은 [시크릿 모드로 무엇을 했나](../../../04-scenarios/activity/private-browsing.md)를 봅니다.
10. **프로필 하나만 봅니다.** 캐시는 프로필마다 따로 있습니다. `Default` 말고 `Profile 1` 같은 폴더와 다른 계열 브라우저도 확인합니다.

### 지우기와 조작

- 브라우저의 "캐시된 이미지 및 파일" 삭제로 캐시 전체를 비우면, 소스는 캐시 폴더의 파일을 지우고 새로 만듭니다 (`backend_impl.cc` 의 `RestartCache`). 그래서 `index` 머리의 캐시를 만든 시각이 그 뒤 시각으로 바뀔 수 있습니다. 손상을 복구할 때도 새로 만들 수 있으니 이 값 하나로 "사용자가 지웠다" 고 쓰지 않습니다.
- 파일을 지우고 새로 만든 흔적은 [USN 변경 저널](../../filesystem/usnjrnl.md)에 남을 수 있습니다. 옛 캐시는 [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)으로 찾습니다.
- 방문 기록만 지우고 캐시는 남기는 경우가 있습니다. 이때 캐시 키의 최상위 사이트가 History 에 없는 사이트를 알려 줍니다.
- 캐시 파일을 손으로 고치면 항목 머리와 순위 노드의 `self_hash` 칸이 안 맞을 수 있습니다. 이 칸은 각 구조의 앞부분으로 계산한 해시입니다 (소스 주석). 다만 해시 계산 방법은 이 글에서 따라가지 않았습니다.
- 완전삭제 도구의 흔적은 [완전삭제 도구를 썼나](../../../04-scenarios/activity/anti-forensics/wiping-tools.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 libyal 명세와 Chromium 소스(`disk_format.h`)로 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다. `??` 는 키 해시처럼 이 예시에서 값을 정하지 않은 바이트입니다. 모든 값은 리틀 엔디언입니다.

**1) 항목 머리 찾기.** `data_1` 에서 키 문자열 `1/0/_dk_` 를 찾습니다. 찾은 위치에서 0x60 을 빼면 항목 머리의 시작입니다. 그 위치는 `8192 + 256 × n` 이어야 합니다. 아니면 긴 키나 다른 스트림 안의 문자열입니다. 아래 예시는 `data_1` 의 0xADC00 (블록 0xABC) 입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    ?? ?? ?? ?? 00 00 00 00 23 01 00 90 02 00 00 00
0x10    00 00 00 00 00 00 00 00 40 33 99 14 DA 8E 2F 00
0x20    54 00 00 00 00 00 00 00 A2 01 00 00 55 BC 00 00
0x30    00 00 00 00 00 00 00 00 56 04 01 A1 5F 00 00 80
0x40    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0x50    00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ??
0x60    31 2F 30 2F 5F 64 6B 5F 68 74 74 70 73 3A 2F 2F   1/0/_dk_https://
        … 키가 0x60 부터 84바이트 이어지고 00 으로 끝납니다
```

**2) 칸 읽기.**

| 오프셋 | 칸 | 바이트 | 값 |
|---|---|---|---|
| 0x00 | 키 해시 (hash) | `?? ?? ?? ??` | `index` 표에서 이 항목을 찾을 때 씁니다 |
| 0x04 | 같은 칸의 다음 항목 (next) | `00 00 00 00` | 없습니다 |
| 0x08 | 순위 노드 주소 | `23 01 00 90` | 0x90000123 |
| 0x0C | 사용 횟수 (reuse_count) | `02 00 00 00` | 2 |
| 0x10 | 다시 받은 횟수 (refetch_count) | `00 00 00 00` | 0 |
| 0x14 | 상태 (state) | `00 00 00 00` | 0 = 정상. 1 은 밀려남, 2 는 지울 예정입니다 |
| 0x18 | 항목을 만든 시각 | `40 33 99 14 DA 8E 2F 00` | 0x002F8EDA14993340 |
| 0x20 | 키 길이 | `54 00 00 00` | 84바이트. 159 이하라 머리 안에 있습니다 |
| 0x24 | 긴 키 주소 | `00 00 00 00` | 없습니다 |
| 0x28 | 스트림 0 크기 | `A2 01 00 00` | 418바이트 |
| 0x2C | 스트림 1 크기 | `55 BC 00 00` | 48,213바이트 |
| 0x38 | 스트림 0 주소 | `56 04 01 A1` | 0xA1010456 |
| 0x3C | 스트림 1 주소 | `5F 00 00 80` | 0x8000005F |
| 0x48 | 항목 플래그 | `00 00 00 00` | 부모·자식 항목이 아닙니다 |
| 0x5C | 머리 해시 (self_hash) | `?? ?? ?? ??` | |
| 0x60 | 키 | | `1/0/_dk_https://example.com https://example.com https://cdn.example.net/img/logo.png` |

**3) 캐시 주소 풀기.** 비트 31 은 사용 중 표시, 비트 28~30 은 형식, 비트 24~25 는 "블록 수 − 1", 비트 16~23 은 `data_N` 번호, 비트 0~15 는 블록 번호입니다. 형식이 0 이면 비트 0~27 이 `f_` 파일 번호입니다 (libyal 명세).

| 주소 | 형식 | 블록 수 | 파일 | 블록 | 찾아갈 곳 |
|---|---|---|---|---|---|
| 0x90000123 | 1 = 순위 노드 (36바이트) | 1 | `data_0` | 0x123 (291) | `data_0` 의 8192 + 291 × 36 = 0x48EC |
| 0xA1010456 | 2 = 256바이트 블록 | 2 | `data_1` | 0x456 (1110) | `data_1` 의 8192 + 1110 × 256 = 0x47600 부터 418바이트 |
| 0x8000005F | 0 = 따로 둔 파일 | | | | `f_00005f` 파일 전체 48,213바이트 |

**4) 순위 노드 읽기.** `data_0` 의 0x48EC 에서 36바이트를 읽습니다.

```
00 D2 A3 0E DB 8E 2F 00  00 00 00 00 00 00 00 00
?? ?? ?? ?? ?? ?? ?? ??  BC 0A 01 A0 00 00 00 00
?? ?? ?? ??
```

- 0x00 마지막 사용 시각은 0x002F8EDB0EA3D200 입니다.
- 0x08 두 번째 시각 칸은 0 입니다. 이 칸은 판단에 쓰지 않습니다.
- 0x10·0x14 는 앞뒤 순위 노드 주소입니다.
- 0x18 은 이 노드가 가리키는 항목 주소 0xA0010ABC 입니다. `data_1` 블록 0xABC, 곧 1) 의 항목 머리입니다. 주소가 서로 맞는지 여기서 확인합니다.

**5) 시각 바꾸기.**

- 항목을 만든 시각: 0x002F8EDA14993340 = 13,386,391,205,000,000 마이크로초입니다. 1601-01-01 부터 세면 2025-03-14 02:00:05 UTC 입니다. 한국 시각으로는 같은 날 11:00:05 입니다.
- 마지막 사용 시각: 0x002F8EDB0EA3D200 = 13,386,395,400,000,000 마이크로초입니다. 2025-03-14 03:10:00 UTC 입니다.
- 이 항목은 02:00:05 에 만들어졌고, 03:10:00 에 마지막으로 쓰였습니다. 사용 횟수는 2 입니다.

**6) 스트림 따라가기.**

- `data_1` 0x47600 에서 418바이트를 읽습니다. 헤더 부분에서 `Content-Type`, `Content-Encoding`, `Date` 를 찾습니다.
- `f_00005f` 가 본문입니다. `Content-Type` 이 `image/png` 이고 `Content-Encoding` 이 없다면 파일은 `89 50 4E 47` 로 시작해야 합니다.

> 그림 자리: 항목 머리 256바이트를 칸별로 색을 나누고, 순위 노드 주소·스트림 0 주소·스트림 1 주소에서 `data_0`·`data_1`·`f_00005f` 로 화살표가 이어지는 그림. 순위 노드의 항목 주소가 다시 항목 머리를 가리키는 화살표도 함께 보여 줍니다

### 공개 도구로 한 번

ChromeCacheView, Hindsight, plaso 의 `chrome_cache` 파서가 이 형식을 읽습니다. 도구는 예로만 듭니다. 결과를 볼 때 다음을 확인합니다.

- 분할 키를 최상위 사이트와 자원 URL 로 나눠 보여 주는지 확인합니다.
- 시각 열이 어느 칸인지 확인합니다. 항목을 만든 시각, 마지막 사용 시각, 응답 시각, `Date` 헤더는 서로 다른 값입니다.
- 시각을 UTC 로 보여 주는지, 분석 PC 의 현지 시각으로 바꿔 보여 주는지 확인합니다.
- `Cache\Cache_Data` 를 찾아 들어가는지, 옛 경로인 `Cache` 만 보는지 확인합니다.
- 본문을 뽑을 때 `Content-Encoding` 을 풀어 주는지 확인합니다.
- 도구가 낸 항목 수를 `index` 머리 0x08 의 항목 수와 비교합니다.
- 한두 항목은 위 헥스 절차로 직접 풀어 도구 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [방문·다운로드 기록 (History)](history.md) | 캐시 키의 최상위 사이트가 방문 기록에 있는지. 없으면 기록을 지웠거나 미리 로드였을 수 있습니다 |
| [세션·탭 복원 (Sessions)](sessions.md) | 복원한 탭이 자원을 다시 받은 것인지 |
| [쿠키 (Cookies)](cookies.md) | 같은 사이트의 쿠키가 만들어지고 마지막으로 쓰인 시각 |
| [웹 저장소 (Local Storage·IndexedDB)](local-storage-indexeddb.md) | 사이트가 스스로 저장한 데이터. `Service Worker\CacheStorage` 와 함께 봅니다 |
| [확장 프로그램 (Extensions)](extensions.md) | 사용자 행위가 아니라 확장 프로그램이 부른 요청인지 |
| [다운로드 출처 표시 (Zone.Identifier)](../../filesystem/zone-identifier.md) | 캐시에 있는 자원 URL 이 내려받은 파일의 출처 URL 과 같은지 |
| [네트워크 사용량 (SRUM)](../../execution/system-resource-usage-monitor/network-data-usage.md) | 같은 시간대에 브라우저가 받은 양 |
| [$MFT](../../filesystem/mft.md) · [USN 변경 저널](../../filesystem/usnjrnl.md) | `f_` 파일과 `data_N` 이 만들어지고 지워진 시각 |

사이트 방문 전체를 재구성하는 흐름은 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md)을 봅니다. 파이어폭스 캐시는 [캐시 (cache2)](../firefox/cache2.md)에서 다룹니다.

## 실습

**직접 만든 Windows 10·11 가상 머신** 에서 해 봅니다.

1. Chrome 이나 Edge 로 사이트 A 를 엽니다. A 가 다른 도메인에서 불러오는 이미지나 스크립트 URL 하나를 적어 둡니다.
2. 브라우저를 닫고 `Cache\Cache_Data` 를 복사합니다. 그 URL 의 키를 찾아 최상위 사이트가 A 인지 봅니다.
3. 같은 CDN 스크립트를 쓰는 다른 사이트 B 를 엽니다. 같은 자원 URL 의 키가 두 개로 나뉘는지 봅니다.
4. 방문 기록만 지우고 캐시는 남깁니다. History 에서는 사라졌지만 캐시 키에는 남은 사이트를 찾습니다.
5. "캐시된 이미지 및 파일" 을 지웁니다. `index` 머리 0x28 의 시각과 폴더의 파일 목록이 어떻게 바뀌는지 봅니다. 같은 시각에 $UsnJrnl 에 무엇이 남는지도 봅니다.
6. 시크릿 창으로 새 사이트를 엽니다. 창을 닫은 뒤 `Cache_Data` 에 그 사이트의 키가 생겼는지 봅니다.
7. 시스템 시계를 한 시간 틀리게 맞춘 뒤 사이트를 엽니다. 응답 시각과 `Date` 헤더의 차이가 한 시간으로 나오는지 봅니다.

**Chrome 을 쓴 공개 Windows 검체** (NIST CFReDS 등) 에서도 풀어 봅니다.

1. 캐시가 `Cache` 바로 아래에 있습니까, `Cache\Cache_Data` 아래에 있습니까? `User Data` 의 `Last Version` 파일이 있다면 함께 봅니다.
2. 키에 `_dk_` 가 있습니까? 없다면 분할 전 버전으로 볼 수 있습니까?
3. History 의 방문 사이트와 캐시 키의 최상위 사이트를 비교합니다. History 에 없는 사이트가 있습니까?
4. 가장 이른 항목을 만든 시각과 `index` 머리의 캐시를 만든 시각을 비교합니다.
5. `f_` 파일을 형식별로 나눠 봅니다. 이미지만 모아 보면 어떤 사이트를 썼는지 보입니까?

## 참고 문헌

- libyal (Joachim Metz), "Chrome Cache file format", dtformats — https://github.com/libyal/dtformats/blob/main/documentation/Chrome%20Cache%20file%20format.asciidoc
- The Chromium Projects, "Disk Cache" 설계 문서 — https://www.chromium.org/developers/design-documents/network-stack/disk-cache/
- The Chromium Projects, "Very Simple Backend" 설계 문서 — https://www.chromium.org/developers/design-documents/network-stack/disk-cache/very-simple-backend/
- Chrome for Developers, HTTP 캐시 분할 안내 (Chrome 86) — https://developer.chrome.com/blog/http-cache-partitioning
- Chromium 소스, `net/disk_cache` (`disk_cache.cc`, `blockfile/disk_format.h`, `blockfile/entry_impl.cc`, `blockfile/block_files.cc`, `blockfile/backend_impl.cc`) — https://github.com/chromium/chromium/tree/main/net/disk_cache
- Chromium 소스, `net/http/http_cache.cc`, `net/http/http_response_info.h`, `content/browser/code_cache/generated_code_cache.cc`, `chrome/browser/net/profile_network_context_service.cc` — https://github.com/chromium/chromium
