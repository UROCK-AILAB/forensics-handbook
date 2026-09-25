---
title: "빠른 보기 섬네일 캐시"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 920
---

# 빠른 보기 섬네일 캐시 (QuickLook)

빠른 보기 섬네일 캐시 (QuickLook thumbnail cache)는 빠른 보기가 만든 파일 섬네일을 사용자마다 모아 두는 곳으로, 메타데이터 DB `index.sqlite` 와 이미지 본체 `thumbnails.data` 로 이뤄집니다 [2][4]. 원본 파일을 지우거나 암호화 볼륨을 내린 뒤에도 섬네일은 여기에 남습니다 [4].

## 무엇을 기록하나 · 왜 생기나

파인더의 보기 설정(아이콘 보기, 목록 보기 등)에 따라서는 사용자가 UI 로 폴더를 열기만 해도 빠른 보기가 그 안 파일의 섬네일을 자동으로 만들어 캐시할 수 있습니다 [4]. 만든 섬네일의 메타데이터는 `index.sqlite` 에 들어가고 이미지 본체는 `thumbnails.data` 에 들어갑니다 [2][4].

이 DB 에는 원본 파일 경로, 사용 횟수(hit count), 섬네일을 마지막으로 쓴 시각, 원본 파일 크기, 원본 파일의 마지막 수정 시각, 그리고 `version` 칸에 담긴 이진 plist(추가 데이터)가 들어 있습니다 [3]. 다만 이는 옛 형식 기준이고, macOS 10.15 Catalina 부터는 DB 에 폴더·파일 이름 칸이 없어져 inode 번호만 남습니다 [1].

## 위치와 버전별 차이

캐시는 사용자 캐시 폴더(DARWIN_USER_CACHE_DIR) 아래에 사용자마다 따로 있습니다 [1][4]. 10.15 이전에는 아래 경로에 있고, 같은 곳을 그 사용자의 `$TMPDIR` 에서 한 단계 올라간 `../C/` 로 가리킬 수도 있습니다 [2][4].

```
/private/var/folders/<무작위>/<무작위>/C/com.apple.QuickLook.thumbnailcache/
$TMPDIR/../C/com.apple.QuickLook.thumbnailcache/
```

macOS 11 Big Sur 부터는 사용자 캐시 폴더 아래에 `com.apple.quicklook.ThumbnailsAgent` 폴더가 한 단계 더 낍니다 [1]. DB 형식은 10.15 에서 한 번 바뀌었습니다 [1].

| macOS | 폴더(사용자 캐시 폴더 아래) | DB 형식 |
|---|---|---|
| 10.14 이하 | `com.apple.QuickLook.thumbnailcache/` | 옛 형식: `files` + `thumbnails`, 경로·이름 있음 [1][2] |
| 10.15 | `com.apple.QuickLook.thumbnailcache/` | 새 형식: `basic_files` + `thumbnails`, inode 만 [1] |
| 11 이상 | `com.apple.quicklook.ThumbnailsAgent/com.apple.QuickLook.thumbnailcache/` | 같은 새 형식(스키마 10 또는 11) [1] |

macOS 12 Monterey 이후 버전의 경로와 형식은 공개 자료가 없어 검체에서 확인합니다.

## 구조

두 형식 모두 SQLite 라서 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)를 따르고, 어느 형식인지는 `files` 테이블이 있는지로 가립니다. `PRAGMA table_info('files');` 결과가 있으면 옛 형식입니다 [1].

### 옛 형식 (10.15 미만)

옛 형식은 원본 파일의 폴더와 파일 이름을 그대로 담아서, 캐시만 보고도 전체 경로를 알 수 있습니다 [4]. 두 테이블은 `files.ROWID = thumbnails.file_id` 로 이어집니다 [1].

| 테이블 | 칸 |
|---|---|
| `files` | `folder`, `file_name`, `fs_id`, `version` (+ rowid) [1][2] |
| `thumbnails` | `file_id`, `size`, `width`, `height`, `bitspercomponent`, `bitsperpixel`, `bytesperrow`, `bitmapdata_location`, `bitmapdata_length`, `last_hit_date`, `hit_count` [1][2] |

