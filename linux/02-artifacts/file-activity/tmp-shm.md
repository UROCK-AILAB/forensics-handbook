---
title: "임시 폴더와 메모리 파일 시스템"
parent: "아티팩트 · 파일 활동"
nav_order: 640
---

# 임시 폴더와 메모리 파일 시스템 (/tmp·/dev/shm)

`/tmp`·`/var/tmp`·`/dev/shm` 은 누구나 쓸 수 있는 임시 자리라서 내려받은 파일이나 실행 파일이 잠깐 머물다 사라지는 곳이고, 이 페이지는 그 자리가 언제 비워지는지와 전원을 끈 뒤에도 무엇이 남는지를 다룹니다.

## 무엇을 기록하나 · 왜 생기나

이 폴더들은 로그처럼 무엇을 기록하지 않습니다. 파일 자체와 그 아이노드의 소유자·권한·시각이 흔적이고, 언제까지 남는지는 폴더를 담은 파일 시스템과 정리 규칙이 정합니다.

`/dev/shm` 은 임시 메모리 파일 시스템 (tmpfs) 입니다. tmpfs 는 파일을 가상 메모리(커널 캐시)에 두고 디스크에는 파일을 만들지 않아서, 마운트를 풀거나 전원을 끄면 안의 내용이 모두 사라집니다[3]. glibc 는 POSIX 공유 메모리(`shm_open`, `shm_unlink`)를 `/dev/shm` 의 tmpfs 에 만듭니다[3][4]. POSIX 공유 메모리 객체는 시스템을 끄거나, 모든 프로세스가 매핑을 풀고 `shm_unlink` 로 지울 때까지 남습니다[4]. systemd 는 부팅할 때 `/dev/shm` 과 `/run` 을 tmpfs 로 올립니다[7].

`/tmp` 와 `/var/tmp` 는 배포판 설정에 따라 디스크 파일 시스템일 수도, tmpfs 일 수도 있습니다. 어느 쪽이든 systemd-tmpfiles 가 정해진 나이를 넘긴 파일을 지웁니다[8][9]. upstream 기본값은 `/tmp` 가 10일, `/var/tmp` 가 30일입니다[10].

서비스에 `PrivateTmp=` 를 켜면 systemd 가 그 서비스에만 보이는 `/tmp`·`/var/tmp` 를 따로 만들고, 서비스가 멈추면 그 안의 임시 파일을 지웁니다[11]. 이 사설 폴더는 호스트의 `/tmp`·`/var/tmp` 아래에 실제로 만들어지고 이름에 부팅 ID 와 유닛 이름이 들어가서[11][12], 어떤 서비스가 어느 부팅에서 돌았는지를 알려 주는 부수 흔적이 됩니다.

## 위치와 버전별 차이

| 경로 | 파일 시스템 | 사라지는 때 |
|---|---|---|
| `/tmp` | 디스크 또는 tmpfs(`tmp.mount` 를 켰을 때) | tmpfs 면 전원을 끌 때, 디스크면 나이 기준 정리(upstream 10일)[9][14] |
| `/var/tmp` | 보통 디스크 | 나이 기준 정리(upstream 30일)[9] |
| `/dev/shm` | tmpfs | 전원을 끌 때, `shm_unlink`, 사용자 로그아웃(RemoveIPC)[4][7][13] |
| `/run` | tmpfs | 전원을 끌 때[7] |
| `/tmp/systemd-private-*`, `/var/tmp/systemd-private-*` | `/tmp`·`/var/tmp` 를 따름 | 서비스가 멈출 때, 다음 부팅 때[9][11] |
| `/run/shm` | 실제 시스템에서 확인 | 실제 시스템에서 확인(UAC 는 `/dev/shm` 과 따로 모음[1]) |

