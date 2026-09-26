---
title: "USB 연결 기록"
parent: "아티팩트 · 네트워크·연결"
nav_order: 800
---

# USB 연결 기록 (USB)

## 한 줄 요약

안드로이드에는 "언제 어느 PC 에 USB 로 꽂았다" 를 한곳에 모아 두는 파일이 따로 없고, USB 디버깅(ADB)을 허용한 PC 의 키와 마지막 연결 시각, 앱이 받은 USB 기기 접근 권한, 메모리 안의 연결 기록과 로그처럼 흩어진 흔적을 모아 USB 사용을 짐작합니다.

## 무엇을 기록하나 · 왜 생기나

USB 연결은 방향이 둘입니다. 휴대폰을 PC 에 꽂으면 휴대폰이 USB 장치 쪽이 되고, AOSP 에서는 `UsbDeviceManager` 가 이 경우를 맡습니다. 거꾸로 휴대폰에 USB 메모리·키보드 같은 기기를 꽂으면(OTG) 휴대폰이 호스트가 되고, 이때는 `UsbHostManager` 가 맡습니다[1][2]. 두 경우에 남는 흔적이 서로 다르므로 조사 질문이 "PC 에 연결했나" 인지 "휴대폰에 무엇을 꽂았나" 인지부터 나눠 두는 편이 좋습니다.

휴대폰이 장치 쪽일 때는 파일 전송(MTP)·사진 전송(PTP)·USB 테더링(RNDIS·NCM)·MIDI·ADB 같은 USB 기능 가운데 무엇을 켰는지가 시스템 속성과 커널 상태로 바뀌고, 연결 상태는 `DISCONNECTED`, `CONNECTED`, `CONFIGURED` 로 움직입니다[1]. `UsbDeviceManager` 는 이 변화를 "UsbDeviceManager activity" 라는 이름의 기록에 최대 200 줄까지 적습니다. 이 기록은 메모리 안에만 있어서 dump 출력으로만 볼 수 있고, 파일로는 남지 않습니다[1]. PC 연결 시각이 영구히 남는 위치를 밝힌 공개 자료도 없습니다.

휴대폰이 호스트일 때는 `UsbHostManager` 가 연결과 분리를 `ConnectionRecord` 로 최대 32 개까지 메모리에 쌓습니다[2]. 이 기록도 파일로 쓰지 않아서 재부팅하면 사라지고, 기기를 꽂을 때 로그캣에 기기 정보가 한 줄 남습니다[2].

오래 남는 흔적은 두 가지 경로에서 생깁니다. PC 에서 USB 디버깅을 쓰려고 "항상 허용" 을 누르면 `AdbDebuggingManager` 가 그 PC 의 공개키를 파일에 적고, 마지막 연결 시각도 따로 적습니다[4]. 앱이 특정 USB 기기에 계속 접근하도록 허락을 받으면 `UsbUserPermissionManager` 가 그 영구 권한을 사용자별 XML 파일에 적습니다[3].

## 위치와 버전별 차이

아래 경로와 이름은 AOSP main 브랜치 기준입니다. 판마다 다를 수 있어 실제 기기에서 확인합니다.

| 흔적 | 위치 | 남는 기간 | 근거 |
|---|---|---|---|
| ADB 허용 키 | `/data/misc/adb/adb_keys` | 파일 | [4] |
| ADB 키별 마지막 연결 시각, 무선 디버깅 신뢰 네트워크 | `/data/misc/adb/adb_temp_keys.xml` | 파일 | [4] |
| 시스템 이미지에 들어 있는 ADB 키 | `/adb_keys` | 파일(시스템 영역) | [4] |
| 앱의 USB 기기·액세서리 영구 권한 | `/data/system/users/<사용자ID>/usb_permissions.xml` | 파일 | [3] |
| 화면 잠금 해제 상태에서 쓸 USB 기능 | `/data/system_de/0/UsbDeviceManagerPrefs.xml`, 키 `usb-screen-unlocked-config-%d` | 파일 | [1] |
| PC 연결 상태 변화 기록 | 메모리("UsbDeviceManager activity", 200 줄) | 재부팅까지 | [1] |
| OTG 연결·분리 기록 | 메모리(`ConnectionRecord`, 32 개) | 재부팅까지 | [2] |
| USB 관련 설정 값 | Settings Global·Secure·System | 파일 |  |

