---
title: "앱 데이터 분석"
parent: "기법 · 분석"
nav_order: 1230
has_children: true
has_toc: false
---

# 앱 데이터 분석 (App Data Analysis)

아이폰 앱의 데이터가 어디에 어떤 모양으로 남는지 짚고, 처음 보는 앱과 이미 지운 앱까지 번들 ID 를 기준으로 흔적을 찾아가는 방법을 모았습니다.

## 왜 중요한가

서드파티 앱은 모두 샌드박스 안에서 돌고 다른 앱의 정보를 모으거나 바꾸지 못하게 설계되어 있으며, 앱마다 설치할 때 무작위로 정해지는 홈 디렉터리가 따로 있습니다[8]. 앱이 남긴 데이터는 먼저 그 앱의 컨테이너에서 찾고, 컨테이너 밖에서는 시스템이 따로 남긴 설치·사용·통신 기록을 찾습니다. 이 핸드북의 아티팩트 사전은 자주 만나는 앱을 앱별로 다루지만, 사건에서는 사전에 없는 앱이나 이미 지운 앱을 만나기도 합니다. 이때 앱 이름이 아니라 번들 ID 를 기준 키로 삼으면 삭제한 앱까지 여러 DB 에서 흔적을 찾을 수 있습니다[3].

수집 방법에 따라 볼 수 있는 범위도 다릅니다. Apple 문서는 앱 컨테이너의 `Library/Caches` 와 `tmp/` 를 백업에서 뺀다고 적고 있고[1], Biome·KnowledgeC·Power Log 같은 기록은 전체 파일 시스템 추출에서만 얻는다는 정리도 있습니다[7]. 어떤 폴더가 어느 수집 방법에 들어가는지 알아야 "없다" 를 "안 모았다" 와 가를 수 있습니다.

## 한눈에 보기

| 위치 | iOS 버전 | 알려 주는 것 |
|---|---|---|
| 앱 데이터 컨테이너 (`/private/var/mobile/Containers/Data/Application/<GUID>`, 백업에서는 `AppDomain-<번들 ID>`) | 파일 시스템 경로[7], 백업 도메인 (확인 범위: iOS 27.0) | 앱이 저장한 설정·DB·문서 |
| 앱 그룹 공유 폴더 (`AppDomainGroup-<그룹 ID>`), 앱 확장 (`AppDomainPlugin-<번들 ID>`) | (확인 범위: iOS 27.0) | 본체와 확장이 함께 쓰는 데이터 |
| `Manifest.db` 의 `Files` 표 | (확인 범위: iOS 27.0) | 로컬 백업 안에서 앱 파일을 찾는 목록 |
| `applicationState.db` | iOS 11.2.1 에서 시험[6], 표 이름은 (확인 범위: iOS 27.0) | 설치 상태, 일부 앱의 삭제 시각 |
| 앱 HTTP 캐시 `Cache.db` | 백업에 안 들어감(iOS 2.2 이후)[1] | 앱이 받아 저장한 HTTP 응답 |
| WebKit `observations.db` | (확인 범위: iOS 27.0) | 앱 안 웹뷰가 접속한 도메인 |
| Mobile Installation 로그, `UninstalledApplications.plist` | 2019년 글[3] | 설치·삭제 시각 |
| Biome `_DKEvent.App.Install` | iOS 16[4] | 설치 시각, 보존 28일 |

## 읽는 순서

1. [처음 보는 앱 분석 순서 (Unknown Apps)](unknown-apps.md) — 번들 ID 확정부터 설치 확인, 컨테이너 열기, 앱 밖의 시스템 기록까지 처음 보는 앱을 여는 순서를 따라갑니다. 컨테이너 구조와 백업 포함 여부 표도 여기에 있습니다.
2. [캐시와 웹뷰 (Cache·WebKit)](cache-webkit.md) — 앱의 HTTP 캐시와 웹뷰가 남기는 WebKit 데이터에서 앱이 통신한 서버와 도메인을 찾습니다.
3. [지운 앱이 남긴 흔적 (Uninstalled Apps)](uninstalled-apps.md) — 앱을 지운 뒤에도 남는 설치 상태, 설치 로그, 구매 기록, 사용 기록을 찾고 삭제와 오프로드를 가릅니다.

## 함께 볼 페이지

앱 번들 ID 와 앱 그룹 ID 를 읽는 법은 [번들 ID와 앱 그룹](../../../01-foundations/value-decoding/bundle-id-app-group.md) 에, 백업 안에서 파일을 찾는 구조는 [로컬 백업](../../../01-foundations/backups/local-backup/index.md) 에 있습니다. 앱 안의 DB 와 설정 파일은 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md) 와 [속성 목록 파일](../../../01-foundations/data-formats/plist.md) 의 방법으로 엽니다. 설치 앱 목록과 사용 기록은 [설치된 앱](../../../02-artifacts/app-usage/installed-apps.md), [KnowledgeC](../../../02-artifacts/app-usage/knowledgec/index.md), [바이옴](../../../02-artifacts/app-usage/biome/index.md) 에서 다루고, 앱을 언제 썼는지 묻는 조사는 [어떤 앱을 언제 썼나](../../../04-scenarios/activity/app-usage.md), 낯선 앱이 악성인지 가리는 조사는 [악성 코드·스파이웨어 흔적](../spyware-triage/index.md) 에서 이어 갑니다.

## 참고 문헌

- [1] Apple Developer, File System Programming Guide — File System Basics (보관 문서) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html
- [3] D20 Forensics, "iOS - Tracking Traces of Deleted Applications" (2019-09) — https://blog.d204n6.com/2019/09/ios-tracking-traces-of-deleted.html
- [4] D20 Forensics, "iOS 16 Breaking Down the Biomes Part 2 - AppInstalls, AppLaunch, & AppIntents" (2022-09) — https://blog.d204n6.com/2022/09/ios-16-breaking-down-biomes-part-2.html
- [6] Alexis Brignoni, "Identifying installed and uninstalled apps in iOS" (2018-12) — https://abrignoni.blogspot.com/2018/12/identifying-installed-and-uninstalled.html
- [7] digital-forensics.it, "Has the user ever used the XYZ application? aka traces of application execution on mobile devices" (2023-12) — https://blog.digital-forensics.it/2023/12/has-user-ever-used-xyz-application-aka.html
- [8] Apple Platform Security, "Security of runtime process in iOS, iPadOS, and visionOS" (2024-12-19) — https://support.apple.com/guide/security/security-of-runtime-process-sec15bfe098e/web
