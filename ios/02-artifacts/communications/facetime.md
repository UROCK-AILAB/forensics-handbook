---
title: "페이스타임"
parent: "아티팩트 · 통화·메시지·연락처"
nav_order: 530
---

# 페이스타임 (FaceTime)

## 한 줄 요약

FaceTime 통화는 내용이 종단 간 암호화되어 기기에서 찾을 흔적이 통화 기록의 행과 계정·설정 파일 같은 메타데이터이고, FaceTime 만의 통화 DB 는 로컬 백업에 없습니다.

## 무엇을 기록하나 · 왜 생기나

FaceTime 영상·음성 통화는 전화 통화와 같은 통화 기록 데이터베이스(`CallHistory.storedata`)의 `ZCALLRECORD` 표에 한 행씩 남고, 통화 종류 칸 `ZCALLTYPE` 값으로 FaceTime 영상인지 음성인지 가립니다 [1]. 표 구조와 값 목록, 시각 해석은 [통화 기록](call-history.md) 에서 다루고, 이 페이지는 FaceTime 에서 달라지는 점과 통화 기록 밖의 흔적을 다룹니다.

통화 내용 자체는 흔적으로 기대하기 어렵습니다. FaceTime 음성·영상 내용은 종단 간 암호화되어 보내는 사람과 받는 사람만 볼 수 있습니다 [2]. 연결은 Apple 푸시 알림 서비스(APNs)로 시작하고, 두 기기가 서로의 신원 인증서를 확인해 세션마다 공유 비밀을 만든 뒤, STUN·ICE 로 되도록 기기끼리 바로(P2P) 잇습니다 [2]. 첫 연결은 Apple 서버가 기기 사이의 패킷을 중계해 이어 줍니다 [2]. 그룹 FaceTime 은 Apple 신원 서비스(IDS) 위에서 키를 정하고 전방 보안(forward secrecy)을 써서, 기기가 뚫려도 지난 통화 내용이 새지 않으며 참여자가 들어오면 새 미디어 키를 만듭니다 [2]. 그래서 조사에서는 "누구와, 언제, 얼마나" 를 보여 주는 메타데이터를 찾는 데 힘을 씁니다. 통화를 녹음했다면 이야기가 달라지는데, 이는 [음성 사서함과 통화 녹음](voicemail-recording.md) 에서 다룹니다.

## 위치와 버전별 차이

통화 한 건의 기록은 통화 기록 DB 에 있고, 그 DB 의 위치와 백업 포함 여부는 [통화 기록](call-history.md) 에 정리되어 있습니다. 로컬 백업에는 FaceTime 전용 SQLite DB 가 없고, 이름에 FaceTime 이 들어간 DB 는 팁 앱 쪽의 `AppDomainGroup-group.com.apple.tipsnext :: com.apple.facetime/.tipkit/tips-store.db` 하나뿐입니다.

로컬 백업에서 FaceTime 과 관련된 도메인은 다음과 같습니다.

| 도메인 | 비고 |
|---|---|
| `AppDomain-com.apple.facetime` | FaceTime 앱. 번들 ID 는 `com.apple.facetime` 으로 읽을 수 있습니다 |
| `AppDomainGroup-group.com.apple.FaceTime` | 앱 그룹 |
| `AppDomain-com.apple.FaceTimeLinkTrampoline` | 이름으로 보아 FaceTime 링크 처리 관련 |
| `AppDomainPlugin-com.apple.DiagnosticExtensions.FaceTime` | 진단 확장 |
| `AppDomainPlugin-com.apple.mobilecal.FacetimeExtension` | 캘린더 확장 |
| `AppDomainPlugin-com.apple.TelephonyUtilities.FaceTimeMessageStoreIntentsExtension` | FaceTime 메시지 저장소 관련 확장 |

FaceTime 링크로 만든 통화의 기록이 어디에 남는지는 공개 자료가 없어 검체에서 확인합니다. 번들 ID 와 도메인 이름의 관계는 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에서 다룹니다.

버전 차이를 FaceTime 만 따로 정리할 자료는 없고, 통화 기록 표의 버전별 칸 변화는 [통화 기록](call-history.md) 을 봅니다.

## 구조

### 통화 기록 안의 FaceTime 행

