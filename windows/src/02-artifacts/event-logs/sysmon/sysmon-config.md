# Sysmon 개념과 설정 확인 (Sysmon Config)

## 한 줄 요약

Sysmon (System Monitor) 은 Windows 서비스와 장치 드라이버로 이루어진 Sysinternals 도구입니다. 설정 파일이 정한 활동만 이벤트 로그에 남깁니다. 그래서 Sysmon 로그를 읽기 전에 어떤 이름으로 설치됐는지, 어떤 설정이 적용됐는지, 설정이 언제 바뀌었는지를 먼저 확인합니다. 이 페이지는 설치 흔적, 설정이 남는 레지스트리 값, 설정 파일 읽는 법, 설정 상태를 알려 주는 이벤트 4·16·255 를 다룹니다.

## Sysmon 은 무엇을 하나

Sysmon 은 Mark Russinovich 와 Thomas Garnier 가 만들었고 Sysinternals 도구로 배포됩니다. 한 번 설치하면 재부팅 뒤에도 남아 시스템 활동을 이벤트 로그에 쓰며, 설치와 제거에 재부팅이 필요 없습니다. 사건을 분석하지 않고, 공격자에게서 자신을 숨기려 하지도 않습니다. Windows 내장 Sysmon 의 Microsoft 문서도 같은 뜻으로, 기록만 하고 분석·경보·차단은 하지 않는다고 적습니다.

다만 Sysinternals 문서의 이벤트 목록에는 실행 파일 생성 차단(27)과 파일 파쇄 차단(28)이 있습니다. 두 문서의 설명이 엇갈리므로 이 두 이벤트는 [파일 생성·삭제](11-23-26.md)에서 따로 봅니다.

Sysmon 은 두 부분이 함께 돕니다.

| 부분 | 하는 일 |
|---|---|
| 서비스 | 드라이버가 모은 사건을 이벤트 로그에 씁니다. 보호 프로세스 (protected process) 로 돌아서 사용자 모드에서 건드릴 수 있는 범위가 좁습니다. |
| 드라이버 | 사건을 잡아 대기열에 쌓습니다. Sysinternals 문서는 이 드라이버를 부팅 초기에 시작하는 드라이버 (boot-start driver) 로 설치한다고 적습니다. Sysmon Community Guide 는 드라이버 시작 방식을 "자동" 으로 적어 두 자료가 다릅니다. 실물에서는 드라이버 키의 Start 값을 봅니다. 부팅 초기 활동은 잡아 두었다가 서비스가 뜨면 넘깁니다. |

### 설정을 먼저 보는 까닭

무엇을 기록할지는 설정 파일이 정합니다. Microsoft 문서는 설정에서 빼서 기록하지 않은 활동은 나중에 되살릴 수 없다고 적습니다. 설정 없이 설치하면 기록하는 이벤트가 몇 개뿐인데, 아래 "기본 동작과 명령줄 스위치" 를 봅니다. 그래서 Sysmon 로그에 어떤 활동이 없다고 해서 그 활동이 없었다고 쓸 수 없고, 그 기간의 설정이 그 활동을 기록하게 돼 있었는지부터 봅니다.

이벤트 번호별 목록은 [Sysmon 로그](index.md) 허브에 있습니다.

## 위치와 버전별 차이

### 배포본과 지원 OS

- 배포 zip 에는 Sysmon.exe, Sysmon64.exe, Sysmon64a.exe (ARM64 용), Eula.txt 가 들어 있습니다.
- v15.22 실행 파일의 파일 버전은 15.22 였고, 서명자는 Microsoft Windows Publisher 였습니다 (확인 범위: 공식 배포본 v15.22).
- v15.22 는 Windows 11 이상과 Windows Server 2019 이상에서 돕니다.
- 예전 버전이 어느 OS 까지 지원했는지는 확인하지 못했습니다. 옛 OS 에서 나온 로그라면 예전 버전 Sysmon 이 남겼을 수 있습니다.
- Vista 이후에는 Microsoft-Windows-Sysmon/Operational 채널에 씁니다. 이벤트 뷰어에서는 "응용 프로그램 및 서비스 로그 > Microsoft > Windows > Sysmon > Operational" 에 보입니다.
- Vista 이전 OS 에서는 System 로그에 씁니다.

