---
title: "스미싱 흔적"
parent: "시나리오 · 침해 사고"
nav_order: 1630
---

# 스미싱 흔적 (Smishing)

스미싱이 의심될 때 그 문자가 아이폰에 남아 있는지, 사용자가 링크를 눌렀는지, 그 뒤 어느 사이트에 접속했는지를 묻는 조사를 다룹니다. `sms.db` 를 WAL 과 함께 열어 문자와 발신자를 찾고, 필터 관련 열·메시지 설정 plist·지운 메시지 표로 정크 분류나 삭제 여부를 봅니다. 링크를 눌렀는지는 Safari 방문 기록과 도메인 관찰 기록 `observations.db` 로 확인하고, 메일 앱의 같은 기록과도 비교합니다.

## 조사 질문

문자 메시지로 가짜 링크를 보내 개인 정보나 계정 암호를 가로채는 스미싱 (smishing)이 의심될 때, 그 문자가 기기에 남아 있는지, 사용자가 링크를 눌렀는지, 그 뒤 어느 사이트에 접속했는지를 확인합니다. 링크를 누른 뒤 계정 암호를 입력했을 가능성이 보이면 [계정 탈취 흔적](account-takeover.md)으로 넘어갑니다. 이 페이지는 남는 흔적과 그 해석만 다룹니다.

## 먼저 확인할 것

**문자가 스미싱인지 가르는 기준**은 피싱 징후입니다. 보낸 사람의 이메일 주소나 번호가 회사 이름과 맞지 않거나, 링크가 그럴듯해 보여도 실제 URL 이 회사 사이트와 다르거나, 암호·카드 번호 같은 개인 정보를 요구하거나, 요청하지 않은 첨부가 붙어 있으면 의심합니다 [1]. Apple 은 어떤 웹사이트에 로그인하라거나 2단계 인증 창에서 "허용" 을 누르라고 요구하지 않습니다 [1]. Apple 위협 알림을 흉내 낸 문자도 있는데, 진짜 위협 알림이 어떤 경로로 오는지는 [스파이웨어 감염 흔적](spyware.md)에 정리했습니다.

**사용자가 이미 한 조치**를 먼저 묻습니다. 아이폰에서는 링크를 길게 눌러 실제 주소를 먼저 볼 수 있고, 메시지 아래의 "정크 신고 (Report Junk)" 로 신고하거나 발신자를 차단할 수 있습니다. Apple 을 사칭한 문자는 화면을 찍어 reportphishing@apple.com 으로 보냅니다 [1]. 사용자가 신고·차단·삭제를 했다면 그 시각을 적어 두어야 기기에 남은 기록과 맞춰 볼 수 있습니다.

**iOS 버전과 수집 범위**도 확인합니다. 메시지 앱의 "최근 삭제된 항목" 은 iOS 16 이후에 있고, 지운 메시지를 30일 동안 보관한다고 알려져 있지만 [4] Apple 은 이 기간을 30~40일로 적었습니다 [5]. Safari 방문 기록은 암호화 백업에만 들어가서 [8], 암호화하지 않은 백업만 받았다면 링크를 눌렀는지를 다른 기록으로 봐야 합니다.

**필터가 개입했는지**도 염두에 둡니다. 모르는 발신자에게서 받은 SMS·MMS 는 메시지 앱이 SMS/MMS 필터 앱 확장 (IdentityLookup)에 넘겨 원치 않는 메시지인지 판단하게 할 수 있습니다. 이 확장은 모르는 발신자의 SMS·MMS 에만 작동하고, 연락처에 있는 발신자나 iMessage 에는 작동하지 않습니다 [2]. 확장이 스스로 판단하지 못하면 메시지 정보를 앱과 연결된 서버로 보내 달라고 메시지 앱에 요청할 수 있는데, 통신은 시스템이 하고 확장은 네트워크에 직접 접근하지 못하며, 앱과 공유하는 컨테이너에 데이터를 쓸 수도 없습니다 [2]. 그래서 필터 앱의 컨테이너에서 메시지 사본을 찾으려 하지 않습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `sms.db` 의 `message`·`handle` 표 | 문자 본문과 링크, 발신 번호, 서비스, 받은 시각 | [메시지](../../02-artifacts/communications/messages/index.md) |
| 2 | `sms.db` 의 필터 관련 열 | 모르는 발신자 필터·정크 분류에 걸렸는지의 단서 | [메시지](../../02-artifacts/communications/messages/index.md) |
| 3 | 메시지 설정 plist | 필터 확장 설치·분류 설정의 단서 | [설정 값](../../02-artifacts/system-account/preferences.md) |
| 4 | 최근 삭제된 항목 표 | 사용자가 지운 문자 | [지운 대화와 사진 찾기](../activity/deleted-content.md) |
| 5 | Safari 방문 기록·도메인 관찰 기록 | 링크를 눌러 접속했는지, 어느 도메인으로 넘어갔는지 | [사파리](../../02-artifacts/browsers/safari/index.md) |
| 6 | 메일 앱의 도메인 관찰 기록 | 같은 링크가 메일로도 왔는지 견줄 거리 | [메일 앱](../../02-artifacts/mail-cloud/apple-mail.md) |

