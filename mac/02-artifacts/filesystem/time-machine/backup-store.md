---
title: "백업 저장소 구조"
parent: "타임 머신"
grand_parent: "아티팩트 · 파일 시스템"
nav_order: 1020
---

# 백업 저장소 구조 (Backup Store)

타임 머신 백업 디스크는 HFS+ 형식이면 `Backups.backupdb` 아래에 파일·폴더·하드 링크로 백업을 쌓고, APFS 형식이면 디스크 루트에 읽기 전용 스냅숏을 백업 하나씩 두며, 백업하는 볼륨에는 따로 로컬 스냅숏이 남습니다.

## 무엇을 기록하나 · 왜 생기나

타임 머신 백업은 두 곳에 남습니다. 백업하는 볼륨마다 만드는 로컬 스냅숏 (local snapshot)이 한 곳이고, 백업 저장장치에 쌓이는 백업 본체가 다른 한 곳입니다 [4]. 백업 본체는 백업한 시점의 파일 상태를 그대로 담아서, 지금 Mac에서 지워졌거나 바뀐 파일의 예전 모습을 볼 수 있는 자리입니다. 이 페이지는 두 곳의 이름과 구조를 다루고, 백업을 언제 했는지와 무엇을 뺐는지를 알려 주는 설정·로그는 [백업 설정과 기록 (Settings·Logs)](settings-logs.md)에서 다룹니다.

## 위치와 버전별 차이

Apple은 백업 디스크 형식으로 APFS와 APFS(암호화)를 권하지만, Mac OS 확장(저널링), Mac OS 확장(대소문자 구분, 저널링), Xsan 형식도 여전히 지원합니다 [3]. APFS가 아닌 새 디스크를 고르면 지우고 다시 포맷할지 묻지만, 이미 Mac OS 확장 형식의 타임 머신 백업이 들어 있는 디스크면 묻지 않습니다 [3]. 그래서 조사하는 백업 디스크가 HFS+ 형식의 옛 구조일 수도 있고 APFS 형식의 스냅숏 구조일 수도 있어서, 디스크 형식부터 확인하고 아래 표에서 맞는 열을 봅니다.

| 구분 | HFS+ 백업 디스크 (옛 구조) | APFS 백업 디스크 (스냅숏 구조) |
|---|---|---|
| 백업 저장소 | 디스크 루트의 최상위 디렉터리 `Backups.backupdb` (매뉴얼 예: `/Volumes/Chronoton/Backups.backupdb`) [1] | 이 구조가 없음 [1] |
| 머신 디렉터리 | 한 컴퓨터의 백업을 모두 담는 디렉터리 [1] | 백업 디스크의 루트가 머신 디렉터리 노릇을 함 [1] |
| 백업 하나의 이름 | 시각 형식, 예: `2011-07-03-123456` [1] | `com.apple.TimeMachine.YYYY-MM-DD-HHMMSS.backup`, 예: `com.apple.TimeMachine.2011-07-03-123456.backup` [1] |
| 백업 하나의 모습 | 파일·폴더·하드 링크로 짠 디렉터리 [4] | 읽기 전용 합성 스냅숏 (synthetic snapshot) [4] |
| 진행 중인 백업 | 이번 자료로 확인하지 못함 | 이름에 `.inprogress` 확장자가 붙음 [5] |
| 백업 사이 변화량 계산 | `tmutil calculatedrift`로 계산 [1] | 매뉴얼에 HFS 한정으로 적혀 있어 쓰지 않음 [1] |

OS X 10.11부터 타임 머신이 백업에 복사한 파일의 체크섬을 기록하고 그 전 버전이 복사한 파일은 거슬러 계산하지 않는데 [1], 체크섬 값을 어디에 어떤 형식으로 두는지는 이번 자료로 확인하지 못했습니다. APFS 백업의 동작은 [5]가 Big Sur와 Monterey에서, [2]가 Sonoma와 Sequoia에서 관찰한 내용이고, APFS 백업이 정확히 어느 버전부터인지는 여기서 단정하지 않습니다.

로컬 스냅숏은 백업하는 APFS 볼륨에 남는 볼륨 스냅숏이고 [1], 보통 24시간 뒤에 지워집니다 [4]. 이름은 `com.apple.TimeMachine.YYYY-MM-DD-HHMMSS.local` 형식이고(예: `com.apple.TimeMachine.2011-07-03-123456.local`) [1][5], 백업 디스크 쪽 이름과 끝의 `.local` / `.backup`만 다릅니다.

