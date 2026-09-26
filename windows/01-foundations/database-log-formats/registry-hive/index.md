---
title: "레지스트리 하이브 구조"
parent: "기반 · 데이터베이스·로그 형식"
nav_order: 130
has_children: true
has_toc: false
---

# 레지스트리 하이브 구조 (Registry Hive)

레지스트리는 디스크에 하이브 (Hive) 라는 파일 여러 개로 나뉘어 저장됩니다. 분석은 이 하이브 파일과 옆에 있는 트랜잭션 로그 (Transaction Log) 를 함께 읽는 데서 시작합니다.

## 왜 중요한가

- 윈도 아티팩트의 상당수가 하이브 안에 있습니다. USB 연결, 프로그램 실행, 폴더 탐색, 계정, 시간대 설정이 모두 키 (Key) 와 값 (Value) 으로 남습니다.
- 압수 이미지에는 레지스트리 편집기가 보여 주는 트리가 없어서 분석가가 하이브 파일을 직접 열기 때문에, 라이브 화면의 어느 루트 키가 어느 파일에서 오는지 알아야 합니다.
  - HKEY_CLASSES_ROOT 는 따로 된 파일이 없습니다. `HKLM\Software\Classes` 와 `HKCU\Software\Classes` 를 합쳐 보여 주는 화면입니다.
  - HKEY_CURRENT_USER 는 지금 로그온한 사용자의 하이브를 가리킵니다.
  - 라이브 시스템의 HKEY_USERS 에는 지금 불러온 사용자 하이브만 있습니다. 이미지에서는 로그온하지 않은 사용자의 NTUSER.DAT 까지 읽을 수 있습니다.
  - 라이브에서 보이는 `CurrentControlSet` 은 부팅할 때 만들어지는 연결입니다. SYSTEM 하이브 파일에는 `ControlSet001` 처럼 번호가 붙은 키만 있습니다.
- 키마다 UTC 기준 FILETIME 인 마지막 기록 시각 (Last Write Time) 이 하나 있습니다. 값에는 따로 시각이 없어서 값이 언제 바뀌었는지는 그 값이 든 키의 시각으로만 짐작할 수 있습니다.
- 주 파일 (primary file) 만으로는 최신 상태가 아닐 수 있습니다. Windows 8.1 부터 쓰이는 새 로그 형식에서는 바뀐 내용이 로그에 먼저 쓰이고 주 파일 쓰기는 최대 한 시간까지 미뤄질 수 있습니다. 하이브를 수집할 때 `.LOG1`·`.LOG2` 를 꼭 함께 가져와야 하는 이유입니다.
- 지운 키와 값은 바로 사라지지 않고, 그 자리의 셀 (Cell) 이 빈 셀로 표시될 뿐이라서 내용은 다른 데이터로 덮이기 전까지 남습니다. 옆의 빈 셀과 합쳐지면 빈 셀 하나에 옛 레코드가 여러 개 들어가는데, 셀 첫머리만 보는 도구는 두 번째 레코드부터 놓칩니다.
- 값을 해석하는 방식에 따라 숫자가 달라집니다. REG_DWORD 값을 부호 없는 10진수로만 보여 주는 도구가 많습니다. 시간대의 Bias 처럼 부호에 뜻이 있는 값은 원시 바이트로 다시 확인합니다. 예를 들어 UTC+9 의 Bias 는 -540 입니다. 이를 부호 없이 읽으면 4294966756 이 됩니다. 자세한 내용은 [시간대 설정](../../../02-artifacts/system-account/time-zone.md) 에 있습니다.

## 한눈에 보기

> 그림 자리: 레지스트리 편집기의 루트 키(HKLM·HKU·HKCU·HKCR)와 디스크의 하이브 파일(SYSTEM·SOFTWARE·SAM·SECURITY·NTUSER.DAT·UsrClass.dat)이 어떻게 이어지는지 선으로 잇는 그림

### 하이브 파일과 알려 주는 것

위치는 Windows Vista 이후 기준입니다. 버전별 경로는 [하이브 파일 종류와 위치](system-software-sam-security-ntuser-dat-usrclass.md) 에 정리합니다.

