---
title: "프리페치"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 790
has_children: true
has_toc: false
---

# 프리페치 (Prefetch)

## 한 줄 요약

프리페치 (Prefetch) 는 윈도가 프로그램을 더 빨리 띄우려고 `C:\Windows\Prefetch` 폴더에 만드는 `.pf` 파일입니다. 이 파일에는 실행 파일 이름, 실행 횟수, 최근 실행 시각, 실행 직후 읽은 파일 목록이 남습니다.

## 왜 중요한가

- `.pf` 파일은 프로그램이 실행될 때 생깁니다. 그래서 그 프로그램이 이 PC 에서 실행된 적이 있다는 흔적이 됩니다.
- 실행 시각이 여러 개 남습니다. Windows 8 부터는 마지막 실행 시각 (Last Run Time) 이 최대 8개까지 남습니다. Windows 7 까지는 1개만 남습니다. 파일 안의 시각은 모두 UTC 기준 FILETIME 입니다.
- 실행 횟수 (Run Count) 가 남습니다. 한 번 쓰고 만 도구인지, 자주 쓴 프로그램인지 가늠할 수 있습니다.
- 실행 직후 약 10초 동안 프로그램이 읽은 파일과 폴더 목록이 남습니다. 이 목록으로 프로그램이 연 문서나 불러온 DLL 을 짐작할 수 있습니다.
- 볼륨 정보 (Volume Information) 에는 장치 경로와 볼륨 시리얼 번호가 남습니다. 그래서 읽은 파일이 어느 볼륨에 있었는지 알 수 있습니다.
- 파일 이름 뒤의 8자리 해시는 실행 파일의 경로로 계산합니다. 같은 이름의 프로그램도 다른 폴더에서 실행하면 `.pf` 파일이 따로 생깁니다. 시스템 파일 이름을 흉내 낸 프로그램이 엉뚱한 폴더에서 실행되면 여기서 드러날 수 있습니다.
- 실행 파일을 지워도 `.pf` 파일은 함께 지워지지 않습니다. 그래서 지금 디스크에 없는 프로그램의 실행 흔적도 찾을 수 있습니다.

프리페치로 증명하지 못하는 것은 다음과 같습니다.

- 누가 실행했는지는 남지 않습니다. 프리페치 폴더는 PC 전체에 하나이고 `.pf` 파일에는 사용자를 가리키는 칸이 없습니다.
- 프리페치는 실행이 시작됐다는 기록입니다. 프로그램이 얼마나 오래 돌았는지, 무엇을 했는지는 남지 않습니다.
- 프리페치가 꺼진 PC 에는 `.pf` 파일이 생기지 않습니다. 서버 판 윈도는 기본으로 꺼져 있다는 설명이 있습니다.
- 보관 개수에 한도가 있어서 한도를 넘으면 기존 파일이 정리되므로, `.pf` 파일이 없다는 것만으로 실행하지 않았다고 단정하지 않습니다.
- `.pf` 파일의 생성 시각으로 첫 실행 무렵을 짐작합니다. 다만 프리페치는 실행 뒤 약 10초 동안 기록한 다음 파일을 씁니다. 그래서 파일 시각은 실제 실행 시각보다 조금 늦습니다. 보고서에는 추정값이라고 밝힙니다.

## 한눈에 보기

> 그림 자리: `.pf` 파일 하나에서 읽을 수 있는 항목(파일 이름·경로 해시·실행 횟수·실행 시각 최대 8개·참조 파일 목록·볼륨 정보)과 `.pf` 파일 자체의 생성·수정 시각을 한 장에 나눠 보여 주는 그림

### 위치와 설정

