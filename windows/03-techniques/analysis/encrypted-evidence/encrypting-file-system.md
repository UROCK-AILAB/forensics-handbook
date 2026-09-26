---
title: "EFS 암호화 파일"
parent: "암호화 증거 다루기"
grand_parent: "기법 · 분석"
nav_order: 3420
---

# EFS 암호화 파일 (Encrypting File System)

> 위치: [암호화 증거 다루기 (Encrypted Evidence)](index.md) > EFS 암호화 파일

## 한 줄 요약

EFS (Encrypting File System) 는 NTFS 볼륨의 파일을 하나씩 공개 키 방식으로 암호화하는 Windows 기능입니다.
암호화한 파일은 MFT 의 파일 속성 플래그 0x00004000 으로 찾으며, 이런 파일에는 이름이 `$EFS` 인 로그 유틸리티 스트림이 붙습니다.
켜진 시스템에서는 `cipher` 명령으로 암호화 파일 목록을 뽑고 인증서와 키를 백업할 수 있습니다.

## 언제 쓰나

- 이미지에서 꺼낸 NTFS 파일이 열리지 않을 때
- 켜진 시스템을 조사하면서 EFS 파일이 있는지, 키를 백업할지 정해야 할 때
- 파일이 암호화되어 있었다는 사실을 보고서에 적어야 할 때

## EFS 가 암호화하는 것

EFS 는 NTFS 볼륨의 개별 파일을 암호화합니다. 파일 시스템이 암호화를 지원하는지는 `GetVolumeInformation` 이 돌려주는 `FS_FILE_ENCRYPTION` 비트로 확인합니다.

- 압축한 파일은 암호화할 수 없습니다. 압축과 암호화는 함께 쓸 수 없습니다.
- 시스템 파일, 시스템 디렉터리, 루트 디렉터리도 암호화할 수 없습니다. 트랜잭션도 암호화할 수 없습니다.
- 희소 파일 (Sparse File) 은 암호화할 수 있습니다.

암호화한 원본을 `CopyFile`·`CopyFileEx` 로 복사하면 `lsass.exe` 안의 EFS 서비스가 호출한 사용자를 가장해 대상 파일을 만들고, 그 대상 파일에 키를 적용합니다.

## 절차

1. **볼륨이 NTFS 인지 확인합니다.** EFS 는 NTFS 에만 있습니다. NTFS 구조는 [NTFS 구조](../../../01-foundations/disk-volume/ntfs/index.md) 를 봅니다.
2. **MFT 에서 암호화 표시가 있는 파일을 모읍니다.** `$STANDARD_INFORMATION` 의 플래그, `$FILE_NAME` 의 플래그, 속성 헤더의 플래그, `$EFS` 스트림의 네 자리를 봅니다. 값은 아래 표에 있습니다. MFT 레코드를 읽는 법은 [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md) 에 있습니다.
3. **표시를 모두 적어 둡니다.** 한 자리의 표시만 보고 판단하지 않습니다. 네 자리의 값을 파일마다 함께 적습니다.
4. **켜진 시스템이면 `cipher` 로 목록을 뽑습니다.** `cipher /u /n` 을 씁니다. `/n` 을 빼면 파일이 바뀔 수 있습니다. 아래 "cipher 명령과 증거 변경" 표를 봅니다.
5. **켜진 시스템이면 키 백업을 정합니다.**
   - `cipher /x` 로 EFS 인증서와 키를 파일로 백업할 수 있습니다.
   - 백업 파일은 증거 볼륨이 아닌 외부 매체에 씁니다.
   - `cipher /y` 로 현재 EFS 인증서 지문을 기록해 둡니다.
   - 켜진 시스템에서 명령을 실행할 때 따를 순서는 [라이브 응답](../../process-acquisition/live-response/index.md) 을 봅니다.
6. **꺼진 이미지라면 개인 키가 든 파일부터 찾습니다.**
   - 사용자가 `cipher /x` 로 백업한 파일이나 복구 에이전트의 `.pfx` 를 찾습니다.
   - 관리자는 `.pfx` 를 가져와 개별 파일을 복구할 수 있습니다.
   - 이미지 안에서 사용자 개인 키를 되살리려면 Windows 가 사용자 비밀 값을 보호하는 구조를 알아야 합니다. 그 구조는 [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) 에 있습니다.
