---
title: "NTFS 메타 파일"
parent: "NTFS 구조"
grand_parent: "기반 · 디스크·볼륨"
nav_order: 100
---

# NTFS 메타 파일 ($Bitmap·$Secure·$Extend)

> 위치: 기반 구조 > 디스크·볼륨 > [NTFS 구조](index.md)

## 한 줄 요약

NTFS 는 볼륨을 관리하는 정보도 메타 파일 (metadata file) 에 담습니다. 이 페이지는 그중 클러스터 사용 표($Bitmap), 보안 설명자 모음($Secure), 확장 메타 파일 폴더($Extend)를 다룹니다.

## 이 형식을 쓰는 아티팩트

| 분석 | 쓰는 메타 파일 | 더 볼 곳 |
|---|---|---|
| 비할당 영역 추출·카빙 | $Bitmap | [비할당 영역과 슬랙](../../../03-techniques/analysis/data-recovery/unallocated-slack-space.md) |
| 지운 파일 복구 가능성 판단 | $Bitmap | [파일시스템 기반 복구](../../../03-techniques/analysis/data-recovery/undelete-ntfs-fat.md) |
| 파일 소유자·권한 확인 | $Secure | [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) |
| 파일 변경 기록 | $Extend\$UsnJrnl | [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) |
| 바로가기 대상 추적 | $Extend\$ObjId | [바로가기 파일](../../../02-artifacts/file-folder-usage/lnk.md) |
| 정션·심볼릭 링크 목록 | $Extend\$Reparse | [링크와 리파스 포인트](hard-link-junction-reparse-point.md) |

## 구조

### 메타 파일 목록

메타 파일에도 MFT 레코드가 하나씩 있습니다. 이름은 `$` 로 시작합니다. 0~11번은 번호가 정해져 있습니다.

| MFT 번호 | 이름 | 담는 것 |
|---|---|---|
| 0 | $MFT | 모든 파일의 MFT 레코드 ([$MFT](../../../02-artifacts/filesystem/mft.md)) |
| 1 | $MFTMirr | $MFT 앞 레코드 4개의 사본 |
| 2 | $LogFile | 메타데이터 변경 기록 ([$LogFile](../../../02-artifacts/filesystem/logfile.md)) |
| 3 | $Volume | 볼륨 이름, NTFS 판 번호, 볼륨 플래그 |
| 4 | $AttrDef | 속성 종류 정의 |
| 5 | `.` | 루트 폴더 |
| 6 | $Bitmap | 클러스터 사용 여부 |
| 7 | $Boot | 부트 섹터 ([부트 섹터와 클러스터](boot-sector-cluster.md)) |
| 8 | $BadClus | 불량 클러스터 목록 |
| 9 | $Secure | 보안 설명자 모음 |
| 10 | $UpCase | 대문자 변환표 |
| 11 | $Extend | 확장 메타 파일을 담는 폴더 |
| 12~15 | (예약) | 사용 중으로 표시되지만 내용은 비어 있음 |
| 16~23 | (미사용) | 미사용으로 표시됨 |

### 버전별 차이

| NTFS 판 | 처음 쓴 Windows | 이 페이지와 관련된 차이 |
|---|---|---|
| 1.2 | NT 3.51 (NT4 도 사용) | 9번 이름이 $Quota 입니다. 보안 설명자는 파일마다 $SECURITY_DESCRIPTOR(0x50) 속성에 둡니다. $STANDARD_INFORMATION 은 48바이트입니다. $Extend 는 없습니다. |
| 3.0 | Windows 2000 | 9번이 $Secure 가 됩니다. 11번 $Extend 가 생기고 $Quota·$ObjId·$Reparse·$UsnJrnl 이 그 안에 놓입니다. $STANDARD_INFORMATION 이 72바이트로 늘고 보안 ID 필드가 생깁니다. |
| 3.1 | Windows XP 이후 (Windows 11 포함) | 메타 파일 구성은 3.0 과 같습니다. |

