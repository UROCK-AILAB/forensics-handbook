---
title: "카메라 사진과 메타데이터"
parent: "아티팩트 · 사진·미디어"
nav_order: 650
---

# 카메라 사진과 메타데이터 (DCIM·EXIF)

## 한 줄 요약

카메라로 찍은 사진은 공용 저장 공간의 DCIM 같은 미디어 폴더에 파일로 남고, 시스템의 미디어 저장소(MediaStore)가 파일 속 EXIF 에서 촬영 시각·방향·카메라 설정 일부를 뽑아 색인하지만 위치는 색인하지 않아서, 촬영 위치와 시차는 원본 파일의 EXIF 를 직접 읽어 확인합니다 [1][3].

## 무엇을 기록하나 · 왜 생기나

시스템은 외부 저장소를 훑어 미디어 파일을 모음(collection)에 넣습니다. 사진이나 스크린샷 같은 이미지는 DCIM/ 과 Pictures/ 에서 MediaStore.Images 모음으로 들어가고, 동영상은 DCIM/·Movies/·Pictures/ 에서 MediaStore.Video 모음으로 들어갑니다 [3]. 이때 MediaProvider 가 파일의 EXIF 에서 촬영 시각(DateTimeOriginal), 방향(Orientation), 노출 시간·조리개·ISO 같은 값을 읽어 files 표의 칸으로 옮기기 때문에 [1], 같은 사진의 정보가 파일 속 EXIF 와 DB 의 칸 두 곳에 남습니다. 두 곳은 담는 범위와 단위가 다르고, 특히 위치는 DB 쪽에 남지 않습니다.

카메라 앱이 어떤 하위 폴더와 파일 이름을 쓰는지는 AOSP 가 정한 규칙이 아니라 카메라 앱마다 다릅니다. 삼성 카메라의 파일 이름 규칙은 이번에 확인하지 못했습니다. files 표의 전체 칸과 표 구조는 [미디어 DB 구조 (external.db)](mediastore/external-db.md) 페이지에 있고, 이 페이지는 EXIF 와 그 칸 사이의 관계를 다룹니다.

## 위치와 버전별 차이

| 항목 | 내용 | 범위 |
|---|---|---|
| 앱이 MediaStore 로 이미지를 넣을 수 있는 최상위 폴더 | DCIM, Pictures (기본값 Pictures) | 현행 AOSP 기준 [2] |
| 앱이 MediaStore 로 동영상을 넣을 수 있는 최상위 폴더 | DCIM, Movies, Pictures (기본값 Movies) | 현행 AOSP 기준 [2] |
| EXIF 위치를 가리지 않고 읽는 조건 | ACCESS_MEDIA_LOCATION 권한 선언과 실행 중 요청(사용자 동의) | Android 10(API 29) 이상을 대상으로 하는 앱 [3] |
| MediaStore 의 latitude·longitude 칸 | 문서상 폐기(deprecated), 항상 NULL | 현행 AOSP 기준 [1][2], 바뀐 버전은 확인 못 함 |
| `/sdcard/DCIM` 아래 | Camera, Screenshots, media 와 가린 폴더 19개(항목 25개) | (확인 범위: SM-S937N, Android 16, One UI 8.5) |

관찰한 기기의 `/sdcard` 최상위에는 DCIM, Pictures, Movies, Recordings 같은 표준 폴더와 가린 폴더 8개가 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). DCIM 아래의 Screenshots 폴더는 AOSP 의 스크린샷 기본 위치와 달라서 [스크린샷과 화면 녹화](screenshots.md) 페이지에서 따로 다루고, DCIM/media 폴더가 무엇을 담는지는 확인하지 못했습니다. 공용 저장 공간의 폴더 구성은 [공용 저장 공간 (Shared Storage·/sdcard)](../../01-foundations/storage/shared-storage.md) 페이지에 있습니다.

## 구조

### EXIF 태그와 MediaStore 칸

MediaStore 문서가 적는 칸과 원본의 관계는 다음과 같습니다 [1].

