---
title: "스냅숏과 백업 비교"
parent: "기법 · 분석"
nav_order: 2260
---

# 스냅숏과 백업 비교 (Snapshot·Time Machine Diff)

두 시점의 APFS 스냅숏이나 타임 머신 백업을 나란히 놓고, 그 사이에 새로 생기거나 사라지거나 바뀐 파일을 가려 내는 방법을 다룹니다.

## 언제 쓰나

지운 파일이 언제까지 디스크에 있었는지, 조사 기간에 어떤 문서가 바뀌었는지, 의심 파일이 어느 시점에 처음 나타났는지를 알고 싶을 때 씁니다. 현재 파일 시스템만 보면 마지막 상태밖에 알 수 없지만, 스냅숏은 한 시점의 파일 시스템을 읽기 전용 사본으로 잡아 두어서 [4] 시점마다 상태를 비교할 수 있습니다. 스냅숏 안에서 지운 파일을 되찾는 일은 [삭제 데이터 복구 (Data Recovery)](data-recovery/index.md) 에서, 타임 머신 아티팩트 자체는 [타임 머신 (Time Machine)](../../02-artifacts/filesystem/time-machine/index.md) 에서 다룹니다.

비교할 재료는 세 가지입니다.

| 재료 | 있는 곳 | 이름 형식 | 성격 |
|---|---|---|---|
| 로컬 스냅숏 | 백업하는 각 APFS 볼륨 [3] | `com.apple.TimeMachine.YYYY-MM-DD-HHMMSS.local` [1] | 대략 한 시간마다 만들고 24시간 보관 [2] |
| APFS 백업 디스크의 백업 | 백업 디스크 루트(머신 디렉터리 역할) [1] | `com.apple.TimeMachine.YYYY-MM-DD-HHMMSS.backup` [1] | 읽기 전용 합성 스냅숏 [3] |
| HFS+ 백업 디스크의 백업 | `Backups.backupdb` 아래 머신 디렉터리 [1] | `YYYY-MM-DD-HHMMSS` [1] | 파일·폴더·하드 링크로 이뤄진 구조 [3] |

Apple 은 백업 디스크 형식으로 APFS 를 권하지만 이미 Mac OS 확장 형식 백업이 있는 디스크는 그대로 쓸 수 있어서 [5], 한 사건에서 두 구조를 모두 만날 수 있습니다. 두 구조의 저장 방식은 [타임 머신 (Time Machine)](../../02-artifacts/filesystem/time-machine/index.md) 에서, APFS 스냅숏의 디스크 구조는 [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md) 에서 봅니다.

버전에 따라 알아 둘 차이는 다음과 같습니다.

| macOS | 달라지는 점 | 출처 |
|---|---|---|
| 10.11 El Capitan 이후 | 타임 머신이 백업 파일의 체크섬을 기록 | [1] |
| 10.13 High Sierra 이후 | macOS 업데이트를 설치하기 전에 로컬 스냅숏을 하나 더 저장 | [2] |
| 10.15 Catalina 이후 | 스냅숏 확장 메타데이터(스냅숏 UUID 등) 추가 | [4] |
| 11 Big Sur 이후 | 시스템 볼륨의 스냅숏에서 부팅 | [6] |
| 13 Ventura 이후 | 백업 빈도를 "수동" 으로 바꾸면 로컬 스냅숏이 몇 분 안에 지워짐(그 전에는 자동 백업 끄기) | [2] |

## 절차

