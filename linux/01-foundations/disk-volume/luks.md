---
title: "LUKS 디스크 암호화"
parent: "기반 · 디스크와 볼륨"
nav_order: 130
---

# LUKS 디스크 암호화 (LUKS·dm-crypt)

LUKS 머리글을 읽으면 볼륨을 어떤 방식으로 암호화했는지, 키 슬롯을 몇 개 쓰는지, 다른 흔적과 맞춰 볼 UUID 가 무엇인지 암호 없이 알 수 있습니다.

리눅스의 디스크 암호화는 커널의 dm-crypt 가 맡습니다. device-mapper 의 crypt 대상 (crypt target) 이 커널 crypto API 로 블록 장치를 투명하게 암호화하고[1], LUKS (Linux Unified Key Setup) 는 그 설정과 키를 장치 앞쪽 머리글에 적어 두는 형식입니다[5]. dm-crypt 를 설정할 때 지금 권하는 방식이 LUKS 입니다[1]. 머리글 없이 명령줄 인자만으로 여는 방식은 plain dm-crypt 라고 부릅니다[5].

## 이 형식을 쓰는 아티팩트

LUKS 볼륨은 파티션 하나, LVM 논리 볼륨, 디스크 전체 어디에나 놓일 수 있습니다. 파티션 표에서 LUKS 를 가리키는 형식 GUID 는 [파티션 (MBR·GPT)](partitions.md) 쪽에, LVM 과 겹쳐 쓰는 배치는 [LVM 논리 볼륨](lvm.md) 쪽에 있습니다.

| 흔적 | 위치 | 알려 주는 것 |
|---|---|---|
| LUKS 머리글 | 볼륨 첫 바이트(LUKS2 는 보조 머리글이 하나 더) | 판, 암호 방식, 키 슬롯, UUID |
| `/etc/crypttab` | 루트 파일 시스템 | 부팅 때 열 볼륨 이름, 장치, 키 파일, 옵션[11] |
| `/etc/cryptsetup-keys.d/`, `/run/cryptsetup-keys.d/` | 루트 파일 시스템, 실행 중 메모리 파일 시스템 | crypttab 에 키 파일을 적지 않았을 때 찾는 `볼륨이름.key` 파일[11] |
| 커널 명령줄의 `rd.luks.*`, `luks.*` | `/proc/cmdline`, 부트 로더 설정 | crypttab 없이 부팅 때 열 LUKS UUID 와 이름[12] |
| `systemd-cryptsetup@.service` 유닛 | systemd 저널 | 부팅 때 볼륨을 연 기록[12] |
| `/dev/mapper/볼륨이름` | 라이브 시스템 | 열린 볼륨의 복호된 장치[11] |

암호화 스왑은 [스왑과 최대 절전](swap-hibernation.md) 쪽에서 함께 다룹니다.

## 구조

### dm-crypt 표

device-mapper 표에서 crypt 대상의 인자는 `cipher key iv_offset device offset` 이고 뒤에 선택 인자가 붙습니다[1]. 암호 방식은 `cipher[:keycount]-chainmode-ivmode[:ivopts]` 꼴로 쓰며, `aes-xts-plain64`, `aes-cbc-essiv:sha256` 이 그 예입니다[1]. 커널 crypto API 이름을 그대로 쓰는 `capi:` 접두 형식도 있습니다[1]. 키 칸에는 16진수 키를 쓰거나, 콜론으로 시작하는 문자열로 커널 keyring 에 있는 키를 가리킵니다[1].

선택 인자 `allow_discards` 를 켜면 TRIM 요청이 암호 장치 아래로 내려갑니다. 기본은 무시이고, 켜면 파일 시스템 형식 같은 정보가 암호문 장치에서 드러날 수 있습니다[1]. crypttab 의 `discard` 옵션이 같은 동작입니다[11]. 현재 적재된 암호 방식 목록은 `/proc/crypto` 에 있습니다[1].

### LUKS1 머리글

