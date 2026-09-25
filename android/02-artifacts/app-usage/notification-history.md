---
title: "알림 기록"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 520
---

# 알림 기록 (Notification History)

## 한 줄 요약

알림 기록 (Notification History) 은 기기에 올라온 알림의 앱 이름·채널·제목·본문·게시 시각을 프로토콜 버퍼 파일로 남기는 시스템 기록이고 [1][2], 하루치만 보관하지만 [1] 메신저 앱에서 지운 메시지의 앞부분이 알림 본문으로 남아 있을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

사용자가 설정에서 알림 기록을 켜 두면, 시스템은 이미 지나간 알림을 다시 볼 수 있도록 알림 내용을 파일에 적어 둡니다. 알림 기록이 켜져 있는지는 설정 값 `notification_history_enabled` 로 판단하고, ALEAPP 는 사용자별 `settings_secure.xml` 에서 이 값을 읽습니다 [3]. 관찰 기기의 settings secure 키 목록에도 `notification_history_enabled` 가 있었고 값은 가려져 있었습니다. 설정 파일을 읽는 법은 [설정 값](../system-account/settings.md) 페이지에 있습니다.

기록에는 알림마다 패키지, 채널, UID, 사용자 번호, 게시 시각, 제목, 본문, 아이콘 정보가 들어갑니다 [2]. 메신저 알림이라면 본문에 메시지 앞부분이 들어가기 때문에, 앱 DB 에서 메시지를 지운 뒤에도 알림 기록에는 남아 있을 수 있습니다.

## 위치와 버전별 차이

ALEAPP 는 아래 경로 패턴으로 기록 파일을 찾습니다 [3].

```
**/system_ce/*/notification_history/history/*
```

`system_ce` 다음 칸은 사용자 번호이고, 기준 디렉터리 `/data/system_ce/<사용자>/notification_history` 라는 전체 경로는 ALEAPP 경로 패턴으로만 확인했습니다 [3]. AOSP 코드에서는 기준 디렉터리 아래 `history` 디렉터리에 기록 파일을 두고, 같은 기준 디렉터리에 `version` 파일을 둡니다 [1].

| 파일 | 뜻 |
|---|---|
| `history/<밀리초 숫자>` | 기록 파일 하나. 이름이 그 파일의 시각 |
| `version` | 버전 파일(내용은 확인하지 못함) |
| `*.new`, `*.bak` | AtomicFile 이 쓰는 도중에 만든 임시 파일 |

기록 파일 이름은 밀리초 시각 숫자이고, 시스템은 최신 파일부터 오래된 파일 순으로 정렬해 다룹니다 [1]. 이름을 숫자로 읽지 못하는 파일은 `INVALID_FILE_TIME_MS = -1` 로 두고 정리 대상에 넣습니다 [1].

다시 알림(스누즈)으로 미뤄 둔 알림은 이 파일이 아니라 `**/system/notification_policy.xml` 에 따로 있고, ALEAPP 는 여기서 Reminder Time 과 Snoozed Notification 을 읽습니다 [3].

| 기기 | 확인한 것 |
|---|---|
| AOSP | 파일 위치 규칙, 보관 기간, 쓰기 주기, proto 구조(현행 소스 기준) [1][2] |
| 삼성 One UI | 설정 키 `notification_history_enabled` 의 존재만 확인. 삼성의 알림 기록 화면이 AOSP 저장소를 그대로 쓰는지는 확인하지 못함 |

기술 매체는 이 기능이 Android 11 에서 들어왔고 기본으로 꺼져 있다고 소개합니다 [4]. 공식 문서로는 확인하지 못했으니, 검체에서는 `notification_history_enabled` 값을 직접 읽어 판단합니다.

## 구조

### 보관과 쓰기 시점

AOSP 코드의 상수 두 개가 이 기록의 성격을 정합니다 [1].

| 상수 | 값 | 뜻 |
|---|---|---|
| `HISTORY_RETENTION_DAYS` | 1 | 하루치만 남기고 그보다 오래된 기록은 지움 |
| `WRITE_BUFFER_INTERVAL_MS` | `1000 * 60 * 20` | 첫 알림이 들어온 뒤 20분마다 버퍼를 디스크에 씀 |

디스크에 쓰기 전 20분 동안의 알림은 메모리에만 있다가 다음 쓰기 때 파일로 갑니다 [1]. 기기를 강제로 끄거나 전원을 끊은 경우 마지막 버퍼가 파일에 남았는지는 확인하지 못했습니다.

### 파일 형식

파일은 프로토콜 버퍼(protobuf)로 쓰고 [1], 최상위 메시지 짜임은 아래와 같습니다 [2]. 프로토콜 버퍼 인코딩 자체는 [프로토콜 버퍼 (Protocol Buffers)](../../01-foundations/data-formats/protobuf.md) 페이지에서 다룹니다.

