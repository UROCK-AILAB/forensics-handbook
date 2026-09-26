---
title: "삼성 이메일"
parent: "아티팩트 · 메일·클라우드"
nav_order: 1090
---

# 삼성 이메일 (Samsung Email)

## 한 줄 요약

삼성 이메일 (Samsung Email) 은 갤럭시 기기에서 쓰는 메일 앱입니다. 패키지 이름·DB 경로·표 이름을 적은 공개 분석 자료가 없어서, 이 페이지는 검체에서 확인할 순서와 비교 기준이 되는 AOSP 이메일 앱의 저장 구조를 정리합니다.

## 무엇을 기록하나 · 왜 생기나

메일 앱은 서버의 메일을 기기에 받아 두고 보여 주기 때문에 계정 설정, 폴더, 메일 머리, 본문, 첨부가 앱 데이터 폴더에 쌓이는 것이 보통입니다. 삼성 이메일도 그런 기록을 남길 것으로 짐작할 수 있지만, 무엇을 어디에 남기는지 적은 공개 포렌식 자료는 없습니다.

공개 도구 ALEAPP 에도 삼성 이메일 전용 모듈은 없습니다 [1]. 메일 관련 모듈은 아래와 같습니다 [1].

```
gmail.py  gmailEmails.py  gmailIMAPEmails.py  outlook.py  FCMQueuedMessageOutlook.py
protonmail.py  protonmailDbMail.py  protonmailInbox.py  yahooMail.py
K9Mail.py  FairEmail.py  thunderbird.py
```

삼성 이메일이 AOSP 이메일 앱을 바탕으로 만들어졌는지, DB 이름이 `EmailProvider.db` 인지는 알려져 있지 않습니다. 그래서 아래 "구조" 절의 AOSP 내용은 앱을 직접 조사할 때 맞춰 볼 기준으로만 쓰고, 삼성 앱에 그대로 있다고 보고서에 쓰면 안 됩니다.

## 위치와 버전별 차이

패키지 이름이 공개되어 있지 않아서, 검체에서 [설치된 앱 (packages.xml)](../app-usage/packages/index.md) 기록으로 패키지 이름부터 확정하고, 그 이름으로 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 페이지에서 설명하는 앱 데이터 폴더를 찾습니다. 패키지 이름과 UID 를 맞춰 보는 법은 [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md) 페이지에 있습니다.

One UI 버전이나 앱 버전에 따른 차이도 공개 자료가 없습니다.

## 구조

### 비교 기준: AOSP 이메일 앱

아래는 AOSP 이메일 앱(`com.android.email` 계열)의 `EmailContent.java` 에 정의된 저장 구조입니다 [2]. 이 소스는 master 브랜치 기준이고 저작권 표기 연도는 2009 입니다 [2].

콘텐츠 제공자 (Content Provider) 의 authority 는 앱 패키지 이름 뒤에 `.provider` 를 붙여 만들고, 패키지 이름은 리소스 `email_package_name` 에서 읽습니다 [2]. 표와 주요 칸은 아래와 같습니다 [2].

| 표 | 주요 칸 | 담긴 것 |
|---|---|---|
| `Message` | `displayName`, `timeStamp`, `subject`, `flagRead`, `flagLoaded`, `flagFavorite`, `flagAttachment`, `flags`, `messageId`, `mailboxKey`, `accountKey`, `fromList`, `toList`, `ccList`, `bccList`, `replyToList`, `snippet`, `threadTopic`, `flagSeen`, `syncServerId`, `syncServerTimeStamp` 등 | 메일 한 통 |
| `Message_Updates`, `Message_Deletes` | 검체에서 확인 | 갱신·삭제된 메시지용 |
| `Body` | `messageKey`, `htmlContent`, `textContent`, `htmlContentUri`, `textContentUri`, `htmlReply`, `textReply`, `sourceMessageKey`, `introText`, `quotedTextStartPos` | 본문 |
| `Attachment` | `fileName`, `mimeType`, `size`, `contentId`, `contentUri`, `cachedFile`, `messageKey`, `location`, `encoding`, `content`, `flags`, `content_bytes`, `accountKey`, `uiState`, `uiDestination`, `uiDownloadedSize` | 첨부 |
| `Account` | `displayName`, `emailAddress`, `syncKey`, `syncLookback`, `syncInterval`, `hostAuthKeyRecv`, `hostAuthKeySend`, `flags`, `isDefault`, `senderName`, `protocolVersion`, `signature`, `maxAttachmentSize` 등 | 메일 계정 |
| `Mailbox` | `displayName`, `serverId`, `parentServerId`, `parentKey`, `accountKey`, `type`, `syncTime`, `unreadCount`, `messageCount`, `lastTouchedTime`, `totalCount`, `hierarchicalName`, `lastFullSyncTime` 등 | 폴더 |
| `HostAuth` | `protocol`, `address`, `port`, `flags`, `login`, `password`, `domain`, `certAlias`, `accountKey`, `serverCert`, `credentialKey` | 메일 서버 접속 정보 |
| `Policy` | `passwordMode`, `passwordMinLength`, `passwordExpirationDays`, `passwordHistory`, `passwordComplexChars`, `passwordMaxFails`, `maxScreenLockTime` 등 | Exchange 보안 정책 |

