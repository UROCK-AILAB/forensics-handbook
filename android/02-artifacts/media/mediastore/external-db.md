---
title: "미디어 DB 구조"
parent: "미디어 저장소"
grand_parent: "아티팩트 · 사진·미디어"
nav_order: 630
---

# 미디어 DB 구조 (external.db)

미디어 저장소(MediaStore)가 공용 저장 공간의 사진·동영상·오디오·문서를 색인해 두는 외부 볼륨 DB(external.db)의 표와 칸, 시각 단위, 스키마 버전을 정리합니다. 표와 칸은 AOSP MediaProvider 저장소의 main 가지, 곧 현행 AOSP 기준이라 Android 출시 버전마다 다를 수 있습니다. 휴지통과 삭제 흔적은 [지운 사진의 흔적](deleted-media.md) 페이지에서 다룹니다.

## 한 줄 요약

external.db 의 중심은 files 표 하나이고, 이미지·오디오·동영상·다운로드 목록은 모두 이 표 위에 만든 보기(view)라서, files 표의 경로·소유 앱·시각·상태 칸을 읽으면 미디어 저장소가 파일 하나를 어떻게 알고 있는지 볼 수 있습니다 [1].

## 무엇을 기록하나 · 왜 생기나

MediaProvider 는 권한(authority) 이름이 "media" 인 콘텐츠 제공자(content provider)이고, 예전 제공자용으로 "media_legacy" 도 정의돼 있습니다 [2]. 앱이 사진을 저장하거나 목록을 조회하면 이 제공자를 거치고, 제공자는 볼륨마다 DB 를 따로 둡니다. 볼륨 이름 상수는 내부 "internal", 외부 전체 "external", 기본 외부 저장소 "external_primary" 이고, DB 파일 이름은 내부 볼륨이 internal.db, 외부 볼륨이 external.db 입니다(DatabaseHelper 의 INTERNAL_DATABASE_NAME, EXTERNAL_DATABASE_NAME) [1][2]. 사용자가 찍은 사진과 내려받은 파일은 외부 볼륨 쪽이라서 조사에서 주로 보는 DB 는 external.db 입니다.

files 표의 행 하나는 공용 저장 공간의 파일 하나에 대응합니다. 앱이 ContentResolver 로 넣은 행도 있고, 파일을 직접 만들거나 고친 뒤 미디어 스캔이 채운 행도 있어서, 행을 마지막으로 바꾼 작업이 어느 쪽이었는지는 뒤에 나오는 `_modifier` 칸으로 가늠합니다.

## 위치와 버전별 차이

external.db 가 기기 안 어느 폴더에 있는지, 그리고 MediaProvider 가 몇 번 Android 부터 메인라인 모듈 패키지로 나뉘었는지는 공개 자료로 정해지지 않아 검체에서 확인합니다. 보고서에는 검체에서 실제로 찾은 경로를 씁니다. 앱 데이터 폴더의 일반 구조는 [앱 데이터 폴더 구조](../../../01-foundations/storage/app-data-layout.md) 페이지에 있습니다.

삼성 기기에는 AOSP external.db 와 별도로 삼성 미디어 제공자의 DB 가 있습니다. 이 DB 는 경로 패턴 `*/com.samsung.android.providers.media/databases/media.db*` 로 찾을 수 있고, ALEAPP 시험 검체 가운데 Android 10·11·13·14·15 삼성 기기에서 나왔습니다 [3]. 두 DB 는 표 구조가 달라서 아래 "삼성 media.db" 절에 따로 정리합니다.

사용자와 프로필이 여럿이면 DB 도 여럿일 수 있습니다. ALEAPP 시험 검체 cookbook_a11 과 samsungs20_a13 에서는 user/150 아래에 두 번째 media.db 가 있었고, `system/users/150.xml` 이 사용자 150 을 "Secure Folder" 라는 관리 프로필로 기록했습니다 [3]. `dumpsys user` 출력에서도 두 번째 사용자(isPrimary=false, parentId 있음)와 UserProperties 의 mMediaSharedWithParent 칸을 볼 수 있고, 그 사용자가 보안 폴더인지는 `system/users/<번호>.xml` 로 확인합니다. 프로필 구조는 [보안 폴더와 작업 프로필](../../../01-foundations/security-model/secure-folder-work-profile.md) 페이지를 봅니다.

