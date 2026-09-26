---
title: "파일시스템 타임라인"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 3280
---

# 파일시스템 타임라인 (Filesystem Timeline: $MFT·$UsnJrnl·$LogFile)

상위 허브: [타임라인 작성 (Timeline)](index.md)

## 한 줄 요약

NTFS 볼륨의 메타데이터 파일 세 개로 파일 단위 시간표를 만듭니다. $MFT 에서는 파일마다 마지막 상태의 시각을 얻고, $UsnJrnl:$J 에서는 변경이 생길 때마다 쌓인 기록을 얻으며, $LogFile 은 메타데이터 트랜잭션 저널입니다(참고 1).

## 언제 쓰나

- 어떤 시간대에 파일이 생기고 바뀌고 지워졌는지 볼 때 씁니다.
- 이름을 바꾸거나 옮긴 파일의 경로를 따라갈 때 씁니다.
- $MFT 에서 이미 사라진 파일의 이름을 찾을 때 씁니다. USN 레코드에는 삭제 기록에도 파일 이름 칸이 있습니다.
- [여러 아티팩트 합친 타임라인](super-timeline.md)의 뼈대를 만들 때 씁니다.

## 세 파일의 위치

| 파일 | MFT 항목 번호 | 내용 (참고 1) |
|---|---|---|
| $MFT | 0 | MFT 항목의 모음 |
| $LogFile | 2 | 메타데이터 트랜잭션 저널 |
| $Extend | 11 | 확장 메타데이터 파일을 담는 폴더 |
| $Extend\$UsnJrnl | 표에 고정 번호 없음 | $J(레코드)와 $Max(메타데이터) 두 스트림 |

- $UsnJrnl 은 $Extend 폴더 안에 있으며 고정된 MFT 항목 번호가 없습니다(참고 1). 그래서 번호가 아니라 $Extend 안의 이름으로 찾습니다.
- 파일마다의 전체 구조는 [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md), [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md), [NTFS 트랜잭션 로그](../../../02-artifacts/filesystem/logfile.md)에서 다룹니다. 이 페이지는 시간표를 만드는 데 쓰는 칸만 다룹니다.

## $MFT 에서 얻는 시각

- MFT 항목마다 $SI 네 시각과 $FN 네 시각이 있습니다. 오프셋과 뜻은 [파일 시각 네 가지와 변화 규칙](macb-timestamp-rules.md)에서 다룹니다.
- 칸마다 마지막 값 하나만 남아서, 그 전 값은 $MFT 로 알 수 없습니다.
- $SI 크기는 NTFS 1.2 에서 48바이트, 3.0 이상에서 72바이트입니다(참고 1). 3.0 이상의 $SI 에는 칸이 더 붙는데(참고 1), 오프셋 48 은 소유자 ID, 52 는 보안 설명자 ID, 56 은 할당량, 64 는 USN(8바이트)입니다(참고 1).
- 오프셋 64 의 USN 칸은 그 파일에 마지막으로 쓰인 USN 레코드의 번호로 알려져 있으며, 이 값으로 MFT 항목과 $J 의 레코드를 이을 수 있습니다.

$FN 은 이름마다 하나씩 있습니다. 어느 이름의 시각인지는 이름공간 (Namespace) 값으로 가립니다(참고 1).

| 이름공간 값 | 이름 (참고 1) |
|---|---|
| 0 | POSIX |
| 1 | Win32 (긴 이름) |
| 2 | DOS (8.3 짧은 이름) |
| 3 | DOS 이름과 Win32 이름이 같음 |

- $SI 없이 $FN 과 $I30 인덱스만 있는 MFT 항목도 있습니다(참고 1). 이런 항목에서는 $SI 줄이 나오지 않습니다. $I30 은 [폴더 인덱스와 슬랙](../../../02-artifacts/filesystem/i30.md)에서 다룹니다.
- MFT 레코드가 $ATTRIBUTE_LIST(0x20)로 확장 레코드를 쓰면, 긴 이름의 $FN 이 확장 레코드에만 있을 수 있습니다. 이때 기본 레코드만 보면 8.3 짧은 이름만 보이고, 확장 레코드는 대개 기본 레코드와 멀리 떨어져 있습니다.

