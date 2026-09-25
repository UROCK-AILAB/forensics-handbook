---
title: "에어드롭"
parent: "아티팩트 · 네트워크·연결"
nav_order: 700
---

# 에어드롭 (AirDrop)

## 한 줄 요약

에어드롭은 가까운 Apple 기기끼리 저전력 블루투스(BLE)로 서로를 찾고 Wi-Fi 로 직접 파일을 주고받는 기능입니다. 기기에는 에어드롭 식별자·받기 제한 설정·받은 사진의 가져오기 정보 같은 흔적이 남지만, 로컬 백업에는 전송 이력이라고 이름이 분명한 파일이 없어서 여러 기록을 이어 붙여 판단합니다.

## 무엇을 기록하나 · 왜 생기나

보내는 기기는 BLE 로 에어드롭 신호를 내보내고, 이 신호에는 사용자의 짧은 신원 해시(AirDrop short identity hash)가 들어 있습니다 [1]. 짧은 신원 해시는 사용자 Apple 계정에 연결된 이메일 주소와 전화번호로 만들고, 확인 단계에서는 긴 신원 해시를 씁니다 [1]. 전송은 인터넷이나 공유기(AP) 없이 기기끼리 Wi-Fi 로 직접 하고, 보내는 기기는 받는 기기와 TLS 암호화 연결을 맺으며 양쪽이 iCloud 신원 인증서를 주고받습니다 [1].

받는 쪽 설정에 따라 응답이 달라집니다. "연락처만" 모드에서는 신원 해시가 연락처와 맞을 때만 받는 기기가 응답하고, "모든 사람" 모드에서는 맞지 않아도 응답합니다 [1]. 받는 기기는 신원이 확인된 경우에만 보낸 사람의 이름과 사진을 보여 주고, 확인되지 않으면 실루엣 아이콘을 보여 줍니다 [1]. 받기 설정은 "수신 끔", "연락처만", "10분 동안 모든 사람" 세 가지입니다 [2].

Apple 공식 문서는 기기에 어떤 기록이 남는지 [1], 받은 항목이 어디에 저장되는지 [2] 설명하지 않습니다. 그래서 여기서는 로컬 백업에서 에어드롭과 이름이 이어지는 설정 파일·도메인·사진 DB 칸을 정리합니다.

## 위치와 버전별 차이

### 로컬 백업 안의 위치

| 도메인 :: 상대 경로 | 들어 있는 것 |
|---|---|
| `HomeDomain :: Library/Preferences/com.apple.sharingd.plist` | 에어드롭 식별자·계정·해시 관리 키(아래 구조) |
| `HomeDomain :: Library/Preferences/com.apple.Sharing.plist` | `hasDoneGenuineDeviceCheck` 키 |
| `AppDomain-com.apple.SharingViewService :: Library/Preferences/com.apple.SharingViewService.plist` | `PASAnalyticsUUIDValueKey`, `PASAnalyticsUUIDDateKey`, `PASAnalyticsDefaultsKey` 키 |
| `SysSharedContainerDomain-systemgroup.com.apple.configurationprofiles :: Library/ConfigurationProfiles/UserSettings.plist` | `restrictedBool` 아래 `allowAirDrop` 키 |
| `CameraRollDomain :: Media/PhotoData/Photos.sqlite` | 가져오기 정보 칸(아래 구조) |

위 표는 iOS 27.0 기준입니다. 이 밖에 `AppDomain-com.apple.Sharing.AirDropUI`, `AppDomainGroup-group.com.apple.sharingd`, `AppDomainPlugin-com.apple.Sharing.AirDrop`, `AppDomainPlugin-com.apple.Sharing.AirDropAlertUI`, `AppDomainPlugin-com.apple.AirDropSettingsIntents` 도메인도 에어드롭과 이름이 이어집니다. 백업 도메인 이름을 읽는 법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.

### 버전별 차이

