---
title: "실행 파일 항목"
parent: "AmCache"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 870
---

# 실행 파일 항목 (InventoryApplicationFile)

## 한 줄 요약

실행 파일 항목 (InventoryApplicationFile) 은 `Amcache.hve` 하이브 안의 `Root\InventoryApplicationFile` 키입니다. 윈도의 호환성 점검 기능이 찾아낸 실행 파일마다 하위 키가 하나씩 생기고, 하위 키에는 파일 경로, 내용의 SHA-1, 크기, 버전 정보, 링크 시각이 남습니다.

## 무엇을 기록하나 · 왜 생기나

윈도는 설치된 프로그램이 새 버전과 잘 맞는지 점검하려고 실행 파일 목록을 모아 `Amcache.hve` 에 적습니다.

목록은 주로 호환성 점검 예약 작업 (Microsoft Compatibility Appraiser) 이 채우며, 이 작업은 `compattelrunner.exe` 를 실행합니다. 호환성 조치 (shim) 가 필요한 프로그램을 실행하면 DiagTrack 서비스가 그 파일을 바로 적고, 설치 프로그램을 실행하면 [프로그램 호환성 도우미 (PCA)](../pca.md) 서비스가 목록을 고칩니다.

ANSSI 는 10.0.16299 버전 라이브러리에서 이 키에 들어오는 파일을 세 종류로 나눴습니다.

| 종류 | 누가 적나 | 실행했다는 뜻인가 |
|---|---|---|
| 호환성 조치가 필요한 창(GUI) 프로그램 EXE 를 실행함 | 실행할 때 DiagTrack | 예 |
| 프로그램을 설치하면서 생긴 EXE·SYS | 설치 처리, 점검 작업 | 아니오 |
| 점검 작업이 훑는 폴더의 EXE (`Program Files`, `Program Files (x86)`, 바탕 화면) | 점검 작업 | 아니오 |

ANSSI 실험에서 설치 폴더의 DLL 은 이 키에 들어오지 않았습니다(10.0.17134 기준). 항목 하나만 보고는 세 종류 가운데 어디에 속하는지 가릴 수 없으며, 실행 증거로 쓸 수 있는 조건은 [AmCache 해석 함정](sha1.md) 에서 다룹니다.

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 하이브 파일 | `%SystemRoot%\AppCompat\Programs\Amcache.hve`. 같은 폴더에 `.LOG1`·`.LOG2` 가 있습니다. |
| 키 경로 | `Root\InventoryApplicationFile\<하위 키>` |
| 하위 키 하나의 단위 | 파일 경로 하나 |
| 사용자 정보 | 없습니다 |
| 시각 | 하위 키의 마지막 기록 시각 (FILETIME, UTC), `LinkDate` 값 (문자열) |

AmCache 형식은 Windows 버전이 아니라 목록을 채우는 라이브러리 버전을 따릅니다. 그래서 업데이트를 받은 Windows 7 에도 Windows 10 과 같은 형식이 생길 수 있습니다. 전체 흐름은 [구조와 버전별 차이](structure-versions.md) 에서 다룹니다. 이 키와 관련된 변화만 추리면 다음과 같습니다(ANSSI).

| 라이브러리 버전 (처음 실린 Windows 10) | 하위 키 이름 | 달라진 점 |
|---|---|---|
| 10.0.14913 (1607) | `0000` + 전체 경로(소문자, UTF-16LE)의 SHA-1 | 이 키가 처음 생깁니다. `Size` 는 16진 문자열입니다. |
| 10.0.16299 (1709) | `파일 이름\|해시` | `Size` 가 REG_QWORD 로 바뀝니다. `Name`·`Publisher`·`Version`·`BinFileVersion`·`ProductName`·`ProductVersion`·`LinkDate`·`BinProductVersion`·`Language`·`IsPeFile`·`IsOsComponent` 가 더해집니다. |
| 10.0.17134 (1803) · 10.0.17763 (1809) | 위와 같음 | 옛 `File`·`Programs` 키가 없어집니다. 실행 파일 목록은 이 키만 맡습니다. |

`파일 이름|해시` 의 해시 계산 방식은 공개되지 않았습니다. ANSSI 는 서로 다른 두 PC 에서 같은 경로에 있는 다른 버전 파일이 같은 해시를 냈기 때문에 이 해시가 파일 이름과 경로로 정해진다고 봤습니다. 해시 길이는 자료마다 달라서 ANSSI 예시는 8자리이고 Windows 10 21H2 관찰 예(Psmths)는 16자리입니다.

