---
title: "하이브 파일 종류와 위치"
parent: "레지스트리 하이브 구조"
grand_parent: "기반 · 데이터베이스·로그 형식"
nav_order: 140
---

# 하이브 파일 종류와 위치 (SYSTEM·SOFTWARE·SAM·SECURITY·NTUSER.DAT·UsrClass.dat)

레지스트리는 파일 하나가 아니라 여러 개의 하이브 (Hive) 파일이 디스크에 따로 저장된 것이고, 부팅할 때와 사용자가 로그온할 때 이 파일들이 한 트리에 붙습니다. 이 페이지는 어떤 파일이 어디에 있는지, 레지스트리 편집기의 어느 경로로 보이는지, 어떤 아티팩트를 담는지 정리합니다.

파일 안의 구조(regf 머리글·hbin·셀)는 [하이브 내부 구조 (regf·hbin·Cell)](regf-hbin-cell.md) 에서 다룹니다.

## 화면의 경로와 디스크의 파일

레지스트리 편집기에 보이는 최상위 키는 파일 이름과 1:1 로 맞지 않습니다. 먼저 둘의 관계를 정리합니다.

- `HKEY_LOCAL_MACHINE`(HKLM) 은 커널 안에서 `\REGISTRY\MACHINE` 입니다. 그 아래 SYSTEM·SOFTWARE·SAM·SECURITY 가 각각 따로 붙은 하이브 파일입니다.
- `HKEY_USERS`(HKU) 는 커널 안에서 `\REGISTRY\USER` 입니다. 지금 메모리에 올라온 사용자 하이브만 여기에 보입니다.
- `HKEY_CURRENT_USER`(HKCU) 는 따로 된 파일이 아닙니다. 현재 사용자의 `HKU\<SID>` 를 가리키는 이름입니다. SID 형식은 [윈도 식별자 형식 (SID·GUID·CLSID·Known Folder ID)](../../value-decoding/sid-guid-clsid-known-folder-id.md) 에 있습니다.
- `HKEY_CLASSES_ROOT`(HKCR) 도 따로 된 파일이 아닙니다. `HKLM\Software\Classes` 와 `HKCU\Software\Classes` 를 합쳐 보여 주는 화면입니다. 두 곳에 같은 설정이 있으면 사용자 쪽이 이깁니다.
- `HKEY_CURRENT_CONFIG` 는 SYSTEM 하이브 안의 현재 하드웨어 프로필을 보여 줍니다.
- `HKLM\HARDWARE` 는 휘발성 하이브 (Volatile Hive) 입니다. 부팅할 때마다 메모리에 새로 만들어지고, 디스크에 파일이 없습니다.

디스크 이미지에서 꺼낸 SYSTEM 파일에는 `CurrentControlSet` 키가 없습니다. 이 키는 실행 중에만 만들어지는 연결입니다. 파일에서 어느 컨트롤셋을 읽을지는 [컨트롤셋 고르기 (ControlSet·Select)](controlset-select.md) 를 봅니다.

## 하이브 파일 목록 (Windows Vista 이후)

`%SystemRoot%` 는 보통 `C:\Windows`, `%UserProfile%` 은 보통 `C:\Users\<사용자>` 입니다.

| 파일 | 디스크 위치 | 붙는 자리 | 누구의 설정인가 |
|---|---|---|---|
| SYSTEM | `%SystemRoot%\System32\config\SYSTEM` | `HKLM\SYSTEM` | 컴퓨터 전체 (부팅·장치·서비스) |
| SOFTWARE | `%SystemRoot%\System32\config\SOFTWARE` | `HKLM\SOFTWARE` | 컴퓨터 전체 (설치 프로그램·OS 설정) |
| SAM | `%SystemRoot%\System32\config\SAM` | `HKLM\SAM` | 로컬 계정 |
| SECURITY | `%SystemRoot%\System32\config\SECURITY` | `HKLM\SECURITY` | 보안 정책·LSA |
| DEFAULT | `%SystemRoot%\System32\config\DEFAULT` | `HKU\.DEFAULT` | LocalSystem 계정 (S-1-5-18) |
| NTUSER.DAT | `%UserProfile%\NTUSER.DAT` | `HKU\<SID>` (그 사용자에게는 HKCU) | 사용자 한 명 |
| UsrClass.dat | `%UserProfile%\AppData\Local\Microsoft\Windows\UsrClass.dat` | `HKU\<SID>_Classes` | 사용자 한 명 |
| 서비스 계정 NTUSER.DAT | `%SystemRoot%\ServiceProfiles\LocalService\NTUSER.DAT`, `...\NetworkService\NTUSER.DAT` | `HKU\S-1-5-19`, `HKU\S-1-5-20` | LocalService·NetworkService 계정 |
| BCD | UEFI 는 EFI 시스템 파티션의 `\EFI\Microsoft\Boot\BCD`, BIOS 방식은 활성 파티션(Microsoft 용어로 시스템 파티션)의 `\Boot\BCD` | `HKLM\BCD00000000` | 부팅 설정 |
| (없음) | 휘발성 | `HKLM\HARDWARE` | 부팅 때 찾은 장치 |

