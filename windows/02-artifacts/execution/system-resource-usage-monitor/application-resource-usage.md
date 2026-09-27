---
title: "앱별 자원 사용"
parent: "SRUM"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 990
---

# 앱별 자원 사용 (Application Resource Usage)

SRUM 데이터베이스 `SRUDB.dat` 안의 `{D10CA2FE-6FCF-4F6D-848E-B2E99266FA89}` 표입니다. 앱과 사용자 계정 짝마다 CPU 사용량, 앱이 앞에 떠 있던 시간, 읽고 쓴 바이트 수를 적으며, 행의 시각 (TimeStamp) 은 활동한 때가 아니라 행을 데이터베이스에 적은 때이고 기본 설정에서는 한 시간 간격으로 적습니다.

## 무엇을 기록하나 · 왜 생기나

SRUM (System Resource Usage Monitor) 은 앱·서비스·네트워크가 쓴 자원을 모으는 윈도 기능입니다. SRUM 은 진단 정책 서비스 (Diagnostic Policy Service, DPS) 안에서 돌아가고 실제 수집과 저장은 `srumsvc.dll` 이 맡습니다. 자원 종류마다 확장 (Extension) DLL 이 따로 있으며, 이 표는 앱 자원 사용 제공자 (Application Resource Usage Provider) 인 `appsruprov.dll` 이 채웁니다.

한 행에는 행을 적은 시각, 앱 (AppId) 과 사용자 계정 (UserId), 그동안 쓴 CPU 사이클 (Cycle), 앱이 사용자 앞에 떠 있던 시간 (FaceTime), 컨텍스트 전환 (Context Switch) 횟수, 읽고 쓴 바이트 수와 횟수, 플러시 (Flush) 횟수가 들어 있습니다.

대부분의 값은 앞 (Foreground) 과 뒤 (Background) 두 벌로 나뉩니다. 앞은 앱 창이 사용자 앞에 떠 있던 동안으로 흔히 읽지만, 두 구분의 정확한 기준을 적은 공식 문서는 없습니다.

이 표로 어떤 앱이 어떤 계정으로 돌면서 자원을 썼는지, 그 일이 대략 어느 시간대에 있었는지, 그 시간대에 앱이 얼마나 많이 읽고 썼는지 (양만) 알 수 있습니다. 실행 파일을 지워도 이 표의 행은 지워지지 않고 보관 기간이 지나야 정리됩니다.

SRUM 전체 구조와 다른 표는 [SRUM](index.md) 허브에서, AppId·UserId 를 문자열로 푸는 법은 [구조와 ID 매핑](srudbidmaptable.md)에서 다룹니다. 여기서는 이 표 하나를 읽고 해석하는 일만 다룹니다.

## 위치와 버전별 차이

| 항목 | 값 |
|---|---|
| 파일 | `C:\Windows\System32\sru\SRUDB.dat` |
| 형식 | [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) |
| 표 이름 | `{D10CA2FE-6FCF-4F6D-848E-B2E99266FA89}` |
| 제공자 등록 | SOFTWARE 하이브 `Microsoft\Windows NT\CurrentVersion\SRUM\Extensions` 아래. DLL 은 `%SystemRoot%\System32\appsruprov.dll` |
| 이름 풀이 | AppId·UserId 는 같은 파일의 `SruDbIdMapTable` 에서 풉니다 |

GUID 가 거의 같은 `{D10CA2FE-6FCF-4F6D-848E-B2E99266FA86}` 표도 있는데, 그 표는 푸시 알림 (WPN) 제공자가 채우므로 끝자리 `89` 와 `86` 을 헷갈리지 않습니다.

| Windows | SRUM | 이 표 | 근거 |
|---|---|---|---|
| 7 이하 | 없음 | 없음 | SRUM 은 Windows 8 부터 있습니다 |
| 8 · 8.1 | 있음 | 열 구성은 공개 자료 없음 | 발표 자료의 버전표 |
| 10 · 11 | 있음 | 있음 | 발표 자료의 표 목록. libyal 명세는 Windows 10 으로 시험했습니다 |
| Server 2019 (1809) | 빌드에 따라 다릅니다 | SRUM 이 있으면 있습니다 | 발표자 실험에서 17763.107 에는 있었고 17763.4645 에는 없었습니다 |
| Server 2022 (21H2) | 있음 | 있음 | 발표자 실험 (20348.587) |

