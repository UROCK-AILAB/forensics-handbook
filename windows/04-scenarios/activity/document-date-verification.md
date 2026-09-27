---
title: "이 문서의 날짜를 믿을 수 있나"
parent: "시나리오 · 행위 재구성"
nav_order: 3870
---

# 이 문서의 날짜를 믿을 수 있나 (Document Date Verification)

문서 파일 하나를 두고 "여기 적힌 날짜에 정말 만들고 고쳤나" 를 묻는 조사를 다룹니다. 계약서의 작성일, 보고서의 수정일처럼 날짜 자체가 다툼거리가 되는 사건에서 자주 나옵니다. 문서의 날짜는 파일 시스템, 문서 안의 속성, 주변 기록 세 곳에 따로 남습니다. 이 페이지는 세 곳의 날짜가 무엇을 뜻하는지, 서로 어긋날 때 어떻게 읽는지를 정리합니다.

형식마다의 속성 구조는 [문서 메타데이터](../../02-artifacts/embedded-metadata/document-metadata/index.md) 에 있습니다.

## 조사 질문

- 이 문서는 적힌 날짜에 만들었습니까?
- 마지막으로 고친 때는 언제입니까?
- 누가 날짜를 바꾼 흔적이 있습니까?
- 다른 PC 나 저장 장치에서 옮겨 온 문서입니까?

## 먼저 확인할 것

| 확인할 것 | 이유 |
|---|---|
| 파일 시스템 종류 | NTFS 는 시각을 UTC 로 저장합니다[1]. FAT 는 컴퓨터의 로컬 시각으로 저장합니다[1]. [NTFS 구조](../../01-foundations/disk-volume/ntfs/index.md) 와 [FAT·exFAT 구조](../../01-foundations/disk-volume/fat-exfat.md) 를 봅니다. |
| 시간대 | FAT 의 시각과 문서 안의 현지 시각을 UTC 로 바꾸려면 시간대가 필요합니다. [시간대 설정](../../02-artifacts/system-account/time-zone.md) 을 읽고, Bias 값은 [이 파일을 누가 언제 열었나](file-access.md) 의 "먼저 확인할 것" 에 적은 대로 부호 있는 수로 읽습니다. |
| 시스템 시각 변경 | PC 의 시각을 바꾸고 문서를 저장하면 파일 시스템 시각과 문서 안의 시각이 함께 틀어집니다. [시간 변경](../../02-artifacts/event-logs/4616-kernel-general.md) 과 [증거를 없애려 했나](anti-forensics/index.md) 를 먼저 봅니다. |
| 문서 형식 | 형식마다 날짜 속성이 들어 있는 곳이 다릅니다. 아래 "문서 안의 날짜" 를 봅니다. |
| 수집 범위 | 문서 원본 파일, $MFT, $UsnJrnl:$J, $LogFile, 사용자 하이브, 윈도 검색 색인 DB 를 함께 확보합니다. 지난 시점의 문서는 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 봅니다. |

## 날짜가 남는 세 곳

| 층 | 무엇이 있나 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1. 파일 시스템 | $MFT 의 만든·쓴·접근 시각 | 이 볼륨에서 이 파일에 일어난 일 | [마스터 파일 테이블](../../02-artifacts/filesystem/mft.md) |
| 2. 문서 안 | 만든 시각, 마지막 저장 시각, 마지막 저장한 사람, 개정 번호 | 문서 내용과 함께 적힌 값 | [문서 메타데이터](../../02-artifacts/embedded-metadata/document-metadata/index.md) |
| 3. 주변 기록 | USN 변경 저널, NTFS 트랜잭션 로그, 폴더 인덱스, 바로가기, 점프리스트, 오피스 사용 흔적, 검색 색인, 섀도 복사본 | 1·2 층과 따로 남은 시각 | 아래 "주변 기록으로 맞춰 보기" |

