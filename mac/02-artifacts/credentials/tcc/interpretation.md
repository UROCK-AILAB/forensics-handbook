---
title: "권한 기록 해석"
parent: "개인 정보 보호 권한"
grand_parent: "아티팩트 · 자격 증명·권한"
nav_order: 1830
---

# 권한 기록 해석 (Services·auth_value)

TCC.db `access` 표의 한 행은 `service`(자료 종류)와 `client`(앱)의 짝에 권한 상태 값과, macOS 11부터는 그 상태가 된 사유 값을 붙여 적은 것이라서, 숫자 값을 이름으로 풀고 서비스 이름을 사람이 아는 권한으로 옮겨야 증거로 읽을 수 있습니다 [1][2][4].

## 무엇을 기록하나

파일과 표의 구조는 [권한 DB 구조](tcc-db.md)에 있고, 이 페이지는 그 칸에 들어가는 값을 풉니다. macOS 10.15 이하에서는 `allowed` 칸 하나로 허용 여부만 남지만, macOS 11부터는 `auth_value`로 상태를 여러 단계로 나누고 `auth_reason`으로 그 상태를 누가 정했는지까지 남깁니다 [1][2][4].

Apple은 이 값들의 공식 정의를 공개하지 않았습니다. 아래 이름은 Jamf Aftermath 소스의 대응표에서 가져왔고 [4], 서비스 설명과 도입 버전은 Apple이 GitHub에 올린 기기 관리 프로파일 (PPPC) 스키마에서 가져왔습니다 [3].

## 권한 상태 값

macOS 10.15 이하의 `allowed` 칸은 0이면 허용 안 됨, 1이면 허용입니다 [1][2]. macOS 11 이상의 `auth_value` 값은 아래와 같습니다 [4].

| `auth_value` | Aftermath 이름 | 뜻 |
|---|---|---|
| 0 | denied | 거부 |
| 1 | unknown | 알 수 없음 |
| 2 | allowed | 허용 |
| 3 | limited | 제한된 허용 |
| 4 | addOnly | 추가만 허용 |
| 5 | singleBootAllowed | 소스 주석은 "allowed for a unique boot_uuid", 한 번의 부팅 동안만 허용 |

3(limited)과 4(addOnly)가 어느 서비스에서 쓰이는지는 확인한 자료가 없습니다. 사진 추가 권한으로 보이는 `kTCCServicePhotosAdd`라는 서비스 이름은 있지만 [4], 두 값과 어떻게 이어지는지는 확인하지 못했습니다.

mac_apt와 APOLLO는 0(거부)과 2(허용)만 이름으로 풀고 나머지 값은 빈칸으로 둡니다 [1][2]. 그래서 도구 출력만 보면 1·3·4·5인 행의 상태가 사라진 것처럼 보이고, 원본 값을 SQL로 따로 확인해야 합니다.

## 사유 값

macOS 11 이상의 `auth_reason` 값은 아래와 같습니다 [4]. 오른쪽 칸은 이름에서 읽히는 구분이고 Apple의 공식 정의가 아닙니다.

| `auth_reason` | Aftermath 이름 | 이름에서 읽히는 구분 |
|---|---|---|
| 0 | inherited | 물려받음 |
| 1 | error | 오류 |
| 2 | userConsent | 사용자가 알림창에서 응답 |
| 3 | userSet | 사용자가 설정에서 직접 바꿈 |
| 4 | systemSet | 시스템이 설정 |
| 5 | servicePolicy | 서비스 정책 |
| 6 | mdmPolicy | MDM 프로파일로 설정 |
| 7 | overridePolicy | 재정의 정책 |
| 8 | missingUsageString | 사용 목적 문구 없음 |
| 9 | promptTimeout | 알림창 시간 초과 |
| 10 | preflightUnknown | 사전 확인 결과 알 수 없음 |
| 11 | entitled | 권한 선언(entitlement)에 따름 |
| 12 | appTypePolicy | 앱 종류 정책 |

최신 macOS에서 12보다 큰 값이 생겼는지는 확인한 자료가 없습니다. 표에 없는 값이 나오면 이름을 짐작해 붙이지 말고 숫자 그대로 보고합니다.

## 서비스 이름

`service` 칸 값은 `kTCCService`로 시작하는 문자열입니다 [4]. 아래 표의 우리말 뜻은 Aftermath 소스가 서비스마다 붙인 영어 이름을 옮긴 것이고, 소스 주석은 이 대응을 TCC.framework의 Localizable.strings와 rainforest.engineering 글에서 모았다고 적고 있습니다 [4]. 괄호 안 설명과 도입 버전은 PPPC 스키마를 따랐습니다 [3]. PPPC 프로파일 키 이름은 `kTCCService`를 뗀 형태입니다 [3].

