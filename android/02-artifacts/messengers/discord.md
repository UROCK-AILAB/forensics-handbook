---
title: "디스코드"
parent: "아티팩트 · 메신저"
nav_order: 1010
---

# 디스코드 (Discord)

디스코드 앱은 계정마다 따로 두는 `kv-storage` 폴더의 SQLite 파일에 메시지를 JSON 으로 남기고, 서버에서 받아 온 API 응답을 `http-cache` 폴더에 따로 쌓아 둡니다.

## 무엇을 기록하나 · 왜 생기나

디스코드 앱(패키지 이름 `com.discord`)의 메시지 흔적은 두 곳에 나뉘어 남습니다[1][2]. 첫째는 앱의 키-값 저장소(kv-storage)로, 로그인한 계정마다 폴더가 하나씩 있고 그 안의 SQLite 파일에 메시지가 한 건씩 JSON 으로 들어 있습니다[1]. 둘째는 앱의 HTTP 응답 캐시로, 앱이 디스코드 서버의 API 를 불러 받은 응답이 파일로 남습니다[2]. 이 캐시에는 채널 메시지 목록과 사용자 프로필 응답이 들어 있고, 첨부 이미지·아바타·서버 아이콘·스티커 이미지도 함께 남습니다[2].

두 곳에 남는 메시지가 서로 다르다는 점이 중요합니다. ALEAPP 시험 이미지에서 캐시에 있던 메시지 169건 가운데 111건은 kv-storage 에도 있었지만 58건은 캐시에만 있었고, kv-storage 의 메시지 2건은 어느 캐시 페이지에도 없었습니다[2]. 그래서 디스코드를 분석할 때는 두 곳을 모두 봅니다.

이 페이지의 사실은 공개 도구 ALEAPP 의 디스코드 모듈 두 개가 적어 둔 설명을 바탕으로 합니다. 디스코드 공식 문서는 직접 열지 않았고, ALEAPP 이 인용한 내용만 옮겼습니다.

## 위치와 버전별 차이

경로는 모두 앱 데이터 폴더 기준이고, 앱 데이터 폴더의 구조는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 에서 다룹니다.

| 흔적 | 경로 | 형식 |
|---|---|---|
| 메시지 저장소 | `files/kv-storage/@account.<계정 ID>/a` | SQLite. 파일 이름이 `a` 한 글자 |
| API 응답 캐시 | `cache/http-cache/<32자리 16진수>.0` | URL·상태 줄·응답 헤더 |
| | `cache/http-cache/<같은 이름>.1` | 응답 본문 |
| | `cache/http-cache/journal` | 캐시 항목 상태 기록 |

폴더 이름 `@account.<숫자>` 의 숫자가 그 기기에 로그인한 계정 ID 이고, 계정이 여럿이면 폴더도 여럿입니다[1]. 응답 캐시는 OkHttp 라이브러리의 DiskLruCache 형식이라서 항목 하나가 `.0` 과 `.1` 두 파일로 짝을 이룹니다[1][2].

앱 데이터 폴더는 시스템이 다른 앱의 접근을 막는 앱 내부 저장소라서 일반 adb 권한으로는 바로 읽을 수 없고, Android 10(API 29) 이상에서는 이 위치가 암호화됩니다[3]. 확보 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 를 봅니다.

ALEAPP 이 이 모듈들을 시험한 추출 이미지는 아래와 같습니다[1][2]. 기기 이름은 이미지 이름에서 읽은 것이고, 앱 버전코드는 모듈에 적힌 것만 옮겼습니다.

| Android | 시험 이미지 | 디스코드 앱 버전코드 |
|---|---|---|
| 13 | falken_a326u | 적혀 있지 않음 |
| 13 | 갤럭시 S20 | 310011 |
| 13 | userb2 | 255014 |
| 14 | 픽셀 7a | 239015 |
| 16 | 픽셀 8 Pro | 333012 |
| 17 | 픽셀 8 Pro | 적혀 있지 않음 |

