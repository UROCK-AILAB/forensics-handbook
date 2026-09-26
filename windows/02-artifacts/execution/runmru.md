---
title: "실행 창 명령 기록"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 1080
---

# 실행 창 명령 기록 (RunMRU)

## 한 줄 요약

실행 창 (Run dialog) 에 친 명령은 사용자 하이브 NTUSER.DAT 의 `Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU` 키에 남습니다. 항목의 순서는 `MRUList` 값이 정합니다. 시각은 키의 마지막 기록 시각 하나뿐입니다.

## 무엇을 기록하나 · 왜 생기나

실행 창은 Windows 키와 R 을 함께 눌러 여는 작은 입력 창이고, 프로그램 이름뿐 아니라 폴더 경로나 주소도 칠 수 있습니다. 여기에 친 명령을 최근에 쓴 순서로 모아 둔 목록 (MRU, Most Recently Used) 이 RunMRU 이며, 다음에 실행 창을 열면 이 목록에서 예전 명령을 고를 수 있습니다.

사용자 하이브에 있어서 사용자마다 목록이 따로 있습니다. 오래 알려진 키로, 이 키를 읽는 RegRipper `runmru` 플러그인은 2008-03-24 에 처음 만들어졌습니다[1].

## 위치와 버전별 차이

| 하이브 | 키 경로 | 라이브에서 보이는 자리 |
|---|---|---|
| NTUSER.DAT | `Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU` | 그 사용자가 로그온해 있으면 HKEY_CURRENT_USER 아래 같은 경로 |

- Windows 버전에 따라 키나 값이 어떻게 다른지는 실제 데이터로 확인해야 합니다.
- 값이 하나도 없는 RunMRU 키가 OS 설치 당일부터 있을 수 있습니다 (Windows 11 25H2 기준).
- 하이브 파일의 위치와 수집하는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 를 따릅니다.

## 구조

키 안에는 명령을 담은 값들과 순서를 적은 `MRUList` 값이 있습니다. RegRipper 의 `runmru` 플러그인은 이 키의 값을 모두 읽어 `MRUList` 를 먼저 보여 준 뒤 나머지 값을 이름순으로 보여 줍니다. 실제 순서는 `MRUList` 가 정하며, 값 이름순은 최근 순서가 아닙니다.

`MRUList` 로 순서를 읽는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 의 MRU 목록 항목에서 다룹니다.

### 공개 근거가 없는 것

아래는 흔히 알려진 내용이지만 공개된 근거가 없습니다. 실제 데이터로 확인한 것만 보고서에 씁니다.

- 값 이름이 `a`, `b`, `c` 같은 한 글자이고, `MRUList` 는 그 글자를 최근 순으로 이은 문자열이라는 점
- 값 데이터 끝에 `\1` 이 붙는다는 점
- 목록에 최대 26개까지 남는다는 점
- 정책 값 `NoRun`·`ClearRecentDocsOnExit`·`NoRecentDocsHistory` (NTUSER.DAT 의 `Policies\Explorer` 키) 와 `Start_TrackProgs` (`Explorer\Advanced` 키) 가 이 목록에 영향을 주는지

기본 상태에서는 위 네 값이 모두 없습니다.

## 증거로서 의미

### 증명하는 것

- 이 사용자 하이브의 RunMRU 에 어떤 문자열이 있으면, 이 계정에서 실행 창에 그 문자열을 친 기록이 있다는 뜻입니다.
- `MRUList` 의 순서는 항목을 마지막으로 쓴 순서를 알려 줍니다.
- `MRUList` 맨 앞 항목은 키의 마지막 기록 시각 무렵에 쳤다고 추정할 근거가 됩니다.

### 증명하지 못하는 것

- 명령이 성공했는지, 프로그램이 실제로 떴는지는 알 수 없습니다.
- 맨 앞 항목이 아닌 항목을 언제 쳤는지는 알 수 없습니다.
- 목록은 순서만 알려 줍니다. 몇 번 쳤는지는 알 수 없습니다.
- 목록이 비었다고 실행 창을 쓰지 않았다고 쓰지 않습니다. 키만 있고 값이 없을 수 있고, 사용자가 목록을 지웠을 수도 있습니다.
- 키보드 앞의 사람이 누구인지는 알 수 없습니다.

보고서에는 "그 시각에 cmd 를 실행했다" 대신 "사용자 X 의 NTUSER.DAT RunMRU 키에 `cmd` 항목이 있고 `MRUList` 맨 앞이다. 키의 마지막 기록 시각은 A(UTC) 이다" 처럼 씁니다.

## 시각 해석

