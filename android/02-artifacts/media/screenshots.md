---
title: "스크린샷과 화면 녹화"
parent: "아티팩트 · 사진·미디어"
nav_order: 690
---

# 스크린샷과 화면 녹화 (Screenshots·Screen Recording)

## 한 줄 요약

AOSP 의 시스템 UI(SystemUI)는 스크린샷을 `Pictures/Screenshots` 에 캡처 시각이 든 이름으로 저장하면서 EXIF 에 시차까지 포함한 캡처 시각과 빌드 표시값을 적고, 화면 녹화는 `screen-날짜-시각.mp4` 이름으로 Movies 에 저장하는데, 삼성 기기는 저장 폴더와 설정이 달라서 기기에서 실제 위치를 먼저 확인합니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

스크린샷과 화면 녹화는 사용자가 화면을 저장한 결과물이라서, 파일 이름·EXIF·MediaStore 행 세 곳에 캡처 시각이 남습니다. AOSP 에서는 SystemUI 의 ImageExporter 가 스크린샷을, ScreenMediaRecorder 가 화면 녹화를 저장하고, 둘 다 미디어 저장소(MediaStore)를 거쳐 파일을 넣습니다 [1][2]. 카메라 사진과 달리 이 파일들은 기기 스스로 만든 것이라, 이름 규칙과 EXIF 내용이 코드로 정해져 있습니다.

## 위치와 버전별 차이

| 항목 | AOSP (현행 기준) | 삼성 One UI |
|---|---|---|
| 스크린샷 폴더 | `Pictures/Screenshots` [1] | `/sdcard/DCIM` 아래에 Screenshots 폴더가 있음 |
| 스크린샷 파일 이름 | `Screenshot_연월일-시분초.확장자` [1] | 검체에서 확인 |
| 스크린샷 형식 | PNG 기본, 호출 쪽이 JPEG·WEBP 로 바꿀 수 있음 [1] | 형식 설정 키가 있음(아래) |
| 화면 녹화 폴더 | Movies(동영상 기본 폴더) [2][3] | 검체에서 확인 |
| 화면 녹화 파일 이름 | `screen-yyyyMMdd-HHmmss.mp4` [2] | 검체에서 확인 |

`/sdcard` 최상위의 Recordings/ 는 음성 녹음 폴더이고, Android 11 이하에는 없습니다 [5]. 삼성 기기에서 화면 녹화 파일이 이 폴더에 들어가는지는 검체에서 확인합니다.

삼성 기기의 settings system 에는 스크린샷과 관련된 이름의 다음 키가 있습니다. 각 키의 뜻을 밝힌 삼성 공식 문서는 없습니다.

```text
screenshot_current_save_dir
smart_capture_screenshot_format
save_original_screenshots
delete_shared_screenshots
exclude_systemui_screenshots
enable_smart_capture
```

키 이름으로 보면 사용자가 저장 폴더(screenshot_current_save_dir)와 저장 형식(smart_capture_screenshot_format)을 바꿀 수 있는 것으로 보이지만, 이름에서 짐작한 것일 뿐입니다. 값을 읽을 수 있다면 [설정 값 (Settings)](../system-account/settings.md) 페이지의 방법으로 확인하고, 스크린샷을 찾을 폴더를 정할 때 참고합니다. 삼성 스크린샷 파일 이름 뒤에 앱 이름이 붙는지는 검체에서 확인합니다.

## 구조

### AOSP 스크린샷

파일 이름은 `Screenshot_%1$tY%<tm%<td-%<tH%<tM%<tS.<확장자>` 형식이고, 예를 들면 `Screenshot_20201215-090626.png` 입니다. 연결된 다른 화면을 찍으면 `Screenshot_20201215-090626-display-1.png` 꼴이 됩니다 [1]. 이름 속 시각은 기기 시간대 기준의 캡처 시각(ZonedDateTime)입니다 [1].

저장은 두 단계로 합니다 [1]. 먼저 MediaStore 에 is_pending=1, date_expires=캡처 시각+24시간(PENDING_ENTRY_TTL)으로 행을 만들고, 이미지와 EXIF 를 쓴 뒤 is_pending=0, date_expires=NULL 로 바꿉니다. 이 행에는 relative_path, `_display_name`, mime_type 과, 캡처 시각의 유닉스 초를 담은 date_added·date_modified 가 들어갑니다 [1]. 저장이 중간에 끊기면 대기(pending) 상태 항목이 남을 수 있고, 대기 항목의 파일 이름 규칙은 [지운 사진의 흔적](mediastore/deleted-media.md) 페이지에 있습니다.

스크린샷 EXIF 에 적는 태그는 다음과 같습니다 [1].

| 태그 | 값 |
|---|---|
| ImageUniqueID | 요청마다 만든 UUID |
| Software | "Android " + Build.DISPLAY |
| ImageWidth, ImageLength | 이미지 가로·세로 |
| DateTimeOriginal | "yyyy:MM:dd HH:mm:ss" 꼴의 캡처 시각 |
| SubSecTimeOriginal | 밀리초 3자리 |
| OffsetTimeOriginal | 시차(예 "+09:00") |

