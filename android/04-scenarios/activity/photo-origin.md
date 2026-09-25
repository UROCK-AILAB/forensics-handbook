---
title: "이 사진은 언제 어디서 찍었나"
parent: "시나리오 · 행위 재구성"
nav_order: 1580
---

# 이 사진은 언제 어디서 찍었나 (Photo Origin)

## 조사 질문

"이 사진은 이 폰으로 찍었나, 아니면 어디서 받았나", "찍은 시각과 장소는 언제 어디인가", "사진에 적힌 날짜를 믿어도 되나" 같은 질문에 답하는 흐름입니다. 사진 한 장의 출처를 가리려면 파일 안의 EXIF, 미디어 저장소(MediaStore)의 색인 행, 파일이 놓인 폴더, 촬영 순간 기기에 남은 상태 변화를 나란히 놓고 서로 맞는지 봐야 합니다.

기록은 "이 파일의 EXIF 에 이 시각과 이 좌표가 적혀 있다", "이 앱이 이 파일을 넣었다" 까지 알려 주지만, EXIF 는 파일 안에 적힌 글자라 고칠 수 있고, 좌표는 기기가 잡은 위치일 뿐 사람이 거기 서 있었다는 뜻은 아닙니다. 사진을 지운 흔적은 [지운 대화와 사진 찾기](deleted-content.md), 그 시각 기기 위치를 다른 기록으로 세우는 일은 [그 시각에 어디 있었나](location.md) 에서 다룹니다.

## 먼저 확인할 것

- **OS 버전과 제조사** — 현행 MediaStore 는 위치를 색인하지 않고 [4] Android 10 이상에서는 앱이 받는 사본에서 위치가 가려질 수 있어서 [6], 검체 버전과 사진을 확보한 경로를 먼저 적어 둡니다. 삼성 기기에는 AOSP 미디어 저장소와 따로 삼성 미디어 제공자의 DB 가 있습니다 [7].
- **시간대** — EXIF 의 촬영 시각은 시간대 없는 현지 시각 문자열이고, 시간대는 따로 된 태그에 적힙니다 [1]. 촬영 당시 기기의 시간대를 모르면 UTC 로 바꾼 값이 틀릴 수 있어서, [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md) 을 먼저 봅니다.
- **사용자와 프로필** — 보안 폴더 안에서 찍은 사진은 다른 사용자 공간에 저장될 수 있습니다([보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md)).
- **수집 범위** — 사진은 원본 파일 그대로 확보해야 합니다. 메신저나 앱을 거쳐 받은 사본은 EXIF 위치가 가려져 있을 수 있고 [6], 파일 시스템 시각은 복사 과정에서 바뀔 수 있습니다. 해시를 매긴 원본과 MediaStore DB 를 함께 확보했는지 확인합니다([모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md)).

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 파일 위치 (`/sdcard/DCIM` 등) | 카메라 폴더인지, 스크린샷인지, 내려받은 파일인지 | [공용 저장 공간](../../01-foundations/storage/shared-storage.md) |
| 2 | EXIF 시각 태그 | 촬영 시각(현지), 그 시각의 시간대, 초 아래 자리 | [카메라 사진과 메타데이터](../../02-artifacts/media/dcim-exif.md) |
| 3 | EXIF GPS 태그 | 좌표와 방향, GPS 가 위치를 잡은 UTC 시각, 위치를 잡은 방법 | [카메라 사진과 메타데이터](../../02-artifacts/media/dcim-exif.md) |
| 4 | EXIF 기기 태그 | 제조사·모델·소프트웨어 | [카메라 사진과 메타데이터](../../02-artifacts/media/dcim-exif.md) |
| 5 | MediaStore `files` 표, 삼성 `media.db` | 색인 시각, 파일을 넣은 앱, 촬영·저장 앱 | [미디어 저장소](../../02-artifacts/media/mediastore/index.md) |
| 6 | 배터리 사용 기록의 camera·gps 줄 | 그 시각에 카메라나 GPS 가 켜졌던 구간 | [배터리 사용 기록](../../02-artifacts/app-usage/batterystats.md) |

## 분석 흐름

