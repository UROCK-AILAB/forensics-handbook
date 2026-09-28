---
title: "OS 버전과 설치 기록"
parent: "아티팩트 · 시스템·계정"
nav_order: 450
---

# OS 버전과 설치 기록 (SystemVersion·InstallHistory)

`SystemVersion.plist` 에서 이 맥에 설치된 macOS 의 버전과 빌드 번호를 읽고, `InstallHistory.plist` 에서 언제 어떤 패키지와 업데이트를 설치했는지 한 항목씩 따라가며, macOS 13 Ventura 이후에는 Preboot 볼륨의 사본까지 함께 봐야 실제 적용 버전을 맞게 적을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

`/System/Library/CoreServices/SystemVersion.plist` 는 설치된 운영체제를 설명하는 속성 목록 파일 (Property List) 입니다. [2][4] 이 파일에는 버전 번호 `ProductVersion` 과 빌드 번호 `ProductBuildVersion` 이 들어 있습니다. [1][5] 이 핸드북의 다른 페이지가 설명하는 경로·키·형식은 버전마다 달라서, 조사를 시작할 때 OS 버전부터 적어 두고 어떤 설명을 적용할지 이 값으로 정합니다.

`/Library/Receipts/InstallHistory.plist` 에는 설치한 응용 프로그램과 업데이트가 차례로 쌓입니다. [2][4] 항목마다 설치 시각, 표시 이름, 표시 버전, 설치를 한 프로세스 이름, 설치된 패키지 식별자 목록이 들어 있어서 [3], 운영체제 업데이트와 앱 설치를 한 줄의 시간 흐름으로 이어 볼 수 있습니다. 같은 설치 과정의 세부 내용은 설치 로그 `/private/var/log/install.log` 에 따로 남습니다. [2]

OS 설치 시각을 추정할 때 쓰는 파일도 있습니다. macOS 10.9 에서 `/var/db/.AppleSetupDone` 은 빈 파일이고, 이 파일의 마지막 수정 시각이 OS 를 설치한 날짜와 시각을 나타냅니다. [4] 최신 macOS 에서도 같은 뜻인지, 업그레이드 때 이 시각이 바뀌는지는 실제 데이터로 확인해야 합니다.

소프트웨어 업데이트의 마지막 시도와 성공을 적는 `com.apple.SoftwareUpdate.plist` 는 [소프트웨어 업데이트 기록](software-update.md) 페이지가 본문으로 다루고, 설치한 앱 자체와 패키지 영수증은 [설치한 앱과 영수증](installed-apps-receipts.md) 페이지에서 다룹니다.

## 위치와 버전별 차이

| 기록 | 위치 | 알려 주는 것 |
|---|---|---|
| 시스템 볼륨의 버전 파일 | `/System/Library/CoreServices/SystemVersion.plist` | OS 버전·빌드 번호 [1][5] |
| Preboot 볼륨의 버전 파일 (macOS 13 이후) | `/{uuid}/cryptex1/current/SystemVersion.plist` | 빠른 보안 대응 패치 정보와 실제 적용 버전 [5] |
| Update 볼륨의 NVRAM 사본 | `/nvram.plist` | mac_apt 가 버전 판단에 함께 참고하는 파일 [5] |
| 설치 이력 | `/Library/Receipts/InstallHistory.plist` | 설치한 앱과 업데이트 목록 [2][3][4] |
| 설치 로그 | `/private/var/log/install.log` (`/var/log/install.log`) | 설치 과정의 세부 기록 [2] |
| 설치 완료 표시 파일 | `/var/db/.AppleSetupDone` | 수정 시각이 OS 설치 시각 (10.9 기준) [4] |

macOS 13 Ventura 부터는 버전을 한 곳에서만 보면 부족합니다. mac_apt 는 Preboot 볼륨의 `cryptex1/current/SystemVersion.plist` 에서 빠른 보안 대응 (Rapid Security Response) 패치 정보인 `ProductVersionExtra` 를 읽고, 그 파일에 `ProductVersion`·`ProductBuildVersion` 이 있으면 시스템 볼륨에서 읽은 값을 이 값으로 덮어씁니다. [5] 그래서 빠른 보안 대응을 적용한 기기는 시스템 볼륨의 `SystemVersion.plist` 만 볼 때 실제 적용 버전과 다른 값을 적게 될 수 있습니다. 볼륨이 여럿으로 나뉘는 구조는 [볼륨 그룹과 펌링크](../../01-foundations/disk-volume/volume-group-firmlinks.md) 와 [APFS 구조](../../01-foundations/disk-volume/apfs/index.md) 페이지에 있습니다.

버전 번호와 이름은 아래 표처럼 대응합니다. 표는 macOS 15 까지입니다. [5]

