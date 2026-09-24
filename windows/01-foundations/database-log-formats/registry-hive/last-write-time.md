# 키 마지막 기록 시각 (Last Write Time)

## 한 줄 요약

레지스트리 키마다 마지막으로 바뀐 때가 하나씩 적혀 있습니다. 이 시각은 UTC 기준 FILETIME 값입니다. 값(value)에는 시각 칸이 없습니다. 키를 만든 시각도 따로 남지 않습니다.

## 이 시각을 쓰는 아티팩트

레지스트리에 기록되는 아티팩트는 거의 모두 이 시각을 씁니다. 값 안에 시각을 따로 담지 않는 키에서는 이 시각이 유일한 시간 단서입니다.

| 아티팩트 | 키 시각이 가리키는 것 | 자세한 내용 |
|---|---|---|
| MRU 목록 (RunMRU·RecentDocs·TypedPaths 등) | 목록이 마지막으로 바뀐 때. 보통 가장 최근 항목이 들어오거나 순서가 바뀐 때입니다 | [MRU 목록 읽는 법](mrulist-mrulistex.md), [실행 창 명령 기록](../../../02-artifacts/execution/runmru.md), [최근 문서](../../../02-artifacts/file-folder-usage/recentdocs.md), [탐색기 입력 기록](../../../02-artifacts/file-folder-usage/typedpaths-wordwheelquery.md) |
| 셸백 | 폴더 항목 키가 마지막으로 바뀐 때 | [셸백 시각 해석](../../../02-artifacts/file-folder-usage/shellbags/timestamps.md) |
| 자동실행·서비스 | 항목이 추가·변경·삭제된 때 | [로그온 자동실행](../../../02-artifacts/persistence/run-runonce-startup-folder.md), [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md) |

값 데이터 안에 자기 시각을 따로 담는 아티팩트도 있습니다. [UserAssist](../../../02-artifacts/execution/userassist.md), [TypedURLsTime](../../../02-artifacts/browsers/ie-edgehtml/typedurls-typedurlstime.md), [USB 장치 속성의 연결 시각](../../../02-artifacts/external-devices/usb-storage-artifacts/deviceclasses-device-properties-0064-0066-0067.md)이 그 예입니다. 이런 경우에는 값 안의 시각이 키 시각보다 구체적입니다.

## 구조

키는 하이브 안에서 키 노드 (Key Node, 서명 `nk`) 셀 하나로 저장됩니다. 셀과 오프셋 계산은 [하이브 내부 구조](regf-hbin-cell.md)에서 다룹니다. 여기서는 시각과 관련된 칸만 봅니다.

| 위치 | 오프셋 | 크기 | 칸 | 뜻 |
|---|---|---|---|---|
| 키 노드 | 4 | 8 | 마지막 기록 시각 (Last written timestamp) | FILETIME, UTC |
| 키 노드 | 12 | 4 | 접근 비트 (Access bits) | Win8 부터 사용합니다. 그 전에는 쓰지 않는 예약 칸입니다. 시각이 아닙니다 |
| 값 (`vk`) | — | — | 없음 | 값에는 시각 칸이 없습니다 |
| 기본 블록 (Base Block) | 12 | 8 | 하이브의 마지막 기록 시각 | FILETIME, UTC. Win8.1 부터는 갱신되지 않습니다 |
| 기본 블록 | 168 | 8 | 마지막 재구성 시각 (Last reorganized timestamp) | Win8 부터 있습니다. 아래 두 비트는 플래그입니다 |
| 첫 hbin 헤더 | 20 | 8 | 기본 블록 시각의 사본 | 첫 hbin 에만 있습니다 |

키 노드의 오프셋은 `nk` 서명의 첫 바이트를 0 으로 센 값입니다. 셀 맨 앞에는 4바이트 크기 칸이 있습니다. 그래서 셀 시작에서 세면 마지막 기록 시각은 8바이트 뒤에 있습니다. Windows 10 1607(Redstone 1)부터 접근 비트 칸은 앞 1바이트만 접근 비트로 쓰고, 나머지는 다른 용도로 나뉘었습니다.

### Windows 버전별 차이

| 항목 | XP·Vista·7 | 8 | 8.1 이후 (10·11 포함) |
|---|---|---|---|
| 키 노드의 마지막 기록 시각 | 있음 | 있음 | 있음 |
| 키 노드의 접근 비트 | 없음 (예약 칸) | 있음 | 있음 |
| 기본 블록의 마지막 기록 시각 | 쓰기 때마다 갱신 | 쓰기 때마다 갱신 | 갱신 안 됨 (하이브를 만들 때만 적힘) |
| 기본 블록의 마지막 재구성 시각 | 없음 | 있음 | 있음 |
| 바뀐 내용이 하이브 파일에 닿는 때 | 플러시할 때 하이브 파일에 씁니다 | 같음 | 트랜잭션 로그에 먼저 씁니다. 하이브 파일 쓰기는 최대 1시간까지 미뤄질 수 있습니다 |

