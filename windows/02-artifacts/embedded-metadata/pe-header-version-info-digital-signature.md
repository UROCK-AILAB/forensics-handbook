# 실행 파일 메타데이터 (PE Header·Version Info·Digital Signature)

## 한 줄 요약

Windows 실행 파일(EXE·DLL) 안에는 PE 헤더, 버전 정보, 디지털 서명이 들어 있습니다. PE 헤더의 TimeDateStamp 는 빌드 시각처럼 보이지만, Windows 10 을 재현 가능한 빌드로 만든 뒤로 Windows 구성 파일에서는 시각이 아니라 해시입니다(참고 3). 같은 Microsoft 파일이라도 Office 의 `WINWORD.EXE` 는 그럴듯한 시각이었습니다(관찰). 버전 정보는 개발자가 적는 값입니다(참고 2). 서명이 유효하면 서명이 덮는 바이트가 서명 뒤로 바뀌지 않았다는 것을 알 수 있습니다(관찰). 세 가지를 함께 봐야 "이 파일이 무엇이고 언제 만들었나" 를 기록이 말하는 만큼 적을 수 있습니다.

> 이 페이지에서 "(관찰)" 을 붙인 내용은 PC 한 대에서 직접 확인한 것입니다. 확인 범위: Windows 11 (빌드 26200), 시간대 Korea Standard Time (UTC+9), Python 3.12.10 과 pefile, PowerShell 5.1 의 `Get-AuthenticodeSignature` 와 .NET `System.Security.Cryptography.Pkcs.SignedCms`. 시험 대상은 `C:\Windows\System32\notepad.exe`, `C:\Windows\System32\kernel32.dll`, 그리고 설치된 `git-bash.exe`·`python.exe`·`WINWORD.EXE` 의 사본입니다. 원본은 읽기만 했습니다. 한 대·한 판에서 본 결과라 다른 판에서도 같다고 장담하지 못합니다.

## 무엇을 기록하나 · 왜 생기나

| 부분 | 언제·누가 넣나 | 알려 주는 것 |
|---|---|---|
| PE 헤더 | 빌드할 때 들어갑니다. 0x3C 의 오프셋은 링크할 때 넣습니다(참고 1) | 절 수, 시각 도장, EXE 인지 DLL 인지, 32비트·64비트, 서브시스템, 체크섬, 데이터 디렉터리 위치 |
| 디버그 디렉터리 | 빌드할 때 들어갑니다 | 디버그 항목 종류, PDB 파일 경로(관찰) |
| 버전 정보 (VERSIONINFO) | 개발자가 리소스에 적습니다(참고 2) | 파일·제품 버전, 원래 파일 이름, 회사 이름, 설명 |
| 디지털 서명 (Authenticode) | 서명한 쪽 | 서명자, 서명 뒤로 바뀌지 않았는지, 타임스탬프 |

- 다른 기록이 이 값들을 옮겨 적습니다. Sysmon 이벤트의 FileVersion·Description·Product·Company·OriginalFileName 은 실행 파일 안의 정보에서 옵니다. 칸의 뜻은 [프로세스 생성 (이벤트 1)](/02-artifacts/event-logs/sysmon/1.md) 에서 다룹니다.
- Amcache 에 옮겨 적힌 값은 [실행 파일 항목 (InventoryApplicationFile)](/02-artifacts/execution/amcache-hve/inventoryapplicationfile.md) 에서 다룹니다.

## 위치와 버전별 차이

- 세 가지 모두 실행 파일 안에 있습니다. 파일만 있으면 어느 Windows 에서 가져왔든 읽을 수 있습니다.
- 파일 안 서명이 없는 파일도 카탈로그 서명으로 유효하다고 나올 수 있습니다(관찰). 카탈로그 파일이 어디에 저장되는지는 이 페이지에서 확인하지 못했습니다.

| 항목 | 범위 | 근거 |
|---|---|---|
| TimeDateStamp 자리에 바이너리에서 만든 해시를 넣음 | Windows 10 의 재현 가능한 빌드 (같은 소스에서 같은 바이너리가 나오는 빌드) | 참고 3 |
| Windows 구성 파일의 TimeDateStamp 가 1979년·2003년 같은 값 | Windows 11 빌드 26200 의 `notepad.exe`·`kernel32.dll` | 관찰 |
| 파일 안에 서명이 없는데 `SignatureType = Catalog` 로 유효 | Windows 11 빌드 26200 의 `notepad.exe` | 관찰 |

