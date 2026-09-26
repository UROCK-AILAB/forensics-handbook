---
title: "sudo·su 사용 기록"
parent: "아티팩트 · 로그인과 계정"
nav_order: 400
---

# sudo·su 사용 기록 (sudo·su)

sudo 와 su 로 다른 계정(대개 root)의 권한을 얻은 흔적은 인증 로그의 sudo·su 줄과 PAM 세션 줄, 감사 로그, 그리고 sudo 가 따로 만드는 시간 기록 파일·강의 파일·admin 플래그 파일·입출력 기록에 나뉘어 남습니다.

## 무엇을 기록하나 · 왜 생기나

sudo 는 사용자가 요청한 명령을 정책(sudoers)과 대조해 허용하거나 거부하고, 그 결과를 한 줄로 남깁니다. 허용한 명령과 거부한 명령을 모두 기록하는 것이 기본이고(`log_allowed`·`log_denied`, 1.8.29 이상)[1], 두 기준 배포판은 이 줄을 syslog 의 `authpriv` 분야로 보내도록 sudo 를 빌드합니다[6][7]. 줄은 기본으로 syslog 로만 보내고, sudoers 에 `logfile` 을 지정하면 파일에도 씁니다[1]. 두 배포판 모두 Linux 감사 연동(`--with-linux-audit`)을 켜고 빌드하므로[6][7], 감사 데몬이 돌고 있었다면 허용·거부한 명령이 감사 로그에도 들어갑니다[1].

sudo 는 명령을 실행하기 전에 PAM 인증과 PAM 세션을 거칩니다. 그래서 sudo 줄 하나 옆에는 `pam_unix(sudo:session)` 세션 열림·닫힘 줄이, 비밀번호를 틀렸다면 `pam_unix(sudo:auth)` 실패 줄이 함께 남습니다[1][11]. 이 밖에 sudo 는 비밀번호를 다시 묻지 않으려고 사용자별 시간 기록 파일(time stamp file)을 만들고[2], 빌드 설정에 따라 처음 사용한 사용자에게 강의(lecture)를 보여 준 표시 파일이나 admin 플래그 파일을 만듭니다[1].

두 기준 배포판의 `/usr/bin/su` 는 util-linux 의 su 입니다[10]. su 는 PAM 인증과 계정 확인이 끝난 뒤 성공인지 실패인지를 syslog 의 `auth` 분야로 한 줄 남기고[8], 실패했을 때는 btmp 에도 레코드를 덧붙입니다[8][9]. su 는 lastlog 에 전혀 쓰지 않고, lastlog 를 남길지는 PAM 설정(`pam_lastlog`)으로 정합니다[9]([로그인 기록 (wtmp·btmp·lastlog)](wtmp-btmp-lastlog.md)).

어느 계정이 sudo 를 쓸 수 있었는지를 정하는 규칙은 [sudo 설정 (sudoers)](../../01-foundations/users-auth/sudoers.md) 에서 다루고, 이 페이지는 실제로 쓴 흔적을 다룹니다.

## 위치와 버전별 차이

| 흔적 | Ubuntu 24.04 LTS | RHEL 9 계열 | 남는 기간 |
|---|---|---|---|
| sudo 판 | 1.9.15p5[6] | 1.9.17p2(CentOS Stream 9)[7] | |
| sudo 줄 (`authpriv`) | `/var/log/auth.log` | `/var/log/secure` | 로그 순환 설정을 따름 |
| su 성공·실패 줄 (`auth`) | `/var/log/auth.log` | `/var/log/messages` | 로그 순환 설정을 따름 |
| su 가 부른 PAM 줄 (`authpriv`) | `/var/log/auth.log` | `/var/log/secure` | 로그 순환 설정을 따름 |
| su 태그 | `su[PID]:` (util-linux 2.39.3)[8] | `su:` PID 없음 (util-linux 2.37.4)[8] | |
| 시간 기록 파일 | `/run/sudo/ts/UID`(`--with-rundir=/run/sudo`)[6] | 빌드 옵션에 폴더 지정 없음. 빌드 기본 규칙은 `/run` 이 있으면 `/run/sudo` 이므로 `/run/sudo/ts/UID`[1][4] | 재부팅하면 사라짐[1][4] |
| 강의 표시 파일 | 없음(`--without-lecture`)[6] | `/var/db/sudo/lectured/UID`, 폴더는 패키지가 0700 으로 설치[7] | 재부팅해도 남음[1] |
| admin 플래그 | `~/.sudo_as_admin_successful`(`--enable-admin-flag`)[1][6] | 없음 | 지우기 전까지 남음 |
| 입출력 기록 | 기본 꺼짐. 켜면 `/var/log/sudo-io/` 아래[1][4] | 같음 | 지우기 전까지 남음 |
| 감사 기록 | 감사 데몬이 켜져 있으면 `/var/log/audit/audit.log` | 같음 | 감사 설정을 따름 |

