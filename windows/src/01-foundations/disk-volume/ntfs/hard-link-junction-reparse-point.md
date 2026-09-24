# 링크와 리파스 포인트 (Hard Link·Junction·Reparse Point)

상위: [NTFS 구조 (NTFS)](index.md)

## 한 줄 요약

NTFS 에서 파일 하나를 여러 경로로 보이게 하는 방법은 두 가지입니다. 하드 링크 (Hard Link)는 MFT 레코드 하나에 이름을 여러 개 붙이고, 정션 (Junction)과 심볼릭 링크 (Symbolic Link)는 리파스 포인트 (Reparse Point)라는 속성에 가리킬 경로를 적어 둡니다. 리파스 포인트는 클라우드 자리표시 파일과 시스템 파일 압축에도 쓰입니다.

## 이 형식을 쓰는 아티팩트

| 만나는 곳 | 쓰는 방식 | 분석할 때 생기는 일 |
|---|---|---|
| `C:\Windows\WinSxS` 와 `System32` 등 | 하드 링크 | 파일 하나가 여러 경로에 보입니다. 폴더 크기를 더하면 실제보다 커집니다. |
| `C:\Documents and Settings`, 프로필 안의 `My Documents` 등 | 정션 | 따라가면 같은 자료를 두 번 담거나 같은 폴더를 계속 돕니다. |
| 클라우드 동기화 폴더 | 클라우드 태그 | 파일은 보이지만 내용이 디스크에 없을 수 있습니다. |
| 시스템 파일 압축 (WOF) | WOF 태그 | 이름 없는 `$DATA` 는 희소 스트림이고, 압축된 내용은 `WofCompressedData` 스트림에 있습니다. |
| 스토어 앱 실행 별칭 | APPEXECLINK 태그 | 크기 0바이트 `.exe` 로 보입니다. |

관찰 사례입니다(확인 범위: Windows 11 25H2, 빌드 26200). `System32\notepad.exe` 는 MFT 레코드 하나에 `\Windows`, `\Windows\System32`, `\Windows\WinSxS\…` 세 경로가 붙어 있었습니다. `%LOCALAPPDATA%\Microsoft\WindowsApps` 의 실행 별칭은 0바이트였고 태그는 0x8000001B 였습니다.

## 구조

### 세 가지 링크 비교

| 구분 | 하드 링크 | 정션 | 심볼릭 링크 |
|---|---|---|---|
| 저장 위치 | 같은 레코드의 `$FILE_NAME` 여러 개 | `$REPARSE_POINT`, 태그 0xA0000003 | `$REPARSE_POINT`, 태그 0xA000000C |
| 가리키는 것 | 파일만 | 폴더만 | 파일과 폴더 |
| 가리킬 수 있는 곳 | 같은 볼륨 | 같은 PC 의 로컬 볼륨 | 로컬 볼륨과 원격 UNC. 상대 경로는 한 볼륨 안 |
| 링크를 지우면 | 그 이름만 없어집니다. 마지막 이름이면 파일이 지워집니다. | 정션만 없어집니다. | 링크만 없어집니다. |
| 만드는 명령 예 | `mklink /H` | `mklink /J` | `mklink`, `mklink /D` |

심볼릭 링크를 만들려면 "심볼릭 링크 만들기" 사용자 권한 (SeCreateSymbolicLinkPrivilege)이 필요합니다. 이 권한은 기본으로 Administrators 그룹에만 있지만 개발자 모드가 켜진 PC 에서는 관리자 권한 없이도 만들 수 있습니다. 정션에는 이 권한 검사가 없습니다. 하드 링크는 CreateHardLink 로 파일 하나에 1,023개까지 만들 수 있습니다.

| 항목 | 해당 Windows |
|---|---|
| 리파스 포인트, `$Extend\$Reparse` | NTFS 3.0(Windows 2000)부터 |
| 심볼릭 링크 | Windows Vista·Server 2008 부터 |
| 호환용 정션 (`Documents and Settings` 등) | Windows Vista·Server 2008 부터 |
| FILE_PLACEHOLDER 태그 (0x80000015) | Windows 8.1 의 옛 자리표시 파일. 지금은 쓰지 않습니다. |