| MediaStore 칸 | 가져오는 원본 | 단위 |
|---|---|---|
| datetaken | MediaMetadataRetriever 의 METADATA_KEY_DATE 또는 EXIF 의 TAG_DATETIME_ORIGINAL | 유닉스 밀리초 |
| orientation | EXIF 의 TAG_ORIENTATION (동영상은 회전 메타데이터) | 0·90·180·270 도 |
| exposure_time | TAG_EXPOSURE_TIME | EXIF 값 |
| f_number | TAG_F_NUMBER | EXIF 값 |
| iso | TAG_ISO_SPEED_RATINGS | EXIF 값 |
| scene_capture_type | TAG_SCENE_CAPTURE_TYPE | EXIF 값 |
| xmp | XMP 메타데이터 | 원본 그대로 |
| latitude·longitude | 색인하지 않음 | 항상 NULL |

date_added 와 date_modified 는 EXIF 에서 오지 않습니다. date_added 는 항목이 처음 추가된 시각이고 읽기 전용 칸이며 [1], MediaProvider 의 insertFile() 은 앱이 넣은 값과 상관없이 이 칸을 그 순간의 유닉스 초로 다시 씁니다 [2]. date_modified 는 파일의 File#lastModified() 값을 초 단위로 색인한 것입니다 [1].

### 위치 정보와 가림

MediaStore 문서는 latitude·longitude 칸에 대해 "location details are no longer indexed for privacy reasons, and this value is now always null" 라고 적고, 위치가 필요하면 ExifInterface#getLatLong() 으로 파일에서 직접 읽으라고 안내합니다 [1]. MediaProvider 도 자기 자신이 아닌 앱이 두 칸에 값을 넣으려 하면 NULL 로 바꿉니다 [2]. 현행 소스에는 사진 선택기 검색용으로 두 칸을 다시 채우는 기능 플래그(indexMediaLatitudeLongitude)가 있지만, 이 플래그가 켜져 있어도 MediaProvider 가 아닌 호출자가 조회하면 NULL 을 돌려줍니다 [2]. 이 플래그가 어느 버전과 기기에서 켜져 있는지는 확인하지 못했습니다. 삼성 기기에는 AOSP 와 별도로 삼성 미디어 제공자의 media.db 에 위도·경도 칸이 있는데, 그 내용은 [미디어 DB 구조 (external.db)](mediastore/external-db.md) 페이지에 있습니다.

파일을 열어 줄 때도 위치를 가립니다. 범위 저장소(scoped storage)를 쓰는 앱이 사진을 열면 시스템이 위치 정보를 기본으로 가리고, 원본 바이트를 받으려면 앱이 ACCESS_MEDIA_LOCATION 권한을 얻은 뒤 MediaStore.setRequireOriginal() 로 바꾼 URI 를 열어야 합니다 [3]. MediaProvider 는 가림이 필요한 호출자에게 RedactionUtils.getRedactionRanges() 로 구한 바이트 구간을 가려서 넘기고, 권한 없이 원본을 요구하면 "Caller must hold ACCESS_MEDIA_LOCATION permission to access original" 예외를 냅니다 [2]. 앱 권한의 일반 구조는 [앱 샌드박스와 권한](../../01-foundations/security-model/sandbox-permissions.md) 페이지에 있습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 파일 속 EXIF 에 촬영 시각·시차·위치 값이 적혀 있다는 것 | 그 값이 사실이라는 것(EXIF 는 파일 안의 값이라 고칠 수 있음) |
| datetaken 이 EXIF 나 동영상 메타데이터에서 뽑은 값이라는 것 | 이 기기로 찍었다는 것 |
| date_added 가 이 DB 에 항목이 처음 들어간 시각이라는 것 | 촬영 시각 |
| DCIM 아래 폴더에 파일이 있다는 것 | 어느 카메라 앱이 만들었는지(폴더 이름 규칙은 앱마다 다름) |
| latitude·longitude 가 NULL 이라는 것 | 사진에 위치가 없다는 것 |