## 구조

### PE 헤더 (참고 1)

- MS-DOS 스텁의 0x3C 위치에 PE 서명까지의 파일 오프셋이 있습니다.
- 그 오프셋에 4바이트 서명 `PE\0\0`(P, E, 0, 0)이 있습니다.
- 서명 바로 뒤에 COFF 파일 헤더가 옵니다.

| COFF 헤더 안 위치 | 크기 | 칸 |
|---|---|---|
| 0 | 2 | Machine |
| 2 | 2 | NumberOfSections |
| 4 | 4 | TimeDateStamp |
| 8 | 4 | PointerToSymbolTable |
| 12 | 4 | NumberOfSymbols |
| 16 | 2 | SizeOfOptionalHeader |
| 18 | 2 | Characteristics |

- TimeDateStamp 는 1970-01-01 00:00 부터 센 초의 아래 32비트입니다. C 런타임의 time_t 값입니다. 참고 1 은 이 값이 파일을 만든 때를 나타낸다고 적었습니다. 푸는 법은 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
- Characteristics 의 0x0002 (IMAGE_FILE_EXECUTABLE_IMAGE) 는 실행할 수 있는 이미지라는 뜻입니다. 0x2000 (IMAGE_FILE_DLL) 은 DLL 이라는 뜻입니다.
- COFF 헤더 뒤에 선택적 헤더 (Optional Header) 가 옵니다. 첫 칸 Magic 이 0x10B 면 PE32, 0x20B 면 PE32+ 입니다.
- CheckSum 은 선택적 헤더의 오프셋 64 에 있는 4바이트입니다. 계산법은 IMAGHELP.DLL 에 있습니다. 로드할 때 이 값을 검사하는 것은 모든 드라이버, 부팅 때 읽는 DLL, 중요한 Windows 프로세스가 읽는 DLL 입니다.
- Subsystem 값 2 는 Windows GUI, 3 은 Windows 콘솔 (CUI) 입니다.

데이터 디렉터리 항목은 선택적 헤더 안 아래 위치에 있습니다.

| 디렉터리 | PE32 | PE32+ |
|---|---|---|
| Export | 96 | 112 |
| Import | 104 | 120 |
| Resource | 112 | 128 |
| Exception | 120 | 136 |
| Certificate Table | 128 | 144 |
| Base Relocation | 136 | 152 |
| Debug | 144 | 160 |

- 항목 하나는 8바이트입니다(관찰). 앞 4바이트는 위치, 뒤 4바이트는 크기입니다.
- Certificate Table 항목의 위치 값은 RVA 가 아니라 파일 오프셋입니다. 인증서는 메모리에 올라가지 않기 때문입니다.
- `.rsrc` 절 안의 트리 구조와 Rich 헤더는 이 페이지에서 확인하지 못했습니다.

### 디버그 디렉터리 (관찰)

pefile 이 붙이는 이름으로 본 디버그 항목 종류입니다.

| 번호 | 이름 |
|---|---|
| 2 | CODEVIEW |
| 10 | RESERVED10 |
| 12 | VC_FEATURE |
| 13 | POGO |
| 16 | REPRO |
| 20 | EX_DLLCHARACTERISTICS |

- 디버그 항목의 날짜·시각 도장은 대부분 C 런타임 시각 형식입니다. IMAGE_DEBUG_TYPE_REPRO 는 예외입니다(참고 1).
- 값이 0 이나 0xFFFFFFFF 면 의미 있는 시각이 아닙니다(참고 1).

CODEVIEW 항목에서 읽은 PDB 파일 경로입니다.

| 파일 | PDB 경로 |
|---|---|
| `notepad.exe` | `notepad.pdb` |
| `kernel32.dll` | `kernel32.pdb` |
| `git-bash.exe` | `D:\git-sdk-64-build-installers\usr\src\MINGW-packages\mingw-w64-git\src\git\git-bash.pdb` |
| `python.exe` | `D:\a\1\b\bin\amd64\python.pdb` |
| `WINWORD.EXE` | `D:\dbs\el\omr\Target\x64\ship\postc2r\x-none\winword.pdb` |

- 파일 이름만 남은 경우도 있고, 빌드한 컴퓨터의 폴더 경로가 통째로 남은 경우도 있었습니다.

### 버전 정보 (참고 2)

