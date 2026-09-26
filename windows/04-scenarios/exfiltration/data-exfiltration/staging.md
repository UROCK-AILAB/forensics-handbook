---
title: "퇴사 전 자료를 모으고 압축했나"
parent: "자료를 밖으로 빼돌렸나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 3660
---

# 퇴사 전 자료를 모으고 압축했나 (Staging)

> 상위 허브: [자료를 밖으로 빼돌렸나 (Data Exfiltration)](index.md)

이 페이지는 자료를 밖으로 내보내기 전에 한 폴더에 모으거나 압축 파일 하나로 묶었는지 확인하는 순서를 다룹니다. 모으고 묶은 흔적은 USB·메일·클라우드 같은 내보내기 흔적과 이어서 봅니다. 압축 프로그램별 기록의 위치와 구조는 [압축 프로그램 사용 기록](../../../02-artifacts/file-folder-usage/7-zip-winrar-bandizip.md) 에서 다룹니다.

## ATT&CK 에서 보는 모으기

이 단계는 MITRE ATT&CK 의 데이터 모아 두기 (T1074 Data Staged) 에 해당합니다. 유출하기 전에 모은 데이터를 한 위치나 폴더에 모아 두는 일입니다[1]. 모은 파일은 따로따로 둘 수도 있고, 압축 같은 방법으로 한 파일로 합칠 수도 있습니다[1].

| 하위 기법 | 모으는 곳 |
|---|---|
| T1074.001 Local Data Staging | 조사 대상 시스템 안 |
| T1074.002 Remote Data Staging | 클라우드나 원격 위치 |

(표는 [1])

이 기법을 드러내는 파일 작업으로는 민감한 파일을 임시 폴더나 공용 폴더에 모으기, 7zip·WinRAR 로 압축하기, 유출 전에 한꺼번에 복사하기가 있습니다[1].

원격 위치에 모았다면 [클라우드로 밖에 보냈나](cloud.md) 와 [웹메일·웹하드로 올렸나](web-upload.md) 를 함께 봅니다.

## 조사 질문

- 퇴사를 앞둔 기간에 여러 자료를 한 폴더로 모은 흔적이 있습니까?
- 모은 자료를 압축 파일로 묶었습니까? 어떤 프로그램이나 명령으로 묶었습니까?
- 모은 폴더나 압축 파일을 나중에 지웠습니까?

## 먼저 확인할 것

