---
title: "APFS의 시각 네 가지"
parent: "APFS 구조"
grand_parent: "기반 · 디스크·볼륨"
nav_order: 40
---

# APFS의 시각 네 가지 (Create·Modify·Change·Access)

APFS 아이노드에는 생성·내용 수정·속성 변경·접근 네 시각이 1970-01-01 00:00 UTC부터 센 나노초로 적히고 [1], 디렉터리 항목의 추가 시각까지 더하면 파일 하나에 시각 다섯 개가 남지만, 접근 시각은 볼륨 설정에 따라 "마지막으로 읽은 때"가 아닐 수 있습니다 [1].

아이노드 레코드 전체의 구조는 [파일 시스템 트리와 아이노드 (FS Tree·Inode)](fs-tree-inode.md)에 있고, 이 페이지는 시각 필드의 뜻과 해석만 다룹니다.

## 이 시각을 쓰는 곳

파일 시스템 시각은 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)의 뼈대이고, [이 파일을 누가 언제 열었나 (File Access)](../../../04-scenarios/activity/file-access.md)와 [이 문서의 날짜를 믿을 수 있나 (Document Date)](../../../04-scenarios/activity/document-date.md) 같은 조사에서 가장 먼저 꺼내 보는 값입니다.

## 네 시각의 정의

`j_inode_val_t` 안의 시각 필드는 아래와 같고, 오프셋은 아이노드 값 시작을 기준으로 셉니다 [1][2].

| 오프셋 | 필드 | 정의 |
|---|---|---|
| 16 | `create_time` | 이 레코드가 만들어진 시각 |
| 24 | `mod_time` | 이 레코드가 마지막으로 수정된 시각 |
| 32 | `change_time` | 이 레코드의 속성이 마지막으로 수정된 시각 |
| 40 | `access_time` | 이 레코드에 마지막으로 접근한 시각 |

네 필드 모두 8바이트이고, 1970-01-01 00:00 UTC부터 윤초를 빼고 센 나노초입니다 [1]. 2001년을 기준으로 하는 맥 절대 시각이 아니라 유닉스 기준이라서, 10^9로 나누면 유닉스 초가 됩니다. 맥에서 쓰는 여러 시각 기준은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../value-decoding/mac-time-values.md)에서 비교합니다.

값이 0이면 설정되지 않은 시각입니다 [2]. [1]은 이 필드를 부호 없는 `uint64_t` 로, [2]는 부호 있는 정수로 적어 둘이 다르지만, 1970년 이후 값을 읽을 때는 결과가 같습니다.

2020-06-22 판 명세까지는 macOS 10.13 이후 이 네 필드의 정의가 바뀌지 않았습니다 [1]. 그 뒤 macOS에서 달라졌는지는 실제 데이터로 확인해야 합니다.

## 접근 시각 규칙

볼륨에 `APFS_FEATURE_STRICTATIME` (0x8)가 켜져 있으면 파일을 읽을 때마다 `access_time` 을 갱신하고, 꺼져 있으면 읽을 때 `access_time` 이 `mod_time` 보다 이전인 경우에만 갱신합니다 [1]. 이 규칙대로라면 플래그가 꺼진 볼륨의 접근 시각은 "마지막 접근"이 아니라 "마지막 수정 뒤 첫 접근"에 가깝습니다.

macOS 기본 볼륨에서 이 플래그가 꺼져 있는지는 공개 문서에 나와 있지 않습니다. 그래서 접근 시각을 해석하기 전에 그 볼륨 슈퍼블록의 `apfs_features` 에서 0x8 비트를 직접 확인합니다. 볼륨 슈퍼블록의 필드 위치는 [컨테이너와 볼륨 (Container·Volume)](container-volume.md)에 있습니다.

## 다섯째 시각 date_added

디렉터리 항목의 값 `j_drec_val_t` 오프셋 8에는 `date_added` 가 있고, 단위는 아이노드 시각과 같은 1970 UTC 기준 나노초입니다 [1][2]. 이 값은 항목이 그 디렉터리에 추가된 시각이고, 같은 디렉터리 안에서 이름만 바꿀 때는 갱신하지 않습니다 [1].

