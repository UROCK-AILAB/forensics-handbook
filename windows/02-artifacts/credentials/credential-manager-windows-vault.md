# 자격 증명 관리자와 볼트 (Credential Manager·Windows Vault)

## 한 줄 요약

Windows 는 사용자가 저장한 웹·앱·네트워크 자격 증명을 사용자 프로필 아래 암호화된 폴더에 담습니다. 자격 증명 관리자 (Credential Manager) 가 이 자격 증명을 관리하고, Microsoft 설명서는 저장 영역을 Windows 볼트 (Windows Vault) 라고 부릅니다. 파일은 DPAPI 로 감싸여 있다고 널리 알려져 있으나, 이번에 연 Microsoft 자료는 "암호화된 특수 폴더"라고만 밝힙니다.

## 무엇을 기록하나 · 왜 생기나

사용자가 웹사이트나 앱, 네트워크 자원에서 사용자 이름과 비밀번호를 저장하면 그 자격 증명이 로컬 컴퓨터의 저장 영역에 남습니다. Microsoft 설명서는 이 저장 영역을 Credential Locker 라고 부르고, 자격 증명 관리자가 이를 관리한다고 밝힙니다. 사용자는 제어판의 자격 증명 관리자로 저장 영역에 접근합니다.

저장 영역은 두 보관함으로 나뉩니다.

- 웹 자격 증명 — Internet Explorer 와 Microsoft Edge 가 씁니다 (MITRE ATT&CK 설명 기준).
- Windows 자격 증명 — 앱과 네트워크 인증이 씁니다.

자격 증명은 다음과 같은 때에 저장됩니다.

- NTLM·Kerberos 인증을 요구하는 사이트·앱·컴퓨터에서 "기본 자격 증명 업데이트"나 "암호 저장"을 고를 때 남습니다.
- 저장된 자격 증명이 거부되고 새 자격 증명으로 접근이 되면 옛 것을 새 것으로 덮어씁니다.
- Internet Explorer 10 은 로그인이 필요한 사이트의 자격 증명을 이 저장 영역에서 찾습니다.

DPAPI 구조 자체는 [DPAPI 구조](/01-foundations/protection/data-protection-api/index.md) 에서 다룹니다. 이 페이지는 볼트의 위치·구조·시각·탐지만 다룹니다.

## 위치와 버전별 차이

### 파일 위치

