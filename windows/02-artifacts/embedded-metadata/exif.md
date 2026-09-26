---
title: "사진 EXIF"
parent: "아티팩트 · 파일 내장 메타데이터"
nav_order: 3000
---

# 사진 EXIF (EXIF)

## 한 줄 요약

EXIF 는 사진 파일 안에 들어가는 메타데이터입니다. 기기 제조사와 모델, 저장한 프로그램 이름, 찍은 시각 같은 값이 필드마다 따로 들어갑니다(참고 1). 날짜 글자열에는 시간대가 없습니다(참고 1). 값은 나중에 고칠 수 있고, 한 파일 안에서도 필드끼리 값이 어긋날 수 있습니다. 그래서 필드 하나만 보고 찍은 시각이나 기기를 단정하지 않습니다.

> 아래 예시 값은 Windows 에 기본으로 들어 있는 JPEG 두 개와 Pillow 12.3.0 으로 만든 JPEG 세 개의 값입니다. 탐색기 동작은 Windows 11 빌드 26200, 시간대 KST (UTC+9) 기준입니다.

## 무엇을 기록하나 · 왜 생기나

### 필드는 목록 몇 개에 나뉘어 들어갑니다

EXIF 의 필드는 태그 (tag) 번호로 구분하며, 필드들은 이미지 파일 디렉터리 (Image File Directory, IFD) 라는 목록에 모여 있습니다. IFD0 에는 기기와 파일에 관한 필드가 있고, 그 안의 ExifOffset 필드가 Exif IFD 를, GPSInfo 필드가 GPS IFD 를 가리킵니다(참고 1). IFD1 에는 섬네일 (thumbnail) 의 위치와 길이가 있습니다(참고 1). 필드 이름을 보면 기기가 채우는 필드(Make·Model·SerialNumber·LensModel)과 프로그램이 채우는 필드(Software)이 섞여 있습니다.

### 포렌식에서 자주 보는 필드

아래 이름은 ExifTool 표의 이름입니다. Exif 명세의 이름과 다른 필드는 괄호에 명세 이름을 적었습니다(참고 1).

| 자리 | 태그 번호 | 이름 (명세 이름) | 뜻 |
|---|---|---|---|
| IFD0 | 0x010F | Make | 기기 제조사 |
| IFD0 | 0x0110 | Model | 기기 모델 |
| IFD0 | 0x0131 | Software | 저장한 프로그램 |
| IFD0 | 0x0132 | ModifyDate (DateTime) | 고친 시각 |
| IFD0 | 0x013B | Artist | 작성자 |
| IFD0 | 0x013C | HostComputer | 컴퓨터 이름 |
| IFD0 | 0x8298 | Copyright | 저작권 글 |
| IFD0 | 0x0112 | Orientation | 방향 |
| IFD0 | 0x8769 | ExifOffset | Exif IFD 위치 |
| IFD0 | 0x8825 | GPSInfo | GPS IFD 위치 |
| IFD0 | 0x9C9B~0x9C9F | XPTitle·XPComment·XPAuthor·XPKeywords·XPSubject | Windows 탐색기가 쓰는 필드 |
| Exif IFD | 0x9000 | ExifVersion | Exif 판 |
| Exif IFD | 0x9003 | DateTimeOriginal | 원본 사진을 찍은 시각 |
| Exif IFD | 0x9004 | CreateDate (DateTimeDigitized) | 시각 필드. 아래 "시각 해석" 을 봅니다 |
| Exif IFD | 0x9010~0x9012 | OffsetTime·OffsetTimeOriginal·OffsetTimeDigitized | 시간대 |
| Exif IFD | 0x9290~0x9292 | SubSecTime·SubSecTimeOriginal·SubSecTimeDigitized | 1초 아래 단위 |
| Exif IFD | 0x9286 | UserComment | 사용자 설명 |
| Exif IFD | 0x927C | MakerNote | 제조사 고유 데이터 |
| Exif IFD | 0xA420 | ImageUniqueID | 이미지 고유 ID |
| Exif IFD | 0xA430 | OwnerName (CameraOwnerName) | 기기 주인 |
| Exif IFD | 0xA431 | SerialNumber (BodySerialNumber) | 본체 일련번호 |
| Exif IFD | 0xA433 · 0xA434 | LensMake · LensModel | 렌즈 제조사·모델 |
| IFD1 | 0x0201 · 0x0202 | ThumbnailOffset · ThumbnailLength | 섬네일 위치·길이 |

