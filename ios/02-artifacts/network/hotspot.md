---
title: "개인용 핫스폿"
parent: "아티팩트 · 네트워크·연결"
nav_order: 710
---

# 개인용 핫스폿 (Personal Hotspot)

## 한 줄 요약

개인용 핫스폿 (Personal Hotspot)은 아이폰의 셀룰러 연결을 다른 기기와 나눠 쓰는 기능이고, 흔적은 핫스폿을 켠 아이폰(이하 제공 기기)과 거기에 붙은 기기(이하 접속 기기) 두 쪽에 나뉘어 남습니다.

## 무엇을 기록하나 · 왜 생기나

사용자는 설정 → 개인용 핫스폿(또는 설정 → 셀룰러 → 개인용 핫스폿)에서 "Allow Others to Join" 을 켜서 핫스폿을 엽니다 [3]. 다른 기기는 Wi-Fi, 블루투스, USB 세 가지 방법으로 붙을 수 있고, 블루투스는 페어링 코드를 확인한 뒤 Pair 를 눌러야 하며, USB 는 아이폰에서 "이 컴퓨터를 신뢰" 를 확인해야 합니다(Windows 에서는 Apple Devices 앱이나 iTunes 가 있어야 합니다) [3]. Wi-Fi 암호는 ASCII 문자로 8자 이상이고, 핫스폿 네트워크 이름으로는 기기 이름(설정 → 일반 → 정보 → 이름)을 그대로 씁니다 [3]. 연결되면 접속 기기 상태 막대의 Wi-Fi 아이콘이 개인용 핫스폿 아이콘으로 바뀝니다 [3]. 한 번에 붙을 수 있는 기기 수는 이동통신사와 아이폰 모델에 따라 다르고, 연결이 잘 안 될 때 켜 보는 "Maximize Compatibility" 항목이 핫스폿 설정 안에 있습니다 [3].

인스턴트 핫스폿 (Instant Hotspot)은 같은 Apple 계정으로 로그인했거나 가족 공유로 묶인 기기끼리 쓰는 방식입니다 [4]. 제공 기기는 아이폰이나 셀룰러 아이패드여야 하고 요금제에 개인용 핫스폿이 들어 있어야 하며, 두 기기 모두 Wi-Fi 와 블루투스를 켠 채 가까이 있어야 합니다 [4]. 인스턴트 핫스폿으로 붙을 때는 제공 기기에서 "Allow Others to Join" 을 켜지 않아도 되고, 같은 Apple 계정 기기와 가족 구성원의 기기는 Wi-Fi 암호를 묻지 않습니다 [4]. 접속 기기에는 "Auto-Join Hotspot" 설정이 있어 Ask to Join(물어봄)과 Automatic(자동) 중에서 고르고, 가족 공유 기기에 대해서는 Automatic(자동으로 붙음)과 Ask for Approval(허락을 물음) 중에서 고릅니다 [4].

접속 기기가 핫스폿에 Wi-Fi 로 붙으면 일반 무선 공유기(AP)에 붙을 때와 같은 파일에 네트워크 기록과 연결 시각이 남습니다 [1]. 제공 기기에서는 앱별 데이터 사용량 DB 에 핫스폿을 켠 흔적이 남을 때가 있고 [1], 로컬 백업에는 핫스폿 설정과 관련된 이름의 plist 도 들어 있습니다(확인 범위: iPhone 13 mini, iOS 27.0).

## 위치와 버전별 차이

### 접속 기기(핫스폿에 붙은 아이폰)

| 경로 | 알려 주는 것 | 출처 |
|---|---|---|
| `/private/var/preferences/com.apple.wifi.known-networks.plist` | 처음 연결, 연결 끝, 자동 재연결, 사용자 재연결 시각 | [1] |
| `/private/var/preferences/SystemConfiguration/com.apple.wifi-private-mac-networks.plist` | 처음 연결, 연결 끝, 가장 최근 연결 시각 | [1] |
| `/var/mobile/Library/Preferences/com.apple.networkserviceproxy.plist` | 네트워크 세션의 시작·끝 시각 | [1] |
| 백업 `HomeDomain :: Library/Preferences/com.apple.networkserviceproxy.plist` | 위 파일의 백업 속 위치 | 관찰(확인 범위: iPhone 13 mini, iOS 27.0) |
| 백업 `HomeDomain :: Library/Preferences/com.apple.wifi.removed-networks.plist` | 지운 Wi-Fi 네트워크 목록 | 관찰(확인 범위: iPhone 13 mini, iOS 27.0) |

