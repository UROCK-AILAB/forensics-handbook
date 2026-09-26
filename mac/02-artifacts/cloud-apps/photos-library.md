---
title: "사진 보관함"
parent: "아티팩트 · 클라우드·애플 앱"
nav_order: 1590
---

# 사진 보관함 (Photos Library)

## 한 줄 요약

사진 앱이 쓰는 보관함 패키지 안의 `Photos.sqlite` 에는 사진·비디오 한 건마다 저장 파일 이름, 원래 파일 이름, 촬영·추가·휴지통 시각, 위치, 가져온 앱 같은 열이 있어서, 어떤 사진이 언제 보관함에 들어오고 지워졌는지 따라갈 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

사진 앱은 사진과 비디오를 보관함 하나에 모아 관리하고, 보관함 안의 SQLite 데이터베이스에 항목마다 행을 하나씩 만듭니다. 이 행에는 보관함 안에 저장한 원본 파일의 위치, 가져올 때의 원래 파일 이름, 휴지통 상태, 숨김·즐겨찾기 표시, 위도·경도, iCloud 관련 값이 함께 들어 있고, 앨범·얼굴·인물·키워드·공유는 별도 표에 들어갑니다. 사용자가 사진을 찍어 동기화하거나 파일을 가져오거나 다른 앱이 사진을 저장할 때 행이 생기고, 편집하거나 휴지통에 넣을 때 해당 열이 바뀝니다.

iCloud 사진 (iCloud Photos) 을 쓰면 다른 기기에서 찍은 사진도 이 보관함으로 내려오고, 한 기기에서 지우거나 편집한 내용이 iCloud 사진을 쓰는 모든 기기에 반영됩니다[6]. 그래서 보관함은 이 맥 한 대의 기록이라기보다 계정 전체의 사진 기록이 이 맥에 비친 모습에 가깝고, 해석할 때 이 점을 늘 염두에 둡니다.

## 위치와 버전별 차이

### 보관함 위치

기본 보관함은 홈 폴더의 사진(Pictures) 폴더에 들어갑니다[4]. 맥에서 데이터베이스가 있는 경로는 다음과 같습니다[3].

```
/Users/<사용자>/Pictures/Photos Library.photoslibrary/database/Photos.sqlite
```

한 맥에 보관함이 여러 개 있을 수 있고, Option 키를 누른 채 사진 앱을 열면 다른 보관함을 고를 수 있습니다[4]. 기본 위치 하나만 보면 다른 보관함을 놓칠 수 있어서, 디스크 전체에서 `.photoslibrary` 이름을 찾아보는 편이 안전합니다.

### 시스템 사진 보관함

여러 보관함 가운데 하나를 시스템 사진 보관함 (System Photo Library) 으로 정하고, 사진 > 설정(또는 환경설정) > 일반 탭의 "시스템 사진 보관함으로 사용(Use as System Photo Library)" 버튼으로 지정합니다[5]. iCloud 사진과 공유 앨범 (Shared Albums) 은 시스템 사진 보관함에서만 쓸 수 있고[5], 다른 앱이 사진 선택기로 보관함에 접근하려면 이 보관함이 시스템 사진 보관함이어야 합니다[4].

새 보관함을 시스템 사진 보관함으로 지정한 뒤 iCloud 사진을 켜면, 새 보관함의 사진·비디오가 iCloud 사진에 있던 것과 합쳐지고 iCloud의 사진·비디오가 모두 기기로 다시 내려옵니다[5]. 그래서 한 보관함 안에 이 맥에서 찍거나 가져오지 않은 사진이 섞여 있을 수 있습니다. 어느 보관함이 시스템 사진 보관함인지 적어 두는 plist 파일과 키는 공개 자료에 나와 있지 않아 실제 데이터로 확인합니다.

### 사진 앱 버전별 차이

사진 5(macOS 10.15 Catalina) 부터 데이터베이스는 `database/Photos.sqlite`, 원본 파일 폴더는 `originals` 이고, 사진 4 이하는 `database/photos.db` 와 `Masters` 를 씁니다[2]. 사진·비디오 한 건씩을 담는 자산 표 이름은 사진 5에서 `ZGENERICASSET`, 사진 6(Big Sur) 이후 `ZASSET` 입니다[1].

데이터베이스의 모델 버전 숫자로 사진 앱 버전을 가를 수 있고, 범위와 macOS 대응은 다음과 같습니다[1].

