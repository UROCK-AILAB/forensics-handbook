---
title: "TRIM과 암호화가 주는 한계"
parent: "삭제 데이터 복구"
grand_parent: "기법 · 분석"
nav_order: 1480
---

# TRIM과 암호화가 주는 한계 (TRIM·Encryption)

Android 내부 저장소는 파일 내용과 파일 시스템 정보를 모두 암호화하고 빈 블록을 주기적으로 TRIM 해서, 저장 장치 층에서 지운 파일을 되살릴 수 있는 범위가 좁습니다. 이 페이지는 그 한계가 어디서 오는지와 복구를 시도하기 전에 가능성을 어떻게 추정하는지 다룹니다.

## 언제 쓰나

삭제 데이터 복구를 계획할 때와, 보고서에 복구하지 못한 이유를 적을 때 씁니다. 복구 가능성은 기기가 어느 Android 버전으로 출시됐는지, 어떤 방식으로 수집했는지, 대상 경로가 어느 암호화 영역에 있는지에 따라 달라집니다. 암호화 구조 자체의 설명은 [저장 공간 암호화](../../../01-foundations/storage/encryption/index.md) 페이지에 있고, 여기서는 복구와 관계있는 부분만 추립니다. 잠금 해제나 키를 얻는 방법은 다루지 않습니다.

## 파일 기반 암호화

파일 기반 암호화 (File-Based Encryption, FBE) 는 Android 7.0 에서 지원하기 시작했고, Android 10 이후 출시 기기에는 의무입니다 [1]. 저장 영역은 둘로 나뉩니다. 자격 증명 암호화 (Credential Encrypted, CE) 저장소는 사용자가 잠금 화면 자격 증명(PIN·패턴·비밀번호)으로 잠금을 푼 뒤에만 쓸 수 있는 기본 저장소이고, 기기 암호화 (Device Encrypted, DE) 저장소는 잠금을 풀기 전(Direct Boot)과 푼 뒤에 모두 쓸 수 있습니다 [1].

| 구분 | 경로 |
|---|---|
| CE | `/data/data`(= `/data/user/0`), `/data/user/<사용자ID>`, `/data/media/<사용자ID>`, `/data/system_ce/<사용자ID>`, `/data/misc_ce/<사용자ID>`, `/data/vendor_ce/<사용자ID>` |
| DE | `/data/user_de/<사용자ID>`, `/data/system_de/<사용자ID>`, `/data/misc_de/<사용자ID>`, `/data/vendor_de/<사용자ID>` |

앱 데이터 폴더와 공용 저장 공간(`/data/media/<사용자ID>`)이 모두 CE 영역에 들어갑니다 [1]. 파일 내용은 AES-256-XTS 나 Adiantum 으로, 파일 이름은 AES-256-CTS, AES-256-HEH, Adiantum, AES-256-HCTR2 중 하나로 암호화하고, Android 14 부터는 암호 가속 명령이 있는 기기에서 파일 이름에 AES-HCTR2 를 권합니다 [1].

내부 저장소의 CE 키는 사용자의 synthetic password 에서 파생한 AES-256-GCM 키가 보호합니다. synthetic password 는 기기에 Weaver HAL 이 있으면 Weaver 가, 없으면 Gatekeeper 가 잠금 화면 추측 횟수를 제한하며 보호합니다 [1]. 잠금 화면 자격 증명을 바꾸면 LockSettingsService 가 옛 자격 증명과 synthetic password 를 잇는 정보를 모두 지우고, Weaver 나 롤백 방지 저장소가 있는 기기에서는 이 삭제가 확실히 보장됩니다 [1]. 공장 초기화 때 키를 지워 옛 데이터를 되살릴 수 없게 만드는지(암호학적 삭제)와, 사용자(프로필)를 지울 때 그 사용자의 CE·DE 키가 어떻게 되는지는 FBE 문서에 나오지 않습니다. 초기화 흔적은 [초기화 흔적](../../../02-artifacts/system-account/factory-reset.md) 페이지에 있습니다.

## 메타데이터 암호화

메타데이터 암호화는 Android 9 에서 지원하기 시작했고, FBE 가 암호화하지 않는 부분을 암호화합니다. 보호 대상은 디렉터리 배치, 파일 크기, 권한, 만든 시각·고친 시각입니다 [2]. 그래서 `/data` 의 물리 이미지에서는 파일 내용뿐 아니라 디렉터리 배치, 크기, 시각 같은 파일 시스템 정보도 암호문이라서, 지운 파일의 inode 나 디렉터리 항목을 찾아 되살리는 방법도 막힙니다.

