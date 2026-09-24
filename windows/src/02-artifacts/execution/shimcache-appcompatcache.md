# 심캐시 (ShimCache·AppCompatCache)

## 한 줄 요약

SYSTEM 하이브의 `AppCompatCache` 값에 실행 파일 경로와 그 파일의 마지막 수정 시각이 목록으로 남습니다. 이 시각은 실행 시각이 아닙니다. Windows 8 이후의 항목이 실행을 뜻하는지는 아직 확인하지 못했습니다.

## 무엇을 기록하나 · 왜 생기나

- Mandiant 는 심캐시를 Microsoft 가 Windows XP 부터 만든 캐시로 설명합니다. 실행한 프로그램의 호환성 문제를 추적하려는 캐시입니다.
- 여러 자료가 이 캐시를 응용 프로그램 호환성 데이터베이스 (Application Compatibility Database) 의 일부로 소개합니다. libyal 은 이 설명에 근거가 없다고 적습니다.
- "Application Compatibility Cache" 와 "Shim Cache" 가 정확히 어떻게 다른지는 알려져 있지 않고 자료마다 두 이름을 섞어 쓰므로, 이 페이지에서는 심캐시로 부릅니다.
- 항목마다 파일 경로와 파일의 마지막 수정 시각이 들어 있고, Windows 버전에 따라 파일 크기나 플래그도 들어 있습니다.
- 캐시를 다루는 DLL 로 apphelp.dll(AppHelp·호환성 DB)과 kernel32.dll(기본 캐시 관리)이 알려져 있습니다.
- libyal 은 관련 키로 `HKLM\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags` 를 듭니다.

Mandiant 가 정리한 항목이 생기는 조건은 아래와 같습니다.

- 파일을 실행하면 항목이 생깁니다. XP 이후 모든 버전이 그렇습니다.
- 이미 있는 파일의 메타데이터가 바뀐 뒤 다시 실행하면 새 항목이 생깁니다.
- Vista·7·Server 2008·Server 2012 에서는 사용자가 탐색기로 연 폴더 안의 파일도 항목으로 남을 수 있습니다. 이 항목은 Application Experience Lookup Service 가 남깁니다.

## 위치와 버전별 차이

| Windows | 위치 |
|---|---|
| 2000 | `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatibility` 아래, 실행 파일 이름(예: Uninstall.exe)으로 된 하위 키 |
| XP | `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatibility` |
| 2003 이후 | `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache` 키의 `AppCompatCache` 값 |

- Windows 2000 의 하위 키가 뒤 버전의 `AppCompatCache` 값과 목적이 같은지는 libyal 도 불분명하다고 적습니다.
- 오프라인 하이브에는 `CurrentControlSet` 이 없습니다. `ControlSet00X` 아래에서 찾습니다. Mandiant 도 오프라인 경로를 `SYSTEM\ControlSet00X\...` 로 적습니다.
- 어느 `ControlSet00X` 가 현재 것인지는 `SYSTEM\Select` 의 `Current` 값으로 고른다는 설명이 흔합니다. 이 설명은 이번에 연 자료로 확인하지 못했습니다.
- Windows 11 PC 한 대의 `Select` 값은 Current=1, Default=1, LastKnownGood=1, Failed=0 이었습니다. (확인 범위: Win11 25H2 한 대)
- 같은 PC 의 `AppCompatCache` 키에는 값이 셋 있었습니다. `AppCompatCache`(REG_BINARY, 214,066바이트), `CacheMainSdb`(REG_BINARY, 6,512바이트), `SdbTime`(REG_BINARY, 96바이트)입니다. (확인 범위: Win11 25H2 한 대)

하이브 파일의 구조와 수집 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

## 구조

값 하나는 헤더와 항목 목록으로 이루어지고, 헤더 크기와 서명은 Windows 버전마다 다릅니다. 아래 표는 libyal 의 정리이며 최대 항목 수는 libyal 도 추정으로 적은 값입니다.

