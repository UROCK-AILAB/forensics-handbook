# BITS 전송 작업 (BITS Jobs·qmgr.db)

## 한 줄 요약

BITS (Background Intelligent Transfer Service) 작업은 파일을 받거나 올리는 예약 전송입니다. 작업에 알림 명령을 걸어 두면 전송이 끝나거나 오류가 날 때 BITS 가 그 명령을 실행합니다. 이 설정은 레지스트리가 아니라 BITS 데이터베이스에 남고, Windows 10 이후에는 그 파일이 ESE 형식의 `qmgr.db` 입니다.

## 무엇을 기록하나 · 왜 생기나

BITS 작업은 파일을 받거나 올리는 예약 전송이고, 전송은 서비스 호스트 프로세스가 합니다. 작업에는 알림 명령 (notify command) 을 걸 수 있으며 SetNotifyCmdLine 으로 설정합니다. 전송이 끝나거나 오류가 나면 BITS 가 그 명령을 실행하는데, 공격자가 이 알림 명령으로 지속성을 만든 사례가 있습니다. 명령은 레지스트리가 아니라 BITS 데이터베이스에 들어가기 때문에 레지스트리만 보는 자동실행 점검에서는 빠집니다.

- 정상 업데이트도 BITS 작업을 계속 만듭니다. Windows 11 PC 한 대에서는 모든 사용자를 합쳐 작업이 3개 있었습니다(Suspended 1, Transferred 2). (확인 범위: Win11 25H2 한 대)

### 사례에 남은 모습

Mandiant 는 Ryuk 관련 KEGTAP 사례를 이렇게 적습니다.

| 항목 | 값 |
|---|---|
| 작업 이름 | "System update" |
| 원본 URL | `http://127.0.0.1/tst/56/` |
| 받은 크기 | 0 |

- 이 작업은 없는 파일을 받게 되어 있어서 오류 상태가 되었고, 그 오류 때 알림 명령이 백도어를 띄웠습니다.
- 그래서 원본 URL 이 자기 PC 주소를 가리키고 받은 크기가 0 인 작업에 알림 명령이 걸려 있으면 먼저 봅니다. 이 문장은 사례에서 끌어낸 해석입니다.

## 위치와 버전별 차이

폴더는 `%ALLUSERSPROFILE%\Microsoft\Network\Downloader` 입니다.

| Windows | 파일 | 형식 |
|---|---|---|
| Windows 10 이전 | `qmgr0.dat`, `qmgr1.dat` | 자체 바이너리 형식. 백업·동기화용 두 파일 |
| Windows 10 이후 | `qmgr.db` | ESE 데이터베이스. 트랜잭션 로그 `edb.log`(최신)와 번호 붙은 이전 로그 세 개가 같이 있습니다 |

Windows 11 PC 한 대의 폴더 내용은 이랬습니다. (확인 범위: Win11 25H2 한 대)

| 파일 | 크기(바이트) |
|---|---|
| qmgr.db | 1,310,720 |
| qmgr.jfm | 16,384 |
| edb.chk | 8,192 |
| edb.log, 번호 붙은 로그 셋(edb0001F.log·edb00020.log·edb00021.log), edbtmp.log | 각 1,310,720 |
| edbres00001.jrs, edbres00002.jrs | 각 1,310,720 |

- 같은 PC 의 `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\BITS` 에는 `JobInactivityTimeout`=7,776,000 과 `JobNoProgressTimeout`=1,209,600 값이 있었습니다. 초로 읽으면 90일과 14일입니다. 두 값의 뜻은 확인하지 못했습니다. (확인 범위: Win11 25H2 한 대)
- 완료된 작업이 DB 에 얼마나 남는지는 확인하지 못했습니다.
- 이벤트 로그 채널은 `Microsoft-Windows-Bits-Client/Operational` 입니다. 파일은 `%SystemRoot%\System32\Winevt\Logs\Microsoft-Windows-Bits-Client%4Operational.evtx` 였습니다. (파일 경로 확인 범위: Win11 25H2 한 대)

## 구조

ESE 데이터베이스 자체의 구조는 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다. 여기서는 Windows 10 이후 `qmgr.db` 의 표 두 개만 봅니다.

### 표

| 표 | 열 |
|---|---|
| Jobs | Id(GUID), Blob(바이너리) |
| Files | Id(GUID), Blob(바이너리) |

### Jobs 표의 Blob

