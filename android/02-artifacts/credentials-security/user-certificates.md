---
title: "설치된 인증서"
parent: "아티팩트 · 자격 증명·보안 설정"
nav_order: 1260
---

# 설치된 인증서 (User Certificates)

## 한 줄 요약

안드로이드는 믿을 CA 인증서를 시스템 폴더와 사용자 폴더에 파일 하나씩 두고, 사용자가 추가한 CA 는 `cacerts-added`, 사용자가 끈 시스템 CA 는 `cacerts-removed` 폴더에 남기 때문에, 이 두 폴더를 보면 누군가 기기의 신뢰 목록을 바꿨는지 알 수 있습니다 [1].

## 무엇을 기록하나 · 왜 생기나

TLS 연결에서 상대 서버를 믿을지는 기기에 등록된 CA (Certificate Authority, 인증 기관) 인증서로 정합니다. 안드로이드의 CA 저장소는 Conscrypt 의 TrustedCertificateStore 가 관리하고, 기기에 처음부터 들어 있는 시스템 CA, 사용자가 추가한 CA, 사용자가 끈 시스템 CA 를 폴더로 나눠 둡니다 [1].

사용자가 시스템 CA 를 끄면 원본은 그대로 두고 똑같은 사본을 `cacerts-removed` 에 넣습니다 [1]. 소스 주석에 따르면 이 삭제는 업그레이드 뒤에도 유지되지만, 시스템 업데이트로 다시 발급된 CA 까지 가리려는 것은 아닙니다 [1]. 그래서 `cacerts-removed` 에 파일이 있으면 누군가 그 시스템 CA 를 끈 흔적으로 읽을 수 있습니다.

CA 가 설치돼 있다고 모든 앱이 그 CA 를 믿지는 않습니다. 앱마다 네트워크 보안 설정 (Network Security Configuration) 으로 어느 CA 를 믿을지 정하고, 기본값은 앱의 targetSdk 에 따라 다릅니다 [2]. 사용자 CA 한 장이 어느 앱의 통신에 영향을 줄 수 있었는지는 이 설정까지 봐야 답할 수 있습니다.

## 위치와 버전별 차이

| 저장소 | 위치 | 비고 |
|---|---|---|
| 시스템 CA | `ANDROID_ROOT/etc/security/cacerts` (보통 `/system/etc/security/cacerts`) [1] | Android 13 까지 |
| 시스템 CA | `/apex/com.android.conscrypt/cacerts` [1] | Android 14 (API 34) 이후, 이 폴더가 있을 때 [1] |
| 사용자가 추가한 CA | `/data/misc/user/<사용자 번호>/cacerts-added` [1][4][5] | 저장소 소스의 기본값은 `/data/misc/keychain/cacerts-added` [1] |
| 사용자가 끈 시스템 CA | `/data/misc/user/<사용자 번호>/cacerts-removed` [1][4][5] | 저장소 소스의 기본값은 `/data/misc/keychain/cacerts-removed` [1] |

저장소 소스에는 `/data/misc/keychain` 아래가 기본값으로 적혀 있지만, 이 기본 폴더는 `setDefaultUserDirectory()` 로 바꿀 수 있습니다 [1]. 앱 프로세스는 시작할 때 이 값을 `Environment.getUserConfigDirectory(사용자 번호)` 로 바꾸고 [5], 이 함수는 `/data/misc/user/<사용자 번호>` 를 돌려주니 [4] 사용자 CA 는 사용자마다 따로 있습니다. 기본 사용자는 0 번이라서 `/data/misc/user/0/cacerts-added` 부터 보고, 여러 사용자가 있는 기기라면 사용자 번호마다 폴더를 확인합니다. 사용자와 프로필 구조는 [사용자와 프로필 (Multi-user·users)](../system-account/users-profiles.md), 파티션과 APEX 같은 저장 영역은 [파티션과 저장 영역 (Partitions)](../../01-foundations/storage/partitions/index.md) 페이지에서 다룹니다.

앱이 사용자 CA 를 믿는 기본값도 버전마다 다릅니다 [2].

