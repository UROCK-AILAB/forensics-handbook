---
title: "누가 그 명령을 실행했나"
parent: "시나리오 · 사용자"
nav_order: 1120
---

# 누가 그 명령을 실행했나 (User Attribution)

명령 하나를 사람 하나에 잇는 조사입니다. Linux 기록이 곧바로 알려 주는 것은 계정(UID·이름)과 로그인 세션까지이고, 그 뒤의 사람은 로그인 경로(SSH 키·원격 주소·콘솔)로 좁힙니다.

## 조사 질문

"이 명령(또는 이 프로세스, 이 파일 변경)을 어느 계정이 실행했나" 와 "그 계정으로 로그인한 사람이 누구인가" 는 서로 다른 질문입니다. 앞의 질문은 감사 로그·인증 로그·셸 기록으로 답할 수 있고, 뒤의 질문은 SSH 키 지문이나 원격 주소처럼 시스템 밖의 증거와 이어야 답이 나옵니다.

이 조사의 중심은 root 나 서비스 계정처럼 여럿이 함께 쓰는 계정으로 실행된 명령을 처음 로그인한 계정으로 되돌려 잇는 일입니다. 이 쪽은 그 사슬을 따라가는 순서를 다루고, 각 기록의 형식은 해당 쪽으로 링크합니다.

## 먼저 확인할 것

**시스템 기본 정보.** 배포판과 판([배포판과 버전](../../02-artifacts/system-info/os-release.md)), 시간대([호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md)), 부팅 구간([부팅과 종료 기록](../../02-artifacts/system-info/boot-shutdown.md))을 먼저 정합니다. 감사 세션 번호(`ses`)는 커널이 메모리에 둔 카운터를 0 에서부터 하나씩 올린 값이라[1] 부팅마다 작은 번호부터 다시 시작할 가능성이 있고, 그래서 번호를 비교할 때는 늘 부팅 구간을 함께 봅니다.

**계정 목록.** `/etc/passwd` 로 UID 와 이름을 잇고, 지운 계정과 UID 재사용을 확인합니다([UID·GID 와 사용자 이름 잇기](../../01-foundations/value-decoding/uid-gid.md)). `useradd` 는 기본으로 `UID_MIN` 이상이면서 다른 모든 사용자보다 큰 가장 작은 값을 주고, `-o` 를 쓰면 이미 있는 UID 로도 계정을 만듭니다[20]. 가장 큰 UID 의 계정을 지운 뒤 새 계정을 만들면 같은 UID 를 받을 수 있으므로, 옛 기록의 UID 를 지금의 passwd 로 풀면 다른 사람 이름이 나올 수 있습니다. 두 기준 배포판의 `UID_MIN` 은 1000 입니다[18][19].

**기록이 켜져 있었는지.** 어떤 기록이 없다는 사실은 그 기록 장치가 꺼져 있었을 때 아무 의미가 없습니다. 다음을 검체에서 확인합니다.

- 감사 데몬 설치 여부와 규칙(`/etc/audit/rules.d/`), 규칙에 `execve` 가 있는지([감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md))
- 로그인 진입점의 PAM 설정에 `pam_loginuid` 가 있는지(아래 표)
- sudoers 의 `log_input`·`log_output`·`log_subcmds`·`logfile` 설정([sudo 설정 (sudoers)](../../01-foundations/users-auth/sudoers.md))
- sshd 의 `LogLevel`(기본 `INFO`, 키 파일 위치까지 남기려면 `VERBOSE`)[15]
- 셸의 `HISTFILE`·`HISTTIMEFORMAT` 설정([셸 명령 기록](../../02-artifacts/execution/shell-history/index.md))
- 저널 영구 저장 여부([systemd 저널](../../01-foundations/logging/systemd-journal/index.md))와 프로세스 회계 설치 여부([프로세스 회계](../../02-artifacts/execution/process-accounting.md))

**로그인 ID 가 믿을 만한지.** 감사 로그의 `auid` 는 로그인 프로그램이 PAM 세션을 열 때 `pam_loginuid` 가 `/proc/self/loginuid` 에 써 넣은 값입니다[5]. PAM 을 쓰는 진입점 프로그램이 모두 세션 단계에 `pam_loginuid` 를 `required` 로 두어야 `auid` 로 찾은 결과가 정확합니다[8].

