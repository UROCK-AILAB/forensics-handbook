---
title: "장치 설치 로그"
parent: "USB 저장장치 흔적"
grand_parent: "아티팩트 · 외부 장치"
nav_order: 1530
---

# 장치 설치 로그 (setupapi.dev.log)

## 한 줄 요약

`setupapi.dev.log` 는 플러그 앤 플레이 (Plug and Play, PnP) 관리자와 SetupAPI 가 장치와 드라이버를 설치할 때 남기는 텍스트 로그이며, USB 저장장치가 이 PC 에 설치된 시각을 밀리초까지 보여 줍니다. 시각은 시간대 표시가 없는 현지 시각이라서 UTC 로 바꿔서 씁니다.

## 무엇을 기록하나 · 왜 생기나

Windows 는 장치 설치 문제를 풀 때 쓰라고 이 로그를 남깁니다. Vista 부터 로그가 둘로 나뉘어, 장치·드라이버 설치는 장치 설치 로그 (`setupapi.dev.log`) 에, 그 밖의 설치 작업은 앱 설치 로그 (`setupapi.app.log`) 에 적습니다. 설치 작업 하나는 로그에서 섹션 (Section) 하나가 됩니다.

새 장치를 꽂으면 PnP 관리자가 드라이버를 골라 장치를 설치하고, 이때 `Device Install (Hardware initiated)` 섹션이 생깁니다(Windows 10 1507, Windows 11 25H2 기준). 설치 섹션의 첫 본문 줄은 "장치가 아직 구성되지 않아 설치가 필요하다" 는 줄입니다(`ump: Install needed due to device having problem code CM_PROB_NOT_CONFIGURED`). 설치 섹션은 꽂을 때마다 생기지 않고 설치가 필요할 때 생깁니다. 그래서 이 로그는 장치를 처음 연결한 시각의 근거로 씁니다.

USB 저장장치만 들어가는 것이 아니라 네트워크 어댑터, 휴대폰, 프린터, 입력 장치의 설치도 같은 로그에 들어갑니다. 장치를 지울 때(`Delete Device`), 드라이버 패키지를 들이거나 뺄 때, 오래 쓰지 않은 장치를 정리할 때도 섹션이 생깁니다.

## 위치와 버전별 차이

| Windows | 파일 | 근거 |
|---|---|---|
| 2000·XP·Server 2003 | `%SystemRoot%\setupapi.log` 하나에 모두 적습니다. XP 에는 `setupapi.log.old` 도 있습니다. | Microsoft, ForensicsWiki |
| Vista 이후 | `%SystemRoot%\INF\setupapi.dev.log`, `%SystemRoot%\INF\setupapi.app.log` | Microsoft |
| 7 이후 | 위 두 파일에 `setupapi.offline.log` 가 더해집니다. | ForensicsWiki |
| 10 이후 | `setupapi.upgrade.log` 가 더해집니다. | ForensicsWiki |
| 11 25H2 | `setupapi.dev.<연월일>_<시분초>.log` 같은 날짜 붙은 옛 로그와 `setupapi.setup.log` 가 있을 수 있습니다. `setupapi.app.log` 는 없을 수 있습니다. |  |

XP 의 `setupapi.log` 는 이름을 바꾸거나 지우면 새로 시작합니다. XP 섹션의 첫 줄은 `[날짜 시각 … Driver Install]` 처럼 대괄호 한 줄로 되어 있어 Vista 이후 형식과 다릅니다.

### 로그 위치와 기록 수준을 바꾸는 값

두 값 모두 SOFTWARE 하이브의 `Microsoft\Windows\CurrentVersion\Setup` 키에 있습니다. 하이브 위치는 [하이브 파일 종류와 위치](../../../01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md)를 봅니다.

| 값 | 형식 | 뜻 |
|---|---|---|
| `LogPath` | REG_SZ | 로그를 둘 폴더입니다. 값이 없거나 폴더가 없으면 `%SystemRoot%\INF` 에 둡니다. |
| `LogLevel` | REG_DWORD | 기록 수준 (Event Level) 을 정합니다. `0xUUUUGHVW` 형식입니다. `VW` 는 앱 로그, `GH` 는 장치 로그를 정합니다. 윗자리 `UUUU` 는 쓰지 않습니다. |

