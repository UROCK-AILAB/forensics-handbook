---
title: "설치 프로그램"
parent: "아티팩트 · 시스템·계정"
nav_order: 660
---

# 설치 프로그램 (Uninstall)

레지스트리의 `Uninstall` 키 아래에는 설치한 앱마다 하위 키가 하나씩 있습니다. 하위 키에는 앱 이름, 버전, 제조사, 설치 위치 같은 값이 있습니다. 앱 항목을 마지막으로 손댄 때는 하위 키의 마지막 기록 시각(LastWrite)으로 봅니다. `InstallDate` 값은 처음 설치한 날이 아니라 마지막으로 패치·복구한 날일 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

앱을 설치하면 그 앱의 정보가 `Uninstall` 키 아래 하위 키로 남습니다. 하위 키 이름은 앱의 제품 코드 GUID 이거나 앱 이름입니다.

Windows Installer (MSI) 로 설치한 앱은 설치 패키지의 속성에서 값을 채웁니다. 예를 들어 `DisplayName` 은 ProductName 속성에서, `Publisher` 는 Manufacturer 속성에서 옵니다. MSI 가 아닌 설치 프로그램은 값 구성이 다를 수 있습니다.

이 키로 다음을 봅니다.

- 이 PC 나 이 사용자에게 어떤 앱이 설치돼 있었는지
- 앱의 버전과 제조사
- 앱 항목을 마지막으로 손댄 때

## 위치와 버전별 차이

| 범위 | 하이브 | 하이브 안의 키 경로 |
|---|---|---|
| 컴퓨터 전체 | SOFTWARE | `Microsoft\Windows\CurrentVersion\Uninstall` |
| 64비트 윈도의 32비트 앱 | SOFTWARE | `Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall` |
| 사용자별 설치 | 사용자의 NTUSER.DAT | `Software\Microsoft\Windows\CurrentVersion\Uninstall` |
| 사용자별 설치 (32비트) | 사용자의 NTUSER.DAT | `Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall` |

- 실행 중인 PC 에서 컴퓨터 전체 키는 `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall` 로 보입니다.
- 64비트 윈도에 32비트 앱을 설치하면 `Wow6432Node` 아래로 들어갑니다. 64비트 윈도에서는 두 자리를 모두 봐야 합니다.
- 사용자별 설치는 그 사용자의 NTUSER.DAT 에만 있습니다. 사용자마다 하이브를 따로 엽니다. 사용자별 NTUSER.DAT 는 [사용자 프로필 목록](profilelist.md)에서 찾은 프로필 폴더에서 찾습니다.
- 하이브 파일 위치는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

## 구조

앱 하위 키마다 아래 값이 있을 수 있습니다. 표는 Windows Installer 로 설치한 앱의 값입니다.

| 값 이름 | 뜻 |
|---|---|
| DisplayName | 표시 이름. ProductName 속성에서 옵니다 |
| DisplayVersion | 표시 버전. ProductVersion 속성에서 만듭니다 |
| Publisher | 제조사. Manufacturer 속성에서 옵니다 |
| InstallDate | 이 제품을 마지막으로 서비스(패치·복구)한 때. 그런 일이 없었으면 이 PC 에 처음 설치한 때 |

이 밖에 다음 값도 있을 수 있습니다.

- InstallLocation, InstallSource
- UninstallString, ModifyPath
- EstimatedSize
- HelpLink, URLInfoAbout, Comments, Contact, Readme, Language
- VersionMajor, VersionMinor, Version

설치 위치(InstallLocation)나 설치 원본(InstallSource)이 있으면 파일 흔적과 맞춰 볼 수 있습니다. `InstallDate` 의 저장 형식은 공개 문서에 정해져 있지 않습니다. 도구가 보여 주는 값을 그대로 옮기고, 형식은 실제 데이터로 확인합니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 하이브를 마지막으로 쓴 때 이 키에 그 앱 항목이 있었습니다 | 그 앱을 실행했는지 |
| 사용자별 키라면 그 사용자 범위로 설치한 항목입니다 | 컴퓨터 전체 키라면 누가 설치했는지 |
| 앱 키의 LastWrite 시각에 그 항목을 마지막으로 손댔습니다 | 처음 설치한 시각. LastWrite 는 마지막으로 손댄 때입니다 |
| `InstallDate` 에 적힌 마지막 서비스 때 | 앱 파일이 지금도 디스크에 있는지 |
| | 목록에 없는 앱을 설치한 적이 없다는 것 |

