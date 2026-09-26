---
title: "탭과 세션"
parent: "사파리"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1180
---

# 탭과 세션 (Tabs·Sessions)

사파리는 열려 있던 창과 탭, 최근에 닫은 탭, 탭별 뒤로/앞으로 목록, iCloud 로 보이는 다른 기기의 탭, 탭 스냅샷을 여러 plist 와 SQLite 파일에 나눠 적어 두고, 이 파일들을 모으면 방문 기록만으로는 보이지 않는 "그때 무엇이 열려 있었나" 를 다시 짤 수 있습니다.

## 무엇을 기록하나

탭 관련 파일은 하는 일이 저마다 다릅니다 [1][3].

| 파일 | 형식 | 담긴 것 |
|---|---|---|
| `LastSession.plist` | plist | 마지막 세션의 창과 탭. 탭마다 주소·제목·마지막 방문 시각·닫은 시각 [1] |
| `RecentlyClosedTabs.plist` | plist | 최근에 닫은 탭과 창, 개인 정보 보호 창 여부 [1] |
| `BrowserState.db` | SQLite | 탭 목록과 탭마다의 뒤로/앞으로 목록 [1] |
| `SafariTabs.db` | SQLite | Safari 17 프로필 이후의 탭·프로필 정보 [1] |
| `CloudTabs.db` | SQLite | iCloud 로 보이는 다른 기기의 탭과 기기 이름 [1] |
| `TabSnapshots/Metadata.db` | SQLite | 탭 스냅샷 파일의 목록 [1][3] |

## 위치와 버전별 차이

탭 스냅샷 목록은 `~/Library/Caches/com.apple.Safari/TabSnapshots/Metadata.db` [3] 와 컨테이너 쪽 `~/Library/Containers/com.apple.Safari/Data/Library/Caches/com.apple.Safari/TabSnapshots/Metadata.db` [1] 두 곳에 있을 수 있습니다. 나머지 파일은 사파리 데이터 폴더에 있지만, `~/Library/Safari/` 와 컨테이너 가운데 파일마다 어느 쪽인지는 알려져 있지 않아서 두 곳을 다 봅니다. 두 폴더 이야기는 허브 [사파리 (Safari)](index.md)에 있습니다.

`SafariTabs.db` 는 Safari 17 에서 프로필(여러 프로필)이 들어오면서 쓰이고 [1], 그 밖의 파일이 어느 macOS·사파리 버전부터 쓰였는지는 공개 자료가 없습니다. 분석 대상의 버전에 따라 어떤 파일은 아예 없을 수 있으니, 없는 파일을 "지웠다" 로 읽기 전에 그 버전에서 원래 쓰는 파일인지부터 확인합니다.

## 구조

### LastSession.plist

맨 위에 `SessionVersion` 과 창 배열 `SessionWindows` 가 있고, 창마다 선택된 탭 번호 `SelectedTabIndex` 와 탭 배열 `TabStates` 가 있습니다 [1]. 탭 항목에는 `TabURL`, `TabTitle`, `LastVisitTime`, `DateClosed` 가 들어 있고, `LastVisitTime` 은 맥 절대 시각 숫자입니다 [1]. 탭 항목의 `SessionState` 는 암호화돼 있어서 mac_apt 도 이 값은 풀지 않습니다 [1].

### RecentlyClosedTabs.plist

맨 위에 `ClosedTabOrWindowPersistentStatesVersion` 과 배열 `ClosedTabOrWindowPersistentStates` 가 있고, 항목마다 종류 `PersistentStateType` 과 내용 `PersistentState` 가 있습니다 [1]. 종류 값 0 은 닫은 탭 하나, 1 은 닫은 창이고, 창이면 안의 `TabStates` 에 탭들이 있습니다 [1]. 내용에는 `DateClosed`, `IsPrivateWindow`, `TabURL`, `TabTitle`, 창이면 `TabStates` 가 들어 있고, `IsPrivateWindow` 는 닫힌 창이 개인 정보 보호 창이었는지를 나타냅니다 [1]. 이 값을 어떻게 해석하는지는 [개인 정보 보호 브라우징 (Private Browsing)](private-browsing.md)에서 다룹니다.

### BrowserState.db

표 `tabs`(열 `id`, `url`, `title`, `uuid`)와 `tab_sessions`(열 `tab_uuid`, `session_data`)를 `tab_sessions.tab_uuid = tabs.uuid` 로 잇습니다 [1]. `session_data` 는 앞 4바이트 뒤에 plist 가 들어 있는 BLOB 이고, 이 plist 의 `SessionHistory` 아래 `SessionHistoryEntries`(항목마다 `SessionHistoryEntryURL`, `SessionHistoryEntryTitle`)에 페이지가 순서대로 있습니다 [1]. 탭 하나마다 뒤로/앞으로 목록이 순서대로 남는 셈입니다. `SessionHistoryCurrentIndex` 라는 키도 있는데, 지금 보던 자리를 뜻하는 것으로 보이며 뜻을 풀어 둔 공개 자료는 없습니다 [1]. 앞 4바이트의 뜻은 알려져 있지 않아서, 직접 뽑을 때는 그 뒤에 plist 머리(바이너리 plist 라면 `bplist`)가 있는지 확인하고 읽습니다.

