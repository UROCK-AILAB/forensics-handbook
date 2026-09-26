---
title: "앨범과 공유 앨범"
parent: "사진 보관함"
grand_parent: "아티팩트 · 사진·미디어"
nav_order: 560
---

# 앨범과 공유 앨범 (Albums·Shared Albums)

## 한 줄 요약

사진 앱의 앨범과 폴더, 공유 앨범은 Photos.sqlite 의 `ZGENERICALBUM` 에 함께 들어 있고, 공유 앨범의 댓글·초대·피드와 iCloud 링크 공유, 공유 사진 보관함은 별도 표에 남습니다.

## 무엇을 기록하나 · 왜 생기나

사용자가 앨범을 만들거나 공유 앨범에 참여하면 사진 앱은 그 앨범을 `ZGENERICALBUM` 에 행으로 적고, 어떤 자산이 어느 앨범에 들어 있는지는 연결 표에 따로 적습니다[2][5]. 공유 앨범은 여러 사람이 사진을 올리고 댓글을 다는 곳이라서, 앨범 행 말고도 소유자 이름, 초대받은 사람, 댓글과 반응, 새 항목 피드가 표로 남습니다. 누구와 사진을 나눴는지, 누가 어떤 사진을 올렸는지를 묻는 조사에서 이 표들을 봅니다.

공유 앨범을 지우면 내 기기와 구독자 기기 모두에서 자동으로 사라지고 앨범 안의 사진도 영구히 지워집니다[1]. 소유자는 누구의 사진·동영상·댓글이든 지울 수 있지만 구독자는 자기가 올린 것만 지울 수 있습니다[1]. "공개 웹사이트" 를 켜면 누구나 웹 브라우저로 앨범을 볼 수 있습니다[1].

Photos.sqlite 의 기본 구조와 `ZASSET` 은 [사진 DB 구조 (Photos.sqlite)](photos-sqlite.md)에서 다룹니다.

## 위치와 버전별 차이

모든 표는 Photos.sqlite 안에 있고, 파일 위치는 [사진 보관함 (Photos Library)](index.md)에 있습니다. 공유 앨범 사진 파일은 `PhotoData/PhotoCloudSharingData/` 아래에 따로 놓이고, `ZASSET.ZSAVEDASSETTYPE` 값이 4 입니다[2][3].

| iOS 버전 | 바뀐 것 | 출처 |
|---|---|---|
| iOS 16 이후 | iCloud 공유 사진 보관함(Shared Photo Library)이 생겼고, iLEAPP 는 Ph31~33 파서로 읽습니다 | [4] |
| iOS 27·iPadOS 27 이후 | 공유 앨범이 원본 해상도 공유, 새 필터·정렬, 이모지 반응, 다른 사람을 앨범에 초대하는 새 방법을 지원하고, Apple 계정이나 Apple 기기가 없어도 웹으로 참여해 사진을 올릴 수 있습니다 | [1] |

iOS 27 이후 공유 앨범은 설정 > [이름] > iCloud > 사진 에서 "공유 앨범" 을 켜서 씁니다[1]. iOS 27.0 의 Photos.sqlite 에는 `ZSHAREPOST` 와 `ZCOLLECTIONSHAREMIGRATIONATTRIBUTES` 표도 있습니다. 두 표의 뜻과 iOS 27 의 공유 앨범 변경과 이어지는지는 실제 데이터로 확인해야 합니다.

## 구조

### 앨범 표 (ZGENERICALBUM)

`ZGENERICALBUM` 에는 아래 열이 있습니다(iOS 27.0 기준). 아래는 일부이고 다른 열이 더 있을 수 있습니다.

| 묶음 | 열 |
|---|---|
| 앨범 정보 | `ZKIND`, `ZTITLE`, `ZUUID`, `ZPARENTFOLDER`, `ZISPINNED`, `ZPRIVACYSTATE`, `ZCACHEDCOUNT`, `ZCACHEDPHOTOSCOUNT`, `ZCACHEDVIDEOSCOUNT` |
| 시각 | `ZCREATIONDATE`, `ZSTARTDATE`, `ZENDDATE`, `ZLASTMODIFIEDDATE`, `ZTRASHEDDATE` |
| 상태 | `ZTRASHEDSTATE`, `ZCLOUDLOCALSTATE`, `ZCLOUDDELETESTATE` |
| 가져오기 | `ZIMPORTEDBYBUNDLEIDENTIFIER`, `ZIMPORTSESSIONID` |
| 공유 앨범 | `ZCLOUDGUID`, `ZCLOUDCREATIONDATE`, `ZCLOUDLASTCONTRIBUTIONDATE`, `ZCLOUDSUBSCRIPTIONDATE`, `ZCLOUDOWNERFIRSTNAME`, `ZCLOUDOWNERLASTNAME`, `ZCLOUDOWNERFULLNAME`, `ZCLOUDOWNERHASHEDPERSONID`, `ZCLOUDOWNEREMAILKEY`, `ZCLOUDPUBLICURLENABLED`, `ZCLOUDMULTIPLECONTRIBUTORSENABLED`, `ZISOWNED`, `ZUNSEENASSETSCOUNT` |