- `HKU\S-1-5-18` 은 따로 된 하이브가 아니라 `HKU\.DEFAULT` 를 가리키는 연결입니다.
- UsrClass.dat 는 사용자가 로그온하면 NTUSER.DAT 다음에 올라오고, `HKU\<SID>\Software\Classes` 는 이 `_Classes` 하이브를 가리키는 연결입니다.
- NTUSER.DAT 는 그 계정이 처음 로그온할 때 만들어지므로, 한 번도 로그온하지 않은 계정에는 프로필 폴더도 NTUSER.DAT 도 없습니다.

`%SystemRoot%\System32\config` 에는 이 밖에도 regf 형식 파일로 COMPONENTS·DRIVERS·ELAM·BBI 가 있지만 이 페이지에서는 다루지 않습니다.

regf 형식은 레지스트리 밖에서도 씁니다.

| 파일 | 위치 | 설명 페이지 |
|---|---|---|
| Amcache.hve | `%SystemRoot%\AppCompat\Programs\Amcache.hve` | [AmCache (Amcache.hve)](../../../02-artifacts/execution/amcache-hve/index.md) |
| settings.dat | `%LocalAppData%\Packages\<패키지 이름>\Settings\settings.dat` | [UWP 앱 데이터 구조 (Packages 폴더·settings.dat)](../../app-mail-data/packages-settings-dat.md) |
| Syscache.hve | Windows 7 의 `System Volume Information` 폴더 | 공개 자료는 이름과 위치뿐입니다[4] |
| 새 사용자 틀 NTUSER.DAT | `C:\Users\Default\NTUSER.DAT` | 새 프로필을 만들 때 복사하는 원본입니다 |

> 그림 자리: 왼쪽에 레지스트리 편집기 트리(HKLM·HKU·HKCU·HKCR), 오른쪽에 디스크 폴더(config 폴더·사용자 프로필 폴더)를 그리고, 어느 키가 어느 파일에 붙는지 화살표로 잇는다. HKCU 와 HKCR 은 "연결·합친 화면" 으로 점선 표시한다.

## 하이브마다 들어 있는 아티팩트

어느 하이브를 가져와야 하는지 정할 때 이 표를 씁니다. 키 경로와 해석은 각 페이지에 있습니다.