| Windows | 헤더 크기 | 서명 | 항목 수 위치 | 최대 항목 수(추정) |
|---|---|---|---|---|
| XP 32비트 | 400바이트 | `ef be ad de` (0xDEADBEEF) | 오프셋 4 | 92 |
| 2003 (64비트 XP 포함) | 8바이트 | `fe 0f dc ba` (0xBADC0FFE) | 오프셋 4 | 512 |
| Vista·2008 | 8바이트 | `fe 0f dc ba` (0xBADC0FFE) | 오프셋 4 | 1024 |
| 7·2008 R2 | 128바이트 | `ee 0f dc ba` (0xBADC0FEE) | 오프셋 4 | 1024 |
| 8.0 | 128바이트 (오프셋 0 의 값이 128) | 항목마다 `00ts` | — | — |
| 8.1 | — | 항목마다 `10ts` | — | — |
| 10 | 48바이트 (오프셋 0 의 값이 48) | 항목마다 `10ts` | 오프셋 36 | — |
| 10 Creators Update 이후 | 52바이트 (오프셋 0 의 값이 52) | 항목마다 `10ts` | 오프셋 40 | — |

버전별 항목 내용은 아래와 같습니다.

- **XP 32비트.** 헤더 오프셋 8 에 최근 사용 순 (LRU) 배열의 항목 수가 있고, 오프셋 16 부터 그 배열이 있습니다. 항목 하나는 552바이트입니다.
- **2003.** 항목은 32비트에서 24바이트, 64비트에서 32바이트입니다. 경로 크기·최대 경로 크기·경로 오프셋·마지막 수정 시각(FILETIME)·파일 크기가 들어 있습니다.
- **Vista·2008.** 2003 의 파일 크기 자리에 Insertion flags(4바이트)와 Shim flags(4바이트)가 들어갑니다. 32비트에서는 오프셋 16·20, 64비트에서는 오프셋 24·28 입니다. 캐시가 비면 헤더만 남습니다.
- **7·2008 R2.** 항목은 32비트에서 32바이트, 64비트에서 48바이트입니다. 경로 크기·최대 경로 크기·경로 오프셋·마지막 수정 시각·Insertion flags·Shim flags·Data 크기·Data 오프셋이 들어 있습니다.
- **8.0 이후.** 항목마다 서명(`00ts` 또는 `10ts`)이 붙습니다. Windows 10 항목은 길이가 제각각입니다.

**XP 항목 (552바이트)**

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 528 | 경로 (UTF-16). 남는 자리에 이전 데이터가 남을 수 있습니다 |
| 528 | 8 | 마지막 수정 시각 (FILETIME) |
| 536 | 8 | 파일 크기 |
| 544 | 8 | 마지막 갱신 시각 (FILETIME) |

**Windows 10 항목 (길이 가변)**

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 4 | 서명 `10ts` |
| 4 | 4 | 알 수 없음 |
| 8 | 4 | 항목 데이터 크기. 앞 12바이트를 뺀 크기입니다 |
| 12 | 2 | 경로 크기 (바이트) |
| 14 | 경로 크기 | 경로 (UTF-16LE, 끝 NUL 없음) |
| 경로 다음 | 8 | 마지막 수정 시각 (FILETIME) |
| 그다음 | 4 | Data 크기 |
| 그다음 | Data 크기 | Data |

- libyal 의 Windows 10 항목 표에는 Insertion flags·Shim flags 칸이 없습니다.
- libyal 은 Insertion flags 의 0x00000002 를 CSRSS 가 실행한 표시로 적습니다. 다만 이 해석을 확정하지 않은 값으로 표시해 둡니다.

> 그림 자리: Windows 10 형식의 헤더 52바이트 뒤로 `10ts` 항목이 이어지는 모습. 항목 데이터 크기로 다음 항목을 찾는 화살표

### Windows 11 25H2 에서 본 모습

아래는 모두 Windows 11 PC 한 대에서 본 것입니다. (확인 범위: Win11 25H2 한 대)

