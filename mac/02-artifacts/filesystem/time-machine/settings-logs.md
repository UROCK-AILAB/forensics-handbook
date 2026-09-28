---
title: "백업 설정과 기록"
parent: "타임 머신"
grand_parent: "아티팩트 · 파일 시스템"
nav_order: 1030
---

# 백업 설정과 기록 (Settings·Logs)

타임 머신 설정 파일 `com.apple.TimeMachine.plist`에는 백업 대상과 백업 시각 목록이 남고 통합 로그에는 백업이 언제 시작해 무엇을 어디로 복사하고 끝났는지가 남아서, 백업 저장소의 백업 하나하나를 시간축 위에 놓는 근거가 됩니다.

## 무엇을 기록하나 · 왜 생기나

타임 머신은 백업 대상과 그 대상에 백업한 시각을 설정 파일에 적고, 백업을 돌릴 때마다 `backupd` 데몬이 통합 로그에 단계별 기록을 남깁니다 [4]. 백업을 언제 시작할지는 DAS-CTS 예약 장치가 정하고 [3], 로그에는 타임 머신 자체 기록과 함께 예약 쪽 판단도 남습니다 [4]. 이 밖에 사용자가 백업에서 뺀 제외 항목과 연결된 백업 대상 정보도 `tmutil`로 확인할 수 있습니다 [1].

백업 저장소에 남는 백업 이름과 스냅숏 구조는 [백업 저장소 구조 (Backup Store)](backup-store.md)에서 다루고, 이 페이지는 그 백업들을 언제 어떤 설정으로 했는지를 알려 주는 기록을 다룹니다.

## 위치와 버전별 차이

plaso의 타임 머신 plist 플러그인은 파일 이름 `com.apple.TimeMachine.plist`와 필수 키 `Destinations`, `RootVolumeUUID`로 이 파일을 알아봅니다 [2]. 수집한 이미지에서는 이 파일 이름으로 전체 경로를 찾습니다.

| 기록 | 내용 | 기준 |
|---|---|---|
| 설정 plist | 아래 "설정 파일" 표의 키 [2] | plaso 플러그인 코드. 최근 macOS에서 `SnapshotDates`가 여전히 채워지는지는 실제 데이터로 확인 |
| 통합 로그의 백업 단계 | 아래 "백업 한 번의 단계" 순서 [4] | Big Sur·Monterey |
| 통합 로그 문구 | 아래 "로그 문구 예" 중 [3] 표시가 붙은 것 | Sonoma·Sequoia |
| `backupd` 감시 | Monterey에서 RunningBoard가 `backupd`를 감시함 [4] | Monterey |

## 구조

### 설정 파일

설정 파일은 속성 목록 (Property List) 형식이고, 읽는 법은 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)에서 다룹니다. plaso는 최상위의 `Destinations` 배열을 돌면서 항목마다 아래 키를 읽고, 그 값을 `destination_identifier`, `snapshot_times`, `backup_alias` 속성으로 내보냅니다 [2].

| 키 | 자리 | 담는 것 |
|---|---|---|
| `Destinations` | 최상위 | 백업 대상 배열. plaso가 파일을 알아보는 필수 키 [2] |
| `RootVolumeUUID` | 최상위 | plaso가 필수로 보는 키 [2]. 값의 뜻은 단정하지 않음 |
| `DestinationID` | `Destinations` 항목 | 백업 대상 식별자 [2] |
| `SnapshotDates` | `Destinations` 항목 | 그 대상에 백업한 시각 목록 [2] |
| `BackupAlias` | `Destinations` 항목 | 바이너리 alias 데이터. 안에 백업 대상 이름 문자열이 들어 있음 [2] |

`BackupAlias`는 alias 구조라서 plaso가 dtFabric 정의 파일(`time_machine.yaml`)로 오프셋 0부터 구조를 읽어 대상 이름을 꺼냅니다 [2]. 그 문자열이 몇 번째 바이트에 있는지는 실제 파일에서 찾고, alias 구조 일반은 [파일 참조 데이터 (Alias·Bookmark)](../../../01-foundations/value-decoding/alias-bookmark.md)에서 다룹니다.

### 제외 항목

`tmutil`이 다루는 제외 항목은 세 종류입니다 [1]. 어느 항목이 제외돼 있는지는 `tmutil isexcluded`로 확인하고 [1], 제외 설정이 디스크의 어느 파일이나 속성에 남는지는 실제 데이터로 확인해야 합니다.

| 종류 | 따라가는 기준 |
|---|---|
| 스티키 제외 (sticky) | 항목 자체. 옮기거나 복사해도 제외가 따라감 [1] |
| 고정 경로 제외 | 경로. `tmutil addexclusion -p`로 넣고, root 권한과 전체 디스크 접근 권한이 필요함 [1] |
| 볼륨 제외 | 볼륨 UUID. `tmutil addexclusion -v`로 넣고, 권한 조건은 고정 경로 제외와 같음 [1] |