### 설치하면 남는 곳

| 흔적 | 위치 | 비고 |
|---|---|---|
| 실행 파일 | `%SystemRoot%` (Windows 폴더) 에 복사한 사본 | 배포본에 "Failed to copy Sysmon from temporary to systemroot" 문자열이 있습니다 |
| 주 서비스 키 | `HKLM\SYSTEM\CurrentControlSet\Services\<서비스 이름>` | ImagePath `%windir%\<실행 파일 이름>`, 자동 시작, LocalSystem 계정 |
| 드라이버 키 | `HKLM\SYSTEM\CurrentControlSet\Services\<드라이버 이름>` | 기본 이름은 SysmonDrv 입니다. ImagePath 는 `<드라이버 이름>.sys` 입니다 |
| 설정 값 | `HKLM\SYSTEM\CurrentControlSet\Services\<드라이버 이름>\Parameters` | Rules 값에 규칙이 들어 있습니다 |
| 로그 채널 등록 | `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WINEVT\Channels\Microsoft-Windows-Sysmon/Operational` | |
| 로그 파일 | `%SystemRoot%\System32\winevt\Logs\Microsoft-Windows-Sysmon%4Operational.evtx` | 이름 규칙으로 짐작한 경로입니다. 아래 설명을 봅니다 |
| 사용자 키 | `HKCU\Software\Sysinternals\System Monitor` | Carlos Perez 는 이 키를 Sysinternals 도구가 사용권 동의를 기록하는 곳으로 설명합니다. 그 밖에 어떤 값이 들어가는지는 확인하지 못했습니다 |

- 오프라인 SYSTEM 하이브에는 CurrentControlSet 이 없습니다. `ControlSet00x` 처럼 번호가 붙은 키에서 찾습니다. 하이브 구조는 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.
- 이벤트 로그 파일 이름은 채널 이름의 "/" 를 "%4" 로 바꿔 짓습니다. Windows 11 25H2 (빌드 26200.9457) PC 한 대에서 `Microsoft-Windows-AAD%4Operational.evtx` 같은 파일로 이 규칙을 확인했습니다. 그 PC 에는 Sysmon 이 없어서 Sysmon 로그 파일 자체는 보지 못했습니다.
- 같은 PC 에서 `-s`·`-?` 만 실행했을 때는 사용자 키가 생기지 않았습니다.
- 서비스 키와 드라이버 키를 읽는 법은 [서비스·드라이버](../../persistence/services-drivers.md)에서 다룹니다.

### 로그 채널 기본값

아래 값은 v15.22 배포본 안의 이벤트 매니페스트에서 뽑았습니다.

| 항목 | 값 |
|---|---|
| 공급자 이름 | Microsoft-Windows-Sysmon |
| 공급자 GUID | {5770385F-C22A-43E0-BF4C-06F5698FFBD9} |
| 채널 기본 최대 크기 | 67108864바이트 (64MiB) |
| 접근 권한 (SDDL) | SYSTEM 모든 권한 · Administrators 읽기·쓰기·지우기 · Backup Operators, Server Operators, Event Log Readers (S-1-5-32-573) 읽기 |

- 최대 크기는 관리자가 바꿀 수 있습니다. 실물에서는 채널 설정을 따로 확인합니다.
- 채널 크기와 보관 방식을 확인하는 법은 [감사 정책과 로그 설정](../audit-policy-log-settings.md)에서 다룹니다.

### Windows 내장 Sysmon

Windows 11 에는 선택적 기능으로 들어 있는 Sysmon 이 있습니다.

기본으로 꺼져 있어 관리자가 직접 켜야 합니다. 켜는 순서는 두 단계로, `Enable-WindowsOptionalFeature -Online -FeatureName Sysmon` 으로 기능을 설치하고 `sysmon -i` 를 실행하며, 이때 설정 파일을 줄 수 있습니다. 따로 받은 Sysmon 과 함께 쓸 수 없어서, Microsoft 문서는 먼저 `Get-Service sysmon*` 으로 기존 설치를 찾아 지우라고 적습니다. 이벤트는 따로 받은 Sysmon 과 같은 채널에 쌓이고, 설정을 바꾸면 바로 적용되며 재부팅 뒤에도 유지됩니다. 대상은 지원되는 Windows 11 이상입니다 (Microsoft 문서, 2026-02-03). Windows 11 25H2 (빌드 26200.9457) PC 한 대에서는 선택적 기능 "Sysmon" 과 "Sysmon-Service" 가 보였고, 둘 다 Disabled 였습니다.

