---
title: "VPN 구성"
parent: "아티팩트 · 네트워크"
nav_order: 1680
---

# VPN 구성 (VPN)

맥의 VPN 설정은 관리 프로필의 VPN 페이로드와 시스템 네트워크 설정의 서비스 항목에 남고, VPN 종류와 제품을 가리키는 번들 ID 를 보면 이 맥에 어떤 VPN 이 설정되어 있었는지 추정할 수 있습니다. 언제 접속했는지 알 수 있는 기록은 실제 기기에서 찾아야 합니다.

## 무엇을 기록하나 · 왜 생기나

VPN 은 관리 프로필로 넣을 수도 있고 네트워크 설정에 직접 만들 수도 있습니다. 관리 프로필의 VPN 페이로드는 macOS 10.7 부터 쓸 수 있고, macOS 에서는 기기 채널과 사용자 채널 둘 다로 배포되며 직접 설치도 허용됩니다 [1]. 페이로드에는 기기에 보이는 VPN 이름과 VPN 종류가 반드시 들어가고, 플러그인이나 네트워크 확장 (network extension) 방식 VPN 이면 제품을 가리키는 번들 ID 도 들어갑니다 [1].

디스크 쪽에서는 `/Library/Preferences/SystemConfiguration/preferences.plist` 의 `NetworkServices` 항목에 `PPP` 사전이 있을 수 있고, mac_apt 가 이 값을 뽑습니다 [2]. 이 파일의 서비스 구조 전체는 [네트워크 인터페이스와 설정 (SystemConfiguration)](network-interfaces.md)에서 다룹니다.

## 위치와 버전별 차이

| 기록 | 위치 | 비고 |
|---|---|---|
| VPN 페이로드 (`com.apple.vpn.managed`) | 설치된 구성 프로필 | macOS 10.7 부터 [1]. 프로필이 디스크에 남는 곳은 [구성 프로파일 (Configuration Profiles·MDM)](../persistence/configuration-profiles.md) |
| 앱별 VPN 페이로드 (`AppLayerVPN`, `AppToAppLayerVPNMapping`) | 설치된 구성 프로필 | VPN 페이로드와 따로 있습니다 [1] |
| 네트워크 서비스의 `PPP` 사전 | `/Library/Preferences/SystemConfiguration/preferences.plist` | mac_apt 가 뽑습니다 [2] |

`VPNType` 값 가운데 `TransparentProxy` 는 macOS 에서만 쓰고 그 설정 사전은 macOS 14 부터이며, `AlwaysOn` 은 iOS 에서만 씁니다 [1]. macOS 10.15 이후 버전마다 디스크 쪽 저장 방식이 어떻게 달라지는지는 공개 자료가 없습니다.

### 실제 기기에서 확인할 것

| 항목 | 상태 |
|---|---|
| 네트워크 확장 방식 VPN 설정의 저장 위치(`/Library/Preferences/com.apple.networkextension.plist` 로 알려짐)와 형식 | 공개 자료 없음 |
| VPN 서비스의 `Interface/Type`, `SubType` 실제 값 | 공개 자료 없음 |
| VPN 접속·해제가 남는 통합 로그 서브시스템, 옛 `/var/log/ppp.log` | 공개 자료 없음 |
| VPN 비밀번호·공유 비밀이 키체인에 들어가는지 | 공개 자료 없음 |
| `netusage.sqlite` 에 VPN 연결이 따로 잡히는지 | 공개 자료 없음 |

## 구조

### VPN 페이로드 (`com.apple.vpn.managed`)

필수 키는 `UserDefinedName`(기기에 보이는 VPN 이름)과 `VPNType` 입니다 [1].

| `VPNType` 값 | 비고 |
|---|---|
| `VPN` | `VPNSubType` 필수 |
| `L2TP` | |
| `IPSec` | |
| `IKEv2` | |
| `AlwaysOn` | iOS 에서만 |
| `TransparentProxy` | macOS 에서만, `VPNSubType` 필수 |

`VPNSubType` 은 플러그인 방식 VPN 이면 플러그인의 번들 ID 이고, 네트워크 확장 제공자라면 제공자를 담은 앱의 번들 ID 입니다 [1]. 대표적인 값은 아래와 같고 [1], 실제 값을 이런 모양의 번들 ID 로 보고 어느 제품의 설정인지 추정합니다.

