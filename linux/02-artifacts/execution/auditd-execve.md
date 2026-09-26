---
title: "감사 로그의 실행 기록"
parent: "아티팩트 · 실행 흔적"
nav_order: 460
---

# 감사 로그의 실행 기록 (auditd execve)

`execve` 시스템 콜을 잡는 감사 규칙이 있으면, 커널은 프로그램이 실행될 때마다 누가 어떤 파일을 어떤 인수로 어느 폴더에서 실행했는지를 감사 로그에 레코드 묶음으로 남깁니다[1][3].

## 무엇을 기록하나 · 왜 생기나

리눅스 감사 체계 (Linux Audit) 는 규칙에 걸린 시스템 콜을 기록합니다. 프로그램 실행은 `execve` 시스템 콜이라서, 이 시스템 콜을 대상으로 하는 규칙이 있을 때만 실행 기록이 생깁니다[1]. 규칙이 없으면 auditd 가 돌고 있어도 실행 기록은 남지 않습니다. 셸 기록 파일은 사용자가 지우거나 끌 수 있지만, 감사 기록은 커널이 적어서 셸 종류와 상관없이 cron·서비스·스크립트가 띄운 프로그램까지 같은 모양으로 남습니다.

시스템 콜 규칙의 일반형은 `-a action,list -S syscall -F field=value -k keyname` 입니다[1]. 64비트와 32비트 인터페이스의 시스템 콜 번호가 다를 수 있어서, 규칙은 `-F arch=b32` 와 `-F arch=b64` 두 줄로 나눠 적습니다[1]. x86_64 에서 `execve` 는 64비트 표의 59번이고 32비트(i386) 표의 11번이라서[6], `arch=b64` 한 줄만 있으면 32비트 프로그램의 실행은 잡히지 않습니다.

실제로 쓰이는 규칙의 예는 다음과 같습니다.

| 규칙 | 어디에 있나 | 잡는 것 |
|---|---|---|
| `-a always,exit -F arch=b64 -S execve -C uid!=euid -F euid=0 -F key=10.2.5.b-elevated-privs-setuid` (b32 줄도 있음) | audit-userspace 예시 묶음 `30-pci-dss-v31.rules`[2] | 실제 uid 와 유효 uid 가 다르고 유효 uid 가 0 인 실행, 곧 root 로 권한이 바뀌는 실행 |
| `auditctl -a exit,always -F arch=b64 -S execve -k procmon` | Velociraptor `Linux.Events.ProcessExecutions` 가 라이브 수집 때 넣는 규칙[11] | 64비트 실행 전부 |

audit-userspace 가 싣는 예시 규칙 묶음은 필요한 조각을 골라 `/etc/audit/rules.d/` 로 복사해 쓰는 것이라[2], 시스템마다 들어 있는 규칙이 다릅니다. 그래서 실행 기록을 해석하기 전에 그 시점의 규칙부터 확인합니다. 감사 로그의 줄 모양, 이벤트와 레코드의 관계, 회전, 필드 사전은 [감사 로그 형식](../../01-foundations/logging/auditd-format.md) 에서 다루고, 이 페이지는 실행 규칙과 실행 레코드를 읽는 법만 다룹니다.

## 위치와 버전별 차이

Ubuntu 24.04 와 RHEL 9 모두 auditd 가 깔려 있어야 아래 경로가 생기고 경로는 같습니다. 설치 여부는 패키지 기록([dpkg·apt 기록](../packages/dpkg-apt.md), [rpm·dnf·yum 기록](../packages/rpm-dnf.md))으로 확인합니다.

