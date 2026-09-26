---
title: "시간대와 시각 설정"
parent: "아티팩트 · 시스템·계정"
nav_order: 300
---

# 시간대와 시각 설정 (Time Zone)

## 한 줄 요약

아이폰의 시간대는 설정에 따라 기기 위치로 저절로 정해지기도 하고 사용자가 도시를 골라 바꾸기도 하며, 전체 파일 시스템 추출에서는 시간대 설정 파일로, 로컬 백업에서는 여러 설정 파일과 앱 DB 에 흩어진 "그때의 시간대" 값으로 확인하고, 이 값을 알아야 UTC 로 적힌 기록을 현지 시각으로 바르게 옮길 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

날짜와 시간을 자동으로 맞추려면 인터넷 연결과 최신 소프트웨어가 필요하고, 설정의 일반 → 날짜 및 시간에서 "자동으로 설정" 을 켜고, 설정의 개인정보 보호 및 보안 → 위치 서비스 → 시스템 서비스에서 "시간대 설정" 을 켜야 합니다[6]. 이렇게 켜 두면 기기가 현재 위치로 시간대를 정하고[6], 자동 설정은 모든 통신사·국가·지역에서 되지는 않을 수 있습니다[6]. 자동이 안 되는 곳에서는 "자동으로 설정" 을 끄고 도시를 입력해 시간대를 직접 바꿀 수 있습니다[6].

스크린 타임 암호가 켜져 있거나 기기 제한이 있는 회사 관리 프로파일이 설치되어 있으면 이 설정이 흐리게 보이고 고를 수 없습니다[6]. 그래서 자동 설정이 켜진 기기는 사용자가 움직이는 대로 시간대가 바뀌니, 시간대가 바뀐 기록이 곧 사용자가 손으로 바꾼 흔적은 아닙니다. 반대로 설정을 고를 수 없는 기기였다면 사용자가 바꿨다고 보기 어렵습니다. 다만 이 둘은 설정 동작에서 이끌어 낸 추론이고, 기기에 실제로 어떻게 기록되는지는 공개된 자료가 없어 검체로 확인해야 합니다.

시간대 설정 말고도 여러 구성 요소가 "무엇을 할 때 시간대가 무엇이었는지" 를 자기 설정 파일에 적어 둡니다. 로컬 백업에서는 App Store, 게임, 스크린 타임, chronod 의 설정 파일과 iCloud 백업 설정에 시간대 이름이나 GMT 와의 차이를 담는 키가 있습니다.

## 위치와 버전별 차이

### 전체 파일 시스템 추출

iOS 15 전체 파일 시스템에서 시간대와 시간대 설정은 아래 파일에 있습니다[1]. 설정 파일 안의 키 이름(예: 자동 시간대가 켜져 있는지)은 공개된 자료가 없어 검체에서 확인합니다.

| 알고 싶은 것 | 경로 |
|---|---|
| 현재 시간대 | `/private/var/db/timezone/localtime` |
| 시간대 설정 | `/private/var/db/timed/Library/Preferences/com.apple.preferences.datetime.plist` |

로컬 백업(iOS 27.0)에는 `/private/var/db/timed/` 나 `/private/var/db/timezone/` 에 해당하는 도메인 경로가 없습니다. 그래서 로컬 백업만으로는 이 두 파일을 보지 못할 가능성이 높지만, 백업에서 빠진다고 밝힌 공개 자료는 없습니다. 수집 방식별 범위는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

### 로컬 백업에 남는 시간대 흔적

로컬 백업에서 시간대를 담는 키는 아래와 같습니다. 모두 `HomeDomain :: Library/Preferences/` 아래 파일입니다.

| 파일 | 키 | 짝이 되는 시각 키 |
|---|---|---|
| `com.apple.AppStore.plist` | `lastBootstrapTimeZone` (str) | `lastBootstrapDate` (float) |
| `com.apple.games.plist` | `lastBootstrapTimeZone` (str) | `lastBootstrapDate` (float) |
| `com.apple.ScreenTimeAgent.plist` | `LastTimeZoneName` (str) | 없음 |
| `com.apple.chronod.plist` | `lastKnownTimes` 안의 `timeZoneSecondsFromGMT`, `world` | `lastEffectiveSignificantTimeChange` (datetime) |
| `com.apple.mobile.ldbackup.plist` | `LastCloudBackupTZ` (str) | `LastCloudBackupDate` (int) |

