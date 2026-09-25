---
title: "계정 생성·변경"
parent: "아티팩트 · 이벤트 로그"
nav_order: 2670
---

# 계정 생성·변경 (Account Management Events)

## 한 줄 요약

사용자 계정을 만들거나 바꾸거나 지우면 보안 로그 (Security) 에 계정 관리 이벤트가 남습니다. 4720 은 계정을 만든 기록이고, 4738 은 계정을 바꾼 기록입니다. 보안 로컬 그룹에 구성원을 넣으면 4732 가 남습니다. 이벤트마다 대상 계정 (Target) 과 작업한 계정 (Subject) 이 따로 적힙니다. 감사 하위 범주 Audit User Account Management 와 Audit Security Group Management 를 켜야 남습니다.

## 무엇을 기록하나 · 왜 생기나

### 사용자 계정 관리 (Audit User Account Management)

이 하위 범주는 사용자 계정에 생기는 다음 일을 감사합니다.

- 계정 만들기·바꾸기·삭제·이름 바꾸기
- 계정 사용·사용 안 함, 잠김·잠김 해제
- 비밀번호 설정·변경
- SID History 추가와 추가 실패
- DSRM 비밀번호 설정
- 관리자 계정의 권한 변경
- 로컬 그룹 구성원 조회
- 자격 증명 관리자 백업·복원

Microsoft 는 이 하위 범주의 이벤트 양을 Low 로 적었습니다.

| ID | 뜻 | 성공 (S) · 실패 (F) |
|---|---|---|
| 4720 | 사용자 계정 만들어짐 | S |
| 4722 | 계정 사용 | S |
| 4723 | 비밀번호 변경 시도 | S, F |
| 4724 | 비밀번호 재설정 시도 | S, F |
| 4725 | 계정 사용 안 함 | S |
| 4726 | 계정 삭제 | S |
| 4738 | 계정 변경 | S |
| 4740 | 계정 잠김 | S |
| 4765 | SID History 추가 | S |
| 4766 | SID History 추가 실패 | F |
| 4767 | 계정 잠김 해제 | S |
| 4780 | 관리자 그룹 구성원 계정에 ACL 설정 | S |
| 4781 | 계정 이름 바뀜 | S |
| 4794 | DSRM 관리자 비밀번호 설정 시도 | S, F |
| 4798 | 사용자의 로컬 그룹 구성원 조회 | S |
| 5376 | 자격 증명 관리자 백업 | S |
| 5377 | 자격 증명 관리자 복원 | S |

4722·4725·4724·4781 같은 일부 이벤트는 컴퓨터 계정에도 생깁니다.

### 보안 그룹 관리 (Audit Security Group Management)

4732 "A member was added to a security-enabled local group." 은 보안 로컬 그룹에 구성원이 더해질 때마다 생기며, 감사 하위 범주는 Audit Security Group Management 입니다.

같은 공급자 매니페스트에는 다음 그룹 이벤트도 있습니다.

| 그룹 종류 | 만들어짐 | 구성원 추가 | 구성원 제거 | 삭제 | 변경 | 구성원 조회 |
|---|---|---|---|---|---|---|
| 보안 로컬 그룹 | 4731 | 4732 | 4733 | 4734 | 4735 | 4799 |
| 전역 그룹 | | 4728 | 4729 | | | |
| 유니버설 그룹 | | 4756 | 4757 | | | |

4732 말고 다른 그룹 이벤트의 감사 하위 범주는 이번에 문서로 확인하지 않았습니다.

### 이 기록이 필요한 까닭

로컬 계정을 만든 시각은 레지스트리에 직접 적혀 있지 않아서 다른 흔적으로 추정해야 합니다. 추정 방법은 [사용자 계정](../system-account/sam.md)에서 다룹니다. 4720 이 남아 있으면 계정을 만든 때를 이벤트 기록 시각으로 바로 알 수 있습니다. 이 비교는 해석입니다.

## 위치와 버전별 차이

| 이벤트 | 감사 하위 범주 | 최소 Windows | 이벤트 버전 |
|---|---|---|---|
| 4720 | Audit User Account Management | Windows Vista · Windows Server 2008 | 0. 한 PC 의 매니페스트에도 버전 0 하나뿐이었습니다 |
| 4732 | Audit Security Group Management | Windows Vista · Windows Server 2008 | 문서는 0. 매니페스트에는 버전 1 도 있습니다 |

