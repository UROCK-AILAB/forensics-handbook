---
title: "시각 조작 탐지"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 3310
---

# 시각 조작 탐지 (Timestomping)

상위 허브: [타임라인 작성 (Timeline)](index.md)

## 한 줄 요약

파일 시각을 일부러 바꾼 흔적을 찾는 일입니다. NTFS 는 파일 하나의 시각을 $STANDARD_INFORMATION 과 $FILE_NAME 두 곳에 적으므로, 두 곳의 값을 비교하고 USN 저널 같은 다른 기록과 맞춰 봅니다. 불일치 하나만으로 조작이라고 단정하지 않습니다.

## 언제 쓰나

- 파일 시각이 다른 기록과 맞지 않을 때 씁니다.
- 의심 파일의 시각이 같은 폴더의 정상 파일과 비슷하게 맞춰져 있을 때 씁니다.
- 문서 날짜를 증거로 쓰기 전에 씁니다. 흐름은 [이 문서의 날짜를 믿을 수 있나](../../../04-scenarios/activity/document-date-verification.md)를 봅니다.
- 증거를 없애려 했는지 따질 때 씁니다. 흐름은 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md)를 봅니다.

## 기법의 정의

MITRE ATT&CK 은 이 기법을 T1070.006 "Timestomp" 로 분류하고 상위 기법은 T1070 Indicator Removal 입니다(참고 1). 이 페이지에서 연 버전 2.0 (마지막 수정 2026-05-12) 에는 전술이 "Stealth (TA0005)" 로 나오고, 대상 플랫폼은 ESXi, Linux, Windows, macOS 입니다(참고 1).

이 기법은 파일의 수정·접근·생성·변경 시각을 바꿔 같은 폴더의 정상 파일 사이에 섞이게 합니다(참고 1). MITRE 는 $STANDARD_INFORMATION($SI)을 사용자에게 보이는 쪽, $FILE_NAME($FN)을 커널이 다루는 쪽으로 설명하며, 두 속성을 모두 바꾸는 "double timestomping" 도 있다고 적었습니다(참고 1).

시스템 시계를 바꾸는 일은 이 기법과 다릅니다. 파일 하나가 아니라 그 뒤에 적히는 모든 시각에 영향을 줍니다. 흔적과 보정 방법은 [시간대·시계 오차 보정](time-normalization.md)에서 다룹니다.

## 시각을 바꾸는 공식 방법

| 방법 | 다루는 시각 | 근거 |
|---|---|---|
| SetFileTime | 생성·마지막 접근·마지막 쓰기 | 참고 2 |
| FILE_BASIC_INFORMATION (ZwSetInformationFile) | CreationTime·LastAccessTime·LastWriteTime·ChangeTime | 참고 3 |

SetFileTime 은 파일 내용을 바꾸지 않고 시각만 바꾸고(참고 2), FILE_BASIC_INFORMATION 으로 값을 설정하려면 FILE_WRITE_ATTRIBUTES 권한이 필요합니다(참고 3). 두 방법 모두 공개된 API 라서 정상 프로그램도 이 API 로 시각을 바꿀 수 있습니다. 시각 값은 1601년 시작부터 센 100나노초 단위이며(참고 3), 날짜로 푸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다.

FILE_BASIC_INFORMATION 에는 특별한 값이 있습니다.

| 넣는 값 | 해당 칸 | 효과 (참고 3) |
|---|---|---|
| 0 | 모든 시각 칸 | 그 시각은 현재 값을 유지 |
| -1 | LastAccessTime·LastWriteTime·ChangeTime | 그 핸들로 하는 I/O 에 대해 파일 시스템이 그 시각을 갱신하지 않음 |
| -2 | 위와 같음 (NTFS·ReFS) | 그 핸들의 시각 갱신을 다시 켬 |

-1 을 넣은 핸들로 내용을 쓰면 마지막 쓰기 시각이 그대로 남을 수 있습니다. 그래서 시각이 그대로라는 사실만으로 내용도 그대로라고 볼 수 없습니다.

