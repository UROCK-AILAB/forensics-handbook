# SSD TRIM과 복구 한계 (SSD·TRIM)

## 한 줄 요약

TRIM 은 OS 가 저장 장치에 어느 블록을 더는 쓰지 않는지 알려 주는 명령이고, 이를 받은 SSD 는 그 영역을 무효로 표시합니다. 그 뒤 드라이브 내부 정리 (Garbage Collection) 가 끝나면 지운 데이터는 되살리기 어렵거나 불가능할 수 있습니다. Windows 의 NTFS 는 기본 설정에서 이 알림을 보냅니다.

이 페이지는 [삭제 데이터 복구 (Data Recovery)](index.md) 의 하위 주제입니다. 다른 하위 페이지의 복구 방법이 SSD 에서 어디까지 통하는지 가늠할 때 봅니다.

## 언제 쓰나

- 증거 매체가 SSD 일 때 복구에 기대할 수 있는 범위를 먼저 정합니다.
- 비할당 영역이 0 이나 같은 값으로 채워져 있을 때 까닭을 따집니다.
- 복구 결과가 적을 때 그 사정을 보고서에 적습니다.

## TRIM 과 드라이브 내부 정리

NAND 플래시 셀은 비어 있을 때만 바로 쓸 수 있고, 데이터가 있으면 먼저 지워야 합니다. TRIM 은 OS 가 드라이브에 어느 블록이 더는 쓰이지 않는지 알려 주는 명령이며, 이를 받은 드라이브는 그 LBA 영역을 무효로 표시하기 때문에 그 뒤 그 영역을 읽어도 의미 있는 데이터가 돌아오지 않습니다. TRIM 이 내려가고 드라이브 내부 정리가 끝나면 지운 데이터 복구는 어렵거나 불가능할 수 있습니다.

> 그림 자리: 파일 삭제 → 파일시스템이 클러스터를 비할당으로 바꿈 → 삭제 알림(TRIM) → 드라이브가 LBA 를 무효로 표시 → 내부 정리 → 읽으면 의미 없는 값. 하드디스크는 덮어쓸 때까지 데이터가 남는 흐름을 나란히 놓은 그림

### TRIM 뒤 읽기 동작

TRIM 한 자리를 읽을 때 무엇이 나오는지는 드라이브마다 다릅니다. SATA 드라이브에서는 IDENTIFY 정보의 워드 69·169 로 이 동작을 알 수 있습니다.

| 종류 | TRIM 한 LBA 를 읽으면 |
|---|---|
| 비결정적 TRIM | 읽을 때마다 다른 데이터가 나올 수 있습니다. |
| DRAT (Deterministic Read After TRIM) | 늘 같은 데이터가 나옵니다. |
| RZAT (Deterministic Read Zero After TRIM) | 늘 0 이 나옵니다. |

## Windows 버전별 TRIM 지원

| Windows | 지원 범위 |
|---|---|
| Windows 7, Windows Server 2008 R2 (2009년 10월) | TRIM 지원이 시작됐습니다. Windows 7 은 처음에 ATA(PATA/SATA) 드라이브만 지원했습니다. |
| Windows 8 | SCSI 드라이버 스택과 USB Attached SCSI (UAS) 에서도 지원합니다. 주기적 TRIM 과 큐 방식 TRIM 이 더해졌습니다. |
| Windows 8.1 | NVMe SSD 의 TRIM 을 지원합니다. |

버전 말고도 TRIM 이 가는지 가르는 조건이 있습니다.

| 조건 | TRIM |
|---|---|
| NTFS·ReFS 볼륨 | 동작합니다. |
| exFAT·FAT·FAT32 볼륨 | Wikipedia 는 지원하지 않는다고 적습니다. |
| 이동식 FAT 볼륨 | Optimize-Volume 의 기본 동작이 아무 작업도 하지 않습니다. |
| 하드웨어 RAID | 대부분 TRIM 을 구현하지 않습니다(Wikipedia, 2017년 1월 기준). |
| SATA 규격 | 초기 TRIM 은 큐에 넣을 수 없는 명령이었습니다. SATA 3.1 에서 큐 방식 TRIM 이 들어왔습니다. |

## Windows 설정 확인

### 삭제 알림 설정 — fsutil

라이브 시스템에서는 아래 명령으로 설정을 봅니다. 라이브 시스템에서 명령을 실행하는 절차는 [라이브 응답](../../process-acquisition/live-response/index.md) 에 있습니다.

```
fsutil behavior query DisableDeleteNotify
```