카메라 정보와 GPS 태그는 쓰지 않고, 스크린샷을 찍을 때 화면에 떠 있던 앱도 파일 이름이나 EXIF 에 넣지 않습니다 [1]. 삼성 media.db 에는 captured_app, captured_url 칸이 있는데 [미디어 DB 구조 (external.db)](mediastore/external-db.md) 페이지에서 다루고, 이 칸과 스크린샷의 관계는 공개된 자료가 없어 검체로 확인해야 합니다.

### AOSP 화면 녹화

녹화하는 동안 SystemUI 는 자기 앱 캐시 폴더(getCacheDir())에 임시 파일 `temp*.mp4`(영상)와 `temp*.aac`(내부 소리)를 씁니다 [2]. 녹화가 끝나면 기기 기본 시간대의 SimpleDateFormat 으로 `screen-yyyyMMdd-HHmmss.mp4` 이름을 만들어 MediaStore 동영상 모음(external_primary)에 mime_type video/mp4 로 넣습니다 [2]. 이때 RELATIVE_PATH 를 지정하지 않아서 MediaProvider 의 동영상 기본 폴더인 Movies 에 저장됩니다 [2][3].

소리를 함께 녹음했다면 캐시 폴더에서 영상과 소리를 합친(mux) 뒤 복사하고 임시 파일을 지웁니다 [2]. 코드 흐름으로 보면 녹화 도중 기기가 꺼질 때 캐시 폴더에 temp 파일이 남을 가능성이 있습니다. 저장한 뒤 알림에 쓰는 섬네일을 ThumbnailUtils.createVideoThumbnail() 로 만드는데 [2], 이 섬네일이 파일로 남는지는 검체에서 확인합니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| AOSP 이름 규칙에 맞는 파일 이름과, 그 이름 속 캡처 시각(기기 시간대 기준) | 그 이름을 SystemUI 가 붙였다는 것(이름은 바꿀 수 있음), 누가 버튼을 눌렀는지 |
| EXIF 의 캡처 시각과 시차 | 그 화면에 어느 앱이 떠 있었는지(AOSP 는 적지 않음) |
| EXIF Software 에 적힌 빌드 표시값 | 이 기기에서 찍었다는 것(다른 기기의 스크린샷을 받아 둔 것일 수 있음) |
| is_pending=1 로 남은 스크린샷 행 | 저장이 끊긴 이유 |
| 화면 녹화 파일의 이름 속 시각 | 녹화를 시작한 시각인지 끝낸 시각인지(코드에서 이름을 만드는 시점은 저장 단계) |

"상대의 대화를 캡처했다" 보다 "이 이름의 PNG 가 이 폴더에 있고, EXIF 에 이 캡처 시각·시차와 이 빌드 표시값이 적혀 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

| 값 | 기준 | 비고 |
|---|---|---|
| 스크린샷 파일 이름 속 시각 | 기기 시간대 현지 시각, 초 단위 | 캡처 시각 [1] |
| EXIF DateTimeOriginal + SubSecTimeOriginal | 현지 시각, 밀리초까지 | [1] |
| EXIF OffsetTimeOriginal | 시차 | 이름 속 시각을 UTC 로 바꿀 때 씀 [1] |
| 스크린샷 행 date_added·date_modified | 유닉스 초(UTC) | 캡처 시각으로 넣지만 date_added 는 MediaProvider 가 넣는 순간의 시각으로 다시 씀 [1][3] |
| 화면 녹화 파일 이름 속 시각 | 기기 기본 시간대 현지 시각 | 저장 단계에서 만든 이름 [2] |
| 화면 녹화 행 datetaken | 유닉스 밀리초(UTC) | System.currentTimeMillis() 를 넣음 [2][4] |

스크린샷은 EXIF 만으로 시차를 포함한 캡처 시각을 알 수 있어서 [1], 이름 속 시각과 OffsetTimeOriginal 로 계산한 UTC 를 date_modified 와 나란히 놓고 크게 어긋나는 파일을 골라 다시 봅니다. 화면 녹화는 insertFile() 이 date_added 를 유닉스 초로 다시 쓰고 [3], datetaken 은 밀리초 칸이라서 [4] 두 칸을 같은 단위로 바꿔 비교합니다. 기기 시간대는 [시간대와 시각 설정](../system-account/time-zone.md), 단위 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지를 봅니다.

## 함정과 한계

- 이름 규칙만 보고 스크린샷을 찾으면 삼성 기기의 다른 이름·다른 폴더를 놓칠 수 있습니다. 삼성 기기에는 AOSP 기본 위치가 아닌 `DCIM/Screenshots` 가 있을 수 있습니다.
- 파일 이름과 EXIF 는 파일을 복사해도 그대로 따라가서, 다른 기기에서 찍은 스크린샷을 받은 파일과 이 기기에서 찍은 파일을 이름만으로 가를 수 없습니다. EXIF Software 의 빌드 표시값을 [기기 정보와 빌드](../system-account/device-build.md) 의 값과 맞춰 봅니다.
- 이 페이지의 AOSP 동작은 현행 main 가지 소스 기준이라 [1][2], 예전 Android 버전의 동작은 검체에서 확인합니다.
- 화면 녹화 temp 파일이 SystemUI 캐시에 남는지는 코드로 짐작한 것일 뿐이고, 그 폴더는 시스템 앱 전용이라 확보 방법에 따라 볼 수 없을 수 있습니다.

