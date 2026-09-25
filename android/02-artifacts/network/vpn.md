---
title: "VPN 설정"
parent: "아티팩트 · 네트워크·연결"
nav_order: 790
---

# VPN 설정 (VPN)

## 한 줄 요약

VPN 흔적은 한 파일에 모여 있지 않고 항상 켜짐 VPN 설정 값, 앱 권한 기록(AppOps)의 VPN 동의와 연결 구간, VPN 프로필 저장소, 데이터 사용량의 VPN 몫에 흩어져 남아서, 이 폰에서 어떤 VPN 을 쓰도록 설정했고 VPN 을 거친 사용량이 있었는지를 여러 기록을 맞춰 가며 확인합니다.

## 무엇을 기록하나 · 왜 생기나

현행 AOSP 는 VPN 을 세 종류로 나눕니다 [1].

| 종류 | 뜻 |
|---|---|
| `TYPE_VPN_SERVICE` | 앱이 VpnService 로 만든 VPN |
| `TYPE_VPN_PLATFORM` | IKEv2 같은 플랫폼 VPN 프로필 |
| `TYPE_VPN_LEGACY` | 예전 내장 VPN |

앱이 VPN 을 쓰려면 사용자 동의가 필요하고, 동의는 앱 권한 기록(AppOps)에 `OPSTR_ACTIVATE_VPN`(VpnService 앱) 또는 `OPSTR_ACTIVATE_PLATFORM_VPN`(플랫폼 VPN) 으로 남습니다 [1]. VPN 이 실제로 연결된 동안에는 시스템이 AppOps 의 `OPSTR_ESTABLISH_VPN_SERVICE`(VpnService 앱) 또는 `OPSTR_ESTABLISH_VPN_MANAGER`(플랫폼 VPN) 을 시작(startOp)하고, 연결이 끝나면 마칩니다(finishOp) [1]. 그래서 AppOps 기록에는 동의했다는 사실과 연결 구간이 따로 남을 수 있습니다. AppOps 를 어느 파일에 저장하는지, 연결 구간이 파일에 얼마나 남는지는 이번 자료로 확인하지 못했습니다. 앱 권한의 짜임새는 [앱 샌드박스와 권한 (Sandbox·Permissions)](../../01-foundations/security-model/sandbox-permissions.md) 페이지에서 다룹니다.

사용자가 특정 VPN 을 늘 켜 두도록 고르면 항상 켜짐(Always-on) VPN 설정이 생기고, 현행 AOSP 는 이 설정을 사용자별 Settings.Secure 에 저장합니다 [1].

| 상수 | 담긴 것 |
|---|---|
| `ALWAYS_ON_VPN_APP` | 항상 켜짐으로 지정한 VPN 앱의 패키지 이름 |
| `ALWAYS_ON_VPN_LOCKDOWN` | VPN 없이는 인터넷을 막는 설정. 항상 켜짐과 잠금이 둘 다일 때만 1 을 씀 |
| `ALWAYS_ON_VPN_LOCKDOWN_WHITELIST` | 잠금 중에도 VPN 을 거치지 않아도 되는 앱 목록(쉼표로 구분한 패키지 이름) |

위 이름은 소스의 상수 이름이고, 설정 DB 에 실제로 적히는 키 문자열은 Settings.java 를 열지 않아 확인하지 못했습니다. 앱은 매니페스트 메타데이터 `VpnService.SERVICE_META_DATA_SUPPORTS_ALWAYS_ON` 을 false 로 두어 항상 켜짐 지원을 끌 수 있습니다 [1].

## 위치와 버전별 차이

| 흔적 | 저장하는 곳 | 확인한 것 |
|---|---|---|
| 항상 켜짐 설정 | 사용자별 Settings.Secure | 상수 이름 [1], 실제 키 문자열은 확인 못 함 |
| VPN 동의와 연결 구간 | AppOps | op 이름 [1], 저장 파일은 확인 못 함 |
| 플랫폼 VPN 프로필 | VpnProfileStore | 저장 이름 규칙 [1], 실제 저장 위치는 확인 못 함 |
| VPN 사용량 | netstats | 연결 종류 17, set 1001·1002 [2] |

플랫폼 VPN 프로필은 VpnProfileStore 에 `Credentials.PLATFORM_VPN` + 사용자 ID + `_` + 패키지 이름이라는 이름으로 저장하고, 프로필 하나는 최대 128kB 입니다 [1]. 앱별 VPN 제외 설정도 같은 저장소에 `VPNAPPEXCLUDED_` + 사용자 ID + `_` + 패키지 이름으로 저장합니다 [1]. VpnProfileStore 가 실제로 어디에(키스토어 등) 저장하는지와 `Credentials.PLATFORM_VPN` 문자열 값은 확인하지 못했습니다. 예전 내장 VPN 은 패키지 이름 자리에 `VpnConfig.LEGACY_VPN` 을 쓰고, 예전 VPN 데몬은 VPN_UID 로 돌며 키스토어 키를 넘겨받습니다(`keystore2.grant`) [1].