RHEL 에서 su 줄과 그 su 의 PAM 줄이 서로 다른 파일에 남는 이유는 rsyslog 규칙 때문입니다. RHEL 의 secure 규칙은 `authpriv` 만 고르고, util-linux su 는 `auth` 분야로 보냅니다[8]. 분야별 파일 배치와 순환본 이름은 [인증 로그 (auth.log·secure)](auth-log.md) 에서 다룹니다. rsyslog 를 쓰지 않는 시스템에서는 같은 메시지를 저널에서 찾습니다.

시간 기록 파일의 이름은 sudo 1.9.15 부터 사용자 이름이 아니라 UID 입니다[5]. 강의 파일도 UID 이름을 쓰고, 1.9.15p5 부터는 옛 이름 기반 강의 파일을 만나면 UID 이름으로 바꿉니다[3][5]. 두 기준 배포판은 모두 이 판 이후라서 파일 이름이 숫자이고, UID 를 계정 이름으로 잇는 방법은 [UID·GID 와 사용자 이름 잇기](../../01-foundations/value-decoding/uid-gid.md) 에 있습니다. 판을 올리기 전에 만든 파일은 이름이 사용자 이름으로 남아 있을 가능성이 있습니다.

## 구조

### sudo 허용 줄

sudo 형식(기본)의 줄은 다음 모양입니다[1].

```
date hostname progname: username : TTY=ttyname ; CHROOT=chroot ; PWD=cwd ; USER=runasuser ; GROUP=runasgroup ; TSID=logid ; ENV=env_vars COMMAND=command
```

| 필드 | 뜻 |
|---|---|
| date·hostname·progname | syslog 가 붙이는 값이라 형식은 syslog 쪽 설정을 따릅니다. progname 은 보통 `sudo` 나 `sudoedit` 입니다[1] |
| username | sudo 를 실행한 사용자의 로그인 이름 |
| TTY | 짧은 터미널 이름(`pts/0`, `tty01` 등). 터미널이 없으면 `unknown` |
| CHROOT | 루트 디렉터리를 지정했을 때만 |
| PWD | sudo 를 실행한 작업 폴더 |
| USER | 명령을 실행한 대상 사용자 |
| GROUP | 명령줄에서 그룹을 지정했을 때만 |
| TSID | 입출력 기록 식별자. `log_input`·`log_output` 이 켜졌을 때만 |
| ENV | 명령줄에서 지정한 환경 변수가 있을 때만 |
| COMMAND | 실제로 실행한 명령과 인자 |

기록 속의 제어 문자는 `#` 뒤에 8진수로 적고(탭은 `#011`), 명령 경로 안의 공백은 `#040` 으로 적습니다. 공백이 든 인자는 작은따옴표로 감쌉니다[1]. 그래서 `COMMAND=/opt/backup#040tool/run.sh` 는 경로 이름 자체에 공백이 든 프로그램 하나를 실행한 것이고, 인자가 여러 개인 명령과 구분됩니다. syslog 로 보낼 때 태그에 PID 를 붙이는 `syslog_pid` 는 기본으로 꺼져 있어서 태그는 `sudo:` 로만 찍힙니다[1]. 한 메시지의 최대 크기는 `syslog_maxlen` 기본값 980바이트이고, 이보다 긴 메시지는 여러 줄로 나뉘며 이어지는 줄에는 사용자 이름 뒤에 `(command continued)` 가 붙습니다[1].

`log_format` 을 `json` 으로 바꾸면 줄 모양이 JSON 으로 바뀝니다[1]. 대상 시스템의 sudoers 에서 `log_format`, `logfile` 설정을 먼저 확인합니다([sudo 설정 (sudoers)](../../01-foundations/users-auth/sudoers.md)).

### sudo 거부 줄

거부한 명령은 사용자 이름 바로 뒤에 사유가 붙고 나머지 필드는 같습니다[1].

