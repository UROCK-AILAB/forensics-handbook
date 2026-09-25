---
title: "셸 시작 파일"
parent: "아티팩트 · 지속성"
nav_order: 530
---

# 셸 시작 파일 (.bashrc·profile)

셸이 뜰 때마다 읽어 실행하는 `/etc/profile`, `~/.bashrc` 같은 파일입니다. 여기에 한 줄을 넣으면 사용자가 터미널을 열거나 로그인할 때마다 그 명령이 돌기 때문에, 지속성 흔적을 찾을 때 서비스·cron 과 함께 반드시 봅니다.

## 무엇을 기록하나 · 왜 생기나

셸 시작 파일 (shell startup file) 은 로그가 아니라 셸이 시작할 때 실행하는 명령 목록입니다. 별칭 (alias), 함수, 환경 변수, `PATH`, 명령 기록 설정이 여기에 들어가고, 파일 안의 어떤 명령이든 셸을 띄운 계정의 권한으로 실행됩니다. 그래서 파일에 남은 내용 자체가 증거이고, 파일 시스템의 시각은 언제 바뀌었는지를, 소유자는 어느 계정의 파일인지를 알려 줍니다.

bash 가 어떤 파일을 읽는지는 셸이 어떻게 떴는지에 따라 다릅니다[1].

- **대화형 로그인 셸** (또는 `--login`): `/etc/profile` 을 읽은 뒤 `~/.bash_profile`, `~/.bash_login`, `~/.profile` 을 이 순서로 찾아 **처음 있고 읽을 수 있는 하나만** 실행합니다. 로그인 셸이 끝날 때 `~/.bash_logout` 을 읽습니다. `--noprofile` 로 끕니다.
- **로그인이 아닌 대화형 셸**: `~/.bashrc` 를 읽습니다. `--norc` 로 끄고, `--rcfile 파일` 로 다른 파일을 지정합니다.
- **비대화형 셸** (스크립트 실행): 환경 변수 `BASH_ENV` 가 가리키는 파일을 읽습니다. 이때 `PATH` 로 파일을 찾지 않습니다.
- **`sh` 라는 이름으로 불린 bash**: 로그인 셸이면 `/etc/profile`, `~/.profile` 을 읽고, 대화형이면 `ENV` 가 가리키는 파일을 읽습니다.
- **원격 셸 데몬이 띄운 비대화형 셸**: 표준 입력이 네트워크 연결이라고 판단하면(rshd·sshd) `~/.bashrc` 를 읽습니다. `sh` 로 불렸을 때는 읽지 않습니다.

실제 사용자 ID 와 유효 사용자 ID (그룹 ID 도 같음) 가 다르고 `-p` 옵션이 없으면 bash 는 시작 파일을 하나도 읽지 않습니다[1].

## 위치와 버전별 차이

원래 bash 는 `/etc/bash.bashrc` 를 읽지 않습니다[1]. Debian 계열 bash 는 컴파일할 때 `SYS_BASHRC "/etc/bash.bashrc"` 와 `SYS_BASH_LOGOUT "/etc/bash.bash_logout"` 을 켜서, 로그인이 아닌 대화형 셸과 원격 비대화형 셸에서 `~/.bashrc` 앞에 `/etc/bash.bashrc` 를 읽습니다[2]. 같은 패치는 초기 환경에 `SSH_CLIENT` 나 `SSH2_CLIENT` 가 있으면 sshd 가 띄운 셸로 보고 `.bashrc` 를 읽는 옵션(`SSH_SOURCE_BASHRC`)도 켭니다[2]. RHEL 쪽 시스템 파일 이름은 `/etc/bashrc` 이고, bash 가 직접 읽는 것이 아니라 `/etc/profile` 과 사용자 `~/.bashrc` 가 불러옵니다[5][6].