내장 Sysmon 의 실행 파일 위치, 서비스·드라이버 이름, 설정이 남는 레지스트리 값은 확인하지 못했습니다. 어느 빌드부터 들어갔는지도 확인하지 못했습니다. 이 페이지의 레지스트리 설명은 따로 받은 Sysmon 을 기준으로 합니다.

## 구조

### 서비스와 드라이버 이름

서비스 이름은 실행 파일 이름을 따르며 기본은 Sysmon 또는 Sysmon64 입니다. 드라이버 기본 이름은 SysmonDrv 이고, 설치할 때 `-d` 로 바꿀 수 있으며 8글자까지입니다.

이름을 바꿔 설치했다면 아래 단서로 찾습니다.

| 단서 | 읽는 법 |
|---|---|
| 서비스 설명 "System Monitor service" | 실행 파일 이름을 바꿔 설치해도 이 설명은 남는다고 Carlos Perez 는 적습니다 |
| 로그 채널 이름 | 이름을 바꿔도 Microsoft-Windows-Sysmon/Operational 그대로입니다 |
| 필터 드라이버 고도 (altitude) 385201 | fltmc 로 필터 드라이버 목록을 보면 이 값으로 찾을 수 있습니다. 배포본 안에도 이 숫자가 있습니다 |
| 서비스 키 Parameters 의 DriverName (REG_SZ) | Matt Graeber 의 스크립트(Sysmon 6.20 시절)는 이 값으로 서비스와 드라이버를 짝지어 찾습니다 |

### Parameters 키의 값

규칙은 드라이버 키 아래 `Parameters` 의 Rules 값에 들어 있습니다. 드라이버 이름을 바꾸면 SysmonDrv 자리가 그 이름으로 바뀝니다. Sysmon 은 설정 레지스트리가 바뀌면 설정을 자동으로 다시 읽습니다.

아래 표는 Matt Graeber 의 PSSysmonTools 스크립트가 읽는 값입니다. 이 스크립트는 Sysmon 6.20 (스키마 3.30\~4.10) 을 기준으로 만들었습니다.

| 값 이름 | 형식 | 뜻 (스크립트 기준) |
|---|---|---|
| Rules | REG_BINARY | 필터 규칙 |
| Options | REG_DWORD | 1 = 네트워크 연결 기록, 2 = 이미지 로드 기록 |
| HashingAlgorithm | REG_DWORD | 1 = SHA1, 2 = MD5, 4 = SHA256, 8 = IMPHASH |
| ProcessAccessMasks | REG_BINARY | 스크립트가 읽는 값입니다. 뜻은 확인하지 못했습니다 |
| ProcessAccessNames | REG_MULTI_SZ | 위와 같습니다 |
| CheckRevocation | REG_BINARY | 위와 같습니다 |

- v15.22 배포본에도 `System\CurrentControlSet\Services\%s\Parameters`, `Rules`, `Options`, `HashingAlgorithm`, `ConfigHash`, `ConfigFile` 문자열이 있습니다.
- 위 비트 뜻이 v15 에서도 같은지는 확인하지 못했습니다.
- ConfigHash·ConfigFile 이 Parameters 아래 값 이름인지도 확인하지 못했습니다.
- Rules 값 안의 바이트 구조는 이 페이지에서 다루지 않습니다. 스크립트에 해석 코드가 있지만, 이번 조사에서는 오프셋을 믿을 만하게 확인하지 못했습니다.

### 설정 파일 (XML)

설정 파일은 세 층으로 짭니다.

1. 최상위 태그 `<Sysmon schemaversion="…">`
2. 그 바로 아래의 전역 설정 항목
3. `<EventFiltering>` 아래의 이벤트별 필터

아래는 명세로 만든 예시입니다. 검체에서 가져온 설정이 아닙니다.

