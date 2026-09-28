---
title: "삼성 노트"
parent: "아티팩트 · 삼성 기기 전용"
nav_order: 1190
---

# 삼성 노트 (Samsung Notes)

삼성 노트는 노트 한 건을 `sdoc.db` 의 `sdoc` 표에 한 행으로 적고, 첨부한 사진·음성 같은 파일은 앱 데이터 폴더의 `SDocData` 아래에 따로 둡니다. 행마다 만든 시각과 고친 시각, 열어 본 시각, 휴지통으로 옮긴 시각이 유닉스 밀리초로 남고, 지운 노트도 삭제 표시만 바뀐 채 행이 남아 있을 수 있습니다[1][2]. 잠근 노트는 제목은 평문으로 남고 본문 열만 암호화되며, 잠금 여부는 같은 행의 표시 열에 남습니다[2].

## 무엇을 기록하나 · 왜 생기나

삼성 노트의 패키지 이름은 `com.samsung.android.app.notes` 입니다[1]. 이 앱은 글과 사진, 그림, 음성 녹음, 파일을 노트에 담을 수 있고, 사용자가 만든 폴더(카테고리)로 노트를 나누며, 다른 기기와 동기화하거나 다른 앱으로 공유할 수 있습니다[2].

노트를 만들거나 고치면 `sdoc` 표의 행이 생기거나 바뀝니다. 노트를 지우면 행을 없애지 않고 삭제 표시 열 값만 바꾸기 때문에, 지운 노트의 제목과 본문이 데이터베이스에 그대로 남아 있을 수 있습니다[2]. 노트를 연 시각도 따로 적어서, 고치지 않고 읽기만 한 흔적까지 남습니다[1].

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 패키지 | `com.samsung.android.app.notes` [1][2] |
| 노트 데이터베이스 | `/data/data/com.samsung.android.app.notes/databases/sdoc.db`. ALEAPP 은 `sdoc.db*` 패턴으로 딸린 파일까지 함께 모읍니다[1][2] |
| 첨부 파일 | 앱 데이터 폴더 아래 `SDocData/…/media/` (ALEAPP 경로 패턴 `*/user/*/com.samsung.android.app.notes/SDocData/*/media/*`) [1] |
| 잠금 설정 흔적 | 앱 데이터 폴더의 `shared_prefs/` 안 설정 파일 [2] |

앱 데이터 폴더의 구조는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 를 봅니다.

| 자료 | 삼성 노트 판 | Android |
|---|---|---|
| Park 외 (2020) 논문[2] | 4.1.03.1 | — |
| ALEAPP `SamsungNotes` 모듈[1] | 4.4.30.91 에서 시험, 시험 자료 버전 코드 441305000·442923000·443081000 | 13·14·15 |

두 자료 사이에 열 이름과 값의 형식이 다른 곳이 있습니다. 논문은 만든 시각 열을 `createAt` 으로 적었고, ALEAPP 쿼리는 `createdAt` 을 씁니다[1][2]. 논문(4.1.03.1)에서는 `content` 가 문자열이고 `displayContent` 가 BLOB 인데[2], ALEAPP(4.4.x)은 `content` 를 바이트로 받아 UTF-8 로 풉니다[1]. 분석 대상 기기에서는 `PRAGMA table_info(sdoc);` 로 열 이름과 형식을 먼저 확인합니다.

수집 방법에 따라 얻을 수 있는 범위가 다릅니다. 4.1.03.1 은 `android:allowBackup` 이 false 라서 Android 백업으로는 앱 데이터를 받을 수 없고, 삼성 Smart Switch 백업에는 `sdoc.db` 가 들어가지만 `shared_prefs` 의 설정 파일은 들어가지 않습니다[2]. 파일 시스템 전체를 확보하면 두 곳을 모두 얻습니다([모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md)).

## 구조

저장 형식 자체는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 를 봅니다.

### sdoc 표

ALEAPP 쿼리[1]와 논문의 표 7[2]에 나오는 열입니다.