| PAM 서비스 | Ubuntu 24.04 LTS | RHEL 9 |
|---|---|---|
| sshd | `session required pam_loginuid.so`[18] | `session required pam_loginuid.so`[19] |
| login(콘솔) | `session required pam_loginuid.so`[18] | 검체의 `/etc/pam.d/login` 에서 확인 |

PAM 구조와 모듈 순서는 [인증 모듈 (PAM)](../../01-foundations/users-auth/pam.md) 에서 다룹니다. 키 입력까지 남기는 `pam_tty_audit` 는 Ubuntu 24.04 의 기본 sshd·login 파일과 RHEL 9 의 기본 sshd 파일에 적혀 있지 않고[18][19], 커널은 기본으로 어떤 터미널의 입력도 감사하지 않습니다[5]. 이 파일들이 불러오는 공통 파일(`common-session`, `password-auth` 등)은 검체에서 확인합니다. 누군가 이 모듈을 켜 두었다면 `aureport --tty` 로 키 입력 기록을 볼 수 있습니다[8].

## 볼 아티팩트와 순서

### 명령을 사람에게 잇는 식별자

명령 하나를 로그인까지 되짚는 일은 아래 식별자를 기록끼리 맞춰 보는 일입니다.

| 식별자 | 정하는 곳 · 바뀌는 때 | 남는 곳 |
|---|---|---|
| 실제 UID (uid) | 로그인 때 정해지고 su·sudo 가 대상 사용자로 바꿉니다 | 감사 `uid=`[9], 저널 `_UID=`[17], `/proc/PID/status` 의 `Uid:` 첫 값[26], Volatility 3 `linux.pslist` 의 UID 열[23] |
| 유효 UID (euid) | setuid 프로그램을 실행하거나 권한을 바꿀 때 | 감사 `euid=`[9], `Uid:` 둘째 값[26], `linux.pslist` 의 EUID 열[23] |
| 로그인 UID (auid, loginuid) | `pam_loginuid` 가 로그인 세션을 열 때 한 번 씁니다. 이미 정해진 값을 바꾸려면 `CAP_AUDIT_CONTROL` 이 필요하고, 변경 금지 기능을 켜면 아예 바뀌지 않습니다[1][7] | 감사 `auid=`[9], 저널 `_AUDIT_LOGINUID=`[17], `/proc/PID/loginuid`[2] |
| 감사 세션 ID (ses) | 로그인 UID 를 유효한 값으로 쓸 때 커널이 카운터를 하나 올려 줍니다[1] | 감사 `ses=`[9], 저널 `_AUDIT_SESSION=`[17], `/proc/PID/sessionid`(읽기 전용)[2] |
| logind 세션 ID | systemd-logind 가 세션을 만들 때 리더 프로세스의 감사 세션 ID 를 그대로 쓰려 하고, 없거나 이미 쓰인 번호면 `c1`, `c2` … 처럼 따로 번호를 매깁니다[16] | 저널 `_SYSTEMD_SESSION=`[17], `New session N of user X.` 줄[16], `/run/systemd/sessions/N`[16] |
| 터미널 (tty) | 로그인 프로그램·sshd 가 세션마다 할당하고, 번호는 세션이 끝나면 다시 씁니다 | wtmp `ut_line`, sudo `TTY=`[11], su `on pts/0`[12], 감사 `tty=`[9], pacct `ac_tty` |
| `SUDO_USER`·`SUDO_UID` 등 | sudo 가 실행하는 명령의 환경 변수로 넣습니다[11] | `/proc/PID/environ`[26], Volatility 3 `linux.envars`[23] |
| `PKEXEC_UID` | pkexec 가 실행하는 명령의 환경 변수로 넣고, sudo 와 맞추려고 `SUDO_UID`·`SUDO_GID` 도 함께 넣습니다[14] | `/proc/PID/environ` |

로그인 UID 가 정해지지 않은 프로세스는 `auid=4294967295` 로 적히고, 감사 규칙에서는 `unset`, `-1`, `4294967295` 가 같은 뜻입니다[7]. `pam_loginuid` 를 sudo·su 에 쓰면 안 되는 까닭은 로그인 UID 가 방금 바꾼 계정으로 바뀌어 모듈의 목적이 없어지기 때문이고[5], 그래서 su·sudo 뒤에도 `auid` 는 처음 로그인한 계정을 그대로 가리킵니다. 로그인 UID 를 새로 쓸 때마다 커널은 `pid=… uid=… old-auid=… auid=… tty=… old-ses=… ses=… res=…` 모양의 LOGIN 레코드를 감사 로그에 남깁니다(감사가 켜져 있을 때)[1].