`usb_permissions.xml` 경로의 사용자 ID 폴더는 기기 사용자마다 따로 있으므로, 보안 폴더나 작업 프로필이 있는 기기라면 사용자 폴더를 모두 봅니다. 사용자 번호를 읽는 법은 [사용자와 프로필](../system-account/users-profiles.md) 에 있습니다.

삼성 기기의 Settings 에는 AOSP 에 없는 아래 키도 있습니다. 뜻을 밝힌 공개 자료가 없는 키가 많아 값은 실제 데이터로 확인해야 합니다.

| 설정 영역 | 키 이름 | 뜻 |
|---|---|---|
| Global | `adb_enabled`, `adb_wifi_enabled` | 이름은 USB 디버깅·무선 디버깅과 맞습니다. 값 형식은 실제 데이터로 확인 |
| Global | `adb_allowed_connection_time` | AOSP 의 `Settings.Global.ADB_ALLOWED_CONNECTION_TIME`, 곧 ADB 연결 허용 기간 설정입니다[4]. 기본값은 실제 기기에서 확인 |
| Global | `usb_mass_storage_enabled` | 공개 자료 없음 |
| Global | `tethered_config_state`, `tether_offload_disabled` | 테더링 쪽 키이고 [테더링과 핫스폿](tethering-hotspot.md) 에서 다룹니다 |
| Secure | `block_usb_lock`, `usb_audio_automatic_routing_disabled` | 삼성 키로 보입니다. 뜻은 공개 자료 없음 |
| Secure | `rampart_blocked_adb_cmd`, `rampart_snapshot_adb_enabled`, `rampart_snapshot_adb_wifi_enabled` | 삼성 키로 보입니다. 뜻은 공개 자료 없음 |
| System | `enable_mtp_settings` | 삼성 키로 보입니다. 뜻은 공개 자료 없음 |

설정 값을 읽는 법과 파일 위치는 [설정 값](../system-account/settings.md) 에 모아 두었습니다.

## 구조

### adb_keys

`adb_keys` 는 "항상 허용" 을 누른 PC 의 공개키를 한 줄에 하나씩 적는 텍스트 파일입니다[4]. 키 한 줄이 곧 신뢰한 호스트 하나이므로 줄 수를 세면 허용한 PC 의 수를 어림할 수 있습니다.

### adb_temp_keys.xml

같은 폴더의 `adb_temp_keys.xml` 에는 키마다 마지막 연결 시각이 들어 있고, 무선 디버깅에서 신뢰한 네트워크의 BSSID 도 함께 들어 있습니다[4].

| 태그 | 속성 | 뜻 |
|---|---|---|
| `keyStore` | `version` | 파일 전체를 감싸는 태그 |
| `adbKey` | `key`, `lastConnection` | 공개키와 그 키로 마지막으로 연결한 시각(유닉스 밀리초) |
| `wifiAP` | `bssid` | 무선 디버깅에서 신뢰한 네트워크의 BSSID |

이 파일은 `Xml.resolveSerializer()` 로 쓰여서, 기기 설정에 따라 텍스트 XML 로도 [안드로이드 바이너리 XML](../../01-foundations/data-formats/abx.md)(ABX)로도 저장될 수 있습니다[4]. 열었을 때 글자가 깨져 보이면 ABX 로 풀어 봅니다.

### usb_permissions.xml

루트 태그 `permissions` 아래에 `permission` 항목이 앱마다 있고, 그 안에 `usb-device` 나 `usb-accessory` 가 들어갑니다[3]. 이 파일도 `Xml.resolveSerializer()` 로 쓰므로 ABX 로 저장될 수 있습니다[3].

| 태그 | 속성 | 뜻 |
|---|---|---|
| `permission` | `uid`, `granted` | 권한을 받은 앱의 UID 와 허용 여부 |
| `usb-device` | `vendor-id`, `product-id`, `serial-number`, `manufacturer`, `product` | 권한 대상 USB 기기 |
| `usb-accessory` | 액세서리 식별 문자열 | 권한 대상 USB 액세서리 |