| 구분 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| 시스템 로그인 파일 | `/etc/profile` → (bash 이고 `PS1` 이 있으면) `/etc/bash.bashrc` → `/etc/profile.d/*.sh`[4] | `/etc/profile` → `/etc/profile.d/*.sh`, `/etc/profile.d/sh.local` → (bash 면) `/etc/bashrc`[6] |
| 시스템 대화형 파일 | `/etc/bash.bashrc` (bash 가 직접 읽음)[2] | `/etc/bashrc` (`~/.bashrc` 가 불러옴, 로그인이 아닌 셸이면 여기서 `/etc/profile.d/*.sh` 도 읽음)[5][6] |
| 사용자 로그인 파일 (skel) | `~/.profile`: bash 면 `~/.bashrc` 를 불러오고 `~/bin`, `~/.local/bin` 을 `PATH` 앞에 붙임[3] | `~/.bash_profile`: `~/.bashrc` 를 불러옴[5] |
| 사용자 대화형 파일 (skel) | `~/.bashrc`: 대화형이 아니면 바로 끝남, `~/.bash_aliases` 와 bash-completion 을 불러옴[3] | `~/.bashrc`: `/etc/bashrc` 를 불러오고 `~/.local/bin:~/bin` 을 `PATH` 앞에 붙이며 `~/.bashrc.d/` 안의 파일을 전부 불러옴[5] |
| 파일을 설치하는 패키지 | `/etc/profile` 은 base-files[4], `/etc/bash.bashrc` 와 skel 파일은 bash[3] | `/etc/profile`·`/etc/bashrc` 는 setup[6], skel 파일은 bash[5] |

두 배포판 모두 `/etc/profile.d/*.sh` 를 불러오므로[4][6] 이 폴더에 파일 하나를 두면 로그인하는 모든 사용자에게 걸립니다. RHEL 은 로그인이 아닌 셸에서도 `/etc/bashrc` 가 이 폴더를 다시 읽습니다[6]. 명령 기록 관련 기본값(`HISTSIZE`, `HISTCONTROL`, `histappend`)은 [bash 기록](../execution/shell-history/bash.md) 쪽을 봅니다.

다른 셸도 저마다 시작 파일이 있습니다. zsh 는 사용자 `~/.zlogin`, `~/.zprofile`, `~/.zshenv`, `~/.zshrc` 와 시스템 `/etc/zshenv`, `/etc/zprofile`, `/etc/zshrc`, `/etc/zlogin` 을 씁니다[7]. UAC 는 ash, dash, fish, ksh, mksh, tcsh 등 셸마다 수집 정의를 따로 두고 있으므로[7], 계정의 로그인 셸(`/etc/passwd` 마지막 칸)을 먼저 보고 그 셸의 파일을 찾으면 됩니다.

셸과 상관없이 로그인 환경 변수를 넣는 길도 있습니다. PAM 의 `pam_env` 모듈은 `/etc/security/pam_env.conf` 와 `/etc/security/pam_env.conf.d/*.conf`, `/etc/environment` 와 `/etc/environment.d/*` 를 읽고, `user_readenv=1` 이면 `$HOME/.pam_environment` 도 읽습니다[9]. `user_readenv` 는 기본으로 꺼져 있고, 1.5.0 부터 앞으로 없앨 기능으로 분류돼 있습니다[9]. PAM 설정 자체를 바꾼 흔적은 [PAM 모듈 변조](pam-backdoor.md) 쪽에서 다룹니다.

## 구조

형식은 셸 문법으로 된 평범한 텍스트이고 따로 머리 구조가 없습니다. 분석에서 중요한 것은 파일이 서로 불러오는 사슬입니다. Ubuntu 기본 설정에서 대화형 로그인 셸은 `/etc/profile` → `/etc/bash.bashrc` → `/etc/profile.d/*.sh` → `~/.profile` → `~/.bashrc` → `~/.bash_aliases` 순으로 이어지고[3][4], RHEL 9 은 `/etc/profile` → `/etc/profile.d/*.sh` → `/etc/bashrc` → `~/.bash_profile` → `~/.bashrc` → `/etc/bashrc` → `~/.bashrc.d/*` 순으로 이어집니다[5][6]. RHEL `/etc/bashrc` 는 `BASHRCSOURCED` 변수로 두 번 실행을 막습니다[6].

파일 안에서 위치도 봐야 합니다. Ubuntu skel `~/.bashrc` 는 맨 앞의 `case $- in ... *) return;; esac` 로 대화형이 아니면 곧바로 끝나고[3], `/etc/bash.bashrc` 도 머리 주석 다음 첫 명령 `[ -z "$PS1" ] && return` 으로 같은 일을 합니다[3]. 그래서 이 검사 **앞**에 들어간 줄은 `ssh 호스트 명령` 처럼 원격으로 띄운 비대화형 셸에서도 실행되고, 뒤에 들어간 줄은 대화형 셸에서만 실행됩니다. RHEL skel `~/.bashrc` 에는 이런 검사가 없습니다[5].

## 증거로서 의미

### 증명하는 것

