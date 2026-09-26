---
title: "근거리 공유로"
parent: "자료를 밖으로 보냈나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 1740
---

# 근거리 공유로 (Quick Share·Bluetooth)

Quick Share, 블루투스 파일 전송처럼 가까운 기기로 자료를 직접 보냈는지 확인하는 순서를 정리합니다. Quick Share 의 보내고 받은 기록이 남는 앱·DB·표와 블루투스 파일 전송(OPP) 기록 DB 의 구조는 공개된 분석 자료가 없어 검체에서 확인해야 합니다. 그래서 이 페이지는 "어떤 기기와 짝지었거나 가까이 있었나" 를 보여 주는 기록과 관련 설정 키를 모아, 전송 기록을 찾을 때의 출발점을 잡는 흐름으로 씁니다. 유출 경로 전체의 길잡이는 [자료를 밖으로 보냈나 (Data Exfiltration)](index.md) 허브에 있습니다.

## 조사 질문

이 기기가 조사 기간에 가까운 다른 기기로 파일을 보냈는지, 보냈다면 어느 기기로 언제 보냈는지 묻습니다. 근거리 공유는 인터넷 서버를 거치지 않을 수 있어서 계정 쪽 자료로 보충하기 어렵고, 기기 안의 기록과 상대 기기의 기록을 함께 봐야 할 때가 많습니다.

## 먼저 확인할 것

블루투스 설정 파일과 Google Play 서비스의 Nearby 캐시는 시스템 폴더나 앱 데이터 폴더에 있어서, 수집본에 그 폴더가 들어 있는지부터 봅니다. `dumpsys bluetooth_manager` 와 설정 키는 adb 일반 셸 권한으로 읽을 수 있습니다. 상대 기기를 확보할 수 있는지도 먼저 정해 둡니다. 받은 쪽 기기의 수신 폴더와 기록이 이 기기의 기록보다 직접적인 경우가 많습니다.

시각 단위가 기록마다 다릅니다. 블루투스 설정 파일은 유닉스 초이고 Nearby 캐시는 유닉스 밀리초라서, 한 타임라인에 올리기 전에 단위를 맞춥니다. 단위별 읽는 법은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 블루투스 설정 파일 | 짝지은 기기의 주소·이름·시각 | [블루투스 장치 (Bluetooth)](../../../02-artifacts/network/bluetooth.md) |
| 2 | dumpsys bluetooth_manager | 블루투스 상태, 켠 앱과 이유 | [dumpsys 출력 (dumpsys)](../../../02-artifacts/logs/dumpsys.md) |
| 3 | 설정 키(Quick Share·Nearby) | 관련 기능을 볼 수 있는 키 | [설정 값 (Settings Global·Secure·System)](../../../02-artifacts/system-account/settings.md) |
| 4 | Quick Share 기록 | 보내고 받은 기록(위치는 검체에서 확인) | [파일 공유 (Quick Share·Nearby Share)](../../../02-artifacts/network/quick-share.md) |
| 5 | Nearby 캐시 | 근처에서 발견한 액세서리·기기 | [LevelDB와 IndexedDB (LevelDB·IndexedDB)](../../../01-foundations/data-formats/leveldb-indexeddb.md) |
| 6 | 공용 저장 공간 | 보낸 파일의 원본, 받은 파일 | [공용 저장 공간 (Shared Storage·/sdcard)](../../../01-foundations/storage/shared-storage.md) |

## 블루투스 기기 기록

블루투스 설정 파일은 `*/bt_config.conf` 패턴으로 찾고 [2], 전체 경로는 버전마다 다를 수 있어 검체에서 확인합니다. 파일은 텍스트이고, `[aa:bb:cc:dd:ee:ff]` 모양의 MAC 주소 절 아래에 `Name = `, `Timestamp = `, `LinkKey = ` 줄이 붙습니다 [2]. 첫 MAC 절 앞부분은 이 기기 자신의 어댑터 정보입니다 [2].

```ini
; ALEAPP 설명의 줄 이름으로 만든 예시. 주소·이름·값은 지어낸 것입니다.
[aa:bb:cc:dd:ee:ff]
Name = EXAMPLE-LAPTOP
Timestamp = 1700000000
LinkKey = (값 생략)
```

