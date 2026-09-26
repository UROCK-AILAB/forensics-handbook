---
title: "known_hosts 와 클라이언트 설정"
parent: "SSH"
grand_parent: "아티팩트 · 로그인과 계정"
nav_order: 380
---

# known_hosts 와 클라이언트 설정 (known_hosts·ssh_config)

ssh 클라이언트는 처음 보는 서버에 접속할 때 그 서버의 호스트 키를 `~/.ssh/known_hosts` 에 한 줄로 덧붙이므로, 이 파일과 클라이언트 설정 `~/.ssh/config` 는 "이 계정이 어느 서버로 나갔나" 를 알려 줍니다.

## 무엇을 기록하나 · 왜 생기나

ssh 는 접속할 때마다 서버가 내민 호스트 키 (host key) 를 known_hosts 에 있는 키와 맞춰 봅니다. 사용자 파일은 저절로 관리되고, 모르는 호스트에 접속하면 그 키를 사용자 파일에 더합니다[1]. 새 줄은 사용자 known_hosts 목록의 첫 파일에 덧붙이고, 파일은 덧붙이기 모드로 엽니다[4][5].

키를 더할지는 `StrictHostKeyChecking` 이 정합니다[2]. 기본값 `ask` 는 사용자가 확인한 뒤에만 더하고, `accept-new` 와 `no` 는 묻지 않고 더하며, `yes` 는 저절로 더하지 않습니다[2]. 그래서 줄이 있다는 것은 사람이 확인 질문에 답했거나, 묻지 않도록 설정돼 있었거나, 누가 손으로 넣었다는 뜻입니다.

한 번 접속에 줄이 여러 개 생길 수도 있습니다. `UpdateHostKeys` 는 사용자가 `UserKnownHostsFile` 을 바꾸지 않았고 `VerifyHostKeyDNS` 를 켜지 않았으면 기본으로 켜지고, 인증이 끝난 뒤 서버가 알려 주는 다른 호스트 키까지 사용자 파일에 더합니다[2]. `CheckHostIP` 는 기본값이 no 이고, yes 면 서버의 IP 주소도 함께 적습니다[2].

클라이언트 설정 파일은 접속 대상을 이름으로 적어 두는 곳입니다. ssh 는 명령행 옵션, `~/.ssh/config`, `/etc/ssh/ssh_config` 순으로 설정을 읽고, 같은 설정 키는 먼저 읽은 값을 씁니다[2]. 흔적으로 볼 만한 설정 키는 아래와 같습니다[2].

| 설정 키 | 알려 주는 것 |
|---|---|
| `Host`, `Match` | 이 뒤의 설정을 적용할 대상 이름(별칭일 수 있음) |
| `HostName` | 실제로 접속하는 호스트 이름 또는 주소 |
| `User`, `Port` | 원격 계정 이름과 포트 |
| `IdentityFile` | 인증에 쓸 개인 키 파일. 기본값은 `~/.ssh/id_rsa`, `id_ecdsa`, `id_ecdsa_sk`, `id_ed25519`, `id_ed25519_sk` 이고, 최신 OpenSSH 는 `id_mldsa44_ed25519` 도 봄 |
| `ProxyJump`, `ProxyCommand` | 중간에 거쳐 가는 호스트나 명령 |
| `ControlPath` | 연결 공유 (connection sharing) 에 쓰는 소켓 경로 |
| `LocalForward`, `RemoteForward`, `DynamicForward` | 포트 전달 설정 |
| `UserKnownHostsFile`, `GlobalKnownHostsFile`, `HashKnownHosts` | known_hosts 위치와 해시 여부 |
| `Include` | 함께 읽을 다른 설정 파일 |

## 위치와 버전별 차이

