---
title: "메일로"
parent: "자료를 밖으로 보냈나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 1580
---

# 메일로 (Email)

아이폰의 기본 메일 앱으로 자료를 첨부해 보냈는지 가리는 페이지입니다. 메일 DB 가 있을 때 보낸편지함의 메일을 찾는 흐름과, DB 를 얻지 못했을 때 설정 파일로 계정과 보낸편지함의 존재를 확인하는 데까지를 다룹니다. 다른 유출 경로와 전체 흐름은 허브 [자료를 밖으로 보냈나 (Data Exfiltration)](index.md) 에 있습니다.

## 조사 질문

"이 아이폰의 메일 앱에서 어느 계정으로, 언제, 누구에게, 어떤 첨부를 붙여 메일을 보냈는가" 를 묻습니다. 메일 앱은 겉봉 정보와 주소·제목·본문 앞부분을 서로 다른 DB 에 나눠 두기 때문에, 한 통의 메일을 온전히 세우려면 두 DB 와 메일 파일을 함께 봅니다.

## 먼저 확인할 것

iOS 버전을 먼저 확인합니다. 메일 DB 의 표 구조는 iOS 12 와 13 사이에서 달라졌고[1], iOS 15 이후의 표 구조는 이 페이지의 자료로 확인하지 못했습니다. 버전은 [기기 정보 (Device Info·Lockdown)](../../../02-artifacts/system-account/device-info.md), 시간대는 [시간대와 시각 설정 (Time Zone)](../../../02-artifacts/system-account/time-zone.md) 에서 봅니다.

수집 범위도 확인합니다. 메일 앱 데이터는 `/private/var/mobile/Library/Mail` 에 있습니다[1]. 관찰한 로컬 백업에는 `Envelope Index`·`Protected Index`·`.emlx` 파일이 없었고(확인 범위: iOS 27.0), 로컬 백업에 이 DB 가 들어가는지는 확인하지 못했습니다. 로컬 백업만 있다면 아래 "메일 DB 가 없을 때" 절의 설정 파일부터 봅니다. 수집 방법은 [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md) 에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `Envelope Index` | 보낸 날짜, 스레드·메시지 ID, 메일이 든 메일함 | [메일 앱 (Apple Mail)](../../../02-artifacts/mail-cloud/apple-mail.md) |
| 2 | `Protected Index` | 주소와 이름, 제목, 본문 앞 500바이트 | [메일 앱 (Apple Mail)](../../../02-artifacts/mail-cloud/apple-mail.md) |
| 3 | 메일함 폴더의 `.emlx`·`.partial.emlx` | 메일 원문과 첨부 | [메일 앱 (Apple Mail)](../../../02-artifacts/mail-cloud/apple-mail.md) |
| 4 | `.mboxCache.plist` | 메일함 URL 의 DAFolderID 를 폴더 이름으로 풀기 | [속성 목록 파일 (plist·NSKeyedArchiver)](../../../01-foundations/data-formats/plist.md) |
| 5 | 메일 설정 plist·계정 DB | 계정 목록과 보낸편지함의 존재 | [설정 값 (Preferences)](../../../02-artifacts/system-account/preferences.md) |

### 메일 DB 두 개

핵심 DB 는 `Envelope Index` 와 `Protected Index` 이고, 둘 다 `-shm`·`-wal` 파일이 함께 있습니다[1]. `Envelope Index` 는 보낸 날짜, 스레드·메시지 ID, 메일함 위치 같은 겉봉 정보만 담고 보낸 사람·받는 사람은 담지 않습니다[1]. 주소와 제목은 `Protected Index` 에 있고, 버전에 따라 표가 다릅니다[1].

| iOS | 주소·제목 | 본문 앞부분 |
|---|---|---|
| 12 | messages 표(보낸 사람·제목·to/cc/bcc) | message_data 표(본문 앞 500바이트) |
| 13 | Addresses 표(주소와 이름), Subjects 표 | Summaries 표(본문 앞 500바이트) |
| 15 이후 | 확인하지 못함 | 확인하지 못함 |

`-wal` 파일에는 아직 본 DB 에 합쳐지지 않은 기록이 있을 수 있어서, 세 파일을 함께 복사한 뒤 사본에서 엽니다. 방법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) 에 있습니다. 두 DB 의 시각 칸이 UNIX 초인지 Mac 절대 시각인지는 확인하지 못했고, [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md) 의 방법으로 후보 기준을 대 본 뒤 `.emlx` 머리글의 날짜와 맞는 기준을 고릅니다.

### 메일함과 메일 파일

계정 폴더 아래에 받은편지함·보낸편지함·임시보관함 같은 메일함 폴더가 있고, 메일은 `.emlx`·`.partial.emlx` 파일로 저장됩니다[1]. DB 의 메일함 URL 은 DAFolderID 로 폴더를 가리키고, 이 값은 `.mboxCache.plist` 로 풀어냅니다[1]. 보낸 메일을 찾을 때는 DAFolderID 를 풀어 보낸편지함에 해당하는 메일함을 먼저 정하고, 그 메일함에 든 메일만 추립니다. 첨부가 원문에 함께 들어 있는지, `.partial.emlx` 처럼 일부만 받아 둔 파일인지도 파일마다 확인합니다.

### 메일 DB 가 없을 때

관찰한 백업에서 메일과 관련해 볼 수 있었던 파일은 아래와 같습니다. 모두 키 이름만 확인했고 값은 읽지 않았습니다(확인 범위: iOS 27.0).