| `ProductVersion` 앞자리 | 이름 |
|---|---|
| 10.15 | Catalina |
| 11 | Big Sur |
| 12 | Monterey |
| 13 | Ventura |
| 14 | Sonoma |
| 15 | Sequoia |

## 구조

### SystemVersion.plist

버전을 알려 주는 키는 다음과 같습니다. [5]

| 키 | 뜻 | 값의 예 [5] |
|---|---|---|
| `ProductVersion` | OS 버전 번호 | "10.15.7", "11.0", "13.5" |
| `ProductBuildVersion` | 빌드 번호 | "19H2" |
| `ProductVersionExtra` | 빠른 보안 대응 패치 정보 (Preboot 볼륨 사본에서 읽음) | 실제 데이터에서 확인 |

### InstallHistory.plist

파일 안에는 설치 한 번이 항목 하나로 들어 있고, plaso 의 `install_history` 플러그인은 아래 다섯 키가 모두 있는 항목만 설치 기록으로 봅니다. [3] plist 를 여는 법과 날짜 값의 저장 방식은 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md) 페이지에 있습니다.

| 키 | 뜻 [3] |
|---|---|
| `date` | 이 항목을 적은 시각. plist 날짜형(UTC 기준)이고 plaso 는 이 값을 기록 시각 (written_time) 으로 씁니다 |
| `displayName` | 설치한 대상의 표시 이름 |
| `displayVersion` | 표시 버전 |
| `processName` | 설치를 한 프로세스 이름 |
| `packageIdentifiers` | 이 설치로 들어온 패키지 식별자 목록 |

`processName` 값이 업데이트 데몬인지, 설치 프로그램인지, App Store 인지는 값만 보고 정하지 않습니다. 실제 데이터에서 나온 값을 그대로 적고, 값이 무엇을 뜻하는지는 설치 로그와 맞춰 본 뒤에 씁니다.

## 증거로서 의미

**증명하는 것.** `SystemVersion.plist` 는 이미지를 뜬 시점에 시스템 볼륨에 적힌 OS 버전과 빌드 번호를 알려 주고, macOS 13 이후에는 Preboot 볼륨의 사본과 함께 보면 빠른 보안 대응 패치가 적용되었는지도 알 수 있습니다. [5] `InstallHistory.plist` 의 각 항목은 이 시각에 이 이름과 버전의 대상이 이 프로세스를 거쳐 설치되었다는 기록이고, `packageIdentifiers` 로 어떤 패키지가 함께 들어왔는지 이어 볼 수 있습니다. [3]

**증명하지 못하는 것.** 버전 파일은 현재 상태만 적고 이전 버전을 남기지 않아서, 사고 당시의 OS 버전은 설치 이력과 업데이트 기록에서 거슬러 올라가 맞춰야 합니다. 설치 이력 항목으로는 누가 설치를 시작했는지, 설치한 앱을 실행했는지, 지금도 디스크에 남아 있는지 알 수 없습니다. `.AppleSetupDone` 의 수정 시각이 설치 시각이라는 설명은 10.9 기준이라서, 최신 macOS 이미지에서는 "처음 설치한 시각" 으로 단정하지 않고 다른 기록과 맞춰 본 뒤에 씁니다.

보고서에는 "`InstallHistory.plist` 에 이 시각, `displayName` 이 무엇이고 `processName` 이 무엇인 항목이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`SystemVersion.plist` 의 버전·빌드 번호 키에는 시각 값이 없습니다. [5]

`InstallHistory.plist` 의 `date` 는 plist 날짜형이고, plaso 는 이 값을 항목이 기록된 시각으로 씁니다. [3] plist 날짜형은 UTC 기준이라서([속성 목록 파일](../../01-foundations/data-formats/plist/index.md)) 현지 시각으로 바꿔 적을 때는 기기의 시간대를 따로 적용하고, 날짜 값을 읽는 법은 [맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md) 페이지를 따르며, 같은 설치를 적은 설치 로그의 시각과도 맞춰 봅니다. 기기의 시간대는 [시간대와 시계 설정](time-zone.md) 에서 따로 확인합니다.

`.AppleSetupDone` 은 내용이 없는 파일이라 파일 시스템의 수정 시각만 봅니다. [4] 파일 시스템 시각을 읽는 법은 [APFS 구조](../../01-foundations/disk-volume/apfs/index.md) 페이지에 있습니다.

## 함정과 한계

시스템 볼륨의 `SystemVersion.plist` 하나만 보고 버전을 적으면 틀리기 쉽습니다. macOS 13 이후 이미지는 Preboot 볼륨의 사본까지 확인하고, 도구 결과가 어느 파일에서 나온 값인지 보고서에 함께 적습니다. [5]

