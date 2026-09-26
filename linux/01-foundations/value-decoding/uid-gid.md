---
title: "UID·GID 와 사용자 이름 잇기"
parent: "기반 · 값 해석"
nav_order: 270
---

# UID·GID 와 사용자 이름 잇기 (UID·GID)

Linux 의 파일 시스템·로그·메모리에는 사용자 이름이 아니라 숫자인 사용자 ID (UID, User ID) 와 그룹 ID (GID, Group ID) 가 남고, 이 숫자를 이름으로 바꾸려면 검체의 계정 데이터베이스를 따로 읽어야 합니다.

## 이 형식을 쓰는 아티팩트

파일 소유자, 로그를 남긴 프로세스의 자격, 로그인 기록의 칸 번호가 모두 UID·GID 숫자입니다. 아래 표는 숫자가 저장되는 곳과 그 폭입니다.

| 어디 | 필드 | 값의 모양 |
|---|---|---|
| ext4 아이노드 | `i_uid`·`i_gid`(하위 16비트)와 `l_i_uid_high`·`l_i_gid_high`(상위 16비트) | 리틀엔디언 16비트 두 조각을 합친 32비트[2] |
| XFS 아이노드 | `di_uid`·`di_gid` | 빅엔디언 32비트(`__be32`)[3] |
| Btrfs inode item | `uid`·`gid` | 리틀엔디언 32비트(`__le32`)[4] |
| `stat`·`statx` 결과 | `st_uid`·`st_gid`, `stx_uid`·`stx_gid` | 정수[1] |
| systemd 저널 | `_UID=`·`_GID=`·`_AUDIT_LOGINUID=`·`_SYSTEMD_OWNER_UID=`·`OBJECT_UID=`·`OBJECT_GID=` | 10진 문자열[16] |
| 저널 파일 이름 | `user-UID.journal` | 파일 이름 안의 10진 UID[17][33] |
| 감사 로그 (auditd) | `auid`·`uid`·`euid`·`fsuid`·`ouid`·`ogid`·`inode_uid`·`obj_uid`·`oauid`·`old-auid`·`id` | 10진 숫자, `acct` 만 이름[22] |
| lastlog | 레코드 순번 자체가 UID(오프셋 = UID × 292) | 이름 칸 없음[10][25] |
| `/proc/PID/status` | `Uid:`·`Gid:` 줄 | real·effective·saved set·filesystem 네 값[21] |
| `/proc/PID/loginuid` | 감사용 로그인 UID | 정하지 않았으면 4294967295[26] |
| 메모리 (Volatility 3 `linux.pslist`) | `task.cred` 의 uid·gid·euid·egid | 정수[31] |

반대로 utmp·wtmp 의 `ut_user` 와 lastlog2 의 `Name` 열에는 UID 없이 이름만 있습니다[25]. 이 두 형식은 [로그인 기록 파일 형식](../logging/utmp-wtmp-format.md)에서 다룹니다.

## 구조

### 숫자가 붙는 규칙

새로 만든 파일의 소유 UID 는 파일을 만든 프로세스의 effective UID 입니다[1]. 소유 GID 는 부모 디렉터리에 set-group-ID 비트가 서 있으면 부모 디렉터리의 GID 를, 아니면 만든 프로세스의 effective GID 를 받습니다[1]. 소유자·그룹은 뒤에 `chown` 으로 바꿀 수 있고, 바꾸면 그 순간 ctime 이 갱신됩니다[1].

저널의 `_UID`·`_GID` 는 메시지를 보낸 프로세스의 값입니다[16]. 다만 포크한 프로세스의 표준 출력·표준 오류로 들어온 항목에는 journald 에 연결을 연 부모 프로세스의 값이 들어갑니다[16]. 자세한 필드 설명은 [systemd 저널](../logging/systemd-journal/index.md)에 있습니다.

### 숫자를 이름으로 바꾸는 곳

| 파일 | 줄 모양 | 쓰임 |
|---|---|---|
| `/etc/passwd` | `name:password:UID:GID:GECOS:directory:shell` | UID → 이름, 네 번째 칸은 기본 그룹[5] |
| `/etc/group` | `group_name:password:GID:user_list` | GID → 그룹 이름, 네 번째 칸은 쉼표로 나눈 구성원[6] |
| `/etc/passwd-` | passwd 와 같음 | shadow 도구 모음이 남기는 백업, 모든 관리 도구가 쓰지는 않음[8] |
| `/etc/nsswitch.conf` | `passwd:`·`group:` 줄에 `files`·`db`·`nis`·`compat` 같은 조회 방식 | 어느 데이터베이스를 어떤 순서로 묻는지[7] |
| `/etc/subuid`·`/etc/subgid` | `로그인이름또는UID:시작ID:개수` | 사용자 네임스페이스에 넘겨줄 하위 ID 범위, 한 사용자에 여러 줄 가능[12][13] |
| `/etc/login.defs` | `UID_MIN`·`UID_MAX`·`SYS_UID_MIN`·`SYS_UID_MAX` 등 | 새 계정에 줄 번호 범위[11][12] |