$Extend 안에는 Vista 부터 $RmMetadata 가, Windows 10 부터 $Deleted 가 더해집니다.

NTFS 판 번호는 $Volume 의 $VOLUME_INFORMATION(0x70) 속성에 있습니다. 속성 내용의 0x08 바이트가 주 번호, 0x09 바이트가 부 번호입니다.

### $Bitmap: 클러스터 사용 표

$Bitmap(6번)의 이름 없는 $DATA 에 비트맵이 들어 있습니다.

비트 하나가 클러스터 하나이고, 1 은 사용 중(할당), 0 은 비어 있음(비할당)입니다. 한 바이트 안에서는 가장 낮은 비트(LSB)가 앞 클러스터입니다. 클러스터 번호는 볼륨 시작 기준 번호인 LCN (Logical Cluster Number) 입니다.

비트맵은 보통 MFT 레코드에 다 들어가지 않을 만큼 큽니다. 그래서 [데이터 런](data-run-resident-non-resident.md)을 따라가 읽습니다.

NTFS 에는 이름이 비슷한 비트맵이 셋 있습니다.

| 비트맵 | 있는 곳 | 비트 하나가 가리키는 것 |
|---|---|---|
| $Bitmap 파일 | MFT 6번의 $DATA | 볼륨의 클러스터 |
| $BITMAP 속성 | MFT 0번($MFT) | MFT 레코드 |
| $BITMAP 속성 | 각 폴더의 [$I30](../../../02-artifacts/filesystem/i30.md) 색인 | 색인 블록 |

$BadClus(8번)는 `$Bad` 라는 이름 붙은 스트림에 불량 클러스터를 기록합니다. 이 스트림의 런이 가리키는 클러스터는 $BadClus 에 할당된 것이므로 $Bitmap 에서 1 입니다.

> 그림 자리: $Bitmap 한 바이트의 비트 8개가 클러스터 8개에 대응하는 모습 (LSB 가 첫 클러스터)

### $Secure: 보안 설명자 모음

보안 설명자 (Security Descriptor) 는 소유자 SID 와 접근 권한 목록(ACL)을 담은 구조입니다. NTFS 3.0 부터는 똑같은 보안 설명자를 $Secure(9번)에 한 번만 저장합니다. 파일은 $STANDARD_INFORMATION 의 보안 ID (Security ID) 로 그 설명자를 가리킵니다. 보안 ID 는 볼륨 안에서만 쓰는 번호이고, 계정을 나타내는 SID 와 다릅니다.

| 이름 | 종류 | 내용 |
|---|---|---|
| $SDS | 이름 붙은 데이터 스트림 | 보안 설명자 본문 |
| $SII | 색인 | 키: 보안 ID(4). 값: $SDS 항목 머리와 같은 20바이트 |
| $SDH | 색인 | 키: 해시(4)+보안 ID(4). 새 설명자가 이미 있는지 찾을 때 씀 |

$Secure 의 이름 없는 $DATA 는 길이가 0 입니다.

$SDS 항목 하나의 구조입니다.

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0x00 | 4 | 보안 설명자 해시 |
| 0x04 | 4 | 보안 ID |
| 0x08 | 8 | 이 항목의 $SDS 안 위치 |
| 0x10 | 4 | 이 항목의 길이 (머리 20바이트 포함) |
| 0x14 | 가변 | 보안 설명자 |

$SDS 항목은 16바이트 경계에 맞춰 놓이고 256 KiB 경계를 넘지 않으며, 항목마다 0x40000(256 KiB) 뒤에 한 벌을 더 저장합니다. 어떤 파일도 쓰지 않게 된 항목도 지우지 않습니다.

$SDS 안의 보안 설명자는 SID 와 ACL 을 안에 함께 담는 형태 (self-relative) 입니다. 머리 20바이트는 판 번호(1), 예약(1), 제어 플래그(2), 그리고 네 개의 위치 필드(각 4)입니다. 위치 필드는 순서대로 소유자 SID, 그룹 SID, SACL(감사 목록), DACL(권한 목록)이고, 설명자 시작 기준 거리입니다. 0 이면 그 부분이 없습니다.

