---
title: "디렉터리 구조와 주요 경로"
parent: "기반 · 파일 시스템"
nav_order: 90
---

# 디렉터리 구조와 주요 경로 (FHS)

Linux 는 어느 배포판이든 뼈대가 비슷한 디렉터리 구조 (File System Hierarchy) 를 따르고, 이 구조를 알면 흔적이 어느 디렉터리에 남는지, 전원을 끄면 무엇이 사라지는지를 먼저 추정할 수 있습니다. 이 페이지는 주요 경로의 쓰임과 휘발성, 이미지 안에서 디렉터리 배치를 되살리는 법을 다룹니다.

전통적인 기준은 hier(7) 설명서와 FHS 3.0 입니다[1][2]. systemd 를 쓰는 시스템은 UAPI.9 "Linux File System Hierarchy" 를 따르고, systemd 의 file-hierarchy(7) 설명서도 본문 대신 이 문서를 가리킵니다[2][3]. UAPI.9 는 옛 문서보다 제조사 기본값과 현지 설정, 설치 파일과 영구 데이터, 실행 중에만 있는 파일을 더 엄격하게 나눕니다[2].

## 이 구조를 쓰는 아티팩트

주요 디렉터리와 그 아래에 남는 흔적을 다루는 페이지를 묶으면 다음과 같습니다. 파일 이름과 형식은 각 페이지에서 설명합니다.

| 디렉터리 | 담기는 것 | 함께 볼 페이지 |
|---|---|---|
| `/etc` | 기계별 설정[1][2] | [계정 파일](../users-auth/passwd-shadow-group.md), [sudo 설정](../users-auth/sudoers.md), [systemd 서비스와 타이머](../../02-artifacts/persistence/systemd-units.md) |
| `/etc/skel` | 새 계정 홈에 복사되는 파일[1] | [셸 시작 파일](../../02-artifacts/persistence/shell-startup.md) |
| `/var/log` | 영구 로그[1][2] | [syslog 형식과 rsyslog](../logging/syslog-rsyslog.md), [systemd 저널](../logging/systemd-journal/index.md) |
| `/var/lib` | 프로그램의 영구 상태 데이터[1][2] | [dpkg·apt 기록](../../02-artifacts/packages/dpkg-apt.md), [rpm·dnf·yum 기록](../../02-artifacts/packages/rpm-dnf.md) |
| `/var/spool/cron`, `/var/spool/at` | cron·at 예약 작업[1] | [cron·anacron·at](../../02-artifacts/persistence/cron-at.md) |
| `/var/mail` | 사용자 메일함(`/var/spool/mail` 을 대신함)[1] | [메일 서버 로그](../../02-artifacts/servers/mail-server-logs.md) |
| `/home`, `/root` | 일반 사용자 홈, root 홈[1][2] | [셸 명령 기록](../../02-artifacts/execution/shell-history/index.md), [Linux 의 브라우저 프로필](../../02-artifacts/desktop/browsers.md) |
| `/tmp`, `/var/tmp`, `/dev/shm` | 누구나 쓸 수 있는 임시 공간[2] | [임시 폴더와 메모리 파일 시스템](../../02-artifacts/file-activity/tmp-shm.md) |
| `/run` | 부팅 뒤 실행 중 데이터·소켓[2] | [라이브 응답 수집](../../03-techniques/acquisition/live-response.md) |
| `/proc`, `/sys` | 커널이 보여 주는 가상 파일 시스템[1][2] | [실행 중인 프로세스](../../02-artifacts/execution/proc.md) |

## 구조

### 최상위 디렉터리

아래 표의 "전원을 끈 뒤" 열은 디스크 이미지에 내용이 남는지를 뜻합니다. 실제로 어느 파일 시스템에 마운트됐는지는 분석 대상 시스템의 `/etc/fstab` 과 마운트 기록으로 확인합니다(아래 "읽는 법").