| iOS | 달라지는 점 | 근거 |
|---|---|---|
| 16.2 이상 | "10분 동안 모든 사람" 설정이 10분 뒤 바뀜 | [2] |
| 17 이상(두 기기 모두) | 기기를 가까이 대어 에어드롭으로 공유 가능 | [2] |
| 27.0 | 위 표의 파일·키·칸 이름 | |

iOS 15 ~ 18 사이에 `com.apple.sharingd.plist` 키나 사진 DB 칸 이름이 어떻게 바뀌었는지는 공개 자료가 없어서 검체에서 확인합니다.

## 구조

### com.apple.sharingd.plist

키를 이름에 따라 묶으면 다음과 같습니다.

| 묶음 | 키 |
|---|---|
| 에어드롭 식별자 | `AirDropID`, `SDAirDropIDMSServiceAccountAltDSID`, `SDAirDropIDMSServiceContactsHistoryToken` |
| 계정 | `AppleIDAccount`, `AppleIDAgentMetaInfo`, `CurrentPseudonym` |
| 해시 관리 | `HashManager-StoredDatabaseVersionKey`, `HashManager-LastUpdatedDateKey`, `HashManager-LastDeviceIDHashKey`, `HashManager-LastRebuiltDateKey`, `HashManager-LastConsumedHistoryTokenKey` |
| 공유 시트 | `UIActivityCategoryShare`, `UIActivityCategoryAction`, `SFCollaborationUserDefaults.com.apple.MobileSMS` |
| 그 밖 | `StreamID`, `expireEscrowTokens` 등 |

`HashManager-LastUpdatedDateKey` 와 `HashManager-LastRebuiltDateKey` 는 날짜형 값입니다. 받기 모드(연락처만·모든 사람)라고 이름이 분명한 키는 없습니다. 그래서 이 파일만 보고 수집 당시 받기 모드를 말할 수 없습니다. 각 키의 뜻을 설명한 공개 자료는 없고, `AirDropID` 가 보안 문서의 신원 해시와 같은 값인지도 알려져 있지 않습니다.

### 기기 관리 제한

구성 프로파일 영역의 `UserSettings.plist` 에는 `restrictedBool` 아래 `allowAirDrop` 키가 있습니다. 이름으로 보아 기기 관리 쪽에서 에어드롭을 허용하는지 담는 값입니다. 이 파일 전체의 읽는 법은 [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md) 에서 다룹니다.

### 사진 DB 의 가져오기 칸

