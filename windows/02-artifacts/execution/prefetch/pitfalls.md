---
title: "프리페치 해석 함정"
parent: "프리페치"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 840
---

# 프리페치 해석 함정 (꺼진 경우·보관 개수 한도·첫 실행 시각)

## 한 줄 요약

.pf 파일이 없다고 해서 실행하지 않았다고 볼 수 없고, .pf 파일이 만들어진 시각도 곧바로 첫 실행 시각이 되지 않습니다.

## 왜 이 세 가지를 따로 보나

프리페치 (Prefetch) 는 실행 흔적 가운데 가장 자주 쓰는 기록인 만큼 잘못 읽는 경우도 많고, 대개 다음 세 가지입니다.

1. 프리페치가 꺼져 있어서 기록이 처음부터 없는 경우
2. 보관 개수 한도 때문에 오래된 기록이 밀려난 경우
3. .pf 파일의 생성 시각을 첫 실행 시각으로 그대로 믿는 경우

.pf 파일의 구조와 압축 형식은 [파일 구조와 버전](format-versions-mam.md)에서 다룹니다. 파일 안의 실행 횟수와 실행 시각은 [실행 횟수와 실행 시각 읽기](run-count-last-run-times.md)에서 다룹니다. 이 페이지는 그 값을 해석할 때 빠지기 쉬운 함정만 다룹니다.

## 함정 1 — 프리페치가 꺼진 경우

### 무엇이 프리페치를 끄나

프리페치를 켜고 끄는 값은 REG_DWORD 형식의 `EnablePrefetcher` 입니다.

- 라이브 시스템: `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters`
- 오프라인 SYSTEM 하이브: `ControlSet00X\Control\Session Manager\Memory Management\PrefetchParameters`

오프라인 하이브에는 CurrentControlSet 이 없습니다. 어느 ControlSet00X 를 읽을지는 [컨트롤셋 고르기](../../../01-foundations/database-log-formats/registry-hive/controlset-select.md)를 따릅니다.

| 값 | 뜻 | .pf 파일 |
|---|---|---|
| 0 | 끔 | 새로 생기지 않음 |
| 1 | 응용 프로그램 시작 프리페치만 켬 | 생김 |
| 2 | 부팅 프리페치만 켬 | 응용 프로그램 .pf 는 생기지 않음 |
| 3 | 둘 다 켬 | 생김 |

Windows 클라이언트에서 흔히 보는 값은 3 입니다.

값 하나만 보고 끝내면 안 됩니다. Vista 이후에는 SysMain 서비스가 .pf 파일을 쓰는데, SysMain 은 svchost.exe 안에서 sysmain.dll 로 돌아갑니다. 이 서비스를 멈추거나 사용 안 함으로 두면 .pf 파일이 새로 생기지 않습니다. 서비스 설정은 SYSTEM 하이브의 `ControlSet00X\Services\SysMain` 키에 있고, 이 키의 `Start` 값이 4 이면 사용 안 함입니다. 서비스 키를 읽는 법은 [서비스·드라이버](../../persistence/services-drivers.md)를 봅니다. 서비스의 화면 표시 이름은 Windows 버전에 따라 Superfetch 로 나오기도 합니다.

### 처음부터 꺼져 있는 환경

| 환경 | 응용 프로그램 프리페치 | 근거 |
|---|---|---|
| Windows XP·Vista·7 클라이언트 (하드디스크) | 켜짐 | 기본 동작 |
| Windows 7 클라이언트 (성능 좋은 SSD) | 꺼짐 | Microsoft Windows 7 개발팀 블로그 |
| Windows 8·8.1·10·11 클라이언트 | 대개 켜짐. SSD 에서도 .pf 파일이 쌓이는 경우가 흔합니다 | 분석가 관찰 |
| Windows Server | 꺼짐으로 널리 알려져 있음 | Microsoft 포럼 답변·분석가 자료 |

Windows 7 은 시스템 디스크가 SSD 이고 임의 읽기·쓰기·플러시 성능이 괜찮으면 부팅 프리페치와 응용 프로그램 프리페치를 끕니다. 이 자동 판단이 `EnablePrefetcher` 값에 어떻게 드러나는지는 공식 문서에 없습니다. 그래서 값이 3 이어도 Prefetch 폴더가 비어 있을 수 있습니다. 값과 폴더 상태를 함께 봅니다.

서버에서 .pf 파일이 없는 것은 대개 정상이며, 서버에서 실행을 확인할 때는 처음부터 다른 기록을 봅니다.

### 확인 순서

