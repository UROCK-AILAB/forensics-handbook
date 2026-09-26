---
title: "VPN 설정"
parent: "아티팩트 · 네트워크·연결"
nav_order: 690
---

# VPN 설정 (VPN)

아이폰의 VPN 구성은 네트워크 확장(Network Extension) 설정 plist 와 구성 프로파일에 남고, 이 흔적으로 기기에 어떤 방식의 VPN 이 설정되어 있었는지 짚어 볼 수 있습니다. 다만 로컬 백업의 키에는 접속 이력으로 보이는 값이 없습니다.

## 무엇을 기록하나 · 왜 생기나

Apple 기기가 지원하는 VPN 연결 방식은 IKEv2, L2TP over IPsec, Cisco IPsec 과, 네트워크 확장 프레임워크로 만든 앱 기반 방식입니다 [1]. 특정 업체의 VPN 을 쓰려면 그 업체의 앱을 설치하고 필요하면 구성을 함께 넣고 [1], 회사나 학교가 관리하는 기기라면 기기 관리 프로필로 VPN 을 배포할 수 있습니다 [1]. 사용자가 설정 앱에서 직접 넣든, 앱이 넣든, 프로필이 넣든 기기에는 VPN 구성이 저장되고, 조사에서는 "이 기기가 통신을 VPN 으로 돌렸을 수 있나" 와 "누가 그 구성을 넣었나" 를 묻는 단서가 됩니다.

VPN 에는 몇 가지 운영 방식이 있습니다. 앱별 VPN(Per-App VPN)은 iOS·iPadOS·macOS·visionOS 와 감독 모드 watchOS 에서 앱마다 트래픽을 나누고, 항상 켜진 VPN(Always On VPN)은 iOS·iPadOS·visionOS 의 IKEv2 에서 쓸 수 있으며 사용자 조작 없이 켜지고 재시동 뒤에도 유지됩니다 [1]. 항상 켜진 VPN 이 설정된 기기라면 모든 통신이 VPN 을 거쳤을 수 있어서, 네트워크 기록을 해석할 때 먼저 확인합니다.

## 위치와 버전별 차이

암호화하지 않은 로컬 백업의 VPN 관련 파일과 도메인은 다음과 같습니다.

| 도메인 :: 상대 경로 | 내용 |
|---|---|
| `SystemPreferencesDomain :: com.apple.networkextension.plist` | 네트워크 확장 구성(아래 구조) |
| `SystemPreferencesDomain :: com.apple.networkextension.control.plist` | `CriticalDomains` 키 |
| `HomeDomain :: Library/Preferences/com.apple.Preferences.plist` | `VPNConnectivity`(정수), `VPNHasRelayConnections`(참·거짓) 키 |
| `SystemPreferencesDomain :: SystemConfiguration/preferences.plist` | `Sets`, `NetworkServices`, `CurrentSet`, `__VERSION__`, `Model`, `System` 키 |
| `SysSharedContainerDomain-systemgroup.com.apple.configurationprofiles` | 구성 프로파일 영역(항목 19개) |

이 밖에 `AppDomainPlugin-com.apple.NetworkExtension.IKEv2Provider`, `AppDomainPlugin-com.apple.DiagnosticExtensions.VPN`, `AppDomainPlugin-com.apple.VPNAppIntentWidget` 같은 시스템 확장 도메인도 있습니다. 이 도메인들은 VPN 을 설정하지 않은 기기에도 있을 수 있어서 VPN 을 썼다는 근거로 쓰지 않습니다.

기기 안 경로는 공개 문서에 나와 있지 않아서, 파일 시스템 추출에서는 파일 이름으로 찾아 위치를 확인합니다. 설정 앱의 어느 메뉴에서 VPN·프로필이 보이는지와 iOS 15 ~ 18 사이에 파일 구조가 바뀌었는지도 공개 문서에 나와 있지 않습니다. 백업 도메인 이름을 읽는 법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.

## 구조

### com.apple.networkextension.plist