| 항목 | 내용 |
|---|---|
| 폴더 | `%SystemRoot%\Prefetch\` (보통 `C:\Windows\Prefetch\`) |
| 파일 이름 | `<실행 파일 이름>-<경로 해시 8자리>.pf`. 실행 파일 이름은 29자에서 잘립니다. 확장자를 뺀 부분은 보통 대문자입니다. |
| 켜고 끄는 값 | SYSTEM 하이브 `ControlSet00X\Control\Session Manager\Memory Management\PrefetchParameters` 키의 `EnablePrefetcher` (REG_DWORD) |
| 값의 뜻 | 0 = 끔, 1 = 프로그램 실행만, 2 = 부팅만, 3 = 둘 다 |
| 시각 형식 | FILETIME, UTC |
| 사용자 정보 | 없음 |

오프라인 SYSTEM 하이브에서 어느 `ControlSet00X` 를 볼지는 [컨트롤셋 고르기](../../../01-foundations/database-log-formats/registry-hive/controlset-select.md) 에서 다룹니다.

### Windows 버전에 따라 달라지는 점

형식 버전과 Windows 버전의 짝은 libscca 문서를 따릅니다. Windows 11 행은 libscca 이슈 보고와 공개 파서 코드를 함께 반영했습니다. 보관 한도는 SANS ISC 글을 따릅니다.

| Windows 버전 | 형식 버전 | 파일 압축 | 마지막 실행 시각 | 보관 한도 |
|---|---|---|---|---|
| XP · 2003 | 17 | 없음 | 1개 | 128개 |
| Vista · 7 | 23 | 없음 | 1개 | 128개 |
| 8 · 8.1 | 26 | 없음 | 최대 8개 | 1,024개 |
| 10 | 30 | MAM (Xpress Huffman) | 최대 8개 | 1,024개 |
| 11 | 30 또는 31 (24H2 부터 31 이라는 보고) | MAM (Xpress Huffman) | 최대 8개 | 1,024개 |

압축하지 않은 파일은 앞 4바이트가 형식 버전이고, 그 뒤 4바이트가 `SCCA` 서명입니다. Windows 10 부터는 파일 전체를 압축하므로 앞 3바이트가 `MAM` 으로 바뀌고, 압축을 풀어야 `SCCA` 서명이 보입니다. 압축 방식은 [윈도 압축 형식](../../../01-foundations/value-decoding/lznt1-xpress-xpress-huffman.md) 에서 다룹니다.

### 알려 주는 것

| 알 수 있는 것 | 어디에 남나 | 자세히 |
|---|---|---|
| 실행된 프로그램 이름 | 파일 이름, 파일 안의 실행 파일 이름 | [파일 구조와 버전](format-versions-mam.md) |
| 같은 이름 프로그램의 실행 위치 구분 | 파일 이름의 경로 해시 | [경로 해시](path-hash.md) |
| 실행 횟수 | 파일 안의 실행 횟수 칸 | [실행 횟수와 실행 시각](run-count-last-run-times.md) |
| 최근 실행 시각 | 파일 안의 마지막 실행 시각 (1개 또는 최대 8개) | [실행 횟수와 실행 시각](run-count-last-run-times.md) |
| 첫 실행 무렵 (추정) | `.pf` 파일 자체의 생성 시각 | [해석 함정](pitfalls.md) |
| 실행 직후 읽은 파일·폴더 | 참조 파일 목록 | [참조 파일·폴더 목록](referenced-files.md) |
| 읽은 파일이 있던 볼륨 | 볼륨 정보 (장치 경로·시리얼 번호·생성 시각) | [참조 파일·폴더 목록](referenced-files.md) |

## 읽는 순서

1. [파일 구조와 버전 (Format Versions·MAM)](format-versions-mam.md) — 형식 버전 17·23·26·30·31 의 차이를 정리합니다. Windows 10 부터 쓰는 MAM 압축을 풀고 헤더를 읽는 법도 다룹니다.
2. [실행 횟수와 실행 시각 읽기 (Run Count·Last Run Times)](run-count-last-run-times.md) — 실행 횟수와 최대 8개의 실행 시각을 읽습니다. 이 시각을 `.pf` 파일 자체의 시각과 맞춰 보는 법도 다룹니다.
3. [참조 파일·폴더 목록 활용 (Referenced Files)](referenced-files.md) — 실행 직후 읽은 파일·폴더 목록과 볼륨 정보를 읽습니다. 프로그램이 연 문서와 실행한 볼륨을 이 목록으로 좁혀 갑니다.
4. [경로 해시로 실행 위치 구분하기 (Path Hash)](path-hash.md) — 파일 이름 뒤 8자리 해시를 경로로 계산하는 법을 다룹니다. 해시 계산 방식은 Windows 버전마다 다릅니다.
5. [프리페치 해석 함정 (꺼진 경우·보관 개수 한도·첫 실행 시각)](pitfalls.md) — `.pf` 파일이 없거나 시각이 어긋나는 경우를 모읍니다. 파일이 없다는 사실을 어디까지 해석할 수 있는지도 다룹니다.

## 함께 볼 페이지

- [어떤 프로그램을 언제 실행했나 (Program Execution)](../../../04-scenarios/activity/program-execution.md) — 프리페치를 다른 실행 흔적과 함께 읽는 순서입니다.
- [심캐시 (ShimCache·AppCompatCache)](../shimcache-appcompatcache.md) · [AmCache (Amcache.hve)](../amcache-hve/index.md) — 실행 파일의 경로와 해시를 따로 남기는 아티팩트입니다.
- [BAM·DAM (Background Activity Moderator)](../background-activity-moderator.md) · [UserAssist](../userassist.md) — 프리페치에 없는 사용자 정보를 채웁니다.
- [SRUM (System Resource Usage Monitor)](../system-resource-usage-monitor/index.md) — 앱이 얼마나 오래, 얼마나 많이 자원을 썼는지 봅니다.
- [프로세스 생성 (4688)](../../event-logs/4688.md) · [Sysmon 프로세스 생성 (이벤트 1)](../../event-logs/sysmon/1.md) — 켜 둔 경우 실행한 사용자와 명령줄이 남습니다.
- [시각 값 형식 (FILETIME·Unix·WebKit·DOS·OLE)](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) — 실행 시각을 사람이 읽는 시각으로 바꿉니다.
- [USN 변경 저널 ($UsnJrnl)](../../filesystem/usnjrnl.md) — `.pf` 파일이 생기고 지워진 기록을 찾습니다.
- [섀도 복사본 활용 (Volume Shadow Copy Analysis)](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 지금은 없는 옛 `.pf` 파일을 꺼냅니다.
- [완전삭제 도구를 썼나 (Wiping Tools)](../../../04-scenarios/activity/anti-forensics/wiping-tools.md) — 지우는 도구 자체의 실행 흔적을 찾습니다.

## 참고 문헌

- libyal, "Windows Prefetch File (PF) format" (libscca) — https://github.com/libyal/libscca/blob/main/documentation/Windows%20Prefetch%20File%20(PF)%20format.asciidoc
- Microsoft Learn, "Disabling Prefetch" (Windows Embedded 보관 문서) — https://learn.microsoft.com/en-us/previous-versions/windows/embedded/bb499146(v=winembedded.5)
- Logan Flook, "Forensic Value of Prefetch", SANS Internet Storm Center (2022) — https://isc.sans.edu/diary/29168
- dfirfpi, "A first look at Windows 10 prefetch files" (2015) — https://blog.digital-forensics.it/2015/06/a-first-look-at-windows-10-prefetch.html
- Tobias Karlsson, "How to enable PreFetch in Windows Server" (2015) — https://truesecdev.wordpress.com/2015/11/25/how-to-enable-prefetch-in-windows-server/
