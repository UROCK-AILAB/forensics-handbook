---
title: "스마트폰으로 옮겼나"
parent: "자료를 밖으로 빼돌렸나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 3600
---

# 스마트폰으로 옮겼나 (MTP·Phone Link)

스마트폰이 PC 와 자료를 주고받는 길은 크게 두 가지입니다. 하나는 USB 선으로 연결해 MTP (Media Transfer Protocol) 로 붙는 길입니다. 다른 하나는 휴대폰과 연결 (Phone Link) 앱으로 휴대폰과 PC 를 연동하는 길입니다. 이 페이지는 두 길이 PC 에 남기는 흔적과, 그 흔적으로 말할 수 있는 범위를 다룹니다.

## 조사 질문

- 이 PC 에 스마트폰을 USB 로 연결했습니까? 어느 휴대폰이고 언제입니까?
- Phone Link 로 휴대폰과 연동했습니까? PC 에 무엇이 남았습니까?
- 이 기록으로 PC 의 파일을 휴대폰으로 옮겼다고 말할 수 있습니까?

## 먼저 확인할 것

| 확인할 것 | 이유 |
|---|---|
| USBSTOR 만 보지 않기 | MTP 로 붙는 휴대폰은 USBSTOR 가 아닌 다른 위치에 남습니다([USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md)). |
| 앱 버전 | 아래 Phone Link DB 위치는 2019년 연구 기준입니다. 분석 대상 PC 에 설치된 Phone Link 판을 먼저 봅니다([스토어 앱 설치 목록](../../../02-artifacts/system-account/appx-staterepository.md)). |
| 시간대 | 레지스트리 장치 속성 시각과 이벤트 시각을 같은 기준으로 맞춥니다([시간대 설정](../../../02-artifacts/system-account/time-zone.md)). |
| 사용자 | 휴대폰 연결 기록이 남는 SYSTEM·SOFTWARE 하이브에는 사용자 정보가 없습니다. Phone Link 폴더는 사용자 프로필 안에 있으므로 사용자별로 봅니다. |
| 수집 범위 | SYSTEM·SOFTWARE 하이브, WPD-MTPClassDriver/Operational·Kernel-PnP/Configuration 이벤트 로그, 사용자마다 `%LocalAppData%\Packages\Microsoft.YourPhone_8wekyb3d8bbwe` 폴더 전체를 확보합니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | SYSTEM `Enum\USB` 의 휴대폰 키 | 휴대폰의 VID·PID, 설치·연결·해제 시각 | [USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md) |
| 2 | SOFTWARE `Windows Portable Devices\Devices` | 사용자가 휴대폰에 붙인 기기 이름 | [USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md) |
| 3 | WPD-MTPClassDriver/Operational 로그 | MTP 드라이버가 시작한 시각 | 이 페이지 아래 |
| 4 | Kernel-PnP/Configuration 로그 | 장치를 설정·시작한 시각 | [외부 장치 연결 이벤트](../../../02-artifacts/event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) |
| 5 | 바로가기 파일·점프리스트·셸백 | 연결 무렵 PC 에서 연 원본 파일, 탐색한 폴더 | [바로가기 파일](../../../02-artifacts/file-folder-usage/lnk.md), [셸백](../../../02-artifacts/file-folder-usage/shellbags/index.md) |
| 6 | Phone Link 폴더 | 연동한 휴대폰의 연락처·메시지·알림·사진·통화 | [휴대폰과 연결](../../../02-artifacts/messengers/phone-link.md) |

## MTP 로 연결한 휴대폰

### 레지스트리

아래 예는 Windows 11 Home 25H2(빌드 26200.9457)에 삼성 휴대폰을 MTP 로 연결한 경우입니다. 다른 제조사 휴대폰이나 다른 빌드에서는 다를 수 있습니다.

삼성 휴대폰(`VID_04E8&PID_6860`)은 `Enum\USBSTOR` 에 없고, SYSTEM 하이브 `Enum\USB\VID_04E8&PID_6860\<인스턴스>` 에 있습니다. 이 인스턴스 키에도 `Properties\{83da6326-97a6-4088-9453-a1923f573b29}` 아래 0064·0065·0066·0067 이 모두 있습니다. 그래서 USB 메모리와 같은 방법으로 설치·연결·해제 시각을 읽습니다. 네 값의 뜻은 [USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md) 에 있습니다.

인스턴스 키의 `Service` 값은 제조사가 만든 드라이버 이름입니다. 삼성 휴대폰은 `dg_ssudbus` 이고, 드라이버 이름은 휴대폰 제조사마다 다릅니다.

SOFTWARE 하이브 `Microsoft\Windows Portable Devices\Devices` 에는 장치마다 하위 키가 있습니다.

