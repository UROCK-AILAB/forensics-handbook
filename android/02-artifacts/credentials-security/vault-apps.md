---
title: "숨김·볼트·앱 잠금 앱"
parent: "아티팩트 · 자격 증명·보안 설정"
nav_order: 1270
---

# 숨김·볼트·앱 잠금 앱 (Vault·App Lock Apps)

볼트 앱 (Vault App) 은 사진·동영상·파일을 원래 자리에서 앱만 아는 곳으로 옮겨 숨기고, 앱 잠금 앱 (App Lock) 은 다른 앱을 열 때 암호를 한 번 더 묻게 합니다 [1][2]. 볼트 기능이 있는 앱은 원래 경로·옮긴 경로·옮긴 시각을 자기 DB 에 적고, 숨긴 파일 자체는 공용 저장 공간의 점(.)으로 시작하는 폴더나 앱 전용 폴더에 둡니다 [3][4][5]. 이 페이지는 그 기록이 어디에 어떤 모양으로 남는지, 계산기처럼 꾸민 앱을 어떻게 알아보는지를 다루고, 숨긴 파일을 여는 절차와 잠금 암호를 푸는 방법은 다루지 않습니다.

## 무엇을 기록하나 · 왜 생기나

볼트 앱은 개인 정보를 지키려고 만든 앱이지만, 같은 기능으로 범죄 증거를 숨길 수도 있어서 수사에서는 안티포렌식 (Anti-Forensics) 도구로도 봅니다 [1][2]. 2017년에 구글 플레이에서 내려받기 수가 합쳐 2억 2천만 회쯤 되는 볼트 앱 18개를 분석했을 때, 12개는 코드를 난독화했고 5개는 네이티브 라이브러리를 썼습니다 [1]. 그래도 10개는 루팅하지 않은 기기에서 숨긴 데이터를 확인할 수 있었고, 6개는 사진을, 8개는 동영상을 암호화하지 않고 보관했습니다 [1]. 앱 잠금 앱도 같은 관점에서 연구됐고, 2023년에는 구글 플레이 내려받기 상위 앱 잠금 앱 9개가 남기는 아티팩트를 분석했습니다 [2]. 이 숫자는 그때 그 버전의 앱으로 얻은 결과라서, 지금 조사하는 기기의 앱이 같은 방식으로 저장한다고 보지 않고 버전마다 다시 확인합니다.

앱마다 구현은 다르지만 흐름은 비슷합니다. 사용자가 사진을 고르면 앱이 파일을 원래 폴더에서 자기 저장 폴더로 옮기고, 원래 경로·원래 이름·저장한 이름·시각을 앱 DB 한 행에 적습니다 [3][4][5][6][7]. 원래 폴더에서는 파일이 사라지기 때문에 갤러리나 파일 앱에서는 보이지 않습니다 [5]. 여기에 여러 앱이 아래 기능을 함께 둡니다.

| 기능 | 남는 기록 | 예 |
|---|---|---|
| 앱 잠금 목록 | 잠근 앱의 패키지 이름 | AppLock 의 lock 표 [5], GalleryVault 의 locked_app 표 [4], HideX 의 p_lock_app 표 [12] |
| 침입자 사진 (break-in) | 잠금 해제에 실패했을 때 찍은 사진과 입력한 값 | GalleryVault 의 break_in_report 표와 BreakInReports 폴더 [4], Calculator Lock 의 Intruder 폴더 [3] |
| 가짜 공간 (decoy) | 가짜 공간을 가리키는 것으로 보이는 이름이나 값 | Private Photo Vault 의 bucket_id 가 `albums_decoy` 인 앨범 [10], HLD 볼트의 IS_MOCK_SPACE 열 [7] |
| 앱 안 브라우저 | 방문 기록과 내려받기 | GalleryVault 의 browser_history·download_task 표 [4], Calculator Lock 의 History 표 [3] |
| 클라우드 백업 | 백업 계정과 올린 파일 목록 | GalleryVault 의 cloud_cache.db [4], Vaulty 설정의 drive_account_name [9] |

