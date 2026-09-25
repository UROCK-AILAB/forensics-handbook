---
title: "아이클라우드"
parent: "아티팩트 · 클라우드·노트"
nav_order: 2250
---

# 아이클라우드 (iCloud for Windows)

## 한 줄 요약

iCloud for Windows 는 아이클라우드 드라이브 (iCloud Drive) 의 파일을 기본으로 `C:\Users\[사용자 이름]\iCloud Drive` 에 둡니다. 버전 14 부터는 이 위치를 다른 드라이브로 옮길 수 있고, 옮길 드라이브는 NTFS 여야 합니다. 버전 7 은 드라이브 내용을 모두 자동으로 내려받습니다. 앱이 설정과 로그를 어디에 두는지, 클라우드 파일 API 를 쓰는지는 공개 자료가 없어 검체에서 확인합니다.

> **(짐작)** 은 사용자 안내서의 항목 이름에서 미루어 본 내용입니다.

## 무엇을 기록하나 · 왜 생기나

아이클라우드 드라이브의 파일과 폴더는 기본으로 `C:\Users\[사용자 이름]\iCloud Drive` 에 저장됩니다. 아이클라우드 드라이브에는 "파일을 내려받은 상태로 유지 (Keep files downloaded)", "내려받기·공유 상태 보기", "최근 삭제된 파일 복구" 기능이 따로 있습니다[1]. 그래서 파일을 필요할 때 내려받는 방식과 최근 삭제한 파일을 되살리는 곳이 있다고 볼 수 있습니다 (짐작). 사진 (iCloud Photos) 에도 설정, 내려받기, "내려받은 상태로 유지", 올리기 항목이 따로 있습니다.

포렌식에서 이 폴더를 보는 이유는 아래와 같습니다.

- 폴더 안 파일 이름으로 아이클라우드와 맞춘 파일 목록을 봅니다.
- 파일 내용이 PC 에 있었는지는 앱 버전과 파일 상태에 따라 다릅니다.
- 이 구분에 따라 보고서에 "이 PC 에 그 파일의 내용이 있었다" 라고 쓸 수 있는지가 갈립니다.

## 위치와 버전별 차이

| 기록 | 위치 | 근거 |
|---|---|---|
| 드라이브 폴더 (기본) | `C:\Users\[사용자 이름]\iCloud Drive` | [1] |
| 드라이브 폴더 (옮긴 경우) | 사용자가 고른 NTFS 드라이브 | [2] (버전 14 이상) |
| 사진 폴더 | 공개 자료 없음 | — |
| 앱 설정·로그 | 공개 자료 없음 | — |
| 동기화 루트 등록 | `SyncRootManager` 에 아이클라우드 키가 생기는지 검체에서 확인 | — |

| iCloud for Windows | 내용 |
|---|---|
| 7 | 아이클라우드 드라이브 내용을 모두 자동으로 내려받습니다 |
| 14 이상 | 드라이브 저장 위치를 바꿀 수 있습니다 |
| 14 이상 | 다른 드라이브로 옮기려면 그 드라이브가 NTFS 여야 합니다 |

- Windows 버전에 따라 흔적이 달라지는지는 공개 자료가 없습니다.

## 구조

### 드라이브 폴더

- 폴더 안 파일과 하위 폴더의 이름·크기·시각은 NTFS 에 남습니다. 읽는 법은 [마스터 파일 테이블](../filesystem/mft.md) 에 있습니다.
앱이 클라우드 파일 API 를 쓴다면 파일마다 내용이 PC 에 있는지를 파일 특성과 재분석 지점으로 가릴 수 있지만, 아이클라우드가 이 API 를 쓰는지는 공개 자료가 없습니다. 확인하려면 SOFTWARE 하이브의 `SyncRootManager` 하위 키 이름을 보고, 동기화 루트 ID 의 첫 부분이 공급자 ID (Storage Provider ID) 입니다.

- ID 형식과 키 안의 값은 [클라우드 동기화 공통 구조](cloud-files-api-syncrootmanager.md) 에 있습니다.

### 파일 상태

