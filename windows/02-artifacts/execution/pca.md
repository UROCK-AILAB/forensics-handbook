# 프로그램 호환성 도우미 (PCA)

## 한 줄 요약

Windows 11 22H2 부터 `C:\Windows\appcompat\pca\` 폴더에 글자 파일 세 개가 생깁니다. `PcaAppLaunchDic.txt` 에는 실행 파일 경로와 시각이 한 줄씩 남고, `PcaGeneralDb0.txt` 에는 프로그램의 비정상 종료·설치 실패·호환성 판정이 칸 여덟 개로 남으며, 사용자 하이브와 SOFTWARE 하이브의 `AppCompatFlags` 키에도 관련 기록이 있습니다.

## 무엇을 기록하나 · 왜 생기나

프로그램 호환성 도우미 (Program Compatibility Assistant, PCA) 는 프로그램 호환성 문제를 다루는 Windows 기능입니다. 서비스 이름은 `PcaSvc` 이고 표시 이름은 "Program Compatibility Assistant Service" 이며, 시작 유형은 자동이었고 실행 중이었습니다. (확인 범위: Win11 25H2 한 대) 세 파일을 어느 프로세스가 쓰는지는 이번 자료로 확인하지 못했습니다.

| 기록 | 담는 것 |
|---|---|
| `PcaAppLaunchDic.txt` | 실행 파일 경로와 시각입니다. AboutDFIR 글은 이 시각을 마지막 실행 시각으로 봅니다 |
| `PcaGeneralDb0.txt` | 실행 시각, 상태 숫자, 경로, 파일 설명, 제조사, 버전, ProgramId, 끝 칸 문장입니다 |
| `PcaGeneralDb1.txt` | 관찰한 PC 에서는 0바이트였습니다 (확인 범위: Win11 25H2 한 대) |
| 레지스트리 `AppCompatFlags` | 호환 모드 설정 (`Layers`) 과, 값 이름이 실행 파일 경로인 목록 (`Compatibility Assistant\Store`) 등입니다 |

실행 흔적 가운데 새로 생긴 기록이고, 글자 파일이라 전용 도구 없이도 읽을 수 있습니다. 관찰한 값으로 보면 `PcaGeneralDb0.txt` 는 정상 실행 목록이 아니라 비정상 종료·설치 실패·호환성 판정 같은 사건 기록에 가깝습니다. (확인 범위: Win11 25H2 한 대)

## 위치와 버전별 차이

### 파일

| 파일 | 위치 | 문자 인코딩 (관찰) |
|---|---|---|
| `PcaAppLaunchDic.txt` | `C:\Windows\appcompat\pca\` | BOM 없는 1바이트 문자, 줄 끝 CRLF |
| `PcaGeneralDb0.txt` | 같은 폴더 | BOM 없는 UTF-16 LE, 줄 끝 LF (`0A 00`) 만 |
| `PcaGeneralDb1.txt` | 같은 폴더 | 0바이트여서 확인하지 못했습니다 |

인코딩 칸은 관찰입니다. (확인 범위: Win11 25H2 한 대)

### Windows 버전

| Windows | 글자 파일 세 개 | 근거 |
|---|---|---|
| Windows 11 21H2 | 없음 | AboutDFIR 글 |
| Windows 11 22H2 | 처음 보임. 글쓴이는 2022년 11월 빌드에서 처음 보았고, Pro 22H2 (빌드 22621.963) 가상 머신과 Process Monitor 로 조사했습니다 | AboutDFIR 글 |
| Windows 11 25H2 Home (빌드 26200) | 세 파일 모두 있음 | 관찰 (확인 범위: Win11 25H2 한 대) |

출처 글 제목에는 "Pro" 가 들어 있지만 관찰한 PC 는 Home 판이었는데도 세 파일이 있었습니다. Windows 10 과 서버 판에 이 파일이 있는지는 확인하지 못했습니다.

### 레지스트리

`AppCompatFlags` 키는 NTUSER.DAT 와 SOFTWARE 하이브 두 곳에서 보며, SOFTWARE 하이브는 `Wow6432Node` 아래도 봅니다. NTUSER.DAT 안의 경로는 `Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags` 입니다.

| 하위 키 | 담는 것 |
|---|---|
| `Layers` | 호환 모드 설정입니다. 값 데이터 예: `ELEVATECREATEPROCESS`, `RUNASADMIN`, `WINXPSP2 RUNASADMIN` |
| `Compatibility Assistant\Store` | 값 이름이 실행 파일 경로입니다 |
| `Compatibility Assistant\Persisted` | RegRipper 플러그인이 읽는 키입니다. 관찰한 PC 에는 없었습니다 (확인 범위: Win11 25H2 한 대) |
| `Custom`, `InstalledSDB` | RegRipper 플러그인이 읽는 키입니다. 담는 내용은 이번 자료로 확인하지 못했습니다 |

하이브를 수집하고 여는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 를 따릅니다.

## 구조

### PcaAppLaunchDic.txt

- 한 줄 모양은 `경로|시각` 입니다.
- AboutDFIR 글의 예 (프로그램 이름은 가림): `C:\Program Files\(프로그램)\(프로그램).exe|2022-12-28 16:06:24.212`

아래는 관찰입니다. (확인 범위: Win11 25H2 한 대)

- 0x7F 를 넘는 바이트가 하나도 없었습니다.
- 95줄이 모두 서로 다른 경로였습니다. 경로 하나에 한 줄입니다.
- 줄 순서는 시각 순서가 아니었습니다.
- 마지막 줄은 한글이 든 경로였는데, 한글 바로 앞에서 끊기고 시각이 없었습니다.
- 같은 프로그램이 `PcaGeneralDb0.txt` 에는 한글 경로까지 온전히 남아 있었습니다.

### PcaGeneralDb0.txt

칸 순서는 AboutDFIR 글을 따랐습니다. "관찰한 값" 칸은 관찰입니다. (확인 범위: Win11 25H2 한 대)

| 순서 | 칸 | 관찰한 값 |
|---|---|---|
| 1 | 실행 시각 | `YYYY-MM-DD HH:MM:SS.mmm` 모양 글자 |
| 2 | 실행 상태 (숫자) | 0, 2, 3 이 나왔고 1 은 없었습니다 |
| 3 | 실행 파일 경로 | 환경 변수로 줄인 경로 |
| 4 | 파일 설명 | 소문자로 적혔습니다 (예: `windows installer - unicode`) |
| 5 | 제조사 | 소문자로 적혔습니다 (예: `microsoft corporation`) |
| 6 | 파일 버전 | |
| 7 | ProgramId | 16진 44자이고 `0000` 으로 시작했습니다. 빈 줄도 있었습니다 (40줄) |
| 8 | 종료 코드 | 코드 숫자가 아니라 문장이 들어 있었습니다 |

- AboutDFIR 글의 예 (앱 폴더 이름은 가림): `2022-05-12 21:32:42.556|2|%USERPROFILE%\appdata\local\(앱)\...\git\cmd\git.exe|git|...`

아래는 관찰입니다. (확인 범위: Win11 25H2 한 대)

- 2,174줄이 모두 칸 8개였습니다.
- 경로는 `%programfiles%`, `%programfiles(x86)%`, `%USERPROFILE%`, `%systemroot%` 같은 환경 변수로 줄여 적혔습니다.
- 환경 변수로 줄일 수 없는 경로는 드라이브 문자 없이 `\` 로 시작했습니다.
- 2번 칸 값과 8번 칸 문장은 아래처럼 짝을 이뤘습니다.

| 2번 칸 | 8번 칸 문장 | 줄 수 |
|---|---|---|
| 0 | `Installer failed` | 29 |
| 2 | `Abnormal process exit with code 0x…` | 2,052 |
| 3 | `PCA resolve is called, resolver name: …, result: …` | 93 |

- 2번 칸이 3 인 줄의 resolver name 으로 `DetectorShim_KernelDriver`, `DetectorShim_ShortRunTime`, `DetectorShim_MessageBoxErrorIcon`, `UninstallFailure` 가 나왔습니다.
- 같은 프로그램이 여러 번 나왔습니다. 한 프로그램이 한 시간마다 비정상 종료하면서 2,174줄 가운데 1,850줄을 차지했습니다.
- 줄 순서는 시각 순서가 아니었습니다.

### PcaGeneralDb1.txt

관찰한 PC 에서는 0바이트였습니다. (확인 범위: Win11 25H2 한 대) `PcaGeneralDb0.txt` 와 번갈아 쓰이는지는 확인하지 못했으며, 크기가 0 이 아니면 같은 방법으로 읽어 봅니다.

### 레지스트리 `Compatibility Assistant\Store`

- 값 이름이 실행 파일 경로입니다.
- RegRipper 의 `appcompatflags` 플러그인은 값 데이터의 오프셋 0x2C 에서 8바이트 시각을 읽습니다.

아래는 관찰입니다. (확인 범위: Win11 25H2 한 대)

- 사용자 하이브의 Store 키에 값이 183개 있었습니다.
- 값 이름은 모두 드라이브 문자로 시작하는 경로였습니다.
- 값 데이터는 REG_BINARY 이고 길이는 60~224바이트였습니다. 모두 `53 41 43 50` ("SACP") 로 시작했습니다.
- 183개 값의 0x2C 시각이 모두 같은 값 하나였습니다. 그 값은 OS 설치 당일이었습니다.
- OS 설치 뒤에 처음 실행한 프로그램의 값도 같은 시각이었습니다.
- Store 키의 마지막 기록 시각 (Last Write Time) 은 `PcaGeneralDb0.txt` 의 마지막 수정 시각과 초 단위까지 같았습니다.

## 증거로서 의미

### 증명하는 것

- `PcaAppLaunchDic.txt` 의 한 줄은 그 경로의 파일이 이 시스템에서 실행된 기록입니다. 적힌 시각은 AboutDFIR 글이 마지막 실행 시각으로 본 값입니다.
- `PcaGeneralDb0.txt` 의 한 줄은 그 시각에 그 경로의 프로그램에 대해 8번 칸의 사건이 기록됐다는 뜻입니다. 1번 칸은 AboutDFIR 글이 실행 시각이라고 부른 값입니다.
- 4~6번 칸에는 파일 설명·제조사·버전이 함께 있습니다. 경로만으로 알기 어려운 프로그램을 가늠할 때 씁니다.
- `Compatibility Assistant\Store` 는 사용자 하이브에도 있습니다. 어느 사용자의 NTUSER.DAT 에 값이 있는지로 사용자를 좁힐 수 있습니다.

### 증명하지 못하는 것

- 모든 실행이 남지 않습니다. 관찰한 PC 에서 터미널로 자주 실행한 `git.exe`·`python.exe`·`cmd.exe`·`powershell.exe` 는 `PcaAppLaunchDic.txt` 에 없었습니다. 반면 `dotnet.exe`·`wsl.exe`·`msiexec.exe` 는 있었습니다. (확인 범위: Win11 25H2 한 대)
- 어떤 실행이 남는지는 AboutDFIR 글도 "더 조사해야 한다" 고 적었습니다. "탐색기에서 연 것만 남는다" 는 주장은 확인하지 못했습니다.
- `PcaAppLaunchDic.txt` 는 경로 하나에 한 줄입니다. 실행 횟수와 그 전의 실행 시각은 알 수 없습니다.
- 누가 실행했는지는 알 수 없습니다. 글자 파일은 시스템에 한 벌만 있고, 사용자를 적는 칸이 없습니다. `%USERPROFILE%` 로 줄인 경로도 어느 사용자 폴더인지 알려 주지 않습니다.
- 비정상 종료의 원인과 프로그램이 악성인지는 알 수 없습니다.
- Store 값의 0x2C 시각을 프로그램별 실행 시각으로 읽으면 틀릴 수 있습니다. 관찰한 PC 에서는 모든 값이 같은 시각이었습니다. (확인 범위: Win11 25H2 한 대)

보고서에는 "그 프로그램을 실행했다" 대신 "`PcaAppLaunchDic.txt` 에 경로 X 와 시각 A 가 적힌 줄이 있다. 이 시각은 파일의 마지막 수정 시각과 견주어 UTC 로 판단했다" 처럼 씁니다.

## 시각 해석

두 파일의 시각은 `YYYY-MM-DD HH:MM:SS.mmm` 모양 글자인데, AboutDFIR 글은 이 시각이 UTC 인지 현지 시각인지 밝히지 않았습니다.

- 관찰한 PC 에서는 두 파일 모두 가장 늦은 줄의 시각이 파일의 마지막 수정 시각 (UTC) 과 같았습니다. 시각은 UTC 로 보입니다. (확인 범위: Win11 25H2 한 대)
- 검체마다 같은 방법으로 확인합니다. 가장 늦은 줄의 시각을 [마스터 파일 테이블](../filesystem/mft.md) 의 수정 시각과 견줍니다.
- 줄 순서는 시각 순서가 아닙니다. 시각 칸으로 정렬한 뒤 읽습니다.
- Store 키의 마지막 기록 시각은 UTC 입니다. 이 시각이 `PcaGeneralDb0.txt` 의 마지막 수정 시각과 맞는지 봅니다. 관찰한 PC 에서는 초 단위까지 같았습니다. (확인 범위: Win11 25H2 한 대)
- 세 파일을 만든 시각은 관찰한 PC 에서 모두 OS 설치 당일이었습니다. 파일을 만든 시각은 어느 프로그램의 첫 실행 시각도 알려 주지 않습니다. (확인 범위: Win11 25H2 한 대)
- 여러 기록을 한 시간 축에 놓는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 을 따릅니다.

## 함정과 한계

- **줄이 없다고 실행하지 않았다고 쓰지 않습니다.** 모든 실행이 남지 않습니다. 다른 실행 흔적과 함께 봅니다.
- **두 파일의 인코딩이 다릅니다.** `PcaGeneralDb0.txt` 는 BOM 이 없는 UTF-16 LE 입니다. 편집기나 도구가 이를 알아보지 못하면 글자 사이에 빈 바이트가 끼어 보입니다. 인코딩을 고르는 법은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에 있습니다.
- **비 ASCII 경로가 잘립니다.** 관찰한 PC 의 `PcaAppLaunchDic.txt` 에서 한글 경로가 잘렸습니다. 같은 프로그램을 `PcaGeneralDb0.txt` 에서 찾아 온전한 경로를 봅니다. (확인 범위: Win11 25H2 한 대)
- **반복 줄에 묻히지 않습니다.** 한 프로그램의 반복 오류가 줄 대부분을 차지할 수 있습니다. 경로별로 묶어 센 뒤 드문 줄부터 봅니다.
- **8번 칸 이름에 매이지 않습니다.** 출처는 종료 코드라고 불렀지만 관찰한 PC 에서는 문장이 들어 있었습니다. 문장 그대로 보고서에 옮깁니다.
- **Store 값의 0x2C 시각을 믿기 전에 확인합니다.** 도구가 이 값을 실행 시각처럼 보여 줄 수 있습니다. 값들이 한 시각으로 몰려 있는지 먼저 봅니다.
- **글자 파일은 고치기 쉽습니다.** 줄을 지우거나 바꿔도 형식이 깨지지 않습니다. 가장 늦은 줄의 시각, 파일 수정 시각, Store 키의 마지막 기록 시각이 서로 맞는지 봅니다. 섀도 복사본 속 옛 파일과 견주고, [USN 변경 저널](../filesystem/usnjrnl.md) 에서 파일이 바뀐 기록을 찾습니다. [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 을 참고합니다.
- **세 파일을 모두 수집합니다.** `PcaGeneralDb1.txt` 가 언제 쓰이는지 모릅니다. 0바이트라도 크기와 시각을 적어 둡니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 두 예시는 위 줄 형식과 관찰한 인코딩으로 만든 것입니다. 특정 검체에서 나온 값이 아닙니다.

`PcaGeneralDb0.txt` 한 줄의 앞부분입니다 (UTF-16 LE).

```
32 00 30 00 32 00 34 00 2D 00 30 00 33 00 2D 00   2.0.2.4.-.0.3.-.
31 00 35 00 20 00 30 00 39 00 3A 00 33 00 30 00   1.5. .0.9.:.3.0.
3A 00 30 00 30 00 2E 00 30 00 30 00 30 00 7C 00   :.0.0...0.0.0.|.
32 00 7C 00                                       2.|.
```

- 글자마다 2바이트입니다. `7C 00` 은 칸을 나누는 `|` 입니다.
- 1번 칸은 `2024-03-15 09:30:00.000`, 2번 칸은 `2` 입니다.
- BOM (`FF FE`) 이 없어서 파일 첫 바이트가 바로 첫 글자입니다.
- 줄 끝은 `0A 00` 하나입니다. `0D 00` 이 앞에 오지 않습니다.

`PcaAppLaunchDic.txt` 한 줄입니다 (1바이트 문자).

```
43 3A 5C 61 70 70 2E 65 78 65 7C 32 30 32 34 2D   C:\app.exe|2024-
30 33 2D 31 35 20 30 39 3A 33 30 3A 30 30 2E 30   03-15 09:30:00.0
30 30 0D 0A                                       00..
```

- 경로 `C:\app.exe` 뒤에 `7C` (`|`) 가 오고, 그 뒤가 시각입니다.
- 줄 끝은 `0D 0A` 입니다.

Store 값 데이터는 아래 두 곳만 봅니다.

```
오프셋 0x00  53 41 43 50                 "SACP" (관찰한 값은 모두 이렇게 시작)
오프셋 0x2C  (8바이트)                    RegRipper 가 시각으로 읽는 자리
```

### 공개 도구로 한 번

세 파일을 사본으로 뜬 뒤 Windows PowerShell 5.1 에서 읽습니다.

```powershell
$cols = 'Time','Status','Path','Description','Vendor','Version','ProgramId','Message'
Import-Csv .\PcaGeneralDb0.txt -Delimiter '|' -Header $cols -Encoding Unicode |
  Sort-Object Time |
  Export-Csv .\PcaGeneralDb0_sorted.csv -NoTypeInformation -Encoding UTF8

