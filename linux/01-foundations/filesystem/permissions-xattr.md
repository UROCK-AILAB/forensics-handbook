---
title: "권한·확장 속성·ACL·Capabilities"
parent: "기반 · 파일 시스템"
nav_order: 100
---

# 권한·확장 속성·ACL·Capabilities (Permissions·xattr)

파일에 걸린 특권 설정은 네 가지이고 두 곳에 나뉘어 저장됩니다. 모드 비트(SUID·SGID·sticky)와 파일 속성(chattr 의 `i`·`a` 등)은 아이노드 필드에 있고, ACL 과 파일 능력 (file capability) 은 확장 속성 (extended attribute, xattr) 에 있습니다. `ls -l` 은 모드 비트를 보여 주고, ACL 같은 다른 접근 방식이 있으면 모드 문자열 뒤에 `+` 한 글자만 붙입니다[23].

아이노드 필드의 전체 배치는 [아이노드와 익스텐트](ext4/inode-extent.md) 에서 다룹니다. 이 페이지는 특권과 관련된 값만 골라, 무엇이 어디에 어떤 모양으로 저장되는지와 조사에서 어떻게 읽는지를 다룹니다.

## 이 형식을 쓰는 아티팩트

권한을 올린 흔적을 찾을 때는 SUID·SGID 파일과 capability 가 붙은 실행 파일을 봅니다. 지우거나 고치지 못하게 막아 둔 파일은 파일 속성 `i`(바꿀 수 없음)와 `a`(덧붙이기만)로 찾습니다. 공개 수집 도구도 이 네 가지를 따로 모읍니다.

| 수집 항목 | 도구 | 방식 |
|---|---|---|
| SUID 파일 | UAC `suid.yaml` | `/` 아래 일반 파일 중 권한 `-4000`, proc 파일 시스템 제외[17] |
| capability 가 붙은 파일 | UAC `getcap.yaml` | `/` 아래 일반 파일마다 `getcap` 실행, `/proc`·`/sys` 제외[17] |
| 바꿀 수 없는 파일 | UAC `immutable_files.yaml` | `lsattr -d` 결과 첫 필드에 `i` 가 있는 줄, `/dev`·`/proc`·`/run`·`/sys` 제외[17] |
| SUID·SGID 파일 | Velociraptor `Linux.Sys.SUID` | 기본 범위 `/usr/**`, 모드 문자열이 `u`·`g` 로 시작하는 파일[18] |
| 숨김·큰 파일·SUID | Velociraptor `Linux.Detection.AnomalousFiles` | 기본 범위 `/home/**`, `tmp/**`[18] |
| 바꿀 수 없는 파일 | Velociraptor `Linux.Forensics.ImmutableFiles` | ext4 액세서로 아이노드 플래그를 직접 읽음, 기본 범위 `/home/*`[18] |

변경 불가 속성은 공격자가 켜기도 하는 설정이라서 강한 신호가 될 수 있습니다[18]. 수집 절차 전반은 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md), 조사 흐름은 [권한을 올렸나](../../04-scenarios/intrusion/privilege-escalation.md) 와 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md) 에서 다룹니다.

기본 파일 시스템은 배포판마다 다릅니다. 확장 속성의 이름과 뜻은 파일 시스템과 관계없이 같고, 디스크에 놓이는 모양만 다릅니다.

| 배포판 | 설치 기본 파일 시스템 | 확장 속성을 두는 곳 |
|---|---|---|
| Ubuntu 24.04 LTS | ext4[21] | 아이노드 뒤 빈 공간, 또는 `i_file_acl` 이 가리키는 블록(이 페이지에서 설명) |
| RHEL 9 | XFS[22] | 아이노드의 속성 포크 (attribute fork), 형식은 `di_aformat` 이 정함[19] |
| (Btrfs 볼륨) | Btrfs | 트리 항목(`BTRFS_XATTR_ITEM_KEY` = 24)[20] |

XFS·Btrfs 의 구조는 [XFS](xfs.md) 와 [Btrfs](btrfs.md) 를 봅니다.

## 구조

### 모드 비트

모드의 위 4비트(마스크 0170000)는 파일 종류이고 아래 12비트(마스크 07777)가 모드 비트입니다[1]. 특권과 관련된 비트는 세 개입니다[1].

