---
title: "앱 지우기"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 1520
---

# 앱 지우기 (App Removal)

기기에 있던 앱을 지웠는지, 어떤 앱을 언제 지웠는지를 따지는 시나리오입니다. 앱을 지워도 그 앱을 가리키는 기록은 앱 밖의 다른 DB·plist·로그에 남아서 [1], 이 기록을 모아 지운 앱과 날짜를 좁힙니다.

## 조사 질문

지금 기기에 없는 앱 가운데 한때 설치했던 앱이 무엇인지, 그 앱을 언제 지웠는지를 묻습니다. 앱을 완전히 지웠는지, 저장 공간을 비우려고 앱 본체만 내린 "앱 정리 (offload)" 인지도 함께 가립니다. 정리한 앱은 앱 본체만 사라지고 데이터 컨테이너는 남아서 [1], 두 경우는 볼 수 있는 데이터의 양이 크게 다릅니다.

## 먼저 확인할 것

지운 앱의 흔적을 다룬 공개 자료는 2019년 것이라 [1], iOS 15 이후에도 경로와 동작이 같은지는 검체에서 확인합니다. 검체의 iOS 버전에서 파일이 실제로 있는지부터 봅니다.

수집 범위가 결과를 크게 가릅니다. 지운 앱을 가장 직접 보여 주는 `UninstalledApplications.plist` 는 전체 파일 시스템 이미지에서만 얻을 수 있고 [1], 로컬 백업에는 이 파일과 `DAAP.sqlitedb` 가 들어 있지 않을 수 있습니다. 로컬 백업만 있다면 설치 목록과 홈 화면 배치를 비교하는 방법이 중심이 됩니다.

기기 이전 이력도 봅니다. `UninstalledApplications.plist` 는 기기마다 따로 있고 다른 기기로 옮겨지지 않아서 [1], 새 기기로 옮긴 경우 예전 기기에서 지운 앱은 이 파일에 없습니다. 복원·이전 흔적은 [초기화 (Erase All Content)](erase-reset.md) 에서 다룹니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 위치 | 알려 주는 것 | 자세히 |
|---|---|---|---|---|
| 1 | 지운 앱 목록 | `/private/var/installd/Library/MobileInstallation/UninstalledApplications.plist` | 번들 ID 와 그 앱을 마지막으로 지운 날짜가 들어 있고, 9개월 넘은 기록도 남습니다 [1] | [설치된 앱](../../../02-artifacts/app-usage/installed-apps.md) |
| 2 | 앱 상태 DB | 기기 `/private/var/mobile/Library/FrontBoard/applicationstate.db`, 백업 HomeDomain `Library/FrontBoard/applicationState.db` | 설치된 앱을 기록하고, 앱을 정리하면 항목이 빠집니다 [1] | [설치된 앱](../../../02-artifacts/app-usage/installed-apps.md) |
| 3 | 홈 화면 배치 | `IconState.plist`(백업 HomeDomain `Library/SpringBoard/`) | 이 파일의 번들 ID 를 앱 상태 DB 와 비교해 정리한 앱과 완전히 설치된 앱을 가릅니다 [1] | [설치된 앱](../../../02-artifacts/app-usage/installed-apps.md) |
| 4 | 구입 앱 목록 | `/private/var/mobile/Library/Caches/com.apple.appstored/DAAP.sqlitedb` | Apple 계정 기준 구입 앱 목록이고(iOS 12 이후), 기기에 지금 없는 앱도 들어 있습니다 [1] | [앱 스토어 기록](../../../02-artifacts/app-usage/app-store.md) |
| 5 | 예전 구입 기록 | `/private/var/mobile/Library/Caches/com.apple.storeservices/AppPurchaseHistory.6.sqlitedb` | 예전 iOS 에서 4번과 비슷한 역할을 했습니다 [1] | [앱 스토어 기록](../../../02-artifacts/app-usage/app-store.md) |

이 밖에 Mobile Installation 로그, 스크린 타임, PowerLog, KnowledgeC, DataUsage.sqlite, netusage.sqlite, CallHistory.storedata 에도 지운 앱의 흔적이 남을 수 있습니다 [1]. 지운 앱이 이 파일들에 어떤 모양으로 남는지는 공개 자료가 적어 검체에서 확인합니다. 각 파일을 읽는 법은 [화면 사용 시간](../../../02-artifacts/app-usage/screen-time.md), [전원 로그](../../../02-artifacts/app-usage/powerlog.md), [KnowledgeC](../../../02-artifacts/app-usage/knowledgec/index.md), [앱별 데이터 사용량](../../../02-artifacts/network/data-usage.md), [통화 기록](../../../02-artifacts/communications/call-history.md) 에서 다룹니다. 로컬 백업에는 KnowledgeC·바이옴·PowerLog·installd 로그가 들어 있지 않을 수 있습니다.

로컬 백업에서 앱 지우기와 관련될 만한 파일은 아래와 같습니다. 앱을 지운 뒤 값이 어떻게 바뀌는지는 공개 자료가 없어 검체에서 확인합니다.

