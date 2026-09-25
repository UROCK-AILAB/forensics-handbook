---
title: "hosts와 DNS 설정"
parent: "아티팩트 · 네트워크"
nav_order: 1700
---

# hosts와 DNS 설정 (hosts·DNS)

맥이 도메인 이름을 어느 주소로 풀지는 hosts 파일, 자동으로 만들어지는 `resolv.conf`, 도메인별 설정을 담는 `/etc/resolver/` 폴더, 네트워크 서비스별 DNS 설정, 구성 프로파일로 넣은 암호화 DNS 설정이 함께 정하고, 이 파일들을 보면 특정 도메인을 다른 곳으로 돌리거나 모든 질의를 한 서버로 모으는 설정이 있었는지 확인할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

hosts 파일은 `/private/etc/hosts` 에 있습니다 [3]. 분석은 원래 없던 줄이 있는지를 찾는 데서 시작하고, 비교할 때는 같은 macOS 버전을 새로 설치한 맥의 hosts 를 기준으로 삼습니다.

`/etc/resolv.conf` 는 기본("primary") DNS 리졸버 클라이언트 설정을 담습니다. macOS 가 이 파일을 자동으로 관리하므로 손으로 고치지 않고, DNS 설정은 네트워크 설정 화면에서 바꿉니다 [1]. 곧 사람이 고치는 파일이 아니라 macOS 가 적용 중인 DNS 설정을 적어 두는 파일이고, 내용은 `/private/var/run/resolv.conf` 경로에서 읽습니다 [3].

`/etc/resolver/` 폴더의 파일은 도메인별 리졸버 설정을 담고, 파일 이름이 곧 도메인 이름입니다 [1]. macOS 의 "Super" DNS 리졸버 클라이언트는 여러 DNS 클라이언트 설정 가운데 질의한 도메인 이름에 맞는 것을 골라 질의를 보내고 [1], 그래서 이 폴더에 도메인 이름 파일이 하나 있으면 그 도메인 질의만 따로 정한 DNS 서버로 갈 수 있습니다.

네트워크 서비스별 DNS 설정은 `/Library/Preferences/SystemConfiguration/preferences.plist` 에 있고 [4], 이 파일의 네트워크 서비스 항목 아래 `DNS` 키에 들어 있습니다 [3]. 조직이나 사용자가 구성 프로파일로 암호화 DNS 를 넣으면 `com.apple.dnsSettings.managed` 페이로드가 설치됩니다 [2].

## 위치와 버전별 차이

| 기록 | 위치 | 알려 주는 것 |
|---|---|---|
| hosts | `/private/etc/hosts` [3] | 이름을 주소로 직접 짝지어 둔 줄 |
| 기본 리졸버 설정 | `/etc/resolv.conf` [1], 실제 파일 `/private/var/run/resolv.conf` [3] | macOS 가 적용 중인 기본 DNS 설정 |
| 도메인별 리졸버 | `/etc/resolver/*` [1] | 도메인마다 따로 정한 DNS 서버와 옵션 |
| 네트워크 서비스별 설정 | `/Library/Preferences/SystemConfiguration/preferences.plist` [3][4] | 서비스별 `DNS` 사전, 프록시, IPv4·IPv6 설정 방식 |
| DHCP 임대 | `/private/var/db/dhcpclient/leases` [3] | 인터페이스별로 받은 IP 와 라우터, 임대 시작 시각 |
| 암호화 DNS 프로파일 | 구성 프로파일의 `com.apple.dnsSettings.managed` 페이로드 [2] | 암호화 DNS 서버 설정과 적용 조건 |

암호화 DNS 페이로드는 macOS 11.0 이상에서 쓸 수 있고, 버전 27.0 에서 사용 중단 표시가 붙어 대체 설정으로 선언형 관리의 `com.apple.configuration.network.dns-settings` 가 나와 있습니다 [2].

| macOS 버전 | 암호화 DNS 설정 방식 |
|---|---|
| 10.15 Catalina | `com.apple.dnsSettings.managed` 페이로드를 쓸 수 없음(11.0 부터) [2] |
| 11.0 ~ 26 | `com.apple.dnsSettings.managed` 페이로드 [2] |
| 27.0 이후 | 위 페이로드는 사용 중단 표시, 선언형 관리 `com.apple.configuration.network.dns-settings` 로 대체 [2] |

설치된 프로파일 목록을 찾는 법은 [구성 프로파일 (Configuration Profiles·MDM)](../persistence/configuration-profiles.md)을 따릅니다.

