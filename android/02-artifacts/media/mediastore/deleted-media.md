---
title: "지운 사진의 흔적"
parent: "미디어 저장소"
grand_parent: "아티팩트 · 사진·미디어"
nav_order: 640
---

# 지운 사진의 흔적 (Deleted Media)

사진이나 동영상을 지울 때 미디어 저장소(MediaStore)와 삼성 기기의 휴지통 기록에 무엇이 남는지 정리합니다. AOSP 쪽 내용은 MediaProvider 저장소의 main 가지 소스로 확인한 "현행 AOSP 기준" 이고, 삼성 쪽 내용은 ALEAPP 의 파서와 그 설명에서 가져왔습니다. files 표의 칸과 시각 단위 전반은 [미디어 DB 구조](external-db.md) 페이지에 있습니다.

## 한 줄 요약

미디어를 휴지통으로 옮기면 files 행이 남은 채 is_trashed=1 과 만료 시각이 적히고 파일은 같은 폴더에서 `.trashed-` 로 시작하는 이름으로 바뀌지만, 바로 지우면 files 행이 사라지고 이미지·동영상이라면 deleted_media 표에 옛 번호와 세대 번호만 남습니다 [2][3][4].

## 무엇을 기록하나 · 왜 생기나

미디어를 지우는 길은 두 가지입니다. 하나는 휴지통으로 옮기는 것이고, 이때 MediaProvider 는 행을 지우지 않고 표시만 바꾼 뒤 만료 시각이 지나면 정리합니다. 다른 하나는 바로 지우는 것이고, 이때는 files 행이 사라집니다 [2][3][5].

앱이 다른 앱이 넣은 미디어를 휴지통에 넣거나 지우려면 사용자 확인 창을 거쳐야 합니다. MediaStore.createTrashRequest() 와 createDeleteRequest() 가 그 확인 창을 띄우는 PendingIntent 를 만듭니다 [5]. 이 두 함수가 몇 번 API 부터 있는지는 이번에 확인하지 못했습니다.

삼성 기기에는 이와 별도로 삼성 휴지통 제공자와 삼성 갤러리가 각자 휴지통 기록을 둡니다 [6]. 그래서 삼성 기기에서 지운 사진을 찾을 때는 AOSP external.db 한 곳만 보지 않습니다.

## 위치와 버전별 차이

| 흔적 | 위치 | 근거 |
|---|---|---|
| is_trashed·date_expires 칸 | external.db 의 files 표 | 현행 AOSP 기준, 스키마 1010 단계에서 생김 [1] |
| 이름이 바뀐 휴지통 파일 | 원래 파일과 같은 폴더의 `.trashed-...` 파일 | 현행 AOSP 기준 [3] |
| deleted_media 표 | external.db | 현행 AOSP 기준, 스키마 1301 단계에서 생김 [1] |
| 삼성 휴지통 제공자 DB | `*/com.samsung.android.providers.trash/databases/trash.db*` | ALEAPP 검체 Android 14·15 [6] |
| 삼성 휴지통 제공자 파일 | `*/data/media/*/Android/.Trash/*`, `*/storage/*/Android/.Trash/*` | ALEAPP 파서의 경로 패턴 [6] |
| 삼성 갤러리 휴지통 DB | `*/data/com.sec.android.gallery3d/databases/local.db` 의 trash 표 | ALEAPP 검체 5개에서 모두 0행 [6] |
| 삼성 갤러리 휴지통 파일 | `*/data/com.sec.android.gallery3d/files/.Trash/**` | ALEAPP 파서의 경로 패턴 [6] |

스키마 단계 번호를 Android 버전으로 옮기는 문제는 [미디어 DB 구조](external-db.md) 페이지의 "스키마 버전" 절에 있습니다. 삼성 휴지통 제공자가 One UI 몇 버전부터 있는지, 요즘 삼성 갤러리가 local.db 의 trash 표 대신 이 제공자를 쓰는지는 확인하지 못했습니다.

