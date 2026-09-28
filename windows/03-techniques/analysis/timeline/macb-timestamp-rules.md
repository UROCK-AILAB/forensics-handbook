---
title: "파일 시각 네 가지와 변화 규칙"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 3270
---

# 파일 시각 네 가지와 변화 규칙 (MACB·Timestamp Rules)

상위 허브: [타임라인 작성 (Timeline)](index.md)

타임라인 도구는 파일 시각을 M·A·C·B 네 글자로 줄여 보여 줍니다. NTFS 는 파일 하나에 이런 시각을 대개 여덟 개 이상 적기 때문에, 타임라인의 한 줄을 바르게 읽으려면 그 시각이 어느 필드에서 왔는지와 그 필드가 언제 갱신되는지를 알아야 합니다.

## 언제 쓰나

타임라인에서 파일 줄의 MACB 표시를 읽을 때 씁니다. 파일 시각 하나를 근거로 "그때 무슨 일이 있었다" 고 쓰기 전에, 접근 시각을 믿어도 되는지 따질 때, 복사·이동·이름 바꾸기 뒤에 시각이 어떻게 남는지 확인할 때도 씁니다.

## MACB 네 글자

MACB 는 파일 시각 네 가지를 한 글자씩 줄인 묶음입니다(참고 5).

| 글자 | 영어 | 뜻 |
|---|---|---|
| M | Modification | 수정 |
| A | Access | 접근 |
| C | Change | 변경 |
| B | Birth | 생성 |

l2t_csv 출력 형식에도 MACB 열이 있는데, 이 열은 mactime 형식과 맞추려고 둔 것입니다(참고 6).

각 글자가 NTFS 의 어느 필드에 대응하는지는 정해진 공식 기준이 없습니다(참고 5, 참고 6). NTFS 에서 C 를 "MFT 항목이 바뀐 시각" 으로 읽는 쓰임이 널리 알려져 있을 뿐입니다. 그래서 도구를 쓸 때마다 어느 필드를 C 로 내보내는지 확인합니다.

## NTFS 가 적는 시각

### 두 속성의 네 시각

NTFS 파일 레코드에서 시각을 담는 속성은 두 가지입니다. 표준 정보 속성 ($STANDARD_INFORMATION, 형식 0x10)과 파일 이름 속성 ($FILE_NAME, 형식 0x30)입니다(참고 4). 아래에서는 $SI, $FN 으로 줄여 씁니다.

| 시각 | $SI 오프셋 | $FN 오프셋 | 흔히 붙이는 글자 |
|---|---|---|---|
| 생성 | 0 | 8 | B |
| 마지막 수정 | 8 | 16 | M |
| MFT 항목 마지막 수정 | 16 | 24 | C (널리 알려진 대응, 위 절 참고) |
| 마지막 접근 | 24 | 32 | A |

오프셋은 속성 값 안에서 센 바이트 위치이고, 각 시각은 8바이트 FILETIME 입니다(참고 4). $FN 은 오프셋 0 에 부모 폴더의 파일 참조 8바이트를 먼저 두므로 $FN 의 시각은 $SI 보다 8바이트씩 뒤에 있습니다(참고 4).

디스크에는 생성·수정·MFT 항목 수정·접근 순서로 들어 있어 MACB 글자 순서와 다르므로, 헥스를 읽을 때 주의합니다. $SI 에 네 개, $FN 에 네 개가 있어 파일 하나의 시각은 대개 여덟 개이지만, $SI 없이 $FN 만 있는 MFT 항목도 있습니다(참고 4). 긴 이름과 짧은 이름(8.3)이 따로 있으면 $FN 이 두 개일 수 있고(참고 4), 그만큼 시각도 늘어납니다.

속성의 저장 형식과 헥스 풀이는 [NTFS 구조](../../../01-foundations/disk-volume/ntfs/index.md)에서 다룹니다. FILETIME 을 날짜로 바꾸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다. NTFS 와 FAT 는 시각을 저장하는 기준이 다릅니다. 기준을 맞추는 법은 [시간대·시계 오차 보정](time-normalization.md)에서 다룹니다.

### API 가 다루는 시각

| API·구조체 | 다루는 시각 |
|---|---|
| GetFileTime·SetFileTime | 생성·마지막 접근·마지막 쓰기 세 개 (참고 1) |
| FILE_BASIC_INFORMATION | CreationTime·LastAccessTime·LastWriteTime·ChangeTime 네 개 (참고 3) |

