---
title: "초기화·재설치"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 2420
---

# 초기화·재설치 (Erase·Reinstall)

맥을 초기화하거나 macOS 를 다시 설치했는지, 했다면 언제였고 그 작업으로 사용자 데이터가 실제로 사라졌는지 묻는 조사를 다룹니다. 모든 콘텐츠 및 설정 지우기는 데이터를 지우고 재설치는 데이터를 지우지 않아서, 먼저 기종과 macOS 버전으로 어떤 지우기가 가능했는지 정하고 사건 당시 계정과 홈 폴더가 남았는지 봅니다. 이어서 `InstallHistory.plist` 의 설치 항목과 지금 버전을 비교하고, APFS 볼륨 시각과 utmpx 의 부팅·종료 레코드를 설치 기록 시각과 맞춥니다.

## 조사 질문

맥을 초기화하거나 macOS 를 다시 설치했는지, 했다면 언제였고 그 작업으로 사용자 데이터가 실제로 사라졌는지를 묻습니다. "초기화" 와 "재설치" 는 흔히 한데 묶어 부르지만 사용자 데이터에 주는 영향이 전혀 달라서, 어느 쪽이었는지 가려내는 일이 이 페이지의 중심입니다.

## 먼저 확인할 것

먼저 기종과 macOS 버전을 확인합니다. "모든 콘텐츠 및 설정 지우기 (Erase All Content and Settings)" 는 macOS Monterey 12 이상에서, 그리고 Apple silicon 맥이나 Apple T2 보안 칩이 있는 맥에서만 쓸 수 있고, 조건이 맞지 않는 맥은 팔거나 넘기기 전에 할 일을 안내한 별도 문서의 절차를 따릅니다 [1]. 그래서 기종과 버전을 알면 어떤 방식의 지우기가 가능했는지부터 좁혀집니다. 기종과 버전을 읽는 곳은 [컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)](../../../02-artifacts/system-account/computer-name-hardware.md)와 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../../../02-artifacts/system-account/os-version-install-history.md)에 있습니다.

다음으로 사건 당시 쓰던 사용자 계정이 지금도 있는지, 그리고 확보본에 시스템 볼륨과 데이터 볼륨, Preboot 볼륨이 모두 들어 있는지 확인합니다. 볼륨 구성은 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../../../01-foundations/disk-volume/volume-group-firmlinks.md)에 있습니다.

## 초기화와 재설치의 차이

| 작업 | 사용자 데이터·앱 | macOS | 조건 |
|---|---|---|---|
| 모든 콘텐츠 및 설정 지우기 | 데이터·설정·앱을 지움 [1] | 설치된 macOS 를 그대로 둠 [1] | macOS 12 이상, Apple silicon 또는 T2 [1] |
| macOS 복구에서 재설치 | 앱과 개인 데이터를 지우지 않음 [2] | 다시 설치 | macOS 복구로 시동 [2] |
| 디스크 유틸리티로 시동 디스크 지우기 | 재설치와는 별도 절차 [2] | — | — |

모든 콘텐츠 및 설정 지우기를 진행하면 macOS 로그인 암호와 Apple 계정 암호를 입력하고, 지운 뒤 맥이 재시작하고 블루투스 액세서리 연결이나 Wi-Fi 선택을 요청할 수 있으며, 이어서 맥이 활성화된 뒤 한 번 더 재시작해 처음 설정하는 것처럼 설정 지원 (Setup Assistant)이 나옵니다 [1]. 암호화 구조는 [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md)에 있습니다.

재설치는 앱과 개인 데이터를 지우지 않으므로 [2], 재설치 기록만으로 증거를 없앴다고 판단할 수 없습니다. 복구에서 받는 macOS 버전은 기종과 시동 방식에 따라 달라서 [2], 재설치 뒤의 버전을 볼 때 아래 표를 참고합니다. Apple silicon 맥이라도 업그레이드 뒤에 디스크 유틸리티로 디스크를 지웠다면 이전에 쓰던 버전이 설치될 수 있습니다 [2].

