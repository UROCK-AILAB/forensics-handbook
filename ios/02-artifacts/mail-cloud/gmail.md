---
title: "지메일"
parent: "아티팩트 · 메일·클라우드·애플 앱"
nav_order: 980
---

# 지메일 (Gmail)

## 한 줄 요약

아이폰의 지메일 앱은 앱 데이터 컨테이너 안 `Library/Application Support/data/` 아래 계정별 폴더에 오프라인 검색 DB 와 라벨 DB 를 두고, 오프라인 검색 DB 에는 보낸 사람·받는 사람·제목·본문까지 한 행에 들어 있습니다.

## 무엇을 기록하나 · 왜 생기나

지메일 앱은 메일 내용을 기기 안 SQLite DB 에 담아 두고, 공개 도구 iLEAPP 의 지메일 파서(작성자 @KevinPagano3, 2024-10-15 작성, 2026-08-24 갱신, 버전 0.0.2)는 이 DB 를 두 가지로 나눠 읽습니다 [1]. 하나는 파일 이름이 `searchsqlitedb` 로 시작하는 오프라인 검색 DB 이고, 다른 하나는 `sqlitedb` 로 시작하는 라벨 DB 입니다 [1]. iLEAPP 는 두 DB 에서 각각 `gmailOfflineSearch`, `gmailLabelDetails` 라는 보고서를 만듭니다 [1].

지메일 계정은 전용 앱 말고 iOS 기본 메일 앱에 추가해서 쓸 수도 있고, 이 경우에는 흔적이 [메일 앱](apple-mail.md) 쪽에 남습니다. 사건에서 "지메일을 썼다" 는 말이 나오면 두 앱 가운데 어느 쪽으로 썼는지부터 가립니다.

## 위치와 버전별 차이

iLEAPP 가 찾는 경로는 아래와 같습니다 [1].

```
오프라인 검색 DB
*/mobile/Containers/Data/Application/*/Library/Application Support/data/*/searchsqlitedb*
라벨 DB
*/mobile/Containers/Data/Application/*/Library/Application Support/data/*/sqlitedb*
```

즉 지메일 데이터는 앱 데이터 컨테이너(`Containers/Data/Application/` 아래 GUID 폴더) 안의 `Library/Application Support/data/` 밑에 폴더 하나를 더 두고 그 안에 있습니다 [1]. `data` 아래 폴더 이름이 계정과 어떻게 대응하는지는 확인하지 못해서, 계정이 여럿이면 폴더마다 DB 를 따로 열어 계정 주소를 맞춰 봅니다.

| 항목 | 내용 | 근거 |
|---|---|---|
| 앱 컨테이너 안 DB 경로 | 위 두 경로 | [1] |
| 파서 버전·갱신일 | 0.0.2, 2026-08-24 | [1] |
| 파서가 시험한 iOS 버전 | 12.4, 15.0.2, 16.1.1, 16.5, 17.3, 17.5.1, 18.0, 18.3.2 (파서 설명에 적힌 목록) | [1] |
| 앱 번들 ID·백업 도메인 이름 | 확인하지 못함 | 관찰 메모가 다른 회사 앱 이름을 가림 |
| 로컬 백업에 들어가는 파일 | 확인하지 못함 | — |

지메일 앱의 번들 ID 는 `com.google.Gmail` 로 알려져 있지만 이번 자료로 확인하지 못했고, 관찰한 백업에서도 다른 회사 앱 도메인 이름은 가려져 있었습니다(확인 범위: iOS 27.0). 검체에서는 설치 앱 목록에서 번들 ID 를 먼저 확인하고, 그 번들 ID 가 들어간 도메인을 찾습니다. 방법은 [설치된 앱](../app-usage/installed-apps.md) 과 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에 있습니다.

## 구조

### 오프라인 검색 DB (searchsqlitedb)

`offline_search_content` 표의 칸 이름은 `c0` 부터 `c8` 까지 번호만 붙어 있고, iLEAPP 는 칸마다 아래 뜻을 붙여 읽습니다 [1].

| 칸 | 뜻 |
|---|---|
| `c0` | 시각 |
| `c1` | 스레드 ID |
| `c2` | 메시지 ID |
| `c3` | 보낸 사람 |
| `c4` | 받는 사람 |
| `c5` | 참조 |
| `c6` | 숨은 참조 |
| `c7` | 제목 |
| `c8` | 본문 |

칸 이름에 뜻이 드러나지 않아서, 다른 버전의 앱에서 칸 순서가 바뀌면 도구가 엉뚱한 칸을 제목이나 본문으로 보여 줄 수 있습니다. 검체에서는 몇 행을 직접 읽어 `c3`~`c6` 에 메일 주소가, `c7` 에 제목다운 짧은 글이 들어 있는지 먼저 확인합니다.

