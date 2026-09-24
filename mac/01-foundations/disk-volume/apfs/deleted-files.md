---
title: "지운 파일과 옛 체크포인트"
parent: "APFS 구조"
grand_parent: "기반 · 디스크·볼륨"
nav_order: 80
---

# 지운 파일과 옛 체크포인트 (Deleted Files·Old Checkpoints)

APFS는 디스크의 객체를 제자리에서 고치지 않고 고친 사본을 늘 새 위치에 쓰며 [1], 과거 시점의 컨테이너 상태를 담은 슈퍼블록 사본도 여러 개 남기기 때문에 [1], 파일을 지운 뒤에도 옛 슈퍼블록과 옛 B-트리 노드를 따라가 지운 파일의 메타데이터와 내용을 찾을 단서가 남아 있을 수 있습니다.

체크포인트 영역과 객체 맵, B-트리 노드의 구조는 [객체와 체크포인트 (Object·Checkpoint)](object-checkpoint.md)에, 스냅숏 안에 남은 파일은 [스냅숏 (Snapshots)](snapshots.md)에 있고, 이 페이지는 삭제와 관련된 구조와 옛 상태를 읽는 순서만 다룹니다. 여러 파일 시스템에 공통인 복구 방법은 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)에서, 조사 흐름은 [지운 파일의 흔적 찾기 (Deleted File Traces)](../../../04-scenarios/activity/deleted-file-traces.md)에서 다룹니다.

## 이 구조를 쓰는 곳

사용자가 휴지통을 비운 파일, 증거를 없애려고 지운 파일, 운영체제가 저절로 정리한 파일은 모두 여기서 설명하는 구조를 거쳐 사라집니다. 지운 흔적을 판단하는 조사는 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)에서, 휴지통에 남는 기록은 [휴지통 (.Trash)](../../../02-artifacts/file-folder-usage/trash.md)에서 이어 봅니다.

## 형식이 남기는 것

### 옛 슈퍼블록과 옛 노드

디스크의 객체는 제자리에서 고치지 않으므로 [1], 파일을 지우거나 바꾸면 B-트리 노드의 새 사본이 다른 블록에 생기고 옛 노드 사본은 그 공간을 다시 쓰기 전까지 디스크에 남을 수 있습니다. 이 점은 [1]의 규칙에서 끌어낸 해석이고, 옛 노드가 얼마나 오래 남는지는 참고 문헌으로 확인하지 못했습니다.

컨테이너 슈퍼블록 사본은 여러 개이고 사본마다 과거 한 시점의 컨테이너 상태를 담으며 [1], 체크포인트 서술자 영역이 링 버퍼라서 최신 체크포인트 앞에 옛 슈퍼블록과 옛 체크포인트 맵이 남아 있습니다 [1][2]. [2]도 서술자 영역 안의 옛 체크포인트 맵과 옛 컨테이너 슈퍼블록을 컨테이너의 구성 요소로 적습니다. 가상 객체를 찾을 때는 트랜잭션 ID로 어느 시점의 사본인지 정하지만 [1], 스냅숏이 없는 볼륨에서도 옛 xid의 매핑이 객체 맵에 남는지는 확인하지 못했습니다.

### 지워진 표시

객체 맵 값의 플래그 `OMAP_VAL_DELETED` (0x1)는 객체가 지워졌고 그 매핑이 자리표시라는 뜻입니다 [1]. B-트리 안에서 항목을 지워 생긴 빈 곳과 값 없는 키(ghost)를 다루는 규칙은 [객체와 체크포인트 (Object·Checkpoint)](object-checkpoint.md)에 있습니다.

### 리퍼와 공간 관리자

리퍼 (reaper)는 큰 객체를 여러 트랜잭션에 걸쳐 지우는 장치로 컨테이너에 하나 있고, 중간에 멈춰도 이어서 지울 수 있도록 상태를 저장합니다 [1].

공간 관리자 (space manager)는 해제된 블록을 free queue B-트리에 넣고, 이 트리는 트랜잭션 ID로 먼저 정렬한 다음 물리 주소로 정렬합니다 [1]. 큐는 `SFQ_IP` (0), `SFQ_MAIN` (1), `SFQ_TIER2` (2) 세 개이고, free queue에서 값 없는 키(ghost)는 한 블록짜리 빈 익스텐트를 뜻합니다 [1]. 아직 free queue에 들어 있는 블록은 최근 트랜잭션에서 해제된 블록으로 볼 수 있지만, 이 점은 [1]에 명시되지 않은 해석입니다.

볼륨 슈퍼블록의 `apfs_total_blocks_freed` 는 블록을 해제할 때마다 늘어나는 누적값이고 [1], 해제 시각은 알려 주지 않습니다.

### 참조 수와 복제

