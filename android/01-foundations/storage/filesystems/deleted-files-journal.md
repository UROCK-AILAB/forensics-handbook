---
title: "지운 파일과 저널"
parent: "파일 시스템"
grand_parent: "기반 · 저장 구조"
nav_order: 70
---

# 지운 파일과 저널 (Deleted Files·Journal)

파일을 지운 뒤에도 ext4 에서는 inode 의 삭제 시각과 저널 (jbd2) 에, F2FS 에서는 무효 블록과 체크포인트 사본에 흔적이 남을 수 있고, 이 페이지는 그 흔적이 어디에 어떤 모양으로 남는지와 암호화가 복구를 어디까지 막는지를 다룹니다.

## 이 흔적을 쓰는 곳

지운 대화·사진을 찾거나 누가 증거를 없애려 했는지 따질 때 파일 시스템 수준의 흔적을 봅니다. 조사 흐름은 [지운 대화와 사진 찾기](../../../04-scenarios/activity/deleted-content.md)와 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md)에서, 복구 절차는 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md)에서 다루고, 이 페이지는 그 밑에 깔린 파일 시스템 구조만 설명합니다. 앱 DB 안에서 지운 레코드는 [SQLite 데이터베이스](../../data-formats/sqlite/index.md) 쪽 이야기입니다.

두 파일 시스템의 흔적을 나란히 놓으면 아래와 같습니다.

| | ext4 | F2FS |
|---|---|---|
| 일관성을 지키는 방식 | 저널 (jbd2) | 체크포인트와 롤포워드 복구. jbd2 같은 저널은 없음 |
| 지운 파일 쪽에 남는 값 | inode 의 i_dtime(삭제 시각) | 무효 블록, SIT 비트맵, SSA 요약 항목 |
| 옛 상태가 남는 곳 | 저널 안 트랜잭션 | 두 벌 중 이전 체크포인트가 가리키는 NAT·SIT 사본 |
| 흔적이 사라지는 계기 | 검체에서 확인 | GC 가 세그먼트를 회수하거나 discard 가 켜져 있어 저장 장치에 해제를 알릴 때. 기본인 `mode=adaptive` 에서는 새 쓰기가 무효 블록 자리를 다시 쓸 수도 있음 |

## ext4 의 저널 (jbd2)

### 저널이 놓이는 곳

ext4 저널은 보통 8번 inode 에 들어 있고, 저널 inode 의 앞 68바이트는 ext4 슈퍼블록에도 복사돼 있습니다. 저널을 다른 장치에 두는 외부 저널이면 슈퍼블록의 s_journal_inum 이 0 이고 s_journal_uuid 가 채워져 있습니다.

### 데이터 모드

저널에 무엇이 들어가는지는 마운트할 때 고르는 데이터 모드에 달려 있습니다.

| 모드 | 저널을 거치는 것 |
|---|---|
| `data=ordered`(기본) | 파일 시스템 메타데이터만 |
| `data=journal` | 데이터와 메타데이터 모두 |
| `data=writeback` | 메타데이터만. 메타데이터를 쓰기 전에 바뀐 데이터 블록을 먼저 내려 쓰지 않음 |

기본 모드에서는 메타데이터만 저널을 거쳐서, 저널에서 찾을 만한 것은 파일 내용이 아니라 inode 테이블·디렉터리·비트맵 같은 메타데이터 쪽이라고 해석할 수 있습니다. 다만 저널에 블록이 통째 사본으로 남는지 차이만 남는지, 저널이 한 바퀴 돌아 덮어써진 뒤에도 옛 트랜잭션이 남는지는 검체에서 확인합니다. Android 기기가 ext4 를 어떤 데이터 모드로 마운트하는지도 기기의 마운트 정보에서 확인합니다.

### 저널 블록

저널 블록은 12바이트 머리로 시작하고, 머리에는 h_magic, h_blocktype, h_sequence 가 들어 있습니다. h_magic 은 `0xC03B3998` 이고, h_sequence 는 그 블록이 속한 트랜잭션 ID 입니다. h_blocktype 값은 아래와 같습니다.

