---
title: "블루투스 장치"
parent: "아티팩트 · 네트워크·연결"
nav_order: 760
---

# 블루투스 장치 (Bluetooth)

블루투스 설정 파일 `bt_config.conf` 에는 폰이 짝지은(페어링한) 기기마다 MAC 주소, 기기 이름, 시각 값, 링크 키가 구역별로 적혀 있어서, 이 폰이 어떤 이어폰·차량·시계 같은 기기와 짝을 맺었는지 확인하는 출발점이 됩니다 [1].

## 무엇을 기록하나 · 왜 생기나

블루투스 기기와 짝을 지으면 폰은 다음에 다시 연결할 때 쓸 정보를 설정 파일에 적어 둡니다. ALEAPP 가 읽는 `bt_config.conf` 는 한 줄에 `키 = 값` 하나씩 적힌 글자 파일이고, 짝지은 기기마다 MAC 주소 머리줄로 구역이 시작합니다 [1]. 첫 MAC 구역 앞부분에는 상대 기기가 아니라 폰 자신의 블루투스 어댑터 정보가 들어 있습니다 [1].

이 파일은 짝지은 관계를 보관하는 설정이지 연결할 때마다 한 줄씩 쌓는 로그가 아닙니다. 블루투스를 언제 켜고 껐는지는 이 파일이 아니라 `dumpsys bluetooth_manager` 출력 같은 시스템 상태 기록에서 찾아야 하고, 이 출력은 아래 "위치와 버전별 차이" 에서 정리합니다.

## 위치와 버전별 차이

ALEAPP 는 파일 이름만으로 찾습니다 [1].

```
*/bt_config.conf
```

Android 11 시험 이미지에서 이 파일은 `/data/misc/bluedroid/bt_config.conf` 에 있었습니다 [2]. 버전과 제조사마다 폴더가 다를 수 있고 패턴도 폴더를 가리지 않으니, 분석 대상 전체에서 이 이름을 찾고 같은 이름의 파일이 여러 개 나오면 각각의 경로를 보고서에 적습니다.

ALEAPP 가 이 모듈을 시험한 이미지에서 짝지은 기기 행은 0~4개였고, Android 16 Pixel 8 Pro 이미지는 0행이었으며, 어댑터 구역의 키는 9~14개였습니다 [1]. 기기 행이 0개인 경우도 있다는 뜻이니, 결과가 비었을 때는 짝지은 기기가 정말 없었는지와 파일 모양이 파서 기대와 달랐는지를 나눠서 확인합니다.

adb 일반 권한으로 받은 `dumpsys bluetooth_manager` 출력은 한 기기에서 약 16,690줄이었고, 앞부분은 아래 모양입니다.

| 부분 | 나온 필드나 줄 모양 |
|---|---|
| Bluetooth Status | `enabled`, `state`, `address`, `name`, `time since enabled` |
| Enable log | `MM-DD HH:MM:SS.mmm  Package [android] requested to [Enable]. Reason is SYSTEM_BOOT` |
| 그 밖의 줄 | `Bluetooth crashed # times`, `Ble app registered: {...}` |
| BluetoothManagerService | `mEnable`, `mQuietEnable`, `mEnableExternal`, `mQuietEnableExternal`, 그 뒤 기능 플래그 목록(`Flag dump`) |

Enable log 에는 블루투스를 켜 달라는 요청이 요청한 패키지와 이유와 함께 남습니다. `Ble app registered` 줄에는 BLE 를 쓰려고 등록한 패키지 목록(`com.samsung.android.mcfserver`, `com.samsung.android.beaconmanager` 등)이 나옵니다. 짝지은 기기 목록이 이 출력에 나오는지는 실제 출력의 뒷부분에서 확인합니다. `dumpsys` 를 받고 읽는 법은 [dumpsys 출력 (dumpsys)](../logs/dumpsys.md) 페이지에 있습니다.

설정 값에도 블루투스 관련 키가 있습니다.

| 설정 영역 | 키 |
|---|---|
| global | `bluetooth_on`, `bluetooth_disabled_profiles`, `bluetooth_btsnoop_default_mode`, `bluetooth_last_device_version`, `bluetooth_airplane_toast_count` |
| secure | `bluetooth_address`, `bluetooth_name`, `bluetooth_addr_valid`, `bluetooth_automatic_turn_on`, `bluetooth_apm_state`, `bluetooth_le_broadcast_name`, `bluetooth_le_broadcast_code`, `bluetooth_cast_mode` 등 |
| system | `volume_music_bt_a#dp`, `volume_voice_bt_sco` 등 블루투스 음량 키 |

