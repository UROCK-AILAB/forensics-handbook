---
title: "메신저로"
parent: "자료를 밖으로 보냈나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 1560
---

# 메신저로 (Messenger)

메신저로 파일·사진·문서를 밖으로 보냈는지 판별하는 페이지입니다. 기본 메시지 앱(iMessage·SMS·RCS)과 다른 회사 메신저는 기록이 남는 곳이 달라서 둘을 나눠 보고, 앱 자체 DB 를 읽지 못할 때 앱별 데이터 사용량으로 넘어가는 순서로 설명합니다. 다른 유출 경로와 전체 흐름은 허브 [자료를 밖으로 보냈나 (Data Exfiltration)](index.md) 에 있습니다.

## 조사 질문

"이 아이폰에서 메신저로 자료를 보낸 기록이 있는가, 있다면 어느 앱으로 언제 무엇을 보냈는가" 를 묻습니다. 보낸 파일의 이름·형식·크기와 받은 사람, 보낸 시각까지 좁히는 데가 목표이고, 앱 DB 가 없으면 "어느 앱이 어느 시간대에 얼마나 송신했는가" 까지만 답합니다.

## 먼저 확인할 것

iOS 버전과 기기에 설정된 시간대를 먼저 적어 둡니다. 버전은 [기기 정보 (Device Info·Lockdown)](../../../02-artifacts/system-account/device-info.md), 시간대는 [시간대와 시각 설정 (Time Zone)](../../../02-artifacts/system-account/time-zone.md) 에서 확인합니다. 시각 값은 DB 마다 기준을 따로 확인하고, 읽는 법은 [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md) 을 따릅니다.

수집 범위도 확인합니다. 로컬 백업이면 기본 메시지 DB 는 `HomeDomain :: Library/SMS/sms.db` 로, 앱별 데이터 사용량 DB 는 `WirelessDomain :: Library/Databases/DataUsage.sqlite` 로 보입니다. 카카오톡·WhatsApp 같은 다른 회사 앱이 백업의 어느 경로에 들어가는지는 실제 데이터로 확인합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 메시지 DB (`sms.db`) 의 attachment·message 표 | 보낸 첨부의 이름·형식·크기, 보낸 메시지의 시각과 서비스 | [메시지 (iMessage·SMS)](../../../02-artifacts/communications/messages/index.md) |
| 2 | WhatsApp `ChatStorage.sqlite` | 메시지(ZWAMESSAGE)와 보낸 미디어 정보(ZWAMEDIAITEM) | [왓츠앱 (WhatsApp)](../../../02-artifacts/messengers/whatsapp.md) |
| 3 | 다른 회사 메신저의 앱 DB | 앱마다 다름 | [카카오톡 (KakaoTalk)](../../../02-artifacts/messengers/kakaotalk/index.md), [텔레그램 (Telegram)](../../../02-artifacts/messengers/telegram.md) |
| 4 | `DataUsage.sqlite` 의 ZLIVEUSAGE·ZPROCESS 표 | 앱별 셀룰러 송신 바이트와 시각 | [앱별 데이터 사용량 (DataUsage.sqlite)](../../../02-artifacts/network/data-usage.md) |

### 기본 메시지 앱

대화 DB 의 전체 구조와 첨부 파일이 저장되는 경로, 시각 기준은 [메시지 (iMessage·SMS)](../../../02-artifacts/communications/messages/index.md) 에 있습니다. 유출을 판별할 때는 그중 첨부와 방향에 관한 열만 골라 봅니다. `sms.db` 의 attachment 표에는 is_outgoing, transfer_name, filename, mime_type, uti, total_bytes, created_date, start_date, transfer_state, original_guid 열이 있고, message 표에는 is_from_me, is_sent, is_delivered, date, date_delivered, date_read, service, account_guid, share_status, share_direction 열이 있습니다. 메시지와 첨부는 message_attachment_join 표로, 대화와 메시지는 chat_message_join 표로 잇습니다.