### 행이 데이터베이스에 들어가기까지

SRUM 은 값을 먼저 메모리 (Tier1) 에 모으고 기본 60초마다 갱신하며 (Tier1Period), 모은 값은 기본 1시간마다 `SRUDB.dat` (Tier2) 에 옮겨 적습니다 (Tier2Period). 컴퓨터를 끌 때와 DPS 서비스를 멈출 때도 옮겨 적습니다. 초기 버전은 옮기기 전의 값을 레지스트리에 두었고, 데스크톱에서는 Windows 10 1607 뒤로 이 값이 메모리에만 있는 것으로 보입니다.

기록 간격과 레지스트리 임시 저장은 [SRUM 해석 함정](1.md)에서 자세히 다룹니다.

### 보관 기간

보관 기간은 Tier2Period × Tier2MaxEntries 로 계산하며, 기본값은 3,600초 × 1,440 으로 60일입니다. Windows Server 에서는 확장마다 Tier2MaxEntries 를 9,000 으로 둔 경우가 많고, 이때는 375일입니다. SRUM 은 이 값들을 SOFTWARE 하이브의 `Microsoft\Windows NT\CurrentVersion\SRUM` 아래에서 읽으며, 분석 대상의 값이 기본값과 다를 수 있으므로 이 키를 확인합니다.

## 구조

이 표는 ESE 표 하나이고, 페이지·B-트리·카탈로그를 읽는 법은 [파일 구조](../../../01-foundations/database-log-formats/extensible-storage-engine/page-b-tree-catalog.md)에서 다룹니다. 아래 열 목록은 Windows 10 파일 기준입니다. 다른 버전의 파일은 카탈로그에서 열 구성을 먼저 확인합니다.

열은 모두 고정 크기이고, ESE 레코드에서 고정 크기 열 값은 4바이트 머리글 뒤에 열 번호 순서로 붙어 있습니다. "위치" 열은 이 규칙과 열 크기로 계산한 값으로, 레코드 데이터의 첫 바이트(머리글 시작)부터 셉니다. 정수는 모두 부호 있는 리틀 엔디언입니다.

| 번호 | 열 이름 | 형식 | 위치 | 뜻 |
|---|---|---|---|---|
| 1 | AutoIncId | 32비트 정수 | 0x04 | 행 번호 |
| 2 | TimeStamp | 날짜·시각 (8바이트) | 0x08 | 행을 적은 시각 |
| 3 | AppId | 32비트 정수 | 0x10 | `SruDbIdMapTable` 의 IdIndex. 앱을 가리킵니다 |
| 4 | UserId | 32비트 정수 | 0x14 | `SruDbIdMapTable` 의 IdIndex. 계정 SID 를 가리킵니다 |
| 5 | ForegroundCycleTime | 64비트 정수 | 0x18 | 앞에서 쓴 CPU 사이클 |
| 6 | BackgroundCycleTime | 64비트 정수 | 0x20 | 뒤에서 쓴 CPU 사이클 |
| 7 | FaceTime | 64비트 정수 | 0x28 | 앱이 사용자 앞에 떠 있던 시간 |
| 8 | ForegroundContextSwitches | 32비트 정수 | 0x30 | 앞 컨텍스트 전환 횟수 |
| 9 | BackgroundContextSwitches | 32비트 정수 | 0x34 | 뒤 컨텍스트 전환 횟수 |
| 10 | ForegroundBytesRead | 64비트 정수 | 0x38 | 앞에서 읽은 바이트 수 |
| 11 | ForegroundBytesWritten | 64비트 정수 | 0x40 | 앞에서 쓴 바이트 수 |
| 12 | ForegroundNumReadOperations | 32비트 정수 | 0x48 | 앞 읽기 횟수 |
| 13 | ForegroundNumWriteOperations | 32비트 정수 | 0x4C | 앞 쓰기 횟수 |
| 14 | ForegroundNumberOfFlushes | 32비트 정수 | 0x50 | 앞 플러시 횟수 |
| 15 | BackgroundBytesRead | 64비트 정수 | 0x54 | 뒤에서 읽은 바이트 수 |
| 16 | BackgroundBytesWritten | 64비트 정수 | 0x5C | 뒤에서 쓴 바이트 수 |
| 17 | BackgroundNumReadOperations | 32비트 정수 | 0x64 | 뒤 읽기 횟수 |
| 18 | BackgroundNumWriteOperations | 32비트 정수 | 0x68 | 뒤 쓰기 횟수 |
| 19 | BackgroundNumberOfFlushes | 32비트 정수 | 0x6C | 뒤 플러시 횟수 |

