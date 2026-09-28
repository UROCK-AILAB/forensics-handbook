---
title: "스포트라이트 검색 색인"
parent: "아티팩트 · 입력·음성 비서"
nav_order: 1085
---

# 스포트라이트 검색 색인 (Spotlight·CoreSpotlight)

아이폰의 스포트라이트 검색은 앱이 넘겨준 메시지·메모·메일 같은 내용을 기기 안의 색인 `index.spotlightV2` 에 따로 담아 둡니다. 색인은 앱의 원래 DB 와 별개라서 앱에서 원본을 지워도 색인 항목이 한동안 남을 수 있고, 분석가는 여기서 원본 DB 에 없는 제목·본문·주소를 찾을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

스포트라이트 (Spotlight) 는 기기 전체를 한 번에 찾는 검색 기능입니다. 앱은 코어 스포트라이트 (Core Spotlight) 프레임워크로 자기 내용을 검색 항목 (`CSSearchableItem`) 으로 만들어 기기 안의 색인에 넣고, 이 색인은 기기에만 저장됩니다 [5]. 항목 하나에는 제목·표시 이름·콘텐츠 형식 같은 속성이 붙고 [5], 메시지 본문 글을 담는 `textContent` 속성도 있습니다 [6]. 앱 개발 문서는 즐겨찾기, 구매한 항목, 주고받은 메시지처럼 사용자가 직접 다루는 내용을 색인에 넣도록 권합니다. 앱은 사용자가 앱에서 한 활동 (`NSUserActivity`) 도 색인에 넣을 수 있습니다 [5].

기본 앱도 이 색인을 씁니다. 2020년 발표 자료 기준으로 메모, 지도, 메일, 사파리, 음성 메모와 iOS 의 메시지(iMessage), iOS 의 크롬이 사용자별·iOS 스포트라이트 색인에 자료를 넣고, 서드파티 앱도 자기 속성을 더할 수 있습니다 [4]. 그래서 한 색인 안에 여러 앱의 내용이 섞여 있고, 항목마다 어느 앱이 넣었는지는 번들 ID 속성 (`_kMDItemBundleID`) 으로 구분합니다 [3].

색인 항목은 원본과 따로 지워집니다. 사용자가 앱에서 원래 자료를 지우면 앱이 색인 항목도 지우도록 되어 있고 [5], 만료 날짜 (`expirationDate`) 를 정하지 않은 항목은 일정 기간이 지나면 시스템이 없앱니다 [5][7]. 그래서 앱이 항목을 지우지 않았거나 아직 처리하지 않았으면 원본이 사라진 뒤에도 색인에 남을 수 있습니다.

## 위치와 버전별 차이

파일시스템 추출 기준으로 색인은 보호 등급마다 한 폴더씩 모두 세 곳에 있습니다 [2][3].

```
/private/var/mobile/Library/Spotlight/CoreSpotlight/NSFileProtectionComplete/index.spotlightV2/
/private/var/mobile/Library/Spotlight/CoreSpotlight/NSFileProtectionCompleteUnlessOpen/index.spotlightV2/
/private/var/mobile/Library/Spotlight/CoreSpotlight/NSFileProtectionCompleteUntilFirstUserAuthentication/index.spotlightV2/
```

폴더 이름은 데이터 보호 등급 (Data Protection class) 이름과 같습니다. 앱은 이름 붙인 색인을 만들 때 보호 등급을 고를 수 있고 [8], 연락처처럼 민감한 자료는 더 안전한 색인에 넣으라는 안내가 있습니다 [5]. 보호 등급에 따라 기기 잠금 상태에서 열리는 파일이 달라서, 수집 시점의 잠금 상태에 따라 세 폴더 가운데 일부만 읽힐 수 있습니다. mac_apt 는 `NSFileProtectionComplete`·`NSFileProtectionCompleteUnlessOpen` 폴더의 파일 서명이 맞지 않으면 암호화된 파일로 보고 건너뜁니다 [3]. 보호 등급은 [데이터 보호](../../01-foundations/storage/data-protection/index.md) 에서 다룹니다.

