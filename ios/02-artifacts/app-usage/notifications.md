---
title: "알림 기록"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 430
---

# 알림 기록 (Notifications)

## 한 줄 요약

알림 기록은 앱이 띄운 알림의 제목·본문·번들 ID·시각을 담은 파일이고, iOS 12 에서는 앱별 폴더의 `DeliveredNotifications.plist`, iOS 15 에서는 `userNotificationEvents` 스트림에서 "이 시각에 이 앱에서 이런 문구의 알림이 왔다" 를 읽을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

알림 기록은 앱을 열어 보지 않고도 알림 문구와 받은 시각을 보여 주는 흔적입니다. iOS 12 조사에서는 `DeliveredNotifications.plist` 에 알림이 만들어진 시각(`AppNotificationCreationDate`), 알림 문구, 전달 시각과 함께 방해 금지 무시·소리·CarPlay 표시 같은 설정 값이 있었고, 같은 폴더의 `AttachmentList.plist` 에 첨부 목록이 `file://` 경로로, `Attachments` 폴더에 첨부 파일 자체가 있었습니다[1].

iOS 15 조사에서는 알림 이벤트 파일에 GUID, 제목, 부제목, 본문, 번들 ID(주·보조), 선택적 문맥 칸, Apple ID 연락처 정보, 시각 4개가 있었습니다[2]. 두 조사 모두 알림의 본문 문구가 기록에 들어 있었다고 적어서[1][2], 앱 안 DB 를 얻지 못한 경우에도 알림 기록에서 문구를 찾아볼 수 있습니다.

## 위치와 버전별 차이

### 버전별 위치

| iOS | 위치 | 출처 |
|---|---|---|
| 12 | 앱 번들 ID 별 하위 폴더 안의 `DeliveredNotifications.plist`, `AttachmentList.plist`, `Attachments/` | [1] |
| 15 | `DuetExpertCenter/streams/userNotificationEvents/local` 의 이벤트 파일 | [2] |
| 16 이후 | 한 연구자의 버전별 정리에서 `DuetExpertCenter/streams/` 아래에 `userNotificationEvents` 가 계속 있고, 17~26 은 위치가 같고 형식만 SEGB v2 | [3] |
| 27.0 로컬 백업 | 아래 "로컬 백업에 보이는 것" 참고 | 관찰 |

```
/private/var/mobile/Library/UserNotifications/<번들 ID>/DeliveredNotifications.plist   (iOS 12)
/private/var/mobile/Library/UserNotifications/<번들 ID>/AttachmentList.plist         (iOS 12)
/private/var/mobile/Library/DuetExpertCenter/streams/userNotificationEvents/local    (iOS 15)
```

iOS 15 이벤트 파일을 조사한 저자는 이 파일을 iOS 15.x 에서만 보았고 시험 자료가 적었다고 밝혔습니다[2]. 이 스트림이 로컬 백업에 들어가는지와 며칠 치를 남기는지는 확인한 자료가 없습니다. 바이옴 (Biome) 스트림 폴더 전반은 [바이옴](biome/index.md) 에서 다룹니다.

### 로컬 백업에 보이는 것

관찰한 로컬 백업에는 `HomeDomain :: Library/UserNotifications/` 아래 `Library.plist` 가 있었고, 하위 폴더마다 다음 plist 들이 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0).

```
HomeDomain :: Library/UserNotifications/Library.plist
HomeDomain :: Library/UserNotifications/<UUID>/Categories.plist
HomeDomain :: Library/UserNotifications/<UUID>/PushRegistration.plist
HomeDomain :: Library/UserNotifications/<UUID>/PendingNotifications.plist
HomeDomain :: Library/UserNotifications/<UUID>/Schedule.plist
HomeDomain :: Library/UserNotifications/<UUID>/Topics.plist
```

iOS 12 에서는 하위 폴더 이름이 번들 ID 였지만[1], 이 백업에서는 하위 폴더 이름이 UUID 꼴이라 관찰 메모에서 가려졌고, 이 plist 들의 키 이름도 가려져 있습니다 (확인 범위: iPhone 13 mini, iOS 27.0). `DeliveredNotifications.plist` 와 `AttachmentList.plist` 는 관찰 메모에 나오지 않아서, 백업에서 빠지는 것인지 기기에 없는 것인지는 판단할 수 없습니다.

알림과 이름이 닿는 설정 파일도 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0).

| 도메인 :: 경로 | 관찰한 키 |
|---|---|
| `HomeDomain :: Library/BulletinBoard/VersionedSectionInfo.plist` | `sectionInfo` 아래에 번들 ID 가 키로 들어 있음(`com.apple.MobileSMS`, `com.apple.ScreenTimeNotifications`, `com.apple.findmy` 등과 다른 회사 앱), `sectionInfoVersionNumber` (int) |
| `HomeDomain :: Library/BulletinBoard/ClearedSections.plist` | 키 없음(빈 plist) |
| `HomeDomain :: Library/Preferences/com.apple.usernotifications.plist` | `BundleLibrarianVacuumInitialComplete` (bool) |