`LogLevel` 의 `VW`·`GH` 바이트는 이렇게 풉니다.

| 바이트 값 | 뜻 |
|---|---|
| `0x00` 또는 값 없음 | 기본 수준으로 기록합니다. |
| `0x01`~`0x0F` | 그 로그를 끕니다. |
| `0x10`~`0x7F` | 기록하고, 윗자리 숫자를 수준으로 씁니다. 예: `0x50` 은 수준 5 입니다. |

기본 수준은 이렇습니다.

| 로그 | Windows 7 이후 | Vista SP2 | Vista SP1 이전 |
|---|---|---|---|
| 앱 로그 | 4 (SUMMARY) | 2 (WARNING) | 5 (DETAILS) |
| 장치 로그 | 5 (DETAILS) | 5 (DETAILS) | 5 (DETAILS) |

Windows 11 25H2 에서 `LogLevel` 값이 `0x20004001` 로 들어 있는 경우가 있습니다. 규칙대로 풀면 앱 로그는 꺼지고 장치 로그는 수준 4 로 켜지며, 쓰지 않는 윗자리에도 값이 있습니다. 이때는 `setupapi.app.log` 가 없습니다. 이 값을 넣은 주체는 공개 자료로 알 수 없으므로, `LogLevel` 이 0 이 아니라는 사실만으로 조작이라고 보지 않습니다.

## 구조

### 파일 전체

- ANSI 일반 텍스트이고, 문구는 영어입니다.
- 파일은 BOM 없이 시작하고 줄 끝이 CR LF (`0D 0A`) 입니다.
- 한국어판 Windows 에서는 서비스 표시 이름 같은 한글이 CP949 로 적힙니다. UTF-8 로 열면 글자가 깨집니다. [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)을 봅니다.
- 맨 앞은 머리말 (Text Log Header) 입니다. `[Device Install Log]` 아래에 OS 버전, 서비스 팩, 아키텍처가 있고 `[BeginLog]` 로 끝납니다.
- 날짜 붙은 옛 로그에도 머리말이 따로 있습니다.
- 머리말 뒤에는 섹션이 만든 순서대로 이어집니다. 줄 순서는 곧 기록한 순서입니다.
- 섹션 사이에 `[Boot Session: 2015/11/22 17:58:03.498]` 같은 줄이 끼어 있습니다. 공식 문서에는 이 줄의 설명이 없으므로 뜻을 확정하지 말고 보조 단서로만 씁니다.

### 섹션 하나

아래는 Windows 10·11 형식을 보여 주려고 만든 예시입니다. 장치 ID 와 시각은 지어낸 값입니다.

```
>>>  [Device Install (Hardware initiated) - USB\VID_1234&PID_5678\SN0001]
>>>  Section start 2024/01/02 03:04:05.678
     ump: Install needed due to device having problem code CM_PROB_NOT_CONFIGURED
     dvi: {Core Device Install} 03:04:05.690
     dvi:      Install Device: Starting device completed. 03:04:05.990
     dvi: {Core Device Install - exit(0x00000000)} 03:04:06.001
<<<  Section end 2024/01/02 03:04:06.012
<<<  [Exit status: SUCCESS]
```

| 부분 | 모양 | 뜻 |
|---|---|---|
| 섹션 제목 | `>>>  [제목 - 대상]` | 작업 이름과 대상입니다. 장치 설치에서는 대상이 장치 인스턴스 ID (Device Instance ID) 입니다. |
| 섹션 시작 | `>>>  Section start 날짜 시각` | 섹션을 연 시각입니다. |
| 본문 줄 | `접두어 범주: 들여쓰기 메시지` | 접두어 `!!!` 는 오류, `!` 는 경고, 공백은 정보입니다. |
| 섹션 끝 | `<<<  Section end 날짜 시각` | 섹션을 닫은 시각입니다. |
| 결과 | `<<<  [Exit status: SUCCESS]` | 작업 결과입니다. |

