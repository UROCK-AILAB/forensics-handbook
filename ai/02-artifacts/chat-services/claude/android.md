---
title: "Claude Android 앱"
parent: "Claude"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 180
---

# Android 앱 (Android)

Android 의 Claude 앱(패키지 ID `com.anthropic.claude`)은 대화 원본을 계정 서버에 두지만, 기기의 앱 데이터 폴더에 대화 목록·메시지·프로젝트를 캐시 데이터베이스로 남기고 계정 정보를 JSON 파일로 남깁니다.

이 쪽 내용이 어느 앱 판 기준인지는 알려져 있지 않고 앱이 자주 바뀌므로, 검체의 앱 판과 맞춰 봅니다[4][5].

## 무엇을 기록하나 · 왜 생기나

Google Play 에서 앱 이름은 "Claude by Anthropic", 개발자는 Anthropic PBC 이고, Play 주소에 붙은 패키지 ID 는 `com.anthropic.claude` 입니다[1][2]. 앱은 claude.ai 와 같은 계정으로 로그인해 쓰고, 대화 원본은 서버에 있습니다. 지운 대화의 서버 쪽 처리는 [Claude](index.md) 허브에 정리해 두었습니다.

앱은 서버에서 받은 대화와 메시지를 기기 안 SQLite 캐시(`acc_*_claude_cache.db`)에 JSON 으로 담아 둡니다[4]. 이 캐시에는 대화 이름·모델·시크릿(Incognito) 여부·즐겨찾기 여부, 메시지 본문·보낸 쪽·시각, 프로젝트 정보가 있고, 계정 이름과 이메일은 따로 `cache.json` 에 있습니다[4]. 메시지는 최근에 연 대화의 것만 캐시에 남고, 대화 제목·모델·시각 같은 목록 정보는 더 넓게 남습니다[5]. 앱은 주로 claude.ai 를 띄운 웹뷰(WebView)이고[5], 추출본에도 웹뷰 저장소 폴더가 있습니다[7]. 웹뷰 저장 구조의 공통 원리는 [Electron·웹뷰 앱의 저장 구조](../../../01-foundations/storage-model/electron-webview.md)에 있습니다.

Android 앱에서는 계정 데이터를 내보낼 수 없고, 내보내기는 웹이나 데스크톱 앱에서만 됩니다[3]. 캐시에 없는 대화까지 필요하면 [계정 데이터 내보내기](export.md)를 웹이나 PC 에서 받거나 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)을 검토합니다.

## 위치와 버전별 차이

아래 경로는 앱 데이터 폴더 `/data/data/com.anthropic.claude/` 기준입니다.

| 흔적 | 경로 | 알 수 있는 것 | 근거 |
|---|---|---|---|
| 대화 캐시 | `databases/acc_{계정UUID}_org_{조직UUID}_claude_cache.db` 와 `-wal`·`-shm` | 대화·메시지·프로젝트 | 경로 패턴 [4], 파일 이름 형식 [5] |
| 계정 정보 | `cache/app_start/acc_*/org_*/cache.json` | 계정 생성·수정 시각, 이름, 표시 이름, 이메일 | [4] |
| 설정 파일 | 앱 데이터 폴더 안 XML 파일 하나(이름·위치는 적혀 있지 않음) | 이메일 | [4] |
| 웹뷰 저장소 | `app_webview/Default/Local Storage/leveldb`, `app_webview/Default/Cookies` | 웹뷰의 사이트 저장소와 쿠키 | [7] |
| 웹뷰 캐시 | `cache/WebView/Default/HTTP Cache/Cache_Data` | 웹뷰가 받은 자원 | [7] |
| 대화 원본 | 계정 서버 | 전체 대화 | [Claude](index.md) 허브 |

캐시 파일 이름에 계정 UUID 와 조직 UUID 가 들어가서, 한 기기에서 계정을 여럿 썼다면 캐시 파일도 여럿 생깁니다[5]. ALEAPP 경로 패턴은 `*/com.anthropic.claude/databases/acc_*_claude_cache.db*` 로 끝이 `db*` 라서 `-wal`·`-shm` 까지 함께 잡습니다[4].

