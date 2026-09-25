---
title: "북마크와 읽기 목록"
parent: "사파리"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 750
---

# 북마크와 읽기 목록 (Bookmarks·Reading List)

## 한 줄 요약

사파리 북마크는 Bookmarks.db 의 `bookmarks` 표에 폴더와 항목이 한 표로 들어가고, 이 DB 는 암호화하지 않은 로컬 백업에도 HomeDomain 아래로 들어가서 방문 기록이 없는 백업에서도 열어 볼 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

사용자가 북마크를 추가하거나 폴더를 만들면 Bookmarks.db 에 행이 생기고, 공개 자료들은 이 DB 에서 URL, 제목, 부모 북마크, `syncable`, `hidden`, `deleted` 값을 뽑습니다[1]. iCloud 로 북마크를 맞추는 기기에서는 동기화 상태를 담는 표와 칸도 함께 쓰입니다(아래 구조 절).

읽기 목록(Reading List)이 이 DB 에 함께 들어간다는 설명은 맥의 예전 `Bookmarks.plist` 에서 "com.apple.ReadingList" 폴더 아래에 둔다는 검색 요약에만 있었고, iOS 의 Bookmarks.db 에서 읽기 목록을 어떻게 구분하는지는 확인하지 못했습니다. 그래서 여기서는 읽기 목록을 가려내는 기준을 단정하지 않고, 검체에서 확인할 칸만 짚습니다.

## 위치와 버전별 차이

| 구분 | 위치 | 출처 |
|---|---|---|
| 기기 | `/private/var/mobile/Library/Safari/Bookmarks.db` | [1][2] |
| 로컬 백업 | HomeDomain `Library/Safari/Bookmarks.db` | 관찰(확인 범위: iOS 27.0) |

관찰한 백업은 암호화하지 않은 백업이었는데도 Bookmarks.db 가 들어 있었습니다(확인 범위: iOS 27.0). 같은 백업에 History.db 와 탭 DB 는 없어서, 백업만 받은 사건에서는 사파리 흔적 가운데 이 DB 를 먼저 열게 됩니다. 백업에서 파일을 찾는 법은 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md)에 있습니다. iOS 버전마다 칸이 어떻게 늘었는지는 이번 자료로 확인하지 못했습니다.

## 구조

관찰한 Bookmarks.db 의 표는 아래와 같습니다(확인 범위: iOS 27.0).

| 표 | 칸 |
|---|---|
| `bookmarks` | 아래 표의 37개 칸 |
| `bookmark_title_words` | `id`, `bookmark_id`, `word`, `word_index` |
| `folder_ancestors` | `id`, `folder_id`, `ancestor_id` |
| `database_properties` | `key`, `value` |
| `generations` | `generation` |
| `sync_properties` | `key`, `value` |
| `sync_record_ids` | `record_type`, `record_name`, `record_id_data` |
| `sync_record_zone_metadata` | `record_zone_name`, `record_zone_id_data`, `last_server_change_token`, `hash_generator`, `sync_record_zone_metadata_state` |
| `sqlite_sequence` | SQLite 가 만드는 표 |

`bookmarks` 표의 칸은 성격에 따라 묶으면 아래와 같습니다. 묶음은 칸 이름으로 나눈 것이고, 각 칸의 값 뜻은 확인하지 못했습니다(확인 범위: iOS 27.0).

| 묶음 | 칸 |
|---|---|
| 위치·종류 | `id`, `special_id`, `parent`, `type`, `subtype`, `num_children`, `order_index`, `last_selected_child`, `hidden`, `hidden_ancestor_count` |
| 내용 | `title`, `url`, `topic_title`, `feature_text`, `fetched_feature_text`, `icon`, `fetched_icon` |
| 상태 | `editable`, `deletable`, `read`, `archive_status`, `deleted`, `web_filter_status`, `is_marked_for_expiration`, `date_closed`, `last_modified`, `added`, `locally_added`, `modified_attributes` |
| 동기화 | `external_uuid`, `server_id`, `sync_key`, `sync_data`, `syncable`, `dav_generation` |
| 이진 속성 | `extra_attributes`, `local_attributes` |

