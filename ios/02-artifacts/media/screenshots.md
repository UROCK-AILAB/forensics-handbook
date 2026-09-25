---
title: "스크린샷과 화면 녹화"
parent: "아티팩트 · 사진·미디어"
nav_order: 590
---

# 스크린샷과 화면 녹화 (Screenshots·Screen Recording)

## 한 줄 요약

아이폰의 스크린샷과 화면 녹화는 사진 보관함에 자산으로 들어가서 Photos.sqlite 의 `ZASSET` 행으로 가려내고, 스크린샷 편집 도구와 화면 녹화 기능 쪽 백업 도메인에는 설정 값만 남습니다.

## 무엇을 기록하나 · 왜 생기나

스크린샷과 화면 녹화가 사진 보관함에 자산으로 들어가면 카메라로 찍은 사진·동영상과 같은 표에 행이 생기고, 두 가지는 자산 종류 칸으로 구별됩니다. 그래서 화면에 무엇이 떠 있었는지를 보여 주는 이미지·동영상이 언제 보관함에 들어왔는지, 아직 보관함에 있는지, "최근 삭제된 항목" 으로 옮겨졌는지를 Photos.sqlite 에서 읽을 수 있습니다. 앱 DB 에서 지워진 대화나 화면이 스크린샷으로만 남아 있을 수도 있어서, 스크린샷은 따로 골라 봅니다.

Photos.sqlite 의 전체 구조와 삭제·편집 기록은 [사진 보관함 (Photos Library)](photos/index.md)에서, 촬영 시각·시간대 칸과 파일 이름 칸은 [카메라 사진과 메타데이터 (DCIM·EXIF·HEIC)](dcim-exif.md)에서 다룹니다.

## 위치와 버전별 차이

스크린샷·화면 녹화를 가려내는 기록은 사진 보관함 DB 에 있고, 그 밖의 흔적은 관찰한 로컬 백업에서 아래 도메인과 plist 로 보였습니다.

| 대상 | 위치 | 출처 |
|---|---|---|
| 사진 보관함 DB | CameraRollDomain :: `Media/PhotoData/Photos.sqlite` | 관찰 |
| 스크린샷 서비스 | AppDomain-com.apple.ScreenshotServicesService (항목 5개) | 관찰 |
| 스크린샷 앱 인텐트 | AppDomainPlugin-com.apple.ScreenshotServicesAppIntents (항목 4개) | 관찰 |
| 화면 녹화(ReplayKit) | AppDomain-com.apple.replaykitangel (항목 4개) | 관찰 |
| 화면 녹화 확장 | AppDomainPlugin-com.apple.ReplayKit.RPBroadcastActivityViewControllerExtension, AppDomainPlugin-com.apple.ReplayKit.RPVideoEditorExtension | 관찰 |

스크린샷·화면 녹화 파일의 확장자와 파일 이름 규칙, "스크린샷" 앨범이 저절로 생기는지는 이번에 연 자료로 확인하지 못했습니다. 아래 값의 뜻이 iOS 버전마다 어떻게 달라지는지도 확인하지 못했고, 관찰 기기인 iOS 27.0 에서 값의 뜻이 같은지도 검증하지 못했습니다.

## 구조

### 사진 보관함 안의 표시

`ZASSET.ZKINDSUBTYPE` 이 10 이면 스크린샷이고, 103 이면 화면 녹화입니다[1]. 화면 녹화는 동영상이라서 `ZKIND` 가 1 입니다[1]. 이 값은 macOS 사진 보관함용 공개 도구 osxphotos 가 쓰는 값이고, 같은 Photos.sqlite 구조이긴 하지만 iOS 기기에서 따로 검증한 자료는 이번에 열지 못했습니다.

| `ZKIND` | `ZKINDSUBTYPE` | 뜻 |
|---|---|---|
| 0 (사진) | 10 | 스크린샷 |
| 1 (동영상) | 103 | 화면 녹화 |

관찰 기기의 `ZASSET` 에는 `ZISDETECTEDSCREENSHOT` 칸도 있습니다. 이름으로 보아 스크린샷으로 판정된 자산을 표시하는 칸으로 보이지만, 값의 뜻과 어느 iOS 부터 생겼는지는 확인하지 못해서 `ZKINDSUBTYPE` 과 나란히 세어 보는 데만 씁니다.

### 스크린샷 서비스 plist

AppDomain-com.apple.ScreenshotServicesService 의 `Library/Preferences/com.apple.ScreenshotServicesService.plist` 에는 `PKPaletteDefaults` 사전 하나만 있고, 그 안에 `PKPaletteAutoHideCorner`, `PKPaletteAutoHideEnabled`, `PKPaletteLastEdge`, `PKPalettePosition` 키가 있습니다. 이름으로 보아 스크린샷을 편집(마크업)할 때 쓰는 도구 팔레트의 위치 설정으로 보이지만 뜻은 확인하지 못했고, 스크린샷을 찍은 기록은 이 plist 에 없습니다.