| 경로 | 쓰임 | 전원을 끈 뒤 |
|---|---|---|
| `/boot` | 커널과 부트로더 파일. EFI 시스템이면 EFI 시스템 파티션(ESP)일 수 있음[2] | 남음 |
| `/efi` | ESP 를 `/boot` 와 따로 둘 때의 마운트 지점[2] | 남음 |
| `/etc` | 기계별 설정. 읽기 전용일 수도 있음[2] | 남음 |
| `/home` | 일반 사용자 홈. 네트워크 파일 시스템일 수 있음[2] | 남음(네트워크면 이미지 밖) |
| `/root` | root 홈. `/home` 이 없어도 root 가 로그인하도록 밖에 둠[2] | 남음 |
| `/opt` | 추가 패키지[1]. UAPI.9 는 쓰지 않기를 권함[2] | 남음 |
| `/srv` | 이 시스템이 내주는 서버 데이터[1][2] | 남음 |
| `/usr` | 제조사가 넣은 운영체제 자원. 관리자는 패키지를 설치·삭제할 때 말고는 고치지 않음[2] | 남음 |
| `/usr/local` | 이 사이트에서 따로 설치한 프로그램[1] | 남음 |
| `/var` | 바뀌는 영구 데이터(로그·스풀·상태)[1][2] | 남음 |
| `/var/cache` | 지워도 다시 만들 수 있는 캐시[1][2] | 남음 |
| `/var/crash` | 시스템 충돌 덤프(선택)[1] | 남음 |
| `/var/tmp` | 크고 오래 두는 임시 파일. 보통 디스크에 있음[2] | 남음 |
| `/tmp` | 작은 임시 파일. 보통 tmpfs[2] | tmpfs 면 사라짐 |
| `/run` | 실행 중 데이터·소켓 파일. tmpfs, 부팅 때 비움[2] | 사라짐 |
| `/run/log` | 실행 중 시스템 로그. `/var/log` 를 쓸 수 없을 때도 쓸 수 있음[2] | 사라짐 |
| `/run/user` | 사용자별 실행 중 디렉터리(`$XDG_RUNTIME_DIR`)가 놓이는 곳. 보통 사용자마다 tmpfs, 재부팅·로그아웃 때 비움[2] | 사라짐 |
| `/dev` | 장치 노드. 보통 devtmpfs[2] | 사라짐 |
| `/dev/shm` | POSIX 공유 메모리. tmpfs, 부팅 때 비움[2] | 사라짐 |
| `/proc`, `/sys` | 커널 가상 파일 시스템. 보통 파일을 두는 곳이 아님[2] | 사라짐 |
| `/lost+found` | 디스크 고장·충돌로 떨어져 나온 파일 조각[1]. ext4 에서는 보통 아이노드 11[4] | 남음 |
| `/media`, `/mnt` | 이동식 매체와 임시 마운트 지점[1] | 마운트 지점만 남음 |

### 호환 심볼릭 링크

UAPI.9 는 제조사 파일을 `/usr` 한 곳에 두고, 옛 경로는 호환 심볼릭 링크로 남깁니다[2].

| 링크 | 가리키는 곳 |
|---|---|
| `/bin`, `/sbin`, `/usr/sbin` | `/usr/bin` |
| `/lib` | `/usr/lib` |
| `/lib64` | 동적 로더를 이 경로에 두는 ABI 에서만 있고, 라이브러리 디렉터리(`$libdir`)를 가리킴 |
| `/var/run` | `/run` |

hier(7) 은 `/bin`·`/sbin` 을 부팅과 복구에 필요한 명령을 두는 별도 디렉터리로 설명합니다[1]. 분석 대상 시스템이 어느 쪽인지는 이미지에서 `/bin` 이 디렉터리인지 링크인지를 보면 됩니다.

### 홈 디렉터리 안

| 경로 | 쓰임 | 바꾸는 환경 변수 |
|---|---|---|
| `~/.config` | 앱 설정. 새 계정에서는 비어 있거나 없음[2] | `$XDG_CONFIG_HOME` |
| `~/.cache` | 지워도 되는 캐시[2] | `$XDG_CACHE_HOME` |
| `~/.local/share` | 여러 패키지가 함께 쓰는 자원(글꼴 등)[2] | `$XDG_DATA_HOME` |
| `~/.local/state` | 앱 상태. 새 계정에서는 비어 있거나 없음[2] | `$XDG_STATE_HOME` |
| `~/.local/bin` | 사용자 `$PATH` 에 들어가는 실행 파일[2] | 없음 |

