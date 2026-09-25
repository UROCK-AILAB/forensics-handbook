---
title: "서비스·드라이버"
parent: "아티팩트 · 자동실행·지속성"
nav_order: 700
---

# 서비스·드라이버 (Services·Drivers)

## 한 줄 요약

`HKLM\SYSTEM\CurrentControlSet\Services` 아래에는 서비스와 커널 드라이버마다 키가 하나씩 있습니다. Start 값은 언제 올릴지, Type 값은 서비스인지 드라이버인지, ImagePath 값은 무엇을 실행할지 정합니다. 부팅할 때 사용자 로그온 없이 도는 자리라서 지속성 조사에서 꼭 봅니다.

## 무엇을 기록하나 · 왜 생기나

Services 트리는 시스템의 서비스마다 정보를 담고, 드라이버마다 `Services\[드라이버 이름]` 키가 있습니다. 서비스(Win32 프로그램)와 커널 드라이버는 같은 트리를 쓰며 Type 값으로 갈립니다.

드라이버를 설치할 때는 INF 파일의 AddService 지시문을 쓰고, Windows 는 그 지시문이 가리키는 절의 ServiceBinary 항목으로 ImagePath 값을 만듭니다. `Parameters` 하위 키에는 드라이버별 데이터가, `Performance` 하위 키에는 성능 모니터링 DLL 이름 같은 정보가 들어갑니다. 자동 시작 서비스는 서비스 제어 관리자 (Service Control Manager, SCM) 가 올립니다.

원격 실행 도구 가운데에는 대상 PC 에 서비스를 만들어 명령을 돌리는 것이 있는데, 그 흐름은 [PsExec·WMI·WinRM](../../04-scenarios/incident/credential-theft-lateral-movement/psexec-wmi-winrm.md) 에서 다룹니다.

## 위치와 버전별 차이

| 무엇 | 경로 |
|---|---|
| 서비스·드라이버 키 | `HKLM\SYSTEM\CurrentControlSet\Services\<이름>` |
| 드라이버별 데이터 | `...\Services\<이름>\Parameters` |
| svchost 그룹 목록 | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Svchost` |

- `CurrentControlSet` 은 켜진 PC 에서 보이는 이름입니다. 이미지에서 어느 컨트롤셋을 읽어야 하는지는 [컨트롤셋 고르기](../../01-foundations/database-log-formats/registry-hive/controlset-select.md) 에서 다룹니다.
- Windows 11 PC 한 대에서 `HKLM\SYSTEM\Select` 는 Current=1, Default=1, LastKnownGood=1, Failed=0 이었습니다. `ControlSet001` 과 `CurrentControlSet` 만 보였고 `ControlSet002` 는 없었습니다.
- 같은 PC 의 `Svchost` 키에는 그룹 목록 값이 67개 있었습니다. 예를 들어 `netsvcs` 그룹에는 lanmanserver·IKEEXT·iphlpsvc 등이 들어 있었습니다.
- 같은 PC 에는 사용자별 서비스가 있었습니다. 아래 "사용자별 서비스" 를 봅니다. 이 형태가 어느 버전부터 생겼는지는 확인하지 못했습니다.

## 구조

### 주요 값

**Start (언제 시작하나)**

| 값 | 이름 | 뜻 |
|---|---|---|
| 0x0 | Boot | 부트 로더가 올립니다 |
| 0x1 | System | I/O 하위 시스템이 올립니다 |
| 0x2 | Automatic | 시스템이 시작할 때 SCM 이 자동으로 올립니다 |
| 0x3 | Demand | 필요할 때 올립니다. 드라이버는 장치에 필요하면 PnP 가 자동으로 올립니다 |
| 0x4 | Disabled | 올리지 않습니다 |

Start=2 에는 지연된 자동 시작도 들어갑니다. 자동 시작 서비스가 다 뜬 뒤 지연을 두고 하나씩 시작하는 방식이고, Windows 11 PC 한 대에서는 `DelayedAutostart`=1 값으로 표시되어 있었습니다(21개).

**Type (조합할 수 있습니다)**

| 값 | 뜻 |
|---|---|
| 0x1 | 커널 드라이버 |
| 0x2 | 파일 시스템 드라이버 |
| 0x8 | 인식기 드라이버 (Recognizer Driver). 시작할 때 파일 시스템을 알아봅니다 |
| 0x10 | 자기 프로세스에서 도는 Win32 서비스 |
| 0x20 | 다른 서비스와 프로세스를 나누어 쓰는 Win32 서비스 |
| 0x110 | Interactive Own Process |
| 0x120 | Interactive Share Process |

0x8·0x110·0x120 은 4697 이벤트 문서의 Type 표에 있는 값입니다.

**ErrorControl (시작에 실패했을 때)**

| 값 | 뜻 |
|---|---|
| 0x0 | 무시합니다 |
| 0x1 | 기록하고 계속합니다. 메시지 상자가 뜰 수 있습니다 |
| 0x2 | 기록하고 마지막 정상 구성 (last-known-good) 으로 재시작합니다 |
| 0x3 | 기록하고 last-known-good 으로 재시작을 시도합니다. 실패하면 부팅을 멈춥니다 |

**그 밖의 값**

- `ImagePath`: 서비스 실행 파일 경로입니다.
- `DisplayName`: 표시 이름입니다.
- `Description`: 설명입니다.
- Windows 11 PC 한 대에서는 `ObjectName`(실행 계정, 예: LocalSystem), `DependOnService`, `FailureActions`(REG_BINARY), `RequiredPrivileges`, `ServiceSidType`, `Group` 값도 보였습니다. 하위 키로는 `Security` 와 `TriggerInfo`(122개 서비스)가 있었습니다.

### svchost 형 서비스

아래는 Windows 11 PC 한 대에서 본 모습입니다.

```
Services\<이름>
    Type        REG_DWORD        0x20
    ImagePath   REG_EXPAND_SZ    %SystemRoot%\System32\svchost.exe -k netsvcs -p
    Parameters\
        ServiceDll    <실제 코드가 든 DLL 경로>