MITRE 는 $SI 는 사용자 수준 API 로 바꿀 수 있고, $FN 은 대개 커널 수준 접근이나 파일 작업이 있어야 바뀐다고 설명합니다(참고 1). 파일을 옮기거나 이름을 바꿔 $FN 이 $SI 값을 베끼게 한다는 구체적인 동작은 이 페이지의 출처로 확인하지 못했습니다.

## 탐지 근거

### $SI 와 $FN 비교

MITRE 는 탐지 방향으로 $SI 와 $FN 의 불일치 찾기를 듭니다(참고 1).

- 같은 종류의 시각끼리 짝지어 비교합니다. 생성은 생성과, 마지막 수정은 마지막 수정과 비교합니다.
- 생성 시각은 $SI 오프셋 0, $FN 오프셋 8 에 있습니다(참고 4). 네 시각의 오프셋 표는 [파일 시각 네 가지와 변화 규칙](macb-timestamp-rules.md)에 있습니다.
- $FN 은 이름마다 하나씩 있습니다. 긴 이름의 $FN 이 확장 레코드에만 있을 수 있습니다(현장 관찰). 그래서 $ATTRIBUTE_LIST 가 있는 파일은 확장 레코드까지 따라가 비교합니다(현장 관찰). 이름공간과 확장 레코드는 [파일시스템 타임라인](filesystem-timeline-mft-usnjrnl-logfile.md)에서 다룹니다.

분석가 사이에서 흔히 쓰는 기준은 아래와 같지만 이 페이지에서 연 자료로는 확인하지 못했습니다.

| 흔히 쓰는 기준 (확인하지 못함) |
|---|
| $SI 생성 시각이 $FN 생성 시각보다 이르면 의심한다 |
| $SI 시각의 초 아래 자리(100나노초 단위 7자리)가 모두 0 이면 도구로 넣은 값일 수 있다 |

압축 해제, 복사, 설치 프로그램처럼 원래 시각을 되살리는 정상 동작도 불일치를 만든다고 알려져 있지만 이 역시 확인하지 못했습니다. 그래서 불일치 하나만으로 조작이라고 단정하지 않습니다. 의심스러운 동작은 검체와 같은 버전에서 재현해 봅니다.

### USN 저널과 맞추기

- USN_REASON_BASIC_INFO_CHANGE (0x00008000) 는 속성이나 시각이 하나 이상 바뀌면 붙고, Reason 값 가운데 시각 변경만 가리키는 플래그는 없습니다(참고 5).
- 그래서 이 플래그는 "속성이나 시각이 바뀌었다" 는 단서일 뿐이며, 레코드의 TimeStamp 는 UTC 로 적은 그 레코드의 시각입니다(참고 5).
- 그 파일의 FILE_CREATE 레코드 시각과 $SI 생성 시각을 비교합니다. 두 값이 크게 다르면 이유를 따로 확인합니다.
- $SI 의 USN 칸은 그 파일의 마지막 USN 레코드 번호로 알려져 있습니다. 이 값으로 마지막 레코드를 찾습니다. 방법은 [파일시스템 타임라인](filesystem-timeline-mft-usnjrnl-logfile.md)에서 다룹니다. 마지막 레코드의 Reason 에 BASIC_INFO_CHANGE 가 있으면, 마지막 변경에 속성이나 시각의 변경이 들어 있었습니다.
- 저널에 남은 기간 밖의 변경은 볼 수 없습니다. 레코드 구조는 [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md)을 봅니다.

### 다른 기록과 맞추기