| 파일 | 기본 경로 | 누가 쓰나 |
|---|---|---|
| 사용자 known_hosts | `~/.ssh/known_hosts`, `~/.ssh/known_hosts2` (`UserKnownHostsFile`) | ssh 가 저절로 더함 |
| 전역 known_hosts | `/etc/ssh/ssh_known_hosts`, `/etc/ssh/ssh_known_hosts2` (`GlobalKnownHostsFile`) | 관리자가 만듦(선택) |
| 사용자 설정 | `~/.ssh/config` | 사용자 |
| 시스템 설정 | `/etc/ssh/ssh_config`, `/etc/ssh/ssh_config.d/*.conf` | 패키지·관리자 |
| 고치기 전 사본 | `~/.ssh/known_hosts.old` | ssh-keygen `-H`·`-R`, `UpdateHostKeys` |

기본 경로는 매뉴얼 값입니다[1][2]. `UserKnownHostsFile` 은 공백으로 나눠 여러 파일을 적을 수 있고 토큰도 쓸 수 있어서[2], 배포되는 `ssh_config` 에는 `UserKnownHostsFile ~/.ssh/known_hosts.d/%k` 처럼 호스트마다 파일을 나누는 주석 예시가 있습니다[9]. `%k` 는 `HostKeyAlias` 가 있으면 그 값이고, 없으면 명령행에 준 원래 호스트 이름입니다[2]. 검체에서는 설정 파일을 먼저 읽어 실제 경로를 정합니다. `Include` 의 상대 경로는 사용자 설정이면 `~/.ssh`, 시스템 설정이면 `/etc/ssh` 기준입니다[2]. `~/.ssh/config` 는 다른 사람이 쓸 수 없는 권한이어야 합니다[3].

두 기준 배포판의 기본 설정은 아래처럼 다릅니다.

| 항목 | Ubuntu 24.04 | RHEL 9 |
|---|---|---|
| `HashKnownHosts` | `/etc/ssh/ssh_config` 의 `Host *` 아래 `HashKnownHosts yes`[10] | 설정하지 않아 기본값 no[2][11] |
| `ssh_config.d` 읽는 자리 | 파일 맨 앞 `Include /etc/ssh/ssh_config.d/*.conf`[10] | 파일 끝 `Include /etc/ssh/ssh_config.d/*.conf`[11] |
| 배포판이 더한 값 | `SendEnv LANG LC_*`, `GSSAPIAuthentication yes`, 코드 기본값 `ForwardX11Trusted yes`[10] | `/etc/ssh/ssh_config.d/50-redhat.conf` 의 `Match final all` 블록에 crypto-policies 설정 include, `GSSAPIAuthentication yes`, `ForwardX11Trusted yes`[11] |

기본 설정만 놓고 보면 Ubuntu 사용자의 known_hosts 에는 해시로 가려진 이름이 쌓이고, RHEL 사용자의 known_hosts 에는 호스트 이름이 평문으로 남습니다. `HashKnownHosts` 는 새로 더하는 줄에만 적용되고 이미 있는 줄은 바꾸지 않으므로[2], 한 파일 안에 평문 줄과 해시 줄이 섞여 있으면 중간에 설정이 바뀌었을 가능성이 있습니다.

## 구조

한 줄이 키 하나이고, 필드는 공백으로 나눈 marker(선택), hostnames, keytype, base64 로 적은 키, comment 입니다[1]. `#` 로 시작하는 줄과 빈 줄은 주석입니다[1].

| 필드 | 내용 |
|---|---|
| marker | `@cert-authority`(인증 기관 키) 또는 `@revoked`(폐기된 키). 없으면 일반 호스트 키 |
| hostnames | 쉼표로 나눈 패턴. `*`·`?` 와일드카드, `!` 부정. 기본 포트가 아니면 `[호스트]:포트` |
| keytype, 키 | 서버 호스트 공개 키 파일(`/etc/ssh/ssh_host_*_key.pub`)에서 그대로 옮긴 값 |
| comment | 줄 끝까지. ssh 는 쓰지 않음 |

키 형식과 base64 키 필드 모양은 [authorized_keys](authorized-keys.md) 와 같습니다.

