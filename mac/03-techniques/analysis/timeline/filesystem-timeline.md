---
title: "파일 시스템 타임라인"
parent: "타임라인 작성"
grand_parent: "기법 · 분석"
nav_order: 2040
---

# 파일 시스템 타임라인 (APFS·FSEvents)

APFS 아이노드에 남은 네 가지 시각과 디렉터리 항목의 추가 시각을 뽑아 시간순으로 합치고, 시각 칸이 없는 FSEvents 기록을 순서 정보로 끼워 넣어 파일 시스템 쪽 타임라인을 만드는 방법을 다룹니다.

## 언제 쓰나

어떤 파일이 언제 생기고 바뀌었는지, 같은 시간대에 어떤 폴더에서 무엇이 일어났는지를 보려 할 때 가장 먼저 만드는 타임라인입니다. 파일 시각은 볼륨 메타데이터에 있어서 앱이 따로 기록을 남기지 않아도 얻을 수 있고, 통합 로그나 앱 데이터에서 나온 사건을 이 위에 겹쳐 보게 됩니다. APFS 볼륨 구조 자체는 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md) 에서, 구형 볼륨은 [HFS+ 구조 (HFS+)](../../../01-foundations/disk-volume/hfs-plus.md) 에서, FSEvents 레코드 형식은 [파일 시스템 이벤트 (FSEvents)](../../../02-artifacts/filesystem/fsevents/index.md) 에서 다루고, 이 페이지는 그 값들을 타임라인으로 엮는 절차만 봅니다.

## 타임라인에 쓰는 APFS 시각

APFS 는 파일마다 아이노드 값(`j_inode_val_t`)에 시각 네 개를 적고, 폴더 안의 항목마다 디렉터리 레코드 값(`j_drec_val_t`)에 그 항목이 추가된 시각을 따로 적습니다 [1]. 다섯 칸 모두 1970-01-01 00:00:00 UTC 기준 나노초를 부호 있는 64비트 정수로 담고, 값을 설정하지 않았으면 0 입니다 [1].

| 구조 | 오프셋 | 칸 | 뜻 |
|---|---|---|---|
| `j_inode_val_t` | 16 | `create_time` | 생성 시각 |
| `j_inode_val_t` | 24 | `mod_time` | 수정 시각 |
| `j_inode_val_t` | 32 | `change_time` | 아이노드 변경 시각 |
| `j_inode_val_t` | 40 | `access_time` | 접근 시각 |
| `j_drec_val_t` | 8 | `date_added` | 디렉터리 항목이 추가된 시각 |

볼륨 단위로는 볼륨 슈퍼블록의 `apfs_unmount_time`(오프셋 64, 마지막 마운트 해제 시각)과 `apfs_last_mod_time`(오프셋 256, 수정 시각)이 같은 형식으로 남고 [1], 스냅샷 메타데이터 값(`j_snap_metadata_val_t`)에는 오프셋 16 에 생성 시각, 오프셋 24 에 마지막 수정 시각이 1970 기준 부호 있는 정수로 들어 있습니다 [1]. 생성 시각은 나노초이지만 수정 시각의 단위는 공개 자료에 나오지 않아서, 도구가 내놓은 값을 다른 시각과 비교해 단위를 먼저 맞춰 봅니다.

HFS+ 볼륨은 칸 구성이 다르고, 카탈로그 파일·폴더 레코드에 createDate, contentModDate, attributeModDate, accessDate, backupDate 가 있습니다 [3]. Mac OS X 의 BSD API 는 attributeModDate 를 파일의 변경 시각(ctime)으로 쓰고, accessDate 는 POSIX 대응용이라서 옛 Mac OS 가 만든 파일에서는 0 으로 남습니다 [3]. 폴더의 contentModDate 는 그 안의 파일이나 폴더를 만들거나 지우거나 옮겨 넣고 뺄 때 바뀝니다 [3].

## 절차

1. **볼륨마다 파일 시스템과 macOS 버전을 적어 둡니다.** 같은 맥이라도 내장 볼륨은 APFS, 외장 디스크는 HFS+ 일 수 있어서, 볼륨마다 어떤 칸이 있고 어떤 기준 시점을 쓰는지가 달라집니다.

2. **아이노드 시각을 나노초까지 그대로 뽑습니다.** 파일마다 경로, 아이노드 번호, 네 시각, `date_added` 를 한 줄로 내보내고, 원래 정수값도 함께 남겨 둡니다. 변환한 문자열만 남기면 나중에 초 아래 자리나 0 값을 다시 확인할 수 없습니다.

   정수값은 10억으로 나눈 몫이 1970 기준 초이고 나머지가 나노초입니다. 명세로 만든 예시로 `1704067200123456789` 는 `1704067200` 초와 `123456789` 나노초로 나뉘어 2024-01-01 00:00:00.123456789 UTC 가 됩니다.

3. **값이 0 인 칸을 따로 표시합니다.** 0 은 설정하지 않은 값이라서 [1] 변환하면 1970-01-01 00:00:00 UTC 가 나오는데, 이 날짜를 실제 사건으로 타임라인에 올리지 않습니다.

4. **볼륨 시각과 스냅샷 시각을 기준선으로 넣습니다.** 마지막 마운트 해제 시각과 스냅샷 생성 시각은 파일 하나가 아니라 볼륨 전체의 시점을 알려 줘서, 파일 시각이 그 시점보다 앞인지 뒤인지 가를 때 씁니다. 스냅샷끼리 내용을 비교하는 방법은 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../snapshot-diff.md) 에서 봅니다.

