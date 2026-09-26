---
title: "카메라 사진과 메타데이터"
parent: "아티팩트 · 사진·미디어"
nav_order: 580
---

# 카메라 사진과 메타데이터 (DCIM·EXIF·HEIC)

## 한 줄 요약

아이폰 카메라로 찍은 사진·동영상은 파일 안의 촬영 정보(EXIF)와 함께 사진 보관함에 등록되고, Photos.sqlite 에는 촬영 시각·시간대·카메라·위치·원래 파일 이름·만든 앱이 따로 적히며, 카메라 설정과 파일 번호 카운터는 plist 에 남습니다.

## 무엇을 기록하나 · 왜 생기나

카메라 앱으로 사진을 찍으면 이미지 파일이 만들어지고, 사진 앱이 그 파일을 보관함의 자산(asset)으로 등록합니다. 파일 안에는 교환 이미지 파일 형식 메타데이터 (EXIF) 로 촬영 시각·카메라·위치 같은 값이 들어가고, Photos.sqlite 에도 이와 비슷한 값이 칸별로 들어 있습니다. 그래서 파일이 있으면 파일의 EXIF 를, 파일이 없어도 DB 행을 읽어 사진이 언제 어느 기기로 찍혔는지 따라가 볼 수 있습니다.

이 페이지는 촬영과 파일 쪽 흔적을 다룹니다. Photos.sqlite 의 전체 구조와 앨범·삭제·편집 기록은 [사진 보관함 (Photos Library)](photos/index.md)에 있고, 스크린샷과 화면 녹화는 [스크린샷과 화면 녹화 (Screenshots·Screen Recording)](screenshots.md)에서 다룹니다.

## 위치와 버전별 차이

### 촬영 형식

아이폰은 iOS 11 부터 사진을 고효율 이미지 파일 형식 (HEIF) 으로, 동영상을 고효율 비디오 코딩 (HEVC, H.265) 으로 저장할 수 있고, iPhone 7 이후 기기 등이 이 형식으로 찍을 수 있습니다[1]. 사용자는 설정 → 카메라 → 포맷에서 "고효율"(HEIF/HEVC)과 "호환성 우선"(JPEG 또는 H.264) 가운데 하나를 고릅니다[1]. 흔히 HEIF 사진을 HEIC 파일이라고 부릅니다. 저장되는 파일 확장자와 촬영 형식 설정이 들어가는 plist 키는 공개 자료가 없어 검체에서 확인합니다.

### 파일과 설정이 놓이는 곳

| 대상 | 위치 | 출처 |
|---|---|---|
| 사진 보관함 DB | 기기: `/private/var/mobile/Media/PhotoData/Photos.sqlite` | [2] |
| 사진 보관함 DB | 로컬 백업: CameraRollDomain :: `Media/PhotoData/Photos.sqlite` |  |
| DCIM 폴더·파일 번호 | CameraRollDomain :: `Media/PhotoData/MISC/DCIM_APPLE.plist` |  |
| iCloud 사진 동기화 상태 | CameraRollDomain :: `Media/PhotoData/CPL/syncstatus.plist` |  |
| 카메라 앱 설정 | HomeDomain :: `Library/Preferences/com.apple.camera.plist` |  |

같은 HomeDomain 의 `Library/Preferences` 에는 `com.apple.cameracapture.plist` 와 `com.apple.cameracaptured.plist` 도 있습니다. iOS 27.0 로컬 백업의 CameraRollDomain 에는 항목이 173개 있습니다. 원본 사진·동영상 파일이 이 도메인의 어느 경로로 들어가는지는 검체의 `Manifest.db` 에서 확인합니다.

### 표 이름과 도구 지원

자산 표는 iOS 12·13 에서 `ZGENERICASSET`, iOS 14 이상에서 `ZASSET` 입니다[2]. 공개 도구 iLEAPP 의 photosMetadata 파서는 iOS 12~14 쿼리만 두어 그보다 새 버전에서는 행을 내지 않고[2], Ph001 파서는 iOS 11~26 쿼리를 나눠 두었고 iOS 27 이상이면 "Unsupported version" 을 남깁니다[3]. iOS 27.0 의 자산 표도 `ZASSET` 이고, 아래 값의 뜻이 iOS 27 에서도 같은지는 검체에서 확인합니다.

