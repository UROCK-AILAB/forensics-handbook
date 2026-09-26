---
title: "섬네일 캐시"
parent: "아티팩트 · 사진·미디어"
nav_order: 660
---

# 섬네일 캐시 (Thumbnails)

## 한 줄 요약

미디어 제공자(MediaProvider)는 앱이 요청할 때 사진·동영상·오디오의 작은 사본(섬네일)을 만들어 공용 저장 공간의 `.thumbnails` 폴더에 MediaStore 번호(`_id`)를 이름으로 저장하고, 앱들도 따로 이미지 캐시를 두기 때문에, 원본을 지운 뒤에도 한동안 사진의 모습이 남을 수 있습니다 [1][4].

## 무엇을 기록하나 · 왜 생기나

앱이 미디어의 섬네일을 요청하면 MediaProvider 가 섬네일 파일을 처음 만들고, 이미 파일이 있으면 그대로 엽니다(ensureThumbnail) [1]. 예전 섬네일 API 인 MediaStore.Images.Thumbnails 등은 폐기됐고, 지금은 ContentResolver#loadThumbnail() 을 씁니다 [2][3]. 섬네일을 미리 만들지 않고 요청이 올 때 만드는 구조라서, 섬네일 파일이 있다는 것은 어떤 앱이 그 항목의 섬네일을 한 번 이상 요청했다는 뜻으로 볼 수 있습니다.

이와 별도로 많은 앱이 이미지 라이브러리의 디스크 캐시에 화면에 띄운 이미지를 저장합니다. 널리 쓰이는 이미지 라이브러리 Glide 의 기본 디스크 캐시 폴더는 앱 cache 아래 image_manager_disk_cache 이고, 공개 도구 ALEAPP 는 이 폴더의 파일을 이미지 캐시로 모읍니다 [4]. 시스템 섬네일과 앱 캐시는 만드는 주체와 지우는 규칙이 달라서 따로 봅니다.

## 위치와 버전별 차이

| 종류 | 위치 | 범위 |
|---|---|---|
| 이미지 섬네일 | 기본 외부 볼륨의 `Pictures/.thumbnails/` | 현행 AOSP 기준 [1] |
| 동영상 섬네일 | 기본 외부 볼륨의 `Movies/.thumbnails/` | 현행 AOSP 기준 [1] |
| 오디오 섬네일 | 기본 외부 볼륨의 `Music/.thumbnails/` | 현행 AOSP 기준 [1] |
| 예전 섬네일 표 | external.db 의 thumbnails(image_id), videothumbnails(video_id) | 현행 AOSP 가 원본 없는 행을 정리 [1] |
| 앱 이미지 캐시(Glide) | `*/cache/image_manager_disk_cache/*.*`, `*/*.cnt` | ALEAPP 의 경로 패턴 [4] |
| 구글 포토 캐시 | [구글 포토](google-photos.md) 페이지 참고 | ALEAPP 시험 이미지 |

MediaProvider 는 섬네일을 항상 기본 외부 저장소(external_primary)에 저장하므로 [1], SD 카드 같은 다른 볼륨의 사진이라도 섬네일은 기본 볼륨 쪽에 생깁니다. 예전 방식의 `/sdcard/DCIM/.thumbnails` 폴더가 어느 버전까지 쓰였는지, 섬네일 폴더가 어느 버전부터 `Pictures/.thumbnails` 로 바뀌었는지는 실제 기기에서 확인합니다.

삼성 기기의 dumpsys package 라이브러리 목록에는 `SemAudioThumbnail` (`/system/framework/SemAudioThumbnail.jar`)이 있는데, 이름으로 보면 삼성의 오디오 섬네일 라이브러리로 짐작됩니다. 삼성 갤러리의 자체 섬네일 캐시 경로와 형식은 실제 기기로 확인해야 합니다.

## 구조

### 파일 이름과 형식

현행 MediaProvider 는 섬네일을 다음 경로에 저장합니다 [1].

```text
<기본 외부 볼륨>/<폴더>/.thumbnails/<MediaStore _id>.jpg
  폴더: 이미지 = Pictures, 동영상 = Movies, 오디오 = Music
  예) /sdcard/Pictures/.thumbnails/<_id>.jpg
```