```

프로세스를 나누어 쓰는 서비스(0x20)의 ImagePath 는 svchost 를 가리켰고, 실제 코드가 든 DLL 은 `Parameters` 하위 키의 `ServiceDll` 값에 있었습니다(226개). 서비스 키 바로 아래에 `ServiceDll` 이 있는 경우도 3개 있었습니다. 그래서 svchost 형 서비스는 ImagePath 만 보면 안 되고 `ServiceDll` 을 봐야 합니다.

### 드라이버 키의 예

Windows 11 PC 한 대의 `disk` 키는 이랬습니다.

```
Services\disk
    ImagePath      System32\drivers\disk.sys
    Type           0x1
    Start          0x0
    ErrorControl   0x1
```

ImagePath 에는 드라이브 문자도 `%SystemRoot%` 도 없는 상대 경로가 들어 있었습니다. ImagePath 가 아예 없을 때 어느 경로를 쓰는지는 확인하지 못했습니다.

### 사용자별 서비스

아래는 모두 Windows 11 PC 한 대에서 본 모습입니다.

Type 0x60 과 0xE0 이 쌍을 이뤘는데, 0x60 은 원형 키였고 0xE0 은 같은 이름 뒤에 `_[16진 5자리]` 가 붙은 사용자 세션용 사본이었습니다. 원형 0x60 키 가운데 15개에 `UserServiceFlags` 값이 있었습니다. 0x40·0x80 비트의 공식 뜻은 확인하지 못했습니다.

### 한 PC 의 분포

Windows 11 PC 한 대의 Services 하위 키 823개 가운데 Type 값이 있는 키는 773개였습니다. 정상 PC 에서 어떤 값이 흔한지 가늠하는 기준으로만 씁니다.

| Type | 개수 | Type | 개수 |
|---|---|---|---|
| 0x1 | 420 | 0x120 | 1 |
| 0x2 | 37 | 0x210 | 1 |
| 0x8 | 1 | 0x50 | 1 |
| 0x10 | 94 | 0x60 | 23 |
| 0x20 | 170 | 0xD0 | 1 |
| 0x110 | 1 | 0xE0 | 23 |

| Start | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| 개수 | 102 | 32 | 116 | 511 | 12 |

## 증거로서 의미

### 증명하는 것

- 수집 시점에 이 이름의 서비스나 드라이버가 등록되어 있었습니다.
- Start 값으로 언제 올라가도록 설정되어 있었는지 알 수 있습니다.
- ImagePath 와 `ServiceDll` 로 어느 파일을 실행하도록 설정되어 있었는지 알 수 있습니다.
- `ObjectName` 으로 어느 계정으로 돌도록 설정되어 있었는지 알 수 있습니다.

### 증명하지 못하는 것

- **실행됐나.** 서비스 키는 등록만 알려 줍니다. 실행은 서비스 상태 변경 이벤트(7036), [프리페치](../execution/prefetch/index.md), [프로세스 생성](../event-logs/4688.md) 으로 따로 봅니다. Windows 11 PC 한 대에는 7036 이 한 건도 없었습니다. 7036 이 없다고 실행되지 않았다고 볼 수 없습니다.
- **언제 설치됐나.** 값에는 시각이 없습니다. 아래 "시각 해석" 의 설치 이벤트와 키 시각을 봅니다.
- **지금 그 경로의 파일이 그때 그 파일인가.** 키에는 해시가 없습니다.
- **누가 설치했나.** 서비스 키에는 설치한 계정을 적는 칸이 없습니다. 설치 이벤트에서 찾습니다.

보고서에는 "수집 시점에 이 이름의 서비스가 자동 시작으로 등록되어 있고, ImagePath 는 이 경로를 가리킨다" 처럼 씁니다.

## 시각 해석

서비스 키의 시각은 [키 마지막 기록 시각](../../01-foundations/database-log-formats/registry-hive/last-write-time.md) 하나뿐이고, 키가 마지막으로 바뀐 때일 뿐이라서 설치 시각이라고 단정하지 않습니다. 설치와 변경의 시각은 이벤트 로그가 알려 줍니다.

| 이벤트 | 로그 | 알려 주는 것 |
|---|---|---|
| 7045 | System (공급자 Service Control Manager) | 서비스가 설치되었습니다 |
| 7040 | System | 서비스의 시작 유형이 바뀌었습니다 |
| 7034 | System | 서비스가 예기치 않게 종료되었습니다 |
| 7036 | System | 서비스 상태가 바뀌었습니다 |
| 4697 | Security (Audit Security System Extension) | 서비스가 설치되었습니다 |

- 4697 의 서비스 파일 경로(ServiceFileName)는 서비스를 만들 때의 값입니다. 나중에 경로를 바꿔도 기록되지 않습니다. 실행 계정(ServiceAccount)도 마찬가지입니다.
- 그래서 설치 이벤트의 경로·계정이 지금 레지스트리 값과 다르면, 설치 뒤에 값이 바뀐 것입니다. 이 문장은 4697 문서에서 끌어낸 해석입니다.
- System 로그가 덮어쓰이면 7045 도 사라집니다. Windows 11 PC 한 대에서 System 로그의 가장 오래된 SCM 이벤트는 2026-06-27(UTC)이었습니다.
- 두 이벤트의 칸과 해석은 [서비스 설치](../event-logs/7045-4697.md) 에서 다룹니다.
- 드라이버 파일의 기록은 [AmCache 드라이버 항목](../execution/amcache-hve/inventorydriverbinary.md) 에서도 찾습니다.

## 함정과 한계

- **svchost 형 서비스는 ImagePath 만 보면 놓칩니다.** `Parameters\ServiceDll` 과 서비스 키 바로 아래 `ServiceDll` 을 함께 봅니다.
- **ImagePath 가 상대 경로일 수 있습니다.** 드라이버 키에서는 `System32\drivers\...` 처럼 드라이브 문자 없이 적혀 있었습니다.
- **도구가 DWORD 를 10진으로 보여 줄 수 있습니다.** Type 0xE0 은 224, 0x110 은 272 로 보입니다. 뜻이 걸린 값은 원시 바이트로 확인합니다.
- **이미지에는 `CurrentControlSet` 이 없습니다.** `Select` 가 가리키는 컨트롤셋을 읽습니다.
- **사용자별 서비스 사본은 이름 뒤에 16진 접미사가 붙습니다.** 비슷한 이름의 키가 여러 개 보여도 그것만으로 이상하다고 보지 않습니다.
- **서비스 키는 수백 개입니다.** Windows 11 PC 한 대에 823개가 있었습니다. 전부 읽기보다 아래 기준으로 먼저 거릅니다.

### 먼저 볼 기준

Microsoft 는 4697 이벤트를 감시할 때 아래 경우를 보라고 권합니다. 같은 기준을 레지스트리 값에도 쓸 수 있습니다.

- 서비스 파일 경로가 `%windir%` 나 Program Files 밖에 있습니다.
- Type 이 0x1·0x2·0x8 입니다. 드라이버는 부팅 초기부터 거의 제한 없는 권한으로 돌고, 드물게 설치됩니다.
- Start 가 0 이나 1 입니다.
- Start 가 4 입니다. 사용 안 함으로 설치된 경우입니다.
- 실행 계정이 localSystem·localService·networkService 가 아닙니다.

실행 계정은 사용자 모드 서비스(0x10·0x20)일 때만 채워집니다. 커널 드라이버에는 계정 이름이 없습니다. 계정을 주지 않고 설치한 Win32 서비스는 LocalSystem 으로 돕니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 값 형식에 맞춰 만든 예시입니다. 특정 검체에서 꺼낸 값이 아닙니다.

**Start 값 (REG_DWORD).**

```
02 00 00 00
```

4바이트를 리틀 엔디언으로 읽으면 2, 곧 Automatic 입니다.

**Type 값 (REG_DWORD).**

```
E0 00 00 00
```

1. 리틀 엔디언으로 읽으면 0xE0 입니다.
2. 10진으로는 224 입니다. 도구가 224 로 보여 주면 이 값입니다.
3. Windows 11 PC 한 대에서 0xE0 은 사용자별 서비스의 세션용 사본이었습니다.

**ImagePath 값의 앞부분 (REG_EXPAND_SZ, `%SystemRoot%`).**

```
25 00 53 00 79 00 73 00 74 00 65 00 6D 00 52 00   %.S.y.s.t.e.m.R.
6F 00 6F 00 74 00 25 00                           o.o.t.%.
```

문자열은 UTF-16LE 입니다. `%SystemRoot%` 는 펼치지 않은 채 저장되어 있습니다.

### 공개 도구로 한 번

1. 이미지에서 HKLM\SYSTEM 과 HKLM\SOFTWARE 에 해당하는 하이브를 하이브 로그와 함께 사본으로 뜹니다.
2. 레지스트리 뷰어로 `Select` 를 먼저 열어 읽을 컨트롤셋을 정합니다.
3. 그 컨트롤셋의 `Services` 아래 키마다 Type·Start·ImagePath·ObjectName 과 `Parameters\ServiceDll` 을 표로 뽑습니다.
4. 위 "먼저 볼 기준" 으로 걸러 봅니다.
5. 켜진 PC 에서는 `reg query HKLM\SYSTEM\CurrentControlSet\Services\<이름> /s` 처럼 읽기만 하는 명령으로 같은 값을 볼 수 있습니다.
6. 걸린 파일의 서명과 버전 정보를 확인합니다. 방법은 [의심 실행 파일 선별](../../03-techniques/analysis/code-signing-yara.md) 과 [실행 파일 메타데이터](../embedded-metadata/pe-header-version-info-digital-signature.md) 에 있습니다.
7. 도구 결과의 한 줄을 골라 위 풀이대로 DWORD 값을 원시 바이트로 직접 한 번 읽어 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 7045·4697 | 설치 시각, 설치 때의 경로·계정 | [서비스 설치](../event-logs/7045-4697.md) |
| 키 마지막 기록 시각 | 서비스 키가 마지막으로 바뀐 때 | [키 마지막 기록 시각](../../01-foundations/database-log-formats/registry-hive/last-write-time.md) |
| AmCache 드라이버 항목 | 드라이버 파일의 기록 | [AmCache 드라이버 항목](../execution/amcache-hve/inventorydriverbinary.md) |
| 4688 | 서비스 실행 파일이 프로세스로 만들어졌나 | [프로세스 생성](../event-logs/4688.md) |
| Sysmon 12·13·14 | 서비스 키를 만들거나 바꾼 프로세스 | [레지스트리 변경](../event-logs/sysmon/12-13-14.md) |
| 로그온 자동실행·예약 작업 | 같은 파일이 다른 자리에도 등록되어 있나 | [로그온 자동실행](run-runonce-startup-folder.md), [예약 작업](scheduled-tasks/index.md) |

자동실행 위치 전체를 훑는 흐름은 [악성코드 지속성(자동실행) 찾기](../../04-scenarios/incident/persistence.md) 에 있습니다.

## 실습

공개 검체(NIST CFReDS 등)에서 레지스트리 하이브와 이벤트 로그를 꺼내 아래 질문을 풀어 봅니다.

1. `Select` 는 어느 컨트롤셋을 가리킵니까? 다른 컨트롤셋도 있습니까?
2. Start 가 0·1·2 인 서비스 가운데 ImagePath 나 `ServiceDll` 이 `%windir%`·Program Files 밖을 가리키는 것이 있습니까?
3. Type 이 0x1·0x2 인 키 가운데 드라이버 파일 경로가 `System32\drivers` 밖인 것이 있습니까?
4. System 로그에 7045 가 있습니까? 그 경로와 계정이 지금 레지스트리 값과 같습니까?
5. 수상한 서비스 하나를 골라 서비스 키의 마지막 기록 시각과 7045 시각을 나란히 적어 봅니다. 두 시각이 가깝습니까?

## 참고 문헌

1. Microsoft Learn, *HKLM\SYSTEM\CurrentControlSet\Services Registry Tree* (ms.date 2024-09-18). 트리의 역할, Start·Type·ErrorControl 값, ImagePath·DisplayName·Description, INF 의 AddService·ServiceBinary, Parameters·Performance 하위 키. https://learn.microsoft.com/en-us/windows-hardware/drivers/install/hklm-system-currentcontrolset-services-registry-tree
2. Microsoft Learn, *4697(S) A service was installed in the system* (보관 문서, ms.date 2021-09-07). 추가 Type 값, 지연된 자동 시작, 설치 때 값만 기록되는 칸, 실행 계정 규칙, 감시 권고. https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4697