| `service` 값 | 뜻 | PPPC 도입 |
|---|---|---|
| `kTCCServiceSystemPolicyAllFiles` | 전체 디스크 접근 ("시스템 관리 파일을 포함한 모든 보호 파일") | 10.14 |
| `kTCCServiceSystemPolicySysAdminFiles` | "시스템 관리에 쓰는 일부 파일" | 10.14 |
| `kTCCServiceAccessibility` | 손쉬운 사용 | 10.14 |
| `kTCCServicePostEvent` | 키 입력 보내기 ("CGEvent 보내기") | 10.14 |
| `kTCCServiceAppleEvents` | 다른 앱에 대한 Apple 이벤트 권한 | 10.14 |
| `kTCCServiceListenEvent` | 입력 모니터링 ("CGEvent 받기") | 10.15 |
| `kTCCServiceScreenCapture` | 화면 기록 ("화면 내용 읽기") | 10.15 |
| `kTCCServiceSystemPolicyDesktopFolder`·`DocumentsFolder`·`DownloadsFolder` | 데스크탑·문서·다운로드 폴더 | 10.15 |
| `kTCCServiceSystemPolicyNetworkVolumes`·`RemovableVolumes` | 네트워크 볼륨·이동식 볼륨 | 10.15 |
| `kTCCServiceSystemPolicyAppBundles` | 앱 관리 ("다른 앱 업데이트·삭제") | 13.0 |
| `kTCCServiceSystemPolicyAppData` | "다른 앱의 데이터 접근" | 14.0 |
| `kTCCServiceDeveloperTool` | 개발자 도구 | PPPC 스키마에 없음 |
| `kTCCServiceEndpointSecurityClient` | Endpoint Security 클라이언트 | PPPC 스키마에 없음 |

PPPC 스키마에는 이 밖에도 10.14에 `AddressBook`·`Calendar`·`Reminders`·`Photos`·`Camera`·`Microphone`이, 10.15에 `MediaLibrary`·`FileProviderPresence`·`SpeechRecognition`이, 11.0에 `BluetoothAlways`가 실려 있습니다 [3]. Aftermath 대응표에는 `kTCCServiceSystemPolicyDeveloperFiles`, `kTCCServiceUserAvailability`, `kTCCServiceContactsFull`, `kTCCServiceContactsLimited`, `kTCCServiceLocation`, `kTCCServiceFileProviderDomain`(iCloud Drive 접근), `kTCCServiceMotion`, `kTCCServiceFocusStatus`, `kTCCServiceGameCenterFriends`, `kTCCServiceWillow`(홈 데이터), `kTCCServicePhotosAdd`, `kTCCServicePrototype3Rights`, `kTCCServiceSiri`, `kTCCServiceLiverpool`(위치), `kTCCServiceUbiquity`(iCloud), `kTCCServiceShareKit`(공유)도 있습니다 [4]. 이 가운데 어느 서비스를 먼저 검토할지는 [권한 변경 흔적](changes.md)의 탐지 절에서 다룹니다.

PPPC 도입 버전은 MDM 프로파일로 그 권한을 다룰 수 있게 된 버전이라서, 그 서비스가 TCC.db에 처음 나타난 버전과 같다고 단정하지 않습니다.

## client와 나머지 칸

`client`는 권한을 받은 앱을 가리킵니다. `client_type`이 0이면 번들 ID, 1이면 절대 경로라는 설명이 널리 퍼져 있지만 확인한 자료가 없고, PPPC 스키마의 `IdentifierType` 값이 `bundleID`와 `path` 두 가지라서 그런 대응이 있으리라 짐작할 수 있을 뿐입니다 [3]. 그래서 `client` 값이 `/`로 시작하는 경로인지, 번들 ID 모양인지를 직접 보고 가립니다. 번들 ID를 읽는 법은 [번들 ID와 팀 ID](../../../01-foundations/value-decoding/bundle-team-id.md)에 있습니다.

`indirect_object_identifier`는 AppleEvents 권한에서 이벤트를 받는 쪽 앱을 가리키는 칸으로 보입니다. PPPC에서 AppleEvents만 받는 프로세스를 적는 `AEReceiverIdentifier`를 따로 두는 것과 맞지만 [3], 칸 뜻 자체는 확인한 자료가 없습니다.

## 증거로서 의미

