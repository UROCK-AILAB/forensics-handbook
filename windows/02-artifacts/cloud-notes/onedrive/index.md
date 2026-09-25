---
title: "원드라이브"
parent: "아티팩트 · 클라우드·노트"
nav_order: 2170
has_children: true
has_toc: false
---

# 원드라이브 (OneDrive)

## 한 줄 요약

OneDrive 는 Microsoft 의 클라우드 저장소입니다. PC 에서는 동기화 앱 `OneDrive.exe` 가 사용자의 동기화 폴더를 클라우드와 맞춥니다. 이 앱은 사용자 프로필 아래에 계정별 설정·DB·로그를 남기고, 레지스트리에 계정과 동기화 폴더를 등록합니다.

> 이 페이지의 경로와 값은 Windows 11 빌드 26200 과 OneDrive 26.168.0830.0006 기준입니다.

## 왜 중요한가

동기화 폴더에 넣은 파일은 클라우드로 올라가므로, 파일이 PC 밖으로 나간 통로를 따질 때 먼저 봅니다. 한 사용자가 개인 계정과 회사 계정을 함께 연결할 수 있고, 기록은 `Personal`, `Business1` … 로 계정마다 따로 쌓입니다.

동기화 DB 에는 파일 목록과 내용 해시가 있어서, 이 해시로 다른 곳에서 찾은 파일과 같은 내용인지 맞춰 볼 수 있습니다. 파일 주문형 (Files On-Demand) 을 쓰면 동기화 폴더의 파일이 내용 없는 자리표시자일 수 있어서 파일 목록과 PC 에 실제로 있던 내용이 다를 수 있습니다.

알려진 폴더 이동 (Known Folder Move, KFM) 을 켜면 바탕 화면·문서 경로가 OneDrive 폴더 안으로 바뀌므로 다른 아티팩트에 찍힌 경로를 읽는 방법이 달라집니다. 로그 안의 파일 이름은 가려져 있어서 푸는 키 파일을 로그와 함께 모아야 합니다.

증명하지 못하는 것도 분명합니다.

기록은 OneDrive 계정과 Windows 사용자 프로필 단위로 남으며, 그 시각에 누가 PC 앞에 있었는지는 남지 않습니다. 동기화는 앱이 스스로 하므로 파일이 올라갔다는 기록만으로 사용자가 올리려는 뜻이 있었다고 단정하지 않습니다.

레지스트리와 DB 의 시각 값은 대부분 정확한 기록 조건에 관한 공개 자료가 없으므로 이름에서 짐작한 뜻이라고 밝혀 씁니다. 로그는 며칠 치만 남을 수 있고, 계정 폴더 로그는 4~5일 치만 남기도 합니다.

## 한눈에 보기

> 그림 자리: 사용자 프로필의 `%LOCALAPPDATA%\Microsoft\OneDrive` 아래 `settings`(계정 폴더별 DB·ini)와 `logs`(Common·Personal·Business1), 그리고 레지스트리의 `Accounts`·`SyncEngines`·`SyncRootManager` 키가 같은 계정·같은 동기화 폴더로 이어지는 모양을 보여 주는 그림

### 무엇이 어디에 남나

`%LOCALAPPDATA%` 는 보통 `C:\Users\<사용자>\AppData\Local` 입니다.

