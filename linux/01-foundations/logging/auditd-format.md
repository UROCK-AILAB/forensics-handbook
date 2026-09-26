---
title: "감사 로그 형식"
parent: "기반 · 로그 체계"
nav_order: 230
---

# 감사 로그 형식 (auditd)

리눅스 감사 체계 (Linux Audit) 는 커널과 신뢰받는 사용자 공간 프로그램이 만든 레코드를 auditd 가 `/var/log/audit/audit.log` 에 한 줄씩 `type=... msg=audit(초.밀리초:일련번호): 키=값 ...` 모양으로 적는 텍스트 로그입니다[1][6][12].

## 이 형식을 쓰는 아티팩트

감사 로그는 규칙에 걸린 시스템 콜을 커널이 기록한 레코드와, 로그인·인증·계정 변경처럼 사용자 공간 프로그램이 보낸 레코드를 한 파일에 모읍니다[10]. 같은 형식을 읽는 쪽이 여럿이라 형식 설명은 이 쪽에 두고, 무엇을 알아내는지는 각 쪽에서 다룹니다.

| 쓰는 곳 | 주로 보는 레코드 | 쪽 |
|---|---|---|
| 프로그램 실행 기록 | SYSCALL, EXECVE, PROCTITLE, CWD, PATH | [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md) |
| 파일 감시 | SYSCALL, PATH (규칙의 `key`) | [감사 로그의 파일 감시](../../02-artifacts/file-activity/auditd-watches.md) |
| 로그인·인증 | USER_AUTH, USER_ACCT, CRED_ACQ, USER_START, USER_LOGIN, USER_END | [인증 로그](../../02-artifacts/logins/auth-log.md), [sudo·su 사용 기록](../../02-artifacts/logins/sudo-su.md) |
| 계정 변경 | ADD_USER, DEL_USER, USER_CHAUTHTOK, USER_MGMT | [계정 생성·변경 흔적](../../02-artifacts/logins/account-changes.md) |
| 부팅·종료 | SYSTEM_BOOT, SYSTEM_SHUTDOWN, SERVICE_START, SERVICE_STOP | [부팅과 종료 기록](../../02-artifacts/system-info/boot-shutdown.md) |

### 파일 위치

auditd 설정 파일 `/etc/audit/auditd.conf` 의 `log_file` 이 로그 경로를 정하고, 값을 적지 않으면 `/var/log/audit/audit.log` 를 씁니다[1]. 감사 규칙과 설정은 다음 경로에 있습니다[3].

| 경로 | 내용 |
|---|---|
| `/etc/audit/auditd.conf` | auditd 설정 (로그 경로·형식·회전·디스크 부족 때 동작) |
| `/etc/audit/audit.rules` | 시작할 때 `auditctl` 이 커널에 넣는 규칙 |
| `/etc/audit/rules.d/` | `augenrules` 가 하나로 합쳐 `audit.rules` 를 만드는 규칙 조각 |
| `/etc/audit/plugins.d/` | 플러그인 설정 |
| `/etc/audit/audit-stop.rules` | auditd 가 멈출 때 넣는 규칙 |
| `/run/audit/auditd.state` | auditd 가 SIGCONT 를 받으면 내부 상태를 적는 보고 파일 |

이 파일들은 auditd 패키지가 깔려 있어야 생기므로, 검체에 `/etc/audit/auditd.conf` 와 `/var/log/audit/` 가 있는지 먼저 보고, `log_file` 값이 기본값과 다르면 그 경로를 따라갑니다. 설치 여부는 패키지 기록([dpkg·apt 기록](../../02-artifacts/packages/dpkg-apt.md), [rpm·dnf·yum 기록](../../02-artifacts/packages/rpm-dnf.md))으로 확인합니다.

### audit-userspace 기본 설정

audit-userspace 가 싣는 기본 `auditd.conf` 에서 분석에 영향을 주는 값은 다음과 같습니다[2].

