---
title: "키 계층"
parent: "파일볼트"
grand_parent: "기반 · 보안·보호"
nav_order: 370
---

# 키 계층 (VEK·KEK)

APFS 암호화 볼륨은 볼륨 암호화 키 (Volume Encryption Key, VEK)로 내용을 암호화하고 그 VEK를 키 암호화 키 (Key Encryption Key, KEK)로 감싸 두며, 감싼 키 사본은 컨테이너와 볼륨의 키백 (keybag)에 들어 있습니다.

## 이 구조를 쓰는 곳

APFS 볼륨을 만들면 기본으로 VEK가 함께 생깁니다 [1]. 파일볼트를 켜지 않은 T2·Apple silicon 맥도 볼륨이 이미 암호화돼 있고, 이때 VEK를 지키는 수단은 Secure Enclave 안의 하드웨어 UID 하나뿐입니다 [1]. 파일볼트를 켜면 KEK를 사용자 암호와 하드웨어 UID를 함께 써서 보호하고, 부팅할 때 자격 증명을 묻습니다 [1]. 그래서 파일볼트를 나중에 켜면 데이터가 이미 암호화돼 있어 켜는 작업이 바로 끝납니다 [1].

이 페이지의 키백 구조와 복호 순서는 외장 저장장치처럼 소프트웨어 암호화를 쓰는 볼륨의 구조입니다 [4]. 하드웨어 암호화를 쓰는 내장 디스크의 사정은 [보안 칩과 데이터 보호 (T2·Apple Silicon·Secure Enclave)](secure-enclave.md)에서 다룹니다. 컨테이너·볼륨·슈퍼블록 같은 APFS 기본 구조는 [APFS 구조 (APFS)](../../disk-volume/apfs/index.md)를 먼저 봅니다.

## 키가 이어지는 순서

| 키 | 하는 일 | 보호 수단 |
|---|---|---|
| 미디어 키 (Media key) | 모든 VEK를 감쌉니다. 기밀성을 더하려는 키가 아니라 빠르고 안전하게 지우려고 둔 키입니다 [1] | — |
| VEK | 볼륨의 암호화된 내용에 접근하는 기본 키이고, macOS에서는 메타데이터도 VEK로 암호화합니다 [4] | KEK가 감쌈 |
| KEK | VEK를 풉니다 (unwrap) [4] | 파일볼트 켬: 사용자 암호 + 하드웨어 UID / 끔: 하드웨어 UID만 [1] |

KEK를 푸는 방법은 사용자 암호, 개인 복구 키, 기관 복구 키, iCloud 복구 키 네 가지이고, 이 가운데 iCloud 복구 키의 구조는 공개 명세에 없습니다 [4]. 복구 키 세 종류는 [복구 키 (Recovery Key)](recovery-key.md)에서 다룹니다.

사용자 암호로 파일 하나를 읽으려면 암호로 KEK를 풀고, KEK로 VEK를 풀고, VEK로 파일 시스템 B-트리를 복호한 다음, 마지막으로 VEK로 파일 데이터를 복호합니다 [4]. 암호화 알고리즘은 AES-XTS입니다 [1][4].

보안 토큰 (Secure Token)은 사용자 암호로 보호하는 감싼 KEK이고, 사용자를 만들 때와 처음 암호를 정할 때, APFS 볼륨에 처음 로그인할 때 생깁니다 [2]. 파일볼트를 켠 뒤에는 예전에 하드웨어 UID로만 보호하던 키로 볼륨을 풀 수 없게 막는 안티 리플레이 (anti-replay) 장치가 있습니다 [1].

## 구조

### 키백이 있는 곳

macOS에서는 컨테이너와 볼륨에 키백(`kb_locker_t`)이 하나씩 있습니다 [4]. 컨테이너 키백의 위치는 컨테이너 슈퍼블록 `nx_superblock_t` 의 `nx_keylocker` 필드(`prange_t`)에 적혀 있고, 컨테이너 키백에는 볼륨마다 감싼 VEK와 그 볼륨 키백의 위치가 들어 있습니다. 볼륨 키백에는 사용자 암호와 복구 키로 각각 감싼 KEK 사본이 여러 개 들어 있습니다 [4].

