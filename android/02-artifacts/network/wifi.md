---
title: "와이파이 설정과 접속 기록"
parent: "아티팩트 · 네트워크·연결"
nav_order: 750
---

# 와이파이 설정과 접속 기록 (WifiConfigStore)

## 한 줄 요약

와이파이 설정 저장소 (WifiConfigStore) 는 폰에 저장된 Wi-Fi 네트워크마다 이름(SSID), 보안 방식, 설정을 만들고 고친 앱, 연결에 성공한 적이 있는지 같은 값을 XML 파일에 적어 두는 곳이고, 삼성 기기에서는 시각 필드와 별도 DB 가 더해져 이 폰이 어떤 네트워크를 알고 있었고 언제쯤 썼는지 추정하는 근거가 됩니다.

## 무엇을 기록하나 · 왜 생기나

사용자가 설정 화면에서 Wi-Fi 에 연결하거나 앱이 네트워크를 제안하면 Wi-Fi 서비스가 그 설정을 저장소에 적습니다. 이 저장소는 네트워크 설정을 보관하는 곳이고 접속할 때마다 한 줄씩 쌓는 로그가 아닙니다. 현행 AOSP 의 네트워크 필드 목록에는 생성 시각이나 마지막 연결 시각 필드가 없어서 [4], 시각은 제조사가 더한 필드나 다른 기록에서 찾아야 합니다.

현행 AOSP 기준으로 저장소는 모든 사용자가 함께 쓰는 공유(shared) 파일 두 개와 사용자마다 따로 두는 사용자별(user) 파일 두 개로 나뉩니다 [3].

| 구분 | 파일 | 담긴 것 | 폴더를 정하는 함수 |
|---|---|---|---|
| 공유 | `WifiConfigStore.xml` | 일반 설정 | `Environment.getWifiSharedDirectory()` |
| 공유 | `WifiConfigStoreSoftAp.xml` | 핫스폿 설정 | 같음 |
| 사용자별 | `WifiConfigStore.xml` | 일반 설정 | `Environment.getWifiUserDirectory(userId)` |
| 사용자별 | `WifiConfigStoreNetworkSuggestions.xml` | 앱이 제안한 네트워크 | 같음 |

핫스폿 설정 파일은 [테더링과 핫스폿 (Tethering·Hotspot)](tethering-hotspot.md) 페이지에서 다룹니다. 사용자별 저장소는 잠금을 푼 뒤에 열리는 CE 영역에 있어서, Wi-Fi 서비스는 부팅 직후에는 이 파일을 읽지 않고 잠금 해제나 사용자 전환 때 읽습니다 [3]. 잠금을 한 번도 풀지 않은 상태로 확보한 기기에서는 사용자별 파일을 읽지 못할 수 있으니, CE 와 DE 영역의 차이는 [저장 공간 암호화 (Encryption)](../../01-foundations/storage/encryption/index.md) 페이지에서 확인합니다. 사용자가 여럿인 기기라면 [사용자와 프로필 (Multi-user·users)](../system-account/users-profiles.md) 에서 사용자 번호부터 확인합니다.

## 위치와 버전별 차이

파일은 예전 위치와 APEX 위치 두 곳 가운데 하나에 있고, ALEAPP 는 두 곳을 아래 패턴으로 찾습니다 [1].

```
*/misc/wifi/WifiConfigStore.xml
*/misc**/apexdata/com.android.wifi/WifiConfigStore.xml
```

첫 줄은 예전 위치인 `/data/misc/wifi` 아래이고, 둘째 줄은 APEX 데이터 폴더 아래이며 `misc` 와 `misc_ce` 가 둘 다 걸리도록 쓴 패턴입니다 [1]. ALEAPP 는 이 모듈을 Android 10~16 이미지로 시험했습니다 [1]. 버전을 짐작해 한 곳만 보지 말고 두 패턴을 모두 찾습니다.

삼성 기기에는 ALEAPP 가 따로 읽는 SQLite DB 가 두 개 더 있습니다 [2]. 두 DB 는 경로 패턴으로 보아 이름이 `system` 인 폴더 아래에 있습니다.

| 파일 | ALEAPP 경로 패턴 | ALEAPP 시험 이미지 |
|---|---|---|
| `WifiConfigStore.db` | `*/system/WifiConfigStore.db*` | Android 13~15 삼성 기기 |
| `wifigeofence.db` | `*/system/wifigeofence.db*` | Android 10~15 삼성 기기 |