```xml
<Sysmon schemaversion="4.91">
  <HashAlgorithms>SHA256</HashAlgorithms>
  <EventFiltering>
    <ProcessCreate onmatch="exclude" />
    <ProcessTerminate onmatch="include" />
  </EventFiltering>
</Sysmon>
```

1. `schemaversion` 은 이 설정 파일이 따르는 스키마 버전입니다.
2. `HashAlgorithms` 는 전역 설정 항목입니다. 해시를 SHA256 으로 계산하라는 뜻입니다.
3. 규칙이 없는 `<ProcessCreate onmatch="exclude" />` 는 뺄 것이 없다는 뜻입니다. 그래서 프로세스 생성을 전부 기록합니다 (Microsoft 예시).
4. 규칙이 없는 `<ProcessTerminate onmatch="include" />` 는 넣을 것이 없다는 뜻입니다. 그래서 프로세스 종료를 기록하지 않습니다 (Sysinternals 예시 주석).

#### 스키마 버전

- 스키마 버전은 Sysmon 실행 파일 버전과 따로 매깁니다. 옛 설정 파일도 읽게 하려는 것입니다.
- v15.22 의 현재 스키마 버전은 4.91 입니다.
- v15.22 는 스키마 4.80, 4.81, 4.82, 4.83, 4.90, 4.91 을 압니다 (`-s all` 출력).

| 스키마 | 처음 나오는 것 (v15.22 `-s all` 출력 기준) |
|---|---|
| 4.80 | 이벤트 1\~26 (v15.22 가 아는 가장 오래된 스키마) |
| 4.81 | FieldSizes 설정 |
| 4.82 | 이벤트 27 |
| 4.83 | 이벤트 28 |
| 4.90 | 이벤트 29 |
| 4.91 | DriverQueueSize, SigningQueueSize 설정 |

각 스키마 버전이 어느 Sysmon 릴리스에 해당하는지는 확인하지 못했습니다. 그래서 설정 파일의 schemaversion 만으로 Sysmon 버전을 적지 않습니다. 실제 버전은 이벤트 4 의 Version 칸이나 실행 파일에서 확인합니다.

#### 전역 설정 항목

| 항목 | 뜻 | 기본값 |
|---|---|---|
| ArchiveDirectory | 각 볼륨 루트에 만드는 삭제 파일 보관 폴더 이름입니다. SYSTEM 만 들어가도록 ACL 이 걸립니다 | Sysmon |
| CheckRevocation | 서명 폐기 여부를 확인합니다 | True |
| CopyOnDeletePE | 지운 실행 파일을 보관합니다 | False |
| CopyOnDeleteSIDs | 지운 파일을 보관할 계정 SID 목록 | |
| CopyOnDeleteExtensions | 지운 파일을 보관할 확장자 목록 | |
| CopyOnDeleteProcesses | 지운 파일을 보관할 프로세스 이름 목록 | |
| DnsLookup | 역방향 DNS 조회를 합니다 | True |
| DriverName | 드라이버·서비스 이미지 이름 | |
| HashAlgorithms | MD5, SHA1, SHA256, IMPHASH, `*` (전부) 가운데 고릅니다 | 표에는 None (아래 설명) |
| DriverQueueSize | 드라이버가 쌓아 두는 이벤트 수 | 50000 |
| SigningQueueSize | 이미지 로드(이벤트 7)의 서명 확인 대기열 크기 | 1000 |
| FieldSizes | "칸 이름:크기" 목록으로 칸의 최대 길이를 정합니다. 예: `CommandLine:100,Image:20` | |

- 서비스가 따라가지 못해 드라이버 대기열(DriverQueueSize)이 차면, 오래된 이벤트부터 버리고 오류 이벤트 255 를 남깁니다.
- 해시 기본값은 Sysinternals 문서 안에서도 엇갈립니다. 기능 목록과 설치 예시는 "기본 SHA1" 이라고 적고, 설정 항목 표는 "HashAlgorithms 기본 None" 이라고 적습니다. 실물에서는 적용된 설정과 이벤트의 Hashes 칸을 직접 봅니다.
- Microsoft 의 내장 Sysmon 문서 표는 CopyOnDeleteExtensions 설명을 "프로세스 이름" 으로 적었습니다. DriverName 기본값은 "자동 생성" 으로 적었습니다. 이 페이지의 설명은 Sysinternals 문서를 따릅니다.
- 삭제 파일 보관 폴더를 읽는 법은 [파일 생성·삭제](11-23-26.md)에서 다룹니다.