파일에는 영구 권한만 들어가고, "기기를 뗄 때까지" 주는 일시 권한은 메모리에만 있습니다[3]. 권한을 준 시각은 저장하지 않습니다[3]. UID 를 패키지 이름으로 바꾸는 법은 [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md) 를 봅니다.

### 메모리 안 기록과 로그

`UsbHostManager` 의 `ConnectionRecord` 에는 시각(`mTimestamp`), 기기 주소(`mDeviceAddress`), 종류(`mMode`), 기기 디스크립터 바이트(`mDescriptors`)가 들어 있고, 종류 값은 `CONNECT`, `CONNECT_BADPARSE`, `CONNECT_BADDEVICE`, `DISCONNECT` 넷입니다[2]. 마지막 정상 연결은 `mLastConnect` 에 따로 두고 dump 에서 디스크립터와 함께 보여 줍니다[2].

기기를 꽂으면 로그캣에 "USB device attached: " 로 시작하는 줄이 남고, 이 줄에는 vendor·product ID, 제조사, 제품명, 버전, 시리얼, 인터페이스 정보가 들어갑니다[2]. 같은 클래스는 "Added device ", "Removed device at ", "USB MIDI Devices Removed: " 메시지도 남기고, 통계 기록 `FrameworkStatsLog.USB_DEVICE_ATTACHED` 도 보냅니다[2]. `isDenyListed()` 는 기기 빌드의 리소스 `config_usbHostDenylist` 에 적힌 주소로 시작하는 기기와, 허브·HID 부트 장치(마우스·키보드)를 걸러 냅니다[2]. 걸러 낸 기기는 연결 기록과 "USB device attached: " 로그 줄을 남기기 전에 처리가 끝나므로, 키보드·마우스를 꽂은 흔적은 이 기록에서 찾을 수 없습니다[2].

PC 쪽 연결에서는 `UsbDeviceManager` 가 `persist.sys.usb.config`, `sys.usb.config`, `sys.usb.state` 같은 시스템 속성과 `/sys/class/android_usb/android0/state` 같은 커널 경로로 현재 USB 기능과 상태를 다룹니다[1]. 휴대폰이 USB 액세서리(AOA)에 붙을 때는 상대가 보낸 `MANUFACTURER`, `MODEL`, `DESCRIPTION`, `VERSION`, `URI`, `SERIAL` 문자열로 액세서리를 알아봅니다[1].

## 증거로서 의미

**증명하는 것**

`adb_keys` 에 키 한 줄이 있으면 어떤 호스트에 대해 USB 디버깅 "항상 허용" 이 적어도 한 번 있었고 그 뒤로 지워지지 않았다는 뜻입니다. `adb_temp_keys.xml` 의 `lastConnection` 은 그 키로 마지막으로 연결한 시각을 알려 주고, `wifiAP` 의 BSSID 는 무선 디버깅을 허용한 네트워크를 가리킵니다[4]. `usb_permissions.xml` 은 어느 앱(UID)이 어느 USB 기기(vendor·product ID, 시리얼)에 영구 접근 권한을 받았는지 알려 줍니다[3]. 기기를 끄지 않은 채 확보했다면 메모리 안의 OTG 연결 기록과 로그캣 줄로 최근에 꽂은 기기의 식별 정보와 시각을 볼 수 있습니다[2].

**증명하지 못하는 것**

ADB 키 파일에는 공개키만 있고 그 PC 가 어느 컴퓨터인지는 나오지 않으므로, 상대 PC 를 가리키려면 PC 쪽 증거와 맞춰 봐야 합니다. USB 디버깅 없이 충전만 하거나 파일 전송(MTP)만 한 연결은 AOSP 에서는 파일로 남는 기록이 없습니다[1]. 어떤 파일을 옮겼는지는 USB 흔적만으로 알 수 없고, `usb_permissions.xml` 에는 시각이 없어서 권한을 언제 줬는지도 알 수 없습니다[3].

보고서에는 "PC 로 자료를 옮겼다" 가 아니라 "이 공개키를 쓰는 호스트에 USB 디버깅을 허용한 기록이 있고, 그 키의 마지막 연결 시각은 이러하다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