XML 파일에는 형식 버전이 적혀 있고, 현행 버전은 3 입니다 [3].

| 형식 버전 | 바뀐 점 |
|---|---|
| 1 | 처음 형식 |
| 2 | 무결성 정보(Integrity) 추가 |
| 3 | 자격 증명 암호화 추가, 무결성 정보 제거 |

`dumpsys wifi` 출력은 1만 줄이 넘을 만큼 길고(한 기기에서 약 10,850줄), 설정 상태(`WifiState`, `AirplaneModeOn`, `ScanAlwaysAvailable`, `WifiStateApm`, `WifiStateBt`, `SatelliteModeOn` 등)와 지원 기능 목록(`SupportedFeatures`), 상태 기계 기록(`WifiController`, `WifiClientModeManager`, `WifiClientModeImpl` 의 `rec[#]: time=... what=CMD_...` 줄)이 나옵니다. `WifiClientModeManager` 기록에는 `RequestorWs: WorkSource{... com.android.settings}` 처럼 Wi-Fi 클라이언트 모드를 켜 달라고 요청한 앱이 함께 찍히고, 이 줄은 특정 네트워크에 붙은 기록이 아니라 모드 전환 명령(`CMD_START`, `CMD_SWITCH_TO_CONNECT_MODE`) 기록입니다. 저장된 네트워크 목록이 이 출력에 나오는지와 adb 일반 권한으로 `WifiConfigStore.xml` 을 직접 읽을 수 있는지는 기기에서 확인합니다. `dumpsys` 를 받는 방법은 [dumpsys 출력 (dumpsys)](../logs/dumpsys.md) 페이지에 있습니다.

삼성 기기의 설정 값에는 Wi-Fi 관련 키가 여러 개 있습니다. global 쪽에는 `wifi_on`, `wifi_scan_always_enabled`, `wifi_wakeup_enabled`, `wifi_networks_available_notification_on`, `wifi_sleep_policy`, `network_avoid_bad_wifi`, `wifi_migration_completed`, `SecureWifiBackupExist`, `adb_wifi_enabled`, `auto_wifi`, `sem_auto_wifi_added_removed_list`, `sem_auto_wifi_control_enabled` 와 `sem_wifi_` 로 시작하는 키 여러 개가 있고, secure 쪽에는 `wifi_saved_state`, `wifi_apm_state`, `sem_wifi_turn_off_by_autowifi`, `sec_wifi_mlo_link_count` 가 있습니다. 키마다 값의 뜻을 밝힌 공식 문서는 없고, 특히 `sem_auto_wifi_added_removed_list` 에 어떤 형식으로 무엇이 들어가는지는 실제 데이터로 확인해야 합니다. 설정 키를 읽는 법은 [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) 페이지에 있습니다.

## 구조

문서 맨 위 요소는 `WifiConfigStoreData` 이고 그 아래에 `Version` 값이 있으며 [3], 네트워크 하나는 `Network` 요소 하나입니다. 네트워크 안의 값은 `name` 속성으로 구분합니다 [1]. 아래는 AOSP 소스의 필드 이름으로 만든 모양 예시이고, 각 값을 담는 요소의 실제 태그 형식은 실제 파일을 열어 확인합니다.

```
WifiConfigStoreData
├─ Version = 3
└─ ... Network
     ├─ name="SSID"
     ├─ name="ConfigKey"
     ├─ name="CreatorName"
     ├─ name="HasEverConnected"
     └─ ...
```

현행 AOSP 가 네트워크마다 적는 필드는 아래와 같습니다 [4].

| 묶음 | 필드 이름 |
|---|---|
| 식별 | `SSID`, `BSSID`, `ConfigKey`, `FQDN`, `ProviderFriendlyName`, `HiddenSSID` |
| 보안 | `PreSharedKey`, `WEPKeys`, `WEPTxKeyIndex`, `RequirePMF`, `AllowedKeyMgmt`, `AllowedProtocols`, `SecurityParamsList`·`SecurityParams`·`SecurityType` |
| 만들고 고친 쪽 | `CreatorUid`, `CreatorName`, `LastUpdateUid`, `LastUpdateName`, `LastConnectUid` |
| 연결 이력 관련 | `IsMostRecentlyConnected`, `NumRebootsSinceLastUse`, `DeletionPriority`, `ValidatedInternetAccess`, `NoInternetAccessExpected`, `DefaultGwMacAddress` |
| 폰 쪽 MAC | `RandomizedMacAddress`, `MacRandomizationSetting` |
| 선택 상태 | `SelectionStatus`, `DisableReason`, `ConnectChoice`, `ConnectChoiceRssi`, `HasEverConnected`, `CaptivePortalNeverDetected`, `HasEverValidatedInternetAccess` |
| IP 설정 | `IpAssignment`, `ProxySettings`, `ProxyHost`, `ProxyPort`, `ProxyPac`, `ProxyExclusionList` |
| 그 밖 | `MeteredHint`, `MeteredOverride`, `AutoJoinEnabled`, `Priority`, `Trusted`, `CarrierId`, `SubscriptionId`, `LinkedNetworksList`, `Shared` |