물리 익스텐트의 `refcnt` 가 0이 되어야 그 익스텐트를 지울 수 있고, 복제된 적이 있는 파일(`INODE_WAS_EVER_CLONED`)을 지울 때는 참조 수를 확인해야 합니다 [1]. 이 규칙대로라면 복제본이 남아 있는 한 원본을 지워도 데이터 블록은 풀리지 않고, 이 점은 [1]의 규칙에서 끌어낸 해석입니다. 복제의 구조는 [복제·희소·압축 파일 (Clone·Sparse·Compression)](clone-sparse-compression.md)에서 다룹니다.

### 정리 대상 파일

아이노드 플래그 `INODE_IS_PURGEABLE` (0x80000)가 켜진 파일은 다음 정리(purge) 때 지워질 파일이고, 정리는 운영체제의 사용자 공간 쪽이 요청합니다 [1]. 사용자가 지우지 않았어도 운영체제가 이런 파일을 없앨 수 있다는 뜻이라서, 사라진 파일을 모두 사람의 삭제로 보지 않습니다.

## SSD, TRIM, 암호화

APFS는 TRIM을 지원하고, TRIM 명령은 파일 삭제나 여유 공간 회수와 비동기로, 메타데이터 변경이 저장된 뒤에만 보냅니다 [3]. 이 규칙대로라면 삭제 직후 짧은 동안에는 TRIM이 아직 가지 않았을 수 있고, 이 점은 필자의 해석입니다. TRIM을 받은 블록을 읽으면 무엇이 나오는지는 참고 문헌으로 확인하지 못했습니다. APFS는 플래시와 SSD에 맞춰 설계했지만 HDD와 외장 저장소에도 쓸 수 있습니다 [3].

하드웨어 암호화를 쓰는 기기의 내장 저장소에는 커널만 접근할 수 있고, 2020년 판인 [1]은 그런 기기로 T2 칩 Mac과 iOS 기기를 듭니다 [1]. 볼륨 키백은 볼륨 UUID로 감싸 두기 때문에 볼륨 슈퍼블록을 안전하게 지우면 그 볼륨의 암호화된 내용을 읽을 수 없게 됩니다 [1]. 암호화된 볼륨을 다루는 방법은 [파일볼트 (FileVault)](../../protection/filevault/index.md)와 [암호화된 증거 다루기 (Encrypted Evidence)](../../../03-techniques/analysis/encrypted-evidence/index.md)에 있습니다.

## 읽는 법

### 헥스로 한 번

옛 슈퍼블록을 찾을 때는 블록 머리의 객체 헤더와 매직으로 알아봅니다. 아래 바이트는 실제 검체가 아니라 명세 [1][2]의 정의에 맞춰 만든 예시이고, `cc` 는 체크섬 자리, `..` 은 이 설명에서 쓰지 않는 칸입니다.

```
블록 안 오프셋 (컨테이너 슈퍼블록)
0000  cc cc cc cc cc cc cc cc 01 00 00 00 00 00 00 00
0010  2A 01 00 00 00 00 00 00 01 00 00 80 .. .. .. ..
0020  4E 58 53 42 ..                                    "NXSB"

블록 안 오프셋 (볼륨 슈퍼블록)
0010  .. .. .. .. .. .. .. .. 0D 00 00 00 .. .. .. ..
0020  41 50 53 42 ..                                    "APSB"
```

컨테이너 슈퍼블록은 오프셋 8의 객체 ID가 `OID_NX_SUPERBLOCK` 인 1이고, 오프셋 24의 형식 값이 0x80000001, 오프셋 32의 매직이 "NXSB"입니다 [1][2]. 오프셋 16의 xid 0x12A(298)는 이 객체를 마지막으로 고친 트랜잭션 ID이고 [1], 같은 컨테이너에서 찾은 사본들을 xid 순서로 늘어놓으면 과거 상태의 순서가 됩니다. 볼륨 슈퍼블록은 형식 값이 보통 0x0000000d이고 스냅숏에 딸린 것은 0x4000000d이며, 매직은 "APSB"입니다 [1][2]. 매직만 맞는 블록은 우연일 수 있으므로 Fletcher-64 체크섬까지 맞는지 확인하고, 계산법은 [객체와 체크포인트 (Object·Checkpoint)](object-checkpoint.md)에 있습니다.

### 절차

