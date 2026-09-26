---
title: "타임라인 작성"
parent: "기법 · 분석"
nav_order: 3260
has_children: true
has_toc: false
---

# 타임라인 작성 (Timeline)

여러 기록에 흩어진 시각을 모아 시간순으로 정리하는 분석 기법입니다. 줄마다 그 시각이 무엇을 뜻하는지, 어느 출처에서 왔는지를 함께 적습니다.

## 왜 중요한가

- 조사 질문에는 대개 "언제" 가 들어 있는데, 아티팩트 하나는 시각 몇 개만 알려 주므로 여러 아티팩트를 시간순으로 합쳐야 앞뒤가 보입니다.
- 출처마다 시각 기준이 다릅니다. NTFS 는 UTC 로 적고, FAT 는 현지 시각으로 적습니다(참고 1). USN 저널과 이벤트 로그는 UTC 로 적습니다(참고 2, 참고 3). 한 기준으로 맞추지 않고 합치면 순서가 뒤바뀝니다.
- 파일 하나에도 시각이 여러 개 있고, 필드마다 바뀌는 조건이 다릅니다.
- 시각은 바뀔 수 있습니다. 누군가 파일 시각을 고치기도 하고 시스템 시계를 바꾸기도 하며, 시스템 시계를 바꾸면 보안 로그에 4616 이 남습니다(참고 3).
- 직접 기록이 없는 시각은 다른 시각으로 추정하기도 합니다. 계정을 만든 시각이 그 예입니다. 그 SID 의 NTUSER.DAT 생성 시각($STANDARD_INFORMATION)으로 추정하고, 그 파일이 없으면 OS 설치 시각을 씁니다. 이런 값은 보고서에 추정값이라고 밝힙니다. 계정 정보는 [사용자 계정](../../../02-artifacts/system-account/sam.md)과 [사용자 프로필 목록](../../../02-artifacts/system-account/profilelist.md)을 봅니다.

## 한눈에 보기

타임라인에 자주 넣는 출처와 시각 기준입니다. 자세한 내용은 오른쪽 열의 페이지에서 다룹니다.

| 출처 | 위치 | Windows 버전 | 시각 기준 | 알려 주는 것 | 다루는 페이지 |
|---|---|---|---|---|---|
| $MFT 의 $SI·$FN | NTFS 볼륨 | — | UTC (참고 1) | 파일마다 생성·수정·MFT 항목 수정·접근의 마지막 값 | 파일 시각 네 가지와 변화 규칙 |
| $UsnJrnl:$J | NTFS 볼륨의 $Extend 폴더 | 레코드 구조체는 Windows XP·Server 2003 부터 지원 (참고 2) | UTC (참고 2) | 파일 생성·삭제·이름 바꾸기 같은 변경 기록 | 파일시스템 타임라인 |
| $LogFile | NTFS 볼륨 | — | 공개 자료 없음 | 메타데이터 트랜잭션 저널 | 파일시스템 타임라인 |
| FAT 파일 시각 | FAT 볼륨 | — | 현지 시각 (참고 1) | 생성·쓰기·접근 | 파일 시각 네 가지와 변화 규칙 |
| 이벤트 로그 | 이벤트 로그 파일 | — | UTC. 끝에 Z 표기 (참고 3) | 이벤트마다 생긴 시각 | 여러 아티팩트 합친 타임라인 |
| 보안 로그 4616 | Security 채널 | Windows Vista·Server 2008 이상 (참고 3) | UTC (참고 3) | 시스템 시계를 바꾼 전후 시각 | 시간대·시계 오차 보정 |
| 시간대 설정 | SYSTEM 하이브 | — | — | 현지 시각을 UTC 로 바꾸는 값 (Bias) | 시간대·시계 오차 보정 |

여러 출처를 한 표에 모으는 공개 도구의 예로 plaso 가 있습니다. plaso 에서는 psort 가 결과를 여러 형식으로 내보냅니다(참고 4).