파일 쪽 보안 ID 는 72바이트 $STANDARD_INFORMATION 의 0x34 에 있는 4바이트입니다. 바로 앞 0x30 은 소유자 ID(4), 뒤 0x38 은 쿼터 사용량(8)입니다. 쿼터 (Quota) 는 사용자별 디스크 사용량 한도이고, 쿼터가 꺼져 있으면 두 필드 모두 0 입니다. 앞쪽 시각 필드는 [두 벌의 시각](standard-information-file-name.md)에서 다룹니다.

> 그림 자리: 파일의 보안 ID → $SII 색인 → $SDS 항목 → 소유자 SID 로 이어지는 흐름

### $Extend: 확장 메타 파일 폴더

$Extend(11번)는 NTFS 3.0 부터 있는 폴더입니다.

| 경로 | 안에 든 것 | 알려 주는 것 |
|---|---|---|
| $UsnJrnl | `$J`(변경 기록), `$Max`(저널 설정) | 파일 생성·삭제·이름 변경 기록 |
| $ObjId | `$O` 색인: 객체 ID → MFT 참조, 처음 만든 볼륨 ID, 처음 객체 ID, 도메인 ID | 객체 ID 가 있는 파일의 지금 MFT 레코드 |
| $Reparse | `$R` 색인: 리파스 태그 + MFT 참조 | 볼륨의 모든 리파스 포인트 |
| $Quota | `$O` 색인: SID → 소유자 ID. `$Q` 색인: 소유자 ID → 사용 바이트·한도 | 쿼터를 켠 볼륨의 사용자별 사용량 |
| $RmMetadata | $Repair, $TxfLog, $Txf 등 | 트랜잭션 NTFS (TxF, Transactional NTFS) 기록 |
| $Deleted | 열린 채로 지워진 파일 | 누군가 열고 있을 때 지워진 파일 |

객체 ID (Object ID) 는 파일에 붙이는 GUID 입니다. 파일 자신의 $OBJECT_ID(0x40) 속성에도 들어 있습니다. 링크 추적 서비스 (Distributed Link Tracking) 는 바로가기 대상이 옮겨져도 이 값으로 다시 찾습니다. 이름 바꾸기·백업·복원은 객체 ID 를 유지합니다. 복사한 사본에는 객체 ID 가 따라가지 않습니다.

$Deleted 에 파일이 들어가는 경우는 이렇습니다. 한 프로세스가 삭제를 허용하는 방식(FILE_SHARE_DELETE)으로 파일을 열어 둡니다. 그동안 다른 프로세스가 그 파일을 지우면 파일은 $Extend\$Deleted 로 옮겨집니다. 이름은 "파일 참조 번호 16진수 + 임의 4바이트 16진수" 형식으로 바뀝니다. 마지막 핸들이 닫히면 지워집니다. 볼륨을 마운트할 때도 남은 파일을 모두 지웁니다.

$Extend 아래 파일은 번호가 정해져 있지 않습니다. $Quota·$ObjId·$Reparse 는 흔히 24·25·26번입니다. 그 뒤 번호는 볼륨마다 한 칸씩 다를 수 있고, $UsnJrnl 은 번호가 따로 정해져 있지 않습니다. 그래서 $Extend 의 $I30 색인에서 이름으로 찾은 뒤, 색인 항목의 MFT 참조로 레코드를 엽니다.

## 읽는 법

### 클러스터 하나가 할당됐는지 보기

클러스터 N 의 비트는 "N ÷ 8 의 몫" 번째 바이트의 "나머지" 번째 비트입니다.

아래는 명세로 만든 예시입니다. 특정 데이터에서 나온 값이 아닙니다. 클러스터 0x12345 는 0x12345 ÷ 8 = 몫 0x2468, 나머지 5 입니다.

```
$Bitmap 스트림 오프셋
00002460  FF FF FF FF FF FF FF FF  2F 00 00 00 00 00 00 00
                                   ^^ 0x2468
```

