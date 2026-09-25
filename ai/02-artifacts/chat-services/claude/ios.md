---
title: "Claude iOS 앱"
parent: "Claude"
grand_parent: "아티팩트 · 대화형 AI 서비스"
nav_order: 190
---

# iOS 앱 (iOS)

iPhone·iPad 의 Claude 앱은 대화 원본을 계정 서버에 두지만, 앱 컨테이너 안의 캐시 데이터베이스에 대화 목록·메시지 본문·프로젝트가 남고 캐시 JSON 에 계정 정보가 남습니다.

> 확인 범위: App Store 페이지와 공식 도움말은 2026-09-25 에 열람한 내용입니다[1][2]. 기기 안의 경로·표·칸은 iLEAPP 분석기 `iOSclaude.py`(Brandon Baye, 네 항목을 2026-07-21~07-28 에 작성, 2026-08-09 갱신)를 근거로 썼고, 이 분석기는 iOS 18.7.8 과 iOS 26.5.2 로 만든 시험 이미지에서 시험했습니다[3]. 분석기 설명에는 시험한 앱 버전이 적혀 있지 않고 지금 판과 다를 수 있으니, 검체의 앱 버전을 함께 적어 둡니다.

## 무엇을 기록하나 · 왜 생기나

App Store 의 앱 이름은 "Claude by Anthropic", 판매자는 Anthropic PBC 이고, 2026-09-25 에 본 버전은 1.260923.20, 크기는 169.2 MB 였습니다[1]. iOS 18.0 이상과 iPadOS 18.0 이상에서 돌아갑니다[1]. 앱은 claude.ai 와 같은 계정으로 로그인해 쓰고, 대화 원본은 서버에 있습니다. 지운 대화의 서버 쪽 처리는 [Claude](index.md) 허브에 정리해 두었습니다.

앱은 서버에서 받은 대화를 기기의 캐시에 둡니다. iLEAPP 분석기는 이 캐시에서 네 가지를 읽습니다[3].

| 분석기 항목 | 알려 주는 것 | 시험 이미지 결과 (iOS 18.7.8 / iOS 26.5.2) |
|---|---|---|
| 계정 정보 | 계정 생성·갱신 시각, 이름, 표시 이름, 이메일 주소, 계정 식별자 | 1행 / 1행 |
| 대화 | 대화 시작·갱신 시각, 대화 ID, 제목, 모델, 시크릿 대화 여부, 별표 여부 | 2행 / 7행 |
| 메시지 | 메시지 시각, 보낸 쪽, 본문, 첨부 파일 이름, 대화 ID | 10행 / 30행 |
| 프로젝트 | 프로젝트 생성·갱신 시각, 이름, 설명, 만든 사람 이름, 문서 수, 문서 파일 이름 | 0행 / 1행 |

iOS 앱에서는 계정 데이터를 내보낼 수 없고, 내보내기는 웹이나 데스크톱 앱에서만 됩니다[2]. 캐시에 없는 대화까지 필요하면 [계정 데이터 내보내기](export.md)를 웹이나 PC 에서 받거나 [서비스 회사에 대한 데이터 요청](../../../03-techniques/acquisition/legal-requests.md)을 검토합니다.

## 위치와 버전별 차이

앱 데이터는 `/private/var/mobile/Containers/Data/Application/<UUID>/` 아래에 있습니다. 폴더 이름이 UUID 라서 폴더 이름만으로는 어느 폴더가 Claude 앱인지 알 수 없습니다. 각 컨테이너의 `.com.apple.mobile_container_manager.metadata.plist` 에서 `MCMMetadataIdentifier` 값을 읽으면 그 컨테이너의 번들 ID 가 나옵니다[4]. Claude 앱의 번들 ID 를 적어 둔 공개 분석 자료가 없으니, 검체에서 읽은 값을 보고서에 그대로 적습니다.

| 파일 | 컨테이너 안의 경로 | 형식 | 근거 |
|---|---|---|---|
| 캐시 데이터베이스 | `Library/Application Support/ClaudeCache/cache_*.sqlite` (같은 이름의 `-wal`·`-shm` 포함) | SQLite | [3] |
| 계정 정보 캐시 | `Library/Caches/bootstrap/*.json` | JSON | [3] |

| 확인 날짜 | 앱 버전 | 크기 | 지원 OS·시험 OS | 근거 |
|---|---|---|---|---|
| 2026-09-25 | 1.260923.20 (App Store 최신판) | 169.2 MB | iOS 18.0 이상, iPadOS 18.0 이상 | [1] |
| 2026-07~08 | 분석기에 적혀 있지 않음 | - | iOS 18.7.8, iOS 26.5.2 시험 이미지 | [3] |

