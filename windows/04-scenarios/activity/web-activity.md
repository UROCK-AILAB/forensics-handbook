---
title: "웹 사용 행위 재구성"
parent: "시나리오 · 행위 재구성"
nav_order: 3820
---

# 웹 사용 행위 재구성 (Web Activity)

"이 PC 에서 어떤 주소를 언제 불러왔나, 무엇을 검색하고 무엇을 받았나" 를 묻는 조사를 다룹니다. 웹 사용 기록은 대부분 브라우저 프로필 안에 남습니다. 브라우저 밖에도 DNS 질의, 앱별 네트워크 사용량, 받은 파일의 출처 표시가 남습니다. 이 페이지는 이 기록을 어떤 순서로 모으는지, 그 기록으로 어디까지 말할 수 있는지를 정리합니다. 브라우저 데이터의 구조는 각 브라우저 페이지에 있습니다.

"(현장 관찰)" 을 붙인 내용은 분석 현장에서 겪은 일을 적어 둔 메모에서 가져왔습니다. 공식 문서로 확인한 내용이 아니므로 검체마다 다시 확인합니다.

## 조사 질문

- 어느 사용자 프로필의 어느 브라우저에 기록이 남았습니까?
- 어떤 주소를 언제 불러왔습니까? 주소를 직접 입력했습니까, 링크를 눌러 옮겨 갔습니까?
- 무엇을 검색했습니까?
- 무엇을 받았습니까?
- 기록이 비어 있다면 왜 비어 있습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | 설치된 브라우저와 기록 형식이 다를 수 있습니다. 옛 IE·Edge 기록은 ESE 형식의 WebCacheV01.dat 에 있습니다. [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 버전과 빌드를 먼저 적습니다. |
| 시간대 | 브라우저마다 시각 형식과 기준이 다릅니다. [시간대 설정](../../02-artifacts/system-account/time-zone.md) 을 읽습니다. Bias 값을 부호 있는 수로 읽는 법은 [이 파일을 누가 언제 열었나](file-access.md) 의 "먼저 확인할 것" 에 있습니다. |
| 사용자·프로필 | 크롬 계열은 `User Data\<프로필>` 폴더마다 기록이 따로 남습니다. 한 사용자에게 프로필이 여럿 있을 수 있습니다. 폴더 구조는 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 에 있습니다. |
| 브라우저 | 어떤 브라우저가 설치돼 있었는지 [설치 프로그램](../../02-artifacts/system-account/uninstall.md) 에서 봅니다. 브라우저 하나만 보고 끝내지 않습니다. |
| 동기화 | 다른 기기의 방문이 동기화로 들어와 있을 수 있습니다. 아래 "동기화된 방문" 을 봅니다. |
| 수집 범위 | 사용자 프로필마다 브라우저 폴더 전체(DB 파일과 함께 있는 저널 파일 포함), SRUDB.dat, Sysmon 로그를 확보합니다. 메모리를 떴다면 함께 봅니다. |

**ESE 형식 DB 다루기 (현장 관찰).** SRUDB.dat·WebCacheV01.dat·Windows.edb 는 ESE 형식입니다. 아래는 이 세 DB 를 다룰 때 겪은 일입니다.

압수 이미지에서 이 DB 는 대부분 비정상 종료 상태였고(현장 관찰), 로그 사슬이 끊겨 있으면 복구가 안 될 수 있습니다(현장 관찰). 그래서 원본을 건드리지 않고 사본에서 작업합니다(현장 관찰). 손상된 DB 는 읽는 방식에 따라 행 수가 달랐는데(현장 관찰), 한 방식은 1,612행, 다른 방식은 1,742행으로 읽은 사례가 있습니다(현장 관찰). 그래서 두 가지 이상 방식으로 열어 행 수와 값을 비교합니다.

ESE 의 구조와 비정상 종료 상태는 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서, 도구마다 결과가 다를 때 맞춰 보는 법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 에서 봅니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 크롬 계열 History | 방문한 주소, 방문마다의 시각과 이동 방식, 검색어, 다운로드 | [크롬 계열 브라우저](../../02-artifacts/browsers/chrome-edge-whale/index.md) |
| 2 | 크롬 계열의 다른 파일 | 쿠키·캐시·세션·웹 저장소·자동완성·즐겨찾기·확장 프로그램 (세부는 허브의 하위 페이지) | [크롬 계열 브라우저](../../02-artifacts/browsers/chrome-edge-whale/index.md) |
| 3 | 파이어폭스 | 방문·다운로드 기록 | [파이어폭스](../../02-artifacts/browsers/firefox/index.md) |
| 4 | 옛 IE·Edge | WebCacheV01.dat 의 기록 | [인터넷 익스플로러·옛 엣지](../../02-artifacts/browsers/ie-edgehtml/index.md) |
| 5 | 받은 파일의 출처 표시 | 받은 주소와 참조 주소 | [이 파일은 어디서 왔나](file-origin.md) · [다운로드 출처 표시](../../02-artifacts/filesystem/zone-identifier.md) |
| 6 | Sysmon 22·3 | 프로세스별 DNS 질의, 네트워크 연결 | [Sysmon 로그](../../02-artifacts/event-logs/sysmon/index.md) |
| 7 | SRUM | 앱별 네트워크 송수신 바이트(1시간 단위) | [SRUM](../../02-artifacts/execution/system-resource-usage-monitor/index.md) |
| 8 | 메모리 | 메모리를 떴을 때, 실행 중이던 브라우저와 네트워크 흔적 | [메모리 분석](../../03-techniques/analysis/memory-forensics/index.md) |

브라우저 기록(1~4)을 먼저 봅니다. 5~8 은 브라우저 기록을 다른 쪽에서 맞춰 보거나, 브라우저 기록이 비어 있을 때 씁니다.

## 크롬 계열 브라우저

크롬 계열 (Chrome·Edge·Whale) 은 `User Data\<프로필>\History` 파일(SQLite)에 방문과 다운로드를 남깁니다. 표와 칸의 세부, 증명하는 것과 증명하지 못하는 것은 [크롬 계열 브라우저](../../02-artifacts/browsers/chrome-edge-whale/index.md) 에 있습니다. 아래는 조사 순서에 필요한 부분만 추린 것입니다.

| 표 | 남는 것 |
|---|---|
| `urls` | 주소마다 한 행 |
| `visits` | 방문마다 한 행 |
| `keyword_search_terms` | 검색어 |
| `downloads` · `downloads_url_chains` | 다운로드 |

- 시각은 1601-01-01 UTC 부터 센 마이크로초입니다. 바꾸는 법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- 다운로드 칸 가운데 출처 조사에 쓰는 칸은 [이 파일은 어디서 왔나](file-origin.md) 에서 다룹니다.

**이동 방식 (transition).**

`visits.transition` 은 32비트 값이며, 아래 8비트는 기본 유형(주소 입력(TYPED), 링크 누름 같은 유형)이고 위 24비트에는 덧붙은 표시가 들어갑니다. 이 값은 음수로 저장될 수 있어서, 음수이면 32비트 부호 없는 값으로 바꾼 뒤 아래 8비트를 떼어 봅니다.

계산 방법만 보여 주는 예시를 듭니다. 저장된 값이 -2147483647 이면 부호 없는 값은 0x80000001 이고, 아래 8비트는 0x01 입니다. 0x01 이 어떤 유형인지는 [크롬 계열 브라우저](../../02-artifacts/browsers/chrome-edge-whale/index.md) 에서 확인합니다.

**동기화된 방문.** 다른 기기에서 동기화로 들어온 방문은 `visit_source.source` 와 `originator_cache_guid` 로 가립니다.

**만료와 지운 흔적.**

90일보다 오래된 방문은 만료로 빠지고, `visits.id` 에 빈 구간이 있으면 기록을 지운 흔적의 단서로 봅니다. 크롬 계열은 SQLite 보안 삭제를 켜고 빌드해서 지운 기록의 자리는 대부분 0 으로 채워져 있지만, 저널 파일에는 지우기 전 페이지가 남아 있을 수 있습니다. DB 파일을 복사할 때 저널 파일을 함께 가져오는 까닭입니다. SQLite 저널의 구조는 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에 있습니다.

## 파이어폭스와 옛 IE·Edge

- 파이어폭스의 방문·다운로드 기록은 [파이어폭스](../../02-artifacts/browsers/firefox/index.md) 에서 봅니다. 이 페이지에서는 세부를 다루지 않습니다.
- 옛 IE·Edge 의 기록은 WebCacheV01.dat 에 남습니다. 위치와 표는 [인터넷 익스플로러·옛 엣지](../../02-artifacts/browsers/ie-edgehtml/index.md) 에 있습니다.
- WebCacheV01.dat 는 ESE 형식이라 압수 이미지에서 비정상 종료 상태가 흔합니다(현장 관찰). 위 "ESE 형식 DB 다루기" 를 따릅니다.
- 브라우저마다 시각 형식이 다릅니다. 각 브라우저 페이지에서 형식을 확인한 뒤 UTC 로 맞춥니다.

## 브라우저 밖의 기록

**Sysmon.**

| 이벤트 | 남는 것 |
|---|---|
| 22 DNSEvent | 프로세스가 DNS 질의를 할 때 생깁니다. 성공·실패·캐시 여부와 관계없이 남습니다. |
| 3 네트워크 연결 | 기본으로 꺼져 있습니다. 켜면 프로세스, IP, 포트, 호스트 이름을 남깁니다. |

(표는 [1] 에서 옮겼습니다.)

- 22 는 Windows 8.1 에서 더해진 원격 측정을 씁니다[1]. 그래서 Windows 7 이하에서는 남지 않습니다[1].
- Sysmon 의 설치 조건과 시각 기준은 [어떤 프로그램을 언제 실행했나](program-execution.md) 의 "Sysmon 이벤트 1" 절에 있습니다.
- 두 이벤트 모두 프로세스 정보가 있습니다. 브라우저 프로세스로 걸러서 브라우저 기록의 시각과 맞춥니다.

**SRUM.**

SRUM 에는 앱별 네트워크 송수신 바이트가 1시간 단위로 남으므로, 이 기록으로 그 시간대에 브라우저가 주고받은 양을 봅니다. 주소는 브라우저 기록과 Sysmon 에서 찾습니다. SRUDB.dat 도 ESE 형식이라 위 "ESE 형식 DB 다루기" 를 따릅니다. 네트워크 사용량 표의 구조는 [SRUM](../../02-artifacts/execution/system-resource-usage-monitor/index.md) 에 있습니다.

**받은 파일.** 받은 파일에 Zone.Identifier 스트림이 있으면 HostUrl·ReferrerUrl 을 브라우저 기록과 맞춥니다. 방법은 [이 파일은 어디서 왔나](file-origin.md) 에 있습니다.

**올린 파일.** 웹으로 파일을 올렸는지는 [자료를 밖으로 빼돌렸나](../exfiltration/data-exfiltration/index.md) 에서 다룹니다.

## 분석 흐름

1. Windows 버전·시간대·사용자 SID 를 정리합니다. 설치된 브라우저와 사용자마다의 브라우저 프로필 폴더를 목록으로 만듭니다.
2. DB 파일을 저널 파일과 함께 사본으로 떠 놓고 사본에서 엽니다. ESE 형식 DB 는 두 가지 이상 방식으로 엽니다.
3. 크롬 계열 History 에서 `visits` 를 `urls` 와 이어, 방문마다 주소·시각·이동 방식을 뽑습니다. 시각은 1601 기준 마이크로초를 UTC 로 바꿉니다.
4. `visit_source` 로 동기화된 방문을 따로 표시합니다.
5. `keyword_search_terms` 에서 검색어를 뽑아 방문 시각과 나란히 놓습니다.
6. `downloads` 와 `downloads_url_chains` 에서 받은 파일을 뽑습니다. 디스크의 파일과 출처 표시를 맞춥니다.
7. `visits.id` 의 빈 구간과 90일 만료 범위를 확인합니다. 기록이 비어 있으면 [시크릿 모드로 무엇을 했나](private-browsing.md) 도 봅니다.
8. 파이어폭스·옛 IE·Edge 가 있으면 같은 방식으로 뽑습니다.
9. Sysmon 22·3 이 있으면 같은 시간대의 DNS 질의와 연결을 브라우저 프로세스로 걸러 봅니다.
10. SRUM 에서 그 시간대에 브라우저가 주고받은 양을 봅니다.
11. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올립니다.
12. 그 시각에 누가 PC 앞에 있었는지는 [그 시각에 PC 를 쓴 사람이 누구인가](user-attribution.md) 를 따라 따로 좁힙니다.

## 흔한 오판

1. **방문 기록을 "보았다" 로 씁니다.** 방문 기록은 이 프로필이 이 주소를 불러온 기록입니다. 사람이 화면을 보고 있었는지, 무엇을 읽었는지는 말하지 않습니다.
2. **행 수를 방문 횟수로 씁니다.** 리다이렉트와 프레임 때문에 한 번 옮겨 가도 행이 여러 개 생깁니다.
3. **동기화된 방문을 이 PC 의 방문으로 씁니다.** `visit_source` 로 가린 뒤에 씁니다.
4. **기록이 없으니 방문하지 않았다고 봅니다.** 시크릿 창을 썼거나, 기록을 지웠거나, 90일이 지나 만료됐을 수 있습니다. 다른 프로필이나 다른 브라우저를 썼을 수도 있습니다.
5. **모든 브라우저의 시각 형식을 같다고 봅니다.** 크롬 계열은 1601-01-01 UTC 부터 센 마이크로초입니다. 다른 브라우저는 각 페이지에서 형식을 확인합니다.
6. **손상된 ESE DB 를 한 방식으로만 읽고 행 수를 확정합니다.** 읽는 방식에 따라 행 수가 달랐습니다(현장 관찰).
7. **DNS 질의를 사용자가 연 사이트로 씁니다.** Sysmon 22 는 프로세스가 이름을 물은 기록입니다. 브라우저 방문 기록과 맞춰 본 뒤에 씁니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 ○○ 에 ○○ 사이트를 보았습니다."
- 쓸 문장: "사용자 ○○ 의 ○○ 브라우저(프로필 ○○) History 에 `https://○○` 방문 기록이 있습니다. 방문 시각은 ○○(UTC) 입니다. 이동 방식의 기본 유형은 주소 입력(TYPED) 입니다. 이 방문에는 동기화된 방문 표시가 없습니다. 이 기록은 이 계정의 세션에서 이 브라우저 프로필이 이 주소를 불러왔음을 보여 줍니다. 사람이 화면을 보고 있었는지, 무엇을 읽었는지는 이 기록만으로 정할 수 없습니다."
- 기록이 비어 있을 때: "사용자 ○○ 의 ○○ 브라우저 History 에는 ○○ 부터 ○○ 까지의 방문 기록이 없습니다. `visits.id` 는 ○○ 에서 ○○ 사이가 비어 있습니다. 이 빈 구간은 기록을 지웠을 가능성을 보여 줍니다. 무엇을 언제 지웠는지는 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [크롬 계열 브라우저](../../02-artifacts/browsers/chrome-edge-whale/index.md) · [파이어폭스](../../02-artifacts/browsers/firefox/index.md) · [인터넷 익스플로러·옛 엣지](../../02-artifacts/browsers/ie-edgehtml/index.md) — 브라우저 기록의 구조입니다.
- [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) · [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) · [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) — 기록이 저장되는 형식입니다.
- [Sysmon 로그](../../02-artifacts/event-logs/sysmon/index.md) · [SRUM](../../02-artifacts/execution/system-resource-usage-monitor/index.md) — 브라우저 밖의 네트워크 기록입니다.
- [이 파일은 어디서 왔나](file-origin.md) — 받은 파일의 출처를 봅니다.
- [시크릿 모드로 무엇을 했나](private-browsing.md) — 기록이 남지 않는 창을 다룹니다.
- [자료를 밖으로 빼돌렸나](../exfiltration/data-exfiltration/index.md) — 웹으로 올린 파일을 봅니다.
- [그 시각에 PC 를 쓴 사람이 누구인가](user-attribution.md) — 계정에서 사람으로 좁힙니다.

## 참고 문헌

1. Microsoft Learn, "Sysmon - Sysinternals" (2026-09-10 판) — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
