# 프로그램 설치·삭제 이벤트 (MsiInstaller)

## 한 줄 요약

Windows Installer (MSI) 로 프로그램을 설치하거나 제거하거나 구성을 바꾸면 응용 프로그램 로그 (Application) 에 이벤트가 남습니다. 이벤트의 원본 (Source) 이름은 MsiInstaller 이고, 제품 이름, 버전, 제조사, 결과 상태가 적힙니다. 관찰 PC 에서는 Binary 칸에 제품 코드 (ProductCode) 가 들어 있었습니다. 제품을 지운 뒤에도 이벤트는 남으므로 레지스트리 설치 목록에서 사라진 앱의 이력을 찾을 수 있습니다. 시각은 UTC 이며, 관찰 PC 처럼 로그가 순환하면 오래된 기록부터 사라집니다.

> 이 페이지에서 "관찰 PC" 는 Windows 11 Home 25H2(빌드 26200, 시간대 Korea Standard Time) PC 한 대를 말합니다. 관찰 PC 에서 본 내용은 모두 "확인 범위: Win11 25H2 한 대" 입니다. 다른 PC 에서도 같다고 보장하지 못합니다.

## 무엇을 기록하나 · 왜 생기나

Windows Installer 는 설치·제거·복구가 성공했는지 실패했는지, 제품을 구성하다가 난 오류, 손상된 구성 데이터를 찾은 일을 이벤트 로그에 씁니다. 기록이 많아 로그 파일이 가득 차면 설치 관리자가 "The Application log file is full." 메시지를 띄웁니다.

### 이벤트 번호를 짓는 규칙

Windows Installer 의 오류 메시지 표 (Error table) 에 있는 일반 메시지는 "메시지 번호 + 10,000" 을 이벤트 ID 로 씁니다. 예를 들어 설치 성공 메시지 1707 은 이벤트 11707 로 남습니다.

| 이벤트 | 메시지 번호 | 메시지 | 확인한 곳 |
|---|---|---|---|
| 11707 | 1707 | Installation operation completed successfully. | Microsoft 이벤트 표에 있습니다 |
| 11708 | 1708 | Installation operation failed. | Microsoft 이벤트 표에 있습니다 |
| 11724 | 1724 | Removal completed successfully. | Microsoft 이벤트 표에는 없습니다. 관찰 PC 에는 실제로 남아 있었습니다 |
| 11725 | 1725 | Removal failed. | 번호 규칙으로 계산한 값입니다. 실제 기록은 보지 못했습니다 |
| 11728 | 1728 | Configuration completed successfully. | Microsoft 이벤트 표에 있습니다 |
| 11729 | 1729 | Configuration failed. | 번호 규칙으로 계산한 값입니다. 실제 기록은 보지 못했습니다 |

관찰 PC 의 11724 는 "Product: DB Browser for SQLite -- Removal completed successfully." 였습니다. 문서 표에 없는 번호도 실제로 남는다는 뜻입니다. 도구가 알려진 번호만 뽑는다면 이 기록을 놓칩니다.

### 결과 요약 이벤트 (1033~1038)

Microsoft 문서가 적은 메시지 틀입니다.

| 이벤트 | 내용 | 메시지 틀 |
|---|---|---|
| 1033 | 설치 결과 | `Product: %1. Version: %2. Language: %3. Installation completed with status: %4. Manufacturer: %5.` |
| 1034 | 제거 결과 | 1033 과 같은 틀에 `Removal completed with status: %4` |
| 1035 | 구성 변경 결과 | 1033 과 같은 틀에 `Configuration change completed with status: %4` |
| 1036 | 업데이트 설치 결과 | `Update: %4 … completed with status: %5. Manufacturer: %6.` |
| 1037 | 업데이트 제거 결과 | 1036 과 같은 틀 |
| 1038 | 재부팅이 필요함 | 재부팅 종류 (Reboot Type) 와 재부팅 이유 (Reboot Reason) 를 적습니다 |

1033 의 칸은 차례로 ProductName, ProductVersion, ProductLanguage, 상태, Manufacturer 입니다. 1036·1037 의 Update 칸에는 패치 이름이 들어가는데, 패치에 MsiPatchMetadata 표가 있으면 알아보기 쉬운 이름이, 없으면 패치 코드 GUID 가 들어갑니다.