매직은 `LUKS\xba\xbe` 6바이트이고, 정수는 모두 네트워크 바이트 순서(빅엔디언)로 적습니다[2]. 아래 오프셋은 구조체 선언에서 계산한 값입니다[2].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x00 | 6 | magic | `LUKS\xba\xbe` |
| 0x06 | 2 | version | 1 |
| 0x08 | 32 | cipherName | 암호 이름 문자열 |
| 0x28 | 32 | cipherMode | 암호 모드 문자열 |
| 0x48 | 32 | hashSpec | 해시 이름 문자열 |
| 0x68 | 4 | payloadOffset | 데이터 영역 시작 위치 |
| 0x6C | 4 | keyBytes | 볼륨 키 길이(바이트) |
| 0x70 | 20 | mkDigest | 볼륨 키 검증값 |
| 0x84 | 32 | mkDigestSalt | 검증값 salt |
| 0xA4 | 4 | mkDigestIterations | 검증값 반복 횟수 |
| 0xA8 | 40 | uuid | UUID 문자열 |
| 0xD0 | 48×8 | keyblock | 키 슬롯 8개 |

키 슬롯 하나(48바이트)는 active(4), passwordIterations(4), passwordSalt(32), keyMaterialOffset(4), stripes(4) 순서입니다[2]. active 값이 `0x00AC71F3` 이면 쓰는 슬롯이고 `0x0000DEAD` 이면 빈 슬롯입니다[2]. 옛 형식의 값 `0xCAFE`(사용)·`0`(빈 슬롯)도 정의에 남아 있습니다[2]. stripes 는 보통 4000 이고, 키 슬롯 자료 영역은 4096바이트 단위로 놓입니다[2]. 키 슬롯 뒤 432바이트 채움까지 더하면 머리글 구조체는 1024바이트입니다[2].

### LUKS2 머리글

LUKS2 는 같은 머리글을 두 벌 둡니다. 주 머리글은 장치 처음에 있고 매직이 `LUKS\xba\xbe`, 보조 머리글은 매직이 `SKUL\xba\xbe` 입니다[3][10]. 바이너리 머리는 4096바이트이고 그 뒤에 JSON 영역이 이어집니다[3]. 정수는 빅엔디언으로 읽습니다[10].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x000 | 6 | magic | `LUKS\xba\xbe` 또는 `SKUL\xba\xbe` |
| 0x006 | 2 | version | 2 |
| 0x008 | 8 | hdr_size | JSON 영역까지 포함한 머리글 크기(바이트) |
| 0x010 | 8 | seqid | 머리글을 고칠 때마다 1씩 늘어나는 번호 |
| 0x018 | 48 | label | 볼륨 이름 |
| 0x048 | 32 | checksum_alg | 머리글 체크섬 알고리즘 이름 |
| 0x068 | 64 | salt | 머리글마다 다른 salt |
| 0x0A8 | 40 | uuid | UUID 문자열 |
| 0x0D0 | 48 | subsystem | 볼륨을 쓰는 쪽이 적는 이름 |
| 0x100 | 8 | hdr_offset | 이 머리글이 놓인 위치(장치 처음부터 바이트) |
| 0x108 | 184 | padding | 채움 |
| 0x1C0 | 64 | csum | 머리글 체크섬 |
| 0x200 | 7×512 | padding | 4096바이트까지 채움 |

uuid 와 checksum_alg 는 LUKS1 의 uuid(0xA8)·hashSpec(0x48) 와 같은 오프셋에 두었습니다[3]. 그래서 판을 모르는 상태에서도 0xA8 에서 UUID 를 읽을 수 있습니다.

보조 머리글은 0x4000, 0x8000, 0x10000, 0x20000, 0x40000, 0x80000, 0x100000, 0x200000, 0x400000 가운데 한 곳에 있습니다[3][10]. libblkid 는 보조 머리글의 hdr_offset 이 실제로 읽은 위치와 같을 때만 받아들입니다[10].

