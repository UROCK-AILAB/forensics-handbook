---
title: "침입 로깅"
parent: "아티팩트 · 로그"
nav_order: 1240
---

# 침입 로깅 (Intrusion Logging)

침입 로깅 (Intrusion Logging) 은 고급 보호 모드 (Advanced Protection) 에서 켜는 선택 기능이고, 앱 프로세스 시작·앱 설치·USB 파일 전송·잠금 해제 같은 보안 이벤트와 앱별 DNS 조회·네트워크 연결을 기기가 암호화해 사용자의 Google 계정에 12개월 동안 보관합니다 [1][2]. 기기 안의 로그와 달리 기기 밖에 사본이 남아서, 기기 소유자가 동의해 내려받은 기록으로 감염이 의심되는 기간의 앱 활동을 시간순으로 따라갈 수 있습니다 [1][13].

## 무엇을 기록하나 · 왜 생기나

고급 보호 모드는 표적 공격을 막는 보호 기능을 한 번에 켜는 설정이고, 켜려면 화면 잠금이 있어야 합니다 [2]. 기기 보호를 켜는 화면에서 침입 로깅을 켜거나 건너뛸 수 있고, 켜면 암호화한 로그를 백업할 Google 계정을 고릅니다 [2]. 침입 로깅은 감염이 의심될 때 기기를 조사할 수 있도록 기록을 남기는 기능이라 [3], 켜 두기 전의 기록은 나중에 만들어 낼 수 없습니다 [13].

기록되는 내용은 세 종류입니다 [5][9].

| JSON 최상위 이름 | 내용 | 어디서 오나 |
|---|---|---|
| `security_event` | 보안 이벤트. 앱 프로세스 시작, 앱 설치·업데이트·제거, ADB 셸과 파일 전송, 잠금 화면, 부팅, 인증서 설치 등 | 기기 관리 정책의 감사 로그 (`SecurityLog`) [4][6] |
| `dns_event` | 앱이 시스템 해석기로 조회한 호스트 이름과 응답 IP | netd 의 DNS 이벤트 [6] |
| `connect_event` | 앱이 연 네트워크 연결의 목적지 IP 와 포트 | netd 의 연결 이벤트 [6] |

AOSP 의 `com.android.server.security.intrusiondetection` 코드는 보안 이벤트를 `DevicePolicyManager` 의 감사 로그 (audit log) 를 켜서 받고, 네트워크 이벤트를 netd 이벤트 콜백으로 받아 한데 모읍니다 [5][6]. 네트워크 이벤트의 패키지 이름은 이벤트에 붙은 UID 를 패키지 관리자에 물어 얻은 이름입니다 [6]. UID 와 패키지 이름의 관계는 [패키지 이름과 UID](../../01-foundations/value-decoding/package-uid.md) 에서 다룹니다.

기록 대상은 앱 프로세스 시작, 앱 설치·업데이트·제거, Wi-Fi·Bluetooth 시작과 중지, DNS 조회와 IP 주소, USB 로 주고받은 파일, 시스템 인증서 변경, 기기 잠금·해제이고, Chrome 시크릿 모드의 네트워크 이벤트도 시스템 수준에서 기록됩니다 [1].

## 위치와 버전별 차이

기록은 Android 16 부터 생깁니다. Google 은 2026년 5월 12일에 침입 로깅을 Android 16 12월 업데이트 이상을 쓰는 기기에 배포하고 있다고 밝혔고 [3], 같은 날 Amnesty International Security Lab 글에는 고급 보호 모드와 침입 로깅이 Android 16 이상의 Pixel 에서만 쓸 수 있고 다른 제조사는 뒤에 지원할 예정이라고 나와 있습니다 [13]. 분석 대상 기기에서 쓸 수 있었는지는 아래 설정 값과 기기 빌드로 확인합니다. 빌드 확인은 [기기 정보와 빌드 (build.prop·Build)](../system-account/device-build.md) 에서 다룹니다.

| 위치 | 내용 |
|---|---|
| Google 계정 (서버) | 기기가 종단 간 암호화한 로그. 12개월이 지나면 자동으로 지워지고, 그 전에는 사용자도 Google 도 지울 수 없음 [1] |
| 기기 설정 secure `advanced_protection_mode` | `1` 이면 고급 보호 모드가 켜져 있음. `0` 이면 꺼져 있음. 키가 없어 `null` 이 나오면 지원하지 않는 기기로 봄 [7] |
| 기기 `/sdcard/Download/Intrusion Logging/` | 사용자가 Download & decrypt 로 받은 파일이 저장되는 폴더 [7][13] |