ssh 가 줄을 쓸 때는 호스트 이름을 소문자로 바꾸고[4], 포트가 22 이면 이름만, 아니면 `[이름]:포트` 로 적습니다[6]. 적는 이름은 `HostKeyAlias` 가 있으면 그 값이고[5], 없으면 `~/.ssh/config` 의 `HostName` 으로 바꾼 뒤의 이름입니다[8]. 그래서 `Host` 별칭 `db` 로 접속해도 known_hosts 에는 `HostName` 에 적은 실제 이름이 남습니다. `CheckHostIP yes` 이고 해시를 쓰지 않으면 `이름,주소` 한 줄로, 해시를 쓰면 이름 줄과 주소 줄을 따로 적습니다[4][5]. `ProxyCommand` 로 접속했거나, 서버가 루프백 주소이거나, 호스트 이름 자체가 주소이면 ssh 가 `CheckHostIP` 를 끄므로 주소를 따로 적지 않습니다[5].

해시한 이름은 `|1|` 로 시작하고, 뒤에 base64 로 적은 salt, `|`, base64 로 적은 HMAC-SHA1 값이 옵니다[4]. salt 는 SHA-1 출력 길이인 20바이트를 줄마다 새로 뽑고, 그 salt 를 키로 삼아 호스트 문자열의 HMAC-SHA1 을 계산합니다[4]. 해시한 이름은 한 줄에 하나만 올 수 있고 와일드카드·부정을 쓸 수 없습니다[1].

아래는 만든 예시입니다. 호스트 이름은 `example.net`, 주소는 문서용 대역이고, 키는 앞부분만 적었습니다.

```
web01.example.net ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI...
[db01.example.net]:2222,[198.51.100.20]:2222 ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAI...
|1|AQIDBAUGBwgJCgsMDQ4PEBESExQ=|pnf7YNGP4aWyz8jgTSTxhlbQ29M= ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI...
@revoked * ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB...
```

셋째 줄은 salt 를 바이트 `01`~`14` 로 정하고 `web01.example.net` 을 해시해 만든 값입니다. 실제 파일에서는 줄마다 salt 가 다릅니다.

## 증거로서 의미

### 증명하는 것

이 계정의 ssh 클라이언트가 이 이름(또는 주소)의 서버가 내민 호스트 키를 받아들인 적이 있다는 것을 보여 줍니다. 사용자 known_hosts 에 줄이 있으면 그 사용자 홈을 쓰는 계정으로 ssh·scp·sftp 를 실행해 그 서버에 연결을 시도했을 가능성이 높습니다. `~/.ssh/config` 의 `Host`·`HostName`·`User`·`IdentityFile` 은 사용자가 어느 서버에 어느 계정과 어느 키로 접속하려고 준비해 두었는지 알려 줍니다.

### 증명하지 못하는 것

호스트 키 확인은 사용자 인증보다 먼저 일어나므로 줄이 있어도 로그인에 성공했는지는 알 수 없습니다. 파일 안에 시각이 없어서 처음 접속한 때, 마지막 접속한 때, 접속한 횟수도 알 수 없습니다. 해시 줄은 후보 이름을 대입해 맞추기 전까지 어느 서버인지 모릅니다. 줄은 편집기로 넣거나 지울 수 있고, 다른 기계의 파일을 복사해 올 수도 있으므로 줄 하나만으로 이 기계에서 접속했다고 단정하지 않습니다. 설정 파일에 적힌 대상은 준비해 둔 것일 뿐 실제로 접속했다는 기록이 아닙니다.

## 시각 해석

줄 자체에는 시각이 없고, 파일 시스템 시각만 단서가 됩니다. 새 줄은 원래 파일에 덧붙이므로[4] mtime 과 ctime 은 마지막으로 줄을 더한 때로 바뀌고 inode 는 그대로입니다[12]. 줄은 파일 끝에 쌓이므로 줄 순서가 처음 접속한 순서일 가능성이 있습니다.

