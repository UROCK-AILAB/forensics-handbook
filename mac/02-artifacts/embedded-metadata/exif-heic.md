---
title: "사진 메타데이터"
parent: "아티팩트 · 파일 내장 메타데이터"
nav_order: 1870
---

# 사진 메타데이터 (EXIF·HEIC)

사진 파일 안에 적힌 EXIF 태그에는 찍은 시각과 시간대, 기기와 렌즈, GPS 위치가 들어 있고, iPhone 사진이면 Apple 제조사 메모에 연속 촬영·라이브 포토 묶음 ID와 부팅 뒤 경과 시간까지 남아 있어서, 파일 하나만 보고도 언제 어떤 기기로 어디서 찍었다고 적혀 있는지 확인할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

EXIF (Exchangeable Image File Format)는 사진 파일 안에 태그 번호와 값을 짝지어 적어 두는 메타데이터이고, 태그마다 번호와 이름이 정해져 있습니다 [1]. 조사에서 주로 보는 태그는 시각, 기기·소프트웨어, GPS, 제조사 메모 네 종류입니다. Make·Model·Software·HostComputer 같은 태그 이름이 보여 주듯 사진을 만든 기기와 소프트웨어를 적는 태그가 따로 있고, 렌즈 제조사와 모델, 기기 일련번호와 소유자 이름을 적는 태그도 있습니다 [1].

제조사 메모 (MakerNote)는 제조사마다 내용이 다른 태그라서 [1], 해석할 때는 제조사별 태그 표를 봅니다. iPhone 사진의 Apple 제조사 메모 태그 표는 ExifTool 이 공개해 두었습니다 [2]. 여기에는 부팅 뒤 켜져 있던 시간, 가속도 방향, 연속 촬영 (burst) 묶음 ID, 라이브 포토 (Live Photo) 구성 파일을 묶는 ID, 촬영 모드와 카메라 종류가 들어갑니다 [2].

## 위치와 버전별 차이

EXIF 는 사진 파일 안에 들어 있는 값이라서 정해진 시스템 경로가 없고, 파일을 찾은 곳이 곧 위치입니다.

| 항목 | 내용 | 출처 |
|---|---|---|
| EXIF 태그 번호·이름·뜻 | ExifTool 태그 표 | [1] |
| Apple 제조사 메모 태그 | ExifTool 태그 표 | [2] |
| HEIC 컨테이너 구조와 그 안에서 EXIF 를 담는 위치 | 이 페이지에서 다루지 않음 | — |
| AirDrop·메일·사진 앱 내보내기에서 위치 정보가 빠지거나 형식이 바뀌는 조건 | 실제 데이터로 확인 | — |

사진 보관함에 들어간 사진은 보관함 데이터베이스에도 따로 정보가 남지만, 그 값과 EXIF 값이 어떤 관계인지는 이 페이지 범위 밖입니다. 보관함 쪽은 [사진 보관함 (Photos Library)](../cloud-apps/photos-library.md)에서 다룹니다.

## 구조

아래 표의 태그 번호와 이름은 ExifTool 태그 표를 그대로 옮겼고, 명세 이름이 ExifTool 이름과 다르면 괄호에 적었습니다 [1].

**시각 태그.** 시각 태그의 자료형은 문자열이고, 시간대는 시각 문자열과 따로 Offset 태그에 담깁니다 [1].

| 번호 | 이름 (명세 이름) | 뜻 | 짝이 되는 시간대 태그 |
|---|---|---|---|
| 0x0132 | ModifyDate (DateTime) | 수정 시각 | 0x9010 OffsetTime |
| 0x9003 | DateTimeOriginal | 원본 사진을 찍은 날짜·시각 | 0x9011 OffsetTimeOriginal |
| 0x9004 | CreateDate (DateTimeDigitized) | 디지털화한 시각 | 0x9012 OffsetTimeDigitized |
| 0x9291 | SubSecTimeOriginal | DateTimeOriginal 의 초 아래 단위 | — |

**기기·소프트웨어 태그.**

| 번호 | 이름 (명세 이름) | 뜻 |
|---|---|---|
| 0x010f | Make | 기기 제조사 |
| 0x0110 | Model | 기기 모델 |
| 0x0131 | Software | 소프트웨어 |
| 0x013c | HostComputer | 호스트 컴퓨터 |
| 0xa433 | LensMake | 렌즈 제조사 |
| 0xa434 | LensModel | 렌즈 모델 |
| 0xa431 | SerialNumber (BodySerialNumber) | 기기 일련번호 |
| 0xa430 | OwnerName (CameraOwnerName) | 기기 소유자 이름 |
| 0xa420 | ImageUniqueID | 이미지 고유 ID |
| 0x927c | MakerNote | 제조사 메모, 제조사마다 내용이 다름 |