- $LogFile 에 바뀌기 전후의 $SI 값이 남는다는 설명이 있지만 이 페이지의 출처로는 확인하지 못했습니다. 해석 방법은 [NTFS 트랜잭션 로그](../../../02-artifacts/filesystem/logfile.md)를 봅니다.
- MITRE 는 탐지 방향을 두 가지 더 듭니다(참고 1). 하나는 SetFileTime 같은 API 호출을 지켜보는 것입니다(참고 1). 다른 하나는 시각을 바꾸는 명령을 평소와 다른 사용자나 폴더에서 쓰는지 살피는 것입니다(참고 1). 사후 분석에서는 그런 도구를 실행한 흔적을 찾습니다. [프로세스 생성](../../../02-artifacts/event-logs/4688.md), [Sysmon 로그](../../../02-artifacts/event-logs/sysmon/index.md), [프리페치](../../../02-artifacts/execution/prefetch/index.md)를 봅니다.
- 파일 안에 날짜를 적는 형식이면 그 값과 비교합니다. [문서 메타데이터](../../../02-artifacts/embedded-metadata/document-metadata/index.md), [사진 EXIF](../../../02-artifacts/embedded-metadata/exif.md)를 봅니다.
- 이 페이지의 $SI·$FN 비교는 NTFS 를 전제로 합니다. FAT·exFAT 에 비교할 두 번째 시각 기록이 있는지는 확인하지 못했습니다.

## 헥스로 한 번

아래 바이트는 명세를 따라 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다.

```
$SI 속성 값
오프셋  00 01 02 03 04 05 06 07
0000    00 80 9E F4 0C 18 D5 01      <- 생성 시각

$FN 속성 값
오프셋  00 01 02 03 04 05 06 07
0000    05 00 00 00 00 00 05 00      <- 부모 폴더 참조
0008    87 26 DA 8A BF 76 DA 01      <- 생성 시각
```

1. $SI 오프셋 0 의 8바이트가 생성 시각입니다(참고 4). 리틀 엔디언으로 0x01D5180CF49E8000, 10진으로 132,038,208,000,000,000 입니다. 날짜로는 2019-06-01 00:00:00.0000000 UTC 입니다.
2. $FN 오프셋 0 의 8바이트는 부모 폴더 참조입니다(참고 4). 이 예시에서는 풀지 않습니다.
3. $FN 오프셋 8 의 8바이트가 생성 시각입니다(참고 4). 리틀 엔디언으로 0x01DA76BF8ADA2687, 10진으로 133,549,704,001,234,567 입니다. 날짜로는 2024-03-15 10:00:00.1234567 UTC 입니다.
4. $SI 생성 시각이 $FN 생성 시각보다 4년 9개월 남짓 이릅니다. 두 속성이 서로 맞지 않습니다.
5. $SI 값은 초 아래 자리가 모두 0 입니다. 위 "흔히 쓰는 기준" 두 가지에 모두 걸리는 예입니다. 두 기준 모두 확인하지 못한 기준이므로 이것만으로 결론을 내지 않습니다.
6. 다음으로 이 파일의 USN 레코드를 찾습니다. FILE_CREATE 레코드가 2024-03-15 10:00 UTC 전후에 있는지, BASIC_INFO_CHANGE 레코드가 그 뒤에 있는지 봅니다.

## 절차

1. **대상을 정합니다.** 의심 파일과 같은 폴더의 파일을 함께 뽑습니다. 폴더 안 시각 분포와 비교하려는 것입니다.
2. **$SI 네 시각을 읽습니다.** 초 아래 자리까지 읽습니다.
3. **$FN 네 시각을 이름마다 읽습니다.** $ATTRIBUTE_LIST 가 있으면 확장 레코드까지 따라갑니다.
4. **짝지어 비교합니다.** 값이 다른 칸, 앞뒤가 뒤바뀐 칸을 표시합니다.
5. **USN 저널에서 그 파일의 레코드를 찾습니다.** FILE_CREATE, RENAME_OLD_NAME·RENAME_NEW_NAME, BASIC_INFO_CHANGE 가 붙은 레코드의 시각을 적습니다.
6. **$SI 의 USN 칸으로 마지막 레코드를 확인합니다.**
7. **같은 폴더의 다른 파일과 비교합니다.** 의심 파일만 시각이 튀는지, 반대로 이웃과 지나치게 똑같은지 봅니다.
8. **시각을 바꾸는 도구를 실행한 흔적을 찾습니다.** 실행 흔적 아티팩트와 이벤트 로그를 봅니다. 흐름은 [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md)를 봅니다.
9. **시스템 시계 변경을 따로 확인합니다.** 보안 로그의 4616 을 봅니다.
10. **정상 동작으로 설명되는지 재현합니다.** 검체와 같은 버전에서 같은 작업을 해 봅니다. 방법은 [파일 시각 네 가지와 변화 규칙](macb-timestamp-rules.md)의 "변화 규칙 재현하기" 를 봅니다.
11. **근거를 표로 정리합니다.** 칸마다 값, 출처, 해석을 적습니다.

