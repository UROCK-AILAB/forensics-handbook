---
title: "암호와 Face ID 설정 흔적"
parent: "아티팩트 · 시스템·계정"
nav_order: 310
---

# 암호와 Face ID 설정 흔적 (Passcode·Biometrics)

## 한 줄 요약

지문 같은 생체 인증 데이터는 기기 밖으로 나가지 않고 백업에도 들어가지 않아서[3], 추출물과 백업에서 찾을 수 있는 것은 암호와 Face ID·Touch ID 를 설정하고 쓸 수 있었는지 보여 주는 설정 흔적이고, 이 흔적은 백업 `Manifest.plist`, 여러 앱의 설정 파일, 구성 프로파일의 암호 정책 파일에 흩어져 있습니다.

## 무엇을 기록하나 · 왜 생기나

### Apple 이 밝힌 동작

이 절은 Apple Platform Security 문서가 설명하는 동작이고, 흔적을 해석할 때 바탕이 됩니다. 잠금 해제나 보안 우회 방법은 다루지 않습니다.

iOS 는 6자리 숫자, 4자리 숫자, 길이를 정하지 않은 영숫자 암호를 지원하고, 기기 암호를 설정하면 데이터 보호(Data Protection)가 저절로 켜집니다[2]. 암호는 기기 고유 키(UID)와 얽혀 있어서 암호를 맞춰 보는 시도는 그 기기 안에서만 할 수 있습니다[2]. 데이터 보호의 짜임은 [데이터 보호](../../01-foundations/storage/data-protection/index.md) 에서 다룹니다.

암호를 잘못 넣으면 다음 입력까지 기다려야 하는 시간이 늘어나고, 이 대기는 Secure Enclave 가 강제합니다. 대기 중에 재시동해도 대기는 풀리지 않고 그 구간의 타이머가 처음부터 다시 돕니다[2]. Apple Platform Security 현재 판의 iOS·iPadOS·visionOS 잠금 화면 대기 시간은 아래와 같습니다[2]. 예전 판 문서는 숫자가 다를 수 있고 이번에 확인하지 않았습니다.

| 연속 실패 횟수 | 대기 |
|---|---|
| 3회까지 | 없음 |
| 4회 | 1분 |
| 5회 | 5분 |
| 6회 | 15분 |
| 7회 | 1시간 |
| 8회 | 3시간 |
| 9회 | 8시간 |
| 10회 이상 | 기기가 잠기고 Mac 이나 PC 에 연결해야 함 |

설정의 Face ID/Touch ID 및 암호 화면에서 "데이터 지우기" 를 켜 두면 연속 10회 틀렸을 때 모든 콘텐츠와 설정이 지워집니다[2]. 이 설정이 켜진 기기가 초기화된 상태로 발견되면, 지우기 명령이 아니라 연속 10회 암호 실패로 지워졌을 가능성도 함께 따져야 합니다. 초기화 흔적은 [초기화와 복원 흔적](erase-restore.md) 에서 다룹니다.

Face ID 나 Touch ID 를 쓰려면 먼저 잠금 해제에 암호를 요구하도록 설정되어 있어야 합니다[4]. 생체 인증을 켜 두었어도 기기는 아래 상태에서 생체 인증 대신 암호를 요구합니다[4].

| 암호를 요구하는 상태[4] |
|---|
| 기기를 막 켰거나 재시동함 |
| 48시간 넘게 잠금을 풀지 않음 |
| 156시간(6.5일) 동안 암호로 잠금을 풀지 않았고, 4시간 동안 생체 인증으로도 풀지 않음 |
| 원격 잠금 명령을 받음 |
| 음량 버튼과 측면 버튼을 함께 눌러 띄운 전원 끄기·긴급 SOS 화면에서 취소를 누름 |
| 생체 인증에 5회 실패함 |

