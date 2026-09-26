---
title: "설치 프로그램 항목"
parent: "AmCache"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 880
---

# 설치 프로그램 항목 (InventoryApplication)

## 한 줄 요약

설치 프로그램 항목 (InventoryApplication) 은 `Amcache.hve` 하이브 안의 `Root\InventoryApplication` 키입니다. 윈도가 설치된 것으로 파악한 프로그램마다 하위 키가 하나씩 있고, 하위 키에는 이름·버전·게시자·설치 방식·설치 폴더·제거 키 경로·설치 날짜가 남습니다. 이 목록은 실행 기록이 아니라 설치 기록입니다. Windows 10 1709 무렵의 라이브러리부터는 목록 전체를 주기적으로 다시 쓰기 때문에 하위 키의 마지막 기록 시각은 설치 시각이 아닙니다.

## 무엇을 기록하나 · 왜 생기나

윈도는 설치된 프로그램이 새 버전과 잘 맞는지 점검하려고 설치 프로그램 목록(인벤토리, Inventory)을 만들고, 이 목록을 `Amcache.hve` 에 적는 곳이 이 키입니다.

설치 프로그램을 실행하면 [프로그램 호환성 도우미 (PCA)](../pca.md) 서비스가 `compattelrunner.exe -m:aeinv.dll -f:UpdateSoftwareInventory` 를 실행하고, 이때 `aeinv.dll` 이 하이브를 고칩니다[1]. 호환성 점검 예약 작업 (Microsoft Compatibility Appraiser) 도 이 키를 고치는데, 10.0.16299 버전 라이브러리부터는 작업이 돌 때마다 항목을 모두 다시 씁니다[1].

윈도는 같은 목록을 진단 데이터로 Microsoft 에 보내고, Microsoft 는 그 이벤트(`Microsoft.Windows.Inventory.Core.InventoryApplicationAdd`)의 필드 설명을 공개합니다[2]. 필드 이름이 이 키의 값 이름과 같아서 값의 뜻을 짐작하는 데 쓸 수 있습니다. 다만 두 쪽이 같다는 공식 보장은 없습니다.

목록에 들어오는 프로그램은 설치 방식으로 나뉩니다. `Source` 값이 그 구분입니다.

| `Source` 값 | 뜻 |
|---|---|
| `AddRemoveProgram` | 설치 파일(EXE)로 설치했고, 프로그램 추가/제거 목록 (Add/Remove Programs, ARP) 에 올라간 프로그램입니다. SOFTWARE 하이브의 제거(Uninstall) 키에 항목이 있습니다 |
| `AddRemoveProgramPerUser` | 사용자별로 설치한 프로그램입니다. 제거 키가 그 사용자의 하이브에 있습니다 |
| `Msi` | Windows Installer 로 설치한 프로그램입니다 |
| `AppxPackage` | 스토어 앱 패키지입니다. 자료에 따라 `AppXPackage` 로도 적습니다 |

옛 라이브러리에는 `File` 값도 있습니다. Windows 7 시절 XML 에서 이 값은 Run 키에 등록된 실행 파일을 가리켰습니다[1].

## 위치와 버전별 차이

| 항목 | 위치 |
|---|---|
| 하이브 파일 | `%SystemRoot%\AppCompat\Programs\Amcache.hve`. 같은 폴더에 트랜잭션 로그 `Amcache.hve.LOG1`·`.LOG2` 가 있습니다 |
| 프로그램 하나 | `Root\InventoryApplication\{ProgramId}` |
| 목록을 마지막으로 고친 시각 | `Root\InventoryApplication` 키 자체의 `LastScanTime` 값 (REG_QWORD) |

AmCache 의 모양은 Windows 버전보다 그 안의 `ae*.dll` 라이브러리 버전을 따릅니다. 라이브러리별 전체 흐름은 [구조와 버전별 차이](structure-versions.md)에서 다룹니다. 아래 표는 이 키와 관련된 부분만 추렸습니다[1].