| 하이브 파일 | 위치 | 라이브에서 보이는 자리 | 알려 주는 것 (예) |
|---|---|---|---|
| SYSTEM | `%SystemRoot%\System32\config\SYSTEM` | `HKLM\SYSTEM` (HKEY_CURRENT_CONFIG 도 여기서 옴) | [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md), [USB 저장장치](../../../02-artifacts/external-devices/usb-storage-artifacts/index.md), [시간대](../../../02-artifacts/system-account/time-zone.md), [심캐시](../../../02-artifacts/execution/shimcache-appcompatcache.md), [BAM](../../../02-artifacts/execution/background-activity-moderator.md), [네트워크 인터페이스](../../../02-artifacts/network/tcp-ip-interfaces.md) |
| SOFTWARE | `%SystemRoot%\System32\config\SOFTWARE` | `HKLM\SOFTWARE` | [시스템 기본 정보](../../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md), [설치 프로그램](../../../02-artifacts/system-account/uninstall.md), [프로필 목록](../../../02-artifacts/system-account/profilelist.md), [네트워크 목록](../../../02-artifacts/network/networklist.md), [예약 작업 캐시](../../../02-artifacts/persistence/scheduled-tasks/taskcache-tree-tasks.md) |
| SAM | `%SystemRoot%\System32\config\SAM` | `HKLM\SAM` | [로컬 계정](../../../02-artifacts/system-account/sam.md), [NT 해시](../../../02-artifacts/credentials/sam-security/nt-hash.md) |
| SECURITY | `%SystemRoot%\System32\config\SECURITY` | `HKLM\SECURITY` | [LSA 시크릿](../../../02-artifacts/credentials/sam-security/lsa-secrets.md), [도메인 캐시 자격증명](../../../02-artifacts/credentials/sam-security/mscache-v2.md), [감사 정책](../../../02-artifacts/event-logs/audit-policy-log-settings.md), 작업그룹·도메인 이름 |
| NTUSER.DAT | `%USERPROFILE%\NTUSER.DAT` | `HKU\<SID>`, 로그온한 사용자는 HKEY_CURRENT_USER | [UserAssist](../../../02-artifacts/execution/userassist.md), [최근 문서](../../../02-artifacts/file-folder-usage/recentdocs.md), [실행 창 명령](../../../02-artifacts/execution/runmru.md), [탐색기 입력](../../../02-artifacts/file-folder-usage/typedpaths-wordwheelquery.md), [열기·저장 대화상자](../../../02-artifacts/file-folder-usage/comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md), [MountPoints2](../../../02-artifacts/external-devices/usb-storage-artifacts/mountpoints2.md), [로그온 자동실행](../../../02-artifacts/persistence/run-runonce-startup-folder.md) |
| UsrClass.dat | `%USERPROFILE%\AppData\Local\Microsoft\Windows\UsrClass.dat` | `HKU\<SID>_Classes`, `HKCU\Software\Classes` | [셸백](../../../02-artifacts/file-folder-usage/shellbags/index.md), [MUICache](../../../02-artifacts/execution/muicache.md) |
| Amcache.hve | `%SystemRoot%\AppCompat\Programs\Amcache.hve` | 레지스트리 편집기에 보이지 않음 | [실행 파일·설치 프로그램 목록](../../../02-artifacts/execution/amcache-hve/index.md) (생기는 버전은 그 페이지 참고) |

`config` 폴더에는 이 밖에도 DEFAULT·COMPONENTS 같은 하이브가 있습니다. 하이브마다 이름 뒤에 `.LOG1`·`.LOG2` 같은 로그 파일이 붙어 있습니다.

### Windows 버전에 따라 달라지는 점

| Windows 버전 | 달라진 점 |
|---|---|
| XP | 새 형식 (latest format) 을 지원하기 시작합니다. HKEY_CURRENT_USER·SAM·SECURITY·`HKU\.DEFAULT` 하이브는 계속 옛 형식 (standard format) 을 씁니다. |
| Vista | 트랜잭션 로그 두 개(`.LOG1`·`.LOG2`)를 쓰는 방식이 들어옵니다. 그 전에는 `.LOG` 하나를 씁니다. |
| 8.1 · Server 2012 R2 | 새 로그 형식이 들어옵니다. 로그 항목마다 `HvLE` 서명이 붙습니다. 바뀐 내용을 로그에 먼저 쓰고 주 파일 쓰기를 미룹니다. |
| 10 (1803) | `config\RegBack` 폴더로 하던 자동 백업을 멈춥니다. 폴더 안의 하이브 파일은 남지만 크기가 0 입니다. |

## 읽는 순서