소프트웨어 업데이트, 기기 지우기, 암호 설정을 보거나 바꾸는 일, 구성 프로파일 설치는 생체 인증과 관계없이 늘 암호를 요구합니다[4]. Touch ID 가 있어도 기기를 켜거나 재시동한 뒤에는 암호가 필요하고, 암호를 바꾸거나 지문을 등록·삭제할 때도 암호가 필요합니다[3]. 마스크를 쓴 채 쓰는 Face ID 는 Face ID 매칭에 성공하거나 암호를 넣거나 Apple Watch 로 잠금을 푼 뒤 6.5시간 동안 쓸 수 있습니다[4].

지문(Touch ID) 템플릿 데이터는 기기를 떠나지 않고, Apple 로 보내지지 않으며, 기기 백업에도 들어가지 않습니다[3]. 받은 자료에서 이 문장은 Touch ID 지문 데이터를 두고 한 말이었고, Face ID 얼굴 데이터에 같은 설명이 있는지는 확인하지 못했습니다. 이 설명에서 이끌어 낸 해석으로는, 추출물에서 찾을 대상은 생체 데이터가 아니라 "생체 인증을 설정했다·쓸 수 있었다" 는 설정 흔적입니다.

## 위치와 버전별 차이

### 로컬 백업에서 본 흔적

관찰한 백업에서 암호·생체 인증과 이름이 닿는 키는 아래와 같습니다. 따로 적지 않은 파일은 `HomeDomain :: Library/Preferences/` 아래에 있고, 값은 보지 않았습니다.

| 파일 | 키 | 이름으로 짐작되는 내용 |
|---|---|---|
| 백업 폴더 맨 위 `Manifest.plist` | `WasPasscodeSet` | 백업할 때 기기 암호가 설정되어 있었는지 |
| `.GlobalPreferences.plist` | `ApplePasscodeKeyboards` (list) | 암호 입력에 쓰는 키보드 목록 |
| `com.apple.AppleMediaServices.plist` | `AMSDeviceBiometricsState` (int), `AMSDeviceBiometricsIdentities` (list) | 미디어 서비스(스토어) 쪽이 본 생체 인증 상태 |
| `com.apple.itunesstored.plist` | `BiometricState` (int), `BiometricStateEnabled` (int) | 스토어 쪽 생체 인증 상태 |
| `AppDomain-com.apple.mobilesafari :: Library/Preferences/com.apple.mobilesafari.plist` | `BiometricAuthenticationIsAvailable` (bool), `BiometricAuthenticationTypeIfAvailable` (int), `PasscodeIsAvailable` (bool) | 사파리가 본 생체 인증·암호 사용 가능 여부와 종류 |
| `com.apple.purplebuddy.plist` | `FaceIDPeriocularPresented` (bool) | 첫 설정 때 마스크 착용 Face ID 화면을 보여 줬는지 |

모두 이름으로 짐작한 뜻이고, 숫자 값이 무엇을 뜻하는지(예: `BiometricAuthenticationTypeIfAvailable` 의 값마다 Touch ID 인지 Face ID 인지)는 확인한 자료가 없어서 적지 않습니다. `Manifest.plist` 의 다른 키는 [로컬 백업](../../01-foundations/backups/local-backup/index.md), `com.apple.purplebuddy.plist` 의 다른 키는 [초기화와 복원 흔적](erase-restore.md) 에서 다룹니다.

도메인 이름으로는 `AppDomainPlugin-com.apple.BiometricKit.BioLogDiagnostic` 과 `AppDomainPlugin-com.apple.PasscodeAndBiometricsSettingsAppIntentsExtension` 이 보였습니다. 백업 안 키체인 파일 `KeychainDomain :: keychain-backup.plist` 에는 `keybag-uuid`, `genp`, `inet`, `cert`, `keys` 키가 있었고, 해석은 [키체인](../../01-foundations/storage/keychain.md) 에서 다룹니다.

### 구성 프로파일의 암호 정책 키