**GPS 태그.** 0x8825 GPSInfo 태그가 GPS 태그 묶음 (GPS IFD)을 가리키고, 아래 태그는 그 묶음 안에 있습니다 [1]. 번호와 이름은 ExifTool 의 GPS 태그 표를 따랐습니다 [3].

| 번호 | 이름 | 뜻 |
|---|---|---|
| 0x0001 | GPSLatitudeRef | 위도 방향 |
| 0x0002 | GPSLatitude | 위도 |
| 0x0003 | GPSLongitudeRef | 경도 방향 |
| 0x0004 | GPSLongitude | 경도 |
| 0x0006 | GPSAltitude | 고도 |
| 0x0007 | GPSTimeStamp | GPS 로 위치를 잡은 시각, UTC |
| 0x001d | GPSDateStamp | GPS 날짜, 형식 YYYY:mm:dd |
| 0x0011 | GPSImgDirection | 찍은 방향 (방향 기준은 0x0010 GPSImgDirectionRef) |
| 0x001f | GPSHPositioningError | 수평 위치 오차 |

**Apple 제조사 메모 (iPhone 사진).** 아래 값은 ExifTool 의 Apple 태그 표에서 옮겼습니다 [2].

| 번호 | 이름 | 뜻 |
|---|---|---|
| 0x0003 | RunTime | 마지막 부팅 뒤 폰이 켜져 있던 시간, 대기 시간은 빠짐. 하위 태그 RunTimeValue·RunTimeScale·RunTimeEpoch·RunTimeFlags 로 나뉨 |
| 0x0008 | AccelerationVector | 폰 앞면 기준 XYZ 가속도, 단위 g |
| 0x000a | HDRImageType | 3=HDR Image, 4=Original Image |
| 0x000b | BurstUUID | 연속 촬영 한 묶음의 사진 모두에 같은 ID |
| 0x0011 | ContentIdentifier | 라이브 포토의 구성 파일(사진·영상)을 묶는 ID |
| 0x0014 | ImageCaptureType | 1=ProRAW, 2=Portrait, 10=Photo, 11=Manual Focus, 12=Scene |
| 0x0017 | LivePhotoVideoIndex | RunTimeScale 로 나누면 초 |
| 0x002e | CameraType | 0=Back Wide Angle, 1=Back Normal, 6=Front |
| 0x0038 | AFMeasuredDepth | 비행시간 (ToF) 보조 자동 초점이 잰 거리 |

ExifTool 은 ContentIdentifier 와 같은 값이 확장 속성 (extended attribute, xattr)으로 나올 때 MediaGroupUUID 라는 이름으로 보여 줍니다 [2]. 짝이 되는 동영상 파일 쪽에서 이 값을 담는 키 이름은 실제 파일로 확인해야 합니다.

## 증거로서 의미

**증명하는 것.** 태그가 있으면 그 파일 안에 그런 값이 적혀 있다는 사실을 보여 줍니다. DateTimeOriginal 은 원본 사진을 찍은 시각으로 적힌 값이고 [1], Make·Model·SerialNumber·LensModel 은 사진을 만든 기기로 적힌 값이라서, 같은 일련번호가 적힌 사진끼리 한 기기에서 나온 것으로 적혀 있다고 말할 수 있습니다. GPS 태그가 있으면 위도·경도와 함께 수평 위치 오차도 볼 수 있어서 [3], 위치를 한 점이 아니라 오차 범위로 적을 수 있습니다. iPhone 사진이면 CameraType 으로 앞·뒤 카메라를, ImageCaptureType 으로 촬영 모드를 구분할 수 있습니다 [2]. BurstUUID 나 ContentIdentifier 가 같은 파일끼리는 한 번의 촬영에서 나온 것으로 묶을 수 있습니다 [2].

**증명하지 못하는 것.** EXIF 는 사진이 만들어진 기기 쪽 기록이라서, 이 맥의 사용자가 그 사진을 찍었다는 것까지 보여 주지는 않고, 받은 사진이나 동기화된 사진에도 같은 값이 그대로 있을 수 있습니다. OwnerName 에 이름이 있어도 기기에 설정된 문자열일 뿐이라서, 그 사람이 셔터를 눌렀다는 뜻은 아닙니다. GPS 태그가 없다고 해서 위치 서비스가 꺼져 있었다고 말할 수도 없는데, 전송·내보내기 과정에서 위치 정보가 빠질 수 있기 때문입니다. Software·HostComputer 값만으로는 어느 단계에서 누가 썼는지 알 수 없습니다.