## 무엇이 이 시각을 바꾸나

Microsoft 문서는 이 시각을 "이 키나 이 키의 값이 마지막으로 바뀐 때" 로 정의합니다. 무엇이 바뀌었는지는 기록하지 않습니다.

| 동작 | 이 키의 시각 | 부모 키의 시각 |
|---|---|---|
| 값을 추가·변경·삭제 | 바뀝니다 | 바뀌지 않습니다 |
| 하위 키를 만들거나 지움 | 새 하위 키에는 만든 시각이 적힙니다 | 바뀝니다 |
| 키 권한(보안 설명자, Security Descriptor)을 바꿈 | 이 글의 참고 문헌에는 설명이 없습니다. 검증 PC 에서 직접 시험해 확인합니다 | 이 글의 참고 문헌에는 설명이 없습니다 |
| 하위 키 안의 값을 바꿈 | 하위 키의 시각만 바뀝니다 | 바뀌지 않습니다 |
| 키를 열거나 값을 읽음 | 바뀌지 않습니다 (Win8 부터 접근 비트만 켜집니다) | 바뀌지 않습니다 |
| `NtSetInformationKey` 에 `KeyWriteTimeInformation` 을 넘김 | 넘긴 값으로 바뀝니다 | 바뀌지 않습니다 |

> 그림 자리: 부모 키·하위 키·값 세 층을 그리고, 값 변경·하위 키 생성·하위 키의 값 변경이 각각 어느 키의 시각을 바꾸는지 화살표로 보여 줍니다.

하위 키의 변경은 부모 키로 올라가지 않습니다. 그래서 부모 키의 시각이 하위 키보다 오래된 일은 흔합니다. Harlan Carvey 는 하이브 하나를 훑어 이런 키가 아주 많다고 보고했습니다(2022).

## 읽는 법

### 헥스로 한 번

아래는 형식 명세를 보고 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

```
셀 시작 기준
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00      A0 FF FF FF 6E 6B 20 00 00 E4 97 34 A2 76 DA 01
10      02 00 00 00 ...
```

1. `A0 FF FF FF` 는 셀 크기 칸입니다. 부호 있는 정수로 -96 입니다. 음수는 사용 중인 셀이라는 뜻입니다.
2. `6E 6B` 는 `nk` 서명입니다.
3. `20 00` 은 플래그 0x0020 입니다. 키 이름이 ASCII 로 저장됐다는 뜻입니다.
4. `00 E4 97 34 A2 76 DA 01` 이 마지막 기록 시각입니다. 리틀 엔디언으로 읽으면 0x01DA76A23497E400 입니다.
5. 이 수는 10진으로 133,549,578,000,000,000 입니다. 1601-01-01 00:00:00 UTC 부터 100나노초 단위로 센 값입니다.
6. 초로 바꾸면 13,354,957,800초입니다. 날짜로는 2024-03-15 06:30:00 UTC 입니다. 한국 시각(UTC+9)으로는 같은 날 15:30:00 입니다.
7. `02 00 00 00` 은 접근 비트입니다. 0x2 가 켜져 있습니다.

FILETIME 계산은 [시각 값 형식](../../value-decoding/filetime-unix-webkit-dos-ole.md)에서 자세히 다룹니다.

### 공개 도구로 한 번

하이브를 읽는 공개 파서는 대부분 키마다 이 시각을 보여 줍니다. yarp, python-registry, libregf 같은 라이브러리와 RegRipper, Registry Explorer·RECmd 같은 도구가 그 예입니다. 도구를 쓸 때는 세 가지를 확인합니다.

- 시각을 UTC 로 보여 주는지, 분석 PC 의 현지 시각으로 바꿔 보여 주는지 확인합니다.
- 트랜잭션 로그를 반영하고 읽었는지 확인합니다. 반영 여부에 따라 시각이 달라질 수 있습니다.
- 헥스로 읽은 값과 한두 키를 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 포렌식에서 중요한 점

### 증명하는 것 / 증명하지 못하는 것

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 그 시각에 이 키에 무언가 바뀐 일이 있었습니다 (조작이 없다면) | 무엇이 바뀌었는지. 어느 값이 바뀌었는지 |
| 그 시각에 이 키가 있었습니다 | 키를 만든 시각 |
| 그 뒤로는 이 키에 변경이 없었습니다 (이 사본 기준) | 그 전에 있었던 변경들 |
| | 누가 바꿨는지. 사용자가 손으로 바꾼 것인지 |
| | 키를 열어 보거나 값을 읽었는지 |

