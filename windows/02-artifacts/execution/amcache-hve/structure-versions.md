---
title: "구조와 버전별 차이"
parent: "AmCache"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 860
---

# 구조와 버전별 차이 (Structure·Versions)

Amcache.hve 는 레지스트리 하이브 형식의 파일이고, 안에 든 키 구성은 Windows 버전이 아니라 이 파일을 채우는 라이브러리의 버전을 따릅니다. 키 구성은 크게 옛 형식(`File`·`Programs`)과 새 형식(`Inventory…`)으로 나뉩니다. 이 페이지는 두 형식의 키 구성, 하이브를 쓰는 주체, 버전마다 달라지는 시각의 뜻을 정리합니다.

## 무엇을 기록하나 · 왜 생기나

Windows 에는 응용 프로그램 호환성 인프라 (Application Compatibility Infrastructure) 가 있습니다. 오래된 프로그램이 새 Windows 에서도 돌도록 호환성 보정(심, Shim)을 거는 장치입니다. Amcache 는 이 장치가 남기는 기록입니다. 실행 파일·설치 프로그램·드라이버·장치 목록을 적습니다. 항목별 내용은 [AmCache 허브](index.md)와 각 항목 페이지에서 다룹니다.

이 기록은 `%WinDir%\System32` 에 있는 `ae` 로 시작하는 라이브러리들이 채웁니다(aecache.dll·aeevts.dll·aeinv.dll·aelupsvc.dll·aepdu.dll·aepic.dll). Microsoft 는 이 라이브러리를 업데이트로 옛 Windows 에도 배포합니다. Windows 7 에는 KB2952664 가, Windows 8·8.1 에는 KB2976978 이 이 업데이트입니다. 그래서 업데이트를 받은 Windows 7 과 같은 시기의 Windows 10 은 같은 형식의 Amcache 를 씁니다. KB2952664 를 받은 Windows 7 에서는 Amcache.hve 와 RecentFileCache.bcf 가 함께 갱신됩니다.

## 위치와 버전별 차이

### 파일 위치