관찰한 백업은 암호화하지 않은 로컬 백업이었고, 이 백업에는 `com.apple.wifi.known-networks.plist` 와 `com.apple.wifi-private-mac-networks.plist` 가 보이지 않았습니다(확인 범위: iPhone 13 mini, iOS 27.0). 그 대신 `SystemPreferencesDomain :: SystemConfiguration/com.apple.wifi-class-d-private-mac-networks.plist`(키 이름을 가린 list 하나)와 `SystemPreferencesDomain :: SystemConfiguration/com.apple.wifi-networks.plist`(비어 있음)가 보였습니다(확인 범위: iPhone 13 mini, iOS 27.0). 앞의 두 파일이 로컬 백업에 들어가는지, 암호화 백업이면 달라지는지는 확인하지 못했으니 파일 시스템 추출본과 백업을 나눠서 봐야 합니다.

### 제공 기기(핫스폿을 켠 아이폰)

| 경로 | 알려 주는 것 | 출처 |
|---|---|---|
| `/private/var/wireless/Library/Databases/DataUsage.sqlite` (백업 `WirelessDomain :: Library/Databases/DataUsage.sqlite`) | ZPROCESS 표의 지운 레코드로 핫스폿을 켠 흔적 | [1][2], 백업 위치는 관찰(확인 범위: iPhone 13 mini, iOS 27.0) |
| `/private/var/networkd/netusage.sqlite` | 프로세스별 Wi-Fi·WWAN 송수신량(핫스폿과의 관계는 확인하지 못함) | [2] |
| 백업 `HomeDomain :: Library/Preferences/com.apple.MobileInternetSharing.plist` | 핫스폿 상태로 보이는 키(뜻은 확인하지 못함) | 관찰(확인 범위: iPhone 13 mini, iOS 27.0) |
| 백업 `HomeDomain :: Library/Preferences/com.apple.Preferences.plist` | `PersonalHotspotDiabled` 키(뜻은 확인하지 못함) | 관찰(확인 범위: iPhone 13 mini, iOS 27.0) |

netusage.sqlite 는 파일 시스템 추출에서만 얻을 수 있고 [2], 관찰한 로컬 백업에도 보이지 않았습니다(확인 범위: iPhone 13 mini, iOS 27.0).

### 버전별로 확인된 범위

| iOS | 확인된 내용 | 출처 |
|---|---|---|
| 11.1.2 | netusage.sqlite·DataUsage.sqlite 구조 | [2] |
| 16.7 | 접속 기기의 known-networks·private-mac-networks·networkserviceproxy 흔적, 제공 기기의 DataUsage 지운 레코드 | [1] |
| 27.0 | 로컬 백업 속 파일 경로와 키 이름(값은 읽지 않음) | 관찰 |

그 밖의 버전에서 경로나 키가 어떻게 다른지는 확인하지 못했습니다.

## 구조

### 접속 기기: Wi-Fi 설정 plist

`com.apple.wifi.known-networks.plist` 에서는 네트워크 항목마다 아래 시각 키를 봅니다 [1]. 파일 전체 구조와 일반 AP 기록 해석은 [와이파이 기록](wifi.md) 페이지에서 다루고, 여기서는 핫스폿 해석에 쓰는 키만 적습니다.

| 키 | 뜻 |
|---|---|
| `AddedAt` | 처음 연결한 시각 |
| `UpdatedAt` | 연결이 끝난 시각(뒤에 다시 바뀔 수 있음) |
| `JoinedBySystemAt` | 시스템이 자동으로 다시 연결하기 시작한 시각 |
| `JoinedByUserAt` | 사용자가 직접 다시 연결하기 시작한 시각 |

`com.apple.wifi-private-mac-networks.plist` 에서는 `addedAt` 이 처음 연결, `lastUpdatedAt` 이 연결 끝, `lastJoined` 가 가장 최근 연결 시작 시각입니다 [1].

### 접속 기기: networkserviceproxy.plist

`NSPServiceStatusManagerInfo` 값 안에는 plist 가 한 번 더 들어 있고, 그 안에서 `PrivacyProxyNetworkStatusTimeNetworkStartTime`(n번째 세션 시작)과 `PrivacyProxyNetworkStatusTimeNetworkEndTime`(n번째 세션 끝)을 찾습니다 [1]. [1]의 시험에서는 네 번 연결했을 때 1~3번째 세션의 시작·끝만 보였고 마지막 네 번째 세션의 시각은 확인되지 않았습니다. 관찰한 백업에서 이 파일의 최상위 키는 다음과 같았습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
NSPRebootFetchCount (int)
NSPConfiguration (bytes)
NSPServiceStatusManagerInfo (bytes)
NSPSignatureInfo (bytes)
NSPProxyAgentManagerPreferences (bytes)
NSPRebootFetchLastDate (datetime)
```

### 접속 기기: removed-networks.plist

지운 네트워크는 SSID 별 항목으로 남고, 항목 안에 `RemovedAt`, `SSID`, `SupportedSecurityTypes` 키가 있습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
wifi.network.ssid.<SSID>: {RemovedAt, SSID, SupportedSecurityTypes}
```