VERSIONINFO 리소스는 파일 버전, 대상 OS, 원래 파일 이름 같은 정보를 담습니다. versionID 는 반드시 1 입니다.

고정 정보입니다.

| 칸 | 내용 |
|---|---|
| FILEVERSION | 16비트 숫자 4개를 32비트 값 2개에 담습니다. 예: `FILEVERSION 3,10,0,61` → 0x0003000A, 0x0000003D |
| PRODUCTVERSION | 같은 방식으로 적은 제품 버전 |
| FILEFLAGS | VS_FF_DEBUG(디버그 정보 포함), VS_FF_PATCHED(같은 버전 번호의 원래 배포 파일과 다르게 고침), VS_FF_PRERELEASE(개발판), VS_FF_PRIVATEBUILD(표준 절차로 빌드하지 않음. PrivateBuild 글자열 필요), VS_FF_SPECIALBUILD(같은 버전의 변형. SpecialBuild 글자열 필요) |
| FILEOS | 대상 OS. 예: VOS_NT_WINDOWS32 |
| FILETYPE | VFT_APP, VFT_DLL, VFT_DRV, VFT_FONT, VFT_VXD, VFT_STATIC_LIB |

StringFileInfo 에는 미리 정한 이름이 있습니다.

- 반드시 넣는 이름: CompanyName, FileDescription, FileVersion, InternalName, OriginalFilename, ProductName, ProductVersion
- 넣어도 되는 이름: Comments, LegalCopyright, LegalTrademarks, PrivateBuild, SpecialBuild
- OriginalFilename 은 경로 없는 원래 파일 이름입니다. 사용자가 파일 이름을 바꿨는지 앱이 알 수 있게 하려고 둡니다.
- InternalName 은 내부 이름입니다. DLL 이면 모듈 이름을 적습니다. 없으면 확장자 없는 원래 파일 이름을 적습니다.
- 블록 이름은 언어 ID 와 문자 집합 ID 를 16진수로 이은 것입니다. 예를 들어 `040904E4` 는 미국 영어와 1252 입니다.
- VarFileInfo 의 Translation 값은 (언어, 코드 페이지) 쌍의 목록입니다.
- 언어 ID 0x0412 는 한국어입니다. 문자 집합 949 (0x03B5) 는 한국어, 1200 (0x04B0) 은 유니코드입니다.

이 PC 의 파일 다섯 개에서 읽은 값입니다(관찰).

| 파일 | 블록 | 눈여겨볼 값 |
|---|---|---|
| `notepad.exe` | `040904B0` | OriginalFilename `NOTEPAD.EXE`, InternalName `Notepad`, FileVersion `10.0.26100.9278 (WinBuild.160101.0800)` |
| `kernel32.dll` | | OriginalFilename `kernel32` (확장자 없음) |
| `git-bash.exe` | | OriginalFilename `git.exe`, InternalName `git`. 실제 파일 이름과 다르지만 정상 배포 파일입니다 |
| `python.exe` | `000004b0` (언어 중립) | FileVersion 글자열 `3.12.10`, 고정 정보 FILEVERSION `3.12.10150.1013`. 글자열과 이진 값이 달랐습니다 |
| `WINWORD.EXE` | `000004E4` | Translation 0x0000·0x04E4. LegalTrademarks1·LegalTrademarks2 처럼 미리 정하지 않은 이름도 있었습니다 |

- 다섯 파일 모두 VS_FIXEDFILEINFO 서명이 0xFEEF04BD 였습니다.
- 다섯 파일 모두 FileDate 칸이 0 이었습니다.

### 디지털 서명: WIN_CERTIFICATE (참고 1)

Certificate Table 이 가리키는 곳에는 WIN_CERTIFICATE 항목이 이어집니다.