### 하드 링크가 기록되는 곳

| 위치 | 오프셋 | 크기 | 내용 |
|---|---|---|---|
| MFT 레코드 머리 | 0x12 | 2 | 링크 수 (Link Count) |
| `$FILE_NAME` 내용 | 0x00 | 8 | 부모 폴더의 MFT 참조 |
| `$FILE_NAME` 내용 | 0x38 | 4 | 파일 속성 플래그. 0x400 이면 리파스 포인트 |
| `$FILE_NAME` 내용 | 0x3C | 4 | 리파스 포인트면 리파스 태그, 아니면 확장 속성 크기 |
| `$FILE_NAME` 내용 | 0x41 | 1 | 이름 공간 (Namespace): 0 POSIX, 1 Win32, 2 DOS, 3 Win32+DOS |

`$FILE_NAME` 전체 구조는 [MFT 레코드와 속성 (FILE Record·Attribute)](file-record-attribute.md)을 봅니다.

이름마다 `$FILE_NAME` 이 하나씩 있고 각 이름에는 자기 부모 폴더 참조가 따로 있으며, 부모 폴더의 `$I30` 색인에도 이름마다 항목이 하나씩 있습니다. `$STANDARD_INFORMATION`, 보안 설명자, `$DATA` 는 레코드에 하나뿐이라 모든 이름이 함께 씁니다. 짧은 이름(8.3)이 따로 있는 파일도 `$FILE_NAME` 이 둘인데, 경로가 둘이라는 뜻은 아닙니다.

### 리파스 포인트

`$REPARSE_POINT` 는 속성 형식 0xC0 이고, 이 속성이 있는 파일은 속성 플래그 0x400 (FILE_ATTRIBUTE_REPARSE_POINT)이 켜집니다.

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x00 | 4 | ReparseTag | 처리할 주인을 나타내는 태그 |
| 0x04 | 2 | ReparseDataLength | 0x08 뒤 데이터 길이 (바이트) |
| 0x06 | 2 | Reserved | 0 |
| 0x08 | 가변 | 데이터 | 태그마다 모양이 다릅니다. |

마이크로소프트 태그가 아니면 0x08 에 16바이트 GUID 가 먼저 오는데, 이때 데이터 길이에 GUID 는 들어가지 않습니다.

리파스 태그 (Reparse Tag)의 위 네 비트는 뜻이 정해져 있고 아래 16비트는 태그 번호입니다.

| 비트 | 마스크 | 뜻 |
|---|---|---|
| 31 (M) | 0x80000000 | 마이크로소프트 태그 |
| 30 (R) | 0x40000000 | 예약 |
| 29 (N) | 0x20000000 | 이름 대리 (Name Surrogate). 시스템의 다른 이름을 대신합니다. |
| 28 (D) | 0x10000000 | 이 태그가 붙은 폴더는 자식을 가질 수 있습니다. |

자주 만나는 태그입니다(MS-FSCC 기준).

| 태그 | 이름 | 쓰임 |
|---|---|---|
| 0xA0000003 | MOUNT_POINT | 정션, 마운트 폴더 |
| 0xA000000C | SYMLINK | 심볼릭 링크 |
| 0x80000017 | WOF | WIMBoot 또는 단일 파일 압축 |
| 0x9000001A, 0x9000101A\~0x9000F01A | CLOUD, CLOUD_1\~CLOUD_F | 클라우드 동기화 엔진이 관리하는 파일 |
| 0x8000001B | APPEXECLINK | 스토어(UWP) 앱 실행 별칭 |
| 0xA000001D | LX_SYMLINK | WSL 의 유닉스 심볼릭 링크 |

### 정션·심볼릭 링크 데이터

오프셋은 `$REPARSE_POINT` 내용 시작에서 잰 값입니다.

| 오프셋 | 크기 | 정션 (0xA0000003) | 심볼릭 링크 (0xA000000C) |
|---|---|---|---|
| 0x08 | 2 | 대체 이름 오프셋 | 같음 |
| 0x0A | 2 | 대체 이름 길이 (바이트) | 같음 |
| 0x0C | 2 | 표시 이름 오프셋 | 같음 |
| 0x0E | 2 | 표시 이름 길이 (바이트) | 같음 |
| 0x10 | 4 | 이름 버퍼 시작 | 플래그: 0 절대 경로, 1 상대 경로 |
| 0x14 | 가변 | (이름 버퍼 계속) | 이름 버퍼 시작 |

