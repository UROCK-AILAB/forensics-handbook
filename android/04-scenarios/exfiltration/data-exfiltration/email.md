---
title: "메일로"
parent: "자료를 밖으로 보냈나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 1720
---

# 메일로 (Email)

메일 앱으로 자료를 밖으로 보냈는지 확인하는 순서를 정리합니다. 이 페이지는 Gmail 을 중심으로 씁니다. Gmail 은 메일 본문과 머리를 압축한 protobuf 로 저장해서 표를 그대로 읽어서는 받는 사람이나 제목이 보이지 않습니다. 유출 경로 전체의 길잡이는 [자료를 밖으로 보냈나 (Data Exfiltration)](index.md) 허브에 있습니다.

## 조사 질문

이 기기의 메일 앱으로 문제의 파일을 첨부해 보냈는지, 보냈다면 어느 계정에서 누구에게 언제 보냈는지 묻습니다. 메일은 서버에 원본이 남는 서비스라서 기기에는 일부만 캐시로 남을 수 있고, 기기에서 찾은 흔적을 서버 쪽 자료와 맞춰 보는 과정까지 염두에 둡니다.

## 먼저 확인할 것

어떤 메일 계정이 기기에 붙어 있었는지부터 봅니다. `dumpsys account` 의 계정 목록과 계정 추가·삭제 기록은 허브에서 요약하고, 구조는 [계정 (Accounts)](../../../02-artifacts/system-account/accounts/index.md) 페이지에 있습니다. 조사 기간에만 잠깐 붙었다 떨어진 메일 계정이 있다면 따로 적어 둡니다.

메일 앱 DB 는 앱 데이터 폴더 안에 있어서 수집본에 그 폴더가 들어 있는지 확인합니다([앱 데이터 폴더 구조 (/data/data·/data/user)](../../../01-foundations/storage/app-data-layout.md)). 어떤 메일 앱이 설치돼 있었는지는 [설치된 앱 (packages.xml)](../../../02-artifacts/app-usage/packages/index.md)에서, 조사 기간에 앞에 띄웠는지는 [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md)에서 봅니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 계정 목록과 변경 기록 | 어떤 메일 계정이 언제 붙고 떨어졌는지 | [계정 (Accounts)](../../../02-artifacts/system-account/accounts/index.md) |
| 2 | 앱 사용 기록 | 메일 앱을 언제 앞에 띄웠는지 | [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) |
| 3 | 메일 앱 DB | 메일 머리·본문·첨부 목록 | [지메일 (Gmail)](../../../02-artifacts/mail-cloud/gmail.md), [삼성 이메일 (Samsung Email)](../../../02-artifacts/mail-cloud/samsung-email.md) |
| 4 | 메일 앱의 첨부 폴더 | 첨부 파일 실물 | 아래 절 |
| 5 | 계정 쪽 자료 | 서버의 보낸편지함 | [클라우드 데이터 (Google Takeout 등)](../../../03-techniques/acquisition/cloud-data.md) |

## Gmail 에서 보낸 메일과 첨부 찾기

Gmail 의 구조 전체는 [지메일 (Gmail)](../../../02-artifacts/mail-cloud/gmail.md) 페이지에 있고, 여기서는 유출을 따질 때 필요한 부분만 적습니다. 메일 DB 는 `*/com.google.android.gm/databases/bigTopDataDB.*` 이고, 로그인한 계정마다 `bigTopDataDB.<숫자 id>` 파일이 하나씩 있습니다 [2]. 어느 파일이 어느 계정인지는 `*/com.google.android.gm/shared_prefs/Gmail.xml` 에 적힌 메일 주소로 맞추는데, ALEAPP 시험 이미지에서는 주소 문자열의 Java `String.hashCode` 값이 파일 이름 뒤의 숫자와 같았습니다 [2]. 계정이 둘 이상이면 파일마다 이 대조를 먼저 해 둡니다.

메일은 `item_messages` 표에, 첨부 목록은 `item_message_attachments` 표에 있고, 첨부 표의 `item_messages_row_id` 가 `item_messages.row_id` 와 이어집니다 [2]. 받는 사람, 회신 주소, 제목 같은 머리와 본문은 `item_messages` 의 `zipped_message_proto` 열에 zlib 으로 압축한 protobuf 로 들어 있습니다 [2]. protobuf 는 필드 이름 없이 번호만 남기는 형식이고, Gmail 의 필드 번호는 ALEAPP 가 시험 이미지에서 맞춰 정한 것입니다 [2]. 형식은 [프로토콜 버퍼 (Protocol Buffers)](../../../01-foundations/data-formats/protobuf.md) 페이지에 있습니다.

읽는 순서는 다음과 같습니다.

1. `item_messages` 의 행마다 `zipped_message_proto` 값을 꺼내 첫 바이트를 떼고 zlib 으로 풉니다 [2].
2. 풀린 바이트를 protobuf 로 해석해 필드 번호와 값의 쌍을 얻습니다.
3. ALEAPP 가 정한 번호로 받는 사람·제목 등을 읽고, 필드 17 을 유닉스 밀리초(UTC) 시각으로 읽습니다 [2].
4. 같은 `row_id` 로 `item_message_attachments` 의 첨부 행을 붙입니다.