| 위치 | 크기 | 칸 | 값 |
|---|---|---|---|
| 0 | 4 | dwLength | 항목 길이 |
| 4 | 2 | wRevision | 0x0100 = WIN_CERT_REVISION_1_0, 0x0200 = WIN_CERT_REVISION_2_0 |
| 6 | 2 | wCertificateType | 0x0002 = WIN_CERT_TYPE_PKCS_SIGNED_DATA (bCertificate 가 PKCS#7 SignedData). 0x0001 = X509 (지원하지 않음) |
| 8 | 가변 | bCertificate | 서명 데이터 |

- 인증서 표는 8바이트 경계에 맞춘 항목들이 이어진 것입니다. 파일의 원래 끝과 표 사이, 그리고 항목 끝에 0 을 채웁니다.

서명이 있는 파일 네 개(`kernel32.dll`, `git-bash.exe`, `WINWORD.EXE`, `python.exe`)에서 본 모양입니다(관찰).

- 인증서 표는 파일 맨 끝에 있었습니다. 표가 끝나는 곳이 파일 끝이었고, 시작 오프셋은 8의 배수였습니다.
- dwLength 는 디렉터리 크기와 같았습니다. wRevision 은 0x0200, wCertificateType 은 0x0002 였습니다.
- CheckSum 칸은 네 파일 모두 다시 계산한 값과 같았습니다.

### 서명이 덮는 범위 (관찰)

- CheckSum 4바이트, Certificate Table 디렉터리 항목 8바이트, 인증서 표 자체를 빼고 SHA-256 을 계산했습니다. 네 파일 모두 서명 안에 그 값이 들어 있었습니다.
- 아무것도 빼지 않고 계산한 값은 서명 안에 없었습니다.
- 이 범위를 적은 공식 문장은 참고 1 에서 확인하지 못했습니다.

`git-bash.exe` 사본을 바꿔 가며 `Get-AuthenticodeSignature` 결과를 봤습니다.

| 바꾼 것 | 결과 |
|---|---|
| 파일 이름만 | Valid |
| CheckSum 한 바이트 | Valid |
| COFF 헤더 TimeDateStamp 한 바이트 | HashMismatch |
| 첫 절 안의 한 바이트 | HashMismatch |

- 서명이 유효하면 TimeDateStamp 와 버전 정보는 서명 뒤로 바뀌지 않은 것입니다.
- 파일 이름과 CheckSum 은 서명 검증과 관계가 없습니다.

> 그림 자리: PE 파일 한 개를 세로 막대로 그리고, 서명 해시에서 빠지는 세 곳(CheckSum 4바이트, Certificate Table 디렉터리 항목 8바이트, 파일 끝의 인증서 표)을 다른 색으로 표시

### 카탈로그 서명 (관찰)

| 파일 | 파일 안 서명 | `Get-AuthenticodeSignature` 의 SignatureType |
|---|---|---|
| `notepad.exe` | 없음 (Certificate Table 크기 0) | Catalog. 결과는 Valid, 서명자 CN=Microsoft Windows |
| `kernel32.dll` | 있음 (17,104바이트) | Catalog |
| `git-bash.exe` | 있음 | Authenticode |
| `python.exe` | 있음 | Authenticode |

- "Catalog" 라는 결과는 파일 안에 서명이 없다는 뜻이 아닙니다.
- 파일 안에 서명이 있는지는 Certificate Table 로 따로 봅니다.
- 이미지를 오프라인으로 분석할 때 카탈로그 서명을 검증하는 방법은 이 페이지에서 확인하지 못했습니다.

### 서명 타임스탬프 (참고 4)

- Authenticode 타임스탬프는 PKCS #7 연서명 (countersignature) 입니다. 서명 인증서가 만료된 뒤에도 서명을 검증할 수 있게 합니다.
- 타임스탬프가 없으면 서명 인증서가 만료될 때 서명도 무효가 됩니다. 그러면 Windows 는 서명 없는 파일로 봅니다.
- 연서명은 원래 서명을 붙인 뒤에 덧붙일 수 있는 비인증 속성 (unauthenticated attribute) 입니다. 연서명이 서명하는 대상은 원래 서명(EncryptedDigest)입니다.
- 타임스탬프 서버의 응답에는 서명 시각 (signing time) 인증 속성이 들어 있습니다. 객체 식별자 (OID) 는 1.2.840.113549.1.9.5 입니다.
- 옛 방식 연서명의 OID 는 1.2.840.113549.1.9.6 입니다. 요청에 쓰는 countersignatureType OID 는 1.3.6.1.4.1.311.3.2.1 입니다.
- 권장 방식은 SHA-256 해시(`/fd SHA256`)와 RFC 3161 타임스탬프(`/tr`, `/td SHA256`)입니다. 코드 서명에서 SHA-1 은 점점 믿지 않습니다.

`git-bash.exe` 와 `python.exe` 의 서명에서 본 값입니다(관찰).

- 두 파일 모두 서명 내용 형식 OID 는 1.3.6.1.4.1.311.2.1.4 였고, 해시는 sha256 이었습니다.
- 두 파일 모두 타임스탬프가 비인증 속성 OID 1.3.6.1.4.1.311.3.3.1 에 들어 있었습니다. 옛 방식 OID 1.2.840.113549.1.9.6 이 아니었습니다.
- 그 안의 내용 형식 OID 는 1.2.840.113549.1.9.16.1.4 였습니다.
- 두 OID 의 공식 이름은 확인하지 못했습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 서명이 유효하면, 서명이 덮는 바이트가 서명 뒤로 바뀌지 않았습니다(관찰) | 파일이 안전한지. 파일이 실행됐는지 |
| 서명이 유효하면, 서명자 인증서의 주체 | 파일 이름이 바뀌지 않았는지. 이름은 서명 검증과 관계가 없습니다(관찰) |
| 타임스탬프가 있으면, 그 시각에 서명이 이미 있었습니다(참고 4) | 빌드 시각, 설치 시각, 이 PC 에 들어온 시각 |
| TimeDateStamp 에 적힌 값 | 실제 빌드 시각. Windows 10 이후 Windows 구성 파일은 해시입니다(참고 3) |
| 버전 정보에 적힌 이름·버전·회사 | 이름을 바꿔 숨겼는지. 정상 배포 파일도 OriginalFilename 이 실제 이름과 다릅니다(관찰) |
| PDB 경로에 적힌 폴더 이름 | 그 폴더가 있는 컴퓨터가 누구의 것인지 |

- 다른 제작사 파일의 TimeDateStamp 가 실제 빌드 시각인지는 확인하지 못했습니다.
- 서명이 없는 파일이면 버전 정보가 바뀌지 않았다는 보증도 없습니다.

### 보고서 문장

아래 경로와 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "`C:\Users\A\AppData\Local\Temp\svc.exe` 의 버전 정보에는 OriginalFilename 이 `tool.exe` 로 적혀 있습니다. 이 파일에는 파일 안 서명이 없습니다(Certificate Table 크기 0). COFF 헤더의 TimeDateStamp 는 2020-01-01 00:00:00 UTC 로 풀립니다. 이 값이 실제 빌드 시각인지는 이 기록만으로 알 수 없습니다."
- 쓰면 안 되는 문장: "공격자가 2020년 1월 1일에 tool.exe 를 만들어 svc.exe 로 이름을 바꿨다."

## 시각 해석

| 값 | 형식 | 누가 정하나 | 읽을 때 주의 |
|---|---|---|---|
| COFF 헤더 TimeDateStamp | 1970 기준 초 (아래 32비트) | 빌드할 때 들어갑니다 | Windows 10 이후 Windows 구성 파일은 해시입니다(참고 3) |
| 디버그 항목 TimeDateStamp | 대부분 같은 형식 | 빌드할 때 들어갑니다 | REPRO 항목은 예외입니다. 0 이나 0xFFFFFFFF 는 의미 없는 값입니다(참고 1) |
| 서명자 인증 속성 signingTime | | 서명하는 쪽으로 보이지만 확인하지 못했습니다 | 타임스탬프 기관의 보증이 있는지는 확인하지 못했습니다 |
| 타임스탬프 genTime | | 타임스탬프 기관 | 그 시각에 서명이 이미 있었다는 보증입니다(참고 4) |
| 파일 시스템 시각 | FILETIME | 파일 시스템과 설치 프로그램 | 아래 관찰처럼 빌드·설치 시각과 다를 수 있습니다 |

### Windows 구성 파일의 TimeDateStamp (관찰)

| 파일 | TimeDateStamp | UTC 로 풀면 | 파일 버전 |
|---|---|---|---|
| `notepad.exe` | 0x112F10A4 | 1979-02-19 18:32:04 | 10.0.26100.9278 |
| `kernel32.dll` | 0x3ECCCF12 | 2003-05-22 13:22:26 | 10.0.26100.9444 |

- 두 파일 모두 디버그 디렉터리에 IMAGE_DEBUG_TYPE_REPRO (16) 항목이 있었습니다.
- 디버그 항목들의 TimeDateStamp 도 헤더 값과 같았습니다.
- 파일 버전은 최근 판인데 시각 값은 맞지 않습니다. 참고 3 은 이 값을 재현 가능한 고유 ID 로 봐야 한다고 설명합니다. "시각 도장을 결과 바이너리의 해시로 두면 재현성이 지켜진다" 는 것이 까닭입니다(참고 3).
- REPRO 항목이 있는 파일은 헤더의 TimeDateStamp 도 시각이 아닐 수 있다고 보고 읽습니다.

### REPRO 항목이 없는 파일의 시각 비교 (관찰)

`git-bash.exe`, `python.exe`, `WINWORD.EXE` 의 TimeDateStamp 는 그럴듯한 시각이었습니다. 세 파일에는 REPRO 항목이 없었습니다. `WINWORD.EXE` 는 Microsoft 파일이지만 Windows 구성 파일이 아니고, 값은 2026-09-15 11:58:07 UTC 였습니다.

| 값 (UTC) | `git-bash.exe` | `python.exe` |
|---|---|---|
| COFF 헤더 TimeDateStamp | 2026-04-20 17:51:23 | 2025-04-08 12:25:11 |
| 서명자 signingTime | 2026-04-20 18:00:31 | 없음 |
| 타임스탬프 genTime | 2026-04-20 18:00:34 | 2025-04-08 12:39:26.074 |
| 파일 수정 시각 | 2026-04-20 08:51:22 | 2025-04-08 03:57:36 |
| 파일 만든 시각 | 2026-06-26 03:20:51 (설치한 때) | 2025-04-08 03:57:36 |

- 두 파일 모두 TimeDateStamp 가 타임스탬프 genTime 보다 앞섰습니다.
- `git-bash.exe` 는 CODEVIEW 디버그 항목의 TimeDateStamp 가 0 이었습니다. 헤더 값은 위 시각이었습니다.
- 두 파일 모두 수정 시각이 서명 시각보다 앞섭니다. 9시간(이 PC 의 시간대 차이)을 더하면 `git-bash.exe` 는 17:51:22, `python.exe` 는 12:57:36 이 됩니다.
- 설치 프로그램이 넣은 값으로 보이지만, 원인은 확인하지 못했습니다.
- 설치된 파일의 수정 시각은 설치 시각도 빌드 시각도 아닐 수 있습니다. 파일 시스템 시각은 [두 벌의 시각](/01-foundations/disk-volume/ntfs/standard-information-file-name.md) 에서 다룹니다.

## 함정과 한계

1. **TimeDateStamp 를 빌드 시각으로 단정합니다.** Windows 10 이후 Windows 구성 파일은 해시입니다(참고 3). 반대로 Microsoft 파일이면 모두 해시라고 보지도 않습니다. `WINWORD.EXE` 에는 REPRO 항목이 없었고 값도 그럴듯한 시각이었습니다(관찰). 다른 파일의 값이 실제 빌드 시각인지도 확인하지 못했습니다.
2. **1979년 같은 시각을 조작의 증거로 씁니다.** 정상 Windows 구성 파일도 그런 값이었습니다(관찰). 디버그 디렉터리의 REPRO 항목을 먼저 봅니다.
3. **OriginalFilename 이 다르면 위장이라고 씁니다.** 정상 배포 파일인 `git-bash.exe` 도 OriginalFilename 이 `git.exe` 였습니다(관찰). 해시와 서명자를 함께 봅니다.
4. **버전 글자열만 봅니다.** `python.exe` 는 FileVersion 글자열과 고정 정보의 이진 값이 달랐습니다(관찰). 도구가 어느 쪽을 보여 주는지 확인합니다.
5. **"Catalog" 를 파일 안 서명이 없다는 뜻으로 읽습니다.** 파일 안에 서명이 있는 `kernel32.dll` 도 Catalog 로 나왔습니다(관찰).
6. **검증 결과만 보고 파일 안 서명을 확인하지 않습니다.** 파일 안 서명이 없는 `notepad.exe` 도 Valid 였습니다(관찰). 파일 안 서명은 Certificate Table 로 따로 봅니다.
7. **서명이 이름 바꾸기를 잡는다고 봅니다.** 파일 이름을 바꿔도 Valid 였습니다(관찰).
8. **CheckSum 이 맞지 않으면 서명도 깨졌다고 봅니다.** CheckSum 을 바꿔도 Valid 였습니다(관찰).
9. **서명자 signingTime 을 보증된 시각으로 씁니다.** 참고 4 는 타임스탬프 응답 안의 서명 시각만 설명합니다. 서명자 쪽 값에 타임스탬프 기관의 보증이 있는지는 확인하지 못했습니다. 보고서에는 타임스탬프 genTime 을 씁니다.
10. **설치된 파일의 수정 시각을 설치 시각으로 씁니다.** 관찰한 두 파일은 수정 시각이 서명 시각보다 앞섰습니다(관찰).
11. **이미지에서 카탈로그 서명을 바로 검증할 수 있다고 봅니다.** 오프라인 검증 방법은 이 페이지에서 확인하지 못했습니다.

### 지우기와 조작

- 서명이 덮는 바이트를 한 바이트라도 바꾸면 HashMismatch 가 나왔습니다(관찰). TimeDateStamp 를 고친 서명 파일은 이 결과로 드러납니다.
- 파일 이름 바꾸기와 CheckSum 바꾸기는 서명 결과에 드러나지 않았습니다(관찰). 이름은 OriginalFilename·해시와 맞춰 봅니다. 알려진 파일 해시와 대조하는 법은 [해시셋 대조와 유사 해시](/03-techniques/analysis/hash-set-fuzzy-hash.md) 에서 다룹니다.
- 서명이 없는 파일은 이런 보증이 없습니다. 버전 정보와 TimeDateStamp 를 다른 기록과 맞춰 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 참고 1 의 구조에 맞춰 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다. `??` 는 이 예시에서 다루지 않는 바이트입니다.

```
오프셋   00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x0030   ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 80 00 00 00
 …
0x0080   50 45 00 00 ?? ?? 06 00 00 E1 0B 5E 00 00 00 00
0x0090   00 00 00 00 ?? ?? 02 20 0B 02 ?? ?? ?? ?? ?? ??
 …
0x0120   ?? ?? ?? ?? ?? ?? ?? ?? 00 20 00 00 00 05 00 00
 …
0x2000   00 05 00 00 00 02 02 00 ?? ?? ?? ?? ?? ?? ?? ??
```

1. 0x3C 의 `80 00 00 00` 을 읽으면 0x80 입니다. PE 서명이 0x80 에 있습니다.
2. 0x80 의 `50 45 00 00` 은 `PE\0\0` 입니다. COFF 헤더는 0x84 부터입니다.
3. 0x86 의 `06 00` 은 NumberOfSections 6 입니다.
4. 0x88 의 `00 E1 0B 5E` 를 뒤집어 읽으면 0x5E0BE100, 즉 1,577,836,800 초입니다. 2020-01-01 00:00:00 UTC 로 풀립니다. 시각으로 쓰기 전에 디버그 디렉터리에 REPRO 항목이 있는지 봅니다.
5. 0x96 의 `02 20` 은 0x2002 입니다. 0x0002 (실행할 수 있는 이미지) 와 0x2000 (DLL) 이 함께 켜져 있으니 DLL 입니다.
6. 선택적 헤더는 0x98 부터입니다. `0B 02` 는 0x20B, 즉 PE32+ 입니다.
7. CheckSum 은 0x98 + 64 = 0xD8 에 있습니다.
8. PE32+ 의 Certificate Table 항목은 0x98 + 144 = 0x128 에 있습니다. 위치 `00 20 00 00` 은 파일 오프셋 0x2000, 크기 `00 05 00 00` 은 0x500 입니다.
9. 파일 오프셋 0x2000 에서 dwLength 0x500, wRevision 0x0200, wCertificateType 0x0002 를 읽습니다. 그 뒤가 PKCS#7 SignedData 입니다.
10. 0x2000 + 0x500 = 0x2500 이 파일 크기와 같은지, 0x2000 이 8의 배수인지 봅니다. 관찰한 서명 파일들은 둘 다 맞았습니다.

### 공개 도구로 한 번

이 페이지의 관찰에 쓴 도구를 예로 듭니다.

- Python 의 pefile 로 COFF 헤더, 선택적 헤더, 디버그 디렉터리, 버전 정보를 읽을 수 있습니다.
- PowerShell 의 `Get-AuthenticodeSignature` 는 서명 상태(Valid, HashMismatch 등)와 SignatureType(Authenticode, Catalog)을 보여 줍니다.
- .NET 의 `SignedCms` 로 서명 데이터를 풀어 서명자 속성과 타임스탬프를 읽을 수 있습니다.

어느 도구를 쓰든 아래를 확인합니다.

- TimeDateStamp 를 날짜로 바꿔 보여 줄 때 REPRO 항목을 함께 보여 주는지 확인합니다.
- 버전 정보를 글자열에서 읽는지, 고정 정보에서 읽는지 확인합니다.
- 서명 결과가 파일 안 서명에서 왔는지, 카탈로그에서 왔는지 확인합니다.
- 몇 개는 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [실행 파일 항목 (InventoryApplicationFile)](/02-artifacts/execution/amcache-hve/inventoryapplicationfile.md) | Amcache 에 옮겨 적힌 버전·게시자·링크 시각 |
| [프로세스 생성 (이벤트 1)](/02-artifacts/event-logs/sysmon/1.md) | 실행 때 기록된 OriginalFileName·버전 정보·해시 |
| [이미지 로드·프로세스 접근 (이벤트 7·8·10)](/02-artifacts/event-logs/sysmon/7-8-10.md) | 불러온 모듈의 버전 정보와 서명 |
| [프로세스 생성](/02-artifacts/event-logs/4688.md) | 파일 경로로 실행한 기록 |
| [다운로드 출처 표시 (Zone.Identifier)](/02-artifacts/filesystem/zone-identifier.md) | 파일이 바깥에서 들어왔는지 |
| [의심 실행 파일 선별](/03-techniques/analysis/code-signing-yara.md) | 서명과 규칙으로 여러 파일을 한꺼번에 선별하기 |
| [해시셋 대조와 유사 해시](/03-techniques/analysis/hash-set-fuzzy-hash.md) | 알려진 파일과 같은지 |
| [두 벌의 시각](/01-foundations/disk-volume/ntfs/standard-information-file-name.md) | 파일 시스템 시각 |

어떤 프로그램을 언제 실행했는지 여러 기록으로 좁히는 순서는 [어떤 프로그램을 언제 실행했나](/04-scenarios/activity/program-execution.md) 에서 다룹니다. 파일의 출처는 [이 파일은 어디서 왔나](/04-scenarios/activity/file-origin.md) 를 봅니다.

## 실습

**직접 만든 Windows 10·11 가상 머신**에서 해 봅니다.

1. `C:\Windows\System32\notepad.exe` 의 TimeDateStamp 를 풀어 보십시오. 몇 년입니까? 디버그 디렉터리에 REPRO 항목이 있습니까?
2. 같은 파일에 파일 안 서명이 있는지 Certificate Table 로 확인하십시오. `Get-AuthenticodeSignature` 의 SignatureType 은 무엇입니까?
3. 서명된 다른 제작사 실행 파일의 사본을 만들어 이름만 바꾼 뒤 서명을 검증해 보십시오. 이어서 TimeDateStamp 한 바이트를 바꾼 뒤 다시 검증해 보십시오. 결과가 어떻게 다릅니까?
4. 그 파일의 TimeDateStamp, 타임스탬프 genTime, 파일 시스템 시각을 나란히 놓아 보십시오. 순서가 맞습니까?
5. 시스템 실행 파일 하나를 다른 이름으로 복사해 버전 정보의 OriginalFilename 과 비교해 보십시오.

**NIST CFReDS 같은 공개 검체의 Windows 디스크 이미지**로도 풀어 봅니다.

1. 사용자 폴더(받은 파일, 임시 폴더 등)에 있는 실행 파일을 모아 파일 안 서명이 있는 것과 없는 것으로 나눠 보십시오.
2. 서명이 없는 파일의 OriginalFilename 과 실제 파일 이름이 다른 것이 있습니까?
3. PDB 경로가 폴더째 남은 파일이 있습니까? 그 경로에서 무엇을 말할 수 있고 무엇을 말할 수 없는지 적어 보십시오.

## 참고 문헌

1. Microsoft Learn, "PE Format" — https://learn.microsoft.com/en-us/windows/win32/debug/pe-format
2. Microsoft Learn, "VERSIONINFO resource" — https://learn.microsoft.com/en-us/windows/win32/menurc/versioninfo-resource
3. Raymond Chen, The Old New Thing, "Why are the module timestamps in Windows 10 so nonsensical?" (2018-01-03) — https://devblogs.microsoft.com/oldnewthing/20180103-00/?p=97705
4. Microsoft Learn, "Time Stamping Authenticode Signatures" — https://learn.microsoft.com/en-us/windows/win32/seccrypto/time-stamping-authenticode-signatures
