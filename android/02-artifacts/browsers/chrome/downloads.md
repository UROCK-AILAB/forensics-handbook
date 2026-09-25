---
title: "다운로드"
parent: "크롬"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 850
---

# 다운로드 (Downloads)

## 한 줄 요약

Chrome for Android 의 다운로드 기록은 `History` 파일 안의 downloads 표에 한 건씩 들어 있고, 저장 경로와 크기, 상태, 내용의 SHA-256 값, 다운로드를 시작한 탭의 URL 이 남으며, 리다이렉트를 거친 실제 파일 주소는 downloads_url_chains 표에 따로 남습니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

Chrome 은 다운로드를 시작할 때 downloads 표에 행을 만들고, 받는 동안과 끝났을 때 받은 크기와 상태, 끝난 시각을 고쳐 적습니다 [1]. 요청한 URL 이 다른 주소로 넘어가면 처음 주소부터 마지막 주소까지를 downloads_url_chains 표에 순서대로 남기고, 파일을 여러 조각으로 나눠 받으면 downloads_slices 표에 조각 정보를 남깁니다 [1].

파일 위치는 [방문 기록 (History)](history.md) 페이지와 같은 `app_chrome/Default/History` 이고, 읽기 전 주의(저널 파일, 사본 만들기)도 그 페이지에 있습니다. 패키지 이름과 폴더 구조는 [크롬 (Chrome for Android)](index.md) 허브를 봅니다.

## 위치와 버전별 차이

downloads 표에는 Chrome 이 버전을 올리며 덧붙인 칸이 많아서, 오래된 DB 에는 일부 칸이 없을 수 있습니다. 소스에는 새 칸을 나중에 덧붙이는 이전(migration) 코드(EnsureColumnExists)가 있습니다 [1].

| DB 버전 또는 시기 | 차이 | 출처 |
|---|---|---|
| DB 버전 24 | downloads_url_chains 표가 생김 | 소스 주석 [1] |
| DB 버전 32 | last_access_time 칸이 없음 | ALEAPP 주석 [2] |
| DB 버전 33 | downloads_slices 표가 생김 | 소스 주석 [1] |
| "pre-v65"(ALEAPP 주석 표기 그대로) | tab_url 칸이 없음 | ALEAPP 주석 [2] |

ALEAPP 가 이 파서로 시험한 표본에서 Downloads 행 수는 0행부터 108행까지 기기마다 크게 달랐습니다 [2]. 파일을 받은 적이 있어도 기록이 남지 않았거나 지워졌을 수 있으니, 0행이라는 결과만으로 다운로드가 없었다고 말하지 않습니다.

## 구조

### downloads 표

현행 Chromium 의 표 정의에 있는 칸은 아래와 같습니다 [1]. 뜻은 소스 주석을 옮긴 것입니다.

| 칸 | 뜻 |
|---|---|
| id, guid | 다운로드 번호와 고유 ID |
| current_path | 현재 디스크 위치 |
| target_path | 최종 디스크 위치 |
| start_time, end_time, last_access_time | 시작, 끝, 마지막 접근 시각(1601-01-01 UTC 부터의 마이크로초) [2] |
| received_bytes, total_bytes | 받은 크기와 전체 크기 |
| state | 상태(아래 표) |
| danger_type | 위험 판정 값(아래 표) |
| interrupt_reason | 중단 사유(아래 표) |
| hash | 내용의 SHA-256 원시값 |
| opened | 한 번이라도 열었으면 1 |
| transient | 일시 다운로드면 1 |
| referrer | HTTP Referrer |
| site_url, embedder_download_data | 소스 정의에 있는 칸(뜻은 이번에 확인하지 않음) |
| tab_url, tab_referrer_url | 다운로드를 시작한 탭의 URL 과 그 탭의 referrer |
| http_method | 요청 방식 |
| by_ext_id, by_ext_name, by_web_app_id | 소스 정의에 있는 칸(뜻은 이번에 확인하지 않음) |
| etag, last_modified | 서버 응답 헤더 값 |
| mime_type, original_mime_type | 파일 형식 |

state 는 소스 주석에 "1=complete, 4=interrupted" 로 적혀 있고, ALEAPP 는 0 진행 중, 1 완료, 2 취소, 3·4 중단으로 풉니다 [1][2]. danger_type 과 interrupt_reason 은 Chromium 의 열거값이고, ALEAPP 가 숫자마다 이름을 붙여 줍니다 [2].

| danger_type | ALEAPP 표시 |
|---|---|
| 1 | Dangerous |
| 2 | Dangerous URL |
| 3 | Dangerous Content |
| 8 | Potentially Unwanted |

