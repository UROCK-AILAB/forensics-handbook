---
title: "디스코드"
parent: "아티팩트 · 메신저"
nav_order: 2080
---

# 디스코드 (Discord)

> 위치: 아티팩트 사전 > 메신저

## 한 줄 요약

디스코드는 사용자 데이터를 `%APPDATA%\discord` 에 두며, 폴더 안은 브라우저와 같은 Chromium 구성입니다. HTTP 캐시에는 채널 메시지 API 응답, 첨부 파일, 아바타가 남을 수 있어서 서버에서 지운 메시지가 캐시에 남아 있을 수 있습니다. 앱 고유 파일 `userDataCache.json` 에는 계정·서버 상태가 담기고, `tokens` 키도 있습니다. 관찰한 PC 에서는 프로그램 폴더가 거의 비었는데도 사용자 데이터는 그대로 남아 있었습니다.

"관찰" 은 디스코드 프로그램을 지운 뒤 사용자 데이터만 남은 PC 기준입니다.

## 무엇을 기록하나 · 왜 생기나

디스코드 폴더에는 Chromium 이 만드는 캐시·쿠키·Local Storage 가 있습니다. (관찰) 관찰한 캐시 키에 채널 메시지 API 주소가 있었는데, 앱이 서버 API 로 메시지를 받아 온다는 단서입니다. (관찰) 이 응답과 첨부·아바타 이미지가 HTTP 캐시에 남을 수 있습니다.

공개 도구 discord_cache_parser 의 README 는 캐시에서 첨부 파일·이미지·썸네일, 웹후크 URL 과 API 호출, JSON API 응답 속 메시지, 아바타를 되살린다고 적었고, 이 결과를 삭제된 내용 복구와 타임라인 재구성에 쓴다고 적었습니다. (discord_cache_parser README)

앱은 창 위치, 계정 상태, 로그, 오류 보고 대기열도 같은 폴더에 적습니다. (관찰)

CCL 글은 Local Storage·IndexedDB 를 LevelDB 로 저장하는 앱 목록에 디스코드를 넣었습니다. (CCL 글)

## 위치와 버전별 차이

| 폴더 | 내용 | 근거 |
|---|---|---|
| `%APPDATA%\discord` | 사용자 데이터. 폴더 이름이 소문자입니다 | 관찰 |
| `%LOCALAPPDATA%\Discord` | 프로그램 | 관찰 |

- `%APPDATA%\discord` 는 Electron 의 기본 규칙 `%APPDATA%\<앱 이름>` 과 맞습니다. (관찰, Electron 문서)
- Electron 앱 폴더의 일반 구조는 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 에서 다룹니다.
- `%APPDATA%\discord\1.0.9253` 이라는 빈 폴더가 있었습니다. 앱 버전 번호의 단서로 보입니다. (관찰)
- PTB·Canary 같은 다른 판의 폴더 이름은 확인하지 못했습니다.
- 두 폴더 모두 사용자 프로필 아래에 있습니다. 사용자마다 따로 봅니다.

### 프로그램이 지워진 경우 (관찰)

관찰 PC 의 `%LOCALAPPDATA%\Discord` 에는 `Update.exe` 와 1바이트 `.dead` 파일만 있고 `app-*` 폴더는 없었지만, `%APPDATA%\discord` 의 데이터는 그대로 남아 있었습니다.

해석: 프로그램은 지워졌거나 지워지는 중이었고, 사용자 데이터는 남았습니다. 단정하지 않습니다. `.dead` 파일의 뜻과 정상 설치 때 `%LOCALAPPDATA%\Discord\app-<버전>` 이 생기는지는 확인하지 못했습니다.

## 구조

### Chromium 구성 (관찰)

`%APPDATA%\discord` 바로 아래에 아래 항목이 있었습니다. `Default` 같은 프로필 하위 폴더는 없었습니다.

| 항목 | 내용 |
|---|---|
| `Cache\Cache_Data` | HTTP 캐시 |
| `Code Cache`, `GPUCache` | 스크립트·GPU 캐시 |
| `Local Storage\leveldb` | Local Storage |
| `Session Storage` | 세션 저장소 |
| `Network` | `Cookies`, `TransportSecurity` 등 |
| `Service Worker`, `blob_storage` | 서비스 워커, blob 저장소 |
| `Local State`, `Preferences`, `DIPS` | Chromium 이 만드는 설정·상태 파일 |

