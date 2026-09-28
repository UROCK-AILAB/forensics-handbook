---
title: "데이터 사용량"
parent: "아티팩트 · 네트워크·연결"
nav_order: 770
---

# 데이터 사용량 (netstats)

데이터 사용량 기록 (netstats) 은 시스템이 네트워크 종류와 앱(UID)별로 주고받은 바이트·패킷 수를 1~2시간 구간으로 묶어 이진 파일에 쌓아 두는 기록이라서, "이 시간대에 이 앱이 이 네트워크로 이만큼 보내고 받았다" 를 앱 데이터와 상관없이 시스템 쪽에서 확인할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

Android 시스템 서비스(NetworkStatsService)가 네트워크 사용량을 세어 파일에 남기고, 현행 AOSP 기준으로 사용량을 기록하는 기록기(recorder)는 세 가지입니다 [2].

| 기록기 | 무엇별로 세나 |
|---|---|
| xt | 기기 전체, 인터페이스별 |
| uid | 앱 UID 별 |
| uid_tag | UID 와 태그별 |

예전에 있던 dev 기록기는 없어졌고, 옛 파일을 가져올 때 호환을 위해서만 잠깐 만듭니다 [2]. 파일 이름 앞부분은 `PREFIX_XT`, `PREFIX_UID`, `PREFIX_UID_TAG` 상수로 정하는데, 상수의 실제 문자열은 다른 소스 파일에 있고, ALEAPP 가 찾는 `xt*`·`uid*` 패턴과 맞습니다 [2][1].

시스템은 사용량을 메모리에 쌓다가 쌓인 양이 기본 2MB(`mPersistThreshold`)를 넘으면 디스크에 씁니다 [2]. 그래서 가장 최근 사용량은 확보 시점에 아직 파일에 들어가지 않았을 수 있습니다.

## 위치와 버전별 차이

현행 AOSP 는 두 위치 가운데 하나를 씁니다 [2].

| 위치 | 정하는 곳 | 비고 |
|---|---|---|
| 예전 위치 | `Environment.getDataDirectory()` 아래 `system/netstats`, 곧 `/data/system/netstats` | `getLegacyStatsDir` |
| 현재 위치 | 테더링(Tethering) 모듈 APEX 의 DE 데이터 폴더 아래 `netstats` | `ApexEnvironment.getApexEnvironment(TETHERING_MODULE_NAME).getDeviceProtectedDataDir()` |

어느 쪽을 쓸지는 DeviceConfig 플래그 `netstats_store_files_in_apexdata` 로 정하고 기본값은 true 입니다 [2]. 현재 위치의 실제 경로와 APEX 위치를 쓰기 시작한 Android 버전은 실제 기기에서 확인합니다. 현재 위치는 DE(기기 보호) 영역이고 [2], CE 와 DE 의 차이는 [저장 공간 암호화 (Encryption)](../../01-foundations/storage/encryption/index.md) 페이지에서 봅니다.

예전 위치에서 새 위치로 옮길 때는 옛 파일을 가져오는(import) 절차가 돌고, 시도·성공·대체 횟수를 통계 폴더 안의 `import.attempts`, `import.successes`, `import.fallbacks` 파일에 셉니다 [2]. 두 위치에 모두 파일이 있는 기기라면 이 세 파일로 가져오기가 어떻게 끝났는지 확인합니다.

ALEAPP 는 폴더 위치와 상관없이 아래 패턴으로 찾고, UID 를 패키지 이름으로 바꾸려고 `*/system/packages.xml` 도 함께 읽습니다 [1].

```
*/netstats/dev*
*/netstats/uid*
*/netstats/xt*
```

ALEAPP 가 이 모듈을 시험한 이미지는 삼성을 포함한 Android 10~17 여러 기기이고, 이미지 하나에서 수천~수만 행이 나왔습니다 [1].