추출본마다 파일 구성이 다릅니다. Claude 앱 폴더는 있는데 대화 캐시 없이 Firebase Analytics 데이터베이스만 나오는 추출본도 있습니다[6]. 공개된 이런 추출본 두 벌은 모두 `databases/` 에 `google_app_measurement_local.db` 와 `com.google.android.datatransport.events` 만 있고, 계정 정보 파일은 `acc_` 단계 없이 `cache/app_start/org_{조직UUID}/cache.json` 에 있습니다[7]. 이 경로는 ALEAPP 경로 패턴에 걸리지 않으므로, 분석기가 계정 정보를 내놓지 않으면 `cache/app_start/` 아래를 직접 봅니다. 같은 추출본의 `shared_prefs/` 에는 `account_prefs{계정UUID}.xml`, `organization_prefs__{계정UUID}_{조직UUID}.xml`, `user_cookies_{계정UUID}.xml`, `device_id_prefs.xml`, `app_prefs_latest_seen_completed_messages.xml` 같은 이름의 파일이 있습니다[7]. 이 파일들의 내용을 설명한 공개 자료는 없어서 검체에서 열어 확인합니다.

앱 데이터 폴더의 하위 폴더 구성은 [앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html)에서, 기기 암호화 때문에 무엇을 언제 읽을 수 있는지는 [저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html)에서 다룹니다.

### 스토어의 데이터 보안 표기

Play 의 데이터 보안 페이지는 앱이 모으는 데이터와 다른 곳과 나누는 데이터를 다음처럼 적고 있습니다[2]. 괄호 안 "선택"은 사용자가 고를 수 있다고 표기한 항목입니다.

| 구분 | 표기한 데이터 |
|---|---|
| 수집 | 이름·이메일·사용자 ID·전화번호, 사진(선택), 기기 ID, 파일·문서(선택), 앱 상호작용·사용자 생성 콘텐츠, 비정상 종료 로그·진단·성능, 대략적 위치·정확한 위치(정확한 위치는 선택) |
| 공유 | 이메일·사용자 ID·전화번호, 앱 상호작용, 비정상 종료 로그·진단·성능, 대략적 위치 |

같은 페이지는 전송 중에 데이터를 암호화하고 사용자가 데이터 삭제를 요청할 수 있다고 적었습니다[2]. 이 표기는 서비스가 다루는 데이터의 종류를 알려 줄 뿐 기기 안 어느 파일에 무엇이 남는지는 알려 주지 않아서, 서비스 회사에 자료를 요청할 때 어떤 항목이 있을 수 있는지 가늠하는 데 씁니다.

## 구조

### 대화 캐시의 표

세 표 모두 한 행에 JSON 한 덩어리를 담고, 필요한 값은 `json_extract` 로 꺼냅니다. 아래 표의 [4] 는 ALEAPP 분석기가 실제로 읽는 칸과 키이고, [5] 는 LEAF 문서에만 있는 내용입니다.

| 표 | 칸 | JSON 키 | 근거 |
|---|---|---|---|
| `cachedConversations` | `uuid`(대화 ID), `conversation_json` | `created_at`, `updated_at`, `name`(대화 이름), `model`, `is_temporary`(시크릿 대화), `is_starred`(즐겨찾기) | [4] |
| | `updated_at`(INTEGER, 밀리초) | `uuid`, `summary`, `settings.enabled_web_search` | [5] |
| `cachedMessages` | `conversation_uuid`, `message_json` | `created_at`, `sender`, `content[]`(`type`, `text`), `files[0].file_name` | [4] |
| | `uuid`(메시지 ID) | `uuid`, `parent_message_uuid`, `index`, `updated_at`, `text`, `content[].start_timestamp`, `content[].stop_timestamp`, `content[].citations` | [5] |
| `cachedProjects` | `project_json` | `created_at`, `updated_at`, `name`, `description`, `creator.full_name`, `is_starred`, `docs_count`, `files_count` | [4] |
| `chatIdListEntries` | 공개 자료 없음 | 공개 자료 없음 | [5] |