`/dev/shm` 의 마운트 옵션은 upstream 이 `mode=01777` 이고 여기에 사용자 할당량 옵션을 붙이는 함수가 더해지며, 플래그는 `MS_NOSUID|MS_NODEV|MS_STRICTATIME` 입니다[7]. RHEL 9 가 쓰는 systemd 252 는 `mode=1777` 에 같은 세 플래그를 씁니다[7]. 두 판 모두 systemd 가 올리는 기본 마운트에는 noexec 가 없어서, 관리자가 옵션을 바꾸지 않았다면 `/dev/shm` 에 둔 파일은 실행할 수 있습니다. `/run` 은 `mode=0755` 에 nosuid·nodev·strictatime 입니다[7]. `/run` 아래 흔적은 [마운트 기록](../devices/mounts.md)에서 다룹니다.

배포판 차이는 `/tmp` 를 tmpfs 로 올리느냐와 정리 기간에서 나옵니다.

| 항목 | Ubuntu 24.04 (systemd 255.4) | RHEL 9 (systemd 252) |
|---|---|---|
| `/tmp` 기본 | 디스크. 패키징이 `tmp.mount` 를 `/usr/share/systemd/` 로 옮기고 `local-fs.target.wants/tmp.mount` 링크를 지움[15] | 디스크. `tmp.mount` 유닛 파일은 설치하지만 `local-fs.target.wants/` 링크는 만들지 않음[14][16] |
| `/tmp` 를 tmpfs 로 켰는지 | `/etc/fstab` 의 `tmpfs` 줄, `/etc/systemd/system/local-fs.target.wants/tmp.mount` | 같음 |
| 정리 기간 | 분석 대상의 `/usr/lib/tmpfiles.d/tmp.conf` 와 `/etc/tmpfiles.d/tmp.conf` 를 읽어 확인 | `q /tmp 1777 root root 10d`, `q /var/tmp 1777 root root 30d`[9] |
| `/dev/shm` | tmpfs, systemd 가 마운트[7] | tmpfs, `mode=1777`[7] |

upstream 은 반대로 `tmp.mount` 를 기본으로 켭니다. meson 빌드가 `local-fs.target.wants/` 에 링크를 만들고, 유닛의 옵션은 `mode=1777,strictatime,nosuid,nodev,size=50%%,nr_inodes=1m,x-systemd.graceful-option=usrquota` 입니다[14]. `/tmp` 가 심볼릭 링크면 이 유닛은 돌지 않습니다(`ConditionPathIsSymbolicLink=!/tmp`)[14]. 두 배포판 모두 관리자가 켤 수 있으므로 분석 대상의 설정을 먼저 읽습니다. 라이브 시스템이면 `findmnt` 출력이 가장 빠르고, UAC 도 이 출력을 받습니다[2].

## 구조

### 정리 규칙 (tmpfiles.d)

systemd-tmpfiles 는 `/etc/tmpfiles.d`, `/run/tmpfiles.d`, `/usr/lib/tmpfiles.d` 의 `.conf` 를 읽습니다. 같은 이름의 파일이 여러 곳에 있으면 `/etc` 가 `/run` 과 `/usr/lib` 을 덮고, `/run` 이 `/usr/lib` 을 덮습니다[8]. 관리자가 배포판 파일을 끄려면 `/etc/tmpfiles.d/` 에 같은 이름으로 `/dev/null` 을 가리키는 링크를 둡니다[8]. 그래서 정리 기간이 기본값과 다른지는 `/etc/tmpfiles.d/tmp.conf` 가 있는지부터 보면 됩니다.

한 줄은 `종류 경로 모드 사용자 그룹 나이` 순서입니다. 이 페이지와 관계있는 줄은 아래와 같습니다(upstream 설정 파일에서 옮김)[9].

```
# tmp.conf
q /tmp 1777 root root 10d
q /var/tmp 1777 root root 30d

# systemd-tmp.conf
x /tmp/systemd-private-%b-*
X /tmp/systemd-private-%b-*/tmp
x /var/tmp/systemd-private-%b-*
X /var/tmp/systemd-private-%b-*/tmp
R! /tmp/systemd-private-*
R! /var/tmp/systemd-private-*

# x11.conf
D /tmp/.X11-unix 1777 root root 1h
D /tmp/.ICE-unix 1777 root root 1h
D /tmp/.XIM-unix 1777 root root 1h
D /tmp/.font-unix 1777 root root 1h
r! /tmp/.X[0-9]*-lock
x /tmp/.X[0-9]*-lock
```

