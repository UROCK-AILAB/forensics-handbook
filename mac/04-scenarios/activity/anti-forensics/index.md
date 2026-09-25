---
title: "증거를 없애려 했나"
parent: "시나리오 · 행위 재구성"
nav_order: 2390
has_children: true
has_toc: false
---

# 증거를 없애려 했나 (Anti-Forensics)

맥에서 로그를 지우거나 시각을 바꾸거나 기기를 초기화하거나 데이터를 덮어써 흔적을 없애려 했는지 확인하고, 그런 시도가 남긴 흔적과 공백을 어떻게 해석하는지 다루는 시나리오입니다.

## 왜 중요한가

흔적을 없애려는 시도는 그 자체로 조사 결론을 바꿉니다. 로그가 빈 구간이나 시각이 틀어진 구간에서 나온 결론은 모두 다시 따져야 하고, 반대로 그런 시도가 없었다는 판단도 근거가 있어야 보고서에 쓸 수 있습니다.

macOS 에는 흔적을 지우거나 바꾸는 기본 수단이 여럿 있습니다. 통합 로그를 지우는 `log erase` [1], 날짜·시각을 바꾸고 네트워크 시각 동기를 끄는 `systemsetup` 옵션 [2], 데이터·설정·앱을 지우고 macOS 는 남기는 "모든 콘텐츠 및 설정 지우기" [3], 디스크나 빈 공간을 덮어쓰는 `diskutil` 명령 [4]이 그 예입니다. 다만 겉보기에 지우는 수단이라도 실제 효과는 다릅니다. macOS 재설치는 앱과 개인 데이터를 지우지 않고 [5] `rm -P` 는 지금 아무 효과가 없어서 [6], 어떤 수단을 썼는지 확인한 뒤에도 그 수단이 실제로 무엇을 없앴는지 따로 판단합니다.

이 수단들을 썼다는 기록 자체가 어디에 남는지는 공개된 자료가 많지 않습니다. 그래서 이 허브의 하위 페이지는 사용한 흔적을 직접 찾는 방법과 함께, 공백과 모순을 여러 기록에 비추어 해석하는 방법을 다루고, 흔적이 나오지 않았을 때 무엇까지 말할 수 있는지를 절마다 다룹니다.

## 한눈에 보기

| 수단 | 먼저 볼 위치 | macOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 로그 지우기 | 통합 로그 저장소, `log stats` 출력, 명령 기록 | 공개 자료 없음 | 로그가 빈 구간과 지운 범위의 가능성 |
| 시스템 시각 바꾸기 | `/private/var/run/utmpx`, 시간대 설정, 통합 로그 timesync | 공개 자료 없음 | 시각이 뛴 지점, 시간대 변경과 시계 변경의 구분 |
| 초기화·재설치 | `/Library/Receipts/InstallHistory.plist`, 사용자 계정, 볼륨 시각 | 모든 콘텐츠 및 설정 지우기는 macOS 12 이상, Apple silicon 또는 T2 [3] | 초기화했는지 재설치만 했는지, 그 시기 |
| 삭제 도구 | 명령 기록, 격리 속성, 빈 공간 내용 | 디스크 유틸리티 보안 지우기 안내는 macOS 10.15 이후 같은 내용, SSD 에서는 옵션 없음 [7] | 덮어쓰기 시도와 덮어쓴 범위 |

## 읽는 순서

1. [로그 지우기 (Log Clearing)](log-clearing.md) — `log erase` 인자별로 지우는 범위와, 로그 공백을 찾고 다른 기록으로 메우는 순서를 다룹니다.
2. [시스템 시각 바꾸기 (Time Change)](time-change.md) — 시간대와 시계 변경을 가르는 법, utmpx 레코드 구조, 기록 사이 시각 모순을 찾는 흐름을 다룹니다.
3. [초기화·재설치 (Erase·Reinstall)](erase-reinstall.md) — 모든 콘텐츠 및 설정 지우기와 재설치의 차이, 설치 기록과 계정·볼륨 시각으로 시기를 가늠하는 법을 다룹니다.
4. [삭제 도구 (Wiping Tools)](wiping-tools.md) — `diskutil`·`rm` 같은 기본 수단이 실제로 하는 일과, 덮어쓰기 흔적과 빈 공간의 모양을 해석하는 법을 다룹니다.

로그 공백이나 기록 사이 모순이 보이면 1번과 2번을 함께 보는 편이 좋습니다. 시각이 틀어진 구간은 로그가 빈 것처럼 보이거나 공백을 가릴 수 있어서, 두 페이지의 확인을 마친 뒤 3번과 4번으로 넘어갑니다.

## 함께 볼 페이지

- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) — 공백과 시각 모순을 한 타임라인에서 찾을 때
- [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md) — 로그 저장소와 timesync 구조
- [지운 파일의 흔적 찾기 (Deleted File Traces)](../deleted-file-traces.md) — 덮어쓰지 않은 일반 삭제를 다룰 때
- [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](../usage-time.md) — 공백 구간에 맥이 켜져 있었는지 볼 때
- [포렌식 보고서 (Forensic Report)](../../../03-techniques/reporting/forensic-report.md) — 흔적이 없을 때 결론을 적는 법

## 참고 문헌

1. SS64 — macOS `log` 명령 — https://ss64.com/mac/log.html
2. SS64 — macOS `systemsetup` 명령 — https://ss64.com/mac/systemsetup.html
3. Apple Support — Erase your Mac (Erase All Content and Settings), 102664 — https://support.apple.com/en-us/102664
4. SS64 — macOS `diskutil` 명령 — https://ss64.com/mac/diskutil.html
5. Apple Support — How to reinstall macOS, 102655 — https://support.apple.com/en-us/102655
6. SS64 — macOS `rm` 명령 — https://ss64.com/mac/rm.html
7. Apple Disk Utility User Guide — Erase and reformat a storage device in Disk Utility on Mac — https://support.apple.com/guide/disk-utility/erase-and-reformat-a-storage-device-dskutl14079/mac
