---
title: "드라이버 항목"
parent: "AmCache"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 890
---

# 드라이버 항목 (InventoryDriverBinary)

## 한 줄 요약

`Amcache.hve` 의 `Root\InventoryDriverBinary` 키에는 드라이버 파일마다 하위 키가 하나씩 있습니다. 하위 키에는 드라이버 파일의 SHA-1, 서명 여부, 윈도 기본 포함 여부, 연결된 서비스·INF 이름, 빌드 시각, 파일 수정 시각이 적혀 있습니다. 이 목록은 실행 기록이 아니라 윈도가 드라이버를 조사해 적은 목록 (Inventory) 이고, 조사할 때 그 경로에 그 드라이버 파일이 있었다는 것을 보여 줍니다.

## 무엇을 기록하나 · 왜 생기나

AmCache 는 윈도의 프로그램 호환성 기능이 쓰는 레지스트리 하이브입니다. 전체 모습은 [AmCache](index.md) 허브에서 다룹니다.

드라이버 항목은 호환성 조사 작업 (Microsoft Compatibility Appraiser) 이라는 예약 작업이 씁니다. Windows 10 1607·1709 의 기본 라이브러리에서는 이 작업만 이 키를 갱신합니다(ANSSI). 그래서 항목은 드라이버가 설치되거나 로드되는 순간이 아니라 작업이 다음에 돌 때 생깁니다.

같은 이름의 필드가 진단 데이터 이벤트 `Microsoft.Windows.Inventory.Core.InventoryDriverBinaryAdd` 에도 있습니다. 이 이벤트의 필드 목록에는 `DriverId` 와 `DriverLastWriteTime` 이 없어서, 이 두 값의 뜻은 연구 자료와 공개 파서 소스에 기댑니다.

드라이버는 커널 권한으로 돕니다. 그래서 루트킷과 취약 드라이버 악용 (BYOVD, Bring Your Own Vulnerable Driver) 을 조사할 때 이 키를 봅니다. 이 키로 보안 프로그램을 끄는 악성코드(AV Killer)를 찾은 사례도 있습니다(Kaspersky Securelist).

## 위치와 버전별 차이

- 파일: `C:\Windows\AppCompat\Programs\Amcache.hve`
- 키: `Root\InventoryDriverBinary`

하이브 파일의 전체 구조와 수집 방법은 [구조와 버전별 차이](structure-versions.md)에서 다룹니다.

AmCache 형식은 OS 버전이 아니라 이 파일을 채우는 라이브러리 버전을 따릅니다(ANSSI). 아래 표는 라이브러리 버전별로 드라이버가 어디에 적히는지 정리한 것입니다. "처음 실린 Windows" 는 그 라이브러리가 기본으로 들어 있던 Windows 입니다.

| 라이브러리 버전 | 처음 실린 Windows | 드라이버가 적히는 곳 |
|---|---|---|
| 6.2.9200 · 6.3.9600 | 8.0 · 8.1 | `Amcache.hve` 의 `Root\Generic\0` 아래에 `0000`+SHA-1 이름의 키만 있습니다. 파일 이름·버전은 `%WinDir%\AppCompat\Programs\AEINV_AMI_WER_*.xml` 의 드라이버 목록에 있습니다 |
| 10.0.10240 | 10 1507 | `Generic` 키가 비어 있습니다. 드라이버 목록은 `AEINV_AMI_WER` XML 에만 있습니다 |
| 10.0.10586 | 10 1511 | 드라이버 설치 정보가 없습니다(ANSSI) |
| 10.0.14913 | 10 1607 | `InventoryDriverBinary` 와 `InventoryDriverPackage` 가 생깁니다. 하위 키 이름은 `0000`+SHA-1 입니다 |
| 10.0.16299 | 10 1709 | 하위 키 이름이 드라이버 전체 경로로 바뀝니다. SHA-1 은 `DriverId` 값에 남습니다 |
| 10.0.17134 | 10 1803 | `Generic` 키가 없어집니다. `InventoryApplicationDriver` 가 생깁니다 |
| 10.0.17763 | 10 1809 | 1803 과 동작이 같습니다(ANSSI) |