| 항목 | iOS 12~13 | iOS 14 이후 | 출처 |
|---|---|---|---|
| 자산 표 | `ZGENERICASSET` | `ZASSET` | [2] |
| 만든·가져온 앱 칸 | `ZADDITIONALASSETATTRIBUTES.ZCREATORBUNDLEID` (iOS 12~14 쿼리) | `ZIMPORTEDBYBUNDLEIDENTIFIER`·`ZIMPORTEDBYDISPLAYNAME` (Ph001 의 iOS 15 이후 쿼리) | [2][3] |
| 파일 형식(UTI) 칸 | `ZGENERICASSET.ZUNIFORMTYPEIDENTIFIER` | `ZASSET.ZUNIFORMTYPEIDENTIFIER` | [2] |

## 구조

### 파일 이름과 위치

`ZASSET.ZDIRECTORY` 와 `ZASSET.ZFILENAME` 이 기기 안에서 파일이 놓인 폴더와 이름을 가리킵니다[3][5]. 원래 파일 이름은 `ZADDITIONALASSETATTRIBUTES.ZORIGINALFILENAME` 과 `ZCLOUDMASTER.ZORIGINALFILENAME` 에 따로 들어 있어서[3], 저장된 이름과 처음 이름이 다른 파일을 가려낼 수 있습니다. iOS 27.0 의 `ZCLOUDMASTER` 에는 `ZORIGINALFILENAME`, `ZIMPORTEDBYBUNDLEIDENTIFIER`, `ZIMPORTEDBYDISPLAYNAME`, `ZIMPORTSESSIONID`, `ZCREATIONDATE`, `ZIMPORTDATE` 칸이 있고, `ZADDITIONALASSETATTRIBUTES` 에는 `ZIMPORTEDBY` 칸이 있습니다. `ZIMPORTEDBY` 의 값별 뜻은 공개 자료가 없어 검체에서 확인합니다.

자산이 어느 경로로 들어왔는지는 `ZASSET.ZSAVEDASSETTYPE` 으로 가릅니다. iOS 12~16 쿼리에서는 값 3 을 보통 `DCIM/***APPLE` 경로에 저장되는 로컬 보관함 자산으로 풀지만[6], 지금의 iLEAPP Ph001 파서는 같은 값 3 을 PhotoData 자산 또는 공유받은(Syndication) 자산으로 함께 적습니다[3]. 다른 값의 뜻과 출처마다 풀이가 다른 점은 [사진 보관함 (Photos Library)](photos/index.md)에서 다룹니다.

`DCIM_APPLE.plist` 에는 `DCIMLastDirectoryNumber`(int) 와 `DCIMLastFileNumber`(int) 두 키가 있습니다. 키 이름으로 보아 카메라가 마지막으로 쓴 폴더 번호와 파일 번호로 보입니다.

### 사진 종류

`ZASSET.ZKIND` 는 0 이 사진, 1 이 동영상이고[2][4], `ZKINDSUBTYPE` 으로 촬영 방식을 더 나눕니다. 아래 값은 macOS 사진 보관함용 공개 도구 osxphotos 가 쓰는 값이라서, 같은 Photos.sqlite 구조이긴 하지만 iOS 기기에서 따로 검증한 값은 아닙니다[4].

| `ZKINDSUBTYPE` | 뜻 |
|---|---|
| 1 | 파노라마 |
| 2 | 라이브 포토 |
| 101 | 슬로모션 동영상 |
| 102 | 타임랩스 동영상 |

`ZADDITIONALASSETATTRIBUTES.ZCAMERACAPTUREDEVICE` 가 1 이면 전면 카메라(셀카)입니다[4]. iOS 27.0 에도 이 칸이 있습니다.

### 촬영 정보가 들어 있는 칸

iOS 27.0 의 `ZEXTENDEDATTRIBUTES` 에는 카메라와 촬영 조건을 적는 칸이 모여 있습니다(전체 41칸). 이 표를 파일의 EXIF 에서 채우는지는 공개 자료가 없습니다.