4720 과 4732 는 도메인 컨트롤러·멤버 서버·워크스테이션 모두에서 생깁니다. 4732·4728·4756 의 버전 1 은 MembershipExpirationTime 칸을 더합니다 (Windows 11 25H2 기준). 4732 버전 1 이 어느 Windows 버전부터 쓰였는지는 판마다 다를 수 있습니다.

Windows XP · 2003 의 계정 이벤트는 이번에 확인하지 못했습니다. 옛 로그 형식은 [구형 EVT 형식 (Windows XP·2003)](../../01-foundations/database-log-formats/evtx-evt-etl/windows-xp-2003.md)에서 다룹니다.

### 권장 설정

Microsoft 는 도메인 컨트롤러·멤버 서버·워크스테이션 모두에서 Audit User Account Management 의 성공과 실패를 켜라고 권합니다. 워크스테이션과 멤버 서버에서는 로컬 계정의 모든 변경을, 특히 기본 제공 Administrator 계정의 변경을 살피라고 적었습니다.

### 한 PC 의 설정

한 PC 에서 읽은 결과는 다음과 같습니다.

User Account Management `{0CCE9235-69AE-11D9-BED3-505054503030}` 와 Security Group Management `{0CCE9237-69AE-11D9-BED3-505054503030}` 는 둘 다 성공 (Success) 이었습니다. 이 값이 Windows 11 의 기본값인지는 확인하지 못했습니다. 보안 로그에는 약 2일치만 남아 있었고, 그 안에 4720·4722·4724·4726·4732 는 0건, 4738 은 4건이었습니다.

감사 설정과 로그 크기를 확인하는 방법은 [감사 정책과 로그 설정](audit-policy-log-settings.md)에서 다룹니다.

## 구조

### 4720 칸

| 무리 | XML 칸 | 읽을 때 주의 |
|---|---|---|
| 새 계정 | TargetUserName, TargetDomainName, TargetSid | 로컬 계정이면 TargetDomainName 에 컴퓨터 이름이 들어갑니다 |
| 만든 계정 | SubjectUserSid, SubjectUserName, SubjectDomainName, SubjectLogonId | 계정입니다. 사람이 아닙니다 |
| 권한 | PrivilegeList | |
| 계정 속성 | SamAccountName, DisplayName, UserPrincipalName, HomeDirectory, HomePath, ScriptPath, ProfilePath, UserWorkstations, PasswordLastSet, AccountExpires, PrimaryGroupId, AllowedToDelegateTo, OldUacValue, NewUacValue, UserAccountControl, UserParameters, SidHistory, LogonHours | 만들 때의 값입니다 |

로컬 계정을 만들 때 흔히 보이는 값은 다음과 같습니다.

| 칸 (화면 이름) | 흔한 값 |
|---|---|
| Display Name · Home Directory · Script Path · Profile Path | `<value not set>` |
| User Principal Name | `-` |
| Logon Hours | All. 새 도메인 계정이면 `<value not set>` 입니다 |
| Old UAC Value | 새 계정이면 항상 `0x0` |
| Primary Group ID | 보통 513. 도메인에서는 Domain Users, 로컬에서는 Users 입니다 |
| Account Expires | 손으로 만든 로컬·도메인 계정이면 보통 `<never>` |
| Password Last Set | 도메인 관리 콘솔에서 손으로 만든 계정이면 보통 `<never>`. 문서는 로컬 계정을 따로 적지 않았습니다 |

- New UAC Value 는 SAM 쪽 계정 플래그 값입니다. 액티브 디렉터리의 userAccountControl 과 정의가 다릅니다.
- 로그온 ID 로 만든 계정의 세션을 잇는 방법은 [로그온 세션 잇기](logon-events/logon-id-4624-4634-4647.md)에서 다룹니다.

### 메시지 번호

XML 에는 `%%1794` 꼴의 값이 들어갑니다. 이 번호는 메시지 파일의 문구를 가리킵니다. 한 PC 의 msobjs.dll 메시지 표에서 읽은 문구는 다음과 같습니다.