## 앱을 알아보는 법

### 패키지 이름

볼트 앱은 앱 이름과 아이콘을 바꿔도 패키지 이름은 그대로라서, 설치된 앱 목록의 패키지 이름을 아래 표와 맞춰 보는 것이 가장 빠릅니다. 설치된 앱 목록은 [설치된 앱 (packages.xml)](../app-usage/packages/index.md), 패키지 이름을 읽는 법은 [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md) 페이지에서 다룹니다.

| 패키지 이름 | 앱 | 겉모양 |
|---|---|---|
| `com.calculator.lock.hide.photo.video` | Calculator Lock | 실제로 계산이 되는 계산기이고, 저장한 암호를 넣으면 보관함이 열림 [3] |
| `com.hld.anzenbokusucal` | HLD 볼트 | 계산기 앱 [7] |
| `com.hld.anzenbokusufake` | HLD 볼트와 같은 계열 패키지 | 앱 잠금이고 설정에 gesture_password 항목이 있음 [7] |
| `com.thinkyeah.galleryvault` | GalleryVault | 갤러리 볼트이고 아이콘 위장·계산기 바로가기 설정이 있음 [4] |
| `com.netqin.ps` | NQ Vault | 갤러리 볼트 [6] |
| `com.theronrogers.vaultyfree` | Vaulty | 갤러리 볼트 [9] |
| `com.enchantedcloud.photovault` | Private Photo Vault | 갤러리 볼트 [10] |
| `playground.develop.applocker` | Playground AppLocker | 앱 잠금과 볼트 [11] |
| `com.domobile.applockwatcher` | AppLock (DoMobile) | 앱 잠금과 볼트 [5] |
| `com.flatfish.cal.privacy` | HideX | 앱 숨김·잠금 [12] |

표에 없는 앱은 [처음 보는 앱 분석 순서 (Unknown Apps)](../../03-techniques/analysis/app-data-analysis/unknown-apps.md) 로 살펴보고, 공용 저장 공간에 점으로 시작하는 폴더가 있는지부터 봅니다.

### 아이콘 위장

앱은 매니페스트에 `<activity-alias>` 를 두어 한 화면을 다른 아이콘과 이름으로 런처에 보일 수 있습니다 [13]. alias 의 intent-filter 에 `android.intent.action.MAIN` 과 `android.intent.category.LAUNCHER` 를 두면 런처에 따로 나타나고, `android:icon` 과 `android:label` 로 alias 만의 아이콘과 이름을 정합니다 [13]. 그래서 APK 매니페스트에 LAUNCHER 를 단 alias 가 여럿 있고 그 가운데 계산기·시계 같은 이름이 있으면 아이콘을 바꿔 보이는 기능이 있다고 읽을 수 있습니다. APK 를 푸는 법은 [APK 정보 (AndroidManifest·서명)](../embedded-metadata/apk.md) 페이지에 있습니다.

앱이 이 alias 를 켜고 끄는 방식으로 아이콘을 바꾼다면, 그 상태가 사용자별 `package-restrictions.xml` 의 `<enabled-components>`·`<disabled-components>` 에 남을 가능성이 있습니다. 이 파일의 구조는 [설치 출처와 설치 시각](../app-usage/packages/install-source-time.md) 페이지에서 다룹니다. 앱 자신도 위장 상태를 적어 둘 수 있습니다. GalleryVault 는 설정 파일 `Kidd.xml` 에 `icon_disguise_enabled`, `calculator_short_cut_id`, 위장을 켠 시각 `last_enable_icon_disguise_time` 을 둡니다 [4].

## 위치와 버전별 차이

