---
title: "설치한 앱과 영수증"
parent: "아티팩트 · 시스템·계정"
nav_order: 540
---

# 설치한 앱과 영수증 (Applications·Receipts)

`/Applications` 폴더의 앱 번들, 설치 프로그램이 남기는 패키지 영수증, `InstallHistory.plist` 의 설치 이력을 함께 맞춰 보면 이 맥에 어떤 앱이 있었고 그중 어떤 것이 패키지로 설치되었는지 가려낼 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

맥에서 앱은 흔히 `/Applications` 폴더 아래에 번들 하나로 놓입니다. [1][4] 조사에서는 이 폴더에서 원격 제어 도구, 파일 전송 도구, 알려진 악성 앱처럼 사건과 이어질 수 있는 앱을 먼저 찾고, 그 앱이 언제 어떻게 들어왔는지를 설치 기록으로 거슬러 올라갑니다.

설치 프로그램 (Installer) 이 패키지를 설치하면 영수증 (receipt) 이 남습니다. `pkgutil` 명령은 macOS 설치 프로그램의 플랫 패키지 (flat package) 를 읽고 다루며, 설치 프로그램이 쓰는 영수증 데이터베이스를 조회합니다. [3] 영수증에는 패키지 식별자와 그 패키지로 설치된 파일 목록이 남아서, 디스크에 흩어진 파일이 어느 패키지에서 왔는지 이을 수 있습니다. [3]

같은 설치는 `/Library/Receipts/InstallHistory.plist` 에도 한 항목으로 쌓이고 [1][4], 그 파일의 키와 해석은 [OS 버전과 설치 기록](os-version-install-history.md) 페이지가 본문으로 다룹니다. 설치 과정의 세부 기록은 [설치 로그](../logs/install-log.md) 페이지에 있습니다.

## 위치와 버전별 차이

| 기록 | 위치 | 알려 주는 것 |
|---|---|---|
| 앱 폴더 | `/Applications/*` | 이미지 확보 시점에 있던 앱 번들 [1][4] |
| 패키지 영수증 데이터베이스 | 위치는 공개 자료 없음. `pkgutil` 로 조회 | 설치된 패키지 식별자, 패키지별 설치 파일 목록 [3] |
| 설치 이력 | `/Library/Receipts/InstallHistory.plist` | 설치 시각, 표시 이름, 패키지 식별자 [1][2][4] |
| 설치 로그 | `/private/var/log/install.log` | 설치 과정의 세부 기록 [1] |

영수증을 저장하는 파일과 디렉터리는 바뀔 수 있어서, 조회와 수정은 늘 `pkgutil` 로 합니다. [3] 영수증 파일이 실제로 놓이는 자리와 그 안의 키, 예전 macOS 에서 쓰던 영수증 방식, App Store 로 설치한 앱의 영수증은 공개 자료가 없습니다. 그래서 영수증은 `pkgutil` 로 읽고, 영수증 파일의 경로는 검체에서 찾은 자리를 그대로 적습니다.

사용자 홈 폴더 아래의 앱 폴더와 운영체제가 기본으로 넣는 앱의 위치, macOS 버전에 따른 차이는 검체에서 확인합니다. 앱 폴더를 볼 때는 `/Applications` 한 곳에서 끝내지 않고, 이미지 전체에서 번들 이름으로 검색해 다른 자리에 놓인 앱이 있는지 확인합니다.

## 구조

### 앱 번들

앱 번들은 폴더 하나로 된 묶음이고, 번들 안의 정보 파일과 서명은 [앱 번들 정보](../embedded-metadata/app-bundle.md) 페이지가, 번들 ID 를 읽는 법은 [번들 ID와 팀 ID](../../01-foundations/value-decoding/bundle-team-id.md) 페이지가 다룹니다.

### 영수증 데이터베이스를 읽는 pkgutil 옵션

`pkgutil` 에서 영수증을 조회하는 옵션은 다음과 같습니다. [3]

| 옵션 | 동작 |
|---|---|
| `--pkgs` | 지정한 볼륨에 설치된 모든 패키지 식별자를 나열 |
| `--pkg-info` 패키지 식별자 | 그 패키지의 확장 정보를 출력 |
| `--pkg-info-plist` 패키지 식별자 | 위와 같은 정보를 plist 로 출력 |
| `--files` 패키지 식별자 | 그 패키지로 설치된 모든 파일을 나열 |
| `--export-plist` 패키지 식별자 | 그 패키지의 모든 영수증 정보를 plist 로 출력 |
| `--volume` 경로 | 지정한 볼륨이나 홈 디렉터리를 대상으로 동작 |
| `--forget` 패키지 식별자 | 설치된 파일은 두고 영수증 데이터만 지움 |

