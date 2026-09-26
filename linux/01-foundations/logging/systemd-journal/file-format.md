---
title: "저널 파일 구조"
parent: "systemd 저널"
grand_parent: "기반 · 로그 체계"
nav_order: 200
---

# 저널 파일 구조 (Journal File Format)

systemd 저널 파일(`.journal`)은 고정 머리 뒤에 객체를 덧붙여 가는 이진 파일이고, 머리 몇 바이트만 읽어도 파일의 상태·기계·시각 범위를 알 수 있습니다.

## 이 형식을 쓰는 아티팩트

systemd-journald 가 쓰는 모든 저널 파일이 이 형식입니다. 활성 파일 `system.journal`·`user-UID.journal`, 회전한 보관 파일 `system@….journal`, 비정상 종료·손상으로 치운 `….journal~` 가 모두 같은 구조입니다[2][10]. 파일이 어느 폴더에 생기는지, 어떤 설정에 따라 영구·휘발로 나뉘는지는 [systemd 저널](index.md) 에서 다룹니다.

명세는 systemd 246 을 기준으로 쓰였고, 명세와 코드가 다르면 코드를 따릅니다[1]. 아래 오프셋은 명세의 구조체에서 나온 값이고, plaso·dissect.target 의 파서 정의와도 같습니다[1][7][8].

## 구조

### 기본 규칙

오프셋·크기·시각·해시 같은 정수 값은 리틀 엔디언 (little-endian) 이고, 오프셋은 파일 처음부터 셉니다[1]. 구조체는 8바이트 경계에 맞춰 놓고 8바이트 배수로 채웁니다[1]. 시각 값은 모두 마이크로초 단위이고, 벽시계 시각 (realtime) 은 1970-01-01 UTC 부터 센 값, 단조 시각 (monotonic) 은 커널 부팅 ID 와 짝을 이루는 값입니다[1]. 단조 시각은 보통 부팅 시점부터 세지만 컨테이너에서는 그렇지 않습니다[1].

파일은 머리 (Header) 로 시작하고 바로 뒤에 객체가 이어집니다[1]. 새 데이터를 쓸 때는 새 객체를 먼저 파일 끝에 덧붙이고, 다 쓴 뒤에 앞쪽 색인에 연결합니다[1]. 한 번 쓴 데이터는 색인용 연결 값 말고는 대부분 다시 고치지 않습니다[1].

### 파일 머리

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x00 | 8 | signature | ASCII `LPKSHHRH` |
| 0x08 | 4 | compatible_flags | 1 = SEALED, 2 = TAIL_ENTRY_BOOT_ID, 4 = SEALED_CONTINUOUS |
| 0x0C | 4 | incompatible_flags | 1 = XZ, 2 = LZ4, 4 = KEYED_HASH, 8 = ZSTD, 16 = COMPACT |
| 0x10 | 1 | state | 0 = OFFLINE, 1 = ONLINE, 2 = ARCHIVED |
| 0x11 | 7 | reserved | 0 |
| 0x18 | 16 | file_id | 파일을 만들 때 무작위로 정한 ID |
| 0x28 | 16 | machine_id | 이 파일을 쓴 기계 ID |
| 0x38 | 16 | tail_entry_boot_id | 마지막 항목의 부팅 ID |
| 0x48 | 16 | seqnum_id | 일련번호 묶음 ID |
| 0x58 | 8 | header_size | 머리 크기 |
| 0x60 | 8 | arena_size | 머리 뒤 영역 크기 |
| 0x68 | 8 | data_hash_table_offset | DATA 해시 표 내용 위치(객체 머리가 아님) |
| 0x70 | 8 | data_hash_table_size | |
| 0x78 | 8 | field_hash_table_offset | FIELD 해시 표 내용 위치 |
| 0x80 | 8 | field_hash_table_size | |
| 0x88 | 8 | tail_object_offset | 마지막 객체 위치 |
| 0x90 | 8 | n_objects | 객체 수 |
| 0x98 | 8 | n_entries | 항목(ENTRY) 수 |
| 0xA0 | 8 | tail_entry_seqnum | 마지막 항목 일련번호 |
| 0xA8 | 8 | head_entry_seqnum | 첫 항목 일련번호 |
| 0xB0 | 8 | entry_array_offset | 전체 항목 배열 사슬의 첫 배열 |
| 0xB8 | 8 | head_entry_realtime | 첫 항목 벽시계 시각 |
| 0xC0 | 8 | tail_entry_realtime | 마지막 항목 벽시계 시각 |
| 0xC8 | 8 | tail_entry_monotonic | 마지막 항목 단조 시각 |
| 0xD0 | 8 | n_data | systemd 187 에서 추가 |
| 0xD8 | 8 | n_fields | 187 |
| 0xE0 | 8 | n_tags | 189 |
| 0xE8 | 8 | n_entry_arrays | 189 |
| 0xF0 | 8 | data_hash_chain_depth | 246 |
| 0xF8 | 8 | field_hash_chain_depth | 246 |
| 0x100 | 4 | tail_entry_array_offset | 252 |
| 0x104 | 4 | tail_entry_array_n_entries | 252 |
| 0x108 | 8 | tail_entry_offset | 254 |

