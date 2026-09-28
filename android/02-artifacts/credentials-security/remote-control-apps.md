---
title: "원격 제어 앱"
parent: "아티팩트 · 자격 증명·보안 설정"
nav_order: 1275
---

# 원격 제어 앱 (TeamViewer·AnyDesk·AirDroid)

범죄 조직이 메신저로 피해자에게 TeamViewer·AnyDesk·AirDroid 같은 원격 제어 앱을 깔게 한 뒤 개인정보를 빼내 금융 사기에 쓰는 일이 늘고 있습니다 [1]. 이런 앱으로 화면을 넘기려면 화면 녹화 동의가 필요하고, 조작까지 넘기려면 대개 따로 까는 추가 앱의 접근성 서비스를 켜야 합니다 [3][4][5][7][9]. 그래서 조사에서는 설치된 패키지, 앱 전용 폴더의 로그, 접근성 설정, 앱 작업(AppOps) 접근 기록을 함께 봅니다.

## 무엇을 기록하나 · 왜 생기나

세 앱 모두 안드로이드 쪽에서 원격 연결을 받으려면 비슷한 단계를 거칩니다. TeamViewer QuickSupport 는 다른 앱 위에 표시(Display over other apps) 권한을 받은 뒤 앱을 열면 TeamViewer ID 를 보여 주고, 사용자가 이 ID 를 상대에게 알려 주면 상대가 연결을 요청합니다 [3]. 요청이 오면 사용자가 허용(Allow)을 눌러야 하고, 기기에 따라 화면 공유를 시작하는 확인 창에서 지금 시작(Start now)을 한 번 더 눌러야 합니다 [3].

화면 녹화 동의는 안드로이드가 직접 띄우는 창입니다. 앱은 화면 캡처 인텐트로 사용자 동의를 받아야 화면을 넘길 수 있고, Android 14 이상에서는 동의 한 번으로 세션 한 번만 열 수 있습니다 [9]. Android 10 이상에서는 AnyDesk 에 무인 접속(Unattended Access)을 설정해 두어도 화면 공유나 녹화를 시작할 때 시스템 확인 창이 뜰 수 있습니다 [5]. Android 15 QPR1 이상에서는 화면 공유·녹화가 이어지는 동안 상태 표시줄에 큰 표시가 뜹니다 [9].

화면을 보는 것과 조작하는 것은 따로입니다. 많은 안드로이드 기기에서 AnyDesk 로 조작까지 하려면 제어 플러그인 (Control Plugin) 이라는 추가 앱을 깔고, 필요하면 설정 → 접근성에서 켜야 합니다 [5]. 범용 플러그인 `ad1` 은 Play 스토어에서 받고, 일부 기기는 제조사 전용 플러그인을 씁니다 [5]. TeamViewer 는 전용 추가 앱이 없는 기기에 범용 추가 앱(Universal Add-On)을 깔아 접근성 메뉴에서 "Universal add-on accessibility service" 를 켜게 합니다 [4]. AirDroid 도 조작하려는 기기에서 AirDroid 계정으로 로그인한 뒤 AirDroid Control Add-on 을 깔고 접근성에서 켜야 하며, 이 방식은 Android 7 이상에서 씁니다 [7]. 그래서 원격 조작까지 받도록 설정한 기기에는 본 앱과 추가 앱 두 패키지가 함께 있는 경우가 많습니다. 다만 AirDroid 는 추가 앱 대신 USB 로 PC 에 연결해 Non-root 권한을 주는 방법으로도 원격 제어를 켤 수 있습니다 [8].

## 위치와 버전별 차이

### 패키지 이름