키백은 컨테이너 UUID나 볼륨 UUID로 암호화해 두고, 풀어 낸 키백 객체는 아래 세 형식 가운데 하나입니다. 셋 다 `media_keybag_t` 구조이고, 이 구조는 객체 머리 `obj_phys_t mk_obj` 뒤에 `kb_locker_t mk_locker` 가 붙은 모양입니다 [4].

| 객체 형식 | 값 | 바이트 순서로 본 모양 [3] |
|---|---|---|
| `OBJECT_TYPE_CONTAINER_KEYBAG` | `'keys'` (0x6b657973) | `73 79 65 6b` ("syek") |
| `OBJECT_TYPE_VOLUME_KEYBAG` | `'recs'` (0x72656373) | `73 63 65 72` ("scer") |
| `OBJECT_TYPE_MEDIA_KEYBAG` | `'mkey'` | — |

### kb_locker_t (머리 16바이트)

필드와 뜻은 [4], 오프셋은 [3] 기준입니다.

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 2 | `kl_version` | `APFS_KEYBAG_VERSION` = 2 (1은 시제품용이라 호환되지 않음) |
| 2 | 2 | `kl_nkeys` | 항목 수 |
| 4 | 4 | `kl_nbytes` | `kl_entries` 데이터 크기 |
| 8 | 8 | padding | 예약 |
| 16 | — | `kl_entries[]` | `keybag_entry_t` 배열 |

### keybag_entry_t (머리 24바이트)

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 16 | `ke_uuid` | 컨테이너 키백: 볼륨 UUID / 볼륨 키백: 사용자 UUID |
| 16 | 2 | `ke_tag` | 키백 태그 |
| 18 | 2 | `ke_keylen` | 데이터 길이. `APFS_VOL_KEYBAG_ENTRY_MAX_SIZE`(512)보다 작아야 함 |
| 20 | 4 | padding | 예약 |
| 24 | — | `ke_keydata[]` | 데이터 |

UUID를 읽는 법은 [식별자 읽기 (UUID·UID·GUID)](../../value-decoding/uuid-uid.md)에 있습니다.

### 키백 태그

| 값 | 이름 | 뜻 [4] |
|---|---|---|
| 0 | `KB_TAG_UNKNOWN` | 디스크에 나타나지 않음 |
| 1 | `KB_TAG_RESERVED_1` | 예약 |
| 2 | `KB_TAG_VOLUME_KEY` | 감싼 VEK. 컨테이너 키백에만 있음 |
| 3 | `KB_TAG_VOLUME_UNLOCK_RECORDS` | 컨테이너 키백: 볼륨 키백 위치(`prange_t`) / 볼륨 키백: 감싼 KEK. macOS 전용 |
| 4 | `KB_TAG_VOLUME_PASSPHRASE_HINT` | 암호 힌트(평문). 볼륨 키백에만 있고 macOS 전용 |
| 5 | `KB_TAG_WRAPPING_M_KEY` | 미디어 키를 감싸는 키. iOS 전용 |
| 6 | `KB_TAG_VOLUME_M_KEY` | 볼륨 미디어 키를 감싸는 키. iOS 전용 |
| 0xF8 | `KB_TAG_RESERVED_F8` | 예약 |

### 감싼 KEK의 안쪽

아래 내용은 Apple 명세에는 없고, 공개 분석 문서 [3]가 관찰해 적은 값입니다. 볼륨 키백의 KEK 항목 값은 DER과 비슷한 태그 구조이고, 바깥 `0x30` 안에 `0x80`(뜻 모름), `0x81`(HMAC), `0x82`(salt), `0xa3`(감싼 KEK 객체)가 있습니다. `0xa3` 안에는 `0x81` 볼륨 UUID, `0x82` KEK 메타데이터, `0x83` 감싼 KEK 데이터, `0x84` 반복 횟수, `0x85` PBKDF2 salt가 들어 있고, KEK 메타데이터 오프셋 0의 플래그 비트로 AES-128과 AES-256을 구분합니다 [3].