5. **FSEvents 기록을 순서 정보로 겹칩니다.** FSEvents 레코드에는 경로·이벤트 ID·플래그가 있고, FSEvents 페이지에서 정리한 대로 macOS 10.13 부터 노드 ID 가, macOS 14 Sonoma 부터 UID 가 더해졌지만 시각 칸은 없습니다. 그래서 FSEvents 는 "어느 경로에 어떤 변경이 어떤 순서로 있었나" 를 채우고, 시각은 같은 경로의 파일 시각이나 다른 출처로 채웁니다. 이벤트 ID 순서와 날짜 어림 방법은 [파일 시스템 이벤트 (FSEvents)](../../../02-artifacts/filesystem/fsevents/index.md) 에서 다룹니다.

6. **한 기준 시각으로 맞춥니다.** HFS+ 볼륨이나 앱 데이터처럼 기준 시점이 다른 출처를 섞기 전에 모두 UTC 한 기준으로 바꾸고, 방법은 [시각 정규화 (Time Normalization)](time-normalization.md) 를 따릅니다.

7. **조작 흔적을 점검합니다.** 생성 시각과 수정 시각이 똑같거나 나노초 자리가 0 인 파일처럼 눈에 띄는 줄은 [시각 조작 흔적 (Timestomping)](timestomping.md) 의 기준으로 다시 봅니다.

> 그림 자리: 한 파일의 생성·수정·변경·접근·추가 시각을 시간 축에 찍고, 같은 경로의 FSEvents 이벤트를 순서만 있는 막대로 겹쳐 보인 그림

## 도구

살아 있는 시스템에서는 `stat` 으로 네 시각을 볼 수 있고, 형식 문자 `a` 가 마지막 접근(`st_atime`), `m` 이 마지막 수정(`st_mtime`), `c` 가 아이노드 마지막 변경(`st_ctime`), `B` 가 아이노드 생성 시각(`st_birthtime`)입니다 [2]. `-t` 로 strftime(3) 형식을 줘서 시각 표시 모양을 바꿀 수 있고, 기본 형식은 `"Jul  8 10:26:03 2004"` 처럼 초까지만 보여 줍니다 [2]. 조사 대상 맥에서 직접 명령을 돌리는 일은 [라이브 대응 (Live Response)](../../process-acquisition/live-response/index.md) 의 순서에 맞춥니다.

이미지에서는 APFS 를 직접 읽는 공개 도구로 아이노드와 디렉터리 레코드를 뽑습니다. 도구마다 `date_added` 나 스냅샷 시각을 내보내는지, 나노초를 잘라 내는지가 다를 수 있어서, 결과를 쓰기 전에 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md) 방식으로 알려진 값과 한 번 맞춰 봅니다.

## 함정과 한계

어떤 동작이 어느 칸을 바꾸는지는 공개 자료에 정리돼 있지 않아서, 복사·이동·압축 해제 같은 동작으로 결론을 내리려면 같은 macOS 버전에서 재현해 확인합니다. 파일을 다른 폴더로 옮기면 `date_added` 가 새로 바뀌는지, Finder 의 "추가된 날짜" 나 스포트라이트의 `kMDItemDateAdded` 가 이 칸과 같은 값인지도 재현으로 확인합니다.

FSEvents 의 노드 ID 가 APFS 아이노드 번호와 같은 값인지는 공개 자료로 정해지지 않아서, 두 기록은 노드 ID 가 아니라 경로로 이어 붙이고 그렇게 했다고 적어 둡니다. HFS+ 시각은 초 단위라서 [3] APFS 파일과 나란히 놓으면 초 아래 자리가 없는 것이 정상이고, 이 차이를 조작 단서로 읽지 않습니다.

## 결과를 어떻게 해석하나

| 칸 | 말해 주는 것 | 말해 주지 못하는 것 |
|---|---|---|
| `create_time` | 이 볼륨의 아이노드에 적힌 생성 시각 | 파일이 처음 만들어진 곳이나 다른 맥에서 만든 시각 |
| `mod_time` | 아이노드에 적힌 내용 수정 시각 | 누가, 어떤 앱으로 바꿨는지 |
| `change_time` | 아이노드 정보가 마지막으로 바뀐 시각 | 무엇이 바뀌었는지 |
| `access_time` | 아이노드에 적힌 접근 시각 | 사람이 파일을 열어 봤는지 |
| `date_added` | 그 폴더에 항목이 추가된 시각 | 파일이 어디서 왔는지 |
| FSEvents 이벤트 | 경로에 어떤 변경이 어떤 순서로 기록됐는지 | 사건이 일어난 시각 |

보고서에는 "이 파일의 APFS 아이노드 수정 시각은 2024-01-01 00:00:00.123456789 UTC 로 기록돼 있다" 처럼 어느 칸의 값인지와 기준 시간대를 함께 적고, 파일이 어디서 왔는지는 [이 파일은 어디서 왔나 (File Origin)](../../../04-scenarios/activity/file-origin.md) 처럼 다른 기록으로 따로 확인합니다.

## 참고 문헌

1. libyal libfsapfs — Apple File System (APFS) format — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
2. stat(1) man 페이지 — https://keith.github.io/xcode-man-pages/stat.1.html
3. Apple Technical Note TN1150, HFS Plus Volume Format — https://developer.apple.com/library/archive/technotes/tn/tn1150.html
