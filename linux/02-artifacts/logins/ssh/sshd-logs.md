---
title: "sshd 로그"
parent: "SSH"
grand_parent: "아티팩트 · 로그인과 계정"
nav_order: 360
---

# sshd 로그 (sshd Logs)

SSH 서버 데몬 sshd 가 인증 성공·실패와 연결 끊김을 syslog 로 남긴 줄이며, 누가 어느 주소에서 어떤 방식과 어떤 키로 들어왔는지를 보여 줍니다.

## 무엇을 기록하나 · 왜 생기나

sshd 는 인증 한 번이 끝날 때마다 결과를 한 줄로 남깁니다[1]. 여기에 없는 사용자 이름으로 들어온 시도, 설정으로 막힌 계정, 연결을 끊은 이유가 함께 남습니다[1][2]. 무엇이 남는지는 `LogLevel` 값에 따라 다르고 기본값은 `INFO` 입니다[7]. 연결 시작, 세션 열고 닫음, 어느 authorized_keys 몇 번째 줄이 맞았는지는 한 단계 위인 `VERBOSE` 에서만 나오므로, 분석 전에 검체의 `LogLevel` 부터 확인합니다([sshd 설정](sshd-config.md)).

이 쪽은 sshd 가 쓰는 문구와 그 해석만 다룹니다. 줄이 어느 파일로 가는지, 시각 형식, PAM 줄(`pam_unix(sshd:session)` 등)은 [인증 로그](../auth-log.md)에서 다룹니다.

## 위치와 버전별 차이

| 항목 | Ubuntu 24.04 | RHEL 9 계열 |
|---|---|---|
| OpenSSH 판 | 9.6p1[10] | CentOS Stream 9 의 현재 패키지는 9.9p1 이고 그 전은 8.7p1 입니다[9]. 검체에서 `rpm -q openssh-server` 로 판을 확인합니다 |
| 기록 facility | 기본값 `AUTH`[7] | `/etc/ssh/sshd_config.d/50-redhat.conf` 의 `SyslogFacility AUTHPRIV`[9] |
| 파일 | `/var/log/auth.log` | `/var/log/secure` |
| 줄의 태그 | `sshd` | 9.9p1 패키지에는 `/usr/libexec/openssh/sshd-session` 이 들어 있어[9] 인증 줄의 태그가 `sshd-session` 일 수 있습니다 |
| 서비스 시작 | `ssh.socket` 소켓 활성화가 기본[10] | `sshd.service`[9] |

OpenSSH 9.8 부터 서버가 연결을 받는 `sshd` 와 연결마다 도는 `sshd-session` 으로 나뉘었고, 인증 줄은 `sshd-session` 이 씁니다[11]. 두 태그를 모두 찾아야 빠뜨리지 않습니다. 저널에서는 facility 와 상관없이 모든 줄이 남으므로 `SYSLOG_IDENTIFIER` 로 두 태그를 함께 고릅니다([systemd 저널](../../../01-foundations/logging/systemd-journal/index.md)).

## 구조

### 인증 결과 줄

인증 결과 줄의 서식은 아래와 같고, 8.7p1·9.6p1·현재 master 가 같습니다[1][8].

```
Accepted|Failed|Partial|Postponed 방식[/하위방식] for [invalid user ]이름 from IP port 포트 ssh2[: 키정보]
```

방식 자리에는 `password`, `publickey`, `keyboard-interactive/pam`, `none` 같은 값이 들어갑니다[1]. 키 정보는 공개 키면 `키형식 지문`(예: `ED25519 SHA256:…`)이고, 인증서면 `형식 지문 ID 키ID (serial N) CA CA형식 CA지문` 입니다[1]. 지문을 만드는 해시는 `FingerprintHash` 로 정하고 기본값은 `sha256` 입니다[7]. 사용자 이름은 100자, 주소는 200자에서 잘립니다[1].

이 줄이 `INFO` 로 남는 조건은 넷입니다. 인증에 성공했을 때, 없는 사용자일 때, 이 연결의 실패 누적이 `MaxAuthTries` 의 절반 이상일 때, 방식이 `password` 일 때입니다[1]. 이 밖은 `VERBOSE` 로 남습니다. `MaxAuthTries` 기본값은 6이므로[7], 있는 계정에 공개 키로 시도해 실패한 처음 세 번은 기본 설정에서 남지 않고 네 번째 실패부터 남습니다[1]. 실패 횟수는 이 줄을 쓴 뒤에 올라가고, 첫 `none` 시도는 셈하지 않습니다[1].