어느 Android 버전부터 이 구조였는지는 확인하지 못했습니다. 저장 이름에 사용자 ID 가 들어가니 사용자가 여럿인 기기에서는 [사용자와 프로필 (Multi-user·users)](../system-account/users-profiles.md) 에서 사용자 번호를 먼저 확인합니다.

관찰 기기에서 adb 일반 권한으로 본 settings secure 키 목록에는 `vpn` 이 들어간 키가 하나도 없었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 키 목록에는 그 기기에 실제로 저장된 키만 나오니, 그 기기에서 항상 켜짐 VPN 을 지정한 적이 없어서일 수 있습니다. 같은 목록에 `lockdown_in_power_menu` 라는 키가 있었지만 (확인 범위: SM-S937N, Android 16, One UI 8.5), 이름에 lockdown 이 들어 있다는 것 말고는 VPN 잠금 설정과 같은 것이라는 근거가 없어서 VPN 흔적으로 보지 않습니다. `dumpsys connectivity` 와 `dumpsys vpn_management` 출력은 관찰하지 못했습니다. 설정 키를 읽는 법은 [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) 페이지에 있습니다.

## 구조

VPN 흔적은 전용 파일 형식이 아니라 각 저장소의 형식을 따릅니다. 항상 켜짐 설정은 설정 값 한 줄씩이고, 사용량은 netstats 이진 파일의 한 행입니다. netstats 에서 VPN 과 관련된 값은 아래 셋이고 [2], 파일 형식 전체는 [데이터 사용량 (netstats)](netstats.md) 페이지에서 다룹니다.

| 칸 | 값 | 뜻 |
|---|---|---|
| 연결 종류 | 17 | VPN |
| set | 1001 | VPN_IN |
| set | 1002 | VPN_OUT |

VPN 상태가 바뀌면 시스템은 `VpnManager.ACTION_VPN_MANAGER_EVENT` 를 VPN 앱에 보내고, 이 알림에는 `EXTRA_TIMESTAMP_MILLIS`(System.currentTimeMillis 값, 유닉스 밀리초)가 들어 있습니다 [1]. 이 이벤트가 파일로 남는지는 확인하지 못했습니다. 연결이 끊기면 시스템은 `NOTE_VPN_DISCONNECTED` 알림을 띄우니 [1], 알림 기록이 남는 기기라면 끊긴 시각을 찾는 단서가 될 수 있습니다.

## 증거로서 의미

**증명하는 것**

항상 켜짐 설정에 패키지 이름이 있으면 사용자(또는 기기 관리 주체)가 그 앱을 항상 켜짐 VPN 으로 지정해 둔 상태였다는 뜻이고, 잠금 값이 1 이면 VPN 없이는 인터넷이 막히도록 설정돼 있었다는 뜻입니다 [1]. AppOps 에 VPN 동의 기록이 있으면 그 앱에 VPN 을 허락했다는 기록이고, 연결 구간 기록이 남아 있다면 VPN 이 연결돼 있던 시간대를 가늠할 수 있습니다 [1]. netstats 에 연결 종류 17 이나 set 1001·1002 행이 있으면 그 구간에 VPN 과 관련된 사용량이 잡혔다는 기록입니다 [2]. 두 set 값이 VPN 사용량을 어떤 방식으로 나눠 적는지는 확인하지 못했으니, 앱별 행과 더해 합계를 내지 않습니다.

**증명하지 못하는 것**

VPN 설정이나 사용량 기록은 VPN 너머에서 어느 사이트에 접속했는지, 무엇을 주고받았는지 말하지 않습니다. VPN 앱이 깔려 있거나 동의 기록이 있다는 사실만으로 사건 시각에 VPN 이 켜져 있었다고 쓸 수 없고, 반대로 항상 켜짐 설정이 없다고 VPN 을 쓰지 않았다고 볼 수도 없습니다. VPN 을 썼다는 사실 자체는 흔한 일이라서 숨기려는 의도로 읽으려면 다른 정황이 따로 필요합니다.

## 시각 해석

항상 켜짐 설정 값에는 시각이 없고, 확보 시점의 상태만 알려 줍니다. VPN 을 거친 사용량의 시각은 netstats 구간 시작 시각(유닉스 밀리초)과 구간 길이로 읽으며 [2], 1~2시간 단위라서 연결한 순간을 짚지 못합니다. `ACTION_VPN_MANAGER_EVENT` 의 시각은 유닉스 밀리초이지만 [1] 파일에 남는지 모르니, 그 값을 찾았다면 어디서 찾았는지 함께 적습니다. 값을 읽는 일반 방법은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../01-foundations/value-decoding/time-values.md), 현지 시각으로 옮기는 법은 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 페이지에 있습니다.