| 파일(백업) | 표·키 이름 |
|---|---|
| HomeDomain `Library/FrontBoard/applicationState.db` | `application_identifier_tab`(`id`, `application_identifier`), `key_tab`(`id`, `key`), `kvs`(`id`, `application_identifier`, `key`, `value`), `schema`(`version`) |
| HomeDomain `Library/SpringBoard/IconState.plist` | `iconLists`, `ignored`, `buttonBar`, `today`, `listUniqueIdentifiers`, `displayName` 등 |
| HomeDomain `Library/SpringBoard/DesiredIconState.plist` | `iconLists`, `dockUtilities`, `metadata`(`creationDate`), `ignored` 등 |
| HomeDomain `Library/Preferences/com.apple.appstored.plist` | `OffloadingGracePeriodStartDate`, `LastUpdatesCheck`, `AppUsageBiomeStartDate` 등(날짜) |
| InstallDomain `Library/MobileInstallation/BackedUpState/SystemAppInstallState.plist`, `BackupSystemAppInstallState.plist` | Apple 기본 앱 번들 ID(`com.apple.mobilesafari`, `com.apple.MobileSMS` 등)가 키이고 값은 정수 |
| WirelessDomain `Library/Databases/DataUsage.sqlite` | `ZPROCESS`(`ZFIRSTTIMESTAMP`, `ZTIMESTAMP`, `ZBUNDLENAME`, `ZPROCNAME` 등) |
| 백업 최상위 `Info.plist` | `Installed Applications` |

`SystemAppInstallState.plist` 의 정수 값이 기본 앱을 지웠는지 나타내는지, 백업 `Info.plist` 의 `Installed Applications` 가 백업 시점의 설치 목록인지는 공개 자료가 없어서, 쓰기 전에 시험 기기로 확인합니다. 백업 파일 구조는 [로컬 백업](../../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.

## 분석 흐름

1. 전체 파일 시스템 수집이라면 `UninstalledApplications.plist` 에서 번들 ID 와 마지막 삭제 날짜를 뽑습니다. 번들 ID 를 앱 이름으로 바꾸는 법은 [번들 ID와 앱 그룹](../../../01-foundations/value-decoding/bundle-id-app-group.md) 을 봅니다.
2. 앱 상태 DB 의 번들 ID 와 `IconState.plist` 의 번들 ID 를 비교합니다. 홈 화면에는 있는데 앱 상태 DB 에 없는 앱은 정리한 앱으로 봅니다 [1].
3. 정리한 앱은 데이터 컨테이너가 남아 있어서, [앱 데이터 분석](../../../03-techniques/analysis/app-data-analysis/index.md) 으로 넘어가 앱 데이터를 그대로 읽습니다.
4. 구입 앱 목록에서 기기에 지금 없는 앱을 찾아 1단계 결과와 맞춰 봅니다. 목록이 계정 기준이라서, 여기 있다는 사실만으로 이 기기에 설치했었다고 보지 않습니다.
5. 후보 번들 ID 마다 [어떤 앱을 언제 썼나 (App Usage)](../app-usage.md) 의 흔적에서 마지막 사용 시각을 찾고, 삭제 날짜와 앞뒤가 맞는지 봅니다.
6. 삭제 날짜를 사건 기간과 함께 [타임라인](../../../03-techniques/analysis/timeline/index.md) 에 올립니다.

## 흔한 오판

지금 설치 목록에 없는 앱을 모두 "지운 앱" 으로 적는 실수가 가장 흔합니다. 정리한 앱은 앱 상태 DB 에서 항목이 빠지지만 [1] 데이터 컨테이너는 남아 있고, 사용자가 지운 앱과는 뜻이 다릅니다.

`UninstalledApplications.plist` 의 날짜를 처음 지운 날짜로 읽는 실수도 있습니다. 이 파일에는 그 앱을 마지막으로 지운 날짜가 들어 있어서 [1], 같은 앱을 여러 번 설치하고 지웠다면 앞선 삭제는 이 파일로 알 수 없습니다.

로컬 백업에 `UninstalledApplications.plist` 가 없다고 앱을 지운 적이 없다고 보면 안 됩니다. 이 파일은 전체 파일 시스템 이미지에서만 얻을 수 있습니다 [1].

앱을 지웠다는 기록은 삭제가 있었다는 사실까지만 말합니다. 앱을 지운 이유나 그 앱의 데이터를 없애려 한 의도는 이 기록으로 알 수 없습니다.

## 보고서 문장 예

> `UninstalledApplications.plist` 에 번들 ID (번들 ID) 항목이 있고, 이 앱을 마지막으로 지운 날짜는 (날짜) 로 기록되어 있습니다. 이 날짜 이전의 삭제 여부와 삭제한 이유는 이 기록으로 알 수 없습니다.

## 함께 볼 페이지

- [증거를 없애려 했나 (Anti-Forensics)](index.md) — 이 시나리오 묶음의 허브
- [메시지·사진 지우기 (Content Deletion)](content-deletion.md) — 앱은 두고 내용만 지운 경우
- [설치된 앱 (Installed Apps·applicationState.db)](../../../02-artifacts/app-usage/installed-apps.md)
- [앱 스토어 기록 (App Store)](../../../02-artifacts/app-usage/app-store.md)
- [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md) — 전체 파일 시스템 수집과 백업의 차이

## 참고 문헌

1. D20 Forensics, "iOS - Tracking Traces of Deleted Applications" (2019) — https://blog.d204n6.com/2019/09/ios-tracking-traces-of-deleted.html