| 메시지 | 필드(번호) |
|---|---|
| `NotificationHistoryProto` | `string_pool`(1), `major_version`(2), `notification`(3, 반복) |
| `StringPool` | `size`(1), `strings`(2, 반복) |
| `Notification` | `package`(1), `package_index`(2), `channel_name`(3), `channel_name_index`(4), `channel_id`(5), `channel_id_index`(6), `uid`(7), `user_id`(8), `posted_time_ms`(9, int64), `title`(10), `text`(11), `icon`(12), `conversation_id`(13), `conversation_id_index`(14) |
| `Icon` | `image_type`, `image_bitmap_filename`, `image_resource_id`, `image_resource_id_package`, `image_data`, `image_data_length`, `image_data_offset`, `image_uri` |

패키지·채널 이름·채널 ID·대화 ID 는 문자열을 직접 넣는 필드와 `*_index` 필드가 짝을 이루고, `*_index` 값은 파일 앞 문자열 풀(`string_pool`)의 위치에 1을 더한 수입니다 [2]. 실제 파일이 어느 쪽 필드를 채우는지는 확인하지 못했으니 두 쪽 모두 읽어야 합니다.

## 증거로서 의미

**증명하는 것**

기록 한 건은 그 게시 시각에 해당 앱이 해당 제목과 본문으로 알림을 올렸다는 기록입니다. 메신저 알림이면 보낸 사람 이름(제목)과 메시지 앞부분(본문)이 남을 수 있어서, 앱 DB 에서 지운 메시지가 이 시간대에 도착했다는 근거가 될 수 있습니다. 스미싱 문자나 악성 앱이 띄운 알림도 같은 방식으로 남으니 [스미싱 흔적 (Smishing)](../../04-scenarios/incident/smishing.md) 조사에서도 봅니다.

**증명하지 못하는 것**

알림이 올라왔다는 기록은 사용자가 그 알림을 읽었다는 뜻이 아닙니다. 사용자가 알림을 봤는지는 usagestats 의 NOTIFICATION_SEEN 같은 다른 이벤트로 따로 확인해야 합니다. 본문은 앱이 알림에 넣은 문자열일 뿐이라 메시지 전체가 아닐 수 있고, 앱이 알림 본문을 가리거나 요약하면 원래 내용과 다릅니다. 알림 기록이 비어 있다고 해서 알림이 없었다고 말할 수도 없는데, 기능이 꺼져 있었거나 하루가 지나 지워졌을 수 있기 때문입니다.

## 시각 해석

`posted_time_ms` 는 알림이 올라온 시각이고 밀리초 단위이며, ALEAPP 는 1000 으로 나눠 UTC 로 바꿉니다 [2][3]. 기록 파일 이름도 밀리초 시각 숫자입니다 [1]. 파일 이름 시각이 파일을 만든 시각인지, 안에 든 알림의 시각과 어떻게 맞물리는지는 확인하지 못했으니 알림 한 건의 시각은 반드시 `posted_time_ms` 에서 읽습니다. 현지 시각으로 옮길 때는 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 을 확인하고, 값 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

## 함정과 한계