### 볼륨 슈퍼블록에 남는 암호화 흔적

| 필드 | 오프셋 [3] | 크기 | 뜻 [4] |
|---|---|---|---|
| `apfs_meta_crypto` (`wrapped_meta_crypto_state_t`) | 96 | 20 | 메타데이터 암호화 키 정보 |
| `apfs_fs_flags` (uint64) | 264 | 8 | 볼륨 플래그 |

`apfs_fs_flags` 에서 `APFS_FS_UNENCRYPTED`(0x1)가 켜져 있으면 암호화하지 않은 볼륨이고, `APFS_FS_ONEKEY`(0x8)가 켜져 있으면 볼륨의 모든 파일을 VEK 하나로 암호화한 볼륨입니다. `APFS_FS_ONEKEY` 는 macOS에서만 쓰고, iOS는 언제나 파일마다 키를 따로 씁니다 [4].

### 보호 등급

파일의 보호 등급 값(`cp_key_class_t`)은 `CP_EFFECTIVE_CLASSMASK`(0x1f)로 걸러 읽습니다 [4].

| 값 | 등급 | 뜻 [4] |
|---|---|---|
| 0 | DIR_NONE | iOS 전용 |
| 1 | A | complete |
| 2 | B | completeUnlessOpen |
| 3 | C | completeUntilFirstUserAuthentication |
| 4 | D | none |
| 6 | F | D와 같지만 키를 영구 저장하지 않음. VM 스왑 같은 임시 파일용 |
| 14 | M | 명세에 설명 없음 |

Apple silicon 맥은 데이터 보호 등급 C와 볼륨 키를 씁니다 [1].

## 읽는 법

VEK를 얻는 순서는 아래와 같습니다 [4]. 시작하기 전에 볼륨에 `APFS_FS_ONEKEY` 플래그가 있는지 먼저 보는데, 파일마다 키를 따로 쓰는 볼륨은 하드웨어 암호화가 있어야 풀리기 때문입니다 [4].

1. 컨테이너 슈퍼블록의 `nx_keylocker` 로 컨테이너 키백 위치를 찾습니다.
2. 컨테이너 UUID로 컨테이너 키백을 풉니다. 방식은 RFC 3394입니다.
3. UUID가 볼륨 UUID이고 태그가 `KB_TAG_VOLUME_KEY` 인 항목이 감싼 VEK입니다.
4. UUID가 볼륨 UUID이고 태그가 `KB_TAG_VOLUME_UNLOCK_RECORDS` 인 항목이 볼륨 키백 위치입니다.
5. 볼륨 UUID로 볼륨 키백을 풉니다.
6. UUID가 사용자의 Open Directory UUID이고 태그가 `KB_TAG_VOLUME_UNLOCK_RECORDS` 인 항목이 감싼 KEK입니다.
7. 사용자 암호로 KEK를 풀고, KEK로 VEK를 풉니다(RFC 3394 AES 키 감싸기).

VEK를 얻으면 루트 파일 시스템 트리(`apfs_root_tree_oid`)를 VEK로 AES-XTS 복호하고, 파일 익스텐트의 `crypto_id` 를 트윅으로 써서 데이터 블록을 복호합니다 [4]. libyal 문서는 AES-XTS 단위 크기를 섹터 크기로 보고 512바이트로 가정합니다 [3]. 이 페이지는 정당하게 확보한 자격 증명으로 구조를 풀어 읽는 순서까지만 다루고, 암호를 알아내는 방법은 다루지 않습니다. 압수한 암호화 볼륨을 어떤 순서로 다룰지는 [암호화된 증거 다루기 (Encrypted Evidence)](../../../03-techniques/analysis/encrypted-evidence/index.md)에 있습니다.

아래는 명세의 필드 배치로 만든 예시이고, 실제 검체에서 뽑은 값이 아닙니다. 복호한 컨테이너 키백에서 `kb_locker_t` 머리와 첫 항목 머리를 읽는 모양을 보여 주며, 길이와 UUID 자리는 글자로 비워 두었습니다.