### 기본 동작과 명령줄 스위치

| 명령 | 하는 일 |
|---|---|
| `sysmon64 -i [설정 파일]` | 설치합니다 |
| `sysmon64 -c [설정 파일]` | 설정을 바꿉니다 |
| `sysmon64 -c` (인수 없이) | 지금 적용된 설정을 보여 줍니다 |
| `sysmon -c --` | 설정을 기본값으로 되돌립니다 |
| `-m` | 이벤트 매니페스트를 설치합니다 |
| `-s` | 스키마를 출력합니다 |
| `-u [force]` | 제거합니다 |
| `-accepteula` | 설치할 때 사용권 동의 창을 건너뜁니다 |

설정 없이 설치하면 다음을 기록합니다 (Sysmon Community Guide).

- 프로세스 생성 (1)
- 프로세스 종료 (5)
- 드라이버 로드 (6)
- 파일 생성 시각 변경 (2)
- 실행 파일의 SHA1 해시

네트워크 연결(3)과 이미지 로드(7)는 기본으로 꺼져 있습니다.

설치 명령에 붙이는 스위치는 다음과 같습니다.

| 스위치 | 켜거나 정하는 것 |
|---|---|
| `-n` | NetworkConnect (이벤트 3) |
| `-l` | ImageLoad (이벤트 7) |
| `-k` | ProcessAccess (이벤트 10) |
| `-dns` | DnsQuery (이벤트 22) |
| `-g` | PipeMonitoring |
| `-h` | HashAlgorithms |
| `-r` | CheckRevocation |
| `-a` | ArchiveDirectory |
| `-d` | DriverName |

- 스위치로 켜는 이벤트도 설정 파일에서는 필터 태그로 따로 정합니다.
- v15.22 스키마의 이벤트 정의에는 ruledefault 속성이 있습니다. 1·5 는 include, 11\~22 는 exclude 이고, 나머지는 없습니다. 이 속성과 기본 기록 여부가 어떻게 이어지는지는 확인하지 못했습니다.

### 필터 규칙

- `onmatch="include"` 는 규칙에 맞는 것만 기록합니다.
- `onmatch="exclude"` 는 규칙에 맞는 것만 빼고 기록합니다.
- 한 이벤트에 include 와 exclude 를 함께 쓸 수 있습니다. 둘 다 맞으면 exclude 가 이깁니다.
- 필드 이름이 같은 조건끼리는 OR 로 묶입니다.
- 필드 이름이 다른 조건끼리는 AND 로 묶입니다.
- RuleGroup 의 `groupRelation="and"` 나 `"or"` 로 묶는 방식을 바꿉니다. `<Rule>` 요소로 규칙 하나하나에 따로 적용할 수도 있습니다.
- 규칙에 name 을 붙이면, 기록된 이벤트의 RuleName 칸에 어느 규칙에 걸렸는지 남습니다.

조건은 대소문자를 가리지 않습니다. 쓸 수 있는 조건은 다음과 같습니다.

`is` (기본), `is any`, `is not`, `contains`, `contains any`, `contains all`, `excludes`, `excludes any`, `excludes all`, `begin with`, `not begin with`, `end with`, `not end with`, `less than`, `more than`, `image`

### 설정 상태를 알려 주는 이벤트 (4·16·255)

| 이벤트 | 남는 때 | 칸 (v15.22 스키마) |
|---|---|---|
| 4 | Sysmon 서비스 상태가 바뀔 때 | UtcTime, State, Version, SchemaVersion |
| 16 | 필터 규칙 갱신 같은 설정 변경이 있을 때 | UtcTime, Configuration, ConfigurationFileHash |
| 255 | 부하가 커서 작업을 못 했거나, 버그가 있거나, 보안·무결성 조건이 맞지 않을 때 | UtcTime, ID, Description |