ANSSI 의 값 목록에 없는 `Usn`·`OriginalFileName`·`Description`·`AppxPackageFullName`·`AppxPackageRelativeId` 도 쓰입니다. Windows 10 21H2 관찰 예에는 `Usn` 이 있고 공개 파서(AmcacheParser)도 이 값들을 읽지만, 어느 버전에서 처음 생겼는지는 확인하지 못했습니다.

Windows 11 도 같은 점검 기능을 쓰고 Microsoft 진단 데이터 문서에 같은 이름의 인벤토리 이벤트가 있습니다. 다만 Windows 11 하이브의 버전별 차이를 정리한 공개 자료는 찾지 못했습니다.

## 구조

하위 키 안에 있는 값입니다. "근거" 칸의 "문서" 는 Microsoft 진단 데이터 문서의 같은 이름 필드 설명입니다. "연구" 는 ANSSI 자료입니다. "추정" 은 공식 정의가 없어서 이름과 관찰로 해석한 값입니다.

| 값 | 형식 | 뜻 | 근거 |
|---|---|---|---|
| `LowerCaseLongPath` | REG_SZ | 파일 전체 경로. 소문자로 남습니다. | 문서 |
| `LongPathHash` | REG_SZ | 경로로 만든 식별자. 관찰 예에서는 하위 키 이름과 같습니다. | 연구·관찰 |
| `Name` | REG_SZ | 파일 이름 | 문서 |
| `FileId` | REG_SZ | `0000` 뒤에 파일 내용의 SHA-1 40자리가 붙습니다. | 문서·연구 |
| `Size` | REG_QWORD | 파일 크기(바이트). 10.0.14913 라이브러리에서는 16진 문자열입니다. | 연구 |
| `ProgramId` | REG_SZ | 파일이 속한 프로그램의 식별자. 이름·버전·게시자·언어로 만든 해시입니다. | 문서 |
| `Publisher` | REG_SZ | 게시자 | 연구 |
| `Version`·`BinFileVersion` | REG_SZ | 파일 버전. `Bin` 쪽은 버전을 숫자 네 칸으로 정리한 값입니다. | 문서 |
| `ProductName`·`ProductVersion`·`BinProductVersion` | REG_SZ | 제품 이름과 제품 버전 | 문서 |
| `LinkDate` | REG_SZ | 파일이 링크된 시각. `MM/DD/YYYY HH:MM:SS` 꼴 문자열입니다. | 문서 |
| `BinaryType` | REG_SZ | 실행 파일 종류. `PE32_I386`, `PE64_AMD64`, `PE32_CLR_32` 같은 이름입니다. | 문서 |
| `Language` | REG_DWORD | 언어 코드 (LCID). 파일 버전 정보의 언어로 봅니다. | 추정 |
| `IsPeFile` | REG_DWORD | PE 파일이면 1 | 추정 |
| `IsOsComponent` | REG_DWORD | 윈도 구성 요소면 1 | 추정 |
| `Usn` | REG_QWORD | NTFS 변경 저널 번호 (USN) 로 보입니다. Microsoft 는 뜻을 밝히지 않았습니다. | 추정 |
| `OriginalFileName`·`Description` | REG_SZ | 버전 정보의 원래 파일 이름과 설명 | 추정 |
| `AppxPackageFullName`·`AppxPackageRelativeId` | REG_SZ | 스토어 앱 패키지에 속한 파일일 때의 패키지 이름 | 추정 |

- 관찰 예(Psmths)에서는 `Publisher`·`ProductName`·`BinaryType` 도 소문자로 남았습니다. 문자열을 찾을 때는 대소문자를 가리지 않습니다.
- 값이 어떻게 셀에 저장되는지는 [하이브 내부 구조](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md) 에서 다룹니다.

### 설치 프로그램과 잇기 (ProgramId)

> 그림 자리: InventoryApplicationFile 하위 키의 `ProgramId` 값이 InventoryApplication 하위 키 이름과 이어지는 모습. 짝이 있는 항목과 짝이 없는 항목을 나란히 보여 주는 그림

