---
title: "SSH 로 들어왔나"
parent: "시나리오 · 침해"
nav_order: 1030
---

# SSH 로 들어왔나 (SSH Intrusion)

## 조사 질문

외부에서 SSH 로 이 서버에 로그인했는지, 했다면 어느 계정으로 어느 주소에서 어떤 인증 방법(비밀번호·공개 키)으로 들어왔는지를 묻습니다. 이어서 세션이 언제 끝났는지, 들어온 뒤 무엇을 했는지, 이 서버에서 다시 다른 서버로 SSH 로 옮겨 갔는지까지 따라갑니다. 비밀번호 대입 (brute force) 이 있었다면 그 대입이 성공으로 이어졌는지가 핵심입니다.

이 쪽은 조사 순서와 해석만 다룹니다. sshd 로그 줄의 문구, authorized_keys·known_hosts 의 구조, sshd 설정 키는 [SSH](../../02-artifacts/logins/ssh/index.md) 아래 쪽에서 다룹니다.

## 먼저 확인할 것

**OpenSSH 판과 로그 태그.** 판에 따라 sshd 줄을 찾는 이름이 달라집니다. OpenSSH 9.8 부터 연결을 받는 `sshd` 와 연결마다 새로 도는 `sshd-session` 이 나뉘었고, 인증 결과 줄은 `sshd-session` 이 씁니다[7][16]. 판은 검체의 패키지 기록([dpkg·apt](../../02-artifacts/packages/dpkg-apt.md), [rpm·dnf](../../02-artifacts/packages/rpm-dnf.md))으로 확인합니다.

| 항목 | Ubuntu 24.04 | RHEL 9 계열 |
|---|---|---|
| OpenSSH 판 | 9.6p1[9] | CentOS Stream 9 패키지는 8.7p1 에서 9.9p1 로 바뀌었습니다[10] |
| 인증 줄의 태그 | `sshd` | 9.9p1 이면 `sshd-session`(`/usr/libexec/openssh/sshd-session`), 8.7p1 이면 `sshd`[7][10] |
| 인증 로그 파일 | `/var/log/auth.log` | `/var/log/secure` |
| 서비스 단위 | `ssh.socket` 소켓 활성화가 기본[9] | `sshd.service`, `sshd.socket`[10] |
| 설정 조각 | `sshd_config` 가 `Include /etc/ssh/sshd_config.d/*.conf` 로 조각을 읽습니다[9] | 같은 `Include` 에 패키지 조각 `50-redhat.conf`(`SyslogFacility AUTHPRIV`, `UsePAM yes`)[10] |
| sshd 자체 감사 기록 | `--with-audit=linux` 로 빌드합니다[9] | `--with-audit=linux` 로 빌드하고 감사 패치가 더 붙습니다[10] |

**설정.** 기본 `LogLevel` 은 `INFO` 이고[6], 이 수준에서는 sshd 의 `Connection from`, `Starting session`, `Close session` 줄이 남지 않습니다[3][7]. 비밀번호 로그인이 허용됐는지, root 로그인이 허용됐는지, 로그 수준이 바뀌었는지는 `sshd_config` 와 `sshd_config.d/` 의 조각을 모두 읽어야 알 수 있습니다. RHEL 에서는 옛 설치 프로그램이 만든 `/etc/sysconfig/sshd-permitrootlogin` 에 root 로그인 허용이 들어 있고 `sshd_config.d/01-permitrootlogin.conf` 가 없으면, 패키지 설치 스크립트가 `sshd_config.d/25-permitrootlogin.conf` 에 `PermitRootLogin yes` 를 씁니다[10].

**시각과 시간대.** Ubuntu 24.04 의 인증 로그 줄에는 연도와 UTC 오프셋이 있고, RHEL 의 전통 형식 줄에는 연도와 시간대가 없습니다([인증 로그](../../02-artifacts/logins/auth-log.md)). 저널은 UTC 로 저장하므로, 파일 로그와 저널을 한 타임라인에 놓기 전에 검체의 시간대를 확인합니다([호스트 이름과 시간대](../../02-artifacts/system-info/hostname-timezone.md)).