`/private/var/mobile/Library/Preferences/com.apple.AppStore.plist` 의 마지막 부트스트랩 시간대와 부트스트랩 날짜로 기기가 마지막으로 시작되거나 재구성될 때 적용된 시간대를 알 수 있다는 해석이 있습니다[5]. 위 표의 `lastBootstrapTimeZone`·`lastBootstrapDate` 가 그 값으로 보입니다. "부트스트랩" 이 기기 시작을 뜻하는지 App Store 가 처음 준비되는 때를 뜻하는지는 다른 공개 자료가 없어 검체로 확인해야 합니다. `LastCloudBackupTZ` 는 이름으로 보아 마지막 iCloud 백업 때의 시간대이고, 나머지 키도 이름으로 뜻을 짐작할 뿐입니다.

### 앱 DB 안의 시간대 칸

시각과 함께 시간대를 적는 칸이 있는 앱 DB 도 있었습니다.

| DB | 표 | 칸 |
|---|---|---|
| `CameraRollDomain :: Media/PhotoData/Photos.sqlite` | `ZADDITIONALASSETATTRIBUTES` | `ZTIMEZONEOFFSET`, `ZINFERREDTIMEZONEOFFSET` |
| 같은 DB | `ZEXTENDEDATTRIBUTES` | `ZTIMEZONEOFFSET`, `ZTIMEZONENAME` |
| 같은 DB | `ZMOMENT` | `ZTIMEZONEOFFSET` |
| 같은 DB | `ZPHOTOSHIGHLIGHT` | `ZSTARTTIMEZONEOFFSET`, `ZENDTIMEZONEOFFSET` |
| `AppDomainGroup-group.com.apple.reminders :: Container_v#/Stores/Data-*.sqlite` | `ZREMCDREMINDER` | `ZTIMEZONE`, `ZDISPLAYDATETIMEZONE`, `ZDISPLAYDATEUPDATEDFORSECONDSFROMGMT` |
| `HomeDomain :: Library/Calendar/Extras.db` | `ZALARM` | `ZENTITYTIMEZONE` |

이런 칸은 사진을 찍거나 일정을 만든 그 순간의 시간대를 담는 것으로 보여서, 기기 설정 파일의 시간대가 하나뿐일 때도 여러 시점의 시간대를 모을 수 있습니다. 오프셋 칸의 단위(초인지 분인지)는 공개된 자료가 없어 검체의 값으로 확인합니다. 사진은 [사진 보관함](../media/photos/index.md), 미리 알림과 일정은 [미리 알림과 캘린더](../mail-cloud/reminders-calendar.md) 에서 다룹니다.

iOS 15 와 iOS 27 사이에 시간대 파일 위치나 키 이름이 바뀌었는지는 공개된 자료가 없습니다. 위 전체 파일 시스템 경로는 iOS 15[1], 백업 쪽 키는 iOS 27.0 기준입니다.

## 구조

`com.apple.preferences.datetime.plist` 와 위 표의 설정 파일은 plist 입니다. 설정 파일에서 시간대는 `LastTimeZoneName` 처럼 문자열 이름으로 적히거나, `timeZoneSecondsFromGMT` 처럼 이름으로 보아 GMT 와의 차이를 초로 적는 키로 나타났습니다. 서머타임이 있는 지역은 같은 시간대 이름이라도 계절마다 GMT 와의 차이가 달라서, 이름과 차이가 둘 다 있으면 함께 봅니다. plist 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

`/private/var/db/timezone/localtime` 의 파일 형식은 공개된 분석 자료가 없어 검체에서 확인합니다.

## 증거로서 의미

**증명하는 것.** 설정 파일에 시간대 이름이 있으면, 그 키가 마지막으로 저장될 때 기기에 그 시간대가 적용되어 있었다는 기록이 됩니다. 짝이 되는 시각 키가 있으면 "이 시각에 이 시간대였다" 는 점 하나를 얻고, 파일 여러 개와 앱 DB 의 시간대 칸을 모으면 시간대가 언제 무엇에서 무엇으로 바뀌었는지 대략의 흐름을 세울 수 있습니다. 보고서에는 "이 파일의 이 키에 이 시간대 이름이 적혀 있다" 처럼 씁니다.

