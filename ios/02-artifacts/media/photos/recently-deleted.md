---
title: "최근 삭제된 항목"
parent: "사진 보관함"
grand_parent: "아티팩트 · 사진·미디어"
nav_order: 570
---

# 최근 삭제된 항목 (Recently Deleted)

## 한 줄 요약

사진 앱에서 지운 사진·동영상은 바로 없어지지 않고 "최근 삭제된 항목" 에 30일 동안 머물며, 그동안 Photos.sqlite 에는 행이 그대로 남은 채 `ZASSET.ZTRASHEDSTATE` 로 삭제 표시만 붙습니다.

## 무엇을 기록하나 · 왜 생기나

지운 사진과 동영상은 "최근 삭제된 항목" 앨범에 30일 동안 있다가 영구 삭제되고[1][2], 30일이 지나면 되살릴 수 없습니다[2]. 이 앨범에서 다시 지운 항목도 되살릴 수 없습니다[1]. 사용자는 사진 앱 > 유틸리티 > 최근 삭제된 항목 에서 Face ID 나 Touch ID 로 앨범을 연 뒤 항목을 골라 복구합니다[2].

DB 에서도 지운 즉시 행을 없애지 않고 `ZASSET.ZTRASHEDSTATE` 를 1 로 바꿔 둡니다. 이 값이 1 인 자산이 최근 삭제된 항목에 있는 자산입니다[6]. 예전 버전에서도 0 은 안 지움, 1 은 지움입니다[4]. 그래서 수집 시점에 최근 삭제된 항목에 있던 사진은 DB 에서 다른 사진과 같은 방법으로 읽을 수 있습니다.

같은 유틸리티에 있는 "가려진 항목" 도 여기서 함께 다룹니다. `ZASSET.ZHIDDEN` 이 1 인 자산이 가려진 항목에 있고[6], iLEAPP 는 최근 삭제를 Ph3, 가려진 항목을 Ph4 파서로 뽑습니다[5].

Photos.sqlite 의 기본 구조는 [사진 DB 구조 (Photos.sqlite)](photos-sqlite.md)에서 다룹니다.

## 위치와 버전별 차이

| iOS 버전 | 바뀐 것 | 출처 |
|---|---|---|
| iOS 16, iPadOS 16.1 이후 | "가려진 항목" 과 "최근 삭제된 항목" 앨범을 볼 때 기본으로 Face ID 나 Touch ID 가 필요하고, 설정 > 앱 > 사진 에서 "Face ID 사용" 을 끄면 풀립니다 | [1] |

보관 기간은 Apple 지원 문서에는 30일로[1][2], 공개 분석 자료에는 "약 30일, 달라질 수 있음" 으로 나옵니다[3]. CameraRollDomain `Media/PhotoData/CPL/cloudphotos-#.#.plist` 의 `configuration` 아래에는 `max.days.inRecentlyDeleted` 키가 있습니다. 이 키가 실제 보관 일수를 정하는지는 분석 대상 기기의 값을 읽어 30일과 맞는지로 확인합니다.

## 구조

Photos.sqlite 에서 삭제와 관련된 열은 아래 표들에 있습니다(iOS 27.0 기준).

| 표 | 열 |
|---|---|
| `ZASSET` | `ZTRASHEDSTATE`, `ZTRASHEDREASON` |
| `ZADDITIONALASSETATTRIBUTES` | `ZPTPTRASHEDSTATE` |
| `ZINTERNALRESOURCE` | `ZTRASHEDSTATE`, `ZTRASHEDDATE`, `ZPTPTRASHEDSTATE` |
| `ZTRANSIENTINTERNALRESOURCE` | `ZTRASHEDSTATE`, `ZTRASHEDDATE` |
| `ZGENERICALBUM` | `ZTRASHEDSTATE`, `ZTRASHEDDATE` |
| `ZMOMENT` | `ZTRASHEDSTATE` |
| `ZSHARE` | `ZTRASHEDSTATE`, `ZTRASHEDDATE`, `ZLASTPARTICIPANTASSETTRASHNOTIFICATIONDATE` |
| `ZDETECTEDFACE` | `ZISINTRASH` |