설치 이력의 항목 수가 적거나 파일이 없더라도 설치가 없었다고 보지 않습니다. 설치 로그는 가장 오래된 기록의 시각을 보고 어느 시점부터 남아 있는지 확인하고, 앱을 끌어다 놓아 복사하는 방식이 설치 이력에 남는지는 시험 기기에서 재현해 확인합니다. 설치했다고 보이는 앱이 이력에 없으면 [설치한 앱과 영수증](installed-apps-receipts.md) 의 방법으로 앱 폴더와 영수증을 따로 확인합니다.

파일이 사라졌거나 항목 순서와 시각이 설치 로그와 어긋나면 지우거나 손댄 흔적일 수도 있지만, 이 파일 하나로 결론 내리지 않습니다. 이전 내용은 [스냅숏과 백업 비교](../../03-techniques/analysis/snapshot-diff.md) 로 찾아보고, 전체 판단은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 시나리오를 따릅니다.

## 직접 분석해 보기

### 헥스로 한 번

바이너리 plist 는 키 이름을 문자열 객체로 저장해서, 헥스 편집기에서 `ProductVersion` 이나 `displayName` 같은 키 이름을 검색하면 파일 안에 그 키가 있는지부터 확인할 수 있습니다. 키와 값을 잇는 오프셋 표와 날짜 객체를 읽는 절차는 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md) 페이지를 그대로 따릅니다. 헥스로 읽은 `date` 값은 도구 결과와 맞춰 보고, 어긋나면 도구 쪽 해석을 다시 확인합니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

> 그림 자리: 헥스 편집기에서 `InstallHistory.plist` 한 항목의 `date` 키와 이어지는 날짜 객체를 표시한 화면(명세로 만든 예시 파일 기준)

### 공개 도구로 한 번

mac_apt 의 `BASICINFO` 플러그인은 OS 버전·빌드 번호·이름을 한 번에 내고 [1], macOS 13 이후 이미지에서는 앞에서 적은 대로 Preboot 볼륨의 값을 반영합니다. [5] 설치 이력은 plaso 의 `install_history` plist 플러그인으로 타임라인에 넣을 수 있고, 항목마다 표시 이름·버전·프로세스 이름·패키지 식별자가 기록 시각과 함께 나옵니다. [3] 타임라인에 넣는 일반 절차는 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 페이지에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 내용 |
|---|---|
| [소프트웨어 업데이트 기록](software-update.md) | 마지막 업데이트 때의 OS 버전과 지금 버전, 업데이트 시각과 가까운 설치 이력 항목 |
| [설치 로그](../logs/install-log.md) | 설치 이력 항목과 같은 시간대의 설치 과정 기록 |
| [설치한 앱과 영수증](installed-apps-receipts.md) | 설치 이력의 패키지 식별자와 영수증·앱 폴더 |
| [통합 로그에서 찾을 것](../logs/unified-log-events/index.md) | 같은 시간대의 설치·업데이트 관련 이벤트 |
| [시간대와 시계 설정](time-zone.md) | 시각을 현지 시각으로 바꿀 때 쓸 시간대 |

## 실습

공개 시험 자료(NIST CFReDS 등)의 맥 이미지로 다음 질문을 풀어 봅니다.

1. 시스템 볼륨의 `SystemVersion.plist` 에서 `ProductVersion` 과 `ProductBuildVersion` 을 읽고, 위 이름 표로 OS 이름을 적어 봅니다.
2. 이미지가 macOS 13 이후라면 Preboot 볼륨에서 `cryptex1/current/SystemVersion.plist` 를 찾아 `ProductVersionExtra` 가 있는지, 버전 값이 시스템 볼륨과 다른지 확인합니다.
3. `InstallHistory.plist` 의 항목을 시각 순서로 늘어놓고, OS 업데이트로 보이는 항목과 앱 설치로 보이는 항목을 `processName` 과 `packageIdentifiers` 로 나눠 봅니다.
4. 가장 이른 설치 이력 항목의 시각과 `.AppleSetupDone` 의 수정 시각을 비교하고, 둘이 어긋나면 어떤 설명이 가능한지 적어 봅니다.
5. 설치 이력의 한 항목을 골라 같은 시간대의 `install.log` 기록을 찾아 서로 맞는지 봅니다.

## 참고 문헌

1. mac_apt `BASICINFO` 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/basicinfo.py
2. ForensicArtifacts `macos.yaml` (MacOSSystemVersionPlistFile, MacOSInstallationHistoryPlistFile, MacOSInstallationLogFile) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
3. plaso `install_history` plist 플러그인 소스 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/plist_plugins/install_history.py
4. Forensics Wiki, Mac OS X 10.9 artifacts location — https://forensics.wiki/mac_os_x_10.9_artifacts_location/
5. mac_apt `macinfo.py` 헬퍼 소스 (SystemVersion 읽기·OS 이름 대응) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/helpers/macinfo.py