`ssh-keygen -H`(모든 이름을 해시)와 `-R 호스트`(그 호스트 줄 지우기)는 제자리에서 고칩니다[3]. 새 내용을 `known_hosts.XXXXXXXXXX` 임시 파일에 쓰고, 원래 파일을 `known_hosts.old` 로 하드 링크한 뒤, 임시 파일을 원래 이름으로 rename 합니다[7]. `UpdateHostKeys` 가 줄을 바꿀 때도 같은 방식으로 `.old` 를 남깁니다[4][13]. 그래서 이런 변경 뒤의 known_hosts 는 inode 가 새것이고, ext4 의 생성 시각 (crtime) 도 그때로 바뀔 가능성이 높습니다. `known_hosts.old` 는 원래 inode 라서 mtime 은 바꾸기 전 마지막으로 쓴 때이고, 링크 수가 바뀌므로 ctime 은 바꾼 때입니다[12]. 시각 값 읽는 법은 [Linux 의 시각 값](../../../01-foundations/value-decoding/time-values.md) 에서, crtime 은 [ext4](../../../01-foundations/filesystem/ext4/index.md) 에서 다룹니다. 모든 시각은 UTC 기준 epoch 값입니다[12].

## 함정과 한계

- `known_hosts.old` 가 있으면 해시하기 전의 평문 이름이나 지우기 전의 줄이 남아 있을 수 있습니다. 다만 `UpdateHostKeys` 도 `.old` 를 만들므로[4] `.old` 가 있다는 것만으로 사람이 ssh-keygen 을 썼다고 보지 않습니다.
- 수집 도구마다 경로 목록이 다릅니다. ForensicArtifacts 의 `SSHKnownHostsFiles` 는 `~/.ssh/known_hosts` 와 `/etc/ssh/known_hosts` 만 적어[14] `known_hosts2`, `known_hosts.old` 를 빠뜨리고, 전역 파일 이름이 매뉴얼의 `/etc/ssh/ssh_known_hosts`[1] 와 다릅니다. UAC 는 사용자 홈의 `.ssh/known_hosts*` 를 모읍니다[15]. dissect.target 은 사용자 홈의 `.ssh/known_hosts*` 와 `/etc/ssh/ssh_known_hosts` 를 읽습니다[16]. 이 세 도구와 Velociraptor 모두 설정 파일의 `UserKnownHostsFile` 을 읽지 않으므로, 다른 경로로 바꾼 설정은 설정 파일을 보고 따로 찾아야 합니다.
- Velociraptor 의 `Linux.Ssh.KnownHosts` 는 줄을 공백으로 나눠 앞 세 칸을 Hostname, Type, PublicKey 로 읽습니다[17]. 줄 앞에 `@revoked` 같은 marker 가 있으면 칸이 하나씩 밀리고, 주석 거르기 조건이 `#` 로 시작하는 줄과 맞지 않아 주석 줄이 결과에 섞일 수 있습니다[17]. dissect.target 은 marker 를 따로 떼고 쉼표로 나눈 이름마다 한 행을 만듭니다[16].
- 해시 후보를 만들 때는 ssh 가 적는 모양 그대로 맞춰야 합니다. 소문자로 바꾸고, 기본 포트가 아니면 `[이름]:포트` 로 감싸고, 별칭이 아니라 `HostName` 값을 씁니다[4][6][8].
- 전역 파일이나 `@cert-authority` 줄로 확인한 서버는 사용자 파일에 줄이 새로 생기지 않을 수 있습니다[1][2]. 사용자 파일에 없다는 것만으로 접속하지 않았다고 말할 수 없습니다.

## 직접 분석해 보기

### 헥스로 한 번

위 만든 예시의 해시 줄 앞부분을 헥스로 보면 아래와 같습니다(명세로 만든 예시).