| 사유 문구 | 뜻 |
|---|---|
| `user NOT in sudoers` | sudoers 에 없는 사용자 |
| `user NOT authorized on host` | sudoers 에 있지만 이 호스트에서는 허용되지 않음 |
| `command not allowed` | 이 호스트에서 이 명령은 허용되지 않음 |
| `3 incorrect password attempts` | 비밀번호를 세 번 틀림. 숫자는 틀린 횟수와 `passwd_tries` 에 따라 바뀜 |
| `a password is required` | `-n` 으로 실행했는데 비밀번호가 필요했음 |
| `sorry, you are not allowed to set the following environment variables` | 허용되지 않은 환경 변수를 명령줄에서 지정함 |

아래는 두 배포판에서 보이는 줄의 만든 예시입니다. 사용자 이름 앞의 공백 개수는 예시일 뿐이므로 실제 줄로 확인합니다.

```
(Ubuntu 24.04, 만든 예시)
2026-03-12T10:02:11.402113+09:00 web01 sudo:    alice : TTY=pts/1 ; PWD=/home/alice ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow
2026-03-12T10:02:11.405871+09:00 web01 sudo: pam_unix(sudo:session): session opened for user root(uid=0) by alice(uid=1001)
2026-03-12T10:02:11.431290+09:00 web01 sudo: pam_unix(sudo:session): session closed for user root

(RHEL 9 계열, 만든 예시)
Mar 12 10:05:40 web01 sudo:    bob : 3 incorrect password attempts ; TTY=pts/2 ; PWD=/tmp ; USER=root ; COMMAND=/usr/bin/id
```

### sudo 가 부르는 PAM 줄

PAM 줄의 머리 `모듈(서비스:단계):` 과 세션 줄 서식은 [인증 로그](auth-log.md) 에서 다룹니다. sudo 에서 알아 둘 점은 둘입니다. 세션 열림 줄의 `by` 뒤 이름은 `pam_modutil_getlogin` 으로 구한 로그인 이름이고, 괄호 안 UID 는 sudo 프로세스의 실제 UID(`getuid()`)입니다[11]. `sudo -i` 로 실행하면 두 배포판 모두 `--with-pam-login` 으로 빌드했으므로 PAM 서비스 이름이 `sudo-i` 가 되어 머리가 `pam_unix(sudo-i:session)` 으로 바뀝니다[1][4][6][7]. `-i`·`-s` 가 아닐 때 sudo 는 PAM 세션 모듈을 조용한 모드(silent)로 부릅니다[1]. pam_unix 가 세션 줄을 남기지 않는 것은 이 플래그가 아니라 PAM 설정 줄에 모듈 인자 `quiet` 가 붙었을 때이므로[11], 세션 줄이 없으면 `/etc/pam.d/sudo` 를 확인합니다([인증 모듈 (PAM)](../../01-foundations/users-auth/pam.md)).

### su 줄

util-linux su 의 기록은 서식 문자열 `%s(to %s) %s on %s` 하나로 만들어집니다[8]. 앞의 `%s` 는 성공이면 빈 문자열, 실패면 `FAILED SU ` 이고, 이어서 대상 사용자, 원래 사용자, 터미널 이름(없으면 `none`)이 들어갑니다[8]. 등급은 `LOG_NOTICE` 입니다[8].

```
(Ubuntu 24.04, 만든 예시)
2026-03-12T11:20:07.118402+09:00 web01 su[4120]: (to root) alice on pts/1
2026-03-12T11:20:07.121937+09:00 web01 su[4120]: pam_unix(su:session): session opened for user root(uid=0) by alice(uid=1001)

(RHEL 9 계열 /var/log/messages, 만든 예시)
Mar 12 11:22:31 web01 su: FAILED SU (to root) bob on pts/2
```

PAM 서비스 이름은 `su` 이고, 로그인 셸로 바꾸는 `su -` 는 `su-l` 입니다[8]. RHEL 의 util-linux 패키지는 `/etc/pam.d/su`, `su-l`, `runuser`, `runuser-l` 를 함께 싣습니다[10]. su 줄 자체에는 `-c` 로 넘긴 명령이 들어가지 않습니다[8].

인증에 실패하면 su 는 btmp 에 레코드를 하나 덧붙입니다. 사용자 필드에는 대상 계정(계정 정보가 없으면 `(unknown)`), 터미널 필드에는 su 를 실행한 터미널이 들어갑니다[8]. 레코드 형식은 [로그인 기록 (wtmp·btmp·lastlog)](wtmp-btmp-lastlog.md) 에 있습니다.

### 시간 기록 파일