다른 디렉터리로 옮기면 새 디렉터리 항목이 생기니 옮긴 시각이 남을 것으로 보입니다. 다만 명세는 같은 디렉터리 안의 이름 변경까지만 다루므로 [1], 보고서에서는 "이 디렉터리에 이 항목이 추가된 시각"이라고만 씁니다.

## 변화를 알려 주는 다른 값

시각은 아니지만 아이노드의 `write_generation_counter` 는 아이노드나 그 데이터가 바뀔 때마다 1씩 늘고, 디렉터리 통계의 `gen_count` 는 그 디렉터리나 자식이 바뀔 때마다 늘어납니다 [1]. 두 값은 바뀐 때가 아니라 바뀐 횟수를 알려 줍니다.

## 볼륨과 스냅숏의 시각

파일 말고도 시각이 남는 곳이 있고, 단위는 모두 1970 UTC 기준 나노초입니다 [1].

| 위치 | 시각 | 자세히 |
|---|---|---|
| 볼륨 슈퍼블록 `apfs_unmount_time` | 마지막 언마운트 | [컨테이너와 볼륨 (Container·Volume)](container-volume.md) |
| 볼륨 슈퍼블록 `apfs_last_mod_time` | 마지막 수정 | 같은 곳 |
| `apfs_formatted_by.timestamp` | 볼륨을 만든 때 | 같은 곳 |
| `apfs_modified_by[i].timestamp` | 볼륨을 고친 프로그램별 마지막 시각. 0번이 가장 최근 | 같은 곳 |
| 스냅숏 메타데이터 `create_time`·`change_time` | 스냅숏 생성과 마지막 수정 | [스냅숏 (Snapshots)](snapshots.md) |

## 읽는 법

### 헥스로 한 번

아래 바이트는 실제 데이터가 아니라 명세 [1]의 정의에 맞춰 만든 예시 값입니다. 아이노드 값의 오프셋 16에 이 8바이트가 있다고 합시다.

```
값 내 오프셋
0010  15 CD C0 08 17 10 A6 17
```

리틀 엔디언으로 읽으면 0x17A6101708C0CD15 = 1704067200123456789이고, 10^9로 나누면 1704067200초와 123456789나노초입니다. 1970-01-01 00:00 UTC에서 1704067200초 뒤는 2024-01-01 00:00:00 UTC이라서, 이 파일의 `create_time` 은 2024-01-01 00:00:00.123456789 UTC입니다. 표시할 현지 시각은 이 값에 확보 대상의 시간대를 적용해서 따로 계산하고, 시간대 설정은 [시간대와 시계 설정 (Time Zone·NTP)](../../../02-artifacts/system-account/time-zone.md)에서 확인합니다.

같은 계산을 파이썬 표준 라이브러리로 하면 아래와 같습니다. 부동소수로 나누면 나노초 자리가 뭉개지므로 정수 나눗셈을 씁니다.

```python
import datetime
ns = int.from_bytes(bytes.fromhex("15cdc0081710a617"), "little")
sec, rem = divmod(ns, 10**9)
print(datetime.datetime.fromtimestamp(sec, datetime.timezone.utc), rem)
```

### 절차

1. 볼륨 슈퍼블록의 `apfs_features` 에서 `APFS_FEATURE_STRICTATIME` 비트를 확인해 접근 시각 규칙을 정합니다.
2. 대상 파일의 아이노드에서 네 시각을, 부모 디렉터리 아래의 디렉터리 항목에서 `date_added` 를 읽습니다.
3. 0인 필드는 "설정 안 됨"으로 따로 표시하고 1970-01-01로 옮겨 적지 않습니다.
4. 모든 값을 UTC로 적고, 현지 시각은 시간대를 밝혀 옆에 덧붙입니다.
5. 같은 파일이 스냅숏에도 있으면 스냅숏 쪽 아이노드의 시각도 읽어 둘을 나란히 놓습니다.

## 증거로서 의미

### 증명하는 것

네 시각은 확보 시점에 파일 시스템이 그 레코드에 적어 둔 값이고, 각 값의 뜻은 위 표의 정의만큼입니다 [1]. `date_added` 는 그 항목이 그 디렉터리에 추가된 시각이고 [1], `apfs_modified_by` 의 시각은 어떤 구현이 볼륨을 고친 마지막 때입니다 [1].

