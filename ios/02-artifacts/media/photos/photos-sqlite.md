---
title: "사진 DB 구조"
parent: "사진 보관함"
grand_parent: "아티팩트 · 사진·미디어"
nav_order: 550
---

# 사진 DB 구조 (Photos.sqlite)

## 한 줄 요약

사진 앱은 보관함에 든 사진·동영상마다 `ZASSET` 행을 하나씩 두고, 촬영 정보와 원본 파일, iCloud 동기화 상태, 얼굴, 편집 기록을 여러 표에 나눠 Photos.sqlite 에 적습니다.

## 무엇을 기록하나 · 왜 생기나

사진 앱은 파일을 폴더에 쌓아 두기만 하지 않고, 사진을 찍거나 받거나 iCloud 에서 내려받을 때마다 그 자산(asset)을 DB 에 등록합니다. 그래서 Photos.sqlite 를 열면 사진이 언제 만들어지고 언제 보관함에 들어왔는지, 어떤 경로로 들어왔는지, 즐겨찾기·가려짐·삭제 표시가 되어 있는지, iCloud 와 동기화되었는지를 한곳에서 볼 수 있습니다[1][3]. 촬영에 쓴 카메라와 렌즈, 위도·경도 같은 촬영 정보도 따로 표에 들어 있어서, 원본 파일이 없어도 DB 행만으로 사진의 내력을 어느 정도 따라갈 수 있습니다.

파일 위치와 부속 plist 는 [사진 보관함 (Photos Library)](index.md)에서, 앨범과 공유는 [앨범과 공유 앨범 (Albums·Shared Albums)](albums-shared.md)에서, 삭제 표시는 [최근 삭제된 항목 (Recently Deleted)](recently-deleted.md)에서 다룹니다.

## 위치와 버전별 차이

기기에서는 `/private/var/mobile/Media/PhotoData/Photos.sqlite` 에 있고[1][3], 로컬 백업에서는 CameraRollDomain 의 `Media/PhotoData/Photos.sqlite` 로 들어 있습니다(확인 범위: iOS 27.0).

자산 기본 표의 이름은 한 번 바뀌었습니다. 예전 쿼리는 `ZGENERICASSET` 을 쓰고[2], iOS 14·15 시험 자료는 `ZASSET` 을 씁니다[1]. iOS 에서 정확히 어느 버전에 바뀌었는지는 이번에 연 자료로 확인하지 못했고, macOS 사진 보관함 기준 공개 도구 값만 아래처럼 확인했습니다[4].

| 보관함 | 자산 표 이름 | 출처 |
|---|---|---|
| macOS 사진 5 (macOS 10.15) | `ZGENERICASSET` | [4] |
| macOS 사진 6 이후 (macOS 11 이후) | `ZASSET` | [4] |
| iOS 14·15 시험 자료 | `ZASSET` | [1] |
| iOS 27.0 관찰 기기 | `ZASSET` | 확인 범위: iOS 27.0 |

시험 자료는 iOS 14.7·15.x 기기를 비교했고, 촬영 정보를 담는 `ZEXTENDEDATTRIBUTES` 는 iOS 15 기기에서만 채워져 있었다고 적습니다[1]. 공개 도구 iLEAPP 는 Photos.sqlite 파서를 iOS 11~18 용으로 두고 주로 15~18 을 다룹니다[3]. iOS 27 을 지원하는지는 확인하지 못했습니다.

## 구조

관찰 기기의 Photos.sqlite 에는 표가 많고, 자산을 읽을 때 자주 여는 표는 아래와 같습니다(확인 범위: iOS 27.0). 표마다 칸 이름은 일부만 적었고, 역할 칸에 "이름으로 보아" 라고 붙인 표는 역할을 문서로 확인하지 못했습니다.

