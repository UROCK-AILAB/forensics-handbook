---
title: "시각 정규화"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 1280
---

# 시각 정규화 (Time Normalization)

아이폰의 여러 기록에 흩어진 시각 값을 같은 기준점과 단위, 같은 시간대로 바꿔서 한 줄에 세울 수 있게 만드는 작업입니다.

## 언제 쓰나

타임라인에 넣을 기록은 SQLite 칸, plist 키, 로그 줄처럼 모양이 제각각이고, 한 DB 안에서도 단위가 다를 수 있습니다. 서로 다른 기록을 나란히 놓거나 [여러 기록 엮기 (Correlation)](correlation.md)로 넘어가기 전에 이 단계를 먼저 거칩니다. Mac 절대 시각이나 Unix 시각 같은 값 형식 자체는 [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md)에서 설명하고, 이 페이지는 그 값을 타임라인에 맞게 바꾸는 순서와 아이폰에서 특히 조심할 곳을 다룹니다.

## 기준점과 단위

Apple 의 Core Foundation 은 참조 시각인 2001-01-01 00:00:00 GMT 부터 센 초로 시각을 다루고, 이 값을 CFAbsoluteTime 이라고 부릅니다. 형식이 double 이라 소수점 아래 값이 붙을 수 있고, 양수는 참조 시각 이후를, 음수는 그 이전을 뜻합니다. CFDate 는 이 절대 시각을 감싼 값이라 한번 만들어지면 바뀌지 않습니다 [1]. Unix 시각(1970-01-01 기준)과는 978307200초 차이가 나서, Mac 절대 초에 978307200 을 더하면 Unix 초가 됩니다 [2].

| 모양 | 알아보는 법 | Unix 초로 바꾸는 법 |
|---|---|---|
| Mac 절대 초 | 9자리 정수, 또는 소수점이 붙은 double | 값 + 978307200 |
| Mac 절대 나노초 | 18자리 정수 | 값 ÷ 10^9 + 978307200 |
| 0 | 값이 0 | 바꾸면 2001-01-01 00:00:00 이 되므로 사건 시각으로 옮기지 않고 따로 표시 |

## 절차

1. **시각 칸과 키를 목록으로 적습니다.** 기록마다 파일(백업 도메인과 경로), 표나 키 이름, 저장된 형을 한 줄씩 적어 두면 나중에 어떤 값을 어떻게 바꿨는지 되짚을 수 있습니다.
2. **저장된 형을 확인합니다.** plist 에서 `datetime` 형은 plist 의 날짜 형식이라 도구가 날짜로 풀어 보여 주지만, `float` 형은 숫자만 들어 있어 기준점을 따로 확인해야 합니다. 예를 들어 `com.apple.ScreenTimeAgent.plist` 의 `UsageGenesisDate` 는 `datetime` 형이고, `com.apple.AppStore.plist` 의 `lastBootstrapDate` 는 `float` 형입니다(확인 범위: iPhone 13 mini, iOS 27.0). `lastBootstrapDate` 가 Mac 절대 초인지는 확인하지 못했으므로, 기준점을 모르는 숫자는 바꾸지 않고 원래 값으로 남겨 둡니다. plist 형식은 [속성 목록 파일 (plist·NSKeyedArchiver)](../../../01-foundations/data-formats/plist.md)에 있습니다.
3. **자릿수로 단위를 가립니다.** 같은 칸 안에서도 초와 나노초가 섞일 수 있어서(아래 "sms.db 에서 섞이는 단위") 칸 단위가 아니라 행 단위로 판단합니다.
4. **UTC 로 바꾸고 원래 값을 함께 남깁니다.** 변환한 시각 옆에 원래 숫자와 적용한 식을 같이 적어야 다른 분석가가 같은 결과를 다시 만들 수 있습니다.
5. **시간대는 따로 적습니다.** 기록에 시간대 칸이 있으면 그 값을 별도 열로 옮기고, 없으면 시간대를 모른다고 적습니다(아래 "시간대가 함께 남는 곳").
6. **알려진 값으로 변환식을 검산합니다.** 아래 "직접 해 보기" 처럼 손으로 계산한 값과 도구가 보여 주는 값이 같은지 한 번 확인합니다.

## sms.db 에서 섞이는 단위

iOS 11 부터 메시지 DB(`sms.db`)의 시각 칸에 길이가 다른 Mac 절대 값이 섞여 들어가고, 같은 칸 안에서도 섞입니다. 9자리 값은 전통적인 Mac 절대 초이고, 18자리 값은 나노초 단위라서 10^9 로 나눠야 초가 되며, 보낸 메시지에서는 0 이 보이기도 했습니다. 글쓴이는 이 혼재를 `chat` 표와 `chat_message_join` 표에서 봤고, 18자리 값 가운데에는 끝자리가 00 으로 채워지지 않은 것도 있었다고 적었습니다 [2].