`type`(폴더인지 항목인지), `special_id`, `read`, `archive_status` 에 어떤 값이 들어가는지는 자료로 확인하지 못했고, 읽기 목록 항목의 `extra_attributes` 에 추가한 날짜나 미리 보기 글이 들어간다는 설명도 확인하지 못했습니다. `read` 와 `archive_status` 는 이름만 보면 읽기 목록과 이어질 것 같지만, 검체에서 읽기 목록에 넣은 항목과 값을 대조해 본 뒤 판단합니다.

SafariTabs.db 의 `bookmarks` 표와 칸 이름이 `parent`, `title`, `url`, `last_modified`, `date_closed`, `extra_attributes`, `local_attributes`, `external_uuid`, `deleted`, `order_index` 로 겹칩니다[3](확인 범위: iOS 27.0). 두 DB 가 같은 구조를 쓰는지는 확인하지 못했고, 탭 쪽은 [탭과 세션 (Tabs)](tabs.md)에서 다룹니다.

설정 파일에도 북마크와 이어진 이름의 키가 있습니다(확인 범위: iOS 27.0).

| 위치 | 키 |
|---|---|
| AppDomain-com.apple.mobilesafari `Library/Preferences/com.apple.mobilesafari.plist` | `LastPeriodicBookmarksAnalyticsReportTime`(float), `LastBookmarksDatabaseHealthReportDate`(datetime) |
| HomeDomain `Library/Preferences/com.apple.SafariBookmarksSyncAgent.plist` | `MigrationStateEncodedRecordData`(bytes), `TabGroupMigrationStateEncodedRecordData`(bytes), `NewestLaunchedSafariBookmarksSyncAgentVersion`(str) 등 |
| 제한 설정(구성 프로파일) plist | 제한 설정 목록 안의 `webContentFilterWhitelistedBookmarks` |

