---
title: "테더링과 핫스폿"
parent: "아티팩트 · 네트워크·연결"
nav_order: 780
---

# 테더링과 핫스폿 (Tethering·Hotspot)

## 한 줄 요약

테더링 (Tethering) 은 폰의 모바일 데이터를 다른 기기에 나눠 주는 기능이고 그 가운데 Wi-Fi 로 나눠 주는 방식이 핫스폿 (Hotspot, SoftAP) 이라서, 핫스폿 설정 파일, 데이터 사용량의 테더링 몫, Wi-Fi 상태 기계 기록, 삼성 설정 키를 함께 보면 이 폰이 네트워크를 내어 주는 쪽이었는지와 그 시간대를 추정할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

핫스폿 이름과 비밀번호, 보안 방식 같은 설정은 다음에 다시 켤 때 쓰려고 파일에 남습니다. 현행 AOSP 기준으로 이 설정은 Wi-Fi 설정 저장소의 공유 파일 `WifiConfigStoreSoftAp.xml` 에 있습니다 [3]. Wi-Fi 설정 저장소 전체의 짜임새(공유 파일과 사용자별 파일, 형식 버전)는 [와이파이 설정과 접속 기록 (WifiConfigStore)](wifi.md) 페이지에서 다루고, 이 페이지는 핫스폿 쪽만 봅니다.

설정 파일은 핫스폿을 켜고 끈 이력을 적는 로그가 아닙니다. 켜고 끈 시각은 `dumpsys wifi` 의 상태 기계 기록에, 다른 기기로 넘겨준 데이터 양은 [데이터 사용량 (netstats)](netstats.md) 에 따로 남습니다. 핫스폿에 접속했던 기기 목록(연결 이력)이 파일로 남는지는 공개 자료가 없습니다.

## 위치와 버전별 차이

ALEAPP 는 예전 이진 파일과 지금의 XML 파일을 아래 패턴으로 찾습니다 [1].

| 형식 | ALEAPP 경로 패턴 |
|---|---|
| 예전 이진 형식 | `*/misc/wifi/softap.conf` |
| XML | `*/misc**/apexdata/com.android.wifi/WifiConfigStoreSoftAp.xml` |

`softap.conf` 는 형식 문서가 없는 이진 파일이고, ALEAPP 는 바이트 위치로 SSID 와 비밀번호를 뽑으므로, 파일 모양이 다르면 틀린 값이 나올 수 있습니다 [1]. 어느 Android 버전에서 XML 로 옮겼는지는 실제 기기에 남은 파일로 확인합니다. ALEAPP 가 이 모듈을 시험한 이미지는 Android 10~16 이며 모두 1행씩 나왔습니다 [1].

adb 일반 권한으로 볼 수 있는 핫스폿 관련 흔적은 아래와 같습니다.

| 출처 | 나오는 것 |
|---|---|
| `dumpsys wifi` 지원 기능 | `SupportedFeatures` 에 `WIFI_FEATURE_MOBILE_HOTSPOT` |
| `dumpsys wifi` WifiController 기록 | `what=CMD_SET_AP`, `what=CMD_AP_STOPPED`, `what=CMD_UPDATE_AP_CAPABILITY` 줄, 각 줄에 `num ClientModeManagers`, `num SoftApManagers` |
| `dumpsys batterystats` 배터리 기록 | 줄에 `-wifi_ap` 표시 |
| settings global | `tether_offload_disabled`, `tethered_config_state`, `tethering_data_warning_sim_slot_#`(슬롯별 2개) |

삼성 기기의 settings secure 쪽에는 핫스폿 관련으로 보이는 키가 여러 개 있습니다.

```
wifi_ap_most_recent_password
wifi_ap_security_type
wifi_ap_timeout_setting
wifi_ap_mobile_data_limit
wifi_ap_mobile_data_limit_value
wifi_ap_wifiapwarning_enabled_history
wifi_ap_wifiapwarning_destroyed_history
wifi_ap_disable_random_mac
wifi_ap_guest_settings_val
wifi_ap_smart_tethering_settings
wifi_client_smart_tethering_settings
adv_autohotspot_client_history
adv_autohotspot_mhs_mac_history
autohotspot_saved_state
smart_tethering_db_ver
```

키마다 뜻을 설명한 삼성 문서는 없습니다. 이름으로 보면 `wifi_ap_most_recent_password` 는 핫스폿 비밀번호, `_history` 로 끝나는 키는 켜고 끈 이력이나 접속 이력일 수 있지만, 이름 이상의 해석은 실제 값을 직접 보고 다른 기록과 맞춘 뒤에만 합니다. 설정 키를 읽는 법은 [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) 페이지에 있습니다.