같은 글에 실린 변환식은 다음과 같습니다(원문 그대로) [2].

```sql
case when LENGTH(chat_message_join.message_date)=18 then datetime(chat_message_join.message_date/1000000000+978307200,'unixepoch','localtime') when LENGTH(chat_message_join.message_date)=9 then datetime(chat_message_join.message_date +978307200,'unixepoch','localtime') else 'N/A' END
```

이 식은 `'localtime'` 을 붙여서 분석하는 PC 의 시간대로 바꿔 보여 줍니다. 여러 기록을 한 줄에 세울 때는 `'localtime'` 을 빼고 UTC 로 받은 뒤, 기기의 시간대는 5단계처럼 따로 적는 편이 뒤섞이지 않습니다.

iOS 27.0 백업의 `HomeDomain :: Library/SMS/sms.db` 에서는 시각이 들어갈 칸 이름을 다음과 같이 확인했습니다(확인 범위: iPhone 13 mini, iOS 27.0). 값은 읽지 않았으므로 이 버전에서 각 칸이 초인지 나노초인지는 확인하지 못했고, 행마다 자릿수를 보고 판단합니다.

| 표 | 시각 칸 |
|---|---|
| `message` | `date`, `date_read`, `date_delivered`, `date_played`, `time_expressive_send_played` |
| `chat` | `last_read_message_timestamp`, `syndication_date` |
| `chat_message_join` | `message_date` |
| `chat_recoverable_message_join` | `delete_date` |
| `attachment` | `created_date`, `start_date` |

메시지 기록 전체의 해석은 [메시지 (iMessage·SMS)](../../../02-artifacts/communications/messages/index.md)에 있습니다.

## 시간대가 함께 남는 곳

몇몇 DB 와 plist 에는 시각 옆에 시간대 칸이나 키가 따로 있습니다. 아래는 iOS 27.0 백업에서 이름을 확인한 곳이고(확인 범위: iPhone 13 mini, iOS 27.0), 값은 읽지 않았습니다. 각 칸의 저장 기준(Mac 절대 초인지 등)과 정확한 쓰임새는 확인하지 못했으므로, 이름만 보고 값을 해석하지 말고 해당 아티팩트 페이지와 실제 값으로 확인합니다.

| 파일(도메인 :: 경로) | 표 또는 키 | 시간대·시각 칸 |
|---|---|---|
| `CameraRollDomain :: Media/PhotoData/Photos.sqlite` | `ZADDITIONALASSETATTRIBUTES` | `ZTIMEZONEOFFSET`, `ZINFERREDTIMEZONEOFFSET`, `ZDATECREATEDSOURCE`, `ZALTERNATEIMPORTIMAGEDATE`, `ZLASTVIEWEDDATE` |
| 같은 파일 | `ZEXTENDEDATTRIBUTES` | `ZDATECREATED`, `ZTIMEZONEOFFSET`, `ZTIMEZONENAME` |
| 같은 파일 | `ZMOMENT` | `ZTIMEZONEOFFSET`, `ZSTARTDATE`, `ZENDDATE` |
| 같은 파일 | `ZPHOTOSHIGHLIGHT` | `ZSTARTTIMEZONEOFFSET`, `ZENDTIMEZONEOFFSET` |
| `AppDomainGroup-group.com.apple.reminders :: Container_v#/Stores/Data-*.sqlite` | `ZREMCDREMINDER` | `ZTIMEZONE`, `ZDISPLAYDATETIMEZONE`, `ZDISPLAYDATEUPDATEDFORSECONDSFROMGMT`, `ZCREATIONDATE`, `ZLASTMODIFIEDDATE`, `ZDUEDATE`, `ZCOMPLETIONDATE` |
| `HomeDomain :: Library/Calendar/Extras.db` | `ZALARM` | `ZENTITYTIMEZONE`, `ZENTITYDATE`, `ZFIRETIME`, `ZACKNOWLEDGEDDATE` |
| `HomeDomain :: Library/Preferences/com.apple.AppStore.plist` | 키 | `lastBootstrapTimeZone` (str), `lastBootstrapDate` (float) |
| `HomeDomain :: Library/Preferences/com.apple.games.plist` | 키 | `lastBootstrapTimeZone` (str), `lastBootstrapDate` (float) |
| `HomeDomain :: Library/Preferences/com.apple.ScreenTimeAgent.plist` | 키 | `LastTimeZoneName` (str), `UsageGenesisDate` (datetime), `LastViewedAllActivityDate` (datetime) |
| `HomeDomain :: Library/Preferences/com.apple.chronod.plist` | 키 | `lastKnownTimes` 안의 `timeZoneSecondsFromGMT`, `world` |