`x`·`X` 는 정리에서 뺄 경로이고, `R` 은 경로를 통째로 지우는 줄이며, `D` 는 `--remove` 로 돌 때 폴더 내용을 지우는 줄입니다[8]. 종류 뒤에 `!` 가 붙은 줄은 `--boot` 로 돌 때만, 곧 부팅 때만 실행합니다[8]. `%b` 는 현재 부팅 ID 로 바뀝니다[8]. 따라서 현재 부팅의 사설 폴더는 나이 정리에서 빠지고, 지난 부팅의 사설 폴더는 다음 부팅 때 지워집니다[9].

나이를 잴 때는 파일의 atime·btime·ctime·mtime 을 모두 보고, 그중 하나라도 기준보다 새로우면 지우지 않습니다[8]. 폴더는 ctime 을 보지 않는데, 정리 작업이 안의 파일을 지우면서 폴더의 ctime 을 바꾸기 때문입니다[8]. 이 규칙이 기본값 `abcmABM` 이고, 나이 필드 앞에 `bmA:` 처럼 글자를 붙이면 볼 시각을 바꿀 수 있습니다[8]. 지우려는 파일이나 폴더에 BSD 잠금(flock)이 걸려 있으면 그것과 그 아래 전체를 건너뜁니다[8].

정리는 `systemd-tmpfiles-clean.timer` 가 부팅 15분 뒤(`OnBootSec=15min`)에 한 번, 그 뒤로는 하루에 한 번(`OnUnitActiveSec=1d`) 돌립니다[9].

### PrivateTmp 사설 폴더

systemd 는 사설 폴더 이름을 `접두 경로/systemd-private-` 뒤에 부팅 ID(32자리 16진수), `-`, 유닛 이름, `-XXXXXX` 를 이어 만들고, `XXXXXX` 는 mkdtemp 가 채우는 무작위 글자 여섯 개입니다[12]. 바깥 폴더는 umask 0077 로 만들고, 서비스가 `/tmp` 로 보는 곳은 그 안의 `tmp` 폴더이며 권한은 1777 입니다[12]. 접두 경로는 `/tmp` 와 `/var/tmp` 두 곳입니다[11].

```
/tmp/systemd-private-0f3c9a7e5b2d4c18a6e1f09d3b7c2a45-chronyd.service-Qx7LmA/tmp/
```

위는 만든 예시입니다. `PrivateTmp=disconnected` 로 설정한 서비스는 호스트 폴더 대신 새 tmpfs 를 받아서 이 폴더가 생기지 않습니다[11]. 이 값은 systemd 257 부터 있어서 Ubuntu 24.04(255)·RHEL 9(252)에는 없습니다[11].

### memfd 와 SYSV 공유 메모리

`memfd_create()` 로 만든 파일은 경로 없이 RAM 에 있고, 모든 참조가 사라지면 저절로 풀립니다[5]. 이름은 `/proc/self/fd/` 링크의 대상으로만 보이고 앞에 `memfd:` 가 붙으며, 디버깅용이라 같은 이름이 여러 개 있어도 됩니다[5]. SYSV 공유 메모리와 공유 익명 매핑은 사용자에게 보이지 않는 커널 내부 tmpfs 마운트를 씁니다[3]. 그래서 이 둘은 `/dev/shm` 을 뒤져도 파일로 나오지 않습니다.

## 증거로서 의미

**증명하는 것**

- 수집한 시점에 그 경로에 그 파일이 있었다는 것과, 그 파일의 소유자·권한·시각입니다. 소유자 UID 를 계정으로 잇는 방법은 [UID·GID 와 사용자 이름 잇기](../../01-foundations/value-decoding/uid-gid.md)를 봅니다.
- `systemd-private-부팅ID-유닛이름-XXXXXX` 폴더가 있으면 그 부팅 ID 의 부팅에서 그 유닛이 `PrivateTmp=` 로 돌았다는 것입니다[12].
- 프로세스의 fd 가 `memfd:` 나 `/dev/shm` 아래 지워진 파일을 가리키면, 수집 시점에 그 프로세스가 그 메모리 파일을 열고 있었다는 것입니다[2][5].