| 사진 앱 | macOS | 모델 버전 범위 (osxphotos 상수) | 자산 표 |
|---|---|---|---|
| 사진 5 | 10.15 Catalina | 13000–13999 | `ZGENERICASSET` |
| 사진 6 | 11 Big Sur | 14000–14999 | `ZASSET` |
| 사진 7 | 12 Monterey | 15000–15999 | `ZASSET` |
| 사진 8 | 13 Ventura | 16000–16999 | `ZASSET` |
| 사진 9 | 14 Sonoma | 17000–17599 | `ZASSET` |
| 사진 9 (상수 이름 `_PHOTOS_9_14_6_`) | 14.6 Sonoma | 17600–17999 | `ZASSET` |
| 사진 10 베타 1 (상수 이름 `_PHOTOS_10B1_`) | 15 Sequoia 베타 | 18000–18200 | `ZASSET` |
| 사진 10 | 15 Sequoia | 18201–18999 | `ZASSET` |
| 사진 11 | 26 (소스 주석은 "16/26") | 19063–19319 | `ZASSET` |
| 사진 11.1 | 26.1 | 19320–19999 | `ZASSET` |
| 사진 12 | 27 이후 | 270000000–270999999 | `ZASSET` |

모델 버전 숫자가 데이터베이스 안의 어느 표·열에 있는지는 공개 자료에 나와 있지 않아 실제 데이터로 확인합니다.

공유 앨범 사진과 그 파생본 (derivatives) 이 들어가는 폴더도 버전에 따라 이름이 바뀝니다[1].

| 사진 앱 | 공유 앨범 사진 | 공유 앨범 파생본 |
|---|---|---|
| 사진 5 | `resources/cloudsharing/data` | `resources/cloudsharing/resources/derivatives/masters` |
| 사진 8 | `scopes/cloudsharing/data` | `scopes/cloudsharing/resources/derivatives/masters` |

iCloud 공유 사진 보관함 (iCloud Shared Photo Library) 전용 폴더·열, 섬네일과 편집본 폴더의 이름과 구조는 공개 자료에 나와 있지 않아 실제 데이터로 확인합니다.

## 구조

`Photos.sqlite` 에서 조사에 자주 쓰는 표는 자산 표(`ZGENERICASSET`/`ZASSET`), 부가 속성 표 `ZADDITIONALASSETATTRIBUTES`, 앨범 표 `ZGENERICALBUM`, 그리고 `ZDETECTEDFACE`, `ZPERSON`, `ZKEYWORD`, `ZMOMENT`, `ZSHARE`, `ZFILESYSTEMVOLUME` 입니다[2]. Apple 은 표 구조를 공개하지 않아서, 표의 역할은 표 이름으로 짐작하는 정도입니다. SQLite 파일 자체의 구조와 WAL 처리는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에서 다루고, `Photos.sqlite` 가 WAL 모드로 동작하는지는 옆에 `-wal` 파일이 있는지로 확인합니다.

### 자산 표에서 볼 열

자산 표에서 조사에 쓸 만한 열은 아래와 같습니다[2]. 뜻 열에 참고 문헌 번호가 붙은 것은 공개 도구가 그 값을 쓰는 방식이고, 번호가 없는 것은 열 이름으로 짐작한 뜻입니다.

| 열 | 뜻 |
|---|---|
| `Z_PK`, `ZUUID` | 행 번호와 자산 식별자 |
| `ZDIRECTORY`, `ZFILENAME` | 원본 파일 경로 = 보관함 / `originals` / `ZDIRECTORY` / `ZFILENAME` [2] |
| `ZDATECREATED`, `ZADDEDDATE`, `ZMODIFICATIONDATE` | 시각 열 (아래 "시각 해석" 참고) |
| `ZTRASHEDSTATE`, `ZTRASHEDDATE` | `ZTRASHEDSTATE` 가 `1` 이면 최근 삭제된 항목에 있습니다[2] |
| `ZHIDDEN`, `ZFAVORITE` | 숨김·즐겨찾기 여부[2] |
| `ZKIND`, `ZKINDSUBTYPE`, `ZUNIFORMTYPEIDENTIFIER` | 파일 종류. `ZKIND` 가 `0` 이면 사진, `1` 이면 비디오입니다[1][2] |
| `ZLATITUDE`, `ZLONGITUDE` | 위치 (위치 없는 사진의 기본값은 실제 데이터로 확인) |
| `ZHASADJUSTMENTS`, `ZADJUSTMENTTIMESTAMP` | 편집 여부와 편집 시각으로 보이는 열 |
| `ZCLOUDASSETGUID`, `ZCLOUDBATCHPUBLISHDATE`, `ZCLOUDOWNERHASHEDPERSONID` | iCloud 관련 열 (값의 뜻은 공개 자료 없음) |
| `ZSAVEDASSETTYPE` | 촬영·가져오기·iCloud 내려받기를 구분하는 값으로 보임 (값의 뜻은 공개 자료 없음) |