`Message_Updates`·`Message_Deletes` 가 `Message` 와 같은 칸으로 되어 있는지, 서버에 반영되기 전의 원래 행이 이 표에 남는지는 검체 DB 에서 확인합니다.

몇몇 칸의 값 뜻은 아래와 같습니다 [2]. `flagRead` 는 0 이 안 읽음, 1 이 읽음이고, `messageId` 는 메일 머리의 Message-ID, `clientId` 는 쓰지 않던 칸을 다시 써서 임시 보관 메일(초안) 정보를 담습니다. `flagLoaded` 는 값 이름으로 보아 메일을 받아 둔 상태를 나타냅니다.

| `flagLoaded` 값 | 이름 |
|---|---|
| 0 | UNLOADED |
| 1 | COMPLETE |
| 2 | PARTIAL |
| 3 | DELETED |
| 4 | UNKNOWN |

`Attachment.size` 는 바이트 단위이고, `location` 은 IMAP 에서는 파트 번호, Exchange ActiveSync (EAS) 에서는 내부 파일 이름입니다 [2]. `HostAuth.password` 는 메일 서버 비밀번호가 들어 있을 수 있는 칸이라서 보고서와 사본을 다룰 때 따로 가려서 취급합니다.

지메일 앱이 IMAP 계정을 담는 `EmailProvider` DB 도 `Message`·`Account`·`Mailbox`·`Attachment`·`HostAuth` 표와 같은 칸 이름을 씁니다 [3]. 그 내용은 [지메일 (Gmail)](gmail.md) 페이지에서 다룹니다.

## 증거로서 의미

아래는 검체의 삼성 이메일 DB 가 위 AOSP 구조와 같다고 직접 확인한 뒤에야 쓸 수 있는 해석입니다.

**증명하는 것**

`Account` 행은 그 주소의 메일 계정을 이 앱에 설정한 적이 있다는 기록이고, `Message` 행은 그 메일이 기기에 받아져 있었다는 뜻입니다. `flagRead` 가 1 이면 앱 안에서 읽음으로 표시된 상태였고, `Mailbox.lastTouchedTime` 은 그 폴더의 메일을 마지막으로 읽은 시각입니다 [2]. `Policy` 행이 있으면 Exchange 서버가 보낸 보안 정책을 받은 적이 있다는 정황이 됩니다.

**증명하지 못하는 것**

`flagRead` 는 서버와 동기화되는 표시일 수 있어서, 1 이라도 이 기기에서 사용자가 열어 보았다고 단정할 수 없습니다. `flagLoaded` 가 PARTIAL 이면 본문 일부만 받은 상태라서 `Body` 가 비어 있어도 메일 내용이 없었다는 뜻이 아닙니다. 삼성 앱이 AOSP 와 다른 구조라면 이 절의 해석은 모두 다시 따져야 합니다.

## 시각 해석

AOSP 이메일 앱에서 `Message.timeStamp` 는 목록에 보이는 시각, `Mailbox.syncTime` 은 마지막 동기화를 마친 시각, `Mailbox.lastTouchedTime` 은 마지막으로 메일을 읽은 시각이고, 모두 밀리초 단위입니다 [2]. Java 에서 흔히 쓰는 유닉스 밀리초로 보이지만, 삼성 앱에서 같은지는 검체 값으로 확인합니다. `timeStamp` 는 메일 머리의 Date 값인지 기기가 받은 시각인지 주석만으로는 가를 수 없습니다. 값을 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md), 현지 시각으로 옮길 때 확인할 것은 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 페이지에 있습니다.

## 함정과 한계

첫째, 삼성 이메일 자체의 저장 구조를 적은 공개 자료는 없습니다. 다른 자료나 도구가 삼성 이메일의 경로를 보여 주더라도 검체에서 직접 확인하고 쓰고, 도구 출력은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 방법으로 원본 행과 맞춰 봅니다.