- `IndexedDB` 폴더는 없었습니다. (관찰)
- `Local State` 의 `os_crypt` 에는 `encrypted_key` 와 `audit_enabled` 만 있었습니다. App-Bound 키는 없었습니다. (관찰)
- 쿠키 암호화와 캐시 형식은 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 에서 다룹니다. Local Storage 형식은 [LevelDB 저장소](../../01-foundations/database-log-formats/leveldb.md) 에서 다룹니다.

### 디스코드 고유 파일 (관찰)

| 파일·폴더 | 내용 |
|---|---|
| `settings.json` | 창 위치(`WINDOW_BOUNDS`), 최대화 여부, 여러 기능 플래그 |
| `userDataCache.json` | 계정·서버 상태. 관찰 PC 에서 약 5.4MB |
| `logs\` | 앱 로그 |
| `sentry\scope_v3.json`, `sentry\queue\queue-v2.json` | 오류 보고 대기열 |
| `module_data\` | `crashlogs`, `discord_utils`, `discord_voice` |
| `quotes.json`, `badge-*.ico` | 뜻은 확인하지 못했습니다 |

`userDataCache.json` 의 최상위 키는 `…Store` 이름들이었습니다. 예는 아래와 같습니다. 값은 열지 않았습니다. (관찰)

`SelectedGuildStore`, `MultiAccountStore`, `user_id_cache`, `FriendGroupsStoreV2`, `GuildRoomStore`, `tokens`

- 키 이름으로 보아 선택한 서버, 여러 계정, 친구 그룹 같은 상태가 담긴 것으로 보입니다.
- `tokens` 키가 있으므로 인증 정보가 들어 있을 수 있습니다(해석). 값을 보고서에 옮기지 않습니다.
- 이 파일이 Local Storage 의 사본인지, 언제 쓰이는지는 확인하지 못했습니다.

`logs\` 에는 아래 파일이 있었습니다. (관찰)

`DiscordSystemHelper_user_rCURRENT.log`, `Discord_updater_rCURRENT.log`, `discord-webrtc_0`, `discord_krisp.log`, `discord_media_rCURRENT.log`, `discord_utils.log`, `renderer_js.log`

로그 줄의 형식과 시각 표기는 확인하지 못했습니다.

### 캐시에 남는 것 (관찰)

- `Cache\Cache_Data` 는 블록 파일 (blockfile) 형식이었습니다. `index`, `data_0` ~ `data_3`, `f_xxxxxx` 파일이 있었고, 모두 178개였습니다.
- 캐시 키(URL)의 숫자 ID 를 가리고 종류를 세어 봤습니다.

| 캐시 키 모양 | 뜻 |
|---|---|
| `https://discordapp.com/api/v9/channels/<id>/messages` | 채널 메시지 API 응답. 관찰 PC 에서 3건 |
| `https://discordapp.com/api/v9/users/…` | 사용자 정보 API |
| `https://discordapp.com/api/v9/guilds/<id>` | 서버(길드) 정보 API |
| `https://discordapp.com/api/v9/channels/<id>` | 채널 정보 API |
| `https://cdn.discordapp.com/avatars/<id>/<hash>…` | 아바타 이미지 |
| `https://cdn.discordapp.com/icons/<id>/<hash>…` | 서버 아이콘 |
| `https://cdn.discordapp.com/app-icons/…`, `…/assets/…` | 앱 아이콘과 자원 |

- 관찰 PC 에서 호스트는 `discord.com` 이 아니라 `discordapp.com` 이었습니다. API 버전은 `v9` 였습니다.
- `Local Storage\leveldb` 의 출처 키는 `_https://discordapp.com` 이었습니다.

## 증거로서 의미

### 증명하는 것

