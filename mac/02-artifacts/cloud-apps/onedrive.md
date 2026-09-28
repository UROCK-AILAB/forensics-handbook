---
title: "원드라이브"
parent: "아티팩트 · 클라우드·애플 앱"
nav_order: 1540
---

# 원드라이브 (OneDrive)

맥의 원드라이브 동기화 앱은 설정을 plist에 남기고, 조직이 건 정책 키가 그 plist에 있으면 어느 조직(테넌트)으로 동기화를 허용했는지, 데스크탑·문서 폴더를 원드라이브로 옮기게 했는지, 무엇을 올리지 않게 했는지를 읽을 수 있습니다.

이 페이지는 설정 파일과 관리 키를 다룹니다 [1]. 동기화 폴더 위치와 로그, 동기화 상태 DB는 실제 데이터로 확인하고, macOS가 클라우드 저장소 앱에 내주는 동기화 틀은 [파일 공급자 (File Provider)](file-provider.md)에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

원드라이브 맥 앱은 단독 설치판 (Standalone)과 Mac App Store 판 두 가지로 나오고, 두 판은 설정 키 이름이 같지만 plist 파일 이름과 도메인이 다릅니다 [1]. 관리자는 이 도메인에 키를 넣어 개인 계정 동기화를 막거나, 특정 테넌트로만 올리게 하거나, 데스크탑·문서 폴더를 원드라이브로 옮기게 할 수 있습니다 [1]. 사용자 쪽에도 원드라이브와 SharePoint 설정을 담는 plist가 따로 있어서 [1], 조사에서는 호스트 전체 설정과 사용자 설정을 나눠서 봅니다.

이 키들은 "이 맥에 어떤 정책이 걸려 있었나" 를 보여 주는 기록이라서, 파일을 실제로 올렸는지나 누가 로그인했는지는 다른 흔적으로 따로 확인합니다.

## 위치와 버전별 차이

### 호스트 전체 설정

| 판 | 설정 파일 | 도메인 |
|---|---|---|
| 단독 설치판 | `/Library/Preferences/com.microsoft.OneDrive.plist` | `com.microsoft.OneDrive` |
| Mac App Store 판 | `/Library/Containers/com.microsoft.OneDrive-mac/Data/Library/Preferences/com.microsoft.OneDrive-mac.plist` | `com.microsoft.OneDrive-mac` |

Mac App Store 판 경로는 `/Library/Containers/...` 로 알려져 있지만 사용자 홈 아래 `~/Library/Containers/...` 일 수도 있어서 [1], 실제 데이터에서는 두 위치를 모두 찾아봅니다.

### 사용자 설정과 업데이터

```
~/Library/Preferences/com.microsoft.SharePoint-mac.plist
~/Library/Group Containers/UBF8T346G9.OneDriveStandaloneSuite/Library/Preferences/UBF8T346G9.OneDriveStandaloneSuite.plist
~/Library/Preferences/com.microsoft.OneDriveUpdater.plist
```

앞의 두 파일에는 웹용 원드라이브의 오프라인 모드를 막는 설정(`DisableOfflineMode`)이 들어가고, 두 번째 파일은 원드라이브 그룹 설정 파일입니다 [1]. 세 번째 파일은 도메인이 `com.microsoft.OneDriveUpdater` 이고, 업데이트 링 값으로 Insiders, Production(기본값), Enterprise(Deferred와 같음) 가운데 하나가 들어갑니다 [1].

### 판과 버전에 따른 차이