### 기록을 보는 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 감사 로그 실행 레코드 | 실행 파일·인수·`uid`·`euid`·`auid`·`ses`·`tty` | [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md), [감사 로그 형식](../../01-foundations/logging/auditd-format.md) |
| 2 | sudo·su·pkexec 줄, PAM 세션 줄 | 권한을 바꾼 계정과 대상 계정, 터미널, 작업 폴더, 명령 | [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md), [인증 로그](../../02-artifacts/logins/auth-log.md) |
| 3 | 셸 기록 파일 | 대화형 셸에서 친 명령과 순서(시각 줄이 있으면 시각) | [셸 명령 기록](../../02-artifacts/execution/shell-history/index.md) |
| 4 | 저널의 신뢰 필드와 logind 줄 | `_UID`·`_AUDIT_LOGINUID`·`_AUDIT_SESSION`·`_SYSTEMD_SESSION`, 세션 시작·끝 | [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) |
| 5 | 프로세스 회계 | 인수 없는 실행 이름·실제 UID·터미널·시작 시각 | [프로세스 회계](../../02-artifacts/execution/process-accounting.md) |
| 6 | 로그인 기록과 sshd 줄 | 세션을 연 계정·터미널·원격 주소·키 지문 | [로그인 기록](../../02-artifacts/logins/wtmp-btmp-lastlog.md), [SSH](../../02-artifacts/logins/ssh/index.md) |
| 7 | 라이브이면 `/proc`, 메모리 이미지이면 Volatility 3 | 실행 중인 프로세스의 UID·로그인 UID·환경 변수 | [실행 중인 프로세스 (/proc)](../../02-artifacts/execution/proc.md), [메모리 분석](../../03-techniques/analysis/memory-analysis.md) |

## 분석 흐름

1. **범위를 정합니다.** 문제의 명령·프로세스·파일 변경이 어느 호스트에서 언제(UTC) 일어났는지 적고, 그 시각이 어느 부팅 구간에 드는지 정합니다.

2. **명령을 프로세스로 찾습니다.** 감사 로그가 있으면 그 시각의 실행 레코드에서 `exe`, 인수, `uid`·`euid`·`auid`·`ses`·`tty` 를 읽습니다. `ausearch` 의 `-ua` 는 `uid`·`euid`·`auid` 가운데 하나라도 맞는 이벤트를, `-ul` 은 `auid` 로, `--session` 은 로그인 세션 ID 로, `-tm` 은 터미널로 찾습니다[8]. 감사 로그가 없으면 셸 기록과 프로세스 회계로 좁힙니다.

3. **`uid` 와 `auid` 가 다른지 봅니다.** `uid=0` 인데 `auid` 가 1000 이상의 사람 계정이면, 그 사람이 로그인한 세션에서 권한을 올려 실행한 명령입니다. 감사 규칙에서 사람 계정만 고르는 조건은 `UID_MIN` 이 1000 일 때 `-F auid>=1000 -F auid!=unset` 이고[7][10], 로그인한 사람이 root 권한으로 남의 홈 파일을 건드린 경우는 `-F uid=0 -F auid>=1000 -F auid!=unset -C auid!=obj_uid` 로 잡을 수 있습니다[10]. 터미널 값이 `cron` 처럼 데몬 이름이면 사람이 대화형으로 친 명령이 아닐 가능성이 있습니다[8].

