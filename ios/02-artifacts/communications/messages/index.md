---
title: "메시지"
parent: "아티팩트 · 통화·메시지·연락처"
nav_order: 460
has_children: true
has_toc: false
---

# 메시지 (iMessage·SMS)

아이폰 기본 메시지 앱은 iMessage·SMS 대화를 sms.db 한 파일에 모으고 첨부 파일은 따로 폴더에 두며, iOS 16 부터는 지운 메시지를 한동안 보관하고 보낸 메시지를 취소·편집한 흔적까지 남깁니다.

## 왜 중요한가

누구와 언제 연락을 주고받았는지 묻는 조사에서 가장 먼저 여는 곳이 메시지 앱이고, 대화 본문과 상대 주소, 보낸·읽은 시각, 주고받은 사진을 한곳에서 볼 수 있습니다. iOS 16 부터 최근 삭제된 항목 복구와 보낸 메시지 취소·편집이 생겨서[1][2][3], 지운 대화나 고친 대화를 찾을 때도 이 앱의 기록부터 봅니다. 다만 표 구조가 버전마다 바뀌고 본문이 여러 열에 나뉘어 있어서, 도구 결과를 그대로 옮기기보다 표를 직접 열어 확인하는 편이 안전합니다.

## 한눈에 보기

| 무엇 | 위치 | iOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 대화 DB | 기기 `/private/var/mobile/Library/SMS/sms.db`[1], 백업 HomeDomain `Library/SMS/sms.db` | 전 버전(날짜 단위는 대략 iOS 11 부터 나노초) | 본문, 보낸 방향, 상대 주소, 서비스, 대화방, 보낸·읽은·전달된 시각 |
| 첨부 파일 | 기기 `/private/var/mobile/Library/SMS/Attachments`[1], 백업 MediaDomain[4] | 전 버전 | 주고받은 사진·영상·파일과 그 이름·형식·크기 |
| 삭제·취소·편집 흔적 | sms.db 안의 복구용 표와 `message` 표의 열 | iOS 16 이후 | 최근 삭제된 항목, 취소·편집한 메시지 |
| 메시지 설정 | 백업 HomeDomain `Library/Preferences/com.apple.MobileSMS.plist` 등 | — | 보관·첨부·필터와 이어진 이름의 설정 키 |
| 서비스 계정 | 백업 HomeDomain `Library/Preferences/` 의 `com.apple.imservice.SMS.plist`, `com.apple.imservice.RCS.plist`, `com.apple.imservice.SatelliteSMS.plist`, `com.apple.imservice.ids.iMessage.plist` | — | SMS·RCS·SatelliteSMS 에는 `Accounts`, `OnlineAccounts`, `ActiveAccounts`, `Status` 키가 있고 ids.iMessage 에는 `Accounts` 를 뺀 세 키가 있습니다. 값의 뜻은 공개된 설명이 없습니다 |
| 별명 캐시 | 백업 HomeDomain `Library/MessagesMetaData/NickNameCache/` 아래 `nickNameKeyStore.db`, `nicknameRecordsStore.db`, `handleSharingPreferences.db`, `unknownSenderRecordInfoStore.db` 등 7개 | — | 모두 `kvtable`(`ROWID`, `key`, `value`, `value_type`, `date`) 구조입니다. 각 DB 의 용도는 공개된 설명이 없습니다 |

메시지 앱의 번들 ID 는 `com.apple.MobileSMS` 이고, 백업에는 `AppDomain-com.apple.MobileSMS` 도메인도 있습니다. 번들 ID 와 백업 도메인의 관계는 [번들 ID와 앱 그룹 (Bundle ID·App Group)](../../../01-foundations/value-decoding/bundle-id-app-group.md)에서 다룹니다.

> 그림 자리: 기기 경로와 백업 도메인(HomeDomain·MediaDomain)에 sms.db 와 첨부 폴더가 어떻게 나뉘어 들어가는지

## 읽는 순서

1. [대화 DB 구조 (sms.db)](sms-db.md) — `message`·`handle`·`chat` 을 이어 붙여 대화를 읽는 법과 날짜 열을 바꾸는 법, WAL 을 빼면 생기는 누락을 다룹니다.
2. [첨부 파일 (Attachments)](attachments.md) — `attachment` 표와 첨부 폴더 경로, 백업에서 MediaDomain 으로 첨부 파일을 찾는 법을 다룹니다.
3. [지운 메시지의 흔적 (Deleted Messages)](deleted-messages.md) — 최근 삭제된 항목과 취소·편집한 메시지가 sms.db 와 바이옴·알림 기록에 남기는 흔적을 다룹니다.

## 함께 볼 페이지

상대가 누구인지는 [연락처 (AddressBook)](../contacts.md)에서, 같은 상대와의 통화는 [통화 기록 (CallHistory)](../call-history.md)과 [페이스타임 (FaceTime)](../facetime.md)에서 찾습니다. 다른 메신저 앱은 [카카오톡 (KakaoTalk)](../../messengers/kakaotalk/index.md)부터 메신저 분류에서 다룹니다.

DB 와 값을 읽는 바탕은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md), [속성 목록 파일 (plist·NSKeyedArchiver)](../../../01-foundations/data-formats/plist.md), [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md), [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md)에 있습니다.

조사 흐름은 [누구와 연락을 주고받았나 (Communication)](../../../04-scenarios/activity/communication.md), [지운 대화와 사진 찾기 (Deleted Content)](../../../04-scenarios/activity/deleted-content.md), [스미싱 흔적 (Smishing)](../../../04-scenarios/incident/smishing.md)에서 이어집니다.

## 참고 문헌

1. Magnet Forensics, "The Meaning of Messages" (2023-03-09) — https://www.magnetforensics.com/blog/the-meaning-of-messages/
2. Apple 지원, "Recover deleted text messages on your iPhone or iPad" — https://support.apple.com/en-us/102615
3. Apple 지원, "How to unsend messages on your iPhone" — https://support.apple.com/en-us/105085
4. ChatExport, ChatExportKnowledge `attachments.md` — https://raw.githubusercontent.com/ChatExport/ChatExportKnowledge/main/attachments.md