`fs_id` 문자열을 11번째 글자부터 자른 뒤 `.` 로 나누면 두 번째 조각이 inode 입니다 [1]. 한 파일에 크기가 다른 섬네일이 여럿 붙을 수 있어서(예: 64×64 와 164×164) [2], `files` 한 행에 `thumbnails` 여러 행이 이어지기도 합니다. `version` 칸의 이진 plist 에 어떤 키가 들어 있는지는 공개 자료가 없고, mac_apt 도 이 BLOB 을 풀지 않고 그대로 넘깁니다 [1]. plist 자체를 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md)에서 다룹니다.

### 새 형식 (10.15 이후)

새 형식에는 `files` 테이블이 없고 `basic_files` 와 `thumbnails` 를 씁니다 [1]. `basic_files.fileId` 는 원본 파일의 inode 번호이고, `thumbnails.file_id` 에는 이 값의 최상위 비트를 켠 값이 들어가서 `(basic_files.fileId | -9223372036854775808) == thumbnails.file_id` 로 두 테이블을 잇습니다 [1]. `-9223372036854775808` 은 64비트 부호 있는 정수로 `0x8000000000000000`, 곧 최상위 비트 하나만 켠 값입니다.

> 그림 자리: `basic_files.fileId`(inode)에 최상위 비트를 켜 `thumbnails.file_id` 와 맞추고, APFS 메타데이터에서 같은 inode 의 이름·상위 폴더를 찾아 경로를 만드는 흐름

새 형식에는 폴더·파일 이름 칸이 없어서, mac_apt 는 같은 볼륨의 APFS 파일시스템 메타데이터(자체 `Combined_Inodes` 테이블의 CNID)에서 inode 로 이름과 상위 폴더를 거꾸로 찾아 경로를 만듭니다 [1]. APFS 의 inode·CNID 구조는 [APFS 구조](../../01-foundations/disk-volume/apfs/index.md)에 있습니다.

새 형식 안에서도 `preferences` 테이블의 `key='version'` 값에 따라 섬네일 형식 칸이 두 가지로 나뉩니다 [1].

| `preferences.version` | 형식 칸 |
|---|---|
| 11 미만 | `bytesperrow`, `bitsperpixel`, `bitspercomponent` 칸 [1] |
| 11 이상 | 그 칸 대신 `bitmapFormat` BLOB(키 아카이브 plist). `$objects[1]` 의 `bpr`(한 줄 바이트 수)·`bpp`(픽셀당 비트)·`bpc`(성분당 비트)를 읽음 [1] |

이 값(10, 11)은 DB 스키마 번호이지 macOS 버전이 아니고, 어느 macOS 부터 11 이 되는지는 공개 자료가 없습니다. 새 형식에서 이 밖에 읽을 칸은 `fileId`, `version`, `size`, `hit_count`, `last_hit_date`, `width`, `height`, `bitmapdata_location`, `bitmapdata_length` 입니다 [1].

### thumbnails.data

`thumbnails.data` 에 든 이미지는 파일 머리·꼬리도, 압축도, 색 팔레트도 없는 raw bitmap 이라서 BMP 파일과 다르고, 외부 정보 없이는 풀 수 없습니다 [2]. 풀 때 필요한 정보는 `index.sqlite` 에 있는데, 시작 위치 `bitmapdata_location` 과 길이 `bitmapdata_length` 로 조각을 잘라 내고 `width`·`height` 로 모양을 잡습니다 [2]. 색 형식은 RGB 에 알파를 더한 RGBA 이고 [2], BGRA 순서로 봐야 할 때도 있습니다 [1]. 줄 끝을 채우는 바이트 때문에 실제 한 줄 폭이 `width` 와 다를 수 있어서, 폭은 `bytesperrow / (bitsperpixel/bitspercomponent)` 로 다시 계산합니다 [1].

## 증거로서 의미

### 증명하는 것