로그를 받는 경로는 기기 설정의 Security & privacy → Advanced Protection → Intrusion Logging → Access logs → Download & decrypt 입니다 [1]. 한국어 화면에서는 같은 순서의 한국어 메뉴 이름으로 찾습니다. 받을 때 기기의 화면 잠금 인증을 거치고 [13], 같은 Google 계정에 로그인한 다른 Android 기기에서도 받을 수 있습니다 [1]. 암호화 키는 Google 계정 비밀번호와 화면 잠금 자격 증명이 보호하고, Google 은 이 둘을 모르기 때문에 사용자 말고는 로그를 읽을 수 없습니다 [1]. 그래서 분석가는 기기 소유자가 직접 내려받아 넘긴 파일만 다룹니다.

기기는 기본값으로 하루에 한 번 로그를 모아 올립니다 [13]. 침입 로깅을 끄면 기록은 바로 멈추고, 모아 두고 아직 올리지 않은 로그는 끄기 전에 올립니다 [1].

## 구조

내려받은 파일은 한 줄에 JSON 객체 하나가 있는 줄 단위 JSON (newline-delimited JSON) 텍스트이고, 객체마다 최상위 키 하나가 이벤트 종류를 나타냅니다 [9]. 아래는 만든 예시입니다.

```
{"dns_event": {"event_time": 1788000000000, "package_name": "com.example.chat", "hostname": "api.example.com", "ip_addresses": ["/203.0.113.10"], "ip_addresses_count": 1}}
{"connect_event": {"event_time": 1788000000350, "package_name": "com.example.chat", "port": 443, "ip_address": "/203.0.113.10"}}
{"security_event": {"event_time": 1788000045123456789, "event_id": 4821, "adb_shell_cmd": {"command": "pm list packages"}}}
```

`dns_event` 에는 `event_time`, `package_name`, `hostname`, `ip_addresses`, `ip_addresses_count` 필드가 있고, `connect_event` 에는 `event_time`, `package_name`, `port`, `ip_address` 필드가 있습니다 [14]. IP 주소 값은 `/203.0.113.10` (만든 예시) 처럼 앞에 `/` 가 붙어 나오고, MVT 는 분석할 때 이 `/` 를 떼어 냅니다 [10][14].

`security_event` 에는 `event_time` 과 `event_id` 가 있고, 나머지 키 하나의 이름이 보안 이벤트 종류이며 그 값이 세부 필드를 담습니다 [10]. 종류 이름은 대부분 `SecurityLog` 태그 이름에서 `TAG_` 를 떼고 소문자로 바꾼 모양이지만 `adb_sync_recv_file` (`TAG_SYNC_RECV_FILE`) 처럼 다른 것도 있고, 태그 번호는 210001 부터 이어집니다 [4][10]. 자주 보는 종류는 아래와 같습니다.

| JSON 이름 | SecurityLog 태그 | 세부 필드 | 뜻 |
|---|---|---|---|
| `app_process_start` | `TAG_APP_PROCESS_START` | `process`, `start_time`, `uid`, `pid`, `seinfo`, `sha256` | 앱 프로세스 시작. `sha256` 은 기본 APK 의 SHA-256 [4][14] |
| `package_installed`, `package_updated`, `package_uninstalled` | `TAG_PACKAGE_INSTALLED` 등 | `package_name`, `version_code`, `user_id` | 앱 설치·업데이트·제거 [4][10] |
| `adb_shell_interactive` | `TAG_ADB_SHELL_INTERACTIVE` | 없음 | `adb shell` 로 대화형 셸을 열었음 [4] |
| `adb_shell_cmd` | `TAG_ADB_SHELL_CMD` | `command` | `adb shell` 뒤에 붙여 실행한 명령 [4][10] |
| `adb_sync_recv_file`, `adb_sync_send_file` | `TAG_SYNC_RECV_FILE`, `TAG_SYNC_SEND_FILE` | `path` | `adb pull` 로 기기에서 꺼낸 파일, `adb push` 로 넣은 파일의 경로 [4][10] |
| `keyguard_dismiss_auth_attempt` | `TAG_KEYGUARD_DISMISS_AUTH_ATTEMPT` | `success`, `method_strength` | 잠금 화면 인증 시도. `method_strength` 는 강한 인증 방법이면 1 [4][14] |
| `keyguard_dismissed` | `TAG_KEYGUARD_DISMISSED` | 없음 | 잠금 해제. PIN·패턴·비밀번호·생체·신뢰할 수 있는 에이전트 어느 것으로 풀었든 남음 [4] |
| `keyguard_secured` | `TAG_KEYGUARD_SECURED` | 없음 | 기기가 잠김 [10] |
| `os_startup` | `TAG_OS_STARTUP` | `verified_boot_state`, `dm_verity_mode` | 부팅. 검증 부팅 상태는 `green`·`yellow`·`orange`, dm-verity 모드는 `enforcing`·`eio`·`disabled` [4][10] |
| `cert_authority_installed`, `cert_authority_removed` | `TAG_CERT_AUTHORITY_INSTALLED` 등 | `success`, `subject` | 신뢰할 수 있는 루트 인증서 설치·제거 [4][10] |
| `password_changed` | `TAG_PASSWORD_CHANGED` | `complexity`, `user_id` | 화면 잠금 비밀번호 변경 [4][10] |
| `bluetooth_connection` | `TAG_BLUETOOTH_CONNECTION` | `mac_address`, `success`, `reason` | Bluetooth 기기 연결 시도 [4][10] |