세 층은 서로 다른 때에 다른 주체가 씁니다. 한 층의 값만으로 날짜를 확정하지 않습니다. 층끼리 맞는지 봅니다.

## 파일 시스템의 날짜

**언제 바뀌나.**

시스템은 응용 프로그램이 파일을 만들고, 읽고, 쓸 때 파일 시각을 기록하지만[1], 시각을 언제 갱신하는지는 여러 이유로 달라집니다[1]. 보장되는 것은 "바꾼 핸들이 닫힐 때 시각이 맞게 반영된다" 는 것 하나뿐이라서[1], 파일에 쓸 때 마지막 쓴 시각은 쓰기에 쓴 핸들이 모두 닫혀야 완전히 갱신됩니다[1]. 또 모든 파일 시스템이 만든 시각과 마지막 접근 시각을 기록하지는 않고[1], 기록하는 방식도 같지 않습니다[1].

- NTFS 의 마지막 접근 시각은 [이 파일을 누가 언제 열었나](file-access.md) 의 "마지막 접근 시각" 절에서 다룹니다.

**FAT 의 해상도.**

| 시각 | 해상도 |
|---|---|
| 만든 시각 | 10밀리초[1] |
| 쓴 시각 | 2초[1] |
| 접근 시각 | 1일. 사실상 날짜만 남습니다[1]. |

**바꿀 수 있나.**

- `SetFileTime` 함수로 파일 내용을 바꾸지 않고 만든 시각·접근 시각·쓴 시각을 바꿀 수 있습니다[1].
- 그래서 파일 시스템 시각 하나만으로 날짜를 확정하지 않습니다.
- $MFT 에는 $STANDARD_INFORMATION 과 $FILE_NAME 두 곳에 시각이 있습니다. 두 곳을 비교하는 법은 [마스터 파일 테이블](../../02-artifacts/filesystem/mft.md) 과 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.
- 비교할 때는 확장 레코드까지 봅니다. $ATTRIBUTE_LIST 로 확장 레코드를 쓰는 파일은 긴 이름의 $FILE_NAME 이 확장 레코드에만 있을 수 있습니다. 기본 레코드만 보면 8.3 짧은 이름만 보입니다. 확장 레코드는 대개 기본 레코드와 멀리 떨어져 있습니다. 레코드 구조는 [NTFS 구조](../../01-foundations/disk-volume/ntfs/index.md) 에 있습니다.

**현지 시각으로 바꿀 때.**

`FileTimeToLocalFileTime` 은 "지금" 의 시간대·일광 절약 설정을 쓰기 때문에 표준시 기간의 시각도, 지금이 일광 절약 기간이면 한 시간 어긋나게 바뀝니다[1].

- NTFS 시각을 현지 시각으로 바꿀 때는 `FileTimeToSystemTime` → `SystemTimeToTzSpecificLocalTime` → `SystemTimeToFileTime` 순서로 바꿉니다[1].
- FAT 에서 `GetFileTime` 은 캐시한 UTC 를 돌려줍니다[1]. 그래서 일광 절약 시간으로 바뀐 뒤 재부팅하기 전까지 한 시간 어긋납니다[1].
- CD(CDFS) 의 파일 시각은 로컬 시간대에 맞춰 조정해서 보여 줍니다[1].
- 도구 화면의 현지 시각을 옮겨 적었다면 이 차이를 의심합니다. 시각을 한 기준으로 맞추는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에 있습니다.

## 문서 안의 날짜

### OLE 복합 파일로 된 문서 — 요약 정보 속성

옛 오피스 형식처럼 [OLE 복합 파일](../../01-foundations/shell-document-formats/compound-file-binary.md) 로 된 문서는 요약 정보 속성 집합을 씁니다.

- 요약 정보 속성 집합은 스트림 `\005SummaryInformation` 에 저장합니다[2].
- FMTID 는 `F29F85E0-4FF9-1068-AB91-08002B27B3D9` (FMTID_SummaryInformation) 입니다[2].
- 속성 이름은 보통 파일에 저장하지 않습니다[2]. 속성 ID 로 무슨 속성인지 알아냅니다[2].