share_status·share_direction 열은 이름만 보면 공유 방향과 관련이 있어 보이지만, 이름만으로 값의 뜻을 단정할 수 없으니 보고서에는 값만 옮깁니다. 백업의 `com.apple.sharingd.plist` 에는 `SFCollaborationUserDefaults.com.apple.MobileSMS` 키가 있고, `HomeDomain :: Library/Application Support/CloudDocs/session/containers/iCloud.com.apple.MobileSMS.plist` 라는 메시지용 iCloud 컨테이너 설정 파일도 있습니다. 두 파일이 무엇을 기록하는지는 이름만으로 판단할 수 없으니 보고서에 근거로 쓰지 않습니다.

### 다른 회사 메신저

WhatsApp 은 대화 DB 가 `ChatStorage.sqlite` 이고, 메시지는 ZWAMESSAGE 표에, 보낸 미디어 정보는 ZWAMEDIAITEM 표에 있습니다[2]. 알려진 경로는 `/root/var/mobile/Applications/net.whatsapp.WhatsApp/Documents/ChatStorage.sqlite` 라는 옛 구조이고[2], 요즘 iOS 에서 앱 그룹 컨테이너 아래 어디에 있는지는 실제 데이터로 확인합니다. 같은 위치의 `Contacts.sqlite` 에는 JID 가 없습니다[2]. 열 이름과 시각 기준은 [왓츠앱 (WhatsApp)](../../../02-artifacts/messengers/whatsapp.md) 에서 확인합니다. 앱 그룹 컨테이너를 찾는 방법은 [번들 ID와 앱 그룹 (Bundle ID·App Group)](../../../01-foundations/value-decoding/bundle-id-app-group.md) 에 있습니다.

카카오톡·텔레그램 같은 다른 메신저의 iOS 저장 구조는 각 앱의 아티팩트 페이지를 따릅니다.

### 앱 DB 를 읽지 못할 때

앱 DB 가 암호화되어 있거나 수집 범위에 들어오지 않았으면 `DataUsage.sqlite` 로 그 앱의 셀룰러 송신량과 시각을 봅니다[1]. ZLIVEUSAGE 표의 ZWWANOUT 열이 셀룰러 송신량이고 단위는 바이트이며, ZPROCESS 표의 ZFIRSTTIMESTAMP 는 그 프로세스를 처음 본 때, ZTIMESTAMP 는 가장 최근 활동을 가리킵니다[1]. 시각은 Mac 절대 시각입니다[1]. ZLIVEUSAGE 표에는 ZKIND, ZMETADATA, ZTAG, ZHASPROCESS, ZBILLCYCLEEND, ZTIMESTAMP, ZWWANIN, ZWWANOUT, ZBUNDLENAME, ZPROCNAME 열이, ZPROCESS 표에는 ZFIRSTTIMESTAMP, ZTIMESTAMP, ZBUNDLENAME, ZEXTENSIONNAME, ZPROCNAME 열이 있습니다. 표 구조와 읽는 법은 [앱별 데이터 사용량 (DataUsage.sqlite)](../../../02-artifacts/network/data-usage.md) 에 있습니다.

## 분석 흐름

1. iOS 버전·시간대·수집 범위를 적고, 조사 기간을 UTC 와 현지 시각으로 함께 정해 둡니다.
2. `sms.db` 에서 attachment 표를 message_attachment_join 으로 message 표에 잇고, 다시 chat_message_join 으로 대화에 잇습니다. 아래 질의는 위 열 이름으로 만든 예시이고, 방향 열의 값은 조건으로 거르지 않고 그대로 뽑아서 [메시지 (iMessage·SMS)](../../../02-artifacts/communications/messages/index.md) 의 설명대로 읽습니다.
   ```sql
   SELECT m.ROWID, m.date, m.service, m.is_from_me, m.is_sent, m.is_delivered,
          a.is_outgoing, a.transfer_name, a.mime_type, a.total_bytes,
          a.created_date, a.transfer_state, cmj.chat_id
   FROM attachment a
   JOIN message_attachment_join maj ON maj.attachment_id = a.ROWID
   JOIN message m ON m.ROWID = maj.message_id
   LEFT JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
   ORDER BY m.date;
   ```