Import-Csv .\PcaGeneralDb0.txt -Delimiter '|' -Header $cols -Encoding Unicode |
  Group-Object Path | Sort-Object Count -Descending |
  Select-Object Count, Name

Import-Csv .\PcaAppLaunchDic.txt -Delimiter '|' -Header 'Path','Time' |
  Sort-Object Time
```

- `-Encoding Unicode` 는 UTF-16 LE 로 읽으라는 뜻입니다.
- 시각이 `YYYY-MM-DD` 로 시작하므로 글자 순서로 정렬해도 시간 순서가 됩니다.
- 두 번째 명령은 경로별 줄 수를 셉니다. 반복 줄을 걸러 낼 때 씁니다.
- 결과 줄 수를 원본 줄 수와 맞춰 봅니다. 칸 안에 큰따옴표가 있으면 칸이 잘못 나뉠 수 있습니다.

레지스트리는 RegRipper 로 봅니다. 사용자 하이브와 SOFTWARE 하이브를 따로 넣습니다.

```
rip.exe -r NTUSER.DAT -p appcompatflags
rip.exe -r SOFTWARE -p appcompatflags
```

- 출력의 Store 시각은 위 "함정과 한계" 의 확인을 거친 뒤에 씁니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 심캐시 | 같은 경로가 실행 파일 목록에 있는지 | [심캐시](shimcache-appcompatcache.md) |
| AmCache | 같은 경로의 파일 정보 | [AmCache](amcache-hve/index.md) |
| 프리페치 | 실행 횟수와 실행 시각 | [프리페치](prefetch/index.md) |
| BAM·DAM | 사용자별 마지막 실행 시각 | [BAM·DAM](background-activity-moderator.md) |
| 윈도 오류 보고 | `Abnormal process exit` 줄과 같은 사건의 보고서·이벤트 | [윈도 오류 보고](wer.md) |
| 프로그램 설치·삭제 이벤트 | `Installer failed` 줄 무렵의 설치 시도 | [프로그램 설치·삭제 이벤트](../event-logs/msiinstaller.md) |

실행 흔적 전체를 엮는 흐름은 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md) 에 있습니다.

## 실습

공개 검체(NIST CFReDS 등) 가운데 Windows 11 22H2 이후 이미지를 고릅니다. 맞는 버전이 없으면 직접 만든 가상 머신으로 풀어 봅니다.

1. `C:\Windows\appcompat\pca\` 에 파일 세 개가 모두 있습니까? 각 파일의 크기와 인코딩은 무엇입니까?
2. `PcaAppLaunchDic.txt` 에서 가장 늦은 줄의 시각과 파일의 마지막 수정 시각을 견줍니다. 시각은 UTC 입니까?
3. `PcaGeneralDb0.txt` 의 줄을 2번 칸 값별로 셉니다. 가장 많은 사건은 무엇이고, 한 프로그램이 대부분을 차지합니까?
4. `PcaAppLaunchDic.txt` 의 프로그램 하나를 골라 프리페치·AmCache·심캐시에서도 찾아봅니다. 반대로 프리페치에는 있는데 PCA 파일에 없는 프로그램은 무엇입니까?
5. 사용자 하이브의 Store 값에서 0x2C 시각을 모두 뽑습니다. 값마다 다릅니까, 한 시각으로 몰려 있습니까?

## 참고 문헌

1. Andrew Rathbun, Lucas Gonzalez, *New Windows 11 Pro (22H2) Evidence of Execution Artifact* (AboutDFIR, 2023-01-03 — 파일 위치, 처음 보인 버전, 두 파일의 줄 형식과 칸 순서, 조사 환경). https://aboutdfir.com/new-windows-11-pro-22h2-evidence-of-execution-artifact/
2. H. Carvey 외, *appcompatflags.pl* (RegRipper 3.0 플러그인 — `AppCompatFlags` 하위 키, 두 하이브와 `Wow6432Node`, Store 값의 0x2C 시각, `Layers` 값 예). https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/appcompatflags.pl
