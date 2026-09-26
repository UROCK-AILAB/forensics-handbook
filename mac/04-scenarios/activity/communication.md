---
title: "누구와 연락을 주고받았나"
parent: "시나리오 · 행위 재구성"
nav_order: 2350
---

# 누구와 연락을 주고받았나 (Communication)

## 조사 질문

조사 대상 맥의 사용자가 누구와, 언제, 어떤 수단으로 연락을 주고받았는지 묻습니다. 메시지·통화·메일·제3자 메신저가 각자 다른 데이터베이스에 기록을 남기고 시각 기준도 서로 달라서, 이 페이지는 수단별 기록을 어떤 순서로 읽고 한 타임라인에 어떻게 맞추는지를 다룹니다. 각 데이터베이스의 자세한 구조는 아티팩트 페이지에 있고, 여기서는 연락 상대와 방향·시각을 뽑는 데 필요한 열만 다룹니다.

## 먼저 확인할 것

먼저 macOS 버전을 확인합니다. 메시지 데이터베이스는 버전에 따라 열이 있기도 하고 없기도 하고 [1], 통화 기록 모듈이 다루는 버전도 정해져 있어서 [3], 버전을 알아야 어느 열을 읽을 수 있는지가 정해집니다. 버전은 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../../02-artifacts/system-account/os-version-install-history.md)에서 확인합니다.

다음으로 맥에 있는 사용자 계정마다 홈 폴더를 확인합니다. 아래 기록은 대부분 사용자 홈 폴더 아래에 있어서 계정별로 따로 읽고, 결과에 어느 계정의 기록인지 붙입니다. 계정 목록은 [사용자 계정 (Local Accounts)](../../02-artifacts/system-account/user-accounts/index.md)에 있습니다. 시간대는 [시간대와 시계 설정 (Time Zone·NTP)](../../02-artifacts/system-account/time-zone.md)에서 확인하고, 모든 시각을 UTC 로 맞춘 뒤 비교합니다.

설치된 메신저 앱도 미리 확인합니다. 메시지와 통화 말고도 카카오톡·텔레그램·슬랙 같은 앱이 따로 기록을 남기고, 앱마다 읽는 법이 달라 해당 페이지를 따라야 합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `~/Library/Messages/chat.db` | 메시지 본문, 상대 식별자, 방향, 보낸·받은·읽은 시각, 서비스 [1] | [메시지 (iMessage·SMS)](../../02-artifacts/messengers/imessage/index.md) |
| 2 | `~/Library/Messages/Attachments/` | 메시지 첨부 파일 [1] | [메시지 (iMessage·SMS)](../../02-artifacts/messengers/imessage/index.md) |
| 3 | `CallHistory.storedata` 의 `ZCALLRECORD` 표 | 통화 상대, 시각, 통화 시간(초) [3] | [페이스타임과 통화 기록 (FaceTime·CallHistory)](../../02-artifacts/messengers/facetime-callhistory.md) |
| 4 | 메일 데이터베이스 | 메일로 주고받은 상대와 시각 | [애플 메일 (Apple Mail)](../../02-artifacts/mail/apple-mail/index.md), [아웃룩 (Outlook for Mac)](../../02-artifacts/mail/outlook.md), [썬더버드 (Thunderbird)](../../02-artifacts/mail/thunderbird.md) |
| 5 | 제3자 메신저 | 앱별 대화 기록 | [카카오톡 맥 (KakaoTalk)](../../02-artifacts/messengers/kakaotalk.md), [텔레그램 (Telegram)](../../02-artifacts/messengers/telegram.md), [슬랙 (Slack)](../../02-artifacts/messengers/slack.md) 등 |
| 6 | 첨부로 받아 저장한 파일의 격리 속성 | 메시지 첨부인지 메일 첨부인지를 가르는 격리 유형 | [격리 속성과 다운로드 기록 (Quarantine)](../../02-artifacts/filesystem/quarantine/index.md) |
| 7 | 연락처 | 상대 번호·주소를 이름과 맞출 때 | [연락처 (Contacts)](../../02-artifacts/cloud-apps/contacts.md) |

### 메시지 (chat.db)

메시지 기록은 `message`, `message_attachment_join`, `attachment`, `chat_message_join`, `chat`, `handle` 표를 이어서 읽습니다 [1]. 연락 상대와 방향·시각을 뽑는 데 쓰는 열은 아래와 같습니다.

