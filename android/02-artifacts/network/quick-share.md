---
title: "파일 공유"
parent: "아티팩트 · 네트워크·연결"
nav_order: 810
---

# 파일 공유 (Quick Share·Nearby Share)

## 한 줄 요약

Quick Share 는 가까운 기기끼리 블루투스와 Wi-Fi 로 파일을 주고받는 기능이고, 전송 기록 파일의 위치와 구조는 공개 자료로 확인되지 않아서 받은 파일, 설정 값, 알림·앱 사용 기록처럼 둘레에 남는 흔적으로 전송을 짐작합니다.

## 무엇을 기록하나 · 왜 생기나

Google 의 Quick Share 는 이전 이름이 Nearby Share 이고, Android 6 이상에서 쓸 수 있습니다[1]. 주고받으려면 양쪽 기기 모두 블루투스를 켜야 하고, Android 12 이하에서는 위치도 켜야 하며, iPhone·iPad·Mac 과 주고받을 때는 Wi-Fi 가 필요합니다[1]. 조사하는 쪽에서 보면 블루투스·위치·Wi-Fi 설정과 기록이 전송 시점 전후로 함께 움직일 수 있다는 뜻이라서, 이 페이지는 그 둘레 흔적을 모으는 데 초점을 둡니다.

받는 쪽이 누구에게 보일지는 공개 범위로 정합니다. 선택지는 내 기기(Your devices), 연락처(Contacts), 10분 동안 모두(Everyone for 10 minutes) 셋이고, "10분 동안 모두" 는 10분이 지나면 이전 설정으로 저절로 돌아갑니다[1]. 받은 파일은 기본 파일 앱에서 Downloads 안의 Quick Share 폴더에서 볼 수 있고, 보내는 화면을 벗어나면 알림 창에 전송 상태 알림이 떠서 진행 상황을 보거나 취소할 수 있습니다[1].

삼성 갤럭시 기기에는 삼성이 만든 Quick Share 가 따로 있습니다. Google 도움말은 Android 10·One UI 2.1 이상 갤럭시에서는 설정과 기능이 다를 수 있다고 적고 삼성 문서로 넘깁니다[1]. 이름이 같아도 두 기능의 저장 위치가 같다고 보면 안 되고, 두 회사 기능을 언제 어디까지 합쳤는지는 이번 자료로 확인하지 못했습니다.

## 위치와 버전별 차이

| 항목 | Google Quick Share | 삼성 Quick Share |
|---|---|---|
| 대상 | Android 6 이상[1] | Android 10·One UI 2.1 이상 갤럭시[1] |
| 필요한 무선 | 블루투스. Android 12 이하는 위치도. iPhone·iPad·Mac 과는 Wi-Fi[1] | 확인하지 못했습니다 |
| 받은 파일 | 파일 앱의 Downloads 안 Quick Share 폴더[1]. 실제 저장 경로는 확인하지 못했습니다 | 확인하지 못했습니다 |
| 패키지 이름 | 확인하지 못했습니다 | 확인하지 못했습니다 |
| 전송 기록 DB·표·칸 | 확인하지 못했습니다 | 확인하지 못했습니다 |
| 전송 기술(BLE·Wi-Fi Direct 등) 목록 | 도움말에 없습니다 | 확인하지 못했습니다 |

도움말은 파일 앱 화면 기준으로만 설명하므로, 받은 파일이 공용 저장 공간의 어느 폴더에 실제로 놓이는지는 검체에서 직접 찾아야 합니다. 공용 저장 공간의 구조는 [공용 저장 공간](../../01-foundations/storage/shared-storage.md) 에 있습니다. 관찰한 기기의 `/sdcard/Download` 아래에는 항목 151 개와 폴더 36 개가 있었지만 폴더 이름을 가려 두어서 "Quick Share" 폴더가 있는지는 알 수 없습니다(확인 범위: Android 16, One UI 8.5).

## 구조

전송 기록 파일의 구조는 확인하지 못했으므로, 관찰한 기기에서 이름이 파일 공유와 닿아 있어 보이는 설정 키와 서비스 등록 목록을 정리합니다. 값은 관찰 메모에서 가려져 있어서 뜻과 값 형식은 모두 확인하지 못했습니다(확인 범위: Android 16, One UI 8.5).

| 설정 영역 | 키 이름 |
|---|---|
| Global | `mcf_quick_share_visibility` |
| Secure | `nearby_sharing_component`, `mcf_continuity_nearby_device_state`, `autohotspot_saved_nearby_state` |
| System | `quickshare_enabled`, `direct_share`, `mcf_continuity`, `mcf_family_device_share_enabled`, `mcf_mydevice_activated` |

