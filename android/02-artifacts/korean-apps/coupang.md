---
title: "쿠팡"
parent: "아티팩트 · 국내 생활 앱"
nav_order: 1060
---

# 쿠팡 (Coupang)

## 한 줄 요약

쿠팡 쇼핑 앱의 패키지 이름은 com.coupang.mobile 이고, 쿠팡이츠(com.coupang.mobile.eats)와는 다른 앱입니다. 주문 내역·장바구니·검색어·배송지가 기기 안에 남는지는 공개 자료로 확인하지 못해서, 지금 근거를 대고 쓸 수 있는 흔적은 이 패키지 이름으로 찾는 시스템 쪽 기록입니다.

## 무엇을 기록하나 · 왜 생기나

Google Play 앱 상세 페이지로 확인한 식별 정보는 아래와 같습니다. [1]

| 항목 | 값 |
|---|---|
| 패키지 이름 | com.coupang.mobile |
| Play 페이지 제목 | 쿠팡(Coupang)-모바일 쇼핑 - Google Play 앱 |
| 개발사 표시 | 쿠팡 주식회사 (주소는 서울특별시 광진구로 표시) |
| Play 에 표시된 마지막 업데이트 날짜 | 2026년 9월 24일 (열람일 2026-09-25 기준) |

같은 회사의 배달 앱인 쿠팡이츠는 com.coupang.mobile.eats 라는 별도 패키지로 올라와 있습니다. [2] 쿠팡이츠의 흔적은 [배달 앱](delivery-apps.md) 페이지에서 다룹니다.

Play 의 "데이터 보안" 칸에는 제3자와 공유할 수 있는 데이터 유형이 "앱 활동, 앱 정보 및 성능 및 기기 또는 기타 ID" 로, 수집할 수 있는 데이터 유형이 "개인 정보, 앱 활동 외 2개" 로 적혀 있고, "전송 중 데이터 암호화됨" 과 "데이터 삭제를 요청할 수 있음" 도 표시돼 있습니다. [1] 이 칸은 개발사가 스스로 적어 낸 내용이고 Play 페이지도 추후 바뀔 수 있다고 밝혀 두어서, 앱이 어떤 종류의 데이터를 다루는지 가늠하는 참고로만 씁니다.

주문 내역, 장바구니, 검색어, 배송지가 기기 안에 남는지, 남는다면 어느 파일·표에 있는지는 확인하지 못했습니다. 쇼핑 앱은 화면을 웹뷰(WebView)로 그리는 경우가 많아 웹뷰 캐시나 쿠키에 흔적이 남을 수 있다는 추정은 있지만, 이 앱에 대해 그렇다고 확인한 자료는 없습니다.

앱 바깥에서는 운영체제가 모든 사용자 앱에 대해 앱 사용 기록과 알림 기록을 쌓고, 이 기록에 패키지 이름이 함께 적힙니다. 관찰 기기에서 두 기록에 어떤 이벤트와 칸이 나왔는지는 [네이버 밴드](band.md) 페이지에 정리했고, 칸의 뜻은 [앱 사용 기록](../app-usage/usagestats/index.md)과 [알림 기록](../app-usage/notification-history.md)에서 다룹니다. 관찰 메모는 기본 앱이 아닌 패키지 이름을 가려 두어서 관찰 기기에 쿠팡이 깔려 있었는지는 알 수 없습니다.

## 위치와 버전별 차이

| 위치 | 기대하는 내용 | 확인 상태 |
|---|---|---|
| 앱 비공개 데이터 폴더(com.coupang.mobile 폴더) | 주문·장바구니·검색·배송지 | 파일 이름·표·칸 이름을 확인하지 못함 |
| 같은 폴더 안의 웹뷰 저장소 | 웹 화면 캐시·쿠키 | 이 앱이 웹뷰를 쓰는지 확인하지 못함 |
| 앱 사용 기록 | 화면 전환·알림 이벤트 | 사용자 앱 전반에 대해 칸 모양을 관찰함 |
| 알림 기록·현재 알림 목록 | 주문·배송 알림의 제목·본문·시각 | 칸 모양을 관찰함(dumpsys 출력에서는 제목·본문이 길이로만 나옴) |