| 앱 | 패키지 이름 | 역할 |
|---|---|---|
| TeamViewer QuickSupport | `com.teamviewer.quicksupport.market` [10] | 지원을 받는 쪽. ID 를 띄움 [3] |
| TeamViewer Host | `com.teamviewer.host.market` [11] | 무인 원격 제어용 [11] |
| TeamViewer Remote Control | `com.teamviewer.teamviewer.market.mobile` [12] | 다른 기기에 접속하는 쪽 [12] |
| TeamViewer Universal Add-On | `com.teamviewer.quicksupport.addon.universal` [13] | QuickSupport 조작용 접근성 서비스, Android 7 이상 [4] |
| AnyDesk | `com.anydesk.anydeskandroid` [14] | 연결을 받고 거는 앱 [5] |
| AnyDesk 플러그인 ad1 | `com.anydesk.adcontrol.ad1` [15] | 조작용 범용 플러그인 [5] |
| AirDroid Personal | `com.sand.airdroid` [16] | 조작당하는 기기에 까는 앱 [8] |
| AirMirror | `com.sand.airmirror` [17] | 다른 폰에서 안드로이드 기기를 조작하는 앱 [8] |

피해자 폰에서 먼저 찾을 것은 연결을 받는 쪽 앱과 그 추가 앱입니다. AnyDesk 사용자 지정 클라이언트는 고유한 패키지 이름을 쓸 수 있고 [5] 제조사 전용 플러그인도 이름이 다를 수 있으므로, 위 표에 없는 이름도 `teamviewer`, `anydesk`, `airdroid`, `sand.` 같은 글자로 패키지 목록을 한 번 더 찾습니다.

### 앱이 남기는 파일

TeamViewer Remote Control·Host·QuickSupport 는 로그 파일을 공용 저장 공간의 `Android/data/<패키지 이름>/files` 에 둡니다 [2]. QuickSupport 는 `/Android/data/com.teamviewer.quicksupport.market/files/`, Host 는 `/Android/data/com.teamviewer.host.market/files/` 입니다 [2]. 앱 화면에서는 QuickSupport·Host 가 점 세 개 메뉴 → Advanced → Log files, Remote Control 이 점 세 개 메뉴 → Settings → Log files 로 같은 로그를 엽니다 [2].

AnyDesk 는 연결 요청을 받으면 `connection_trace.txt` 를 만들고, 여기에 연결 날짜와 시각, 연결을 받아들였는지 거절했는지, 누가 요청했는지를 적습니다 [6]. 이 파일은 AnyDesk 설정 파일과 같은 폴더에 있습니다 [6]. 앱 안에서는 About AnyDesk → Open AnyDesk Log 로 로그를 볼 수 있고, 지원용 추적 파일(trace file)을 메일로 보내는 메뉴도 있습니다 [5]. 안드로이드에서 `connection_trace.txt` 와 로그 파일이 있는 폴더는 내부 앱 폴더와 `Android/data/com.anydesk.anydeskandroid` 를 파일 이름으로 검색해 찾습니다.

AirDroid 는 조작당하는 기기에서 AirDroid 계정으로 로그인해야 원격 제어를 쓸 수 있고 [7][8], 조작하는 쪽 PC 프로그램이나 웹도 같은 계정으로 로그인합니다 [8]. 그래서 피해자 폰의 AirDroid 에 로그인된 계정이 누구 것인지가 조사의 단서가 됩니다.

세 앱 모두 내부 앱 폴더(`/data/data/<패키지 이름>`)에도 설정과 데이터가 남습니다. 앱 폴더의 짜임은 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 페이지에 있습니다.

### 버전별 차이

| 범위 | 차이 |
|---|---|
| Android 7 이상 | TeamViewer 범용 추가 앱, AirDroid Control Add-on, AnyDesk 원격 조작을 쓸 수 있음 [4][5][7] |
| Android 10 이상 | 무인 접속이어도 화면 공유 시작 때 시스템 확인 창이 뜰 수 있음 (AnyDesk 안내) [5] |
| Android 14 이상 | 화면 캡처 동의 한 번에 세션 한 번 [9]. 앱 작업 접근 기록이 `appops_accesses.xml` 로 나뉨 [18] |
| Android 15 QPR1 이상 | 화면 공유 중 상태 표시줄 표시 [9] |
| AnyDesk 7.2.0 이상 | 권한 설정 점검 목록(Setup Checklist) [5] |

## 구조

### 앱 작업 접근 기록