삭제 알림(trim, unmap)은 파일 삭제로 풀린 클러스터를 저장 장치에 알리는 기능입니다. 값 1 은 삭제 알림을 끈 상태이고 값 0 은 켠 상태입니다. NTFS 는 관리자가 끄지 않는 한 기본으로 켜져 있으며, ReFS 는 v2 가 기본으로 꺼져 있고 v1 은 기본으로 켜져 있습니다. 하드디스크나 SAN 이 TRIM 을 지원하지 않는다고 알리면 알림을 받지 않습니다. 켜고 끌 때 재부팅이 필요 없고, 다음 unmap 명령부터 바뀐 설정을 따릅니다. 설정 명령 예는 `fsutil behavior set disabledeletenotify 1` (NTFS·ReFS v1) 과 `fsutil behavior set disabledeletenotify ReFS 0` (ReFS v2) 입니다.

한 PC 에서 본 결과는 이렇습니다(확인 범위: Windows 11 25H2 빌드 26200, NVMe SSD 한 대).

```
NTFS DisableDeleteNotify = 0  (Allows TRIM operations to be sent to the storage device)
ReFS DisableDeleteNotify = 0  (뒤 설명 줄임)
```

같은 PC 의 `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem` 에서 `DisableDeleteNotification` 값은 0 이었고, 같은 키에 `RefsDisableDeleteNotification` 값은 없었습니다. fsutil 문서에는 "레지스트리를 바꾼다" 는 말만 있고 값 이름은 없어서, 이 레지스트리 값이 fsutil 설정과 같은 것인지는 공식 문서로 확인하지 못했습니다. 디스크 이미지에서 이 값을 근거로 쓰려면 이 관계부터 따로 확인합니다. 하이브 읽는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다.

### 빈 섹터 전체에 다시 TRIM — Optimize-Volume·defrag

`Optimize-Volume -ReTrim` 은 볼륨에서 지금 쓰지 않는 모든 섹터에 TRIM·Unmap 힌트를 보냅니다. 저장 장치에 그 섹터를 비워도 된다고 알리는 것입니다.

매개변수 없이 실행하면 드라이브 종류마다 기본 동작이 다릅니다.

| 드라이브 종류 | 기본 동작 |
|---|---|
| HDD, 고정 VHD, Storage Space | Analyze + Defrag |
| 계층 Storage Space | TierOptimize |
| TRIM 을 지원하는 SSD | Retrim |
| 씬 프로비저닝 Storage Space, SAN 가상 디스크, 동적 VHD, 차이 VHD | Analyze + SlabConsolidate + Retrim |
| TRIM 을 지원하지 않는 SSD, 이동식 FAT, 알 수 없음 | 작업 안 함 |

기본 우선순위는 낮음이고 `-NormalPriority` 를 주면 보통 우선순위로 돕니다. `defrag /?` 도움말은 `/L` (`/Retrim`) 을 이렇게 적습니다. 씬 프로비저닝 볼륨에서는 빈 slab 을 풉니다. SSD 에서는 쓰기 성능을 위해 retrim 합니다(확인 범위: 위와 같은 PC).

### 예약된 retrim 과 그 기록

아래는 한 PC 에서 본 것입니다(확인 범위: Windows 11 25H2 빌드 26200, NVMe SSD 한 대). 모든 PC 에 맞는다고 보장하지 못합니다.

예약 작업 `\Microsoft\Windows\Defrag\ScheduledDefrag` 는 Ready 상태였고, 이 작업은 `%windir%\system32\defrag.exe` 를 인수 `-c -h -o -$` 로 실행합니다. defrag 도움말에서 `/C` 는 모든 볼륨, `/H` 는 보통 우선순위, `/O` 는 매체 종류에 알맞은 최적화입니다. `-$` 의 뜻은 확인하지 못했습니다.

Application 로그에는 공급자 `Microsoft-Windows-Defrag` 의 이벤트 ID 258 이 16건 있었습니다. 메시지 예는 "The storage optimizer successfully completed 다시 잘라내기 on OS (C:)" 와 "... 조각 모음 on OS (C:)" 이며, 한국어 표시에서 retrim 은 "다시 잘라내기" 로 나왔습니다. 258 이벤트는 2026-09-12, 2026-09-19 처럼 1주 간격으로 C: 와 RESTORE 볼륨에 나란히 남았고, NVMe SSD 인데도 "다시 잘라내기" 와 "조각 모음" 이벤트가 둘 다 남았습니다. 이 이벤트로 retrim 시각을 읽는 방법이 모든 Windows 버전에 맞는지는 확인하지 못했고, 로그를 얼마나 오래 두는지도 확인하지 못했습니다.

작업 정의를 이미지에서 읽는 법은 [예약 작업](../../../02-artifacts/persistence/scheduled-tasks/index.md) 에 있습니다. 이벤트 로그 파일을 읽는 법은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에 있습니다.

## 절차