환경 변수가 설정돼 있으면 앱은 기본 경로 대신 그 경로를 쓰므로[2], 흔적이 기본 경로에 없으면 셸 시작 파일과 세션 환경에서 이 변수를 찾아봅니다.

### 설치 기본 분할

| 항목 | Ubuntu 24.04 LTS | RHEL 9 |
|---|---|---|
| 기본 파일 시스템 | ext4[13] | XFS[11] |
| 기본 구성 | 안내 설치에서 직접 분할·LVM·ZFS 가운데 고름[13] | LVM[12] |
| 나뉘는 마운트 지점 | 직접 분할이면 부팅용 파티션 말고는 `/` 하나, LVM 이면 ext4 `/boot` 파티션과 볼륨 그룹 `ubuntu-vg` 안 논리 볼륨 `ubuntu-lv`(`/`)[13] | `/`(최소 1 GiB, 최대 70 GiB), `/home`(최소 500 MiB, 여유 공간 50 GiB 필요), swap[11] |

RHEL 9 기본 설치에서 `/home` 이 따로 만들어지면 `/` 와 다른 논리 볼륨이라서, `/` 만 이미징하면 사용자 홈이 빠집니다. LVM 구조는 [LVM 논리 볼륨](../disk-volume/lvm.md), 스왑은 [스왑과 최대 절전](../disk-volume/swap-hibernation.md) 페이지에서 다룹니다.

## 읽는 법

디스크 이미지에는 파일 시스템이 따로따로 들어 있으므로, 먼저 각 파일 시스템이 어느 디렉터리에 붙어 있었는지를 되살립니다.

1. 루트 파일 시스템에서 `/etc/fstab` 을 읽습니다. ForensicArtifacts 는 이 파일을 `LinuxFstab` 으로 수집합니다[5]. 한 줄은 장치, 마운트 지점, 파일 시스템 종류, 옵션, 나머지 두 필드까지 여섯 필드입니다[6]. 장치 필드는 `UUID=`, `LABEL=`, `/dev/mapper/...`, `/dev/VG이름/LV이름` 같은 모양으로 적힙니다[6].
2. 장치 필드의 UUID·레이블을 이미지 안 파일 시스템의 UUID·볼륨 이름과 맞춥니다. dissect.target 은 여기에 ext 계열 슈퍼블록의 "마지막 마운트 디렉터리"(`s_last_mounted`)가 fstab 마운트 지점과 같은지, Btrfs 면 `subvol`·`subvolid` 옵션이 같은지까지 비교해 파일 시스템을 제자리에 붙입니다[6]. 슈퍼블록 필드는 [ext4](ext4/index.md) 페이지에서 설명합니다.
3. `/tmp` 가 fstab 에 tmpfs 로 적혀 있는지 봅니다. dissect.target 은 swap·tmpfs·devpts·sysfs·procfs·overlayfs 줄을 지원하지 않는 종류로 보고 건너뜁니다[6]. tmpfs 로 붙은 디렉터리는 디스크 이미지에서 비어 있어도 정상입니다.
4. 실행 중인 시스템이면 `mount` 출력으로 지금 붙어 있는 파일 시스템을 기록합니다. UAC 는 이 출력을 `live_response/storage/mount.txt` 로 남깁니다[7]. fstab 에 없는 마운트(손으로 붙인 USB 등)는 이 출력에만 보이고, 흔적은 [마운트 기록](../../02-artifacts/devices/mounts.md) 페이지에서 다룹니다.
5. `/etc` 의 설정을 제조사 기본값과 비교할 때는 `/usr/share/factory/etc` 를 봅니다. UAPI.9 는 이 디렉터리에 `/etc` 에 놓일 수 있는 설정 파일의 원래 판을 두라고 정합니다[2]. 이 디렉터리가 채워져 있는 시스템이라면 바뀐 설정을 빠르게 추릴 수 있습니다. 패키지 파일 전체를 확인하는 방법은 [패키지 파일 변조 확인](../../02-artifacts/packages/package-verify.md) 페이지에 있습니다.

만든 예시 fstab 줄은 다음과 같습니다.