앱을 지우면 항목이 목록에서 빠질 수 있고, 설치 과정 없이 쓰는 프로그램은 처음부터 목록에 없을 수 있습니다. 그래서 "목록에 없다" 는 "설치한 적이 없다" 가 아닙니다.

### 보고서 문장

아래 이름과 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "SOFTWARE 하이브의 Uninstall 키에 `ExampleApp` 항목이 있습니다. 이 항목의 키는 2025-02-20 04:15:30 UTC 에 마지막으로 기록됐습니다."
- 쓰면 안 되는 문장: "사용자가 2025-02-20 에 ExampleApp 을 설치해 사용했습니다."

## 시각 해석

한 앱 항목에서 볼 시각은 두 가지입니다. 뜻이 다릅니다.

| 시각 | 가리키는 때 | 비고 |
|---|---|---|
| `InstallDate` 값 | 마지막으로 서비스(패치·복구)한 때. 그런 일이 없었으면 처음 설치한 때 | 바뀔 수 있는 값입니다 |
| 앱 키의 LastWrite | 그 앱 항목을 마지막으로 손댄 때 | 레지스트리 키마다 있는 FILETIME 이라 UTC 로 해석합니다 |

- 공개 도구(RegRipper 의 `uninstall`)는 앱 키마다 `DisplayName`·`DisplayVersion` 만 읽고 `InstallDate` 는 읽지 않으며, 대신 앱 키의 LastWrite 를 뽑아 최신순으로 늘어놓습니다. 이렇게 "언제 설치하거나 바꿨나" 를 봅니다.
- 두 시각은 뜻이 달라서 서로 다를 수 있으며, 다르다고 조작의 흔적은 아닙니다.
- LastWrite 가 무엇이고 어디 있는지는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다. FILETIME 계산은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다.
- 현지 시각으로 바꿀 때는 [시간대 설정](time-zone.md)을 씁니다.

## 함정과 한계

1. **한 자리만 봅니다.** 64비트 윈도의 `Wow6432Node` 와 사용자별 NTUSER.DAT 를 빼먹으면 앱을 놓칩니다. 네 자리를 모두 봅니다.
2. **`InstallDate` 를 처음 설치한 날로 씁니다.** 패치나 복구를 했다면 그 뒤 날짜입니다.
3. **LastWrite 를 설치한 날로 씁니다.** LastWrite 는 항목을 마지막으로 손댄 때입니다. 처음 설치한 날보다 뒤일 수 있습니다.
4. **설치를 실행으로 씁니다.** 설치 기록은 실행 기록이 아닙니다. 실행은 [프리페치](../execution/prefetch/index.md) 같은 실행 흔적으로 따로 확인합니다.
5. **MSI 표대로 값을 기대합니다.** MSI 가 아닌 설치 프로그램은 값 구성이 다를 수 있습니다. 값이 빠졌다고 이상한 항목은 아닙니다.
6. **도구가 읽지 않은 값을 놓칩니다.** 공개 도구 출력에 `InstallDate`·`InstallLocation` 이 없다면 레지스트리 뷰어로 키를 직접 엽니다.

### 지우기와 조작