이름 오프셋은 이름 버퍼 시작에서 잰 값이고 두 이름의 순서는 정해져 있지 않으며, 이름 길이에는 끝의 널 문자가 들어가지 않습니다. 대체 이름 (Substitute Name)은 시스템이 실제로 따라가는 경로이고 절대 경로면 보통 `\??\C:\…` 꼴입니다. 표시 이름 (Print Name)은 사람에게 보여 주려고 적은 경로입니다.

마운트 폴더 (Mounted Folder)도 정션과 같은 태그를 쓰며, 대체 이름이 `\??\Volume{GUID}\` 꼴이면 볼륨을 폴더에 붙인 것입니다. 볼륨 GUID 의 짝은 [드라이브 문자 매핑 (MountedDevices)](../../../02-artifacts/external-devices/usb-storage-artifacts/mounteddevices.md)에서 찾습니다.

`$Extend\$Reparse` 파일은 볼륨의 리파스 포인트를 `$R` 색인에 모아 둡니다. 색인 키는 리파스 태그(4바이트)와 MFT 참조(8바이트)이고 데이터는 없으며, 이 색인만 읽어도 링크·자리표시 파일이 있는 MFT 레코드 목록을 얻습니다. `$Extend` 의 다른 파일은 [NTFS 메타 파일 ($Bitmap·$Secure·$Extend)](bitmap-secure-extend.md)을 봅니다.

## 읽는 법

### 헥스로 정션 따라가기

`D:\Work` 를 가리키는 정션의 `$REPARSE_POINT` 내용을 MS-FSCC 명세대로 만든 예시입니다. 실제 검체에서 나온 값이 아닙니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    03 00 00 A0 30 00 00 00 00 00 16 00 18 00 0E 00
0x10    5C 00 3F 00 3F 00 5C 00 44 00 3A 00 5C 00 57 00   \??\D:\W
0x20    6F 00 72 00 6B 00 00 00 44 00 3A 00 5C 00 57 00   ork.D:\W
0x30    6F 00 72 00 6B 00 00 00                           ork.
```

1. 0x00 의 `03 00 00 A0` 는 리틀 엔디언으로 0xA0000003, 곧 정션 태그입니다.
2. 0x04 의 `30 00` 은 데이터 길이 48바이트입니다. 전체는 0x08 + 0x30 = 0x38 바이트입니다.
3. 0x08 부터 네 값은 대체 이름 오프셋 0, 길이 22바이트(11글자), 표시 이름 오프셋 0x18, 길이 14바이트(7글자)입니다.
4. 이름 버퍼는 0x10 에서 시작합니다. 대체 이름은 0x10 부터 22바이트인 `\??\D:\Work` 입니다.
5. 표시 이름은 0x10 + 0x18 = 0x28 부터 14바이트인 `D:\Work` 입니다.

심볼릭 링크라면 0x10 의 플래그를 먼저 읽고 이름 버퍼는 0x14 부터 셉니다. 플래그가 1 이면 대체 이름을 링크가 있는 폴더 기준으로 풉니다.

### 하드 링크 경로 모으기

1. MFT 레코드 머리 0x12 의 링크 수를 봅니다. 1보다 크면 이름이 여럿일 수 있습니다.
2. `$FILE_NAME` 을 모두 모읍니다. `$ATTRIBUTE_LIST` 가 있으면 확장 레코드의 `$FILE_NAME` 까지 모읍니다.
3. 이름 공간이 2(DOS)인 이름은 같은 경로의 짧은 이름이므로 따로 둡니다.
4. 남은 이름마다 부모 참조를 따라 루트까지 올라가 전체 경로를 만듭니다.

2번을 빠뜨린 관찰 사례가 있습니다. 확장 레코드를 쓰는 파일은 Win32 긴 이름이 확장 레코드에만 있을 수 있는데, 이때 기본 레코드만 보면 8.3 짧은 이름만 보이고 확장 레코드는 대개 기본 레코드와 멀리 떨어져 있습니다.