| interrupt_reason | ALEAPP 표시 |
|---|---|
| 1 | File Error |
| 3 | Disk Full |
| 20 | Network Error |
| 40 | Canceled |
| 41 | Browser Shutdown |
| 50 | Browser Crashed |

위 두 표는 ALEAPP 가 푸는 값 가운데 일부만 옮긴 것이고, 나머지 값은 ALEAPP 코드나 Chromium 열거값 정의에서 확인합니다.

### downloads_url_chains 표

칸은 id(downloads.id 와 같은 값), chain_index, url 입니다. chain_index 0 이 처음 요청한 URL 이고, 가장 큰 번호가 리다이렉트를 거친 뒤의 최종 URL 입니다 [1]. ALEAPP 는 이 표를 읽지 않고, ALEAPP 결과의 "Tab URL" 은 파일 주소가 아니라 다운로드를 시작한 페이지라고 주석에 밝혀 두었습니다 [2]. 실제 파일을 어디서 받았는지는 이 표를 직접 열어 확인합니다.

### downloads_slices 표

칸은 download_id, offset, received_bytes, finished 이고, 파일을 여러 조각으로 나눠 동시에 받을 때 씁니다 [1].

## 증거로서 의미

| 기록 | 말할 수 있는 것 | 말할 수 없는 것 |
|---|---|---|
| state 완료, received_bytes = total_bytes | 이 프로필의 Chrome 이 그 크기의 내용을 target_path 로 받은 기록이 있다 | 파일이 지금도 그 경로에 있다는 것 |
| hash | 받은 내용의 SHA-256 값 | 지금 디스크의 파일이 같은 내용이라는 것(다시 계산해 비교해야 함) |
| opened = 1 | 한 번이라도 연 기록이 있다 | 누가, 언제, 어떤 앱으로 열었는지 |
| tab_url | 다운로드를 시작한 페이지 | 파일을 실제로 내려 준 주소(url_chains 로 확인) |
| url_chains 마지막 url | 리다이렉트를 거친 최종 파일 주소 | 서버 쪽 파일이 지금 같은 내용인지 |
| danger_type 값 | Chrome 이 위험 판정을 내린 기록 | 파일이 실제로 악성인지 |
| 기록이 없음 | — | 파일을 받지 않았다는 것 |

악성 앱 설치 파일(APK)을 어디서 받았는지 따지는 사건은 [악성 앱은 어디서 들어왔나 (Initial Access)](../../../04-scenarios/incident/initial-access.md), 받은 파일을 밖으로 내보냈는지는 [자료를 밖으로 보냈나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md) 시나리오를 봅니다.

## 시각 해석

start_time, end_time, last_access_time 은 1601-01-01 UTC 부터의 마이크로초이고 [2], 바꾸는 계산과 헥스 예시는 [방문 기록 (History)](history.md) 페이지에 있습니다. 값이 0 인 칸을 그대로 바꾸면 1601년 날짜가 나오니, 빈 값으로 두고 날짜로 옮겨 적지 않습니다. 시작과 끝 사이의 간격으로 받는 데 걸린 시간을 가늠할 때는 received_bytes 와 함께 보고, 나눠 받은 다운로드라면 downloads_slices 의 조각 정보도 함께 봅니다.

## 함정과 한계

진행 중(IN_PROGRESS)으로 남은 행은 Chrome 이 다운로드 기록을 조회하거나 만들고, 고치고, 지울 때 먼저 부르는 정리 함수(EnsureInProgressEntriesCleanedUp)가 한꺼번에 중단(INTERRUPTED)으로 바꾸고 interrupt_reason 을 충돌(crash) 사유로 채웁니다 [1]. 그래서 중단 행 가운데는 사용자가 멈춘 것이 아니라 앱이 비정상 종료된 흔적이 섞일 수 있고, 이런 행의 중단 사유를 사용자의 행동으로 읽지 않습니다. 앱 종료 기록은 [앱 오류·종료 기록 (DropBox·tombstones·ANR)](../../app-usage/crash-records.md)에서 맞춰 봅니다.

다운로드 행을 지우면(RemoveDownload) downloads 행과 함께 downloads_url_chains, downloads_slices 의 같은 번호 행도 지워집니다 [1]. 기록만 지우고 실제 파일은 남는지, 반대로 파일만 지우면 기록이 어떻게 바뀌는지는 확인하지 못했습니다. 기록과 파일 둘 중 하나만 있는 경우를 찾았다면 둘을 따로 적고, 지운 행의 흔적은 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)와 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md) 페이지를 봅니다.