`SecurityLog` 의 Wi-Fi 태그 (`TAG_WIFI_CONNECTION`) 는 관리되는 Wi-Fi 네트워크 (managed WiFi network) 연결을 기록하고 BSSID 는 끝 두 옥텟만 남깁니다 [4]. 태그 목록 전체는 [4] 에, MVT 가 아는 이름과 번호는 [10] 에 있습니다. MVT 가 모르는 새 종류가 나오면 MVT 는 경고를 남기고 원래 값을 그대로 타임라인에 넣습니다 [10].

## 증거로서 의미

**증명하는 것**

`dns_event` 와 `connect_event` 로는 어느 시각에 어느 앱이 어떤 호스트 이름을 조회했고 어느 IP 의 몇 번 포트로 연결했는지 알 수 있습니다 [14]. 스파이웨어 조사에서는 이 호스트 이름과 IP 를 알려진 침해 지표 (Indicator of Compromise, IOC) 와 맞춰 보고, MVT 도 이 값과 패키지 이름을 지표와 비교합니다 [9]. `app_process_start` 에는 APK 의 SHA-256 이 들어 있어서 [4], 기기에서 이미 지워진 앱이라도 실행된 적이 있으면 그 해시로 알려진 악성 앱과 맞춰 볼 수 있습니다.

`adb_shell_cmd`·`adb_sync_*` 는 누군가 USB 디버깅으로 기기에 명령을 보내거나 파일을 넣고 뺀 기록이고, `package_installed` 는 앱이 설치된 시각을 남깁니다 [4]. `keyguard_dismiss_auth_attempt` 의 실패 기록이 이어지면 누군가 잠금을 풀려고 여러 번 시도한 기록이 됩니다 [4]. `os_startup` 의 검증 부팅 상태가 `orange` 이면 기기를 마음대로 고칠 수 있는 상태로 부팅한 기록입니다 [4].

로그가 기기 밖에 있어서 기기를 초기화해도 이미 올라간 기록은 남고, 12개월이 지나기 전에는 사용자도 Google 도 지울 수 없습니다 [1]. 보고서에는 "이 시각에 이 앱이 이 호스트를 조회하고 이 IP 의 443번 포트로 연결한 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

**증명하지 못하는 것**

연결 기록에는 목적지와 포트만 있고 주고받은 내용이나 양은 없습니다 [14]. 데이터를 얼마나 보냈는지는 [데이터 사용량 (netstats)](../network/netstats.md) 에서 따로 봅니다. 앱이 DNS-over-HTTPS 로 직접 이름을 풀면 DNS-over-HTTPS 서버를 찾는 처음 조회만 남고 그 뒤 조회는 남지 않습니다 [14]. 그래서 어떤 호스트의 `dns_event` 가 없다고 그 앱이 그 호스트에 접속하지 않았다고 판단하지 않습니다.

`package_installed` 에는 설치 출처가 없어서 Play 스토어에서 받았는지, 직접 APK 로 설치했는지, ADB 로 넣었는지 알 수 없습니다 [14]. 출처는 [설치 출처와 설치 시각](../app-usage/packages/install-source-time.md) 에서 확인합니다. `adb_shell_interactive` 는 대화형 셸을 열었다는 사실만 남기고, 셸 안에서 입력한 명령은 남지 않습니다 [4][14].