섬네일 행이 있으면 그 사용자 계정의 빠른 보기가 그 파일의 섬네일을 만든 적이 있고, `hit_count` 만큼 섬네일을 쓴 기록과 `last_hit_date` 에 마지막으로 쓴 기록이 있다고 말할 수 있습니다 [1][3]. 섬네일 이미지를 되살리면 원본 파일이 지금 없어도 그 파일이 어떻게 생겼는지 볼 수 있는데, 원본 파일을 지워도 섬네일은 남습니다 [4]. 암호화된 디스크나 TrueCrypt·VeraCrypt 컨테이너 안의 파일을 미리 본 경우에도 섬네일은 컨테이너 밖 캐시에 남고, 컨테이너를 내린 뒤에도 그대로 있습니다 [4]. 옛 형식이면 외부·암호화 볼륨에 있던 파일의 경로와 이름까지 캐시에서 읽을 수 있습니다 [4].

### 증명하지 못하는 것

폴더를 열기만 해도 섬네일이 생길 수 있어서, 섬네일이 있다는 것만으로 사용자가 그 파일을 열어 봤다고 단정할 수 없습니다 [4]. 보고서에는 "이 파일을 봤다" 가 아니라 "이 계정의 빠른 보기 캐시에 이 파일의 섬네일이 있고, 마지막 사용 기록은 이 시각이다" 처럼 기록이 말하는 만큼만 씁니다. 10.15 이후 새 형식은 캐시만으로 파일 이름을 알 수 없어서, 같은 볼륨의 파일시스템 정보가 있어야 경로를 되살릴 수 있습니다 [1]. 원본 파일이 지워졌거나 다른 볼륨에 있던 경우에 새 형식에서 이름을 되살릴 수 있는지, 외부 볼륨 파일이 어떻게 기록되는지는 공개 자료가 없어 검체에서 확인합니다.

## 시각 해석

`last_hit_date` 는 섬네일을 마지막으로 쓴(접근한) 시각이고 [3], 값은 2001-01-01 00:00:00 UTC 부터 센 초인 맥 절대 시각 (Mac Absolute Time)입니다 [1]. 옛·새 형식 모두 아래 식으로 바꾸면 UTC 시각이 나옵니다 [1].

```sql
datetime(last_hit_date + strftime('%s', '2001-01-01 00:00:00'), 'unixepoch')
```

맥 절대 시각을 다른 기준과 가려 읽는 법은 [맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md)에 있습니다. 섬네일을 처음 만든 시각을 담는 칸은 알려져 있지 않으므로, `last_hit_date` 를 "섬네일을 만든 시각" 이나 "파일을 연 시각" 으로 읽지 않습니다. 원본 파일의 마지막 수정 시각 [3] 이 어느 칸이나 키에 어떤 기준으로 들어 있는지는 공개 자료가 없어 검체에서 확인합니다.

## 함정과 한계

도구 출력이 캐시의 전부는 아닙니다. mac_apt 는 파일 하나에 섬네일이 여럿이면 `max(size)` 로 가장 큰 것 하나만 골라 보여 주므로 [1], 크기별 섬네일과 각각의 `hit_count` 를 모두 보려면 DB 를 직접 조회합니다. 새 형식의 `preferences.version` 을 macOS 버전으로 착각하기 쉬운데, 이 값은 스키마 번호입니다 [1].

접근 권한도 버전에 따라 다를 수 있습니다. 2018년 무렵의 macOS 에서는 사용자 권한으로 도는 모든 코드가 이 캐시를 읽을 수 있었습니다 [4]. 10.15 이후 이 폴더에 전체 디스크 접근(TCC)이나 SIP 제한이 걸리는지는 공개 자료가 없어 검체 환경에서 확인합니다. `-wal`·`-shm` 파일이 같이 생길 수 있으니, 수집할 때는 캐시 폴더를 통째로 받아 둡니다.