둘째, AOSP 소스는 오래된 master 브랜치라서 [2], 칸이 더해지거나 빠졌을 수 있습니다. 표 이름이 같아도 칸 목록은 검체 DB 에서 다시 읽습니다.

셋째, 삭제한 메일이 `Message_Deletes` 나 SQLite 여유 공간에 남는지는 검체에서 확인해야 합니다. SQLite 에서 지운 행을 찾는 방법은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md) 페이지에서 다룹니다.

## 직접 분석해 보기

### 앱을 직접 조사하기

공개 자료가 없으니 시험 기기에 앱을 설치해 계정을 넣고 메일을 주고받은 뒤, 앱 데이터 폴더에 무엇이 생기는지 보면 됩니다. 알려진 동작을 한 가지씩 하고 파일을 비교하는 절차는 [앱 데이터 분석 (App Data Analysis)](../../03-techniques/analysis/app-data-analysis/index.md) 페이지에서 다룹니다. SQLite 파일을 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에 있습니다.

DB 를 찾았으면 먼저 표 이름을 뽑아 AOSP 구조와 맞는지 봅니다. 아래 질의는 위 AOSP 구조 표로 만든 예시이고, 검체 DB 에 같은 표가 있을 때만 돌아갑니다.

```sql
SELECT name FROM sqlite_master WHERE type = 'table';

SELECT a.emailAddress, mb.displayName AS folder,
       datetime(m.timeStamp / 1000, 'unixepoch') AS ts_utc,
       m.fromList, m.subject, m.flagRead, m.flagLoaded
FROM Message m
JOIN Account a  ON m.accountKey = a._id
JOIN Mailbox mb ON m.mailboxKey = mb._id
ORDER BY m.timeStamp;
```

### 공개 도구로 한 번

ALEAPP 에는 삼성 이메일 전용 모듈이 없습니다 [1]. SQLite 뷰어로 직접 여는 것이 기본이고, DB 가 AOSP 구조와 같다고 확인되면 지메일 앱의 EmailProvider 를 읽는 ALEAPP 모듈 [3] 의 질의를 참고해 볼 수 있습니다. 이때 모듈이 찾는 경로는 지메일 앱 폴더라서 그대로는 삼성 이메일 DB 를 찾지 못합니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [계정 (Accounts)](../system-account/accounts/index.md) | 메일 계정을 기기에 넣고 뺀 기록 |
| [설치된 앱 (packages.xml)](../app-usage/packages/index.md) | 앱 패키지 이름과 설치·업데이트 시점 |
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | 메일 시각 앞뒤로 앱을 앞에 띄운 기록 |
| [알림 기록 (Notification History)](../app-usage/notification-history.md) | 새 메일 알림과 DB 의 메일이 맞는지 |

`dumpsys account` 출력에는 계정 추가·삭제 동작을 적은 "Accounts History" 표가 있습니다. 칸 뜻과 읽는 법은 [계정 (Accounts)](../system-account/accounts/index.md) 페이지에서 다룹니다. 메일로 누구와 연락했는지 묶어 보는 흐름은 [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md) 에 있습니다.

## 실습

공개 안드로이드 검체(NIST CFReDS 등) 중 갤럭시 기기 이미지가 있으면 아래 질문을 풀어 봅니다.

1. 설치된 앱 목록에서 삼성 이메일에 해당하는 패키지를 찾을 수 있습니까? 그 근거는 무엇입니까?
2. 그 앱 데이터 폴더의 `databases` 아래에 어떤 파일이 있고, 표 이름이 위 AOSP 구조와 얼마나 겹칩니까?
3. `Message` 와 같은 표가 있다면 `flagLoaded` 값별 행 수는 어떻게 됩니까?
4. `HostAuth` 와 같은 표가 있다면, 비밀번호 칸을 보고서에서 어떻게 가릴지 정해 봅니다.

## 참고 문헌

1. ALEAPP 저장소 파일 목록 (GitHub API, git trees, recursive) — https://api.github.com/repos/abrignoni/ALEAPP/git/trees/main?recursive=1
2. AOSP Email 앱 EmailContent.java (aosp-mirror platform_packages_apps_email, master) — https://raw.githubusercontent.com/aosp-mirror/platform_packages_apps_email/master/emailcommon/src/com/android/emailcommon/provider/EmailContent.java
3. ALEAPP — scripts/artifacts/gmailIMAPEmails.py (Gmail - IMAP Mailbox Emails, IMAP Accounts 모듈) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/gmailIMAPEmails.py