백업 대상은 연결한 디스크뿐 아니라 AirPort Time Capsule이나 SMB·AFP로 타임 머신을 지원하는 NAS일 수도 있고, Apple은 둘 중 SMB를 권합니다 [3]. 네트워크 백업이 어떤 디스크 이미지 이름과 구조로 남는지는 이번 자료로 확인하지 못했고, 디스크 이미지 형식 일반은 [디스크 이미지 형식 (DMG·Sparsebundle)](../../../01-foundations/disk-volume/dmg-sparsebundle.md)에서 다룹니다.

## 구조

HFS+ 백업은 파일·폴더·하드 링크로 이뤄진 디렉터리 트리라서 [4] 백업 이름 폴더를 열어 그 시점의 파일을 볼 수 있습니다. HFS+ 볼륨 구조는 [HFS+ 구조 (HFS+)](../../../01-foundations/disk-volume/hfs-plus.md)를 봅니다.

APFS 백업은 백업 하나가 스냅숏 하나이고 읽기 전용이라서, 백업 안의 항목 하나만 골라 지울 수 없고 백업 전체를 지우는 것만 됩니다 [4]. 백업 전체를 지우는 길은 Finder, 디스크 유틸리티의 스냅숏 목록, 그리고 다음 명령입니다 [4].

```
tmutil delete -d <백업 저장소> -t <백업 시각>
```

macOS는 백업 저장장치의 스냅숏을 숨은 폴더 `/Volumes/.timemachine` 아래에 마운트해서 보여 줍니다 [4]. APFS 볼륨 구조는 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md)에서 다룹니다.

> 그림 자리: HFS+ 백업 디스크(`Backups.backupdb` → 머신 디렉터리 → 시각 이름 폴더)와 APFS 백업 디스크(루트 → `.backup` 스냅숏 여러 개), 원본 볼륨의 `.local` 스냅숏을 나란히 놓은 그림

## 증거로서 의미

**증명하는 것.** 백업 하나에 어떤 파일이 들어 있으면 그 백업을 만들 무렵 백업 대상 볼륨에 그 경로와 내용의 파일이 있었다는 기록입니다. 백업 여러 개를 시각 순으로 놓으면 파일이 처음 보인 백업과 마지막으로 보인 백업 사이로 생긴 때와 사라진 때의 범위를 좁힐 수 있고, 지금 Mac에서는 지워진 파일의 내용을 되찾을 수도 있습니다.

**증명하지 못하는 것.** 백업은 백업 순간의 상태만 담아서 백업과 백업 사이에 잠깐 있다가 사라진 파일은 남지 않고, 누가 파일을 만들거나 열었는지도 알려 주지 않습니다. 제외 항목으로 뺀 경로는 백업에 없으니, 백업에 없다는 사실만으로 그 파일이 없었다고 쓰지 않습니다. 제외 설정은 [백업 설정과 기록 (Settings·Logs)](settings-logs.md)에서 확인합니다.

보고서에는 "파일을 만들었다" 가 아니라 "`com.apple.TimeMachine.2011-07-03-123456.backup` 백업에 이 경로의 파일이 이 크기로 들어 있다" 처럼 백업이 말하는 만큼만 씁니다(이 문장의 이름은 매뉴얼 예시입니다).

## 시각 해석

백업 이름과 로컬 스냅숏 이름에 든 `YYYY-MM-DD-HHMMSS`는 백업을 만든 시각이고, `tmutil listlocalsnapshotdates`도 로컬 스냅숏 생성 날짜를 같은 형식으로 보여 줍니다 [1]. 이 시각이 현지 시각인지 UTC인지는 이번 자료로 확인하지 못해서, 같은 백업을 가리키는 로그 기록이나 설정 파일의 날짜와 맞춰 본 뒤에 시간대를 정합니다. 백업 안 파일의 수정 시각은 원래 파일의 값이라서 백업 이름의 시각과 따로 읽고, 두 값을 섞어 "이때 고쳤다" 고 쓰지 않습니다. 맥 시각 값의 여러 형식은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)을 봅니다.

## 함정과 한계

APFS 백업 디스크의 스냅숏은 다른 곳으로 복사하거나 옮길 방법이 없다고 적혀 있어서(2022년 글 기준) [4], 파일 몇 개만 골라 복사하면 스냅숏 구조를 잃습니다. 필자 판단으로는 백업 디스크 전체를 이미징하는 쪽이 현실적이고, 절차는 [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)를 따릅니다.

