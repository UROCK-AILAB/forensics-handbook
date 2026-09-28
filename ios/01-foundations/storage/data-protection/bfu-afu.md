---
title: "잠금 해제 전·후"
parent: "데이터 보호"
grand_parent: "기반 · 저장 구조"
nav_order: 60
---

# 잠금 해제 전·후 (BFU·AFU)

재부팅 뒤 한 번도 잠금을 풀지 않은 상태(BFU)와 한 번이라도 푼 상태(AFU)는 메모리에 남은 등급 키가 달라서, 같은 기기라도 어느 상태에서 수집했느냐에 따라 읽을 수 있는 데이터가 달라집니다.

## 두 상태

잠금 해제 전 (BFU, Before First Unlock) 은 재부팅한 뒤 사용자가 아직 한 번도 잠금을 풀지 않은 상태이고, 사용자 데이터는 암호화된 채 있습니다[2]. 잠금 해제 후 (AFU, After First Unlock) 는 첫 해제 뒤 풀린 키가 메모리에 남아 있는 상태입니다[2]. AFU 는 "지금 잠금이 풀려 있다" 는 뜻이 아니고, 화면이 잠겨 있어도 재부팅 뒤 한 번 풀었다면 AFU 입니다.

## 상태와 등급을 함께 읽는 법

어떤 파일을 기기가 풀 수 있는지는 파일 등급과 잠금 상태를 함께 봐야 정해집니다. 등급마다 키를 언제 버리는지는 [보호 등급 (Protection Classes)](protection-classes.md) 에 있고, 이를 상태별로 옮기면 아래와 같습니다.

| 등급 | BFU | AFU, 화면 잠김 | AFU, 잠금 풀림 |
|---|---|---|---|
| Class A | 풀 수 없음 | 풀 수 없음. 잠그고 약 10초 뒤 키를 버림 | 풀 수 있음 |
| Class C | 풀 수 없음 | 풀 수 있음. 잠가도 키가 메모리에 남음 | 풀 수 있음 |
| Class D | 풀 수 있음(해석) | 풀 수 있음 | 풀 수 있음 |

(출처: [1]. Class D 칸은 "등급 키가 UID 로만 보호된다" 는 [1] 의 설명을 바탕으로 한 해석입니다)

Class B 는 잠긴 동안에도 파일을 쓸 수 있게 만든 등급이라서 이 표의 틀에 그대로 들어맞지 않습니다. 동작은 [보호 등급 (Protection Classes)](protection-classes.md) 에 있습니다.

제3자 앱 데이터는 앱이 따로 정하지 않으면 Class C 입니다[1]. 그래서 앱 데이터 대부분은 BFU 냐 AFU 냐에 따라 풀리는지가 갈릴 가능성이 높지만, 앱마다 등급을 달리 정했을 수 있습니다.

키체인도 같은 방식으로 나뉩니다. `AfterFirstUnlock` 등급 항목은 AFU 에서 쓸 수 있고, `WhenUnlocked` 등급 항목은 잠금이 풀려 있는 동안에만 쓸 수 있습니다[3].

> 그림 자리: 가로축에 "재부팅 → 첫 잠금 해제 → 화면 잠금 → 다시 해제" 를 두고, Class A·C·D 키가 각 구간에서 메모리에 있는지를 색 막대로 보여 주는 그림

## 비활성 재부팅 (Inactivity Reboot)

iOS 18 에서는 잠긴 채 72시간(3일)이 지나면 기기가 스스로 재부팅해 BFU 로 돌아가고, 잠금을 풀 때마다 이 타이머가 새로 시작합니다[2]. 기기가 Wi-Fi 에 연결돼 있어도 재부팅합니다[2]. 처음 들어온 버전은 코드 분석으로 드러난 버전과 문답으로만 전해진 버전이 다릅니다.

| iOS 버전 | 내용 |
|---|---|
| iOS 18.0 | 7일 타이머로 처음 들어왔고 나중에 3일로 줄었다는 설명이 [2] 의 문답 절에 있음 |
| iOS 18.1·18.2 베타 | 분석 이벤트 문자열에 기능이 들어 있음 |
| iOS 18.2 | 분석 이벤트 문자열이 `inactivity_reboot` 에서 `inactivity_reboot_enabled` 로 바뀜 |

(출처: [2])

72시간이 지났는지는 Secure Enclave 가 판단합니다. `AppleSEPKeyStore` 커널 확장이 Secure Enclave 의 통지를 받아 사용자 영역에 알리고, SpringBoard 가 사용자 영역 프로세스를 정상 절차로 끝낸 뒤 재부팅합니다[2]. 기기는 재부팅 전에 NVRAM 변수 `aks-inactivity` 를 써 두고, 재부팅 뒤 `keybagd` 가 이 변수를 읽어 값이 있으면 잠금을 풀지 않은 시간을 담은 분석 이벤트를 Apple 로 보냅니다[2].