사진 쪽 표는 사건마다 시간대가 붙어 있어서 사건 단위로 현지 시각을 맞출 수 있는 후보이지만, plist 키는 성격이 다릅니다. `com.apple.AppStore.plist` 에서 읽는 마지막 부트스트랩 시간대와 그 시간대를 적용한 날짜는 수집 시점의 설정을 찍어 둔 값이지 시각마다 쌓인 사건 기록이 아니라고 설명한 글이 있습니다 [3]. 이런 키로 과거의 모든 사건에 같은 시간대를 씌우면 안 되고, 시간대 설정 기록 자체는 [시간대와 시각 설정 (Time Zone)](../../../02-artifacts/system-account/time-zone.md)에서 다룹니다. 사진의 시각 해석은 [사진 보관함 (Photos Library)](../../../02-artifacts/media/photos/index.md), 미리 알림과 캘린더는 [미리 알림과 캘린더 (Reminders·Calendar)](../../../02-artifacts/mail-cloud/reminders-calendar.md)에 있습니다.

## 직접 해 보기

아래 값은 명세로 만든 예시이고, 특정 기기에서 나온 값이 아닙니다.

Mac 절대 초 `700000000.0` 을 IEEE 754 double 로, 바이트 순서를 big-endian 으로 적으면 다음 8바이트가 됩니다.

```
41 c4 dc 93 80 00 00 00
```

이 값에 978307200 을 더하면 Unix 초 1678307200 이 되고, UTC 로는 2023-03-08 20:26:40 입니다. 한국 표준시(UTC+9)로 적으면 2023-03-09 05:26:40 이라서 날짜가 하루 넘어가는데, 시간대를 섞어 쓰면 이런 날짜 차이가 타임라인에서 사건 순서를 뒤집기도 합니다.

같은 시각을 나노초 단위로 적으면 `700000000000000000` 이라는 18자리 정수가 되고, 10^9 로 나누면 다시 `700000000` 이 됩니다. 도구가 이 18자리 값을 초로 읽으면 터무니없이 먼 미래 날짜가 나오므로, 결과가 수집 시각보다 한참 뒤라면 단위를 잘못 본 것은 아닌지 먼저 의심합니다. 파일 안에서 값이 저장되는 방식은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)와 [속성 목록 파일 (plist·NSKeyedArchiver)](../../../01-foundations/data-formats/plist.md)에서 확인합니다.

## 도구

변환은 SQLite 명령줄 셸이나 DB Browser for SQLite 같은 공개 도구에서 SQL 로 해도 되고, 스프레드시트에서 해도 됩니다. 어느 도구를 쓰든 도구가 보여 주는 날짜만 옮기지 말고 원래 숫자를 함께 뽑아 두어야 위의 검산을 할 수 있습니다. 도구가 시각을 어떻게 바꾸는지 확인하는 방법은 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md)에 있습니다.

## 함정과 한계

변환식에 `'localtime'` 같은 수정자가 들어 있으면 결과는 기기의 시간대가 아니라 분석 PC 의 시간대로 나오고, PC 를 바꾸면 같은 식이 다른 결과를 냅니다. 한 칸 안에 초와 나노초가 섞이는 경우가 있어서 칸 하나에 식 하나만 걸면 일부 행이 틀어지고, 0 이 들어간 행을 그대로 바꾸면 2001-01-01 이라는 가짜 시각이 타임라인 맨 앞에 끼어듭니다. plist 의 `float` 키처럼 기준점을 확인하지 못한 숫자는 Mac 절대 초라고 짐작해서 바꾸지 않습니다. 이 페이지의 칸·키 이름은 iOS 27.0 백업 하나에서 이름만 확인한 것이라, 다른 버전에서는 이름이 다를 수 있습니다.

## 결과를 어떻게 해석하나

정규화한 표에는 행마다 원래 값, 판단한 단위, UTC 시각, 기기 시간대와 그 근거, 원본 위치를 둡니다. 시간대 칸이 있는 기록은 그 값을, 없는 기록은 "시간대 모름" 을 적어 두어야 보고서에서 현지 시각을 말할 때 어느 쪽이 추정인지 드러납니다. 정규화는 값을 같은 자로 잰 것일 뿐 기기 시계가 맞았는지까지 보장하지 않으므로, 시계를 손으로 바꾼 흔적은 [시각 조작 흔적 (Time Manipulation)](time-manipulation.md)에서 따로 확인합니다.

## 참고 문헌

1. Date Representations, Dates and Times Programming Guide for Core Foundation (Apple Developer) — https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFDatesAndTimes/Concepts/DataReps.html
2. Time is NOT on our side when it comes to messages in iOS 11 (Smarter Forensics, 2017-09) — https://smarterforensics.com/2017/09/time-is-not-on-our-side-when-it-comes-to-messages-in-ios-11/
3. iOS Timezone Information (Forensafe) — https://forensafe.com/blogs/ios-timezone-information.html