| 조건 | 차이 |
|---|---|
| 단독 설치판과 App Store 판 | 데스크탑·문서 폴더를 옮기는 Folder Backup 설정은 단독 설치판에서만 되고 App Store 판은 지원하지 않습니다 [1]. |
| macOS 13 Ventura 이후 | 앱이 사용자 동의 없이 백그라운드에서 돌지 못해서, 관리 프로필 `com.apple.servicemanagement` 에 규칙 `LabelPrefix` = `com.microsoft.OneDrive`, `BundleIdentifierPrefix` = `com.microsoft.OneDriveLauncher` 를 넣어 허용합니다. App Store 판의 식별자는 `com.microsoft.OneDrive-mac` 입니다 [1]. |
| 동기화 앱 24.113 | 로그인 때 자동 실행을 정하는 `OpenAtLogin` 키가 폐지 예정입니다 [1]. |
| 동기화 앱 26.027 이상, macOS 13 이상 | `open -a OneDrive --args /createloginitem` 과 `/removeloginitem` 으로 로그인 항목을 등록하고 해제합니다 [1]. |

Ventura 이후의 백그라운드 실행 승인과 로그인 항목 기록은 [로그인 항목 (Login Items)](../persistence/login-items.md)에서 다룹니다.

### 실제 데이터로 확인할 것

| 항목 | 확인 방법 |
|---|---|
| 동기화 폴더가 `~/Library/CloudStorage/` 아래에 있는지와 폴더 이름 규칙 | `~/Library/CloudStorage/` 아래 폴더 목록에서 확인 |
| 원드라이브가 File Provider 방식으로 바뀐 앱 버전과 macOS 조건 | 시험 기기에서 재현해 확인 |
| 로그 위치(`~/Library/Logs/OneDrive/` 등) | `~/Library/Logs/` 아래 폴더 목록에서 확인 |
| 동기화 상태 DB(파일 목록·해시)의 경로와 형식 | 앱 데이터 폴더에서 DB 파일을 찾아 파일 헤더와 표 구조를 확인 |
| 로그인한 계정·테넌트가 남는 plist 키 | 설정 plist를 열어 키 이름과 값을 확인 |

## 구조

설정 파일은 속성 목록 파일이라서 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)을 따릅니다. 아래 키는 관리 키 가운데 조사에서 뜻이 있는 것들이고, 값이 들어 있으면 그 정책이 이 맥에 걸려 있었다는 흔적으로 읽습니다 [1].

| 키 | 값 | 뜻 |
|---|---|---|
| `AllowTenantList` / `BlockTenantList` | dict, 테넌트 ID 키에 true | 테넌트별로 동기화를 허용하거나 막아서 다른 조직으로 파일을 올리지 못하게 합니다. 둘을 함께 켜지 않습니다. |
| `BlockExternalSync` | | 다른 조직이 공유한 라이브러리·폴더의 동기화를 막습니다. |
| `DisablePersonalSync` | | 개인 계정 로그인과 동기화를 막고, 개인 계정으로 이미 동기화 중이었으면 로그아웃시킵니다. |
| `DefaultFolder` | dict: `Path`, `TenantId` | 조직별 원드라이브 폴더의 기본 위치입니다. 문서 목록에는 DefaultFolderLocation 이라는 이름으로 나오지만 plist 예시의 키는 `DefaultFolder` 입니다. |
| `KFMSilentOptIn` | 테넌트 ID 문자열 | 데스크탑·문서 폴더를 원드라이브로 옮기는 Folder Backup 설정입니다. `KFMSilentOptInDesktop`, `KFMSilentOptInDocuments`, `KFMSilentOptInWithNotification`, `KFMOptInWithWizard` 가 같은 무리입니다. |
| `KFMBlockOptIn` | 1 또는 2 | Folder Backup을 막고, 값이 2이면 옮겼던 폴더를 기기로 되돌립니다. |
| `KFMBlockOptOut` | | Folder Backup을 사용자가 끄지 못하게 합니다. |
| `EnableODIgnore` | 파일 이름 패턴 배열(예 `*.pst`) | 패턴에 맞는 새 파일을 올리지 않습니다. 걸린 파일은 로컬 폴더에 남고 Finder에 "Excluded from sync" 아이콘이 붙습니다. |
| `EnableODIgnoreFolders` | 폴더 이름 배열 | 이름이 같은 새 폴더를 올리지 않습니다. 와일드카드는 쓰지 않고, 이미 올라간 폴더와 내용은 클라우드에서 지우지 않습니다. |
| `LocalMassDeleteFileDeleteThreshold` | 0~100000 | 로컬에서 한꺼번에 지울 때 알림을 띄우는 기준입니다. 설정하지 않으면 짧은 시간에 200개 넘게 지울 때 알림이 뜹니다. |
| `DisableFirstDeleteDialog` | 1 | "Deleted files are removed everywhere" 알림을 숨깁니다. |
| `HydrationDisallowedApps` | JSON 문자열 | 온라인 전용 파일을 자동으로 내려받지 못하게 할 앱 목록입니다. |
| `UploadBandwidthLimited` / `DownloadBandwidthLimited` | KB/s | 올리기·내려받기 속도 상한입니다. `AutomaticUploadBandwidthPercentage` 도 올리기 속도를 정합니다. |
| `OpenAtLogin` | | 로그인 때 자동 실행입니다. |

