---
title: "PC 연결로"
parent: "자료를 밖으로 보냈나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 1730
---

# PC 연결로 (USB·PC)

기기를 PC 에 연결해 자료를 옮겼는지 확인하는 순서를 정리합니다. USB 파일 전송(MTP)으로 PC 가 무엇을 복사해 갔는지 기기에 남는 기록은 공개된 분석 자료가 없습니다. 그래서 이 페이지는 "어떤 PC 와 연결된 적이 있나" 를 보여 주는 기록들을 모아, 연결 시점과 기기 안의 파일 작업을 맞춰 보는 흐름으로 씁니다. 유출 경로 전체의 길잡이는 [자료를 밖으로 보냈나 (Data Exfiltration)](index.md) 허브에 있습니다.

## 조사 질문

이 기기가 조사 기간에 PC 와 연결됐는지, 연결됐다면 어떤 PC 였고 그 무렵 기기에서 어떤 파일 작업이 있었는지 묻습니다. 연결 경로는 USB 선을 이용한 파일 전송, USB 디버깅(ADB), Windows 의 휴대폰과 연결(Phone Link), 삼성 DeX 처럼 여러 가지이고 경로마다 남는 흔적이 다릅니다.

## 먼저 확인할 것

PC 쪽 기록이 있는지부터 봅니다. PC 가 기기를 어떻게 기억하는지는 PC 운영체제의 기록이라서 이 핸드북 범위 밖이지만, 기기 쪽 기록만으로는 복사 여부를 말하기 어려워서 PC 를 함께 조사할 수 있는지에 따라 결론을 어디까지 낼 수 있는지가 달라집니다.

기기 쪽에서는 수집 범위를 확인합니다. 아래 기록 가운데 ADB 인증 파일, Phone Link DB, 내 파일 작업 기록은 시스템 폴더나 앱 데이터 폴더에 있어서 수집본에 그 폴더가 들어 있어야 합니다. 설정 키와 logcat 은 adb 일반 셸 권한으로 읽을 수 있습니다. 연결 시각을 현지 시각으로 옮기려면 기기 시간대가 필요하고, 이는 [시간대와 시각 설정 (Time Zone)](../../../02-artifacts/system-account/time-zone.md) 페이지에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | ADB 인증 기록 | 인증해 둔 PC 의 키와 이름, 마지막 연결 시각 | 아래 절 |
| 2 | Phone Link 기록 | 짝지은 Windows 계정, 콘텐츠 접근 이벤트 | 아래 절 |
| 3 | 설정 키(ADB·USB·DeX) | 관련 기능을 볼 수 있는 키 | [설정 값 (Settings Global·Secure·System)](../../../02-artifacts/system-account/settings.md) |
| 4 | USB 연결 기록 | USB 연결 흔적 | [USB 연결 기록 (USB)](../../../02-artifacts/network/usb.md) |
| 5 | 삼성 내 파일 작업 기록 | 복사·이동 같은 파일 작업 | 아래 절 |
| 6 | logcat | 최근 시스템 로그 | [logcat (logcat)](../../../02-artifacts/logs/logcat.md) |

## ADB 인증 기록

USB 디버깅을 허용한 PC 는 기기에 공개 키가 남습니다. 이 파일은 `*/misc/adb/adb_temp_keys.xml` 패턴으로 찾고, 요즘 버전에서는 ABX(바이너리 XML), 예전 버전에서는 일반 XML 입니다 [2]. 어느 버전부터 ABX 로 바뀌었는지는 실제 기기에서 확인하고, ABX 읽는 법은 [안드로이드 바이너리 XML (ABX)](../../../01-foundations/data-formats/abx.md) 페이지에 있습니다.

파일 안에는 `adbKey` 요소가 키마다 하나씩 있습니다 [2]. `key` 속성은 PC 공개 키 뒤에 공백과 `user@hostname` 모양의 주석이 붙은 값이고, 이 주석은 PC 의 adb 가 적습니다 [2]. 시스템도 이 값을 공백으로 나눈 두 번째 토큰을 연결한 PC 이름으로 보여 줍니다(AOSP 의 AdbDebuggingManager.getPairedDevices) [2]. `lastConnection` 속성은 마지막 연결 시각이고 유닉스 밀리초입니다 [2].

```xml
<!-- ALEAPP 설명의 요소·속성 이름으로 만든 예시(일반 XML 로 풀었을 때의 모양). 값은 지어낸 것입니다. -->
<adbKey key="QAAAA...(공개 키)... analyst@WORKPC" lastConnection="1700000000000" />
```