안티포렌식 관점에서 보면, `qlmanage -r cache` 를 실행하면 재부팅 없이 캐시가 비워졌고 `qlmanage -r` 만으로는 캐시가 지워지지 않는 것처럼 보였다는 관찰이 있습니다(2018년 글 당시 macOS 기준) [4]. ss64 사용법에는 `qlmanage -r`("Reset the Quick Look Server and all Quick Look client's generator cache.")만 있고 `cache` 인자는 적혀 있지 않습니다 [5]. 캐시를 비운 흔적이 통합 로그 등에 남는지는 공개 자료가 없습니다. 그래서 캐시가 비어 있다는 사실만으로 누가 일부러 지웠다고 보지 않고 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md)의 다른 기록과 함께 판단합니다.

## 직접 분석해 보기

### SQLite 와 헥스로 한 번

먼저 `files` 테이블이 있는지 보고 형식을 가린 뒤, 형식에 맞는 쿼리로 행을 뽑습니다 [1].

```sql
PRAGMA table_info('files');   -- 결과가 있으면 옛 형식

-- 옛 형식
SELECT f.rowid, f.folder, f.file_name, f.fs_id,
       t.size, t.width, t.height, t.bytesperrow, t.bitsperpixel, t.bitspercomponent,
       t.bitmapdata_location, t.bitmapdata_length, t.hit_count,
       datetime(t.last_hit_date + strftime('%s', '2001-01-01 00:00:00'), 'unixepoch') AS last_hit_utc
FROM files f JOIN thumbnails t ON f.rowid = t.file_id;

-- 새 형식
SELECT b.fileId AS inode, t.size, t.width, t.height,
       t.bitmapdata_location, t.bitmapdata_length, t.hit_count,
       datetime(t.last_hit_date + strftime('%s', '2001-01-01 00:00:00'), 'unixepoch') AS last_hit_utc
FROM basic_files b JOIN thumbnails t
  ON (b.fileId | -9223372036854775808) = t.file_id;
```

새 형식에서 스키마가 11 미만이면 `bytesperrow`·`bitsperpixel`·`bitspercomponent` 칸을 함께 뽑고, 11 이상이면 `bitmapFormat` BLOB 을 plist 로 풀어 `$objects[1]` 의 `bpr`·`bpp`·`bpc` 를 읽습니다 [1].

다음은 명세로 만든 예시이고 실제 검체 값이 아닙니다. inode 가 12345(`0x3039`)인 파일이라면 `thumbnails.file_id` 쪽 값은 최상위 비트를 켠 `0x8000000000003039` 이어야 두 행이 이어집니다. 어떤 행이 `bitmapdata_location` 0, `bitmapdata_length` 16384, `width`·`height` 64, `bytesperrow` 256, `bitsperpixel` 32, `bitspercomponent` 8 이라면 성분은 32/8 = 4개(RGBA)이고, 폭은 256 / 4 = 64 픽셀로 `width` 와 맞으며, 64줄 × 256바이트 = 16384 바이트라서 길이와도 맞습니다. 이 조각을 잘라 헥스로 보면 머리 없이 곧바로 픽셀 바이트가 이어지는데, 이것으로 raw bitmap 인지 확인합니다 [2].

```sh
dd if=thumbnails.data bs=1 skip=<bitmapdata_location> count=<bitmapdata_length> 2>/dev/null | xxd | head
```

잘라 낸 조각은 아래처럼 그림으로 만듭니다 [1]. 색이 뒤바뀌어 보이면 BGRA 순서로 다시 봅니다.

```python
from PIL import Image
w = bytesperrow // (bitsperpixel // bitspercomponent)   # 줄 끝 채움을 반영한 폭
img = Image.frombytes('RGBA', (w, height), data, decoder_name='raw')
```

### 공개 도구로 한 번

mac_apt 의 `QUICKLOOK` 플러그인("Parses QuickLook Thumbnail Cache data")은 옛·새 형식을 모두 처리하고 섬네일 이미지도 뽑으며, 출력 칸은 Folder, File_Name, Hit_Count, Last_Hit_Date, version, bitmap_data_location, bitmap_data_length, Width, Height, fs_id, inode, row_id, Source 입니다 [1]. 새 형식에서 Folder·File_Name 을 채우려면 같은 볼륨의 APFS 메타데이터를 함께 처리해야 합니다 [1].