**사용자와 수집 범위.** 로그인할 수 있는 계정과 홈 디렉터리 목록을 [계정 파일](../../01-foundations/users-auth/passwd-shadow-group.md)에서 뽑아 둡니다. 순환된 옛 로그(`auth.log.1`, `.gz`)와 저널 파일, `/root` 를 포함한 모든 홈의 `~/.ssh/` 가 수집 범위에 들어 있어야 합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | auth.log·secure, 저널의 sshd·sshd-session·systemd-logind 줄 | 인증 성공·실패, 원격 주소, 인증 방법, 공개 키 지문, 세션 끝 | [인증 로그](../../02-artifacts/logins/auth-log.md), [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) |
| 2 | wtmp·btmp·lastlog | 터미널 세션의 시작·끝, 비밀번호 실패 | [로그인 기록](../../02-artifacts/logins/wtmp-btmp-lastlog.md) |
| 3 | `sshd_config` 와 `sshd_config.d/*` | 허용된 인증 방법, 로그 수준, 포트 | [SSH](../../02-artifacts/logins/ssh/index.md) |
| 4 | 각 홈의 `~/.ssh/`(authorized_keys, rc, environment, known_hosts, 개인 키) | 들어온 키, 로그인 때 도는 명령, 밖으로 나간 흔적 | [SSH](../../02-artifacts/logins/ssh/index.md) |
| 5 | 감사 로그 | sshd 가 남긴 로그인 성공·실패, 세션 프로세스의 `auid` | [감사 로그 형식](../../01-foundations/logging/auditd-format.md) |
| 6 | 셸 명령 기록, sudo·su 기록 | 로그인 뒤 한 일 | [셸 명령 기록](../../02-artifacts/execution/shell-history/index.md), [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md) |
| 7 | 파일 시스템 타임라인 | 로그인 시각 뒤에 생기거나 바뀐 파일 | [타임라인 만들기](../../03-techniques/analysis/timeline.md) |

## 분석 흐름

1. **판·설정·태그를 정합니다.** 위 표에서 인증 줄의 태그(`sshd` 또는 `sshd-session`), 로그 파일, 시각 형식, `LogLevel` 을 정한 뒤 검색 조건을 만듭니다. 두 태그를 함께 찾으면 판을 잘못 짚어도 빠뜨리지 않습니다.

2. **실패를 주소별로 셉니다.** `Failed password`, `Invalid user` 줄을 원격 주소별·시간대별로 세고, 같은 주소에서 뒤이어 `Accepted` 줄이 나오는지 봅니다. Velociraptor `Linux.Events.SSHBruteforce` 도 같은 방식으로, 한 시간 안에 같은 사용자의 비밀번호 실패가 `MinimumFailedLogins`(기본 2)보다 많이 쌓인 뒤 비밀번호 성공이 오면 알립니다[17]. `UsePAM yes` 설정에서는 sshd 줄과 따로 `pam_unix(sshd:auth)` 의 `authentication failure` 줄이 남고, 같은 사용자의 이어진 실패는 `N more authentication failures` 한 줄로 묶이므로[14], 건수는 sshd 줄로 셉니다.

3. **성공한 인증을 하나씩 정리합니다.** `Accepted` 줄마다 시각, 계정, 원격 주소와 포트, 방식을 적습니다. 인증 결과 줄의 서식은 아래와 같습니다[1].

    ```
    Accepted|Failed 방식 for [invalid user ]이름 from IP port 포트 ssh2[: 키형식 지문]
    ```

    방식이 `publickey` 이면 줄 끝의 지문을 각 계정 authorized_keys 의 키 지문과 맞춰 어느 키가 쓰였는지 찾습니다. authorized_keys 파일을 `ssh-keygen -l -f` 로 읽으면 키 줄마다 지문이 나옵니다[8].