| 묶음 | 칸 |
|---|---|
| 카메라 | `ZCAMERAMAKE`, `ZCAMERAMODEL`, `ZLENSMODEL` |
| 노출 | `ZAPERTURE`, `ZISO`, `ZFOCALLENGTH`, `ZSHUTTERSPEED`, `ZEXPOSUREBIAS`, `ZFLASHFIRED`, `ZMETERINGMODE`, `ZWHITEBALANCE`, `ZDIGITALZOOMRATIO`, `ZORIENTATION` |
| 시각·위치 | `ZDATECREATED`, `ZTIMEZONENAME`, `ZTIMEZONEOFFSET`, `ZLATITUDE`, `ZLONGITUDE` |
| 동영상 | `ZCODEC`, `ZDURATION`, `ZFPS`, `ZBITRATE`, `ZSAMPLERATE`, `ZTRACKFORMAT` |
| 그 밖 | `ZCAPTUREREASON`, `ZGENERATIVEAITYPE`, `ZCREDIT` |

`ZADDITIONALASSETATTRIBUTES` 에는 원본 파일 쪽 값이 있습니다. iOS 27.0 에는 `ZMEDIAMETADATA`, `ZEDITEDIPTCATTRIBUTES`, `ZORIGINALFILESIZE`, `ZORIGINALWIDTH`, `ZORIGINALHEIGHT`, `ZORIGINALORIENTATION` 과 파일 안 썸네일 위치를 적는 `ZEMBEDDEDTHUMBNAILOFFSET`·`ZEMBEDDEDTHUMBNAILLENGTH`·`ZEMBEDDEDTHUMBNAILWIDTH`·`ZEMBEDDEDTHUMBNAILHEIGHT` 칸이 있고, `ZORIGINALFILESIZE` 는 원본 파일 크기입니다[2].

### 위치

`ZASSET.ZLATITUDE`·`ZLONGITUDE` 가 -180.0 이면 위치가 없는 자산입니다[2]. 위치 값을 보조하는 칸으로 `ZADDITIONALASSETATTRIBUTES.ZSHIFTEDLOCATIONISVALID`·`ZREVERSELOCATIONDATAISVALID` 가 있고[2], iOS 27.0 에는 이 둘과 함께 `ZGPSHORIZONTALACCURACY`, `ZLOCATIONHASH` 칸도 있습니다.

### 원본이 기기에 없는 경우

iCloud 사진을 쓰면 DB 행은 있어도 원본 파일이 기기에 없을 수 있습니다. iOS 27.0 의 `ZCLOUDRESOURCE` 에는 `ZISLOCALLYAVAILABLE`, `ZFILEPATH`, `ZUNIFORMTYPEIDENTIFIER`, `ZLASTONDEMANDDOWNLOADDATE`, `ZPRUNEDAT` 칸이, `ZINTERNALRESOURCE` 에는 `ZLOCALAVAILABILITY`, `ZREMOTEAVAILABILITY`, `ZCOMPACTUTI`, `ZFINGERPRINT` 칸이 있습니다. iLEAPP 에는 원본이 기기에 없을 수 있는 "최적화" 자산을 뽑는 Ph051PossOptimizedAssetsIntResouData 파서가 있습니다[7]. `syncstatus.plist` 에는 `iCloudLibraryExists`, `initialSyncDate`, `lastSyncDate`, `cloudAssetCountPerType`(`public.image`, `public.movie`) 키가 있어서 iCloud 사진이 켜져 있었는지를 먼저 확인할 수 있습니다.

### 카메라 설정