| 무엇 | 경로 | 볼 점 |
|---|---|---|
| 감사 로그 | `/var/log/audit/audit.log`, 회전 파일 `audit.log.1` … | `auditd.conf` 의 `log_file` 로 바뀔 수 있음([감사 로그 형식](../../01-foundations/logging/auditd-format.md)) |
| 규칙 조각 | `/etc/audit/rules.d/*.rules` | `-S execve` 또는 `-S execveat` 가 든 줄, `arch` 값, 키 |
| 합친 규칙 | `/etc/audit/audit.rules` | augenrules 가 `rules.d` 의 `.rules` 파일을 이름 순으로 이어 붙인 결과[19] |
| 커널에 들어간 규칙 | `auditctl -l` 출력 | 라이브 시스템에서만 볼 수 있음[12] |

systemd-journald 는 커널 감사 체계에서 읽은 레코드를 `_TRANSPORT=audit` 로 저널에 남길 수 있습니다[14]. 이 경우는 [감사 로그 형식](../../01-foundations/logging/auditd-format.md) 과 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 을 봅니다.

## 구조

### 한 번의 execve 가 남기는 레코드

커널은 시스템 콜이 끝날 때 다음 순서로 레코드를 적고, 모든 레코드가 같은 `msg=audit(초.밀리초:일련번호)` 를 씁니다[3][8].

| 순서 | 레코드 (번호) | 내용 |
|---|---|---|
| 1 | `SYSCALL` (1300) | 아키텍처, 시스템 콜 번호, 성공 여부, 프로세스·사용자 정보, 규칙 키 |
| 2 | `BPRM_FCAPS` (1321) | 파일 capability 로 권한이 늘어난 실행일 때만 |
| 3 | `EXECVE` (1309) | 인수 개수와 인수. 길면 여러 줄 |
| 4 | `CWD` (1307) | 실행 당시 작업 폴더 |
| 5 | `PATH` (1302) | 실행에 쓰인 파일마다 한 줄, SYSCALL 의 `items` 개수만큼 |
| 6 | `PROCTITLE` (1327) | 명령줄 앞부분 |
| 7 | `EOE` (1320) | 여러 줄 이벤트의 끝 |

`EXECVE` 레코드는 실행 파일을 불러오는 데 성공한 뒤에 준비됩니다[5]. 그래서 파일이 없거나 권한이 없어 실패한 `execve` 는 `success=no` 인 SYSCALL 은 남아도 인수를 담은 EXECVE 레코드는 없을 수 있습니다.

### SYSCALL 레코드에서 볼 필드

커널은 SYSCALL 레코드를 `arch=… syscall=… success=… exit=… a0=… a1=… a2=… a3=… items=…` 로 시작하고, 이어서 `ppid pid auid uid gid euid suid fsuid egid sgid fsgid tty ses comm exe` 를 늘 같은 순서로 적은 뒤 끝에 `key=` 를 붙입니다[3][4]. 규칙에 키가 없으면 `key=(null)` 입니다[4].

| 필드 | 실행 기록에서의 뜻 |
|---|---|
| `arch` | ELF 아키텍처 값. x86_64 는 `c000003e`, i386 은 `40000003`[7] |
| `syscall` | 시스템 콜 번호. x86_64 의 `execve` 는 59, `execveat` 는 322[6] |
| `success`, `exit` | 실행 성공 여부와 반환 값[8] |
| `a0`~`a3` | 시스템 콜 인수의 16진 값[8]. `execve` 에서는 사용자 메모리 주소라 명령줄을 알려 주지 않음 |
| `items` | 이 이벤트의 PATH 레코드 수[8] |
| `ppid`, `pid` | 부모 프로세스 ID, 실행한 프로세스 ID |
| `auid`, `ses` | 로그인 사용자 ID, 로그인 세션 ID[8] |
| `uid`, `euid` | 실제·유효 사용자 ID. 레코드를 적는 때가 실행 뒤라 setuid 파일이면 `euid` 가 바뀐 값[3][4] |
| `tty` | 터미널 이름. 없으면 `(none)`[4] |
| `comm`, `exe` | 새 프로그램의 명령 이름과 실행 파일 경로[8] |
| `key` | 걸린 규칙의 키[8] |