```
00000000: 7c31 7c41 5149 4442 4155 4742 7767 4a43  |1|AQIDBAUGBwgJC
00000010: 6773 4d44 5134 5045 4245 5345 7851 3d7c  gsMDQ4PEBESExQ=|
```

`7c 31 7c` 가 `|1|` 이고, 다음 `7c` 까지가 salt 의 base64 입니다. 이를 풀면 20바이트 `01 02 … 14` 가 나옵니다. 후보 이름 `web01.example.net` 을 이 salt 로 HMAC-SHA1 한 값을 base64 로 적어 둘째 칸 `pnf7YNGP4aWyz8jgTSTxhlbQ29M=` 와 같으면 이 줄의 호스트가 그 이름입니다[4]. 후보를 하나씩 대입하는 계산은 짧은 스크립트로 충분합니다.

```
import base64, hashlib, hmac
salt = base64.b64decode("AQIDBAUGBwgJCgsMDQ4PEBESExQ=")
mac = hmac.new(salt, b"web01.example.net", hashlib.sha1).digest()
print(base64.b64encode(mac).decode())   # pnf7YNGP4aWyz8jgTSTxhlbQ29M=
```

후보 이름은 `~/.ssh/config` 의 `HostName`, 셸 기록의 `ssh`·`scp` 명령, `/etc/hosts` 에서 모읍니다. 이름 해석 파일은 [이름 해석](../../network/name-resolution.md) 에서 다룹니다.

### 공개 도구로 한 번

- `ssh-keygen -F 호스트 -f 파일` 은 해시된 줄까지 찾아 보여 주고[3], 분석용 사본에 쓰면 원본을 건드리지 않습니다. `ssh-keygen -l -f 파일` 은 줄마다 키 지문을 보여 줍니다[3]. `-H`·`-R` 은 파일을 고치므로 증거 원본에 쓰지 않습니다.
- dissect.target 의 `openssh.known_hosts` 는 marker, 이름, 키 형식, 지문(MD5·SHA-1·SHA-256), 파일 경로, 사용자를 행으로 내놓습니다[16].
- Velociraptor 의 `Linux.Ssh.KnownHosts` 는 사용자마다 known_hosts 를 읽고, `HostPublicKeys` 소스로 각 기계의 `/etc/ssh/ssh_host*.pub` 를 모읍니다[17]. 여러 기계에서 함께 수집하면 "Resolve Known Hosts" 질의가 공개 키를 맞춰 해시 줄의 호스트를 밝힙니다[17].

## 교차 검증

| 함께 볼 것 | 맞춰 보는 것 |
|---|---|
| [셸 명령 기록](../../execution/shell-history/index.md) | 이 계정이 친 `ssh`·`scp`·`sftp` 명령의 대상과 순서 |
| 상대 서버의 [sshd 로그](sshd-logs.md) | 이 기계 주소에서 들어온 인증 성공·실패 줄과 시각 |
| 상대 서버의 호스트 키 `/etc/ssh/ssh_host_*_key.pub` | known_hosts 의 키와 같은지(해시 줄 풀기) |
| [authorized_keys](authorized-keys.md) | 이 계정의 `IdentityFile` 공개 키가 상대 서버에 등록돼 있는지 |
| `~/.ssh/config` 와 `known_hosts.old` | 설정의 `HostName` 목록, 해시 전·삭제 전 줄 |

양쪽 기계의 기록을 시간순으로 합치는 방법은 [타임라인 만들기](../../../03-techniques/analysis/timeline.md) 에서, 한 사건으로 엮는 순서는 [SSH 로 들어왔나](../../../04-scenarios/intrusion/ssh-intrusion.md) 에서 다룹니다. 파일을 지우거나 줄을 지운 흔적은 [흔적을 지웠나](../../../04-scenarios/insider/anti-forensics.md) 와 [지운 파일 되살리기](../../../03-techniques/analysis/file-recovery.md) 를 봅니다.

## 실습