파일 이름의 숫자는 ContentUris.parseId(uri) 로 얻은 MediaStore files 표의 `_id` 라서 [1], 섬네일 파일을 external.db 의 같은 `_id` 행과 짝지을 수 있습니다. 섬네일은 JPEG 품질 90 으로 저장하고, 먼저 "thumb" 로 시작하는 임시 파일에 쓴 뒤 최종 이름으로 바꿉니다 [1]. 크기는 화면 짧은 변 픽셀 수의 절반을 한 변으로 하는 정사각 범위 안에 맞춥니다(mThumbSize) [1].

예전 API 의 섬네일 종류 상수(@hide)는 MINI_KIND 512×384, FULL_SCREEN_KIND 1024×786, MICRO_KIND 96×96 이고 [2], 오래된 기기나 앱 코드에서 이 크기를 만날 수 있습니다.

### `.database_uuid` 파일과 지우는 규칙

각 `.thumbnails` 폴더에는 `.database_uuid` 파일이 있고, MediaProvider DB 의 UUID 를 적어 둡니다. 디스크에 적힌 값과 DB 의 값이 다르면 그 폴더의 섬네일을 모두 지웁니다(ensureThumbnailsValid) [1]. 섬네일이 사라지는 경우는 다음 셋입니다 [1].

| 계기 | 동작 |
|---|---|
| 원본 행을 지우거나(files_delete) 종류가 바뀔 때 | invalidateThumbnails() 가 Music·Movies·Pictures 세 폴더에서 같은 `_id` 섬네일을 지움 |
| 유휴 유지보수(pruneThumbnails) | files 표에 없는 `_id` 이름의 섬네일 파일을 지움(`.database_uuid` 와 `.nomedia` 계열 파일은 남김) |
| DB UUID 가 바뀔 때 | 그 폴더의 섬네일을 모두 지움 |

같은 유지보수에서 예전 표 thumbnails·videothumbnails 가운데 원본이 없는 행도 지웁니다 [1]. 소스로 보면 원본 행이 지워진 뒤 다음 유지보수가 돌기 전까지는 섬네일 파일이 남아 있을 수 있고, 이 틈이 섬네일을 찾는 이유입니다.

### 앱 이미지 캐시

ALEAPP 는 `*/cache/image_manager_disk_cache/*.*` 와 `*/*.cnt` 파일을 이미지 캐시로 모으고, 시각으로는 파일 시스템의 마지막 수정 시각(mtime)만 씁니다 [4]. ALEAPP 가 공개한 시험 이미지 10개(Android 10~16)에서 이 모듈은 458~19,294 행을 냈습니다 [4]. 앱 데이터 폴더의 위치는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 페이지에 있습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| `_id` 이름의 섬네일이 있으면 그 번호의 미디어 행이 있었다는 것 | 원본 파일의 정확한 내용(섬네일은 작게 줄인 JPEG) |
| 섬네일 이미지가 보여 주는 장면 | 사용자가 그 사진을 직접 봤다는 것(요청한 앱이 누구인지 남지 않음) |
| files 표에 없는 `_id` 섬네일이 남아 있으면 원본 행이 지워졌을 가능성 | 언제 지웠는지 |
| 앱 캐시에 이미지가 있으면 그 앱이 그 이미지를 받아 저장한 적이 있다는 것 | 화면에 실제로 띄웠다는 것 |

"사용자가 이 사진을 봤다" 보다 "`Pictures/.thumbnails` 에 이 `_id` 의 섬네일이 있고, files 표에는 같은 번호가 없다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

섬네일 파일 안에는 시각 값이 없고, 파일 시스템의 시각만 남습니다. 임시 파일에 쓴 뒤 이름을 바꾸는 방식이라 [1], 섬네일 파일의 수정 시각은 섬네일을 만든 무렵으로 볼 수 있지만 원본의 촬영 시각과는 관계가 없습니다. 원본 시각은 같은 `_id` 의 files 행과 원본 EXIF 에서 읽고, ext4·F2FS 의 시각 필드는 [파일 시스템 (ext4·F2FS)](../../01-foundations/storage/filesystems/index.md) 페이지를 봅니다. 앱 이미지 캐시도 ALEAPP 는 mtime 만 보여 주니 [4], 그 시각은 캐시 파일을 쓴 시각이지 이미지를 찍은 시각이 아닙니다.

## 함정과 한계

