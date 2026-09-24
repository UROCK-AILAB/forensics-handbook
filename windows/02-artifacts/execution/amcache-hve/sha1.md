---
title: "AmCache 해석 함정"
parent: "AmCache"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 930
---

# AmCache 해석 함정 (실행 증거가 아닌 경우·SHA1 계산 범위)

## 한 줄 요약

AmCache 에 항목이 있다는 것은 대개 그 파일이 있었다는 뜻이고, 실행했다는 뜻은 일부 항목에만 해당합니다. 항목에 적힌 SHA-1 은 파일 앞 31,457,280바이트(30MiB)만으로 구한 값입니다.

## 왜 이 두 가지를 따로 보나

AmCache (Amcache.hve) 는 실행 흔적을 다루는 자료마다 이름이 나옵니다. 그래서 "AmCache 에 있으니 실행했다" 는 문장이 보고서에 자주 들어갑니다. 해시에서도 비슷한 실수가 나옵니다. `FileId` 를 해시셋 (Hash Set) 이나 위협 정보 (Threat Intelligence) 와 대조해 맞는 것이 없으면 "알려지지 않은 파일" 로 읽기 쉽습니다.

이 페이지는 두 함정만 다룹니다.

1. 항목이 있어도 실행이 아닌 경우
2. SHA-1 을 파일 앞부분으로만 계산하는 문제

키 구성과 판별 차이는 [구조와 버전별 차이](structure-versions.md)에서 다룹니다. 값 하나하나를 읽는 법은 [실행 파일 항목](inventoryapplicationfile.md)에서 다룹니다. 하이브의 저장 형식은 [하이브 내부 구조](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)를 봅니다.

AmCache 의 동작은 Windows 버전이 아니라 호환성 라이브러리의 판에 따라 달라집니다. 이 페이지에서 "판" 은 그 라이브러리의 판을 말합니다. 괄호 안의 Windows 는 그 판이 처음 실린 버전입니다. 동작 설명은 대부분 ANSSI 논문의 실험 결과입니다(확인 범위: 라이브러리 10.0.17134 판, Win10 1803). 논문은 10.0.17763 판도 같게 동작한다고 적습니다. 그 뒤 판에서는 검체마다 키 구성부터 확인합니다.

## 함정 1 — 항목이 있어도 실행이 아닌 경우

### 항목이 들어오는 세 갈래

ANSSI 는 10.0.16299 판(Win10 1709)부터 InventoryApplicationFile 에 파일이 들어오는 길을 셋으로 나눴습니다. 2025년 Kaspersky 글도 같은 세 갈래를 들고, 그 가운데 호환성 보정이 필요한 GUI 실행 파일 갈래(아래 ①)만 실행을 뜻한다고 적습니다.

| 갈래 | 들어오는 길 | 실행을 뜻하나 | 키 마지막 기록 시각 |
|---|---|---|---|
| ① | 호환성 보정 (Shimming) 이 필요한 GUI 실행 파일을 실행함 | 뜻합니다 | 첫 실행 시각 |
| ② | 프로그램을 설치할 때 함께 깔린 EXE·SYS 파일 | 뜻하지 않습니다 | 실행 시각과, 파일이 생긴 뒤 예약 작업이 처음 돈 시각 가운데 이른 쪽 |
| ③ | 호환성 평가 예약 작업 (Microsoft Compatibility Appraiser) 이 정해진 폴더를 훑어 찾은 EXE 파일 | 뜻하지 않습니다 | ②와 같음 |

③에서 훑는 폴더는 사용자 바탕 화면, `C:\Program Files`, `C:\Program Files (x86)` 입니다. 이 폴더에 파일을 두기만 해도 항목이 생깁니다. 시작 메뉴 폴더는 LNK 파일만 훑습니다. 그 결과는 [바로가기 항목](inventoryapplicationshortcut.md)에 들어갑니다.

ANSSI 가 정리한 값 가운데 어느 갈래로 들어왔는지 알려 주는 값은 없습니다. 그래서 갈래는 경로와 다른 기록으로 짐작해야 합니다.

### 판마다 다른 실행 표시