ALEAPP 시험 이미지 31개 가운데 응답 캐시가 있던 것은 6개뿐이었습니다[2]. 삼성 기기인 갤럭시 S20(Android 13) 이미지에서는 kv-storage 메시지가 1건, 캐시 메시지가 0건이었습니다[1][2]. 삼성 One UI 에서 경로나 구조가 다르다는 자료는 찾지 못했습니다.

## 구조

SQLite 파일 자체의 구조는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.

### kv-storage 의 messages0 표

`a` 파일 안의 `messages0` 표에는 `data` 칸이 있고, 이 칸의 값은 앞에 길이 바이트가 붙은 JSON 입니다[1]. ALEAPP 은 인쇄할 수 없는 문자를 지운 뒤 JSON 으로 읽습니다[1].

JSON 최상위에는 `id`, `channelId`, `message` 가 있고, `message` 아래 필드는 아래와 같습니다[1].

| 필드 | 뜻 |
|---|---|
| `timestamp` | 메시지 시각(ISO 8601 문자열) |
| `edited_timestamp` | 고친 시각 |
| `author` | 보낸 사람(`id`, `username`, `avatar`) |
| `content` | 본문 |
| `attachments` | 첨부(`filename`, `url`, `proxy_url`) |
| `mentions`, `mention_roles` | 언급한 사용자·역할 |
| `pinned` | 고정 여부 |

메시지 종류(type) 값은 ALEAPP 이 디스코드 개발자 문서에서 인용한 것으로, 0 이 일반 메시지(DEFAULT), 3 이 통화(CALL), 7 이 사용자 참여(USER_JOIN), 19 가 답장(REPLY)입니다[1][2].

### http-cache 의 API 응답

캐시 항목의 URL 을 보면 어떤 API 응답인지 알 수 있습니다[2]. `/api/v<숫자>/channels/<채널 ID>/messages` 응답은 메시지 JSON 목록이고, 같은 메시지 ID 가 캐시 페이지 여러 개에 겹쳐 있기도 해서 시험 이미지에서는 한 메시지가 최대 5개 페이지에 나왔습니다[2]. `/api/v<숫자>/users/<사용자 ID>/profile` 응답에는 사용자 이름, 표시 이름, 자기소개(bio), 연결된 계정, 공통 서버가 들어 있습니다[2].

`.0` 파일의 응답 헤더에는 `OkHttp-Sent-Millis` 와 `OkHttp-Received-Millis` 가 있어서 앱이 요청을 보낸 시각과 응답을 받은 시각을 알 수 있고, 시험 이미지의 317개 항목 모두에 이 두 헤더가 있었습니다[2]. `Content-Encoding` 헤더가 gzip 이면 `.1` 본문도 gzip 으로 압축돼 있습니다[2]. `journal` 파일에는 항목마다 DIRTY·CLEAN·REMOVE 줄이 쌓이고(항목을 읽을 때 남는 READ 줄도 있습니다), 마지막 상태 줄로 그 항목의 상태를 봅니다[2]. 시험 이미지에서는 모든 항목이 CLEAN 이었습니다[2].

시험 이미지 캐시의 317개 항목 가운데 255개는 JSON, 55개는 이미지였습니다[2]. kv-storage 쪽 첨부는 URL 경로에서 서명·크기 인자를 뺀 부분이 캐시 항목 URL 과 같은 것을 찾아 잇는데, 시험 이미지에서 첨부 12개 가운데 7개는 캐시에서 찾았고 4개는 캐시 사본이 없었습니다[1].

## 증거로서 의미

**증명하는 것.** kv-storage 의 메시지 행은 그 채널에 그 시각의 메시지가 기기에 저장돼 있었다는 기록입니다. `author.id` 가 폴더 이름의 계정 ID 와 같으면 이 기기에 로그인한 계정이 보낸 메시지로 봅니다[1]. 이 방향은 두 값을 견주어 계산한 결과라서 보고서에 근거를 함께 적습니다. 캐시 항목의 `OkHttp-Sent-Millis`·`OkHttp-Received-Millis` 는 앱이 그 API 를 부른 시각이라서, 앱이 그 무렵 서버와 통신하며 해당 채널이나 프로필을 받아 왔다는 사실을 보여 줍니다[2].