7. **기록합니다.** 파일마다 네 자리의 표시, 복호 여부, 쓴 키의 출처를 적습니다.

### MFT 안의 표시

| 자리 | 값 | 이름 | 뜻 |
|---|---|---|---|
| `$STANDARD_INFORMATION` 과 `$FILE_NAME` 의 파일 속성 플래그 | 0x00004000 | `FILE_ATTRIBUTE_ENCRYPTED` | 암호화한 파일 |
| 같은 자리 (비교용) | 0x00000800 | `FILE_ATTRIBUTE_COMPRESSED` | 압축한 파일 |
| MFT 속성 헤더의 데이터 플래그 | 0x4000 | `ATTRIBUTE_FLAG_ENCRYPTED` | 이 속성의 데이터가 암호화됨 |
| 로그 유틸리티 스트림 (`$LOGGED_UTILITY_STREAM`, 속성 형식 0x100) | 이름 `$EFS` | — | EFS 용 스트림 |

로그 유틸리티 스트림 속성 가운데 이름이 `$EFS` 인 것이 EFS 용입니다. `$EFS` 안의 구조를 밝힌 공개 형식 문서는 없습니다.

### cipher 명령과 증거 변경

`cipher` 는 켜진 시스템에서 쓰는 Windows 기본 명령입니다.

| 명령 | 하는 일 | 파일·키를 바꾸나 |
|---|---|---|
| `cipher` (인자 없음) | 현재 디렉터리의 암호화 상태를 보여 줍니다. 암호화한 항목은 E, 아닌 항목은 U 입니다 | 보여 주기만 함 |
| `cipher /c` | 암호화한 파일의 정보를 보여 줍니다 | 보여 주기만 함 |
| `cipher /u /n` | 로컬 드라이브의 암호화 파일을 모두 찾습니다 | 바꾸지 않음 |
| `cipher /u` (`/n` 없이) | 사용자 파일 암호화 키나 복구 에이전트 키가 바뀐 경우 파일을 갱신합니다 | 바꿈 |
| `cipher /x[:efsfile] [파일이름]` | EFS 인증서와 키를 파일로 백업합니다. `:efsfile` 을 붙이면 그 파일에 쓴 사용자 인증서를 백업합니다 | 백업 파일을 새로 씀 |
| `cipher /y` | 로컬 컴퓨터의 현재 EFS 인증서 지문을 보여 줍니다 | 보여 주기만 함 |
| `cipher /r:<파일이름>` | 복구 에이전트 키와 인증서를 만들어 `.pfx`(인증서와 개인 키)와 `.cer`(인증서만)로 씁니다 | 파일을 새로 씀 |
| `cipher /k` | EFS 용 새 인증서와 키를 만듭니다 | 바꿈 |
| `cipher /rekey` | 지정한 암호화 파일이 지금 설정된 EFS 키를 쓰도록 갱신합니다 | 바꿈 |
| `cipher /removeuser /certhash:<hash>` | 인증서의 SHA1 해시로 사용자를 뺍니다 | 바꿈 |
| `cipher /w:<디렉터리>` | 볼륨 전체의 빈 공간에서 데이터를 지웁니다 | 바꿈. 비할당 영역이 사라짐 |

- 관리자는 `.cer` 을 EFS 복구 정책에 넣어 복구 에이전트를 만듭니다.
- 상위 디렉터리가 암호화되어 있지 않으면, 암호화 파일이 수정될 때 복호될 수 있습니다.

### 헥스로 한 번 따라가기

아래 값은 **명세로 만든 예시**입니다. 실제 파일에서 나온 값이 아닙니다.
NTFS 는 여러 바이트 값을 리틀 엔디언으로 적습니다. 그래서 헥스 편집기에서는 바이트 순서가 뒤집혀 보입니다.

```
파일 속성 플래그 4바이트 (명세로 만든 예시)
00 40 00 00   → 0x00004000  FILE_ATTRIBUTE_ENCRYPTED
00 08 00 00   → 0x00000800  FILE_ATTRIBUTE_COMPRESSED
```

