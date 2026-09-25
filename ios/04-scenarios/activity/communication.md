---
title: "누구와 연락을 주고받았나"
parent: "시나리오 · 행위 재구성"
nav_order: 1420
---

# 누구와 연락을 주고받았나 (Communication)

특정 상대와 언제, 어떤 수단으로, 몇 번 연락했는지를 아이폰에 남은 기록으로 되짚는 시나리오입니다. 메시지·통화·연락처 DB 하나하나의 구조는 아티팩트 페이지에서 다루고, 이 페이지는 여러 기록을 어떤 순서로 엮어 상대와 시각을 맞추는지에 집중합니다.

## 조사 질문

"사건 전날 두 사람이 연락했나", "이 번호와 처음 연락한 때는 언제인가", "통화를 끊은 뒤 곧바로 메시지를 보냈나" 같은 질문입니다. 답은 상대(번호·이메일·연락처 이름), 수단(SMS·iMessage·전화·FaceTime·다른 회사 메신저), 방향(보냄·받음), 시각 넷으로 나뉩니다. 한 기록으로 넷을 다 채우기는 어려워서 메시지 DB·통화 기록·연락처를 먼저 잇고, 수집 범위가 허락하면 연락 상대 요약 DB (interactionC) 와 바이옴 (Biome) 으로 빈칸을 메웁니다.

## 먼저 확인할 것

**수집 범위**가 결론의 크기를 정합니다. 통화 기록은 암호를 건 로컬 백업에만 들어간다고 Apple 이 밝혔고 [10], 실제로 암호를 걸지 않은 로컬 백업에는 `CallHistory.storedata` 가 없고 HomeDomain 의 `Library/Preferences/com.apple.CallHistorySyncHelper.plist` 만 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). interactionC 는 자료마다 적은 조건이 달라서, MVT 는 암호 건 백업에서 읽는 모듈로 표시하고 [13] 다른 글은 전체 파일 시스템 추출에서만 얻는 기록으로 분류했습니다 [21]. 바이옴은 전체 파일 시스템 추출에서 얻는다고 정리돼 있습니다 [21].

| 기록 | 암호 없는 로컬 백업에서 본 것 (확인 범위: iPhone 13 mini, iOS 27.0) | 자료가 적은 수집 조건 |
|---|---|---|
| 메시지 `sms.db` | HomeDomain `Library/SMS/sms.db` 가 있음 | — |
| 연락처 `AddressBook.sqlitedb` | HomeDomain `Library/AddressBook/AddressBook.sqlitedb` 가 있음 | — |
| 음성 사서함 `voicemail.db` | HomeDomain `Library/Voicemail/voicemail.db` 가 있음 | — |
| 통화 기록 `CallHistory.storedata` | 없음 | 암호 건 백업 [10] |
| interactionC `interactionC.db` | 없음 | 암호 건 백업 [13], 전체 파일 시스템 추출 [21] |
| 바이옴 메시지 스트림 | 관찰 메모가 DB·plist 만 적어서 판단하지 않음 | 전체 파일 시스템 추출 [21] |

**iOS 버전**에 따라 시각을 푸는 법과 읽을 칸이 달라집니다.

| iOS 버전 | 달라지는 점 |
|---|---|
| iOS 10 이하 | `sms.db` 시각 칸은 초 단위 Mac 절대 시각입니다 [5][6] |
| iOS 11 무렵 이후 | `sms.db` 시각 칸이 나노초 단위로 바뀌어 1e9 로 나눠 읽고 [5][6], 같은 칸 안에 9자리(초) 값과 18자리(나노초) 값이 섞여 나옵니다 [7] |
| iOS 15 | 알림 이벤트 폴더 `/private/var/mobile/Library/DuetExpertCenter/streams/userNotificationEvents/` 가 처음 확인됐습니다 [15][16] |
| iOS 16 | 보내기를 취소한 메시지도 바이옴 (AppIntents) 과 알림 기록에 날짜·시각·내용·상대가 남을 수 있다고 시험으로 보고됐습니다 [14] |
| iOS 26 이후 | 통화 기록에 `ZAUTOANSWEREDREASON`, `ZCOMMUNICATIONTRUSTSCORE`, `ZORIGINATINGDEVICENAME`, `ZBLOCKEDBYEXTENSIONNAME` 칸이 생겨 iLEAPP 는 칸이 있을 때만 읽습니다 [8] |
| iOS 27.0 | `sms.db`, `AddressBook.sqlitedb`, `voicemail.db` 의 표·칸 이름을 암호 없는 백업에서 확인했습니다 (확인 범위: iPhone 13 mini, iOS 27.0) |