그 밖에 `ZVISIBILITYSTATE`, `ZMOMENT`, `ZMOMENTSHARE`, `ZHEIGHT`, `ZWIDTH`, `ZORIENTATION`, `ZAVALANCHEUUID`, `ZAVALANCHEPICKTYPE`, `ZCUSTOMRENDEREDVALUE`, `ZSPATIALTYPE` 열이 있습니다[2].

### 부가 속성 표에서 볼 열

`ZADDITIONALASSETATTRIBUTES` 에는 `ZORIGINALFILENAME`, `ZTITLE`, `ZMASTERFINGERPRINT`, `ZTIMEZONEOFFSET`, `ZINFERREDTIMEZONEOFFSET`, `ZTIMEZONENAME`, `ZCAMERACAPTUREDEVICE`, `ZREVERSELOCATIONDATA`, `ZORIGINALRESOURCECHOICE`, `ZORIGINALHEIGHT`, `ZORIGINALWIDTH`, `ZORIGINALORIENTATION`, `ZORIGINALFILESIZE`, `ZIMPORTEDBYDISPLAYNAME`, `ZIMPORTEDBYBUNDLEIDENTIFIER` 열이 있습니다[2]. 열 이름으로 보면 `ZORIGINALFILENAME` 은 가져올 때의 원래 파일 이름이고 `ZFILENAME` 은 보관함 안에 저장한 이름이며, `ZIMPORTEDBYBUNDLEIDENTIFIER`·`ZIMPORTEDBYDISPLAYNAME` 은 어느 앱이 가져왔는지를 나타내는 것으로 보입니다. 번들 ID 읽는 법은 [번들 ID와 팀 ID](../../01-foundations/value-decoding/bundle-team-id.md) 페이지를 봅니다. `ZMASTERFINGERPRINT` 는 원본을 가리키는 식별값으로 보이고, 계산 방식은 공개 자료가 없습니다.

### 앨범 종류 값

`ZGENERICALBUM` 의 `ZKIND` 열 값으로 앨범 종류를 구분할 수 있습니다[1][2].

| 값 | 앨범 종류 |
|---|---|
| `2` | 일반 앨범 |
| `1505` | 공유 앨범 |
| `1506` | 가져오기 세션 앨범 |
| `1508` | 프로젝트 앨범 |
| `3999` | 최상위 폴더 |
| `4000` | 폴더 |

## 증거로서 의미

**증명하는 것.** 자산 표에 행이 있으면 그 사진·비디오가 이 보관함에 등록된 적이 있다는 기록이고, `ZDIRECTORY`·`ZFILENAME` 으로 원본 파일을 찾아 내용과 대조할 수 있습니다. `ZTRASHEDSTATE` 가 `1` 이면 최근 삭제된 항목에 들어 있는 상태이고, `ZTRASHEDDATE` 가 그 시점을 말해 줄 후보입니다. 가져오기 세션 앨범(`1506`)과 공유 앨범(`1505`) 기록은 사진이 어떤 경로로 보관함에 모였는지 좁히는 데 쓸 수 있습니다.

**증명하지 못하는 것.** iCloud 사진을 켠 보관함에서는 행이 있어도 이 맥에서 찍거나 가져왔다고 단정할 수 없고, 휴지통 상태도 이 맥에서 지웠다는 뜻이 아닙니다. 한 기기에서 지운 사진은 iCloud 사진을 쓰는 모든 곳에서 지워지기 때문입니다[6]. 또 저장 공간 최적화 (Optimize Mac Storage) 를 고른 맥에는 공간을 아낀 버전만 남고 원본은 iCloud에 있어서[6], 행이 있는데 `originals` 에 원본이 없을 수 있습니다. 원본 다운로드 (Download Originals to this Mac) 를 고르면 원본이 iCloud와 맥 양쪽에 있습니다[6]. 이 두 설정이 기록되는 plist 키는 공개 자료에 나와 있지 않아 실제 데이터로 확인합니다. 보고서에는 "이 맥의 보관함에 이 시각을 추가 시각으로 하는 자산 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`ZDATECREATED` 같은 날짜 열은 2001-01-01을 기준으로 한 값입니다[2]. 곧 맥 절대 시각 (Mac Absolute Time) 이며, 바꾸는 법은 [맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md) 페이지에 있습니다.

