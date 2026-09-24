# Wi-Fi 프로필 (WLAN Profiles)

## 한 줄 요약

윈도는 무선 네트워크 설정을 프로필마다 XML 파일 하나로 저장합니다. 파일에는 SSID 와 인증 방식이 들어 있고, 키를 쓰는 네트워크면 암호화된 키도 들어 있습니다. 만든 시각이나 연결한 시각은 들어 있지 않습니다.

## 무엇을 기록하나 · 왜 생기나

- 무선 프로필 (wireless profile) 은 WLAN_profile 스키마를 따르는 XML 입니다.
- 프로필은 이 PC 에 저장해 둔 무선 네트워크 설정입니다. 연결 기록이 아닙니다.
- 프로필에는 모든 사용자용 (all-user) 과 사용자별 (per-user) 이 있습니다.
- 무선 LAN API 의 WlanGetProfile 결과에 `WLAN_PROFILE_USER` 플래그가 없으면 모든 사용자용 프로필입니다.
- 그룹 정책으로 만든 프로필은 `WLAN_PROFILE_GROUP_POLICY` 플래그로 구분합니다.
- 그룹 정책 프로필은 읽기 전용입니다. 내용도 우선순위도 바꿀 수 없습니다.
- 프로필 이름은 대소문자를 가리고, 최대 255자입니다.
- Windows 11 PC 한 대에서 무선 프로필 9개는 모두 프로필 이름이 SSID 이름과 같았습니다. (확인 범위: Win11 25H2 한 대)
- 같은 PC 의 AP 프로필 (`WLANAPProfile`) 1개는 프로필 이름이 SSID 이름과 달랐습니다. 이 프로필이 모바일 핫스팟 설정인지는 확인하지 못했습니다. (확인 범위: Win11 25H2 한 대)

## 위치와 버전별 차이

Windows 11 PC 한 대에서 본 위치는 아래와 같습니다. (확인 범위: Win11 25H2 한 대)

```
C:\ProgramData\Microsoft\Wlansvc\Profiles\Interfaces\{인터페이스 GUID}\{프로필 GUID}.xml
```

- 인터페이스 GUID 폴더는 2개였습니다. 두 폴더 이름 모두 `SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces` 의 하위 키 이름과 같았습니다. 어댑터 이름을 찾는 방법은 [네트워크 인터페이스 설정](tcp-ip-interfaces.md) 에서 다룹니다.
- 한 폴더에는 무선 프로필 (`WLANProfile`) 9개가 있었습니다. 다른 폴더에는 AP 프로필 1개가 있었습니다.
- 프로필 XML 파일 이름의 GUID 는 [네트워크 목록](networklist.md) 의 프로필 GUID 와 하나도 같지 않았습니다(0/10).
- `Wlansvc` 폴더 아래에는 `Profiles` 폴더만 있었습니다.
- 관리자 권한 셸에서는 이 폴더가 읽혔습니다. 일반 사용자 권한으로 읽히는지는 확인하지 못했습니다.

버전별 차이는 WlanGetProfile 문서로 확인한 것만 적습니다.

| Windows | 달라지는 점 |
|---|---|
| XP SP2·SP3 (XP 용 무선 LAN API) | 프로필 이름을 SSID 에서 자동으로 정합니다. 일반 네트워크는 SSID 그대로, 애드혹은 SSID 뒤에 `-adhoc` 이 붙습니다. 사용자별 프로필을 지원하지 않습니다. 키를 암호화하지 않고 돌려줍니다 |
| Vista·Server 2008 | WlanGetProfile 이 돌려주는 키가 늘 암호화돼 있습니다 |
| 7 이후 | 평문 키를 따로 요청할 수 있습니다 (아래 "키" 절) |

- WlanGetProfile 은 Windows Vista·XP SP3·Server 2008 이후에 있습니다.
- Vista·7·8 에서도 파일이 위와 같은 경로에 있는지는 이번에 확인하지 못했습니다.
- XP (무선 제로 구성) 시절의 저장 위치와 사용자별 프로필의 디스크 위치도 확인하지 못했습니다.

## 구조

### XML 요소

- 네임스페이스는 `http://www.microsoft.com/networking/WLAN/profile/v1` 이고, 루트 요소는 `WLANProfile` 입니다. (확인 범위: Win11 25H2 한 대)
- 각 요소의 공식 정의는 이번에 열어 보지 못했습니다. 아래 표에는 요소 이름과 Windows 11 PC 한 대에서 본 값만 적습니다. (확인 범위: Win11 25H2 한 대)