공개 명세에는 열 이름과 형식만 있습니다. 5번부터 19번 열의 뜻은 열 이름을 풀이한 것입니다.

### 값 읽는 법

- **한 행은 한 기록 구간의 양으로 읽습니다.** 한 작업에 걸친 여러 행의 값을 더하면 전체 양이 됩니다. 작업이 기록 시점을 넘기면 값이 여러 행에 나뉩니다. 이 해석을 적은 공식 문서는 없습니다.
- **사이클 값은 시간이 아닙니다.** 단위는 명세에 없습니다. 이름대로 CPU 사이클 수라면 같은 값이라도 CPU 속도에 따라 걸린 시간이 다릅니다. 초로 바꾸지 말고 같은 PC 안에서 앱끼리 비교하는 데 씁니다.
- **FaceTime 은 단위가 명세에 없습니다.** 보고서에 시간으로 적으려면 같은 Windows 버전의 시험 PC 에서 단위를 먼저 확인합니다(아래 실습).
- **AppId 문자열은 여러 종류입니다.** 실행 파일 경로, 서비스, 스토어 앱이 섞여 있습니다. 푸는 법은 [구조와 ID 매핑](srudbidmaptable.md)을 봅니다.
- **UserId 는 계정입니다.** `S-1-5-18` (SYSTEM) 같은 시스템 계정 행은 사람 계정의 활동이 아닙니다. SID 읽는 법은 [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md), 계정 이름 찾기는 [사용자 프로필 목록](../../system-account/profilelist.md)을 봅니다.

### 같은 파일의 앱 타임라인 표와 구분하기

`{5C8CF1C7-7257-4F13-B223-970EF5939312}` 표도 앱 단위로 기록합니다. 이 표는 앱 타임라인 제공자 (App Timeline Provider) 인 `eeprov.dll` 이 채웁니다. 이 표에는 끝난 무렵 시각 (EndTime) 과 실행 시간 (DurationMS, 밀리초) 열이 있지만 앱별 자원 사용 표에는 이런 열이 없습니다. 앱 타임라인 표는 Windows 10 · 11 에만 있고 서버에는 없습니다. 그래서 서버에서는 앱별 자원 사용 표가 앱 활동을 보여 주는 주된 SRUM 기록입니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| AppId 가 가리키는 앱이 이 PC 에서 돌면서 자원을 썼습니다 | 앱을 누가 시작했는지. 사용자가 직접 켰는지 |
| 그 활동이 UserId 가 가리키는 계정에 묶여 있습니다 | 그 계정의 주인이 그때 PC 앞에 있었는지 |
| 행을 적은 시각 앞의 기록 구간에 활동이 있었습니다 | 앱이 시작하거나 끝난 정확한 시각 |
| 그 구간에 앱이 읽고 쓴 바이트 양 | 어떤 파일을 읽고 썼는지. 쓴 양이 어떤 파일의 크기와 같다는 것 |
| FaceTime 이 0 이 아니면 앱이 앞에 떠 있던 때가 있었다고 볼 수 있습니다 (열 이름 기준) | 사용자가 그 창을 보거나 조작했는지 |
| | 행이 없으니 실행도 없었다는 것 |

행이 없어도 실행이 없었다고 할 수 없는 이유는 아래 함정과 한계 절에 모았습니다.

### 보고서 문장

아래 경로·SID·값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "`SRUDB.dat` 의 앱별 자원 사용 표에 `C:\Users\Public\tool.exe` 를 가리키는 행이 3개 있습니다. 세 행의 사용자는 SID `S-1-5-21-…-1001` 입니다. 행을 적은 시각은 2025-03-14 02:11 부터 04:11 (UTC) 사이입니다. 세 행의 ForegroundBytesWritten 을 더하면 12,582,912 바이트입니다."
- 쓰면 안 되는 문장: "사용자가 02:11 에 tool.exe 를 실행해 12 MB 짜리 파일을 만들었습니다."