## $UsnJrnl:$J 에서 얻는 기록

### 레코드의 칸 (USN_RECORD_V2)

칸 이름은 Microsoft 구조체의 이름입니다(참고 2). 오프셋은 참고 1 에 있습니다.

| 오프셋 | 크기 | 칸 | 시간표에서 쓰는 곳 |
|---|---|---|---|
| 0 | 4 | RecordLength | 다음 레코드로 넘어가기 |
| 4 | 2 | MajorVersion | 2 인지 확인 |
| 6 | 2 | MinorVersion | |
| 8 | 8 | FileReferenceNumber | MFT 항목과 잇기 |
| 16 | 8 | ParentFileReferenceNumber | 경로 붙이기 |
| 24 | 8 | Usn | $SI 의 USN 칸과 잇기 |
| 32 | 8 | TimeStamp | 줄의 시각 |
| 40 | 4 | Reason | 무엇이 바뀌었나 |
| 44 | 4 | SourceInfo | 사용자 변경이 아닌 것 거르기 |
| 48 | 4 | SecurityId | |
| 52 | 4 | FileAttributes | |
| 56 | 2 | FileNameLength | 이름 길이(바이트) |
| 58 | 2 | FileNameOffset | 이름 위치 |
| 60 | 가변 | FileName | 파일 이름 |

- MajorVersion 2 는 USN_RECORD_V2, 3 은 V3, 4 는 V4 입니다(참고 2).
- 버전이 2 가 아니면 위 표로 읽지 않습니다.
- Windows 8·Server 2012 이전에는 이 구조체 이름이 USN_RECORD 였습니다(참고 2).
- 이 구조체의 최소 지원 버전은 Windows XP·Windows Server 2003 입니다(참고 2).
- TimeStamp 는 이 레코드의 UTC FILETIME 입니다(참고 2).
- 파일 이름 길이는 FileNameLength(바이트)로 잽니다(참고 2). 끝의 '\0' 에 기대지 않습니다(참고 2).
- 레코드는 64비트 경계에 맞춰 놓입니다(참고 1, 참고 2).

### Reason 읽기

Reason 은 파일이 열린 뒤 쌓인 변경 이유 플래그입니다(참고 2). 파일이 닫힐 때 USN_REASON_CLOSE 가 붙은 마지막 레코드가 생기고, 그다음 변경은 새 레코드에서 플래그를 처음부터 다시 쌓습니다(참고 2). 그래서 CLOSE 가 붙은 레코드의 Reason 에는 열고 닫는 사이의 이유가 모여 있습니다. 레코드 한 건을 사용자 행동 한 번으로 읽지 않습니다.

| 값 (참고 2) | USN_REASON_ 뒤 이름 | 뜻 |
|---|---|---|
| 0x00000001 | DATA_OVERWRITE | 데이터를 덮어씀 |
| 0x00000002 | DATA_EXTEND | 데이터가 늘어남 |
| 0x00000004 | DATA_TRUNCATION | 데이터가 잘림 |
| 0x00000010 · 0x00000020 · 0x00000040 | NAMED_DATA_OVERWRITE · _EXTEND · _TRUNCATION | 이름 있는 스트림을 덮어씀 · 늘어남 · 잘림 |
| 0x00000100 | FILE_CREATE | 파일을 처음 만듦 |
| 0x00000200 | FILE_DELETE | 파일을 지움 |
| 0x00000400 | EA_CHANGE | EA 변경 |
| 0x00000800 | SECURITY_CHANGE | 접근 권한 변경 |
| 0x00001000 | RENAME_OLD_NAME | 레코드의 이름이 옛 이름 |
| 0x00002000 | RENAME_NEW_NAME | 레코드의 이름이 새 이름 |
| 0x00004000 | INDEXABLE_CHANGE | FILE_ATTRIBUTE_NOT_CONTENT_INDEXED 속성 변경 |
| 0x00008000 | BASIC_INFO_CHANGE | 속성이나 시각 가운데 하나 이상 변경 |
| 0x00010000 | HARD_LINK_CHANGE | 하드 링크 변경 |
| 0x00020000 | COMPRESSION_CHANGE | 압축 상태 변경 |
| 0x00040000 | ENCRYPTION_CHANGE | 암호화 상태 변경 |
| 0x00080000 | OBJECT_ID_CHANGE | 개체 ID 변경 |
| 0x00100000 | REPARSE_POINT_CHANGE | 리파스 포인트 변경 |
| 0x00200000 | STREAM_CHANGE | 이름 있는 스트림 추가·삭제·이름 변경 |
| 0x00400000 | TRANSACTED_CHANGE | TxF 트랜잭션 변경 |
| 0x00800000 | INTEGRITY_CHANGE | FILE_ATTRIBUTE_INTEGRITY_STREAM 속성 변경 |
| 0x80000000 | CLOSE | 파일이 닫힘 |