adb 일반 셸 권한으로 external.db 파일 자체를 읽을 수 있는지는 공개 자료가 없어 기기에서 확인해야 합니다.

### 스키마 버전

현행 AOSP 의 DatabaseHelper 에는 출시 버전별 스키마 번호 상수가 있고, 최신(VERSION_LATEST)은 VERSION_V 입니다. Android 16 용 상수는 따로 없습니다 [1].

| 상수 | 값 |
|---|---|
| VERSION_R | 1115 |
| VERSION_S | 1209 |
| VERSION_T | 1308 |
| VERSION_U | 1409 |
| VERSION_V | 1506 |

주요 칸과 표는 아래 업그레이드 단계에서 생겼습니다 [1].

| 단계 | 생긴 것 |
|---|---|
| 1000 미만 | owner_package_name |
| 1004 | `_hash`, is_pending |
| 1005 | 다운로드 정보 |
| 1010 | date_expires, is_trashed |
| 1018 전후 | relative_path 등 경로 칸 |
| 1020 | volume_name |
| 1109 | generation_added, generation_modified |
| 1202 | `_modifier` |
| 1205 | is_recording |
| 1207 | redacted_uri_id |
| 1208 | `_user_id` |
| 1301 | deleted_media 표 |
| 1302 | `_special_format` |
| 1408 전후 | media_grants 재생성, generation_granted |
| 1500 | oem_metadata |
| 1501 | inferred_media_date |

상수 이름의 글자를 Android 버전으로 읽어 "deleted_media 표는 Android 13 부터" 처럼 말하면 상수 이름에 기댄 추정이 됩니다. 번호로 말할 수 있는 것은 is_trashed 와 date_expires 가 VERSION_R(1115) 이전 단계에서, deleted_media 표가 VERSION_S(1209) 와 VERSION_T(1308) 사이에서 생겼다는 점까지입니다 [1]. 검체의 external.db 가 몇 번 스키마인지는 위 표의 칸이 있는지 없는지를 맞춰 보면 대략 어느 단계 이후의 DB 인지 짐작할 수 있습니다.

## 구조

### 표와 보기

현행 스키마를 만드는 코드(createLatestSchema)가 만드는 표와 보기는 다음과 같습니다 [1].

| 종류 | 이름 |
|---|---|
| 표 | local_metadata(generation), android_metadata(locale), thumbnails, album_art, videothumbnails, files, log(time, message), deleted_media |
| 외부 볼륨에만 있는 표 | audio_playlists_map, media_grants, search_index_processing_status |
| 보기 | audio, video, images, downloads, audio_playlists(외부만), audio_artists, audio_artists_albums, audio_albums, audio_genres, search, searchhelpertitle |
| 트리거 | files_insert, files_update, files_delete |

보기는 files 표를 조건으로 거른 것이라서, images 는 media_type=1, audio 는 media_type=2, video 는 media_type=3, audio_playlists 는 media_type=4, downloads 는 is_download=1 인 행입니다 [1]. media_type 값 전체는 0 NONE, 1 IMAGE, 2 AUDIO, 3 VIDEO, 4 PLAYLIST, 5 SUBTITLE, 6 DOCUMENT 입니다 [2]. 보기는 조건에 맞는 행만 보여 주니, 분석할 때는 files 표를 직접 읽어야 media_type 이 0 인 행까지 빠짐없이 봅니다. 음악 관련 보기(audio_artists, audio_albums, audio_genres 등)는 is_pending=0 AND is_trashed=0 조건으로 대기·휴지통 항목도 뺍니다 [1].