**증명하지 못하는 것.** 시간대는 기기 설정이지 사람의 위치 기록이 아닙니다. 자동 설정이 켜져 있었다면 위치에 따라 바뀌었을 수 있고, 꺼져 있었다면 사용자가 고른 값이라서 실제 위치와 다를 수 있습니다[6]. 따라서 시간대 값만으로 사용자가 그 나라에 있었다고 쓰지 않고, 위치는 [그 시각에 어디 있었나](../../04-scenarios/activity/location.md) 의 흐름대로 위치 기록과 맞춰 봅니다. 시간대가 바뀐 기록도 자동 변경인지 사용자가 바꾼 것인지 이 키들만으로는 가릴 수 없습니다.

## 시각 해석

iOS 기록의 시각 값 가운데는 Mac 절대 시각이나 유닉스 시각처럼 시간대 없는 숫자가 많습니다. 시각 값의 기준 시점과 단위는 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다루고, 이 페이지는 그 값을 현지 시각으로 옮길 때 어느 시간대를 쓰는지를 다룹니다.

첫째, 기록을 만든 그때의 시간대를 씁니다. 수집 시점의 시간대 하나로 모든 기록을 옮기면, 사용자가 다른 시간대에 있던 기간의 기록이 몇 시간씩 어긋나 보입니다. 사진처럼 기록 자체에 시간대 칸이 있으면 그 칸을 우선하고, 없으면 위 설정 파일과 앱 DB 에서 모은 시간대 흐름으로 그 기간의 시간대를 정합니다.

둘째, 보고서에는 UTC 값과 현지 시각을 둘 다 적고, 현지 시각을 만들 때 쓴 시간대와 그 근거(어느 파일의 어느 키)를 밝힙니다.

셋째, 로그의 시간대를 먼저 확인합니다. iOS 15 이미지에서는 일부 로그 항목의 시각이 Cupertino(미국 태평양 시간대) 기준으로 적혀 있었습니다[1]. 어떤 로그가 그런지 정리된 자료가 없으니, 로그를 볼 때는 시각 문자열에 시간대 표시가 있는지, 없다면 어느 시간대 기준인지부터 확인합니다.

넷째, 시간대가 바뀐 것과 시계가 바뀐 것을 나눕니다. 시간대를 바꾸면 UTC 값은 그대로이고 화면에 보이는 현지 시각만 달라지지만, 자동 설정을 끄고 날짜와 시각 자체를 바꾸면 그 뒤 기록의 UTC 값부터 틀어질 수 있습니다. 기기 시계를 손으로 바꾼 흔적은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 의 방법대로 서버에서 받은 시각이 들어간 기록과 맞춰 찾습니다.

## 함정과 한계

**수집 시점의 시간대로 모든 기록을 옮기지 않습니다.** 분석 도구가 한 가지 시간대를 전체에 적용하는 설정이면, 여행 기간 기록이 틀린 현지 시각으로 보입니다. 도구 설정의 시간대를 확인하고, 필요하면 UTC 로 둔 채 따로 옮깁니다.

**"마지막" 값 하나만 남습니다.** 설정 파일의 시간대 키는 대부분 가장 최근 값 하나만 담아서, 그 이전에 어떤 시간대를 거쳤는지는 보여 주지 않습니다. 이전 기간은 사진·미리 알림·일정처럼 기록마다 시간대를 적는 DB 에서 채웁니다.

**서로 다른 키가 서로 다른 때를 가리킵니다.** App Store 의 부트스트랩 시각, iCloud 백업 시각, 스크린 타임의 마지막 값은 저장된 때가 제각각입니다. 값이 서로 다르면 조작을 의심하기 전에 각 키가 언제 저장되었는지부터 맞춰 봅니다.

**지우기와 조작.** 사용자가 시간대나 시계를 바꿔 기록의 겉보기 시각을 흐릴 수 있습니다. 시간대 값이 위치 기록이나 서버 시각과 맞지 않으면 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름으로 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 이진 plist 명세로 만든 예시이고 특정 검체에서 나온 바이트가 아닙니다. 이진 plist 에서 ASCII 문자열 길이가 15 이상이면 표시 바이트 하위 4비트를 `1111` 로 두고 뒤에 길이를 정수 객체로 따로 적습니다. `lastBootstrapTimeZone` 은 21글자라서 `5F` 뒤에 1바이트 정수 표시 `10` 과 길이 `15`(=21)가 오고 글자가 이어집니다.

```
5F 10 15 6C 61 73 74 42 6F 6F 74 73 74 72 61 70  _..lastBootstrap
54 69 6D 65 5A 6F 6E 65                          TimeZone
```

값이 `Asia/Seoul` 이라고 가정하면(예시 값) 10글자라서 표시 바이트 `5A` 뒤에 글자가 바로 옵니다.