| 열 | 뜻 | 근거 |
|---|---|---|
| `UUID` | 노트마다 붙는 UUID | [2] |
| `accountName` | 삼성 계정 ID | [2] |
| `categoryUUID` | 노트가 들어 있는 폴더(카테고리)의 UUID | [2] |
| `title` | 제목(문자열) | [1][2] |
| `displayTitle` | 제목(BLOB) | [2] |
| `content` | 본문. 줄바꿈 문자를 뺀 글 | [1][2] |
| `strippedContent` | 본문. `content` 와 같은 글 | [2] |
| `displayContent` | 본문(BLOB). 줄바꿈 문자를 포함 | [2] |
| `contentUUID` | 사진·음성·오디오를 넣은 노트에서 채워지는 값 | [2] |
| `size` | 노트 크기 | [2] |
| `createdAt` | 만든 시각 (논문 표기 `createAt`) | [1][2] |
| `lastModifiedAt` | 마지막으로 고친 시각 | [1][2] |
| `firstOpendAt` | 처음 연 시각 (열 이름 철자가 `Opend`) | [1] |
| `secondOpenedAt` | 두 번째로 연 시각 | [1] |
| `lastOpenedAt` | 마지막으로 연 시각 | [1] |
| `isDeleted` | 삭제 표시 | [1][2] |
| `recycle_bin_time_moved` | 휴지통으로 옮긴 시각 | [1][2] |
| `isLock` | 잠금 표시. 잠금 1, 잠금 아님 0 | [2] |
| `ContentSecureVersion` | 잠금 표시. 잠금 1, 잠금 아님 0 | [2] |
| `filePath` | 노트 파일 경로. 첨부 파일과 짝지을 때 씀 | [1] |

ALEAPP 은 `filePath` 값의 마지막 이름이 경로에 들어 있는 `media` 폴더 파일을 그 노트의 첨부로 짝짓고, 이름이 `dat`·`spi` 로 끝나는 파일은 첨부에서 뺍니다[1].

### 폴더(카테고리) 표

노트를 나누는 폴더는 따로 표에 있습니다. 논문은 이 표 이름을 `categorytree` 와 "category tree" 두 가지로 적었고 열은 `UUID`, `displayName`(폴더 이름), `createAt`, `lastModifiedAt`, `isDeleted` 입니다[2]. 실제 표 이름은 `.tables` 로 확인합니다. 노트의 `categoryUUID` 와 이 표의 `UUID` 를 이으면 노트가 들어 있던 폴더 이름을 알 수 있습니다[2].

```sql
-- 표 이름은 .tables 결과에 맞춰 바꿉니다
SELECT s.title, c.displayName
FROM sdoc s LEFT JOIN 폴더표 c ON s.categoryUUID = c.UUID;
```

### 삭제 표시 값

`isDeleted` 값은 논문 안에서 엇갈립니다. 본문에는 노트를 지우면 `sdoc` 표의 값이 1, 폴더를 지우면 폴더 표의 값이 2 가 된다고 적혀 있고, 표 7 에는 반대로 `sdoc` 은 2, 폴더 표는 1 로 적혀 있습니다[2]. ALEAPP 은 값을 풀지 않고 그대로 보여 줍니다[1]. 그래서 값의 뜻은 분석 대상 데이터에서 `recycle_bin_time_moved` 가 채워진 행이 어떤 `isDeleted` 값을 갖는지 보고 정합니다.

### 잠긴 노트가 남기는 표시

잠금은 삼성 계정으로 로그인해야 쓸 수 있고, 비밀번호 하나가 모든 잠긴 노트에 함께 쓰입니다[2]. 노트를 잠그면 같은 행의 `isLock` 과 `ContentSecureVersion` 이 1 이 되고, `content`·`strippedContent`·`displayContent` 세 열이 암호화됩니다[2]. 제목 열은 암호화하지 않아서 잠긴 노트도 제목은 읽을 수 있습니다[2].

잠금 비밀번호를 만들면 확인용 값이 `shared_prefs` 폴더의 `UserAuthInfo.xml` 등 설정 파일에 저장됩니다[2]. 그래서 이 값이 있으면 그 기기에서 노트 잠금을 설정한 적이 있다는 표시가 됩니다. 설정 파일을 읽는 법은 [설정 XML과 SharedPreferences](../../01-foundations/data-formats/shared-preferences.md) 에 있습니다.

## 증거로서 의미

### 증명하는 것

`sdoc` 표의 행 하나는 그 제목과 본문을 담은 노트가 이 기기의 삼성 노트에 있었다는 기록입니다. `createdAt` 과 `lastModifiedAt` 으로 노트를 만든 때와 마지막으로 고친 때를, `firstOpendAt`·`secondOpenedAt`·`lastOpenedAt` 으로 노트를 연 때를 따로 볼 수 있습니다[1]. 고친 시각보다 연 시각이 늦으면 마지막으로 고친 뒤에도 노트를 다시 열었다는 뜻으로 볼 수 있습니다.