## 포렌식에서 중요한 점

**지운 링크의 흔적**

- 하드 링크 이름 하나를 지우면 그 `$FILE_NAME` 과 부모 폴더의 `$I30` 항목만 빠지고 데이터는 마지막 이름이 지워질 때까지 남습니다.
- 그래서 지운 기록이 있어도 같은 MFT 번호의 다른 경로로 내용이 남아 있을 수 있습니다.
- 빠진 이름은 부모 폴더 `$I30` 의 빈 공간에 남을 수 있습니다([폴더 인덱스와 슬랙 ($I30)](../../../02-artifacts/filesystem/i30.md)). `$I30` 항목의 `$FILE_NAME` 사본에는 리파스 태그도 들어가므로, 지운 정션·심볼릭 링크도 가늠할 수 있습니다.
- 변경 저널에는 하드 링크가 생기거나 지워질 때 USN_REASON_HARD_LINK_CHANGE (0x00010000)가 남습니다. 리파스 포인트를 붙이거나 바꾸거나 떼면 USN_REASON_REPARSE_POINT_CHANGE (0x00100000)가 남습니다([USN 변경 저널 ($UsnJrnl)](../../../02-artifacts/filesystem/usnjrnl.md)).

**시각**

- `$STANDARD_INFORMATION` 은 레코드에 하나라서 어느 경로로 고쳐도 같은 네 시각이 바뀌지만, `$FILE_NAME` 시각은 이름마다 따로 있어서 경로마다 다를 수 있습니다([두 벌의 시각](standard-information-file-name.md)).
- 폴더 목록(`$I30`)의 크기·속성 사본은 변경이 일어난 경로의 항목만 바로 바뀝니다. 다른 경로의 목록 값은 옛 값일 수 있습니다.
- 정션·심볼릭 링크에는 자기 MFT 레코드가 따로 있으며, 그 시각은 링크 자체의 기록이고 대상의 시각이 아닙니다.
- 모든 시각은 UTC 기준 FILETIME 입니다([시각 값 형식](../../value-decoding/filetime-unix-webkit-dos-ole.md)).
- 프로필 안의 호환용 정션은 보통 프로필이 만들어질 때 함께 생깁니다. 그래서 그 생성 시각으로 프로필 생성 시점을 어림할 수 있지만, 추정값으로만 씁니다([사용자 프로필 목록 (ProfileList)](../../../02-artifacts/system-account/profilelist.md)).

**악용될 때 남는 모습**

- 눈에 안 띄는 폴더에 하드 링크로 두 번째 이름을 붙이면 보이는 경로를 지워도 데이터가 남습니다. 사용자 파일인데 링크 수가 2 이상이면 모든 경로를 뽑아 봅니다.
- 심볼릭 링크 대상에 `HarddiskVolumeShadowCopy` 장치 이름이 있으면 섀도 복사본 안을 폴더처럼 연 흔적일 수 있습니다. 이 방법은 잠긴 파일을 복사할 때도 씁니다([자격 증명을 빼냈나 (Credential Dumping)](../../../04-scenarios/incident/credential-theft-lateral-movement/credential-dumping.md), [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)).
- Microsoft 는 심볼릭 링크 공격으로 파일 권한을 바꾸거나 데이터를 망가뜨릴 수 있다고 경고합니다. 사용자가 쓸 수 있는 폴더에 시스템 폴더를 가리키는 링크가 있으면, 만든 시각 전후의 실행 기록을 함께 봅니다.

## 함정