`sender` 값은 사용자면 `human`, Claude 면 `assistant` 입니다[4][5]. 메시지 본문은 `content` 배열에서 `type` 이 `text` 인 항목의 `text` 를 이어 붙이면 됩니다[4]. `content` 에는 웹 검색 같은 도구 호출이 `type` 이 `tool_use` 인 항목으로 들어가고, 이 항목에 `name`·`input` 이 있습니다[5]. 대화 안 순서는 `index` 나 `created_at` 으로 정합니다[5]. `is_temporary`·`is_starred` 는 0 이나 1 로 들어 있고, ALEAPP 은 그 밖의 값을 "Unknown" 으로 표시합니다[4]. 메시지의 `conversation_uuid` 는 `cachedConversations` 의 `uuid` 와 이어져, 메시지마다 대화 이름을 붙일 수 있습니다[4].

아래는 `message_json` 한 행의 모양을 보여 주려고 만든 예시입니다. UUID·시각·본문은 모두 지어낸 값입니다.

```json
{
  "uuid": "0a1b2c3d-0000-4000-8000-000000000001",
  "parent_message_uuid": "00000000-0000-4000-8000-000000000000",
  "index": 0,
  "created_at": "2026-03-02T01:15:20.100Z",
  "updated_at": "2026-03-02T01:15:20.100Z",
  "sender": "human",
  "text": "",
  "content": [
    {"type": "text", "text": "회의 일정표를 표로 정리해 줘",
     "start_timestamp": "2026-03-02T01:15:20.050Z",
     "stop_timestamp": "2026-03-02T01:15:20.050Z", "citations": []}
  ]
}
```

### 계정 정보 파일

`cache.json` 의 `response.account` 아래에 `created_at`, `updated_at`, `full_name`, `display_name`, `email_address` 가 있습니다[4]. ALEAPP 은 `display_name` 을 적힌 그대로 보여 줍니다[4].

## 증거로서 의미

**증명하는 것.** 캐시에 대화가 있으면 이 기기의 앱에 그 계정으로 로그인한 적이 있고, 그 대화의 이름·모델·시각이 캐시에 들어온 적이 있다고 쓸 수 있습니다. 메시지 행이 있으면 사용자가 입력한 글(`human`)과 Claude 의 답(`assistant`)을 시각과 함께 보고서에 옮길 수 있습니다. `is_temporary` 가 1 이면 시크릿 대화로 표시된 대화입니다. `cache.json` 과 캐시 파일 이름은 앱에 로그인한 계정의 이메일·이름·계정 UUID 를 알려 줍니다.

