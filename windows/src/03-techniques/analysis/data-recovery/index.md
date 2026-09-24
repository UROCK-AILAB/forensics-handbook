# 삭제 데이터 복구 (Data Recovery)

## 한 줄 요약

파일을 지워도 데이터는 대개 매체에 남습니다. 이 묶음은 남은 데이터를 파일시스템 기록, 빈 공간과 슬랙, 파일·레코드 서명으로 되살리는 방법을 다룹니다. SSD 에서 복구가 어디서 막히는지도 함께 다룹니다.

## 왜 중요한가

파일을 지우면 파일 위치를 가리키는 디렉터리 자료에 "삭제" 표시만 남고 매체의 데이터는 대개 지워지지 않습니다. OS 는 그 공간을 빈 공간으로 보고 언제든 덮어쓸 수 있습니다. 그래서 되살린 내용이 원래 파일의 것인지는 따로 확인해야 합니다.

수집 방식이 복구 범위를 정하는데, 파일·폴더를 복사하는 논리 백업에는 지운 파일과 슬랙의 옛 데이터가 담기지 않고 비트 단위 이미지에는 빈 공간과 슬랙까지 담깁니다. 방법마다 돌아오는 정보도 다른데, 파일시스템 기록으로 되살리면 이름과 시각이 함께 나올 수 있지만 파일 카빙 결과에는 파일 이름과 시각이 없습니다.

SSD 는 사정이 다릅니다. Windows 의 NTFS 는 기본으로 TRIM(삭제 알림)이 켜져 있고, TRIM 이 내려가고 드라이브 내부 정리가 끝나면 지운 데이터 복구는 어렵거나 불가능할 수 있습니다.

## 한눈에 보기

| 방법 | 무엇을 보고 판단하나 | 알려 주는 것 | Windows 버전 | 자세히 |
|---|---|---|---|---|
| 파일시스템 기반 복구 — NTFS | MFT 레코드의 사용 중 플래그와 $Bitmap | 지운 파일의 이름·크기·시각·데이터 위치 | — | [파일시스템 기반 복구](undelete-ntfs-fat.md) |
| 파일시스템 기반 복구 — FAT12·FAT16·FAT32 | 디렉터리 항목 첫 바이트 0xE5 (할당 안 된 항목) | 짧은 이름·크기·시각·시작 클러스터 | — | [파일시스템 기반 복구](undelete-ntfs-fat.md) |
| 파일시스템 기반 복구 — exFAT | 항목 종류 바이트의 bit 7(InUse)이 0 이면 쓰지 않는 항목 | 파일 항목의 시각, 시작 클러스터와 길이 | — | [파일시스템 기반 복구](undelete-ntfs-fat.md) |
| 비할당 영역·슬랙 | 할당 비트맵과 FAT 표에서 비어 있는 클러스터, 파일 끝 뒤 남는 공간 | 옛 데이터 조각. 비트 단위 이미지에만 담깁니다. | — | [비할당 영역과 슬랙](unallocated-slack-space.md) |
| 파일 카빙 | 파일 형식 서명과 끝 표시 | 파일 내용. 파일 이름·시각 같은 메타정보는 돌아오지 않습니다. | — | [파일 카빙](file-carving.md) |
| 레코드 카빙 | 레코드 서명과 형식 안의 검사 값. EVTX 레코드는 크기와 끝의 크기 사본을 맞춰 봅니다. | 레코드 하나. EVTX 레코드면 레코드 번호와 쓴 시각 | — | [레코드 카빙](record-carving.md) |
| SSD·TRIM | 삭제 알림 설정과 retrim 기록 | 복구를 기대할 수 있는 범위 | Windows 7·Server 2008 R2 부터 TRIM 지원 | [SSD TRIM과 복구 한계](ssd-trim.md) |

"—" 는 Windows 버전보다 파일시스템이나 파일의 형식을 기준으로 보는 방법이라는 뜻입니다. TRIM 의 버전별 지원 범위는 SSD 페이지에 표로 정리했습니다.

> 그림 자리: 지운 파일 하나를 두고, 디렉터리 자료(파일시스템 기반 복구) → 비할당 클러스터와 슬랙 → 서명으로 찾기(파일·레코드 카빙) 순서로 남은 정보가 줄어드는 모습. 옆에 SSD 는 TRIM 뒤 클러스터 내용이 사라지는 갈래를 그린 그림

