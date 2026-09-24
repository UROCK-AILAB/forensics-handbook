---
title: "클라우드로 밖에 보냈나"
parent: "자료를 밖으로 빼돌렸나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 3630
---

# 클라우드로 밖에 보냈나 (Cloud)

> 상위 허브: [자료를 밖으로 빼돌렸나 (Data Exfiltration)](index.md)

이 페이지는 원드라이브 같은 동기화 앱으로 자료를 클라우드 저장소에 올렸는지 확인하는 순서를 다룹니다. 브라우저로 웹하드나 클라우드 웹 화면에 직접 올린 경우는 [웹메일·웹하드로 올렸나 (Web Upload)](web-upload.md) 에서 다룹니다.

이 페이지에서 "(관찰)" 을 붙인 내용은 Windows 11 Home 25H2(빌드 26200.9457) PC 한 대에서 직접 본 것입니다(확인 범위: Win11 25H2 한 대). 이 PC 에는 원드라이브 개인 계정과 회사 계정이 함께 등록돼 있었습니다.

## 조사 질문

- 이 PC 에서 어느 사용자가 어느 클라우드 서비스·계정으로 어느 폴더를 동기화했습니까?
- 조사 대상 파일이 그 폴더에 언제 들어갔고, 클라우드로 올라갔습니까?
- 회사 자료를 개인 계정 쪽 폴더로 옮겼습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | 클라우드 파일 API (Cloud Files API) 는 Windows 10 1709(Fall Creators Update) 에서 들어왔습니다[1]. 그보다 앞선 판에는 아래 동기화 루트 기록을 기대하지 않습니다. |
| 설치된 동기화 앱 | [설치 프로그램](../../../02-artifacts/system-account/uninstall.md) 과 [스토어 앱 설치 목록](../../../02-artifacts/system-account/appx-staterepository.md) 에서 원드라이브·구글 드라이브·드롭박스 같은 앱을 찾습니다. |
| 사용자 SID | 동기화 루트 기록은 사용자를 SID 로 적습니다. SID 와 사용자 이름의 짝은 [사용자 프로필 목록](../../../02-artifacts/system-account/profilelist.md) 에서 찾습니다. |
| 파일 시스템 | 클라우드 파일 API 의 핵심 드라이버 cldflt.sys 는 NTFS 볼륨만 지원합니다[1]. 동기화 폴더는 NTFS 볼륨에서 찾습니다. |
| 라이브인지 이미지인지 | 실행 중인 PC 에서는 파일을 열기만 해도 내용을 내려받아 상태가 바뀔 수 있습니다. 아래 "파일 상태" 를 먼저 읽습니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | SOFTWARE `SyncRootManager` | 어느 사용자가 어느 서비스·계정으로 어느 폴더를 동기화하나 | [클라우드 동기화 공통 구조](../../../02-artifacts/cloud-notes/cloud-files-api-syncrootmanager.md) |
| 2 | 동기화 폴더 안 파일의 상태 | 내용이 PC 에 있나, 클라우드에만 있나 | [클라우드 동기화 공통 구조](../../../02-artifacts/cloud-notes/cloud-files-api-syncrootmanager.md), [NTFS 구조](../../../01-foundations/disk-volume/ntfs/index.md) |
| 3 | $MFT·$UsnJrnl | 파일이 동기화 폴더에 만들어지거나 이름이 바뀐 시각 | [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md), [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) |
| 4 | 서비스별 동기화 DB·로그 | 올린 기록 | [원드라이브](../../../02-artifacts/cloud-notes/onedrive/index.md) 등 아래 "함께 볼 페이지" |
| 5 | SRUM 네트워크 사용량 | 동기화 앱이 그 시간대에 보낸 양 | [SRUM](../../../02-artifacts/execution/system-resource-usage-monitor/index.md) |

## 동기화 루트 기록

### 클라우드 파일 API 한눈에 보기

클라우드 파일 API 는 동기화 엔진 (Sync Engine) 을 운영체제가 공식으로 지원하는 틀이며[1], 두 부분으로 이루어집니다[1]. Cloud Filter API(Win32) 는 플레이스홀더 (Placeholder) 파일·폴더를 만들고 관리하고, Windows.Storage.Provider 네임스페이스(WinRT) 는 동기화 루트 (Sync Root) 를 운영체제에 등록합니다. 서비스가 이 틀을 쓰면 운영체제에 동기화 루트가 등록되므로, 서비스가 달라도 같은 자리에서 먼저 찾아봅니다.

### 레지스트리 위치 (관찰)

관찰한 PC 의 동기화 루트는 아래 키에 등록돼 있었습니다(관찰).

```
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\SyncRootManager\
    OneDrive!<SID>!Personal|<16진 문자열>
    OneDrive!<SID>!Business1|<16진 문자열>
```

- 하위 키 이름은 `!` 로 나뉩니다. 앞에서부터 서비스 이름, 사용자 SID, 계정 구분이 들어 있었습니다(관찰).
- `Personal` 과 `Business1` 이 따로 등록돼 있었습니다(관찰). 이름으로 개인 계정과 회사 계정을 가릅니다.
- 하위 키에는 아래 값 이름이 있었습니다(관찰).