| 기종 | 복구 시동 방식 | 설치되는 버전 [2] |
|---|---|---|
| Apple silicon | macOS 복구 | 가장 최근에 설치했던 macOS 의 현재 버전 |
| 그 밖의 맥 | Command-R | 가장 최근에 설치했던 macOS 의 현재 버전 |
| 그 밖의 맥 | Option-Command-R | 호환되는 최신 macOS |
| 그 밖의 맥 | Shift-Option-Command-R | 출하 때 macOS 또는 가장 가까운 버전 |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | `/Library/Receipts/InstallHistory.plist` | macOS·앱 설치 기록과 시각 [3] | [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../../../02-artifacts/system-account/os-version-install-history.md) |
| 2 | `/System/Library/CoreServices/SystemVersion.plist` | 지금 설치된 macOS 버전·빌드 [4] | [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../../../02-artifacts/system-account/os-version-install-history.md) |
| 3 | `/Library/Preferences/SystemConfiguration/preferences.plist` | 모델명, 호스트 이름, 컴퓨터 이름 [4] | [컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)](../../../02-artifacts/system-account/computer-name-hardware.md) |
| 4 | `/Library/Preferences/com.apple.loginwindow.plist` | 마지막 사용자, 첫 로그인 계정 [4] | [로그인 창 설정 (loginwindow)](../../../02-artifacts/system-account/loginwindow.md) |
| 5 | APFS 컨테이너·볼륨 속성 | 볼륨 생성·갱신 시각 [4] | [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md) |
| 6 | `/System/Volumes/Preboot/{uuid}/restore/BuildManifest.plist` | 인텔·Apple silicon 구분 [4] | 아래 분석 흐름 |
| 7 | `/private/var/run/utmpx` | 부팅·종료 레코드 [5] | [시스템 시각 바꾸기 (Time Change)](time-change.md) |
| 8 | 설치 로그 | 설치 과정의 텍스트 기록 | [설치 로그 (install.log)](../../../02-artifacts/logs/install-log.md) |

InstallHistory.plist 의 항목마다 `contentType`, `date`, `displayName`, `displayVersion`, `packageIdentifiers`, `processName` 키가 있고, `date` 는 날짜 값입니다 [3]. 이 시각을 다른 기록과 맞출 때는 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../../../02-artifacts/system-account/os-version-install-history.md)의 설명을 따릅니다.

loginwindow.plist 에서는 `autoLoginUser`, `GuestEnabled`, `lastUserName`, `lastUser`, `lastLoginPanic`, `AccountInfo/FirstLogins`, `AccountInfo/MaximumUsers`, `AccountInfo/OnConsole` 을 읽고, `lastLoginPanic` 은 맥 절대 시각에서 변환합니다 [4]. 사건 당시 쓰던 계정이 `AccountInfo/FirstLogins` 나 마지막 사용자에 보이지 않으면 계정 구성이 바뀌었을 가능성을 봅니다.

Preboot 볼륨의 `BuildManifest.plist` 에서 `BuildIdentities[0]/Manifest` 안에 `x86,SystemVolume` 키가 있으면 인텔 맥이고, 없으면 `RestoreRamDisk` 의 `Info/Path` 값에 `arm64` 가 들어 있는지로 Apple silicon 인지를 판별합니다 [4]. 이 결과는 지금 확보본이 어떤 기종에서 나왔는지 확인해 모든 콘텐츠 및 설정 지우기가 가능한 기종이었는지 판단할 때 씁니다.

## 분석 흐름