1. SYSTEM 하이브에서 `EnablePrefetcher` 값을 읽습니다.
2. `Services\SysMain` 의 `Start` 값을 읽습니다.
3. `%SystemRoot%\Prefetch` 폴더에 .pf 파일이 있는지, 가장 최근 .pf 가 언제 갱신됐는지 봅니다.
4. 다른 실행 흔적([BAM·DAM](../background-activity-moderator.md), [AmCache](../amcache-hve/index.md), [프로세스 생성 4688](../../event-logs/4688.md))은 계속 쌓이는데 .pf 갱신만 어느 날 멈췄는지 봅니다.

4번에서 멈춘 날이 보이면 그 무렵에 설정이 바뀌었을 수 있습니다. `PrefetchParameters` 키와 `SysMain` 키의 [마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md)을 그 날과 비교합니다. 마지막 기록 시각은 키 안의 어떤 값이 바뀌었는지까지 알려 주지 않습니다.

## 함정 2 — 보관 개수 한도

### 한도

| Windows 버전 | .pf 파일 보관 한도 |
|---|---|
| XP·Vista·7 | 128 개 |
| 8 이후 (8.1·10·11 포함) | 1,024 개 |

한도에 이르면 Windows 가 오래된 .pf 파일을 지우고 새 파일을 만드는데, 어떤 순서로 몇 개를 지우는지는 공개 문서에 없습니다.

Prefetch 폴더에는 .pf 말고도 Layout.ini, Ag 로 시작하는 .db 파일 같은 다른 파일이 있는데, 한도와 비교할 때는 .pf 파일만 셉니다.

### 어떻게 읽나

- .pf 파일 수가 한도에 가까우면 오래된 기록이 이미 밀려났을 수 있습니다. 이때 .pf 가 없다는 것은 거의 아무 뜻이 없습니다.
- .pf 파일 수가 한도보다 한참 적은데 찾는 프로그램의 .pf 가 없으면, 몇 가지 가능성이 남습니다. 실행하지 않았을 수 있습니다. .pf 를 누가 지웠을 수 있습니다. 그때 프리페치가 꺼져 있었을 수 있습니다. 파일 수만으로는 이 가운데 무엇인지 가를 수 없습니다.
- Windows 7 이하는 한도가 128 개라서 8 이후보다 기록이 훨씬 빨리 밀려납니다. 얼마 만에 밀려나는지는 사용 습관에 따라 다릅니다.

지워진 .pf 는 [$MFT](../../filesystem/mft.md)의 지운 레코드, [$UsnJrnl](../../filesystem/usnjrnl.md)의 삭제 기록, [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)에 남을 수 있습니다. $UsnJrnl 에 .pf 파일 이름과 삭제 기록이 있으면 그 이름의 .pf 가 한때 있었다는 뜻입니다.

## 함정 3 — 첫 실행 시각

### .pf 생성 시각이 첫 실행 시각과 어긋나는 이유

.pf 파일은 그 실행 파일이 처음 실행될 때 만들어지므로 파일시스템의 생성 시각을 첫 실행 시각으로 읽는 관행이 있습니다. 이 관행은 .pf 파일이 한 번도 지워지거나 다시 만들어지지 않았을 때만 맞습니다.

| 원인 | 결과 | 확인할 곳 |
|---|---|---|
| 기록 시점이 실행 시작보다 늦음 | 생성 시각이 실제 시작보다 몇 초 늦음 | 다른 실행 기록의 초 단위 시각 |
| 보관 한도로 지워진 뒤 다시 실행 | 생성 시각이 다시 만든 시각이 됨 | $UsnJrnl 의 같은 이름 삭제·생성 기록 |
| 사용자나 정리 도구가 지운 뒤 다시 실행 | 위와 같음 | 정리 도구의 실행 흔적, $UsnJrnl |
| 처음 실행할 때 프리페치가 꺼져 있었음 | 생성 시각이 프리페치를 켠 뒤 첫 실행 시각이 됨 | 함정 1 의 확인 순서 |
| 처음에는 다른 경로에서 실행 | 경로가 다르면 .pf 도 따로 생김 | [경로 해시로 실행 위치 구분하기](path-hash.md) |
| 수집할 때 일반 복사로 옮김 | 사본의 생성 시각이 복사한 시각으로 바뀜 | 원본 이미지의 $MFT |
| 생성 시각을 조작함 | 생성 시각이 앞이나 뒤로 옮겨짐 | [두 벌의 시각](../../../01-foundations/disk-volume/ntfs/standard-information-file-name.md), [시각 조작 탐지](../../../03-techniques/analysis/timeline/timestomping.md) |

### 몇 초 늦게 찍히는 문제

프리페치는 프로그램이 시작한 뒤 처음 10초 동안 읽은 파일을 모은 다음 .pf 파일을 씁니다. 그래서 .pf 의 생성 시각, 수정 시각, 파일 안의 실행 시각이 실제 시작보다 늦게 찍힙니다. 초 단위로 볼 때는 흔히 10초를 빼 보지만, 차이가 정확히 10초라는 Microsoft 공식 문서는 없습니다. 초 단위가 중요하면 [프로세스 생성 4688](../../event-logs/4688.md)이나 [Sysmon 이벤트 1](../../event-logs/sysmon/1.md) 같은 시작 시각 기록과 맞춰 봅니다.