원격 제어 앱이 화면을 넘기거나 다른 앱 위에 창을 띄우거나 접근성 서비스에 붙으면, 앱 작업 서비스가 그 작업의 접근 시각을 남길 수 있습니다. 원격 제어와 관련된 작업 번호는 아래 세 가지입니다 [18].

| 작업 번호 | 이름 | 원격 제어와의 관계 |
|---|---|---|
| 24 | `SYSTEM_ALERT_WINDOW` | 다른 앱 위에 표시. QuickSupport 가 요구 [3] |
| 46 | `PROJECT_MEDIA` | 화면 캡처(화면 공유) |
| 73 | `BIND_ACCESSIBILITY_SERVICE` | 접근성 서비스 연결 |

Android 14 이상에서는 `/data/system/appops_accesses.xml` 에 `pkg`(패키지) → `uid` → `op`(작업 번호) → `st` 순서로 기록이 들어 있고, `st` 요소의 `t` 는 접근 시각, `r` 은 거부 시각, `d` 는 접근이 이어진 시간(밀리초)입니다 [18]. `st` 의 `n` 값에는 접근할 때 앱 상태와 호출 방식이 함께 담겨 있어서, 앱이 화면 맨 앞(TOP)에 있을 때 쓴 것인지 뒤에서 쓴 것인지 나눌 수 있습니다 [18]. 파일 형식과 Android 13 이하의 `appops.xml` 은 [권한 사용 기록](../app-usage/packages/permission-usage.md) 페이지에서 다룹니다.

아래는 모양만 보여 주려고 만든 예시입니다. `n="429496729601"` 은 앱 상태 TOP(200)을 31비트 왼쪽으로 옮기고 SELF(1) 를 더한 값입니다 [18].

```xml
<!-- (만든 예시) -->
<pkg n="com.teamviewer.quicksupport.market">
  <uid n="10321">
    <op n="46">
      <st n="429496729601" t="1767225600000" d="1500000" />
    </op>
  </uid>
</pkg>
```

이 예시라면 `t` 값 1767225600000 은 2026-01-01 00:00:00 UTC 이고, `d` 값은 25분입니다.

### 접근성 설정

추가 앱의 접근성 서비스가 켜져 있으면 settings secure 의 `enabled_accessibility_services` 에 그 서비스가 남습니다. 키 목록과 읽는 법은 [기기 관리자와 접근성 권한](device-admin-accessibility.md) 페이지에 있습니다.

## 증거로서 의미

**증명하는 것**

본 앱과 추가 앱이 함께 깔려 있고 추가 앱의 접근성 서비스가 켜져 있으면, 그 기기가 원격 화면 보기뿐 아니라 원격 조작까지 받을 수 있게 설정돼 있었다는 뜻입니다 [4][5][7]. 접근성 서비스와 화면 녹화 동의는 모두 기기에서 사람이 직접 허용해야 하므로 [4][5][7][9], 이 설정이 있으면 누군가 기기 화면에서 허용 단계를 거쳤다고 볼 수 있습니다. `appops_accesses.xml` 의 작업 46 에 접근 시각이 있으면 그 앱이 그 시각에 화면 캡처 작업을 했다는 기록이 됩니다 [18]. AnyDesk 의 `connection_trace.txt` 가 남아 있으면 연결 요청 시각, 수락·거절, 요청한 쪽을 연결마다 알 수 있습니다 [6].

앱에 남은 로그인 계정 정보나 닉네임 설정은 범인을 추정하는 단서가 됩니다 [1].

**증명하지 못하는 것**

원격 제어 앱이 깔려 있다는 사실만으로 원격 연결이 있었다고 할 수 없고, 연결이 있었다는 사실만으로 상대가 무엇을 봤거나 조작했는지를 알 수는 없습니다. 상대 ID 는 상대 기기의 앱을 가리키는 값이라서 그 앱을 쓴 사람이 누구인지는 따로 밝혀야 합니다. `appops_accesses.xml` 은 작업마다 최근 접근 시각을 적어 두는 파일이라서 [18], 원격 세션이 몇 번 있었는지 모두 알 수는 없습니다. 반대로 접근성 서비스가 꺼져 있어도 조작이 없었다고 할 수 없습니다. 일부 Samsung·Vivo 기기는 화면이 잠기면, Xiaomi·Huawei 기기는 AirDroid 를 닫으면 접근성 권한이 꺼집니다 [7]. 원격 제어 앱은 원래 원격 지원용이라서 깔려 있다고 곧 범죄에 쓰였다는 뜻도 아닙니다 [1].