4. **세션의 앞뒤를 묶습니다.** 한 접속은 보통 아래 순서로 남습니다. 인증 뒤에는 sshd 가 권한을 내린 자식 프로세스를 새로 띄워 세션을 맡기므로, 연결이 끝나는 `Disconnected` 줄의 PID 는 `Accepted` 줄의 PID 와 다릅니다[7]. 그래서 같은 접속은 원격 주소와 포트로 묶고, 인증 뒤 끝나는 줄의 머리말은 `user 이름` 입니다[2][3].

    ```
    (만든 예시, Ubuntu 24.04 형식)
    2026-03-12T14:04:51.102938+09:00 web01 sshd[2211]: Failed password for invalid user oracle from 203.0.113.10 port 51002 ssh2
    2026-03-12T14:05:09.551204+09:00 web01 sshd[2230]: Accepted password for alice from 203.0.113.10 port 51234 ssh2
    2026-03-12T14:05:09.771020+09:00 web01 sshd[2230]: pam_unix(sshd:session): session opened for user alice(uid=1001) by (uid=0)
    2026-03-12T14:05:09.790114+09:00 web01 systemd-logind[811]: New session 7 of user alice.
    2026-03-12T15:02:13.300871+09:00 web01 sshd[2275]: Disconnected from user alice 203.0.113.10 port 51234
    2026-03-12T15:02:13.310422+09:00 web01 sshd[2230]: pam_unix(sshd:session): session closed for user alice
    2026-03-12T15:02:13.330157+09:00 web01 systemd-logind[811]: Removed session 7.
    ```

    pam_unix 의 세션 줄과 systemd-logind 의 `New session N of user 이름.`, `Removed session N.` 줄이 sshd 줄을 둘러쌉니다[14][15]. RHEL 9.9p1 이면 sshd 줄의 태그 자리가 `sshd-session` 이고, 전통 형식이면 줄 머리가 `Mar 12 14:05:09 web01` 모양입니다.

5. **로그인 기록 파일과 맞춥니다.** sshd 는 터미널(pty)을 받은 세션에서만 wtmp 에 로그인을 기록합니다[3][5]. 그래서 셸을 연 세션은 `last` 에도 나오고, 명령 하나만 실행한 접속이나 scp·sftp 는 인증 로그에만 나옵니다. btmp 에는 없는 계정 이름의 시도와 비밀번호·keyboard-interactive 방식의 실패가 터미널 칸 `ssh:notty` 로 남습니다[1][4]. wtmp·btmp 는 `last -f /var/log/wtmp`, `last -f /var/log/btmp` 로 읽을 수 있습니다[19].

6. **감사 로그를 봅니다.** 두 배포판 모두 sshd 의 PAM 설정에 `pam_loginuid` 가 있어서[9][10], SSH 세션에서 뜬 프로세스의 감사 기록 `auid` 에는 로그인한 계정의 UID 가 들어갑니다[12]. 데몬이 띄운 프로세스는 `auid` 가 설정되지 않아 `4294967295` 로 찍힙니다[13]. 두 배포판 모두 OpenSSH 를 Linux 감사 기능과 함께 빌드하고[9][10], 이 코드는 터미널을 받은 세션을 열 때(성공)와 인증에 실패하거나 없는 계정일 때(실패) `USER_LOGIN`(1112) 레코드를 남깁니다[4][11][12]. RHEL 패키지에는 감사 패치가 더 붙으므로[10] 실제로 어떤 레코드가 있는지는 검체의 audit.log 에서 확인합니다.

7. **들어온 키와 로그인 때 도는 것을 봅니다.** authorized_keys 의 줄 앞 옵션 `command="…"` 는 그 키로 인증하면 정해 둔 명령을 실행하게 합니다[5]. `~/.ssh/rc` 는 `PermitUserRC` 가 켜져 있으면 로그인 때 사용자 셸보다 먼저 실행되고, 이 파일이 없거나 `PermitUserRC` 가 꺼져 있으면 `/etc/ssh/sshrc` 가 있을 때 그것이 실행됩니다[5]. 파일의 바뀐 시각과 첫 로그인 시각을 비교해, 들어온 뒤 키를 심었는지 봅니다. 자세한 확인 방법은 [무엇이 계속 살아남게 했나](persistence-hunt.md)에서 다룹니다.

8. **로그인 뒤 한 일을 좁힙니다.** 로그인한 계정의 셸 명령 기록, sudo·su 줄을 시각순으로 붙입니다. 파일 쪽에서는 로그인 시각을 기준으로 그 뒤에 생기거나 바뀐 파일을 찾습니다. 한 침해 사례에서는 `find rootvol/ -type f -newercm rootvol/var/log/lastlog` 로 로그인 뒤 추가된 파일을 찾아 공격에 쓴 실행 파일을 발견했습니다[19]. 이 방법은 기준 파일의 ctime 에 기대므로, 어느 파일을 기준으로 삼느냐에 따라 결과가 달라집니다.