| 앱의 targetSdk | 기본으로 믿는 CA |
|---|---|
| Android 6.0 (API 23) 이하 | 시스템 CA 와 사용자 CA (`src="system"`, `src="user"`) |
| Android 7.0 (API 24) 이상 | 시스템 CA 만 (`<certificates src="system" />`) |

Android 11 부터 CA 를 설정 앱에서만 설치할 수 있다는 설명과 사용자 CA 를 설치하면 "네트워크가 모니터링될 수 있음" 알림이 뜬다는 설명은 이번에 확인하지 못했습니다. 삼성 One UI 의 인증서 설정 화면 위치와 녹스 쪽 인증서 저장소도 확인하지 못했습니다.

## 구조

폴더 안의 파일 하나가 인증서 한 장입니다. 저장소가 사용자 폴더에 인증서를 쓸 때는 `getEncoded()` 로 얻은 DER(이진) X.509 를 그대로 쓰고, 읽을 때는 `CertificateFactory` 를 써서 [1] PEM 텍스트 파일도 읽힙니다. 시스템 폴더의 파일은 PEM 텍스트로 들어 있는 경우가 많다고 알려져 있으니, 파일을 열기 전에 첫 줄이 `-----BEGIN CERTIFICATE-----` 인지 봅니다. 파일 이름은 OpenSSL 의 `X509_NAME_hash_old` 로 주체 이름을 해시한 8자리 16진수에 `.` 과 충돌 번호를 붙여 만들고, 같은 해시가 겹치면 번호를 올립니다 [1]. 아래는 소스에 나오는 이름 예입니다.

```
7651b327.0
```

저장소는 인증서를 별칭(alias)으로 부르고, 시스템 인증서는 `system:` 뒤에, 사용자 인증서는 `user:` 뒤에 파일 이름을 붙입니다 [1].

```
system:7651b327.0
user:7651b327.0
```

인증서 파일 안에는 설치 시각이 없습니다. 이름이 같은 파일이 `cacerts-removed` 와 시스템 폴더에 함께 있으면 그 시스템 CA 가 꺼져 있다는 뜻이고, `cacerts-added` 에만 있는 파일은 사용자가 추가한 CA 입니다.

### 앱 쪽 설정

앱은 `res/xml/network_security_config.xml` 을 두고 매니페스트의 `android:networkSecurityConfig` 로 가리켜 기본값을 바꿀 수 있습니다 [2]. `<trust-anchors>` 안에 `<certificates src="user" />` 가 있으면 그 앱은 사용자 CA 를 믿고, `<debug-overrides>` 안의 CA 는 매니페스트에 `android:debuggable="true"` 가 있을 때만 믿습니다 [2]. APK 를 푸는 법은 [APK 정보 (AndroidManifest·서명)](../embedded-metadata/apk.md) 페이지에서 다룹니다.

```xml
<network-security-config>
  <base-config>
    <trust-anchors>
      <certificates src="system" />
      <certificates src="user" />
    </trust-anchors>
  </base-config>
</network-security-config>
```

위 XML 은 문서의 요소 이름으로 만든 모양 예시이고, 이 모양이면 앱 전체가 사용자 CA 까지 믿습니다 [2].

### 기기 관리자·설정 쪽 기록

기기 관리자 정책 파일 `device_policies.xml` 에는 `accepted-ca-certificate`, `owner-installed-ca-cert` 라는 태그 이름이 있습니다 [3]. 관리자 앱이 설치한 CA 와 사용자가 확인한 CA 를 적는 곳으로 보이지만 뜻은 소스 주석으로 확인하지 못했고, 파일 자체는 [기기 관리자와 접근성 권한 (Device Admin·Accessibility)](device-admin-accessibility.md) 페이지에서 다룹니다. 관찰 기기의 settings secure 에는 `config_update_certificate` 키가 있었지만 뜻은 모르고, 키 이름만 확인했습니다.