### EXECVE 레코드의 인수

EXECVE 레코드는 `argc=인수개수` 로 시작하고 인수를 `a0=`, `a1=` … 로 적습니다[3]. `a0` 은 실행한 프로그램이 받은 첫 인수이고, 보통 명령 이름입니다.

인수에 큰따옴표, 0x21 보다 작은 바이트(공백·제어 문자), 0x7E 보다 큰 바이트가 하나라도 있으면 커널은 그 인수를 따옴표 없는 대문자 16진 문자열로 적고, 없으면 큰따옴표로 감싸 적습니다[3][4]. 공백이 든 경로나 한글이 든 인수는 늘 16진으로 적힙니다. 이 판단은 인수마다 따로 하므로 한 줄 안에 따옴표 인수와 16진 인수가 섞입니다.

EXECVE 레코드 한 줄의 인수 부분은 7500바이트(`MAX_EXECVE_AUDIT_LEN`)를 넘지 않습니다[3]. 인수 하나가 남은 자리에 다 들어가지 않으면 커널은 `aN_len=길이 aN[0]=… aN[1]=…` 처럼 조각으로 나눠 적고, 줄이 차면 새 EXECVE 레코드를 열어 이어 적습니다[3]. 그래서 한 이벤트에 EXECVE 줄이 여러 개일 수 있고, `argc=` 는 첫 줄에만 있습니다. 인수가 7500바이트 이상이라 여러 번에 나눠 읽어야 하면 내용과 상관없이 16진으로 적습니다[3]. `aN_len` 은 기록된 값의 길이라서 16진이면 원래 바이트 수의 두 배입니다[3]. 조각은 번호 순으로 이어 붙여 읽습니다.

### PROCTITLE 레코드

PROCTITLE 은 `/proc/[pid]/cmdline` 과 같은 곳에서 명령줄을 최대 128바이트(`MAX_PROCTITLE_AUDIT_LEN`)까지 읽고, 끝의 출력할 수 없는 문자를 잘라 낸 뒤 같은 규칙으로 적습니다[3][4]. 명령줄은 인수 사이를 NUL(0x00)로 나누므로 인수가 둘 이상이면 PROCTITLE 은 16진이 됩니다. EXECVE 레코드가 없는 이벤트에도 PROCTITLE 은 남으므로, 긴 명령줄은 EXECVE 로, 앞부분만 필요할 때는 PROCTITLE 로 봅니다.

## 증거로서 의미

### 증명하는 것

실행 레코드 묶음은 규칙에 걸린 `execve` 가 그 시각에 그 `pid`·`ppid` 로 호출됐고, 어떤 실행 파일(`exe`, PATH)을 어떤 인수(EXECVE)로 어느 폴더(CWD)에서 실행했는지, 성공했는지(`success`·`exit`)를 커널이 적은 기록입니다[3][8]. `auid` 는 로그인 때 정해져 `su`·`sudo` 뒤에도 그대로 따라가므로, root 로 실행한 명령이라도 처음 로그인한 계정을 가리킵니다([감사 로그 형식](../../01-foundations/logging/auditd-format.md)). `ses` 가 같은 이벤트를 모으면 한 로그인 세션에서 실행한 명령이 순서대로 보이고, `ppid` 를 따라가면 어떤 셸이나 서비스가 띄운 프로그램인지 좁힐 수 있습니다. `success=no` 인 이벤트는 실행을 시도했다가 실패한 흔적입니다.

### 증명하지 못하는 것