1038 의 두 값은 아래와 같습니다.

| 값 | 뜻 |
|---|---|
| Reboot Type 1 | 바로 다시 시작합니다 |
| Reboot Type 2 | 다시 시작을 미룹니다 |
| Reboot Reason 0 | 이유를 모릅니다 |
| Reboot Reason 1 | 사용 중인 파일을 바꿨습니다 |
| Reboot Reason 2 | ScheduleReboot 동작 때문입니다 |
| Reboot Reason 3 | ForceReboot 동작 때문입니다 |
| Reboot Reason 4 | 사용자 지정 동작이 MsiSetMode 를 불렀습니다 |

### 트랜잭션 시작과 끝 (1040·1042)

관찰 PC 에는 Microsoft 이벤트 표에 없는 1040 과 1042 가 있었습니다.

1040 은 "Beginning a Windows Installer transaction: <.msi 경로>. Client Process Id: <번호>." 이고, 1042 는 "Ending a Windows Installer transaction: …" 입니다. Data 1 에는 .msi 경로가, Data 2 에는 클라이언트 프로세스 ID 가 들어 있었습니다.

관찰 PC 의 1040 한 건은 경로가 `C:\Users\<사용자>\AppData\Local\Temp\<임의 폴더>\data\<16진 32자>-x64.msi` 모양이고 Client Process Id 는 27940 이었습니다. 이 경로로 설치에 쓴 .msi 파일이 그때 사용자 임시 폴더에 있었다는 것을 알 수 있습니다.

### 그 밖의 이벤트

Microsoft 이벤트 표에 있는 이벤트입니다.

| 이벤트 | 내용 |
|---|---|
| 1005 | 설치가 재부팅을 시작했습니다 |
| 1007, 1008 | 소프트웨어 제한 정책이 설치를 막았습니다 |
| 1019 | 업데이트를 제거했습니다 |
| 1020, 1021 | 업데이트 제거가 실패했습니다 |
| 1022 | `Product: %1 - Update '%2' installed successfully.` |
| 1023, 1024 | 업데이트 설치가 실패했습니다 |
| 1025 | `Product: %1. The file %2 is being used by the following process: Name: %3 , Id %4.` |
| 1044 | Microsoft 서명이 없어 Windows 잠금 정책 (Windows Lockdown Policy) 이 거부했습니다 |
| 10005 | 예상하지 못한 내부 오류입니다 |

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 로그 | 응용 프로그램 (Application) |
| 원본 이름 | MsiInstaller |
| 로그 파일 | `%SystemRoot%\System32\Winevt\Logs\Application.evtx` |
| 메시지 파일 | `HKLM\SYSTEM\CurrentControlSet\Services\EventLog\Application\MsiInstaller` 의 `EventMessageFile` 값. 관찰 PC 에서는 `C:\Windows\System32\msimsg.dll` 이었습니다 |

- MsiInstaller 는 매니페스트 공급자가 아니라 예전 방식의 이벤트 원본이며, 관찰 PC 에서 공급자 GUID 가 0 이었습니다.
- 관찰 PC 레코드의 Keywords 는 `0x80000000000000` 이었고, 이 값은 표준 키워드 EventLogClassic 입니다.
- 오프라인 이미지에서는 SYSTEM 하이브의 `ControlSet00X` 아래 같은 경로를 엽니다. `ControlSet00X` 를 고르는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.
- 메시지 파일로 문장을 푸는 법은 [공급자와 메시지 파일](../../01-foundations/database-log-formats/evtx-evt-etl/provider-message-table.md)에서 다룹니다.

### 관찰 PC 의 로그 상태

| 항목 | 값 |
|---|---|
| Application 로그 최대 크기 | 20,971,520 바이트 |
| 꽉 찼을 때 | 오래된 기록부터 덮어씁니다 |
| 레코드 수 | 18,747건 |
| 가장 오래된 레코드 | 2026-08-28 |

관찰한 날 기준으로 약 한 달치만 남아 있었습니다. 이 가운데 MsiInstaller 이벤트 수는 아래와 같았습니다.