**증명하지 못하는 것.** 캐시는 서버 기록의 일부만 담아서, 캐시에 없는 대화나 메시지를 없었다고 쓸 수 없습니다[5]. 대화 원본은 계정 서버에 있고 같은 계정을 웹·PC 에서도 쓸 수 있어서, 캐시에 있는 대화를 이 기기에서 입력했다고 단정할 수 없습니다. 휴대폰 브라우저로 claude.ai 를 쓴 흔적은 [웹 브라우저](web.md)와 [크롬 (Chrome for Android)](https://urock-ailab.github.io/forensics-handbook-android/02-artifacts/browsers/chrome/index.html)에서 봅니다. 누가 기기를 쥐고 입력했는지는 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 좁힙니다. 첨부 파일은 `files[0].file_name` 에 이름만 남을 수 있고, ALEAPP 시험 데이터에서는 메시지에 적힌 이미지 폴더가 비어 있었습니다[4]. 그래서 파일 이름만으로 그 파일이 기기에 있었다고 쓰지 않습니다.

보고서에는 "이 기기의 Claude 앱 캐시에 이 계정의 대화 N 건과 메시지 M 행이 있고, 가장 늦은 메시지의 `created_at` 은 이 시각이다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

| 값 | 형식 | 근거 |
|---|---|---|
| 대화·메시지·프로젝트·계정 JSON 의 `created_at`, `updated_at` | ISO 8601 문자열, 끝의 `Z` 는 UTC | [4] |
| 메시지 `content[]` 의 `start_timestamp`, `stop_timestamp` | ISO 8601 문자열(UTC) | [5] |
| `cachedConversations` 의 `updated_at` 칸 | 유닉스 시각 밀리초(정수) | [5] |

ALEAPP 은 ISO 8601 문자열에서 `T` 와 `Z` 를 떼고 UTC 로 읽습니다[4]. JSON 안 시각은 대화·메시지 객체가 만들어지고 바뀐 시각이라, 기기가 그 행을 캐시에 쓴 시각과 같다고 보지 않습니다. 앱을 언제 설치·업데이트했는지와 캐시 파일이 언제 바뀌었는지는 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-android/03-techniques/analysis/timeline/index.html)의 방법으로 파일 시스템 시각에서 읽습니다. 기기 시각과 계정 내보내기 자료의 시각을 맞추는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

- **WAL 을 함께 수집합니다.** 캐시 데이터베이스와 `-wal`·`-shm` 을 같이 복사하지 않으면 마지막 변경이 빠질 수 있습니다. WAL 을 읽는 방법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html)에 있습니다.
- **캐시가 없을 수 있습니다.** 추출본에 따라 대화 캐시 없이 분석용 데이터베이스만 나오기도 합니다[6]. `/data/data` 아래를 읽지 못하는 수집 방법도 많아서, 캐시가 없다고 앱을 쓰지 않았다고 쓰지 않습니다.
- **경로가 분석기 패턴과 다를 수 있습니다.** 계정 정보 파일이 `acc_` 단계 없이 놓인 추출본이 있습니다[7]. 분석기 결과가 비어 있으면 폴더 목록을 직접 봅니다.
- **LEAF 문서는 보조 자료입니다.** README 는 Claude 대화 데이터베이스를 아직 추출하지 않았다고 적었고, 스키마 문서는 대화 캐시의 표를 설명해서 두 문서가 서로 어긋납니다[5][6]. LEAF 에만 있는 칸·키는 검체에서 한 번 더 확인하고 씁니다.
- **분석기가 시험한 범위가 좁습니다.** ALEAPP 분석기에 적힌 시험 이미지는 두 개이고, 한쪽은 대화 14 행·메시지 78 행, 다른 쪽은 대화 1 행·메시지 8 행·프로젝트 0 행이었습니다[4]. 앱 버전은 적혀 있지 않아서 지금 판과 다를 수 있습니다.
- **인증 정보를 가립니다.** 웹뷰의 `Cookies` 와 `shared_prefs/` 의 `user_cookies_` 로 시작하는 파일[7]은 이름으로 보아 쿠키를 담는 파일이라서, 검체에서 열어 인증 값이 있으면 보고서에 옮길 때 가립니다. 인증 정보가 남는 곳의 일반 원리는 [API 키와 토큰이 남는 곳](../../../01-foundations/storage-model/api-keys-tokens.md)에 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** `databases/` 에서 이름이 `_claude_cache.db` 로 끝나는 파일을 열어 첫 16 바이트가 `53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00`("SQLite format 3" 과 널 바이트)인지 봅니다. 이 값은 SQLite 파일 머리의 명세 값입니다. 같은 폴더에 `-wal` 파일이 있으면 첫 4 바이트가 `37 7F 06 82` 나 `37 7F 06 83` 인지 봅니다. 파일 안에서 `"sender":"human"` 같은 문자열을 찾으면 JSON 이 평문으로 들어 있는지 알 수 있습니다.