구성 프로파일과 제한 설정 파일 안에 암호 정책으로 보이는 키 이름이 있었습니다.

| 파일(`HomeDomain :: Library/UserConfigurationProfiles/` 아래) | `restrictedValue` 안의 암호 관련 키 |
|---|---|
| `Truth.plist`, `PublicInfo/Truth.plist` | `maxFailedAttempts`, `maxGracePeriod`, `maxInactivity`, `maxPINAgeInDays`, `minComplexChars`, `minLength`, `passcodeKeyboardComplexity`, `pinHistory`, `simplePasscodeComplexity` |
| `EffectiveUserSettings.plist`, `PublicInfo/PublicEffectiveUserSettings.plist` | `maxGracePeriod`, `maxInactivity`, `minLength`, `passcodeKeyboardComplexity`, `simplePasscodeComplexity` |

같은 파일의 `restrictedBool` 안에는 `allowAccessWithoutPasscodeInAppLock` 같은 키도 있었습니다. 이 이름들이 MDM 암호 정책과 같은 이름이라고 확인한 자료는 이번에 없고, 키 이름이 있다고 정책이 걸려 있었다는 뜻도 아닙니다. 값이 기본값인지, 프로파일이 건 값인지는 파일을 열어 값과 프로파일 목록을 함께 봐야 가릴 수 있습니다. 파일 구성은 [설정 값](preferences.md), 프로파일 설치 흔적은 [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md) 에서 다룹니다.

### 확인하지 못한 것

암호 실패 횟수나 마지막 잠금 해제 시각이 어느 파일에 남는지, 시스템 키 가방 파일의 위치와 내용은 이번 자료로 확인하지 못했습니다. iOS 버전에 따라 위 키가 언제 생겼는지도 확인하지 못했고, 위 표는 iOS 27.0 백업 하나에서 본 것입니다. 도난 기기 보호(Stolen Device Protection)도 이번에 연 Apple 문서에는 없어서 다루지 않습니다.

## 구조

위 흔적은 모두 plist 의 키이고, 참거짓(bool)·정수(int)·목록(list) 값으로 적혀 있습니다. 한 파일에 암호 흔적이 모여 있지 않고 스토어, 사파리, 설정 도우미, 프로파일 관리처럼 서로 다른 구성 요소가 각자 필요한 만큼 적어 두는 모양입니다. plist 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 값을 확인했을 때, 여러 구성 요소가 적어 둔 암호·생체 인증 상태가 서로 맞으면 수집 전에 기기에 암호가 설정되어 있었고 생체 인증을 쓸 수 있는 상태였다는 판단을 받쳐 줍니다. 프로파일 쪽 정책 값은 조직이 기기에 암호 규칙을 걸었는지 보여 줄 수 있습니다. 보고서에는 "이 파일의 이 키 값이 이렇다" 를 적고, 그 값에서 끌어낸 해석은 해석이라고 밝혀 씁니다.

**증명하지 못하는 것.** 이 흔적은 설정 상태일 뿐이고, 특정 시각에 누가 암호나 얼굴로 잠금을 풀었는지는 말해 주지 않습니다. 생체 인증이 켜져 있었다는 사실도 등록된 얼굴이나 지문이 누구 것인지 알려 주지 않습니다. 기기 암호 값 자체나 암호를 몇 번 틀렸는지도 이 흔적에서는 알 수 없습니다.

## 시각 해석

위 키에는 시각 값이 거의 없어서, 이 흔적만으로는 암호나 생체 인증을 언제 켰는지 알 수 없습니다. 시점은 파일이 저장된 때(백업의 `Manifest.db` 에 적힌 파일 정보)나 백업을 만든 때로 좁히고, 잠금과 잠금 해제의 시각은 다른 기록에서 찾습니다. [전원 로그](../app-usage/powerlog.md) 에는 화면 잠금·해제 상태 변화가 시각과 함께 남고, [KnowledgeC](../app-usage/knowledgec/index.md) 에도 잠금 상태 구간이 남는데 iOS 16 부터는 이 기록 대부분을 [바이옴](../app-usage/biome/index.md) 이 넘겨받았으니 둘을 함께 보고, [통합 로그에서 찾을 것](../logs/unified-log-events.md) 에서도 잠금 관련 기록을 찾습니다.