### 제공 기기: DataUsage.sqlite

DataUsage.sqlite 의 표 구조와 사용량 해석은 [앱별 데이터 사용량](data-usage.md) 페이지에서 다룹니다. 핫스폿과 관련해서는 ZPROCESS 표를 보고, 관찰한 백업에서 칸 이름은 아래와 같았습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
ZPROCESS: Z_PK, Z_ENT, Z_OPT, ZFIRSTTIMESTAMP, ZTIMESTAMP, ZBUNDLENAME, ZEXTENSIONNAME, ZPROCNAME
```

ZTIMESTAMP 는 가장 최근 활동, ZFIRSTTIMESTAMP 는 처음 쓴 때입니다 [2]. [1]은 ZPROCESS 에서 지워진 레코드의 ZTIMESTAMP 값이 있으면 핫스폿이 켜졌던 것으로 봅니다. [1]의 판본에 따라 칸 이름이 "ZTIMESTMAP" 로 적혀 보일 수 있지만, 관찰한 백업의 칸 이름은 ZTIMESTAMP 였습니다(확인 범위: iPhone 13 mini, iOS 27.0). 핫스폿 트래픽이 ZPROCNAME 에 어떤 프로세스 이름으로 잡히는지는 확인하지 못했습니다.

DataUsage 는 Wi-Fi 사용량을 기록하지 않고 [2], 관찰한 백업의 ZLIVEUSAGE 표에도 Wi-Fi 칸 없이 ZWWANIN·ZWWANOUT 만 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

### 뜻을 확인하지 못한 항목

아래 항목은 이름이 핫스폿·네트워크 공유와 관련되어 보이지만 값의 뜻을 확인하지 못했습니다. 모두 관찰한 백업에서 이름만 확인했습니다(확인 범위: iPhone 13 mini, iOS 27.0).

| 위치 | 키·항목 | 비고 |
|---|---|---|
| `HomeDomain :: Library/Preferences/com.apple.MobileInternetSharing.plist` | `State` (int), `UState` (int), `Version` (int) | 켜짐·꺼짐을 나타내는 값인지 확인하지 못함 |
| `HomeDomain :: Library/Preferences/com.apple.Preferences.plist` | `PersonalHotspotDiabled` (bool) | 철자가 "Diabled" 그대로라서 검색할 때 이 철자로 찾아야 함 |
| 백업 도메인 `AppDomainPlugin-com.apple.WiFiKit.PersonalHotspotControl` | 항목 4개 | 이름으로는 제어 센터용 핫스폿 컨트롤 확장으로 보임 |
| `HomeDomain :: Library/Preferences/com.apple.MobileBluetooth.debug.plist` | `NETSHARING`, `NETWORKCONSUMER` 항목과 그 안의 `BtConnectionTypeCounter`, `BtConnectionTypeDuration`, `BtConnectionTypeStartTimeStamp` | 블루투스 핫스폿 공유 횟수·시간인지 확인하지 못함 |
| `SysSharedContainerDomain-systemgroup.com.apple.bluetooth :: Library/Preferences/com.apple.MobileBluetooth.devices.plist` | 기기별 항목의 `ServiceNetSharingUser` | 블루투스 기기 목록은 [블루투스 장치](bluetooth.md) 참고 |
| `SystemPreferencesDomain :: SystemConfiguration/preferences.plist` | `Sets`, `NetworkServices`, `CurrentSet`, `__VERSION__`, `Model`, `System` | 핫스폿용 네트워크 서비스가 남는지 확인하지 못함 |
| `DatabaseDomain :: com.apple.xpc.launchd/disabled.plist` | `com.apple.bootpd` (bool) | 핫스폿 주소 할당과 관계가 있는지 확인하지 못함 |

## 증거로서 의미

### 증명하는 것

접속 기기에 핫스폿 네트워크 기록과 연결 시각이 있으면 그 시각대에 두 기기가 가까이 있었다는 근거로 쓸 수 있습니다 [1]. 처음 연결할 때는 암호를 직접 넣어야 하고 그 뒤로는 연결 거리 안에 들어오면 자동으로 다시 붙기 때문에, [1]은 자동 재연결 기록(`JoinedBySystemAt`)을 이전에 사용자가 암호를 넣은 적이 있다는 뜻으로 해석합니다. 제공 기기에서 DataUsage.sqlite ZPROCESS 의 지운 레코드에 타임스탬프 값이 남아 있으면 핫스폿이 켜졌던 것으로 봅니다 [1].

### 증명하지 못하는 것

인스턴트 핫스폿은 같은 Apple 계정 기기와 가족 구성원 기기에 암호를 묻지 않아서 [4], 인스턴트 핫스폿으로 붙은 기록이라면 사용자가 암호를 알고 직접 입력했다는 근거가 되지 않습니다. 네트워크 이름은 제공 기기의 기기 이름이지만 접속한 뒤에 기기 이름을 바꾸면 기록과 달라질 수 있고 [1], 이름이 맞는다는 사실만으로 특정 기기를 가리킬 수는 없으니 다른 흔적과 맞춰 봐야 합니다. 핫스폿을 통해 무엇을 주고받았는지, 제공 기기에 어떤 기기(MAC 주소·이름)가 붙었는지를 알려 주는 기록은 확인하지 못했습니다. ZPROCESS 의 지운 레코드는 늘 생기지는 않으니 [1], 레코드가 없다는 사실을 핫스폿을 켜지 않았다는 증거로 쓰지 않습니다.

보고서에는 "피의자 기기로 인터넷을 썼다" 가 아니라 "접속 기기의 Wi-Fi 기록에 제공 기기 이름과 같은 네트워크가 있고, 처음 연결 시각과 자동 재연결 시각이 이러하다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

known-networks, private-mac-networks, networkserviceproxy 의 시각 값은 CFAbsoluteTime(Mac 절대 시각)이고, 2001-01-01 00:00:00 UTC 부터 센 초라서 UTC 기준입니다 [1]. 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 페이지를 봅니다.

연결·끊김 시각은 실제로 끊긴 뒤에 갱신되기도 하고 `UpdatedAt` 은 나중에 다시 바뀔 수 있어서, [1]은 이 값들을 참고용으로만 쓰라고 권합니다. 끊긴 시각을 분 단위로 단정하지 말고, 처음 연결 시각과 재연결 시작 시각을 중심으로 시간 범위를 잡는 편이 안전합니다. DataUsage.sqlite 의 시각 값 형식은 [앱별 데이터 사용량](data-usage.md) 페이지를 따르고, removed-networks 의 `RemovedAt` 형식은 확인하지 못했습니다.

## 함정과 한계

핫스폿 네트워크와 일반 AP 를 plist 키 하나로 가려내는 방법은 확인하지 못했습니다. 지금은 네트워크 이름이 제공 기기 이름과 맞는지, 연결 시각이 다른 흔적과 맞는지를 함께 보고 판단해야 합니다.

[1]은 접속 기기 쪽 흔적을 기기 안의 경로로 적었고, 관찰한 로컬 백업에서는 known-networks 와 private-mac-networks 파일이 보이지 않았습니다(확인 범위: iPhone 13 mini, iOS 27.0). 로컬 백업만 받았다면 접속 흔적이 없다고 결론 내리기 전에 수집 범위부터 확인합니다([로컬 백업](../../01-foundations/backups/local-backup/index.md), [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md)).

제공 기기의 핵심 흔적은 지운 레코드라서 SQLite 여유 공간이나 WAL 에서 복구해야 합니다. 복구 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md)와 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지를 봅니다.

사용자가 Wi-Fi 네트워크 목록에서 네트워크를 지우면 관찰한 백업처럼 `com.apple.wifi.removed-networks.plist` 에 `RemovedAt` 이 붙은 항목이 생길 수 있지만(확인 범위: iPhone 13 mini, iOS 27.0), 지운 네트워크 중 핫스폿이 들어가는지는 확인하지 못했습니다. 핫스폿 기본 주소 대역, 통합 로그에서 핫스폿 켜기·클라이언트 접속을 찾을 프로세스 이름, KnowledgeC·바이옴에 핫스폿 상태가 남는지도 확인하지 못했으니 이런 내용을 보고서에 쓸 때는 직접 검증한 결과만 씁니다.

## 직접 분석해 보기

### 헥스로 한 번

이 페이지에는 검체에서 뽑은 바이트를 싣지 않습니다. 아래 순서로 직접 따라가 봅니다.

1. networkserviceproxy.plist 를 plist 도구로 열어 `NSPServiceStatusManagerInfo` 의 bytes 값을 파일로 따로 저장합니다.
2. 저장한 바이트를 헥스 편집기로 열어 맨 앞 머리가 plist 형식인지 확인합니다. 형식 머리와 오프셋 표 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 페이지에 있습니다.
3. 안쪽 plist 를 다시 읽어 `PrivacyProxyNetworkStatusTimeNetworkStartTime`·`PrivacyProxyNetworkStatusTimeNetworkEndTime` 값을 찾고 CFAbsoluteTime 으로 바꿉니다 [1].
4. 제공 기기의 DataUsage.sqlite 와 WAL 파일을 헥스로 열어 ZPROCESS 표의 페이지와 여유 공간에 남은 레코드 조각을 찾습니다. 페이지 구조는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지를 따릅니다.

### 공개 도구로 한 번

APOLLO 에는 DataUsage.sqlite 와 netusage.sqlite 를 읽는 모듈 `datausage_zliveusage`, `datausage_zprocess`, `netusage_zliveusage`, `netusage_zprocess`, `netusage_zliverouteperf` 가 있습니다 [2]. 이 모듈은 남아 있는 행을 읽으므로, [1]이 말한 지운 레코드는 복구 결과와 따로 맞춰 봐야 합니다. Wi-Fi 설정 plist 는 plist 를 읽는 공개 도구로 열어 위 표의 키를 찾습니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [와이파이 기록](wifi.md) | 접속 기기의 네트워크 기록 전체와 다른 AP 연결 시각 |
| [블루투스 장치](bluetooth.md) | 블루투스로 핫스폿에 붙었을 때 두 기기의 페어링 기록 |
| [앱별 데이터 사용량](data-usage.md) | 제공 기기의 셀룰러 사용량 흐름 |
| [기기 정보](../system-account/device-info.md) | 제공 기기의 기기 이름과 접속 기기에 남은 네트워크 이름 |
| [애플 계정](../system-account/apple-account.md) | 인스턴트 핫스폿 조건인 같은 Apple 계정·가족 공유 여부 |
| [통합 로그에서 찾을 것](../logs/unified-log-events.md) | 같은 시각대의 네트워크 이벤트 |
| [타임라인 작성](../../03-techniques/analysis/timeline/index.md) | 두 기기의 시각을 한 줄로 맞추기 |
| [그 시각에 어디 있었나](../../04-scenarios/activity/location.md) | 두 기기가 가까이 있었다는 판단을 위치 흔적과 맞추기 |

## 실습

공개 검체(NIST CFReDS 등)의 아이폰 이미지로 아래 질문을 풀어 봅니다. 검체에 핫스폿 흔적이 없을 수도 있으니, 없으면 없다는 사실과 그 이유(수집 범위, iOS 버전)를 적는 것까지 연습합니다.

1. 검체의 iOS 버전과 수집 방식(로컬 백업인지 파일 시스템 추출인지)을 확인하고, 위 표의 파일 가운데 어느 것이 들어 있는지 적어 봅니다.
2. known-networks 에서 이름이 아이폰 기기 이름처럼 보이는 네트워크를 찾아 `AddedAt`, `JoinedBySystemAt`, `JoinedByUserAt` 을 UTC 로 바꿔 봅니다.
3. networkserviceproxy.plist 안쪽 plist 에서 세션 시작·끝 시각을 꺼내 2번의 시각과 맞춰 봅니다.
4. DataUsage.sqlite 와 WAL 에서 ZPROCESS 의 지운 레코드를 찾아보고, 찾지 못했다면 그 결과를 보고서에 어떻게 적을지 써 봅니다.
5. `com.apple.MobileInternetSharing.plist` 의 `State`·`UState` 값을 핫스폿을 켜고 끈 시험 기기와 비교해 뜻을 검증해 봅니다.

## 참고 문헌

1. GMDSOFT Tech Letter Vol.17 — Detecting Hotspot Connection Evidence on Suspect Devices — https://www.gmdsoft.com/blog/gmdsoft-tech-letter-vol17-detecting-hotspot-connection-evidence-on-suspect-devices/
2. mac4n6.com (Sarah Edwards) — Network and Application Usage using netusage.sqlite & DataUsage.sqlite iOS Databases — http://www.mac4n6.com/blog/2019/1/6/network-and-application-usage-using-netusagesqlite-amp-datausagesqlite-ios-databases
3. Apple Support — Connect to the Personal Hotspot of an iPhone or iPad — https://support.apple.com/en-us/111785
4. Apple Support — Use Instant Hotspot to connect to your Personal Hotspot — https://support.apple.com/en-us/109321