`/etc/passwd` 는 `ls` 같은 도구가 UID 를 이름으로 바꿀 때 쓰는 파일이라 누구나 읽을 수 있게 둡니다[5]. 보조 그룹은 `/etc/group` 에만 있으므로, 한 사용자의 그룹을 정리하려면 passwd 의 기본 그룹과 group 의 구성원 목록을 함께 봅니다[5][6]. 파일 형식 자체는 [계정 파일](../users-auth/passwd-shadow-group.md)에서 다룹니다.

### 특수 번호와 범위

| UID | 뜻 |
|---|---|
| 0 | root[14] |
| 1–999 | 배포판의 시스템 사용자(옛 시스템은 499/500 이나 99/100 경계)[14] |
| 1000–60000 | `adduser` 류가 보통 주는 일반 사용자 범위[14] |
| 60001–60513 | systemd-homed 가 관리하는 홈 디렉터리 사용자[14] |
| 60514–60577 | 컨테이너 안으로 매핑한 호스트 사용자[14] |
| 60578–60705 | 동적 greeter 사용자[14] |
| 61184–65519 | `DynamicUser=` 서비스용 동적 사용자[14][15] |
| 65534 | nobody, 매핑할 수 없는 ID 가 떨어지는 overflow UID[14] |
| 65535 | 16비트 시절의 (uid_t) -1, 쓰지 않음[14] |
| 524288–1879048191 | systemd-nspawn 컨테이너에 나눠 주는 범위[14] |
| 2147352576–2147418111 | 외부 OS 이미지용 foreign UID 범위[14] |
| 4294967295 | 32비트 (uid_t) -1, 사용자에게 줄 수 없음[14] |

GID 도 같은 범위를 따르고, `tty` 그룹만은 devpts 마운트 인자에 들어가야 해서 GID 5 로 고정입니다[14]. 2147483648(2^31) 이상은 커널의 devpts 파일 시스템처럼 UID 를 부호 있는 정수로 다루는 코드가 제대로 처리하지 못합니다[14].

shadow 도구의 기본값은 `UID_MIN` 1000, `UID_MAX` 60000, `SYS_UID_MIN` 101, `SYS_UID_MAX` 는 `UID_MIN` 빼기 1 이고 GID 도 같습니다[11]. shadow 가 함께 배포하는 예시 `login.defs` 의 값은 `SYS_UID_MAX 999`, `SUB_UID_MIN 100000`, `SUB_UID_MAX 600100000`, `SUB_UID_COUNT 65536` 입니다[12]. 실제 값은 검체의 `/etc/login.defs` 에서 읽습니다.

기준 배포판의 systemd 빌드 설정은 아래처럼 다릅니다.

| 항목 | Ubuntu 24.04 (systemd 255) | RHEL 9 계열 (CentOS Stream 9, systemd 252) |
|---|---|---|
| nobody 그룹 이름 | `nogroup`[18] | `nobody`[19] |
| 시스템·일반 사용자 경계 | 빌드 설정에서 999 로 정함(`-Dsystem-uid-max=999`, `-Dsystem-gid-max=999`)[18] | 실행 중에 `/etc/login.defs` 를 읽음(`-Dcompat-mutable-uid-boundaries=true`)[19][14] |
| tty·users GID | 빌드 설정에 따로 적지 않음[18] | `-Dtty-gid=5`, `-Dusers-gid=100`[19] |

## 읽는 법

1. 파일 시스템 메타데이터나 로그에서 숫자 UID·GID 를 뽑습니다. ext4 는 `i_uid` + (`l_i_uid_high` × 65536) 으로 합칩니다[2].
2. 검체의 `/etc/passwd`·`/etc/passwd-`·`/etc/group`·`/etc/login.defs`·`/etc/nsswitch.conf`·`/etc/subuid`·`/etc/subgid` 를 모아 숫자 → 이름 표를 만듭니다.
3. 표에 없는 숫자는 위 범위표에 대어 봅니다. 동적 서비스 사용자, 컨테이너 범위, subuid 범위, nobody 가운데 어디에 드는지 적습니다.
4. `nsswitch.conf` 의 `passwd:` 줄에 `files` 말고 다른 방식(`nis`, `ldap` 같은 모듈)이 있으면 원격 계정일 가능성을 적습니다[7][14].