### SafariTabs.db

표 `bookmarks` 에 열 `id`, `special_id`, `parent`, `type`, `subtype`, `title`, `url`, `local_attributes`, `date_closed`, `external_uuid`, `server_id` 가 있고, `local_attributes` 는 plist 로 안에 `LastVisitTime`, `DateClosed` 가 있습니다 [1]. 이름은 `bookmarks` 지만 이 표에는 탭과 프로필이 들어 있습니다. 프로필 목록은 `parent == 0 AND type == 1 AND subtype == 2` 인 행입니다 [1]. `title` 은 프로필 이름, `external_uuid` 는 `Profiles` 아래 폴더 이름과 맞춰 보는 값, `server_id` 는 그 프로필의 확장 폴더 이름 앞에 붙는 값입니다 [1]. Safari 17 이후 프로필마다 방문 기록 파일이 따로 생기는 점은 [방문 기록 (History.db)](history.md)에서 다룹니다.

### CloudTabs.db

표 `cloud_tabs`(열 `device_uuid`, `tab_uuid`, `system_fields`, `title`, `url`, `is_showing_reader`, `is_pinned`)와 `cloud_tab_devices`(열 `device_uuid`, `device_name`)를 `device_uuid` 로 잇습니다 [1]. `system_fields` 는 직렬화된 plist 이고 `RecordCtime`, `RecordMtime` 을 담습니다 [1].

### TabSnapshots/Metadata.db

표 `snapshot_metadata` 에 열 `date_created`, `filename`, `url` 이 있어서 [1], 스냅샷 파일 이름과 그 탭의 주소, 만든 시각을 짝지을 수 있습니다.

## 증거로서 의미

**증명하는 것.** `LastSession.plist` 와 `BrowserState.db` 는 기록을 남긴 시점에 열려 있던 탭과 탭마다의 이동 순서를, `RecentlyClosedTabs.plist` 는 닫은 탭·창과 닫은 시각을 보여 줍니다 [1]. 탭별 뒤로/앞으로 목록은 한 탭 안에서 어떤 순서로 페이지를 옮겨 다녔는지를 보여 줘서, 방문 기록의 시간순 목록에 "어느 탭에서" 라는 축을 더할 수 있습니다. `CloudTabs.db` 는 같은 iCloud 계정에 묶인 다른 기기의 이름과 그 기기에서 열려 있던 탭을 보여 줍니다 [1].

**증명하지 못하는 것.** 탭이 열려 있었다는 기록은 사용자가 그 페이지를 보고 있었다는 뜻이 아닙니다. `CloudTabs.db` 의 탭은 다른 기기에서 열린 것이라서 이 맥에서 방문한 것으로 쓰면 안 되고, `RecordCtime`·`RecordMtime` 이 무엇을 기준으로 한 시각인지(이름으로 보면 레코드 생성·수정 시각)는 공개 자료가 없습니다. iCloud 탭과 탭 그룹은 표준 데이터 보호에서도 종단간 암호화되므로 [4], 이 기기 안의 파일이 다른 기기의 탭을 보여 주는 드문 자료가 될 수 있습니다.

보고서에는 "이 기기의 `CloudTabs.db` 에 'OO' 이라는 이름의 기기에서 이 주소가 열린 탭으로 올라 있다" 처럼 파일과 기기를 함께 밝혀 씁니다.

## 시각 해석

사파리의 plist·DB 시각은 대부분 맥 절대 시각(2001-01-01 00:00:00 UTC 부터 흐른 초)입니다 [1]. 이 페이지의 시각 값은 다음과 같습니다.

| 값 | 있는 곳 | 뜻 |
|---|---|---|
| `LastVisitTime` | `LastSession.plist` 탭, `SafariTabs.db` `local_attributes` | 탭의 마지막 방문 시각 [1] |
| `DateClosed` | `LastSession.plist`, `RecentlyClosedTabs.plist`, `SafariTabs.db` `local_attributes` | 탭·창을 닫은 시각 [1] |
| `date_closed` | `SafariTabs.db` `bookmarks` 표 | 닫은 시각(열 이름 기준) [1] |
| `RecordCtime`, `RecordMtime` | `CloudTabs.db` `system_fields` | 공개 자료 없음 [1] |
| `date_created` | `TabSnapshots/Metadata.db` | 스냅샷을 만든 시각(열 이름 기준) [1] |

열마다 저장 형식이 실수인지 plist 날짜인지는 파일을 열어 직접 확인하고, 바꾸는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다.

## 함정과 한계

