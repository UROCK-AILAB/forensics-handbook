---
title: "삼성 갤러리"
parent: "아티팩트 · 사진·미디어"
nav_order: 680
---

# 삼성 갤러리 (Samsung Gallery)

## 한 줄 요약

삼성 기기의 기본 갤러리 앱(com.sec.android.gallery3d)은 앱 전용 폴더의 local.db 에 휴지통 기록을 두고, 숨긴 앨범(Hidden Album)을 쓰면 secured.db 와 sec_pass 폴더에 숨긴 사진의 원래 경로로 보이는 값과 기기 모델 이름으로 보이는 값 같은 기록을 남기는데, 두 곳 모두 삼성이 공개한 규격이 없어 공개 도구의 해석에 기대어 읽습니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

갤러리 앱은 MediaStore 가 색인한 사진을 보여 주는 앱이지만, 사진을 휴지통으로 보내거나 숨기는 기능은 앱이 따로 처리하고 자기 DB 에 적습니다. 휴지통 기록은 local.db 의 trash 표와 `.Trash` 폴더에 [1], 숨긴 앨범 기록은 secured.db 의 files 표와 sec_pass 폴더에 있습니다 [2]. 그래서 삼성 기기에서 사진이 "안 보이는" 이유를 찾을 때는 MediaStore 의 휴지통·숨김 표시와 함께 갤러리 앱의 이 두 기록을 봅니다.

삼성 기기에는 AOSP 의 external.db 와 따로 삼성 미디어 제공자(com.samsung.android.providers.media)의 media.db 가 있고, 그 표의 captured_url, captured_app, is_hide 같은 칸은 [미디어 DB 구조 (external.db)](mediastore/external-db.md) 페이지에 있습니다. 이 페이지는 갤러리 앱이 자기 폴더에 남기는 기록만 다룹니다.

## 위치와 버전별 차이

| 무엇 | 경로 패턴 | 근거 |
|---|---|---|
| 휴지통 DB | `*/data/com.sec.android.gallery3d/databases/local.db` 의 trash 표 | ALEAPP 경로 패턴 [1] |
| 휴지통 파일 | `*/data/com.sec.android.gallery3d/files/.Trash/**` | ALEAPP 경로 패턴 [1] |
| 숨긴 앨범 DB | `*/sec/gallery/secured/databases/secured.db` 의 files 표 | ALEAPP 경로 패턴, 사례 1건 [2] |
| 숨긴 앨범 미디어 | `*/data/sec_pass/*` | ALEAPP 경로 패턴, 사례 1건 [2] |

ALEAPP 는 Android 10·13·14·14·15 삼성 기기 검체에서 휴지통 모듈을 시험했고, 앱 버전 코드는 1450000033(Android 13), 1500100001(Android 14), 1550500003(Android 15) 이었습니다 [1]. 숨긴 앨범이 One UI 몇 버전부터 있는지, sec_pass 의 전체 경로가 어느 파티션·사용자 폴더 아래인지, 암호화돼 있는지는 공개된 자료가 없어 검체에서 확인합니다. 앱 전용 폴더의 위치는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 페이지에 있습니다.

## 구조

### 휴지통 (local.db)

trash 표의 칸, 시각 단위, `__restoreExtra` JSON 안의 촬영 시각·위치는 [지운 사진의 흔적](mediastore/deleted-media.md) 페이지의 "삼성 갤러리 휴지통" 절에 있습니다. `.Trash` 폴더의 파일은 파일 이름으로 trash 행과 짝지을 수 있습니다 [1]. ALEAPP 검체 5개에서는 trash 표가 모두 0행이었습니다 [1]. 요즘 갤러리가 이 표 대신 삼성 휴지통 제공자(com.samsung.android.providers.trash)를 쓰는지, `__expiredPeriod` 의 단위와 휴지통 보관 기간은 공개된 자료가 없어 검체에서 확인합니다.

### 숨긴 앨범 (secured.db)

secured.db 의 files 표에는 다음 칸이 있습니다 [2].

| 칸 | 이름으로 보이는 뜻 |
|---|---|
| date_added, date_modified, datetime | 시각 세 가지(단위 불명, 아래 "시각 해석" 참고) |
| `_data` | 숨긴 뒤의 파일 경로 |
| `_size`, `_display_name` | 크기, 표시 이름 |
| original_path | 숨기기 전 원래 경로 |
| captured_url | 공개 자료 없음 |
| cam_model | 촬영 기기 모델 |
| owner_package_name | 파일을 넣은 앱 |

오른쪽 뜻은 칸 이름에서 짐작한 것이고, 삼성이 공개한 문서나 소스는 없습니다. captured_url 은 삼성 media.db 에도 같은 이름의 칸이 있지만 무엇을 담는지는 공개된 자료가 없습니다.

ALEAPP 의 숨긴 앨범 모듈은 공유할 수 없는 사례 1건을 바탕으로 만들어졌고, 시험 자료는 칸 이름에 맞춘 합성 자료이며, 공개 검체에서는 이 저장소가 나온 적이 없습니다 [2]. secured.db 와 sec_pass 미디어는 숨긴 앨범이 잠금 해제된 상태에서 얻은 추출본에만 있었다는 제보가 있습니다 [2]. 그래서 이 칸 이름과 경로는 확정 규격이 아니라 한 사례에서 본 모양으로 다룹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| trash 행과 `.Trash` 파일이 있으면 그 사진을 갤러리 휴지통에 보냈다는 것 | 누가 보냈는지 |
| secured.db 에 행이 있으면 그 파일이 숨긴 앨범에 들어 있었다는 것 | 숨긴 시각(세 시각 칸 가운데 어느 것이 숨긴 시각인지 공개 자료 없음) |
| original_path 가 적은 숨기기 전 경로 | 그 경로의 파일을 이 기기에서 만들었다는 것 |
| cam_model 값 | 그 기기로 사진을 찍었다는 것(값의 출처에 대한 공개 자료 없음) |
| secured.db 가 없다는 것 | 숨긴 앨범을 쓰지 않았다는 것(잠금 해제 상태에서만 보였다는 사례가 있음) |