`webContentFilterWhitelistedBookmarks` 는 이름으로 보아 관리 기기의 웹 콘텐츠 필터가 허용한 북마크와 이어져 보이지만 해석은 확인하지 못했고, 구성 프로파일은 [구성 프로파일과 MDM (Configuration Profiles·MDM)](../../credentials-security/configuration-profiles.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `bookmarks` 에 URL 이 있는 행이 있으면 수집 시점에 그 주소가 사파리 북마크 DB 에 저장되어 있었다는 사실을 보여 줍니다. `parent` 와 `folder_ancestors` 를 따라가면 어느 폴더 아래에 두었는지도 알 수 있습니다.

**증명하지 못하는 것.** 북마크가 있다고 그 페이지를 방문했다고 할 수 없고, 누가 언제 추가했는지도 이 행만으로는 말할 수 없습니다. `sync_*` 표와 `server_id`·`sync_key`·`sync_data` 칸이 채워져 있으면 iCloud 동기화와 이어진 행일 수 있어서(확인 범위: iOS 27.0), 이 기기에서 직접 추가한 것인지 다른 기기에서 넘어온 것인지를 가를 근거는 아직 확인하지 못했습니다. `deleted` 값이 있는 행을 지운 북마크로 볼 수 있을지도 검체에서 확인한 뒤에 씁니다.

보고서에는 "수집 시점에 이 URL 이 사파리 북마크 DB 의 이 폴더 아래에 저장되어 있었다" 처럼 씁니다.

## 시각 해석

`last_modified`, `added`, `date_closed` 는 이름으로 보아 시각이나 시각과 이어진 값이지만(확인 범위: iOS 27.0), 기준과 단위는 이번에 연 자료로 확인하지 못했습니다. 같은 사파리의 방문 기록과 탭 DB 에서 쓰는 방식처럼 값이 978307200 보다 큰지 작은지로 UNIX 시각과 Apple 절대 시각을 가려 본 뒤, 결과가 수집 시각보다 앞인지 확인하고 씁니다. 두 기준은 [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

## 함정과 한계

- 공개 도구 iLEAPP 의 북마크 모듈은 `SELECT title, url, hidden FROM bookmarks` 만 해서 읽기 목록과 폴더를 나누지 않고 시각도 바꾸지 않습니다[4]. 도구 결과만 보면 폴더 행과 항목 행이 섞이고, 읽기 목록 여부와 시각은 빠집니다.
- 이 DB 에는 폴더 행도 함께 들어 있어서, 행 수를 북마크 개수로 그대로 옮기지 않습니다.
- `hidden` 과 `hidden_ancestor_count` 가 채워진 행은 화면에 보이지 않는 항목일 수 있어서, 사용자가 본 목록과 DB 의 행이 다를 수 있습니다. 값의 뜻은 검체로 확인합니다.

## 직접 분석해 보기

백업이라면 Manifest.db 에서 HomeDomain `Library/Safari/Bookmarks.db` 를 찾아 사본을 만들고 sqlite3 로 엽니다. 먼저 폴더 구조를 보려고 모든 행을 부모 순서로 뽑습니다.

```sql
SELECT id, parent, type, special_id, title, url,
       hidden, deleted, read, archive_status, syncable,
       added, last_modified, date_closed
FROM bookmarks
ORDER BY parent, order_index;
```

`url` 이 빈 행은 폴더일 수 있어서 그 행의 `title` 로 폴더 이름을 보고, 그 폴더 아래 행들의 `type`·`read`·`archive_status` 값이 다른 폴더와 어떻게 다른지 비교합니다. 폴더 경로를 한꺼번에 보려면 `folder_ancestors` 를 이어 붙입니다.

```sql
SELECT b.id, b.title, b.url, a.ancestor_id, f.title AS ancestor_title
FROM bookmarks b
JOIN folder_ancestors a ON a.folder_id = b.parent
LEFT JOIN bookmarks f ON f.id = a.ancestor_id
WHERE b.url IS NOT NULL
ORDER BY b.id;
```

이 질의는 `folder_ancestors.folder_id` 가 항목의 부모 폴더를 가리킨다고 보고 쓴 예라서, 결과가 이상하면 `parent` 를 거슬러 올라가는 방식으로 바꿔 확인합니다. `extra_attributes` 와 `local_attributes` 는 이진 값이라 `hex()` 로 꺼내 [속성 목록 파일 (plist·NSKeyedArchiver)](../../../01-foundations/data-formats/plist.md)의 방법으로 열어 봅니다. 공개 도구로는 iLEAPP 결과[4]와 행 수를 맞춰 보되, 폴더 행이 섞여 있는지 함께 확인합니다.

> 그림 자리: `bookmarks` 표에서 폴더 행과 항목 행이 `parent` 로 이어지고, `folder_ancestors` 가 조상 폴더를 한 번에 가리키는 모양

## 교차 검증

북마크한 URL 을 [방문 기록 (History.db)](history.md)에서 찾아 실제 방문이 있는지 맞춰 보고, 열린 탭은 [탭과 세션 (Tabs)](tabs.md)에서 봅니다. 조사 흐름은 [웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md)을 따릅니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 검체나 직접 만든 시험 기기의 백업으로 아래를 풀어 봅니다.

1. 시험 기기에서 북마크 하나와 읽기 목록 항목 하나를 추가한 뒤 백업하고, 두 행의 `parent`·`type`·`read`·`archive_status` 값이 어떻게 다른지 비교합니다.
2. `url` 이 빈 행의 `title` 을 모두 뽑아 어떤 폴더가 있는지 봅니다.
3. `added` 와 `last_modified` 값의 자릿수를 보고 시각 기준을 판단해 봅니다.
4. `deleted` 값이 채워진 행이 있는지 찾고, 사파리 화면에 그 북마크가 보이는지 비교합니다.

## 참고 문헌

1. Forensafe, iOS Safari Browser — https://forensafe.com/blogs/iOSSafari.html
2. iOS 15 Image Forensics Analysis and Tools Comparison - Native Apps (blog.digital-forensics.it, 2023-10) — https://blog.digital-forensics.it/2023/10/ios-15-image-forensics-analysis-and.html
3. iLEAPP `scripts/artifacts/safariTabs.py` (abrignoni/iLEAPP, main) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/safariTabs.py
4. iLEAPP `scripts/artifacts/safariBookmarks.py` (abrignoni/iLEAPP, main, 2026-07-21 갱신) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/safariBookmarks.py
