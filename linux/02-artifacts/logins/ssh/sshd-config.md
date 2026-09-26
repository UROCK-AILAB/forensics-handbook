---
title: "sshd 설정"
parent: "SSH"
grand_parent: "아티팩트 · 로그인과 계정"
nav_order: 390
---

# sshd 설정 (sshd_config)

SSH 서버(sshd)가 어떤 인증을 받아 주고, 무엇을 어느 분야로 기록하고, 로그인 때 무엇을 실행하는지 정하는 텍스트 설정 파일이며, 기본 위치는 `/etc/ssh/sshd_config` 와 `/etc/ssh/sshd_config.d/*.conf` 입니다.

## 무엇을 기록하나 · 왜 생기나

sshd_config 는 사건을 기록하는 파일이 아니라 다른 기록을 해석하는 기준입니다. sshd 로그에 어떤 줄이 남아야 하는지는 `LogLevel` 이, 그 줄이 어느 파일로 가는지는 `SyslogFacility` 가 정하고, 어떤 공개 키 파일을 읽는지는 `AuthorizedKeysFile` 이 정합니다[1]. 그래서 [sshd 로그](sshd-logs.md)와 [authorized_keys](authorized-keys.md)를 보기 전에 이 파일부터 읽어 두면 "왜 이 줄이 없는가", "이 키 파일이 실제로 쓰였는가" 를 판단할 수 있습니다.

침입자가 이 파일을 고쳐 root 로그인이나 암호 인증을 열어 두거나, 로그인 때마다 실행되는 파일을 쓸 수 있게 바꿀 수도 있습니다. 이런 변경은 설정 파일 자체와 파일의 시각에 흔적이 남습니다.

## 위치와 버전별 차이

sshd 는 `/etc/ssh/sshd_config` 를 읽고, 명령줄의 `-f` 로 다른 파일을 줄 수 있습니다[1]. 두 기준 배포판은 모두 본 파일의 설정 줄보다 앞에 `Include /etc/ssh/sshd_config.d/*.conf` 를 넣어 두었습니다[5][6]. 배포판 기본값과 upstream OpenSSH 코드 기본값의 차이는 다음과 같습니다.

| 키 | OpenSSH 기본값[1] | Ubuntu 24.04 LTS[5] | RHEL 9[6] |
|---|---|---|---|
| 추가 설정 폴더 | 없음 | 본 파일 맨 앞에서 `sshd_config.d/*.conf` 를 읽음 | 같음. `sshd_config.d/50-redhat.conf` 를 함께 설치 |
| `SyslogFacility` | `AUTH` | 기본값 | `AUTHPRIV` (50-redhat.conf) |
| `LogLevel` | `INFO` | 기본값 | 기본값 |
| `UsePAM` | `no` | `yes` | `yes` (50-redhat.conf) |
| `KbdInteractiveAuthentication` | `yes` | `no` | 옛 이름 `ChallengeResponseAuthentication no` (50-redhat.conf) |
| `PasswordAuthentication` | `yes` | 기본값 | 기본값 |
| `PermitRootLogin` | `prohibit-password` | 기본값(주석 줄만 있음) | 기본값 |
| `AuthorizedKeysFile` | `.ssh/authorized_keys .ssh/authorized_keys2` | 주석 처리해 기본값을 씀(두 파일 모두) | upstream 설정 파일 그대로 `.ssh/authorized_keys` 만[4] |
| `X11Forwarding` | `no` | `yes` | `yes` (50-redhat.conf) |
| `PrintMotd` | `yes` | `no` | `no` (50-redhat.conf) |
| `AcceptEnv` | 없음 | `LANG LC_*` | 없음 |
| `Subsystem sftp` | upstream 설정 파일은 `/usr/libexec/sftp-server`[4] | `/usr/lib/openssh/sftp-server` | 실제 시스템에서 확인. 패키지는 sftp 서버를 `/usr/libexec/openssh/sftp-server` 에 설치 |
| `GSSAPIAuthentication` | `no` (`GSSAPICleanupCredentials` 는 `yes`) | 기본값 | `yes`, `GSSAPICleanupCredentials no` (50-redhat.conf) |
| 암호 알고리즘 정책 | — | — | 50-redhat.conf 첫 설정 줄 `Include /etc/crypto-policies/back-ends/opensshserver.config` |