반출이나 은닉을 조사할 때는 문제의 자료가 든 경로가 제외돼 있는지 보고, 최근에 새로 제외된 경로가 있으면 따로 해석합니다.

### 대상 정보

`tmutil destinationinfo`는 백업 대상마다 Name, Kind, URL, Mount Point, ID를 보여 줍니다 [1]. 이 ID가 설정 파일의 `DestinationID`와 같은 값이라고 단정하지 않고, 둘을 맞춰 볼 때는 대상 이름과 마운트 지점도 함께 봅니다.

### 통합 로그

로그에서 타임 머신 기록을 찾을 때 쓰는 이름은 아래와 같습니다 [4]. 통합 로그 저장 형식은 [통합 로그 형식 (Unified Log)](../../../01-foundations/data-formats/unified-log/index.md)에서 다룹니다.

| 이름 | 가리키는 것 |
|---|---|
| `com.apple.TimeMachine` | 타임 머신 자체 기록의 서브시스템 [4] |
| `com.apple.backupd-auto` | CTS가 돌리는 백업 작업 [4] |
| `com.apple.duetactivityscheduler` | DAS의 예약 판단 [4] |
| `backupd` | 백업을 실제로 하는 데몬 [4] |

**로그 문구 예.** 아래는 문구의 앞부분만 옮긴 것이고, 숫자와 대상 이름은 줄 끝 번호의 참고 문헌에 실린 예의 값입니다. `Backing up` 줄 뒤에는 장치 경로·옵션 값·마운트 지점이, `Finished copying` 줄 뒤에는 항목 수와 크기가 더 붙는데 여기서는 줄였습니다 [3]. macOS 버전에 따라 문구가 다를 수 있습니다.

```
Starting automatic backup                                                    [4]
Estimated 318 files (565.4 MB) need to be backed up from all sources         [4]
Backing up 1 volumes to ThunderBay2                                          [3]
Finished copying from volume "External1"                                     [3][4]
Completed backup: 2021-09-28-191949.backup                                   [4]
Created 4 new snapshots, and deleted 4 old snapshots.                        [3]
```

**백업 한 번의 단계.** Big Sur·Monterey 기준으로 [4] 타임 머신은 먼저 마운트 지점과 머신 저장소를 점검하고, 오래된 스냅숏을 솎으면서 안정된 스냅숏을 만듭니다. 이어서 FSEvents를 어떻게 쓸지 정하고 이벤트 캐시를 저장한 뒤 파일을 복사하고, 새 기준 스냅숏을 처리한 다음 마지막으로 오래된 백업을 솎습니다.

이 순서에서 보듯 타임 머신은 바뀐 파일을 FSEvents로 찾아서, 백업 기록과 [파일 시스템 이벤트 (FSEvents)](../fsevents/index.md)를 함께 읽으면 백업 사이에 무엇이 바뀌었는지를 좁힐 수 있습니다.

## 증거로서 의미

**증명하는 것.** `SnapshotDates`는 그 대상에 백업한 시각 목록이고 [2], 로그는 백업을 시작한 때, 복사할 파일 수와 크기의 추정치, 복사한 볼륨과 대상 이름, 완료한 백업 이름을 남깁니다 [3][4]. 그래서 "이 시각에 이 대상 이름의 저장장치로 백업이 끝났다" 는 문장을 설정 파일과 로그 두 곳으로 받칠 수 있습니다. 백업 대상 이름이 외장 디스크나 NAS를 가리키면 그 시각에 해당 저장장치가 연결돼 있었다는 단서가 되고, 연결 기록은 [USB 저장 장치 (USB Storage)](../../external-devices/usb/index.md)나 [공유 폴더 연결 기록 (SMB·AFP)](../../network/network-shares.md)과 맞춰 봅니다.

**증명하지 못하는 것.** 로그 문구에는 파일 수와 크기가 나오지만 어떤 파일을 복사했는지는 나오지 않아서, 파일 단위 내용은 백업 저장소에서 확인합니다. `Starting automatic backup`이 보이지 않는다는 사실만으로 사람이 직접 백업했다고 쓰지 않습니다. 제외 항목은 지금 설정만 보여 주므로, 제외를 언제 넣었는지는 설정 파일로 알 수 없습니다.

보고서에는 "백업했다" 가 아니라 "통합 로그에 이 시각 `Completed backup:` 기록이 있고, 설정 파일의 `SnapshotDates`에도 같은 무렵의 시각이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`SnapshotDates`의 값은 plist 날짜값이고, plaso는 이 값에 시간대 정보가 없어서 UTC로 붙여 해석합니다 [2]. 로그 기록의 시각은 통합 로그 쪽 규칙을 따르고, 완료 기록의 백업 이름(`2021-09-28-191949.backup` 형식)에 든 시각은 백업 저장소의 이름과 같은 `YYYY-MM-DD-HHMMSS` 표기라서 [4] 세 값을 나란히 놓으면 백업 이름의 시간대를 추정하는 데 쓸 수 있습니다. 백업 이름의 시간대 문제는 [백업 저장소 구조 (Backup Store)](backup-store.md)의 시각 해석을 봅니다. plist 날짜값과 여러 시각 형식은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에서 다룹니다.

