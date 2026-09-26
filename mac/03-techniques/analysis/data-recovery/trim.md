---
title: "트림과 복구 한계"
parent: "삭제 데이터 복구"
grand_parent: "기법 · 분석"
nav_order: 2160
---

# 트림과 복구 한계 (TRIM)

요즘 Mac 내장 SSD 에서 지운 데이터 복구를 가로막는 세 가지, 곧 TRIM·상시 암호화·키 삭제가 어떻게 작동하는지와, 그 조건에서도 남는 복구 기회를 정리합니다.

## 언제 쓰나

삭제 데이터 복구에 들어가기 전에 무엇을 기대할 수 있는지 정하고, 보고서에 "복구하지 못했다" 를 쓸 때 그 이유를 설명하려고 씁니다. 이 페이지는 절차보다는 판단 기준을 다루고, 실제 복구 방법은 [APFS에서 지운 파일 (APFS)](apfs-deleted-files.md), [SQLite 레코드 되살리기 (SQLite)](sqlite-records.md), [카빙 (Carving)](carving.md) 에서 봅니다.

## 복구를 막는 세 가지

### TRIM

APFS 는 파일을 지우거나 빈 공간을 회수할 때 TRIM 명령을 비동기로 보내고, 그래서 메타데이터 변경이 안정된 저장소에 기록된 뒤에만 TRIM 이 실행됩니다 [1]. 파일을 지운 순간 바로 블록이 비워지지는 않지만, 메타데이터가 기록된 뒤 블록이 비워질 수 있다는 뜻입니다.

`trimforce` 는 서드파티 AHCI 연결 SSD 에서 TRIM 을 켜고 끄는 명령이고(enable/disable, 재부팅 필요), OS X 10.10.4 에서 처음 나왔습니다 [2]. TRIM 명령 뒤 가비지 컬렉션이 일어나면 데이터 복구가 매우 어렵습니다 [2]. Apple 순정 SSD 에서 TRIM 이 기본으로 켜져 있는지, 조사 대상 Mac 에서 TRIM 상태를 어디서 보는지, TRIM 한 자리를 읽으면 0 이 돌아오는지는 실제 기기에서 확인해야 합니다.

APFS 명세의 inode 플래그 INODE_ACTIVE_FILE_TRIMMED 는 "트림된 오버프로비저닝 파일" 이라는 뜻이라서 [4], 일반 파일 삭제 뒤의 TRIM 과는 다른 것으로 읽습니다.

### 상시 암호화

Apple 실리콘·T2 Mac 에서는 모든 APFS 볼륨을 기본으로 볼륨 암호화 키(VEK)로 만듭니다 [3]. FileVault 를 켜면 키 암호화 키(KEK)를 사용자 암호와 하드웨어 UID 로 보호하고, 켜지 않으면 VEK 를 Secure Enclave 의 하드웨어 UID 로만 보호합니다 [3]. Apple 실리콘 Mac 의 Data Protection 기본 등급(Class C)은 파일마다 따로 키를 쓰지 않고 FileVault 와 같은 모델로 볼륨 키를 쓰며, Class D 는 지원하지 않습니다 [3]. macOS 26.4 이후 Mac 은 FileVault 가 기본으로 켜지고, 사용자가 끌 수 있습니다 [3].

그래서 내장 저장소의 원시 블록은 키 없이 읽으면 의미 있는 내용이 보이지 않고, 지운 블록이 TRIM 되지 않고 남아 있어도 키가 있어야 읽힙니다. 키를 다루는 방법은 [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md) 와 [암호화된 증거 다루기 (Encrypted Evidence)](../encrypted-evidence/index.md) 에 있습니다.

### 키 삭제

볼륨을 지우면 Secure Enclave 가 그 볼륨의 VEK 를 안전하게 지웁니다 [3]. 모든 VEK 는 미디어 키로 한 번 더 감싸여 있고, 미디어 키가 없으면 복호할 수 없습니다 [3]. 즉시 원격 지우기(instant remote wipe)는 Apple 실리콘 Mac, T2 칩 Mac, 또는 FileVault 를 켠 Mac 에서 되고, 미디어 키를 안전하게 버리는 방식으로 이뤄집니다 [3].

Effaceable Storage 는 키를 담는 NAND 의 전용 영역입니다. 직접 주소로 접근해 안전하게 지울 수 있어서 빠른 지우기와 전방 보안에 쓰고, Mac 에서는 미디어 키가 키 재료와 모든 메타데이터, FileVault 데이터를 감쌉니다 [3]. iPhone·iPad 에서는 파일 메타데이터 키가 설치할 때나 "모든 콘텐츠 및 설정 지우기(Erase All Content and Settings)" 때 새로 만들어지고, 기기를 지울 때마다 키 감싸기 키가 바뀝니다 [3]. Mac 에서 같은 기능이 어떻게 동작하는지는 공개 자료가 없습니다.

## 하드웨어와 버전별 정리

