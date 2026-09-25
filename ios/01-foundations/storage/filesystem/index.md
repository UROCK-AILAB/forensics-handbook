---
title: "iOS의 파일 시스템"
parent: "기반 · 저장 구조"
nav_order: 0
has_children: true
has_toc: false
---

# iOS의 파일 시스템 (APFS on iOS)

아이폰은 APFS 로 저장소를 여러 볼륨으로 나누고, 앱마다 컨테이너를 따로 두며, 시스템 볼륨은 서명과 스냅숏으로 지키고 사용자 데이터는 암호화된 Data 볼륨에 둡니다.

## 왜 중요한가

메시지·사진·위치·앱 기록처럼 이 핸드북이 다루는 아티팩트는 모두 파일 시스템의 어느 경로에 있는 파일이고, 경로를 알아야 무엇을 수집했고 무엇이 빠졌는지 설명할 수 있습니다. 기기 파일 시스템에서는 앱 폴더 이름이 UUID 라서 번들 ID 와 이어 줘야 하고 [4], 로컬 백업에서는 같은 파일이 "도메인 + 상대 경로" 로 바뀌어 나타나서 [7], 두 표기를 오가며 읽을 줄 알아야 합니다. 또 시스템 볼륨은 iOS 15 이상에서 서명된 시스템 볼륨이라 사용자가 보호를 끌 수 없고 [1], 사용자 활동의 흔적은 Data 볼륨에 남습니다.

## 한눈에 보기

| 구조 | 위치 | iOS 버전 | 알려 주는 것 | 자세히 |
|---|---|---|---|---|
| System 볼륨(SSV) | 시스템 볼륨 | iOS 15 이상 SSV | 운영체제 파일, 서명 검사 대상 | [볼륨 구성](volumes.md) |
| Data 볼륨 | 사용자 데이터 볼륨(암호화) | 관찰: iOS 18.5 | 사용자·앱 데이터 전부, 파일별 키 암호화 | [볼륨 구성](volumes.md) |
| 번들·데이터 컨테이너 | `/private/var/containers/Bundle/Application/`, `/private/var/mobile/Containers/Data/Application/` | 2020·2021년 글 기준 | 앱 실행 파일과 앱별 데이터 | [앱 컨테이너](app-containers.md) |
| 앱 그룹 컨테이너 | `/private/var/mobile/Containers/Shared/AppGroup/` | 2020·2021년 글 기준 | 앱과 확장이 함께 쓰는 데이터 | [앱 컨테이너](app-containers.md) |
| 시스템 스냅숏 | 루트(/)의 `com.apple.os.update-` 스냅숏 | iOS 15.0, 18.3.2 예 | 시스템 볼륨의 한 시점 모습 | [시스템 스냅숏과 업데이트](snapshots-updates.md) |
| 업데이트 흔적 | 백업 도메인의 설정 파일(plist) | 관찰: iOS 27.0 | 이전·현재 OS 버전 키, 업데이트 관련 키 | [시스템 스냅숏과 업데이트](snapshots-updates.md) |

버전 칸은 각 하위 페이지의 출처가 확인한 범위이고, Apple 이 iOS 버전별로 파일 시스템 구조를 표로 공개한 자료는 이번에 확인하지 못했습니다.

> 그림 자리: 볼륨(System·Data) → Data 볼륨 안의 컨테이너(Bundle·Data·AppGroup) → 로컬 백업 도메인(AppDomain·AppDomainGroup)으로 이어지는 대응 관계

## 읽는 순서

1. [볼륨 구성 (System·Data·Preboot)](volumes.md) — 컨테이너와 볼륨 목록, 서명된 시스템 볼륨, Data 볼륨의 파일별 키, 백업 도메인이 어느 경로에 대응하는지를 다룹니다.
2. [앱 컨테이너 (Bundle·Data·App Group)](app-containers.md) — 컨테이너 경로와 폴더별 백업 여부, UUID 폴더를 번들 ID 로 잇는 파일, 백업의 앱·그룹 도메인을 다룹니다.
3. [시스템 스냅숏과 업데이트 (Snapshots·Updates)](snapshots-updates.md) — 시스템 볼륨 스냅숏과 업데이트, 백업의 설정 파일에 남는 업데이트 관련 키를 다룹니다.

## 함께 볼 페이지

- [데이터 보호 (Data Protection)](../data-protection/index.md) — Data 볼륨 파일의 보호 클래스와 잠금 상태
- [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../backups/local-backup/index.md) — 백업의 파일 배치와 `Manifest.db`
- [번들 ID와 앱 그룹 (Bundle ID·App Group)](../../value-decoding/bundle-id-app-group.md) — 번들 ID·그룹 ID 이름 규칙
- [설치된 앱 (Installed Apps·applicationState.db)](../../../02-artifacts/app-usage/installed-apps.md) — 설치 앱 목록 만들기
- [앱 데이터 분석 (App Data Analysis)](../../../03-techniques/analysis/app-data-analysis/index.md) — 컨테이너 안의 앱 데이터를 읽는 절차

## 참고 문헌

- [1] Signed system volume security — Apple Platform Security Guide. https://support.apple.com/guide/security/signed-system-volume-security-secd698747c9/web
- [4] iOS - Tracking Bundle IDs for Containers, Shared Containers, and Plugins — D20 Forensics (2020-09). https://blog.d204n6.com/2020/09/ios-tracking-bundle-ids-for-containers.html
- [7] A deep dive into the iOS backup/restore system — GitHub Gist (leminlimez). https://gist.github.com/leminlimez/c602c067349140fe979410ef69d39c28
