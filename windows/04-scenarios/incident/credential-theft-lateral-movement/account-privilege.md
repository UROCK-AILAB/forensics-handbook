---
title: "새 계정을 만들거나 권한을 올렸나"
parent: "계정 탈취와 측면 이동"
grand_parent: "시나리오 · 침해 사고"
nav_order: 3760
---

# 새 계정을 만들거나 권한을 올렸나 (Account·Privilege)

이 페이지는 공격자가 계속 들어올 발판으로 계정을 새로 만들거나, 이미 있는 계정의 권한을 관리자급으로 올렸는지 확인하는 순서를 다룹니다. 계정·그룹 이벤트의 필드는 [계정 생성·변경](../../../02-artifacts/event-logs/account-management-events.md) 에서도 다루지만, 이 페이지는 그 이벤트를 침해 판단에 쓰는 방법을 다룹니다.

## 조사 질문

- 사고 무렵에 계정이 새로 만들어졌습니까?
- 이미 있는 계정이 Administrators 같은 중요 그룹에 들어갔습니까?
- 누가(어느 계정으로) 그 일을 했고, 어느 시각입니까?
- 계정을 만들거나 그룹을 바꾸기 전에 계정·그룹을 조회한 흔적이 있습니까?

## 먼저 확인할 것

| 확인할 것 | 이유 |
|---|---|
| Windows 버전 | 이벤트 버전에 따라 필드가 다를 수 있습니다. Windows 11 Home(빌드 26200)의 4720 템플릿은 버전 0 입니다. |
| 시간대 | 이벤트·레지스트리·파일 시각을 같은 기준으로 맞춥니다([시간대 설정](../../../02-artifacts/system-account/time-zone.md)). |
| 로컬·도메인 구분 | 로컬 계정 이벤트는 그 PC 에, 도메인 계정 이벤트는 도메인 컨트롤러에 남습니다. |
| 감사 정책 | 계정 관리·그룹 관리 감사가 켜져 있어야 이 이벤트가 남습니다. 권장 표는 "권장"일 뿐이고 실제 기본값은 이미지에서 확인합니다[1]. |
| 수집 범위 | 보안 로그, SAM 하이브, 사용자 프로필(NTUSER.DAT)을 함께 확보합니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 계정 이벤트 (4720·4722·4724·4738 등) | 계정 생성·활성화·비밀번호 재설정·변경 | [계정 생성·변경](../../../02-artifacts/event-logs/account-management-events.md) |
| 2 | 그룹 이벤트 (4732·4728·4756 등) | 계정이 어느 그룹에 들어갔나 | 이 페이지 아래 |
| 3 | 특수 권한·명시적 자격 증명 (4672·4648) | 관리자급 권한 세션, 다른 계정 자격 증명 사용 | [명시적 자격 증명·특수 권한](../../../02-artifacts/event-logs/logon-events/4648-4672.md) |
| 4 | 조회 이벤트 (4798·4799) | 계정을 만들기 전 정찰 흔적 | 이 페이지 아래 |
| 5 | SAM 하이브·프로필 목록 | 계정 목록과 만들어진 시각 근거 | [사용자 계정 (SAM)](../../../02-artifacts/system-account/sam.md), [사용자 프로필 목록](../../../02-artifacts/system-account/profilelist.md) |

## 계정 이벤트 (계정 관리 감사)

계정 관리 감사(Audit User Account Management) 하위 범주가 남기는 이벤트입니다[1].

| 이벤트 | 뜻 |
|---|---|
| 4720 | 계정 생성 |
| 4722 | 계정 활성화 |
| 4723 | 비밀번호 변경 시도 |
| 4724 | 비밀번호 재설정 시도 |
| 4725 | 계정 비활성화 |
| 4726 | 계정 삭제 |
| 4738 | 계정 변경 |
| 4740 | 계정 잠김 |
| 4767 | 계정 잠금 해제 |
| 4781 | 계정 이름 변경 |
| 4798 | 사용자의 로컬 그룹 구성원 조회 |
| 5376·5377 | 자격 증명 관리자 백업·복원 |

- 4722·4724·4725·4781 같은 일부 이벤트는 컴퓨터 계정에도 생깁니다[1].
- 권장 설정은 도메인 컨트롤러·멤버 서버·워크스테이션 모두에서 성공·실패 감사를 켜는 것입니다[1]. 워크스테이션·멤버 서버에서는 로컬 계정, 특히 내장 Administrator 의 변경을 모두 봅니다[1]. 실제 설정은 이미지에서 확인합니다.
- 계정 잠김(4740)은 대입 공격 쪽에서도 봅니다. [비밀번호 대입 공격이 있었나](brute-force.md) 를 봅니다.

### 4720 (계정 생성) 읽기

Windows 11 Home(빌드 26200)의 4720 템플릿(버전 0)에는 아래 필드가 있습니다: TargetUserName, TargetDomainName, TargetSid, SubjectUserSid, SubjectUserName, SubjectDomainName, SubjectLogonId, SamAccountName, DisplayName, UserPrincipalName, HomeDirectory, ScriptPath, PasswordLastSet, AccountExpires, UserAccountControl, SidHistory 등.