sudo 는 사용자가 인증에 성공하면 UID 별 파일 하나에 레코드를 적어 두고, 제한 시간(`timestamp_timeout`) 안에 다시 실행하면 비밀번호를 묻지 않습니다[2]. 기본으로는 터미널마다 따로 레코드를 만듭니다[2]. 파일의 첫 레코드는 여러 sudo 가 동시에 새 레코드를 넣지 않게 막는 잠금 레코드(`TS_LOCKEXCL`)이고, 그 뒤에 실제 레코드가 이어집니다[2][3]. 레코드 구조는 다음과 같습니다[2].

| 필드 | C 형식 | 뜻 |
|---|---|---|
| version | unsigned short | 레코드 판. 새 레코드는 2[2] |
| size | unsigned short | 레코드 바이트 수 |
| type | unsigned short | `0x01` TS_GLOBAL, `0x02` TS_TTY, `0x03` TS_PPID, `0x04` TS_LOCKEXCL |
| flags | unsigned short | `0x01` TS_DISABLED(`sudo -k` 로 끈 레코드), `0x02` TS_ANYUID |
| auth_uid | uid_t | 인증에 쓴 UID. `rootpw`·`runaspw`·`targetpw` 설정에 따라 호출한 사용자, root, 기본 runas 사용자, 대상 사용자일 수 있음 |
| sid | pid_t | 터미널 세션 ID |
| start_time | struct timespec | TS_TTY 는 세션 리더, TS_PPID 는 부모 프로세스의 시작 시각(1.8.22 에서 추가) |
| ts | struct timespec | 시간 기록. 단조 시계 값이고 sudo 로 명령을 실행할 때마다 갱신 |
| u | dev_t 또는 pid_t | TS_TTY 는 터미널 장치 번호, TS_PPID 는 부모 PID |

x86_64 Linux 에서 이 구조체를 C 배치 규칙대로 놓으면 레코드 하나는 56바이트(0x38)이고 모든 값은 리틀 엔디언입니다. 이 크기는 계산한 값이므로 실제 데이터에서는 각 레코드의 `size` 필드로 확인합니다. sudo 는 읽은 레코드의 `version` 이 2 가 아니거나 `size` 가 읽은 크기와 다르면 그 레코드를 만료된 것으로 봅니다[3].

### 강의 표시 파일과 admin 플래그

강의는 비밀번호를 물을 때 함께 보여 주는 짧은 안내문입니다[1]. RHEL 계열의 기본 설정(`lecture=once`)에서는 사용자가 강의를 한 번 받으면 `lecture_status_dir` 에 그 사용자의 UID 이름으로 크기 0 인 파일을 만들고, 이 폴더는 재부팅해도 비우지 않습니다[1][3][4]. 파일은 이미 있으면 새로 만들지 않습니다(`O_CREAT|O_EXCL`)[3].

Ubuntu 의 sudo 는 강의를 끄고 대신 admin 플래그를 켜고 빌드합니다[6]. `sudo` 또는 `admin` 그룹에 든 사용자가 sudo 를 처음 실행하면 홈 폴더에 `~/.sudo_as_admin_successful` 을 만듭니다[1].

### 입출력 기록

`log_input`·`log_output` 이나 명령 태그 `LOG_INPUT`·`LOG_OUTPUT` 이 켜져 있을 때만 생깁니다[1]. 기록은 `iolog_dir`(빌드 기본 `/var/log/sudo-io`) 아래 `iolog_file`(기본 `%{seq}`) 경로에 명령마다 폴더 하나로 남습니다[1][4]. `%{seq}` 는 `0100A5` 같은 36진수 일련번호이고 두 글자마다 폴더를 나눠 `01/00/A5` 가 됩니다[1]. 이 경로가 sudo 줄의 `TSID=` 값입니다[1].

| 파일 | 내용 |
|---|---|
| `log` | 첫 줄은 콜론으로 나눈 실행 시각·실행 사용자·대상 사용자·대상 그룹(선택)·터미널·터미널 줄 수와 열 수, 둘째 줄은 작업 폴더, 셋째 줄은 명령과 인자[1] |
| `log.json` | `log` 와 같은 정보에 더해 `timestamp`(초·나노초), `runargv`, `runenv`, `runuid`, `submituser`, `submithost`, `submitcwd`, `ttyname` 등[1] |
| `timing` | 줄마다 기록 종류 번호와 앞 기록 뒤로 흐른 시간, 바이트 수 등. 0~4 는 표준 입력·표준 출력·표준 오류·터미널 입력·터미널 출력[1] |
| `ttyin`·`ttyout` | 터미널 입력(친 키 그대로)과 터미널 출력[1] |
| `stdin`·`stdout`·`stderr` | 파이프나 파일로 연결된 입출력[1] |