4. **권한을 바꾼 기록을 되짚습니다.** 같은 시각대의 sudo·su·pkexec 줄과 PAM 세션 줄을 찾습니다. 기록마다 "원래 사용자" 를 정하는 방법이 달라서, 같은 명령에서도 서로 다른 이름이 찍힐 수 있습니다.

   | 기록 | 원래 사용자 칸에 들어가는 값 |
   |---|---|
   | sudo 줄의 username | sudo 를 실행한 사용자의 로그인 이름. 단 root 가 `SUDO_USER` 를 가진 채 sudo 를 다시 부르면 sudoers 는 그 값을 실제 사용자로 씁니다[11] |
   | su 줄 `(to 대상) 원래 on 터미널` | su 를 부른 프로세스의 실제 UID 의 이름입니다[12][13]. 성공이면 앞이 비고, 실패면 `FAILED SU ` 가 붙습니다[12] |
   | `pam_unix(서비스:session): session opened for user 대상(uid=N) by 이름(uid=M)` | `by` 뒤 이름은 `getlogin()` 결과이고[6], glibc 의 Linux 판 `getlogin` 은 먼저 `/proc/self/loginuid` 를 읽어 그 UID 의 이름을 돌려줍니다[4]. 괄호 안 숫자는 PAM 을 부른 프로세스의 실제 UID 입니다[6] |
   | pkexec 줄 `원래: 메시지 [USER=대상] [TTY=…] [CWD=…] [COMMAND=…]` | pkexec 를 실행한 사용자 이름. 터미널이 없으면 `TTY=unknown` 입니다[14] |

   그래서 alice 가 `sudo su -` 로 root 셸을 열면 su 줄의 원래 사용자는 `root`, PAM 줄은 `by alice(uid=0)` 로 찍힐 가능성이 있습니다(만든 예시). 줄 형식과 로그 파일 위치는 [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md) 에 있습니다.

5. **셸 안에서 친 명령을 찾습니다.** `sudo -s`·`sudo -i`·`su` 로 연 셸 안의 명령은 sudo 줄에 남지 않습니다. sudo 는 `log_subcmds` 를 켰을 때만 그 셸이 실행한 명령을 따로 기록하고[11], 두 기준 배포판의 기본 sudoers 에는 이 설정이 없습니다. 이런 명령은 감사 로그의 `auid`·`ses` 와 셸 기록 파일에서 찾습니다. bash 는 기록을 `HOME` 아래 `~/.bash_history` 에 저장하고[21], `su` 는 옵션 없이 쓰면 `HOME`·`SHELL` 을 대상 계정 값으로 바꾸지만 `-m`·`-p` 를 쓰면 바꾸지 않습니다[12]. 따라서 `su -m` 으로 연 root 셸의 명령은 원래 사용자 홈의 기록 파일에 쌓일 가능성이 있고, `su`·`su -`·`sudo -i` 의 명령은 `/root` 쪽 기록 파일에 들어갑니다.

6. **프로세스를 세션에 잇습니다.** 한 부팅 구간 안에서 감사 `ses=N`, 저널 `_AUDIT_SESSION=N`, logind 세션 N 은 같은 로그인 세션을 가리킬 가능성이 큽니다. systemd-logind 가 세션 ID 를 감사 세션 ID 와 맞추려 하기 때문입니다[16]. 새 세션 줄은 RHEL 9(systemd 252)와 Ubuntu 24.04(systemd 255) 모두 `New session N of user X.` 이고, 끝날 때 `Session N logged out. Waiting for processes to exit.` 와 `Removed session N.` 이 남습니다[16]. 터미널로 이을 때는 모양을 먼저 맞춥니다. 커널은 터미널 이름을 드라이버 이름에 번호를 붙여 만들어서 감사 레코드에는 `tty=pts0` 처럼 빗금이 없고[3], sudo 줄과 로그인 기록에는 `pts/0` 으로 적힙니다[11].

7. **세션을 로그인에 잇습니다.** 세션이 시작된 시각의 로그인 기록과 sshd 인증 줄을 찾습니다. sshd 는 `Accepted publickey for 계정 from 주소 port 번호 ssh2: 키형식 지문` 모양으로 계정·원격 주소·키 지문을 남기고[15], 지문은 기본으로 SHA256 입니다[15]. `LogLevel` 이 `VERBOSE` 이상이면 `Accepted key 키형식 지문 found at 파일:줄번호` 가 더 남아 `authorized_keys` 의 몇 번째 줄 키로 들어왔는지까지 알 수 있습니다[15]. `ssh-keygen -l -f 공개키파일` 로 공개 키의 지문을 계산해 로그의 지문과 대조합니다[15]. 침입 여부를 따지는 흐름은 [SSH 로 들어왔나](../intrusion/ssh-intrusion.md) 에 있습니다.

8. **로그인을 사람에게 잇습니다.** 키 지문은 `authorized_keys` 의 해당 줄(주석 칸)과 키를 발급·보관한 사람으로, 원격 주소는 네트워크 장비와 상대 호스트의 기록으로 이어 갑니다. 여기서부터는 Linux 밖의 증거입니다. 결론은 외부 증거가 없으면 "계정·세션·로그인 경로" 까지만 씁니다.

