---
title: "인증 로그"
parent: "아티팩트 · 로그인과 계정"
nav_order: 340
---

# 인증 로그 (auth.log·secure)

로그인·권한 전환·계정 변경처럼 인증과 관련된 syslog 메시지를 rsyslog 가 모아 쓰는 텍스트 파일이고, Ubuntu 에서는 `/var/log/auth.log`, RHEL 에서는 `/var/log/secure` 입니다.

## 무엇을 기록하나 · 왜 생기나

인증 로그는 따로 정해진 형식이 있는 파일이 아닙니다. 여러 프로그램이 syslog 의 `auth` 나 `authpriv` 분야 (facility)로 보낸 메시지를 rsyslog 가 설정 규칙에 따라 한 파일로 모은 결과입니다[1][2]. 그래서 어떤 줄이 이 파일에 들어가는지는 프로그램마다 어느 분야로 보내는지와 배포판의 rsyslog 규칙을 함께 봐야 알 수 있습니다.

이 파일로 들어오는 주요 기록은 다음과 같습니다.

| 보내는 프로그램 | 분야 | 대표 내용 | 자세한 페이지 |
|---|---|---|---|
| sshd | 기본 `AUTH`, RHEL 은 `AUTHPRIV` 로 바꿈[5][7] | 원격 로그인 성공·실패, 접속 끊김 | [sshd 로그](ssh/sshd-logs.md) |
| PAM 모듈(pam_unix 등) | `authpriv` 고정[3] | 인증 실패, 세션 열림·닫힘 | [인증 모듈 (PAM)](../../01-foundations/users-auth/pam.md) |
| sudo | 두 배포판 모두 `authpriv` 로 빌드[8][9] | 허용·거부한 명령 | [sudo·su 사용 기록](sudo-su.md) |
| useradd·usermod·passwd 등 shadow 도구 | `authpriv`[10] | 계정 생성·변경, 암호 변경 | [계정 생성·변경 흔적](account-changes.md) |
| su (util-linux) | `auth`[11] | 사용자 전환 성공·실패 | [sudo·su 사용 기록](sudo-su.md) |
| systemd-logind | `auth`[12] | 로그인 세션 생성·제거 | [SSH](ssh/index.md) |

이 페이지는 파일이 어디에 생기고 줄을 어떻게 읽는지를 다룹니다. 프로그램마다 남기는 문구의 뜻은 위 표의 페이지에서 다룹니다.

## 위치와 버전별 차이

기준 배포판의 rsyslog 기본 설정은 다음과 같습니다.

| 항목 | Ubuntu 24.04 LTS | RHEL 9 계열 |
|---|---|---|
| 인증 파일 규칙 | `auth,authpriv.* /var/log/auth.log`[1] | `authpriv.* action(type="omfile" file="/var/log/secure")`[2] |
| 일반 파일 규칙 | `*.*;auth,authpriv.none -/var/log/syslog`[1] | `*.info;mail.none;authpriv.none;cron.none` → `/var/log/messages`[2] |
| `auth` 분야가 가는 곳 | `auth.log` | `messages` (secure 규칙은 authpriv 만 고른다) |
| 줄 서식 | 서식 지정 없음 → `RSYSLOG_FileFormat`(RFC 3339)[1][21] | `RSYSLOG_TraditionalFileFormat`[2][21] |
| 입력 | imuxsock(로컬 소켓), imklog[1] | imuxsock 소켓 끔(`SysSock.Use="off"`), imjournal 로 저널에서 가져옴[2] |
| 파일 권한 | `$FileOwner syslog`, `$FileGroup adm`, `$FileCreateMode 0640`[1] | 설정 파일에 지정 없음[2] |
| 순환 | `weekly`, `rotate 4`, `compress`, `delaycompress` → `auth.log.1`, `auth.log.2.gz` …[1] | 개별 옵션 없이 전역 `logrotate.conf` 의 `weekly`, `rotate 4`, `dateext` → `secure-YYYYMMDD`, 압축 지시 없음[2][20] |

두 배포판의 차이에서 가장 중요한 점은 RHEL 에서 `auth` 분야 메시지가 secure 로 가지 않는다는 것입니다. util-linux 의 su 는 `auth` 로 보내므로[11] `(to root) alice on pts/1` 같은 성공·실패 줄은 `/var/log/messages` 에 남고, 같은 su 가 부른 PAM 의 `pam_unix(su:session)` 줄은 `authpriv` 라서 secure 에 남습니다[2][3]. systemd-logind 의 `New session …` 줄도 같은 이유로 RHEL 에서는 messages 에 있습니다[2][12]. Ubuntu 는 두 분야를 모두 auth.log 에 모으고 syslog 에서는 뺍니다[1].