`log` 를 뺀 파일은 `compress_io` 를 끄지 않았다면 gzip 으로 압축되어 있습니다[1]. `ttyin` 에는 화면에 보이지 않은 비밀번호가 평문으로 들어 있을 수 있습니다[1].

## 증거로서 의미

### 증명하는 것

sudo 허용 줄은 "그 시각에 그 사용자가 그 터미널·작업 폴더에서 그 대상 사용자로 그 명령을 sudo 에 요청했고 정책이 허용했다" 는 기록입니다[1]. 거부 줄은 요청과 거부 사유를 보여 주고, 특히 `user NOT in sudoers` 는 권한이 없는 계정이 root 권한을 얻으려 한 흔적입니다. 같은 시각의 `pam_unix(sudo:session)` 열림·닫힘 짝은 sudo 가 명령을 실행하려고 세션을 열었다는 점을 보강합니다.

su 줄은 그 시각에 그 터미널에서 어느 계정이 어느 계정으로 바꾸려 했고, 인증과 계정 확인이 성공했는지 실패했는지를 보여 줍니다[8]. su 뒤에 이어지는 `pam_unix(su:session)` 또는 `pam_unix(su-l:session)` 줄은 로그인 셸로 바꿨는지(`su -`)를 알려 줍니다.

강의 표시 파일과 admin 플래그 파일은 한 번 만들어지면 다시 만들지 않으므로, 그 계정이 이 시스템에서 sudo 를 쓴 적이 있다는 흔적입니다. 파일을 지우지 않았다면 만들어진 시각은 처음 사용한 시각에 가까울 가능성이 있습니다. 입출력 기록은 sudo 로 실행한 명령의 화면 출력과 입력까지 보여 줍니다.

### 증명하지 못하는 것

sudo 줄에는 명령이 성공했는지가 나오지 않습니다. 종료 값은 `log_exit_status` 를 켰을 때만 남고 기본은 꺼져 있습니다(1.9.8 이상)[1]. `sudo -i`·`sudo -s`·`sudo bash` 처럼 셸을 연 경우 sudo 줄에는 셸만 남고, 그 셸 안에서 친 명령은 `log_subcmds`(기본 꺼짐)나 입출력 기록이 켜져 있지 않으면 sudo 기록 어디에도 없습니다[1]. 그런 명령은 [셸 명령 기록](../execution/shell-history/index.md) 과 [감사 로그의 실행 기록](../execution/auditd-execve.md) 에서 찾습니다.

username 은 sudo 를 실행한 계정이지 그 계정을 쓴 사람이 아닙니다. 같은 계정을 여러 사람이 쓰거나 비밀번호가 새었을 가능성은 로그인 기록과 원격 주소로 따로 따져야 합니다([누가 그 명령을 실행했나](../../04-scenarios/attribution/user-attribution.md)). su 줄에는 su 뒤에 무엇을 했는지가 없습니다.

강의 파일과 admin 플래그 파일이 없다고 sudo 를 쓰지 않은 것은 아닙니다. 강의는 비밀번호를 물을 때 보여 주므로 `NOPASSWD` 규칙으로만 sudo 를 쓴 사용자에게는 강의 파일이 생기지 않을 가능성이 있고, 두 파일 모두 사용자가 지울 수 있습니다. 시간 기록 파일은 재부팅하면 사라지므로 전원을 끈 뒤 만든 디스크 이미지에는 없습니다[1][4].

## 시각 해석

로그 줄의 시각은 syslog 가 붙인 값입니다[1]. Ubuntu 24.04 의 auth.log 는 연도·마이크로초·UTC 오프셋이 있는 RFC 3339 시각이고, RHEL 의 secure·messages 는 연도와 시간대가 없는 현지 시각입니다. 연도를 정하는 방법은 [인증 로그](auth-log.md) 의 시각 해석을 따릅니다. `logfile` 로 쓴 sudo 파일 기록은 `log_year` 를 켜지 않으면 연도가 없습니다[1].

sudo 줄의 시각은 정책 판단을 기록한 때이고 명령이 끝난 때가 아닙니다. 세션 닫힘 줄의 시각이 명령이 끝난 시각에 가까울 가능성이 있지만, 명령이 오래 걸린 경우 두 줄 사이에 다른 기록이 많이 끼어듭니다.

