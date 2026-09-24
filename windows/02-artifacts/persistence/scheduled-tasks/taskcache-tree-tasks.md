---
title: "작업 캐시 레지스트리"
parent: "예약 작업"
grand_parent: "아티팩트 · 자동실행·지속성"
nav_order: 730
---

# 작업 캐시 레지스트리 (TaskCache Tree·Tasks)

> 상위 허브: [예약 작업 (Scheduled Tasks)](index.md)

## 한 줄 요약

작업 스케줄러는 작업을 등록할 때 SOFTWARE 하이브의 `TaskCache` 아래에 키를 두 개 만듭니다. `Tree` 아래 키는 작업 경로를 이름으로 쓰고, `Tasks` 아래 키는 GUID 를 이름으로 쓰며 작업의 해시·명령·시각을 담습니다. XML 파일과 따로 남기 때문에, 파일이 없거나 바뀌었을 때 비교할 기준이 됩니다.

## 무엇을 기록하나 · 왜 생기나

작업 하나를 등록하면 레지스트리에 다음 두 키가 생깁니다.

- `...\Schedule\TaskCache\Tree\<작업 경로>`
- `...\Schedule\TaskCache\Tasks\{GUID}`

Tree 쪽 키에는 Id·Index·SD 값이 있습니다. Id 는 Tasks 쪽 키의 GUID 를 가리킵니다. Tasks 쪽 키에는 작업 경로, XML 해시, 트리거, 동작, 등록·실행 시각이 들어 있습니다. 같은 때에 `C:\Windows\System32\Tasks` 아래에 XML 파일도 생기는데, 이 파일은 [작업 정의 파일 (System32\Tasks XML)](system32-tasks-xml.md)에서 다룹니다.

## 위치와 버전별 차이

### 키 위치