`--volume` 은 이미지를 마운트해 볼 때 대상 볼륨을 정하는 데 쓸 수 있습니다. [3] `--forget` 은 영수증을 지우는 옵션이라 조사 중에는 쓰지 않고, 아래 함정 절에서 보듯 영수증이 없는 까닭을 따질 때 알아 둡니다.

패키지 안에 들어 있는 BOM (Bill of Materials) 파일은 그 패키지가 설치하는 파일 목록을 담습니다. [3] `--files` 로 나오는 목록과 디스크에 실제로 있는 파일을 맞춰 보면, 패키지로 들어온 파일 가운데 나중에 지워지거나 바뀐 파일을 찾을 수 있습니다.

## 증거로서 의미

**증명하는 것.** `/Applications` 에 번들이 있으면 이미지를 뜬 시점에 그 앱이 디스크에 있었다는 기록입니다. 영수증 데이터베이스에 패키지 식별자가 있으면 그 패키지가 설치 프로그램을 거쳐 설치되었다는 기록이고, `--files` 목록은 그 패키지로 어떤 파일이 들어왔는지 보여 줍니다. [3] `InstallHistory.plist` 에 같은 패키지 식별자가 있으면 설치 시각과 설치를 한 프로세스까지 이어 볼 수 있습니다. [2]

**증명하지 못하는 것.** 앱이 폴더에 있다는 사실은 그 앱을 실행했다는 뜻이 아니고, 누가 설치했는지도 알려 주지 않습니다. 실행 여부는 [어떤 앱을 언제 썼나](../../04-scenarios/activity/app-usage.md) 시나리오의 기록으로 따로 확인합니다. 영수증이 없다고 해서 설치가 없었다고 볼 수도 없습니다. `pkgutil --forget` 은 설치된 파일은 그대로 두고 영수증 데이터만 지우기 때문에 [3], 영수증이 없는 앱은 파일 자체와 `InstallHistory.plist`, 설치 로그를 함께 봐야 합니다. 앱을 폴더로 끌어다 놓는 방식의 설치가 영수증이나 설치 이력에 남는지는 공개 자료가 없어 검체로 확인해야 합니다.

보고서에는 "`/Applications` 에 이 번들이 있고, 영수증 데이터베이스에 이 패키지 식별자가 있으며, `InstallHistory.plist` 의 이 시각 항목에 같은 식별자가 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

앱 번들과 그 안의 파일에는 파일 시스템 시각이 붙지만, 이 시각이 설치한 시각과 같다는 근거는 없습니다. 번들을 복사하거나 압축을 풀 때 원래 시각이 따라올 수도 있다고 보고, 파일 시스템 시각은 [APFS 구조](../../01-foundations/disk-volume/apfs/index.md) 페이지의 방법으로 읽되 설치 시각은 `InstallHistory.plist` 의 `date` 와 설치 로그에서 찾습니다. `pkgutil --pkg-info` 가 내는 확장 정보에 어떤 시각 값이 들어가는지는 검체에서 직접 출력해 확인합니다.

설치 시각을 현지 시각으로 바꾸는 기준은 [시간대와 시계 설정](time-zone.md) 에서 확인합니다.

## 함정과 한계

분석 컴퓨터에서 이미지를 마운트해 볼 때 `--volume` 을 빼면 결과가 어느 볼륨에서 나왔는지 가리기 어렵습니다. `--volume` 으로 대상 볼륨을 밝히고, 결과에 어느 볼륨을 읽었는지 함께 적습니다. [3] 영수증 데이터를 바꾸는 `--forget` 은 조사 중에 쓰지 않습니다.

영수증 저장 위치는 바뀔 수 있어서 [3], 특정 경로를 가정하고 영수증을 읽는 도구는 macOS 버전에 따라 영수증을 놓칠 수 있습니다. 도구가 영수증을 못 찾았다고 보고하면 `pkgutil` 결과와 맞춰 보고, 도구 쪽 가정을 [도구 검증](../../03-techniques/reporting/tool-validation.md) 의 방법으로 확인합니다.