날짜와 작성자에 관계있는 속성만 골랐습니다. 전체 표는 [문서 메타데이터](../../02-artifacts/embedded-metadata/document-metadata/index.md) 에서 봅니다.

| 이름 | ID 문자열 | ID | 형식 |
|---|---|---|---|
| Author | PIDSI_AUTHOR | 0x04 | VT_LPSTR |
| Last Saved By | PIDSI_LASTAUTHOR | 0x08 | VT_LPSTR |
| Revision Number | PIDSI_REVNUMBER | 0x09 | VT_LPSTR |
| Total Editing Time | PIDSI_EDITTIME | 0x0A | VT_FILETIME (UTC) |
| Last Printed | PIDSI_LASTPRINTED | 0x0B | VT_FILETIME (UTC) |
| Create Time/Date | PIDSI_CREATE_DTM | 0x0C | VT_FILETIME (UTC) |
| Last saved Time/Date | PIDSI_LASTSAVE_DTM | 0x0D | VT_FILETIME (UTC) |
| Name of Creating Application | PIDSI_APPNAME | 0x12 | VT_LPSTR |

(값은 [2] 의 표에서 골랐습니다.)

- Total Editing Time 의 형식은 VT_FILETIME (UTC) 입니다[2]. 이 값을 시각으로 읽을지, 편집한 시간의 길이로 읽을지는 [문서 메타데이터](../../02-artifacts/embedded-metadata/document-metadata/index.md) 에서 봅니다.
- FILETIME 값을 읽는 법은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- BBS 에서 내려받기 같은 일부 파일 전송 방법은 만든 시각·마지막 저장 시각의 "파일 시스템 쪽 값" 을 제대로 유지하지 않습니다[2]. 그래서 문서 안의 시각과 파일 시스템 시각이 어긋나는 것만으로 조작을 뜻하지 않습니다.

### OPC 패키지로 된 문서 — 핵심 속성

새 오피스 형식처럼 OPC (Open Packaging Conventions) 패키지로 된 문서는 핵심 속성 (core properties) 을 씁니다.

- 핵심 속성 이름은 Category, ContentStatus, ContentType, Created, Creator, Description, Identifier, Keywords, Language, LastModifiedBy, LastPrinted, Modified, Revision, Subject, Title, Version 입니다[3].

| 속성 | 뜻 |
|---|---|
| Created | 패키지를 만든 날짜·시각[3] |
| Modified | 마지막으로 바뀐 날짜·시각[3] |
| LastModifiedBy | 내용을 마지막으로 수정한 사용자[3] |
| LastPrinted | 마지막으로 인쇄한 날짜·시각[3] |
| Revision | 개정 번호[3] |
| Creator | 패키지와 내용을 만든 사람·주체[3] |

- 이 속성이 패키지 안 어느 파일에 어떤 시각 형식으로 저장되는지는 [문서 메타데이터](../../02-artifacts/embedded-metadata/document-metadata/index.md) 에서 봅니다.
- 편집 시간, 앱 이름 같은 확장 속성도 같은 페이지에서 봅니다.

### PDF·한글 문서·사진

PDF, 한글 문서, 사진의 날짜 속성은 [문서 메타데이터](../../02-artifacts/embedded-metadata/document-metadata/index.md) 와 [사진 EXIF](../../02-artifacts/embedded-metadata/exif.md) 에서 봅니다.

## 주변 기록으로 맞춰 보기