1. **파일이 놓인 자리를 봅니다.** 관찰 기기의 `/sdcard/DCIM` 아래에는 `Camera`, `Screenshots`, `media` 와 이름이 가려진 폴더들이 있었고, 스크린샷이 AOSP 기본 위치로 알려진 `Pictures/Screenshots` 가 아니라 `DCIM/Screenshots` 에 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 같은 기기의 `/sdcard/Download` 에는 항목이 151개, `Pictures` 에는 39개 있었는데 (확인 범위: SM-S937N, Android 16, One UI 8.5), 받은 사진은 이렇게 `DCIM/Camera` 밖에 쌓일 수 있습니다. 폴더는 출발점일 뿐이라서 사용자가 파일을 옮기면 자리도 바뀝니다. 파일 이름에 날짜가 들어 있어도 이름은 사용자가 바꿀 수 있고 다른 기기에서 받은 파일일 수도 있으므로, 이름의 날짜를 촬영 시각의 근거로 쓰지 않습니다.

2. **EXIF 시각 태그를 읽습니다.** 촬영 시각은 `DateTimeOriginal`(0x9003)에 "원본 이미지를 찍은 날짜·시각" 으로 적히고, 그 시간대는 `OffsetTimeOriginal`(0x9011)에, 초 아래 자리는 `SubSecTimeOriginal`(0x9291)에 따로 적힙니다 [1]. 도구마다 태그 이름이 달라 보고서에서 혼동하기 쉬운 두 태그가 있어 아래처럼 같이 적습니다 [1].

   | 태그 번호 | ExifTool 표시 이름 | EXIF 규격 이름 | 시간대 태그 |
   |---|---|---|---|
   | 0x9003 | DateTimeOriginal | DateTimeOriginal | OffsetTimeOriginal (0x9011) |
   | 0x9004 | CreateDate | DateTimeDigitized | OffsetTimeDigitized (0x9012) |
   | 0x0132 | ModifyDate | DateTime | OffsetTime (0x9010) |

   Android 의 `ExifInterface` 도 같은 이름 문자열(`DateTime`, `DateTimeOriginal`, `OffsetTimeOriginal`, `SubSecTimeOriginal`)을 씁니다 [3]. 시간대 태그가 없는 파일이라면 촬영 시각은 "시간대를 모르는 현지 시각" 으로만 적습니다.

3. **EXIF GPS 태그를 읽습니다.** GPS 태그는 EXIF 안의 따로 된 IFD 에 들어 있습니다 [2]. 위도 `GPSLatitude`(0x0002)와 경도 `GPSLongitude`(0x0004)는 도·분·초 세 값의 유리수이고, 북·남과 동·서는 `GPSLatitudeRef`(0x0001, N/S)와 `GPSLongitudeRef`(0x0003, E/W)에 따로 있어서 Ref 를 빠뜨리면 남반구·서반구 좌표의 부호가 틀립니다 [2]. `GPSTimeStamp`(0x0007)는 GPS 가 위치를 잡은 UTC 시각이고 `GPSDateStamp`(0x001d)는 `YYYY:mm:dd` 형식의 UTC 날짜입니다 [2]. `GPSProcessingMethod`(0x001b)에는 "GPS", "CELLID", "WLAN", "MANUAL" 같은 값이 들어가 위성·기지국·Wi-Fi·수동 중 무엇으로 위치를 잡았는지 알려 주고, `GPSHPositioningError`(0x001f)는 수평 위치 오차입니다 [2]. 삼성 카메라가 이 두 태그를 채우는지는 확인하지 못했으므로, 비어 있으면 비어 있다고 적습니다.

   > 그림 자리: EXIF 안에서 IFD0 → Exif IFD(시각 태그) 와 IFD0 → GPS IFD(위치 태그) 로 갈라지는 구조를 상자로 그린 그림. 명세로 만든 예시라고 밝힌다

4. **두 시각을 맞춰 봅니다.** `DateTimeOriginal` 은 현지 시각이고 GPS 날짜·시각은 UTC 라서 기준이 다릅니다 [1][2]. 두 값의 차이가 `OffsetTimeOriginal` 과 맞으면 촬영 당시 기기 시간대 설정이 일관된 것이고, 맞지 않으면 기기 시각이 잘못 맞춰져 있었거나 GPS 가 위치를 잡은 때가 촬영보다 앞섰거나 EXIF 가 고쳐졌을 가능성을 차례로 봅니다. 이 단계는 두 출처에서 끌어낸 해석이라서, 보고서에는 두 값을 그대로 적고 차이를 따로 적습니다.

