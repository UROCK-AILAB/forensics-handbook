---
title: "배달 앱"
parent: "아티팩트 · 국내 생활 앱"
nav_order: 1070
---

# 배달 앱 (배달의민족·쿠팡이츠·요기요)

## 한 줄 요약

배달의민족(com.sampleapp)·쿠팡이츠(com.coupang.mobile.eats)·요기요(com.fineapp.yogiyo)는 주문 내역·배달 주소·채팅이 기기 안 어디에 남는지 설명한 공개 자료가 없습니다. 그래서 근거를 대고 쓸 수 있는 흔적은 패키지 이름으로 찾는 시스템 쪽 기록이고, 그 가운데 주문이 진행되는 동안 올라오는 알림이 가장 먼저 볼 자리입니다.

## 무엇을 기록하나 · 왜 생기나

Google Play 앱 상세 페이지에 표시된 식별 정보는 아래와 같습니다. 마지막 업데이트 날짜는 열람일 2026-09-25 기준으로 Play 에 표시된 날짜입니다.

| 앱 | 패키지 이름 | 개발사 표시 | Play 마지막 업데이트 | 출처 |
|---|---|---|---|---|
| 배달의민족 | com.sampleapp | (주)우아한형제들 | 2026년 9월 22일 | [1] |
| 쿠팡이츠 | com.coupang.mobile.eats | 쿠팡 주식회사 | 2026년 9월 21일 | [2] |
| 요기요 | com.fineapp.yogiyo | (주)위대한상상 | 2026년 9월 16일 | [3] |

배달의민족의 패키지 이름은 앱 이름과 전혀 닮지 않은 com.sampleapp 이고, 이 패키지의 Play 페이지 제목은 "배달의민족 - Google Play 앱" 입니다. [1] "baemin" 이나 "woowa" 로 찾으면 놓치니 설치 기록과 사용 기록은 com.sampleapp 으로 찾습니다. 쿠팡이츠 Play 페이지의 제목은 "쿠팡이츠 - 와우회원 배달비 0원 - Google Play 앱" 이고, 개발자 주소로는 서울특별시 송파구(쿠팡(주))와 서울특별시 광진구(쿠팡 주식회사) 두 가지가 함께 적혀 있습니다. [2] 요기요 Play 페이지의 제목은 "요기요 - 배달할 때마다 포인트 적립 - Google Play 앱" 입니다. [3]

Play 의 "데이터 보안" 칸에 개발사가 신고한 내용은 아래와 같고, 세 앱 모두 "전송 중 데이터 암호화됨" 과 "데이터 삭제를 요청할 수 있음" 도 표시돼 있습니다. [1][2][3]

| 앱 | 제3자와 공유할 수 있는 데이터 유형 | 수집할 수 있는 데이터 유형 |
|---|---|---|
| 배달의민족 | 위치, 메시지 외 3개 | 위치, 개인 정보 외 6개 |
| 쿠팡이츠 | 앱 활동 및 앱 정보 및 성능 | 위치, 개인 정보 외 6개 |
| 요기요 | 메시지, 앱 활동 외 2개 | 개인 정보, 금융 정보 외 3개 |

이 칸은 개발사가 스스로 적어 낸 내용이고 Play 페이지에도 추후 바뀔 수 있다는 문구가 붙어 있어서, 앱이 어떤 종류의 데이터를 다루는지 가늠하는 참고로만 씁니다.

주문 내역, 배달 주소, 가게 검색 기록, 라이더·가게와 주고받은 채팅이 기기 안 어디에 남는지, 어떤 파일·표·칸에 있는지는 세 앱 모두 공개 자료가 없어 검체로 확인해야 합니다.

앱 바깥에서는 운영체제가 모든 사용자 앱에 대해 앱 사용 기록과 알림 기록을 쌓고, 이 기록에 패키지 이름이 함께 적힙니다. 배달 앱은 주문을 받았을 때, 배달을 시작했을 때, 배달을 마쳤을 때 알림을 띄우는 일이 흔해서 알림 쪽 기록이 주문 흐름을 따라가는 단서가 될 수 있습니다. 다만 세 앱이 쓰는 알림 채널 이름은 판마다 다를 수 있어 검체에서 확인합니다. 두 기록에 나오는 이벤트와 칸은 [네이버 밴드](band.md) 페이지에 정리돼 있습니다.

## 위치와 버전별 차이

| 위치 | 기대하는 내용 | 비고 |
|---|---|---|
| 앱 비공개 데이터 폴더(패키지 이름 폴더) | 주문·주소·검색·채팅 | 세 앱 모두 파일 이름·표·칸 이름은 공개 자료 없음, 검체에서 확인 |
| 알림 기록 | 주문 상태 알림의 채널·제목·본문·시각 | dumpsys 출력에서는 제목·본문이 길이로만 나옴, 앱별 채널 이름은 검체에서 확인 |
| 앱 사용 기록 | 화면 전환과 알림 이벤트 | 모든 사용자 앱에 대해 같은 칸 모양으로 쌓임 |
| 설치된 앱 기록 | 설치 사실과 판 정보 | 패키지 이름으로 찾음 |