트리거 세 개는 각각 `_INSERT`, `_UPDATE`, `_DELETE` 라는 사용자 정의 함수를 불러 MediaProvider 에 변경을 알리는 역할만 하고, DB 안에 따로 기록을 남기지는 않습니다 [1][6].

### files 표의 주요 칸

| 묶음 | 칸 |
|---|---|
| 식별·경로 | `_id`(INTEGER PRIMARY KEY AUTOINCREMENT), `_data`(TEXT UNIQUE, 전체 경로), `_display_name`, relative_path, volume_name, bucket_id, bucket_display_name, parent, primary_directory, secondary_directory |
| 크기·종류 | `_size`, mime_type, media_type, format, width, height, orientation, duration, resolution |
| 시각 | date_added, date_modified, datetaken, date_expires, inferred_date, inferred_media_date |
| 위치 | latitude(DOUBLE), longitude(DOUBLE) |
| 출처·소유 | owner_package_name, is_download, download_uri, referer_uri |
| 상태 | is_pending, is_trashed, is_favorite, is_drm, is_recording |
| 동기화 번호 | generation_added, generation_modified |
| 기타 | `_hash`(BLOB), xmp(BLOB), document_id, instance_id, original_document_id, `_modifier`, `_user_id`, `_special_format`, `_transcode_status`, `_video_codec_type`, redacted_uri_id, oem_metadata(BLOB), 카메라 값(exposure_time, f_number, iso, scene_capture_type), 오디오 값(artist, album, genre 등) |

위 칸은 모두 현행 AOSP 기준입니다 [1]. 이 가운데 해석에 자주 쓰는 칸의 뜻은 다음과 같습니다.

**경로와 폴더.** `_data` 는 파일의 전체 경로이고 한 DB 안에서 겹치지 않습니다. bucket_id 는 부모 폴더 경로를 소문자로 바꾼 문자열의 hashCode() 값이고, bucket_display_name 은 부모 폴더 이름이며 최상위 폴더에 있는 파일이면 NULL 입니다 [5]. is_download 는 경로가 `/storage/<볼륨>/(<사용자ID>/)Download/` 아래일 때 1 로 채우는 업그레이드 단계가 있습니다(정규식 PATTERN_DOWNLOADS_FILE) [1][5]. `/sdcard/DCIM` 아래의 Camera, Screenshots 같은 폴더 이름이 relative_path 와 bucket_display_name 에 그대로 나타납니다. 공용 저장 공간의 폴더 구성은 [공용 저장 공간](../../../01-foundations/storage/shared-storage.md) 페이지에 있습니다.

**소유 앱.** owner_package_name 은 이 미디어를 넣은 패키지 이름이고, 소유를 확실히 알 수 없으면 NULL 일 수 있습니다. Android 14(UPSIDE_DOWN_CAKE)부터는 앱이 이 칸을 조회할 때 패키지 가시성에 따라 결과가 제한됩니다 [2]. 그래서 앱을 거쳐 조회한 결과와 DB 파일을 직접 읽은 결과가 다를 수 있습니다. 패키지 이름을 앱과 맞추는 법은 [패키지 이름과 UID](../../../01-foundations/value-decoding/package-uid.md) 페이지에 있습니다.

**대기 상태.** is_pending 은 소유 앱이 아직 파일을 쓰는 중인 항목이고, 이 표시가 있는 동안에는 소유 앱만 파일을 열 수 있습니다. 앱이 0 으로 바꾸거나 date_expires 가 지나면 대기가 끝나며, 대기 항목의 date_expires 기본값은 7일 뒤입니다 [2]. is_trashed 와 휴지통 쪽 date_expires 는 [지운 사진의 흔적](deleted-media.md) 페이지에서 다룹니다.

**바꾼 작업의 종류.** `_modifier` 는 숨김 칸이고, 행을 마지막으로 바꾼 작업의 종류를 숫자로 적습니다 [2].