**증명하지 못하는 것**

- 디스크 이미지만으로는 tmpfs(`/dev/shm`, tmpfs 로 올린 `/tmp`, `/run`)에 있던 파일을 볼 수 없습니다[3]. dissect.target 도 fstab 을 읽을 때 `tmpfs` 줄을 건너뜁니다[17].
- `/tmp` 에 파일이 없다는 사실만으로 "만든 적이 없다" 고 쓸 수 없습니다. 나이 기준 정리, 부팅 때 정리, 서비스가 멈출 때 사설 폴더 삭제, 로그아웃 때 RemoveIPC 삭제는 모두 정상 동작입니다[8][10][11][13].
- 파일이 있던 사실만으로 누가 만들었는지는 알 수 없습니다. 소유자는 파일을 만든 프로세스의 계정일 뿐이고, 1777 폴더라 어느 계정이든 쓸 수 있습니다.

보고서에는 "수집 시점에 `/dev/shm` 에 UID 1001 소유의 실행 권한이 있는 파일이 있었다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

아이노드 시각은 1970-01-01 00:00:00 UTC 를 영점으로 잰 값입니다[6]. 도구가 화면에 낼 때 현지 시각으로 바꾸는지는 도구 설정에서 확인합니다. 값의 단위와 변환은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)에서 다룹니다. atime 은 읽을 때, mtime 은 내용을 쓸 때, ctime 은 내용이나 소유자·권한을 바꿀 때 바뀝니다[6].

- `/dev/shm` 과 upstream `tmp.mount` 는 strictatime 으로 붙어서, 파일을 읽기만 해도 atime 이 바뀝니다[7][14]. 정리 규칙은 atime 도 보므로, 최근에 읽힌 파일은 기간이 지나도 지워지지 않습니다[8]. 디스크 `/tmp` 의 atime 동작은 그 파일 시스템의 마운트 옵션을 따릅니다.
- tmpfs 파일에도 atime·mtime·ctime 은 있지만, 전원을 끄면 파일째 사라지므로 라이브 수집이나 메모리 분석에서만 읽을 수 있습니다[3].
- 사설 폴더 이름의 부팅 ID 는 저널 항목의 `_BOOT_ID`(128비트 16진 문자열)와 맞춰 볼 수 있습니다[21]. `/proc/sys/kernel/random/boot_id` 는 UUID 라서 `-` 가 들어가므로 빼고 비교합니다[22]. 부팅 ID 는 [부팅과 종료 기록](../system-info/boot-shutdown.md)에서 다룹니다.
- Volatility 3 `linux.pagecache.RecoverFs` 로 되살린 파일의 수정 시각은 원래 값이 아니라 플러그인을 돌린 시각입니다[18]. 원래 시각은 `linux.pagecache.Files` 출력의 AccessTime·ModificationTime·ChangeTime 열에서 읽습니다[18].

## 함정과 한계

- "/tmp 는 재부팅하면 비워진다" 는 `/tmp` 가 tmpfs 일 때 이야기입니다. Ubuntu 24.04 와 RHEL 9 는 기본이 디스크라서 나이 기준 정리만 있을 수 있으므로, 먼저 마운트 종류를 확인합니다[14][15].
- 디스크 `/tmp` 에서 지워진 파일은 파일 시스템에 따라 되살릴 여지가 있습니다. 방법은 [지운 파일 되살리기](../../03-techniques/analysis/file-recovery.md)를 봅니다.
- tmpfs 페이지는 메모리가 모자라면 스왑으로 나갈 수 있고, `noswap` 옵션을 붙이면 막힙니다[3]. 전원을 끈 뒤에도 스왑 영역에 조각이 남을 수 있으므로 [스왑과 최대 절전](../../01-foundations/disk-volume/swap-hibernation.md)을 함께 봅니다.
- memfd 는 경로가 없어서 `/dev/shm` 목록에 나오지 않고, SYSV 공유 메모리도 마찬가지입니다[3][5]. 라이브 시스템에서 `/proc/PID/fd` 링크를 봐야 합니다. `/proc` 읽는 법은 [실행 중인 프로세스](../execution/proc.md)에서 다룹니다.
- logind 의 `RemoveIPC=` 는 기본이 yes 라서, 사용자의 마지막 세션이 끝나면 그 사용자의 System V·POSIX IPC 객체를 지웁니다. POSIX 공유 메모리도 여기에 들고, root 와 시스템 계정은 빠집니다[13]. 일반 계정이 `/dev/shm` 에 만든 객체는 로그아웃 뒤 사라졌을 가능성이 있습니다.
- UAC 는 `/tmp`·`/var/tmp`·`/dev/shm`·`/run/shm` 에서 일반 파일과 심볼릭 링크만, 한 파일에 10MB(`max_file_size: 10485760`)까지만 가져옵니다[1]. 그보다 큰 파일은 가져오지 않습니다.
- Velociraptor `Linux.Detection.AnomalousFiles` 의 기본 검색 경로는 `/home/**,tmp/**` 이고 `tmp` 앞에 `/` 가 없습니다[19]. 결과에 `/tmp` 아래 경로가 실제로 들어왔는지 확인합니다.