### 그 밖의 줄

| 줄 모양 | 등급 | 뜻 |
|---|---|---|
| `Invalid user 이름 from IP port 포트` | INFO | 없는 계정 이름으로 접속했습니다[1] |
| `maximum authentication attempts exceeded for [invalid user ]이름 from IP port 포트 ssh2` | ERROR | 실패가 `MaxAuthTries` 에 닿아 서버가 끊었습니다[1] |
| `User 이름 from 호스트 not allowed because not listed in AllowUsers` 등 | INFO | `AllowUsers`·`DenyUsers`·`AllowGroups`·`DenyGroups` 에 막혔습니다[1] |
| `User 이름 not allowed because shell 경로 does not exist` / `… is not executable` | INFO | 셸이 없거나 실행할 수 없습니다[1] |
| `ROOT LOGIN REFUSED FROM IP port 포트` | INFO | root 로그인이 막혔습니다[1] |
| `Received disconnect from IP port 포트:코드: 문구` | 서버에서 받은 끊는 이유가 `SSH2_DISCONNECT_BY_APPLICATION` 이면 INFO, 아니면 ERROR | 상대가 끊음 메시지를 보냈고, 문구는 상대가 보낸 문자열을 그대로 찍은 것입니다[2] |
| `Disconnected from 머리말 IP port 포트` / `Connection closed by …` / `Connection reset by …` / `Connection from … timed out` | INFO | 연결이 끝난 모양입니다[2] |
| `Authentication refused: bad ownership or modes for file 경로` | INFO | authorized_keys 나 그 위 폴더의 소유자·권한 때문에 키를 읽지 않았습니다[6] |
| `파일:줄: Authentication tried for 이름 with correct key but not from a permitted host (host=…, ip=…, required=…).` | INFO | 맞는 키지만 `from=` 옵션이 허용한 곳이 아닙니다[6] |
| `Timeout before authentication for …` | 기본 설정에서 남음 | 로그인 제한 시간 안에 인증을 끝내지 못했습니다[4][8] |
| `Server listening on 주소 port 포트.` / `Received signal N; terminating.` | INFO | 서버가 시작했거나 끝났습니다[4] |
| `Connection from IP port 포트 on IP port 포트` | VERBOSE | 연결이 들어왔습니다[4][8] |
| `Starting session: 종류[ on tty] for 이름 from IP port 포트 id N` / `Close session: user 이름 from IP port 포트 id N` | VERBOSE | 세션을 열고 닫았고, 종류는 `shell`·`command`·`subsystem '…'`·`forced-command …` 입니다[5][8] |
| `Accepted key 형식 지문 found at 파일:줄번호` | VERBOSE | 어느 authorized_keys 의 몇 번째 줄이 맞았는지 보여 줍니다[6] |

연결 끝 줄의 머리말 (preamble) 은 인증 중이면 `authenticating user 이름` 이나 `invalid user 이름`, 인증 뒤면 `user 이름` 입니다[2][3]. 줄 끝의 `[preauth]`·`[postauth]` 는 권한을 낮춘 자식 프로세스가 남긴 줄을 감시 프로세스 (monitor) 가 대신 쓸 때 붙입니다[3]. `[preauth]` 줄은 인증 전 단계에서 나왔다는 뜻이고, 계정이 있다는 뜻은 아닙니다.

### 한 번의 접속 흐름

아래는 Ubuntu 24.04 에서 무작위 계정 시도 하나와 공개 키 로그인 하나를 보여 주는 만든 예시입니다. 시각 형식은 [인증 로그](../auth-log.md)에서 설명합니다.

```
(만든 예시)
2025-03-04T09:14:55.000001+09:00 web01 sshd[2201]: Invalid user admin from 198.51.100.7 port 41022
2025-03-04T09:14:57.000002+09:00 web01 sshd[2201]: Failed password for invalid user admin from 198.51.100.7 port 41022 ssh2
2025-03-04T09:14:58.000003+09:00 web01 sshd[2201]: Connection closed by invalid user admin 198.51.100.7 port 41022 [preauth]
2025-03-04T09:15:02.000004+09:00 web01 sshd[2211]: Accepted publickey for alice from 203.0.113.10 port 50122 ssh2: ED25519 SHA256:(생략)
2025-03-04T09:15:02.000005+09:00 web01 sshd[2211]: pam_unix(sshd:session): session opened for user alice(uid=1001) by (uid=0)
2025-03-04T09:40:11.000007+09:00 web01 sshd[2211]: Received disconnect from 203.0.113.10 port 50122:11: disconnected by user
2025-03-04T09:40:11.000008+09:00 web01 sshd[2211]: Disconnected from user alice 203.0.113.10 port 50122
2025-03-04T09:40:11.000009+09:00 web01 sshd[2211]: pam_unix(sshd:session): session closed for user alice
```