- **이 계정이 디스코드를 썼다는 것.** 사용자 프로필 아래에 데이터 폴더가 있습니다.
- **프로그램을 지운 뒤에도 남은 사용.** 관찰 PC 처럼 프로그램 폴더가 비어도 사용자 데이터는 남을 수 있습니다.
- **앱이 받아 온 서버·채널·사용자.** 캐시 키의 `guilds`·`channels`·`users` ID 는 앱이 그 대상의 정보를 받아 왔다는 기록입니다.
- **앱이 받아 온 메시지.** `channels/<id>/messages` 응답이 캐시에 남으면, 그 시점에 앱이 받은 메시지를 볼 수 있습니다.
- **첨부·이미지.** 캐시에서 첨부 파일·이미지·썸네일을 되살릴 수 있습니다. (discord_cache_parser README)
- **여러 계정 사용의 단서.** `userDataCache.json` 에 `MultiAccountStore` 키가 있습니다.

### 증명하지 못하는 것

- **사용자가 메시지를 읽었는지.** 캐시에는 앱이 받아 온 응답이 남습니다. 화면에서 읽었다는 뜻은 아닙니다.
- **메시지가 지금도 서버에 있는지.** 캐시는 받아 온 시점의 사본입니다.
- **사용자가 보냈는지.** 이 페이지는 응답 JSON 의 칸을 확인하지 못했습니다. 보낸 사람은 응답 안의 칸을 보고 판단합니다.
- **캐시에 없는 대화.** 캐시 크기와 교체에 따라 얼마나 남는지 달라집니다. 없다고 대화가 없었다고 말할 수 없습니다.
- **누가 자판 앞에 있었는지.** 계정까지만 알려 줍니다. 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.

해석: 채널을 연 순간의 메시지 API 응답이 캐시에 남으면, 서버에서 나중에 지운 메시지도 캐시에서 보일 수 있습니다. 얼마나 오래 남는지는 확인하지 못했습니다.

보고서에는 "피의자가 이 메시지를 봤다" 가 아니라 이렇게 씁니다. "A 계정의 디스코드 HTTP 캐시에 채널 X 의 메시지 API 응답이 있다. 응답에는 이 메시지가 들어 있다. 캐시 항목의 시각은 Y 이다."

## 시각 해석