| 번호 | 문구 |
|---|---|
| `%%1793` | `<value not set>` |
| `%%1794` | `<never>` |
| `%%2080` | Account Disabled |
| `%%2082` | 'Password Not Required' - Enabled |
| `%%2084` | 'Normal Account' - Enabled |
| `%%2089` | 'Don't Expire Password' - Enabled |
| `%%2090` | Account Locked |
| `%%2093` | 'Trusted For Delegation' - Enabled |

메시지 파일을 읽는 방법은 [공급자와 메시지 파일](../../01-foundations/database-log-formats/evtx-evt-etl/provider-message-table.md)에서 다룹니다.

### Microsoft 예시

Microsoft 문서의 4720 예시 가운데 일부입니다. 문서가 보여 주는 예시이며 검체에서 나온 값이 아닙니다. 예시의 새 계정은 도메인 계정입니다.

| 항목 | 값 |
|---|---|
| EventID · Version | 4720 · 0 |
| Task · Keywords | 13824 · `0x8020000000000000` |
| Channel | Security |
| PasswordLastSet · AccountExpires | `%%1794` |
| LogonHours | `%%1793` |
| NewUacValue | `0x15` |
| UserAccountControl | `%%2080 %%2082 %%2084` |

예시 XML 의 LogonHours 값 `%%1793` 은 메시지 표에서 `<value not set>` 입니다. 문서는 새 도메인 계정이면 Logon Hours 가 `<value not set>`, 새 로컬 계정이면 "All" 이라고 적었습니다. 도메인 계정 예시이므로 설명과 맞습니다. Logon Hours 값을 읽을 때는 로컬 계정인지 도메인 계정인지 먼저 가립니다.

### 다른 사용자 계정 이벤트의 칸

아래 표는 한 PC 의 공급자 매니페스트에서 읽었습니다.

| ID | 칸 |
|---|---|
| 4722 · 4725 · 4724 · 4740 · 4767 | TargetUserName, TargetDomainName, TargetSid, Subject 네 칸 |
| 4723 · 4726 | 위 칸 + PrivilegeList |
| 4738 | 맨 앞에 Dummy 칸이 있고, 그 뒤는 4720 과 같은 속성 칸 목록 |
| 4781 | OldTargetUserName, NewTargetUserName, TargetDomainName, TargetSid, Subject 네 칸, PrivilegeList |
| 4798 | Target 세 칸, Subject 네 칸, CallerProcessId, CallerProcessName |

### 4732 칸

| XML 칸 | 뜻 | 읽을 때 주의 |
|---|---|---|
| MemberName | 더해진 구성원의 고유 이름 (DN, 예: `CN=○○,CN=Users,DC=○○`) | 로컬 그룹이면 보통 `-` 입니다. 새 구성원이 도메인 계정이어도 그렇습니다 |
| MemberSid | 더해진 구성원 SID | 누가 더해졌는지는 이 칸으로 봅니다 |
| TargetUserName | 그룹 이름 | 더해진 계정이 아닙니다 |
| TargetDomainName | 그룹 도메인 | 기본 제공 그룹이면 `Builtin` 입니다 |
| TargetSid | 그룹 SID | |
| SubjectUserSid · SubjectUserName · SubjectDomainName · SubjectLogonId | 구성원을 더한 계정 | |
| PrivilegeList | 권한 | |

구성원 하나마다 4732 가 따로 생기고, 그 앞에는 아무것도 바뀌지 않은 4735 "A security-enabled local group was changed." 가 보통 먼저 보입니다. Microsoft 문서 예시의 4732 는 Version 0, Task 13826, Keywords `0x8020000000000000` 입니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 기록 시각에 이 이름·SID 의 계정이 만들어졌다는 것 (4720) | 그 요청을 한 계정 뒤에 있던 사람이 누구인지 |
| 계정을 만든 요청이 어느 계정·로그온 세션에서 왔는지 (4720 의 Subject) | 어떤 프로그램으로 만들었는지. 4720 칸 목록에 프로그램 칸이 없습니다 |
| 만들 때의 계정 속성과 플래그 (4720) | 만든 계정으로 그 뒤에 로그온했는지 (4624 에서 따로 봅니다) |
| 기록 시각에 계정 속성이 바뀌었다는 것 (4738) | 감사가 꺼져 있던 기간이나 로그가 밀려난 기간에 계정 변경이 없었다는 것 |
| 이 SID 의 계정이 이 그룹에 더해졌다는 것 (4732) | 더해진 계정이 그 권한을 실제로 썼는지 |

