---
title: "UWP 앱 데이터 구조"
parent: "기반 · 앱·메일 데이터 구조"
nav_order: 470
---

# UWP 앱 데이터 구조 (Packages 폴더·settings.dat)

## 한 줄 요약

스토어 앱처럼 패키지로 설치하는 앱을 패키지 앱 (Packaged App) 이라고 합니다.
패키지 앱은 사용자마다 앱 데이터 저장소를 따로 받으며, Windows 11 에서는 그 저장소가 `%LOCALAPPDATA%\Packages\<패키지 패밀리 이름>` 폴더입니다.
폴더 이름을 나눠 읽으면 앱 이름과 게시자를 가릴 수 있습니다.
앱 설정은 그 안의 `Settings\settings.dat` 에 있습니다. 이 파일은 레지스트리 하이브 형식이고, 값마다 끝에 8바이트 시각이 붙어 있습니다.
앱을 지우면 시스템이 이 저장소를 모두 지웁니다.

공식 문서에는 저장 위치와 파일 형식이 없습니다[1].
이 페이지의 경로·파일 형식·개수는 Windows 11 25H2(빌드 26200) 기준이고, settings.dat 수치는 LOG1·LOG2 로그를 적용하지 않은 사본 75개 기준입니다.
판마다 다를 수 있어 검체에서 확인합니다.

## 이 형식을 쓰는 아티팩트

패키지 앱이 남기는 설정과 파일이 이 구조 위에 쌓입니다. 패키지가 없는 앱은 이 저장소를 쓰지 못하고 파일이나 레지스트리에 직접 씁니다[1].

앱별 해석은 아래 페이지에서 다룹니다. 조사하는 PC 에서 그 앱이 패키지 앱으로 설치됐는지는 폴더 이름과 설치 기록으로 먼저 확인합니다.
  - [Windows 메일 앱](../../02-artifacts/mail/hxstore.md)
  - [스티커 메모](../../02-artifacts/cloud-notes/sticky-notes.md)
  - [휴대폰과 연결](../../02-artifacts/messengers/phone-link.md)
  - [메모장 탭 저장 파일](../../02-artifacts/file-folder-usage/notepad-tabstate.md)
- 설치된 패키지 목록은 [스토어 앱 설치 목록](../../02-artifacts/system-account/appx-staterepository.md) 에서 다룹니다.

## 구조

> 그림 자리: `Packages\<패키지 패밀리 이름>` 폴더 아래 여덟 폴더, 그 가운데 `Settings\settings.dat` 안의 `Test` 루트 키와 `LocalState`·`RoamingState` 키

### 앱 데이터의 종류

앱 데이터는 앱이 만들고 관리하는 데이터이며 내용이 계속 바뀝니다. 실행 상태, 앱 설정, 사용자 선호, 참고 자료(사전 앱의 뜻풀이 등)가 여기에 들어갑니다[1].
사용자 데이터는 앱 데이터와 따로 봅니다. 문서·미디어 파일, 메일이나 대화 기록, 사용자가 만든 DB 레코드가 사용자 데이터입니다[1].
앱 데이터는 설정 (Settings) 과 파일 (Files) 두 가지이고, 앱을 설치하면 시스템이 사용자마다 설정 저장소와 파일 저장소를 줍니다. 앱 데이터에는 버전을 매길 수 있습니다(`ApplicationData.Version`, `SetVersionAsync`).

이 구분은 뜻을 나눈 것일 뿐이므로, 앱이 사용자 데이터를 실제로 어느 폴더에 두는지는 앱마다 확인합니다.

### 패키지 이름 읽는 법

패키지 식별자 (Package Identity) 는 다섯 부분입니다[3].

| 부분 | 내용 | 길이·값 |
|---|---|---|
| Name | 패키지 이름 | 3~50자 |
| Version | 패키지 버전 | — |
| Architecture | 대상 아키텍처 | `neutral`, `x86`, `x64`, `arm`, `arm64`, `x86a64` |
| ResourceId | 리소스 구분 | 0~30자. 번들은 늘 `~` |
| Publisher | 서명 인증서의 주체 이름 | 이름 안에는 게시자 ID 로 들어갑니다 |

이름은 두 가지 꼴로 씁니다[3].