`Timestamp` 는 유닉스 초이고 밀리초가 아닙니다 [2]. ALEAPP 는 이 값을 UTC 로 바꿔 "First Connected Timestamp" 로 이름 붙였지만 [2], 처음 연결한 시각인지 마지막으로 갱신한 시각인지는 밝힌 공개 자료가 없어 다른 기록과 맞춰 봅니다. `LinkKey` 는 연결 키 값이라서 보고서에는 값을 옮기지 않고 있는지 없는지만 적습니다. 블루투스 기록의 자세한 구조는 [블루투스 장치 (Bluetooth)](../../../02-artifacts/network/bluetooth.md) 페이지에 있습니다.

블루투스 파일 전송(OPP) 기록 DB 의 표와 칸은 공개된 분석 자료가 없어 검체에서 확인해야 합니다. 그래서 블루투스 설정 기록으로는 "이 주소의 기기와 짝지었다" 는 데까지만 말하고, 파일을 보냈는지는 전송 기록이나 상대 기기에서 확인합니다.

`dumpsys bluetooth_manager` 에는 Bluetooth Status(enabled, state, address, name, time since enabled), 블루투스를 켜 달라고 한 패키지와 이유가 적힌 Enable log, "Ble app registered" 목록, 기능 플래그 목록이 나오고, 출력이 16,690줄에 이르기도 합니다. 삼성 기기에서는 BLE 에 등록한 앱 목록에 com.samsung.android.mcfserver, com.samsung.android.mcfds, com.samsung.android.beaconmanager, com.samsung.android.mdx.kit 가 나올 수 있습니다. 이 출력은 수집 시점의 상태라서 과거의 전송을 보여 주지는 않지만, 블루투스를 언제부터 켜 두었는지와 어떤 앱이 BLE 를 쓰고 있었는지를 적어 둘 수 있습니다.

설정 표에 있는 블루투스 키는 global 표의 `bluetooth_on`, `bluetooth_btsnoop_default_mode`, `bluetooth_disabled_profiles` 와 secure 표의 `bluetooth_address`, `bluetooth_name`, `bluetooth_automatic_turn_on`, `bluetooth_le_broadcast_name` 입니다. `bluetooth_btsnoop_default_mode` 는 HCI 기록(btsnoop) 모드 키이고, 켜져 있었는지는 검체에서 값을 읽어 확인합니다.

## Quick Share·Nearby

Quick Share 관련 설정 키는 다음과 같습니다. 누구에게 보이도록 했는지 같은 값의 뜻은 공개 자료가 없어 검체에서 확인합니다.

| 표 | 키 |
|---|---|
| global | `mcf_quick_share_visibility` |
| secure | `nearby_sharing_component`, `mcf_continuity_nearby_device_state` |
| system | `quickshare_enabled`, `nearby_scanning_enabled` |

`nearby_sharing_component` 는 이름으로 보아 근거리 공유를 맡은 앱 부품 이름이 들어가는 키로 보이고, 어느 앱인지는 값을 읽어 확인합니다. Quick Share 로 보내고 받은 기록이 남는 앱·DB·표 이름과, Google Nearby Share 와 삼성 Quick Share 가 합쳐진 시기·버전은 공개된 분석 자료가 없습니다. 전송 기록은 [파일 공유 (Quick Share·Nearby Share)](../../../02-artifacts/network/quick-share.md) 페이지에서 다룹니다.

Google Play 서비스에는 Nearby 캐시가 두 가지 있고, 둘 다 LevelDB 입니다 [3]. Fast Pair 캐시는 `*/nearby-fast-pair/nearby_fast_pair_item_cache.db/*` 에 있고, 레코드마다 MAC 주소, 모델 이름, 표시 이름, 처음·마지막으로 본 시각(유닉스 밀리초)이 있을 수 있습니다 [3]. 이 캐시는 이어폰 같은 액세서리 기록이고, 한 행이 곧 짝지었다는 뜻은 아닙니다 [3]. 발견 캐시는 `*/nearby-discovery/nearby_discovery_item_cache.db/*` 에 있고, 칸은 처음·마지막으로 본 시각(밀리초), 항목 ID, MAC 주소, RSSI, 상태입니다 [3]. RSSI 는 dBm 단위의 신호 세기이고 거리가 아니며, 한 행은 "캐시에 있었다" 는 뜻일 뿐 사용자가 그 기기와 무엇을 주고받았다는 뜻은 아닙니다 [3].