관찰한 기기의 `/sdcard/Android` 목록에는 data, media, obb 만 보였고 .Trash 는 보이지 않았습니다. 다만 이 목록이 점으로 시작하는 숨김 항목까지 나열한 결과인지 관찰 메모에 적혀 있지 않아서, 이 기기에 .Trash 가 없다고 결론 낼 수는 없습니다. 같은 기기의 global 설정에 contact_setting_trash_bin_on 키가 있었지만, 이름으로 보아 연락처 휴지통 설정이고 사진 휴지통과의 관계는 확인하지 못했습니다.

## 구조

### MediaStore 휴지통

휴지통에 넣으면 files 행은 그대로 남고 is_trashed 가 1, date_expires 가 "지금 + 30일" 의 유닉스 초가 됩니다. 휴지통에서 꺼내면 date_expires 는 NULL 이 됩니다 [3]. 앱이 date_expires 를 직접 정할 수는 없는데, computeDateExpires 가 앱이 넣은 값을 지우기 때문입니다 [3].

파일 쪽에서는 같은 폴더 안에서 이름이 바뀝니다. 휴지통 파일은 `.trashed-<date_expires 초>-<원래 파일 이름>`, 대기 항목은 `.pending-<초>-<이름>` 모양이고, 이름이 길면 잘라내기(trimFilename) 때문에 휴지통에서 꺼낸 뒤 파일 이름이 원래와 다를 수 있다고 소스 주석이 적습니다 [3]. 거꾸로 파일 이름이 `.trashed-<숫자>-<이름>` 모양이면 MediaProvider 는 그 파일을 is_trashed=1, date_expires=숫자, `_display_name`=이름 으로 색인합니다(정규식 PATTERN_EXPIRES_FILE, 대소문자 무시) [3]. 그래서 DB 가 없어도 파일 이름에서 만료 시각과 원래 이름을 읽을 수 있습니다.

앱이 조회할 때 휴지통·대기 항목은 기본으로 빠지고, 포함하려면 QUERY_ARG_MATCH_TRASHED("android:query-arg-match-trashed") 에 MATCH_INCLUDE(1) 이나 MATCH_ONLY(3) 를 줘야 합니다 [5][2]. 앱 화면이나 앱을 거친 조회에 사진이 안 보여도 files 표에는 휴지통 행이 남아 있을 수 있다는 뜻입니다.

### 만료 항목 정리

MediaProvider 는 유휴 유지보수 때 외부 볼륨에서 date_expires 가 지금(초)보다 작은 항목을 찾아, 만료된 지 1주일 안인 항목은 지우고 1주일이 넘은 항목은 지우지 않고 만료 시각을 지금 + 7일(DEFAULT_DURATION_EXTENDED)로 늦춥니다. 늦출 때는 파일 이름도 새 만료 시각으로 바꿉니다. 시간대 자료가 틀려 데이터를 잃는 일을 막으려는 동작이라고 소스 주석이 적습니다 [2][3]. 마운트되지 않은 볼륨의 만료 항목은 오래된 볼륨 정보를 정리할 때 지운다고 주석이 적습니다 [2].

### deleted_media 표

칸은 `_id`(AUTOINCREMENT), old_id(INTEGER UNIQUE), generation_modified(INTEGER NOT NULL) 셋뿐입니다 [1]. 외부 볼륨 DB 에서만 쓰고 이미지·동영상 행만 대상입니다 [4].

files 행이 지워지면 그 행의 `_id` 가 old_id 로, 그때의 generation 번호가 generation_modified 로 들어갑니다 [4][2]. 행이 지워지지 않아도 "보이는 미디어" 가 "안 보이는 미디어" 로 바뀌면 들어가는데, 보이는 미디어는 휴지통 아님·대기 아님·이미지나 동영상인 행이라서 휴지통에 넣을 때도 기록됩니다 [4]. 다시 보이게 되면(휴지통에서 꺼냄 등) 그 old_id 행은 표에서 지워지고, 같은 old_id 가 다시 들어오면 새 행을 만들지 않고 generation_modified 만 새 값으로 바꿉니다 [4].