`ZKIND` 는 앨범의 종류를 구분하는 열입니다. macOS 사진 보관함 기준 값은 아래와 같고[5], iOS 에서도 같은 값인지는 실제 데이터로 확인합니다.

| `ZKIND` | 뜻 |
|---|---|
| 2 | 사용자가 만든 앨범 |
| 1505 | 공유 앨범 |
| 1506 | 가져오기 세션 |
| 1508 | 프로젝트 |
| 3999 | 최상위 폴더 |
| 4000 | 사용자 폴더 |

일반 앨범은 부모가 최상위 폴더(Root Folder)라서[2] `ZPARENTFOLDER` 를 따라가면 폴더 구조를 되살릴 수 있습니다. iCloud 사진을 켠 기기에서는 일반 앨범의 `ZCLOUDLOCALSTATE` 가 1, 공유 앨범이 0 으로 나뉘지만[3], iCloud 사진을 끈 기기에서는 일반 앨범도 0 이라서[2] 이 열만으로 공유 앨범을 구분하지 않습니다.

### 자산과 앨범의 연결 표

자산과 앨범은 `Z_##ASSETS` 형식의 연결 표로 잇고, macOS 11 이후 기준으로 열은 `Z_##ALBUMS`, `Z_3ASSETS`, 앨범 안 순서를 담는 `Z_FOK_3ASSETS` 입니다[5]. macOS 10.15 에서는 자산 열이 `Z_34ASSETS`, 순서 열이 `Z_FOK_34ASSETS` 였습니다[5]. 표 번호도 버전마다 바뀌고, macOS 사진 보관함 기준 번호는 아래와 같습니다[5].

| macOS | 연결 표 |
|---|---|
| 10.15, 11 | `Z_26ASSETS` |
| 12 | `Z_27ASSETS` |
| 13, 14 | `Z_28ASSETS` |
| 14.6 | `Z_29ASSETS` |
| 15.0 베타 1 | `Z_31ASSETS` |
| 15 | `Z_30ASSETS` |
| 26 | `Z_32ASSETS` |
| 26.1 | `Z_33ASSETS` |
| 27.0(개발자 베타 기준) | `Z_34ASSETS` |

iOS 버전별 번호는 공개된 자료가 없어서, 분석하는 DB 마다 `sqlite_master` 에서 표 이름을 먼저 찾습니다.

### 공유 앨범의 활동 표

공유 앨범의 댓글·피드·초대는 아래 표에 있습니다.

| 표 | 열(일부) |
|---|---|
| `ZCLOUDSHAREDCOMMENT` | `ZCOMMENTTEXT`, `ZCOMMENTDATE`, `ZCOMMENTCLIENTDATE`, `ZISLIKE`, `ZISMYCOMMENT`, `ZCOMMENTERHASHEDPERSONID`, `ZREACTTEXT`, `ZCOMMENTEDASSET` |
| `ZCLOUDFEEDENTRY` | `ZENTRYDATE`, `ZENTRYTYPE`, `ZENTRYISMINE`, `ZENTRYALBUMGUID`, `ZENTRYCLOUDASSETGUID` |
| `ZCLOUDSHAREDALBUMINVITATIONRECORD` | `ZINVITEEFULLNAME`, `ZINVITEEFIRSTNAME`, `ZINVITEELASTNAME`, `ZINVITEEEMAILKEY`, `ZINVITEEHASHEDPERSONID`, `ZINVITEESUBSCRIPTIONDATE`, `ZINVITATIONSTATE`, `ZISMINE`, `ZALBUMGUID` |

`ZREACTTEXT` 는 이름으로 보면 iOS 27 의 이모지 반응과 이어질 가능성이 있습니다. `ZCOMMENTDATE` 와 `ZCOMMENTCLIENTDATE` 가 서로 어떻게 다른지는 공개된 자료가 없어서, 보고서에는 두 열을 모두 적고 차이가 크면 따로 밝힙니다.