볼트 앱의 기록은 두 곳으로 나뉩니다. 앱 DB 와 설정 파일은 대개 앱 데이터 폴더(`/data/data/패키지` 또는 `/data/user/사용자 번호/패키지`)에 있고, 숨긴 파일은 공용 저장 공간이나 앱 전용 폴더에 있습니다. 두 곳의 구조는 [앱 데이터 폴더 구조 (/data/data·/data/user)](../../01-foundations/storage/app-data-layout.md) 와 [공용 저장 공간 (Shared Storage·/sdcard)](../../01-foundations/storage/shared-storage.md) 페이지에서 다룹니다. 아래 경로는 ALEAPP 모듈의 경로 패턴과 설명에 나온 것이고, 시험 환경은 모듈에 적힌 기기와 버전입니다.

| 앱 | 앱 데이터 폴더 | 숨긴 파일이 있는 곳 | 시험 환경 |
|---|---|---|---|
| Calculator Lock | `databases/note_contact.db`, `shared_prefs/com.calculator.lock.hide.photo.video_preferences.xml` [3] | 공용 저장 공간 `Pictures/.Calculator_Lock/` 아래 Photos, Videos, Files, Intruder, Recycle_bin [3] | Pixel 7a, Android 14 [3] |
| HLD 볼트 | `shared_prefs/share_privacy_safe.xml` [7] | 공용 저장 공간 `.privacy_safe/` 아래 picture, video, db/privacy_safe.db [7][8] | Pixel 3, Android 11·12 [7] |
| GalleryVault | `databases/galleryvault.db`, `databases/AppLock.db`, `databases/cloud_cache.db`, `shared_prefs/Kidd.xml` [4] | 공용 저장 공간 `.galleryvault_` 로 시작하는 폴더 아래 files, BreakInReports, backup/file_action_log.db [4] | Pixel 7a Android 14(버전 코드 40309), Pixel 8 Pro Android 17(버전 코드 406018) [4] |
| NQ Vault | — | `SystemAndroid/Data/` 아래. 이름이 `322w465ay423xy11` 인 SQLite DB 와, 경로에 `.image`·`.video` 가 들어간 `.bin` 파일 [6] | 모듈에 적힌 것 없음 |
| Vaulty | `databases/media.db`, `shared_prefs/com.theronrogers.vaultyfree_preferences.xml` [9] | media.db 의 `_data` 열이 가리키는 곳 [9] | 모듈에 적힌 것 없음 |
| Private Photo Vault | `databases/ppv.db`(와 `ppv.db-wal`), `shared_prefs/APP_PREFERENCES.xml` [10] | ppv.db 의 file_path·thumbnail_path 열이 가리키는 곳 [10] | Pixel 7a, Android 14 [10] |
| Playground AppLocker | `shared_prefs/` 아래 설정 파일 [11] | `applocker/vault/` [11] | 모듈에 적힌 것 없음 |
| AppLock (DoMobile) | `databases/domobile_elock.db` [5] | 앱 데이터 폴더 `files/Medias/Photos` 와 공용 저장 공간 `.do0mo7bi1le1/medias` 두 곳 [5] | 에뮬레이터 Android 15, 앱 6.3.3 [5] |
| HideX | `databases/hidex.db` [12] | — | 모듈에 적힌 것 없음 |

GalleryVault 는 버전마다 DB 모양이 다릅니다. file_v1 표의 delete_state 열은 없는 판이 있고, export_unhidden_history 표는 버전 코드 40309 에는 없었습니다 [4]. 다른 앱도 판이 바뀌면 표와 열이 바뀔 수 있으니, 열 이름은 `PRAGMA table_info` 로 먼저 확인합니다. 삼성 갤러리의 숨긴 앨범은 제조사 기본 기능이라서 [삼성 갤러리](../media/samsung-gallery.md) 페이지에서, 삼성 보안 폴더는 [보안 폴더와 작업 프로필 (Secure Folder·Work Profile)](../../01-foundations/security-model/secure-folder-work-profile.md) 페이지에서 다룹니다.