FaceTime 행을 읽을 때 [통화 기록](call-history.md) 의 칸 설명에 더해 볼 점은 두 가지입니다. 첫째, `ZFACE_TIME_DATA` 칸이 따로 있지만 [1] 무엇이 담기는지 밝힌 공개 자료가 없으니 값이 있으면 원본 바이트를 그대로 보존해 둡니다. 둘째, 그룹 FaceTime 처럼 여럿이 한 통화는 `ZADDRESS` 한 칸으로 드러나지 않아서 참여자 표를 이어 읽어야 하며, 그 방법은 [통화 기록](call-history.md) 의 그룹 통화 설명을 따릅니다 [3]. 상대가 전화번호가 아닌 계정 주소(이메일)로 기록될 수도 있으니 검체의 `ZADDRESS` 값 모양을 직접 봅니다.

### 계정과 설정 파일

`HomeDomain :: Library/Preferences/` 아래에는 다음 키가 있습니다. 값의 뜻을 밝힌 공개 자료는 없습니다.

| 파일 | 보인 키 |
|---|---|
| `com.apple.imservice.ids.FaceTime.plist` | `ActiveAccounts`, `OnlineAccounts`, `Status` |
| `com.apple.facetime.bag.plist` (`RootDomain` 에도 같은 이름) | `CacheCertificate`, `CacheTime`, `CachedBag`, `CachedSignature`, `Date` |
| `com.apple.facetimemessagestored.plist` | `transcriptionEnabled`, `accountMigrationStatus`, `lastFetchedContactHistoryToken`, `spotlightIndexVersion`, `lastReindexCompletionDate`, `lastReindexLocale` 등 |
| `com.apple.TelephonyUtilities.plist` | `FaceTimeNewCallersFilterMode` |
| `com.apple.CallHistorySyncHelper.plist` | `CHFacetimeSearchableStatus` |

`imservice.ids.FaceTime.plist` 는 이름과 키로 보아 FaceTime 이 쓰는 계정 목록이고, `facetime.bag.plist` 는 서버 설정 묶음(bag)의 캐시로 보이며, `facetimemessagestored.plist` 는 FaceTime 메시지 저장소의 설정으로 보입니다. 셋 다 뜻이 밝혀지지 않았으니 "FaceTime 계정이 설정되어 있었다" 같은 결론의 단서로만 쓰고, 계정 자체는 [애플 계정](../system-account/apple-account.md) 에서 확인합니다. 이 밖에 계정 목록에는 `com.apple.account.FaceTime`, 알림 설정 목록에는 `com.apple.facetime`, 설정 제한 목록에는 `deniedICCIDsForiMessageFaceTime` 키가 있습니다.

plist 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 통화 기록의 FaceTime 행은 기록된 시각에 이 기기가 해당 상대와 FaceTime 영상 또는 음성 통화를 시작했거나 받으려 했다는 사실과, 방향·응답 여부·통화 시간을 보여 줍니다 [1]. 계정 설정 파일은 이 기기에 FaceTime 계정이 설정되어 있었다는 정황이 됩니다.

**증명하지 못하는 것.** 통화에서 오간 말과 화면은 종단 간 암호화되어 [2] 기기 흔적으로 되살릴 수 있다고 기대하지 않습니다. 영상 통화 행이 있다고 실제로 카메라가 켜져 있었는지, 누가 화면 앞에 있었는지도 알 수 없습니다. 그룹 통화에서 참여자 표를 잇지 않으면 상대가 한 명인 것처럼 잘못 읽을 수 있습니다 [3].

보고서에는 "이 기기의 통화 기록에 FaceTime 영상 통화로 분류된 행이 있고, 상대 주소는 X, 시작 시각은 T, 통화 시간은 N초로 기록되어 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

FaceTime 행의 시각도 통화 기록의 `ZDATE` 로, Mac 절대 시각(2001-01-01 00:00:00 UTC 부터 초)입니다 [1]. 끝 시각을 계산하는 방식과 주의점은 [통화 기록](call-history.md) 에 있습니다. 설정 파일의 `lastReindexCompletionDate` 같은 날짜 키는 이름대로라면 검색 색인 작업의 시각이라서 통화 시각으로 쓰지 않습니다. 날짜 값 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 을 봅니다.