- 이벤트 4 와 16 은 필터로 끌 수 없습니다.
- Sysinternals 문서는 이벤트 4 가 서비스의 시작·중지 상태를 알린다고 적습니다. 배포본에도 "Started", "Stopped" 문자열이 있습니다. State 칸에 이 문자열이 그대로 적히는지는 실물로 확인하지 못했습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 하이브에 서비스 키·드라이버 키·Parameters 값이 있으면, 하이브를 수집한 때 Sysmon 이 설치돼 있었습니다 | 지금 설정이 과거 어느 시점에도 같았다는 것 |
| `-c` 출력은 그 순간 적용된 설정입니다 | 설정이 기록하게 돼 있지 않았던 활동이 없었다는 것 |
| 이벤트 16 은 설정이 바뀐 시각입니다 | 드라이버 대기열이 넘친 동안(255)의 활동이 모두 기록됐다는 것 |
| 이벤트 4 는 서비스 상태가 바뀐 시각입니다 | 누가 설정을 바꿨는지 (이벤트 16 칸에 계정이 없습니다) |
| 이벤트 255 는 그 무렵 기록이 빠졌을 수 있다는 표시입니다 | 내장 Sysmon 이 이 페이지와 같은 흔적을 남긴다는 것 |

### 보고서 문장

- 쓸 수 있는 문장: "이 PC 의 SYSTEM 하이브에는 설명이 'System Monitor service' 인 서비스 키가 있습니다. 같은 하이브의 드라이버 키 Parameters 아래에 Rules 값이 있습니다. Sysmon 로그에는 <시각> UTC 에 이벤트 16 이 있고, 그 뒤로는 설정 변경 기록이 없습니다."
- 쓰면 안 되는 문장: "이 PC 에서는 Sysmon 이 모든 활동을 기록하고 있었으므로, 로그에 없는 프로그램은 실행되지 않았다."

두 번째 문장은 설정을 확인하지 않고 기록 범위를 넘겨짚습니다.

## 시각 해석

- Sysmon 이벤트의 시각은 UTC 입니다. UtcTime 칸의 서식은 [프로세스 생성](1.md)에서 다룹니다.
- 이벤트 16 의 UtcTime 은 설정이 바뀐 때입니다. 이 시각 앞뒤로 기록되는 이벤트 종류가 달라질 수 있습니다.
- 이벤트 4 의 UtcTime 은 서비스 상태가 바뀐 때입니다.
- 드라이버는 부팅 초기 활동을 모아 두었다가 서비스가 뜬 뒤 넘깁니다. 그래서 부팅 직후에는 서비스 시작보다 이른 UtcTime 의 이벤트가 나중에 쓰일 수 있습니다. 이 점은 추론이며 확인하지 못했습니다.
- `-c` 로 설정을 바꾸면 Parameters 아래 값이 바뀌므로, 그 키의 마지막 기록 시각도 함께 바뀔 것으로 보입니다. 이 점도 추론입니다. 이벤트 16 의 시각과 맞춰 확인합니다.

## 함정과 한계

1. **기본 이름으로만 찾습니다.** 서비스 이름과 드라이버 이름은 바꿀 수 있습니다. 서비스 설명, 채널 이름, 고도 값으로도 찾습니다.
2. **기록이 없으니 활동도 없었다고 씁니다.** 설정에서 뺀 활동은 남지 않습니다. 설정부터 확인합니다.
3. **해시 알고리즘을 문서 기본값으로 짐작합니다.** 문서 안에서도 기본값이 엇갈립니다. 적용된 설정과 실제 Hashes 칸을 봅니다.
4. **레지스트리 비트 뜻을 그대로 믿습니다.** Options·HashingAlgorithm 비트 뜻은 Sysmon 6.20 시절 스크립트에서 왔습니다. v15 에서 같은지는 확인하지 못했습니다.
5. **내장 Sysmon 문서의 설정 표를 그대로 옮깁니다.** CopyOnDeleteExtensions, DriverName 설명이 Sysinternals 문서와 다릅니다.
6. **schemaversion 을 Sysmon 버전으로 적습니다.** 두 번호는 따로 매깁니다.
7. **기록이 끊긴 구간을 지나칩니다.** 이벤트 255 가 있으면 그 무렵 기록이 빠졌을 수 있습니다.
8. **채널 크기를 기본값으로 짐작합니다.** 64MiB 는 매니페스트 기본값입니다. 관리자가 바꿀 수 있습니다.
9. **내장 Sysmon 과 따로 받은 Sysmon 을 같은 것으로 봅니다.** 둘은 함께 쓸 수 없습니다. 내장 Sysmon 의 흔적 위치는 확인하지 못했습니다.