Apple 이 밝힌 시간 조건은 기기를 확보한 뒤의 상태를 해석할 때 씁니다. 예를 들어 확보한 기기가 48시간 넘게 잠금 해제되지 않았거나 재시동되었다면 생체 인증 대신 암호를 요구하는 상태가 됩니다[4]. 증거 확보 계획을 세울 때는 이 조건을 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 와 함께 봅니다.

## 함정과 한계

**이름이 닮은 다른 설정과 섞지 않습니다.** 관찰한 백업의 `com.apple.onetimepasscodes.plist` 에는 `DeleteVerificationCodes` 키가 있었고, 이름으로 보아 일회용 인증 코드 설정이고 기기 암호 설정과는 다른 것으로 보입니다. 파일 이름에 "passcode" 가 들어 있다고 기기 암호 흔적으로 묶지 않습니다.

**`WasPasscodeSet` 하나로 결론 내리지 않습니다.** 이 키는 백업 폴더에 있어서 백업을 만든 때의 상태로 보이고, 값의 뜻도 이름으로 짐작한 것입니다. 기기 암호 설정 여부는 사파리의 `PasscodeIsAvailable` 같은 다른 구성 요소의 기록과 함께 봅니다.

**정책 키 이름과 정책 적용을 나눕니다.** 프로파일 파일에 `maxFailedAttempts` 같은 이름이 있어도 그 정책이 걸려 있었다는 뜻이 아닙니다. 값과 설치된 프로파일을 확인한 뒤에만 "정책이 있었다" 고 씁니다.

**지우기와 조작.** "데이터 지우기" 설정이나 원격 지우기로 기기가 초기화되면 이 페이지의 설정 파일도 새로 만들어집니다. 초기화 전 상태는 그 전에 만든 백업에서만 볼 수 있을 수 있으니, 컴퓨터에 남은 백업과 [아이클라우드 백업](../../01-foundations/backups/icloud-backup.md) 을 찾습니다. 조작 가능성은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 이진 plist 명세로 만든 예시이고 특정 검체에서 나온 바이트가 아닙니다. 이진 plist 에서 참거짓 값은 1바이트 객체로, `08` 이 거짓, `09` 가 참입니다. `WasPasscodeSet` 은 14글자라서 표시 바이트 `5E`(하위 4비트 `1110` = 길이 14) 뒤에 글자가 바로 옵니다.

```
5E 57 61 73 50 61 73 73 63 6F 64 65 53 65 74     ^WasPasscodeSet
...
09                                               참(true) 값 객체의 예
```

키 문자열과 값 객체는 파일 안에서 떨어져 있어서, 헥스 편집기로 키 이름을 찾은 뒤 사전의 참조 표를 따라 값 객체의 번호를 찾고, 오프셋 표로 그 객체 위치를 찾아 `08` 인지 `09` 인지 확인합니다. `Manifest.plist` 가 이진 plist 가 아니라 XML 이면 키 뒤에 `<true/>` 나 `<false/>` 가 글자로 보입니다.

### 공개 도구로 한 번

1. 로컬 백업이면 `Manifest.db` 에서 위 설정 파일의 fileID 를 찾아 꺼냅니다. 방법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.
2. Python 표준 라이브러리 `plistlib` 로 파일마다 해당 키를 모아 한 표로 봅니다. 원본이 아니라 꺼낸 사본에서 실행합니다.