관리 키가 plist로 직접 들어갔는지 구성 프로파일로 배포됐는지는 [구성 프로파일 (Configuration Profiles·MDM)](../persistence/configuration-profiles.md)에서 설치된 프로파일과 맞춰 확인합니다.

## 증거로서 의미

**증명하는 것.** 관리 키에 값이 있으면 그 설정이 이 맥에 걸려 있었다는 기록이 있다는 뜻입니다 [1]. `AllowTenantList`, `KFMSilentOptIn`, `DefaultFolder` 에 들어 있는 테넌트 ID는 이 맥이 어느 조직의 원드라이브와 묶이도록 설정됐는지 알려 주고, `EnableODIgnore` 와 `EnableODIgnoreFolders` 는 어떤 파일과 폴더를 동기화에서 빼도록 설정했는지 알려 줍니다 [1]. 사용자 홈에 원드라이브 plist가 있으면 그 사용자 계정에서 앱 설정이 만들어졌다는 기록으로 읽습니다.

**증명하지 못하는 것.** 정책이 걸려 있었다는 기록만으로 파일이 올라갔는지, 언제 로그인했는지, 누가 그 계정을 썼는지는 알 수 없습니다. `KFMSilentOptIn` 이 있어도 폴더가 실제로 옮겨졌는지는 파일 위치와 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)로 따로 확인하고, `LocalMassDeleteFileDeleteThreshold` 는 알림 기준일 뿐 실제로 한꺼번에 지웠는지는 알려 주지 않습니다. `DisableFirstDeleteDialog` 가 1이면 사용자가 "지운 파일이 모든 곳에서 사라진다" 는 알림을 보지 못했을 가능성이 있습니다. 다만 이는 해석이므로 보고서에는 설정 값만 적습니다.

보고서에는 "이 맥의 원드라이브 설정에 테넌트 ID 이 값으로 Folder Backup을 켜는 키가 있다" 처럼 설정이 보여 주는 만큼만 씁니다.

## 시각 해석

관리 키에는 시각 값이 없습니다. 설정이 언제 들어갔는지는 plist 파일의 수정 시각과 FSEvents 기록, 구성 프로파일 설치 기록으로 좁히고, 파일 수정 시각은 마지막으로 바뀐 때만 알려 준다는 점을 함께 적습니다. 시각 값의 기준은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다.

## 함정과 한계