- **앱을 지웁니다.** 항목이 목록에서 빠질 수 있습니다. 옛 항목은 [섀도 복사본](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 속 하이브나 하이브 안의 빈 공간에서 찾습니다. 설치·삭제 기록은 [프로그램 설치·삭제 이벤트](../event-logs/msiinstaller.md)에서 찾습니다.
- **항목만 지웁니다.** 앱 파일은 남고 목록에서만 빠질 수 있습니다. [AmCache](../execution/amcache-hve/index.md)와 파일 흔적으로 확인합니다.
- **값을 고칩니다.** `DisplayName`·`Publisher` 는 레지스트리 값이라 고칠 수 있습니다. 설치 위치의 실행 파일 정보([실행 파일 메타데이터](../embedded-metadata/pe-header-version-info-digital-signature.md))와 맞춰 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 FILETIME 형식을 보고 만든 예시입니다. 실제 데이터에서 뽑은 값이 아닙니다. 앱 하위 키의 LastWrite 필드가 다음 8바이트라고 합니다. 키 레코드 안에서 이 필드를 찾는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

```
LastWrite (8바이트)  00 1D C6 13 4E 83 DB 01
```

1. 8바이트를 리틀 엔디언으로 읽으면 0x01DB834E13C61D00 입니다.
2. 이 수는 10진으로 133,844,985,300,000,000 입니다. 1601-01-01 00:00:00 UTC 부터 센 100나노초 단위 값입니다.
3. 날짜로 바꾸면 2025-02-20 04:15:30 UTC 입니다.
4. 한국 시각(UTC+9)으로는 같은 날 13:15:30 입니다.
5. 같은 키의 `InstallDate` 값과 비교합니다. 두 시각이 다르면, 어느 쪽이 처음 설치이고 어느 쪽이 마지막 손댄 때인지 뜻에 맞춰 적습니다.

> 그림 자리: Uninstall 아래 앱 하위 키 하나를 펼쳐, 값 목록(DisplayName·DisplayVersion·Publisher·InstallDate)과 키의 LastWrite 가 서로 다른 곳에 있다는 것을 보여 주는 그림

### 공개 도구로 한 번

RegRipper 의 `uninstall` 플러그인은 앱 키를 LastWrite 최신순으로 늘어놓고 이름과 버전을 보여 줍니다. 도구를 쓸 때는 다음을 확인합니다.

- `Wow6432Node` 와 사용자별 NTUSER.DAT 도 읽었는지 확인합니다.
- LastWrite 를 UTC 로 보여 주는지 확인합니다.
- 도구가 읽지 않는 값은 레지스트리 뷰어로 직접 봅니다.
- 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [프로그램 설치·삭제 이벤트](../event-logs/msiinstaller.md) | 설치·삭제 시각. 지금 목록에 없는 앱의 설치 이력 |
| [AmCache](../execution/amcache-hve/index.md) | 같은 앱의 실행 파일 정보와 해시 |
| [프리페치](../execution/prefetch/index.md) | 설치한 앱을 실제로 실행했는지 |
| [마스터 파일 테이블](../filesystem/mft.md) | 설치 위치 폴더와 파일의 생성 시각. LastWrite 무렵에 생긴 파일 |
| [윈도 업데이트 기록](windows-update-cbs-log.md) | 윈도 구성 요소의 설치·갱신 이력 |
| [스토어 앱 설치 목록](appx-staterepository.md) | 스토어 앱의 설치 기록 |

설치 기록과 실행 기록을 함께 읽는 흐름은 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md)에서 다룹니다. 원격 제어 프로그램 설치를 찾는 흐름은 [원격 제어 프로그램으로 누가 조작했나](../../04-scenarios/incident/remote-access-tool-abuse.md)에서 다룹니다.

## 실습

**NIST CFReDS 같은 공개 시험 이미지**에서 SOFTWARE 하이브와 사용자별 NTUSER.DAT 를 꺼내 풀어 봅니다.

1. 네 자리의 `Uninstall` 키에서 앱 항목은 각각 몇 개입니까?
2. LastWrite 최신순으로 앱을 늘어놓아 보십시오. 가장 최근에 손댄 앱은 무엇입니까?
3. 한 앱의 `InstallDate` 값과 LastWrite 를 비교해 보십시오. 두 시각은 같습니까?
4. 목록의 앱 가운데 실행 흔적이 있는 앱과 없는 앱을 나눠 보십시오.
5. 이벤트 로그에 설치 기록이 있는데 지금 목록에 없는 앱이 있습니까?

**직접 만든 가상 머신**에서도 해 봅니다.

1. MSI 앱 하나와 MSI 가 아닌 앱 하나를 설치합니다. 설치한 시각을 적어 둡니다.
2. 두 앱의 하위 키 값 구성을 비교합니다.
3. MSI 앱을 복구 설치한 뒤 `InstallDate` 와 LastWrite 가 어떻게 바뀌는지 봅니다.
4. 앱을 지운 뒤 하위 키가 남는지 확인합니다.

## 참고 문헌

- Microsoft Learn, "Windows Installer Properties for the Uninstall Registry Key" — https://learn.microsoft.com/en-us/windows/win32/msi/uninstall-registry-key
- keydet89, RegRipper3.0 `uninstall.pl` (Uninstall·Wow6432Node·NTUSER 경로, LastWrite 정렬) — https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/uninstall.pl