| 8진수 | ext4 `i_mode` 값 | 이름 | 뜻 |
|---|---|---|---|
| 04000 | 0x800 | `S_ISUID` | 실행하면 유효 UID 가 파일 소유자로 바뀜 |
| 02000 | 0x400 | `S_ISGID` | 실행 파일이면 유효 GID 가 파일 그룹으로 바뀜. 디렉터리면 안에서 만든 파일이 디렉터리의 그룹을 물려받고, 안에서 만든 디렉터리도 SGID 를 받음. 그룹 실행 비트가 없는 파일이면 강제 잠금 표시 |
| 01000 | 0x200 | `S_ISVTX` | 디렉터리에 걸리면 파일 소유자·디렉터리 소유자·특권 프로세스만 안의 파일 이름을 바꾸거나 지울 수 있음(sticky) |

ext4 는 이 값을 아이노드 0x00 의 `i_mode` 에 그대로 적습니다[5]. 새로 만든 파일의 소유 UID 는 만든 프로세스의 유효 UID 이고, 소유 GID 는 부모 디렉터리에 SGID 가 있으면 디렉터리의 그룹, 없으면 프로세스의 유효 GID 입니다[1].

`nosuid` 로 마운트한 파일 시스템에서는 커널이 실행할 때 SUID·SGID 비트와 파일 capability 를 따르지 않습니다[2]. 이 옵션은 파일이 아니라 마운트 지점에 걸리므로[2], 이미지에서 찾은 SUID 파일이 실제로 권한을 올릴 수 있었는지는 그 파일 시스템이 어떤 옵션으로 마운트됐는지와 함께 봐야 합니다([마운트 기록](../../02-artifacts/devices/mounts.md)).

### 파일 속성 (chattr·lsattr)

`chattr` 로 켜고 `lsattr` 로 보는 파일 속성은 ext4 아이노드 0x20 의 `i_flags` 에 들어갑니다[5]. 조사에서 자주 보는 속성은 아래와 같습니다.

| 문자 | ext4 `i_flags` | 뜻 |
|---|---|---|
| `i` | 0x10 | 지우기·이름 바꾸기·링크 만들기·쓰기 열기가 막히고 권한·시각·소유자·링크 수 같은 메타데이터도 바꿀 수 없음. root 도 막힘[3][4] |
| `a` | 0x20 | 쓰기는 덧붙이기(`O_APPEND`)로만 열 수 있음. root 도 막힘[3][4] |
| `d` | 0x40 | `dump` 백업에서 뺌[4][5] |
| `A` | 0x80 | 접근해도 atime 을 바꾸지 않음[3][4] |
| `s`·`u` | 0x1·0x2 | 지울 때 0 으로 덮기·내용 보존. ext2·ext3·ext4 는 따르지 않음[4] |

`i` 와 `a` 는 `CAP_LINUX_IMMUTABLE` 능력이 있는 프로세스만 켜고 끌 수 있습니다[3][4]. `E`(암호화), `I`(해시 트리 디렉터리), `N`(인라인 데이터), `V`(fs-verity)는 `lsattr` 에 보이기만 하고 `chattr` 로는 바꾸지 못하는 값이고, `e`(익스텐트)는 `chattr` 로 뗄 수 없습니다[4]. 나머지 플래그 값은 [아이노드와 익스텐트](ext4/inode-extent.md) 의 `i_flags` 표에 있습니다.

### 확장 속성의 이름 공간

확장 속성은 파일·디렉터리에 붙는 "이름:값" 쌍이고, 이름은 늘 `이름공간.속성` 모양입니다[8]. 이름 공간은 넷이고 읽고 쓰는 조건이 서로 다릅니다[8].

| 이름 공간 | 쓰임 | 접근 조건 |
|---|---|---|
| `security.` | 보안 모듈(`security.selinux` 등)과 파일 capability | 보안 모듈의 정책을 따름. 모듈이 없으면 누구나 읽고, 쓰기는 `CAP_SYS_ADMIN` 만 |
| `system.` | 커널이 쓰는 객체(ACL 등) | 파일 시스템의 정책을 따름 |
| `trusted.` | 일반 프로세스가 보면 안 되는 사용자 공간 정보 | `CAP_SYS_ADMIN` 이 있어야 보이고 쓸 수 있음 |
| `user.` | 사용자가 붙이는 임의 정보(문자 집합, MIME 형식 등) | 파일 권한 비트를 따름. 일반 파일·디렉터리에만 붙음 |