| 라이브러리 버전 (처음 실린 Windows) | 설치 프로그램 목록 | 하위 키의 마지막 기록 시각 | 프로그램을 지우면 |
|---|---|---|---|
| 6.2 ~ 10.0.10586 (Windows 8 ~ 10 1511) | `Root\Programs` 키. 이 키는 아직 없습니다 | — | `Programs` 항목의 `b` 값에 제거 시각(Unix 시각)이 남습니다 |
| 10.0.14913 (Windows 10 1607) | 이 키가 새로 생깁니다. `Programs` 도 남아 있습니다 | 설치 시각과 맞습니다 | 이 키에서는 하위 키를 지웁니다. `Programs` 의 `b` 값에는 제거 시각이 남습니다 |
| 10.0.16299 이후 (Windows 10 1709~) | 점검 작업이 돌 때마다 항목을 모두 다시 씁니다. 10.0.17134 부터 `Programs` 키가 없어집니다 | 점검 작업이 돈 시각입니다 | 다음에 다시 쓸 때 목록에서 빠집니다 |

이 표는 10.0.17763 (Windows 10 1809) 까지의 동작입니다[1]. Windows 11 25H2 하이브에서도 하위 키 321개의 마지막 기록 시각이 모두 `LastScanTime` 16초 앞부터 42초 뒤 사이에 몰려 있어, 1709 이후 동작과 같습니다.

## 구조

저장 형식은 보통의 레지스트리 하이브입니다. 셀 구조는 [하이브 내부 구조](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)에서 다룹니다. 여기서는 값의 뜻만 봅니다.

"형식" 열은 Windows 10 21H2[4]와 Windows 11 25H2 하이브의 형식입니다. 두 판에 다 있는 값은 형식이 같습니다. "근거" 열의 "문서" 는 Microsoft 진단 데이터 문서[2]입니다.

| 값 | 형식 | 뜻 | 근거 |
|---|---|---|---|
| `ProgramId` | REG_SZ | 하위 키 이름과 같습니다. 이름·버전·게시자·언어로 만든 해시입니다 | 문서 |
| `ProgramInstanceId` | REG_SZ | 프로그램에 딸린 파일들의 ID 로 만든 해시입니다 | 문서 |
| `Name`·`Version`·`Publisher` | REG_SZ | 이름·버전·게시자입니다. 게시자를 어디서 가져오는지는 `Source` 에 따라 다릅니다 | 문서 |
| `Language` | REG_DWORD | 언어 식별자 (LCID) 입니다. 1033 은 영어(미국)입니다 | ANSSI |
| `Source` | REG_SZ | 설치 방식입니다. 위 표를 봅니다 | 문서 |
| `Type` | REG_SZ | `Application`·`Hotfix`·`BOE`·`Service`·`Unknown` 중 하나입니다. BOE 는 ARP·MSI 항목이 없는 앱입니다 | 문서 |
| `StoreAppType` | REG_SZ | 스토어 앱의 종류입니다(UWP, Win8StoreApp 등) | 문서 |
| `MsiProductCode`·`MsiPackageCode` | REG_SZ | MSI 제품·패키지 GUID 입니다 | 문서 |
| `HiddenArp` | REG_DWORD | 프로그램 추가/제거 목록에 나오지 않게 숨긴 프로그램인지 나타냅니다 | 문서 |
| `InboxModernApp` | REG_DWORD | 0 또는 1 입니다. 뜻을 설명한 공식 문서는 없습니다 |  |
| `OSVersionAtInstallTime` | REG_SZ | 설치 당시 OS 버전 네 자리입니다 | 문서 |
| `InstallDate` | REG_SZ | 설치 날짜 추정값입니다. 아래 "시각 해석" 을 봅니다 | 문서 |
| `MsiInstallDate` | REG_SZ | MSI 패키지에 적힌 설치 날짜입니다 | 문서 |
| `RootDirPath` | REG_SZ | 설치 폴더입니다 | 문서 |
| `UninstallString` | REG_SZ | 제거 명령입니다 | Psmths |
| `RegistryKeyPath` | REG_SZ | 이 항목을 만든 제거 키의 경로입니다. 예: `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\…` | Psmths |
| `PackageFullName`·`ManifestPath`·`BundleManifestPath` | REG_SZ | 스토어 앱의 패키지 전체 이름과 매니페스트 경로입니다 | 문서 |
| `UserSid` | REG_SZ | 사용자 SID 입니다. 사용자별 설치 항목과 일부 MSI 항목에만 있습니다. 공식 설명은 없습니다 |  |

라이브러리 버전에 따라 값 목록이 다릅니다. Windows 11 25H2 하이브에는 `Type` 과 `OSVersionAtInstallTime` 이 없을 수 있고, Microsoft 문서[2]에 있는 `InstallDateArpLastModified`·`InstallDateMsi`·`InstallDateFromLinkFile` 도 없을 수 있습니다.