VPN·Wi-Fi 에 쓰는 사용자 인증서(클라이언트 인증서와 개인 키)가 어디에 어떤 모양으로 남는지는 이 페이지에서 확인하지 않았습니다. 설정 쪽 흔적은 [VPN 설정 (VPN)](../network/vpn.md) 과 [와이파이 설정과 접속 기록 (WifiConfigStore)](../network/wifi.md), 키 저장소는 [저장 공간 암호화 (Encryption)](../../01-foundations/storage/encryption/index.md) 페이지에서 봅니다.

## 증거로서 의미

**증명하는 것**

`cacerts-added` 에 파일이 있으면 그 사용자 폴더에 사용자 CA 가 추가돼 있다는 뜻이고, 인증서의 주체·발급자·유효 기간으로 어떤 CA 인지 알 수 있습니다. `cacerts-removed` 에 파일이 있으면 누군가 그 시스템 CA 를 껐다는 흔적입니다 [1]. APK 의 `network_security_config.xml` 과 targetSdk 를 함께 보면 어느 앱이 기본값이나 명시 설정으로 사용자 CA 를 믿었는지 가려낼 수 있습니다 [2].

**증명하지 못하는 것**

사용자 CA 가 있다는 사실만으로 통신을 가로챘다고 말할 수 없습니다. API 24 이상을 목표로 하고 `src="user"` 를 따로 두지 않은 앱은 기본적으로 사용자 CA 로 만든 TLS 연결을 받아들이지 않으니 [2], 영향을 받았을 수 있는 앱은 앱마다 설정을 보고 좁혀야 합니다. 누가, 어떤 경로로 CA 를 설치했는지도 인증서 파일은 말하지 않습니다. 회사 관리 앱이 넣은 CA 인지 사용자가 직접 넣은 CA 인지는 `device_policies.xml` 의 관련 태그와 관리자 앱 기록을 함께 봐야 하는데, 그 태그의 정확한 뜻은 아직 확인하지 못했습니다.

보고서에는 "이 사용자 폴더에 이 주체 이름의 CA 가 추가돼 있고, 이 앱들은 설정상 사용자 CA 를 믿는다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

인증서 안의 유효 기간(시작·만료)은 CA 가 만든 시각이지 기기에 설치한 시각이 아닙니다. 설치 시각은 인증서 안에 없어서 파일 시스템의 생성·수정 시각이 설치 시점의 단서가 될 수 있다는 정도로만 추정합니다. 파일 시스템 시각을 읽는 법은 [파일 시스템 (ext4·F2FS)](../../01-foundations/storage/filesystems/index.md) 페이지에 있고, 사본을 만드는 과정에서 시각이 바뀌지 않았는지 먼저 확인합니다. `cacerts-removed` 사본의 시각도 같은 방식으로 "그 무렵 시스템 CA 를 껐을 수 있다" 는 추정에 그칩니다.

## 함정과 한계

첫째, 사용자 CA 폴더는 사용자 번호마다 따로 있고 저장소 소스의 기본값(`/data/misc/keychain`)과도 다릅니다 [1][5]. 0 번 사용자 폴더에 파일이 없다고 기기 전체에 사용자 CA 가 없다고 결론 내리지 말고, `cacerts-added`·`cacerts-removed` 라는 폴더 이름으로 전체를 찾습니다.

둘째, Android 14 이후는 시스템 CA 가 APEX 쪽에 있습니다 [1]. `/system/etc/security/cacerts` 만 보고 시스템 CA 목록을 만들면 비교 기준이 틀어집니다.

셋째, 파일 이름은 주체 이름의 해시라서 이름이 같아도 다른 인증서일 수 있고, 충돌 번호가 붙은 파일은 따로 봐야 합니다 [1]. 두 폴더의 파일을 비교할 때는 이름보다 내용(지문)으로 맞춥니다.

넷째, 시스템 업데이트로 다시 발급된 CA 는 예전 `cacerts-removed` 사본에 가려지지 않을 수 있습니다 [1]. 끈 흔적과 지금 믿는 목록이 다를 수 있다는 뜻이라서, 두 쪽을 따로 적습니다.

## 직접 분석해 보기

### 파일 한 장을 직접 읽기