| 이름 | 형식 | 문서의 예 |
|---|---|---|
| 패키지 전체 이름 (Package Full Name) | `<Name>_<Version>_<Architecture>_<ResourceId>_<PublisherId>` | `Microsoft.Windows.Photos_2020.20090.1002.0_x64__8wekyb3d8bbwe` |
| 패키지 패밀리 이름 (Package Family Name) | `<Name>_<PublisherId>` | `Microsoft.Windows.Photos_8wekyb3d8bbwe` |

전체 이름의 예에서는 ResourceId 가 비어 있어서 밑줄이 두 개 이어집니다. 패밀리 이름에는 버전, 아키텍처, ResourceId 가 없습니다.

게시자 ID (PublisherId) 는 Publisher 에서 만든 13자 문자열이고, Crockford 방식 Base32 글자를 쓰며 I·L·O·U 는 쓰지 않습니다. `8wekyb3d8bbwe` 는 Microsoft 의 게시자 ID 입니다[3].
Publisher 만 대소문자를 가리고, 나머지(Name, ResourceId, 게시자 ID, 전체 이름, 패밀리 이름)는 가리지 않습니다.

데이터와 보안은 보통 패키지 패밀리 단위로 묶입니다. 앱 버전이 올라가도 설정을 이어 쓰게 하려는 것입니다[3].
앱 식별자 (AUMID) 는 패키지 패밀리 이름과 매니페스트의 앱 ID 로 만듭니다.
패키지 하나에는 앱이 0~100개 들어갈 수 있으며, 프레임워크 패키지와 리소스 패키지는 앱을 선언할 수 없습니다.

### 관련 위치