## 구조

XML 파일의 `SoftAp` 요소 아래 필드는 현행 AOSP 기준으로 아래와 같고 [4], 괄호 안은 예전 필드 이름입니다.

| 묶음 | 필드 이름 |
|---|---|
| 이름과 주소 | `WifiSsid`(예전 `SSID`), `Bssid`, `HiddenSSID` |
| 대역과 채널 | `Band`, `Channel`, `BandChannel`, `BandChannelMap`, `ApBand`, `MaxChannelWidth` |
| 보안 | `SecurityType`, `Passphrase`(예전 `Wpa2Passphrase`) |
| 접속 기기 제한 | `MaxNumberOfClients`, `ClientControlByUser`, `BlockedClientList`, `AllowedClientList`, `ClientMacAddress`, `ClientIsolation` |
| 자동 끄기 | `AutoShutdownEnabled`, `ShutdownTimeoutMillis` |
| 폰 쪽 MAC | `MacRandomizationSetting`, 지속 랜덤 MAC 필드 |

`BlockedClientList` 와 `AllowedClientList` 안의 `ClientMacAddress` 에는 사용자가 막거나 허용한 접속 기기의 MAC 주소가 남을 수 있습니다 [4]. 목록이 실제로 채워진 모양은 실제 데이터로 확인합니다.

ALEAPP 는 이 파일에서 SSID, `Passphrase`, `SecurityType` 세 값만 뽑습니다 [1]. 나머지 필드는 파일을 직접 열어 읽어야 합니다.

## 증거로서 의미

**증명하는 것**

핫스폿 설정 파일은 확보 시점에 이 폰에 설정된 핫스폿 이름과 보안 방식을 알려 주고, 차단·허용 목록이 채워져 있다면 사용자가 특정 MAC 주소의 기기를 막거나 허용했다는 기록이 됩니다. [데이터 사용량 (netstats)](netstats.md) 에서 테더링으로 나간 데이터는 특수 UID -5(UID_TETHERING)로 잡히니 [2], 그 행이 있는 구간에 이 폰이 다른 기기에 데이터를 넘겨준 양을 볼 수 있습니다. `dumpsys wifi` 의 `CMD_SET_AP`·`CMD_AP_STOPPED` 줄은 핫스폿을 켜고 끄는 명령이 처리된 시각을 보여 줍니다.

**증명하지 못하는 것**

설정 파일에 핫스폿 이름이 있다고 해서 핫스폿을 실제로 켠 적이 있다는 뜻은 아닙니다. UID -5 사용량으로는 어느 기기가 받아 갔는지, 그 기기에서 무엇을 했는지 알 수 없습니다. 위 기록으로는 핫스폿에 접속한 기기 목록을 복원할 수 없으니, 보고서에는 "이 시간대에 이 폰이 테더링으로 이만큼 데이터를 넘겨준 기록이 있다" 만큼만 씁니다.

## 시각 해석

`dumpsys wifi` 상태 기계 기록의 시각은 `time=MM-DD HH:MM:SS.mmm` 모양이고 연도가 없습니다. 연도는 수집 날짜에서 거꾸로 짐작하고, 시간대는 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 에서 확인합니다. WifiController 기록에는 `total records` 값이 따로 찍히니, 출력에 보이는 `rec[#]` 줄 수와 이 값을 비교해 보이는 줄이 전체 기록의 일부인지 확인합니다. 기록을 몇 개까지 남기는지는 공개 자료가 없으니, 사건 시각의 줄이 없다고 핫스폿을 켜지 않았다고 결론 내리지 않습니다.

netstats 의 UID -5 기록은 구간 시작 시각(유닉스 밀리초)과 구간 길이로 이루어져 있어서 몇 시 몇 분에 켰는지가 아니라 어느 1~2시간 구간에 사용량이 있었는지만 알려 줍니다. 구간 해석은 [데이터 사용량 (netstats)](netstats.md) 페이지를 따릅니다.

`ShutdownTimeoutMillis` 는 이름 그대로 밀리초 단위 시간 길이로 보이고, 시각 값이 아닙니다.

## 함정과 한계

첫째, 설정 파일에는 비밀번호가 평문으로 있을 수 있습니다. ALEAPP 도 `Passphrase` 를 뽑아 보여 주니 [1], 보고서와 공유용 사본에서는 가립니다.

둘째, `softap.conf` 이진 파일은 공식 형식 문서가 없어서 도구가 틀린 값을 낼 수 있습니다 [1]. 도구 결과의 SSID 가 이상하면 헥스로 파일을 열어 글자가 실제로 어디 있는지 확인합니다.