## 시각 해석

`appops_accesses.xml` 의 `t`·`r` 은 Unix 밀리초이고 UTC 기준입니다 [18]. 이 파일은 변경 뒤 최대 30분 늦게 쓰는 방식이라서 [18], 확보 직전의 접근은 빠져 있을 수 있습니다. 설치 시각은 [설치 출처와 설치 시각](../app-usage/packages/install-source-time.md) 페이지의 방법으로 읽습니다.

TeamViewer 로그와 AnyDesk `connection_trace.txt` 의 시각이 UTC 인지 기기 시간대인지는 파일 안 시각을 설치 시각이나 앱 작업 기록처럼 기준이 분명한 값과 맞춰 보고 판단합니다. 기기 시간대는 [시간대와 시각 설정](../system-account/time-zone.md), 값 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

## 함정과 한계

첫째, 앱을 지우면 내부 앱 폴더와 `Android/data/<패키지 이름>` 이 함께 지워집니다([앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md)). 범행 뒤 피해자에게 앱을 지우게 했다면 로그 파일은 없고 시스템 쪽 기록만 남을 수 있습니다. `appops_accesses.xml` 에는 확보 때 설치돼 있지 않은 패키지가 남아 있을 수 있어서 [18], 지운 원격 제어 앱을 찾는 단서로 씁니다.

둘째, 본 앱만 보고 추가 앱을 빠뜨리기 쉽습니다. 조작 여부는 추가 앱의 접근성 설정으로 판단하므로 두 패키지를 함께 봅니다.

셋째, 앱 로그의 파일 이름과 형식은 앱 버전마다 다를 수 있으므로 폴더 안 파일을 모두 확보한 뒤 상대 ID·시각이 적힌 줄을 찾습니다.

## 직접 분석해 보기

### 파일로 한 번

1. 전체 파일 시스템 사본에서 `/data/system/appops_accesses.xml`(Android 14 이상) 또는 `appops.xml` 을 꺼냅니다. 파일이 텍스트로 열리지 않으면 [안드로이드 바이너리 XML (ABX)](../../01-foundations/data-formats/abx.md) 페이지 방법으로 풉니다.
2. 위 패키지 이름으로 `pkg` 요소를 찾고, 작업 24·46·73 의 `st` 에서 `t`·`r`·`d` 를 적습니다.
3. 공용 저장 공간의 `Android/data/<패키지 이름>/files` 와 내부 앱 폴더를 확보해 로그 파일을 모두 엽니다. 앱 화면에서 본 상대 ID, 계정 메일 주소, 닉네임이 있으면 그 문자열로 `shared_prefs`·`databases` 를 검색해 어느 파일에 있는지 확인합니다.

### 공개 도구로 한 번

ALEAPP 의 appOpsAccesses 모듈은 `appops_accesses.xml` 을 읽어 접근 시각·거부 시각·패키지·작업 이름·앱 상태를 표로 내놓습니다 [18]. 결과를 원격 제어 앱 패키지로 거르고, 실행 중인 기기라면 `dumpsys appops` 출력과 맞춰 봅니다([dumpsys 출력](../logs/dumpsys.md)).

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [통화 기록](../communications/call-log.md) | 설치 직전에 걸려 온 전화와 통화 길이 |
| [문자](../communications/messages/index.md) | 설치 링크나 앱 이름이 든 문자 |
| [설치 출처와 설치 시각](../app-usage/packages/install-source-time.md) | 본 앱과 추가 앱의 설치 시각, 설치한 앱 |
| [권한 사용 기록](../app-usage/packages/permission-usage.md) | 작업 24·46·73 의 접근 시각 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 원격 제어 앱과 은행 앱이 화면에 올라온 순서 |
| [알림 기록](../app-usage/notification-history.md) | 원격 제어 앱이 띄운 알림 |
| [기기 관리자와 접근성 권한](device-admin-accessibility.md) | 추가 앱의 접근성 서비스가 켜져 있는지 |