이 표는 사진 선택기(PhotoPicker)가 마지막 동기화 이후 사라진 항목을 알아내려고 쓰고, queryDeletedMedia 는 generation_modified 가 기준값보다 큰 old_id 를 돌려줍니다 [4]. 파일 이름·경로·시각은 이 표에 없고, 이 표의 행이 언제 정리되는지도 확인하지 못했습니다.

### 바로 지운 경우

files 행이 지워지면(files_delete 트리거) MediaProvider 는 URI 권한 회수, 썸네일 무효화, 오디오면 재생목록 항목 제거, 사진 선택기 알림(deleted_media 기록), DB 백업 기록에서 빼기를 합니다. 외부 기본 볼륨(external_primary)이고 백업·복원 기능이 켜져 있으면 그 경로의 백업 기록도 지웁니다(deleteBackupForPath) [2].

MediaProvider 는 다음 행 번호(next row id)와 DB 세션 ID 를 `/data/media/0` 디렉터리의 확장 속성(xattr)에 저장하고, 작업 프로필은 `/data/media/<사용자ID>` 에 권한이 없어서 `/data/media/0` 을 쓴다고 주석이 적습니다 [1]. files 표의 `_id` 는 AUTOINCREMENT 라 지운 번호를 다시 쓰지 않으니, `_id` 번호 사이의 빈 곳은 지운 행이 있었다는 단서가 될 수 있습니다 [1]. 이것을 실제 사례로 확인한 자료는 이번에 열지 않았습니다.

### 삼성 휴지통 제공자 (trash.db)

trashes 표의 칸은 다음과 같습니다 [6].

| 칸 | 뜻(ALEAPP 기준) |
|---|---|
| `_id` | 행 번호 |
| `_data` | 지금 휴지통 안 경로 |
| original_path | 원래 경로 |
| title, `_display_name` | 제목과 표시 이름 |
| `_size`, mime_type | 크기와 종류 |
| delete_package_name | 지운 앱 |
| user_id | 사용자 번호 |
| date_deleted, date_expires | 지운 시각과 만료 시각 |
| extra | JSON |

ALEAPP 는 `_data` 에서 "/Android/.Trash/" 뒤의 부분으로 실제 휴지통 파일을 찾아 짝짓습니다 [6]. ALEAPP 검체에서는 Android 15 검체에 3행, Android 14 검체 둘에 0행과 29행이 있었습니다 [6].

### 삼성 갤러리 휴지통 (local.db)

trash 표의 칸은 `__deleteTime`, `__Title`, `__absPath`, `__originTitle`, `__originPath`, `__expiredPeriod`, `__restoreExtra` 이고, `__restoreExtra` 는 JSON 이라서 ALEAPP 는 그 안의 `__dateTaken`, latitude, longitude 를 꺼냅니다 [6]. `__expiredPeriod` 의 단위는 확인하지 못했습니다.

삼성 media.db 의 files 표에도 is_trashed, is_hide, deleted 칸이 있지만 ALEAPP 검체에서 값이 비어 있거나 0 이었고, 그 내용은 [미디어 DB 구조](external-db.md) 페이지의 "삼성 media.db" 절에 있습니다.

## 시각 해석

| 값 | 단위 | 뜻 |
|---|---|---|
| files.date_expires | 유닉스 초 | 휴지통 만료 시각(기본 넣은 시각 + 30일) [3] |
| `.trashed-` 파일 이름 속 숫자 | 유닉스 초 | 그 파일의 만료 시각 [3] |
| deleted_media.generation_modified | 세대 번호 | 시각이 아님 [4] |
| trash.db 의 date_deleted, date_expires | 유닉스 밀리초(ALEAPP 가 1000 으로 나눔) | 지운 시각, 만료 시각 [6] |
| local.db 의 `__deleteTime` | 유닉스 밀리초(ALEAPP 가 1000 으로 나눔) | 지운 시각 [6] |
| `__restoreExtra` 의 `__dateTaken` | 유닉스 밀리초 | 촬영 시각 [6] |