각 폴더에서 볼 파일은 다음과 같습니다.

| 파일 | 담는 것 | 근거 |
|---|---|---|
| `store.db`, `.store.db` | 색인 항목과 속성 값. SQLite 가 아닌 Apple 전용 형식 | [2][4] |
| `dbStr-1.map.*` | 속성 이름 목록 | [2] |
| `dbStr-2.map.*` | 분류(카테고리) 목록 | [2] |
| `dbStr-4.map.*`, `dbStr-5.map.*` | 인덱스 목록 두 개 | [2] |
| `Cache/*/*.txt` | 색인 캐시의 텍스트 파일. 글 내용이 들어 있음. iLEAPP 는 `NSFileProtectionCompleteUntilFirstUserAuthentication` 폴더에서만 찾음 | [1] |

`dbStr-*` 파일은 각각 `.map.data`, `.map.offsets`, `.map.header` 세 개로 이루어지고, 같은 폴더의 `store.db` 와 짝을 이룹니다 [2]. 이 파일이 없으면 iOS 의 `store.db` 는 속성 이름을 풀 수 없어서, 파일 하나가 아니라 폴더째 수집해야 합니다 [2].

버전별로 보면, `index.spotlightV2` 경로는 2020년 12월 발표 자료에도 같게 나와 있고 [4], iLEAPP 의 캐시 텍스트 시험 표본은 iOS 18.3.2(468행), 18.7(126행), 18.7.8(13행) 입니다 [1]. 표본의 행 수는 기기 사용량에 따라 다르므로 버전 차이로 읽지 않습니다. 맥의 사용자 색인은 `~/Library/Metadata/CoreSpotlight/` 아래(macOS 12 이상은 보호 등급 폴더 아래) `index.spotlightV3` 로 이름이 다릅니다 [2][3].

로컬 백업에 이 폴더가 들어가는지는 백업마다 `Manifest.db` 의 경로 목록에서 `Library/Spotlight` 를 찾아 확인합니다. 백업을 읽는 법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md), 수집 범위를 정하는 법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에 있습니다.

## 구조

`store.db` 는 블록으로 나뉜 전용 형식이고, 블록 위치는 0x1000(4096바이트) 단위로 적혀 있습니다 [2]. 파일 맨 앞 4바이트가 `38 74 73 64`(`8tsd`) 이면 2판 형식이고, 오프셋 36·40·44 에 헤더 크기·첫 블록 크기·블록 크기가 4바이트씩 있습니다 [2]. 오프셋 48 의 4바이트(속성 블록 위치)가 0 이면 속성·분류·인덱스가 파일 안이 아니라 `dbStr-*` 파일에 있다는 뜻이고, 공개 파서는 이것으로 iOS 색인(또는 맥 사용자 색인)을 구분합니다 [2]. 오프셋 0x144 부터 256바이트에는 원래 경로 문자열이 있습니다 [2].

헤더 뒤 첫 블록은 서명이 `1mbd` 또는 `2mbd` 이고, 여기에 항목 블록의 위치 목록이 있습니다 [2]. 나머지 블록은 서명이 `2pbd` 이고, 블록 종류 0x09 가 항목(메타데이터) 블록입니다 [2]. 항목 블록은 압축되어 있어서 블록 종류 값에 따라 LZ4(`bv41` 조각), LZFSE(`bvx1`·`bvx2`·`bvxn`), zlib 가운데 하나로 풉니다 [2].

풀린 항목 하나에는 항목 ID, 플래그, 저장소 ID(`Store_ID`), 상위 ID, 마지막 갱신 시각이 먼저 오고 그 뒤에 속성 이름과 값이 이어집니다 [2]. 도구 결과에서 자주 보는 속성은 다음과 같습니다.

| 속성 | 뜻 | 근거 |
|---|---|---|
| `_kMDItemBundleID` | 항목을 넣은 앱의 번들 ID | [3] |
| `kMDItemContentType` | 콘텐츠 형식(UTI) | [3] |
| `kMDItemDisplayName` | 표시 이름 | [2][4] |
| `kMDItemAuthorAddresses`, `kMDItemRecipientAddresses` | 보낸 사람·받는 사람 주소(맥 메시지 예시) | [4] |