1. **로컬 스냅숏부터 확보합니다.** 로컬 스냅숏은 오래되거나 공간이 필요하면 자동으로 지워지고, 여유 공간이 넉넉한 디스크에만 저장됩니다 [2]. 조사 중에도 사라질 수 있어서 라이브 시스템이라면 스냅숏 목록을 가장 먼저 남기고, 수집 순서는 [라이브 대응 (Live Response)](../process-acquisition/live-response/index.md) 과 [맥 증거 확보 (Acquisition)](../process-acquisition/evidence-acquisition/index.md) 를 따릅니다.
2. **백업 디스크는 통째로 이미징합니다.** APFS 백업 디스크의 스냅숏을 다른 곳으로 복사하거나 옮길 방법이 없다고 알려져 있어서(2022년 글 기준) [3], 백업 디스크 전체를 이미지로 확보하는 쪽을 택합니다(필자 판단입니다).
3. **비교할 시점 목록을 만듭니다.** 라이브 시스템에서는 `tmutil listlocalsnapshots` 와 `tmutil listlocalsnapshotdates`(생성 날짜를 `YYYY-MM-DD-HHMMSS` 로 표시), `tmutil listbackups -t`(이름 대신 시각만 표시) 를 쓰는데, 일부 명령에는 root 와 전체 디스크 접근 권한이 필요합니다 [1]. 사본 이미지에서는 APFS 스냅숏 메타데이터의 `create_time`(1970-01-01 UTC 기준 나노초)으로 생성 시각을 읽습니다 [4]. 스냅숏 이름 속 시각이 현지 시각인지 UTC 인지는 이번 자료로 확인하지 못해서 `create_time` 과 맞춰 보고 정합니다. 시각 값 읽는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md) 에서 봅니다.
4. **두 시점을 고릅니다.** 조사할 사건 시각 바로 앞과 바로 뒤의 시점을 한 쌍으로 잡고, 필요하면 쌍을 늘려 가며 변화가 처음 나타난 구간을 좁힙니다.
5. **시점마다 파일 목록을 뽑습니다.** 각 시점에서 경로, 크기, 파일 시스템 시각, 내용 해시를 한 줄씩 적은 목록을 만듭니다. 라이브 시스템에서는 `tmutil listbackups -m` 으로 백업을 마운트해 볼 수 있고, macOS 는 백업 디스크의 스냅숏을 숨은 폴더 `/Volumes/.timemachine` 아래에 마운트합니다 [1][3]. 사본 이미지에서 스냅숏을 여는 방법은 도구마다 지원 범위가 달라서 아래 도구 절을 봅니다.
6. **두 목록을 비교해 나눕니다.** 뒤 시점에만 있으면 추가, 앞 시점에만 있으면 삭제, 경로는 같은데 해시가 다르면 변경으로 나눕니다. 해시가 같은데 경로만 다른 항목은 이동이나 이름 변경 후보로 따로 표시합니다(필자 판단입니다). 라이브 시스템에서 현재 상태와 백업을 비교할 때는 `tmutil compare` 를 쓸 수 있고 `-X` 로 XML 출력을 받습니다 [1].
7. **다른 기록과 맞춰 봅니다.** 타임 머신은 백업할 변경 파일을 정할 때 FSEvents 를 쓰는 단계가 있어서 [7], 비교 결과의 변경 구간을 [파일 시스템 이벤트 (FSEvents)](../../02-artifacts/filesystem/fsevents/index.md) 기록과 대조합니다. 두 시점 사이 변화를 시각 순서로 펼치는 일은 [타임라인 작성 (Timeline)](timeline/index.md) 으로 넘깁니다.
8. **결과를 기록합니다.** 비교한 두 시점의 이름과 생성 시각, 목록을 만든 도구와 버전, 해시 방식, 분류 기준을 함께 적습니다.

## 도구

라이브 시스템에서는 기본 명령 `tmutil` 이 백업·스냅숏 목록(`listbackups`, `listlocalsnapshots`, `listlocalsnapshotdates`), 현재 상태와 백업의 차이(`compare`), 지정 경로에만 있는 데이터 크기(`uniquesize`)를 보여 주고, HFS+ 머신 디렉터리에서는 `calculatedrift` 로 백업 사이 변화량을 계산합니다 [1]. 사본 이미지에서 APFS 스냅숏을 열어 파일 목록을 뽑는 공개 도구의 지원 범위는 이번에 확인하지 못했습니다. 도구를 고르기 전에 스냅숏이 있는 시험 이미지로 스냅숏을 읽는지, 어느 시점의 파일을 보여 주는지를 [도구 검증 (Tool Validation)](../reporting/tool-validation.md) 에 따라 확인합니다. 파일 목록끼리 비교하는 일은 해시를 계산하고 목록을 맞대는 일반 도구로 충분합니다.

## 함정과 한계

두 시점 사이에 생겼다가 사라진 파일은 비교 결과에 나오지 않습니다. 로컬 스냅숏이 한 시간 간격이면 그 사이의 짧은 활동은 빠질 수 있어서, 비교 결과는 FSEvents 나 통합 로그처럼 더 촘촘한 기록으로 메웁니다.