설정 값의 global 영역에는 `netstats_enabled` 키가 있고, 모바일 데이터 관련 키로 `mobile_data`, `mobile_data_always_on`, `data_roaming`(유심 슬롯별 `data_roaming#` 포함), `preferred_network_mode` 가 있습니다. 설정 키를 읽는 법은 [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) 페이지에 있습니다.

## 구조

ALEAPP 의 netstats 모듈은 AOSP 소스를 따라 이진 파일을 읽고, 아래 내용은 그 모듈이 기대하는 모양입니다 [1]. 파일은 네트워크 식별 묶음(NetworkIdentitySet) 여러 개로 이루어지고, 묶음마다 기록(UID, set, tag, 이력)이 여러 개 들어 있습니다.

파일 첫 4바이트는 글자 "ANET" 이고 그다음 4바이트는 빅엔디언 정수로 된 형식 버전입니다. ALEAPP 는 통합 형식 버전 16 만 읽고, 예전 UID 형식(버전 2~4)은 읽지 않습니다 [1].

네트워크 식별 필드는 연결 종류(`net_type`), `rat_type`, `subscriber_id`, `network_id`, 로밍, 요금제 여부(metered), 기본 네트워크 여부(default_network), OEM 기능값, `sub_id`, `transport_type` 이고, 식별 버전이 올라가며 필드가 늘었습니다 [1].

| 식별 버전 | 더해진 필드 |
|---|---|
| 2 | 로밍 |
| 3 | `network_id` |
| 4 | metered |
| 5 | default_network |
| 6 | OEM 관리 네트워크 |
| 7 | `sub_id` |
| 8 | `transport_type` |

`network_id` 와 `subscriber_id` 에 실제로 어떤 값(SSID, 가입자 식별값 등)이 들어가는지는 실제 데이터에서 값을 읽은 뒤 [와이파이 설정과 접속 기록 (WifiConfigStore)](wifi.md) 의 SSID 목록과 맞춰 보고 뜻을 정합니다.

연결 종류 번호는 `ConnectivityManager` 의 옛 `TYPE_` 상수를 씁니다 [1].

| 번호 | 연결 종류 |
|---|---|
| 0 | MOBILE |
| 1 | WIFI |
| 4 | MOBILE_DUN |
| 7 | BLUETOOTH |
| 9 | ETHERNET |
| 13 | WIFI_P2P |
| 17 | VPN |

set 값과 특수 UID 는 아래처럼 풉니다 [1].

| 필드 | 값 | 뜻 |
|---|---|---|
| set | -1 | 합계 |
| set | 0 | 백그라운드 |
| set | 1 | 포그라운드 |
| set | 1001 | VPN_IN |
| set | 1002 | VPN_OUT |
| UID | -1 | 전체 합계(UID_ALL, 앱 구분 없음) |
| UID | -4 | 삭제된 앱(UID_REMOVED) |
| UID | -5 | 테더링(UID_TETHERING) |

이력(NetworkStatsHistory) 한 항목에는 구간 시작 시각, 구간 길이, 받은 바이트, 받은 패킷, 보낸 바이트, 보낸 패킷, operations 가 들어 있습니다 [1]. 이력 버전 1 에는 패킷 수와 operations 가 없고, 버전 2·3 은 값을 가변 길이 정수(varlong) 배열로 저장합니다 [1].

현행 AOSP 의 기록기별 기본 설정은 아래와 같습니다 [2].

| 기록기 | 구간 길이 | 회전 나이 | 삭제 나이 |
|---|---|---|---|
| xt | 1시간 | 15일 | 90일 |
| uid | 2시간 | 15일 | 90일 |
| uid_tag | 2시간 | 5일 | 15일 |

기본값대로라면 xt·uid 기록은 90일, uid_tag 기록은 15일이 지나면 지웁니다. 제조사가 이 값을 바꿨을 수 있으니 실제 기기에 남은 가장 오래된 구간으로 확인합니다.

## 증거로서 의미

**증명하는 것**