### 라벨 DB (sqlitedb)

`label_counts` 표에는 `label_server_perm_id`, `unread_count`, `total_count`, `unseen_count` 칸이 있습니다 [1]. 라벨마다 전체·읽지 않음·보지 않음 개수가 남아서, 수집 시점의 메일함 규모를 가늠하는 데 씁니다. `label_server_perm_id` 값이 어떤 라벨 이름과 대응하는지는 이번 자료로 확인하지 못했습니다.

### 기본 메일 앱 쪽 흔적

관찰한 백업의 `com.apple.accountsd.plist` 에 있는 `AuthenticationPluginCache` 에는 `com.apple.account.Google` 이 들어 있었지만, 인증 플러그인 목록이라서 구글 계정을 실제로 추가했다는 뜻인지는 확인하지 못했습니다(확인 범위: iOS 27.0). 같은 백업의 `group.com.apple.mail.plist` 의 `UserNotificationMailboxCutoffs` 안에는 아래처럼 이름에 `Gmail` 이 들어간 IMAP 메일함 URL 이 있었습니다(확인 범위: iOS 27.0).

```
AppDomainGroup-group.com.apple.mail :: Library/Preferences/group.com.apple.mail.plist
UserNotificationMailboxCutoffs: {imap://<UUID>/%#BGmail%#D/%#CSent, imap://<UUID>/INBOX}
(# 은 관찰 메모에서 가린 숫자)
```

이 항목은 기본 메일 앱에 지메일 계정을 IMAP 으로 연결했을 때 남는 흔적으로 보이지만, 그 해석은 이름에서 나온 추정이고 확인하지 못했습니다. 계정을 확정하려면 계정 DB 의 `ZACCOUNT` 행을 함께 봅니다. 읽는 법은 [메일 앱](apple-mail.md) 에 있습니다.

## 증거로서 의미

### 증명하는 것

오프라인 검색 DB 에 행이 있으면, 그 메일이 수집 시점에 이 기기의 지메일 앱 저장소에 내려받혀 있었다는 기록이 되고, 보낸 사람·받는 사람·제목·본문이 한 행에 함께 남습니다 [1]. 스레드 ID(`c1`)가 같은 행을 묶으면 한 대화에 속한 메일을 모을 수 있습니다. 라벨 DB 의 개수는 수집 시점에 각 라벨에 메일이 몇 통 있었는지를 보여 줍니다.

### 증명하지 못하는 것

오프라인 검색 DB 는 앱이 검색용으로 담아 둔 것이라서, 계정의 메일 전체가 들어 있다고 볼 근거는 없습니다. 이 DB 에 없는 메일이 서버에도 없었다고 쓰지 않고, 서버에서 지운 메일이 이 표에 남는지도 확인하지 못했습니다. 보낸 사람 칸이 사용자 주소라고 해서 이 기기에서 보냈다고 말할 수 없고, 같은 계정을 웹이나 다른 기기에서 썼다면 그쪽에서 보낸 메일일 수 있습니다. 행이 있다는 사실만으로 사용자가 그 메일을 열어 읽었다고 말할 수도 없습니다.

보고서에는 "이 메일을 받았다" 대신 "수집 시점에 지메일 앱의 오프라인 검색 DB 에 이 스레드 ID·제목·보낸 사람으로 된 행이 있다" 처럼 씁니다.

## 시각 해석

iLEAPP 는 `c0` 를 `datetime(c0/1000,'unixepoch')` 로, 즉 밀리초 단위 Unix 시각(1970-01-01 UTC 기준)으로 보고 바꿉니다 [1]. 앱 버전이 다른 검체에서는 보고서에 쓰기 전에 값의 자릿수(밀리초 Unix 시각이면 2020년대 값이 13자리)를 보고 확인합니다. 이 값이 서버가 메일을 받은 시각인지, 보낸 사람이 보낸 시각인지는 확인하지 못했습니다. 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

## 함정과 한계

이 페이지의 구조는 공개 파서 하나 [1] 에 기대고 있고, 파서 설명에는 iOS 12.4 부터 18.3.2 까지 시험한 버전이 적혀 있지만 지메일 앱 버전은 적혀 있지 않습니다 [1]. 앱 업데이트로 파일 이름이나 칸 순서가 바뀌면 도구가 빈 결과를 내거나 칸을 잘못 붙일 수 있어서, 도구 결과를 그대로 쓰기 전에 [도구 검증](../../03-techniques/reporting/tool-validation.md) 방식으로 원본 DB 와 대조합니다.