`com.apple.camera.plist` 에는 `CAMUserPreferenceCaptureMode`, `CAMUserPreferenceDesiredHDRMode`, `CAMUserPreferenceDesiredFlashMode`, `CAMUserPreferenceDesiredNightMode`, `CAMUserPreferenceTimerDuration` 같은 설정 키와 `CAMUserPreferencesLastWrittenSettingsDate`, `CAMUserPreferencesLastViewedSettingsInterfaceDate` 두 날짜 키가 있습니다. iLEAPP 에는 이 plist 를 읽는 Ph081comappleCameraPlist 파서가 있습니다[7]. 값의 뜻은 공개 자료가 없으므로, 키 이름으로 짐작한 설정은 결론의 근거로 쓰지 않습니다. plist 를 읽는 법은 [속성 목록 파일 (plist·NSKeyedArchiver)](../../01-foundations/data-formats/plist.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** `ZSAVEDASSETTYPE` 이 3 이고 `ZDIRECTORY` 가 DCIM 폴더를 가리키며 `ZEXTENDEDATTRIBUTES` 에 카메라 모델과 촬영 시각이 적혀 있으면, 보관함이 그 자산을 로컬 보관함의 DCIM 자산으로 기록했다는 사실을 보여 줍니다. 값 3 에는 공유받은 자산도 섞일 수 있어서[3] 이것만으로 이 기기 카메라로 찍었다고 쓰지는 않습니다. 원래 파일 이름과 가져온 앱 칸은 사진이 다른 앱이나 다른 기기에서 들어왔는지 가르는 단서가 되고, 위치 칸이 -180.0 이 아니면 자산에 위치 값이 적혀 있다는 사실을 보여 줍니다.

**증명하지 못하는 것.** EXIF 와 DB 의 카메라 모델은 "이 모델의 카메라로 찍었다" 는 기록일 뿐이라서, 같은 모델의 다른 기기에서 찍어 보낸 사진과 구별되지 않습니다. 위치 값은 사진에 적힌 위치이고 수집한 기기가 그 자리에 있었다는 뜻은 아니며, `ZDATECREATED` 도 파일에 적힌 시각을 따른다면 기기 밖에서 만든 값일 수 있습니다. 사진 행이 있어도 원본 파일이 기기에 있다는 뜻은 아닙니다.

보고서에는 "Photos.sqlite 에 로컬 보관함의 DCIM 자산으로 기록된 사진이 있고, 촬영 정보에는 이 카메라 모델과 이 시각이 적혀 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

Photos.sqlite 의 날짜 칸인 `ZASSET.ZDATECREATED`, `ZADDEDDATE`, `ZMODIFICATIONDATE`, `ZTRASHEDDATE`, `ZLASTSHAREDDATE` 와 `ZCLOUDMASTER.ZCREATIONDATE` 는 Mac 절대 시각이라서, 978307200 을 더하면 유닉스 시각이 됩니다[3][5]. 바꾼 값은 UTC 이고, 현지 시각은 `ZTIMEZONENAME`·`ZTIMEZONEOFFSET` 을 함께 읽어 맞춥니다[3][2]. iOS 27.0 의 `ZADDITIONALASSETATTRIBUTES` 에는 `ZTIMEZONEOFFSET` 과 함께 `ZINFERREDTIMEZONEOFFSET`, `ZDATECREATEDSOURCE` 칸도 있습니다. 두 칸의 뜻은 공개 자료가 없어 검체에서 확인합니다. 시각 형식 전반은 [시각 값 (Mac 절대 시각·Unix·기타)](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

`ZADDITIONALASSETATTRIBUTES.ZEXIFTIMESTAMPSTRING` 은 EXIF 날짜를 문자열 그대로 담고 있습니다[3][2]. 이 문자열을 DB 의 UTC 값과 나란히 놓고, 둘의 차이를 시간대 칸으로 설명할 수 있는지 봅니다.

`ZDATECREATED` 는 촬영 시각, `ZADDEDDATE` 는 보관함에 들어온 시각으로 칸이 따로 있습니다[3]. 두 값이 가까우면 기기에서 찍어 바로 등록한 자산일 가능성이, 멀면 나중에 저장하거나 가져온 자산일 가능성이 있습니다. 이 해석만으로 정하지 말고 `ZSAVEDASSETTYPE`·가져온 앱 칸과 함께 판단합니다.

## 함정과 한계

형식이 바뀌면 해시도 바뀝니다. USB 로 컴퓨터에 사진을 가져오면 JPEG 나 H.264 로 바뀔 수 있고, 설정 → 앱 → 사진에서 "원본 유지" 를 고르면 바뀌지 않습니다[1]. AirDrop·메시지·메일로 보낼 때도 받는 기기가 새 형식을 읽지 못하면 더 호환되는 형식으로 바꿔 보낼 수 있습니다[1]. 그래서 받은 쪽 파일과 원본의 형식·해시가 다르다는 사실만으로 다른 사진이라고 판단하지 않습니다. HomeDomain :: `Library/Preferences/com.apple.mobilesms.compose.plist` 에 있는 `kCKMediaObjectManagerDefaultsUTITypes` 목록에는 `public.heics`, `public.heif`, `public.heif-standard`, `public.jpeg`, `public.png` 가 들어 있지만, 사진 앱이 아닌 메시지 쪽 키라서 보조 근거로만 씁니다.

값의 뜻은 대부분 공개 도구와 쿼리에서 왔고 Apple 이 공개한 명세가 아닙니다. `ZKINDSUBTYPE`·`ZCAMERACAPTUREDEVICE` 값은 macOS 도구 기준이고, `ZSAVEDASSETTYPE` 은 옛 쿼리와 새 쿼리의 풀이가 다릅니다[6][2]. `ZDATECREATED`, `ZFILENAME`, `ZDIRECTORY`, `ZLATITUDE`, `ZUNIFORMTYPEIDENTIFIER`, `ZORIGINALFILENAME`(`ZADDITIONALASSETATTRIBUTES` 쪽), `ZEXIFTIMESTAMPSTRING` 은 공개 도구 쿼리에 나오는 칸 이름이라서, 새 버전 검체에서는 `PRAGMA table_info` 로 칸이 있는지부터 확인합니다.

사진을 지우면 곧바로 행이 사라지지 않고 "최근 삭제된 항목" 표시가 남을 수 있고, 편집하면 편집 기록이 따로 남습니다. 이 두 흔적은 [사진 보관함 (Photos Library)](photos/index.md)에서 다룹니다.

## 직접 분석해 보기

먼저 헥스로 "위치 없음" 값을 따라가 봅니다. `SELECT typeof(ZLATITUDE) FROM ZASSET LIMIT 1;` 로 실수(`real`)인지 확인하면, SQLite 레코드 안에는 8바이트 빅 엔디언 IEEE 754 실수로 들어 있습니다. 아래는 IEEE 754 명세로 만든 예시이고 특정 검체에서 나온 값이 아닙니다.

```text
C0 66 80 00 00 00 00 00   → -180.0
부호 1 | 지수 0x406 (1030 - 1023 = 7) | 가수 1.40625
-1.40625 × 2^7 = -180.0   → iLEAPP 가 "위치 없음" 으로 보는 값
```

레코드 헤더에서 칸의 형식 번호를 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에 있습니다.

그다음 WAL 을 함께 둔 사본을 sqlite3 로 열어 자산과 촬영 정보를 이어 봅니다. 표 연결은 `ZASSET.ZADDITIONALATTRIBUTES = ZADDITIONALASSETATTRIBUTES.Z_PK` 이고[3], `ZEXTENDEDATTRIBUTES` 는 iOS 27.0 에서 `ZASSET` 칸으로 자산을 가리킵니다. 판마다 칸이 다를 수 있어서 먼저 `PRAGMA table_info(ZASSET);` 로 칸 이름을 확인합니다.

```sql
SELECT a.Z_PK, a.ZDIRECTORY, a.ZFILENAME, a.ZKIND, a.ZKINDSUBTYPE, a.ZSAVEDASSETTYPE,
       datetime(a.ZDATECREATED + 978307200, 'unixepoch') AS created_utc,
       datetime(a.ZADDEDDATE   + 978307200, 'unixepoch') AS added_utc,
       aa.ZORIGINALFILENAME, aa.ZEXIFTIMESTAMPSTRING, aa.ZTIMEZONEOFFSET,
       e.ZCAMERAMAKE, e.ZCAMERAMODEL, e.ZLENSMODEL,
       CASE WHEN a.ZLATITUDE = -180.0 THEN NULL ELSE a.ZLATITUDE END AS lat,
       CASE WHEN a.ZLONGITUDE = -180.0 THEN NULL ELSE a.ZLONGITUDE END AS lon
FROM ZASSET a
LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON aa.Z_PK = a.ZADDITIONALATTRIBUTES
LEFT JOIN ZEXTENDEDATTRIBUTES e ON e.ZASSET = a.Z_PK
ORDER BY a.ZDATECREATED;
```

원본 파일이 있으면 공개 도구 ExifTool 같은 EXIF 판독기로 파일의 촬영 시각·카메라·GPS 를 읽어 위 결과와 맞춥니다. iLEAPP 로는 Ph001 기본 자산 파서와 Ph051 최적화 자산 파서, Ph081 카메라 설정 파서를 돌리되[3][7], iOS 27 이상은 Ph001 이 지원하지 않는다고 남기므로[3] 쿼리 결과로 몇 행을 골라 직접 맞춰 봅니다.

## 교차 검증

촬영 위치는 [중요 위치 (Significant Locations)](../location/significant-locations.md)와 [위치 기록 데몬 (routined)](../location/routined.md)의 같은 시간대 기록과 맞춰 봅니다. 사진이 다른 경로로 들어온 것 같으면 [에어드롭 (AirDrop)](../network/airdrop.md)과 [메시지 (iMessage·SMS)](../communications/messages/index.md)의 첨부 기록을, iCloud 에서 내려받은 자산이면 [클라우드 데이터 (iCloud·계정 데이터 요청)](../../03-techniques/acquisition/cloud-data.md)를 봅니다. 촬영 시각을 현지 시각으로 옮기기 전에 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md)도 확인합니다. 사진 한 장의 촬영 시각과 장소를 밝히는 흐름은 [이 사진은 언제 어디서 찍었나 (Photo Origin)](../../04-scenarios/activity/photo-origin.md)를 따릅니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 검체로 아래를 풀어 봅니다.

1. 검체의 iOS 버전에서 자산 표 이름과 만든·가져온 앱 칸 이름을 확인합니다.
2. `ZLATITUDE` 가 -180.0 인 자산과 아닌 자산이 각각 몇 개인지 세고, 위치가 없는 자산의 `ZSAVEDASSETTYPE` 분포를 봅니다.
3. 원본 파일이 있는 사진 하나를 골라 파일 EXIF 의 촬영 시각과 `ZEXIFTIMESTAMPSTRING`, `ZDATECREATED` 를 나란히 놓고 시간대 차이를 설명해 봅니다.
4. `ZDATECREATED` 와 `ZADDEDDATE` 의 차이가 큰 자산을 골라 원래 파일 이름과 가져온 앱 칸이 무엇을 가리키는지 봅니다.
5. `ZCLOUDRESOURCE.ZISLOCALLYAVAILABLE` 값별 행 수를 세고, 검체에 실제 파일이 있는 자산과 비교해 봅니다.

## 참고 문헌

1. Apple Support, "Using HEIF or HEVC media on Apple devices" — https://support.apple.com/en-us/116944
2. iLEAPP, `scripts/artifacts/photosMetadata.py` (@abrignoni, 2026-08-08 갱신) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/photosMetadata.py
3. iLEAPP, `scripts/artifacts/Ph001BasicAssetData.py` (Scott Koenig, v6.0, 2026-07-27 갱신) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/Ph001BasicAssetData.py
4. osxphotos, `osxphotos/photosdb/photosdb.py` (RhetTbull) — https://raw.githubusercontent.com/RhetTbull/osxphotos/main/osxphotos/photosdb/photosdb.py
5. iLEAPP, `scripts/artifacts/Ph003TrashedRemovedfromCamRoll.py` (Scott Koenig, v6.0) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/Ph003TrashedRemovedfromCamRoll.py
6. Scott Koenig, "Local Photo Library Photos.sqlite Query Variations & WHERE statements", The Forensic Scooter (2022-02-21, 2022-09-24 갱신) — https://theforensicscooter.com/2022/02/21/photos-sqlite-update/
7. iLEAPP 저장소 파일 목록(GitHub API, git tree) — https://api.github.com/repos/abrignoni/iLEAPP/git/trees/main?recursive=1