이름을 바꾸거나 옮기면 레코드가 두 건 생깁니다(참고 2). 한 건에는 옛 부모 폴더가 적힙니다(참고 2). 다른 한 건에는 새 부모 폴더가 적힙니다(참고 2). 두 건을 함께 읽으면 옛 경로와 새 경로를 모두 얻습니다. 어느 쪽 이름인지는 RENAME_OLD_NAME·RENAME_NEW_NAME 플래그로 가립니다.

SourceInfo 는 변경을 만든 쪽이 FSCTL_MARK_HANDLE 로 붙인 출처 정보입니다(참고 2). 백신 필터처럼 알려진 출처가 만든 레코드를 걸러 낼 때 씁니다(참고 2). DATA_MANAGEMENT 는 쓰기가 있었어도 사용자 관점에서 데이터가 바뀌지 않았다는 표시입니다(참고 2).

| SourceInfo 값 | USN_SOURCE_ 뒤 이름 (참고 2) |
|---|---|
| 0x1 | DATA_MANAGEMENT |
| 0x2 | AUXILIARY_DATA |
| 0x4 | REPLICATION_MANAGEMENT |
| 0x8 | CLIENT_REPLICATION_MANAGEMENT |

### $Max 와 $J 추출

| $Max 오프셋 | 크기 | 뜻 (참고 1) |
|---|---|---|
| 0 | 8 | 최대 크기 |
| 8 | 8 | 할당 증분 |
| 16 | 8 | 저널 식별자 (FILETIME) |
| 24 | 8 | 미상 |

- $Max 는 32바이트입니다(참고 1).
- $J 는 희소 스트림 (Sparse Stream)입니다(참고 1).
- $J 앞부분은 비어 있습니다. 빈 구멍을 0 으로 채워 뽑으면 논리 크기만큼 나오는데 이 크기는 수 GB 에 이르고, 구멍을 건너뛰어 뽑으면 실제 데이터만 남습니다.
- 두 방법은 크기와 해시가 달라서 어느 방법으로 뽑았는지 기록합니다. 획득 절차는 [증거 획득](../../process-acquisition/evidence-acquisition/index.md)을 봅니다.
- 저널의 최대 크기는 검체의 $Max 에서 직접 읽습니다.

### 헥스로 한 번