두 캐시의 필드 번호는 Chromium 의 StoredDiscoveryItem(ash/quick_pair/proto/fastpair_data.proto)을 따릅니다 [3]. 두 캐시는 액세서리와 발견 항목을 담는 기록이라서 Quick Share 파일 전송 기록으로 쓰지 않습니다 [3]. LevelDB 는 같은 키의 옛 사본을 남기기 때문에 같은 주소가 여러 번 나올 수 있습니다 [3]. ALEAPP 시험에서 samsunga53_a14 는 Fast Pair 캐시 15행, 발견 캐시 0행이었습니다 [3].

## 다른 근거리 공유 앱과 핫스팟

ALEAPP 에는 파일 공유 앱 모듈 shareit.py 와 Xender.py 가 있습니다 [1]. 이런 앱이 설치돼 있었다면 [설치된 앱 (packages.xml)](../../../02-artifacts/app-usage/packages/index.md)과 [앱 사용 기록 (usagestats)](../../../02-artifacts/app-usage/usagestats/index.md)으로 사용 시각대를 먼저 좁힙니다.

와이파이 다이렉트(P2P) 연결 기록의 위치는 공개된 분석 자료가 없어 검체에서 확인해야 합니다. `dumpsys wifi` 에는 핫스팟(SoftAp) 관련 줄(CMD_SET_AP, CMD_AP_STOPPED 등)이 나오고, secure 표에는 `autohotspot_saved_nearby_state`, `autohotspot_family_sharing_nearby_saved_state` 키가 있습니다. 핫스팟 기록은 [테더링과 핫스폿 (Tethering·Hotspot)](../../../02-artifacts/network/tethering-hotspot.md) 페이지에서 다룹니다.

## 분석 흐름

1. 수집본에 블루투스 설정 파일과 Google Play 서비스 앱 데이터가 들어 있는지 확인합니다.
2. `bt_config.conf` 에서 짝지은 기기의 주소·이름·`Timestamp` 를 뽑고, 조사 기간에 걸리는 기기를 표시합니다.
3. Quick Share·Nearby 설정 키와 `dumpsys bluetooth_manager` 를 적어 수집 시점의 상태를 남깁니다.
4. 파일 공유 앱의 전송 기록을 찾고, 없으면 공용 저장 공간에서 조사 기간 전후로 모으거나 옮긴 파일을 찾습니다.
5. 상대 기기를 확보했다면 수신 기록과 받은 파일을 이 기기의 시각과 맞춥니다.

## 흔한 오판

`bt_config.conf` 에 기기가 있다는 사실을 파일을 보낸 기록으로 읽지 않습니다. 한 절은 짝지은 기기가 있었다는 기록일 뿐 전송을 보여 주지 않습니다.

Nearby 캐시의 행을 만남이나 전송의 증거로 쓰지 않습니다. 발견 캐시는 근처에서 신호를 본 기록이고, RSSI 는 거리가 아닙니다 [3].

`Timestamp` 를 밀리초로 읽어 먼 미래나 1970년 근처 시각을 만들지 않습니다. 블루투스 설정 파일의 시각은 초 단위입니다 [2].

## 보고서 문장 예

- "`bt_config.conf` 에 MAC 주소 (주소), 이름 (이름)인 기기의 절이 있고, `Timestamp` 는 (현지 시각)입니다. 이 기록은 해당 기기와 짝지은 적이 있다는 뜻이며, 이 시각이 처음 연결한 시각인지와 파일을 주고받았는지는 이 기록만으로 알 수 없습니다."
- "수집 시점에 system 설정 표에 `quickshare_enabled` 키가 있었으나, 값의 뜻과 전송 기록은 확인되지 않았습니다."

## 함께 볼 페이지

- [블루투스 장치 (Bluetooth)](../../../02-artifacts/network/bluetooth.md)
- [파일 공유 (Quick Share·Nearby Share)](../../../02-artifacts/network/quick-share.md)
- [그 시각에 어디 있었나 (Location)](../../activity/location.md)
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)
- 같은 허브의 다른 경로: [메신저로 (Messenger)](messenger.md), [클라우드로 (Cloud)](cloud.md), [메일로 (Email)](email.md), [PC 연결로 (USB·PC)](usb-pc.md)

## 참고 문헌

1. ALEAPP scripts/artifacts 폴더 목록 — GitHub API, https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
2. bluetoothConnections.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/bluetoothConnections.py
3. nearbyDevices.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/nearbyDevices.py
