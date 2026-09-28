---
title: "이 사진은 언제 어디서 찍었나"
parent: "시나리오 · 행위 재구성"
nav_order: 1440
---

# 이 사진은 언제 어디서 찍었나 (Photo Origin)

아이폰 사진 보관함에 있는 사진 한 장이 언제, 어디서, 어떤 경로로 기기에 들어왔는지를 기록으로 거슬러 올라가 찾는 시나리오입니다. 사진 보관함 DB 와 EXIF 의 구조는 아티팩트 페이지에서 다루고, 이 페이지는 "이 기기로 찍었나, 받아서 저장했나" 를 가르는 순서와 판단에 집중합니다.

## 조사 질문

"이 사진을 피의자의 폰으로 찍었나", "찍은 시각과 장소는 어디인가", "메신저로 받은 사진을 저장한 것인가", "사진을 지웠다면 언제인가" 같은 질문입니다. 답은 찍은 시각, 위치, 들어온 경로(이 기기 카메라·다른 앱·iCloud·공유 앨범), 이후의 편집·삭제로 나뉩니다. 사진 파일 안의 EXIF 만 보면 앞의 둘은 알 수 있어도 들어온 경로는 알기 어려워서, 사진 보관함 DB (`Photos.sqlite`) 의 열을 함께 읽습니다.

## 먼저 확인할 것

**사진 보관함 DB 위치**는 기기에서 `/private/var/mobile/Media/PhotoData/Photos.sqlite` [4] 이고, 암호 없는 로컬 백업에서는 CameraRollDomain 의 `Media/PhotoData/Photos.sqlite` 에 있습니다. 백업에서 사진 원본 파일을 어디서 찾는지는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 과 [카메라 사진과 메타데이터](../../02-artifacts/media/dcim-exif.md) 를 따릅니다.

**iOS 버전**에 따라 기본 표 이름과 공개 도구의 쿼리가 다릅니다.

| iOS 버전 | 기본 표 | 참고할 점 |
|---|---|---|
| iOS 12·13 | `ZGENERICASSET` [2] | 옛 iLEAPP 쿼리는 `ZSAVEDASSETTYPE` 2 를 사진 스트림, 7 을 삭제됨으로 풀었습니다 [2] |
| iOS 14 이후 | `ZASSET` [2] | iLEAPP 기본 자산 파서는 쿼리를 iOS 11~13, 14, 15, 16~17, 18~26 으로 나눕니다 [1] |
| iOS 18 | `ZASSET` | 가져온 앱을 `ZIMPORTEDBYBUNDLEIDENTIFIER`·`ZIMPORTEDBYDISPLAYNAME` 으로 읽습니다 [1][2] |
| iOS 27 | `ZASSET`, `ZADDITIONALASSETATTRIBUTES`, `ZEXTENDEDATTRIBUTES` 등 | 같은 iLEAPP 파서는 iOS 27 이상에서 "Unsupported version" 을 남겨서 [1], 쿼리를 직접 맞춰야 합니다 |

**시각 기준**은 `ZASSET.ZDATECREATED`(찍은 시각), `ZADDEDDATE`(보관함에 들어온 시각), `ZMODIFICATIONDATE`, `ZTRASHEDDATE` 모두 Mac 절대 시각이라서 Unix 시각으로 바꾸려면 978307200 을 더합니다 [1][3]. EXIF 날짜는 `ZADDITIONALASSETATTRIBUTES.ZEXIFTIMESTAMPSTRING` 에 문자열 그대로 들어 있고 [1][2], 시간대는 `ZTIMEZONENAME` [1] 과 `ZTIMEZONEOFFSET` [1] 에서 봅니다. 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 을 따릅니다.