한 기록은 "이 구간에 이 UID 가 이 연결 종류로 이만큼 받고 보냈다" 를 뜻합니다. set 값으로 앱이 앞에 있을 때(포그라운드)인지 뒤에서(백그라운드) 쓴 것인지 나눌 수 있고, UID -5 기록은 테더링으로 다른 기기에 넘겨준 양입니다. 연결 종류 17 과 set 1001·1002 는 ALEAPP 가 VPN 으로 푸는 값이라서 VPN 과 관련된 사용량으로 볼 수 있지만, 두 set 값이 VPN 사용량을 어떻게 나눠 적는지는 단정할 수 없습니다. 앱 데이터가 지워졌어도 시스템 쪽 기록이라 남아 있을 수 있고, UID -4 는 그 사이 삭제된 앱의 사용량을 모아 둔 값입니다. 평소보다 보낸 바이트가 크게 튄 구간이 있으면 [자료를 밖으로 보냈나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) 조사에서 시간대를 좁히는 근거가 됩니다.

**증명하지 못하는 것**

상대 서버 주소, 주고받은 내용, 어떤 파일이었는지는 기록되지 않습니다. 시각은 1~2시간 구간 단위라서 몇 시 몇 분에 보냈는지 말할 수 없고, 보낸 바이트가 많다는 사실만으로 사용자가 무엇을 올렸다고 쓸 수 없습니다. UID 는 앱 하나가 아니라 같은 UID 를 나눠 쓰는 여러 패키지일 수 있으며, UID -4 로 합쳐진 사용량은 어느 앱이었는지 가릴 수 없습니다. 보고서에는 "이 시간대에 이 UID 가 모바일 네트워크로 이만큼 송신한 기록이 있다" 만큼만 씁니다.

## 시각 해석

이력의 구간 시작 시각은 유닉스 밀리초이고 [1] UTC 기준으로 바꾼 뒤 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 에서 확인한 기기 시간대로 옮깁니다. 구간 끝 시각은 시작 시각에 구간 길이를 더해 구하고, 사용이 그 구간 안 어느 순간에 있었는지는 알 수 없습니다. 값을 읽는 일반 방법은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

같은 사건이라도 xt 기록은 1시간, uid 기록은 2시간 구간이라서 [2] 두 기록의 경계가 어긋납니다. 기기 전체 사용량과 앱별 사용량을 나란히 놓을 때는 2시간 단위로 맞춰 비교합니다.

## 함정과 한계

첫째, 최근 사용량이 빠져 있을 수 있습니다. 메모리에 쌓인 양이 2MB 를 넘어야 디스크에 쓰니 [2], 확보 직전 몇 시간은 파일에 없을 수 있습니다. 기기가 켜져 있다면 아래 "공개 도구로 한 번" 의 `dumpsys netstats` 로 확인해 볼 수 있습니다. adb 일반 권한에서 되는지는 기기에서 먼저 확인합니다.

둘째, 보관 기간이 짧습니다. 기본값으로 uid_tag 는 15일, xt·uid 는 90일이라 [2], 오래된 사건은 이미 지워졌을 수 있습니다.

셋째, UID 를 패키지 이름으로 바꾸려면 `packages.xml` 이 필요합니다. ALEAPP 시험 이미지 하나에서는 `packages.xml` 이 암호화돼 있어 UID 만 보였습니다 [1]. UID 를 푸는 법은 [패키지 이름과 UID (Package Name·UID)](../../01-foundations/value-decoding/package-uid.md) 와 [설치된 앱 (packages.xml)](../app-usage/packages/index.md) 페이지에 있습니다.

넷째, 형식 버전이 다르면 도구가 읽지 못합니다. ALEAPP 는 버전 16 만 읽으니 [1], 예전 형식 파일이 결과에서 빠졌는지 파일 머리의 버전부터 확인합니다.

다섯째, 합계 행을 두 번 세지 않습니다. set -1 과 UID -1 은 합계라서 [1], 앱별 행과 더하면 사용량이 부풀려집니다.