| 판 (처음 실린 Windows) | 실행을 뜻하는 것 | 실행을 뜻하지 않는 것 |
|---|---|---|
| 6.2.9200 (Win8) ~ 10.0.10586 (Win10 1511) | 옛 `File` 키 항목 가운데 `Orphan` 키에도 걸린 파일. 어느 프로그램에도 속하지 않은 파일입니다. | 설치 폴더 아래 있어서 `File` 키에 들어간 파일 |
| 10.0.14913 (Win10 1607) | 위와 같습니다. 옛 `File`·`Orphan` 키로 판단합니다. | 새 InventoryApplicationFile 항목. 이 판에서는 프로그램에 속한 EXE 만 담습니다. |
| 10.0.16299 (Win10 1709) 이후 | InventoryApplicationFile 의 ① 갈래 항목 | ②·③ 갈래 항목 |

10.0.16299 판에서 옛 키 네 개는 비어 있습니다. ANSSI 는 옛 `Orphan` 키의 내용이 새 형식 어디에도 옮겨지지 않았다고 적었습니다. 새 형식에는 "실행했음" 을 바로 보여 주는 표시가 없다는 뜻입니다. 옛 형식과 새 형식이 한 파일에 같이 있을 때 가려 읽는 법은 [구조와 버전별 차이](structure-versions.md)를 봅니다.

### 새 형식에서 ①을 가려내는 점검

아래 순서는 판단을 돕는 점검입니다. 명세가 보장하는 규칙은 아닙니다.

1. `LowerCaseLongPath` 가 ③의 세 폴더 아래인지 봅니다. 그 아래면 폴더를 훑다가 들어왔을 수 있습니다.
2. `ProgramId` 가 [설치 프로그램 항목](inventoryapplication.md)의 키 하나를 가리키는지 봅니다. InventoryApplication 의 키 이름이 곧 `ProgramId` 입니다. 가리키면 ② 갈래일 수 있습니다.
3. GUI 실행 파일인지 봅니다. ①은 GUI 실행 파일만 담습니다. 파일이 남아 있으면 PE 헤더로 확인합니다. 읽는 법은 [실행 파일 메타데이터](../../embedded-metadata/pe-header-version-info-digital-signature.md)를 봅니다.
4. 같은 설치 폴더의 항목끼리 키 마지막 기록 시각을 견줍니다. ANSSI 는 혼자 시각이 다른 파일을 설치 뒤에 끼워 넣은 파일로 의심해 보라고 권합니다.
5. 1~3에서 ②·③으로 설명되지 않으면 실행 쪽으로 기웁니다. 그래도 다른 실행 흔적으로 확인하기 전에는 "실행했다" 고 쓰지 않습니다.

### 항목이 없다고 실행하지 않은 것은 아님

- ① 갈래는 호환성 보정이 필요한 GUI 실행 파일만 담습니다. 콘솔 프로그램이나 보정이 필요 없는 파일은 실행해도 항목이 생기지 않을 수 있습니다.
- ANSSI 는 항목이 있다는 사실로만 결론을 내리라고 적었습니다. 항목이 없다는 사실로 추론하는 것은 실험 범위 밖이라고 밝혔습니다.
- ③ 갈래는 예약 작업이 돌아야 들어옵니다. 마지막으로 돈 뒤에 생긴 파일은 아직 없을 수 있습니다.
- 최근 변경은 주 파일이 아니라 `.LOG1`·`.LOG2` 에만 있을 수 있습니다. 로그를 반영해 읽는 법은 [트랜잭션 로그와 반영 안 된 변경](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md)을 봅니다.
- Windows 7 의 옛 라이브러리(6.1 판)는 USB 드라이브나 네트워크 공유에서 실행한 파일을 [RecentFileCache.bcf](recentfilecache-bcf.md)에 남기지 않았습니다(ANSSI 실험). 새 형식에서도 그런지는 공개 실험으로 확인하지 못했습니다.

### 키 마지막 기록 시각을 실행 시각으로 읽지 않기

