---
title: "누구와 연락을 주고받았나"
parent: "시나리오 · 행위 재구성"
nav_order: 1560
---

# 누구와 연락을 주고받았나 (Communication)

## 조사 질문

"그 사람과 언제부터 연락했나", "사건 전날 밤 누구에게 전화를 걸었고 몇 분 통화했나", "지운 대화가 있다면 적어도 연락한 흔적은 남았나" 같은 질문에 답하는 흐름입니다. 한 사람과 주고받은 연락이 통화 기록, 문자, 메신저, 알림 기록에 따로따로 남기 때문에 이 페이지는 흔적을 어떤 순서로 보고 어떻게 한 표로 합치는지를 다룹니다. 각 흔적의 칸과 구조는 아티팩트 페이지에 있고, 여기서는 질문에 답하는 데 필요한 만큼만 짚습니다.

기록은 "이 번호와 이 시각에 이만큼 통화한 행이 있다" 까지 알려 주지만, 그 번호를 실제로 누가 쓰고 있었는지, 폰을 든 사람이 기기 주인이었는지는 알려 주지 않습니다. 사람을 가리는 문제는 [그 시각에 폰을 쓴 사람이 누구인가](user-attribution.md) 에서 이어 갑니다. 통신사가 가진 통화 내역처럼 기기 밖에 있는 자료는 이 핸드북에서 다루지 않습니다.

## 먼저 확인할 것

- **OS 버전과 제조사** — 삼성 기기는 연락처 제공자의 패키지 이름이 다릅니다. 공개 도구 ALEAPP 는 통화 기록을 `*/com.android.providers.contacts/databases/calllog.db*` 와 `*/com.samsung.android.providers.contacts/databases/calllog.db*` 두 경로에서 찾고, 시험 표본 중 삼성 기기(Galaxy S10 Android 10, Galaxy S20 Android 13, Galaxy A53 Android 14 등)는 모두 삼성 쪽 경로였습니다 [1]. 문자와 메신저도 제조사·앱에 따라 저장 위치가 달라서, 검체의 제조사와 Android 버전, 기본 메시지 앱을 먼저 적어 둡니다.
- **시간대** — 칸마다 시각 단위가 다르고 대부분 UTC 기준의 에포크 값이라, 현지 시각으로 바꾸려면 기기 시간대가 필요합니다([시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md), [시각 값](../../01-foundations/value-decoding/time-values.md)).
- **사용자와 프로필** — 보안 폴더나 작업 프로필 안에서 쓴 앱은 따로 된 사용자 공간에 기록을 남길 수 있습니다([보안 폴더와 작업 프로필](../../01-foundations/security-model/secure-folder-work-profile.md)).
- **수집 범위** — 통화 기록·문자·메신저 DB 는 앱 데이터 영역에 있어 adb 일반 권한으로 보이는 범위에 들어 있지 않습니다. 관찰 기기에서 일반 권한으로 볼 수 있던 것은 `dumpsys` 출력과 설정 키 이름, `/sdcard` 폴더 목록 정도였습니다 (확인 범위: Android 16, One UI 8.5). 어떤 방식으로 무엇까지 확보했는지를 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 기준으로 먼저 정리해 두어야 "기록이 없다" 와 "확보하지 못했다" 를 가를 수 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 통화 기록 `calllog.db` 의 `calls` 표 | 상대 번호, 통화 시각, 통화 길이, 수신·발신·부재중 같은 방향 | [통화 기록](../../02-artifacts/communications/call-log.md) |
| 2 | 문자 `mmssms.db` 와 메시지 앱 DB | SMS·MMS 상대 주소, 보낸 시각·받은 시각, 본문 | [문자](../../02-artifacts/communications/messages/index.md) |
| 3 | 메신저 앱 DB | 대화방, 보낸 사람 ID, 메시지 시각 | [카카오톡](../../02-artifacts/messengers/kakaotalk/index.md) 등 메신저 페이지 |
| 4 | 연락처 `contacts2.db` | 번호에 붙은 이름, 지운 연락처의 흔적 | [연락처](../../02-artifacts/communications/contacts.md) |
| 5 | 알림 기록과 `dumpsys usagestats` 의 알림 이벤트 | 앱 DB 에 본문이 없을 때 남는 알림 제목·본문, 알림이 온 시각 | [알림 기록](../../02-artifacts/app-usage/notification-history.md) |
| 6 | 통화 녹음 폴더와 녹음 설정 | 녹음 파일이 있을 수 있는 자리 | [통화 녹음과 음성 사서함](../../02-artifacts/communications/call-recording-voicemail.md) |