`ChallengeResponseAuthentication` 은 `KbdInteractiveAuthentication` 의 옛 이름으로, 지금도 같은 뜻으로 받아들입니다[1]. RHEL 패키지는 `/etc/ssh/sshd_config` 와 `50-redhat.conf` 를 권한 0600 으로, `sshd_config.d` 폴더를 0700 으로 설치합니다[6].

RHEL 은 설정 파일 말고도 명령줄로 값을 넘길 수 있습니다. `sshd.service` 가 `EnvironmentFile=-/etc/sysconfig/sshd` 를 읽고 `ExecStart=/usr/sbin/sshd -D $OPTIONS` 로 sshd 를 띄우므로[6], `/etc/sysconfig/sshd` 에 `OPTIONS` 줄이 있으면 그 값도 함께 봅니다. 패키지 설치 스크립트에는 옛 설치본을 옮기는 단계도 있는데, `/etc/sysconfig/sshd-permitrootlogin` 에 `PERMITROOTLOGIN="-oPermitRootLogin=yes"` 가 있고, `sshd_config.d/01-permitrootlogin.conf` 가 없고, 본 파일에 `Include /etc/ssh/sshd_config.d/*.conf` 줄이 있으면 `sshd_config.d/25-permitrootlogin.conf` 에 `PermitRootLogin yes` 를 써 넣고 옛 파일을 지웁니다[6]. 이런 이름의 파일은 사람이 만든 것이 아닐 수 있으므로 패키지 설치 기록과 함께 봅니다.

Ubuntu 는 포트를 소켓 단위가 엽니다. 생성기(sshd-socket-generator)가 sshd 설정의 기본값이 아닌 `Port`·`ListenAddress` 를 읽어 `ssh.socket` 설정에 옮기므로[5], 포트를 확인할 때는 설정 파일과 소켓 설정을 함께 봅니다. 서비스 단위의 차이는 [SSH 허브](index.md)에서 다룹니다.

## 구조

한 줄에 키 하나와 인자를 적고, `#` 로 시작하는 줄과 빈 줄은 주석입니다[1]. 키 이름은 대소문자를 구분하지 않지만 인자는 구분합니다[1]. 해석할 때 지켜야 할 규칙은 셋입니다.

첫째, 예외로 밝힌 키가 아니면 **먼저 나온 값이 이깁니다**[1]. 같은 키가 파일에 두 번 있으면 뒤의 값은 무시됩니다.

둘째, `Include` 는 여러 경로와 glob 을 받고, 펼친 파일을 사전 순으로 읽으며, 절대 경로가 아니면 `/etc/ssh` 기준으로 찾습니다[1]. 두 배포판이 이 줄을 본 파일 맨 앞에 두었으므로 `sshd_config.d` 의 값이 본 파일의 값보다 먼저 읽혀 이깁니다[5][6]. 폴더 안에서는 이름이 앞서는 파일이 이기므로, RHEL 에서 `50-redhat.conf` 보다 이름이 앞서는 파일(예: `10-local.conf`)의 값이 배포판 기본값을 누릅니다. 50-redhat.conf 는 첫 설정 줄에서 암호 알고리즘 정책 파일을 읽으므로, 암호 알고리즘(Ciphers, MACs 등)을 바꾸는 값은 이 파일보다 앞에 읽혀야 적용됩니다[6].

셋째, `Match` 는 조건 블록이고, 조건이 맞으면 다음 `Match` 나 파일 끝까지의 값이 전역 값을 덮습니다[1]. 조건은 `User`, `Group`, `Host`, `LocalAddress`, `LocalPort`, `Address` 등이고, 맞는 블록이 여럿이면 키마다 처음 나온 값만 씁니다[1]. `Include` 는 `Match` 안에도 올 수 있습니다[1]. 그래서 전역 설정이 `PasswordAuthentication no` 여도 특정 주소나 사용자에게만 암호 인증을 열어 둘 수 있습니다.

### 흔적 해석에서 볼 키