### 살펴볼 값

Microsoft 는 4720 에서 다음 값을 살피라고 권합니다.

- SAM Account Name 이 비었거나 `-` 입니다.
- Password Last Set 이 미래 시각입니다.
- Account Expires 가 `<never>` 가 아닙니다.
- Primary Group ID 가 513 이 아닙니다.
- Old UAC Value 가 `0x0` 이 아닙니다.
- SID History 가 `-` 가 아닙니다.
- 'Don't Expire Password' 가 켜져 있습니다.

4732 에서는 기본 제공 로컬 Administrators 그룹, Domain Admins, Enterprise Admins 같은 중요 그룹에 구성원이 더해지는지 살피라고 권합니다.

### 보고서 문장

- 쓸 수 있는 문장: "보안 로그에 ○○(UTC) 의 4720 이 있습니다. 새 계정은 ○○ (SID ○○) 입니다. Subject 는 ○○\○○ 이고 로그온 ID 는 ○○ 입니다. ○○(UTC) 의 4732 에서 MemberSid 가 이 SID 이고 그룹 이름은 ○○ 입니다."
- 쓰면 안 되는 문장: "사용자 ○○가 몰래 관리자 계정을 만들었다."

두 번째 문장은 기록에 없는 사람과 의도를 적고 있습니다. 로그온 ID 로 세션을 잇고, 그 세션의 다른 기록을 따로 적습니다.

## 시각 해석

- 4720 의 기록 시각은 계정이 만들어진 때이고, 4738 은 계정이 바뀐 때, 4732 는 구성원이 더해진 때입니다.
- 4720 의 PasswordLastSet 칸은 이벤트 시각과 따로 적힌 값이며, Microsoft 는 이 값이 미래 시각이면 살피라고 권합니다.
- 레코드의 기록 시각을 저장하는 형식은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.
- 여러 기록의 시각을 한 기준으로 맞추는 방법은 [시간대·시계 오차 보정](../../03-techniques/analysis/timeline/time-normalization.md)에서 다룹니다.
- 보안 로그는 크기 한도에 이르면 오래된 기록부터 밀려납니다. 한 PC 에서는 약 2일치만 남아 있었습니다. 오래전에 만든 계정의 4720 은 남아 있지 않을 때가 많습니다.

## 함정과 한계

1. **4732 의 TargetUserName 을 더해진 계정으로 읽습니다.** 이 칸은 그룹 이름입니다. 더해진 계정은 MemberSid 로 봅니다.
2. **MemberName 이 `-` 라서 구성원을 모른다고 봅니다.** 로컬 그룹이면 MemberName 은 보통 `-` 입니다. MemberSid 를 [사용자 프로필 목록](../system-account/profilelist.md)이나 다른 이벤트의 SID 와 맞춥니다.
3. **4735 하나를 그룹 조작으로 봅니다.** 4732 앞에는 아무것도 바뀌지 않은 4735 가 보통 먼저 보입니다.
4. **4738 이 있으면 사람이 계정을 바꿨다고 봅니다.** 한 PC 의 4738 4건은 모두 Subject 가 S-1-5-18 (SYSTEM) 이었습니다. 대상은 RID 1001 계정이었습니다. `-` 가 아닌 속성 칸은 DisplayName 하나였고, Old·New UAC 는 `-` 였습니다. 사용자 조작 없이 SYSTEM 이 표시 이름을 바꾼 기록으로 보입니다. 원인은 확인하지 못했습니다.
5. **4720 과 함께 4722·4738 이 반드시 남는다고 봅니다.** 계정을 만들 때 4722·4738 이 함께 남는다는 설명이 있습니다. 4720 문서에는 이 내용이 없었습니다. 검체에서 직접 확인합니다.
6. **New UAC Value 를 액티브 디렉터리 기준으로 풉니다.** 이 값은 SAM 쪽 계정 플래그입니다. userAccountControl 과 정의가 다릅니다.
7. **컴퓨터 계정의 기록을 사용자 계정으로 읽습니다.** 4722·4725·4724·4781 같은 이벤트는 컴퓨터 계정에도 생깁니다. TargetSid 와 TargetUserName 으로 어떤 계정인지 먼저 가립니다.
8. **분석 PC 의 매니페스트를 검체에 그대로 씁니다.** 검체의 Windows 버전이 다르면 이벤트 버전과 칸 구성이 다를 수 있습니다. 레코드의 Version 값을 먼저 봅니다.

