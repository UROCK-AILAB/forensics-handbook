---
title: "구글 드라이브"
parent: "아티팩트 · 클라우드·노트"
nav_order: 2220
---

# 구글 드라이브 (DriveFS·Backup and Sync)

## 한 줄 요약

구글 드라이브의 PC 앱은 Drive for desktop 입니다. 이 앱은 설정을 레지스트리의 `Software\Google\DriveFS` 키 세 곳에 두고, 파일 내용을 콘텐츠 캐시 폴더에 둡니다. 예전 앱 Backup and Sync 는 폴더와 DB 이름이 다릅니다. 공식 문서로 확인한 것은 Drive for desktop 의 설정 레지스트리와 캐시 기본 위치뿐입니다. 계정별 DB 와 Backup and Sync 의 파일 이름은 공개 자료로 확인하지 못했습니다.

> **(구현)** 표시는 한 포렌식 분석 구현의 소스 코드에 들어 있던 파일·표·칸 이름입니다. 실제 검체나 공개 자료로 확인하지 않았고, 어느 앱 버전 것인지도 모릅니다. 검체에서 찾아볼 후보로만 적습니다. **(확인 못 함)** 은 공개 자료로 확인하지 못했다는 뜻입니다.

## 무엇을 기록하나 · 왜 생기나

Drive for desktop 은 관리자와 사용자가 정한 설정을 레지스트리에 두고, 파일 내용은 콘텐츠 캐시에 둡니다. 설정에는 로그인할 수 있는 계정 규칙, 캐시 위치, 마운트 위치, 미러링을 끌지 여부가 들어갑니다. 미러링을 끄는 값이 따로 있어서 앱에는 두 방식이 있는 것으로 봅니다. 하나는 가상 드라이브로 파일을 보여 주는 스트리밍이고, 다른 하나는 로컬 폴더에 실제 사본을 두는 미러링입니다 (문서의 설정 이름에서 짐작).

포렌식에서 이 기록을 보는 이유는 아래와 같습니다.

- 설정 레지스트리로 캐시가 어디 있는지 먼저 알아야 파일 내용을 찾을 수 있습니다.
- 마운트 위치를 알면 다른 아티팩트에 찍힌 드라이브 문자 경로가 구글 드라이브인지 가릴 수 있습니다.
- 외부 저장 매체 백업 설정은 USB 저장장치 조사와 이어집니다.

## 위치와 버전별 차이