### 파일 안의 실행 시각과 함께 보기

Windows 8 이후 .pf 파일 안에는 최근 실행 시각이 8개까지 있고, XP~7 에는 1개만 있습니다. 실행 횟수가 8번을 넘으면 파일 안의 가장 이른 시각도 첫 실행이 아니며, 이때 .pf 파일에서 첫 실행에 가장 가까운 단서는 생성 시각입니다. 파일 안의 시각을 읽는 법은 [실행 횟수와 실행 시각 읽기](run-count-last-run-times.md)를 봅니다.

실행 횟수가 8 이하이면 파일 안의 가장 이른 시각과 생성 시각이 가까운지 확인해 볼 수 있고, 둘이 크게 다르면 생성 시각 조작이나 시계 변경을 의심하고 더 봅니다. 이 비교는 판단을 돕는 점검일 뿐, 명세가 보장하는 규칙은 아닙니다.

### 시각의 기준

- .pf 파일 안의 실행 시각은 UTC 기준 FILETIME 입니다. 값 형식은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다.
- NTFS 의 생성·수정 시각도 UTC 로 저장됩니다. 도구가 현지 시각으로 바꿔 보여 주는지 확인합니다.
- 두 시각 모두 그때의 시스템 시계를 따릅니다. 시계를 바꾼 흔적은 [시스템 시각을 바꿨나](../../../04-scenarios/activity/anti-forensics/system-time-change.md)에서 확인합니다.
- .pf 생성 시각이 OS 설치 시각보다 이르면 더 따져 봅니다. Windows 10 이후에는 기능 업데이트 때 설치 시각이 다시 기록될 수 있으므로 곧바로 조작으로 보지 않습니다. 설치 시각은 [시스템 기본 정보](../../system-account/os-version-computer-name-install-date-shutdown-t.md)에서 봅니다.

## 증거로서 의미

**증명하는 것**

- .pf 파일이 있으면, 그 이름과 경로의 실행 파일이 이 시스템에서 실행된 적이 있습니다.
- .pf 생성 시각은 "늦어도 이 무렵에는 실행됐다" 는 뜻입니다. 조작이 없다는 전제가 필요합니다.
- .pf 파일 수가 한도보다 적고 삭제 흔적도 없으면, 수집 시점에 남은 기록이 한도 때문에 잘린 것은 아닐 가능성이 큽니다.

**증명하지 못하는 것**

- .pf 가 없다는 것은 실행하지 않았다는 증거가 아닙니다.
- .pf 생성 시각만으로 "이때 처음 실행했다" 고 말할 수 없습니다.
- `EnablePrefetcher` 가 지금 0 이라는 것은 수집 시점의 설정만 보여 줍니다. 언제부터 0 이었는지는 알려 주지 않습니다.

## 지우기·끄기가 남기는 흔적

- Prefetch 폴더를 통째로 지우면 $UsnJrnl 에 .pf 삭제 기록이 한꺼번에 몰려 남을 수 있습니다.
- 지운 뒤에도 정리 도구나 명령을 실행하면 그 도구의 .pf 가 새로 생길 수 있습니다. 이 .pf 의 생성 시각이 지운 시각 근처를 가리킵니다.
- 설정을 바꾸면 `PrefetchParameters` 키나 `SysMain` 키의 마지막 기록 시각이 바뀝니다.
- 프리페치를 꺼도 다른 실행 흔적은 계속 쌓입니다. .pf 갱신만 멈춘 구간이 보이면 그 구간을 안티포렌식 가능성으로 표시합니다. 자세한 흐름은 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md)를 봅니다.

## 직접 분석해 보기

