---
title: "미디어 저장소"
parent: "아티팩트 · 사진·미디어"
nav_order: 620
has_children: true
has_toc: false
---

# 미디어 저장소 (MediaStore)

미디어 저장소(MediaStore)는 공용 저장 공간의 사진·동영상·오디오·문서를 시스템 쪽 제공자(MediaProvider)가 볼륨마다 SQLite DB 로 색인해 두는 곳이고, 외부 볼륨 DB 인 external.db 의 files 표 하나에 파일 경로, 넣은 앱, 여러 시각, 휴지통 상태가 함께 적힙니다 [1][2].

## 왜 중요한가

사진이 언제 저장됐는지, 어느 앱이 넣었는지, 지금은 휴지통에 있는지 같은 질문에 파일 하나하나를 열지 않고 한 표에서 답할 수 있어서, 미디어 조사를 시작할 때 먼저 보는 기록입니다. 이 제공자의 권한(authority) 이름은 "media" 이고 [2], 이미지·오디오·동영상·다운로드 목록이 모두 files 표 위에 만든 보기라서 [1] 카메라로 찍은 사진뿐만 아니라 Download 폴더에 내려받은 파일까지 같은 표에서 봅니다.

다만 files 표에는 초 단위 시각과 밀리초 단위 시각이 섞여 있고, 시각이 아닌 세대 번호(generation) 열도 있어서 열마다 뜻을 알고 읽어야 합니다. 지운 사진은 휴지통으로 옮긴 경우와 바로 지운 경우에 남는 흔적이 크게 다르고, 삼성 기기에는 AOSP 와 별도로 삼성 미디어 제공자와 휴지통 제공자의 DB 가 따로 있습니다 [3]. 두 하위 페이지가 이 차이를 나눠 다룹니다.

## 한눈에 보기

| 위치 | Android 버전 | 알려 주는 것 |
|---|---|---|
| MediaProvider 의 external.db (기기 안 경로는 실제 기기에서 확인) | 현행 AOSP 기준 | files 표의 경로·크기·종류·넣은 앱·시각·대기와 휴지통 상태, 지웠거나 안 보이게 된 이미지·동영상의 옛 번호(deleted_media) |
| MediaProvider 의 internal.db | 현행 AOSP 기준 | 내부 볼륨의 미디어 색인 |
| `*/com.samsung.android.providers.media/databases/media.db*` | ALEAPP 시험 자료 Android 10·11·13·14·15 (삼성) | 삼성 미디어 제공자의 files·location 표 |
| 삼성 휴지통 제공자와 삼성 갤러리의 휴지통 DB | ALEAPP 시험 자료 Android 10·13·14·15 (삼성) | 원래 경로, 지운 앱, 지운 시각 |
| 공용 저장 공간의 `.trashed-` 파일 | 현행 AOSP 기준 | 휴지통에 들어간 파일 본체와 만료 시각 |

`/sdcard` 최상위에는 Alarms, Android, Audiobooks, DCIM, Documents, Download, Movies, Music, Notifications, Pictures, Podcasts, Recordings, Ringtones 같은 폴더가 있습니다. external.db 가 기기 안 어느 경로에 있는지, adb 일반 셸 권한으로 그 파일을 읽을 수 있는지는 실제 기기에서 확인해야 합니다.

## 읽는 순서

1. [미디어 DB 구조 (external.db)](external-db.md) — 표와 보기, files 표의 열과 시각 단위, `_modifier` 와 generation 번호, 스키마 버전 번호, 보안 폴더 같은 두 번째 사용자의 DB, 삼성 media.db 를 다룹니다.
2. [지운 사진의 흔적 (Deleted Media)](deleted-media.md) — 휴지통 표시와 `.trashed-` 파일 이름, 만료 항목 정리와 만료 시각 연장, deleted_media 표, 바로 지운 경우, 삼성 휴지통 제공자와 갤러리 휴지통을 다룹니다.

## 함께 볼 페이지

- [카메라 사진과 메타데이터 (DCIM·EXIF)](../dcim-exif.md), [섬네일 캐시 (Thumbnails)](../thumbnails.md), [스크린샷과 화면 녹화](../screenshots.md) — 색인된 파일 자체와 그 사본
- [삼성 갤러리 (Samsung Gallery)](../samsung-gallery.md), [구글 포토 (Google Photos)](../google-photos.md) — 같은 사진을 앱 쪽에서 남기는 기록
- [공용 저장 공간 (Shared Storage·/sdcard)](../../../01-foundations/storage/shared-storage.md), [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md), [시각 값](../../../01-foundations/value-decoding/time-values.md), [패키지 이름과 UID](../../../01-foundations/value-decoding/package-uid.md) — DB 를 직접 읽을 때 필요한 기초
- [보안 폴더와 작업 프로필](../../../01-foundations/security-model/secure-folder-work-profile.md), [사용자와 프로필](../../system-account/users-profiles.md) — 사용자마다 따로 생기는 미디어 DB
- [이 사진은 언제 어디서 찍었나 (Photo Origin)](../../../04-scenarios/activity/photo-origin.md), [지운 대화와 사진 찾기 (Deleted Content)](../../../04-scenarios/activity/deleted-content.md), [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) — 이 기록을 쓰는 시나리오와 기법

## 참고 문헌

1. AOSP MediaProvider — DatabaseHelper.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/DatabaseHelper.java
2. AOSP MediaProvider — apex/framework/java/android/provider/MediaStore.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/apex/framework/java/android/provider/MediaStore.java
3. ALEAPP (커밋 c044fe5) — scripts/artifacts/samsungMediaProvider.py, SamsungTrash.py, galleryTrash.py, https://github.com/abrignoni/ALEAPP/tree/main/scripts/artifacts