| 키 | 왜 보나 |
|---|---|
| `LogLevel`, `LogVerbose`, `SyslogFacility` | 어떤 줄이 어느 파일에 남았어야 하는지 정한다. 등급별로 남는 줄은 [sshd 로그](sshd-logs.md) |
| `AuthorizedKeysFile`, `AuthorizedKeysCommand`, `AuthorizedKeysCommandUser`, `TrustedUserCAKeys`, `AuthorizedPrincipalsFile` | 공개 키를 어디서 가져오는지 정한다. `AuthorizedKeysCommand` 는 키를 찾아 주는 프로그램이라 파일이 없어도 키 인증이 될 수 있다[1] |
| `PermitRootLogin`, `PasswordAuthentication`, `KbdInteractiveAuthentication`, `PubkeyAuthentication`, `PermitEmptyPasswords` | 허용한 인증 방법. `PermitRootLogin` 은 `yes`, `prohibit-password`, `forced-commands-only`, `no` 중 하나다[1] |
| `AllowUsers`, `DenyUsers`, `AllowGroups`, `DenyGroups` | 들어올 수 있는 계정 범위 |
| `ForceCommand`, `PermitUserEnvironment`, `PermitUserRC` | 로그인 때 실행되는 명령과 읽히는 환경 파일(아래 절) |
| `AllowTcpForwarding`, `GatewayPorts`, `PermitTunnel`, `PermitOpen`, `PermitListen` | 이 서버를 거쳐 다른 곳으로 중계할 수 있었는지 |
| `Port`, `ListenAddress` | 어느 포트로 들어왔나 |
| `StrictModes` | `no` 면 홈 폴더와 키 파일의 권한·소유자를 검사하지 않는다[1] |

주요 키의 OpenSSH 기본값은 `MaxAuthTries` 6, `PubkeyAuthentication yes`, `PermitEmptyPasswords no`, `StrictModes yes`, `UseDNS no`, `PrintLastLog yes`, `PermitUserEnvironment no`, `PermitUserRC yes`, `FingerprintHash sha256`, `AllowTcpForwarding yes`, `GatewayPorts no`, `PermitTunnel no` 입니다[1]. 파일에 줄이 없으면 이 값이 적용된 것으로 읽습니다.

### 로그인 때 실행되거나 읽히는 파일

로그인이 성공하면 sshd 는 `/etc/nologin` 을 확인하고, 사용자 권한으로 바꾼 뒤 기본 환경을 만들고, 허용된 경우 `~/.ssh/environment` 를 읽고, 홈 폴더로 옮긴 뒤 `~/.ssh/rc` 를 실행하고, 그 파일이 없거나 `PermitUserRC` 가 꺼져 있으면 `/etc/ssh/sshrc` 를 실행한 다음 사용자의 셸이나 명령을 띄웁니다[2]. `~/.ssh/rc` 는 `PermitUserRC` 가 켜져 있을 때만 돌고(기본 yes)[1][2], `~/.ssh/environment` 는 `PermitUserEnvironment` 가 켜져 있을 때만 읽습니다(기본 no)[1][2]. `~/.ssh/environment` 에는 빈 줄, `#` 주석, `이름=값` 줄만 올 수 있습니다[2]. `ForceCommand` 가 있으면 클라이언트가 보낸 명령과 `~/.ssh/rc` 를 무시하고 그 명령을 사용자의 로그인 셸 `-c` 로 실행합니다[1].