**시각 기준**은 대부분 Mac 절대 시각 (2001-01-01 00:00:00 UTC 기준) 이라서 978307200 을 더해 Unix 시각으로 바꾸지만, `voicemail.db` 는 `date` 를 Unix 시각으로, `trashed_date` 를 Mac 절대 시각으로 읽어야 합니다 [12]. 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 을, 현지 시각으로 옮길 때는 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md) 을 따릅니다.

**사용자와 계정**도 적어 둡니다. 바이옴에서 `remote` 폴더에 든 기록은 같은 Apple 계정의 다른 기기에서 동기화된 것이라 [19][20], 이 기기에서 연락한 기록과 나눠서 봐야 합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 1 | 메시지 — 기기 `/private/var/mobile/Library/SMS/sms.db` [5] | `handle` 표에 상대 번호·이메일과 그 주소로 쓴 서비스가 들어 있고 [5], `message.is_from_me` 가 0 이면 받음, 1 이면 보냄입니다 [4]. 대화방은 `chat`, `chat_handle_join`, `chat_message_join` 으로 잇습니다 (확인 범위: iPhone 13 mini, iOS 27.0) | [메시지](../../02-artifacts/communications/messages/index.md) |
| 2 | 통화 기록 — 기기 `/private/var/mobile/Library/CallHistoryDB/CallHistory.storedata` 의 `ZCALLRECORD` 표 [8] | `ZDATE`(Mac 절대 시각), `ZDURATION`(초), `ZADDRESS`, `ZORIGINATED`(0 받음, 1 걺), `ZANSWERED`(0 안 받음, 1 받음), `ZCALLTYPE`(0 다른 회사 앱, 1 전화, 8 FaceTime 영상, 16 FaceTime 음성), `ZSERVICE_PROVIDER` [8] | [통화 기록](../../02-artifacts/communications/call-history.md) |
| 3 | 연락처 — 백업 HomeDomain `Library/AddressBook/AddressBook.sqlitedb` 의 `ABPerson`·`ABMultiValue` 표 (확인 범위: iPhone 13 mini, iOS 27.0) | 번호·이메일에 사람 이름을 붙입니다. `ABMultiValue.property` 가 3 이면 전화번호, 4 면 이메일로 iLEAPP 가 라벨을 붙였고, Apple 문서로 확인한 값은 아닙니다 [11] | [연락처](../../02-artifacts/communications/contacts.md) |
| 4 | 음성 사서함 — 백업 HomeDomain `Library/Voicemail/voicemail.db` 의 `voicemail` 표 (확인 범위: iPhone 13 mini, iOS 27.0) | `sender`, `callback_num`, `date`, `duration`, `trashed_date` 칸으로 누가 언제 남겼고 언제 지웠는지를 봅니다 | [음성 사서함과 통화 녹음](../../02-artifacts/communications/voicemail-recording.md) |
| 5 | interactionC — 기기 `private/var/mobile/Library/CoreDuet/People/interactionC.db` [1] | 상호작용 한 건마다의 시작·끝 시각, 번들 ID, 방향, 상대 [1][2] | 아래 "interactionC 읽기" |
| 6 | 바이옴 `Siri.Remembers.MessageHistory` — `/private/var/mobile/Library/Biome/streams/restricted/` [3] | 메시지 시각, 방향(Incoming/Outgoing), 번들 ID, 보낸 사람과 받는 사람, 그룹 이름, 대화 ID, 메시지 GUID, 동기화 출처 [3] | [바이옴](../../02-artifacts/app-usage/biome/index.md) |
| 7 | 알림 이벤트 — `/private/var/mobile/Library/DuetExpertCenter/streams/userNotificationEvents/` [16] | 알림 제목·본문·번들 ID (iOS 15.x 시험) [15] | [알림 기록](../../02-artifacts/app-usage/notifications.md) |
| 8 | 다른 회사 메신저 | 앱마다 자기 DB 를 따로 씁니다 | [카카오톡](../../02-artifacts/messengers/kakaotalk/index.md), [텔레그램](../../02-artifacts/messengers/telegram.md), [왓츠앱](../../02-artifacts/messengers/whatsapp.md) 등 |

