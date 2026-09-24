---
title: "파일볼트 이미지 열기"
parent: "암호화된 증거 다루기"
grand_parent: "기법 · 분석"
nav_order: 2180
---

# 파일볼트 이미지 열기 (FileVault)

파일볼트(FileVault)로 잠긴 맥 디스크 이미지를 열 때 어떤 방식의 암호화인지 먼저 가르고, 쓸 수 있는 풀 수단을 확인한 뒤 사본을 읽기 전용으로 연결하는 순서를 다룹니다.

## 언제 쓰나

맥 디스크 이미지를 열었는데 볼륨이 잠겨 있을 때, 또는 살아 있는 맥을 끄기 전에 파일볼트가 켜져 있는지 판단해야 할 때 씁니다. 키가 어떤 순서로 이어지는지(볼륨 암호화 키·키 암호화 키·키백)와 복구 키를 보관하는 구조는 [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md) 쪽에 있고, 이 페이지는 이미지를 실제로 여는 순서와 그 과정에서 확인할 흔적만 다룹니다.

맥의 파일볼트는 두 방식으로 나뉘고, 방식에 따라 이미지 구조와 쓸 도구가 달라집니다.

| 방식 | macOS 버전 | 이미지에서 알아보는 곳 | 출처 |
|---|---|---|---|
| CoreStorage 파일볼트 2 | 10.7 Lion에서 도입(libfvde 형식 문서의 시험 범위 10.7~10.15) | 물리 볼륨 머리 오프셋 88의 시그니처 `CS` | [3] |
| APFS 파일볼트 | macOS 10.13 이후 | APFS 볼륨 슈퍼블록의 `apfs_fs_flags` | [FV-2][FV-4] |
| APFS 파일볼트(macOS 11 이후) | macOS 11 이후 | 시스템 볼륨은 서명된 시스템 볼륨(SSV)이고 데이터 볼륨만 암호화 | [FV-1] |

APFS 안에서도 소프트웨어 암호화와 하드웨어 암호화를 나눠 봐야 합니다. APFS 명세에 따르면 소프트웨어 암호화는 외장 저장장치와, 하드웨어 암호화를 지원하지 않는 기기의 내장 저장장치에 쓰이고, T2 맥처럼 하드웨어 암호화를 지원하는 기기의 내장 저장장치는 하드웨어 암호화를 씁니다. 공개 명세가 설명하는 쪽은 소프트웨어 암호화뿐입니다 [FV-4].

T2·Apple silicon 맥은 파일볼트를 켜지 않아도 내장 볼륨이 암호화돼 있고, 볼륨 암호화 키는 Secure Enclave 안의 하드웨어 UID로 보호됩니다 [FV-1]. 이 UID는 Secure Enclave 밖의 소프트웨어가 읽을 수 없고 JTAG 같은 디버그 인터페이스로도 읽을 수 없습니다 [FV-5]. 공개 도구 apfs-fuse도 T2 칩 맥 내장 드라이브의 하드웨어 암호화 볼륨은 지원하지 않는다고 적습니다 [9]. 이 세 가지를 이으면 이런 맥의 내장 디스크는 떼어 낸 디스크나 칩오프 이미지만으로는 풀 수 없다는 결론이 나오지만, 문서 세 곳을 이어 붙인 추론이라서 보고서에 쓸 때도 추론이라고 밝힙니다. 이런 맥이라면 획득 방법을 [맥 증거 확보 (Acquisition)](../../process-acquisition/evidence-acquisition/index.md)와 [라이브 대응 (Live Response)](../../process-acquisition/live-response/index.md)에서 함께 검토합니다.

## 절차