5. **어느 기기가 찍었는지 봅니다.** `Make`(0x010f), `Model`(0x0110), `Software`(0x0131), `ImageUniqueID`(0xa420) 같은 태그로 찍은 기기와 소프트웨어를 봅니다 [1]. `Make`·`Model` 이 조사 기기와 다르면 받은 파일일 가능성을 먼저 봅니다. AOSP 스크린샷은 EXIF 에 `ImageUniqueID`, `Software`("Android " 와 빌드 표시 이름), `DateTimeOriginal`, `SubSecTimeOriginal`, `OffsetTimeOriginal` 을 쓰고 카메라·GPS 태그는 쓰지 않아서 [8] 카메라 사진과 가를 수 있지만, 삼성 스크린샷도 같은지는 확인하지 못했습니다.

6. **MediaStore 행과 맞춥니다.** `datetaken` 은 EXIF `DateTimeOriginal`(동영상은 메타데이터의 날짜)에서 뽑은 유닉스 밀리초이고, 문서 주석은 이미지의 경우 `DateTimeOriginal` 과 `OffsetTimeOriginal` 이 둘 다 있어야 이 값을 믿을 수 있다고 적습니다 [4]. `date_added` 는 처음 색인한 시각, `date_modified` 는 파일 수정 시각이고 둘 다 유닉스 초입니다 [4]. 현행 AOSP 에서는 앱이 어떤 값을 넣든 MediaProvider 가 `date_added` 를 그때의 현재 시각으로 다시 쓰므로 [5], `datetaken` 보다 `date_added` 가 한참 늦다면 나중에 기기로 들어온 파일일 수 있습니다. `owner_package_name` 은 이 미디어를 넣은 패키지이고 확실하지 않으면 NULL 일 수 있습니다 [4]. 삼성 `media.db` 의 `files` 표에는 `captured_url`, `captured_app` 칸도 있어 ALEAPP 가 함께 읽는데 [7], 칸 뜻을 삼성이 공개한 문서는 찾지 못했으므로 값은 원래 칸 이름과 함께 옮깁니다.

7. **위치는 원본 파일에서 읽습니다.** MediaStore 의 `latitude`·`longitude` 칸은 폐기돼 항상 NULL 이고 [4], MediaProvider 는 자신이 아닌 앱이 이 칸에 값을 넣으려 하면 NULL 로 바꿉니다 [5]. Android 10 이상에서 앱이 EXIF 위치를 가리지 않은 채 읽으려면 `ACCESS_MEDIA_LOCATION` 권한과 사용자 동의가 필요하므로 [6], 앱을 거쳐 뽑은 사본에 좌표가 없다고 해서 원본에도 없다고 단정하지 않습니다.

8. **촬영 순간의 보조 흔적을 겹칩니다.** 관찰 기기의 `dumpsys batterystats` 이력에는 `+camera`·`-camera` 가 붙은 줄과 `+gps`·`-gps` 줄이 있었고, 줄 앞 시각은 연도 없는 `MM-DD HH:MM:SS.mmm` 모양이었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). camera 줄이 카메라 하드웨어 사용 구간을 뜻하는지는 출처로 확인하지 못했고 gps 줄에는 좌표가 없으므로, EXIF 시각 근처에 이런 줄이 있는지를 보조 근거로만 씁니다.

## 흔한 오판

**"기기에 있다" 를 "기기가 찍었다" 로 읽는 오판**이 가장 흔합니다. `Make`·`Model` 이 다르거나, EXIF 가 비어 있거나, `owner_package_name` 이 카메라 앱이 아니면 받은 파일일 가능성을 먼저 봅니다. 메신저가 전송 과정에서 EXIF 를 지우는지는 앱마다 달라 확인하지 못했습니다.

**`DateTimeOriginal` 을 UTC 로 읽는 실수**도 자주 나옵니다. 이 값은 시간대 없는 현지 시각이고 시간대는 `OffsetTimeOriginal` 에 따로 있습니다 [1].