규칙이 없던 시기, 규칙이 잡지 않는 아키텍처, `execveat` 처럼 규칙에 없는 시스템 콜로 한 실행은 기록되지 않습니다. `cd`·`echo`·`history` 같은 셸 내장 명령 (builtin) 은 새 프로그램을 실행하지 않으므로 `execve` 가 없고, 셸 안에서 한 입력은 이 기록에 나오지 않습니다. 실행 기록은 프로그램이 시작됐다는 사실만 보여 주고, 프로그램이 무엇을 했는지, 언제 끝났는지, 결과가 무엇이었는지는 보여 주지 않습니다. auditd 가 디스크 부족으로 기록을 멈춘 구간도 비어 있습니다([감사 로그 형식](../../01-foundations/logging/auditd-format.md)). `auid` 는 로그인 프로그램의 PAM 설정에 `pam_loginuid` 가 있어야 정확하고[9], 로그인 ID 가 없는 프로세스는 `auid=4294967295` 로 적힙니다[1]([인증 모듈 (PAM)](../../01-foundations/users-auth/pam.md)).

보고서에는 "이 시각에 auid 1000 의 세션 3 에서 `/usr/bin/zip` 을 이 인수로 실행한 기록이 있다" 처럼 레코드로 확인되는 만큼만 씁니다.

## 시각 해석

`msg=audit(초.밀리초:일련번호)` 의 시각은 커널이 `execve` 시스템 콜에 들어갈 때 읽은 실제 시각 시계(wall clock) 값입니다[3]. UTC 기준 Unix epoch 초에 밀리초를 붙인 값이라 시간대 정보가 없고, 현지 시각으로 바꿀 때는 분석 대상의 시간대를 따로 확인합니다([Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)). 레코드는 시스템 콜이 끝날 때 적지만 시각은 들어갈 때의 값이므로, 같은 이벤트의 모든 줄이 한 시각을 씁니다. 시스템 시계를 바꾸면 그 뒤 기록도 바뀐 시계를 따릅니다.

이 시각은 프로그램이 시작된 때이지 끝난 때가 아닙니다. 끝난 때와 쓴 CPU 시간은 [프로세스 회계](process-accounting.md) 가 켜져 있을 때 거기서 찾습니다.

## 함정과 한계

- **문자열 검색이 16진 인수를 놓칩니다.** 인수에 공백 하나만 있어도 16진으로 적히므로[3][4], `grep` 으로 경로나 명령을 찾을 때는 16진으로 바꾼 문자열도 함께 찾거나, 먼저 풀어 놓고 찾습니다. EXECVE 레코드에서 파일 이름 문자열만 찾는 탐지 규칙도 있어서[17], 이런 규칙의 결과가 없다는 것이 곧 실행이 없었다는 뜻은 아닙니다.
- **`comm` 을 프로그램 이름으로 믿지 않습니다.** `comm` 은 NUL 을 포함해 16바이트에서 잘리고 프로세스가 스스로 바꿀 수 있습니다[13]. `exe`·PATH·EXECVE 의 `a0` 과 견줘 봅니다.
- **`a0` 도 실행 파일 이름이 아닐 수 있습니다.** `a0` 은 실행한 쪽이 넘긴 첫 인수라서 실제 경로는 `exe` 와 PATH 레코드로 확인합니다. 스크립트를 실행하면 `exe` 가 인터프리터 경로로 적힐 가능성이 있으니, 스크립트 파일은 PATH 레코드에서 찾습니다.
- **`ausearch -sc execve` 는 분석하는 기계의 시스템 콜 표로 번호를 찾습니다**[9]. 다른 아키텍처(예: aarch64) 시스템의 로그라면 번호로 찾습니다.
- **`ausearch -i` 의 사용자 이름은 분석 기계 기준일 수 있습니다.** 풀이 값이 없는 로그는 분석하는 기계의 계정 정보로 uid 를 바꿉니다[9]. 이름은 분석 대상의 계정 파일로 다시 확인합니다([UID·GID 와 사용자 이름 잇기](../../01-foundations/value-decoding/uid-gid.md)).
- **도구가 덧붙인 부모 명령줄은 수집 시점 값입니다.** Velociraptor `Linux.Events.ProcessExecutions` 는 부모 프로세스의 명령줄을 이벤트를 받을 때 `/proc/PPID/cmdline` 에서 읽어 붙입니다[11]. 부모가 이미 끝났거나 PID 가 재사용됐으면 비거나 다른 값이 됩니다. 감사 레코드 자체에는 `ppid` 번호만 있습니다.
- **저널의 `_COMM`·`_EXE`·`_CMDLINE` 은 실행 인수가 아닙니다.** 저널 필드 정의상 이 값들은 그 항목을 보낸 프로세스의 것입니다[14]. 감사 레코드 본문의 `exe`·EXECVE 와 섞어 읽지 않습니다.
- **sudo 로 실행한 명령은 두 번 보일 수 있습니다.** sudo 는 사용자 공간에서 `USER_CMD`(1123) 레코드로 명령을 따로 남기고, 명령 문자열은 같은 16진 규칙으로 적습니다[8][15]. 여기에 execve 규칙이 있으면 sudo 가 띄운 프로그램의 EXECVE 이벤트가 이어집니다. 자세한 읽는 법은 [sudo·su 사용 기록](../logins/sudo-su.md) 에 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시이고 값은 모두 지어낸 것입니다. 사용자가 `zip -r /tmp/q3.zip "/srv/share/q3 report"` 를 실행한 경우입니다. SYSCALL 의 주소 값과 PATH 의 나머지 필드는 `…` 로 줄였습니다.