1. **분석 PC 로 빠지는 경로.** 이미지를 드라이브 문자로 붙이고 링크를 따라가면 대체 이름의 `\??\C:\` 는 분석 PC 의 C: 로 풀립니다. 링크는 따라가지 말고 대체 이름 문자열로 기록합니다.
2. **중복과 순환.** 논리 복사·수집 도구가 정션을 따라가면 같은 자료를 두 번 담거나 순환에 빠집니다. Microsoft 도 백업 프로그램이 호환용 정션을 따라가지 말라고 안내합니다([선별 수집](../../../03-techniques/process-acquisition/evidence-acquisition/triage-collection.md)).
3. **액세스 거부는 숨김이 아님.** 호환용 정션에는 숨김·시스템 속성과 Everyone 읽기 거부 ACL 이 걸려 있습니다. 목록 열기가 실패하는 것은 정상입니다.
4. **같은 해시 여러 개.** 하드 링크된 파일은 해시가 같은 파일 여러 개로 나옵니다. MFT 번호가 같으면 사본이 아니라 한 파일입니다([해시셋 대조와 유사 해시](../../../03-techniques/analysis/hash-set-fuzzy-hash.md)).
5. **내용이 빈 파일.** WOF·클라우드 태그 파일에서 이름 없는 `$DATA` 만 읽으면 비어 있거나 0 으로 보입니다. WOF 는 `WofCompressedData` 스트림을 풀어야 합니다([압축·희소 파일](compressed-sparse.md), [ADS](ads.md)). 클라우드 자리표시 파일은 내용이 디스크에 없을 수 있습니다([클라우드 동기화 공통 구조](../../../02-artifacts/cloud-notes/cloud-files-api-syncrootmanager.md)).
6. **이름 순서와 널 문자.** 관찰 사례입니다(확인 범위: Windows 11 25H2, 빌드 26200). `C:\Users\All Users` 심볼릭 링크는 표시 이름 `C:\ProgramData` 가 앞에, 대체 이름 `\??\C:\ProgramData` 가 뒤에 있었고 널 문자가 없었습니다. 같은 PC 의 `C:\Documents and Settings` 정션은 대체 이름이 앞이었고 이름마다 널 문자가 붙어 있었습니다. 항상 오프셋과 길이로 읽습니다.
7. **태그 값이 문서마다 다름.** 문서나 도구에 따라 태그 이름과 값이 다르게 적힌 곳이 있습니다. 태그 값은 MS-FSCC 표로 확인합니다.

## 도구

- Windows 기본 명령: `fsutil reparsepoint query` 는 태그와 리파스 데이터를 헥스로 보여 줍니다. `fsutil hardlink list` 는 같은 파일의 모든 경로를 보여 줍니다. `dir /AL` 은 링크만 골라 `<JUNCTION>`·`<SYMLINKD>` 처럼 표시합니다. 붙인 이미지에서 쓸 때는 함정 1 을 기억합니다.
- libyal libfsntfs 의 `fsntfsinfo` 는 MFT 항목의 `$FILE_NAME` 과 리파스 포인트(태그, 대체 이름)를 풀어 보여 줍니다.
- The Sleuth Kit 의 `istat` 은 MFT 항목의 속성 목록을 보여 줍니다. MFT 파서 결과에 링크 수·리파스 대상이 없으면 이 페이지의 오프셋으로 헥스를 직접 봅니다([마스터 파일 테이블 ($MFT)](../../../02-artifacts/filesystem/mft.md)).

## 참고 문헌

1. Microsoft Learn, "Hard Links and Junctions" — https://learn.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions · "Junction Points" — https://learn.microsoft.com/en-us/windows/win32/vss/junction-points
2. Microsoft Learn, CreateHardLinkW — https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createhardlinkw · CreateSymbolicLinkW — https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createsymboliclinkw · "Create symbolic links" — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/create-symbolic-links
3. Microsoft Learn, "Determine the Actual Size of the WinSxS Folder" — https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/determine-the-actual-size-of-the-winsxs-folder
4. [MS-FSCC] Reparse Tags — https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/c8e77b37-3909-4fe6-a4ea-2b9d423b1ee4 · REPARSE_GUID_DATA_BUFFER — https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/a4d08374-0e92-43e2-8f88-88b94112f070 · Symbolic Link Reparse Data Buffer — https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/b41f1cbf-10df-4a47-98d4-1c52a833d913 · Mount Point Reparse Data Buffer — https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/ca069dad-ed16-42aa-b057-b6b207f447cc
5. Joachim Metz, libfsntfs "New Technologies File System (NTFS)" — https://github.com/libyal/libfsntfs/blob/main/documentation/New%20Technologies%20File%20System%20(NTFS).asciidoc
6. Linux-NTFS 문서, "$Reparse" — https://flatcap.github.io/linux-ntfs/ntfs/files/reparse.html