| 위치 | 하위 이름의 꼴 | 내용 |
|---|---|---|
| `%LOCALAPPDATA%\Packages\` | 패키지 패밀리 이름 (예: `Microsoft.Paint_8wekyb3d8bbwe`) | 사용자별 앱 데이터. 폴더 138개 |
| `C:\Program Files\WindowsApps\` | 패키지 전체 이름 | 설치 폴더 |
| `HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages` | 패키지 전체 이름 | 하위 키 221개 |
| `C:\ProgramData\Microsoft\Windows\AppRepository\` | `StateRepository-Machine.srd`, `StateRepository-Deployment.srd` | 앞 16바이트가 `SQLite format 3` 인 파일. `-wal`·`-shm` 파일이 함께 있었습니다 |

번들 설치 폴더는 ResourceId 자리에 `~` 가 있었고 꼴은 `<Name>_<Version>_neutral_~_<PublisherId>` 였습니다. 리소스 패키지 설치 폴더는 그 자리에 `split.language-ko` 가 있었습니다.
Repository 키 아래 값의 예는 아래와 같습니다.

| 값 이름 | 형식 | 내용 |
|---|---|---|
| `PackageRootFolder` | REG_SZ | 설치 폴더 전체 경로 |
| `PackageID` | — | 패키지 ID |
| `DisplayName` | — | `ms-resource:` 꼴 문자열 |
| `PackageSid` | REG_BINARY | 패키지 SID |
| `OSMinVersion`, `OSMaxVersionTested` | REG_QWORD | OS 버전 값 |

- StateRepository 파일로 설치 기록을 읽는 법은 [스토어 앱 설치 목록](../../02-artifacts/system-account/appx-staterepository.md) 에서 다룹니다.
- 디스크 이미지에서 `HKCU\Software\Classes` 를 어느 하이브 파일에서 읽는지는 [레지스트리 하이브 구조](../database-log-formats/registry-hive/index.md) 를 봅니다.

### 패키지 폴더 안

폴더 138개 모두에 `AC` 폴더가 있습니다. 86개에는 여덟 폴더가 모두 있고(`AC`, `AppData`, `LocalCache`, `LocalState`, `RoamingState`, `Settings`, `SystemAppData`, `TempState`), 나머지 52개에는 `AC` 폴더만 있습니다.
`AC` 만 있는 폴더는 `Microsoft.UI.Xaml.2.8`, `Microsoft.NET.Native.Framework.2.2`, `Microsoft.Ink.Handwriting.ko-KR.1.0` 처럼 프레임워크나 언어 팩으로 보이는 패키지입니다.

앱 데이터 API 는 저장소마다 시스템이 정한 루트 폴더를 줍니다[1].
아래 표의 "비슷한 이름의 API 저장소" 는 이름이 닮아서 짝지은 것이며, 폴더와 API 저장소가 짝이라는 공식 설명은 없습니다.

| 폴더 | 비슷한 이름의 API 저장소 | 문서가 밝힌 성격 |
|---|---|---|
| `LocalState` | LocalFolder | 로컬 파일. 일반적인 크기 제한이 없습니다 |
| `RoamingState` | RoamingFolder | 로밍 파일. Windows 11 부터 로밍 데이터·설정을 지원하지 않습니다 |
| `TempState` | TemporaryFolder | 캐시처럼 동작합니다. 시스템 유지 관리 작업이 언제든 지울 수 있고, 사용자가 디스크 정리로 지울 수도 있습니다 |
| `LocalCache` | LocalCacheFolder | 백업·복원에 들어가지 않는 파일을 둡니다 |
| `Settings` | LocalSettings·RoamingSettings | 설정 값. 아래 settings.dat 를 봅니다 |
| `AC`, `AppData`, `SystemAppData` | — | 공개 자료 없음 |

`Settings` 폴더 안에는 아래 파일이 있습니다.

| 파일 | 개수 | 비고 |
|---|---|---|
| `settings.dat` | 86 | 설정 하이브 |
| `roaming.lock` | 86 | 모두 0바이트 |
| `settings.dat.LOG1`, `settings.dat.LOG2` | 65 | 하이브 트랜잭션 로그 |

### settings.dat 의 뼈대

settings.dat 는 일반 레지스트리 하이브 형식이어서 앞 4바이트가 `regf` 였고, 형식 버전은 75개 모두 1.3, 루트 셀 위치는 0x20, 파일 크기는 8KB 에서 128KB 사이였습니다.
기본 블록의 파일 이름 칸에는 경로 끝부분(`…\Settings\settings.dat`)이 UTF-16 으로 들어 있었습니다.
regf·hbin·셀의 배치는 [레지스트리 하이브 구조](../database-log-formats/registry-hive/index.md) 에서 다룹니다.

키 트리는 아래 꼴이었습니다.

```
Test                        ← 루트 키. 75개 모두 이 이름
├─ LocalState               ← 값과 하위 키(컨테이너)
│   └─ Exp\{GUID}\Values\…  ← 여러 단계 컨테이너가 있는 파일의 예
└─ RoamingState             ← 75개 모두 값이 없었음
```

설정은 컨테이너 (ApplicationDataContainer) 로 묶을 수 있고, 컨테이너는 32단계까지 겹칠 수 있습니다[1].
`LocalState` 키는 LocalSettings 와, `RoamingState` 키는 RoamingSettings 와 짝으로 보이지만 이름으로 한 짐작이며, 공식 설명은 없습니다.
두 파일의 루트 키에는 일반 레지스트리 형식 값도 있었습니다. 이름은 `Version`, 형식은 REG_DWORD(4) 였습니다.

### 값 형식 번호

값 (vk) 의 형식 칸에는 REG_SZ 같은 일반 번호가 아니라 `0x05F5E1xx` 꼴 수가 있었습니다. `0x05F5E100` 은 10진수로 100,000,000 이고, 형식 칸에서 이 수를 빼면 `Windows.Foundation.PropertyType` 번호와 맞아떨어졌습니다.
값 데이터는 실제 값 뒤에 8바이트가 더 붙은 꼴이었습니다.

| 형식 칸 | 뺀 나머지 | PropertyType | 데이터 크기(바이트) | 개수 |
|---|---|---|---|---|
| `0x05F5E103` | 3 | UInt16 | 10 (2 + 8) | 4 |
| `0x05F5E104` | 4 | Int32 | 12 (4 + 8) | 266 |
| `0x05F5E105` | 5 | UInt32 | 12 (4 + 8) | 120 |
| `0x05F5E106` | 6 | Int64 | 16 (8 + 8) | 27 |
| `0x05F5E107` | 7 | UInt64 | 16 (8 + 8) | 53 |
| `0x05F5E109` | 9 | Double | 16 (8 + 8) | 6 |
| `0x05F5E10B` | 11 | Boolean | 9 (1 + 8) | 301 |
| `0x05F5E10C` | 12 | String | UTF-16LE 글자 + NUL 2 + 8 | 248 |
| `0x05F5E10D` | 13 | Inspectable (합성 값) | 항목에 따라 다름 | 203 |
| `0x05F5E10E` | 14 | DateTime | 16 (8 + 8) | 8 |
| `0x05F5E110` | 16 | Guid | 24 (16 + 8) | 3 |

PropertyType 에는 위 표에 없는 번호도 있습니다[2]. Empty 0, UInt8 1, Int16 2, Single 8, Char16 10, TimeSpan 15, Point 17, Size 18, Rect 19, OtherType 20 입니다. 배열 형식은 1025 (UInt8Array) 부터 1044 (OtherTypeArray) 까지입니다. 이 번호들이 settings.dat 에 어떤 꼴로 들어가는지는 검체에서 확인합니다.

설정 값에 쓸 수 있는 형식은 UInt8, Int16, UInt16, Int32, UInt32, Int64, UInt64, Single, Double, Boolean, Char16, String, DateTime, TimeSpan, GUID, Point, Size, Rect, 합성 값 (ApplicationDataCompositeValue) 입니다[1].

### 값 끝의 8바이트 시각

끝 8바이트를 FILETIME(1601-01-01 부터 센 100ns 단위, UTC)으로 풀면 날짜가 맞게 나왔고, 이 시각은 값마다 달랐습니다. 값을 마지막으로 쓴 시각으로 보이지만 공식 설명은 없습니다.
String 값은 UTF-16LE 글자와 끝 NUL 2바이트 뒤에 이 8바이트가 붙어 있었습니다.
DateTime 값 4건은 값 자체도 FILETIME 으로 풀렸고, 값과 끝 시각의 차이는 몇 밀리초 안이었습니다.
값 1,239개 가운데 1,234개는 끝 시각이 그 키의 마지막 기록 시각보다 늦지 않았지만, 나머지 5개는 키 시각보다 늦었습니다. 로그를 적용하지 않은 사본 기준입니다.

### 합성 값의 예

104바이트짜리 합성 값의 예입니다. 항목 이름은 A·R·G·B 넷이고, 항목마다 아래 칸이 차례로 이어집니다.

| 칸 | 크기 | 이 예의 값 |
|---|---|---|
| 항목 크기 | 4바이트 | 17 |
| 형식 (PropertyType 번호) | 4바이트 | 1 (UInt8) |
| 이름 길이 | 4바이트 | 1 (`A` 한 글자) |
| 이름 | UTF-16 글자 + NUL | `A` |
| 값 | 형식에 따른 크기 | 1바이트 |

항목 크기 17 은 4 + 4 + 4 + 4 + 1 로, 크기 칸 자신도 셉니다.
항목은 8바이트 경계에 맞춰 이어져서 17바이트 항목 하나가 24바이트 자리를 쓰고, 맨 끝에 8바이트 시각이 있었습니다. 4 × 24 + 8 = 104 로 전체 크기와 맞습니다.
다른 형식이 섞인 합성 값도 같은 꼴인지는 검체에서 확인합니다.
합성 값은 한꺼번에 저장하고 읽어야 하는 설정 묶음이며, 적은 양에 맞춘 형식입니다[1].

### 값 이름

값 이름은 앱마다 다릅니다.

| 앱 | 값 이름의 예 |
|---|---|
| 메모장 (`LocalState`) | `RecentFilesFirstLoad`, `WebAccountId`, `FirstSignIn` |
| 사진 | `LAST_CLOSED_VIEWER_WINDOW_PLACEMENT`, `LifetimeSessionNumber` |
| 계산기 | `Mode` |

값의 뜻은 이름으로만 짐작할 수 있으므로, 앱마다 동작을 바꿔 가며 확인한 뒤에 보고서에 씁니다.

## 읽는 법

1. **폴더와 로그를 함께 수집합니다.** `settings.dat`, `settings.dat.LOG1`, `settings.dat.LOG2` 를 한 벌로 가져옵니다. 실행 중인 앱의 파일은 잠겨 있을 수 있습니다. 아래 "라이브 수집" 을 봅니다.
2. **폴더 이름을 나눕니다.** 패밀리 이름은 마지막 밑줄 뒤 13자가 게시자 ID 이고, 그 앞이 Name 입니다.
3. **설치 기록과 짝짓습니다.** 설치 폴더 이름과 Repository 키 이름은 전체 이름입니다. 여기서 버전과 아키텍처를 읽습니다.
4. **하이브로 엽니다.** 하이브 도구나 헥스 편집기로 `Test\LocalState` 아래를 봅니다. 로그를 적용했는지 결과에 적어 둡니다.
5. **형식 번호를 풉니다.** 형식 칸이 `0x05F5E1xx` 꼴이면 `0x05F5E100` 을 뺍니다. 남은 수를 위 표의 PropertyType 으로 읽습니다.
6. **끝 8바이트를 떼어 냅니다.** 앞부분은 값으로 읽고, 끝 8바이트는 FILETIME 으로 풉니다. 푸는 법은 [시각 값 형식](../value-decoding/filetime-unix-webkit-dos-ole.md) 을 봅니다.
7. **합성 값은 항목 단위로 풉니다.** 크기 칸을 따라가며 8바이트 경계마다 다음 항목을 읽습니다.
8. **폴더 안 파일도 봅니다.** `LocalState` 같은 폴더 안 파일의 형식은 앱마다 따로 확인합니다.

### 헥스로 한 번 따라가기

아래 바이트는 위 규칙대로 만든 예시이며 실제 파일에서 옮긴 바이트가 아닙니다. `vv` 는 값 자리, `tt` 는 끝 시각 8바이트 자리입니다.

**vk 셀의 형식 칸 (4바이트, 리틀 엔디언)**

```
0B E1 F5 05
```

- 뒤집어 읽으면 `0x05F5E10B` 입니다.
- `0x05F5E10B` − `0x05F5E100` = `0x0B` = 11 입니다.
- 11 은 PropertyType 의 Boolean 입니다.

**Boolean 값의 데이터 (9바이트)**

```
오프셋  00 01 02 03 04 05 06 07 08
0000    vv tt tt tt tt tt tt tt tt
```

- 0x00 한 바이트가 값입니다.
- 0x01 부터 8바이트가 끝 시각입니다.

**String 값 `ab` 의 데이터 (14바이트)**

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D
0000    61 00 62 00 00 00 tt tt tt tt tt tt tt tt   a.b.....
```