| 표 | 관찰한 칸(일부) | 역할 |
|---|---|---|
| `ZASSET` | `ZKIND`, `ZKINDSUBTYPE`, `ZFAVORITE`, `ZHIDDEN`, `ZTRASHEDSTATE`, `ZTRASHEDREASON`, `ZSAVEDASSETTYPE`, `ZCLOUDLOCALSTATE`, `ZCLOUDDELETESTATE`, `ZCLOUDISMYASSET`, `ZISDETECTEDSCREENSHOT`, `ZVISIBILITYSTATE`, `ZSYNDICATIONSTATE`, `ZHEIGHT`, `ZORIENTATION` | 자산 하나에 행 하나 |
| `ZADDITIONALASSETATTRIBUTES` | `ZIMPORTEDBY`, `ZORIGINALFILESIZE`, `ZORIGINALHEIGHT`, `ZORIGINALWIDTH`, `ZTIMEZONEOFFSET`, `ZINFERREDTIMEZONEOFFSET`, `ZVIEWCOUNT`, `ZPLAYCOUNT`, `ZSHARECOUNT`, `ZLASTVIEWEDDATE`, `ZDATECREATEDSOURCE`, `ZLOCATIONHASH`, `ZSYNDICATIONHISTORY` | 이름으로 보아 자산의 부가 정보 |
| `ZEXTENDEDATTRIBUTES` | `ZCAMERAMAKE`, `ZCAMERAMODEL`, `ZLENSMODEL`, `ZLATITUDE`, `ZLONGITUDE`, `ZDATECREATED`, `ZTIMEZONENAME`, `ZTIMEZONEOFFSET`, `ZISO`, `ZAPERTURE`, `ZSHUTTERSPEED`, `ZFOCALLENGTH`, `ZFLASHFIRED`, `ZCODEC`, `ZDURATION`, `ZFPS`, `ZGENERATIVEAITYPE`, `ZCAPTUREREASON` | 촬영 정보(시험 자료에서는 iOS 15 기기에서만 채워짐[1]) |
| `ZCLOUDMASTER` | `ZORIGINALFILENAME`, `ZIMPORTEDBYBUNDLEIDENTIFIER`, `ZIMPORTEDBYDISPLAYNAME`, `ZCREATIONDATE`, `ZIMPORTDATE`, `ZCLOUDMASTERGUID`, `ZUNIFORMTYPEIDENTIFIER`, `ZMEDIAMETADATATYPE` | 이름으로 보아 iCloud 쪽 원본 정보 |
| `ZINTERNALRESOURCE` | `ZASSET`, `ZRESOURCETYPE`, `ZDATALENGTH`, `ZFINGERPRINT`, `ZSTABLEHASH`, `ZCOMPACTUTI`, `ZLOCALAVAILABILITY`, `ZREMOTEAVAILABILITY`, `ZTRASHEDSTATE`, `ZTRASHEDDATE` | 이름으로 보아 자산 하나에 딸린 파일(원본·파생본) |
| `ZCLOUDRESOURCE` | `ZASSETUUID`, `ZFILEPATH`, `ZISLOCALLYAVAILABLE`, `ZLASTONDEMANDDOWNLOADDATE`, `ZLASTPREFETCHDATE`, `ZPRUNEDAT` | 이름으로 보아 iCloud 파일의 내려받기 상태 |
| `ZDETECTEDFACE`·`ZPERSON`·`ZFACECROP` | `ZPERSON` 에 `ZDISPLAYNAME`, `ZFULLNAME` | 얼굴과 사람 |
| `ZUNMANAGEDADJUSTMENT` | `ZADJUSTMENTTIMESTAMP`, `ZADJUSTMENTFORMATIDENTIFIER`, `ZEDITORLOCALIZEDNAME` | 이름으로 보아 편집 기록 |
| `ZMIGRATIONHISTORY` | `ZMIGRATIONDATE`, `ZOSVERSION`, `ZHARDWAREMODEL`, `ZDEVICEUNIQUEID`, `ZSTOREUUID`, `ZMODELVERSION`, `ZCPLENABLED` | 이름으로 보아 DB 를 새 버전으로 옮긴 기록 |
| `ACHANGE`·`ATRANSACTION` | `ACHANGE` 에 `ZCHANGETYPE`, `ZENTITY`, `ZENTITYPK`, `ATRANSACTION` 에 `ZTIMESTAMP`, `ZAUTHOR`, `ZBUNDLEID`, `ZCONTEXTNAME` | 이름으로 보아 Core Data 변경 이력 |

이 밖에 `ZGENERICALBUM`, `ZALBUMLIST`, `ZMOMENT`, `ZPHOTOSHIGHLIGHT`, `ZMEMORY`, `ZSHARE`, `ZSHAREPARTICIPANT`, `ZCLOUDSHAREDCOMMENT`, `ZCLOUDFEEDENTRY` 도 있습니다(확인 범위: iOS 27.0). 앨범·공유 쪽 표는 [앨범과 공유 앨범 (Albums·Shared Albums)](albums-shared.md)에서 다룹니다.