`n_data` 부터는 나중에 붙은 필드라서 `header_size` 를 먼저 보고 그 안에 들어 있을 때만 읽습니다[1]. 판마다 머리 크기는 187 이전 208, 187 은 224, 189 는 240, 246 은 256, 252 는 264, 254 는 272 바이트입니다[1][7]. RHEL 9 의 systemd 는 252 라서[3] 새로 만든 파일의 머리는 264 바이트일 가능성이 높습니다. Ubuntu 24.04 검체는 `header_size` 값으로 같은 방식으로 가늠합니다.

`compatible_flags` 도 판에 따라 다릅니다. 최신 코드는 새 파일에 TAIL_ENTRY_BOOT_ID 를 늘 켜고, 봉인할 때는 SEALED 와 SEALED_CONTINUOUS(4) 를 함께 켭니다[2][11]. RHEL 9 코드는 봉인할 때 SEALED 만 켜고 TAIL_ENTRY_BOOT_ID 는 켜지 않습니다[3].

현재 쓰는 영역은 `header_size + arena_size` 까지입니다[1]. journald 는 파일을 8MB 단위로 미리 할당하고 `arena_size` 도 그만큼 늘리므로[2], 파일 뒷부분에는 아직 객체가 없는 0 구역이 있는 것이 정상입니다.

### 객체

객체는 모두 16바이트 공통 머리로 시작합니다[1].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| +0 | 1 | type | 0 UNUSED, 1 DATA, 2 FIELD, 3 ENTRY, 4 DATA_HASH_TABLE, 5 FIELD_HASH_TABLE, 6 ENTRY_ARRAY, 7 TAG |
| +1 | 1 | flags | DATA 에만 씀: 1 = XZ, 2 = LZ4, 4 = ZSTD 압축 |
| +2 | 6 | reserved | 0 |
| +8 | 8 | size | 공통 머리를 포함한 객체 전체 크기 |

객체 종류별 나머지 필드는 아래와 같습니다[1][8]. 압축형 (compact) 은 머리의 `incompatible_flags` 에 COMPACT(16) 가 켜진 파일입니다.