VFS 는 이름을 255바이트, 값을 64kB 로 제한합니다[8]. mke2fs 의 기본 마운트 옵션은 `acl,user_xattr` 입니다[14].

### ext4 에 저장하는 모양

ext4 는 확장 속성을 두 군데에 둡니다[6]. 첫째는 아이노드 자리 안에서 구조체가 끝나는 128 + `i_extra_isize` 바이트 뒤부터 다음 아이노드 앞까지입니다. `s_inode_size` 256, `i_extra_isize` 32 라면 96바이트를 씁니다. 둘째는 아이노드 0x68 의 `i_file_acl_lo`(상위 16비트는 `l_i_file_acl_high`)가 가리키는 블록 하나입니다[5][6].

아이노드 안 영역은 4바이트 머리로 시작하고, 속성 블록은 32바이트 머리로 시작합니다[6]. 모든 값은 리틀 엔디언입니다.

| 영역 | 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|---|
| 아이노드 안 | 0x0 | 4 | `h_magic` | 0xEA020000 |
| 속성 블록 | 0x0 | 4 | `h_magic` | 0xEA020000 |
| 속성 블록 | 0x4 | 4 | `h_refcount` | 이 블록을 쓰는 아이노드 수 |
| 속성 블록 | 0x8 | 4 | `h_blocks` | 쓰는 디스크 블록 수 |
| 속성 블록 | 0xC | 4 | `h_hash` | 모든 속성의 해시 |
| 속성 블록 | 0x10 | 4 | `h_checksum` | 파일 시스템 UUID·블록 번호·블록 전체로 계산한 체크섬 |
| 속성 블록 | 0x14 | 12 | `h_reserved` | 0 |

머리 뒤에는 `ext4_xattr_entry` 가 줄지어 나옵니다[6].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x0 | 1 | `e_name_len` | 이름 길이 |
| 0x1 | 1 | `e_name_index` | 이름 접두 번호(아래 표) |
| 0x2 | 2 | `e_value_offs` | 값 위치. 아이노드 안이면 첫 항목 기준, 블록이면 블록 시작 기준 |
| 0x4 | 4 | `e_value_inum` | 값을 담은 아이노드 번호. 0 이면 같은 영역 안 |
| 0x8 | 4 | `e_value_size` | 값 길이 |
| 0xC | 4 | `e_hash` | 이름·값 해시. 아이노드 안 항목은 0 |
| 0x10 | `e_name_len` | `e_name` | 접두를 뗀 이름, 끝의 NUL 없음 |

값은 영역 끝에서 앞쪽으로 쌓이고 4바이트 경계에 맞춥니다[6]. 항목 목록의 끝은 첫 네 필드가 0 인 항목으로 표시합니다[6]. 블록 안 항목은 `e_name_index`, `e_name_len`, `e_name` 순으로 정렬하고 아이노드 안 항목은 정렬하지 않습니다[6].

이름의 앞부분은 번호로 줄여 적습니다[6].

| `e_name_index` | 접두 |
|---|---|
| 0 | 없음 |
| 1 | `user.` |
| 2 | `system.posix_acl_access` |
| 3 | `system.posix_acl_default` |
| 4 | `trusted.` |
| 6 | `security.` |
| 7 | `system.`(인라인 데이터) |
| 8 | `system.richacl` |

예를 들어 `user.fubar` 는 번호 1 과 이름 `fubar` 로 적습니다[6]. 이름 전체가 접두와 같은 ACL 은 떼고 나면 이름이 남지 않습니다.

INCOMPAT_EA_INODE 기능이 켜진 볼륨은 아이노드 안에도 속성 블록에도 들어가지 않는 큰 값을 따로 만든 아이노드의 데이터 블록에 둡니다[7]. 이 아이노드는 `e_value_inum` 으로만 이어지고 디렉터리 항목이 없습니다[6][7].

### ACL