### 링크 공유와 참여자 (ZSHARE·ZSHAREPARTICIPANT)

`ZSHARE` 는 iCloud 링크 공유 등에 쓰이고, `ZSTATUS`, `ZCREATIONDATE`, `ZSTARTDATE`, `ZENDDATE`, `ZEXPIRYDATE`, `ZTITLE`, `ZSHAREURL`, `ZASSETCOUNT`, `ZUUID`, `ZPUBLICPERMISSION` 열이 있습니다[2]. iOS 27.0 의 `ZSHARE` 에는 `ZCOLLECTIONSHAREKIND`, `ZSCOPETYPE`, `ZSCOPEIDENTIFIER`, `ZTITLE`, `ZCREATIONDATE`, `ZACCEPTANCEDATE`, `ZEXPIRYDATE`, `ZTRASHEDSTATE`, `ZTRASHEDDATE`, `ZPUBLICURLSTATE`, `ZALLOWSANONYMOUSPUBLICACCESS` 열도 있습니다.

참여자는 `ZSHAREPARTICIPANT` 에 있고, `ZEMAILADDRESS`, `ZPHONENUMBER`, `ZPARTICIPANTROLE`, `ZACCEPTANCESTATUS`, `ZISCURRENTUSER`, `ZCONTRIBUTEDASSETSCOUNT`, `ZSUBSCRIPTIONDATE` 열이 있습니다.

### 공유 사진 보관함

iCloud 공유 사진 보관함은 iOS 16 이후 기능이고[4], `ZASSET` 에는 `ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE` 와 `ZLIBRARYSCOPESHARESTATE` 열이 있습니다. 두 열의 값 뜻은 실제 데이터로 확인해야 합니다.

### 사진 앱 설정

CameraRollDomain 의 `Media/PhotoData/private/com.apple.mobileslideshow/appPrivateData.plist` 에는 `HasSignificantRegularAlbumCount`, `HasSignificantSharedAlbumActivities` 같은 키가 있습니다. 이름으로 보면 앨범 수와 공유 앨범 활동이 많은지를 적은 값으로 보이고, 기준은 공개된 자료가 없습니다.

## 증거로서 의미

**증명하는 것.** `ZGENERICALBUM` 에 공유 앨범 행이 있으면 수집 시점에 이 기기가 그 공유 앨범을 알고 있었다는 사실을 보여 주고, 소유자 이름 열과 `ZISOWNED` 로 누가 만든 앨범인지를 추정할 수 있습니다. `ZCLOUDSHAREDCOMMENT` 의 `ZISMYCOMMENT`, `ZCLOUDFEEDENTRY` 의 `ZENTRYISMINE` 은 이름으로 보면 이 기기 사용자의 활동인지를 구분하는 열이라서, 실제 데이터에서 값 분포를 확인한 뒤 누가 댓글을 달고 사진을 올렸는지를 나누는 데 씁니다.

**증명하지 못하는 것.** 공유 앨범은 여러 사람이 사진을 올리는 곳이고 소유자는 남의 사진·댓글을 지울 수 있어서[1], 앨범에 사진이 있다고 이 기기 사용자가 올렸다는 뜻은 아니고, 없다고 올린 적이 없다는 뜻도 아닙니다. iOS 27 부터는 Apple 계정이 없는 사람도 웹으로 사진을 올릴 수 있어서[1], 올린 사람을 Apple 계정으로만 찾지 않습니다. 앨범을 지우면 모든 참여자 기기에서 사라지므로[1] 행이 없다는 사실만으로 참여한 적이 없다고 쓰지 않습니다.

보고서에는 "이 기기의 사진 DB 에 이런 이름의 공유 앨범과 이 참여자가 기록되어 있고, 이 기기 사용자 것으로 표시된 댓글이 몇 건 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

앨범과 공유 표의 날짜 열도 Mac 절대 시각이고, 바꾸는 법은 [사진 DB 구조 (Photos.sqlite)](photos-sqlite.md)의 시각 해석 절에 있습니다. `ZCLOUDCREATIONDATE`, `ZCLOUDLASTCONTRIBUTIONDATE`, `ZCLOUDSUBSCRIPTIONDATE` 는 이름으로 보면 공유 앨범을 만든 시각, 마지막으로 사진이 올라온 시각, 구독한 시각으로 보입니다. 이름이 비슷한 `ZCREATIONDATE` 와 `ZCLOUDCREATIONDATE` 가 다를 수 있으니 둘을 섞어 쓰지 않습니다.

## 함정과 한계