GetFileTime 으로 읽으면 시각이 세 개만 나옵니다(참고 1). ChangeTime 은 "파일이 마지막으로 바뀐 시각" 이라는 설명뿐이라(참고 3), $SI 의 어느 필드인지 이것만으로는 정할 수 없습니다. 이름이 비슷하다고 MACB 의 C 와 같은 값으로 단정하지 않습니다.

## 해상도와 갱신 시점

### FAT 의 해상도

| FAT 시각 | 해상도 (참고 1) |
|---|---|
| 생성 | 10밀리초 |
| 쓰기 | 2초 |
| 접근 | 1일 (사실상 날짜만) |

FAT 접근 시각으로는 그날 몇 시에 열었는지 알 수 없고, 쓰기 시각이 같은 두 파일은 2초 안에서 어느 쪽이 먼저인지 알 수 없습니다. 구조는 [FAT·exFAT 구조](../../../01-foundations/disk-volume/fat-exfat.md)를 봅니다.

### 핸들이 닫힐 때 반영됩니다

파일 시각이 제대로 반영된다고 보장되는 때는 변경을 만든 핸들이 닫힐 때뿐이며, 쓰기에 쓴 핸들이 모두 닫혀야 마지막 쓰기 시각이 완전히 갱신됩니다(참고 1). 그래서 프로그램이 파일을 연 채 쓰고 있으면 디스크의 쓰기 시각은 아직 최종값이 아닐 수 있습니다.

### 접근 시각은 최대 1시간 늦게 적힙니다

- NTFS 는 마지막 접근 시각을 디스크에 적는 일을 마지막 접근 뒤 최대 1시간까지 미룹니다(참고 1, 참고 2).
- 다른 속성을 갱신할 때 미뤄 둔 접근 시각이 있으면 함께 적습니다(참고 2). 마지막 수정 시각이 그런 속성의 예입니다(참고 2).
- 실행 중인 시스템에서 조회하면 메모리에 있는 정확한 값을 돌려줍니다(참고 2).
- 그래서 디스크 이미지의 접근 시각에는 마지막 1시간 안의 접근이 빠져 있을 수 있고, 라이브로 본 값과 이미지에서 읽은 값이 다를 수 있습니다.

### 접근 시각 갱신 설정

- `fsutil behavior set disablelastaccess 1` 은 디렉터리를 나열할 때 마지막 접근 시각 갱신을 끕니다(참고 2). 값을 0 으로 주면 끄지 않습니다(참고 2).
- 바꾼 설정은 재시작해야 적용됩니다(참고 2).
- 이 명령은 레지스트리 값 `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\NtfsDisableLastAccessUpdate` 를 바꿉니다(참고 2).
- 뜻이 설명된 값은 1 과 0 뿐입니다(참고 2). 실제 기기에서 다른 값이 보이면 같은 버전에서 재현해 뜻을 확인합니다.
- 기본값은 Windows 버전마다 다르다고 알려져 있습니다. 그래서 기본값을 짐작하지 않고 분석 대상의 값을 직접 읽습니다.
- 오프라인 SYSTEM 하이브에서 어느 컨트롤셋을 읽을지는 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)를 봅니다.

## 작업별 변화 규칙

이름 바꾸기·이동이 USN 저널에 어떻게 남는지는 [파일시스템 타임라인](filesystem-timeline-mft-usnjrnl-logfile.md)에서 다룹니다.

아래 규칙은 분석가 사이에서 흔히 인용되지만 공식 규칙이 아니고, Windows 버전마다 다르다는 말도 있습니다.

| 작업 | 흔히 인용되는 규칙 |
|---|---|
| 복사 | 새 파일의 생성 시각은 복사한 때가 되고, 수정 시각은 원본 값을 물려받는다 |
| 같은 볼륨 안에서 이동 | $SI 생성 시각이 그대로 남는다 |
| $FN 시각 | 파일을 만들거나 이름·위치를 바꿀 때만 갱신된다 |

이 규칙을 보고서 근거로 쓸 때는 분석 대상과 같은 버전에서 직접 재현해 확인합니다. 방법은 아래 절차에 있습니다.

## 절차

### 파일 시각 읽기

