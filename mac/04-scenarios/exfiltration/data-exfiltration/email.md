---
title: "메일로"
parent: "자료를 밖으로 빼돌렸나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 2480
---

# 메일로 (Email)

이 맥의 메일 앱으로 자료를 첨부해 밖으로 보냈는지를 묻는 조사를 다룹니다. 애플 메일의 `Accounts.plist` 로 계정을 정리하고, Envelope Index 데이터베이스의 `mailboxes`·`messages`·`attachments`·`recipients` 표에서 보낸 편지함의 메시지와 첨부 이름, 받는 사람을 뽑은 뒤 보낸 시각을 메시지 파일 헤더와 대조합니다. 마지막으로 첨부 이름으로 최근 항목과 FSEvents 에서 원본 파일을 찾아, 보낸 시각 전후에 그 파일을 다룬 흔적이 있는지 봅니다.

## 조사 질문

이 맥의 메일 앱으로 자료를 첨부해 밖으로 보냈는지 묻습니다. 애플 메일 (Apple Mail)은 메시지와 첨부 목록을 데이터베이스와 메시지 파일로 남기고, 그 저장 구조와 표 설명은 [애플 메일 (Apple Mail)](../../../02-artifacts/mail/apple-mail/index.md) 페이지에 있습니다. 이 페이지는 그 기록에서 보낸 메일과 첨부를 골라내는 순서를 다루고, 브라우저로 웹메일을 쓴 경우는 [웹 업로드로](web-upload.md) 페이지에서 다룹니다. 경로마다 공통으로 쓰는 판단 원칙은 [자료를 밖으로 빼돌렸나](index.md) 허브에 있습니다.

## 먼저 확인할 것

먼저 어떤 메일 앱을 썼는지 확인합니다. [설치한 앱과 영수증](../../../02-artifacts/system-account/installed-apps-receipts.md)과 [어떤 앱을 언제 썼나](../../activity/app-usage.md)로 사용한 앱을 좁히고, 애플 메일이 아니라면 [아웃룩 (Outlook for Mac)](../../../02-artifacts/mail/outlook.md)이나 [썬더버드 (Thunderbird)](../../../02-artifacts/mail/thunderbird.md) 페이지를 따릅니다. 이 페이지의 흐름은 애플 메일 기준입니다.

사용자와 수집 범위도 함께 봅니다. 애플 메일 경로와 그 ForensicArtifacts 정의 이름은 아래와 같고, 모두 사용자 홈 아래에 있습니다 [1].

| 정의 이름 | 경로 |
|---|---|
| MacOSMailAccounts | `~/Library/Mail/V[0-9]/MailData/Accounts.plist` |
| MacOSMailPreferences | `~/Library/Preferences/com.apple.Mail.plist` |
| MacOSMailMainDirectory | `~/Library/Mail/V[0-9]/*` |
| MacOSMailboxes | `~/Library/Mail/V[0-9]/Mailboxes/*` |
| MacOSMailDownloadAttachments | `~/Library/Containers/com.apple.mail/Data/Library/Mail Downloads/*` |

정의의 `V[0-9]`는 한 자리 숫자에만 맞는 패턴이고, 정의에 적힌 폴더는 V2·V3·V5입니다 [1]. `V10`처럼 두 자리 이름의 폴더는 이 패턴에 맞지 않아 자동 수집에서 빠질 수 있으므로, 수집 결과에 메일 폴더가 비어 있으면 실제 폴더 이름부터 확인합니다. 시각은 [시간대와 시계 설정](../../../02-artifacts/system-account/time-zone.md)으로 맥의 시간대를 확인한 뒤 한 기준으로 바꿔 적습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `Accounts.plist` | 이 맥에 설정한 메일 계정 | [애플 메일](../../../02-artifacts/mail/apple-mail/index.md) |
| 2 | Envelope Index 데이터베이스의 `mailboxes` 표 | 계정별 메일함 목록 | [애플 메일](../../../02-artifacts/mail/apple-mail/index.md) |
| 3 | 같은 데이터베이스의 `messages`, `attachments`, `recipients` 표 | 메시지, 첨부 이름, 받는 사람 | [애플 메일](../../../02-artifacts/mail/apple-mail/index.md) |
| 4 | `Mailboxes` 아래 메시지 파일(emlx) | 메시지 원본과 헤더 | [애플 메일](../../../02-artifacts/mail/apple-mail/index.md) |
| 5 | 첨부 원본 파일의 최근 항목과 FSEvents | 첨부하기 전에 그 파일을 다룬 흔적 | [최근 항목](../../../02-artifacts/file-folder-usage/recent-items/index.md), [파일 시스템 이벤트](../../../02-artifacts/filesystem/fsevents/index.md) |