## 구조

### 도메인별 리졸버 파일

`/etc/resolver/` 아래 파일은 키워드와 값을 적는 텍스트 파일이고, 쓸 수 있는 키워드는 아래와 같습니다 [1].

| 키워드 | 분석에서 보는 점 |
|---|---|
| `nameserver` | 이 도메인 질의를 보낼 DNS 서버 |
| `port` | DNS 서버 포트 |
| `domain` | 도메인 이름 |
| `search` | 검색 도메인 목록 |
| `search_order` | 같은 도메인을 맡은 설정이 여럿일 때 질의를 보내는 순서(값이 작은 것부터) |
| `sortlist` | 돌려받은 주소를 IP·넷마스크 쌍 기준으로 정렬 |
| `timeout` | 응답 기다리는 시간 |
| `options` | 하위 옵션 `debug`, `usevc`, `ndots`, `timeout`, `attempts`, `no_tld_query`, `reload-period` |
### 네트워크 서비스별 설정 (preferences.plist)

`preferences.plist` 는 ForensicArtifacts 에 `MacOSSystemConfigurationPreferencesPlistFile` 이라는 이름으로 올라 있고 [4], 이 파일에서 볼 키는 `NetworkServices`, `DNS`, `UserDefinedName`, `Proxies`, `ExceptionsList`, `IPv4`, `ConfigMethod`, `IPv6`, `Interface`, `DeviceName`, `Hardware`, `Type`, `SMB`, `NetBIOSName`, `Workgroup` 입니다 [3]. 네트워크 서비스와 인터페이스 쪽 칸 전체는 [네트워크 인터페이스와 설정 (SystemConfiguration)](network-interfaces.md)에서 다루고, 여기서는 서비스 항목 아래 `DNS` 사전만 봅니다. `DNS` 사전 안의 하위 키는 실제 파일을 열어 그대로 옮겨 적습니다.

수동으로 넣은 DNS 와 DHCP 로 받은 DNS 가 각각 어디에 남는지, DHCP 임대 파일에 DNS 서버 값이 들어 있는지는 검체에서 확인합니다. DHCP 임대 파일은 mac_apt 가 `Network_DHCP` 표로 내고, 칸은 `Interface`, `MAC_Address`, `IPAddress`, `LeaseLength`, `LeaseStartDate`, `PacketData`, `RouterHardwareAddress`, `RouterIPAddress`, `SSID`, `Source` 입니다 [3].

### 암호화 DNS 페이로드

`com.apple.dnsSettings.managed` 페이로드의 최상위 키는 아래와 같습니다 [2].

| 키 | 필수 | 뜻 |
|---|---|---|
| `DNSSettings` | 필수 | 암호화 DNS 서버 설정을 담은 사전 |
| `OnDemandRules` | 선택 | 적용 조건. 없으면 늘 적용 |
| `ProhibitDisablement` | 선택 | 기본 false. 감독 기기에서만 사용자가 끄지 못하게 함 |

MDM 으로 설치하면 관리되는 Wi-Fi 네트워크에만 적용되고 수동으로 설치하면 셀룰러 네트워크에도 적용되며, 수동 설치는 iOS, macOS, visionOS 에서 허용됩니다 [2].

## 증거로서 의미

**증명하는 것.** hosts 에 기준본에 없는 줄이 있으면 그 이름을 그 주소로 풀도록 누군가 설정해 두었다는 기록이고, `/etc/resolver/` 아래 파일이 있으면 그 파일 이름의 도메인 질의를 따로 정한 서버로 보내도록 설정했다는 기록입니다 [1]. `resolv.conf` 는 macOS 가 자동으로 적는 파일이라 [1] 수동 변조 흔적을 찾는 곳이 아니고, 마지막으로 적용된 기본 DNS 설정을 보는 곳으로 씁니다. 암호화 DNS 프로파일이 설치되어 있으면 `OnDemandRules` 에 적힌 조건 아래에서 DNS 질의를 그 설정의 서버로 보내도록 되어 있었다는 기록입니다 [2].

해석은 조심스럽게 합니다. hosts 에 추가된 줄은 특정 도메인을 가짜 서버로 돌리거나, 보안 업데이트·보안 제품 서버 이름을 자기 자신이나 없는 주소로 막아 두는 흔적일 수 있습니다. `/etc/resolver/` 파일은 사내 도메인이나 VPN 설정으로 흔히 생길 수 있지만 특정 도메인 질의를 가로채는 설정일 수도 있고, 사용자가 모르게 들어간 DNS 프로파일은 모든 질의를 한 서버로 모을 수 있습니다. 이 해석은 설정의 뜻에서 끌어낸 판단이라서, 보고서에는 "이 파일에 이런 줄이 있다" 까지만 쓰고 누가 왜 넣었는지는 다른 기록으로 뒷받침합니다.