POSIX ACL 은 접근 ACL (access ACL) 을 `system.posix_acl_access` 에, 기본 ACL (default ACL) 을 `system.posix_acl_default` 에 저장합니다[6]. ext4 디스크 형식은 4바이트 머리(`a_version` = 1) 뒤에 항목이 이어지는 모양입니다[6][9]. 항목은 `e_tag`(2바이트)·`e_perm`(2바이트)·`e_id`(4바이트)이고, `e_id` 는 이름 붙은 사용자·그룹 항목에만 있어 나머지 항목은 4바이트입니다[6][9]. 사용자 공간에서 `getxattr` 로 읽으면 같은 항목 모양이지만 버전이 2(`POSIX_ACL_XATTR_VERSION`)이고 모든 항목에 `e_id` 가 붙습니다[10]. 그래서 디스크에서 직접 읽은 값과 라이브 시스템에서 읽은 값은 바이트가 다릅니다.

| 값 | `e_tag` | 뜻 |
|---|---|---|
| 0x01 | `ACL_USER_OBJ` | 파일 소유자 |
| 0x02 | `ACL_USER` | 이름 붙은 사용자(`e_id` = UID) |
| 0x04 | `ACL_GROUP_OBJ` | 파일 그룹 |
| 0x08 | `ACL_GROUP` | 이름 붙은 그룹(`e_id` = GID) |
| 0x10 | `ACL_MASK` | 마스크 |
| 0x20 | `ACL_OTHER` | 나머지 |

`e_perm` 은 읽기 0x04, 쓰기 0x02, 실행 0x01 입니다[11].

### 파일 capability

실행 파일의 capability 는 확장 속성 `security.capability` 에 저장하고, 이 속성을 쓰려면 `CAP_SETFCAP` 이 있어야 합니다[12]. Linux 2.6.24 부터 쓰는 기능입니다[12]. 파일에는 Permitted, Inheritable 두 집합과 Effective 비트 하나가 있습니다[12]. Effective 비트가 켜져 있으면 실행하는 순간 새로 얻은 Permitted 능력이 모두 유효 집합에도 올라갑니다[12].

값은 `vfs_cap_data` 구조이고 모두 리틀 엔디언입니다[13].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0x0 | 4 | `magic_etc` | 위 8비트가 판(0x01·0x02·0x03), 비트 0x000001 이 Effective |
| 0x4 | 4 | `data[0].permitted` | 능력 0~31 |
| 0x8 | 4 | `data[0].inheritable` | 능력 0~31 |
| 0xC | 4 | `data[1].permitted` | 능력 32~63(판 2·3) |
| 0x10 | 4 | `data[1].inheritable` | 능력 32~63(판 2·3) |
| 0x14 | 4 | `rootid` | 판 3 에만 있음 |

판마다 크기가 다릅니다. 판 1 은 32비트 마스크 한 쌍이라 12바이트, 판 2(Linux 2.6.25 부터)는 64비트라 20바이트, 판 3(Linux 4.14 부터)은 판 2 뒤에 `rootid` 를 붙여 24바이트입니다[12][13]. 능력 번호 n 은 `data[n >> 5]` 의 비트 `1 << (n & 31)` 입니다[13]. 예를 들어 `CAP_NET_BIND_SERVICE` 는 10, `CAP_NET_RAW` 는 13, `CAP_SETUID` 는 7, `CAP_SYS_ADMIN` 은 21 입니다[13].

판 3 은 사용자 이름 공간 (user namespace) 을 위한 형식입니다. 파일 시스템을 마운트한 이름 공간이 아닌 다른 사용자 이름 공간의 프로세스가 속성을 쓰면 커널이 자동으로 판 3 으로 만들고, 그 이름 공간의 root 가 초기 이름 공간에서 어떤 UID 인지를 `rootid` 에 적습니다[12]. 초기 이름 공간에서 쓰면 판 2 가 됩니다[12]. 판 3 속성을 그 이름 공간 안에서 읽으면 커널이 판 2 모양으로 바꿔 돌려주므로[12], 컨테이너 안에서 본 값과 디스크의 값이 다를 수 있습니다.

## 읽는 법

### 헥스로 한 번

아래는 명세로 만든 예시이고 값은 모두 지어낸 것입니다. `s_inode_size` 256, `i_extra_isize` 32 인 ext4 아이노드에서 0xA0 부터 아이노드 끝 0xFF 까지 아이노드 안 확장 속성 영역을 보여 줍니다. 판 2 `security.capability` 하나를 담았고, 값은 영역 끝에 두었습니다.

