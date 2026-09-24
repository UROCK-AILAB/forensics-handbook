# 대체 데이터 스트림 (ADS)

## 한 줄 요약

NTFS 파일에는 이름 없는 기본 데이터 스트림 (Default Data Stream) 이 하나 있습니다. 여기에 이름 있는 데이터 스트림을 더 붙일 수 있습니다. 이것을 대체 데이터 스트림 (Alternate Data Stream, ADS) 이라고 합니다. MFT 레코드 안에서는 이름이 붙은 $DATA 속성 하나가 스트림 하나입니다.

## 이 형식을 쓰는 아티팩트

Windows 와 앱은 평소에도 ADS 를 씁니다. 스트림이 있다는 것만으로는 수상하다고 볼 수 없습니다.

| 스트림 이름 (예) | 붙는 곳 | 누가 만드나 | 자세히 |
|---|---|---|---|
| Zone.Identifier | 인터넷에서 받은 파일 | 파일을 내려받은 프로그램 | [다운로드 출처 표시 (Zone.Identifier)](/02-artifacts/filesystem/zone-identifier.md) |
| WofCompressedData | Windows Overlay Filter (WOF) 로 압축한 파일 | Windows 10 이후 Windows | [압축·희소 파일 (Compressed·Sparse)](/01-foundations/disk-volume/ntfs/compressed-sparse.md) |
| $J, $Max | $Extend\$UsnJrnl | NTFS | [USN 변경 저널 ($UsnJrnl)](/02-artifacts/filesystem/usnjrnl.md) |
| $SDS | $Secure | NTFS | [NTFS 메타 파일 ($Bitmap·$Secure·$Extend)](/01-foundations/disk-volume/ntfs/bitmap-secure-extend.md) |
| $Bad | $BadClus | NTFS | [NTFS 메타 파일 ($Bitmap·$Secure·$Extend)](/01-foundations/disk-volume/ntfs/bitmap-secure-extend.md) |
| 아무 이름 | 아무 파일·폴더 | 사용자, 앱, 공격자 | 이 페이지의 "숨기는 데 쓰이는 경우" |

## 구조

### 스트림은 이름 있는 $DATA 속성입니다

- 파일 내용은 $DATA 속성에 들어 있습니다. 속성 종류 코드는 0x80 입니다.
- 속성 머리글에는 이름 길이 칸과 이름 위치 칸이 있습니다.
- 이름 길이가 0 이면 기본 스트림입니다.
- 이름 길이가 0 이 아니면 ADS 입니다.
- 한 레코드에 $DATA 속성이 여러 개 있을 수 있습니다. 이름만 서로 다르면 됩니다.
- 스트림마다 할당 크기, 실제 크기, 유효 데이터 길이 (Valid Data Length, VDL) 가 따로 있습니다.
- 압축·암호화·희소 상태도 스트림마다 따로 정해집니다.
- 상주·비상주도 스트림마다 따로 정해집니다. 작은 ADS 는 MFT 레코드 안에 들어갑니다. 큰 ADS 는 데이터 런으로 클러스터를 가리킵니다. 방법은 [데이터 런과 상주·비상주 데이터](/01-foundations/disk-volume/ntfs/data-run-resident-non-resident.md) 에 있습니다.
- 속성이 레코드 하나에 다 들어가지 않으면 $ATTRIBUTE_LIST 로 확장 레코드에 나뉩니다. 이름 있는 $DATA 도 확장 레코드에 있을 수 있습니다.

> 그림 자리: MFT 레코드 하나를 세로로 그린 그림. $STANDARD_INFORMATION, $FILE_NAME, 이름 없는 $DATA(기본 스트림), 이름이 "Zone.Identifier" 인 $DATA(ADS) 를 차례로 쌓고, 두 $DATA 머리글의 "이름 길이" 칸(0 과 15)을 강조한다.

### ADS 를 가려낼 때 보는 칸