관찰 메모는 표마다 칸을 60개까지만 적어서 `ZASSET`, `ZADDITIONALASSETATTRIBUTES` 의 칸 목록이 중간에 끊겨 있습니다. 그래서 공개 도구 자료가 쓰는 `ZASSET` 의 날짜·파일 칸인 `ZDATECREATED`, `ZADDEDDATE`, `ZMODIFICATIONDATE`, `ZTRASHEDDATE`, `ZLASTSHAREDDATE`, `ZDIRECTORY`, `ZFILENAME`[5]은 관찰 기기에서 보지 못했고, 출처로만 적습니다.

### ZASSET 의 값

`ZASSET` 의 몇몇 칸은 숫자 코드라서 뜻을 알아야 읽을 수 있습니다. 아래 값은 공개 쿼리와 도구 자료가 쓰는 해석이고, 버전마다 달라질 수 있습니다.

| 칸 | 값과 뜻 | 출처 |
|---|---|---|
| `ZKIND` | 0 사진, 1 동영상 | [2] |
| `ZKINDSUBTYPE` | 0 보통, 1 파노라마, 101 슬로모션, 102 타임랩스(옛 스키마 기준 쿼리이고 최신 값은 확인하지 못함) | [2] |
| `ZSAVEDASSETTYPE` | 0 다른 경로로 저장, 3 이 기기 카메라(DCIM-APPLE), 4 공유 앨범(PhotoCloudSharingData), 6 iCloud 사진(CPLAssets), 8 iCloud 공유 링크(CMMAssets), 12 나와 공유됨(Syndication) | [1] |
| `ZSAVEDASSETTYPE`(옛 쿼리) | 2 사진 스트림, 7 삭제 | [2] |
| `ZCLOUDLOCALSTATE` | iCloud 사진을 켠 기기에서 1 iCloud 와 동기화된 자산, 0 공유 앨범의 자산. 끈 기기에서는 0 이 일반 앨범의 자산이고 1 의 뜻은 시험 자료도 더 확인이 필요하다고 적음 | [1] |
| `ZVISIBILITYSTATE` | 자산이 보관함 화면에 보이는지. 다른 Apple 계정과 공유된 자산은 보관함에는 안 보이고 공유 앨범에만 보일 수 있음 | [1] |

`ZSAVEDASSETTYPE` 은 사진이 어느 경로로 보관함에 들어왔는지를 가르는 칸이라서, 이 기기 카메라로 찍은 사진과 받거나 내려받은 사진을 나눌 때 먼저 봅니다. 값마다 파일이 놓이는 폴더는 [사진 보관함 (Photos Library)](index.md)의 표에 있습니다.

### 편집 기록

사진을 편집하면 편집 정보가 DB 와 plist 두 곳에 남습니다. DB 에는 `ZUNMANAGEDADJUSTMENT` 가 있고, CameraRollDomain 의 `Media/PhotoData/Mutations/PhotoData/CPLAssets/group###/` 아래 자산별 폴더에 `Adjustments/Adjustments.plist` 가 있으며, 이 plist 에는 `adjustmentBaseVersion`, `adjustmentData`, `adjustmentEditorBundleID`, `adjustmentFormatIdentifier`, `adjustmentFormatVersion`, `adjustmentRenderTypes`, `adjustmentTimestamp` 키가 있습니다(확인 범위: iOS 27.0). `adjustmentEditorBundleID` 는 이름으로 보아 편집한 앱을 가리키지만 문서로 확인하지는 못했습니다. iLEAPP 는 편집본을 Ph8 파서로 따로 뽑습니다[3].

## 증거로서 의미

**증명하는 것.** `ZASSET` 행이 있으면 수집 시점에 그 자산이 이 보관함에 등록되어 있었다는 사실을 보여 줍니다. `ZSAVEDASSETTYPE` 값으로는 이 기기 카메라로 저장된 자산인지, 공유 앨범·iCloud·나와 공유됨 쪽에서 들어온 자산인지를 가를 수 있고[1], `ZEXTENDEDATTRIBUTES` 의 카메라 모델·위도·경도는 DB 가 적어 둔 촬영 정보를 보여 줍니다.