## 분석 흐름

1. `Accounts.plist`에서 이 맥에 설정한 메일 계정을 정리합니다.
2. Envelope Index의 `mailboxes` 표에서 계정별 보낸 편지함에 해당하는 메일함을 고릅니다. 보낸 편지함이 이 표에서 어떤 값으로 나타나는지는 공개된 분석 자료가 없어서, 표 내용을 직접 보고 고릅니다.
3. 그 메일함에 속한 메시지를 뽑고, `attachments` 표(message, name)에서 각 메시지에 붙은 첨부 이름을 얻습니다.
4. `recipients` 표에서 같은 메시지의 받는 사람을 얻습니다.
5. 보낸 시각을 정합니다. 데이터베이스의 어느 열을 보낸 시각으로 볼지는 [애플 메일](../../../02-artifacts/mail/apple-mail/index.md) 페이지의 시각 설명을 따르고 메시지 파일 헤더의 시각과도 대조합니다.
6. 첨부 이름으로 맥 쪽 최근 항목과 FSEvents에서 원본 파일을 찾고, 메일을 보낸 시각 전후로 그 파일을 다룬 흔적이 있는지 [타임라인](../../../03-techniques/analysis/timeline/index.md)에 올려 봅니다.

## 흔한 오판

- **`Mail Downloads` 폴더의 파일을 보낸 첨부로 보는 경우.** 정의 이름대로 메일 앱이 첨부를 내려받아 두는 폴더라서, 보낸 메일의 근거로 바로 쓰지 않습니다.
- **보낸 편지함에 없으니 보내지 않았다고 보는 경우.** 사용자가 메일을 지웠을 수 있고, 지운 흔적은 [지운 파일의 흔적 찾기](../../activity/deleted-file-traces.md)와 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md)의 방법으로 따로 찾습니다.
- **자동 수집 결과에 메일 폴더가 없으니 메일 앱을 쓰지 않았다고 보는 경우.** 앞에서 적은 `V[0-9]` 패턴 문제로 폴더가 빠졌을 수 있습니다.
- **메일 앱 기록이 없으니 메일로 보내지 않았다고 보는 경우.** 브라우저로 웹메일을 썼다면 메일 앱에는 흔적이 없고, [웹 업로드로](web-upload.md) 페이지의 방법으로 찾습니다.

## 보고서 문장 예

> 사용자 ○○의 애플 메일 데이터베이스(Envelope Index)에는 계정 ○○의 보낸 편지함에 속한 메시지 한 건에 "○○.zip" 첨부 이름이 기록되어 있고, 받는 사람으로 ○○@○○이 기록되어 있습니다. 이 기록은 메일 앱이 이 메시지를 보낸 편지함에 저장했다는 사실을 보여 주지만, 받는 쪽 서버가 메일을 받았는지는 이 맥의 기록으로 알 수 없습니다.

## 함께 볼 페이지

- [애플 메일 (Apple Mail)](../../../02-artifacts/mail/apple-mail/index.md) — 저장 구조와 표 설명
- [누구와 연락을 주고받았나 (Communication)](../../activity/communication.md) — 받는 사람을 연락 기록 전체와 맞춰 보는 방법
- [웹 업로드로 (Web Upload)](web-upload.md) — 웹메일로 보낸 경우
- [메신저로 (Messenger)](messenger.md) — 메시지 첨부로 보낸 경우

## 참고 문헌

1. ForensicArtifacts, "artifacts/data/macos.yaml" — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
