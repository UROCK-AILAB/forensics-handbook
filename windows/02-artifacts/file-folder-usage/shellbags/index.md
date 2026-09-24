---
title: "셸백"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1150
has_children: true
has_toc: false
---

# 셸백 (ShellBags)

## 한 줄 요약

셸백 (ShellBags) 은 탐색기 (File Explorer) 가 폴더마다 보기 설정을 기억하려고 사용자 레지스트리에 남기는 기록입니다. 보기 설정과 함께 그 폴더를 가리키는 셸 아이템 (Shell Item) 이 남습니다. 그래서 사용자가 탐색기로 들어가 본 폴더 경로를 되살릴 수 있습니다.

## 왜 중요한가

탐색기는 폴더 창의 크기·위치·아이콘 보기 방식을 폴더마다 기억하는데, 이 설정을 담는 곳이 셸백입니다. 셸백은 설정을 찾아가려고 폴더 경로도 저장하며, 경로는 셸 아이템을 한 단계씩 이어 붙인 모양으로 남습니다.

셸백은 사용자마다 따로 있는 하이브(NTUSER.DAT·UsrClass.dat)에 남으므로 어느 사용자 프로필에서 탐색한 기록인지 나뉩니다. 폴더를 지워도 셸백 항목은 함께 지워지지 않아서 지금 디스크에 없는 폴더도 찾을 수 있고, 떼어 낸 USB 저장장치, 휴대용 장치(MTP), 네트워크 공유, ZIP 파일 안의 폴더도 셸 아이템으로 남습니다.

셸 아이템에는 폴더의 만든 시각·수정 시각·접근 시각이 들어 있는데, 이 값은 셸백 항목을 처음 만들 때 파일시스템에서 옮겨 적은 값입니다. Vista 이후의 셸 아이템에는 폴더의 NTFS 파일 참조(MFT 번호·순번) 칸도 있어서 [$MFT](../../filesystem/mft.md) 의 레코드와 맞춰 볼 수 있습니다.

셸백으로 증명하지 못하는 것은 아래와 같습니다.

- 셸 아이템 속 시각은 폴더를 연 시각이 아닙니다. 폴더를 다시 열어도 이 값은 바뀌지 않습니다. (확인 범위: Windows 7, 4n6k 시험)
- 셸 아이템 속 시각은 FAT 날짜·시각 형식이라 2초 단위로만 남습니다.
- 레지스트리 키의 마지막 기록 시각은 키마다 하나뿐입니다. 하위 폴더가 여럿이면 이 시각은 가장 최근에 고른 하위 폴더 하나에만 들어맞습니다.
- 처음 여는 폴더가 생기면 BagMRU 맨 위 키의 NodeSlots 값이 바뀌고 맨 위 키의 시각도 바뀌므로, 바로 아래 항목들이 모두 방금 열린 것처럼 보일 수 있습니다. (확인 범위: Windows 7, 4n6k 시험)
- 셸백은 폴더 단위 기록입니다. 폴더 안의 어떤 파일을 열었는지, 복사했는지는 남지 않습니다.
- 셸백은 윈도 셸 창의 보기 설정입니다. 명령줄에서 폴더를 옮겨 다닌 것은 남지 않습니다.
- 키의 마지막 기록 시각은 도구로 바꿀 수 있습니다. 셸 아이템 속 시각은 파일시스템의 시각과 맞춰 봅니다.

## 한눈에 보기

> 그림 자리: BagMRU 트리(숫자 이름 하위 키 하나가 폴더 경로 한 단계), 각 키 안의 숫자 값(셸 아이템)·MRUListEx·NodeSlot, 그리고 NodeSlot 번호로 이어지는 `Bags\<번호>` 보기 설정을 한 장에 보여 주는 그림

### 위치

| Windows 버전 | 하이브 파일 | 키 (하이브 맨 위 기준) |
|---|---|---|
| XP · 2003 | NTUSER.DAT | `Software\Microsoft\Windows\ShellNoRoam\BagMRU` · `Software\Microsoft\Windows\ShellNoRoam\Bags` |
| XP · 2003 | NTUSER.DAT | `Software\Microsoft\Windows\Shell\BagMRU` · `Software\Microsoft\Windows\Shell\Bags` |
| Vista 이후 | UsrClass.dat | `Local Settings\Software\Microsoft\Windows\Shell\BagMRU` · `Local Settings\Software\Microsoft\Windows\Shell\Bags` |
| Vista 이후 | NTUSER.DAT | `Software\Microsoft\Windows\Shell\BagMRU` · `Software\Microsoft\Windows\Shell\Bags` |

| 하이브 파일 | 위치 |
|---|---|
| NTUSER.DAT | `%UserProfile%\NTUSER.DAT` |
| UsrClass.dat (XP · 2003) | `%UserProfile%\Local Settings\Application Data\Microsoft\Windows\UsrClass.dat` |
| UsrClass.dat (Vista 이후) | `%UserProfile%\AppData\Local\Microsoft\Windows\UsrClass.dat` |