탐색기는 XPTitle 보다 ImageDescription 을 먼저 씁니다(참고 1).

### 한 파일에 메타데이터가 여러 벌 들어갑니다

Windows 기본 이미지 `C:\Windows\Web\touchkeyboard\TouchKeyboardThemeDark000.jpg` 에는 EXIF 말고도 메타데이터 조각이 여럿 있습니다.

- 조각 순서는 APP1 (Exif) → APP13 (Photoshop) → APP1 (XMP, `http://ns.adobe.com/xap/1.0/`) → APP2 (ICC_PROFILE) → APP14 (Adobe) 입니다.
XMP 속성의 뜻은 [PDF 정보 사전과 XMP](document-metadata/pdf-info-xmp.md) 에서 다룹니다. 같은 뜻의 값이 IFD0, Exif IFD, XMP, 섬네일에 따로 있을 수 있으며, 어긋난 예는 아래 "구조" 에 있습니다.

## 위치와 버전별 차이

### 파일 안 위치

- JPEG 에서는 EXIF 가 APP1 조각에 들어갑니다. 조각 앞머리에 식별 글자 `Exif\0\0` 가 있습니다.
- 조각 순서는 파일마다 다릅니다. `C:\Windows\Web\Wallpaper\Spotlight\img50.jpg` 는 APP0 (JFIF) 조각이 먼저 오고, 그 뒤에 34바이트짜리 작은 EXIF APP1 조각이 있습니다.
- 확장자와 실제 형식이 맞는지는 [파일 형식 식별](../../03-techniques/analysis/content-search/file-signature.md) 로 먼저 확인합니다.

### 버전별 차이

EXIF 는 파일 안에 들어 있습니다. 그래서 값 자체는 Windows 버전과 관계가 없습니다. 달라질 수 있는 것은 Exif 판과, Windows 가 값을 읽어 보여 주는 방식입니다.

| 항목 | 범위 | 근거 |
|---|---|---|
| 파일의 Exif 판 | 파일마다 ExifVersion 필드에 적습니다 | 참고 1 |
| 탐색기 "찍은 날짜" 가 OffsetTimeOriginal 을 무시함 | Windows 11 빌드 26200 | — |

## 구조

### JPEG 머리에서 TIFF 머리까지

`TouchKeyboardThemeDark000.jpg` 의 배치입니다. APP1 조각이 파일 첫 2바이트 바로 뒤에 올 때의 위치입니다.

| 파일 위치 | 크기 | 값 | 뜻 |
|---|---|---|---|
| 0 | 2 | `FF D8` | 파일 첫 2바이트 |
| 2 | 2 | `FF E1` | APP1 조각 표시 |
| 4 | 2 | 빅 엔디언 숫자 | 조각 길이. 이 파일에서는 2472 |
| 6 | 6 | `45 78 69 66 00 00` | 식별 글자 `Exif\0\0` |
| 12 | 8 | `49 49 2A 00 08 00 00 00` | TIFF 머리 |

TIFF 머리는 이렇게 읽습니다.

- `49 49` 는 글자 "II" 입니다. 뒤의 숫자를 리틀 엔디언으로 읽으라는 뜻입니다.
- `2A 00` 은 42 입니다.
- `08 00 00 00` 은 8 입니다. IFD0 이 TIFF 머리에서 8바이트 뒤에 있습니다.