Ubuntu 의 adduser 는 자기 기록을 `user` 분야로 보내므로 `/var/log/syslog` 에 남고[13], adduser 가 부른 useradd 의 기록은 `authpriv` 라 auth.log 에 남습니다[10]. 한 번의 계정 생성이 두 파일에 나뉘어 남는 셈입니다.

이 파일은 rsyslog 가 쓰므로 rsyslog 가 없거나 꺼진 시스템에는 생기지 않고, 메시지는 저널에만 남습니다. 분석 대상에서 `/etc/rsyslog.conf` 와 `/etc/rsyslog.d/` 를 먼저 확인하면 규칙을 바꾼 흔적도 함께 볼 수 있습니다. 규칙 문법과 메시지가 rsyslog 로 들어오는 길은 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md) 에서, 순환본 이름과 순서는 [로그 순환 (logrotate)](../../01-foundations/logging/logrotate.md) 에서 다룹니다.

## 구조

한 줄은 시각, 호스트 이름, 태그(보낸 프로그램 이름과 PID), 메시지로 되어 있습니다. 같은 sshd 로그인 성공이 두 배포판에서 이렇게 찍힙니다(만든 예시).

```
Ubuntu 24.04:  2026-03-12T09:15:02.123456+09:00 web01 sshd[2211]: Accepted publickey for alice from 203.0.113.10 port 50122 ssh2: ED25519 SHA256:(생략)
RHEL 9 계열:   Mar 12 09:15:02 web01 sshd[2211]: Accepted publickey for alice from 203.0.113.10 port 50122 ssh2: ED25519 SHA256:(생략)
```

Ubuntu 24.04 의 줄은 RFC 3339 시각으로 시작하고, RHEL 은 달 이름으로 시작합니다[1][2][21]. OpenSSH 9.8 부터 인증 기록을 쓰는 세션 프로세스가 `sshd-session` 으로 갈라져서[18], RHEL 계열에서 이 프로그램이 설치된 판(CentOS Stream 9 의 9.9p1 패키지에 들어 있음[7])이면 태그가 `sshd-session` 일 수 있습니다. 분석 대상에서 `rpm -q openssh-server` 로 판을 확인합니다.

### PAM 줄의 머리

PAM 모듈이 남기는 메시지 앞에는 `모듈(서비스:단계):` 모양의 머리가 붙습니다[3]. 단계는 `auth`, `setcred`, `account`, `session`, `chauthtok` 가운데 하나입니다[3]. 서비스 이름은 PAM 을 부른 프로그램이 정하고, sshd 의 기본 서비스 이름은 `sshd` 입니다[6]. 태그는 PAM 을 부른 프로그램의 이름이 됩니다.

| 줄 (만든 예시) | 뜻 |
|---|---|
| `pam_unix(sshd:session): session opened for user alice(uid=1001) by (uid=0)` | 세션 열림[4] |
| `pam_unix(sshd:session): session closed for user alice` | 세션 닫힘[4] |
| `pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=198.51.100.7  user=alice` | 암호 인증 실패[4] |
| `pam_unix(sshd:auth): 2 more authentication failures; logname= …` | 첫 실패 뒤로 더 이어진 실패 횟수[4] |
| `pam_unix(sshd:auth): check pass; user unknown` | 없는 사용자[4] |

세션 열림 줄의 서식은 `session opened for user %s(uid=%s) by %s(uid=%lu)` 이고, `by` 뒤 이름은 호출한 쪽의 로그인 이름이며 알 수 없으면 빈 문자열이 됩니다[4]. 그래서 sshd 에서는 `by (uid=0)` 처럼 이름 없이 찍힙니다[4][17]. 인증 실패 줄의 `tty=ssh` 는 sshd 가 PAM 에 넘기는 터미널 값이 `ssh` 로 고정되어 있기 때문입니다[6]. 실패 줄의 서식은 `rhost=%s ` 뒤에 `" user="` 를 이어 붙이므로 `rhost=` 값과 `user=` 사이에 공백이 두 칸입니다[4]. 이 공백을 한 칸으로 가정한 정규식은 사용자 이름을 놓칩니다.

## 증거로서 의미

### 증명하는 것