| 키 | 기본값 | 뜻 |
|---|---|---|
| `log_format` | `ENRICHED` | 원래 레코드 뒤에 사람이 읽는 풀이 값을 덧붙임[1] |
| `flush` / `freq` | `INCREMENTAL_ASYNC` / `50` | 50개 레코드마다 비동기로 디스크에 내려씀[1] |
| `max_log_file` | `8` | 파일 하나의 최대 크기 (MiB)[1] |
| `max_log_file_action` | `ROTATE` | 최대 크기에 닿으면 회전[1] |
| `num_logs` | `5` | 회전할 때 남기는 파일 수[1] |
| `space_left` / `space_left_action` | `75` / `SYSLOG` | 남은 공간이 75 MiB 아래면 syslog 로 경고[1] |
| `admin_space_left` / `admin_space_left_action` | `50` / `SUSPEND` | 50 MiB 아래면 디스크 기록을 멈춤[1] |
| `disk_full_action`, `disk_error_action` | `SUSPEND` | 디스크가 차거나 쓰기 오류가 나면 기록을 멈춤[1] |
| `name_format` | `NONE` | 레코드 앞에 `node=` 를 붙이지 않음[1] |
| `end_of_event_timeout` | `2` | 이벤트가 끝났다고 보는 시간 (초)[1] |

man 페이지는 설정 파일에 `num_logs` 가 없을 때 기본값을 0(회전 안 함)이라고 적어서, 배포되는 설정 파일의 5 와 다릅니다[1][2]. 검체에서는 실제 `auditd.conf` 의 값을 읽고 판단합니다.

## 구조

### 한 줄의 모양

auditd 는 레코드 하나를 한 줄로 적고, `name_format` 이 `NONE` 이 아니면 줄 앞에 `node=호스트` 를 붙입니다[6]. 레코드 안의 줄바꿈은 공백으로 바꾸고 끝의 공백은 지웁니다[6].

```text
[node=호스트 ]type=종류이름 msg=audit(초.밀리초:일련번호): 키=값 키=값 ...
```

`audit(...)` 부분은 커널이 `audit(%llu.%03lu:%u): ` 형식으로 만듭니다[12]. 앞의 수는 Unix epoch 초, 점 뒤의 세 자리는 밀리초, 콜론 뒤의 수는 이벤트 일련번호입니다[4][12]. `type=` 뒤에는 번호 대신 이름이 오고, auditd 가 이름을 모르는 번호는 `UNKNOWN[번호]` 로 적습니다[6].

### 이벤트와 레코드

이벤트 (event) 하나는 레코드 (record) 여러 줄로 이루어집니다. 시스템 콜 하나가 사용자 공간에서 커널로 들어갔다 나오는 동안 생긴 레코드는 모두 같은 일련번호를 나누어 쓰고, 다음 시스템 콜은 다른 번호를 받습니다[4]. 예를 들어 `open` 을 감사하면 커널이 SYSCALL 레코드와 함께 파일 이름을 담은 PATH 레코드를 덧붙입니다[4]. 여러 줄 이벤트의 끝에는 EOE (1320) 가 오고, PROCTITLE 은 늘 마지막 레코드입니다[1][10].

아래는 명세로 만든 예시로, 한 번의 `execve` 가 남기는 레코드 묶음입니다(값은 모두 지어낸 것이고, 두 번째 PATH 레코드와 일부 필드, ENRICHED 풀이 부분은 줄였습니다).

```text
type=SYSCALL msg=audit(1767225600.123:4821): arch=c000003e syscall=59 success=yes exit=0 a0=55d0c1a2b3c0 a1=55d0c1a2b400 a2=55d0c1a2b440 a3=0 items=2 ppid=2001 pid=2044 auid=1000 uid=1000 gid=1000 euid=1000 suid=1000 fsuid=1000 egid=1000 sgid=1000 fsgid=1000 tty=pts0 ses=3 comm="id" exe="/usr/bin/id" key="exec_log"
type=EXECVE msg=audit(1767225600.123:4821): argc=1 a0="id"
type=CWD msg=audit(1767225600.123:4821): cwd="/home/alice"
type=PATH msg=audit(1767225600.123:4821): item=0 name="/usr/bin/id" inode=393312 nametype=NORMAL
type=PROCTITLE msg=audit(1767225600.123:4821): proctitle="id"
```

SYSCALL 레코드의 `ppid` 부터 `ses` 까지는 커널이 늘 같은 순서로 적는 작업 정보이고, 사용자·그룹 번호는 처음 사용자 이름공간 (init user namespace) 기준 값입니다[12]. 그래서 컨테이너 안의 root 가 호스트 쪽 번호로 찍힐 가능성이 있습니다.

### 레코드 종류 번호대

종류 번호는 만든 쪽에 따라 구간이 나뉩니다[10].