- 범주 (Event Category) 는 작업 종류를 알려 줍니다. `dvi:` 장치 설치, `ump:` 사용자 모드 PnP 관리자, `ndv:` 새 장치 마법사, `inf:` INF 처리, `cpy:` 파일 복사, `sto:` 드라이버 저장소, `sig:` 서명 확인, `set:` 일반 설치가 있습니다.
- 문서에 없는 범주도 나옵니다. `utl:`·`dvs:`·`cmd:` 가 그 예입니다.
- `cmd:` 줄에는 그 작업을 시작한 프로그램의 명령줄이 있습니다. 예를 들어 인쇄 스풀러나 디스크 정리 프로그램입니다. 장치를 꽂아서 생긴 설치 섹션에는 이 줄이 없습니다.
- 본문 줄 끝에 날짜 없이 시각만 붙는 경우가 있습니다.

### 문서 예시와 실제 형식이 다릅니다

Microsoft 문서의 섹션 예시에는 2005년 날짜가 찍혀 있습니다. 이 예시는 실제 Windows 10·11 파일과 세 곳이 다릅니다.

| 부분 | Microsoft 문서 예시 | Windows 10·11 파일 |
|---|---|---|
| 섹션 시작 | `>>>  2005/02/13 22:06:28.109: Section start` | `>>>  Section start 2015/11/22 17:59:28.110` |
| 섹션 끝 | `<<<  [2005/02/13 22:06:29.000: Section end]` | `<<<  Section end 날짜 시각` |
| 결과 | `<<<  [Exit Status(0x00000000)]` | `<<<  [Exit status: SUCCESS]` |

공개 파서 plaso 는 오른쪽 형식만 읽습니다. 다른 도구도 한쪽 형식만 읽을 수 있습니다.

### USB 저장장치 하나가 남기는 섹션

Windows 11 25H2 에서는 USB 메모리 하나를 처음 꽂으면 설치 섹션이 둘 생깁니다.

| 섹션 대상 | 설치한 것 |
|---|---|
| `USB\VID_xxxx&PID_xxxx\<일련번호>` | USB 장치. 드라이버는 `usbstor.inf` 입니다. |
| `SWD\WPDBUSENUM\_??_USBSTOR#Disk&Ven_…&Prod_…&Rev_…#<일련번호>&0#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}` | 휴대용 장치 (WPD) |

두 섹션의 시작 시각은 1초 안쪽으로 붙어 있습니다. `USBSTOR\Disk&…` 를 대상으로 한 섹션은 없고 로그 전체에서 `USBSTOR\Disk` 문자열도 나오지 않으므로, `USBSTOR` 로 찾지 말고 일련번호로 찾습니다. 일련번호가 Windows 가 만든 ID 일 수 있는데, 이 경우는 [USB 저장장치 목록 (USBSTOR)](usbstor.md)에서 다룹니다. VID·PID 읽는 법은 [USB 장치 식별자](enum-usb-vid-pid.md)에서 다룹니다.

> 그림 자리: USB 메모리 하나가 만든 두 설치 섹션(USB\VID…, SWD\WPDBUSENUM…)이 같은 일련번호로 USBSTOR·Enum\USB 레지스트리 항목에 이어지는 모습

## 증거로서 의미

### 증명하는 것

- 섹션에 적힌 장치 인스턴스를 이 PC 에 설치하는 작업이 있었습니다.
- 그 작업이 시작하고 끝난 현지 시각을 밀리초까지 알 수 있습니다.
- `Exit status` 로 설치가 성공했는지 알 수 있습니다.
- 어떤 INF·드라이버로 설치했는지 알 수 있습니다. 모르는 장치가 무슨 기능인지 짐작할 때 씁니다.
- 남아 있는 로그 범위 안에서 가장 이른 설치 섹션이 그 장치의 첫 설치 시각입니다.
- 이 로그는 레지스트리 밖의 파일입니다. 레지스트리의 USB 흔적만 지운 경우에도 이 로그에는 남을 수 있습니다.
- 오래 쓰지 않은 장치를 Windows 가 지운 기록도 남습니다. 레지스트리에서 사라진 장치를 여기서 찾을 수 있습니다.

### 증명하지 못하는 것