- ANSSI 연구는 1809 까지만 다룹니다.
- Windows 11 22H2·23H2 의 진단 데이터에도 캐시에 든 `InventoryDriverBinary` 개수를 세는 필드가 있습니다. 그래서 Windows 11 에서도 이 목록이 쓰인다고 볼 수 있습니다.
- 값 구성은 빌드마다 늘거나 줄 수 있습니다. 드라이버 항목에 `COMPID`·`HWID` 같은 값이 들어 있기도 합니다. 공개 파서 AmcacheParser 는 이 값을 건너뛰고, 모르는 값 이름을 만나면 경고를 남깁니다.

## 구조

### 하위 키 이름

| 형식 | 하위 키 이름 | 예 (ANSSI) |
|---|---|---|
| 1607 | `0000` + 드라이버 파일의 SHA-1 | `0000895407cb018368e62fc360b972a8b0da7e729662` |
| 1709 이후 | 드라이버 전체 경로. 소문자이고 구분자는 `/` 입니다 | `c:/windows/system32/drivers/1394ohci.sys` |

- 레지스트리 키 이름에는 역슬래시(`\`)를 쓸 수 없습니다(Microsoft 문서). 그래서 경로 구분자를 `/` 로 바꿔 적은 것으로 보입니다.
- 1709 이후에는 경로가 키 이름이라서 한 경로에 항목이 하나뿐입니다. 같은 경로의 파일이 다른 파일로 바뀌면 이 키에는 새 SHA-1 만 남을 것으로 봅니다. 옛 값은 [트랜잭션 로그](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md), [지워진 키·값](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md), [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)에서 찾습니다.
- 1607 형식에서는 키 이름이 해시입니다. 경로로 키를 찾는 방식이 통하지 않습니다.

키와 값이 하이브 파일 안에 어떻게 저장되는지는 [하이브 내부 구조](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)에서 다룹니다.

### 값

"공식 설명" 칸은 Microsoft 진단 데이터 문서의 필드 설명을 옮긴 것입니다.

| 값 | 공식 설명 | 읽을 때 주의 |
|---|---|---|
| `DriverName` | 드라이버 파일 이름 | |
| `DriverId` | (공식 필드 목록에 없음) 드라이버의 SHA-1 앞에 `0000` 을 붙인 값입니다(ANSSI) | 앞 네 글자를 떼고 해시를 조회합니다. 계산 범위는 [AmCache 해석 함정](sha1.md)을 봅니다 |
| `DriverVersion` | 드라이버 파일의 버전 | |
| `DriverCompany` | 드라이버를 만든 회사 이름 | 파일 버전 정보에 적힌 글자입니다. 서명한 곳과 다를 수 있습니다 |
| `Product` · `ProductVersion` | 드라이버 파일에 적힌 제품 이름과 제품 버전 | |
| `DriverSigned` | 서명된 드라이버인가 | 0·1 만 있습니다. 서명자와 인증서가 유효한지는 알 수 없습니다 |
| `DriverInBox` | 운영체제에 기본으로 들어 있는 드라이버인가 | |
| `DriverIsKernelMode` | 커널 모드 드라이버인가 | 이 값이 따로 있으므로 커널 모드가 아닌 드라이버도 목록에 오를 수 있다고 읽힙니다 |
| `DriverType` | 드라이버 속성을 나타내는 비트 값 | 아래 표를 봅니다 |
| `DriverTimeStamp` | 드라이버 파일 시각의 하위 32비트 | Unix 형식의 컴파일 날짜입니다(ANSSI). 아래 시각 해석을 봅니다 |
| `DriverLastWriteTime` | (공식 필드 목록에 없음) 드라이버 파일의 마지막 수정 시각 | 문자열입니다 |
| `DriverCheckSum` | 드라이버 파일의 체크섬 | 이름으로 보아 PE 선택 헤더의 `CheckSum` 으로 보입니다. 아래 헥스 절에서 맞춰 봅니다 |
| `ImageSize` | 드라이버 파일의 크기 | 아래 함정과 한계 4번을 봅니다 |
| `Inf` | INF 파일 이름 | |
| `Service` | 장치용으로 설치된 서비스 이름 | [서비스·드라이버](../../persistence/services-drivers.md) 키와 잇습니다 |
| `DriverPackageStrongName` | 드라이버 패키지의 강한 이름 (Strong Name) | |
| `WdfVersion` | 드라이버 프레임워크 (Windows Driver Framework) 버전 | |

### DriverType 비트

비트 이름은 공개돼 있지만, 각 비트를 어떤 기준으로 켜는지는 공개돼 있지 않습니다.

| 비트 | 이름 | 뜻 |
|---|---|---|
| 0x0001 | `DRIVER_MAP_DRIVER_TYPE_PRINTER` | 프린터 드라이버 |
| 0x0002 | `DRIVER_MAP_DRIVER_TYPE_KERNEL` | 커널 모드 |
| 0x0004 | `DRIVER_MAP_DRIVER_TYPE_USER` | 사용자 모드 |
| 0x0008 | `DRIVER_MAP_DRIVER_IS_SIGNED` | 서명됨 |
| 0x0010 | `DRIVER_MAP_DRIVER_IS_INBOX` | 윈도 기본 포함 |
| 0x0020 | `DRIVER_MAP_DRIVER_IS_SELF_SIGNED` | 자체 서명 |
| 0x0040 | `DRIVER_MAP_DRIVER_IS_WINQUAL` | 문서에 이름만 있습니다 |
| 0x0080 | `DRIVER_MAP_DRIVER_IS_CI_SIGNED` | 코드 무결성 (Code Integrity) 서명 |
| 0x0100 | `DRIVER_MAP_DRIVER_HAS_BOOT_SERVICE` | 부팅 때 시작하는 서비스가 있음 |
| 0x10000 | `DRIVER_MAP_DRIVER_TYPE_I386` | x86 |
| 0x20000 | `DRIVER_MAP_DRIVER_TYPE_IA64` | IA-64 |
| 0x40000 | `DRIVER_MAP_DRIVER_TYPE_AMD64` | x64 |
| 0x100000 | `DRIVER_MAP_DRIVER_TYPE_ARM` | ARM |
| 0x200000 | `DRIVER_MAP_DRIVER_TYPE_THUMB` | ARM Thumb |
| 0x400000 | `DRIVER_MAP_DRIVER_TYPE_ARMNT` | ARM NT |
| 0x800000 | `DRIVER_MAP_DRIVER_IS_TIME_STAMPED` | 문서에 이름만 있습니다 |

6.2 라이브러리의 `AEINV_AMI_WER` XML 드라이버 목록에 적힌 `1394ohci.sys` 의 `Type` 값 `0x0004001A` 를 예로 듭니다(ANSSI). 같은 비트 정의를 씁니다. 이 값은 0x40000 + 0x10 + 0x8 + 0x2 입니다. x64, 기본 포함, 서명됨, 커널 모드라는 뜻입니다.

`DriverSigned`·`DriverInBox`·`DriverIsKernelMode` 와 이 비트가 서로 맞는지도 봅니다. 어긋나면 어느 쪽이 맞는지 문서로는 가릴 수 없습니다. 드라이버 파일이 남아 있으면 파일을 직접 확인합니다.

### 함께 보는 두 키

- **`InventoryDriverPackage`** 는 INF 로 묶인 드라이버 패키지를 적습니다. 필드에는 `Class`·`ClassGuid`·`Date`·`Directory`·`DriverInBox`·`Inf`·`Provider`·`SubmissionId`·`Version` 이 있습니다. `Date` 의 공식 설명은 "드라이버 패키지 날짜" 뿐입니다. 기본 INF(`acpi.inf`)의 날짜가 06/21/2006 인 예가 있습니다(ANSSI). 그래서 `Date` 를 설치한 날짜로 읽지 않습니다.
- **`InventoryApplicationDriver`** 는 프로그램이 함께 설치한 드라이버를 적습니다(1803 라이브러리부터). 값은 `DriverServiceName` 과 `ProgramIds` 두 개입니다. `ProgramIds` 는 [설치 프로그램 항목](inventoryapplication.md)의 키 이름을 가리킵니다. 예를 들어 Wireshark 를 설치하면 `npcap` 항목이 생깁니다(ANSSI).

[장치 항목 (InventoryDevicePnp)](inventorydevicepnp.md)에도 `DriverName`·`Inf`·`Service` 값이 있습니다. 이 값으로 장치와 드라이버를 잇습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 조사 작업이 돌 때 이 경로에 이 SHA-1 의 드라이버 파일이 있었습니다 | 드라이버가 로드됐거나 실행됐는지 |
| 그 파일에 적힌 버전 정보, 서명 여부, 빌드 시각 값 | 언제 설치되거나 복사됐는지 |
| 어느 서비스·INF 와 연결됐는지 (`Service`·`Inf` 가 채워진 경우) | 누가 설치했는지 |
| | 서명이 유효하고 믿을 만한지 |
| | 분석하는 지금도 파일이 있는지 |

로드 여부를 두고는 자료마다 표현이 다릅니다.

- ANSSI 는 "설치된 드라이버" 목록이라고 적습니다.
- Microsoft 문서는 "시스템에서 실행 중인 드라이버 바이너리" 의 정보를 보낸다고 적습니다.
- Securelist 는 "시스템이 로드한 커널 모드 드라이버" 를 적는다고 설명합니다.

설치만 되고 한 번도 로드되지 않은 드라이버가 목록에 오르는지 밝힌 공개 자료는 없습니다. 그래서 이 항목 하나로 "로드했다" 고 쓰지 않습니다. 로드는 아래 교차 검증 절의 기록으로 따로 확인합니다.

### 보고서 문장

아래 경로와 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "`Amcache.hve` 의 `InventoryDriverBinary` 에 `c:/windows/system32/drivers/sample.sys` 항목이 있습니다. 이 항목의 SHA-1 은 (값) 이고 `DriverSigned` 는 1, `DriverInBox` 는 0 입니다. 항목 키의 마지막 기록 시각은 2025-03-14 01:23:45 UTC 입니다."
- 쓰면 안 되는 문장: "공격자가 2025-03-14 01:23 에 sample.sys 드라이버를 설치해 로드했습니다."

## 시각 해석

이 항목에서 보이는 시각은 네 가지이고 뜻이 모두 다릅니다.

| 시각 | 자리 | 무엇을 가리키나 | 시간대 |
|---|---|---|---|
| 키 마지막 기록 시각 (Last Write Time) | 하위 키 | 조사 작업이 이 항목을 쓴 때 | UTC FILETIME |
| `DriverTimeStamp` | 값 (정수) | 드라이버 파일 PE 헤더의 빌드 시각 | 1970-01-01 UTC 부터 센 초 |
| `DriverLastWriteTime` | 값 (문자열) | 드라이버 파일의 마지막 수정 시각 | 공식 문서가 없습니다 |
| `InventoryDriverPackage` 의 `Date` | 값 | 드라이버 패키지에 적힌 날짜 | 날짜만 있습니다 |

### 키 마지막 기록 시각

이 시각은 조사 작업이 이 항목을 쓴 때라서 드라이버를 설치한 때보다 늦고, 둘 사이는 작업이 도는 간격만큼 벌어질 수 있습니다.

1709 이후 조사 작업은 돌 때마다 `InventoryApplication` 의 항목을 모두 다시 씁니다(ANSSI). 드라이버 항목도 그런지 밝힌 공개 자료는 없습니다. 여러 드라이버 키의 시각이 몇 초 안에 몰려 있으면 한꺼번에 다시 쓴 것으로 보고, 이런 시각은 드라이버 하나하나의 시각으로 쓰지 않습니다. 키 시각의 성질은 [키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md)에서 다룹니다.

### DriverTimeStamp

이 값은 드라이버 파일 시각의 하위 32비트입니다. PE 형식에서 COFF 파일 헤더의 `TimeDateStamp` 는 1970년 1월 1일 0시부터 센 초의 하위 32비트입니다. 두 설명이 같으므로 이 값은 PE 헤더의 `TimeDateStamp` 로 봅니다. Unix 형식의 컴파일 날짜라는 설명(ANSSI)과도 맞습니다.

이 값을 날짜로 믿기 전에 두 가지를 확인합니다.

- **재현 가능한 빌드 (Reproducible Build)** 입니다. Windows 10 부터 Microsoft 는 모듈의 이 칸에 실제 시각 대신 결과 파일의 해시를 넣습니다(Raymond Chen). 이런 파일은 날짜로 바꾸면 엉뚱한 날짜가 나옵니다. Windows 10 이후 `DriverInBox` 가 1 인 드라이버는 이 값을 날짜로 읽지 않습니다. 같은 방식으로 빌드한 다른 회사 드라이버도 같을 수 있습니다.
- **조작**입니다. 이 값은 PE 헤더의 4바이트입니다. 빌드한 PC 의 시계를 따르고, 헤더를 고치면 바뀝니다.

### DriverLastWriteTime

이 값은 날짜와 시각을 적은 문자열입니다. 공개 파서 AmcacheParser 는 이 문자열을 날짜로 읽고 UTC 로 다룹니다. 이 문자열의 시간대를 밝힌 공식 문서는 없습니다. 그래서 검체마다 [$MFT](../../filesystem/mft.md)의 파일 수정 시각과 한 번 맞춰 보고, 그 결과를 보고서에 적습니다.

윈도 API 가 돌려주는 파일 수정 시각은 보통 $STANDARD_INFORMATION 의 값입니다. 그래서 이 값도 시각 조작 도구의 영향을 받을 수 있다고 봅니다([두 벌의 시각](../../../01-foundations/disk-volume/ntfs/standard-information-file-name.md)).

수정 시각이 빌드 시각보다 늦은 것은 정상입니다. 드라이버 파일은 빌드한 뒤에 복사되고 설치되기 때문입니다. 이것만으로 파일을 고쳤다고 보지 않습니다.

### 현지 시각으로 바꾸기

UTC 값은 그 PC 의 [시간대 설정](../../system-account/time-zone.md)으로 바꿉니다. 계산은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)과 [시간대·시계 오차 보정](../../../03-techniques/analysis/timeline/time-normalization.md)을 봅니다.

## 함정과 한계

1. **실행 증거로 씁니다.** 이 목록은 조사 결과입니다. AmCache 전체에 걸친 이 함정은 [AmCache 해석 함정](sha1.md)에서 다룹니다.
2. **키 시각을 설치 시각으로 씁니다.** 키 시각은 조사 작업이 쓴 때입니다. 설치 시각은 [장치 설치 로그](../../external-devices/usb-storage-artifacts/setupapi-dev-log.md)나 [서비스 설치 이벤트](../../event-logs/7045-4697.md)에서 찾습니다.
3. **재현 가능한 빌드의 시각을 날짜로 읽습니다.** 위 시각 해석의 DriverTimeStamp 절을 봅니다.
4. **`ImageSize` 를 파일 크기와 바로 비교합니다.** Microsoft 문서는 이 값을 파일 크기라고 적습니다. 그런데 ANSSI 가 `AEINV_AMI_WER` XML 에서 보인 예시 값 `0x0003D000` 은 4KB(0x1000)의 배수입니다. 이 모양은 PE 헤더의 `SizeOfImage`(메모리에 올렸을 때의 크기)와 닮았습니다. 파일 크기와 다르다고 곧바로 변조로 보지 않습니다.
5. **`DriverCompany` 를 서명한 곳으로 읽습니다.** 회사 이름은 파일에 누구나 적을 수 있는 글자입니다. 서명자는 파일의 서명에서 확인합니다([실행 파일 메타데이터](../../embedded-metadata/pe-header-version-info-digital-signature.md)).
6. **조사 작업 사이에 들어왔다 나간 드라이버를 찾습니다.** 작업이 돌기 전에 드라이버를 올리고 지웠다면 이 목록에 남지 않을 수 있습니다. 목록에 없다고 드라이버가 없었다고 쓰지 않습니다.
7. **도구마다 `DriverType` 을 다르게 보여 줍니다.** 10진(예: 262170)으로 보여 주는 도구도 있습니다. 비트를 읽을 때는 16진(0x4001A)으로 바꿉니다.

### 지우기와 조작

- **드라이버 파일을 지웁니다.** 드라이버 목록 항목이 더는 없다고 알리는 진단 이벤트(`InventoryDriverBinaryRemove`)도 있습니다. 그래서 다음 조사 때 항목이 빠질 수 있습니다. 빠진 뒤에는 [지워진 키·값 복구](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md), [트랜잭션 로그](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md), [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)을 봅니다.
- **`Amcache.hve` 를 지우거나 고칩니다.** 하이브 파일은 오프라인에서 고칠 수 있습니다. 파일을 지우거나 바꾼 흔적은 [$MFT](../../filesystem/mft.md)와 [$UsnJrnl](../../filesystem/usnjrnl.md)에 남을 수 있습니다.
- **기본 드라이버 이름을 흉내 냅니다.** 이름만 보지 않고 경로, SHA-1, `DriverInBox`, `DriverSigned` 를 함께 봅니다.
- **PE 헤더의 시각을 고칩니다.** `DriverTimeStamp` 도 고친 값을 따릅니다. 파일 시스템 시각과 다른 기록의 시각을 함께 봅니다.

## 직접 분석해 보기

### 헥스로 한 번 — 드라이버 파일의 PE 헤더와 맞춰 보기

하이브 안의 키와 값을 헥스로 따라가는 법은 [하이브 내부 구조](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)에서 다룹니다. 여기서는 드라이버 파일이 남아 있을 때 `DriverTimeStamp`·`ImageSize`·`DriverCheckSum` 에 대응하는 칸을 파일에서 직접 찾습니다.

PE 형식에서 각 칸의 위치는 다음과 같습니다.

| 칸 | 위치 | 크기 |
|---|---|---|
| PE 서명 위치 (`e_lfanew`) | 파일 0x3C | 4바이트 |
| PE 서명 `PE\0\0` | `e_lfanew` | 4바이트 |
| `Machine` | `e_lfanew` + 4 | 2바이트 |
| `TimeDateStamp` | `e_lfanew` + 8 | 4바이트 |
| 선택 헤더 시작 | `e_lfanew` + 24 | |
| `SizeOfImage` | 선택 헤더 + 56 | 4바이트 |
| `CheckSum` | 선택 헤더 + 64 | 4바이트 |

아래는 형식 명세를 보고 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다. `e_lfanew` 는 설명을 위해 0xE8 로 정했습니다. 세 값은 `AEINV_AMI_WER` XML 에 적힌 `1394ohci.sys` 예시 값입니다(ANSSI). `..` 은 이 풀이와 관계없는 바이트입니다.

```
오프셋   00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x0000  4D 5A .. .. .. .. .. .. .. .. .. .. .. .. .. ..
0x0030  .. .. .. .. .. .. .. .. .. .. .. .. E8 00 00 00
0x00E0  .. .. .. .. .. .. .. .. 50 45 00 00 64 86 .. ..
0x00F0  E6 AA 10 50 .. .. .. .. .. .. .. .. .. .. .. ..
0x0130  .. .. .. .. .. .. .. .. 00 D0 03 00 .. .. .. ..
0x0140  21 70 04 00 .. .. .. .. .. .. .. .. .. .. .. ..
```

1. `4D 5A` 는 `MZ` 입니다. PE 파일의 시작입니다.
2. 0x3C 의 `E8 00 00 00` 은 0xE8 입니다. PE 서명이 0xE8 에 있습니다.
3. 0xE8 의 `50 45 00 00` 은 `PE\0\0` 서명입니다.
4. 0xEC 의 `64 86` 은 0x8664 입니다. x64 파일입니다. `DriverType` 의 0x40000 비트와 맞습니다.
5. 0xF0(= 0xE8 + 8)의 `E6 AA 10 50` 을 리틀 엔디언으로 읽으면 0x5010AAE6 입니다. 10진으로 1,343,269,606 입니다.
6. 이 수를 1970-01-01 00:00:00 UTC 에 초로 더하면 2012-07-26 02:26:46 UTC 입니다. 이 값이 `DriverTimeStamp` 와 같은지 봅니다.
7. 선택 헤더는 0x100(= 0xE8 + 24)에서 시작합니다. 0x138 의 `00 D0 03 00` 은 `SizeOfImage` 0x0003D000(249,856)입니다.
8. 0x140 의 `21 70 04 00` 은 `CheckSum` 0x00047021(290,849)입니다. 이 값이 `DriverCheckSum` 과 같은지 봅니다.
9. 이 예시에서는 `SizeOfImage` 와 `ImageSize` 예시 값이 같게 만들었습니다. 실제 검체에서는 `ImageSize` 가 `SizeOfImage` 와 같은지, 파일 크기와 같은지 직접 확인합니다.

> 그림 자리: 드라이버 파일 헤더에서 0x3C(e_lfanew), TimeDateStamp, SizeOfImage, CheckSum 자리를 색으로 나누고, 각각 InventoryDriverBinary 의 DriverTimeStamp·ImageSize·DriverCheckSum 과 선으로 잇는 그림

### 공개 도구로 한 번

AmcacheParser, Registry Explorer 같은 공개 도구로 이 키를 볼 수 있습니다. 레지스트리 뷰어로 키를 직접 열면 도구가 건너뛴 값 이름도 보입니다. 도구를 쓸 때는 다음을 확인합니다.

- AmcacheParser 소스는 `DriverId` 의 앞 네 글자(`0000`)를 떼고 보여 줍니다. 다른 도구 결과와 비교할 때 이 차이를 맞춥니다.
- 같은 소스는 `DriverLastWriteTime` 문자열을 UTC 로 다룹니다. `DriverTimeStamp` 는 1970년부터 센 초로 바꾸고, 0 이면 비워 둡니다.
- 도구가 그 라이브러리 형식을 아는지 확인합니다. 1607 형식처럼 키 이름이 해시인 파일도 읽는지 봅니다.
- 항목 한두 개는 레지스트리 뷰어로 연 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [서비스·드라이버 (Services·Drivers)](../../persistence/services-drivers.md) | `Service` 값의 서비스가 SYSTEM 하이브에 있는지. 이미지 경로와 시작 방식 |
| [서비스 설치 (7045·4697)](../../event-logs/7045-4697.md) | 드라이버 서비스가 설치된 시각 |
| [Sysmon 로그](../../event-logs/sysmon/index.md) | Sysmon 설정에서 드라이버 로드(이벤트 6) 기록을 켰다면 로드 시각과 서명 정보 |
| [장치 설치 로그 (setupapi.dev.log)](../../external-devices/usb-storage-artifacts/setupapi-dev-log.md) | `Inf` 값의 INF 가 설치된 시각 |
| [장치 항목 (InventoryDevicePnp)](inventorydevicepnp.md) | 같은 `Inf`·`Service` 를 쓰는 장치 |
| [설치 프로그램 항목 (InventoryApplication)](inventoryapplication.md) | `InventoryApplicationDriver` 의 `ProgramIds` 가 가리키는 프로그램 |
| [실행 파일 항목 (InventoryApplicationFile)](inventoryapplicationfile.md) | 프로그램 설치와 함께 생긴 SYS 파일도 이 키에 오릅니다(1709 라이브러리, ANSSI) |
| [$MFT](../../filesystem/mft.md) · [$UsnJrnl](../../filesystem/usnjrnl.md) | `.sys` 파일이 생기고 지워진 시각 |
| [실행 파일 메타데이터](../../embedded-metadata/pe-header-version-info-digital-signature.md) | 파일이 남아 있으면 서명자와 버전 정보 |
| [해시셋 대조](../../../03-techniques/analysis/hash-set-fuzzy-hash.md) | `DriverId` 의 SHA-1 이 LOLDrivers 같은 공개 취약 드라이버 목록에 있는지 |
| [코드 주입·숨긴 프로세스 탐지](../../../03-techniques/analysis/memory-forensics/injection-rootkit.md) | 메모리 덤프가 있으면 실제로 올라와 있던 드라이버 |

드라이버를 이용한 지속성과 보안 프로그램 무력화는 [악성코드 지속성 찾기](../../../04-scenarios/incident/persistence.md)와 [보안 프로그램을 끄거나 지웠나](../../../04-scenarios/activity/anti-forensics/defense-evasion.md)에서 흐름으로 다룹니다.

## 실습

**공개 검체** — NIST CFReDS 등에서 Windows 10 이상 PC 이미지를 하나 고릅니다.

1. `InventoryDriverBinary` 의 하위 키 이름은 해시입니까, 경로입니까? 위 표에서 어느 라이브러리 형식인지 짐작해 보십시오.
2. `DriverInBox` 가 0 인 항목만 골라 목록을 만드십시오. 각 항목의 `Service` 이름이 SYSTEM 하이브의 서비스 목록에 있습니까?
3. 그중 하나의 `DriverTimeStamp` 를 날짜로 바꿔 보십시오. 드라이버 파일이 이미지에 남아 있으면 PE 헤더에서 직접 읽어 맞춰 보십시오.
4. 드라이버 키들의 마지막 기록 시각을 모아 보십시오. 몇 초 안에 몰려 있습니까?
5. `ImageSize` 를 파일 크기, `SizeOfImage` 와 비교해 보십시오. 어느 쪽과 같습니까?

**직접 만든 Windows 10·11 가상 머신**에서도 해 봅니다.

1. 드라이버를 함께 설치하는 프로그램을 설치합니다. 설치한 시각을 적어 둡니다.
2. 곧바로 `Amcache.hve` 사본을 떠서 항목이 생겼는지 봅니다.
3. 작업 스케줄러의 `Application Experience` 폴더에서 호환성 조사 작업을 찾아 한 번 실행합니다. 작업 이름은 빌드마다 다를 수 있습니다. 실행 뒤 사본을 다시 떠서 비교합니다.
4. `DriverLastWriteTime` 과 $MFT 의 파일 수정 시각을 비교해 이 문자열이 UTC 인지 확인합니다.
5. 설치만 하고 로드하지 않은 드라이버도 목록에 오르는지 확인합니다. 드라이버 파일을 지운 뒤 작업을 다시 돌리면 항목이 빠지는지도 확인합니다.

## 참고 문헌

- Blanche Lagny, "Analysis of the AmCache v2", ANSSI (2019) — https://cyber.gouv.fr/documents/632/anssi-coriin_2019-analysis_amcache-v2.pdf
- Microsoft Learn, "Required diagnostic events and fields for Windows 10, versions 22H2 and 21H2" (InventoryDriverBinaryAdd·InventoryDriverPackageAdd) — https://learn.microsoft.com/en-us/windows/privacy/required-windows-diagnostic-data-events-and-fields-2004 · Windows 11 판(AmiTelCacheChecksum) — https://learn.microsoft.com/en-us/windows/privacy/required-diagnostic-events-fields-windows-11-22h2
- Microsoft Learn, "PE Format" — https://learn.microsoft.com/en-us/windows/win32/debug/pe-format
- Raymond Chen, "Why are the module timestamps in Windows 10 so nonsensical?", The Old New Thing (2018) — https://devblogs.microsoft.com/oldnewthing/20180103-00/?p=97705
- Kaspersky Securelist, "AmCache artifact: forensic value and a tool for data extraction" — https://securelist.com/amcache-forensic-artifact/117622/
- Eric Zimmerman, AmcacheParser 소스 `AmcacheNew.cs` — https://github.com/EricZimmerman/AmcacheParser/blob/master/Amcache/AmcacheNew.cs