### 지우기와 조작

- **계정을 지웁니다.** 감사가 켜져 있었다면 4726 이 남습니다. 계정이 SAM 에서 사라져도 이미 남은 4720·4726 은 보안 로그에 그대로 있습니다. 이 판단은 두 기록이 다른 곳에 저장된다는 점에서 나온 해석입니다.
- **계정 이름을 바꿉니다.** 4781 에 옛 이름과 새 이름이 함께 남습니다. 여러 이벤트는 이름 대신 TargetSid 로 묶어 봅니다.
- **로그를 지웁니다.** 보안 로그를 지우면 1102 가 남습니다. [이벤트 로그 삭제 (1102·104)](1102-104.md)를 봅니다.
- **레코드 일부만 남아 있습니다.** 지우거나 덮어쓴 레코드가 파일 안에 남아 있을 수 있습니다. [파일 안에 남은 지운·손상 레코드](../../01-foundations/database-log-formats/evtx-evt-etl/chunk-slack-corrupted-evtx.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

Microsoft 예시의 NewUacValue `0x15` 를 손으로 풀어 봅니다. 이 값은 문서 예시이며 검체에서 나온 값이 아닙니다.

```
0x15 = 0001 0101 (2진)
     = 0x10 + 0x04 + 0x01
```

1. 2진으로 바꾸면 켜진 비트가 세 개입니다.
2. 세 비트의 값은 0x01, 0x04, 0x10 입니다.
3. 같은 예시의 UserAccountControl 에는 `%%2080 %%2082 %%2084` 세 문구가 있습니다.
4. 메시지 표에서 세 문구는 Account Disabled, 'Password Not Required' - Enabled, 'Normal Account' - Enabled 입니다.
5. 4720 문서는 이 값의 비트 목록을 [MS-SAMR] USER_ACCOUNT Codes 로 안내합니다. 그 표에서 0x01 은 USER_ACCOUNT_DISABLED, 0x04 는 USER_PASSWORD_NOT_REQUIRED, 0x10 은 USER_NORMAL_ACCOUNT 입니다.
6. 세 비트의 뜻이 세 문구와 하나씩 맞습니다.

이 값은 SAM 쪽 플래그이므로 액티브 디렉터리 표로 풀지 않습니다. 같은 표에서 0x200 은 USER_DONT_EXPIRE_PASSWORD 입니다. SAM 하이브의 계정 플래그는 [사용자 계정](../system-account/sam.md)에서 다룹니다.

> 그림 자리: 0x15 를 8비트 칸으로 펼치고, 켜진 비트 세 개에서 UserAccountControl 문구 세 개로 화살표를 그은 그림

### 공개 도구로 한 번

Windows 에 들어 있는 이벤트 뷰어와 PowerShell 의 `Get-WinEvent` 로 볼 수 있습니다. 분석 PC 로 옮긴 파일은 `Path` 로 엽니다. 아래 `E:\case\` 는 예시 경로입니다.

```powershell
# 사용자 계정과 로컬 그룹 이벤트
$ids = 4720, 4722, 4723, 4724, 4725, 4726, 4738, 4740, 4767, 4781, 4731, 4732, 4733, 4734, 4735
Get-WinEvent -FilterHashtable @{ Path = 'E:\case\Security.evtx'; Id = $ids }

# 4732 에서 그룹과 더해진 구성원 SID 꺼내기
Get-WinEvent -FilterHashtable @{ Path = 'E:\case\Security.evtx'; Id = 4732 } | ForEach-Object {
  $d = @{}; ([xml]$_.ToXml()).Event.EventData.Data | ForEach-Object { $d[$_.Name] = $_.'#text' }
  [pscustomobject]@{ Time = $_.TimeCreated; Group = $d.TargetUserName; MemberSid = $d.MemberSid; By = $d.SubjectUserName; LogonId = $d.SubjectLogonId }
}
```

칸 구성은 공급자 매니페스트에서 확인할 수 있습니다.

```powershell
(Get-WinEvent -ListProvider Microsoft-Windows-Security-Auditing).Events |
  Where-Object Id -in 4720, 4738, 4732 | Select-Object Id, Version, Template
```

이 명령은 분석 PC 의 매니페스트를 읽습니다. 라이브 시스템의 감사 설정은 다음 두 명령으로 확인합니다.

```
auditpol /get /subcategory:{0CCE9235-69AE-11D9-BED3-505054503030} /r
auditpol /get /subcategory:{0CCE9237-69AE-11D9-BED3-505054503030} /r
```

도구가 `%%2080` 같은 번호를 문구로 바꿔 보여 주는지, 번호 그대로 보여 주는지 확인합니다. 레코드 한두 개는 XML 원문과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [사용자 계정](../system-account/sam.md) | 이벤트의 TargetSid 끝 값(RID)과 SAM 의 계정, 지금 남은 계정 플래그 |
| [사용자 프로필 목록](../system-account/profilelist.md) | 새 계정 SID 의 프로필 폴더가 생겼는지 |
| [로그온 세션 잇기](logon-events/logon-id-4624-4634-4647.md) | Subject 의 로그온 ID 와 같은 4624, 새 계정의 첫 로그온 |
| [명시적 자격 증명·특수 권한 (4648·4672)](logon-events/4648-4672.md) | 그룹에 더해진 계정이 그 뒤 특수 권한으로 로그온했는지 |
| [프로세스 생성 (4688)](4688.md) | 같은 로그온 ID 세션에서 계정을 만든 무렵 실행된 프로그램 |
| [레지스트리 속 비밀번호 정보](../credentials/sam-security/index.md) | 계정의 비밀번호 관련 값 |

조사 순서는 [새 계정을 만들거나 권한을 올렸나](../../04-scenarios/incident/credential-theft-lateral-movement/account-privilege.md)에서 다룹니다.

## 실습

**직접 만든 Windows 10·11 가상 머신**에서 해 봅니다. 각 단계의 시각을 적어 둡니다.

1. 위 `auditpol` 명령으로 두 하위 범주의 설정을 봅니다. 꺼져 있으면 `/set ... /success:enable /failure:enable` 로 켭니다.
2. 로컬 계정을 하나 만듭니다. 4720 의 속성 칸을 위 "흔한 값" 표와 비교합니다.
3. 같은 시각 무렵에 4722·4738 이 함께 남는지 봅니다. 이 페이지가 확인하지 못한 점입니다.
4. 그 계정을 Administrators 그룹에 넣습니다. 4735 와 4732 가 어떤 순서로 남는지, MemberName 이 `-` 인지 봅니다.
5. 계정 이름을 바꾸고 4781 을, 계정을 지우고 4726 을 봅니다. 모든 이벤트를 TargetSid 로 묶어 봅니다.
6. 새 계정으로 한 번 로그온한 뒤 NTUSER.DAT 의 생성 시각과 4720 의 시각을 비교합니다.

**NIST CFReDS 같은 공개 검체**에서는 다음을 풀어 봅니다.

1. 보안 로그에 4720 이 있습니까? 없다면 감사 설정과 로그가 남아 있는 기간부터 확인합니다.
2. 4732 에서 기본 제공 Administrators 그룹에 더해진 MemberSid 가 있습니까? 그 SID 는 SAM 의 어느 계정입니까?
3. 4738 의 Subject 가 SYSTEM 인 기록과 사용자 계정인 기록을 나눕니다. 각각 어떤 칸이 `-` 가 아닙니까?

## 참고 문헌

- Microsoft Learn, "4720(S) A user account was created." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4720
- Microsoft Learn, "Audit User Account Management" — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-user-account-management
- Microsoft Learn, "4732(S) A member was added to a security-enabled local group." — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4732
- Microsoft Learn, "[MS-SAMR]: USER_ACCOUNT Codes" — https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/b10cfda1-f24f-441b-8f43-80cb93e786ec