```
UUID=0a1b2c3d-1111-2222-3333-444455556666  /home  xfs    defaults          0 0
/dev/mapper/vg0-var                          /var   ext4   defaults          0 2
tmpfs                                        /tmp   tmpfs  nosuid,nodev      0 0
```

## 포렌식에서 중요한 점

**휘발 영역과 영구 영역이 나뉩니다.** `/run`, `/run/user`, `/dev/shm` 은 tmpfs 라서 전원을 끄면 사라지고, `/tmp` 도 보통 tmpfs 입니다[2]. 실행 중인 서비스의 소켓, PID 파일, 사용자 세션 파일, 공유 메모리에 둔 파일은 메모리나 라이브 수집으로만 얻을 수 있습니다. 반면 `/var/tmp` 는 보통 디스크에 있고 부팅 때 비우지 않습니다[2]. 수집 순서는 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md) 페이지를 봅니다.

**일반 사용자가 쓸 수 있는 곳은 몇 군데뿐입니다.** 일반 사용자는 `/tmp`, `/var/tmp`, `/dev/shm`, 자기 `$HOME`, `/run/user` 아래 자기 `$XDG_RUNTIME_DIR` 에만 쓸 수 있고, 권한 없는 시스템 프로세스는 `/tmp`, `/var/tmp`, `/dev/shm` 에만 쓸 수 있습니다[2]. 권한 없는 계정으로 들어온 침입자가 파일을 남겼다면 이 경로들이 먼저 볼 곳입니다. 이 밖의 시스템 경로에 새로 생긴 파일은 root 권한이나 패키지 설치를 거쳤을 가능성이 있습니다.

**임시 디렉터리는 오래된 파일을 저절로 지웁니다.** systemd 의 기본 `tmp.conf` 는 `/tmp` 를 10일, `/var/tmp` 를 30일 기준으로 정리하고, RHEL 9 용 systemd 소스의 파일도 같은 값입니다[8][9].

```
q /tmp 1777 root root 10d
q /var/tmp 1777 root root 30d
```

마지막 필드가 나이 (Age) 입니다. 기본으로는 파일의 접근·생성·수정·상태 변경 시각 가운데 하나라도 "지금 − 나이" 보다 새로우면 지우지 않고, 디렉터리는 상태 변경 시각(ctime)을 보지 않습니다[10]. 그래서 임시 디렉터리에서 파일이 없다는 사실만으로 누군가 지웠다고 볼 수 없습니다. 설정 파일은 `/etc/tmpfiles.d`, `/run/tmpfiles.d`, `/usr/local/lib/tmpfiles.d`, `/usr/lib/tmpfiles.d` 에서 읽고, `/etc/tmpfiles.d` 의 같은 이름 파일이 `/usr/lib/tmpfiles.d` 의 파일을 덮어씁니다[10]. 실제 시스템의 정리 기준은 이 디렉터리들의 `tmp.conf` 를 읽고 정합니다.

**장치 노드와 소켓이 놓일 자리가 정해져 있습니다.** UAPI.9 는 장치 노드를 `/dev` 아래에만, 소켓과 FIFO 를 `/run` 아래에만 두기를 권합니다[2]. 다른 경로에서 장치 노드나 소켓 파일이 보이면 무엇이 만들었는지 확인해 볼 만합니다. 파일 종류는 아이노드의 모드 값으로 구분하고, 권한 비트는 [권한·확장 속성·ACL·Capabilities](permissions-xattr.md) 페이지에서 다룹니다.

**`/lost+found` 에 조각이 있을 수 있습니다.** 이 디렉터리에는 디스크 고장이나 시스템 충돌로 망가져 떨어져 나온 파일 조각이 들어갑니다[1]. 비어 있지 않다면 예전에 파일 시스템 손상이나 비정상 종료가 있었을 가능성이 있습니다.

## 함정

**디스크 이미지의 `/var/run` 은 비어 있습니다.** `/var/run` 은 tmpfs 인 `/run` 을 가리키는 링크라서, 이미지에서는 링크만 있거나 가리키는 디렉터리가 비어 있습니다[2]. `/var/run` 에 두던 프로세스 ID(PID) 파일과 로그인 사용자 정보(utmp)도 같은 이유로 이미지에 없을 수 있습니다[1]. 로그인 기록 파일은 [로그인 기록 파일 형식](../logging/utmp-wtmp-format.md) 페이지에서 다룹니다.