| 하이브 | 대표 아티팩트 |
|---|---|
| SYSTEM | [컨트롤셋](controlset-select.md), [컴퓨터 이름·마지막 종료 시각](../../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md), [시간대](../../../02-artifacts/system-account/time-zone.md), [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md), [USBSTOR](../../../02-artifacts/external-devices/usb-storage-artifacts/usbstor.md), [MountedDevices](../../../02-artifacts/external-devices/usb-storage-artifacts/mounteddevices.md), [네트워크 인터페이스](../../../02-artifacts/network/tcp-ip-interfaces.md), [ShimCache](../../../02-artifacts/execution/shimcache-appcompatcache.md), [BAM](../../../02-artifacts/execution/background-activity-moderator.md), [블루투스 장치](../../../02-artifacts/external-devices/bthport.md) |
| SOFTWARE | [OS 버전·설치 시각](../../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md), [ProfileList](../../../02-artifacts/system-account/profilelist.md), [설치 프로그램](../../../02-artifacts/system-account/uninstall.md), [컴퓨터 전체 Run](../../../02-artifacts/persistence/run-runonce-startup-folder.md), [Winlogon·IFEO](../../../02-artifacts/persistence/winlogon-ifeo-appinit-dlls.md), [NetworkList](../../../02-artifacts/network/networklist.md), [예약 작업 캐시](../../../02-artifacts/persistence/scheduled-tasks/taskcache-tree-tasks.md), [WPD·EMDMgmt](../../../02-artifacts/external-devices/usb-storage-artifacts/wpd-emdmgmt.md) |
| SAM | [로컬 계정·그룹·로그온 횟수](../../../02-artifacts/system-account/sam.md), [암호화된 NT 해시](../../../02-artifacts/credentials/sam-security/nt-hash.md) |
| SECURITY | [LSA 시크릿](../../../02-artifacts/credentials/sam-security/lsa-secrets.md), [도메인 캐시 자격증명](../../../02-artifacts/credentials/sam-security/mscache-v2.md), [시스템 DPAPI 키](../../protection/data-protection-api/dpapi-system.md), [감사 정책](../../../02-artifacts/event-logs/audit-policy-log-settings.md), 작업그룹·도메인 이름(`Policy\PolPrDmN` 기본값, 현장 관찰) |
| NTUSER.DAT | [UserAssist](../../../02-artifacts/execution/userassist.md), [RecentDocs](../../../02-artifacts/file-folder-usage/recentdocs.md), [RunMRU](../../../02-artifacts/execution/runmru.md), [TypedPaths·WordWheelQuery](../../../02-artifacts/file-folder-usage/typedpaths-wordwheelquery.md), [ComDlg32](../../../02-artifacts/file-folder-usage/comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md), [MountPoints2](../../../02-artifacts/external-devices/usb-storage-artifacts/mountpoints2.md), [사용자 Run](../../../02-artifacts/persistence/run-runonce-startup-folder.md), [오피스 최근 파일](../../../02-artifacts/file-folder-usage/microsoft-office/file-mru-place-mru.md), [TypedURLs](../../../02-artifacts/browsers/ie-edgehtml/typedurls-typedurlstime.md), [원격 데스크톱 접속 기록](../../../02-artifacts/network/rdp-client-mru.md), [FeatureUsage](../../../02-artifacts/execution/featureusage.md) |
| UsrClass.dat | [셸백](../../../02-artifacts/file-folder-usage/shellbags/ntuser-usrclass-bagmru-bags.md) (Vista 이후 주로 여기), [MUICache](../../../02-artifacts/execution/muicache.md) (Vista 이후), 사용자별 파일 연결·COM 등록 |
| DEFAULT | LocalSystem 으로 도는 프로그램의 사용자 설정 (로그온 화면 설정 등) |

SAM 의 해시는 SYSTEM 하이브에서 구한 부트키로 풀리므로 SAM 만 가져오면 해시를 풀지 못합니다. 절차는 [부트키 구하기 (SYSTEM Boot Key)](../../../02-artifacts/credentials/sam-security/system-boot-key.md) 에 있습니다.

## Windows 버전별 차이