둘째 바이트가 `40` 이면 암호화 플래그, `08` 이면 압축 플래그입니다.
두 플래그는 비트 자리가 달라서 둘 다 켜진 값(`00 48 00 00`)도 만들 수는 있지만, 압축과 암호화는 함께 쓸 수 없으므로 이런 값이 보이면 파서가 제대로 읽었는지부터 다시 확인합니다.

## 도구

아래 공개 도구는 예로만 듭니다. 한 도구의 결과에만 기대지 않습니다.

| 도구 | 쓰임 |
|---|---|
| `cipher.exe` (Windows 기본) | 켜진 시스템에서 암호화 파일 목록을 뽑고 인증서·키를 백업합니다 |
| libfsntfs (`fsntfsinfo`) | MFT 항목의 속성과 플래그를 읽습니다 |
| The Sleuth Kit (`istat`) | MFT 레코드 하나의 속성 목록을 봅니다 |
| 헥스 편집기 | 파일 속성 플래그 4바이트를 직접 봅니다 |

## 함정과 한계

- **압축 플래그를 암호화 플래그로 읽습니다.** 0x0800 과 0x4000 은 다른 비트입니다.
- **`cipher /u` 를 `/n` 없이 실행합니다.** 키가 바뀐 경우 파일을 갱신합니다. 조사할 때는 반드시 `/n` 을 붙입니다.
- **`cipher /w` 를 증거 시스템에서 실행합니다.** 볼륨 전체의 빈 공간을 지웁니다. 지운 파일을 되살릴 자리가 사라집니다.
- **이미지에서 꺼낸 파일을 평문이라고 봅니다.** 이미지에서 NTFS 데이터를 그대로 꺼내면 암호문입니다. 키 없이 열면 알아볼 수 없는 바이트만 나옵니다.
- **켜진 시스템에서 보통 복사로 파일을 모읍니다.** `CopyFile` 로 복사하면 EFS 서비스가 대상 파일에도 키를 적용합니다. 복사본도 EFS 로 암호화되어 있을 수 있습니다.
- **`$EFS` 스트림을 해석하려 합니다.** 구조를 밝힌 공개 명세가 없습니다. 도구가 보여 주는 해석은 그 도구의 결과로만 적습니다.

## 결과를 어떻게 해석하나

- **플래그 0x4000 이 켜진 파일**: MFT 레코드를 기록한 때 그 파일이 EFS 로 암호화된 상태였다는 뜻입니다.
- **증명하지 못하는 것**: 플래그만으로는 누가, 언제 암호화했는지 알 수 없습니다. MFT 시각이 무엇을 따라 바뀌는지는 [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md) 을 봅니다.
- **플래그가 없는 파일**: 한 번도 암호화된 적이 없다는 뜻은 아닙니다. 상위 디렉터리가 암호화되어 있지 않으면 수정할 때 복호될 수 있습니다. 옛 상태는 섀도 복사본 속 MFT 와 비교해 봅니다. 방법은 [섀도 복사본 활용](../volume-shadow-copy-analysis.md) 에 있습니다.
- **`cipher /w` 를 쓴 흔적**: 사용자가 빈 공간을 지웠다면 지운 파일 복구가 어려워집니다. 증거를 없애려 했는지는 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) 에서 함께 판단합니다.

보고서 문장 예:

- "MFT 레코드 N 의 `$STANDARD_INFORMATION` 파일 속성 플래그에 0x4000(암호화)이 켜져 있고, 이름이 `$EFS` 인 로그 유틸리티 스트림 속성이 있다. 이 파일은 EFS 로 암호화된 상태였다."
- "이 파일을 복호할 개인 키를 찾지 못해 내용을 확인하지 못했다."

## 참고 문헌

- Microsoft Learn, *File Encryption* (Win32 apps, 2025-07-08) — https://learn.microsoft.com/en-us/windows/win32/fileio/file-encryption
- Microsoft Learn, *cipher* (Windows Commands) — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cipher
- libyal, *New Technologies File System (NTFS)* (libfsntfs 문서) — https://raw.githubusercontent.com/libyal/libfsntfs/main/documentation/New%20Technologies%20File%20System%20(NTFS).asciidoc
