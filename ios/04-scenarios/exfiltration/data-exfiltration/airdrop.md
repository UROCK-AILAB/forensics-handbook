---
title: "에어드롭으로"
parent: "자료를 밖으로 보냈나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 1590
---

# 에어드롭으로 (AirDrop)

AirDrop 으로 자료를 주변 기기에 넘겼는지 가리는 페이지입니다. AirDrop 은 인터넷이나 공유기 없이 기기끼리 주고받기 때문에[1], 기기 안의 로그와 받은 쪽 기기의 흔적을 중심으로 봅니다. 기능과 설정 파일의 자세한 설명은 [에어드롭 (AirDrop)](../../../02-artifacts/network/airdrop.md) 에 있고, 이 페이지는 유출을 가리는 순서와 해석을 다룹니다. 다른 유출 경로와 전체 흐름은 허브 [자료를 밖으로 보냈나 (Data Exfiltration)](index.md) 에 있습니다.

## 조사 질문

"이 아이폰에서 AirDrop 으로 자료를 보냈는가, 받은 기기가 있다면 그 기기에서 보낸 사람을 가릴 수 있는가" 를 묻습니다. 보낸 쪽 기기에 무엇을 누구에게 보냈는지가 남는지는 이 페이지의 자료로 확인하지 못했습니다. 그래서 받은 쪽 기기를 확보할 수 있는지가 조사 범위를 크게 가릅니다.

## 먼저 확인할 것

AirDrop 은 BLE 와 Apple 의 기기 간 Wi-Fi(peer-to-peer)로 주변 기기를 찾고, 인터넷이나 공유기가 필요 없습니다[1]. 받는 사람이 직접 수락해야 전송되고, 전송은 TLS 로 암호화됩니다[1]. 두 기기가 같은 시간에 가까이 있었는지는 [그 시각에 어디 있었나 (Location)](../../activity/location.md) 의 위치 기록으로 따로 확인합니다.

버전에 따라 설정과 기능이 달라서 iOS 버전도 확인합니다.

| iOS | 달라진 점 |
|---|---|
| 16.2 이상 | "모든 사람(10분 동안)" 을 고르면 10분 뒤 설정이 바뀝니다. Apple 계정에 로그인되어 있으면 "연락처만", 아니면 "수신 끔" 으로 돌아갑니다[2]. |
| 17 이상 | 두 기기가 모두 iOS 17 이상이면 기기를 맞대어 AirDrop 으로 공유할 수 있습니다[2]. |

인터넷(셀룰러)으로 이어서 보내는 기능은 이 페이지의 자료로 확인하지 못했습니다.

수집 범위도 확인합니다. 아래에서 쓰는 로그는 sysdiagnose 묶음 안의 `system_logs.logarchive` 에서 얻고[3], 로컬 백업에는 AirDrop 과 관련된 설정 파일과 사진 DB 가 들어 있습니다. sysdiagnose 를 받는 방법은 [sysdiagnose 묶음 (sysdiagnose)](../../../01-foundations/backups/sysdiagnose.md) 에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | sysdiagnose 의 통합 로그(AirDrop 범주) | AirDrop 이벤트와 시각, 받은 쪽에서는 보낸 사람의 부분 해시 | [통합 로그에서 찾을 것 (Unified Log Events)](../../../02-artifacts/logs/unified-log-events.md) |
| 2 | `com.apple.sharingd.plist` | AirDrop 식별자와 연락처 해시 관리 기록의 키 | [에어드롭 (AirDrop)](../../../02-artifacts/network/airdrop.md) |
| 3 | `EffectiveUserSettings.plist` | 구성 프로파일로 AirDrop 을 막았는지 | [구성 프로파일과 MDM (Configuration Profiles·MDM)](../../../02-artifacts/credentials-security/configuration-profiles.md) |
| 4 | 받은 쪽의 `Photos.sqlite`·파일 앱 Inbox | 사진·파일이 어느 경로로 들어왔는지 | [사진 보관함 (Photos Library)](../../../02-artifacts/media/photos/index.md) |

### 통합 로그

AirDrop 이벤트는 `system_logs.logarchive` 에서 AirDrop 범주로 걸러 볼 수 있고, 로그를 남기는 프로세스는 sharingd 입니다[3].

```sh
log show --predicate 'category = "AirDrop"' system_logs.logarchive
```