## 시각 해석

### 형식

TimeStamp 열은 ESE 의 날짜·시각 열 (JET_coltypDateTime) 입니다. 이 형식은 날 수를 담은 8바이트 실수이고, 변형 날짜 (Variant Date) 와 같습니다. 흔히 OLE 자동화 날짜 (OLE Automation Date) 라고 부릅니다. 0 은 1899-12-30 자정입니다. 정수 부분이 날이고 소수 부분이 하루 안의 시각입니다. 계산법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다.

libesedb 명세는 이 열 형식을 FILETIME 으로 적고 실수라는 설명과 맞춰 봐야 한다는 메모를 남겼지만, SRUM 명세와 Microsoft 문서는 실수로 적으므로 직접 파서를 짤 때는 실수로 읽습니다.

### 시간대

값에는 시간대 정보가 없고 명세에도 시간대가 없습니다. srum-dump 는 이 값을 UTC 로 풀어 보여 줍니다. 실제 데이터에서는 알려진 사건과 한 번 맞춰 보고, 컴퓨터를 끌 때도 행을 적으므로 종료 시각 무렵에 행이 몰려 있는지 봅니다([켜짐·꺼짐](../../event-logs/power-on-off-events.md)). 현지 시각으로 바꾸는 법은 [시간대 설정](../../system-account/time-zone.md)과 [시간대·시계 오차 보정](../../../03-techniques/analysis/timeline/time-normalization.md)을 봅니다.

### 행을 적은 때와 활동한 때

TimeStamp 는 메모리의 값을 `SRUDB.dat` 에 옮겨 적은 때이고, 활동은 그 앞의 기록 구간에 있었습니다. 구간은 Tier2Period 로 정해지며 기본값은 1시간입니다. 끄기나 DPS 중지로 적은 행은 구간이 1시간보다 짧을 수 있습니다. Windows 10 21H2 에서는 TimeStamp 와 실제 활동 시각 사이에 한 시간쯤 차이가 납니다. 그래서 보고서에는 한 시각이 아니라 "이 시각 이전의 기록 구간" 처럼 폭으로 적습니다.

### 순서로 시계 변경 찾기

AutoIncId 는 이름대로라면 행을 넣을 때마다 커지는 번호이므로 AutoIncId 가 커질수록 TimeStamp 도 같거나 커야 하고, 순서가 뒤집힌 곳은 시계 변경을 의심할 단서입니다. 이 규칙은 명세에 적힌 것이 아니라 열 이름에서 나온 기대입니다. 확인은 [시간 변경 (4616·Kernel-General)](../../event-logs/4616-kernel-general.md)과 맞춰서 합니다.

## 함정과 한계

1. **TimeStamp 를 실행 시각으로 씁니다.** TimeStamp 는 행을 적은 때입니다. 실행 시각은 [프리페치](../prefetch/index.md)나 [프로세스 생성 (4688)](../../event-logs/4688.md)에서 찾습니다.
2. **행이 없으면 실행도 없었다고 봅니다.** 행이 빠지는 경우는 여럿입니다.
   - 짧게 돈 프로그램이 남지 않을 수 있습니다. Windows 10 21H2 에서 지우기 스크립트를 돌린 시험에서는 `python.exe` 의 행 없이 `cmd.exe` 의 행만 남았습니다.
   - 같은 파일의 앱 타임라인 표는 60초 갱신 때 실행 중이어야 남습니다. 이 표에도 같은 규칙이 맞는지는 공개 자료가 없습니다.
   - 보관 기간(기본 60일)이 지난 행은 정리됩니다.
   - 전원을 갑자기 끊으면 마지막으로 옮겨 적은 뒤의 값은 파일에 없을 수 있습니다. 라이브 수집에서도 아직 메모리에만 있는 값은 파일에 없습니다.