### 남는 흔적

| 흔적 | 내용 |
|---|---|
| 커널 로그 메시지 | `notifying user space of inactivity reboot` |
| 재부팅 실패 때 커널 패닉 문자열 | `max inactivity window expired, failed to reboot the device` |
| NVRAM 변수 | `aks-inactivity`. 재부팅 뒤에도 남음 |

(출처: [2])

압수한 뒤 획득하기 전에 기기가 BFU 로 돌아갔는지 판단할 때 이 흔적을 봅니다. 획득 기록에 BFU 상태로 적혀 있으면, 압수 시점에 이미 BFU 였는지 보관 중에 비활성 재부팅이 일어났는지를 이 로그와 NVRAM 변수로 구분해 볼 수 있습니다. 어떤 획득 방식에서 이 로그를 볼 수 있는지는 실제 기기로 확인해야 합니다. 통합 로그에서 찾는 방법은 [통합 로그에서 찾을 것 (Unified Log Events)](../../../02-artifacts/logs/unified-log-events.md) 에, 획득 방식은 [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md) 에 있습니다.

## 백업과 설정에서 보이는 이름

로컬 백업에는 잠금·키 가방과 관련된 이름을 단 키가 몇 개 있습니다. 키의 뜻은 이름만으로 단정할 수 없으니, 아래 표는 어디에 어떤 이름이 있는지까지만 알려 줍니다.

| 파일 | 키(형식) | 이름으로 짐작되는 것 |
|---|---|---|
| 백업 폴더 `Manifest.plist` | `WasPasscodeSet` | 백업할 때 기기에 암호가 설정돼 있었는지 |
| `HomeDomain` `Library/Preferences/com.apple.MobileBackup.plist` | `NotifyDaemonNextTimeKeyBagIsUnlocked` (bool), `FetchMissingKeysAtNextUnlock` (bool) | 다음 잠금 해제 때 할 백업 관련 작업 |
| `HomeDomain` `Library/Preferences/com.apple.NanoRegistry.NRLaunchNotificationController.volatile.plist` | `com.apple.mobile.keybagd.first_unlock.enabled` (int) | `keybagd` 의 첫 잠금 해제 알림 |

이 가운데 `WasPasscodeSet` 은 백업 당시 암호 설정 여부로 보이지만, 백업 시점의 값일 뿐 수집 시점의 BFU·AFU 상태를 알려 주지는 않습니다.

로컬 백업의 `HomeDomain` 에 있는 `Library/UserConfigurationProfiles/EffectiveUserSettings.plist` 와 `Library/UserConfigurationProfiles/Truth.plist` 의 `restrictedValue` 안에 `maxGracePeriod`, `maxInactivity`, `maxFailedAttempts`, `minLength`, `passcodeKeyboardComplexity` 같은 암호 정책 이름이 보입니다. `maxInactivity` 는 이름이 비슷하지만 비활성 재부팅과 같은 설정이라고 단정할 수 없으니 섞어 해석하지 않습니다. 프로필 흔적은 [구성 프로파일과 MDM (Configuration Profiles·MDM)](../../../02-artifacts/credentials-security/configuration-profiles.md) 에서, 암호 설정 흔적은 [암호와 Face ID 설정 흔적 (Passcode·Biometrics)](../../../02-artifacts/system-account/passcode-biometrics.md) 에서 다룹니다.

## 함정

- AFU 라고 모든 데이터가 풀리지는 않습니다. 화면이 잠긴 AFU 기기에서 Class A 파일과 `WhenUnlocked` 키체인 항목은 풀리지 않습니다[1][3].
- BFU 라고 아무것도 풀리지 않는 것도 아닙니다. Class D 는 UID 로만 보호되니 BFU 에서도 기기 안에서 풀릴 수 있다고 해석합니다[1].
- 비활성 재부팅이 iOS 18.0 에 7일 타이머로 들어왔다는 것은 [2] 의 문답 절에만 나오니, 보고서에는 "iOS 18 부터" 정도로 쓰고 첫 버전과 그 버전의 타이머 길이를 단정하지 않습니다[2].
- 보관 중 BFU 로 돌아간 기기를 두고 "압수 때부터 BFU 였다" 고 쓰지 않습니다. 재부팅 흔적을 확인한 만큼만 씁니다.

## 참고 문헌

1. Data Protection classes — Apple Platform Security — https://support.apple.com/guide/security/data-protection-classes-secb010e978a/web
2. Reverse Engineering iOS 18 Inactivity Reboot — Jiska Classen — https://naehrdine.blogspot.com/2024/11/reverse-engineering-ios-18-inactivity.html
3. Keychain data protection — Apple Platform Security — https://support.apple.com/guide/security/keychain-data-protection-secb0694df1a/web