한 행에서 말할 수 있는 것은 수집 시점에 이 앱이 이 자료 종류에 대해 이 권한 상태였다는 것이고, macOS 11 이상이면 그 상태가 사용자 응답·사용자 설정·시스템·MDM 가운데 어느 쪽 결정으로 기록됐는지도 `auth_reason`으로 가를 수 있습니다.

권한이 허용이라고 해서 앱이 실제로 카메라를 켜거나 파일을 읽었다는 뜻은 아닙니다. `auth_reason`이 사용자 응답이어도 그 순간 누가 맥 앞에 있었는지는 이 값으로 알 수 없고, 사람을 특정하려면 [그 시각에 맥을 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md)의 다른 흔적과 맞춰 봐야 합니다.

## 함정과 한계

도구 출력의 빈칸은 값이 없다는 뜻이 아닐 수 있어서, 앞의 권한 상태 값 절에서 본 것처럼 빈칸이 보이면 원본 값을 확인합니다.

`auth_value`와 `auth_reason`의 이름은 도구 작성자가 소스에 적은 대응이라서, 보고서에는 숫자 값과 함께 "Jamf Aftermath 소스의 대응표에 따르면"처럼 출처를 적습니다. 서비스 목록도 확인한 자료에 있는 이름까지라서, 새 macOS에서 처음 보는 `kTCCService` 이름이 나오면 뜻을 짐작하지 말고 이름 그대로 옮깁니다.

macOS 10.15 이하의 `allowed` 값(1=허용)과 macOS 11 이상의 `auth_value` 값(2=허용)은 숫자가 달라서, 두 구조의 결과를 한 표에 섞을 때는 먼저 이름으로 바꾼 뒤 합칩니다.

## 직접 분석해 보기

도구가 빈칸으로 두는 상태 값만 골라 보려면 아래처럼 읽습니다(macOS 11 이상 구조).

```sql
SELECT service, client, client_type, auth_value, auth_reason
FROM access
WHERE auth_value NOT IN (0, 2);
```

사유 값별로 행 수를 세면 사용자 응답과 MDM 설정이 얼마나 섞여 있는지 한눈에 보입니다.

```sql
SELECT auth_reason, auth_value, COUNT(*)
FROM access
GROUP BY auth_reason, auth_value;
```

## 교차 검증

- [권한 DB 구조 (TCC.db)](tcc-db.md) — 칸 구성과 버전 판별
- [권한 변경 흔적 (Changes)](changes.md) — 상태가 언제 바뀌었는지, MDM 프로파일과 맞춰 볼 때
- [구성 프로파일 (Configuration Profiles·MDM)](../../persistence/configuration-profiles.md) — `auth_reason` 6(mdmPolicy)인 행의 출처를 찾을 때
- [앱 번들 정보 (Info.plist·Code Signature)](../../embedded-metadata/app-bundle.md) — `client`가 가리키는 앱이 무엇인지 확인할 때
- [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../../01-foundations/protection/codesign-notarization-sip.md)
- [원격 접속 (Remote Access)](../../network/remote-access/index.md) — 화면 기록·손쉬운 사용 권한을 받은 앱이 원격 접속 도구인지 확인할 때

## 실습

1. TCC.db에서 `auth_value`가 0도 2도 아닌 행을 찾아 mac_apt 출력의 같은 행과 비교해 봅니다.
2. 화면 기록(`kTCCServiceScreenCapture`)과 입력 모니터링(`kTCCServiceListenEvent`) 권한을 받은 앱을 모두 뽑고, 각 행의 `auth_reason`이 무엇인지 적어 봅니다.
3. `client` 값 가운데 경로 모양인 것과 번들 ID 모양인 것을 나누고, `client_type` 값과 어떻게 짝지어지는지 관찰해 봅니다.

## 참고 문헌

1. mac_apt TCC 플러그인 소스 tcc.py (Minoru Kobayashi, 2022) — https://github.com/ydkhatri/mac_apt/blob/master/plugins/tcc.py
2. APOLLO 모듈 tcc_db.txt (Sarah Edwards, mac4n6) — https://github.com/mac4n6/APOLLO/blob/master/modules/tcc_db.txt
3. Apple device-management 저장소, PPPC 프로파일 스키마 com.apple.TCC.configuration-profile-policy.yaml — https://raw.githubusercontent.com/apple/device-management/release/mdm/profiles/com.apple.TCC.configuration-profile-policy.yaml
4. Jamf Aftermath 소스 analysis/DatabaseParser.swift (TCCAuthValue·TCCAuthReason·TCCService) — https://github.com/jamf/aftermath/blob/main/analysis/DatabaseParser.swift