메시지 서비스 설정은 `com.apple.imservice.*.plist` 파일이 SMS·RCS·SatelliteSMS·ids.iMessage 로 나뉘어 있고, 별명 캐시 DB 7개가 HomeDomain `Library/MessagesMetaData/NickNameCache/` 아래에 있습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 이 두 곳이 상대를 밝히는 데 얼마나 쓸모 있는지는 이 핸드북에서 확인하지 못했습니다.

### interactionC 읽기

interactionC 는 판단에 필요한 만큼만 여기에 적습니다. 백업 안에서는 HomeDomain 의 `Library/CoreDuet/People/interactionC.db` 자리이고, MVT 가 쓰는 백업 파일 ID `1f5a521220a3ad80ebfdc196978df8e7a2e49dee` 는 `SHA1("HomeDomain-Library/CoreDuet/People/interactionC.db")` 를 계산한 값과 같습니다 [1]. 파일 ID 를 구하는 법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 을 봅니다.

`ZINTERACTIONS` 표가 상호작용 한 건이고, `ZCONTACTS` 가 상대 요약, `ZATTACHMENT` 가 첨부이며, 연결 표 `Z_1INTERACTIONS`·`Z_2INTERACTIONRECIPIENT` 로 서로 이어집니다 [1]. iLEAPP 는 `ZINTERACTIONS` 에서 `ZSTARTDATE`, `ZENDDATE`, `ZBUNDLEID`, `ZDIRECTION`, `ZISRESPONSE`, `ZRECIPIENTCOUNT`, `ZCREATIONDATE`, `ZCONTENTURL`, `ZSENDER`, `ZTARGETBUNDLEID`, `ZUUID` 를 읽고, `ZSENDER` 를 `ZCONTACTS.Z_PK` 와 이어 `ZDISPLAYNAME`·`ZIDENTIFIER` 를 붙입니다 [2]. 모든 날짜 칸은 Mac 절대 시각입니다 [1][2].

```sql
SELECT datetime(i.ZSTARTDATE + 978307200, 'unixepoch')    AS start_utc,
       datetime(i.ZENDDATE + 978307200, 'unixepoch')      AS end_utc,
       datetime(i.ZCREATIONDATE + 978307200, 'unixepoch') AS created_utc,
       i.ZBUNDLEID, i.ZDIRECTION, i.ZRECIPIENTCOUNT,
       c.ZDISPLAYNAME, c.ZIDENTIFIER
FROM ZINTERACTIONS i
LEFT JOIN ZCONTACTS c ON i.ZSENDER = c.Z_PK
ORDER BY i.ZSTARTDATE;
```

칸 구성이 버전마다 달라서 MVT 는 칸을 줄인 쿼리 네 개를 차례로 시도하고, 예전 스키마에는 `ZPHOTOLOCALIDENTIFIER`·`ZGROUPNAME` 이 없다고 적었습니다 [1]. 위 쿼리가 칸 이름 오류로 멈추면 먼저 `PRAGMA table_info(ZINTERACTIONS);` 로 실제 칸을 확인합니다. `ZDIRECTION` 숫자가 들어옴·나감 중 무엇인지, `ZBUNDLEID` 에 어떤 앱이 기록되는지는 이번에 연 자료에 풀이가 없어서, 같은 시각의 `sms.db` 나 통화 기록과 맞춰 본 뒤에만 방향을 적습니다.

## 분석 흐름

1. iOS 버전, 시간대, 수집 방법을 적고 위 수집 범위 표로 손에 있는 기록을 확인합니다. 암호 없는 로컬 백업만 있다면 통화 기록이 빠진다는 점을 보고서 초안에 먼저 적습니다.
2. 조사 대상 상대의 번호·이메일을 모든 표기로 모읍니다. 연락처 DB 의 `ABMultiValue` 에서 이름으로 번호를 찾고 [11], `sms.db` 의 `handle` 표에서는 `id` 와 `uncanonicalized_id` 두 칸을 모두 검색합니다 (칸 이름 확인 범위: iPhone 13 mini, iOS 27.0).
3. `sms.db` 에서 그 상대가 든 대화방과 메시지를 뽑고, 시각 칸은 자릿수를 보고 단위를 가려 풉니다 [5][6][7].

   ```sql
   SELECT m.ROWID, h.id AS address, h.service, m.is_from_me,
          datetime(CASE WHEN m.date > 1000000000000 THEN m.date / 1000000000
                        ELSE m.date END + 978307200, 'unixepoch') AS sent_utc
   FROM message m
   LEFT JOIN handle h ON m.handle_id = h.ROWID
   WHERE h.id LIKE '%조사할 번호 끝자리%'
   ORDER BY sent_utc;
   ```

   `message` 표의 `handle_id`, `date`, `date_read`, `date_delivered`, `is_from_me` 칸과 `handle` 표의 `ROWID` 칸은 관찰한 백업에서 이름을 확인했습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 그룹 대화에서 누가 들어 있었는지는 `chat_handle_join` 으로 봅니다.