3. **바이트 수를 파일 크기로 읽습니다.** Windows 10 21H2 에서 약 228 MB 파일을 C: 에서 USB 로 복사한 시험에서는 `explorer.exe` 행의 읽은 양이 파일 크기의 절반쯤이었고, 쓴 양은 약 4.2 MB 였습니다. 같은 시험에서 완전삭제 도구로 약 8.97 GB 빈 공간을 지웠을 때 쓴 양은 약 72.9 MB 로 적혔습니다. 바이트 수는 활동이 있었다는 단서로만 씁니다.
4. **사이클과 FaceTime 을 시간으로 바꿉니다.** 두 값 모두 명세에 단위가 없습니다. 시간으로 적으려면 시험으로 단위를 먼저 확인합니다.
5. **`...FA89` 와 `...FA86` 을 헷갈립니다.** 끝자리 하나만 다른 푸시 알림 표입니다.
6. **날짜 열을 FILETIME 으로 읽습니다.** 8바이트 실수를 정수로 읽으면 엉뚱한 날짜가 나옵니다.
7. **손상된 파일을 한 가지 방법으로만 읽습니다.** 압수 이미지에서 꺼낸 `SRUDB.dat` 는 대부분 비정상 종료 (Dirty Shutdown) 상태입니다. 손상 파일 한 건의 이 표를 도구마다 다르게 읽어 1,612 행과 1,742 행이 나온 사례가 있습니다. B-트리를 끝까지 따라가지 못한 쪽이 적게 냈습니다. 두 가지 이상 방법으로 열어 행 수를 비교합니다. 비정상 종료 상태는 [트랜잭션 로그와 비정상 종료 상태](../../../01-foundations/database-log-formats/extensible-storage-engine/edb-log-dirty-shutdown.md)에서 다룹니다.
8. **시스템 계정 행을 사람의 활동으로 씁니다.** UserId 가 시스템 계정이면 서비스 활동일 수 있습니다.

### 지우기와 조작

- **`SRUDB.dat` 를 통째로 지웁니다.** DPS 가 돌아가는 동안에는 서비스가 이 파일을 씁니다. 그래서 지우려면 보통 서비스를 먼저 멈춥니다. 지운 흔적은 [$MFT](../../filesystem/mft.md)와 [$UsnJrnl](../../filesystem/usnjrnl.md)에 남을 수 있습니다. 옛 파일은 [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)에서 찾습니다.
- **DPS 를 멈추거나 끕니다.** 멈추는 순간 메모리의 값이 파일에 적힙니다. 그래서 정시가 아닌 시각에 행이 몰려 있으면 서비스 중지나 종료를 의심해 봅니다. 서비스를 꺼 두면 그 뒤로는 기록이 쌓이지 않을 것으로 보이지만, 이 동작을 시험한 공개 자료는 없습니다. 서비스 설정은 [서비스·드라이버](../../persistence/services-drivers.md)에서 확인합니다.
- **행을 지우거나 고칩니다.** ESE 는 지운 레코드가 페이지에 남을 수 있습니다([파일 안에 남은 지운 레코드](../../../01-foundations/database-log-formats/extensible-storage-engine/deleted-records.md)). 고친 값은 파일 하나만 봐서는 판별하기 어렵습니다. 섀도 복사본의 옛 `SRUDB.dat` 와 비교합니다.
- **시스템 시각을 바꿉니다.** TimeStamp 도 바뀐 시계를 따를 것입니다. 위의 순서 검사를 합니다([시스템 시각을 바꿨나](../../../04-scenarios/activity/anti-forensics/system-time-change.md)).
- **완전삭제 도구를 씁니다.** 위 3번처럼 쓴 양은 지운 양과 맞지 않을 수 있습니다. 도구의 행이 있다는 사실을 단서로 씁니다([완전삭제 도구를 썼나](../../../04-scenarios/activity/anti-forensics/wiping-tools.md)).

## 직접 분석해 보기

### 헥스로 한 번

먼저 사본을 만듭니다. 원본을 도구로 열면 파일이 바뀔 수 있습니다. 카탈로그에서 표 이름으로 이 표의 페이지를 찾습니다. 그다음 잎 페이지에서 레코드 하나를 꺼냅니다. 페이지 안에서 레코드를 찾는 법은 [파일 구조](../../../01-foundations/database-log-formats/extensible-storage-engine/page-b-tree-catalog.md)에서 다룹니다.

아래는 명세를 보고 만든 예시입니다. 실제 데이터에서 뽑은 값이 아닙니다. 레코드 데이터의 앞 48바이트만 보입니다. `..` 은 설명과 관계없어 줄인 바이트입니다.