- 실행 중인 시스템에서는 UsrClass.dat 가 `HKEY_CURRENT_USER\Software\Classes` 아래에 붙습니다. 그래서 같은 키가 `HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\BagMRU` 로 보입니다.
- Vista 이후 검체는 UsrClass.dat 쪽을 먼저 봅니다. NTUSER.DAT 쪽 `Shell` 키도 빼놓지 않고 함께 봅니다.
- 하이브 파일의 쓰임새는 [하이브 파일 종류와 위치](../../../01-foundations/database-log-formats/registry-hive/system-software-sam-security-ntuser-dat-usrclass.md) 에서 다룹니다.

### Windows 버전에 따라 달라지는 점

폴더를 가리키는 셸 아이템에는 확장 블록 (Extension Block) 이 붙습니다. 만든 시각과 접근 시각은 서명이 `0xbeef0004` 인 확장 블록에 들어 있습니다. 이 블록의 버전은 Windows 버전에 따라 다릅니다. 아래 표는 libfwsi 명세를 따릅니다.

| Windows 버전 | 셸백이 있는 하이브 | `0xbeef0004` 블록 버전 | NTFS 파일 참조 칸 |
|---|---|---|---|
| XP · 2003 | NTUSER.DAT | 3 | 없음 |
| Vista (SP0) | UsrClass.dat · NTUSER.DAT | 7 | 있음 |
| 2008 · 7 · 8.0 | UsrClass.dat · NTUSER.DAT | 8 | 있음 |
| 8.1 · 10 | UsrClass.dat · NTUSER.DAT | 9 | 있음 |

- libfwsi 명세는 파일 참조 칸에 늘 파일 참조가 들어가는지는 아직 확인되지 않았다고 적습니다.
- Windows 11 의 블록 버전 값은 libfwsi 명세에 따로 적혀 있지 않습니다.
- 셸 아이템의 형식은 문서로 공개되지 않았습니다. 형식 설명은 [셸 아이템 (Shell Item·PIDL)](../../../01-foundations/shell-document-formats/shell-item-pidl.md) 에서 다룹니다.

### 시각 값

| 시각 | 어디에 남나 | 형식 | 언제 바뀌나 |
|---|---|---|---|
| 폴더 수정 시각 | 파일 항목 셸 아이템 | FAT 날짜·시각, 2초 단위 | 셸백 항목을 처음 만들 때 적고 그 뒤로 바뀌지 않음 |
| 폴더 만든 시각·접근 시각 | `0xbeef0004` 확장 블록 | FAT 날짜·시각, 2초 단위 | 위와 같음 |
| 키 마지막 기록 시각 | BagMRU 아래 각 하위 키 | FILETIME, UTC | 그 키의 값(MRUListEx·NodeSlots 등)이 바뀔 때 |

- libfwsi 명세는 셸 아이템의 FAT 날짜·시각을 UTC 로 적습니다.
- 키 시각을 읽는 법은 [키 마지막 기록 시각 (Last Write Time)](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md) 에서 다룹니다.

### 알려 주는 것

| 알 수 있는 것 | 어디에 남나 | 자세히 |
|---|---|---|
| 탐색기로 들어가 본 폴더 경로 | BagMRU 트리의 숫자 값(셸 아이템) | [저장 위치와 구조](ntuser-usrclass-bagmru-bags.md) |
| 같은 부모 폴더 안에서 최근에 고른 순서 | 각 키의 MRUListEx 값 | [저장 위치와 구조](ntuser-usrclass-bagmru-bags.md) |
| 폴더 창 크기·보기 방식 | `Bags\<번호>` 키 | [저장 위치와 구조](ntuser-usrclass-bagmru-bags.md) |
| 셸백 항목을 만들 때의 폴더 시각 | 파일 항목 셸 아이템, `0xbeef0004` 블록 | [셸백 시각 해석](timestamps.md) |
| 최근에 고른 하위 폴더가 바뀐 무렵 | 각 하위 키의 마지막 기록 시각 | [셸백 시각 해석](timestamps.md) |
| USB·휴대용 장치·네트워크 공유·ZIP 안 폴더 | 볼륨·MTP 장치·네트워크 위치·압축 폴더 셸 아이템 | [외부 장치·네트워크·압축 폴더](removable-network-zip.md) |
| 지금은 없는 폴더 | 셸백 경로와 지금 파일시스템의 차이, NTFS 파일 참조 | [지운 폴더 흔적 찾기](deleted-folders.md) |

## 읽는 순서