**증명하지 못하는 것.** 행이 있다고 원본 파일이 기기나 백업에 있다는 뜻은 아닙니다. `ZINTERNALRESOURCE.ZLOCALAVAILABILITY` 와 `ZCLOUDRESOURCE.ZISLOCALLYAVAILABLE` 이 이름으로 보아 파일이 기기에 있는지와 이어지지만, 값의 뜻은 확인하지 못했습니다. 조회 수·공유 수 같은 칸은 누가 봤는지나 누구에게 보냈는지를 알려 주지 않습니다. 공유 날짜 칸이 채워져 있어도 공유가 실제로 끝났다는 뜻은 아니고, 공유 흐름이 중간에 끊겨도 흔적이 남을 수 있습니다[5]. `ZLATITUDE`·`ZLONGITUDE` 도 자산에 적힌 위치일 뿐이라서 이 칸만으로는 이 기기가 그 자리에 있었는지 알 수 없고, `ZSAVEDASSETTYPE` 으로 자산이 들어온 경로를 먼저 확인합니다.

보고서에는 "Photos.sqlite 에 이 기기 카메라로 저장된 자산으로 기록된 사진이 있고, 촬영 정보의 시각은 이렇다" 처럼 DB 가 적어 둔 만큼만 씁니다.

## 시각 해석