첫째, 보관 기간이 하루라서 [1] 압수 뒤 기기를 켜 둔 채 하루가 지나면 사건 시각의 알림이 스스로 지워질 수 있습니다. 알림 기록이 중요한 사건이면 수집을 서두르고, 수집 전에 기기가 켜져 있던 시간을 기록해 둡니다. 증거 확보 순서는 [모바일 증거 확보 (Acquisition)](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

둘째, 20분 쓰기 주기 때문에 [1] 가장 최근 알림은 파일에 아직 없을 수 있습니다. 라이브 기기라면 `dumpsys notification` 으로 지금 떠 있는 알림을 따로 남깁니다.

셋째, 지워진 기록 파일이나 `.new`·`.bak` 임시 파일에 더 오래된 알림이 남아 있을 수 있습니다. 파일 시스템 수준 복구는 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

넷째, 삼성 One UI 가 AOSP 와 같은 파일을 쓰는지 확인하지 못했으니, 삼성 검체에서 파일이 없으면 기능이 꺼져 있었는지와 경로가 다른지를 모두 따집니다.

## 라이브 기기에서 보이는 모양 (dumpsys notification)

`dumpsys notification` 은 파일에 저장된 기록이 아니라 지금 떠 있는 알림(`NotificationRecord`)을 보여 줍니다. 관찰 기기에서 본 칸은 다음과 같습니다.

| 묶음 | 칸 |
|---|---|
| 앱·사용자 | `pkg=`, `user=`, `uid=`, `userId=`, `opPkg=` |
| 알림 식별 | `id=`, `tag=`, `key=`, `groupKey=` |
| 상태 | `importance=`, `flags=`, `seen=` |
| 내용 | `extras` 안의 `android.title=`, `android.text=` (값 대신 `[length=##]` 로 표시) |
| 반응 통계 | `stats=` 안의 `posttimeToFirstClickMs`, `posttimeToDismissMs`, `airtimeCount`, `airtimeMs` 등 |
| 시각 | `when=`, `mRankingTimeMs=`, `mCreationTimeMs=`, `mVisibleSinceMs=`, `mUpdateTimeMs=` |

관찰 기기 출력에서 제목과 본문은 실제 글자 대신 `[length=##]` 처럼 길이만 찍혔습니다. 이 출력에 알림 기록 파일의 내용이 함께 나오는지는 관찰 메모에 없어서 확인하지 못했습니다. dumpsys 전반은 [dumpsys 출력 (dumpsys)](../logs/dumpsys.md) 페이지에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 35바이트는 위 proto 구조로 만든 예시이고 실제 검체에서 나온 값이 아닙니다. 알림 한 건에 패키지 이름, UID, 게시 시각, 제목만 넣었습니다.

```
10 01 1a 1f 0a 0f 63 6f 6d 2e 65 78 61 6d 70 6c
65 2e 61 70 70 38 8b 4f 48 80 d0 95 ff bc 31 52
02 48 69
```

| 바이트 | 뜻 |
|---|---|
| `10 01` | 필드 2(`major_version`), varint, 값 1 |
| `1a 1f` | 필드 3(`notification`), 길이 구분, 뒤 31바이트가 알림 한 건 |
| `0a 0f` + 15바이트 | 필드 1(`package`), 문자열 `com.example.app` |
| `38 8b 4f` | 필드 7(`uid`), varint, 값 10123 |
| `48 80 d0 95 ff bc 31` | 필드 9(`posted_time_ms`), varint, 값 1700000000000 |
| `52 02 48 69` | 필드 10(`title`), 문자열 `Hi` |

필드 머리 바이트는 필드 번호를 왼쪽으로 3비트 밀고 값 종류(varint 0, 길이 구분 2)를 더한 값이라서 필드 9 는 `0x48`, 필드 10 은 `0x52` 가 됩니다. 게시 시각 1700000000000 을 1000 으로 나누면 유닉스 초 1700000000 이고 UTC 로 2023-11-14 22:13:20 입니다. 실제 파일에서는 필드 3 이 알림 수만큼 되풀이되고, 문자열 대신 `*_index` 필드가 나오면 앞의 문자열 풀에서 해당 순번의 문자열을 찾습니다.

### 공개 도구로 한 번

ALEAPP 의 notificationHistory 모듈이 기록 파일을 풀어 알림 목록을 만들고, 켜짐 설정과 스누즈 알림도 함께 보여 줍니다 [3]. 스키마 없이 `protoc --decode_raw` 로 한 파일을 풀어 필드 번호별 값이 도구 결과와 같은지 몇 건 맞춰 봅니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [앱 사용 기록 (usagestats)](usagestats/index.md) | 같은 시각의 NOTIFICATION_INTERRUPTION(`channelId=` 포함)과 NOTIFICATION_SEEN |
| [디지털 웰빙 (Digital Wellbeing)](digital-wellbeing.md) | NOTIFICATION_INTERRUPTION 이벤트 시각 |
| [문자 (SMS·MMS·RCS)](../communications/messages/index.md) | 문자 알림 본문과 문자 DB 의 메시지가 맞는지 |
| [카카오톡 (KakaoTalk)](../messengers/kakaotalk/index.md) 등 메신저 | 알림 본문에만 있고 앱 DB 에는 없는 메시지가 있는지 |

관찰 기기의 usagestats 에는 NOTIFICATION_INTERRUPTION(`channelId=` 칸 포함)과 NOTIFICATION_SEEN 이벤트가 있어서, 알림 기록 파일이 없을 때 어느 앱의 알림이 언제 울렸는지를 보조로 알려 줍니다. 대화 상대를 재구성하는 흐름은 [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md) 와 [지운 대화와 사진 찾기 (Deleted Content)](../../04-scenarios/activity/deleted-content.md) 에서 다룹니다.

## 실습

공개 안드로이드 검체(NIST CFReDS 등)의 `/data/system_ce/` 아래에 `notification_history` 폴더가 있으면 아래 질문을 풀어 봅니다.

1. `history` 폴더의 파일은 몇 개이고, 파일 이름 숫자를 UTC 로 바꾸면 언제입니까?
2. 가장 이른 `posted_time_ms` 와 가장 늦은 값의 차이가 하루 안쪽입니까?
3. 메신저 앱 알림 가운데 앱 DB 에서 찾을 수 없는 본문이 있습니까?
4. `settings_secure.xml` 의 `notification_history_enabled` 값은 무엇입니까?

## 참고 문헌

1. AOSP frameworks/base — NotificationHistoryDatabase.java — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/notification/NotificationHistoryDatabase.java
2. AOSP frameworks/base — notificationhistory.proto — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/proto/android/server/notificationhistory.proto
3. ALEAPP — scripts/artifacts/notificationHistory.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/notificationHistory.py
4. How-To Geek — How to See Your Notification History in Android — https://www.howtogeek.com/689683/how-to-see-your-notification-history-in-android/