시간 기록 파일의 `ts` 는 실제 시각 시계(wall clock) 값이 아니라 단조 시계 값이고, sudo 는 가능하면 잠자기 중에도 흐르는 단조 시계를 씁니다[2]. 그래서 이 값은 부팅한 뒤로 흐른 시간에 가깝고, [부팅 시각](../system-info/boot-shutdown.md) 에 더해야 대략의 시각이 됩니다. 파일은 레코드를 고쳐 쓸 때마다(`pwrite`) 바뀌므로[3], 파일의 수정 시각은 그 사용자가 마지막으로 sudo 인증 기록을 갱신한 때일 가능성이 있습니다.

강의 파일·admin 플래그 파일·입출력 기록 폴더의 시각은 파일 시스템 시각입니다. 해석은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 을 따릅니다. `log.json` 의 `timestamp` 는 초와 나노초로 나뉜 값입니다[1].

## 함정과 한계

- RHEL 에서 secure 만 보면 su 성공·실패 줄을 놓칩니다. su 줄은 `/var/log/messages` 에, 같은 su 의 PAM 줄은 secure 에 있습니다.
- sudo 가 `logfile` 로 쓴 파일은 한 줄이 `loglinelen`(기본 80자)을 넘으면 다음 줄로 넘기고 네 칸 들여씁니다[1]. 줄 단위 grep 은 넘어간 부분을 놓치므로 들여쓴 줄을 앞 줄에 붙여서 읽습니다.
- 메시지가 `syslog_maxlen`(기본 980바이트)보다 길면 한 요청이 여러 줄로 나뉩니다[1]. `(command continued)` 가 붙은 줄을 앞 줄에 이어 붙여 읽습니다.
- dissect.target 의 `authlog` 는 sudo 줄에서 `TTY=`·`PWD=`·`USER=`·`COMMAND=` 만 뽑고 사용자 이름 뒤의 거부 사유는 따로 뽑지 않습니다[13]. 구조화된 필드만 보면 거부 줄이 허용 줄처럼 보이므로 원래 메시지를 함께 봅니다. `TTY=unknown` 이나 `GROUP=` 이 낀 줄에서 필드가 비는 문제와 su 파서의 한계는 [인증 로그](auth-log.md) 의 함정에 있습니다.
- Velociraptor 의 `Linux.Users.RootUsers` 는 설명에 `sudo` 그룹 사용자를 찾는다고 적혀 있지만, 질의는 `id -Gn` 결과에 `root` 라는 문자열이 있는지만 봅니다[17]. `sudo`·`wheel`·`admin` 그룹 구성원은 [계정 파일](../../01-foundations/users-auth/passwd-shadow-group.md) 의 `/etc/group` 에서 직접 확인합니다.
- ForensicArtifacts 의 `UnixSudoersConfigurationFile` 은 `/etc/sudoers` 만 잡고 `/etc/sudoers.d/` 는 잡지 않습니다[15]. 입출력 기록 정의(`LinuxSudoReplayLogs`)는 `/var/log/sudo-io/**` 만 잡으므로[15], sudoers 에서 `iolog_dir` 을 바꿨다면 그 경로를 따로 모아야 합니다.
- 인증 로그는 텍스트라 줄을 지우기 쉽습니다. sudo 줄이 빠진 구간이 있으면 저널, 감사 로그, 시간 기록 파일, 강의 파일과 맞대어 봅니다([흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md)).
- 기준 배포판이 아닌 시스템에서는 su 가 shadow 패키지의 su 일 수 있고, 그 경우 줄 모양이 다릅니다. `/usr/bin/su` 가 어느 패키지에 속하는지 대상 시스템에서 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

라이브 수집으로 얻은 `/run/sudo/ts/1001` 을 x86_64 에서 읽었다고 가정한 예입니다(명세의 구조체로 만든 예시, 값은 모두 지어낸 것).

```
00000000: 0200 3800 0400 0000 0000 0000 0000 0000  ..8.............
00000010: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000020: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000030: 0000 0000 0000 0000 0200 3800 0200 0000  ..........8.....
00000040: e903 0000 a208 0000 2a07 0000 0000 0000  ........*.......
00000050: 80b2 e60e 0000 0000 8b13 0000 0000 0000  ................
00000060: 000e 2707 0000 0000 0188 0000 0000 0000  ..'.............
```