## 직접 분석해 보기

### 헥스로 한 번

파일 사본을 헥스 편집기로 열어 첫 8바이트를 봅니다. 아래는 형식 설명으로 만든 예시이고 실제 데이터에서 나온 값이 아닙니다.

```
오프셋  00 01 02 03  04 05 06 07
0000   41 4E 45 54  00 00 00 10
       A  N  E  T   버전 16 (빅엔디언)
```

첫 4바이트가 "ANET" 이 아니면 netstats 이진 파일이 아니거나 다른 형식이고, 버전이 16 이 아니면 예전 형식이라 도구가 건너뛸 수 있습니다. 그 뒤 네트워크 식별 묶음부터는 식별 버전과 이력 버전에 따라 필드 수가 달라지니, 직접 끝까지 따라가기보다 머리를 확인한 뒤 도구 결과와 맞춰 봅니다.

### 공개 도구로 한 번

ALEAPP 의 `netstats` 모듈이 위 패턴의 파일을 읽어 구간 시각, 연결 종류, UID(패키지 이름), set, 받고 보낸 바이트를 표로 만들어 줍니다 [1]. 도구 결과에서 한 구간을 골라, 같은 구간의 앱별 행을 더한 값이 기기 전체 기록과 크게 어긋나지 않는지 확인합니다. 검증 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 페이지에 있습니다.

기기가 켜져 있고 명령을 쓸 수 있는 상황이라면 아래 명령으로 메모리에 있는 최근 기록까지 볼 수 있고, `detail` 은 `--uid`·`--tag` 를 함께 켭니다 [2]. adb 일반 권한에서 이 명령이 되는지는 기기에서 먼저 확인합니다. `dumpsys` 를 다루는 법은 [dumpsys 출력 (dumpsys)](../logs/dumpsys.md) 페이지에 있습니다.

```
dumpsys netstats --full --uid --tag --poll --checkin
```

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | 포그라운드 사용량이 있는 구간에 그 앱이 앞에 올라온 기록이 있는지 |
| [배터리 사용 기록 (batterystats)](../app-usage/batterystats.md) | 같은 시간대에 앱 작업이나 네트워크 상태 변화가 있는지 |
| [와이파이 설정과 접속 기록 (WifiConfigStore)](wifi.md) | Wi-Fi 사용 구간의 네트워크 식별값이 저장된 네트워크와 맞는지 |
| [테더링과 핫스폿 (Tethering·Hotspot)](tethering-hotspot.md) | UID -5 사용량이 있는 구간에 핫스폿이 켜져 있었는지 |
| [VPN 설정 (VPN)](vpn.md) | 연결 종류 17 이나 set 1001·1002 행이 있을 때 어느 VPN 이었는지 |

여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md), 조사 흐름은 [자료를 밖으로 보냈나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 시험 이미지에서 아래 질문을 풀어 봅니다.

1. netstats 파일이 예전 위치와 APEX 위치 가운데 어디에 있고, 파일 머리의 형식 버전은 몇입니까?
2. xt 기록에서 가장 이른 구간과 가장 늦은 구간은 언제이고, 그 사이 며칠치가 남아 있습니까?
3. uid 기록에서 보낸 바이트가 가장 큰 구간은 언제이고, 그 UID 는 어느 패키지입니까?
4. UID -4(삭제된 앱)나 UID -5(테더링) 행이 있습니까? 있다면 어느 시간대입니까?
5. 같은 구간의 앱별 행을 더한 값과 기기 전체 행은 얼마나 차이가 납니까?

## 참고 문헌

1. ALEAPP — scripts/artifacts/netstats.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/netstats.py
2. AOSP packages/modules/Connectivity — NetworkStatsService.java (main) — https://android.googlesource.com/platform/packages/modules/Connectivity/+/refs/heads/main/service-t/src/com/android/server/net/NetworkStatsService.java