## 도구

MFT 를 푸는 공개 도구의 예로 libfsntfs, The Sleuth Kit 이 있습니다. 어느 도구를 쓰든 아래를 확인합니다.

- $FN 시각을 보여 주는지 확인합니다.
- 어느 이름공간의 $FN 을 보여 주는지 확인합니다.
- $ATTRIBUTE_LIST 의 확장 레코드를 따라가는지 확인합니다.
- 초 아래 자리를 잘라 내지 않는지 확인합니다. 초 단위까지만 담는 출력 형식도 있습니다([여러 아티팩트 합친 타임라인](super-timeline.md)).
- 몇 파일은 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../reporting/tool-validation.md)을 봅니다.

## 함정과 한계

1. **불일치를 곧 조작으로 읽습니다.** 공개 API 로 시각을 바꾸는 정상 프로그램도 있습니다.
2. **일치하면 조작이 없다고 읽습니다.** 두 속성을 모두 바꾸는 수법도 있습니다(참고 1).
3. **짧은 이름의 $FN 만 비교합니다.** 긴 이름의 $FN 이 확장 레코드에 따로 있을 수 있습니다(현장 관찰).
4. **BASIC_INFO_CHANGE 를 시각 변경으로 읽습니다.** 이 플래그는 속성 변경에도 붙습니다(참고 5).
5. **저널이 비어 있으면 변경이 없었다고 읽습니다.** 저널에 남은 기간보다 앞의 변경은 보이지 않습니다.
6. **초 단위 출력으로 비교합니다.** 초 아래 자리의 차이를 놓칩니다.
7. **시스템 시계 변경과 섞어 읽습니다.** 시계를 바꾸면 그 뒤의 모든 기록이 함께 어긋납니다. 파일 하나만 어긋난 것과 다릅니다.
8. **시각이 그대로면 내용도 그대로라고 읽습니다.** 시각 갱신을 끈 핸들로 쓸 수 있습니다(참고 3).

## 결과를 어떻게 해석하나

비교 결과는 "어느 칸에 어떤 값이 있고, 다른 칸과 어떻게 다르다" 까지만 말합니다. 조작이라는 판단은 여러 근거가 한 방향을 가리킬 때 "조작을 뒷받침하는 기록이 있다" 는 수준으로 씁니다.

- 쓸 수 있는 문장(예): "invoice.exe 의 $SI 생성 시각은 2019-06-01 00:00:00 UTC 이고 $FN 생성 시각은 2024-03-15 10:00:00 UTC 입니다. 두 값은 4년 9개월 남짓 차이 납니다."
- 쓸 수 있는 문장(예): "USN 저널에는 2024-03-15 10:00 UTC 에 invoice.exe 의 FILE_CREATE 레코드가 있습니다. 이 시각은 $SI 생성 시각과 맞지 않고 $FN 생성 시각과 맞습니다."
- 쓰면 안 되는 문장(예): "공격자가 invoice.exe 의 시각을 2019년으로 조작했습니다."
- 쓰면 안 되는 문장(예): "$SI 와 $FN 이 같으므로 시각은 조작되지 않았습니다."

## 참고 문헌

1. MITRE ATT&CK, "Indicator Removal: Timestomp, T1070.006" — https://attack.mitre.org/techniques/T1070/006/
2. Microsoft Learn, "File Times" — https://learn.microsoft.com/en-us/windows/win32/sysinfo/file-times
3. Microsoft Learn, "FILE_BASIC_INFORMATION structure (wdm.h)" — https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_file_basic_information
4. libyal, "New Technologies File System (NTFS) format" (libfsntfs 문서) — https://raw.githubusercontent.com/libyal/libfsntfs/main/documentation/New%20Technologies%20File%20System%20(NTFS).asciidoc
5. Microsoft Learn, "USN_RECORD_V2 structure (winioctl.h)" — https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-usn_record_v2