### ProgramId 읽기

ProgramId 는 Name·Version·Publisher·Language 로 만든 해시이고[2], 계산 방법은 공개되지 않았습니다. 같은 프로그램의 같은 버전은 다른 PC 에서도 ProgramId 가 같고[1], 버전이 해시 입력에 들어가므로 업데이트한 뒤에는 다른 ProgramId 로 잡힐 수 있습니다.

- 하위 키 이름은 `0000` 으로 시작하는 16진 44자리입니다.
- 끝 네 자리는 `Language` 값을 리틀 엔디언 2바이트로 적은 것과 같습니다. 예를 들어 1033(0x0409)은 `0904`, 65535 는 `ffff` 입니다(Windows 11 25H2 기준). 공식 설명은 없습니다.

### 다른 키와 잇기

> 그림 자리: 가운데 InventoryApplication 하위 키(ProgramId)를 두고, InventoryApplicationFile 의 `ProgramId` 와 InventoryApplicationDriver 의 `ProgramIds` 가 이 키 이름을 가리키는 모습. `RegistryKeyPath` 가 SOFTWARE 또는 NTUSER.DAT 의 Uninstall 키를 가리키는 화살표도 함께 그립니다.

- [실행 파일 항목 (InventoryApplicationFile)](inventoryapplicationfile.md) 의 `ProgramId` 가 이 키의 하위 키 이름과 같으면, 그 실행 파일은 이 설치 프로그램에 딸린 파일입니다.
- ARP 항목이 없는 실행 파일은 파일 정보로 ProgramId 를 따로 만듭니다[2]. 이런 ProgramId 는 이 키에서 찾을 수 없습니다.
- `Root\InventoryApplicationDriver` 의 `ProgramIds` 값에는 그 드라이버를 설치한 프로그램의 ProgramId 가 들어 있습니다[1]. 드라이버 자체는 [드라이버 항목 (InventoryDriverBinary)](inventorydriverbinary.md)에서 봅니다.

## 증거로서 의미

### 증명하는 것

- 목록을 쓴 때에 윈도는 이 이름·버전·게시자의 프로그램을 설치된 것으로 파악했습니다.
- `Source` 로 설치 방식을 나눌 수 있습니다. 설치 파일, MSI, 스토어 앱, 사용자별 설치가 구분됩니다.
- `RegistryKeyPath` 가 있으면 그때 그 경로에 제거 키가 있었습니다.
- `RootDirPath` 는 윈도가 설치 폴더로 본 경로입니다.
- `Source` 가 `AddRemoveProgramPerUser` 인 항목은 `UserSid` 사용자의 하이브에 제거 키가 있었습니다. `RegistryKeyPath` 안의 SID 가 `UserSid` 와 같습니다. `UserSid` 가 있는 MSI 항목의 제거 키는 `HKEY_LOCAL_MACHINE` 아래에 있습니다.

### 증명하지 못하는 것

- 프로그램을 실행했다는 사실. 이 키는 설치 목록입니다. 실행 여부는 [프리페치](../prefetch/index.md) 같은 실행 흔적으로 따로 확인합니다. AmCache 전반의 같은 함정은 [AmCache 해석 함정](sha1.md)에서 다룹니다.
- 정확한 설치 시각. `InstallDate` 는 추정 날짜입니다.
- 수집한 때에도 설치되어 있었다는 사실. 목록은 `LastScanTime` 무렵의 모습입니다.
- 목록에 없는 프로그램은 설치된 적이 없다는 사실. 결론은 항목이 "있을 때" 만 냅니다[1].
- 누가 설치했는지. `Source` 가 `AddRemoveProgram` 인 항목에는 사용자 정보가 없습니다.

보고서 문장 예(괄호 안은 자리 표시입니다):

> `Amcache.hve` 의 InventoryApplication 에 이름 (이름), 버전 (버전), 게시자 (게시자), 설치 폴더 (경로) 인 항목이 있습니다. 이 목록의 `LastScanTime` 은 (UTC 시각) 입니다. 따라서 적어도 이 시각에 윈도는 이 프로그램을 설치된 것으로 파악하고 있었습니다. 이 항목만으로는 프로그램을 실행했는지 알 수 없습니다.

## 시각 해석

