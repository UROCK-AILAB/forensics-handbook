---
title: "구조와 ID 매핑"
parent: "SRUM"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 980
---

# 구조와 ID 매핑 (SruDbIdMapTable)

> 위치: [SRUM (System Resource Usage Monitor)](index.md) > 구조와 ID 매핑

## 한 줄 요약

SRUM 데이터베이스(SRUDB.dat)의 기록 표에는 프로그램 경로와 사용자 SID 가 글자로 들어 있지 않고 번호만 있습니다.
그 번호가 가리키는 이름은 ID 매핑 표 (SruDbIdMapTable) 에 따로 있어서 이 표를 먼저 풀어야 "어느 프로그램이, 어느 계정으로" 를 읽을 수 있습니다.

## 무엇을 기록하나

SRUM 은 기능별 제공자 (Provider) 마다 자원 사용 기록을 따로 모으고, 제공자마다 표가 하나씩 있으며 표 이름은 제공자의 GUID 입니다. 이 표들에는 모두 AppId 열과 UserId 열이 있고, 두 열에는 32비트 정수만 들어 있습니다. 이 정수는 SruDbIdMapTable 의 IdIndex 값을 가리킵니다.

SruDbIdMapTable 의 한 행에는 번호 하나와 이름 하나가 짝지어 있습니다. 이름은 실행 파일 경로일 수도 있고 SID 일 수도 있습니다.

각 기록 표의 수치 열은 형제 페이지에서 다루고, 이 페이지는 번호를 이름으로 바꾸는 과정만 다룹니다.

## 위치와 버전별 차이