MediaStore 휴지통에는 "넣은 시각" 칸이 따로 없어서, 넣은 시각은 기본값 기준 "만료 시각 − 30일" 로 짐작할 뿐입니다. 만료 항목 정리가 만료 시각을 7일씩 늦추고 파일 이름도 바꾸기 때문에, 이름 속 숫자가 넣은 시각 + 30일과 맞지 않으면 이 연장이 한 번 이상 일어났을 수 있습니다 [2][3]. 보고서에는 "휴지통에 넣은 시각" 이 아니라 "만료 시각이 이 값으로 적혀 있다" 고 쓰고, 넣은 시각은 계산한 추정값이라고 밝힙니다. 삼성 쪽 두 DB 의 단위는 ALEAPP 의 변환 방식에서 읽은 것이고 삼성의 공개 문서로 확인한 것은 아닙니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| is_trashed=1 인 행이 있으면 그 파일이 MediaStore 휴지통 상태였다는 것 | 휴지통에 넣은 정확한 시각(만료 시각에서 거꾸로 짐작할 뿐) |
| `.trashed-` 파일이 있으면 그 파일이 휴지통 상태로 저장 공간에 남아 있다는 것 | 사용자가 직접 넣었는지, 어느 앱이 넣었는지 |
| deleted_media 에 old_id 가 있으면 그 번호의 이미지·동영상 행이 지워졌거나 안 보이게 됐다는 것 | 그 행의 파일 이름·경로·내용, 지웠는지 휴지통에 넣었는지의 구분 |
| trash.db 의 delete_package_name 이 적은 지운 앱 이름 | 그 앱을 사람이 조작했는지 |
| `_id` 사이의 빈 번호가 있으면 행이 지워졌을 가능성 | 빈 번호마다 지운 행이 미디어였다는 것 |

"사진을 지웠다" 보다 "files 표에 이 경로의 이미지가 is_trashed=1, 만료 시각 이 값으로 남아 있다" 나 "deleted_media 에 old_id 이 번호가 generation 이 값으로 남아 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 함정과 한계

- 앱을 거친 조회는 휴지통 항목을 기본으로 빼서 [5][2], 라이브 기기에서 앱 화면에 안 보인다고 files 표에도 없다고 판단하면 안 됩니다.
- deleted_media 에는 휴지통으로 옮긴 경우와 바로 지운 경우가 함께 들어가고, 휴지통에서 꺼내면 그 행이 사라집니다 [4]. 이 표만으로 삭제 여부를 가르지 말고 files 표에 같은 `_id` 가 남아 있는지 함께 봅니다.
- 휴지통 파일 이름은 잘릴 수 있어서 [3] 원래 이름과 한 글자씩 맞지 않을 수 있습니다.
- 지운 files 행이 SQLite 빈 페이지나 WAL 에 남는지는 확인하지 않았습니다. 레코드 복구는 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 페이지의 일반 방법을 따릅니다.
- 삼성 휴지통 제공자와 갤러리 휴지통의 칸 뜻과 단위는 ALEAPP 해석에 기대고 있고, ALEAPP 검체에서도 행이 없는 경우가 많았습니다 [6].

## 직접 분석해 보기

**파일 이름 읽기.** 소스 주석에 나오는 예 `/storage/emulated/0/DCIM/.trashed-1621147340-test.jpg` 를 따라가 봅니다 [3]. 이 값은 소스 주석의 예시이고 실제 검체에서 나온 값이 아닙니다.

```text
.trashed-1621147340-test.jpg
         └ 만료 시각(유닉스 초) 1621147340 = 2021-05-16 06:42:20 UTC
                    └ 원래 이름 test.jpg
기본값(30일)으로 거꾸로 계산한 넣은 시각 추정 = 2021-04-16 06:42:20 UTC
```

**external.db 쿼리.** 확보한 사본을 SQLite 를 읽는 공개 도구(예: sqlite3 명령줄)로 열어 휴지통 행, deleted_media 행, 빈 `_id` 번호를 차례로 봅니다. 아래 쿼리는 이 페이지의 칸 이름으로 만든 예시입니다.