### 헥스로 한 번

아래는 ext4 명세로 만든 예시로, UID·GID 가 모두 100000(0x000186A0)인 아이노드의 해당 바이트만 보인 것입니다. `l_i_uid_high` 는 `i_osd2`(0x74) 안 +0x4, `l_i_gid_high` 는 +0x6 이라 아이노드 기준 0x78·0x7A 입니다[2].

```
오프셋  바이트   필드
0x02    A0 86    i_uid (하위 16비트) = 0x86A0
0x18    A0 86    i_gid (하위 16비트) = 0x86A0
0x78    01 00    l_i_uid_high        = 0x0001
0x7A    01 00    l_i_gid_high        = 0x0001

UID = 0x86A0 + (0x0001 << 16) = 0x186A0 = 100000
```

하위 16비트만 읽으면 34464 가 나오므로, 상위 칸을 빠뜨리면 전혀 다른 사용자로 잇게 됩니다. 같은 값을 XFS `di_uid` 에서 보면 빅엔디언이라 `00 01 86 A0` 순서로 나옵니다[3]. 100000 은 shadow 예시 `login.defs` 의 `SUB_UID_MIN` 과 같은 값이라, 이런 숫자가 passwd 에 없으면 컨테이너 안 사용자일 가능성부터 봅니다[12][13].

### 명령으로 한 번

검체를 분석 PC 에 마운트한 뒤 `ls -l` 이나 `stat` 을 그대로 쓰면, 도구가 분석 PC 의 `/etc/passwd` 로 이름을 붙입니다[5]. 그래서 `ls -n` 이나 `stat -c '%u %g'` 처럼 숫자로 출력한 뒤 검체의 표로 잇습니다[32]. The Sleuth Kit 의 `istat` 도 ext4 UID·GID 를 위 식대로 합친 숫자로 보여 줍니다[30].

## 포렌식에서 중요한 점

### 증명하는 것

파일 소유 UID 는 그 파일을 만든 프로세스의 effective UID 이거나, 나중에 누군가 `chown` 으로 정한 값입니다[1]. 로그의 UID 는 기록 시점에 그 숫자 자격으로 이벤트가 일어났다는 것을 보여 줍니다. 감사 로그의 `auid` 는 로그인 때 정한 로그인 사용자 ID 라서, `uid` 와 다르면 로그인 뒤 권한을 바꾼 상태의 행위로 읽습니다([감사 로그 형식](../logging/auditd-format.md)).

### 증명하지 못하는 것

숫자가 기록 당시 어떤 이름이었는지는 숫자만으로 알 수 없습니다. 검체의 passwd 는 분석 시점의 상태이고, 그 사이 계정을 지우거나 번호를 바꿨을 수 있습니다. 같은 UID 를 여러 이름이 나눠 쓸 수도 있고, 사람이 누구였는지는 계정 공유 여부를 따로 봐야 합니다. 파일 소유자는 `chown` 으로 바뀔 수 있으므로, 소유자가 곧 만든 사람이라고 쓰지 않습니다[1].

### 지운 계정과 번호 재사용

`userdel -r` 은 홈 디렉터리와 메일 스풀만 지우고, 다른 파일 시스템의 파일은 손으로 찾아 지워야 합니다[9]. 그래서 지운 계정의 UID 를 소유자로 둔 파일이 passwd 에 없는 숫자로 남습니다. `usermod -u` 도 홈 안 파일과 메일함만 새 UID 로 바꾸고 홈 밖 파일은 옛 UID 로 둡니다[9]. 이런 파일은 `find` 의 `-nouser`·`-nogroup` 조건으로 모을 수 있고, UAC 의 find 명령 조립 코드도 이 두 조건을 지원합니다[29].

`useradd` 는 기본으로 `UID_MIN` 이상이면서 기존 모든 사용자보다 큰 가장 작은 값을 줍니다[9]. 이 규칙대로라면 가장 큰 UID 를 가진 계정을 지운 뒤 새 계정을 만들면 같은 번호를 받을 가능성이 있습니다. 그러면 옛 계정이 남긴 파일이 새 계정 이름으로 보입니다.

lastlog 에는 지운 사용자의 레코드가 남을 수 있고, `lastlog` 명령은 현재 사용자만 보여 줍니다[10]. `/etc/passwd-` 는 `/etc/passwd` 의 백업이라, 계정을 지우기 전 목록이 남아 있으면 지운 계정의 이름을 찾을 수 있습니다[8]. 계정 변경 흔적 전체는 [계정 생성·변경 흔적](../../02-artifacts/logins/account-changes.md)에서 다룹니다.