| 항목 | 내용 |
|---|---|
| 살아 있는 시스템 | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache` |
| 오프라인 | SOFTWARE 하이브의 `Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache` |
| 최소 버전 | Windows Vista |

하이브 파일을 읽는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.

`Schedule` 키 아래에는 Aliases, CompatibilityAdapter, Configuration, CredWom, Handlers, Handshake, TaskCache 하위 키가 있습니다. DomainJoinDetected, HashingCompleted, MigrationCleanupCompleted 값도 있습니다. 이 값들의 뜻은 winreg-kb 문서에 비어 있습니다.

### TaskCache 하위 키

| 하위 키 | 내용 |
|---|---|
| Tree | 작업 경로를 이름으로 쓰는 키. 폴더도 키가 됩니다 |
| Tasks | GUID 를 이름으로 쓰는 키. 작업 정보가 들어 있습니다 |
| Boot · Logon · Plain | GUID 이름의 하위 키만 있고 값은 없었습니다 (확인 범위: Win11 25H2 한 대) |
| Maintenance | winreg-kb 목록에는 없습니다. Win11 25H2 한 대에서 보였고, 역시 GUID 하위 키만 있었습니다 |

### Windows 버전별 차이

| Windows | 작업 정보를 담는 곳 | DynamicInfo 크기 |
|---|---|---|
| XP | `HKLM\Software\Microsoft\SchedulingAgent` ([옛 작업 파일](job-at.md) 참고) | 없음 |
| Vista · 2008 · 7 | `Schedule\TaskCache` | 28바이트 |
| 8 · 10 | `Schedule\TaskCache` | 36바이트 |
| 11 25H2 | `Schedule\TaskCache` (Maintenance 하위 키도 있음) | 36바이트 (확인 범위: 한 대) |

## 구조

### Tree\<작업 경로>

Tree 아래 키 경로는 Tasks\{GUID} 의 Path 값을 Tree 뒤에 붙인 것입니다. 예를 들어 Path 가 `\Microsoft\Windows\Media Center\ehDRMInit` 이면 키는 `Tree\Microsoft\Windows\Media Center\ehDRMInit` 입니다.

| 값 | 뜻 |
|---|---|
| Id | Tasks 아래 항목의 GUID |
| Index | winreg-kb 문서에 뜻이 비어 있습니다 |
| SD | 보안 설명자 (Security Descriptor) |

폴더에 해당하는 Tree 키에는 Id 가 없고 SD 값만 있었습니다. 한 PC 에서 이런 키가 142개였습니다. (확인 범위: Win11 25H2 한 대)

**SD 값.** 한 PC 에서 SD 는 148바이트, 152바이트 같은 REG_BINARY 였습니다. 자기 상대형 (self-relative) 보안 설명자로 풀면 다음과 같은 SDDL 문자열이 나왔습니다. (확인 범위: Win11 25H2 한 대)

```
O:BAG:SYD:(A;ID;0x1f019f;;;BA)(A;ID;0x1f019f;;;SY)(A;ID;FA;;;BA)(A;;FR;;;SY)
```

`O:` 뒤는 소유자, `G:` 뒤는 그룹, `D:` 뒤의 괄호들은 접근 허용 항목입니다. `BA` 는 Administrators 그룹, `SY` 는 SYSTEM 계정을 가리키는 약어입니다. SID 표기는 [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md)에서 다룹니다. 작업 키에 SD 값이 없을 때 무슨 일이 생기는지는 [숨긴 예약 작업 찾기 (SD 값 삭제)](sd.md)에서 다룹니다.

**Index 값.** 공식 뜻은 이번 조사에서 확인하지 못했습니다. 한 PC 에서는 Index 값과, 같은 GUID 가 들어 있는 하위 키가 이렇게 맞았습니다. (확인 범위: Win11 25H2 한 대)

| Index | 작업 키 수 | 같은 GUID 가 있던 하위 키 |
|---|---|---|
| 1 | 23 | Boot |
| 2 | 40 | Logon |
| 3 | 206 | Plain |
| 0 | 37 | 없음 (Tasks 에도 없음) |

Maintenance 에 있는 GUID 는 위 하위 키와 겹쳤습니다. Plain 과 겹친 것이 53개, Logon 과 겹친 것이 3개, Boot 와 겹친 것이 1개였습니다.

Index 가 0 인 37개는 Id 의 GUID 가 Tasks·Boot·Logon·Plain·Maintenance 어디에도 없었습니다. XML 파일도 없었고, Get-ScheduledTask 에도 나오지 않았습니다. 예를 들면 `\Microsoft\Windows\Application Experience\AitAgent` 가 이랬습니다. 없어진 작업의 Tree 키가 남은 것으로 보입니다.

### Tasks\{GUID}

winreg-kb 문서는 값으로 DynamicInfo, Hash, Path, Triggers 를 적습니다. 한 PC 의 한 작업에는 값이 더 있었습니다. (확인 범위: Win11 25H2 한 대)

| 값 | 형식 (관찰) | 뜻 |
|---|---|---|
| Path | REG_SZ | Tree 아래 대응 키의 상대 경로 |
| Hash | REG_BINARY | XML 파일의 무결성 해시 |
| Schema | REG_DWORD | XML 의 version 속성과 짝을 이룹니다 (관찰) |
| Author | REG_SZ | |
| Description | REG_SZ | |
| URI | REG_SZ | |
| Triggers | REG_BINARY | 트리거 (바이너리) |
| Actions | REG_BINARY | 동작 (바이너리) |
| DynamicInfo | REG_BINARY | 등록·실행 시각 |

Boot·Logon·Plain·Maintenance 아래 GUID 키에는 값이 없었습니다. 작업 정보는 모두 Tasks 쪽에서 읽습니다.

### Hash

Hash 는 `System32\Tasks` 에 있는 XML 파일의 무결성 해시입니다. 알고리즘은 SHA-256 이고(KB2305420 이전에는 CRC32 였습니다), 파일 앞의 BOM(`FF FE`)은 계산에서 뺍니다.

한 PC 에서 Hash(32바이트) 269개가 모두 "BOM 을 뺀 XML 의 SHA-256" 과 같았습니다. BOM 을 넣고 계산한 해시와는 한 건도 맞지 않았습니다. (확인 범위: Win11 25H2 한 대)

그래서 Hash 로 XML 파일을 검증할 수 있습니다. 두 값이 다르면 레지스트리에 적힌 해시와 지금 파일 내용이 다르다는 뜻입니다. 파일을 따로 고쳤거나 바꿔 넣었는지 따져 봅니다.

### Schema

한 PC 에서 Schema 값과 XML version 속성은 이렇게 짝을 이뤘습니다. (확인 범위: Win11 25H2 한 대)

| Schema (10진) | 16진 | XML version |
|---|---|---|
| 65538 | 0x00010002 | 1.2 |
| 65539 | 0x00010003 | 1.3 |
| 65540 | 0x00010004 | 1.4 |
| 65542 | 0x00010006 | 1.6 |

16진으로 바꾸면 위쪽 2바이트는 소수점 앞 숫자(1)와 같고, 아래쪽 2바이트는 소수점 뒤 숫자와 같습니다. version 속성이 없는 XML 179개는 Schema 값도 없었습니다. version 이 1.6 인데 Schema 값이 없는 작업도 9개 있었습니다.

### DynamicInfo

DynamicInfo 는 시각 값이 들어 있는 바이너리입니다. 크기는 Windows 버전에 따라 다릅니다. 아래 표의 뜻은 winreg-kb 문서를 따르고, 필드 이름은 libyal 의 파서 정의(task_cache.yaml)를 따릅니다.

| 오프셋 | 크기 | winreg-kb 문서의 뜻 | libyal 필드 이름 | 관찰 (Win11 25H2 한 대) |
|---|---|---|---|---|
| 0 | 4 | 값 3. 뜻 모름 | unknown1 | 269개 모두 3 |
| 4 | 8 | FILETIME. "마지막 등록 또는 갱신 시각?" (문서가 물음표로 적음). 없으면 0 | last_registered_time | 아래 "시각 해석" |
| 12 | 8 | FILETIME. "실행 시각?" (물음표). 없으면 0 | launch_time | 마지막 실행 시각, UTC |
| 20 | 4 | 뜻 모름 (플래그?) | unknown2 | 269개 모두 0 |
| 24 | 4 | 뜻 모름 | unknown3 | |
| 28 | 8 | FILETIME. 뜻 모름. Windows 8·10 에서 추가 | unknown_time | 아래 "시각 해석" |

Vista·2008·7 은 오프셋 0~27 의 28바이트입니다. Windows 8·10 은 오프셋 28 의 8바이트가 더해진 36바이트입니다. 한 PC(Win11 25H2)의 DynamicInfo 269개는 모두 36바이트였습니다.

winreg-kb 문서의 예시 헥스에서 오프셋 20 값은 Windows 7 예가 `2b 04 07 80`(0x8007042B), Windows 8·10 예가 `20 04 07 80`(0x80070420) 입니다. 이 값이 오류 코드인지는 이번 조사에서 확인하지 못했습니다.

### Actions · Triggers

두 값의 공개 명세는 이번 조사에서 찾지 못했습니다. 아래는 한 PC 에서 본 모습입니다. (확인 범위: Win11 25H2 한 대)

Actions 269개는 모두 첫 2바이트가 `03 00` 이었습니다. 한 Actions 값은 `03 00`, `0C 00 00 00`(12), UTF-16 문자열 `Author`, `66 66` 순서로 시작했고, 12 는 `Author` 여섯 글자를 UTF-16 으로 쓴 바이트 수와 같습니다. 그 뒤에는 명령 경로와 인자가 UTF-16 문자열로 들어 있었으며, XML 의 `<Actions Context="Author">`, Command, Arguments 와 같은 글자였습니다.

winreg-kb 문서는 Triggers 값 안의 FILETIME 이 현지 시각으로 보인다고 적었습니다.

## 증거로서 의미

**증명하는 것**

- Tree 키의 Id 가 가리키는 GUID 가 Tasks 에 있으면, 작업 스케줄러가 알고 있는 작업입니다. 한 PC 에서 Tasks 하위 키 수(269)와 Get-ScheduledTask 결과 수(269)가 같았습니다. (확인 범위: Win11 25H2 한 대)
- DynamicInfo 오프셋 12 는 마지막 실행 시각입니다. 한 PC 에서 한 번 이상 실행된 작업 175개 모두 이 값이 Get-ScheduledTaskInfo 의 LastRunTime(UTC)과 초 단위까지 같았습니다. (확인 범위: Win11 25H2 한 대)
- Actions 값에 명령 경로와 인자가 문자열로 남아서, XML 파일이 없을 때 실행 대상을 찾는 단서가 됩니다.
- Hash 로 지금의 XML 파일이 레지스트리에 적힌 내용과 같은지 확인할 수 있습니다.

**증명하지 못하는 것**

- 누가 등록했는지는 여기서 확정하지 못합니다. Author 는 문자열 값입니다. 등록한 계정은 [예약 작업 이벤트](../../event-logs/taskscheduler-4698.md)에서 찾습니다(켜 둔 경우).
- 오프셋 12 는 마지막 한 번의 실행 시각입니다. 이 값만으로는 그 전에 몇 번, 언제 실행했는지 알 수 없습니다.
- 오프셋 4 를 작업을 처음 만든 시각으로 단정하지 못합니다. 문서도 물음표로 적었고, 기본 작업에서는 OS 설치보다 앞선 날짜가 나왔습니다.
- 실행이 성공했는지는 여기서 알 수 없습니다. 오프셋 20 과 28 의 뜻이 확정되지 않았습니다.

보고서에는 "`Tasks\{GUID}` 의 DynamicInfo 에 이 작업의 마지막 실행 시각이 `<UTC 시각>` 으로 남아 있다" 처럼 씁니다. "이 시각에 악성 프로그램이 실행되었다" 는 실행 흔적을 따로 확인한 다음에 씁니다.

## 시각 해석

| 값 | 형식 | 기준 | 읽는 법 |
|---|---|---|---|
| DynamicInfo 오프셋 4 | FILETIME | UTC 로 읽을 때 XML 파일 기록 시각과 맞았습니다 (관찰) | 마지막 등록·갱신 시각으로 보입니다. 확정은 아닙니다 |
| DynamicInfo 오프셋 12 | FILETIME | UTC (관찰) | 마지막 실행 시각. 실행한 적 없으면 0 |
| DynamicInfo 오프셋 28 | FILETIME | 확인 못 함 | 뜻 모름 |
| Triggers 안의 시각 | FILETIME | 현지 시각으로 보임 (winreg-kb) | 트리거에 적은 시각 |

FILETIME 을 사람이 읽는 시각으로 바꾸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다. 현지 시각 값은 [시간대 설정](../../system-account/time-zone.md)을 보고 바꿉니다.

한 PC 에서 본 모습은 다음과 같습니다. (확인 범위: Win11 25H2 한 대)

- **오프셋 4.** Windows 기본 작업 153개에서 2024-05-25 (UTC) 였습니다. OS 설치 시각(2026-06-26)보다 앞섭니다. 설치 이미지에 미리 등록해 둔 시각이 남은 것으로 보입니다.
- **오프셋 4 와 XML 파일.** 여러 작업에서 오프셋 4 의 시각과 XML 파일의 마지막 기록 시각(UTC)이 초 단위까지 같았습니다. 모든 작업이 이렇지는 않았습니다.
- **오프셋 28.** 0 인 것이 100개, 오프셋 12 와 같거나 늦은 것이 159개였습니다. 늦은 것은 대개 몇 초 뒤였습니다. 오프셋 12 보다 이른 것도 10개 있었습니다. 마지막 완료 시각으로 보이지만 확인하지 못했습니다.

한 번도 실행하지 않은 작업을 PowerShell 로 조회하면 특이한 날짜가 나옵니다. 이 내용은 [옛 작업 파일 (.job·at)](job-at.md)의 상태 값 절에서 다룹니다.

## 함정과 한계

- **Tree 키 수는 작업 수가 아닙니다.** 폴더 키가 있고, 없어진 작업의 키(Index 0)도 남습니다. 한 PC 에서 Id 가 있는 Tree 키는 306개였고, 작업은 269개였습니다. (확인 범위: Win11 25H2 한 대)
- **Maintenance 는 다른 하위 키와 겹칩니다.** Boot·Logon·Plain·Maintenance 의 GUID 를 더하면 작업 수보다 커집니다.
- **오프셋 4 는 작업 생성 시각이 아닐 수 있습니다.** 기본 작업은 OS 설치보다 이른 날짜가 나옵니다.
- **REG_DWORD 표시에 주의합니다.** 값을 문자열로 받는 도구는 REG_DWORD 를 부호 없는 10진수로 보여 줍니다. Schema 같은 값은 원시 바이트로 확인합니다.
- **옛 시스템의 Hash 는 CRC32 입니다.** KB2305420 이전 시스템에서는 SHA-256 으로 비교하면 맞지 않습니다.
- **Actions·Triggers 해석은 관찰에 기댑니다.** 공개 명세를 찾지 못했습니다. 같은 작업의 XML 과 맞춰 보며 읽습니다.
- **Index 의 뜻은 확정되지 않았습니다.** Index 를 0 으로 바꾸면 작업이 숨는지도 확인하지 못했습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 DynamicInfo 예시(36바이트)입니다. 실제 검체에서 뽑은 값이 아닙니다.

```
00000000  03 00 00 00 00 eb c8 bf e6 6e da 01 80 70 5e 3e  |.........n...p^>|
00000010  59 6f da 01 00 00 00 00 00 00 00 00 80 ca c0 40  |Yo.............@|
00000020  59 6f da 01                                      |Yo..|
```

1. 0x00 의 `03 00 00 00` 은 3 입니다.
2. 0x04 의 8바이트 `00 eb c8 bf e6 6e da 01` 을 리틀 엔디언으로 읽으면 `0x01DA6EE6BFC8EB00` 입니다. FILETIME 으로 바꾸면 2024-03-05 10:20:30 (UTC) 입니다.
3. 0x0C 의 8바이트 `80 70 5e 3e 59 6f da 01` 은 `0x01DA6F593E5E7080` 입니다. 2024-03-06 00:00:05 (UTC) 이고, 마지막 실행 시각입니다.
4. 0x14 와 0x18 의 4바이트 두 칸은 0 입니다.
5. 0x1C 의 8바이트 `80 ca c0 40 59 6f da 01` 은 `0x01DA6F5940C0CA80` 입니다. 2024-03-06 00:00:09 (UTC) 이고, 뜻이 확정되지 않은 칸입니다.

### 공개 도구로 한 번

오프라인 하이브는 공개 레지스트리 뷰어로 열어 값을 바이트로 꺼냅니다. libyal 의 winreg-kb 저장소에는 TaskCache 구조를 적은 정의 파일(task_cache.yaml)이 있습니다.

꺼낸 바이트는 Python 표준 라이브러리로 풀 수 있습니다.

```python
import datetime, hashlib, struct

EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)

def filetime(v):
    return None if v == 0 else EPOCH + datetime.timedelta(microseconds=v // 10)

def dynamic_info(b):                      # b: DynamicInfo 값의 바이트
    unk1, off4, off12, off20, off24 = struct.unpack_from("<IQQII", b, 0)
    out = {"offset0": unk1, "offset4": filetime(off4),
           "offset12_last_run": filetime(off12), "offset20": hex(off20)}
    if len(b) >= 36:                      # Windows 8 이후
        out["offset28"] = filetime(struct.unpack_from("<Q", b, 28)[0])
    return out

def xml_hash(path):                       # Tasks\{GUID} 의 Hash 와 비교할 값
    data = open(path, "rb").read()
    if data[:2] == b"\xff\xfe":           # BOM 은 빼고 계산합니다
        data = data[2:]
    return hashlib.sha256(data).hexdigest()
```

살아 있는 시스템에서는 PowerShell 로 같은 값을 읽을 수 있습니다. 아래 결과를 `Get-ScheduledTaskInfo` 의 LastRunTime 과 맞춰 봅니다.

```powershell
$k = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tasks'
Get-ChildItem $k | ForEach-Object {
  $p = Get-ItemProperty $_.PSPath
  if (-not $p.DynamicInfo) { return }
  $run = [BitConverter]::ToInt64($p.DynamicInfo, 12)
  [pscustomobject]@{
    Path       = $p.Path
    LastRunUtc = if ($run) { [DateTime]::FromFileTimeUtc($run) } else { $null }
  }
}
```

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 작업 정의 XML | Path 로 파일을 찾고 Hash 로 내용을 검증합니다 | [작업 정의 파일](system32-tasks-xml.md) |
| Tree 의 SD 값 | SD 가 없는 작업 키는 숨긴 작업일 수 있습니다 | [숨긴 예약 작업 찾기](sd.md) |
| 예약 작업 이벤트 | 등록한 계정과 등록 시각 (켜 둔 경우) | [예약 작업 이벤트](../../event-logs/taskscheduler-4698.md) |
| 프리페치 · 프로세스 생성 | 오프셋 12 무렵에 Actions 의 프로그램이 실행됐는지 | [프리페치](../../execution/prefetch/index.md), [프로세스 생성 (4688)](../../event-logs/4688.md) |
| 시스템 기본 정보 | OS 설치 시각과 오프셋 4 비교 | [시스템 기본 정보](../../system-account/os-version-computer-name-install-date-shutdown-t.md) |
| 섀도 복사본 | 예전 SOFTWARE 하이브의 TaskCache 와 비교 | [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

## 실습

공개 검체(NIST CFReDS 등)의 SOFTWARE 하이브와 `System32\Tasks` 폴더로 아래 질문을 풀어 봅니다.

1. Tree 아래 키 가운데 Id 가 있는 키와 없는 키는 각각 몇 개입니까?
2. Id 의 GUID 가 Tasks 에 없는 Tree 키가 있습니까? 그 키의 Index 는 몇입니까?
3. 작업 하나를 골라 BOM 을 뺀 XML 의 SHA-256 을 계산합니다. Hash 값과 같습니까?
4. DynamicInfo 오프셋 12 가 가장 늦은 작업은 무엇입니까? 그 시각 무렵 Actions 의 프로그램이 프리페치에 남아 있습니까?
5. 오프셋 4 가 OS 설치 시각보다 이른 작업은 몇 개입니까?

## 참고 문헌

1. Microsoft Security Blog, "Tarrask malware uses scheduled tasks for defense evasion" (2022-04-12). https://www.microsoft.com/en-us/security/blog/2022/04/12/tarrask-malware-uses-scheduled-tasks-for-defense-evasion/
2. libyal winreg-kb, "Task scheduler". https://github.com/libyal/winreg-kb/blob/main/docs/sources/system-keys/Task-scheduler.md
3. libyal winreg-kb, task_cache.yaml (Task Scheduler Cache dtFabric 정의). https://github.com/libyal/winreg-kb/blob/main/winregrc/task_cache.yaml