- 누가 꽂았는지 알 수 없습니다. 이 로그는 시스템 전체에 하나입니다. 사용자는 [MountPoints2](mountpoints2.md)로 좁힙니다.
- 장치에서 파일을 복사하거나 열었는지 알 수 없습니다.
- 마지막 연결 시각, 해제 시각, 연결 횟수를 알 수 없습니다.
- 가장 이른 섹션이 "처음 꽂은 때" 라고 단정할 수 없습니다. 옛 로그가 없어졌거나, 장치를 지운 뒤 다시 설치했을 수 있습니다.
- 섹션이 없다고 연결한 적이 없다는 뜻이 아닙니다. 로그를 껐거나, 다른 폴더에 두었거나, 지웠거나, 업그레이드로 새로 시작했을 수 있습니다.

### 보고서 문장 예

- 쓰지 않을 문장: "사용자는 2024년 1월 2일 03:04 에 이 USB 를 처음 꽂았다."
- 쓸 문장: "`setupapi.dev.log` 에 일련번호 ○○○ 인 장치를 대상으로 한 `Device Install (Hardware initiated)` 섹션이 있다. 섹션 시작 시각은 현지 시각 ○○○○-○○-○○ ○○:○○:○○.○○○ (UTC ○○:○○:○○) 이고, 결과는 SUCCESS 이다. 남아 있는 로그 가운데 이 장치에 대한 가장 이른 설치 기록이다. 누가 연결했는지는 이 기록만으로 알 수 없다."

## 시각 해석

| 시각 | 무엇을 뜻하나 | 기준 |
|---|---|---|
| `Section start` | 섹션을 연 때입니다. 장치 설치 섹션이면 설치를 시작한 때입니다. | 현지 시각, 시간대 표시 없음 |
| `Section end` | 섹션을 닫은 때입니다. | 현지 시각 |
| 본문 줄 끝 시각 | 그 단계의 시각입니다. 날짜가 없습니다. | 현지 시각 |
| `[Boot Session: …]` | 문서에 설명이 없습니다. | 날짜 모양은 섹션 시각과 같습니다. |
| 옛 로그 파일 이름 속 날짜·시각 | 그 파일 마지막 섹션의 시각과 같습니다. | 현지 시각 |

- 섹션 헤더의 시각은 현지 시각이므로, UTC 로 바꾸려면 기록할 당시의 시간대 설정이 필요합니다. [시간대 설정](../../system-account/time-zone.md)을 봅니다.
- 시간대의 `Bias` 값은 부호 있는 32비트로 읽습니다. UTC+9 는 `-540` 입니다. 부호 없이 읽으면 `4294966756` 이 됩니다.
- 일광 절약 시간이 끝나는 날에는 같은 현지 시각이 두 번 있습니다. 그 한 시간 안의 시각은 UTC 로 하나로 정할 수 없습니다.
- 섹션이 자정을 넘기면 본문 줄의 날짜는 섹션 시작 날짜와 다를 수 있습니다.
- 줄 순서는 기록한 순서입니다. 그런데 뒤에 나온 `Boot Session` 시각이 앞의 것보다 이른 경우가 있습니다. 이런 역전은 시계나 시간대를 바꾼 흔적일 수 있습니다. [시스템 시각을 바꿨나](../../../04-scenarios/activity/anti-forensics/system-time-change.md)의 절차로 확인합니다.
- 레지스트리의 첫 설치 시각 (`DEVPKEY_Device_FirstInstallDate`) 은 FILETIME 이고 UTC 입니다. 이 로그 시각을 UTC 로 바꾼 뒤에 비교합니다. 위치는 [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md)에서 다룹니다.
- 이 로그의 설치 시작·끝 시각은 장치 컨테이너 속성의 두 시각과 맞고, 그 두 시각은 레지스트리의 설치·첫 설치 시각과 조금 다릅니다. 그러므로 이 로그 시각과 레지스트리 첫 설치 시각이 딱 맞지 않을 수 있습니다. 차이의 크기는 실제 데이터로 확인합니다.

## 함정과 한계