촬영 시각을 현지 시각으로 바꿀 때는 부가 속성 표의 `ZTIMEZONEOFFSET`(과 `ZTIMEZONENAME`) 을 씁니다[2]. 날짜 열 자체가 UTC 기준인지는 공개 자료가 없으니, 보고서에 적을 때는 원래 값과 적용한 시간대 오프셋을 함께 적습니다. 열마다 무엇이 바뀔 때 값이 바뀌는지도 공개 문서가 없고, 열 이름으로 짐작한 뜻은 아래와 같습니다.

| 열 | 열 이름으로 짐작한 뜻 |
|---|---|
| `ZDATECREATED` | 촬영(생성) 시각 |
| `ZADDEDDATE` | 보관함에 들어온 시각 |
| `ZMODIFICATIONDATE` | 레코드 수정 시각 |
| `ZTRASHEDDATE` | 휴지통에 넣은 시각 |

촬영 시각은 파일 안의 메타데이터에서 왔을 수 있어서, 원본 파일의 EXIF 값과 맞춰 봅니다([사진 메타데이터](../embedded-metadata/exif-heic.md)).

## 함정과 한계

- **보관함이 하나라고 가정하는 실수.** 한 맥에 보관함이 여러 개 있을 수 있고[4], iCloud 사진은 시스템 사진 보관함에서만 동작합니다[5]. 보관함마다 따로 분석하고 어느 쪽이 iCloud와 연결됐는지 따져 봅니다.
- **버전에 맞지 않는 표 이름.** Catalina 보관함에는 `ZASSET` 이 없고 `ZGENERICASSET` 이 있어서[1], 다른 버전용 쿼리를 그대로 돌리면 결과가 비거나 오류가 납니다.
- **최근 삭제된 항목 기간.** 지운 항목은 최근 삭제된 항목에서 30일 동안 되살릴 수 있고, 그 뒤에는 영구 삭제됩니다[6]. iCloud 사진을 끈 맥에서도 기간이 같은지, 영구 삭제 뒤 데이터베이스 행이 남는지, `originals` 파일이 언제 지워지는지는 공개 자료에 나와 있지 않아 실제 데이터로 확인합니다. 지운 레코드와 파일을 되살리는 일반 방법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 페이지를 봅니다.
- **열 이름만 보고 뜻을 단정하는 실수.** Apple 은 이 데이터베이스 구조를 공개하지 않았고, 열의 뜻 대부분은 공개 도구 소스와 열 이름에서 짐작한 것입니다. 중요한 결론은 실제 보관함에서 사진을 넣고 지워 보는 식으로 검증한 뒤 씁니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).
- **공개 자료가 없는 부분.** 얼굴 인식·장면 분석을 하는 프로세스와 그 결과 데이터베이스, 사진 앱 관련 통합 로그 서브시스템, 사진 권한이 TCC로 제한되는지와 그 서비스 이름, 사진 4 이하 `photos.db` 표 구조는 공개 자료에 나와 있지 않아 실제 데이터로 확인해야 합니다.

## 직접 분석해 보기

### 헥스로 한 번

`Photos.sqlite` 는 일반 SQLite 파일이라, 헤더와 페이지·레코드를 헥스로 따라가는 방법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지를 그대로 따릅니다. 먼저 보관함 폴더 전체를 사본으로 떠서 작업하고, 사본에서 같은 이름의 `-wal`·`-shm` 파일이 있는지 확인한 뒤 함께 다룹니다. 원본 보관함을 사진 앱이나 SQLite 도구로 직접 열면 파일이 바뀔 수 있습니다.

> 그림 자리: 보관함 패키지 안의 `database/Photos.sqlite` 와 `originals/` 폴더 배치, 자산 행의 `ZDIRECTORY`·`ZFILENAME` 이 원본 파일 경로로 이어지는 모습

### 도구로 한 번

sqlite3 명령행 도구로 사본을 열어, 먼저 버전에 맞는 자산 표가 있는지 봅니다.

```
sqlite3 Photos.sqlite ".tables"
sqlite3 Photos.sqlite ".schema ZADDITIONALASSETATTRIBUTES"
```