| 파일 | 위치 | 설명 |
|---|---|---|
| Amcache.hve | `%WinDir%\AppCompat\Programs\` | 본 하이브입니다 |
| Amcache.hve.LOG1·Amcache.hve.LOG2 | 같은 폴더 | 트랜잭션 로그 (Transaction Log) 입니다. 하이브에 아직 반영되지 않은 변경이 여기에만 있을 수 있습니다 |
| RecentFileCache.bcf | 같은 폴더 | Amcache.hve 이전 형식입니다. [구버전 실행 기록](recentfilecache-bcf.md)에서 다룹니다 |
| AEINV_*.xml·FullCompatReport.xml | 같은 폴더 | 일부 라이브러리 버전에서만 생기는 보고서 파일입니다. 10.0.10586 부터는 보이지 않습니다 |
| INSTALL_*.xml·INSTALL_*.txt | `%WinDir%\AppCompat\Programs\Install\` | 설치 과정 기록입니다. 6.2~10.0.14913 은 XML 이고, 10.0.16299 에서는 쓰지 않으며, 10.0.17134 부터 TXT 로 다시 생깁니다 |
| APPRAISER_*.xml·APPRAISER_*.bin | `%WinDir%\AppCompat` 아래 `appraiser` 폴더 | Appraiser 작업이 쓰는 파일입니다. 공개 자료에 위치 표기가 두 가지로 나와 있어 실제 기기에서 확인합니다 |

### 라이브러리 버전과 키 구성

아래 표는 라이브러리 버전별로 실험해 얻은 차이입니다. 표의 "처음 실린 Windows" 는 그 라이브러리가 기본으로 들어 있던 Windows 입니다. 업데이트로 라이브러리가 바뀌면 OS 가 옛것이어도 새 라이브러리의 형식을 따릅니다.

| 라이브러리 버전 | 처음 실린 Windows | Amcache.hve 키 구성 |
|---|---|---|
| 6.1.7600·6.1.7601 | 7 (SP0·SP1), Server 2008 R2 | Amcache.hve 가 없습니다. RecentFileCache.bcf 만 씁니다 |
| 6.2.9200 | 8, Server 2012 | Amcache.hve 가 처음 생깁니다. `File`·`Programs`·`Orphan`·`Generic` 네 키입니다(옛 형식) |
| 6.3.9600 | 8.1, Server 2012 R2 | 6.2 와 같습니다 |
| 10.0.10240 | 10 1507 | `Device`·`HwItem`·`Metadata` 가 생기지만 실험에서 늘 비어 있었습니다. `Generic` 도 비었습니다. `File` 은 GUI 가 없는 실행 파일을, 프로그램에 속하거나 Windows 구성 요소일 때만 적습니다 |
| 10.0.10586 | 10 1511 | 키 구성은 같습니다. 예약 작업이 하이브를 쓰지 않습니다 |
| 10.0.14913 | 10 1607 | `Inventory…` 계열 키 8개가 생깁니다. 옛 키와 새 키가 함께 채워집니다 |
| 10.0.16299 | 10 1709 | 옛 키 4개는 남아 있지만 비어 있습니다. 새 키 5개가 생깁니다 |
| 10.0.17134·10.0.17763 | 10 1803·1809 | 옛 키 4개와 `Device`·`HwItem`·`Metadata` 가 사라집니다. 새 키 11개가 생깁니다 |

ANSSI 의 실험은 10.0.17763 까지입니다. 그 뒤 버전(Windows 10 뒤 버전과 Windows 11)을 라이브러리 버전별로 정리한 공개 연구는 없으므로 실제 데이터로 확인해야 합니다. 요즘 시스템의 Amcache 에서는 `InventoryApplicationFile`·`InventoryApplication`·`InventoryDriverBinary`·`InventoryApplicationShortcut` 이 중심입니다.

### 하이브를 누가 언제 쓰나

Amcache 는 한 곳에서만 쓰는 기록이 아니라, 실행할 때와 설치할 때와 예약 작업 (Scheduled Task) 이 돌 때 서로 다른 주체가 씁니다. 이 차이가 키 시각의 뜻을 바꿉니다.

| 라이브러리 버전 | 실행할 때 | 설치할 때 | 예약 작업 |
|---|---|---|---|
| 6.1 | AeLookupSvc 서비스가 심이 필요한 실행 파일 경로를 RecentFileCache.bcf 에 적습니다 | — | ProgramDataUpdater 가 매일 00:30 에 bcf 를 비우고 XML 을 씁니다. 컴퓨터가 3분 이상 쉬고 있을 때만 돕니다 |
| 6.2·6.3 | AeLookupSvc 가 심이 필요한 실행 파일을 Amcache.hve 에 적습니다 | PcaSvc 서비스가 aeinv.dll 을 불러 Install 폴더와 Amcache.hve 에 씁니다 | ProgramDataUpdater 가 유지 관리 작업 (Maintenance Task) 으로 3일마다 하이브를 갱신합니다. 6.3.9600.17415 부터 Microsoft Compatibility Appraiser 작업이 생기지만 FullCompatReport.xml 만 씁니다 |
| 10.0.10240 | AeLookupSvc 가 없어지고 DiagTrack 서비스가 씁니다 | PcaSvc | ProgramDataUpdater 가 하이브를 갱신합니다 |
| 10.0.10586 | DiagTrack | PcaSvc(compattelrunner.exe 를 거쳐 aeinv.dll 호출) | 두 예약 작업 모두 하이브를 쓰지 않습니다 |
| 10.0.14913 | DiagTrack | PcaSvc 가 `InventoryApplication` 에 적습니다 | 두 작업 모두 하이브를 씁니다. `Programs` 는 ProgramDataUpdater 가, `InventoryApplicationFile`·`InventoryDriverBinary` 는 Appraiser 가 채웁니다 |
| 10.0.16299 이후 | DiagTrack | PcaSvc | Appraiser 가 사용자 바탕 화면·`Program Files`·`Program Files (x86)` 의 EXE 와 시작 메뉴의 LNK 를 찾아 적습니다. `InventoryApplication` 은 돌 때마다 다시 씁니다. ProgramDataUpdater 는 하이브를 쓰지 않습니다 |

## 구조

Amcache.hve 는 일반 레지스트리 하이브 (regf) 입니다. 기본 블록·hbin·셀 구조는 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)와 [하이브 내부 구조](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)에서 다룹니다. 이 페이지는 `Root` 키부터 경로를 적습니다.

### 옛 형식 (6.2.9200 ~ 10.0.14913)

```
Root                              값 Sync: ProgramDataUpdater 마지막 실행 시각
├─ File\{볼륨 GUID}\{파일 ID}       실행 파일 하나에 키 하나
├─ Programs\{ProgramId}           설치 프로그램 하나에 키 하나
├─ Orphan\{볼륨 GUID}@{파일 ID}     프로그램에 속하지 않은 실행 파일
└─ Generic\0\{0000+SHA-1}          설치된 드라이버
```

- `File` 아래 첫 단계는 볼륨 GUID (Volume GUID) 입니다. 이 GUID 는 SYSTEM 하이브의 [MountedDevices](../../external-devices/usb-storage-artifacts/mounteddevices.md)에 있는 볼륨 GUID 와 같습니다.
- 둘째 단계는 파일 ID 입니다. NTFS 에서는 MFT 순번(Sequence Number) 뒤에 MFT 항목 번호를 8자리 16진수로 붙입니다. 순번 5, 항목 번호 0xF99C 인 파일의 키 이름은 `50000f99c` 입니다. MFT 항목 번호와 순번은 [MFT 레코드와 속성](../../../01-foundations/disk-volume/ntfs/file-record-attribute.md)에서 다룹니다.
- FAT 볼륨에서는 파일 ID 자리에 디렉터리 항목의 바이트 오프셋이 들어갑니다.
- `Orphan` 아래 키에는 값 `c` 하나만 있습니다. 값은 0 이나 1 입니다.
- `Generic\0` 아래에는 드라이버 SHA-1 앞에 `0000` 을 붙인 이름의 키가 있습니다. 같은 자리에 장치 모델 ID(DeviceModelId) 로 보이는 GUID 이름의 키도 있습니다.

`File` 아래 실행 파일 키의 값은 아래와 같습니다. 값 이름이 숫자라서, 아래 뜻은 공개 분석으로 밝혀진 것입니다.

| 값 | 뜻 | 형식 |
|---|---|---|
| 0·1·c | 제품 이름·회사 이름·파일 설명 | 문자열 |
| 2·5 | 파일 버전(2 는 번호만) | 문자열 |
| 3 | 언어 코드 (1033 = en-US) | DWORD |
| 4 | SwitchBackContext | QWORD |
| 6 | 파일 크기 | DWORD |
| 7·9 | PE 헤더의 SizeOfImage·체크섬 | DWORD |
| 8 | PE 헤더 해시 (계산법은 공개되지 않았습니다) | 문자열 |
| f | 링크(컴파일) 시각 | DWORD, Unix 시각 |
| 11·17 | 마지막 수정 시각 두 벌 | FILETIME |
| 12 | 만든 시각 | FILETIME |
| 15 | 전체 경로 | 문자열 |
| 100 | ProgramId | 문자열 |
| 101 | SHA-1 (앞에 `0000`) | 문자열 |
| d | 이미지 버전(PE 헤더의 MajorImageVersion·MinorImageVersion)이라는 해석이 있습니다. 뜻은 확정되지 않았습니다 | DWORD |
| a·b·10·16 | 뜻이 확인되지 않았습니다 | — |

값 11 과 17 은 둘 다 수정 시각으로 보입니다. 17 은 11 과 거의 늘 1초 차이가 납니다. 11 은 수정 시각이거나 그보다 몇 초 뒤라는 해석이 있습니다. 값 101 은 비어 있는 키가 많습니다. 이유는 [AmCache 해석 함정](sha1.md)에서 다룹니다.

`Programs` 아래 프로그램 키의 값은 아래와 같습니다. 6.2 부터는 Uninstall 키에 등록된 프로그램만 적습니다.

| 값 | 뜻 |
|---|---|
| 0·1·2 | 프로그램 이름·버전·게시자 |
| 6 | 설치 방식 (Msi, AddRemoveProgram 등) |
| 7 | Uninstall 하위 키 이름 |
| a | 설치 시각 (Unix 시각) |
| b | 제거 시각 (Unix 시각). 아직 설치돼 있으면 0 입니다 |
| d | 설치 폴더와, 실행 파일이 든 하위 폴더 |
| Files | 설치로 생긴 실행 파일 목록. 항목마다 `{볼륨 GUID}@{파일 ID}` 형식입니다 |
| 11·12 | MSI 제품 코드·패키지 코드 (MSI 로 설치한 경우). f·10 에도 같은 값이 들어갑니다 |
| 3·5·13 | 뜻이 확인되지 않았습니다 |
| 14~18 | 10.0.10240 에서 생긴 값입니다. 뜻이 확인되지 않았습니다 |

`Programs` 에는 제거된 프로그램도 남습니다. 제거된 프로그램은 값 b 에 제거 시각이 들어갑니다. 설치 프로그램 목록 자체는 [설치 프로그램 (Uninstall)](../../system-account/uninstall.md)과 대조합니다.

### 새 형식 (10.0.14913 부터)

```
Root
├─ InventoryApplicationFile\{키}       실행 파일
├─ InventoryApplication\{ProgramId}    설치 프로그램
├─ InventoryDriverBinary\{키}          드라이버 파일
├─ InventoryApplicationShortcut\{키}   바로가기 (10.0.16299 부터)
├─ InventoryDevicePnp\{키}             PnP 장치
└─ …                                   그 밖의 Inventory 계열 키
```

주요 키는 항목 페이지에서 따로 다룹니다.

- [실행 파일 항목 (InventoryApplicationFile)](inventoryapplicationfile.md)
- [설치 프로그램 항목 (InventoryApplication)](inventoryapplication.md)
- [드라이버 항목 (InventoryDriverBinary)](inventorydriverbinary.md)
- [바로가기 항목 (InventoryApplicationShortcut)](inventoryapplicationshortcut.md)
- [장치 항목 (InventoryDevicePnp)](inventorydevicepnp.md)

나머지 키가 처음 보인 버전은 아래와 같습니다.

| 처음 보인 버전 | 키 |
|---|---|
| 10.0.14913 | InventoryDriverPackage, DeviceCensus(OS 정보), InventoryDeviceMediaClass, InventoryDeviceContainer |
| 10.0.16299 | DriverPackageExtended, InventoryDeviceInterface(센서), InventoryDeviceUsbHubClass(USB 포트 수), InventoryApplicationFramework |
| 10.0.17134 | InventoryApplicationAppV(늘 비어 있었음), InventoryApplicationDriver(드라이버를 설치한 프로그램), InventoryMiscellaneousOffice 로 시작하는 키 8개, InventoryMiscellaneousUUPInfo |

키 이름을 짓는 방식도 버전에 따라 바뀌었습니다.

| 키 | 10.0.14913 | 10.0.16299 부터 |
|---|---|---|
| InventoryApplicationFile 아래 | 소문자 전체 경로(UTF-16LE)의 SHA-1 앞에 `0000` 을 붙인 이름 | `파일 이름\|해시` 형식. 해시 계산법은 밝혀지지 않았습니다 |
| InventoryDriverBinary 아래 | 드라이버 SHA-1 앞에 `0000` 을 붙인 이름 | 드라이버 전체 경로. SHA-1 은 값 `DriverId` 로 옮겨 갑니다 |
| InventoryApplication 아래 | ProgramId | ProgramId |

값 이름은 새 형식부터 `Name`·`Publisher`·`LinkDate` 처럼 영어 단어입니다. Amcache.hve 파일을 따로 설명한 Microsoft 문서는 없습니다. 대신 Microsoft 진단 데이터 문서에 같은 이름의 인벤토리 이벤트(예: `InventoryApplicationFileAdd`, `InventoryDriverBinaryAdd`)와 필드 설명이 있습니다. 진단 데이터에서 ProgramId 는 앱의 Name·Version·Publisher·Language 로 만든 해시입니다. 필드 뜻을 짐작하는 자료로 쓸 수 있지만, 하이브 값과 같다는 보장은 없습니다.

## 증거로서 의미

이 절은 키 구성과 버전 판별이 알려 주는 것만 다룹니다. 실행 증거로서의 의미는 [AmCache 해석 함정](sha1.md)에서 다룹니다.

| 알려 주는 것 | 알려 주지 못하는 것 |
|---|---|
| 하이브를 채운 라이브러리의 세대. 키 구성으로 범위를 좁힐 수 있습니다 | 설치된 Windows 버전. 라이브러리는 업데이트로 바뀝니다 |
| 옛 형식 `Root` 의 `Sync` 값: 마지막 ProgramDataUpdater 실행 시각 (6.2 기준) | 라이브러리가 언제 바뀌었는지. 업데이트 기록과 맞춰 봐야 합니다 |
| 새 형식의 `LastScanTime` 값: 마지막 Appraiser 실행 시각 | 비어 있는 키가 "그런 활동이 없었다" 는 것 |

## 시각 해석

- 하이브 안에는 시각 형식이 섞여 있습니다. 옛 형식 `File` 의 값 11·12·17 과 `Root` 의 `Sync` 는 FILETIME 입니다. 값 f 와 `Programs` 의 a·b 는 Unix 시각입니다. 변환은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다.
- FILETIME 은 정의상 UTC 기준이며, `Sync` 값도 UTC 입니다.
- 기본 블록 (Base Block) 의 마지막 기록 시각은 Win8.1 부터 갱신되지 않으므로, 이 값으로 Amcache 가 마지막으로 바뀐 때를 판단하지 않습니다.
- 키 마지막 기록 시각 (Last Write Time) 은 키가 마지막으로 바뀐 때입니다([키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md)). Amcache 에서는 이 시각을 누가 바꿨는지가 버전마다 다릅니다. 아래 표는 ANSSI 실험 결과입니다.

| 라이브러리 버전 | 키 | 키 시각이 맞았던 것 |
|---|---|---|
| 6.2·6.3 | `File` 아래 실행 파일 키 | 경우마다 다릅니다. 실행 시각, 실행 뒤 첫 ProgramDataUpdater 시각, 프로그램 설치 시각 가운데 하나였습니다. Windows 구성 요소는 어느 것과도 맞지 않았습니다 |
| 10.0.10240 | `File` 아래 실행 파일 키 | 대부분 ProgramDataUpdater 실행 시각이었습니다 |
| 10.0.10586 | `File` 아래 실행 파일 키 | 첫 실행 시각이나 프로그램 설치 시각이었습니다 |
| 10.0.14913 | `InventoryApplicationFile` | 늘 Appraiser 실행 시각이었습니다 |
| 10.0.14913 | `Programs` / `InventoryApplication` | ProgramDataUpdater 실행 시각 / 설치 시각이었습니다 |
| 10.0.16299 이후 | `InventoryApplication` | Appraiser 가 다시 쓴 시각입니다. 설치 시각이 아닙니다 |
| 10.0.16299 이후 | `InventoryApplicationFile` | 심이 필요한 GUI 실행 파일은 첫 실행 시각이었습니다. 나머지는 실행 시각과, 파일이 생긴 뒤 첫 Appraiser 실행 시각 가운데 이른 쪽이었습니다 |

같은 "키 시각" 이라도 버전을 모르면 뜻을 정할 수 없습니다. 보고서에는 판별한 라이브러리 세대와 그 근거를 함께 적습니다.

## 함정과 한계

1. **OS 버전으로 형식을 단정합니다.** 형식은 라이브러리 버전을 따릅니다. KB2952664 를 받은 Windows 7 에도 새 형식 키가 있을 수 있습니다.
2. **업그레이드한 시스템의 옛 파일을 놓칩니다.** 라이브러리가 바뀌어도 이전 형식의 파일이 남아 계속 쓰일 수 있습니다. Windows 7 에서 RecentFileCache.bcf 와 Amcache.hve 가 함께 있는 경우가 그 예입니다.
3. **빈 키를 "기록 없음" 으로 읽습니다.** 10.0.16299 에서는 옛 키 4개가 빈 채로 남습니다. 빈 키는 지운 흔적이 아닐 수 있습니다. 항목이 없다는 사실만으로 내릴 수 있는 결론은 공개 연구에 정리되어 있지 않습니다.
4. **도구가 한쪽 형식만 읽습니다.** 도구마다 읽는 키가 다릅니다. 도구 결과에 없는 키가 하이브에 있는지 트리를 직접 열어 확인합니다([도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)).
5. **트랜잭션 로그를 빼고 읽습니다.** 최근 항목이 LOG1·LOG2 에만 있을 수 있습니다. 로그를 반영하는 방법은 [트랜잭션 로그와 반영 안 된 변경](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md)에서 다룹니다.
6. **뜻이 밝혀지지 않은 값을 해석합니다.** 옛 형식 값 이름의 뜻은 대부분 코드 분석이 아니라 실험으로 얻은 것입니다. "뜻이 확인되지 않았습니다" 인 값은 보고서 근거로 쓰지 않습니다.
7. **1809 이후 동작을 옛 연구로 설명합니다.** 이 페이지의 버전별 동작은 10.0.17763 까지의 실험입니다. 뒤 버전에서는 실제 데이터로 다시 확인하고, 어느 버전에서 확인했는지 보고서에 적습니다.

Amcache.hve 도 레지스트리 하이브이므로 지운 키가 빈 셀이나 트랜잭션 로그에 남을 수 있습니다([지워진 키·값 복구](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md)). 섀도 복사본 안의 옛 Amcache.hve 와 비교하면 사라진 항목을 찾을 수 있습니다([섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)).

## 직접 분석해 보기

### 헥스로 한 번

먼저 기본 블록에서 하이브 상태를 확인합니다. 아래는 regf 형식 명세를 보고 만든 예시입니다. 실제 데이터에서 뽑은 값이 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00000000  72 65 67 66 5C 03 00 00 5B 03 00 00 00 E4 97 34
00000010  A2 76 DA 01 01 00 00 00 05 00 00 00 00 00 00 00
00000020  01 00 00 00 20 00 00 00 00 90 1C 00 01 00 00 00
```