최상위에는 정수·문자열·목록 키가 하나씩 있고, UUID 를 키로 한 사전이 있으며 그 사전 안에 `Generation`, `Index`, `Version` 키가 있습니다. VPN 구성 항목이 어떤 키 아래에 들어가는지는 실제 데이터로 확인합니다. 열었을 때 `$objects`·`$top` 같은 키가 보이면 NSKeyedArchiver 로 싼 값이라서 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 의 풀이 방법을 따릅니다.

`com.apple.networkextension.control.plist` 에는 `CriticalDomains` 목록 하나가 있고, 무엇을 담는지는 알려져 있지 않습니다.

### 설정 앱 plist 의 VPN 키

`com.apple.Preferences.plist` 의 `VPNConnectivity` 는 정수, `VPNHasRelayConnections` 는 참·거짓 값입니다. 키 이름으로 보면 설정 앱이 VPN 연결 상태를 표시하려고 두는 값으로 보이지만, 값의 뜻과 언제 바뀌는지를 설명한 공개 문서는 없습니다. 값을 보고서에 쓰려면 연습용 기기에서 VPN 을 켜고 끄며 값이 어떻게 바뀌는지 먼저 시험합니다.

### 구성 프로파일

MVT 의 `ConfigurationProfiles` 모듈은 설치된 구성 프로파일 정보를 백업과 파일 시스템 추출에서 뽑고, 여기에는 VPN 같은 제3자 구성도 들어갑니다 [2]. 프로파일 영역의 파일과 읽는 법은 [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md) 에서 다루고, 이 페이지에서는 VPN 페이로드가 있는지 확인하는 데만 씁니다. VPN 페이로드의 식별자 문자열은 실제 기기의 프로필에서 확인합니다.

## 증거로서 의미

**증명하는 것**

- 네트워크 확장 설정이나 구성 프로파일에 VPN 구성이 있으면, 수집 시점에 기기에 그 VPN 구성이 저장되어 있었다는 사실을 보여 줍니다.
- 구성 프로파일에 VPN 페이로드가 있으면, 그 VPN 이 프로필을 거쳐 들어왔다는 경위까지 말할 수 있습니다.
- VPN 업체 앱이 설치되어 있고 네트워크 확장 구성이 있으면, 그 앱으로 VPN 을 설정한 흔적으로 볼 수 있습니다.

**증명하지 못하는 것**

- 구성이 있다는 사실은 특정 시각에 VPN 이 켜져 있었다는 증거가 아닙니다. 이 키들에는 켜고 끈 시각이 없어서, 그 시각은 다른 기록에서 따로 찾아야 합니다.
- VPN 으로 무엇을 주고받았는지, 어느 서버에 접속했는지는 이 흔적만으로 알 수 없습니다.
- VPN 을 썼다는 사실만으로 숨기려 했다고 해석하지 않습니다. 회사 업무용이나 관리 프로필이 넣은 구성일 수 있어서 경위를 먼저 확인합니다.

보고서에는 "수집 시점에 이 기기에 IKEv2 방식 VPN 구성이 저장되어 있었다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`com.apple.networkextension.plist` 의 키에는 시각으로 이름이 분명한 키가 없고, `Generation`·`Version` 은 이름으로 보면 판 번호 같습니다. 구성을 언제 넣었는지는 구성 프로파일의 설치 기록이나 VPN 앱의 설치 시각에서 찾는 편이 낫고, 그 방법은 [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md) 과 [설치된 앱](../app-usage/installed-apps.md) 에서 다룹니다. 파일 시스템 추출에서는 파일의 수정 시각도 참고하되, 파일 시스템 시각은 무엇이 바뀔 때 바뀌는지 [iOS의 파일 시스템](../../01-foundations/storage/filesystem/index.md) 에서 확인한 뒤에 씁니다.

## 함정과 한계

VPN 이 켜진 동안의 통신은 기기 밖의 공유기·통신사 기록에 VPN 서버 주소로만 남을 수 있어서, 외부 기록과 기기 기록이 맞지 않을 때 VPN 구성을 먼저 확인합니다. 항상 켜진 VPN 이 설정된 기기라면 사용자 조작 없이 켜진다는 점도 [1] 함께 적습니다.