- DB UUID 가 바뀌면 폴더 전체가 지워지고 유휴 유지보수가 원본 없는 섬네일을 정리해서 [1], 섬네일이 없다고 원본이 없었다고 말할 수 없습니다.
- 섬네일 파일 이름은 `_id` 뿐이라 원본 경로·이름은 external.db 가 있어야 알 수 있습니다. DB 에서 행이 지워졌다면 [지운 사진의 흔적](mediastore/deleted-media.md) 페이지의 방법으로 옛 번호를 찾습니다.
- 섬네일은 요청이 있을 때만 생기므로 [1], 모든 사진에 섬네일이 있지는 않습니다.
- ALEAPP 가 모으는 image_manager_disk_cache 는 Glide 의 기본 폴더 이름이라서 [4], 다른 라이브러리를 쓰거나 다른 폴더를 쓰는 앱의 캐시는 이 패턴에 걸리지 않을 수 있습니다.

## 직접 분석해 보기

**섬네일과 DB 짝짓기.** 확보한 공용 저장 공간에서 세 `.thumbnails` 폴더의 파일 목록을 뽑고, 이름의 숫자를 external.db 의 `_id` 와 맞춥니다. 아래는 섬네일 번호를 임시 표(thumbs)에 넣었다고 가정하고 쓴 예시 쿼리입니다.

```sql
-- 섬네일은 있는데 files 표에 없는 번호
SELECT t.id FROM thumbs t
WHERE NOT EXISTS (SELECT 1 FROM files f WHERE f._id = t.id);

-- 섬네일과 원본 행을 나란히 보기
SELECT t.id, f._data, f.is_trashed,
       datetime(f.datetaken / 1000, 'unixepoch') AS taken_utc
FROM thumbs t JOIN files f ON f._id = t.id;
```

첫 쿼리에 나온 번호는 원본 행이 지워졌을 가능성이 있는 항목이고, deleted_media 표의 옛 번호와도 맞춰 봅니다. `.database_uuid` 의 내용이 현재 DB 와 같은지도 함께 적어 두면, 섬네일이 한꺼번에 지워진 적이 있는지 판단할 때 씁니다.

**공개 도구.** ALEAPP 의 이미지 캐시 모듈(imagemngCache)은 앱의 Glide 캐시 파일을 모아 mtime 과 함께 보여 줍니다 [4]. 도구 결과에서 관심 이미지를 찾은 뒤, 그 파일이 어느 앱 폴더 아래에 있는지로 캐시를 남긴 앱을 구분합니다.

## 교차 검증

- [미디어 저장소 (MediaStore)](mediastore/index.md) — `_id` 로 원본 경로·넣은 앱·휴지통 상태를 찾습니다.
- [카메라 사진과 메타데이터 (DCIM·EXIF)](dcim-exif.md) — 원본이 남아 있으면 촬영 시각과 위치를 봅니다.
- [구글 포토 (Google Photos)](google-photos.md), [삼성 갤러리 (Samsung Gallery)](samsung-gallery.md) — 갤러리 앱의 캐시와 휴지통을 봅니다.
- [최근 앱 화면 (Recents·Snapshots)](../app-usage/recents-snapshots.md) — 앱 화면을 찍어 둔 다른 종류의 작은 이미지입니다.
- [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md), [지운 대화와 사진 찾기 (Deleted Content)](../../04-scenarios/activity/deleted-content.md) — 이 기록을 쓰는 기법과 시나리오입니다.

## 실습

공개 시험 이미지(NIST CFReDS 등)에서 Android 이미지를 구할 수 있으면 다음을 풀어 봅니다.

1. `Pictures/.thumbnails`, `Movies/.thumbnails`, `Music/.thumbnails` 가 있는지, 파일 이름이 모두 숫자.jpg 형식인지 확인합니다.
2. 섬네일 번호 가운데 external.db files 표에 없는 번호를 찾고, 그 섬네일이 보여 주는 장면을 기록합니다.
3. `.database_uuid` 파일의 값을 적고, 섬네일 파일의 수정 시각 분포가 원본 촬영 시각 분포와 어떻게 다른지 봅니다.
4. 앱 cache 아래 image_manager_disk_cache 폴더를 찾아 어느 앱들이 이미지 캐시를 남겼는지 정리합니다.

## 참고 문헌

1. AOSP MediaProvider — src/com/android/providers/media/MediaProvider.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/MediaProvider.java
2. AOSP MediaProvider — apex/framework/java/android/provider/MediaStore.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/apex/framework/java/android/provider/MediaStore.java
3. Android Developers — Access media files from shared storage, https://developer.android.com/training/data-storage/shared/media
4. ALEAPP — scripts/artifacts/imagemngCache.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/imagemngCache.py