1. `72 65 67 66` 는 `regf` 서명입니다. 확장자가 .hve 라도 일반 하이브와 형식이 같습니다.
2. 오프셋 4 의 `5C 03 00 00` 은 첫째 순번 (Primary Sequence Number) 0x35C 입니다.
3. 오프셋 8 의 `5B 03 00 00` 은 둘째 순번 (Secondary Sequence Number) 0x35B 입니다.
4. 두 순번이 다르므로 이 하이브는 쓰기가 끝나지 않은 상태(dirty)입니다. 오프셋 508 의 체크섬이 틀려도 같은 상태로 봅니다. 이때는 LOG1·LOG2 를 반영해야 가장 새 내용이 보입니다.
5. 오프셋 12 의 8바이트(`00 E4 … DA 01`)는 기본 블록의 마지막 기록 시각입니다. Win8.1 부터 갱신되지 않으므로 해석에 쓰지 않습니다.
6. 오프셋 36 의 `20 00 00 00` 은 루트 셀 오프셋 0x20 입니다. 이 값은 hbin 데이터 시작(파일 오프셋 4096)에서 센 값입니다. 그래서 루트 키 셀은 파일 오프셋 0x1020 에 있습니다.
7. 루트 키에서 `Root` 키와 그 하위 키 이름을 차례로 따라갑니다. 키 셀을 읽는 법은 [하이브 내부 구조](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)에서 다룹니다.

