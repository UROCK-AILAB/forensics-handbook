---
title: "그 시각에 PC 를 쓴 사람이 누구인가"
parent: "시나리오 · 행위 재구성"
nav_order: 3860
---

# 그 시각에 PC 를 쓴 사람이 누구인가 (User Attribution)

어떤 행위의 기록을 찾은 뒤 "그 시각에 이 PC 를 쓴 사람이 누구인가" 를 묻는 조사를 다룹니다. Windows 의 기록은 사람이 아니라 계정을 가리키므로 이 질문은 세 단계로 나뉩니다. 기록이 어느 계정의 것인지 정하고, 그 시각에 그 계정의 세션이 어떤 모습이었는지 확인하고, 그 계정을 누가 쓸 수 있었는지 좁힙니다. 이 페이지는 이 세 단계를 어떤 기록으로 밟는지 정리합니다.

## 조사 질문

- 이 기록은 어느 계정의 것입니까?
- 그 계정은 로컬 계정입니까, 도메인 계정입니까?
- 그 시각에 그 계정의 세션이 열려 있었습니까? PC 앞에서 연 세션입니까, 원격 세션입니까?
- 그 계정을 다른 사람도 쓸 수 있었습니까?
- 피조사자와 그 계정을 이어 주는 다른 증거가 있습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| 계정 목록 | 로컬 계정은 [사용자 계정](../../02-artifacts/system-account/sam.md) 에서, 프로필 폴더와 SID 의 짝은 [사용자 프로필 목록](../../02-artifacts/system-account/profilelist.md) 에서 정리합니다. |
| 도메인 가입 여부 | 도메인 계정은 PC 밖의 Active Directory 에도 기록이 있습니다. 작업 그룹·도메인 이름을 읽는 법은 [레지스트리 속 비밀번호 정보](../../02-artifacts/credentials/sam-security/index.md) 에 있습니다. |
| 시간대 | 세션 기록과 행위 기록을 한 줄로 세우려면 시간대가 필요합니다. [시간대 설정](../../02-artifacts/system-account/time-zone.md) 을 읽고, Bias 값은 [이 파일을 누가 언제 열었나](file-access.md) 의 "먼저 확인할 것" 에 적은 대로 부호 있는 수로 읽습니다. |
| 감사 정책 | 로그온·잠금 이벤트는 감사가 켜져 있어야 남습니다. [감사 정책과 로그 설정](../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 확인합니다. |
| 수집 범위 | SAM·SECURITY·SOFTWARE·SYSTEM 하이브, 사용자마다의 NTUSER.DAT·UsrClass.dat, Security 로그를 함께 확보합니다. 하이브 구조는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | SAM·프로필 목록 | 계정 이름과 SID, 프로필 폴더 | [사용자 계정](../../02-artifacts/system-account/sam.md) · [사용자 프로필 목록](../../02-artifacts/system-account/profilelist.md) |
| 2 | 계정 생성·변경 이벤트 | 계정을 만들고 바꾼 시각 | [계정 생성·변경](../../02-artifacts/event-logs/account-management-events.md) |
| 3 | 로그온·로그오프 이벤트 | 그 시각 앞뒤로 열린 세션과 로그온 유형 | [로그온·로그오프](../../02-artifacts/event-logs/logon-events/index.md) |
| 4 | 잠금·해제·원격 세션 이벤트 | 세션 안에서 화면이 잠겼는지, 원격으로 이어졌는지 | [PC 사용 시간 재구성](system-usage-time.md) · [원격 데스크톱 이벤트](../../02-artifacts/event-logs/rdp-event-logs/index.md) |
| 5 | 사용자 하이브의 실행 흔적 | 그 계정의 세션에서 실행한 프로그램 | [UserAssist](../../02-artifacts/execution/userassist.md) · [BAM·DAM](../../02-artifacts/execution/background-activity-moderator.md) |
| 6 | 원격 제어 프로그램 흔적 | 화면을 다른 곳에서 조작했을 가능성 | [원격 제어 프로그램](../../02-artifacts/network/remote-access-tools/index.md) |
| 7 | 자동 로그온 설정 | 비밀번호 없이 그 계정으로 들어갈 수 있었는지 | [레지스트리 속 비밀번호 정보](../../02-artifacts/credentials/sam-security/index.md) |

## 계정은 SID 로 가립니다

보안 식별자 (Security Identifier, SID) 는 Windows 가 계정을 가리키는 값입니다. 사람을 가리키는 값이 아닙니다.

SID 는 계정이나 그룹을 만들 때 생기고, 운영체제는 안에서 계정을 이름이 아니라 SID 로 가리킵니다. 사람은 계정 이름으로 부릅니다[1]. 한 번 쓴 SID 는 지운 계정의 것까지 포함해 다른 사용자·그룹에 다시 쓰지 않으므로, 같은 사람이 계정을 지웠다가 새로 만들면 새 SID 를 받고 두 계정은 서로 다른 계정입니다[1]. 로컬 SAM 은 쓴 상대 식별자 (Relative Identifier, RID) 를 기록해 다시 쓰지 않습니다[1].

로컬 계정의 SID 는 그 컴퓨터의 LSA 가 만들어 레지스트리의 보안 영역에 다른 계정 정보와 함께 저장하고, 만든 컴퓨터 안에서 고유합니다[1]. 다른 PC 에 이름이 같은 로컬 계정이 있어도 같은 계정으로 보지 않습니다. 도메인 계정의 SID 는 Active Directory 사용자 개체의 objectSID 속성에 저장하며, 사용자가 다른 도메인으로 옮기면 새 SID 를 받고 옛 SID 는 SIDHistory 속성에 남습니다[1].

**문자열 표기.** SID 는 `S-R-X-Y1-Y2-…-Yn` 으로 씁니다[1]. R 은 개정, X 는 식별자 기관, Y 는 하위 기관 값입니다[1]. 마지막 값 Yn 이 RID 이고, 그 앞 값들이 도메인 식별자입니다[1]. 예를 들어 `S-1-5-21-1004336348-1177238915-682003330-512` 에서 `21-1004336348-1177238915-682003330` 이 도메인 식별자, `512` 가 RID 입니다[1]. 바이트 단위 형식은 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에 있습니다.

**기록에서 자주 만나는 SID.**

| SID | 이름 | 조사에서 뜻하는 것 |
|---|---|---|
| S-1-5-18 | System (LocalSystem) | 운영체제와 LocalSystem 으로 로그인하는 서비스가 씁니다[1]. 사람의 계정이 아닙니다. |
| S-1-5-19 · S-1-5-20 | LocalService · NetworkService | 서비스 계정입니다[1]. |
| S-1-5-4 | Interactive | 대화형으로 로그인한 사용자입니다[1]. 원격 데스크톱으로 로그인해도 토큰에 들어갑니다[1]. |
| S-1-5-14 | Remote Interactive Logon | 원격 데스크톱으로 로그인한 사용자입니다[1]. 이 SID 가 있는 토큰에는 Interactive SID 도 있습니다[1]. |
| S-1-5-5-X-Y | Logon Session | 로그인 세션마다 X·Y 가 다릅니다[1]. |
| S-1-0-0 | Null SID | SID 값을 모를 때 흔히 씁니다[1]. |
| RID 500 | Administrator | 운영체제를 설치할 때 처음 만드는 계정입니다[1]. 이름을 바꿀 수 있습니다[1]. |
| RID 501 | Guest | 실제 계정이며 대화형 로그인이 됩니다[1]. 비밀번호가 없어도 되지만 걸 수는 있습니다[1]. |
| S-1-5-32-544 · 545 · 555 | Administrators · Users · Remote Desktop Users | 그룹의 SID 입니다[1]. 사람 한 명을 가리키지 않습니다. |

사용자가 로그인할 때마다 시스템은 액세스 토큰을 만들고, 토큰에는 사용자 SID 와 사용자가 속한 그룹의 SID 가 들어갑니다[1]. 그래서 Interactive SID 만으로는 PC 앞에서 로그인했는지 원격으로 로그인했는지 가릴 수 없습니다. Remote Interactive Logon SID 가 함께 있는지 봅니다.

## 계정과 프로필을 짝짓기

- 프로필 폴더와 SID 의 짝은 [사용자 프로필 목록](../../02-artifacts/system-account/profilelist.md) 에서 읽습니다.
- 사용자 하이브(NTUSER.DAT)에 남은 기록은 그 SID 의 프로필에 속합니다. 이름이 아니라 SID 로 묶습니다.

로컬 계정을 만든 시각은 레지스트리에 직접 적혀 있지 않습니다. 흔히 그 SID 의 NTUSER.DAT 파일 생성 시각($STANDARD_INFORMATION)으로 추정하고, NTUSER.DAT 가 없으면 OS 설치 시각을 씁니다. 이 값은 추정값이므로 보고서에 추정값이라고 밝힙니다.

- 계정 생성 이벤트가 남아 있으면 [계정 생성·변경](../../02-artifacts/event-logs/account-management-events.md) 으로 확인합니다.

## 그 시각의 세션 찾기

- 로그온·로그오프 이벤트로 조사 시각 앞뒤에 열린 세션을 찾습니다. 한 세션의 시작과 끝을 잇는 법과 로그온 유형의 뜻은 [로그온·로그오프](../../02-artifacts/event-logs/logon-events/index.md) 에 있습니다.
- 세션 안의 잠금·해제, 화면 보호기, 원격 세션 다시 연결·끊김 이벤트는 [PC 사용 시간 재구성](system-usage-time.md) 의 "로그온·잠금·원격 세션" 절에 정리했습니다.
- 같은 감사 하위 범주에는 무선·유선 네트워크 인증 요청 이벤트인 5632·5633 도 있고, 이 이벤트의 계정은 사용자 계정일 수도, 컴퓨터 계정일 수도 있습니다[2].
- 원격 데스크톱으로 들어온 세션은 [원격 데스크톱 이벤트](../../02-artifacts/event-logs/rdp-event-logs/index.md) 와 [원격 데스크톱 침입 확인](../incident/rdp-intrusion.md) 을 따라 접속한 곳을 확인합니다.
- 화면을 원격으로 넘겨받는 프로그램이 있었다면, PC 앞에서 연 세션이라도 PC 앞의 사람이 조작했다고 단정할 수 없습니다. [원격 제어 프로그램으로 누가 조작했나](../incident/remote-access-tool-abuse.md) 를 봅니다.

## 계정에서 사람으로

PC 안의 기록은 계정까지만 가리킵니다. 사람으로 좁히려면 계정을 쓸 수 있었던 사람을 줄여 가야 합니다.

- **다른 사람도 들어갈 수 있었나.** 자동 로그온 설정이 있었다면 PC 를 켠 사람 누구나 그 계정으로 들어갈 수 있었습니다. Guest 처럼 비밀번호 없는 계정이 켜져 있었는지도 봅니다.
- **같은 시간대에 다른 세션이 있었나.** 다른 계정의 세션이 함께 열려 있었으면 행위가 어느 세션에서 일어났는지부터 가립니다.
- **세션 안에 그 사람만 쓰는 것이 있었나.** 같은 세션에서 개인 메일·메신저 계정에 로그인한 흔적이 있으면 사람을 좁히는 단서가 됩니다. [누구와 연락을 주고받았나](communication-reconstruction.md) 를 봅니다.
- **PC 밖의 기록과 맞나.** 출입 기록, 근무 기록, 다른 기기의 기록처럼 PC 밖의 자료와 시각을 맞춰 봅니다.
- **계정을 탈취당했을 가능성은 없나.** 낯선 곳에서 들어온 로그온이 있으면 [계정 탈취와 측면 이동](../incident/credential-theft-lateral-movement/index.md) 을 봅니다.

## 분석 흐름

1. 계정 목록을 SID 로 정리합니다. 이름을 바꾼 계정, 지웠다가 다시 만든 계정이 있는지 SID 로 확인합니다.
2. 도메인 가입 여부를 확인합니다. 도메인 계정이면 Active Directory 쪽 기록을 따로 요청합니다.
3. 조사할 행위의 기록에서 SID 를 뽑습니다. 사용자 하이브의 기록이면 그 하이브의 SID 입니다.
4. 조사 시각 앞뒤로 그 SID 의 로그온 세션을 찾습니다. 로그온 유형으로 PC 앞의 세션인지 원격 세션인지 가립니다.
5. 세션 안의 잠금·해제와 원격 세션 이벤트로, 조사 시각에 화면이 잠겨 있었는지와 원격으로 이어져 있었는지 확인합니다.
6. 같은 시간대에 다른 계정의 세션이 있었는지 봅니다.
7. 그 세션의 실행 흔적(UserAssist·BAM)과 개인 계정 로그인 흔적을 모읍니다.
8. 자동 로그온 설정, 비밀번호 없는 계정, 원격 제어 프로그램 흔적을 확인합니다.
9. 모든 시각을 UTC 로 맞춰 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올리고 PC 밖의 기록과 맞춥니다.
10. 보고서에는 계정을 두고 내린 결론과 사람을 두고 내린 결론을 나눠 씁니다.

## 흔한 오판

1. **계정 이름을 사람 이름으로 씁니다.** 기록은 계정을 가리킵니다. 사람은 다른 기록으로 좁힙니다.
2. **계정 이름으로 기록을 묶습니다.** 지웠다가 다시 만든 계정은 이름이 같아도 SID 가 다릅니다[1]. SID 로 묶습니다.
3. **"Administrator" 라는 이름만 찾습니다.** RID 500 계정은 이름을 바꿀 수 있습니다[1]. RID 로 찾습니다.
4. **S-1-5-18 의 기록을 사용자 행위로 봅니다.** 이 SID 는 운영체제와 LocalSystem 서비스가 씁니다[1].
5. **Interactive SID 가 있으니 PC 앞에서 로그인했다고 봅니다.** 원격 데스크톱으로 로그인해도 Interactive SID 가 토큰에 들어갑니다[1].
6. **NTUSER.DAT 생성 시각을 계정을 만든 시각으로 단정합니다.** 이 값은 추정값입니다.
7. **5632·5633 의 계정을 사람의 계정으로 봅니다.** 컴퓨터 계정일 수도 있습니다[2].
8. **세션이 열려 있었으니 그 사람이 PC 앞에 있었다고 봅니다.** 화면이 잠겨 있었을 수 있고, 원격 제어 프로그램이 조작했을 수도 있습니다.

## 보고서 문장 예

- 쓰지 않을 문장: "○○ 시각에 피조사자가 이 PC 를 사용했습니다."
- 쓸 문장: "○○(UTC) 앞뒤로 SID `S-1-5-21-○○-○○○○` 계정(이름 ○○)의 대화형 세션이 열려 있었습니다. 이 세션에서 ○○(UTC)에 잠금 해제 이벤트(4801)가 있습니다. 같은 시간대에 다른 계정의 세션은 없습니다. 이 기록은 해당 시각에 이 계정의 세션에서 작업이 있었음을 보여 줍니다. 이 계정을 쓴 사람은 PC 기록만으로 정할 수 없습니다. 이 계정의 비밀번호를 아는 사람이 누구인지는 따로 확인해야 합니다."

## 함께 볼 페이지

- [사용자 계정](../../02-artifacts/system-account/sam.md) · [사용자 프로필 목록](../../02-artifacts/system-account/profilelist.md) — 계정과 SID, 프로필 폴더입니다.
- [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) — SID 의 바이트 형식입니다.
- [로그온·로그오프](../../02-artifacts/event-logs/logon-events/index.md) — 세션을 잇는 법과 로그온 유형입니다.
- [PC 사용 시간 재구성](system-usage-time.md) — 켜짐·꺼짐과 잠금·원격 세션 구간입니다.
- [원격 데스크톱 침입 확인](../incident/rdp-intrusion.md) · [원격 제어 프로그램으로 누가 조작했나](../incident/remote-access-tool-abuse.md) — 다른 곳에서 조작한 경우입니다.
- [계정 탈취와 측면 이동](../incident/credential-theft-lateral-movement/index.md) — 계정을 빼앗긴 경우입니다.

## 참고 문헌

1. Microsoft Learn, "Security Identifiers" (2025-06-26, 갱신 2026-02-16) — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers
2. Microsoft Learn, "Audit Other Logon/Logoff Events" (Windows 10 보관 문서, 2021-09-06, 갱신 2026-04-27) — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-other-logonlogoff-events
