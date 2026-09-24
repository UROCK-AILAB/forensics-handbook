# 구버전 실행 기록 (RecentFileCache.bcf)

> 위치: [AmCache (Amcache.hve)](/02-artifacts/execution/amcache-hve/index.md) > 구버전 실행 기록

## 한 줄 요약

RecentFileCache.bcf 는 Windows 7 과 Windows Server 2008 R2 에서 Amcache.hve 보다 먼저 쓰던 파일입니다. 호환성 보정이 필요한 실행 파일의 경로를 소문자로 모아 둡니다. 파일 안에는 시각이 하나도 없습니다. 매일 밤 예약 작업이 이 파일을 비웁니다. 그래서 남아 있는 경로는 마지막으로 비운 뒤에 실행된 파일을 가리킵니다.

## 무엇을 기록하나 · 왜 생기나

Windows 에는 오래된 프로그램이 새 Windows 에서도 돌도록 호환성 보정(심, Shim)을 거는 장치가 있습니다. Windows 7 에서는 Application Experience 서비스가 이 일의 일부를 맡습니다. 서비스 이름은 `AeLookupSvc` 입니다. 이 서비스는 `svchost.exe -k netsvcs` 안에서 돕니다.

- 실행 파일(PE)이 뜰 때 이 서비스는 그 파일에 호환성 보정이 필요한지 확인합니다.
- 필요하면 그 파일의 경로를 RecentFileCache.bcf 에 적습니다.
- 실행 파일이 쓰는 의존 파일 가운데 호환성 보정이 필요한 것도 적습니다. (여기까지 ANSSI, 2019)

실제로는 시스템에 새로 들어온 실행 파일이 주로 남습니다. Harrell 은 같은 프로그램을 여러 방식으로 실행해 비교했습니다(2013).

| 실행 방식 | 기록 |
|---|---|
| 다른 곳에서 복사해 온 뒤 실행 | 남음 |
| 웹 브라우저로 내려받은 뒤 실행 | 남음 |
| 설치 파일에서 풀려 나온 뒤 실행 | 남음 |
| 원래 시스템에 있던 프로그램을 실행 | 안 남음 |
| 원래 있던 프로그램의 이름만 바꿔 실행 | 안 남음 |

이 목록은 오래 가지 않습니다. 예약 작업 (Scheduled Task) `ProgramDataUpdater` 가 매일 0시 30분에 돌게 잡혀 있습니다. 이 작업은 `%windir%\system32\rundll32.exe aepdu.dll,AePduRunUpdate` 를 실행합니다. 이때 RecentFileCache.bcf 를 비웁니다. 설치된 프로그램 목록은 같은 폴더의 `AEINV_PREVIOUS.xml` 에 씁니다. 이 작업은 컴퓨터가 3분 이상 쉬고 있을 때만 돕니다. 조건이 안 맞거나 컴퓨터가 꺼져 있으면 다음 23시간 동안 다시 시도합니다. (ANSSI, 2019)

## 위치와 버전별 차이