| 번호 | 만든 쪽 |
|---|---|
| 1000~1099 | 감사 체계 제어 명령 |
| 1100~1199 | 사용자 공간 신뢰 프로그램 (로그인·인증·계정) |
| 1200~1299 | auditd 자신 |
| 1300~1399 | 감사 이벤트 |
| 1400~1499 | 커널 SELinux |
| 1500~1599 | AppArmor, 커널 LSPP |
| 1600~1699 | 커널 암호 |
| 1700~1799 | 커널 이상 징후 |
| 2100~2199 | 사용자 공간 이상 징후 |

자주 보는 종류는 다음과 같습니다[10].

| 이름 | 번호 | 뜻 |
|---|---|---|
| LOGIN | 1006 | 커널이 로그인 ID 를 정함 |
| USER_AUTH / USER_ACCT | 1100 / 1101 | 인증 / 권한 확인 |
| CRED_ACQ / CRED_DISP | 1103 / 1104 | 자격 증명 얻음 / 버림 |
| USER_START / USER_END | 1105 / 1106 | 사용자 세션 시작 / 끝 |
| USER_MGMT | 1102 | 계정 속성 바뀜 |
| USER_CHAUTHTOK | 1108 | 암호나 PIN 바꿈 |
| USER_LOGIN / USER_LOGOUT | 1112 / 1113 | 로그인 / 로그아웃 |
| ADD_USER / DEL_USER | 1114 / 1115 | 계정 추가 / 삭제 |
| USER_CMD | 1123 | 사용자 셸 명령과 인수 |
| SYSTEM_BOOT / SYSTEM_SHUTDOWN | 1127 / 1128 | 부팅 / 종료 |
| SERVICE_START / SERVICE_STOP | 1130 / 1131 | 서비스 시작 / 멈춤 |
| DAEMON_START / DAEMON_END / DAEMON_ABORT | 1200 / 1201 / 1202 | auditd 시작 / 정상 종료 / 오류 종료 |
| DAEMON_CONFIG / DAEMON_ROTATE / DAEMON_RESUME | 1203 / 1205 / 1206 | 설정 바뀜 / 회전 / 기록 다시 시작 |
| SYSCALL / PATH / CWD / EXECVE | 1300 / 1302 / 1307 / 1309 | 시스템 콜, 파일 경로, 작업 폴더, execve 인수 |
| CONFIG_CHANGE | 1305 | 감사 설정·규칙 바뀜 |
| SOCKADDR | 1306 | 소켓 주소 인수 |
| TTY | 1319 | 관리용 TTY 입력 |
| EOE | 1320 | 여러 줄 이벤트의 끝 |
| PROCTITLE | 1327 | 프로세스 제목과 명령줄 |
| KERN_MODULE | 1330 | 커널 모듈 이벤트 |
| AVC | 1400 | SELinux 허용·거부 |
| ANOM_ABEND | 1701 | 프로세스 비정상 종료 |
| ANOM_LOGIN_FAILURES | 2100 | 로그인 실패 한도 도달 |

### 주요 필드

필드 사전에서 분석에 자주 쓰는 필드는 다음과 같습니다[11]. "encoded" 로 표시한 필드는 값이 16진 문자열일 수 있습니다.

| 필드 | 형식 | 뜻 |
|---|---|---|
| `auid` | 10진 | 로그인 사용자 ID (login user ID) |
| `ses` | 10진 | 로그인 세션 ID |
| `uid`, `euid` | 10진 | 사용자 ID, 유효 사용자 ID |
| `pid`, `ppid` | 10진 | 프로세스 ID, 부모 프로세스 ID |
| `comm`, `exe` | encoded | 프로그램 이름, 실행 파일 경로 |
| `cwd`, `proctitle` | encoded | 작업 폴더, 프로세스 제목과 명령줄 |
| `key` | encoded | 걸린 감사 규칙에 붙인 키 |
| `acct`, `addr` | encoded | 계정 이름, 접속해 온 원격 주소 |
| `hostname`, `terminal`, `tty` | 문자 | 접속 호스트, 터미널 이름, tty 장치 |
| `syscall` | 10진 | 시스템 콜 번호 |
| `arch` | 16진 | ELF 아키텍처 플래그 |
| `a0`~`a3` | 16진 | 시스템 콜 인수 |
| `success`, `exit` | 문자, 10진 | 성공 여부, 시스템 콜 반환 값 |
| `res` | 10진 | 감사한 작업의 결과 (성공·실패) |
| `op` | 문자 | 감사한 작업 이름 |
| `name`, `inode`, `nametype` | encoded, 10진, 문자 | 파일 이름, 아이노드 번호, 파일 작업 종류 |
| `items` | 10진 | 이벤트에 딸린 PATH 레코드 수 |
| `saddr` | encoded | 소켓 주소 구조체 |
| `old-auid` | 10진 | 바뀌기 전 auid |