앱 비공개 폴더의 구조는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md)에서, 그 폴더를 읽을 수 있는 권한은 [앱 샌드박스와 권한](../../01-foundations/security-model/sandbox-permissions.md)에서 다룹니다.

Android 버전이나 One UI 버전에 따라 세 앱의 흔적이 어떻게 달라지는지는 공개 자료가 없습니다.

## 구조

앱 폴더 안의 DB 이름, 표 이름, 칸 이름은 세 앱 모두 공개 자료가 없습니다. 앱 폴더를 확보했다면 파일마다 형식을 먼저 가려내고 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md), [설정 XML과 SharedPreferences](../../01-foundations/data-formats/shared-preferences.md) 같은 기반 구조 페이지를 따라 읽습니다. 처음 보는 앱 폴더를 훑는 순서는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md)에 있습니다.

알림 쪽 칸은 모양이 정해져 있습니다. 앱 사용 기록에서 NOTIFICATION_INTERRUPTION 이벤트 줄에는 package 칸과 함께 channelId 칸이 나옵니다. dumpsys notification 출력의 NotificationRecord 에는 pkg, channel, android.title, android.text, when, mCreationTimeMs, mUpdateTimeMs 칸이 있고, android.title·android.text 는 실제 글자 대신 [length=##] 모양으로 길이만 나옵니다. 칸마다의 뜻과 보관 방식은 [알림 기록](../app-usage/notification-history.md)과 [앱 사용 기록](../app-usage/usagestats/index.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 설치된 앱 기록에 세 패키지 가운데 하나가 있으면 그 기기(사용자)에 그 배달 앱이 설치돼 있었다는 사실을 보여 줍니다. 앱 사용 기록에 그 패키지의 화면 전환 이벤트가 있으면 그 시간대에 앱 화면이 앞에 나와 있었다는 기록이 되고, NOTIFICATION_INTERRUPTION 이 있으면 그 시각에 앱이 사용자를 방해하는(interruptive) 알림을 올렸다는 기록이 됩니다. 알림 기록 파일이 남아 있으면 알림이 올라온 시각과 채널, 제목·본문까지 볼 수 있습니다.

**증명하지 못하는 것.** 알림이 있다고 해서 그 기기 사용자가 주문했다는 뜻은 아닙니다. 알림은 앱이 띄운 안내 문자열이고, 알림 채널이 주문 안내인지 광고인지는 채널 이름만으로 단정할 수 없습니다. 주문 알림처럼 보여도 음식을 실제로 받았는지, 누가 받았는지, 결제를 누가 했는지는 시스템 기록으로 알 수 없어서 가게·배달 쪽 기록이나 계정 쪽 자료와 맞춰 봐야 합니다.

보고서에는 "음식을 주문했다" 가 아니라 "이 시각에 com.sampleapp 이 이런 제목의 알림을 올린 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

앱 내부 시각 칸의 기준은 세 앱 모두 공개 자료가 없어 검체에서 확인합니다. 숫자 모양으로 기준을 가늠하는 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md)에 있습니다.

dumpsys notification 출력에서 mCreationTimeMs 와 mUpdateTimeMs 는 값 뒤 괄호 안에 +#### 모양의 시간대 오프셋이 붙은 시각으로 나옵니다. 칸 이름대로라면 두 값은 알림이 처음 만들어진 시각과 마지막으로 바뀐 시각이고, 같은 알림을 주문 상태에 맞춰 고쳐 쓰는 앱이라면 두 값이 벌어질 수 있습니다. 세 앱이 알림을 고쳐 쓰는지 새로 띄우는지는 알려진 자료가 없으니, 검체에서 두 값을 나란히 적어 두고 판단합니다. 앱 사용 기록의 time 값은 출력만으로 어느 시간대 기준인지 알기 어려우니 [시간대와 시각 설정](../system-account/time-zone.md)에서 기기의 시간대부터 확인합니다.

## 함정과 한계

**패키지 이름으로 찾기 어렵습니다.** 배달의민족은 앱 이름과 닮지 않은 com.sampleapp 이라서 이름으로 찾으면 놓칩니다. 쿠팡이츠의 com.coupang.mobile.eats 는 앞부분이 쿠팡 쇼핑 앱 com.coupang.mobile 과 같아서, 쇼핑 앱 쪽을 찾을 때 섞여 나옵니다. 두 쿠팡 앱을 나눠 거르는 방법은 [쿠팡](coupang.md) 페이지에 있습니다.

**공개 도구에 전용 모듈이 없습니다.** ALEAPP 의 scripts/artifacts 폴더 519개 항목 가운데 이름에 baemin, woowa, sampleapp, yogiyo, eats, deliver 가 들어간 파일이 없고, CARPE(GitHub 조직 dfrc-korea)의 modules 폴더 80개 항목에도 세 앱 이름이 붙은 모듈이 없습니다. [4][5] 도구 결과에 배달 앱이 안 나오면 앱 폴더를 직접 엽니다.