| 항목 | 내용 |
|---|---|
| 경로 | `%WinDir%\AppCompat\Programs\RecentFileCache.bcf` (보통 `C:\Windows\AppCompat\Programs\`) |
| 범위 | 컴퓨터 전체에 파일 하나입니다. 사용자별 파일이 아닙니다 |
| 쓰는 주체 | Application Experience 서비스(`AeLookupSvc`) |
| 비우는 주체 | 예약 작업 `ProgramDataUpdater` |
| 시각 | 파일 안에는 없습니다 |

이 파일을 쓰는지는 Windows 버전보다 호환성 라이브러리(`%WinDir%\System32` 의 `ae` 로 시작하는 DLL) 버전을 따릅니다. 라이브러리 버전과 Amcache 형식의 관계는 [구조와 버전별 차이](/02-artifacts/execution/amcache-hve/structure-versions.md)에서 다룹니다. 이 파일에 필요한 부분만 추리면 다음과 같습니다.

| 환경 | RecentFileCache.bcf | Amcache.hve | 근거 |
|---|---|---|---|
| Windows 7 SP0·SP1, Server 2008 R2 (처음 실린 라이브러리 6.1.7600·6.1.7601) | 씁니다 | 없습니다 | ANSSI |
| KB2952664 를 받은 Windows 7 | 남아서 계속 갱신될 수 있습니다 | 생깁니다 | Khatri, ANSSI |
| Windows 8·Server 2012 이후 (라이브러리 6.2 이후) | 없습니다 | 씁니다 | ANSSI |

- KB2952664 는 2015년 4월에 나왔습니다. 자동 배포로 널리 퍼진 때는 그해 10월 무렵입니다 (Khatri, 2016).
- Khatri 는 이 업데이트를 받은 Windows 7 에서 두 파일이 함께 갱신되는 것을 확인했습니다. 같은 실행 파일에 대해 Amcache.hve 쪽 정보가 훨씬 많았습니다.
- ANSSI 는 라이브러리 버전이 운영체제 버전보다 낮은 경우를 보지 못했다고 적었습니다. 그래서 Windows 10 에는 이 파일이 없다고 봅니다.
- Windows Vista 이하에서 이 파일을 다룬 자료는 찾지 못했습니다.

## 구조

파일은 20바이트 머리와 경로 항목의 나열로 되어 있습니다. 숫자는 리틀 엔디언입니다. 머리에 항목 개수 칸이 없습니다. 그래서 파일 끝까지 항목을 읽습니다.

### 파일 머리

| 오프셋 | 크기 | 값 | 뜻 |
|---|---|---|---|
| 0x00 | 4 | 바이트 `FE FF EE FF` | 서명 |
| 0x04 | 4 | 0x00002211 | 알 수 없음 |
| 0x08 | 4 | 3 | 알 수 없음 |
| 0x0C | 4 | 1 | 알 수 없음 |
| 0x10 | 4 | — | 알 수 없음. libyal 명세는 체크섬으로 봅니다 |

- ANSSI 는 앞 16바이트가 늘 같다고 적었습니다.
- 자료마다 서명 숫자를 적는 방식이 다릅니다. 파일 첫 4바이트를 그대로 보면 `FE FF EE FF` 입니다. 이 바이트를 32비트 리틀 엔디언으로 읽으면 0xFFEEFFFE 입니다.
- 0x10 의 값을 어떻게 계산하는지 밝힌 자료는 찾지 못했습니다.

### 경로 항목

| 오프셋(항목 안) | 크기 | 뜻 |
|---|---|---|
| 0 | 4 | 경로의 글자 수 |
| 4 | 글자 수 × 2 | 경로, UTF-16LE |
| 4 + 글자 수 × 2 | 2 | 문자열 끝 표시 `00 00` |

- 첫 항목은 0x14 에서 시작합니다.
- 경로는 소문자로 적힙니다 (ANSSI).
- UTF-16LE 를 읽는 법은 [문자 인코딩](/01-foundations/value-decoding/utf-16le-utf-8-cp949.md)에 있습니다.

글자 수에 끝 표시가 들어가는지는 자료마다 다릅니다. libyal 명세는 들어간다고 적었습니다. ANSSI 는 들어가지 않는다고 적었습니다. 공개 파서 한 곳의 코드도 끝 표시를 빼고 셉니다. 이 코드는 글자 수 × 2 바이트를 읽은 뒤 2바이트를 더 건너뜁니다. 검체에서 직접 가리려면 글자 수 × 2 바이트 뒤를 봅니다. 거기에 `00 00` 이 있고, 그다음 4바이트가 다음 항목의 글자 수로 읽히면 끝 표시를 빼고 센 것입니다.

## 증거로서 의미

### 증명하는 것

- 적힌 경로의 실행 파일이 마지막 `ProgramDataUpdater` 실행 뒤 어느 때에 실행된 흔적입니다. ANSSI 는 이 구간에 "처음" 실행된 것으로 해석합니다.
- 적힌 파일은 대개 최근에 시스템에 들어온 파일입니다 (Harrell).
- 사용자가 직접 띄우지 않은 파일도 남습니다. ANSSI 실험에서는 프로그램을 설치하는 동안 딸려 실행된 `vcredist_x86.exe`·`msiexec.exe`·`wusa.exe` 경로가 남았습니다.

### 증명하지 못하는 것

- 실행 시각을 알려 주지 않습니다. 파일 안에 시각 칸이 없습니다.
- 누가 실행했는지 알려 주지 않습니다. 컴퓨터 전체에 파일이 하나이고 사용자 칸이 없습니다.
- 실행 횟수를 알려 주지 않습니다.
- 실행 파일의 내용을 알려 주지 않습니다. 해시와 크기가 없어서 같은 경로의 다른 파일과 구별하지 못합니다.
- 목록 순서가 실행 순서라고 볼 수 없습니다. ANSSI 실험에서 마지막 경로가 늘 마지막에 실행한 파일은 아니었습니다.
- 경로가 없다고 해서 실행하지 않았다고 볼 수 없습니다. 이유는 아래 "함정과 한계" 에 있습니다.

보고서에는 기록이 말하는 만큼만 씁니다. 예를 들면 "RecentFileCache.bcf 에 이 경로가 적혀 있다. 이 파일은 예약 작업이 매일 비우므로, 이 경로의 실행 파일이 마지막 비움 작업 뒤부터 수집 시점 사이에 실행된 흔적으로 본다" 처럼 씁니다. 실행 시각은 다른 아티팩트로 따로 밝힙니다.

## 시각 해석

파일 안에 시각이 없으므로 시각은 모두 파일 밖에서 구합니다.

| 알고 싶은 것 | 볼 곳 | 확인 수준 |
|---|---|---|
| 구간의 시작(마지막 비움) | 작업 스케줄러 로그에 남은 `ProgramDataUpdater` 실행 기록. [예약 작업 이벤트](/02-artifacts/event-logs/taskscheduler-4698.md) 참고 | 작업이 파일을 비운다는 점은 확인된 사실입니다. 로그가 남아 있어야 쓸 수 있습니다 |
| 구간의 시작(보조) | `AEINV_PREVIOUS.xml` 의 NTFS 시각 | 추정입니다. 작업이 돌 때마다 이 파일을 새로 만들어 이름을 바꾸므로 실마리가 될 수 있습니다. 검증한 자료는 찾지 못했습니다 |
| 구간의 끝 | 수집 시각 또는 이미지 확보 시각 | — |
| 마지막으로 쓴 때 | RecentFileCache.bcf 자체의 NTFS 수정 시각 | 추정입니다. 항목이 붙거나 파일이 비워질 때 바뀔 것으로 봅니다 |
| 항목이 붙은 때 | [$UsnJrnl](/02-artifacts/filesystem/usnjrnl.md) 에 남은 이 파일의 변경 기록 | 추정입니다. 기록이 남아 있으면 쓰인 시각을 좁힐 수 있습니다. 검증한 자료는 찾지 못했습니다 |

- NTFS 시각은 UTC 입니다. $STANDARD_INFORMATION 과 $FILE_NAME 의 차이는 [두 벌의 시각](/01-foundations/disk-volume/ntfs/standard-information-file-name.md)에서 다룹니다.
- 0시 30분이 어느 시간대 기준인지는 작업 정의에서 확인합니다. 작업 정의 파일은 [작업 정의 파일](/02-artifacts/persistence/scheduled-tasks/system32-tasks-xml.md)에서 다룹니다.
- 컴퓨터가 꺼져 있었거나 쉬지 않았으면 작업이 밀립니다. 그러면 구간이 하루보다 길어질 수 있습니다.

## 함정과 한계

1. **모든 실행을 적지 않습니다.** ANSSI 실험 결과는 다음과 같습니다.
   - 설치를 시작한 실행 파일 자체는 남지 않았습니다.
   - USB 드라이브와 네트워크 공유에서 실행한 파일은 남지 않았습니다. 로컬 드라이브에서 실행하면 남는 파일도 그랬습니다.
   - 같은 파일도 놓인 폴더에 따라 달랐습니다. `C:\Users\<사용자>\Documents\test` 에서는 남았고, `C:\Users\<사용자>\Documents` 에서는 남지 않았습니다.
   - 사용자 폴더의 파일은 생긴 직후 실행하면 남았습니다. 몇 시간 기다렸다 실행하면 남지 않았습니다.
2. **관찰끼리 어긋나는 부분이 있습니다.** Harrell 은 실제 사건 검체에서 이동식 매체에서 실행한 파일이 적힌 경우를 봤다고 적었습니다. 실행하지 않은 파일이 적힌 경우도 봤다고 적었습니다. 두 경우 모두 실험으로 재현하지는 못했습니다. 그래서 이 파일 하나로 "실행했다" 나 "실행하지 않았다" 를 단정하지 않습니다.
3. **목록이 짧게 삽니다.** 작업이 매일 파일을 비우므로 수집이 늦으면 찾는 경로가 이미 사라졌을 수 있습니다. 빈 파일은 정상 상태일 수 있습니다. 빈 파일만으로 누가 지웠다고 보지 않습니다.
4. **대소문자를 잃습니다.** 경로가 소문자로 적히므로 원래 파일 이름의 대소문자는 알 수 없습니다.
5. **비워진 정보가 다른 파일로 옮겨 갈 수 있습니다.** 일부 시스템에서는 작업이 `AEINV_WER_{MachineId}_YYYYMMDD_HHmmss.xml` 도 씁니다. 이 파일의 Orphan 목록에는 RecentFileCache.bcf 에 있던 실행 파일 가운데 어느 프로그램에도 속하지 않는 것이 남습니다. 여기에는 SHA-1 과 파일의 만든 시각·수정 시각이 들어갑니다. 다만 한 경로에 대해 첫 실행 뒤 한 번만 적습니다. 그래서 같은 경로의 파일을 나중에 바꿔치기하면 갱신되지 않습니다. (ANSSI, 2019)
6. **예전 판이 섀도 복사본에 있을 수 있습니다.** Windows 7 은 볼륨 섀도 복사본을 만듭니다. 섀도 복사본 안의 예전 RecentFileCache.bcf 에는 이미 비워진 경로가 남아 있을 수 있습니다. 방법은 [섀도 복사본 활용](/03-techniques/analysis/volume-shadow-copy-analysis.md)에서 다룹니다.
7. **파일이 지워졌을 수 있습니다.** 파일이 아예 없으면 [$MFT](/02-artifacts/filesystem/mft.md) 와 [$UsnJrnl](/02-artifacts/filesystem/usnjrnl.md) 에서 이 파일의 삭제 흔적을 찾아봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시입니다. 실제 검체에서 나온 값이 아닙니다. 경로 `c:\t.exe` 하나만 든 파일입니다. 0x10~0x13 은 값을 알 수 없어서 `??` 로 두었습니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00   FE FF EE FF 11 22 00 00 03 00 00 00 01 00 00 00
0x10   ?? ?? ?? ?? 08 00 00 00 63 00 3A 00 5C 00 74 00
0x20   2E 00 65 00 78 00 65 00 00 00
```

1. 0x00~0x0F 가 `FE FF EE FF 11 22 00 00 03 00 00 00 01 00 00 00` 인지 봅니다.
2. 0x10~0x13 은 뜻을 모르는 값이라 건너뜁니다.
3. 0x14 의 `08 00 00 00` 은 글자 수 8 입니다.
4. 0x18 부터 16바이트(8 × 2)를 UTF-16LE 로 읽습니다. `c` `:` `\` `t` `.` `e` `x` `e` 입니다.
5. 0x28 의 `00 00` 은 끝 표시입니다.
6. 다음 항목은 0x2A 에서 시작합니다. 파일 끝까지 3~5 를 되풀이합니다.

### 공개 도구로 한 번

공개 도구의 예로 Eric Zimmerman 의 RecentFileCacheParser 가 있습니다. 이 도구는 서명을 확인한 뒤 0x14 부터 항목을 읽습니다. Velociraptor 의 `Windows.Forensics.RecentFileCache` 수집 규칙은 머리를 해석하지 않습니다. 이 규칙은 정규식으로 `드라이브 문자:` 로 시작하는 UTF-16 문자열을 찾습니다. 이 규칙의 설명은 항목 순서를 실행 흐름으로 봅니다. ANSSI 실험 결과와는 맞지 않으므로 순서는 참고로만 씁니다.

읽는 방식이 서로 다르므로 두 가지 이상으로 읽고 항목 수를 맞춰 봅니다. 차이가 나면 헥스로 돌아가 확인합니다. 방법은 [도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md)에서 다룹니다.

## 교차 검증 — 함께 볼 아티팩트

| 아티팩트 | 맞춰 볼 점 |
|---|---|
| [심캐시 (ShimCache·AppCompatCache)](/02-artifacts/execution/shimcache-appcompatcache.md) | 같은 호환성 장치의 다른 기록입니다. 더 오래 남습니다 |
| [프리페치 (Prefetch)](/02-artifacts/execution/prefetch/index.md) | 실행 횟수와 마지막 실행 시각(Windows 7 은 1개)을 줍니다 |
| [실행 파일 항목 (InventoryApplicationFile)](/02-artifacts/execution/amcache-hve/inventoryapplicationfile.md) | KB2952664 를 받은 Windows 7 이면 같은 파일의 SHA-1 등을 줍니다. 옛 형식 키는 [구조와 버전별 차이](/02-artifacts/execution/amcache-hve/structure-versions.md)에서 봅니다 |
| [UserAssist](/02-artifacts/execution/userassist.md) | 탐색기로 띄운 프로그램을 사용자별로 줍니다 |
| [마스터 파일 테이블 ($MFT)](/02-artifacts/filesystem/mft.md) | 실행 파일이 언제 생겼는지 봅니다. 새로 들어온 파일인지 가릴 수 있습니다 |
| [다운로드 출처 표시 (Zone.Identifier)](/02-artifacts/filesystem/zone-identifier.md) | 내려받은 파일이면 출처를 봅니다 |
| [USN 변경 저널 ($UsnJrnl)](/02-artifacts/filesystem/usnjrnl.md) | 실행 파일이 생긴 때와 이 파일이 바뀐 때를 봅니다 |
| [예약 작업 이벤트 (TaskScheduler·4698)](/02-artifacts/event-logs/taskscheduler-4698.md) | `ProgramDataUpdater` 가 언제 돌았는지 봅니다 |
| [윈도 업데이트 기록 (Windows Update·CBS Log)](/02-artifacts/system-account/windows-update-cbs-log.md) | KB2952664 를 언제 받았는지 봅니다 |

조사 전체 흐름은 [어떤 프로그램을 언제 실행했나](/04-scenarios/activity/program-execution.md)에서 다룹니다.

## 실습

NIST CFReDS 의 "Data Leakage Case" PC 이미지는 Windows 7 Ultimate SP1 (64비트) 입니다. 이 이미지로 아래 질문을 풀어 봅니다.

1. RecentFileCache.bcf 의 앞 16바이트가 명세 값과 같습니까?
2. 첫 항목의 글자 수 칸에 끝 표시가 들어갑니까? 글자 수 × 2 바이트 뒤를 확인합니다.
3. 적힌 경로 가운데 사용자 폴더에 있는 것은 무엇입니까? 그 실행 파일의 $MFT 생성 시각은 언제입니까?
4. 같은 경로가 심캐시·프리페치·UserAssist 에도 있습니까? 한쪽에만 있다면 이유를 설명할 수 있습니까?
5. `AEINV_PREVIOUS.xml` 의 NTFS 시각과 작업 스케줄러 로그로 마지막 비움 시각을 추정할 수 있습니까? 둘이 맞습니까?
6. 섀도 복사본이 있다면, 그 안의 RecentFileCache.bcf 는 지금 판과 무엇이 다릅니까?
7. 같은 폴더에 Amcache.hve 가 있습니까? 있다면 두 파일에 함께 적힌 경로를 비교합니다.

## 참고 문헌

- Joachim Metz, "Recent file cache (RecentFileCache.bcf) file format", libyal dtformats — https://github.com/libyal/dtformats/blob/main/documentation/RecentFileCache.bcf%20format.asciidoc
- Blanche Lagny, "Analysis of the AmCache v2", ANSSI (2019) — https://cyber.gouv.fr/documents/632/anssi-coriin_2019-analysis_amcache-v2.pdf
- Corey Harrell, "Revealing the RecentFileCache.bcf File", Journey Into Incident Response (2013) — http://journeyintoir.blogspot.com/2013/12/revealing-recentfilecachebcf-file.html
- Yogesh Khatri, "Amcache on Windows 7", Swift Forensics (2016) — http://www.swiftforensics.com/2016/05/amcache-on-windows-7.html
- Eric Zimmerman, RecentFileCacheParser 소스 코드 `RecentFileCacheFile.cs` — https://github.com/EricZimmerman/RecentFileCacheParser/blob/master/RecentFileCache/RecentFileCacheFile.cs
- Velociraptor Artifact Exchange, "Windows.Forensics.RecentFileCache" — https://docs.velociraptor.app/exchange/artifacts/pages/windows.forensics.recentfilecache/