| 제품 | `VPNSubType` |
|---|---|
| Cisco AnyConnect | `com.cisco.anyconnect.applevpn.plugin` |
| Juniper SSL | `net.juniper.sslvpn` |
| F5 SSL | `com.f5.F5-Edge-Client.vpnplugin` |
| SonicWALL Mobile Connect | `com.sonicwall.SonicWALL-SSLVPN.vpnplugin` |
| Aruba VIA | `com.arubanetworks.aruba-via.vpnplugin` |

번들 ID 를 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md)를 따릅니다. 나머지 사전 키는 `IKEv2`, `IPSec`, `IPv4`, `PPP`(L2TP·PPTP 용), `Proxies`, `DNS`, `VPN`, `VendorConfig`, `TransparentProxy`, `AlwaysOn` 이고, `VendorConfig` 는 `VPNSubType` 이 있을 때만 읽습니다 [1].

### preferences.plist 의 PPP 사전

`NetworkServices` 의 서비스 항목 안에 `PPP` 사전이 있으면 mac_apt 가 이를 뽑습니다 [2]. 이 사전 안의 키와, VPN 서비스를 가리키는 `Interface/Type`·`SubType` 값은 알려져 있지 않아서, 실제 파일에서 연 값을 그대로 옮겨 적습니다. 같은 서비스의 `UserDefinedName` 과 `Interface` 사전을 함께 적어 두면 어떤 이름의 서비스인지 설명할 수 있습니다 [2].

## 증거로서 의미

**증명하는 것.** VPN 페이로드가 설치되어 있으면 이 맥에 그 이름(`UserDefinedName`)과 종류(`VPNType`)의 VPN 설정이 들어갔다는 기록이고, `VPNSubType` 의 번들 ID 는 어느 VPN 제품이나 앱이 연결을 맡도록 설정됐는지 추정하는 근거가 됩니다 [1]. 이 추정은 페이로드 정의에서 끌어낸 해석이라서, 그 번들 ID 의 앱이 실제로 설치되어 있었는지를 [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md)으로 함께 확인합니다. `preferences.plist` 의 서비스에 `PPP` 사전이 있으면 그 서비스에 PPP 설정이 들어 있었다는 기록입니다 [2].

**증명하지 못하는 것.** 설정이 있다는 사실은 VPN 에 접속했다는 뜻이 아니고, 언제 접속했는지, 어느 서버로 얼마나 주고받았는지도 알려 주지 않습니다. 접속 기록이 남는 로그 위치는 공개 자료가 없습니다. 관리 프로필로 들어온 설정이라면 사용자가 직접 만든 것이 아니라 조직이 배포한 것일 수 있어서, 설정이 있다는 사실로 사용자의 의도를 읽지 않습니다.

VPN 은 조직의 정상 접속 수단이면서 트래픽 출처를 가리는 수단으로도 쓰일 수 있어서, 자료 유출이나 원격 접속을 따질 때 VPN 설정이 있으면 그 무렵 네트워크 기록의 출발 주소를 해석할 때 함께 적습니다. 보고서에는 "이 맥에 `VPNType` 이 `IKEv2` 이고 이름이 이것인 VPN 페이로드가 설치되어 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

VPN 페이로드 키와 `PPP` 사전에는 알려진 시각 값이 없습니다. 설정이 들어온 무렵은 구성 프로필의 설치 기록과 `preferences.plist` 의 파일 수정 시각, [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)로 좁히고, 파일 수정 시각은 마지막으로 바뀐 때만 알려 줄 뿐 VPN 서비스가 그때 생겼다는 뜻은 아니라는 점을 함께 적습니다. 시각 값의 기준은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다.

## 함정과 한계

- **설정과 접속은 다릅니다.** 페이로드나 서비스 항목은 설정이 있었다는 기록일 뿐이고, 접속 기록이 남는 위치는 공개 자료가 없습니다.
- **두 종류의 설정.** 관리 프로필로 들어온 VPN 과 네트워크 설정에 직접 만든 VPN 은 남는 곳이 달라서, 한쪽만 보면 다른 쪽을 놓칩니다.
- **네트워크 확장 방식.** 네트워크 확장 제공자 방식 VPN 의 설정이 디스크 어디에 남는지는 공개 자료가 없어서, `preferences.plist` 에 없다고 VPN 설정이 없다고 단정하지 않습니다.
- **앱별 VPN.** `AppLayerVPN`, `AppToAppLayerVPNMapping` 은 VPN 페이로드와 따로 있어서 [1], 프로필을 볼 때 이 두 페이로드도 함께 찾습니다.
- **비밀 값.** VPN 비밀번호와 공유 비밀이 키체인에 들어가는지는 실제 기기에서 확인하고, 키체인 구조는 [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md)에서 다룹니다.