Wi-Fi 기록은 출처끼리 설명이 다릅니다. 사용자 도움말은 Wi-Fi 시작과 중지를 기록 대상으로 꼽지만 [1], iVerify 가 Android 16 Pixel 10 Pro 수집본을 분석한 글에는 Wi-Fi 네트워크 이력이 남지 않아 가짜 접속 지점에 붙었는지 알 수 없다고 나와 있습니다 [14]. 어느 네트워크에 접속했는지는 [와이파이 설정과 접속 기록 (WifiConfigStore)](../network/wifi.md) 에서 확인합니다. 전원 끄기도 `SecurityLog` 에는 `TAG_OS_SHUTDOWN` 태그가 있지만 [4], 같은 iVerify 수집본에는 전원을 끈 흔적이 남지 않았습니다 [14].

침입 로깅이 켜져 있지 않았던 기간에는 기록이 없습니다 [13]. 기록이 없는 기간을 두고 아무 일도 없었다고 쓰지 않습니다.

## 시각 해석

`event_time` 은 모두 Unix 기준 시각이라 UTC 로 읽지만, 이벤트 종류마다 단위가 다릅니다 [10][11].

| 필드 | 단위 | 만든 예시 값 | UTC |
|---|---|---|---|
| `dns_event.event_time`, `connect_event.event_time` | 밀리초 | `1788000000000` | 2026-08-29 10:40:00.000 |
| `security_event.event_time` | 나노초 | `1788000045123456789` | 2026-08-29 10:40:45.123 |
| `app_process_start.start_time` | 밀리초 (`System.currentTimeMillis()` 기준) | `1788000045100` | 2026-08-29 10:40:45.100 |

2026년 무렵의 값은 밀리초면 13자리, 나노초면 19자리라 자릿수로 단위를 구분할 수 있습니다. 나노초 값을 밀리초로 알고 바꾸면 먼 미래 날짜가 나오니, 변환 결과가 이상하면 단위부터 확인합니다. 한국 시간은 UTC 에 9시간을 더합니다. 변환 방법 전반은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

MVT 는 따로 시간대를 주지 않으면 UTC 로 출력하고, `--timezone` 을 주거나 AndroidQF 수집본의 `getprop.txt` 에 `persist.sys.timezone` 이 있으면 그 시간대의 현지 시각으로 바꿔 출력합니다 [9][12]. 이때 출력 값에는 시간대 표시가 붙지 않으니 [11], 보고서에 옮길 때 어느 시간대인지 함께 적습니다.

기록 시각은 이벤트가 일어난 시각이고, 서버에 올라간 시각이 아닙니다. 기기는 하루에 한 번 로그를 올려서 [13] 가장 최근 12~24시간의 활동은 내려받은 묶음에 아직 없을 수 있습니다 [14].

## 함정과 한계

첫째, 기능을 미리 켜 두어야 기록이 생깁니다 [13]. 고급 보호 모드를 켰어도 침입 로깅은 건너뛸 수 있으니 [2], `advanced_protection_mode` 가 `1` 이라는 사실만으로 침입 로깅 기록이 있다고 보지 않습니다.

둘째, 내려받은 로그에는 앱마다 조회한 호스트 이름과 연결한 IP 가 들어 있어 사생활 정보가 많습니다 [14]. 내려받아 복호화한 뒤의 보안은 전부 사용자가 책임지니 [1], 소유자에게 무엇이 담기는지 설명하고 동의를 받은 뒤 받고, 전달·보관 경로를 수집 기록에 남깁니다. 사용자는 12개월이 지나기 전에 로그를 지울 수 없다는 점도 [1] 동의 받을 때 알립니다.

셋째, 수집 과정이 기기에 흔적을 남깁니다. 로그를 내려받으면 `Download/Intrusion Logging` 폴더에 새 파일이 생기고 [7], AndroidQF 는 수집할 때 Google Play 서비스의 `IntrusionDetectionRetrievalActivity` 를 열어 소유자에게 내려받기를 요청합니다 [8]. 받은 시각과 방법을 수집 기록에 적어 원래 있던 파일과 구별합니다. ADB 로 수집하면 그 수집 자체가 `adb_shell_cmd` 로 기록될 수 있으니, 수집 시각 이후의 ADB 이벤트는 분석가 자신의 작업과 먼저 맞춰 봅니다 [4].

