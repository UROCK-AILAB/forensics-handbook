---
title: "메신저로"
parent: "자료를 밖으로 보냈나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 1700
---

# 메신저로 (Messenger)

메신저 앱으로 파일이나 글을 밖으로 보냈는지 확인하는 순서를 정리합니다. 메신저마다 DB 가 따로 있어서 앱을 먼저 정하고, 그 앱의 DB 에서 보낸 쪽 메시지와 첨부를 골라내는 흐름으로 봅니다. 공개 도구 ALEAPP 의 모듈이 읽는 방식을 근거로 삼았습니다. 유출 경로 전체의 길잡이는 [자료를 밖으로 보냈나 (Data Exfiltration)](index.md) 허브에 있습니다.

## 조사 질문

이 기기의 메신저로 문제의 파일이나 내용을 보냈는지, 보냈다면 언제 어느 대화방(상대)에 무엇을 보냈는지 묻습니다. 메신저 기록은 "보냈다"는 방향 값과 첨부 파일 경로를 함께 남기는 경우가 많아서, 다른 유출 경로보다 보낸 쪽을 직접 가려낼 가능성이 높습니다. 다만 이렇게 볼 수 있는 것은 수집본에 앱 데이터 폴더가 들어 있을 때뿐입니다.

## 먼저 확인할 것

메신저 DB 는 앱 데이터 폴더 안에 있습니다. 수집 방법에 따라 이 폴더가 수집본에 없을 수 있으니, 분석을 시작하기 전에 대상 앱의 데이터 폴더가 들어 있는지부터 봅니다. 실제 폰에서 adb 일반 셸 권한으로 읽어 본 범위는 dumpsys 출력, 설정 키, /sdcard 폴더 목록이었고 앱 데이터 폴더의 내용은 없었습니다. 폴더 구조는 [앱 데이터 폴더 구조 (/data/data·/data/user)](../../../01-foundations/storage/app-data-layout.md)에, 수집 방법별 차이는 [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md)에 있습니다.

그다음 어떤 메신저가 설치돼 있었는지와 지금도 남아 있는지를 [설치된 앱 (packages.xml)](../../../02-artifacts/app-usage/packages/index.md)에서 확인합니다. 실제 폰에서는 시스템 앱 486개, 사용자가 설치한 앱 168개가 있었습니다. 앱이 여러 개면 조사 기간에 앞에 띄운 앱부터 좁힙니다.

메신저 DB 의 시각은 대부분 유닉스 밀리초라서, 보고서에 현지 시각으로 옮기려면 기기의 시간대를 알아야 합니다. 값 읽는 법은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../../01-foundations/value-decoding/time-values.md)에, 기기 시간대는 [시간대와 시각 설정 (Time Zone)](../../../02-artifacts/system-account/time-zone.md)에 있습니다. 보안 폴더나 작업 프로필에 같은 메신저가 따로 깔려 있을 수 있어서 [사용자와 프로필 (Multi-user·users)](../../../02-artifacts/system-account/users-profiles.md)도 함께 봅니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 설치된 앱 | 어떤 메신저가 있었는지, 지워졌는지 | [설치된 앱](../../../02-artifacts/app-usage/packages/index.md) |
| 2 | 앱 사용 기록 | 메신저를 언제 앞에 띄웠는지 | [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md) |
| 3 | 메신저 DB | 보낸 메시지, 첨부 경로·크기, 상대 | 아래 절과 앱별 페이지 |
| 4 | 공용 저장 공간의 첨부 폴더 | 보낸 파일의 실물 | [공용 저장 공간 (Shared Storage·/sdcard)](../../../01-foundations/storage/shared-storage.md) |
| 5 | 알림 기록 | 대화가 오간 시각(받은 쪽) | [알림 기록 (Notification History)](../../../02-artifacts/app-usage/notification-history.md) |

## WhatsApp 에서 보낸 것 가려내기

WhatsApp 의 구조 전체는 [왓츠앱 (WhatsApp)](../../../02-artifacts/messengers/whatsapp.md) 페이지에 있고, 여기서는 유출을 따질 때 필요한 연결만 적습니다. 메시지와 통화는 `msgstore.db`, 연락처는 `wa.db` 에 있고, ALEAPP 는 이 파일을 `*/com.whatsapp/databases/msgstore.db*`, `*/com.whatsapp/databases/wa.db*` 패턴으로 찾습니다 [2]. 첨부 파일은 `*/WhatsApp/Media/*` 와 `*/com.whatsapp/files/Media/*` 패턴으로 찾는데, 공용 저장 공간 안의 정확한 전체 경로는 이번에 확인하지 못했습니다 [2].

