# 윈도 식별자 형식 (SID·GUID·CLSID·Known Folder ID)

## 한 줄 요약

Windows 는 계정과 그룹을 보안 식별자 (SID, Security Identifier) 로 가리킵니다.
COM 클래스나 표준 폴더 같은 대상은 GUID 로 가리킵니다.
두 식별자 모두 문자열로 적을 때와 디스크에 저장할 때 바이트 배치가 다릅니다.
헥스를 보이는 순서대로 이으면 다른 값이 되므로, 배치 규칙대로 풀어 읽습니다.

## 이 형식을 쓰는 아티팩트

| 식별자 | 볼 수 있는 곳 | 자세한 내용 |
|---|---|---|
| SID | 사용자 계정 정보와 사용자 프로필 목록 | [사용자 계정](/02-artifacts/system-account/sam.md), [사용자 프로필 목록](/02-artifacts/system-account/profilelist.md) |
| SID | SECURITY 하이브의 작업그룹·도메인 정보 | [레지스트리 속 비밀번호 정보](/02-artifacts/credentials/sam-security/index.md) |
| CLSID | `HKLM\SOFTWARE\Classes\CLSID\{GUID}` 의 클래스 등록 정보 | 아래 "CLSID" 절 |
| Known Folder ID | `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FolderDescriptions\{GUID}` 의 폴더 정의 | 아래 "Known Folder ID" 절 |

두 레지스트리 경로는 한국어 Windows 11 PC 에서 확인했습니다.

아래 아티팩트에도 GUID 나 CLSID 가 나옵니다.
어느 칸에 어떤 식별자가 들어가는지는 각 페이지에서 다룹니다.

- [셸 아이템](/01-foundations/shell-document-formats/shell-item-pidl.md), [셸백](/02-artifacts/file-folder-usage/shellbags/index.md)
- [바로가기 파일](/02-artifacts/file-folder-usage/lnk.md), [점프리스트](/02-artifacts/file-folder-usage/jump-lists.md)
- [UserAssist](/02-artifacts/execution/userassist.md)

## 구조

### SID 문자열

SID 는 `S-1-식별기관-하위기관1-하위기관2-…-하위기관n` 꼴로 적습니다.

- 식별 기관 (IdentifierAuthority) 이 2^32 보다 작으면 10진으로 적습니다.
- 식별 기관이 2^32 이상이면 `0x` 뒤에 16진 12자리로 적습니다.
- 하위 기관 (SubAuthority) 은 늘 10진으로 적고, 앞자리에 0 을 붙이지 않습니다.
- 마지막 하위 기관을 상대 식별자 (RID, Relative Identifier) 라고 합니다.
- 한 도메인 안의 SID 는 RID 로 서로 구분됩니다.

명세는 도메인이나 컴퓨터 같은 계정 저장소를 새로 만들 때 96비트 식별자를 붙인다고 적습니다.
이 식별자는 암호학적 강도의 난수입니다.
저장소 안의 보안 주체에는 그 저장소 안에서만 유일한 32비트 식별자를 붙입니다.
`S-1-5-21-X-Y-Z-RID` 에서 X·Y·Z 는 32비트씩 모두 96비트입니다.
그래서 X·Y·Z 는 저장소 식별자에, RID 는 보안 주체 식별자에 해당한다고 볼 수 있습니다.
이 대응은 명세의 설명과 비트 수를 맞춰 본 추론입니다.

### SID 이진 구조

| 오프셋 | 크기 | 칸 | 뜻 |
|---|---|---|---|
| 0 | 1 | Revision | 늘 0x01 |
| 1 | 1 | SubAuthorityCount | 하위 기관 개수. 최대 15 |
| 2 | 6 | IdentifierAuthority | 식별 기관. 큰 자리부터 저장 |
| 8 | 4 × 개수 | SubAuthority | 부호 없는 32비트 값의 배열 |

전체 길이는 8 + 4 × 하위 기관 개수 바이트입니다.
가장 길면 68바이트입니다.

명세의 식별 기관 표는 NT 기관을 `{0x00,0x00,0x00,0x00,0x00,0x05}` 로 적습니다.
6바이트 가운데 마지막 바이트가 가장 낮은 자리라는 뜻입니다.