라이브 시스템이나 메모리 이미지가 있으면 실행 중인 프로세스에서 곧바로 사슬을 읽을 수 있습니다. `/proc/PID/loginuid` 와 `/proc/PID/sessionid` 가 로그인 UID 와 감사 세션 ID 를 보여 주고[2], `/proc/PID/environ` 은 `SUDO_USER`, `PKEXEC_UID`, 그리고 sshd 가 넣은 `SSH_CLIENT`(원격 주소·원격 포트·로컬 포트)와 `SSH_CONNECTION`(원격 주소·원격 포트·로컬 주소·로컬 포트)을 보여 줍니다[11][14][15]. 메모리 이미지에서는 Volatility 3 의 `linux.bash` 가 `bash`·`sh`·`dash` 프로세스에서 명령 기록을 꺼내지만 출력 열은 PID·Process·CommandTime·Command 뿐이라[23], 같은 PID 를 `linux.pslist`(UID·EUID 열)와 `linux.envars`(KEY·VALUE 열)에 맞춰 계정을 정합니다[23].

## 흔한 오판

- **"root 가 실행했다" 로 끝냅니다.** `uid=0` 이어도 `auid` 가 사람 계정이면 그 계정으로 로그인한 세션에서 권한을 올려 실행한 명령입니다[1][5].
- **`/root/.bash_history` 를 한 사람의 기록으로 봅니다.** `sudo -i`·`su`·`su -` 로 root 셸을 연 여러 관리자의 명령이 한 파일에 섞입니다. sudo 의 기본 `env_reset` 은 `HOME` 을 대상 사용자 값으로 두기 때문입니다[11].
- **도구가 붙인 사용자 칸을 실행자로 읽습니다.** dissect.target 은 기록 파일을 그 파일이 있는 홈 폴더의 주인 계정에 붙입니다[24]. Velociraptor `Linux.Events.ProcessExecutions` 의 `UserId`·`User` 열은 `Summary.Actor.Primary` 에서 오고[22], go-libaudit 는 이 칸에 `auid` 를 넣습니다[25]. 곧 이 열은 실제로 실행한 UID 가 아니라 로그인 계정입니다.
- **su 줄의 원래 사용자와 PAM 줄의 `by` 이름을 같은 값으로 봅니다.** su 는 실제 UID 의 이름을[13], PAM 줄은 로그인 UID 의 이름을 적으므로[4][6] `sudo su -` 같은 경우 두 값이 다릅니다. dissect.target 의 PAM 줄 정규식은 `by (uid=0)` 처럼 이름이 빈 모양만 받도록 짜여 있어서[24], `by alice(uid=1000)` 모양의 줄에서는 PAM 필드를 뽑지 못합니다. 원래 메시지를 함께 봅니다.
- **환경 변수의 `SUDO_UID` 만 보고 sudo 로 판단합니다.** pkexec 도 같은 변수를 넣습니다[14]. `/proc/PID/environ` 은 프로그램을 실행할 때의 처음 환경이라, 실행 뒤에 바뀐 값은 보이지 않습니다[26].
- **세션 번호를 부팅을 건너 비교합니다.** `ses` 는 부팅마다 다시 작은 번호부터 올라갈 가능성이 있습니다[1]. logind 세션 번호도 감사 세션 ID 를 따라가므로 같은 문제가 있습니다. 저널의 `_BOOT_ID` 나 로그인 기록의 재부팅 레코드로 구간을 먼저 나눕니다.
- **터미널 번호만으로 잇습니다.** `pts/0` 은 세션이 끝나면 다음 세션이 다시 씁니다. 시각 범위와 함께 맞춥니다.
- **기록이 없으면 안 했다고 읽습니다.** 비대화형 셸(스크립트, `ssh 호스트 명령`)은 기록 파일에 남기지 않습니다. bash 의 기록 기능은 대화형 셸에서만 기본으로 켜지기 때문입니다[21]. sshd 도 강제 명령이 아닌 원격 명령 문자열은 사생활 보호를 이유로 적지 않습니다[15]. 감사 데몬이 없었거나 저널이 메모리에만 있었던 경우도 같습니다.
- **로그인 UID 는 절대 바뀌지 않는다고 봅니다.** 이미 정해진 로그인 UID 는 `CAP_AUDIT_CONTROL` 이 있으면 바꿀 수 있고, `auditctl --loginuid-immutable` 을 켜야 바꿀 수 없게 됩니다[1][7]. 바뀌면 커널이 `old-auid=` 와 `auid=` 를 함께 적은 LOGIN 레코드를 남기므로, 의심스러우면 그 레코드를 찾습니다[1]. 기록을 지우거나 끈 흔적은 [흔적을 지웠나](../insider/anti-forensics.md) 에서 다룹니다.
- **다른 기계에서 감사 로그의 숫자를 이름으로 풉니다.** 보강되지 않은(unenriched) 감사 로그를 `ausearch -i` 로 풀면 분석하는 기계의 계정 정보로 UID 를 이름으로 바꿉니다[8]. 이름 풀이는 검체의 `/etc/passwd` 로 합니다([감사 로그 형식](../../01-foundations/logging/auditd-format.md)).

