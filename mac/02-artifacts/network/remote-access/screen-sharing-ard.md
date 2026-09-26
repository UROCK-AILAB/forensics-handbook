---
title: "화면 공유와 원격 관리"
parent: "원격 접속"
grand_parent: "아티팩트 · 네트워크"
nav_order: 1640
---

# 화면 공유와 원격 관리 (Screen Sharing·ARD)

화면 공유 (Screen Sharing) 앱은 사용자 컨테이너 안의 plist에 연결했던 상대의 주소·로그인 이름·마지막 연결 날짜를 남기고, 원격 관리 (Apple Remote Desktop, ARD)는 관리하는 맥과 관리받는 맥의 `/private/var/db/RemoteManagement/` 아래에 DB와 캐시 파일을 남깁니다.

## 무엇을 기록하나 · 왜 생기나

화면 공유와 원격 관리는 다른 맥의 화면을 보거나 조작하는 기능이고, 받는 쪽 맥에서는 시스템 설정의 공유 화면에서 켭니다. 켜는 곳은 [원격 접속 (Remote Access)](index.md) 허브에 정리했습니다.

이 페이지가 다루는 흔적은 세 가지입니다. 첫째는 화면 공유 앱의 연결 기록이고, 이 파일에는 상대의 IP 주소, 호스트 이름, 로그인 사용자 이름, 그룹 이름, 마지막 연결 날짜가 들어 있습니다 [1]. 둘째는 ARD 파일입니다. ARD 는 2002년에 처음 나왔고, ForensicArtifacts 에는 관리하는 쪽(`MacOSRemoteDesktopAdministratorSystem`)과 관리받는 쪽(`MacOSRemoteDesktopClientSystem`) 두 정의로 나뉘어 있습니다 [2]. 셋째는 원격 관리 설정을 명령줄에서 바꾸는 kickstart 도구이고, 이 페이지에서는 사용법이 아니라 실행된 흔적을 찾을 때 쓸 이름과 문자열만 다룹니다 [3].

## 위치와 버전별 차이

| 흔적 | 경로 | 있는 맥 | 근거 |
|---|---|---|---|
| 화면 공유 연결 기록 | `~/Library/Containers/com.apple.ScreenSharing/Data/Library/Preferences/com.apple.ScreenSharing.plist` | 화면 공유 앱을 쓴 사용자의 홈 | [1] |
| ARD 정의(관리하는 쪽) | `/private/var/db/RemoteManagement/ClientCaches/*` | 관리하는 맥 | [2] |
| ARD 정의(관리하는 쪽) | `/private/var/db/RemoteManagement/RMDB/rmdb.sqlite3` | 관리하는 맥 | [2] |
| ARD 정의(관리받는 쪽) | `/private/var/db/RemoteManagement/caches/AppUsage.plist` | 관리받는 맥 | [2] |
| ARD 정의(관리받는 쪽) | `/private/var/db/RemoteManagement/caches/UserAcct.tmp` | 관리받는 맥 | [2] |
| kickstart 도구 | `/System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart` | 도구가 들어 있는 맥 | [3] |

ARD 경로는 `/var/db/RemoteManagement/...` 형태로도 나타납니다 [2]. 사용자마다 홈이 따로 있어서 화면 공유 연결 기록은 계정 수만큼 찾아봅니다.

이 plist 구조가 어느 macOS 버전부터 쓰였는지는 공개된 자료가 없습니다. Apple 의 kickstart 안내에는 macOS Mojave 10.14 이후에 관한 내용이 있지만 [3], 최근 버전에서 kickstart만으로 원격 관리를 켤 수 있는지 같은 제한은 실제 기기에서 확인합니다. 경로가 보이면 그 기기의 macOS 버전을 함께 적습니다.

## 구조

### 화면 공유 연결 기록

mac_apt 플러그인이 읽는 키와 뽑아내는 필드는 아래와 같습니다 [1]. `connectionsStore` 는 값 안에 plist가 다시 들어 있어서 한 번 더 풀어야 읽을 수 있고, 그 안의 `connectionDetails` 와 `sessionMetadatas` 는 연결 상대마다 붙은 UUID를 키로 삼아 같은 상대의 항목을 서로 잇습니다.

| 플러그인이 읽는 키 | 담긴 것 | 플러그인 출력 필드 |
|---|---|---|
| `connectionsStore` | 안에 plist가 한 번 더 들어 있는 값 | — |
| `connectionDetails` 의 키 | 연결 상대의 UUID | `Host_UUID` |
| `connectionDetails` → (UUID) → `connectionParameters` → `networkAddress` → `_0` → `address` | 연결한 상대의 주소 | `Address` |
| 같은 `_0` 아래의 `username` | 로그인에 쓴 사용자 이름 | `Login_Username` |
| 같은 `_0` 아래의 `displayName` | 목록에 보이는 이름 | `Display_Name` |
| `connectionGroups` → (그룹 UUID) → `groupName`, `members` | 그룹 이름과 그 그룹에 든 상대 UUID | `Groups` |
| `sessionMetadatas` → (UUID) → `lastConnectedDate` | 마지막 연결 날짜 | `Last_Connection_Date` |