"이 사진을 이곳에서 찍었다" 보다 "이 파일의 EXIF 에 이 위도·경도와 이 촬영 시각이 적혀 있고, MediaStore 에는 이 시각에 처음 색인됐다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

| 값 | 기준 | 무엇이 바뀔 때 바뀌나 |
|---|---|---|
| EXIF DateTimeOriginal | 현지 시각 문자열(시간대 없음) | 촬영할 때 카메라 앱이 적음 |
| EXIF OffsetTimeOriginal | 시차 문자열(예 +09:00) | 촬영할 때 함께 적음 |
| datetaken | 유닉스 밀리초(UTC) | 색인할 때 EXIF 나 동영상 메타데이터에서 뽑음 [1] |
| date_added | 유닉스 초(UTC) | 항목이 DB 에 처음 들어갈 때 [1][2] |
| date_modified | 유닉스 초(UTC) | 파일의 마지막 수정 시각을 다시 색인할 때 [1] |

MediaStore 문서 주석은 이미지의 TAG_DATETIME_ORIGINAL 과 TAG_OFFSET_TIME_ORIGINAL 이 둘 다 있어야 에포크 기준 시각을 믿을 수 있다고 적습니다 [1]. DateTimeOriginal 은 시간대 없는 현지 시각이라서, 시차 태그가 없는 사진이면 datetaken 의 UTC 환산이 틀릴 수 있다는 뜻으로 읽힙니다. 이런 사진은 datetaken 을 UTC 로 단정하지 말고, 기기 시간대 설정과 함께 원본 EXIF 를 다시 봅니다. 시각 값 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md), 기기 시간대 기록은 [시간대와 시각 설정](../system-account/time-zone.md) 페이지에 있습니다.

date_added 가 촬영 시각보다 한참 늦으면 파일이 나중에 복사되거나 옮겨져 새로 색인됐을 수 있고, 반대로 두 값이 거의 같으면 찍은 뒤 곧바로 저장되고 색인된 사진일 가능성이 큽니다. 어느 쪽이든 추정이라서 다른 기록과 맞춰 봐야 합니다.

## 함정과 한계

- 공유하거나 MediaStore 를 거쳐 복사한 사진은 위치가 가려진 사본일 수 있어서 [2][3], 파일 시스템에서 직접 얻은 원본과 EXIF 가 다를 수 있습니다. 실제 사례로 확인한 자료는 이번에 열지 않았습니다.
- latitude·longitude 가 비어 있다고 위치 정보가 없다고 판단하면 안 됩니다. 현행 AOSP 는 이 칸을 채우지 않습니다 [1][2].
- 라이브 기기에서 앱을 통해 받은 파일은 가림 처리를 거쳤을 수 있으니, 위치를 볼 때는 파일 시스템 수준으로 확보한 원본을 씁니다. 확보 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지에 있습니다.
- EXIF 태그 전체 목록(Make, Model, GPS 태그 등)의 공식 설명과 삼성 카메라가 넣는 제조사 전용 값(MakerNote 등)은 이번에 확인하지 못했습니다.

## 직접 분석해 보기

**헥스로 촬영 시각 찾기.** AOSP 의 스크린샷 코드는 DateTimeOriginal 을 `yyyy:MM:dd HH:mm:ss` 꼴로, OffsetTimeOriginal 을 `+09:00` 꼴로 적습니다 [4]. 카메라 앱도 같은 꼴을 쓴다면 헥스 편집기에서 이런 ASCII 문자열을 찾아 촬영 시각과 시차를 눈으로 확인할 수 있습니다. 아래는 이 형식으로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다.

```text
DateTimeOriginal  "2020:12:15 09:06:26"
  32 30 32 30 3A 31 32 3A 31 35 20 30 39 3A 30 36 3A 32 36
OffsetTimeOriginal "+09:00"
  2B 30 39 3A 30 30
해석: 현지 2020-12-15 09:06:26, 시차 +09:00 → UTC 2020-12-15 00:06:26
```