```
5A 41 73 69 61 2F 53 65 6F 75 6C                 ZAsia/Seoul
```

헥스 편집기에서 키 이름 문자열을 찾은 뒤, 사전의 참조 표를 따라 짝이 되는 값 객체로 넘어가 읽습니다.

### 공개 도구로 한 번

1. 로컬 백업에서 위 설정 파일을 꺼내 Python 표준 라이브러리 `plistlib` 로 시간대 키를 모읍니다. 원본이 아니라 꺼낸 사본에서 실행합니다.

```python
import plistlib

targets = {
    "com.apple.AppStore.plist": ["lastBootstrapTimeZone", "lastBootstrapDate"],
    "com.apple.games.plist": ["lastBootstrapTimeZone", "lastBootstrapDate"],
    "com.apple.ScreenTimeAgent.plist": ["LastTimeZoneName"],
    "com.apple.chronod.plist": ["lastKnownTimes", "lastEffectiveSignificantTimeChange"],
    "com.apple.mobile.ldbackup.plist": ["LastCloudBackupTZ", "LastCloudBackupDate"],
}
for name, keys in targets.items():
    try:
        with open(name, "rb") as f:
            d = plistlib.load(f)
    except FileNotFoundError:
        print(name, "없음")
        continue
    for k in keys:
        print(name, k, d.get(k))
```

2. 사진 DB 사본에서 시간대 오프셋이 어떻게 나뉘는지 셉니다. 값이 여러 개로 나뉘면 사진을 찍은 기간에 시간대가 바뀐 적이 있다는 단서가 됩니다.

```sql
SELECT ZTIMEZONENAME, ZTIMEZONEOFFSET, COUNT(*) AS n
FROM ZEXTENDEDATTRIBUTES
GROUP BY ZTIMEZONENAME, ZTIMEZONEOFFSET
ORDER BY n DESC;
```

3. 도구가 보여 주는 현지 시각은 어느 시간대 설정으로 옮긴 것인지 확인하고, 같은 값을 UTC 로 한 번 더 뽑아 비교합니다. 도구 검증은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

시간대 흐름은 위치 기록과 맞춰 봐야 뜻이 섭니다. [중요 위치](../location/significant-locations.md) 와 [위치 기록 데몬](../location/routined.md) 의 방문 장소, [카메라 사진과 메타데이터](../media/dcim-exif.md) 의 촬영 위치와 시각을 시간대 값과 나란히 놓습니다. 기기 지역 코드는 [기기 정보](device-info.md) 의 `com.apple.AppSupport.plist` 키와, 스크린 타임 쪽 값은 [화면 사용 시간](../app-usage/screen-time.md) 과 비교합니다. 로그 시각은 [통합 로그에서 찾을 것](../logs/unified-log-events.md) 에서, 모든 기록을 한 줄로 세우는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등의 iOS 이미지나 백업)로 다음 질문을 풀어 봅니다.

1. 전체 파일 시스템 추출이라면 `com.apple.preferences.datetime.plist` 에 어떤 키가 있고, 자동 시간대 설정을 나타내는 것으로 보이는 키는 무엇입니까?
2. 백업의 설정 파일 다섯 개에 적힌 시간대 이름은 모두 같습니까? 다르다면 짝이 되는 시각 키로 순서를 세워 봅니다.
3. `Photos.sqlite` 의 `ZTIMEZONENAME` 은 몇 가지 값으로 나뉘고, 각 값의 사진은 언제부터 언제까지 찍혔습니까?
4. 같은 사진의 `ZEXTENDEDATTRIBUTES.ZTIMEZONEOFFSET` 과 `ZADDITIONALASSETATTRIBUTES.ZTIMEZONEOFFSET` 값이 같습니까?
5. 분석 도구의 시간대 설정을 UTC 와 검체 시간대로 바꿔 가며 같은 기록의 표시 시각이 어떻게 달라지는지 확인합니다.

## 참고 문헌

- [1] iOS 15 Image Forensics Analysis and Tools Comparison: Processing details and general device information — digital-forensics.it (2023-09) — https://blog.digital-forensics.it/2023/09/ios-15-image-forensics-analysis-and.html
- [5] iOS Timezone Information — Forensafe — https://forensafe.com/blogs/ios-timezone-information.html
- [6] If you can't change the time or time zone on your Apple device (101619) — Apple Support — https://support.apple.com/en-us/101619