한 줄은 "그 시각에 그 태그를 단 메시지가 `auth` 나 `authpriv` 분야로 rsyslog 에 들어와 이 파일에 쓰였다" 는 기록입니다. sshd 의 `Accepted` 줄과 pam_unix 세션 줄이 짝을 이루면 그 시각에 그 원격 주소에서 그 계정으로 인증이 성공하고 세션이 열렸다고 쓸 수 있습니다. PAM 머리의 서비스 이름은 인증이 어느 경로(sshd, sudo, su, login 등)로 일어났는지를 알려 줍니다.

### 증명하지 못하는 것

태그가 실제 그 프로그램이라는 보장은 없습니다. syslog 에서는 누구나 어느 분야로든 메시지를 보낼 수 있어서, 로컬 사용자가 `sshd` 태그를 단 줄을 이 파일에 남길 수 있습니다([syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)). 실제로 보낸 프로세스는 저널의 `_COMM`, `_PID` 처럼 밑줄로 시작하는 필드로 확인하고, 이 필드는 클라이언트가 바꿀 수 없습니다[14]. 반대로 `SYSLOG_IDENTIFIER` 와 `SYSLOG_FACILITY` 는 저널이 값을 검증하지 않습니다[14].

기록이 빠짐없이 남았다는 뜻도 아닙니다. 저널과 imjournal 의 속도 제한을 넘은 메시지는 버려집니다([syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md)). sshd 는 기본 등급에서 연결 시작이나 세션 종류를 남기지 않으므로([sshd 로그](ssh/sshd-logs.md)), 이 파일만으로는 세션이 대화형이었는지 알 수 없습니다. 세션 안에서 무엇을 했는지도 이 파일에는 없습니다.

## 시각 해석

Ubuntu 24.04 의 줄에는 연도·마이크로초·UTC 오프셋이 있어서 적힌 오프셋을 빼면 UTC 가 됩니다. RHEL 의 옛 서식에는 연도와 시간대가 없고 초까지만 있어서, 기록한 시스템의 현지 시각으로 보고 연도를 추정해야 합니다. 도구마다 연도를 추정하는 방식과 로컬 줄의 시각이 보낸 시각인지 받은 시각인지는 [syslog 형식과 rsyslog](../../01-foundations/logging/syslog-rsyslog.md) 의 "시각 해석" 에서 다룹니다. 시간대는 [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md) 에서 확인합니다.

RHEL 은 로컬 메시지를 imjournal 로 저널에서 가져오므로[2], 줄의 시각이 저널 항목의 어느 시각을 따르는지는 분석 대상의 저널 `__REALTIME_TIMESTAMP` 와 같은 메시지를 맞대어 확인합니다. 순환본의 `dateext` 날짜는 파일이 덮는 기간이 아니라 회전한 날입니다([로그 순환 (logrotate)](../../01-foundations/logging/logrotate.md)).

## 함정과 한계

- RHEL 에서 secure 만 보면 su 성공·실패와 logind 세션 줄을 놓칩니다. secure 와 messages 를 함께 봅니다.
- 한 번의 암호 실패가 sshd 의 `Failed password …` 줄과 pam_unix 의 `authentication failure` 줄로 두 번 찍힐 수 있습니다. 두 코드가 각각 기록하므로, 실패 횟수를 셀 때는 한 종류의 줄만 셉니다.
- 텍스트 파일이라 줄을 지우거나 파일을 비우기 쉽습니다. 같은 메시지는 저널에도 들어가므로, 저널이 디스크에 남는 시스템이면 두 쪽을 맞대어 빠진 구간을 찾습니다([흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md)).
- PAM 설정이나 모듈이 바뀌면 인증은 되는데 기록이 남지 않을 수 있습니다. 세션 줄이 사라진 구간이 있으면 [PAM 모듈 변조](../persistence/pam-backdoor.md) 를 확인합니다.
- dissect.target 의 `authlog` 는 서비스별로 필드를 뽑지만 정규식에 한계가 있습니다[17]. sudo 줄은 `TTY=` 값이 `pts/0` 모양이고 `PWD=`·`USER=`·`COMMAND=` 가 차례로 붙어야 필드가 나오므로, `TTY=unknown` 이거나 `GROUP=` 이 낀 줄은 필드가 빕니다. sshd 의 인증 방식은 줄에 `password` 가 없으면 모두 publickey 로 분류하므로 `keyboard-interactive/pam` 도 publickey 로 나옵니다. su 파서는 소문자 `failed` 와 `Successful` 을 찾으므로 util-linux su 의 `FAILED SU` 줄은 결과가 비고, ISO 시각 판별은 `+hh:mm` 오프셋만 받아서 `-05:00` 처럼 음수 오프셋인 파일은 읽히지 않을 가능성이 있습니다[17].
- Velociraptor 의 `Linux.Syslog.SSHLogin` 은 옛 서식 시각만 받는 Grok 식을 쓰고 태그가 `sshd` 인 줄만 고르므로[19], Ubuntu 24.04 의 RFC 3339 줄과 `sshd-session` 태그 줄은 빠질 가능성이 있습니다.
- plaso 는 `sshd` 와 `sshd-session` 을 모두 sshd 로 읽지만 인증 방식은 `password` 와 `publickey` 만 구조화합니다[18].