### IFD 읽기

- IFD 안의 오프셋은 파일 처음이 아니라 TIFF 머리부터 센 값입니다.
- 필드 하나는 12바이트입니다.

| 필드 안 위치 | 크기 | 내용 |
|---|---|---|
| 0 | 2 | 태그 번호 |
| 2 | 2 | 자료형 |
| 4 | 4 | 개수 |
| 8 | 4 | 값, 또는 값이 있는 곳의 오프셋 |

- 4바이트보다 긴 값(글자열 등)은 필드 밖에 따로 두고 오프셋으로 가리킵니다.
- 필드들이 끝난 뒤 4바이트는 다음 IFD (IFD1) 의 오프셋입니다. 이 파일에서는 300 이었습니다.
- 자료형 번호의 뜻은 이 페이지에서 다루지 않습니다.

### 한 파일 안에서 값이 어긋난 예

같은 `TouchKeyboardThemeDark000.jpg` 의 값입니다.

| 항목 | 한 자리의 값 | 다른 자리의 값 |
|---|---|---|
| 프로그램 이름 | IFD0 Software = `Adobe Photoshop 21.1 (Windows)` | XMP CreatorTool = `Adobe Photoshop 22.0 (Windows)` |
| 이미지 크기 | IFD0 ImageWidth·ImageLength = 4096 × 2304 | Exif IFD PixelXDimension·PixelYDimension = 2736 × 1539 |

실제 이미지 크기는 2736 × 1539 로 Exif IFD 쪽 값과 맞았고, IFD1 에는 JPEG 섬네일(Compression 값 6, 오프셋 394, 길이 2070)이 따로 있었습니다. 편집 프로그램이 모든 필드를 함께 고치지는 않는다는 뜻입니다.

> 그림 자리: JPEG 한 파일 안에서 APP1(Exif: IFD0 → Exif IFD, IFD1 섬네일), APP13, APP1(XMP) 조각을 나란히 그리고, 같은 뜻의 필드(프로그램 이름·이미지 크기·시각)을 선으로 이어 값이 다른 곳을 표시

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 파일 안 어느 자리(IFD0·Exif IFD·XMP)에 어떤 값이 적혀 있는지 | 적힌 값이 사실인지. 값은 나중에 고칠 수 있습니다 |
| 시간대 필드가 있으면, 값을 적은 쪽이 밝힌 UTC 와의 차이 | 시간대 필드가 없을 때 그 시각이 현지 시각인지 UTC 인지(참고 1) |
| Make·Model·SerialNumber 에 적힌 기기 정보 | 그 기기로 찍었는지, 누가 찍었는지 |
| Software·CreatorTool 에 적힌 프로그램 이름 | 그 프로그램이 마지막으로 저장했는지. 필드마다 따로 남습니다 |
| | 기기 시계가 맞았는지 |
| | 이 PC 로 사진을 옮기거나 연 시각 |

### 보고서 문장

아래 파일 이름과 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "`IMG_0001.jpg` 의 Exif IFD 에는 DateTimeOriginal 값 `2020:01:02 03:04:05` 가 있습니다. 같은 IFD 에 OffsetTimeOriginal 필드는 없습니다. 그래서 이 값이 어느 시간대의 시각인지 파일만으로는 알 수 없습니다."
- 쓰면 안 되는 문장: "이 사진은 2020년 1월 2일 오전 3시 4분에 찍었다."

## 시각 해석

### 시각 필드 (참고 1)

| 시각 필드 | 자리 | 시간대 필드 | 1초 아래 필드 |
|---|---|---|---|
| ModifyDate (DateTime), 0x0132 | IFD0 | OffsetTime, 0x9010 | SubSecTime, 0x9290 |
| DateTimeOriginal, 0x9003 | Exif IFD | OffsetTimeOriginal, 0x9011 | SubSecTimeOriginal, 0x9291 |
| CreateDate (DateTimeDigitized), 0x9004 | Exif IFD | OffsetTimeDigitized, 0x9012 | SubSecTimeDigitized, 0x9292 |