받는 쪽 로그에는 보낸 사람의 부분 SHA-256 해시가 남습니다[3]. 해석의 바탕이 되는 신원 확인 방식은 이렇습니다. AirDrop 은 Apple 계정의 이메일·전화번호로 만든 짧은 신원 해시(short identity hash)를 보내고, "연락처만" 모드에서는 받는 쪽이 이 해시를 자기 연락처와 대조해 맞을 때만 응답합니다[1]. 그 뒤 긴 신원 해시를 주고받아 확인되면 보낸 사람의 이름과 사진을 보여 주고, 확인되지 않으면 실루엣과 기기 이름만 보여 줍니다[1].

[3] 은 받는 쪽 로그의 부분 해시를, 국가·지역 번호 조합으로 만든 후보 번호의 해시와 대조해 보낸 전화번호를 찾는 방법을 소개합니다. 이 방법은 보낸 사람이 Apple 계정의 전화번호로 보냈을 때만 통하고, 이메일로 보낸 경우는 추가 연구가 필요하다고 적었습니다[3]. 방법의 출처는 Epstein·Klein·Feuerstein 의 논문 "Analysis of Sysdiagnose in iOS 15 to Identify the Sending Phone Number of AirDrop Data"(Journal of Forensic Sciences, 2022년 1월)이고, [3] 은 iPhone 13 Pro, iOS 15.3.1 에서 시험해 RLEAPP 모듈로 자동화했습니다. 다른 버전에서 로그 문구와 해시 길이가 같은지는 확인하지 못했으니, 적용하기 전에 같은 버전의 시험 기기로 먼저 확인합니다. 방법은 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md) 을 따릅니다.

보낸 쪽 기기의 같은 범주 로그에 무엇이 남는지는 [3] 이 다루지 않았습니다. 보낸 쪽 로그에서 AirDrop 이벤트를 찾더라도 받는 사람과 파일을 곧바로 적지 않고, 로그 문구가 말하는 만큼만 씁니다.

### 설정 파일

관찰한 백업의 `HomeDomain :: Library/Preferences/com.apple.sharingd.plist` 에는 아래 키가 있었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```text
AirDropID
CurrentPseudonym
SDAirDropIDMSServiceAccountAltDSID
SDAirDropIDMSServiceContactsHistoryToken
HashManager-LastUpdatedDateKey
HashManager-LastRebuiltDateKey
HashManager-LastDeviceIDHashKey
HashManager-StoredDatabaseVersionKey
HashManager-LastConsumedHistoryTokenKey
AppleIDAccount
UIActivityCategoryShare
UIActivityCategoryAction
StreamID
```

키 이름만 확인했고 뜻은 확인하지 못했습니다. 수신 모드("연락처만"·"모든 사람")를 드러내는 이름의 키는 이 목록에 없었습니다(확인 범위: iPhone 13 mini, iOS 27.0). 같은 백업에는 AppDomain-com.apple.Sharing.AirDropUI, AppDomainGroup-group.com.apple.sharingd, AppDomainPlugin-com.apple.Sharing.AirDrop, AppDomainPlugin-com.apple.Sharing.AirDropAlertUI, AppDomainPlugin-com.apple.AirDropSettingsIntents, AppDomain-com.apple.SharingViewService 도메인이 있었지만 각각 항목이 3~4개뿐이었습니다(확인 범위: iPhone 13 mini, iOS 27.0).

`HomeDomain :: Library/UserConfigurationProfiles/EffectiveUserSettings.plist` 의 restrictedBool 안에는 allowAirDrop 키가 있습니다(확인 범위: iPhone 13 mini, iOS 27.0). 회사 기기라면 이 값으로 AirDrop 이 막혀 있었는지를 먼저 봅니다. 다만 이 값은 수집 시점의 설정이라서, 사건 당시에도 막혀 있었는지는 프로파일을 설치하거나 지운 기록과 함께 판단합니다.

### 받은 쪽 기기

받은 쪽 기기를 확보했으면 들어온 자료의 경로를 봅니다. `Photos.sqlite` 에서는 ZADDITIONALASSETATTRIBUTES.ZIMPORTEDBY 와 ZCLOUDMASTER 의 ZIMPORTEDBY·ZIMPORTEDBYBUNDLEIDENTIFIER·ZIMPORTEDBYDISPLAYNAME·ZORIGINALFILENAME 칸으로 사진이 어떻게 들어왔는지 가립니다(확인 범위: iPhone 13 mini, iOS 27.0). AirDrop 으로 들어온 사진에 어떤 값이 들어가는지는 확인하지 못했으니, 같은 버전의 시험 기기로 AirDrop 을 한 번 받아 값을 확인한 뒤 씁니다. 파일 앱에서 AirDrop 으로 받은 파일은 Inbox 로 갑니다[4](iOS 13 기준).