| 순서 | 필드 | 크기 |
|---|---|---|
| 1 | Type | 4바이트 |
| 2 | Priority | 4바이트 |
| 3 | State | 4바이트 |
| 4 | Job ID | GUID 16바이트 |
| 5 | Name | UTF-16, 길이 가변 |
| 6 | Description | UTF-16 |
| 7 | Command (알림 명령) | UTF-16 |
| 8 | Arguments | UTF-16 |
| 9 | User SID | UTF-16 문자열 |
| 10 | Flags | 4바이트 |
| 11 | 파일 목록 | XFER GUID `{7756DA36-516F-435A-ACAC-44A248FFF34D}` 로 구분 |

### Files 표의 Blob

| 순서 | 필드 | 크기 |
|---|---|---|
| 1 | 목적지 파일 이름 | UTF-16 |
| 2 | 원본 파일 이름 또는 URL | UTF-16 |
| 3 | 임시 파일 이름 | UTF-16 |
| 4 | 다운로드 크기 | 8바이트 |
| 5 | 전송 크기 | 8바이트 |
| 6 | 드라이브 | UTF-16 |
| 7 | 볼륨 GUID | UTF-16 |

- Mandiant 의 필드 목록에는 시각 필드가 없습니다. 작업을 만든 시각·바꾼 시각·완료 시각이 Blob 어디에 있는지는 확인하지 못했습니다.
- UTF-16 가변 필드의 길이를 어떻게 적는지는 이 목록에 없습니다. 필드를 손으로 끝까지 따라가려면 파서의 코드를 함께 봅니다.

### 지운 작업을 찾는 GUID

지워진 항목도 식별 GUID 로 찾아 카빙할 수 있습니다. 트랜잭션 로그 파일에서도 기록을 되살릴 수 있습니다.

| 용도 | GUID |
|---|---|
| 파일 식별 | `{519ECFE4-D946-4397-B73E-268513051AB2}` |
| 작업 식별 | `{E10956A1-AF43-42C9-92E6-6F9856EBA7F6}` |
| 작업 식별 | `{4CD4959F-7064-4BF2-84D7-476A7E62699F}` |
| 작업 식별 | `{A92619F1-0332-4CBF-9427-898818958831}` |
| 작업 식별 | `{DDBC33C1-5AFB-4DAF-B8A1-2268B39D01AD}` |
| 작업 식별 | `{8F5657D0-012C-4E3E-AD2C-F4A5D7656FAF}` |
| 작업 식별 | `{94416750-0357-461D-A4CC-5DD9990706E4}` |