`CreatorUid`·`LastUpdateUid` 같은 숫자 UID 를 패키지 이름으로 바꾸는 법은 [패키지 이름과 UID (Package Name·UID)](../../01-foundations/value-decoding/package-uid.md) 페이지에서 다룹니다. `ConfigKey` 문자열을 큰따옴표로 자르면 세 번째 조각이 보안 방식(끝에 붙은 `WPA_PSK` 같은 값)입니다 [1]. `DefaultGwMacAddress` 는 그 네트워크의 기본 게이트웨이, 곧 공유기의 MAC 주소이고 폰이나 같은 네트워크에 붙은 다른 기기의 주소가 아닙니다 [1].

형식 버전 3 에서는 `PreSharedKey`(비밀번호), `WEPKeys`, DPP 키를 암호화해서 쓸 수 있고, 암호화하면 `EncryptedData` 와 `IV` 값으로 저장됩니다 [4]. 암호화할지는 파일을 만들 때 넘기는 `shouldEncryptCredentials` 값으로 정해지고 [3], 기본값은 기기와 버전마다 다를 수 있어 실제 기기에서 확인합니다. 암호화 도구가 없거나 암호화에 실패하면 알리지 않고 평문으로 쓰기 때문에 [4], 같은 버전의 파일이라도 비밀번호가 평문으로 보일 수도 있고 암호문으로 보일 수도 있습니다.

삼성 `WifiConfigStore.db` 에서 ALEAPP 가 읽는 표는 `configs` 이고, 열은 `CREATION_TIME`, `CONFIG_KEY`, `NETWORK_SCORE`, `CAPTIVE_PORTAL`, `LOCK_DOWN`, `NO_INTERNET_ACCESS_EXPECTED`, `NETWORK_DISABLE_REASON`, `_ID` 입니다 [2]. 예전 One UI 에는 `CREATION_TIME` 열이 없었고, Android 11 에서는 `NETWORK_DISABLE_REASON` 열도 없었습니다 [2]. `wifigeofence.db` 의 `geofence_wifi` 표에는 Wi-Fi 네트워크별 좌표가 들어 있고, 열은 `time`, `time_major`, `config_key`, `bssid`, `latitude`, `longitude`, `latitude_major`, `longitude_major`, `location_id`, `network_id`, `_id` 입니다 [2]. 좌표가 1000.0(열 기본값)이나 -1.0 이면 값이 없는 것입니다 [2].

## 증거로서 의미

**증명하는 것**

파일에 `Network` 항목이 있으면 그 SSID 의 설정이 확보 시점에 이 폰에 저장돼 있었다는 뜻이고, `CreatorName`·`LastUpdateName` 으로 설정을 만들고 마지막으로 고친 앱을 알 수 있습니다. 필드 이름으로 보면 `HasEverConnected` 는 연결에 성공한 적이 있는지, `IsMostRecentlyConnected` 는 가장 최근에 연결한 네트워크인지를 적는 필드라서, 저장만 해 둔 네트워크와 실제로 붙어 본 네트워크를 나누는 데 씁니다. `DefaultGwMacAddress` 는 공유기 주소라서 이름이 같은 네트워크가 여러 곳에 있을 때 어느 공유기였는지 가려내는 단서가 될 수 있고, 삼성 `wifigeofence.db` 에 좌표가 있으면 그 네트워크와 묶인 위치를 볼 수 있습니다. 앱이 제안한 네트워크 파일에 항목이 있으면 사용자가 아니라 앱이 넣은 네트워크라는 점을 따로 구분할 수 있습니다.

**증명하지 못하는 것**

