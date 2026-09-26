---
title: "SSH"
parent: "아티팩트 · 로그인과 계정"
nav_order: 350
has_children: true
has_toc: false
---

# SSH (SSH)

SSH 흔적은 서버 쪽(누가 이 기계로 들어왔나)과 클라이언트 쪽(이 계정이 어디로 나갔나)에 따로 남고, 둘을 맞대어 보면 사람이 기계 사이를 옮겨 다닌 경로가 드러납니다.

## 왜 중요한가

Linux 서버에 원격으로 들어오는 가장 흔한 길이 SSH 이고, 침입 조사에서 "처음 어디로 들어왔나" 와 "그다음 어디로 옮겨 갔나" 를 가르는 기록이 대부분 여기에 있습니다. 서버 쪽에는 sshd 가 남기는 인증 줄, 로그인 기록(wtmp·lastlog), 공개 키를 등록해 두는 authorized_keys, 서버 설정인 sshd_config 가 있습니다. 클라이언트 쪽에는 접속한 적 있는 서버의 호스트 키를 모아 두는 known_hosts 와 접속 대상을 적어 두는 `~/.ssh/config` 가 있습니다.

서버 쪽 기록은 "이 기계로 들어온 것" 을, 클라이언트 쪽 기록은 "이 기계에서 나간 것" 을 알려 줍니다. 한 기계의 `.bash_history` 와 다른 기계의 auth.log 를 맞대어 공격자가 SSH 키로 옆 기계에 들어간 것을 밝힌 사례가 있습니다[9]. 한쪽 기계만 보면 이런 이동이 끊겨 보이므로, 가능하면 양쪽 기계를 함께 수집합니다.

authorized_keys 에 공개 키 한 줄을 넣으면 암호를 몰라도 그 계정으로 다시 들어올 수 있어서, 이 파일은 로그인 흔적이면서 지속성(Persistence) 흔적이기도 합니다. 로그인할 때 sshd 가 읽거나 실행하는 `~/.ssh/environment`, `~/.ssh/rc`, `/etc/ssh/sshrc` 도 같은 이유로 봅니다[1].

## 한눈에 보기

| 아티팩트 | 위치 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| sshd 인증 줄 | Ubuntu `/var/log/auth.log`, RHEL `/var/log/secure`, 저널 | 누가 어디서 어떤 방식·어떤 키로 들어왔나, 어떤 시도가 실패했나 | [sshd 로그](sshd-logs.md) |
| authorized_keys | `~/.ssh/authorized_keys`, `~/.ssh/authorized_keys2`, 또는 `AuthorizedKeysFile` 이 가리키는 경로 | 어떤 공개 키로 이 계정에 들어올 수 있나 | [authorized_keys](authorized-keys.md) |
| known_hosts, 클라이언트 설정 | `~/.ssh/known_hosts`, `~/.ssh/known_hosts2`, `/etc/ssh/ssh_known_hosts`, `~/.ssh/config`, `/etc/ssh/ssh_config` | 이 계정의 ssh 클라이언트가 어느 서버에 접속한 적이 있나 | [known_hosts 와 클라이언트 설정](known-hosts.md) |
| sshd_config | `/etc/ssh/sshd_config`, `/etc/ssh/sshd_config.d/*.conf` | 서버가 어떤 인증을 허용했고 무엇을 어디에 기록했어야 하나 | [sshd 설정](sshd-config.md) |
| 로그인 때 읽거나 실행하는 파일 | `~/.ssh/environment`, `~/.ssh/rc`, `/etc/ssh/sshrc` | 로그인마다 실행되는 명령, 바뀐 환경 변수 | [sshd 설정](sshd-config.md) |
| 호스트 키 | `/etc/ssh/ssh_host_ecdsa_key`, `ssh_host_ed25519_key`, `ssh_host_rsa_key` 와 각각의 `.pub` | 이 서버의 신원. 다른 기계의 known_hosts 에 있는 키와 맞대어 접속 대상을 밝힌다 | 이 쪽 |
| 로그인 기록 | `/var/log/wtmp`, `/var/log/btmp`, `/var/log/lastlog` | pty 를 받은 로그인, 암호·키보드 대화식 인증 실패와 없는 사용자 이름으로 한 시도 | [로그인 기록](../wtmp-btmp-lastlog.md) |