> 그림 자리: 왼쪽에 출처 상자 여러 개($MFT, $UsnJrnl, FAT 장치, 이벤트 로그, 레지스트리)를 세로로 두고, 각 상자에 "UTC" 또는 "현지 시각" 꼬리표를 붙인다. 가운데 "기준 맞추기(Bias·일광 절약 시간·4616)" 단계를 거쳐 오른쪽의 한 줄짜리 시간표로 모이는 흐름을 그린다. 시간표 아래에 "시각 조작 확인" 상자를 둔다.

## 읽는 순서

1. [파일 시각 네 가지와 변화 규칙 (MACB·Timestamp Rules)](macb-timestamp-rules.md) — M·A·C·B 네 글자와 NTFS 의 $SI·$FN 시각을 잇습니다. 접근 시각이 늦게 적히는 문제와 FAT 해상도를 다룹니다.
2. [파일시스템 타임라인 (Filesystem Timeline: $MFT·$UsnJrnl·$LogFile)](filesystem-timeline-mft-usnjrnl-logfile.md) — $MFT 의 마지막 상태와 $UsnJrnl:$J 의 변경 기록으로 파일 단위 시간표를 만듭니다. USN 레코드의 Reason 을 읽는 법을 다룹니다.
3. [여러 아티팩트 합친 타임라인 (Super Timeline)](super-timeline.md) — 파일시스템·레지스트리·이벤트 로그·브라우저의 시각을 한 표에 모읍니다. 출력 형식과 필드를 다룹니다.
4. [시간대·시계 오차 보정 (Time Normalization)](time-normalization.md) — 출처마다 다른 시각 기준을 UTC 로 맞춥니다. Bias 의 부호, 일광 절약 시간, 다른 컴퓨터에서 쓴 FAT 장치, 4616 을 다룹니다. 3번에서 출처를 합치기 전에 이 절차로 기준을 맞춥니다.
5. [시각 조작 탐지 (Timestomping)](timestomping.md) — $SI·$FN 비교와 USN 저널로 파일 시각을 일부러 바꾼 흔적을 찾습니다.

## 함께 볼 페이지

시각을 담는 구조입니다.

- [NTFS 구조](../../../01-foundations/disk-volume/ntfs/index.md)
- [FAT·exFAT 구조](../../../01-foundations/disk-volume/fat-exfat.md)
- [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)
- [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md)
- [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md)

타임라인에 자주 들어가는 아티팩트입니다.

- [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md)
- [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md)
- [NTFS 트랜잭션 로그](../../../02-artifacts/filesystem/logfile.md)
- [시간대 설정](../../../02-artifacts/system-account/time-zone.md)
- [시간 변경](../../../02-artifacts/event-logs/4616-kernel-general.md)
- [프리페치](../../../02-artifacts/execution/prefetch/index.md)

결과를 다루는 기법입니다.

- [도구 결과 교차 검증](../../reporting/tool-validation.md)
- [분석 보고서 작성](../../reporting/forensic-report.md)
- [섀도 복사본 활용](../volume-shadow-copy-analysis.md)

타임라인을 쓰는 조사 시나리오입니다.

- [PC 사용 시간 재구성 (켜짐·꺼짐·로그온)](../../../04-scenarios/activity/system-usage-time.md)
- [이 문서의 날짜를 믿을 수 있나](../../../04-scenarios/activity/document-date-verification.md)
- [지운 파일의 흔적 찾기](../../../04-scenarios/activity/deleted-file-traces.md)
- [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md)

## 참고 문헌

1. Microsoft Learn, "File Times" — https://learn.microsoft.com/en-us/windows/win32/sysinfo/file-times
2. Microsoft Learn, "USN_RECORD_V2 structure (winioctl.h)" — https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-usn_record_v2
3. Microsoft Learn, "4616(S) The system time was changed." (Windows 10 보관 문서) — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4616
4. Plaso documentation, "Output and formatting" — https://plaso.readthedocs.io/en/latest/sources/user/Output-and-formatting.html