커널은 문자열에 큰따옴표, 공백, 0x21 보다 작은 바이트, 0x7E 보다 큰 바이트가 하나라도 있으면 값 전체를 대문자 16진으로 적고, 없으면 큰따옴표로 감싸 적습니다[12]. `proctitle` 은 인수 사이에 NUL 이 들어가 인수가 둘 이상이면 16진으로 적히고, 길이는 128바이트까지만 남습니다[13]. 16진 풀이와 `EXECVE` 인수 해석은 [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md) 에서 다룹니다.

로그인 ID 를 정하지 않은 프로세스는 `auid` 와 `ses` 가 부호 없는 -1, 즉 `4294967295` 로 찍힙니다[9][14].

### ENRICHED 형식의 덧붙임

`log_format = ENRICHED` 이면 auditd 가 uid·gid·시스템 콜·아키텍처·소켓 주소를 풀어 적어서, 다른 기계로 옮긴 로그도 뜻을 알 수 있습니다[1]. auditd 는 커널이 보낸 원래 레코드를 그대로 적은 뒤, 구분 문자 0x1D (`AUDIT_INTERP_SEPARATOR`) 를 한 번 넣고 풀이 필드를 공백으로 이어 붙입니다[6][7]. 풀이 필드의 이름은 원래 필드 이름을 대문자로 바꾼 것입니다[6]. uid·gid 계열 풀이 값은 `AUID="alice"` 처럼 큰따옴표로 감싸고, 값에 공백 같은 문자가 있으면 16진으로 적습니다[6][8]. 시스템 콜·아키텍처·소켓 주소 풀이 값은 `SYSCALL=execve` 처럼 따옴표 없이 적습니다[6]. `RAW` 이면 커널이 보낸 값만 남습니다[1].

명세로 만든 예시에서 원래 레코드 끝 `key="exec_log"` 와 풀이 부분이 만나는 곳은 헥스로 이렇게 보입니다.

```text
... 6B 65 79 3D 22 65 78 65 63 5F 6C 6F 67 22 1D 41 52 43 48 3D 78 38 36 5F 36 34 20 53 59 53 43 41 4C 4C 3D 65 78 65 63 76 65 ...
    k  e  y  =  "  e  x  e  c  _  l  o  g  "  ␝  A  R  C  H  =  x  8  6  _  6  4     S  Y  S  C  A  L  L  =  e  x  e  c  v  e
```

0x1D 는 화면에 보이지 않는 문자라서 `less` 나 편집기에서는 `^]` 로 보이거나 아예 보이지 않을 수 있습니다.

## 읽는 법

1. `auditd.conf` 에서 `log_file`, `log_format`, `num_logs`, `max_log_file_action`, 디스크 부족 때 동작을 먼저 읽습니다. 이 값이 로그 경로, 풀이 값이 있는지, 회전 파일이 몇 개인지를 정합니다.
2. `audit.log` 와 회전 파일 `audit.log.1`, `audit.log.2` … 를 모두 모읍니다. 번호가 클수록 오래된 파일입니다[1].
3. 줄마다 `msg=audit(초.밀리초:번호)` 를 뽑고, 시각과 번호가 같은 레코드를 한 이벤트로 모읍니다. 한 이벤트의 레코드가 줄지어 붙어 있지 않을 수 있어서, 앞뒤 몇 줄만 보지 말고 파일 전체에서 모읍니다[1].
4. 이벤트마다 SYSCALL 의 `auid`·`uid`·`exe`·`success`·`key` 와, 같은 번호의 PATH·CWD·EXECVE·PROCTITLE 을 함께 읽습니다.
5. 16진 값은 풀어 읽고, uid 를 이름으로 바꿀 때는 원래 기계의 계정 파일([UID·GID 와 사용자 이름 잇기](../value-decoding/uid-gid.md))이나 ENRICHED 풀이 값을 씁니다.