### 증명하지 못하는 것

네 시각의 정의는 모두 "이 레코드" 기준이라서 [1], `create_time` 이 문서 내용이 처음 만들어진 때와 같다는 보장은 없습니다. 문서 안에 적힌 날짜는 [문서 메타데이터 (iWork·Office)](../../../02-artifacts/embedded-metadata/iwork-office.md)에서 따로 읽고 서로 맞춰 봅니다.

시각에는 누가 바꿨는지가 적히지 않고, 접근 시각이 갱신됐다고 사람이 파일을 열어 봤다고 단정할 수도 없습니다. 복사, 이동, 압축 풀기, Finder 복사, `touch`, `cp -p` 때 각 시각이 어떻게 바뀌는지는 공개된 분석 자료가 없어서, 이런 동작을 가정한 해석은 같은 macOS 버전에서 직접 실험한 결과가 있을 때만 씁니다.

보고서에는 "이 볼륨의 파일 시스템 레코드에 이 파일의 내용 수정 시각이 2024-01-01 00:00:00 UTC로 기록되어 있다"처럼 기록으로 확인되는 만큼만 씁니다.

## 함정

단위를 헷갈리는 일이 가장 흔합니다. APFS 아이노드 시각은 1970 기준 나노초인데 같은 맥 안의 plist와 SQLite에는 2001 기준 초를 쓰는 값도 있어서, 값의 자릿수로 먼저 단위를 추정합니다. 1970 기준 나노초라면 요즘 값은 19자리 10진수입니다.

`change_time` 은 이름과 달리 생성 시각이 아니라 속성이 마지막으로 바뀐 시각이고 [1], `mod_time` 은 내용 쪽입니다 [1]. 윈도우 도구의 열 이름 순서에 맞춰 옮기다 두 필드를 바꿔 적지 않도록 필드 이름을 함께 적습니다.

시각 필드는 아이노드 값 안의 숫자라서 바꾸려면 아이노드를 고쳐야 하고, `write_generation_counter` 는 아이노드가 바뀔 때마다 늘어납니다 [1]. 이 정의대로라면 시각만 고친 조작도 카운터를 늘릴 수 있지만, 카운터 값 하나로는 언제 몇 번 바뀌었는지 알 수 없어서 스냅숏이나 백업에 남은 같은 아이노드의 값과 비교할 때만 단서가 됩니다. 조작을 판단하는 방법은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

## 교차 검증

아이노드 시각 하나만으로 행위를 단정하지 않고 다른 기록과 맞춰 봅니다. 파일 생성·이름 변경·삭제 이벤트는 [파일 시스템 이벤트 (FSEvents)](../../../02-artifacts/filesystem/fsevents/index.md)에, 파일을 열거나 쓴 앱의 흔적은 [스포트라이트 (Spotlight)](../../../02-artifacts/file-folder-usage/spotlight/index.md)와 [최근 항목 (Shared File Lists)](../../../02-artifacts/file-folder-usage/recent-items/index.md)에 남습니다. 스냅숏이나 [타임 머신 (Time Machine)](../../../02-artifacts/filesystem/time-machine/index.md) 백업에 같은 파일이 있으면 그 시점의 시각과 지금 시각을 나란히 놓아 바뀐 필드를 찾고, 방법은 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../../03-techniques/analysis/snapshot-diff.md)에 있습니다.

## 도구

afro는 APFS에서 뽑아낸 파일로 body file을 만들어 mactime 타임라인에 넣을 수 있게 해 주지만, 지금은 유지보수하지 않는 도구입니다 [3]. 어떤 도구를 쓰든 시각 하나를 골라 위 헥스 계산과 같은 값이 나오는지, 표시 시간대가 UTC인지 먼저 확인합니다.

## 참고 문헌

1. Apple, Apple File System Reference (2020-06-22 판, PDF) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
2. Joachim Metz, libfsapfs — Apple File System (APFS) 형식 문서 (개정 0.0.18, 2026년 8월) — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
3. afro (APFS file recovery) README, Jonas Plum — https://raw.githubusercontent.com/cugu/afro/master/README.md