## 함정

- **한 UID 에 여러 이름**: `useradd`·`usermod` 의 `-o, --non-unique` 로 이미 있는 UID 를 또 줄 수 있습니다[9]. passwd 에서 UID 0 을 가진 이름이 root 하나뿐인지 확인합니다.
- **passwd 에 없는 것이 정상인 번호**: 61184–65519 동적 사용자는 nss-systemd 가 실행 중에 만들어 내므로 `/etc/passwd` 에 없습니다[14]. 이 번호는 서비스가 끝나면 다른 유닛이 다시 받을 수 있습니다[15]. `StateDirectory=` 같은 디렉터리는 `/var/lib/private`·`/var/cache/private`·`/var/log/private` 아래에 만들어집니다[15].
- **원격 계정**: 일반 사용자는 LDAP·NIS 같은 원격 데이터베이스에 있을 수 있어서 로컬 passwd 에 없어도 됩니다[14].
- **컨테이너와 사용자 네임스페이스**: `uid_map` 한 줄은 "네임스페이스 안 시작 ID, 바깥 시작 ID, 길이" 세 수이고, 루트 네임스페이스는 `0 0 4294967295` 입니다[20]. `stat`·`getuid`·`/proc/PID/status` 는 매핑 안 된 ID 를 overflow UID(기본 65534)로 돌려줍니다[20]. systemd-nspawn 방식은 바깥 UID 의 하위 16비트가 안쪽 UID 라서 `INTERNAL_UID = EXTERNAL_UID & 0x0000FFFF` 로 풉니다[14].
- **65534 와 4294967295**: 65534 는 16비트만 지원하는 파일 시스템, NFS, 사용자 네임스페이스에서 매핑할 수 없는 사용자가 떨어지는 값입니다[14]. 감사 로그와 `/proc/PID/loginuid` 의 4294967295 는 "정하지 않음" 입니다[23][26].
- **도구 필드 이름**: dissect.target 의 프로세스 플러그인 `uid` 속성은 실제로 `loginuid` 파일을 읽고, 4294967295 면 -1 을 돌려줍니다[26]. 같은 플러그인의 `owner` 는 UID 가 0 이면 이름 조회를 건너뜁니다[26].
- **lastlog 의 이름**: lastlog 레코드에는 이름이 없어서 도구가 분석 시점의 사용자 목록으로 붙이고, 지운 사용자의 칸은 이름 없이 나옵니다[25].
- **Velociraptor `Linux.Users.RootUsers`**: 설명은 sudo 그룹 사용자를 찾는다고 하지만, 쿼리는 라이브 시스템에서 `id -Gn` 을 실행해 출력에 `root` 가 있는지만 봅니다[27].
- **ENRICHED 감사 로그**: 이름을 풀어 붙인 값은 로그를 쓴 기계에서 그 순간 푼 것입니다. 분석 PC 에서 다시 풀면 다른 이름이 나올 수 있습니다([감사 로그 형식](../logging/auditd-format.md)).

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| ForensicArtifacts | `/etc/passwd`·`/etc/group`·`/etc/nsswitch.conf` 수집 경로 정의[28] |
| UAC | `/etc` 를 통째로 모으되 `shadow`·`gshadow` 류는 빼고 모음[29] |
| Velociraptor | `Linux.Sys.Users` 가 `/etc/passwd` 를, `Linux.Sys.Groups` 가 `/etc/group` 을 칸별로 나눔[27] |
| dissect.target | `/etc/passwd`·`/etc/passwd-`·`/etc/master.passwd` 를 모두 읽고 이름·홈·셸이 같은 줄은 한 번만 냄[24] |
| The Sleuth Kit `istat` | 아이노드의 숫자 UID·GID 출력[30] |
| Volatility 3 `linux.pslist` | 메모리의 프로세스별 UID·GID·EUID·EGID[31] |

라이브 시스템에서는 `/proc/PID/status`, `/proc/PID/loginuid`, `/proc/PID/uid_map` 을 함께 읽습니다([실행 중인 프로세스](../../02-artifacts/execution/proc.md)). 로그인 기록과 잇는 방법은 [로그인 기록](../../02-artifacts/logins/wtmp-btmp-lastlog.md), 시각 값 풀이는 [Linux 의 시각 값](time-values.md)에서 다룹니다. 파일 시스템별 아이노드 구조는 [ext4](../filesystem/ext4/index.md), [XFS](../filesystem/xfs.md), [Btrfs](../filesystem/btrfs.md)에 있습니다.