## 직접 분석해 보기

### 이름과 링크로 한 번

tmpfs 는 디스크 구조가 없어서 헥스로 따라갈 대상이 없습니다. 대신 폴더 이름과 fd 링크를 읽습니다. 아래 값은 모두 만든 예시입니다.

```
/tmp/systemd-private-0f3c9a7e5b2d4c18a6e1f09d3b7c2a45-nginx.service-Bv3kPq
/var/tmp/systemd-private-0f3c9a7e5b2d4c18a6e1f09d3b7c2a45-nginx.service-T8wZrc
/tmp/systemd-private-9a41d07c3e8f4b52b1c6e2f7a0d95b3e-nginx.service-Lm2QxN
```

1. `systemd-private-` 뒤 32자리가 부팅 ID 입니다. 첫 두 줄은 같은 부팅이고 셋째 줄은 다른 부팅입니다.
2. 부팅 ID 뒤 `-XXXXXX` 앞까지가 유닛 이름입니다. 셋 다 `nginx.service` 가 `PrivateTmp=` 로 돈 흔적입니다.
3. 다른 부팅의 폴더가 남아 있다면, 다음 부팅의 `R!` 정리가 아직 돌지 않았거나 정리 규칙을 바꾼 것입니다[9]. `journalctl --list-boots` 로 두 부팅 ID 가 언제였는지 맞춥니다.
4. 사설 폴더 안의 `tmp` 에 남은 파일은 그 서비스가 쓴 임시 파일이고, 서비스가 멈추면 사라집니다[11].

라이브 시스템에서 fd 링크를 읽으면 아래 모양이 나옵니다.

```
$ readlink /proc/4242/fd/5
/memfd:worker (deleted)
$ readlink /proc/4242/fd/7
/dev/shm/.cache01 (deleted)
```

`/memfd:` 로 시작하면 memfd 이고[5], `(deleted)` 는 원래 경로가 지워졌다(unlink)는 표시입니다[20]. 프로세스가 fd 를 쥐고 있는 동안에는 `/proc/4242/fd/5` 를 읽어 내용을 떠 올 수 있습니다[2].

### 공개 도구로 한 번