`isDeleted` 가 삭제 값이고 `recycle_bin_time_moved` 가 채워진 행은 그 노트를 지운 기록이면서, 지운 노트의 제목과 본문을 함께 담고 있습니다[2]. `isLock` 이 1 인 행은 그 노트를 잠갔다는 기록입니다[2]. `categoryUUID` 로 이은 폴더 이름과 `accountName` 의 삼성 계정 ID 는 노트를 어떻게 정리했고 어느 계정으로 썼는지 알려 줍니다[2].

### 증명하지 못하는 것

노트를 이 기기에서 직접 썼는지, 같은 삼성 계정의 다른 기기에서 쓰고 동기화로 들어왔는지는 이 행만으로 구분할 수 없습니다[2]. 동기화 기록은 [삼성 클라우드와 원드라이브](../mail-cloud/samsung-cloud-onedrive.md) 와 함께 봅니다. 기기를 쓴 사람이 누구인지도 이 기록에 나오지 않습니다([그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)).

`lastModifiedAt` 은 마지막으로 고친 때만 남아서, 그 전에 몇 번 고쳤고 무엇을 바꿨는지는 알 수 없습니다. 연 시각 열도 처음·두 번째·마지막 세 번만 담아서, 그 사이에 몇 번 열었는지는 나오지 않습니다[1]. 잠긴 노트는 본문이 암호문이라 제목과 시각만으로 판단해야 합니다.

보고서에는 "피의자가 이 메모를 작성했다" 가 아니라 "이 기기의 삼성 노트 `sdoc.db` 에 제목 ○○, 만든 시각 UTC ○○, 마지막으로 고친 시각 UTC ○○ 인 노트 행이 있고, 이 행의 `isDeleted` 값은 ○, 휴지통으로 옮긴 시각은 UTC ○○ 입니다" 처럼 씁니다.

## 시각 해석

| 열 | 값 | 무엇이 바뀔 때 바뀌나 |
|---|---|---|
| `createdAt` | 유닉스 밀리초, UTC | 노트를 만든 때 |
| `lastModifiedAt` | 유닉스 밀리초, UTC | 노트를 고친 때 |
| `firstOpendAt`, `secondOpenedAt`, `lastOpenedAt` | 유닉스 밀리초, UTC | 노트를 처음·두 번째·마지막으로 연 때 |
| `recycle_bin_time_moved` | 유닉스 밀리초, UTC | 노트를 휴지통으로 옮긴 때 |

ALEAPP 은 이 여섯 열을 모두 1000 으로 나눈 뒤 UTC 로 바꿉니다[1]. 현지 시각은 기기 시간대를 더해 따로 적습니다([시간대와 시각 설정](../system-account/time-zone.md), [시각 값](../../01-foundations/value-decoding/time-values.md)).

지우지 않은 노트나 한 번만 연 노트는 해당 시각 열이 0 으로 남을 가능성이 있습니다. 값이 0 이면 아래 SQL 의 `datetime()` 은 1970-01-01 00:00:00 을 돌려주고, ALEAPP 은 시각으로 바꾸지 않고 0 을 그대로 둡니다[1]. 1970-01-01 은 "값이 없음" 으로 읽고 사건 시각으로 적지 않습니다.

## 함정과 한계

`isDeleted` 값의 뜻이 자료마다 엇갈리므로, 1 이나 2 한 값만 보고 "삭제됨" 으로 거르지 않습니다. 위 "삭제 표시 값" 처럼 휴지통 시각과 함께 판단합니다.

ALEAPP 은 `content` 를 오류 처리 없이 UTF-8 로 풉니다[1]. 잠긴 노트의 본문은 암호문이라[2], 글자로 풀리지 않는 값을 만나면 결과가 빠지거나 모듈이 멈출 가능성이 있습니다. 도구 결과의 노트 수가 `SELECT count(*) FROM sdoc;` 와 다르면 원본 표를 직접 열어 빠진 행을 찾습니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

휴지통에서 완전히 지운 노트가 표에 남는지는 판에 따라 다를 수 있습니다. 행이 없으면 `sdoc.db` 의 빈 페이지와 `-wal` 파일에서 제목 글자를 찾아봅니다([삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)). 보안 폴더 안의 삼성 노트는 다른 사용자 번호의 앱 데이터 폴더에 있어서 따로 찾아야 합니다([보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md)).

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 형식 명세로 만든 예시이고, 실제 기기에서 나온 값이 아닙니다. 확보한 `sdoc.db` 가 암호화되지 않은 SQLite 파일인지 파일 맨 앞 16바이트로 먼저 확인합니다.