하위 기관의 바이트 순서는 명세에 "그 프로토콜이 정한다" 고만 적혀 있습니다.
한국어 Windows 11 PC 에서 .NET `SecurityIdentifier.GetBinaryForm` 으로 바꿔 보았습니다.
그 결과에서는 하위 기관이 리틀 엔디언이었습니다.

| SID | 이진 형태 (한국어 Windows 11 PC 의 .NET 결과) |
|---|---|
| S-1-5-18 | `01 01 00 00 00 00 00 05 12 00 00 00` |
| S-1-5-32-544 | `01 02 00 00 00 00 00 05 20 00 00 00 20 02 00 00` |

저장된 SID 를 읽을 때는 이 배치로 푼 결과가 알려진 문자열 SID 와 맞는지 한 번 확인합니다.

### 식별 기관 값

| 값 | 이름 | 예 |
|---|---|---|
| 0 | NULL | S-1-0-0 |
| 1 | WORLD | S-1-1-0 (Everyone) |
| 2 | LOCAL | S-1-2-0 |
| 3 | CREATOR | S-1-3-0 ~ S-1-3-2 |
| 4 | NON_UNIQUE | 쓰지 않음 |
| 5 | NT | 나머지 SID 대부분 |
| 0x0F | APP_PACKAGE | 앱 권한 SID |
| 0x10 | MANDATORY_LABEL | 무결성 수준 |
| 0x11 | SCOPED_POLICY_ID | |
| 0x12 | AUTHENTICATION | S-1-18-1, S-1-18-2 |

### 자주 보는 잘 알려진 SID

| SID | 이름 | 비고 |
|---|---|---|
| S-1-5-18 | LOCAL_SYSTEM | 운영체제가 쓰는 계정 |
| S-1-5-19 | LOCAL_SERVICE | |
| S-1-5-20 | NETWORK_SERVICE | |
| S-1-5-2 | NETWORK | |
| S-1-5-4 | INTERACTIVE | |
| S-1-5-6 | SERVICE | |
| S-1-5-7 | ANONYMOUS | |
| S-1-5-11 | AUTHENTICATED_USERS | |
| S-1-5-14 | REMOTE_INTERACTIVE_LOGON | |
| S-1-5-5-x-y | LOGON_ID | 로그온 세션마다 x·y 가 다릅니다. 재시작하면 같은 값을 다시 씁니다 |
| S-1-5-21-<컴퓨터>-500 | ADMINISTRATOR | |
| S-1-5-21-<컴퓨터>-501 | GUEST | 기본값은 꺼져 있고, 암호가 필요 없습니다 |
| S-1-5-21-<도메인>-502 | KRBTGT | |
| S-1-5-21-<도메인>-512 | DOMAIN_ADMINS | |
| S-1-5-21-<도메인>-513 | DOMAIN_USERS | |
| S-1-5-21-<도메인>-514 | DOMAIN_GUESTS | |
| S-1-5-21-<도메인>-515 | DOMAIN_COMPUTERS | |
| S-1-5-21-<도메인>-516 | DOMAIN_DOMAIN_CONTROLLERS | |
| S-1-5-21-<루트 도메인>-519 | ENTERPRISE_ADMINS | |
| S-1-5-32-544 | BUILTIN_ADMINISTRATORS | |
| S-1-5-32-545 | BUILTIN_USERS | |
| S-1-5-32-546 | BUILTIN_GUESTS | |
| S-1-5-32-551 | BACKUP_OPERATORS | |
| S-1-5-32-555 | REMOTE_DESKTOP | |
| S-1-5-32-573 | EVENT_LOG_READERS | |
| S-1-5-80 | NT_SERVICE | |
| S-1-5-80-0 | 모든 서비스 | 서비스마다 붙는 SID 는 S-1-5-80-<숫자 5개> 꼴입니다 |
| S-1-5-113 | LOCAL_ACCOUNT | |
| S-1-5-114 | 로컬 계정이면서 Administrators 구성원 | |
| S-1-15-2-1 | ALL_APP_PACKAGES | |

무결성 수준 SID 는 다음과 같습니다.

| SID | 수준 |
|---|---|
| S-1-16-0 | Untrusted |
| S-1-16-4096 | Low |
| S-1-16-8192 | Medium |
| S-1-16-8448 | Medium Plus |
| S-1-16-12288 | High |
| S-1-16-16384 | System |
| S-1-16-20480 | Protected Process |