```
위치    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    13 .. .. .. 22 C8 00 00 E9 93 3E E9 42 54 E6 40
0x10    38 01 00 00 07 00 00 00 34 1C DC DF 02 00 00 00
0x20    B1 68 DE 3A 00 00 00 00 59 DA 44 00 00 00 00 00
```

1. 0x00 의 `13` 은 머리글의 첫 바이트입니다. 이 바이트는 레코드에 든 마지막 고정 크기 열 번호입니다. 값이 19 이므로 19개 열이 모두 들어 있습니다. 값이 19 보다 작으면 그 뒤 열은 레코드에 없습니다.
2. 0x04 의 `22 C8 00 00` 은 AutoIncId 51,234 입니다.
3. 0x08 부터 8바이트가 TimeStamp 입니다. 리틀 엔디언 8바이트 실수 (IEEE 754) 로 풀면 45730.0909722… 입니다.
4. 정수 부분 45,730 을 1899-12-30 에 더하면 2025-03-14 입니다.
5. 소수 부분에 24 를 곱하면 2.18333 시간, 곧 02:11:00 입니다. 실수 오차가 있으므로 초 단위로 반올림합니다.
6. 이 시각은 행을 적은 때입니다. 활동은 그 앞의 기록 구간에 있었습니다.
7. 0x10 의 `38 01 00 00` 은 AppId 312 입니다. `SruDbIdMapTable` 에서 IdIndex 가 312 인 행을 찾아 앱 이름을 얻습니다.
8. 0x14 의 `07 00 00 00` 은 UserId 7 입니다. IdIndex 7 인 행의 IdType 이 3 이면 IdBlob 에 SID 가 들어 있습니다.
9. 0x18 은 ForegroundCycleTime 0x2DFDC1C34 (12,345,678,900) 입니다. 0x20 은 BackgroundCycleTime 0x3ADE68B1 (987,654,321) 입니다.
10. 0x28 은 FaceTime 0x44DA59 (4,512,345) 입니다. 단위를 모르므로 원값 그대로 적습니다.
11. 나머지 열은 위 열 표의 위치에서 같은 방법으로 읽습니다.

> 그림 자리: 레코드 데이터의 머리글(0x00~0x03)과 열 19개의 위치를 색으로 나누고, TimeStamp 8바이트가 날짜로 바뀌는 과정을 옆에 적은 그림

### 공개 도구로 한 번

libesedb 의 `esedbexport`, ESEDatabaseView, SrumECmd, srum-dump 같은 공개 도구가 이 표를 보여 줍니다. 도구를 쓸 때는 다음을 확인합니다.

- AppId·UserId 를 문자열로 풀어 보여 주는지, 번호만 보여 주는지 확인합니다.
- TimeStamp 를 UTC 로 보여 주는지, 분석 PC 의 현지 시각으로 바꿔 보여 주는지 확인합니다.
- 비정상 종료 상태의 파일을 어떻게 여는지 확인합니다. JET API 로 여는 도구는 같은 폴더의 트랜잭션 로그로 먼저 복구해야 합니다. 이미지 안의 로그가 끊겨 있으면 복구가 안 될 수 있습니다. 페이지를 직접 해석하는 도구는 로그 없이 읽습니다.
- 두 방법으로 연 결과의 행 수를 비교합니다. 일부 공개 도구는 이 파일을 읽다가 파싱 오류를 냅니다.
- 행 한두 개는 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

B-트리가 망가져 도구가 행을 못 찾으면 레코드 단위로 긁어 볼 수 있습니다. 위 열 표의 위치와 TimeStamp 가 그럴듯한 날짜인지가 판별 기준이 됩니다([레코드 카빙](../../../03-techniques/analysis/data-recovery/record-carving.md)).

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| 같은 파일의 [구조와 ID 매핑](srudbidmaptable.md) | AppId·UserId 가 가리키는 앱 이름과 SID |
| 같은 파일의 [네트워크 사용량](network-data-usage.md) | 같은 앱·같은 시간대에 보내고 받은 바이트 |
| 같은 파일의 앱 타임라인 표 | 실행이 끝난 무렵 시각과 실행 시간 (Windows 10 · 11) |
| [프리페치](../prefetch/index.md) | 같은 실행 파일의 최근 실행 시각이 이 표의 기록 구간 안에 드는지 |
| [AmCache](../amcache-hve/index.md) | 같은 경로의 실행 파일 정보와 해시 |
| [BAM·DAM](../background-activity-moderator.md) | 사용자별 마지막 실행 시각. UserId 의 SID 와 맞는지 |
| [프로세스 생성 (4688)](../../event-logs/4688.md) · [Sysmon 이벤트 1](../../event-logs/sysmon/1.md) | 초 단위 시작 시각과 실행 계정 |
| [$MFT](../../filesystem/mft.md) · [$UsnJrnl](../../filesystem/usnjrnl.md) | 그 시간대에 만들어지거나 바뀐 파일. 쓴 바이트 수가 크게 나온 구간에 무슨 파일이 생겼는지 |
| [켜짐·꺼짐](../../event-logs/power-on-off-events.md) | 정시가 아닌 시각의 행이 종료 시각과 맞는지 |