| h_blocktype | 블록 |
|---|---|
| 1 | 디스크립터 블록 |
| 2 | 커밋 블록 |
| 3 | 저널 슈퍼블록 v1 |
| 4 | 저널 슈퍼블록 v2 |
| 5 | revoke 블록(취소 기록) |

저널 슈퍼블록에는 저널을 읽어 나갈 때 필요한 값이 들어 있습니다.

| 칸 | 뜻 |
|---|---|
| s_blocksize | 저널 블록 크기 |
| s_maxlen | 저널 전체 블록 수 |
| s_first | 로그가 들어 있는 첫 블록 |
| s_sequence | 로그에서 기대하는 첫 커밋 ID |
| s_start | 로그가 시작하는 블록 |

커밋 블록에는 h_commit_sec(유닉스 에포크부터 센 초)와 h_commit_nsec(나노초)가 있어서 트랜잭션을 커밋한 시각을 알 수 있습니다. 에포크 기준 값이라 시간대가 들어 있지 않고, 바꾸는 법은 [시각 값](../../value-decoding/time-values.md)에서 다룹니다.

revoke 블록은 특정 블록을 다시 재생하지 말라는 기록이고, 메타데이터 블록이 해제된 뒤 파일 데이터 블록으로 다시 할당된 경우에 씁니다. fast commit 은 메타데이터를 다시 만드는 데 필요한 최소한의 차이만 TLV(tag-length-value) 형태로 저장합니다.

### 읽는 법

jbd2 의 모든 칸은 빅 엔디언으로 적혀서 리틀 엔디언인 ext4 와 반대이니, 헥스로 읽을 때 바이트 순서를 바꿔 읽지 않도록 주의합니다.

1. 슈퍼블록에서 저널 inode 번호를 확인하고(보통 8번), 외부 저널이면 s_journal_uuid 로 저널 장치를 찾습니다.
2. 저널에서 h_blocktype 이 3 또는 4 인 저널 슈퍼블록을 찾아 s_first, s_start, s_sequence 를 얻습니다.
3. 로그 영역에서 h_magic 이 `0xC03B3998` 인 블록을 찾아 h_blocktype 과 h_sequence 로 트랜잭션별로 묶습니다.
4. 커밋 블록에서 h_commit_sec·h_commit_nsec 를 읽어 트랜잭션마다 커밋 시각을 붙이고, revoke 블록에 적힌 블록은 따로 표시해 둡니다.

아래는 명세대로 만든 예시이고 특정 검체에서 나온 값이 아닙니다. 커밋 블록 머리를 해석하면 이런 모양이 됩니다.

```
h_magic       = 0xC03B3998   저널 블록 표시
h_blocktype   = 2            커밋 블록
h_sequence    = 트랜잭션 ID
h_commit_sec  = 유닉스 에포크부터 센 초
h_commit_nsec = 나노초
```

## ext4 에서 지운 파일

지운 파일의 inode 에는 i_dtime 에 삭제 시각이 에포크 초로 기록되지만, orphan inode 에서는 이 칸을 다른 용도로 씁니다. 이 함정과 inode 의 나머지 시각 칸은 [ext4 구조](ext4.md)에서 다룹니다.

ext4 가 파일을 지울 때 inode 의 extent 정보까지 지우는지, 디렉터리 항목을 지우면 앞 항목이 늘어나 이름이 남는지는 공개 문서에 설명이 없어 검체에서 확인합니다.

## F2FS 에서 지운 파일

F2FS 는 블록을 제자리에 덮어쓰지 않아서, 지운 파일과 내용을 고친 파일의 옛 블록이 무효 블록으로 디스크에 남습니다. 이 블록은 GC 가 그 세그먼트를 회수하거나 `discard` 가 켜져 있어 저장 장치에 해제를 알릴 때 사라집니다. 기본 할당 방식인 `mode=adaptive` 는 Main 영역에 임의 쓰기를 허용해서, GC 전이라도 새 쓰기가 무효 블록 자리를 다시 쓸 수 있습니다(임의 쓰기를 막는 쪽은 `mode=lfs`). 그래서 무효 블록이 얼마나 오래 남는지는 장담할 수 없습니다. 구조는 [F2FS 구조](f2fs.md)에서 다룹니다.

