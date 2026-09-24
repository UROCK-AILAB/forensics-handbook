# 슬랙 (Slack)

> 위치: 아티팩트 사전 > 메신저

## 한 줄 요약

슬랙 데스크톱 앱은 Electron 앱이고, 사용자 데이터는 `C:\Users\<사용자>\AppData\Roaming\Slack\` 에 있습니다. 대화 기록은 이 폴더의 `IndexedDB\` 안 LevelDB 파일에 남으며, 캐시·앱 로그·내려받은 파일 기록도 같은 폴더에 있습니다.

이 페이지의 폴더 설명은 한 공개 수집 정의 파일과 그 작성자의 관찰 메모를 따릅니다. 관찰 메모는 오래된 버전 기준일 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

지금의 슬랙 데스크톱 앱은 Electron 기반이고, Electron 앱은 Chromium 의 저장 방식을 그대로 씁니다. 그래서 앱 폴더 안에 브라우저와 같은 모양의 폴더(`Cache`, `Local Storage`, `IndexedDB` 등)가 생깁니다. 이 공통 구조는 [Electron·WebView2 앱 데이터 위치](../../01-foundations/app-mail-data/chromium-electron-webview2/teams-discord-slack.md) 와 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 에서 다루고, 이 페이지는 슬랙에 고유한 내용만 적습니다.

수집 정의 파일은 `IndexedDB\` 를 대화 기록(Chat Logs)으로 분류합니다. 앱 로그는 `logs\` 에, 내려받은 파일 기록은 `storage\` 에 남습니다. PC 에 남는 대화는 앱이 받아서 저장한 만큼이라고 보는 편이 안전합니다(해석).

## 위치와 버전별 차이

### 폴더 위치

| 항목 | 위치 | 근거 |
|---|---|---|
| 사용자 데이터 폴더 | `C:\Users\<사용자>\AppData\Roaming\Slack\` | 수집 정의 파일 |
| 프로그램 설치 폴더 | 알려진 바로는 사용자별 설치는 `%LOCALAPPDATA%\slack\`, MSI 로 한 전 컴퓨터 설치는 `Program Files` 아래 (버전마다 확인 필요) | 확인하지 못함 |
| Microsoft Store 판 데이터 | 알려진 바로는 `%LOCALAPPDATA%\Packages\` 아래 (버전마다 확인 필요) | 확인하지 못함 |

- `%APPDATA%` 는 사용자마다 따로 있습니다. 사용자 프로필마다 봅니다.
- 저장 위치가 Windows 버전에 따라 다르다는 자료는 찾지 못했습니다.

### 폴더별 내용

| 폴더 | 내용 (수집 정의 파일) |
|---|---|
| `IndexedDB\` | 대화 기록 |
| `Local Storage\leveldb` | LevelDB 파일 |
| `logs\` | Electron 앱 로그. 추가 기록이 여기 있습니다 |
| `Cache` | 캐시 파일. Chrome 브라우저 캐시처럼 해석할 수 있습니다 |
| `storage\` | 사용자 활동 기록이 있을 수 있습니다. 내려받은 파일 기록(slack-downloads)이 들어 있습니다 |

- `storage\` 안의 파일 이름은 이번에 확인하지 못했습니다.

### 버전별 차이

아래 "구조" 절의 관찰은 수집 정의 작성자가 주석으로 남긴 것입니다. 작성 연도는 알 수 없고, 근거로 2017년 대학 보고서를 달아 두었습니다. 요즘 버전에서 `IndexedDB\` 가 워크스페이스마다 나뉘는지, 앱을 꺼야 기록이 반영되는지는 확인하지 못했습니다. 그래서 검체의 슬랙 버전을 먼저 적고, 관찰 내용이 그 버전에도 맞는지 폴더를 보고 확인합니다.

## 구조

LevelDB 의 파일 구성(`.log`·`.ldb`·`MANIFEST-*`·`CURRENT`), 순서 번호, 압축 정리는 [LevelDB 저장소](../../01-foundations/database-log-formats/leveldb.md) 에서 다룹니다.

### IndexedDB — 수집 정의 작성자의 관찰

> 그림 자리: `Slack\IndexedDB\` 아래 폴더 하나 안에 워크스페이스별 `.log` 파일이 나란히 있고, 앱을 끈 뒤 `.ldb` 로 옮겨 가는 모습

| 관찰 | 분석할 때의 뜻 |
|---|---|
| `IndexedDB\` 안에 워크스페이스마다 나뉘지 않은 폴더가 하나 있었습니다 | 폴더 수로 워크스페이스 수를 셀 수 없습니다 |
| 워크스페이스 두 곳에 들어가 있어도 폴더가 따로 생기지 않았습니다 | 한 폴더 안에서 워크스페이스를 가려야 합니다 |
| 그 폴더 안에 워크스페이스마다 `.log` 파일이 하나씩 있었습니다. 예: `000039.log`, `000041.log` | 작성자는 분석을 이 `.log` 파일에 집중하라고 적었습니다 |
| 슬랙을 제대로 종료해야 새 기록이 이 폴더에 반영됐습니다 | 앱이 켜진 채 수집하면 최근 기록이 빠질 수 있습니다 |
| 앱을 끄면 `.log` 가 `.ldb` 로 바뀌었고, `.ldb` 에는 정보가 적어 보였다고 적었습니다 | `.ldb` 도 버리지 말고 풀어서 읽습니다. 아래 설명을 봅니다 |
| 입력한 글자마다 시각이 찍히는 기록은 없었습니다 | 글을 쓰던 과정을 글자 단위로 되짚을 수 없습니다 |
| 메시지 본문을 찾을 때 `subtype_` 를 검색어로 쓰라고 적었습니다 | 아래 "헥스로 한 번" 에서 따라갑니다 |

`.ldb` 에 정보가 적어 "보인" 이유는 확인하지 못했습니다. `.ldb` 는 LevelDB 의 표 파일이고 블록이 압축돼 있을 수 있는데, 압축된 블록은 풀기 전에는 문자열 검색에 걸리지 않습니다. 압축 정리 뒤에는 지운 레코드와 옛 값이 빠질 수도 있습니다. 두 가지 모두 [LevelDB 저장소](../../01-foundations/database-log-formats/leveldb.md) 에서 확인합니다.

### Local Storage

`Local Storage\leveldb` 는 크롬 계열 브라우저의 로컬 스토리지와 같은 LevelDB 폴더이고, 키와 값의 모양은 [크롬 계열 브라우저](../browsers/chrome-edge-whale/index.md) 의 웹 저장소 설명을 따릅니다. 슬랙이 여기에 무엇을 넣는지는 이번에 확인하지 못했습니다.

### Cache

수집 정의 파일은 `Cache` 를 Chrome 브라우저 캐시처럼 해석할 수 있다고 적었습니다. 캐시 형식은 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 에서 다루며, 대화에 올라온 이미지·파일 미리보기가 캐시에 남았는지 봅니다.

### logs

`logs\` 에는 Electron 앱 로그가 있는데, 수집 정의 파일은 추가 기록이 여기 있다고만 적었습니다. 로그 줄의 모양과 시각 형식은 확인하지 못했습니다.

### storage

`storage\` 에는 사용자 활동 기록이 있을 수 있고, 내려받은 파일 기록(slack-downloads)도 여기 들어 있습니다. 내려받은 파일 기록은 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 조사에서 파일이 들어온 경로를 보여 줄 수 있습니다.

### 암호화

쿠키 같은 값을 Chromium 방식으로 암호화하는지는 슬랙에 대해 확인하지 못했습니다. Chromium 방식은 `Local State` 파일에 둔 키를 DPAPI 로 보호하므로, 슬랙 폴더의 `Local State` 에 암호화 키 칸이 있는지 직접 봅니다. 키 칸이 있으면 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 의 암호화 설명과 [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) 를 봅니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 사용자 프로필에 `Slack` 폴더가 있으면, 그 Windows 계정에서 슬랙 데스크톱 앱이 실행된 적이 있습니다 | 누가 그 계정으로 앱을 조작했는지 |
| `IndexedDB\` 에 메시지 본문이 있으면, 이 PC 의 앱이 그 메시지를 받아 저장했습니다 | 워크스페이스의 전체 대화. 서버에만 있는 대화가 있을 수 있습니다 |
| `storage\` 에 내려받은 파일 기록이 있으면, 앱으로 파일을 내려받은 기록이 있습니다 | 그 파일이 지금 디스크에 있는지, 누가 열었는지 |
| `Cache` 에 이미지가 있으면 앱이 그 이미지를 받은 적이 있습니다 | 사용자가 그 이미지를 봤는지 |
| | 메시지가 없다고 대화가 없었다는 것. 앱이 켜진 채 수집했거나 압축 정리로 빠졌을 수 있습니다 |

### 보고서 문장

아래 사용자 이름과 개수는 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 A 의 슬랙 데이터 폴더 `IndexedDB\` 에서 메시지 본문으로 보이는 레코드 120건을 찾았습니다. `storage\` 에는 파일 5개를 내려받은 기록이 있습니다."
- 쓰면 안 되는 문장: "사용자 A 는 슬랙으로 파일 5개를 받아 외부로 넘겼습니다."

## 시각 해석

| 시각 | 자리 | 무엇이 바뀔 때 바뀌나 | 기준 |
|---|---|---|---|
| 메시지 시각 | 레코드 값 안 | 메시지마다 붙는 `ts` 값 | 아래 설명 |
| `.log`·`.ldb` 파일 시각 | 파일 시스템 | 앱이 파일을 쓰거나 새로 만들 때 | UTC |
| 로그 줄의 시각 | `logs\` 파일 안 | 앱이 로그를 쓸 때 | 확인하지 못함 |

LevelDB 레코드 자체에는 시각이 없고 순서 번호로 앞뒤만 알 수 있어서, 메시지 시각은 레코드 값 안에서 찾습니다.

슬랙 개발자 문서는 메시지 값 `ts` 가 유닉스 시각처럼 보이지만 실제로는 한 대화방 안에서 겹치지 않는 메시지 식별자라고 적습니다. 점 앞 부분은 유닉스 초로 만들어지고 UTC 기준이며, 푸는 법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다. 점 뒤 숫자는 식별을 위한 값이어서 정확한 소수 초로 읽지 않습니다. 앱이 PC 에 `ts` 를 그대로 저장하는지는 버전마다 확인합니다.

관찰 메모대로 앱을 꺼야 기록이 반영되면, `.ldb` 파일의 시각은 앱을 끈 때에 가까울 수 있으므로(해석) 이 시각을 메시지 시각으로 쓰지 않습니다.

- 로그 줄의 시각이 UTC 인지 현지 시각인지는 시험 환경에서 확인합니다.

## 함정과 한계

- **옛 관찰을 지금 버전에 그대로 씁니다.** 관찰 메모는 2017년 보고서를 근거로 합니다. 폴더 구성이 바뀌었을 수 있습니다.
- **앱이 켜진 채 수집하고 끝냅니다.** 관찰 메모에서는 앱을 제대로 종료해야 새 기록이 반영됐습니다. 라이브 수집에서 앱을 끌지 말지는 조사 목적에 따라 정하고, 무엇을 했는지 기록합니다. 방법은 [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) 에서 다룹니다.
- **`.ldb` 를 빈 파일로 봅니다.** 압축된 블록은 풀어야 보입니다.
- **한 인코딩으로만 검색합니다.** 문자열은 한 바이트 문자로도, UTF-16LE 로도 저장될 수 있습니다. 두 모양을 모두 검색합니다. 인코딩은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.
- **폴더 하나를 워크스페이스 하나로 봅니다.** 관찰 메모에서는 워크스페이스 두 곳이 한 폴더를 같이 썼습니다.
- **기본 위치만 봅니다.** 설치형과 스토어 판의 위치가 다를 수 있습니다. 경로를 모르면 [Electron·WebView2 앱 데이터 위치](../../01-foundations/app-mail-data/chromium-electron-webview2/teams-discord-slack.md) 의 방법처럼 `Local State` 이름으로 찾습니다.
- **같은 메시지가 여러 번 나와 여러 건으로 셉니다.** LevelDB 에는 같은 키의 레코드가 여러 개 남을 수 있습니다. 순서 번호로 나중 기록을 가립니다.
- **지운 흔적을 앱 폴더에서만 찾습니다.** 사용자가 로그아웃하거나 앱 데이터를 지우면 무엇이 지워지는지는 확인하지 못했습니다. 지운 파일의 흔적은 [USN 변경 저널](../filesystem/usnjrnl.md) 과 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에서도 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

관찰 메모는 메시지 본문을 찾을 때 `subtype_` 를 검색어로 쓰라고 했습니다. 아래 바이트는 이 문자열을 두 인코딩으로 바꿔 만든 예시이며, 검체에서 나온 값이 아닙니다.

```
한 바이트 문자   73 75 62 74 79 70 65 5F                            subtype_
UTF-16LE         73 00 75 00 62 00 74 00 79 00 70 00 65 00 5F 00    s.u.b.t.y.p.e._.
```

1. `IndexedDB\` 아래 폴더를 통째로 복사합니다. 원본 폴더에서 바로 작업하지 않습니다.
2. 복사한 `.log` 파일에서 위 두 바이트 열을 모두 검색합니다.
3. 찾은 자리 앞뒤에서 메시지 본문으로 보이는 문자열과 `ts` 로 보이는 숫자 문자열을 찾습니다.
4. 찾은 자리가 어느 LevelDB 레코드 안인지 봅니다. 레코드의 키와 순서 번호를 읽는 법은 [LevelDB 저장소](../../01-foundations/database-log-formats/leveldb.md) 에 있습니다.
5. 같은 본문이 여러 번 나오면 순서 번호를 비교해 어느 것이 나중 기록인지 가립니다.
6. `.ldb` 파일은 블록을 풀어 같은 검색을 되풀이합니다.

### 공개 도구로 한 번

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| LevelDB·IndexedDB 를 읽는 공개 파서 | `IndexedDB\` 와 `Local Storage\leveldb` 의 레코드를 키·값·순서 번호로 뽑습니다 |
| 크롬 캐시를 읽는 공개 도구 | `Cache` 폴더의 항목과 URL 을 뽑습니다 |
| 텍스트 편집기, JSON 조회 도구 | `logs\`·`storage\` 의 파일과 `Local State` 를 봅니다 |

도구가 낸 메시지 수와 헥스 검색으로 찾은 수를 맞춰 보고, 차이가 나면 헥스로 돌아갑니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 점 |
|---|---|
| [설치 프로그램](../system-account/uninstall.md) · [스토어 앱 설치 목록](../system-account/appx-staterepository.md) | 설치 방식과 설치 폴더 |
| [프리페치](../execution/prefetch/index.md) · [AmCache](../execution/amcache-hve/index.md) | 슬랙 실행 파일의 경로와 실행 시각 |
| [SRUM](../execution/system-resource-usage-monitor/index.md) | 슬랙 앱의 네트워크 사용량 기록이 있는지 |
| [윈도 알림 기록](../execution/wpndatabase-db.md) | 슬랙 알림이 남았는지 |
| [다운로드 출처 표시](../filesystem/zone-identifier.md) | `storage\` 에 기록된 내려받은 파일에 출처 표시가 붙었는지 |
| [크롬 계열 브라우저](../browsers/chrome-edge-whale/index.md) | 브라우저에서 슬랙 웹을 연 기록이 있는지 |
| [마스터 파일 테이블](../filesystem/mft.md) | 내려받은 파일이 디스크 어디에 생겼는지 |

- 같은 Electron 계열 메신저는 [마이크로소프트 팀즈](teams.md) 와 [디스코드](discord.md) 페이지를 봅니다.
- 조사 전체 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 에서 다룹니다.

## 실습

슬랙이 든 공개 검체는 이번에 확인하지 못했습니다. Windows 가상 머신에 슬랙 데스크톱 앱을 설치해 직접 시험하고, 시험 전에 앱 버전과 Windows 버전을 적어 둡니다.

1. 워크스페이스 두 곳에 로그인합니다. `IndexedDB\` 아래 폴더가 몇 개 생깁니까? `.log` 파일은 몇 개입니까?
2. 메시지를 주고받은 뒤, 앱을 끄기 전과 끈 뒤에 `.log`·`.ldb` 파일이 어떻게 바뀝니까?
3. `.log` 에서 `subtype_` 를 검색하면 보낸 메시지 본문을 찾을 수 있습니까? 한 바이트 문자와 UTF-16LE 중 어느 모양으로 걸립니까?
4. 보낸 시각을 적어 두고, 레코드 안의 `ts` 값과 맞춥니다. `ts` 는 어떤 모양입니까?
5. 파일을 내려받은 뒤 `storage\` 에 어떤 기록이 생깁니까?
6. 슬랙 폴더의 `Local State` 에 암호화 키 칸이 있습니까?
7. 설치형과 스토어 판의 데이터 폴더가 다릅니까?

## 참고 문헌

- Slack developer docs, *Retrieving messages* (`ts` 설명) — https://docs.slack.dev/messaging/retrieving-messages
- KapeFiles, *Targets/Apps/Slack.tkape* (작성 Andrew Rathbun, Chad Tilbury, 버전 1.1) — https://raw.githubusercontent.com/EricZimmerman/KapeFiles/master/Targets/Apps/Slack.tkape