## 구조

### 계산기 모양 볼트

Calculator Lock 의 `note_contact.db` 는 암호화하지 않은 SQLite 이고, 숨긴 파일 말고도 메모·연락처·브라우저 기록을 따로 담습니다 [3].

| 표 | 열 | 담긴 것 |
|---|---|---|
| Hide | hide_name, hide_path | 보관함 폴더 안의 파일 이름과 경로 문자열. 시험 이미지에서는 hide_path 가 `Download/Imgur` 아래 경로였음 [3] |
| Note | note_id, note_title, note_data, note_date | 보관함 안 메모 [3] |
| Contact | contact_id, contact_name, contact_number | 보관함 안 연락처. 시각 열 없음 [3] |
| File | file_id, file_title, file_path, file_org_path, file_extend, file_date | 보관한 문서 파일 [3] |
| Delete_Data | delete_name, delete_date | 보관함 휴지통과 관련된 것으로 보이는 기록 [3] |
| History | history_id, history_name, history_url, history_image, history_date | 앱 안 브라우저 기록으로 보이는 표 [3] |

시험 이미지에서 Hide 표의 hide_name 과 같은 이름의 파일이 `Pictures/.Calculator_Lock/Photos` 에 있었고, 그 파일은 암호화하지 않은 JPEG 였습니다 [3]. 설정 파일에는 설정 화면에서 켜고 끄는 `TAKE_PICTURE` 항목이 있고, 앱 안에 TakePictureActivity 와 Intruder 폴더도 있어서 침입자 사진 기능과 관련된 항목일 가능성이 있습니다 [3].

HLD 볼트는 모양이 다릅니다. 공용 저장 공간 `.privacy_safe/db/privacy_safe.db` 가 SQLCipher 로 암호화된 색인이라서 일반 SQLite 도구로는 열리지 않고, 설정 파일 `share_privacy_safe.xml` 은 항목 이름과 문자열 값이 모두 16진수 암호문으로 적혀 있습니다 [7]. 색인에는 FILE_INFO 표(ORIGIN_NAME, ORIGIN_PATH, ENCRYPT_NAME, ENCRYPT_PATH, ADD_TIME, CREATE_TIME, IS_MOCK_SPACE, THUMBNAIL 등)와 앨범 목록 SAFE_BOX 표가 있고, NOTE, BOOKMARK, HIDE_APP, LOCK_APP, INTRUDER_SHOOT 표도 있습니다 [7]. ORIGIN_ 열은 파일을 가져온 곳이고 ENCRYPT_ 열은 앱이 그 자리에 쓴 이름과 경로입니다 [7].

### 갤러리 볼트

GalleryVault 는 숨긴 파일마다 공용 저장 공간 `.galleryvault_` 폴더 아래 `files/` 에 객체 파일 하나를 둡니다 [4]. 객체의 앞 2803바이트는 가짜 PNG 이고, 그 뒤에 원래 파일의 나머지 부분이 오고, 끝에 `>>tyfs>>` 와 `<<tyfs<<` 로 둘러싼 꼬리 부분이 붙습니다 [4]. 꼬리 부분에는 원래 파일의 앞부분, 원래 크기, 원래 이름과 만든 시각을 담은 JSON 이 암호화돼 들어 있습니다 [4]. 파일 이름은 UUID 이고, `_t` 로 끝나는 것은 섬네일입니다 [4].

앱 DB `galleryvault.db` 에서 볼 표는 아래와 같습니다 [4].