```
DisplayNameResource, IconResource, Flags, Handler, BannerNotificationHandler,
CustomStateHandler, ThumbnailProvider, UriHandler, ShareHandler, CopyHook,
SuggestionHandlerFactory, SearchHandlerFactory, AUMID, Cid, TenantName,
StorageProviderStatusUISourceFactory
```

- 하위 키 `UserSyncRoots` 에서 값 이름은 사용자 SID 였습니다(관찰).
- 그 값의 데이터(REG_SZ)는 그 사용자의 로컬 동기화 폴더 경로였습니다(관찰). 예: `C:\Users\<사용자>\OneDrive - <회사명>`.
- 하위 키 이름의 SID 와 `UserSyncRoots` 를 함께 보면 어느 사용자가 어느 폴더를 동기화했는지 이을 수 있습니다.
- SOFTWARE 하이브는 PC 전체에 하나입니다. 사용자는 SID 로만 구분됩니다.

### 버전에 따라 생기는 값

동기화 루트 레지스트리 키 아래에는 아래 값을 둘 수 있습니다[1]. 판에 따라 값이 없을 수 있으므로, 값이 없다는 것만으로 이상하게 보지 않습니다.

| 값 | 둘 수 있는 Windows 판 |
|---|---|
| CopyHook | Windows 10 Insider Preview 빌드 19624 이후 |
| ShareHandler | Windows 11 21H2 이후 |
| SearchHandlerFactory | Windows 11 24H2 이후의 Copilot+ PC·AI 기능 Cloud PC |

(표는 [1])

## 파일 상태

동기화 폴더 안의 파일은 세 가지 상태 가운데 하나입니다[1].

| 상태 | 뜻 | PC 에 내용이 있나 |
|---|---|---|
| 플레이스홀더 파일 | 빈 표현입니다. 동기화 서비스가 있을 때만 쓸 수 있습니다. | 없습니다. 파일 시스템 헤더용 1KB 만 차지합니다. |
| 전체 파일 (Full File) | 암묵적으로 채워진 파일입니다. | 있습니다. 공간이 필요하면 시스템이 다시 비울 수 있습니다. |
| 고정된 전체 파일 (Pinned Full File) | 사용자가 탐색기에서 명시적으로 채운 파일입니다. | 있습니다. 오프라인에서도 보장됩니다. |

(표는 [1])

플레이스홀더는 보통 쓰면 자동으로 채워지는데[1], 이 동작을 채우기 (Hydration) 라고 합니다. 앱이 플레이스홀더를 열 때 몇 초 넘게 걸리면 진행 표시가 나오고[1], 사용자가 직접 열지 않은 백그라운드 채우기에는 알림(toast)이 뜹니다[1]. 플레이스홀더는 리파스 포인트 (Reparse Point) 로 구현됩니다[1].

운영체제는 동기화 엔진과, 실행 파일이 `%systemroot%` 아래에 있는 프로세스에만 이 리파스 포인트를 보여 줍니다[1]. 다른 앱은 따로 호출해 드러내도록 설정해야 볼 수 있습니다[1]. 라이브 응답에서 다른 위치에서 실행한 도구로 보면 리파스 포인트를 놓칠 수 있으므로, 이미지에서는 NTFS 구조를 직접 읽어 확인합니다([NTFS 구조](../../../01-foundations/disk-volume/ntfs/index.md)).

- 상태를 읽는 자세한 방법은 [클라우드 동기화 공통 구조](../../../02-artifacts/cloud-notes/cloud-files-api-syncrootmanager.md) 에서 다룹니다.

**증거로 읽는 법.**

- 동기화 폴더에 파일이 "있다" 는 것은 올렸다는 증거가 아닙니다.
- 플레이스홀더는 내용이 클라우드에만 있고 PC 에는 헤더만 있는 상태일 수 있습니다. 이 PC 에서 그 파일의 해시를 낼 수 없습니다.
- 전체 파일은 클라우드에서 내려받아 채운 파일일 수 있습니다. 이 PC 에서 올린 파일이라는 뜻이 아닙니다.
- 문서는 고정된 전체 파일을 사용자가 탐색기에서 명시적으로 채운 파일로 설명합니다[1]. 누가 언제 그렇게 했는지는 다른 기록으로 정합니다.
- 라이브 상태에서 플레이스홀더를 열면 채우기가 일어나 파일 상태가 바뀝니다. 라이브 응답에서는 동기화 폴더 안 파일을 함부로 열지 않습니다([라이브 응답](../../../03-techniques/process-acquisition/live-response/index.md)).
- 실제로 올렸는지는 서비스별 동기화 DB·로그로 봅니다. 원드라이브의 기록은 [원드라이브](../../../02-artifacts/cloud-notes/onedrive/index.md) 에서 다룹니다. 이 페이지를 쓰면서 서비스별 자료는 따로 확인하지 않았습니다.

## 분석 흐름