- Target* 필드는 만들어진 계정이고, Subject* 필드는 만든 계정입니다.
- SubjectLogonId 로 만든 사람의 4624 로그온 세션과 잇습니다. Logon ID 로 세션을 잇는 방법은 [로그온 세션 잇기](../../../02-artifacts/event-logs/logon-events/logon-id-4624-4634-4647.md) 에 있습니다.
- 로컬 계정은 그 PC 에, 도메인 계정은 도메인 컨트롤러에 남는 것으로 보고 수집 대상을 정합니다. 어느 컴퓨터에 남는지 확실치 않으면 두 곳을 모두 봅니다.

## 그룹 이벤트 (그룹 관리 감사)

그룹 관리 감사(Audit Security Group Management) 하위 범주가 남기는 이벤트입니다[2].

| 그룹 종류 | 생성 | 구성원 추가 | 구성원 제거 | 삭제 | 변경 |
|---|---|---|---|---|---|
| 로컬 그룹 | 4731 | 4732 | 4733 | 4734 | 4735 |
| 전역 그룹 (도메인) | 4727 | 4728 | 4729 | 4730 | 4737 |
| 유니버설 그룹 (도메인) | 4754 | 4756 | 4757 | 4758 | 4755 |

- 로컬 그룹 조회는 4799 로 남습니다[2]. 이 하위 범주에는 실패 이벤트가 없고, 권장은 성공 감사 Yes, 실패 No 입니다[2]. 전역·유니버설 판은 필드·권장 사항이 로컬 판과 같고 그룹 종류만 다릅니다[2].

### 4732 (로컬 그룹에 구성원 추가) 읽기

관리자 그룹에 계정을 넣는 일은 4732 로 남고, 추가된 구성원마다 4732 가 하나씩 생깁니다[3].

- EventData 필드(예시 순서): MemberName, MemberSid, TargetUserName, TargetDomainName, TargetSid, SubjectUserSid, SubjectUserName, SubjectDomainName, SubjectLogonId, PrivilegeList[3].
- XML 의 TargetUserName·TargetSid 는 그룹입니다(화면의 Group 절)[3]. 이 필드를 추가된 계정으로 읽으면 안 됩니다.
- Member\Account Name(MemberName)은 추가된 계정의 DN 입니다. 로컬 그룹이면 새 구성원이 도메인 계정이어도 보통 "-" 입니다[3]. 그래서 누가 추가됐는지는 MemberSid 로 봅니다.
- Group Domain 필드는 로컬 그룹이면 그 컴퓨터 이름, 내장 그룹이면 "Builtin" 입니다[3].
- 4732 바로 앞에 아무것도 안 바뀐 4735(로컬 그룹 변경)가 흔히 보이며, 4735 하나만으로는 놀라지 않습니다.
- 내장 로컬 Administrators·Domain Admins·Enterprise Admins 같은 중요 그룹은 Group Name 으로 모두 봅니다[3]. 계정 종류와 그룹 용도가 안 맞는 추가(예: 컴퓨터 계정을 사용자용 그룹에)도 봅니다[3].

## 조회(정찰) 이벤트

계정을 만들거나 그룹을 바꾸기 전에 공격자가 계정·그룹을 살펴본 흔적이 남기도 합니다.

- 4798 "A user's local group membership was enumerated." 필드에는 CallerProcessId, CallerProcessName 이 있습니다.
- 4799 "A security-enabled local group membership was enumerated."[2].
- 4798 에는 조회한 프로세스 이름 필드가 있는데, 정상 프로그램도 조회하므로 프로세스 이름으로 구분합니다.

## 권한이 올라갔나

- 새 로그온 세션의 특수 권한은 4672 로, 관리자 권한 세션은 4624 의 관리자 권한 토큰(Elevated Token)으로 봅니다. [명시적 자격 증명·특수 권한](../../../02-artifacts/event-logs/logon-events/4648-4672.md) 과 [로그온 세션 잇기](../../../02-artifacts/event-logs/logon-events/logon-id-4624-4634-4647.md) 를 봅니다.
- 4732 로 Administrators 에 들어간 계정의 그 뒤 첫 4624·4672 를 이어 봅니다. 권한이 실제로 쓰였는지 봅니다.

## 레지스트리·파일 쪽

- 로컬 계정이 만들어진 시각은 레지스트리에 직접 적혀 있지 않습니다. 흔히 그 SID 의 NTUSER.DAT 생성 시각($STANDARD_INFORMATION)으로 추정합니다. NTUSER.DAT 가 없으면 OS 설치 시각을 씁니다. 보고서에는 추정값이라고 밝힙니다.
- 로그인한 적 없는 새 계정은 프로필(NTUSER.DAT)이 아직 없을 수 있습니다.
- 로컬 계정 목록은 SAM 하이브에 있습니다. [사용자 계정 (SAM)](../../../02-artifacts/system-account/sam.md) 과 [레지스트리 속 비밀번호 정보](../../../02-artifacts/credentials/sam-security/index.md) 를 봅니다.