9. **옆으로 옮겨 갔는지 봅니다.** `~/.ssh/known_hosts` 에는 사용자가 처음 접속한 서버의 호스트 키가 자동으로 추가됩니다[5]. 그래서 침해된 계정의 known_hosts, 셸 기록의 `ssh` 명령, 개인 키 파일이 이 서버에서 밖으로 나간 흔적입니다. Ubuntu 는 `/etc/ssh/ssh_config` 에 `HashKnownHosts yes` 를 두어 호스트 이름과 주소를 해시로 저장하므로[9], 의심 서버가 있는지는 `ssh-keygen -F 호스트` 로 찾습니다[8]. 앞의 사례에서도 한 서버의 `.bash_history` 와 다른 서버의 auth.log 를 맞춰 SSH 키로 옮겨 간 경로를 확인했습니다[19]. 상대 서버의 인증 로그에 같은 시각, 이 서버 주소로 된 `Accepted publickey` 줄이 있는지 봅니다.

## 흔한 오판

- **"공개 키 실패 줄이 없으니 키 대입은 없었다."** 기본 `INFO` 에서 인증 결과 줄은 성공, 없는 계정, 비밀번호 방식, 실패 누적이 `MaxAuthTries` 의 절반 이상일 때만 남고 그 밖은 `VERBOSE` 로 남습니다[1]. 있는 계정에 공개 키로 시도한 초반 실패는 기본 설정에서 보이지 않습니다.
- **"wtmp 에 없으니 로그인이 없었다."** 터미널 없는 접속은 wtmp 에 쓰지 않습니다[3]. 인증 로그의 `Accepted` 줄이 기준입니다.
- **"btmp 에 없으니 실패가 없었다."** 공개 키 실패는 btmp 에 쓰지 않습니다[1]. `/var/log/btmp` 가 없으면 sshd 는 기록하지 않고, root 소유가 아니거나 그룹 실행·다른 사용자 권한이 있으면 기록하지 않고 `Excess permission or bad ownership on file /var/log/btmp` 를 남깁니다[4].
- **"`sshd[` 로 검색하면 다 나온다."** OpenSSH 9.8 이상에서는 인증 줄의 태그가 `sshd-session` 입니다[7][16]. Velociraptor 의 SSH 로그인 아티팩트는 프로그램 이름이 `sshd` 인 줄만 고르고 시각 칸을 전통 형식(`SYSLOGTIMESTAMP`)으로 읽으므로[17], `sshd-session` 줄이나 Ubuntu 24.04 의 RFC 3339 줄이 빠질 가능성이 있습니다.
- **"`Invalid user` 뒤 이름은 노린 계정 목록이다."** 이 이름은 클라이언트가 보낸 문자열 그대로이고[16], btmp 에도 그대로 들어갑니다[4]. 사용자가 이름 칸에 비밀번호를 잘못 넣은 경우도 그대로 남으므로[4], 보고서에 옮길 때 주의합니다.
- **"`Connection closed by … [preauth]` 는 로그인이다."** `[preauth]` 는 인증 전 단계의 줄에 붙습니다[3]. 로그인 성공은 `Accepted` 줄로만 판단합니다.
- **"설정 파일만 보면 된다."** 두 배포판 모두 `sshd_config.d/` 조각을 읽고, RHEL 은 로그 facility 와 PAM 사용 여부가 조각에 있습니다[9][10]. dissect 의 sshd 설정 플러그인은 `Include` 를 따라가지 않으므로[18], 그 결과만으로 설정을 판단하면 틀릴 수 있습니다.
- **"원격 주소가 공격자다."** 원격 주소는 마지막으로 연결한 기계의 주소입니다. 중계 서버나 다른 침해 서버를 거쳤을 수 있습니다.

## 보고서 문장 예

아래 값은 모두 만든 예시입니다.

- "2026-03-12 14:05:09(+09:00)에 203.0.113.10 포트 51234 에서 계정 alice 로 비밀번호 인증에 성공한 기록(`Accepted password`)이 /var/log/auth.log 에 있습니다. 같은 주소에서 그 전 40분 동안 `Failed password` 줄이 312개 있습니다."
- "같은 접속의 세션은 15:02:13(+09:00)에 끝났고(`Disconnected from user alice`), 이 시각 범위의 wtmp 에 alice 의 터미널 세션이 있습니다."
- "이 기록은 해당 계정으로 인증이 성공했음을 보여 줄 뿐, 접속한 사람을 특정하지 않습니다."

## 함께 볼 페이지