확인한 한국어 Windows 11 PC 의 현재 사용자 RID 는 1001 이었습니다.
로컬 사용자에게 RID 를 몇 번부터 매기는지는 이 페이지의 자료로 확인하지 않았습니다.

### GUID 구조

GUID 는 16바이트 값입니다.
GUID 와 UUID 는 같은 말로 쓰며, 특정한 생성 방식을 뜻하지 않습니다.
명세는 GUID 를 세 가지로 표현합니다. RPC IDL 구조체, 패킷 바이트열, 중괄호 문자열입니다.

| 오프셋 | 크기 | 구조체 칸 | DCE UUID 칸 | 디스크 바이트 순서 |
|---|---|---|---|---|
| 0 | 4 | Data1 | time_low | 리틀 엔디언 |
| 4 | 2 | Data2 | time_mid | 리틀 엔디언 |
| 6 | 2 | Data3 | time_hi_and_version | 리틀 엔디언 |
| 8 | 8 | Data4 | clock_seq_hi_and_reserved, clock_seq_low, node | 적힌 순서 그대로 |

명세 [MS-DTYP] 는 따로 정하지 않은 여러 바이트 정수를 빅 엔디언으로 봅니다.
GUID 의 앞 세 칸은 리틀 엔디언이라고 따로 밝혀 두었습니다.
Data4 는 8바이트 배열이라서 순서가 바뀌지 않습니다.

문자열은 16진수를 `{8-4-4-4-12}` 자리로 끊어 중괄호로 감쌉니다.
중괄호 안은 RFC 4122 형식입니다.
명세의 예는 `{f81d4fae-7dec-11d0-a765-00a0c91e6bf6}` 입니다.

> 그림 자리: GUID 문자열 다섯 묶음과 디스크 16바이트를 위아래로 놓고, 앞 세 묶음은 바이트 순서가 뒤집히는 화살표로, 뒤 두 묶음은 곧은 화살표로 잇는 그림

### 버전 1 GUID (시각 기반)

dfDateTime 문서는 UUID 버전 1 의 구조를 다음과 같이 설명합니다.

- 시각은 1582-10-15 00:00:00 부터 센 100나노초 단위 60비트 값입니다.
- 오프셋 7 의 상위 4비트가 버전입니다.
- 오프셋 8 부터 16비트가 variant 와 clock sequence 입니다.
- 오프셋 10 부터 48비트가 노드 식별자입니다. 버전 1 에서는 대개 MAC 주소입니다.

그래서 버전 1 GUID 에서는 만든 시각과 장치의 MAC 주소를 뽑을 수 있습니다.
RFC 4122 의 정의로는 60비트 시각이 time_hi_and_version 의 아래 12비트, time_mid 16비트, time_low 32비트를 차례로 이은 값입니다.
기준 시각이 FILETIME 의 1601-01-01 과 다릅니다.
그래서 FILETIME 변환식에 그대로 넣으면 틀린 날짜가 나옵니다.
시각 형식 전반은 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
어떤 아티팩트에 버전 1 GUID 가 들어가는지는 [바로가기 파일](/02-artifacts/file-folder-usage/lnk.md) 등 각 페이지에서 봅니다.

### CLSID

CLSID 는 COM 클래스를 가리키는 GUID 로 알려져 있습니다.
KNOWNFOLDERID 문서의 예제 코드는 `CLSID_KnownFolderManager` 를 `CoCreateInstance` 함수에 넘겨 객체를 만듭니다.
레지스트리에 등록된 CLSID 는 `HKLM\SOFTWARE\Classes\CLSID\{GUID}` 키에서 이름을 찾을 수 있습니다.
아래는 한국어 Windows 11 PC 에서 이 키들의 값을 확인한 예입니다.

| CLSID | 기본값 | LocalizedString 값 |
|---|---|---|
| `{20D04FE0-3AEA-1069-A2D8-08002B30309D}` | This PC | `@windows.storage.dll,-9216` |
| `{645FF040-5081-101B-9F08-00AA002F954E}` | Recycle Bin | `@shell32.dll,-8964` |
| `{59031a47-3f72-44a7-89c5-5595fe6b30ee}` | UsersFiles | |
| `{031E4825-7B94-4dc3-B131-E946B44C8DD5}` | UsersLibraries | |

