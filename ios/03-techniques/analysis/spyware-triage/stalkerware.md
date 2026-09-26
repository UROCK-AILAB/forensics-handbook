---
title: "감시 앱 흔적"
parent: "악성 코드·스파이웨어 흔적"
grand_parent: "기법 · 분석"
nav_order: 1380
---

# 감시 앱 흔적 (Stalkerware)

가까운 사람이 기기나 계정에 손대 위치·메시지를 엿본다는 의심이 있을 때, 안전 확인(Safety Check) 화면과 백업에 남은 공유·권한·위치·자동화 기록을 차례로 점검하는 방법입니다.

## 언제 쓰나

배우자나 가족, 전 연인처럼 기기에 손댈 기회가 있던 사람이 감시한다는 진술이 있을 때 씁니다. MVT 가 받아 오는 공개 스토커웨어 지표(Te-k/stalkerware-indicators)는 주로 Android 용이라서 [1], iOS 에서는 지표 대조만으로 끝내지 않고 계정·구성 프로파일·권한 점검을 함께 합니다. 지표 대조 방법은 [스파이웨어 흔적 찾기 (MVT)](spyware-mvt.md) 에, 프로파일·권한·위치 요청 파일의 자세한 구조는 [구성 프로파일과 설정으로 찾기](profiles-settings.md) 에 있습니다. iOS 감시 앱이 어떤 경로로 들어오는지는 믿을 만한 공개 자료가 없어 이 페이지에서 다루지 않습니다.

## 절차

1. **공유를 끊기 전에 기록을 남깁니다.** 공유를 멈추거나 프로파일을 지우면 그 상태가 바뀌니 로컬 백업과 화면 사진을 먼저 받아 둡니다. 백업은 [로컬 백업](../../../01-foundations/backups/local-backup/index.md) 형식으로 받습니다. 상대가 가까이 있는 상황이라면 안전 확인의 빠른 나가기(Quick Exit)로 설정 앱을 바로 닫고 홈 화면으로 갈 수 있고, 그 전에 바꾼 내용은 저장됩니다 [2].

2. **안전 확인 화면을 봅니다.** 안전 확인은 설정 → 개인정보 보호 및 보안 → 안전 확인 에 있고, iOS 16 이상에서 2단계 인증을 쓰는 Apple 계정이어야 씁니다 [2]. 공유 및 접근 관리(Manage Sharing & Access)에서 사람과의 공유, 앱 접근, Apple 계정에 연결된 기기, 앱 권한을 검토할 수 있고, 긴급 재설정(Emergency Reset)은 모든 사람·앱과의 공유를 바로 멈추고 긴급 연락처·연결 기기·계정 보안을 점검합니다 [2]. 공유를 멈출 때 상대가 알림을 받는지는 공개된 설명이 없고, 일부 앱·서비스는 공유를 다시 시작하면 알립니다 [2]. 화면에 나온 사람·기기·앱 목록을 사진으로 남기고 나서 조치합니다.

3. **모르는 구성 프로파일을 확인합니다.** 모르는 구성 프로파일은 설정 화면에서 확인하고 지울 수 있습니다 [3]. 점검 순서와 볼 파일은 [구성 프로파일과 설정으로 찾기](profiles-settings.md) 를 따릅니다.