1. 원본을 쓰기 방지한 상태로 이미지를 만들고, 이미지에서만 작업합니다.
2. 체크포인트 서술자 영역에서 매직과 체크섬이 맞는 컨테이너 슈퍼블록을 모두 모아 xid 순서로 늘어놓습니다. 영역이 연속이 아니거나 링 버퍼의 끝을 넘는 경우는 [객체와 체크포인트 (Object·Checkpoint)](object-checkpoint.md)의 규칙대로 읽습니다.
3. 옛 슈퍼블록마다 마운트 순서와 같은 길로 컨테이너 객체 맵, 볼륨 슈퍼블록, 파일 시스템 트리를 따라갑니다.
4. 옛 트리에는 있지만 현재 트리에는 없는 아이노드와 디렉터리 항목을 삭제 또는 이동 후보로 적습니다. 이름이 바뀐 파일도 같은 모양으로 보이므로 후보를 곧바로 삭제로 부르지 않습니다.
5. 후보 파일의 익스텐트가 가리키는 물리 블록을 현재 트리의 다른 파일이 쓰고 있는지 확인합니다. 다른 파일이 쓰고 있다면 그 블록의 내용은 지운 파일의 내용이 아닐 수 있습니다.
6. 스냅숏이 있으면 [스냅숏 (Snapshots)](snapshots.md)의 방법으로 같은 비교를 합니다.
7. 찾은 결과마다 근거가 된 슈퍼블록의 위치와 xid를 기록해 두어 다른 분석가가 같은 결과를 다시 얻을 수 있게 합니다.

## 포렌식에서 중요한 점

옛 슈퍼블록에서 따라간 트리에 어떤 파일이 있다면, 그 xid 시점에 파일 시스템 메타데이터에 그 파일이 있었다는 것까지는 말할 수 있습니다. 누가 지웠는지, 정확히 언제 지웠는지는 이 구조에 적히지 않고 xid는 순서만 알려 주므로, 시각이 필요하면 [APFS의 시각 네 가지 (Create·Modify·Change·Access)](timestamps.md)의 시각 칸과 [파일 시스템 이벤트 (FSEvents)](../../../02-artifacts/filesystem/fsevents/index.md) 같은 다른 기록으로 좁힙니다. 보고서에는 "xid 298 시점의 파일 시스템 메타데이터에 이 경로의 파일이 있었고 현재 트리에는 없다"처럼 기록이 말하는 만큼만 씁니다.

정리 대상 파일처럼 운영체제가 스스로 없애는 데이터가 있고 [1], 로컬 스냅숏도 저절로 지워지므로([스냅숏 (Snapshots)](snapshots.md) 참고), 사라졌다는 사실만으로 사용자의 삭제 행위를 말하지 않습니다. 비정상 종료 뒤 무효가 된 체크포인트에만 남은 변경도 있을 수 있고, 이 경우는 [객체와 체크포인트 (Object·Checkpoint)](object-checkpoint.md)에서 다룹니다.

## 함정

블록 0의 컨테이너 슈퍼블록 사본은 옛것일 수 있으므로 [1], 이 사본만 보고 현재 상태나 과거 상태를 정하지 않습니다. 반대로 옛 슈퍼블록을 따라간 결과를 현재 상태로 착각하지 않도록, 결과마다 어느 xid에서 나왔는지 함께 적습니다.

실제 복구 성공률이나 지운 뒤 옛 노드가 얼마나 오래 남는지 같은 수치는 참고 문헌으로 확인하지 못했습니다. 복구 결과가 없다고 해서 지운 파일이 없었다고 결론 내리지 않습니다.

하드웨어 암호화를 쓰는 내장 저장소에서 칩을 떼어 내 원시 블록을 읽는 방식으로는 비할당 영역을 해석할 수 없을 것으로 보이지만, 이 점도 참고 문헌으로 확인하지 못한 해석입니다.

## 도구

afro는 다른 도구가 찾지 못하는 지운 파일을 APFS에서 복구한다고 밝힌 공개 도구이고, 볼륨마다 파일 시스템의 여러 버전을 번호 붙은 폴더로 뽑아내며 mactime 타임라인에 넣을 body file도 만듭니다 [4]. 결과 폴더 이름에 `carve_apsb` 가 보여 볼륨 슈퍼블록을 카빙하는 것으로 보이지만, 무엇을 어떻게 카빙하는지는 README에 설명이 없고 지금은 유지보수하지 않는 도구입니다 [4]. afro README는 J. Plum과 A. Dewald의 "Forensic APFS File Recovery", K. H. Hansen과 F. Toolan의 "Decoding the APFS file system"을 인용하지만 [4], 두 논문의 복구 방법은 이 페이지에서 원문으로 확인하지 않았습니다.

mac_apt의 TRASH 플러그인은 `.Trash` 폴더의 `.DS_Store` 파일에서 지운 파일과 폴더의 메타데이터를 읽습니다 [5]. 이 파일의 구조는 [폴더 보기 파일 (.DS_Store)](../../../02-artifacts/file-folder-usage/ds-store.md)에서 다룹니다.

## 참고 문헌

1. Apple, Apple File System Reference (2020-06-22 판, PDF) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
2. Joachim Metz, libfsapfs — Apple File System (APFS) 형식 문서 (개정 0.0.18, 2026년 8월) — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
3. Apple, Apple File System Guide — Frequently Asked Questions (보관 문서, 2018-06-04) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/FAQ/FAQ.html
4. afro (APFS file recovery) README, Jonas Plum — https://raw.githubusercontent.com/cugu/afro/master/README.md
5. mac_apt README, Yogesh Khatri (v1.33.2) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/README.md