보고서에는 기록이 말하는 만큼만 씁니다.

- 쓸 수 있는 문장: "NTUSER.DAT 의 RunMRU 키는 2024-03-15 06:30:00 UTC 에 마지막으로 바뀐 기록이 있습니다."
- 쓰면 안 되는 문장: "사용자가 2024-03-15 06:30:00 UTC 에 이 명령을 실행했습니다."

### 트랜잭션 로그에 남은 더 새 시각

Win8.1 부터는 바뀐 내용이 트랜잭션 로그에 먼저 기록됩니다. 하이브 파일에 반영되는 것은 최대 1시간까지 늦어질 수 있습니다. 전원이 갑자기 꺼지거나 실행 중에 하이브를 복사하면, 가장 새 시각이 로그에만 있을 수 있습니다. 로그를 반영하는 방법은 [트랜잭션 로그와 반영 안 된 변경](log1-log2.md)에서 다룹니다. 보고서에는 로그를 반영했는지 함께 적습니다.

### 지운 키와 옛 사본

지운 키의 셀이 비할당 영역에 남아 있으면, 그 셀에도 마지막 기록 시각이 남아 있습니다. 이 시각은 지우기 전 마지막 변경 시각입니다. 지운 시각이 아닙니다. 하위 키를 지우면 부모 키의 시각이 바뀝니다. 그래서 부모 키의 시각이 삭제 시각의 단서가 될 수 있습니다. 복구 방법은 [지워진 키·값 복구](deleted-keys-values.md)를 봅니다.

키 시각은 마지막 한 번만 남습니다. 그 전 시각은 옛 사본에서 찾습니다. 섀도 복사본 안의 하이브가 대표적입니다([섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)). `System32\config\RegBack` 폴더도 옛 사본 자리입니다. 다만 Windows 10 1803 부터는 기본으로 백업하지 않습니다. 이때 RegBack 의 하이브 파일은 0바이트입니다.

### 읽기 흔적: 접근 비트 (Win8 이후)

키 시각은 읽기로는 바뀌지 않습니다. 대신 Win8 부터 키를 열거나 만들 때 접근 비트가 켜집니다.

| 비트 | 뜻 |
|---|---|
| 0x1 | 부팅 중 레지스트리 초기화(`NtInitializeRegistry`) 전에 열렸습니다 |
| 0x2 | 레지스트리 초기화 뒤에 열렸습니다 |
| 0 | 접근 기록이 비어 있습니다 |

형식 명세에 따르면 하이브 재구성 (Reorganization) 은 하이브가 잠겨 있지 않을 때 일주일에 한 번 일어납니다. 재구성은 하이브 조각 모음을 하거나 접근 기록을 지웁니다. 조각 모음을 해도 접근 기록은 함께 지워집니다. 마지막 재구성 시각의 가장 아래 비트(1)가 켜져 있으면 조각 모음을 한 것입니다. 그다음 비트(2)가 켜져 있으면 접근 기록을 지운 것입니다. 접근 비트가 켜져 있으면, 마지막 접근 기록 정리 뒤에 이 키가 열린 적이 있다는 뜻입니다. 언제 열렸는지는 알 수 없습니다.

## 시각 해석

- 값은 UTC 입니다. 현지 시각으로 바꿀 때는 그 PC 의 시간대 설정을 씁니다([시간대 설정](../../../02-artifacts/system-account/time-zone.md), [시간대·시계 오차 보정](../../../03-techniques/analysis/timeline/time-normalization.md)).
- 시각은 변경이 일어날 때의 시스템 시계에서 옵니다. 누군가 시스템 시각을 바꿔 두었다면 키 시각도 그 틀린 시계를 따릅니다([시스템 시각을 바꿨나](../../../04-scenarios/activity/anti-forensics/system-time-change.md)).
- 단위는 100나노초입니다.
- 한 번도 바뀌지 않은 키에는 만든 시각이 그대로 남습니다. 하지만 이 값만 보고 만든 시각인지, 나중에 바뀐 시각인지 구분할 수는 없습니다.

## 함정