| 이벤트 | 1033 | 1034 | 1035 | 1040 | 1042 | 11707 | 11724 | 11728 |
|---|---|---|---|---|---|---|---|---|
| 건수 | 11 | 3 | 4 | 19 | 19 | 11 | 3 | 4 |

11707 과 1033, 11724 와 1034, 11728 과 1035, 1040 과 1042 의 건수가 서로 같습니다. 관찰 PC 에서는 이 이벤트들이 짝을 지어 남았습니다. 짝은 "시각 해석" 에서 다룹니다.

### Windows Installer 판에 따른 차이

- Windows Installer 3.1 이하에는 1033·1034·1036·1037·1038 이 없습니다.
- Windows Installer 4.5 이하에는 Manufacturer 칸이 없습니다.
- Windows Installer 의 어느 판이 어느 Windows 에 들어갔는지는 이 글에서 확인하지 못했습니다.

### 문서의 문장과 실제 문장이 다르다

관찰 PC 의 1033·1034·1035 문장은 Microsoft 문서의 틀과 달랐습니다.

| 이벤트 | 관찰 PC 의 문장 (Win11 25H2) |
|---|---|
| 1033 | `Windows Installer installed the product. Product Name: …. Product Version: …. Product Language: 1033. Manufacturer: …. Installation success or error status: 0.` |
| 1034 | `Windows Installer removed the product. … Removal success or error status: 0.` |
| 1035 | `Windows Installer reconfigured the product. … Reconfiguration success or error status: 0.` |

문서의 문장으로 검색하면 이 기록을 놓칩니다. 원본 이름과 이벤트 ID 로 거릅니다.

## 구조

### 1033·1034·1035 의 EventData

관찰 PC 에서는 이름 없는 Data 가 6개 있었습니다.

| 순서 | 뜻 | 관찰 PC 의 1033 한 건 |
|---|---|---|
| 1 | 제품 이름 | `Microsoft.NET.Workloads.10.0.300 (x64)` |
| 2 | 버전 | `84.188.58235` |
| 3 | 언어 | `1033` |
| 4 | 상태 | `0` |
| 5 | 제조사 | `Microsoft Corporation` |
| 6 | 비어 있음 | `(NULL)` |

제품 이름은 설치 패키지의 ProductName 속성 값이라서 실제 프로그램과 다를 수 있습니다. 언어 칸의 1033 은 이벤트 ID 1033 과 다른 값이므로 둘을 헷갈리지 않습니다. 관찰 PC 에는 1035 의 언어 칸이 0 인 레코드도 있었습니다(Office 16 Click-to-Run Extensibility Component).

### 상태 값

설치 관리자의 반환 코드는 아래와 같습니다.

| 코드 | 이름 | 뜻 |
|---|---|---|
| 0 | ERROR_SUCCESS | 성공 |
| 1602 | ERROR_INSTALL_USEREXIT | 사용자가 취소했습니다 |
| 1603 | ERROR_INSTALL_FAILURE | 설치하다가 치명적인 오류가 났습니다 |
| 1605 | ERROR_UNKNOWN_PRODUCT | 모르는 제품입니다 |
| 1618 | ERROR_INSTALL_ALREADY_RUNNING | 다른 설치가 진행 중입니다 |
| 1619 | ERROR_INSTALL_PACKAGE_OPEN_FAILED | 설치 패키지를 열지 못했습니다 |
| 1620 | ERROR_INSTALL_PACKAGE_INVALID | 설치 패키지가 올바르지 않습니다 |
| 1625 | ERROR_INSTALL_PACKAGE_REJECTED | 시스템 정책이 설치를 금지합니다 |
| 1638 | ERROR_PRODUCT_VERSION | 다른 버전이 이미 설치돼 있습니다 |
| 1641 | ERROR_SUCCESS_REBOOT_INITIATED | 성공했고 다시 시작을 시작했습니다 |
| 3010 | ERROR_SUCCESS_REBOOT_REQUIRED | 성공했고 다시 시작이 필요합니다 |

0, 1641, 3010 이 성공입니다. 1033 의 상태 칸에 이 반환 코드가 그대로 들어간다고 적은 문서는 찾지 못했고, 관찰 PC 의 1033·1034·1035 는 상태가 모두 0 이었습니다.

### 11707·11724·11728 의 EventData