**SQL 로 한 번.** 사본을 DB Browser for SQLite 같은 도구로 열고, ALEAPP 이 쓰는 쿼리[4]와 같은 방식으로 메시지를 꺼냅니다.

```sql
SELECT
  json_extract(m.message_json, '$.created_at') AS created_at,
  json_extract(m.message_json, '$.sender')     AS sender,
  (SELECT group_concat(json_extract(je.value, '$.text'), ' ')
     FROM json_each(m.message_json, '$.content') je
    WHERE json_extract(je.value, '$.type') = 'text') AS message,
  json_extract(c.conversation_json, '$.name')  AS conversation_name,
  c.uuid                                       AS conversation_id
FROM cachedMessages m
LEFT JOIN cachedConversations c ON c.uuid = m.conversation_uuid
ORDER BY created_at;
```

**공개 도구로 한 번.** ALEAPP 에 앱 데이터 폴더나 기기 이미지를 넣으면 "Claude" 분류 아래 계정 정보, 대화, 메시지, 프로젝트 네 결과가 나옵니다[4]. 결과를 위 쿼리 결과와 대조하고, 행 수가 다르면 WAL 반영 여부부터 봅니다. 웹뷰의 `Local Storage/leveldb` 는 [LevelDB와 IndexedDB](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/leveldb-indexeddb.html), `shared_prefs/` 의 XML 은 [설정 XML과 SharedPreferences](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/shared-preferences.html)의 방법으로 읽습니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [계정 데이터 내보내기](export.md) | 캐시에 없는 대화까지 포함한 대화 본문과 시각 |
| [웹 브라우저](web.md) | 휴대폰 브라우저로 쓴 흔적 |
| [대화 내용 되살리기](../../../03-techniques/analysis/content-recovery.md) | 캐시·WAL 에서 지워진 행을 되살리는 방법 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 회사 네트워크에서 접속한 기록 |
| [iOS 앱](ios.md) | 같은 계정을 iPhone 에서 쓴 경우 |

## 실습

시험용 계정과 Android 기기를 준비해 풀어 봅니다.

1. 대화 셋을 만들고 그중 하나만 다시 연 뒤 추출하면, `cachedConversations` 와 `cachedMessages` 에 각각 몇 행이 남는가?
2. 시크릿 대화를 하나 만들면 `is_temporary` 가 1 인 행이 생기는가?
3. 웹에서만 만든 대화가 앱의 `cachedConversations` 에 들어오는가, 들어온다면 메시지 행도 있는가?
4. 이미지를 첨부한 메시지에서 `files[0].file_name` 에는 무엇이 남고, 앱 데이터 폴더 어디에 이미지가 남는가?
5. `-wal` 파일을 빼고 연 결과와 함께 연 결과는 행 수가 어떻게 다른가?

## 참고 문헌

1. Claude by Anthropic — Google Play 상세 페이지 주소 — https://play.google.com/store/apps/details?id=com.anthropic.claude
2. Claude by Anthropic — Google Play 데이터 보안(2026-09-25 열람) — https://play.google.com/store/apps/datasafety?id=com.anthropic.claude
3. How can I export my Claude data? (Claude Help Center) — https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-data
4. ALEAPP, Brandon Baye, `scripts/artifacts/claude.py`(2026-07-21~24 작성, 2026-08-09 갱신) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/claude.py
5. LEAF - Law Enforcement AI Forensics, `docs/parser-schemas.md`(Android 15, 2026-04-20 추출) — https://github.com/MarcosAOSperoni/LEAF-Digital-Forensics/blob/main/docs/parser-schemas.md
6. LEAF - Law Enforcement AI Forensics, `leaf/README.md` — https://github.com/MarcosAOSperoni/LEAF-Digital-Forensics/blob/main/leaf/README.md
7. LEAF - Law Enforcement AI Forensics, 저장소 파일 목록(`Autopsy Case/`, `manual-forensics/cases/` 아래 추출본) — https://github.com/MarcosAOSperoni/LEAF-Digital-Forensics