### 지우기와 조작

- **드라이버를 내립니다.** fltmc 로 Sysmon 드라이버를 내리면 System 로그에 Filter Manager 이벤트 1 이 남는다고 Carlos Perez 는 적습니다. Sysmon 은 그 명령의 실행을 마지막으로 기록합니다.
- **규칙 값을 지웁니다.** 레지스트리 감사를 켜 두었다면, Rules 값을 지운 행위가 보안 로그 4657 로 보인다고 Carlos Perez 는 적습니다. 감사 설정은 [감사 정책과 로그 설정](../audit-policy-log-settings.md)에서 확인합니다.
- **설정을 바꿉니다.** 설정 변경은 이벤트 16 으로 남고, 필터로 끌 수 없습니다.
- **서비스 상태를 바꿉니다.** 서비스 상태 변경은 이벤트 4 로 남고, 필터로 끌 수 없습니다.
- **로그를 지웁니다.** 매니페스트 기본 권한으로는 Administrators 가 이 채널을 지울 수 있습니다. [이벤트 로그 삭제](../1102-104.md)를 봅니다.
- **Sysmon 을 제거합니다.** 제거 뒤에 무엇이 남는지는 확인하지 못했습니다. 설치 때 남은 [서비스 설치](../7045-4697.md) 기록과 실행 흔적을 찾습니다.

여러 흔적을 모아 판단하는 순서는 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

## 직접 분석해 보기

### 라이브 시스템에서

1. `Get-Service sysmon*` 로 서비스를 찾습니다. 이름을 바꾼 설치는 여기서 안 보일 수 있습니다.
2. `fltmc` 로 필터 드라이버 목록을 보고 고도 385201 을 찾습니다.
3. 찾은 실행 파일로 `-c` 를 인수 없이 실행해 지금 설정을 봅니다.
4. `-s` 로 그 실행 파일이 아는 스키마를 봅니다.

라이브 시스템에서 명령을 실행하면 시스템에 흔적이 더해집니다. 순서와 기록 방법은 [라이브 응답](../../../03-techniques/process-acquisition/live-response/index.md)에서 다룹니다.

### 디스크 이미지에서

1. SYSTEM 하이브의 Services 아래에서 설명이 "System Monitor service" 인 서비스를 찾습니다.
2. 서비스 키 Parameters 의 DriverName 값으로 드라이버 키를 찾습니다. 값이 없으면 SysmonDrv 부터 봅니다.
3. 드라이버 키 Parameters 아래 값을 모두 적습니다.
4. SOFTWARE 하이브에서 채널 등록 키를 확인합니다.
5. 로그 폴더에서 Sysmon 로그 파일을 찾아 이벤트 4·16·255 를 뽑습니다.
6. `%SystemRoot%` 의 실행 파일에서 버전과 서명을 확인합니다. 방법은 [실행 파일 메타데이터](../../embedded-metadata/pe-header-version-info-digital-signature.md)에서 다룹니다.

### 헥스로 한 번

REG_DWORD 값은 4바이트를 리틀 엔디언으로 저장합니다. 아래는 PSSysmonTools 스크립트의 비트 정의로 만든 예시입니다. 검체에서 나온 값이 아닙니다. v15 에서도 뜻이 같은지는 확인하지 못했습니다.

```
Options           03 00 00 00   → 0x00000003
HashingAlgorithm  05 00 00 00   → 0x00000005
```

1. Options 는 0x3 입니다. 1 (네트워크 연결) 과 2 (이미지 로드) 를 더한 값입니다. 두 기록이 모두 켜져 있다는 뜻입니다.
2. HashingAlgorithm 은 0x5 입니다. 1 (SHA1) 과 4 (SHA256) 를 더한 값입니다.

하이브 안에서 값 데이터를 찾아가는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

### 공개 도구로 한 번