관찰 PC 에서는 첫 Data 에 완성된 문장이 들어 있었고 나머지 Data 5개는 `(NULL)` 이었습니다. 문장이 레코드 안에 그대로 저장되므로 한 로그 안에서 언어가 섞일 수 있습니다. 관찰 PC 의 11707 은 영어(`Product: … -- Installation completed successfully.`)였고, 같은 PC 의 11728 은 한국어(`제품: Office 16 Click-to-Run Extensibility Component -- 구성을 마쳤습니다.`)였습니다. Microsoft 문서에 따르면, 패키지에 이벤트용 오류 문자열이 없을 때 설치 관리자는 ProductLanguage 속성의 언어로 된 문자열을 불러옵니다.

### Binary 칸과 제품 코드

| 이벤트 | Binary 칸을 ASCII 로 풀면 (관찰 PC) |
|---|---|
| 11707, 11724, 11728 | 제품 코드 GUID 문자열 |
| 1033, 1034, 1035 | 제품 코드 뒤에 `0000` + 16진 32자 + 16진 8자 |

관찰 PC 에서 마지막 16진 8자는 `00000904` 이거나 `00000000` 이었고, 제품 코드 뒤에 붙는 부분의 뜻은 확인하지 못했습니다. 같은 제품을 여러 번 설치해도 1033 의 Binary 는 바이트 하나까지 같았는데, 관찰 PC 의 .NET Workloads 제품 1033 9건이 그랬습니다. 그래서 Binary 로는 설치 한 번 한 번을 가를 수 없고 시각으로 가릅니다.

제품 코드로 레지스트리의 설치 목록을 찾을 수 있습니다. 관찰 PC 에서 `{A7AB73A3-CB10-4AA5-9D38-6AEFFBDE4C91}` 로 `SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{A7AB73A3-CB10-4AA5-9D38-6AEFFBDE4C91}` 키를 찾았습니다.