앱 비공개 폴더의 구조는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md)에서, 그 폴더를 읽을 수 있는 권한은 [앱 샌드박스와 권한](../../01-foundations/security-model/sandbox-permissions.md)에서 다룹니다. 웹뷰가 쓰는 저장 형식을 만나면 [LevelDB와 IndexedDB](../../01-foundations/data-formats/leveldb-indexeddb.md)와 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)를 참고합니다.

Android 버전이나 One UI 버전에 따라 이 앱의 흔적이 어떻게 달라지는지 보여 주는 자료는 찾지 못해서 버전별 표를 싣지 않습니다.

## 구조

앱 폴더 안의 DB 이름, 표 이름, 칸 이름은 공개 자료로 확인하지 못했습니다. 앱 폴더를 확보했다면 파일마다 형식을 먼저 가려내고 형식에 맞는 기반 구조 페이지를 따라 읽습니다. 처음 보는 앱 폴더를 훑는 순서는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** 설치된 앱 기록에 com.coupang.mobile 이 있으면 그 기기(사용자)에 쿠팡 쇼핑 앱이 설치돼 있었다는 사실을 보여 줍니다. 앱 사용 기록에 이 패키지의 화면 전환 이벤트가 있으면 그 시간대에 쿠팡 화면이 앞에 나와 있었다는 기록이 되고, 알림 기록 파일이 남아 있으면 그 시각에 앱이 올린 알림의 제목·본문을 볼 수 있습니다.

**증명하지 못하는 것.** 시스템 기록만으로는 무엇을 샀는지, 결제를 마쳤는지, 누가 주문했는지 알 수 없습니다. 주문·배송 알림이 남아 있어도 알림 문자열은 앱이 띄운 안내일 뿐이라, 실제 주문 내역은 계정 쪽 자료와 맞춰 봐야 말할 수 있습니다. 한 계정을 여러 기기에서 쓸 수 있어서, 계정의 주문 내역이 곧 이 기기에서 한 주문이라고 쓰지도 않습니다.

보고서에는 "쿠팡에서 물건을 샀다" 가 아니라 "이 시간대에 com.coupang.mobile 화면이 앞에 나온 기록과 이 앱의 알림 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

앱 내부 시각 칸의 기준은 확인하지 못했습니다. 숫자 모양으로 기준을 가늠하는 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md)에 있습니다. 시스템 기록의 시각을 읽을 때는 기기의 시간대부터 [시간대와 시각 설정](../system-account/time-zone.md)에서 확인합니다.

## 함정과 한계

**패키지 이름이 겹칩니다.** com.coupang.mobile 은 쿠팡이츠 패키지 com.coupang.mobile.eats 의 앞부분과 같아서, "com.coupang.mobile" 로 그냥 찾으면 쿠팡이츠 줄까지 섞여 나옵니다. 패키지 이름 바로 뒤에 공백이 오는 줄만 고르는 식으로 정확히 걸러야 두 앱을 나눌 수 있습니다. 아래 "직접 분석해 보기" 의 명령이 이렇게 거릅니다.

**공개 도구에 전용 모듈이 없습니다.** ALEAPP 의 scripts/artifacts 폴더 519개 항목 가운데 이름에 coupang 이 들어간 파일이 없고, CARPE(GitHub 조직 dfrc-korea)의 modules 폴더 80개 항목에도 쿠팡 이름이 붙은 모듈이 없습니다. [3][4] CARPE 의 android_user_apps 폴더 안에 이 앱을 다루는 코드가 있는지는 열어 보지 못했습니다. 도구 결과에 쿠팡이 안 나오면 앱 폴더를 직접 엽니다.

