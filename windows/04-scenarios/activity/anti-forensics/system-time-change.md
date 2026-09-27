---
title: "시스템 시각을 바꿨나"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 3920
---

# 시스템 시각을 바꿨나 (System Time Change)

시스템 시각을 바꾸면 이벤트 로그 항목과 파일의 타임스탬프가 틀어질 수 있습니다[2]. Windows 는 시스템 시각이 바뀔 때마다 보안 로그에 4616 을 남깁니다[1]. 이 페이지는 4616 으로 누가 어떤 프로세스로 시각을 바꿨는지 가려내고, 틀어진 구간을 표시하는 순서를 다룹니다. 4616 이벤트 자체는 [시간 변경](../../../02-artifacts/event-logs/4616-kernel-general.md) 에서, 시각 값 형식은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

## 조사 질문

- 시스템 시각을 누가 언제 바꿨습니까?
- 시각을 얼마나 옮겼습니까?
- 어느 프로세스가 바꿨습니까? 자동 시각 보정입니까, 사람이 바꾼 것입니까?
- 시각이 틀어진 동안 생긴 기록을 얼마나 믿을 수 있습니까?

## 먼저 확인할 것

| 확인할 것 | 이유 |
|---|---|
| Windows 버전 | 4616 은 Windows Vista·Windows Server 2008 부터 있습니다[1]. 이벤트 버전 0 은 Vista·Server 2008 입니다[1]. 버전 1 은 Windows 7·Server 2008 R2 이고, "Process Information" 절이 더해졌습니다[1]. |
| 시간대 | 시각을 바꾸는 일과 시간대를 바꾸는 일은 다릅니다. 권한도 따로 있습니다[2]. 시간대 값은 [시간대 설정](../../../02-artifacts/system-account/time-zone.md) 에서 먼저 읽습니다. |
| 도메인 가입 여부 | 도메인 PC 는 인증한 도메인 컨트롤러와 자동으로 시각을 맞춥니다[2]. 도메인 컨트롤러는 PDC 에뮬레이터와 맞춥니다[2]. |
| 수집 범위 | 보안 로그와 다른 이벤트 로그, 사용자 권한 정책, 파일 시스템 메타데이터($MFT·USN 변경 저널)를 확보합니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 보안 4616 | 바뀌기 전후 시각, 바꾼 계정, 프로세스 | [시간 변경](../../../02-artifacts/event-logs/4616-kernel-general.md) |
| 2 | 보안 4624 | 바꾼 계정의 로그온 세션 | [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) |
| 3 | 보안 4688 | 시각을 바꾼 프로세스를 만든 기록 | [프로세스 생성](../../../02-artifacts/event-logs/4688.md) |
| 4 | 사용자 권한 정책 | 시각을 바꿀 수 있는 계정 | 이 페이지 아래 |
| 5 | 이벤트 로그 레코드 | 레코드 식별자와 기록 시각 | [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) |
| 6 | 파일 시스템 시각 | 틀어진 구간에 만들거나 고친 파일 | [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md) · [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) |
| 7 | 서비스 설정 | Windows Time 서비스를 멈추거나 바꿨는지 | [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md) |

## 4616 에서 읽을 것

제목은 "4616(S) The system time was changed." 이고 시스템 시각이 바뀔 때마다 생깁니다[1]. 하위 범주는 Audit Security State Change 이지만 이 하위 범주의 설정과 상관없이 항상 기록되며[1], 공급자는 Microsoft-Windows-Security-Auditing, 채널은 Security 입니다[1]. 조사에 쓰는 필드는 아래와 같습니다[1].

| 필드 | 뜻 | 이어 볼 곳 |
|---|---|---|
| SubjectUserSid·SubjectUserName·SubjectDomainName | "시스템 시각 바꾸기" 를 요청한 계정 | |
| SubjectLogonId | 그 계정의 로그온 ID | 같은 로그온 ID 의 4624 |
| PreviousTime | 바뀌기 전 시각 (FILETIME, UTC) | |
| NewTime | 바뀐 뒤 시각 (FILETIME, UTC) | |
| ProcessId | 시각을 바꾼 프로세스의 ID (16진) | 4688 의 New Process ID |
| ProcessName | 시각을 바꾼 프로세스의 경로 | |