| 값 | 이름 | 뜻 |
|---|---|---|
| 1 | FUSE | 파일을 직접 조작함 |
| 2 | CR | 앱이 ContentResolver 로 호출함 |
| 3 | MEDIA_SCAN | 미디어 스캔 |
| 4 | CR_PENDING_METADATA | (소스 상수 이름) |
| 5 | SCHEMA_UPDATE | 스키마 업데이트 |

어느 패키지가 바꿨는지는 이 칸으로 알 수 없습니다 [2]. 스키마 업그레이드로 이 칸이 처음 생길 때 기존 행은 모두 3(MEDIA_SCAN)으로 채우기 때문에 [1], 오래된 행의 3 은 실제 미디어 스캔이 아니었을 수 있습니다.

**문서 ID.** document_id 는 XMP Media Management 표준의 문서 ID(GUID)이고, 파일에 XMP 메타데이터가 없으면 null 입니다 [2].

### 그 밖의 표

**log 표.** 칸은 time(DATETIME), message(TEXT) 이고 현행 스키마에서도 만들어집니다. 다만 스키마 버전 1106 으로 올리는 단계(updateMigrateLogs)가 기존 log 표 내용을 새 기록 방식(Logging.logPersistent, "Historical log ..." 형태)으로 옮기고 표를 비웁니다 [1].

**media_grants 표(외부 볼륨).** 칸은 owner_package_name, file_id, package_user_id, generation_granted 이고, file_id 는 files(`_id`)를 참조해서 파일 행이 지워지면 이 표의 행도 같이 지워집니다(ON DELETE CASCADE) [1]. 이 표가 정확히 무엇을 기록하는지(예: 사진 선택기로 앱에 준 접근 허가인지)는 소스 주석에 설명이 없어, 검체의 다른 기록과 맞춰 보고 해석합니다.

**deleted_media 표.** 지워지거나 안 보이게 된 이미지·동영상의 옛 번호를 모으는 표이고, [지운 사진의 흔적](deleted-media.md) 페이지에서 다룹니다.

### 삼성 media.db

ALEAPP 가 삼성 media.db 의 files 표에서 읽는 칸은 datetaken, date_added, date_modified, `_display_name`, `_data`, mime_type, `_size`, latitude, longitude, addr, bucket_display_name, owner_package_name, captured_url, captured_app, is_favorite, is_hide, is_trashed, deleted 이고, addr 는 여러 부분을 `|` 로 이어 붙인 문자열입니다 [3]. location 표에서는 latitude, longitude, address_text, country_name, country_code, admin_area, sub_admin_area, locality, sub_locality, street_name, street_number, postal_code 를 읽습니다 [3].

ALEAPP 시험 검체 10개에서는 is_hide 와 deleted 가 모든 행에서 비어 있었고 is_favorite·is_trashed 는 0 이거나 비어 있어서, 다른 값이 무엇을 뜻하는지는 알려져 있지 않습니다 [3]. 이 DB 의 칸 뜻과 시각 단위는 삼성이 공개한 문서가 없으니, captured_app 같은 칸을 해석할 때는 같은 파일의 AOSP external.db 행과 나란히 놓고 봅니다.

## 시각 해석

files 표에는 초 단위 칸과 밀리초 단위 칸이 섞여 있습니다 [2]. 모두 유닉스 시각이라 UTC 기준이지만, datetaken 은 원래 값을 어디서 가져왔는지에 따라 믿을 수 있는 정도가 다릅니다.

| 칸 | 단위 | 무엇이 바뀔 때 바뀌나 |
|---|---|---|
| date_added | 유닉스 초 | 미디어 항목이 처음 추가된 시각 |
| date_modified | 유닉스 초 | 파일의 File#lastModified() 를 색인한 값 |
| datetaken | 유닉스 밀리초 | MediaMetadataRetriever 의 METADATA_KEY_DATE 나 EXIF 의 TAG_DATETIME_ORIGINAL 에서 뽑은 값 |
| date_expires | 유닉스 초 | is_pending 이나 is_trashed 가 바뀔 때 자동으로 계산 |
| inferred_date | 공개 자료 없음 | datetaken 이 있으면 그 값, 없으면 date_modified |