속성 머리글 전체는 [MFT 레코드와 속성](/01-foundations/disk-volume/ntfs/file-record-attribute.md) 에 있습니다. 여기서는 ADS 를 가려내는 데 필요한 칸만 적습니다. 오프셋은 속성 시작 기준입니다.

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0x00 | 4 | 속성 종류. $DATA 는 0x80 |
| 0x04 | 4 | 속성 전체 길이 |
| 0x08 | 1 | 비상주 표시. 0 이면 상주 |
| 0x09 | 1 | 이름 길이. UTF-16 글자 수이며 끝 널 문자는 세지 않음 |
| 0x0A | 2 | 이름 위치 |
| 0x0C | 2 | 데이터 표시. 0x0001 압축, 0x4000 암호화, 0x8000 희소 |
| 0x0E | 2 | 속성 번호 (Attribute Identifier) |
| 0x10 | 4 | (상주일 때) 내용 크기 |
| 0x14 | 2 | (상주일 때) 내용 위치 |

- 이름은 상주·비상주 머리글 바로 뒤에 옵니다.
- 속성은 8바이트 경계에 맞춰 놓입니다. 남는 자리는 채움 바이트입니다.

### 이름 쓰는 법

- 스트림의 전체 이름은 `파일이름:스트림이름:스트림종류` 입니다. 예: `report.docx:note:$DATA`
- 기본 스트림의 전체 이름은 `report.docx::$DATA` 입니다. 이것은 `report.docx` 와 같습니다.
- 파일 이름에 쓸 수 있는 글자는 스트림 이름에도 모두 쓸 수 있습니다. 빈칸도 됩니다.
- `$DATA` 도 스트림 이름이 될 수 있습니다. 이때 전체 이름은 `sample:$DATA:$DATA` 입니다.
- 스트림 종류는 NTFS 가 정해 둔 것만 있습니다. 사용자가 새 종류를 만들 수 없습니다.

### ADS 와 헷갈리기 쉬운 것

| 이름 | 속성 종류 | ADS 인가 |
|---|---|---|
| 폴더의 $I30 | $INDEX_ROOT·$INDEX_ALLOCATION | 아닙니다. 폴더 목록 인덱스입니다. [폴더 인덱스와 슬랙 ($I30)](/02-artifacts/filesystem/i30.md) |
| $EFS | $LOGGED_UTILITY_STREAM | 아닙니다. EFS 가 암호화 정보를 두는 곳입니다. [EFS 암호화 파일](/03-techniques/analysis/encrypted-evidence/encrypting-file-system.md) |
| 확장 특성 (Extended Attributes, EA) | $EA·$EA_INFORMATION | 아닙니다. $DATA 가 아니므로 스트림 목록에 나오지 않습니다 |

MITRE ATT&CK 은 ADS 와 EA 를 둘 다 자료를 숨기는 기법(T1564.004)으로 묶습니다. 숨긴 자료를 찾을 때는 둘을 따로 확인해야 합니다.

## 읽는 법

### 헥스로 한 번

아래는 명세로 만든 예시입니다. 특정 검체에서 나온 값이 아닙니다. 파일에 이름이 "note" 인 ADS 가 있고, 내용이 "hello" 5바이트인 경우의 $DATA 속성입니다.

```
오프셋  00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
0000    80 00 00 00 28 00 00 00  00 04 18 00 00 00 03 00
0010    05 00 00 00 20 00 00 00  6E 00 6F 00 74 00 65 00
0020    68 65 6C 6C 6F 00 00 00
```