보고서에는 "이 사람이 이 장소에서 사진을 찍었다" 가 아니라 "이 파일의 EXIF 에는 DateTimeOriginal 이 이 값, OffsetTimeOriginal 이 이 값, 기기 모델이 이 값으로 적혀 있다" 처럼 파일에 적힌 만큼만 씁니다.

## 시각 해석

시각 태그는 수정 시각(ModifyDate), 찍은 시각(DateTimeOriginal), 디지털화한 시각(CreateDate) 세 가지이고, 각각 시간대 태그가 따로 짝지어져 있습니다 [1]. 시각을 UTC 로 옮길 때는 짝이 되는 Offset 태그를 함께 읽고, Offset 태그가 없는 파일이면 시간대는 [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md) 같은 다른 기록에서 따로 찾습니다. 세 시각 태그 문자열에는 시간대가 붙지 않습니다. 그래서 세 시각을 UTC 나 현지 시각으로 단정하지 말고, 같은 파일의 Offset 태그나 다른 시각 기록과 대 본 뒤에 판단합니다. GPS 쪽은 사정이 달라서, GPSTimeStamp 는 GPS 로 위치를 잡은 UTC 시각입니다 [3]. GPSDateStamp 와 GPSTimeStamp 를 합친 값을 DateTimeOriginal 과 비교하면 그 차이로 촬영 당시 기기의 시간대를 추정해 볼 수 있지만, 위치를 잡은 시각과 셔터를 누른 시각이 다를 수 있어서 어림값으로만 씁니다.

SubSecTimeOriginal 은 DateTimeOriginal 에만 붙는 초 아래 단위라서 [1], 같은 초에 찍힌 연속 촬영 사진의 순서를 가릴 때 함께 봅니다.

EXIF 시각은 파일 안에 적힌 값이고, 파일 시스템이 적는 만든 시각·수정 시각과는 따로 움직입니다. 파일 시스템 시각은 [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md)와 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에서 다룹니다.

Apple 제조사 메모의 RunTime 은 실제 시각(wall clock)이 아니라 마지막 부팅 뒤 켜져 있던 시간이고 대기 시간은 빠집니다 [2]. RunTime 은 하위 태그 네 개로 나뉘는 CMTime 구조이고 [2], 이름으로 짐작하면 RunTimeValue 를 RunTimeScale 로 나누면 초가 됩니다. 같은 기기에서 나온 사진끼리 RunTime 과 DateTimeOriginal 의 간격을 비교하면 그 사이에 재부팅이 있었는지 추정해 볼 수 있습니다.

## 함정과 한계

**HEIC 구조는 이 페이지에서 다루지 않습니다.** 이 페이지는 HEIC 컨테이너 구조가 아니라 EXIF 태그 해석만 다룹니다. HEIC 파일에서 값을 뽑을 때는 도구가 그 형식을 읽는지 먼저 확인합니다.

**제조사 메모는 제조사마다 다릅니다.** 0x927c MakerNote 의 내용은 제조사마다 다르고 [1], 이 페이지의 표는 Apple 표입니다 [2]. 다른 제조사의 사진에 Apple 표를 대입하지 않습니다.

**EXIF 값만으로 조작 여부를 판별하지 못합니다.** 태그 값은 파일 안에 적힌 데이터라서, 값이 그럴듯해도 그대로 믿지 말고 파일 시스템 시각, 사진 보관함, 전송 기록과 맞는지 봅니다. 세 시각 태그와 Offset 태그, UTC 로 적힌 GPS 날짜·시각이 서로 맞지 않으면 편집이나 변환을 거쳤을 가능성을 살펴볼 계기로 삼습니다.

**전송 경로에 따라 값이 빠질 수 있습니다.** AirDrop·메일·사진 앱 내보내기를 거치면서 위치 정보가 빠지거나 다른 형식으로 바뀔 수 있으므로, 태그가 없는 파일을 보고 원래부터 없었다고 쓰지 않습니다.