요즘 스키마에서는 `message` 표의 `from_me` 칸이 방향을 알려 주고, 1 이면 보낸 메시지, 0 이면 받은 메시지입니다 [2]. 첨부는 `message_media` 표에 있고 `message_row_id` 로 `message._id` 와 이어지며, 이 표의 `file_path` 와 `file_size` 가 기기 안의 파일 위치와 크기를 알려 줍니다 [2]. 상대는 `message.chat_row_id` 에서 `chat._id` 로, `chat.jid_row_id` 에서 `jid._id` 로 따라가 `jid.raw_string` 을 얻고, 이 값을 `wa.db` 의 `wa_contacts.jid` 와 맞춰 연락처 이름을 붙입니다 [2]. ALEAPP 는 `message.recipient_count` 가 0 이면 1:1 대화, 1 이상이면 그룹 대화로 나눕니다 [2].

아래는 ALEAPP 가 쓰는 연결 방식을 따라 만든 예시 질의로, 보낸 메시지 가운데 첨부가 있는 것만 뽑습니다.

```sql
SELECT m._id, m.timestamp, m.message_type, m.recipient_count,
       mm.file_path, mm.file_size, j.raw_string AS chat_jid
FROM message m
JOIN message_media mm ON mm.message_row_id = m._id
LEFT JOIN chat c ON c._id = m.chat_row_id
LEFT JOIN jid j ON j._id = c.jid_row_id
WHERE m.from_me = 1
ORDER BY m.timestamp;
```

`message_type` 값은 ALEAPP 가 다음처럼 풀어 씁니다 [2]. WhatsApp 공식 문서로 확인한 값이 아니라서 보고서에는 "ALEAPP 해석 기준" 이라고 밝힙니다.

| 값 | ALEAPP 해석 |
|---|---|
| 0 | 글 |
| 1 | 사진 |
| 2 | 음성 |
| 3 | 동영상 |
| 5 | 위치 |
| 7 | 시스템 메시지 |
| 9 | 문서 |
| 16 | 실시간 위치 |

`timestamp` 와 `received_timestamp` 는 둘 다 유닉스 밀리초이고, 0 이면 값이 비어 있다는 뜻입니다 [2]. 예전 스키마에서는 `messages` 표 하나에 `key_from_me`(0 받음, 1 보냄), `key_remote_jid`, `remote_resource`, `data`, `media_url`, `received_timestamp` 같은 칸이 들어 있어서, 요즘 스키마의 표가 없으면 이쪽을 찾습니다 [2]. 통화는 `call_log` 표의 `from_me`, `timestamp`(밀리초), `duration` 으로 봅니다 [2]. ALEAPP 시험 이미지에는 Android 14 이미지(sharon_a14)가 들어 있지만, 이 스키마가 모든 버전에서 같다는 보증은 아닙니다 [2].

## 다른 메신저

ALEAPP 에는 telegramAndroid.py, signalAndroid.py, line.py, weChat.py, googleChat.py, googleMessages.py, discordChats.py, FacebookMessenger.py, Viber.py, Threema.py, kikMessenger.py 모듈이 있습니다 [1]. 이 페이지를 쓰면서 모듈 안의 표·칸 이름은 열어 보지 않았으니, 앱별 구조는 [텔레그램 (Telegram)](../../../02-artifacts/messengers/telegram.md), [시그널 (Signal)](../../../02-artifacts/messengers/signal.md), [라인 (LINE)](../../../02-artifacts/messengers/line.md), [위챗 (WeChat)](../../../02-artifacts/messengers/wechat.md), [디스코드 (Discord)](../../../02-artifacts/messengers/discord.md), [페이스북 메신저 (Messenger)](../../../02-artifacts/messengers/facebook-messenger.md) 페이지에서 확인합니다. 어느 앱이든 확인할 점은 같아서, 보낸 방향을 나타내는 칸, 첨부 파일 경로 칸, 대화방과 상대를 잇는 열쇠를 찾습니다.

카카오톡 전용 모듈은 ALEAPP 목록에 없습니다 [1]. 카카오톡의 경로와 대화 DB 는 [카카오톡 (KakaoTalk)](../../../02-artifacts/messengers/kakaotalk/index.md) 페이지에서 다룹니다.