출력의 `Source` 필드에는 plist 값이 아니라 읽은 파일의 경로가 들어갑니다 [1]. 도구 결과를 보고서에 옮길 때는 원본 plist의 값과 한 번 맞춰 봅니다. plist 형식 자체를 읽는 법은 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에 있습니다.

### ARD 파일

`rmdb.sqlite3` 의 표와 열, `AppUsage.plist` 와 `UserAcct.tmp` 의 키와 내용, 시각 기준은 공개된 분석 자료가 없습니다. 이름으로 짐작해 열의 뜻을 붙이지 말고, 표 목록과 열 이름을 그대로 뽑아 기록한 뒤 같은 기기의 다른 기록과 맞춰 뜻을 확인합니다. SQLite 파일을 다루는 법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md)에 있습니다.

### kickstart 옵션 이름

kickstart 옵션 이름은 `-activate`, `-configure`, `-deactivate`, `-access`, `-privs`, `-allowAccessFor`, `-allUsers`, `-restart -agent`, `-help` 입니다 [3]. `-allowAccessFor` 옵션만은 다른 kickstart 옵션과 함께 쓸 수 없습니다 [3]. 셸 기록이나 프로세스 실행 기록에서 이 도구 경로나 옵션 이름을 찾으면 원격 관리 설정을 바꾸려 한 흔적으로 봅니다.

## 증거로서 의미

### 증명하는 것

화면 공유 연결 기록에 항목이 있으면 그 사용자 계정의 화면 공유 앱 설정에 이 주소와 로그인 이름으로 된 연결 항목이 저장되어 있고, 마지막 연결 날짜가 이렇게 적혀 있다고 말할 수 있습니다 [1]. 그룹 이름과 구성원이 있으면 어느 연결 항목이 같은 그룹에 묶여 있었는지도 알 수 있습니다.

ARD 파일이 있으면 관리하는 쪽 또는 관리받는 쪽 파일이 그 맥에 있다는 사실을 말할 수 있고 [2], 그 맥이 어느 쪽 역할로 쓰였는지 판별할 출발점이 됩니다. kickstart 경로나 옵션 이름이 실행 기록에 있으면 원격 관리 설정을 바꾸는 도구가 실행된 기록이 있다고 쓸 수 있습니다 [3].

### 증명하지 못하는 것

플러그인이 뽑는 시각은 마지막 연결 날짜 하나라서 그 전에 몇 번, 언제 연결했는지는 이 파일만으로 알 수 없습니다 [1]. 이 항목이 이 맥에서 다른 컴퓨터로 건 연결만 담는지는 공개된 자료가 없습니다. 파일이 화면 공유 앱의 컨테이너에 있으니 이 사용자가 앱으로 접속한 상대 목록으로 읽는 편이 자연스럽지만, 실제 기기에서 확인하기 전에는 이 맥으로 들어온 연결의 증거로 쓰지 않습니다. 연결 항목이 있다는 것만으로 인증에 성공했는지, 화면을 보기만 했는지 조작했는지도 알 수 없습니다.

kickstart 실행 흔적은 설정을 바꾸려 했다는 기록일 뿐이고, 설정이 실제로 바뀌었는지 보여 주는 plist나 로그 문구는 실제 기기에서 확인해야 합니다. 계정에 기록이 있다고 해서 그 계정 주인이 직접 연결했다고 단정할 수도 없어서, 사람을 판별하는 문제는 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)에서 다룹니다.

보고서에는 "사용자가 원격으로 서버를 조작했다" 대신 "이 계정의 화면 공유 연결 기록에 주소 A, 로그인 이름 B로 된 항목이 있고 마지막 연결 날짜는 C로 적혀 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`lastConnectedDate` 는 plist 날짜형이고, mac_apt 는 이 값을 시간대 표시 없이 문자열로 바꿔 출력합니다 [1]. 모든 macOS 버전에서 날짜형인지는 알려진 자료가 없어서, 먼저 원본 plist에서 값의 형식을 확인하고, [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 따라 바꾼 뒤 어느 시간대로 보였는지 함께 적습니다. ARD 파일 안의 시각은 기준이 알려져 있지 않아서, 실제 기기에서 확인하기 전까지는 파일 시스템의 생성·수정 시각을 보조로 쓰고 무엇이 바뀔 때 바뀌는 시각인지 보고서에 밝힙니다.