첨부 파일 실물은 `*/com.google.android.gm/files/downloads/*/attachments/*/*.*` 에 있습니다 [2]. 이 폴더에 파일이 있다고 해서 그 파일을 보냈다는 뜻은 아니고, 받은 메일의 첨부를 내려받은 것일 수도 있습니다.

같은 앱의 `downloader.db` 에는 `download_requests` 표가 있고, 열은 `request_time_ms`(밀리초), `account_name`, `type`, `caller_id`, `url`, `target_file_path`, `target_file_size`, `priority` 입니다 [2]. 이름 그대로 내려받기 요청의 기록이라서 보낸 쪽보다는 받은 첨부를 언제 기기에 내려받았는지를 볼 때 씁니다. ALEAPP 시험 이미지 대부분에서 0행이었습니다 [2].

`bigTopDataDB` 의 `label_counts` 표에는 라벨마다 `label_server_perm_id`, `unread_count`, `total_count`, `unseen_count` 가 있습니다 [2]. 이 표는 라벨별 개수만 담아서, 이것만으로 보낸 메일을 골라낼 수는 없습니다. 그래서 기기 쪽에서는 메일이 이 계정 저장소에 있었다는 사실과 받는 사람·제목·시각까지만 적고, 보낸 메일인지는 계정 쪽 보낸편지함과 맞춰 확인합니다. ALEAPP 시험 이미지에는 삼성 Galaxy S10(galaxys10_a10, Android 10)과 Pixel 기기가 섞여 있고, 계정 저장소가 둘인 이미지도 있습니다 [2].

## 다른 메일 앱

ALEAPP 에는 gmail.py, gmailIMAPEmails.py, outlook.py, protonmail.py, protonmailDbMail.py, protonmailInbox.py, yahooMail.py, K9Mail.py, FairEmail.py, thunderbird.py, tutanota.py 모듈이 있습니다 [1].

삼성 기기라면 [삼성 이메일 (Samsung Email)](../../../02-artifacts/mail-cloud/samsung-email.md) 페이지를 따로 봅니다.

## 분석 흐름

1. 계정 목록과 계정 변경 기록으로 조사 기간의 메일 계정을 적습니다.
2. usagestats 로 메일 앱을 앞에 띄운 시각대를 좁힙니다.
3. Gmail 이면 계정별 `bigTopDataDB` 파일을 계정 주소와 맞춘 뒤, 메일 protobuf 를 풀어 받는 사람·제목·시각을 뽑습니다.
4. 첨부가 있는 메일을 골라 첨부 이름을 문제의 파일과 맞춰 봅니다.
5. 찾은 메일이 보낸 메일인지는 적법한 절차로 받은 계정 쪽 자료의 보낸편지함과 맞춰 확인합니다. 기기 캐시에 없는 메일도 이 단계에서 드러납니다.

## 흔한 오판

첨부 폴더나 `download_requests` 에 문제의 파일이 있다는 사실만으로 보냈다고 보지 않습니다. 두 곳 모두 받은 메일의 첨부를 내려받을 때도 생기는 기록입니다.

protobuf 필드 번호를 공식 사양처럼 적지 않습니다. 번호의 뜻은 ALEAPP 가 시험 이미지에서 맞춰 보고 정했을 뿐이라서, 앱 판이 다르면 맞지 않을 수 있습니다. 보고서에 받는 사람이나 시각을 적을 때는 어떤 필드 번호를 어떻게 읽었는지 함께 적습니다.

기기 캐시에 메일이 없다는 사실로 보내지 않았다고 결론 내리지 않습니다. 메일 원본은 서버에 있고 기기에는 일부만 남을 수 있습니다.

## 보고서 문장 예

- "Gmail 앱의 `bigTopDataDB` 파일 가운데 (계정 주소)에 해당하는 파일에서, 첨부 이름이 문제의 파일과 같은 메일이 확인됩니다. 이 메일의 시각(protobuf 필드 17, ALEAPP 해석 기준)은 (현지 시각)입니다."
- "이 기록은 해당 첨부가 달린 메일이 이 계정의 메일 저장소에 있었다는 뜻이며, 이 메일을 이 기기에서 보냈는지와 받는 사람이 열었는지는 이 기록만으로 알 수 없습니다."

## 함께 볼 페이지

- [누구와 연락을 주고받았나 (Communication)](../../activity/communication.md)
- [계정 탈취 흔적 (Account Takeover)](../../incident/account-takeover.md)
- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)
- 같은 허브의 다른 경로: [메신저로 (Messenger)](messenger.md), [클라우드로 (Cloud)](cloud.md), [PC 연결로 (USB·PC)](usb-pc.md), [근거리 공유로 (Quick Share·Bluetooth)](nearby-share.md)

## 참고 문헌

1. ALEAPP scripts/artifacts 폴더 목록 — GitHub API, https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
2. gmailEmails.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/gmailEmails.py
