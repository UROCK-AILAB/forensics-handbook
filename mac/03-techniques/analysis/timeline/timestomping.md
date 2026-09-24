---
title: "시각 조작 흔적"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 2070
---

# 시각 조작 흔적 (Timestomping)

파일 시각을 일부러 바꿨을 때 macOS 파일 시스템과 로그에 어떤 어긋남이 남는지, 어느 칸이 바뀌지 않고 기준이 되는지를 정리하고, 그 어긋남으로 조작을 의심하고 확인하는 방법을 다룹니다.

## 언제 쓰나

파일 시각이 다른 기록과 맞지 않거나, 문서 날짜가 쟁점이거나, 침해 사고에서 악성 파일이 주변 시스템 파일과 똑같은 날짜를 달고 있을 때 씁니다. MITRE ATT&CK 은 파일 시각 조작을 T1070.006 Timestomping(상위 기법 T1070 Indicator Removal)으로 분류하고 적용 플랫폼에 macOS 를 넣었으며, 이 페이지는 2026-05-12 판(버전 2.0)을 기준으로 합니다 [4]. macOS 사례로는 OSX_OCEANLOTUS.D 가 `touch -t` 를 썼고 MacMa 에 파일 시각을 만들고 바꾸는 기능이 있었다고 적혀 있습니다 [4]. 파일 시각을 타임라인으로 뽑는 방법은 [파일 시스템 타임라인 (APFS·FSEvents)](filesystem-timeline.md) 에서 다룹니다.

## 어느 칸이 바뀌고 어느 칸이 남나

`setattrlist` 시스템 호출은 생성(`ATTR_CMN_CRTIME`), 수정(`ATTR_CMN_MODTIME`), 변경(`ATTR_CMN_CHGTIME`), 접근(`ATTR_CMN_ACCTIME`), 백업(`ATTR_CMN_BKUPTIME`), 추가(`ATTR_CMN_ADDEDTIME`) 시각을 설정 대상으로 받습니다 [1]. 다만 man 페이지는 `ATTR_CMN_CHGTIME` 을 프로그램으로 설정할 수 없고 설정하려는 시도는 무시된다고 적고 있어서 [1], 변경 시각(ctime, APFS 의 `change_time`)은 조작을 가릴 때 기준으로 삼을 수 있는 칸입니다.

생성·수정·접근·추가 시각을 바꾸려면 파일 소유자여야 하고, 그 밖의 속성은 쓰기 권한이 있으면 됩니다 [1]. 관리자 권한이 없는 사용자도 자기 파일의 시각은 바꿀 수 있어서, 조작 가능성을 따질 때 권한 상승 흔적이 없다는 점만으로 가능성을 지우지 않습니다.

`ATTR_CMN_MODTIME` 을 `ATTR_CMN_CRTIME` 보다 이른 시각으로 설정하면 생성 시각도 같은 값이 됩니다 [1]. 수정 시각만 과거로 돌려도 생성 시각이 함께 끌려 내려가서, 생성 시각과 수정 시각이 나노초까지 똑같은 파일이 남을 수 있습니다.

`touch` 명령은 수정·접근 시각을 설정하고, man 페이지에는 생성·변경 시각을 다룬다는 말이 없습니다 [2]. 셸 기록이나 로그에서 아래 모양의 명령을 만나면 시각을 손댄 흔적인지 확인합니다.

| 옵션 | 뜻 [2] |
|---|---|
| `-a` / `-m` | 접근 시각만 / 수정 시각만 |
| `-r` | 다른 파일의 시각을 그대로 복사 |
| `-t` | `[[CC]YY]MMDDhhmm[.SS]` 형식으로 시각 지정 |
| `-d` | `YYYY-MM-DDThh:mm:SS[.frac][tz]` 형식으로 시각 지정 |
| `-A` | 파일의 접근·수정 시각을 지정한 값만큼 앞뒤로 조정 |
| `-h` | 심볼릭 링크가 가리키는 파일이 아니라 링크 자체 |

## 절차

1. **의심 파일과 비교 대상을 정합니다.** 의심 파일 하나만 보지 않고 같은 폴더의 다른 파일, 같은 시각에 설치됐어야 할 파일을 함께 뽑아 네 시각과 `date_added` 를 나노초까지 나란히 놓습니다.

2. **변경 시각과 다른 시각을 비교합니다.** 변경 시각이 생성·수정 시각보다 한참 뒤라면 그 사이에 아이노드 정보를 바꾼 일이 있었다는 뜻이라서, 그 시각 무렵의 로그와 셸 기록을 찾아봅니다. 시각을 설정하는 동작 자체가 변경 시각을 새로 찍는지는 이번 출처로 직접 확인하지 못해서, 같은 macOS 버전에서 재현해 본 뒤에 결론에 씁니다.

3. **생성 시각과 수정 시각이 똑같은지 봅니다.** 둘이 나노초까지 같고 둘 다 주변 파일보다 과거라면, 수정 시각을 생성 시각보다 이르게 설정했을 때 생성 시각이 함께 맞춰지는 동작 [1] 과 들어맞는지 따집니다.