HomeDomain 의 `Library/Preferences/.GlobalPreferences.plist` 에는 `com.apple.VisualIntelligence.FeatureAwareness.Screenshot`(int) 키가 있습니다. 이 값의 뜻도 확인하지 못했습니다.

### 화면 녹화 쪽 흔적

HomeDomain 의 `Library/Preferences/com.apple.replaykit.AudioConferenceControlCenterModule.plist` 에는 `SBIconVisibility`(bool) 키 하나만 있습니다. 관찰 메모에는 ReplayKit 이 화면 녹화 기록을 따로 적는 DB 가 없어서, 화면 녹화 흔적은 보관함에 든 동영상 자산(`ZKINDSUBTYPE` 103)에서 찾습니다. 녹화를 시작하고 끝낸 시각을 따로 적은 기록은 확인하지 못했습니다.

plist 를 읽는 법은 [속성 목록 파일 (plist·NSKeyedArchiver)](../../01-foundations/data-formats/plist.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** `ZKINDSUBTYPE` 이 10 이나 103 인 `ZASSET` 행은 수집 시점에 그 스크린샷이나 화면 녹화가 사진 보관함에 자산으로 등록되어 있었다는 사실을 보여 줍니다. 원본 파일이 있으면 그 화면에 무엇이 떠 있었는지를 이미지·동영상으로 보여 주고, `ZTRASHEDSTATE` 가 1 이면 "최근 삭제된 항목" 에 들어가 있다는 사실도 보여 줍니다[2].

**증명하지 못하는 것.** 스크린샷 자산이 있다고 이 기기에서 찍었다는 뜻은 아닙니다. 다른 곳에서 받아 저장한 이미지도 보관함에 자산으로 들어오고, 받은 스크린샷이 어떤 종류 값으로 기록되는지는 확인하지 못해서 원래 파일 이름과 가져온 앱 칸으로 경로를 따로 확인합니다. 화면 녹화 동영상도 녹화한 앱이나 녹화 중 누가 기기를 조작했는지는 알려 주지 않습니다. 스크린샷에 카메라 EXIF(제조사·모델·GPS)가 없다는 해석은 자료로 확인하지 못해서, EXIF 가 비어 있다는 사실만으로 스크린샷이라고 단정하지 않습니다.

보고서에는 "사진 보관함에 스크린샷으로 분류된 자산이 있고, 보관함 기록에 따른 생성 시각은 이렇다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

스크린샷과 화면 녹화도 다른 자산과 같은 날짜 칸을 쓰고, `ZDATECREATED`·`ZADDEDDATE`·`ZTRASHEDDATE` 는 2001-01-01 UTC 를 기준으로 한 Mac 절대 시각이라서 978307200 을 더하면 UTC 유닉스 시각이 되고, iLEAPP Ph003 파서도 `ZTRASHEDDATE` 를 이렇게 바꿉니다[2]. 칸별 뜻과 시간대 칸을 함께 읽는 법은 [카메라 사진과 메타데이터 (DCIM·EXIF·HEIC)](dcim-exif.md)에서, 시각 형식 전반은 [시각 값 (Mac 절대 시각·Unix·기타)](../../01-foundations/value-decoding/time-values.md)에서 다룹니다. 스크린샷을 찍은 순간을 KnowledgeC·바이옴·통합 로그에서 찾는 방법은 이번에 연 자료로 확인하지 못했습니다.

## 함정과 한계

값 해석이 macOS 도구에서 왔다는 점이 가장 큰 한계입니다. 검체의 iOS 버전에서 `ZKINDSUBTYPE` 값별 행 수를 먼저 세고, 10·103 으로 뽑은 자산 몇 개를 실제 이미지·동영상과 대조해 스크린샷·화면 녹화가 맞는지 확인한 다음 결론에 씁니다. `ZISDETECTEDSCREENSHOT` 처럼 뜻을 모르는 칸은 모른다고 적습니다.

스크린샷을 지우면 다른 자산과 마찬가지로 `ZTRASHEDSTATE`·`ZTRASHEDDATE` 로 "최근 삭제된 항목" 여부를 봅니다[2]. 스크린샷에만 따로 적용되는 삭제 규칙이 없다고 단정할 자료는 없고, 마크업으로 편집한 스크린샷에 편집 기록이 남는지도 확인하지 못했습니다. 삭제와 편집 기록 전반은 [사진 보관함 (Photos Library)](photos/index.md)에서 다룹니다.

iCloud 사진을 쓰는 기기라면 DB 행만 있고 원본 파일은 기기에 없을 수 있어서, 화면 내용을 확인하려면 [클라우드 데이터 (iCloud·계정 데이터 요청)](../../03-techniques/acquisition/cloud-data.md)도 함께 봅니다.

## 직접 분석해 보기

먼저 헥스로 종류 값을 따라가 봅니다. SQLite 레코드 헤더에서 형식 번호 1 은 1바이트 부호 있는 정수라서, `ZKINDSUBTYPE` 이 10 이면 본문에 `0A` 한 바이트가, 103 이면 `67` 한 바이트가 들어 있습니다. 아래는 SQLite 파일 형식 명세로 만든 예시이고 특정 검체에서 나온 값이 아닙니다.

```text
헤더의 형식 번호 01   → 1바이트 정수
본문 0A               → 10  (스크린샷)
본문 67               → 103 (화면 녹화)
```

레코드 헤더와 형식 번호는 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

그다음 WAL 을 함께 둔 사본을 sqlite3 로 열어 스크린샷과 화면 녹화를 뽑습니다. `ZDATECREATED`·`ZADDEDDATE`·`ZTRASHEDDATE`·`ZDIRECTORY`·`ZFILENAME` 은 출처 자료 기준이라서 먼저 `PRAGMA table_info(ZASSET);` 로 칸이 있는지 확인합니다.

```sql
SELECT a.Z_PK, a.ZKIND, a.ZKINDSUBTYPE, a.ZISDETECTEDSCREENSHOT,
       a.ZDIRECTORY, a.ZFILENAME, a.ZTRASHEDSTATE,
       datetime(a.ZDATECREATED + 978307200, 'unixepoch') AS created_utc,
       datetime(a.ZADDEDDATE   + 978307200, 'unixepoch') AS added_utc,
       datetime(a.ZTRASHEDDATE + 978307200, 'unixepoch') AS trashed_utc
FROM ZASSET a
WHERE a.ZKINDSUBTYPE IN (10, 103) OR a.ZISDETECTEDSCREENSHOT <> 0
ORDER BY a.ZDATECREATED;
```

공개 도구로는 iLEAPP 의 Photos.sqlite 파서로 자산 목록을 뽑고, Ph003 파서로 "최근 삭제된 항목" 에 든 자산을 따로 봅니다[2]. 도구 결과는 위 쿼리 결과와 몇 행을 맞춰 보고 씁니다.

## 교차 검증

스크린샷이 다른 경로로 들어왔는지는 [에어드롭 (AirDrop)](../network/airdrop.md)과 [메시지 (iMessage·SMS)](../communications/messages/index.md)의 첨부 기록으로 확인합니다. 스크린샷에 찍힌 대화나 화면이 앱 DB 에도 남아 있는지는 해당 앱 페이지와 [앱 데이터 분석 (App Data Analysis)](../../03-techniques/analysis/app-data-analysis/index.md)을 따라 대조합니다. 그 시각에 어떤 앱을 쓰고 있었는지는 [KnowledgeC (knowledgeC.db)](../app-usage/knowledgec/index.md)와 [바이옴 (Biome)](../app-usage/biome/index.md)으로 맞춰 보고, 지운 스크린샷을 찾는 흐름은 [지운 대화와 사진 찾기 (Deleted Content)](../../04-scenarios/activity/deleted-content.md)를 따릅니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 검체로 아래를 풀어 봅니다.

1. `ZKINDSUBTYPE` 값별 행 수를 세고, 10 과 103 인 자산이 몇 개인지 봅니다.
2. `ZISDETECTEDSCREENSHOT` 칸이 있는 버전이라면 이 칸의 값과 `ZKINDSUBTYPE` = 10 이 얼마나 겹치는지 비교합니다.
3. 스크린샷 자산 몇 개를 골라 실제 이미지를 열어 보고, 스크린샷이 맞는지와 EXIF 에 무엇이 들어 있는지 확인합니다.
4. `ZTRASHEDSTATE` = 1 인 스크린샷이 있으면 `ZTRASHEDDATE` 를 UTC 로 바꾸고, 같은 시간대의 앱 사용 기록과 나란히 놓아 봅니다.

## 참고 문헌

1. osxphotos, `osxphotos/photosdb/photosdb.py` (RhetTbull) — https://raw.githubusercontent.com/RhetTbull/osxphotos/main/osxphotos/photosdb/photosdb.py
2. iLEAPP, `scripts/artifacts/Ph003TrashedRemovedfromCamRoll.py` (Scott Koenig, v6.0) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/Ph003TrashedRemovedfromCamRoll.py