1. Windows 판이 1709 이후인지, 동기화 폴더가 NTFS 볼륨에 있는지 확인합니다.
2. SOFTWARE 하이브 `SyncRootManager` 의 하위 키를 모두 뽑습니다. 키 이름에서 서비스, SID, 계정 구분을 나눕니다.
3. SID 를 [사용자 프로필 목록](../../../02-artifacts/system-account/profilelist.md) 에서 사용자 이름으로 바꿉니다.
4. `UserSyncRoots` 에서 사용자별 로컬 동기화 폴더 경로를 적습니다. 회사 계정 폴더와 개인 계정 폴더를 나눠 적습니다.
5. 조사 대상 파일이 어느 동기화 폴더에 있는지 찾고, 파일마다 상태(플레이스홀더·전체·고정)를 적습니다.
6. $MFT·$UsnJrnl 에서 파일이 그 폴더에 만들어지거나 이름이 바뀐 시각을 찾습니다. 회사 폴더에서 개인 계정 폴더로 옮긴 흔적이 있는지도 봅니다.
7. 서비스별 동기화 DB·로그에서 그 파일을 올린 기록을 찾습니다.
8. SRUM 에서 동기화 앱의 송신량을 6·7 의 시각 앞뒤로 봅니다. SRUM 이 말해 주는 범위는 [웹메일·웹하드로 올렸나](web-upload.md) 에서 다룹니다.
9. 모든 시각을 UTC 로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리합니다.

## 흔한 오판

1. **동기화 폴더에 있으니 올렸다고 봅니다.** 폴더에 있는 것과 이 PC 에서 올린 것은 다릅니다. 올린 기록은 서비스 쪽 DB·로그에서 찾습니다.
2. **전체 파일이니 이 PC 에서 만든 파일이라고 봅니다.** 클라우드에서 내려받아 채운 파일일 수 있습니다.
3. **플레이스홀더의 해시를 원본 해시와 비교합니다.** 플레이스홀더에는 내용이 없습니다. 내용은 클라우드 쪽 자료로 확인합니다.
4. **동기화 루트가 없으니 클라우드를 안 썼다고 봅니다.** 브라우저로 올렸을 수 있습니다. [웹메일·웹하드로 올렸나](web-upload.md) 를 함께 봅니다.
5. **라이브 상태에서 동기화 폴더를 훑어봅니다.** 파일을 열면 채우기가 일어나 증거 상태가 바뀝니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 회사 도면을 개인 원드라이브에 올렸습니다."
- 쓸 문장: "SOFTWARE 하이브 SyncRootManager 에 사용자 ○○ 의 SID 로 원드라이브 개인 계정(Personal) 동기화 루트가 등록돼 있습니다. `UserSyncRoots` 에 적힌 이 사용자의 로컬 동기화 폴더에 ○○ 파일이 있습니다. 이 파일은 PC 에 내용이 있는 전체 파일 상태입니다. $UsnJrnl 에는 ○○(UTC) 에 이 파일이 이 폴더에 만들어진 기록이 있습니다. 이 기록은 파일이 그 시각에 개인 계정 동기화 폴더에 들어왔음을 보여 줍니다. 클라우드로 올라갔는지는 동기화 앱 기록이나 서비스 쪽 자료로 확인해야 합니다."

## 함께 볼 페이지

- [클라우드 동기화 공통 구조](../../../02-artifacts/cloud-notes/cloud-files-api-syncrootmanager.md) — SyncRootManager 와 파일 상태를 읽는 법입니다.
- [원드라이브](../../../02-artifacts/cloud-notes/onedrive/index.md) · [구글 드라이브](../../../02-artifacts/cloud-notes/drivefs-backup-and-sync.md) · [드롭박스](../../../02-artifacts/cloud-notes/dropbox.md) · [네이버 MYBOX](../../../02-artifacts/cloud-notes/naver-mybox.md) · [아이클라우드](../../../02-artifacts/cloud-notes/icloud-for-windows.md) · [박스 드라이브](../../../02-artifacts/cloud-notes/box-drive.md) · [메가](../../../02-artifacts/cloud-notes/mega.md) — 서비스별 동기화 DB·로그입니다.
- [NTFS 구조](../../../01-foundations/disk-volume/ntfs/index.md) · [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md) · [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) — 동기화 폴더에 파일이 들어온 시각입니다.
- [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) · [사용자 프로필 목록](../../../02-artifacts/system-account/profilelist.md) — 키 이름의 SID 를 사용자로 바꿉니다.
- [웹메일·웹하드로 올렸나 (Web Upload)](web-upload.md) — 브라우저로 올린 경우와 SRUM 송신량입니다.
- [퇴사 전 자료를 모으고 압축했나 (Staging)](staging.md) — 동기화 폴더로 옮기기 전에 모은 흔적입니다.
- [라이브 응답](../../../03-techniques/process-acquisition/live-response/index.md) — 실행 중인 PC 에서 동기화 폴더를 다룰 때 봅니다.

## 참고 문헌

1. Microsoft Learn, "Build a Cloud Sync Engine that Supports Placeholder Files" — https://learn.microsoft.com/en-us/windows/win32/cfapi/build-a-cloud-file-sync-engine