| 항목 | 위치·값 |
|---|---|
| 데이터베이스 파일 | `C:\Windows\System32\sru\SRUDB.dat` |
| 파일 형식 | ESE 데이터베이스. 형식은 [ESE 데이터베이스 (Extensible Storage Engine)](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에 있습니다 |
| 트랜잭션 로그 | 같은 `sru` 폴더. 공개 파서 안내문의 복구 명령(`esentutl /r sru`)이 로그 기본 이름으로 `sru` 를 씁니다 |
| 제공자 목록 | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SRUM\Extensions` 아래의 GUID 키 |

libyal 명세가 적은 제공자와 표는 아래와 같습니다.

| 표 이름 (GUID) | 제공자 DLL | 명세의 이름 | 이 위키 페이지 |
|---|---|---|---|
| `{D10CA2FE-6FCF-4F6D-848E-B2E99266FA89}` | appsruprov.dll | Application Resource Usage Provider | [앱별 자원 사용](application-resource-usage.md) |
| `{973F5D5C-1D90-4944-BE8E-24B94231A174}` | nduprov.dll | Network Data Usage Monitor | [네트워크 사용량](network-data-usage.md) |
| `{DD6636C4-8929-4683-974E-22C046A43763}` | ncuprov.dll | Network Connectivity Usage Monitor | [네트워크 연결 기록](network-connectivity.md) |
| `{FEE4E14F-02A9-4550-B5CE-5FA2DA202E37}`, 이름 끝에 `LT` 가 붙은 같은 GUID 표 | energyprov.dll | Energy Usage Provider | [전원·배터리 사용](energy-usage.md) |
| `{D10CA2FE-6FCF-4F6D-848E-B2E99266FA86}` | wpnsruprov.dll | Push Notifications (WPN) Provider | — |
| `{DA73FB89-2BEA-4DDC-86B8-6E048C6DA477}` | eeprov.dll | 뜻 모름 (Energy Estimator 로 추정) | — |
| `{5C8CF1C7-7257-4F13-B223-970EF5939312}` | eeprov.dll | 뜻 모름 (Energy Estimator 로 추정) | — |

- libyal 명세는 레지스트리 경로를 `WindowsNT` 로 붙여 적었습니다. 실제 키 이름은 `Windows NT` 입니다.
- srum-dump 는 `{5C8CF1C7-…}` 표를 "Application Timeline" 이라고 부릅니다.
- 공개 파서 가운데에는 명세에 없는 표(`{7ACBBAA3-D029-4BE4-9A7A-0885927F1D8F}`)를 읽는 것도 있습니다.
- 그래서 표 구성은 Extensions 키와 실제 DB 의 표 목록을 둘 다 보고 판단합니다.

버전 차이는 아래 범위까지만 확인했습니다.

| 대상 | 확인 범위 |
|---|---|
| libyal 명세 (개정 0.0.2, 2021년 6월) | Windows 10 으로 확인했습니다. Windows 8 은 "할 일" 로 남아 있습니다 |
| SruDbIdMapTable 열 배치 | 버전마다 다르다는 공개 자료를 찾지 못했습니다 |
| 공개 파서 (plaso, srum-dump, SrumECmd 라이브러리) | 셋 다 Windows 버전을 가리지 않고 같은 코드로 이 표를 읽습니다 |

## 구조

> 그림 자리: 앱별 자원 사용 표의 한 행(AppId 42, UserId 7) → SruDbIdMapTable 의 IdIndex 42 행(IdType 0, 실행 파일 경로)과 IdIndex 7 행(IdType 3, SID) → SOFTWARE 하이브 ProfileList 의 프로필 폴더로 이어지는 연결도

### SRUDB.dat 안의 표

| 표 | 하는 일 |
|---|---|
| `MSysObjects` 처럼 `MSys` 로 시작하는 표 | ESE 가 스스로 쓰는 카탈로그 표입니다. [파일 구조 (Page·B+Tree·Catalog)](../../../01-foundations/database-log-formats/extensible-storage-engine/page-b-tree-catalog.md) 에 있습니다 |
| `SruDbIdMapTable` | 번호와 이름의 짝을 담습니다 |
| `SruDbCheckpointTable` | 명세에는 열 이름(ProviderId·CheckpointId·NextIncId·SeqNumber·RecordSet)만 있고 뜻은 적혀 있지 않습니다 |
| `{GUID}` 표 | 제공자별 기록입니다 |
| `{GUID}LT` 표 | 명세는 장기 (long-term) 기록이라고 설명합니다 |

### SruDbIdMapTable 의 열

| 열 번호 | 열 이름 | 형식 | 뜻 |
|---|---|---|---|
| 1 | IdType | 8비트 부호 없는 정수 | IdBlob 의 종류 |
| 2 | IdIndex | 32비트 부호 있는 정수 | 기록 표의 AppId·UserId 가 가리키는 번호 |
| 256 | IdBlob | 긴 이진 데이터 (Large Binary) | 이름 본문. 내용은 IdType 에 따라 다릅니다 |

- 이 표에는 시각 열이 없습니다.
- IdBlob 은 긴 이진 형식입니다. 이 형식의 값은 크면 레코드 밖의 긴 값 (Long Value) 으로 따로 저장될 수 있습니다. 저장 방식은 [긴 값과 압축 열](../../../01-foundations/database-log-formats/extensible-storage-engine/long-value-compressed-column.md) 에 있습니다.
- 열 번호가 고정·가변·태그 열 가운데 무엇인지 가리는 규칙은 [파일 구조 (Page·B+Tree·Catalog)](../../../01-foundations/database-log-formats/extensible-storage-engine/page-b-tree-catalog.md) 에 있습니다.

### IdType 값

| IdType | libyal 명세 | SrumECmd 라이브러리의 이름 | IdBlob 내용 |
|---|---|---|---|
| 0 | 뜻 모름. UTF-16 문자열 | NormalApp (일반 프로그램) | 실행 파일 경로. `\Device\HarddiskVolume번호\…` 꼴과 `!!` 로 시작하는 꼴이 있습니다 |
| 1 | 뜻 모름. UTF-16 문자열 | Service (서비스) | UTF-16 문자열 |
| 2 | 뜻 모름. UTF-16 문자열 | ModernApp (스토어 앱) | UTF-16 문자열 |
| 3 | 사용자 식별자 (UserId) | Sid | 이진 SID |

- 명세는 0·1·2 의 뜻을 아직 정하지 않았습니다.
- "일반 프로그램·서비스·스토어 앱" 은 공개 파서 한 곳이 붙인 이름입니다.
- IdType 0 이 실행 파일 경로라는 점은 Autopsy 의 SRUM 모듈 코드에서도 보입니다.
- 이 코드는 IdType 0 행에서 `\Device\HarddiskVolume` 앞머리를 떼어 프로그램 이름을 만들고, `!!` 로 시작하는 IdType 0 행은 따로 뺍니다.
- 문자열은 UTF-16LE 입니다. 공개 파서들은 끝에 붙은 0 을 잘라 냅니다. 인코딩은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에 있습니다.
- IdType 3 의 IdBlob 은 Windows 의 이진 SID 이며, 개정 번호 1바이트, 하위 권한 개수 1바이트, 식별 기관 6바이트, 하위 권한 4바이트씩으로 이어집니다.
- 공개 파서는 식별 기관을 큰 엔디언으로, 하위 권한을 리틀 엔디언으로 읽습니다. 자세한 구조는 [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에 있습니다.

### `!!` 로 시작하는 IdBlob

srum-dump 문서에는 아래 예가 실려 있습니다.

```
!!svchost.exe!1972/12/14:16:22:50!1c364![LocalService] [nsi]
```

- SrumECmd 라이브러리는 앞의 `!!` 를 떼고 나머지를 `!` 로 나눈 뒤, 뒤에서 세 조각을 차례로 시각, 뜻 모를 칸, 설명으로 읽습니다.
- 그 앞의 조각은 모두 파일 이름으로 다시 잇는데, 파일 이름 안에 `!` 가 있어도 되게 한 처리입니다.
- 시각 조각은 `yyyy/MM/dd:HH:mm:ss` 꼴로 읽고 UTC 로 보지만, 이 꼴의 뜻을 설명한 명세나 Microsoft 문서는 없습니다.
- 위 예의 시각은 1972년입니다. 그래서 이 칸을 실행 시각으로 읽을 수 없습니다.
- 위 예의 마지막 칸은 svchost 서비스 그룹 이름과 서비스 이름처럼 보입니다. 이 해석을 확인한 자료는 없습니다.

### 기록 표와 잇는 법

```
기록 표.AppId  = SruDbIdMapTable.IdIndex   → 이 행의 IdType 은 0·1·2 여야 합니다
기록 표.UserId = SruDbIdMapTable.IdIndex   → 이 행의 IdType 은 3 이어야 합니다
```

- 기록 표에는 공통으로 AutoIncId·TimeStamp·AppId·UserId 열이 있습니다.
- srum-dump 는 매핑 표의 모든 행을 IdIndex 하나로 찾는 사전 하나에 넣습니다.
- SrumECmd 라이브러리는 IdType 3 행과 나머지 행을 두 사전에 나눠 넣습니다.
- srum-dump 문서의 예에서는 IdIndex 3 이 프로그램이고 4 가 SID(S-1-5-19) 입니다.
- 두 방식이 같은 결과를 내려면 IdIndex 가 종류와 상관없이 겹치지 않아야 합니다. 명세에는 이 점이 적혀 있지 않습니다.
- SID 를 계정과 잇는 일은 이 표 밖에서 합니다. 같은 PC 의 SOFTWARE 하이브 `Microsoft\Windows NT\CurrentVersion\ProfileList\<SID>` 의 ProfileImagePath 를 봅니다. 자세한 내용은 [사용자 프로필 목록 (ProfileList)](../../system-account/profilelist.md) 에 있습니다.
- 네트워크 표의 L2ProfileId 는 이 표로 풀지 않습니다. 공개 파서는 SOFTWARE 하이브 `Microsoft\WlanSvc\Interfaces\…\Profiles` 의 ProfileIndex 로 풉니다. [네트워크 사용량](network-data-usage.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것**

- 매핑 행이 있으면 SRUM 이 그 이름에 번호를 붙인 적이 있습니다.
- 기록 표의 행이 그 번호를 가리키면 그 행의 수치는 그 이름에 딸린 기록입니다.
- IdType 0 의 경로는 SRUM 이 기록한 실행 파일의 볼륨 장치와 경로를 보여 줍니다.
- IdType 3 의 SID 는 기록이 어느 보안 주체 이름으로 쌓였는지 보여 줍니다.

**증명하지 못하는 것**

- 매핑 행만으로는 그 이름이 언제 쓰였는지 모릅니다. 이 표에는 시각 열이 없습니다.
- 매핑 행만으로 실행이나 사용량을 말하지 않습니다. 그 판단은 기록 표의 행으로 합니다.
- 매핑 표에는 해시·크기 같은 파일 식별 정보가 없습니다. 그래서 그 경로에 있던 파일이 지금 디스크의 파일과 같은지는 이 표로 말할 수 없습니다.
- SID 는 계정을 가리킵니다. 그 계정을 쓴 사람이 누구인지는 가리키지 않습니다.
- 매핑 행이 언제 지워지는지는 공개 자료에서 확인하지 못했습니다. 그래서 기록 표가 가리키지 않는 매핑 행의 뜻을 단정하지 않습니다.
- IdType 0·1·2 의 구분은 명세가 아니라 파서의 해석입니다.

보고서에는 번호와 풀이를 함께 적습니다.
예: "SRUDB.dat 의 앱별 자원 사용 표에 AppId 42 를 가리키는 행이 있습니다. 매핑 표에서 IdIndex 42 는 IdType 0 이고 값은 `\Device\HarddiskVolume3\…\x.exe` 입니다." (번호와 경로는 설명용 예시입니다.)

## 시각 해석

- SruDbIdMapTable 에는 시각 열이 없고, 시각은 기록 표에 있습니다.
- 기록 표의 TimeStamp 는 OLE 자동화 날짜 (OLE Automation Date) 입니다. srum-dump 는 이 값을 UTC 로 봅니다.
- 네트워크 연결 기록 표의 ConnectStartTime 은 FILETIME 입니다.
- 두 형식을 푸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- TimeStamp 가 실제 사용 시각과 어떻게 어긋나는지는 [SRUM 해석 함정](1.md) 에서 다룹니다.
- `!!` 행 안의 시각 문자열은 뜻이 확인되지 않았습니다. 타임라인에 넣을 때는 실행 시각과 섞지 않고 따로 표시합니다.

## 함정과 한계

1. **IdType 0·1·2 의 이름은 명세에 없습니다.** 파서마다 부르는 이름이 다를 수 있습니다. 보고서에는 IdType 숫자를 함께 적습니다.
2. **매핑을 못 찾은 번호를 도구마다 다르게 다룹니다.** srum-dump 는 빈칸으로 둡니다. SrumECmd 라이브러리(`Srum.cs`, 2022년 11월 코드)는 번호를 확인하지 않고 사전에서 바로 꺼냅니다. 번호가 없으면 예외가 납니다. 그러면 그 표의 나머지 행은 처리하지 않고 경고만 남깁니다. 결과 행 수와 경고 기록을 확인하고, 다른 도구와 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 에 있습니다.
3. **모르는 IdType 을 다루는 방식도 다릅니다.** plaso 는 0~3 밖의 값을 만나면 경고를 냅니다. SrumECmd 라이브러리는 0~3 밖의 값을 알리지 않고 건너뜁니다. 매핑 표의 IdType 별 행 수를 직접 세어 둡니다.
4. **종류가 맞는지 확인합니다.** AppId 를 풀었는데 SID 가 나오거나, UserId 를 풀었는데 경로가 나오면 매핑을 잘못 읽은 것입니다.
5. **볼륨 번호는 드라이브 문자가 아닙니다.** `HarddiskVolume3` 은 Windows 가 볼륨 장치에 붙인 번호입니다. 이 표만으로는 이 번호가 어느 드라이브 문자인지 정할 수 없습니다. 드라이브 문자로 경로를 적는 다른 아티팩트와 맞춰 봅니다. 번호가 시스템 볼륨과 다르면 다른 볼륨에서 실행한 흔적일 수 있습니다. 경로를 비교할 때는 대소문자를 무시합니다.
6. **비정상 종료 상태가 흔합니다.** 압수 이미지에서 꺼낸 SRUDB.dat 는 대부분 비정상 종료 (Dirty Shutdown) 상태였습니다. 이미지 안의 로그 사슬이 끊겨 로그로 복구하지 못한 경우도 있었습니다(관찰). 복구하면 파일이 바뀌므로 항상 사본에서 작업합니다. 자세한 내용은 [트랜잭션 로그와 비정상 종료 상태](../../../01-foundations/database-log-formats/extensible-storage-engine/edb-log-dirty-shutdown.md) 에 있습니다.
7. **손상된 DB 는 읽는 방식마다 결과가 다릅니다.** 같은 손상 SRUDB.dat 의 앱 사용량 표에서 도구마다 행 수가 1,612 와 1,742 로 달랐습니다(관찰). B-트리를 끝까지 못 따라간 쪽이 적게 냈습니다. 매핑 표를 끝까지 못 읽으면 풀리지 않는 번호가 생깁니다. 두 가지 이상 방식으로 열어 매핑 표 행 수부터 비교합니다.
8. **긴 값 경계를 잘못 잡으면 경로가 조용히 망가집니다.** ESE 의 긴 값은 여러 조각으로 나뉘어 저장됩니다. 조각 경계를 잘못 계산한 파서가 오류 없이 크기가 다른 값을 낸 사례가 있습니다(관찰, ESE 일반). 경로 끝이 이상하거나 UTF-16 으로 풀리지 않는 바이트가 섞이면 다른 도구로 다시 읽습니다.
9. **SID 를 계정 이름으로 바꾸려면 같은 PC 의 SOFTWARE 하이브가 필요합니다.** ProfileImagePath 의 폴더 이름은 계정 이름과 다를 수 있습니다. 계정 이름을 바꿔도 프로필 폴더 이름은 그대로이기 때문입니다. 프로필을 지웠으면 ProfileList 에 그 SID 키가 없습니다. 이때는 이름을 짐작하지 말고 SID 그대로 적습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 **명세로 만든 예시**이며 실제 검체에서 나온 값이 아닙니다.
ESE 페이지에서 레코드와 열 값을 꺼내는 과정은 [파일 구조 (Page·B+Tree·Catalog)](../../../01-foundations/database-log-formats/extensible-storage-engine/page-b-tree-catalog.md) 에 있습니다.
여기서는 꺼낸 열 값부터 시작합니다.

**1단계. 기록 표 한 행에서 AppId 와 UserId 를 읽습니다.**

```
앱별 자원 사용 표의 한 행 (명세로 만든 예시)
AppId  열: 2A 00 00 00
UserId 열: 07 00 00 00
```

- 두 값은 32비트 리틀 엔디언 정수입니다.
- AppId 는 0x2A, 곧 42 입니다.
- UserId 는 7 입니다.

**2단계. 매핑 표에서 IdIndex 42 행을 찾습니다.**

```
SruDbIdMapTable, IdIndex 42 행 (명세로 만든 예시)
IdType: 00
IdBlob:
00000000  5C 00 44 00 65 00 76 00  69 00 63 00 65 00 5C 00   \.D.e.v.i.c.e.\.
00000010  48 00 61 00 72 00 64 00  64 00 69 00 73 00 6B 00   H.a.r.d.d.i.s.k.
00000020  56 00 6F 00 6C 00 75 00  6D 00 65 00 33 00 5C 00   V.o.l.u.m.e.3.\.
00000030  57 00 69 00 6E 00 64 00  6F 00 77 00 73 00 5C 00   W.i.n.d.o.w.s.\.
00000040  65 00 78 00 70 00 6C 00  6F 00 72 00 65 00 72 00   e.x.p.l.o.r.e.r.
00000050  2E 00 65 00 78 00 65 00                            ..e.x.e.
```

- IdType 0 이므로 IdBlob 을 UTF-16LE 로 풉니다.
- 값은 `\Device\HarddiskVolume3\Windows\explorer.exe` 입니다.
- 글자마다 2바이트이고 뒤 바이트가 `00` 인 모양이 UTF-16LE 영문의 특징입니다.
- 끝에 `00 00` 이 붙어 있으면 잘라 냅니다.

**3단계. 매핑 표에서 IdIndex 7 행을 찾습니다.**

```
SruDbIdMapTable, IdIndex 7 행 (명세로 만든 예시)
IdType: 03
IdBlob:
00000000  01 01 00 00 00 00 00 05  12 00 00 00               ............
```

- IdType 3 이므로 IdBlob 을 이진 SID 로 풉니다.
- 0x00 의 `01` 은 개정 번호 1 입니다.
- 0x01 의 `01` 은 하위 권한이 1개라는 뜻입니다.
- 0x02~0x07 의 `00 00 00 00 00 05` 는 식별 기관 5 입니다. 큰 엔디언으로 읽습니다.
- 0x08 의 `12 00 00 00` 은 하위 권한 18 입니다. 리틀 엔디언으로 읽습니다.
- 합치면 `S-1-5-18`, 곧 로컬 시스템 (LocalSystem) 입니다.
- 로컬 사용자 SID 라면 둘째 바이트가 `05` 이고, `15 00 00 00`(21) 뒤에 4바이트 값 셋과 RID 가 이어집니다. 예를 들어 RID 1001 은 `E9 03 00 00` 입니다.

**4단계. 풀이를 한 줄로 적습니다.**

- 이 행은 `\Device\HarddiskVolume3\Windows\explorer.exe` 에 딸린 기록입니다.
- 기록은 `S-1-5-18` 이름으로 쌓였습니다.
- ProfileList 에서 `S-1-5-18` 키의 ProfileImagePath 는 시스템 프로필 폴더를 가리킵니다.

### 공개 도구로 한 번

- ESE 를 직접 여는 도구: libyal 의 libesedb(esedbexport), NirSoft 의 ESEDatabaseView.
- SRUM 을 풀어 주는 도구: srum-dump, Eric Zimmerman 의 SrumECmd, plaso 의 SRUM 플러그인.

ESE 를 직접 여는 도구와 SRUM 전용 도구를 하나씩 골라 아래를 맞춰 봅니다.

- SruDbIdMapTable 의 전체 행 수와 IdType 별 행 수
- 같은 IdIndex 에 대해 두 도구가 내는 문자열
- 기록 표에서 이름이 빈칸으로 나온 행 수
- SRUM 전용 도구가 남긴 경고 기록

값이 다르면 위 헥스 절차로 IdBlob 을 직접 풀어 어느 쪽이 맞는지 가립니다.

## 교차 검증

- [사용자 프로필 목록 (ProfileList)](../../system-account/profilelist.md): IdType 3 의 SID 를 프로필 폴더와 잇습니다.
- [사용자 계정 (SAM)](../../system-account/sam.md): 로컬 계정 SID 의 RID 와 계정 이름을 확인합니다.
- [BAM·DAM (Background Activity Moderator)](../background-activity-moderator.md): 같은 `\Device\HarddiskVolume번호\` 꼴 경로로 실행 파일을 적습니다. 경로를 그대로 맞춰 볼 수 있습니다.
- [실행 파일 항목 (InventoryApplicationFile)](../amcache-hve/inventoryapplicationfile.md): 드라이브 문자 경로와 SHA1 이 있습니다. 볼륨 번호를 드라이브 문자와 맞추고, 파일이 같은지 확인할 때 씁니다.
- [Wi-Fi 프로필 (WLAN Profiles)](../../network/wlan-profiles.md): 네트워크 표의 L2ProfileId 를 푸는 데 씁니다.
- [윈도 식별자 형식 (SID·GUID·CLSID·Known Folder ID)](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md): 이진 SID 해석입니다.
- [도구 결과 교차 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md): 파서마다 결과가 다를 때 따릅니다.

## 실습

공개 검체(NIST CFReDS 등)에서 Windows 10 이상 이미지를 골라 풀어 봅니다.

1. SRUDB.dat 의 표 목록과 SOFTWARE 하이브 `SRUM\Extensions` 의 GUID 목록을 나란히 적습니다. 한쪽에만 있는 GUID 가 있습니까?
2. SruDbIdMapTable 의 행을 IdType 별로 셉니다. 0~3 밖의 값이 있습니까?
3. IdType 0 행 가운데 `!!` 로 시작하는 행을 뽑습니다. 그 안의 시각 조각은 어느 범위에 걸쳐 있습니까? 실행 시각으로 읽을 수 있는 값입니까?
4. 앱별 자원 사용 표에서 매핑 표에 없는 AppId 가 있습니까? IdType 3 이 아닌 행을 가리키는 UserId 가 있습니까?
5. IdType 3 의 SID 를 ProfileList 로 풉니다. 풀리지 않는 SID 는 무엇입니까?
6. 경로에 나온 `HarddiskVolume` 번호가 몇 가지입니까? 각 번호를 AmCache 의 드라이브 문자 경로와 맞춰 봅니다.
7. 두 도구로 같은 파일을 열어 매핑 표 행 수와 빈칸 행 수를 비교합니다.

## 참고 문헌

1. Joachim Metz, "System Resource Usage Monitor (SRUM) database", libyal esedb-kb 문서 (개정 0.0.2, 2021년 6월). https://github.com/libyal/esedb-kb/blob/main/documentation/System%20Resource%20Usage%20Monitor%20(SRUM).asciidoc
2. Microsoft Learn, "[MS-DTYP]: SID--Packet Representation". https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dtyp/f992ad60-0fe4-4b87-9fed-beb478836861
3. Eric Zimmerman, Srum 저장소 `SrumData/Srum.cs` 와 README (Srum.cs 마지막 변경 2022-11-08). https://github.com/EricZimmerman/Srum
4. Mark Baggett, srum-dump 저장소 `configuration_file.md` 와 `srum-dump/db_ese.py`. https://github.com/MarkBaggett/srum-dump/blob/master/configuration_file.md
5. Plaso 문서, `plaso.parsers.esedb_plugins.srum` 소스. https://plaso.readthedocs.io/en/latest/_modules/plaso/parsers/esedb_plugins/srum.html
6. Autopsy API 문서 4.20.0, `ExtractSru.java` 소스. https://sleuthkit.org/autopsy/docs/api-docs/4.20.0/_extract_sru_8java_source.html