| 시각 | 저장 형식 | 무엇이 바뀔 때 바뀌나 | 주의 |
|---|---|---|---|
| 하위 키의 마지막 기록 시각 | FILETIME, UTC | 10.0.14913: 설치할 때. 10.0.16299 이후: 점검 작업이 목록을 다시 쓸 때 | 최신 시스템에서는 설치 시각으로 읽지 않습니다 |
| `LastScanTime` | REG_QWORD, FILETIME | 점검 작업이 마지막으로 돈 때입니다[3][4] | 목록 전체의 기준 시각입니다 |
| `InstallDate` | REG_SZ, `월/일/연 시:분:초` | 폴더 생성 날짜 등으로 짐작한 설치 날짜입니다[2] | 시간대 표시가 없습니다 |
| `MsiInstallDate` | REG_SZ, 같은 모양 | MSI 패키지에 적힌 설치 날짜입니다 | 대개 `InstallDate` 와 날짜가 같습니다. Windows 11 25H2 하이브에서는 MSI 항목 82개가 모두 같았습니다 |
| `OSVersionAtInstallTime` | REG_SZ | 설치할 때 한 번 정해집니다 | 시각은 아닙니다. 기능 업데이트 전후 어느 쪽에 설치했는지 알려 줍니다 |

`InstallDate` 는 이렇게 읽습니다.

- 날짜는 월/일/연 순서입니다. 예를 들어 `10/18/2023` 은 2023년 10월 18일입니다. 일이 12 이하이면 순서를 바꿔 읽기 쉬우므로 조심합니다.
- 10.0.16299 라이브러리에서 이 값은 날짜 단위까지만 맞습니다[1].
- Windows 11 25H2 하이브에서는 128개 가운데 115개가 `00:00:00` 이고, `AddRemoveProgram` 계열 항목 13개에만 시·분·초가 있습니다.
- 문자열에 시간대가 적혀 있지 않습니다. 어떤 도구는 이 문자열을 UTC 로 간주해 보여 줍니다. 예를 들어 AmcacheParser 는 시간대 차이를 0 으로 두고 읽습니다[5]. 보고서에는 날짜만 쓰고 다른 근거로 확인합니다.

FILETIME 을 바꾸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서, 키 시각이 바뀌는 규칙은 [키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md)에서 다룹니다.

## 함정과 한계

