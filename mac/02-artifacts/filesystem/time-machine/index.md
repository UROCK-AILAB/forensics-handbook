---
title: "타임 머신"
parent: "아티팩트 · 파일 시스템"
nav_order: 1010
has_children: true
has_toc: false
---

# 타임 머신 (Time Machine)

타임 머신 (Time Machine)은 macOS에 들어 있는 백업 기능이고, 백업 디스크에 쌓인 지난 시점의 파일과 설정 파일·통합 로그에 남은 백업 기록을 함께 보면 지금은 없는 파일의 예전 모습과 그 파일이 언제까지 있었는지를 좁힐 수 있습니다.

## 왜 중요한가

타임 머신 백업은 백업하는 볼륨마다 만드는 로컬 스냅숏 (local snapshot)과 백업 저장장치에 쌓이는 백업 본체, 두 곳에 남습니다 [4]. Sonoma·Sequoia에서 로컬 APFS 저장장치로 하는 자동 백업은 한 시간마다 돌고 [2], 백업 본체에는 사용자가 지운 파일이나 고치기 전 문서가 시점별로 남아 있을 수 있습니다. 조사에서는 지운 파일을 되찾는 자리이면서, 백업 이름과 백업 기록으로 파일이 있었던 기간을 확인하는 자리이기도 합니다.

해석할 때는 백업 디스크의 형식부터 봅니다. Apple은 APFS 형식을 권하지만 Mac OS 확장(HFS+) 형식 백업도 여전히 지원해서 [3], 조사하는 백업 디스크가 옛 디렉터리 구조일 수도 있고 스냅숏 구조일 수도 있습니다. 백업은 백업 순간의 상태만 담고 제외 항목으로 뺀 경로는 담지 않아서, 백업에 없다는 사실만으로 파일이 없었다고 쓰지 않습니다.

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 위치 | 백업 디스크(HFS+ 형식이면 `Backups.backupdb`, APFS 형식이면 디스크 루트의 `.backup` 스냅숏) [1], 백업하는 볼륨의 `.local` 로컬 스냅숏 [1], 설정 파일 `com.apple.TimeMachine.plist` [5], 통합 로그 |
| 백업 대상 | 연결한 디스크, AirPort Time Capsule, SMB·AFP로 타임 머신을 지원하는 NAS [3] |
| macOS 버전 | macOS 10.15 Catalina 이후 [3]. APFS 백업 동작은 Big Sur·Monterey와 Sonoma·Sequoia 기준(하위 페이지 참고) |
| 알려 주는 것 | 백업 시점의 파일 내용, 백업한 시각 목록, 백업 대상 이름, 백업 시작·완료 기록, 제외 항목 |
| 알려 주지 않는 것 | 백업과 백업 사이에 잠깐 있던 파일, 누가 파일을 만들거나 열었는지, 제외한 경로의 내용 |
| 공개 도구 | macOS의 `tmutil`(여러 명령에 root 권한과 전체 디스크 접근 권한이 필요) [1], plaso 타임 머신 plist 플러그인 [5] |

## 읽는 순서

1. [백업 저장소 구조 (Backup Store)](backup-store.md) — HFS+와 APFS 백업 디스크의 구조와 백업 이름, 로컬 스냅숏, 지우는 단위와 수집할 때의 주의점을 다룹니다.
2. [백업 설정과 기록 (Settings·Logs)](settings-logs.md) — 설정 파일의 백업 대상·백업 시각, 제외 항목, 통합 로그에 남는 백업 단계와 문구를 다룹니다.

## 함께 볼 페이지

- [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md) — 백업과 로컬 스냅숏이 올라가는 볼륨 구조
- [HFS+ 구조 (HFS+)](../../../01-foundations/disk-volume/hfs-plus.md) — 옛 형식 백업 디스크를 읽을 때
- [파일 시스템 이벤트 (FSEvents)](../fsevents/index.md) — 백업 사이에 바뀐 경로를 찾을 때
- [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../../03-techniques/analysis/snapshot-diff.md) — 백업끼리 비교하는 절차
- [맥 증거 확보 (Acquisition)](../../../03-techniques/process-acquisition/evidence-acquisition/index.md) — 백업 디스크를 수집할 때
- [지운 파일의 흔적 찾기 (Deleted File Traces)](../../../04-scenarios/activity/deleted-file-traces.md)
- [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md)
- [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)

## 참고 문헌

1. tmutil(8) 매뉴얼 페이지 (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/tmutil.8.html
2. The Eclectic Light Company, "Understand and check Time Machine backups to APFS" (2024-10-03) — https://eclecticlight.co/2024/10/03/understand-and-check-time-machine-backups-to-apfs/
3. Apple 지원, macOS 사용 설명서 "Types of disks you can use with Time Machine" — https://support.apple.com/guide/mac-help/types-of-disks-you-can-use-with-time-machine-mh15139/mac
4. The Eclectic Light Company, "What can you do with Time Machine backups on APFS?" (2022-07-19) — https://eclecticlight.co/2022/07/19/what-can-you-do-with-time-machine-backups-on-apfs/
5. plaso Time Machine plist 플러그인 소스 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/plist_plugins/time_machine.py