| 종류 | +16 부터의 필드 | 압축형에서 다른 점 |
|---|---|---|
| DATA | hash(8), next_hash_offset(8), next_field_offset(8), entry_offset(8, 이 값을 쓰는 첫 ENTRY), entry_array_offset(8), n_entries(8), +64 payload(`필드이름=값`) | +64 tail_entry_array_offset(4), +68 tail_entry_array_n_entries(4), +72 payload |
| FIELD | hash(8), next_hash_offset(8), head_data_offset(8), +40 payload(필드 이름만) | 같음 |
| ENTRY | seqnum(8), realtime(8), monotonic(8), boot_id(16), xor_hash(8), +64 items | items 한 칸이 object_offset(8)+hash(8) 16바이트에서 object_offset(4) 4바이트로 줄어듦 |
| DATA_HASH_TABLE·FIELD_HASH_TABLE | 칸마다 head_hash_offset(8), tail_hash_offset(8) | 같음 |
| ENTRY_ARRAY | next_entry_array_offset(8), +24 items(ENTRY 오프셋 8바이트씩) | items 가 4바이트씩 |
| TAG | seqnum(8), epoch(8), tag(32, SHA-256 HMAC) | 같음 |

항목 (ENTRY) 하나는 필드 값 (DATA) 여러 개를 오프셋으로 묶은 것입니다[1]. 같은 `필드이름=값` 은 파일 안에 DATA 객체 하나로만 저장하고, 여러 항목이 그 객체를 함께 가리킵니다[1]. 해시 표 두 개는 파일을 만들 때 첫 두 객체로 만들고, 머리의 해시 표 오프셋은 객체 머리가 아니라 칸이 시작하는 곳을 가리킵니다[1]. 해시 표 칸 수는 DATA 가 최소 2047, FIELD 가 1023 입니다[2].

해시는 KEYED_HASH 가 켜진 파일이면 `file_id` 를 키로 쓰는 siphash24 이고, 아니면 Jenkins lookup3 입니다[1]. ENTRY 의 `xor_hash` 만은 KEYED_HASH 파일에서도 Jenkins 해시를 씁니다[1].

ENTRY_ARRAY 는 사슬로 이어지고, 앞 배열이 차면 두 배 크기의 다음 배열을 붙입니다[1]. 머리의 `entry_array_offset` 에서 시작하는 사슬이 파일의 모든 항목을 차례대로 가리키고, DATA 마다 그 값을 쓰는 항목을 모은 사슬이 따로 있습니다[1].

512바이트보다 큰 DATA 는 기본으로 압축하고, 이 기준은 journald.conf 의 `Compress=` 로 바꿀 수 있습니다[4][2]. LZ4 로 압축한 payload 는 앞 8바이트에 풀린 크기가 있고 그 뒤가 LZ4 블록이며, XZ·ZSTD 는 payload 전체를 그대로 풉니다[7][8]. journald 는 압축을 쓰도록 되어 있으면 파일을 만들 때 해당 알고리즘 비트를 머리에 미리 켭니다[2][3]. KEYED_HASH 와 COMPACT 는 환경 변수 `SYSTEMD_JOURNAL_KEYED_HASH`·`SYSTEMD_JOURNAL_COMPACT` 로 끄지 않는 한 켜서 만들고, 이 동작은 최신 코드와 RHEL 9 코드가 같습니다[2][3]. 압축형 파일은 오프셋을 32비트로 적기 때문에 4GiB 를 넘게 자라지 않습니다[2].

### 파일 상태와 이름

journald 는 쓰려고 파일을 열면 `state` 를 ONLINE(1) 으로, 쓰기를 마치고 닫으면 OFFLINE(0) 으로, 회전한 뒤에는 ARCHIVED(2) 로 바꾸고, 바꾸기 전후에 `fdatasync()` 를 부릅니다[1]. OFFLINE 이 아닌 파일에 쓰라는 요청을 받으면 그 파일은 고치지 않고 회전합니다[1].

회전한 파일 이름은 `원래이름@seqnum_id(16진 32자리)-head_entry_seqnum(16진 16자리)-head_entry_realtime(16진 16자리).journal` 이고, 치운 파일 이름은 `원래이름@치운시각(16진 16자리)-무작위값(16진 16자리).journal~` 입니다[2].

```text
system@44444444444444444444444444444444-000000000000002a-00064861e7e78000.journal
```