**external.db 와 맞춰 보기.** 확보한 external.db 사본을 SQLite 를 읽는 공개 도구(예: sqlite3 명령줄)로 열어 DCIM 아래 행의 시각 칸을 뽑고, 같은 파일의 EXIF 값과 나란히 놓습니다. 아래 쿼리는 이 페이지의 칸 이름으로 만든 예시입니다.

```sql
SELECT _id, _data,
       datetime(datetaken / 1000, 'unixepoch') AS taken_utc,
       datetime(date_added, 'unixepoch')       AS added_utc,
       datetime(date_modified, 'unixepoch')    AS modified_utc,
       orientation, latitude, longitude
FROM files
WHERE relative_path LIKE 'DCIM/%'
ORDER BY datetaken;
```

taken_utc 와 EXIF 의 현지 시각·시차로 계산한 UTC 가 맞지 않으면 시차 태그가 없거나 파일이 편집됐을 수 있으니 원본 파일을 다시 봅니다. SQLite 를 읽는 방법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에 있습니다.

## 교차 검증

- [미디어 저장소 (MediaStore)](mediastore/index.md) — 같은 파일의 색인 행, 넣은 앱, 휴지통 상태를 봅니다.
- [섬네일 캐시 (Thumbnails)](thumbnails.md) — 원본이 없어진 뒤에도 작은 사본이 남는지 봅니다.
- [구글 포토 (Google Photos)](google-photos.md), [삼성 갤러리 (Samsung Gallery)](samsung-gallery.md) — 앱이 따로 적어 둔 촬영 시각·시차·위치와 비교합니다.
- [배터리 사용 기록 (batterystats)](../app-usage/batterystats.md) — 관찰한 기기의 Battery History 에는 `+camera`·`-camera` 표시가 붙은 줄이 여러 개 있었고, 각 줄 앞에는 월-일 시:분:초.밀리초 꼴의 시각이 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 이 표시가 카메라 사용의 시작과 끝을 뜻하는지는 출처로 확인하지 않았습니다.
- [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) — 촬영 시각 무렵 카메라 앱이 앞에 떠 있었는지 봅니다.
- [설정 값 (Settings)](../system-account/settings.md) — 관찰한 기기의 settings system 에는 camera_feedback_vibrate, csc_pref_camera_forced_shuttersound_key 키가 있었고 (확인 범위: SM-S937N, Android 16, One UI 8.5), 뜻은 확인하지 못했습니다.
- [이 사진은 언제 어디서 찍었나 (Photo Origin)](../../04-scenarios/activity/photo-origin.md) — 이 기록을 쓰는 조사 시나리오입니다.

## 실습

공개 검체(NIST CFReDS 등)에서 Android 이미지를 구할 수 있으면 다음을 풀어 봅니다.

1. DCIM 아래 사진 몇 장의 EXIF 에서 DateTimeOriginal 과 OffsetTimeOriginal 을 읽고, external.db 의 datetaken 을 UTC 로 바꾼 값과 같은지 확인합니다.
2. 시차 태그가 없는 사진을 찾아 datetaken 이 기기 시간대 설정과 어떻게 어긋나는지 봅니다.
3. latitude·longitude 칸이 모두 NULL 인지 확인하고, 같은 사진의 EXIF 에 GPS 값이 있는지 봅니다.
4. date_added 가 datetaken 보다 크게 늦은 행을 골라, 그 파일이 다른 앱에서 받거나 옮긴 파일인지 넣은 앱 칸과 함께 확인합니다.

## 참고 문헌

1. AOSP MediaProvider — apex/framework/java/android/provider/MediaStore.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/apex/framework/java/android/provider/MediaStore.java
2. AOSP MediaProvider — src/com/android/providers/media/MediaProvider.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/MediaProvider.java
3. Android Developers — Access media files from shared storage, https://developer.android.com/training/data-storage/shared/media
4. AOSP frameworks/base — packages/SystemUI/src/com/android/systemui/screenshot/ImageExporter.java (main), https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/packages/SystemUI/src/com/android/systemui/screenshot/ImageExporter.java