키 마지막 기록 시각 (Last Write Time) 은 UTC 기준 FILETIME 입니다. 무엇이 이 시각을 바꾸는지는 판마다 다릅니다.

| 판 | 키 | 키 시각이 가리키는 것 (ANSSI 실험) |
|---|---|---|
| 6.2.9200 (Win8) | `File` | 경우마다 다릅니다. 실행 시각, 예약 작업 ProgramDataUpdater 가 돈 시각, 설치 시각 가운데 하나입니다. 운영체제 파일은 어느 쪽에도 맞지 않았습니다. |
| 10.0.10240 (Win10 1507) | `File` | 대개 ProgramDataUpdater 가 돈 시각입니다. |
| 10.0.10586 (Win10 1511) | `File` | 첫 실행 시각이나 프로그램 설치 시각입니다. 이 판에서는 예약 작업이 이 키를 고치지 않습니다. |
| 10.0.14913 (Win10 1607) | InventoryApplicationFile | 언제나 호환성 평가 예약 작업이 돈 시각입니다. |
| 10.0.16299 (Win10 1709) 이후 | InventoryApplicationFile | ①은 첫 실행 시각입니다. ②·③은 실행 시각과 예약 작업 시각 가운데 이른 쪽입니다. |

ANSSI 는 옛 `File` 키 시각을 실행 시각 자체로 보지 말라고 적었습니다. 다른 기록으로 실행을 증명했더라도 이 시각은 실행 시각의 상한입니다. 상한은 "늦어도 이 시각 전에는 실행했다" 는 뜻입니다.

키 시각이 바뀌는 조건은 [키 마지막 기록 시각](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md)을 봅니다. FILETIME 을 읽는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다. 항목 안의 `LinkDate` 는 PE 헤더에 적힌 빌드 시각입니다. 실행 시각과 관계가 없습니다.

### 다른 키도 실행 기록이 아님

| 키 | 흔한 오해 | 실제 뜻 |
|---|---|---|
| [InventoryApplication](inventoryapplication.md) | 키 시각이 설치 시각이다 | 예약 작업이 돌 때마다 모든 항목을 다시 씁니다. 설치 날짜는 `InstallDate` 에 날짜 단위로만 남습니다. 지운 프로그램은 항목이 사라집니다. |
| [InventoryDriverBinary](inventorydriverbinary.md) | 드라이버가 로드되었다 | 2025년 Kaspersky 글은 로드된 드라이버로 봅니다. ANSSI 실험에서는 이 키를 예약 작업만 고쳤습니다. 로드 여부는 [서비스·드라이버](../../persistence/services-drivers.md)와 [서비스 설치 이벤트](../../event-logs/7045-4697.md)로 따로 확인합니다. |
| [InventoryApplicationShortcut](inventoryapplicationshortcut.md) | 바로가기로 실행했다 | 시작 메뉴 폴더에 LNK 파일이 있었다는 기록입니다. |

## 함정 2 — SHA-1 계산 범위

### 규칙

`FileId` 는 문자열 값이고, 앞에 `0000` 네 글자가 붙은 뒤 SHA-1 40글자가 옵니다. 이 SHA-1 은 파일 앞 31,457,280바이트만으로 계산합니다. NVISO 는 Windows 8 과 Windows 10(둘 다 64비트)에서 파일 앞부분을 `dd` 로 잘라 구한 SHA-1 이 `FileId` 와 맞는 것을 확인했고, 2025년 Kaspersky 글도 실험으로 같은 결과를 적었습니다. 파일이 31,457,280바이트 이하이면 `FileId` 는 파일 전체의 SHA-1 과 같습니다.

`Size` 값에는 파일 전체 크기가 남습니다. 10.0.16299 판부터 `Size` 는 64비트 정수(REG_QWORD) 이고, 그 전 판에서는 16진수를 적은 문자열이었습니다(ANSSI).

31,457,280바이트는 30 × 1,048,576바이트, 곧 30MiB 이며 10진 단위로는 약 31.46MB 입니다. 자료마다 "30MB", "31MB", "31.4MB" 로 적지만 모두 같은 값입니다.