```
오프셋     00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
000000A0  00 00 02 EA 0A 06 48 00  00 00 00 00 14 00 00 00
000000B0  00 00 00 00 63 61 70 61  62 69 6C 69 74 79 00 00
000000C0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
000000D0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
000000E0  00 00 00 00 00 00 00 00  00 00 00 00 01 00 00 02
000000F0  00 20 00 00 00 00 00 00  00 00 00 00 00 00 00 00
```

1. 0xA0 의 `00 00 02 EA` 는 0xEA020000 이라 아이노드 안 속성 영역임을 알 수 있습니다.
2. 0xA4 부터 첫 항목입니다. `e_name_len` 0x0A(10), `e_name_index` 6(`security.`), `e_value_offs` 0x48, `e_value_inum` 0, `e_value_size` 0x14(20), `e_hash` 0 입니다.
3. 0xB4 부터 10바이트 `capability` 가 이름이라 전체 이름은 `security.capability` 입니다. 항목은 0xBE~0xBF 를 채워 4바이트 경계에서 끝납니다.
4. 0xC0 의 항목은 첫 네 필드가 0 이라 목록의 끝입니다.
5. 값 위치는 첫 항목(0xA4) + 0x48 = 0xEC 입니다. `01 00 00 02` 는 0x02000001 이라 판 2 이고 Effective 비트가 켜져 있습니다. 크기 20바이트도 판 2 와 맞습니다.
6. 0xF0 의 `data[0].permitted` 는 0x00002000 이라 비트 13, 곧 `CAP_NET_RAW` 입니다. 나머지 세 필드는 0 입니다.

파일 쪽 설정으로는 `CAP_NET_RAW` 를 Permitted 에 주고 Effective 비트를 켠 상태라서, 실행하면 새로 얻은 Permitted 능력이 유효 집합에도 올라갑니다[12].

ACL 도 같은 방식으로 읽습니다. 아래는 명세로 만든 `system.posix_acl_access` 값의 예시입니다(ext4 디스크 형식).

```
01 00 00 00                 a_version 1
01 00 06 00                 USER_OBJ   rw-
02 00 06 00 E9 03 00 00     USER       rw-  UID 1001
04 00 04 00                 GROUP_OBJ  r--
10 00 06 00                 MASK       rw-
20 00 04 00                 OTHER      r--
```

소유자·그룹·나머지 항목 말고 이름 붙은 사용자 항목으로 UID 1001 에 `rw-` 를 따로 적은 ACL 입니다. UID 를 계정 이름으로 바꾸는 방법은 [UID·GID 와 사용자 이름 잇기](../value-decoding/uid-gid.md) 에 있습니다.

### 공개 도구로 한 번

e2fsprogs 의 `debugfs` 는 이미지를 마운트하지 않고 읽습니다. `ea_list` 는 파일의 확장 속성 목록을, `ea_get` 은 속성 하나의 값을 보여 주고, `inode_dump -x` 는 아이노드 안 속성 영역을 풀어서, `-e` 는 헥스로 보여 줍니다[15]. `ea_set`·`ea_rm` 은 값을 바꾸는 명령이라 증거물에는 쓰지 않습니다[15].

```
debugfs -R 'stat /usr/bin/example' ext4.img
debugfs -R 'ea_list /usr/bin/example' ext4.img
debugfs -R 'inode_dump -x /usr/bin/example' ext4.img
```

TSK `istat` 은 `i_file_acl` 이 0 이 아닐 때 그 블록을 읽어 "Extended Attributes" 절에 보여 주고, ACL 은 항목별 UID·GID 와 권한으로 풀어 줍니다[16]. `user.`·`trusted.`·`security.` 값은 문자열로 찍고 255바이트에서 자릅니다[16].

## 포렌식에서 중요한 점

### 증명하는 것

모드 비트, `i_flags`, ACL, `security.capability` 를 읽으면 이미지를 뜬 시점에 파일에 어떤 특권 실행 설정이 걸려 있었는지, 어떤 파일이 바꿀 수 없게 잠겨 있었는지, 소유자·그룹 말고 누구에게 권한이 더 주어졌는지를 증명합니다. 판 3 capability 의 `rootid` 는 그 속성을 사용자 이름 공간 안에서 썼다는 사실과 그 이름 공간의 root 가 어떤 UID 였는지를 알려 줍니다[12].