앱이 사라진 뒤에도 영수증이나 설치 이력은 남아 있을 수 있고, 거꾸로 영수증만 지워졌을 수도 있습니다. 세 기록이 서로 맞지 않으면 지우거나 손댄 흔적일 수도 있지만 한 기록만으로 결론 내리지 않고, 이전 상태는 [스냅숏과 백업 비교](../../03-techniques/analysis/snapshot-diff.md) 로 찾아보며, 전체 판단은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 시나리오를 따릅니다.

## 직접 분석해 보기

### 헥스로 한 번

영수증 파일의 위치와 형식은 공개 자료가 없어서, 헥스로 따라가는 단계는 `InstallHistory.plist` 로 합니다. 헥스 편집기에서 `packageIdentifiers` 키 문자열을 찾고, 이어지는 배열에서 패키지 식별자 문자열을 읽는 절차는 [속성 목록 파일](../../01-foundations/data-formats/plist/index.md) 페이지를 따릅니다. 여기서 읽은 식별자를 아래 `pkgutil --pkgs` 결과와 맞춰 봅니다.

> 그림 자리: 헥스 편집기에서 `InstallHistory.plist` 의 `packageIdentifiers` 배열과 식별자 문자열을 표시한 화면(명세로 만든 예시 파일 기준)

### 공개 도구로 한 번

macOS 분석 컴퓨터에서 이미지를 읽기 전용으로 마운트한 뒤 `pkgutil` 로 영수증을 읽습니다. [3] 아래는 순서를 보여 주는 예이고, 마운트 경로와 패키지 식별자는 검체에 맞게 바꿉니다.

```sh
pkgutil --volume "/Volumes/<마운트한 볼륨>" --pkgs
pkgutil --volume "/Volumes/<마운트한 볼륨>" --pkg-info-plist "<패키지 식별자>"
pkgutil --volume "/Volumes/<마운트한 볼륨>" --files "<패키지 식별자>"
```

`--pkgs` 로 전체 목록을 뽑고, 사건과 관련 있어 보이는 식별자마다 `--pkg-info-plist` 와 `--files` 결과를 저장해 둡니다. 설치 이력은 plaso 의 `install_history` plist 플러그인으로 타임라인에 넣어 영수증 목록과 맞춰 볼 수 있습니다. [2] 타임라인에 넣는 일반 절차는 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 페이지에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 내용 |
|---|---|
| [OS 버전과 설치 기록](os-version-install-history.md) | 영수증의 패키지 식별자와 설치 이력 항목, 설치 시각 |
| [설치 로그](../logs/install-log.md) | 같은 패키지의 설치 과정 기록 |
| [앱 번들 정보](../embedded-metadata/app-bundle.md) | 번들 식별자·버전·서명 |
| [격리 속성과 다운로드 기록](../filesystem/quarantine/index.md) | 앱이나 설치 패키지를 어디서 내려받았는지 |
| [실행 정책 평가 기록](../execution/execpolicy-gatekeeper.md) | 처음 실행할 때 보안 검사를 거쳤는지 |
| [소프트웨어 업데이트 기록](software-update.md) | 앱 업데이트로 들어온 패키지 |

## 실습

공개 검체(NIST CFReDS 등)의 맥 이미지로 다음 질문을 풀어 봅니다.

1. `/Applications` 의 앱 번들을 모두 적고, 운영체제 기본 앱이 아닌 것으로 보이는 앱을 골라 봅니다.
2. 이미지를 마운트해 `pkgutil --volume ... --pkgs` 로 패키지 식별자 목록을 뽑고, 1번의 앱과 이어지는 식별자를 찾아봅니다.
3. 그 식별자로 `--files` 목록을 뽑아 디스크에 실제로 있는 파일과 맞춰 보고, 사라진 파일이 있는지 확인합니다.
4. `InstallHistory.plist` 에서 같은 식별자가 들어간 항목을 찾아 설치 시각과 `processName` 을 적어 봅니다.
5. 앱 폴더에는 있는데 영수증과 설치 이력에 모두 없는 앱이 있다면, 어떻게 들어왔을지 격리 속성과 다운로드 기록으로 따져 봅니다.

## 참고 문헌

1. ForensicArtifacts `macos.yaml` (MacOSApplicationsDirectory, MacOSInstallationHistoryPlistFile, MacOSInstallationLogFile) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
2. plaso `install_history` plist 플러그인 소스 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/plist_plugins/install_history.py
3. pkgutil(1) man 페이지 (Xcode man pages 모음) — https://keith.github.io/xcode-man-pages/pkgutil.1.html
4. Forensics Wiki, Mac OS X 10.9 artifacts location — https://forensics.wiki/mac_os_x_10.9_artifacts_location/