| 대상 | 볼륨 암호화 | 즉시 원격 지우기 | 출처 |
|---|---|---|---|
| Apple 실리콘 Mac | FileVault 를 꺼도 VEK 로 암호화 | 됨 | [3] |
| T2 칩 Mac | FileVault 를 꺼도 VEK 로 암호화 | 됨 | [3] |
| 그 밖의 Mac | 공개 자료 없음 | FileVault 를 켰을 때 됨 | [3] |
| macOS 26.4 이후 Mac | FileVault 기본 켜짐(끌 수 있음) | — | [3] |
| 서드파티 AHCI SSD | — | — | `trimforce` 로 TRIM 을 켜고 끔, OS X 10.10.4 이후 [2] |

## 기대치를 정하는 순서

1. **저장 매체를 확인합니다.** 조사 대상이 내장 SSD 인지, 서드파티 SSD 인지, 외장 매체인지와 Mac 의 칩 종류를 [컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)](../../../02-artifacts/system-account/computer-name-hardware.md) 와 확보 기록에서 확인합니다.
2. **암호화 상태와 키를 확인합니다.** 위 표에 따라 볼륨이 암호화돼 있는지, FileVault 가 켜져 있는지, 복호에 쓸 키나 복호된 사본을 확보했는지 적습니다.
3. **지우기 흔적을 봅니다.** 볼륨을 지우거나 기기를 원격으로 지운 흔적이 있으면 키가 버려져 옛 데이터를 복호할 수 없다고 보고, 다시 설치한 흔적은 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../../../02-artifacts/system-account/os-version-install-history.md) 에서, 의도적인 지우기 정황은 [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md) 에서 봅니다.
4. **남는 기회를 고릅니다.** 원시 블록 복구 대신 현재 볼륨 안의 흔적부터 봅니다. 순서는 아래 절에 정리합니다.
5. **판단 근거를 적어 둡니다.** 1~3단계의 결과를 보고서에 남겨, 복구하지 못한 이유가 도구 탓인지 매체 조건 탓인지 읽는 사람이 가를 수 있게 합니다.

## TRIM 뒤에도 남는 기회

APFS 는 지운 블록에 TRIM 을 보내고 [1] TRIM 뒤 가비지 컬렉션이 일어나면 복구가 매우 어려워지며 [2], 상시 암호화 때문에 키 없는 원시 블록은 의미가 없으며, 볼륨이나 기기를 지운 뒤에는 키가 버려져 복호할 수 없어서 [3], 요즘 Mac 내장 SSD 에서는 파일 시스템을 무시하는 원시 블록 복구보다 현재 볼륨 안의 흔적이 더 현실적입니다.

| 남는 자리 | 이유 | 자세히 |
|---|---|---|
| 스냅샷 | 특정 시점 파일 시스템의 읽기 전용 사본이라서 [4] | [스냅숏과 백업 비교](../snapshot-diff.md) |
| 옛 체크포인트 | 객체를 제자리에서 고치지 않고 새 위치에 써서 [4] | [APFS에서 지운 파일](apfs-deleted-files.md) |
| SQLite 내부 잔재 | freelist·freeblock·WAL 은 파일 안의 빈 자리라서 파일 시스템 TRIM 대상이 아님 | [SQLite 레코드 되살리기](sqlite-records.md) |
| 백업 | 다른 매체에 따로 쓰인 사본 | [타임 머신](../../../02-artifacts/filesystem/time-machine/index.md) |
| 외장 매체 | 내장 저장소의 상시 암호화가 적용되지 않는 매체일 수 있음 | [카빙](carving.md) |

## 함정과 한계

TRIM 은 비동기라서 [1] 삭제 직후에 확보한 이미지라면 아직 비워지지 않은 블록이 있을 수 있지만, 언제 비워지는지는 공개 자료가 없어서 삭제 뒤 경과 시간만으로 복구 가능성을 말하지 않습니다. TRIM 한 자리를 읽을 때 무엇이 돌아오는지도 공개 자료가 없어서, 0 으로 채워진 영역을 보고 누가 일부러 덮어 썼다고 판단하지 않습니다.

키 삭제로 옛 데이터를 복호할 수 없게 된 경우와 처음부터 데이터가 없던 경우는 원시 이미지에서 구분하기 어렵습니다. 그래서 "복구하지 못했다" 를 "없었다" 로 옮겨 쓰지 않습니다.

## 결과를 어떻게 해석하나

이 페이지의 판단은 복구 결과가 아니라 복구의 전제 조건이라서, 보고서에는 확인한 사실과 판단을 나눠 적습니다. 예를 들면 "대상은 Apple 실리콘 Mac 의 내장 저장소이고, Apple Platform Security 에 따르면 이 저장소의 볼륨은 FileVault 설정과 상관없이 볼륨 키로 암호화돼 있다. 복호된 볼륨의 스냅샷과 옛 체크포인트에서 복구를 시도했고, 원시 블록 카빙은 하지 않았다" 처럼 씁니다.

## 참고 문헌

1. Apple, Apple File System Guide — Frequently Asked Questions (2018-06-04) — https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/FAQ/FAQ.html
2. SS64, trimforce — https://ss64.com/mac/trimforce.html
3. Apple, Apple Platform Security (2026년 8월) — https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf
4. Apple, Apple File System Reference (2020-06-22) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