PreviousTime·NewTime 은 YYYY-MM-DDThh:mm:ss.nnnnnnnZ 형식으로 보이며[1], 두 값의 차이가 시각을 옮긴 폭입니다. 예를 들어 PreviousTime 이 2015-10-09T05:04:30.000941900Z, NewTime 이 2015-10-09T05:04:30.000000000Z 이면[1] 1밀리초가 안 되는 보정입니다.

**정상 보정과 나누는 기준.**

Subject 의 Security ID 가 LOCAL SERVICE 인 4616 은 보통 보이는 정상 시각 보정입니다[1]. Subject 가 LOCAL SERVICE 가 아니면 Windows Time 서비스가 한 변경이 아니므로 따로 살펴봅니다[1]. Process Name 이 `C:\Windows\System32\svchost.exe` 가 아닌 경우도 따로 살펴봅니다[1].

## 누가 시각을 바꿀 수 있나

시각을 바꾸려면 "Change the system time" 사용자 권한(상수 이름 SeSystemtimePrivilege)이 있어야 합니다[2]. 이 권한으로 이벤트 로그·DB 트랜잭션·파일 시스템 기록에 붙는 날짜와 시각을 바꿀 수 있고, 시각 동기화 프로세스에도 이 권한이 필요합니다[2].

- 정책 위치는 `Computer Configuration\Windows Settings\Security Settings\Local Policies\User Rights Assignment` 입니다[2].
- 기본으로 이 권한을 받는 계정은 아래와 같습니다[2].

| 컴퓨터 종류 | 기본으로 권한을 받는 계정 |
|---|---|
| 워크스테이션·서버 | Administrators, Local Service |
| 도메인 컨트롤러 | Administrators, Server Operators, Local Service |

시간대를 바꾸는 권한("Change the time zone")은 따로 있으며[2], 시각을 바꾸는 권한은 시간대에 영향이 없습니다[2].
- 4616 의 Subject 가 이 기본 목록에 없는 계정이면, 권한 정책을 바꿨는지 함께 봅니다.

## 시각을 바꾸면 무엇이 틀어지나

시각을 바꾸면 아래 문제가 생길 수 있습니다[2].

- 이벤트 로그 항목의 타임스탬프가 부정확해질 수 있습니다.
- 새로 만들거나 고친 파일·폴더의 타임스탬프가 틀릴 수 있습니다.
- 도메인 인증이 안 될 수 있습니다. Kerberos 는 허용 시차 안에서 시계가 맞아야 합니다.
- 시각을 바꾼 뒤 Windows Time 서비스를 멈추거나 부정확한 시간 서버로 바꾸면 더 심각해집니다.

## 이벤트 로그 레코드로 순서 보기

.evtx 레코드마다 레코드 식별자와 기록 시각(FILETIME, UTC)이 함께 들어 있으므로[3], 레코드를 식별자 순서로 늘어놓고 기록 시각이 거꾸로 가는 곳이 있는지 살펴볼 수는 있습니다. 다만 이 방법은 4616 을 보조하는 단서로만 씁니다.

- 손상된 파일에서는 식별자가 이어지지 않을 수 있습니다[3]. 식별자를 읽는 주의점은 [이벤트 로그를 지웠나 (Log Clearing)](log-clearing.md) 에 있습니다.

## 분석 흐름

1. 시간대 설정을 먼저 읽습니다. 시간대 변경과 시각 변경을 섞지 않습니다.
2. 보안 로그에서 4616 을 모두 뽑습니다.
3. Subject 가 LOCAL SERVICE 이고 ProcessName 이 `C:\Windows\System32\svchost.exe` 인 이벤트를 따로 묶습니다. 보통 보이는 자동 보정입니다[1].
4. 나머지 4616 마다 PreviousTime 과 NewTime 의 차이를 계산합니다.
5. SubjectLogonId 로 4624 를 찾아 어느 세션에서 바꿨는지 봅니다. ProcessId 로 4688 을 찾아 그 프로세스를 만든 기록을 봅니다[1].
6. 시각을 옮긴 4616 뒤에 시각을 되돌린 4616 이 있는지 봅니다. 두 이벤트 사이가 시각이 틀어진 구간입니다.
7. 도메인 PC 이면 사람이 바꾼 4616 뒤에 LOCAL SERVICE 의 4616 이 이어지는지 봅니다. 도메인 PC 는 도메인 컨트롤러와 자동으로 시각을 맞춥니다[2].
8. 틀어진 구간에 만들거나 고친 파일과 로그 항목을 표시하고, 옮긴 폭을 함께 적습니다. 시각을 고쳐 적을지는 다른 기록과 맞춰 본 뒤 정합니다.
9. Windows Time 서비스의 설정을 [서비스·드라이버](../../../02-artifacts/persistence/services-drivers.md) 에서 확인합니다.
10. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리합니다.