`ZKIND` 값과 연결 표 번호는 macOS 사진 보관함 기준 값이라서[5], iOS 데이터에서는 값 분포와 표 이름을 먼저 확인합니다. `ZSHARE` 는 iCloud 링크 공유 등에 쓰이는 표이지만[2] `ZCOLLECTIONSHAREKIND`·`ZSCOPETYPE` 의 값 뜻은 공개된 자료가 없어서, 행마다 어떤 방식의 공유인지 단정하지 않습니다.

## 직접 분석해 보기

먼저 연결 표 이름을 찾습니다.

```sql
SELECT name FROM sqlite_master
WHERE type = 'table' AND name LIKE 'Z\_%ASSETS' ESCAPE '\';
```

찾은 번호를 `nn` 자리에 넣어 앨범별 자산을 뽑습니다. 열 이름도 `PRAGMA table_info(Z_nnASSETS);` 로 확인합니다.

```sql
SELECT g.Z_PK, g.ZKIND, g.ZTITLE, g.ZCLOUDOWNERFULLNAME, g.ZISOWNED,
       datetime('2001-01-01', g.ZCLOUDCREATIONDATE || ' seconds') AS cloud_created_utc,
       a.Z_PK AS asset_pk, a.ZSAVEDASSETTYPE
FROM ZGENERICALBUM g
JOIN Z_nnASSETS j ON j.Z_nnALBUMS = g.Z_PK
JOIN ZASSET a     ON a.Z_PK = j.Z_3ASSETS
ORDER BY g.Z_PK, j.Z_FOK_3ASSETS;
```

공유 앨범 댓글은 이렇게 읽습니다.

```sql
SELECT c.ZCOMMENTEDASSET, c.ZISMYCOMMENT, c.ZISLIKE, c.ZCOMMENTTEXT, c.ZREACTTEXT,
       datetime('2001-01-01', c.ZCOMMENTDATE || ' seconds') AS comment_utc
FROM ZCLOUDSHAREDCOMMENT c
ORDER BY c.ZCOMMENTDATE;
```

공개 도구 iLEAPP 는 자산과 앨범을 Ph2, 앨범과 공유 앨범을 Ph20~24, 공유 사진 보관함을 Ph31~33 파서로 나눠 읽습니다[4]. 도구 결과는 위 쿼리로 몇 행을 맞춰 보고 씁니다.

## 교차 검증

공유 앨범 참여자와 초대받은 사람은 [연락처 (AddressBook)](../../communications/contacts.md)에서 이름과 이메일을 맞춰 보고, 계정 정보는 [애플 계정 (Apple Account)](../../system-account/apple-account.md)에서 봅니다. 사진을 밖으로 나눈 흐름은 [자료를 밖으로 보냈나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md)와 [누구와 연락을 주고받았나 (Communication)](../../../04-scenarios/activity/communication.md)에서 이어 봅니다. 서버 쪽 공유 기록은 [클라우드 데이터 (iCloud·계정 데이터 요청)](../../../03-techniques/acquisition/cloud-data.md)에서 다룹니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 시험 이미지로 아래를 풀어 봅니다.

1. `ZGENERICALBUM.ZKIND` 값마다 행이 몇 개인지 세고, macOS 기준 값 표와 맞는지 봅니다.
2. 시험 이미지에서 연결 표 번호를 찾고, 그 이미지의 iOS 버전과 함께 적어 둡니다.
3. 공유 앨범 하나를 골라 `ZISMYCOMMENT` 가 참인 댓글과 거짓인 댓글이 몇 건인지 셉니다.
4. `ZCLOUDSHAREDALBUMINVITATIONRECORD` 의 초대받은 사람을 연락처와 맞춰 봅니다.

## 참고 문헌

1. Apple 지원, "How to use Shared Albums in Photos on your iPhone, iPad, or Apple Vision Pro" — https://support.apple.com/en-us/108314
2. The Forensic Scooter (Scott Koenig), "Local Photo Library Photos.sqlite Query Documentation & Notable Artifacts" (2022-05-02) — https://theforensicscooter.com/2022/05/02/photos-sqlite-query-documentation-notable-artifacts/
3. The Forensic Scooter, "Local Photo Library Photos.sqlite Query Variations & WHERE statements" (2022-02-21) — https://theforensicscooter.com/2022/02/21/photos-sqlite-update/
4. The Forensic Scooter, "iLEAPP Parsers & Photos.sqlite Queries" (2024-05-18) — https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/
5. RhetTbull, osxphotos `_constants.py` (macOS 사진 보관함 기준, GitHub) — https://raw.githubusercontent.com/RhetTbull/osxphotos/main/osxphotos/_constants.py