audit-userspace 의 `ausearch` 는 이 작업을 해 줍니다. `-if 파일|폴더` 로 다른 기계로 옮긴 로그를 읽고, `-a 번호` 로 한 이벤트를, `-m 종류` 로 레코드 종류를, `-k 키` 로 규칙 키를, `-ul` 로 auid 를, `--session` 으로 로그인 세션을 찾습니다[4]. `-i` 는 숫자를 이름으로 바꾸고, `--format csv` 는 이벤트를 정규화해 CSV 로 냅니다[4]. `aureport` 는 로그인(`-l`), 인증(`-au`), 계정 변경(`-m`), 실행 파일(`-x`), 규칙 키(`-k`), 이상 징후(`-n`), 파일마다 처음과 마지막 시각(`-t`) 같은 요약을 만들고, 요약의 이벤트 번호로 `ausearch -a` 를 다시 부르면 전체 이벤트를 볼 수 있습니다[5].

## 포렌식에서 중요한 점

### 증명하는 것

감사 로그는 규칙에 걸린 시스템 콜이나 신뢰 프로그램이 보낸 사건이 그 시각에 그 `auid`·`uid`·`pid`·`exe` 로 일어났다는 커널과 프로그램의 기록입니다. `auid` 는 로그인 사용자 ID 이고[11], 로그인 프로그램의 PAM 모듈 `pam_loginuid` 가 정합니다. `su`·`sudo` 에는 이 모듈을 쓰지 않게 되어 있어서, 사용자를 바꿔 root 로 실행한 명령도 처음 로그인한 계정의 `auid` 를 가리킵니다[22]. `ses` 는 같은 로그인에서 나온 프로세스를 하나로 묶습니다[4]. `success` 와 `exit` 는 시도가 성공했는지 실패했는지를 나눕니다[11].

### 증명하지 못하는 것

감사 로그는 규칙이 있던 행위만 적으므로, 기록이 없다고 해서 그 행위가 없었다고 볼 수 없습니다. 그 시점의 규칙은 `/etc/audit/audit.rules`·`rules.d/` 로 가늠하고, 라이브 시스템이면 `auditctl -l` 로 커널에 실제로 들어간 규칙을 확인합니다[21]. `auid` 는 로그인 프로그램의 PAM 설정에 `pam_loginuid` 가 있어야 정확합니다[4]([인증 모듈 (PAM)](../users-auth/pam.md)). RAW 형식 로그의 uid 는 원래 기계의 계정 파일 없이는 이름으로 제대로 바꿀 수 없습니다[4]. PATH 레코드처럼 호스트 이름이나 로그인 ID 를 담지 않는 레코드도 있습니다[4].

### 시각 해석

`audit(...)` 의 시각은 커널이 시스템 콜에 들어갈 때 읽은 벽시계 (CLOCK_REALTIME) 값이고, UTC 기준 Unix epoch 초에 밀리초를 붙인 것입니다[12][13]. 시간대 정보가 없고 로캘에도 따르지 않으므로 UTC 로 바꿔 적고, 현지 시각은 [호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md) 로 따로 맞춥니다. 시스템 시계를 바꾸면 그 뒤 레코드의 시각도 함께 바뀝니다. 시각 형식 일반은 [Linux 의 시각 값](../value-decoding/time-values.md) 을 봅니다.

`ausearch -ts`·`-te` 의 날짜는 분석하는 기계의 로캘 형식(`date '+%x'`)을 따르고, `boot` 은 지금 시각에서 `/proc/uptime` 을 뺀 값이라 부팅 뒤 시계를 맞췄으면 틀립니다[4]. 이미지를 분석할 때는 `boot` 대신 시각을 직접 적습니다.

### 회전과 삭제

auditd 는 logrotate 를 쓰지 않고 스스로 회전합니다([로그 순환 (logrotate)](logrotate.md)). `max_log_file` 에 닿거나 SIGUSR1 을 받으면 `audit.log.N-1` 을 `audit.log.N` 으로, 마지막에 `audit.log` 를 `audit.log.1` 로 이름을 바꾸고 새 `audit.log` 를 엽니다[3][6]. 이름만 바꾸므로 회전 파일의 아이노드와 쓰기 시각은 그대로 남습니다. 회전할 때 닫는 파일은 권한을 소유자 읽기 전용(`log_group` 이 root 가 아니면 그룹 읽기 추가)으로 바꿉니다[6]. `num_logs` 가 2 보다 작으면 회전하지 않고[1][6], 기본값 5 이면 `audit.log` 와 `audit.log.1`~`.4` 까지 다섯 파일이 남아 가장 오래된 파일은 다음 회전 때 덮어써집니다[6]. `max_log_file_action = KEEP_LOGS` 이면 `num_logs` 를 쓰지 않고 오래된 파일을 지우지 않습니다[1].

