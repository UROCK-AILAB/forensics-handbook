---
title: "이벤트 로그를 지웠나"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 3890
---

# 이벤트 로그를 지웠나 (Log Clearing)

> 상위 허브: [증거를 없애려 했나 (Anti-Forensics)](index.md)

이벤트 로그를 지우면 지운 일이 또 하나의 기록으로 남습니다. 이 페이지는 로그를 지운 흔적을 찾고, 누가 어디서 지웠는지 좁히는 순서를 다룹니다. 1102·104 이벤트 자체는 [이벤트 로그 삭제](../../../02-artifacts/event-logs/1102-104.md) 에서, .evtx 파일 형식은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에서 다룹니다. 여기서는 조사에 쓰는 필드만 봅니다.

## 조사 질문

- 이벤트 로그를 누가 언제 지웠습니까?
- 어느 로그를 지웠습니까? 보안 로그입니까, 다른 로그입니까?
- 이 PC 에서 지웠습니까, 다른 PC 에서 원격으로 지웠습니까?
- 지우기 전 기록을 얼마나 되살릴 수 있습니까?

## 먼저 확인할 것

| 확인할 것 | 이유 |
|---|---|
| Windows 버전 | 1102 는 Windows Vista·Windows Server 2008 부터 있습니다[1]. 이벤트 버전은 0 하나뿐입니다[1]. |
| 시간대 | 이벤트 레코드의 기록 시각은 FILETIME 형식의 UTC 입니다[3]. 현지 시각으로 옮길 때는 [시간대 설정](../../../02-artifacts/system-account/time-zone.md) 을 먼저 읽습니다. |
| 사용자 | 1102 의 Subject 필드가 로그를 지운 계정입니다[1]. 그 계정의 로그온 세션은 [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) 이벤트로 잇습니다. |
| 수집 범위 | 로그 폴더(기본 위치 `C:\Windows\System32\winevt\Logs\`)[3] 전체, USN 변경 저널, 프리패치를 확보합니다. 볼륨 섀도 복사본이 있으면 함께 확보합니다. 원격으로 지웠을 수 있으면 같은 네트워크의 다른 PC 로그도 확보합니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 보안 로그 1102 | 보안 로그를 지운 때와 지운 계정 | [이벤트 로그 삭제](../../../02-artifacts/event-logs/1102-104.md) |
| 2 | 104 | 보안 로그가 아닌 로그를 지운 흔적 | [이벤트 로그 삭제](../../../02-artifacts/event-logs/1102-104.md) |
| 3 | 보안 4624·4634·4672 | 지운 계정의 로그온·로그오프와 쓴 특권 | [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) |
| 4 | 보안 4688, Sysmon 1 | 지우는 명령을 실행한 프로그램 | [프로세스 생성](../../../02-artifacts/event-logs/4688.md) · [Sysmon 로그](../../../02-artifacts/event-logs/sysmon/index.md) |
| 5 | USN 변경 저널 | .evtx 파일이 덮어써지고 줄어든 기록 | [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) |
| 6 | 프리패치 | 지우는 도구를 실행한 기록 | [프리패치](../../../02-artifacts/execution/prefetch/index.md) |
| 7 | .evtx 파일, 섀도 복사본 | 남은 레코드, 청크의 빈 공간, 지우기 전 파일 | [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) · [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

## 1102 — 보안 로그를 지웠을 때

보안 감사 로그를 지울 때마다 1102 "The audit log was cleared." 가 남습니다[1]. 채널은 Security 이고 하위 범주는 Other Events 이며, 공급자는 Microsoft-Windows-Eventlog, GUID 는 {fc65ddd8-d6ef-4962-83d5-6e5cfe9ce148} 입니다[1]. 로그온 이벤트(4624 등)의 공급자는 Microsoft-Windows-Security-Auditing 인데[1], 공급자 이름으로 보안 로그를 거르면 1102 가 빠질 수 있습니다. 1102 의 내용은 EventData 가 아니라 UserData 아래 LogFileCleared 요소에 들어 있어서[1], EventData 필드만 뽑는 도구에서는 Subject 필드가 비어 보일 수 있습니다.

| 필드 | 뜻 | 이어 볼 곳 |
|---|---|---|
| SubjectUserSid | 로그를 지운 계정의 SID | [사용자 계정](../../../02-artifacts/system-account/sam.md) |
| SubjectUserName | 로그를 지운 계정 이름 | |
| SubjectDomainName | 그 계정의 도메인 | |
| SubjectLogonId | 로그를 지운 세션의 로그온 ID | 같은 로그온 ID 의 4624 |

보통은 이 이벤트가 보이지 않습니다. 보안 로그를 손으로 지울 일은 대부분 없으므로, 1102 가 있으면 왜 지웠는지 조사합니다[1].

## 104 — 다른 로그를 지웠을 때

wevtutil 로 원격 호스트의 System 로그를 지우면, 로그가 지워진 호스트에 104 "The System log file was cleared." 가 남습니다[2]. 104 는 지운 로그의 맨 앞에 기록되므로[2], 로그의 첫 레코드가 104 이면 그 로그를 지운 흔적으로 봅니다.

Application 같은 다른 로그를 지웠을 때 104 가 어느 로그에 남는지는 실제 기기에서 확인해야 합니다.

## wevtutil 로 원격에서 지운 흔적

wevtutil 로 원격 로그를 지우는 명령 형식은 아래와 같습니다[2]. `/r:` 뒤에 로그를 지울 원격 호스트를 적습니다.

```
wevtutil [Process] [Log Name] /r:[Destination]
```

| 쪽 | 기록 | 알려 주는 것 |
|---|---|---|
| 실행한 쪽 | Sysmon 1 | `C:\Windows\System32\wevtutil.exe` 실행과 명령줄 |
| 실행한 쪽 | 보안 4688 | 프로세스 생성 |
| 실행한 쪽 | Sysmon 3 | 135번 포트 연결 |
| 실행한 쪽 | 보안 5156·5158 | Windows 필터링 플랫폼 (Windows Filtering Platform) 연결 |
| 실행한 쪽 | 프리패치 | wevtutil 실행 기록 |
| 지워진 쪽 | 104 | 로그를 지움 |
| 지워진 쪽 | 보안 5447 | 필터 변경. "remote event log management (RPC-EPMAP)" |
| 지워진 쪽 | 보안 4672 | SeSecurityPrivilege·SeBackupPrivilege·SeRestorePrivilege 특권 |
| 지워진 쪽 | 보안 4624·4634 | 이 작업의 로그온(Kerberos 네트워크 로그온, 유형 3)·로그오프 |
| 지워진 쪽 | USN 변경 저널 | 지워진 .evtx 파일에 DATA_OVERWRITE + DATA_TRUNCATION |

(표는 JPCERT/CC 가 wevtutil 로 원격 호스트의 로그를 지운 분석 결과입니다[2].)

- DATA_TRUNCATION 은 파일 크기가 줄었다는 뜻입니다[2].
- 원격으로 지우면 명령을 실행한 흔적은 실행한 쪽 PC 에 남습니다[2]. 지워진 PC 만 보면 명령줄을 찾지 못합니다.
- 이 분석은 Windows 버전을 밝히지 않았습니다[2]. 버전마다 다를 수 있으니 실제 기기에서 확인합니다.
- wevtutil 말고 다른 방법으로 지웠을 때 남는 흔적은 방법마다 다를 수 있어 실제 기기에서 확인합니다.

## 지운 뒤 .evtx 파일에서 볼 것

.evtx 파일은 4096바이트 파일 헤더와 65536바이트 청크로 이루어집니다[3]. 조사에 쓰는 필드는 아래와 같습니다[3]. 전체 구조는 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에 있습니다.

| 위치 | 오프셋 | 필드 |
|---|---|---|
| 파일 헤더 | 0 | 서명 "ElfFile\x00" (8바이트) |
| 파일 헤더 | 24 | 다음 레코드 식별자 (8바이트) |
| 파일 헤더 | 42 | 청크 수 (4바이트) |
| 파일 헤더 | 120 | 파일 플래그 (4바이트). 0x0001 더티 (Is dirty), 0x0002 가득 참 (Is full) |
| 청크 헤더 | 0 | 서명 "ElfChnk\x00" |
| 청크 헤더 | 48 | 빈 공간 시작 위치 |
| 이벤트 레코드 | 8 | 레코드 식별자 (8바이트) |
| 이벤트 레코드 | 16 | 기록 시각 (FILETIME, UTC) |

레코드 번호와 레코드 식별자는 다른 값입니다[3]. 손상된 파일에서는 청크 안의 식별자가 이어지지 않을 수 있는데[3], 식별자가 건너뛴 것 하나로 레코드를 골라 지웠다고 단정하지 않습니다. 로그를 지운 뒤 식별자가 어떻게 바뀌는지는 실제 기기에서 확인해야 합니다. 104·1102 레코드의 식별자와 기록 시각을 적어 둡니다.

청크의 빈 공간을 살펴보면 레코드를 되살릴 수 있습니다[3]. 빈 공간 시작 위치가 청크 끝을 가리키고 마지막 레코드 뒤가 0 으로 채워진 경우도 있습니다[3]. 빈 공간 시작 위치만 믿지 말고 청크 끝까지 차례로 읽습니다. 섀도 복사본이 있으면 지우기 전 시점의 .evtx 파일을 그 안에서 찾으며, 방법은 [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에 있습니다.

## 분석 흐름

1. 로그 폴더의 .evtx 파일마다 첫 레코드의 이벤트 ID·레코드 식별자·기록 시각을 뽑습니다.
2. 보안 로그에서 1102 를 찾습니다. 공급자 Microsoft-Windows-Eventlog 로 찾고, UserData 아래 Subject 필드를 읽습니다.
3. 다른 로그에서 104 를 찾습니다. 로그의 맨 앞 레코드부터 봅니다.
4. 1102 의 SubjectLogonId 와 로그온 ID 가 같은 4624 를 찾습니다. 같은 세션의 4672 도 찾습니다.
5. 같은 시간대의 4688·Sysmon 1 에서 지우는 명령을 찾습니다. 없으면 프리패치에서 실행 기록을 찾습니다.
6. 지워진 PC 에 5447 과 이 작업의 4624·4634 가 있는데 실행 흔적이 없으면, 원격에서 지운 경우를 봅니다. 4624 에서 로그온한 곳을 확인하고 그 PC 를 확보합니다.
7. USN 변경 저널에서 .evtx 파일 이름으로 DATA_OVERWRITE·DATA_TRUNCATION 을 찾습니다. 이벤트 기록과 따로, 로그 파일이 줄어든 시각을 확인합니다.
8. 청크의 빈 공간과 섀도 복사본에서 지우기 전 레코드를 되살립니다.
9. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리합니다.

## 흔한 오판

1. **1102 의 Task 값을 이벤트 ID 104 로 읽습니다.** 1102 이벤트 XML 의 Task 필드 값은 104 입니다[1]. 이벤트 ID 104 와는 다른 값입니다.
2. **보안 로그를 공급자 Security-Auditing 으로만 거릅니다.** 1102 의 공급자는 Microsoft-Windows-Eventlog 입니다[1]. 이렇게 거르면 1102 가 빠집니다.
3. **1102 가 없으니 로그를 지우지 않았다고 봅니다.** 1102 는 보안 로그를 지웠을 때의 기록입니다[1]. 다른 로그를 지운 흔적은 104 로 따로 찾습니다[2]. USN 변경 저널에서 .evtx 파일이 줄어든 기록도 봅니다.
4. **로그를 지운 계정을 지운 사람으로 씁니다.** Subject 는 로그를 지운 계정입니다[1]. 그 계정을 누가 썼는지는 [그 시각에 PC 를 쓴 사람이 누구인가](../user-attribution.md) 를 따라 따로 확인합니다.
5. **레코드 식별자가 이어지지 않으면 골라 지웠다고 단정합니다.** 손상된 파일에서도 식별자가 이어지지 않을 수 있습니다[3].
6. **원격으로 지운 경우에 지워진 PC 만 봅니다.** 명령 실행 흔적(4688·Sysmon 1·프리패치)은 실행한 쪽에 남습니다[2].

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 증거를 없애려고 보안 로그를 지웠습니다."
- 쓸 문장: "보안 로그에 1102(감사 로그 지움) 이벤트가 ○○(UTC) 에 있습니다. 이 이벤트의 Subject 필드는 ○○\○○ 계정이고 로그온 ID 는 ○○ 입니다. 같은 로그온 ID 의 4624 는 ○○(UTC) 에 있습니다. 이 기록은 해당 계정의 세션에서 보안 로그를 지웠음을 보여 줍니다. 지운 이유와 지운 레코드의 내용은 이 기록만으로 알 수 없습니다."

## 함께 볼 페이지

- [이벤트 로그 삭제](../../../02-artifacts/event-logs/1102-104.md) — 1102·104 이벤트의 구조입니다.
- [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) — .evtx 파일 헤더·청크·레코드를 읽는 법입니다.
- [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) — 로그가 남는 조건입니다.
- [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) · [프로세스 생성](../../../02-artifacts/event-logs/4688.md) · [Sysmon 로그](../../../02-artifacts/event-logs/sysmon/index.md) — 지운 계정과 명령을 잇는 기록입니다.
- [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) — 로그 파일이 줄어든 기록입니다.
- [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 지우기 전 로그 파일을 찾습니다.
- [이벤트 로그 규칙 검색](../../../03-techniques/analysis/sigma-rules.md) — 이벤트를 규칙으로 찾는 법입니다.
- [보안 프로그램을 끄거나 지웠나 (Defense Evasion)](defense-evasion.md) — 로그를 지우기 전후에 보안 프로그램을 건드렸는지 봅니다.

## 참고 문헌

1. Microsoft Learn, "1102(S) The audit log was cleared." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-1102
2. JPCERT/CC, Tool Analysis Result Sheet, "wevtutil" — https://jpcertcc.github.io/ToolAnalysisResultSheet/details/wevtutil.htm
3. libyal libevtx, "Windows XML Event Log (EVTX) format" — https://raw.githubusercontent.com/libyal/libevtx/main/documentation/Windows%20XML%20Event%20Log%20(EVTX).asciidoc
