# NTFS 구조 (NTFS)

## 한 줄 요약

NTFS (New Technology File System) 는 Windows 가 기본으로 쓰는 파일 시스템입니다. 볼륨 안의 모든 파일과 폴더는 마스터 파일 테이블 (Master File Table, MFT) 에 레코드로 적힙니다.

## 왜 중요한가

- Windows 아티팩트는 대부분 NTFS 볼륨 위에 있는 파일입니다. 레지스트리 하이브도, 이벤트 로그도, 프리페치도 NTFS 위의 파일입니다.
- 그래서 디스크 이미지에서 아티팩트를 꺼내는 일은 곧 NTFS 를 읽는 일입니다. 도구가 NTFS 를 잘못 읽으면 그 뒤의 분석도 모두 틀어집니다.
- MFT 에는 파일마다 최소 한 개의 레코드가 있습니다. 파일의 크기, 시각, 권한, 데이터 위치가 모두 이 레코드에 있거나, 이 레코드가 가리키는 곳에 있습니다.
- 파일을 지우면 그 MFT 레코드는 "비어 있음" 으로 표시됩니다. 레코드는 다른 파일이 다시 쓸 때까지 그 자리에 남습니다.
- 파일을 지워도 MFT 크기는 줄지 않습니다. 그래서 지운 파일의 레코드를 MFT 안에서 찾을 수 있습니다.
- 파일 하나에 시각이 두 벌 있습니다. 두 벌은 바뀌는 조건이 다릅니다. 이 차이가 시각 조작을 가려내는 단서가 됩니다.
- NTFS 의 시각 값은 UTC 기준 FILETIME 으로 저장됩니다. 화면에 보이는 현지 시각은 도구가 시간대를 적용해 바꾼 값입니다. 값 형식은 [시각 값 형식](../../value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.

## 한눈에 보기

### 볼륨을 이루는 메타 파일

NTFS 는 자기 관리 정보도 파일로 둡니다. 이 파일들을 메타 파일 (Metadata File) 이라고 합니다. 메타 파일은 MFT 의 앞쪽 고정 번호에 있습니다.

| 메타 파일 | 위치 | NTFS 버전 | 알려 주는 것 |
|---|---|---|---|
| $MFT | MFT 0번 | 모든 버전 | 파일·폴더마다 이름, 크기, 시각, 데이터 위치 |
| $MFTMirr | MFT 1번 | 모든 버전 | $MFT 앞 레코드 4개의 사본 |
| $LogFile | MFT 2번 | 모든 버전 | 메타데이터 변경을 적은 트랜잭션 로그 |
| $Volume | MFT 3번 | 모든 버전 | 볼륨 이름, NTFS 버전, 검사가 필요하다는 표시(더티 플래그) |
| $AttrDef | MFT 4번 | 모든 버전 | 속성 종류의 정의 |
| 루트 폴더 (.) | MFT 5번 | 모든 버전 | 폴더 트리가 시작하는 곳 |
| $Bitmap | MFT 6번 | 모든 버전 | 클러스터마다 쓰는 중인지 비어 있는지 |
| $Boot | MFT 7번 (볼륨 첫 섹터부터) | 모든 버전 | 섹터·클러스터 크기, $MFT 시작 위치, 볼륨 일련번호 |
| $BadClus | MFT 8번 | 모든 버전 | 불량 클러스터 목록 |
| $Secure | MFT 9번 | 3.0 이상 | 여러 파일이 함께 쓰는 보안 설명자 (Security Descriptor) |
| $UpCase | MFT 10번 | 모든 버전 | 이름을 비교할 때 쓰는 대문자 표 |
| $Extend | MFT 11번 (폴더) | 3.0 이상 | 아래 확장 메타 파일을 담는 폴더 |
| $Extend\$UsnJrnl | $J·$Max 스트림 | 3.0 이상 | 파일이 바뀐 기록 (변경 저널) |
| $Extend\$ObjId·$Quota·$Reparse | $Extend 폴더 안 | 3.0 이상 | 개체 ID, 사용량 한도, 리파스 포인트 목록 |
| $Extend\$RmMetadata | $Extend 폴더 안 | Windows Vista 이상 | 트랜잭션 NTFS (TxF) 자료 |

- MFT 9번은 NTFS 1.2 에서 $Quota 였습니다. NTFS 3.0 부터 $Secure 로 바뀌었습니다.
- MFT 12~15번은 "쓰는 중" 으로 표시되지만 비어 있습니다. 16~23번은 비어 있는 예약 자리입니다.

> 그림 자리: 볼륨 한 개를 가로 막대로 그린 배치도. 맨 앞 부트 섹터, $MFT 와 그 뒤 예약 영역(MFT 존), 일반 데이터 영역, $MFTMirr 위치를 표시하고, $MFT 0~11번 레코드가 각 메타 파일을 가리키는 화살표를 넣는다.

### NTFS 버전과 Windows

| NTFS 버전 | 처음 쓴 Windows | 달라진 점 |
|---|---|---|
| 1.2 | Windows NT 3.51 | MFT 9번이 $Quota |
| 3.0 | Windows 2000 | $Secure, $Extend 폴더, 변경 저널이 생김 |
| 3.1 | Windows XP | XP 이후 지금까지 이 버전을 씁니다 |

### 알아 둘 기본값

- 클러스터 (Cluster) 는 NTFS 가 공간을 나눠 주는 단위입니다. 기본 크기는 4KB 입니다. 볼륨마다 다를 수 있으므로 부트 섹터에서 읽어야 합니다.
- MFT 레코드는 보통 1,024바이트입니다. 큰 레코드 (Large File Record Segment) 옵션으로 포맷한 볼륨은 레코드가 더 큽니다. 레코드 크기도 부트 섹터에서 읽어야 합니다.
- $MFT 도 파일입니다. 그래서 $MFT 도 조각나서 여러 곳에 흩어질 수 있습니다.
- 8.3 짧은 이름 만들기는 `NtfsDisable8dot3NameCreation` 값으로 시스템 전체나 볼륨마다 끌 수 있습니다. 값 3 은 시스템 볼륨만 빼고 모두 끕니다([fsutil 8dot3name](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-8dot3name)). 그래서 짧은 이름이 없는 파일이 있어도 이상한 일이 아닙니다.

## 읽는 순서

아래 순서대로 읽으면 볼륨 첫 섹터에서 출발해 파일 내용까지 따라갈 수 있습니다.

1. [부트 섹터와 클러스터 (Boot Sector·Cluster)](boot-sector-cluster.md) — 볼륨 첫 섹터에서 섹터 크기, 클러스터 크기, $MFT 위치, 레코드 크기를 읽습니다. 뒤의 모든 계산이 여기서 시작합니다.
2. [MFT 레코드와 속성 (FILE Record·Attribute)](file-record-attribute.md) — 레코드 머리글, 섹터 끝 바이트를 되돌리는 고정값 (Fixup), 속성 (Attribute) 목록을 읽습니다. 레코드 하나에 다 담기지 않는 파일은 $ATTRIBUTE_LIST 로 확장 레코드를 씁니다. 이때 긴 이름이 확장 레코드에만 있을 수 있습니다 (현장 관찰).
3. [데이터 런과 상주·비상주 데이터 (Data Run·Resident·Non-resident)](data-run-resident-non-resident.md) — 작은 파일은 내용이 레코드 안에 있습니다. 큰 파일은 데이터 런으로 클러스터 위치를 적습니다. 조각난 파일과 조각난 $MFT 를 이 방법으로 따라갑니다.
4. [두 벌의 시각 ($STANDARD_INFORMATION·$FILE_NAME)](standard-information-file-name.md) — 두 속성의 시각이 각각 언제 바뀌는지 봅니다. 시각 조작을 찾는 방법의 바탕입니다.
5. [대체 데이터 스트림 (ADS)](ads.md) — 파일 하나에 이름 있는 $DATA 스트림이 여럿 붙을 수 있습니다. 탐색기에는 보이지 않습니다. 다운로드 출처를 적는 Zone.Identifier 가 대표 예입니다.
6. [압축·희소 파일 (Compressed·Sparse)](compressed-sparse.md) — 압축된 파일과 구멍이 있는 희소 파일은 데이터 런이 다르게 생겼습니다. $UsnJrnl:$J 도 희소 스트림입니다. 구멍을 0 으로 채워 뽑는지, 건너뛰고 뽑는지에 따라 크기와 해시가 달라집니다 (현장 관찰).
7. [링크와 리파스 포인트 (Hard Link·Junction·Reparse Point)](hard-link-junction-reparse-point.md) — 하드 링크 이름과 8.3 짧은 이름도 $FILE_NAME 속성에 들어갑니다. 정션과 심볼릭 링크는 리파스 포인트로 다른 경로를 가리킵니다.
8. [NTFS 메타 파일 ($Bitmap·$Secure·$Extend)](bitmap-secure-extend.md) — $Bitmap 으로 클러스터가 쓰이는지 확인하고, $Secure 로 권한을 찾고, $Extend 안의 파일들을 봅니다.

## 함께 볼 페이지

이 구조 위에서 읽는 아티팩트입니다.

- [마스터 파일 테이블 ($MFT)](../../../02-artifacts/filesystem/mft.md) — MFT 를 증거로 해석하는 법
- [NTFS 트랜잭션 로그 ($LogFile)](../../../02-artifacts/filesystem/logfile.md) — 메타데이터 변경 기록
- [USN 변경 저널 ($UsnJrnl)](../../../02-artifacts/filesystem/usnjrnl.md) — 파일 생성·삭제·이름 변경 기록
- [폴더 인덱스와 슬랙 ($I30)](../../../02-artifacts/filesystem/i30.md) — 폴더 목록 B-트리와 그 안에 남은 옛 항목
- [다운로드 출처 표시 (Zone.Identifier)](../../../02-artifacts/filesystem/zone-identifier.md) — ADS 를 쓰는 대표 아티팩트

이 구조를 쓰는 분석 기법입니다.

- [파일시스템 타임라인 (Filesystem Timeline: $MFT·$UsnJrnl·$LogFile)](../../../03-techniques/analysis/timeline/filesystem-timeline-mft-usnjrnl-logfile.md)
- [시각 조작 탐지 (Timestomping)](../../../03-techniques/analysis/timeline/timestomping.md)
- [파일시스템 기반 복구 (Undelete: NTFS·FAT)](../../../03-techniques/analysis/data-recovery/undelete-ntfs-fat.md)
- [비할당 영역과 슬랙 (Unallocated·Slack Space)](../../../03-techniques/analysis/data-recovery/unallocated-slack-space.md)
- [섀도 복사본 활용 (Volume Shadow Copy Analysis)](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)
- [SSD TRIM과 복구 한계 (SSD·TRIM)](../../../03-techniques/analysis/data-recovery/ssd-trim.md)
- [EFS 암호화 파일 (Encrypting File System)](../../../03-techniques/analysis/encrypted-evidence/encrypting-file-system.md)
- [도구 결과 교차 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)

NTFS 앞뒤에 있는 구조입니다.

- [증거 이미지·가상 디스크 형식 (E01·RAW·AFF4·VHDX·VMDK)](../e01-raw-aff4-vhdx-vmdk.md)
- [파티션 구조 (MBR·GPT)](../mbr-gpt.md)
- [FAT·exFAT 구조 (FAT·exFAT)](../fat-exfat.md)
- [볼륨 섀도 복사본 구조 (Volume Shadow Copy)](../volume-shadow-copy.md)
- [윈도 압축 형식 (LZNT1·Xpress·Xpress Huffman)](../../value-decoding/lznt1-xpress-xpress-huffman.md)
- [시각 값 형식 (FILETIME·Unix·WebKit·DOS·OLE)](../../value-decoding/filetime-unix-webkit-dos-ole.md)

이 구조가 쓰이는 조사 시나리오입니다.

- [지운 파일의 흔적 찾기 (Deleted File Traces)](../../../04-scenarios/activity/deleted-file-traces.md)
- [이 문서의 날짜를 믿을 수 있나 (Document Date Verification)](../../../04-scenarios/activity/document-date-verification.md)

## 참고 문헌

1. libyal, "New Technologies File System (NTFS)" 형식 문서 (libfsntfs). https://github.com/libyal/libfsntfs/blob/main/documentation/New%20Technologies%20File%20System%20(NTFS).asciidoc
2. Microsoft Learn, "Master File Table (Local File Systems)". https://learn.microsoft.com/en-us/windows/win32/fileio/master-file-table
3. Microsoft Learn, "NTFS overview". https://learn.microsoft.com/en-us/windows-server/storage/file-server/ntfs-overview
4. Microsoft Learn, "File Streams (Local File Systems)". https://learn.microsoft.com/en-us/windows/win32/fileio/file-streams
5. Linux-NTFS Project, "NTFS Documentation: Files". https://flatcap.github.io/linux-ntfs/ntfs/files/index.html
6. Dave Hull, "Digital Forensics: Detecting time stamp manipulation", SANS DFIR Blog, 2010. https://www.sans.org/blog/digital-forensics-detecting-time-stamp-manipulation
7. Microsoft Learn, "fsutil 8dot3name". https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-8dot3name