| 값 | 관찰 PC |
|---|---|
| 제품 | Microsoft Teams Meeting Add-in for Microsoft Office 1.26.21803 |
| InstallDate | 20260907 |
| InstallSource | `C:\Users\<사용자>\AppData\Local\Microsoft\TeamsMeetingAddinMsis\1.26.21803\` |
| WindowsInstaller | 1 |

`Uninstall` 키의 값과 32비트·사용자별 위치는 [설치 프로그램](../system-account/uninstall.md)에서 다룹니다.

### 기록한 계정

레코드의 System 부분에 있는 `Security UserID` 에 SID 가 들어갑니다. 관찰 PC 에는 사용자 SID(`S-1-5-21-…-1001`) 인 레코드와 `S-1-5-18`(SYSTEM) 인 레코드가 섞여 있었습니다. Teams Meeting Add-in 과 .NET Workloads 설치는 사용자 SID 였고, Office Click-to-Run 구성 변경(11728·1035)은 `S-1-5-18` 이었습니다. 한 트랜잭션에서 1040 은 사용자 SID 로, 1042 는 `S-1-5-18` 로 남은 예도 있었습니다.

이 SID 가 "설치를 시작한 사람" 이라고 적은 문서는 찾지 못했습니다. 업데이트 서비스가 SYSTEM 으로 설치했다면 사용자가 한 일이 아닐 수 있습니다.

SID 의 모양과 읽는 법은 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md)에서 다룹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 기록된 시각에 이 제품 코드의 MSI 설치·제거·구성 변경이 이 상태로 끝났다는 기록이 있습니다 | 계정 뒤의 사람이 직접 설치했다는 것 (SID 의 뜻을 확인하지 못했고, SYSTEM 으로 남는 기록도 있습니다) |
| 설치 패키지가 적은 제품 이름, 버전, 제조사 | 제품 이름이 실제 프로그램과 같다는 것 |
| 지금 `Uninstall` 키에 없는 제품도 이벤트가 남아 있으면 설치·제거 이력을 보여 줍니다 | `Uninstall` 키가 없으니 제거했다는 것 |
| 1040 이 있으면 설치에 쓴 .msi 파일의 경로 | 설치한 프로그램을 실행했다는 것 |
| | 이벤트가 없으니 설치하지 않았다는 것 (로그가 덮어써졌거나 MSI 가 아닐 수 있습니다) |

### 보고서 문장

아래 시각과 이름은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "응용 프로그램 로그에는 <시각> UTC 에 MsiInstaller 1033 이 있습니다. 제품 이름은 ○○, 버전은 ○○, 상태 값은 0 입니다. 같은 시각의 11707 Binary 칸을 풀면 제품 코드 {…} 입니다. 레코드의 SID 는 사용자 ○○ 의 SID 입니다."
- 쓰면 안 되는 문장: "○○ 이 이 프로그램을 설치해 사용했다."

두 번째 문장은 사람과 사용을 단정합니다. 이벤트에는 설치 결과와 SID 만 있습니다. 실행은 다른 기록으로 확인합니다.

## 시각 해석

이벤트 시각은 `<TimeCreated SystemTime>` 에 있고, 끝에 Z 가 붙은 UTC 값입니다. 관찰 PC 의 한 레코드는 `2026-09-22T22:45:04.4126114Z` 였는데, 한국 시각으로는 2026-09-23 07:45:04 라서 날짜가 하루 바뀝니다. 현지 시각으로 바꾸는 법은 [시간대 설정](../system-account/time-zone.md)에서 다룹니다.

### 짝으로 남는 기록

관찰 PC 에서는 한 번의 조작이 두 이벤트로 1ms 안쪽 간격을 두고 남았습니다.

| 조작 | 짝 |
|---|---|
| 설치 | 11707 + 1033 |
| 제거 | 11724 + 1034 |
| 구성 변경 | 11728 + 1035 |

업그레이드로 보이는 경우도 있었습니다. Teams Meeting Add-in 은 `2026-09-07 02:53:33Z` 에 제거(11724·1034)가 남았습니다. 약 2초 뒤인 `02:53:35Z` 에 같은 제품 코드의 설치(11707·1033)가 남았습니다. 제거 바로 뒤에 같은 제품 코드의 설치가 오면 업그레이드일 수 있습니다.

### 1040 과 1033 의 시각

1040 이 설치의 시작이고 11707·1033 이 설치의 끝이라는 해석이 있을 수 있습니다. 이 글에서는 1040 과 1033 을 같은 설치로 묶어 시각 차이를 재 보지 않았습니다. 두 시각의 차이를 "설치에 걸린 시간" 으로 쓰지 않습니다.

### Uninstall 키의 날짜와 맞추기

관찰 PC 의 Teams Meeting Add-in 1033 은 `2026-09-07 02:53:35Z`(한국 시각으로 11:53:35)였고, 같은 제품의 `InstallDate` 는 20260907 이어서 날짜가 맞았습니다. `InstallDate` 는 처음 설치한 날이 아니라 마지막으로 패치·복구한 날일 수 있으며, 뜻은 [설치 프로그램](../system-account/uninstall.md)에서 다룹니다. `InstallDate` 가 어느 시간대 기준 날짜인지는 확인하지 못했으므로, UTC 날짜와 현지 날짜가 다른 시간대에 설치했다면 두 날짜를 모두 적어 비교합니다.

## 함정과 한계

1. **메시지 문장으로 검색합니다.** Win11 의 1033 문장은 문서의 틀과 다릅니다. 11707·11728 문장은 레코드마다 언어가 다를 수 있습니다. 원본 이름과 이벤트 ID 로 거릅니다.
2. **`Uninstall` 키가 없으면 제거했다고 봅니다.** 관찰 PC 에서 2026-09-21 에 제거(1034)된 DB Browser for SQLite `{541AE182-7C1D-426C-8155-4867303B75A4}` 는 HKLM(64비트·32비트)과 HKCU 어디에도 키가 없었습니다. 그런데 설치 기록(1033)만 있는 .NET Workloads `{4D85867C-3C0F-4100-BCD2-F1E7A383BB23}` 도 키가 없었습니다. 키가 없는 이유는 확인하지 못했습니다. 제거는 1034·11724 로 확인합니다.
3. **SID 를 설치한 사람으로 읽습니다.** SYSTEM 으로 남는 기록이 있습니다. 한 트랜잭션 안에서도 SID 가 바뀐 예가 있습니다.
4. **상태 칸을 반환 코드표로 바로 풉니다.** 상태 칸이 반환 코드라고 적은 문서는 찾지 못했습니다. 0 이 아닌 값이 나오면 같은 시각의 11708 같은 실패 이벤트와 함께 봅니다.
5. **문서 표에 없는 번호를 버립니다.** 11724·1040·1042 는 Microsoft 이벤트 표에 없지만 실제로 남았습니다.
6. **1033 Binary 가 같으니 같은 설치로 묶습니다.** 같은 제품을 다시 설치해도 Binary 가 같았습니다. 시각으로 나눕니다.
7. **MSI 가 아닌 설치도 여기 남는다고 봅니다.** 자체 EXE 설치 프로그램, 압축만 푸는 프로그램, 스토어 앱이 이 이벤트를 남기는지는 확인하지 못했습니다. 스토어 앱은 [스토어 앱 설치 목록](../system-account/appx-staterepository.md)을 따로 봅니다.
8. **오래된 설치를 찾습니다.** 관찰 PC 처럼 응용 프로그램 로그가 한 달쯤만 남으면 그보다 오래된 설치·제거는 이벤트로 볼 수 없습니다. 가장 오래된 레코드의 시각을 먼저 적어 둡니다.

### 지우기와 조작

- **응용 프로그램 로그를 지웁니다.** 지운 흔적은 [이벤트 로그 삭제](1102-104.md)에서 찾습니다.
- **로그를 빨리 채웁니다.** 로그가 꽉 차면 오래된 기록부터 덮어씁니다. 가장 오래된 레코드가 유난히 최근이면 로그 크기와 기록 양을 함께 봅니다.
- **흔적을 지우는 도구를 설치했다가 지웁니다.** 그 도구가 MSI 로 설치됐다면 1033 과 1034 가 남을 수 있습니다. 찾는 순서는 [완전삭제 도구를 썼나](../../04-scenarios/activity/anti-forensics/wiping-tools.md)에서 다룹니다.
- 지운 레코드를 파일 안에서 찾는 법은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번 — Binary 칸을 제품 코드로 풀기

Binary 칸은 제품 코드 GUID 문자열을 ASCII 바이트로 담습니다. 관찰 PC 의 Binary 칸 값은 `7B34443835…7D` 처럼 16진으로 보였습니다.

아래는 관찰 PC 에서 본 제품 코드 `{4D85867C-3C0F-4100-BCD2-F1E7A383BB23}` 를 ASCII 표대로 바이트로 옮긴 예시입니다. 레코드에서 그대로 떠 온 바이트가 아닙니다.

```
7B 34 44 38 35 38 36 37 43 2D 33 43 30 46 2D 34   {4D85867C-3C0F-4
31 30 30 2D 42 43 44 32 2D 46 31 45 37 41 33 38   100-BCD2-F1E7A38
33 42 42 32 33 7D                                 3BB23}
```

1. 이벤트 뷰어에서 11707 한 건을 열고 "자세히 → XML 보기" 로 갑니다.
2. Binary 칸의 16진 글자를 두 글자씩 끊습니다.
3. 두 글자를 한 바이트로 보고 ASCII 로 바꿉니다. `7B` 는 `{`, `7D` 는 `}` 입니다.
4. 처음 38바이트가 중괄호를 포함한 제품 코드입니다.
5. 1033 이면 38바이트 뒤에 `0000` 과 16진 글자가 더 이어집니다. 이 부분은 뜻을 확인하지 못했으므로 그대로 옮겨 적습니다.
6. 풀어 낸 제품 코드로 `Uninstall` 키를 찾습니다.

EVTX 파일 안에서 이 칸이 저장되는 방식은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.

### 공개 도구로 한 번

Windows 에 들어 있는 PowerShell 로 사본 파일에서 MsiInstaller 이벤트를 뽑고, Binary 칸을 제품 코드로 풀 수 있습니다.

```powershell
Get-WinEvent -Path .\Application.evtx -FilterXPath "*[System[Provider[@Name='MsiInstaller']]]" -Oldest |
  ForEach-Object {
    $x   = ([xml]$_.ToXml()).Event
    $hex = [string]$x.EventData.Binary
    $txt = -join ($hex -split '(..)' | Where-Object { $_ } | ForEach-Object { [char][Convert]::ToByte($_, 16) })
    [pscustomobject]@{
      TimeUtc     = $_.TimeCreated.ToUniversalTime()
      EventId     = $_.Id
      Sid         = $_.UserId
      Data1       = @($x.EventData.Data)[0]
      ProductCode = if ($txt.Length -ge 38) { $txt.Substring(0, 38) } else { $txt }
    }
  } | Format-Table -AutoSize