**`/tmp` 가 tmpfs 인지는 배포판과 설정에 따라 다릅니다.** `/tmp` 는 보통 tmpfs 이지만 늘 그런 것은 아닙니다[2]. 실제 시스템의 fstab 과 마운트 기록으로 확인하고, 디스크의 `/tmp` 디렉터리가 비어 있다고 파일이 없었다고 보지 않습니다.

**링크를 따라가면 같은 파일을 두 번 셉니다.** `/bin` 이 `/usr/bin` 을 가리키는 시스템에서 두 경로를 모두 수집하거나 해시하면 같은 파일이 두 번 나옵니다. 경로를 비교할 때도 `/bin/bash` 와 `/usr/bin/bash` 가 같은 파일일 수 있습니다[2].

**네트워크 홈은 이미지 밖에 있습니다.** `/home` 은 다른 시스템과 공유하는 네트워크 파일 시스템일 수 있습니다[2]. fstab 에 `nfs` 줄이 있으면 사용자 흔적은 파일 서버에서 따로 수집해야 합니다.

**환경 변수가 기본 경로를 바꿉니다.** `$TMPDIR` 이 설정되면 앱은 `/tmp`·`/var/tmp` 대신 그 경로를 쓰고[2], XDG 변수는 홈 안 경로를 바꿉니다[2].

## 도구

| 도구 | 쓰임 |
|---|---|
| dissect.target | 이미지 안 fstab 을 읽어 파일 시스템을 마운트 지점에 붙임[6] |
| UAC | 실행 중인 시스템의 `mount` 출력 수집[7] |
| ForensicArtifacts `LinuxFstab` | `/etc/fstab` 수집 정의[5] |
| `systemd-path` | 이 시스템에서 표준 경로가 실제로 어디인지 조회[2] |
| `ls -l /`, `stat` | 이미지를 읽기 전용으로 붙인 뒤 최상위 경로가 링크인지 확인 |

## 참고 문헌

1. man-pages, `man7/hier.7`. https://github.com/mkerrisk/man-pages/blob/master/man7/hier.7
2. UAPI Group, "UAPI.9 Linux File System Hierarchy", `specs/linux_file_system_hierarchy.md`. https://github.com/uapi-group/specifications/blob/main/specs/linux_file_system_hierarchy.md
3. systemd, `man/file-hierarchy.xml`. https://github.com/systemd/systemd/blob/main/man/file-hierarchy.xml
4. Linux 커널, `Documentation/filesystems/ext4/special_inodes.rst`. https://github.com/torvalds/linux/blob/master/Documentation/filesystems/ext4/special_inodes.rst
5. ForensicArtifacts, `artifacts/data/linux.yaml` (LinuxFstab). https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
6. dissect.target, `dissect/target/plugins/os/unix/_os.py` (`_add_mounts`, `parse_fstab`). https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/_os.py
7. UAC, `artifacts/live_response/storage/mount.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/live_response/storage/mount.yaml
8. systemd, `tmpfiles.d/tmp.conf`. https://github.com/systemd/systemd/blob/main/tmpfiles.d/tmp.conf
9. systemd-rhel9, `tmpfiles.d/tmp.conf`. https://github.com/redhat-plumbers/systemd-rhel9/blob/main/tmpfiles.d/tmp.conf
10. systemd, `man/tmpfiles.d.xml`. https://github.com/systemd/systemd/blob/main/man/tmpfiles.d.xml
11. anaconda (rhel-9 가지), `data/product.d/rhel.conf`. https://github.com/rhinstaller/anaconda/blob/rhel-9/data/product.d/rhel.conf
12. anaconda (rhel-9 가지), `data/anaconda.conf`. https://github.com/rhinstaller/anaconda/blob/rhel-9/data/anaconda.conf
13. subiquity (ubuntu/noble 가지), `subiquity/server/controllers/storage.py`. https://github.com/canonical/subiquity/blob/ubuntu/noble/subiquity/server/controllers/storage.py