0x2F 는 2진수 `0010 1111` 입니다. 오른쪽 끝이 비트 0 입니다. 비트 5 가 1 이므로 클러스터 0x12345 는 사용 중입니다. 같은 바이트의 비트 4·6·7 은 0 이므로 클러스터 0x12344·0x12346·0x12347 은 비어 있습니다.

LCN 을 디스크 오프셋으로 바꾸려면 클러스터 크기를 곱하고 파티션 시작 위치를 더합니다. 파티션 시작은 [파티션 구조](../mbr-gpt.md)에서 봅니다.

### 파일 소유자 SID 찾기

1. 파일의 $STANDARD_INFORMATION 내용 0x34 에서 보안 ID 를 읽습니다.
2. $Secure 의 $SII 색인에서 그 보안 ID 를 찾아 $SDS 위치·길이를 얻습니다.
3. $SDS 의 그 위치를 읽고, 항목 머리의 보안 ID 가 같은지 확인합니다.
4. 설명자 머리의 소유자 위치로 가서 SID 를 풉니다.
5. SID 를 [사용자 계정 (SAM)](../../../02-artifacts/system-account/sam.md)과 [사용자 프로필 목록](../../../02-artifacts/system-account/profilelist.md)으로 계정에 잇습니다.

아래도 명세로 만든 예시입니다. 파일의 $STANDARD_INFORMATION 내용 0x30 줄입니다.

```
+0x30  00 00 00 00 1F 01 00 00  00 00 00 00 00 00 00 00
       소유자 ID 0  보안 ID     쿼터 사용량 0
```

보안 ID 는 0x11F 입니다. $SII 에서 0x11F 의 값이 위치 0x5080, 길이 0x6C 였다고 합시다.

```
$SDS 스트림 오프셋
00005080  A1 B2 C3 D4 1F 01 00 00  80 50 00 00 00 00 00 00
00005090  6C 00 00 00 01 00 04 80  14 00 00 00 30 00 00 00
000050A0  00 00 00 00 3C 00 00 00  01 05 00 00 00 00 00 05
000050B0  15 00 00 00 11 11 11 11  22 22 22 22 33 33 33 33
000050C0  E9 03 00 00 01 01 00 00  00 00 00 05 12 00 00 00
000050D0  02 00 1C 00 01 00 00 00  00 00 14 00 FF 01 1F 00
000050E0  01 01 00 00 00 00 00 05  12 00 00 00 00 00 00 00
```

| 위치 | 값 | 뜻 |
|---|---|---|
| 0x5084 | 0x11F | 보안 ID. 찾던 값과 같습니다. |
| 0x5088 | 0x5080 | 항목 위치. 지금 읽는 자리와 같습니다. |
| 0x5090 | 0x6C | 항목 길이 108바이트 (머리 20 + 설명자 88) |
| 0x5094 | 01 00 04 80 | 설명자 시작. 판 번호 1, 제어 플래그 0x8004 (self-relative 0x8000 + DACL 있음 0x0004) |
| 0x5098 | 0x14 | 소유자 SID 는 0x5094 + 0x14 = 0x50A8 |
| 0x509C | 0x30 | 그룹 SID 는 0x50C4 |
| 0x50A0 | 0 | SACL 없음 |
| 0x50A4 | 0x3C | DACL 은 0x50D0 |

0x50A8 의 SID 는 판 번호 1, 하위 값 5개, 기관 값 5 입니다. 하위 값은 21, 0x11111111, 0x22222222, 0x33333333, 0x3E9 입니다. 그래서 소유자는 `S-1-5-21-286331153-572662306-858993459-1001` 입니다. 그룹은 `S-1-5-18`(SYSTEM)입니다. DACL 에는 SYSTEM 에게 권한을 주는 항목(ACE) 하나가 있습니다. SID 형식은 [윈도 식별자 형식](../../value-decoding/sid-guid-clsid-known-folder-id.md)에서 다룹니다.

이 항목의 둘째 벌은 0x5080 + 0x40000 = 0x45080 에 있습니다.