1. 수집본에서 Prefetch 폴더의 .pf 파일은 복사본의 시각이 아니라 원본 이미지의 $MFT 레코드로 생성 시각을 읽습니다. 수집 방법은 [선별 수집](../../../03-techniques/process-acquisition/evidence-acquisition/triage-collection.md)을 봅니다.
2. .pf 파일 수를 세어 버전별 한도와 비교합니다.
3. SYSTEM 하이브에서 `Select` 값으로 ControlSet 을 고르고 `EnablePrefetcher` 와 `SysMain\Start` 를 읽습니다. REG_DWORD 값 3 은 원시 바이트로 `03 00 00 00` 입니다(리틀 엔디언, 명세로 만든 예시).
4. 공개 도구를 예로 들면 PECmd 로 .pf 내용을, MFTECmd 로 $MFT 와 $UsnJrnl 을, Registry Explorer 나 RegRipper 로 두 키를 읽을 수 있습니다. 도구 하나의 결과만 믿지 말고 두 가지 이상으로 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 무엇을 채워 주나 | 링크 |
|---|---|---|
| $UsnJrnl | .pf 가 지워지고 다시 생긴 기록 | [USN 변경 저널](../../filesystem/usnjrnl.md) |
| $MFT | .pf 의 두 벌 시각, 지운 .pf 레코드 | [마스터 파일 테이블](../../filesystem/mft.md) |
| AmCache | 실행 파일의 경로·해시. 프리페치가 꺼진 환경에서 보완 | [AmCache](../amcache-hve/index.md) |
| BAM·DAM | 사용자별 마지막 실행 시각 | [BAM·DAM](../background-activity-moderator.md) |
| 심캐시 | 실행 파일이 있었다는 흔적 | [심캐시](../shimcache-appcompatcache.md) |
| UserAssist | 탐색기로 실행한 기록과 횟수 | [UserAssist](../userassist.md) |
| SRUM | 시간 단위 앱 자원 사용 | [SRUM](../system-resource-usage-monitor/index.md) |
| 4688·Sysmon 1 | 초 단위 프로세스 시작 시각 | [4688](../../event-logs/4688.md), [Sysmon 1](../../event-logs/sysmon/1.md) |

전체 흐름은 [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md)를 봅니다.

## 보고서 문장 예

- 쓰지 말 것: "A.exe 는 이 PC 에서 실행된 적이 없다."
- 쓸 것: "수집 시점 Prefetch 폴더에 A.exe 의 .pf 파일은 없다. 같은 폴더의 .pf 파일은 (개수)개로 Windows 10 의 보관 한도 1,024 개에 가깝다. 오래된 기록이 밀려났을 가능성이 있다."
- 쓰지 말 것: "A.exe 는 (시각)에 처음 실행됐다."
- 쓸 것: "A.exe 의 .pf 파일은 (시각, UTC)에 만들어졌다. 이 시각 이전에 .pf 가 지워진 기록은 $UsnJrnl 보존 범위 안에서 찾지 못했다."

## 실습

NIST CFReDS 같은 공개 시험 이미지에서 Windows 10 이미지를 하나 골라 아래 질문을 풀어 봅니다.

1. `EnablePrefetcher` 값과 `SysMain\Start` 값은 무엇입니까? 이 두 값으로 보아 수집 시점에 .pf 가 생기는 상태였습니까?
2. .pf 파일은 몇 개입니까? 한도에 가깝습니까?
3. 실행 횟수가 8을 넘는 .pf 를 하나 고릅니다. 파일 안의 가장 이른 실행 시각과 .pf 생성 시각은 얼마나 떨어져 있습니까?
4. $UsnJrnl 에 .pf 삭제 기록이 있습니까? 있다면 같은 이름으로 다시 생긴 기록도 있습니까?
5. .pf 가 없는데 AmCache 나 BAM 에는 흔적이 있는 실행 파일이 있습니까? 그 이유로 가장 그럴듯한 것은 무엇입니까?

## 함께 볼 페이지

- [프리페치 (Prefetch)](index.md)
- [참조 파일·폴더 목록 활용](referenced-files.md)
- [PC 를 초기화하거나 윈도를 다시 깔았나](../../../04-scenarios/activity/anti-forensics/reset-reinstall.md)

## 참고 문헌

- Microsoft Learn, "Disable Prefetch (Standard 7 SP1)" — `EnablePrefetcher` 경로와 값 0~3. https://learn.microsoft.com/en-us/previous-versions/windows/embedded/ff794503(v=winembedded.60)
- Microsoft Learn (Engineering Windows 7 블로그 보관본), "Support and Q&A for Solid-State Drives", 2009 — Windows 7 의 SSD 프리페치 자동 해제 조건. https://learn.microsoft.com/en-us/archive/blogs/e7/support-and-qa-for-solid-state-drives
- libyal, "Windows Prefetch File (PF) format" — 실행 시각이 UTC FILETIME, 버전별 실행 시각 개수, MAM 압축. https://github.com/libyal/libscca/blob/main/documentation/Windows%20Prefetch%20File%20(PF)%20format.asciidoc
- SANS Internet Storm Center, Logan Flook, "Forensic Value of Prefetch", 2022 — 보관 한도 128·1,024 개, 10초 차이. https://isc.sans.edu/diary/29168
- Seth Enoka, "Windows Prefetch Forensics: Execution Evidence and Its Limits" — 서버 기본 해제, 다시 만든 .pf 의 생성 시각 문제. https://sethenoka.com/prefetch-execution-evidence-and-its-limits/
- PassTheHashBrowns, "Muting Prefetch" — SysMain 서비스(sysmain.dll)와 프리페치를 막는 방법이 남기는 흔적. https://passthehashbrowns.github.io/muting-prefetch/