## 함정과 한계

- **"FaceTime 앱 DB" 를 찾는 헛수고.** 로컬 백업에는 FaceTime 전용 통화 DB 가 없습니다. 통화 기록은 통화 기록 DB 에서 찾습니다.
- **음성 통화 분류 누락.** FaceTime 음성 통화는 영상과 다른 `ZCALLTYPE` 값이라서 [1], 영상 값만 걸러 내면 음성 통화를 놓칩니다.
- **서버 중계와 P2P.** 연결 방식은 보안 설계의 설명이고 [2], 특정 통화가 어느 경로로 이어졌는지 기기 흔적에서 가리는 방법은 알려져 있지 않습니다.
- **통화 기록 수집 범위.** 암호화하지 않은 백업에는 통화 기록 DB 자체가 빠질 수 있습니다. FaceTime 행이 안 보이면 수집 범위부터 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 파일 형식 명세로 만든 예시이고 실제 검체 값이 아닙니다. `ZCALLTYPE` 처럼 작은 정수는 레코드 머리에 형식 번호 1(1바이트 정수)로 적히고 본문에 한 바이트로 들어갑니다.

```
레코드 머리의 이 칸 형식 번호 : 01        (1바이트 정수)
레코드 본문의 이 칸 값        : 08        = 8
                              또는 10     = 16
```

8 은 FaceTime 영상, 16 은 FaceTime 음성으로 읽습니다 [1]. 헥스에서 16 이 `10` 으로 보이는 점을 헷갈리지 않도록 10진수로 바꿔 적어 둡니다.

### 공개 도구로 한 번

통화 기록 DB 사본을 `sqlite3` 로 열어 FaceTime 행만 뽑습니다.

```sql
SELECT Z_PK,
       datetime(ZDATE + 978307200, 'unixepoch') AS start_utc,
       CASE ZCALLTYPE WHEN 8 THEN 'FaceTime video'
                      WHEN 16 THEN 'FaceTime audio' END AS kind,
       ZORIGINATED, ZANSWERED, ZDURATION, ZADDRESS,
       length(ZFACE_TIME_DATA) AS ft_data_len
FROM ZCALLRECORD
WHERE ZCALLTYPE IN (8, 16)
ORDER BY ZDATE;
```

iLEAPP 의 통화 기록 모듈 결과에서 같은 종류의 행 수가 맞는지 확인합니다 [1]. 계정·설정 plist 는 plist 도구로 열어 키 목록이 위 표와 같은지 봅니다.

## 교차 검증

상대 주소의 이름은 [연락처](contacts.md) 에서 찾고, 같은 상대와의 iMessage 대화는 [메시지](messages/index.md) 에서 봅니다. FaceTime 을 연 시각은 [KnowledgeC](../app-usage/knowledgec/index.md) 와 [바이옴](../app-usage/biome/index.md) 의 앱 사용 기록에서, 걸려 온 FaceTime 알림은 [알림 기록](../app-usage/notifications.md) 에서 확인해 통화 기록과 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 함께 올립니다.

## 실습

NIST CFReDS 등에 공개된 iOS 검체로 풀어 봅니다.

1. 통화 기록에서 FaceTime 영상 행과 음성 행은 각각 몇 개입니까?
2. FaceTime 행의 `ZADDRESS` 는 어떤 모양입니까? 전화번호 말고 다른 형식이 있습니까?
3. `ZFACE_TIME_DATA` 에 값이 있는 행이 있다면 첫 몇 바이트로 어떤 형식인지 짐작해 보십시오.
4. 참여자가 여럿인 FaceTime 통화가 있는지 참여자 표를 이어 확인해 보십시오.
5. `com.apple.imservice.ids.FaceTime.plist` 의 계정 키가 [애플 계정](../system-account/apple-account.md) 의 기록과 맞습니까?

## 참고 문헌

1. iLEAPP, `scripts/artifacts/callHistory.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/callHistory.py
2. Apple Platform Security, "FaceTime security" (2022-05-13 갱신) — https://support.apple.com/guide/security/facetime-security-seca331c55cd/web
3. James McGee, The Metadata Perspective, "Hello! Who is on the Line?" (2025-02-05) — https://metadataperspective.com/2025/02/05/hello-who-is-on-the-line/