| 표 | 주요 열 | 담긴 것 |
|---|---|---|
| file_v1 | added_time_utc, file_last_modified_time_utc, name, original_path, mime_type, file_size, uuid, source, delete_state | 숨긴 파일과 가져온 경로 |
| folder_v1 | create_time_utc, name, folder_type, child_file_count | 폴더. folder_type 은 -1 휴지통, 1 공유로 받음, 2 내려받음, 3 카메라, 4 복원, 0 은 기본 폴더 이름과 맞지 않는 값 |
| recycle_bin_v1 | delete_time, file_id | 볼트 안 휴지통 |
| export_unhidden_history | action_time, create_time, name, action_type, target_path, original_path | 볼트에서 다시 꺼낸 기록과 꺼내 놓은 경로 |
| break_in_report | timestamp, wrongly_attempt_code, locking_type, photo_path, location_latitude, location_longitude, address | 잠금 해제 실패 기록 |
| browser_history, web_url, download_task | last_visit_time_utc, url, local_path 등 | 앱 안 브라우저 |

공용 저장 공간의 `backup/file_action_log.db` 에는 file_action 표(action_time, action_type, file_path)가 있어서, 앱 데이터 폴더 밖에도 파일 동작 기록이 남습니다 [4]. `BreakInReports` 폴더의 사진은 `PS_20260115_213045.jpg`(만든 예시)처럼 촬영 날짜와 시각을 이름에 담습니다 [4].

NQ Vault 는 hideimagevideo 표에 원래 경로(file_path_from), 원래 이름(file_name_from), 볼트 안 경로(file_path_new), 시각(time)을 적고, 앨범 이름은 albums·albumstemp 표에 둡니다 [6]. 볼트 안 파일은 `.bin` 확장자로 바뀌어 있어 확장자나 파일 앞 시그니처만으로는 사진인지 알기 어렵습니다 [6]. Vaulty 는 media.db 의 Media 표에 원래 경로(path)와 볼트 안 경로(_data)를 두고 [9], Private Photo Vault 는 ppv.db 의 MediaFile 표에 file_path, thumbnail_path, mime_type, 가로·세로 크기, is_deleted, view_count 를 둡니다 [10]. Private Photo Vault 가 보관한 파일은 알려진 이미지 시그니처로 시작하지 않습니다 [10]. Playground AppLocker 의 `applocker/vault/` 파일은 이름에 `EIF`·`EVF` 뒤로 숫자가 붙고, ALEAPP 은 이 숫자를 파일을 암호화한 시각(유닉스 밀리초)으로 읽습니다 [11].

### 앱 잠금 앱

앱 잠금 목록은 대개 패키지 이름 한 열로 된 표입니다.

| 앱 | 파일과 표 | 열 |
|---|---|---|
| AppLock (DoMobile) | `domobile_elock.db` 의 lock | pname, type [5] |
| GalleryVault | `AppLock.db` 의 locked_app, break_in_report_in_applock | package_name, disguise_lock / timestamp, package_name, wrongly_attempt_code, photo_path [4] |
| HideX | `hidex.db` 의 p_lock_app | id, packageName, isActive [12] |

AppLock 의 `domobile_elock.db` 에는 locks 라는 비슷한 이름의 표도 있지만, 시험 기기에 설치되지 않은 패키지까지 들어 있어 잠금 목록으로 보지 않습니다 [5]. AppLock 은 볼트 기능도 있어서 SMediaTable 표에 uid, dateToken, lastTime, name, albumName, mimeType, srcPath(원래 경로), srcMd5, fileSize 를 적습니다 [5]. 시험 기기에서는 숨긴 파일 3개가 원래 경로에서 모두 사라졌고, 앱 데이터 폴더 `files/Medias/Photos` 에 uid 이름으로 원본과 같은 파일이 남아 있었습니다 [5]. 이 사본의 MD5 는 srcMd5 열 값과 같았습니다 [5]. 공용 저장 공간 `.do0mo7bi1le1/medias` 의 두 번째 사본은 16바이트 머리 뒤로 알아볼 수 없는 데이터가 이어졌습니다 [5].

## 증거로서 의미

**증명하는 것**