AOSP 필드에는 시각이 없어서 이 파일만으로는 특정 시각에 그 네트워크에 붙어 있었다고 말할 수 없고, 연결 횟수나 연결된 동안 주고받은 데이터 양도 나오지 않습니다. SSID 는 누구나 같은 이름으로 만들 수 있어서 이름만으로 장소를 정할 수 없고, `PreSharedKey` 가 저장돼 있다고 해서 사용자가 비밀번호를 직접 입력했거나 알고 있었다는 뜻도 아닙니다. 네트워크를 지운 뒤 파일에 무엇이 남는지 밝힌 공개 자료가 없으니, 항목이 없다는 사실만으로 연결한 적이 없다고 결론 내리지 않습니다.

## 시각 해석

`semCreationTime`, `semUpdateTime`, `LastConnectedTime` 세 필드는 유닉스 밀리초 시각이고, 0 이하 값은 비어 있는 값입니다 [1]. `sem` 으로 시작하는 두 필드는 AOSP 필드 목록에 없어서 제조사(삼성)가 더한 필드로 보입니다. `LastConnectedTime` 을 쓰는 제조사 범위는 공개 자료가 없어 실제 데이터로 확인해야 합니다. 필드 이름으로 보면 설정을 만든 시각, 고친 시각, 마지막으로 연결한 시각으로 읽을 수 있지만, 정확히 어떤 동작 때 값이 바뀌는지는 실제 데이터에서 다른 기록과 맞춰 본 뒤 씁니다.

삼성 `configs` 표의 `CREATION_TIME` 은 유닉스 시각을 담은 TEXT 열이고 [2], 초인지 밀리초인지는 값으로 판별합니다. 값이 13자리 안팎이면 밀리초, 10자리 안팎이면 초일 가능성이 높으니 자릿수부터 보고 바꿉니다. `wifigeofence.db` 의 `time`·`time_major` 열 단위도 같은 방법으로 판별합니다. 값을 읽는 일반 방법은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

`dumpsys wifi` 상태 기계 기록의 시각은 `time=MM-DD HH:MM:SS.mmm` 모양이고 연도가 없습니다. 출력에 시간대도 적혀 있지 않으니, 연도는 수집 날짜에서 거꾸로 짐작하고 시간대는 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 에서 확인한 뒤 보고서에 씁니다.

## 함정과 한계

첫째, 경로가 두 곳입니다. 예전 위치에서 파일을 찾지 못했다고 Wi-Fi 설정이 없다고 보면 안 되고, APEX 위치와 사용자별 폴더, 앱 제안 네트워크 파일까지 모두 확인합니다.

둘째, 비밀번호 필드는 평문일 때도 암호문일 때도 있습니다. 암호문이면 `EncryptedData`·`IV` 값만 보이고, 평문이면 보고서와 증거 사본을 다룰 때 제3자의 비밀번호가 드러나지 않게 가립니다.

셋째, 시각 필드는 제조사 쪽 필드입니다. 다른 제조사 기기나 AOSP 에 가까운 기기에서는 시각 필드가 아예 없을 수 있어서, 이때는 [데이터 사용량 (netstats)](netstats.md) 이나 [배터리 사용 기록 (batterystats)](../app-usage/batterystats.md) 에서 시간대를 찾습니다.

넷째, 저장은 AtomicFile 로 하고 쓰기를 모아 두었다가 알람("WriteBufferAlarm")으로 한꺼번에 쓰는 방식이 있어서 [3], 설정을 바꾼 순간과 파일 수정 시각이 다를 수 있습니다. 파일 수정 시각을 네트워크 추가 시각으로 읽지 않습니다.

다섯째, 저장된 네트워크가 거의 없는 기기라면 초기화 뒤에 쓰던 기기일 수도 있으니, 네트워크 목록이 짧다는 사실만으로 해석하지 말고 [초기화 흔적 (Factory Reset)](../system-account/factory-reset.md) 페이지의 기록부터 확인합니다.

## 직접 분석해 보기

### 파일을 직접 한 번

XML 은 글자로 된 형식이라 헥스 대신 문서 구조를 따라갑니다. 사본을 텍스트 편집기로 열어 `WifiConfigStoreData` 아래 `Version` 값을 먼저 보고, `Network` 요소를 하나씩 따라가며 `name` 속성이 `SSID`, `ConfigKey`, `CreatorName`, `HasEverConnected` 인 값을 적어 둡니다. 편집기에서 글자가 보이지 않고 이진 데이터처럼 보이면 바이너리 XML 로 저장됐을 수 있으니 [안드로이드 바이너리 XML (ABX)](../../01-foundations/data-formats/abx.md) 페이지를 보고 변환부터 합니다.