### 공개 도구로 한 번

레지스트리 하이브를 읽는 공개 도구면 무엇이든 됩니다. regipy, python-registry, yarp 같은 라이브러리나 Registry Explorer, RegRipper 가 그 예입니다. 형식은 아래 순서로 판별합니다.

1. 원본이 아닌 사본에서 작업합니다. Amcache.hve 와 LOG1·LOG2 를 함께 복사합니다.
2. 로그를 반영한 상태로 엽니다. 도구가 로그를 반영했는지 확인합니다.
3. `Root` 바로 아래 하위 키 이름과 하위 키 개수를 뽑습니다.
4. 위의 "라이브러리 버전과 키 구성" 표와 맞춥니다. `File` 에 하위 키가 있고 `Inventory…` 키가 없으면 6.2~10.0.10586 세대입니다. 둘 다 채워져 있으면 10.0.14913 세대입니다. `File` 이 비어 있으면 10.0.16299 세대입니다. `File` 이 없고 `InventoryApplicationDriver` 가 있으면 10.0.17134 이후 세대입니다.
5. 판별 결과와 근거(보인 키 목록)를 기록해 둡니다. 시각 해석은 이 결과에 맞춰 합니다.

## 교차 검증

| 확인할 것 | 함께 볼 기록 |
|---|---|
| 라이브러리를 바꾼 업데이트(KB2952664·KB2976978)를 언제 받았나 | [윈도 업데이트 기록](../../system-account/windows-update-cbs-log.md) |
| 실제 OS 버전과 설치 시각 | [시스템 기본 정보](../../system-account/os-version-computer-name-install-date-shutdown-t.md) |
| ProgramDataUpdater·Microsoft Compatibility Appraiser 작업이 있고 돌았나 | [예약 작업](../../persistence/scheduled-tasks/index.md) |
| 실행 사실과 실행 시각 | [심캐시](../shimcache-appcompatcache.md), [프리페치](../prefetch/index.md), [프로그램 호환성 도우미](../pca.md), [BAM·DAM](../background-activity-moderator.md) |
| 설치·제거된 프로그램 | [설치 프로그램 (Uninstall)](../../system-account/uninstall.md) |