날짜 글자열 형식은 `YYYY:mm:dd HH:MM:SS` 이고 시간대가 없어서, 시간대는 OffsetTime 계열 필드에 따로 적습니다(참고 1). DateTimeOriginal 은 원본 사진을 찍은 시각인데(참고 1), 기기 시계가 맞았는지는 이 값만으로 알 수 없습니다.

### EXIF 와 XMP 의 시각

`TouchKeyboardThemeDark000.jpg` 의 시각 값입니다.

| 자리 | 값 |
|---|---|
| EXIF ModifyDate | `2021:04:09 09:43:05` (시간대 없음) |
| XMP ModifyDate, XMP MetadataDate | `2021-04-09T09:43:05-07:00` |
| XMP CreateDate | `2020-12-11T17:19:52+01:00` |
| XMP 편집 이력 (stEvt:when) | `2020-12-11T17:19:52+01:00`, `2020-12-14T11:24:57+01:00`, `2021-04-09T09:43:05-07:00` |

EXIF 값은 XMP 값에서 시간대만 뺀 모양이며, 편집한 컴퓨터의 현지 시각이었습니다. XMP 편집 이력을 보면 편집한 곳의 시간대가 +01:00 에서 -07:00 으로 바뀌었습니다. 그래서 시간대가 다른 곳에서 편집한 파일은 EXIF 시각만 늘어놓으면 순서가 틀릴 수 있으므로, 시간대가 적힌 XMP 값과 함께 봅니다.

### 탐색기의 "찍은 날짜"

DateTimeOriginal 과 CreateDate 가 모두 `2020:01:02 03:04:05` 이고 OffsetTimeOriginal 만 다른 JPEG 세 개를 탐색기에서 보면 아래와 같습니다.

| 파일 | OffsetTimeOriginal | 탐색기 "찍은 날짜 (Date taken)" 열 | 셸 속성 System.Photo.DateTaken |
|---|---|---|---|
| 1 | 없음 | 2020-01-02 오전 3:04 | 2020-01-01 18:04:05 (Kind=Unspecified) |
| 2 | `+09:00` | 2020-01-02 오전 3:04 | 2020-01-01 18:04:05 (Kind=Unspecified) |
| 3 | `-05:00` | 2020-01-02 오전 3:04 | 2020-01-01 18:04:05 (Kind=Unspecified) |

세 파일 모두 값이 같습니다. 탐색기는 OffsetTimeOriginal 을 반영하지 않습니다. System.Photo.DateTaken 은 EXIF 값에서 PC 의 시간대 차이(KST 는 9시간)를 뺀 값입니다. Windows 는 EXIF 시각을 "보고 있는 PC 의 현지 시각" 으로 보고 UTC 로 바꿔 두었다가, 화면에 보여 줄 때 다시 현지 시각으로 바꿉니다.

- 그래서 Windows 검색 색인에 저장된 찍은 날짜도 색인한 PC 의 시간대에 따라 달라질 수 있습니다. 색인 속에 남은 파일 속성은 [파일 속성 되살리기 (PropertyStore)](../file-folder-usage/windows-search/propertystore.md) 에서 다룹니다.
- 분석 대상 PC 의 시간대는 [시간대 설정](../system-account/time-zone.md) 에서 확인합니다.
- 파일 시스템 시각은 EXIF 와 다른 기록입니다. 읽는 법은 [두 벌의 시각](../../01-foundations/disk-volume/ntfs/standard-information-file-name.md) 에서 다룹니다.

## 함정과 한계