## 직접 분석해 보기

### 헥스로 한 번

RHEL 옛 서식의 pam_unix 인증 실패 줄을 바이트로 보면 다음과 같습니다(명세의 서식 문자열로 만든 예시).

```
00000000: 4d61 7220 3132 2030 393a 3134 3a35 3720  Mar 12 09:14:57 
00000010: 7765 6230 3120 7373 6864 5b32 3230 315d  web01 sshd[2201]
00000020: 3a20 7061 6d5f 756e 6978 2873 7368 643a  : pam_unix(sshd:
00000030: 6175 7468 293a 2061 7574 6865 6e74 6963  auth): authentic
00000040: 6174 696f 6e20 6661 696c 7572 653b 206c  ation failure; l
00000050: 6f67 6e61 6d65 3d20 7569 643d 3020 6575  ogname= uid=0 eu
00000060: 6964 3d30 2074 7479 3d73 7368 2072 7573  id=0 tty=ssh rus
00000070: 6572 3d20 7268 6f73 743d 3139 382e 3531  er= rhost=198.51
00000080: 2e31 3030 2e37 2020 7573 6572 3d61 6c69  .100.7  user=ali
00000090: 6365 0a                                  ce.
```

0x00 부터 15바이트가 시각이고 연도와 시간대가 없습니다. 0x10 의 `web01` 이 호스트, `sshd[2201]:` 가 태그입니다. 0x86~0x87 의 `20 20` 이 `rhost=` 값 뒤의 두 칸 공백이고, 줄은 `0a` 로 끝납니다. `logname=` 뒤가 바로 공백(0x57 의 `20`)인 것은 로그인 이름이 비어 있다는 뜻입니다.

### 공개 도구로 한 번

```
# 현재 파일과 순환본(압축 포함)을 오래된 것부터 모아 보기 (rotate 4 기준)
zcat -f /mnt/evidence/var/log/auth.log.4.gz /mnt/evidence/var/log/auth.log.3.gz /mnt/evidence/var/log/auth.log.2.gz /mnt/evidence/var/log/auth.log.1 /mnt/evidence/var/log/auth.log | grep -E 'sshd|pam_unix'

# RHEL: secure 와 messages 를 함께
grep -hE 'sshd|pam_unix|\(to [^)]+\)|New session' /mnt/evidence/var/log/secure* /mnt/evidence/var/log/messages*

# 저널에서 같은 분야만 (4=auth, 10=authpriv)
journalctl -D /mnt/evidence/var/log/journal SYSLOG_FACILITY=10 -o verbose
```

dissect.target 은 `/var/log/auth.log*` 와 `/var/log/secure*` 를 모아 `authlog`(별칭 `securelog`) 로 읽고 압축본도 엽니다[17]. plaso 의 `syslog` 파서는 sshd 줄의 성공·실패와 방식을 필드로 나눕니다[18]. 수집할 때 ForensicArtifacts 의 `LinuxAuthLogs` 정의는 `/var/log/auth*` 와 `/var/log/secure*` 를 잡으므로[16], RHEL 의 su·logind 줄이 든 `/var/log/messages*` 는 따로 모아야 합니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [로그인 기록 (wtmp·btmp·lastlog)](wtmp-btmp-lastlog.md) | `Accepted` 와 같은 시각에 pty 세션 레코드가 있는지, 암호 실패가 btmp 에도 있는지 |
| [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) | 같은 메시지의 `_COMM`·`_PID` 로 보낸 프로세스 확인, 파일에서 빠진 구간 |
| [감사 로그 형식 (auditd)](../../01-foundations/logging/auditd-format.md) | `USER_AUTH`(1100), `USER_ACCT`(1101), `CRED_ACQ`(1103), `USER_START`(1105), `USER_END`(1106), `USER_LOGIN`(1112), `USER_CMD`(1123)[15] |
| [셸 명령 기록](../execution/shell-history/index.md) | 세션이 열린 뒤 친 명령 |
| [SSH 로 들어왔나](../../04-scenarios/intrusion/ssh-intrusion.md) | 원격 로그인 조사 흐름 전체 |