JSON 영역의 최상위 키는 `keyslots`, `tokens`, `segments`, `digests`, `config` 입니다[4]. 키 슬롯과 토큰은 각각 32개까지 둘 수 있습니다[3]. 토큰 (token) 은 어느 키 슬롯을 무엇으로 여는지 적은 JSON 객체이고[5], PKCS#11·FIDO2·TPM2 로 여는 볼륨은 여는 데 쓰는 저장 키를 이 토큰에 둘 수 있습니다[11]. cryptsetup 이 기본으로 아는 토큰 이름은 `luks2-` 로 시작합니다(예: `luks2-keyring`)[3]. 다른 토큰 형식 이름은 검체에서 `cryptsetup luksDump` 결과로 확인합니다.

머리글 전체 크기의 기본값은 16MB 이고 만들 때 바꿀 수 있습니다[5]. LUKS2 는 메타데이터를 머리글에만 두고 장치 가운데나 끝에는 두지 않습니다. 실험 기능인 무결성 지원을 쓰면 데이터 영역 처음에 무결성 머리글이 하나 더 생기지만, 이것도 장치 앞쪽에 있습니다[5]. `cryptsetup luksFormat` 의 기본 형식은 LUKS2 입니다[9].

LUKS1·LUKS2 구조체와 JSON 최상위 키 어디에도 시각 칸이 없습니다[2][3][4].

### crypttab

`/etc/crypttab` 은 한 줄에 볼륨 하나를 `볼륨이름 암호화장치 키파일 옵션` 순서로 적고, 앞 두 칸만 필수입니다[11]. 볼륨은 `/dev/mapper/볼륨이름` 으로 생기고, 장치 칸에는 경로나 `UUID=` 를 씁니다[11]. 키파일 칸이 없거나 `none`·`-` 이면 `/etc/cryptsetup-keys.d/` 와 `/run/cryptsetup-keys.d/` 에서 `볼륨이름.key` 를 찾고, 그것도 없으면 부팅 때 암호를 묻습니다[11]. 스왑에는 `/dev/urandom` 을 키 파일로 적어 부팅마다 새 키를 쓸 수 있습니다[11].

모드는 LUKS·TrueCrypt·BitLocker·plain 네 가지입니다[11]. 옵션에 모드가 없을 때는 장치에 LUKS 서명이 있으면 LUKS 로, 없으면 plain 으로 엽니다[11]. 해석에 쓰는 옵션은 아래와 같습니다[11].

| 옵션 | 뜻 |
|---|---|
| `luks`, `plain`, `tcrypt`, `bitlk` | 모드를 정함 |
| `swap` | 열고 나서 mkswap 으로 포맷, plain 을 뜻함 |
| `tmp=` | 열고 나서 /tmp 용으로 포맷, plain 을 뜻함 |
| `header=` | 머리글을 따로 둔 장치나 파일 |
| `discard` | TRIM 요청을 아래로 내려보냄 |
| `keyfile-offset=`, `keyfile-size=` | 키 파일에서 읽을 범위 |
| `tpm2-device=`, `fido2-device=`, `pkcs11-uri=` | 하드웨어 토큰으로 여는 볼륨 |
| `noauto`, `nofail` | 부팅 때 자동으로 열지 않음, 실패해도 부팅 계속 |
| `x-initrd.attach` | initrd 단계에서 엶 |

아래는 만든 예시입니다. 첫 줄은 UUID 로 가리킨 LUKS 볼륨이고, 둘째 줄은 부팅마다 새 키로 여는 암호화 스왑입니다.

```
data   UUID=0b3d5e7a-1c2f-4a6b-9d8e-2f4a6c8e0b1d   none   luks,discard
swap   /dev/sdb3   /dev/urandom   swap
```

### 부팅 때 여는 방식

systemd-cryptsetup-generator 가 부팅 초기에 crypttab 을 읽어 `systemd-cryptsetup@.service` 유닛을 만듭니다[12]. 커널 명령줄에서도 열 볼륨을 정할 수 있습니다. `rd.luks.uuid=`·`luks.uuid=` 는 LUKS UUID 를, `rd.luks.name=UUID=이름` 은 UUID 와 이름을 함께 지정하고, `rd.luks.crypttab=no` 는 crypttab 을 무시하게 하며, `rd.luks=no` 는 생성기를 끕니다[12]. `rd.` 이 붙은 쪽은 initrd 에서만 읽습니다[12]. crypttab 에 없는 UUID 로 연 볼륨은 이름이 `luks-UUID` 가 됩니다[12].