1. **시간대 없는 시각을 UTC 로 읽습니다.** EXIF 날짜 글자열에는 시간대가 없습니다(참고 1). OffsetTime 계열 필드가 있으면 그 값을 씁니다. 없으면 "시간대 모름" 으로 적습니다.
2. **탐색기 "찍은 날짜" 를 그대로 옮겨 적습니다.** 탐색기는 OffsetTimeOriginal 을 무시합니다. 화면 값 대신 원래 필드를 읽습니다.
3. **필드 하나만 봅니다.** 한 파일 안에서 IFD0·Exif IFD·XMP·섬네일 값이 서로 다를 수 있습니다.
4. **EXIF 조각이 파일 맨 앞에 있다고 봅니다.** APP0 조각이 먼저 오는 파일이 있습니다. 조각 표시를 차례로 따라가며 찾습니다.
5. **오프셋을 파일 처음부터 셉니다.** IFD 안의 오프셋은 TIFF 머리부터 셉니다.
6. **도구가 보여 주는 이름으로 명세를 찾습니다.** ExifTool 은 명세의 DateTimeDigitized 를 CreateDate 라고 부릅니다(참고 1). 보고서에는 두 이름을 함께 적습니다.
7. **EXIF 가 없다는 것만으로 결론을 냅니다.** 메신저·SNS 로 보낸 사진에서 EXIF 가 지워지는지는 서비스마다 다를 수 있어 실제 데이터로 확인합니다.

### 지우기와 조작