셋째, 배터리 기록의 `-wifi_ap` 표시는 핫스폿 켜짐 상태 표시로 보이지만 뜻을 설명한 공식 문서는 없습니다. 이 표시만으로 핫스폿을 켰다고 쓰지 말고 `dumpsys wifi` 기록이나 netstats UID -5 와 함께 씁니다. 배터리 기록 읽는 법은 [배터리 사용 기록 (batterystats)](../app-usage/batterystats.md) 페이지에 있습니다.

넷째, 연결 종류 번호 4 는 옛 `ConnectivityManager` 상수의 TYPE_MOBILE_DUN 이지만 [2], 이 번호가 테더링 사용량을 뜻한다는 공개 자료는 없습니다. 이 번호를 테더링 사용량으로 읽지 말고, 테더링 몫은 UID -5 로 봅니다.

다섯째, 삼성 설정 키의 이름은 뜻을 짐작하게 하지만 값 형식을 모릅니다. `_history` 키에 목록이 들어 있더라도 무엇의 이력인지 확인하기 전에는 보고서에 해석을 붙이지 않습니다.

## 직접 분석해 보기

### 파일을 직접 한 번

`WifiConfigStoreSoftAp.xml` 사본을 편집기로 열어 `SoftAp` 요소 아래 필드를 위 구조 표와 맞춰 읽습니다. 예전 `softap.conf` 는 이진 파일이라 헥스 편집기로 열고, 형식 문서가 없으니 SSID 로 짐작되는 글자열이 어디서 시작하는지 눈으로 찾아 도구가 뽑은 값과 같은지만 확인합니다. 형식을 모르는 파일에서 바이트 위치를 넘겨짚어 값을 만들지 않습니다.

라이브 기기라면 `dumpsys wifi` 출력에서 핫스폿 명령 줄만 걸러 볼 수 있습니다. 명령은 아래와 같고, 출력을 받는 방법은 [dumpsys 출력 (dumpsys)](../logs/dumpsys.md) 페이지에 있습니다.

```
adb shell dumpsys wifi | grep -E 'CMD_SET_AP|CMD_AP_STOPPED'
```

### 공개 도구로 한 번

ALEAPP 의 `wifiHotspot` 모듈이 두 형식을 찾아 SSID, 비밀번호, 보안 방식을 보여 주고 [1], `netstats` 모듈 결과에서 UID -5 행을 걸러 테더링 사용 구간을 볼 수 있습니다 [2]. 두 도구 결과를 한 시간축에 놓는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md) 페이지에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [데이터 사용량 (netstats)](netstats.md) | UID -5 사용량이 있는 구간 |
| [dumpsys 출력 (dumpsys)](../logs/dumpsys.md) | `CMD_SET_AP`·`CMD_AP_STOPPED` 줄의 시각이 UID -5 구간과 겹치는지 |
| [배터리 사용 기록 (batterystats)](../app-usage/batterystats.md) | `wifi_ap` 표시가 바뀐 시각 |
| [와이파이 설정과 접속 기록 (WifiConfigStore)](wifi.md) | 같은 시간대에 이 폰이 다른 Wi-Fi 에 붙어 있었는지 |
| [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) | 삼성 `wifi_ap_` 키 값이 설정 파일과 같은지 |

다른 기기로 데이터를 넘긴 정황을 따지는 흐름은 [자료를 밖으로 보냈나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 시험 이미지에서 아래 질문을 풀어 봅니다.

1. 핫스폿 설정이 `softap.conf` 와 `WifiConfigStoreSoftAp.xml` 가운데 어느 형식으로 남아 있습니까?
2. 핫스폿 이름과 보안 방식은 무엇이고, 비밀번호 필드는 평문입니까?
3. `BlockedClientList` 나 `AllowedClientList` 에 MAC 주소가 있습니까?
4. netstats 에 UID -5 행이 있습니까? 있다면 가장 많은 데이터가 나간 구간은 언제입니까?

## 참고 문헌

1. ALEAPP — scripts/artifacts/wifiHotspot.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/wifiHotspot.py
2. ALEAPP — scripts/artifacts/netstats.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/netstats.py
3. AOSP packages/modules/Wifi — WifiConfigStore.java (main) — https://android.googlesource.com/platform/packages/modules/Wifi/+/refs/heads/main/service/java/com/android/server/wifi/WifiConfigStore.java
4. AOSP packages/modules/Wifi — XmlUtil.java (main) — https://android.googlesource.com/platform/packages/modules/Wifi/+/refs/heads/main/service/java/com/android/server/wifi/util/XmlUtil.java
