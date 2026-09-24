# 어떤 프로그램을 언제 실행했나 (Program Execution)

실행 파일 하나를 두고 "이 PC 에서 실행됐나, 언제·몇 번·어느 계정의 세션에서 실행됐나" 를 묻는 조사를 다룹니다. Windows 에는 실행과 관계있는 기록이 여럿 있고 기록마다 증명하는 범위가 다릅니다. 이 페이지는 기록마다 실행을 증명하는지 나눠 보고, 어떤 순서로 맞춰 보는지를 정리합니다.

"(관찰)" 을 붙인 내용은 Windows 11 Home 25H2(빌드 26200, 시간대 Korea Standard Time) PC 한 대에서 직접 본 것입니다(확인 범위: Win11 25H2 한 대). 다른 빌드나 다른 PC 에서는 다를 수 있습니다.

## 조사 질문

- 이 실행 파일이 이 PC 에서 실행된 적이 있습니까?
- 언제, 몇 번 실행했습니까?
- 어느 계정의 세션에서 실행했습니까?
- 어떤 명령줄로 실행했고, 어느 프로세스가 띄웠습니까?
- 실행 파일이 지금 디스크에 없다면, 어떤 파일이었습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | 심캐시 형식, UserAssist 키, 4688 의 칸이 버전마다 다릅니다. [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 버전과 빌드를 먼저 적습니다. |
| 시간대 | 기록마다 시각 기준이 다릅니다. [시간대 설정](../../02-artifacts/system-account/time-zone.md) 을 읽습니다. Bias 값을 부호 있는 수로 읽는 법은 [이 파일을 누가 언제 열었나](file-access.md) 의 "먼저 확인할 것" 에 있습니다. |
| 사용자 | 프리페치와 심캐시에는 사용자 정보가 없습니다. UserAssist 는 사용자 하이브(NTUSER.DAT)에 남습니다. [사용자 프로필 목록](../../02-artifacts/system-account/profilelist.md) 으로 SID 와 프로필을 짝지어 둡니다. |
| 프리페치 설정 | `EnablePrefetcher` 값이 0 이면 프리페치 파일이 생기지 않습니다. |
| 감사 정책 | 4688 은 프로세스 만들기 감사가 켜져 있을 때만 남습니다[1]. [감사 정책과 로그 설정](../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 확인합니다. |
| Sysmon | Sysmon 은 따로 설치해야 생기는 로그입니다[2]. 설치 여부부터 봅니다. |
| 수집 범위 | 프리페치 폴더, SYSTEM·SOFTWARE·사용자 하이브, AmCache 하이브, SRUDB.dat, `C:\Windows\appcompat\pca\` 폴더, 보안 로그, Sysmon 로그를 함께 확보합니다. |

**`EnablePrefetcher` 값.**

| 값 | 뜻 |
|---|---|
| 0 | 끔 |
| 1 | 프로그램 실행만 |
| 2 | 부팅만 |
| 3 | 둘 다 |

이 PC 는 `EnablePrefetcher` 가 3 이었고 `.pf` 파일이 294개 있었으며, 프로세스 만들기 감사는 꺼져 있었습니다(관찰). `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit` 에는 `ProcessCreationIncludeCmdLine_Enabled` 값이 없었습니다(관찰). 이 값이 아래 "명령줄 포함" 정책과 짝이라는 것은 확인하지 못했습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 실행을 증명하나 | 링크 |
|---|---|---|---|---|
| 1 | 프리페치 | 실행 횟수, 최근 실행 시각(Windows 8 이후 최대 8개), 실행 직후 읽은 파일 | 증명합니다. 사용자는 알려 주지 않습니다. | [프리페치](../../02-artifacts/execution/prefetch/index.md) |
| 2 | UserAssist | 사용자별 실행 횟수, 마지막 실행 시각 | 그 사용자 세션의 실행으로 읽습니다. GUID 의 뜻은 알려진 해석입니다. | [UserAssist](../../02-artifacts/execution/userassist.md) |
| 3 | BAM | SID 별 장치 경로와 FILETIME 으로 읽히는 값(관찰) | 값의 뜻을 문서로 확인하지 못했습니다. 다른 기록과 맞춰 씁니다. | [BAM·DAM](../../02-artifacts/execution/background-activity-moderator.md) |
| 4 | 프로그램 호환성 도우미 | 전체 경로와 시각(관찰) | 보조 기록으로 씁니다. | [프로그램 호환성 도우미](../../02-artifacts/execution/pca.md) |
| 5 | 보안 로그 4688 | 새 프로세스, 부모 프로세스, 명령줄, 권한 상승 여부 | 감사가 켜져 있으면 증명합니다. | [프로세스 생성](../../02-artifacts/event-logs/4688.md) |
| 6 | Sysmon 이벤트 1 | 명령줄, 파일 해시, ProcessGUID | 설치돼 있으면 증명합니다. | [Sysmon 로그](../../02-artifacts/event-logs/sysmon/index.md) |
| 7 | SRUM | 앱·사용자별 자원 사용량(1시간 단위) | 그 시간대에 앱이 자원을 쓴 기록입니다. | [SRUM](../../02-artifacts/execution/system-resource-usage-monitor/index.md) |
| 8 | AmCache | 파일 경로, SHA-1 | 항목만으로는 증명하지 못합니다. | [AmCache](../../02-artifacts/execution/amcache-hve/index.md) |
| 9 | 심캐시 | 경로, 파일의 마지막 수정 시각 | 항목만으로는 증명하지 못합니다. | [심캐시](../../02-artifacts/execution/shimcache-appcompatcache.md) |
| 10 | 그 밖의 기록 | 아래 "그 밖의 흔적" 참고 | 기록마다 다릅니다. | 아래 링크 |

프리페치·AmCache·SRUM 의 구조와 해석은 각 링크 페이지에 있습니다. 아래에서는 조사 순서에 필요한 부분만 다룹니다. SRUDB.dat 는 ESE 형식입니다. 압수 이미지에서 손상된 DB 를 다루는 법은 [웹 사용 행위 재구성](web-activity.md) 의 "먼저 확인할 것" 과 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에 있습니다.

## 심캐시

심캐시 (ShimCache·AppCompatCache) 는 SYSTEM 하이브의 값 하나에 여러 항목이 이어 붙은 형식입니다.

- 2000·XP 는 `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatibility` 에 남습니다[3].
- 2003 이후는 `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache` 에 남습니다[3].

| Windows | 형식 서명 | 머리 크기 |
|---|---|---|
| XP | 0xdeadbeef | 400바이트 |
| 2003·Vista | 0xbadc0ffe | 8바이트 |
| 7 | 0xbadc0fee | 128바이트 |
| 8.0 | "00ts" | 128바이트 |
| 8.1 | "10ts" | (확인하지 못함) |
| 10 | "10ts" | 48 또는 52바이트 |

(표는 [3] 에서 옮겼습니다.)

**Windows 10 항목.** 서명 "10ts", 알 수 없는 칸, 항목 데이터 크기, 경로 크기, UTF-16 경로, 마지막 수정 시각(FILETIME), 데이터 크기, 데이터 순서로 이어집니다[3].

**항목의 시각은 실행 시각이 아닙니다.**

NTFS 에서 항목의 시각은 캐시를 갱신한 시각이 아니라 그 파일 $STANDARD_INFORMATION 의 마지막 수정 시각입니다[3]. 그래서 이 시각을 실행 시각으로 쓰지 않습니다.

**삽입 플래그.** Windows 7~8.1 항목에는 삽입 플래그가 있습니다[3]. 값 0x00000002 는 "CSRSS.EXE 가 실행했다고 표시" 한 것입니다[3]. Windows 10 에서는 이 플래그가 항목 구조에서 빠졌습니다[3].

**캐시 비우기.** Vista 이후에는 `Rundll32.exe apphelp.dll,ShimFlushCache` 명령으로 캐시를 비웁니다[3]. 항목이 없다고 파일이 없었다고 단정하지 않습니다.

**레지스트리에 쓰는 시점.** 참고한 문서에는 캐시를 레지스트리에 언제 쓰는지 적혀 있지 않습니다[3]. "종료할 때 쓴다" 는 설명이 널리 알려져 있지만 확인하지 못했습니다.

**이 PC 에서 본 값.**

AppCompatCache 값은 214,066바이트였고, 앞 4바이트 값은 0x34(52)였으며, 오프셋 0x34 에서 "10ts" 가 나왔습니다(관찰). 값 안에 "10ts" 서명은 904개 있었습니다(관찰).

아래는 이 배치를 보여 주려고 명세와 관찰을 바탕으로 만든 예시입니다. 실제 검체에서 떼어 온 바이트가 아닙니다.

```
오프셋      바이트            뜻
00000000   34 00 00 00       앞 4바이트 = 0x34 (52)
00000034   31 30 74 73       "10ts" — 첫 항목의 서명
```

## UserAssist

UserAssist 는 사용자 하이브의 탐색기(Explorer) 키 아래에 남는 실행 기록입니다.

- 키는 `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist` 이고, 파일로는 NTUSER.DAT 에 있습니다[4].

| GUID | 알려진 해석 | Windows |
|---|---|---|
| {CEBFF5CD-ACE2-4F4F-9178-9926F41749EA} | 실행 파일 실행 (추정) | 2008·7·8·10 |
| {F4E57C4B-2036-45F0-A9AB-443BCFE33D9F} | 바로가기 실행 (추정) | 2008·7·8·10 |
| {75048700-EF1F-11D0-9888-006097DEACF9} · {5E6AB780-7743-11CF-A12B-00AA004AE837} | — | 2000~Vista |

문서도 GUID 의 뜻을 "Assumed" 로 적었으므로 보고서에도 알려진 해석이라고 씁니다[4].

**값 이름은 ROT-13 입니다.**

값 이름은 ASCII 영문자 [A-Za-z] 만 ROT-13 으로 바꿔 적고 다른 글자는 그대로 둡니다[4].

- 예를 들어 `HRZR_PGYFRFFVBA` 를 풀면 `UEME_CTLSESSION` 이 됩니다.
- 특수 값으로 UEME_CTLSESSION(세션 식별자)과 UEME_CTLCUACount:ctor 가 있습니다[4].

**값 데이터.**

| 형식 | Windows | 크기 | 오프셋과 뜻 |
|---|---|---|---|
| 버전 3 | 2000·XP·2003·Vista | 16바이트 | 0 세션 식별자(4), 4 실행 횟수(4), 8 마지막 실행 시각 FILETIME(8) |
| 버전 5 | 7·8 등 | 72바이트 | 4 실행 횟수(4), 8 포커스 횟수(4), 12 포커스 시간(4), 60 마지막 실행 시각 FILETIME(8, 없으면 0) |

(표는 [4] 에서 옮겼습니다. 포커스 시간의 단위는 확인하지 못했습니다.)

**이 PC 에서 본 값.**

- GUID 키 9개의 Version 값이 모두 5 였습니다(관찰).
- {CEBFF5CD…} 의 Count 키에는 값이 203개 있었습니다(관찰). 72바이트 값이 202개, 1,612바이트 값이 1개였습니다(관찰).
- {F4E57C4B…} 의 Count 키에는 값이 25개 있었습니다(관찰). 72바이트 값이 24개, 1,612바이트 값이 1개였습니다(관찰).
- 1,612바이트 값의 이름은 `HRZR_PGYFRFFVBA` 였습니다(관찰).
- 값 이름 가운데 경로 앞부분이 `{…GUID…}\` 로 된 것이 있었습니다(관찰). 알려진 폴더 GUID 로 보입니다. 경로로 바꾸는 법은 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에서 봅니다.
- 스토어 앱 식별자(…!App) 형식의 값 이름도 있었습니다(관찰).
- 명령줄로 띄운 실행이 UserAssist 에 남는지는 확인하지 못했습니다.

## BAM

BAM (Background Activity Moderator) 키에는 SID 별로 실행 파일 경로가 남습니다. 아래는 모두 이 PC 에서 본 내용입니다.

- `HKLM\SYSTEM\CurrentControlSet\Services\bam\State\UserSettings\<SID>` 아래에 SID 별 키가 있었습니다(관찰).
- SID 는 S-1-5-18, 사용자 SID 두 개, S-1-5-90-0-1 이었습니다(관찰).
- 값 이름은 `\Device\HarddiskVolumeN\...\이름.exe` 형식의 장치 경로이거나 스토어 앱 패키지 이름이었습니다(관찰).
- 값 데이터는 24바이트였습니다(관찰). 앞 8바이트를 FILETIME 으로 읽으면 최근 날짜가 나왔습니다(관찰).
- `dam\State\UserSettings` 키는 이 PC 에 없었습니다(관찰).

값 이름이 드라이브 문자가 아니라 볼륨 장치 경로라서 `HarddiskVolumeN` 을 드라이브 문자와 맞추는 과정이 필요합니다. BAM 이 생긴 Windows 버전, 값이 뜻하는 시각, 오래된 항목을 지우는지는 확인하지 못했습니다. 이 값을 "마지막 실행 시각" 으로 단정하지 않고 프리페치·UserAssist 와 맞춰 씁니다.

## 프로그램 호환성 도우미

아래는 모두 이 PC 에서 본 내용입니다.

- `C:\Windows\appcompat\pca\` 에 PcaAppLaunchDic.txt, PcaGeneralDb0.txt, PcaGeneralDb1.txt 가 있었습니다(관찰). PcaGeneralDb1.txt 는 0바이트였습니다(관찰).
- PcaAppLaunchDic.txt 는 UTF-8(또는 ASCII) 글자 파일이었습니다(관찰).
- 이 파일의 95줄 가운데 94줄이 `전체 경로|YYYY-MM-DD HH:MM:SS.fff` 형식이었습니다(관찰).
- 이 가운데 두 줄(WindowsTerminal.exe, Orca.exe)의 시각을 같은 프로그램의 프리페치 파일 수정 시각(UTC)과 비교했습니다(관찰). 차이는 0~19초였습니다(관찰).
- 이 PC 의 시간대는 UTC+9 입니다. 그래서 이 파일의 시각은 UTC 로 보입니다. 두 건만 맞춘 결과이므로 검체마다 다시 맞춰 봅니다.
- PcaGeneralDb0.txt 는 UTF-16 글자 파일이었습니다(관찰). 한 줄이 `|` 로 나뉜 8칸이었고, 첫 칸이 시각이었습니다(관찰). 나머지 칸의 뜻은 확인하지 못했습니다.

PCA 파일이 어느 Windows 버전부터 생겼는지는 확인하지 못했습니다. 검체에 폴더가 없으면 버전부터 확인합니다.

## 보안 로그 4688

4688 "A new process has been created." 은 Audit Process Creation 하위 범주의 이벤트입니다[1]. 새 프로세스가 시작될 때마다 생깁니다[1].

| 이벤트 버전 | Windows | 달라진 점 |
|---|---|---|
| 0 | Vista·Server 2008 | 처음 판 |
| 1 | 8.1·Server 2012 R2 | Process Command Line 칸이 붙었습니다. |
| 2 | 10 | Subject 가 Creator Subject 로 바뀌었습니다. Target Subject·Mandatory Label·Creator Process Name 이 붙었습니다. |

(표는 [1] 에서 옮겼습니다.)

**조사에 쓰는 칸.**

| 묻는 것 | 칸 |
|---|---|
| 누가 띄웠나 | SubjectUserSid, SubjectUserName, SubjectDomainName, SubjectLogonId |
| 무엇이 떴나 | NewProcessId, NewProcessName, CommandLine |
| 어느 프로세스가 띄웠나 | ProcessId, ParentProcessName |
| 어떤 권한으로 | TokenElevationType, MandatoryLabel |
| 새 프로세스의 계정 | TargetUserSid, TargetUserName, TargetDomainName, TargetLogonId |

**명령줄은 기본으로 비어 있습니다.** 그룹 정책 "Administrative Templates\System\Audit Process Creation\Include command line in process creation events" 를 켜야 명령줄이 들어갑니다[1]. 기본값에서는 Process Command Line 칸이 비어 있습니다[1].

**Token Elevation Type.**

| 표시 | 유형 | 뜻 |
|---|---|---|
| %%1936 | 유형 1 | 전체 토큰입니다. UAC 가 꺼져 있거나, 기본 Administrator 계정이거나, 서비스 계정 등입니다. |
| %%1937 | 유형 2 | 관리자 권한으로 실행한 상승 토큰입니다. |
| %%1938 | 유형 3 | 제한 토큰입니다. |

**Mandatory Label.** S-1-16-4096 은 Low, S-1-16-8192 는 Medium, S-1-16-12288 은 High, S-1-16-16384 는 System, S-1-16-20480 은 Protected process 입니다[1].

SubjectLogonId 는 로그온 이벤트와 이어 봅니다([로그온·로그오프](../../02-artifacts/event-logs/logon-events/index.md)). PowerShell 로 실행한 명령은 [PowerShell 실행 기록](../../02-artifacts/event-logs/powershell-event-logs-4103-4104.md) 에서 함께 봅니다.

## Sysmon 이벤트 1

Sysmon 은 서비스와 드라이버를 설치해야 기록을 남기고, Vista 이후에는 `Applications and Services Logs/Microsoft/Windows/Sysmon/Operational` 에 씁니다[2]. 이벤트 시각은 UTC 입니다[2]. 현재 판은 클라이언트 Windows 11 이상, 서버 Windows Server 2019 이상에서 돈다고 적혀 있습니다[2].

| 이벤트 | 남는 것 |
|---|---|
| 1 프로세스 생성 | 전체 명령줄, `ProcessGUID`, `HashType` 에 적힌 알고리즘으로 계산한 파일 전체 해시 |
| 5 프로세스 종료 | `UtcTime`, `ProcessGuid`, `ProcessId` |
| 29 | 새 실행 파일(PE) 생성 탐지 |

(표는 [2] 에서 옮겼습니다.)

- `ProcessGUID` 는 도메인 안에서 이 프로세스를 가리키는 고유 값입니다[2]. 이벤트 1 과 5 는 이 값으로 짝지어 봅니다.
- 기본 설치는 SHA1 해시를 남기고 네트워크는 감시하지 않습니다[2].

## 그 밖의 흔적

아래 기록은 이 페이지에서 세부를 다루지 않습니다. 조사 질문에 맞는 것을 골라 봅니다.

- [MUICache](../../02-artifacts/execution/muicache.md) · [작업표시줄 사용 기록](../../02-artifacts/execution/featureusage.md) · [실행 창 명령 기록](../../02-artifacts/execution/runmru.md)
- [PowerShell 명령 기록](../../02-artifacts/execution/consolehost-history-txt.md) · [PowerShell 실행 기록](../../02-artifacts/event-logs/powershell-event-logs-4103-4104.md)
- [윈도 오류 보고](../../02-artifacts/execution/wer.md) · [디펜더 검사 로그·격리 파일](../../02-artifacts/execution/mplog-detectionhistory-quarantine.md)
- [서비스 설치](../../02-artifacts/event-logs/7045-4697.md) · [예약 작업 이벤트](../../02-artifacts/event-logs/taskscheduler-4698.md)

## 분석 흐름

1. Windows 버전·시간대·사용자 SID 를 정리합니다. `EnablePrefetcher` 값, 프로세스 만들기 감사, Sysmon 설치 여부를 적어 둡니다.
2. 프리페치 폴더에서 실행 파일 이름으로 `.pf` 파일을 찾습니다. 이름이 같고 경로 해시가 다른 파일이 여럿이면 경로마다 따로 봅니다.
3. 프리페치의 실행 횟수와 최근 실행 시각을 적습니다. 실행 직후 읽은 파일 목록도 함께 봅니다.
4. 사용자마다 UserAssist 값 이름의 ROT-13 을 풀어 같은 실행 파일을 찾습니다. 실행 횟수와 마지막 실행 시각을 적습니다.
5. BAM 에서 SID 별로 같은 파일을 찾습니다. 장치 경로를 드라이브 문자로 바꿔 경로를 맞춥니다.
6. PCA 파일에서 같은 경로를 찾아 시각을 적습니다.
7. 4688 이나 Sysmon 이벤트 1 이 있으면 명령줄, 부모 프로세스, 해시, 계정을 봅니다. SubjectLogonId 로 로그온 세션을 잇습니다.
8. SRUM 에서 그 시간대에 이 앱이 자원을 쓴 기록을 봅니다.
9. AmCache·심캐시로 파일 경로·SHA-1·수정 시각을 확인합니다. 이 둘은 실행 증거가 아니라 파일 정보를 보태는 기록으로 씁니다. 실행 파일이 지금 없으면 이 경로와 해시로 찾습니다([지운 파일의 흔적 찾기](deleted-file-traces.md)).
10. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올립니다.
11. 자동실행으로 뜬 것인지는 [악성코드 지속성(자동실행) 찾기](../incident/persistence.md) 로 확인합니다. 그 시각에 누가 PC 앞에 있었는지는 [그 시각에 PC 를 쓴 사람이 누구인가](user-attribution.md) 로 좁힙니다.

## 흔한 오판

1. **AmCache 나 심캐시에 있으니 실행했다고 씁니다.** AmCache 항목이 있다고 실행했다는 뜻이 아닙니다. 심캐시 항목도 실행을 증명하지 못합니다.
2. **심캐시 시각을 실행 시각으로 씁니다.** 그 시각은 파일의 마지막 수정 시각입니다[3].
3. **최근 항목 바로가기로 실행을 말합니다.** 실행 파일은 최근 항목에서 걸러집니다. 바로가기 파일은 [이 파일을 누가 언제 열었나](file-access.md) 에서 다룹니다.
4. **프리페치가 없으니 실행하지 않았다고 봅니다.** 프리페치는 꺼져 있을 수 있습니다. Windows 8 이후 보관 한도는 1,024개라서 오래된 파일이 밀려날 수 있습니다.
5. **UserAssist GUID 의 뜻을 확정된 사실로 씁니다.** 두 GUID 의 뜻은 추정입니다[4].
6. **BAM·PCA 시각을 문서로 확인된 실행 시각처럼 씁니다.** 이 페이지의 BAM·PCA 내용은 한 PC 에서 본 것입니다(관찰).
7. **4688 이 없으니 실행하지 않았다고 봅니다.** 감사 정책이 꺼져 있었을 수 있습니다(관찰).
8. **4688 명령줄이 비어 있으니 인자 없이 실행했다고 봅니다.** 정책을 켜지 않으면 명령줄 칸은 비어 있습니다[1].
9. **실행 기록을 사람의 조작으로 씁니다.** 서비스·예약 작업·자동실행으로 뜬 프로그램도 같은 기록을 남깁니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 ○○ 에 ○○.exe 를 실행했습니다."
- 쓸 문장: "프리페치 파일 `○○.EXE-○○.pf` 에는 실행 횟수 ○회와 최근 실행 시각 ○개가 있습니다. 가장 최근 값은 ○○(UTC) 입니다. 사용자 ○○ 의 UserAssist 에도 같은 실행 파일 항목이 있습니다. 이 항목의 마지막 실행 시각은 ○○(UTC) 입니다. 이 기록은 이 PC 에서 이 실행 파일이 실행됐음을 보여 줍니다. 명령줄 인자와 화면 앞에 있던 사람은 이 기록만으로 정할 수 없습니다."
- 심캐시만 있을 때: "SYSTEM 하이브의 심캐시에 `○○` 경로 항목이 있습니다. 이 항목은 그 경로에 파일이 있었음을 보여 줍니다. 항목의 시각 ○○ 은 파일의 마지막 수정 시각입니다. 이 시각은 실행 시각이 아닙니다."

## 함께 볼 페이지

- [프리페치](../../02-artifacts/execution/prefetch/index.md) · [AmCache](../../02-artifacts/execution/amcache-hve/index.md) · [SRUM](../../02-artifacts/execution/system-resource-usage-monitor/index.md) — 실행 기록의 구조입니다.
- [심캐시](../../02-artifacts/execution/shimcache-appcompatcache.md) · [UserAssist](../../02-artifacts/execution/userassist.md) · [BAM·DAM](../../02-artifacts/execution/background-activity-moderator.md) · [프로그램 호환성 도우미](../../02-artifacts/execution/pca.md) — 레지스트리와 파일에 남는 실행 흔적입니다.
- [프로세스 생성](../../02-artifacts/event-logs/4688.md) · [Sysmon 로그](../../02-artifacts/event-logs/sysmon/index.md) — 이벤트 로그의 실행 기록입니다.
- [악성코드 지속성(자동실행) 찾기](../incident/persistence.md) — 자동으로 뜬 프로그램을 가립니다.
- [악성코드는 어디서 들어왔나](../incident/initial-access.md) — 실행 파일이 들어온 경로를 봅니다.
- [이 파일은 어디서 왔나](file-origin.md) — 실행 파일의 출처를 봅니다.
- [그 시각에 PC 를 쓴 사람이 누구인가](user-attribution.md) — 계정에서 사람으로 좁힙니다.

## 참고 문헌

1. Microsoft Learn, "4688(S) A new process has been created." (Windows 10 보관 문서) — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4688
2. Microsoft Learn, "Sysmon - Sysinternals" (2026-09-10 판) — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
3. libyal, Windows Registry Knowledge Base, "Application Compatibility Cache" — https://winreg-kb.readthedocs.io/en/latest/sources/system-keys/Application-compatibility-cache.html
4. libyal, Windows Registry Knowledge Base, "Windows User Assist Registry Key" — https://winreg-kb.readthedocs.io/en/latest/sources/explorer-keys/User-assist.html