넷째, 하루 단위로 나뉜 파일의 기간이 겹치면 같은 이벤트가 여러 파일에 들어 있을 수 있고, MVT 는 처음 나온 것만 남기고 겹친 것을 지웁니다 [9]. 파일을 직접 합칠 때도 같은 이벤트를 두 번 세지 않게 합니다.

다섯째, 도구 버전을 확인합니다. MVT 2026.5.12 에서는 보안 이벤트가 실제 종류 대신 모두 `event_id` 로 표시됐고 [14], 2026년 6월 11일에 병합된 PR #815 에서 고쳤습니다 [15]. 명령 이름도 처음 소개된 `check-advanced-logs` [13] 에서 지금은 `check-intrusion-logs` 로 바뀌었습니다 [9]. 분석 보고서에 MVT 버전을 적습니다.

여섯째, 이벤트 양이 많습니다. Android 16 Pixel 10 Pro 에서 받은 수집본은 한 묶음에 약 9만 3천 건에서 60만 건 가까이였고, 가장 긴 것은 3주가 넘었습니다 [14]. 전체를 읽기보다 조사 기간과 의심 앱으로 먼저 좁힙니다.

## 직접 분석해 보기

### 텍스트로 한 번

로그는 JSON 텍스트라 헥스 대신 텍스트 도구로 따라갑니다.

1. 받은 파일의 해시를 먼저 기록하고 사본에서 작업합니다.
2. 파일마다 최상위 키별 줄 수를 셉니다. `security_event`, `dns_event`, `connect_event` 말고 다른 키가 있으면 새 이벤트 종류일 수 있으니 따로 적습니다.
3. 파일마다 가장 이른 `event_time` 과 가장 늦은 `event_time` 을 UTC 로 바꿔 로그가 덮는 기간을 적고, 기간 사이에 빈 구간이 있는지 봅니다.
4. 의심 앱의 패키지 이름으로 `dns_event` 와 `connect_event` 를 골라 호스트 이름과 IP 목록을 만들고 지표와 맞춰 봅니다.
5. 같은 패키지 이름의 `package_installed` 와 `app_process_start` 를 찾아 설치 시각, 첫 실행 시각, APK 해시를 적습니다.

아래는 `jq` 로 2단계와 4단계를 하는 예시입니다. 파일 이름과 패키지 이름은 만든 예시입니다.

```
jq -r 'keys[0]' il-example.txt | sort | uniq -c
jq -c 'select(.dns_event.package_name == "com.example.chat") | .dns_event | [.event_time, .hostname, .ip_addresses]' il-example.txt
date -u -d @1788000000
```

### 공개 도구로 한 번

AndroidQF 로 수집하면 기기가 고급 보호 모드를 지원할 때 침입 로그도 받을지 묻고, 받기로 하면 설정의 침입 로깅 화면을 열어 소유자가 기기에서 Download & decrypt 를 누르게 한 뒤 폴더의 파일을 수집본의 `intrusion_logs/` 아래로 가져옵니다 [7][8]. 고급 보호 모드가 꺼져 있으면 새로 받지 않고 폴더에 이미 있는 파일만 가져옵니다 [7].

```
mvt-android check-androidqf --output /path/to/results/ /path/to/androidqf-output/
mvt-android check-intrusion-logs --output /path/to/results/ /path/to/intrusion-logs/
```

`check-androidqf` 는 수집본에서 `intrusion_logs` 폴더를 찾으면 침입 로그 분석을 함께 돌리고 [12], 따로 받은 로그는 `check-intrusion-logs` 에 폴더나 `.zip` 을 넘겨 분석합니다 [9]. 결과는 `DnsEvent`, `ConnectEvent`, `SecurityEvent` 모듈별 JSON 과 타임라인 CSV 로 나오고, 지표와 맞으면 `CRITICAL` 경고가 붙습니다 [9]. 인증서 설치, 키 무결성 위반, 인증서 검증 실패, 초기화 실패, 암호 모듈 자체 시험 실패는 지표가 없어도 경고로 표시합니다 [10].

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [설치 출처와 설치 시각](../app-usage/packages/install-source-time.md) | `package_installed` 시각과 설치 출처 |
| [데이터 사용량 (netstats)](../network/netstats.md) | 연결 기록이 있는 시간대에 그 앱의 송수신량 |
| [USB 연결 기록 (USB)](../network/usb.md) | `adb_*` 이벤트 시각의 USB 연결 |
| [설치된 인증서 (User Certificates)](../credentials-security/user-certificates.md) | `cert_authority_installed` 의 `subject` 와 기기에 남은 인증서 |
| [이벤트 로그 버퍼 (events)](events-buffer.md) | 수집 직전 구간의 프로세스 시작 기록 |
| [기기 정보와 빌드 (build.prop·Build)](../system-account/device-build.md) | Android 버전과 `os_startup` 의 검증 부팅 상태 |
| [감시 앱 흔적 (Stalkerware)](../../03-techniques/analysis/malicious-app-triage/stalkerware.md) | 감시 앱 지표의 패키지 이름·도메인 |