- EXIF 값은 나중에 고칠 수 있습니다. DateTimeOriginal 에 임의 값을 넣은 JPEG 도 탐색기는 그 값을 찍은 날짜로 보여 줍니다.
- 자리끼리 어긋난 값과 XMP 편집 이력은 파일을 다시 저장했는지 따질 때 단서가 됩니다. 어긋남만으로 조작이라고 결론 내지 않습니다. 정상 편집에서도 생깁니다.
- 날짜를 여러 기록으로 따지는 순서는 [이 문서의 날짜를 믿을 수 있나](../../04-scenarios/activity/document-date-verification.md) 에서 다룹니다. 일부러 지우거나 바꾼 정황은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에서 다른 흔적과 함께 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 이 페이지의 구조 설명에 맞춰 만든 예시입니다. 실제 데이터에서 뽑은 값이 아닙니다. 길이 필드에는 예로 2472(`09 A8`)를 넣었습니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    FF D8 FF E1 09 A8 45 78 69 66 00 00 49 49 2A 00   ......Exif..II*.
0x10    08 00 00 00 ...                                   ....
```

1. 0x00 의 `FF D8` 은 파일 첫 2바이트입니다.
2. 0x02 의 `FF E1` 은 APP1 조각 표시입니다. 0x04 의 `09 A8` 을 빅 엔디언으로 읽으면 2472 입니다.
3. 0x06 부터 `Exif` 와 `00 00` 이 옵니다.
4. 0x0C 부터 TIFF 머리입니다. 이 위치를 기준점으로 적어 둡니다.
5. `49 49` 이므로 뒤의 숫자는 리틀 엔디언으로 읽습니다. `2A 00` 은 42 입니다.
6. 0x10 의 `08 00 00 00` 은 8 입니다. IFD0 은 기준점 + 8, 즉 파일 오프셋 0x14 에 있습니다.
7. IFD0 의 필드를 12바이트씩 읽으며 태그 번호 `69 87`(0x8769, ExifOffset)을 찾습니다. 이 필드의 마지막 4바이트가 Exif IFD 위치입니다. 기준점을 더해 파일 오프셋으로 바꿉니다.
8. Exif IFD 에서 `03 90`(0x9003, DateTimeOriginal) 필드를 찾습니다. 날짜 글자열은 4바이트보다 길어서, 필드의 마지막 4바이트가 글자열 위치를 가리킵니다.
9. 글자열 `2020:01:02 03:04:05` 는 바이트로 `32 30 32 30 3A 30 31 3A 30 32 20 30 33 3A 30 34 3A 30 35` 입니다.
10. 같은 Exif IFD 에 `11 90`(0x9011, OffsetTimeOriginal) 필드가 있는지 봅니다. 없으면 시간대를 모르는 값입니다.

### 공개 도구로 한 번

- ExifTool 은 필드 이름을 참고 1 의 표 이름으로 보여 줍니다(참고 1). 그래서 명세 이름과 다른 필드가 있습니다.
- Python 의 Pillow 로도 필드를 읽을 수 있습니다.

어느 도구를 쓰든 아래를 확인합니다.

- IFD0·Exif IFD·XMP 값을 자리별로 나눠 보여 주는지 확인합니다.
- 시각을 적힌 그대로 보여 주는지, 분석 PC 의 시간대로 바꿔 보여 주는지 확인합니다.
- IFD1 섬네일을 따로 뽑을 수 있는지 확인합니다.
- 몇 개는 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.
- 메타데이터를 고치는 명령을 실수로 주지 않도록 사본에서 작업합니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [썸네일 캐시](../file-folder-usage/thumbcache-db-thumbs-db.md) | 사진의 작은 그림이 캐시에 남았는지. `%LOCALAPPDATA%\Microsoft\Windows\Explorer` 에 `thumbcache_exif.db` 가 생길 수 있으며, 담긴 내용은 실제 데이터로 확인합니다 |
| [파일 속성 되살리기 (PropertyStore)](../file-folder-usage/windows-search/propertystore.md) | 색인에 들어간 파일 속성 |
| [시간대 설정](../system-account/time-zone.md) | 분석 대상 PC 의 시간대 |
| [두 벌의 시각](../../01-foundations/disk-volume/ntfs/standard-information-file-name.md) | 파일을 만들거나 옮긴 시각 |
| [문서 메타데이터](document-metadata/index.md) | 문서 파일 안의 작성자·시각. XMP 는 [PDF 정보 사전과 XMP](document-metadata/pdf-info-xmp.md) 에서 다룹니다 |
| [파일 형식 식별](../../03-techniques/analysis/content-search/file-signature.md) | 확장자와 실제 형식이 맞는지 |

파일이 어디서 왔는지 여러 기록으로 좁히는 순서는 [이 파일은 어디서 왔나](../../04-scenarios/activity/file-origin.md) 에서 다룹니다.

## 실습

**직접 만든 Windows 10·11 가상 머신**에서 해 봅니다.

1. 스마트폰이나 카메라로 찍은 사진 하나를 PC 로 옮겨 DateTimeOriginal 과 OffsetTimeOriginal 을 읽어 보십시오. 시간대 필드가 있습니까?
2. 같은 사진을 탐색기 세부 정보에서 보십시오. "찍은 날짜" 가 원래 필드 값과 같습니까?
3. PC 의 시간대를 바꾼 뒤 다시 보십시오. "찍은 날짜" 가 바뀝니까? System.Photo.DateTaken 은 어떻게 됩니까?
4. 사본을 편집 프로그램으로 다시 저장해 보십시오. IFD0 Software, XMP CreatorTool, 섬네일 가운데 무엇이 바뀌었습니까?
5. 사진을 메신저로 보냈다가 받은 사본에서 EXIF 가 남았는지 보십시오.

**NIST CFReDS 같은 공개 데이터셋의 Windows 디스크 이미지**로도 풀어 봅니다.

1. 사용자 사진 폴더의 JPEG 가운데 EXIF 가 있는 파일은 몇 개입니까? Make·Model 은 어떤 값들입니까?
2. DateTimeOriginal 과 파일 시스템 시각을 나란히 놓으면 어느 쪽이 앞섭니까? 그 차이를 어떤 기록으로 설명할 수 있습니까?
3. 한 파일 안에서 IFD0·Exif IFD·XMP 값이 어긋난 파일이 있습니까? 있다면 어떤 프로그램 이름이 적혀 있습니까?

## 참고 문헌

1. ExifTool, "EXIF Tags" — https://exiftool.org/TagNames/EXIF.html
