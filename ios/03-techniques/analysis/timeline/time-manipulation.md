---
title: "시각 조작 흔적"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 1300
---

# 시각 조작 흔적 (Time Manipulation)

아이폰의 날짜와 시각을 손으로 바꾼 흔적, 그리고 기록끼리 앞뒤가 맞지 않는 곳을 찾아서 타임라인을 어디까지 믿을 수 있는지 정하는 방법입니다.

## 언제 쓰나

기록의 시각 자체가 쟁점인 사건이거나, 타임라인을 만들다가 수집 시각보다 뒤에 찍힌 기록이나 앞뒤가 뒤집힌 기록이 나왔을 때 씁니다. 시계를 손으로 바꾼 뒤에는 기기가 보여 주는 시각이 실제와 다를 수 있어서 [1], 그 사이의 기록을 그대로 타임라인에 세우면 순서가 어긋날 수 있습니다. 사용자는 설정 앱의 일반 메뉴에 있는 날짜 및 시간 항목에서 날짜와 시각을 정할 수 있고, Apple 사용 설명서는 iOS 27 판에서도 이 위치를 안내합니다 [4]. 증거를 없애려 한 정황을 전체로 보는 흐름은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에 있고, 시각을 바꾼 사건을 조사하는 순서는 [시각 바꾸기 (Time Change)](../../../04-scenarios/activity/anti-forensics/time-change.md)에 있습니다.

## 통합 로그에 남는 흔적

날짜나 시각을 손으로 바꾸면 `timed` 프로세스가 통합 로그에 기록을 남기고, 메시지에 `TMSetManualTime` 이 들어 있으면 손으로 시각을 바꾼 것입니다. 같은 로그의 `TMCurrentTime` 변수에는 Cocoa 시각, 곧 2001-01-01 부터 센 초가 들어 있어서, 이 값을 바꾸면 사용자가 맞춘 날짜와 시각이 나옵니다 [1]. 값을 바꾸는 법은 [시각 정규화 (Time Normalization)](time-normalization.md)에 있습니다.

같은 로그도 보는 방법에 따라 시각이 다르게 보일 수 있습니다. 로그를 logarchive 로 뽑아서 보면 시계를 손으로 바꾼 뒤에도 실제로 일이 일어난 시각이 남지만, 라이브 Console 로 보면 바뀐 시스템 시각으로 보입니다. 소개된 사례에서는 Console 에서 3월 6일로 보인 로그가 logarchive 에서는 3월 23일이었고, 글쓴이는 logarchive 쪽이 실제 시각을 담는다고 봅니다. 이 글은 시험한 iOS 버전을 적지 않았습니다 [1]. 한 사건에 속한 로그를 ActivityID 로 묶는 법은 [여러 기록 엮기 (Correlation)](correlation.md)에 있습니다.

암호화하지 않은 iOS 27.0 로컬 백업의 관찰 메모에는 통합 로그(tracev3·logarchive)가 나오지 않았습니다(확인 범위: iPhone 13 mini, iOS 27.0). 로컬 백업만 확보한 사건에서는 이 흔적을 볼 수 없으니, 통합 로그를 보지 못했다는 사실을 결과에 적습니다. 로그 형식은 [통합 로그 형식 (Unified Log·tracev3)](../../../01-foundations/data-formats/unified-log.md), 로그에서 찾을 사건은 [통합 로그에서 찾을 것 (Unified Log Events)](../../../02-artifacts/logs/unified-log-events.md)에 있습니다.

## 기록 사이의 앞뒤 모순

로그가 없어도 기록끼리 앞뒤가 맞지 않는 곳에서 시계가 바뀐 정황을 볼 수 있습니다. 한 업체 블로그 글은 시계를 앞 날짜로 옮긴 기기에서 다음과 같은 모양을 이상 징후로 듭니다 [2]. 출처가 하나뿐이라, 하나가 보인다고 조작이라고 단정하지 말고 다른 기록과 함께 봅니다.

| 이상 징후 | 볼 곳 |
|---|---|
| 수집 날짜보다 뒤 시각이 찍힌 수신 SMS | [메시지 (iMessage·SMS)](../../../02-artifacts/communications/messages/index.md) |
| 쿠키를 만든 시각이 마지막 방문 시각보다 뒤인 경우 | [사파리 (Safari)](../../../02-artifacts/browsers/safari/index.md) |
| 앞 날짜로 옮긴 파일 가운데 길이가 0 인 손상 파일 | [iOS의 파일 시스템 (APFS on iOS)](../../../01-foundations/storage/filesystem/index.md) |
| 원래 그 뒤에 설치되는 파일에 찍힌 1970 년(Unix 0) 시각 | 같은 페이지 |
| Photos.sqlite, Extras.db, sms.db, powerlog DB 가 정상 기기와 다른 모양 | [사진 보관함](../../../02-artifacts/media/photos/index.md), [미리 알림과 캘린더](../../../02-artifacts/mail-cloud/reminders-calendar.md), [전원 로그](../../../02-artifacts/app-usage/powerlog.md) |

같은 글은 특정 도구를 쓴 사례를 다루고 그 도구에만 딸린 문자열도 소개하지만, 이 핸드북은 일반 흔적만 옮기고 도구에 딸린 문자열이나 방법은 싣지 않습니다.

