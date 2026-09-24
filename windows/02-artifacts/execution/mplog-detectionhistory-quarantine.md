# 디펜더 검사 로그·격리 파일 (MPLog·DetectionHistory·Quarantine)

## 한 줄 요약

Microsoft Defender 바이러스 백신은 `C:\ProgramData\Microsoft\Windows Defender` 아래에 파일 흔적을 세 가지 남깁니다. 검사 로그 MPLog 에는 탐지가 없어도 프로세스 이름과 파일 경로가 남습니다. 보호 기록 (DetectionHistory) 에는 탐지 한 건마다 파일이 하나씩 생깁니다. 격리 폴더 (Quarantine) 에는 격리한 파일의 원본 내용이 암호화된 채 남습니다.

## 무엇을 기록하나 · 왜 생기나

| 흔적 | 무엇을 기록하나 | 언제 생기나 |
|---|---|---|
| MPLog | 검사 성능, 파일 해시, 탐지를 적은 텍스트 로그 | Defender 가 동작하는 동안 이어서 씁니다 |
| DetectionHistory | 탐지 한 건의 위협 이름, 파일, 해시, 사용자, 부모 프로세스 | 실시간 보호 (Real-Time Protection, RTP) 가 위협을 잡을 때 |
| Quarantine | 격리한 파일의 원래 경로, 탐지 정보, 원본 내용 | 탐지한 파일을 격리할 때 |

- MPLog 는 Windows Defender 나 Microsoft Security Essentials 가 만드는 텍스트 로그입니다.
- DetectionHistory 는 실시간 보호가 PUA·바이러스·트로이 목마 같은 위협을 잡을 때 생깁니다. 사용자가 그 파일을 실행했는지와는 관계가 없습니다.
- DetectionHistory 파일은 Windows 보안 > 바이러스 및 위협 방지 > "보호 기록 (Protection History)" 에 보이는 항목의 원본입니다.
- 격리 폴더에서는 원본 파일을 되살릴 수 있습니다. 그래서 공격자가 떨어뜨린 도구의 원본을 되찾는 통로가 됩니다.

Defender 는 운영 이벤트 로그에도 탐지 (1116) 와 조치 (1117) 를 남깁니다. 이 페이지는 파일 쪽만 다룹니다. 이벤트는 [Windows Defender 탐지](../event-logs/1116-1117.md) 에서 다룹니다.

## 위치와 버전별 차이

### 위치