| 표 | 열 [1] | 쓰임 |
|---|---|---|
| `message` | `handle_id` | 상대를 가리키는 값. `handle` 표와 이어 붙임 |
| `message` | `text`, `attributedBody` | 본문 |
| `message` | `is_from_me` | 방향 |
| `message` | `service`, `account`, `destination_caller_id` | 서비스와 어느 계정으로 주고받았는지 |
| `message` | `date`, `date_delivered`, `date_read`, `is_read` | 시각과 읽음 여부 |
| `handle` | `id` | 상대의 식별자 |
| `chat` | `chat_identifier` | 대화방 식별자 |
| `attachment` | `filename`, `transfer_name`, `total_bytes` | 첨부 경로·이름·크기 |

`destination_caller_id` 열은 데이터베이스 버전에 따라 없을 수 있어서, 열이 있을 때만 쿼리에 넣습니다 [1]. `account` 와 `destination_caller_id` 에 어느 계정으로 주고받았는지가 담기지만, 두 열 값의 정확한 뜻은 실제 데이터로 확인해야 합니다.

방향을 읽을 때는 도구가 보여 주는 화살표보다 `is_from_me` 열 값 자체를 봅니다. mac_apt 는 `is_from_me` 가 0 이면 `->`, 1 이면 `<-` 로 바꿔 보여 주는데 [1], 이 화살표는 도구마다 정하는 표시일 뿐이라서 보고서에는 "`is_from_me` 값이 1 인 메시지" 처럼 열 값으로 적고, 같은 데이터에서 방향을 알고 있는 메시지 하나로 값의 뜻을 확인해 둡니다.

`date`, `date_delivered`, `date_read` 는 맥 절대 시각 (Mac Absolute Time)이라 2001-01-01 을 기준으로 바꿉니다 [1][2]. 값의 절댓값이 `0xFFFFFFFF` 보다 크면 나노초로 보고 10^9 로 나눈 뒤 더하고, 그렇지 않으면 초로 봅니다 [2]. 같은 열에 초 단위와 나노초 단위가 섞여 있을 수 있고, 단위가 바뀐 macOS 버전은 알려져 있지 않아서 값 크기로 구분합니다. 나노초 값이라면 아래처럼 바꿉니다.

```sql
-- 명세로 만든 예시 쿼리. date 가 나노초 단위일 때
SELECT datetime(date / 1000000000 + 978307200, 'unixepoch') AS date_utc,
       is_from_me, service, account, handle_id, text
FROM message
ORDER BY date;
```

지운 메시지를 가리키는 표와 그 밖의 구조는 [메시지 (iMessage·SMS)](../../02-artifacts/messengers/imessage/index.md)에 있습니다.

### 통화 기록 (CallHistory.storedata)

통화 기록은 `CallHistory.storedata` 의 `ZCALLRECORD` 표에 있고, 이 구조가 알려진 버전은 iOS 8~14 와 macOS 10.13, 10.14, 10.15, 10.16 입니다 [3]. 그 뒤 버전은 실제 데이터에서 표와 열이 있는지 먼저 봅니다. 파일의 전체 경로는 [페이스타임과 통화 기록 (FaceTime·CallHistory)](../../02-artifacts/messengers/facetime-callhistory.md)에서 확인합니다.

| 열 [3] | 내용 |
|---|---|
| `ZDATE` | 통화 시각. 맥 절대 시각(2001-01-01 기준 초) |
| `ZADDRESS` | 상대 번호·주소 |
| `ZDURATION` | 통화 시간(초) |
| `ZANSWERED`, `ZORIGINATED`, `ZCALLTYPE` | 열 이름으로는 응답·발신·통화 종류. 값의 뜻은 실제 데이터로 확인 |
| `ZSERVICE_PROVIDER` | 서비스 제공자 |
| `ZISO_COUNTRY_CODE`, `ZLOCATION` | 국가 코드, 위치 |
| `ZDISCONNECTED_CAUSE` | 끊긴 원인(macOS 10.13 이상) |

시각은 `DATETIME(ZDATE+978307200,'UNIXEPOCH')` 로 바꿉니다 [3]. `ZCALLTYPE`·`ZORIGINATED`·`ZANSWERED` 값이 수신·발신이나 페이스타임 음성·영상을 어떻게 가르는지와, 버전에 따라 `ZADDRESS` 가 평문인지 암호화된 값인지는 공개된 자료가 없습니다. 그래서 이 세 열은 값을 그대로 적고, 값의 뜻은 같은 데이터에서 알고 있는 통화로 맞춰 본 뒤에만 풀어 씁니다.

## 분석 흐름