**데이터 보안 칸을 기기 흔적으로 읽지 않습니다.** 요기요의 수집 항목에 "금융 정보" 가 있고 배달의민족의 공유 항목에 "메시지" 가 있어도, 기기 안에 결제 정보나 메시지가 남는다는 뜻은 아닙니다. [1][3]

**알림은 사라지기 쉽습니다.** 사용자가 알림을 지우거나 시간이 지나면 현재 알림 목록에서 빠질 수 있으니, 알림 기록을 수집하는 시점을 보고서에 함께 적습니다. 지운 알림이 어디에 얼마나 남는지는 [알림 기록](../app-usage/notification-history.md)에서 다룹니다.

## 직접 분석해 보기

**헥스로 한 번.** 세 앱의 파일 형식은 공개 명세가 없습니다. 앱 폴더를 확보했다면 파일마다 앞부분을 헥스로 열어 형식을 알려 주는 머리 바이트를 확인하고, 그 형식의 기반 구조 페이지로 넘어갑니다.

**명령으로 한 번.** 알림 이벤트와 알림 레코드를 세 패키지 이름으로 걸러 봅니다.

```
adb shell "dumpsys usagestats | grep NOTIFICATION_INTERRUPTION | grep -E 'com.sampleapp|com.coupang.mobile.eats|com.fineapp.yogiyo'"
adb shell "dumpsys notification | grep -E -A 3 'pkg=(com.sampleapp|com.coupang.mobile.eats|com.fineapp.yogiyo) '"
```

첫 명령에서는 channelId 칸 값을 앱별로 모아 채널이 몇 가지인지 세고, 둘째 명령에서 NotificationRecord 줄을 찾은 다음 그 아래의 channel·mCreationTimeMs·mUpdateTimeMs 칸을 읽습니다. 이 출력에서 제목·본문은 길이만 나오므로 글자는 알림 기록 파일에서 찾습니다. 알림 레코드는 줄이 길어서 -A 뒤의 숫자를 늘려 가며 봅니다. 이어서 같은 패키지의 ACTIVITY_RESUMED 시각을 알림 시각 옆에 두면, 알림을 받고 앱을 열었는지를 시간 순서로 볼 수 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 내용 |
|---|---|
| [알림 기록](../app-usage/notification-history.md) | 주문 상태 알림의 시각·제목·본문 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 알림 앞뒤로 앱 화면이 앞에 나왔는지 |
| [설치된 앱](../app-usage/packages/index.md) | 설치된 적이 있는지, 언제 설치·업데이트됐는지 |
| [위치 캐시](../location/cached-locations.md) | 주문·배달 시각의 기기 위치 |
| [데이터 사용량](../network/netstats.md) | 그 시간대에 이 앱들이 주고받은 데이터 양 |
| [쿠팡](coupang.md) | 같은 회사 쇼핑 앱과 패키지 이름 구분 |

그 시각 기기 위치를 따지는 조사라면 [그 시각에 어디 있었나](../../04-scenarios/activity/location.md)를, 여러 기록을 한 줄로 세우려면 [타임라인 작성](../../03-techniques/analysis/timeline/index.md)을 함께 봅니다.

## 실습

검체를 고른 다음 설치 기록에서 패키지 이름을 찾는 일부터 시작합니다.

1. 검체의 설치된 앱 기록에 com.sampleapp, com.coupang.mobile.eats, com.fineapp.yogiyo 가운데 어느 것이 있는가?
2. 앱 사용 기록에서 이 패키지들의 NOTIFICATION_INTERRUPTION 이 몇 번 나오고, channelId 값은 앱마다 몇 가지인가?
3. dumpsys notification 출력에 남은 알림 가운데 mCreationTimeMs 와 mUpdateTimeMs 가 다른 것이 있는가, 있다면 두 값은 얼마나 벌어져 있는가?
4. 알림이 올라온 시각 바로 뒤에 같은 패키지의 ACTIVITY_RESUMED 가 있는가?

## 참고 문헌

1. 배달의민족 - Google Play 앱 (com.sampleapp). https://play.google.com/store/apps/details?id=com.sampleapp&hl=ko
2. 쿠팡이츠 - 와우회원 배달비 0원 - Google Play 앱 (com.coupang.mobile.eats). https://play.google.com/store/apps/details?id=com.coupang.mobile.eats&hl=ko
3. 요기요 - 배달할 때마다 포인트 적립 - Google Play 앱 (com.fineapp.yogiyo). https://play.google.com/store/apps/details?id=com.fineapp.yogiyo&hl=ko
4. abrignoni/ALEAPP — scripts/artifacts 폴더 목록(GitHub API, 519개 항목). https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
5. dfrc-korea/carpe — modules 폴더 목록(GitHub API, 80개 항목). https://api.github.com/repos/dfrc-korea/carpe/contents/modules