## 실습

NIST CFReDS 등에 공개된 Linux 디스크 이미지로 다음 질문을 풀어 봅니다.

1. 분석 대상의 rsyslog 설정에서 `auth` 와 `authpriv` 는 각각 어느 파일로 가는가? 기본 설정과 다른 규칙이 `/etc/rsyslog.d/` 에 있는가?
2. 줄 서식이 RFC 3339 인가, 옛 서식인가? 옛 서식이면 순환본마다 연도를 무엇으로 정했는가?
3. `session opened for user` 줄의 서비스 이름별 건수는 몇인가? sshd 세션 가운데 `session closed` 짝이 없는 것이 있는가?
4. 암호 인증 실패가 가장 많은 원격 주소는 어디이고, 그 주소에서 성공한 로그인이 있는가?
5. 인증 로그의 마지막 줄 시각과 저널의 같은 분야 마지막 항목 시각이 맞는가?

## 참고 문헌

1. Ubuntu rsyslog 패키지(noble-updates), debian/50-default.conf·rsyslog.conf·rsyslog.logrotate. https://git.launchpad.net/ubuntu/+source/rsyslog/tree/debian?h=ubuntu/noble-updates
2. CentOS Stream 9 rsyslog 패키지, rsyslog.conf·rsyslog.log. https://gitlab.com/redhat/centos-stream/rpms/rsyslog/-/tree/c9s
3. Linux-PAM, libpam/pam_syslog.c. https://github.com/linux-pam/linux-pam/blob/master/libpam/pam_syslog.c
4. Linux-PAM, modules/pam_unix/support.c·pam_unix_sess.c. https://github.com/linux-pam/linux-pam/tree/master/modules/pam_unix
5. OpenSSH, sshd_config.5. https://github.com/openssh/openssh-portable/blob/master/sshd_config.5
6. OpenSSH, auth-pam.c·configure.ac·servconf.c. https://github.com/openssh/openssh-portable/tree/master
7. CentOS Stream 9 openssh 패키지, openssh-7.7p1-redhat.patch·openssh.spec. https://gitlab.com/redhat/centos-stream/rpms/openssh/-/tree/c9s
8. Ubuntu sudo 패키지(noble-updates), debian/rules. https://git.launchpad.net/ubuntu/+source/sudo/tree/debian?h=ubuntu/noble-updates
9. CentOS Stream 9 sudo 패키지, sudo.spec. https://gitlab.com/redhat/centos-stream/rpms/sudo/-/tree/c9s
10. shadow, lib/io/syslog.h. https://github.com/shadow-maint/shadow/tree/master/lib
11. util-linux, login-utils/su-common.c. https://github.com/util-linux/util-linux/blob/master/login-utils/su-common.c
12. systemd v255, src/login/logind.c·logind-session.c. https://github.com/systemd/systemd/blob/v255/src/login/logind.c
13. Ubuntu adduser 패키지(noble), AdduserLogging.pm. https://git.launchpad.net/ubuntu/+source/adduser/tree/?h=ubuntu/noble
14. systemd, man/systemd.journal-fields.xml. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
15. linux-audit, audit-documentation specs/messages/message-dictionary.csv. https://github.com/linux-audit/audit-documentation/blob/main/specs/messages/message-dictionary.csv
16. ForensicArtifacts, artifacts/data/linux.yaml. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
17. fox-it dissect.target, dissect/target/plugins/os/unix/log/auth.py·helpers.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/auth.py
18. plaso, plaso/parsers/text_plugins/syslog.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/syslog.py
19. Velociraptor, artifacts/definitions/Linux/Syslog/SSHLogin.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Syslog/SSHLogin.yaml
20. logrotate 3.18.0, examples/logrotate.conf. https://github.com/logrotate/logrotate/tree/3.18.0/examples
21. rsyslog 문서, omfile.rst·templates.rst. https://github.com/rsyslog/rsyslog-doc/tree/main/source/configuration