## 분석 흐름

1. 두 기기(보낸 쪽으로 의심되는 기기와 받은 쪽 기기)의 iOS 버전·시간대를 적고, 조사 기간을 정합니다.
2. `EffectiveUserSettings.plist` 로 AirDrop 이 막혀 있었는지 확인합니다.
3. 두 기기에서 sysdiagnose 를 받아 AirDrop 범주 로그를 조사 기간으로 거릅니다.
4. 받은 쪽 로그에서 보낸 사람의 부분 해시를 찾고, 의심 기기의 Apple 계정 전화번호로 만든 해시와 맞는지 대조합니다.
5. 받은 쪽 `Photos.sqlite` 와 파일 앱 Inbox 에서 조사 기간에 들어온 자료를 찾고, 파일 이름·형식을 유출 의심 자료와 맞춰 봅니다.
6. 두 기기의 로그 시각과 사진 가져온 시각을 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) 에 올리고, 같은 시간대에 두 기기가 가까이 있었는지 위치 기록으로 받칩니다.

## 흔한 오판

AirDrop 은 받는 사람이 수락해야 전송된다고 설명되어 있지만[1], 같은 Apple 계정에 로그인한 자기 기기끼리 보낼 때도 수락 절차가 있는지는 이 페이지의 자료로 확인하지 못했습니다. 그래서 받은 쪽 기록에 파일이 있다는 사실만으로 받은 기기에서 누군가 수락했다고 쓰지 않고, 두 기기의 Apple 계정이 같은지부터 확인합니다. 반대로 보낸 쪽 로그에 전송 시도가 보여도 받은 쪽이 거절했을 수 있어서, 보낸 쪽 기록만으로 "전달되었다" 고 쓰지 않습니다.

부분 해시가 맞는다는 결과는 보낸 기기에 로그인된 Apple 계정의 전화번호를 가리킬 뿐, 그 순간 기기를 쥔 사람을 가리키지 않습니다. 사용자 판단은 [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](../../activity/user-attribution.md) 를 따릅니다.

iOS 16.2 이상에서 "모든 사람(10분 동안)" 은 10분 뒤 돌아가므로[2], 수집 시점의 설정이 사건 당시의 설정과 다를 수 있습니다.

## 보고서 문장 예

> 받은 쪽 기기의 sysdiagnose 통합 로그에 현지 시각 ○○ AirDrop 범주 이벤트가 있고, 이 이벤트에 남은 보낸 사람의 부분 SHA-256 해시가 전화번호 ○○로 만든 해시와 일치합니다. 이 결과는 보낸 기기의 Apple 계정에 이 전화번호가 연결되어 있었다는 뜻이며, 기기를 사용한 사람을 가리키지는 않습니다.

> 조사 대상 기기의 로컬 백업에는 AirDrop 전송 내용(파일 이름·받는 사람)을 담은 기록이 확인되지 않습니다. 이 백업만으로는 AirDrop 전송 여부를 판단할 수 없습니다.

## 함께 볼 페이지

- [에어드롭 (AirDrop)](../../../02-artifacts/network/airdrop.md)
- [sysdiagnose 안의 로그 (sysdiagnose Logs)](../../../02-artifacts/logs/sysdiagnose-logs.md)
- [통합 로그 형식 (Unified Log·tracev3)](../../../01-foundations/data-formats/unified-log.md)
- [메신저로 (Messenger)](messenger.md), [클라우드로 (Cloud)](cloud.md), [메일로 (Email)](email.md), [PC 동기화로 (PC Sync)](pc-sync.md)
- [이 사진은 언제 어디서 찍었나 (Photo Origin)](../../activity/photo-origin.md)

## 참고 문헌

1. Apple Platform Security, "AirDrop security" — https://support.apple.com/guide/security/airdrop-security-sec2261183f4/web
2. Apple 지원 문서 119857 (AirDrop 사용·문제 해결) — https://support.apple.com/en-us/119857
3. 4n6 Ninja, "(Air)Dropping some Knowledge: Using RLEAPP to Identify the Phone Number Used in an AirDrop Transfer" — https://gforce4n6.blogspot.com/2022/03/airdropping-some-knowledge-using-rleapp.html
4. D20 Forensics, "iOS - The Files App" — https://blog.d204n6.com/2020/09/ios-files-app.html