1. 0x00 의 `80 00 00 00` 은 종류 0x80 입니다. $DATA 속성입니다.
2. 0x08 의 `00` 은 상주라는 뜻입니다.
3. 0x09 의 `04` 는 이름이 4글자라는 뜻입니다. 0 이 아니므로 ADS 입니다.
4. 0x0A 의 `18 00` 은 이름이 0x18 에서 시작한다는 뜻입니다. 0x18 의 `6E 00 6F 00 74 00 65 00` 은 UTF-16LE 로 "note" 입니다.
5. 0x0C 의 `00 00` 은 압축·암호화·희소가 아니라는 뜻입니다.
6. 0x0E 의 `03 00` 은 속성 번호 3 입니다. 이 값은 예시로 넣었습니다.
7. 0x10 의 `05 00 00 00` 은 내용이 5바이트라는 뜻입니다.
8. 0x14 의 `20 00` 은 내용이 0x20 에서 시작한다는 뜻입니다. 0x20 의 `68 65 6C 6C 6F` 는 "hello" 입니다.
9. 0x04 의 `28 00 00 00` 은 속성 길이 40바이트입니다. 내용 뒤 3바이트는 8바이트 경계를 맞추는 채움입니다.

같은 레코드의 기본 스트림은 0x09 가 `00` 입니다. 레코드 안의 0x80 속성을 모두 찾아 이름 길이를 보면 ADS 를 빠짐없이 셀 수 있습니다. 확장 레코드가 있으면 거기도 봐야 합니다.

### 실행 중인 시스템에서

아래 명령은 살아 있는 시스템에서 쓰는 방법입니다. 디스크 이미지는 뒤의 "도구" 에 적은 방법으로 읽습니다.

- `dir /r` 는 파일의 대체 데이터 스트림을 함께 보여 줍니다.
- PowerShell 의 `Get-Item <경로> -Stream *` 은 스트림 이름과 크기를 보여 줍니다. `Get-Content <경로> -Stream <이름>` 은 스트림 내용을 읽습니다.
- `fsutil file layout <경로>` 는 속성 종류 코드, 스트림 이름, 상주 여부를 함께 보여 줍니다 (확인 범위: Windows 11 25H2).
- 폴더에 붙인 ADS 는 `dir /r` 에서 `.:이름:$DATA` 로 보였습니다. 같은 폴더에 `Get-Item -Stream *` 을 쓰면 아무것도 나오지 않았습니다 (확인 범위: Windows 11 25H2, Windows PowerShell 5.1).

## 포렌식에서 중요한 점

### 스트림에는 자기 시각이 없습니다

- 스트림마다 따로 매긴 시각은 없습니다.
- 어느 스트림이든 바뀌면 파일의 시각이 바뀝니다.
- 그래서 파일의 수정 시각이 바뀌었다고 해서 기본 스트림의 내용이 바뀌었다고 할 수 없습니다.
- 작은 ADS 를 새로 붙이자 $STANDARD_INFORMATION 의 수정·접근·MFT 변경 시각이 함께 바뀌었습니다. 만든 시각은 그대로였습니다 (확인 범위: Windows 11 25H2).
- 그 ADS 를 지우자 MFT 변경 시각만 바뀌었습니다. 수정 시각은 그대로였습니다 (확인 범위: Windows 11 25H2).
- 스트림이 언제 생겼는지는 변경 저널과 $LogFile 에서 찾습니다.
- 두 벌의 시각이 각각 언제 바뀌는지는 [두 벌의 시각](/01-foundations/disk-volume/ntfs/standard-information-file-name.md) 과 [파일 시각 네 가지와 변화 규칙](/03-techniques/analysis/timeline/macb-timestamp-rules.md) 에 있습니다.

### 변경 저널에 남는 것

[USN 변경 저널 ($UsnJrnl)](/02-artifacts/filesystem/usnjrnl.md) 에는 이름 있는 스트림만 따로 가리키는 이유 코드가 있습니다.

| 이유 코드 | 값 | 뜻 |
|---|---|---|
| USN_REASON_STREAM_CHANGE | 0x00200000 | 이름 있는 스트림을 더했거나, 지웠거나, 이름을 바꿈 |
| USN_REASON_NAMED_DATA_EXTEND | 0x00000020 | 이름 있는 스트림이 커짐 |
| USN_REASON_NAMED_DATA_OVERWRITE | 0x00000010 | 이름 있는 스트림의 내용을 덮어씀 |
| USN_REASON_NAMED_DATA_TRUNCATION | 0x00000040 | 이름 있는 스트림이 작아짐 |