### Known Folder ID

KNOWNFOLDERID 상수는 시스템에 Known Folder 로 등록된 표준 폴더를 가리키는 GUID 입니다.
Windows Vista 부터 있습니다.
컴퓨터마다 해당하는 폴더만 설치됩니다.
항목마다 GUID, 표시 이름, 폴더 종류(PERUSER·FIXED·VIRTUAL·COMMON), 기본 경로, CSIDL 대응값이 정해져 있습니다.

| 상수 | GUID | 기본 경로 |
|---|---|---|
| FOLDERID_Desktop | `{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}` | `%USERPROFILE%\Desktop` |
| FOLDERID_Documents | `{FDD39AD0-238F-46AF-ADB4-6C85480369C7}` | `%USERPROFILE%\Documents` |
| FOLDERID_Downloads | `{374DE290-123F-4565-9164-39C4925E467B}` | `%USERPROFILE%\Downloads` (CSIDL 없음) |
| FOLDERID_Pictures | `{33E28130-4E1E-4676-835A-98395C3BC3BB}` | `%USERPROFILE%\Pictures` |
| FOLDERID_Profile | `{5E6C858F-0E22-4760-9AFE-EA3317B67173}` | `%USERPROFILE%` |
| FOLDERID_RoamingAppData | `{3EB685DB-65F9-4CF6-A03A-E3EF65729F3D}` | `%APPDATA%` |
| FOLDERID_LocalAppData | `{F1B32785-6FBA-4FCF-9D55-7B8E7F157091}` | `%LOCALAPPDATA%` |
| FOLDERID_LocalAppDataLow | `{A520A1A4-1780-4FF6-BD18-167343C5AF16}` | `%USERPROFILE%\AppData\LocalLow` |
| FOLDERID_Recent | `{AE50C081-EBD2-438A-8655-8A092E34987A}` | `%APPDATA%\Microsoft\Windows\Recent` |
| FOLDERID_Startup | `{B97D20BB-F46A-4C97-BA10-5E3608430854}` | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\StartUp` |
| FOLDERID_SkyDrive | `{A52BBA46-E9E1-435f-B3D9-28DAA648C0F6}` | `%USERPROFILE%\OneDrive` (Windows 8.1 에서 추가) |
| FOLDERID_Windows | `{F38BF404-1D43-42F2-9305-67DE0B28FC23}` | `%windir%` |
| FOLDERID_System | `{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}` | `%windir%\system32` |
| FOLDERID_SystemX86 | `{D65231B0-B2F1-4857-A4CE-A8E7C6EA7D27}` | 아래 표 참고 |
| FOLDERID_ProgramFiles | `{905e63b6-c1bf-494e-b29c-65b732d3d21a}` | 아래 표 참고 |
| FOLDERID_ProgramFilesX86 | `{7C5A40EF-A0FB-4BFC-874A-C0F2E0B9FA8E}` | 아래 표 참고 |
| FOLDERID_ProgramFilesX64 | `{6D809377-6AF0-444b-8957-A3773F02200E}` | 32비트 OS 와 32비트 앱에서는 쓸 수 없음 |
| FOLDERID_ProgramData | `{62AB5D82-FDC1-4DC3-A9DD-070D1D495D97}` | `%ALLUSERSPROFILE%` |
| FOLDERID_Public | `{DFDF76A2-C82A-4D63-906A-5644AC457385}` | `%SystemDrive%\Users\Public` |
| FOLDERID_UserProfiles | `{0762D272-C50A-4BB0-A382-697DCD729B80}` | `%SystemDrive%\Users` |

경로가 없는 가상 폴더도 있습니다.

| 상수 | GUID |
|---|---|
| FOLDERID_ComputerFolder | `{0AC0837C-BBF8-452A-850D-79D08E667CA7}` |
| FOLDERID_ControlPanelFolder | `{82A74AEB-AEB4-465C-A014-D097EE346D63}` |
| FOLDERID_NetworkFolder | `{D20BEEC4-5CA8-4905-AE3B-BF251EA09B53}` |
| FOLDERID_RecycleBinFolder | `{B7534046-3ECB-4C18-BE4E-64CD4CB7D6AC}` |
| FOLDERID_UsersFiles | `{f3ce0f7c-4901-4acc-8648-d5d44b04ef8f}` |

프로그램 폴더 GUID 는 OS 와 앱의 비트 수에 따라 가리키는 곳이 다릅니다.

| 조합 | ProgramFiles | ProgramFilesX86 | SystemX86 |
|---|---|---|---|
| 64비트 OS 의 64비트 앱 | Program Files | Program Files (x86) | `%windir%\syswow64` |
| 64비트 OS 의 32비트 앱 | Program Files (x86) | Program Files (x86) | |
| 32비트 OS | Program Files | Program Files | system32 (System 과 같음) |

설치 때 고른 설정이나 나중의 폴더 리디렉션 때문에 실제 경로는 기본 경로와 다를 수 있습니다.

한국어 Windows 11 PC 에서는 Known Folder 정의가 `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FolderDescriptions\{GUID}` 아래에 있었습니다.
Downloads 키에는 `Name=Downloads`, `RelativePath=Downloads` 값이 있었습니다.

## 읽는 법

### 헥스로 한 번 — SID

아래 바이트는 지어낸 SID `S-1-5-21-1004336348-1177238915-682003330-1001` 을 한국어 Windows 11 PC 의 .NET 으로 이진 형태로 바꾼 예시입니다.
실제 계정의 SID 가 아닙니다.

```
01 05 00 00 00 00 00 05 15 00 00 00 DC F4 DC 3B
83 3D 2B 46 82 8B A6 28 E9 03 00 00
```

1. `01` 은 Revision 1 입니다.
2. `05` 는 하위 기관이 5개라는 뜻입니다. 길이는 8 + 4 × 5 = 28바이트입니다.
3. `00 00 00 00 00 05` 는 식별 기관입니다. 큰 자리부터 읽어 5, 곧 NT 기관입니다.
4. `15 00 00 00` 은 리틀 엔디언으로 0x15, 곧 21 입니다.
5. `DC F4 DC 3B` 는 0x3BDCF4DC, 곧 1004336348 입니다.
6. `83 3D 2B 46` 은 0x462B3D83, 곧 1177238915 입니다.
7. `82 8B A6 28` 은 0x28A68B82, 곧 682003330 입니다.
8. `E9 03 00 00` 은 0x3E9, 곧 1001 입니다. 이 값이 RID 입니다.
9. 이어 적으면 `S-1-5-21-1004336348-1177238915-682003330-1001` 입니다.

### 헥스로 한 번 — GUID

아래 바이트는 FOLDERID_Desktop 을 명세 규칙대로 디스크 배치로 바꾼 예시입니다.
Python `uuid` 모듈로 계산했습니다.

```
3A CC BF B4 2C DB 4C 42 B0 29 7F E9 9A 87 C6 41
```

1. `3A CC BF B4` 를 뒤집어 읽으면 Data1 `B4BFCC3A` 입니다.
2. `2C DB` 를 뒤집어 읽으면 Data2 `DB2C` 입니다.
3. `4C 42` 를 뒤집어 읽으면 Data3 `424C` 입니다.
4. `B0 29` 는 그대로 넷째 묶음 `B029` 입니다.
5. `7F E9 9A 87 C6 41` 은 그대로 다섯째 묶음 `7FE99A87C641` 입니다.
6. 이어 적으면 `{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}` 입니다.

앞 8바이트만 뒤집히고 뒤 8바이트는 그대로입니다.
오프셋 7 의 바이트는 `42` 이고, 상위 4비트는 4 입니다.
버전이 1 이 아니므로 이 GUID 에서는 시각을 뽑지 않습니다.

## 포렌식에서 중요한 점

### SID 숫자로 뜻을 짐작하지 않습니다

명세는 SID 를 쓰는 쪽이 "구조가 맞다" 는 것 이상에 기대면 안 된다고 적습니다.
잘 알려진 SID 가 아니면 숫자만 보고 계정 종류를 단정하지 않습니다.
그 SID 가 누구인지는 [사용자 계정](/02-artifacts/system-account/sam.md) 과 [사용자 프로필 목록](/02-artifacts/system-account/profilelist.md) 에서 이름과 맞춰 봅니다.
시각과 사람을 잇는 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](/04-scenarios/activity/user-attribution.md) 에서 다룹니다.

### LOGON_ID 는 재시작을 넘어 유일하지 않습니다

S-1-5-5-x-y 는 로그온 세션마다 x·y 가 다릅니다.
재시작하면 같은 값을 다시 씁니다.
그래서 서로 다른 부팅의 기록에 같은 LOGON_ID 가 보여도 같은 세션이라고 단정하지 않습니다.

### 손상된 데이터에서 SID 를 찾을 때

카빙한 조각이나 손상된 레코드에서 SID 를 뽑을 때는 구조로 걸러 냅니다.

1. 첫 바이트가 `01` 인지 봅니다.
2. 둘째 바이트가 15 이하인지 봅니다.
3. 남은 바이트가 8 + 4 × 개수 만큼 있는지 봅니다.

세 조건이 모두 맞아도 우연히 맞는 바이트열일 수 있습니다.
그래서 알려진 SID 와 맞춰 보기 전에는 후보로만 다룹니다.

### Known Folder 경로는 그 PC 에서 확인합니다

기본 경로 표는 출발점일 뿐입니다.
폴더 리디렉션이나 설치 설정 때문에 실제 경로가 다를 수 있습니다.
ProgramFiles 처럼 비트 수에 따라 다른 곳을 가리키는 GUID 도 있습니다.
그래서 GUID 를 경로로 바꿀 때는 압수 PC 의 설정을 함께 봅니다.

## 함정

- **GUID 는 대소문자를 가리지 않고 비교합니다.** Microsoft 문서의 표 안에서도 `{905e63b6-...}`, `{A52BBA46-E9E1-435f-...}` 처럼 대소문자가 섞여 있습니다.
- **GUID 바이트를 헥스 그대로 이으면 다른 GUID 가 됩니다.** 위 예에서 `B4BFCC3A` 가 헥스 편집기에는 `3ACCBFB4` 로 보입니다.
- **ProgramFiles GUID 하나가 여러 경로를 가리킵니다.** 64비트 OS 에서도 32비트 앱에서는 Program Files (x86) 입니다.
- **SID 가 다른 값 뒤에 붙어 있기도 합니다.** 길이 칸이 있는 문자열 뒤에 이진 SID 가 이어지는 예는 [문자 인코딩](/01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 의 길이 칸 설명에 있습니다.
- **식별 기관과 하위 기관은 바이트 순서가 다릅니다.** 식별 기관은 큰 자리부터, 하위 기관은 리틀 엔디언으로 읽어야 알려진 SID 와 맞습니다(확인 범위: 한국어 Windows 11 PC 의 .NET 변환 결과).

## 도구

- **.NET `SecurityIdentifier` 클래스** — 문자열 SID 와 이진 SID 를 서로 바꿀 수 있습니다. PowerShell 에서도 쓸 수 있습니다. 이 페이지의 이진 예시는 이 클래스의 `GetBinaryForm` 으로 만들었습니다.
- **Python `uuid` 모듈** — 디스크의 16바이트를 `bytes_le` 로 넘기면 문자열 GUID 를 돌려줍니다.

```python
import uuid
uuid.UUID(bytes_le=bytes.fromhex('3ACCBFB42CDB4C42B0297FE99A87C641'))
# UUID('b4bfcc3a-db2c-424c-b029-7fe99a87c641')
```

- **레지스트리 조회 도구** — CLSID 이름과 Known Folder 정의를 찾을 때 씁니다. 분석 PC 가 아니라 압수 PC 의 SOFTWARE 하이브에서 찾습니다. 하이브를 읽는 법은 [레지스트리 하이브 구조](/01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다.

## 참고 문헌

- Microsoft, [MS-DTYP]: Windows Data Types, v20241119 — https://winprotocoldocs-bhdugrdyduf5h2e4.b02.azurefd.net/MS-DTYP/%5bMS-DTYP%5d.pdf
- Microsoft Learn, KNOWNFOLDERID — https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid
- Joachim Metz, dfDateTime 문서 "Date and time values" — https://dfdatetime.readthedocs.io/en/latest/sources/Date-and-time-values.html