1. 파일시스템이 NTFS 인지 FAT 인지 확인합니다.
2. $SI 의 네 시각을 뽑습니다.
3. $FN 의 네 시각을 이름마다 뽑습니다. 긴 이름과 짧은 이름을 따로 적습니다.
4. 도구가 MACB 글자를 어느 필드에 붙였는지 확인합니다.
5. 접근 시각을 근거로 쓸 때는 `NtfsDisableLastAccessUpdate` 값과 최대 1시간 지연을 함께 봅니다.
6. 타임라인의 줄마다 속성($SI·$FN)과 시각 종류를 적어 둡니다.

### 변화 규칙 재현하기

1. 분석 대상과 같은 Windows 버전·빌드로 시험 환경을 만듭니다. 분석 대상의 버전은 [시스템 기본 정보](../../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md)에서 확인합니다.
2. 시험 파일을 만들고 그 파일의 $SI 와 $FN 시각을 적어 둡니다.
3. 확인하려는 작업을 한 가지만 합니다. 복사, 같은 볼륨 안 이동, 다른 볼륨으로 이동, 이름 바꾸기가 그 예입니다.
4. 작업에 쓴 프로그램을 닫은 뒤 두 속성을 다시 읽습니다. 접근 시각은 최대 1시간 늦게 적힐 수 있다는 점을 감안합니다.
5. 바뀐 필드와 그대로인 필드를 표로 남깁니다.
6. 작업 방법을 한 가지씩 바꿔 되풀이합니다. 탐색기, 명령 줄, 압축 프로그램이 그 예입니다.
7. 보고서에 재현 환경과 절차를 적습니다.

## 도구

- 타임라인 도구는 MACB 열 말고도 시각의 뜻을 적는 열을 둡니다. plaso 의 timestamp_desc 가 그 예입니다(참고 5). 출력 열은 [여러 아티팩트 합친 타임라인](super-timeline.md)에서 다룹니다.
- 어느 도구든 파일 몇 개를 골라 헥스로 읽은 값과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../reporting/tool-validation.md)을 봅니다.
- 도구가 보여 주는 $FN 이 긴 이름의 것인지 짧은 이름의 것인지 확인합니다.

## 함정과 한계

1. **MACB 순서와 저장 순서가 다릅니다.** 디스크에는 생성·수정·MFT 항목 수정·접근 순서로 들어 있습니다.
2. **C 의 뜻이 도구마다 다를 수 있습니다.** 글자와 필드의 대응이 정해져 있지 않기 때문입니다.
3. **접근 시각을 "마지막으로 연 때" 로 씁니다.** 갱신이 꺼져 있을 수 있습니다. 켜져 있어도 최대 1시간 늦게 적힙니다.
4. **FAT 시각을 초 단위로 정렬합니다.** FAT 쓰기 시각은 2초 단위이고 접근 시각은 날짜 단위입니다.
5. **흔한 규칙을 재현 없이 씁니다.** 복사·이동 규칙은 공식 규칙이 아니므로 분석 대상과 같은 버전에서 재현해 확인합니다.
6. **짧은 이름의 $FN 만 보고 판단합니다.** 긴 이름의 $FN 이 따로 있을 수 있습니다.

## 결과를 어떻게 해석하나

시각 하나로 알 수 있는 것은 "그 필드에 그 값이 적혀 있다" 는 사실뿐이므로, 누가 무엇을 했는지는 다른 기록과 이어서 판단합니다. 보고서에는 어느 속성의 어느 시각인지 늘 밝힙니다.

- 쓸 수 있는 문장(예): "report.docx 의 $SI 마지막 수정 시각은 2024-03-15 10:00:00 UTC 입니다."
- 쓰면 안 되는 문장(예): "사용자가 2024-03-15 10:00:00 UTC 에 report.docx 를 고쳤습니다."
- 시각을 누군가 고쳤을 가능성은 [시각 조작 탐지](timestomping.md)에서 따집니다.

## 참고 문헌

1. Microsoft Learn, "File Times" — https://learn.microsoft.com/en-us/windows/win32/sysinfo/file-times
2. Microsoft Learn, "fsutil behavior" — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-behavior
3. Microsoft Learn, "FILE_BASIC_INFORMATION structure (wdm.h)" — https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_file_basic_information
4. libyal, "New Technologies File System (NTFS) format" (libfsntfs 문서) — https://raw.githubusercontent.com/libyal/libfsntfs/main/documentation/New%20Technologies%20File%20System%20(NTFS).asciidoc
5. Plaso documentation, "Output and formatting" — https://plaso.readthedocs.io/en/latest/sources/user/Output-and-formatting.html
6. Forensics Wiki, "L2T CSV" — https://forensics.wiki/l2t_csv/