같은 접속의 줄은 대괄호 안 PID 와 원격 포트가 같으므로 이 둘로 묶습니다. `Received disconnect` 뒤의 문구는 클라이언트가 보낸 문자열이라 클라이언트마다 다릅니다[2].

## 증거로서 의미

**증명하는 것.** `Accepted` 줄은 그 시각에 그 원격 주소·포트에서 그 계정으로 그 방식의 인증이 성공했다는 기록입니다[1]. 공개 키 방식이면 쓰인 키의 지문까지 남으므로 어느 키로 들어왔는지 좁힐 수 있습니다[1]. `Invalid user`·`Failed` 줄은 그 이름과 방식으로 시도해 실패했다는 기록입니다.

**증명하지 못하는 것.** 로그인 뒤에 무엇을 했는지는 남지 않습니다. 기본 `INFO` 에서는 `Starting session` 이 없어서 셸을 열었는지 명령 하나만 돌렸는지도 알 수 없고, 이 판단은 [로그인 기록](../wtmp-btmp-lastlog.md)의 터미널 세션과 함께 합니다. 공개 키 실패 초반 시도는 앞에서 본 대로 빠집니다. 원격 주소는 마지막으로 연결한 기계의 주소이지 사람의 위치가 아니며, 중계 서버를 거쳤을 수 있습니다([known_hosts 와 클라이언트 설정](known-hosts.md)). 실패 줄의 사용자 이름은 클라이언트가 보낸 문자열이라 그 계정이 있다는 뜻이 아닙니다[11].

보고서에는 "2025-03-04 09:15:02(+09:00)에 203.0.113.10 에서 alice 계정으로 ED25519 키 공개 키 인증에 성공한 기록이 있다" 처럼 줄이 말하는 만큼만 씁니다.

## 시각 해석

줄의 시각은 sshd 가 그 사건을 기록한 때이고, 파일에 적히는 모양은 배포판의 rsyslog 서식을 따릅니다. Ubuntu 24.04 줄에는 연도와 UTC 오프셋이 있지만 RHEL 9 의 전통형 줄에는 연도·시간대가 없으므로, 연도를 추정하는 방법은 [인증 로그](../auth-log.md)와 [syslog 형식과 rsyslog](../../../01-foundations/logging/syslog-rsyslog.md)를 봅니다. 한 접속의 길이는 `Accepted` 줄과 같은 PID 의 `Disconnected from`·`session closed` 줄 사이로 잽니다.

Ubuntu 는 소켓 활성화가 기본이라서[10] 연결이 올 때 sshd 가 시작될 수 있고, `Server listening` 줄의 시각이 부팅 시각과 다를 가능성이 있습니다.

## 함정과 한계