| 기록 | 맞춰 볼 것 | 링크 |
|---|---|---|
| USN 변경 저널 | 파일을 만들고, 쓰고, 이름을 바꾼 순서 | [USN 변경 저널](../../02-artifacts/filesystem/usnjrnl.md) |
| NTFS 트랜잭션 로그 | 파일 시스템 메타데이터의 변경 기록 | [NTFS 트랜잭션 로그](../../02-artifacts/filesystem/logfile.md) |
| 폴더 인덱스 | 폴더 쪽에 남은 파일 이름과 시각 | [폴더 인덱스와 슬랙](../../02-artifacts/filesystem/i30.md) |
| 바로가기·점프리스트 | 사용자가 문서를 다룰 때 기록한 대상 파일의 시각 | [바로가기 파일](../../02-artifacts/file-folder-usage/lnk.md) · [점프리스트](../../02-artifacts/file-folder-usage/jump-lists.md) |
| 오피스 사용 흔적 | 오피스 앱이 남긴 최근 파일과 자동 복구 파일 | [오피스 사용 흔적](../../02-artifacts/file-folder-usage/microsoft-office/index.md) |
| 윈도 검색 색인 | 색인할 때 적어 둔 예전 속성 값 | [윈도 검색 색인 DB](../../02-artifacts/file-folder-usage/windows-search/index.md) |
| 섀도 복사본 | 지난 시점의 문서와 속성 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 다운로드 출처 표시 | 내려받은 문서인지 | [다운로드 출처 표시](../../02-artifacts/filesystem/zone-identifier.md) · [이 파일은 어디서 왔나](file-origin.md) |

- `$UsnJrnl:$J` 는 앞부분이 빈 희소 스트림입니다. 빈 곳을 0 으로 채워 뽑으면 논리 크기(수 GB)가 됩니다. 빈 곳을 건너뛰면 실제 데이터만 남습니다. 두 방식은 크기와 해시가 다릅니다. 어떻게 뽑았는지 기록합니다.
- 윈도 검색 색인에서 예전 파일 시각을 찾을 때는 열 이름에 주의합니다. Windows 8·10 의 색인 속성 표는 열 이름 앞에 숫자 속성 ID 가 붙습니다. 속성 이름을 정확히 찾는 도구는 이 표에서 0건을 낼 수 있습니다. 자세한 내용은 [윈도 검색 색인 DB](../../02-artifacts/file-folder-usage/windows-search/index.md) 에 있습니다.

## 분석 흐름

1. 문서 원본을 보존하고 사본으로 작업합니다.
2. 문서가 있는 볼륨의 파일 시스템 종류와 PC 의 시간대를 확인합니다.
3. 시스템 시각을 바꾼 흔적이 있는지 먼저 봅니다.
4. $MFT 에서 문서의 레코드를 찾습니다. $STANDARD_INFORMATION 과 $FILE_NAME 의 시각을 확장 레코드까지 함께 뽑습니다.
5. 문서 형식을 확인하고 문서 안의 날짜 속성을 뽑습니다.
6. 두 층의 시각을 UTC 로 맞춥니다. 요약 정보 속성의 FILETIME 은 UTC 입니다[2]. NTFS 시각도 UTC 입니다[1].
7. USN 변경 저널, NTFS 트랜잭션 로그, 폴더 인덱스에서 문서를 만들고 쓰고 이름을 바꾼 순서를 확인합니다.
8. 바로가기·점프리스트·오피스 사용 흔적·검색 색인에 남은 예전 시각과 비교합니다.
9. 섀도 복사본이 있으면 지난 시점의 문서와 속성을 비교합니다.
10. 층끼리 어긋나면 그 이유가 될 만한 것을 모두 적습니다. 복사·전송·내려받기, 다른 PC 에서 작성, 시스템 시각 변경, 시각 조작이 후보입니다. 후보마다 뒷받침하는 기록과 반대하는 기록을 나란히 적습니다.
11. 모든 시각을 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올립니다.

## 흔한 오판