- [SSH](../../02-artifacts/logins/ssh/index.md) — sshd 로그 문구, 설정, authorized_keys, known_hosts
- [인증 로그](../../02-artifacts/logins/auth-log.md) — 줄 머리, 시각 형식, PAM 줄
- [로그인 기록](../../02-artifacts/logins/wtmp-btmp-lastlog.md) — wtmp·btmp·lastlog 읽는 법
- [권한을 올렸나](privilege-escalation.md) — 로그인 뒤 root 를 얻었는지
- [무엇이 계속 살아남게 했나](persistence-hunt.md) — authorized_keys·rc 로 남긴 것
- [안티포렌식](../insider/anti-forensics.md) — 로그를 지운 흔적
- [사용자 특정](../attribution/user-attribution.md) — 계정과 사람을 잇는 법

## 참고 문헌

1. OpenSSH portable, auth.c (`auth_log`, `record_failed_login` 호출). https://github.com/openssh/openssh-portable/blob/master/auth.c
2. OpenSSH portable, packet.c (`sshpkt_fmt_connection_id`, 연결 끝 줄). https://github.com/openssh/openssh-portable/blob/master/packet.c
3. OpenSSH portable, session.c · monitor.c · auth2.c. https://github.com/openssh/openssh-portable/blob/master/session.c , https://github.com/openssh/openssh-portable/blob/master/monitor.c , https://github.com/openssh/openssh-portable/blob/master/auth2.c
4. OpenSSH portable, loginrec.c (`record_failed_login`) · configure.ac (`USE_BTMP`). https://github.com/openssh/openssh-portable/blob/master/loginrec.c , https://github.com/openssh/openssh-portable/blob/master/configure.ac
5. OpenSSH portable, sshd.8 (LOGIN PROCESS, SSHRC, AUTHORIZED_KEYS FILE FORMAT, SSH_KNOWN_HOSTS FILE FORMAT). https://github.com/openssh/openssh-portable/blob/master/sshd.8
6. OpenSSH portable, sshd_config.5 (`LogLevel`, `MaxAuthTries`). https://github.com/openssh/openssh-portable/blob/master/sshd_config.5
7. OpenSSH portable, V_9_9_P1 태그의 sshd.c · sshd-session.c (`privsep_postauth`). https://github.com/openssh/openssh-portable/tree/V_9_9_P1
8. OpenSSH portable, ssh-keygen.1 (`-l`, `-F`) · ssh-keygen.c. https://github.com/openssh/openssh-portable/blob/master/ssh-keygen.1 , https://github.com/openssh/openssh-portable/blob/master/ssh-keygen.c
9. Ubuntu, openssh 패키지 noble-updates (changelog, README.Debian, debian-config.patch, openssh-server.sshd.pam.in, rules). https://git.launchpad.net/ubuntu/+source/openssh/tree/debian?h=ubuntu/noble-updates
10. CentOS Stream 9, openssh 패키지 (openssh.spec, openssh-7.7p1-redhat.patch, sshd.pam). https://gitlab.com/redhat/centos-stream/rpms/openssh/-/tree/c9s
11. OpenSSH portable, audit-linux.c. https://github.com/openssh/openssh-portable/blob/master/audit-linux.c
12. linux-audit, audit-documentation specs/messages/message-dictionary.csv · specs/fields/field-dictionary.csv. https://github.com/linux-audit/audit-documentation/tree/main/specs
13. linux-audit, audit-userspace docs/audit.rules.7. https://github.com/linux-audit/audit-userspace/blob/master/docs/audit.rules.7
14. Linux-PAM, modules/pam_unix/pam_unix_sess.c · support.c. https://github.com/linux-pam/linux-pam/tree/master/modules/pam_unix
15. systemd, v255 src/login/logind-session.c. https://github.com/systemd/systemd/blob/v255/src/login/logind-session.c
16. log2timeline plaso, plaso/parsers/text_plugins/syslog.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/syslog.py
17. Velocidex velociraptor, artifacts/definitions/Linux/Events/SSHBruteforce.yaml · Syslog/SSHLogin.yaml. https://github.com/Velocidex/velociraptor/tree/master/artifacts/definitions/Linux
18. fox-it dissect.target, dissect/target/plugins/apps/ssh/opensshd.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/ssh/opensshd.py
19. Ali Hadi, Mariam Khader, Thomas Claflin, "Learning Linux Forensic Analysis and Why it Matters", DFRWS 발표. https://dfrws.org/presentation/learning-linux-forensic-analysis-and-why-it-matters/