1. 매체 종류와 연결 방식을 적습니다. SSD 인지, SATA·NVMe·USB·하드웨어 RAID 가운데 어느 것으로 붙었는지 봅니다.
2. 볼륨마다 파일시스템을 적습니다. NTFS·ReFS 인지 FAT·exFAT 인지 봅니다.
3. Windows 버전을 적습니다. 버전은 [시스템 기본 정보](../../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 읽습니다. 위 버전 표와 맞춰 그 연결 방식에 TRIM 이 갈 수 있었는지 봅니다.
4. 라이브 시스템이면 `fsutil behavior query DisableDeleteNotify` 결과를 남깁니다.
5. 예약된 retrim 을 봅니다. ScheduledDefrag 작업과 Defrag 이벤트 258 을 찾습니다. 위 관찰 범위를 함께 적습니다.
6. 이미지를 뜹니다. 방법은 [증거 획득](../../process-acquisition/evidence-acquisition/index.md) 에 있습니다.
7. 비할당 영역에서 0 이나 같은 값으로 채워진 구간이 얼마나 되는지 적습니다. 비할당 영역을 뽑는 법은 [비할당 영역과 슬랙](unallocated-slack-space.md) 에 있습니다.
8. 복구를 시도합니다. 1~5단계에서 적은 조건을 결과와 함께 적습니다.

## 함정과 한계

- 비결정적 TRIM 드라이브는 TRIM 한 LBA 를 읽을 때마다 다른 데이터가 나올 수 있습니다. 이 성질대로라면 같은 드라이브를 두 번 이미징해도 그 구간이 달라 해시가 다를 수 있습니다.
- 이미지에서 0 이 이어진 구간이 TRIM 때문인지 완전삭제 도구 때문인지 이미지만으로 가르는 근거는 이 위키에서 확인하지 못했습니다. 0 구간만으로 지우려 했다고 쓰지 않습니다. 완전삭제 여부는 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) 에서 다른 기록과 함께 봅니다.
- 삭제 알림이 켜져 있어도 TRIM 이 드라이브까지 간다고 단정하지 않습니다. USB 로 붙인 외장 SSD, 하드웨어 RAID, FAT·exFAT 볼륨은 TRIM 이 가지 않을 수 있습니다.
- TRIM 이 내려간 뒤 실제로 언제 지워지는지는 드라이브 내부 정리에 달렸습니다. 파일을 지운 시각과 데이터가 사라진 시각은 다를 수 있습니다.
- 예약된 retrim 은 삭제 시점과 상관없이 비어 있는 모든 섹터에 TRIM 을 다시 보냅니다. 그래서 파일을 지울 때 알림이 가지 않았더라도 다음 retrim 때 알림이 갈 수 있습니다.
- 설정은 재부팅 없이 바뀝니다. 수집 때 본 값이 파일을 지울 때의 값과 같다고 보지 않습니다.
- 복구가 어렵다고 해서 파일시스템 기록까지 사라지는 것은 아닙니다. 이름·시각 같은 기록은 [파일시스템 기반 복구](undelete-ntfs-fat.md) 로 따로 봅니다.

## 결과를 어떻게 해석하나

**증명하는 것**

- DisableDeleteNotify 가 0 이면, 확인한 시점에 그 파일시스템의 삭제 알림이 켜져 있었다는 것
- Defrag 이벤트 258 이 있으면, 그 시각에 그 볼륨에서 retrim 이나 조각 모음을 마쳤다는 것(위 관찰 범위 안에서)
- 이미지의 그 구간을 읽은 값

**증명하지 못하는 것**

- 특정 파일의 클러스터에 TRIM 이 실제로 갔는지
- 드라이브가 언제 그 데이터를 지웠는지
- 0 구간이 사용자가 일부러 지운 결과인지
- 파일을 지울 때도 설정이 지금과 같았는지

보고서 문장 예: "증거 매체는 NVMe SSD 이고 볼륨은 NTFS 이다. 수집 시점에 NTFS 삭제 알림은 켜져 있었다(DisableDeleteNotify = 0). Application 로그에는 이 볼륨의 retrim 완료 이벤트(Microsoft-Windows-Defrag, 이벤트 ID 258)가 D1, D2 에 남아 있다. 비할당 영역에서 파일 X 의 내용은 되살리지 못했다. 이 결과만으로 사용자가 파일을 완전삭제했다고 볼 수는 없다."

## 참고 문헌

1. Wikipedia, "Trim (computing)" — https://en.wikipedia.org/wiki/Trim_(computing)
2. Microsoft Learn, "fsutil behavior" — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-behavior
3. Microsoft Learn, "Optimize-Volume (Storage)" — https://learn.microsoft.com/en-us/powershell/module/storage/optimize-volume