1. **하위 키 시각을 설치 시각으로 읽는 실수.** 1709 이후 라이브러리는 목록을 통째로 다시 씁니다. 하위 키 시각이 `LastScanTime` 근처에 몰려 있으면 설치 시각이 아닙니다.
2. **새로 설치한 프로그램이 아직 없을 수 있습니다.** ANSSI 는 설치 프로그램을 실행할 때 PCA 서비스가 바로 이 키를 고친다고 봤지만[1], Kaspersky 와 Psmths 는 마지막 점검 작업 뒤에 설치한 프로그램은 안 보일 수 있다고 씁니다[3][4]. `LastScanTime` 뒤의 설치는 이 키만으로 판단하지 않습니다.
3. **지운 프로그램은 빠집니다.** 1607 라이브러리는 프로그램을 지우면 하위 키를 지웁니다. 1709 이후는 다음에 다시 쓸 때 빠집니다. 그 사이에 수집하면 항목이 남아 있을 수 있습니다. 실제 사고 조사에서도 이미 지운 원격 제어 프로그램 항목이 여러 번 나왔습니다[3].
4. **지운 항목은 다른 곳에 남을 수 있습니다.** 하이브의 빈 셀, 트랜잭션 로그, 볼륨 섀도 복사본에 예전 항목이 남을 수 있습니다. [지워진 키·값 복구](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md)와 [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)을 봅니다.
5. **로그를 반영하지 않은 하이브.** 이미지에서 꺼낸 `Amcache.hve` 는 최근 변경이 `.LOG1`·`.LOG2` 에만 있을 수 있습니다. 세 파일을 함께 꺼내 반영합니다. 방법은 [트랜잭션 로그와 반영 안 된 변경](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md)에서 다룹니다.
6. **스토어 앱이 목록 대부분을 차지할 수 있습니다.** Windows 11 25H2 하이브의 예에서는 321개 중 193개가 `AppxPackage` 입니다. `Source` 로 걸러서 봅니다.
7. **사용자별 설치를 놓치기 쉽습니다.** `AddRemoveProgramPerUser` 항목의 `RegistryKeyPath` 는 `HKEY_USERS\{SID}\…` 로 시작합니다. 그 SID 의 NTUSER.DAT 에서 제거 키를 찾습니다.
8. **도구마다 보여 주는 값이 다릅니다.** 라이브러리 버전에 따라 값 목록이 바뀝니다. 도구가 모르는 값은 빠지거나 빈칸이 될 수 있습니다. 중요한 항목은 레지스트리 뷰어로 원래 값을 확인합니다. [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

**안티포렌식.** 프로그램을 지우면 다음 재작성 때 이 목록에서 빠집니다. 하지만 설치 폴더에 있던 실행 파일은 [실행 파일 항목](inventoryapplicationfile.md), [$MFT](../../filesystem/mft.md), [$UsnJrnl](../../filesystem/usnjrnl.md)에 흔적이 남을 수 있습니다. `Amcache.hve` 파일을 지우거나 바꾸면 그 파일의 생성·변경 시각과 $UsnJrnl 기록에 흔적이 남습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 형식 명세(libregf)로 만든 예시입니다. 실제 하이브에서 뽑은 값이 아닙니다. ProgramId 하위 키의 값 목록을 따라가 `InstallDate` 값 셀을 찾았다고 가정합니다.

값 셀 (`vk`):

```
셀 시작 기준
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00      D8 FF FF FF 76 6B 0B 00 28 00 00 00 20 3A 01 00
10      01 00 00 00 01 00 00 00 49 6E 73 74 61 6C 6C 44
20      61 74 65 00 00 00 00 00
```

1. `D8 FF FF FF` 는 셀 크기 필드입니다. 부호 있는 정수로 -40 입니다. 음수는 사용 중인 셀이라는 뜻입니다.
2. `76 6B` 는 `vk` 서명입니다.
3. `0B 00` 은 값 이름 길이 11 입니다.
4. `28 00 00 00` 은 데이터 크기 40바이트입니다. 맨 위 비트가 꺼져 있으므로 데이터는 다른 셀에 있습니다.
5. `20 3A 01 00` 은 데이터 오프셋 0x13A20 입니다. 첫 hbin 시작(파일 오프셋 0x1000)부터 센 값입니다. 파일 오프셋으로는 0x14A20 입니다.
6. `01 00 00 00` 은 데이터 형식 1, 곧 REG_SZ 입니다.
7. `01 00` 은 플래그 0x0001 입니다. 값 이름이 ASCII 로 저장됐다는 뜻입니다.
8. 오프셋 0x18 부터 11바이트가 값 이름 `InstallDate` 입니다. 나머지는 8바이트 맞춤용 채움입니다.

데이터 셀 (파일 오프셋 0x14A20):

```
셀 시작 기준
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00      D0 FF FF FF 30 00 33 00 2F 00 31 00 35 00 2F 00
10      32 00 30 00 32 00 34 00 20 00 30 00 30 00 3A 00
20      30 00 30 00 3A 00 30 00 30 00 00 00 00 00 00 00
```

9. `D0 FF FF FF` 는 셀 크기 -48 입니다.
10. 뒤의 40바이트를 UTF-16LE 로 읽으면 `03/15/2024 00:00:00` 과 끝 널 문자입니다. 인코딩은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)에서 다룹니다.
11. 월/일/연 순서이므로 2024년 3월 15일입니다. 시각 부분은 `00:00:00` 입니다. 시간대 표시는 없습니다.

`HiddenArp`·`Language` 같은 REG_DWORD 값은 데이터 크기 필드의 맨 위 비트가 켜져 있습니다(예: `04 00 00 80`). 이때는 데이터 오프셋 필드 4바이트가 곧 값입니다. `LastScanTime` 은 REG_QWORD 라서 8바이트 데이터 셀에 FILETIME 으로 들어 있습니다.

### 공개 도구로 한 번