```

- 결과에서 같은 제품 코드끼리 모으면 설치·제거·다시 설치의 순서가 보입니다.
- 1033·1034·1035 의 Data 1 은 제품 이름이고, 11707·11724·11728 의 Data 1 은 완성된 문장입니다.
- EvtxECmd, python-evtx 같은 공개 도구도 이 레코드를 읽습니다. 도구가 Binary 칸을 빼고 보여 주는지 확인합니다. 도구의 풀이는 XML 원문 한두 건과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 무엇을 맞춰 보나 | 링크 |
|---|---|---|
| 설치 프로그램 목록 | 같은 제품 코드의 키가 있는지, `InstallDate` 와 `InstallSource` | [설치 프로그램](../system-account/uninstall.md) |
| AmCache 설치 프로그램 항목 | 같은 앱이 AmCache 에도 설치 프로그램으로 남아 있는지 | [설치 프로그램 항목 (InventoryApplication)](../execution/amcache-hve/inventoryapplication.md) |
| 프로세스 생성 (4688) | 1040 의 Client Process Id 와 같은 번호의 프로세스. 1040 은 10진(예: 27940), 4688 은 16진(예: `0x6D24`)이라 진법을 맞춥니다. 두 번호가 같은 프로세스를 가리키는지는 확인하지 못했습니다 | [프로세스 생성](4688.md) |
| 이벤트 로그 삭제 | 응용 프로그램 로그가 지워진 적이 있는지 | [이벤트 로그 삭제](1102-104.md) |
| 메시지 파일 | 도구가 문장을 제대로 풀었는지 | [공급자와 메시지 파일](../../01-foundations/database-log-formats/evtx-evt-etl/provider-message-table.md) |

설치한 프로그램을 실제로 실행했는지는 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md)의 순서로 확인합니다.

## 실습

직접 만든 Windows 10·11 가상 머신에서 해 봅니다. 각 단계의 시각을 적어 둡니다.

1. 공개된 MSI 설치 파일 하나로 프로그램을 설치합니다. 11707 과 1033 이 짝으로 남는지, 두 레코드의 Binary 칸이 어떻게 다른지 보십시오.
2. 설치 도중에 취소합니다. 1033 의 상태 칸에 어떤 값이 남는지 보십시오. "상태 값" 의 확인하지 못한 부분이 여기서 풀립니다.
3. 같은 프로그램을 제거합니다. 11724·1034 가 남는지, `Uninstall` 키가 사라지는지 보십시오.
4. 1040 이 남았다면 같은 설치의 1033 과 시각 차이를 재 보십시오.
5. EXE 설치 프로그램과 스토어 앱을 하나씩 설치합니다. MsiInstaller 이벤트가 남는지 보십시오. 함정 7번의 답이 여기서 나옵니다.
6. 관리자 계정과 일반 계정으로 각각 설치합니다. 레코드의 SID 가 어떻게 남는지 비교하십시오.

NIST CFReDS 같은 공개 검체에서 응용 프로그램 로그를 꺼냈다면 아래를 풀어 봅니다.

- 가장 오래된 레코드는 언제입니까? 그보다 오래된 설치는 이 로그로 볼 수 없습니다.
- 1034 나 11724 가 있는 제품 가운데 지금 `Uninstall` 키가 없는 제품은 무엇입니까?
- 1033 이 있는데 `Uninstall` 키가 없는 제품이 있습니까? 1034 도 있는지 확인하십시오.

## 참고 문헌

- Microsoft Learn, "Event Logging (Windows Installer)" — https://learn.microsoft.com/en-us/windows/win32/msi/event-logging
- Microsoft Learn, "Windows Installer Error Messages (for Developers)" — https://learn.microsoft.com/en-us/windows/win32/msi/windows-installer-error-messages
- Microsoft Learn, "MsiExec.exe and InstMsi.exe error messages (for developers)" — https://learn.microsoft.com/en-us/windows/win32/msi/error-codes
