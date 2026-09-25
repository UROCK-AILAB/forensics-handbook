---
title: "파일 시스템"
parent: "기반 · 저장 구조"
nav_order: 40
has_children: true
has_toc: false
---

# 파일 시스템 (ext4·F2FS)

## 한 줄 요약

Android 의 사용자 데이터 파티션은 ext4 와 F2FS 가운데 하나로 만들어지고, 이 묶음은 두 파일 시스템의 구조와 지운 파일이 남기는 흔적을 다룹니다.

## 왜 중요한가

앱 DB 와 사진, 내려받은 파일은 모두 사용자 데이터 파티션(userdata)의 파일 시스템 위에 놓입니다. 파일을 앱 쪽에서 읽을 때는 파일 시스템이 드러나지 않지만, 파일 생성 시각을 따지거나 지운 파일을 찾으려면 그 아래 파일 시스템이 무엇인지부터 알아야 합니다. ext4 와 F2FS 는 일관성을 지키는 방식과 옛 데이터가 남는 자리가 서로 달라서, 한쪽에서 통하는 해석이 다른 쪽에서는 통하지 않습니다.

Android 의 파일 기반 암호화는 ext4 와 F2FS 를 지원하고(커널 3.18 이상), Android 10 이상으로 출시되는 기기는 이 암호화를 반드시 써야 합니다. 그래서 원본 이미지에서 파일 시스템을 읽을 때는 암호화가 어디까지 가리는지도 함께 따집니다. 자세한 내용은 [저장 공간 암호화](../encryption/index.md)에 있습니다.

실제 폰에서 adb 일반 셸 권한으로 /sdcard 최상위의 표준 폴더와 /sdcard/Android 아래 data·media·obb 폴더는 보였지만, 기기 관찰 메모에는 마운트 정보가 없어서 이 기기의 userdata 가 ext4 인지 F2FS 인지는 관찰하지 못했습니다. 폴더가 보인다는 것만으로는 그 아래 파일 시스템 종류를 알 수 없다는 점을 염두에 둡니다.

## 한눈에 보기

| | ext4 | F2FS |
|---|---|---|
| 기본 구조 | 블록 그룹마다 비트맵·inode 테이블을 고정 자리에 둠 | 볼륨을 SB·CP·SIT·NAT·SSA·Main 여섯 영역으로 나눈 로그 구조 |
| 일관성 | 저널 (jbd2) | 체크포인트 두 벌과 롤포워드 복구. jbd2 같은 저널은 없음 |
| 파일 시각 | inode 에 접근·변경·수정·삭제 시각 칸. 생성 시각은 128바이트보다 큰 inode 에만 있음 | 이 묶음의 출처로 칸 이름을 확인하지 못함 |
| 지운 파일 흔적 | i_dtime, 저널 안 트랜잭션 | 무효 블록, SIT 비트맵, SSA 요약 항목, 이전 체크포인트 사본 |
| 흔적이 사라지는 계기 | 이 묶음의 출처로 확인하지 못함 | GC 가 세그먼트를 회수하거나 discard 로 해제를 알릴 때, 또는 새 쓰기가 무효 블록 자리를 다시 쓸 때 |

Android 버전과 기기에 따라 달라지는 점은 아래와 같습니다.

| Android · 기기 | 파일 시스템 쪽 변화 |
|---|---|
| 10 이상 출시 기기 | 파일 기반 암호화 필수 |
| 11 이상 출시 기기 | 내부 저장소 메타데이터 암호화 필수. 커널 5.4 이상이면 /sdcard 에 SDCardFS 대신 FUSE 를 쓰고, 대소문자 무시를 파일 시스템 자체 기능으로 처리 |
| 삼성 갤럭시 | userdata 에 F2FS 를 쓰는지, 어느 모델·One UI 부터인지 확인하지 못함 |

## 읽는 순서

1. [ext4 구조 (ext4)](ext4.md) — 블록 그룹과 inode, 다섯 가지 시각 칸, 암호화된 inode 를 읽는 법
2. [F2FS 구조 (F2FS)](f2fs.md) — 여섯 영역과 node·디렉터리 구조, 제자리에 덮어쓰지 않는 쓰기 방식, 분석에 영향을 주는 마운트 옵션
3. [지운 파일과 저널 (Deleted Files·Journal)](deleted-files-journal.md) — ext4 저널 블록과 커밋 시각, F2FS 무효 블록, 암호화가 복구를 어디까지 막는지

## 함께 볼 페이지

- [파티션과 저장 영역](../partitions/index.md) — userdata 와 metadata 파티션이 어디 놓이는지
- [저장 공간 암호화](../encryption/index.md) — 파일 기반 암호화와 메타데이터 암호화
- [앱 데이터 폴더 구조](../app-data-layout.md) — 파일 시스템 위에 앱 폴더가 놓이는 방식
- [공용 저장 공간](../shared-storage.md) — /sdcard 와 FUSE
- [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) — 지운 데이터를 찾는 절차
- [지운 대화와 사진 찾기](../../../04-scenarios/activity/deleted-content.md) — 조사 시나리오

## 참고 문헌

- File-based encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/file-based
- Metadata encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/metadata
- Deprecate SDCardFS — Android Open Source Project, https://source.android.com/docs/core/storage/sdcardfs-deprecate
- General Filesystem Information: F2FS — docs.kernel.org, https://docs.kernel.org/filesystems/f2fs.html
- ext4 Global Structures — docs.kernel.org, https://docs.kernel.org/filesystems/ext4/globals.html
- ext4 Journal (jbd2) — docs.kernel.org, https://docs.kernel.org/filesystems/ext4/journal.html
- ext4 Index Nodes — docs.kernel.org, https://docs.kernel.org/filesystems/ext4/inodes.html