**iCloud 사진** 사용 여부도 미리 봅니다. 암호 없는 백업의 CameraRollDomain `Media/PhotoData/CPL/syncstatus.plist` 에 `iCloudLibraryExists`, `initialSyncDate`, `lastSyncDate` 키가 있습니다. iCloud 사진이 켜져 있으면 다른 기기에서 지운 사진이 이 기기에서도 지워지고 [9], 원본이 기기에 없고 iCloud 에만 있을 수도 있습니다 [5].

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 1 | `ZASSET` 시각 열 | `ZDATECREATED`, `ZADDEDDATE`, `ZMODIFICATIONDATE`, `ZTRASHEDDATE` [1][3] | [사진 보관함](../../02-artifacts/media/photos/index.md) |
| 2 | `ZASSET` 위치 열 | `ZLATITUDE`·`ZLONGITUDE`. -180.0 이면 위치가 없는 값입니다 [2] | [사진 보관함](../../02-artifacts/media/photos/index.md) |
| 3 | `ZASSET.ZSAVEDASSETTYPE` | 들어온 경로. 아래 값 표 [1] | [사진 보관함](../../02-artifacts/media/photos/index.md) |
| 4 | `ZADDITIONALASSETATTRIBUTES` | EXIF 날짜 문자열, 시간대, 원래 파일 이름 `ZORIGINALFILENAME` [1], 만든 앱 `ZCREATORBUNDLEID`(iOS 12~14 쿼리) [2] | [사진 보관함](../../02-artifacts/media/photos/index.md) |
| 5 | `ZEXTENDEDATTRIBUTES` | `ZCAMERAMAKE`, `ZCAMERAMODEL`, `ZLENSMODEL`, `ZLATITUDE`, `ZLONGITUDE`, `ZDATECREATED`, `ZTIMEZONENAME`, `ZCAPTUREREASON`, `ZGENERATIVEAITYPE` 등 | [카메라 사진과 메타데이터](../../02-artifacts/media/dcim-exif.md) |
| 6 | `ZCLOUDMASTER` | `ZORIGINALFILENAME`, `ZIMPORTEDBYBUNDLEIDENTIFIER`, `ZIMPORTEDBYDISPLAYNAME`, `ZCREATIONDATE`, `ZIMPORTDATE` | [사진 보관함](../../02-artifacts/media/photos/index.md) |
| 7 | 편집 기록 `ZUNMANAGEDADJUSTMENT` 와 `Adjustments.plist` | `ZADJUSTMENTTIMESTAMP`, `ZADJUSTMENTFORMATIDENTIFIER`, `ZEDITORLOCALIZEDNAME` 열과 `adjustmentEditorBundleID`, `adjustmentTimestamp` 키 | [사진 보관함](../../02-artifacts/media/photos/index.md) |
| 8 | 메시지 첨부 — `sms.db` 의 `attachment` 표 | `created_date`, `filename`, `transfer_name` 등. 첨부 파일은 백업에서 MediaDomain 에 있습니다 [8] | [메시지](../../02-artifacts/communications/messages/index.md) |
| 9 | 카메라 사용 흔적 — 바이옴 `CameraCapture.AutoFocusROI` [11], 전원 로그 `PLCameraAgent_EventForward_Camera` [12] | 카메라 포트와 초점 영역, 보관 28일 [11]. 전원 로그에는 카메라를 쓴 앱(`BundleId`)과 시각이 남고, `CameraType`·`State` 값의 뜻은 풀리지 않았습니다 [12] | [바이옴](../../02-artifacts/app-usage/biome/index.md), [전원 로그](../../02-artifacts/app-usage/powerlog.md) |

`ZSAVEDASSETTYPE` 값은 iLEAPP 기본 자산 파서가 아래처럼 풉니다 [1]. 1·2·7 은 파서 안에서도 "StillTesting" 으로 남겨 두었고, 옛 쿼리는 같은 열을 다르게 풀어서 [2] 값 풀이는 버전과 출처마다 다를 수 있다고 보고 씁니다.

| 값 | iLEAPP 의 풀이 [1] |
|---|---|
| 0 | 다른 경로로 저장 |
| 3 | 이 기기의 사진 보관함 자산(DCIM) |
| 4 | 공유 앨범 (Photo Cloud Sharing) |
| 5 | Photo Booth |
| 6 | iCloud 사진 보관함 |
| 8 | iCloud 링크 |
| 12 | "나와 공유됨" (Shared with You) |

사진 종류는 `ZKIND` 가 0 이면 사진, 1 이면 동영상이고 [2], macOS 사진 보관함에서는 `ZKINDSUBTYPE` 10 이 스크린샷, 103 이 화면 녹화입니다 [6]. `ZASSET` 에는 `ZISDETECTEDSCREENSHOT` 열도 있습니다. macOS 사진 보관함에서는 전면 카메라 사진의 `ZADDITIONALASSETATTRIBUTES.ZCAMERACAPTUREDEVICE` 가 1 입니다 [6]. 아이폰에서도 같은 값인지는 실제 데이터로 확인합니다.

## 분석 흐름