Mari DeGrazia 의 OSX-QuickLook-Parser 는 Python 도구이고, `-d` 로 캐시 폴더, `-o` 로 출력 폴더를 받으며 `-t excel` 을 주지 않으면 TSV 로 씁니다 [2][3]. 섬네일 이미지도 뽑고 biplist 와 Pillow 가 필요합니다 [3]. 옛 형식용이고 10.15 이후를 지원하는지는 README 에 적혀 있지 않습니다 [3].

```
python quicklook_parser.py -d "C:\com.apple.QuickLook.thumbnailcache" -o "C:\report_folder" -t excel
```

두 도구의 결과를 직접 조회한 행 수·크기별 섬네일과 맞춰 보면, 도구가 고르거나 빠뜨린 행을 찾을 수 있습니다. 도구 결과를 확인하는 절차는 [도구 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증 — 함께 볼 아티팩트

새 형식에서 inode 를 이름으로 바꾸려면 같은 볼륨의 [APFS 구조](../../01-foundations/disk-volume/apfs/index.md)를 함께 읽어야 하고, 섬네일이 폴더 탐색만으로도 생길 수 있어서 그 폴더를 파인더로 연 흔적을 [폴더 보기 파일 (.DS_Store)](ds-store.md)와 [파인더 설정과 기록](finder-plist.md)에서 찾아 맞춰 봅니다. 파일을 실제로 열었는지는 [최근 항목](recent-items/index.md) 같은 사용 기록으로 따로 확인하고, 파일이 만들어지고 지워진 흐름은 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)와 [스포트라이트](spotlight/index.md)에서 찾습니다. 외장 장치나 암호화 컨테이너에 있던 파일이면 [USB 저장 장치](../external-devices/usb/index.md)와 [암호화된 증거 다루기](../../03-techniques/analysis/encrypted-evidence/index.md)를 함께 봅니다.

조사 흐름 안에서 이 캐시를 어디에 두는지는 [지운 파일의 흔적 찾기](../../04-scenarios/activity/deleted-file-traces.md), [이 파일을 누가 언제 열었나](../../04-scenarios/activity/file-access.md), [타임라인 작성](../../03-techniques/analysis/timeline/index.md)에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 검체의 macOS 버전을 먼저 확인하고, 그 버전에 맞는 캐시 폴더를 사용자별로 찾습니다. 사용자가 여럿이면 캐시도 여럿입니다.
2. `files` 테이블이 있는지로 형식을 가리고, 새 형식이면 `preferences` 의 `version` 값이 10 인지 11 인지 확인합니다.
3. `hit_count` 가 가장 큰 섬네일 다섯 개를 뽑고 `last_hit_date` 를 UTC 로 바꿔 적습니다.
4. 새 형식이면 inode 를 APFS 메타데이터와 맞춰 경로를 되살리고, 되살리지 못한 행이 몇 개인지 셉니다.
5. 섬네일 하나를 헥스로 잘라 그림으로 만들고, mac_apt 가 뽑은 이미지와 같은지 비교합니다.
6. 섬네일은 있지만 원본 파일이 지금 볼륨에 없는 항목을 찾고, 다른 기록으로 그 파일이 언제 사라졌는지 설명해 봅니다.

## 참고 문헌

1. Yogesh Khatri, mac_apt QuickLook 플러그인 소스(quicklook.py) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/quicklook.py
2. Mari DeGrazia, "QuickLook thumbnails.data parser", az4n6 블로그(2016-10) — https://az4n6.blogspot.com/2016/10/quicklook-thumbnailsdata-parser.html
3. Mari DeGrazia, OSX-QuickLook-Parser README — https://github.com/mdegrazia/OSX-QuickLook-Parser
4. Patrick Wardle, "Cache Me Outside: apple's 'quicklook' cache may leak encrypted data", Objective-See(2018-06-15, 발견 Wojciech Reguła) — https://objective-see.org/blog/blog_0x30.html
5. SS64, qlmanage 명령 설명 — https://ss64.com/mac/qlmanage.html