위치는 OpenSSH 매뉴얼의 기본값입니다[1][2][3]. `AuthorizedKeysFile`, `UserKnownHostsFile` 같은 설정 키로 경로를 바꿀 수 있으므로, 검체에서는 설정 파일을 먼저 읽고 실제 경로를 정합니다. 수집 도구의 기본 경로 목록도 대체로 이 기본값을 따르지만, ForensicArtifacts 는 전역 known_hosts 를 매뉴얼의 `/etc/ssh/ssh_known_hosts` 가 아닌 `/etc/ssh/known_hosts` 로 적어 두었습니다[3][7][8].

호스트 키 공개 파일(`/etc/ssh/ssh_host_*_key.pub`)은 다른 기계의 접속 기록을 푸는 데 씁니다. 여러 기계에서 모은 호스트 공개 키를 한 기계의 known_hosts 에 있는 키와 맞추면, 호스트 이름이 해시로 가려진 줄도 어느 서버를 가리키는지 알 수 있고, Velociraptor 는 이렇게 맞추는 질의를 함께 제공합니다[10].

### 배포판별 차이

| 항목 | Ubuntu 24.04 LTS | RHEL 9 |
|---|---|---|
| OpenSSH 판 | 9.6p1[4] | 처음 판은 8.7p1, CentOS Stream 9 는 2025년 9월에 9.9p1 로 올렸다[5]. 검체에서 `rpm -q openssh-server` 로 확인한다 |
| 서비스 단위 | `ssh.service`, `ssh.socket`. 소켓 활성화가 기본이다[4] | `sshd.service`, `sshd.socket`, `sshd@.service`[5] |
| 인증 줄을 남기는 프로세스 이름 | `sshd` | 9.9p1 이면 `sshd-session`(`/usr/libexec/openssh/sshd-session`)[5] |
| sshd 로그 facility | 기본값 AUTH → `/var/log/auth.log` | `/etc/ssh/sshd_config.d/50-redhat.conf` 의 `SyslogFacility AUTHPRIV` → `/var/log/secure`[5] |
| 추가 설정 파일 | `/etc/ssh/sshd_config.d/*.conf` 를 본 파일 맨 앞에서 읽는다[4] | 같고, `50-redhat.conf` 를 함께 설치한다[5] |
| known_hosts 해시 | `/etc/ssh/ssh_config` 에 `HashKnownHosts yes`[4] | 설정하지 않아 기본값 no[5] |

OpenSSH 9.8 부터 서버가 연결을 받는 `sshd` 와 세션마다 따로 뜨는 `sshd-session` 으로 나뉘었고, 인증 줄은 `sshd-session` 이 남깁니다[6]. 로그를 프로그램 이름 `sshd` 로만 거르면 새 판의 인증 줄을 놓치므로 두 이름을 모두 씁니다. Ubuntu 는 소켓 활성화라 `ssh.socket` 이 22번 포트를 열어 두고, 설정 파일에 기본값이 아닌 `Port`·`ListenAddress` 가 있으면 생성기(sshd-socket-generator)가 그 값을 소켓 설정에 옮깁니다[4]. 그래서 연결이 올 때 서비스가 뜰 수 있고, 서비스 시작 시각을 부팅 시각으로 읽으면 안 됩니다.

## 읽는 순서

1. [sshd 로그 (sshd Logs)](sshd-logs.md) — 인증 성공·실패 줄의 모양과 기록 등급, 기본 설정에서 남지 않는 줄을 다룹니다. 들어온 기록은 여기서 시작합니다.
2. [authorized_keys (authorized_keys)](authorized-keys.md) — 등록된 공개 키, 키 앞에 붙는 옵션, 로그에 찍힌 키 지문과 파일의 줄을 맞추는 방법을 다룹니다.
3. [known_hosts 와 클라이언트 설정 (known_hosts·ssh_config)](known-hosts.md) — 이 계정이 접속한 서버, 해시된 호스트 이름을 되살리는 방법, `known_hosts.old` 를 다룹니다.
4. [sshd 설정 (sshd_config)](sshd-config.md) — 먼저 나온 값이 이기는 읽기 규칙과 두 배포판의 기본 설정, 로그인 때 실행되는 파일을 다룹니다. 앞의 세 쪽을 해석할 때 기준이 됩니다.