위 줄은 이름 짜임을 보여 주려고 만든 예시입니다. 마지막 칸 `00064861e7e78000` 은 1768435200000000 마이크로초, 곧 2026-01-15 00:00:00 UTC 이고, 이 시각은 파일의 첫 항목 시각입니다. `.journal~` 이름이 무엇을 뜻하는지는 [손상·삭제된 저널](corruption.md) 에서 다룹니다.

## 읽는 법

머리에서 시작해 아래 순서로 따라가면 항목을 모두 읽을 수 있습니다[1].

1. 0x00 의 8바이트가 `LPKSHHRH` 인지 봅니다.
2. `incompatible_flags` 에서 압축 알고리즘과 COMPACT 여부를 확인합니다. 모르는 비트가 있으면 읽지 않고 멈춥니다[1].
3. `header_size` 로 머리 뒤쪽 필드가 있는지 판단합니다.
4. `entry_array_offset` 의 ENTRY_ARRAY 부터 `next_entry_array_offset` 이 0 이 될 때까지 사슬을 따라가며 ENTRY 오프셋을 모읍니다. 배열 끝의 0 칸은 아직 쓰지 않은 칸입니다.
5. ENTRY 마다 `items` 의 오프셋을 따라가 DATA 의 payload 를 읽고, 압축 플래그가 있으면 풉니다.

아래는 명세로 만든 헥스 예시이고, 값은 모두 지어낸 것입니다. 머리의 앞 0x68 바이트입니다.

```text
00000000  4C 50 4B 53 48 48 52 48  02 00 00 00 1C 00 00 00   LPKSHHRH........
00000010  01 00 00 00 00 00 00 00  11 11 11 11 11 11 11 11
00000020  11 11 11 11 11 11 11 11  22 22 22 22 22 22 22 22
00000030  22 22 22 22 22 22 22 22  33 33 33 33 33 33 33 33
00000040  33 33 33 33 33 33 33 33  44 44 44 44 44 44 44 44
00000050  44 44 44 44 44 44 44 44  10 01 00 00 00 00 00 00
00000060  F0 FE 7F 00 00 00 00 00
```

`compatible_flags` 는 2 라서 TAIL_ENTRY_BOOT_ID 만 켜져 있고 봉인 (SEALED) 은 꺼져 있습니다. `incompatible_flags` 0x1C 는 KEYED_HASH(4)·ZSTD(8)·COMPACT(16) 를 더한 값입니다. `state` 는 1(ONLINE) 이고, `header_size` 0x110 은 272 바이트라서 254 이후 판이 만든 머리입니다. `arena_size` 0x7FFEF0 에 머리 272 바이트를 더하면 8MB(0x800000) 가 됩니다. 0x18 부터의 네 ID 는 자리만 보여 주려고 같은 바이트로 채웠습니다.

아래는 같은 방식으로 만든 압축형 ENTRY 객체 예시이고, 항목에 필드가 4개 있습니다.

```text
+00  03 00 00 00 00 00 00 00  50 00 00 00 00 00 00 00   type=3(ENTRY), size=0x50
+10  2A 00 00 00 00 00 00 00  00 80 E7 E7 61 48 06 00   seqnum=42, realtime
+20  40 86 95 D6 00 00 00 00  33 33 33 33 33 33 33 33   monotonic, boot_id
+30  33 33 33 33 33 33 33 33  5A 5A 5A 5A 5A 5A 5A 5A   boot_id, xor_hash
+40  40 1F 00 00 90 1F 00 00  E0 1F 00 00 30 20 00 00   DATA 오프셋 4개
```

realtime `0x00064861E7E78000` 은 1768435200000000 마이크로초라서 2026-01-15 00:00:00 UTC 입니다. monotonic `0xD6958640` 은 3600123456 마이크로초라서 `boot_id` 로 가리키는 부팅 뒤 약 1시간입니다. 크기 0x50 은 고정부 64바이트에 4바이트 오프셋 4개를 더한 값입니다. 마이크로초 값을 날짜로 바꾸는 방법은 [Linux 의 시각 값](../../value-decoding/time-values.md) 에서 다룹니다.