구성의 인증 정보(암호·인증서)는 plist 가 아니라 키체인에 따로 있을 수 있고, 이 핸드북은 그 값을 꺼내는 방법을 다루지 않습니다. 키체인의 구조와 보호 방식은 [키체인](../../01-foundations/storage/keychain.md) 에서 다룹니다.

공개 도구가 네트워크 확장 plist 의 어느 키를 VPN 이름·서버·방식으로 읽는지는 도구 결과와 원본을 대조해 확인합니다. VPN 앱을 지우거나 프로필을 지운 흔적은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름으로 확인합니다.

## 직접 분석해 보기

로컬 백업이면 `Manifest.db` 에서 네트워크 확장 파일과 구성 프로파일 영역의 파일을 먼저 뽑습니다.

```sql
SELECT fileID, domain, relativePath
FROM Files
WHERE relativePath LIKE '%networkextension%'
   OR domain = 'SysSharedContainerDomain-systemgroup.com.apple.configurationprofiles'
ORDER BY domain, relativePath;
```

찾은 파일을 복사본으로 옮긴 뒤 헥스 편집기로 첫 8바이트를 봅니다. 아래는 이진 plist 명세로 만든 예시이고 특정 기기의 값이 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07   문자
00000000  62 70 6C 69 73 74 30 30   bplist00
```

이진 plist 로 확인되면 Python 표준 모듈 `plistlib` 로 열어 최상위 키와 UUID 사전 안의 키를 모두 적습니다. 값에 `$archiver` 키가 보이면 NSKeyedArchiver 로 싼 값이라서 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 의 방법으로 풀고, 안에서 VPN 이름·서버 주소·방식으로 보이는 키를 찾습니다. 공개 도구로는 MVT 의 `ConfigurationProfiles` 모듈이 설치된 구성 프로파일을 뽑아 주니 [2], 프로필로 들어온 VPN 이 있는지 이 결과로 먼저 살펴봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md) | VPN 페이로드가 든 프로필과 설치 기록 |
| [설치된 앱](../app-usage/installed-apps.md) | VPN 업체 앱이 설치되어 있는지 |
| [앱별 데이터 사용량](data-usage.md) | VPN 앱 프로세스가 통신한 기록이 있는지 |
| [통합 로그에서 찾을 것](../logs/unified-log-events.md) | VPN 을 켜고 끈 순간 |
| [와이파이 기록](wifi.md) | 같은 시간대에 붙어 있던 네트워크 |
| [키체인](../../01-foundations/storage/keychain.md) | VPN 인증 정보가 어디에 보관되는지 |

VPN 이 침해 사고와 관련된 경우의 흐름은 [악성 코드는 어디서 들어왔나](../../04-scenarios/incident/initial-access.md) 와 [스파이웨어 감염 흔적](../../04-scenarios/incident/spyware.md) 에서 다룹니다.

## 실습

공개 시험 데이터(NIST CFReDS 등)에 VPN 구성이 든 아이폰 추출이 있으면 아래 질문으로 풀어 봅니다. 없으면 연습용 기기에 IKEv2 VPN 구성을 하나 넣은 전후로 백업을 떠서 비교합니다.

1. VPN 구성을 넣기 전후로 `com.apple.networkextension.plist` 의 최상위 키와 UUID 사전은 어떻게 달라집니까?
2. VPN 이름과 서버 주소는 어느 키 아래에 들어갑니까? NSKeyedArchiver 로 싸여 있습니까?
3. VPN 을 켜고 끈 뒤 `com.apple.Preferences.plist` 의 `VPNConnectivity` 값이 바뀝니까?
4. 구성 프로파일 영역에 VPN 관련 항목이 생깁니까? 설정 앱에서 직접 넣은 경우와 프로필로 넣은 경우는 어떻게 다릅니까?
5. VPN 앱을 설치한 경우 DataUsage.sqlite 에 그 앱의 프로세스가 나타납니까?

## 참고 문헌

1. Apple Platform Deployment, "VPN settings overview" — https://support.apple.com/guide/deployment/vpn-settings-overview-depae3d361d0/web
2. MVT 문서, "Records extracted by mvt-ios" — https://docs.mvt.re/en/latest/ios/records/