`Photos.sqlite` 의 `ZADDITIONALASSETATTRIBUTES` 표에 `ZIMPORTEDBY` 칸이 있고, `ZCLOUDMASTER` 표에 `ZIMPORTEDBY`, `ZIMPORTEDBYBUNDLEIDENTIFIER`, `ZIMPORTEDBYDISPLAYNAME`, `ZIMPORTDATE` 칸이 있습니다. 이름으로 보아 사진을 어떤 경로·앱으로 가져왔는지 담는 칸이지만, 에어드롭으로 받은 사진이 `ZIMPORTEDBY` 에 어떤 숫자로 남는지는 공개된 분석 자료가 없어 시험으로 확인해야 합니다. 에어드롭으로 받은 사진을 `ZCREATORBUNDLEID` 칸으로 가린다는 자료도 있지만, iOS 27.0 에는 그 이름의 칸이 없습니다. 사진 DB 전체 구조는 [사진 보관함](../media/photos/index.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것**

- 사진 DB 의 가져오기 칸 값이 에어드롭을 가리킨다고 시험으로 확인했다면, 그 사진이 에어드롭 경로로 기기에 들어왔다는 기록이 있다는 사실까지 말할 수 있습니다.
- `allowAirDrop` 값이 있으면, 수집 시점의 기기 관리 설정에 에어드롭 제한 항목이 들어 있었다는 사실을 보여 줍니다.
- `com.apple.sharingd.plist` 에 에어드롭 식별자 키가 있으면, 이 기기에 에어드롭 관련 계정 설정이 저장되어 있었다는 사실을 보여 줍니다.

**증명하지 못하는 것**

- 받는 기기가 보여 주는 보낸 사람 이름은 신원이 확인된 경우에만 나오고 [1], 기기에 보낸 사람 정보가 어디에 남는지는 알려져 있지 않습니다. 그래서 보낸 사람을 기기 기록만으로 특정하지 않습니다.
- 전송은 공유기를 거치지 않고 기기끼리 직접 해서 [1], 공유기나 통신사 기록에서 이 전송을 찾을 수 없습니다. 기록이 없다고 해서 전송이 없었다고 말하지 않습니다.
- 파일을 받은 기록은 그 파일을 열어 보았다는 증거가 아닙니다.
- 에어드롭 설정이 켜져 있었다는 사실은 특정 시각에 무엇을 주고받았다는 증거가 아닙니다.

보고서에는 "이 사진은 가져오기 칸 값이 이것이고, 같은 조건의 시험에서 이 값은 에어드롭으로 받은 사진에 나타났다" 처럼 기록과 시험이 말하는 만큼만 씁니다.

## 시각 해석

`com.apple.sharingd.plist` 의 `HashManager-LastUpdatedDateKey`·`HashManager-LastRebuiltDateKey` 는 plist 날짜형이라서 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 의 규칙대로 읽지만, 무엇이 바뀔 때 이 값이 바뀌는지는 알려져 있지 않습니다. 이름으로 보아 해시 목록을 고친 때로 보이고, 전송 시각으로 읽지 않습니다.

받은 사진의 시각은 사진 DB 의 가져오기 시각(`ZIMPORTDATE`)과 사진 자체의 촬영 시각이 다를 수 있습니다. 사진 DB 시각 칸의 기준은 [사진 보관함](../media/photos/index.md) 과 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서, 촬영 시각은 [카메라 사진과 메타데이터](../media/dcim-exif.md) 에서 확인합니다. 보낸 기기의 촬영 시각과 받은 기기의 가져오기 시각을 섞어 쓰면 사건 순서가 틀어질 수 있어서, 두 값을 칸 이름과 함께 따로 적습니다.

## 함정과 한계

Apple 공식 문서는 에어드롭이 기기에 남기는 기록이나 받은 항목의 저장 위치를 설명하지 않습니다 [1][2]. 그래서 공개 자료나 도구가 말하는 에어드롭 흔적은 버전마다 시험으로 다시 확인해야 하고, 한 버전에서 확인한 칸 이름이나 값을 다른 버전에 그대로 적용하지 않습니다.

"10분 동안 모든 사람" 설정은 iOS 16.2 이상에서 10분 뒤 바뀌어서 [2], 수집 시점의 받기 모드가 사건 당시의 받기 모드와 다를 수 있습니다. 받기 모드를 담는 키도 이름으로는 드러나 있지 않습니다.

사진이 아닌 파일이 어디에 저장되는지는 공식 문서에 없어서 [2], 사진 DB 만 보고 에어드롭으로 받은 것이 없다고 결론 내리지 않습니다. 통합 로그에 전송 흔적이 남는지와 로컬 백업에 통합 로그가 들어가는지는 검체에서 확인합니다. 로그를 얻는 방법은 [sysdiagnose 묶음](../../01-foundations/backups/sysdiagnose.md), 찾을 사건은 [통합 로그에서 찾을 것](../logs/unified-log-events.md) 에서 다룹니다.

받은 사진을 지운 경우는 사진 DB 의 지운 항목과 [지운 대화와 사진 찾기](../../04-scenarios/activity/deleted-content.md) 의 흐름으로 확인합니다.

## 직접 분석해 보기

로컬 백업이면 `Manifest.db` 에서 에어드롭·공유와 이름이 이어지는 도메인의 파일을 먼저 뽑습니다.

```sql
SELECT fileID, domain, relativePath
FROM Files
WHERE domain LIKE '%AirDrop%'
   OR domain LIKE '%sharingd%'
   OR relativePath LIKE '%sharingd%'
ORDER BY domain, relativePath;
```

찾은 plist 는 복사본으로 옮겨 헥스 편집기로 첫 8바이트를 봅니다. 아래는 이진 plist 명세로 만든 예시이고 특정 검체의 값이 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07   문자
00000000  62 70 6C 69 73 74 30 30   bplist00
```

`com.apple.sharingd.plist` 에는 계정·해시 값이 들어 있어서, 먼저 값 없이 키 이름과 형식만 뽑아 보고 필요한 키만 엽니다.

```python
import plistlib

with open("sharingd-copy.plist", "rb") as f:
    data = plistlib.load(f)

for key, value in data.items():
    print(key, type(value).__name__)
```

사진 쪽은 `Photos.sqlite` 복사본을 SQLite 명령행 도구(`sqlite3` 등)로 열어, 가져오기 칸 값이 어떻게 나뉘는지부터 봅니다.

```sql
SELECT ZIMPORTEDBY, ZIMPORTEDBYBUNDLEIDENTIFIER, ZIMPORTEDBYDISPLAYNAME,
       COUNT(*) AS n
FROM ZCLOUDMASTER
GROUP BY ZIMPORTEDBY, ZIMPORTEDBYBUNDLEIDENTIFIER, ZIMPORTEDBYDISPLAYNAME
ORDER BY n DESC;
```

값의 뜻은 연습용 기기에서 에어드롭으로 사진을 한 장 받은 뒤 같은 질의를 돌려, 새로 생긴 값과 비교해 정합니다. 이렇게 정한 뜻은 검체의 iOS 버전과 함께 적어 둡니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [사진 보관함](../media/photos/index.md) | 받은 사진의 가져오기 정보와 시각 |
| [카메라 사진과 메타데이터](../media/dcim-exif.md) | 받은 사진의 촬영 시각·촬영 기기 |
| [연락처](../communications/contacts.md) | "연락처만" 모드에서 응답할 상대가 연락처에 있는지 |
| [애플 계정](../system-account/apple-account.md) | 신원 해시의 바탕이 되는 계정 |
| [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md) | 에어드롭 제한 설정 |
| [블루투스 장치](bluetooth.md) · [와이파이 기록](wifi.md) | 같은 시간대의 무선 상태 |
| [통합 로그에서 찾을 것](../logs/unified-log-events.md) | 전송이 일어난 순간 |

자료를 밖으로 보냈는지 따지는 흐름은 [자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration/index.md), 누구와 주고받았는지는 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md) 에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등)에 에어드롭으로 받은 사진이 든 아이폰 추출이 있으면 아래 질문으로 풀어 봅니다. 없으면 연습용 기기 두 대로 사진을 한 장 주고받은 전후로 받은 쪽 백업을 떠서 비교합니다.

1. 받은 뒤 `ZCLOUDMASTER` 의 `ZIMPORTEDBY`·`ZIMPORTEDBYBUNDLEIDENTIFIER` 에 어떤 값이 새로 생겼습니까?
2. 받은 사진의 `ZIMPORTDATE` 와 EXIF 촬영 시각은 어떻게 다릅니까?
3. `com.apple.sharingd.plist` 에서 전송 전후로 값이 바뀐 키가 있습니까? 받기 모드를 바꾸면 어느 키가 바뀝니까?
4. `AppDomainGroup-group.com.apple.sharingd` 도메인의 파일은 무엇이고, 전송 뒤에 달라집니까?
5. 사진이 아닌 파일(예: PDF)을 받으면 어디에 저장되고, 사진 DB 에는 흔적이 남습니까?

## 참고 문헌

1. Apple Platform Security, "AirDrop security" — https://support.apple.com/guide/security/airdrop-security-sec2261183f4/web
2. Apple 지원 문서 119857 (iPhone 에어드롭 사용) — https://support.apple.com/en-us/119857