## 포렌식에서 중요한 점

머리만으로 파일의 요약을 얻을 수 있습니다. `head_entry_realtime`·`tail_entry_realtime` 은 파일이 담은 첫 항목과 마지막 항목의 시각이고, `n_entries` 는 항목 수입니다[1]. 두 시각 모두 UTC 기준 마이크로초입니다[1]. 파일이 닫힌 시각이나 회전한 시각은 머리 어디에도 없습니다.

`state` 는 파일이 어떻게 끝났는지 알려 줍니다. 수집한 보관 파일이 ARCHIVED 가 아니라 ONLINE 이면 쓰는 도중에 멈춘 파일일 가능성이 있습니다[1][2]. 살아 있는 시스템에서 활성 파일을 복사해도 ONLINE 이 정상이고, 동기화 규칙이 느슨해서 끝부분 구조가 잠시 어긋나 보일 수 있습니다[1].

`machine_id` 는 파일을 쓴 기계를 가리킵니다. journald 는 머리의 `machine_id` 가 자기 기계와 다르면 그 파일에 쓰지 않고 회전합니다[1]. 다른 곳에서 옮겨 온 파일인지 볼 때 폴더 이름의 기계 ID 와 비교합니다. `seqnum_id` 가 같은 파일끼리는 일련번호가 1부터 이어지고 겹치지 않으므로, 시스템 파일과 사용자 파일을 한 흐름으로 맞출 때 씁니다[1]. 같은 번호 묶음을 시스템 파일과 사용자 파일이 나눠 쓰므로, 한 파일 안에서 번호가 건너뛴 것만으로 항목이 빠졌다고 볼 수는 없습니다[1].

항목은 일련번호 순서로 쓰고, 같은 부팅 안에서는 단조 시각도 커집니다[1]. 벽시계 시각은 시계를 고치지 않는 한 커지므로[1], 일련번호는 이어지는데 realtime 만 뒤로 가면 시계가 바뀐 지점일 가능성이 있습니다. `journalctl --header` 로 머리를 보면 시계가 틀린 채 부팅해 순서가 어긋난 항목을 찾는 데 도움이 됩니다[5].

봉인 (Forward Secure Sealing) 을 쓰는 파일은 `compatible_flags` 에 SEALED 가 켜지고 TAG 객체가 들어 있습니다[1][2]. TAG 의 HMAC 은 앞 태그 이후에 쓴 객체들로 계산하지만, 나중에 바뀔 수 있는 연결 오프셋 같은 필드는 계산에서 뺍니다[1].

지운 데이터 쪽에서 보면, 새 객체는 파일 끝에 덧붙이고 한 번 쓴 데이터는 색인용 연결 값 말고는 고치지 않습니다[1]. 색인에 연결되기 전에 멈춘 ENTRY 가 파일 끝에 남을 수 있고, 이런 항목은 사슬을 따라가는 도구에는 보이지 않습니다. 파일째 지운 경우와 손상 파일 처리는 [손상·삭제된 저널](corruption.md) 에서 다룹니다.

## 함정

- 원시 파일에서 문자열을 검색하면 놓치는 것이 있습니다. 512바이트보다 큰 DATA 는 압축되어 있고[4], 같은 `필드이름=값` 은 한 번만 저장하므로[1] 문자열이 나온 횟수는 항목 수와 다릅니다.
- 회전한 파일 이름의 16진 시각은 첫 항목 시각입니다[2]. 파일을 닫은 시각으로 읽으면 안 됩니다.
- `tail_entry_monotonic` 은 `compatible_flags` 에 TAIL_ENTRY_BOOT_ID 가 없으면 `tail_entry_boot_id` 와 다른 부팅의 값일 수 있습니다[1]. RHEL 9 가 만든 파일에는 이 비트가 없습니다[3].
- 해시 값은 KEYED_HASH 파일이면 `file_id` 를 키로 계산하므로 같은 값이라도 파일마다 해시가 다릅니다[1]. 파일끼리 해시로 항목을 맞추면 안 됩니다.
- 분석 PC 의 systemd 가 검체보다 오래되면 모르는 `incompatible_flags` 비트(COMPACT·ZSTD 등) 때문에 파일을 못 열 수 있습니다[1].
- 파일 뒤쪽 0 구역은 미리 할당한 빈 공간입니다[2]. dissect.target 은 사슬이 가리키는 곳에서 UNUSED(0) 객체를 만나면 "아직 쓰지 않은 할당 공간" 이라는 경고를 내고 멈춥니다[8].