| 안내서 항목 | 흔적과의 관계 |
|---|---|
| 파일을 내려받은 상태로 유지 | 사용자가 고른 파일은 내용이 PC 에 늘 있을 수 있습니다 (짐작) |
| 내려받기·공유 상태 보기 | 파일마다 내려받았는지, 공유했는지 상태가 있습니다. 이 상태를 PC 어디에 적는지는 공개 자료가 없습니다 |
| 최근 삭제된 파일 복구 | 지운 파일을 되살리는 곳이 있습니다. 그곳이 PC 에 있는지 클라우드에 있는지는 공개 자료가 없습니다 |

> 그림 자리: 드라이브 폴더의 파일을 "내용이 PC 에 있음 / 이름만 있음" 으로 가르는 흐름. 앱 버전 확인 → 파일 특성 확인 → 결론 순서.

### 사진

사진에도 "내려받은 상태로 유지" 항목이 있어서 사진도 필요할 때 내려받는 방식일 수 있습니다 (짐작). 사진 폴더의 기본 위치는 공개 자료가 없고, 흔히 `사진\iCloud Photos` 로 거론합니다.

### 앱 자료 폴더 (후보)

- 흔히 거론하는 후보는 아래와 같습니다. 검체에 있는지 확인합니다.
  - 스토어 앱 패키지 이름 `AppleInc.iCloud_…` 와 `%LOCALAPPDATA%\Packages\…` 아래의 설정·로그 폴더
  - 스토어 판 이전 설치본의 `%APPDATA%\Apple Computer` 폴더
- 스토어 앱 폴더를 읽는 법은 [UWP 앱 데이터 구조](../../01-foundations/app-mail-data/packages-settings-dat.md) 에 있습니다.

## 증거로서 의미

### 증명하는 것

- 드라이브 폴더에 있는 파일 이름은, 이미지를 뜬 시점에 그 이름의 항목이 동기화 폴더에 있었다는 기록입니다.
- 버전 7 은 드라이브 내용을 모두 내려받습니다. 그래서 폴더 안 파일의 내용도 PC 에 있었다고 볼 근거가 됩니다. 그래도 파일마다 특성과 크기를 확인합니다.
- 드라이브 폴더가 기본 위치가 아닌 NTFS 드라이브에 있으면, 저장 위치를 바꾼 적이 있다고 볼 수 있습니다 (짐작).
- `SyncRootManager` 에 아이클라우드 공급자 키가 있으면, [클라우드 동기화 공통 구조](cloud-files-api-syncrootmanager.md) 의 해석을 그대로 씁니다.

### 증명하지 못하는 것

- 버전 7 보다 새 버전에서는 폴더에 파일 이름이 있어도 내용이 PC 에 있었다고 단정하지 않습니다. 이름만 있고 내용은 클라우드에만 있을 수 있습니다.
- 폴더 이름이 `iCloud Drive` 라고 해서 아이클라우드가 만든 폴더라고 단정하지 않습니다. 사용자가 같은 이름의 폴더를 직접 만들 수 있습니다. 설치 기록과 함께 봅니다.
- 폴더에 파일이 있다는 것만으로는 이 PC 에서 올린 파일인지, 다른 기기에서 올린 파일을 받은 것인지 가르지 못합니다.
- 누가 파일을 공유했는지, 언제 클라우드에 올라갔는지는 폴더만으로 알 수 없습니다.
- 폴더에 없는 파일이 원래 없었다는 뜻도 아닙니다. 최근 삭제한 파일을 되살리는 기능이 있습니다.
- 그 시각에 누가 PC 앞에 있었는지는 알 수 없습니다. 이 질문은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.

## 시각 해석

- 아이클라우드 앱이 따로 남기는 시각 기록은 공개 자료가 없습니다.
- 드라이브 폴더 안 파일의 시각은 NTFS 가 적는 파일 시각입니다. 형식과 시간대는 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- 이 시각이 클라우드 쪽 시각을 옮겨 적은 것인지, PC 에서 파일을 받은 시각인지는 알려지지 않았습니다.
- 그래서 파일 시각을 "사용자가 이 PC 에서 파일을 만든 시각" 으로 읽지 않습니다.
- 저장 위치를 옮길 때 파일 시각이 어떻게 되는지도 알려지지 않았습니다.
- 파일이 이 PC 의 폴더에 언제 생기고 언제 지워졌는지는 [USN 변경 저널](../filesystem/usnjrnl.md) 과 맞춰 봅니다.