백업에 없는 파일이 원래 없었다는 뜻은 아닙니다. 타임 머신에는 항목을 따라다니는 스티키 제외, 고정 경로 제외, 볼륨 제외가 있고 `tmutil isexcluded` 로 제외 여부를 확인합니다 [1]. 진행 중인 백업에는 `.inprogress` 가 붙어서 [7], 이런 백업은 완료된 백업과 섞어 비교하지 않습니다.

로컬 스냅숏이 없다는 사실만으로 누군가 지웠다고 볼 수는 없습니다. 오래된 스냅숏과 공간이 부족할 때의 스냅숏은 자동으로 지워지고, 여유 공간이 적은 디스크에는 처음부터 저장하지 않기 때문입니다 [2]. 다만 백업 빈도를 "수동" 으로 바꾸거나 자동 백업을 끄면 몇 분 안에 로컬 스냅숏이 지워지고 [2] `tmutil deletelocalsnapshots`·`thinlocalsnapshots` 로도 지우거나 줄일 수 있어서 [1], 사라진 시점 앞뒤의 설정 변경과 명령 흔적을 함께 봅니다. 이 흐름은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md) 에서 다룹니다.

APFS 백업 디스크의 백업은 읽기 전용이라 백업 안의 항목 하나만 지울 수 없고 백업 전체를 지우는 것만 됩니다 [3]. 그래서 한 백업에서 파일 하나만 빠져 있다면 백업 안에서 골라 지운 결과보다 그 시점에 원본이 없었거나 제외됐을 가능성을 먼저 봅니다(필자 판단입니다).

macOS 11 이후 시스템 볼륨도 스냅숏으로 부팅해서 [6], 스냅숏 목록에 타임 머신과 무관한 스냅숏이 섞일 수 있습니다(필자 판단입니다). 이름으로 타임 머신 스냅숏을 가려 낸 뒤 비교합니다.

## 결과를 어떻게 해석하나

비교 결과는 "시점 A 의 스냅숏에는 이 파일이 이 상태로 있었고 시점 B 의 스냅숏에는 없다" 를 말해 줍니다. 파일이 두 시점 사이 언제 사라졌는지, 누가 지웠는지, 휴지통을 거쳤는지는 알려 주지 않아서 [지운 파일의 흔적 찾기 (Deleted File Traces)](../../04-scenarios/activity/deleted-file-traces.md) 의 흔적과 맞춰 좁힙니다. 스냅숏에 남은 옛 내용에서 특정 문자열을 찾을 때는 [콘텐츠 검색 (Content Search)](content-search.md) 을 씁니다.

보고서에는 "로컬 스냅숏 두 개(각 스냅숏 이름과 `create_time` 을 적음)를 비교한 결과, 앞 스냅숏에 있던 이 경로의 파일이 뒤 스냅숏에는 없다" 처럼 비교한 시점과 기준을 함께 적고, 삭제 시각은 두 스냅숏 사이의 구간으로만 씁니다. 보고서 형식은 [포렌식 보고서 (Forensic Report)](../reporting/forensic-report.md) 를 따릅니다.

## 참고 문헌

1. tmutil(8) 매뉴얼 페이지 (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/tmutil.8.html
2. Apple Support, About Time Machine local snapshots (102154) — https://support.apple.com/en-us/102154
3. The Eclectic Light Company, "What can you do with Time Machine backups on APFS?" (2022-07-19) — https://eclecticlight.co/2022/07/19/what-can-you-do-with-time-machine-backups-on-apfs/
4. Apple, Apple File System Reference (2020-06-22) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
5. Apple 지원, macOS 사용 설명서 "Types of disks you can use with Time Machine" — https://support.apple.com/guide/mac-help/types-of-disks-you-can-use-with-time-machine-mh15139/mac
6. Apple Platform Security, Role of Apple File System (2024-12-19) — https://support.apple.com/guide/security/role-of-apple-file-system-seca6147599e/web
7. The Eclectic Light Company, "Going beyond T2M2 with Mints: grokking Time Machine to APFS" (2021-09-29) — https://eclecticlight.co/2021/09/29/going-beyond-t2m2-with-mints-grokking-time-machine-to-apfs/