## 보고서 문장 예

아래 값은 모두 만든 예시입니다(사용자 alice, 호스트 web01, 주소 203.0.113.25). 한 부팅 구간 안에서 기록이 다음처럼 이어진 경우입니다. syslog 머리 부분은 줄였습니다.

```
# 만든 예시
sshd[2101]: Accepted publickey for alice from 203.0.113.25 port 51522 ssh2: ED25519 SHA256:…
systemd-logind[812]: New session 7 of user alice.
sudo: alice : TTY=pts/0 ; PWD=/home/alice ; USER=root ; COMMAND=/usr/bin/tar czf /tmp/d.tgz /srv/data
sudo: pam_unix(sudo:session): session opened for user root(uid=0) by alice(uid=1001)
type=SYSCALL msg=audit(1709514131.204:8812): … pid=2230 auid=1001 uid=0 gid=0 euid=0 … tty=pts0 ses=7 comm="tar" exe="/usr/bin/tar" …
```

기록이 말하는 만큼만 씁니다.

- "2024-03-04 01:02:11 UTC, web01 의 감사 로그에 로그인 UID 1001(alice), 실제 UID 0, 감사 세션 7 로 `/usr/bin/tar` 를 실행한 기록이 있습니다."
- "같은 시각대 인증 로그에는 alice 계정이 pts/0 에서 sudo 로 root 권한을 얻어 같은 명령을 요청하고 허용된 기록이 있습니다."
- "같은 부팅 구간의 저널에 systemd-logind 가 alice 의 세션 7 을 만든 기록이 있고, 그 직전 sshd 기록에는 alice 계정이 203.0.113.25 에서 ED25519 공개 키로 인증한 기록이 있습니다."
- "이 키의 지문은 `/home/alice/.ssh/authorized_keys` 의 세 번째 줄 키의 지문과 같습니다." (`VERBOSE` 기록이 있거나 지문을 직접 대조했을 때)