`ZASSET.ZTRASHEDDATE` 는 삭제 표시가 붙은 시각입니다[3]. `ZTRASHEDREASON` 과 `ZPTPTRASHEDSTATE` 의 값 뜻은 공개된 자료가 없습니다.

앨범에도 `ZTRASHEDSTATE`·`ZTRASHEDDATE` 열이 있어서 앨범 자체에 삭제 표시가 붙을 수 있어 보이지만, 앨범을 지운 뒤 사진 앱이 어떻게 동작하는지는 실제 기기로 확인해야 합니다. 앨범 표는 [앨범과 공유 앨범 (Albums·Shared Albums)](albums-shared.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `ZTRASHEDSTATE` 가 1 인 자산은 수집 시점에 최근 삭제된 항목에 있었다는 사실을 보여 주고[6], `ZTRASHEDDATE` 가 있으면 삭제 표시가 붙은 시각까지 알 수 있습니다[3]. 행은 지워지지 않고 표시만 붙어 있어서, 같은 행의 날짜·파일 열과 촬영 정보 표를 이어 읽으면 지운 사진이 언제 어떤 경로로 보관함에 들어왔는지까지 볼 수 있습니다.

**증명하지 못하는 것.** iCloud 사진이 켜져 있으면 한 기기에서 지운 사진이 같은 Apple 계정의 다른 기기에서도 지워집니다[1]. 그래서 이 기기 DB 의 삭제 표시가 이 기기에서 한 삭제인지, 같은 계정의 다른 기기에서 한 삭제가 넘어온 결과인지는 이 열만으로 구분할 수 없습니다. 누가 지웠는지도 나와 있지 않습니다. 영구 삭제(30일이 지났거나 최근 삭제된 항목에서 다시 지운 경우) 뒤에 DB 행이나 파일 조각이 남는지는 공개된 분석 자료가 없어서, 삭제 표시가 없다고 지운 사진이 없었다고 쓰지 않습니다.

보고서에는 "수집 시점에 이 사진은 최근 삭제된 항목으로 표시되어 있고, 표시된 시각은 이렇다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`ZTRASHEDDATE` 는 삭제 표시된 시각이고 UTC 이며, 최근 삭제로 옮길 때 `ZMODIFICATIONDATE` 도 함께 갱신됩니다[3]. 값은 2001-01-01 을 기준으로 한 Mac 절대 시각이라서 [사진 DB 구조 (Photos.sqlite)](photos-sqlite.md)의 시각 해석 절대로 바꿉니다. `ZMODIFICATIONDATE` 가 삭제 때문에 바뀔 수 있으므로, 삭제 표시가 붙은 자산에서는 이 열을 편집 시각으로 읽지 않습니다.

`ZTRASHEDDATE` 에 30일을 더하면 영구 삭제 예정 시각을 어림할 수 있지만, 보관 기간은 약 30일이고 달라질 수 있어서[3] 어림값이라고 밝혀 씁니다.

## 함정과 한계

컴퓨터(Finder·iTunes)로 동기화해 넣은 사진은 기기의 사진 앱에서 바로 지울 수 없어서[1], 이런 사진에는 사용자가 기기에서 지운 흔적이 생기지 않을 수 있습니다.

가려진 항목과 최근 삭제된 항목은 iOS 16 이후 기본으로 생체 인증을 거쳐야 사진 앱에서 열리고[1], DB 에서는 두 상태가 `ZHIDDEN` 과 `ZTRASHEDSTATE` 로 따로 적힙니다[6]. 화면에서 둘이 같은 유틸리티 아래 있다고 가려진 사진을 지운 사진으로 읽지 않도록 두 열을 따로 봅니다.

지운 행과 WAL·빈 페이지에서 되살리는 방법은 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)와 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