`quickshare_enabled` 와 `mcf_quick_share_visibility` 는 이름으로 보아 Quick Share 를 켰는지와 공개 범위에 닿아 있을 것으로 짐작하지만, 값을 보지 못했으므로 짐작에 그칩니다. `nearby_sharing_component` 가 어떤 구성 요소를 가리키는지, `mcf_` 로 시작하는 키들이 Quick Share 와 어떤 관계인지도 확인하지 못했습니다. 설정 값을 읽는 법과 파일 위치는 [설정 값](../system-account/settings.md) 에 있습니다.

같은 기기의 `dumpsys bluetooth_manager` 출력에는 "Ble app registered:" 목록이 있고, 여기에 `com.samsung.android.mcfserver`, `com.samsung.android.mcfds`, `com.samsung.android.beaconmanager`, `com.samsung.android.mdx.kit` 가 보였습니다(확인 범위: Android 16, One UI 8.5). BLE 를 쓰려고 등록한 삼성 구성 요소라는 점까지는 출력으로 알 수 있지만, 이 가운데 어느 것이 Quick Share 를 맡는지는 확인하지 못했습니다. 블루투스 쪽 흔적은 [블루투스 장치](bluetooth.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것**

받은 파일이 검체에 남아 있으면 그 파일이 기기에 있었다는 사실과 파일 시스템·미디어 저장소의 시각을 알 수 있습니다. 앱 사용 기록에는 앱 화면이 앞에 나온 때(`ACTIVITY_RESUMED`)와 포그라운드 서비스가 시작·종료한 때(`FOREGROUND_SERVICE_START`, `FOREGROUND_SERVICE_STOP`), 알림이 뜬 때(`NOTIFICATION_INTERRUPTION`, `channelId` 포함)가 남습니다(확인 범위: Android 16, One UI 8.5). 보내는 화면을 벗어나면 전송 상태 알림이 뜨므로[1], 공유를 맡은 패키지를 찾아낸 뒤에는 그 패키지의 알림·서비스 이벤트가 전송 시점의 간접 흔적이 될 수 있습니다.

**증명하지 못하는 것**

설정 키는 확보 시점의 설정 상태만 보여 주고 전송이 있었다는 증거가 되지 못합니다. 공개 범위 "10분 동안 모두" 는 10분 뒤 저절로 돌아가므로[1], 확보 시점의 값으로 사건 당시의 공개 범위를 말할 수 없습니다. Downloads 폴더에 있는 파일은 Quick Share 말고도 브라우저·메신저 등 여러 경로로 들어올 수 있으므로, 폴더 위치만으로 "Quick Share 로 받았다" 고 쓸 수 없습니다. 상대 기기가 누구인지, 무엇을 보냈는지(보낸 쪽 기록)는 이번 자료로 확인한 흔적에서 알 수 없습니다.

보고서에는 "Quick Share 로 파일을 보냈다" 가 아니라 "이 시간대에 이 패키지가 포그라운드 서비스를 시작하고 알림을 띄운 기록이 있고, 같은 시간대에 이 파일이 Download 아래에 생겼다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

전송 기록 자체의 시각 칸은 확인하지 못했으므로 둘레 흔적의 시각을 씁니다. 받은 파일은 파일 시스템 시각과 [미디어 저장소](../media/mediastore/index.md) 의 시각을, 앱 사용과 알림은 [앱 사용 기록](../app-usage/usagestats/index.md) 과 [알림 기록](../app-usage/notification-history.md) 의 시각을 봅니다. 관찰한 기기의 usagestats dump 는 시각이 `time="…"` 칸에 들어 있었지만 값이 가려져 있어 표시 형식과 시간대는 확인하지 못했습니다(확인 범위: Android 16, One UI 8.5). 시각 값 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에, 기기 시간대 확인은 [시간대와 시각 설정](../system-account/time-zone.md) 에 있습니다.

파일을 받은 시각과 파일 시스템에 찍힌 시각이 같은지, 원본 파일의 수정 시각을 넘겨받는지는 이번 자료로 확인하지 못했으니 한 가지 시각에 기대지 말고 여러 흔적을 맞춰 봅니다.

## 함정과 한계

가장 큰 함정은 이름입니다. Google 의 Quick Share(예전 Nearby Share)와 삼성의 Quick Share 는 이름은 같아도 설정과 기능이 다를 수 있다고 Google 도움말이 따로 적고 있으므로[1], 한쪽에서 알아낸 경로나 패키지를 다른 쪽 검체에 그대로 대입하지 않습니다. 설정 키 이름에 `quickshare`, `nearby` 가 들어 있다고 해서 그 키가 어느 쪽 기능의 것인지도 이름만으로는 알 수 없습니다.

관찰한 기기에서 공유 앱의 패키지 이름은 가려져 있어서, usagestats 에 Quick Share 이벤트가 실제로 찍혔는지는 확인하지 못했습니다(확인 범위: Android 16, One UI 8.5). 오래된 전송이라면 둘레 흔적도 남아 있지 않을 수 있으니, 앱 사용 기록이 얼마 동안 남는지는 [앱 사용 기록](../app-usage/usagestats/index.md) 에서 확인합니다.

받은 파일을 사용자가 지우거나 다른 폴더로 옮기면 Download 아래 흔적은 사라지거나 바뀝니다. 지운 파일을 찾는 방법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 를, 흔적을 없애려 한 정황을 판단하는 흐름은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 를 봅니다.

## 직접 분석해 보기

### 출력 모양을 한 번 따라가기

Quick Share 전송 기록의 파일 형식을 확인하지 못해서 헥스로 따라갈 대상은 아직 없습니다. 대신 관찰한 기기의 usagestats dump 에서 알림 이벤트 한 줄의 모양을 옮기면 아래와 같고, 값은 가려진 상태 그대로 둡니다(확인 범위: Android 16, One UI 8.5).

```text
time="…" type=NOTIFICATION_INTERRUPTION package=<패키지> channelId=<값> flags=<값>
time="…" type=FOREGROUND_SERVICE_START package=<패키지> class=<패키지> flags=<값>
time="…" type=FOREGROUND_SERVICE_STOP package=<패키지> class=<패키지> flags=<값>
```

같은 `package` 로 `FOREGROUND_SERVICE_START` 와 `FOREGROUND_SERVICE_STOP` 이 짝을 이루고 그 사이에 알림 줄이 있다면, 그 구간을 전송 후보 시간대로 놓고 받은 파일의 시각과 맞춰 봅니다.

### 공개 도구로 한 번

기기가 켜져 있고 adb 를 쓸 수 있다면 `adb shell settings list global`, `settings list secure`, `settings list system` 으로 위 표의 키를 확인하고, `adb shell dumpsys bluetooth_manager` 로 "Ble app registered:" 목록을, `adb shell dumpsys usagestats` 로 앱 사용 이벤트를 봅니다. 관찰한 기기에서는 이 출력들을 adb 일반 셸 권한으로 읽었습니다(확인 범위: Android 16, One UI 8.5). dumpsys 출력을 다루는 법은 [dumpsys 출력](../logs/dumpsys.md) 에 있고, 공유 앱의 데이터 폴더를 찾아 직접 여는 방법은 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md) 을 봅니다. 공개 분석 도구가 Quick Share 기록을 읽어 주는지는 이번 자료로 확인하지 못했습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 점 |
|---|---|
| [앱 사용 기록](../app-usage/usagestats/index.md) | 공유 앱의 화면·포그라운드 서비스·알림 이벤트 시각 |
| [알림 기록](../app-usage/notification-history.md) | 전송 상태 알림이 남아 있는지 |
| [미디어 저장소](../media/mediastore/index.md) | 받은 파일이 언제 어느 경로로 등록됐는지 |
| [공용 저장 공간](../../01-foundations/storage/shared-storage.md) | Download 아래 실제 폴더 이름과 파일 |
| [블루투스 장치](bluetooth.md) | 전송 시간대에 블루투스가 켜져 있었는지 |
| [와이파이 설정과 접속 기록](wifi.md) | iPhone·iPad·Mac 과 주고받을 때 필요한 Wi-Fi 상태 |
| [설치된 앱](../app-usage/packages/index.md) | 공유를 맡은 패키지가 설치되어 있는지와 버전 |

유선으로 옮긴 경우는 [USB 연결 기록](usb.md) 을, 자료 반출 여부를 묻는 조사 흐름은 [자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 를 봅니다.

## 실습

공개 검체(NIST CFReDS 등)의 안드로이드 이미지를 하나 골라 아래 질문을 풀어 봅니다. 검체에 Quick Share 사용 흔적이 들어 있는지는 확인하지 못했으니 먼저 찾아봅니다.

1. 공용 저장 공간의 Download 아래에 "Quick Share" 라는 이름의 폴더가 있는가? 있다면 그 안의 파일은 언제 생겼는가?
2. 검체의 Settings 에 위 표의 키가 있는가? 없다면 Google 쪽 기능과 삼성 쪽 기능 가운데 어느 쪽 기기로 보이는가?
3. 앱 사용 기록에서 공유를 맡은 것으로 보이는 패키지의 포그라운드 서비스 시작·종료 짝을 찾고, 그 사이에 뜬 알림의 `channelId` 는 무엇인가?
4. 그 시간대에 받은 파일의 시각과 블루투스 기록이 서로 맞는가?

## 참고 문헌

1. Android 도움말 "Share files with Quick Share"(Google) — https://support.google.com/android/answer/9286773?hl=en