아래 바이트는 위 표를 따라 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0000    48 00 00 00 02 00 00 00 2A 01 00 00 00 00 03 00
0010    05 00 00 00 00 00 05 00 00 A8 3C 01 00 00 00 00
0020    00 50 C7 8A BF 76 DA 01 00 01 00 80 00 00 00 00
0030    00 00 00 00 20 00 00 00 0A 00 3C 00 61 00 2E 00
0040    74 00 78 00 74 00 00 00
```

1. `48 00 00 00` 은 RecordLength 입니다. 레코드 길이는 0x48, 곧 72바이트입니다. 72 는 8의 배수이므로 64비트 경계에 맞습니다.
2. `02 00` 은 MajorVersion 2 입니다. 그래서 위 V2 표로 읽습니다.
3. 0x08 의 8바이트는 이 파일의 참조 번호입니다.
4. 0x10 의 8바이트는 부모 폴더의 참조 번호입니다. 참조 번호의 구성은 [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md)에서 다룹니다.
5. 0x18 의 `00 A8 3C 01 00 00 00 00` 은 Usn 입니다. 리틀 엔디언으로 0x013CA800, 10진으로 20,752,384 입니다. 이 파일의 $SI USN 칸이 같은 값이면 이 레코드가 그 파일의 마지막 USN 레코드입니다.
6. 0x20 의 `00 50 C7 8A BF 76 DA 01` 은 TimeStamp 입니다. 리틀 엔디언으로 0x01DA76BF8AC75000, 10진으로 133,549,704,000,000,000 입니다. 날짜로는 2024-03-15 10:00:00 UTC 입니다. 계산법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다.
7. 0x28 의 `00 01 00 80` 은 Reason 0x80000100 입니다. FILE_CREATE(0x00000100)와 CLOSE(0x80000000)가 켜져 있습니다. 파일을 만들고 닫았다는 기록입니다.
8. 0x2C 의 SourceInfo 는 0 입니다. 켜진 플래그가 없습니다.
9. 0x30 은 SecurityId, 0x34 는 FileAttributes 입니다. 이 예시에서는 풀지 않습니다.
10. 0x38 의 `0A 00` 은 이름 길이 10바이트입니다. 0x3A 의 `3C 00` 은 이름 위치 60(0x3C)입니다.
11. 0x3C 부터 10바이트는 UTF-16LE 이름 `a.txt` 입니다. 뒤의 `00 00` 두 바이트는 8바이트 경계를 맞추는 채움입니다.

## $LogFile

$LogFile 은 페이지 단위로 읽습니다. 페이지 헤더 서명은 "RSTR"(재시작), "RCRD"(레코드), "CHKD" 세 가지입니다(참고 1).

재시작 페이지 헤더는 30바이트입니다(참고 1).

| 오프셋 | 크기 | 칸 (참고 1) |
|---|---|---|
| 0 | 4 | 서명 |
| 4 | 2 | fix-up 오프셋 |
| 6 | 2 | fix-up 개수 |
| 8 | 8 | chkdsk 마지막 LSN |
| 16 | 4 | 시스템 페이지 크기 |
| 20 | 4 | 로그 페이지 크기 |
| 24 | 2 | 재시작 오프셋 |
| 26 | 2 | 부 버전 |
| 28 | 2 | 주 버전 (-1 베타, 0 전환, 1 update sequence) |

- 레코드 헤더(LFS_RECORD_HEADER)에는 LSN 이 있습니다(참고 1).
- $LogFile 해석 결과를 시간표에 넣을 때는 도구가 시각을 어디서 가져왔는지 확인합니다. 해석 방법은 [NTFS 트랜잭션 로그](../../../02-artifacts/filesystem/logfile.md)에서 다룹니다.

## 절차

1. 볼륨에서 $MFT, $LogFile, $Extend\$UsnJrnl 의 $J·$Max 를 뽑습니다. $J 를 어떤 방법으로 뽑았는지 적습니다.
2. $MFT 를 풉니다. 항목마다 $SI 시각을 한 줄로 냅니다. $FN 시각은 이름마다 한 줄로 냅니다.
3. $ATTRIBUTE_LIST 가 있는 항목은 확장 레코드까지 따라갑니다.
4. $J 를 풉니다. 레코드마다 MajorVersion 을 확인합니다.
5. $J 레코드마다 TimeStamp·Reason·SourceInfo·파일 참조·부모 참조·이름을 한 줄로 냅니다.
6. 파일 참조 번호로 $J 레코드와 MFT 항목을 잇습니다. 부모 참조 번호로 경로를 붙입니다.
7. 이름 바꾸기·이동은 두 레코드를 한 사건으로 묶습니다. 옛 경로와 새 경로를 함께 적습니다.
8. $SI 의 USN 칸과 $J 의 Usn 을 맞춥니다. $MFT 에 보이는 마지막 상태가 어느 레코드 다음의 것인지 확인합니다.
9. $LogFile 해석 결과는 따로 줄로 넣고 출처를 표시합니다.
10. $MFT 와 $J 의 시각은 둘 다 UTC 입니다(참고 3, 참고 2). 한 기준으로 정렬하고 줄마다 출처 칸을 남깁니다.
11. 다른 아티팩트와 합칠 때는 [여러 아티팩트 합친 타임라인](super-timeline.md)으로 넘어갑니다.

## 도구

libfsntfs(참고 1), The Sleuth Kit, plaso 가 공개 도구의 예입니다. 어느 도구를 쓰든 아래를 확인합니다.

- $FN 을 어느 이름공간의 것으로 내보내는지 확인합니다.
- $ATTRIBUTE_LIST 의 확장 레코드를 따라가는지 확인합니다.
- MajorVersion 3·4 의 USN 레코드를 읽는지 확인합니다.
- SourceInfo 칸을 보여 주는지 확인합니다.
- 시각을 UTC 로 내는지, 분석 PC 의 현지 시각으로 바꿔 내는지 확인합니다.

몇 줄은 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../reporting/tool-validation.md)을 봅니다.

## 함정과 한계

1. **$MFT 는 마지막 값만 보여 줍니다.** 그 전의 변경은 $J 에서 찾습니다.
2. **USN 레코드 한 건은 행동 한 번이 아닙니다.** 열고 닫는 사이의 이유가 한 레코드에 모입니다.
3. **BASIC_INFO_CHANGE 만으로 시각 변경을 가릴 수 없습니다.** 이 플래그는 속성이나 시각 가운데 하나 이상이 바뀌면 붙습니다(참고 2). 시각 조작 여부는 [시각 조작 탐지](timestomping.md)에서 따집니다.
4. **SourceInfo 가 켜진 레코드를 사용자 행동으로 읽습니다.** 사용자 관점에서 데이터가 바뀌지 않은 변경일 수 있습니다(참고 2).
5. **$J 를 뽑는 방법에 따라 크기와 해시가 다릅니다.** 방법을 적지 않으면 나중에 해시를 맞출 수 없습니다.
6. **기본 레코드만 읽습니다.** 긴 이름과 그 시각을 놓칠 수 있습니다.
7. **$J 의 시작점을 잊습니다.** $J 에 남은 가장 이른 레코드가 이 기록의 시작점입니다. 그보다 앞의 변경은 $J 로 볼 수 없습니다.

## 결과를 어떻게 해석하나

- $MFT 줄은 "지금 이 칸에 이 값이 적혀 있다" 는 뜻입니다.
- $J 줄은 "이 시각에 이 이유로 레코드가 쓰였다" 는 뜻입니다.
- FILE_DELETE 레코드에는 지운 파일의 이름과 부모 폴더 참조가 남습니다. $MFT 에서 사라진 파일을 찾을 때 씁니다. 자세한 흐름은 [지운 파일의 흔적 찾기](../../../04-scenarios/activity/deleted-file-traces.md)를 봅니다.
- 쓸 수 있는 문장(예): "USN 저널에 2024-03-15 10:00:00 UTC, 이름 a.txt, 이유 FILE_CREATE·CLOSE 인 레코드가 있습니다."
- 쓰면 안 되는 문장(예): "사용자가 2024-03-15 10:00:00 UTC 에 a.txt 를 만들었습니다."

## 참고 문헌

1. libyal, "New Technologies File System (NTFS) format" (libfsntfs 문서) — https://raw.githubusercontent.com/libyal/libfsntfs/main/documentation/New%20Technologies%20File%20System%20(NTFS).asciidoc
2. Microsoft Learn, "USN_RECORD_V2 structure (winioctl.h)" — https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-usn_record_v2
3. Microsoft Learn, "File Times" — https://learn.microsoft.com/en-us/windows/win32/sysinfo/file-times