| 시각 | 무엇이 바뀔 때 | 주의 |
|---|---|---|
| 캐시 항목의 시각 | 앱이 응답을 받아 캐시에 적을 때 | 형식과 기준은 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 의 캐시 형식에서 다룹니다 |
| 응답 JSON 안의 시각 | 서버가 적은 값 | 칸 이름과 형식은 확인하지 못했습니다. [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 후보 형식을 봅니다 |
| 로그 줄 시각 | 로그를 쓸 때 | 형식을 확인하지 못했습니다. UTC 인지 현지 시각인지 파일 수정 시각과 맞춰 봅니다 |
| 파일 시스템 시각 | 파일을 다시 쓸 때 | UTC. [마스터 파일 테이블](../filesystem/mft.md) 에서 봅니다 |

- 디스코드의 숫자 ID 에서 시각을 읽어 내는 방법이 알려져 있습니다. 이 페이지는 공식 문서로 확인하지 못해 싣지 않습니다.
- 현지 시각으로 옮길 때는 [시간대 설정](../system-account/time-zone.md) 을 확인합니다.

## 함정과 한계

- **`discord.com` 만 찾습니다.** 관찰 PC 의 캐시와 Local Storage 는 `discordapp.com` 이었습니다. 두 호스트를 모두 찾습니다.
- **IndexedDB 를 찾습니다.** 관찰 PC 에는 IndexedDB 폴더가 없었습니다. 캐시와 Local Storage 가 주된 자료입니다.
- **`Default` 프로필을 찾습니다.** 프로필 하위 폴더 없이 `%APPDATA%\discord` 바로 아래에 Chromium 구성이 있었습니다. `Default` 를 찾는 도구는 이 폴더를 건너뛸 수 있습니다.
- **프로그램 폴더로 설치 여부를 판단합니다.** 관찰 PC 처럼 프로그램이 없어도 사용자 데이터가 남을 수 있습니다.
- **토큰을 보고서에 옮깁니다.** `userDataCache.json` 의 `tokens` 값은 인증 정보일 수 있습니다. 값은 옮기지 않고 키가 있다는 사실만 적습니다.
- **증거 PC 에서 앱을 엽니다.** 앱을 열면 캐시가 새로 쓰이고 옛 항목이 밀려날 수 있습니다. 폴더를 먼저 복사합니다. 켜진 PC 는 [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) 순서를 따릅니다.
- **캐시가 모든 메시지를 담는다고 봅니다.** 관찰 PC 의 메시지 API 캐시 키는 3건뿐이었습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 검색 문자열은 ASCII 로 만든 예시입니다. 실제 검체에서 나온 값이 아닙니다.

1. `Cache\Cache_Data` 폴더를 통째로 복사합니다.
2. `data_*` 와 `f_*` 파일에서 아래 바이트를 찾습니다. `/api/v9/channels/` 를 ASCII 로 적은 것입니다.

   ```
   2F 61 70 69 2F 76 39 2F 63 68 61 6E 6E 65 6C 73 2F      /api/v9/channels/
   ```

3. 찾은 자리 뒤에 `/messages` 가 이어지면 채널 메시지 API 의 캐시 키입니다.
4. 같은 검색을 `discordapp.com` 과 `discord.com` 으로도 합니다.
5. 캐시 키와 응답 본문을 잇는 구조, 본문이 압축돼 있는지는 [크롬 계열 앱 공통 구조](../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 의 캐시 형식에서 확인합니다.
6. 문자열 검색 방법은 [파일 내용 검색](../../03-techniques/analysis/content-search/index.md) 에서 다룹니다.

### 공개 도구로 한 번

공개 도구의 예로 discord_cache_parser 가 있습니다. README 는 캐시에서 첨부·이미지·썸네일, 웹후크 URL, API 응답 속 메시지, 아바타를 되살린다고 적었습니다. README 에는 폴더 경로와 형식 설명이 없었습니다. 이 페이지에서는 도구 자체의 동작을 시험하지 않았습니다.

- 도구가 낸 API 응답 수와 헥스 검색으로 찾은 캐시 키 수를 맞춰 봅니다.
- 크롬 계열 캐시를 읽는 다른 도구로도 같은 폴더를 읽어 봅니다.
- 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 점 |
|---|---|
| [설치 프로그램](../system-account/uninstall.md) | 설치·제거 기록과 프로그램 폴더 상태를 맞춰 봅니다 |
| [프리페치](../execution/prefetch/index.md) | 디스코드 실행 시각을 봅니다 |
| [SRUM](../execution/system-resource-usage-monitor/index.md) | 앱이 네트워크를 쓴 시간대를 봅니다 |
| [윈도 알림 기록](../execution/wpndatabase-db.md) | 디스코드 알림이 남았는지 봅니다 |
| [다운로드 출처 표시](../filesystem/zone-identifier.md) | 디스코드에서 받은 파일에 출처 표시가 붙었는지 봅니다 |
| [크롬 계열 브라우저](../browsers/chrome-edge-whale/index.md) | 브라우저로 디스코드 웹을 쓴 흔적을 봅니다 |

조사 전체 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 에서 다룹니다. 프로그램을 지운 흔적은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 와 함께 봅니다.

## 실습

디스코드가 들어간 공개 검체는 확인하지 못했습니다. Windows 11 가상 머신에 앱을 설치해 직접 시험합니다. 시험 전에 앱 버전을 적어 둡니다.

1. 로그인 뒤 `%APPDATA%\discord` 에 어떤 폴더가 생깁니까? `Default` 프로필 폴더가 있습니까?
2. 채널 하나를 연 뒤 캐시에 `channels/<id>/messages` 키가 생깁니까? 호스트는 `discord.com` 입니까, `discordapp.com` 입니까?
3. 상대가 메시지를 지운 뒤, 앱을 다시 열기 전 캐시 사본에 그 메시지가 남아 있습니까?
4. 앱을 제거한 뒤 `%APPDATA%\discord` 와 `%LOCALAPPDATA%\Discord` 에는 무엇이 남습니까? `.dead` 파일이 생깁니까?
5. `logs\` 의 로그 줄 시각은 UTC 입니까, 현지 시각입니까? 파일 수정 시각과 비교합니다.

## 참고 문헌

- jwdfir, discord_cache_parser — README — https://github.com/jwdfir/discord_cache_parser
- Electron docs, *app* (`app.getPath`) — https://www.electronjs.org/docs/latest/api/app
- CCL Solutions Group, "Hang on! That's not SQLite! Chrome, Electron and LevelDB" — https://www.cclsolutionsgroup.com/post/hang-on-thats-not-sqlite-chrome-electron-and-leveldb