1. **옛 로그를 빠뜨리는 실수.** Windows 11 에서는 옛 내용이 `setupapi.dev.<날짜>_<시각>.log` 로 따로 남습니다. `setupapi.dev*.log` 를 모두 모아서 봅니다. 파일을 언제, 몇 개까지 넘기는지는 공식 문서에 없습니다.
2. **업그레이드 뒤에 로그가 새로 시작합니다.** 기능 업데이트를 하면 그날부터 로그가 새로 시작하고, 그 전 내용은 `INF` 폴더에 남지 않을 수 있습니다. 업그레이드 전 기록은 [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)이나 `Windows.old` 폴더에서 찾습니다.
3. **"처음 연결" 이 두 번 나올 수 있습니다.** 같은 장치 인스턴스의 설치 섹션이 같은 날 두 번 있을 수 있습니다. 가장 이른 것을 쓰고, 나머지는 따로 설명합니다.
4. **장치 정리 뒤 다시 설치될 수 있습니다.** `Plug and Play Cleanup` 예약 작업은 30일 넘게 꽂지 않은 장치를 레지스트리에서 지웁니다(Windows 8.1·10). 이 작업은 `Device and Driver Disk Cleanup Handler` 섹션에 `set: Device … was removed.` 로 남습니다. 지운 장치를 다시 꽂으면 설치 섹션이 새로 생길 수 있습니다. 이 섹션의 `cmd:` 줄은 Windows 8.1·10 에서는 `taskhostw.exe`, Windows 11 에서는 디스크 정리 프로그램(`cleanmgr.exe /autocleanstoragesense`) 입니다.
5. **로그를 끄거나 옮길 수 있습니다.** `LogLevel`·`LogPath` 값과 그 키의 [마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md)을 봅니다. 다만 앞에서 본 것처럼 0 이 아닌 `LogLevel` 이 곧 조작은 아닙니다.
6. **텍스트 파일이라 고치기 쉽습니다.** 관리자 권한이 있으면 지우거나 줄을 뺄 수 있습니다. 머리말이 없는지, 기간이 비는지, 시각이 거꾸로 가는지 봅니다. 파일 크기가 줄어든 흔적은 [$MFT](../../filesystem/mft.md)와 [$UsnJrnl](../../filesystem/usnjrnl.md)에서 찾습니다.
7. **지운 로그는 조각으로 되살릴 수 있습니다.** 형식이 일정한 텍스트라서 비할당 영역에서 찾기 쉽습니다. [비할당 영역과 슬랙](../../../03-techniques/analysis/data-recovery/unallocated-slack-space.md)을 봅니다.
8. **USBSTOR 에 없는 장치도 여기에는 남을 수 있습니다.** 이 로그는 드라이버 종류와 관계없이 설치 작업을 적습니다. UASP 장치나 SD 카드는 [USBSTOR 에 안 남는 장치](uasp-scsi-sd.md)를 함께 봅니다.
9. **인코딩.** 비 ASCII 글자는 시스템 ANSI 코드 페이지로 적힙니다. 문자열 검색 도구의 인코딩을 맞춥니다.

## 직접 분석해 보기

### 텍스트와 헥스로 한 번

1. `%SystemRoot%\INF\setupapi*.log` 를 모두 사본으로 확보합니다. XP 는 `%SystemRoot%\setupapi.log*` 입니다.
2. SOFTWARE 하이브에서 `LogPath` 를 봅니다. 값이 있으면 그 폴더에서도 수집합니다.
3. 조사할 장치의 일련번호를 [USBSTOR](usbstor.md) 에서 구합니다.
4. 모든 로그에서 일련번호를 대소문자 구분 없이 찾습니다. ANSI 파일이므로 한 바이트 문자로 찾습니다. UTF-16 으로 찾으면 걸리지 않습니다.
5. 걸린 줄에서 위로 올라가 `>>>  [` 로 시작하는 섹션 제목을 찾습니다. 바로 다음 줄에서 `Section start` 시각을 읽습니다.
6. 아래로 내려가 `<<<  [Exit status:` 줄에서 결과를 읽습니다.
7. 기록 당시 시간대로 UTC 를 구합니다.
8. 파일이 없거나 비어 있으면 비할당 영역에서 `>>>  [Device Install` 바이트열을 찾습니다.