## 백업에서 볼 수 있는 단서

로컬 백업에도 시각 설정과 관계있어 보이는 키가 있지만, 아래 키는 이름만 확인했고 뜻은 출처로 확인하지 못했습니다(확인 범위: iPhone 13 mini, iOS 27.0). 조작을 판단하는 근거가 아니라 다른 기록과 맞춰 볼 후보로만 적어 둡니다.

| 파일(도메인 :: 경로) | 키 | 형 |
|---|---|---|
| `HomeDomain :: Library/Preferences/com.apple.chronod.plist` | `lastEffectiveSignificantTimeChange` | datetime |
| 같은 파일 | `lastKnownTimes` 안의 `timeZoneSecondsFromGMT` | — |

시간대 키(`com.apple.ScreenTimeAgent.plist` 의 `LastTimeZoneName`, `com.apple.AppStore.plist`·`com.apple.games.plist` 의 `lastBootstrapTimeZone`)는 [시각 정규화](time-normalization.md)의 표에 모아 두었습니다. 앱 스토어 plist 의 부트스트랩 시간대는 수집 시점의 설정을 찍어 둔 값이라는 설명이 있어서 [3], 과거 사건 시각의 시간대와 다르다는 것만으로 조작이라고 볼 수는 없습니다. 이런 키를 조작 탐지에 쓸 수 있는지는 이 핸드북에서 확인하지 못했습니다. 시간대 설정 기록 자체는 [시간대와 시각 설정 (Time Zone)](../../../02-artifacts/system-account/time-zone.md)에 있습니다.

## 절차

1. **수집 시각을 확인합니다.** 백업을 만든 시각을 기준점으로 적고, 그 방법은 [여러 기록 엮기](correlation.md)의 절차 1단계를 따릅니다.
2. **수집 시각보다 뒤에 있는 기록을 찾습니다.** 정규화한 타임라인에서 기준점 뒤에 찍힌 행을 모두 뽑습니다. 먼저 단위를 잘못 본 것은 아닌지 [시각 정규화](time-normalization.md)의 검산으로 확인합니다.
3. **통합 로그가 있으면 `timed` 로그를 찾습니다.** `TMSetManualTime` 이 들어 있는 메시지를 찾고 `TMCurrentTime` 을 바꿔서 사용자가 맞춘 시각을 적습니다. 가능하면 logarchive 로 뽑은 로그를 기준으로 보고, Console 로 본 시각과 다르면 두 값을 모두 적습니다.
4. **앞뒤 모순을 표로 모읍니다.** 위 "기록 사이의 앞뒤 모순" 표의 유형마다 해당하는 행이 있는지 확인하고, 기록마다 원래 값을 함께 남깁니다.
5. **시계가 바뀌었다고 보이는 구간을 표시합니다.** 조작 흔적이 있으면 그 앞뒤 구간의 기록 시각을 "기기 시계 기준" 으로 따로 표시하고, 다른 기록과 순서를 맞춰 볼 때 이 구간은 확정하지 않습니다.

## 함정과 한계

logarchive 쪽이 실제 시각을 담는다는 판단과 이상 징후 목록은 각각 출처 하나의 설명이고, 시험한 iOS 버전도 모두 밝혀져 있지는 않습니다. 수집 시각보다 뒤에 있는 기록은 조작 말고도 단위를 잘못 읽었거나 시간대를 섞어서 생길 수 있어서, 2단계의 검산을 건너뛰면 멀쩡한 기록을 조작으로 오해합니다. 반대로 모순이 보이지 않는다고 해서 시계가 바뀌지 않았다는 뜻은 아니고, 그 구간에 모순을 드러낼 기록이 없었을 수도 있습니다.

## 결과를 어떻게 해석하나

`TMSetManualTime` 로그는 누군가 기기에서 시각을 손으로 맞췄다는 것까지 보여 주고, 누가 왜 그랬는지는 보여 주지 않습니다. 보고서에는 "logarchive 기준 이 시각에 `timed` 가 수동 시각 설정 로그를 남겼고, 로그에 담긴 설정 시각은 이 값이다" 처럼 기록이 말하는 만큼만 적고, 그 뒤 구간의 다른 기록은 기기 시계 기준이라 실제 시각과 다를 수 있다고 밝힙니다. 통합 로그를 보지 못한 사건이라면 앞뒤 모순만 근거로 들고, 로그를 확인하지 못했다는 사실을 함께 적습니다.

## 참고 문헌

1. Don't Trust the Clock: Timestamp Discrepancies in iOS Unified Logs (ios-unifiedlogs.com) — https://www.ios-unifiedlogs.com/post/ios-unified-logs-don-t-trust-the-clock-timestamp
2. Identify Clock Manipulation or Hot Loader used on iOS Device (Coker Forensics) — https://cokerforensics.com/identifying-when-a-hot-loader-was-used-to-backdate-an-ios-device/
3. iOS Timezone Information (Forensafe) — https://forensafe.com/blogs/ios-timezone-information.html
4. Change the date and time on iPhone (Apple 지원, iPhone 사용 설명서) — https://support.apple.com/guide/iphone/change-the-date-and-time-iph65f82af3e/ios