- USN_RECORD_V2 의 이름 칸에는 파일이나 폴더 이름이 들어갑니다.
- 스트림 이름을 적는 칸은 없습니다.
- 그래서 변경 저널만으로는 어느 스트림이 바뀌었는지 알 수 없습니다. 지금 MFT 레코드에 있는 스트림 목록과 맞춰 봐야 합니다.

### 지운 스트림

- 파일을 지우면 MFT 레코드가 "비어 있음" 으로 표시됩니다. 레코드 안의 이름 있는 $DATA 속성도 레코드가 다시 쓰일 때까지 함께 남습니다. 복구 방법은 [파일시스템 기반 복구](/03-techniques/analysis/data-recovery/undelete-ntfs-fat.md) 에 있습니다.
- 파일은 두고 스트림만 지우면 그 속성이 레코드에서 빠집니다.
- 지운 스트림이 비상주였다면 쓰던 클러스터는 비할당 영역이 됩니다. [비할당 영역과 슬랙](/03-techniques/analysis/data-recovery/unallocated-slack-space.md) 을 봅니다.
- 스트림을 지운 흔적은 변경 저널의 STREAM_CHANGE 기록, [$LogFile](/02-artifacts/filesystem/logfile.md), [섀도 복사본](/03-techniques/analysis/volume-shadow-copy-analysis.md) 에서 찾습니다.

### 숨기는 데 쓰이는 경우

- 탐색기와 옵션 없는 `dir` 는 ADS 를 보여 주지 않습니다.
- 파일 크기에는 기본 스트림 크기만 나옵니다. ADS 크기는 더해지지 않습니다.
- MITRE ATT&CK 은 ADS 에 자료를 숨기는 것을 T1564.004 로 분류합니다.
- MITRE 는 esentutl, expand 같은 Windows 기본 도구가 ADS 를 읽고 쓰는 데 쓰인다고 적습니다.
- 명령줄에 `파일이름:스트림이름` 모양의 콜론이 있으면 단서가 됩니다. 명령줄은 [프로세스 생성 (4688)](/02-artifacts/event-logs/4688.md) 이나 [Sysmon 이벤트 1](/02-artifacts/event-logs/sysmon/1.md) 에 남을 수 있습니다.
- 보고서에는 기록이 말하는 만큼만 씁니다. 예: "이 파일에 이름이 X 인 ADS 가 있고, 크기는 N 바이트입니다."
- 누가 왜 만들었는지는 변경 저널, 프로세스 기록 같은 다른 근거가 있을 때만 씁니다.

### 옮기거나 모으면 사라질 수 있습니다

- Windows 의 파일 복사 함수(CopyFileEx)는 ADS 도 함께 복사합니다.
- PowerShell `Copy-Item` 으로 복사한 사본에 5,000바이트 ADS 가 비상주로 그대로 있었습니다 (확인 범위: Windows 11 25H2).
- FAT 처럼 NTFS 가 아닌 파일시스템으로 옮기면 ADS 는 없어집니다. FAT 구조는 [FAT·exFAT 구조](/01-foundations/disk-volume/fat-exfat.md) 에 있습니다.
- 파일을 골라 모으는 [선별 수집](/03-techniques/process-acquisition/evidence-acquisition/triage-collection.md) 은 수집 도구가 ADS 를 챙기는지 따로 확인해야 합니다.
- [디스크 이미징](/03-techniques/process-acquisition/evidence-acquisition/disk-imaging.md) 은 MFT 와 클러스터를 통째로 담습니다. 그래서 ADS 도 이미지에 남습니다.
- 경로로 파일을 열면 기본 스트림이 열립니다. 그래서 경로로 연 파일의 해시는 기본 스트림만 계산한 값입니다. ADS 는 따로 해시해야 합니다. [해시로 무결성 검증](/03-techniques/process-acquisition/evidence-acquisition/hash-verification.md) 을 함께 봅니다.
- 같은 이유로 [키워드 검색](/03-techniques/analysis/content-search/keyword-search.md) 도 도구가 ADS 를 검색 대상에 넣는지 확인해야 합니다.