이미지의 datetaken 은 EXIF 의 TAG_DATETIME_ORIGINAL 과 TAG_OFFSET_TIME_ORIGINAL 이 둘 다 있어야 에포크 기준 시각을 믿을 수 있습니다 [2]. 시차 칸이 없는 사진이라면 datetaken 을 UTC 로 단정하지 말고 원본 파일의 EXIF 를 [카메라 사진과 메타데이터](../dcim-exif.md) 페이지 방법으로 다시 읽습니다. inferred_date 는 기능 플래그(FLAG_INFERRED_MEDIA_DATE)가 붙은 칸이고, 예전 칸 inferred_media_date 는 더는 쓰지 않습니다 [1][2].

단위가 섞인 탓에 칸 두 개를 한 번에 날짜로 바꾸면 한쪽이 1970년 근처나 먼 미래로 나오는 일이 생깁니다. 사진 선택기 쪽 쿼리도 date_modified 에 1000 을 곱해 밀리초로 맞춥니다 [4]. 시각 값 변환 일반은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

generation_added 와 generation_modified 는 시각이 아니라 세대 번호입니다. 항목이 추가되거나 바뀔 때 local_metadata 표의 generation 값을 적고, 이 값은 쓰기 트랜잭션을 시작할 때마다 1씩 오릅니다 [1][2]. 앱이 File#setLastModified() 를 부르거나 시스템 시계가 틀리면 날짜 값이 예상과 다르게 바뀔 수 있어서, 추가·변경을 감지하는 데는 generation 번호가 date_added·date_modified 보다 믿을 만합니다 [2]. 그래서 날짜 칸끼리 순서가 어긋나 보이면 generation 번호로 행이 바뀐 순서를 다시 맞춰 봅니다. 다만 MediaStore 버전(getVersion)이 바뀌면 generation 번호가 초기화된 것으로 보고 처음부터 다시 맞춰야 하니 [2], 번호 비교는 같은 DB 세대 안에서만 합니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 색인할 때 그 경로에 그 이름·크기·종류의 파일이 있었다는 것 | 지금도 파일이 그 경로에 같은 내용으로 있다는 것 |
| owner_package_name 이 비어 있지 않으면 그 패키지가 항목을 넣었다는 것 | 사진을 누가 찍었는지, 어느 앱이 나중에 파일을 고쳤는지 |
| `_modifier` 로 본 마지막 변경 작업의 종류(직접 조작·ContentResolver·스캔) | 마지막 변경을 한 패키지 |
| generation 번호로 본 행 추가·변경의 상대 순서 | generation 번호만으로 본 절대 시각 |
| datetaken 이 뽑아 온 원본 메타데이터 값 | 원본 메타데이터 자체가 사실이라는 것 |

보고서에는 "이 사진을 찍었다" 가 아니라 "MediaStore 색인에 이 경로의 이미지가 date_added 기준 이 시각에 추가됐고, 넣은 패키지는 이 이름으로 기록돼 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 함정과 한계

- external.db 의 기기 안 경로와 메인라인 모듈로 나뉜 버전은 공개 자료로 정해지지 않았습니다. 도구가 보여 주는 경로와 버전을 그대로 옮기지 말고 검체에서 확인합니다.
- 보기(images, video 등)는 조건에 맞는 행만 보여 주고 음악 관련 보기는 휴지통·대기 항목까지 빼서, 개수를 셀 때는 files 표를 기준으로 삼습니다.
- `_modifier` 칸이 생기기 전부터 있던 행은 모두 3 으로 채워졌습니다 [1].
- 삼성 media.db 칸의 뜻은 공개 문서가 없고, ALEAPP 검체에서도 is_hide·deleted 가 비어 있었습니다 [3].
- 지운 행이 SQLite 빈 페이지에 남는지는 공개 자료가 없어 검체에서 확인합니다. SQLite 에서 지운 레코드를 찾는 일반 방법은 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md)와 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 페이지를 봅니다.