```text
type=SYSCALL msg=audit(1767225900.412:5310): arch=c000003e syscall=59 success=yes exit=0 a0=… a1=… a2=… a3=… items=2 ppid=2001 pid=2107 auid=1000 uid=1000 gid=1000 euid=1000 suid=1000 fsuid=1000 egid=1000 sgid=1000 fsgid=1000 tty=pts0 ses=3 comm="zip" exe="/usr/bin/zip" key="exec_log"
type=EXECVE msg=audit(1767225900.412:5310): argc=4 a0="zip" a1="-r" a2="/tmp/q3.zip" a3=2F7372762F73686172652F7133207265706F7274
type=CWD msg=audit(1767225900.412:5310): cwd="/home/alice"
type=PATH msg=audit(1767225900.412:5310): item=0 name="/usr/bin/zip" …
type=PATH msg=audit(1767225900.412:5310): item=1 name=…
type=PROCTITLE msg=audit(1767225900.412:5310): proctitle=7A6970002D72002F746D702F71332E7A6970002F7372762F73686172652F7133207265706F7274
type=EOE msg=audit(1767225900.412:5310):
```

`a3` 에는 따옴표가 없으므로 16진 값입니다. 두 자리씩 끊으면 공백(0x20)이 있어서 16진으로 적혔다는 것을 알 수 있습니다.

```text
2F 73 72 76 2F 73 68 61 72 65 2F 71 33 20 72 65 70 6F 72 74
 /  s  r  v  /  s  h  a  r  e  /  q  3     r  e  p  o  r  t
```

PROCTITLE 은 `zip`, `-r`, `/tmp/q3.zip`, `/srv/share/q3 report` 를 NUL(0x00)로 이은 39바이트입니다. `7A 69 70 00 2D 72 00 …` 처럼 `00` 이 인수 경계이고, 128바이트보다 짧아서 명령줄 전체가 들어 있습니다. `echo 7A69…7274 | xxd -r -p | tr '\0' ' '` 처럼 풀면 명령줄이 나옵니다.

인수 하나가 8000바이트인 명령이라면 EXECVE 는 `argc=3 a0="sh" a1="-c" a2_len=16000 a2[0]=…` 로 시작하고, 다음 EXECVE 줄이 `a2[1]=…` 로 이어집니다. 인수가 7500바이트보다 길어 16진으로 적혔기 때문에 `a2_len` 이 8000 의 두 배입니다[3].

### 공개 도구로 한 번