## 흔한 오판

1. **4616 이 있으니 시각을 조작했다고 봅니다.** LOCAL SERVICE 가 남긴 4616 은 보통 보이는 정상 보정입니다[1].
2. **4616 이 없으니 감사 설정이 꺼져 있었다고 봅니다.** 4616 은 하위 범주 설정과 상관없이 항상 기록됩니다[1]. 4616 이 없으면 로그를 지웠는지 [이벤트 로그를 지웠나 (Log Clearing)](log-clearing.md) 를 따라 봅니다.
3. **PreviousTime·NewTime 을 현지 시각으로 읽습니다.** 두 값은 UTC 입니다[1].
4. **시간대 변경을 시각 변경으로 봅니다.** 둘은 권한부터 다릅니다[2]. 시간대 Bias 는 REG_DWORD 로 저장되지만 부호 있는 32비트로 읽습니다. UTC+9 는 -540 이고, 부호 없이 읽으면 4294966756 입니다.
5. **도구가 보여 준 10진 값을 그대로 씁니다.** 레지스트리 값을 문자열로 받는 도구는 REG_DWORD 를 부호 없는 10진으로 보여 주는 경우가 많습니다. 부호에 뜻이 있는 값은 원시 바이트로 확인합니다.
6. **틀어진 구간의 파일 시각을 그대로 보고합니다.** 시각을 바꾸면 새로 만들거나 고친 파일의 타임스탬프가 틀릴 수 있습니다[2]. 문서 날짜를 따질 때는 [이 문서의 날짜를 믿을 수 있나](../document-date-verification.md) 를 함께 봅니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 알리바이를 만들려고 PC 시각을 조작했습니다."
- 쓸 문장: "보안 로그에 4616(시스템 시각 변경) 이벤트가 있습니다. 이 이벤트의 PreviousTime 은 ○○(UTC), NewTime 은 ○○(UTC) 로 약 ○시간 차이입니다. Subject 필드는 ○○\○○ 계정이고, ProcessName 은 ○○ 입니다. 이 기록은 이 계정의 세션에서 이 프로세스가 시스템 시각을 바꿨음을 보여 줍니다. ○○ 부터 ○○ 사이에 생긴 파일과 로그의 시각은 이 차이만큼 틀어졌을 수 있습니다. 시각을 바꾼 이유는 이 기록만으로 알 수 없습니다."

## 함께 볼 페이지

- [시간 변경](../../../02-artifacts/event-logs/4616-kernel-general.md) — 시간 변경 이벤트의 구조입니다.
- [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) — FILETIME 을 읽는 법입니다.
- [시간대 설정](../../../02-artifacts/system-account/time-zone.md) — 시간대 값과 Bias 를 읽는 법입니다.
- [로그온·로그오프](../../../02-artifacts/event-logs/logon-events/index.md) · [프로세스 생성](../../../02-artifacts/event-logs/4688.md) — 4616 의 계정과 프로세스를 잇는 기록입니다.
- [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) — 틀어진 구간을 표시해 시각을 정리합니다.
- [이 문서의 날짜를 믿을 수 있나](../document-date-verification.md) — 파일과 문서의 날짜를 따로 따집니다.

## 참고 문헌

1. Microsoft Learn, "4616(S) The system time was changed." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4616
2. Microsoft Learn, "Change the system time - security policy setting" — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/change-the-system-time
3. libyal libevtx, "Windows XML Event Log (EVTX) format" — https://raw.githubusercontent.com/libyal/libevtx/main/documentation/Windows%20XML%20Event%20Log%20(EVTX).asciidoc