- **태그 필터.** OpenSSH 9.8 이상에서는 태그가 `sshd-session` 일 수 있습니다[11]. Velociraptor `Linux.Syslog.SSHLogin` 은 전통형 시각(`SYSLOGTIMESTAMP`)만 받고 프로그램이 `sshd` 인 줄만 고르므로[14], Ubuntu 24.04 의 RFC 3339 줄이나 `sshd-session` 줄이 빠질 가능성이 있습니다. dissect `authlog` 도 필드를 더 뽑는 서비스 목록에 `sshd` 만 있어서[12] `sshd-session` 줄은 사용자·주소가 따로 나뉘지 않습니다.
- **방식 분류.** plaso 는 `Failed`·`Accepted` 줄의 방식으로 `password`·`publickey` 만 알아보므로[11] `keyboard-interactive/pam` 줄은 구조화되지 않습니다. dissect 는 줄에 `password` 가 없으면 publickey 로 분류하므로[12] `keyboard-interactive/pam` 이 publickey 로 잡힐 가능성이 있습니다.
- **plaso 의 연결 줄.** plaso 는 `Connection from IP port N` 을 따로 파싱하지만[11], 실제 줄은 `Connection from IP port N on IP port N` 이고 `VERBOSE` 에서만 나옵니다[4][8]. 기본 설정 검체에서는 이 이벤트가 없다고 해서 연결이 없었다는 뜻이 아닙니다.
- **건수 세기.** `UsePAM yes` 인 기본 설정에서[9][10] 비밀번호 실패는 sshd 의 `Failed password` 줄과 `pam_unix(sshd:auth)` 줄이 따로 남으므로, 두 줄을 같이 세면 실패 건수가 두 배로 보일 가능성이 있습니다.
- **꾸민 줄.** syslog 태그와 facility 는 보낸 쪽이 정하는 값이라, 로컬 사용자가 `sshd` 태그를 단 가짜 줄을 넣을 수 있습니다. 저널이 남아 있으면 `_EXE`·`_COMM` 같은 신뢰 필드로 실제로 보낸 프로그램을 확인합니다([systemd 저널](../../../01-foundations/logging/systemd-journal/index.md)).
- **지우기.** 줄을 지우거나 파일을 비워도 저널, 순환된 옛 파일, 원격 로그 서버, wtmp 에 같은 접속이 남아 있을 수 있습니다. 한 곳에만 있고 다른 곳에 없는 접속이 조작을 가리키는 단서가 됩니다([안티포렌식](../../../04-scenarios/insider/anti-forensics.md)).

## 직접 분석해 보기

**줄 뽑기.** 순환된 파일과 압축본까지 한 번에 봅니다.

```
zgrep -hE 'sshd(-session)?\[[0-9]+\]: (Accepted|Failed|Invalid user)' /mnt/evidence/var/log/auth.log*
zgrep -hE 'sshd(-session)?\[[0-9]+\]: (Accepted|Failed|Invalid user)' /mnt/evidence/var/log/secure*
```

`Accepted` 줄의 원격 주소와 계정, 방식을 묶어 세면 어느 주소가 어느 계정으로 몇 번 들어왔는지 나옵니다. `Failed`·`Invalid user` 가 한 주소에서 몰린 뒤 같은 주소의 `Accepted` 가 이어지면 비밀번호 대입 뒤 성공한 흐름일 가능성이 있습니다. Velociraptor `Linux.Events.SSHBruteforce` 는 같은 계정의 비밀번호 실패가 한 시간 안에 정한 횟수(기본 2)보다 많이 쌓인 뒤 이어진 비밀번호 성공을 찾습니다[17].

**키 맞추기.** 기본 설정의 로그 지문은 `SHA256:` 뒤에 공개 키 값(키 줄의 base64 를 푼 바이트)을 sha256 으로 해시해 base64 로 적고 끝의 `=` 를 뺀 값을 붙인 모양입니다[11][13]. authorized_keys 의 키 줄 하나를 따로 파일로 떼어 `ssh-keygen -l -E sha256 -f 파일` 로 읽으면 지문이 나오므로[16], `Accepted publickey` 줄의 지문과 맞춰 어느 키가 쓰였는지 찾습니다([authorized_keys](authorized-keys.md)). dissect 의 `authlog` 플러그인은 sshd 줄에서 사용자·주소·포트·방식을 뽑고[12], `openssh.authorized_keys` 는 authorized_keys 키마다 지문을 계산합니다[13]. 다만 이 함수가 내는 sha256 지문은 16진 문자열이라서[13], 로그와 맞추려면 16진 값을 바이트로 바꿔 base64 로 적고 끝의 `=` 를 뺍니다.

## 교차 검증

| 함께 볼 것 | 맞춰 볼 점 |
|---|---|
| [로그인 기록](../wtmp-btmp-lastlog.md) | 같은 시각·같은 원격 주소로 터미널 세션이 열렸는지, 로그아웃 시각 |
| [인증 로그](../auth-log.md) | PAM 세션 열고 닫음, systemd-logind 세션 번호 |
| [systemd 저널](../../../01-foundations/logging/systemd-journal/index.md) | 파일이 지워졌을 때 같은 줄, 보낸 프로그램 |
| [authorized_keys](authorized-keys.md) | 로그의 지문에 해당하는 키 줄과 그 파일이 바뀐 시각 |
| [셸 명령 기록](../../execution/shell-history/index.md) | 로그인 뒤 무엇을 했는지 |
| [감사 로그 형식](../../../01-foundations/logging/auditd-format.md) | `USER_LOGIN`, `CRYPTO_KEY_USER`(2404), `CRYPTO_SESSION`(2407) 레코드[15] |