Photos.sqlite 의 날짜 칸은 Mac 절대 시각이라서 2001-01-01 00:00:00 UTC 부터 흐른 초로 적혀 있고, 공개 쿼리도 `datetime('2001-01-01', 칸 || ' seconds')` 로 바꿉니다[2]. 유닉스 시각이 필요하면 1970-01-01 과 2001-01-01 사이의 978307200 초를 더합니다. 바꾼 값은 도구 자료처럼 UTC 로 읽고[1], 현지 시각으로 옮길 때는 `ZADDITIONALASSETATTRIBUTES.ZTIMEZONEOFFSET` 이나 `ZEXTENDEDATTRIBUTES.ZTIMEZONENAME` 같은 시간대 칸(확인 범위: iOS 27.0)을 참고하되, 이 칸들이 어느 시각에 맞춘 값인지는 확인하지 못했습니다. 시각 값 전반은 [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

칸마다 바뀌는 때가 다릅니다. `ZDATECREATED` 와 `ZADDEDDATE` 는 도구 자료가 읽는 칸이고[5], 이름으로 보아 만든 시각과 보관함에 추가된 시각이지만 문서로 뜻을 확인하지는 못했습니다. 최근 삭제로 옮길 때는 `ZMODIFICATIONDATE` 도 갱신됩니다[1]. 그래서 `ZMODIFICATIONDATE` 를 편집 시각으로만 읽으면 안 되고, 편집은 `ZUNMANAGEDADJUSTMENT.ZADJUSTMENTTIMESTAMP` 나 `Adjustments.plist` 의 `adjustmentTimestamp` 와 맞춰 봅니다.

## 함정과 한계

시험 자료는 Photos.sqlite 를 WAL 파일과 함께 꺼내야 한다고 적습니다[1]. 관찰 메모에는 Photos.sqlite 의 `-wal`·`-shm` 파일이 적혀 있지 않아서, 백업에 두 파일이 들어가는지는 확인하지 못했습니다. WAL 을 다루는 법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에 있습니다.

값 해석은 대부분 공개 쿼리와 도구 자료에서 왔고 Apple 이 공개한 명세가 아닙니다. `ZKINDSUBTYPE` 은 옛 스키마 기준이고, `ZSAVEDASSETTYPE` 은 옛 쿼리와 새 자료가 적은 값이 다릅니다[1][2]. 새 버전 검체에서는 값의 분포를 먼저 세어 보고, 뜻을 모르는 값은 모른다고 적습니다.

`ZMIGRATIONHISTORY` 와 `ACHANGE`·`ATRANSACTION` 은 이름만 보면 DB 이전 기록과 변경 이력처럼 보이지만(확인 범위: iOS 27.0), 이번에 연 자료로 뜻을 확인하지 못해서 결론의 근거로 쓰지 않습니다.

## 직접 분석해 보기

먼저 헥스로 날짜 칸 하나를 따라가 봅니다. `SELECT typeof(ZDATECREATED) FROM ZASSET LIMIT 1;` 로 저장 형식을 확인하고, 실수(`real`)로 나오면 SQLite 레코드 안에는 8바이트 빅 엔디언 IEEE 754 실수로 들어 있습니다. 아래는 명세로 만든 예시이고 특정 검체에서 나온 값이 아닙니다.

```text
41 C4 DC 93 80 00 00 00   → 700000000.0 (Mac 절대 시각, 초)
700000000 + 978307200     = 1678307200 (유닉스 시각)
                          = 2023-03-08 20:26:40 UTC
```

레코드 헤더에서 칸의 형식 번호를 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

그다음 WAL 을 함께 둔 사본을 sqlite3 로 열어 자산과 촬영 정보를 이어 봅니다. `ZASSET` 의 날짜·파일 칸은 출처 자료 기준[5]이라서, 먼저 `PRAGMA table_info(ZASSET);` 로 칸이 있는지 확인합니다.

```sql
SELECT a.Z_PK, a.ZDIRECTORY, a.ZFILENAME, a.ZKIND, a.ZSAVEDASSETTYPE,
       datetime('2001-01-01', a.ZDATECREATED || ' seconds') AS created_utc,
       datetime('2001-01-01', a.ZADDEDDATE   || ' seconds') AS added_utc,
       e.ZCAMERAMODEL, e.ZLATITUDE, e.ZLONGITUDE
FROM ZASSET a
LEFT JOIN ZEXTENDEDATTRIBUTES e ON e.ZASSET = a.Z_PK
ORDER BY a.ZDATECREATED;
```

공개 도구로는 iLEAPP 의 Photos.sqlite 파서를 씁니다. Ph1 기본 자산, Ph5 위치, Ph6 본·재생한 것, Ph7 즐겨찾기, Ph8 편집본처럼 나뉘어 있고, 얼굴·사람 파서는 iOS 14 이상을 대상으로 합니다[3]. 도구 결과는 위 쿼리로 몇 행을 골라 맞춰 보고 씁니다.

## 교차 검증

파일 안의 EXIF 와 DB 의 촬영 정보는 [카메라 사진과 메타데이터 (DCIM·EXIF·HEIC)](../dcim-exif.md)에서, `ZISDETECTEDSCREENSHOT` 과 이어지는 화면 캡처는 [스크린샷과 화면 녹화 (Screenshots·Screen Recording)](../screenshots.md)에서 맞춰 봅니다. 촬영 위치는 [중요 위치 (Significant Locations)](../../location/significant-locations.md)와 같은 시간대의 기록으로 확인하고, 조사 흐름은 [이 사진은 언제 어디서 찍었나 (Photo Origin)](../../../04-scenarios/activity/photo-origin.md)를 따릅니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 검체로 아래를 풀어 봅니다.

1. `ZASSET` 의 `ZSAVEDASSETTYPE` 값마다 행이 몇 개인지 세고, 표에 없는 값이 있는지 봅니다.
2. `ZDATECREATED` 와 `ZADDEDDATE` 가 크게 차이 나는 자산을 골라, 어떤 경로로 들어온 자산인지 `ZSAVEDASSETTYPE` 과 함께 봅니다.
3. 편집된 자산 하나를 골라 `ZUNMANAGEDADJUSTMENT` 의 시각과 `Adjustments.plist` 의 `adjustmentTimestamp` 가 맞는지 비교합니다.
4. 검체의 iOS 버전에서 자산 표 이름이 `ZASSET` 인지 `ZGENERICASSET` 인지 확인합니다.

## 참고 문헌

1. The Forensic Scooter (Scott Koenig), "Local Photo Library Photos.sqlite Query Documentation & Notable Artifacts" (2022-05-02) — https://theforensicscooter.com/2022/05/02/photos-sqlite-query-documentation-notable-artifacts/
2. kacos2000, Queries `Photos_sqlite.sql` (GitHub) — https://raw.githubusercontent.com/kacos2000/queries/master/Photos_sqlite.sql
3. The Forensic Scooter, "iLEAPP Parsers & Photos.sqlite Queries" (2024-05-18) — https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/
4. RhetTbull, osxphotos `_constants.py` (macOS 사진 보관함 기준, GitHub) — https://raw.githubusercontent.com/RhetTbull/osxphotos/main/osxphotos/_constants.py
5. The Forensic Scooter, "Local Photo Library Photos.sqlite Query Variations & WHERE statements" (2022-02-21) — https://theforensicscooter.com/2022/02/21/photos-sqlite-update/