```sql
-- 휴지통 행과 만료 시각
SELECT _id, _data, _display_name, owner_package_name,
       datetime(date_expires, 'unixepoch') AS expires_utc,
       datetime(date_expires - 30*86400, 'unixepoch') AS trashed_guess_utc
FROM files WHERE is_trashed = 1;

-- 지웠거나 안 보이게 된 이미지·동영상의 옛 번호
SELECT old_id, generation_modified FROM deleted_media ORDER BY generation_modified;

-- 뒤 번호가 없는 _id (빈 번호 구간의 시작 바로 앞)
SELECT _id FROM files f
WHERE NOT EXISTS (SELECT 1 FROM files g WHERE g._id = f._id + 1)
ORDER BY _id;
```

deleted_media 의 old_id 가운데 files 표에 같은 `_id` 가 is_trashed=1 로 남아 있는 것은 휴지통 항목이고, files 표에 아예 없는 것은 행이 지워진 항목으로 나눠 볼 수 있습니다. generation_modified 는 files 표의 generation 번호와 같은 수열이라서 앞뒤에 바뀐 다른 행과 비교해 대략의 순서를 잡습니다.

**공개 도구.** ALEAPP 의 SamsungTrash 와 galleryTrash 모듈이 삼성 휴지통 제공자와 삼성 갤러리 휴지통을 읽고, 밀리초 시각을 바꿔 보여 줍니다 [6]. 도구 결과의 원래 경로·지운 앱·시각을 trash.db 를 직접 연 값과 한 번 맞춰 봅니다.

## 교차 검증

- [섬네일 캐시](../thumbnails.md) — 원본을 지운 뒤에도 작은 사본이 남는지 봅니다.
- [삼성 갤러리](../samsung-gallery.md), [구글 포토](../google-photos.md) — 앱 쪽 휴지통과 동기화 기록을 봅니다.
- [앱 사용 기록](../../app-usage/usagestats/index.md) — delete_package_name 의 앱이나 갤러리 앱이 그 무렵 앞에 떠 있었는지 봅니다.
- [지운 대화와 사진 찾기](../../../04-scenarios/activity/deleted-content.md), [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) — 이 흔적을 쓰는 조사 시나리오입니다.

## 실습

공개 검체(NIST CFReDS 등)에서 Android 이미지를 구할 수 있으면 다음을 풀어 봅니다.

1. external.db 에서 is_trashed=1 인 행을 모두 찾고, 같은 폴더에 `.trashed-` 파일이 실제로 있는지, 이름 속 숫자와 date_expires 가 같은지 확인합니다.
2. 만료 시각 − 30일로 넣은 시각을 추정하고, 그 무렵의 앱 사용 기록과 맞는지 봅니다.
3. deleted_media 의 old_id 를 files 표와 맞춰 휴지통 항목과 바로 지운 항목으로 나눕니다.
4. 삼성 기기 검체라면 trash.db 의 original_path 와 delete_package_name 을 external.db 의 같은 파일 기록과 비교합니다.

## 참고 문헌

1. AOSP MediaProvider — DatabaseHelper.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/DatabaseHelper.java
2. AOSP MediaProvider — MediaProvider.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/MediaProvider.java
3. AOSP MediaProvider — util/FileUtils.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/util/FileUtils.java
4. AOSP MediaProvider — photopicker/data/ExternalDbFacade.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/src/com/android/providers/media/photopicker/data/ExternalDbFacade.java
5. AOSP MediaProvider — apex/framework/java/android/provider/MediaStore.java (main), https://android.googlesource.com/platform/packages/providers/MediaProvider/+/refs/heads/main/apex/framework/java/android/provider/MediaStore.java
6. ALEAPP (커밋 c044fe5) — scripts/artifacts/SamsungTrash.py, galleryTrash.py, https://github.com/abrignoni/ALEAPP/tree/main/scripts/artifacts
