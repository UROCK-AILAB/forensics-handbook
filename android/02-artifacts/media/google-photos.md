---
title: "구글 포토"
parent: "아티팩트 · 사진·미디어"
nav_order: 670
---

# 구글 포토 (Google Photos)

## 한 줄 요약

구글 포토 앱(com.google.android.apps.photos)은 앱 전용 폴더의 gphotos DB 에 기기 안 미디어(local_media)와 클라우드 미디어(remote_media)를 따로 적고, 이미지 캐시와 앱 휴지통 DB 도 따로 두어서, 기기에서 지운 사진이 클라우드 쪽 목록이나 캐시에 남는지 볼 수 있습니다 [1].

## 무엇을 기록하나 · 왜 생기나

구글 포토는 기기의 사진을 보여 주는 갤러리이면서 계정의 클라우드 사진을 함께 보여 주는 앱이라서, 기기 안 파일 목록과 클라우드 항목 목록을 한 DB 안의 다른 표에 적습니다. 기기 안 미디어는 local_media 표에, 클라우드 미디어는 remote_media 표에, 공유받은 미디어는 shared_media 표에, 백업 대상 폴더는 backup_folders 표에 적힙니다 [1]. 화면에 띄운 이미지는 캐시 폴더에, 앱 안에서 휴지통으로 보낸 기기 사진은 local_trash.db 와 trash_files 폴더에 남습니다 [1].

각 표와 열의 공식 뜻은 구글이 공개하지 않았습니다. 이 페이지의 열 이름과 단위는 ALEAPP 가 읽는 방식에서 가져온 것이고, 앱 버전이 바뀌면 열이 없어지거나 늘어날 수 있습니다.

## 위치와 버전별 차이

경로 패턴은 아래와 같습니다 [1].

| 무엇 | 경로 패턴 |
|---|---|
| 주 DB | `*/com.google.android.apps.photos/databases/gphotos*.db` |
| 캐시 색인 DB | `*/com.google.android.apps.photos/databases/disk_cache` |
| 캐시 이미지 | `*/com.google.android.apps.photos/cache/glide_cache/*` |
| 앱 휴지통 DB | `*/com.google.android.apps.photos/databases/local_trash.db` |
| 앱 휴지통 파일 | `*/com.google.android.apps.photos/files/trash_files/*` |