1. 이미지에서 `Amcache.hve`·`.LOG1`·`.LOG2` 를 함께 꺼냅니다. 사본에서 작업합니다.
2. 레지스트리 뷰어(예: Registry Explorer)로 하이브를 엽니다. 트랜잭션 로그를 반영했는지 확인합니다.
3. `Root\InventoryApplication` 키에서 `LastScanTime` 을 먼저 읽습니다.
4. 하위 키를 마지막 기록 시각으로 정렬합니다. `LastScanTime` 근처에 몰려 있는지 봅니다.
5. 전용 파서(예: AmcacheParser)로 설치 프로그램 표를 뽑습니다. 몇 항목을 골라 뷰어의 원래 값과 맞춰 봅니다. 특히 `InstallDate` 를 어떤 시간대로 보여 주는지 확인합니다.
6. `Source` 가 `AppxPackage` 인 항목을 빼고 나머지를 먼저 검토합니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [설치 프로그램 (Uninstall)](../../system-account/uninstall.md) | `RegistryKeyPath` 의 제거 키가 아직 있는지, 그 키의 설치 날짜와 마지막 기록 시각 |
| [프로그램 설치·삭제 이벤트 (MsiInstaller)](../../event-logs/msiinstaller.md) | `Source` 가 `Msi` 인 항목의 설치·제거 시각 |
| [스토어 앱 설치 목록 (AppX·StateRepository)](../../system-account/appx-staterepository.md) | `AppxPackage` 항목의 설치 시각과 사용자 |
| [실행 파일 항목 (InventoryApplicationFile)](inventoryapplicationfile.md) | 같은 ProgramId 로 묶인 실행 파일의 경로와 SHA-1 |
| [바로가기 항목 (InventoryApplicationShortcut)](inventoryapplicationshortcut.md) | 설치하면서 생긴 시작 메뉴 바로가기 |
| [마스터 파일 테이블 ($MFT)](../../filesystem/mft.md) | `RootDirPath` 폴더의 생성 시각. `InstallDate` 의 근거를 확인합니다 |
| [프리페치](../prefetch/index.md), [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md) | 설치한 프로그램을 실제로 실행했는지 |
| [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 예전 `Amcache.hve` 의 목록. 그 사이에 빠진 프로그램 |

## 실습

NIST CFReDS 같은 공개 데이터 세트에서 Windows 10 1709 이후 이미지를 하나 고릅니다. 가상 머신에 직접 프로그램을 설치하고 점검 작업 전후의 하이브를 비교해도 됩니다.

1. `LastScanTime` 을 UTC 와 현지 시각으로 바꿔 봅니다. 시간대는 [시간대 설정](../../system-account/time-zone.md)에서 찾습니다.
2. 하위 키의 마지막 기록 시각은 어떻게 퍼져 있습니까? 이 하이브는 어느 라이브러리 동작을 따릅니까?
3. `Source` 별로 개수를 세어 봅니다. 스토어 앱을 뺀 목록을 만듭니다.
4. 항목 하나를 골라 `RegistryKeyPath` 의 제거 키를 SOFTWARE 또는 NTUSER.DAT 에서 찾습니다. 제거 키의 설치 날짜, `InstallDate`, `RootDirPath` 폴더의 생성 시각을 비교합니다.
5. 그 항목의 ProgramId 를 가진 실행 파일을 InventoryApplicationFile 에서 찾습니다. ProgramId 짝이 없는 실행 파일은 무엇을 뜻할 수 있습니까?
6. 섀도 복사본에 예전 `Amcache.hve` 가 있으면 두 목록을 비교합니다. 그 사이에 빠진 프로그램은 무엇입니까?

## 참고 문헌

- Blanche Lagny (ANSSI), "Analysis of the AmCache" v2 (2019) — https://cyber.gouv.fr/documents/632/anssi-coriin_2019-analysis_amcache-v2.pdf
- Microsoft Learn, "Required diagnostic events and fields for Windows 10, versions 22H2 and 21H2" (`Microsoft.Windows.Inventory.Core.InventoryApplicationAdd`) — https://learn.microsoft.com/en-us/windows/privacy/required-windows-diagnostic-data-events-and-fields-2004
- Cristian Souza (Kaspersky), "AmCache artifact: forensic value and a tool for data extraction", Securelist (2025) — https://securelist.com/amcache-forensic-artifact/117622/
- Psmths, "AmCache.hve", windows-forensic-artifacts — https://github.com/Psmths/windows-forensic-artifacts/blob/main/execution/amcache.md
- Eric Zimmerman, AmcacheParser 소스 `Amcache/AmcacheNew.cs` — https://github.com/EricZimmerman/AmcacheParser/blob/master/Amcache/AmcacheNew.cs
- Joachim Metz, "Windows NT Registry File (REGF) format", libregf — https://github.com/libyal/libregf/blob/main/documentation/Windows%20NT%20Registry%20File%20(REGF)%20format.asciidoc