- **라이브**: UAC 의 `files/system` 항목이 `/tmp`, `/var/tmp`, `/dev/shm`, `/run/shm` 을 모읍니다[1]. `live_response/process/deleted` 는 실행 파일이 `(deleted)` 인 프로세스의 fd 중 `/dev/shm` 을 가리키면서 `(deleted)` 인 것과, 모든 프로세스의 fd 중 `memfd` 이면서 `(deleted)` 인 것을 찾아 `dd ... bs=1024 count=20000` 으로 앞부분(약 20MB)을 떠 옵니다[2]. `live_response/storage/findmnt` 는 `findmnt --ascii` 와 `findmnt -J` 출력을 받습니다[2]. 라이브 수집 순서는 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md)을 봅니다.
- **라이브(탐지)**: Velociraptor `Linux.Detection.AnomalousFiles` 는 점으로 시작하는 숨김 파일, 10485760바이트보다 큰 파일, SUID 파일을 찾습니다[19].
- **메모리**: Volatility 3 `linux.pagecache.Files` 는 페이지 캐시에 있는 아이노드를 마운트 지점·파일 종류·권한·세 시각·경로와 함께 냅니다[18]. `linux.pagecache.InodePages` 는 아이노드 하나의 내용을 파일로 떠 오고, `linux.pagecache.RecoverFs --tmpfs-only` 는 tmpfs 파일만 골라 압축 tar 로 되살립니다[18]. 메모리 수집과 분석 일반은 [메모리 수집](../../03-techniques/acquisition/memory-acquisition.md)과 [메모리 분석](../../03-techniques/analysis/memory-analysis.md)을 봅니다.
- **사후 이미지**: `/etc/fstab`, `/etc/tmpfiles.d/`, `/usr/lib/tmpfiles.d/tmp.conf`, `/etc/systemd/system/local-fs.target.wants/` 를 읽어 `/tmp` 의 종류와 정리 기간을 정하고, 디스크 `/tmp`·`/var/tmp` 에 남은 파일과 `systemd-private-*` 폴더를 목록으로 뽑습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [셸 명령 기록](../execution/shell-history/index.md) | `/tmp`·`/dev/shm` 경로가 든 명령과 파일 이름 |
| [감사 로그의 파일 감시](auditd-watches.md) | `/tmp` 나 `/dev/shm` 에 감시 규칙이 걸려 있었다면 파일을 만든 프로세스와 계정 |
| [감사 로그의 실행 기록](../execution/auditd-execve.md) | 임시 폴더 경로로 실행한 기록 |
| [실행 중인 프로세스](../execution/proc.md) | `exe`·`fd` 링크의 `(deleted)`, `memfd:` |
| [systemd 서비스와 타이머](../persistence/systemd-units.md) | 유닛 파일의 `PrivateTmp=` 설정과 사설 폴더 이름의 유닛 |
| [부팅과 종료 기록](../system-info/boot-shutdown.md) | 사설 폴더의 부팅 ID, 정리 타이머가 돈 부팅 |
| [로그인 기록](../logins/wtmp-btmp-lastlog.md) | `/dev/shm` 파일 소유 계정의 로그아웃 시각(RemoveIPC) |

여러 기록의 시각을 한 줄로 늘어놓는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md)를 봅니다. 채굴기처럼 임시 폴더에서 실행 파일이 도는 사건의 흐름은 [채굴기가 돌았나](../../04-scenarios/intrusion/cryptominer.md)에서 다룹니다.

## 실습

공개 Linux 시험 데이터(NIST CFReDS 등)나 직접 만든 가상 머신 이미지로 아래 질문을 풀어 봅니다.

1. 이 시스템의 `/tmp` 는 디스크인가 tmpfs 인가? `/etc/fstab` 과 `local-fs.target.wants/` 중 어디서 답을 찾았는가?
2. `/etc/tmpfiles.d/` 에 `tmp.conf` 가 있는가? 있다면 `/tmp`·`/var/tmp` 의 정리 기간은 기본값과 어떻게 다른가?
3. `systemd-private-*` 폴더가 있다면 부팅 ID 는 몇 개이고, 각각 저널의 어느 부팅과 맞는가? 어떤 유닛이 `PrivateTmp=` 로 돌았는가?
4. 디스크 `/tmp`·`/var/tmp` 에 남은 파일 중 점으로 시작하거나 실행 권한이 있는 파일이 있는가? 그 소유자는 어느 계정인가?
5. 같은 시점의 메모리 이미지가 있다면 `linux.pagecache.Files` 에서 `/dev/shm` 아래 파일이 보이는가? 그 시각은 디스크의 다른 기록과 맞는가?

## 참고 문헌