Chrome 의 기본 저장 위치가 공용 저장 공간의 `Download` 폴더인지, 받은 파일을 미디어 저장소(MediaStore)의 Downloads 에 등록하는지는 이번에 확인하지 못했고, 경로는 target_path 에 적힌 값을 그대로 따라갑니다. 관찰 기기의 `/sdcard/Download` 에는 항목이 151개, 그 가운데 폴더가 36개 있었지만 이름은 가려서 어느 앱이 만든 것인지는 알 수 없었습니다 (확인 범위: Android 16, One UI 8.5). 공용 저장 공간은 여러 앱이 함께 쓰는 곳이라, 그 폴더에 파일이 있다는 것만으로 Chrome 이 받았다고 말하지 않습니다. 폴더 구조는 [공용 저장 공간 (Shared Storage·/sdcard)](../../../01-foundations/storage/shared-storage.md), 파일 등록 기록은 [미디어 저장소 (MediaStore)](../../media/mediastore/index.md) 페이지를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

hash 칸은 SHA-256 원시값 32바이트라서 [1], 도구 화면에서 글자가 깨져 보이면 16진수로 바꿔 봅니다. target_path 의 파일이 아직 있으면 그 파일의 SHA-256 을 다시 계산해 아래처럼 비교합니다. 아래 값은 모양을 보여 주려고 만든 예시이고, 실제 검체에서 나온 해시가 아닙니다.

```
hash 칸(32바이트)  : 3F 8A … (32바이트) … 1C
hex(hash)          : 3F8A…1C  (64자)
파일 SHA-256       : 3f8a…1c  (64자, 대소문자만 다름)
```

두 값이 같으면 기록에 남은 다운로드 내용과 지금 파일의 내용이 같다고 말할 수 있고, 다르면 받은 뒤 파일이 바뀌었거나 다른 파일일 수 있습니다.

### 공개 도구로 한 번

사본을 sqlite3 명령줄이나 DB Browser for SQLite 로 열어, ALEAPP 가 읽지 않는 URL 사슬까지 한 번에 봅니다. 오래된 DB 에서는 없는 칸이 있어 오류가 나면 그 칸을 빼고 다시 실행합니다.

```sql
SELECT d.id,
       datetime(d.start_time/1000000 - 11644473600, 'unixepoch') AS start_utc,
       datetime(d.end_time/1000000 - 11644473600, 'unixepoch')   AS end_utc,
       d.target_path, d.received_bytes, d.total_bytes,
       d.state, d.danger_type, d.interrupt_reason, d.opened,
       hex(d.hash) AS sha256,
       d.tab_url, d.mime_type,
       c.chain_index, c.url AS chain_url
FROM downloads d
LEFT JOIN downloads_url_chains c ON c.id = d.id
ORDER BY d.id, c.chain_index;
```

결과는 ALEAPP 의 Downloads 결과와 나란히 놓고 행 수와 시각이 맞는지 확인합니다.

## 교차 검증

다운로드 직전에 어느 페이지를 봤는지는 [방문 기록 (History)](history.md)에서 tab_url 과 같은 URL 의 방문을 찾아 맞춰 보고, 그 페이지가 탭으로 남아 있는지는 [탭과 세션 (Tabs·Sessions)](tabs-sessions.md)을 봅니다. 받은 파일이 APK 라면 [APK 정보 (AndroidManifest·서명)](../../embedded-metadata/apk.md)와 [설치된 앱 (packages.xml)](../../app-usage/packages/index.md)으로 설치 여부를 확인하고, 문서라면 [문서 메타데이터 (PDF·Office)](../../embedded-metadata/documents.md)를 봅니다. 받는 동안 오간 데이터 양은 [데이터 사용량 (netstats)](../../network/netstats.md)과 비교합니다.

## 실습

Chrome 이 깔린 공개 Android 검체로 아래 질문을 풀어 봅니다.

1. downloads 의 각 행에 대해 downloads_url_chains 의 첫 URL 과 마지막 URL 을 뽑고, tab_url 과 다른 경우가 몇 건인지 셉니다.
2. state 가 중단인 행의 interrupt_reason 을 모아, 사용자가 멈춘 것과 앱 종료로 보이는 것을 나눠 봅니다.
3. target_path 의 파일이 남아 있는 행을 골라 SHA-256 을 다시 계산하고 hash 칸과 비교합니다.
4. 공용 저장 공간의 `Download` 폴더에 있는 파일 가운데 downloads 표에 기록이 없는 파일을 찾아, 다른 앱이 만들었을 가능성을 적어 봅니다.

## 참고 문헌

1. Chromium `components/history/core/browser/download_database.cc` — https://raw.githubusercontent.com/chromium/chromium/main/components/history/core/browser/download_database.cc
2. ALEAPP `scripts/artifacts/chrome.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/chrome.py