App Store 페이지의 버전·크기·지원 OS 는 열람한 날의 최신판 기준입니다. 검체 기기에 깔린 버전은 기기 쪽 자료에서 따로 확인해 이 표와 비교합니다. 기기 잠금과 파일별 보호 등급에 따라 무엇을 언제 읽을 수 있는지는 [데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html)에서, 로컬 백업에 앱 데이터가 들어가는지는 [로컬 백업](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/backups/local-backup/index.html)에서 다룹니다.

## 구조

### 캐시 데이터베이스

SQLite 의 일반 구조와 WAL 은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/sqlite/index.html)에 있습니다. 분석기가 읽는 표와 칸은 다음과 같습니다[3].

| 표 | 칸 | 내용 |
|---|---|---|
| `conversations` | `id`, `name`, `model` | 대화 ID, 대화 제목, 모델 이름 |
| | `createdAT`, `updatedAT` | 대화 시작·갱신 시각 |
| | `isTemporary` | 1 이면 시크릿 대화 |
| | `isStarred` | 1 이면 별표 표시 |
| `messages` | `conversationId` | `conversations.id` 와 이어지는 대화 ID |
| | `createdAT` | 메시지 시각 |
| | `sender` | 보낸 쪽. 사용자는 `human`, 응답은 `assistant` |
| | `content` | JSON 배열. `type` 이 `text` 인 항목의 `text` 가 본문 |
| | `files` | JSON 배열. `$[0].fileName` 에 첫 첨부 파일 이름 |
| `projects` | `id`, `name`, `description`, `creatorFullName` | 프로젝트 ID, 이름, 설명, 만든 사람 이름 |
| | `createdAt`, `updatedAt` | 프로젝트 생성·갱신 시각 |
| | `isStarred`, `docsCount` | 별표 여부, 문서 수 |
| `projectDocuments` | `projectID`, `fileName` | 프로젝트에 넣은 문서의 파일 이름 |

분석기 SQL 은 대화·메시지 표에서는 `createdAT` 으로, 프로젝트 표에서는 `createdAt` 으로 적습니다. SQLite 는 칸 이름의 대소문자를 가리지 않으므로 실제 철자는 검체에서 `.schema` 로 확인합니다.

분석기 설명에는 다음 관찰이 적혀 있습니다[3]. 시험 데이터에서 시크릿 대화는 대화 제목이 비어 있었습니다. 최종 응답은 `assistant` 가 보낸 메시지로 저장됩니다. 올린 이미지 파일을 두는 경로는 시험 데이터에서 비어 있었습니다. 프로젝트 행은 프로젝트에 넣은 대화를 가리킬 수 있고, 프로젝트에 문서를 넣으면 파일 이름이 저장됩니다.

### 계정 정보 캐시

`Library/Caches/bootstrap/` 안의 JSON 가운데 `account` 객체가 있는 파일에 계정 정보가 있습니다[3]. `account` 의 키는 `created_at`, `updated_at`, `full_name`, `display_name`, `email_address`, `tagged_id` 입니다. 이메일 주소와 이름은 사람을 가리키는 값이라서 보고서에는 필요한 만큼만 싣습니다.

## 증거로서 의미

**증명하는 것.** 캐시 데이터베이스에 대화와 메시지가 있으면, 그 대화를 이 기기의 앱이 한 번 이상 받아 두었다고 쓸 수 있습니다. `sender` 로 사용자 입력과 응답을 나눌 수 있고, `isTemporary` 로 시크릿 대화였는지 알 수 있습니다. 계정 정보 캐시로 이 앱에 로그인한 계정을 특정할 수 있고, 프로젝트 표로 어떤 이름의 문서를 프로젝트에 넣었는지 알 수 있습니다.

**증명하지 못하는 것.** 캐시에 있는 대화라고 해서 이 기기에서 입력했다는 뜻은 아닙니다. 같은 계정으로 웹이나 다른 기기에서 한 대화도 앱이 받아 캐시에 둘 수 있습니다. 캐시에 없다고 그 대화가 없었다는 뜻도 아닙니다. 첨부는 분석기가 첫 번째 파일 이름만 읽고, 올린 이미지 파일을 두는 경로는 시험 데이터에서 비어 있었으니[3] 파일 본체가 남는지는 검체로 확인합니다. 누가 기기를 쥐고 있었는지는 [그 대화를 한 사람이 누구인가](../../../04-scenarios/attribution/user-attribution.md)의 방법으로 좁힙니다.

## 시각 해석

