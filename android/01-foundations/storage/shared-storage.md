---
title: "공용 저장 공간"
parent: "기반 · 저장 구조"
nav_order: 140
---

# 공용 저장 공간 (Shared Storage·/sdcard)

## 한 줄 요약

사용자가 파일 앱이나 PC 연결로 보는 `/sdcard` 는 실제로는 `/data/media/<userid>` 에 있는 데이터를 앱마다 알맞은 보기로 보여 주는 공간이고, 사진·다운로드·녹음처럼 앱을 지워도 남는 파일과 `Android/data` 아래 앱 전용 파일이 함께 들어 있습니다.

## 이 구조를 쓰는 아티팩트

카메라 사진과 스크린샷, 다운로드한 파일, 녹음 파일이 모두 이 공간에 놓이고, 시스템은 이 공간을 훑어 미디어 파일을 [미디어 저장소 (MediaStore)](../../02-artifacts/media/mediastore/index.md) 에 모읍니다. 사진 파일 자체의 메타데이터는 [카메라 사진과 메타데이터](../../02-artifacts/media/dcim-exif.md), 스크린샷은 [스크린샷과 화면 녹화](../../02-artifacts/media/screenshots.md), 갤러리 앱이 따로 남기는 기록은 [삼성 갤러리](../../02-artifacts/media/samsung-gallery.md) 페이지에서 다룹니다. 자료를 밖으로 옮겼는지 볼 때도 이 공간이 출발점이 되고, 그 흐름은 [자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 시나리오에서 다룹니다.

## 구조

### 위치와 보기 방식

AOSP 저장소 문서는 공용 저장 공간의 표준 위치로 `/sdcard` 와 사용자별로 나뉜 `/storage/emulated/<userId>` 를 들고, installd 소스는 사용자별 실제 데이터 위치를 `/data/media/<userid>` 로 정합니다. 에뮬레이션 저장소는 Android 3.0 이상에서 내부 저장소를 FUSE 계층을 거쳐 보여 주는 방식이고, Android 11 이상으로 출시하면서 커널 5.4 이상을 쓰는 기기는 이 계층에 SDCardFS 대신 FUSE 를 씁니다. 관찰 기기에서 `/sdcard` 가 어느 쪽인지는 마운트 정보를 보지 않아 확인하지 못했습니다.

앱마다 보이는 모습이 다를 수 있다는 점도 중요합니다. AOSP 문서에 따르면 Zygote 가 앱 프로세스를 만들 때 앱마다 마운트 네임스페이스 (Mount Namespace) 를 따로 만들고 그 앱에 맞는 보기를 bind mount 로 붙이며, 권한에 따라 `/mnt/runtime/default`(저장소 권한 없음), `/mnt/runtime/read`, `/mnt/runtime/write` 가운데 하나를 씁니다. 이 방식이 FUSE 전환 뒤 어떻게 바뀌었는지는 출처에서 확인하지 못했습니다.

저장 볼륨은 세 가지로 나뉩니다.

| 종류 | 설명 |
|---|---|
| 기존 저장소 | 휴대용 SD 카드·USB 와 에뮬레이션 저장소 |
| 채택 저장소 (Adoptable Storage) | Android 6.0 이상, 외장 매체를 암호화·포맷해 내부 저장소처럼 씀. 데이터 뿌리는 `/mnt/expand/<volume_uuid>` |
| 휴대용 저장소 (Portable Storage) | 외장 매체를 따로 떼어 쓰는 볼륨 |

`/data/media/<userid>` 가 CE 영역에 속하는지 같은 암호화 구분은 [저장 공간 암호화](encryption/index.md) 갈래에서, 파일 시스템 자체는 [파일 시스템](filesystems/index.md) 갈래에서 다룹니다.

### 표준 폴더와 MediaStore 모음

시스템은 공용 저장 공간을 자동으로 훑어 미디어 파일을 모음 (Collection) 별로 나눠 넣고, 공식 문서가 적는 폴더와 모음의 짝은 아래와 같습니다.

| 모음 | 들어가는 폴더 | 버전 차이 |
|---|---|---|
| Images | `DCIM/`, `Pictures/` | 사진과 스크린샷 |
| Video | `DCIM/`, `Movies/`, `Pictures/` | |
| Audio | `Alarms/`, `Audiobooks/`, `Music/`, `Notifications/`, `Podcasts/`, `Ringtones/`, `Recordings/` | `Recordings/` 는 Android 11 이하에 없음 |
| Downloads | `Download/` | Android 9 이하에는 이 모음이 없음 |
| Files | 모든 종류의 미디어 파일 | 범위 지정 저장소가 켜진 앱에는 그 앱이 만든 사진·동영상·오디오만 보임 |

볼륨 이름도 두 가지를 구분합니다. `VOLUME_EXTERNAL` 은 모든 공용 저장 볼륨을 합쳐 보여 주는 읽기 전용 합성 볼륨이고, `VOLUME_EXTERNAL_PRIMARY` 는 읽고 쓸 수 있는 주 공용 저장 볼륨입니다.

관찰 기기의 `/sdcard` 최상위에는 `Alarms`, `Android`, `Audiobooks`, `DCIM`, `Documents`, `Download`, `Movies`, `Music`, `Notifications`, `Pictures`, `Podcasts`, `Recordings`, `Ringtones` 이 있었고, 이름을 가린 표준 밖 폴더가 8개 더 있었습니다(확인 범위: SM-S937N, Android 16, One UI 8.5). Android 16 기기에서 `Recordings` 가 보인 것은 공식 문서의 "Android 11 이하에는 없음" 과 어긋나지 않습니다. 스크린샷은 `DCIM/Screenshots` 에 있었고, `DCIM` 아래에는 `Camera`, `Screenshots`, `media` 와 표준 밖 폴더 19개를 합쳐 항목 25개가 있었습니다(확인 범위: SM-S937N, Android 16, One UI 8.5). `DCIM/media` 의 용도와 다른 제조사 기기의 스크린샷 폴더는 확인하지 못했습니다.

> 그림 자리: `/sdcard` 최상위 표준 폴더와 각 폴더가 들어가는 MediaStore 모음을 선으로 이은 그림

### Android 폴더 (data·media·obb)

관찰 기기의 `/sdcard/Android` 아래에는 `data`, `media`, `obb` 세 폴더가 있었습니다(확인 범위: SM-S937N, Android 16, One UI 8.5). 세 폴더는 성격이 서로 다릅니다.

| 폴더 | 성격 |
|---|---|
| `Android/data/<패키지>` | 앱 전용 폴더입니다. 앱을 지우면 함께 지워지고, 구조는 [앱 데이터 폴더 구조](app-data-layout.md) 페이지에서 다룹니다 |
| `Android/media/<패키지>` | 공식 문서가 공용 저장 공간의 일부라고 적는 폴더입니다 |
| `Android/obb` | Android 11 을 대상으로 하는 앱은 문서 선택 화면으로 사용자에게 `Android/data` 와 이 폴더 안의 파일을 고르게 할 수 없습니다 |

관찰 기기의 `Android/media` 아래에는 앱 폴더가 5개로 적혔고, 이름이 보인 것은 `com.google.android.gms` 와 `com.samsung.android.spay` 였습니다(확인 범위: SM-S937N, Android 16, One UI 8.5). adb 일반 셸 권한으로 `Android/data` 와 `Android/obb` 안을 나열할 수 있는지는 관찰하지 않았습니다.

### 버전별 접근 규칙

다른 앱이 공용 저장 공간의 어디까지 읽을 수 있었는지는 기기의 Android 버전과 앱이 대상으로 삼은 버전에 따라 다릅니다. 파일을 누가 만들고 읽었을 수 있는지 따질 때 이 표를 기준으로 삼습니다.

| 버전 | 규칙 |
|---|---|
| Android 9 이하 | 저장소 권한만 있으면 다른 앱의 `Android/data` 파일까지 접근할 수 있었습니다 |
| Android 10(API 29) 대상 앱 | 범위 지정 저장소 (Scoped Storage) 가 기본이고, `requestLegacyExternalStorage` 로 잠시 빠질 수 있었습니다 |
| Android 11(API 30) 대상 앱 | 시스템이 `requestLegacyExternalStorage` 를 무시합니다 |
| Android 11 이상 기기 | 대상 버전과 상관없이 MediaStore 말고도 File API·`fopen()` 같은 직접 경로로 공용 미디어에 접근할 수 있습니다 |
| Android 10~12 | 미디어를 읽는 권한은 `READ_EXTERNAL_STORAGE` 입니다 |
| Android 13 이상 | `READ_MEDIA_IMAGES`, `READ_MEDIA_VIDEO`, `READ_MEDIA_AUDIO` 로 나뉩니다 |

모든 파일 접근 권한 (`MANAGE_EXTERNAL_STORAGE`) 은 설정 화면에서 "Allow access to manage all files" 로 보이고, 이 권한을 받은 앱은 공용 저장 공간 전체와 MediaStore.Files 표 내용, OTG·SD 카드의 뿌리 폴더까지 읽고 쓸 수 있습니다. 그래도 `/sdcard/Android` 아래 대부분과 다른 앱의 `Android/data` 는 이 권한으로도 볼 수 없습니다. Google Play 는 2021년 5월부터 이 권한에 정책을 적용했습니다. 탐지 관점에서 이 권한을 받은 앱 목록은 곧 공용 저장 공간 전체를 읽을 수 있는 앱 목록이지만, 권한 부여 상태가 기기의 어디에 남는지는 확인하지 못했습니다. 권한 전반은 [앱 샌드박스와 권한](../security-model/sandbox-permissions.md) 페이지를 봅니다.

### 사용자가 여럿인 기기

공용 저장 공간도 사용자마다 따로 있습니다(`/storage/emulated/<userId>`, `/data/media/<userid>`). 관찰 기기의 `dumpsys user` 출력에는 사용자가 두 명이었고 `UserProperties` 아래 `mMediaSharedWithParent=false` 가 두 번 보였습니다(확인 범위: SM-S937N, Android 16, One UI 8.5). 칸 이름으로 보아 부모 사용자와 공용 저장 공간을 나눠 쓰지 않는다는 뜻으로 읽을 수 있지만, 이 칸의 뜻을 설명한 문서는 확인하지 못했습니다. 사용자 목록은 [사용자와 프로필](../../02-artifacts/system-account/users-profiles.md) 페이지에서 다룹니다.

## 읽는 법

1. 기기의 사용자 목록을 먼저 보고, 사용자마다 공용 저장 공간을 따로 확보합니다.
2. 파일 시스템 이미지가 있으면 `/data/media/<userid>` 를, 실행 중인 기기에서 모으면 `/sdcard` 를 기준으로 삼습니다. 두 경로를 한 사건에서 섞어 쓰면 같은 파일이 두 번 잡힐 수 있어서 기준 경로를 하나로 정합니다.
3. 표준 폴더와 표준 밖 폴더를 나눕니다. 표준 밖 폴더는 대개 특정 앱이 만든 것이라, 이름을 [설치된 앱](../../02-artifacts/app-usage/packages/index.md) 목록과 대조합니다.
4. 파일 목록은 MediaStore 기록과 맞춰 봅니다. 폴더에는 없는데 MediaStore 에 남은 행, 폴더에는 있는데 MediaStore 에 없는 파일이 모두 단서가 됩니다.
5. `Android/data/<패키지>` 는 앱 데이터로 분류해 해당 앱의 내부 폴더와 함께 봅니다.

관찰 기기에서는 adb 일반 셸 권한으로 `/sdcard` 최상위와 `DCIM`, `Pictures`, `Download`, `Documents`, `Android`, `Android/media` 의 목록을 읽었습니다(확인 범위: SM-S937N, Android 16, One UI 8.5). 이때 `Pictures` 에는 항목 39개(폴더 11개), `Download` 에는 151개(폴더 36개), `Documents` 에는 2개(폴더 2개)가 있었습니다. 수집 방식 전반은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지를 봅니다.

## 포렌식에서 중요한 점

**앱을 지워도 남는 파일과 함께 지워지는 파일이 나뉩니다.** 앱이 MediaStore 로 공용 폴더에 저장한 파일은 앱을 지워도 기기에 남고, `Android/data/<패키지>` 의 파일은 앱과 함께 지워집니다. 앱을 지웠다 다시 설치한 뒤 예전에 만든 파일에 접근하려면 `READ_EXTERNAL_STORAGE` 가 필요한데, 시스템이 그 파일을 이전 설치본의 것으로 보기 때문입니다. 이 동작으로 보아 MediaStore 가 파일마다 만든 앱을 기록하는 것으로 읽을 수 있지만, 그 칸 이름은 이 페이지의 출처에서 확인하지 못했습니다.

**파일 소유자와 권한 비트는 만든 앱을 뜻하지 않습니다.** Android 4.4 부터 외부 저장소 파일의 소유자·그룹·권한 비트는 디렉터리 구조를 바탕으로 만들어 낸 값입니다. 그래서 `/sdcard` 에서 보이는 소유자로 파일을 만든 앱을 가리면 안 됩니다.

**MediaStore 의 칸은 뜻을 알고 읽어야 합니다.** 공식 문서가 적는 칸 가운데 해석에 영향을 주는 것은 아래와 같고, MediaStore 데이터베이스 자체의 위치와 표 구조는 [미디어 저장소](../../02-artifacts/media/mediastore/index.md) 페이지에서 다룹니다.

| 칸 | 공식 문서의 설명 | 해석할 때 |
|---|---|---|
| `DATA` | 파일 경로지만 파일이 늘 있다고 가정하지 말라고 적습니다 | 경로가 있어도 파일은 없을 수 있습니다 |
| `RELATIVE_PATH`, `DISPLAY_NAME` | 파일을 만들거나 고칠 때 쓰는 칸입니다 | 폴더와 파일 이름을 따로 읽습니다 |
| `IS_PENDING` | 쓰는 동안 1, 끝나면 0 입니다 | 1 로 남은 행은 쓰다 만 파일일 수 있습니다 |
| `IS_TRASHED` | 휴지통 상태입니다. 제조사가 미리 넣은 갤러리 앱은 확인 창 없이 이 칸을 1 로 바꿀 수 있고, 다른 앱은 `createTrashRequest()` 를 씁니다 | 지운 것이 아니라 휴지통에 옮긴 상태일 수 있습니다 |
| `DATE_ADDED` | 앱이 `setLastModified()` 를 부르거나 사용자가 시스템 시계를 바꾸면 값이 바뀔 수 있다고 적습니다 | 파일이 처음 생긴 확정 시각으로 쓰지 않습니다 |
| `DATE_MODIFIED` | `DATE_ADDED` 와 같은 이유로 바뀔 수 있다고 적습니다 | 마지막으로 고친 확정 시각으로 쓰지 않습니다 |

공식 문서는 변경을 알아낼 때 날짜 칸보다 `MediaStore.getGeneration()` 이 돌려주는 세대 값이 믿을 만하다고 적고, 이 값은 계속 커지기만 합니다. 시스템 시계를 바꾼 흔적이 있는 기기라면 날짜 칸을 더 조심해서 읽어야 합니다. 날짜 칸의 단위(초인지 밀리초인지)는 이 페이지의 출처에서 확인하지 못해서, 시각 값을 읽을 때는 [시각 값](../value-decoding/time-values.md) 페이지의 방법으로 단위를 먼저 가립니다.

**앱이 받은 사진과 원본 파일의 위치 정보가 다를 수 있습니다.** 앱이 `ACCESS_MEDIA_LOCATION` 권한 없이 사진을 열면 EXIF 위치 정보가 가려진 사본을 받을 수 있고, 원본은 `MediaStore.setRequireOriginal()` 로 엽니다. 그래서 어떤 앱이 내보낸 사진에 위치가 없더라도 공용 저장 공간의 원본 파일에는 위치가 남아 있을 수 있습니다. 동영상 위치는 `MediaMetadataRetriever` 의 `METADATA_KEY_LOCATION` 으로 읽습니다.

## 함정

- **스크린샷 폴더를 한 곳으로 가정하기.** 관찰 기기의 스크린샷은 `DCIM/Screenshots` 에 있었습니다(확인 범위: SM-S937N, Android 16, One UI 8.5). 제조사와 버전마다 다를 수 있어서 `Pictures` 아래도 함께 봅니다.
- **`Android/media` 를 앱 전용 폴더로 보기.** `Android/data` 와 이름이 비슷하지만 공용 저장 공간에 속하는 폴더입니다.
- **모든 파일 접근 권한이면 다 읽는다고 보기.** 이 권한으로도 다른 앱의 `Android/data` 는 읽지 못합니다.
- **폴더에 없으면 없던 파일로 보기.** `IS_TRASHED` 상태의 파일, MediaStore 에만 남은 행이 있을 수 있습니다. 휴지통 파일의 실제 이름 규칙과 보관 기간, 삼성 갤러리 휴지통 위치는 이 페이지에서 확인하지 못했고 [삼성 갤러리](../../02-artifacts/media/samsung-gallery.md) 페이지에 맡깁니다.
- **Android 버전을 빼고 접근 가능성 말하기.** 같은 앱이라도 기기가 Android 9 이하인지, 앱이 어느 버전을 대상으로 했는지에 따라 읽을 수 있던 범위가 다릅니다.
- **외장 SD 카드 경로.** 외장 카드는 `/sdcard` 와 다른 볼륨이지만, 그 경로 형식은 이 페이지의 출처에서 확인하지 못했습니다. 볼륨 목록을 먼저 확인하고 볼륨마다 따로 확보합니다.

## 도구

폴더 목록은 실행 중인 기기라면 `adb shell ls` 로, 이미지라면 파일 시스템을 여는 공개 도구로 읽을 수 있습니다. 사진의 EXIF 는 [카메라 사진과 메타데이터](../../02-artifacts/media/dcim-exif.md) 페이지, MediaStore 데이터베이스는 [미디어 저장소](../../02-artifacts/media/mediastore/index.md) 페이지에서 읽는 법을 다룹니다.

## 참고 문헌

1. Storage (Data storage overview) — Android Open Source Project, https://source.android.com/docs/core/storage
2. Deprecate SDCardFS — Android Open Source Project, https://source.android.com/docs/core/storage/sdcardfs-deprecate
3. cmds/installd/utils.cpp (main 브랜치) — AOSP frameworks/native, https://android.googlesource.com/platform/frameworks/native/+/refs/heads/main/cmds/installd/utils.cpp
4. Access media files from shared storage — Android Developers, https://developer.android.com/training/data-storage/shared/media
5. Access app-specific files — Android Developers, https://developer.android.com/training/data-storage/app-specific
6. Storage updates in Android 11 — Android Developers, https://developer.android.com/about/versions/11/privacy/storage
7. Manage all files on a storage device — Android Developers, https://developer.android.com/training/data-storage/manage-all-files