**증명하지 못하는 것.** 이 설정들은 그 이름을 실제로 조회했는지, 조회 결과로 어느 서버와 통신했는지 알려 주지 않습니다. hosts 나 resolver 파일만으로는 누가 언제 그 줄을 넣었는지도 알 수 없고, 설정이 있었다는 사실과 그 설정이 실제 통신에 쓰였다는 사실은 따로 입증합니다.

## 시각 해석

hosts, `/etc/resolver/` 파일, `preferences.plist` 에는 시각 값이 없습니다. 그래서 언제 바뀌었는지는 파일 시스템 시각으로 판단하고, 파일 수정 시각은 마지막으로 바뀐 때만 알려 주지 어느 줄이 그때 들어갔는지는 알려 주지 않습니다. 줄이 들어간 무렵을 좁히려면 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)의 해당 경로 기록과, 스냅숏이나 백업에 남은 예전 판을 함께 봅니다. DHCP 임대의 `LeaseStartDate` 는 시각 기준을 밝힌 공개 자료가 없어서, 값을 읽을 때는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에서 후보 기준을 차례로 맞춰 봅니다.

DNS 질의 기록은 통합 로그에서 프로세스 `mDNSResponder`, 서브시스템 `com.apple.mDNSResponder` 로 찾을 수 있지만, 비공개 데이터 표시가 꺼져 있으면 호스트 이름이 가려집니다. 로그 쪽 찾는 법은 [통합 로그에서 찾을 것 (Unified Log Events)](../logs/unified-log-events/index.md)과 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)을 따릅니다.

## 함정과 한계

- `resolv.conf` 는 macOS 가 자동으로 관리하는 파일이라 [1], 여기 적힌 DNS 서버가 언제부터 쓰였는지, 사람이 넣었는지 DHCP 로 받았는지는 이 파일만으로 알 수 없습니다.
- `/private/var/run/resolv.conf` 는 재부팅 뒤에 이미지에 남지 않을 수 있어서, 전원을 끈 뒤 뜬 이미지에서 이 파일이 비었거나 없으면 그 점을 그대로 적습니다.
- `/etc/resolver/` 파일의 도메인은 파일 안이 아니라 파일 이름에 있어서 [1], 파일 내용만 뽑아 두면 어느 도메인 설정인지 잃습니다.
- 도메인별 설정이 있으면 도메인에 따라 다른 서버로 질의가 가서 [1], `resolv.conf` 의 기본 DNS 서버만 보고 모든 질의가 그 서버로 갔다고 쓰면 틀릴 수 있습니다.
- 암호화 DNS 프로파일은 MDM 으로 설치했는지 수동으로 설치했는지에 따라 적용되는 네트워크가 다릅니다 [2].
- 설정 파일을 지우거나 되돌리면 현재 상태에는 흔적이 남지 않습니다. 스냅숏·백업의 예전 판과 FSEvents 를 함께 보고, 방법은 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md)를 따릅니다.
- 라이브에서 지금 적용 중인 DNS 설정을 볼 때의 수집 순서는 [라이브 대응 (Live Response)](../../03-techniques/process-acquisition/live-response/index.md)을 따릅니다.

## 직접 분석해 보기

hosts, `/private/var/run/resolv.conf`, `/etc/resolver/` 폴더 전체, `preferences.plist`, DHCP 임대 폴더를 파일 이름과 시각을 지키는 방식으로 작업 폴더에 복사한 뒤 사본으로 봅니다.

### 헥스로 한 번

`/etc/resolver/` 파일과 hosts 는 텍스트라서, 헥스로 보면 편집기에서 안 보이는 글자까지 확인할 수 있습니다. 아래는 man 페이지 [1]의 키워드로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다. 주소 `192.0.2.53` 은 문서용 예시 주소입니다.

```
파일 이름: example.com   ← 이 이름이 곧 도메인
내용: "nameserver 192.0.2.53" + 줄바꿈 (예시)

6e 61 6d 65 73 65 72 76 65 72 20 31 39 32 2e 30 2e 32 2e 35 33 0a
n  a  m  e  s  e  r  v  e  r  sp 1  9  2  .  0  .  2  .  5  3  \n
```