1. UAC, artifacts/files/system (tmp.yaml·var_tmp.yaml·dev_shm.yaml·run_shm.yaml) — https://github.com/tclahr/uac/tree/main/artifacts/files/system
2. UAC, artifacts/live_response/process/deleted.yaml·storage/findmnt.yaml — https://github.com/tclahr/uac/blob/main/artifacts/live_response/process/deleted.yaml , https://github.com/tclahr/uac/blob/main/artifacts/live_response/storage/findmnt.yaml
3. Linux kernel, Documentation/filesystems/tmpfs.rst — https://github.com/torvalds/linux/blob/master/Documentation/filesystems/tmpfs.rst
4. Linux man-pages, shm_overview(7) — https://github.com/mkerrisk/man-pages/blob/master/man7/shm_overview.7
5. Linux man-pages, memfd_create(2) — https://github.com/mkerrisk/man-pages/blob/master/man2/memfd_create.2
6. Linux man-pages, inode(7) — https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
7. systemd, src/shared/mount-setup.c — https://github.com/systemd/systemd/blob/main/src/shared/mount-setup.c ; RHEL 9 source-git — https://github.com/redhat-plumbers/systemd-rhel9/blob/main/src/shared/mount-setup.c
8. systemd, tmpfiles.d(5)·systemd-tmpfiles(8) — https://github.com/systemd/systemd/blob/main/man/tmpfiles.d.xml , https://github.com/systemd/systemd/blob/main/man/systemd-tmpfiles.xml
9. systemd, tmpfiles.d/tmp.conf·systemd-tmp.conf·x11.conf, units/systemd-tmpfiles-clean.timer — https://github.com/systemd/systemd/blob/main/tmpfiles.d/tmp.conf , https://github.com/systemd/systemd/blob/main/tmpfiles.d/systemd-tmp.conf , https://github.com/systemd/systemd/blob/main/tmpfiles.d/x11.conf , https://github.com/systemd/systemd/blob/main/units/systemd-tmpfiles-clean.timer ; RHEL 9 source-git — https://github.com/redhat-plumbers/systemd-rhel9/blob/main/tmpfiles.d/tmp.conf
10. systemd, docs/TEMPORARY_DIRECTORIES.md — https://github.com/systemd/systemd/blob/main/docs/TEMPORARY_DIRECTORIES.md
11. systemd, systemd.exec(5) (PrivateTmp=) — https://github.com/systemd/systemd/blob/main/man/systemd.exec.xml ; v255·v257 태그 — https://github.com/systemd/systemd/blob/v255/man/systemd.exec.xml , https://github.com/systemd/systemd/blob/v257/man/systemd.exec.xml ; RHEL 9 source-git — https://github.com/redhat-plumbers/systemd-rhel9/blob/main/man/systemd.exec.xml
12. systemd, src/core/namespace.c — https://github.com/systemd/systemd/blob/main/src/core/namespace.c
13. systemd, logind.conf(5) (RemoveIPC=) — https://github.com/systemd/systemd/blob/main/man/logind.conf.xml
14. systemd, units/tmp.mount·units/meson.build — https://github.com/systemd/systemd/blob/main/units/tmp.mount , https://github.com/systemd/systemd/blob/main/units/meson.build ; RHEL 9 source-git — https://github.com/redhat-plumbers/systemd-rhel9/blob/main/units/tmp.mount , https://github.com/redhat-plumbers/systemd-rhel9/blob/main/units/meson.build
15. Ubuntu systemd 패키징(255.4-1ubuntu8.17), debian/rules — https://git.launchpad.net/ubuntu/+source/systemd/tree/debian/rules?h=ubuntu/noble-updates
16. CentOS Stream 9 systemd 패키징, systemd.spec (패치 0092·0105) — https://gitlab.com/redhat/centos-stream/rpms/systemd/-/blob/c9s/systemd.spec
17. dissect.target, plugins/os/unix/_os.py — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/_os.py
18. Volatility 3, plugins/linux/pagecache.py — https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/pagecache.py
19. Velociraptor, Linux/Detection/AnomalousFiles.yaml — https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Detection/AnomalousFiles.yaml
20. Linux man-pages, proc(5) — https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
21. systemd, systemd.journal-fields(7) (_BOOT_ID=) — https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
22. Linux kernel, Documentation/admin-guide/sysctl/kernel.rst (random/boot_id) — https://github.com/torvalds/linux/blob/master/Documentation/admin-guide/sysctl/kernel.rst