ALEAPP 시험에서 키 23개 가운데 20개에 이름 주석이 있었고, 그중 2개는 user 부분이 비어 있었습니다 [2]. 이름 주석은 PC 쪽에서 정한 값이라서 PC 이름을 확정하는 근거로는 약하고, PC 를 확보했다면 PC 에 남은 adb 공개 키와 이 값을 직접 맞춰 봅니다.

adbd 가 실제 인증에 쓰는 파일은 시각이 없는 일반 텍스트 목록 `adb_keys`(data/misc/adb/adb_keys)이고, `adb_temp_keys.xml` 은 오래 쓰지 않은 키를 정리하고 무선 디버깅 접속 지점을 관리하는 데 씁니다 [2]. 한 행은 "그 PC 의 개인 키를 가진 호스트를 인증해 두었다" 는 뜻이지 파일이 옮겨졌다는 뜻이 아닙니다 [2]. ALEAPP 시험 이미지 가운데 삼성 기기 samsungs20_a13·samsunga53_a14·s20fe_a13 에서는 1행씩 나왔습니다 [2]. ALEAPP 에는 adb_hosts.py 모듈도 있습니다 [1].

global 설정 표에는 `adb_enabled`, `adb_wifi_enabled`, `adb_allowed_connection_time` 키가 있고, 삼성 기기의 secure 표에는 `rampart_blocked_adb_cmd`, `rampart_snapshot_adb_enabled`, `rampart_snapshot_adb_wifi_enabled` 키가 있습니다. `adb_allowed_connection_time` 의 단위와 rampart 로 시작하는 키의 뜻은 실제 기기에서 확인합니다.

## 휴대폰과 연결(Phone Link)

Microsoft 의 휴대폰과 연결은 기기 쪽 앱 com.microsoft.appmanager 로 휴대폰을 Windows PC 와 짝짓습니다 [3]. 계정은 `*/com.microsoft.appmanager/files/datastore/ACCOUNT_NAME.preferences_pb` 에 Jetpack DataStore protobuf 로 들어 있고, 키는 "계정이름:종류", 값은 종류와 username 이 든 JSON 입니다 [3]. 이 파일에는 시각이 없고, 지금도 PC 가 연결돼 있다는 뜻도 아닙니다 [3]. 옆 파일 `ACCOUNT_DATA_NAME.preferences_pb` 에는 개인 키나 신원 토큰 같은 자격 증명 성격의 속성 이름이 있어서 ALEAPP 는 값을 보여 주지 않습니다 [3].

이벤트는 `*/com.microsoft.appmanager/databases/eventstore*` 의 `content_access_event` 표에 있고, 열은 `uid`, `start_time`(유닉스 밀리초), `duration`(단위 기록 없음), `content_type`, `access_was_useful` 입니다 [3]. `content_type` 코드의 뜻은 출처가 없고, DB 파일과 WAL 파일의 행이 서로 달라 둘 다 읽어야 합니다 [3]. 같은 eventstore 에 FcmNotificationEvent, agent_service_event 표도 있습니다 [3]. `PhoneAppsDatabase` 의 `phoneAppsTable` 에는 `lastUpdatedTime`(밀리초), `appName`, `appPackageName`, `appVersion`, `favoriteRank`, `id` 가 있고, 같은 DB 의 browserHistoryTable 과 recentAppsTable 은 시험 이미지에서 비어 있었습니다 [3]. Phone Link 로 파일을 실제로 옮겼는지 보여 주는 표는 공개된 분석 자료가 없습니다.

## USB 파일 전송과 삼성 기능

USB 선으로 파일을 옮기는 MTP 연결에 대해서는, PC 가 복사해 간 파일 목록이나 USB 연결 시각을 기기가 어디에 남기는지는 실제 데이터로 확인해야 합니다. USB 연결 흔적은 [USB 연결 기록 (USB)](../../../02-artifacts/network/usb.md) 페이지에서 다룹니다. 관련 설정 키 이름은 다음과 같고, 값의 뜻은 실제 데이터로 확인합니다.

| 표 | 키 | 기능 |
|---|---|---|
| global | `usb_mass_storage_enabled` | USB |
| system | `enable_mtp_settings` | USB |
| secure | `block_usb_lock`, `usb_audio_automatic_routing_disabled` | USB |
| global | `wireless_dex_last_wireless_connection_type`, `wireless_dex_remembered_device_address_list`, `wireless_dex_uuid_tv` | 삼성 DeX |
| system | `dex_on_external_display` 등 dex_ 로 시작하는 키 | 삼성 DeX |
| global | `smartswitch_transfer_completed`, `smartswitch_transfer_start_in_oobe` | Smart Switch |
| system | `hwrs_storageshare_running`, `hwrs_storageshare_setting`, `hwrs_camerashare_setting` | 이름으로 보면 저장소·카메라 공유 |