**증명하지 못하는 것.** 프로필 응답이 캐시에 있다는 것은 그 시각에 앱이 그 프로필을 받아 왔다는 뜻일 뿐이고, 그 프로필이 누구의 것인지나 왜 받아 왔는지를 말해 주지 않습니다[2]. 채널 메시지가 캐시에 있다고 해서 사용자가 그 메시지를 읽었다고 할 수도 없습니다. 캐시 헤더의 시각은 지금 남아 있는 응답을 받은 한 번의 시각이라서, 그 전에 같은 요청을 몇 번 했는지는 이 값으로 알 수 없습니다. 첨부의 캐시 사본이 없더라도 첨부가 기기에서 열리지 않았다고 단정할 수 없는데, 시험 이미지에서도 첨부 12개 가운데 4개는 캐시 사본이 없었습니다[1]. 메시지 종류가 3(CALL) 인 행은 통화 메시지 항목이고, 통화가 얼마나 이어졌는지는 이 값만으로 알 수 없습니다.

보고서에는 "이 사용자와 대화했다" 보다 "이 계정 폴더의 kv-storage 에 이 채널의 메시지가 있고, 그중 이 시각의 메시지는 `author.id` 가 계정 ID 와 같다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

| 값 | 위치 | 형식 |
|---|---|---|
| `timestamp`, `edited_timestamp` | 메시지 JSON | ISO 8601 문자열(예: `2024-02-08T16:44:47.780000+00:00`) |
| `OkHttp-Sent-Millis` | 캐시 `.0` 헤더 | 유닉스 밀리초. 요청을 보낸 시각 |
| `OkHttp-Received-Millis` | 캐시 `.0` 헤더 | 유닉스 밀리초. 응답을 받은 시각 |

메시지 시각은 유닉스 숫자가 아니라 ISO 8601 문자열이고, 예시처럼 끝에 시간대 차이가 붙어 있습니다[2]. `+00:00` 은 UTC 라는 뜻이고, 현지 시각으로 옮길 때는 [시간대와 시각 설정](../system-account/time-zone.md) 을 함께 봅니다. 두 종류의 시각은 뜻이 다릅니다. 메시지 `timestamp` 는 메시지 JSON 에 든 메시지 자체의 시각이고, 캐시 헤더의 시각은 이 기기의 앱이 그 응답을 받아 온 시각이라 메시지 시각보다 한참 뒤일 수 있습니다. 시각 형식 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

## 함정과 한계

kv-storage 와 캐시 가운데 하나만 보면 메시지가 빠집니다. 시험 이미지에서도 58건은 캐시에만, 2건은 kv-storage 에만 있었습니다[2]. 반대로 두 곳을 합칠 때는 같은 메시지가 kv-storage 와 여러 캐시 페이지에 겹쳐 나오니 메시지 ID 로 중복을 걸러 냅니다[2].

ALEAPP 은 kv-storage 를 읽을 때 `-wal`·`-shm`·`-journal` 짝 파일도 함께 경로에 넣습니다[1]. 확보할 때 짝 파일을 모두 복사하고 사본을 엽니다.

OkHttp 는 GET 응답만 캐시합니다[2]. 그래서 캐시에 있는 메시지는 앱이 서버에서 받아 온 목록이고, GET 이 아닌 요청의 응답은 캐시에서 찾을 수 없습니다. 캐시가 비어 있거나 없다고 해서 앱을 쓰지 않았다고 볼 수도 없는데, 시험 이미지 31개 가운데 캐시가 있던 이미지는 6개뿐이었습니다[2].

시험 이미지에서는 `edited_timestamp` 가 모두 비어 있고 `pinned` 는 모두 False 였습니다[1]. 이 두 칸이 실제 검체에서 어떻게 채워지는지는 시험 자료로 확인되지 않았으니, 값이 있으면 앱에서 같은 동작을 재현해 확인한 뒤 해석합니다.

앱을 지우면 앱 전용 저장소의 파일도 지워져서[3] 이 페이지의 흔적이 남지 않습니다. 이때는 [설치된 앱](../app-usage/packages/index.md) 과 [앱 사용 기록](../app-usage/usagestats/index.md) 으로 앱이 있었는지를 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

