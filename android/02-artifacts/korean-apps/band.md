---
title: "네이버 밴드"
parent: "아티팩트 · 국내 생활 앱"
nav_order: 1040
---

# 네이버 밴드 (BAND)

## 한 줄 요약

네이버 밴드는 NAVER 의 모임 앱이고 패키지 이름은 com.nhn.android.band 입니다. 앱이 자기 폴더에 어떤 파일과 표를 남기는지 설명한 공개 자료가 없어서, 근거를 대고 쓸 수 있는 흔적은 이 패키지 이름으로 찾는 시스템 쪽 기록(설치·사용·알림)입니다.

## 무엇을 기록하나 · 왜 생기나

Google Play 앱 상세 페이지에 표시된 식별 정보는 아래와 같습니다[1].

| 항목 | 값 |
|---|---|
| 패키지 이름 | com.nhn.android.band |
| Play 페이지 제목 | 밴드 - Google Play 앱 |
| 개발사 표시 | NAVER Corporation (개발자 연락처 주소 "분당구 정자일로 95") |
| Play 에 표시된 마지막 업데이트 날짜 | 2026년 9월 15일 (열람일 2026-09-25 기준) |

Play 의 "데이터 보안" 항목에는 제3자와 공유할 수 있는 데이터 유형이 "개인 정보, 앱 활동 및 기기 또는 기타 ID" 로, 수집할 수 있는 데이터 유형이 "위치, 개인 정보 외 8개" 로 적혀 있고, "전송 중 데이터 암호화됨" 과 "데이터 삭제를 요청할 수 있음" 도 표시돼 있습니다. [1] 이 항목은 개발사가 스스로 적어 낸 내용이라 Play 페이지에도 "다음은 개발자가 제공한 정보이며 추후 업데이트될 수 있습니다" 라는 문구가 붙어 있습니다. 기기에 무엇이 남는지 알려 주는 자료가 아니어서, 앱이 어떤 종류의 데이터를 다루는지 가늠하는 참고로만 씁니다.

글·댓글·채팅·가입한 밴드 목록이 기기 안의 DB 에 쌓이는지, 화면을 열 때마다 서버에서 받아 오는지는 실제 기기로 확인해야 합니다. 사진·동영상을 저장할 때 공용 저장 공간의 어느 폴더를 쓰는지도 실제 기기에서 확인합니다.

앱 바깥의 시스템 기록은 앱 이름과 상관없이 모든 사용자 앱에 대해 쌓입니다. 앱 사용 기록(dumpsys usagestats)에는 사용자가 설치한 앱마다 ACTIVITY_RESUMED·ACTIVITY_PAUSED·ACTIVITY_STOPPED, NOTIFICATION_INTERRUPTION·NOTIFICATION_SEEN, SHORTCUT_INVOCATION, USER_INTERACTION, STANDBY_BUCKET_CHANGED, FOREGROUND_SERVICE_START·FOREGROUND_SERVICE_STOP 이벤트가 package 필드와 함께 나옵니다. 현재 알림 목록(dumpsys notification)의 NotificationRecord 에는 pkg, channel, android.title, android.text, when, mCreationTimeMs, mUpdateTimeMs 필드가 있고, 제목·본문은 실제 글자 대신 [length=##] 처럼 길이만 찍힙니다. 각 기록의 필드 뜻은 [앱 사용 기록](../app-usage/usagestats/index.md)과 [알림 기록](../app-usage/notification-history.md)에서 다룹니다.

## 위치와 버전별 차이

| 위치 | 기대하는 내용 | 비고 |
|---|---|---|
| 앱 비공개 데이터 폴더(패키지 이름 폴더) | 앱 DB·설정 파일 | 파일 이름·표·열 이름은 공개 자료 없음, 실제 기기에서 확인 |
| 공용 저장 공간 | 저장한 사진·동영상·내려받은 파일 | 앱이 쓰는 폴더 이름은 실제 기기에서 확인 |
| 앱 사용 기록 | 화면 전환·알림·바로 가기 이벤트 | 모든 사용자 앱에 대해 같은 필드 구성으로 쌓임 |
| 알림 기록·현재 알림 목록 | 알림 채널·제목·본문·시각 | dumpsys 출력에서는 제목·본문이 길이로만 나옴 |
| 설치된 앱 기록 | 설치 사실과 판 정보 | 패키지 이름으로 찾음 |

앱 비공개 폴더의 구조와 사용자별 폴더는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md)에서, 그 폴더를 어떤 권한으로 읽을 수 있는지는 [앱 샌드박스와 권한](../../01-foundations/security-model/sandbox-permissions.md)에서 다룹니다.