$SII 없이 $SDS 만 처음부터 차례로 읽어도 "보안 ID → 설명자" 표를 만들 수 있습니다. 이때 같은 항목이 두 번씩 나오므로 보안 ID 로 한 번만 셉니다. 블록 끝 빈 곳에는 알 수 없는 바이트가 있을 수 있으므로, 머리의 위치 필드가 실제 위치와 맞는 항목만 받습니다.

## 포렌식에서 중요한 점

### 지운 데이터

파일을 지우면 그 파일이 쓰던 클러스터의 비트가 0 이 됩니다. 지운 파일의 MFT 레코드에 데이터 런이 남아 있으면 그 클러스터들의 비트를 지금 $Bitmap 에서 확인할 수 있습니다.

- 비트가 1 이면 다른 파일이 그 클러스터를 다시 가져간 것이므로 원래 내용은 덮였을 수 있습니다.
- 비트가 0 이어도 원래 내용이 그대로라는 보장은 없습니다. 다른 파일이 잠시 썼다가 지웠을 수 있고, SSD 는 비할당 클러스터가 0 으로 읽힐 수도 있습니다([SSD TRIM과 복구 한계](../../../03-techniques/analysis/data-recovery/ssd-trim.md)).

지운 파일의 MFT 레코드에도 보안 ID 가 남고 $SDS 는 항목을 지우지 않으므로 그 소유자 SID 를 풀 수 있습니다. USN 레코드 구조에도 보안 ID 필드(SecurityId)가 있어서, 이 필드가 채워져 있으면 MFT 레코드가 덮인 파일의 소유자도 찾을 수 있습니다.