| 흔적 | 위치 |
|---|---|
| MPLog | `C:\ProgramData\Microsoft\Windows Defender\Support\MPLog-*` |
| DetectionHistory | `C:\ProgramData\Microsoft\Windows Defender\Scans\History\Service\DetectionHistory\<번호 폴더>\<GUID>` |
| Quarantine | `C:\ProgramData\Microsoft\Windows Defender\Quarantine\` 아래 `Entries`, `ResourceData`, `Resources` |

`Windows Defender` 폴더 아래에서는 하위 폴더 13개를 봤습니다. (확인 범위: Windows 11 25H2, PC 한 대)

```
Certificates, Clean Store, Definition Updates, Features, LocalCopy, Models,
Network Inspection System, Payloads, Platform, Quarantine, Scans, Snapshots, Support
```

### 버전에 따라 달라지는 점

| 항목 | 내용 | 근거 |
|---|---|---|
| MPLog 를 만드는 제품 | Windows Defender 또는 Microsoft Security Essentials | CrowdStrike |
| MPLog 줄 형식 | 시기마다 바뀝니다. 언제 쓰였느냐에 따라 칸이 더 많거나 적습니다 | CrowdStrike |
| DetectionHistory | 적어도 Windows 10 에서 생깁니다 | defender-detectionhistory-parser |
| 그룹 정책 경로 | Windows 10 2004 (2020년 5월) 전에는 경로에 Microsoft 대신 Windows Defender Antivirus 라는 이름이 쓰였을 수 있습니다 | Microsoft Learn |
| 관찰한 PC | Windows 11 25H2 (빌드 26200), Defender Product 4.18.26080.3 / Engine 1.1.26080.3. 세 폴더가 모두 위 위치에 있었습니다 | 관찰 (PC 한 대) |

## 구조

### MPLog

| 항목 | 내용 |
|---|---|
| 파일 이름 | `MPLog-YYYYMMDD-HHMMSS.log` (관찰 예: `MPLog-20260907-063545.log`) |
| 인코딩 | UTF-16LE 텍스트. 파일 앞 2바이트가 `FF FE` 입니다 (관찰) |
| 시각 | UTC |

인코딩을 읽는 방법은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다. 관찰한 PC 의 `Support` 폴더에는 MPLog 말고도 다음 파일이 있었습니다. (확인 범위: Windows 11 25H2, PC 한 대)

- `MPDetection-*.log` (UTF-16LE)
- `MPDeviceControl-*.log`, `MPScanSkip-*.log`
- `MpWppCoreTracing-*.bin`, `MpWppTracing-*.bin`, `MpWppUpdateLogging-*.bin`

#### 줄 종류

CrowdStrike 는 포렌식에 쓸 만한 줄을 네 가지로 나눕니다.

| 줄 종류 | 들어 있는 칸 | 알려 주는 것 |
|---|---|---|
| 성능 영향 (EstimatedImpact) | ProcessImageName, TotalTime, Count, MaxTime, MaxTimeFile, EstimatedImpact | 그 프로세스가 실행됐고 파일에 접근했습니다 |
| SDN | 파일 전체 경로, Sha1, Sha2 (SHA-256) | 그 파일이 디스크에 있었습니다. 해시도 알려 줍니다 |
| 탐지 | 시각 (UTC), 탐지명, PID, ProcessStart, File (전체 경로) | 어느 프로세스와 파일에서 무엇을 탐지했는지 |
| EMS 탐지 | 프로세스 이름, PID, 탐지명 | 메모리 검사로 잡은 프로세스 주입 |

성능 영향 줄의 칸은 다음 뜻입니다.

| 칸 | 뜻 |
|---|---|
| ProcessImageName | 실행 파일 이름 |
| TotalTime | 그 프로세스가 접근한 파일을 검사하는 데 쓴 누적 시간 (ms) |
| Count | 접근해서 검사한 파일 수 |
| MaxTime | 가장 오래 걸린 검사 한 번의 시간 (ms) |
| MaxTimeFile | 그 검사의 파일 경로 |
| EstimatedImpact | 프로세스가 활동한 시간 가운데 검사에 쓴 비율 (%) |

관찰한 PC 에서는 성능 영향 줄이 다음 모양이었습니다. 실행 파일 이름과 경로 뒷부분은 줄였습니다. (확인 범위: Windows 11 25H2, PC 한 대)

```
ProcessImageName: <이름>.exe, Pid: 11536, TotalTime: 24424254, Count: 4341109, MaxTime: 93, MaxTimeFile: \Device\HarddiskVolume3\..., EstimatedImpact: 37%
```

- 원문 목록에 없는 `Pid` 칸이 있었습니다.
- 경로는 드라이브 문자가 아니라 `\Device\HarddiskVolumeN` 장치 경로로 적혀 있었습니다.
- 약 16일 분량의 MPLog 한 개에 성능 영향 줄이 16,462개 있었습니다.
- `SDN:` 으로 시작하는 줄은 0개였습니다.

#### 관찰한 다른 줄

아래 줄은 확인한 자료에 설명이 없습니다. 모양만 적습니다. (확인 범위: Windows 11 25H2, PC 한 대)

```
[RTP] [Mini-filter] Unsuccessful scan status(#n): <경로>. Process: <경로>, Status: 0x...
[RTP] [MpRtp] Engine VFZ lofi/sample/expensive: <경로>. status=..., threatid=0x80000000, sigseq=...
ReportLowfi(<경로>, 0x...)
Engine:command line reported as lowfi: <명령줄>
Detection State: Finished(0) Failed(0) CriticalFailed(0) Additional Actions(0)
```

- `Engine:command line reported as lowfi` 줄에는 명령줄이 통째로 남았습니다. 이 줄이 어떤 조건에서 생기는지는 확인하지 못했습니다.
- 서비스가 시작될 때 격리 복구 블록이 남았습니다. `Beginning quarantine recovery` 로 시작해 `Quarantine ID:{...}`, `Target:`, `Flags:131074`, `Start time:09-07-2026 06:05:24` 가 이어지고 `Finished quarantine recovery` 로 끝났습니다.
- `MPDetection-*.log` 에는 서비스 시작 줄과 버전 줄이 있었습니다. 서비스 시작 줄은 `Service started - Microsoft Defender 바이러스 백신 (GUID)` 처럼 OS 표시 언어로 적혀 있었습니다. 버전 줄은 `Version: Product 4.18.26080.3 Service ... Engine 1.1.26080.3 AS 1.457.348.0 AV 1.457.348.0` 모양이었습니다.

MPLog 가 몇 개까지 남는지, 언제 새 파일로 넘어가는지는 확인하지 못했습니다.

### DetectionHistory

| 항목 | 내용 |
|---|---|
| 파일 이름 | GUID (예: `8CC4BE3D-8D3F-4952-9953-F24EB6638A37`) |
| 파일 머리 | 앞 5바이트가 `08 00 00 00 08` 입니다. 공개 파서는 머리가 다르면 파일을 거부합니다 |
| GUID 저장 | 앞 세 덩어리는 바이트 순서를 뒤집어 저장합니다 |
| 칸 구분 | ASCII 콜론 (`0x3A`) |
| 구역 | 세 구역이 서로 다른 방식으로 적혀 있습니다. 3구역 구분자는 `0A 00` 입니다 |

GUID 의 바이트 순서는 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에서 다룹니다.

| 구역 | 칸 |
|---|---|
| 1구역 | DetectionHistory GUID, Magic Version, ThreatStatusID (오프셋 `0xF0`), "Threat Type / Threat Name", 파일 이름 |
| 2구역 | ThreatTrackingId, ThreatTrackingSha256, ThreatTrackingMD5, ThreatTrackingSha1, ThreatTrackingStartTime (FILETIME, UTC), ThreatTrackingSize, ThreatTrackingThreatId, ThreatTrackingScanSource, ThreatTrackingScanType. PUA 는 regkey·uninstall 칸이 더 붙을 수 있습니다 |
| 3구역 | User (도메인\사용자), SpawningProcess (예: explorer.exe), SecurityGroup (있을 때만) |

관찰한 PC 의 `Scans` 폴더에서는 다음을 봤습니다. 모두 확인한 자료에 설명이 없어 뜻을 풀지 않습니다. (확인 범위: Windows 11 25H2, PC 한 대)

- `DetectionHistory` 아래에 `00`, `03`, `04` … `18` 같은 두 자리 숫자 폴더가 있었습니다. 폴더 안 파일은 0개였습니다.
- `History\Service` 폴더에 `Detections.log`, `Unknown.Log`, `History.Log` 가 있었습니다. 셋 다 UTF-16LE 였습니다.
- `Detections.log` 의 줄은 `2147893196|containerfile|C:\...`, `2147893196|file|C:\...` 처럼 "숫자|종류|경로" 모양이었습니다.
- `Unknown.Log` 에는 숫자만 한 줄씩 있었습니다.
- `Scans\History` 아래에 `CacheManager`, `RemCheck`, `ReportLatency`, `Results` (`Quick`, `Resource`), `Store` 폴더가 있었습니다.
- `Scans` 폴더에 `mpenginedb.db` (SQLite, `-wal`·`-shm` 파일이 함께 있음), `mpcache-*.bin` 여러 개, `DefenderEcsCache.bin64`, `MpDiag.bin` 이 있었습니다.

### Quarantine

| 하위 폴더 | 담는 것 |
|---|---|
| `Entries` | GUID 이름의 메타데이터 파일 |
| `ResourceData` | 격리한 원본 내용. 해시 이름의 파일이 이름 앞 두 글자 하위 폴더에 들어갑니다 (예: `ResourceData\5D\5D92927E35A6D8FECE000ABB9739F5AEFF914A3E`) |
| `Resources` | 항목과 원본 내용 파일을 이어 주는 메타데이터 |

- 폴더 안 파일은 모두 고정 키 RC4 로 암호화돼 있습니다.
- 키는 256바이트입니다. `0x1E, 0x87, 0x78, 0x1B, 0x8D` … 로 시작해 … `0x82, 0x53` 으로 끝납니다.
- `Entries` 파일은 따로 암호화한 세 덩어리로 되어 있습니다. 풀면 원래 전체 경로, 탐지 정보, 시각이 나옵니다. `ResourceData` 파일과 짝지을 해시도 나옵니다.
- `ResourceData` 파일을 풀면 원본 앞뒤에 메타데이터가 붙어 있습니다. 이것을 떼어 내야 원본 파일이 됩니다.
- 오프셋과 칸 단위의 구조는 확인한 자료에 없습니다.

관찰한 PC 에서는 다음을 봤습니다. (확인 범위: Windows 11 25H2, PC 한 대)

- `Entries`, `ResourceData`, `Resources` 의 파일 수가 모두 11개로 같았습니다.
- `ResourceData` 파일 이름은 40자리 16진수였습니다. SHA-1 과 길이가 같습니다.
- `ResourceData` 파일 크기는 249바이트에서 215MB 까지 다양했습니다. 원본 크기를 따라가는 것으로 보였습니다.
- `Entries` 파일 이름은 `{80063FCC-0000-0000-…}` 모양이었습니다. 앞 8자리 16진수 `0x80063FCC` 는 10진수로 2147893196 입니다. `Detections.log` 의 앞머리 숫자와 같았습니다. 모든 항목이 이렇게 맞는다는 근거는 없습니다.

### 보관 기간과 조치 정책

Microsoft 문서에 나오는 설정입니다. 기본값은 문서마다 다르게 적혀 있습니다. 그룹 정책 설명 문서는 검사 기록 30일, 격리 90일이라고 적었습니다. `Set-MpPreference` 명령 설명서는 검사 기록 15일이라고 적었고, 격리는 값을 주지 않으면 지우지 않는다고 적었습니다. 검체에서는 실제 설정 값을 확인합니다.

| 설정 | 그룹 정책 이름 | 그룹 정책 문서의 기본값 | PowerShell |
|---|---|---|---|
| 검사 기록 보관 | "Turn on removal of items from scan history folder" (Scan 아래) | 30일 | `Set-MpPreference -ScanPurgeItemsAfterDelay`. 0 이면 지우지 않습니다 |
| 격리 보관 | "Configure removal of items from Quarantine folder" (Quarantine 아래) | 90일 | `Set-MpPreference -QuarantinePurgeItemsAfterDelay`. 0 이면 지우지 않습니다 |
| 복원 지점 | "Create a system restore point" | Disabled | 켜면 치료·검사 전에 하루 한 번 복원 지점을 만듭니다 |

- 조치 종류는 Clean, Quarantine, Remove, Allow, User defined, Block 입니다. Allow 는 치료하지 않고, 뒤이은 탐지 이벤트도 막습니다.
- 그룹 정책의 위협 수준 값은 1 Low, 2 Medium, 4 High, 5 Severe 입니다.
- 그룹 정책의 조치 값은 2 Quarantine, 3 Remove, 6 Ignore, 11 None 입니다.
- Ignore (6) 와 None (11) 은 둘 다 치료하지 않습니다. Ignore 는 뒤이은 탐지 이벤트를 막습니다. None 은 경고와 보호 기록 항목을 계속 남깁니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| MPLog 성능 영향 줄: 그 이름의 프로세스가 실행됐고 파일에 접근했습니다 | 누가 실행했는지. 원문의 칸 목록에도, 관찰한 줄에도 사용자 칸이 없습니다 |
| MPLog SDN 줄: 그 경로에 파일이 있었고, 해시가 그 값이었습니다 | 그 파일을 실행했는지 |
| MPLog 탐지 줄·EMS 탐지 줄: Defender 가 그 탐지명으로 잡았습니다 | 파일이 실제로 악성인지. 오탐일 수 있습니다 |
| DetectionHistory: 실시간 보호가 그 파일을 잡았습니다. 해시, 사용자, 부모 프로세스도 알려 줍니다 | 사용자가 그 파일을 실행했는지. 실행하지 않아도 생깁니다 |
| Quarantine: 그 경로의 파일을 격리했습니다. 원본 내용을 되찾을 수 있습니다 | 격리 전에 그 파일이 실행됐는지 |

- 성능 영향 줄은 탐지가 없어도 남습니다. 프리페치가 꺼진 서버 같은 곳에서는 실행을 보여 주는 보조 근거가 됩니다.
- 기록이 없다고 탐지가 없었다고 단정하지 않습니다. 보관 기간이 지나면 DetectionHistory 와 격리 파일이 지워집니다. 보관 기간은 정책으로 바꿀 수 있습니다.

### 보고서 문장

아래 이름과 숫자는 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "MPLog 에 `tool.exe` 의 성능 영향 줄이 있습니다. 줄 앞머리 시각은 2025-03-10 02:14:07 UTC 입니다. 이 줄의 Count 는 1200 입니다. 이 프로세스가 접근한 파일 1,200개를 Defender 가 검사했다는 기록입니다."
- 쓰면 안 되는 문장: "사용자 A 가 2025-03-10 11:14 에 tool.exe 로 파일 1,200개를 열었습니다."

## 시각 해석

| 시각 | 어디에 남나 | 형식 | 기준 |
|---|---|---|---|
| MPLog 줄 앞머리 | 각 줄 | 원문 예 `2020-06-14T20:11:42.880Z`. 관찰한 줄은 `2026-09-07T06:05:24.539` 처럼 끝에 `Z` 가 없었습니다 | UTC |
| MPLog 탐지 줄의 시각 | 탐지 줄 | 확인한 자료에 형식 설명이 없습니다 | UTC |
| MPLog 탐지 줄의 ProcessStart | 탐지 줄 | CrowdStrike 는 웹킷 시각 형식이라고 적었습니다. 그런데 원문 예시 값 `132696072639875080` 은 18자리입니다. FILETIME 으로 풀면 2021-07-01 10:01:03 UTC 가 되고, 웹킷 (마이크로초) 으로 풀면 5805년이 됩니다. 두 방식으로 모두 풀어 보고 맞는 쪽을 고릅니다 | 확인한 자료에 없습니다 |
| 격리 복구 블록의 Start time | 서비스 시작 때 남는 블록 (관찰) | `09-07-2026 06:05:24` 처럼 월-일-년 순서 | 확인하지 못했습니다 |
| ThreatTrackingStartTime | DetectionHistory 2구역 | FILETIME | UTC |
| Entries 의 시각 | 풀어낸 `Entries` 파일 | 확인한 자료에 없습니다 | 확인한 자료에 없습니다 |

- 줄 앞머리에 `Z` 가 없어도 UTC 입니다. 관찰한 PC 에서 로그 마지막 줄은 11:36 이었습니다. 그때 한국 시각은 20:36 이었고 9시간 차이가 났습니다. (확인 범위: Windows 11 25H2, PC 한 대)
- 한 파일 안에서도 날짜를 적는 순서가 다릅니다. 줄 앞머리는 년-월-일, 격리 복구 블록은 월-일-년이었습니다.
- MPLog 파일 이름 속 날짜가 무엇을 기준으로 붙는지는 확인하지 못했습니다.
- FILETIME 과 웹킷 시각을 푸는 방법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다. 현지 시각으로 바꿀 때는 [시간대 설정](../system-account/time-zone.md) 을 봅니다.

## 함정과 한계

1. **탐지를 실행으로 읽습니다.** DetectionHistory 는 파일을 실행하지 않아도 생깁니다. 실행 여부는 성능 영향 줄이나 다른 실행 흔적으로 따로 확인합니다.
2. **Count 를 "사용자가 연 파일 수" 로 읽습니다.** Count 는 그 프로세스가 접근해서 Defender 가 검사한 파일 수입니다. 사용자가 파일을 하나하나 열었다는 뜻이 아닙니다.
3. **장치 경로를 그대로 적습니다.** MPLog 경로는 `\Device\HarddiskVolumeN` 형식입니다. 드라이브 문자로 바꿔 읽어야 합니다. 볼륨 번호와 드라이브 문자의 짝은 따로 확인합니다.
4. **칸 위치에 기대 파싱합니다.** MPLog 줄 형식은 시기마다 바뀝니다. 관찰한 줄에는 원문 목록에 없는 `Pid` 칸이 있었습니다. 칸 이름으로 값을 찾습니다.
5. **보통 방식으로 복사합니다.** 서비스가 켜져 있으면 MPLog 가 잠겨 있어 보통 방식으로는 열리지 않습니다. 관찰한 PC 에서는 공유 읽기 (`FileShare.ReadWrite`) 로는 읽혔습니다. (확인 범위: Windows 11 25H2, PC 한 대) 수집 방법은 [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) 에서 다룹니다.
6. **MPLog 가 오래된 기록까지 담는다고 봅니다.** 관찰한 PC 에는 약 24MB 의 MPLog 가 하나뿐이었고 약 16일 분량이었습니다. (확인 범위: Windows 11 25H2, PC 한 대) 옛 기록은 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 찾습니다.
7. **빈 DetectionHistory 를 "탐지 없음" 으로 읽습니다.** 관찰한 PC 에서는 DetectionHistory 파일이 0개였습니다. 같은 PC 의 7월 말 격리 항목은 남아 있었습니다. 검사 기록 보관 기간 (그룹 정책 문서 기준 30일) 이 격리 보관 기간 (90일) 보다 짧아서 먼저 지워진 것으로 보입니다. 이 PC 의 실제 설정 값은 확인하지 않았고, 이것은 추정입니다. (확인 범위: Windows 11 25H2, PC 한 대)
8. **영어 문구로만 검색합니다.** `MPDetection-*.log` 의 서비스 이름은 OS 표시 언어로 적혔습니다. 한국어 Windows 에서는 한국어 문구로도 검색합니다.

### 지우기와 조작

- **보호 기록 파일을 지웁니다.** DetectionHistory 파일을 지우면 보호 기록 화면의 알림도 사라집니다. 화면에 없어도 MPLog, [Windows Defender 탐지](../event-logs/1116-1117.md) 이벤트, 격리 폴더를 따로 봅니다.
- **보관 기간을 줄입니다.** 위 "보관 기간과 조치 정책" 의 두 설정을 짧게 바꾸면 기록이 빨리 지워집니다. 정책 값과 `Set-MpPreference` 설정을 함께 확인합니다.
- **조치를 바꿉니다.** Allow 와 조치 값 Ignore (6) 는 치료하지 않고 뒤이은 탐지 이벤트를 막습니다. 조치 값 None (11) 도 치료하지 않지만 경고와 보호 기록 항목은 남깁니다.
- **격리에서 복원합니다.** Microsoft 문서에 따르면 오탐으로 격리된 파일은 장치를 재부팅한 뒤 격리에서 복원할 수 있습니다. 복원한 뒤 격리 폴더에 무엇이 남는지는 확인하지 못했습니다.
- **파일을 직접 지웁니다.** 지운 로그와 격리 파일의 흔적은 [마스터 파일 테이블](../filesystem/mft.md) 과 [USN 변경 저널](../filesystem/usnjrnl.md) 에서 찾습니다. 지운 내용을 되살리는 방법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 세 예시는 명세와 관찰한 형식을 보고 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

**MPLog 앞부분**

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    FF FE 32 00 30 00 32 00 35 00 2D 00 30 00 33 00
0x10    2D 00 31 00 30 00 54 00 30 00 32 00 3A 00 31 00
```

1. 0x00 의 `FF FE` 는 UTF-16LE 표시입니다.
2. 0x02 부터 2바이트씩 읽습니다. `2025-03-10T02:1` … 입니다.
3. 시각 뒤에 `Z` 가 없어도 UTC 로 읽습니다.

**DetectionHistory 머리와 GUID**

```
오프셋  00 01 02 03 04
0x00    08 00 00 00 08
```

4. 앞 5바이트가 `08 00 00 00 08` 인지 봅니다. 다르면 DetectionHistory 파일이 아니거나 손상된 파일입니다.

GUID `8CC4BE3D-8D3F-4952-9953-F24EB6638A37` 은 파일 안에 다음 바이트로 들어갑니다. 파일 안 위치는 확인한 자료에 없어 적지 않습니다.

```
3D BE C4 8C  3F 8D  52 49  99 53  F2 4E B6 63 8A 37
```

5. 앞 세 덩어리 `3D BE C4 8C`, `3F 8D`, `52 49` 는 뒤집어 읽습니다. `8CC4BE3D`, `8D3F`, `4952` 입니다.
6. 뒤 두 덩어리 `99 53`, `F2 4E B6 63 8A 37` 은 그대로 읽습니다.
7. 칸 사이의 `3A` (콜론) 를 찾아 칸을 나눕니다. 3구역은 `0A 00` 뒤에서 시작합니다.
8. ThreatStatusID 는 오프셋 `0xF0` 에서 읽습니다.

**Quarantine**

격리 파일은 RC4 로 암호화돼 있어 헥스 편집기로 바로 읽히지 않습니다. 헥스 없이도 짝은 맞춰 볼 수 있습니다.

9. `ResourceData` 아래 하위 폴더 이름이 그 안 파일 이름의 앞 두 글자와 같은지 봅니다.
10. `Entries`, `ResourceData`, `Resources` 의 파일 수를 셉니다. 수가 다르면 지워졌거나 손상된 항목이 있는지 봅니다.

### 공개 도구로 한 번

- **MPLog**: 텍스트 파일입니다. UTF-16LE 를 읽는 편집기나 검색 도구로 엽니다. `EstimatedImpact`, `SDN:`, 탐지명으로 줄을 걸러 냅니다.
- **DetectionHistory**: 공개 도구 defender-detectionhistory-parser (Python) 가 세 구역을 풀어 줍니다. 머리가 `08 00 00 00 08` 이 아닌 파일은 거부합니다.
- **Quarantine**: 공개 도구 defender-dump (Python) 가 격리 목록을 보여 줍니다. `--dump` 를 주면 원본 파일을 `quarantine.tar` 로 묶어 꺼냅니다.
- 꺼낸 파일은 격리 전 원본입니다. 악성 코드일 수 있으므로 분석용으로 따로 떼어 둔 환경에서만 다룹니다.
- 도구가 보여 준 시각이 UTC 인지, 분석 PC 의 현지 시각인지 확인합니다.
- 파일 한두 개는 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [Windows Defender 탐지](../event-logs/1116-1117.md) | 탐지와 조치 이벤트의 시각, 탐지명 |
| [프리페치](prefetch/index.md) | 성능 영향 줄의 프로세스가 실행된 시각과 횟수 |
| [AmCache](amcache-hve/index.md) | 같은 실행 파일의 경로와 해시 |
| [프로세스 생성](../event-logs/4688.md) | 성능 영향 줄의 프로세스를 누가 언제 만들었는지 |
| [윈도 오류 보고](wer.md) | 같은 프로세스가 오류를 낸 기록 |
| [마스터 파일 테이블](../filesystem/mft.md) · [USN 변경 저널](../filesystem/usnjrnl.md) | 격리한 파일이 원래 경로에 생긴 때와 사라진 때 |
| [다운로드 출처 표시](../filesystem/zone-identifier.md) | 탐지한 파일을 어디서 받았는지 |
| [해시셋 대조와 유사 해시](../../03-techniques/analysis/hash-set-fuzzy-hash.md) | SDN 줄과 DetectionHistory 의 해시를 알려진 해시와 대조 |
| [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 보관 기간이 지나 사라진 DetectionHistory·격리 파일과 옛 MPLog |

여러 기록을 합쳐 읽는 순서는 [악성코드는 어디서 들어왔나](../../04-scenarios/incident/initial-access.md) 와 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md) 에서 다룹니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 Windows 10 이후의 이미지를 골라 다음을 풀어 봅니다.

1. `Windows Defender\Support` 폴더에 MPLog 가 몇 개 있습니까? 가장 이른 줄과 가장 늦은 줄의 시각 (UTC) 은 언제입니까?
2. 성능 영향 줄에서 EstimatedImpact 가 가장 큰 프로세스 다섯 개를 적어 봅니다. 그 가운데 프리페치나 AmCache 에 없는 프로세스가 있습니까?
3. SDN 줄이나 탐지 줄이 있습니까? 있다면 해시를 DetectionHistory 의 해시와 비교해 봅니다.
4. DetectionHistory 파일을 하나 골라 앞 5바이트와 GUID 를 직접 읽어 봅니다. 3구역의 사용자와 SpawningProcess 는 무엇입니까?
5. 격리 폴더의 세 하위 폴더 파일 수가 같습니까? 격리 항목의 원래 경로가 MFT 에 남아 있습니까?
6. 검체에서 검사 기록·격리 보관 기간 정책이 기본값에서 바뀌어 있는지 찾아봅니다. 정책 값이 레지스트리 어디에 남는지도 함께 확인해 봅니다.

실험용 가상 머신이 있으면 무해한 테스트 파일로 탐지를 일으켜 봅니다. 앞뒤로 세 폴더를 떠서 어떤 파일이 새로 생기는지 비교합니다. 결과에는 Windows 버전과 Defender 버전을 함께 적습니다.

## 참고 문헌

- CrowdStrike, "How to Use Microsoft Protection Logging for Forensic Investigations" — https://www.crowdstrike.com/blog/how-to-use-microsoft-protection-logging-for-forensic-investigations/
- jklepsercyber, "defender-detectionhistory-parser" (GitHub README) — https://github.com/jklepsercyber/defender-detectionhistory-parser
- reversingfun, "How to extract quarantine files from Windows Defender" — https://reversingfun.com/posts/how-to-extract-quarantine-files-from-windows-defender/
- Microsoft Learn, "Configure remediation for Microsoft Defender Antivirus detections" — https://learn.microsoft.com/en-us/defender-endpoint/configure-remediation-microsoft-defender-antivirus