## 알림과 앱 사용 기록으로 보강하기

메신저 DB 를 얻지 못했거나 DB 의 시각을 다른 기록과 맞춰 보고 싶을 때는 시스템 쪽 기록을 씁니다. `dumpsys notification` 에는 알림마다 `NotificationRecord(pkg=..., user=..., id=..., key=...)` 줄과 `channel=`, `when=`, `seen=` 칸이 나왔고, `dumpsys usagestats` 에는 channelId 가 붙은 NOTIFICATION_INTERRUPTION 과 NOTIFICATION_SEEN 이벤트가 나왔습니다. 알림은 메시지를 받은 쪽의 흔적이라서 대화가 오간 시각대를 알려 주지만, 이 기기에서 무엇을 보냈는지까지 보여 주는지는 확인하지 못했습니다.

사용자가 공유 창에서 어느 메신저를 골랐는지 남는 기록은 이번 자료에서 찾지 못했습니다. system 설정 표에 `direct_share` 키가 있었으나 뜻은 확인하지 못했습니다.

## 분석 흐름

1. 수집본에 대상 메신저의 앱 데이터 폴더가 들어 있는지 확인합니다.
2. 설치된 앱 목록과 usagestats 로 조사 기간에 쓴 메신저를 좁힙니다.
3. 메신저 DB 에서 보낸 방향의 메시지만 골라, 첨부 파일 경로·크기·대화방·시각을 뽑습니다.
4. 첨부 경로의 파일이 공용 저장 공간에 남아 있는지 보고, 문제의 파일과 크기·해시를 맞춰 봅니다.
5. 대화방의 상대를 연락처 DB 로 풀고, 1:1 인지 그룹인지 적습니다.
6. 메시지 시각을 usagestats 의 ACTIVITY_RESUMED·ACTIVITY_PAUSED 구간과 알림 시각에 맞춰, 그 시각에 앱을 앞에 띄워 쓰고 있었는지 확인합니다.

## 흔한 오판

첨부 파일이 공용 저장 공간에 있다는 사실만으로 보냈다고 보지 않습니다. 받은 첨부도 같은 폴더에 쌓일 수 있어서, 방향은 DB 의 `from_me` 같은 칸으로 판단합니다. 반대로 첨부 파일이 지워졌어도 DB 의 `file_path`·`file_size` 행은 남아 있을 수 있습니다.

`message_type` 숫자의 뜻을 공식 값처럼 적지 않습니다. 위 표는 ALEAPP 의 해석이고, 앱 판이 바뀌면 달라질 수 있습니다. 그룹 대화로 보낸 메시지는 받은 사람이 여럿일 수 있어서, 보고서에는 받은 사람을 대화방 단위로 적습니다.

`timestamp` 가 0 인 행을 1970년 1월 1일에 보낸 메시지로 읽지 않습니다. 0 은 값이 비어 있다는 뜻입니다 [2].

## 보고서 문장 예

- "WhatsApp `msgstore.db` 의 `message` 표에 `from_me` 값이 1 인 행이 있고, 이 행과 이어진 `message_media` 행의 `file_path` 가 문제의 파일 이름과 같으며 `file_size` 가 문제의 파일 크기와 같습니다. 이 행의 `timestamp` 는 (현지 시각)에 해당합니다."
- "이 기록은 해당 대화방으로 첨부를 보낸 기록이 앱 DB 에 있다는 뜻이며, 상대 기기에서 파일을 받아 열었는지는 이 기기의 기록으로 알 수 없습니다."

## 함께 볼 페이지

- [누구와 연락을 주고받았나 (Communication)](../../activity/communication.md)
- [어떤 앱을 언제 썼나 (App Usage)](../../activity/app-usage.md)
- [지운 대화와 사진 찾기 (Deleted Content)](../../activity/deleted-content.md)
- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)
- 같은 허브의 다른 경로: [클라우드로 (Cloud)](cloud.md), [메일로 (Email)](email.md), [PC 연결로 (USB·PC)](usb-pc.md), [근거리 공유로 (Quick Share·Bluetooth)](nearby-share.md)

## 참고 문헌

1. ALEAPP scripts/artifacts 폴더 목록 — GitHub API, https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
2. WhatsApp.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/WhatsApp.py