사진 6 이후 보관함이라면 아래처럼 휴지통 상태와 시각 열을 뽑고, 사진 5라면 `ZASSET` 을 `ZGENERICASSET` 으로 바꿉니다. 시각은 원래 값 그대로 뽑아 [맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md) 방식으로 바꿉니다.

```
SELECT Z_PK, ZUUID, ZDIRECTORY, ZFILENAME, ZKIND,
       ZDATECREATED, ZADDEDDATE, ZMODIFICATIONDATE,
       ZTRASHEDSTATE, ZTRASHEDDATE, ZHIDDEN,
       ZLATITUDE, ZLONGITUDE, ZCLOUDASSETGUID
FROM ZASSET
ORDER BY ZADDEDDATE;
```

부가 속성 표는 `ZADDITIONALASSETATTRIBUTES.ZASSET` 이 자산 표의 `Z_PK` 를 가리키는 방식으로 이어집니다[2]. 원래 파일 이름과 가져온 앱까지 함께 보려면 아래처럼 잇습니다.

```
SELECT a.Z_PK, a.ZFILENAME, b.ZORIGINALFILENAME,
       b.ZIMPORTEDBYBUNDLEIDENTIFIER, b.ZTIMEZONEOFFSET
FROM ZASSET a
JOIN ZADDITIONALASSETATTRIBUTES b ON b.ZASSET = a.Z_PK;
```

공개 도구 osxphotos 로 같은 사본을 읽어 쿼리 결과와 맞춰 보면, 두 결과로 서로를 검증할 수 있습니다[1][2].

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [아이클라우드 계정](icloud-account.md) | 보관함과 연결된 iCloud 계정 |
| [사진 메타데이터](../embedded-metadata/exif-heic.md) | 원본 파일 안의 촬영 시각·기기·위치 |
| [파일 시스템 이벤트](../filesystem/fsevents/index.md) | 보관함 안 `originals` 파일이 생기고 지워진 흐름 |
| [에어드롭](../external-devices/airdrop.md) | 다른 기기에서 받은 사진이 보관함으로 들어왔는지 |
| [아이폰·아이패드 연결](../external-devices/ios-devices/index.md) | 연결한 기기에서 사진을 가져온 시점 |
| [타임 머신](../filesystem/time-machine/index.md) | 예전 시점의 보관함 사본 |

사진이 보관함에서 사라진 사건은 [지운 파일의 흔적 찾기](../../04-scenarios/activity/deleted-file-traces.md) 시나리오와, 여러 아티팩트의 시각을 시간순으로 합치는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 과 함께 봅니다.

## 실습

NIST CFReDS 같은 공개 시험 데이터 가운데 사진 보관함이 들어 있는 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 디스크에 `.photoslibrary` 보관함이 몇 개 있고, 각각 어떤 사진 앱 버전의 표 이름(`ZGENERICASSET`/`ZASSET`)을 쓰나요?
2. `ZTRASHEDSTATE` 가 `1` 인 자산은 몇 건이고, `ZTRASHEDDATE` 를 맥 절대 시각으로 바꾸면 언제인가요?
3. 자산 행 가운데 `originals` 아래에 원본 파일이 없는 것이 있나요? 있다면 iCloud 설정과 어떻게 맞춰 설명할 수 있나요?
4. `ZORIGINALFILENAME` 과 `ZFILENAME` 이 다른 자산을 골라, 원래 이름에서 어떤 출처를 짐작할 수 있는지 적어 봅니다.
5. 가져오기 세션 앨범(`1506`)의 자산과 USB·아이폰 연결 기록의 시각이 맞물리나요?

## 참고 문헌

1. osxphotos `_constants.py` (RhetTbull/osxphotos, main 브랜치) — https://raw.githubusercontent.com/RhetTbull/osxphotos/main/osxphotos/_constants.py
2. osxphotos `photosdb.py` (RhetTbull/osxphotos, main 브랜치) — https://raw.githubusercontent.com/RhetTbull/osxphotos/main/osxphotos/photosdb/photosdb.py
3. ScottKjr3347, iOS_Local_PL_Photos.sqlite_Queries — https://github.com/ScottKjr3347/iOS_Local_PL_Photos.sqlite_Queries
4. Apple Support, 사진 보관함 관련 문서 (HT201517) — https://support.apple.com/en-us/HT201517
5. Apple Support, "Designate a System Photo Library in Photos" (HT204414) — https://support.apple.com/en-us/HT204414
6. Apple Support, "Set up and use iCloud Photos" (HT204264) — https://support.apple.com/en-us/HT204264