- 헤더 첫 4바이트는 0x34(52)였습니다. Creators Update 이후 형식과 같습니다.
- 헤더 오프셋 16 의 값은 22 였습니다.
- libyal 이 항목 수라고 적은 헤더 오프셋 40 의 값은 0 이었습니다.
- 그래서 `10ts` 항목을 처음부터 끝까지 따라가며 셌습니다. 항목은 904개였고, 마지막 항목이 값 끝(214,066바이트)에 정확히 닿았습니다.
- 경로가 `C:\` 로 시작하는 항목은 689개였습니다. `\\?\` 로 시작하는 항목은 4개였습니다.
- 나머지 211개는 패키지 앱 항목으로 보였습니다. 경로 칸이 탭으로 나뉜 7칸(끝 탭 포함)이었고, 시각은 모두 0 이었습니다.
- 첫 패키지 앱 항목의 칸은 16진 숫자 칸 세 개, `8664`, 패키지 이름, 게시자 ID 순이었습니다. 각 칸의 뜻은 확인하지 못했습니다.
- 확장자는 .exe 656개, 확장자 없음 22개, .tmp 9개, .com 3개, .dll 2개, .scr 1개였습니다.
- 항목의 Data 크기는 72·84·36·24·60·48바이트 등으로 제각각이었습니다.

## 증거로서 의미

### 증명하는 것

- 항목의 경로에 파일이 있었던 적이 있습니다. 지금은 없는 파일도 남습니다. Windows 11 PC 한 대에서 `C:\` 경로 항목 689개 가운데 259개는 그 경로에 파일이 더는 없었습니다. (확인 범위: Win11 25H2 한 대)
- 항목의 시각은 그 파일의 마지막 수정 시각입니다. 지금 파일의 수정 시각과 다르면 그 사이에 파일이 바뀌었을 수 있습니다.
- Vista·7·Server 2008·Server 2012 에서는 항목마다 실행 표시 (Process Execution Flag) 가 있다고 Mandiant 는 설명합니다. 프로세스를 만들 때 CSRSS 가 이 표시를 켭니다. 표시가 켜져 있으면 실행한 항목입니다.
- XP·2003 에는 이 표시가 없습니다. Mandiant 는 이 두 버전의 항목을 시스템에 있었고 한 번은 실행됐을 가능성이 높은 파일로 봅니다.

### 증명하지 못하는 것

- **실행 시각.** 항목의 시각은 수정 시각입니다. Mandiant 도 "it is not indicative of the file execution time" 이라고 적습니다.
- **Windows 8·10·11 항목의 실행 여부.** 이번에 연 자료로 확인하지 못했습니다. Mandiant 글은 8·10·2012 R2 를 다루지 않습니다. libyal 의 Windows 10 항목 표에는 플래그 칸이 없습니다. "Windows 10 이후 심캐시만으로는 실행을 증명하지 못한다" 는 설명이 흔하지만 이 설명도 확인하지 못했습니다. 실행을 말하려면 다른 아티팩트로 받칩니다.
- **탐색만 한 파일과 실행한 파일의 구분 (Vista\~2012).** 실행 표시가 꺼진 항목은 폴더를 탐색하다 생겼을 수 있습니다.
- **누가 실행했나.** 항목에 사용자 칸이 없습니다. SYSTEM 하이브는 사용자마다 나뉘지 않습니다.
- **몇 번 실행했나.** 항목에 실행 횟수 칸이 없습니다.

보고서에는 "이 검체의 심캐시에 이 경로의 항목이 있고, 항목에 적힌 파일 수정 시각은 이 시각이다" 처럼 씁니다. Windows 8 이후 검체라면 이 항목만으로 "실행했다" 고 쓰지 않습니다.

## 시각 해석

- 항목의 시각은 파일의 마지막 수정 시각이며, NTFS 에서는 `$STANDARD_INFORMATION` 의 수정 시각입니다. 이 속성은 [마스터 파일 테이블](../filesystem/mft.md) 에서 다룹니다.
- 시각은 FILETIME 이고 UTC 로 읽습니다. 변환은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
- 예외가 하나 있습니다. PsExec 는 원격 PC 에 PSEXESVC.exe 를 새로 만들므로 이 항목의 수정 시각은 파일을 만든 시각과 같고, 결과적으로 실행 무렵의 시각이 됩니다.
- XP 항목에는 마지막 갱신 시각 칸이 따로 있습니다(오프셋 544).
- 목록은 위에서 아래로 최근 사용 순 큐입니다. 맨 위가 가장 최근 항목입니다. 시각은 수정 시각이라서 목록 순서와 시각 순서가 다를 수 있습니다.
- Windows 11 PC 한 대에서 시각이 1970-01-01 00:00:00(UTC)인 항목이 있었습니다. 패키지 앱 항목의 시각은 모두 0 이었습니다. 이런 값은 타임라인에 그대로 넣지 말고 파일 쪽 시각과 맞춰 봅니다. (확인 범위: Win11 25H2 한 대)
- 같은 PC 에서 `C:\` 경로 항목 689개 가운데 404개는 지금 파일의 수정 시각과 값이 정확히 같았습니다. 26개는 달랐습니다. (확인 범위: Win11 25H2 한 대)
- `AppCompatCache` 키의 마지막 기록 시각은 캐시가 쓰인 시각이 아닐 수 있습니다. 같은 키에 `CacheMainSdb`·`SdbTime` 값도 있기 때문입니다. Windows 11 PC 한 대에서 이 키의 마지막 기록 시각은 마지막 부팅 두 시간 뒤였습니다. (확인 범위: Win11 25H2 한 대)

## 함정과 한계

- **수정 시각을 실행 시각으로 읽는 오해.** 가장 흔한 오판입니다. 실행 시각은 [프리페치](prefetch/index.md) 나 [프로세스 생성](../event-logs/4688.md) 이벤트에서 찾습니다.
- **최근 항목이 빠질 수 있습니다.** Mandiant 는 이 캐시가 "somewhat volatile" 하니 되도록 빨리 보존하라고 적습니다. 캐시를 메모리에 두었다가 종료나 재부팅 때만 레지스트리에 쓴다는 설명도 흔합니다. 이 설명은 이번에 연 자료로 확인하지 못했습니다. 켜진 PC 는 [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) 과 [메모리 분석](../../03-techniques/analysis/memory-forensics/index.md) 도 함께 검토합니다.
- **헤더의 항목 수를 믿지 않습니다.** Windows 11 PC 한 대에서 헤더의 항목 수 칸은 0 이었지만 실제 항목은 904개였습니다. 항목을 끝까지 따라가며 셉니다. (확인 범위: Win11 25H2 한 대)
- **32비트와 64비트의 항목 크기가 다릅니다.** 2003·Vista·7 형식은 운영체제의 비트 수에 맞는 표로 읽습니다.
- **XP 경로 칸에 이전 데이터가 남습니다.** 528바이트 경로 칸의 남는 자리에 앞 항목의 글자가 남을 수 있습니다. 문자열 끝의 NUL 뒤는 버립니다.
- **실행 파일만 있지 않습니다.** Windows 11 PC 한 대에는 .tmp·.dll·.scr 과 확장자 없는 항목도 있었습니다. (확인 범위: Win11 25H2 한 대)
- **캐시를 비우는 명령이 있습니다.** Vista 이후에는 `Rundll32.exe apphelp.dll,ShimFlushCache`, XP·2003 에서는 `Rundll32.exe kernel32.dll,BaseFlushAppcompatCache` 입니다. Vista 형식은 캐시가 비면 헤더만 남습니다. 항목이 없거나 너무 적으면 이전 시점 하이브를 [섀도 복사본](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에서 꺼내 비교합니다. 명령 실행 흔적은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름으로 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 libyal 명세로 만든 예시입니다. 특정 검체에서 꺼낸 값이 아닙니다. 경로 `C:\a.exe` 도 예시로 넣은 값입니다.

**헤더 첫 4바이트.**

```
34 00 00 00
```

리틀 엔디언으로 읽으면 0x34, 곧 52 입니다. Windows 10 Creators Update 이후 형식입니다. 헤더 52바이트 뒤, 곧 오프셋 52 에서 첫 항목이 시작합니다.

**`10ts` 항목 하나 (Data 크기 0 으로 만든 예시).**

```
31 30 74 73                                       서명 "10ts"
?? ?? ?? ??                                       알 수 없음
1E 00 00 00                                       항목 데이터 크기 = 30
10 00                                             경로 크기 = 16바이트
43 00 3A 00 5C 00 61 00 2E 00 65 00 78 00 65 00   경로 "C:\a.exe"
00 C0 89 76 45 3C DA 01                           마지막 수정 시각
00 00 00 00                                       Data 크기 = 0
```

1. 첫 4바이트 `31 30 74 73` 은 ASCII 로 `10ts` 입니다. 항목의 시작이 맞습니다.
2. 오프셋 8 의 `1E 00 00 00` 은 30 입니다. 앞 12바이트를 뺀 나머지 길이입니다. 2(경로 크기) + 16(경로) + 8(시각) + 4(Data 크기) = 30 입니다.
3. 오프셋 12 의 `10 00` 은 16 입니다. 경로가 16바이트, 곧 UTF-16LE 여덟 글자입니다. 인코딩은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.
4. 경로 뒤 8바이트를 리틀 엔디언으로 읽으면 `0x01DA3C457689C000` 입니다. FILETIME 으로 바꾸면 2024-01-01 00:00:00(UTC) 입니다. 실행 시각이 아니라 파일의 수정 시각입니다.
5. 다음 항목은 이 항목 시작점에서 12 + 30 = 42바이트 뒤에 있습니다. 이 예시에서는 오프셋 52 + 42 = 94 입니다.

### 공개 도구로 한 번

1. SYSTEM 하이브와 하이브 로그를 함께 사본으로 뜹니다.
2. 레지스트리 뷰어로 사본을 열고 쓸 `ControlSet00X` 를 고릅니다.
3. `Control\Session Manager\AppCompatCache` 의 `AppCompatCache` 값을 엽니다. 첫 4바이트로 형식을 확인합니다.
4. 심캐시를 풀어 주는 공개 파서로 목록을 뽑습니다.
5. 파서가 보여 준 항목 수를 직접 센 수와 맞춰 봅니다. 헤더의 항목 수만 믿는 파서는 항목을 놓칠 수 있습니다.
6. 항목 하나를 골라 위 헥스 풀이대로 경로와 시각을 직접 한 번 읽어 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 프리페치 | 같은 실행 파일의 실행 횟수와 실행 시각을 봅니다 | [프리페치](prefetch/index.md) |
| AmCache | 같은 경로의 실행 파일 기록이 있는지 봅니다 | [AmCache](amcache-hve/index.md) |
| BAM | 사용자 계정별로 남은 최근 실행 시각을 봅니다 | [BAM·DAM](background-activity-moderator.md) |
| UserAssist | 탐색기로 띄운 횟수와 마지막 실행 시각을 봅니다 | [UserAssist](userassist.md) |
| MUICache | 사용자가 쓰기 시작한 프로그램 이름이 있는지 봅니다 | [MUICache](muicache.md) |
| 프로그램 호환성 도우미 | 같은 경로가 있는지 봅니다 | [프로그램 호환성 도우미](pca.md) |
| 마스터 파일 테이블 | 파일의 지금 수정 시각과 항목 시각을 비교합니다 | [마스터 파일 테이블](../filesystem/mft.md) |
| 프로세스 생성 이벤트 | 실행 시각을 이벤트로 확인합니다 | [프로세스 생성](../event-logs/4688.md) |
| 섀도 복사본 | 이전 시점 캐시에 지금은 없는 항목이 있는지 봅니다 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

실행 흔적 전체를 엮는 흐름은 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md) 에 있습니다. 시각을 한 줄로 늘어놓는 방법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등)의 SYSTEM 하이브로 아래 질문을 풀어 봅니다.

1. 검체의 Windows 버전은 무엇입니까? 헤더 첫 4바이트는 그 버전의 형식과 맞습니까?
2. 헤더의 항목 수 칸과 직접 따라가며 센 항목 수가 같습니까?
3. 맨 위 항목 다섯 개의 시각을 직접 FILETIME 으로 바꿔 봅니다. 도구가 보여 주는 값과 같습니까?
4. 목록에 있는 경로 가운데 지금 디스크에 없는 파일은 몇 개입니까?
5. 같은 실행 파일이 프리페치에도 있습니까? 프리페치의 실행 시각과 심캐시의 수정 시각은 어떻게 다릅니까?
6. Vista·7 검체라면 실행 표시가 꺼진 항목은 무엇입니까? 그 폴더를 탐색한 흔적이 [셸백](../file-folder-usage/shellbags/index.md) 에 있습니까?

## 참고 문헌

1. libyal, *winreg-kb: Application compatibility cache* (버전별 위치, 헤더·항목 구조, 서명, 시각의 뜻, 캐시 비우기 명령, 관련 DLL·키). https://raw.githubusercontent.com/libyal/winreg-kb/main/docs/sources/system-keys/Application-compatibility-cache.md
2. Timothy Parisi, *Caching Out: The Value of Shimcache for Investigators*, Mandiant (Google Cloud Blog), 2015-06-17 (만든 목적, 실행 표시, 항목이 생기는 조건, 최근 사용 순, 실행 시각이 아니라는 점, PsExec 예외, 휘발성, 오프라인 경로 표기). https://cloud.google.com/blog/topics/threat-intelligence/caching-out-the-val/
