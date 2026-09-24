# 이 파일을 누가 언제 열었나 (File Access)

파일 하나를 두고 "어느 계정이 언제 열었나" 를 묻는 조사에서 기록을 모으는 순서를 다룹니다. 아티팩트마다의 구조는 각 아티팩트 페이지에 있습니다. 이 페이지는 어느 기록을 어떤 순서로 보는지, 그 기록으로 어디까지 말할 수 있는지를 정리합니다.

"(관찰)" 을 붙인 내용은 Windows 11 Home 25H2(빌드 26200) PC 한 대에서 직접 본 것입니다(확인 범위: Win11 25H2 한 대). 다른 빌드나 다른 PC 에서는 다를 수 있습니다. "(현장 관찰)" 은 분석 현장에서 겪은 일을 적어 둔 메모에서 가져왔습니다.

## 조사 질문

- 이 파일을 연 기록이 어느 사용자 프로필에 남았습니까?
- 언제 열었습니까? 기록에 적힌 시각이 정말 연 시각입니까?
- 연 것입니까, 저장한 것입니까?
- 이 기록으로 특정 사람이 열었다고 말할 수 있습니까?

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | 기록이 생기는 조건과 이벤트 버전이 Windows 버전마다 다릅니다. [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 버전과 빌드를 먼저 적어 둡니다. |
| 시간대 | 기록마다 UTC 와 현지 시각이 섞여 있습니다. 아래 "시간대 값의 부호" 를 먼저 봅니다. |
| 사용자 | 바로가기 파일·점프리스트·셸백은 사용자 프로필마다 따로 남습니다. [사용자 프로필 목록](../../02-artifacts/system-account/profilelist.md) 으로 SID 와 프로필 폴더를 짝지어 둡니다. |
| 감사 정책 | 파일 접근 이벤트 4663 은 감사를 켜 둔 PC 에서만 남습니다. [감사 정책과 로그 설정](../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 먼저 확인합니다. |
| 마지막 접근 시각 설정 | 갱신이 꺼져 있으면 파일 시스템의 접근 시각을 쓸 수 없습니다. 아래 "마지막 접근 시각" 절을 봅니다. |
| 수집 범위 | 사용자 하이브, 사용자 프로필 폴더, $MFT, 보안 로그를 함께 확보합니다. 지난 시점의 기록은 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 봅니다. |

**시간대 값의 부호.** `SYSTEM\ControlSet00X\Control\TimeZoneInformation\Bias` 는 REG_DWORD 로 저장되고 부호 있는 32비트로 읽습니다(현장 관찰). UTC+9 는 -540 이고, 부호 없이 읽으면 4294966756 이 나옵니다(현장 관찰). 도구가 REG_DWORD 를 부호 없는 10진수로 보여 주는 경우가 많습니다(현장 관찰). 그래서 원시 바이트로 한 번 더 확인합니다. 다른 시간대 값은 [시간대 설정](../../02-artifacts/system-account/time-zone.md) 에서 다룹니다.

**감사 정책.** 이 PC 에서는 파일 시스템 감사가 꺼져 있었습니다(관찰). 그래서 4663 이 없다는 사실만으로 열람이 없었다고 볼 수 없으며, 감사가 켜져 있었는지부터 확인합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 최근 항목 바로가기 파일 | 대상 경로, 바로가기를 쓸 때의 대상 시각·크기, 볼륨·기계 정보 | [바로가기 파일](../../02-artifacts/file-folder-usage/lnk.md) |
| 2 | 점프리스트 | 앱마다 최근에 다룬 파일, 마지막 갱신 시각 | [점프리스트](../../02-artifacts/file-folder-usage/jump-lists.md) |
| 3 | 최근 문서·열기·저장 대화상자 기록 | 사용자 하이브에 남은 파일·폴더 목록 | [최근 문서](../../02-artifacts/file-folder-usage/recentdocs.md) · [열기·저장 대화상자 기록](../../02-artifacts/file-folder-usage/comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) |
| 4 | 오피스 사용 흔적 | 오피스 앱에서 다룬 파일 | [오피스 사용 흔적](../../02-artifacts/file-folder-usage/microsoft-office/index.md) |
| 5 | 셸백 | 탐색기로 들어가 본 폴더 | [셸백](../../02-artifacts/file-folder-usage/shellbags/index.md) |
| 6 | $MFT 의 마지막 접근 시각 | 갱신이 켜져 있을 때만, 파일에 접근한 시각의 단서 | [마스터 파일 테이블](../../02-artifacts/filesystem/mft.md) |
| 7 | 보안 로그 4663 | 감사를 켜 둔 PC 에서만, 접근한 계정·프로세스·권한 | [파일 접근 감사](../../02-artifacts/event-logs/4656-4663-4660.md) |
| 8 | 윈도 타임라인·썸네일 캐시·윈도 검색 색인 | 보조 단서 | [윈도 타임라인](../../02-artifacts/file-folder-usage/activitiescache-db.md) · [썸네일 캐시](../../02-artifacts/file-folder-usage/thumbcache-db-thumbs-db.md) · [윈도 검색 색인 DB](../../02-artifacts/file-folder-usage/windows-search/index.md) |
| 9 | 공유 폴더 접근 5140·5145 | 파일이 공유 폴더에 있을 때 | [공유 폴더 접근](../../02-artifacts/event-logs/5140-5145.md) |

사용자 프로필에 남은 기록(1\~5)을 먼저 봅니다. 파일 시스템과 이벤트 로그(6\~7)는 설정에 따라 아예 없을 수 있습니다.

## 사용자 프로필의 기록

### 바로가기 파일과 점프리스트

최근 항목 바로가기 파일 (LNK) 은 앱이 `SHAddToRecentDocs` 함수를 부를 때 생깁니다. 탐색기에서 항목을 열 때와 공용 파일 대화상자로 열기·저장·새로 만들기를 할 때는 셸이 이 함수를 대신 부릅니다. 자기 화면으로 파일을 고르는 앱이 이 함수를 부르지 않으면 최근 항목에 오르지 않습니다. 실행 파일(.exe)은 XP 이후 최근 항목에서 걸러지며, 프로그램 실행은 [어떤 프로그램을 언제 실행했나](program-execution.md) 에서 다룹니다.

점프리스트 (Jump List) 는 앱(AppID)마다 파일 하나로 남고, 그 파일 안에 항목마다 바로가기 데이터와 마지막 갱신 시각이 있습니다. 공용 대화상자로 열기·저장·새로 만들기를 하면 같은 함수가 불리므로 바로가기 파일과 점프리스트로는 연 것과 저장한 것을 가릴 수 없습니다.

"문서를 열면 그 파일의 바로가기와 부모 폴더의 바로가기가 함께 생긴다" 는 설명이 널리 퍼져 있지만, 이 동작은 Microsoft 문서에 적혀 있지 않으므로 이 설명에 기대어 판단하지 않습니다.

구조와 시각 해석은 [바로가기 파일](../../02-artifacts/file-folder-usage/lnk.md) 과 [점프리스트](../../02-artifacts/file-folder-usage/jump-lists.md) 에 있습니다. 바이트 단위 형식은 [바로가기 형식](../../01-foundations/shell-document-formats/shell-link-lnk.md) 에 있습니다.

### 폴더와 목록 기록

셸백 (ShellBags) 은 탐색기로 들어가 본 폴더 경로를 남기는데, 파일 단위가 아니라 폴더 단위라서 그 폴더에 들어간 흔적으로만 씁니다.

최근 문서, 열기·저장 대화상자 기록, 오피스의 최근 파일 목록에도 사용자가 다룬 파일이 남습니다. 이 페이지에서는 세부를 다루지 않으며, 위치와 해석은 표의 링크 페이지에서 확인합니다. 탐색기 주소창과 검색창에 입력한 내용은 [탐색기 입력 기록](../../02-artifacts/file-folder-usage/typedpaths-wordwheelquery.md) 에서 봅니다.

## 마지막 접근 시각

파일 시스템의 마지막 접근 시각 (Last Access Time) 은 설정에 따라 갱신되지 않을 수 있습니다. 먼저 설정부터 봅니다.

`fsutil behavior set disablelastaccess {1|0}` 은 NTFS 에서 마지막 접근 시각 갱신을 끄거나 켭니다[1]. 이 명령은 `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\NtfsDisableLastAccessUpdate` 값을 바꾸며, 바꾼 뒤에는 재시작해야 적용됩니다[1]. 백업 같은 프로그램이 이 기능에 기대기도 한다고 문서에 적혀 있습니다[1].

NTFS 는 디스크의 마지막 접근 시각 갱신을 최대 1시간까지 미룰 수 있고, 미뤄 둔 접근 시각은 마지막 수정 시각 같은 다른 속성을 갱신할 때 함께 씁니다[1]. 실행 중인 시스템에서 조회하면 디스크 값이 최신이 아니어도 메모리에 있는 정확한 값을 돌려줍니다[1]. 그래서 라이브로 본 값과 이미지에서 읽은 값이 다를 수 있습니다.

**이 PC 의 설정.** `NtfsDisableLastAccessUpdate` 값은 0x80000001 이었습니다(관찰). `fsutil behavior query disablelastaccess` 는 "DisableLastAccess = 1 (User Managed, Last Access Time Updates DISABLED)" 로 보여 주었습니다(관찰). 이 PC 의 C: 에서는 마지막 접근 시각이 갱신되지 않습니다(관찰).

참고한 문서는 0 과 1 두 값만 설명하고[1], 0x80000000 대의 값이 무엇을 뜻하는지는 문서로 확인하지 못했습니다. 검체에서는 값을 그대로 적고, 뜻은 fsutil 출력이나 다른 자료로 따로 확인합니다.

시각 속성마다 무엇이 바뀔 때 바뀌는지는 [NTFS 구조](../../01-foundations/disk-volume/ntfs/index.md) 와 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 보안 로그 4663

4663 "An attempt was made to access an object." 은 파일에 실제로 접근한 계정과 프로세스를 적습니다. 다만 남는 조건이 까다롭습니다.

4663 은 Audit File System·Audit Kernel Object·Audit Registry·Audit Removable Storage 하위 범주의 이벤트이고, 개체의 SACL 에 해당 접근을 기록하라는 ACE 가 있을 때만 생깁니다[2]. 핸들 요청을 적는 4656 과 달리 4663 은 권한을 실제로 썼다는 기록이며, 실패 이벤트는 없습니다[2].

공급자는 Microsoft-Windows-Security-Auditing 이고 채널은 Security 입니다[2]. 최소 OS 는 Vista·Server 2008 이며[2], 버전 1 은 Windows 8·Server 2012 에서 Resource Attributes 칸이 붙은 판입니다[2].

**조사에 쓰는 칸.**

| 묻는 것 | 칸 |
|---|---|
| 누가 | SubjectUserSid, SubjectUserName, SubjectDomainName, SubjectLogonId |
| 무엇을 | ObjectType, ObjectName |
| 어떤 권한으로 | AccessList, AccessMask |
| 어느 프로세스로 | ProcessId, ProcessName, HandleId |

**파일 열람과 관계있는 접근 권한 값.**

| AccessMask | 이름 | AccessList 표시 |
|---|---|---|
| 0x1 | ReadData (폴더는 ListDirectory) | %%4416 |
| 0x2 | WriteData (폴더는 AddFile) | %%4417 |
| 0x4 | AppendData | %%4418 |
| 0x8 | ReadEA | %%4419 |
| 0x20 | Execute·Traverse | %%4421 |
| 0x80 | ReadAttributes | %%4423 |
| 0x100 | WriteAttributes | %%4424 |

(값은 [2] 의 표에서 골랐습니다. 삭제 권한은 [지운 파일의 흔적 찾기](deleted-file-traces.md) 에서, 나머지 값은 [파일 접근 감사](../../02-artifacts/event-logs/4656-4663-4660.md) 에서 봅니다.)

**다른 이벤트와 잇기.**

- ProcessId 는 4688 의 New Process ID 와 이어 볼 수 있습니다[2].
- HandleId 는 4656 의 Handle ID 와 이어 볼 수 있습니다[2]. 핸들이 잡히지 않았으면 0x0 으로 나옵니다[2].
- SubjectLogonId 는 4624 의 Logon ID 와 이어 볼 수 있습니다[2]. 로그온 이벤트는 [로그온·로그오프](../../02-artifacts/event-logs/logon-events/index.md) 에서 다룹니다.

**Sysmon 에는 읽기 이벤트가 없습니다.**

Sysmon 이벤트 목록에는 파일 읽기를 기록하는 이벤트가 없습니다[3]. 파일과 관계있는 이벤트는 2(생성 시각 변경), 11 FileCreate(생성·덮어쓰기), 15(이름 있는 스트림 생성), 23·26(삭제), 27·28(실행 파일 생성 차단·완전삭제 차단), 29(실행 파일 생성 탐지), 9 RawAccessRead 이고, 9 RawAccessRead 는 `\\.\` 형식으로 드라이브를 직접 읽을 때 남습니다[3].

그래서 Sysmon 이 설치돼 있어도 파일을 연 기록은 직접 남지 않습니다. Sysmon 전반은 [Sysmon 로그](../../02-artifacts/event-logs/sysmon/index.md) 에서 봅니다.

## 그 밖의 흔적

**윈도 타임라인.** 이 PC 에는 `%LOCALAPPDATA%\ConnectedDevicesPlatform\<폴더>\ActivitiesCache.db` 가 두 개 있었습니다(관찰). 그 가운데 하나는 조사 당일에도 쓰였습니다(관찰).

사본의 표는 Activity, ActivityOperation, AppSettings, Metadata, ManualSequence, Activity_PackageId, DataEncryptionKeys, Asset 이었고(관찰), Activity 표는 711행, ActivityOperation 표는 0행이었습니다(관찰). ActivityType 값은 11·12·15 세 가지뿐이었으며(관찰) 각 값이 무엇을 뜻하는지는 확인하지 못했습니다.

그래서 Windows 11 에서는 이 DB 를 파일 열람 기록으로 기대하기 어렵습니다. 단정하지 말고 검체마다 표 내용을 확인합니다.

**그 밖의 보조 기록.**

- 사진·문서의 미리 보기 그림은 [썸네일 캐시](../../02-artifacts/file-folder-usage/thumbcache-db-thumbs-db.md) 에 남을 수 있습니다.
- 색인된 파일의 정보는 [윈도 검색 색인 DB](../../02-artifacts/file-folder-usage/windows-search/index.md) 에 남을 수 있습니다.
- 파일이 공유 폴더에 있으면 파일 서버의 [공유 폴더 접근](../../02-artifacts/event-logs/5140-5145.md) 이벤트를 봅니다.
- 파일이 USB 저장장치에 있었으면 [USB 저장장치 흔적](../../02-artifacts/external-devices/usb-storage-artifacts/index.md) 으로 연결 시각을 먼저 정합니다.

## 분석 흐름

1. Windows 버전·시간대·사용자 SID 를 정리합니다. 시간대 Bias 는 부호 있는 값으로 읽습니다.
2. 대상 파일의 경로와 이름을 정하고 $MFT 에서 레코드를 찾습니다. 이름으로 찾을 때 주의할 점은 [지운 파일의 흔적 찾기](deleted-file-traces.md) 의 "MFT 레코드" 절에 있습니다.
3. 사용자마다 최근 항목 바로가기 파일과 점프리스트에서 대상 경로가 든 항목을 찾습니다.
4. 바로가기 파일에 적힌 대상 시각·크기를 $MFT 의 시각·크기와 비교합니다. 값이 다르면 바로가기를 쓴 뒤에 파일이 바뀌었거나, 이름만 같은 다른 파일일 수 있습니다.
5. 최근 문서, 열기·저장 대화상자 기록, 오피스 사용 흔적에서 같은 경로를 찾습니다.
6. 셸백에서 대상 파일이 있는 폴더에 들어간 흔적을 찾습니다.
7. 마지막 접근 시각 설정을 확인합니다. 갱신이 켜져 있을 때만 접근 시각을 참고 자료로 씁니다.
8. 파일 시스템 감사가 켜져 있었다면 4663 을 ObjectName 으로 찾습니다. SubjectLogonId 로 로그온 세션을 잇고, ProcessId 로 프로세스를 잇습니다.
9. 섀도 복사본이 있으면 지난 시점의 바로가기 파일·점프리스트와 비교합니다.
10. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올립니다. 시각 값의 형식은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 확인합니다.
11. 그 시각에 누가 PC 앞에 있었는지는 [그 시각에 PC 를 쓴 사람이 누구인가](user-attribution.md) 를 따라 따로 좁힙니다.

## 흔한 오판

1. **점프리스트나 최근 항목 바로가기를 "열었다" 는 증거로 씁니다.** 두 기록은 연 것과 저장한 것을 가리지 못합니다. "열었거나 저장했다" 까지만 씁니다.
2. **바로가기 헤더의 시각을 연 시각으로 씁니다.** 헤더 시각은 대상 파일의 시각입니다. 바로가기 파일 자신의 시각과 다릅니다. 자세한 내용은 [바로가기 파일](../../02-artifacts/file-folder-usage/lnk.md) 에 있습니다.
3. **마지막 접근 시각을 연 시각으로 씁니다.** 갱신이 꺼져 있을 수 있습니다(관찰). 켜져 있어도 디스크에는 최대 1시간 늦게 쓰일 수 있습니다[1].
4. **4663 이 없으니 열지 않았다고 봅니다.** 감사가 꺼져 있었을 수 있습니다(관찰). 감사가 켜져 있어도 SACL 이 없는 파일은 남지 않습니다[2].
5. **Sysmon 에서 열람 기록을 찾습니다.** Sysmon 에는 파일 읽기 이벤트가 없습니다[3].
6. **바로가기 파일이 없으니 열지 않았다고 봅니다.** `SHAddToRecentDocs` 를 부르지 않는 앱으로 열면 최근 항목에 오르지 않습니다.
7. **계정을 사람으로 씁니다.** 기록은 어느 계정의 세션에서 일어났는지를 보여 줍니다. 그 계정을 누가 썼는지는 다른 기록으로 좁힙니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 ○○ 에 계약서.docx 를 열어 보았습니다."
- 쓸 문장: "사용자 ○○ 프로필의 점프리스트(앱 ○○)에 `○○\계약서.docx` 항목이 있습니다. 이 항목은 ○○(UTC) 에 마지막으로 갱신됐습니다. 이 기록은 이 계정의 세션에서 해당 앱이 이 파일을 열었거나 저장했음을 보여 주지만, 연 것인지 저장한 것인지는 이 기록만으로 정할 수 없습니다. 이 PC 는 마지막 접근 시각 갱신과 파일 시스템 감사가 모두 꺼져 있었습니다. 그래서 파일 시스템과 보안 로그로는 접근 시각을 확인할 수 없었습니다."

## 함께 볼 페이지

- [바로가기 파일](../../02-artifacts/file-folder-usage/lnk.md) · [점프리스트](../../02-artifacts/file-folder-usage/jump-lists.md) — 파일을 다룬 기록의 구조와 시각입니다.
- [셸백](../../02-artifacts/file-folder-usage/shellbags/index.md) — 탐색기로 들어간 폴더입니다.
- [파일 접근 감사](../../02-artifacts/event-logs/4656-4663-4660.md) · [감사 정책과 로그 설정](../../02-artifacts/event-logs/audit-policy-log-settings.md) — 4663 이 남는 조건과 전체 칸입니다.
- [마스터 파일 테이블](../../02-artifacts/filesystem/mft.md) — 파일 시스템의 시각입니다.
- [어떤 프로그램을 언제 실행했나](program-execution.md) — 실행 파일을 연 기록은 여기서 다룹니다.
- [이 파일은 어디서 왔나](file-origin.md) — 파일이 이 PC 에 들어온 경로입니다.
- [지운 파일의 흔적 찾기](deleted-file-traces.md) — 대상 파일이 지금 없을 때 봅니다.
- [그 시각에 PC 를 쓴 사람이 누구인가](user-attribution.md) — 계정에서 사람으로 좁힙니다.
- [자료를 밖으로 빼돌렸나](../exfiltration/data-exfiltration/index.md) — 연 파일을 밖으로 옮겼는지 봅니다.

## 참고 문헌

1. Microsoft Learn, "fsutil behavior" — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-behavior
2. Microsoft Learn, "4663(S) An attempt was made to access an object." (Windows 10 보관 문서) — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4663
3. Microsoft Learn, "Sysmon - Sysinternals" (2026-09-10 판) — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