```python
import plistlib

targets = {
    "Manifest.plist": ["WasPasscodeSet"],
    ".GlobalPreferences.plist": ["ApplePasscodeKeyboards"],
    "com.apple.AppleMediaServices.plist": ["AMSDeviceBiometricsState"],
    "com.apple.itunesstored.plist": ["BiometricState", "BiometricStateEnabled"],
    "com.apple.mobilesafari.plist": ["BiometricAuthenticationIsAvailable",
                                     "BiometricAuthenticationTypeIfAvailable",
                                     "PasscodeIsAvailable"],
    "com.apple.purplebuddy.plist": ["FaceIDPeriocularPresented"],
}
for name, keys in targets.items():
    try:
        with open(name, "rb") as f:
            d = plistlib.load(f)
    except FileNotFoundError:
        print(name, "없음")
        continue
    for k in keys:
        print(name, k, d.get(k, "(키 없음)"))
```

3. 프로파일 파일은 `restrictedValue` 아래를 풀어 봅니다.

```python
import plistlib

with open("Truth.plist", "rb") as f:
    truth = plistlib.load(f)
for k, v in truth.get("restrictedValue", {}).items():
    print(k, v)
```

4. 값의 뜻을 단정하기 어려우면, 같은 기종·같은 iOS 버전의 시험 기기에서 설정을 켜고 끄며 백업을 두 번 만들어 값이 어떻게 바뀌는지 비교합니다. 이 시험 결과는 시험한 기종과 버전을 밝혀 [도구 검증](../../03-techniques/reporting/tool-validation.md) 의 기록 방식으로 남깁니다.

## 교차 검증

잠금·잠금 해제 시각은 [전원 로그](../app-usage/powerlog.md), [KnowledgeC](../app-usage/knowledgec/index.md), [통합 로그에서 찾을 것](../logs/unified-log-events.md) 과 맞춰 보고, 암호 정책을 건 프로파일은 [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md) 에서 확인합니다. 암호가 데이터 보호와 키체인에 어떻게 얽히는지는 [데이터 보호](../../01-foundations/storage/data-protection/index.md) 와 [키체인](../../01-foundations/storage/keychain.md), 사파리 암호 자동 입력은 [저장된 암호](../credentials-security/saved-passwords.md) 에서 봅니다. 기기를 쓴 사람을 가리는 흐름은 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 를 따릅니다.

## 실습

공개 검체(NIST CFReDS 등의 iOS 이미지나 백업)로 다음 질문을 풀어 봅니다.

1. 백업 `Manifest.plist` 의 `WasPasscodeSet` 값은 무엇이고, 사파리 설정의 `PasscodeIsAvailable` 값과 맞습니까?
2. `BiometricAuthenticationIsAvailable`, `BiometricState`, `AMSDeviceBiometricsState` 값을 나란히 놓으면 서로 어긋나는 곳이 있습니까?
3. 검체 기종에는 Touch ID 와 Face ID 가운데 무엇이 있고, `BiometricAuthenticationTypeIfAvailable` 값과 어떻게 대응해 보입니까? 대응을 단정할 근거가 있습니까?
4. `UserConfigurationProfiles/Truth.plist` 의 `restrictedValue` 아래 암호 관련 키 값은 무엇이고, 설치된 프로파일이 있습니까?
5. 검체 기기가 초기화된 흔적이 있다면, "데이터 지우기" 설정으로 지워졌을 가능성을 어떤 기록으로 따져 볼 수 있습니까?

## 참고 문헌

- [2] Passcodes and passwords — Apple Platform Security — https://support.apple.com/guide/security/passcodes-and-passwords-sec20230a10d/web
- [3] Face ID and Touch ID security — Apple Platform Security — https://support.apple.com/guide/security/face-id-and-touch-id-security-sec067eb0c9e/web
- [4] Face ID, Touch ID, passcodes, and passwords — Apple Platform Security — https://support.apple.com/guide/security/face-id-touch-id-passcodes-and-passwords-sec9479035f1/web