다른 판의 사용자 식별자는 [윈도 식별자 형식 (SID·GUID·CLSID·Known Folder ID)](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/value-decoding/sid-guid-clsid-known-folder-id.html), [맥의 식별자 읽기 (UUID·UID·GUID)](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/value-decoding/uuid-uid.html), [안드로이드 패키지 이름과 UID](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/value-decoding/package-uid.html)에서 다룹니다.

## 참고 문헌

1. inode(7), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
2. Linux kernel, `Documentation/filesystems/ext4/inodes.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/inodes.rst
3. Linux kernel, `fs/xfs/libxfs/xfs_format.h`. https://github.com/torvalds/linux/blob/master/fs/xfs/libxfs/xfs_format.h
4. Linux kernel, `include/uapi/linux/btrfs_tree.h`. https://github.com/torvalds/linux/blob/master/include/uapi/linux/btrfs_tree.h
5. passwd(5), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man5/passwd.5
6. group(5), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man5/group.5
7. nsswitch.conf(5), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man5/nsswitch.conf.5
8. shadow, passwd(5). https://github.com/shadow-maint/shadow/blob/master/man/passwd.5.xml
9. shadow, useradd(8)·usermod(8)·userdel(8). https://github.com/shadow-maint/shadow/tree/master/man
10. shadow, lastlog(8). https://github.com/shadow-maint/shadow/blob/master/man/lastlog.8.xml
11. shadow, `man/login.defs.d/UID_MAX.xml`·`SYS_UID_MAX.xml`·`GID_MAX.xml`·`SYS_GID_MAX.xml`. https://github.com/shadow-maint/shadow/tree/master/man/login.defs.d
12. shadow, `etc/login.defs`. https://github.com/shadow-maint/shadow/blob/master/etc/login.defs
13. shadow, subuid(5). https://github.com/shadow-maint/shadow/blob/master/man/subuid.5.xml
14. systemd, "Users, Groups, UIDs and GIDs on systemd Systems" (`docs/UIDS-GIDS.md`). https://github.com/systemd/systemd/blob/main/docs/UIDS-GIDS.md
15. systemd, systemd.exec(5). https://github.com/systemd/systemd/blob/main/man/systemd.exec.xml
16. systemd, systemd.journal-fields(7). https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
17. systemd, journald.conf(5). https://github.com/systemd/systemd/blob/main/man/journald.conf.xml
18. Ubuntu 24.04 systemd 패키지, `debian/rules`. https://git.launchpad.net/~ubuntu-core-dev/ubuntu/+source/systemd/plain/debian/rules?h=ubuntu-noble
19. CentOS Stream 9 systemd 패키지, `systemd.spec`. https://gitlab.com/redhat/centos-stream/rpms/systemd/-/raw/c9s/systemd.spec
20. user_namespaces(7), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man7/user_namespaces.7
21. proc(5), Linux man-pages. https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
22. Linux Audit, `specs/fields/field-dictionary.csv`. https://github.com/linux-audit/audit-documentation/blob/main/specs/fields/field-dictionary.csv
23. plaso, `parsers/text_plugins/selinux.py`. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/selinux.py
24. dissect.target, `plugins/os/unix/_os.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/_os.py
25. dissect.target, `plugins/os/unix/log/lastlog.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/lastlog.py
26. dissect.target, `plugins/os/unix/linux/proc.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/proc.py
27. Velociraptor, `Linux/Sys/Users.yaml`·`Linux/Sys/Groups.yaml`·`Linux/Users/RootUsers.yaml`. https://github.com/Velocidex/velociraptor/tree/master/artifacts/definitions/Linux
28. ForensicArtifacts, `artifacts/data/linux.yaml`·`unix_common.yaml`. https://github.com/ForensicArtifacts/artifacts/tree/main/artifacts/data
29. UAC, `artifacts/files/system/etc.yaml`·`lib/build_find_command.sh`. https://github.com/tclahr/uac
30. The Sleuth Kit, `tsk/fs/ext2fs.cpp`. https://github.com/sleuthkit/sleuthkit/blob/develop/tsk/fs/ext2fs.cpp
31. Volatility 3, `plugins/linux/pslist.py`. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/pslist.py
32. GNU coreutils, `doc/coreutils.texi`(`ls --numeric-uid-gid`, `stat` 의 `%u`·`%g`). https://github.com/coreutils/coreutils/blob/master/doc/coreutils.texi
33. systemd, `src/libsystemd/sd-journal/journal-file.c`. https://github.com/systemd/systemd/blob/main/src/libsystemd/sd-journal/journal-file.c