## 읽는 법

### 헥스로 한 번

아래는 LUKS2 구조체로 만든 예시이고 값은 모두 지어낸 것입니다. salt·체크섬처럼 읽지 않아도 되는 칸은 `..` 로 가렸습니다.

```
오프셋     00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000  4C 55 4B 53 BA BE 00 02  00 00 00 00 00 00 40 00   LUKS..........@.
00000010  00 00 00 00 00 00 00 05  00 00 00 00 00 00 00 00   ................
00000040  00 00 00 00 00 00 00 00  73 68 61 32 35 36 00 00   ........sha256..
000000A0  .. .. .. .. .. .. .. ..  30 62 33 64 35 65 37 61   ........0b3d5e7a
000000B0  2D 31 63 32 66 2D 34 61  36 62 2D 39 64 38 65 2D   -1c2f-4a6b-9d8e-
00000100  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00   ................
```

0x00 의 `4C 55 4B 53 BA BE` 가 매직이고, 0x06 의 `00 02` 가 판 2 입니다. 0x08 의 hdr_size 는 0x4000(16,384바이트)이라 JSON 영역이 0x1000 부터 0x4000 앞까지입니다. 0x10 의 seqid 는 5 이고, 머리글을 고칠 때마다 1씩 늘어나는 값이라 보조 머리글이나 머리글 백업 파일의 값과 견줄 때 씁니다. 0x48 에서 체크섬 알고리즘 `sha256` 을, 0xA8 부터 UUID 문자열을 읽습니다. 0x100 의 hdr_offset 이 0 이라 이 머리글은 주 머리글입니다.

같은 예시에서 보조 머리글은 0x4000 에 있습니다.

```
00004000  53 4B 55 4C BA BE 00 02  00 00 00 00 00 00 40 00   SKUL..........@.
00004010  00 00 00 00 00 00 00 05  00 00 00 00 00 00 00 00   ................
00004100  00 00 00 00 00 00 40 00  00 00 00 00 00 00 00 00   ......@.........
```

매직이 `SKUL` 로 뒤집혀 있고, 0x4100 의 hdr_offset 이 0x4000 으로 자기 위치와 같습니다. 두 머리글의 seqid 가 다르면 한쪽만 고쳐졌거나 한쪽이 손상됐을 가능성이 있습니다. JSON 영역은 평문 텍스트라 0x1000 부터 읽으면 `keyslots`, `segments` 같은 키가 그대로 보입니다.

LUKS1 이면 0x06 이 `00 01` 이고, 0x08·0x28·0x48 에서 암호 이름·모드·해시 문자열을 읽은 뒤 0xD0 부터 48바이트씩 8번 끊어 각 슬롯의 active 값을 봅니다[2].

### 공개 도구로 한 번

`cryptsetup luksDump` 는 암호 없이 머리글과 키 슬롯 정보를 보여 줍니다[6]. LUKS2 에서는 첫 부분에 `Version`, `Epoch`, `Metadata area`, `Keyslots area`, `UUID`, `Label`, `Subsystem` 이 나오고 이어서 `Flags`, `Data segments`, `Keyslots`, `Tokens`, `Digests` 가 나옵니다[4]. `Epoch` 은 머리글의 seqid 입니다[4]. `--dump-json-metadata` 를 주면 JSON 영역을 그대로 출력합니다[6].

`blkid` 는 LUKS 볼륨의 형식을 `crypto_LUKS` 로 표시하고, UUID 와 함께 LUKS2 에서는 LABEL 과 SUBSYSTEM 도 알려 줍니다[10]. 주 머리글이 없으면 보조 머리글 위치를 차례로 찾아봅니다. 다만 안전 검사(safeprobe) 방식으로 부를 때는 이 단계를 건너뜁니다[10]. dissect.fve 는 파이썬에서 LUKS1·LUKS2 를 읽고, `find_luks_headers` 로 주·보조 머리글 위치와 판을 찾습니다[13].