## 함정

- **"ADS 를 붙여도 파일 시각은 안 바뀐다"** 는 옛 설명입니다. 2000년대 초 자료 중에 이렇게 쓴 것이 있습니다. Microsoft 문서는 어느 스트림이 바뀌어도 파일 시각이 바뀐다고 적습니다. Windows 11 25H2 에서도 바뀌었습니다.
- **흔한 ADS 를 수상하다고 보고하지 않습니다.** Zone.Identifier 와 WofCompressedData 는 정상 동작으로 생깁니다.
- **파일만 훑는 방법은 폴더의 ADS 를 놓칠 수 있습니다.** 폴더에도 이름 있는 $DATA 를 붙일 수 있습니다.
- **기본 레코드만 읽는 도구는 확장 레코드에 있는 스트림을 놓칠 수 있습니다.** 확장 레코드는 [MFT 레코드와 속성](/01-foundations/disk-volume/ntfs/file-record-attribute.md) 에 설명이 있습니다.
- **이름을 콜론으로 자를 때 조심합니다.** 스트림 이름이 `$DATA` 이거나 빈칸을 품고 있으면 이름 해석이 어긋날 수 있습니다.
- **희소 표시가 기본 스트림 이야기가 아닐 수 있습니다.** 파일의 희소 속성 (FILE_ATTRIBUTE_SPARSE_FILE) 은 스트림 중 하나라도 희소였던 적이 있으면 켜집니다.
- **$EFS 와 EA 는 스트림 목록에 나오지 않습니다.** 스트림 목록이 비었다고 레코드에 숨은 자료가 없다고 할 수 없습니다.

## 도구

도구 이름은 예시입니다. 한 도구 결과만 믿지 말고 [도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md) 을 합니다.

| 상황 | 방법 (예) |
|---|---|
| 실행 중인 시스템 | `dir /r`, PowerShell `-Stream`, `fsutil file layout`, Sysinternals Streams |
| 디스크 이미지 | MFT 레코드의 $DATA 속성을 모두 나열하는 공개 파서. 예: The Sleuth Kit `istat` 로 속성 목록을 보고, `icat` 에 `레코드번호-128-속성번호` 를 줘 한 스트림만 꺼냄 |
| MFT 전체 훑기 | MFT 를 표로 풀어 주는 공개 파서 (예: MFTECmd, analyzeMFT). 결과를 [마스터 파일 테이블 ($MFT)](/02-artifacts/filesystem/mft.md) 해석과 함께 봅니다 |

## 참고 문헌

1. Microsoft Learn, "File Streams (Local File Systems)". https://learn.microsoft.com/en-us/windows/win32/fileio/file-streams
2. Microsoft Learn, "USN_RECORD_V2 structure (winioctl.h)". https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-usn_record_v2
3. Microsoft Learn, "CopyFileExA function (winbase.h)". https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-copyfileexa
4. libyal, "New Technologies File System (NTFS)" 형식 문서 (libfsntfs). https://github.com/libyal/libfsntfs/blob/main/documentation/New%20Technologies%20File%20System%20(NTFS).asciidoc
5. MITRE ATT&CK, "Hide Artifacts: NTFS File Attributes (T1564.004)". https://attack.mitre.org/techniques/T1564/004/
6. Damon Martin, "Windows, NTFS and Alternate Data Streams", GIAC GSEC Practical, SANS Institute. https://www.giac.org/paper/gsec/715/windows-ntfs-alternate-data-streams/101622