4. 통화 기록이 있으면 `ZCALLRECORD` 에서 같은 상대의 `ZADDRESS` 를 찾고, `ZORIGINATED`·`ZANSWERED`·`ZDURATION` 을 함께 읽어 "걸었으나 받지 않음" 과 "통화가 이어짐" 을 나눕니다 [8]. 그룹 통화 참여자는 `ZHANDLE` 과 연결 표 `Z_2REMOTEPARTICIPANTHANDLES` 를 이어야 드러납니다 [9].
5. `ZCALLTYPE` 이 0 이고 `ZSERVICE_PROVIDER` 에 다른 회사 앱 이름이 있는 통화는 메신저 앱 통화라서 [8], 그 앱의 DB 를 열어 같은 시각의 대화가 있는지 봅니다.
6. 전체 파일 시스템 추출이 있으면 interactionC 와 바이옴 `Siri.Remembers.MessageHistory` 에서 같은 상대·시각을 찾아 메시지 DB 에서 지워진 구간이 있는지 봅니다. 바이옴 스트림은 몇 달에 걸친 기록이 보였다고 보고됐지만 [3], 보관 기간을 정한 문서는 없어서 기간 밖의 빈칸을 "연락 없음" 으로 읽지 않습니다. SEGB 파일 읽는 법은 [SEGB 형식](../../01-foundations/data-formats/segb.md) 을 따릅니다.
7. 알림 이벤트에서 메신저 알림 제목·본문을 찾아, 앱 DB 에 없는 수신 기록을 보충합니다 [15].
8. 음성 사서함, FaceTime, 다른 회사 메신저까지 모은 뒤 한 줄로 늘어놓아 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올리고, 처음 연락한 때·마지막 연락한 때·수단별 횟수를 셉니다.
9. 지운 메시지와 대화가 의심되면 [지운 대화와 사진 찾기](deleted-content.md) 로 넘어갑니다.

## 흔한 오판

통화 기록 한 줄을 곧바로 "통화했다" 로 옮기는 실수가 가장 흔합니다. `ZANSWERED` 가 0 이면 받지 않은 통화이고 [8], `ZCALLTYPE` 이 0 이면 일반 전화가 아니라 다른 회사 앱 통화입니다 [8]. 방향(`ZORIGINATED`)과 응답 여부, 통화 길이를 함께 적어야 기록이 말하는 만큼이 됩니다.

기록이 없다는 사실을 "연락하지 않았다" 로 읽는 실수도 조심합니다. 암호 없는 백업에는 통화 기록이 들어가지 않고 [10], 사용자가 메시지를 지웠을 수 있으며, 다른 회사 메신저는 자기 DB 에만 흔적을 남깁니다. FaceTime 과 iMessage 는 내용을 종단 간 암호화로 보호하지만 [17][18], 통화 기록 같은 메타데이터는 기기에 남습니다 [17].

`sms.db` 시각을 한 가지 단위로만 푸는 실수도 있습니다. iOS 11 이후 같은 칸 안에 초 값과 나노초 값이 섞여 나와서 [7], 행마다 자릿수를 보고 단위를 가립니다.

바이옴의 `remote` 폴더 기록을 이 기기의 연락으로 적는 일도 있습니다. 같은 Apple 계정의 다른 기기에서 동기화된 기록이라 [19][20], `Sync Origin` 같은 필드 [3] 와 폴더를 확인한 뒤 이 기기의 기록만 남깁니다.

interactionC 의 `ZCREATIONDATE` 를 연락 시각으로 쓰는 실수도 있습니다. MVT 는 `ZCREATIONDATE` 가 시작 시각과 3600초 넘게 다를 때만 따로 타임라인에 넣을 만큼 두 시각을 구분하고 [1], 연락 시각은 `ZSTARTDATE` 로 잡습니다.