디스크가 모자라거나 쓰기 오류가 나면 기본 설정에서 auditd 가 기록을 멈춥니다(`SUSPEND`)[1][2]. 이와 따로, auditd 가 떠 있지 않아 커널이 레코드를 넘기지 못하거나 다시 보낼 대기열이 넘치면, 커널은 그 레코드를 `audit: type=번호 ...` 모양으로 커널 로그에 찍고(EOE 는 빼고, 속도 제한 있음), 잃어버린 레코드 수는 `audit_lost=` 경고로 남깁니다[12]. 기록이 끊긴 구간은 [커널 로그](../../02-artifacts/system-info/kernel-log.md) 와 syslog 경고에서 이유를 찾습니다.

auditd 의 시작·종료·설정 변경·회전은 감사 로그 자신에 DAEMON_START·DAEMON_END·DAEMON_CONFIG·DAEMON_ROTATE 로 남습니다[3][10]. SIGTERM 을 받으면 종료 이벤트를 쓰고 끝나고, SIGHUP 으로 설정을 다시 읽는 데 성공하면 DAEMON_CONFIG 를 남깁니다[3]. 규칙을 바꾸면 커널이 CONFIG_CHANGE 를 적습니다[10]. 이 레코드들이 끊긴 구간 앞뒤에 있는지 보면 감사를 멈춘 흔적을 가려낼 수 있습니다. 지우기·조작 흔적 전반은 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md) 를 봅니다.

## 함정

- **auditd 가 없어도 감사 레코드가 있을 수 있습니다.** systemd-journald 는 `systemd-journald-audit.socket` 이 켜져 있으면 커널 감사 레코드를 모아 `_TRANSPORT=audit` 로 저장합니다[15][16][17]. journald.conf 의 `Audit=` 는 커널 감사를 켤지만 정하고 수집 여부는 정하지 않으며, 기본 이름공간에서 기본값은 yes 입니다[15]. `/var/log/audit/` 가 없으면 [systemd 저널](systemd-journal/index.md) 을 봅니다. 저널 항목의 `_AUDIT_LOGINUID`·`_AUDIT_SESSION` 은 감사 체계가 관리하는 auid·ses 입니다[17].
- **부팅 초기 프로세스는 커널 인수에 `audit=1` 이 없으면 제대로 감사되지 않습니다**[3]. auditd 가 뜨기 전 시작한 프로세스의 기록이 비는 이유가 될 수 있습니다.
- **여러 파일·여러 부팅의 로그를 합칠 때는 번호가 겹칠 가능성이 있습니다.** 일련번호는 커널 안의 계수기라 부팅할 때마다 0 부터 다시 세고, 커널은 (시각, 일련번호) 쌍으로 한 시스템 콜의 레코드를 묶습니다[12]. 합쳐 읽을 때는 초와 번호를 함께 키로 씁니다.
- **ENRICHED 줄을 공백으로만 나누면 0x1D 뒤 대문자 필드가 원래 필드와 섞입니다.** dissect.target 의 audit 플러그인은 `type=`·`msg=audit(...)` 뒤 전부를 `message` 하나로 넣으므로 풀이 필드도 같은 문자열에 함께 들어가고, 줄이 `type=` 으로 시작해야 읽으므로 `node=` 가 붙은 줄은 건너뜁니다[19]. 소문자 필드(커널 값)와 대문자 필드(auditd 풀이)를 나눠 읽습니다.
- **`ausearch -i` 를 분석 기계에서 돌리면 틀린 이름이 나올 수 있습니다.** RAW 로그는 분석하는 기계의 계정 정보로 uid 를 바꾸기 때문입니다[4]. `aureport -i` 는 로그 형식과 상관없이 늘 분석하는 기계의 계정 정보를 씁니다[5].
- **회전 파일 번호를 거꾸로 읽지 않습니다.** 번호가 클수록 오래됐습니다[1].
- **systemd-update-utmp 는 부팅·종료를 utmp·wtmp 와 감사 로그 양쪽에 씁니다**[18]. SYSTEM_BOOT·SYSTEM_SHUTDOWN 은 [로그인 기록 파일 형식](utmp-wtmp-format.md) 의 `reboot`·`shutdown` 레코드와 맞춰 봅니다.