4. **초 아래 자리를 봅니다.** APFS 는 나노초까지 저장하지만 [3] `touch -t` 는 초까지만 받아서 [2], 나노초 자리가 모두 0 인 파일은 이런 방식으로 시각을 지정했을 가능성을 보여 줍니다. `touch -d` 는 소수 초도 받고 [2], HFS+ 볼륨의 시각은 원래 초 단위라서 [5], 0 이 아니라고 조작이 없었다거나 0 이라고 조작이 있었다고 단정하지 않습니다.

5. **다른 출처의 순서와 맞춰 봅니다.** 디렉터리 레코드의 `date_added` [3], [파일 시스템 이벤트 (FSEvents)](../../../02-artifacts/filesystem/fsevents/index.md) 의 이벤트 순서, 통합 로그 항목과 파일 시각이 같은 순서로 이어지는지 봅니다. `date_added` 도 파일 소유자가 `ATTR_CMN_ADDEDTIME` 으로 설정할 수 있는 칸이라서 [1], 한 출처가 아니라 여러 출처가 함께 어긋나는지를 봅니다.

6. **명령 실행 흔적을 찾습니다.** MITRE 의 탐지 전략에는 `touch -a -m -t`, `touch -r` 같은 명령 실행을 감시하는 내용이 들어 있어서 [4], [터미널 명령 기록 (zsh_history·bash_sessions)](../../../02-artifacts/execution/shell-history.md) 과 [통합 로그의 프로세스 실행 기록 (Process Events)](../../../02-artifacts/execution/unified-log-process.md) 에서 같은 모양의 명령과 대상 경로를 찾습니다.

> 그림 자리: 조작된 파일의 생성·수정 시각은 과거에 있고 변경 시각과 FSEvents 순서, 통합 로그 속 `touch` 실행은 최근에 모여 있는 타임라인

## 도구

살아 있는 시스템에서는 `stat` 으로 네 시각을 보고, 이미지에서는 APFS 를 직접 읽는 공개 도구로 나노초까지 뽑습니다. 초까지만 보여 주는 도구로는 절차 3·4 의 비교를 할 수 없어서, 쓰기 전에 도구가 나노초를 내보내는지 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md) 방식으로 확인합니다.

## 함정과 한계

위 단서는 모두 조작을 의심하게 만드는 어긋남일 뿐이고, 정상 동작에서도 비슷한 모양이 나올 수 있습니다. 파일 소유자라면 어느 프로그램이든 시각을 설정할 수 있어서 [1] 정상 프로그램이 설정한 값일 수도 있고, 복사·압축 해제·설치 같은 동작이 어느 칸을 어떻게 설정하는지는 이 페이지의 출처로 확인하지 못했습니다. `SetFile`·`GetFileInfo` 같은 개발자 도구가 지금도 제공되는지도 확인하지 못했습니다.

윈도우에서는 $STANDARD_INFORMATION 과 $FILE_NAME 의 시각을 비교해 조작을 찾지만 [4], 맥에는 그런 두 번째 시각 사본이 없어서 변경 시각, FSEvents, 로그 같은 다른 출처와 비교하는 수밖에 없습니다. 변경 시각도 프로그램으로 설정할 수 없을 뿐이라서, 시스템 시계를 돌려 놓고 작업했거나 볼륨을 직접 편집했다면 변경 시각 역시 실제 시각과 어긋날 수 있고, 이럴 때는 [시각 정규화 (Time Normalization)](time-normalization.md) 의 방법대로 맥 밖에서 찍힌 시각과 맞춰 봅니다.

## 결과를 어떻게 해석하나

| 발견 | 말해 주는 것 | 말해 주지 못하는 것 |
|---|---|---|
| 변경 시각이 생성·수정 시각보다 한참 뒤 | 그 사이 아이노드 정보가 바뀐 일이 있음 | 시각을 조작했는지, 다른 속성이 바뀌었는지 |
| 생성 시각 = 수정 시각, 둘 다 과거 | 수정 시각을 과거로 설정한 동작과 모양이 맞음 | 조작이 있었다는 확정 |
| 나노초 자리가 0 | 초 단위로 시각을 지정했을 가능성 | 어떤 도구로, 누가 지정했는지 |
| 셸 기록·로그의 `touch -t`·`touch -r` | 그 명령이 실행된 기록이 있음 | 그 명령이 이 파일에 실제로 적용됐는지(경로 대조 필요) |

보고서에는 "이 파일의 생성·수정 시각은 2019년이지만 변경 시각과 같은 경로의 FSEvents 기록, 셸 기록의 `touch` 실행은 2024년 3월에 모여 있어 시각이 설정됐을 가능성이 있다" 처럼 어긋난 기록을 나란히 적고, 누가 했는지와 목적은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md) 와 [이 문서의 날짜를 믿을 수 있나 (Document Date)](../../../04-scenarios/activity/document-date.md) 의 흐름으로 따로 확인합니다.

## 참고 문헌

1. setattrlist(2) man 페이지 — https://keith.github.io/xcode-man-pages/setattrlist.2.html
2. touch(1) man 페이지 — https://keith.github.io/xcode-man-pages/touch.1.html
3. libyal libfsapfs — Apple File System (APFS) format — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
4. MITRE ATT&CK, T1070.006 Timestomping — https://attack.mitre.org/techniques/T1070/006/
5. Apple Technical Note TN1150, HFS Plus Volume Format — https://developer.apple.com/library/archive/technotes/tn/tn1150.html