아래는 앞의 예시 두 줄을 형식대로 바이트로 옮긴 것입니다. 실제 데이터에서 나온 값이 아닙니다.

```
오프셋  바이트                                              글자
000000  3E 3E 3E 20 20 5B 44 65 76 69 63 65 20 49 6E 73    >>>  [Device Ins
000010  74 61 6C 6C 20 28 48 61 72 64 77 61 72 65 20 69    tall (Hardware i
000020  6E 69 74 69 61 74 65 64 29 20 2D 20 55 53 42 5C    nitiated) - USB\
000030  56 49 44 5F 31 32 33 34 26 50 49 44 5F 35 36 37    VID_1234&PID_567
000040  38 5C 53 4E 30 30 30 31 5D 0D 0A 3E 3E 3E 20 20    8\SN0001]..>>>  
000050  53 65 63 74 69 6F 6E 20 73 74 61 72 74 20 32 30    Section start 20
000060  32 34 2F 30 31 2F 30 32 20 30 33 3A 30 34 3A 30    24/01/02 03:04:0
000070  35 2E 36 37 38 0D 0A                               5.678..
```

- 섹션 제목 줄은 `3E 3E 3E 20 20 5B` (`>>>` 와 공백 두 칸, `[`) 로 시작합니다.
- 섹션 끝 줄은 `3C 3C 3C 20 20` (`<<<` 와 공백 두 칸) 으로 시작합니다.
- 카빙할 때는 이 두 바이트열을 짝으로 찾으면 섹션 하나를 온전히 떼어 낼 수 있습니다.

### 공개 도구로 한 번

- 텍스트 편집기나 `grep` 같은 문자열 검색 도구로 충분합니다. 예: 일련번호로 찾고 앞뒤 몇 줄을 함께 봅니다.
- 타임라인 도구 plaso 에는 이 로그의 파서가 있습니다. 이 파서는 섹션 시작·끝 시각을 현지 시각으로 처리합니다. 그래서 분석할 때 시간대를 맞게 지정해야 합니다.
- 도구가 섹션을 0건으로 내면 먼저 형식을 확인합니다. 앞의 "문서 예시와 실제 형식이 다릅니다" 표를 봅니다.
- 도구 결과와 직접 찾은 결과가 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 절차를 따릅니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 값 | 링크 |
|---|---|---|
| USBSTOR | 일련번호, 제조사·모델 | [USB 저장장치 목록 (USBSTOR)](usbstor.md) |
| Enum\USB | VID·PID·일련번호 | [USB 장치 식별자 (Enum\USB VID·PID)](enum-usb-vid-pid.md) |
| 장치 속성 | 첫 설치 시각(UTC)과 `Section start`(현지) | [연결·해제 시각](deviceclasses-device-properties-0064-0066-0067.md) |
| MountedDevices | 드라이브 문자 | [드라이브 문자 매핑 (MountedDevices)](mounteddevices.md) |
| MountPoints2 | 어느 사용자 환경에서 연결됐나 | [사용자별 장치 연결 (MountPoints2)](mountpoints2.md) |
| WPD·EMDMgmt | 볼륨 이름, WPD 장치 ID | [휴대용 장치·볼륨 이름 기록 (WPD·EMDMgmt)](wpd-emdmgmt.md) |
| AmCache 장치 항목 | 같은 장치 ID 가 다른 파일에도 있나 | [장치 항목 (InventoryDevicePnp)](../../execution/amcache-hve/inventorydevicepnp.md) |
| 외부 장치 연결 이벤트 | 설치 시각 앞뒤의 연결 이벤트 | [외부 장치 연결 이벤트](../../event-logs/partition-diagnostic-kernel-pnp-driverframeworks.md) |
| 시간대 설정 | 현지 시각을 UTC 로 바꿀 값 | [시간대 설정 (Time Zone)](../../system-account/time-zone.md) |
| 켜짐·꺼짐 이벤트 | `Boot Session` 줄과 부팅 시각 | [켜짐·꺼짐](../../event-logs/power-on-off-events.md) |