키워드와 값 사이가 `20`(공백)으로 나뉘고 줄 끝이 `0a` 인지 봅니다. 줄 끝이 `0d 0a` 이거나 키워드 안에 눈에 안 보이는 바이트가 끼어 있으면, 편집기 화면과 다른 그 바이트를 그대로 기록해 둡니다. hosts 도 같은 방식으로 보고, 기준본과 바이트 단위로 비교하면 추가된 줄이 바로 드러납니다.

### 공개 도구로 한 번

mac_apt NETWORKING 플러그인은 hosts, `/private/var/run/resolv.conf`, `preferences.plist`, DHCP 임대 파일, `NetworkInterfaces.plist` 를 읽어 `Network_Details`, `Network_DHCP` 같은 표로 냅니다 [3]. 결과 표에서 서비스별 `DNS` 값과 DHCP 임대의 `SSID`, `RouterIPAddress` 를 나란히 놓으면 어떤 네트워크에서 어떤 설정이 쓰였을지 좁힐 수 있습니다. `/etc/resolver/` 폴더는 따로 파일 목록을 뽑아 파일 이름과 내용, 파일 시스템 시각을 함께 적어 둡니다. `preferences.plist` 는 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에 나오는 plist 도구로 직접 열어 `DNS` 사전을 확인합니다.

## 교차 검증

- [네트워크 인터페이스와 설정 (SystemConfiguration)](network-interfaces.md) — 같은 `preferences.plist` 의 서비스·인터페이스 설정과 맞춰 봅니다.
- [구성 프로파일 (Configuration Profiles·MDM)](../persistence/configuration-profiles.md) — 암호화 DNS 프로파일이 언제, 어떤 방식으로 설치됐는지 봅니다.
- [VPN 구성 (VPN)](vpn.md) — `/etc/resolver/` 파일이 VPN 연결과 함께 생긴 설정인지 봅니다.
- [와이파이 기록 (Wi-Fi)](wifi.md) — DHCP 임대의 `SSID` 와 와이파이 연결 기록을 맞춰 봅니다.
- [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) — hosts 와 resolver 파일이 언제 바뀌었는지 좁힙니다.
- [공유 폴더 연결 기록 (SMB·AFP)](network-shares.md) — 서버 이름으로 붙은 공유가 어느 주소로 풀렸을지 봅니다.
- [악성 코드 지속성 찾기 (Persistence)](../../04-scenarios/incident/persistence.md), [정보 탈취 악성 코드 (Infostealer)](../../04-scenarios/incident/infostealer.md) — 이 설정을 쓰는 침해 사고 조사 흐름입니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 검체의 hosts 를 같은 macOS 버전의 기준본과 비교하면 추가된 줄이 있나요? 있다면 그 줄은 어떤 이름을 어떤 주소로 돌리나요?
2. `/etc/resolver/` 폴더에 파일이 있나요? 있다면 파일 이름(도메인)과 `nameserver` 값을 표로 정리하고, 사내 도메인·VPN 설정으로 설명되는지 보세요.
3. `/private/var/run/resolv.conf` 가 이미지에 남아 있나요? 남아 있다면 적힌 DNS 서버가 `preferences.plist` 의 서비스별 `DNS` 사전 값과 같은가요?
4. DHCP 임대 파일의 `SSID`·`RouterIPAddress`·`LeaseStartDate` 를 뽑고, `LeaseStartDate` 를 어떤 시각 기준으로 읽어야 말이 되는지 확인해 보세요.
5. 구성 프로파일 가운데 `com.apple.dnsSettings.managed` 페이로드가 있나요? 있다면 `OnDemandRules` 와 `ProhibitDisablement` 값은 무엇이고, 검체의 macOS 버전에서 이 페이로드를 쓸 수 있나요?
6. hosts 와 resolver 파일의 수정 시각 무렵 FSEvents 에는 어떤 프로세스나 경로 변화가 함께 남아 있나요?

## 참고 문헌

1. resolver(5) man 페이지 (Xcode man pages 모음) — https://keith.github.io/xcode-man-pages/resolver.5.html
2. Apple Developer, Device Management "DNSSettings" (문서 JSON) — https://developer.apple.com/tutorials/data/documentation/devicemanagement/dnssettings.json
3. mac_apt `plugins/networking.py` (NETWORKING 1.0, Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/networking.py
4. ForensicArtifacts `artifacts/data/macos.yaml` — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