0x00 의 첫 레코드는 version `0x0002`, size `0x0038`(56), type `0x0004`(TS_LOCKEXCL)이고 나머지는 0 인 잠금 레코드입니다. 0x38 부터 두 번째 레코드가 시작하고 type 은 `0x0002`(TS_TTY), flags 는 0 입니다. 0x40 의 auth_uid 는 `0x3e9`(1001), 0x44 의 sid 는 `0x8a2`(2210)입니다. 0x48 의 start_time 은 초 `0x72a`(1834)와 0x50 의 나노초 `0x0ee6b280`(250000000)이고, 0x58 의 ts 는 초 `0x138b`(5003)와 0x60 의 나노초 `0x07270e00`(120000000)입니다. 0x68 의 `0x8801` 은 터미널 장치 번호입니다. 이 사용자는 부팅 뒤 약 5003초가 지났을 때 이 터미널에서 마지막으로 sudo 인증 기록을 갱신했다는 뜻으로 읽습니다. flags 에 `0x01` 이 켜져 있으면 `sudo -k` 로 기록을 끈 레코드입니다[2].

sudo 소스에 들어 있는 `tsdump` 도구로도 이 파일을 풀어 볼 수 있습니다[2].

### 공개 도구로 한 번

```
# Ubuntu: sudo·su 줄과 PAM 줄을 순환본까지 모아 보기
zcat -f /mnt/evidence/var/log/auth.log* | grep -E ' sudo(\[[0-9]+\])?: | su(\[[0-9]+\])?: '

# RHEL: sudo 는 secure, su 성공·실패는 messages
grep -h ' sudo: ' /mnt/evidence/var/log/secure*
grep -hE ' su: (FAILED SU )?\(to ' /mnt/evidence/var/log/messages*

# 저널에서 태그로 고르기
journalctl -D /mnt/evidence/var/log/journal SYSLOG_IDENTIFIER=sudo -o short-iso
journalctl -D /mnt/evidence/var/log/journal SYSLOG_IDENTIFIER=su -o short-iso

# 감사 로그의 sudo 명령 기록
ausearch -if /mnt/evidence/var/log/audit/audit.log -m USER_CMD -i

# 강의 파일과 admin 플래그 파일의 시각
stat /mnt/evidence/var/db/sudo/lectured/* /mnt/evidence/home/*/.sudo_as_admin_successful

# 입출력 기록 목록과 재생
sudoreplay -d /mnt/evidence/var/log/sudo-io -l
sudoreplay -d /mnt/evidence/var/log/sudo-io 000001
```

`sudoreplay` 는 입출력 기록을 나열하거나 재생합니다[16]. dissect.target 의 `authlog` 는 sudo·su·pkexec 줄을 서비스별로 나눠 필드를 뽑습니다[13]. UAC 는 라이브 응답에서 `/var/db/sudo/lectured` 와 `/var/lib/sudo/lectured` 안 파일의 시각을 stat 로 모읍니다[14]. 감사 기록 번호 `USER_CMD` 는 1123 이고[12], `ausearch` 의 `-if` 는 읽을 파일을, `-i` 는 숫자 값을 이름으로 풀어 보여 주는 옵션입니다[18].

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [인증 로그 (auth.log·secure)](auth-log.md) | 같은 시각의 sshd 로그인과 `pam_unix(sudo:auth)` 실패 줄 |
| [로그인 기록 (wtmp·btmp·lastlog)](wtmp-btmp-lastlog.md) | sudo·su 줄의 터미널(`pts/1`)을 그 시각에 연 로그인 세션과 원격 주소, su 실패의 btmp 레코드 |
| [감사 로그 형식 (auditd)](../../01-foundations/logging/auditd-format.md) | `USER_CMD`(1123) 기록과 로그인 때 붙은 감사 ID(auid)[12] |
| [감사 로그의 실행 기록](../execution/auditd-execve.md) | sudo 로 연 셸 안에서 실행한 프로그램 |
| [셸 명령 기록](../execution/shell-history/index.md) | 호출한 사용자의 기록에 남은 `sudo …` 명령, root 의 기록에 남은 그 뒤 명령 |
| [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) | 같은 메시지의 `_PID`·`_UID`·`_COMM` 으로 보낸 프로세스 확인 |
| [sudo 설정 (sudoers)](../../01-foundations/users-auth/sudoers.md) | 그 명령이 어느 규칙으로 허용됐는지, 기록 설정이 켜져 있었는지 |
| [계정 생성·변경 흔적](account-changes.md) | sudo 로 실행한 `useradd`·`usermod` 와 그 결과 줄 |

sudo·su 기록을 중심으로 권한 상승을 따라가는 흐름은 [권한을 올렸나](../../04-scenarios/intrusion/privilege-escalation.md) 에서 다룹니다.