1. **기본 블록 시각과 혼동합니다.** Win8.1 부터 기본 블록의 마지막 기록 시각은 갱신되지 않습니다. 이 값을 하이브가 마지막으로 바뀐 때로 읽으면 안 됩니다.
2. **하이브 파일의 NTFS 시각과 혼동합니다.** 하이브 파일의 수정 시각은 파일이 디스크에 쓰인 때입니다. 키가 바뀐 때와 다릅니다. Win8.1 부터는 파일 쓰기가 늦어지므로 차이가 더 커질 수 있습니다([두 벌의 시각](../../disk-volume/ntfs/standard-information-file-name.md)).
3. **부모 키가 하위 키보다 오래됐다고 조작으로 봅니다.** 하위 키 안의 변경은 부모로 올라가지 않으므로 이 차이는 흔합니다.
4. **사용자 하이브의 시각을 사용자 행동으로 단정합니다.** NTUSER.DAT 의 키라도 그 사용자 권한으로 돌던 프로그램이면 어느 것이든 바꿀 수 있습니다.
5. **여러 키의 시각이 같으면 한 행동으로 봅니다.** 설치 프로그램이나 시스템 작업이 많은 키를 한꺼번에 다시 쓰면 여러 키의 시각이 비슷해집니다.
6. **분석 중에 원본을 바꿉니다.** 분석 PC 에 하이브를 불러와(`reg load`) 키를 고치면 그 키의 시각은 분석한 때로 바뀝니다. 불러오는 과정에서 로그가 반영되며 파일이 바뀔 수도 있습니다. 항상 사본에서 작업합니다.

## 조작과 흔적

`NtSetInformationKey` 에 `KeyWriteTimeInformation` 을 넘기면 키의 마지막 기록 시각을 원하는 값으로 바꿀 수 있습니다. 그 키를 고칠 수 있는 권한이면 됩니다. 값은 그대로 두고 시각만 바꿀 수 있습니다. 공개 도구로도 나와 있습니다(Carvey, 2022). 조작 흔적은 다음처럼 찾습니다.

- **다른 기록과 순서를 비교합니다.** Sysmon 이벤트 13(값 설정)처럼 변경 시각을 따로 남기는 기록보다 키 시각이 앞서면 이상합니다([Sysmon 레지스트리 변경](../../../02-artifacts/event-logs/sysmon/12-13-14.md)).
- **값 안의 시각과 비교합니다.** 값 데이터에 담긴 시각보다 키 시각이 앞서면 이상합니다.
- **옛 사본과 비교합니다.** 트랜잭션 로그·섀도 복사본·RegBack 의 같은 키 시각이 더 새것이면 이상합니다.
- **말이 안 되는 시각을 찾습니다.** OS 설치 시각보다 앞선 시각이나 수집 시각보다 뒤의 시각이 그 예입니다([시스템 기본 정보](../../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md)).
- **4바이트 한쪽이 모두 0 인 시각을 찾습니다.** Carvey(2022)는 공개 조작 도구의 예시 시각을 넣으면 8바이트 시각을 4바이트씩 나눈 두 칸 가운데 하나가 모두 0 이 된다고 적었습니다. 그래서 하이브 전체에서 이런 시각을 자동으로 찾아보자고 제안했습니다. 조작 여부를 가르는 기준이 아니라 더 볼 키를 고르는 단서로만 씁니다.

하위 키가 없는 키는 부모와 비교할 거리도 없습니다. 이런 키는 위의 다른 기록에 기대야 합니다. 시각 조작 전반은 [시각 조작 탐지](../../../03-techniques/analysis/timeline/timestomping.md)를 봅니다.

## 함께 볼 페이지

- [레지스트리 하이브 구조](index.md)
- [하이브 내부 구조 (regf·hbin·Cell)](regf-hbin-cell.md)
- [트랜잭션 로그와 반영 안 된 변경 (.LOG1·.LOG2)](log1-log2.md)
- [MRU 목록 읽는 법 (MRUList·MRUListEx)](mrulist-mrulistex.md)
- [여러 아티팩트 합친 타임라인](../../../03-techniques/analysis/timeline/super-timeline.md)

## 참고 문헌

- Maxim Suhanov, "Windows registry file format specification" — https://github.com/msuhanov/regf/blob/master/Windows%20registry%20file%20format%20specification.md
- Microsoft Learn, "KEY_BASIC_INFORMATION structure (wdm.h)" — https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_key_basic_information
- Microsoft Learn, "NtSetInformationKey function (winternl.h)" — https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntsetinformationkey
- Rohn Edwards, "Leverage Registry Key Time Stamps via PowerShell", Microsoft Scripting Blog (2014) — https://devblogs.microsoft.com/scripting/leverage-registry-key-time-stamps-via-powershell/
- Harlan Carvey, "Timestomping Registry Keys", Windows Incident Response (2022) — http://windowsir.blogspot.com/2022/04/timestomping-registry-keys.html
- Microsoft Learn, "The system registry is no longer backed up to the RegBack folder starting in Windows 10 version 1803" — https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/system-registry-no-backed-up-regback-folder