- 0x00~0x03 은 UTF-16LE 로 `ab` 입니다.
- 0x04~0x05 는 끝 NUL 입니다.
- 0x06 부터 8바이트가 끝 시각입니다.
- 글자 인코딩은 [문자 인코딩](../value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.

## 포렌식에서 중요한 점

### 앱을 지우면 저장소도 사라집니다

앱을 지우면 시스템이 이 저장소의 내용을 모두 지웁니다[1]. 그래서 앱을 지운 PC 에는 그 앱의 폴더가 없을 수 있습니다.
지운 폴더와 파일은 파일 시스템 수준에서 찾습니다. [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 와 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 을 봅니다.

앱을 업데이트할 때는 시스템이 대체로 내용을 남기지만, RoamingSettings 는 스토어 업데이트 때 남지 않을 수 있고, Windows 10 에서도 그렇습니다[1].
임시 저장소는 시스템이 언제든 지울 수 있으므로, 비어 있다고 앱을 쓰지 않았다고 단정하지 않습니다.

### Windows 버전별 차이

| 항목 | Windows 10 | Windows 11 |
|---|---|---|
| 로밍 데이터·설정 | 문서가 지원 중단을 밝히지 않은 버전입니다. 스토어 업데이트 때 RoamingSettings 가 남지 않을 수 있습니다 | 지원하지 않습니다[1] |
| settings.dat 의 `RoamingState` 키 | 검체에서 확인 | 25H2(빌드 26200) 에서 75개 모두 값 없음 |

### 비정상 종료와 LOG1·LOG2

settings.dat 옆에는 LOG1·LOG2 가 있는 경우가 많습니다(86개 가운데 65개). 로그를 적용하지 않은 사본에서는 값 끝 시각이 키 시각보다 늦은 값이 있습니다(5개). 그래서 로그를 함께 수집하고, 적용했는지 결과에 적습니다.
로그를 다루는 법은 [레지스트리 하이브 구조](../database-log-formats/registry-hive/index.md) 에서 다룹니다.

### 지운 키와 값

settings.dat 는 일반 하이브 형식이어서 하이브에서 지운 키·값을 찾는 방법을 그대로 써 볼 수 있습니다. 다만 settings.dat 에서 되살린 결과는 따로 검증합니다.

### 시각

- 키 마지막 기록 시각이 2012-05-22 00:00 UTC 인 키가 많습니다.
  - 루트 키: 75개 가운데 73개
  - `RoamingState`: 75개 모두
  - `LocalState`: 75개 가운데 53개
- 빈 틀 파일에 박힌 시각으로 보이며, 앱을 설치하거나 쓴 시각이 아닙니다.
- 값 끝 시각은 값마다 따로 있고 공식 설명이 없으므로, 보고서에는 "이 값의 끝 8바이트를 FILETIME 으로 풀면 이 시각이 나온다" 까지만 씁니다.
- 키 시각을 값 시각의 상한으로 쓰지 않습니다. 키 시각보다 늦은 값도 있습니다(1,239개 가운데 5개).
- 키 시각의 일반 해석은 [레지스트리 하이브 구조](../database-log-formats/registry-hive/index.md) 를 봅니다.

### 설정 파일 속 비밀 값

앱에 따라 settings.dat 에 PEM 꼴 개인 키 문자열이 String 값으로 들어 있습니다. 한 예로 값 이름이 `CertificateHelper_PrivateKey` 인 값이 있습니다.
설정 파일에 비밀 값이 평문으로 있을 수 있으므로 결과를 넘길 때 값 내용을 가립니다.

### 라이브 수집

실행 중인 앱의 settings.dat 는 잠겨서 복사되지 않을 수 있습니다. 86개 가운데 11개에서 "Device or resource busy" 가 납니다.
볼륨 섀도 복사본이나 원시 디스크 읽기로 가져옵니다. [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) 과 [볼륨 섀도 복사본 구조](../disk-volume/volume-shadow-copy.md) 를 봅니다.

## 함정

- **폴더 수를 설치 앱 수로 셉니다.** 폴더 138개 가운데 52개는 `AC` 만 있는 프레임워크·언어 팩 성격이었습니다.
- **폴더 수와 Repository 키 수를 바로 비교합니다.** 폴더 이름은 패밀리 이름이고, 키 이름은 전체 이름입니다. 폴더 138개에 키 221개처럼 수가 다릅니다.
- **폴더 이름에서 버전을 찾습니다.** 패밀리 이름에는 버전이 없습니다. 버전은 설치 폴더나 Repository 키 이름에서 봅니다.
- **게시자 ID 를 게시자 이름으로 적습니다.** 게시자 ID 는 서명 인증서의 주체 이름에서 만든 13자 값입니다. 게시자 이름은 설치 기록의 Publisher 와 짝지어 적습니다.
- **`RoamingState` 가 비어 있어 이상하다고 봅니다.** Windows 11 은 로밍을 지원하지 않습니다. 25H2 에서는 75개 모두 값이 없습니다.
- **2012-05-22 키 시각을 앱 사용 시각으로 봅니다.** 빈 틀 파일의 시각으로 보입니다.
- **도구가 보여 준 형식을 그대로 믿습니다.** 형식 칸이 `0x05F5E1xx` 꼴이면 일반 레지스트리 형식이 아닙니다. 이 번호를 보여 주는 방식은 도구마다 다를 수 있습니다. 헥스로 형식 칸과 데이터 크기를 확인합니다.
- **끝 8바이트까지 값으로 읽습니다.** Int32 값의 데이터 12바이트를 통째로 정수로 읽으면 값이 틀립니다. String 은 NUL 뒤 8바이트를 떼어 냅니다.
- **경로가 늘 같다고 봅니다.** 공식 문서에는 위치가 없습니다[1]. 다른 Windows 버전에서는 폴더를 직접 확인합니다.

## 도구

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| 헥스 편집기 | 형식 칸, 끝 8바이트, 합성 값 항목을 직접 봅니다 |
| 레지스트리 하이브 도구 (Registry Explorer, regipy 등) | 키 트리와 값 목록을 봅니다. 형식 번호와 끝 시각은 직접 풀어 대조합니다 |
| SQLite 조회 도구 | StateRepository 파일을 엽니다. 형식은 [SQLite 데이터베이스](../database-log-formats/sqlite/index.md) 에서 다룹니다 |

도구마다 결과가 다르면 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 참고 문헌

1. Microsoft Learn, *Store and retrieve settings and other app data* (2026-04-08) — https://learn.microsoft.com/en-us/windows/apps/develop/data/store-and-retrieve-app-data
2. Microsoft Learn, *PropertyType Enum (Windows.Foundation)* — https://learn.microsoft.com/en-us/uwp/api/windows.foundation.propertytype
3. Microsoft Learn, *An overview of Package Identity in Windows apps* (2026-07-09) — https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/package-identity-overview