logcat 에는 main, system, crash, kernel 버퍼가 있고 줄마다 연도 없는 `MM-DD HH:MM:SS.mmm` 시각이 붙습니다. USB 연결과 관련된 로그 태그는 판마다 다를 수 있어 실제 기기에서 확인하고, logcat 의 보관 범위와 읽는 법은 [logcat (logcat)](../../../02-artifacts/logs/logcat.md) 페이지에 있습니다.

## 삼성 내 파일 작업 기록

삼성 내 파일(My Files) 앱은 `*/com.sec.android.app.myfiles/databases/OperationHistory.db*` 의 `operation_history` 표에 파일 작업을 적습니다 [4]. 열은 순서대로 계정, 경로, 작업 날짜, 작업 종류, 항목 수, 폴더 수, 페이지 종류입니다 [4]. 날짜가 어느 시간대로 적힌 값인지는 알려져 있지 않아 다른 기록과 맞춰 봅니다 [4].

경로는 글자를 바꿔 치는 방식으로 가려져 있습니다. ALEAPP 의 풀이표에는 출처가 없고 Android 10~12 에서만 맞는다고 적혀 있어서 모듈도 이 버전에서만 경로를 풀며, Android 13·14 에서는 `#G$` 로 시작하는 값이 나와 풀지 못합니다 [4]. 경로가 보안 폴더 사용자 폴더(`/user/1xx` 모양, 보통 150)면 그 번호를 사용자로 적습니다 [4]. ALEAPP 시험 이미지(Android 14·15)에서는 0행이었습니다 [4]. 복사·이동 대상이 USB 저장 장치였는지는 실제 데이터로 확인합니다.

## 분석 흐름

1. 수집본에 ADB 인증 파일, Phone Link 앱 데이터, 내 파일 DB 가 들어 있는지 확인합니다.
2. `adb_temp_keys.xml` 에서 키마다 이름 주석과 `lastConnection` 을 뽑고, 조사 기간에 걸리는 키를 표시합니다.
3. Phone Link 계정 파일로 짝지은 Windows 계정을 적고, `content_access_event` 의 `start_time` 을 시간순으로 늘어놓습니다.
4. 내 파일 작업 기록과 공용 저장 공간의 파일 시각을 연결 시각 주변에서 찾아, 옮길 파일을 모으거나 이동한 작업이 있었는지 봅니다.
5. PC 를 확보했다면 PC 쪽 기록(adb 키, 장치 연결 기록)과 기기 쪽 시각을 맞춥니다.

## 흔한 오판

ADB 인증 키가 있다는 사실을 "그 PC 로 파일을 빼냈다" 로 읽지 않습니다. 키는 인증을 허락해 둔 기록이고, `lastConnection` 도 마지막으로 연결한 시각 하나만 남습니다 [2]. 이름 주석도 기기가 아니라 PC 쪽 adb 가 적은 값입니다 [2].

Phone Link 계정 파일을 지금 연결된 상태로 읽지 않습니다. 이 파일에는 시각이 없습니다 [3].

MTP 연결 흔적이 없다는 사실로 PC 연결이 없었다고 결론 내리지 않습니다. 기기가 MTP 복사 목록을 남기는지부터 공개된 분석 자료가 없습니다.

## 보고서 문장 예

- "`adb_temp_keys.xml` 에 이름 주석이 (주석 값)인 공개 키가 있고, 이 키의 `lastConnection` 은 (현지 시각)입니다. 이 기록은 해당 키를 가진 PC 를 USB 디버깅 대상으로 인증해 둔 적이 있다는 뜻이며, 파일을 옮겼는지는 이 기록만으로 알 수 없습니다."
- "Phone Link 앱의 `content_access_event` 표에 (시각)부터 (시각)까지 이벤트가 (행 수)건 있습니다. `content_type` 코드의 뜻은 공개 자료로 확인되지 않았습니다."

## 함께 볼 페이지

- [USB 연결 기록 (USB)](../../../02-artifacts/network/usb.md)
- [공용 저장 공간 (Shared Storage·/sdcard)](../../../01-foundations/storage/shared-storage.md)
- [보안 폴더와 작업 프로필 (Secure Folder·Work Profile)](../../../01-foundations/security-model/secure-folder-work-profile.md)
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)
- 같은 허브의 다른 경로: [메신저로 (Messenger)](messenger.md), [클라우드로 (Cloud)](cloud.md), [메일로 (Email)](email.md), [근거리 공유로 (Quick Share·Bluetooth)](nearby-share.md)

## 참고 문헌

1. ALEAPP scripts/artifacts 폴더 목록 — GitHub API, https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
2. adbAuthorizations.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/adbAuthorizations.py
3. phoneLink.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/phoneLink.py
4. smyfilesOpHistory.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/smyfilesOpHistory.py