| 위치 | 칸 | 형식 | 분석기의 처리 |
|---|---|---|---|
| 캐시 데이터베이스 | `createdAT`, `updatedAT`, `createdAt`, `updatedAt` | `YYYY-MM-DD HH:MM:SS` 문자열, 소수점 아래가 붙을 수 있음 | UTC 로 보고 소수점 아래를 버림 |
| 계정 정보 캐시 | `created_at`, `updated_at` | ISO 8601 (`T`·`Z` 포함) | `T`·`Z` 를 떼고 UTC 로 읽음 |

iLEAPP 의 `convert_human_ts_to_utc` 는 소수점 앞까지만 잘라 `%Y-%m-%d %H:%M:%S` 로 읽고 시간대를 UTC 로 붙입니다[5]. 데이터베이스의 시각 문자열에는 시간대 표시가 없으므로, 기기 쪽 다른 기록과 맞춰 보고 UTC 인지 확인한 뒤 보고서에 적습니다. 소수점 아래 값이 필요하면 원래 문자열을 직접 읽습니다. iOS 26 시험 데이터에서는 계정 이름을 바꾸자 `updated_at` 이 바뀌었습니다[3]. 같은 앱의 Android 판은 캐시 시각을 `T`·`Z` 가 붙은 ISO 8601 로 두므로, 두 판의 시각을 나란히 놓을 때는 형식을 맞춥니다([Android 앱](android.md)). 설치 시각 같은 기기 쪽 시각은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-ios/03-techniques/analysis/timeline/index.html)의 방법으로 읽고, 서버 자료와 합치는 방법은 [AI 사용 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

- 계정 정보 캐시의 경로 `Library/Caches/bootstrap/*.json` 은 다른 앱 컨테이너에도 있을 수 있습니다. 분석기는 `account` 객체가 있는 첫 JSON 을 고르므로[3], 그 파일이 Claude 앱 컨테이너 안에 있는지 번들 ID 로 다시 확인합니다.
- 분석기는 `cache_*.sqlite` 에 맞는 첫 파일 하나만 읽습니다[3][5]. 파일 이름의 뒷부분이 계정마다 달라지는지는 공개 자료에 없으므로, 파일이 여러 개면 하나씩 직접 엽니다.
- 분석기의 프로젝트 항목은 `projects` 와 `projectDocuments` 를 내부 조인합니다[3]. 그래서 문서가 없는 프로젝트는 결과에 나오지 않고, 문서가 여러 개면 프로젝트 하나가 여러 행으로 나옵니다. 프로젝트 목록 전체는 `projects` 표를 직접 봅니다.
- 메시지 본문은 `content` 배열에서 `type` 이 `text` 인 항목만 이어 붙입니다[3]. 다른 종류의 항목은 분석기 결과에 나오지 않으니 원래 JSON 을 함께 봅니다.
- 캐시 데이터베이스 옆의 `-wal` 파일을 빼고 복사하면 최근 기록이 빠질 수 있습니다.
- App Store 에는 비슷한 이름의 다른 앱이 있을 수 있어서, 앱 이름만으로 가리지 말고 판매자와 번들 ID 를 함께 확인합니다.
- 로컬 백업이나 논리 수집으로 앱 데이터가 나오지 않았다고 앱에 흔적이 없다고 쓰지 않습니다. 어떤 수집 방식으로 무엇을 얻었는지를 함께 적습니다.
- App Store 호환 표기는 iPhone·iPad 뿐이어서[1], Mac 의 Claude 흔적은 [macOS 앱](macos.md)에서 봅니다.

## App Store 의 개인정보 표기

App Store 페이지의 App Privacy 는 "사용자에게 연결된 데이터"를 쓰는 목적별로 다음처럼 적고 있습니다[1].

| 목적 | 표기한 데이터 |
|---|---|
| 광고·마케팅 | 대략적 위치, 연락처 정보, 식별자, 사용 데이터 |
| 분석 | 위치, 사용자 콘텐츠, 식별자, 사용 데이터, 진단 |
| 앱 기능 | 위치, 연락처 정보, 사용자 콘텐츠, 식별자, 사용 데이터, 진단 |

추적에 쓰는 데이터 항목은 표기에 없었습니다[1]. 이 표기는 서비스가 다루는 데이터의 종류만 알려 주고 기기 안 어느 파일에 무엇이 남는지는 알려 주지 않아서, 서비스 회사에 자료를 요청할 때 항목을 가늠하는 데 씁니다. 같은 기준의 Android 표기는 [Android 앱](android.md)에 있습니다.

## 직접 분석해 보기

**헥스로 한 번.** 컨테이너에서 `cache_*.sqlite` 를 찾았으면 첫 16바이트로 SQLite 파일인지 먼저 가립니다. SQLite 파일은 모두 같은 머리글로 시작하고, 아래는 그 머리글을 적은 예시입니다.

```
00000000  53 51 4c 69 74 65 20 66  6f 72 6d 61 74 20 33 00  |SQLite format 3.|
```

`messages.content` 는 JSON 배열입니다. 다음은 칸 이름만 분석기에 맞춰 만든 예시이고 값은 지어낸 것입니다.

```json
[{"type": "text", "text": "회의록을 세 줄로 요약해 줘"}]
```

**공개 도구로 한 번.** iLEAPP 을 추출 폴더에 돌리면 "Claude" 분류 아래에 계정 정보·대화·메시지·프로젝트 네 항목이 나옵니다[3]. 분석기 없이 직접 볼 때는 다음 순서를 따릅니다.

1. 컨테이너마다 `.com.apple.mobile_container_manager.metadata.plist` 의 `MCMMetadataIdentifier` 를 읽어 Claude 앱 컨테이너를 찾고 번들 ID 를 적습니다[4]. plist 를 읽는 법은 [속성 목록 파일](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/plist.html)에 있습니다.
2. `Library/Application Support/ClaudeCache/` 의 `cache_*.sqlite` 를 `-wal`·`-shm` 과 함께 복사한 뒤 `.schema` 로 표와 칸 이름을 적습니다.
3. 다음 질의로 대화별 메시지를 시각 순서로 뽑습니다. 본문을 이어 붙이는 방식은 분석기 SQL 과 같습니다[3].

```sql
SELECT m.createdAT, m.sender, c.name, c.isTemporary,
       (SELECT group_concat(json_extract(je.value, '$.text'), ' ')
          FROM json_each(m.content) je
         WHERE json_extract(je.value, '$.type') = 'text') AS body,
       json_extract(m.files, '$[0].fileName') AS file_name
FROM messages m
LEFT JOIN conversations c ON c.id = m.conversationId
ORDER BY m.conversationId, m.createdAT;
```

4. `Library/Caches/bootstrap/` 의 JSON 에서 `account` 객체를 찾아 계정과 생성·갱신 시각을 적습니다.
5. 찾은 내용은 검체의 앱 버전·iOS 버전과 함께 기록하고, 이 페이지의 버전 표와 비교합니다.

로그인 정보를 키체인에 두는지는 공개된 분석 자료가 없어 검체로 확인해야 하고, 키체인 구조는 [키체인](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/keychain.html)에 있습니다.

## 교차 검증

| 함께 볼 것 | 알려 주는 것 |
|---|---|
| [계정 데이터 내보내기](export.md) | 캐시에 없는 대화의 본문과 시각, 캐시 내용과의 대조 |
| [웹 브라우저](web.md), [사파리](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/safari/index.html), [크롬 (Chrome for iOS)](https://urock-ailab.github.io/forensics-handbook-ios/02-artifacts/browsers/chrome.html) | 앱 대신 휴대폰 브라우저로 claude.ai 를 쓴 흔적 |
| [Android 앱](android.md) | 같은 계정을 다른 휴대폰에서 쓴 경우 |
| [AI 서비스 도메인과 네트워크 기록](../../network-enterprise/network-traces.md) | 회사 네트워크에서 접속한 기록 |

## 실습

iLEAPP 분석기를 시험한 이미지는 `hc_ios18_7`(iOS 18.7.8)과 `hc_ios26`(iOS 26.5.2)입니다[3]. 직접 만든 시험용 기기의 추출본으로 다음을 풀어 봅니다.

1. Claude 앱 컨테이너의 번들 ID 는 무엇이고, `ClaudeCache` 폴더에 `cache_*.sqlite` 파일이 몇 개 있는가?
2. 시크릿 대화를 하나 만든 뒤 `conversations` 에 `isTemporary` 가 1 인 행이 생기는가, 그 행의 `name` 은 비어 있는가?
3. 웹에서 만든 대화가 앱을 연 뒤 캐시에 들어오는가, 들어온다면 `createdAT` 은 웹에서 대화를 시작한 시각과 같은가?
4. 계정 이름을 바꾸면 bootstrap JSON 의 `updated_at` 이 바뀌는가?

## 참고 문헌

1. Claude by Anthropic — App Store — https://apps.apple.com/us/app/claude-by-anthropic/id6473753684
2. How can I export my Claude data? (Claude Help Center) — https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-data
3. iLEAPP, Claude 분석기 (Brandon Baye) — https://github.com/abrignoni/iLEAPP , `scripts/artifacts/iOSclaude.py`
4. iLEAPP, 앱 사용자 기본값 분석기 (@jfhyla) — https://github.com/abrignoni/iLEAPP , `scripts/artifacts/userDefaults.py`
5. iLEAPP, 공통 함수 `convert_human_ts_to_utc`·`get_file_path` — https://github.com/abrignoni/iLEAPP , `scripts/ilapfuncs.py`