## 함정과 한계

- **기본 위치만 보지 않습니다.** 버전 14 부터는 드라이브 저장 위치를 다른 드라이브로 옮길 수 있습니다. 옮길 드라이브는 NTFS 여야 합니다[2]. 그래서 NTFS 볼륨은 모두 찾아보고, FAT·exFAT 볼륨은 저장 위치 후보에서 뺍니다.
- **앱 버전을 먼저 적습니다.** 버전 7 은 모두 내려받고, 새 버전은 필요할 때 내려받는 방식으로 보입니다. 버전에 따라 "내용이 PC 에 있었나" 의 답이 달라집니다.
- **자동으로 내려받는 조건을 결론으로 쓰지 않습니다.** 1MB 보다 작은 파일은 자동으로 내려받습니다[2]. 이 조건이 어느 버전부터인지, 예외가 있는지는 알려지지 않았습니다. 그래서 1MB 보다 작은 파일도 파일마다 특성과 크기로 내용이 PC 에 있었는지 확인합니다.
- **살아 있는 PC 에서 폴더 파일을 읽지 않습니다.** 앱이 필요할 때 내려받는 방식이면, 파일을 읽는 순간 내용을 가져올 수 있습니다. 파일 특성 `RECALL_ON_DATA_ACCESS` 가 켜진 파일은 읽으면 원격 저장소에서 가져옵니다. 목록과 특성만 모으고, 절차는 [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) 을 따릅니다.
- **저장 위치를 바꾼 흔적을 의심합니다.** 저장 위치를 바꾸기 전에 아이클라우드 드라이브가 켜져 있으면 먼저 꺼야 합니다[2]. 끌 때 로컬 파일이 어떻게 되는지는 알려지지 않았습니다. 옛 위치에 파일이 남았거나 새 위치 폴더가 비었다면 이 절차를 떠올립니다.
- **NTFS 조건만으로 클라우드 파일 API 를 쓴다고 판단하지 않습니다.** 둘의 관계는 [클라우드 동기화 공통 구조](cloud-files-api-syncrootmanager.md) 에 정리했습니다. `SyncRootManager` 키로 직접 확인합니다.
- **앱 자료 위치를 모릅니다.** 설정·로그 파일 이름과 위치는 공개 자료가 없습니다. 위 후보 폴더가 검체에 있는지부터 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

1. 디스크 이미지의 MFT 에서 드라이브 폴더 아래 파일의 레코드를 찾습니다.
2. `$STANDARD_INFORMATION` 속성에서 파일 특성 값을 읽습니다. 속성의 위치와 배치는 [마스터 파일 테이블](../filesystem/mft.md) 에 있습니다.
3. 값을 비트로 나눕니다.
4. 재분석 지점 속성이 붙었는지 봅니다. 붙었다면 태그 값을 적습니다.

아래는 파일 특성 상수 정의[3]로 만든 예시입니다. 검체에서 나온 값이 아닙니다.

```
파일 특성 값 0x00401620 (리틀 엔디언 바이트: 20 16 40 00)

  0x00400000  RECALL_ON_DATA_ACCESS
  0x00001000  OFFLINE
  0x00000400  REPARSE_POINT
  0x00000200  SPARSE_FILE
  0x00000020  ARCHIVE
```

- 각 비트의 뜻, `0x40000` 을 읽을 때의 함정, 재분석 태그 해석은 [클라우드 동기화 공통 구조](cloud-files-api-syncrootmanager.md) 에 있습니다.
- 드라이브 폴더 파일에 재분석 지점이 하나도 없다면, 아이클라우드가 이 볼륨에서 클라우드 파일 API 방식을 쓰지 않았을 수 있습니다 (짐작).

### 공개 도구로 한 번