그래서 `~/.ssh/rc` 나 `/etc/ssh/sshrc` 가 있으면 ssh 로그인 때마다 실행되는 지속성 흔적일 가능성이 있고, `PermitUserEnvironment yes` 는 사용자가 로그인 환경 변수를 바꿀 수 있게 연 설정입니다. 같은 역할의 셸 시작 파일은 [셸 시작 파일](../../persistence/shell-startup.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 수집 시점에 파일에 적혀 있던 설정과, 그 설정을 따랐다면 서버가 어떤 인증을 받아 주고 어떤 줄을 어디에 남겼어야 하는지를 보여 줍니다. 로그에 `Accepted password` 줄이 있는데 설정은 `PasswordAuthentication no` 라면, 사건 뒤에 설정이 바뀌었거나 `Match` 블록이 그 접속에만 암호를 허용했을 가능성을 살펴야 합니다.

**증명하지 못하는 것.** 사건 당시 sshd 가 실제로 쓰던 값은 보여 주지 못합니다. sshd 는 SIGHUP 을 받으면 설정을 다시 읽으므로[2], 파일을 고친 뒤 다시 읽기 전까지는 옛 값이 적용됩니다. 누가 파일을 고쳤는지도 파일에는 남지 않습니다.

## 시각 해석

설정 파일 자체에는 시각이 없고, 파일 시스템의 수정 시각(mtime)과 변경 시각(ctime)만 볼 수 있습니다. mtime 은 내용을 마지막으로 고친 때 한 번만 남기므로 그 전에 몇 번 바뀌었는지는 알 수 없습니다. 파일 시스템의 시각은 UTC 기준 epoch 값이라 표시할 때 시간대를 붙입니다([Linux 의 시각 값](../../../01-foundations/value-decoding/time-values.md)).

설정이 언제 적용되었는지는 sshd 로그로 추정합니다. sshd 는 들을 주소를 열 때 `Server listening on 주소 port 번호.` 를, SIGHUP 으로 다시 읽을 때 `Received SIGHUP; restarting.` 을 INFO 등급으로 남기고, 이 줄은 upstream 9.6p1(Ubuntu 24.04 의 바탕)과 8.7p1(RHEL 9 초기 판의 바탕) 코드에도 같습니다[3]. RHEL 의 `sshd.service` 는 `ExecReload=/bin/kill -HUP $MAINPID` 라서 `systemctl reload sshd` 도 이 줄을 남깁니다[6]. 파일 mtime 과 가장 가까운 다음 재시작·다시 읽기 줄 사이가 새 설정이 적용되기 전의 틈입니다. 서비스 시작·정지 기록은 [systemd 저널](../../../01-foundations/logging/systemd-journal/index.md)에서도 볼 수 있습니다.

## 함정과 한계

- 첫 값이 이기는 규칙을 "마지막 값이 이긴다" 로 착각하기 쉽습니다. 특히 본 파일의 `PermitRootLogin no` 가 `sshd_config.d` 의 `PermitRootLogin yes` 에 밀리는 경우를 놓치지 않습니다.
- dissect.target 의 `opensshd.config` 는 `/etc/ssh/sshd_config` 한 파일만 읽고 `Include` 를 따라가지 않으며, `Match` 블록은 건너뜁니다(코드 주석 "This parser does not (yet) follow Include directives", "A match statement, ignore for now")[7]. 두 기준 배포판 모두 중요한 값이 `sshd_config.d` 에 있고 RHEL 은 `SyslogFacility`·`UsePAM` 까지 그 폴더에 있으므로, 이 결과만 믿으면 기본값을 잘못 읽습니다.
- ForensicArtifacts 의 Linux 정의에는 sshd_config 항목이 없습니다[9]. UAC 는 `/etc` 를 통째로 모으므로(shadow·gshadow 제외) `sshd_config.d` 까지 들어옵니다[8].
- 분석 기계에서 `sshd -T -f 증거파일` 로 적용값을 뽑으면, `Include /etc/ssh/sshd_config.d/*.conf` 가 절대 경로라서 증거물이 아니라 분석 기계의 폴더를 읽습니다. 이미지에서는 규칙을 손으로 따라가는 편이 안전합니다.
- 설정 파일이 패키지 기본본과 같은지는 따로 확인합니다([패키지 파일 변조 확인](../../packages/package-verify.md)).

## 직접 분석해 보기

**손으로 한 번.** 아래는 Ubuntu 24.04 시스템을 가정한 만든 예시입니다.

```text
# /etc/ssh/sshd_config.d/10-ops.conf  (만든 예시)
PermitRootLogin yes
Match Address 203.0.113.0/24
    PasswordAuthentication yes

# /etc/ssh/sshd_config  (만든 예시, 필요한 줄만)
Include /etc/ssh/sshd_config.d/*.conf
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
UsePAM yes
```

1. `sshd_config` 첫 설정 줄이 `Include` 이므로 `sshd_config.d/*.conf` 를 이름 순으로 먼저 읽습니다.
2. `10-ops.conf` 의 `PermitRootLogin yes` 가 먼저 나왔으므로 본 파일의 `PermitRootLogin no` 는 무시됩니다.
3. `Match Address 203.0.113.0/24` 블록은 그 대역에서 온 접속에만 `PasswordAuthentication yes` 를 적용하고, 나머지 접속은 본 파일의 `no` 를 따릅니다.
4. 결론은 "root 로그인은 허용되어 있었고, 203.0.113.0/24 에서 온 접속에는 암호 인증이 열려 있었다" 입니다. 이어서 `10-ops.conf` 의 mtime 과 sshd 로그의 `Accepted password for root from 203.0.113.x` 줄을 맞대 봅니다.

**도구로 한 번.** 실행 중인 시스템이면 `sshd -T` 를 실행해 적용값을 봅니다. `-T` 는 설정을 검사해 적용값을 출력하고, `-C user=alice,addr=203.0.113.10` 처럼 접속 조건을 주면 맞는 `Match` 를 반영한 값을 보여 줍니다[2]. 이미지라면 dissect.target 의 `opensshd.config` 로 본 파일의 값과 mtime 을 뽑되[7], 위 함정대로 `sshd_config.d` 는 따로 읽습니다.

## 교차 검증

| 함께 볼 것 | 맞춰 볼 내용 |
|---|---|
| [sshd 로그](sshd-logs.md) | 로그의 인증 방법이 설정에서 허용된 것인가, `LogLevel` 에 맞는 줄만 있는가, 재시작·다시 읽기 시각 |
| [authorized_keys](authorized-keys.md) | `AuthorizedKeysFile` 이 가리키는 파일이 실제로 무엇인가(Ubuntu 는 `authorized_keys2` 도 읽음) |
| [인증 로그 (auth.log·secure)](../auth-log.md) | `SyslogFacility` 에 따라 sshd 줄이 어느 파일로 갔어야 하나 |
| [PAM 모듈 변조](../../persistence/pam-backdoor.md) | `UsePAM yes` 일 때 거치는 `/etc/pam.d/sshd` 의 변조 |
| [셸 시작 파일](../../persistence/shell-startup.md) | `~/.ssh/rc`·`/etc/ssh/sshrc` 와 함께 로그인 때 실행되는 파일 |
| [rpm·dnf·yum 기록](../../packages/rpm-dnf.md), [dpkg·apt 기록](../../packages/dpkg-apt.md) | openssh-server 설치·갱신 시각과 설정 파일 mtime 이 겹치는가 |

사건 전체 흐름은 [SSH 로 들어왔나](../../../04-scenarios/intrusion/ssh-intrusion.md)에서 다룹니다.

## 실습

공개 시험 데이터(NIST CFReDS 등)의 Linux 이미지로 다음을 풀어 봅니다.

1. `/etc/ssh/sshd_config` 에서 `Include` 줄은 어디에 있고, `sshd_config.d` 에는 어떤 파일이 있습니까? 이름 순으로 읽었을 때 `PermitRootLogin`, `PasswordAuthentication`, `LogLevel`, `SyslogFacility` 의 적용값은 무엇입니까?
2. `Match` 블록이 있다면 어떤 조건에서 어떤 값을 바꿉니까?
3. 설정 파일들의 mtime 은 언제이고, 그 뒤 sshd 로그에 `Server listening on` 이나 `Received SIGHUP; restarting.` 줄이 처음 나오는 시각은 언제입니까?
4. 사용자 홈에 `~/.ssh/rc` 나 `~/.ssh/environment` 가 있습니까? 설정상 실제로 실행되거나 읽힐 수 있었습니까?

## 참고 문헌

1. OpenSSH portable, sshd_config.5 (`Include`, `Match`, `PermitRootLogin`, `KbdInteractiveAuthentication`, `PermitUserEnvironment`, `PermitUserRC`, `ForceCommand`, `AuthorizedKeysCommand`, `StrictModes` 등). https://github.com/openssh/openssh-portable/blob/master/sshd_config.5
2. OpenSSH portable, sshd.8 (`-T`, `-C`, SIGHUP, LOGIN PROCESS, SSHRC, FILES). https://github.com/openssh/openssh-portable/blob/master/sshd.8
3. OpenSSH portable, sshd.c (master, V_9_6_P1, V_8_7_P1 태그). https://github.com/openssh/openssh-portable/blob/master/sshd.c , https://github.com/openssh/openssh-portable/tree/V_9_6_P1 , https://github.com/openssh/openssh-portable/tree/V_8_7_P1
4. OpenSSH portable, sshd_config (master, V_9_9_P1 태그). https://github.com/openssh/openssh-portable/blob/master/sshd_config , https://github.com/openssh/openssh-portable/tree/V_9_9_P1
5. Ubuntu, openssh 패키지 noble-updates (debian-config.patch, restore-authorized_keys2.patch, README.Debian). https://git.launchpad.net/ubuntu/+source/openssh/tree/debian?h=ubuntu/noble-updates
6. CentOS Stream 9, openssh 패키지 (openssh.spec, openssh-7.7p1-redhat.patch, sshd.service, sshd.sysconfig). https://gitlab.com/redhat/centos-stream/rpms/openssh/-/tree/c9s
7. fox-it dissect.target, dissect/target/plugins/apps/ssh/opensshd.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/ssh/opensshd.py
8. tclahr UAC, artifacts/files/system/etc.yaml, artifacts/files/ssh/rc.yaml. https://github.com/tclahr/uac/tree/main/artifacts
9. ForensicArtifacts artifacts, artifacts/data/linux.yaml, unix_common.yaml. https://github.com/ForensicArtifacts/artifacts/tree/main/artifacts/data