키마다 값의 뜻은 실제 데이터로 확인합니다. 이름으로 보면 `bluetooth_address`·`bluetooth_name` 은 폰 자신의 블루투스 주소와 이름이라서, `bt_config.conf` 어댑터 구역의 값과 맞춰 볼 수 있습니다. 설정 키를 읽는 법은 [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) 페이지에 있습니다.

## 구조

아래는 ALEAPP 가 기대하는 모양 [1] 으로 만든 예시이고, 실제 데이터의 값이 아닙니다. 어댑터 구역의 머리줄과 키 이름은 기기마다 직접 확인합니다.

```
(어댑터 구역: 폰 자신의 블루투스 정보, 키 9~14개)
...

[aa:bb:cc:dd:ee:ff]
Name = (상대 기기 이름)
Timestamp = (정수)
LinkKey = (링크 키)
...
```

ALEAPP 가 기기 구역에서 읽는 키는 세 개입니다 [1].

| 키 | 담긴 것 |
|---|---|
| 머리줄 `[aa:bb:cc:dd:ee:ff]` | 짝지은 기기의 MAC 주소 |
| `Name` | 기기 이름 |
| `Timestamp` | 정수 시각 값 |
| `LinkKey` | 링크 키 |

어댑터 구역은 ALEAPP 가 키와 값을 모두 그대로 보여 줍니다 [1]. 기기 구역에는 기기 종류나 지원 서비스 같은 다른 키도 있을 수 있습니다. 실제 데이터에서 처음 보는 키는 이름만 적고 뜻은 따로 확인합니다.

## 증거로서 의미

**증명하는 것**

`LinkKey` 가 있는 기기 구역은 그 MAC 주소의 기기와 짝을 맺은 설정이 확보 시점에 이 폰에 남아 있었다는 뜻이고, `Name` 으로 그 기기가 어떤 이름으로 보였는지 알 수 있습니다. 차량이나 특정 사무실 장비처럼 주인이 분명한 기기의 MAC 주소가 나오면, 그 기기와 짝을 맺은 적이 있다는 기록이 됩니다. `dumpsys bluetooth_manager` 의 Enable log 는 블루투스를 켜 달라고 요청한 패키지와 이유를 알려 줍니다.

**증명하지 못하는 것**

짝을 맺었다는 기록에는 연결된 시각이나 횟수가 나오지 않고, 특정 시각에 두 기기가 붙어 있었다는 근거도 아닙니다. 기기 이름은 같은 모델끼리 겹칠 수 있어서 이름만으로 기기를 특정하지 않고 MAC 주소와 함께 씁니다. 블루투스로 어떤 파일이나 소리를 주고받았는지도 이 파일에는 없습니다. `LinkKey` 가 있는 구역은 짝지은 기기로 봅니다 [2]. `LinkKey` 없이 이름만 있는 구역은 뜻을 단정할 수 없으니, 구역마다 `LinkKey` 가 있는지 함께 적습니다. 짝을 끊은 기기의 구역이 파일에 남는지는 시험 기기에서 짝을 끊어 보고 확인하고, 구역이 없다고 짝을 맺은 적이 없다고 결론 내리지 않습니다.

## 시각 해석

ALEAPP 는 `Timestamp` 값을 정수 유닉스 초로 보고 UTC 로 바꾸며, 이 열을 "First Connected Timestamp" 라고 부릅니다 [1]. Android 11 시험 이미지에서는 이 값이 시험 기록에 적힌 처음 연결 시각과 맞았습니다 [2]. 다만 짝을 다시 맺거나 설정이 바뀔 때 값이 새로 쓰일 수 있으니, 보고서에는 도구가 붙인 이름을 옮기지 말고 "설정 파일의 이 기기 구역에 기록된 시각" 처럼 씁니다. 값을 읽는 일반 방법은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

`dumpsys bluetooth_manager` Enable log 의 시각은 `MM-DD HH:MM:SS.mmm` 모양이고 연도가 없습니다. 연도는 수집 날짜에서 거꾸로 짐작하고, 시간대는 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 에서 확인한 뒤 씁니다. Bluetooth Status 의 `time since enabled` 는 이름으로 보면 켜진 뒤 흐른 시간이라서, 수집 시각에서 빼면 마지막으로 켜진 시각을 추정할 수 있습니다. 값의 단위와 모양은 실제 출력에서 확인합니다.