## 직접 분석해 보기

WAL 을 함께 둔 사본을 sqlite3 로 열고 삭제 표시가 붙은 자산을 뽑습니다. `ZASSET` 의 날짜·파일 열[3][6]은 버전마다 다를 수 있어서, 먼저 `PRAGMA table_info(ZASSET);` 로 열이 있는지 확인합니다.

```sql
SELECT Z_PK, ZDIRECTORY, ZFILENAME, ZTRASHEDSTATE, ZTRASHEDREASON, ZHIDDEN,
       datetime('2001-01-01', ZTRASHEDDATE      || ' seconds') AS trashed_utc,
       datetime('2001-01-01', ZTRASHEDDATE      || ' seconds', '+30 days') AS approx_purge_utc,
       datetime('2001-01-01', ZMODIFICATIONDATE || ' seconds') AS modified_utc
FROM ZASSET
WHERE ZTRASHEDSTATE = 1
ORDER BY ZTRASHEDDATE;
```

가려진 항목은 조건을 `ZHIDDEN = 1` 로 바꿔 따로 뽑습니다. 공개 도구로는 iLEAPP 의 Ph3(최근 삭제)과 Ph4(가려진 항목) 파서를 쓰고[5], 도구가 낸 개수가 위 쿼리의 개수와 같은지 먼저 맞춰 봅니다. 날짜 열을 헥스로 따라가는 법은 [사진 DB 구조 (Photos.sqlite)](photos-sqlite.md)의 직접 분석해 보기 절에 있습니다.

## 교차 검증

같은 사진이 다른 곳에 남았는지는 [메시지 (iMessage·SMS)](../../communications/messages/index.md)의 첨부 파일과 [아이클라우드 드라이브 (iCloud Drive)](../../mail-cloud/icloud-drive.md)에서 찾아봅니다. 사진을 지운 시각 앞뒤의 사용 흔적은 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)으로 한 줄에 놓고 봅니다. 조사 흐름은 [지운 대화와 사진 찾기 (Deleted Content)](../../../04-scenarios/activity/deleted-content.md)와 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)를 따릅니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 시험 이미지로 아래를 풀어 봅니다.

1. `ZTRASHEDSTATE = 1` 인 자산과 `ZHIDDEN = 1` 인 자산이 각각 몇 개인지, 둘 다인 자산이 있는지 셉니다.
2. 삭제 표시가 붙은 자산의 `ZTRASHEDDATE` 와 `ZMODIFICATIONDATE` 가 같은지 비교합니다.
3. `ZTRASHEDREASON` 값마다 행이 몇 개인지 세어 봅니다.
4. 가장 이른 `ZTRASHEDDATE` 와 수집 시각의 차이가 30일을 넘는지 확인합니다.

## 참고 문헌

1. Apple 지원, "Delete photos on your iPhone or iPad" — https://support.apple.com/en-us/104967
2. Apple 지원, "How to recover deleted photos on your iPhone, iPad, Mac, or Apple Vision Pro" — https://support.apple.com/en-us/124460
3. The Forensic Scooter (Scott Koenig), "Local Photo Library Photos.sqlite Query Documentation & Notable Artifacts" (2022-05-02) — https://theforensicscooter.com/2022/05/02/photos-sqlite-query-documentation-notable-artifacts/
4. kacos2000, Queries `Photos_sqlite.sql` (GitHub) — https://raw.githubusercontent.com/kacos2000/queries/master/Photos_sqlite.sql
5. The Forensic Scooter, "iLEAPP Parsers & Photos.sqlite Queries" (2024-05-18) — https://theforensicscooter.com/2024/05/18/ileapp-parsers-photos-sqlite-queries/
6. The Forensic Scooter, "Local Photo Library Photos.sqlite Query Variations & WHERE statements" (2022-02-21) — https://theforensicscooter.com/2022/02/21/photos-sqlite-update/