1. **살아 있는 맥이면 끄기 전에 파일볼트 상태를 기록합니다.** `fdesetup status` 와 `fdesetup list -extended` 결과를 남기고, 복구 키로 풀린 상태인지(`usingrecoverykey`)도 확인합니다. 명령마다 무엇을 알려 주는지는 아래 "살아 있는 맥에 남는 흔적" 절에 정리했습니다.
2. **이미지에서 컨테이너 종류를 가립니다.** 파티션 표에서 CoreStorage 볼륨인지 APFS 컨테이너인지 먼저 보고([파티션 구조 (GPT·APFS 파티션)](../../../01-foundations/disk-volume/gpt-partitions.md)), CoreStorage라면 물리 볼륨 머리 오프셋 88에서 `CS` 를 확인합니다. APFS라면 볼륨 슈퍼블록 오프셋 264의 `apfs_fs_flags` 를 보고, `APFS_FS_UNENCRYPTED`(0x1) 비트가 서 있는지로 암호화 여부를 1차로 판단합니다. 이 칸에는 `APFS_FS_ONEKEY`(0x8)도 들어갈 수 있습니다 [FV-3][FV-4]. 슈퍼블록을 읽는 법은 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md)에 있습니다.
3. **풀 수단을 모읍니다.** 사용자 로그인 암호, 개인 복구 키(PRK), 기관 복구 키, MDM으로 에스크로한 복구 키 가운데 무엇을 합법적으로 얻을 수 있는지 확인합니다. 기관 복구 키 파일과 MDM 에스크로 파일(`/var/db/FileVaultPRK.dat`, PRK를 인증서로 암호화한 CMS 봉투 [FV-8])이 어디에 남는지는 [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md) 쪽에 정리돼 있습니다.
4. **원본이 아닌 사본을 읽기 전용 도구로 연결합니다.** APFS는 apfs-fuse나 libfsapfs의 `fsapfsmount` 로, CoreStorage는 libfvde 계열 도구로 엽니다. 도구별 옵션은 아래 "도구" 절에 있습니다.
5. **연결에 쓴 도구 이름·판·옵션과 풀 수단의 종류를 기록합니다.** 어떤 키로 열었는지는 결과 해석에도 들어가고, 도구를 검증하는 법은 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md)에 있습니다.

## CoreStorage 볼륨 구조

CoreStorage 볼륨은 APFS와 구조가 전혀 달라서 따로 정리합니다. 아래 내용은 libfvde 형식 문서를 따른 것입니다 [3].

물리 볼륨 머리(physical volume header)는 512바이트이고, 볼륨 끝에 백업 사본이 하나 더 있습니다.

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 88 | 2 | Core Storage 시그니처 `CS` |
| 96 | 4 | 블록 크기(바이트) |
| 100 | 4 | 메타데이터 크기(바이트) |
| 104 | 8×4 | 메타데이터 블록 번호 배열(볼륨 시작 기준) |
| 168 | 4 | 키 데이터 크기(보통 16) |
| 172 | 4 | 암호화 방식(2 = AES-XTS) |
| 176 | 16 | 키 데이터 |
| 304 | 16 | 물리 볼륨 식별자(UUID, 빅엔디언, AES-XTS 트윅 키로 씀) |
| 320 | 16 | 논리 볼륨 그룹 식별자(UUID, 빅엔디언) |

메타데이터 블록마다 앞에 64바이트 머리가 붙고, 오프셋 0에 CRC-32(4바이트), 8에 버전(2바이트), 10에 블록 종류(2바이트), 32에 메타데이터 시작 기준 블록 번호(8바이트), 48에 블록 크기(4바이트)가 있습니다. 암호화된 메타데이터는 머리의 키 데이터를 주 키로, 물리 볼륨 식별자를 트윅 키로 쓴 AES-XTS로 암호화돼 있고, 암호화 단위는 8192바이트입니다.

"Recovery HD" 파티션에는 `EncryptedRoot.plist.wipekey` 가 있습니다. 이 파일은 128비트 AES-XTS로 암호화돼 있고 단위 크기는 파일 전체인데, 주 키로 무엇을 쓰는지는 형식 문서 안에서도 절마다 달라서(한 곳은 물리 볼륨 식별자, 다른 곳은 키 데이터) 여기서는 물리 볼륨 머리에 있는 값으로 푼다는 것까지만 적습니다. 볼륨 마스터 키(VMK, 128비트)는 `KEKWrappedVolumeKeyStruct` 여러 개에 감싸여 저장되고, 이 KEK는 사용자 암호나 복구 암호로 풀립니다. 볼륨 트윅 키는 VMK와 논리 볼륨 패밀리 UUID를 이어 붙여 SHA-256을 구한 값의 앞 128비트입니다. 암호에서 키를 얻을 때는 PBKDF2-SHA256을 쓰고, 소금은 284바이트 구조인 `PassphraseWrappedKEKStruct` 안에 있습니다. 복구 암호는 4글자씩 6묶음을 대시로 이은 모양이고, 대시까지 키 유도에 들어갑니다.