## 직접 분석해 보기

원본을 바로 열지 말고 `preferences.plist` 와 설치된 구성 프로필 파일을 파일 시각을 지키는 방식으로 작업 폴더에 복사한 뒤 사본으로 봅니다.

### 헥스로 한 번

`preferences.plist` 를 헥스 편집기로 열어 바이너리 plist 인지 XML 인지 첫 바이트로 구분하고, 바이너리라면 오프셋 표를 따라 `PPP` 키 문자열이 든 객체를 찾아갑니다. 머리말과 오프셋 표를 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에서 다룹니다.

설치된 프로필의 VPN 페이로드는 아래처럼 페이로드 키 [1]로 만든 예시와 맞춰 봅니다. 실제 기기에서 나온 값이 아니고, 이름 `Example VPN` 과 번들 ID `com.example.vpnclient` 은 예시로 지은 값이며, 페이로드의 나머지 공통 키와 `VendorConfig` 내용은 생략했습니다.

```xml
<dict>
    <key>UserDefinedName</key>
    <string>Example VPN</string>
    <key>VPNType</key>
    <string>VPN</string>
    <key>VPNSubType</key>
    <string>com.example.vpnclient</string>
</dict>
```

`VPNType` 이 `VPN` 이라서 `VPNSubType` 이 반드시 있고 [1], 이 번들 ID 가 연결을 맡는 플러그인이나 네트워크 확장 제공자 앱을 가리킵니다.

### 공개 도구로 한 번

macOS 의 `plutil` 로 `preferences.plist` 사본을 열어 `NetworkServices` 에서 `PPP` 사전이 있는 서비스를 찾고, 그 서비스의 `UserDefinedName` 과 `Interface` 사전을 함께 옮겨 적습니다.

```
plutil -p preferences.plist
```

mac_apt NETWORKING 플러그인 [2]을 돌려 같은 서비스의 `PPP` 값이 나오는지 맞춰 보면, 직접 읽은 값과 도구 결과를 서로 검증할 수 있습니다. 설치된 프로필에서 `com.apple.vpn.managed` 페이로드를 찾는 법은 구성 프로파일 페이지를 따릅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [구성 프로파일 (Configuration Profiles·MDM)](../persistence/configuration-profiles.md) | VPN 페이로드와 앱별 VPN 페이로드가 설치되어 있었는지, 설치 시각 |
| [네트워크 인터페이스와 설정 (SystemConfiguration)](network-interfaces.md) | `PPP` 사전이 있는 서비스와 붙은 인터페이스 |
| [hosts와 DNS 설정 (hosts·DNS)](hosts-dns.md) | VPN 과 함께 생긴 도메인별 DNS 설정 |
| [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) | `VPNSubType` 번들 ID 의 앱이 설치되어 있었는지 |
| [커널·시스템 확장 (KEXT·System Extension)](../persistence/kext-system-extension.md) | VPN 앱이 올린 확장이 있었는지 |
| [원격 접속 침입 확인 (Remote Intrusion)](../../04-scenarios/incident/remote-intrusion.md) | 접속 기록의 출발 주소를 VPN 설정과 함께 해석하는 흐름 |

## 실습

공개 시험 데이터(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. `preferences.plist` 의 `NetworkServices` 에 `PPP` 사전이 있는 서비스가 있나요? 있다면 그 서비스의 `UserDefinedName` 과 `Interface` 사전을 옮겨 적어 보세요.
2. 설치된 구성 프로필 가운데 페이로드 형식이 `com.apple.vpn.managed` 인 것이 있나요? 있다면 `UserDefinedName`, `VPNType`, `VPNSubType` 을 표로 정리해 보세요.
3. `VPNSubType` 의 번들 ID 에 해당하는 앱이 `/Applications` 에 있나요?
4. `AppLayerVPN` 이나 `AppToAppLayerVPNMapping` 페이로드가 있다면 어떤 앱에 VPN 을 걸도록 했는지 적어 보세요.

## 참고 문헌

1. Apple Developer, Device Management — VPN — https://developer.apple.com/documentation/devicemanagement/vpn
2. mac_apt `networking.py` NETWORKING 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/networking.py