"사진을 숨겼다" 보다 "secured.db 의 files 표에 이 original_path 와 이 `_data` 의 행이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

secured.db 의 세 시각 칸은 단위를 밝힌 삼성 자료가 없어서, ALEAPP 는 값의 크기를 보고 초·밀리초·마이크로초 가운데 하나로 판단합니다 [2]. 요즘 날짜라면 유닉스 초는 10자리, 밀리초는 13자리, 마이크로초는 16자리 정도라서 자릿수로 가를 수 있지만, 이 판단은 도구의 추정이라는 점을 보고서에 밝힙니다. 휴지통 쪽 시각은 유닉스 밀리초로 다루며, 그 설명은 [지운 사진의 흔적](mediastore/deleted-media.md) 페이지에 있습니다. 시각 값 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지를 봅니다.

## 함정과 한계

- 휴지통과 숨긴 앨범의 칸 뜻·단위는 모두 ALEAPP 해석이고, 휴지통 표는 검체 5개에서 모두 비어 있었으며 숨긴 앨범은 사례 1건과 합성 자료가 전부입니다 [1][2].
- 숨긴 앨범 자료는 잠금 해제된 상태의 추출본에서만 보였다는 제보가 있어서 [2], 확보 방법과 시점에 따라 아예 보이지 않을 수 있습니다.
- 휴지통 기록이 갤러리 local.db, 삼성 휴지통 제공자, MediaStore 세 곳에 나뉠 수 있고, 어느 기기·버전에서 어디를 쓰는지는 검체에서 확인합니다.
- 숨긴 앨범과 [보안 폴더](../../01-foundations/security-model/secure-folder-work-profile.md) 안의 갤러리가 저장 위치에서 어떻게 다른지는 공개된 자료가 없어 검체로 확인해야 합니다.

## 직접 분석해 보기

**DB 쿼리.** 확보한 secured.db 사본을 SQLite 를 읽는 공개 도구(예: sqlite3 명령줄)로 열어 먼저 files 표의 칸을 확인하고, 있는 칸만 뽑습니다. 아래 쿼리는 이 페이지의 칸 이름으로 만든 예시입니다.

```sql
PRAGMA table_info(files);

SELECT _display_name, _data, original_path, owner_package_name, cam_model,
       date_added, date_modified, "datetime",
       length(CAST("datetime" AS TEXT)) AS digits
FROM files
ORDER BY "datetime";
```

digits 가 10 이면 초, 13 이면 밀리초, 16 이면 마이크로초로 보고 바꾸되, 같은 파일의 sec_pass 쪽 파일 시스템 시각이나 MediaStore 행과 맞는지 확인합니다. original_path 는 같은 경로가 external.db 의 `_data` 에 남아 있는지 찾는 데 씁니다.

**공개 도구.** ALEAPP 의 galleryTrash 모듈이 휴지통을, SamsungGalleryHiddenAlbum 모듈이 숨긴 앨범을 읽습니다 [1][2]. 숨긴 앨범 모듈의 시각 단위는 자동 판단이라서, 도구 결과의 시각을 위 쿼리의 원래 값과 한 번 맞춰 봅니다.

## 교차 검증

- [미디어 저장소 (MediaStore)](mediastore/index.md) — 원래 경로와 같은 파일의 색인 행, 삼성 media.db 의 is_hide 칸을 봅니다.
- [카메라 사진과 메타데이터 (DCIM·EXIF)](dcim-exif.md) — 숨긴 사진 원본의 EXIF 와 cam_model 을 비교합니다.
- [섬네일 캐시 (Thumbnails)](thumbnails.md) — 숨기거나 지운 사진의 작은 사본이 남는지 봅니다.
- [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) — 그 무렵 갤러리 앱이 앞에 떠 있었는지 봅니다.
- [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md), [지운 대화와 사진 찾기 (Deleted Content)](../../04-scenarios/activity/deleted-content.md) — 이 기록을 쓰는 조사 시나리오입니다.

## 실습

공개 검체(NIST CFReDS 등)에서 삼성 기기 이미지를 구할 수 있으면 다음을 풀어 봅니다.

1. local.db 가 있는지, trash 표에 행이 있는지, `.Trash` 폴더에 파일이 있는지 확인합니다.
2. 같은 검체에서 삼성 휴지통 제공자와 MediaStore 휴지통 표시를 함께 보고, 한 사진이 세 곳 가운데 어디에 남는지 정리합니다.
3. secured.db 가 있다면 세 시각 칸의 자릿수를 보고 단위를 추정한 뒤, 도구가 보여 준 시각과 같은지 확인합니다.
4. original_path 의 경로가 external.db 에 남아 있는지, 남아 있다면 is_trashed·is_pending 값이 무엇인지 봅니다.

## 참고 문헌

1. ALEAPP — scripts/artifacts/galleryTrash.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/galleryTrash.py
2. ALEAPP — scripts/artifacts/SamsungGalleryHiddenAlbum.py (main), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/SamsungGalleryHiddenAlbum.py