- 레지스트리 값에는 따로 시각이 없습니다. 키마다 마지막 기록 시각 (Last Write Time) 하나만 있습니다. [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.
- RegRipper `runmru` 플러그인은 이 키의 마지막 기록 시각을 UTC 로 보여 줍니다.
- 이 시각은 `MRUList` 맨 앞 항목을 친 시각을 추정하는 근거이지만, 키 시각은 목록이 바뀐 때이지 한 항목을 친 때라고 적힌 값이 아닙니다. 무엇이 바뀔 때 이 시각이 바뀌는지는 하이브 구조 페이지의 마지막 기록 시각 항목을 따릅니다.
- 나머지 항목의 시각은 다른 기록으로 좁힙니다.
  - 섀도 복사본 속 옛 NTUSER.DAT 의 RunMRU 와 비교하면, 항목이 목록에 들어온 때를 두 복사본 사이로 좁힐 수 있습니다. [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 을 참고합니다.
  - 친 명령이 프로그램이면 그 프로그램의 실행 흔적과 시각을 맞춥니다.
- 여러 기록을 한 시간 축에 놓는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 을 따릅니다.

## 함정과 한계

- **키가 있다고 실행 창을 썼다는 뜻이 아닙니다.** 값이 없는 키가 OS 설치 당일부터 있을 수 있습니다.
- **값 이름순으로 읽지 않습니다.** 도구가 값을 이름순으로 보여 줄 수 있습니다. 순서는 늘 `MRUList` 로 읽습니다.
- **로그 파일을 함께 수집합니다.** 주 하이브 파일만으로는 최신 상태가 아닐 수 있습니다. [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 를 따라 트랜잭션 로그를 함께 가져옵니다.
- **정책과 설정 값을 함께 적어 둡니다.** `NoRun`·`ClearRecentDocsOnExit`·`NoRecentDocsHistory`·`Start_TrackProgs` 의 영향을 설명한 공개 자료는 없습니다. 분석 대상에 이 값이 있는지 보고서에 함께 적습니다.
- **지운 항목.** 사용자가 목록을 지웠을 수 있습니다. 지운 값은 하이브의 빈 셀, 트랜잭션 로그, 섀도 복사본에서 찾습니다. 찾는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 와 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 있습니다.
- **친 문자열이 곧 실행한 파일은 아닙니다.** 실행 창에는 폴더 경로나 주소도 칠 수 있습니다. 무엇을 열었는지는 다른 기록으로 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

키의 마지막 기록 시각은 FILETIME 8바이트입니다. 키 셀 안에서 이 8바이트를 찾는 법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다. 아래는 FILETIME 규칙으로 만든 예시입니다. 실제 데이터에서 나온 값이 아닙니다.

```
00 1C E5 59 BB 76 DA 01                 디스크에 놓인 순서 (리틀 엔디언)
→ 0x01DA76BB59E51C00                     바이트를 거꾸로 읽은 값
→ 133549686000000000                     1601-01-01 00:00 UTC 부터 센 100나노초 수
133549686000000000 ÷ 10,000,000 − 11644473600 = 1710495000 (유닉스 시간, 초)
→ 2024-03-15 09:30:00 UTC
```

- 시각 값 변환은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 정리합니다.

### 공개 도구로 한 번

사용자의 NTUSER.DAT 와 트랜잭션 로그를 함께 사본으로 뜬 뒤 RegRipper 로 읽습니다.

```
rip.exe -r NTUSER.DAT -p runmru
```

- 출력 맨 위에 키의 마지막 기록 시각 (UTC) 이 나옵니다.
- 이어서 `MRUList` 값이 나오고, 나머지 값이 이름순으로 나옵니다.
- `MRUList` 에 적힌 순서대로 값을 다시 늘어놓은 뒤 읽습니다.
- 다른 하이브 뷰어로 같은 키를 열어 결과를 한 번 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 프리페치 | 친 명령이 프로그램이면 그 실행 시각 | [프리페치](prefetch/index.md) |
| BAM·DAM | 사용자별 마지막 실행 시각 | [BAM·DAM](background-activity-moderator.md) |
| 탐색기 입력 기록 | 같은 경로를 탐색기 주소 창에도 쳤는지 | [탐색기 입력 기록](../file-folder-usage/typedpaths-wordwheelquery.md) |
| 공유 폴더·네트워크 드라이브 | 공유 폴더 경로를 친 경우 그 연결 흔적 | [공유 폴더·네트워크 드라이브](../network/network-shares-mapped-drives.md) |
| 인터넷 익스플로러·옛 엣지 | 주소를 쳐서 연 경우 주소 입력 기록 | [인터넷 익스플로러·옛 엣지](../browsers/ie-edgehtml/index.md) |
| 섀도 복사본 | 예전 목록과의 차이 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

실행 흔적 전체를 엮는 흐름은 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md) 에 있습니다.

## 실습

공개 시험 이미지(NIST CFReDS 등)에서 사용자마다 NTUSER.DAT 를 꺼내 풀어 봅니다.

1. RunMRU 키가 있습니까? 값은 몇 개이고, `MRUList` 는 무엇입니까?
2. `MRUList` 순서대로 항목을 늘어놓습니다. 가장 최근 항목은 무엇이고, 키의 마지막 기록 시각은 언제입니까?
3. 값 이름, `MRUList` 모양, 값 데이터 끝 문자가 "공개 근거가 없는 것" 에 적은 내용과 같습니까?
4. 가장 최근 항목이 프로그램이면 프리페치에서 같은 프로그램의 실행 시각을 찾습니다. 키 시각과 가깝습니까?
5. 섀도 복사본이 있으면 옛 NTUSER.DAT 의 RunMRU 와 비교합니다. 두 복사본 사이에 새로 들어온 항목은 무엇입니까?

## 참고 문헌

1. H. Carvey, *runmru.pl* (RegRipper 3.0 플러그인 — 키 경로, `MRUList` 로 순서를 정하는 처리, 마지막 기록 시각 UTC 출력, 2008-03-24 처음 작성). https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/runmru.pl