공용 저장 공간에는 /sdcard 최상위와 DCIM·Pictures·Download 아래에 앱이 만든, 표준 이름이 아닌 폴더가 생길 수 있습니다. /sdcard/Android/media 아래에는 com.google.android.gms 처럼 패키지 이름을 그대로 폴더 이름으로 쓴 앱별 폴더가 생깁니다. 밴드가 이런 폴더를 만드는지는 알려진 자료가 없으니, 실제 기기에서 com.nhn.android.band 이름의 폴더가 있는지 직접 찾아봅니다. 공용 저장 공간의 구조는 [공용 저장 공간](../../01-foundations/storage/shared-storage.md)에서 다룹니다.

Android 버전이나 One UI 버전에 따라 이 앱의 흔적이 어떻게 달라지는지는 공개 자료가 없습니다.

## 구조

앱 폴더 안의 DB 이름, 표 이름, 열 이름은 공개 자료가 없습니다. 실제 기기에서 앱 폴더를 확보했다면 파일마다 형식을 먼저 가려내고, 형식에 맞는 기반 구조 페이지를 따라 읽습니다. SQLite 는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), XML 설정 파일은 [설정 XML과 SharedPreferences](../../01-foundations/data-formats/shared-preferences.md)에서 다루고, 처음 보는 앱의 폴더를 살펴보는 순서는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** 설치된 앱 기록에 com.nhn.android.band 가 있으면 그 기기(사용자)에 밴드가 설치돼 있었다는 사실을 보여 줍니다. 앱 사용 기록에 이 패키지의 ACTIVITY_RESUMED 와 ACTIVITY_PAUSED 가 있으면 그 시간대에 밴드 화면이 앞에 나와 있었다는 기록이 되고, NOTIFICATION_INTERRUPTION 이 있으면 그 시각에 밴드가 사용자를 방해하는(interruptive) 알림을 올렸다는 기록이 됩니다. 알림 기록 파일이 남아 있다면 알림이 올라온 시각과 제목·본문까지 볼 수 있지만, dumpsys notification 출력에서는 제목·본문이 길이로만 나옵니다.

**증명하지 못하는 것.** 시스템 기록만으로는 누가 폰을 들고 있었는지, 어느 밴드에서 무슨 글을 읽거나 썼는지 알 수 없습니다. 알림 본문은 앱이 알림으로 띄운 문자열이라 원글 전체와 같은지는 앱 내부 기록이나 서비스 쪽 자료와 맞춰 봐야 알 수 있습니다. 이 앱이 기기에 무엇을 남기는지 알려진 바가 없으므로, 앱 폴더에서 대화나 글이 나오지 않았더라도 "대화가 없었다" 고 쓰지 않습니다.

보고서에는 "밴드로 글을 올렸다" 가 아니라 "이 시간대에 com.nhn.android.band 화면이 앞에 나온 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

앱 내부 시각 열의 기준(유닉스 밀리초인지 다른 기준인지)은 실제 데이터로 확인합니다. 숫자 모양을 보고 기준을 추정하는 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

시스템 쪽 기록에서 dumpsys notification 출력의 mCreationTimeMs·mUpdateTimeMs 는 값 뒤 괄호 안에 +#### 모양의 시간대 오프셋이 붙은 시각으로 나옵니다. 앱 사용 기록의 time 값은 출력만으로 어느 시간대 기준인지 알기 어려우니, 기기의 시간대 설정을 [시간대와 시각 설정](../system-account/time-zone.md)에서 먼저 확인하고 맞춥니다.

## 함정과 한계

공개 도구에 이 앱을 풀어 주는 전용 모듈이 없습니다. ALEAPP 의 scripts/artifacts 폴더 519개 항목 가운데 이름에 naver 나 band 가 들어간 파일이 없고, CARPE(GitHub 조직 dfrc-korea)의 modules 폴더 80개 항목에도 밴드 이름이 붙은 모듈이 없습니다. [2][3] 도구 결과에 밴드가 안 나온다고 흔적이 없다고 보지 말고 앱 폴더를 직접 엽니다.