## 분석 흐름

1. 시간대와 감사 정책을 먼저 정합니다. 계정·그룹 관리 감사가 그 기간에 켜져 있었는지 봅니다.
2. 4720·4722·4738 을 시각순으로 모읍니다. Target(만들어진 계정)과 Subject(만든 계정)를 표로 적습니다.
3. 4732·4728·4756 에서 중요 그룹(Administrators 등)에 들어간 계정을 찾습니다. Group Name 은 TargetUserName, 추가된 계정은 MemberSid 로 읽습니다.
4. 각 이벤트의 SubjectLogonId 로 만든 사람의 4624 세션을 찾습니다. 그 세션의 로그온 유형·원본 주소를 봅니다.
5. 앞선 4798·4799 조회 이벤트가 같은 세션에 있는지 봅니다.
6. 그룹에 들어간 계정의 그 뒤 첫 4624·4672 를 이어, 오른 권한이 쓰였는지 봅니다.
7. 계정이 새로 만들어졌으면 그 SID 의 NTUSER.DAT 생성 시각과 SAM 을 맞춰, 이벤트 시각과 어긋나지 않는지 봅니다.
8. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리합니다.

## 흔한 오판

1. **4732 의 TargetUserName 을 추가된 계정으로 봅니다.** 이 필드는 그룹입니다. 추가된 계정은 MemberSid 로 봅니다.
2. **MemberName 이 "-" 라 계정을 못 찾는다고 봅니다.** 로컬 그룹이면 도메인 계정이어도 이 필드가 "-" 일 수 있습니다[3]. MemberSid 로 계정을 찾습니다.
3. **4735 하나를 그룹 조작으로 봅니다.** 4732 앞에 아무것도 안 바뀐 4735 가 흔히 붙습니다[3].
4. **감사가 꺼져 있었는데 이벤트가 없으니 계정 변경도 없었다고 봅니다.** SAM 하이브·프로필로 계정 목록을 직접 확인합니다.
5. **NTUSER.DAT 생성 시각을 계정 생성 시각으로 단정합니다.** 이는 추정값이고, 로그인한 적 없는 계정은 프로필이 없을 수 있습니다. 이벤트·SAM 과 맞춰 봅니다.
6. **조회 이벤트를 곧 공격으로 봅니다.** 정상 프로그램도 계정·그룹을 조회합니다. CallerProcessName 으로 구분합니다.

## 보고서 문장 예

아래 값은 설명을 위해 만든 예입니다.

- 쓰지 않을 문장: "공격자가 백도어 계정을 만들어 관리자로 올렸습니다."
- 쓸 문장: "이 PC 의 Security.evtx 에는 ○○(UTC)에 TargetUserName ○○ 인 4720 이 있습니다. 그 계정을 만든 Subject 는 ○○, SubjectLogonId 는 ○○입니다. 같은 세션에서 ○○(UTC)에 Group Name Administrators, MemberSid 가 그 계정인 4732 가 있습니다. 이 계정의 SID 폴더 NTUSER.DAT 생성 시각은 ○○입니다. 이 기록은 계정 ○○이 만들어져 로컬 Administrators 그룹에 들어갔음을 보여 줍니다. 그 뒤 이 계정으로 무엇을 했는지는 이어지는 로그온·실행 기록으로 따로 봅니다."

## 함께 볼 페이지

- [계정 생성·변경](../../../02-artifacts/event-logs/account-management-events.md) — 계정·그룹 이벤트 목록과 필드입니다.
- [명시적 자격 증명·특수 권한 (4648·4672)](../../../02-artifacts/event-logs/logon-events/4648-4672.md) · [로그온 세션 잇기](../../../02-artifacts/event-logs/logon-events/logon-id-4624-4634-4647.md) — 오른 권한이 쓰인 세션을 잇습니다.
- [사용자 계정 (SAM)](../../../02-artifacts/system-account/sam.md) · [사용자 프로필 목록](../../../02-artifacts/system-account/profilelist.md) · [레지스트리 속 비밀번호 정보](../../../02-artifacts/credentials/sam-security/index.md) — 계정 목록과 만들어진 시각 근거입니다.
- [이벤트 로그 삭제 (1102·104)](../../../02-artifacts/event-logs/1102-104.md) — 계정 변경 흔적을 지운 흔적입니다.
- [감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md) — 이 이벤트가 남을 조건입니다.
- [비밀번호 대입 공격이 있었나](brute-force.md) · [다른 PC 에서 원격 실행했나](psexec-wmi-winrm.md) — 앞선 단계입니다.

## 참고 문헌

1. Microsoft Learn, "Audit User Account Management" — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-user-account-management
2. Microsoft Learn, "Audit Security Group Management" — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-security-group-management
3. Microsoft Learn, "4732(S) A member was added to a security-enabled local group." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4732