같은 일을 파이썬 표준 라이브러리로 하면 아래와 같습니다. `Network` 요소를 차례로 읽고 `name` 속성으로 필드를 구분하는 예시이고 [1], 값이 속성에 있을 때와 글자로 있을 때를 모두 찍습니다.

```python
import xml.etree.ElementTree as ET

root = ET.parse('WifiConfigStore.xml').getroot()
for net in root.iter('Network'):
    print('---')
    for elem in net.iter():
        name = elem.attrib.get('name')
        if name in ('SSID', 'ConfigKey', 'CreatorName',
                    'HasEverConnected', 'DefaultGwMacAddress'):
            print(name, elem.attrib, (elem.text or '').strip())
```

삼성 DB 는 사본을 SQLite 도구로 열어 아래처럼 읽습니다. 예전 One UI 에는 `CREATION_TIME` 열이 없으니 오류가 나면 열 목록부터 확인합니다. SQLite 파일을 다루는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md) 페이지에 있습니다.

```sql
SELECT _ID, CONFIG_KEY, CREATION_TIME, NETWORK_DISABLE_REASON
FROM configs
ORDER BY CREATION_TIME;
```

### 공개 도구로 한 번

ALEAPP 의 `wifiProfiles` 모듈이 XML 두 위치를 찾아 네트워크 표를 만들고 [1], `samsungWifiDatabases` 모듈이 삼성 DB 두 개를 읽습니다 [2]. 도구 결과의 SSID·시각 몇 줄을 위에서 직접 읽은 값과 맞춰 보면 도구가 필드를 제대로 풀었는지 확인할 수 있고, 검증 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 페이지에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [데이터 사용량 (netstats)](netstats.md) | Wi-Fi 연결 종류로 데이터가 오간 시간대가 있는지 |
| [배터리 사용 기록 (batterystats)](../app-usage/batterystats.md) | 배터리 기록의 `+wifi_scan`·`-wifi_scan` 표시가 있는 시간대와 연결 시각이 어울리는지 |
| [위치 캐시 (Cached Locations)](../location/cached-locations.md) | `wifigeofence.db` 좌표와 같은 시간대 위치 기록이 맞는지 |
| [테더링과 핫스폿 (Tethering·Hotspot)](tethering-hotspot.md) | 폰이 네트워크에 붙은 쪽인지, 네트워크를 내어 준 쪽인지 |
| [설치된 앱 (packages.xml)](../app-usage/packages/index.md) | `CreatorUid`·`LastUpdateUid` 가 어느 앱인지 |

장소와 시각을 엮는 흐름은 [그 시각에 어디 있었나 (Location)](../../04-scenarios/activity/location.md), 여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 시험 이미지에서 아래 질문을 풀어 봅니다.

1. `WifiConfigStore.xml` 이 예전 위치와 APEX 위치 가운데 어디에 있고, `Version` 값은 몇입니까?
2. 저장된 네트워크는 몇 개이고, 그 가운데 `HasEverConnected` 값으로 보아 연결에 성공한 적이 있는 네트워크는 몇 개입니까?
3. 설정을 만든 앱(`CreatorName`)이 설정 앱이 아닌 네트워크가 있습니까? 있다면 어느 앱입니까?
4. 비밀번호 필드는 평문입니까, `EncryptedData`·`IV` 로 된 암호문입니까?
5. 삼성 기기라면 `configs` 표의 `CREATION_TIME` 은 몇 자리이고, 초와 밀리초 가운데 어느 쪽으로 바꿔야 날짜가 말이 됩니까?

## 참고 문헌

1. ALEAPP — scripts/artifacts/wifiProfiles.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/wifiProfiles.py
2. ALEAPP — scripts/artifacts/samsungWifiDatabases.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/samsungWifiDatabases.py
3. AOSP packages/modules/Wifi — WifiConfigStore.java (main) — https://android.googlesource.com/platform/packages/modules/Wifi/+/refs/heads/main/service/java/com/android/server/wifi/WifiConfigStore.java
4. AOSP packages/modules/Wifi — XmlUtil.java (main) — https://android.googlesource.com/platform/packages/modules/Wifi/+/refs/heads/main/service/java/com/android/server/wifi/util/XmlUtil.java