1. macOS 버전, 시간대, 사용자 계정 목록을 적고, 계정마다 `~/Library/Messages/` 와 통화 기록 파일, 메일·메신저 데이터 폴더를 확보했는지 확인합니다.
2. `chat.db` 에서 `message`·`handle`·`chat` 을 이어 붙여 메시지마다 상대 식별자, 대화방, `is_from_me`, `service`, 시각을 뽑습니다. 시각은 값 크기로 초인지 나노초인지 먼저 확인합니다.
3. 첨부가 있는 메시지는 `attachment` 의 `filename` 으로 `~/Library/Messages/Attachments/` 아래 파일이 실제로 남아 있는지 확인합니다.
4. `ZCALLRECORD` 에서 통화마다 `ZDATE`, `ZADDRESS`, `ZDURATION` 과 방향·종류 열 값을 뽑습니다.
5. 메일과 제3자 메신저의 기록을 각 페이지의 방법대로 뽑습니다.
6. 상대 식별자(전화번호·이메일 주소·앱 계정)를 한 열로 모아, 같은 사람이 여러 수단에 걸쳐 나타나는지 봅니다. 이름은 연락처와 맞춰 보되, 연락처에 적힌 이름은 사용자가 입력한 값이라는 점을 함께 적습니다.
7. 메시지 첨부나 메일 첨부로 받아 다른 곳에 저장한 파일은 격리 유형(`kLSQuarantineTypeInstantMessageAttachment`, `kLSQuarantineTypeEmailAttachment`)으로 어느 수단에서 왔는지 확인합니다.
8. 모든 기록을 UTC 로 맞춰 한 타임라인에 올리고, 상대별·수단별로 묶어 봅니다. 타임라인은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)을 따릅니다.

> 그림 자리: 상대 한 명을 기준으로 메시지·통화·메일 기록을 시간 축 위에 나란히 올린 타임라인

## 흔한 오판

맥에 있는 메시지를 모두 이 맥에서 주고받았다고 보는 경우가 많습니다. 메시지와 통화 기록은 같은 계정을 쓰는 다른 Apple 기기와 관련될 수 있지만, 어느 기록이 어느 기기에서 생겼는지는 이 데이터베이스만으로 구분하기 어렵습니다. 그래서 "이 맥의 데이터베이스에 기록이 있다" 까지만 말하고, 기기 연결은 [연속성과 유니버설 클립보드 (Continuity·Handoff)](../../02-artifacts/cloud-apps/continuity.md)와 [아이폰·아이패드 연결 (iOS Devices)](../../02-artifacts/external-devices/ios-devices/index.md)에서 따로 확인합니다.

도구 화면의 화살표나 "보냄·받음" 표시를 그대로 옮기는 것도 흔한 실수입니다. 표시 방식은 도구가 정하는 것이라서, 보고서에는 `is_from_me` 처럼 원래 열 값을 함께 적습니다.

`ZDURATION` 이 0 인 통화나 `date_read` 가 비어 있는 메시지를 "통화하지 않았다", "읽지 않았다" 로 단정하지 않습니다. 열 값의 뜻이 모두 밝혀져 있지 않아서 값 그대로 적고, 의미는 다른 기록과 맞춰 본 뒤에 씁니다.

## 보고서 문장 예

- "사용자 계정 A 의 `~/Library/Messages/chat.db` 에 식별자 X 와 주고받은 메시지가 YYYY-MM-DD 부터 YYYY-MM-DD 까지 N건 있으며, 그중 `is_from_me` 값이 1 인 메시지가 N건입니다. 시각은 `date` 열의 맥 절대 시각을 UTC 로 바꾼 값입니다."
- "`CallHistory.storedata` 의 `ZCALLRECORD` 표에 `ZADDRESS` 값이 X 인 통화 기록이 N건 있고, `ZDURATION` 합계는 N초입니다. `ZORIGINATED` 값의 뜻은 이 데이터에서 확인하지 못해 원래 값을 함께 적었습니다."

## 함께 볼 페이지

- [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](user-attribution.md) — 어느 계정으로 보냈는지를 사람과 잇는 방법
- [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../exfiltration/data-exfiltration/index.md) — 첨부로 파일이 나갔는지 볼 때
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md) — 맥 절대 시각과 단위
- [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md) — 데이터베이스를 읽는 법과 지운 레코드

## 참고 문헌

1. mac_apt `plugins/imessage.py` (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/imessage.py
2. mac_apt `plugins/helpers/common.py` (ReadMacAbsoluteTime·ReadAPFSTime·ReadUnixTime) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/helpers/common.py
3. APOLLO 모듈 `call_history.txt` (Sarah Edwards, mac4n6) — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/call_history.txt