| 값 | 형식 | 바뀌는 때 | 근거 |
|---|---|---|---|
| `adbKey` 의 `lastConnection` | 유닉스 밀리초, 기기 시계 기준 | 그 키로 연결할 때와 "항상 허용" 을 누를 때 | [4] |
| `ConnectionRecord` 의 시각 | 유닉스 밀리초, 기기 시계 기준 | OTG 기기를 꽂거나 뗄 때 | [2] |
| `ConnectionRecord` 의 dump 표시 | `MM-dd HH:mm:ss:SSS`, 연도 없음 | — | [2] |
| batterystats 기록 줄 앞 시각 | `MM-DD HH:MM:SS.mmm` 모양, 연도 없음 | — |  |
| 로그캣 줄 앞 시각 | `MM-DD HH:MM:SS.mmm` 모양, 연도 없음 | — |  |

유닉스 밀리초는 UTC 기준 값이라 시간대에 따라 바꿔 읽어야 하고, 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 정리해 두었습니다. dump·로그 출력처럼 연도와 시간대 표시가 없는 시각은 확보한 날짜와 [시간대와 시각 설정](../system-account/time-zone.md) 을 함께 보고 연도를 채워 넣어야 하며, 기기 시계를 사용자가 바꿨다면 그 차이도 따로 확인합니다.

## 함정과 한계

가장 흔한 오해는 "USB 연결 기록이 어딘가에 쭉 쌓여 있다" 는 생각입니다. AOSP 에는 연결 자체를 시간순으로 파일에 남기는 곳이 없고, 메모리 안 기록은 재부팅하면 사라집니다[1][2]. 기기를 끈 뒤 받은 이미지에서 OTG 연결 이력을 찾으려 하면 헛수고가 되기 쉽습니다.

`adb_keys` 에 키가 없다고 해서 ADB 연결이 없었다고 할 수 없습니다. "항상 허용" 을 누르지 않고 한 번만 허용했을 수도 있고, 키를 나중에 지웠을 수도 있습니다. 시스템도 스스로 키를 지우는데, 마지막 연결 시각에서 연결 허용 기간(`adb_allowed_connection_time`)이 지난 키는 `adb_temp_keys.xml` 에서 빠지고 `adb_keys` 도 다시 쓰입니다[4]. 그래서 오래 연결하지 않은 PC 의 키는 사용자가 손대지 않아도 사라질 수 있습니다. 파일이 비어 있거나 없을 때 사용자가 승인을 취소했는지 기기를 초기화했는지 가를 근거도 이 파일에는 없으니 [초기화 흔적](../system-account/factory-reset.md) 과 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 를 함께 봅니다.

`/adb_keys` 는 시스템 이미지에 들어 있는 키이고 dump 에서도 `system_keys` 로 따로 보여 줍니다[4]. 제조사나 빌드가 넣어 둔 키일 수 있으므로 사용자가 허용한 `/data/misc/adb/adb_keys` 와 섞어 세지 않습니다.

`usb_permissions.xml` 은 영구 권한만 담으므로, 앱이 USB 기기를 한 번 쓰고 일시 권한만 받았다면 파일에 남지 않습니다[3]. 로그캣의 USB 줄은 로그 버퍼에 남아 있는 동안만 볼 수 있고, 버퍼가 얼마나 오래 가는지는 [logcat](../logs/logcat.md) 에서 다룹니다.

## 직접 분석해 보기

### 파일 구조를 한 번 따라가기

아래는 소스의 태그·속성 이름으로 짜 본 예시이고, 실제 파일에서 나온 값이 아닙니다. 값은 `…` 로 두었고, 태그 순서와 들여쓰기도 실제 파일과 다를 수 있습니다.

```xml
<keyStore version="…">
  <adbKey key="…" lastConnection="…" />
  <wifiAP bssid="…" />
</keyStore>
```

```xml
<permissions>
  <permission uid="…" granted="…">
    <usb-device vendor-id="…" product-id="…" serial-number="…" manufacturer="…" product="…" />
  </permission>
</permissions>
```