`VersionedSectionInfo.plist` 가 앱별 알림 설정을 담는지는 확인하지 못했지만, 번들 ID 가 키로 들어 있어서 알림과 관련된 앱 목록을 모을 때 후보로 씁니다. 이 밖에 `AppDomainPlugin-com.apple.UserNotificationsServer.UserNotificationsThumbnailProvider`, `com.apple.MobileSMS.MessagesNotificationExtension` 처럼 알림 확장 도메인도 많았습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 백업 구조는 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.

## 구조

**iOS 12 의 plist.** `DeliveredNotifications.plist` 는 NSKeyedArchiver 형식 plist 입니다[1]. 이 형식은 객체를 번호로 서로 가리키게 풀어 둔 plist 라서, 키 하나를 찾으려면 번호를 따라가야 합니다. 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

**iOS 15 의 이벤트 파일.** 파일 헤더에 `SEGB` 서명(`0x53 45 47 42`)이 있습니다[2]. iOS 15 는 SEGB v1 을 쓰던 때라서, 서명은 파일 맨 앞이 아니라 56바이트 헤더의 끝 부분에 있습니다([SEGB 형식](../../01-foundations/data-formats/segb.md)). 기록 하나에 제목·본문·번들 ID·시각이 함께 들어 있고[2], 파일 헤더와 기록 헤더의 모양, v1 과 v2 차이는 [SEGB 형식](../../01-foundations/data-formats/segb.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 기록이 남아 있으면, 어떤 번들 ID 의 앱이 이런 제목과 본문의 알림을 이 시각에 만들거나 전달했다는 사실을 보여 줍니다[1][2]. iOS 12 에서는 첨부 목록과 첨부 파일까지 남아서[1] 알림으로 받은 사진 같은 파일이 기기에 있었다는 근거도 됩니다. 앱을 지운 뒤에도 알림 기록은 6일 넘게 남았다는 보고가 있어서[4], 지금 설치되어 있지 않은 앱이 그 기간에 있었다는 흔적으로 쓸 수 있습니다.

**증명하지 못하는 것.** 알림이 기기에 왔다는 사실은 사용자가 그 알림을 보거나 읽었다는 뜻이 아니고, 알림을 눌러 앱을 열었다는 뜻도 아닙니다. 알림 문구가 원래 메시지 전체와 같은지는 확인한 자료가 없어서, 앱 DB 의 본문과 따로 맞춰 봅니다. 기록이 없다고 알림이 오지 않았다고 말할 수도 없는데, 알림을 지웠을 때 기록이 사라지는지는 참고한 글이 다루지 않았습니다[1].

보고서에는 "이 메시지를 읽었다" 대신 "번들 ID `com.example.app` 의 알림 기록에 이 시각, 이 제목과 본문이 있다" 처럼 씁니다.

## 시각 해석

iOS 15 이벤트 파일 안의 시각은 Apple 절대 시각(Cocoa 시각, 2001-01-01 00:00:00 UTC 부터 센 초)을 8바이트 리틀 엔디언으로 저장합니다[2]. 파일 이름도 변형된 Cocoa 시각이라, 1,000,000 으로 나눈 값을 Cocoa 시각으로 바꿉니다[2]. 기록 하나에 시각이 4개 있지만[2] 각 시각이 무엇을 뜻하는지는 원문으로 가르지 못했으니, 보고서에는 몇 번째 시각인지 밝혀 적습니다.

아래는 명세로 만든 예시이고 특정 검체의 파일 이름이 아닙니다.

```
파일 이름         700000000000000
÷ 1,000,000     700000000 (Cocoa 초)
+ 2001-01-01    2023-03-08 20:26:40 UTC
```

iOS 12 plist 의 `AppNotificationCreationDate` 는 알림이 만들어진 시각이고 전달 시각은 따로 있습니다[1]. 두 값이 다를 때 그 차이가 무엇을 뜻하는지는 원문이 설명하지 않아서, 두 시각을 모두 적어 둡니다. 시각 기준 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

## 함정과 한계

**버전마다 파일이 다릅니다.** iOS 12 의 plist 와 iOS 15 의 이벤트 파일은 형식과 위치가 모두 다르고[1][2], iOS 15 이벤트 파일은 한 저자가 적은 시험 자료로 본 결과입니다[2]. iOS 27.0 백업에서는 두 파일 이름이 모두 관찰 메모에 나오지 않았습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 검체의 iOS 버전을 먼저 확인하고, 그 버전에 어느 파일이 있는지부터 찾습니다.

**이름만 보고 해석하지 않습니다.** `ClearedSections.plist` 는 이름에 "지움" 이 들어가지만 관찰한 백업에서는 빈 plist 였고 (확인 범위: iPhone 13 mini, iOS 27.0), 무엇을 기록하는 파일인지 확인하지 못했습니다. 이 파일이 비어 있다고 알림을 지운 적이 없다고 쓰지 않습니다.

**App Store 서비스의 푸시 표와 헷갈리지 않습니다.** `itunesstored_private.sqlitedb` 에도 `ZPUSHNOTIFICATION`(`ZCLIENT`, `ZUSERINFO`)·`ZPUSHNOTIFICATIONCLIENT` 표가 있지만 (확인 범위: iPhone 13 mini, iOS 27.0), 이름만으로는 앱 알림 기록과 같은 것인지 알 수 없습니다. 이 DB 는 [앱 스토어 기록](app-store.md) 에서 다룹니다.

**지우기와 조작.** 앱을 지워도 알림 기록은 한동안 남는다는 보고가 있지만[4], 보관 기간이 지나면 사라질 수 있습니다. 앱 삭제와 기록 공백을 함께 볼 때는 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름을 따릅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시이고 특정 검체에서 나온 값이 아닙니다. iOS 15 이벤트 파일은 헤더에 SEGB 서명 4바이트가 있고[2], v1 이라 파일 맨 앞이 아니라 헤더 끝 부분에서 찾습니다.

```
53 45 47 42                                         SEGB
```

이 서명이 파일 맨 앞에 있는지, 헤더 뒤쪽에 있는지에 따라 SEGB 버전이 갈리고, 그 판단법은 [SEGB 형식](../../01-foundations/data-formats/segb.md) 에 있습니다. 서명을 찾았으면 기록마다 8바이트 시각 값을 리틀 엔디언으로 읽고, 위 방법대로 Cocoa 시각으로 바꿉니다[2].

iOS 12 의 `DeliveredNotifications.plist` 는 NSKeyedArchiver plist 라서[1], 이진 plist 라면 첫 8바이트가 `bplist00` 이고 안에서 `$archiver`, `$objects` 같은 키를 찾을 수 있습니다.

### 공개 도구로 한 번

SEGB 파일은 SEGB 형식 페이지에 적힌 공개 파서로 기록을 나눈 뒤, 기록 본문에서 제목·본문·번들 ID 문자열을 확인합니다. plist 는 Python 표준 라이브러리 `plistlib` 로 연 다음 `$objects` 배열에서 번호를 따라가 `AppNotificationCreationDate` 와 문구를 찾습니다. 어느 방법이든 도구 결과 몇 건을 헥스와 맞춰 보고 씁니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

## 교차 검증

알림이 온 시각에 메시지 앱에 해당 메시지가 있는지 [메시지](../communications/messages/index.md) 와 [카카오톡](../messengers/kakaotalk/index.md) 같은 앱 DB 에서 확인하고, 그 앱이 설치되어 있었는지는 [설치된 앱](installed-apps.md) 에서 봅니다. 알림 수 합계는 [화면 사용 시간](screen-time.md), 알림 뒤 앱을 열었는지는 [KnowledgeC](knowledgec/index.md) 와 [바이옴](biome/index.md) 에서 확인합니다. 조사 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md), [스미싱 흔적](../../04-scenarios/incident/smishing.md), [지운 대화와 사진 찾기](../../04-scenarios/activity/deleted-content.md) 를 봅니다.