- 파일을 수집한 시점에 그 명령·별칭·함수·환경 변수가 적혀 있었다는 것.
- 파일의 소유자와 권한, 그리고 어느 사슬에 걸려 있는지를 보면 그 명령이 어느 계정의 셸에서, 어떤 종류의 셸에서 실행될 조건이었는지.
- 패키지가 설치한 원본(`/etc/skel`, 패키지 데이터베이스)과 다르다면, 설치 뒤에 누군가 내용을 바꿨다는 것.

### 증명하지 못하는 것

- 그 명령이 실제로 실행됐다는 것. 셸이 열렸는지는 로그인 기록과 대조해야 하고, 어떤 종류의 셸이 열렸는지에 따라 읽는 파일이 다릅니다.
- 누가 파일을 고쳤는지. 파일 소유자는 고친 사람이 아니라 파일을 가진 계정이고, root 는 어느 사용자의 파일이든 고칠 수 있습니다.
- 파일에 적힌 값이 실행 중인 셸의 값과 같다는 것. 셸 안에서 나중에 바꾼 값은 파일에 남지 않습니다.

## 시각 해석

파일 시스템의 시각은 1970-01-01 00:00:00 UTC 를 기준으로 센 값이라 시간대가 없고[14], 도구가 현지 시각으로 바꿔 보여 줄 뿐입니다([시각 값](../../01-foundations/value-decoding/time-values.md)). mtime 은 마지막으로 내용을 바꾼 때, ctime 은 내용을 쓰거나 소유자·권한 같은 아이노드 정보를 마지막으로 바꾼 때입니다[14]. 대화형 셸이 뜰 때마다 파일을 읽으므로 atime 은 자주 바뀔 수 있고, 얼마나 자주 갱신하는지는 검체의 마운트 옵션에 따라 다르므로 `/etc/fstab` 과 [마운트 기록](../devices/mounts.md)으로 먼저 확인합니다. ext4 생성 시각 (crtime) 은 [ext4](../../01-foundations/filesystem/ext4/index.md) 쪽을 봅니다.

mtime 은 사용자가 되돌릴 수 있지만 그렇게 아이노드 정보를 바꾸면 ctime 이 함께 바뀌므로[14], mtime 이 오래됐는데 ctime 만 최근이면 시각을 손봤을 가능성이 있습니다. 시각 조작을 가려내는 흐름은 [시각을 조작했나](../../04-scenarios/insider/time-manipulation.md) 쪽을 봅니다.

## 함정과 한계

- **처음 하나만 읽는다.** `~/.bash_profile` 이 있으면 bash 로그인 셸은 `~/.profile` 을 읽지 않습니다[1]. Ubuntu 기본은 `~/.profile` 만 있으므로[3], 누군가 `~/.bash_profile` 을 새로 만들면 읽는 흐름 자체가 바뀝니다. 반대로 `~/.profile` 의 내용만 보고 "이 설정이 적용됐다" 고 쓰면 틀릴 수 있습니다.
- **수집 목록에서 빠지는 파일.** UAC 의 bash 정의는 `~/.bashrc`, `~/.profile`, `~/.bash_login`, `~/.bash_profile`, `~/.bash_aliases`, `~/.bash_logout`, `~/.inputrc`, `/etc/bash.bashrc` 를 모으고, 공통 정의는 `/etc/.login`, `/etc/profile`, `/etc/shells`, `/etc/profile.d/*` 를 모읍니다[7]. RHEL `/etc/bashrc` 는 `/etc` 전체 수집으로만 잡히고[8], `~/.bashrc.d/` 는 어느 목록에도 없습니다. RHEL 은 이 폴더 안 파일을 전부 불러오므로[5] 따로 모아야 합니다.
- **`PATH` 앞자리.** 두 배포판 모두 사용자 홈의 `bin` 폴더를 `PATH` 앞에 붙이므로[3][5], 그 폴더에 시스템 명령과 이름이 같은 파일이 있으면 그 파일이 먼저 실행됩니다. 시작 파일에 변화가 없어도 이 폴더는 따로 봐야 합니다.
- **명령 기록 설정.** 시작 파일에서 `HISTFILE` 이나 `HISTSIZE` 를 바꾸면 명령 기록 자체가 달라집니다. 수집 도구가 설정 파일에서 `HISTFILE=` 줄을 찾아 경로를 따라가는 것도 그래서입니다[7]. 영향은 [셸 명령 기록](../execution/shell-history/index.md) 쪽을 봅니다.
- **불러온 파일이 또 다른 파일을 부른다.** 시작 파일에 `. /경로/파일` 이나 `source` 한 줄만 있고 실제 명령은 다른 곳에 있을 수 있으므로, 불러오는 줄은 끝까지 따라갑니다.
- **라이브 환경 변수.** `/proc/PID/environ` 은 프로그램이 `execve` 로 시작할 때의 초기 환경이고, 그 뒤에 바꾼 값은 반영하지 않습니다[10][13]. 그래서 셸 프로세스 자신의 `environ` 에는 시작 파일이 넣은 값이 보이지 않고, 시작 파일이 `export` 한 값은 그 셸이 뒤에 띄운 자식 프로세스의 `environ` 에서 보일 수 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 사용자 `~/.bashrc` 맨 앞에 한 줄이 끼어든 경우를 가정해 만든 예시입니다. Ubuntu skel `~/.bashrc` 는 `# ~/.bashrc: executed by bash(1) for non-login shells.` 라는 주석으로 시작하므로[3], 오프셋 0 이 이 주석이 아니면 원본 앞에 무언가가 들어간 것입니다.