```
오프셋  바이트                                              읽는 법
0x00    02 00 02 00 NN NN NN NN PP PP PP PP PP PP PP PP     kl_version=2, kl_nkeys=2, kl_nbytes, padding
0x10    UU UU UU UU UU UU UU UU UU UU UU UU UU UU UU UU     ke_uuid (볼륨 UUID)
0x20    02 00 LL LL PP PP PP PP                             ke_tag=2 (KB_TAG_VOLUME_KEY), ke_keylen, padding
0x28    ..                                                  ke_keydata (감싼 VEK)
```

## 포렌식에서 중요한 점

암호 힌트는 태그 4 항목에 평문으로 저장하지만, 그 항목이 들어 있는 볼륨 키백 자체를 볼륨 UUID로 암호화해 두기 때문에 디스크 바이트를 그대로 검색해서 보이는 값은 아닙니다 [4]. 볼륨 키백 항목 가운데 개인 복구 키 항목을 알아보는 법은 [복구 키 (Recovery Key)](recovery-key.md)에 있습니다. 볼륨 키백에서 감싼 KEK 항목에 적힌 사용자 UUID는 [사용자 계정 (Local Accounts)](../../../02-artifacts/system-account/user-accounts/index.md)의 계정 목록과 맞춰 봅니다.

볼륨 슈퍼블록을 안전하게 지워 UUID를 없애면 키백을 읽을 수 없게 되고 볼륨 내용에도 접근할 수 없으며, 컨테이너 쪽은 체크포인트 영역의 모든 사본과 블록 0 사본을 다 없애야 같은 효과가 납니다 [4]. 미디어 키가 모든 VEK를 감싸는 이유도 빠르고 안전하게 지우기 위해서입니다 [1]. 이렇게 UUID가 사라진 암호화 볼륨은 내용에 접근할 수 없으므로, [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)를 계획할 때 슈퍼블록과 키백이 남아 있는지부터 확인합니다.

`apfs_fs_flags` 는 이미지에서 소프트웨어 암호화 볼륨인지를 처음 가려내는 데 쓸 수 있습니다. 다만 T2·Apple silicon 내장 볼륨에서 이 플래그가 어떻게 찍히는지는 공개된 자료가 없으니, 플래그 하나로 암호화 여부를 단정하지 않습니다.

## 함정

키백 태그 번호가 자료마다 다릅니다. libyal 문서 [3]는 1을 wrapping key, 2를 volume master key로 적고 볼륨 키백의 3을 "volume key" 로 적는데, Apple 명세 [4]와 어긋나서 이 페이지는 명세 값을 따랐습니다. 도구 결과에 태그 이름이 나오면 어느 쪽 번호 체계인지 먼저 확인합니다.

객체 형식 값은 리틀엔디언이라서 바이트 그대로 보면 `'keys'` 가 "syek", `'recs'` 가 "scer" 로 거꾸로 보입니다 [3]. 헥스 검색어를 만들 때 이 순서를 지킵니다.

명세 판은 2020-06-22 판이고 소프트웨어 암호화만 설명합니다 [4]. 감싼 KEK 안쪽의 태그 구조는 Apple이 보증한 값이 아니라 공개 분석 문서의 관찰값입니다.

## 도구

형식을 직접 따라가려면 libyal libfsapfs 프로젝트의 APFS 형식 문서 [3]를 명세 [4]와 나란히 놓고 봅니다. 두 자료가 어긋나는 곳이 있으니, 도구 결과를 증거로 쓰기 전에 [도구 검증 (Tool Validation)](../../../03-techniques/reporting/tool-validation.md)의 절차대로 결과를 확인합니다.

## 참고 문헌

1. Apple Platform Security — Volume encryption with FileVault in macOS — https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/web
2. Apple Platform Security — Managing FileVault in macOS — https://support.apple.com/guide/security/managing-filevault-sec8447f5049/web
3. libyal libfsapfs — Apple File System (APFS) format 문서 — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
4. Apple, Apple File System Reference (2020-06-22 판, PDF) — https://developer.apple.com/support/downloads/Apple-File-System-Reference.pdf