- **두 판, 두 경로.** 단독 설치판과 App Store 판은 plist 이름과 도메인이 달라서 [1], 한쪽만 보면 다른 판의 설정을 놓칩니다.
- **모호한 App Store 판 경로.** App Store 판 설정 파일이 `/Library/Containers/...` 와 사용자 홈 아래 `~/Library/Containers/...` 가운데 어디에 있는지 분명하지 않아서 [1], 두 곳을 모두 봅니다.
- **문서와 키 이름이 다른 항목.** 문서 목록의 DefaultFolderLocation 은 plist에서 `DefaultFolder` 라는 키로 들어갑니다 [1]. 문서 목록 이름으로 검색하면 찾지 못합니다.
- **로컬에 남은 제외 파일.** `EnableODIgnore` 에 걸린 파일은 원드라이브 폴더 안에 있어도 올라가지 않아서 [1], 폴더 안에 있다는 사실만으로 업로드를 단정하지 않습니다. 거꾸로 이 규칙은 새 파일과 새 폴더에만 걸리고 이미 올라간 것은 클라우드에 그대로 두어서 [1], 규칙이 있다고 그 전에 올라간 파일이 없었다고 말하지도 못합니다.
- **되돌린 폴더.** `KFMBlockOptIn` 값 2는 옮겼던 폴더를 기기로 되돌려서 [1], 폴더가 원래 자리에 있어도 한 번 옮겨진 적이 있을 수 있습니다.
- **폐지 예정 키.** `OpenAtLogin` 은 24.113에서 폐지 예정이라서 [1], 새 버전에서는 자동 실행 여부를 로그인 항목 쪽에서 확인합니다.
- **동기화 흔적.** 도구가 동기화 폴더, 로그, 상태 DB에 뜻을 붙여 보여 주면 그 근거를 확인한 뒤에 씁니다.

## 직접 분석해 보기

### 헥스로 한 번

설정 plist를 헥스 편집기로 열어 바이너리 plist인지 XML인지 첫 바이트로 구분하고, 바이너리라면 오프셋 표를 따라 `AllowTenantList` 같은 키 문자열이 들어 있는 객체를 찾아갑니다. 머리말과 오프셋 표를 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에서 다룹니다.

### 공개 도구로 한 번

사본을 만든 뒤 macOS의 `plutil` 로 엽니다.

```
plutil -p "com.microsoft.OneDrive.plist"
plutil -p "com.microsoft.OneDrive-mac.plist"
plutil -p "com.microsoft.OneDriveUpdater.plist"
plutil -p "UBF8T346G9.OneDriveStandaloneSuite.plist"
```

위 구조 표의 키가 있는지 차례로 보고, 테넌트 ID가 나오면 여러 키에 같은 값이 들어 있는지 맞춰 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [파일 공급자 (File Provider)](file-provider.md) | 클라우드 저장소 앱의 동기화 폴더와 파일 상태 |
| [로그인 항목 (Login Items)](../persistence/login-items.md) | 원드라이브가 로그인 항목·백그라운드 항목으로 등록됐는지 |
| [구성 프로파일 (Configuration Profiles·MDM)](../persistence/configuration-profiles.md) | 관리 키와 `com.apple.servicemanagement` 규칙이 프로파일로 들어왔는지 |
| [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) | 데스크탑·문서 폴더가 옮겨진 흔적, 대량 삭제 |
| [앱별 네트워크 사용량 (netusage)](../network/netusage.md) | 원드라이브 프로세스가 보낸 양 |
| [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) | 클라우드 동기화를 유출 경로로 따지는 흐름 |

## 실습

공개 시험 데이터(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. `/Library/Preferences/`, `/Library/Containers/`, 사용자 홈의 `Library/Containers/` 에서 원드라이브 설정 plist를 찾고, 어느 판이 설치돼 있었는지 적어 보세요.
2. 설정 plist에 테넌트 ID가 든 키가 있으면 모두 뽑고, 같은 값이 여러 키에 나오는지 확인해 보세요.
3. `EnableODIgnore` 나 `EnableODIgnoreFolders` 가 있으면 그 패턴에 맞는 파일이 원드라이브 폴더 안에 있는지 찾아보세요.
4. 업데이터 plist에서 업데이트 링 값을 읽고, 설치된 앱 버전과 함께 적어 보세요.

## 참고 문헌

1. Microsoft Learn, "Deploy and configure the OneDrive sync app for Mac" (2026-08 갱신) — https://learn.microsoft.com/en-us/sharepoint/deploy-and-configure-on-macos
