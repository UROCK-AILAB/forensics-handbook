# 지운 파일의 흔적 찾기 (Deleted File Traces)

파일이 지금 디스크에 없을 때 "이런 파일이 있었나, 언제 어떻게 없어졌나, 내용을 되살릴 수 있나" 를 묻는 조사를 다룹니다. 지운 파일의 흔적은 한곳에 모여 있지 않습니다. 휴지통, 파일 시스템 메타데이터, 변경 저널, 사용 흔적, 이벤트 로그에 조각으로 흩어져 남습니다. 이 페이지는 이 조각을 어떤 순서로 모으는지, 그 기록으로 어디까지 말할 수 있는지를 정리합니다. 아티팩트마다의 구조는 각 아티팩트 페이지에 있습니다.

"(현장 관찰)" 을 붙인 내용은 분석 현장에서 겪은 일을 적어 둔 메모에서 가져왔습니다. 공식 문서로 확인한 내용이 아니므로 검체마다 다시 확인합니다.

## 조사 질문

- 이 이름·경로의 파일이 이 PC 에 있었습니까?
- 언제 없어졌습니까? 지운 것입니까, 옮기거나 이름만 바꾼 것입니까?
- 휴지통을 거쳤습니까?
- 어느 계정·프로세스가 지웠습니까?
- 내용을 되살릴 수 있습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | 휴지통 `$I` 형식과 변경 저널 레코드의 버전이 Windows 버전마다 다릅니다. [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 버전과 빌드를 먼저 적습니다. |
| 시간대 | [시간대 설정](../../02-artifacts/system-account/time-zone.md) 을 읽습니다. Bias 값을 부호 있는 수로 읽는 법은 [이 파일을 누가 언제 열었나](file-access.md) 의 "먼저 확인할 것" 에 있습니다. |
| 사용자 | 휴지통은 SID 별 폴더에 남습니다. [사용자 프로필 목록](../../02-artifacts/system-account/profilelist.md) 으로 SID 와 사용자를 짝지어 둡니다. |
| 저장 장치 | SSD 와 TRIM 설정에 따라 지운 자리를 되살리기 어려울 수 있습니다. 아래 "복구 가능성" 을 봅니다. |
| 감사 정책·Sysmon | 4663 은 감사와 SACL 이 있어야 남습니다. Sysmon 23·26 은 Sysmon 이 설치돼 있어야 남습니다. [감사 정책과 로그 설정](../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 확인합니다. |
| 수집 범위 | 볼륨마다 $MFT, $UsnJrnl:$J, $LogFile, `$Recycle.Bin` 을 확보합니다. 사용자 하이브와 섀도 복사본도 함께 확보합니다. 비할당 영역까지 보려면 파일 사본이 아니라 디스크 이미지를 뜹니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 휴지통 (`$I`·`$R`) | 원래 경로, 크기, 휴지통으로 옮긴 시각, 내용 | [휴지통](../../02-artifacts/file-folder-usage/recycle-bin.md) |
| 2 | $MFT | 해제된 레코드의 이름·시각·순번 | [마스터 파일 테이블](../../02-artifacts/filesystem/mft.md) |
| 3 | $UsnJrnl | 만들기·지우기·이름 바꾸기가 일어난 시각과 이유 | [USN 변경 저널](../../02-artifacts/filesystem/usnjrnl.md) |
| 4 | $LogFile·폴더 인덱스 | 보조 기록(세부는 링크 페이지) | [NTFS 트랜잭션 로그](../../02-artifacts/filesystem/logfile.md) · [폴더 인덱스와 슬랙](../../02-artifacts/filesystem/i30.md) |
| 5 | 사용 흔적 | 지운 뒤에도 남는 경로·시각·파일 참조 | 아래 "지운 뒤에도 남는 기록" |
| 6 | 보안 로그 4663 | 삭제 권한을 쓴 계정·프로세스 | [파일 접근 감사](../../02-artifacts/event-logs/4656-4663-4660.md) |
| 7 | Sysmon 23·26·28 | 지운 파일, 보관한 사본, 완전삭제를 막은 기록 | [Sysmon 로그](../../02-artifacts/event-logs/sysmon/index.md) |
| 8 | 섀도 복사본 | 지우기 전 시점의 파일과 기록 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 9 | 비할당 영역 | 되살릴 내용 | [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) |

휴지통과 파일 시스템 기록(1\~3)을 먼저 봅니다. 이 셋으로 "있었나, 언제 없어졌나" 를 정합니다. 5\~7 은 경로와 행위자를 보태고, 8\~9 는 내용을 되살리는 데 씁니다.

## 휴지통

Vista 이후 휴지통으로 보낸 항목마다 `\$Recycle.Bin\<SID>\` 에 `$R` 파일과 `$I` 파일이 생깁니다. `$R` 에는 내용이 있고 `$I` 에는 원래 경로, 크기, 지운 시각(UTC FILETIME)이 있습니다. `$R` 은 원래 파일과 파일 ID(MFT 레코드 번호·순번)가 같은데, 복사한 것이 아니라 이름과 부모 폴더만 바꾼 것입니다.

휴지통을 거치지 않는 삭제가 많습니다. 또 `$I` 는 있는데 `$R` 이 없다고 휴지통을 비웠다고 볼 수 없으며, 복원한 뒤에도 `$I` 가 남습니다.

`$I` 의 오프셋과 버전별 차이는 [휴지통](../../02-artifacts/file-folder-usage/recycle-bin.md) 에 있습니다.

## MFT 레코드

MFT 레코드 머리 (FILE_RECORD_SEGMENT_HEADER) 에서 지운 파일을 가리는 칸은 셋입니다[1].

| 칸 | 뜻 |
|---|---|
| Flags | FILE_RECORD_SEGMENT_IN_USE(0x0001)가 켜져 있으면 쓰는 레코드입니다. 이 밖에 FILE_FILE_NAME_INDEX_PRESENT(0x0002)가 있습니다. |
| SequenceNumber | 레코드가 해제될 때마다 1씩 늘어납니다. 쓰이지 않은 레코드는 0 입니다. |
| BaseFileRecordSegment | 확장 레코드이면 기본 레코드를 가리킵니다. 기본 레코드이면 0 입니다. |

(표는 [1] 에서 옮겼습니다.)

- 0x0002 를 "폴더" 로 읽는 설명이 흔합니다. 문서에는 이름만 있습니다[1].
- 칸은 MultiSectorHeader, Reserved1(8), SequenceNumber(2), Reserved2(2), FirstAttributeOffset(2), Flags(2), Reserved3(8), BaseFileRecordSegment(8), Reserved4(2), UpdateSequenceArray 순서입니다[1].
- MultiSectorHeader 에는 "FILE" 서명과 업데이트 시퀀스 배열의 위치·크기가 있습니다[1].
- 참고한 문서에는 MultiSectorHeader 의 크기가 없습니다. 그래서 이 페이지에는 칸의 오프셋을 적지 않습니다. 오프셋은 [파일 레코드와 속성](../../01-foundations/disk-volume/ntfs/file-record-attribute.md) 에서 확인합니다.
- 이 구조는 NTFS 주 버전 3, 부 버전 0 또는 1 에만 맞는다고 문서에 적혀 있습니다[1].

**Flags 값 읽기.** 아래는 두 비트를 조합해 만든 예시 값입니다.

| Flags | 켜진 비트 | 레코드 상태 |
|---|---|---|
| 0x0000 | 없음 | 해제됨 |
| 0x0001 | IN_USE | 쓰는 중 |
| 0x0002 | FILE_NAME_INDEX_PRESENT | 해제됨 |
| 0x0003 | IN_USE, FILE_NAME_INDEX_PRESENT | 쓰는 중 |

**순번으로 레코드 재사용을 가립니다.**

파일 참조의 순번이 지금 레코드의 SequenceNumber 와 다르면 그 참조는 낡은 것입니다[1]. 셸백·바로가기 파일·$UsnJrnl 에는 파일 참조가 남으므로 이 순번을 지금 $MFT 와 비교하면 그 레코드를 다른 파일이 다시 썼는지 알 수 있습니다. 레코드를 다른 파일이 다시 쓰면 옛 파일의 정보는 덮입니다.

**이름으로 찾을 때.** 레코드가 $ATTRIBUTE_LIST 로 확장 레코드를 쓰면 Win32 긴 이름이 확장 레코드에만 있을 수 있는데(현장 관찰), 이때 기본 레코드만 보면 8.3 짧은 이름만 보입니다(현장 관찰). 그래서 긴 이름으로 찾아 나오지 않으면 BaseFileRecordSegment 로 확장 레코드를 기본 레코드에 묶어 다시 찾습니다.

해제된 레코드에서 내용을 되살리는 절차는 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에 있습니다.

## $UsnJrnl (변경 저널)

변경 저널 레코드 (USN_RECORD_V2) 의 칸은 RecordLength, MajorVersion, MinorVersion, FileReferenceNumber, ParentFileReferenceNumber, Usn, TimeStamp, Reason, SourceInfo, SecurityId, FileAttributes, FileNameLength, FileNameOffset, FileName 입니다[2].

- TimeStamp 는 64비트 UTC FILETIME 입니다[2].
- MajorVersion 2·3·4 가 각각 V2·V3·V4 구조입니다[2].
- Windows 8 이전에는 이 구조의 이름이 USN_RECORD 였습니다[2].
- FileName 은 끝 표시(0)에 기대지 않습니다. FileNameLength(바이트 수)만큼 잘라 읽습니다[2].
- 레코드에는 경로가 아니라 이름만 있습니다. 경로는 ParentFileReferenceNumber 로 부모 폴더를 따라가며 이어 붙입니다.

**Reason 은 쌓입니다.**

- Reason 은 파일이 열린 뒤 쌓인 변경 이유를 모은 값입니다[2].
- 파일이 닫히면 USN_REASON_CLOSE 가 켜진 마지막 레코드가 생깁니다[2].
- 다음 변경은 새 레코드에서 처음부터 다시 쌓입니다[2].
- 이름 바꾸기와 옮기기는 레코드 두 개를 만듭니다[2]. 하나에는 옛 부모 폴더가, 다른 하나에는 새 부모 폴더가 적힙니다[2].

**지우기와 관계있는 Reason 값.**

| 값 | 이름 |
|---|---|
| 0x00000001 | USN_REASON_DATA_OVERWRITE |
| 0x00000002 | USN_REASON_DATA_EXTEND |
| 0x00000004 | USN_REASON_DATA_TRUNCATION |
| 0x00000100 | USN_REASON_FILE_CREATE |
| 0x00000200 | USN_REASON_FILE_DELETE |
| 0x00001000 | USN_REASON_RENAME_OLD_NAME |
| 0x00002000 | USN_REASON_RENAME_NEW_NAME |
| 0x00008000 | USN_REASON_BASIC_INFO_CHANGE |
| 0x00010000 | USN_REASON_HARD_LINK_CHANGE |
| 0x80000000 | USN_REASON_CLOSE |

(값은 [2] 에서 골랐습니다. 이름 있는 스트림과 관계있는 값은 [이 파일은 어디서 왔나](file-origin.md) 에서, 나머지 값은 [USN 변경 저널](../../02-artifacts/filesystem/usnjrnl.md) 에서 봅니다.)

값을 조합해 만든 예시로 읽는 법을 보입니다. Reason 이 0x80000200 이면 USN_REASON_FILE_DELETE(0x00000200)와 USN_REASON_CLOSE(0x80000000)가 함께 켜진 것입니다. Reason 이 0x00001000 이면 이름 바꾸기의 옛 이름 쪽 레코드입니다. 이때는 같은 파일 참조로 USN_REASON_RENAME_NEW_NAME 이 켜진 레코드를 찾아 새 이름과 새 부모 폴더를 확인합니다.

**휴지통으로 보낸 파일.**

`$R` 은 원래 파일의 파일 ID 를 그대로 쓰므로 휴지통으로 보낸 때에는 저널에 USN_REASON_FILE_DELETE 가 아니라 이름 바꾸기 레코드가 남을 것으로 보입니다. 이 동작은 직접 확인하지 못했고, 휴지통을 비울 때 USN_REASON_FILE_DELETE 가 남는지도 확인하지 못했습니다. 검체에서 `$R` 이름이 든 레코드를 찾아 어떤 값이 켜졌는지 확인합니다.

**$J 를 뽑을 때 (현장 관찰).** `$UsnJrnl:$J` 는 앞부분이 비어 있는 희소 스트림인데(현장 관찰), 빈 구간을 0 으로 채워 뽑으면 논리 크기(수 GB)만큼의 파일이 나오고(현장 관찰), 빈 구간을 건너뛰어 뽑으면 실제 데이터만 남습니다(현장 관찰). 두 방법은 크기와 해시가 다르므로 어떤 방법으로 뽑았는지 기록에 적습니다. 희소 파일의 구조는 [NTFS 구조](../../01-foundations/disk-volume/ntfs/index.md) 에서 봅니다.

## 지운 뒤에도 남는 기록

| 기록 | 남는 것 | 링크 |
|---|---|---|
| 바로가기 파일·점프리스트 | 대상을 지운 뒤에도 대상 경로와 시각이 남습니다. | [바로가기 파일](../../02-artifacts/file-folder-usage/lnk.md) · [점프리스트](../../02-artifacts/file-folder-usage/jump-lists.md) |
| 셸백 | 폴더를 지워도 남습니다. 항목의 NTFS 파일 참조를 지금 $MFT 와 맞추면 지웠는지·옮겼는지·이름만 바꿨는지 가를 수 있습니다. | [셸백](../../02-artifacts/file-folder-usage/shellbags/index.md) |
| 윈도 검색 색인 | 지금 없는 파일의 기록이 남을 수 있습니다. | [윈도 검색 색인 DB](../../02-artifacts/file-folder-usage/windows-search/index.md) |
| 프리페치·AmCache | 지운 실행 파일의 경로와 SHA-1 이 남을 수 있습니다. | [프리페치](../../02-artifacts/execution/prefetch/index.md) · [AmCache](../../02-artifacts/execution/amcache-hve/index.md) |
| 썸네일 캐시 | 미리 보기 그림(세부는 링크 페이지) | [썸네일 캐시](../../02-artifacts/file-folder-usage/thumbcache-db-thumbs-db.md) |
| 브라우저 기록 | 지운 방문 기록의 단서 | [웹 사용 행위 재구성](web-activity.md) |
| ESE·레지스트리 | 지운 레코드, 지운 키와 값 | [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) · [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) |

**윈도 검색 색인.**

- Windows 11 의 색인 DB 에서는 변경 내용이 본 DB 에 쓰이기 전까지 WAL 에 지금 없는 파일의 기록이 남을 수 있습니다.
- ESE 형식의 색인 DB 에는 SystemIndex_DeletedDocIds 표가 있습니다.
- Windows 8·10 의 SystemIndex_PropertyStore 표는 열 이름 앞에 숫자 속성 ID 와 선택적 'F' 가 붙습니다(현장 관찰). 그래서 속성 이름만으로 열을 찾으면 0건이 나옵니다(현장 관찰).

## 이벤트 로그

**4663 의 삭제 권한.**

| AccessMask | 이름 | AccessList 표시 |
|---|---|---|
| 0x10000 | DELETE | %%1537 |
| 0x40 | DeleteChild | %%4422 |

(값은 [3] 의 표에서 골랐습니다.)

- 4663 은 SACL 이 걸린 개체에서만 남고[3], 접근 권한에 DELETE 가 있으면 삭제 권한을 썼다는 기록입니다[3].
- 4663 의 다른 칸과 다른 이벤트와 잇는 법은 [이 파일을 누가 언제 열었나](file-access.md) 의 "보안 로그 4663" 절에 있습니다.
- 개체 삭제 이벤트 4660 의 뜻과 칸은 [파일 접근 감사](../../02-artifacts/event-logs/4656-4663-4660.md) 에서 봅니다.

**Sysmon.**

| 이벤트 | 남는 것 |
|---|---|
| 23 FileDelete | 지운 파일을 `ArchiveDirectory` 에 보관하고 기록합니다. 보관 폴더의 기본 이름은 `Sysmon` 이고(C: 에서는 `C:\Sysmon`), 볼륨 루트에 있습니다. 이 폴더에는 System ACL 이 걸려 있습니다. |
| 26 FileDeleteDetected | 보관하지 않고 기록만 합니다. |
| 28 FileBlockShredding | SDelete 같은 완전삭제 도구를 막을 때 생깁니다. |

(표는 [4] 에서 옮겼습니다.)

- 23 을 켜 둔 PC 에서는 볼륨 루트의 보관 폴더에서 지운 파일의 사본을 찾습니다.
- 완전삭제 도구를 쓴 흔적은 [증거를 없애려 했나](anti-forensics/index.md) 에서 다룹니다.

## 복구 가능성

NTFS 에서 TRIM(삭제 알림)은 관리자가 끄지 않는 한 기본으로 켜져 있고[5], 저장 장치가 TRIM 을 지원하지 않으면 알림이 가지 않습니다[5]. 설정은 `fsutil behavior query DisableDeleteNotify` 로 확인하는데[5], 이 명령은 실행 중인 시스템에서 씁니다. 이미지만 있으면 저장 장치 종류를 먼저 적어 두고, 복구 결과와 함께 판단합니다.

- 해제된 레코드로 되살리기, 카빙, 비할당 영역 검색은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.
- 지우기 전 시점의 파일은 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 찾습니다.

## 분석 흐름

1. Windows 버전·시간대·사용자 SID·저장 장치 종류를 정리합니다. 감사 정책과 Sysmon 설치 여부를 적습니다.
2. 볼륨마다 `$Recycle.Bin` 의 SID 별 폴더에서 `$I` 를 읽고, 원래 경로가 대상과 같은 항목을 찾습니다. 짝이 되는 `$R` 이 있으면 내용을 확보합니다.
3. $MFT 에서 IN_USE 가 꺼진 레코드를 이름으로 찾습니다. 긴 이름이 확장 레코드에만 있을 수 있으므로 확장 레코드까지 묶어 봅니다.
4. $UsnJrnl 에서 대상 이름으로 레코드를 찾습니다. FILE_CREATE, RENAME_OLD_NAME·RENAME_NEW_NAME, FILE_DELETE 가 켜진 레코드의 시각을 적습니다. 경로는 ParentFileReferenceNumber 로 이어 붙입니다.
5. 이름 바꾸기 레코드가 있으면 새 이름과 새 부모 폴더로 파일을 다시 찾습니다. 옮긴 파일을 지운 파일로 적지 않습니다.
6. 바로가기 파일·점프리스트·셸백·검색 색인·프리페치·AmCache 에서 같은 경로를 찾습니다. 남은 파일 참조의 순번을 지금 $MFT 와 비교합니다.
7. 감사가 켜져 있었으면 4663 을 ObjectName 과 DELETE 권한으로 찾습니다. Sysmon 이 있으면 23·26·28 을 봅니다.
8. 섀도 복사본에서 지우기 전 시점의 파일과 기록을 봅니다.
9. 내용이 필요하면 저장 장치 종류와 TRIM 설정을 확인한 뒤 복구와 카빙을 시도합니다.
10. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올립니다. 시각 값의 형식은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 확인합니다.
11. 완전삭제 도구나 일괄 삭제 흔적이 보이면 [증거를 없애려 했나](anti-forensics/index.md) 로 이어 갑니다. 그 시각에 누가 PC 앞에 있었는지는 [그 시각에 PC 를 쓴 사람이 누구인가](user-attribution.md) 로 좁힙니다.

## 흔한 오판

1. **`$I` 의 시각을 사람이 파일을 지운 시각으로 씁니다.** 이 시각은 휴지통으로 옮긴 시각입니다. 누가 옮겼는지는 이 기록만으로 알 수 없습니다.
2. **흔적이 없으니 지우지 않았다고 봅니다.** 휴지통을 거치지 않는 삭제가 많습니다. 저널에서도 오래된 레코드는 없어질 수 있습니다.
3. **`$I` 만 있고 `$R` 이 없으니 휴지통을 비웠다고 봅니다.** 복원한 뒤에도 `$I` 가 남습니다.
4. **이름 바꾸기·옮기기를 삭제로 읽습니다.** 이름 바꾸기와 옮기기는 저널에 레코드 두 개를 남깁니다[2]. 새 이름 쪽 레코드를 찾아 확인합니다.
5. **다시 쓰인 레코드의 정보를 옛 파일의 정보로 씁니다.** 레코드를 다른 파일이 다시 쓰면 옛 정보는 덮입니다. 파일 참조의 순번으로 가립니다[1].
6. **기본 레코드에 긴 이름이 없으니 그 파일이 없었다고 봅니다.** 긴 이름이 확장 레코드에만 있을 수 있습니다(현장 관찰).
7. **4663 이 없으니 지우지 않았다고 봅니다.** 감사가 꺼져 있었거나 SACL 이 없었을 수 있습니다[3].

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 ○○ 에 계약서.docx 를 삭제했습니다."
- 휴지통 기록이 있을 때: "`C:\$Recycle.Bin\○○\`(사용자 ○○ 의 SID) 에 `$I○○.docx` 가 있습니다. 이 파일에 적힌 원래 경로는 `○○\계약서.docx` 입니다. 휴지통으로 옮긴 시각은 ○○(UTC) 입니다. 짝이 되는 `$R○○.docx` 는 없습니다. 이 기록은 이 파일이 이 계정의 휴지통 폴더로 들어갔음을 보여 줍니다. `$R` 이 없는 까닭과 옮긴 사람은 이 기록만으로 정할 수 없습니다."
- 저널 기록이 있을 때: "C: 볼륨의 $UsnJrnl 에 파일 이름 `계약서.docx` 의 레코드가 있습니다. Reason 에 USN_REASON_FILE_DELETE 가 켜진 레코드의 TimeStamp 는 ○○(UTC) 입니다. 이 기록은 이 시각에 이 볼륨에서 이 파일이 지워졌음을 보여 줍니다. 어느 프로세스와 계정이 지웠는지는 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [휴지통](../../02-artifacts/file-folder-usage/recycle-bin.md) — `$I`·`$R` 의 구조입니다.
- [마스터 파일 테이블](../../02-artifacts/filesystem/mft.md) · [NTFS 구조](../../01-foundations/disk-volume/ntfs/index.md) — 파일 레코드와 속성의 구조입니다.
- [USN 변경 저널](../../02-artifacts/filesystem/usnjrnl.md) · [NTFS 트랜잭션 로그](../../02-artifacts/filesystem/logfile.md) — 파일 시스템 변경 기록입니다.
- [타임라인 작성](../../03-techniques/analysis/timeline/index.md) — 파일 시스템 기록을 한 줄로 세웁니다.
- [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) · [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) — 내용을 되살립니다.
- [증거를 없애려 했나](anti-forensics/index.md) — 완전삭제 도구와 흔적 지우기를 봅니다.
- [이 파일을 누가 언제 열었나](file-access.md) — 지우기 전에 파일을 다룬 기록입니다.
- [이 파일은 어디서 왔나](file-origin.md) — 지운 파일이 들어온 길입니다.

## 참고 문헌

1. Microsoft Learn, "FILE_RECORD_SEGMENT_HEADER structure" — https://learn.microsoft.com/en-us/windows/win32/devnotes/file-record-segment-header
2. Microsoft Learn, "USN_RECORD_V2 structure" — https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-usn_record_v2
3. Microsoft Learn, "4663(S) An attempt was made to access an object." (Windows 10 보관 문서) — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4663
4. Microsoft Learn, "Sysmon - Sysinternals" (2026-09-10 판) — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
5. Microsoft Learn, "fsutil behavior" — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-behavior