- [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 안의 $Bitmap 은 그 스냅숏 시점의 할당 상태입니다.

### 손상·비정상 종료

- 전원이 갑자기 끊긴 볼륨은 $Bitmap 과 $MFT 가 서로 맞지 않을 수 있습니다. 이런 볼륨을 쓰기 가능하게 마운트하면 $LogFile 로 메타 파일이 고쳐질 수 있습니다. 원본은 [쓰기 방지](../../../03-techniques/process-acquisition/evidence-acquisition/write-blocker.md) 상태로 다룹니다.
- 볼륨 비트맵은 읽는 순간의 상태이고, 쓰기가 일어나면 곧바로 틀려질 수 있습니다. 그래서 [실행 중 시스템 이미징](../../../03-techniques/process-acquisition/live-response/live-imaging.md)으로 뜬 이미지는 $Bitmap 이 다른 메타 파일과 어긋날 수 있습니다.
- $MFT 앞부분이 망가지면 $MFTMirr 의 사본을 읽습니다. $MFTMirr 의 클러스터 번호는 부트 섹터에 있습니다.
- $SDS 항목 한 벌이 망가지면 0x40000 떨어진 다른 벌을 읽습니다.
- $Extend\$Deleted 는 마운트할 때 비워집니다. 그래서 비정상 종료 뒤 다시 마운트되지 않은 이미지나, 실행 중에 뜬 이미지에는 파일이 남아 있을 수 있습니다.

### 시각과 안티포렌식

$Bitmap 과 $Secure 에는 시각이 없습니다. 언제 바뀌었는지는 [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md)의 이유 플래그로 봅니다. USN 레코드의 시각은 UTC 입니다.

| 바뀐 것 | USN 이유 플래그 |
|---|---|
| 접근 권한 | USN_REASON_SECURITY_CHANGE (0x00000800) |
| 객체 ID | USN_REASON_OBJECT_ID_CHANGE (0x00080000) |
| 리파스 포인트 | USN_REASON_REPARSE_POINT_CHANGE (0x00100000) |

- 소유자나 권한을 바꾸면 파일의 보안 ID 가 바뀝니다. 옛 설명자는 $SDS 에 남지만, 어느 파일이 썼는지는 $SDS 만으로 알 수 없습니다. 바뀌기 전 USN 레코드의 보안 ID 필드와 비교합니다.
- 빈 공간 지우기 도구는 $Bitmap 이 0 인 클러스터를 덮어씁니다([완전삭제 도구를 썼나](../../../04-scenarios/activity/anti-forensics/wiping-tools.md)).
- 멀쩡한 클러스터를 $BadClus 의 $Bad 에 올리면, 그 클러스터는 사용 중으로 남고 사용자 파일 목록에는 보이지 않습니다. $Bad 에 런이 있으면 그 클러스터 내용을 직접 봅니다.
- $Bitmap 비트만 1 로 바꾼 클러스터도 숨는 자리가 됩니다. 모든 파일(메타 파일 포함)의 데이터 런을 모아 $Bitmap 과 비교하면 "사용 중인데 주인 없는 클러스터"가 드러납니다.

## 함정

- **비트맵 셋을 섞지 않습니다.** 클러스터는 $Bitmap 파일, MFT 레코드는 $MFT 의 $BITMAP, 색인 블록은 폴더의 $BITMAP 입니다.
- **보안 ID 는 SID 가 아닙니다.** 볼륨 안 번호이므로, 다른 볼륨의 같은 번호는 다른 설명자입니다.
- **$SDS 를 차례로 읽으면 항목이 두 번씩 나옵니다.** 설명자 수를 셀 때 두 배로 세지 않습니다.
- **소유자는 행위자가 아닙니다.** 소유자는 흔히 파일을 만든 계정이지만, 소유권은 나중에 바꿀 수 있습니다. Administrators 그룹(`S-1-5-32-544`)이 소유자인 파일도 있습니다. 보고서에는 "이 파일의 소유자는 이 SID 로 기록돼 있다" 까지만 씁니다.
- **$Extend 아래 번호를 가정하지 않습니다.** 24번을 $Quota 라고 믿고 열면 다른 파일을 읽을 수 있습니다.
- **NTFS 판 번호로 Windows 버전을 짐작하지 않습니다.** Windows 10(1809)이 64 KiB 클러스터 볼륨에 NTFS 1.2 를 쓴 사례가 있습니다.
- **$UsnJrnl:$J 는 뽑는 방식에 따라 크기가 다릅니다.** 앞부분이 비어 있는 희소 스트림이라, 구멍을 0 으로 채우면 논리 크기(수 GB)가 되고 건너뛰면 실제 데이터만 남습니다. 둘은 크기와 해시가 다르므로 어떻게 뽑았는지 기록합니다. [압축·희소 파일](compressed-sparse.md)을 봅니다.

## 도구

아래는 예로 든 공개 도구입니다. 도구마다 결과가 다를 수 있으므로 중요한 값은 헥스로 한 건씩 대조합니다([도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)).

- The Sleuth Kit: 클러스터 할당 상태 확인, 비할당 클러스터 추출, 메타 파일 스트림 추출, $Extend\$Deleted 목록 보기
- MFTECmd: $SDS 해석
- Secure2Csv: $Secure 의 보안 설명자를 표로 풀기
- libfsntfs: 볼륨 정보와 메타 파일 읽기

## 참고 문헌

- libyal, "New Technologies File System (NTFS)" (libfsntfs 문서) — https://github.com/libyal/libfsntfs/blob/main/documentation/New%20Technologies%20File%20System%20(NTFS).asciidoc
- NTFS-3G, `include/ntfs-3g/layout.h` (구조 정의와 주석) — https://github.com/tuxera/ntfs-3g/blob/edge/include/ntfs-3g/layout.h
- Microsoft Learn, "FSCTL_GET_VOLUME_BITMAP" — https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ni-winioctl-fsctl_get_volume_bitmap
- Microsoft Learn, "Distributed Link Tracking and Object Identifiers" — https://learn.microsoft.com/en-us/windows/win32/fileio/distributed-link-tracking-and-object-identifiers
- Microsoft Learn, "USN_RECORD_V2 structure" — https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-usn_record_v2
- dfir.ru, "The \"$Extend\$Deleted\" directory" (2020-03-21) — https://dfir.ru/2020/03/21/the-extenddeleted-directory/