## 실습

공개 검체(NIST CFReDS 등의 iOS 이미지)로 다음 질문을 풀어 봅니다.

1. 검체의 iOS 버전에서 알림 기록은 `UserNotifications` 폴더와 `DuetExpertCenter/streams/userNotificationEvents` 가운데 어디에 있습니까?
2. iOS 15 이벤트 파일이 있다면 파일 이름을 1,000,000 으로 나눠 Cocoa 시각으로 바꾼 값이 파일 안 기록의 시각과 가깝습니까?
3. 알림 기록에 나오는 번들 ID 가운데 수집 시점에 설치되어 있지 않은 앱이 있습니까?
4. 메시지 앱 알림의 본문과 메시지 DB 의 같은 시각 메시지 본문이 같습니까, 알림 쪽이 잘려 있습니까?
5. iOS 12 검체라면 `AttachmentList.plist` 의 `file://` 경로에 실제 파일이 남아 있습니까?

## 참고 문헌

- [1] iOS 12 - Delivered Notifications and a new way to parse them — D20 Forensics (2019-08) — https://blog.d204n6.com/2019/08/ios-12-delivered-notifications-and-new.html
- [2] Peeking at User Notification Events in iOS 15 — 4n6 Ninja (2022-05) — https://gforce4n6.blogspot.com/2022/05/peeking-at-user-notification-events-in.html
- [3] 84 Streams Later: Exploring the Evolution of Apple Biome in iOS — digital-forensics.it (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-exploring-evolution-of.html
- [4] Has the user ever used the XYZ application? aka traces of application execution on mobile devices — digital-forensics.it (2023-12) — https://blog.digital-forensics.it/2023/12/has-user-ever-used-xyz-application-aka.html