## 도구

| 도구 | 하는 일 |
|---|---|
| `ausearch` (audit-userspace) | 조건으로 이벤트 검색, `-if` 로 옮긴 로그 읽기, `-i` 풀이, CSV·문장 형식 출력[4] |
| `aureport` (audit-userspace) | 로그인·인증·실행 파일·키·이상 징후 요약[5] |
| dissect.target `audit` 플러그인 | `/var/log/audit/audit.log*` 와 `auditd.conf` 의 `log_file` 경로를 찾아 줄마다 시각·종류·번호·나머지로 나눔[19] |
| ForensicArtifacts `LinuxAuditLogs` | 수집 경로 `/var/log/audit/*`[20] |
| UAC | 라이브 수집에서 `auditctl -l`(규칙), `auditctl -s`(상태) 결과를 저장[21] |

라이브 시스템에서는 로그 파일과 함께 `auditctl -l`·`auditctl -s` 결과를 남겨 두어야 그때 어떤 규칙이 걸려 있었는지 알 수 있습니다([라이브 응답 수집](../../03-techniques/acquisition/live-response.md)). 여러 로그를 시각으로 합치는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 와 [로그 분석](../../03-techniques/analysis/log-analysis.md) 을 봅니다.

## 참고 문헌

1. linux-audit, audit-userspace, `auditd.conf(5)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/auditd.conf.5
2. linux-audit, audit-userspace, 기본 설정 파일 `init.d/auditd.conf`. https://github.com/linux-audit/audit-userspace/blob/master/init.d/auditd.conf
3. linux-audit, audit-userspace, `auditd(8)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/auditd.8
4. linux-audit, audit-userspace, `ausearch(8)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/ausearch.8
5. linux-audit, audit-userspace, `aureport(8)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/aureport.8
6. linux-audit, audit-userspace, `src/auditd-event.c` (`format_raw`, `format_enrich`, `add_simple_field`, `rotate_logs`). https://github.com/linux-audit/audit-userspace/blob/master/src/auditd-event.c
7. linux-audit, audit-userspace, `lib/libaudit.h` (`AUDIT_INTERP_SEPARATOR`). https://github.com/linux-audit/audit-userspace/blob/master/lib/libaudit.h
8. linux-audit, audit-userspace, `lib/audit_logging.c` (`audit_encode_nv_string`). https://github.com/linux-audit/audit-userspace/blob/master/lib/audit_logging.c
9. linux-audit, audit-userspace, `audit.rules(7)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/audit.rules.7
10. linux-audit, audit-documentation, `message-dictionary.csv`, `message-dictionary-ranges.txt`. https://github.com/linux-audit/audit-documentation/tree/main/specs/messages
11. linux-audit, audit-documentation, `field-dictionary.csv`. https://github.com/linux-audit/audit-documentation/blob/main/specs/fields/field-dictionary.csv
12. Linux 커널, `kernel/audit.c`. https://github.com/torvalds/linux/blob/master/kernel/audit.c
13. Linux 커널, `kernel/auditsc.c`. https://github.com/torvalds/linux/blob/master/kernel/auditsc.c
14. Linux 커널, `include/uapi/linux/audit.h`. https://github.com/torvalds/linux/blob/master/include/uapi/linux/audit.h
15. systemd, `journald.conf(5)`. https://github.com/systemd/systemd/blob/main/man/journald.conf.xml
16. systemd, `systemd-journald.service(8)`. https://github.com/systemd/systemd/blob/main/man/systemd-journald.service.xml
17. systemd, `systemd.journal-fields(7)`. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
18. systemd, `systemd-update-utmp.service(8)`. https://github.com/systemd/systemd/blob/main/man/systemd-update-utmp.service.xml
19. fox-it, dissect.target, `plugins/os/unix/log/audit.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/audit.py
20. ForensicArtifacts, artifacts, `linux.yaml` (`LinuxAuditLogs`). https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
21. tclahr, UAC, `artifacts/live_response/system/auditctl.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/live_response/system/auditctl.yaml
22. linux-pam, `pam_loginuid(8)`. https://github.com/linux-pam/linux-pam/blob/master/modules/pam_loginuid/pam_loginuid.8.xml