| 항목 | 내용 | 출처 |
|---|---|---|
| FBE 지원 시작 | Android 7.0 | [1] |
| FBE 의무 | Android 10 이후 출시 기기 | [1] |
| 메타데이터 암호화 지원 시작 | Android 9 | [2] |
| 메타데이터 암호화 의무 | Android 11 이후 출시 기기의 내부 저장소 | [2] |
| 내부 저장소로 쓰는 SD 카드(adoptable) | FBE 가 켜져 있으면 메타데이터 암호화도 항상 켜짐 | [2] |
| dm-default-key 커널 모듈 사용 | Android 11 이후 | [2] |
| 파일 이름 암호화에 AES-HCTR2 권장 | Android 14 이후, 암호 가속 명령이 있는 기기 | [1] |
| 삼성 One UI 별 차이 | 기기마다 fstab 의 암호화 플래그로 확인 | — |

의무 조건은 출시할 때의 Android 버전을 기준으로 적혀 있어서, 옛 버전으로 출시한 뒤 업데이트한 기기에 어떤 암호화가 걸려 있는지는 기기마다 확인합니다. 메타데이터 암호화는 기본으로 AES-256-XTS 를 쓰고, AES 가속이 없는 기기는 Adiantum 을 씁니다 [2]. 키는 KeyMint(예전 이름 Keymaster)가 보호하고 KeyMint 는 검증 부팅 (Verified Boot) 이 보호하며, 키 블롭은 `/metadata` 파티션(권장 크기 16MB)에 있습니다. fstab 에서는 `keydirectory=/metadata/vold/metadata_encryption` 같은 플래그로 이 자리를 가리킵니다 [2]. 검증 부팅은 [부트로더와 검증 부팅](../../../01-foundations/security-model/verified-boot.md) 페이지에 있습니다.

## TRIM

현행 AOSP 기준으로 볼륨 관리 데몬 vold 의 유휴 유지보수(`RunIdleMaint`)는 F2FS 청소, 트림, 저장 장치 청소를 묶어 실행하고, 그 안의 `Trim()` 이 마운트된 파일 시스템마다 `FITRIM` ioctl 을 보냅니다. 범위는 `range.len = ULLONG_MAX` 라서 파일 시스템 전체를 대상으로 합니다 [3]. 중단할 때는 `AbortIdleMaint` 를 부릅니다 [3].

| 구분 | 내용 |
|---|---|
| 대상 | fstab 항목과 vold 가 관리하는 볼륨. `/data`, `/cache`, `/metadata` 같은 마운트 지점 |
| 제외 | 읽기 전용 파일 시스템, bind 마운트, `no_trim` 표시 항목, 원시 파티션 종류(`emmc`, `mtd`, `swap`) |
| 웨이크락 | 유지보수 중 `IdleMaint` 웨이크락을 잡음 |
| 로그 문자열 | `Starting trim of`(DEBUG), `Trimmed`(바이트 수·밀리초와 함께, INFO), `Failed to open`·`Trim failed on`(WARNING) |

F2FS 쪽에서는 `/sys/fs/f2fs/<장치>/gc_urgent` 와 `gc_urgent_sleep_time` 을 조절해 청소를 재촉하고, `dirty_segments` 가 기준값(`DIRTY_SEGMENTS_THRESHOLD = 100`) 아래로 떨어지거나 제한 시간(`GC_TIMEOUT_SEC = 420`, 7분)이 지날 때까지 기다립니다. 저장 장치 청소의 제한 시간은 `DEVGC_TIMEOUT_SEC = 120`(2분)입니다 [3]. 같은 코드가 저장 장치 수명 값(`GetStorageLifeTime()`, `GetStorageRemainingLifetime()`, `/sys/fs/f2fs/<장치>/lifetime_write_kbytes`)도 읽습니다 [3].

F2FS 는 이 주기적 `FITRIM` 말고도 discard 마운트 옵션이 켜져 있으면 세그먼트를 청소할 때마다 discard·TRIM 명령을 보내고, `nodiscard` 로 끌 수 있습니다 [4]. discard 가 기본으로 켜지는지는 기기의 마운트 옵션에서 확인합니다. 유지보수가 얼마나 자주, 어떤 조건(충전 중, 화면 꺼짐 등)에서 도는지와 삼성 기기의 주기·설정이 AOSP 와 다른지는 실제 기기로 확인합니다. TRIM 한 블록을 플래시 컨트롤러가 언제 실제로 지우는지, 그 뒤에 읽으면 0 을 돌려주는지는 장치마다 다릅니다.

## 추정하는 순서