`a` 파일 사본을 헥스 편집기로 열면 첫 16바이트가 일반 SQLite 머리 문자열로 시작합니다. 아래는 SQLite 형식 명세로 만든 예시이고 특정 검체에서 나온 값이 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
```

그다음 문자열 `"channelId"` 로 `a` 파일과 `-wal` 파일을 검색합니다. `data` 칸의 JSON 은 헥스 화면에서도 글자로 보이지만 앞에 길이 바이트가 붙어 있어서, JSON 이 시작하는 `{` 앞의 몇 바이트는 글자가 아닌 값으로 보입니다[1]. 표에서 지워졌지만 빈 공간에 남은 JSON 조각이 보이면 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 따라 다룹니다.

응답 캐시의 `.0` 파일은 URL 과 헤더가 글자로 들어 있어 헥스 화면이나 텍스트 편집기로 바로 읽을 수 있습니다[1][2]. `OkHttp-Sent-Millis` 를 검색해 값을 찾고, 같은 이름의 `.1` 파일이 gzip 인지를 `.0` 의 `Content-Encoding` 헤더로 확인합니다.

### 공개 도구로 한 번

공개 도구 ALEAPP 에는 kv-storage 메시지를 읽는 모듈과 API 응답 캐시를 읽는 모듈이 따로 있습니다[1][2]. 두 결과를 메시지 ID 로 맞춰 보면 어느 메시지가 한쪽에만 있는지 드러납니다. 도구 결과는 SQLite 셸로 직접 뽑은 값과 견줍니다. 아래는 `messages0` 표의 행 수와 `data` 칸 앞부분을 보는 예입니다.

```sql
SELECT count(*) FROM messages0;
SELECT substr(data, 1, 200) FROM messages0 LIMIT 5;
```

`data` 앞에는 길이 바이트가 붙어 있어서, JSON 으로 읽으려면 `{` 부터 잘라 냅니다. 도구와 직접 확인한 결과가 다를 때 가려내는 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 확인할 것 |
|---|---|
| [앱 사용 기록](../app-usage/usagestats/index.md) | 캐시 헤더 시각 앞뒤로 디스코드 앱이 화면에 올라온 기록이 있는지 |
| [알림 기록](../app-usage/notification-history.md) | 받은 메시지 시각에 디스코드 알림이 있었는지 |
| [데이터 사용량](../network/netstats.md) | 캐시 헤더 시각 무렵 앱의 네트워크 사용 기록 |
| [설치된 앱](../app-usage/packages/index.md) | 앱 설치·업데이트 시각 |
| [미디어 저장소](../media/mediastore/index.md) | 첨부 이미지를 공용 저장 공간에 저장했는지 |

여러 앱의 대화를 한 흐름으로 세우는 방법은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md) 와 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등) 가운데 디스코드 앱 데이터가 든 Android 이미지를 골라 아래 질문을 풀어 봅니다.

1. `kv-storage` 아래 `@account.` 폴더가 몇 개이고, 폴더마다 계정 ID 가 무엇인지 적습니다.
2. kv-storage 메시지와 캐시 메시지를 메시지 ID 로 맞춰, 한쪽에만 있는 메시지가 각각 몇 건인지 셉니다.
3. 같은 메시지의 `timestamp` 와 그 메시지가 든 캐시 항목의 `OkHttp-Received-Millis` 를 나란히 놓고 차이를 설명합니다.
4. `journal` 파일에서 항목마다 마지막 줄이 CLEAN 이 아닌 것이 있는지 찾습니다.
5. 프로필 응답 캐시 항목 하나를 골라, 보고서에 이 항목으로 쓸 수 있는 문장과 쓸 수 없는 문장을 나눠 적습니다.

## 참고 문헌

1. ALEAPP, `discordChats.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/discordChats.py
2. ALEAPP, `discordApiCache.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/discordApiCache.py
3. Android Developers, "Access app-specific files" — https://developer.android.com/training/data-storage/app-specific