제조사에 따라 달라지는 부분은 아래처럼 나눠 적습니다.

| 기록 | AOSP·구글 기준 | 삼성 One UI | 비고 |
|---|---|---|---|
| 통화 기록 경로 | `com.android.providers.contacts` 아래 `calllog.db` [1] | `com.samsung.android.providers.contacts` 아래 `calllog.db` [1] | ALEAPP 는 두 경로를 같은 SQL 로 읽습니다. 삼성 쪽 표에 전용 칸이 더 있는지는 확인하지 못했습니다 |
| 문자 | `com.android.providers.telephony` 의 `mmssms.db` [3] | 삼성 표본에도 `mmssms.db` 행이 있었습니다 [4] | 삼성 메시지 앱 자체 DB 의 경로와 표는 공개 자료로 확인하지 못했습니다 |
| Google 메시지 앱 | `bugle_db` 를 따로 둡니다 [6] | 삼성 표본(Galaxy A53 Android 14, Galaxy S20 Android 13)에도 `bugle_db` 가 있었습니다 [6] | 기본 메시지 앱이 무엇이냐에 따라 본문이 있는 DB 가 달라집니다 |
| 연락처 | `contacts2.db` | 삼성 기기에서 `contacts2.db` 가 삼성 제공자 아래에 있는지는 확인하지 못했습니다 | 통화 기록 경로에서 미루어 짐작만 할 수 있습니다 |

## 분석 흐름

1. **상대를 번호로 고정합니다.** 조사 대상이 사람 이름으로 주어졌다면 먼저 [연락처](../../02-artifacts/communications/contacts.md) 에서 그 이름에 붙은 번호와 계정을 모두 뽑습니다. 이름은 사용자가 저장한 글자일 뿐이고 번호 하나에 여러 이름이, 이름 하나에 여러 번호가 붙을 수 있어서, 이후 단계는 번호와 메신저 ID 를 기준으로 찾습니다. 연락처를 지운 흔적은 `deleted_contacts` 표에 남지만 이 표에는 `contact_id` 와 삭제 시각 두 칸만 있어 지운 사람의 이름이나 번호는 나오지 않습니다 [7].

2. **통화 기록을 읽습니다.** ALEAPP 는 `calls` 표에서 `date`, `number`, `type`, `duration`, `phone_account_address`, `geocoded_location`, `countryiso`, `transcription`, `deleted` 같은 칸을 읽고, `date` 는 밀리초 값을 UTC 로 바꾸며 `duration` 은 저장된 초 값을 그대로 보여 줍니다 [1]. `type` 값은 아래와 같습니다 [1].

   | 값 | 뜻 |
   |---|---|
   | 1 | 수신 (Incoming) |
   | 2 | 발신 (Outgoing) |
   | 3 | 부재중 (Missed) |
   | 4 | 음성 사서함 (Voicemail) |
   | 5 | 거절 (Rejected) |
   | 6 | 차단 (Blocked) |
   | 7 | 다른 기기에서 받음 (Answered Externally) |

   `deleted` 칸은 ALEAPP 가 값을 그대로 보여 줄 뿐 뜻을 풀지 않아서 [1], 이 칸이 1 인 행을 곧바로 "사용자가 지운 통화" 로 읽지 않습니다. 또 AOSP 기본값으로 통화 기록은 전화 계정마다 500건까지만 남기 때문에 [2], 오래된 기간에 통화가 없다고 해서 통화가 없었다고 결론 내리지 않습니다.

3. **문자를 읽습니다.** `mmssms.db` 한 파일 안에 SMS(`sms` 표)와 MMS(`pdu`·`part`·`addr` 표)가 함께 있고, 두 종류는 `threads` 표의 대화 번호를 같이 씁니다 [3][5]. 방향은 `sms.type` 의 1(받음)·2(보냄) [5], MMS 는 `pdu.msg_box` 의 1(받음)·2(보냄)로 가르고 [5], MMS 상대는 `addr.type` 의 137(보낸 사람)·151(받는 사람)으로 구합니다 [4]. 단위가 서로 다르다는 점이 가장 흔한 함정이라서, `sms.date` 는 유닉스 밀리초이고 `pdu.date` 는 유닉스 초라는 점을 먼저 맞춥니다 [3][4]. 기본 메시지 앱이 Google 메시지라면 `bugle_db` 의 `parts.timestamp`(유닉스 밀리초)도 함께 봅니다 [6].