## 직접 분석해 보기

확보한 external.db 사본을 SQLite 를 읽는 공개 도구(예: sqlite3 명령줄)로 엽니다. 원본이 아니라 사본에서 작업하고, DB 파일에 딸린 파일(저널 등)까지 함께 다루는 법은 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md) 페이지를 따릅니다. 아래 쿼리는 이 페이지의 칸 이름으로 만든 예시입니다.

```sql
-- 초 단위와 밀리초 단위를 각각 맞춰 UTC 로 바꾼다
SELECT _id, _data, media_type, owner_package_name, _modifier,
       datetime(date_added, 'unixepoch')          AS added_utc,
       datetime(date_modified, 'unixepoch')       AS modified_utc,
       datetime(datetaken / 1000, 'unixepoch')    AS taken_utc,
       generation_added, generation_modified,
       is_pending, is_trashed
FROM files
ORDER BY generation_modified;
```

`ORDER BY generation_modified` 로 정렬해 날짜 칸의 순서와 비교하면, 시계가 바뀌었거나 파일 수정 시각을 따로 바꾼 행이 드러날 수 있습니다. 삼성 기기라면 같은 `_data` 로 삼성 media.db 의 files 표를 찾아 captured_app·addr 칸을 옆에 놓습니다. 공개 도구로는 ALEAPP 에 삼성 media.db 를 읽는 모듈(samsungMediaProvider)이 있어서 [3], 직접 뽑은 값과 도구 결과를 맞춰 보는 데 씁니다.

## 교차 검증

- [카메라 사진과 메타데이터](../dcim-exif.md) — datetaken 과 위치 칸의 원본인 EXIF 를 파일에서 직접 읽습니다.
- [섬네일 캐시](../thumbnails.md) — 원본 파일이 없어진 뒤에도 남을 수 있는 작은 사본입니다.
- [삼성 갤러리](../samsung-gallery.md), [구글 포토](../google-photos.md) — 같은 사진을 앱 쪽에서 따로 기록합니다.
- [스크린샷과 화면 녹화](../screenshots.md) — Screenshots 폴더 행을 해석할 때 봅니다.
- [앱 사용 기록](../../app-usage/usagestats/index.md) — owner_package_name 의 앱이 그 시각에 앞에 떠 있었는지 봅니다.

## 실습

공개 검체(NIST CFReDS 등)에서 Android 이미지를 구할 수 있으면 external.db 를 찾아 다음을 풀어 봅니다.

1. files 표의 행 수와 images·video 보기의 행 수를 비교하고, 차이가 나는 행의 media_type·is_pending·is_trashed 값을 확인합니다.
2. datetaken 이 비어 있는 이미지와 date_modified 가 date_added 보다 이른 행을 찾아, 원본 파일의 EXIF 와 비교합니다.
3. 위 스키마 표의 칸(`_modifier`, `_user_id`, oem_metadata 등)이 있는지로 이 DB 가 어느 단계 이후의 스키마인지 짐작해 봅니다.
4. owner_package_name 이 NULL 인 행의 경로를 모아 어떤 폴더에 몰려 있는지 봅니다.

## 참고 문헌

1. AOSP MediaProvider — DatabaseHelper.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/DatabaseHelper.java
2. AOSP MediaProvider — apex/framework/java/android/provider/MediaStore.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/apex/framework/java/android/provider/MediaStore.java
3. ALEAPP (커밋 c044fe5) — scripts/artifacts/samsungMediaProvider.py, https://github.com/abrignoni/ALEAPP/tree/main/scripts/artifacts
4. AOSP MediaProvider — photopicker/data/ExternalDbFacade.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/photopicker/data/ExternalDbFacade.java
5. AOSP MediaProvider — util/FileUtils.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/util/FileUtils.java
6. AOSP MediaProvider — MediaProvider.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/MediaProvider.java