**웹뷰 추정을 사실로 쓰지 않습니다.** 앱 폴더에서 웹 캐시로 보이는 파일이 나오면 그때 그 파일로 확인한 만큼만 씁니다.

## 직접 분석해 보기

**헥스로 한 번.** 이 앱의 파일 형식을 설명한 공개 명세를 찾지 못해서 명세로 만든 헥스 예시를 싣지 않습니다. 앱 폴더를 확보했다면 파일마다 앞부분을 헥스로 열어 형식을 알려 주는 머리 바이트를 확인하고, 그 형식의 기반 구조 페이지로 넘어갑니다.

**명령으로 한 번.** 앱 사용 기록을 쿠팡 쇼핑 앱 줄만 남기도록 거릅니다. 관찰 기기의 앱 사용 기록 줄은 package 칸 값 다음에 공백과 class 같은 다음 칸이 이어지는 모양이었고, dumpsys notification 출력의 NotificationRecord 줄도 pkg 칸 값 다음에 공백과 user 칸이 이어졌습니다.

```
adb shell "dumpsys usagestats | grep 'package=com.coupang.mobile '"
adb shell "dumpsys notification | grep -A 3 'pkg=com.coupang.mobile '"
```

찾는 말 끝에 공백을 하나 붙여 두어서 두 명령 모두 com.coupang.mobile.eats 줄은 거르고 쇼핑 앱 줄만 남깁니다. 다른 판의 기기에서 줄 모양이 달라 결과가 비면 공백을 빼고 넓혀 찾은 다음 쿠팡이츠 줄을 눈으로 빼냅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 내용 |
|---|---|
| [설치된 앱](../app-usage/packages/index.md) | 설치된 적이 있는지, 언제 설치·업데이트됐는지 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 화면이 앞에 나온 시간대 |
| [알림 기록](../app-usage/notification-history.md) | 주문·배송 알림이 올라온 시각 |
| [계정](../system-account/accounts/index.md) | 기기에 등록된 계정 |
| [데이터 사용량](../network/netstats.md) | 그 시간대에 이 앱이 주고받은 데이터 양 |
| [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) | 계정 쪽 주문 내역을 받는 방법 |

앱을 쓴 시간대를 따지는 조사라면 [어떤 앱을 언제 썼나](../../04-scenarios/activity/app-usage.md)를 함께 봅니다.

## 실습

공개 검체 가운데 쿠팡이 설치된 것이 있는지는 확인하지 못했습니다. 검체를 고른 다음 설치 기록에서 패키지 이름을 찾는 일부터 시작합니다.

1. 검체의 설치된 앱 기록에서 "com.coupang" 으로 찾으면 패키지가 몇 개 나오고, 각각 어떤 앱인가?
2. 앱 사용 기록을 "com.coupang.mobile" 로만 거른 결과와 위 명령처럼 정확히 거른 결과는 줄 수가 얼마나 다른가?
3. 알림 기록에 이 앱의 알림이 남아 있다면 channel 칸에 나오는 값은 몇 가지이고, 주문·배송 안내로 보이는 채널은 어느 것인가?
4. 앱 비공개 폴더를 확보했다면 웹 캐시로 보이는 폴더가 있는가, 있다면 어떤 형식의 파일이 들어 있는가?

## 참고 문헌

1. 쿠팡(Coupang)-모바일 쇼핑 - Google Play 앱 (com.coupang.mobile). https://play.google.com/store/apps/details?id=com.coupang.mobile&hl=ko
2. 쿠팡이츠 - 와우회원 배달비 0원 - Google Play 앱 (com.coupang.mobile.eats). https://play.google.com/store/apps/details?id=com.coupang.mobile.eats&hl=ko
3. abrignoni/ALEAPP — scripts/artifacts 폴더 목록(GitHub API, 519개 항목). https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
4. dfrc-korea/carpe — modules 폴더 목록(GitHub API, 80개 항목). https://api.github.com/repos/dfrc-korea/carpe/contents/modules