1. [하이브 파일 종류와 위치](system-software-sam-security-ntuser-dat-usrclass.md) — 하이브 파일마다 어느 루트 키로 올라가는지 정리합니다. 사용자 하이브와 옛 사본을 어디서 찾는지도 다룹니다.
2. [하이브 내부 구조 (regf·hbin·Cell)](regf-hbin-cell.md) — 파일 헤더, 4096바이트 단위 블록, 그 안의 셀을 헥스로 따라갑니다. 셀 크기가 음수면 쓰는 셀이고, 양수면 빈 셀입니다.
3. [키 마지막 기록 시각 (Last Write Time)](last-write-time.md) — 키마다 하나뿐인 시각이 무엇이 바뀔 때 바뀌는지 다룹니다. 이 시각이 증명하는 것과 증명하지 못하는 것도 나눕니다.
4. [트랜잭션 로그와 반영 안 된 변경 (.LOG1·.LOG2)](log1-log2.md) — 주 파일에 아직 안 들어간 변경을 로그에서 되살리는 법을 다룹니다. 헤더의 두 순번이 다르면 반영 안 된 변경이 있다는 뜻입니다.
5. [지워진 키·값 복구 (Deleted Keys·Values)](deleted-keys-values.md) — 빈 셀, 로그, 섀도 복사본에서 지운 키와 값을 찾는 법과 그 한계를 다룹니다.
6. [컨트롤셋 고르기 (ControlSet·Select)](controlset-select.md) — 오프라인 SYSTEM 하이브에서 `Select` 키로 실제 쓰인 `ControlSet00X` 를 고르는 법을 다룹니다.
7. [MRU 목록 읽는 법 (MRUList·MRUListEx)](mrulist-mrulistex.md) — 목록 값에 적힌 순서로 최근 항목을 읽는 법을 다룹니다. 항목마다 시각이 없으므로 키 시각과 어떻게 짝짓는지도 설명합니다.

## 함께 볼 페이지

- [시각 값 형식 (FILETIME·Unix·WebKit·DOS·OLE)](../../value-decoding/filetime-unix-webkit-dos-ole.md) — 키 시각을 사람이 읽는 시각으로 바꿉니다.
- [윈도 식별자 형식 (SID·GUID·CLSID·Known Folder ID)](../../value-decoding/sid-guid-clsid-known-folder-id.md) — `HKU\<SID>` 의 SID 를 읽습니다.
- [사용자 프로필 목록 (ProfileList)](../../../02-artifacts/system-account/profilelist.md) — SID 와 NTUSER.DAT 경로를 잇습니다.
- [문자 인코딩 (UTF-16LE·UTF-8·CP949)](../../value-decoding/utf-16le-utf-8-cp949.md) — 키 이름과 문자열 값의 인코딩을 다룹니다.
- [선별 수집 (Triage Collection)](../../../03-techniques/process-acquisition/evidence-acquisition/triage-collection.md) — 하이브를 로그 파일과 함께 수집하는 법을 다룹니다.
- [섀도 복사본 활용 (Volume Shadow Copy Analysis)](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 옛 시점의 하이브를 꺼내 지금과 비교합니다.
- [레지스트리 변경 (Sysmon 이벤트 12·13·14)](../../../02-artifacts/event-logs/sysmon/12-13-14.md) — 하이브 밖에 남은 변경 기록입니다.
- [SRUM 해석 함정 (1시간 단위 기록·레지스트리 임시 저장)](../../../02-artifacts/execution/system-resource-usage-monitor/1.md) — 레지스트리에 잠시 머무는 데이터의 예입니다.

## 참고 문헌

- Microsoft Learn, "Registry Hives" — https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry-hives
- Microsoft Learn, "Windows registry for advanced users" — https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/windows-registry-advanced-users
- Microsoft Learn, "The system registry is no longer backed up to the RegBack folder starting in Windows 10 version 1803" — https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/system-registry-no-backed-up-regback-folder
- Maxim Suhanov, "Windows registry file format specification" — https://github.com/msuhanov/regf/blob/master/Windows%20registry%20file%20format%20specification.md
- Maxim Suhanov, "Exploring intermediate states of a registry hive using transaction log files" — https://dfir.ru/2018/11/19/exploring-intermediate-states-of-a-registry-hive-using-transaction-log-files/
- Mandiant, "Digging Up the Past: Windows Registry Forensics Revisited" — https://cloud.google.com/blog/topics/threat-intelligence/digging-up-the-past-windows-registry-forensics-revisited/