### 증명하지 못하는 것

언제, 누가 설정했는지는 증명하지 못합니다. 확장 속성 항목과 ACL 항목에는 시각 필드가 없고[6][9], 아이노드의 ctime 은 소유자·그룹·링크 수·모드 같은 아이노드 정보를 바꾸거나 파일에 쓸 때 바뀌는 마지막 변경 시각일 뿐입니다[1]. 설정 뒤에 다른 변경이 있었으면 ctime 은 그 뒤의 시각을 가리킵니다. 설정이 악의적인지도 이 값만으로는 알 수 없고, 배포판 패키지가 원래 설치한 값인지 패키지 관리자 기록과 대조해야 합니다.

### 시각 해석

모드·소유자·그룹을 바꾸면 ctime 이 바뀝니다[1]. 확장 속성이나 파일 속성을 바꿀 때 ctime 이 바뀌는지는 분석 대상과 같은 판의 커널에서 시험 파일로 확인합니다. ctime 은 UTC 기준 epoch 초이고[1], ext4 에서 나노초와 2038년 이후 범위를 푸는 법은 [시각 값](ext4/timestamps.md) 에 있습니다. `i` 가 켜진 동안에는 시각도 바꿀 수 없으므로[3], 그 파일의 시각 값은 `i` 를 켠 무렵이나 그 전의 변경을 가리킬 가능성이 있습니다.

### 지운 파일과 공유 블록

속성 블록은 `h_refcount` 로 여러 아이노드가 함께 쓸 수 있습니다[6]. 그래서 한 블록의 ACL·SELinux 레이블이 여러 파일의 값일 수 있고, 지운 파일의 아이노드가 아직 `i_file_acl` 을 가리키면 그 블록에서 지우기 전 속성을 읽을 수 있을 가능성이 있습니다. 지운 파일 전반은 [지운 파일이 남기는 것](ext4/deleted-files.md) 에서 다룹니다.

## 함정

- **`ls -l` 로는 알 수 없는 설정이 셋 있습니다.** capability 와 파일 속성은 보이지 않고, ACL 은 `+` 표시만 있을 뿐 항목 내용은 보이지 않으므로[23] 따로 모아야 합니다. UAC 도 SUID·capability·변경 불가 파일을 각각 다른 항목으로 모읍니다[17].
- **TSK `istat` 은 아이노드 안 속성을 "Extended Attributes" 절에 찍지 않습니다.** 이 절은 `i_file_acl` 블록만 읽으므로[16], 256바이트 아이노드 안에 들어간 `security.capability` 나 짧은 ACL 은 이 절에 나오지 않습니다. `debugfs ea_list` 나 헥스로 아이노드 뒤 영역을 확인합니다.
- **capability 값은 이진 값입니다.** `istat` 처럼 문자열로 찍는 도구에서는 첫 0 바이트에서 끊겨 판 번호조차 보이지 않을 수 있으므로 헥스로 읽습니다.
- **ACL 판 번호는 읽은 경로에 따라 다릅니다.** 디스크에서 직접 읽으면 1, `getxattr` 결과이면 2 입니다[9][10].
- **nosuid 마운트의 SUID 파일은 권한을 올리지 못합니다.** 권한 상승 경로로 보고하기 전에 마운트 옵션을 확인합니다[2].
- **xattr(7) 의 "속성 전체가 블록 하나에 들어가야 한다" 는 설명은 EA_INODE 기능이 없는 볼륨의 이야기입니다.** xattr(7) 은 ext2·ext3·ext4 의 모든 속성 이름·값이 블록 하나에 들어가야 한다고 설명하지만[8], ext4 의 EA_INODE 기능은 큰 값을 별도 아이노드에 둡니다[7]. 슈퍼블록 기능 비트로 어느 쪽인지 확인합니다([슈퍼블록과 블록 그룹](ext4/superblock-block-group.md)).
- **`a`·`i` 를 켜도 이미 열린 파일 디스크립터로는 쓸 수 있습니다[4].** 속성이 켜진 파일의 내용이 속성을 켠 뒤에 바뀌지 않았다고 단정하지 않습니다.
- **`i_flags` 의 0x1·0x2(`s`·`u`)는 ext4 에서 동작하지 않습니다[4].** 켜져 있어도 지운 파일이 0 으로 덮였거나 보존됐다는 뜻이 아닙니다.