조사 흐름은 [스미싱 흔적](../../04-scenarios/incident/smishing.md), [악성 앱은 어디서 들어왔나](../../04-scenarios/incident/initial-access.md), [몰래 설치된 감시 앱](../../04-scenarios/incident/stalkerware.md) 에서 다루고, 모든 시각을 한 줄로 합치는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 이미지에서 아래 질문을 풀어 봅니다.

1. 패키지 목록에 위 표의 패키지나 `teamviewer`·`anydesk`·`airdroid` 가 들어간 패키지가 있습니까? 본 앱과 추가 앱이 함께 있습니까?
2. `enabled_accessibility_services` 에 추가 앱의 서비스가 있습니까?
3. `appops_accesses.xml` 에서 그 패키지의 작업 46 접근 시각은 언제이고, 그때 앱 상태는 무엇입니까?
4. `Android/data` 아래 그 패키지 폴더에 로그 파일이 있다면, 상대 ID 와 연결 시각이 적힌 줄은 어디입니까?

## 참고 문헌

1. 박현재·손태식, "원격 제어용 어플리케이션에서의 아티팩트 수집 및 분석", 디지털포렌식연구 18(1), 46–62, 2024 — https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE11750873
2. Find your log files — TeamViewer Knowledge Base — https://www.teamviewer.com/en-us/global/support/knowledge-base/teamviewer-remote/contact-support/find-your-log-files/
3. Remote control an Android device via attended access — TeamViewer Knowledge Base — https://www.teamviewer.com/en-us/global/support/knowledge-base/teamviewer-classic/mobile/android/remote-control-an-android-device-via-attended-access/
4. Universal add-on for Android — TeamViewer Knowledge Base — https://www.teamviewer.com/en-us/global/support/knowledge-base/teamviewer-classic/mobile/android/universal-add-on-for-android/
5. AnyDesk for Android / ChromeOS — AnyDesk Documentation — https://support.anydesk.com/docs/anydesk-for-android
6. What are Trace Files? — AnyDesk Documentation — https://support.anydesk.com/docs/what-are-trace-files
7. How to Control Android devices through AirDroid Control Add-on (Accessibility)? — AirDroid Support Center — https://help.airdroid.com/hc/en-us/articles/4405983257243-How-to-Control-Android-devices-through-AirDroid-Control-Add-on-Accessibility
8. How to remote control Android device from a computer with AirDroid Personal? — AirDroid Support Center — https://help.airdroid.com/hc/en-us/articles/360004121114-How-to-remote-control-Android-device-from-a-computer-with-AirDroid-Personal
9. Media projection — Android Developers — https://developer.android.com/media/grow/media-projection
10. TeamViewer QuickSupport — Google Play — https://play.google.com/store/apps/details?id=com.teamviewer.quicksupport.market
11. TeamViewer Host — Google Play — https://play.google.com/store/apps/details?id=com.teamviewer.host.market
12. TeamViewer Remote Control — Google Play — https://play.google.com/store/apps/details?id=com.teamviewer.teamviewer.market.mobile
13. TeamViewer Universal Add-On — Google Play — https://play.google.com/store/apps/details?id=com.teamviewer.quicksupport.addon.universal
14. AnyDesk Remote Desktop — Google Play — https://play.google.com/store/apps/details?id=com.anydesk.anydeskandroid
15. AnyDesk plugin ad1 — Google Play — https://play.google.com/store/apps/details?id=com.anydesk.adcontrol.ad1
16. AirDroid: File & Remote Access — Google Play — https://play.google.com/store/apps/details?id=com.sand.airdroid
17. AirMirror: Remote control — Google Play — https://play.google.com/store/apps/details?id=com.sand.airmirror
18. appOpsAccesses.py — ALEAPP — https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/appOpsAccesses.py