## 도구

| 도구 | 읽는 방식 | 참고 |
|---|---|---|
| `journalctl --header --file=파일` | 머리 필드를 사람이 읽는 꼴로 출력(State, Compatible flags, Incompatible flags, Header size, Head/Tail realtime timestamp 등)[2][5] | 읽는 방법 전반은 [journalctl 로 읽기](journalctl.md) |
| plaso `systemd_journal` 파서 | `entry_array_offset` 부터 ENTRY_ARRAY 사슬을 따라감, 머리 크기 208·224·240·256·264·272 만 받음[7] | |
| dissect.target journal 플러그인 | ENTRY_ARRAY 사슬을 따라감, LZ4·XZ·ZSTD 해제[8] | |
| Velociraptor `parse_journald`(go-journalctl) | `header_size` 부터 객체를 차례로 훑어 ENTRY 를 모두 냄[9] | 색인에 연결되지 않은 ENTRY 도 낼 수 있음 |

도구마다 항목을 찾는 방식이 달라서 같은 파일에서도 결과 항목 수가 다를 수 있습니다. 손상 파일에서 도구별 차이는 [손상·삭제된 저널](corruption.md) 에 정리했습니다. 파일 구조가 아니라 스트림으로 내보낼 때는 `journalctl -o export` 형식을 쓰며, 항목 사이는 줄바꿈 두 번(빈 줄 하나)으로 나누고 이진 필드는 이름·줄바꿈 뒤에 64비트 리틀 엔디언 길이와 데이터를 붙입니다[6].

## 참고 문헌

1. systemd, "Journal File Format" (docs/JOURNAL_FILE_FORMAT.md). https://github.com/systemd/systemd/blob/main/docs/JOURNAL_FILE_FORMAT.md
2. systemd, src/libsystemd/sd-journal/journal-file.c. https://github.com/systemd/systemd/blob/main/src/libsystemd/sd-journal/journal-file.c
3. Red Hat, systemd-rhel9 source-git (meson.build `version : '252'`, src/libsystemd/sd-journal/journal-file.c). https://github.com/redhat-plumbers/systemd-rhel9
4. systemd, man/journald.conf.xml (`Compress=`). https://github.com/systemd/systemd/blob/main/man/journald.conf.xml
5. systemd, man/journalctl.xml (`--header`). https://github.com/systemd/systemd/blob/main/man/journalctl.xml
6. systemd, "Journal Export Formats" (docs/JOURNAL_EXPORT_FORMATS.md). https://github.com/systemd/systemd/blob/main/docs/JOURNAL_EXPORT_FORMATS.md
7. log2timeline plaso, plaso/parsers/systemd_journal.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/systemd_journal.py
8. fox-it dissect.target, dissect/target/plugins/os/unix/log/journal.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/journal.py
9. Velocidex go-journalctl, parser/open.go. https://github.com/Velocidex/go-journalctl/blob/master/parser/open.go
10. systemd, man/systemd-journald.service.xml. https://github.com/systemd/systemd/blob/main/man/systemd-journald.service.xml
11. systemd, src/libsystemd/sd-journal/journal-def.h. https://github.com/systemd/systemd/blob/main/src/libsystemd/sd-journal/journal-def.h