## 함정과 한계

로그 문구는 macOS 버전마다 다를 수 있어서 위 예시 문구로 문자열 검색만 하면 기록을 놓칠 수 있습니다. 서브시스템 이름으로 먼저 거른 뒤 문구를 읽는 편이 안전합니다. 로그에 백업 기록이 없는 기간이 있으면 설정 파일의 `SnapshotDates`와 백업 저장소의 백업 이름으로 그 기간을 채우고, 세 기록이 서로 어긋나는 자리를 따로 적어 둡니다.

설정 파일에서 plaso가 읽는 키는 몇 개뿐이라서, 그 밖의 키 값은 짐작으로 해석해 보고서에 쓰지 않습니다.

안티포렌식 쪽에서는 백업 디스크에서 백업을 지운 흔적과 제외 항목을 늘린 흔적을 봅니다. 백업을 지우는 단위와 방법은 [백업 저장소 구조 (Backup Store)](backup-store.md)에서 다루고, 로그의 `Created ... new snapshots, and deleted ... old snapshots.` 문구 [3]처럼 타임 머신이 스스로 스냅숏을 솎은 기록은 사람이 지운 흔적과 나눠서 읽습니다.

## 직접 분석해 보기

**헥스로.** 설정 파일은 plist라서 헥스로는 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)의 방법대로 객체 표를 따라가 `Destinations` 배열과 그 안의 `SnapshotDates`, `BackupAlias` 값을 찾습니다. `BackupAlias` 안 문자열의 오프셋은 실제 파일에서 찾고, alias 구조는 [파일 참조 데이터 (Alias·Bookmark)](../../../01-foundations/value-decoding/alias-bookmark.md)의 설명을 따라 읽습니다.

**공개 도구로.** 수집한 설정 파일은 plaso의 타임 머신 plist 플러그인으로 읽어 `destination_identifier`, `snapshot_times`, `backup_alias` 값을 타임라인에 넣을 수 있습니다 [2]. 실행 중인 Mac에서는 `tmutil destinationinfo`로 대상 정보를, `tmutil isexcluded`로 특정 경로의 제외 여부를 확인하고 [1], 이때 필요한 권한은 [백업 저장소 구조 (Backup Store)](backup-store.md)에 정리돼 있습니다. 통합 로그는 서브시스템 `com.apple.TimeMachine`으로 걸러 읽고 [4], 조회 명령을 쓰는 법은 [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md)과 [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md)을 봅니다.

## 교차 검증

- [백업 저장소 구조 (Backup Store)](backup-store.md) — 로그의 완료 기록과 `SnapshotDates`를 실제 백업 이름과 맞춰 봅니다.
- [파일 시스템 이벤트 (FSEvents)](../fsevents/index.md) — 백업이 찾은 변경 경로를 이벤트 기록과 맞춰 볼 때
- [USB 저장 장치 (USB Storage)](../../external-devices/usb/index.md) — 외장 백업 디스크가 연결된 시각을 확인할 때
- [공유 폴더 연결 기록 (SMB·AFP)](../../network/network-shares.md) — NAS로 백업한 경우
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)
- [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md)
- [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)

## 실습

공개 시험 이미지나 직접 백업을 만든 실습용 Mac에서 다음을 풀어 봅니다.

1. 설정 파일에서 백업 대상이 몇 개인지 세고, 대상마다 `BackupAlias`에서 대상 이름을 꺼냅니다.
2. `SnapshotDates`의 시각 목록과 통합 로그의 `Completed backup:` 기록, 백업 저장소의 백업 이름을 한 표에 놓고 어긋나는 자리를 찾습니다.
3. 조사 대상 폴더가 제외 항목에 들어 있는지 확인하고, 들어 있다면 보고서에 어떻게 적을지 문장으로 써 봅니다.

## 참고 문헌

1. tmutil(8) 매뉴얼 페이지 (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/tmutil.8.html
2. plaso Time Machine plist 플러그인 소스 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/plist_plugins/time_machine.py
3. The Eclectic Light Company, "Understand and check Time Machine backups to APFS" (2024-10-03) — https://eclecticlight.co/2024/10/03/understand-and-check-time-machine-backups-to-apfs/
4. The Eclectic Light Company, "Going beyond T2M2 with Mints: grokking Time Machine to APFS" (2021-09-29) — https://eclecticlight.co/2021/09/29/going-beyond-t2m2-with-mints-grokking-time-machine-to-apfs/