`adb_temp_keys.xml` 을 헥스 편집기로 열었을 때 앞 4바이트가 `41 42 58 00`(ASCII `ABX`)이면 ABX 이고, `<` 로 시작하면 텍스트 XML 입니다. `lastConnection` 값을 찾았다면 1000 으로 나눠 유닉스 초로 만든 뒤 UTC 로 바꿉니다.

```sh
# lastConnection 값(밀리초)을 UTC 시각으로 바꾼다. MS 자리에 실제 값을 넣는다.
MS=…
date -u -d @$((MS / 1000))
```

### 공개 도구로 한 번

`/data/misc/adb` 와 `/data/system/users` 는 앱 데이터와 마찬가지로 전체 파일 시스템을 확보해야 볼 수 있는 곳으로 보고 계획을 세웁니다. 확보 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 를 봅니다. 기기가 켜져 있고 adb 를 쓸 수 있다면 `adb shell settings list global` 로 위 표의 설정 키를 확인하고, 메모리 안 기록은 dumpsys 로 봅니다. dumpsys 출력을 다루는 법은 [dumpsys 출력](../logs/dumpsys.md) 에 있습니다. 공개 분석 도구로 이 파일들을 읽었다면 결과를 위 태그 표와 대조해 검증합니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 점 |
|---|---|
| [배터리 사용 기록](../app-usage/batterystats.md) | 기록 첫 상태 줄에 `status=`, `health=`, `plug=` 필드와 `-otg` 표시가 보입니다. `plug=` 에 USB 가 어떻게 찍히는지는 실제 데이터로 확인합니다 |
| [logcat](../logs/logcat.md) | "USB device attached: " 줄의 vendor·product ID 를 `usb_permissions.xml` 의 `vendor-id`·`product-id` 와 맞춰 봅니다 |
| [와이파이 설정과 접속 기록](wifi.md) | `wifiAP` 의 BSSID 가 저장된 와이파이 네트워크 가운데 어느 것인지 찾습니다 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | USB 권한을 받은 앱을 언제 썼는지 봅니다 |
| [테더링과 핫스폿](tethering-hotspot.md) | USB 기능 가운데 RNDIS·NCM 은 USB 테더링 쪽입니다 |
| [미디어 저장소](../media/mediastore/index.md) | PC 에서 옮긴 파일이 새 항목으로 생겼는지 봅니다. MTP 전송이 여기에 어떤 흔적을 남기는지는 실제 데이터로 확인합니다 |

여러 흔적을 한 시간선에 올리는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에, 자료 반출 여부를 묻는 조사 흐름은 [자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에 있습니다. 무선으로 파일을 주고받는 경우는 [파일 공유](quick-share.md) 를 봅니다.

## 실습

공개 시험 데이터(NIST CFReDS 등)의 안드로이드 전체 파일 시스템 이미지를 하나 골라 아래 질문을 풀어 봅니다. 이미지에 따라 이 파일들이 없을 수 있으니 먼저 파일이 있는지부터 봅니다.

1. `/data/misc/adb/adb_keys` 에 키가 몇 줄 있고, `/adb_keys` 와 겹치는 키가 있는가?
2. `adb_temp_keys.xml` 의 `lastConnection` 을 UTC 와 기기 시간대로 각각 바꾸면 언제인가? 그 시각에 다른 아티팩트에도 활동이 있는가?
3. `wifiAP` 가 있다면 그 BSSID 는 와이파이 설정의 어느 네트워크와 맞는가?
4. `usb_permissions.xml` 에서 영구 권한을 받은 UID 는 어느 패키지이고, 대상 기기의 vendor·product ID 는 무엇인가?

## 참고 문헌

1. AOSP frameworks/base — `services/usb/java/com/android/server/usb/UsbDeviceManager.java` — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usb/java/com/android/server/usb/UsbDeviceManager.java
2. AOSP frameworks/base — `services/usb/java/com/android/server/usb/UsbHostManager.java` — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usb/java/com/android/server/usb/UsbHostManager.java
3. AOSP frameworks/base — `services/usb/java/com/android/server/usb/UsbUserPermissionManager.java` — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/usb/java/com/android/server/usb/UsbUserPermissionManager.java
4. AOSP frameworks/base — `services/core/java/com/android/server/adb/AdbDebuggingManager.java` — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/adb/AdbDebuggingManager.java