수집 절차 전반은 [모바일 증거 확보 (Acquisition)](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서, 감시 앱 의심 사건의 조사 흐름은 [몰래 설치된 감시 앱 (Stalkerware)](../../04-scenarios/incident/stalkerware.md) 에서 다룹니다.

## 실습

본인 Google 계정으로 쓰는 시험용 Android 16 기기에서 침입 로깅을 켜고 하루 넘게 둔 뒤, 로그를 내려받아 아래 질문을 풀어 봅니다.

1. 받은 로그가 덮는 첫 시각과 마지막 시각은 UTC 로 언제이고, 내려받은 시각보다 얼마나 앞섭니까?
2. `adb shell` 로 명령 하나를 보낸 시각의 `adb_shell_cmd` 는 무엇이고, 대화형 셸을 열었을 때는 어떤 이벤트가 남습니까?
3. 시험 앱 하나를 설치하고 실행했을 때 `package_installed` 와 첫 `app_process_start` 의 시각 차이는 얼마이고, `sha256` 은 APK 파일의 해시와 같습니까?
4. Chrome 으로 사이트 하나를 열었을 때 그 호스트 이름의 `dns_event` 가 남습니까?

## 참고 문헌

1. Google — Log your Android device activity with Advanced Protection (Android Help) — https://support.google.com/android/answer/16927813?hl=en
2. Google — Improve device security with Advanced Protection for Android (Android Help) — https://support.google.com/android/answer/16339980?hl=en
3. Google — Android Show: New Android Security and Privacy Features in 2026 (2026-05-12) — https://blog.google/security/whats-new-in-android-security-privacy-2026/
4. Android Open Source Project — SecurityLog.java — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/app/admin/SecurityLog.java
5. Android Open Source Project — IntrusionDetectionEvent.java — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/security/intrusiondetection/IntrusionDetectionEvent.java
6. Android Open Source Project — NetworkLogSource.java, SecurityLogSource.java — https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/security/intrusiondetection/NetworkLogSource.java , https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/security/intrusiondetection/SecurityLogSource.java
7. AndroidQF — modules/intrusion_logs.go — https://raw.githubusercontent.com/mvt-project/androidqf/main/modules/intrusion_logs.go
8. AndroidQF — adb/adb.go — https://raw.githubusercontent.com/mvt-project/androidqf/main/adb/adb.go
9. MVT — Check Android Intrusion Logs (docs/android/intrusion_logs.md) — https://raw.githubusercontent.com/mvt-project/mvt/main/docs/android/intrusion_logs.md
10. MVT — modules/intrusion_logs/security_event.py, connect_event.py, dns_event.py — https://raw.githubusercontent.com/mvt-project/mvt/main/src/mvt/android/modules/intrusion_logs/security_event.py , https://raw.githubusercontent.com/mvt-project/mvt/main/src/mvt/android/modules/intrusion_logs/connect_event.py , https://raw.githubusercontent.com/mvt-project/mvt/main/src/mvt/android/modules/intrusion_logs/dns_event.py
11. MVT — modules/intrusion_logs/base.py — https://raw.githubusercontent.com/mvt-project/mvt/main/src/mvt/android/modules/intrusion_logs/base.py
12. MVT — cmd_check_androidqf.py — https://raw.githubusercontent.com/mvt-project/mvt/main/src/mvt/android/cmd_check_androidqf.py
13. Amnesty International Security Lab — Android Intrusion Logging as a new source of data for consensual forensic analysis (2026-05-12) — https://securitylab.amnesty.org/latest/2026/05/android-intrusion-logging-as-a-new-source-of-data-for-consensual-forensic-analysis/
14. David Gillies, Lorena Carthy-Wilmot — Android Intrusion Logs - A First Look, iVerify (2026-08-04) — https://www.iverify.com/blog/android-intrusion-logging-forensics-analysis
15. MVT — Fix intrusion log event ID parsing (PR #815) — https://github.com/mvt-project/mvt/pull/815