여러 실행 기록을 합쳐 읽는 순서는 [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md)에서 다룹니다. 자료를 모으고 압축한 흔적을 찾을 때는 [퇴사 전 자료를 모으고 압축했나](../../../04-scenarios/exfiltration/data-exfiltration/staging.md)를 봅니다.

## 실습

**직접 만든 Windows 10 · 11 가상 머신**에서 해 봅니다. 시험 전에 SOFTWARE 하이브의 `Microsoft\Windows NT\CurrentVersion\SRUM` 값을 적어 둡니다.

1. 메모장을 앞에 띄워 두고 정확히 10분 동안 둡니다. 시작과 끝 시각을 적습니다.
2. 크기를 아는 파일(예: 100 MB)을 탐색기로 다른 드라이브에 한 번 복사합니다.
3. 명령 창에서 몇 초 만에 끝나는 프로그램을 하나 실행합니다.
4. 컴퓨터를 정상 종료하고 이미지에서 `SRUDB.dat` 를 꺼냅니다.

풀어 볼 질문입니다.

1. 메모장 행의 FaceTime 원값은 얼마입니까? 10분과 비교하면 단위가 무엇으로 보입니까?
2. `explorer.exe` 행들의 읽은·쓴 바이트 합은 파일 크기와 같습니까? 다르다면 얼마나 다릅니까?
3. 몇 초 만에 끝난 프로그램의 행이 있습니까?
4. 행의 TimeStamp 와 적어 둔 시각은 얼마나 차이 납니까? 종료 시각 무렵에 적힌 행이 있습니까?
5. 도구 두 가지로 이 표를 열어 행 수가 같은지 봅니다.

**공개 데이터 세트**에서도 해 봅니다. NIST CFReDS 등에서 Windows 10 이상 이미지를 하나 고릅니다.

1. `SRUDB.dat` 는 정상 종료 상태입니까?
2. TimeStamp 가 가장 이른 행과 가장 늦은 행 사이는 며칠입니까? 보관 기간 설정과 맞습니까?
3. 사람 계정 SID 의 행 가운데 한 앱을 골라, 프리페치의 실행 시각이 이 표의 기록 구간 안에 드는지 확인해 보십시오.

## 참고 문헌

- libyal, "System Resource Usage Monitor (SRUM) database" (esedb-kb) — https://github.com/libyal/esedb-kb/blob/main/documentation/System%20Resource%20Usage%20Monitor%20(SRUM).asciidoc
- libyal, "Extensible Storage Engine (ESE) Database File (EDB) format" (libesedb) — https://github.com/libyal/libesedb/blob/main/documentation/Extensible%20Storage%20Engine%20(ESE)%20Database%20File%20(EDB)%20format.asciidoc
- Microsoft Learn, "JET_COLTYP" — https://learn.microsoft.com/en-us/windows/win32/extensible-storage-engine/jet-coltyp
- Catarina de Faria Cristas · Lucas Echard · Diego Fuschini, "Exploring the depths of SRUM for incident response", SANS DFIR Summit Europe 2023 — https://github.com/ReversecLabs/slide-decks/blob/main/2023-SANS_DFIR_Summit_Europe/Exploring_the_depths_of_SRUM_for_incident_response.pdf
- Ilya Kobzar, "Behavioral analysis of user file operations with SRUM" (2025) — https://www.ilyakobzar.com/p/behavioral-analysis-of-user-file
- Mark Baggett, srum-dump "configuration_file.md" — https://github.com/MarkBaggett/srum-dump/blob/master/configuration_file.md