볼트 앱 DB 에 행이 있으면 그 앱으로 파일을 보관함에 넣은 기록이 있다는 뜻이고, 원래 경로 열(original_path, hide_path, srcPath, ORIGIN_PATH, file_path_from, path)로 그 파일이 원래 어느 폴더에 있었는지 알 수 있습니다 [3][4][5][6][7][9]. 원래 경로가 `DCIM/Camera` 면 기기로 찍은 사진, `Download` 면 내려받은 파일일 가능성이 있어서 출처를 좁히는 데 씁니다. GalleryVault 의 export_unhidden_history 는 볼트에서 파일을 다시 꺼낸 기록이고 [4], break_in_report 는 잠금 해제에 실패한 시각과 입력한 값, 그때 찍은 사진의 경로를 담습니다 [4]. 앱 잠금 표에 패키지가 있으면 그 앱이 잠금 목록에 들어 있다는 뜻입니다 [5].

**증명하지 못하는 것**

누가 파일을 숨겼는지는 기록에 없습니다. 앱 잠금 목록에 패키지가 있다고 그 앱을 열 때 실제로 잠금 화면이 떴다는 뜻은 아니고, AppLock 의 lock 표에는 목록에 넣은 시각도 없습니다 [5]. 가짜 공간 표시(IS_MOCK_SPACE, `albums_decoy`)는 저장된 값만 보여 주므로, 이 값만으로 사용자가 가짜 공간을 썼다고 단정하지 않습니다 [7][10]. 표가 비어 있다고 기능을 쓴 적이 없다는 뜻도 아닙니다. GalleryVault 는 file_v1 표가 비어 있어도 공용 저장 공간에 객체 파일이 남아 있을 수 있습니다 [4].

보고서에는 "이 앱의 DB 에 원래 경로가 DCIM/Camera 인 사진 12건이 보관함으로 옮겨진 기록이 있고, 그 가운데 9건의 객체 파일이 공용 저장 공간에 남아 있다"(만든 예시)처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

볼트 앱의 시각 값은 앱마다 단위와 기준이 다르고, 같은 표 안에서도 다를 수 있습니다.

| 앱 | 값 | 단위·기준 |
|---|---|---|
| GalleryVault | `_utc` 로 끝나는 열, timestamp, action_time, delete_time, `Kidd.xml` 의 시각 항목 | 유닉스 밀리초, UTC [4] |
| GalleryVault | BreakInReports 파일 이름 | 시간대 표시 없음. 기기 현지 시각일 가능성이 있음 [4] |
| AppLock | SMediaTable.lastTime (숨긴 시각) | 유닉스 밀리초, UTC [5] |
| AppLock | SMediaTable.dateToken (미디어 날짜) | 기기 현지 시각을 에포크 값 자리에 넣은 값. UTC 로 읽으면 시간대 차이만큼 어긋남 [5] |
| HLD 볼트 | FILE_INFO.ADD_TIME, CREATE_TIME | 기기 현지 시각 문자열, 시간대 표시 없음 [7] |
| Calculator Lock | note_date, file_date, delete_date, history_date | `dd-MM-yyyy` 또는 `dd/MM/yyyy` 문자열, 시각·시간대 없음 [3] |
| Vaulty | Media.date_added / date_modified | 초 / 밀리초 [9] |
| NQ Vault | hideimagevideo.time | 밀리초 [6] |
| Private Photo Vault | MediaFile.creation_date / installDate, lastKeyEventDate | ISO 8601 문자열 / 밀리초 [10] |
| Playground AppLocker | 파일 이름의 EIF·EVF 뒤 숫자 | 밀리초 [11] |

Vaulty 는 열 이름과 담긴 값이 어긋날 수 있습니다. ALEAPP 은 한 분석 글을 따라 date_added 를 파일을 만든 시각(초), date_modified 를 볼트에 넣은 시각(밀리초)으로 읽는데, 이 해석은 그 글 하나에서 나온 것이라 실제 데이터에서 두 열 값을 원래 파일의 촬영 시각과 맞춰 보고 씁니다 [9]. 현지 시각으로 적힌 값은 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 에서 그 무렵 기기 시간대를 확인한 뒤 UTC 로 바꿉니다. 시각 값 일반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