| 파일 | 키 |
|---|---|
| `HomeDomain :: Library/Mail/MailboxCollections.plist` | buildVersion, lastSelectedItem, collections, version |
| `HomeDomain :: Library/DataAccess/(계정 이름)/.mboxCache.plist` | mboxes, separator, capabilities |
| `AppDomainGroup-group.com.apple.mail :: Library/Preferences/group.com.apple.mail.plist` | UserNotificationMailboxCutoffs, EMUserDefaultMailDatabaseSize, MobileMailVersion 등 |
| `AppDomain-com.apple.mobilemail :: Library/Preferences/com.apple.mobilemail.plist` | MailAccountsOrder, MessageAccountsVersion 등 |
| `HomeDomain :: Library/Preferences/com.apple.email.maild.plist` | kDefaultsKeyLastVerifiedMessageID, com.apple.mobilemail.purge.bodies.purge_markers 등 |
| `HomeDomain :: Library/Preferences/com.apple.icloudmailagent.plist` | com.apple.icloud.mail.lastRetryTimestamp, com.apple.icloud.mail.lastSyncAllTimestamp(실수) |

`group.com.apple.mail.plist` 의 UserNotificationMailboxCutoffs 안에는 아래처럼 IMAP 계정의 보낸편지함과 받은편지함을 가리키는 항목이 있었습니다(확인 범위: iOS 27.0).

```text
imap://<UUID>/...Sent
imap://<UUID>/INBOX
```

이 항목으로 기기에 IMAP 계정이 있고 그 계정에 보낸편지함이 있다는 데까지는 말할 수 있지만, 메일을 보냈다는 근거로는 쓰지 않습니다. 메일 계정 목록은 `HomeDomain :: Library/Accounts/Accounts#.sqlite` 의 ZACCOUNTTYPE 표 등에서도 볼 수 있고(확인 범위: iOS 27.0), 계정 종류별 식별자 값은 확인하지 못했습니다.

Gmail·Outlook 같은 다른 회사 메일 앱의 저장 구조는 이 페이지의 자료로 확인하지 못했습니다. Gmail 앱은 [지메일 (Gmail)](../../../02-artifacts/mail-cloud/gmail.md) 을 따릅니다.

## 분석 흐름

1. iOS 버전·시간대·수집 범위를 적고, 메일 DB 와 `-shm`·`-wal` 파일, 메일함 폴더를 함께 사본으로 옮깁니다.
2. `.mboxCache.plist` 로 DAFolderID 를 풀어 계정마다 보낸편지함에 해당하는 메일함을 정합니다.
3. `Envelope Index` 에서 그 메일함에 든 메일의 보낸 날짜와 메시지 ID 를 조사 기간으로 추립니다.
4. `Protected Index` 에서 같은 메일의 받는 사람·제목·본문 앞부분을 찾습니다. 표 이름은 iOS 버전 표를 따릅니다.
5. 해당 메일의 `.emlx` 파일을 열어 머리글의 날짜·받는 사람과 첨부 파일 이름을 확인하고, DB 에서 읽은 값과 맞춰 봅니다.
6. 메일 DB 를 얻지 못했으면 설정 plist 와 계정 DB 로 계정과 메일함의 존재까지만 적고, 서버 쪽 기록은 [클라우드 데이터 (iCloud·계정 데이터 요청)](../../../03-techniques/acquisition/cloud-data.md) 절차로 요청합니다.
7. 찾은 시각을 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) 에 올립니다.

## 흔한 오판

`Envelope Index` 만 보고 받는 사람을 적으려 하면 칸이 없어서 찾지 못합니다[1]. 주소는 `Protected Index` 에서 읽습니다.

iOS 12·13 의 표 이름을 그대로 iOS 15 이후 기기에 적용하면 표가 없다고 잘못 판단할 수 있습니다. 표 목록부터 뽑아 확인합니다.

보낸편지함에 메일이 있다는 기록은 이 기기의 메일 앱이 그 메일을 보낸편지함에 두었다는 뜻입니다. 같은 계정을 쓰는 다른 기기에서 보낸 메일도 IMAP 계정의 보낸편지함에 모일 수 있는지는 이 페이지의 자료로 확인하지 못했으니, 보낸 기기를 단정하지 않습니다.

`.partial.emlx` 는 이름대로 일부만 있는 파일일 수 있어서, 첨부가 파일에 없다는 사실만으로 첨부 없이 보냈다고 쓰지 않습니다.

## 보고서 문장 예

> `Envelope Index` 에서 보낸편지함(DAFolderID ○○, `.mboxCache.plist` 로 확인)에 든 메일 가운데 메시지 ID 가 ○○인 행이 있고, `Protected Index` 에서 같은 메일의 받는 사람은 ○○, 제목은 ○○입니다. 같은 메일의 `.emlx` 파일에 이름이 ○○인 첨부가 들어 있습니다.

> 로컬 백업의 `group.com.apple.mail.plist` 에 IMAP 계정의 보낸편지함을 가리키는 항목이 있습니다. 이 백업에는 메일 DB 가 없어서, 메일을 보낸 기록은 이 자료로 확인할 수 없습니다.

## 함께 볼 페이지

- [메일 앱 (Apple Mail)](../../../02-artifacts/mail-cloud/apple-mail.md)
- [메신저로 (Messenger)](messenger.md), [클라우드로 (Cloud)](cloud.md), [에어드롭으로 (AirDrop)](airdrop.md), [PC 동기화로 (PC Sync)](pc-sync.md)
- [누구와 연락을 주고받았나 (Communication)](../../activity/communication.md)
- [문서 메타데이터 (PDF·Office·iWork)](../../../02-artifacts/embedded-metadata/documents.md)

## 참고 문헌

1. DoubleBlak (Ian Whiffin), "iOS Mail" — https://www.doubleblak.com/blogPost.php?k=iosmail