```
00000000  65 78 70 6f 72 74 20 48 49 53 54 46 49 4c 45 3d  |export HISTFILE=|
00000010  2f 64 65 76 2f 6e 75 6c 6c 0a 23 20 7e 2f 2e 62  |/dev/null.# ~/.b|
00000020  61 73 68 72 63 3a 20 65 78 65 63 75 74 65 64 20  |ashrc: executed |
```

`0a` (줄바꿈) 가 0x19 에 있고, 원래 첫 줄의 `#` (`23`) 은 0x1a 에서 시작합니다. 끼어든 줄이 대화형 검사(`case $- in`)보다 앞에 있으므로 비대화형 셸에서도 실행됩니다. 이 예시 줄은 명령 기록을 `/dev/null` 로 보내므로 해당 계정의 `.bash_history` 가 비어 있거나 멈춘 까닭을 함께 설명할 수 있습니다. 긴 공백 뒤로 밀린 명령이나 화면에 드러나지 않는 제어 문자도 이렇게 바이트로 보면 드러납니다.

### 공개 도구로 한 번

1. UAC 로 라이브 수집을 하면 `files/shell/` 정의가 사용자별 시작 파일과 `/etc/profile.d/*` 를 모으고, `HISTFILE=` 값을 뽑아 그 경로의 파일까지 모으며[7], `live_response/system/env.txt` 에 `env` 출력을 남깁니다[8]. RHEL 이면 `~/.bashrc.d/` 를 손으로 더합니다.
2. 이미지에서는 모든 홈 폴더와 `/root`, `/etc/skel`, `/etc/profile.d` 의 파일 목록을 mtime·ctime·소유자와 함께 뽑고, 사용자 파일을 `/etc/skel` 사본과 `diff` 로 비교합니다. skel 사본 자체가 바뀌었을 수 있으므로 `/etc/skel` 과 `/etc/profile`, `/etc/bash.bashrc`, `/etc/bashrc` 는 [패키지 파일 변조 확인](../packages/package-verify.md) 방법으로 패키지 기준값과 맞춰 봅니다.
3. 불변 속성 (immutable) 을 걸어 지우지 못하게 한 경우는 Velociraptor `Linux.Forensics.ImmutableFiles` 로 찾습니다. ext4 플래그에서 `IMMUTABLE` 을 찾는 아티팩트이고 기본 범위는 `/home/*` 이므로[11], `/etc/profile.d` 와 `/root` 로 범위를 넓혀 씁니다. 속성 자체는 [권한·확장 속성](../../01-foundations/filesystem/permissions-xattr.md) 쪽을 봅니다.

## 교차 검증

| 함께 볼 것 | 맞춰 보는 내용 |
|---|---|
| [로그인 기록](../logins/wtmp-btmp-lastlog.md), [인증 로그](../logins/auth-log.md), [SSH](../logins/ssh/index.md) | 시작 파일을 바꾼 뒤 그 계정으로 셸이 실제로 열렸는지, 원격 비대화형 명령이 있었는지 |
| [셸 명령 기록](../execution/shell-history/index.md) | 파일을 고친 명령(`echo ... >>`, 편집기)이 남았는지, 바뀐 뒤 기록이 멈췄는지 |
| [dpkg·apt 기록](../packages/dpkg-apt.md), [rpm·dnf·yum 기록](../packages/rpm-dnf.md) | 파일의 mtime 이 패키지 설치·업그레이드 시각과 맞는지 |
| [sudo·su 사용 기록](../logins/sudo-su.md) | 다른 사용자의 파일이나 `/etc` 아래 파일을 root 권한으로 고친 때 |
| [메모리 분석](../../03-techniques/analysis/memory-analysis.md) | 실행 중인 프로세스의 환경 변수에 시작 파일이 넣은 값이 있는지 |
| [타임라인 만들기](../../03-techniques/analysis/timeline.md) | 위 기록과 시작 파일 시각을 한 줄로 세우기 |