## 보고서 문장 예

> `sms.db` 의 `message` 표에 `handle` 표의 (번호) 와 이어진 메시지가 (건수) 건 있고, 그중 `is_from_me` 가 1 인 보낸 메시지는 (건수) 건입니다. 가장 이른 기록은 (시각, UTC), 가장 늦은 기록은 (시각, UTC) 입니다. 이 기록은 이 기기의 메시지 앱이 해당 주소와 메시지를 주고받은 사실을 보여 주며, 기기를 누가 조작했는지는 보여 주지 않습니다.

> `CallHistory.storedata` 의 `ZCALLRECORD` 표에 (시각, UTC) 에 (번호) 로 건 통화가 있고, `ZANSWERED` 는 0, `ZDURATION` 은 0초입니다. 이 기록은 발신을 시도했으나 상대가 받지 않았음을 보여 줍니다.

## 함께 볼 페이지

- [메시지 (iMessage·SMS)](../../02-artifacts/communications/messages/index.md)
- [통화 기록 (CallHistory)](../../02-artifacts/communications/call-history.md)
- [연락처 (AddressBook)](../../02-artifacts/communications/contacts.md)
- [페이스타임 (FaceTime)](../../02-artifacts/communications/facetime.md)
- [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](user-attribution.md) — 연락한 기록을 사람과 잇기
- [지운 대화와 사진 찾기 (Deleted Content)](deleted-content.md)
- [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. MVT, `src/mvt/ios/modules/mixed/interactionc.py` — https://raw.githubusercontent.com/mvt-project/mvt/main/src/mvt/ios/modules/mixed/interactionc.py
2. iLEAPP, `scripts/artifacts/interactionCcontacts.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/interactionCcontacts.py
3. digital-forensics.it, "84 Streams Later, Part 2: Inside Apple Biome" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html
4. iLEAPP, `scripts/artifacts/sms.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/sms.py
5. Magnet Forensics, "The Meaning of Messages" (2023-03-09) — https://www.magnetforensics.com/blog/the-meaning-of-messages/
6. ChatExport, ChatExportKnowledge README — https://github.com/ChatExport/ChatExportKnowledge
7. Smarter Forensics, "Time is NOT on our side when it comes to messages in iOS 11" (2017-09) — https://smarterforensics.com/2017/09/time-is-not-on-our-side-when-it-comes-to-messages-in-ios-11/
8. iLEAPP, `scripts/artifacts/callHistory.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/callHistory.py
9. James McGee, The Metadata Perspective, "Hello! Who is on the Line?" (2025-02-05) — https://metadataperspective.com/2025/02/05/hello-who-is-on-the-line/
10. Apple 지원, "About encrypted backups on your iPhone, iPad, or iPod touch" — https://support.apple.com/en-us/108353
11. iLEAPP, `scripts/artifacts/addressBook.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/addressBook.py
12. iLEAPP, `scripts/artifacts/voicemail.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/voicemail.py
13. MVT 문서, "Records extracted by mvt-ios" — https://docs.mvt.re/en/latest/ios/records/
14. D20 Forensics, "iOS 16 - "Paul unsent a message." ... OR DID HE?!" (2022-09) — https://blog.d204n6.com/2022/09/ios-16-paul-unsent-message-or-did-he.html
15. 4n6 Ninja, "Peeking at User Notification Events in iOS 15" (2022-05) — https://gforce4n6.blogspot.com/2022/05/peeking-at-user-notification-events-in.html
16. digital-forensics.it, "84 Streams Later: Exploring the Evolution of Apple Biome in iOS" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-exploring-evolution-of.html
17. Apple Platform Security, "FaceTime security" — https://support.apple.com/guide/security/facetime-security-seca331c55cd/web
18. Apple Platform Security, "How iMessage sends and receives messages securely" — https://support.apple.com/guide/security/how-imessage-sends-and-receives-messages-secd9764312f/web
19. iLEAPP, `scripts/artifacts/biomeInfocus.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/biomeInfocus.py
20. Magnet Forensics, "Bringing it Back With Biome Data" — https://www.magnetforensics.com/blog/bringing-it-back-with-biome-data/
21. digital-forensics.it, "Has the user ever used the XYZ application? aka traces of application execution on mobile devices" (2023-12) — https://blog.digital-forensics.it/2023/12/has-user-ever-used-xyz-application-aka.html