## 분석 흐름

1. **`sms.db` 를 WAL 과 함께 엽니다.** 기기에서는 `/private/var/mobile/Library/SMS/sms.db` 에 있고 [3], 로컬 백업에서는 `HomeDomain :: Library/SMS/sms.db` 입니다. WAL 없이 열면 최근 메시지가 경고 없이 빠집니다 [4]. 날짜는 2001-01-01 UTC 기준 Mac 절대 시각이고 대략 iOS 11 부터 나노초 단위라서, 초로 나눈 뒤 978307200 을 더하면 UNIX 시각이 됩니다 [4]. 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md)에 자세히 있습니다.

2. **문자와 발신자를 찾습니다.** `handle` 표의 `id`, `service`, `uncanonicalized_id` 로 발신 번호와 서비스를 보고, `message` 표의 `text`, `attributedBody` 에서 본문과 링크를 찾습니다. `message` 표에는 `has_dd_results`, `was_data_detected`, `balloon_bundle_id`, `payload_data` 열도 있어서 링크가 본문 밖에 담긴 경우를 함께 봅니다. MVT 의 SMS 모듈은 `sms.db` 에서 메시지 속 링크를 뽑아 공개 지표와 대조합니다 [6].

3. **필터에 걸렸는지 봅니다.** `sms.db` 에는 필터와 관련된 다음 열이 있습니다.

   ```
   chat:              is_filtered, is_blackholed, is_pending_review
   chat_message_join: filter_action, filter_sub_action
   sync_chat_slice:   filter_action, filter_sub_action
   ```

   각 값이 정크 폴더·차단·검토 대기 가운데 무엇을 뜻하는지는 실제 데이터로 확인해야 합니다. 값을 해석할 때는 같은 기기에서 사용자가 정크로 옮긴 대화와 그렇지 않은 대화의 값을 비교하고, 해석 근거를 보고서에 적습니다.

4. **메시지 설정 plist 를 봅니다.** `HomeDomain :: Library/Preferences/com.apple.MobileSMS.plist` 에는 필터와 모르는 발신자에 관련된 이름의 키가 있습니다.

   ```
   MessageSpamFilteringExtensionInstalled
   FirstPartyTextMessageFilterAvailable
   spamFiltrationFirstPartyExtensionVersion
   FilterMessageRequestsMigrationVersion
   PromotionsRequestsMigrationVersion
   TransactionsRequestsMigrationVersion
   TimeSensitiveRequestsMigrationVersion
   VerificationCodesRequestsMigrationVersion
   NumberOfUnknownChatsOpened
   DeleteVerificationCodes
   EnhancedLinkSecurityURLKey
   simFilterIndex
   ```

   각 키의 뜻은 이름에서 짐작할 수 있을 뿐 공개된 분석 자료가 없으므로, 보고서에는 키 이름과 값만 적고 뜻을 단정하지 않습니다. 필터 확장과 관련된 백업 도메인 `AppDomain-com.apple.smsFilter` 와 `AppDomainPlugin-com.apple.smsFilter.extension` 도 있습니다.

5. **정크 자동 삭제 가능성을 염두에 둡니다.** `HomeDomain :: Library/Preferences/com.apple.IMAutomaticHistoryDeletionAgent.plist` 에 날짜 형식의 키 `startDeletingJunkMessagesFrom` 이 있습니다. 이름으로 보면 정크 메시지 자동 삭제와 관련 있어 보이지만, 동작과 보관 기간은 공개된 분석 자료가 없습니다. 사용자가 받았다고 말한 문자가 보이지 않으면, 정크로 분류된 뒤 지워졌을 가능성을 열어 두고 이 키의 값과 받은 시각을 함께 적습니다.

6. **지운 문자를 찾습니다.** `sms.db` 에는 `chat_recoverable_message_join`(`delete_date` 포함)과 `recoverable_message_part`(`part_text` 포함) 표가 있습니다. 복구 절차는 [지운 대화와 사진 찾기](../activity/deleted-content.md)를 따릅니다. 모르는 발신자 기록으로 보이는 `HomeDomain :: Library/MessagesMetaData/NickNameCache/unknownSenderRecordInfoStore.db`(표 `kvtable`: `ROWID`, `key`, `value`, `value_type`, `date`)도 있지만, 용도는 공개된 분석 자료가 없습니다.