같은 갈래에서는 [systemd 서비스와 타이머](systemd-units.md), [cron·anacron·at](cron-at.md), [공유 라이브러리 가로채기](ld-preload.md), [데스크톱 자동 실행](xdg-autostart.md) 을 함께 보고, 전체 흐름은 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md) 쪽을 따릅니다.

WSL 에서도 같은 파일이 쓰입니다. DFRWS 2020 USA 발표의 실험에서는 Windows 레지스트리 `HKEY_CURRENT_USER\Environment` 에 `BASH_ENV` 값을 `/etc/bash.bashrc` 로 넣고 `/etc/bash.bashrc` 를 고친 뒤, `/etc/bash.bashrc`, `~/.bash_history`, `~/.sh_history` 의 MAC 시각과 내용, 아이노드 타임라인, Windows 쪽 실행 흔적을 함께 따라갔습니다[12].

## 실습

공개 Linux 검체(NIST CFReDS 등)나 직접 만든 가상 머신 이미지로 풀어 봅니다.

1. 계정마다 로그인 셸은 무엇이고, 그 셸이 로그인할 때 실제로 읽는 사용자 파일은 어느 것인가? `~/.bash_profile` 과 `~/.profile` 이 둘 다 있는 계정이 있는가?
2. 사용자 `~/.bashrc` 를 `/etc/skel/.bashrc` 와 비교했을 때 다른 줄은 무엇이고, 그 줄은 대화형 검사 앞에 있는가 뒤에 있는가?
3. `/etc/profile.d/` 에서 어느 패키지에도 속하지 않는 파일은 무엇이고, 그 파일의 mtime·ctime 은 언제인가?
4. 시작 파일 가운데 `HISTFILE`, `HISTSIZE`, `PATH` 를 바꾸는 줄이 있는가, 있다면 그 뒤로 명령 기록 파일의 mtime 은 어떻게 바뀌었는가?
5. 시작 파일의 mtime 전후로 그 계정이나 root 로 로그인한 기록이 있는가?

## 참고 문헌

1. GNU Bash 5.3, doc/bash.1 (INVOCATION). https://github.com/tianon/mirror-bash/blob/master/doc/bash.1
2. Debian bash 패키지, debian/patches deb-bash-config.diff·man-bashrc.diff. https://salsa.debian.org/debian/bash/-/tree/debian/master/debian
3. Ubuntu 24.04 bash 5.2.21-2ubuntu4 소스 패키지, debian/skel.bashrc·skel.profile·etc.bash.bashrc. https://git.launchpad.net/ubuntu/+source/bash/tree/debian?h=ubuntu/noble
4. Ubuntu 24.04 base-files 13ubuntu10, share/profile. https://git.launchpad.net/ubuntu/+source/base-files/tree/share/profile?h=ubuntu/noble
5. CentOS Stream 9 bash 패키지, dot-bashrc·dot-bash_profile·dot-bash_logout. https://gitlab.com/redhat/centos-stream/rpms/bash/-/tree/c9s
6. setup 2.13.7 (CentOS Stream 9 setup.spec 의 원본), profile·bashrc. https://releases.pagure.org/setup/setup-2.13.7.tar.bz2 , https://gitlab.com/redhat/centos-stream/rpms/setup/-/blob/c9s/setup.spec
7. UAC, artifacts/files/shell/ (bash.yaml·common.yaml·zsh.yaml 등). https://github.com/tclahr/uac/tree/main/artifacts/files/shell
8. UAC, artifacts/files/system/etc.yaml, artifacts/live_response/system/env.yaml. https://github.com/tclahr/uac/tree/main/artifacts
9. Linux-PAM, modules/pam_env/pam_env.8.xml. https://github.com/linux-pam/linux-pam
10. Linux man-pages, man5/proc.5 (`/proc/[pid]/environ`). https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
11. Velociraptor, artifacts/definitions/Linux/Forensics/ImmutableFiles.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Forensics/ImmutableFiles.yaml
12. Asif Matadar, "Investigating Windows Subsystem for Linux (WSL) Endpoints", DFRWS 2020 USA 발표 자료. https://dfrws.org/presentation/investigating-windows-subsystem-for-linux-wsl-endpoints/
13. fox-it dissect.target, dissect/target/plugins/os/unix/linux/environ.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/environ.py
14. Linux man-pages, man7/inode.7. https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