RHEL 9 계열 openssh 패키지는 감사 패치를 넣고 `--with-audit=linux` 로 빌드하므로[9] audit.log 에 SSH 로그인 레코드가 함께 남을 가능성이 있고, 검체의 audit.log 에서 확인합니다. 흐름 전체는 [SSH 로 들어왔나](../../../04-scenarios/intrusion/ssh-intrusion.md)에서 다룹니다.

## 실습

SSH 로 들어온 흔적이 있는 공개 Linux 검체에서 아래 질문을 풀어 봅니다.

1. 검체의 OpenSSH 판과 `LogLevel`·`SyslogFacility` 는 무엇이고, sshd 줄은 어느 파일에 남았습니까?
2. `Accepted` 줄은 몇 개이고, 원격 주소·계정·방식별로 나누면 어떻게 됩니까?
3. 실패가 몰린 주소 중에서 뒤이어 성공한 주소가 있습니까?
4. `Accepted publickey` 줄의 지문은 어느 계정의 authorized_keys 몇 번째 줄과 맞습니까?
5. 같은 접속이 wtmp 와 저널에도 남아 있습니까?

## 참고 문헌

1. OpenSSH portable, auth.c (`auth_log`, `format_method_key`, `allowed_user`). https://github.com/openssh/openssh-portable/blob/master/auth.c
2. OpenSSH portable, packet.c (`sshpkt_fmt_connection_id`, `sshpkt_vfatal`, 끊음 메시지 처리). https://github.com/openssh/openssh-portable/blob/master/packet.c
3. OpenSSH portable, monitor.c · auth2.c (로그 머리말, `[preauth]`·`[postauth]`). https://github.com/openssh/openssh-portable/blob/master/monitor.c , https://github.com/openssh/openssh-portable/blob/master/auth2.c
4. OpenSSH portable, sshd.c · sshd-session.c. https://github.com/openssh/openssh-portable/blob/master/sshd.c , https://github.com/openssh/openssh-portable/blob/master/sshd-session.c
5. OpenSSH portable, session.c. https://github.com/openssh/openssh-portable/blob/master/session.c
6. OpenSSH portable, auth2-pubkeyfile.c · misc.c (`safe_path`). https://github.com/openssh/openssh-portable/blob/master/auth2-pubkeyfile.c
7. OpenSSH portable, sshd_config.5 (`LogLevel`, `MaxAuthTries`, `FingerprintHash`, `SyslogFacility`). https://github.com/openssh/openssh-portable/blob/master/sshd_config.5
8. OpenSSH portable, V_9_6_P1 · V_8_7_P1 태그의 auth.c · auth2.c · packet.c · session.c · sshd.c. https://github.com/openssh/openssh-portable/tree/V_9_6_P1 , https://github.com/openssh/openssh-portable/tree/V_8_7_P1
9. CentOS Stream 9, openssh 패키지 (openssh.spec, openssh-7.7p1-redhat.patch). https://gitlab.com/redhat/centos-stream/rpms/openssh/-/tree/c9s
10. Ubuntu, openssh 패키지 noble-updates (changelog, README.Debian, debian-config.patch). https://git.launchpad.net/ubuntu/+source/openssh/tree/debian?h=ubuntu/noble-updates
11. log2timeline plaso, plaso/parsers/text_plugins/syslog.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/syslog.py
12. fox-it dissect.target, dissect/target/plugins/os/unix/log/auth.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/auth.py
13. fox-it dissect.target, dissect/target/plugins/apps/ssh/ssh.py (`calculate_fingerprints`) · openssh.py (`authorized_keys`). https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/ssh/ssh.py , https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/apps/ssh/openssh.py
14. Velocidex velociraptor, artifacts/definitions/Linux/Syslog/SSHLogin.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Syslog/SSHLogin.yaml
15. linux-audit, audit-documentation specs/messages/message-dictionary.csv. https://github.com/linux-audit/audit-documentation/blob/main/specs/messages/message-dictionary.csv
16. OpenSSH portable, ssh-keygen.1. https://github.com/openssh/openssh-portable/blob/master/ssh-keygen.1
17. Velocidex velociraptor, artifacts/definitions/Linux/Events/SSHBruteforce.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Events/SSHBruteforce.yaml