**확장 속성은 따로 움직입니다.** MediaGroupUUID 처럼 확장 속성으로 나오는 값은 파일 내용이 아니라서 [2], 복사·압축·전송 과정에서 파일 안 EXIF 와 다르게 남거나 빠질 수 있습니다. 확장 속성이 복사할 때 어떻게 되는지는 [다운로드 출처 속성 (kMDItemWhereFroms)](../filesystem/where-froms.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

태그 항목을 오프셋 단위로 헥스로 따라가려면 EXIF 명세를 옆에 두고 봅니다.

명세 없이도 헥스 편집기로 할 수 있는 일은 있습니다. 시각 태그 값은 문자열이라서 [1] 헥스 화면의 글자 영역에서 날짜처럼 보이는 문자열을 눈으로 찾을 수 있고, Make·Model 태그에 기기 이름이 문자열로 들어 있으면 같은 방법으로 보입니다. 도구가 보여 준 값과 헥스에서 찾은 문자열이 같은지 한 번 대 보면, 도구가 값을 바꾸거나 빠뜨리지 않았는지 확인할 수 있습니다.

### 공개 도구로 한 번

1. 원본 증거 대신 사본에서 사진 파일을 꺼냅니다. 이미지를 다루는 절차는 [맥 증거 확보 (Acquisition)](../../03-techniques/process-acquisition/evidence-acquisition/index.md)를 따릅니다.
2. ExifTool 로 파일을 읽어 위 표의 태그 이름으로 값을 봅니다. 태그 이름은 ExifTool 표 [1][2][3]와 같습니다.
3. DateTimeOriginal·CreateDate·ModifyDate 를 짝이 되는 Offset 태그와 함께 적고, SubSecTimeOriginal 이 있으면 덧붙입니다.
4. GPS 태그가 있으면 위도·경도와 방향 태그, GPSHPositioningError, GPSDateStamp·GPSTimeStamp 를 함께 적습니다.
5. iPhone 사진이면 Apple 제조사 메모에서 BurstUUID·ContentIdentifier·CameraType·ImageCaptureType 을 적고, 같은 ID 를 쓰는 다른 파일을 찾습니다.
6. 파일 시스템 시각과 확장 속성을 함께 적어 둡니다.

여러 사진의 시각을 한 줄로 늘어놓는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [사진 보관함 (Photos Library)](../cloud-apps/photos-library.md) | 보관함에 들어간 사진의 목록과 보관함 쪽 정보 |
| [다운로드 출처 속성 (kMDItemWhereFroms)](../filesystem/where-froms.md) | 내려받은 사진이면 받은 주소 |
| [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md) | 받은 시각과 받은 앱 |
| [에어드롭 (AirDrop)](../external-devices/airdrop.md) | 다른 기기에서 넘겨받은 흔적 |
| [아이폰·아이패드 연결 (iOS Devices)](../external-devices/ios-devices/index.md) | EXIF 의 기기와 같은 기기가 이 맥에 연결된 적이 있는지 |
| [스포트라이트 (Spotlight)](../file-folder-usage/spotlight/index.md) | 색인에 남은 파일 속성 |
| [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) | 파일이 이 맥에 만들어지고 옮겨진 흔적 |
| [시간대와 시계 설정 (Time Zone·NTP)](../system-account/time-zone.md) | Offset 태그가 없을 때 쓸 시간대 |

사진이 이 맥에 어떻게 들어왔는지 따라가는 순서는 [이 파일은 어디서 왔나 (File Origin)](../../04-scenarios/activity/file-origin.md)에 정리했습니다.

## 실습

NIST CFReDS 같은 공개 데이터셋 가운데 사진 파일이 들어 있는 macOS 이미지를 골라 아래 질문을 풀어 봅니다.

1. 사진 한 장에서 DateTimeOriginal·CreateDate·ModifyDate 와 짝이 되는 Offset 태그를 모두 찾아 적고, 세 시각이 서로 같은지 다른지 설명할 수 있나요?
2. Offset 태그가 없는 사진이 있다면, 그 시각을 UTC 로 옮기려고 어떤 기록을 더 찾아봐야 하나요?
3. EXIF 의 Make·Model·SerialNumber 로 사진을 기기별로 나눌 수 있나요? 그 기기가 이 맥에 연결된 흔적도 있나요?
4. iPhone 사진 가운데 BurstUUID 나 ContentIdentifier 가 같은 파일끼리 묶어 보고, 묶음마다 SubSecTimeOriginal 순서가 맞는지 확인할 수 있나요?
5. GPS 태그가 있는 사진에서 수평 위치 오차를 함께 적어, 보고서에 위치를 어떤 범위로 쓸지 정할 수 있나요?

## 참고 문헌

1. ExifTool, "EXIF Tags" — https://exiftool.org/TagNames/EXIF.html
2. ExifTool, "Apple Tags" — https://exiftool.org/TagNames/Apple.html
3. ExifTool, "GPS Tags" — https://exiftool.org/TagNames/GPS.html