| 확인할 것 | 이유 |
|---|---|
| 조사 기간 | 퇴사일, 사직 의사를 밝힌 날 같은 기준일을 받아 조사 기간을 정합니다. |
| 사용자 | WinRAR 의 압축 파일 기록은 사용자 하이브(NTUSER.DAT)에 있습니다[2]. 사용자마다 따로 봅니다. |
| 설치된 압축 프로그램 | [설치 프로그램](../../../02-artifacts/system-account/uninstall.md) 에서 찾고, `HKCU\Software` 아래에 7-Zip·WinRAR·Bandizip 키가 있는지도 봅니다. |
| 로그 설정 | 명령줄로 압축한 흔적은 프로세스 생성·Sysmon·PowerShell 로그가 켜져 있을 때만 이벤트로 남습니다([감사 정책과 로그 설정](../../../02-artifacts/event-logs/audit-policy-log-settings.md)). |
| 시간대 | 파일 시스템 시각과 레지스트리 시각을 같은 기준으로 맞춥니다([시간대 설정](../../../02-artifacts/system-account/time-zone.md)). |
| 수집 범위 | $MFT, $UsnJrnl:$J, 사용자 하이브, 이벤트 로그, 휴지통, 섀도 복사본을 확보합니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | $MFT·$UsnJrnl | 한 폴더에 파일이 몰려 만들어진 시각, 압축 파일이 생긴 시각, 지운 기록 | [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md), [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) |
| 2 | 압축 프로그램 기록 | 만들거나 연 압축 파일의 경로 | [압축 프로그램 사용 기록](../../../02-artifacts/file-folder-usage/7-zip-winrar-bandizip.md) |
| 3 | 프로세스 생성·Sysmon·PowerShell 기록 | 명령줄 압축 도구를 실행한 흔적 | [프로세스 생성](../../../02-artifacts/event-logs/4688.md), [Sysmon 로그](../../../02-artifacts/event-logs/sysmon/index.md), [PowerShell 실행 기록](../../../02-artifacts/event-logs/powershell-event-logs-4103-4104.md), [PowerShell 명령 기록](../../../02-artifacts/execution/consolehost-history-txt.md) |
| 4 | 셸백·바로가기 파일·점프리스트·최근 문서 | 모은 폴더를 연 흔적, 원본 파일을 연 흔적 | [셸백](../../../02-artifacts/file-folder-usage/shellbags/index.md), [바로가기 파일](../../../02-artifacts/file-folder-usage/lnk.md), [점프리스트](../../../02-artifacts/file-folder-usage/jump-lists.md), [최근 문서](../../../02-artifacts/file-folder-usage/recentdocs.md) |
| 5 | 윈도 타임라인 | 파일과 앱을 쓴 흐름 | [윈도 타임라인](../../../02-artifacts/file-folder-usage/activitiescache-db.md) |
| 6 | 휴지통·섀도 복사본 | 지운 모음 폴더나 압축 파일 | [휴지통](../../../02-artifacts/file-folder-usage/recycle-bin.md), [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

## 모은 흔적

- 여러 파일을 짧은 시간에 한 폴더로 복사했다면, 그 폴더의 파일 생성 기록이 한 시간대에 몰려 있는지 $MFT·$UsnJrnl 에서 봅니다.
- 모은 파일이 어디서 왔는지는 [이 파일은 어디서 왔나](../../activity/file-origin.md) 순서로 원본과 잇습니다. 모은 폴더를 탐색기로 연 흔적은 셸백에서, 폴더 안 파일을 연 흔적은 바로가기 파일·점프리스트·최근 문서에서 찾습니다.

**$UsnJrnl:$J 를 뽑을 때.**

$UsnJrnl:$J 는 앞부분이 빈 희소 스트림 (Sparse Stream) 이라서 뽑는 방식에 따라 크기와 해시가 달라집니다. 보고서에는 어떤 방식으로 뽑았는지 적습니다.

## 압축한 흔적

### 압축 프로그램 기록

WinRAR 는 NTUSER.DAT 의 `Software\WinRAR\ArcHistory` 키 값에 보관 파일 경로 기록을 남깁니다[2]. RegRipper 플러그인 winrar.pl 로 이 키의 마지막 기록 시각과 키 안의 모든 값을 값 이름 순서로 뽑을 수 있습니다[2].

키의 마지막 기록 시각은 키 하나에 하나뿐이라서 값 하나하나가 언제 적혔는지는 이 시각으로 알 수 없습니다([레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)).
winrar.pl 은 ArcHistory 키만 읽습니다[2]. WinRAR 의 다른 기록 키와 7-Zip·반디집·알집의 기록 위치는 [압축 프로그램 사용 기록](../../../02-artifacts/file-folder-usage/7-zip-winrar-bandizip.md) 에서 다룹니다.

### 윈도에 들어 있는 도구로 압축

Windows 11 Home 25H2(빌드 26200.9457)에는 `C:\Windows\System32\tar.exe` 가 들어 있고, 버전은 bsdtar 3.8.8 입니다. libarchive 3.8.8 에 liblzma·zstd 가 함께 들어 있습니다. 따로 설치한 압축 프로그램이 없어도 명령줄로 압축 파일을 만들 수 있습니다.

tar.exe 가 들어 있는지, 탐색기 자체의 압축 기능이 어떤지는 윈도 판마다 다를 수 있어 분석 대상 PC 에서 확인합니다.

명령줄 압축은 프로세스 생성(4688)·Sysmon 1·PowerShell 기록으로 보며, 해당 로그 설정이 켜져 있을 때만 남습니다. 4688 에 명령줄이 함께 남으려면 프로세스 생성 감사와 별도로 명령줄 기록 설정도 켜져 있어야 합니다([프로세스 생성](../../../02-artifacts/event-logs/4688.md)).
- tar.exe 같은 도구를 실행한 흔적 전반은 [어떤 프로그램을 언제 실행했나](../../activity/program-execution.md) 순서로 찾습니다.

## 지운 흔적

퇴사 전에 모은 폴더나 압축 파일을 지웠을 수 있으므로 휴지통, $UsnJrnl 의 삭제 기록, 섀도 복사본을 봅니다. 지운 파일을 찾는 순서는 [지운 파일의 흔적 찾기](../../activity/deleted-file-traces.md) 에서 다룹니다.

지우기 도구를 쓰거나 로그를 지웠는지는 [증거를 없애려 했나](../../activity/anti-forensics/index.md) 에서 봅니다.

## 분석 흐름

1. 기준일로 조사 기간을 정하고, 사용자와 시간대를 확인합니다.
2. $MFT·$UsnJrnl 에서 조사 기간의 파일 생성 기록을 폴더별로 셉니다. 생성 기록이 짧은 시간에 몰린 폴더를 찾습니다.
3. 그 폴더에 만들어진 파일을 원본 위치의 파일과 이름·크기·해시로 맞춥니다([해시셋 대조와 유사 해시](../../../03-techniques/analysis/hash-set-fuzzy-hash.md)).
4. 조사 기간에 생긴 압축 파일을 찾고, 만든 시각과 경로를 적습니다.
5. 사용자 하이브의 압축 프로그램 기록에 그 압축 파일 경로가 있는지 봅니다.
6. 압축 프로그램 기록이 없으면 tar.exe 같은 명령줄 도구를 실행한 흔적을 4688·Sysmon·PowerShell 기록에서 찾습니다.
7. 압축 파일이나 모은 폴더가 이후 밖으로 나갔는지 다른 하위 페이지로 이어 봅니다.
8. 모은 폴더나 압축 파일을 지웠다면 휴지통·$UsnJrnl·섀도 복사본에서 지운 시각과 이름을 찾습니다.
9. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리합니다.

## 흔한 오판

1. **압축 프로그램 키가 없으니 압축하지 않았다고 봅니다.** 압축 프로그램이 없어도 tar.exe 같은 윈도 도구가 있을 수 있습니다.
2. **ArcHistory 키의 마지막 기록 시각을 모든 값의 시각으로 씁니다.** 이 시각은 키 하나에 하나입니다. 가장 최근에 바뀐 때만 알려 줍니다.
3. **파일이 한 폴더에 모였으니 유출 준비라고 단정합니다.** 백업이나 업무 인수인계로 모았을 수 있습니다. 모은 뒤 무엇을 했는지 이어서 봅니다.
4. **모은 흔적을 유출 증거로 씁니다.** 모은 것과 밖으로 내보낸 것은 다릅니다. 내보낸 흔적은 다른 하위 페이지에서 따로 찾습니다.
5. **$UsnJrnl:$J 해시가 다르다고 증거가 바뀌었다고 봅니다.** 뽑는 방식이 다르면 해시가 달라질 수 있습니다. 뽑은 방식부터 맞춥니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 퇴사 전에 영업 자료를 몰래 모아 압축했습니다."
- 쓸 문장: "$UsnJrnl 에는 ○○(UTC) 부터 ○분 동안 ○○ 폴더에 파일 ○개를 만든 기록이 있습니다. 같은 날 ○○(UTC) 에 압축 파일 ○○ 를 만든 기록이 있습니다. 사용자 ○○ 의 NTUSER.DAT 에서 WinRAR ArcHistory 값에 이 압축 파일 경로가 있습니다. 이 기록은 그 기간에 파일이 한 폴더에 모였고, 같은 경로의 압축 파일이 WinRAR 기록에 남았음을 보여 줍니다. 압축 파일이 밖으로 나갔는지는 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [압축 프로그램 사용 기록](../../../02-artifacts/file-folder-usage/7-zip-winrar-bandizip.md) — 압축 프로그램별 기록 위치와 구조입니다.
- [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md) · [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) — 파일을 만들고 지운 시각입니다.
- [프로세스 생성](../../../02-artifacts/event-logs/4688.md) · [Sysmon 로그](../../../02-artifacts/event-logs/sysmon/index.md) · [PowerShell 실행 기록](../../../02-artifacts/event-logs/powershell-event-logs-4103-4104.md) · [PowerShell 명령 기록](../../../02-artifacts/execution/consolehost-history-txt.md) — 명령줄로 압축한 흔적입니다.
- [셸백](../../../02-artifacts/file-folder-usage/shellbags/index.md) · [바로가기 파일](../../../02-artifacts/file-folder-usage/lnk.md) · [점프리스트](../../../02-artifacts/file-folder-usage/jump-lists.md) · [최근 문서](../../../02-artifacts/file-folder-usage/recentdocs.md) · [윈도 타임라인](../../../02-artifacts/file-folder-usage/activitiescache-db.md) — 폴더와 파일을 연 흔적입니다.
- [휴지통](../../../02-artifacts/file-folder-usage/recycle-bin.md) · [볼륨 섀도 복사본 구조](../../../01-foundations/disk-volume/volume-shadow-copy.md) · [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 지운 모음 폴더와 압축 파일입니다.
- [지운 파일의 흔적 찾기](../../activity/deleted-file-traces.md) · [증거를 없애려 했나](../../activity/anti-forensics/index.md) — 퇴사 전 정리 흔적입니다.
- [USB 로 무엇을 가져갔나 (USB)](usb.md) · [클라우드로 밖에 보냈나 (Cloud)](cloud.md) · [웹메일·웹하드로 올렸나 (Web Upload)](web-upload.md) — 모은 자료를 내보낸 경로입니다.

## 참고 문헌

1. MITRE ATT&CK, "Data Staged" (T1074) — https://attack.mitre.org/techniques/T1074/
2. Harlan Carvey, RegRipper 3.0 플러그인 winrar.pl — https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/winrar.pl