4. **메신저를 읽습니다.** 메신저는 앱마다 DB 가 다르므로 해당 앱 페이지를 따라갑니다. 예를 들어 카카오톡의 대화 DB 에는 대화 기록 표 `chat_logs` 와 대화방 표 `chat_rooms` 가 있고, 파일 전체가 아니라 메시지 본문 같은 일부 칸만 암호화돼 있습니다 [8]. 공개 도구도 `-wal`·`-shm`·`-journal` 파일을 본 파일과 함께 꺼내는데 [9], 최근 메시지가 아직 본 파일에 옮겨지지 않고 `-wal` 에만 있을 수 있어서 수집할 때 이 파일들을 빠뜨리지 않습니다. 이 핸드북은 암호화된 칸을 푸는 절차를 다루지 않고, 칸이 암호화돼 있어 그대로는 읽을 수 없다는 사실까지만 적습니다.

5. **알림 흔적으로 빈자리를 메웁니다.** 앱 DB 가 없거나 대화가 지워진 경우에도 알림 기록이 남아 있을 수 있습니다. 알림 기록 파일은 ALEAPP 경로 패턴 `**/system_ce/*/notification_history/history/*` 아래 protobuf 이고 [12], 한 건마다 `package`, `channel_id`, `posted_time_ms`(밀리초), `title`, `text`, `conversation_id` 같은 칸이 있습니다 [11]. 다만 하루치만 남기고(`HISTORY_RETENTION_DAYS = 1`) 20분마다 디스크에 쓰기 때문에 [10] 오래된 사건에는 거의 쓰지 못합니다. 이 기능이 켜져 있었는지는 settings secure 의 `notification_history_enabled` 로 판단하고 [12], 관찰 기기에도 이 키 이름이 있었습니다(값은 가려짐) (확인 범위: Android 16, One UI 8.5).

   `dumpsys usagestats` 에는 알림이 왔다는 사실만 남습니다. 관찰 기기에서는 `type=NOTIFICATION_INTERRUPTION ... channelId=CHANNEL_ID_SMS_MMS` 줄이 2번 나왔는데, 채널 이름으로 문자 알림이 왔다는 것은 볼 수 있지만 상대방과 본문은 이 줄에 없습니다 (확인 범위: Android 16, One UI 8.5). `dumpsys notification` 에는 지금 떠 있는 알림의 `android.title`·`android.text` 칸이 보였고, 관찰 메모에서는 값 대신 `[length=##]` 로 가려져 있었습니다 (확인 범위: Android 16, One UI 8.5).

6. **통화 녹음이 있는지 봅니다.** 관찰 기기의 `/sdcard` 최상위에는 `Recordings` 폴더가 있었고, settings system 에는 `record_calls_automatically_on_off`, `record_calls_automatically_type`, `record_call_storage_setting_value` 같은 통화 녹음 설정 키 이름이 있었습니다 (확인 범위: Android 16, One UI 8.5). 폴더 안의 내용과 키 값의 뜻, 삼성 통화 녹음 파일의 이름 규칙은 확인하지 못했으므로, 녹음 파일을 찾았다면 파일 자체의 메타데이터와 통화 기록 시각을 나란히 놓아 맞춰 봅니다. 관찰 기기의 `dumpsys batterystats` 에는 `+audio`·`-audio` 줄도 있었지만, 오디오를 쓴 구간일 뿐 그것이 통화였는지는 이 줄만으로 알 수 없습니다 (확인 범위: Android 16, One UI 8.5).

7. **한 표로 합칩니다.** 통화·문자·메신저·알림을 상대 번호(또는 ID)와 시각 기준으로 한 표에 모읍니다. 이때 `calls.date`·`sms.date`·알림의 `posted_time_ms` 는 밀리초이고 `pdu.date` 는 초라서 단위를 먼저 맞추고, 칸마다 출처 파일과 원래 값을 함께 남깁니다. 여러 기록을 한 시간 축에 놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

> 그림 자리: 가로 시간 축 위에 통화(막대, 길이 = 통화 시간), 문자(점), 메신저(점), 알림(세모)을 상대별 줄로 나눠 찍은 그림

## 흔한 오판

**통화 기록의 이름 칸을 상대의 신원으로 읽는 오판**이 흔합니다. 이름은 기기에 저장된 연락처에서 온 글자이고, 번호의 실제 사용자가 누구인지는 기기 밖 자료로 확인해야 합니다.

**부재중(3)이나 거절(5)을 "통화했다" 로 세는 경우**도 있습니다. 방향 값은 반드시 풀어서 적고, 통화 길이 0초인 행을 따로 셉니다.

**MMS 시각을 밀리초로 읽는 실수**도 자주 나옵니다. `pdu.date` 를 밀리초로 읽으면 1970년 1월로 나오므로, 이런 값이 보이면 단위를 먼저 의심합니다 [3].