**기록 지우기가 탭 쪽도 지웁니다.** 기록 지우기는 열린 페이지의 뒤로/앞으로 목록과 열린 페이지 스냅샷도 지웁니다 [2]. 그래서 `BrowserState.db` 의 뒤로/앞으로 목록이나 스냅샷 목록이 비어 있으면 기록 지우기와 함께 따져 보고, 지우기 대상 전체는 [방문 기록 (History.db)](history.md)에서 봅니다.

**`LastSession.plist` 는 마지막 세션만 보여 줍니다.** 이름과 키 구성으로 보면 마지막 세션의 창과 탭만 담는 파일로 보여서, 그 전에 열려 있던 탭은 다른 파일이나 방문 기록에서 찾습니다. 파일을 언제 새로 쓰는지는 공개 자료가 없습니다.

**`bookmarks` 표를 북마크로 읽지 않습니다.** `SafariTabs.db` 의 `bookmarks` 표에는 탭과 프로필이 들어 있고, 북마크 자체가 이 표로 옮겨 갔는지는 공개 자료가 없습니다. 북마크는 [북마크와 읽기 목록 (Bookmarks·Reading List)](bookmarks.md)에서 다룹니다.

## 직접 분석해 보기

사본에서 `BrowserState.db` 의 탭과 세션 BLOB 을 짝짓습니다. LEFT JOIN 으로 이어서 세션 행이 없는 탭도 빠뜨리지 않습니다 [1].

```sql
SELECT t.id, t.title, t.url, length(s.session_data) AS blob_len
FROM tabs AS t
LEFT JOIN tab_sessions AS s ON s.tab_uuid = t.uuid;
```

`session_data` 는 plist 가 든 BLOB 이라서, 파일로 떼어 낸 뒤 앞 4바이트를 잘라 내고 `plutil -p` 나 파이썬 `plistlib` 으로 열고 `SessionHistoryEntries` 를 순서대로 읽습니다.

`SafariTabs.db` 의 프로필 목록은 아래 질의로 뽑습니다 [1].

```sql
SELECT id, title, external_uuid, server_id
FROM bookmarks
WHERE parent = 0 AND type = 1 AND subtype = 2;
```

`external_uuid` 가 `Profiles` 아래 폴더 이름과 같은 행이 그 프로필입니다 [1]. 결과를 실제 폴더 이름과 나란히 놓고, 짝이 없는 폴더나 행이 있는지 봅니다.

`CloudTabs.db` 는 기기 이름과 탭을 이어 읽습니다 [1].

```sql
SELECT d.device_name, t.title, t.url, t.is_pinned, t.is_showing_reader
FROM cloud_tabs AS t
JOIN cloud_tab_devices AS d ON d.device_uuid = t.device_uuid
ORDER BY d.device_name;
```

공개 도구로는 mac_apt 의 사파리 플러그인이 위 파일들을 모두 읽습니다 [1]. SQLite 파일 옆에 `-wal` 파일이 있으면 함께 수집하고, 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md), plist 는 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에서 다룹니다.

## 교차 검증

| 함께 볼 것 | 이유 |
|---|---|
| [방문 기록 (History.db)](history.md) | 탭에서 연 주소의 방문 시각 |
| [캐시와 웹 데이터 (Cache·WebKit)](cache-webkit.md) | 같은 주소의 쿠키와 캐시 |
| [개인 정보 보호 브라우징 (Private Browsing)](private-browsing.md) | `IsPrivateWindow` 해석 |
| [앱 저장 상태 (Saved Application State)](../../file-folder-usage/saved-application-state.md) | 앱 쪽에 남는 창 상태 |
| [아이클라우드 계정 (iCloud Account)](../../cloud-apps/icloud-account.md) | `CloudTabs.db` 기기들이 묶인 계정 |
| [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md) | 브라우저 흔적을 묶어 읽는 순서 |

## 실습

공개 맥 시험 이미지에서 사파리 데이터 폴더와 캐시 폴더를 모아 아래 질문을 풀어 봅니다.

1. 이 이미지에는 위 표의 파일 가운데 어느 것이 있고, 각각 `~/Library/Safari/` 와 컨테이너 가운데 어디에 있는가
2. `LastSession.plist` 에서 창은 몇 개이고, 창마다 선택된 탭의 주소는 무엇인가
3. `BrowserState.db` 에서 뒤로/앞으로 목록이 가장 긴 탭을 골라 이동 순서를 적고, 방문 기록의 시각과 맞춰 보라
4. `RecentlyClosedTabs.plist` 에 `IsPrivateWindow` 가 참인 항목이 있는가
5. `CloudTabs.db` 가 있다면 기기 이름은 몇 개이고, 이 맥의 방문 기록에도 있는 주소가 있는가

## 참고 문헌

1. mac_apt Safari 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/safari.py
2. Apple Support, Safari 사용 설명서(Mac) — Clear your browsing history in Safari on Mac — https://support.apple.com/guide/safari/clear-your-browsing-history-sfri47acf5d6/mac
3. ForensicArtifacts 정의 파일 webbrowser.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
4. Apple Support, iCloud data security overview (2026-01-05) — https://support.apple.com/en-us/102651