1. iOS 버전, 시간대, 수집 방법, iCloud 사진 사용 여부를 적습니다. 조사할 사진을 파일 이름이나 해시로 특정하고, `ZASSET` 에서 그 행을 찾습니다.
2. 들어온 경로부터 봅니다. `ZSAVEDASSETTYPE` 을 위 표로 읽고, 가져온 앱 열(`ZIMPORTEDBYBUNDLEIDENTIFIER`, 예전 버전은 `ZCREATORBUNDLEID`)과 `ZCLOUDMASTER` 의 원래 파일 이름을 함께 적습니다 [1][2].

   ```sql
   SELECT Z_PK, ZKIND, ZSAVEDASSETTYPE,
          datetime(ZDATECREATED + 978307200, 'unixepoch') AS created_utc,
          datetime(ZADDEDDATE + 978307200, 'unixepoch')   AS added_utc,
          CASE WHEN ZLATITUDE = -180.0 THEN NULL ELSE ZLATITUDE END   AS lat,
          CASE WHEN ZLONGITUDE = -180.0 THEN NULL ELSE ZLONGITUDE END AS lon
   FROM ZASSET
   ORDER BY ZDATECREATED;
   ```

   EXIF 날짜 문자열·시간대·원래 파일 이름이 든 `ZADDITIONALASSETATTRIBUTES` 는 `ZASSET.ZADDITIONALATTRIBUTES` 를 `ZADDITIONALASSETATTRIBUTES.Z_PK` 와 이어 붙입니다 [3]. 버전마다 열이 달라질 수 있어서 쿼리가 멈추면 `PRAGMA table_info(ZADDITIONALASSETATTRIBUTES);` 로 열을 먼저 확인합니다.
3. 시각을 셋으로 맞춰 봅니다. `ZDATECREATED`, EXIF 날짜 문자열, `ZADDEDDATE` 가 서로 가까운지 보고, 시간대 열로 현지 시각을 만듭니다. `ZDATECREATED` 와 `ZADDEDDATE` 의 차이만으로는 "이 기기에서 찍음" 과 "나중에 저장함" 을 가를 수 없어서, 2번의 경로 열과 함께 쓸 때만 근거로 삼습니다.
4. 위치를 봅니다. `ZASSET` 의 위도·경도에 더해 `ZADDITIONALASSETATTRIBUTES` 의 `ZSHIFTEDLOCATIONISVALID`, `ZREVERSELOCATIONDATAISVALID` [2] 와 `ZGPSHORIZONTALACCURACY` 를 적습니다. 위치가 있는 자산만 모아 보려면 iLEAPP 의 `Ph005HasLocations` 파서를 쓸 수 있습니다 [5].
5. 이 기기 카메라로 찍었다고 판단했다면, 수집 범위에 바이옴과 전원 로그가 있을 때 같은 시각에 카메라를 쓴 흔적을 `CameraCapture.AutoFocusROI` 와 `PLCameraAgent_EventForward_Camera` 에서 찾습니다 [11][12]. 사진 위치는 [그 시각에 어디 있었나](location.md) 의 위치 기록과도 맞춰 봅니다.
6. 받은 사진이라면 `sms.db` 의 `attachment` 표나 메신저 앱 DB 에서 같은 파일 이름·크기를 찾습니다. 메시지·AirDrop·메일로 보낼 때 받는 기기가 새 형식을 읽지 못하면 호환 형식으로 바꿔 보낼 수 있어서 [7], 받은 파일과 원본의 형식·해시가 다를 수 있습니다.
7. 편집과 삭제를 봅니다. 편집 기록 열과 `Adjustments.plist` 로 어느 앱이 언제 고쳤는지 적고, `ZTRASHEDSTATE` 가 1 인 자산이 최근 삭제 항목이고 `ZTRASHEDDATE` 는 Mac 절대 시각입니다 [3]. 최근 삭제 항목은 30일 뒤 영구 삭제됩니다 [9][10]. 영구 삭제된 사진은 [지운 대화와 사진 찾기](deleted-content.md) 로 넘깁니다.
8. 판단한 경로·시각·위치를 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올립니다.

## 흔한 오판

사진의 위치를 "그 사람이 그곳에 있었다" 로 옮기는 실수가 가장 흔합니다. 사진 위치로는 사진이 찍힌 곳만 알 수 있고, 받은 사진이라면 다른 사람이 찍은 곳입니다. 사용자가 위치를 고쳤는지는 시험 기기에서 위치를 고쳐 보고 어느 열이 바뀌는지로 확인합니다. 사람의 위치는 [그 시각에 어디 있었나](location.md) 의 기록과 겹칠 때만 적습니다.

`ZSAVEDASSETTYPE` 풀이를 확정된 값처럼 적는 일도 조심합니다. 같은 열을 도구와 버전마다 다르게 풀었고 [1][2], iOS 27 은 공개 파서가 아직 다루지 않습니다 [1].