아래 헥스는 명세로 만든 예시이고 실제 검체에서 뽑은 값이 아닙니다. 오프셋 0x58(88)의 `43 53` 이 `CS` 이고, 나머지 바이트는 설명을 위해 0으로 채웠습니다.

```
00000050  00 00 00 00 00 00 00 00  43 53 00 00 00 00 00 00  |........CS......|
```

## 살아 있는 맥에 남는 흔적

살아 있는 맥에서는 `fdesetup` 으로 파일볼트 상태를 확인합니다. 아래 동작은 2025-07-02 판 man 페이지를 따른 것입니다 [2].

| 동사 | 알려 주는 것 |
|---|---|
| `status` | 파일볼트가 켜져 있는지, `-extended` 를 붙이면 진행률까지 |
| `list` | 파일볼트 사용자와 UUID, `-extended` 를 붙이면 사용자 종류와 에스크로 상태까지 |
| `isactive` | 켜져 있으면 종료 코드 0 |
| `haspersonalrecoverykey` | 개인 복구 키가 설정돼 있는지 |
| `hasinstitutionalrecoverykey` | 기관 복구 키가 설정돼 있는지(CoreStorage에서는 공개 키 해시를 돌려줌) |
| `usingrecoverykey` | 현재 개인 복구 키로 풀린 상태인지 |
| `supportsauthrestart` | 인증 재시동을 지원하는지 |

`-outputplist` 는 복구 키와 시스템 정보를 plist 사전으로 표준 출력에 내고, 복구 키가 바뀌면 `Change` 키가 붙고 `EnableDate` 키에 바뀐 날짜가 들어간다고 man 페이지는 적습니다. 복구 키가 든 이 출력을 파일로 조직이 따로 보관해 두었다면 풀 수단이 될 수 있습니다. 일부 옵션은 APFS에서 지원하지 않아 종료 코드 34를 내니, 이 코드가 나오면 명령 실패가 아니라 볼륨 방식 차이로 읽습니다.

기관 복구 키는 `/Library/Keychains/FileVaultMaster.keychain` 파일을 쓰고, 이 키의 인증서 일반 이름은 "FileVault Recovery Key" 입니다 [2][FV-9]. 증거에서 이 파일이 보이면 기관 복구 키를 설정한 맥일 가능성을 따져 봅니다.

`fdesetup authrestart` 는 잠금 해제 키 사본을 시스템 메모리와, 지원하는 시스템에서는 SMC에도 두고, 대기 중에 키를 남기지 않게 하는 설정은 `pmset destroyfvkeyonstandby` 입니다 [2]. 인증 재시동을 거친 맥은 재부팅 뒤 파일볼트 암호 화면 없이 부팅될 수 있어서, 현장에서 "암호 화면이 없었다" 를 곧바로 "파일볼트가 꺼져 있었다" 로 읽지 않습니다.

## 도구

아래 도구는 공개 도구의 예이고, 옵션은 각 도구 문서에 적힌 것만 옮겼습니다.

| 도구 | 대상 | 문서에 적힌 옵션과 범위 |
|---|---|---|
| apfs-fuse | APFS | 읽기 전용 FUSE 드라이버이고 소프트웨어 암호화 볼륨을 지원하며, 암호화된 볼륨이면 암호를 묻습니다. `-r` 로 암호나 개인 복구 키를 주고, `-v` 볼륨 번호, `-p` 파티션 번호, `-s` 컨테이너 오프셋, `-f` 퓨전 드라이브 보조 장치, `-o`(uid, gid, vol, blksize, pass, xid, snap), `-d` 디버그를 받습니다. 입력은 원시 APFS 장치, GPT 파티션 표, DMG(zlib·ADC 압축과 암호화 포함)입니다 [9]. |
| libfsapfs `fsapfsmount` | APFS | `-f` 파일 시스템(볼륨) 번호, `-p` 암호, `-o` 컨테이너 오프셋을 받습니다. 예: `fsapfsmount -f 1 -p PASSWORD image.dmg /mnt/fuse` [5] |
| libfvde | CoreStorage | 이 페이지의 CoreStorage 구조 설명이 이 프로젝트의 형식 문서에서 나왔습니다 [3]. |