## 포렌식에서 중요한 점

### 증명하는 것

- 어떤 파티션·논리 볼륨이 LUKS 로 암호화돼 있는지, 판이 1 인지 2 인지
- 암호 방식·해시·키 길이, 키 슬롯이 몇 개 쓰이고 있는지, 토큰으로 하드웨어 장치(TPM2·FIDO2·PKCS#11)를 등록했는지
- LUKS UUID. 이 값은 crypttab 의 `UUID=`, `/dev/disk/by-uuid` 링크, 커널 명령줄의 `rd.luks.uuid=`, 저널의 유닛 이름과 맞춰 볼 수 있습니다[11][12].
- LUKS2 의 seqid. 머리글을 몇 번 고쳤는지 가늠하는 번호입니다[3].
- crypttab 이나 부팅 기록에 plain 모드 볼륨이 적혀 있다면, 머리글이 없어도 그 장치를 암호화해 썼다는 설정이 있었다는 점

### 증명하지 못하는 것

- 언제 암호화했는지, 언제 암호를 바꾸거나 키 슬롯을 더했는지. 머리글에 시각 칸이 없습니다[2][3].
- 누가 볼륨을 열었는지, 안에 무엇이 있는지
- 누군가 키를 갖고 있다는 것. 머리글만으로는 시험 삼아 만든 볼륨인지, 무작위 키로 만든 암호화 스왑인지 알 수 없습니다[5].
- plain dm-crypt 를 썼다는 것. plain 은 디스크에 메타데이터가 없고, 무작위 값으로 덮어쓴 영역과 똑같이 보입니다[5]. 그래서 plain 볼륨의 흔적은 crypttab·커널 명령줄·저널 쪽에서 찾습니다.

### 시각

LUKS 머리글에는 시각이 없으므로 다른 흔적으로 좁힙니다. 부팅 때 볼륨을 연 시점은 저널의 `systemd-cryptsetup@볼륨이름.service` 유닛 기록으로 보고, 저널 시각 해석은 [systemd 저널](../logging/systemd-journal/index.md) 쪽을 따릅니다. 부팅 흐름 전체는 [부팅과 종료 기록](../../02-artifacts/system-info/boot-shutdown.md) 쪽에 있습니다. crypttab·키 파일·머리글 백업 파일은 파일 시스템의 시각으로 만든 때와 고친 때를 가늠할 수 있습니다. 볼륨을 설치할 때 만들었다면 설치 시각과 가깝습니다.

### 배포판 차이

설치기 코드 기준으로, 설치할 때 암호화를 고르면 아래처럼 만듭니다. 볼륨 이름은 검체의 `/etc/crypttab` 첫 칸과 `lsblk` 결과로 확인합니다.

| 항목 | Ubuntu 24.04 (subiquity) | RHEL 9 (anaconda) |
|---|---|---|
| 암호화 선택지 | 안내 설치의 LVM_LUKS, ZFS_LUKS_KEYSTORE[15] | 자동 파티션에서 암호화 선택[14] |
| 배치 | `/boot` 를 ext4 파티션으로 따로 두고, 나머지 파티션을 VG `ubuntu-vg` 로 쓰며 암호는 그 VG 설정에 붙음[15] | LVM·Btrfs 로 쓸 구성원 파티션을 `lvmpv`·`btrfs` 대신 `luks` 형식으로 만듦[14] |
| 복구 키 | 복구 키 파일 이름의 기본 끝부분이 `recovery-key-VG이름.txt`(예: `recovery-key-ubuntu-vg.txt`)[15] | 검체로 확인 |

Ubuntu 의 복구 키 파일이 사용자 저장소나 이동식 매체에 남아 있으면 볼륨을 여는 단서가 되므로 이 이름으로 찾아봅니다.

### 지우기·조작에 남는 것

`cryptsetup erase` 는 키 슬롯만 지우고 데이터 영역은 덮어쓰지 않습니다[8]. 같은 장치에 `luksFormat` 을 다시 해도 새 머리글과 키 슬롯만 만들 뿐 데이터 영역은 그대로입니다[9]. 두 경우 모두 옛 머리글 백업이 있으면 옛 데이터를 풀 수 있습니다[8][9].

`luksHeaderBackup` 으로 만든 파일과 백업할 때 유효했던 암호가 있으면, 나중에 장치에서 그 암호를 바꾸거나 지웠어도 데이터를 풀 수 있습니다[7]. 백업 파일 이름에는 정해진 규칙이 없으므로 크기와 매직 `LUKS\xba\xbe` 로 찾습니다.

머리글의 키 슬롯 영역을 덮어쓰면 복호는 영구히 불가능합니다. LUKS1 은 키 슬롯마다 256비트 salt 가 있고, 이 값은 다시 만들 수 없습니다[5]. 새 파일 시스템을 만들거나 RAID 구성원으로 넣는 일도 머리글을 덮어씁니다[5].

SSD 와 플래시 저장 장치는 웨어 레벨링 때문에 옛 키 슬롯과 머리글이 장치 안쪽 예비 영역에 오래 남을 수 있어, 머리글을 덮어써도 옛 암호가 살아 있을 수 있습니다[5].

## 함정

**장치 앞에 매직이 없다고 암호화가 없는 것은 아닙니다.** 머리글을 다른 장치나 파일에 따로 둔 볼륨(crypttab 의 `header=`)은 데이터 장치 앞에 LUKS 매직이 없습니다[11][5]. 커널 명령줄의 `rd.luks.options=` 에 `header=` 가, `rd.luks.data=` 에 데이터 장치가 적혀 있을 수도 있습니다[12]. plain dm-crypt 도 머리글이 없습니다[5].

**주 머리글만 지워진 LUKS2 볼륨이 있습니다.** 장치 처음이 0 으로 덮였어도 보조 머리글 위치에 `SKUL\xba\xbe` 가 남아 있을 수 있습니다[3]. libblkid 의 안전 검사(safeprobe) 방식에서는 보조 머리글을 찾지 않습니다[10].

**`blkid` 가 한 장치에서 LUKS 와 ext2/swap 을 함께 볼 수 있습니다.** 옛 cryptsetup 이 머리글을 만들 때 이전 서명을 다 지우지 않은 경우입니다[5]. 두 결과가 나오면 이전 파일 시스템의 잔재를 의심합니다.

**LUKS2 subsystem 칸이 `HW-OPAL` 이면** 하드웨어 자체 암호화(OPAL)를 함께 쓰는 볼륨이고, libblkid 는 잠긴 OPAL 장치도 이 머리글로 LUKS 로 알아봅니다[10]. 이 경우 `erase` 가 키를 하드웨어에서 지우므로 머리글 백업으로도 복구할 수 없습니다[8].

**키 파일은 암호화한 루트 안에 있을 수 있습니다.** `/etc/cryptsetup-keys.d/` 는 루트 파일 시스템 안이라, 루트를 연 뒤에야 다른 데이터 볼륨의 키 파일이 보입니다[11]. 라이브 수집에서 `/etc` 를 통째로 모으면 crypttab 과 이 폴더가 함께 들어옵니다[16].

**열린 볼륨의 키는 전원을 끄면 사라집니다.** 매핑이 열려 있는 LUKS1 볼륨은 device-mapper 표에서 볼륨 키를 다시 얻는 복구 절차가 있습니다[5]. LUKS2 는 키를 커널 keyring 에 두므로 `--disable-keyring` 으로 열지 않았다면 이 절차가 통하지 않습니다[5]. 암호를 모르는 채로 켜진 시스템을 만났다면 전원을 끄기 전에 [메모리 수집](../../03-techniques/acquisition/memory-acquisition.md)과 복호된 `/dev/mapper` 장치의 논리 이미지 수집을 먼저 검토합니다. 메모리 이미지 분석은 [메모리 분석](../../03-techniques/analysis/memory-analysis.md) 쪽에 있습니다. `luksDump --dump-volume-key` 는 암호를 알아야 볼륨 키를 출력합니다[6].

**암호화 스왑은 전원을 끈 뒤 읽을 수 없습니다.** crypttab 에 `/dev/urandom` 과 `swap` 으로 적은 스왑은 부팅마다 키와 스왑 서명의 UUID 가 바뀝니다[11][5]. 이런 스왑은 crypttab 에서 UUID 로 가리킬 수 없어 장치 경로로 적습니다[5].

## 도구

| 도구 | 쓰임 |
|---|---|
| `cryptsetup luksDump` | 머리글·키 슬롯·토큰 정보, `--dump-json-metadata` 로 LUKS2 JSON[6] |
| `blkid`, `lsblk -f` | `crypto_LUKS` 형식과 UUID·LABEL 표시(UAC 가 모으는 명령)[10][16] |
| dissect.fve | LUKS1·LUKS2·BitLocker·VeraCrypt 파서, 머리글 위치 찾기, 암호·키 파일로 열기[13] |
| 헥스 편집기 | 0 과 보조 머리글 후보 위치에서 매직 확인 |
| `/proc/crypto` | 실행 중 커널에 적재된 암호 방식[1] |

## 참고 문헌

1. Linux kernel, `Documentation/admin-guide/device-mapper/dm-crypt.rst`. https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/device-mapper/dm-crypt.rst
2. cryptsetup, `lib/luks1/luks.h`. https://github.com/mbroz/cryptsetup/blob/main/lib/luks1/luks.h
3. cryptsetup, `lib/luks2/luks2.h`. https://github.com/mbroz/cryptsetup/blob/main/lib/luks2/luks2.h
4. cryptsetup, `lib/luks2/luks2_json_metadata.c`. https://github.com/mbroz/cryptsetup/blob/main/lib/luks2/luks2_json_metadata.c
5. cryptsetup, `FAQ.md`. https://github.com/mbroz/cryptsetup/blob/main/FAQ.md
6. cryptsetup, `man/cryptsetup-luksDump.8.adoc`. https://github.com/mbroz/cryptsetup/blob/main/man/cryptsetup-luksDump.8.adoc
7. cryptsetup, `man/cryptsetup-luksHeaderBackup.8.adoc`. https://github.com/mbroz/cryptsetup/blob/main/man/cryptsetup-luksHeaderBackup.8.adoc
8. cryptsetup, `man/cryptsetup-erase.8.adoc`. https://github.com/mbroz/cryptsetup/blob/main/man/cryptsetup-erase.8.adoc
9. cryptsetup, `man/cryptsetup-luksFormat.8.adoc`. https://github.com/mbroz/cryptsetup/blob/main/man/cryptsetup-luksFormat.8.adoc
10. util-linux, `libblkid/src/superblocks/luks.c`. https://github.com/util-linux/util-linux/blob/master/libblkid/src/superblocks/luks.c
11. systemd, `man/crypttab.xml`. https://github.com/systemd/systemd/blob/main/man/crypttab.xml
12. systemd, `man/systemd-cryptsetup-generator.xml`. https://github.com/systemd/systemd/blob/main/man/systemd-cryptsetup-generator.xml
13. dissect.fve, `README.md`·`dissect/fve/luks/luks.py`. https://github.com/fox-it/dissect.fve/blob/main/README.md , https://github.com/fox-it/dissect.fve/blob/main/dissect/fve/luks/luks.py
14. anaconda, `pyanaconda/modules/storage/partitioning/automatic/utils.py`. https://github.com/rhinstaller/anaconda/blob/main/pyanaconda/modules/storage/partitioning/automatic/utils.py
15. subiquity, `subiquity/server/controllers/storage.py`. https://github.com/canonical/subiquity/blob/main/subiquity/server/controllers/storage.py
16. UAC, `artifacts/files/system/etc.yaml`·`artifacts/live_response/storage/` (blkid.yaml, lsblk.yaml). https://github.com/tclahr/uac/tree/main/artifacts