3. 뽑은 행의 transfer_name·mime_type·total_bytes 를 유출이 의심되는 자료의 이름·형식·크기와 맞춰 봅니다. 이름이 바뀌었을 수 있어서 크기와 형식을 함께 봅니다.
4. 다른 회사 메신저가 설치되어 있으면 [설치된 앱 (Installed Apps·applicationState.db)](../../../02-artifacts/app-usage/installed-apps.md) 에서 확인하고, 그 앱의 DB 를 해당 아티팩트 페이지대로 읽습니다.
5. 앱 DB 를 읽지 못하면 `DataUsage.sqlite` 에서 그 앱의 번들 ID 행을 찾아 조사 기간의 ZWWANOUT 값과 시각을 봅니다.
6. 찾은 시각을 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) 에 올리고, 같은 시간대의 앱 사용 기록과 겹쳐 봅니다.

## 흔한 오판

첨부 행이 있다는 사실만으로 받은 사람이 파일을 저장하거나 열었다고 쓰지 않습니다. 보낸 쪽 기기의 기록으로는 보낸 쪽에서 일어난 일까지만 알 수 있습니다.

`DataUsage.sqlite` 는 Wi-Fi 사용량을 기록하지 않습니다[1]. 그래서 셀룰러 송신량이 적거나 0 이어도 그 앱이 Wi-Fi 로 많이 보냈을 수 있고, Wi-Fi·셀룰러를 모두 담는 `netusage.sqlite` 는 파일 시스템 추출에서만 얻습니다[1]. 로컬 백업에도 `netusage.sqlite` 는 들어가지 않습니다.

복원을 거친 기기는 옛 기기의 사용량 기록까지 이어져서, 2013년 기록이 남은 예가 있습니다[1]. ZFIRSTTIMESTAMP 가 조사 대상 기기의 구입 시기보다 이르면 복원 이력을 [초기화와 복원 흔적 (Erase·Restore)](../../../02-artifacts/system-account/erase-restore.md) 에서 확인합니다.

WhatsApp 파일을 옛 경로 그대로 찾으면 요즘 기기에서는 파일이 없다고 잘못 판단할 수 있습니다.

## 보고서 문장 예

> 메시지 DB(`sms.db`)의 attachment 표에 파일 이름이 ○○이고 크기가 ○○바이트인 첨부 행이 있고, message_attachment_join 으로 이어진 message 행의 date 값은 현지 시각 ○○입니다. 이 행은 이 기기에서 해당 첨부가 포함된 메시지를 처리한 기록이며, 받은 사람이 파일을 열었는지는 이 기록으로 알 수 없습니다.

> `DataUsage.sqlite` 의 ZLIVEUSAGE 표에 번들 ID ○○ 앱의 셀룰러 송신량(ZWWANOUT)이 ○○바이트로 기록되어 있고, 이 행의 ZTIMESTAMP 는 현지 시각 ○○입니다. 이 표는 Wi-Fi 송신을 담지 않습니다.

## 함께 볼 페이지

- [누구와 연락을 주고받았나 (Communication)](../../activity/communication.md)
- [클라우드로 (Cloud)](cloud.md), [메일로 (Email)](email.md), [에어드롭으로 (AirDrop)](airdrop.md), [PC 동기화로 (PC Sync)](pc-sync.md)
- [앱 데이터 분석 (App Data Analysis)](../../../03-techniques/analysis/app-data-analysis/index.md)
- [지운 대화와 사진 찾기 (Deleted Content)](../../activity/deleted-content.md)

## 참고 문헌

1. mac4n6.com, "Network and Application Usage using netusage.sqlite & DataUsage.sqlite iOS Databases" — http://www.mac4n6.com/blog/2019/1/6/network-and-application-usage-using-netusagesqlite-amp-datausagesqlite-ios-databases
2. Magnet Forensics, "Artifact Profile - WhatsApp Messenger" — https://www.magnetforensics.com/blog/artifact-profile-whatsapp-messenger/