해석은 설정에 달려 있어서, 실제 조사에서는 sshd_config 를 먼저 읽어 로그 등급(`LogLevel`)과 키 파일 경로(`AuthorizedKeysFile`)를 정한 뒤 로그와 키 파일을 보면 됩니다.

## 함께 볼 페이지

- [로그인 기록 (wtmp·btmp·lastlog)](../wtmp-btmp-lastlog.md) — sshd 는 tty 를 받은 로그인만 로그인 기록에 씁니다[1]. `ssh 호스트 명령`, scp, sftp 처럼 pty 를 요청하지 않는 세션이 왜 wtmp 에 없는지를 다룹니다.
- [인증 로그 (auth.log·secure)](../auth-log.md) — sshd 줄이 어느 파일로 가는지, 순환된 파일 이름과 시각 형식을 다룹니다.
- [셸 명령 기록 (Shell History)](../../execution/shell-history/index.md) — 이 기계에서 나간 `ssh`·`scp` 명령을 봅니다.
- [PAM 모듈 변조 (PAM Backdoor)](../../persistence/pam-backdoor.md) — sshd 가 `UsePAM yes` 로 PAM 을 거칠 때 남는 변조 흔적입니다.
- [셸 시작 파일 (.bashrc·profile)](../../persistence/shell-startup.md) — `~/.ssh/rc` 와 함께 로그인 때 실행되는 다른 파일입니다.
- [인증 모듈 (PAM)](../../../01-foundations/users-auth/pam.md) — `pam_unix(sshd:session)` 줄이 어디서 오는지 설명합니다.
- [SSH 로 들어왔나 (SSH Intrusion)](../../../04-scenarios/intrusion/ssh-intrusion.md) — 이 갈래의 아티팩트를 한 사건에 엮는 순서입니다.

## 참고 문헌

1. OpenSSH, sshd(8) 매뉴얼 (FILES, LOGIN PROCESS 절). https://github.com/openssh/openssh-portable/blob/master/sshd.8
2. OpenSSH, sshd_config(5) 매뉴얼 (AuthorizedKeysFile). https://github.com/openssh/openssh-portable/blob/master/sshd_config.5
3. OpenSSH, ssh_config(5) 매뉴얼 (UserKnownHostsFile, GlobalKnownHostsFile). https://github.com/openssh/openssh-portable/blob/master/ssh_config.5
4. Ubuntu openssh 패키지 noble-updates (1:9.6p1-3ubuntu13.19): debian/changelog, debian/README.Debian, debian/patches/debian-config.patch. https://git.launchpad.net/ubuntu/+source/openssh/tree/debian?h=ubuntu/noble-updates
5. CentOS Stream 9 openssh 패키지 (c9s): openssh.spec, openssh-7.7p1-redhat.patch. https://gitlab.com/redhat/centos-stream/rpms/openssh/-/tree/c9s
6. plaso, syslog 텍스트 파서 (sshd·sshd-session 처리). https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/syslog.py
7. ForensicArtifacts, linux.yaml (SSHAuthorizedKeysFiles, SSHHostPubKeys, SSHKnownHostsFiles). https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
8. UAC, files/ssh 수집 정의. https://github.com/tclahr/uac/tree/main/artifacts/files/ssh
9. Ali Hadi, Mariam Khader, Thomas Claflin, "Learning Linux Forensic Analysis and Why it Matters", DFRWS 발표 자료. https://dfrws.org/presentation/learning-linux-forensic-analysis-and-why-it-matters/
10. Velociraptor, Linux.Ssh.KnownHosts 아티팩트 정의 ("Resolve Known Hosts" 질의). https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Ssh/KnownHosts.yaml