4. **백업에서 흔적을 봅니다.** 자세한 설명이 다른 페이지에 있는 항목은 링크만 남겼습니다.

   | 볼 것 | 백업 경로 | 이 페이지에서 볼 점 |
   |---|---|---|
   | 위치를 요청한 앱 | `RootDomain :: Library/Caches/locationd/clients.plist` | 모르는 번들 ID. MVT LocationdClients 모듈 [4]. 키는 [구성 프로파일과 설정으로 찾기](profiles-settings.md) |
   | 앱 권한 | `HomeDomain :: Library/TCC/TCC.db` | 마이크·카메라·위치 권한. MVT TCC 모듈 [4]. 표는 같은 페이지 |
   | 지오펜스 | `RootDomain :: Library/Caches/locationd/consolidated.db` | `GeoFence` 표(`FenceIndex`, `BundleId`, `Name`, `Timestamp`, `Distance`, `OnBehalfBundleId` 등)와 `BeaconFences` 표(`BundleIdentifier`, `OnBehalfBundleIdentifier` 등) |
   | 앱별 셀룰러 사용량 | `WirelessDomain :: Library/Databases/DataUsage.sqlite` | MVT Datausage 모듈 [4]. [앱별 데이터 사용량](../../../02-artifacts/network/data-usage.md) |
   | App Store 밖 서명 프로파일 | `MobileDeviceDomain :: ProvisioningProfiles/mis.db` | 해석은 공개 자료 없음. [구성 프로파일과 설정으로 찾기](profiles-settings.md) |
   | 단축어 자동화 | `HomeDomain :: Library/Shortcuts/Shortcuts.sqlite`, `HomeDomain :: Library/Shortcuts/ExternalTriggers/ExternalTriggers.sqlite` | 사용자가 모르는 자동화. MVT Shortcuts 모듈 [4] |
   | 나의 찾기 | `SysSharedContainerDomain-systemgroup.com.apple.icloud.findmydevice.managed :: Library/Preferences/FMIPStateInfo.plist`, `AppDomain-com.apple.findmy` 도메인 | `fmipActive`, `fmipLostModeType` 키. [나의 찾기](../../../02-artifacts/location/find-my.md) |
   | 백업 설정 | `HomeDomain :: Library/Preferences/com.apple.mobile.ldbackup.plist` | `CloudBackupEnabled`, `LastCloudBackupDate`, `LastCloudBackupTZ`, `RequiresEncryption`, `WillEncrypt`, `Version` 키 |

   지오펜스 표의 `OnBehalfBundleId` 와 `BeaconFences` 의 `OnBehalfBundleIdentifier` 는 이름으로 보면 다른 앱을 대신해 등록한 경우를 가리키는 것으로 보이지만, 뜻과 스토커웨어 탐지에 쓴 공개 사례는 알려져 있지 않습니다. `com.apple.mobile.ldbackup.plist` 로 아이클라우드 백업이 켜져 있는지 볼 수 있을 가능성도 있지만, 키 이름에서 나온 추정입니다.

5. **계정 쪽을 봅니다.** 기기 안에서 걸린 것이 없어도 계정 점검은 따로 합니다. 계정 흔적은 [애플 계정](../../../02-artifacts/system-account/apple-account.md) 과 [계정 탈취 흔적](../../../04-scenarios/incident/account-takeover.md) 에서, 백업 사본은 [아이클라우드 백업](../../../01-foundations/backups/icloud-backup.md) 에서 다룹니다.

## 도구

MVT 의 LocationdClients, TCC, Datausage, Shortcuts 모듈이 표의 파일 일부를 읽습니다 [4]. `consolidated.db`, `ExternalTriggers.sqlite`, `FMIPStateInfo.plist`, `com.apple.mobile.ldbackup.plist` 는 sqlite3 와 plist 뷰어 같은 공개 도구로 직접 엽니다.

## 함정과 한계

공개 스토커웨어 지표가 주로 Android 용이라서 [1], iOS 백업에서 걸린 것이 없다는 결과의 무게는 가볍습니다. 탈옥 흔적이 어떤 파일로 남는지, 위치 공유 상대 목록이 어디에 남는지는 공개 자료가 없어 검체로 확인해야 합니다. 위 표는 암호화하지 않은 백업 기준이라 암호화 백업에만 들어가는 기록은 빠져 있습니다. 안전 확인에서 공유를 멈추면 화면의 목록이 바뀌고, 조치 전 상태는 미리 찍어 둔 화면 사진과 백업에서만 볼 수 있습니다.

## 결과를 어떻게 해석하나

이 점검으로 말할 수 있는 범위는 "백업 시점에 이 번들 ID 가 위치 권한과 백그라운드 위치를 받은 기록이 있다", "안전 확인 화면에 사용자가 모르는 기기가 연결돼 있었다" 까지입니다. 그 앱을 누가 설치했는지, 상대가 실제로 무엇을 봤는지는 기기 기록만으로 증명하지 못합니다. 보고서에는 화면 사진을 찍은 시각과 백업을 받은 시각을 함께 적고, 조사 흐름은 [조사 절차](../../acquisition/investigation-process.md) 를 따릅니다.

## 참고 문헌

1. Indicators of Compromise — Mobile Verification Toolkit — https://docs.mvt.re/en/latest/iocs/
2. Safety Check for an iPhone with iOS 16 or later — Apple Personal Safety User Guide — https://support.apple.com/guide/personal-safety/safety-check-iphone-ios-16-ips2aad835e1/web
3. Review and delete configuration profiles — Apple Personal Safety User Guide — https://support.apple.com/guide/personal-safety/review-and-delete-configuration-profiles-ips327569a75/web
4. Records extracted by mvt-ios — Mobile Verification Toolkit — https://docs.mvt.re/en/latest/ios/records/