| 경로 | 담긴 것 | 근거 |
|---|---|---|
| `%LocalAppData%\Microsoft\Vault\` | 암호화된 자격 증명 파일 | MITRE ATT&CK T1555.004 |
| `%LocalAppData%\Microsoft\Credentials\` | 암호화된 자격 증명 파일 | MITRE ATT&CK T1555.004 |

- `Vault` 폴더에는 `.vcrd` 파일과 `.vpol` 파일이 있습니다. `.vcrd` 는 암호화된 자격 증명, `.vpol` 은 암호화 키를 담습니다.
- 파일은 사용자 프로필 아래 암호화된 특수 폴더에 들어 있습니다. Microsoft 설명서는 이 폴더가 암호화되어 있다고만 밝힙니다.
- Roaming 프로필의 자격 증명 폴더 경로, 시스템 계정 (systemprofile) 쪽 경로, `%ProgramData%\Microsoft\Vault` 경로는 확인하지 못했습니다.
- MITRE ATT&CK T1555.004 는 암호화 키가 `Policy.vpol` 이라는 파일에 있고, 보통 자격 증명 파일과 같은 폴더에 있다고 적습니다.
- 볼트 폴더 아래 `{GUID}` 하위 폴더 구조와 웹·Windows 보관함을 가리키는 GUID 값은 확인하지 못했습니다.

### 버전별 차이

| 버전 | 달라진 점 | 근거 |
|---|---|---|
| Windows 7 / Server 2008 R2 | 자격 증명 관리자가 제어판 기능으로 처음 들어왔습니다. USB 로 보관함 자동 불러오기·내보내기, 여러 보관함 만들기·지우기·복사 UI, 웹 비밀번호 추가·편집 UI, 보관함 잠금·해제, 보관함 비밀번호 보호가 있었습니다 | Credentials Processes in Windows Authentication, Credential Locker Overview |
| Windows 8 / Server 2012 | 위 기능들이 빠졌습니다. Windows 스토어 앱이 저장 영역을 쓸 수 있게 됐습니다. Microsoft 계정으로 자격 증명을 로밍(동기화)합니다 | Credential Locker Overview |
| Windows 8.1 / Server 2012 R2 | 같은 자원에 자격 증명이 여럿일 때 기본값을 지정합니다. 화면에 "마지막 사용 날짜"가 보입니다 | Credential Locker Overview |

- 자격 증명 로밍은 도메인에 가입하지 않은 PC 에선 기본으로 켜지고, 도메인 가입 PC 에선 꺼집니다.
- 로밍 때문에 저장 영역 파일은 비밀번호로 보호할 수 없고 접근을 잠글 수 없습니다.
- Windows 10 과 11 에서 달라진 점은 이번에 연 자료로 확인하지 못했습니다.

## 구조

### 한 건의 자격 증명이 담는 칸

아래 칸 이름과 값은 Win32 API 가 돌려주는 `CREDENTIALW` 구조체 기준입니다. 디스크 파일의 바이트 배치가 이 순서와 같다는 확인은 하지 못했습니다.

| 칸 | 뜻 |
|---|---|
| `Flags` | 자격 증명 속성 플래그 |
| `Type` | 자격 증명 종류 (아래 표) |
| `TargetName` | 이 자격 증명을 가리키는 이름 |
| `Comment` | 설명 |
| `LastWritten` | 마지막으로 고친 시각 (FILETIME) |
| `CredentialBlobSize` | 비밀 데이터 크기 |
| `CredentialBlob` | 비밀 데이터 (Type 에 따라 뜻이 다름) |
| `Persist` | 얼마나 오래 남는지 (아래 표) |
| `AttributeCount`, `Attributes` | 앱이 붙인 속성 |
| `TargetAlias` | 대상의 별칭 |
| `UserName` | 사용자 이름 |

칸 순서는 `Flags`, `Type`, `TargetName`, `Comment`, `LastWritten`, `CredentialBlobSize`, `CredentialBlob`, `Persist`, `AttributeCount`, `Attributes`, `TargetAlias`, `UserName` 입니다. 최소 지원은 클라이언트 Windows XP, 서버 Windows Server 2003 입니다.

`TargetName` 과 `Type` 이 한 자격 증명을 유일하게 가립니다. 만든 뒤에는 이 둘을 바꿀 수 없습니다.

### Type 값

| 값 | 이름 | 뜻 |
|---|---|---|
| 1 | `CRED_TYPE_GENERIC` | 일반. 특정 인증 패키지가 쓰지 않습니다. `CredentialBlob` 내용은 앱이 정합니다 |
| 2 | `CRED_TYPE_DOMAIN_PASSWORD` | NTLM·Kerberos·Negotiate 가 대상에 연결할 때 자동으로 쓰는 비밀번호. `CredentialBlob` 은 평문 유니코드 비밀번호이고 인증 패키지만 읽습니다 |
| 3 | `CRED_TYPE_DOMAIN_CERTIFICATE` | 인증서 자격 증명. `CredentialBlob` 은 PIN 이고 로그온 세션을 넘어 보존되지 않습니다 |
| 4 | `CRED_TYPE_DOMAIN_VISIBLE_PASSWORD` | 더는 지원하지 않습니다 (XP·2003 의 Passport 용) |
| 5 | `CRED_TYPE_GENERIC_CERTIFICATE` | Vista·2008 이하에선 지원하지 않습니다 |
| 6 | `CRED_TYPE_DOMAIN_EXTENDED` | Vista·2008 이하에선 지원하지 않습니다 |

- `TargetName` 은 대소문자를 가리지 않습니다.
- 도메인 비밀번호형의 `TargetName` 에는 서버 이름 (NetBIOS·DNS), 와일드카드 (`*.example.com`, `도메인\*`), `*` 가 올 수 있습니다.
- 일반형은 회사 이름을 앞에 붙이도록 권합니다. Microsoft 서비스는 `Microsoft_서비스이름_대상` 꼴을 씁니다.
- `UserName` 은 도메인 비밀번호형이면 `도메인\사용자` 또는 UPN 이고, 인증서형이면 마샬링된 인증서 참조입니다. 일반형은 값이 있어도 관리자가 무시합니다.

### Persist 값

| 값 | 이름 | 얼마나 남나 |
|---|---|---|
| 1 | `CRED_PERSIST_SESSION` | 그 로그온 세션 동안만. 로그오프하면 사라집니다 |
| 2 | `CRED_PERSIST_LOCAL_MACHINE` | 이 컴퓨터의 이후 모든 세션. 다른 컴퓨터에선 보이지 않습니다 |
| 3 | `CRED_PERSIST_ENTERPRISE` | 이 컴퓨터와 다른 컴퓨터 세션 모두. 로밍 프로필이 없으면 로컬에만 남습니다 |

### 길이 한도

| 칸 | 한도 |
|---|---|
| `TargetName` | 도메인형 337자 / 일반형 32767자 |
| `Comment`, `TargetAlias` | 256자 |
| `UserName` | 513자 |
| `CredentialBlob` | 5×512 바이트 |
| 속성 | 64개 |

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 이 사용자 프로필에 어떤 대상 (`TargetName`) 의 자격 증명이 저장돼 있었는지 | 저장된 비밀번호가 지금도 맞는 값인지 |
| 자격 증명 종류 (`Type`) 가 무엇인지 | 그 자격 증명을 실제로 로그인에 몇 번 썼는지 |
| 마지막으로 고친 시각 (`LastWritten`) | 그 계정 앞에 누가 앉아 있었는지 |
| 얼마나 오래 남도록 저장됐는지 (`Persist`) | 파일이 없을 때 자격 증명을 저장한 적이 없다는 것 |

- 도메인 비밀번호형 (`Type` 2) 의 `CredentialBlob` 은 평문 비밀번호입니다. 그래서 이 볼트는 비밀번호가 그대로 남는 자리입니다.
- 파일은 암호화돼 있습니다. 널리 알려진 대로 DPAPI 로 감싸여 있다면, 사용자 마스터키를 풀 재료가 없을 때 내용을 읽지 못합니다.
- 저장된 자격 증명이 있다고 해서 그 계정이나 서비스에 실제로 접속했다고 단정하지 않습니다. 접속 여부는 이벤트 로그나 접속 기록으로 따로 맞춰 봅니다.

### 보고서 문장

아래 대상 이름과 시각은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "사용자 A 의 프로필에 `host01` 을 대상으로 하는 도메인 비밀번호형 자격 증명이 있고, `LastWritten` 이 2024-03-15 06:30:00 UTC 입니다. 이 자격 증명을 마지막으로 저장하거나 고친 시각이 이 값입니다."
- 쓰면 안 되는 문장: "사용자 A 가 2024-03-15 에 host01 에 원격 데스크톱으로 접속했습니다."

## 시각 해석

| 시각 | 어디에 남나 | 무엇을 가리키나 | 형식 |
|---|---|---|---|
| `LastWritten` | 자격 증명 칸 | 그 자격 증명을 마지막으로 고친 때 | FILETIME, UTC |

- `LastWritten` 은 쓰기 때 넣은 값을 무시하고 시스템이 정합니다. 그래서 앱이 이 값을 마음대로 넣지는 못합니다. 다만 값은 그 컴퓨터의 시계를 따르므로, 시계가 틀렸으면 이 값도 틀립니다.
- Windows 8.1 부터 화면에 "마지막 사용 날짜"가 보입니다. 이 값이 디스크 파일 어느 칸에 있는지는 확인하지 못했습니다. 그래서 "마지막 사용"과 "마지막 고침"을 섞지 않습니다.
- `.vcrd` 파일의 파일시스템 시각 (생성·수정) 이 저장·갱신 시점과 맞는지는 확인하지 못했습니다.
- FILETIME 계산은 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서, 현지 시각 변환은 [시간대 설정](/02-artifacts/system-account/time-zone.md) 에서 다룹니다.

## 함정과 한계

1. **파일만 있고 열쇠가 없으면 못 읽습니다.** 볼트 파일은 DPAPI 로 감싸여 있다고 알려져 있습니다. 사용자 마스터키와 그 마스터키를 풀 재료 (로그온 비밀번호나 도메인 백업키) 가 함께 있어야 풉니다. 구조는 [DPAPI 구조](/01-foundations/protection/data-protection-api/index.md) 를 봅니다.
2. **덮어쓴 자격 증명은 사라집니다.** 저장된 자격 증명이 거부되고 새 자격 증명으로 접근이 되면, 자격 증명 관리자가 옛 값을 새 값으로 덮어씁니다. 이전 값은 [섀도 복사본 활용](/03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 옛 파일에서 찾아 봅니다.
3. **로밍 프로필을 놓칩니다.** 로밍이 켜진 계정은 자격 증명이 다른 컴퓨터에도 있을 수 있습니다. Roaming 폴더 쪽 경로는 이번 자료로 확인하지 못했으므로 사용자 프로필 전체를 훑습니다.
4. **API 구조체 순서를 디스크 배치로 오해합니다.** 위 칸 순서는 API 가 돌려주는 순서입니다. 파일 바이트 배치가 같다고 단정하지 않습니다.
5. **세션형은 디스크에 안 남을 수 있습니다.** `Persist` 가 1 (세션) 인 자격 증명은 로그오프하면 사라집니다. 디스크 이미지에 없다고 저장한 적이 없다고 보지 않습니다.

### 지우기와 조작

- **자격 증명 관리자 UI 로 지웁니다.** 지운 `.vcrd` 파일이 볼트 폴더에서 사라져도 파일시스템에 흔적이 남을 수 있습니다. 방법은 [삭제 데이터 복구](/03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.
- **정책으로 저장을 막습니다.** "네트워크 액세스: 네트워크 인증을 위한 암호 및 자격 증명의 저장 허용 안 함" 정책을 켜면 도메인 인증용 자격 증명이 저장되지 않습니다. 스토어 앱의 자격 증명 저장은 관리자가 막을 수 없습니다.
- **백업 파일로 빼돌립니다.** 자격 증명 관리자의 백업 기능으로 저장된 자격 증명을 파일로 내보낼 수 있습니다. 백업·복원 창은 `rundll32.exe keymgr.dll` 로도 띄웁니다 (MITRE ATT&CK T1555.004). 백업하면 이벤트 5376 이 남습니다 (아래).

## 직접 분석해 보기

### 헥스로 한 번

아래는 FILETIME 명세를 보고 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

`LastWritten` 칸의 값 (FILETIME, 8바이트) 입니다.

```
오프셋  00 01 02 03 04 05 06 07
0x00    00 E4 97 34 A2 76 DA 01
```

1. 8바이트를 리틀 엔디언으로 읽습니다. `0x01DA76A234 97E400` 입니다.
2. 10진수로 바꾸면 133549578000000000 입니다.
3. FILETIME 으로 풀면 2024-03-15 06:30:00 UTC 입니다.
4. 이 값은 그 자격 증명을 마지막으로 고친 시각입니다.

### 공개 도구로 한 번

- 라이브 시스템에서는 Windows 에 들어 있는 `vaultcmd.exe` 로 저장된 자격 증명 목록을 봅니다.
- 오프라인 이미지에서는 DPAPI 복호를 지원하는 공개 도구로 `.vpol`·`.vcrd` 를 풉니다. 사용자 마스터키를 풀 재료가 함께 있어야 합니다.
- 도구가 보여 준 시각이 UTC 인지, 분석 PC 의 현지 시각인지 확인합니다.
- 값 한두 개는 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [DPAPI 구조](/01-foundations/protection/data-protection-api/index.md) | 볼트 파일을 풀 마스터키와 그 재료 |
| [레지스트리 속 비밀번호 정보 (SAM·SECURITY)](/02-artifacts/credentials/sam-security/index.md) | 시스템·계정이 저장한 다른 비밀 |
| [사용자 프로필 목록](/02-artifacts/system-account/profilelist.md) | 볼트가 어느 사용자 SID 아래에 있는지 |
| [원격 데스크톱 접속 기록](/02-artifacts/network/rdp-client-mru.md) | 원격 호스트를 대상으로 하는 자격 증명과 접속 이력 (원격 데스크톱 자격 증명의 `TargetName` 형식은 확인하지 못했습니다) |
| [로그온·로그오프](/02-artifacts/event-logs/logon-events/index.md) | 저장된 자격 증명으로 실제 로그온했는지 |
| [계정 탈취와 측면 이동](/04-scenarios/incident/credential-theft-lateral-movement/index.md) | 볼트를 노린 공격을 조사하는 흐름 |

### 탐지에서 보는 것

MITRE ATT&CK T1555.004 는 다음을 탐지 대상으로 꼽습니다.

- `vaultcmd.exe` 실행.
- `rundll32.exe` 로 `keymgr.dll` 을 부르는 실행 (자격 증명 백업·복원 창).
- `CredEnumerateA` 같은 자격 증명 열거 API 호출.
- 저장 영역 폴더의 `.vcrd`·`.vpol` 파일을 직접 읽는 접근.

이벤트 로그에는 사용자가 자격 증명 관리자 DB 를 백업할 때마다 이벤트가 남습니다.

- 이벤트 5376 (S) "Credential Manager credentials were backed up."
- 채널 Security, 공급자 Microsoft-Windows-Security-Auditing, 하위 범주 Audit User Account Management, 성공만 (S), Task 13824.
- 최소 OS 는 Windows Vista·Windows Server 2008. DC·멤버 서버·워크스테이션 모두에서 생깁니다.
- 칸은 `SubjectUserSid`, `SubjectUserName`, `SubjectDomainName`, `SubjectLogonId` 입니다. `SubjectLogonId` 로 [로그온·로그오프](/02-artifacts/event-logs/logon-events/index.md) 의 4624 와 이어 봅니다.
- Microsoft 는 사용자가 거의 쓰지 않는 동작이라 모든 5376 을 기록하도록 권합니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 Windows 8 이후의 이미지를 골라 다음을 풀어 봅니다.

1. 사용자 프로필 아래 `Microsoft\Vault` 와 `Microsoft\Credentials` 폴더에 파일이 있습니까? `.vcrd` 와 `.vpol` 이 각각 몇 개입니까?
2. 마스터키를 풀 재료 (로그온 비밀번호나 도메인 백업키) 가 검체에 함께 있습니까?
3. 자격 증명을 하나 풀어 `Type`, `TargetName`, `LastWritten` 을 적어 봅니다. `TargetName` 이 어떤 서비스를 가리킵니까?
4. `LastWritten` 을 직접 풀어 UTC 로 적고, 같은 시간대에 로그온·접속 기록이 있는지 봅니다.
5. Security 이벤트 로그에 5376 이 있습니까? 있으면 `SubjectLogonId` 로 4624 와 이어 봅니다.

## 참고 문헌

- Microsoft, "Credential Locker Overview" (Windows 8/8.1, Server 2012/2012 R2, 보관 문서) — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-8.1-and-8/jj554668(v=ws.11)
- Microsoft, "CREDENTIALW structure (wincred.h)" — https://learn.microsoft.com/en-us/windows/win32/api/wincred/ns-wincred-credentialw
- Microsoft, "5376(S) Credential Manager credentials were backed up" (보관 문서) — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5376
- Microsoft, "Credentials Processes in Windows Authentication" — https://learn.microsoft.com/en-us/windows-server/security/windows-authentication/credentials-processes-in-windows-authentication
- MITRE ATT&CK, "T1555.004 Credentials from Password Stores: Windows Credential Manager" — https://attack.mitre.org/techniques/T1555/004/