[설치 프로그램 항목 (InventoryApplication)](inventoryapplication.md) 의 하위 키 이름은 `ProgramId` 이고(ANSSI), 이 키의 `ProgramId` 와 같은 이름의 하위 키가 있으면 그 설치 프로그램에 딸린 파일입니다. 짝이 없는 항목은 설치 기록과 이어지지 않는 파일이며, 공개 파서 AmcacheParser 는 이런 항목을 "Unassociated" 로 따로 모읍니다. 설치 없이 들어온 파일이 이 무리에 섞이므로 먼저 훑어볼 후보가 됩니다. 다만 프로그램을 지우면 InventoryApplication 쪽 하위 키가 지워지므로(ANSSI), 짝이 없다는 것만으로 설치 없이 들어온 파일이라고 단정하지 않습니다.

## 증거로서 의미

### 증명하는 것

- 기록한 때에 그 경로에 그 파일이 있었습니다. 경로와 크기와 SHA-1 이 함께 남습니다.
- 파일이 지금 디스크에 없어도 경로와 SHA-1 로 무슨 파일이었는지 찾아볼 수 있습니다. SHA-1 은 [해시셋 대조](../../../03-techniques/analysis/hash-set-fuzzy-hash.md) 로 알려진 파일과 맞춰 봅니다.
- 버전 정보와 게시자로 파일이 무엇인지 좁힐 수 있습니다.
- `ProgramId` 로 어느 설치 프로그램에 딸린 파일인지 알 수 있습니다.

### 증명하지 못하는 것

- 대부분의 항목은 실행 기록이 아닙니다. 폴더를 훑거나 프로그램을 설치할 때도 항목이 생깁니다.
- 누가 파일을 두었는지, 누가 실행했는지는 남지 않습니다. 사용자를 가리키는 값이 없습니다.
- 실행 횟수와 마지막 실행 시각은 없습니다.
- 큰 파일의 `FileId` 는 파일 전체의 해시가 아닐 수 있습니다. 계산 범위는 [AmCache 해석 함정](sha1.md) 에서 다룹니다.
- 항목이 없다고 파일이 없었던 것은 아닙니다. 점검 작업이 돌기 전에 지운 파일은 목록에 들어오지 않을 수 있습니다.
- 항목이 언제 지워지는지는 공개 자료로 확인하지 못했습니다.

보고서에는 기록이 말하는 만큼만 씁니다.

> `Amcache.hve` 의 InventoryApplicationFile 에 `<경로>` 항목이 있습니다. 이 항목의 SHA-1 은 `<값>` 이고, 하위 키의 마지막 기록 시각은 `<시각> UTC` 입니다. 이 시각에 이 경로에 이 파일이 있었다는 기록입니다. 이 항목만으로는 실행 여부를 판단할 수 없습니다.

## 시각 해석

| 시각 | 있는 곳 | 기준 | 언제 정해지나 |
|---|---|---|---|
| 하위 키 마지막 기록 시각 | 하위 키 (nk 셀) | FILETIME, UTC | 항목을 쓰거나 고칠 때 |
| `LinkDate` | 값 | 문자열, 시간대 표시 없음 | 파일을 빌드할 때. 이 PC 에서 일어난 일이 아닙니다. |

### 하위 키 마지막 기록 시각

ANSSI 실험에서 이 시각의 뜻은 라이브러리 버전에 따라 달랐습니다.

| 라이브러리 버전 | 하위 키 시각이 맞은 때 |
|---|---|
| 10.0.14913 | 늘 점검 작업이 돈 때 |
| 10.0.16299 이후, 호환성 조치가 필요한 창 프로그램을 실행한 경우 | 처음 실행한 때 |
| 10.0.16299 이후, 그 밖의 경우 | 실행한 때와, 파일이 생긴 뒤 처음 점검 작업이 돈 때 가운데 이른 쪽 |

- 가장 안전한 해석은 "이 시각에 이 경로에 이 파일이 있었다" 입니다.
- 파일이 처음 생긴 때는 이 시각보다 앞일 수 있습니다.
- 이 시각은 키 단위입니다. 어느 값이 바뀌어서 시각이 바뀌었는지는 알 수 없습니다. 자세한 성질은 [키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md) 에서 다룹니다.

### LinkDate

- Microsoft 문서는 이 값을 "파일이 링크된 날짜와 시각" 이라고 설명합니다.
- PE 헤더의 링크 시각 칸 (TimeDateStamp) 은 1970년 1월 1일 0시부터 센 초입니다.
- 공개 파서 AmcacheParser 는 이 문자열을 UTC 로 읽습니다.
- 이 칸은 파일을 만든 쪽이 정합니다. 마음대로 바꿀 수 있습니다.
- Windows 10 의 자체 모듈은 재현 가능한 빌드 (reproducible build) 때문에 이 칸에 시각 대신 해시를 넣습니다(Raymond Chen). 그래서 엉뚱한 날짜가 나옵니다.
- 원본 파일이 남아 있으면 헤더 값과 맞춰 봅니다. PE 헤더는 [실행 파일 메타데이터](../../embedded-metadata/pe-header-version-info-digital-signature.md) 에서 다룹니다.