안티포렌식 쪽에서는 지우는 단위를 봅니다. APFS 백업은 항목 하나를 지울 수 없어서 [4] 백업을 통째로 지운 흔적은 백업 이름의 시각 순서가 비는 자리로 드러날 수 있고(필자 판단), 로컬 스냅숏은 `tmutil deletelocalsnapshots`로 지우거나 `tmutil thinlocalsnapshots`로 공간을 회수할 수 있습니다 [1]. 다만 로컬 스냅숏은 보통 24시간 뒤에 저절로 지워지니 [4] 로컬 스냅숏이 적다는 사실만으로 누가 지웠다고 보지 않고, 백업 디스크의 백업 목록과 로그를 함께 봅니다.

`tmutil`의 여러 명령은 root 권한과 전체 디스크 접근 권한(Full Disk Access)이 있어야 돌아갑니다 [1]. 증거 원본에 지우기·솎기 명령을 쓰면 증거가 바뀌니, 원본 디스크에는 조회 명령만 씁니다.

## 직접 분석해 보기

백업 저장소는 바이너리 레코드가 아니라 디렉터리 이름과 스냅숏 이름으로 짜여 있어서, 헥스로 따라가기보다 이름과 목록을 읽는 쪽이 맞습니다. APFS 볼륨을 헥스로 읽는 법은 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md)에서 다룹니다.

공개 도구로는 macOS에 들어 있는 `tmutil`을 씁니다 [1]. 아래는 조회 명령만 모은 것이고, 분석용 Mac에 백업 디스크 사본을 읽기 전용으로 붙인 상태를 가정합니다.

| 명령 | 알려 주는 것 |
|---|---|
| `tmutil listbackups` | 백업 목록. `-d`(대상 볼륨)·`-m`(백업 마운트)·`-t`(시각만 출력) 옵션이 있음 [1] |
| `tmutil latestbackup` | 가장 최근 백업 [1] |
| `tmutil machinedirectory` | 현재 컴퓨터의 머신 디렉터리 경로 [1] |
| `tmutil listlocalsnapshots` / `tmutil listlocalsnapshotdates` | 로컬 스냅숏 목록과 생성 날짜 [1] |
| `tmutil compare` | 현재 시스템과 백업의 차이. `-X`로 XML 출력 [1] |
| `tmutil uniquesize` | 지정한 경로가 백업 안에서 따로 차지하는 크기(HFS+·APFS 백업 모두) [1] |
| `tmutil calculatedrift` | HFS 머신 디렉터리의 백업 사이 변화량 [1] |

백업끼리 또는 백업과 현재 시스템을 비교해 사라진 파일과 바뀐 파일을 골라내는 절차는 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../../03-techniques/analysis/snapshot-diff.md)에서 다룹니다.

## 교차 검증

- [백업 설정과 기록 (Settings·Logs)](settings-logs.md) — 설정 파일의 백업 시각 목록과 로그의 완료 기록을 백업 이름과 맞춰 봅니다.
- [파일 시스템 이벤트 (FSEvents)](../fsevents/index.md) — 백업 사이에 바뀐 경로를 찾을 때
- [휴지통 (.Trash)](../../file-folder-usage/trash.md) — 지운 파일이 백업에 남아 있는지 볼 때
- [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)

## 실습

공개 검체나 직접 백업을 만든 실습용 Mac에서 다음을 풀어 봅니다.

1. 백업 디스크가 HFS+ 형식인지 APFS 형식인지 확인하고, 그에 맞는 머신 디렉터리 위치를 찾습니다.
2. 백업 이름을 시각 순으로 늘어놓고 간격이 유난히 긴 자리를 찾은 뒤, 로그나 설정 파일로 그 사이에 백업이 있었는지 확인합니다.
3. 지금 Mac에 없는 파일 하나를 골라 그 파일이 들어 있는 첫 백업과 마지막 백업을 찾고, 보고서 문장으로 적어 봅니다.

## 참고 문헌

1. tmutil(8) 매뉴얼 페이지 (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/tmutil.8.html
2. The Eclectic Light Company, "Understand and check Time Machine backups to APFS" (2024-10-03) — https://eclecticlight.co/2024/10/03/understand-and-check-time-machine-backups-to-apfs/
3. Apple 지원, macOS 사용 설명서 "Types of disks you can use with Time Machine" — https://support.apple.com/guide/mac-help/types-of-disks-you-can-use-with-time-machine-mh15139/mac
4. The Eclectic Light Company, "What can you do with Time Machine backups on APFS?" (2022-07-19) — https://eclecticlight.co/2022/07/19/what-can-you-do-with-time-machine-backups-on-apfs/
5. The Eclectic Light Company, "Going beyond T2M2 with Mints: grokking Time Machine to APFS" (2021-09-29) — https://eclecticlight.co/2021/09/29/going-beyond-t2m2-with-mints-grokking-time-machine-to-apfs/