보관함 폴더 속 파일의 수정 시각은 숨긴 시각이 아닐 수 있습니다. 같은 볼륨 안에서 옮기면 파일 수정 시각이 그대로 남을 수 있어서, Calculator Lock 폴더 파일의 수정 시각으로는 파일이 보관함에 들어간 때를 정하지 않습니다 [3].

## 함정과 한계

첫째, 볼트 앱의 기록은 앱 데이터 폴더와 공용 저장 공간에 나뉘어 있습니다. 앱 데이터 폴더를 얻지 못한 수집에서도 공용 저장 공간의 보관함 폴더는 볼 수 있고, 반대로 앱을 지운 뒤에도 공용 저장 공간 폴더가 남을 수 있습니다. 지운 앱의 흔적을 찾는 순서는 [지운 앱이 남긴 흔적 (Uninstalled Apps)](../../03-techniques/analysis/app-data-analysis/uninstalled-apps.md) 에 있습니다.

둘째, 보관함 폴더와 파일은 점으로 시작하는 이름이 많아서 일반 파일 목록에서 숨김 파일로 보일 수 있습니다. 수집할 때 숨김 파일까지 포함했는지 확인합니다.

셋째, 파일 앞 시그니처만 보고 파일 종류를 정하면 틀릴 수 있습니다. GalleryVault 객체는 가짜 PNG 로 시작하고 [4], NQ Vault 와 Private Photo Vault 파일은 알려진 시그니처로 시작하지 않습니다 [6][10]. 반대로 Calculator Lock 처럼 원본 그대로 두는 앱도 있습니다 [3].

넷째, DB 행과 파일이 늘 짝을 이루지는 않습니다. DB 에만 있는 행, 폴더에만 있는 파일을 모두 따로 적습니다 [3][4]. 원래 경로에서 파일이 사라졌다는 사실은 MediaStore 기록과 맞춰 볼 수 있고, 그 방법은 [미디어 저장소 (MediaStore)](../media/mediastore/index.md) 페이지에 있습니다.

다섯째, 한 기기에 사용자가 여럿이면 사용자마다 앱 데이터가 따로 있습니다 [4][10]. 사용자 번호별 폴더를 모두 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

1. 추출본에서 `.Calculator_Lock`, `.privacy_safe`, `.galleryvault_`, `.do0mo7bi1le1`, `SystemAndroid` 같은 폴더 이름으로 찾고, 점으로 시작하는 폴더 전체의 목록도 따로 만듭니다.
2. 보관함 파일 몇 개를 헥스 편집기로 열어 앞 16바이트를 봅니다. `FF D8 FF` 로 시작하면 JPEG 원본 그대로이고, `89 50 4E 47` 로 시작하면 PNG 입니다. `.galleryvault_` 폴더 파일이 PNG 로 시작하면 파일 끝 쪽에서 ASCII `>>tyfs>>` 를 찾아 GalleryVault 객체인지 확인합니다 [4].
3. `privacy_safe.db` 처럼 DB 로 보이는 파일의 앞 16바이트가 `SQLite format 3` 이 아니면 암호화된 DB 로 적습니다 [7].

### 공개 도구로 한 번

ALEAPP 은 이 페이지의 앱마다 모듈이 있어서 [3]–[12], 추출본을 넣으면 앱 DB 의 표를 시각 열과 함께 보여 줍니다. 모듈이 없는 판이거나 열 이름이 다르면 SQLite 도구로 직접 엽니다.

```
sqlite3 galleryvault.db "PRAGMA table_info(file_v1);"
sqlite3 galleryvault.db "SELECT added_time_utc, name, original_path FROM file_v1 ORDER BY added_time_utc;"
```