| 요소 | 이 PC 에서 본 내용 |
|---|---|
| `name` | 프로필 이름 |
| `SSIDConfig/SSID/hex` | SSID 바이트를 16진수로 쓴 값. 10개 모두 풀면 `SSID/name` 과 같았습니다 |
| `SSIDConfig/SSID/name` | SSID 이름 |
| `connectionType` | 값은 따로 정리하지 않았습니다 |
| `connectionMode` | `auto`·`manual` |
| `MSM/security/authEncryption/authentication` | `open`·`WPA2PSK`·`WPA3SAE` |
| `MSM/security/authEncryption/encryption` | `WEP`·`AES` |
| `MSM/security/authEncryption/useOneX` | 값은 따로 정리하지 않았습니다 |
| `MSM/security/authEncryption/transitionMode` | 일부 프로필에만 있었습니다 |
| `sharedKey/keyType` | `networkKey`(WEP)·`passPhrase` |
| `sharedKey/protected` | 키가 있는 9개 모두 `true` |
| `sharedKey/keyMaterial` | 키. 아래 "키" 절 |
| `MacRandomization/enableRandomization`, `randomizationSeed` | 값의 뜻은 확인하지 못했습니다 |

- AP 프로필 (`WLANAPProfile`) 에는 `name`, `SSIDConfig`, `MSM/connectivity/maxNumberOfClients`, `security`(`authEncryption`·`transitionMode`·`sharedKey`) 가 있었습니다. (확인 범위: Win11 25H2 한 대)
- 프로필 XML 안에는 만든 시각이나 마지막 연결 시각을 적는 칸이 없었습니다. (확인 범위: Win11 25H2 한 대)

### 키 (keyMaterial)

WlanGetProfile 문서가 적는 내용은 아래와 같습니다.

- WlanGetProfile 이 돌려주는 `keyMaterial` 은 기본으로 암호화돼 있습니다.
- 같은 컴퓨터에서 LocalSystem 계정으로 도는 프로세스는 CryptUnprotectData 로 이 키를 풀 수 있습니다.
- Windows 7 이후에는 `WLAN_PROFILE_GET_PLAINTEXT_KEY` 플래그로 평문 키를 요청할 수 있습니다.
- 이 요청은 기본으로 로컬 Administrators 그룹 구성원만 할 수 있습니다.
- 권한이 없으면 오류를 내지 않고 암호화된 키를 돌려줍니다.
- WEP 키는 ASCII 5자로 넣든 16진 10자로 넣든 16진 10자로 저장하고 돌려줍니다.

디스크의 XML 파일에서 본 모습은 아래와 같습니다. (확인 범위: Win11 25H2 한 대)

- 키가 있는 프로필 9개 모두 `protected` 가 `true` 였습니다.
- 9개 모두 `keyMaterial` 이 16진 `01000000D08C9DDF0115D1118C7A00C04FC297EB` 로 시작했습니다.
- 이 머리는 DPAPI 블롭의 머리로 알려진 모양입니다. 블롭 구조는 [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) 에서 다룹니다.
- `netsh wlan export profile` 로 `key=clear` 없이 내보낸 XML 의 `keyMaterial` 도 같은 머리로 시작했습니다.