```
53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   "SQLite format 3" 과 끝의 00
```

잠긴 노트의 `content` 는 파일 전체가 아니라 열 값만 암호화되어 있어서, 파일은 평범한 SQLite 로 열립니다[2]. 잠긴 행의 `content` 를 `hex(content)` 로 보면 글자로 읽히지 않는 바이트가 나오고, 같은 행의 `title` 은 글자로 읽힙니다.

### 공개 도구로 한 번

1. 파일 시스템 전체 추출본에서 `databases/sdoc.db` 를 딸린 파일까지, `SDocData` 폴더와 `shared_prefs` 폴더를 함께 복사합니다.
2. SQLite 도구로 열고 `PRAGMA table_info(sdoc);` 로 열 이름을 확인한 뒤 아래처럼 읽습니다.

```sql
SELECT datetime(createdAt/1000,'unixepoch')      AS created_utc,
       datetime(lastModifiedAt/1000,'unixepoch') AS modified_utc,
       datetime(lastOpenedAt/1000,'unixepoch')   AS last_opened_utc,
       title, isDeleted,
       datetime(recycle_bin_time_moved/1000,'unixepoch') AS recycled_utc,
       isLock, ContentSecureVersion, categoryUUID, filePath
FROM sdoc ORDER BY createdAt;
```

3. ALEAPP 으로 같은 폴더를 처리하면 Creation Time, Last Modification Time, Title, Text Content, Deleted?, Deletion Time, First Opened Time, Second Opened Time, Last Opened Time, Media 열로 나옵니다[1].
4. 2단계에서 직접 읽은 값과 ALEAPP 결과를 몇 행 골라 맞춰 봅니다. 잠금 열은 ALEAPP 결과에 나오지 않으므로 2단계 결과로 적습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [앱 사용 기록](../app-usage/usagestats/index.md) | 만든 시각·연 시각·휴지통 시각 앞뒤로 삼성 노트가 앞에 떠 있었는지 |
| [알림 기록](../app-usage/notification-history.md) | 공유하거나 동기화할 때 생긴 알림 |
| [계정](../system-account/accounts/index.md) | `accountName` 의 삼성 계정이 기기에 등록되어 있었는지 |
| [구글 Keep](../google-services/keep.md) | 같은 기기에서 다른 메모 앱에 비슷한 내용을 적었는지 |

여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 을, 노트 본문에서 낱말을 찾는 방법은 [콘텐츠 검색](../../03-techniques/analysis/content-search.md) 을, 지운 내용을 찾는 조사 흐름은 [지운 대화와 사진 찾기](../../04-scenarios/activity/deleted-content.md) 를 봅니다.

## 실습

공개 이미지 가운데 삼성 노트를 쓴 삼성 기기 이미지(ALEAPP 시험 자료처럼 Android 13~15)를 골라 아래 질문을 풀어 봅니다.

1. `sdoc` 표의 열 목록에 `createdAt` 과 `createAt` 가운데 어느 이름이 있습니까? `content` 의 형식은 TEXT 입니까, BLOB 입니까?
2. `recycle_bin_time_moved` 가 0 이 아닌 행은 몇 개이고, 그 행들의 `isDeleted` 값은 무엇입니까?
3. `isLock` 이 1 인 행이 있습니까? 있다면 그 행의 `title` 과 `hex(content)` 의 앞부분을 적습니다.
4. 노트 하나를 골라 `lastModifiedAt` 과 `lastOpenedAt` 을 UTC 로 적고, 같은 시각의 앱 사용 기록과 맞춰 봅니다.
5. `filePath` 가 가리키는 노트의 `SDocData/…/media/` 폴더에는 어떤 파일이 있고, ALEAPP 의 Media 열과 같습니까?

## 참고 문헌

1. ALEAPP, scripts/artifacts/SamsungNotes.py (GitHub main) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/SamsungNotes.py
2. Myungseo Park, Soram Kim, Jongsung Kim, "Research on Note-Taking Apps with Security Features", Journal of Wireless Mobile Networks, Ubiquitous Computing, and Dependable Applications (JoWUA), 11(4):63-76, 2020. DOI: 10.22667/JOWUA.2020.12.31.063 — https://isyou.info/jowua/papers/jowua-v11n4-5.pdf