| 기록 | 위치 | Windows·앱 버전 | 알려 주는 것 | 페이지 |
|---|---|---|---|---|
| 계정·설정 레지스트리 | `HKCU\Software\Microsoft\OneDrive` (아래 `Accounts\Personal`, `Accounts\Business1` …) | 값 구성은 앱 버전을 따릅니다 | 연결한 계정, 동기화 폴더, 로그인 시각, 알려진 폴더 이동 상태 | [계정·설정 레지스트리](accounts-settings.md) |
| 동기화 루트 등록 | `HKCU\Software\SyncEngines\Providers\OneDrive\…`, `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\SyncRootManager\OneDrive!…` | 일부 값은 Windows 10 Insider 19624·Windows 11 21H2 이후에 생깁니다 | 사용자 SID 별 동기화 폴더 | [계정·설정 레지스트리](accounts-settings.md) |
| 설정·DB 폴더 | `%LOCALAPPDATA%\Microsoft\OneDrive\settings\Personal`, `settings\Business<1-9>` | 옛 앱은 `.dat` 파일, 새 앱은 SQLite | 파일·폴더 목록, 해시, 서비스 작업 기록, 삭제 기록 | [동기화 DB](syncenginedatabase-db.md) |
| 로그 폴더 | `%LOCALAPPDATA%\Microsoft\OneDrive\logs\` (아래 `Common`, `Business1`, `Personal`) | 로그 형식 버전 2·3 | 앱이 부른 함수와 시각 | [로그 (ODL·ODLGZ)](odl-odlgz.md) |
| 관리자 정책 | `HKLM\SOFTWARE\Policies\Microsoft\OneDrive`, `HKCU\SOFTWARE\Policies\Microsoft\OneDrive` | — | 관리자가 건 설정, 관리 대상 조직의 테넌트 ID | [계정·설정 레지스트리](accounts-settings.md), [회사용 OneDrive와 SharePoint 동기화](business-tenant.md) |
| 회사 계정과 SharePoint 라이브러리 | `Business` 키·폴더, 조직 이름 폴더 | SharePoint 라이브러리 동기화는 Microsoft 365 회사·학교 구독이나 SharePoint Server 2019 가 필요합니다 | 어느 조직 계정인지, 어느 라이브러리를 동기화했는지 | [회사용 OneDrive와 SharePoint 동기화](business-tenant.md) |

### 시각 형식

| 기록 | 형식 |
|---|---|
| 레지스트리·DB 의 시각 값 | Unix 초. 변환하면 UTC 입니다 |
| 로그 레코드의 시각 | Unix 밀리초. 변환하면 UTC 입니다 |
| 로그 파일 이름의 날짜·시각 | UTC 입니다 |

단위가 초와 밀리초로 섞여 있으므로, 한 시간 축에 놓기 전에 맞춥니다. 변환은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.

### 프로그램 설치 위치

사용자별 설치는 `%localappdata%\Microsoft\OneDrive\<빌드 번호>\` 아래에, 컴퓨터 전체 설치는 `%ProgramFiles(x86)%\Microsoft OneDrive\<빌드 번호>\` 또는 `%ProgramFiles%\Microsoft OneDrive\<빌드 번호>\` 아래에 정책 템플릿 폴더 `adm` 이 있습니다.

컴퓨터 전체 설치(`C:\Program Files\Microsoft OneDrive\OneDrive.exe`)여도 `settings`·`logs` 는 사용자 프로필의 `%LOCALAPPDATA%\Microsoft\OneDrive` 아래에 있습니다. 그래서 설치 방식과 관계없이 사용자 프로필마다 `settings`·`logs` 를 찾습니다.

### 동기화 폴더

- 개인 계정의 동기화 폴더는 `C:\Users\<사용자>\OneDrive` 같은 경로입니다.
- 회사 계정 폴더와 SharePoint 라이브러리 폴더의 이름·위치는 [회사용 OneDrive와 SharePoint 동기화](business-tenant.md) 에서 다룹니다.
- 실제 폴더 경로는 레지스트리의 `UserFolder`·`MountPoint` 값으로 확인합니다.

### 파일 주문형과 자리표시자

- Windows 10 1709 부터 클라우드 파일 API (cloud files API) 가 생겼습니다. 동기화 앱은 이 API 로 자리표시자 (placeholder) 파일을 만듭니다.
- 파일 상태는 셋입니다.

| 상태 | 뜻 |
|---|---|
| 자리표시자 | 내용이 없습니다. 서비스에 닿을 때만 열립니다 |
| 전체 파일 | 파일을 열어서 암묵적으로 받은 것입니다. 공간이 모자라면 시스템이 다시 비울 수 있습니다 |
| 고정된 전체 파일 | 사용자가 탐색기에서 직접 받은 것입니다. 오프라인에서도 쓸 수 있게 보장합니다 |

- 자리표시자는 파일 시스템 머리 1KB 만 차지합니다.
- 이 기능의 중심은 미니필터 드라이버 `cldflt.sys` 이고, NTFS 볼륨만 지원합니다.
- 자리표시자는 재분석 지점 (reparse point) 으로 만듭니다. 동기화 엔진과 `%systemroot%` 아래 프로그램이 아닌 앱에는 이 재분석 지점을 숨깁니다.
- 살아 있는 PC 에서 자리표시자를 읽으면 내려받기가 일어납니다. 수집할 때 조심할 점은 [동기화 DB](syncenginedatabase-db.md) 의 함정 절에 있습니다.
- 파일 주문형을 켜는 정책과 드라이버 설정 값은 [계정·설정 레지스트리](accounts-settings.md) 에 있습니다.
- 자리표시자와 동기화 루트 등록의 공통 구조는 [클라우드 동기화 공통 구조](../cloud-files-api-syncrootmanager.md) 에서 다룹니다.

### 알려진 폴더 이동 (KFM, 백업)

옮길 수 있는 폴더는 바탕 화면, 문서, 사진, 스크린샷, 카메라 앨범(Desktop, Documents, Pictures, Screenshots, Camera Roll)이고, OneDrive 정책은 음악·동영상 폴더에는 영향을 주지 않습니다.

KFM 을 켠 PC 에서는 `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders` 의 `Desktop`·`Personal`·`My Pictures` 값이 모두 OneDrive 동기화 폴더 아래(`…\Desktop`, `…\Documents`, `…\Pictures`)를 가리킵니다. 그래서 바로가기 파일·점프리스트 같은 기록에 바탕 화면·문서 경로가 OneDrive 폴더 안 경로로 찍히는 것으로 보입니다. OneDrive 폴더 안 경로라고 해서 사용자가 일부러 그 폴더에 넣었다고 단정하지 않습니다.
- 계정별 이동 상태 값은 [계정·설정 레지스트리](accounts-settings.md), 관리자 정책은 [회사용 OneDrive와 SharePoint 동기화](business-tenant.md) 에서 다룹니다.

### 공개 도구

- odl.py (Yogesh Khatri) 는 ODL 로그를 CSV 로 풀어 줍니다.
- OneDriveExplorer 는 `settings` 의 DB 로 폴더 구조를 다시 만듭니다. `$Recycle.Bin` 으로 지운 항목을, 사용자 레지스트리 하이브로 동기화 폴더 위치를 찾습니다. ODL 로그를 항목과 엮어 보여 주기도 합니다.
- 도구 하나에 기대지 않고, 각 하위 페이지의 헥스·SQL 절차로 결과를 한 번 맞춰 봅니다.

## 읽는 순서

1. [계정·설정 레지스트리 (Accounts·Settings)](accounts-settings.md) — 어느 계정을 연결했고 동기화 폴더가 어디인지 레지스트리에서 찾습니다. 계정 키의 시각 값, `SyncRootManager` 의 사용자 SID, settings 폴더의 ini 파일, 일반 정책 키도 다룹니다.
2. [동기화 DB (SyncEngineDatabase.db)](syncenginedatabase-db.md) — 파일·폴더 목록으로 경로를 다시 만들고, QuickXorHash 해시와 로컬 수정 시각을 읽습니다. 내려받기 기록, 서비스 작업 기록, `SafeDelete.db` 의 삭제 기록도 봅니다.
3. [로그 (ODL·ODLGZ)](odl-odlgz.md) — ODL 파일 머리와 레코드 머리를 헥스로 따라가고, 압축을 풉니다. 가려진 이름을 `general.keystore` 로 푸는 법도 다룹니다.
4. [회사용 OneDrive와 SharePoint 동기화 (Business Tenant)](business-tenant.md) — 테넌트 ID 와 SharePoint 주소로 조직 계정을 가립니다. 라이브러리 동기화 폴더와 조직에 관한 정책을 다룹니다.

## 함께 볼 페이지

- [클라우드 동기화 공통 구조 (Cloud Files API·SyncRootManager)](../cloud-files-api-syncrootmanager.md) — 여러 클라우드 앱이 함께 쓰는 자리표시자와 동기화 루트 등록 구조입니다.
- [구글 드라이브](../drivefs-backup-and-sync.md) · [드롭박스](../dropbox.md) — 같은 PC 에서 다른 클라우드 앱을 썼는지 봅니다.
- [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) — 동기화 DB 와 WAL 파일을 읽는 법입니다.
- [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) — `NTUSER.DAT`·`SOFTWARE` 하이브를 읽는 법입니다.
- [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) — Unix 초·밀리초를 UTC 로 바꿉니다.
- [사용자 프로필 목록](../../system-account/profilelist.md) — `SyncRootManager` 의 SID 를 사용자로 바꿉니다.
- [바로가기 파일](../../file-folder-usage/lnk.md) · [점프리스트](../../file-folder-usage/jump-lists.md) — 동기화 폴더 안 파일을 연 기록을 찾습니다.
- [휴지통](../../file-folder-usage/recycle-bin.md) — 동기화 폴더에서 지운 파일을 찾습니다.
- [해시셋 대조와 유사 해시](../../../03-techniques/analysis/hash-set-fuzzy-hash.md) — DB 의 해시로 파일을 맞춰 봅니다.
- [자료를 밖으로 빼돌렸나](../../../04-scenarios/exfiltration/data-exfiltration/index.md) — 클라우드 동기화를 포함한 유출 경로를 따라가는 순서입니다.
- [지운 파일의 흔적 찾기](../../../04-scenarios/activity/deleted-file-traces.md) — 동기화 폴더에서 지운 파일의 흔적을 다른 기록과 함께 봅니다.

## 참고 문헌

- Microsoft Learn, "Use OneDrive policies to control sync settings" (2026-09 갱신) — https://learn.microsoft.com/en-us/sharepoint/use-group-policy
- Microsoft Learn, "Redirect and move Windows known folders to OneDrive" — https://learn.microsoft.com/en-us/sharepoint/redirect-known-folders
- Microsoft Support, "Sync SharePoint and Teams files with your computer" — https://support.microsoft.com/en-us/office/sync-sharepoint-and-teams-files-with-your-computer-6de9ede8-5b6e-4503-80b2-6190f3354a88
- Microsoft Learn, "Build a Cloud Sync Engine that Supports Placeholder Files" — https://learn.microsoft.com/en-us/windows/win32/cfapi/build-a-cloud-file-sync-engine
- Yogesh Khatri, "Reading OneDrive Logs" (Swift Forensics, 2022-02) — https://www.swiftforensics.com/2022/02/reading-onedrive-logs.html
- ydkhatri/OneDrive, README (OneDrive .ODL Parser) — https://github.com/ydkhatri/OneDrive
- Beercow/OneDriveExplorer, README — https://github.com/Beercow/OneDriveExplorer