휴대폰은 [스마트폰으로 옮겼나](../../../04-scenarios/exfiltration/data-exfiltration/mtp-phone-link.md)를, USB 흔적 전체 흐름은 [USB 저장장치 흔적](index.md)과 [USB 로 무엇을 가져갔나](../../../04-scenarios/exfiltration/data-exfiltration/usb.md)를 봅니다.

## 실습

NIST CFReDS 같은 공개 실습 이미지 가운데 USB 사용이 들어 있는 Windows 이미지를 골라 풀어 봅니다.

1. `setupapi.dev*.log` 파일이 몇 개인가요? 파일마다 첫 섹션과 마지막 섹션의 시각을 적습니다. 파일 사이에 빈 기간이 있나요?
2. USBSTOR 에 있는 일련번호마다 로그에서 가장 이른 설치 섹션을 찾습니다. 섹션 대상은 `USB\VID…`, `SWD\WPDBUSENUM…`, `USBSTOR\…` 가운데 무엇인가요?
3. 그 `Section start` 를 UTC 로 바꿉니다. 레지스트리의 첫 설치 시각과 얼마나 차이 나나요?
4. 로그에는 있는데 USBSTOR 에는 없는 장치가 있나요? 있다면 정리 섹션(`Device and Driver Disk Cleanup Handler`)에 그 장치가 나오나요?
5. SOFTWARE 하이브의 `LogLevel`·`LogPath` 값은 무엇인가요? 규칙대로 풀면 어떤 로그가 켜져 있나요?
6. `Boot Session` 줄이나 섹션 시각이 거꾸로 가는 곳이 있나요? 있다면 시간 변경 이벤트와 맞춰 봅니다.

## 참고 문헌

- Microsoft Learn, SetupAPI 텍스트 로그 문서 묶음 — "SetupAPI Text Logs" https://learn.microsoft.com/en-us/windows-hardware/drivers/install/setupapi-text-logs · "Format of a Text Log Header" https://learn.microsoft.com/en-us/windows-hardware/drivers/install/format-of-a-text-log-header · "Format of a Text Log Section Header" https://learn.microsoft.com/en-us/windows-hardware/drivers/install/format-of-a-text-log-section-header · "Format of a Text Log Section Body" https://learn.microsoft.com/en-us/windows-hardware/drivers/install/format-of-a-text-log-section-body · "Format of a Text Log Section Footer" https://learn.microsoft.com/en-us/windows-hardware/drivers/install/format-of-a-text-log-section-footer · "Setting the Event Level for a Text Log" https://learn.microsoft.com/en-us/windows-hardware/drivers/install/setting-the-event-level-for-a-text-log · "Setting the Directory Path of the Text Logs" https://learn.microsoft.com/en-us/windows-hardware/drivers/install/setting-the-directory-path-of-the-text-logs · "DEVPKEY_Device_FirstInstallDate" https://learn.microsoft.com/en-us/windows-hardware/drivers/install/devpkey-device-firstinstalldate
- Microsoft Learn, "SetupAPI Logging (Windows Server 2003, Windows XP, and Windows 2000)" — https://learn.microsoft.com/en-us/windows-hardware/drivers/install/setupapi-logging--windows-server-2003--windows-xp--and-windows-2000-
- plaso, SetupAPI 로그 파서 소스와 공개 시험 파일(2026-09 열람) — https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/setupapi.py · https://github.com/log2timeline/plaso/blob/main/test_data/setupapi.dev.log
- David Cowen, Hacking Exposed Computer Forensics Blog, "Daily Blog #66: Understanding the artifacts setupapi.log/setupapi.dev.log", 2013 — https://www.hecfblog.com/2013/08/daily-blog-66-understanding-artifacts.html · "Windows, Now with built in Anti Forensics!", 2017 — https://www.hecfblog.com/2017/04/windows-now-built-in-anti-forensics.html
- ForensicsWiki, "Setup API Logs" — https://forensics.wiki/setup_api_logs/ · "USB History Viewing" — https://forensics.wiki/usb_history_viewing/
- Jason Hale, Digital Forensics Stream, "Leveraging the DeviceContainers Key", 2015 — https://df-stream.com/2015/02/leveraging-devicecontainers-key/