audit-userspace 의 `ausearch`·`aureport` 는 다른 기계로 옮긴 로그도 `-if` 로 읽습니다[9][10].

```text
ausearch -if /case/var/log/audit/ -sc execve -i
ausearch -if /case/var/log/audit/ -k exec_log -ul 1000 -i
ausearch -if /case/var/log/audit/ -x /usr/bin/zip -i
ausearch -if /case/var/log/audit/ -a 5310 -i
aureport -if /case/var/log/audit/ -x
```

`-sc` 는 시스템 콜, `-k` 는 규칙 키, `-ul` 은 auid, `-x` 는 실행 파일 이름, `-a` 는 이벤트 번호로 찾고, `-i` 는 숫자 값을 글자로 풀어 보여 줍니다[9]. `aureport -x` 는 실행 파일 보고서를 만들고, 보고서의 이벤트 번호로 `ausearch -a` 를 다시 부르면 레코드 묶음 전체가 나옵니다[10].

dissect.target 의 `audit` 플러그인은 `/var/log/audit/audit.log*` 와 `auditd.conf` 의 `log_file` 경로를 찾아 줄마다 시각·종류·일련번호·나머지 문자열로 나눕니다[16]. 16진 값을 풀거나 같은 번호의 레코드를 한 이벤트로 묶지는 않으므로, 결과를 일련번호로 묶고 16진 인수는 따로 풉니다. 라이브 시스템이라면 로그와 함께 `auditctl -l`·`auditctl -s` 결과를 남겨 두어야 그때 걸려 있던 규칙을 알 수 있습니다[12]([라이브 응답 수집](../../03-techniques/acquisition/live-response.md)).

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 점 | 페이지 |
|---|---|---|
| 셸 명령 기록 | 같은 시각대의 명령과 셸 내장 명령, 기록 파일이 지워진 흔적 | [셸 명령 기록](shell-history/index.md) |
| 프로세스 회계 | 같은 명령 이름의 시작 시각, 끝난 때, uid | [프로세스 회계](process-accounting.md) |
| 실행 중인 프로세스 | 라이브 수집 때 아직 떠 있는 `pid` 의 명령줄과 실행 파일 | [실행 중인 프로세스](proc.md) |
| 감사 로그의 파일 감시 | 같은 `ses`·`pid` 에서 건드린 파일 | [감사 로그의 파일 감시](../file-activity/auditd-watches.md) |
| sudo·su 사용 기록 | `USER_CMD` 와 뒤따르는 실행 이벤트, `auid` 와 `uid` 차이 | [sudo·su 사용 기록](../logins/sudo-su.md) |
| 로그인 기록 | `ses` 가 시작된 로그인과 접속 주소 | [로그인 기록](../logins/wtmp-btmp-lastlog.md) |
| 임시 폴더 | `exe` 나 PATH 가 `/tmp`·`/dev/shm` 을 가리킬 때 그 파일의 흔적 | [임시 폴더와 메모리 파일 시스템](../file-activity/tmp-shm.md) |
| TTY 감사 | `pam_tty_audit` 가 켜져 있으면 셸 내장 명령까지 포함한 키 입력이 TTY(1319) 레코드로 남고 `aureport --tty` 로 봄[8][18] | [인증 모듈 (PAM)](../../01-foundations/users-auth/pam.md) |

여러 기록을 한 줄로 늘어놓는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 와 [로그 분석](../../03-techniques/analysis/log-analysis.md) 을, 조사 흐름은 [누가 그 명령을 실행했나](../../04-scenarios/attribution/user-attribution.md) 와 [권한을 올렸나](../../04-scenarios/intrusion/privilege-escalation.md) 를, 감사 기록을 멈추거나 지운 흔적은 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md) 를 봅니다.

## 실습

auditd 가 깔리고 execve 규칙이 있는 공개 Linux 시험 이미지(NIST CFReDS 등)나 직접 만든 가상 머신 이미지로 풀어 봅니다.