옛 형식 `File` 키는 `101` 값에 같은 모양(`0000` + SHA-1)으로 해시를 적습니다. ANSSI 실험에서 이 값은 자주 비어 있었습니다. 6.2.9200 판에서는 프로그램에 속한 파일 가운데 실행하지 않았거나 보정이 필요 없던 파일에 이 값이 없었습니다. 해시가 비어 있다고 해서 파일을 읽지 못했다는 뜻은 아닙니다.

### 이 규칙이 만드는 함정

| 상황 | 잘못 읽기 | 바르게 읽기 |
|---|---|---|
| 30MiB 가 넘는 파일의 `FileId` 가 해시셋·위협 정보에 없음 | 알려지지 않은 파일이다 | 전체 파일 해시가 아니라서 원래 맞지 않습니다. 전체 해시 목록과는 비교할 수 없습니다. |
| 수집한 파일의 전체 SHA-1 과 `FileId` 가 다름 | 기록 뒤에 파일이 바뀌었다 | 먼저 `Size` 를 봅니다. 31,457,280바이트를 넘으면 앞부분만으로 다시 구해 견줍니다. |
| 30MiB 가 넘는 두 파일의 `FileId` 가 같음 | 같은 파일이다 | 앞 30MiB 가 같다는 뜻입니다. 그 뒤 내용은 다를 수 있습니다. |
| 30MiB 이하 파일의 `FileId` 가 지금 파일의 SHA-1 과 다름 | 계산 범위 탓이다 | 계산 범위로는 설명되지 않습니다. 기록 뒤에 내용이 바뀌었거나 다른 파일입니다. |
| 키 이름이 `0000` 과 40글자로 되어 있음 | 파일 내용의 해시다 | 10.0.14913 판의 InventoryApplicationFile 키 이름은 소문자 전체 경로(UTF-16LE)의 SHA-1 입니다. 파일 내용의 해시가 아닙니다. |
| 키 이름이 `파일이름\|해시` 모양 | 뒤쪽이 파일 해시다 | 10.0.16299 판부터 쓰는 이름입니다. ANSSI 는 뒤쪽 해시의 계산법을 찾지 못했습니다. 파일 내용이 아니라 이름과 경로로 정해지는 듯하다고 적었습니다. |
| 도구마다 `0000` 이 붙거나 빠짐 | 서로 다른 값이다 | 앞 `0000` 을 떼고 견줍니다. |

해시셋 대조의 일반 절차는 [해시셋 대조와 유사 해시](../../../03-techniques/analysis/hash-set-fuzzy-hash.md)를 봅니다.

### 기록 시점의 해시

`FileId` 는 항목을 쓸 때의 파일 내용으로 구한 값이라서, 그 뒤 파일이 바뀌면 항목을 다시 쓰지 않은 한 지금 파일의 해시와 맞지 않습니다. ANSSI 실험에서 두 시스템의 같은 이름·같은 경로 파일은 판이 달라도 같은 키 이름을 받았습니다. 같은 경로에 다른 판 파일이 오면 한 키의 `FileId` 가 새 값으로 바뀌는지는 공개 자료로 확인하지 못했습니다. 그래서 한 키의 `FileId` 가 그 경로의 모든 판을 대표한다고 보지 않습니다.

## 증거로서 의미

**증명하는 것**

- 항목의 경로에 그 파일이 한때 있었습니다.
- 파일이 31,457,280바이트 이하이면, `FileId` 는 기록 당시 파일 전체의 SHA-1 입니다.
- 파일이 그보다 크면, `FileId` 는 앞 30MiB 의 내용만 가리킵니다.
- 옛 형식의 `Orphan` 항목과 새 형식의 ① 갈래 항목은 실행을 뜻합니다(확인 범위: ANSSI 실험).

**증명하지 못하는 것**

- 새 형식 InventoryApplicationFile 에 항목이 있다는 사실만으로는 실행을 말할 수 없습니다.
- 키 마지막 기록 시각은 실행 시각이 아닐 수 있습니다.
- 항목이 없다는 사실은 실행하지 않았다는 증거가 아닙니다.
- 30MiB 가 넘는 파일의 `FileId` 가 해시셋에 없다는 것은 모르는 파일이라는 증거가 아닙니다.
- InventoryApplicationFile 항목에는 어느 사용자가 실행했는지 적혀 있지 않습니다.