## 함정과 한계

첫째, 흔적이 흩어져 있어서 한 곳만 보고 "VPN 기록 없음" 이라고 쓰기 쉽습니다. 설정 값, AppOps, 프로필 저장소, netstats 를 모두 확인하고, 확인하지 못한 곳은 보고서에 따로 적습니다.

둘째, 키 문자열을 짐작하지 않습니다. 상수 이름과 실제 설정 키 문자열은 다를 수 있으니, 설정 목록 전체를 받아 `vpn` 이 들어간 키를 찾는 쪽이 안전합니다.

셋째, 이름이 비슷한 키에 속지 않습니다. 관찰 기기의 `lockdown_in_power_menu` 처럼 lockdown 이 들어간 키가 VPN 과 관련 있다는 근거는 없습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5).

넷째, 항상 켜짐 VPN 은 사용자가 아니라 회사 기기 관리 정책이 지정했을 수도 있습니다. 기기 관리 주체가 있는지는 [기기 관리자와 접근성 권한 (Device Admin·Accessibility)](../credentials-security/device-admin-accessibility.md) 과 [보안 폴더와 작업 프로필 (Secure Folder·Work Profile)](../../01-foundations/security-model/secure-folder-work-profile.md) 에서 확인합니다.

다섯째, VPN 앱마다 자기 데이터 폴더에 따로 기록을 남길 수 있습니다. ALEAPP 에는 앱별 VPN 모듈(`nordVpn.py`, `protonVPN.py`)이 있지만 [3] 이번에 내용을 열어 보지 않았으니, 앱 쪽 기록은 [앱 데이터 분석 (App Data Analysis)](../../03-techniques/analysis/app-data-analysis/index.md) 방법으로 따로 봅니다.

## 직접 분석해 보기

### 설정 값으로 한 번

기기가 켜져 있고 adb 를 쓸 수 있는 상황이라면 secure 설정 목록 전체를 받아 VPN 관련 키가 있는지 찾습니다. 관찰 기기에서는 이 방법으로 본 목록에 `vpn` 이 들어간 키가 없었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5).

```
adb shell settings list secure | grep -i vpn
```

키가 나오면 값에 적힌 패키지 이름을 [설치된 앱 (packages.xml)](../app-usage/packages/index.md) 목록에서 찾아 설치 시각과 설치한 곳을 확인합니다. 이미지로 확보한 검체라면 설정 저장 파일에서 같은 키를 찾고, 설정 저장 형식은 [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) 페이지를 따릅니다.

### netstats 로 한 번

netstats 이진 파일의 헥스 따라가기는 [데이터 사용량 (netstats)](netstats.md) 페이지에 있습니다. ALEAPP `netstats` 모듈 결과 [2] 에서 연결 종류가 17 이거나 set 이 1001·1002 인 행만 거르면 VPN 을 거친 사용량이 잡힌 구간이 나오고, 그 구간에 어느 UID 가 사용량을 냈는지 봅니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [데이터 사용량 (netstats)](netstats.md) | VPN 몫 사용량이 있는 구간 |
| [설치된 앱 (packages.xml)](../app-usage/packages/index.md) | 항상 켜짐으로 지정된 VPN 앱이 언제 어디서 설치됐는지 |
| [알림 기록 (Notification History)](../app-usage/notification-history.md) | VPN 연결이 끊겼다는 알림이 남아 있는지 |
| [설치된 인증서 (User Certificates)](../credentials-security/user-certificates.md) | 같은 시기에 사용자 인증서가 추가됐는지 |
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | VPN 앱 화면이 앞에 올라온 시각 |

모르는 VPN 앱이 설정돼 있을 때 따지는 흐름은 [악성 앱 흔적 분석 (Malicious App Triage)](../../03-techniques/analysis/malicious-app-triage/index.md) 과 [몰래 설치된 감시 앱 (Stalkerware)](../../04-scenarios/incident/stalkerware.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 검체에서 아래 질문을 풀어 봅니다.

1. secure 설정에 VPN 관련 키가 있습니까? 있다면 어느 패키지가 항상 켜짐으로 지정돼 있고, 잠금 값은 무엇입니까?
2. 지정된 VPN 앱은 언제 설치됐습니까?
3. netstats 에 연결 종류 17 이나 set 1001·1002 행이 있습니까? 있다면 가장 이른 구간과 가장 늦은 구간은 언제입니까?
4. VPN 사용량이 잡힌 구간과 그 VPN 앱이 앞에 올라온 시각은 어떻게 이어집니까?

## 참고 문헌

1. AOSP frameworks/base — Vpn.java (main) — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/connectivity/Vpn.java
2. ALEAPP — scripts/artifacts/netstats.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/netstats.py
3. ALEAPP — scripts/artifacts 폴더 목록 — https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