1. `/etc/audit/rules.d/` 와 `audit.rules` 에 `execve` 규칙이 있는가? `arch=b32` 와 `arch=b64` 가 둘 다 있는가? 키는 무엇인가?
2. `syscall=59` 인 이벤트 가운데 `success=no` 인 것은 몇 개이고, 그 이벤트에 EXECVE 레코드가 있는가?
3. 한 `ses` 값을 골라 실행 이벤트를 시각 순서로 늘어놓자. 첫 실행은 어떤 `ppid` 에서 나왔는가?
4. EXECVE 인수 가운데 16진으로 적힌 것을 모두 풀어 보자. 공백이나 한글이 든 경로가 있는가?
5. `uid` 와 `auid` 가 다른 실행 이벤트가 있는가? 같은 시각의 sudo 기록과 맞는가?
6. PROCTITLE 이 128바이트에서 잘린 이벤트를 찾아 같은 이벤트의 EXECVE 인수와 견줘 보자.

## 참고 문헌

1. linux-audit, audit-userspace, `audit.rules(7)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/audit.rules.7
2. linux-audit, audit-userspace, `rules/README-rules`, `rules/30-pci-dss-v31.rules`. https://github.com/linux-audit/audit-userspace/tree/master/rules
3. Linux 커널, `kernel/auditsc.c` (`audit_log_exit`, `audit_log_execve_info`, `audit_log_proctitle`, `__audit_syscall_entry`). https://github.com/torvalds/linux/blob/master/kernel/auditsc.c
4. Linux 커널, `kernel/audit.c` (`audit_log_task_info`, `audit_string_contains_control`, `audit_log_n_string`, `audit_log_key`). https://github.com/torvalds/linux/blob/master/kernel/audit.c
5. Linux 커널, `fs/exec.c` (`exec_binprm`). https://github.com/torvalds/linux/blob/master/fs/exec.c
6. Linux 커널, `arch/x86/entry/syscalls/syscall_64.tbl`, `syscall_32.tbl`. https://github.com/torvalds/linux/tree/master/arch/x86/entry/syscalls
7. Linux 커널, `include/uapi/linux/audit.h`, `include/uapi/linux/elf-em.h`. https://github.com/torvalds/linux/tree/master/include/uapi/linux
8. linux-audit, audit-documentation, `message-dictionary.csv`, `field-dictionary.csv`. https://github.com/linux-audit/audit-documentation/tree/main/specs
9. linux-audit, audit-userspace, `ausearch(8)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/ausearch.8
10. linux-audit, audit-userspace, `aureport(8)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/aureport.8
11. Velocidex, velociraptor, `Linux/Events/ProcessExecutions.yaml`. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Events/ProcessExecutions.yaml
12. tclahr, UAC, `artifacts/live_response/system/auditctl.yaml`. https://github.com/tclahr/uac/blob/main/artifacts/live_response/system/auditctl.yaml
13. man-pages, `proc(5)` (`/proc/[pid]/comm`). https://github.com/mkerrisk/man-pages/blob/master/man5/proc.5
14. systemd, `systemd.journal-fields(7)`. https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
15. linux-audit, audit-userspace, `audit_log_user_command(3)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/audit_log_user_command.3
16. fox-it, dissect.target, `plugins/os/unix/log/audit.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/log/audit.py
17. SigmaHQ, sigma, `rules/linux/auditd/execve/lnx_auditd_susp_histfile_operations.yml`. https://github.com/SigmaHQ/sigma/blob/master/rules/linux/auditd/execve/lnx_auditd_susp_histfile_operations.yml
18. linux-pam, `pam_tty_audit(8)`. https://github.com/linux-pam/linux-pam/blob/master/modules/pam_tty_audit/pam_tty_audit.8.xml
19. linux-audit, audit-userspace, `augenrules(8)`. https://github.com/linux-audit/audit-userspace/blob/master/docs/augenrules.8