1. 기종과 macOS 버전을 확인해 모든 콘텐츠 및 설정 지우기가 가능했던 맥인지 정합니다.
2. 사건 당시 쓰던 사용자 계정과 홈 폴더가 남아 있는지 확인합니다. 계정과 데이터가 그대로 있으면 재설치만 했거나 초기화하지 않았을 가능성이 크고, 계정이 모두 새로 만들어진 모습이면 초기화 가능성을 계속 따라갑니다.
3. InstallHistory.plist 에서 macOS 설치 항목의 날짜와 버전을 차례로 읽고, 사건 시점 전후에 macOS 설치 항목이 있는지 봅니다. 기록이 짧다는 사실만으로 초기화를 단정하지 않습니다.
4. 지금 macOS 버전을 설치 기록의 마지막 macOS 항목과 비교하고, 복구 시동 방식별 설치 버전 표와 어긋나지 않는지 봅니다.
5. APFS 볼륨 시각을 읽어 설치 기록의 시각과 비교합니다. 볼륨마다 생성 시각 (Created Time)과 갱신 시각 (Updated Time)이 있습니다 [4]. 볼륨 생성 시각이 지우기나 재설치 시점을 가리킨다는 해석이 있지만, 지우기나 재설치 때 이 값이 새로 정해지는지는 알려져 있지 않아 보조 근거로만 씁니다.
6. utmpx 의 BOOT_TIME(2)·SHUTDOWN_TIME(11) 레코드로 부팅·종료 시각을 보고 [5], 설치 기록 시각과 이어지는지 확인합니다. 초기화 뒤에도 이 레코드가 남는지는 실제 데이터로 확인합니다.
7. 사용자 데이터가 남아 있는 경우에는 데이터가 남은 범위를, 사라진 경우에는 [타임 머신 (Time Machine)](../../../02-artifacts/filesystem/time-machine/index.md)이나 아이클라우드처럼 맥 밖에 남은 사본을 찾아 확인합니다.

## 흔한 오판

가장 흔한 오판은 재설치 기록을 보고 "증거를 없앴다" 고 쓰는 경우입니다. 재설치는 앱과 개인 데이터를 지우지 않으므로 [2], 재설치 기록은 "이 시각에 macOS 를 다시 설치한 기록이 있다" 까지만 말하고 데이터 삭제는 따로 확인합니다.

반대로 모든 콘텐츠 및 설정 지우기를 거친 맥이라면 macOS 가 그대로 남아 있어서 [1] 시스템 파일만 보면 초기화 흔적이 드러나지 않을 수 있습니다. 설치 기록에 새 macOS 설치 항목이 없다고 해서 지우지 않았다고 보지 말고, 사용자 계정과 데이터가 남은 모습을 함께 봅니다.

초기화 흔적을 찾았을 때 그 시각을 곧바로 사건과 잇는 것도 조심합니다. 기기를 팔거나 넘기려고 초기화하는 경우도 있어서, 초기화 시각이 사건 시점과 어떤 순서에 있는지와 다른 기록에 무엇이 나와 있는지를 함께 적습니다.

## 보고서 문장 예

- "InstallHistory.plist 에 YYYY-MM-DD 날짜로 macOS 설치 항목이 기록돼 있고, 같은 날짜 이전에 만든 사용자 계정의 홈 폴더가 남아 있습니다. 이 기록은 macOS 재설치와 들어맞지만 사용자 데이터를 지웠다는 근거는 아닙니다."
- "확보본의 사용자 계정은 모두 YYYY-MM-DD 이후에 처음 로그인한 기록만 있고, 이 맥은 모든 콘텐츠 및 설정 지우기를 쓸 수 있는 기종입니다. 이 시점에 기기를 초기화했을 가능성이 있으나 직접 기록은 찾지 못했습니다."

## 함께 볼 페이지

- [증거를 없애려 했나 (Anti-Forensics)](index.md) — 이 허브의 다른 수단과 전체 흐름
- [삭제 도구 (Wiping Tools)](wiping-tools.md) — 디스크나 볼륨을 덮어써 지운 경우
- [사용자 계정 (Local Accounts)](../../../02-artifacts/system-account/user-accounts/index.md) — 계정이 언제 만들어졌는지 볼 때
- [소프트웨어 업데이트 기록 (Software Update)](../../../02-artifacts/system-account/software-update.md) — 설치 기록의 macOS 항목이 업데이트인지 볼 때
- [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../../03-techniques/analysis/snapshot-diff.md) — 초기화 전 사본과 지금을 견줄 때

## 참고 문헌

1. Apple Support — Erase your Mac (Erase All Content and Settings), 102664 — https://support.apple.com/en-us/102664
2. Apple Support — How to reinstall macOS, 102655 — https://support.apple.com/en-us/102655
3. mac_apt `plugins/installhistory.py` — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/installhistory.py
4. mac_apt `plugins/basicinfo.py` — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/basicinfo.py
5. mac_apt `plugins/utmpx.py` (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/utmpx.py