1. **출시 버전과 현재 버전을 확인합니다.** 빌드 정보를 읽는 법은 [기기 정보와 빌드](../../../02-artifacts/system-account/device-build.md) 페이지에 있습니다. Android 10 이후 출시 기기면 FBE, Android 11 이후 출시 기기면 메타데이터 암호화가 걸려 있다고 보고 시작합니다 [1][2].
2. **수집 방식을 확인합니다.** 파일 시스템을 거쳐 읽은 논리 수집 결과라면 지워지지 않은 파일 안의 잔재를 찾는 쪽으로 가고, 그 방법은 [SQLite 레코드 되살리기](sqlite-records.md) 페이지에 있습니다. 키 없이 뜬 `/data` 의 물리 이미지라면 저장 장치 층 복구는 사실상 막힌다고 적습니다.
3. **대상 경로의 영역을 확인합니다.** 찾는 데이터가 위 표의 CE·DE 어느 경로에 있는지 정리합니다.
4. **트림 기록을 찾아봅니다.** 수집한 logcat 이나 버그 리포트에서 위 로그 문자열을 검색합니다. 실제 기기의 logcat 에 이 줄이 남는지와 배터리 사용 기록에 `IdleMaint` 웨이크락 이름이 남는지는 기기마다 다를 수 있습니다. 로그를 읽는 법은 [logcat](../../../02-artifacts/logs/logcat.md), [버그 리포트](../../../02-artifacts/logs/bugreport.md), [배터리 사용 기록](../../../02-artifacts/app-usage/batterystats.md) 페이지에 있습니다.
5. **휴대용 SD 카드를 따로 봅니다.** 암호화하지 않은 휴대용 SD 카드라면 [파일 카빙](carving.md) 을 시도할 수 있습니다. 휴대용 SD 카드의 암호화 여부와 One UI 의 처리는 기기에서 확인합니다.

## 상황별 복구 가능성

| 상황 | 영향 | 근거 |
|---|---|---|
| `/data` 물리 이미지, 키 없음 | 파일 내용(FBE)과 파일 시스템 정보(메타데이터 암호화)가 모두 암호문이라 카빙과 파일 시스템 복구가 사실상 막힘 | [1][2] 에서 끌어낸 결론 |
| TRIM 한 블록 | 파일 시스템이 빈 블록이라고 장치에 알림. 장치가 실제로 지우는 시점과 읽기 결과는 장치마다 다름 | [3][4] |
| 파일은 살아 있고 안의 레코드만 지움 | 저장 장치 층 암호화와 TRIM 과 따로 봄. 플랫폼 SQLite 설정이 흔적을 줄임 | [SQLite 레코드 되살리기](sqlite-records.md) |
| 암호화하지 않은 휴대용 SD 카드 | 카빙 도구가 다루는 파일 시스템(FAT·exFAT 등)이면 카빙 대상 | [파일 카빙](carving.md) |

## 함정과 한계

F2FS 는 고친 데이터를 새 자리에 써서 옛 블록이 남는 파일 시스템이지만 [4], 그 옛 블록도 FBE 암호문이고 청소와 TRIM 으로 비워질 수 있습니다. "로그 구조라서 옛 데이터가 남는다" 는 설명을 Android 내부 저장소에 그대로 옮기지 않습니다.

실제 기기의 logcat 에 트림 줄이 늘 남는다는 보장이 없어서, 트림 줄이 없다는 것을 트림이 없었다는 근거로 쓰지 않습니다. 트림 줄이 있어도 소스에 적힌 문자열은 바이트 수와 걸린 시간만 담고 있어서 [3], 어느 파일의 블록이 비워졌는지는 알려 주지 않습니다.

## 결과를 어떻게 해석하나

이 페이지의 결론은 "되살릴 수 없었다" 는 결과를 설명하는 근거로 씁니다. 복구 결과가 비었다는 사실은 저장 장치 층의 한계를 보여 줄 뿐, 사용자가 무엇을 지웠는지나 지우지 않았는지를 증명하지 못합니다. 의도적인 증거 인멸을 따지려면 다른 흔적을 봐야 하고, 그 방법은 [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) 페이지에 있습니다.

보고서에는 "데이터가 지워져 복구할 수 없다" 가 아니라 "이 기기는 Android 10 이후 출시 기기라 내부 저장소에 FBE 가 걸려 있고, 키 없이 뜬 물리 이미지에서는 파일 내용을 읽을 수 없어 카빙을 하지 않았다" 처럼 판단 근거와 한 일을 씁니다.

## 참고 문헌

1. File-based encryption (Android Open Source Project) — https://source.android.com/docs/security/features/encryption/file-based
2. Metadata encryption (Android Open Source Project) — https://source.android.com/docs/security/features/encryption/metadata
3. AOSP platform/system/vold, IdleMaint.cpp (main) — https://android.googlesource.com/platform/system/vold/+/refs/heads/main/IdleMaint.cpp
4. WHAT IS Flash-Friendly File System (F2FS)? (Linux kernel documentation) — https://docs.kernel.org/filesystems/f2fs.html
