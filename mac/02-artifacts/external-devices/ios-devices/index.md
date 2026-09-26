---
title: "아이폰·아이패드 연결"
parent: "아티팩트 · 외부 장치"
nav_order: 1090
has_children: true
has_toc: false
---

# 아이폰·아이패드 연결 (iOS Devices)

아이폰·아이패드를 맥에 연결하고 신뢰하면 맥에는 크게 두 가지 흔적이 남는데, 시스템 폴더 `/var/db/lockdown` 의 페어링 기록과 사용자 홈 `~/Library/Application Support/MobileSync/Backup/` 의 기기 백업입니다 [1][2].

## 왜 중요한가

기기가 컴퓨터를 신뢰하면 그 컴퓨터는 기기와 동기화하고 사진·동영상·연락처 같은 콘텐츠에 접근할 수 있고, 이 신뢰는 사용자가 신뢰 목록을 바꾸거나 기기를 지우기 전까지 이어집니다 [3]. 그래서 어떤 기기가 이 맥을 신뢰했는지는 맥과 기기 사이에 데이터가 오갈 수 있었는지를 따지는 출발점이 됩니다.

두 흔적은 알려 주는 것이 다릅니다. 페어링 기록은 이 맥과 짝을 맺은 기기의 UDID를 알려 주지만 맥 전체에 하나라서 사용자 계정을 구분해 주지 않고, 기기 백업은 사용자 계정마다 따로 남아 어느 계정에서 어떤 기기를 언제 마지막으로 백업했는지와 기기 안 파일의 사본까지 담습니다 [1][2][5]. 두 기록을 UDID로 이으면 같은 기기로 묶을 수 있어서 [4][5], 기기 한 대를 두고 "이 맥과 페어링했고, 이 계정에서 백업됐다" 까지 좁힐 수 있습니다.

## 한눈에 보기

| 항목 | 페어링 기록 | 기기 백업 |
|---|---|---|
| 위치 | `/var/db/lockdown` [1] | `~/Library/Application Support/MobileSync/Backup/` [2] |
| 범위 | 맥 전체에 하나 [1] | 사용자 계정마다 따로 [2] |
| 형태 | 기기마다 `<UDID>.plist` 하나 [4] | 기기 UDID 이름의 폴더 안에 plist 파일 [5]과 `Manifest.db`, 파일 사본 |
| macOS 버전 | 버전별 차이에 대한 공개 자료 없음 | macOS 10.15 Catalina 이후는 Finder, 10.14 Mojave 이전은 iTunes로 백업하고 관리함 [6]. 위치는 같은 경로 [2] |
| 알려 주는 것 | 이 맥과 페어링한 기기의 UDID, 인증서와 키 | 기기 식별값, 마지막 백업 시점, 백업 완료 여부, 설치 앱 목록, 파일 사본 |
| 알려 주지 않는 것 | 페어링 시각, 연결한 사용자 계정 | 백업을 실행한 사람, 백업 이후의 기기 상태 |

## 읽는 순서

1. [페어링 기록 (Lockdown)](lockdown.md) — `/var/db/lockdown` 폴더의 파일 구성과 키, 신뢰의 뜻, 개인 키를 민감 자료로 다루는 법, 기기 쪽 신뢰 초기화와의 관계를 다룹니다.
2. [기기 백업 (MobileSync)](mobilesync.md) — 백업 폴더의 `Info.plist`·`Status.plist`·`Manifest.plist`·`Manifest.db` 구조와 암호화 여부 확인, 마지막 백업 시점, 페어링 기록과 UDID로 맞춰 보는 방법을 다룹니다.

## 함께 볼 페이지

- [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md) — 페어링 기록과 백업의 plist 파일을 읽을 때
- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) — 백업의 `Manifest.db` 를 읽을 때
- [USB 저장 장치 (USB Storage)](../usb/index.md) — 다른 외장 장치 연결 기록과 함께 볼 때
- [사용자 계정 (Local Accounts)](../../system-account/user-accounts/index.md) — 백업이 어느 계정 홈에 있는지 확인할 때
- [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md) — 기기 연결 시각을 다른 기록에서 찾을 때
- [암호화된 증거 다루기 (Encrypted Evidence)](../../../03-techniques/analysis/encrypted-evidence/index.md) — 암호화 백업을 만났을 때
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) — 백업 시점을 다른 기록과 한 시간축에 놓을 때
- [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)

## 참고 문헌

1. libimobiledevice/usbmuxd README — https://github.com/libimobiledevice/usbmuxd
2. Apple Support — Locate backups of your iPhone, iPad, and iPod touch — https://support.apple.com/en-us/108809
3. Apple Support — About the "Trust This Computer" alert on your iPhone, iPad, or iPod touch — https://support.apple.com/en-us/109054
4. libimobiledevice 소스 common/userpref.c — https://raw.githubusercontent.com/libimobiledevice/libimobiledevice/master/common/userpref.c
5. libimobiledevice 소스 tools/idevicebackup2.c — https://raw.githubusercontent.com/libimobiledevice/libimobiledevice/master/tools/idevicebackup2.c
6. Apple Support — How to back up your iPhone or iPad with your Mac — https://support.apple.com/en-us/108796