**Ref 태그를 빼고 좌표를 옮기는 실수**가 있습니다. Ref 가 빠지면 서경·남위 좌표의 부호가 뒤집혀 전혀 다른 곳이 나옵니다 [2].

**EXIF 를 바꿀 수 없는 기록으로 믿는 것**도 조심합니다. EXIF 는 파일 안의 글자라 고칠 수 있으므로, EXIF 시각·MediaStore 의 `date_added`·파일 시스템 시각·배터리 기록을 함께 맞춰 봅니다. 서로 어긋나면 어긋났다는 사실 자체를 적고, 어긋난 까닭은 근거가 있을 때만 적습니다.

**MediaStore 에서 좌표가 NULL 이라 위치 정보가 없다고 보는 경우**가 있습니다. 이 칸은 폐기돼 항상 NULL 이고 위치는 원본 파일에 있습니다 [4].

## 보고서 문장 예

| 쓰지 않을 문장 | 쓸 문장 |
|---|---|
| 피의자는 ○○일 ○○시에 ○○에서 이 사진을 찍었다. | 파일 ○○(SHA-256 ○○)의 EXIF 에 촬영 시각 `DateTimeOriginal` ○○:○○:○○(시간대 `OffsetTimeOriginal` +09:00)과 GPS 좌표 ○○, ○○(`GPSProcessingMethod` 값 ○○)가 적혀 있고, GPS UTC 시각은 ○○:○○:○○ 입니다. `Make`·`Model` 태그는 조사 기기와 같은 ○○ 입니다. |
| 이 사진은 받은 사진이다. | 이 파일은 `/sdcard/Download` 아래에 있고, EXIF 의 `Model` 태그는 조사 기기와 다른 ○○ 이며, MediaStore 의 `owner_package_name` 은 ○○ 입니다. `date_added` 는 `datetaken` 보다 ○○일 늦습니다. |
| 촬영 시각이 조작됐다. | EXIF 의 `DateTimeOriginal` 과 GPS UTC 시각의 차이는 ○○시간으로 `OffsetTimeOriginal` 값과 맞지 않습니다. 이 차이의 원인은 확보한 기록으로 판단할 수 없습니다. |

보고서 전체의 틀은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 아티팩트 본문: [카메라 사진과 메타데이터](../../02-artifacts/media/dcim-exif.md), [미디어 저장소](../../02-artifacts/media/mediastore/index.md), [삼성 갤러리](../../02-artifacts/media/samsung-gallery.md), [섬네일 캐시](../../02-artifacts/media/thumbnails.md), [스크린샷과 화면 녹화](../../02-artifacts/media/screenshots.md), [구글 포토](../../02-artifacts/media/google-photos.md)
- 기반 구조: [공용 저장 공간](../../01-foundations/storage/shared-storage.md), [시각 값](../../01-foundations/value-decoding/time-values.md)
- 이어지는 시나리오: [그 시각에 어디 있었나](location.md), [지운 대화와 사진 찾기](deleted-content.md)
- 기법: [타임라인 작성](../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. ExifTool Tag Names, EXIF Tags — https://exiftool.org/TagNames/EXIF.html
2. ExifTool Tag Names, GPS Tags — https://exiftool.org/TagNames/GPS.html
3. AOSP frameworks/base, media/java/android/media/ExifInterface.java (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/media/java/android/media/ExifInterface.java
4. AOSP MediaProvider — apex/framework/java/android/provider/MediaStore.java (main) — https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/apex/framework/java/android/provider/MediaStore.java
5. AOSP MediaProvider — src/com/android/providers/media/MediaProvider.java (main) — https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/MediaProvider.java
6. Android Developers — Access media files from shared storage — https://developer.android.com/training/data-storage/shared/media
7. ALEAPP (커밋 c044fe5) — scripts/artifacts/samsungMediaProvider.py — https://github.com/abrignoni/ALEAPP/tree/main/scripts/artifacts
8. AOSP frameworks/base — packages/SystemUI/src/com/android/systemui/screenshot/ImageExporter.java (main) — https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/packages/SystemUI/src/com/android/systemui/screenshot/ImageExporter.java