사용자 폴더의 DER 파일은 텍스트로 열리지 않으니 OpenSSL 같은 공개 도구로 읽고, 시스템 폴더 파일이 PEM 이면 아래 명령에서 `-inform DER` 을 `-inform PEM` 으로 바꿉니다. `-subject_hash_old` 는 파일 이름을 만드는 `X509_NAME_hash_old` 값을 보여 줘서, 파일 이름 앞 8자리와 같은지 맞춰 볼 수 있습니다.

```
openssl x509 -inform DER -in 7651b327.0 -noout -subject -issuer -dates
openssl x509 -inform DER -in 7651b327.0 -noout -subject_hash_old
openssl x509 -inform DER -in 7651b327.0 -noout -fingerprint -sha256
```

헥스 편집기로는 파일이 이진 DER(보통 `30 82` 로 시작)인지 PEM 텍스트인지만 확인하고, 필드 해석은 위 명령에 맡기는 편이 안전합니다.

### 폴더 비교로 한 번

1. 전체 파일 시스템 사본에서 `cacerts-added`, `cacerts-removed` 폴더를 모두 찾습니다.
2. 각 폴더 파일마다 주체, 발급자, 유효 기간, SHA-256 지문, 파일 시스템 시각을 표로 적습니다.
3. `cacerts-removed` 의 파일을 같은 기기의 시스템 CA 폴더(Android 버전에 맞는 쪽)와 지문으로 맞춰, 어느 시스템 CA 를 껐는지 확인합니다.
4. 설치된 앱 가운데 조사 대상 앱의 APK 에서 targetSdk 와 `network_security_config.xml` 을 확인해, 사용자 CA 를 믿는 앱 목록을 만듭니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [기기 관리자와 접근성 권한 (Device Admin·Accessibility)](device-admin-accessibility.md) | `device_policies.xml` 에 인증서 관련 태그와 관리자 앱이 있는지 |
| [VPN 설정 (VPN)](../network/vpn.md) | CA 추가 무렵 VPN 설정이 생겼는지 |
| [와이파이 설정과 접속 기록 (WifiConfigStore)](../network/wifi.md) | 인증서를 쓰는 Wi-Fi 설정이 있는지 |
| [설치된 앱 (packages.xml)](../app-usage/packages/index.md) | CA 파일 시각과 가까운 때 설치된 앱이 있는지 |
| [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) | 인증서 이름이 들어간 설정 키와 값 |

조사 흐름은 [악성 앱 흔적 분석 (Malicious App Triage)](../../03-techniques/analysis/malicious-app-triage/index.md), [몰래 설치된 감시 앱 (Stalkerware)](../../04-scenarios/incident/stalkerware.md), [계정 탈취 흔적 (Account Takeover)](../../04-scenarios/incident/account-takeover.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 검체에서 아래 질문을 풀어 봅니다.

1. 검체에 `cacerts-added` 나 `cacerts-removed` 폴더가 있습니까? 있다면 어느 경로에 있고 파일은 몇 개입니까?
2. `cacerts-added` 의 인증서마다 주체와 발급자는 무엇이고, `-subject_hash_old` 값이 파일 이름과 맞습니까?
3. `cacerts-removed` 의 인증서는 시스템 CA 폴더의 어느 파일과 지문이 같습니까?
4. 검체의 Android 버전으로 보아 시스템 CA 는 어느 폴더에서 찾아야 합니까?
5. 설치된 앱 하나를 골라 targetSdk 와 `network_security_config.xml` 을 보면, 그 앱은 사용자 CA 를 믿습니까?

## 참고 문헌

1. TrustedCertificateStore.java (AOSP external/conscrypt, main) — https://android.googlesource.com/platform/external/conscrypt/+/refs/heads/main/platform/src/main/java/org/conscrypt/TrustedCertificateStore.java
2. Network security configuration — Android Developers — https://developer.android.com/privacy-and-security/security-config
3. DevicePolicyData.java (AOSP frameworks/base, main) — https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/services/devicepolicy/java/com/android/server/devicepolicy/DevicePolicyData.java
4. Environment.java (AOSP frameworks/base, main) — https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/os/Environment.java
5. ActivityThread.java (AOSP frameworks/base) — https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/app/ActivityThread.java