- GUID 를 바이트로 적는 규칙은 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에서 다룹니다. `qmgr.db` 안에서 이 GUID 가 어떤 바이트 순서로 들어 있는지는 이번 자료로 확인하지 못했습니다.
- ESE 파일 안에 지운 행이 어떻게 남는지는 [파일 안에 남은 지운 레코드](../../01-foundations/database-log-formats/extensible-storage-engine/deleted-records.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

- DB 에 작업이 있으면, 그 작업의 이름·알림 명령·인자·소유자 SID 가 수집 시점에 저장되어 있었습니다.
- Files 표로 어느 URL 에서 어느 경로로 받도록 했는지, 얼마나 받았는지 알 수 있습니다.
- 지운 작업도 식별 GUID 나 트랜잭션 로그로 되살릴 수 있습니다.
- 이벤트 3 의 processPath 로 어느 프로그램이 작업을 만들었는지 볼 수 있습니다. 이 문장은 이벤트의 칸 구성에서 끌어낸 해석이며, 실제 악성 사례로는 확인하지 못했습니다.

### 증명하지 못하는 것

- **알림 명령이 실행됐나.** DB 에 명령이 있다는 것은 설정만 알려 줍니다. 이벤트 64 는 실행에 **실패했을 때** 남습니다. 실행은 [프로세스 생성](../event-logs/4688.md) 이나 [Sysmon 이벤트 1](../event-logs/sysmon/1.md) 로 따로 봅니다.
- **언제 만들었나.** Blob 의 시각 필드를 확인하지 못했습니다. 아래 "시각 해석" 을 봅니다.
- **받은 파일이 지금도 있나.** 목적지 경로의 파일을 따로 확인합니다.

보고서에는 "`qmgr.db` 에 이 이름의 작업이 있고, 알림 명령으로 이 경로가 설정되어 있다" 처럼 씁니다.

## 시각 해석

- 켜진 PC 의 API(`Get-BitsTransfer`)는 CreationTime·ModificationTime·TransferCompletionTime 속성을 보여 줍니다. 같은 API 는 NotifyCmdLine·OwnerAccount·FileList·JobState 도 보여 줍니다. (확인 범위: Win11 25H2 한 대)
- 오프라인 DB 에서는 시각을 이벤트 로그와 파일 시스템 시각으로 보탭니다.
- `Microsoft-Windows-Bits-Client/Operational` 의 주요 이벤트는 아래와 같습니다. 메시지와 칸은 Windows 11 PC 한 대의 공급자 메시지에서 읽었습니다. (확인 범위: Win11 25H2 한 대)

| 이벤트 | 뜻 | 칸 |
|---|---|---|
| 3 | 새 작업을 만들었습니다 | jobTitle, jobId, jobOwner, processPath, processId, ClientProcessStartKey |
| 4 | 전송 작업을 마쳤습니다 | User, jobTitle, jobId, jobOwner, fileCount, bytesTransferred, bytesTransferredFromPeer |
| 5 | 작업을 취소했습니다 | |
| 59 | 이 URL 의 전송을 시작했습니다 | transferId, name, Id, url, peer, fileTime, fileLength, bytesTotal, bytesTransferred, bytesTransferredFromPeer |
| 60 | 이 URL 의 전송을 멈췄습니다. 상태 코드가 함께 남습니다 | 59 의 칸에 hr(상태 코드), proxy 등이 더 있습니다 |
| 61 | 60 과 메시지 문구가 같습니다 | |
| 64 | 전송 뒤 실행하도록 설정된 프로그램을 띄우지 못했습니다. BITS 는 성공할 때까지 주기적으로 다시 시도합니다 | |

- 이벤트 3 은 버전마다 칸이 다릅니다. 버전 0 에는 작업 이름과 소유자만 있고, 버전 2 부터 Process Path·Process ID 가 있습니다. Windows 11 PC 한 대의 템플릿은 버전 3 이었습니다. (확인 범위: Win11 25H2 한 대)
- Mandiant 는 이벤트 3(작업 생성), 61(전송 중지 경고), 64(알림 명령 경고) 를 짚습니다. 64 에는 작업 이름·대상 실행 파일·URL 이 보입니다.
- 이벤트 로그 형식은 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에서 다룹니다.

## 함정과 한계

- **로그가 금방 밀려납니다.** Windows 11 PC 한 대에서 이 로그는 최대 약 1MB, 순환 방식이었습니다. 1,451건이 약 17일 치(2026-09-06~09-23 UTC)였습니다. (확인 범위: Win11 25H2 한 대)
- 같은 PC 에서 많은 이벤트는 59(236건), 3(226), 60(226), 16403(226), 4(225), 306(191), 310(103), 61(10) 순이었습니다. 정상 업데이트 작업이 3·59·60·4 를 계속 남기므로 오래된 악성 작업의 기록은 쉽게 밀려납니다.
- **켜진 PC 에서는 파일이 잠겨 있습니다.** Windows 11 PC 한 대에서 BITS 서비스가 `qmgr.db` 를 잠가 다시 읽지 못했습니다. `esentutl /mh` 도 JET_errFileAccessDenied(-1032) 로 실패했습니다. (확인 범위: Win11 25H2 한 대)
- BitsParser 단독판도 잠긴 파일은 읽지 못합니다. 서비스를 멈추거나 잠긴 파일을 복사하는 도구를 따로 씁니다. 수집 방법은 [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) 에서 다룹니다.
- **압수 이미지의 `qmgr.db` 는 비정상 종료 상태일 수 있습니다.** 손상된 ESE DB 는 읽는 방식마다 행 수가 다를 수 있습니다. 로그를 함께 수집하고 [트랜잭션 로그와 비정상 종료 상태](../../01-foundations/database-log-formats/extensible-storage-engine/edb-log-dirty-shutdown.md) 를 봅니다.
- **이벤트 64 는 실패의 기록입니다.** 알림 명령이 성공적으로 실행되었을 때 어떤 이벤트가 남는지는 확인하지 못했습니다.
- **이벤트 61 과 60 은 메시지 문구가 같습니다.** 이벤트 ID 로 구별합니다.
- **Windows 10 이전 검체는 형식이 다릅니다.** `qmgr0.dat`·`qmgr1.dat` 를 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 형식에 맞춰 만든 예시입니다. 특정 검체에서 꺼낸 값이 아닙니다.

**`qmgr.db` 앞 12바이트.**

```
?? ?? ?? ?? EF CD AB 89 20 06 00 00
```

1. 오프셋 4 의 `EF CD AB 89` 를 리틀 엔디언으로 읽으면 0x89ABCDEF 입니다. ESE 파일의 서명입니다.
2. Windows 11 PC 한 대의 `qmgr.db` 에서도 오프셋 4 에 이 4바이트가 있었고, 오프셋 8 의 값은 0x620 이었습니다. `20 06 00 00` 은 그 값을 리틀 엔디언으로 적은 모양입니다. (확인 범위: Win11 25H2 한 대)
3. 오프셋 0 의 4바이트와 오프셋 8 값의 뜻은 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다.

**Files Blob 에서 URL 을 찾을 때의 바이트 (`http://`).**

```
68 00 74 00 74 00 70 00 3A 00 2F 00 2F 00         h.t.t.p.:././.
```

1. Files Blob 의 원본 URL 은 UTF-16 입니다.
2. 그래서 한 글자가 2바이트이고, ASCII 글자 뒤에 `00` 이 붙습니다.
3. DB 파일과 트랜잭션 로그에서 이 모양을 찾으면 URL 후보가 나옵니다. 후보가 어느 작업에 속하는지는 파서 결과와 맞춰 봅니다.

### 공개 도구로 한 번

1. 이미지에서 `Downloader` 폴더의 파일을 모두 사본으로 뜹니다. `qmgr.db` 와 함께 로그·체크포인트 파일도 뜹니다.
2. 공개 도구 BitsParser(https://github.com/fireeye/BitsParser) 로 사본을 읽습니다. Mandiant 는 이 도구가 모든 버전의 BITS DB 를 읽고, 지운 작업과 파일 정보도 복구한다고 설명합니다. 수정한 Impacket ESE 파서를 쓰는 Python 도구입니다.
3. 작업마다 이름, 알림 명령(Command·Arguments), 소유자 SID, 파일 목록의 URL 과 목적지를 한 줄로 적습니다.
4. 알림 명령이 있는 작업을 먼저 봅니다. URL 이 자기 PC 주소이거나 받은 크기가 0 인 작업도 따로 표시합니다.
5. 켜진 PC 에서는 관리자 권한 PowerShell 의 `Get-BitsTransfer -AllUsers` 로 모든 사용자의 작업을 읽을 수 있습니다.
6. Bits-Client/Operational 로그에서 같은 작업 이름의 이벤트 3·4·59·60·61·64 를 뽑아 시각을 붙입니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 4688·Sysmon 1 | bitsadmin.exe·powershell.exe 가 작업을 만든 흔적, 알림 명령으로 뜬 프로세스 | [프로세스 생성](../event-logs/4688.md), [Sysmon 이벤트 1](../event-logs/sysmon/1.md) |
| 프리페치 | BITSADMIN.EXE 나 알림 명령 프로그램의 실행 흔적 | [프리페치](../execution/prefetch/index.md) |
| SRUM | 그 무렵 앱별 네트워크 사용량 | [SRUM](../execution/system-resource-usage-monitor/index.md) |
| 마스터 파일 테이블 | 목적지 파일이 만들어진 시각 | [마스터 파일 테이블](../filesystem/mft.md) |
| 다른 자동실행 위치 | 같은 명령이 다른 자리에도 있나 | [로그온 자동실행](run-runonce-startup-folder.md), [예약 작업](scheduled-tasks/index.md) |

자동실행 위치 전체를 훑는 흐름은 [악성코드 지속성(자동실행) 찾기](../../04-scenarios/incident/persistence.md) 에 있습니다.

## 실습

공개 검체(NIST CFReDS 등)에서 `Downloader` 폴더와 이벤트 로그를 꺼내 아래 질문을 풀어 봅니다.

1. 검체의 Windows 버전으로 보아 어느 파일을 찾아야 합니까? 그 파일이 있습니까?
2. `qmgr.db` 의 오프셋 4 에 ESE 서명이 있습니까? 헤더로 보아 비정상 종료 상태입니까?
3. 파서로 읽은 작업 가운데 알림 명령이 있는 작업이 있습니까? 명령은 무엇을 가리킵니까?
4. 지운 작업을 복구한 결과와 살아 있는 작업 목록이 어떻게 다릅니까?
5. Bits-Client/Operational 로그는 며칠 치를 담고 있습니까? 이벤트 3 의 processPath 에는 어떤 프로그램들이 나옵니까?

## 참고 문헌

1. Mandiant(David Via, Scott Runnels), *Attacker Use of Windows Background Intelligent Transfer Service*, Google Cloud Blog, 2021-03-31. 알림 명령과 지속성, KEGTAP 사례, 버전별 파일, `qmgr.db` 의 표와 Blob 필드, 지운 작업 식별 GUID, 이벤트 3·61·64, BitsParser. https://cloud.google.com/blog/topics/threat-intelligence/attacker-use-of-windows-background-intelligent-transfer-service/