오프라인 이미지에서 이 키를 푸는 절차는 이번에 연 자료로 확인하지 못했습니다. WlanGetProfile 문서는 같은 컴퓨터의 LocalSystem 프로세스가 CryptUnprotectData 로 푸는 데까지만 적습니다. 시스템 계정 DPAPI 는 [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

- 이 PC 에 이 SSID 의 무선 네트워크 설정이 저장돼 있었습니다.
- 그 설정의 인증 방식·암호화 방식·`connectionMode` 값을 알 수 있습니다.
- 프로필이 어느 인터페이스(어댑터) 폴더에 있는지로 어느 무선 어댑터에 딸린 설정인지 좁힐 수 있습니다.
- 키를 풀 수 있으면 그 네트워크에 쓰던 키를 알 수 있습니다.

### 증명하지 못하는 것

- **연결했는지.** 설정을 저장만 하고 연결하지 않았는지는 프로필만으로 알 수 없습니다.
- **언제 연결했는지.** XML 안에 시각이 없습니다. 연결 여부와 시각은 [네트워크 목록](networklist.md)·[네트워크 연결 이벤트](../event-logs/wlan-autoconfig-networkprofile.md)·[SRUM](../execution/system-resource-usage-monitor/index.md) 에서 봅니다.
- **누가 만들었는지.** Windows 11 PC 한 대에서 본 XML 요소에는 사용자를 가리키는 칸이 없었습니다. (확인 범위: Win11 25H2 한 대)
- **키의 평문.** 디스크에는 암호화된 키만 있습니다. 키를 풀지 못하면 SSID·인증 방식까지만 씁니다.

보고서에는 "이 PC 의 무선 프로필 폴더에 SSID 가 이 이름인 프로필 파일이 있고, 인증 방식은 WPA2PSK 로 적혀 있다" 처럼 씁니다.

## 시각 해석

- XML 안에 시각이 없으므로 파일 시스템 시각($STANDARD_INFORMATION)을 봅니다. 읽는 법은 [마스터 파일 테이블](../filesystem/mft.md) 에서 다룹니다.
- 파일 생성 시각이 곧 프로필을 처음 만든 때라고 단정하지 않습니다. Windows 11 PC 한 대에서 본 모습은 아래와 같습니다. (확인 범위: Win11 25H2 한 대)

| 본 것 | 값 |
|---|---|
| 레지스트리 InstallDate | 2026-06-27 03:07 (현지 시각) |
| 생성 시각이 2026-06-26 인 프로필 파일 | 10개 (AP 프로필 포함) 가운데 7개 |
| 그중 수정 시각이 생성 시각보다 앞선 파일 | 6개 (수정 시각 2025-04 ~ 2026-06) |
| 업그레이드 날 생성된 파일 가운데 나중에 수정된 파일 | 1개 (수정 시각 2026-09-16). 무엇 때문에 바뀌었는지는 확인하지 못했습니다 |

- 이 모습은 윈도 업그레이드 때 파일을 옮기면서 생성 시각만 새로 찍힌 것으로 보입니다. 원인은 확인하지 못했습니다.
- InstallDate 가 기능 업데이트 때 바뀌는지도 확인하지 못했습니다. InstallDate 는 [시스템 기본 정보](../system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 다룹니다.
- 업그레이드 뒤에 새로 만든 프로필 2개는 XML 생성 시각과 네트워크 목록의 DateCreated 가 거의 같았습니다. 한 건은 XML 이 2026-06-27 03:08:23, DateCreated 가 03:08:24 였습니다. 다른 한 건은 둘 다 2026-09-18 12:38 대였습니다. 둘 다 현지 시각입니다.
- 업그레이드로 옮겨진 프로필 2개는 반대로 DateCreated 가 2026-09-04 로 XML 보다 늦었습니다.
- 위 대응은 네트워크 목록의 `Description` 이름으로 맞춘 것입니다. 같은 이름의 프로필이 둘이면 틀릴 수 있습니다.

## 함정과 한계

- **수정 시각이 생성 시각보다 앞서도 조작으로 단정하지 않습니다.** 업그레이드 때 파일을 옮기면 이런 모습이 나올 수 있습니다. [시스템 기본 정보](../system-account/os-version-computer-name-install-date-shutdown-t.md) 의 설치 시각과 먼저 맞춰 봅니다.
- **라이브 명령 결과와 파일 수가 다를 수 있습니다.** Windows 11 PC 한 대에서 `netsh wlan show profiles` 는 "All User Profile" 9개를 보였습니다. 같은 PC 에서 `netsh wlan export profile` 은 파일 6개만 만들었습니다. 이유는 확인하지 못했습니다. (확인 범위: Win11 25H2 한 대)
- **네트워크 목록과 GUID 로 이어지지 않습니다.** 파일 이름 GUID 가 네트워크 목록 프로필 GUID 와 달랐습니다. 이름으로 맞춰야 합니다.
- **이름도 늘 같지는 않습니다.** Windows 11 PC 한 대에서 프로필 이름 10개 가운데 4개만 네트워크 목록의 `ProfileName` 과 같았습니다. (확인 범위: Win11 25H2 한 대)
- **SSID 는 hex 값으로도 맞춥니다.** `SSIDConfig/SSID/hex` 는 SSID 바이트 그대로입니다. 네트워크 목록과 TCP/IP 인터페이스 키에도 SSID 를 16진수로 적은 값이 있습니다.
- **프로필 이름은 대소문자를 가립니다.** 대소문자만 다른 두 프로필을 같은 것으로 합치지 않습니다.
- **파일이 없으면 이전 시점을 봅니다.** 프로필을 지울 때 파일이 어떻게 되는지는 이번에 확인하지 못했습니다. [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 과 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 로 이전 시점의 파일을 찾아봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 XML 은 요소 구조를 보여 주려고 만든 예시입니다. 특정 검체에서 꺼낸 파일이 아닙니다. SSID 는 `HOME` 으로 정했고, 요소 일부를 줄였습니다.

```xml
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
  <name>HOME</name>
  <SSIDConfig>
    <SSID>
      <hex>484F4D45</hex>
      <name>HOME</name>
    </SSID>
  </SSIDConfig>
  <connectionMode>auto</connectionMode>
  <MSM>
    <security>
      <authEncryption>
        <authentication>WPA2PSK</authentication>
        <encryption>AES</encryption>
      </authEncryption>
      <sharedKey>
        <keyType>passPhrase</keyType>
        <protected>true</protected>
        <keyMaterial>01000000D08C9DDF0115D1118C7A00C04FC297EB…</keyMaterial>
      </sharedKey>
    </security>
  </MSM>
</WLANProfile>
```

**SSID 풀기.**

```
hex   48 4F 4D 45
문자   H  O  M  E
```

1. `hex` 값을 두 자리씩 끊습니다.
2. 각 바이트를 문자로 바꾸면 `HOME` 입니다. `name` 과 같습니다.

**keyMaterial 머리 읽기.** 아래 20바이트는 Windows 11 PC 한 대의 프로필 9개에 공통으로 있던 머리입니다. 그 뒤는 줄였습니다. (확인 범위: Win11 25H2 한 대)

```
오프셋  바이트                                              읽은 값
0x00    01 00 00 00                                         1 (리틀 엔디언 4바이트)
0x04    D0 8C 9D DF 01 15 D1 11 8C 7A 00 C0 4F C2 97 EB     {DF9D8CD0-1501-11D1-8C7A-00C04FC297EB}
```

1. 앞 4바이트를 리틀 엔디언으로 읽으면 1 입니다.
2. 다음 16바이트를 GUID 로 읽습니다. 앞 세 묶음(4·2·2바이트)은 바이트 순서를 뒤집고, 나머지 8바이트는 그대로 씁니다.
3. 이 머리로 시작하면 DPAPI 블롭으로 보고 [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) 의 방법으로 읽습니다.

### 공개 도구로 한 번

1. 이미지에서 `Wlansvc\Profiles\Interfaces` 폴더를 통째로 꺼냅니다.
2. 인터페이스 GUID 폴더마다 [네트워크 인터페이스 설정](tcp-ip-interfaces.md) 의 방법으로 어댑터 이름을 찾습니다.
3. XML 파일을 텍스트 편집기나 XML 뷰어로 열어 `name`·`SSID/hex`·`authentication`·`encryption`·`connectionMode` 를 표로 적습니다.
4. 공개 MFT 파서로 각 XML 파일의 생성·수정 시각을 뽑습니다.
5. 라이브 시스템이면 `netsh wlan show profiles` 결과와 폴더의 파일 수를 비교합니다.
6. `netsh wlan export profile` 로 내보낸 파일 이름은 `<인터페이스 이름>-<프로필 이름>.xml` 모양이었습니다. 이 이름으로 인터페이스 이름도 확인할 수 있습니다. (확인 범위: Win11 25H2 한 대)

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 네트워크 목록 | 같은 이름 네트워크를 처음 본 때와 마지막 연결 시각 | [네트워크 목록](networklist.md) |
| 네트워크 인터페이스 설정 | 인터페이스 GUID 의 어댑터, SSID 별 DHCP 임대 | [네트워크 인터페이스 설정](tcp-ip-interfaces.md) |
| 네트워크 연결 이벤트 | 연결 시각 | [네트워크 연결 이벤트](../event-logs/wlan-autoconfig-networkprofile.md) |
| SRUM | 네트워크 연결 기록 | [SRUM](../execution/system-resource-usage-monitor/index.md) |
| 마스터 파일 테이블 | 프로필 파일의 생성·수정 시각 | [마스터 파일 테이블](../filesystem/mft.md) |
| DPAPI | `keyMaterial` 블롭 구조 | [DPAPI 구조](../../01-foundations/protection/data-protection-api/index.md) |

## 실습

공개 검체(NIST CFReDS 등)에서 `Wlansvc` 폴더와 SYSTEM·SOFTWARE 하이브를 꺼내 아래 질문을 풀어 봅니다.

1. 인터페이스 GUID 폴더는 몇 개입니까? 각 폴더는 어느 어댑터입니까?
2. 무선 프로필은 몇 개입니까? 프로필 이름과 SSID 이름이 다른 것이 있습니까?
3. `SSID/hex` 를 직접 풀어서 `SSID/name` 과 같은지 확인해 봅니다.
4. `authentication` 값이 `open` 인 프로필이 있습니까?
5. `keyMaterial` 은 어떤 머리로 시작합니까?
6. 프로필 파일의 생성 시각과 네트워크 목록의 DateCreated 를 이름으로 맞춰 보면 얼마나 차이 납니까?

## 참고 문헌

1. Microsoft Learn, *WlanGetProfile function (wlanapi.h)* (프로필 XML 스키마, 모든 사용자용·사용자별·그룹 정책 프로필 플래그, 프로필 이름 규칙, XP 용 API 차이, keyMaterial 암호화와 평문 키 플래그, WEP 키 저장 형식, 지원 버전). https://learn.microsoft.com/en-us/windows/win32/api/wlanapi/nf-wlanapi-wlangetprofile