**기록이 없는 기간을 "연락이 없었다" 로 단정하는 것**도 조심합니다. 통화 기록은 계정마다 500건 한도가 있고 [2], 알림 기록은 하루치뿐이며 [10], 메신저 대화는 사용자가 지우거나 앱을 다시 깔면 사라질 수 있습니다. 지운 기록을 찾는 흐름은 [지운 대화와 사진 찾기](deleted-content.md) 에 있습니다.

**알림 이벤트를 메시지 본문의 증거로 쓰는 경우**도 있습니다. `NOTIFICATION_INTERRUPTION` 줄에는 앱과 채널만 있고 상대와 내용은 없습니다 (확인 범위: Android 16, One UI 8.5).

## 보고서 문장 예

기록이 말하는 만큼만 적고, 기록마다 출처 파일과 원래 값을 밝힙니다.

| 쓰지 않을 문장 | 쓸 문장 |
|---|---|
| 피의자는 ○○에게 전화를 걸어 5분간 통화했다. | 통화 기록(`calllog.db` 의 `calls` 표)에 ○○일 ○○:○○(UTC ○○:○○) 번호 ○○○ 로 향한 발신(type 2) 행이 있고, 통화 길이 칸 값은 300초입니다. |
| 두 사람은 그날 문자를 주고받지 않았다. | 확보한 `mmssms.db` 에서 ○○일에 번호 ○○○ 와 주고받은 SMS·MMS 행은 찾지 못했습니다. 이 기기의 기본 메시지 앱과 그 앱의 DB 는 ○○ 이유로 확보하지 못했습니다. |
| 피의자는 ○○에게서 문자를 받았다. | 알림 기록에 ○○일 ○○:○○ 메시지 앱이 올린 알림이 있고, 제목 칸은 "○○", 본문 칸은 "○○" 입니다. 이 기록은 알림이 올라왔다는 사실을 보여 주며, 사용자가 이 알림을 읽었는지는 담지 않습니다. |

보고서 전체의 틀은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 아티팩트 본문: [통화 기록](../../02-artifacts/communications/call-log.md), [문자](../../02-artifacts/communications/messages/index.md), [연락처](../../02-artifacts/communications/contacts.md), [통화 녹음과 음성 사서함](../../02-artifacts/communications/call-recording-voicemail.md), [알림 기록](../../02-artifacts/app-usage/notification-history.md)
- 메신저: [카카오톡](../../02-artifacts/messengers/kakaotalk/index.md), [텔레그램](../../02-artifacts/messengers/telegram.md), [왓츠앱](../../02-artifacts/messengers/whatsapp.md), [시그널](../../02-artifacts/messengers/signal.md)
- 이어지는 시나리오: [지운 대화와 사진 찾기](deleted-content.md), [그 시각에 폰을 쓴 사람이 누구인가](user-attribution.md)
- 기법: [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md), [타임라인 작성](../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. ALEAPP, scripts/artifacts/calllog.py (main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/calllog.py
2. CallLog.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/provider/CallLog.java
3. AOSP packages/providers/TelephonyProvider, MmsSmsDatabaseHelper.java (main) — https://android.googlesource.com/platform/packages/providers/TelephonyProvider/+/refs/heads/main/src/com/android/providers/telephony/MmsSmsDatabaseHelper.java
4. ALEAPP, scripts/artifacts/smsmms.py (main) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/smsmms.py
5. AOSP frameworks/base, core/java/android/provider/Telephony.java (main) — https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/provider/Telephony.java
6. ALEAPP, scripts/artifacts/googleMessages.py (main) — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/googleMessages.py
7. DeletedContactsTableUtil.java — AOSP ContactsProvider (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_packages_providers_contactsprovider/main/src/com/android/providers/contacts/database/DeletedContactsTableUtil.java
8. jiru/kakaodecrypt — kakaodecrypt.py — https://github.com/jiru/kakaodecrypt/blob/HEAD/kakaodecrypt.py
9. dfrc-korea/carpe — modules/kakaotalk_mobile_decrypt_connector.py — https://github.com/dfrc-korea/carpe/blob/HEAD/modules/kakaotalk_mobile_decrypt_connector.py
10. NotificationHistoryDatabase.java — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/notification/NotificationHistoryDatabase.java
11. notificationhistory.proto — AOSP frameworks/base (GitHub 미러, main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/proto/android/server/notificationhistory.proto
12. ALEAPP, scripts/artifacts/notificationHistory.py (main) — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/notificationHistory.py