## 함정과 한계

화면 공유 서비스와 ARD 에이전트가 통합 로그에 어떤 서브시스템과 문구로 인증 성공·실패를 남기는지는 공개된 자료가 없습니다. 인터넷에서 본 predicate를 그대로 쓰기보다, 실제 기기의 통합 로그에서 원격 연결 시간대 전후를 넓게 뽑아 프로세스 이름을 확인하는 편이 안전하고, 찾는 방법은 [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md)에서 다룹니다.

화면 녹화·손쉬운 사용 같은 개인 정보 보호 권한과 화면 공유 사이의 관계도 알려진 자료가 없어서, [개인 정보 보호 권한 (TCC)](../../credentials/tcc/index.md)의 항목을 원격 연결의 증거로 바로 읽지 않습니다.

연결 기록 plist는 사용자가 앱에서 항목을 지우거나 파일째 지울 수 있어서, 항목이 없다고 연결한 적이 없다고 읽지 않습니다. 지운 흔적은 [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md)에서, 예전 사본은 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../../03-techniques/analysis/snapshot-diff.md)로 찾아봅니다.

## 직접 분석해 보기

헥스로 따라가는 방법은 plist 형식 공통이라서 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에 맡기고, 여기서는 키를 따라가는 순서만 적습니다.

1. 사용자 홈마다 `~/Library/Containers/com.apple.ScreenSharing/Data/Library/Preferences/com.apple.ScreenSharing.plist` 를 복사합니다.
2. 사본을 사람이 읽을 수 있는 형태로 풀고(예: macOS의 `plutil -p`), `connectionsStore` 값을 찾아 안에 든 plist를 한 번 더 풉니다.
3. 구조 절의 표를 따라 주소, 로그인 이름, 표시 이름, 그룹, `lastConnectedDate` 를 뽑아 표로 정리합니다.
4. 같은 파일을 공개 도구 mac_apt의 `ScreenSharing` 플러그인으로 돌려 `Address`·`Login_Username`·`Last_Connection_Date` 필드가 손으로 뽑은 값과 같은지 맞춰 봅니다 [1]. 도구 결과를 맞춰 보는 방법은 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)에 있습니다.
5. 관리하는 맥이라면 `rmdb.sqlite3` 사본을 SQLite 도구로 읽기 전용으로 열어 표 목록과 열 이름을 기록하고, 관리받는 맥이라면 `AppUsage.plist` 의 키 목록을 뽑아 둡니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [원격 접속 (Remote Access)](index.md) | 같은 시간대의 로그인 기록 파일(utmpx·lastlog) |
| [터미널 명령 기록 (zsh_history·bash_sessions)](../../execution/shell-history.md) | kickstart 경로와 옵션 이름 |
| [통합 로그의 프로세스 실행 기록 (Process Events)](../../execution/unified-log-process.md) | kickstart나 화면 공유 관련 프로세스가 실행된 시각 |
| [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md) | 연결 시간대 전후의 이벤트 |
| [네트워크 인터페이스와 설정 (SystemConfiguration)](../network-interfaces.md) | 연결 기록의 주소가 그때 쓰던 네트워크 대역인지 |
| [SSH 접속 기록 (SSH)](ssh.md) | 같은 상대와 SSH로도 오갔는지 |

여러 기록을 엮어 침입 여부를 판단하는 흐름은 [원격 접속 침입 확인 (Remote Intrusion)](../../../04-scenarios/incident/remote-intrusion.md)에서 다룹니다.

## 실습

macOS 공개 시험 데이터(NIST CFReDS 등)로 아래 질문을 풀어 봅니다.

1. 사용자 홈마다 화면 공유 연결 기록 plist가 있는가, 있다면 `connectionsStore` 를 풀었을 때 항목이 몇 개인가?
2. 가장 최근 `lastConnectedDate` 는 언제이고, 값의 형식은 plist 날짜형인가?
3. `/private/var/db/RemoteManagement/` 아래에 ForensicArtifacts의 관리하는 쪽과 관리받는 쪽 가운데 어느 쪽 파일이 있는가?
4. 셸 기록이나 프로세스 실행 기록에 kickstart 경로나 옵션 이름이 있는가, 있다면 그 시각 전후에 로그인 기록이 있는가?

## 참고 문헌

1. mac_apt(ydkhatri), "plugins/screensharing.py" — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/screensharing.py
2. ForensicArtifacts, "artifacts/data/macos.yaml" — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
3. Apple Support HT201710, "Use the kickstart command-line utility in Apple Remote Desktop" — https://support.apple.com/en-us/HT201710