| 기록 | 위치 | 근거 |
|---|---|---|
| 컴퓨터 전체 설정 | `HKEY_LOCAL_MACHINE\Software\Google\DriveFS` | 문서 |
| 사용자 설정 | `HKEY_CURRENT_USER\Software\Google\DriveFS` | 문서 |
| 강제 (override) 설정 | `HKEY_LOCAL_MACHINE\Software\Policies\Google\DriveFS` | 문서 |
| 콘텐츠 캐시 기본 위치 | Windows `%LOCALAPPDATA%\Google\DriveFS`, macOS `~/Library/Application Support/Google/DriveFS` | 문서 |
| Drive for desktop 계정별 DB | `%LOCALAPPDATA%\Google\DriveFS\<계정별 폴더>\` | 확인 못 함 |
| Backup and Sync 계정 폴더 | `%LOCALAPPDATA%\Google\Drive\<계정 폴더>\` (예: `user_default`) | 구현 |

- `%LOCALAPPDATA%` 는 보통 `C:\Users\<사용자>\AppData\Local` 입니다.
- `HKEY_LOCAL_MACHINE` 두 곳은 `SOFTWARE` 하이브에, `HKEY_CURRENT_USER` 는 사용자 `NTUSER.DAT` 에 있습니다. 하이브를 읽는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다.

### 설정이 겹칠 때

같은 설정이 여러 곳에 있으면 아래 순서로 앞선 값이 이깁니다.

| 순서 | 위치 | 설명 |
|---|---|---|
| 1 | 강제 설정 | 사용자 값보다 앞섭니다 |
| 2 | 사용자 설정 | 앱 안에서 사용자가 고른 값이 여기에 저장됩니다. 컴퓨터 전체 설정보다 앞섭니다 |
| 3 | 컴퓨터 전체 설정 | 나머지 경우에 씁니다 |

### 앱 버전

| 앱 | 내용 |
|---|---|
| Drive for desktop | 이 페이지의 설정 레지스트리와 캐시 위치는 이 앱의 관리자 문서에서 확인했습니다 |
| Backup and Sync | 예전 앱입니다. 이번에 연 문서에는 이 앱 이야기가 없었습니다. Drive for desktop 으로 바뀐 시기와 지원 종료 날짜는 확인하지 못했습니다 |

## 구조

### 설정 레지스트리 값

아래 이름과 형식은 Google Workspace 관리자 도움말에서 확인했습니다.

| 값 | 형식 | 뜻 |
|---|---|---|
| `AllowedAccountsPattern` | String | 이 기기에 로그인할 수 있는 계정을 정하는 정규식 |
| `ContentCachePath` | String | 콘텐츠 캐시 위치 |
| `ContentCacheMaxKbytes` | QWORD | 콘텐츠 캐시 크기 한도(KB) |
| `MinFreeDiskSpaceKBytes` | QWORD | 캐시가 쓰는 로컬 공간 조절 |
| `DefaultMountPoint` | String | 마운트할 드라이브 문자나 경로 |
| `DisableMirroredMyDrive` | DWORD | 내 드라이브 전체 미러링 끄기 |
| `DisableMirroredFolders` | DWORD | 임의 폴더 미러링 끄기 |
| `DisableExternalMediaSync` | DWORD | 외부 저장 매체 백업 끄기 |
| `AutoStartOnLogin` | DWORD | 로그인 때 자동 시작 |
| `BandwidthRxKBPS`, `BandwidthTxKBPS` | DWORD | 받기·보내기 속도 한도 |

문서에는 아래 설정도 있습니다.

- `DisableOutlookPlugin`, `DisableMeetOutlookPlugin`, `DisableRealTimePresence`, `OpenOfficeFilesInDocs`
- `DefaultWebBrowser` (Windows 전용)
- `DirectConnection`, `DisableCRLCheck`, `TrustedRootCertsFile`
- `DisableSSLValidation` (컴퓨터 전체 설정에만 둡니다)
- `DisableOnboardingDialog`, `DisableLocalizedVirtualFolders`

### 계정별 DB (확인 못 함)

아래는 모두 공개 자료로 확인하지 못한 이름입니다.

- `%LOCALAPPDATA%\Google\DriveFS\` 아래 계정별 폴더에 DB 가 있다는 것부터 확인하지 못했습니다.
- 계정 폴더 안 `mirror_metadata_sqlite.db` 에 표 `items` 가 있고, 칸 `local_title`, `file_size`, `trashed`, `modified_date`, `viewed_by_me_date`, `is_folder` 가 있습니다 (구현).
- 흔히 거론하는 이름으로 `metadata_sqlite_db`, `root_preference_sqlite.db`, `content_cache` 폴더, 로그 폴더가 있습니다. 이번에 확인하지 못했습니다.
- SQLite 파일을 읽는 법은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에 있습니다.

### Backup and Sync 파일 (구현)

아래는 모두 한 구현에서 본 이름입니다.

| 파일 | 표 | 칸 |
|---|---|---|
| `sync_config.db` | `data` | `entry_key`, `data_value`. `entry_key` 가 `user_email` 인 행에 계정 메일이 있습니다 |
| `snapshot.db` | `cloud_entry`, `cloud_relations`, `local_entry`, `local_relations` | `doc_id`, `filename`, `doc_type`, `shared`, `size`, `inode`, `is_folder`, `child_doc_id`, `parent_doc_id`, `child_inode`, `parent_inode` |
| `sync_log.log` | (텍스트) | 한 줄에 동기화 이벤트 하나 |

`cloud_entry` 는 클라우드 쪽 파일, `local_entry` 는 로컬 쪽 파일이라서 두 표를 비교하면 한쪽에만 있는 항목을 찾을 수 있습니다 (구현에서 짐작).

## 증거로서 의미

### 증명하는 것

- `Software\Google\DriveFS` 키에 값이 있으면, 이 PC 나 이 사용자에게 Drive for desktop 설정을 적은 적이 있습니다.
- 강제 설정 위치에 값이 있으면, 관리자가 그 설정을 강제한 적이 있습니다.
- `AllowedAccountsPattern` 은 이 기기에 로그인할 수 있던 계정의 규칙을 보여 줍니다.
- `ContentCachePath` 는 캐시가 기본 위치가 아닌 곳에 있었다는 것을 보여 줍니다.
- `DefaultMountPoint` 는 앱이 쓰도록 정한 드라이브 문자나 경로를 보여 줍니다.
- `DisableExternalMediaSync` 는 외부 저장 매체 백업을 끄도록 정했는지 보여 줍니다.

### 증명하지 못하는 것

- 설정 값은 설정일 뿐입니다. 어떤 파일을 올리거나 내려받았는지는 알려 주지 않습니다.
- `AllowedAccountsPattern` 은 규칙입니다. 실제로 로그인한 계정이 무엇인지는 알려 주지 않습니다.
- 사용자 설정 위치는 앱 안에서 고른 값이 저장되는 곳입니다. 다른 방법으로 적었을 수도 있으므로, 값이 있다고 사용자가 직접 골랐다고 단정하지 않습니다.
- 설정 키만으로 앱이 지금 깔려 있다고 단정하지 않습니다. 설치는 [설치 프로그램](../system-account/uninstall.md) 에서 따로 봅니다.
- 계정별 DB 와 Backup and Sync 파일로 무엇을 증명할 수 있는지는 검체에서 이름과 뜻을 확인한 뒤에 판단합니다.

## 시각 해석

문서에 나온 설정 값 가운데 시각 값은 없습니다. 레지스트리 키의 마지막 쓰기 시각은 키 안의 다른 값이 바뀌어도 바뀔 수 있어서 설정한 시각으로 바로 읽지 않습니다.

계정별 DB 의 시각 칸(`modified_date`, `viewed_by_me_date` 등)은 단위가 초인지, 밀리초인지, 마이크로초인지 확인하지 못했습니다 (확인 못 함). 한 구현은 값의 크기로 단위를 짐작해 바꿨습니다 (구현). 자릿수로 단위를 가리는 법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다. UTC 인지 현지 시각인지도 확인하지 못했으므로, 알려진 시각에 만든 파일로 한 번 맞춰 본 뒤에 해석합니다.

## 함정과 한계

- **세 레지스트리 위치를 모두 봅니다.** `ContentCachePath` 가 설정돼 있으면 캐시가 기본 위치에 없습니다. 기본 위치만 보고 캐시가 없다고 결론 내리지 않습니다.
- **드라이브 문자를 짐작하지 않습니다.** 마운트 위치는 `DefaultMountPoint` 로 정합니다. 기본 드라이브 문자는 이번에 연 문서에 나오지 않았습니다. 설정 값이 없으면 다른 아티팩트의 경로로 확인합니다.
- **macOS 는 캐시 기본 위치가 다릅니다.** macOS 검체에서는 `~/Library/Application Support/Google/DriveFS` 를 봅니다.
- **두 앱을 섞지 않습니다.** Backup and Sync 와 Drive for desktop 은 폴더 이름부터 다를 수 있습니다. 파일 이름 후보가 모두 확인 못 한 값이므로, 검체에서 폴더 목록을 먼저 봅니다.
- **스트리밍 방식 파일을 살아 있는 PC 에서 읽을 때 조심합니다.** 가상 드라이브의 파일을 읽으면 내용을 내려받을 수 있다고 보고 다룹니다. 이 동작은 확인하지 못했습니다. 자리표시자가 있는 동기화 폴더의 일반 주의는 [클라우드 동기화 공통 구조](cloud-files-api-syncrootmanager.md) 에 있습니다.
- **클라우드 파일 API 사용 여부를 모릅니다.** Drive for desktop 이 이 API 로 동기화 루트를 등록하는지는 확인하지 못했습니다. `SyncRootManager` 에 구글 공급자 키가 있는지 검체에서 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

**QWORD 설정 값.** 아래는 문서의 형식(QWORD, 단위 KB)으로 만든 예시 값입니다. 특정 검체에서 옮긴 값이 아닙니다.

```
값 이름:              ContentCacheMaxKbytes (QWORD)
값 데이터 (8바이트):  00 00 A0 00 00 00 00 00
뒤집어 읽기:          0x0000000000A00000 = 10485760
단위 KB 로 읽기:      10485760 KB = 10240 MB = 10 GB
```

**DWORD 설정 값.** 역시 만든 예시입니다.

```
값 이름:              DisableMirroredMyDrive (DWORD)
값 데이터 (4바이트):  01 00 00 00
뒤집어 읽기:          0x00000001 = 1
```

- 값 셀에서 형식 번호와 데이터를 찾는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다.
- 어떤 값일 때 미러링을 끄는지는 이번에 확인하지 못했습니다. 보고서에는 값만 적고, 뜻은 관리자 도움말 원문으로 확인합니다.

### 공개 도구로 한 번

1. `SOFTWARE` 하이브와 사용자 `NTUSER.DAT` 를 사본으로 뜹니다. 하이브 옆의 트랜잭션 로그 파일도 함께 뜹니다.
2. 레지스트리 하이브 뷰어로 세 위치를 엽니다. 설정 이름마다 어느 위치에 어떤 값이 있는지 표로 만듭니다.
3. 위 "설정이 겹칠 때" 순서를 적용해 실제로 쓰인 값을 고릅니다.
4. `ContentCachePath` 가 있으면 그 경로를, 없으면 기본 위치를 모읍니다.
5. 캐시 폴더 안 SQLite 파일은 사본에서 SQLite 뷰어로 엽니다. 먼저 표 이름 목록을 보고, 위 후보 이름이 실제로 있는지 확인합니다.

살아 있는 PC 에서는 Windows 에 들어 있는 `reg` 명령으로 강제 설정을 볼 수 있습니다.

```
reg query "HKLM\Software\Policies\Google\DriveFS"
```

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 클라우드 동기화 공통 구조 | `SyncRootManager` 에 구글 공급자 키가 있는지, 동기화 폴더의 파일 특성을 봅니다 | [클라우드 동기화 공통 구조](cloud-files-api-syncrootmanager.md) |
| 설치 프로그램 | Drive for desktop 이나 Backup and Sync 를 깔았는지, 언제 깔았는지 봅니다 | [설치 프로그램](../system-account/uninstall.md) |
| 셸백·바로가기 파일·점프리스트 | 마운트 위치 경로 아래 폴더를 둘러보거나 파일을 연 기록을 찾습니다 | [셸백](../file-folder-usage/shellbags/index.md), [바로가기 파일](../file-folder-usage/lnk.md), [점프리스트](../file-folder-usage/jump-lists.md) |
| USB 저장장치 흔적 | 외부 저장 매체 백업이 켜져 있었다면 연결한 장치를 봅니다 | [USB 저장장치 흔적](../external-devices/usb-storage-artifacts/index.md) |
| SRUM | 앱별 네트워크 송수신 양을 봅니다 | [SRUM](../execution/system-resource-usage-monitor/index.md) |
| 크롬 계열 브라우저 | 웹에서 구글 드라이브에 접속한 기록을 봅니다 | [크롬 계열 브라우저](../browsers/chrome-edge-whale/index.md) |

반출 여부를 따지는 흐름은 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에 있습니다.

## 실습

구글 드라이브 앱을 쓴 공개 검체(NIST CFReDS 등)나 직접 만든 시험 PC 에서 아래 질문을 풀어 봅니다.

1. `Software\Google\DriveFS` 키는 세 위치 가운데 어디에 있습니까? 같은 이름의 값이 두 곳 이상에 있다면 실제로 쓰인 값은 무엇입니까?
2. `ContentCachePath` 가 있습니까? 캐시는 어디에 있습니까?
3. `DefaultMountPoint` 가 있습니까? 없다면 셸백이나 바로가기 파일에서 구글 드라이브 경로의 드라이브 문자를 찾을 수 있습니까?
4. `%LOCALAPPDATA%\Google\` 아래에 `Drive` 와 `DriveFS` 폴더가 모두 있습니까? 각 폴더 아래 파일 이름을 이 페이지의 후보와 맞춰 봅니다.
5. 계정별 DB 에 시각 칸이 있다면 값은 몇 자리입니까? 초·밀리초·마이크로초 가운데 어느 단위로 읽어야 알려진 시각과 맞습니까?
6. `DisableExternalMediaSync` 로 외부 저장 매체 백업을 끄지 않았다면, 같은 기간에 연결한 USB 저장장치가 있습니까?

## 참고 문헌

1. Google Workspace 관리자 도움말, "Advanced Drive for desktop configuration" — https://support.google.com/a/answer/7644837 (연결되는 주소: https://knowledge.workspace.google.com/admin/drive/advanced-drive-for-desktop-configuration)