## 읽는 순서

지운 데이터는 남은 정보가 많은 방법부터 찾습니다. 먼저 [휴지통](../../../02-artifacts/file-folder-usage/recycle-bin.md) 과 [섀도 복사본 활용](../volume-shadow-copy-analysis.md) 에서 파일이 그대로 남았는지 봅니다. 그다음 아래 순서로 읽습니다.

1. [파일시스템 기반 복구 (Undelete: NTFS·FAT)](undelete-ntfs-fat.md) — MFT 레코드와 FAT·exFAT 디렉터리 항목에서 지운 파일의 이름·크기·데이터 위치를 읽습니다. 되살린 내용에 다른 파일의 데이터가 섞였는지 가리는 법도 다룹니다.
2. [비할당 영역과 슬랙 (Unallocated·Slack Space)](unallocated-slack-space.md) — 어느 파일에도 속하지 않은 클러스터와 파일 끝 뒤에 남는 공간을 다룹니다. 파일시스템마다 찾는 자리와 뽑는 절차를 정리합니다.
3. [파일 카빙 (File Carving)](file-carving.md) — 파일시스템 정보 없이 서명과 끝 표시로 파일을 되살립니다. 조각난 파일과 메타정보가 없는 결과를 어떻게 읽는지 다룹니다.
4. [레코드 카빙 (Record Carving)](record-carving.md) — EVTX 레코드와 MFT 레코드·색인 블록을 레코드 단위로 찾습니다. 크기 사본·CRC32·fix-up 으로 진짜 레코드인지 가립니다.
5. [SSD TRIM과 복구 한계 (SSD·TRIM)](ssd-trim.md) — TRIM 과 드라이브 내부 정리가 복구를 어떻게 막는지 다룹니다. Windows 버전별 지원과 설정·retrim 기록을 확인하는 법을 정리합니다.

## 함께 볼 페이지

- [지운 파일의 흔적 찾기](../../../04-scenarios/activity/deleted-file-traces.md) — 조사 질문에서 출발해 이 묶음의 방법을 어느 단계에서 쓰는지 봅니다.
- [증거 획득](../../process-acquisition/evidence-acquisition/index.md) — 빈 공간과 슬랙까지 담는 비트 단위 이미지를 뜨는 법입니다.
- [NTFS 구조](../../../01-foundations/disk-volume/ntfs/index.md), [FAT·exFAT 구조](../../../01-foundations/disk-volume/fat-exfat.md) — 복구에 쓰는 값이 들어 있는 파일시스템 구조입니다.
- [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md), [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) — 지운 파일의 이름과 시각을 보강하는 기록입니다.
- [파일 내용 검색](../content-search/index.md) — 비할당 영역과 슬랙에서 키워드를 찾는 법입니다.
- [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) — 완전삭제 도구를 썼는지 다른 기록과 함께 가립니다.
- [도구 결과 교차 검증](../../reporting/tool-validation.md) — 복구 도구마다 결과가 다를 때 따를 절차입니다.

## 참고 문헌

1. NIST SP 800-86, "Guide to Integrating Forensic Techniques into Incident Response" (2006년 8월) — https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf
2. libyal/libfsntfs, "New Technologies File System (NTFS)" 형식 문서 — https://raw.githubusercontent.com/libyal/libfsntfs/main/documentation/New%20Technologies%20File%20System%20(NTFS).asciidoc
3. libyal/libfsfat, "File Allocation Table (FAT) format" 형식 문서 — https://raw.githubusercontent.com/libyal/libfsfat/main/documentation/File%20Allocation%20Table%20(FAT)%20format.asciidoc
4. Microsoft Learn, "exFAT file system specification" — https://learn.microsoft.com/en-us/windows/win32/fileio/exfat-specification
5. Wikipedia, "File carving" — https://en.wikipedia.org/wiki/File_carving
6. CGSecurity, "PhotoRec" — https://www.cgsecurity.org/wiki/PhotoRec
7. libyal/libevtx, "Windows XML Event Log (EVTX)" 형식 문서 — https://raw.githubusercontent.com/libyal/libevtx/main/documentation/Windows%20XML%20Event%20Log%20(EVTX).asciidoc
8. Microsoft Learn, "fsutil behavior" — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-behavior
9. Wikipedia, "Trim (computing)" — https://en.wikipedia.org/wiki/Trim_(computing)