블록이 유효한지는 SIT 의 비트맵에, 블록이 어느 파일의 것인지는 SSA 의 요약 항목에 있습니다. 이 구조로 보면 무효 블록의 원래 주인을 SSA 로 따라갈 수 있을 것으로 보이지만, 이를 복구 절차로 정리한 공개 자료가 없어 검체로 확인해야 합니다. 체크포인트를 두 벌 두기 때문에 이전 체크포인트가 가리키는 NAT·SIT 사본도 남을 수 있고, 이 사본을 복구에 쓸 수 있는지도 마찬가지로 검체로 확인합니다.

백그라운드 GC 는 기기가 한가할 때 커널 스레드가 돌려서, 기기를 켠 채 두는 동안에도 무효 블록이 회수될 수 있습니다. 전원 상태를 어떻게 다룰지는 [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md)에서 다룹니다.

## 암호화가 복구에 주는 영향

Android 의 파일 기반 암호화는 fscrypt 로 파일 내용과 이름을 암호화해서, 지운 파일의 블록이 남아 있어도 키 없이는 암호문입니다. fscrypt 가 가리지 않는 파일 크기·권한·시각도 Android 11 이상으로 출시된 기기는 메타데이터 암호화로 블록 단위로 암호화해서, 전원이 꺼진 기기의 원본 이미지에서는 파일 시스템 구조 자체를 키 없이 읽기 어렵다고 해석할 수 있습니다. 암호화 방식과 키 구조는 [저장 공간 암호화](../encryption/index.md)에서 다룹니다.

fscrypt 에서 키를 제거할 때(FS_IOC_REMOVE_ENCRYPTION_KEY) 사용 중인 파일의 파일별 키는 제거되거나 지워지지 않습니다. 사용자나 앱을 지울 때 Android 가 CE·DE 키를 파기하는지, TRIM 으로 해제한 블록을 저장 장치(UFS)가 0 으로 돌려주는지는 검체에서 확인합니다.

## 함정

F2FS 의 무효 블록을 곧바로 "지운 파일" 로 보고하지 않습니다. 내용을 고친 파일의 옛 버전도 똑같이 무효 블록으로 남아서, 무효 블록 하나로는 삭제와 수정을 가를 수 없습니다.

저널 커밋 시각은 트랜잭션을 커밋한 시각이고, 그 트랜잭션 안의 변경을 일으킨 사용자 동작이 언제 있었는지를 따로 적은 칸은 없습니다. 보고서에는 "이 시각에 커밋된 트랜잭션에 이 메타데이터 변경이 있다" 처럼 기록이 말하는 만큼만 씁니다.

암호화된 기기의 원본 이미지에서 시그니처로 조각을 찾으면 암호문 조각만 나올 수 있습니다. 복구 결과를 해석하기 전에 기기의 암호화 방식과 확보 방법부터 적어 둡니다.

## 도구

공개 도구가 jbd2 저널이나 F2FS 무효 블록을 어디까지 보여 주는지는 도구마다 먼저 확인합니다. 도구가 내놓은 복구 결과는 [도구 검증](../../../03-techniques/reporting/tool-validation.md)의 방법으로 먼저 확인하고, 저널은 위 "읽는 법" 순서대로 블록 머리를 헥스로 한 번 대조합니다.

## 참고 문헌

- ext4 Journal (jbd2) — docs.kernel.org, https://docs.kernel.org/filesystems/ext4/journal.html
- ext4 Index Nodes — docs.kernel.org, https://docs.kernel.org/filesystems/ext4/inodes.html
- General Filesystem Information: F2FS — docs.kernel.org, https://docs.kernel.org/filesystems/f2fs.html
- Filesystem-level encryption (fscrypt) — docs.kernel.org, https://docs.kernel.org/filesystems/fscrypt.html
- File-based encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/file-based
- Metadata encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/metadata