1. [저장 위치와 구조 (NTUSER·UsrClass·BagMRU·Bags)](ntuser-usrclass-bagmru-bags.md) — Windows 버전별 키 위치를 정리합니다. BagMRU 트리를 따라 경로를 이어 붙이는 법과 NodeSlot 으로 `Bags` 를 찾는 법도 다룹니다.
2. [셸백 시각 해석 (처음 연 때·마지막 바뀐 때)](timestamps.md) — 셸 아이템 속 시각과 키 시각을 나눠 읽습니다. 어떤 조건에서 "처음 연 때" 나 "마지막으로 고른 때" 로 읽을 수 있는지 다룹니다.
3. [외부 장치·네트워크·압축 폴더 탐색 흔적](removable-network-zip.md) — USB 볼륨, MTP 장치, 네트워크 공유, ZIP 파일 안 폴더의 셸 아이템을 읽습니다. 이 흔적을 장치 연결 기록과 잇는 법도 다룹니다.
4. [지운 폴더 흔적 찾기 (Deleted Folders)](deleted-folders.md) — 셸백 경로를 지금 파일시스템과 비교해 사라진 폴더를 찾습니다. 하이브 안에 남은 지운 셸백 키도 다룹니다.
5. [셸백 해석 함정 (Pitfalls)](pitfalls.md) — 셸 아이템 시각을 접근 시각으로 읽는 실수, 맨 위 키 시각이 바뀌는 경우, 키 시각 조작을 모읍니다.

## 함께 볼 페이지

- [셸 아이템 (Shell Item·PIDL)](../../../01-foundations/shell-document-formats/shell-item-pidl.md) — 셸백 값 하나하나를 이루는 형식입니다.
- [MRU 목록 읽는 법 (MRUList·MRUListEx)](../../../01-foundations/database-log-formats/registry-hive/mrulist-mrulistex.md) — BagMRU 키마다 있는 순서 목록을 읽습니다.
- [트랜잭션 로그와 반영 안 된 변경 (.LOG1·.LOG2)](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md) · [지워진 키·값 복구 (Deleted Keys·Values)](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md) — 하이브 본문에 아직 없거나 이미 지워진 셸백 항목을 찾습니다.
- [바로가기 파일 (LNK)](../lnk.md) · [점프리스트 (Jump Lists)](../jump-lists.md) — 같은 셸 아이템 형식으로 파일 단위 열람을 남깁니다.
- [열기·저장 대화상자 기록 (ComDlg32)](../comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) · [최근 문서 (RecentDocs)](../recentdocs.md) · [탐색기 입력 기록 (TypedPaths·WordWheelQuery)](../typedpaths-wordwheelquery.md) — 셸백과 함께 보는 탐색 기록입니다.
- [USB 저장장치 흔적 (USB Storage Artifacts)](../../external-devices/usb-storage-artifacts/index.md) · [사용자별 장치 연결 (MountPoints2)](../../external-devices/usb-storage-artifacts/mountpoints2.md) — 셸백의 볼륨이 어떤 장치였는지 확인합니다.
- [공유 폴더·네트워크 드라이브 (Network Shares·Mapped Drives)](../../network/network-shares-mapped-drives.md) — 셸백에 남은 네트워크 경로를 연결 기록과 맞춰 봅니다.
- [마스터 파일 테이블 ($MFT)](../../filesystem/mft.md) — 셸 아이템의 파일 참조와 시각을 파일시스템과 맞춰 봅니다.
- [이 파일을 누가 언제 열었나 (File Access)](../../../04-scenarios/activity/file-access.md) · [USB 로 무엇을 가져갔나 (USB)](../../../04-scenarios/exfiltration/data-exfiltration/usb.md) · [지운 파일의 흔적 찾기 (Deleted File Traces)](../../../04-scenarios/activity/deleted-file-traces.md) — 셸백을 쓰는 조사 흐름입니다.
- [섀도 복사본 활용 (Volume Shadow Copy Analysis)](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 옛 UsrClass.dat 를 꺼내 셸백이 언제 생겼는지 좁힙니다.

## 참고 문헌

- Joachim Metz, "Windows Shell Item format specification" (libfwsi) — https://github.com/libyal/libfwsi/blob/main/documentation/Windows%20Shell%20Item%20format.asciidoc
- Joachim Metz, "Windows Registry files" (winreg-kb) — https://winreg-kb.readthedocs.io/en/latest/sources/windows-registry/Files.html
- Dan Pullega, "Shellbags Forensics: Addressing a Misconception", 4n6k (2013) — https://www.4n6k.com/2013/12/shellbags-forensics-addressing.html
- Harlan Carvey, "Shellbag Analysis, Revisited...Some Testing", Windows Incident Response (2012) — https://windowsir.blogspot.com/2012/10/shellbag-analysis-revisitedsome-testing.html
- Volatility Labs, "MoVP 3.2 Shellbags in Memory, SetRegTime, and TrueCrypt Volumes" (2012) — https://volatility-labs.blogspot.com/2012/09/movp-32-shellbags-in-memory-setregtime.html