Play 데이터 보안 항목에 "위치" 가 적혀 있어도 기기 안에 위치 기록이 남는다는 뜻은 아닙니다. 이 항목은 개발사가 신고한 수집·공유 범위이고, 기기에 남는 파일과는 관계가 없습니다. [1]

시스템 기록은 오래 쌓아 두지 않아서 오래된 사용 흔적은 남아 있지 않을 수 있습니다. 기록마다 얼마나 보관하는지는 각 기록의 페이지에서 다룹니다.

## 직접 분석해 보기

**헥스로 한 번.** 이 앱의 파일 형식은 공개 명세가 없습니다. 실제 기기에서 앱 폴더를 확보했다면 파일마다 앞부분 몇 바이트를 헥스로 열어 형식을 알려 주는 머리 바이트를 확인하고, 그 형식의 기반 구조 페이지로 넘어갑니다.

**명령으로 한 번.** 앱 사용 기록과 알림 기록은 adb 일반 셸 권한으로 읽을 수 있고, 패키지 이름으로 걸러 이 앱의 줄만 봅니다.

```
adb shell "dumpsys usagestats | grep com.nhn.android.band"
adb shell "dumpsys notification | grep -A 3 pkg=com.nhn.android.band"
```

첫 명령에서 type 필드를 보고 화면 전환·알림·바로 가기 이벤트를 나누고, 둘째 명령에서 NotificationRecord 줄을 찾은 다음 그 아래의 channel·mCreationTimeMs 필드를 읽습니다. 이 출력에서 제목·본문은 길이만 나오므로 글자는 알림 기록 파일에서 찾습니다. 알림 레코드는 줄이 길어서 -A 뒤의 숫자를 늘려 가며 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 내용 |
|---|---|
| [설치된 앱](../app-usage/packages/index.md) | 설치된 적이 있는지, 언제 설치·업데이트됐는지 |
| [구글 플레이 기록](../app-usage/play-store.md) | 스토어를 거쳐 받았는지 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 화면이 앞에 나온 시간대 |
| [알림 기록](../app-usage/notification-history.md) | 알림이 올라온 시각과 제목·본문 |
| [최근 앱 화면](../app-usage/recents-snapshots.md) | 마지막으로 본 화면이 남았는지 |
| [데이터 사용량](../network/netstats.md) | 그 시간대에 이 앱이 주고받은 데이터 양 |
| [미디어 저장소](../media/mediastore/index.md) | 앱이 공용 저장 공간에 저장한 사진·동영상 |

연락 상대를 따지는 조사라면 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md)를, 지운 글이나 대화를 찾는 조사라면 [지운 대화와 사진 찾기](../../04-scenarios/activity/deleted-content.md)를 함께 봅니다.

## 실습

분석할 이미지를 고른 다음 설치 기록에서 패키지 이름을 찾는 일부터 시작합니다.

1. 이미지의 설치된 앱 기록에 com.nhn.android.band 가 있는가, 있다면 처음 설치 시각과 마지막 업데이트 시각은 언제인가?
2. 앱 사용 기록에서 이 패키지의 ACTIVITY_RESUMED 가 가장 많이 몰린 날은 언제이고, 그날 NOTIFICATION_INTERRUPTION 은 몇 번 나오는가?
3. 앱 비공개 폴더를 확보했다면 그 안의 파일을 형식별로 나누면 SQLite·XML·그 밖의 파일이 각각 몇 개인가?
4. 공용 저장 공간에서 이 앱이 만든 것으로 보이는 폴더를 찾았다면, 그 폴더 파일의 시각이 앱 사용 기록의 시간대와 겹치는가?

## 참고 문헌

1. 밴드 - Google Play 앱 (com.nhn.android.band). https://play.google.com/store/apps/details?id=com.nhn.android.band&hl=ko
2. abrignoni/ALEAPP — scripts/artifacts 폴더 목록(GitHub API, 519개 항목). https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
3. dfrc-korea/carpe — modules 폴더 목록(GitHub API, 80개 항목). https://api.github.com/repos/dfrc-korea/carpe/contents/modules