공개 검체(NIST CFReDS 의 Linux 디스크 이미지 등)로 아래 질문을 풀어 봅니다.

1. 모든 사용자 홈과 `/root` 에서 `.ssh/known_hosts*`, `.ssh/config` 를 찾고, `/etc/ssh/ssh_config` 와 `ssh_config.d` 에서 `UserKnownHostsFile`·`HashKnownHosts` 를 바꾼 줄이 있는지 확인합니다.
2. 줄마다 평문인지 해시인지 가르고, 한 파일 안에 둘이 섞여 있는지 봅니다.
3. 해시 줄은 셸 기록과 `~/.ssh/config` 에서 모은 후보 이름으로 풀어 봅니다.
4. known_hosts 와 `known_hosts.old` 의 inode, mtime, ctime 을 비교해 마지막으로 파일을 고친 때를 가늠합니다.

## 참고 문헌

1. OpenSSH, sshd(8) 매뉴얼 (SSH_KNOWN_HOSTS FILE FORMAT, FILES). https://github.com/openssh/openssh-portable/blob/master/sshd.8
2. OpenSSH, ssh_config(5) 매뉴얼 (DESCRIPTION, StrictHostKeyChecking, UpdateHostKeys, CheckHostIP, HashKnownHosts, UserKnownHostsFile, GlobalKnownHostsFile, IdentityFile, Include, TOKENS). https://github.com/openssh/openssh-portable/blob/master/ssh_config.5
3. OpenSSH, ssh-keygen(1) 매뉴얼 (`-F`, `-H`, `-R`, `-l`), ssh(1) 매뉴얼 (FILES). https://github.com/openssh/openssh-portable/blob/master/ssh-keygen.1 , https://github.com/openssh/openssh-portable/blob/master/ssh.1
4. OpenSSH, hostfile.c (`host_hash`, `format_host_entry`, `add_host_to_hostfile`, `hostfile_replace_entries`). https://github.com/openssh/openssh-portable/blob/master/hostfile.c
5. OpenSSH, sshconnect.c (`get_hostfile_hostname_ipaddr`, 호스트 키 추가). https://github.com/openssh/openssh-portable/blob/master/sshconnect.c
6. OpenSSH, misc.c (`put_host_port`). https://github.com/openssh/openssh-portable/blob/master/misc.c
7. OpenSSH, ssh-keygen.c (known_hosts 제자리 고치기). https://github.com/openssh/openssh-portable/blob/master/ssh-keygen.c
8. OpenSSH, ssh.c (`HostName` 치환). https://github.com/openssh/openssh-portable/blob/master/ssh.c
9. OpenSSH, 배포 기본 ssh_config. https://github.com/openssh/openssh-portable/blob/master/ssh_config
10. Ubuntu openssh 패키지 noble-updates (1:9.6p1-3ubuntu13.19), debian/patches/debian-config.patch. https://git.launchpad.net/ubuntu/+source/openssh/tree/debian?h=ubuntu/noble-updates
11. CentOS Stream 9 openssh 패키지 (c9s), openssh-7.7p1-redhat.patch, openssh.spec. https://gitlab.com/redhat/centos-stream/rpms/openssh/-/tree/c9s
12. Linux man-pages, inode(7) (mtime, ctime). https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
13. OpenSSH, clientloop.c (`update_known_hosts`). https://github.com/openssh/openssh-portable/blob/master/clientloop.c
14. ForensicArtifacts, artifacts/data/linux.yaml (SSHKnownHostsFiles). https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
15. UAC, artifacts/files/ssh/known_hosts.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/ssh/known_hosts.yaml
16. dissect.target, dissect/target/plugins/apps/ssh/openssh.py (`known_hosts`), ssh.py (`KnownHostRecord`, `calculate_fingerprints`). https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/ssh/openssh.py , https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/ssh/ssh.py
17. Velociraptor, artifacts/definitions/Linux/Ssh/KnownHosts.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Ssh/KnownHosts.yaml