로컬 백업에 지메일 앱 데이터가 들어가는지, 들어간다면 어느 파일이 포함되는지는 확인하지 못했습니다. iCloud 백업은 기기에 내려받은 앱의 앱 데이터를 포함한다고 Apple 은 설명하지만 [2], 지메일 앱이 백업에서 빼는 파일이 있는지는 확인하지 못했습니다. 백업에서 이 DB 가 보이지 않으면 파일 시스템 전체 수집이 가능한지 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 검토하고, 계정 쪽 자료는 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 절차로 확보합니다.

경로 패턴 끝이 `*` 로 끝나서 파서는 같은 이름으로 시작하는 파일을 모두 잡는데 [1], 검체에 `-wal` 파일이 함께 있으면 본 DB 와 같이 복사해야 최근 변경이 빠지지 않습니다. 자세한 내용은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

`searchsqlitedb` 라는 이름에 확장자가 없어서, 헥스 편집기로 열어 첫 16바이트가 SQLite 머리말인지 먼저 확인합니다. 아래는 SQLite 파일 형식으로 만든 예시이고 검체에서 나온 값이 아닙니다.

```
00000000  53 51 4C 69 74 65 20 66  6F 72 6D 61 74 20 33 00   SQLite format 3.
```

같은 폴더에 이름이 비슷한 파일이 여럿 있으면 이 머리말이 있는 파일이 본 DB 이고, 나머지는 `-wal`·`-shm` 같은 곁가지 파일인지 확인합니다. 머리말 뒤의 페이지 크기·페이지 구조는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 따라갑니다.

### 공개 도구로 한 번

1. 앱 컨테이너에서 `Library/Application Support/data/` 아래 폴더를 모두 복사합니다.
2. 오프라인 검색 DB 를 sqlite3 로 열어 시각을 바꾸며 읽습니다.

   ```sql
   SELECT datetime(c0/1000, 'unixepoch') AS time_utc,
          c1 AS thread_id, c3 AS sender, c4 AS recipients, c7 AS subject
   FROM offline_search_content
   ORDER BY c0;
   ```

3. 라벨 DB 에서 라벨별 개수를 봅니다.

   ```sql
   SELECT label_server_perm_id, total_count, unread_count, unseen_count
   FROM label_counts;
   ```

4. 같은 폴더를 iLEAPP 에 넣어 `gmailOfflineSearch`·`gmailLabelDetails` 보고서를 만들고, 2·3번 결과와 행 수와 시각이 같은지 견줍니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [설치된 앱](../app-usage/installed-apps.md) | 지메일 앱이 설치되어 있었는지 |
| [메일 앱](apple-mail.md) | 같은 계정을 기본 메일 앱으로도 썼는지 |
| [알림 기록](../app-usage/notifications.md) | 새 메일 알림이 온 시각과 미리보기 |
| [KnowledgeC](../app-usage/knowledgec/index.md)·[바이옴](../app-usage/biome/index.md)·[화면 사용 시간](../app-usage/screen-time.md) | 지메일 앱을 앞에 띄워 쓴 시각 |
| [앱별 데이터 사용량](../network/data-usage.md) | 앱이 주고받은 데이터 양 |
| [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) | 서버에 남은 메일을 확보하는 절차 |

계정이 남의 손에 넘어갔는지를 묻는 사건이라면 [계정 탈취 흔적](../../04-scenarios/incident/account-takeover.md) 에서, 자료를 메일로 내보냈는지를 묻는 사건이라면 [자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에서 이 흔적을 어떤 순서로 맞추는지 봅니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 지메일 앱이 설치된 iOS 검체가 있는지 먼저 확인하고, 있으면 아래 질문을 풀어 봅니다.

1. 설치 앱 목록에서 지메일 앱의 번들 ID 를 찾고, 앱 컨테이너 안에 `Library/Application Support/data/` 폴더가 있는지 봅니다.
2. `data` 아래 폴더가 몇 개인지 세고, 폴더마다 오프라인 검색 DB 의 보낸 사람 칸을 보고 어느 계정인지 맞춥니다.
3. `offline_search_content` 의 `c0` 가 정말 13자리 밀리초 값인지 확인하고, 가장 이른 값과 가장 늦은 값을 UTC 로 바꿉니다.
4. 같은 `c1` 값을 공유하는 행을 묶어, 가장 긴 스레드에 메일이 몇 통 있는지 셉니다.
5. `label_counts` 의 `total_count` 합을 오프라인 검색 DB 의 행 수와 견주어, 앱이 메일 일부만 담아 두었는지 판단합니다.

## 참고 문헌

1. iLEAPP, `scripts/artifacts/gmail.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/gmail.py
2. Apple 지원 108770, "What does iCloud back up?" — https://support.apple.com/en-us/108770