주 DB 파일 이름은 gphotos 뒤에 번호가 붙는 형식이라 계정마다 파일이 따로 생기는 것으로 보이지만, 번호의 뜻은 공개 자료가 없습니다. ALEAPP 시험 자료(Android 10·13·14·15·16, 앱 버전 코드 36652547 ~ 51832862)에서 이 구조의 DB 를 읽을 수 있었습니다 [1]. 앱 전용 폴더의 위치와 확보 조건은 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md), [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지에 있습니다.

## 구조

### gphotos DB 의 표

| 표 | 주요 열 | 메모 |
|---|---|---|
| local_media | utc_timestamp, filename, filepath, capture_timestamp, timezone_offset, width, height, size_bytes, duration, latitude, longitude, folder_name, media_store_id, trash_timestamp, purge_timestamp | 뒤의 네 열(folder_name, media_store_id, trash_timestamp, purge_timestamp)은 없는 DB 도 있어 먼저 확인 |
| remote_media | utc_timestamp, filename, remote_url, capture_timestamp, timezone_offset, duration, latitude, longitude, inferred_latitude, inferred_longitude, upload_status | inferred_latitude·inferred_longitude, upload_status 는 없는 DB 도 있음. remote_url 끝의 "=s0-d" 를 지워 보여 줌 |
| shared_media | utc_timestamp, filename, remote_url, size_bytes, capture_timestamp, timezone_offset, upload_status | 표가 없는 DB 도 있음 |
| backup_folders | bucket_id | local_media 와 bucket_id 로 이어짐 |

local_media 의 media_store_id 는 이름으로 보면 MediaStore 의 `_id` 로 보이지만, 짝지어 확인한 공개 자료는 없어서 실제 데이터에서 맞춰 봅니다. remote_media 의 upload_status 는 저장된 값 그대로이고 퍼센트가 아닙니다 [1]. 값마다의 뜻은 공개 자료가 없습니다. inferred_latitude·inferred_longitude 가 무엇으로 추정한 위치인지도 알려져 있지 않습니다. backup_folders 표에 폴더가 있다고 해서 그 폴더의 파일이 올라갔다는 뜻은 아닙니다 [1].

### 캐시

disk_cache 는 SQLite DB 이고 journal 표에 last_modified_time, key, size, pending_delete 열이 있습니다 [1]. 캐시 이미지 파일은 glide_cache 폴더에 있고, journal 의 key 가 파일 경로에 들어 있는 파일을 찾으면 두 쪽을 짝지을 수 있습니다 [1]. ALEAPP 시험 자료에서 이 캐시는 0~1,833 행이었습니다 [1]. 다른 앱의 이미지 캐시와 시스템 섬네일은 [섬네일 캐시](thumbnails.md) 페이지에서 다룹니다.

### 앱 휴지통

local_trash.db 의 local 표에는 deleted_time, local_path, content_uri, trash_file_name, media_store_id(없을 수 있음), is_video 열이 있고, 휴지통 파일은 trash_files 폴더에서 trash_file_name 으로 짝짓습니다 [1]. 이 결과는 아직 남아 있는 파일을 짝지은 것일 뿐 복구(carving)한 것이 아닙니다 [1]. ALEAPP 시험 자료 10개에서 local_trash 는 모두 0행이었습니다 [1]. 구글 포토 휴지통의 보관 기간과, 구글 포토가 휴지통으로 보낸 기기 사진이 MediaStore 휴지통 표시(is_trashed)와 어떻게 맞물리는지는 실제 기기로 확인해야 합니다. MediaStore 쪽 휴지통은 [지운 사진의 흔적](mediastore/deleted-media.md) 페이지에 있습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| local_media 에 행이 있으면 앱이 그 경로의 기기 미디어를 알고 있었다는 것 | 지금도 그 파일이 기기에 있다는 것 |
| remote_media 에 행이 있으면 그 항목이 이 앱이 본 클라우드 목록에 있었다는 것 | 이 기기에서 올렸다는 것, 올린 시각 |
| backup_folders 에 폴더가 있다는 것 | 그 폴더의 파일이 실제로 올라갔다는 것 [1] |
| glide_cache 에 이미지가 있으면 앱이 그 이미지를 받아 캐시에 저장했다는 것 | 사용자가 그 이미지를 직접 열어 봤다는 것 |
| local 표에 앱 휴지통으로 보낸 시각(deleted_time)과 원래 경로(local_path)가 적혀 있다는 것 | 앱 휴지통에서 비운 뒤의 파일 내용 |

"클라우드에 사진을 올렸다" 보다 "remote_media 에 이 파일 이름과 이 촬영 시각의 항목이 있고 upload_status 가 이 값이다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

| 열 | 단위(ALEAPP 처리) | 비고 |
|---|---|---|
| utc_timestamp | 유닉스 밀리초 | 뜻은 공개되지 않음 |
| capture_timestamp | 유닉스 밀리초 | utc_timestamp 와의 차이는 공개 자료 없음 |
| timezone_offset | 밀리초 단위 시차 | ALEAPP 는 3,600,000 으로 나눠 시간 단위로 보여 줌 |
| trash_timestamp, purge_timestamp | 유닉스 밀리초 | 없는 DB 도 있음 |
| duration | 밀리초 | 이름으로 보면 재생 길이 |
| disk_cache journal.last_modified_time | 유닉스 밀리초 | 캐시 항목 |
| local_trash local.deleted_time | 유닉스 밀리초 | 앱 휴지통 |

ALEAPP 는 timezone_offset 을 시간 단위로 나눌 때 나머지를 버립니다 [1]. 그래서 +5:30 처럼 30분 단위 시차는 19,800,000 밀리초인데 도구 화면에는 5 로 나옵니다. 30분·45분 단위 시차를 쓰는 지역이 걸린 사건이면 원래 값을 DB 에서 직접 읽습니다. 유닉스 밀리초를 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

## 함정과 한계

- 열 이름·단위는 공개 도구의 해석이고 구글의 규격이 아닙니다 [1]. 앱 버전마다 열이 다를 수 있어서, 쿼리 전에 표 구조를 먼저 확인합니다.
- local_media 는 앱이 알고 있는 기기 미디어 목록이라 파일이 지워진 뒤에도 행이 얼마나 남는지는 실제 데이터로 확인합니다.
- 클라우드 쪽 원본과 전체 기록은 기기에 없고, 계정에서 받은 자료로 확인해야 합니다. 방법은 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 페이지에 있습니다.
- 앱 휴지통 결과는 남아 있는 파일을 짝지은 것이라 [1], 비운 파일은 이 방법으로 나오지 않습니다.

## 직접 분석해 보기

**DB 쿼리.** 확보한 gphotos DB 사본을 SQLite 를 읽는 공개 도구(예: sqlite3 명령줄)로 열어 봅니다. 아래 쿼리는 이 페이지의 열 이름으로 만든 예시이고, 열이 없는 버전이면 그 열을 빼고 씁니다.

```sql
-- 표 구조부터 확인
PRAGMA table_info(local_media);

-- 기기 안 미디어: 촬영 시각과 시차
SELECT filename, filepath,
       datetime(capture_timestamp / 1000, 'unixepoch') AS capture_utc,
       timezone_offset / 60000.0 AS offset_minutes,
       media_store_id, trash_timestamp
FROM local_media ORDER BY capture_timestamp;

-- 클라우드 항목
SELECT filename, remote_url, upload_status,
       datetime(capture_timestamp / 1000, 'unixepoch') AS capture_utc
FROM remote_media ORDER BY capture_timestamp;
```

offset_minutes 로 보면 30분 단위 시차가 잘리지 않습니다. remote_media 의 파일 이름·촬영 시각이 local_media 에 없으면, 기기에서 지웠거나 다른 기기에서 올린 항목일 수 있으니 MediaStore 와 캐시를 함께 봅니다.

**공개 도구.** ALEAPP 의 googlePhotos 모듈이 위 표들과 캐시, 앱 휴지통을 읽어 보고서로 보여 줍니다 [1]. 도구 결과의 시차 열은 시간 단위로 잘린 값이라서, 시차가 중요한 항목은 위 쿼리로 원래 값을 다시 확인합니다.

## 교차 검증

- [미디어 저장소 (MediaStore)](mediastore/index.md) — media_store_id 로 보이는 번호를 files 표의 `_id` 와 맞춰 봅니다.
- [카메라 사진과 메타데이터 (DCIM·EXIF)](dcim-exif.md) — 원본 파일의 EXIF 시각·시차와 capture_timestamp·timezone_offset 을 비교합니다.
- [섬네일 캐시 (Thumbnails)](thumbnails.md) — 시스템 섬네일과 다른 앱 캐시를 봅니다.
- [계정 (Accounts)](../system-account/accounts/index.md) — 기기에 등록된 구글 계정을 확인합니다.
- [데이터 사용량 (netstats)](../network/netstats.md) — 구글 포토의 송신량이 올린 시기와 맞는지 봅니다.
- [자료를 밖으로 보냈나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md), [지운 대화와 사진 찾기 (Deleted Content)](../../04-scenarios/activity/deleted-content.md) — 이 기록을 쓰는 조사 시나리오입니다.

## 실습

공개된 시험 자료(NIST CFReDS 등)에서 구글 포토가 설치된 Android 이미지를 구할 수 있으면 다음을 풀어 봅니다.

1. gphotos DB 가 몇 개인지, 각 DB 에 local_media·remote_media·shared_media·backup_folders 표가 모두 있는지 확인합니다.
2. local_media 의 media_store_id 를 external.db 의 `_id` 와 맞춰, 같은 파일인지 경로로 확인합니다.
3. timezone_offset 이 한 시간 단위가 아닌 행이 있는지 찾고, 도구 화면의 값과 비교합니다.
4. disk_cache 의 journal 항목과 glide_cache 파일을 짝지어, 기기 안에 원본이 없는 캐시 이미지가 있는지 봅니다.

## 참고 문헌

1. ALEAPP — scripts/artifacts/googlePhotos.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/googlePhotos.py