## 도구

| 도구 | 쓰임 |
|---|---|
| debugfs `stat`, `ea_list`, `ea_get`, `inode_dump -x`·`-e` | 이미지에서 모드·플래그·확장 속성 읽기[15] |
| TSK `istat` | 모드·플래그와 속성 블록의 확장 속성·ACL 해석[16] |
| UAC `suid`·`getcap`·`immutable_files` | 라이브 시스템에서 SUID·capability·변경 불가 파일 목록 수집[17] |
| Velociraptor `Linux.Sys.SUID`, `Linux.Forensics.ImmutableFiles`, `Linux.Detection.AnomalousFiles` | SUID·SGID·변경 불가·숨김 파일 찾기[18] |

## 참고 문헌

1. man-pages, `inode(7)`. https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
2. util-linux, `mount(8)`. https://github.com/util-linux/util-linux/blob/master/sys-utils/mount.8.adoc
3. man-pages, `ioctl_iflags(2)`. https://github.com/mkerrisk/man-pages/blob/master/man2/ioctl_iflags.2
4. e2fsprogs, `chattr(1)`. https://github.com/tytso/e2fsprogs/blob/master/misc/chattr.1.in
5. Linux kernel, `Documentation/filesystems/ext4/inodes.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/inodes.rst
6. Linux kernel, `Documentation/filesystems/ext4/attributes.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/attributes.rst
7. Linux kernel, `Documentation/filesystems/ext4/eainode.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/eainode.rst
8. man-pages, `xattr(7)`. https://github.com/mkerrisk/man-pages/blob/master/man7/xattr.7
9. Linux kernel, `fs/ext4/acl.h`. https://github.com/torvalds/linux/blob/master/fs/ext4/acl.h
10. Linux kernel, `include/uapi/linux/posix_acl_xattr.h`. https://github.com/torvalds/linux/blob/master/include/uapi/linux/posix_acl_xattr.h
11. Linux kernel, `include/uapi/linux/posix_acl.h`. https://github.com/torvalds/linux/blob/master/include/uapi/linux/posix_acl.h
12. man-pages, `capabilities(7)`. https://github.com/mkerrisk/man-pages/blob/master/man7/capabilities.7
13. Linux kernel, `include/uapi/linux/capability.h`. https://github.com/torvalds/linux/blob/master/include/uapi/linux/capability.h
14. e2fsprogs, `misc/mke2fs.conf.in`. https://github.com/tytso/e2fsprogs/blob/master/misc/mke2fs.conf.in
15. e2fsprogs, `debugfs(8)`. https://github.com/tytso/e2fsprogs/blob/master/debugfs/debugfs.8.in
16. The Sleuth Kit, `tsk/fs/ext2fs.cpp`. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs.cpp
17. UAC, `artifacts/system/suid.yaml`, `getcap.yaml`, `immutable_files.yaml`. https://github.com/tclahr/uac/tree/main/artifacts/system
18. Velociraptor, `Linux.Sys.SUID`, `Linux.Forensics.ImmutableFiles`, `Linux.Detection.AnomalousFiles` 아티팩트 정의. https://github.com/Velocidex/velociraptor/tree/master/artifacts/definitions/Linux
19. Linux kernel, `fs/xfs/libxfs/xfs_format.h`. https://github.com/torvalds/linux/blob/master/fs/xfs/libxfs/xfs_format.h
20. Linux kernel, `include/uapi/linux/btrfs_tree.h`. https://github.com/torvalds/linux/blob/master/include/uapi/linux/btrfs_tree.h
21. Canonical subiquity(ubuntu/noble), `subiquity/server/controllers/storage.py`. https://github.com/canonical/subiquity/blob/ubuntu/noble/subiquity/server/controllers/storage.py
22. Anaconda(rhel-9), `data/product.d/rhel.conf`. https://github.com/rhinstaller/anaconda/blob/rhel-9/data/product.d/rhel.conf
23. GNU coreutils, `doc/coreutils.texi`(`ls` 의 `-l` 출력). https://github.com/coreutils/coreutils/blob/master/doc/coreutils.texi