기기에서 지워진 사진을 "이 기기 사용자가 지웠다" 로 적는 실수도 있습니다. iCloud 사진이 켜져 있으면 다른 기기에서 지운 사진도 이 기기에서 지워져서 [9], 삭제 표시만으로는 어느 기기에서 지웠는지 말할 수 없습니다.

기기 시각이 바뀌었을 가능성도 따집니다. 사용자가 기기 시각을 손으로 바꾸면 knowledgeC.db 의 기록 시각도 틀어집니다 [13]. 사진 DB 의 열도 같은 영향을 받는지는 시험 기기에서 시각을 바꾼 뒤 사진을 찍어 확인합니다. EXIF 날짜 문자열과 `ZDATECREATED`, 앞뒤 사진의 순서가 어긋나면 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md) 을 먼저 봅니다.

받은 파일의 해시가 원본과 다르다고 "다른 사진" 으로 단정하는 일도 있습니다. 보낼 때 호환 형식으로 바뀌거나 [7], USB 로 컴퓨터에 가져올 때 "원본 유지" 설정이 아니면 JPEG·H.264 로 바뀔 수 있습니다 [7].

## 보고서 문장 예

> `Photos.sqlite` 의 `ZASSET` 표 (Z_PK 값) 행의 `ZSAVEDASSETTYPE` 은 3 이고, iLEAPP 는 이 값을 이 기기 사진 보관함의 자산으로 풉니다. `ZDATECREATED` 는 (시각, UTC), EXIF 날짜 문자열은 (값), 위도·경도는 (값) 입니다. 이 기록은 이 사진이 이 기기의 사진 보관함에 기기 자산으로 들어 있었음을 보여 주며, 누가 촬영했는지는 보여 주지 않습니다.

> 같은 행의 `ZTRASHEDSTATE` 는 1, `ZTRASHEDDATE` 는 (시각, UTC) 입니다. 이 기기의 iCloud 사진 사용 여부는 (확인 결과) 였고, 삭제가 이 기기에서 이뤄졌는지는 (확인 방법) 으로 따졌습니다.

## 함께 볼 페이지

- [사진 보관함 (Photos Library)](../../02-artifacts/media/photos/index.md)
- [카메라 사진과 메타데이터 (DCIM·EXIF·HEIC)](../../02-artifacts/media/dcim-exif.md)
- [스크린샷과 화면 녹화 (Screenshots·Screen Recording)](../../02-artifacts/media/screenshots.md)
- [그 시각에 어디 있었나 (Location)](location.md)
- [지운 대화와 사진 찾기 (Deleted Content)](deleted-content.md)
- [문서 메타데이터 (PDF·Office·iWork)](../../02-artifacts/embedded-metadata/documents.md)

## 참고 문헌

1. iLEAPP, `scripts/artifacts/Ph001BasicAssetData.py` (Scott Koenig) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/Ph001BasicAssetData.py
2. iLEAPP, `scripts/artifacts/photosMetadata.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/photosMetadata.py
3. iLEAPP, `scripts/artifacts/Ph003TrashedRemovedfromCamRoll.py` (Scott Koenig) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/Ph003TrashedRemovedfromCamRoll.py
4. Scott Koenig, "Local Photo Library Photos.sqlite Query Documentation & Notable Artifacts", The Forensic Scooter (2022-05) — https://theforensicscooter.com/2022/05/02/photos-sqlite-query-documentation-notable-artifacts/
5. iLEAPP, `scripts/artifacts` 폴더 목록 (GitHub API) — https://api.github.com/repos/abrignoni/iLEAPP/contents/scripts/artifacts
6. osxphotos, `osxphotos/photosdb/photosdb.py` (RhetTbull) — https://raw.githubusercontent.com/RhetTbull/osxphotos/main/osxphotos/photosdb/photosdb.py
7. Apple 지원, "Using HEIF or HEVC media on Apple devices" — https://support.apple.com/en-us/116944
8. ChatExport, ChatExportKnowledge `attachments.md` — https://raw.githubusercontent.com/ChatExport/ChatExportKnowledge/main/attachments.md
9. Apple 지원, "Delete photos on your iPhone or iPad" — https://support.apple.com/en-us/104967
10. Apple 지원, "How to recover deleted photos on your iPhone, iPad, Mac, or Apple Vision Pro" — https://support.apple.com/en-us/124460
11. digital-forensics.it, "84 Streams Later, Part 2: Inside Apple Biome" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html
12. iLEAPP, `scripts/artifacts/powerlog.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/powerlog.py
13. Belkasoft, "KnowledgeC Database Forensics: A Comprehensive Guide" — https://belkasoft.com/knowledgec-database-forensics-with-belkasoft