- 공개 레지스트리 뷰어(예: Registry Explorer, RegRipper)로 서비스 키와 Parameters 값을 봅니다.
- PSSysmonTools 의 SysmonRuleParser.ps1 에는 Rules 값을 해석하는 코드가 있습니다. Sysmon 6.20 시절 형식 기준이라, 요즘 버전의 Rules 값에 맞는지는 따로 확인합니다.
- 이벤트 4·16·255 는 이벤트 뷰어나 공개 EVTX 해석 도구(예: EvtxECmd, python-evtx)로 뽑습니다. EVTX 저장 구조는 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.
- 도구 결과는 한두 건이라도 원본과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [서비스·드라이버](../../persistence/services-drivers.md) | Sysmon 서비스·드라이버 키의 이름, 시작 방식, 실행 파일 경로 |
| [서비스 설치](../7045-4697.md) | Sysmon 을 설치한 시각 |
| [이벤트 로그 삭제](../1102-104.md) | Sysmon 채널이 지워진 흔적 |
| [감사 정책과 로그 설정](../audit-policy-log-settings.md) | 채널 크기·보관 방식, 레지스트리 감사가 켜져 있었는지 |
| [프리페치](../../execution/prefetch/index.md) | Sysmon 실행 파일이나 fltmc 를 실행한 흔적 |
| [실행 파일 메타데이터](../../embedded-metadata/pe-header-version-info-digital-signature.md) | Sysmon 실행 파일의 버전과 서명 |
| 같은 로그의 [프로세스 생성](1.md) | 설정 변경 명령을 실행한 프로세스와 명령줄 |

## 실습

직접 만든 Windows 11 가상 머신에서 해 봅니다. 각 단계의 시각을 적어 둡니다.

1. 설정 파일 없이 Sysmon 을 설치합니다. `-c` 출력과 실제로 남는 이벤트 번호를 비교하십시오.
2. 실행 파일 이름을 바꾸고 `-d` 로 드라이버 이름도 바꿔 설치합니다. 서비스 설명, 채널 이름, fltmc 고도로 설치를 찾아 보십시오.
3. `-n`, `-l`, `-h` 를 바꿔 가며 설치합니다. Options·HashingAlgorithm 값이 어떻게 바뀌는지 보십시오. 위 "헥스로 한 번" 의 비트 뜻이 v15 에서도 같은지 여기서 답이 나옵니다.
4. `-c` 로 설정을 바꿉니다. 이벤트 16 의 칸과 Parameters 키의 마지막 기록 시각을 비교하십시오. ConfigHash·ConfigFile 값이 생기는지도 보십시오.
5. 실습용 가상 머신에서만 fltmc 로 드라이버를 내립니다. System 로그와 Sysmon 로그의 마지막 이벤트를 확인하십시오.
6. 다른 가상 머신에서 내장 Sysmon 을 켭니다. 실행 파일 위치, 서비스·드라이버 이름, 레지스트리 값을 따로 받은 Sysmon 과 비교하십시오.

## 참고 문헌

- Microsoft Learn, "Sysmon - Sysinternals" — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
- Sysinternals, Sysmon 공식 배포본 v15.22 (Sysmon.zip) — https://download.sysinternals.com/files/Sysmon.zip
- Carlos Perez, "Operating Offensively Against Sysmon" (2018) — https://www.darkoperator.com/blog/2018/10/5/operating-offensively-against-sysmon
- Matt Graeber, PSSysmonTools SysmonRuleParser.ps1 — https://raw.githubusercontent.com/mattifestation/PSSysmonTools/master/PSSysmonTools/Code/SysmonRuleParser.ps1
- Microsoft Learn, "Enable and configure Sysmon in Windows" (2026-02-03) — https://learn.microsoft.com/en-us/windows/security/operating-system-security/sysmon/how-to-enable-sysmon
- Microsoft Learn, "Sysmon configuration files" (2026-02-03) — https://learn.microsoft.com/en-us/windows/security/operating-system-security/sysmon/sysmon-configuration-files
- TrustedSec, Sysmon Community Guide, "install_windows.md" — https://raw.githubusercontent.com/trustedsec/SysmonCommunityGuide/master/chapters/install_windows.md