7. **링크를 눌렀는지 봅니다.** 암호화 백업이라면 Safari `History.db` 의 `history_items`(`url`, `visit_count`)와 `history_visits`(`visit_time`, `redirect_source`, `redirect_destination`, `origin`)에서 문자 속 URL 과 그 뒤 리디렉션을 찾습니다 [7]. 암호화하지 않은 백업에도 `AppDomain-com.apple.mobilesafari :: Library/WebKit/WebsiteData/ResourceLoadStatistics/observations.db` 가 들어가고, 표 `ObservedDomains`(`registrableDomain`, `lastSeen`, `hadUserInteraction`, `mostRecentUserInteractionTime` 등)와 `TopFrameUniqueRedirectsTo`(`sourceDomainID`, `toDomainID`), `TopFrameUniqueRedirectsFrom`, `SubresourceUniqueRedirectsTo` 등이 있습니다. MVT 의 WebkitResourceLoadStatistics 모듈은 이 파일에서 접속한 도메인과 시각을 뽑습니다 [6]. `lastSeen` 이 어떤 기준 시각인지는 알려져 있지 않아서, 문자 받은 시각과 비교하기 전에 다른 기록으로 기준을 맞춥니다. 시각 해석과 표 구성은 [사파리](../../02-artifacts/browsers/safari/index.md)에, 행위 재구성은 [웹 사용 행위 재구성](../activity/web-activity.md)에 있습니다.

8. **메일 쪽도 비교합니다.** 메일 앱에도 `AppDomain-com.apple.mobilemail :: Library/WebKit/WebsiteData/ResourceLoadStatistics/observations.db` 가 있습니다. 같은 도메인이 메일 쪽에도 나오면 같은 피싱이 메일로도 왔는지 [메일 앱](../../02-artifacts/mail-cloud/apple-mail.md)에서 확인합니다.

## 흔한 오판

- **메시지 목록에 없으니 받지 않았다고 봅니다.** 정크로 분류됐거나 사용자가 지웠을 수 있습니다. 필터 열과 최근 삭제된 항목 표부터 봅니다.
- **필터 앱 컨테이너에 원본 문자가 있을 거라고 봅니다.** 필터 확장은 공유 컨테이너에 데이터를 쓸 수 없습니다 [2].
- **iMessage 로 온 문자도 필터 앱이 걸렀을 거라고 봅니다.** IdentityLookup 필터는 모르는 발신자의 SMS·MMS 에만 작동합니다 [2].
- **방문 기록이 없으니 링크를 누르지 않았다고 봅니다.** 암호화하지 않은 백업에는 Safari 방문 기록이 들어가지 않습니다 [8]. 도메인 관찰 기록으로 보고, 둘 다 없으면 "확인하지 못했다" 고 씁니다.
- **`sms.db` 본 파일만 엽니다.** WAL 을 빼면 최근 메시지가 빠집니다 [4].

## 보고서 문장 예

> `sms.db` 에서 발신 번호 (번호)가 (UTC 시각)에 보낸 SMS 가 있고, 본문에 (도메인)으로 가는 링크가 있었다. 이 대화의 `chat.is_filtered` 값은 (값)이지만, 이 값이 뜻하는 분류는 확인하지 못했다.

> Safari `observations.db` 의 `ObservedDomains` 표에 (도메인) 행이 있었다. 이 기록은 해당 도메인에 접속한 기록이 있다는 것까지 보여 주며, 사용자가 그 페이지에 무엇을 입력했는지는 보여 주지 않는다.

## 함께 볼 페이지

- [계정 탈취 흔적](account-takeover.md) — 링크를 누른 뒤 계정이 넘어갔는지
- [메시지](../../02-artifacts/communications/messages/index.md) · [사파리](../../02-artifacts/browsers/safari/index.md) · [메일 앱](../../02-artifacts/mail-cloud/apple-mail.md)
- [누구와 연락을 주고받았나](../activity/communication.md) · [웹 사용 행위 재구성](../activity/web-activity.md)
- [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) — WAL 을 함께 읽는 법
- [로컬 백업](../../01-foundations/backups/local-backup/index.md) — 암호화 여부에 따라 들어가는 파일

## 참고 문헌

1. Apple Support, Recognize and avoid phishing messages, phony support calls, and other scams (102568, 2026-06-15) — https://support.apple.com/en-us/102568
2. Apple Developer Documentation, SMS and MMS Message Filtering (IdentityLookup) — https://developer.apple.com/tutorials/data/documentation/identitylookup/sms-and-mms-message-filtering.json
3. Magnet Forensics, The Meaning of Messages (2023-03-09) — https://www.magnetforensics.com/blog/the-meaning-of-messages/
4. ChatExport/ChatExportKnowledge, README — https://github.com/ChatExport/ChatExportKnowledge
5. Apple Support, Recover deleted text messages on your iPhone or iPad — https://support.apple.com/en-us/102615
6. MVT, Records extracted by mvt-ios — https://docs.mvt.re/en/latest/ios/records/
7. iLEAPP, scripts/artifacts/safariHistory.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/safariHistory.py
8. Apple Support, About encrypted backups on your iPhone, iPad, or iPod touch — https://support.apple.com/en-us/108353