## 직접 분석해 보기

**이름과 EXIF 읽기.** AOSP 소스의 예시 이름을 따라가 봅니다 [1]. 아래 EXIF 값은 소스의 형식으로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다.

```text
Screenshot_20201215-090626.png
           └ 2020-12-15 09:06:26 (기기 시간대 현지 시각)
EXIF DateTimeOriginal   "2020:12:15 09:06:26"
     SubSecTimeOriginal "123"      → 09:06:26.123
     OffsetTimeOriginal "+09:00"   → UTC 2020-12-15 00:06:26.123
     Software           "Android <Build.DISPLAY 값>"
```

EXIF 문자열을 헥스로 찾는 방법은 [카메라 사진과 메타데이터](dcim-exif.md) 페이지에 있습니다. 이름 속 시각과 EXIF 시각이 다르면 파일 이름을 바꿨거나 AOSP 가 아닌 다른 앱이 만든 파일일 수 있습니다.

**external.db 쿼리.** 확보한 external.db 사본을 SQLite 를 읽는 공개 도구(예: sqlite3 명령줄)로 열어 스크린샷·화면 녹화 행과 대기 상태 행을 뽑습니다. 아래 쿼리는 이 페이지의 칸 이름으로 만든 예시입니다.

```sql
SELECT _id, relative_path, _display_name, mime_type, is_pending,
       datetime(date_added, 'unixepoch')       AS added_utc,
       datetime(date_modified, 'unixepoch')    AS modified_utc,
       datetime(datetaken / 1000, 'unixepoch') AS taken_utc,
       datetime(date_expires, 'unixepoch')     AS expires_utc
FROM files
WHERE _display_name LIKE 'Screenshot%'
   OR _display_name LIKE 'screen-%'
   OR relative_path LIKE '%Screenshots%'
ORDER BY date_added;
```

is_pending=1 이고 expires_utc 가 캡처 시각에서 하루 뒤쯤인 행은 저장이 끝나지 않은 스크린샷 후보입니다.

## 교차 검증

- [미디어 저장소 (MediaStore)](mediastore/index.md) — 같은 파일의 넣은 앱과 휴지통 상태를 봅니다.
- [최근 앱 화면 (Recents·Snapshots)](../app-usage/recents-snapshots.md) — 사용자가 저장하지 않아도 시스템이 남기는 앱 화면 사본입니다.
- [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) — 캡처 시각 무렵 앞에 떠 있던 앱을 봅니다.
- [알림 기록 (Notification History)](../app-usage/notification-history.md) — AOSP 화면 녹화는 저장 뒤 알림용 섬네일을 만드니 [2], 그 무렵 SystemUI 알림이 남았는지 봅니다.
- [섬네일 캐시 (Thumbnails)](thumbnails.md) — 지운 스크린샷의 작은 사본이 남는지 봅니다.
- [파일 공유 (Quick Share·Nearby Share)](../network/quick-share.md), [자료를 밖으로 보냈나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) — 화면을 저장해 밖으로 보냈는지 볼 때 함께 봅니다.

## 실습

공개 검체(NIST CFReDS 등)에서 Android 이미지를 구할 수 있으면 다음을 풀어 봅니다.

1. `Pictures/Screenshots` 와 `DCIM/Screenshots` 가운데 어디에 스크린샷이 있는지, 이름이 AOSP 규칙과 같은지 확인합니다.
2. 스크린샷 몇 장의 이름 속 시각, EXIF DateTimeOriginal·OffsetTimeOriginal, external.db 의 date_modified 를 한 표에 놓고 차이를 봅니다.
3. EXIF Software 값을 검체의 빌드 정보와 비교해, 다른 기기에서 받은 스크린샷이 섞여 있는지 봅니다.
4. is_pending=1 로 남은 행이 있는지, 화면 녹화 파일이 Movies 에 있는지 확인합니다.

## 참고 문헌

1. AOSP frameworks/base — packages/SystemUI/src/com/android/systemui/screenshot/ImageExporter.java (main), https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/packages/SystemUI/src/com/android/systemui/screenshot/ImageExporter.java
2. AOSP frameworks/base — packages/SystemUI/src/com/android/systemui/screenrecord/ScreenMediaRecorder.java (main), https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/packages/SystemUI/src/com/android/systemui/screenrecord/ScreenMediaRecorder.java
3. AOSP MediaProvider — src/com/android/providers/media/MediaProvider.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/MediaProvider.java
4. AOSP MediaProvider — apex/framework/java/android/provider/MediaStore.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/apex/framework/java/android/provider/MediaStore.java
5. Android Developers — Access media files from shared storage, https://developer.android.com/training/data-storage/shared/media