1. `SOFTWARE` 하이브와 트랜잭션 로그를 사본으로 뜹니다. 레지스트리 하이브 뷰어로 `SyncRootManager` 하위 키 이름을 모두 적습니다.
2. 아이클라우드 공급자로 보이는 키가 있으면 `UserSyncRoots` 값에서 사용자 SID 와 폴더 경로를 읽습니다. 없으면 이 API 를 쓰지 않았거나 키가 지워졌을 수 있습니다.
3. 설치 기록에서 iCloud for Windows 의 버전을 찾습니다. [설치 프로그램](../system-account/uninstall.md) 과 [스토어 앱 설치 목록](../system-account/appx-staterepository.md) 을 모두 봅니다.
4. MFT 파서로 모든 NTFS 볼륨의 파일 목록을 뽑습니다. `iCloud Drive` 라는 이름의 폴더를 찾고, 그 아래 파일의 특성 칸을 봅니다.
5. 사용자 프로필에서 사진 폴더와 앱 자료 폴더 후보가 있는지 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 클라우드 동기화 공통 구조 | `SyncRootManager` 에 아이클라우드 공급자 키가 있는지, 파일 특성의 뜻을 봅니다 | [클라우드 동기화 공통 구조](cloud-files-api-syncrootmanager.md) |
| 마스터 파일 테이블 | 드라이브 폴더 파일의 이름·크기·시각·특성을 봅니다 | [마스터 파일 테이블](../filesystem/mft.md) |
| USN 변경 저널 | 폴더 안 파일이 언제 생기고 바뀌고 지워졌는지 봅니다 | [USN 변경 저널](../filesystem/usnjrnl.md) |
| 설치 프로그램·스토어 앱 설치 목록 | 앱을 깔았는지, 어느 버전인지 봅니다 | [설치 프로그램](../system-account/uninstall.md), [스토어 앱 설치 목록](../system-account/appx-staterepository.md) |
| 셸백·바로가기 파일·점프리스트 | 드라이브 폴더를 둘러보거나 그 안 파일을 연 기록을 찾습니다 | [셸백](../file-folder-usage/shellbags/index.md), [바로가기 파일](../file-folder-usage/lnk.md), [점프리스트](../file-folder-usage/jump-lists.md) |
| SRUM | 앱별 네트워크 송수신 양을 봅니다 | [SRUM](../execution/system-resource-usage-monitor/index.md) |

- 반출 여부를 따지는 흐름은 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에 있습니다.
- 지운 파일을 따지는 흐름은 [지운 파일의 흔적 찾기](../../04-scenarios/activity/deleted-file-traces.md) 에 있습니다.

## 실습

iCloud for Windows 를 쓴 공개 검체(NIST CFReDS 등)나 직접 만든 시험 PC 에서 아래 질문을 풀어 봅니다.

1. 설치 기록에 나온 iCloud for Windows 버전은 무엇입니까? 버전 7 과 14 가운데 어느 쪽 설명이 맞습니까?
2. `C:\Users\<사용자>\iCloud Drive` 폴더가 있습니까? 없다면 다른 NTFS 볼륨에 같은 이름의 폴더가 있습니까?
3. `SyncRootManager` 에 아이클라우드 공급자로 보이는 키가 있습니까? 있다면 공급자 ID 는 무엇입니까?
4. 드라이브 폴더 파일 가운데 `OFFLINE` 이나 `RECALL_ON_DATA_ACCESS` 가 켜진 파일은 몇 개입니까?
5. 재분석 지점이 붙은 파일이 있다면 태그 값은 무엇입니까? OneDrive 파일의 태그 값과 같습니까?
6. 사진 폴더는 어디에 있습니까? 앱 자료 폴더 후보 가운데 실제로 있는 것은 무엇입니까?

## 참고 문헌

1. Apple 지원, "iCloud for Windows User Guide" — https://support.apple.com/guide/icloud-windows/welcome/icloud
2. Apple 지원, iCloud for Windows 사용자 안내서 "Set up iCloud Drive" — https://support.apple.com/guide/icloud-windows/set-up-icloud-drive-icw0144825a5/icloud
3. Microsoft Learn, "File Attribute Constants (WinNT.h)" (2025-09-23 갱신) — https://learn.microsoft.com/en-us/windows/win32/fileio/file-attribute-constants
4. Microsoft Learn, "StorageProviderSyncRootInfo.Id Property (Windows.Storage.Provider)" — https://learn.microsoft.com/en-us/uwp/api/windows.storage.provider.storageprovidersyncrootinfo.id