## 실습

NIST CFReDS 등에 공개된 Linux 디스크 이미지나 직접 만든 가상 머신 이미지로 다음 질문을 풀어 봅니다.

1. 대상 시스템의 sudo 판은 무엇이고, sudoers 에 `logfile`, `log_format`, `log_input`, `log_output`, `log_subcmds` 설정이 있는가?
2. 거부 줄 가운데 `user NOT in sudoers` 가 있는가? 그 계정은 언제 어디서 로그인했는가?
3. `sudo -i`·`sudo su -`·`sudo bash` 처럼 셸을 연 줄이 있다면, 그 뒤에 실행한 명령을 어느 기록에서 찾을 수 있는가?
4. RHEL 시스템이라면 messages 의 `(to root)` 줄 수와 secure 의 `pam_unix(su` 세션 열림 줄 수가 맞는가?
5. `/var/db/sudo/lectured` 나 `~/.sudo_as_admin_successful` 의 시각은 인증 로그의 첫 sudo 줄 시각과 맞는가? 로그가 순환되어 사라진 기간에도 sudo 를 쓴 흔적이 있는가?

## 참고 문헌

1. sudo, docs/sudoers.man.in (EVENT LOGGING, I/O LOGGING, 설정 항목). https://github.com/sudo-project/sudo/blob/main/docs/sudoers.man.in
2. sudo, docs/sudoers_timestamp.man.in. https://github.com/sudo-project/sudo/blob/main/docs/sudoers_timestamp.man.in
3. sudo, plugins/sudoers/timestamp.c. https://github.com/sudo-project/sudo/blob/main/plugins/sudoers/timestamp.c
4. sudo, configure.ac·m4/sudo.m4. https://github.com/sudo-project/sudo/blob/main/configure.ac , https://github.com/sudo-project/sudo/blob/main/m4/sudo.m4
5. sudo, NEWS (1.9.15, 1.9.15p5). https://github.com/sudo-project/sudo/blob/main/NEWS
6. Ubuntu sudo 패키지(noble-updates), debian/rules·debian/etc/sudoers·changelog. https://git.launchpad.net/ubuntu/+source/sudo/tree/debian?h=ubuntu/noble-updates
7. CentOS Stream 9 sudo 패키지, sudo.spec·sudoers. https://gitlab.com/redhat/centos-stream/rpms/sudo/-/tree/c9s
8. util-linux, login-utils/su-common.c (master, v2.39.3, v2.37.4). https://github.com/util-linux/util-linux/blob/master/login-utils/su-common.c , https://github.com/util-linux/util-linux/blob/v2.39.3/login-utils/su-common.c , https://github.com/util-linux/util-linux/blob/v2.37.4/login-utils/su-common.c
9. util-linux, login-utils/su.1.adoc. https://github.com/util-linux/util-linux/blob/master/login-utils/su.1.adoc
10. Ubuntu util-linux 패키지(noble-updates), debian/util-linux.install. https://git.launchpad.net/ubuntu/+source/util-linux/tree/debian?h=ubuntu/noble-updates ; CentOS Stream 9 util-linux 패키지, util-linux.spec. https://gitlab.com/redhat/centos-stream/rpms/util-linux/-/tree/c9s
11. linux-pam, modules/pam_unix/pam_unix_sess.c·libpam/pam_syslog.c. https://github.com/linux-pam/linux-pam/tree/master/modules/pam_unix , https://github.com/linux-pam/linux-pam/blob/master/libpam/pam_syslog.c
12. linux-audit, audit-documentation specs/messages/message-dictionary.csv. https://github.com/linux-audit/audit-documentation/blob/main/specs/messages/message-dictionary.csv
13. dissect.target, plugins/os/unix/log/auth.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/auth.py
14. UAC, artifacts/live_response/system/sudo_lectured.yaml. https://github.com/tclahr/uac/blob/main/artifacts/live_response/system/sudo_lectured.yaml
15. ForensicArtifacts, linux.yaml·unix_common.yaml. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml , https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/unix_common.yaml
16. sudo, docs/sudoreplay.man.in. https://github.com/sudo-project/sudo/blob/main/docs/sudoreplay.man.in
17. Velociraptor, artifacts/definitions/Linux/Users/RootUsers.yaml. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Users/RootUsers.yaml
18. linux-audit, audit-userspace ausearch.8. https://github.com/linux-audit/audit-userspace/blob/master/docs/ausearch.8