실행 흔적을 모아 보는 흐름은 [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md)에서 다룹니다.

## 실습

공개 실습 이미지(NIST CFReDS 등)에서 Amcache.hve 를 꺼내 아래 질문을 풀어 봅니다.

1. 기본 블록의 두 순번이 같은가요? 다르다면 로그를 반영하기 전과 뒤에 `Root` 아래 하위 키 개수가 달라지나요?
2. `Root` 아래 키 목록으로 라이브러리 세대를 판별하면 어느 것인가요? 그 판별이 이미지의 OS 버전과 맞나요?
3. 옛 형식 하이브라면 `Root` 의 `Sync` 값은 언제인가요? 그 시각이 `File` 아래 키 시각들과 어떻게 겹치나요?
4. 새 형식 하이브라면 `InventoryApplication` 아래 키들의 마지막 기록 시각이 한 시각에 몰려 있나요? 몰려 있다면 그것이 설치 시각이 아닌 이유를 설명해 봅니다.

## 참고 문헌

- Blanche Lagny (ANSSI), "Analysis of the AmCache v2" (2019) — https://cyber.gouv.fr/documents/632/anssi-coriin_2019-analysis_amcache-v2.pdf
- Yogesh Khatri, "Amcache.hve in Windows 8 - Goldmine for malware hunters", Swift Forensics (2013) — http://www.swiftforensics.com/2013/12/amcachehve-in-windows-8-goldmine-for.html
- Yogesh Khatri, "Amcache on Windows 7", Swift Forensics (2016) — http://www.swiftforensics.com/2016/05/amcache-on-windows-7.html
- Kaspersky, "AmCache artifact: forensic value and a tool for data extraction", Securelist (2025) — https://securelist.com/amcache-forensic-artifact/117622/
- Microsoft Learn, "Required diagnostic events and fields for Windows 10, versions 22H2 and 21H2" — https://learn.microsoft.com/en-us/windows/privacy/required-windows-diagnostic-data-events-and-fields-2004
- Maxim Suhanov, "Windows registry file format specification" — https://github.com/msuhanov/regf/blob/master/Windows%20registry%20file%20format%20specification.md