기록은 그 계정·세션·키가 쓰였다는 사실을 보여 주지만, 키보드 앞에 누가 있었는지는 보여 주지 않습니다. 여러 사람이 계정이나 키를 나눠 썼다면 기록만으로는 구분할 수 없습니다. 그래서 "alice 가 자료를 빼냈다" 나 `auid` 를 확인하지 않은 "root 가 실행했다" 같은 문장은 쓰지 않습니다. 보고서 전체 구성은 [Linux 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 를 따릅니다.

## 함께 볼 페이지

- [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md) — sudo·su 줄, 시간 기록 파일, admin 플래그, 입출력 기록
- [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md) — 실행 레코드와 `auid`·`ses`
- [셸 명령 기록](../../02-artifacts/execution/shell-history/index.md) — 기록 파일 위치·저장 시점·시각 줄
- [SSH](../../02-artifacts/logins/ssh/index.md) — sshd 줄과 키 파일
- [권한을 올렸나](../intrusion/privilege-escalation.md) — 권한 상승 경로를 찾는 조사
- [타임라인 만들기](../../03-techniques/analysis/timeline.md) — 여러 기록을 한 시간축에 맞추기
- [로그 분석](../../03-techniques/analysis/log-analysis.md)

## 참고 문헌

1. Linux, kernel/audit.c (audit_set_loginuid_perm, audit_log_set_loginuid, session_id). https://github.com/torvalds/linux/blob/master/kernel/audit.c
2. Linux, fs/proc/base.c (loginuid, sessionid). https://github.com/torvalds/linux/blob/master/fs/proc/base.c
3. Linux, drivers/tty/tty_io.c·drivers/tty/pty.c. https://github.com/torvalds/linux/blob/master/drivers/tty/tty_io.c , https://github.com/torvalds/linux/blob/master/drivers/tty/pty.c
4. glibc, sysdeps/unix/sysv/linux/getlogin_r.c. https://github.com/bminor/glibc/blob/master/sysdeps/unix/sysv/linux/getlogin_r.c
5. linux-pam, modules/pam_loginuid/pam_loginuid.8.xml·modules/pam_tty_audit/pam_tty_audit.8.xml. https://github.com/linux-pam/linux-pam/tree/master/modules
6. linux-pam, modules/pam_unix/pam_unix_sess.c·libpam/pam_modutil_getlogin.c. https://github.com/linux-pam/linux-pam/blob/master/modules/pam_unix/pam_unix_sess.c , https://github.com/linux-pam/linux-pam/blob/master/libpam/pam_modutil_getlogin.c
7. linux-audit, audit-userspace docs/auditctl.8·docs/audit.rules.7. https://github.com/linux-audit/audit-userspace/tree/master/docs
8. linux-audit, audit-userspace docs/ausearch.8·docs/aureport.8. https://github.com/linux-audit/audit-userspace/blob/master/docs/ausearch.8 , https://github.com/linux-audit/audit-userspace/blob/master/docs/aureport.8
9. linux-audit, audit-documentation specs/fields/field-dictionary.csv. https://github.com/linux-audit/audit-documentation/tree/main/specs
10. linux-audit, audit-userspace rules/30-stig.rules·rules/32-power-abuse.rules. https://github.com/linux-audit/audit-userspace/tree/master/rules
11. sudo, docs/sudo.man.in·docs/sudoers.man.in. https://github.com/sudo-project/sudo/tree/main/docs
12. util-linux, login-utils/su-common.c·login-utils/su.1.adoc. https://github.com/util-linux/util-linux/blob/master/login-utils/su-common.c , https://github.com/util-linux/util-linux/blob/master/login-utils/su.1.adoc
13. util-linux, lib/pwdutils.c (xgetlogin). https://github.com/util-linux/util-linux/blob/master/lib/pwdutils.c
14. polkit, src/programs/pkexec.c. https://github.com/polkit-org/polkit/blob/main/src/programs/pkexec.c
15. OpenSSH portable, auth.c·auth2-pubkeyfile.c·session.c·sshd_config.5·ssh-keygen.1. https://github.com/openssh/openssh-portable/tree/master
16. systemd, src/login/logind-dbus.c·src/login/logind-session.c (main, v255), systemd-rhel9 src/login/logind-session.c. https://github.com/systemd/systemd/blob/main/src/login/logind-dbus.c , https://github.com/systemd/systemd/blob/v255/src/login/logind-session.c , https://github.com/redhat-plumbers/systemd-rhel9/blob/main/src/login/logind-session.c
17. systemd, man/systemd.journal-fields.xml. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
18. Ubuntu openssh 패키지(noble-updates) debian/sshd.pam.in, shadow 패키지 debian/login.pam·debian/login.defs. https://git.launchpad.net/ubuntu/+source/openssh/tree/debian?h=ubuntu/noble-updates , https://git.launchpad.net/ubuntu/+source/shadow/tree/debian?h=ubuntu/noble-updates
19. CentOS Stream 9 openssh 패키지 sshd.pam, shadow-utils 패키지 login.defs. https://gitlab.com/redhat/centos-stream/rpms/openssh/-/tree/c9s , https://gitlab.com/redhat/centos-stream/rpms/shadow-utils/-/tree/c9s
20. shadow, man/useradd.8.xml. https://github.com/shadow-maint/shadow/blob/master/man/useradd.8.xml
21. GNU Bash 5.2, doc/bash.1. https://github.com/tianon/mirror-bash/tree/bash-5.2
22. Velociraptor, artifacts/definitions/Linux/Events/ProcessExecutions.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Events/ProcessExecutions.yaml
23. Volatility 3, volatility3/framework/plugins/linux/bash.py·pslist.py·envars.py. https://github.com/volatilityfoundation/volatility3/tree/develop/volatility3/framework/plugins/linux
24. dissect.target, plugins/os/unix/history.py·plugins/os/unix/log/auth.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/history.py , https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/auth.py
25. go-libaudit, aucoalesce/coalesce.go. https://github.com/elastic/go-libaudit/blob/main/aucoalesce/coalesce.go
26. man-pages, man5/proc.5. https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