설정 XML 의 읽는 법은 [설정 XML과 SharedPreferences](../../01-foundations/data-formats/shared-preferences.md), SQLite 에서 지운 행을 찾는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [설치된 앱 (packages.xml)](../app-usage/packages/index.md) | 볼트 앱 설치 시각, 아이콘 위장용 컴포넌트 상태 |
| [미디어 저장소 (MediaStore)](../media/mediastore/index.md) | 원래 경로의 파일이 MediaStore 에 남아 있는지 |
| [섬네일 캐시 (Thumbnails)](../media/thumbnails.md) | 숨기기 전 사진의 작은 사본이 남아 있는지 |
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | 숨긴 시각 무렵 볼트 앱이 화면에 올라왔는지 |
| [최근 앱 화면 (Recents·Snapshots)](../app-usage/recents-snapshots.md) | 볼트 앱 화면이 캡처돼 남아 있는지 |
| [구글 플레이 기록 (Play Store)](../app-usage/play-store.md) | 볼트 앱을 내려받은 기록 |

앱을 지운 경우는 [앱 지우기](../../04-scenarios/activity/anti-forensics/app-removal.md), 파일을 지운 경우는 [메시지·사진 지우기](../../04-scenarios/activity/anti-forensics/content-deletion.md) 시나리오에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 이미지나 볼트 앱을 설치해 만든 시험 이미지에서 아래 질문을 풀어 봅니다.

1. 설치된 앱 목록에 위 표의 패키지가 있습니까? 없다면 공용 저장 공간에 점으로 시작하는 보관함 폴더가 있습니까?
2. 볼트 앱 DB 에서 원래 경로 열을 모으면 어느 폴더에서 가져온 파일이 가장 많습니까?
3. DB 에 있는 파일 가운데 보관함 폴더에 실제로 남은 것은 몇 개이고, 폴더에만 있는 파일은 몇 개입니까?
4. 시각 열마다 단위와 시간대를 정하고 UTC 로 바꾸면, 숨긴 시각이 다른 사건 시각과 얼마나 떨어져 있습니까?
5. 잠금 해제 실패 기록이나 침입자 사진이 있습니까? 있다면 그 시각은 언제입니까?

## 참고 문헌

1. Xiaolu Zhang, Ibrahim Baggili, Frank Breitinger, "Breaking into the vault: Privacy, security and forensic analysis of Android vault applications", Computers & Security 70, pp. 516–531, 2017. DOI: 10.1016/j.cose.2017.07.011, https://www.sciencedirect.com/science/article/abs/pii/S0167404817301529
2. 이신영·김한결·박명서, "안드로이드 환경에서의 앱 잠금 애플리케이션 분석: 암호화 및 복호화 방법에 대한 연구", 디지털포렌식연구 17권 4호, pp. 17–27, 2023. DOI: 10.22798/KDFS.2023.17.4.17, https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART003043385
3. ALEAPP — scripts/artifacts/calculatorLockVault.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/calculatorLockVault.py
4. ALEAPP — scripts/artifacts/galleryVault.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/galleryVault.py
5. ALEAPP — scripts/artifacts/appLock.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/appLock.py
6. ALEAPP — scripts/artifacts/NQ_Vault.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/NQ_Vault.py
7. ALEAPP — scripts/artifacts/hldPrivacySafe.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/hldPrivacySafe.py
8. ALEAPP — scripts/artifacts/appLockerfishingnet.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/appLockerfishingnet.py
9. ALEAPP — scripts/artifacts/vaulty_files.py, vaulty_info.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/vaulty_files.py , https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/vaulty_info.py
10. ALEAPP — scripts/artifacts/PrivatePhotoVault.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/PrivatePhotoVault.py
11. ALEAPP — scripts/artifacts/playgroundVault.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/playgroundVault.py
12. ALEAPP — scripts/artifacts/HideX.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/HideX.py
13. `<activity-alias>` — Android Developers, https://developer.android.com/guide/topics/manifest/activity-alias-element