| 항목 | XP·2003 | Vista ~ 10 1709 | 10 1803 이후·11 |
|---|---|---|---|
| 사용자 프로필 폴더 | `C:\Documents and Settings\<사용자>` | `C:\Users\<사용자>` | `C:\Users\<사용자>` |
| UsrClass.dat 위치 | `%UserProfile%\Local Settings\Application Data\Microsoft\Windows\` | `%UserProfile%\AppData\Local\Microsoft\Windows\` | 같음 |
| 새 사용자 틀 | `...\Default User\NTUSER.DAT` | `C:\Users\Default\NTUSER.DAT` | 같음 |
| 하이브 옆 로그 파일 | `.LOG` 한 개 | `.LOG1`·`.LOG2` | 같음 |
| config 폴더 안 옛 사본 | `.sav` (설치 도중 만든 사본) | `RegBack` 폴더에 RegIdleBackup 예약 작업이 만든 사본 | `RegBack` 에 크기 0 파일만 남음 (기본값) |
| 그 밖의 옛 사본 | 시스템 복원 지점 | 볼륨 섀도 복사본 | 볼륨 섀도 복사본 |

- Windows 10 1803 부터는 RegBack 백업이 기본으로 꺼져 있어서 파일 이름은 보이지만 크기가 0 입니다.
- `HKLM\System\CurrentControlSet\Control\Session Manager\Configuration Manager\EnablePeriodicBackup` 을 1 로 두면 예전처럼 백업하므로, 분석 대상에서 이 값이 1 이면 RegBack 사본이 있을 수 있습니다.
- 로그 파일의 형식과 쓰는 법은 [트랜잭션 로그와 반영 안 된 변경 (.LOG1·.LOG2)](log1-log2.md) 에서 다룹니다.

## 읽는 법 — 이 파일은 누구의 것인가

1. **실행 중인 시스템**: `HKLM\SYSTEM\CurrentControlSet\Control\hivelist` 를 봅니다. 값 이름이 붙은 자리(`\REGISTRY\USER\<SID>_Classes` 등)이고, 값 데이터가 `\Device\HarddiskVolumeN\...` 형태의 파일 경로입니다. 이 목록은 커널이 실행 중에 채웁니다. 이미지에서 꺼낸 SYSTEM 파일에는 이 키가 없습니다.
2. **디스크 이미지**: config 폴더와 사용자 프로필 폴더를 직접 살펴봅니다. 프로필 폴더와 SID 는 SOFTWARE 하이브의 [ProfileList](../../../02-artifacts/system-account/profilelist.md) 로 짝을 맞춥니다. 폴더 이름만 보고 계정을 단정하지 않습니다.
3. **이름이 바뀌었거나 카빙한 파일**: 첫 4바이트를 봅니다. 아래는 명세로 만든 예시입니다.

   ```
   오프셋    00 01 02 03
   00000000  72 65 67 66    regf
   ```

   `regf` 로 시작하면 하이브 파일입니다. 첫 블록에는 디버깅용으로 원래 파일 경로 일부가 적힙니다. 이 필드로 어느 하이브였는지 짐작할 수 있습니다. 위치는 [하이브 내부 구조](regf-hbin-cell.md) 를 봅니다.

## 포렌식에서 중요한 점

**수집**

- 올라와 있는 하이브는 운영체제가 잠가 두므로 탐색기 복사로는 가져올 수 없고, 원시 NTFS 를 읽는 수집 도구나 섀도 복사본으로 복사합니다. 방법은 [선별 수집 (Triage Collection)](../../../03-techniques/process-acquisition/evidence-acquisition/triage-collection.md) 과 [실행 중 시스템 이미징 (Live Imaging)](../../../03-techniques/process-acquisition/live-response/live-imaging.md) 에 있습니다.
- 하이브를 가져올 때 같은 폴더의 `.LOG1`·`.LOG2` 를 함께 가져옵니다. 최근 변경이 아직 하이브 파일에 쓰이지 않고 로그에만 있을 수 있습니다.
- `config\TxR` 폴더와 사용자 하이브 옆의 `.regtrans-ms` 파일도 함께 가져옵니다. 이 파일들은 `.LOG1`·`.LOG2` 와는 다른 트랜잭션 레지스트리 (TxR) 기록입니다.
- API 로 내보낸 사본(`reg save` 등)은 원본 파일을 바이트 그대로 복사한 것이 아니라서 지운 키가 남은 빈 공간이 사본에는 없을 수 있습니다. 지운 데이터를 볼 계획이면 원본 파일을 그대로 복사합니다.

**옛 사본과 비교**

- 한 PC 에 같은 하이브의 옛 판이 여러 벌 남을 수 있습니다. RegBack 폴더, 볼륨 섀도 복사본, 업그레이드 뒤 남은 `Windows.old` 폴더, XP 의 시스템 복원 지점입니다.
- 지금 하이브와 옛 판을 비교하면 지워지거나 바뀐 키가 드러납니다. 방법은 [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 과 [지워진 키·값 복구 (Deleted Keys·Values)](deleted-keys-values.md) 에 있습니다.
- `Windows.old` 는 윈도를 다시 깔거나 올린 흔적이기도 합니다. [PC 를 초기화하거나 윈도를 다시 깔았나](../../../04-scenarios/activity/anti-forensics/reset-reinstall.md) 를 함께 봅니다.

**하이브 파일 자체의 시각**

- NTUSER.DAT 가 만들어진 시각은 그 계정이 처음 로그온한 때에 가깝고, 계정을 만든 시각은 레지스트리에 직접 적혀 있지 않습니다. 그래서 현장에서는 이 파일의 생성 시각($STANDARD_INFORMATION)을 계정 생성 시각 대신 쓰는 경우가 많습니다. 보고서에는 추정값이라고 밝힙니다 (현장 관찰). NTFS 시각은 [두 벌의 시각](../../disk-volume/ntfs/standard-information-file-name.md) 을 봅니다.
- 하이브 파일의 NTFS 수정 시각은 파일에 마지막으로 쓴 때입니다. 특정 키가 바뀐 때가 아닙니다. 키마다의 시각은 [키 마지막 기록 시각 (Last Write Time)](last-write-time.md) 에서 읽습니다.

## 함정

- **`HKU\.DEFAULT` 는 새 사용자의 기본값이 아닙니다.** LocalSystem 계정의 설정이고, 새 사용자 틀은 `C:\Users\Default\NTUSER.DAT` 입니다.
- **새 프로필은 틀을 복사해 만듭니다.** 그래서 새 사용자의 NTUSER.DAT 안에는 계정보다 먼저 기록된 키 시각이 있을 수 있으며, 이 시각을 사용자 행위로 읽지 않습니다.
- **`HKCU\Software\Classes` 는 NTUSER.DAT 에 없고 UsrClass.dat 에 있습니다.** 사용자 단위 COM 등록을 이용한 자동실행을 찾을 때 NTUSER.DAT 만 보면 놓칩니다. [악성코드 지속성 찾기](../../../04-scenarios/incident/persistence.md) 를 함께 봅니다.
- **실행 중 시스템의 HKU 에는 로그온한 사용자만 보입니다.** 다른 사용자의 설정은 그 사람의 NTUSER.DAT 파일을 따로 열어야 봅니다.
- **서비스 계정 하이브를 빼먹기 쉽습니다.** LocalService·NetworkService 로 도는 프로그램의 사용자 설정은 사람 계정의 NTUSER.DAT 가 아니라 `ServiceProfiles` 아래에 남습니다.
- **관리자 권한으로도 SAM·SECURITY 속은 비어 보입니다.** 실행 중 시스템에서 이 두 하이브의 속은 SYSTEM 계정만 읽도록 권한이 걸려 있으므로, 비어 보인다고 내용이 없는 것은 아닙니다.
- **64비트 Windows 의 SOFTWARE 에는 32비트 프로그램 설정이 `WOW6432Node` 아래에 따로 있습니다.** 같은 파일 안이므로 두 곳을 다 봅니다.
- **RegBack 파일이 있다고 사본이 있는 것이 아닙니다.** 1803 이후 기본값에서는 크기가 0 입니다. 파일 크기를 먼저 확인합니다.

## 도구

아래 도구는 예시입니다. 한 도구에 기대지 말고, 결과가 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 방법으로 비교합니다.

- 하이브 열기: Registry Explorer·RECmd, RegRipper, libregf, yarp 같은 공개 도구가 있습니다.
- 로그 반영: 도구마다 `.LOG1`·`.LOG2` 를 반영하는지, 반영한 결과를 원본과 따로 저장하는지 다릅니다. 쓰기 전에 확인합니다.
- 실행 중 시스템에서 파일 경로 확인: 레지스트리 편집기로 `hivelist` 키를 봅니다.

## 함께 볼 페이지

- [레지스트리 하이브 구조 (Registry Hive)](index.md) — 상위 허브
- [하이브 내부 구조 (regf·hbin·Cell)](regf-hbin-cell.md)
- [키 마지막 기록 시각 (Last Write Time)](last-write-time.md)
- [트랜잭션 로그와 반영 안 된 변경 (.LOG1·.LOG2)](log1-log2.md)
- [지워진 키·값 복구 (Deleted Keys·Values)](deleted-keys-values.md)
- [컨트롤셋 고르기 (ControlSet·Select)](controlset-select.md)
- [MRU 목록 읽는 법 (MRUList·MRUListEx)](mrulist-mrulistex.md)
- [볼륨 섀도 복사본 구조 (Volume Shadow Copy)](../../disk-volume/volume-shadow-copy.md)
- [레지스트리 속 비밀번호 정보 (SAM·SECURITY)](../../../02-artifacts/credentials/sam-security/index.md)
- [그 시각에 PC 를 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)

## 참고 문헌

1. Microsoft Learn, "Registry Hives". https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-hives
2. Microsoft Learn, "HKEY_CLASSES_ROOT Key". https://learn.microsoft.com/en-us/windows/win32/sysinfo/hkey-classes-root-key
3. Microsoft Learn, "The system registry is no longer backed up to the RegBack folder starting in Windows 10 version 1803" (KB4509719). https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/system-registry-no-backed-up-regback-folder
4. libyal, "Windows NT Registry File (REGF) format" (libregf). https://github.com/libyal/libregf/blob/main/documentation/Windows%20NT%20Registry%20File%20(REGF)%20format.asciidoc
5. Mateusz Jurczyk, "The Windows Registry Adventure #4: Hives and the registry layout", Google Project Zero, 2024. https://projectzero.google/2024/10/the-windows-registry-adventure-4-hives.html
6. Harlan Carvey, "Accessing Historical Information During DF Work", Windows Incident Response, 2016. http://windowsir.blogspot.com/2016/05/accessing-historical-information-during.html