## 함정과 한계

- **항목은 경로마다 하나입니다.** 하위 키 이름이 경로로 정해지기 때문입니다. 같은 경로의 파일을 다른 파일로 바꾸면 같은 항목의 값이 바뀔 수 있습니다. 이전 `FileId` 는 [지워진 키·값 복구](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md), [트랜잭션 로그](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md), [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에서 찾아봅니다.
- **같은 파일도 경로가 다르면 항목이 따로 생깁니다.** `FileId` 로 묶어 보면 복사해 옮긴 흔적이 보입니다.
- **점검 작업이 돌아야 목록이 채워집니다.** 이 작업이 꺼져 있거나 오래 돌지 않은 PC 에서는 새 항목이 늦게 생기거나 생기지 않을 수 있습니다.
- **경로는 소문자로만 남습니다.** 원래 대소문자는 알 수 없습니다.
- **최근 변경이 하이브 본문에 없을 수 있습니다.** 사용 중인 하이브는 바뀐 내용을 `.LOG1`·`.LOG2` 에 먼저 적습니다. 로그를 반영하지 않으면 최근 항목을 놓칩니다.
- **도구마다 읽는 값이 다릅니다.** AmcacheParser 소스는 `AppxPackageFullName` 같은 값을 결과에 넣지 않습니다. 결과가 이상하면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 처럼 원시 값을 다시 봅니다.
- **하이브는 오프라인에서 고칠 수 있습니다.** 지운 하위 키는 빈 셀로 남을 수 있습니다. 다른 실행 흔적과 어긋나는 항목은 조작을 의심해 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

1. `Amcache.hve` 와 `.LOG1`·`.LOG2` 를 함께 복사합니다. 켜져 있는 시스템에서는 하이브가 잠겨 있습니다. 수집 방법은 [선별 수집](../../../03-techniques/process-acquisition/evidence-acquisition/triage-collection.md) 에서 다룹니다.
2. 사본에 트랜잭션 로그를 반영합니다.
3. `Root` → `InventoryApplicationFile` → 하위 키 순서로 내려갑니다.
4. 하위 키의 값 셀 (vk) 에서 이름·형식·데이터를 읽습니다. 형식 번호는 REG_SZ 가 1, REG_DWORD 가 4, REG_QWORD 가 11 입니다.
5. 하위 키 셀 (nk) 의 마지막 기록 시각을 FILETIME 으로 풉니다. 변환은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

아래는 명세로 만든 예시입니다. 실제 검체에서 나온 값이 아닙니다. `FileId` 에는 설명하려고 빈 데이터의 SHA-1 (`da39a3ee…`) 을 넣었습니다.

```
FileId (REG_SZ, UTF-16LE) 데이터 앞부분
30 00 30 00 30 00 30 00  64 00 61 00 33 00 39 00     "0000da39"
→ 앞 "0000" 4글자를 떼면 SHA-1 40글자가 이어집니다.
→ 44글자 × 2바이트 = 88바이트이고, 끝에 NUL 이 붙으면 더 깁니다.

Size (REG_QWORD, 8바이트, 리틀 엔디언)
87 D6 12 00 00 00 00 00                              0x12D687 = 1,234,567 바이트

LinkDate (REG_SZ, UTF-16LE)
30 00 31 00 2F 00 30 00  32 00 2F 00 32 00 30 00     "01/02/20"
32 00 34 00 20 00 30 00  33 00 3A 00 30 00 34 00     "24 03:04"
3A 00 30 00 35 00                                    ":05"
→ "01/02/2024 03:04:05" = 2024년 1월 2일 03:04:05 (월/일/년 순서)
```

`LinkDate` 는 월이 앞에 옵니다. 일/월 순서로 읽으면 날짜가 틀립니다.

### 공개 도구로 한 번

- 레지스트리 뷰어(예: Registry Explorer, RegRipper 의 amcache 플러그인)로 같은 하위 키를 열어 헥스로 읽은 값과 맞춥니다.
- 전용 파서(예: AmcacheParser)는 `ProgramId` 로 InventoryApplication 과 짝을 지어 줍니다. 짝이 없는 항목만 따로 볼 때 편합니다. 이 파서는 `FileId` 앞의 `0` 을 떼고 SHA-1 만 보여 줍니다.
- 메모리 이미지에서는 Volatility 3 의 amcache 플러그인이 같은 키를 읽습니다.
- 두 가지 이상의 도구로 항목 수와 값을 비교합니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 더 알려 주는 것 |
|---|---|
| [설치 프로그램 항목 (InventoryApplication)](inventoryapplication.md) | `ProgramId` 의 짝, 설치 날짜 |
| [바로가기 항목 (InventoryApplicationShortcut)](inventoryapplicationshortcut.md) | 같은 프로그램의 시작 메뉴 바로가기 |
| [드라이버 항목 (InventoryDriverBinary)](inventorydriverbinary.md) | SYS 파일의 해시와 서명 정보 |
| [프리페치 (Prefetch)](../prefetch/index.md) | 실행 횟수, 실행 시각 |
| [심캐시 (ShimCache·AppCompatCache)](../shimcache-appcompatcache.md) | 같은 경로의 파일 수정 시각 |
| [BAM·DAM](../background-activity-moderator.md) · [UserAssist](../userassist.md) | 실행한 사용자, 마지막 실행 시각 |
| [마스터 파일 테이블 ($MFT)](../../filesystem/mft.md) | 파일이 생긴 시각. 하위 키 시각보다 앞서는지 봅니다. |
| [USN 변경 저널 ($UsnJrnl)](../../filesystem/usnjrnl.md) | 파일이 생기고 지워진 기록. `Usn` 값을 맞춰 볼 곳입니다. |
| [다운로드 출처 표시 (Zone.Identifier)](../../filesystem/zone-identifier.md) | 파일을 내려받은 주소 |
| [프로세스 생성 (4688)](../../event-logs/4688.md) · [Sysmon 이벤트 1](../../event-logs/sysmon/1.md) | 켜 둔 경우 실행 증거와 명령줄 |
| [예약 작업 이벤트 (TaskScheduler·4698)](../../event-logs/taskscheduler-4698.md) | 로그가 켜져 있으면 점검 작업이 돈 시각 |

여러 흔적을 묶어 읽는 순서는 [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md) 에서 다룹니다.

## 실습

Windows 10 이상 공개 검체(NIST CFReDS 등)의 `Amcache.hve` 로 풀어 봅니다.

1. `ProgramId` 의 짝이 없는 항목을 모두 뽑습니다. 그 가운데 `\users\` 아래 경로는 몇 개입니까?
2. 한 항목의 `FileId` 와 디스크에 남은 같은 경로 파일의 SHA-1 이 같습니까? 다르면 먼저 `Size` 를 봅니다.
3. 같은 설치 폴더에 있는 항목들의 하위 키 시각을 나란히 놓습니다. 혼자 튀는 항목이 있습니까?
4. 한 항목의 하위 키 시각, 같은 파일의 `$MFT` 생성 시각, 프리페치 실행 시각은 어떤 순서입니까?
5. 실습용 가상 머신에서 실행 파일 하나를 바탕 화면에 복사만 하고 실행하지 않습니다. 점검 작업이 돈 뒤 항목이 생기는지 하이브를 전후로 비교합니다.

## 참고 문헌

- Blanche Lagny (ANSSI), "Analysis of the AmCache" v2 (2019) — https://cyber.gouv.fr/documents/632/anssi-coriin_2019-analysis_amcache-v2.pdf
- Microsoft Learn, "Required diagnostic events and fields for Windows 11, versions 23H2 and 22H2" (`Microsoft.Windows.Appraiser.General.InventoryApplicationFileAdd`) — https://learn.microsoft.com/en-us/windows/privacy/required-diagnostic-events-fields-windows-11-22h2
- Microsoft Learn, "PE Format" (COFF File Header 의 TimeDateStamp) — https://learn.microsoft.com/en-us/windows/win32/debug/pe-format
- Raymond Chen, "Why are the module timestamps in Windows 10 so nonsensical?", The Old New Thing (2018) — https://devblogs.microsoft.com/oldnewthing/20180103-00/?p=97705
- Eric Zimmerman, AmcacheParser 소스 `Amcache/AmcacheNew.cs` — https://github.com/EricZimmerman/AmcacheParser/blob/master/Amcache/AmcacheNew.cs
- Psmths, "AmCache.hve", windows-forensic-artifacts — https://github.com/Psmths/windows-forensic-artifacts/blob/main/execution/amcache.md