## 지우기·조작이 남기는 흔적

- 원래 파일을 지워도 AmCache 항목은 남습니다. 파일이 없어도 경로·크기·`FileId` 로 무엇이 있었는지 알 수 있습니다.
- 하이브에서 키를 지우면 지운 키가 하이브 안이나 로그 파일에 남을 수 있습니다. 찾는 법은 [지워진 키·값 복구](../../../01-foundations/database-log-formats/registry-hive/deleted-keys-values.md)를 봅니다.
- 섀도 복사본에 남은 옛 Amcache.hve 와 견주면 사라진 항목을 찾을 수 있습니다. 절차는 [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)을 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

1. `%WinDir%\AppCompat\Programs\` 에서 `Amcache.hve` 와 `.LOG1`·`.LOG2` 를 함께 가져옵니다. 사본에서 작업합니다.
2. `Root\InventoryApplicationFile` 아래 키 하나를 골라 `FileId`·`Size`·`LowerCaseLongPath` 값의 데이터를 찾습니다. 값 레코드를 따라가는 법은 [하이브 내부 구조](../../../01-foundations/database-log-formats/registry-hive/regf-hbin-cell.md)를 봅니다.
3. `FileId` 데이터는 UTF-16LE 문자열입니다. 인코딩은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)을 봅니다.

아래는 명세로 만든 예시입니다. 모양만 보이려고 빈 입력의 SHA-1(`da39a3ee…`)을 넣었습니다. 검체에서 나온 값이 아닙니다. 왼쪽 숫자는 값 데이터 시작부터 센 바이트 위치입니다.

```
위치  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0000  30 00 30 00 30 00 30 00 64 00 61 00 33 00 39 00   0.0.0.0.d.a.3.9.
0010  61 00 33 00 65 00 65 00 35 00 65 00 36 00 62 00   a.3.e.e.5.e.6.b.
```

4. 앞 8바이트(`30 00` 네 번)가 `0000` 입니다. 그 뒤 80바이트가 SHA-1 40글자입니다.
5. 문자열은 모두 44글자, 88바이트입니다. 끝에 널 문자 2바이트가 붙어 있으면 값 크기는 90바이트입니다.
6. `Size` 가 31,457,280 보다 크면 앞부분 해시를 따로 구합니다. 파일이 남아 있거나 복구했다면 아래처럼 두 값을 구합니다.

```
head -c 31457280 sample.exe | sha1sum     # AmCache 방식: 앞 30MiB
sha1sum sample.exe                        # 파일 전체
```

`Size` 가 31,457,280 이하이면 두 값이 같아야 합니다.

### 공개 도구로 한 번

공개 도구로는 AmcacheParser, RegRipper, Plaso 같은 것이 있습니다. 도구마다 `0000` 을 떼고 보여 주기도 하고, 그대로 두기도 합니다. 예를 들어 Plaso 소스는 옛 `101` 값에서는 `0000` 을 떼고, `FileId` 는 `0000` 이 붙은 채로 둡니다. 같은 항목을 두 도구 이상으로 읽어 값을 맞춰 봅니다. 도구 결과를 견주는 법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 확인할 것 | 볼 아티팩트 | 링크 |
|---|---|---|
| 실제로 실행했나, 몇 번 했나 | 프리페치 | [프리페치](../prefetch/index.md) |
| 사용자별 마지막 실행 시각 | BAM·DAM | [BAM·DAM](../background-activity-moderator.md) |
| 탐색기로 실행한 기록 | UserAssist | [UserAssist](../userassist.md) |
| 초 단위 프로세스 시작 시각 | 4688·Sysmon 1 | [4688](../../event-logs/4688.md), [Sysmon 1](../../event-logs/sysmon/1.md) |
| 파일이 그 경로에 언제 생겼나 | $MFT·$UsnJrnl | [$MFT](../../filesystem/mft.md), [$UsnJrnl](../../filesystem/usnjrnl.md) |
| 같은 호환성 기능의 다른 기록 | 심캐시·PCA | [심캐시](../shimcache-appcompatcache.md), [PCA](../pca.md) |
| 파일 전체의 해시 | 남아 있거나 복구한 파일 | [해시로 무결성 검증](../../../03-techniques/process-acquisition/evidence-acquisition/hash-verification.md) |

전체 흐름은 [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md)를 봅니다.

## 보고서 문장 예

- 쓰지 말 것: "B.exe 는 (시각)에 실행되었다(AmCache)."
- 쓸 것: "AmCache 의 InventoryApplicationFile 에 `c:\users\(사용자)\desktop\b.exe` 항목이 있다. 이 항목은 이 경로에 파일이 한때 있었음을 보여 준다. 키 마지막 기록 시각은 (시각, UTC)이다. 이 경로는 호환성 평가 예약 작업이 훑는 폴더라서, 이 항목만으로는 실행 여부를 판단할 수 없다."
- 쓰지 말 것: "C.exe 의 SHA-1 은 (값)이며 알려진 악성 파일과 일치하지 않는다."
- 쓸 것: "AmCache 의 `FileId` 는 (값)이다. `Size` 는 (크기)바이트로 31,457,280바이트보다 크다. 따라서 이 값은 파일 앞 30MiB 의 SHA-1 이며, 파일 전체의 해시 목록과 직접 비교할 수 없다."

## 실습

NIST CFReDS 같은 공개 검체에서 Windows 10 이미지를 하나 골라 아래 질문을 풀어 봅니다.

1. Amcache.hve 의 `Root` 아래 키 목록을 봅니다. 옛 키(`File`·`Orphan`)가 있습니까, 비어 있습니까? 이 목록으로 보아 라이브러리 판은 어디쯤입니까?
2. InventoryApplicationFile 항목 가운데 경로가 사용자 바탕 화면·Program Files·Program Files (x86) 밖인 항목을 고릅니다. 그 가운데 프리페치에도 흔적이 있는 것은 몇 개입니까?
3. `Size` 가 31,457,280 보다 큰 항목이 있습니까? 이미지 안에 그 파일이 남아 있으면 앞 30MiB 의 SHA-1 과 전체 SHA-1 을 구해 `FileId` 와 견줍니다.
4. 키 마지막 기록 시각이 몇 초 안에 몰린 항목 무리가 있습니까? 그 무렵에 compattelrunner.exe 가 돈 흔적이 있습니까?
5. 한 설치 폴더의 항목들 가운데 키 시각이 혼자 다른 파일이 있습니까? 있다면 $MFT 의 생성 시각과 견줘 봅니다.

## 함께 볼 페이지

- [AmCache (Amcache.hve)](index.md)
- [프리페치 해석 함정 (꺼진 경우·보관 개수 한도·첫 실행 시각)](../prefetch/pitfalls.md)
- [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md)

## 참고 문헌

- Blanche Lagny (ANSSI), "Analysis of the AmCache" v2, 2019 — 라이브러리 판별 동작, InventoryApplicationFile 의 세 갈래, 키 시각의 뜻, `Orphan` 키, 키 이름 규칙, `Size` 형식. https://cyber.gouv.fr/documents/632/anssi-coriin_2019-analysis_amcache-v2.pdf
- NVISO Labs, "Amcache contains SHA-1 Hash – It Depends!", 2022 — SHA-1 을 앞 31,457,280바이트로만 계산함, Windows 8·10 에서 확인. https://blog.nviso.eu/2022/03/07/amcache-contains-sha-1-hash-it-depends/
- Cristian Souza (Kaspersky Securelist), "Forensic journey: hunting evil within AmCache", 2025 — 실행을 뜻하는 갈래, 31MB 계산 범위 실험, 드라이버 항목 해석. https://securelist.com/amcache-forensic-artifact/117622/
- Plaso, AmCache 레지스트리 파서 소스(amcache.py) — `FileId` 의 `0000`, 옛 `101` 값에서 `0000` 을 떼는 처리. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/winreg_plugins/amcache.py