| 장치 | 하위 키 이름 모양 | FriendlyName 값 |
|---|---|---|
| MTP 휴대폰 | `USB#VID_04E8&PID_6860&MS_COMP_MTP&SAMSUNG_ANDROID#<인스턴스>` | 사용자가 휴대폰에서 정한 기기 이름 (예: "○○의 S25 Edge") |
| USB 메모리 | `SWD#WPDBUSENUM#_??_USBSTOR#DISK&VEN_…` | `D:\` 같은 드라이브 문자 |

휴대폰 키 이름에는 VID·PID 와 `MS_COMP_MTP` 가 함께 들어 있어서 이 글자로 MTP 장치를 골라냅니다. 키 이름 끝의 인스턴스 부분은 `Enum\USB` 의 인스턴스 키 이름과 맞춰 봅니다.

기기 이름에 사람 이름이 들어 있을 수 있어 사용자를 특정하는 재료가 되지만, 사용자가 휴대폰에서 이름을 바꿀 수 있으므로 이름만으로 휴대폰 주인을 단정하지 않습니다.

### WPD-MTPClassDriver/Operational 로그

`Microsoft-Windows-WPD-MTPClassDriver/Operational` 로그에는 1000~1006 이벤트가 남습니다. 이 로그가 기본으로 켜져 있는지, 어느 Windows 버전부터 있는지는 공개 문서에 나와 있지 않으므로, 분석 대상 PC 에 로그가 있는지부터 봅니다.

| ID | 메시지 |
|---|---|
| 1000 | "MTP Driver started successfully." |
| 1001 | "Device will enter the suspend state if idle for 30 seconds." |
| 1002 | 유휴 (idle) 상태에 들어갔다는 기록 |
| 1003 | 유휴 상태에서 돌아왔다는 기록 |
| 1006 | "Driver has failed to start, HRESULT …" |

1000 에는 EventData 필드가 없어서 어느 휴대폰이 붙었는지 이 이벤트만으로는 알 수 없습니다. 기록한 계정은 S-1-5-19 (LOCAL SERVICE) 이고, 이 계정은 사용자를 가리키지 않습니다. 그래서 이 로그로는 "그 시각에 MTP 장치가 붙었다" 까지만 알 수 있으며, 어느 장치인지는 `Enum\USB` 의 장치 속성 시각, Kernel-PnP/Configuration 이벤트와 시각을 맞춰 정합니다.

### 파일을 옮겼나

MTP 로 복사한 파일 목록이 PC 쪽에 따로 남는다는 공개 자료는 없습니다. 휴대폰 안 폴더를 탐색기로 연 기록이 셸백에 어떤 모양으로 남는지도 정리된 자료가 없으므로, 셸백에서 휴대폰 기기 이름이 든 경로가 있는지 찾아봅니다. 그래서 PC 쪽 흔적은 연결 구간과 그 구간에 연 원본 파일까지만 이을 수 있습니다.

## Phone Link

Phone Link 의 옛 이름은 Your Phone 입니다. 앱 데이터 폴더의 일반 구조는 [UWP 앱 데이터 구조](../../../01-foundations/app-mail-data/packages-settings-dat.md) 에서, 이 앱의 흔적은 [휴대폰과 연결](../../../02-artifacts/messengers/phone-link.md) 에서 자세히 다룹니다.

### 2019년 연구 기준 위치와 DB

Windows 10 1809·1903·빌드 18932, Your Phone 1.19041.481.0·1.19061.410.0 에서 DB 위치는 아래와 같습니다[1].

```
%LocalAppData%\Packages\Microsoft.YourPhone_8wekyb3d8bbwe\LocalCache\Indexed\<GUID>\System\Database\
```

| DB | 들어 있는 것 |
|---|---|
| Phone.db | 연락처, SMS |
| Notifications.db | 휴대폰에서 온 알림 |
| Settings.db | 휴대폰에 설치된 앱, 앱 버전·아이콘, 알림을 켰는지 |
| Photos.db | 동기화된 사진의 시각·크기·휴대폰 속 위치, 썸네일, 원본 이미지 |
| calling.db | 통화 기록 |

(표는 [1])

- 동기화된 사진은 두 곳에 남습니다[1]. 하나는 Photos.db 안의 원본 이미지 blob 입니다. 다른 하나는 파일 시스템의 `User\<휴대폰 이름>\Recent Photos` 폴더입니다.
- .heic 사진도 동기화되지만 앱 화면에는 보이지 않습니다[1]. 앱 화면으로 사진 목록을 정하지 말고 DB 와 폴더를 직접 봅니다.
- 이 DB 들에 든 것은 휴대폰에서 PC 로 온 자료입니다. PC 의 파일을 휴대폰으로 보낸(끌어 놓은) 기록이 어디 남는지는 실제 기기에서 확인해야 합니다.

### 최신 판

Phone Link 패키지 1.26072.255.0 에서는 패키지 폴더에 `LocalCache\Indexed` 가 없을 수 있습니다. 이때 `LocalCache` 에는 `DeviceMetadataStorage.json`, `PlatformEncryptedKeyStorage.json` 과 `Local`·`Roaming` 폴더만 있습니다. 휴대폰과 연동한 적이 없어서인지, 판이 바뀌어 위치가 달라졌는지는 알려져 있지 않습니다.

최신 Windows 11 에는 `MicrosoftWindows.CrossDevice` 패키지(1.26072.116.0)도 함께 있을 수 있습니다. 이 패키지가 휴대폰 연동 기록을 어디에 남기는지는 공개된 자료가 없습니다. 그래서 최신 판에 2019년 경로가 그대로 있다고 가정하지 않고, 두 패키지 폴더를 통째로 확보해 둡니다.

## 분석 흐름

1. SYSTEM 하이브 `Enum\USB` 에서 USBSTOR 에 없는 장치 가운데 휴대폰을 찾습니다. VID 로 제조사를 확인하고, `Service` 값으로 제조사 드라이버를 확인합니다.
2. 그 인스턴스의 0064~0067 을 읽어 처음 설치·마지막 연결·마지막 해제 시각을 정리합니다.
3. SOFTWARE 하이브 WPD 장치 목록에서 `MS_COMP_MTP` 가 든 키를 찾습니다. 인스턴스 부분으로 1번 키와 잇고 FriendlyName 을 기록합니다.
4. WPD-MTPClassDriver/Operational 의 1000 시각을 모두 뽑습니다. Kernel-PnP/Configuration 이벤트와 장치 속성 시각에 맞춰 휴대폰마다 연결 구간표를 만듭니다.
5. 연결 구간 안에 PC 의 원본 파일을 연 흔적이 있는지 바로가기 파일·점프리스트·셸백에서 찾습니다.
6. 사용자마다 Phone Link 패키지 폴더를 봅니다. `LocalCache\Indexed` 가 있으면 DB 를 사본으로 열어 휴대폰 이름과 DB 에 남은 시각을 확인합니다.
7. 블루투스로 짝지은 장치 목록에 같은 휴대폰이 있는지 [블루투스 장치](../../../02-artifacts/external-devices/bthport.md) 에서 확인합니다.
8. 모든 시각을 UTC 로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리합니다.

## 흔한 오판

1. **USBSTOR 에 없으니 휴대폰을 연결하지 않았다고 봅니다.** MTP 휴대폰은 `Enum\USB` 와 WPD 장치 목록에 남습니다.
2. **MTPClassDriver 1000 을 특정 휴대폰의 연결로 봅니다.** 이 이벤트에는 장치를 가리키는 필드가 없습니다. 다른 기록과 시각을 맞춘 뒤에만 장치를 적습니다.
3. **기기 이름 속 사람 이름을 주인으로 단정합니다.** 기기 이름은 사용자가 바꿀 수 있습니다.
4. **연결 기록을 파일 복사 증거로 씁니다.** 연결 기록은 휴대폰이 붙었다는 것만 보여 줍니다.
5. **Phone Link 의 사진을 PC 에서 보낸 파일로 봅니다.** Photos.db 에는 휴대폰 속 위치가 적힌 동기화 사진이 들어 있습니다[1]. 방향은 휴대폰에서 PC 쪽입니다.
6. **Phone Link DB 가 없으니 연동하지 않았다고 봅니다.** 최신 판은 DB 위치가 다를 수 있습니다. 없다는 사실은 "2019년 연구 기준 위치에 없다" 로만 적습니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 자기 휴대폰으로 회사 파일을 옮겼습니다."
- 쓸 문장: "SYSTEM 하이브 `Enum\USB` 에 VID_04E8·PID_6860 인 장치 기록이 있고, 마지막 연결 시각은 ○○(UTC) 입니다. SOFTWARE 하이브 WPD 장치 목록의 같은 장치 키에는 기기 이름 '○○' 이 적혀 있습니다. WPD-MTPClassDriver/Operational 로그에는 ○○(UTC) 에 MTP 드라이버가 시작했다는 1000 이벤트가 있습니다. 이 기록은 그 시각 무렵 MTP 장치가 이 PC 에 연결됐음을 보여 줍니다. 휴대폰으로 파일을 옮겼는지는 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [USB 로 무엇을 가져갔나 (USB)](usb.md) — 저장장치로 붙는 USB 메모리의 조사 순서입니다.
- [USB 저장장치 흔적](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md) — `Enum\USB`·장치 속성·WPD 키의 구조입니다.
- [외부 장치 연결 이벤트](../../../02-artifacts/event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) — Kernel-PnP 이벤트로 연결 시각을 찾습니다.
- [휴대폰과 연결](../../../02-artifacts/messengers/phone-link.md) — Phone Link DB 의 구조입니다.
- [블루투스 장치](../../../02-artifacts/external-devices/bthport.md) — 블루투스로 짝지은 장치 목록입니다.
- [스마트폰 백업 파일](../../../02-artifacts/external-devices/itunes-smart-switch-backup.md) — PC 에 남은 휴대폰 백업입니다.
- [메신저로 파일을 보냈나 (Messenger)](messenger.md) — 메신저 PC 판으로 파일을 보낸 경우입니다.
- [그 시각에 PC 를 쓴 사람이 누구인가](../../activity/user-attribution.md) — 기기 이름을 사용자 특정에 쓸 때 함께 봅니다.

## 참고 문헌

1. Costas Katsavounidis (kacos2000), "YourPhone" 연구 readme (2019, Windows 10 1809·1903) — https://raw.githubusercontent.com/kacos2000/Win10/master/YourPhone/readme.md