본문이 어느 속성 이름으로 나오는지는 앱과 버전마다 다를 수 있으므로, 도구 결과에서 사건 관련 낱말로 먼저 검색하고 그 낱말이 걸린 속성 이름을 확인합니다. 번들 ID 를 읽는 법은 [번들 ID 와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에 있습니다.

`.store.db` 는 `store.db` 와 같은 형식의 두 번째 파일입니다. 맥 볼륨 색인을 시험한 결과로는 변경이 `.store.db` 에 먼저 적히고 나중에 `store.db` 에 반영되었습니다 [9]. mac_apt 는 `.store.db` 에서 `store.db` 에 없는 항목이나 갱신된 항목만 이름이 `-.store-DIFF` 로 끝나는 표로 따로 냅니다 [3].

## 증거로서 의미

**증명하는 것**

색인 항목이 있으면 그 번들 ID 의 앱이 이 내용(제목·주소·본문)을 이 기기의 검색 색인에 넣은 적이 있다고 말할 수 있습니다 [3][5]. 같은 내용이 앱의 원래 DB 에 없으면, 원본이 지워졌거나 옮겨졌는데 색인 항목은 남아 있을 가능성이 있습니다. 이때는 지운 메시지·메모의 제목이나 본문을 색인에서 볼 수 있습니다.

**증명하지 못하는 것**

색인 항목만으로는 사용자가 그 내용을 언제 쓰거나 읽었는지, 스포트라이트에서 검색했는지 알 수 없습니다. 항목은 앱이 색인에 넣은 것이라, 항목이 있다고 사용자가 그 내용을 열어 봤다는 뜻은 아닙니다 [5]. 앱이 색인에 넣지 않았거나, 앱이 지웠거나, 만료로 사라졌을 수 있으므로 색인에 없다고 원본이 없었다고 판단하지도 않습니다 [5][7]. 누가 원본을 지웠는지, 언제 지웠는지도 색인으로는 알 수 없습니다.

보고서에는 "이 앱이 넣은 검색 색인 항목에 이 제목과 본문이 있고, 수집 시점에 앱의 대화 DB 에는 같은 메시지가 없다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

| 값 | 기준 | 근거 |
|---|---|---|
| 항목의 마지막 갱신 시각(도구 출력 `Last_Updated`·`Date_Updated`) | 1970-01-01 기준 마이크로초. UTC 로 바꿔 출력 | [2][3] |
| 날짜 형식 속성 값(예: 콘텐츠 만든 날짜) | 8바이트 실수, Mac 절대 시각(2001-01-01 기준 초) | [2] |
| iLEAPP 캐시 텍스트의 `File Modified Time` | 추출된 파일의 수정 시각을 UTC 로 표시 | [1] |

마지막 갱신 시각은 색인이 그 항목을 고친 때를 가리키는 이름이라서, 메시지를 보내거나 메모를 쓴 때로 읽지 않습니다. 발표 자료의 맥 예시에서도 2019-10-17 에 만든 파일의 항목에 마지막 갱신 시각이 2020-12-02 로 적혀 있습니다 [4]. 내용의 시각은 속성 값에 든 날짜를 보고, 그 날짜가 무엇을 뜻하는지는 앱의 원래 DB 시각과 맞춰 확인합니다. 두 기준(1970·2001)을 섞으면 31년쯤 어긋나므로 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 기준을 확인하고, 현지 시각으로 바꿀 때는 [시간대와 시각 설정](../system-account/time-zone.md) 을 봅니다.

iLEAPP 의 캐시 텍스트 시각은 파일 내용이 아니라 파일시스템의 수정 시각이라서 [1], 추출 도구가 원래 시각을 보존하지 않으면 추출한 시각이 나옵니다. mac_apt 는 다른 표시가 없으면 날짜와 시각을 UTC 로 출력합니다 [4].

## 함정과 한계

공개 파서는 첫 블록의 위치 목록에 올라 있는 항목 블록만 읽습니다 [2]. 그래서 목록에서 빠진 블록이 파일 안에 남아 있어도 결과에는 나오지 않으니, 결과에 없다고 파일 안에 흔적이 없다고 판단하지 않습니다. 맥 볼륨 색인을 시험한 연구에서는 파일을 지우고 5분 안에 색인 항목도 지워졌고, 지운 항목은 색인 파일 안에서 되살릴 수 없었습니다 [9]. FAT32 볼륨의 색인만은 예외라서 항목이 시험 내내 남았습니다 [9]. 한 폴더의 파일을 한꺼번에 지웠을 때는 색인에서 빠진 페이지를 파일시스템의 미할당 공간에서 되살릴 수 있었습니다 [9]. 이 결과는 macOS 볼륨 색인의 시험 조건에서 나온 것이라, iOS 앱 색인에 그대로 적용하지 않습니다. 지운 데이터를 찾는 일반 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 있습니다.

`dbStr-*` 파일을 빼고 `store.db` 만 가져오면 공개 파서는 처리를 멈춥니다 [2]. iLEAPP 의 스포트라이트 항목은 `Cache` 폴더의 텍스트 파일만 읽고 `store.db` 는 풀지 않으므로 [1], iLEAPP 보고서에 스포트라이트 행이 적다고 색인이 작다고 판단하지 않습니다.

한 색인에 여러 앱의 항목이 섞여 있고 앱이 속성을 스스로 정하므로 [4][5], 같은 속성 이름도 앱마다 담는 값이 다를 수 있습니다. 항목을 해석할 때는 번들 ID 부터 확인하고 앱별로 따로 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 공개 파서 코드의 헤더 정의로 만든 예시이고, 특정 기기에서 뽑은 값이 아닙니다(만든 예시).

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
000000  38 74 73 64 .. .. .. .. .. .. .. .. .. .. .. ..   8tsd = 2판 형식
000020  .. .. .. .. 00 10 00 00 .. .. .. .. 00 10 00 00   0x24 헤더 크기, 0x2C 블록 크기
000030  00 00 00 00 .. .. .. .. .. .. .. .. .. .. .. ..   0x30 속성 블록 위치 = 0 → 속성은 dbStr 파일에
```

값은 모두 리틀 엔디언입니다 [2]. 헤더 크기만큼 건너뛴 자리에서 `1mbd`·`2mbd` 서명의 첫 블록을 찾고, 거기 적힌 위치 × 0x1000 자리에서 `2pbd` 서명의 항목 블록을 확인합니다 [2]. 블록 안쪽 오프셋 20 부터가 압축된 데이터라서, `bv41` 이나 `bvx2` 같은 표지가 보이면 어떤 압축인지 알 수 있습니다 [2].

### 공개 도구로 한 번

spotlight_parser 는 `store.db` 경로와 출력 폴더를 받고, 같은 폴더의 `dbStr-*` 파일을 함께 읽습니다 [2].

```
python spotlight_parser.py ./NSFileProtectionComplete/index.spotlightV2/store.db ./out
```

결과는 `spotlight-store_data.txt` 한 파일로 나오고, iOS 색인에서는 전체 경로 파일(`_fullpaths.tsv`)을 만들지 않습니다 [2]. 항목마다 아래 모양으로 적힙니다(만든 예시).

```
------------------------------------------------------------
Inode_Num --> 1234
Flags --> 0
Store_ID --> 5678
Parent_Inode_Num --> 1
Last_Updated --> 2026-01-02 03:04:05.123456
_kMDItemBundleID --> com.example.notes
kMDItemContentType --> ...
kMDItemDisplayName --> 회의 메모
```

mac_apt 의 SPOTLIGHT 플러그인은 세 폴더의 `store.db` 와 `.store.db` 를 모두 읽고, iOS 색인은 번들 ID 마다 보기(view)를 만들어 앱별로 볼 수 있게 합니다 [3][4]. iLEAPP 의 `spotlightIndex.py` 는 `Cache` 텍스트 파일의 내용·폴더·파일 이름·수정 시각을 표로 보여 줍니다 [1]. 도구 결과를 보고서에 쓰기 전에 원본 파일과 한두 항목을 맞춰 보는 절차는 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에 있습니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [지운 메시지의 흔적](../communications/messages/deleted-messages.md), [대화 DB 구조 (sms.db)](../communications/messages/sms-db.md) | 색인의 메시지 본문이 sms.db 에 아직 있는지, 최근 삭제된 항목에 들어 있는지 |
| [메모](../mail-cloud/notes.md), [Apple 메일](../mail-cloud/apple-mail.md) | 색인의 제목·본문이 원래 DB 에 남아 있는지 |
| [사파리 방문 기록](../browsers/safari/history.md) | 사파리 설정의 `didMigrateHistoryToCoreSpotlightAfterUpgrade` 와 색인의 사파리 항목 |
| [텔레그램](../messengers/telegram.md) | 앱이 스포트라이트에 넘기려고 따로 만든 연락처 캐시 |

원본 DB 에 없는 내용이 색인에서만 나오면 [지운 대화와 사진 찾기](../../04-scenarios/activity/deleted-content.md) 와 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름에 넣어 다른 기록과 함께 봅니다.

## 실습

공개 iOS 시험 자료(NIST CFReDS 등)의 파일시스템 추출 이미지로 다음 질문을 풀어 봅니다.

1. `Library/Spotlight/CoreSpotlight/` 아래 세 폴더 가운데 `store.db` 와 `dbStr-*` 파일이 모두 있는 폴더는 어디입니까?
2. `store.db` 맨 앞 4바이트와 오프셋 48 의 값을 헥스로 읽고, 이 파일이 속성을 `dbStr` 파일에 두는 형식인지 판별합니다.
3. spotlight_parser 결과에서 `_kMDItemBundleID` 값별 항목 수를 세고, 메시지·메모·메일 앱의 항목을 골라 냅니다.
4. 3번에서 고른 메시지 항목의 본문을 sms.db 에서 찾아보고, 색인에만 있는 항목이 있는지 확인합니다.

## 참고 문헌

1. iLEAPP `scripts/artifacts/spotlightIndex.py` (Spotlight Index Cache V2) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/spotlightIndex.py
2. Yogesh Khatri, spotlight_parser (README, `spotlight_parser.py` 1.0.4) — https://github.com/ydkhatri/spotlight_parser
3. mac_apt `plugins/spotlight.py`, `plugins/helpers/spotlight_filter.py` — https://github.com/ydkhatri/mac_apt/blob/master/plugins/spotlight.py , https://github.com/ydkhatri/mac_apt/blob/master/plugins/helpers/spotlight_filter.py
4. Yogesh Khatri, "Spotlight – Forensic Goldmine in iOS & macOS" (NW3C 발표 자료, 2020-12) — https://github.com/ydkhatri/Presentations/blob/master/NW3C%20Spotlight%20on%20iOS%20and%20macOS-%20December%202020.pdf
5. Apple Developer, "Adding your app's content to Spotlight indexes" / `CSSearchableItem` — https://developer.apple.com/documentation/corespotlight/adding-your-app-s-content-to-spotlight-indexes , https://developer.apple.com/documentation/corespotlight/cssearchableitem
6. Apple Developer, `CSSearchableItemAttributeSet.textContent` — https://developer.apple.com/documentation/corespotlight/cssearchableitemattributeset/textcontent
7. Apple Developer, `CSSearchableItem.expirationDate` — https://developer.apple.com/documentation/corespotlight/cssearchableitem/expirationdate
8. Apple Developer, `CSSearchableIndex.init(name:protectionClass:)` — https://developer.apple.com/documentation/corespotlight/cssearchableindex/init(name:protectionclass:)
9. T. S. Atwal, M. Scanlon, N.-A. Le-Khac, "Shining a light on Spotlight: Leveraging Apple's desktop search utility to recover deleted file metadata on macOS", Digital Investigation, 2019. DOI: 10.1016/j.diin.2019.01.019 — https://arxiv.org/abs/1903.07053