1. **문서 안의 "만든 시각" 을 이 PC 에서 만든 시각으로 봅니다.** 문서 안의 속성은 파일 내용의 일부입니다. 파일을 복사하면 속성도 함께 옮겨 갑니다.
2. **파일 시스템 시각과 문서 안 시각이 다르면 조작이라고 봅니다.** 일부 전송 방법은 파일 시스템 쪽 값을 유지하지 않습니다[2]. 어긋남은 조사할 이유이지 결론이 아닙니다.
3. **파일 시스템 시각을 그대로 믿습니다.** `SetFileTime` 으로 내용을 바꾸지 않고 시각만 바꿀 수 있습니다[1].
4. **FAT 저장 장치의 시각을 UTC 로 읽습니다.** FAT 는 로컬 시각으로 저장합니다[1]. 쓴 시각은 2초 단위입니다[1].
5. **도구 화면의 현지 시각을 그대로 옮깁니다.** 바꾸는 방법에 따라 일광 절약 시간 때문에 한 시간 어긋날 수 있습니다[1].
6. **기본 레코드만 보고 $FILE_NAME 이 짧은 이름뿐이라고 봅니다.** 긴 이름은 확장 레코드에만 있을 수 있습니다.
7. **"마지막 저장한 사람" 속성을 사람으로 씁니다.** 요약 정보의 Last Saved By 는 문자열입니다(VT_LPSTR)[2]. 계정이나 사람과 이으려면 다른 기록이 필요합니다.
8. **마지막 접근 시각을 문서를 연 시각으로 씁니다.** [이 파일을 누가 언제 열었나](file-access.md) 의 "마지막 접근 시각" 절을 봅니다.

## 보고서 문장 예

- 쓰지 않을 문장: "이 문서는 ○○ 에 작성됐습니다."
- 쓸 문장: "문서 `○○.docx` 의 핵심 속성 Created 값은 ○○(UTC)입니다. 이 파일의 $MFT 레코드에 적힌 만든 시각($STANDARD_INFORMATION)은 ○○(UTC)입니다. 두 값은 ○일 차이 납니다. USN 변경 저널에는 ○○(UTC)에 이 이름의 파일을 만든 기록이 있습니다. Microsoft 문서는 일부 파일 전송 방법이 파일 시스템 쪽 시각을 유지하지 않는다고 적었습니다. 그래서 두 값의 차이만으로 시각을 조작했다고 볼 수 없습니다. 이 문서의 내용을 ○○(UTC)에 처음 작성했는지는 이 기록들만으로 정할 수 없습니다."

## 함께 볼 페이지

- [문서 메타데이터](../../02-artifacts/embedded-metadata/document-metadata/index.md) — 형식마다의 날짜 속성과 전체 표입니다.
- [마스터 파일 테이블](../../02-artifacts/filesystem/mft.md) · [USN 변경 저널](../../02-artifacts/filesystem/usnjrnl.md) — 파일 시스템의 시각과 변경 기록입니다.
- [타임라인 작성](../../03-techniques/analysis/timeline/index.md) — 시각을 한 기준으로 맞추고 조작 흔적을 봅니다.
- [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) — FILETIME 을 읽는 법입니다.
- [이 파일은 어디서 왔나](file-origin.md) — 문서가 이 PC 에 들어온 경로입니다.
- [이 파일을 누가 언제 열었나](file-access.md) — 문서를 연 기록입니다.
- [증거를 없애려 했나](anti-forensics/index.md) — 시스템 시각 변경과 기록 지우기입니다.

## 참고 문헌

1. Microsoft Learn, "File Times" (2018-05-31, 갱신 2025-04-15) — https://learn.microsoft.com/en-us/windows/win32/sysinfo/file-times
2. Microsoft Learn, "The Summary Information Property Set" (2018-05-31, 갱신 2025-03-12) — https://learn.microsoft.com/en-us/windows/win32/stg/the-summary-information-property-set
3. Microsoft Learn, "PackageProperties Class (System.IO.Packaging)" — https://learn.microsoft.com/en-us/dotnet/api/system.io.packaging.packageproperties