apfs-fuse는 T2 하드웨어 암호화 볼륨, LZFSE 투명 압축, 펌링크(firmlink)를 지원하지 않습니다 [9]. LZFSE로 압축된 파일은 연결이 돼도 내용을 제대로 읽지 못할 수 있고, 펌링크를 따라가지 못하니 데이터 볼륨과 시스템 볼륨을 이어 보는 경로가 실제 맥과 다르게 보일 수 있습니다. 펌링크는 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../../../01-foundations/disk-volume/volume-group-firmlinks.md)를 참고합니다.

## 함정과 한계

- `apfs_fs_flags` 로 암호화 여부를 판단하는 방법은 공개 명세가 설명하는 소프트웨어 암호화 볼륨을 기준으로 합니다. T2·Apple silicon 내장 볼륨에서 이 칸이 어떻게 찍히는지는 이 핸드북이 확인한 범위 밖이라서, 그런 볼륨에 같은 판단을 그대로 적용하지 않습니다.
- CoreStorage 물리 볼륨 머리는 볼륨 끝에 백업 사본이 있어서, 앞쪽 머리가 손상된 이미지는 끝쪽 사본으로 구조를 확인할 수 있습니다.
- 한 도구가 볼륨을 열지 못했다고 해서 키가 틀렸다고 단정하지 않습니다. 도구마다 지원 범위가 달라서, 다른 도구로 한 번 더 열어 보고 그 결과까지 기록합니다.
- 쓰기가 가능한 방식으로 붙이면 사본 이미지가 바뀔 수 있어서 읽기 전용 연결을 지킵니다.

## 결과를 어떻게 해석하나

이미지를 연 결과가 말해 주는 범위는 "이 풀 수단으로 이 볼륨의 잠금이 풀렸다" 까지입니다. 볼륨이 열렸다는 사실만으로는 누가 언제 그 맥을 썼는지 알 수 없고, 그 판단은 볼륨 안의 아티팩트로 따로 합니다([그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)).

살아 있는 맥에서 얻은 기록은 해석할 거리가 더 있습니다. `usingrecoverykey` 가 참이면 볼륨이 개인 복구 키로 풀린 상태라는 뜻입니다. `fdesetup list -extended` 의 에스크로 항목은 복구 키를 맡기도록 설정됐는지를 보여 주지만, man 페이지는 서버로 아직 보내지 못한 경우에도 "Yes" 로 나온다고 적어서, 이 값만으로 조직이 복구 키를 실제로 받았다고 쓰지 않습니다. 보고서에는 "개인 복구 키로 데이터 볼륨의 잠금을 풀고 읽기 전용으로 연결했으며, 사용한 도구와 판은 부록에 적었다" 처럼 쓴 풀 수단과 도구를 함께 적습니다.

## 참고 문헌

- [2] fdesetup(8) man 페이지(2025-07-02 판) — https://keith.github.io/xcode-man-pages/fdesetup.8.html
- [3] libyal libfvde, FileVault Drive Encryption (FVDE) 형식 문서 — https://raw.githubusercontent.com/libyal/libfvde/main/documentation/FileVault%20Drive%20Encryption%20(FVDE).asciidoc
- [5] libyal libfsapfs 위키, Mounting — https://github.com/libyal/libfsapfs/wiki/Mounting
- [9] apfs-fuse README (sgan81) — https://github.com/sgan81/apfs-fuse
- [FV-1] Apple Platform Security, Volume encryption with FileVault in macOS — https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/web
- [FV-2] Apple Platform Security, Managing FileVault in macOS — https://support.apple.com/guide/security/managing-filevault-sec8447f5049/web
- [FV-3] libyal libfsapfs, Apple File System (APFS) 형식 문서 — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
- [FV-4] Apple, Apple File System Reference(2020-06-22 판) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
- [FV-5] Apple Platform Security, The Secure Enclave — https://support.apple.com/guide/security/secure-enclave-sec59b0b31ff/web
- [FV-8] Apple device-management 저장소, com.apple.security.FDERecoveryKeyEscrow.yaml — https://raw.githubusercontent.com/apple/device-management/release/mdm/profiles/com.apple.security.FDERecoveryKeyEscrow.yaml
- [FV-9] Apple device-management 저장소, com.apple.MCX.FileVault2.yaml — https://raw.githubusercontent.com/apple/device-management/release/mdm/profiles/com.apple.MCX.FileVault2.yaml