## 함정과 한계

첫째, `LinkKey` 는 두 기기 사이의 비밀 값입니다. 분석에는 MAC 주소와 이름이면 충분한 경우가 많으니, 보고서와 공유용 사본에서는 링크 키를 가립니다.

둘째, 도구가 붙인 열 이름을 그대로 믿지 않습니다. 위 시각 열처럼 "처음 연결" 이라는 이름이 붙어 있어도 실제 뜻은 이름과 다를 수 있습니다.

셋째, 파일이 없거나 기기 행이 0개인 경우가 있습니다. ALEAPP 시험 이미지에서도 0행이 있었으니 [1], 결과가 비면 파일 경로와 모양을 직접 확인합니다.

넷째, 설정 값과 `dumpsys` 는 수집 순간의 상태입니다. `bluetooth_on` 값이나 Bluetooth Status 의 `state` 는 확보할 때 켜져 있었는지를 알려 줄 뿐이고, 사건 시각의 상태는 아닙니다.

다섯째, 설정에 `bluetooth_btsnoop_default_mode` 키가 있을 수 있습니다. 이름으로 보면 블루투스 통신 기록(btsnoop) 설정과 관련된 키 같지만 이름만으로 값의 뜻을 단정할 수 없으니, 이 키가 있다는 사실만으로 통신 기록 파일이 있다고 쓰지 않습니다.

## 직접 분석해 보기

### 파일을 직접 한 번

`bt_config.conf` 는 글자 파일이라 헥스 대신 편집기나 `grep` 으로 읽습니다. 사본에서 머리줄과 ALEAPP 가 읽는 세 키만 뽑으면 기기마다 한 덩어리로 보입니다.

```
grep -E '^\[|^Name|^Timestamp' bt_config.conf
```

`Timestamp` 값은 ALEAPP 처럼 유닉스 초로 보고 바꿔 봅니다. 아래 명령의 숫자 자리는 실제로 읽은 값으로 바꿉니다.

```
date -u -d @1700000000
```

바꾼 날짜가 기기 사용 기간 안에 들어가는지 먼저 보고, 말이 안 되면 단위가 다른지 의심합니다. 위 명령은 `LinkKey` 줄을 뽑지 않습니다.

### 공개 도구로 한 번

ALEAPP 의 `bluetoothConnections` 모듈이 `bt_config.conf` 를 찾아 어댑터 정보와 기기 목록을 따로 보여 줍니다 [1]. 도구가 보여 준 MAC 주소 수와 위 `grep` 결과의 머리줄 수가 같은지, 시각이 같은 날짜로 바뀌었는지 맞춰 봅니다. 검증 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 페이지에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) | 폰 블루투스 주소·이름 키와 어댑터 구역 값이 같은지 |
| [dumpsys 출력 (dumpsys)](../logs/dumpsys.md) | Enable log 에 사건 시간대 켜기 요청이 있는지, 요청한 패키지가 무엇인지 |
| [배터리 사용 기록 (batterystats)](../app-usage/batterystats.md) | 사건 시간대의 기기 상태 기록 (블루투스 전용 표시가 있는지는 실제 데이터로 확인) |
| [파일 공유 (Quick Share·Nearby Share)](quick-share.md) | 근처 기기와 파일을 주고받은 기록이 따로 있는지 |
| [와이파이 설정과 접속 기록 (WifiConfigStore)](wifi.md) | 같은 시간대에 붙어 있던 네트워크가 있는지 |

기기를 누가 썼는지 따지는 흐름은 [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](../../04-scenarios/activity/user-attribution.md), 여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 시험 이미지에서 아래 질문을 풀어 봅니다.

1. 이미지 안에 `bt_config.conf` 가 몇 개 있고, 각각 어느 경로에 있습니까?
2. 어댑터 구역에는 키가 몇 개 있고, 폰 자신의 블루투스 이름이 적혀 있습니까?
3. 짝지은 기기 구역은 몇 개이고, 각 기기의 이름은 무엇입니까?
4. 각 기기의 `Timestamp` 를 유닉스 초로 바꾸면 날짜가 기기의 사용 기간 안에 들어갑니까?

## 참고 문헌

1. ALEAPP — scripts/artifacts/bluetoothConnections.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/bluetoothConnections.py
2. Kevin Pagano (stark4n6) — Android Bluetooth Connection Configuration — https://www.stark4n6.com/2021/06/android-bluetooth-connection.html
